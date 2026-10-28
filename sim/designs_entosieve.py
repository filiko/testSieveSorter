"""EntoSieve (Ascenzi et al. 2025, PMC12225705; build files osf.io/6t25n) for the sorter sim: one sieve container,
a perforated plate at its bottom, moved straight up and down through a water bath that stays put. Units mm, tray
frame (it moves with the container). Sources and assumptions: ENTOSIEVE.md.

    entosieve:<screen>[,key=value,...]
        screen   r<hole>b<bar>: round holes on a staggered grid (designs_holder.round_screen), e.g. r1p5b1p5;
                 solid: no holes (a closed cup, for liquid checks)
        d        open plate diameter, mm (133.4: bucket.stl's ledge, inner radius 66.7)
        bore     container bore (138.2: bucket.stl; the paper's plates are cut to 138 mm and rest on the ledge)
        t        plate thickness (1.0: "aluminium perforated plates of 1 mm thickness")
        above    container wall above the plate (85: bucket.stl is 100 mm tall, the ledge 15 mm)
        below    catch floor this far below the plate (60, ASSUMED). EntoSieve's catch (an inner bowl with a coffee
                 filter) stands still in the lab; here it moves with the container. A specimen counts as passed once
                 its root is under the plate, and 60 mm keeps a passed specimen from being swept back up.
        sides    polygon sides per hole (12)
        drop     specimens are dropped from 5 to 35 mm over the plate; drop=<mm> drops them from 0.2 to <mm> instead
                 (liquid_check.py box: specimens resting on the floor before the shake)
Zones: retained (on the plate, inside the container) and passed (under it). Ideal zone: passed if the specimen's
width fits the hole (end first), the sim's geometric rule; entosieve.py scores EntoSieve's body-length classes.
info["liquid_boxes"]: the inside of the container above the plate, where liquid.py's entrain applies.
"""
import functools
import math

from common import Design
from designs_holder import (HOLDER_RGBA, LID_RGBA, ROUND_INSERT, ROUND_SIDES, SCREEN_RGBA, box, round_screen)

DEFAULTS = {"d": 133.4, "bore": 138.2, "t": 1.0, "above": 85.0, "below": 60.0, "sides": ROUND_SIDES, "drop": 0.0}
WALL = 2.4               # bucket.stl: bore r 69.1, outside r 71.5
WALL_SEGMENTS = 48
SPAWN_R = 42.0           # specimens are dropped over a 84 x 84 mm square in the middle of the plate
SPAWN_Z = (5.0, 35.0)    # above the plate, inside the 30-50 mm of water the paper fills to


def ring(r_in, z0, z1, n, rgba, role):
    """A polygonal cylinder wall of n boxes whose inner faces are tangent to radius r_in."""
    out = []
    half = (r_in + WALL) * math.tan(math.pi / n) + 0.05
    for k in range(n):
        a = 2 * math.pi * k / n
        g = box(-half, half, -WALL / 2, WALL / 2, z0, z1, rgba, role)
        rc = r_in + WALL / 2
        g["pos"] = [rc * math.cos(a), rc * math.sin(a), (z0 + z1) / 2]
        g["quat"] = [math.cos((a + math.pi / 2) / 2), 0.0, 0.0, math.sin((a + math.pi / 2) / 2)]
        out.append(g)
    return out


def ideal_zone(dims, hole):
    return "passed" if hole > 0 and dims["width"] <= hole else "retained"


def build(args):
    opts = {**DEFAULTS}
    screens = [a for a in args if "=" not in a]
    for a in args:
        if "=" in a:
            k, v = a.split("=", 1)
            if k not in DEFAULTS:
                raise ValueError(f"unknown entosieve option {k!r}: use {sorted(DEFAULTS)}")
            opts[k] = int(v) if k == "sides" else float(v)
    if len(screens) != 1:
        raise ValueError("entosieve takes one screen, e.g. entosieve:r1p5b1p5 or entosieve:solid")
    screen = screens[0]
    r_open, r_bore, t = opts["d"] / 2, opts["bore"] / 2, opts["t"]
    z_floor, z_plate = 0.0, opts["below"]
    z_top, z_rim = z_plate + t, z_plate + t + opts["above"]
    geoms = [box(-r_bore - WALL, r_bore + WALL, -r_bore - WALL, r_bore + WALL, z_floor - 1.0, z_floor, HOLDER_RGBA, "floor")]
    geoms += ring(r_bore, z_floor, z_rim, WALL_SEGMENTS, HOLDER_RGBA, "wall")
    if screen == "solid":
        hole, bar, centres = 0.0, 0.0, []
        geoms.append(box(-r_bore, r_bore, -r_bore, r_bore, z_plate, z_top, SCREEN_RGBA, "screen"))
    else:
        m = ROUND_INSERT.match(screen)
        if not m:
            raise ValueError(f"entosieve screen {screen!r}: use r<hole>b<bar> (e.g. r1p5b1p5) or solid")
        hole, bar = (float(v.replace("p", ".")) for v in m.group(1, 2))
        keep = (lambda x, y, rho: math.hypot(x, y) + rho <= r_open)
        g, centres = round_screen(hole, bar, -r_bore, r_bore, -r_bore, r_bore, z_plate, t, keep=keep,
                                  sides=int(opts["sides"]))
        geoms += g
    # invisible lid above the rim, so a dry run can't throw a specimen out
    geoms.append(box(-r_bore - WALL, r_bore + WALL, -r_bore - WALL, r_bore + WALL, z_rim, z_rim + 2.0, LID_RGBA, "lid"))
    zones = [{"name": "retained", "box": [-r_bore, r_bore, -r_bore, r_bore, z_plate, z_rim]},
             {"name": "passed", "box": [-r_bore, r_bore, -r_bore, r_bore, z_floor, z_plate]}]
    open_area = len(centres) * math.pi * hole * hole / 4
    layer = {"zone": "retained", "insert": screen, "rule": "round" if hole else "solid", "opening_mm": hole,
             "opening": f"{hole:g} mm round holes ({len(centres)}), bars {bar:g} mm" if hole else "solid plate",
             "surface_z_mm": [z_plate, z_top], "holes": len(centres), "open_area_mm2": round(open_area, 1),
             "open_pct_of_plate": round(100 * open_area / (math.pi * r_open ** 2), 1),
             "hole_centres_mm": [[round(x, 3), round(y, 3)] for x, y in centres]}
    name = f"entosieve:{screen}" + "".join(f",{k}={opts[k]:g}" for k in DEFAULTS if opts[k] != DEFAULTS[k])
    return Design(
        name=name, geoms=geoms, zones=zones,
        spawn=[-SPAWN_R, SPAWN_R, -SPAWN_R, SPAWN_R, *((z_top + 0.2, z_top + opts["drop"]) if opts["drop"] > 0 else
                                                       (z_top + SPAWN_Z[0], z_top + SPAWN_Z[1]))],
        ideal_zone=functools.partial(ideal_zone, hole=hole),
        info={"source": "Ascenzi et al. 2025 (PMC12225705) and its OSF build files (osf.io/6t25n); see ENTOSIEVE.md",
              "layers": [layer], "plate_top_z_mm": z_top, "plate_bottom_z_mm": z_plate, "rim_z_mm": z_rim,
              "open_diameter_mm": opts["d"], "bore_mm": opts["bore"], "catch_floor_z_mm": z_floor,
              "liquid_boxes": [[-r_bore, r_bore, -r_bore, r_bore, z_plate, z_rim]], "geoms": len(geoms),
              "catch_note": "the catch floor moves with the container (in EntoSieve it stands still in the lab)"})


if __name__ == "__main__":
    import sys
    for spec in sys.argv[1:] or ["entosieve:r1p5b1p5", "entosieve:r3b2", "entosieve:r5b3"]:
        kind, _, arg = spec.partition(":")
        d = build([a for a in arg.split(",") if a])
        L = d.info["layers"][0]
        print(f"{d.name}: {d.info['geoms']} geoms, {L['opening']}, open area {L['open_pct_of_plate']} % of the plate")
