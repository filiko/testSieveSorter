"""The whole machine as one buildable assembly: the seesaw stack on its frame, with the push-rod drive and
the buzz puck (docs/SYSTEM.md sections 2 and 3). The build sheet is PRODUCT.md.

Levels, top to bottom. Each box tips about a Y axis through its own pivot (box centre, mid-height); the
pivots are PITCH apart and neighbours tip opposite ways:
    level0  seesaw_holder_drive_a     + the breaker B-164f355a (BREAKER, breaker_layer.py)
    level1  seesaw_holder_drive_b     + sieve_insert_5mm_across
    level2  seesaw_holder_drive_a     + sieve_insert_2mm_across
    level3  seesaw_catch_pan_drive_b

Drive. BugSorter's controller runs one linear stage between two limit switches at constant speed (default
stroke 20 mm, at most 5 cm/s: docs/current-system-vs-our-idea.md). A yoke on that stage carries two vertical
push rods on the +Y side. Rod A at x = +R drives levels 0 and 2; rod B at x = -R drives levels 1 and 3. A
3 mm cross-pin on each rod rides in the box's drive-lug slot (seesaw_holder.py). When the stage rises by u,
the rod-A boxes lift their +X ends and the rod-B boxes their -X ends, so neighbours always tip opposite ways,
each by atan(u / R). R = seesaw_holder.DRIVE_R = 56.7 mm, so the default 20 mm stroke gives +/-10 deg.
- The yoke is a flat plate low on the +Y side, outboard of the +Y post. Nothing crosses over the top, where
  samples go in and the spray comes down.
- It carries frame_holder's mounting tab (22 x 4.5 x 25, 6 mm hole 6.5 from the end), so it takes the bolt
  the old box tab took. The stage itself, and where it stands, are ASSUMED.
- The buzz puck (Dayton TT25-8 size, PUCK_D x PUCK_H, driven by pi/buzz.py) sits on the yoke, axis vertical.

Frame. A base plate with two pedestals, and a pivot post standing in a socket in each, at x = 0 on +Y and
-Y. Each post has a 6.2 mm hole at every pivot height, and a 6 mm pin goes from the post into the box's
blind lug hole. The posts stand POST_GAP off the pivot lugs: the yoke bar passes outboard of the +Y post, and
a box can slide 6 mm toward -Y off its drive pin when it comes out. The pedestals keep each post under the
220 mm bed. The pan's pivot sits PAN_PIVOT_Z up, so the pan clears the base with margin past the angle where
the levels would touch each other.

Coordinates: mm, Z up, X along the boxes, the base's bottom at z = 0, every pivot on x = y = 0. "At rest" is
mid-stroke: u = 0, every box level. Tilt phi_k about +Y (right-handed, so phi > 0 tips +X down, as in
sim/rocking.py): phi_k = -atan(u / drive_x_k) = -sign_k atan(u / R).

Writes, in out/:
    product_assembly.step    cq.Assembly of named, coloured parts, at rest
    product.png              3/4 view at the +10 deg pose (stage up 10 mm)
    product_side.png         side view from +Y (looking along -Y) at the same pose
    product_checks.json      tilt per stroke, clearances, envelope
    product.glb              nodes frame, level0-3, drive; vertices at rest, glTF axes (metres, Y up)
    product_kinematics.json  per level: pivot, sign, drive x; R, pitch, units; the GLB's axes
and ../docs/assets/product.stl, the whole machine at the +10 deg pose, coarse, for GitHub's 3D viewer. The
printable frame and drive parts go through export_all, laid on the bed the way they print: product_post (x2),
product_base, product_yoke, product_rod_a, product_rod_b.

Run from this folder (WSL):  ~/venvs/sieve/bin/python product.py [parts] [assembly]
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import cadquery as cq
from PIL import Image
import trimesh
import vtk
from vtk.util import numpy_support
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopAbs import TopAbs_REVERSED
from OCP.TopLoc import TopLoc_Location

from cadkit import OUT, export_all
import breaker_layer as bl
import frame_holder as box
import seesaw_holder as sh
import sieve_insert as si

DOC_STL = Path(__file__).resolve().parent.parent / "docs" / "assets" / "product.stl"

# the stack
PITCH = 55.0                      # pivot to pivot (WORKING_DIMENSIONS.md: 55 at +/-10 deg)
STROKE = 20.0                     # the firmware's default stroke: u runs -STROKE/2 .. +STROKE/2
CHECK_STROKES = (20.0, 30.0, 40.0)
R = sh.DRIVE_R                    # 56.71: pivot to drive pin
CLEAR = 3.0                       # the clearance seesaw_tower.py asks of neighbours at full tilt
BREAKER = "breaker:open=11.3,bar=1.6,pin_d=3.1,pin_h=8,pitch=8.5,tip=round"   # B-164f355a
LEVELS = (                        # (node, holder part, insert, sim/rocking.py sign: drive x = sign * R)
    ("level0", "seesaw_holder_drive_a", "breaker", 1),
    ("level1", "seesaw_holder_drive_b", "sieve_insert_5mm_across", -1),
    ("level2", "seesaw_holder_drive_a", "sieve_insert_2mm_across", 1),
    ("level3", "seesaw_catch_pan_drive_b", None, -1),
)

# frame
BASE_T = 6.0                      # base plate thickness
BASE_X, BASE_Y = 160.0, 172.0     # base plate footprint
BASE_HOLE_D, BASE_HOLE_IN = 5.5, 8.0   # M5 to the bench, centre in from each edge
PAN_PIVOT_Z = 58.0                # the catch pan's pivot above the base's bottom
PIN_D, PIN_L = 6.0, 30.0          # pivot pin: blind lug hole (8) + POST_GAP + post + 2 proud
POST_GAP = 8.0                    # pivot lug face to post
POST_W, POST_T = 16.0, 12.0       # post across X, along Y; its top is a half-round over the top pivot
PED_TOP, SOCKET, PED_WALL = 34.0, 18.0, 4.0   # pedestal top, post depth in it, socket wall
FIT = 0.4                         # total clearance of a printed part in a printed socket
POST_BOLT_D = 4.4                 # M4 across X through pedestal and post

# drive
ROD_W, ROD_T = 10.0, 8.0          # push rod across X, along Y
ROD_GAP = 1.5                     # drive lug face to rod
ROD_ABOVE = 8.0                   # rod top above its top pin
CROSS_PIN_L = 14.0                # 3 mm dowel, flush with the rod's outer face: 4.5 mm in the slot
YOKE_Z, YOKE_T = 34.0, 8.0        # yoke plate bottom at rest, thickness
ARM_W, BAR_W = 14.0, 12.0         # yoke arms (along Y, under each rod) and bar (along X, outboard)
BAR_GAP = 2.0                     # yoke bar to the +Y pedestal
BOSS_WALL, BOSS_H = 4.0, 18.0     # the U socket that holds each rod's foot
M3_D = 3.2
PUCK_D, PUCK_H = 50.0, 20.0       # Dayton TT25-8 size tactile transducer
PAD_RIM, PUCK_SEAT = 4.0, 1.5     # pad round the puck; locating recess depth

# derived layout (y of faces on the +Y side)
Y_LUG = box.W / 2 + sh.LUG_T                      # 58: pivot and drive lug faces
ROD_Y0, ROD_Y1 = Y_LUG + ROD_GAP, Y_LUG + ROD_GAP + ROD_T
POST_Y0, POST_Y1 = Y_LUG + POST_GAP, Y_LUG + POST_GAP + POST_T
PED_X, PED_Y0, PED_Y1 = POST_W / 2 + PED_WALL, POST_Y0 - PED_WALL, POST_Y1 + PED_WALL
BAR_Y0, BAR_Y1 = PED_Y1 + BAR_GAP, PED_Y1 + BAR_GAP + BAR_W
PUCK_Y = BAR_Y0 + PUCK_D / 2 + PAD_RIM
YOKE_TOP = YOKE_Z + YOKE_T

# output
TESS = (0.15, 0.5)                # coarse tessellation: mm, rad
TESS_ROLE = {"screen": (0.3, 3.0),    # the tapered holes' corners are tiny cones: one facet each is plenty
             "breaker": (0.3, 0.8)}   # 3.1 mm pins: about 8 facets round
SUPERSAMPLE = 2                   # render this many times larger, then scale down (FXAA blacks out offscreen)
COLORS = {"frame": (0.56, 0.58, 0.61), "steel": (0.80, 0.81, 0.84), "holder": (0.40, 0.55, 0.73),
          "screen": (0.96, 0.66, 0.20), "breaker": (0.27, 0.66, 0.42), "drive": (0.88, 0.27, 0.20),
          "puck": (0.17, 0.17, 0.19)}
GROUPS = ("frame", "level0", "level1", "level2", "level3", "drive")
TO_GLTF = np.array([[1.0, 0, 0], [0, 0, 1.0], [0, -1.0, 0]])   # Z-up (x, y, z) -> Y-up (x, z, -y)


def pivot_z(k):
    return PAN_PIVOT_Z + (len(LEVELS) - 1 - k) * PITCH


def phi(k, u):
    """Level k's tilt in degrees about +Y (phi > 0 tips +X down) when the stage is u above mid-stroke."""
    return -math.degrees(math.atan(u / (LEVELS[k][3] * R)))


def blk(x0, x1, y0, y1, z0, z1):
    """An axis-aligned box between two corners."""
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(axis, r, p0, length):
    """A cylinder of radius r from point p0, `length` along +axis ("x", "y" or "z"; negative: the other way)."""
    d = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis]
    s = 1 if length > 0 else -1
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(r, abs(length), cq.Vector(*p0), cq.Vector(*(s * c for c in d))))


# ---------- the levels ----------

def insert(name):
    if name == "breaker":
        return bl.layer(bl.spec(BREAKER))[0]
    return si.insert_across(name)[0]


def level(k):
    """Level k's pieces at rest: [(name, role, shape)]."""
    node, holder_name, insert_name, _ = LEVELS[k]
    holder, info = sh.PARTS[holder_name]()
    z = pivot_z(k) - info["pivot_mm"][2]               # the part's own pivot onto this level's
    pieces = [(f"{node}_{holder_name}", "holder", holder.translate((0, 0, z)))]
    if insert_name:
        role = "breaker" if insert_name == "breaker" else "screen"
        pieces.append((f"{node}_{insert_name}", role, insert(insert_name).translate((0, 0, z + box.LEDGE_T))))
    return pieces


# ---------- the frame ----------

def post(side=1):
    """A pivot post at x = 0 on the +Y (side 1) or -Y side: standing in its pedestal, a hole at each pivot."""
    y0, y1 = sorted((side * POST_Y0, side * POST_Y1))
    top = pivot_z(0)
    p = blk(-POST_W / 2, POST_W / 2, y0, y1, PED_TOP - SOCKET, top).union(cyl("y", POST_W / 2, (0, y0, top), POST_T))
    for k in range(len(LEVELS)):
        p = p.cut(cyl("y", sh.PIN_D / 2, (0, y0 - 1, pivot_z(k)), POST_T + 2))
    return p.cut(cyl("x", POST_BOLT_D / 2, (-POST_W, (y0 + y1) / 2, PED_TOP - SOCKET / 2), 2 * POST_W))


def base():
    """The base plate, a pedestal with a post socket at each side, M5 holes at the corners."""
    hx, hy = BASE_X / 2 - BASE_HOLE_IN, BASE_Y / 2 - BASE_HOLE_IN
    b = blk(-BASE_X / 2, BASE_X / 2, -BASE_Y / 2, BASE_Y / 2, 0, BASE_T)
    b = b.cut(cq.Workplane("XY").pushPoints([(sx * hx, sy * hy) for sx in (1, -1) for sy in (1, -1)])
              .circle(BASE_HOLE_D / 2).extrude(BASE_T))
    for side in (1, -1):
        y0, y1 = sorted((side * PED_Y0, side * PED_Y1))
        p0, p1 = sorted((side * (POST_Y0 - FIT / 2), side * (POST_Y1 + FIT / 2)))
        ped = blk(-PED_X, PED_X, y0, y1, BASE_T - 0.01, PED_TOP)
        ped = ped.cut(blk(-POST_W / 2 - FIT / 2, POST_W / 2 + FIT / 2, p0, p1, PED_TOP - SOCKET, PED_TOP + 1))
        b = b.union(ped.cut(cyl("x", POST_BOLT_D / 2, (-PED_X - 1, (y0 + y1) / 2, PED_TOP - SOCKET / 2), 2 * PED_X + 2)))
    return b


def pivot_pins():
    """A 6 mm pin from each post into each box's blind lug hole."""
    return [cyl("y", PIN_D / 2, (0, side * (Y_LUG - sh.PIN_DEPTH), pivot_z(k)), side * PIN_L)
            for k in range(len(LEVELS)) for side in (1, -1)]


# ---------- the drive ----------

def rod_levels(side):
    return [k for k, lv in enumerate(LEVELS) if lv[3] == side]


def rod(side):
    """Push rod A (side 1, x = +R) or B (side -1): from the yoke up past its top pin, a hole for each cross-pin."""
    ks = rod_levels(side)
    x = side * R
    r = blk(x - ROD_W / 2, x + ROD_W / 2, ROD_Y0, ROD_Y1, YOKE_TOP, pivot_z(min(ks)) + ROD_ABOVE)
    for k in ks:
        r = r.cut(cyl("y", sh.DRIVE_PIN_D / 2, (x, ROD_Y0 - 1, pivot_z(k)), ROD_T + 2))
    return r.cut(cyl("x", M3_D / 2, (x - ROD_W, (ROD_Y0 + ROD_Y1) / 2, YOKE_TOP + BOSS_H / 2), 2 * ROD_W))


def cross_pins(side):
    """3 mm dowels through the rod, flush outside, reaching into each driven box's slot."""
    return [cyl("y", sh.DRIVE_PIN_D / 2, (side * R, ROD_Y1, pivot_z(k)), -CROSS_PIN_L) for k in rod_levels(side)]


def yoke():
    """The yoke at rest: arms under the rods, a bar outboard of the +Y post, a pad for the puck, a U socket
    for each rod's foot, and frame_holder's mounting tab at the +X end."""
    z0, z1 = YOKE_Z, YOKE_TOP
    y = blk(-R - ARM_W / 2, R + ARM_W / 2, BAR_Y0, BAR_Y1, z0, z1)
    y = y.union(cyl("z", PUCK_D / 2 + PAD_RIM, (0, PUCK_Y, z0), YOKE_T))
    for side in (1, -1):
        x = side * R
        y = y.union(blk(x - ARM_W / 2, x + ARM_W / 2, ROD_Y0, BAR_Y0 + 1, z0, z1))
        boss = blk(x - ROD_W / 2 - BOSS_WALL, x + ROD_W / 2 + BOSS_WALL, ROD_Y0, ROD_Y1 + BOSS_WALL, z1 - 0.01, z1 + BOSS_H)
        boss = boss.cut(blk(x - (ROD_W + FIT) / 2, x + (ROD_W + FIT) / 2, ROD_Y0 - 1, ROD_Y1 + FIT / 2, z1, z1 + BOSS_H + 1))
        y = y.union(boss.cut(cyl("x", M3_D / 2, (x - ROD_W, (ROD_Y0 + ROD_Y1) / 2, z1 + BOSS_H / 2), 2 * ROD_W)))
    y = y.cut(cyl("z", (PUCK_D + 0.6) / 2, (0, PUCK_Y, z1 - PUCK_SEAT), PUCK_SEAT + 1))
    tx, yc = R + ARM_W / 2, (BAR_Y0 + BAR_Y1) / 2
    tab = blk(tx - 1, tx + box.TAB_L, yc - box.TAB_T / 2, yc + box.TAB_T / 2, z0, z0 + box.H)
    return y.union(tab.cut(cyl("y", box.HOLE_D / 2, (tx + box.TAB_L - box.HOLE_FROM_END, yc - box.TAB_T, z0 + box.H / 2),
                               2 * box.TAB_T)))


def stage_bolt():
    """Where the yoke's tab hole is at rest: the ASSUMED stage interface."""
    return [round(R + ARM_W / 2 + box.TAB_L - box.HOLE_FROM_END, 2), round((BAR_Y0 + BAR_Y1) / 2, 2), YOKE_Z + box.H / 2]


def puck():
    """Stand-in for the TT25-8: a disc in the yoke's recess, axis vertical."""
    return (cq.Workplane("XY").workplane(offset=YOKE_TOP - PUCK_SEAT).center(0, PUCK_Y).circle(PUCK_D / 2)
            .extrude(PUCK_H).edges(">Z").fillet(2.0))


# ---------- the assembly ----------

def pieces():
    """Every piece at rest: {group: [(name, role, cq.Shape)]}."""
    out = {"frame": [("frame_base", "frame", base()), ("frame_post_py", "frame", post(1)), ("frame_post_my", "frame", post(-1))]
           + [(f"frame_pivot_pin_{i}", "steel", p) for i, p in enumerate(pivot_pins())]}
    for k in range(len(LEVELS)):
        out[LEVELS[k][0]] = level(k)
    out["drive"] = ([("drive_yoke", "drive", yoke()), ("drive_rod_a", "drive", rod(1)), ("drive_rod_b", "drive", rod(-1)),
                     ("drive_puck", "puck", puck())]
                    + [(f"drive_cross_pin_{i}", "steel", p) for i, p in enumerate(cross_pins(1) + cross_pins(-1))])
    return {g: [(n, role, w.val()) for n, role, w in ps] for g, ps in out.items()}


def posed(shape, group, u):
    """A shape of `group` moved to stage position u."""
    if group == "drive":
        return shape.translate(cq.Vector(0, 0, u))
    if group.startswith("level"):
        k = int(group[5:])
        p = cq.Vector(0, 0, pivot_z(k))
        return shape.rotate(p, p + cq.Vector(0, 1, 0), phi(k, u))
    return shape


def pose_matrix(group, u):
    """The same move as a 4 x 4 matrix, for meshes."""
    m = np.eye(4)
    if group == "drive":
        m[2, 3] = u
    elif group.startswith("level"):
        a, zp = math.radians(phi(int(group[5:]), u)), pivot_z(int(group[5:]))
        c, s = math.cos(a), math.sin(a)
        m[:3, :3] = [[c, 0, s], [0, 1, 0], [-s, 0, c]]
        m[:3, 3] = m[:3, :3] @ [0, 0, -zp] + [0, 0, zp]
    return m


def compound(shapes):
    return cq.Compound.makeCompound(list(shapes))


def save_step(parts):
    assy = cq.Assembly(name="product")
    for g in GROUPS:
        sub = cq.Assembly(name=g)
        for name, role, s in parts[g]:
            sub.add(s, name=name, color=cq.Color(*COLORS[role]))
        assy.add(sub, name=g)
    assy.export(str(OUT / "product_assembly.step"))


# ---------- checks ----------

def holders(parts, u):
    return [posed(parts[LEVELS[k][0]][0][2], LEVELS[k][0], u) for k in range(len(LEVELS))]


def neighbour_gaps(parts, u):
    """Gap between each pair of neighbouring boxes (lugs included) with the stage at u."""
    h = holders(parts, u)
    return [h[k].distance(h[k + 1]) for k in range(len(h) - 1)]


def touch_stroke(parts, gap):
    """The largest stroke (mm) that keeps every neighbour pair at least `gap` apart over a cycle."""
    lo, hi = 0.0, 40.0
    while hi - lo > 0.05:
        mid = (lo + hi) / 2
        ok = min(min(neighbour_gaps(parts, s * mid / 2)) for s in (1, -1)) >= gap
        lo, hi = (mid, hi) if ok else (lo, mid)
    return lo


def checks(parts):
    u0 = STROKE / 2
    poses = (u0, -u0)
    rnd = lambda v: round(float(v), 2)
    out = {"units": "mm, deg", "pitch_mm": PITCH, "R_mm": rnd(R), "default_stroke_mm": STROKE,
           "tilt_law": "phi = atan((stroke / 2) / R): the pin rides a slot fixed in the box, the rod stays vertical"}
    rows = []
    for s in CHECK_STROKES:
        gaps = [min(neighbour_gaps(parts, sg * s / 2)) for sg in (1, -1)]
        rows.append({"stroke_mm": s, "tilt_deg": rnd(math.degrees(math.atan(s / 2 / R))),
                     "asin_formula_deg_for_reference": rnd(math.degrees(math.asin(s / 2 / R))),
                     "min_neighbour_gap_mm": rnd(min(gaps)), "neighbours_collide": min(gaps) <= 0.0})
    out["tilt_per_stroke"] = rows
    pairs = {}
    for u in poses:
        for k, g in enumerate(neighbour_gaps(parts, u)):
            key = f"level{k}-level{k + 1}"
            pairs[key] = rnd(min(g, pairs.get(key, 1e9)))
    out["neighbour_gap_at_default_stroke_mm"] = pairs
    s3, s0 = touch_stroke(parts, CLEAR), touch_stroke(parts, 0.01)
    out["stroke_limit"] = {f"max_stroke_with_{CLEAR:g}mm_gap_mm": rnd(s3), "tilt_deg": rnd(math.degrees(math.atan(s3 / 2 / R))),
                           "stroke_where_boxes_touch_mm": rnd(s0), "tilt_where_boxes_touch_deg": rnd(math.degrees(math.atan(s0 / 2 / R)))}

    def gap(a, b, ga, gb):
        return rnd(min(posed(a, ga, u).distance(posed(b, gb, u)) for u in poses))

    frame = dict((n, s) for n, _, s in parts["frame"])
    drive = dict((n, s) for n, _, s in parts["drive"])
    lv = {LEVELS[k][0]: parts[LEVELS[k][0]][0][2] for k in range(len(LEVELS))}
    rods = {"rod_a": drive["drive_rod_a"], "rod_b": drive["drive_rod_b"]}
    out["rod_to_box_mm"] = {f"{r}-{g}": gap(s, h, "drive", g) for r, s in rods.items() for g, h in lv.items()}
    pins = [(n, s) for n, s in drive.items() if "cross_pin" in n]
    driven = [LEVELS[k][0] for side in (1, -1) for k in rod_levels(side)]
    out["cross_pin_in_slot_mm"] = {f"{n}-{g}": gap(s, lv[g], "drive", g) for (n, s), g in zip(pins, driven)}
    posts = {"post_py": frame["frame_post_py"], "post_my": frame["frame_post_my"]}
    out["post_to_box_mm"] = {f"{p}-{g}": gap(s, h, "frame", g) for p, s in posts.items() for g, h in lv.items()}
    fixed = compound([s for n, s in frame.items() if "pivot_pin" not in n])
    out["base_and_posts_to_drive_mm"] = gap(fixed, compound(drive.values()), "frame", "drive")
    out["pivot_pins_to_drive_mm"] = gap(compound([s for n, s in frame.items() if "pivot_pin" in n]), compound(drive.values()), "frame", "drive")
    out["base_and_pedestals_to_catch_pan_mm"] = gap(frame["frame_base"], lv["level3"], "frame", "level3")
    yp = compound([drive["drive_yoke"], drive["drive_puck"]])
    out["yoke_and_puck_to_boxes_mm"] = {g: gap(yp, h, "drive", g) for g, h in lv.items()}
    pan_low = lambda deg: pivot_z(3) - (sh.CATCH_DEPTH + sh.PIVOT_Z) * math.cos(math.radians(deg)) - box.L / 2 * math.sin(math.radians(deg))
    out["base_plate_under_pan_closed_form"] = {"at_10deg_mm": rnd(pan_low(10) - BASE_T), "at_15deg_mm": rnd(pan_low(15) - BASE_T)}
    out["inserts_below_rim"] = {n: rnd(s.BoundingBox().zmax - (pivot_z(int(g[5:])) + sh.PIVOT_Z)) for g in GROUPS[1:4]
                                for n, role, s in parts[g][1:]}
    out["inserts_below_rim_note"] = "insert top minus box rim at rest; negative = below the rim, inside the box"
    bbs = [compound([posed(s, g, u) for g in GROUPS for _, _, s in parts[g]]).BoundingBox() for u in (0.0, u0, -u0)]
    env = lambda bb: {"x": [rnd(bb.xmin), rnd(bb.xmax)], "y": [rnd(bb.ymin), rnd(bb.ymax)], "z": [rnd(bb.zmin), rnd(bb.zmax)],
                      "size": [rnd(bb.xlen), rnd(bb.ylen), rnd(bb.zlen)]}
    swept = bbs[0]
    for bb in bbs[1:]:
        swept = swept.add(bb)
    out["envelope_at_rest_mm"] = env(bbs[0])
    out["envelope_swept_default_stroke_mm"] = env(swept)
    out["stage_bolt_at_rest_mm"] = {"xyz": stage_bolt(), "axis": "Y", "hole_d": box.HOLE_D, "status": "ASSUMED: stage not measured"}
    out["pivot_z_mm"] = {LEVELS[k][0]: pivot_z(k) for k in range(len(LEVELS))}
    return out


# ---------- meshes ----------

def tessellate(shape, tol=TESS[0], ang=TESS[1]):
    """Vertices (n x 3) and triangles (m x 3) of a shape, one vertex set per face (sharp edges stay sharp)."""
    BRepMesh_IncrementalMesh(shape.wrapped, tol, False, ang, True)
    vs, fs, n = [], [], 0
    for f in shape.Faces():
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(f.wrapped, loc)
        if tri is None:
            continue
        t = loc.Transformation()
        pts = [tri.Node(i).Transformed(t) for i in range(1, tri.NbNodes() + 1)]
        idx = np.array([[tri.Triangle(i).Value(j) for j in (1, 2, 3)] for i in range(1, tri.NbTriangles() + 1)]) - 1 + n
        if f.wrapped.Orientation() == TopAbs_REVERSED:
            idx = idx[:, ::-1]
        vs.append(np.array([(p.X(), p.Y(), p.Z()) for p in pts]))
        fs.append(idx)
        n += len(pts)
    return np.vstack(vs), np.vstack(fs).astype(np.int64)


def meshes(parts):
    """{group: {role: (V, F)}} at rest, the pieces of one role in a group merged."""
    out = {}
    for g in GROUPS:
        by_role = {}
        for _, role, s in parts[g]:
            by_role.setdefault(role, []).append(tessellate(s, *TESS_ROLE.get(role, TESS)))
        out[g] = {}
        for role, ms in by_role.items():
            offs = np.cumsum([0] + [len(v) for v, _ in ms[:-1]])
            out[g][role] = (np.vstack([v for v, _ in ms]), np.vstack([f + o for (_, f), o in zip(ms, offs)]))
    return out


def moved(mesh, group, u):
    v, f = mesh
    m = pose_matrix(group, u)
    return v @ m[:3, :3].T + m[:3, 3], f


def write_stl(mesh_set, u, path):
    vs, fs, n = [], [], 0
    for g, roles in mesh_set.items():
        for role, m in roles.items():
            v, f = moved(m, g, u)
            vs.append(v)
            fs.append(f + n)
            n += len(v)
    trimesh.Trimesh(np.vstack(vs), np.vstack(fs), process=False).export(str(path), file_type="stl")


def write_glb(mesh_set, path):
    """One node per moving group under the scene root, a child mesh per role with that role's material.
    Vertices at rest in glTF axes: metres, Y up, (x, y, z) mm Z-up -> (x, z, -y) / 1000."""
    scene = trimesh.Scene()
    mats = {r: trimesh.visual.material.PBRMaterial(name=r, baseColorFactor=[*c, 1.0], roughnessFactor=0.55,
                                                    metallicFactor=0.6 if r == "steel" else 0.0) for r, c in COLORS.items()}
    for g in GROUPS:
        scene.graph.update(frame_from=scene.graph.base_frame, frame_to=g, matrix=np.eye(4))
        for role, (v, f) in mesh_set[g].items():
            m = trimesh.Trimesh(v @ TO_GLTF.T / 1000.0, f, process=False)
            m.visual = trimesh.visual.TextureVisuals(material=mats[role])
            scene.add_geometry(m, node_name=f"{g}_{role}", geom_name=f"{g}_{role}", parent_node_name=g)
    path.write_bytes(trimesh.exchange.gltf.export_glb(scene, include_normals=True))


def kinematics():
    lv = []
    for k, (node, holder, ins, sign) in enumerate(LEVELS):
        p = [0.0, 0.0, pivot_z(k)]
        lv.append({"node": node, "holder": holder, "insert": ins or "none (catch pan)", "pivot_mm": p, "sign": sign,
                   "drive_x_mm": round(sign * R, 3), "rod": "A" if sign > 0 else "B",
                   "pivot_gltf_m": [round(c, 6) for c in (TO_GLTF @ p / 1000.0)]})
    return {
        "units": "mm (CAD, Z up); the GLB is in metres, Y up",
        "R_mm": round(R, 3), "pitch_mm": PITCH, "default_stroke_mm": STROKE, "default_tilt_deg": 10.0,
        "stage_u": "u = stage position above mid-stroke, mm; the firmware's default stroke runs u = -10 .. +10",
        "tilt_cad": "level k turns by phi_k = -sign_k * atan(u / R) (radians) about +Y through pivot_mm "
                    "(right-handed; phi > 0 tips +X down, as sim/rocking.py). Equivalently phi_k = -atan(u / drive_x_k).",
        "sign": "sim/rocking.py's sign_k: +1, -1, +1, -1 from the top. drive_x_mm = sign * R.",
        "drive": {"node": "drive", "moves": "translates by u along +Z (CAD) = +Y (glTF); u in mm, so u / 1000 m in the GLB"},
        "frame": {"node": "frame", "moves": "static"},
        "levels": lv,
        "glb": {"file": "product.glb", "units": "m", "up": "+Y", "pose": "rest (u = 0, every box level)",
                "mapping": "gltf = (x, z, -y) / 1000 from CAD (x, y, z) in mm, Z up",
                "level_rotation": "rotate the level node about +Z (glTF) through pivot_gltf_m by sign_k * atan(u / R) radians: "
                                  "positive lifts the +X end",
                "nodes": list(GROUPS), "children": "<group>_<role>: one mesh per role, material named by the role",
                "materials": {r: [round(c, 3) for c in rgb] for r, rgb in COLORS.items()}},
    }


# ---------- renders ----------

def polydata(v, f):
    pts = vtk.vtkPoints()
    pts.SetData(numpy_support.numpy_to_vtk(np.ascontiguousarray(v, dtype=np.float64), deep=True))
    cells = vtk.vtkCellArray()
    offsets = numpy_support.numpy_to_vtkIdTypeArray(np.arange(0, 3 * len(f) + 1, 3, dtype=np.int64), deep=True)
    conn = numpy_support.numpy_to_vtkIdTypeArray(np.ascontiguousarray(f.ravel(), dtype=np.int64), deep=True)
    cells.SetData(offsets, conn)
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.SetPolys(cells)
    return pd


def actor(v, f, rgb, edges):
    """A shaded actor, plus its CAD edges as dark lines: each BRep face is its own mesh patch, so the face
    outlines are the mesh's boundary edges."""
    pd = polydata(v, f)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(pd)
    normals.SetFeatureAngle(35)
    normals.SplittingOn()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    a = vtk.vtkActor()
    a.SetMapper(mapper)
    p = a.GetProperty()
    p.SetColor(*rgb)
    p.SetAmbient(0.2)
    p.SetDiffuse(0.8)
    p.SetSpecular(0.12)
    p.SetSpecularPower(20)
    if not edges:
        return [a]
    fe = vtk.vtkFeatureEdges()
    fe.SetInputData(pd)
    fe.BoundaryEdgesOn()
    fe.FeatureEdgesOff()
    fe.ManifoldEdgesOff()
    fe.NonManifoldEdgesOff()
    em = vtk.vtkPolyDataMapper()
    em.SetInputConnection(fe.GetOutputPort())
    em.ScalarVisibilityOff()
    ea = vtk.vtkActor()
    ea.SetMapper(em)
    ea.GetProperty().SetColor(*(c * 0.4 for c in rgb))
    ea.GetProperty().SetLineWidth(1.5 * SUPERSAMPLE)
    return [a, ea]


def render(mesh_set, u, png, view, labels=(), title="", size=(1500, 1500)):
    """Offscreen multi-colour VTK render of the meshes posed at u, drawn SUPERSAMPLE times larger and scaled
    down for smooth edges. view: (camera direction, view up, parallel projection?, zoom). labels: (text,
    world point, pixel offset at the final size)."""
    ss = SUPERSAMPLE
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    ren.SetBackground2(0.88, 0.90, 0.94)
    ren.GradientBackgroundOn()
    for g, roles in mesh_set.items():
        for role, m in roles.items():
            v, f = moved(m, g, u)
            for a in actor(v, f, COLORS[role], edges=role in ("holder", "frame", "drive")):
                ren.AddActor(a)
    kit = vtk.vtkLightKit()
    kit.SetKeyLightIntensity(0.85)
    kit.AddLightsToRenderer(ren)
    direction, up, parallel, zoom = view
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(0, 0, 0)
    cam.SetPosition(*direction)
    cam.SetViewUp(*up)
    cam.SetParallelProjection(parallel)
    cam.SetViewAngle(20)
    ren.ResetCamera()
    cam.Zoom(zoom)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.AddRenderer(ren)
    win.SetSize(size[0] * ss, size[1] * ss)
    win.Render()
    for text, xyz, (dx, dy) in labels:
        ren.SetWorldPoint(*xyz, 1.0)
        ren.WorldToDisplay()
        x, y, _ = ren.GetDisplayPoint()
        ren.AddViewProp(text_actor(text, x + dx * ss, y + dy * ss, 24 * ss))
    if title:
        ren.AddViewProp(text_actor(title, 30 * ss, (size[1] - 50) * ss, 28 * ss, bold=True))
    win.Render()
    grab = vtk.vtkWindowToImageFilter()
    grab.SetInput(win)
    grab.Update()
    img = grab.GetOutput()
    w, h, _ = img.GetDimensions()
    rgb = numpy_support.vtk_to_numpy(img.GetPointData().GetScalars()).reshape(h, w, -1)[::-1, :, :3]
    Image.fromarray(np.ascontiguousarray(rgb)).resize(size, Image.LANCZOS).save(png)


def text_actor(text, x, y, size, bold=False):
    t = vtk.vtkTextActor()
    t.SetInput(text)
    t.SetDisplayPosition(int(x), int(y))
    p = t.GetTextProperty()
    p.SetFontSize(size)
    p.SetColor(0.12, 0.13, 0.16)
    p.SetBold(bold)
    p.SetBackgroundColor(1, 1, 1)
    p.SetBackgroundOpacity(0.0 if bold else 0.75)
    return t


def level_labels(u, anchor, dx, dy=-12):
    """A label for each level, anchored at (x, y) beside it at its pivot height."""
    names = {"breaker": "breaker", "sieve_insert_5mm_across": "5 mm screen", "sieve_insert_2mm_across": "2 mm screen"}
    out = []
    for k, (_, _, ins, _) in enumerate(LEVELS):
        tilt = -phi(k, u)
        out.append((f"L{k} {names.get(ins, 'catch pan')}: {'+' if tilt > 0 else '-'}X end up {abs(tilt):.0f}\N{DEGREE SIGN}",
                    (*anchor, pivot_z(k)), (dx, dy)))
    return out


def pose_title(u):
    return f"Stage up {u:g} mm of the {STROKE:g} mm stroke: every box at {math.degrees(math.atan(u / R)):.0f}\N{DEGREE SIGN}, neighbours opposite"


def hero(ms, u, png, size=(1500, 1500)):
    """3/4 view from -X, +Y, above: the drive side, and down into the boxes."""
    tab = (R + ARM_W / 2 + box.TAB_L, (BAR_Y0 + BAR_Y1) / 2, YOKE_Z + u + box.H)
    labels = level_labels(u, (-box.L / 2, -box.W / 2), 16) + [
        ("rod A", (R, ROD_Y1, 150), (-100, 0)), ("rod B", (-R, ROD_Y1, 125), (14, 0)),
        ("pivot post", (0, POST_Y1, 205), (14, 0)),
        ("yoke + buzz puck", (0, PUCK_Y + PUCK_D / 2, YOKE_Z + u), (-60, -60)),
        ("stage tab (interface ASSUMED)", tab, (-330, 14))]
    render(ms, u, png, ((-0.9, 1.3, 0.95), (0, 0, 1), False, 0.9), labels, pose_title(u), size)


def side(ms, u, png, size=(1500, 1500)):
    """Looking along -Y from the +Y side (so +X is on the left), parallel projection."""
    labels = level_labels(u, (-box.L / 2 - 6, 0), 24) + [
        ("rod A (x = +R)", (R, ROD_Y1, 142), (-190, 0)), ("rod B (x = -R)", (-R, ROD_Y1, 142), (14, 0)),
        ("yoke + puck", (0, PUCK_Y, YOKE_Z + u), (-60, -40)),
        ("+X", (box.L / 2, 0, 0), (-10, -45)), ("-X", (-box.L / 2, 0, 0), (-10, -45))]
    render(ms, u, png, ((0, 1, 0), (0, 0, 1), True, 1.0), labels, pose_title(u) + " (side view from +Y)", size)


# ---------- printable parts ----------

def lay_flat(part):
    """Turn a part standing along Z onto its side so its Y holes print vertical, then put it on the bed."""
    p = part.rotate((0, 0, 0), (1, 0, 0), -90)
    bb = p.val().BoundingBox()
    return p.translate((-bb.center.x, -bb.center.y, -bb.zmin))


def on_bed(part):
    bb = part.val().BoundingBox()
    return part.translate((-bb.center.x, -bb.center.y, -bb.zmin))


PARTS = {
    "product_post": lambda: (lay_flat(post(1)), {"print": "on its side, pin holes vertical", "count": 2,
                                                 "pin_hole_d_mm": sh.PIN_D, "pivot_z_mm": [pivot_z(k) for k in range(len(LEVELS))]}),
    "product_base": lambda: (on_bed(base()), {"print": "plate on the bed, pedestals up", "count": 1}),
    "product_yoke": lambda: (on_bed(yoke()), {"print": "plate on the bed", "count": 1, "stage_bolt_at_rest_mm": stage_bolt(),
                                              "stage_interface": "ASSUMED"}),
    "product_rod_a": lambda: (lay_flat(rod(1)), {"print": "on its side, cross-pin holes vertical", "count": 1,
                                                  "drives": [LEVELS[k][0] for k in rod_levels(1)]}),
    "product_rod_b": lambda: (lay_flat(rod(-1)), {"print": "on its side, cross-pin holes vertical", "count": 1,
                                                   "drives": [LEVELS[k][0] for k in rod_levels(-1)]}),
}


def build_assembly():
    t0 = time.time()
    parts = pieces()
    print(f"built {sum(len(v) for v in parts.values())} pieces in {time.time() - t0:.0f} s", flush=True)
    save_step(parts)
    print(f"step written ({time.time() - t0:.0f} s)", flush=True)
    c = checks(parts)
    print(f"checks done ({time.time() - t0:.0f} s)", flush=True)
    ms = meshes(parts)
    del parts
    tris = {g: {r: len(f) for r, (_, f) in roles.items()} for g, roles in ms.items()}
    print("triangles", json.dumps(tris), flush=True)
    u = STROKE / 2
    hero(ms, u, OUT / "product.png")
    side(ms, u, OUT / "product_side.png")
    print(f"renders done ({time.time() - t0:.0f} s)", flush=True)
    write_stl(ms, u, DOC_STL)
    write_glb(ms, OUT / "product.glb")
    c["files_bytes"] = {"product.glb": (OUT / "product.glb").stat().st_size, "docs/assets/product.stl": DOC_STL.stat().st_size}
    c["triangles"] = tris
    (OUT / "product_checks.json").write_text(json.dumps(c, indent=2), encoding="utf-8")
    (OUT / "product_kinematics.json").write_text(json.dumps(kinematics(), indent=2), encoding="utf-8")
    print(json.dumps(c, indent=1))


if __name__ == "__main__":
    what = sys.argv[1:] or ["parts", "assembly"]
    if "parts" in what:
        for n, make in PARTS.items():
            part, info = make()
            print(n, json.dumps(export_all(part, n, info)), flush=True)
    if "assembly" in what:
        build_assembly()
