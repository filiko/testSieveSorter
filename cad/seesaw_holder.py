"""Seesaw holder box and catch pan: frame_holder.py's box re-made for a tray that tips about a pivot across
its middle (docs/SYSTEM.md section 3), with neighbours tipping opposite ways.

    seesaw_holder      the holder box with no +X mounting tab and a pivot lug on each long wall
    seesaw_catch_pan   the bottom level: a solid floor, CATCH_DEPTH deeper than a box, and an inward lip
    seesaw_holder_drive_a     seesaw_holder plus a drive lug toward +X (levels 0 and 2 of cad/product.py)
    seesaw_holder_drive_b     seesaw_holder plus a drive lug toward -X (level 1)
    seesaw_catch_pan_drive_b  seesaw_catch_pan plus a drive lug toward -X (level 3, the bottom)

Changes from frame_holder.py (same 140 x 104 x 25 body, same pocket, ledge and open bottom, so every
insert, plinko layer, gated container and the breaker layer drops in unchanged):
- No +X tab. A middle pivot doesn't need it, and the tab ends decide how close the levels can hang
  (seesaw_tower.py): with it gone, levels hang about half as far apart at +/-10 deg, so specimens drop
  about half as far between levels (the clump session found those drops give the largest impact force).
- A pivot lug on the middle of each long wall: a D-shaped plate LUG_W wide standing LUG_T out from the
  wall, from the bed up to a half-round top, with a blind PIN_D hole along Y at PIVOT_Z (mid-height, the
  pivot the sim assumes). A 6 mm rod or shoulder bolt from each post of the rig goes in; the two holes
  are coaxial. The lug prints from the bed, so nothing overhangs but the small hole's top.
- No finger notches: the lugs sit where they were. Lift the box off its pins to swap inserts, or reach
  the pull tabs from above (levels hang 50 mm or more apart).

The catch pan keeps a box's top 25 mm (the same rim, and the pivot the same 12.5 mm under it) and reaches
CATCH_DEPTH further down, where nothing hangs below it, so it doesn't change the pitch. Its rim has an
inward lip, LIP_T thick with a 45 deg underside (prints without supports), leaving exactly the 122 x 82
open bottom of the box above: everything falling from above still lands in the pan, and grains that
bounce at the ends hit the lip instead of leaving (the 11:20 renders lost grains over the ends).

The drive variants (cad/product.py, cad/PRODUCT.md) let one linear stage rock the whole stack. A yoke on
the stage carries two vertical push rods on the +Y side: rod A at x = +DRIVE_R drives levels 0 and 2, rod B
at x = -DRIVE_R drives levels 1 and 3. So each box gets a third lug, a drive lug, on its +Y long wall:
- the pivot lug's D shape (LUG_W wide, LUG_T out, from the bed up), centred on its slot;
- a blind horizontal slot along the box's X, DRIVE_SLOT_W wide, LUG_T deep (the lug's whole thickness,
  nothing into the wall), at the pivot height;
- a DRIVE_PIN_D cross-pin on the rod rides in the slot.
The rod stays vertical at x = DRIVE_R, so a stage move u tips the box by atan(u / DRIVE_R) and the pin
slides outward along the slot by DRIVE_R (1 / cos(theta) - 1): 0.9 mm at 10 deg. DRIVE_R puts the firmware's
default 20 mm stroke at +/-10 deg exactly. The slot runs from DRIVE_SLACK inside the pin's rest position to
DRIVE_SLACK past its position at DRIVE_MAX_DEG, so the slot never stops the rock (the levels touch first).
The lug stays inside the box's outline in X and Z, so it doesn't change the pitch.

Prints with the flat bottom on the bed, no supports.

Run from this folder:  <venv python> seesaw_holder.py [seesaw_holder seesaw_catch_pan seesaw_holder_drive_a ...]
"""
import json
import math
import sys
import cadquery as cq
from cadkit import export_all
import frame_holder as box

PIVOT_Z = box.H / 2               # pivot height above the box bottom (the sim's assumption)
PIN_D = 6.2                       # blind hole for a 6 mm rod or shoulder bolt
PIN_DEPTH = 8.0                   # from the lug face: through the lug and half the wall
LUG_W, LUG_T = 16.0, 6.0          # lug width along X, how far it stands out from the long wall
CATCH_DEPTH = 20.0                # the catch pan reaches this much further down than a box
LIP_T = 2.0                       # the pan's inward lip: flat top thickness, then a 45 deg underside
FLOOR_T = 3.0                     # the pan's solid floor
DRIVE_R = 10.0 / math.tan(math.radians(10.0))   # 56.71: pivot to the drive pin at rest; a 20 mm stroke tips +/-10 deg
DRIVE_PIN_D = 3.0                 # the push rod's cross-pin: a 3 mm steel dowel
DRIVE_SLOT_W = 3.3                # slot width: the pin plus 0.3
DRIVE_MAX_DEG = 20.0              # the slot is long enough for this tilt (a 41 mm stroke)
DRIVE_SLACK = 0.5                 # slot length past the pin's travel at each end


def cyl_y(r, y0, length, z):
    """A cylinder along Y from y0, `length` long (negative: toward -Y), centred on x = 0 at height z."""
    d = 1 if length > 0 else -1
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(r, abs(length), cq.Vector(0, y0, z), cq.Vector(0, d, 0)))


def walls(h):
    """A ring of the box's outer walls, h tall."""
    return (cq.Workplane("XY").box(box.L, box.W, h, centered=(True, True, False))
            .cut(cq.Workplane("XY").box(box.L - 2 * box.WALL, box.W - 2 * box.WALL, h, centered=(True, True, False))))


def body():
    """frame_holder's box with the +X tab cut off at the end wall and the finger notches filled."""
    b = box.frame().intersect(cq.Workplane("XY").box(box.L, box.W, box.H, centered=(True, True, False)))
    return b.union(walls(box.H).intersect(cq.Workplane("XY").box(box.NOTCH_W + 2, box.W, box.H,
                                                                 centered=(True, True, False))))


def with_lugs(part, pivot_z):
    """Add a pivot lug to each long wall at x = 0 and drill the blind pin holes, centred pivot_z up."""
    r = LUG_W / 2
    for sy in (1, -1):
        y_wall, y_face = sy * box.W / 2, sy * (box.W / 2 + LUG_T)
        plate = cq.Workplane("XY").box(LUG_W, LUG_T, pivot_z, centered=(True, False, False))
        plate = plate.translate((0, box.W / 2 if sy > 0 else -box.W / 2 - LUG_T, 0))
        part = part.union(plate).union(cyl_y(r, y_wall, sy * LUG_T, pivot_z))
        part = part.cut(cyl_y(PIN_D / 2, y_face, -sy * PIN_DEPTH, pivot_z))
    return part


def holder():
    part = with_lugs(body(), PIVOT_Z)
    return part, {"pivot_mm": [0.0, 0.0, PIVOT_Z], "pin_hole_mm": {"d": PIN_D, "depth_from_lug_face": PIN_DEPTH},
                  "lug_mm": {"w": LUG_W, "out_from_wall": LUG_T}, "tab": False, "finger_notches": False,
                  "overall_y_mm": box.W + 2 * LUG_T, "same_as_frame_holder": "body, pocket, ledge, open bottom"}


def catch_pan():
    """A box's top 25 mm on a CATCH_DEPTH skirt, a solid floor, the inward lip at the rim."""
    h = box.H + CATCH_DEPTH
    part = walls(h).union(cq.Workplane("XY").box(box.L - 1, box.W - 1, FLOOR_T, centered=(True, True, False)))
    # the lip: a slab LIP_T thick plus a 45 deg chamfer under it, cut back to the box above's open bottom
    ix, iy = box.L - 2 * box.WALL, box.W - 2 * box.WALL
    lip_x, lip_y = (ix - box.OPEN_L) / 2, (iy - box.OPEN_W) / 2     # 5 at the ends, 7 along the sides
    d = max(lip_x, lip_y)
    lip = cq.Workplane("XY").box(ix + 0.2, iy + 0.2, LIP_T + d, centered=(True, True, False)).translate((0, 0, h - LIP_T - d))
    opening = (cq.Workplane("XY").workplane(offset=h - LIP_T).rect(box.OPEN_L, box.OPEN_W).extrude(LIP_T + 1)
               .union(cq.Workplane("XY").workplane(offset=h - LIP_T).rect(box.OPEN_L, box.OPEN_W)
                      .workplane(offset=-(d + 0.5)).rect(box.OPEN_L + 2 * d + 1, box.OPEN_W + 2 * d + 1).loft()))
    part = part.union(lip.cut(opening))
    part = with_lugs(part, CATCH_DEPTH + PIVOT_Z)
    return part, {"pivot_mm": [0.0, 0.0, CATCH_DEPTH + PIVOT_Z], "height_mm": h, "catch_depth_below_box_mm": CATCH_DEPTH,
                  "floor_t_mm": FLOOR_T, "floor_top_below_rim_mm": h - FLOOR_T,
                  "lip_mm": {"t": LIP_T, "underside_deg": 45, "in_at_ends": lip_x, "in_at_sides": lip_y,
                             "opening": [box.OPEN_L, box.OPEN_W]},
                  "note": "rim and pivot sit as on a box (pivot 12.5 under the rim), so it hangs at the same pitch"}


def drive_slot_span():
    """How far from the pivot the pin centre can sit along the slot: (inner end, outer end)."""
    return DRIVE_R - DRIVE_SLACK, DRIVE_R / math.cos(math.radians(DRIVE_MAX_DEG)) + DRIVE_SLACK


def with_drive_lug(part, side, slot_z):
    """Add a drive lug on the +Y long wall toward +X (side 1) or -X (side -1), its slot centred slot_z up."""
    s0, s1 = drive_slot_span()
    xc, y_wall, y_face = side * (s0 + s1) / 2, box.W / 2, box.W / 2 + LUG_T
    plate = cq.Workplane("XY").box(LUG_W, LUG_T, slot_z, centered=(True, False, False)).translate((xc, y_wall, 0))
    part = part.union(plate).union(cyl_y(LUG_W / 2, y_wall, LUG_T, slot_z).translate((xc, 0, 0)))
    slot = (cq.Workplane("XZ", origin=(0, y_face + 0.01, 0)).center(xc, slot_z)     # XZ extrudes toward -Y
            .slot2D(s1 - s0 + DRIVE_SLOT_W, DRIVE_SLOT_W).extrude(LUG_T + 0.01))
    return part.cut(slot)


def drive_info(side, slot_z):
    s0, s1 = drive_slot_span()
    return {"drive_lug": {"wall": "+Y", "pin_x_at_rest_mm": round(side * DRIVE_R, 2),
                          "slot_x_mm": sorted([round(side * s0, 2), round(side * s1, 2)]), "slot_z_mm": slot_z,
                          "slot_w_mm": DRIVE_SLOT_W, "slot_depth_mm": LUG_T, "pin_d_mm": DRIVE_PIN_D,
                          "slot_covers_tilt_deg": DRIVE_MAX_DEG,
                          "tilt_law": "theta = atan(u / DRIVE_R), u = rod travel from the level pose"}}


def holder_drive(side):
    part, info = holder()
    return with_drive_lug(part, side, PIVOT_Z), {**info, **drive_info(side, PIVOT_Z)}


def catch_pan_drive(side):
    part, info = catch_pan()
    z = CATCH_DEPTH + PIVOT_Z
    return with_drive_lug(part, side, z), {**info, **drive_info(side, z)}


PARTS = {"seesaw_holder": holder, "seesaw_catch_pan": catch_pan,
         "seesaw_holder_drive_a": lambda: holder_drive(1), "seesaw_holder_drive_b": lambda: holder_drive(-1),
         "seesaw_catch_pan_drive_b": lambda: catch_pan_drive(-1)}


if __name__ == "__main__":
    for n in sys.argv[1:] or list(PARTS):
        part, info = PARTS[n]()
        print(n, json.dumps(export_all(part, n, info)))
