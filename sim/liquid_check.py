"""Validation of liquid.py (LIQUID.md). Prints markdown tables; nothing is tuned here.

    <venv python> liquid_check.py stokes      closed-form Stokes drag of spheroids vs liquid.py's ellipsoid integrals
    <venv python> liquid_check.py settle      terminal velocity of spheres and ellipsoids vs published correlations
    <venv python> liquid_check.py neutral     a neutral body stays put; a light one floats up and rests at the surface
    <venv python> liquid_check.py frames      a neutral sphere in a box shaken at 40 Hz: entrain 1 rides along, 0 stays
    <venv python> liquid_check.py box         Malaise specimens on a box floor shaken at 40 Hz, 0.35 mm: dry vs wet
    <venv python> liquid_check.py all         all of the above
    <venv python> liquid_check.py cost        resets and wall time per step, dry vs wet: buzzed tower and seesaw (6 workers)
    <venv python> liquid_check.py clump       a Malaise insect clump on the seesaw, dry vs in ethanol (4 workers)
    <venv python> liquid_check.py sink        how fast the generated Malaise specimens sink in still ethanol and water

References (sources in LIQUID.md): Clift, Grace & Weber 1978 standard sphere curve (Table 5.2); Stokes; exact Stokes
drag of spheroids (Happel & Brenner 1983 / Chwang & Wu 1975); Hoelzer & Sommerfeld 2008 (orientation-specific);
Ganser 1993 (with the orientation's exact Stokes factor); Bagheri & Bonadonna 2016 (freely falling particles).
"""
import sys

import mujoco
import numpy as np

import common
import liquid

G = liquid.G


# ---------- reference correlations ----------
def clift_cd(Re):
    """Clift, Grace & Weber (1978) Table 5.2, smooth sphere, Re < 1500."""
    w = np.log10(Re)
    if Re < 0.01:
        return 3 / 16 + 24 / Re
    if Re < 20:
        return 24 / Re * (1 + 0.1315 * Re ** (0.82 - 0.05 * w))
    if Re < 260:
        return 24 / Re * (1 + 0.1935 * Re ** 0.6305)
    return 10 ** (1.6435 - 1.1242 * w + 0.1558 * w * w)


def spheroid_stokes(a, b, along_axis):
    """Exact Stokes drag per unit (mu U) of a spheroid with polar semi-axis a and equatorial b, moving along its axis
    of symmetry or across it (Happel & Brenner 1983; Chwang & Wu 1975)."""
    if abs(a - b) < 1e-9 * a:
        return 6 * np.pi * a
    if a > b:                                          # prolate
        e = np.sqrt(1 - b * b / (a * a))
        L = np.log((1 + e) / (1 - e))
        if along_axis:
            return 16 * np.pi * a * e ** 3 / ((1 + e * e) * L - 2 * e)
        return 32 * np.pi * a * e ** 3 / (2 * e + (3 * e * e - 1) * L)
    e = np.sqrt(1 - a * a / (b * b))                   # oblate: b equatorial radius, a polar
    if along_axis:
        return 8 * np.pi * b * e ** 3 / (e * np.sqrt(1 - e * e) - (1 - 2 * e * e) * np.arcsin(e))
    return 16 * np.pi * b * e ** 3 / ((1 + 2 * e * e) * np.arcsin(e) - e * np.sqrt(1 - e * e))


def solve_v(cd_of_re, weight, rho, mu, d, area):
    """Terminal speed with drag C_D(Re) 1/2 rho v^2 area = weight, Re = rho v d / mu (bisection in log v)."""
    lo, hi = 1e-6, 1e5
    for _ in range(200):
        v = np.sqrt(lo * hi)
        Re = rho * v * d / mu
        f = cd_of_re(Re) * 0.5 * rho * v * v * area - weight
        lo, hi = (v, hi) if f < 0 else (lo, v)
    return np.sqrt(lo * hi)


def hs_cd(Re, phi, phi_perp):
    return (8 / (Re * np.sqrt(phi_perp)) + 16 / (Re * np.sqrt(phi)) + 3 / (np.sqrt(Re) * phi ** 0.75)
            + 0.42 * 10 ** (0.4 * (-np.log10(phi)) ** 0.2) / phi_perp)


def ganser_cd(Re, kS, kN):
    x = Re * kN / kS
    return 24 * kS / Re * (1 + 0.1118 * x ** 0.6567) + 0.4305 * kN / (1 + 3305 / x)


def bagheri_cd(Re, semi, rho_ratio):
    """Bagheri & Bonadonna 2016, Eq. 34, freely falling; L >= I >= S the particle's lengths, ellipsoid form."""
    S, I, L = np.sort(2 * np.asarray(semi))
    f, e = S / I, I / L
    dv = (L * I * S) ** (1 / 3)                    # ellipsoid: d_eq^3 = L I S
    FS = f * e ** 1.3 * (dv ** 3 / (L * I * S))
    FN = f * f * e * (dv ** 3 / (L * I * S))
    kS = (FS ** (1 / 3) + FS ** (-1 / 3)) / 2
    lr = np.log10(rho_ratio)
    a2 = 0.45 + 10 / (np.exp(2.5 * lr) + 30)
    b2 = 1 - 37 / (np.exp(3 * lr) + 100)
    kN = 10 ** (a2 * (-np.log10(FN)) ** b2)
    x = Re * kN / kS
    return 24 * kS / Re * (1 + 0.125 * x ** (2 / 3)) + 0.46 * kN / (1 + 5330 / x)


# ---------- one free body in a still bath ----------
def one_body_model(xml, dt=1e-4, floor=False, quat=(1, 0, 0, 0), z=0.0):
    fl = '<geom type="box" size="60 60 1" pos="0 0 -1" friction="0.4 0.005 0.0001" solref="0.00025 1" ' \
         'solimp="0.95 0.99 0.0001"/>' if floor else ""
    q = " ".join(f"{c:g}" for c in quat)
    m = mujoco.MjModel.from_xml_string(
        f'<mujoco><option timestep="{dt}" gravity="0 0 {-G}" integrator="implicitfast"/><size memory="64M"/>'
        f'<default><geom solref="0.00025 1" solimp="0.95 0.99 0.0001" friction="0.4 0.005 0.0001"/></default>'
        f'<worldbody>{fl}<body name="p000" pos="0 0 {z}" quat="{q}"><freejoint/>{xml}</body></worldbody></mujoco>')
    return m, mujoco.MjData(m)


def ell_xml(semi, density):
    return f'<geom type="ellipsoid" size="{semi[0]:.6g} {semi[1]:.6g} {semi[2]:.6g}" density="{density:.6g}"/>'


def fall(semi, density, spec, quat=(1, 0, 0, 0), t_end=None, dt=1e-4):
    """Release from rest in a still, unbounded bath; returns terminal velocity (3), final body z-axis and x-axis."""
    xml = ell_xml(semi, density)
    m, d = one_body_model(xml, dt=dt, quat=quat)
    part = common.Particle("e", "grain", xml, {})
    lq = liquid.Liquid(spec).bind(m, d, [part], ["p000"])
    vol = 4 / 3 * np.pi * np.prod(semi)
    k_est = lq.mu * 3 * np.pi * (6 * vol / np.pi) ** (1 / 3)
    tau = (m.body_mass[1] + lq.rho * vol) / k_est
    t_end = t_end or min(max(8 * tau, 0.3), 6.0)
    hist = []
    for i in range(int(t_end / dt)):
        d.xfrc_applied[:] = 0
        lq.step(m, d, i)
        mujoco.mj_step(m, d)
        if i % 50 == 0:
            hist.append(d.qvel[:3].copy())
    R = d.xmat[1].reshape(3, 3)
    v = np.mean(hist[-10:], axis=0)
    return v, R[:, 2], R[:, 0], np.linalg.norm(hist[-1] - hist[-11]) / max(np.linalg.norm(v), 1e-12)


def cmd_stokes():
    print("| shape (semi-axes a, b, b; a along the axis) | motion | exact (Happel & Brenner) | liquid.py (Carlson) | diff |")
    print("|---|---|---|---|---|")
    for a, b in ((1.0, 1.0), (3.0, 1.0), (10.0, 1.0), (0.3, 1.0), (0.05, 1.0)):
        G_, _, _ = liquid.ellipsoid_coeffs(np.array([[a, b, b]]))
        for along, i, lab in ((True, 0, "along axis"), (False, 1, "across")):
            ex = spheroid_stokes(a, b, along)
            print(f"| {a:g}, {b:g}, {b:g} | {lab} | {ex:.4f} | {G_[0, i]:.4f} | {100 * (G_[0, i] / ex - 1):+.2f} % |")


SHAPES = {  # name: semi-axes for a long axis of 1 (scaled to the size), and the test orientations
    "sphere": ((0.5, 0.5, 0.5), [("any", (1, 0, 0, 0), 2)]),
    "prolate 3:1:1": ((0.5, 1 / 6, 1 / 6), [("broadside", (1, 0, 0, 0), 2), ("end-on", (np.sqrt(.5), 0, np.sqrt(.5), 0), 0)]),
    "oblate 1:1:0.3": ((0.5, 0.5, 0.15), [("face-on", (1, 0, 0, 0), 2), ("edge-on", (np.sqrt(.5), np.sqrt(.5), 0, 0), 1)]),
}
FLUIDS = [("water", 1.05e-3), ("water", 1.15e-3), ("ethanol", 1.05e-3)]
SIZES = [0.5, 1.0, 2.0, 4.0, 6.0]


def cmd_settle(sizes=SIZES, fluids=FLUIDS, munk=0.0):
    print("Terminal velocity, fixed orientation (munk 0). Reference: sphere Clift et al. 1978; ellipsoids Hoelzer & "
          "Sommerfeld 2008 (HS, orientation-specific) and Ganser 1993 (exact Stokes factor of the orientation). "
          "Stokes: the same body at 1000 x the viscosity against the closed form.\n")
    print("| shape | orientation | fluid | rho_b | long axis mm | Re | v sim mm/s | v ref mm/s (ref) | error | other ref | error |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    rows = []
    for shape, (semi1, orients) in SHAPES.items():
        for orient, quat, ax in orients:
            for fluid, rho_b in fluids:
                for L in sizes:
                    semi = np.array(semi1) * L
                    spec = {"liquid": fluid, "munk": munk}
                    v, _, _, drift = fall(semi, rho_b, spec, quat)
                    lq = liquid.LIQUIDS[fluid]
                    rho, mu = lq["rho"], lq["mu"]
                    vol = 4 / 3 * np.pi * semi.prod()
                    dv = (6 * vol / np.pi) ** (1 / 3)
                    W = (rho_b - rho) * G * vol
                    vs = abs(v[2])
                    Re = rho * vs * dv / mu
                    Av = np.pi * dv * dv / 4
                    a_ax = semi[ax]
                    other = [semi[i] for i in range(3) if i != ax]
                    if shape == "sphere":
                        ref = solve_v(clift_cd, W, rho, mu, dv, Av)
                        refn, ref2, ref2n = "Clift", None, ""
                    else:
                        phi_perp = Av / (np.pi * other[0] * other[1])
                        phi = min(1.0, np.pi * dv * dv / liquid.ellipsoid_area(semi[None])[0])
                        ref = solve_v(lambda r: hs_cd(r, phi, phi_perp), W, rho, mu, dv, Av)
                        G_, _, _ = liquid.ellipsoid_coeffs(semi[None])
                        kS = G_[0, ax] / (3 * np.pi * dv)
                        kN = 10 ** (1.8148 * (-np.log10(phi)) ** 0.5743)
                        ref2 = solve_v(lambda r: ganser_cd(r, kS, kN), W, rho, mu, dv, Av)
                        refn, ref2n = "HS", "Ganser"
                    err = 100 * (vs / ref - 1)
                    e2 = f"{100 * (vs / ref2 - 1):+.1f} %" if ref2 else ""
                    rows.append((shape, orient, fluid, rho_b, L, Re, vs, ref, err))
                    print(f"| {shape} | {orient} | {fluid} | {rho_b * 1e3:.2f} | {L:g} | {Re:.3g} | {vs:.3g} | {ref:.3g} ({refn}) "
                          f"| {err:+.1f} % | {f'{ref2:.3g} ({ref2n})' if ref2 else ''} | {e2} |", flush=True)
    # Stokes limit: same bodies at 1000 x viscosity, against the closed form
    print("\n| shape | orientation | Re | v sim mm/s | v Stokes closed form mm/s | error |")
    print("|---|---|---|---|---|---|")
    for shape, (semi1, orients) in SHAPES.items():
        for orient, quat, ax in orients:
            semi = np.array(semi1) * 2.0
            spec = {"liquid": "water", "mu": 1.0, "munk": munk}
            v, _, _, _ = fall(semi, 1.15e-3, spec, quat, dt=1e-4)
            W = (1.15e-3 - 0.998e-3) * G * 4 / 3 * np.pi * semi.prod()
            other = [semi[i] for i in range(3) if i != ax]
            if shape == "sphere":
                K = 6 * np.pi * semi[0]
            elif shape.startswith("prolate"):
                K = spheroid_stokes(semi[0], semi[1], ax == 0)
            else:
                K = spheroid_stokes(semi[2], semi[0], ax == 2)
            vs = abs(v[2])
            ref = W / (1.0 * K)
            Re = 0.998e-3 * vs * 2 * (semi.prod()) ** (1 / 3) / 1.0
            print(f"| {shape} | {orient} | {Re:.2g} | {vs:.4g} | {ref:.4g} | {100 * (vs / ref - 1):+.2f} % |", flush=True)
    return rows


def cmd_freefall():
    """With the Munk moment on, released 45 deg tilted: the body turns broadside; v against Bagheri & Bonadonna."""
    print("\nFree fall with the Munk moment (munk 1), released tilted 45 deg: final tilt and v against freely-falling "
          "correlations.\n")
    print("| shape | fluid | rho_b | long axis mm | final orientation | Re | v sim | v Bagheri & Bonadonna 2016 | error | v Ganser (orientation-averaged kS) | error |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    c, s = np.cos(np.pi / 8), np.sin(np.pi / 8)
    for shape in ("prolate 3:1:1", "oblate 1:1:0.3"):
        semi1 = np.array(SHAPES[shape][0])
        for fluid, rho_b in FLUIDS:
            for L in (1.0, 2.0, 4.0):
                semi = semi1 * L
                v, zax, xax, _ = fall(semi, rho_b, {"liquid": fluid, "munk": 1.0}, (c, s, s * 0.3, 0.0), t_end=4.0)
                lq = liquid.LIQUIDS[fluid]
                rho, mu = lq["rho"], lq["mu"]
                vol = 4 / 3 * np.pi * semi.prod()
                dv = (6 * vol / np.pi) ** (1 / 3)
                W = (rho_b - rho) * G * vol
                Av = np.pi * dv * dv / 4
                ref = solve_v(lambda r: bagheri_cd(r, semi, rho_b / rho), W, rho, mu, dv, Av)
                G_, _, _ = liquid.ellipsoid_coeffs(semi[None])
                kS = 3 / ((3 * np.pi * dv / G_[0]).sum())    # random orientation: harmonic mean over the 3 axes
                phi = min(1.0, np.pi * dv * dv / liquid.ellipsoid_area(semi[None])[0])
                kN = 10 ** (1.8148 * (-np.log10(phi)) ** 0.5743)
                ref2 = solve_v(lambda r: ganser_cd(r, kS, kN), W, rho, mu, dv, Av)
                vs = abs(v[2])
                Re = rho * vs * dv / mu
                if shape.startswith("prolate"):
                    tilt = np.degrees(np.arcsin(min(1.0, abs(xax[2]))))
                    o = f"long axis {tilt:.0f} deg from horizontal"
                else:
                    tilt = np.degrees(np.arccos(min(1.0, abs(zax[2]))))
                    o = f"face {tilt:.0f} deg from horizontal"
                print(f"| {shape} | {fluid} | {rho_b * 1e3:.2f} | {L:g} | {o} | {Re:.3g} | {vs:.3g} | {ref:.3g} | "
                      f"{100 * (vs / ref - 1):+.1f} % | {ref2:.3g} | {100 * (vs / ref2 - 1):+.1f} % |", flush=True)


def cmd_neutral():
    print("\n| check | result | expected |")
    print("|---|---|---|")
    # neutral sphere, still bath
    semi = np.array([1.0, 1.0, 1.0])
    rho = liquid.LIQUIDS["water"]["rho"]
    xml = ell_xml(semi, rho)
    m, d = one_body_model(xml, dt=1.25e-4)
    lq = liquid.Liquid({"liquid": "water"}).bind(m, d, [common.Particle("e", "g", xml, {})], ["p000"])
    for i in range(int(2.0 / 1.25e-4)):
        d.xfrc_applied[:] = 0
        lq.step(m, d, i)
        mujoco.mj_step(m, d)
    print(f"| neutral 2 mm sphere (rho = water's), still bath, 2 s | moved {np.linalg.norm(d.qpos[:3]):.2e} mm | 0 |")
    # neutral fly-like ellipsoid with legs, tilted, still bath
    for shape, rb, level in (("2 mm sphere", 0.90e-3, 5.0), ("prolate 3:1:1, long 3 mm", 0.90e-3, 5.0),
                             ("oblate 1:1:0.3, 3 mm", 0.90e-3, 5.0), ("2 mm sphere", 0.70e-3, 5.0)):
        semi = np.array([1.0, 1.0, 1.0]) if "sphere" in shape else (
            np.array([1.5, 0.5, 0.5]) if "prolate" in shape else np.array([1.5, 1.5, 0.45]))
        xml = ell_xml(semi, rb)
        m, d = one_body_model(xml, dt=1.25e-4, quat=(np.cos(0.3), np.sin(0.3), 0, 0))
        lq = liquid.Liquid({"liquid": "water", "level_mm": level}).bind(m, d, [common.Particle("e", "g", xml, {})], ["p000"])
        zs = []
        for i in range(int(4.0 / 1.25e-4)):
            d.xfrc_applied[:] = 0
            lq.step(m, d, i)
            mujoco.mj_step(m, d)
            if i % 80 == 0:
                zs.append(d.qpos[2])
        zs = np.array(zs)
        s_end = lq.s_body[0]
        osc = zs[-20:].max() - zs[-20:].min()
        R = d.xmat[1].reshape(3, 3)
        flat = np.degrees(np.arccos(min(1.0, abs(R[2, 2])))) if "oblate" in shape else (
            np.degrees(np.arcsin(min(1.0, abs(R[2, 0])))) if "prolate" in shape else 0.0)
        print(f"| {shape}, rho_b {rb * 1e3:.2f}, released 5 mm under the surface | rose to the surface; submerged "
              f"fraction {s_end:.3f}, last 0.5 s range {osc:.3f} mm" + (f", tilt {flat:.0f} deg" if flat else "")
              + f" | {rb / rho:.3f} (Archimedes) |")


def cmd_frames(dt=1.25e-4):
    """A neutral 1 mm sphere in liquid inside a box (the sim frame) shaken vertically at 40 Hz, 0.35 mm, with no
    contact: it should ride along with the box at entrain 1 and stay still in the lab at entrain 0."""
    print("\n| entrain | added mass | sphere motion relative to the box, amplitude mm | relative to the lab, amplitude mm | expected |")
    print("|---|---|---|---|---|")
    A0, f = 0.35, 40.0
    w = 2 * np.pi * f
    for e in (1.0, 0.5, 0.0):
        for am in (1.0, 0.0):
            rho = liquid.LIQUIDS["water"]["rho"]
            xml = ell_xml(np.array([0.5, 0.5, 0.5]), rho * 1.0)
            m, d = one_body_model(xml, dt=dt)
            box = [{"body": 0, "lo": np.array([-50.0, -50, -50]), "hi": np.array([50.0, 50, 50])}]
            lq = liquid.Liquid({"liquid": "water", "entrain": e, "added_mass": am}, box).bind(
                m, d, [common.Particle("e", "g", xml, {})], ["p000"])
            rel, lab = [], []
            n = int(0.5 / dt)
            d.qvel[2] = -(1 - e) * A0 * w          # start moving with the liquid (the box starts at full speed)
            for i in range(n):
                t = i * dt
                x, v, a = A0 * np.sin(w * t), A0 * w * np.cos(w * t), -A0 * w * w * np.sin(w * t)
                m.opt.gravity[:] = [0, 0, -a - G]
                d.xfrc_applied[:] = 0
                lq.step(m, d, i, (0, 0, x), (0, 0, v), (0, 0, a))
                mujoco.mj_step(m, d)
                if i > n // 2:
                    rel.append(d.qpos[2])
                    lab.append(d.qpos[2] + A0 * np.sin(w * (t + dt)))
            amp = lambda s: (np.max(s) - np.min(s)) / 2          # noqa: E731
            expect = {1.0: "0 relative to the box", 0.0: "0 in the lab", 0.5: "between"}[e]
            print(f"| {e:g} | {'on' if am else 'off'} | {amp(rel):.4f} | {amp(lab):.4f} | {expect} |", flush=True)


def cmd_box(seeds=(0, 1), duration=1.0):
    """Malaise specimens resting on a box floor shaken straight up and down, 40 Hz, 0.35 mm (2.3 g): dry, and in water
    and ethanol at entrain 0, 0.5 and 1, with and without added mass. Uses sorter.run on the solid EntoSieve cup."""
    import tempfile
    from pathlib import Path

    import sorter
    print("\n| condition | hop: CoM rise over rest, p50 / p95 mm | time off the floor | lateral travel mm/s | "
          "speed relative to the box, rms mm/s | resets | liquid ms/step | total ms/step |")
    print("|---|---|---|---|---|---|---|---|")
    conds = [("dry", None)]
    for fl in ("water", "ethanol"):
        for e in (0.0, 0.5, 1.0):
            conds.append((f"{fl}, entrain {e:g}", {"liquid": fl, "entrain": e}))
    conds.append(("water, entrain 0, no added mass", {"liquid": "water", "entrain": 0.0, "added_mass": 0.0}))
    conds.append(("water, entrain 0, no Munk moment", {"liquid": "water", "entrain": 0.0, "munk": 0.0}))
    for label, lqspec in conds:
        stats = []
        for seed in seeds:
            with tempfile.TemporaryDirectory() as tmp:
                cfg = sorter.RunConfig(design="entosieve:solid,drop=12", mix={"insect_malaise_lt2": 6, "insect_malaise_2to6": 6},
                                       stroke={"profile": "sine", "amp_mm": 0.35, "freq_hz": 40.0, "angle_deg": 90.0},
                                       duration_s=duration, settle_s=2.5, seed=seed, dt=1.25e-4,
                                       contact={"friction": 0.4, "timeconst": 2.5e-4, "dampratio": 1.0},
                                       liquid=lqspec, record_fps=1000.0, out_dir=tmp)
                r = sorter.run(cfg)
                tr = np.load(Path(tmp) / "traj.npz")
            t, pos = tr["t"], tr["pos"]
            sh = t >= cfg.settle_s + 0.1
            z = pos[sh][:, :, 2]
            rest = np.percentile(z, 5, axis=0)
            rise = z - rest
            dt_rec = np.diff(t[sh]).mean()
            vel = np.diff(pos[sh], axis=0) / dt_rec
            lat = np.linalg.norm(pos[sh][-1, :, :2] - pos[sh][0, :, :2], axis=1) / (t[sh][-1] - t[sh][0])
            stats.append((np.percentile(rise, 50), np.percentile(rise, 95), np.mean(rise > 0.05), lat.mean(),
                          np.sqrt((vel ** 2).sum(2).mean()), len(r["unstable_resets"]),
                          r.get("liquid", {}).get("ms_per_step", 0.0), 1000 * r["wall_s"] / r["steps"]))
        s = np.mean(stats, axis=0)
        print(f"| {label} | {s[0]:.3f} / {s[1]:.3f} | {s[2]:.0%} | {s[3]:.2f} | {s[4]:.1f} | {int(s[5])} | {s[6]:.2f} | "
              f"{s[7]:.2f} |", flush=True)


def _run(job):
    import sorter
    label, cfg = job
    r = sorter.run(sorter.RunConfig(**cfg))
    return label, r


TOWER = {"design": "inserts:5mm,2mm", "stroke": {"profile": "sine", "amp_mm": 0.35, "freq_hz": 40.0, "angle_deg": 90.0},
         "duration_s": 2.0, "settle_s": 1.0, "dt": 1.25e-4,
         "contact": {"friction": 0.4, "timeconst": 2.5e-4, "dampratio": 1.0}, "record_fps": 0.0}
SEESAW = {"design": "inserts:5mm_across,2mm_across,pitch=55,holder=seesaw",
          "stroke": {"profile": "seesaw", "deg": 10.0, "period_s": 2.0, "vib_mm": 0.3, "vib_hz": 40.0},
          "duration_s": 4.0, "settle_s": 1.0, "dt": 1.25e-4,
          "contact": {"friction": 0.4, "timeconst": 2.5e-4, "dampratio": 1.0}, "record_fps": 0.0}
CLUMP = {"design": "inserts:5mm,2mm,pitch=85", "mix": {},
         "clump": {"kinds": {"insect_malaise": 40, "leaf": 1, "twig": 2, "dirt": 10}, "bond": "medium"},
         "stroke": {"profile": "seesaw", "deg": 10.0, "period_s": 2.0},
         "duration_s": 4.0, "settle_s": 1.0, "dt": 6.25e-5,
         "contact": {"friction": 0.4, "timeconst": 2.5e-4, "dampratio": 1.0}, "record_fps": 0.0}


def cmd_cost(which=("tower", "seesaw"), seeds=(0, 1), workers=6):
    """Stability (MuJoCo resets) and wall time per step, dry vs wet, at the insect time step (dt 0.125 ms,
    timeconst 0.25 ms): the stacked tower buzzed at 40 Hz (tray frame), and the seesaw tower with the buzz."""
    import multiprocessing as mp

    import insects
    jobs = []
    wets = [("dry", None), ("ethanol, entrain 0", {"liquid": "ethanol", "entrain": 0.0}),
            ("ethanol, entrain 0.5", {"liquid": "ethanol", "entrain": 0.5}),
            ("ethanol, entrain 1", {"liquid": "ethanol", "entrain": 1.0}),
            ("water, entrain 0", {"liquid": "water", "entrain": 0.0})]
    for name in which:
        base = {"tower": TOWER, "seesaw": SEESAW}[name]
        for label, lq in wets:
            for seed in seeds:
                jobs.append(((name, label, seed), {**base, "mix": dict(insects.MALAISE_MIX_STRATIFIED), "liquid": lq,
                                                   "seed": seed}))
    with mp.get_context("spawn").Pool(workers) as pool:
        res = pool.map(_run, jobs)
    print("\n| scene | condition | seeds | resets | worst overlap on the tray mm | ms/step | liquid ms/step | "
          "overhead | in the ideal zone (lt2 / 2to6 / gt6) |")
    print("|---|---|---|---|---|---|---|---|---|")
    groups = {}
    for (name, label, seed), r in res:
        groups.setdefault((name, label), []).append(r)
    dry_ms = {name: np.mean([1000 * r["wall_s"] / r["steps"] for r in rs])
              for (name, label), rs in groups.items() if label == "dry"}
    for (name, label), rs in groups.items():
        ms = np.mean([1000 * r["wall_s"] / r["steps"] for r in rs])
        lq = np.mean([r["liquid"]["ms_per_step"] for r in rs]) if rs[0].get("liquid") else 0.0
        rec = [np.mean([r["recovery"].get(k, 0) for r in rs]) for k in insects.MALAISE_MIX_STRATIFIED]
        print(f"| {name} | {label} | {len(rs)} | {sum(len(r['unstable_resets']) for r in rs)} | "
              f"{max(r['max_penetration_mm'] for r in rs):.3f} | {ms:.2f} | {lq:.2f} | "
              f"{100 * (ms / dry_ms[name] - 1):+.0f} % | " + " / ".join(f"{x:.2f}" for x in rec) + " |", flush=True)


def cmd_clump(seeds=(0, 1), workers=4):
    """A Malaise insect clump (40 specimens + leaf, twigs, dirt; medium bonds) on the seesaw: dry vs in ethanol."""
    import multiprocessing as mp

    import clumps
    jobs = []
    for label, lq in (("dry", None), ("ethanol, entrain 0.5", {"liquid": "ethanol", "entrain": 0.5}),
                      ("ethanol, entrain 0", {"liquid": "ethanol", "entrain": 0.0})):
        for seed in seeds:
            jobs.append(((label, seed), {**CLUMP, "liquid": lq, "seed": seed}))
    with mp.get_context("spawn").Pool(workers) as pool:
        res = pool.map(_run, jobs)
    print("\n| condition | seed | free at end | t50 s | t90 s | largest cluster | bonds broken | peak force p90 mN | "
          "resets | ms/step |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for (label, seed), r in res:
        c = r["clumps"]
        print(f"| {label} | {seed} | {c['free_frac']:.0%} | {c['t50_s']} | {c['t90_s']} | {c['largest_cluster']} | "
              f"{c['broken']}/{c['n_bonds']} | {c['damage']['p90_mN']:.2f} | {len(r['unstable_resets'])} | "
              f"{1000 * r['wall_s'] / r['steps']:.2f} |", flush=True)
        print("    " + clumps.summary(c).strip(), flush=True)


def cmd_sink(n=12, seed=0, t_end=3.0, dt=1e-4):
    """Generated Malaise specimens (n per class, one seed), each released alone in a still, unbounded bath, free to
    turn: the sinking speed over the last 0.5 s of t_end."""
    import sorter
    print("\n| liquid | class | length mm | sinking speed mm/s: min | median | max | 110 mm at the median takes |")
    print("|---|---|---|---|---|---|---|")
    for fluid in ("ethanol", "water"):
        for kind in ("insect_malaise_lt2", "insect_malaise_2to6", "insect_malaise_gt6"):
            rng = np.random.default_rng(seed)
            parts = [sorter.make_particle(kind, rng) for _ in range(n)]
            names = [f"p{i:03d}" for i in range(n)]
            body = "".join(f'<body name="{nm}" pos="{30 * i} 0 0"><freejoint/>{p.xml}</body>'
                           for i, (nm, p) in enumerate(zip(names, parts)))
            m = mujoco.MjModel.from_xml_string(f'<mujoco><option timestep="{dt}" gravity="0 0 {-G}" '
                                               f'integrator="implicitfast"/><worldbody>{body}</worldbody></mujoco>')
            d = mujoco.MjData(m)
            lq = liquid.Liquid({"liquid": fluid}).bind(m, d, parts, names)
            n_end, n_mark = int(t_end / dt), int((t_end - 0.5) / dt)
            for i in range(n_end):
                d.xfrc_applied[:] = 0.0
                lq.step(m, d, i)
                mujoco.mj_step(m, d)
                if i == n_mark:
                    z0 = d.xpos[1:, 2].copy()
            v = (z0 - d.xpos[1:, 2]) / (dt * (n_end - 1 - n_mark))
            L = [p.dims["length"] for p in parts]
            print(f"| {fluid} | {kind.removeprefix('insect_malaise_')} | {min(L):.2f}-{max(L):.2f} | {v.min():.1f} | "
                  f"{np.median(v):.1f} | {v.max():.1f} | {110 / np.median(v):.0f} s |", flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    nw = int(sys.argv[2]) if len(sys.argv) > 2 else None        # workers for cost / clump
    if what == "cost":
        cmd_cost(workers=nw or 6)
    if what == "clump":
        cmd_clump(workers=nw or 4)
    if what == "sink":
        cmd_sink()
    if what in ("stokes", "all"):
        cmd_stokes()
    if what in ("settle", "all"):
        cmd_settle()
    if what in ("freefall", "all"):
        cmd_freefall()
    if what in ("neutral", "all"):
        cmd_neutral()
    if what in ("frames", "all"):
        cmd_frames()
    if what in ("box", "all"):
        cmd_box()
