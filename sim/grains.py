"""Pantry grains for the sorter sim: the bench calibration set. Units mm, g, s.

Sizes are typical values until the team's caliper measurements replace them: once
bench/grain_dims.csv has at least MIN_MEASURED rows of a kind, that kind's mean size, spread and
density come from the measurements. Each dimension varies by the kind's relative spread (SD until
measured), clipped to +/-20%.

    rice      long-grain, an ellipsoid
    quinoa    a lens: round, flat ellipsoid
    chickpea  a near-round ellipsoid
    pasta     ditalini: a short tube of 8 boxes, open at both ends

Run from sim\\ to print one of each:  <venv python> grains.py
"""
import csv
from pathlib import Path

import numpy as np
from common import Particle

SD = 0.07
SPREAD = {}                  # measured relative spread per kind; SD for the rest
# kind: ((length, width, thickness) mm, density g/mm^3, rgba). Pasta: (outer diameter, outer diameter, length).
SIZES = {
    "rice": ((6.5, 2.0, 1.7), 1.45e-3, "0.96 0.95 0.88 1"),
    "quinoa": ((2.0, 2.0, 1.1), 1.20e-3, "0.82 0.62 0.38 1"),
    "chickpea": ((8.5, 8.0, 7.5), 1.30e-3, "0.88 0.76 0.42 1"),
    "pasta": ((6.5, 6.5, 6.0), 1.45e-3, "0.97 0.70 0.20 1"),
}
PASTA_WALL = 1.2
PASTA_SEGMENTS = 8
KINDS = tuple(SIZES)
MEASURED = Path(__file__).resolve().parent / "bench" / "grain_dims.csv"
MIN_MEASURED = 5             # grains of a kind needed before the measurements replace SIZES


def load_measured(path=MEASURED):
    """Replace SIZES and SPREAD with bench measurements where a kind has MIN_MEASURED rows: mean size,
    the mean relative spread, and density from mass over ellipsoid volume (pasta keeps its density).
    Returns the kinds that changed."""
    if not path.exists():
        return []
    rows = [r for r in csv.DictReader(open(path, encoding="utf-8")) if r["kind"] in SIZES and r.get("length_mm")]
    changed = []
    for kind in SIZES:
        d = np.array([[float(r[k]) for k in ("length_mm", "width_mm", "thickness_mm")] for r in rows if r["kind"] == kind])
        if len(d) < MIN_MEASURED:
            continue
        mean = d.mean(axis=0)
        SPREAD[kind] = float(np.mean(d.std(axis=0) / mean))
        density = SIZES[kind][1]
        masses = [float(r["mass_mg"]) for r in rows if r["kind"] == kind and r.get("mass_mg")]
        if masses and kind != "pasta":
            density = np.mean(masses) * 1e-3 / (np.pi / 6 * np.prod(mean))
        SIZES[kind] = (tuple(mean.round(3)), float(density), SIZES[kind][2])
        changed.append(kind)
    return changed


load_measured()


def make(kind, rng, size_scale=1.0):
    base, density, rgba = SIZES[kind]
    d = np.array(base) * size_scale * np.clip(rng.normal(1.0, SPREAD.get(kind, SD), 3), 0.8, 1.2)
    if kind == "quinoa":
        d[1] = d[0]
    if kind == "pasta":
        d[1] = d[0]
        r_out, half_len = d[0] / 2, d[2] / 2
        seg = np.pi / PASTA_SEGMENTS
        geoms = []
        for k in range(PASTA_SEGMENTS):
            a = 2 * seg * k
            r_mid = r_out - PASTA_WALL / 2
            geoms.append(
                f'<geom type="box" size="{PASTA_WALL / 2:.4f} {r_out * np.tan(seg):.4f} {half_len:.4f}" '
                f'pos="{r_mid * np.cos(a):.4f} {r_mid * np.sin(a):.4f} 0" quat="{np.cos(a / 2):.5f} 0 0 {np.sin(a / 2):.5f}" '
                f'density="{density}" rgba="{rgba}"/>')
        xml = "".join(geoms)
    else:
        xml = f'<geom type="ellipsoid" size="{d[0] / 2:.4f} {d[1] / 2:.4f} {d[2] / 2:.4f}" density="{density}" rgba="{rgba}"/>'
    length, width, thickness = sorted(d, reverse=True)
    span = float(np.hypot(d[0], d[2])) if kind == "pasta" else float(length)
    return Particle(kind, "grain", xml, {"length": float(length), "width": float(width),
                                         "thickness": float(thickness), "span": span})


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    print("measured kinds from", MEASURED.name, ":", load_measured() or "none yet")
    for kind in KINDS:
        p = make(kind, rng)
        print(kind, {k: round(v, 2) for k, v in p.dims.items()})
