"""BugSorter sieve system, every part exactly the size of a 24-well plate
(127.76 x 85.47 x 20.27 mm, SBS/ANSI footprint), so it drops into any plate holder,
plate shaker or plate gripper.

Stack, top to bottom. A short lip under each part nests into the part below;
the lip sits inside the 20.27 mm height, so each part's envelope is the plate's.
    lid
    tray_coarse_5p0                        pasta stays on top
    tray_fine_2p3 or tray_fine_slot_1p3    rice/quinoa split (see SCREENS)
    collector                              catches what passes the fine tray

Also:
    tray_open + clamp_ring   frame for a cut piece of the kit's metal sheet
    gate_coupon_2p3/_5p0     the "gates" idea: raised deck, a row of posts, a drop
                             into a pocket. Shake it along its long (X) axis.

Holes and slots widen downward by RELIEF_DEG, so a grain that gets into an opening
falls free instead of wedging. Inner corners are rounded so grains can't park there.

Run from this folder:
    <venv python> sieve_system.py                  all parts
    <venv python> sieve_system.py tray_fine_2p3    one or more parts by name
<venv python> is ..\\..\\..\\BioKEA-hack\\.venv\\Scripts\\python.exe on this PC.

Print hole_gauge.py first and pour each grain over it, so the aperture numbers
below are what your printer actually makes.
"""
import json
import math
import sys
import cadquery as cq
from cadkit import export_all

# --- 24-well plate envelope (mm), same numbers as BioKEA-hack\cad\well_plate_24.py ---
L, W, H = 127.76, 85.47, 20.27
CORNER_R = 3.18

# --- shared (mm) -------------------------------------------------------------
WALL = 3.0
INNER_R = 3.0        # inner corner radius, so grains don't park in corners
FIT = 0.6            # total nesting clearance, 0.3 per side (Chris's value)
LIP_H = 3.0          # nesting lip at the bottom of each part, inside the plate height
LIP_WALL = 2.0
FLOOR_T = 2.0        # screen thickness
RELIEF_DEG = 8.0     # openings widen downward by this angle; 0 = straight
WEB = 1.0            # plastic left between openings, measured at the wide (bottom) side
EDGE = 1.5           # solid border between the perforation and the lip
LABEL_H, LABEL_D = 4.0, 0.6

# Screen presets for the food test. Measure 10 grains of each with calipers first.
#   round: sorts by width. slot: sorts by thickness (things pass edge-on).
# For insects, EntoSieve used round 1.5 / 3.0 / 5.0 mm.
SCREENS = {
    "tray_coarse_5p0": ("round", 5.0, None),      # pasta stays; rice and quinoa pass
    "tray_fine_2p3": ("round", 2.3, None),        # short-grain rice stays; quinoa passes
    "tray_fine_slot_1p3": ("slot", 1.3, 12.0),    # long-grain rice (~1.7 thick) stays; quinoa (~1 thick) passes edge-on
}

# --- open tray for the kit's metal sheets ------------------------------------
LEDGE = 4.0          # ledge the cut sheet rests on
RING_FIT = 0.3       # total clearance for the clamp ring (snug; it holds by friction)
RING_H = 5.0
RING_WALL = 2.4

# --- gate coupon ---------------------------------------------------------------
DECK_FRACTION = 0.5  # share of the inside length that is raised deck
STEP = 5.0           # drop from the deck into the pocket
POST_R = 1.5
TAIL = 4.0           # posts taper downstream, so each channel widens after the throat
GATES = {"gate_coupon_2p3": 2.3, "gate_coupon_5p0": 5.0}

IN_L, IN_W = L - 2 * WALL, W - 2 * WALL
LIP_L, LIP_W = IN_L - FIT, IN_W - FIT
LIP_R = INNER_R - FIT / 2
LIP_IN_L, LIP_IN_W = LIP_L - 2 * LIP_WALL, LIP_W - 2 * LIP_WALL
LIP_IN_R = max(LIP_R - LIP_WALL, 0.5)
FLOOR_Z = LIP_H      # floors sit on top of the lip


def rounded_box(x, y, h, r, z0=0.0):
    return (cq.Workplane("XY").box(x, y, h, centered=(True, True, False))
            .edges("|Z").fillet(r).translate((0, 0, z0)))


def ring(ox, oy, ix, iy, h, r_out, r_in, z0=0.0):
    return rounded_box(ox, oy, h, r_out, z0).cut(rounded_box(ix, iy, h, r_in, z0))


def label(body, text):
    """Deboss text into the outside of the +X end wall."""
    cutter = (cq.Workplane("YZ").workplane(offset=L / 2 + 0.01).center(0, (FLOOR_Z + H) / 2)
              .text(text, LABEL_H, -(LABEL_D + 0.01), combine=False))
    return body.cut(cutter)


def shell(floor=True):
    """Plate-sized tray: walls above the lip, a floor on top of the lip, lip below."""
    body = rounded_box(L, W, H - LIP_H, CORNER_R, z0=LIP_H)
    body = body.cut(rounded_box(IN_L, IN_W, H, INNER_R, z0=FLOOR_Z + (FLOOR_T if floor else 0)))
    if not floor:  # a ledge for a cut metal sheet instead of a printed floor
        body = body.union(ring(IN_L + 1, IN_W + 1, IN_L - 2 * LEDGE, IN_W - 2 * LEDGE, FLOOR_T,
                               INNER_R, max(INNER_R - LEDGE, 1.0), z0=FLOOR_Z))
    return body.union(ring(LIP_L, LIP_W, LIP_IN_L, LIP_IN_W, LIP_H + 0.5, LIP_R, LIP_IN_R))


def inside_rounded_rect(x, y, hx, hy, r):
    dx = max(abs(x) - (hx - r), 0.0)
    dy = max(abs(y) - (hy - r), 0.0)
    return math.hypot(dx, dy) <= r


def opening_layout(kind, size, slot_len):
    """Centres of openings that fit inside the lip, checked at their wide bottom."""
    grow = 2 * FLOOR_T * math.tan(math.radians(RELIEF_DEG))
    hx, hy = LIP_IN_L / 2 - EDGE, LIP_IN_W / 2 - EDGE
    r_region = max(LIP_IN_R - EDGE, 0.0)
    pts = []
    if kind == "round":
        d_bot = size + grow
        pitch = d_bot + WEB
        row = pitch * math.sqrt(3) / 2
        for j in range(-int(hy / row) - 1, int(hy / row) + 2):
            off = pitch / 2 if j % 2 else 0.0
            for i in range(-int(hx / pitch) - 2, int(hx / pitch) + 3):
                x, y = i * pitch + off, j * row
                if inside_rounded_rect(x, y, hx - d_bot / 2, hy - d_bot / 2, max(r_region - d_bot / 2, 0.0)):
                    pts.append((x, y))
        open_frac = (math.pi / (2 * math.sqrt(3))) * (size / pitch) ** 2
    else:
        w_bot, l_bot = size + grow, slot_len + grow
        px, py = w_bot + WEB, l_bot + 1.5 * WEB
        for i in range(-int(hx / px) - 1, int(hx / px) + 2):
            off = py / 2 if i % 2 else 0.0
            for j in range(-int(hy / py) - 2, int(hy / py) + 3):
                x, y = i * px, j * py + off
                ends = [(x, y - (l_bot - w_bot) / 2), (x, y + (l_bot - w_bot) / 2)]
                if all(inside_rounded_rect(ex, ey, hx - w_bot / 2, hy - w_bot / 2, max(r_region - w_bot / 2, 0.0))
                       for ex, ey in ends):
                    pts.append((x, y))
        open_frac = (size * slot_len - (4 - math.pi) * (size / 2) ** 2) / (px * py)
    return pts, open_frac


def sieve_tray(name):
    kind, size, slot_len = SCREENS[name]
    pts, open_frac = opening_layout(kind, size, slot_len)
    wp = cq.Workplane("XY").workplane(offset=FLOOR_Z + FLOOR_T + 0.01).pushPoints(pts)
    wp = wp.circle(size / 2) if kind == "round" else wp.slot2D(slot_len, size, 90)
    body = shell().cut(wp.extrude(-(FLOOR_T + 0.2), taper=-RELIEF_DEG))
    body = label(body, f"{size:g}" if kind == "round" else f"S{size:g}")
    info = {"opening": kind, "top_size_mm": size,
            "bottom_size_mm": round(size + 2 * FLOOR_T * math.tan(math.radians(RELIEF_DEG)), 2),
            "openings": len(pts), "open_area_pct": round(100 * open_frac, 1),
            "headroom_above_floor_mm": round(H - FLOOR_Z - FLOOR_T, 2)}
    if slot_len:
        info["slot_length_mm"] = slot_len
    return body, info


def tray_open():
    return label(shell(floor=False), "OPEN"), {
        "sheet_cut_mm": [round(IN_L - FIT, 1), round(IN_W - FIT, 1)], "ledge_mm": LEDGE,
        "note": "cut a kit sheet to sheet_cut_mm, clip the corners, drop it on the ledge, press clamp_ring on top"}


def clamp_ring():
    ox, oy = IN_L - RING_FIT, IN_W - RING_FIT
    r = INNER_R - RING_FIT / 2
    return ring(ox, oy, ox - 2 * RING_WALL, oy - 2 * RING_WALL, RING_H, r, max(r - RING_WALL, 0.5)), {}


def collector():
    body = rounded_box(L, W, H, CORNER_R)
    body = body.cut(rounded_box(IN_L, IN_W, H, INNER_R, z0=FLOOR_T))
    return label(body, "BIN"), {"inner_mm": [round(IN_L, 2), round(IN_W, 2), round(H - FLOOR_T, 2)],
                                "volume_ml": round(IN_L * IN_W * (H - FLOOR_T) / 1000)}


def lid():
    plate = rounded_box(L, W, FLOOR_T, CORNER_R, z0=LIP_H)
    return plate.union(ring(LIP_L, LIP_W, LIP_IN_L, LIP_IN_W, LIP_H + 0.5, LIP_R, LIP_IN_R)), {}


def gate_coupon(name):
    gap = GATES[name]
    body = rounded_box(L, W, H, CORNER_R)
    body = body.cut(rounded_box(IN_L, IN_W, H, INNER_R, z0=FLOOR_T))
    x0 = -IN_L / 2
    fence_x = x0 + IN_L * DECK_FRACTION
    deck = (cq.Workplane("XY").box(fence_x - x0 + 1, IN_W + 1, STEP, centered=False)
            .translate((x0 - 1, -IN_W / 2 - 0.5, FLOOR_T)))
    body = body.union(deck)
    xc, h = fence_x + POST_R - 0.5, H - FLOOR_T   # posts bite 0.5 mm into the deck edge so they fuse cleanly
    ys, y = [], -IN_W / 2 + gap + POST_R
    while y + POST_R + gap <= IN_W / 2 + 1e-6:
        ys.append(y)
        y += 2 * POST_R + gap
    for y in ys:
        post = (cq.Workplane("XY").workplane(offset=FLOOR_T).center(xc, y).circle(POST_R).extrude(h)
                .union(cq.Workplane("XY").workplane(offset=FLOOR_T)
                       .polyline([(xc, y - POST_R), (xc + POST_R + TAIL, y), (xc, y + POST_R)]).close().extrude(h)))
        body = body.union(post)
    filler_y0 = ys[-1] + POST_R + gap
    if filler_y0 < IN_W / 2:  # close the leftover so the last channel is exactly GAP wide
        body = body.union(cq.Workplane("XY").box(2 * POST_R, IN_W / 2 + 0.5 - filler_y0, h, centered=False)
                          .translate((xc - POST_R, filler_y0, FLOOR_T)))
    body = label(body, f"G{gap:g}")
    return body, {"gap_mm": gap, "posts": len(ys), "step_mm": STEP, "shake_axis": "X (long side)",
                  "deck_mm": round(fence_x - x0, 1), "pocket_mm": round(IN_L - (fence_x - x0) - 2 * POST_R, 1)}


PARTS = {**{n: (lambda n=n: sieve_tray(n)) for n in SCREENS},
         "tray_open": tray_open, "clamp_ring": clamp_ring, "collector": collector, "lid": lid,
         **{n: (lambda n=n: gate_coupon(n)) for n in GATES}}


if __name__ == "__main__":
    for n in sys.argv[1:] or list(PARTS):
        part, info = PARTS[n]()
        print(n, json.dumps(export_all(part, n, info)))
