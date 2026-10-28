"""Round-hole and slot screens for the printed sieve inserts of an inserts: tower (designs_holder.py). Units mm.

    r<hole>b<bar>[_across]            round holes <hole> across on a square grid, <bar> between neighbours
    s<width>x<length>b<bar>[_across]  slots <width> wide and <length> long, running along X (the tilt direction),
                                      <bar> between them, ends square
Sizes are as modelled, with p for the point, like h<hole>b<bar>: r1p05b0p95_across is 1.05 mm holes with 0.95 mm
bars on the ribs-across frame (optimize.py prints nominal - 0.15 mm for holes and + 0.15 for bars). _across puts
the screen on the ribs-across frame (sieve_insert.py ACROSS); without it, on the flat 3 x 2 frame (INSERTS). The
screen is 1.6 mm thick for openings of 3 mm and up, else 1.4, as designs_holder.insert_spec does for h<hole>b<bar>.

Why: a square hole passes a flat item corner to corner. A 2 mm square is 2.83 mm across its diagonal, so long flat
grains and specimens leak through it. A round hole is the same width every way; a slot cuts on thickness only.

How round holes are modelled (ASSUMED shape): MuJoCo collides convex pieces, and a plate with round holes isn't
convex. So each hole is a regular octagon <hole> across the flats: the square-hole grid's bars (tapered RELIEF_DEG,
as printed_screen builds them), plus a box turned 45 deg about Z at every node where four holes meet, whose edges
are the four holes' corner cuts, and a smaller one at each hole corner on the window edge. Corner to corner the
octagon is 1.082 x <hole> across, against 1.414 x for a square. The corner fills have no relief taper; the hole at
the top surface is still the narrowest. It costs about one extra geom per hole.

This module is self-contained: designs_holder.insert() hands it any name that parse() accepts, and its layer record
uses the rules "round" (fits_round) and "slot" (thickness <= width) in designs_holder.ideal_zone.
"""
import math
import re

import numpy as np

ROUND = re.compile(r"^r(\d+(?:p\d+)?)b(\d+(?:p\d+)?)(_across)?$")
SLOT = re.compile(r"^s(\d+(?:p\d+)?)x(\d+(?:p\d+)?)b(\d+(?:p\d+)?)(_across)?$")
OCTAGON_CUT = 1.0 / (2.0 + math.sqrt(2.0))     # corner cut along each side, as a share of the hole
OCTAGON_DIAG = 1.0 / math.cos(math.pi / 8)      # 1.082: corner-to-corner over flat-to-flat
OCTAGON_AREA = 2.0 * (math.sqrt(2.0) - 1.0)     # 0.828: area over hole^2
SCREEN_RGBA = [0.35, 0.55, 0.85, 1.0]
Q45 = [math.cos(math.pi / 8), 0.0, 0.0, math.sin(math.pi / 8)]   # 45 deg about Z


def _num(s):
    return float(s.replace("p", "."))


def parse(short):
    """A round-hole or slot spec name (no sieve_insert_ prefix) -> dict, else None. hx, hy: opening along X, Y."""
    m = ROUND.match(short)
    if m:
        hole, bar = _num(m.group(1)), _num(m.group(2))
        return {"shape": "round", "hole": hole, "bar": bar, "hx": hole, "hy": hole, "across": bool(m.group(3))}
    m = SLOT.match(short)
    if m:
        w, length, bar = _num(m.group(1)), _num(m.group(2)), _num(m.group(3))
        if length < w:
            raise ValueError(f"slot {short}: length {length:g} is less than its width {w:g}")
        return {"shape": "slot", "width": w, "length": length, "bar": bar, "hx": length, "hy": w,
                "across": bool(m.group(4))}
    return None


def opening(spec):
    """The size the ideal-zone rule cuts on: the round hole across its flats, or the slot's width."""
    return spec["hole"] if spec["shape"] == "round" else spec["width"]


def thickness(spec):
    return 1.6 if opening(spec) >= 3 else 1.4


def fits_round(w, t, s, steps=46):
    """Whether a w x t elliptical cross-section passes the modelled round hole (a regular octagon s across the
    flats) at its best turn: it must fit between each of the octagon's four pairs of parallel sides."""
    a, b = w / 2, t / 2
    u = np.array([0.0, 0.25, 0.5, 0.75]) * np.pi - np.linspace(0.0, np.pi / 4, steps)[:, None]
    half = np.sqrt((a * np.cos(u)) ** 2 + (b * np.sin(u)) ** 2)
    return bool(np.any(np.all(2 * half <= s, axis=1)))


def _diamond(xc, yc, r, z0, z1):
    """A box turned 45 deg about Z: |x - xc| + |y - yc| <= r, from z0 to z1. A primitive, so legs (capsules) collide
    with it analytically; a convex mesh would go through the general convex collider."""
    s = r / math.sqrt(2.0)
    return {"type": "box", "size": [s, s, (z1 - z0) / 2], "pos": [xc, yc, (z0 + z1) / 2], "quat": Q45,
            "rgba": SCREEN_RGBA, "role": "screen"}


def _centres(w0, w1, n, pitch):
    c0 = (w0 + w1) / 2 - (n - 1) * pitch / 2
    return [c0 + k * pitch for k in range(n)]


def grid(spec, windows, rows, inner, z0, t, taper):
    """The screen's geoms in every window and its opening count. inner: the frame's inner half sizes (bars run to
    them, under the ribs and borders)."""
    import designs_holder as dh
    hx, hy, bar = spec["hx"], spec["hy"], spec["bar"]
    px, py, z1 = hx + bar, hy + bar, z0 + t
    g = []

    def bars(axis, w0, w1, n, hole, pitch, a0, a1):
        for a, b, ah, bh in dh.solid_runs(w0, w1, _centres(w0, w1, n, pitch), hole):
            g.append(dh.prism([(a + taper * ah, z0), (b - taper * bh, z0), (b, z1), (a, z1)], axis, a0, a1,
                              SCREEN_RGBA, "screen"))

    nx = lambda wl: int((wl - bar) // px)
    ny = lambda ww: int((ww - bar) // py)
    for cx, _cy, wl, _ww in windows[::rows]:          # one per column: bars along Y, between openings in X
        bars("y", cx - wl / 2, cx + wl / 2, nx(wl), hx, px, -inner[1], inner[1])
    for _cx, cy, _wl, ww in windows[:rows]:           # one per row: bars along X, between openings in Y
        bars("x", cy - ww / 2, cy + ww / 2, ny(ww), hy, py, -inner[0], inner[0])
    n_open = sum(nx(wl) * ny(ww) for _, _, wl, ww in windows)
    if spec["shape"] != "round":
        return g, n_open
    h = spec["hole"]
    c = OCTAGON_CUT * h
    for cx, cy, wl, ww in windows:
        xs, ys = _centres(cx - wl / 2, cx + wl / 2, nx(wl), px), _centres(cy - ww / 2, cy + ww / 2, ny(ww), py)
        # Where four holes meet: the diamond |x| + |y| <= bar + c about the bar crossing. Its four edges are the four
        # holes' corner cuts (x + y = bar + c for the hole up and right); the rest of it lies inside the bars.
        for i in range(len(xs) - 1):
            for j in range(len(ys) - 1):
                g.append(_diamond((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2, bar + c, z0, z1))
        # A hole corner with no hole diagonally beyond it (on the window edge): the diamond |dx| + |dy| <= c about
        # the corner. Inside the hole that is the corner cut; outside, solid screen or (when c > bar) the next
        # hole's own corner cut.
        for i, xc in enumerate(xs):
            for j, yc in enumerate(ys):
                for sx in (-1, 1):
                    for sy in (-1, 1):
                        if 0 <= i + sx < len(xs) and 0 <= j + sy < len(ys):
                            continue
                        g.append(_diamond(xc + sx * h / 2, yc + sy * h / 2, c, z0, z1))
    return g, n_open


def insert(short, spec, z_seat, drain_area):
    """Geoms of one round-hole or slot insert seated on a ledge top at z_seat, and its layer record (as
    designs_holder.insert returns for a printed insert)."""
    import designs_holder as dh
    si = dh.cad()[1]
    name, t = f"sieve_insert_{short}", thickness(spec)
    if spec["across"]:
        # insert_frame_across reads the screen thickness from ACROSS, as for an h<hole>b<bar>_across insert
        si.ACROSS.setdefault(name, (opening(spec), spec["bar"], t))
        frame, win, rows = dh.insert_frame_across(z_seat, name), si.across_windows(), 1
        inner = (si.L / 2 - si.ACROSS_BORDER[0], si.W / 2 - si.ACROSS_BORDER[1])
    else:
        frame, win, rows = dh.insert_frame(z_seat), si.windows(), si.ROWS
        inner = (si.L / 2 - si.BORDER, si.W / 2 - si.BORDER)
    screen, n = grid(spec, win, rows, inner, z_seat, t, t * math.tan(math.radians(si.RELIEF_DEG)))
    if spec["shape"] == "round":
        open_area = n * OCTAGON_AREA * spec["hole"] ** 2
        desc = (f"{spec['hole']:g} mm round holes ({n}; modelled as octagons, {OCTAGON_DIAG * spec['hole']:.2f} mm "
                f"corner to corner), bars {spec['bar']:g} mm")
    else:
        open_area = n * spec["width"] * spec["length"]
        desc = f"{spec['width']:g} x {spec['length']:g} mm slots along X ({n}), bars {spec['bar']:g} mm"
    win_area = sum(wl * ww for _, _, wl, ww in win)
    geoms = frame + screen
    layer = {"zone": f"on_{short}", "insert": name, "opening": desc, "rule": spec["shape"],
             "opening_mm": opening(spec), "shape": spec["shape"], "frame": "across" if spec["across"] else "flat",
             "insert_bottom_z_mm": round(z_seat, 3), "surface_z_mm": [round(z_seat, 3), round(z_seat + t, 3)],
             "open_area_mm2": round(open_area, 1), "open_pct_of_drainable": round(100 * open_area / drain_area, 1),
             "open_pct_of_windows": round(100 * open_area / win_area, 1), "geoms": len(geoms), "holes": n}
    if spec["shape"] == "slot":
        layer["slot_mm"] = [spec["width"], spec["length"]]
    return geoms, layer
