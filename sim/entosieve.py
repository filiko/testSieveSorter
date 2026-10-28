"""EntoSieve replication (ENTOSIEVE.md): the paper's sieve container, round-hole plates and stroke, dry and in water.

EntoSieve (Ascenzi et al. 2025, PMC12225705) sorted Malaise specimens by body length with three plates used one after
another: 1.5 mm holes, then 3 mm, then 5 mm, giving four fractions A < 1.5 mm, B 1.5-3, C 3-5, D > 5 mm long. Here each
plate is one sim run (designs_entosieve.py) with the same specimens (same seed); a specimen's fraction is the first plate
it passes, as in the paper's sequence. Efficiency of class X = the share of class-X specimens that end in fraction X.
Specimens: insects.MALAISE_MIX_STRATIFIED, each weighted by insects.MALAISE_SHARES over its stratum's share in the run.

flexy(stroke, n, dt) is the motion as EntoSieve's firmware drives it (osf.io/6t25n, EntoSive_v1_1.ino: FlexyStepper,
acceleration 100 mm/s^2, speed knob 25-100 mm/s): from 0 up to stroke_mm and back down, accelerating at accel_mm_s2 to
at most speed_mm_s and decelerating to rest at each end. sorter.py calls it for --stroke flexy:...

Run from sim\\ (WSL venv):
    <venv python> entosieve.py run --workers 8 [--cycles 6] [--conditions dry,water_e0,water_e0.5,water_e1]
    <venv python> entosieve.py report            tables from out/entosieve/rows/*.json (markdown)
    <venv python> entosieve.py curve --plate MA --condition water_e0 --cycles 40    passage per cycle on one plate
    <venv python> entosieve.py one --plate r1p5b1p5 --condition water_e0 --seed 0 --out out/runs/ento_1p5
"""
import argparse
import json
import multiprocessing as mp
import os
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "entosieve"
# ASSUMED: the paper gives hole diameters and 1 mm aluminium, not the hole pitch. These are the common punched-plate
# layouts for those holes (60 deg staggered, Rv 1.5-3, Rv 3-5, Rv 5-8).
PLATES = {"MA": "r1p5b1p5", "MB": "r3b2", "MC": "r5b3"}
HOLES = {"MA": 1.5, "MB": 3.0, "MC": 5.0}
STROKE = {"profile": "flexy", "stroke_mm": 50.0, "speed_mm_s": 100.0, "accel_mm_s2": 100.0, "angle_deg": 90.0}
WATER_ABOVE_PLATE = 40.0      # mm at the lowest position (paper: 30-50); the 50 mm stroke lifts the plate 10 mm out
SETTLE_S = 1.5
CLASSES = [("A", 0.0, 1.5), ("B", 1.5, 3.0), ("C", 3.0, 5.0), ("D", 5.0, 1e9)]
PAPER = {"test 1 (6 min per plate)": {"A": 95.56, "B": 97.57, "C": 98.39, "D": 100.0},
         "test 2 (20 min per plate)": {"A": 78.32, "B": 96.0, "C": 94.65, "D": 100.0}}
CONDITIONS = {"dry": None,
              "water_e0": {"liquid": "water", "entrain": 0.0},
              "water_e0.5": {"liquid": "water", "entrain": 0.5},
              "water_e1": {"liquid": "water", "entrain": 1.0},
              "ethanol_e0": {"liquid": "ethanol", "entrain": 0.0},
              # exploratory: the same still bath plus liquid.ScreenFlow, the flow through the holes (unvalidated)
              "water_e0_holeflow": {"liquid": "water", "entrain": 0.0, "screen_flow": 1}}
FRICTIONS = [0.3, 0.4, 0.5]   # sweep.py's default friction sets
SEEDS = [0, 1, 2]


def flexy(stroke, n, dt):
    """Displacement, velocity and acceleration along the stroke axis at each of n steps, starting at rest at 0."""
    L = float(stroke["stroke_mm"])
    vmax = float(stroke.get("speed_mm_s", 100.0))
    acc = float(stroke.get("accel_mm_s2", 100.0))
    t_acc = vmax / acc
    if acc * t_acc * t_acc > L:                     # never reaches vmax: triangular speed profile
        t_acc = np.sqrt(L / acc)
        vmax = acc * t_acc
    t_cru = (L - acc * t_acc * t_acc) / vmax
    leg = 2 * t_acc + t_cru
    t = (np.arange(n) * dt) % (2 * leg)
    up = t < leg
    tau = np.where(up, t, t - leg)
    s = np.where(tau < t_acc, 0.5 * acc * tau ** 2,
                 np.where(tau < t_acc + t_cru, 0.5 * acc * t_acc ** 2 + vmax * (tau - t_acc),
                          L - 0.5 * acc * (leg - tau) ** 2))
    sd = np.where(tau < t_acc, acc * tau, np.where(tau < t_acc + t_cru, vmax, acc * (leg - tau)))
    sdd = np.where(tau < t_acc, acc, np.where(tau < t_acc + t_cru, 0.0, -acc))
    return np.where(up, s, L - s), np.where(up, sd, -sd), np.where(up, sdd, -sdd)


def period(stroke=STROKE):
    """Seconds per up-and-down cycle, and the peak speed."""
    L, vmax, acc = float(stroke["stroke_mm"]), float(stroke.get("speed_mm_s", 100.0)), float(stroke.get("accel_mm_s2", 100.0))
    t_acc = min(vmax / acc, np.sqrt(L / acc))
    v = acc * t_acc
    return 2 * (2 * t_acc + (L - acc * t_acc * t_acc) / v), v


def length_class(L):
    return next(c for c, lo, hi in CLASSES if lo <= L < hi)


def config(plate, condition, seed, friction, cycles, out_dir=None, fps=10.0):
    import designs
    import insects
    import sorter
    spec = f"entosieve:{PLATES[plate]}"
    top = designs.build(spec).info["plate_top_z_mm"]
    lq = CONDITIONS[condition]
    if lq is not None:
        lq = {**lq, "level_mm": top + WATER_ABOVE_PLATE}
    return sorter.RunConfig(design=spec, mix=dict(insects.MALAISE_MIX_STRATIFIED), stroke=dict(STROKE),
                            duration_s=cycles * period()[0], settle_s=SETTLE_S, seed=seed, dt=1.25e-4,
                            contact={"friction": friction, "timeconst": 2.5e-4, "dampratio": 1.0}, liquid=lq,
                            record_fps=fps, out_dir=out_dir)


def specimens(seed):
    """The run's specimens, regenerated exactly as sorter.run makes them: kind, plan, L (mm), dims."""
    import insects
    import sorter
    rng = np.random.default_rng(seed)
    out = []
    for k, n in insects.MALAISE_MIX_STRATIFIED.items():
        for _ in range(n):
            p = sorter.make_particle(k, rng)
            out.append({"kind": k, "plan": p.xml.split()[1], "L": float(p.xml.split()[2][2:-3]), "dims": p.dims})
    return out


def one(job):
    """Run one plate/condition/seed/friction; returns a compact row (written to out/entosieve/rows/<key>.json)."""
    import sorter
    key = job["key"]
    path = OUT / "rows" / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    run_dir = OUT / "runs" / key
    cfg = config(job["plate"], job["condition"], job["seed"], job["friction"], job["cycles"], str(run_dir))
    t0 = time.perf_counter()
    r = sorter.run(cfg)
    tr = np.load(run_dir / "traj.npz")
    t, pos, quat = tr["t"], tr["pos"], tr["quat"]
    info = r["design_info"]
    zb = info["plate_bottom_z_mm"]
    # Passed = under the plate's LOWEST position (lab z, the plate bottom at tray_d = 0). The plate never comes back
    # down there, so it can't sweep the specimen back up through a hole, as it can while a specimen is still inside
    # the 50 mm the plate sweeps through; in EntoSieve such a specimen sinks on into the collecting bowl.
    below = pos[:, :, 2] + tr["tray_d"][:, None, 2] < zb
    first = np.where(below.any(0), np.argmax(below, axis=0), -1)
    t_pass = [None if f < 0 else round(float(t[f] - SETTLE_S), 3) for f in first]
    # final pose of the specimens still on the plate: tilt of the body's long (x) axis from horizontal
    w, x, y, z = (quat[-1, :, k] for k in range(4))
    xz = 2 * (x * z - w * y)                            # z component of the body x axis
    tilt = np.degrees(np.arcsin(np.clip(np.abs(xz), 0, 1)))
    spec = specimens(job["seed"])
    rows = [{"kind": s["kind"], "plan": s["plan"], "L": round(s["L"], 4), "width": s["dims"]["width"],
             "thickness": s["dims"]["thickness"], "span": s["dims"]["span"], "zone": p["final_zone"],
             "passed": tp is not None, "t_pass": tp, "tilt_end_deg": round(float(tl), 1)}
            for s, p, tp, tl in zip(spec, r["particles"], t_pass, tilt)]
    row = {**{k: job[k] for k in ("key", "plate", "condition", "seed", "friction", "cycles")},
           "period_s": period()[0], "wall_s": round(time.perf_counter() - t0, 1), "steps": r["steps"],
           "ms_per_step": round(1000 * r["wall_s"] / r["steps"], 3), "resets": len(r["unstable_resets"]),
           "max_pen_mm": r["max_penetration_mm"], "liquid": r.get("liquid"), "specimens": rows}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=0, default=float))
    for f in ("scene.json", "results.json"):            # keep traj.npz only; the rows hold what the report needs
        (run_dir / f).unlink(missing_ok=True)
    print(f"  {key}: {sum(s['passed'] for s in rows)}/{len(rows)} passed, {row['ms_per_step']} ms/step, "
          f"{row['wall_s']} s wall, resets {row['resets']}", flush=True)
    return row


def jobs(conditions, cycles, seeds=SEEDS, frictions=FRICTIONS, plates=tuple(PLATES)):
    out = []
    for c in conditions:
        for plate in plates:
            for seed in seeds:
                for f in frictions:
                    out.append({"key": f"{plate}_{c}_s{seed}_mu{f:g}_c{cycles:g}", "plate": plate, "condition": c,
                                "seed": seed, "friction": f, "cycles": cycles})
    return out


def free_gb():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable"):
                return int(line.split()[1]) / 1e6
    except OSError:
        pass
    return 99.0


def run_all(jl, workers):
    todo = [j for j in jl if not (OUT / "rows" / f"{j['key']}.json").exists()]
    print(f"{len(jl)} jobs, {len(todo)} to run, {workers} workers, {free_gb():.1f} GB free", flush=True)
    if free_gb() < 3.0:
        raise SystemExit("under 3 GB free: back off")
    with mp.get_context("spawn").Pool(workers, maxtasksperchild=1) as pool:
        for _ in pool.imap_unordered(one, todo):
            pass


# ---------- report ----------
def load(cycles=None):
    rows = [json.loads(p.read_text()) for p in sorted((OUT / "rows").glob("*.json"))]
    return [r for r in rows if cycles is None or r["cycles"] == cycles]


def weights():
    """Importance weight of each stratum: real share / share in MALAISE_MIX_STRATIFIED."""
    import insects
    n = insects.MALAISE_MIX_STRATIFIED
    tot = sum(n.values())
    real = dict(zip(n, insects.MALAISE_SHARES.values()))
    return {k: real[k] / (n[k] / tot) for k in n}


def chain(rows_by_plate, t_max=None):
    """Per specimen (same seed and friction on every plate): its fraction = the first plate it passes (by t_max)."""
    plates = list(PLATES)
    spec = rows_by_plate[plates[0]]["specimens"]
    out = []
    for i, s in enumerate(spec):
        frac = "D"
        for pl, fr in zip(plates, "ABC"):
            p = rows_by_plate[pl]["specimens"][i]
            ok = p["passed"] if t_max is None else (p["t_pass"] is not None and p["t_pass"] <= t_max)
            if ok:
                frac = fr
                break
        out.append({**s, "cls": length_class(s["L"]), "frac": frac})
    return out


def efficiencies(cases, w):
    """Weighted per-class efficiency (%) and counts over a list of chained specimen lists."""
    num, den, cnt = {c: 0.0 for c, *_ in CLASSES}, {c: 0.0 for c, *_ in CLASSES}, {c: 0 for c, *_ in CLASSES}
    for spec in cases:
        for s in spec:
            ww = w[s["kind"]]
            den[s["cls"]] += ww
            num[s["cls"]] += ww * (s["frac"] == s["cls"])
            cnt[s["cls"]] += 1
    return {c: (100 * num[c] / den[c] if den[c] else None) for c in num}, cnt


def lying(row, near_mm=3.0):
    """[(kind, tilt of the body's long axis from the plate, deg)] for specimens resting on the plate in every recorded
    frame at the top of a stroke (from the run's traj.npz), or None if the trajectory is gone."""
    import designs
    path = OUT / "runs" / row["key"] / "traj.npz"
    if not path.exists():
        return None
    tr = np.load(path)
    td, pos, quat = tr["tray_d"][:, 2], tr["pos"], tr["quat"]
    top = designs.build(f"entosieve:{PLATES[row['plate']]}").info["plate_top_z_mm"]
    frames = np.flatnonzero(td > STROKE["stroke_mm"] - 1.0)
    kinds = [s["kind"] for s in row["specimens"]]
    out = []
    for f in frames:
        w, x, y, z = (quat[f, :, k] for k in range(4))
        tilt = np.degrees(np.arcsin(np.clip(np.abs(2 * (x * z - w * y)), 0, 1)))
        on = (pos[f, :, 2] > top) & (pos[f, :, 2] < top + near_mm)
        out += [(kinds[i], float(tilt[i])) for i in np.flatnonzero(on)]
    return out


def grouped(rows):
    """{(condition, seed, friction): {plate: row}} for complete triples."""
    g = {}
    for r in rows:
        g.setdefault((r["condition"], r["seed"], r["friction"]), {})[r["plate"]] = r
    return {k: v for k, v in g.items() if len(v) == len(PLATES)}


def report(cycles=None):
    rows = load(cycles)
    if not rows:
        print("no rows in", OUT / "rows")
        return
    w = weights()
    g = grouped(rows)
    T, vpk = period()
    conds = [c for c in CONDITIONS if any(k[0] == c for k in g)]
    print(f"Stroke: {STROKE['stroke_mm']:g} mm up and down, peak {vpk:.0f} mm/s, {T:.2f} s per cycle; "
          f"{rows[0]['cycles']:g} cycles simulated per plate; water {WATER_ABOVE_PLATE:g} mm over the plate at the bottom.\n")
    print("| condition | A < 1.5 mm | B 1.5-3 | C 3-5 | D > 5 | mean | runs (seeds x friction) | specimens A/B/C/D |")
    print("|---|---|---|---|---|---|---|---|")
    for name, p in PAPER.items():
        print(f"| EntoSieve paper, {name} | {p['A']:.1f} | {p['B']:.1f} | {p['C']:.1f} | {p['D']:.1f} | "
              f"{np.mean(list(p.values())):.1f} | | |")
    summary = {}
    for c in conds:
        keys = [k for k in g if k[0] == c]
        cases = [chain(g[k]) for k in keys]
        eff, cnt = efficiencies(cases, w)
        per_run = [efficiencies([chain(g[k])], w)[0] for k in keys]
        sd = {cl: np.std([e[cl] for e in per_run if e[cl] is not None]) for cl in eff}
        summary[c] = (eff, sd)
        print(f"| sim, {c.replace('_', ' ')} | " + " | ".join(f"{eff[cl]:.1f} ± {sd[cl]:.1f}" for cl, *_ in CLASSES)
              + f" | {np.mean([eff[cl] for cl, *_ in CLASSES]):.1f} | {len(keys)} | "
              + "/".join(str(cnt[cl]) for cl, *_ in CLASSES) + " |")
    print("\n± is the spread (sd) of one run's efficiency across seeds and friction sets.")
    # passage per plate by class
    print("\nShare of each length class that passes each plate (weighted), all runs pooled:\n")
    print("| condition | plate | A < 1.5 | B 1.5-3 | C 3-5 | D > 5 |")
    print("|---|---|---|---|---|---|")
    for c in conds:
        for pl in PLATES:
            num, den = {}, {}
            for k, rp in g.items():
                if k[0] != c:
                    continue
                for s in rp[pl]["specimens"]:
                    cl = length_class(s["L"])
                    num[cl] = num.get(cl, 0) + w[s["kind"]] * s["passed"]
                    den[cl] = den.get(cl, 0) + w[s["kind"]]
            print(f"| {c.replace('_', ' ')} | {HOLES[pl]:g} mm | " + " | ".join(
                f"{100 * num[cl] / den[cl]:.0f} %" if den.get(cl) else "-" for cl, *_ in CLASSES) + " |")
    # length vs width: does the hole cut by length?
    print("\nPassing the 1.5 mm plate, specimens whose width fits the hole (width < 1.5 mm), by body length (weighted):\n")
    print("| condition | L < 1.5 | 1.5-2 | 2-3 | 3-5 | > 5 |")
    print("|---|---|---|---|---|---|")
    bins = [(0, 1.5), (1.5, 2), (2, 3), (3, 5), (5, 99)]
    for c in conds:
        cells = []
        for lo, hi in bins:
            num = den = 0.0
            for k, rp in g.items():
                if k[0] != c:
                    continue
                for s in rp["MA"]["specimens"]:
                    if s["width"] < 1.5 and lo <= s["L"] < hi:
                        den += w[s["kind"]]
                        num += w[s["kind"]] * s["passed"]
            cells.append(f"{100 * num / den:.0f} %" if den else "-")
        print(f"| {c.replace('_', ' ')} | " + " | ".join(cells) + " |")
    # how retained specimens lie on the plate
    print("\nHow specimens lie on the 1.5 mm plate at the top of each stroke (plate out of the water), all frames at the "
          "top, specimens within 3 mm of the plate (weighted):\n")
    print("| condition | specimens on the plate | long axis within 20 deg of the plate | more than 45 deg (end-up) |")
    print("|---|---|---|---|")
    for c in conds:
        flat = up = tot = 0.0
        for k, rp in g.items():
            if k[0] != c:
                continue
            res = lying(rp["MA"])
            if res is None:
                continue
            for (wkind, tilt) in res:
                ww = w[wkind]
                tot += ww
                flat += ww * (tilt < 20)
                up += ww * (tilt > 45)
        if tot:
            print(f"| {c.replace('_', ' ')} | {tot:.0f} (weighted) | {100 * flat / tot:.0f} % | {100 * up / tot:.0f} % |")
    # efficiency over time
    print("\nEfficiency over time (wet runs; a specimen counts once it has passed by then):\n")
    nc = int(rows[0]["cycles"])
    print("| condition | cycles | " + " | ".join(cl for cl, *_ in CLASSES) + " |")
    print("|---|---|" + "---|" * len(CLASSES))
    for c in conds:
        keys = [k for k in g if k[0] == c]
        for ncyc in sorted({1, 2, max(1, nc // 2), nc}):
            eff, _ = efficiencies([chain(g[k], t_max=ncyc * T) for k in keys], w)
            print(f"| {c.replace('_', ' ')} | {ncyc} | " + " | ".join(f"{eff[cl]:.1f}" for cl, *_ in CLASSES) + " |")
    # passage rate per cycle, and where a constant rate would get to in the paper's 6 min (an extrapolation)
    n6 = 360.0 / T
    print(f"\nPer-cycle passage of the specimens that fit (fraction of those not yet through that pass in one cycle, "
          f"cycles 2 to {nc}), and the share through after {n6:.0f} cycles (6 min) IF that rate held. "
          "An extrapolation with an ASSUMED constant rate, not a sim result:\n")
    print("| condition | plate | class | through after 1 cycle | after " + f"{nc}" + " cycles | per-cycle rate | "
          f"through after {n6:.0f} cycles (extrapolated) |")
    print("|---|---|---|---|---|---|---|")
    for c in conds:
        for pl, fits in (("MA", "A"), ("MB", "B"), ("MC", "C")):
            num1 = numN = den = 0.0
            for k, rp in g.items():
                if k[0] != c:
                    continue
                for s in rp[pl]["specimens"]:
                    if length_class(s["L"]) != fits:
                        continue
                    ww = w[s["kind"]]
                    den += ww
                    tp = s["t_pass"]
                    num1 += ww * (tp is not None and tp <= T)
                    numN += ww * (tp is not None)
            if not den:
                continue
            r1, rN = 1 - num1 / den, 1 - numN / den
            rate = 1 - (rN / r1) ** (1 / (nc - 1)) if r1 > 0 and rN > 0 and nc > 1 else float("nan")
            ext = 1 - rN * (1 - rate) ** (n6 - nc) if np.isfinite(rate) else float("nan")
            print(f"| {c.replace('_', ' ')} | {HOLES[pl]:g} mm | {fits} | {100 * (1 - r1):.0f} % | {100 * (1 - rN):.0f} % | "
                  f"{100 * rate:.1f} % | {100 * ext:.0f} % |")
    # cost
    print("\n| condition | plate | ms/step (mean) | liquid ms/step | resets | worst overlap mm |")
    print("|---|---|---|---|---|---|")
    for c in conds:
        for pl in PLATES:
            rr = [r for r in rows if r["condition"] == c and r["plate"] == pl]
            if rr:
                lq = [r["liquid"]["ms_per_step"] for r in rr if r.get("liquid")]
                print(f"| {c.replace('_', ' ')} | {HOLES[pl]:g} mm | {np.mean([r['ms_per_step'] for r in rr]):.2f} | "
                      f"{np.mean(lq) if lq else 0:.2f} | {sum(r['resets'] for r in rr)} | "
                      f"{max(r['max_pen_mm'] for r in rr):.3f} |")
    return summary


def curve(plate, condition, cycles):
    """Share (weighted) of each length class through one plate after each cycle, over every run of that plate,
    condition and length: does the per-cycle rate stay constant?"""
    rows = [r for r in load(cycles) if r["plate"] == plate and r["condition"] == condition]
    if not rows:
        print("no rows")
        return
    w, T = weights(), period()[0]
    print(f"{plate} ({HOLES[plate]:g} mm), {condition}, {len(rows)} runs, {cycles:g} cycles each\n")
    print("| cycles | " + " | ".join(c for c, *_ in CLASSES) + " |")
    print("|---|" + "---|" * len(CLASSES))
    for n in sorted({1, 2, 4, 8, 12, 16, 20, 25, 30, 35, 40} & set(range(1, int(cycles) + 1))):
        cells = []
        for cl, *_ in CLASSES:
            num = den = 0.0
            for r in rows:
                for s in r["specimens"]:
                    if length_class(s["L"]) == cl:
                        den += w[s["kind"]]
                        num += w[s["kind"]] * (s["t_pass"] is not None and s["t_pass"] <= n * T)
            cells.append(f"{100 * num / den:.0f} %" if den else "-")
        print(f"| {n} | " + " | ".join(cells) + " |")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("what", choices=["run", "report", "one", "curve"])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--cycles", type=float, default=6)
    ap.add_argument("--conditions", default="dry,water_e0,water_e0.5,water_e1")
    ap.add_argument("--seeds", default=",".join(map(str, SEEDS)))
    ap.add_argument("--frictions", default=",".join(f"{f:g}" for f in FRICTIONS))
    ap.add_argument("--plates", default=",".join(PLATES))
    ap.add_argument("--plate", default="MA")
    ap.add_argument("--condition", default="water_e0")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--friction", type=float, default=0.4)
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    os.chdir(HERE)
    if a.what == "run":
        jl = jobs(a.conditions.split(","), a.cycles, [int(s) for s in a.seeds.split(",")],
                  [float(f) for f in a.frictions.split(",")], a.plates.split(","))
        run_all(jl, a.workers)
        report(a.cycles)
    elif a.what == "report":
        report(a.cycles if a.cycles else None)
    elif a.what == "curve":
        curve(a.plate, a.condition, a.cycles)
    else:
        import sorter
        plate = a.plate if a.plate in PLATES else next(k for k, v in PLATES.items() if v == a.plate)
        cfg = config(plate, a.condition, a.seed, a.friction, a.cycles, a.out, a.fps)
        r = sorter.run(cfg)
        print(f"{r['design']}: {r['counts']}, {1000 * r['wall_s'] / r['steps']:.2f} ms/step, resets "
              f"{len(r['unstable_resets'])}" + (f", recorded to {a.out}" if a.out else ""))


if __name__ == "__main__":
    main()
