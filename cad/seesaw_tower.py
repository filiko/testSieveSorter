"""Seesaw tower: how far apart the holder boxes have to hang when each tips about its own pivot across
its middle and neighbours tip opposite ways (docs/SYSTEM.md section 3, confirmed by the user at 10:50).

Each level is frame_holder.py's box turned by +/-tilt about a Y axis through PIVOT (ASSUMED: the middle
of the box body at mid-height; change it when the bench pivot is measured). For each tilt the smallest
pitch (pivot to pivot) that leaves CLEAR mm between neighbours is found from the real solids, with the
+X mounting tab and with it cut off, since a pivot in the middle may not need the tab.

Writes out/seesaw_tower.png (three levels at the middle tilt, at its pitch with the tab rounded up to 5 mm),
its checks with the pitch table, and prints the table.

Run from this folder:  <venv python> seesaw_tower.py [tilt_deg ...]
"""
import json
import sys
import cadquery as cq
from cadkit import export_all
import frame_holder as box

PIVOT = (0.0, 0.0, box.H / 2)      # ASSUMED: body centre, mid-height
CLEAR = 3.0                        # mm left between neighbours at full tilt
TILTS = (20.0, 25.0, 30.0)         # SYSTEM.md: about 20-30 deg either side
LEVELS = 3


def body(tab=True):
    b = box.frame()
    if not tab:                    # cut the +X mounting tab off at the end wall
        b = b.intersect(cq.Workplane("XY").box(box.L, box.W, box.H, centered=(True, True, False)))
    return b


def level(b, tilt, z):
    """The box tipped by tilt (deg, about +Y through PIVOT), its pivot raised by z."""
    p = cq.Vector(*PIVOT)
    return b.rotate(p, p + cq.Vector(0, 1, 0), tilt).translate((0, 0, z))


def clearance(b, tilt, pitch):
    """The smaller gap over both half-cycles: the -X ends close in on one, the +X (tab) ends on the other."""
    return min(level(b, s * tilt, 0).val().distance(level(b, -s * tilt, pitch).val()) for s in (1, -1))


def min_pitch(b, tilt, clear=CLEAR):
    lo, hi = box.H, 300.0          # touching at lo (rim on rim), clear at hi
    while hi - lo > 0.25:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if clearance(b, tilt, mid) < clear else (lo, mid)
    return hi


def tower(b, tilt, pitch, n=LEVELS):
    """n levels, bottom first, neighbours tipped opposite ways (the bottom one +X end up, so the tab ends of
    the lowest pair close in). Whole boxes: there is nothing inside them to show."""
    stack = None
    for k in range(n):
        lv = level(b, -tilt if k % 2 == 0 else tilt, k * pitch)
        stack = lv if stack is None else stack.union(lv)
    return stack


if __name__ == "__main__":
    tilts = [float(a) for a in sys.argv[1:]] or list(TILTS)
    with_tab, no_tab = body(True), body(False)
    table = []
    for t in tilts:
        row = {"tilt_deg": t, "min_pitch_mm_with_tab": round(min_pitch(with_tab, t), 1),
               "min_pitch_mm_tab_cut_off": round(min_pitch(no_tab, t), 1)}
        table.append(row)
        print(json.dumps(row))
    show = table[len(table) // 2]
    pitch = -(-show["min_pitch_mm_with_tab"] // 5) * 5          # rounded up to 5 mm
    info = {"preview_only": True, "pivot_mm": list(PIVOT), "pivot_assumed": True, "clearance_mm": CLEAR,
            "levels": LEVELS, "shown_tilt_deg": show["tilt_deg"], "shown_pitch_mm": pitch, "pitch_table": table,
            "note": "pitch = pivot to pivot; neighbours tip opposite ways; boxes only, inserts sit inside them"}
    print("seesaw_tower", json.dumps(export_all(tower(with_tab, show["tilt_deg"], pitch), "seesaw_tower", info)))
