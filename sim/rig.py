"""BioKEA's BugSorter tower, drawn around a holder-box run on the replay page (viewer.py --rig bugsorter).
Display only: none of it is in the physics, and it stays still while the boxes shake.

What it shows, from the team's photo of the bench unit (2026-10-25): a black aluminium-extrusion frame
standing in a white water tub; the holder boxes hanging one above the other from rods through their +X
mounting tabs, each rod with a knob on the front; a hex-perforated spray plate over the top box; the
M5Stack controller on a plate across the top; clear acrylic panels round the back and the ends.

Every size below is ESTIMATED from that photo, scaled by the 140 x 104 x 25 mm holder box. Measure the
bench unit and change them here. The spacing of the boxes is the sim's own (designs_holder.py pitch=);
the photo suggests about 65 mm bottom to bottom.
"""
import math

EXTRUSION = 20.0              # square aluminium extrusion
FRAME_Y = 72.0                # extrusion centre lines at y = +/- this (the box is 104 wide)
FRAME_X_FREE = 8.0            # the -X pair stands this far past the boxes' free end
HOLE_FROM_END = 6.5           # frame_holder.py: tab hole centre from the tab's end; the rods go through it
ROD_D, KNOB_D, KNOB_L = 6.0, 20.0, 10.0
KNOB_SIDE = 1                 # knobs on the +Y side, the side the photo is taken from
SPRAY_ABOVE = 50.0            # spray plate above the top box's rim
SPRAY_L, SPRAY_W, SPRAY_T = 120.0, 100.0, 2.0
HEX_PITCH, HEX_D = 9.0, 5.0   # spray plate holes, on a hexagonal grid
TOP_ABOVE = 110.0             # top of the frame above the top box's rim
TOP_PLATE_T = 5.0
TUB_L, TUB_W, TUB_DEPTH, TUB_WALL = 380.0, 280.0, 120.0, 3.0
TUB_RIM_BELOW = 10.0          # tub rim below the bottom box
WATER = 70.0                  # water depth in the tub
ACRYLIC_T, ACRYLIC_GAP = 4.0, 30.0

BLACK = [0.09, 0.09, 0.10, 1.0]
STEEL = [0.55, 0.57, 0.60, 1.0]
KNOB = [0.42, 0.44, 0.47, 1.0]
WHITE = [0.95, 0.95, 0.93, 1.0]
SPRAY = [0.86, 0.87, 0.89, 1.0]
HOLE = [0.20, 0.21, 0.24, 1.0]
TUB = [0.97, 0.97, 0.97, 0.45]
WATER_RGBA = [0.55, 0.74, 0.95, 0.22]
ACRYLIC = [0.85, 0.92, 1.0, 0.07]
_S = math.sqrt(0.5)
AXIS_QUAT = {"x": [_S, 0.0, _S, 0.0], "y": [_S, -_S, 0.0, 0.0], "z": [1.0, 0.0, 0.0, 0.0]}   # local z onto x, y, z


def box(x0, x1, y0, y1, z0, z1, rgba, part):
    return {"type": "box", "size": [(x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2],
            "pos": [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2], "quat": [1.0, 0.0, 0.0, 0.0],
            "rgba": rgba, "role": "rig", "part": part}


def cylinder(axis, a0, a1, centre, r, rgba, part):
    """Along `axis` from a0 to a1; centre gives the other two coordinates (and is overwritten on the axis)."""
    pos = list(centre)
    pos["xyz".index(axis)] = (a0 + a1) / 2
    return {"type": "cylinder", "size": [r, abs(a1 - a0) / 2], "pos": pos, "quat": AXIS_QUAT[axis],
            "rgba": rgba, "role": "rig", "part": part}


def holder_tabs(tray_geoms):
    """(tab end x, [(z0, z1) per holder box]): the holder tabs are the boxes reaching furthest along +X."""
    boxes = [g for g in tray_geoms if g["type"] == "box" and g.get("role") != "lid"]
    x_end = max(g["pos"][0] + g["size"][0] for g in boxes)
    tabs = [g for g in boxes if abs(g["pos"][0] + g["size"][0] - x_end) < 1e-6]
    return x_end, sorted((g["pos"][2] - g["size"][2], g["pos"][2] + g["size"][2]) for g in tabs)


def bugsorter(scene):
    """The tower around scene["tray"]: a list of display-only geoms in the lab frame (the tray at rest)."""
    tray = [g for g in scene["tray"]["geoms"] if g.get("role") != "lid"]
    x_end, levels = holder_tabs(tray)
    x_free = min(g["pos"][0] - g["size"][0] for g in tray if g["type"] == "box")
    z_rim = levels[-1][1]                                     # top box's rim
    xr = x_end - HOLE_FROM_END                                # rods, and the +X pair of uprights
    xl = x_free - FRAME_X_FREE - EXTRUSION / 2                # the -X pair
    xc = (xl + xr) / 2
    e = EXTRUSION / 2
    z_floor = levels[0][0] - TUB_RIM_BELOW - TUB_DEPTH
    z_top = z_rim + TOP_ABOVE
    g = []
    # frame: four uprights standing on the tub floor, rails round the top, a plate on them
    for x in (xl, xr):
        for y in (-FRAME_Y, FRAME_Y):
            g.append(box(x - e, x + e, y - e, y + e, z_floor + TUB_WALL, z_top, BLACK, "frame"))
    for y in (-FRAME_Y, FRAME_Y):
        g.append(box(xl + e, xr - e, y - e, y + e, z_top - EXTRUSION, z_top, BLACK, "frame"))
    for x in (xl, xr):
        g.append(box(x - e, x + e, -FRAME_Y + e, FRAME_Y - e, z_top - EXTRUSION, z_top, BLACK, "frame"))
    g.append(box(xc - 45, xc + 85, -FRAME_Y - e, FRAME_Y + e, z_top, z_top + TOP_PLATE_T, BLACK, "top plate"))
    # controller: printed mount and the M5Stack Core on top
    zc = z_top + TOP_PLATE_T
    g.append(box(xc - 10, xc + 65, -30, 30, zc, zc + 28, WHITE, "controller mount"))
    g.append(box(xc + 1, xc + 55, -27, 27, zc + 28, zc + 45, BLACK, "controller"))
    # each box hangs from a rod through its tab, knob on the front
    y_out = FRAME_Y + e
    for z0, z1 in levels:
        zm = (z0 + z1) / 2
        g.append(cylinder("y", -y_out, y_out, (xr, 0, zm), ROD_D / 2, STEEL, "rod"))
        ky = KNOB_SIDE * (y_out + KNOB_L / 2)
        g.append(cylinder("y", ky - KNOB_L / 2, ky + KNOB_L / 2, (xr, 0, zm), KNOB_D / 2, KNOB, "knob"))
    # spray plate over the top box, hung from the top rails, holes on a hex grid
    zs = z_rim + SPRAY_ABOVE
    sx = (x_free + x_end - 22.0) / 2                          # over the box body, not the tab
    g.append(box(sx - SPRAY_L / 2, sx + SPRAY_L / 2, -SPRAY_W / 2, SPRAY_W / 2, zs, zs + SPRAY_T, SPRAY, "spray plate"))
    for x in (sx - SPRAY_L / 2 + 6, sx + SPRAY_L / 2 - 6):
        g.append(cylinder("z", zs + SPRAY_T, z_top - EXTRUSION, (x, 0, 0), 2.0, STEEL, "spray hanger"))
    row_h = HEX_PITCH * math.sqrt(3) / 2
    for j in range(int((SPRAY_W - HEX_PITCH) // row_h) + 1):
        y = -SPRAY_W / 2 + HEX_PITCH / 2 + j * row_h
        x0 = sx - SPRAY_L / 2 + HEX_PITCH / 2 + (HEX_PITCH / 2 if j % 2 else 0)
        while x0 <= sx + SPRAY_L / 2 - HEX_PITCH / 2 + 1e-6:
            g.append(cylinder("z", zs - 0.1, zs + SPRAY_T + 0.1, (x0, y, 0), HEX_D / 2, HOLE, "spray hole"))
            x0 += HEX_PITCH
    # the tub, with water in it
    tx, ty = TUB_L / 2, TUB_W / 2
    z_rim_tub = z_floor + TUB_DEPTH
    g.append(box(xc - tx, xc + tx, -ty, ty, z_floor, z_floor + TUB_WALL, TUB, "tub"))
    for sy in (-1, 1):
        g.append(box(xc - tx, xc + tx, sy * ty - (TUB_WALL if sy > 0 else 0), sy * ty + (0 if sy > 0 else TUB_WALL),
                     z_floor, z_rim_tub, TUB, "tub"))
    for sx_ in (-1, 1):
        g.append(box(xc + sx_ * tx - (TUB_WALL if sx_ > 0 else 0), xc + sx_ * tx + (0 if sx_ > 0 else TUB_WALL),
                     -ty + TUB_WALL, ty - TUB_WALL, z_floor, z_rim_tub, TUB, "tub"))
    g.append(box(xc - tx + TUB_WALL, xc + tx - TUB_WALL, -ty + TUB_WALL, ty - TUB_WALL, z_floor + TUB_WALL,
                 z_floor + TUB_WALL + WATER, WATER_RGBA, "water"))
    # acrylic: behind the frame (away from the knobs) and at both ends
    yb = -KNOB_SIDE * (FRAME_Y + e + ACRYLIC_GAP)
    xa = (xr - xl) / 2 + e + ACRYLIC_GAP
    g.append(box(xc - xa, xc + xa, yb - ACRYLIC_T / 2, yb + ACRYLIC_T / 2, z_rim_tub, z_top + 20, ACRYLIC, "acrylic"))
    y0, y1 = sorted((yb, KNOB_SIDE * (FRAME_Y + e)))        # from the back panel to the front of the frame
    for sx_ in (-1, 1):
        x = xc + sx_ * xa
        g.append(box(x - ACRYLIC_T / 2, x + ACRYLIC_T / 2, y0, y1, z_rim_tub, z_top + 20, ACRYLIC, "acrylic"))
    return g
