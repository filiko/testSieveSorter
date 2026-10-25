"""Sieve inserts for BioKEA's holder box: the flat 2x3-window frames with pull tabs from
the bench photos (Downloads\\IMG20261024193841.jpg, IMG20261024193846.jpg), with the mesh
printed in as square holes instead of glued on.

    sieve_insert_5mm   5.0 mm square holes (the coarse mesh in the photos)
    sieve_insert_2mm   2.0 mm square holes (the insert marked "2 mm")

Read from the photos: the insert's proportions match the holder pocket, a border about
10 mm wide, ribs about 3 mm making six windows (about 35 x 36 mm), and two upright pull
tabs in the middle of the long edges. Measure one of your existing inserts with calipers
and correct the numbers below; the size defaults to the frame_holder.py pocket guess.

The square-hole screen sits at the bottom of each window, on the print bed, so it prints
cleanly with no bridging. The border and ribs stand FRAME_T - SCREEN_T above it. Holes
widen downward by RELIEF_DEG so a grain that gets in falls free instead of wedging.
Prints flat, right side up, no supports.

Run from this folder:  <venv python> sieve_insert.py
"""
import json
import sys
import cadquery as cq
from cadkit import export_all
import frame_holder as box

FIT = 0.6                         # total clearance in the holder pocket
L = box.L - 2 * box.WALL - FIT    # 131.4 with the frame_holder guesses
W = box.W - 2 * box.WALL - FIT    # 95.4
FRAME_T = 3.0                     # border and rib height
BORDER = 10.0
RIB = 3.0
COLS, ROWS = 3, 2
TAB_W, TAB_T, TAB_H = 20.0, 6.0, 18.0   # pull tab: along the edge, thickness, height above the frame
RELIEF_DEG = 8.0
LABEL_H, LABEL_D = 4.0, 0.6

# name: (hole size, bar width between holes, screen thickness)
INSERTS = {
    "sieve_insert_5mm": (5.0, 1.2, 1.6),
    "sieve_insert_2mm": (2.0, 1.0, 1.4),
}


def windows():
    """Centre and size of each of the COLS x ROWS windows."""
    win_l = (L - 2 * BORDER - (COLS - 1) * RIB) / COLS
    win_w = (W - 2 * BORDER - (ROWS - 1) * RIB) / ROWS
    out = []
    for i in range(COLS):
        for j in range(ROWS):
            out.append((-L / 2 + BORDER + win_l / 2 + i * (win_l + RIB),
                        -W / 2 + BORDER + win_w / 2 + j * (win_w + RIB), win_l, win_w))
    return out


def insert(name):
    hole, bar, screen_t = INSERTS[name]
    body = cq.Workplane("XY").box(L, W, FRAME_T, centered=(True, True, False))
    pitch = hole + bar
    holes = []
    for cx, cy, wl, ww in windows():
        body = body.cut(cq.Workplane("XY").box(wl, ww, FRAME_T, centered=(True, True, False))
                        .translate((cx, cy, screen_t)))
        nx, ny = int((wl - bar) // pitch), int((ww - bar) // pitch)   # whole holes that fit with a bar at each edge
        x0, y0 = cx - (nx - 1) * pitch / 2, cy - (ny - 1) * pitch / 2
        holes += [(x0 + i * pitch, y0 + j * pitch) for i in range(nx) for j in range(ny)]
    cutter = (cq.Workplane("XY").workplane(offset=screen_t + 0.01).pushPoints(holes)
              .rect(hole, hole).extrude(-(screen_t + 0.2), taper=-RELIEF_DEG))
    body = body.cut(cutter)
    for sy in (1, -1):
        tab = cq.Workplane("XY").box(TAB_W, TAB_T, FRAME_T + TAB_H, centered=(True, False, False))
        body = body.union(tab.translate((0, W / 2 - TAB_T if sy > 0 else -W / 2, 0)))
    label = cq.Workplane("XY").workplane(offset=FRAME_T + TAB_H + 0.01).center(0, W / 2 - TAB_T / 2) \
        .text(f"{hole:g}", LABEL_H, -(LABEL_D + 0.01), combine=False)
    body = body.cut(label)
    open_pct = 100 * len(holes) * hole * hole / sum(wl * ww for _, _, wl, ww in windows())
    return body, {"hole_mm": hole, "bar_mm": bar, "screen_t_mm": screen_t, "holes": len(holes),
                  "open_area_of_windows_pct": round(open_pct, 1), "outside_mm": [round(L, 2), round(W, 2), FRAME_T],
                  "window_mm": [round(windows()[0][2], 1), round(windows()[0][3], 1)]}


PARTS = {n: (lambda n=n: insert(n)) for n in INSERTS}


if __name__ == "__main__":
    for n in sys.argv[1:] or list(PARTS):
        part, info = PARTS[n]()
        print(n, json.dumps(export_all(part, n, info)))
