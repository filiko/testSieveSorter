"""Each box of a stacked tower moves on its own (sim/BOXES.md). Units mm, g, s.

Each holder box of an inserts: tower, the catch pan included, is its own body with three slide joints (X, Y, Z, in
the lab) and a hinge about Y through its pivot (x = y = 0, half way up the box, as in rocking.py). Before every step
all four joints' qpos and qvel are written from that level's own prescribed motion, in the lab frame with gravity
-Z, and a generalized force gives each joint its prescribed acceleration during the step (feed-forward), so the
contact solve sees the box accelerate rather than only a velocity jump at the next write. Nothing couples the
levels: each has its own tilt and its own vibration, and their phases are free.

    theta_k(t) = e(t) deg_k f_k(t / period_s_k + phase_k)        f: constant_speed (a triangle wave, reversals
                                                                 rounded over ramp_s) or sine; in [-1, 1]
    s_k(t)     = e(t) vib_mm_k sin(2 pi (vib_hz_k t + vib_phase_k)) u_k
    u_k        = (cos a cos b, cos a sin b, sin a),  a = vib_angle_deg_k (0 along X, 90 straight up), b = vib_az_deg_k
    e(t)       = 0 to 1 over ramp_in_s after the settle (a smoothstep), so a box that starts mid-cycle doesn't jump

t counts from the end of the settle; nothing moves during the settle. theta > 0 tips the +X end down. The hinge
turns about the pivot after the slides have moved it, so a level's geom at rest point x is at s + p + R(theta)(x - p).

The motion is KINEMATIC. No actuator, motor, spring or mount is modelled: each box follows its prescribed path
exactly, whatever the load. A level body weighs 1e6 g with its mass on the pivot and its gravity compensated
(gravcomp), so particles can't push it and it doesn't sag within a step. The vibration direction is fixed in the
lab, not in the tilted box (ASSUMED; at 12 deg of tilt a box-mounted shaker would point 12 deg off).

Stroke (sorter.py --stroke boxes:k=v,...). A per-level key takes one value for every level, or a slash list top to
bottom with the catch pan last (inserts:a,b has 3 levels: a, b, catch):
    deg            tilt amplitude either side of level, degrees (0: no tilt; the default)
    period_s       one tilt cycle, s (2)
    shape          constant_speed (default; constant angular speed, reversals rounded over ramp_s) or sine
    phase          where in its tilt cycle the level starts, fraction of a cycle (0: level and tipping +X down)
    ramp_s         reversal time of constant_speed, s (0.02)
    vib_mm         vibration amplitude, mm (0: off; the default). Peak acceleration vib_mm (2 pi vib_hz)^2
    vib_hz         vibration frequency, Hz (40)
    vib_angle_deg  vibration direction in the XZ plane: 0 along X (the tilt direction), 90 straight up (90)
    vib_az_deg     turns the vibration's horizontal part from X toward Y, degrees (0)
    vib_phase      where in its vibration cycle the level starts, fraction of a cycle (0)
  One value for the whole tower:
    ramp_in_s      ease every level in from rest over this long after the settle, s (0.2; 0 starts at full speed)
e.g. --stroke boxes:deg=8/6/0,period_s=2/1.5/1,phase=0/0.3/0,vib_mm=0.3/0.3/0,vib_hz=40/55/40

Clearance. Neighbouring boxes move independently, so over a long run every combination of their phases comes up.
clearance() poses each pair of neighbours at every combination of their tilts (a CLEAR_GRID x CLEAR_GRID grid from
-deg to +deg, ends included) and takes MuJoCo's closest distance between their frame, wall and floor geoms. The
vibrations then move the two boxes apart or together by at most vib_mm_k + vib_mm_k+1 (triangle inequality), and
that is subtracted. So min_mm is a lower bound on the gap over any phases. Tray-tray contacts are switched off
(the trays are driven), so a touching config doesn't show in the physics; it is flagged here instead.

Run from sim\\ to print the clearance and the pitch needed:
    <venv python> boxes.py inserts:h2p85b1p15_across,h1p45b1p15_across,pitch=55,holder=seesaw --stroke deg=10,vib_mm=0.3
"""
import argparse
import re

import mujoco
import numpy as np

import rocking

LEVEL_KEYS = {"deg": 0.0, "period_s": 2.0, "shape": "constant_speed", "phase": 0.0, "ramp_s": 0.02,
              "vib_mm": 0.0, "vib_hz": 40.0, "vib_angle_deg": 90.0, "vib_az_deg": 0.0, "vib_phase": 0.0}
GLOBAL_KEYS = {"ramp_in_s": 0.2}
SHAPES = ("constant_speed", "sine")
G = 9810.0                      # mm/s^2
LEVEL_MASS = rocking.LEVEL_MASS
LEVEL_INERTIA = rocking.LEVEL_INERTIA
SLIDES = (("x", "1 0 0"), ("y", "0 1 0"), ("z", "0 0 1"))
CLEAR_GRID = 9                  # tilts per level in the clearance check, -deg to +deg, ends included
CLEAR_ROLES = ("frame", "wall", "floor")   # the box itself; screens sit inside it, lids are invisible
CHUNK = 4096                    # steps of motion evaluated at once


# ---------------------------------------------------------------- parsing

def values(v):
    """One value, a slash list ("8/6/0") or a list -> a list."""
    if isinstance(v, (list, tuple)):
        return list(v)
    if isinstance(v, str) and "/" in v:
        return [x for x in v.split("/")]
    return [v]


def per_level(stroke, names):
    """The stroke's per-level keys -> one dict per level, top to bottom. names: the levels' zones (for messages)."""
    unknown = set(stroke) - set(LEVEL_KEYS) - set(GLOBAL_KEYS) - {"profile"}
    if unknown:
        raise ValueError(f"unknown boxes option(s) {sorted(unknown)}: use {sorted(LEVEL_KEYS)} per level, "
                         f"{sorted(GLOBAL_KEYS)} for the tower")
    n = len(names)
    out = [{} for _ in range(n)]
    for key, default in LEVEL_KEYS.items():
        vals = values(stroke.get(key, default))
        if len(vals) == 1:
            vals = vals * n
        if len(vals) != n:
            raise ValueError(f"boxes: {key} has {len(vals)} values, but this tower has {n} levels "
                             f"({' / '.join(names)}, top to bottom, catch pan last); give one value or {n}")
        for k, v in enumerate(vals):
            out[k][key] = str(v).strip() if key == "shape" else float(v)
    for k, L in enumerate(out):
        where = f"boxes level {k} ({names[k]})"
        if L["shape"] not in SHAPES:
            raise ValueError(f"{where}: shape {L['shape']!r}; use {' or '.join(SHAPES)}")
        if L["period_s"] <= 0:
            raise ValueError(f"{where}: period_s must be > 0")
        if L["vib_mm"] < 0 or L["ramp_s"] < 0:
            raise ValueError(f"{where}: vib_mm and ramp_s can't be negative (use vib_phase=0.5 to flip)")
        if L["vib_mm"] and L["vib_hz"] <= 0:
            raise ValueError(f"{where}: vib_hz must be > 0")
    return out


def tower_options(stroke):
    out = {}
    for k, v in GLOBAL_KEYS.items():
        out[k] = float(stroke.get(k, v))
    if out["ramp_in_s"] < 0:
        raise ValueError("boxes: ramp_in_s can't be negative")
    return out


# ---------------------------------------------------------------- the motion

def _tri(u):
    """Triangle wave in cycles: 0 at u = 0 rising to +1 at 1/4, -1 at 3/4."""
    u = np.mod(u, 1.0)
    return np.where(u < 0.25, 4 * u, np.where(u < 0.75, 2 - 4 * u, 4 * u - 4))


def _dtri(u):
    u = np.mod(u, 1.0)
    return np.where((u >= 0.25) & (u < 0.75), -4.0, 4.0)


def _tri_int(u):
    """Antiderivative of _tri over one cycle (periodic: _tri has zero mean), 0 at u = 0."""
    u = np.mod(u, 1.0)
    return np.where(u < 0.25, 2 * u * u, np.where(u < 0.75, 2 * u - 2 * u * u - 0.25, 2 * u * u - 4 * u + 2))


def triangle(u, r):
    """f, df/du and d2f/du2 of the constant-speed profile: the triangle wave box-filtered over r cycles (rounded
    reversals, as rocking.profile's smoothed square-wave speed), rescaled so the peak is exactly 1 (it is 1 - r
    before). r = 0: hard reversals (their impulses left out of d2f). r is capped at 1/4 cycle."""
    r = np.minimum(np.asarray(r, float), 0.25)
    soft = r > 0
    rs = np.where(soft, r, 1.0)
    f = np.where(soft, (_tri_int(u + rs / 2) - _tri_int(u - rs / 2)) / rs, _tri(u))
    df = np.where(soft, (_tri(u + rs / 2) - _tri(u - rs / 2)) / rs, _dtri(u))
    ddf = np.where(soft, (_dtri(u + rs / 2) - _dtri(u - rs / 2)) / rs, 0.0)
    peak = np.where(soft, 1.0 - rs, 1.0)
    return f / peak, df / peak, ddf / peak


def envelope(t, ramp_in_s):
    """Smoothstep from 0 to 1 over ramp_in_s, and its first and second time derivatives, at times t (s)."""
    t = np.asarray(t, float)
    if ramp_in_s <= 0:
        return np.ones_like(t), np.zeros_like(t), np.zeros_like(t)
    s = np.clip(t / ramp_in_s, 0.0, 1.0)
    inside = (s > 0) & (s < 1)
    return (s * s * (3 - 2 * s), np.where(inside, 6 * s * (1 - s) / ramp_in_s, 0.0),
            np.where(inside, 6 * (1 - 2 * s) / ramp_in_s ** 2, 0.0))


def unit(L):
    a, b = np.radians(L["vib_angle_deg"]), np.radians(L["vib_az_deg"])
    return np.array([np.cos(a) * np.cos(b), np.cos(a) * np.sin(b), np.sin(a)])


class Motion:
    """Every level's prescribed motion; motion(t) for t in s after the settle (a scalar or an array of times)."""

    def __init__(self, levels, ramp_in_s):
        col = lambda k: np.array([L[k] for L in levels], float)
        self.amp, self.T, self.phase, self.ramp = np.radians(col("deg")), col("period_s"), col("phase"), col("ramp_s")
        self.sine = np.array([L["shape"] == "sine" for L in levels])
        self.A, self.w, self.vphase = col("vib_mm"), 2 * np.pi * col("vib_hz"), col("vib_phase")
        self.U = np.array([unit(L) for L in levels])
        self.ramp_in_s = ramp_in_s

    def __call__(self, t):
        """The tilt and its first two time derivatives, (..., levels) in rad, rad/s, rad/s^2; then the vibration
        displacement and its two derivatives, (..., levels, 3) in mm, mm/s, mm/s^2; at time(s) t."""
        t = np.asarray(t, float)[..., None]
        e, de, dde = envelope(t, self.ramp_in_s)
        u = t / self.T + self.phase
        ft, dft, ddft = triangle(u, self.ramp / self.T)
        c, s = np.cos(2 * np.pi * u), np.sin(2 * np.pi * u)
        f = np.where(self.sine, s, ft)
        df = np.where(self.sine, 2 * np.pi * c, dft) / self.T
        ddf = np.where(self.sine, -(2 * np.pi) ** 2 * s, ddft) / self.T ** 2
        th = e * self.amp * f
        dth = self.amp * (de * f + e * df)
        ddth = self.amp * (dde * f + 2 * de * df + e * ddf)
        ph = self.w * t + 2 * np.pi * self.vphase
        x, dx, ddx = self.A * np.sin(ph), self.A * self.w * np.cos(ph), -self.A * self.w ** 2 * np.sin(ph)
        U = self.U
        return (th, dth, ddth, (e * x)[..., None] * U, (de * x + e * dx)[..., None] * U,
                (dde * x + 2 * de * dx + e * ddx)[..., None] * U)

    def joints(self, t):
        """qpos, qvel and qacc of every level's x, y, z slides and hinge at times t: each (len(t), levels * 4)."""
        th, dth, ddth, s, ds, dds = self(t)
        n = len(np.atleast_1d(t))
        return tuple(np.concatenate([lin, ang[..., None]], axis=-1).reshape(n, -1)
                     for lin, ang in ((s, th), (ds, dth), (dds, ddth)))


# ---------------------------------------------------------------- the tower

class Boxes(rocking.Seesaw):
    """One tower whose boxes each move on their own: builds the level bodies, drives their joints, reports per level.
    Reuses rocking.Seesaw's contact exclusions, orientations and zone frames."""
    result_key = "boxes"

    @classmethod
    def of(cls, cfg, design):
        """A Boxes for a RunConfig whose stroke profile is "boxes", else None."""
        if cfg.stroke.get("profile") != "boxes":
            return None
        return cls(cfg.stroke, design, cfg.dt, round(cfg.settle_s / cfg.dt), round(cfg.duration_s / cfg.dt))

    def __init__(self, stroke, design, dt, n_settle, n_shake):
        self.design = design
        self.levels, self.static = rocking.find_levels(design)
        self.n = len(self.levels)
        self.motion_cfg = per_level(stroke, [L["zone"] for L in self.levels])
        self.tower = tower_options(stroke)
        self.cfg = {**self.tower, "levels": self.motion_cfg}
        for L, mc in zip(self.levels, self.motion_cfg):
            L["sign"], L["amp_rad"] = 1, float(np.radians(mc["deg"]))
        self.motion = Motion(self.motion_cfg, self.tower["ramp_in_s"])
        self.dt, self.n_settle, self.n_shake = dt, n_settle, n_shake
        self.zone_level = {L["zone"]: k for k, L in enumerate(self.levels)}
        self.clear = None
        self._chunk = (0, *[np.zeros((0, 4 * self.n))] * 3)

    # ---------- model ----------
    def split_xml(self, assets, tray):
        """sorter.tray_xml's output -> (geoms that stay in the lab, one body per level with its four joints). Also
        checks the clearance between neighbouring levels."""
        geoms = rocking.tray_geoms(self.design, tray)
        self.clear = clearance(self.design, self.levels, self.motion_cfg, assets, geoms)
        return "".join(geoms[i] for i in self.static), "".join(level_body(L, geoms) for L in self.levels)

    def bind(self, m):
        """Joint addresses and body ids in a compiled model: per level x, y, z, hinge."""
        self.body = np.array([m.body(L["name"]).id for L in self.levels])
        jnt = np.array([[m.joint(f"{L['name']}_{a}").id for a, _ in SLIDES] + [m.joint(L["name"]).id]
                        for L in self.levels])
        self.qadr, self.dadr = m.jnt_qposadr[jnt].ravel(), m.jnt_dofadr[jnt].ravel()
        # Each level's mass matrix block is diagonal and constant (mass on the pivot, slides before the hinge), so
        # the force that gives a level its prescribed acceleration is that diagonal times the acceleration.
        d = mujoco.MjData(m)
        mujoco.mj_forward(m, d)
        M = np.zeros((m.nv, m.nv))
        try:
            mujoco.mj_fullM(m, d, M)                 # MuJoCo >= 3.3
        except TypeError:
            mujoco.mj_fullM(m, M, d.qM)
        blk = M[np.ix_(self.dadr, self.dadr)]
        if np.abs(blk - np.diag(np.diag(blk))).max() > 1e-6 * np.abs(blk).max():
            raise RuntimeError("boxes: a level's mass matrix isn't diagonal; the feed-forward force would be wrong")
        self.mdiag = np.diag(blk).copy()
        return self

    # ---------- every step ----------
    def drive(self, d, i):
        """Step i (counted from the start of the settle): write every level's slides and hinge qpos and qvel, and
        apply the generalized force that gives each joint its prescribed acceleration during the step, so the
        contact solve sees the boxes accelerate (as the seesaw's pseudo-force does for its shared buzz) instead of
        only a velocity jump at the next write. The motion is evaluated CHUNK steps at a time."""
        if i < self.n_settle:
            d.qpos[self.qadr] = 0.0
            d.qvel[self.dadr] = 0.0
            d.qfrc_applied[self.dadr] = 0.0
            return
        j = i - self.n_settle
        if not (self._chunk[0] <= j < self._chunk[0] + len(self._chunk[1])):
            self._chunk = (j, *self.motion.joints((j + np.arange(CHUNK)) * self.dt))
        k = j - self._chunk[0]
        d.qpos[self.qadr] = self._chunk[1][k]
        d.qvel[self.dadr] = self._chunk[2][k]
        d.qfrc_applied[self.dadr] = self.mdiag * self._chunk[3][k]

    def vib_axis(self):
        """sorter.py's stroke axis: unused, since nothing is shared (vibration() is zero)."""
        return np.array([0.0, 0.0, 1.0])

    def vibration(self, n_shake, dt):
        """No shared translation: every level vibrates through its own slides. Zero pseudo-force."""
        z = np.zeros(n_shake)
        return z, z.copy(), z.copy()

    def positions(self, d):
        """Each level body's origin in the lab, levels x 3 (mm). A rest-frame point x of level k is drawn at
        positions[k] + R(quats[k]) x."""
        return d.xpos[self.body].astype(np.float32)

    def widen(self, bounds):
        """sorter's lost-particle bounds, grown to cover every level's box geoms at full tilt both ways and full
        vibration."""
        lo, hi = (np.array(b, dtype=float) for b in bounds)
        for L, mc in zip(self.levels, self.motion_cfg):
            p = np.array(L["pivot"])
            th = abs(L["amp_rad"])
            pad = 5.0 + mc["vib_mm"]
            for i in L["geoms"]:
                g = self.design.geoms[i]
                if g["type"] != "box":
                    continue
                c = np.array(g["pos"]) + np.array(np.meshgrid(*[(-s, s) for s in g["size"]])).reshape(3, -1).T
                for a in (th, -th):
                    r = (c - p) @ rocking.rot_y(a).T + p
                    lo, hi = np.minimum(lo, r.min(axis=0) - pad), np.maximum(hi, r.max(axis=0) + pad)
        return lo, hi

    # ---------- reporting ----------
    def scene_levels(self, m):
        """rocking's scene["levels"] plus each level's motion (the viewer reads level_q and level_p)."""
        out = super().scene_levels(m)
        for lv, mc in zip(out, self.motion_cfg):
            lv["motion"] = mc
            lv.pop("sign", None)
        return out

    def summary(self):
        return {"profile": "boxes", **self.tower,
                "levels": [{"zone": L["zone"], "pivot": L["pivot"], **mc,
                            "vib_peak_g": round(mc["vib_mm"] * (2 * np.pi * mc["vib_hz"]) ** 2 / G, 3)}
                           for L, mc in zip(self.levels, self.motion_cfg)],
                "pitch_mm": self.design.info.get("pitch_mm"), "clearance": self.clear}


def level_body(L, geoms):
    p = " ".join(f"{c:.4f}" for c in L["pivot"])
    n = L["name"]
    return (f'<body name="{n}" pos="0 0 0" gravcomp="1">'
            + "".join(f'<joint name="{n}_{a}" type="slide" axis="{ax}" armature="{LEVEL_MASS:g}"/>' for a, ax in SLIDES)
            + f'<joint name="{n}" type="hinge" pos="{p}" axis="0 1 0" armature="{LEVEL_INERTIA:g}"/>'
            f'<inertial pos="{p}" mass="{LEVEL_MASS:g}" diaginertia="{LEVEL_INERTIA:g} {LEVEL_INERTIA:g} {LEVEL_INERTIA:g}"/>'
            + "".join(geoms[i] for i in L["geoms"]) + "</body>")


# ---------------------------------------------------------------- clearance

def clearance(design, levels, motion, assets, geoms, grid=CLEAR_GRID, distmax=60.0):
    """Lower bound on the gap between neighbouring levels over every combination of their phases, mm (negative:
    the boxes overlap). Each pair is posed at grid x grid tilt combinations (ends included); the vibration
    amplitudes are then subtracted. Only the box geoms count (CLEAR_ROLES). assets, geoms: sorter.tray_xml's
    meshes and its geoms split by rocking.tray_geoms()."""
    sub = [{"name": L["name"], "pivot": L["pivot"],
            "geoms": [i for i in L["geoms"] if design.geoms[i]["role"] in CLEAR_ROLES]} for L in levels]
    keep = {i for L in sub for i in L["geoms"]}
    meshes = "".join(s for s in re.findall(r"<mesh [^>]*/>", assets)        # only the meshes of the kept geoms
                     if int(re.search(r'name="tray(\d+)"', s).group(1)) in keep)
    m = mujoco.MjModel.from_xml_string(f'<mujoco><asset>{meshes}</asset><worldbody>'
                                       f'{"".join(rocking.level_body(L, geoms) for L in sub)}</worldbody></mujoco>')
    d = mujoco.MjData(m)
    qadr = [m.jnt_qposadr[m.joint(L["name"]).id] for L in sub]
    ids = [np.array([m.geom(f"tray{i}").id for i in L["geoms"]], dtype=int) for L in sub]
    out = []
    for k in range(len(sub) - 1):
        a, b = ids[k], ids[k + 1]
        tilts = [np.linspace(-1, 1, grid) * abs(np.radians(motion[j]["deg"])) if motion[j]["deg"] else np.zeros(1)
                 for j in (k, k + 1)]
        best = (np.inf, None, None)
        for t0 in tilts[0]:
            for t1 in tilts[1]:
                d.qpos[:] = 0.0
                d.qpos[qadr[k]], d.qpos[qadr[k + 1]] = t0, t1
                mujoco.mj_kinematics(m, d)
                gap = (np.linalg.norm(d.geom_xpos[a][:, None] - d.geom_xpos[b][None], axis=2)
                       - m.geom_rbound[a][:, None] - m.geom_rbound[b][None])
                for i, j in zip(*np.nonzero(gap < distmax)):
                    dist = mujoco.mj_geomDistance(m, d, int(a[i]), int(b[j]), distmax, None)
                    if dist < best[0]:
                        best = (dist, (round(float(np.degrees(t0)), 3), round(float(np.degrees(t1)), 3)),
                                (int(a[i]), int(b[j])))
        vib = motion[k]["vib_mm"] + motion[k + 1]["vib_mm"]
        tilt = round(float(best[0]), 2) if np.isfinite(best[0]) else None
        roles = [design.geoms[int(m.geom(g).name[4:])]["role"] for g in best[2]] if best[2] else None
        out.append({"upper": levels[k]["zone"], "lower": levels[k + 1]["zone"], "tilt_mm": tilt,
                    "vib_mm": round(vib, 3), "min_mm": None if tilt is None else round(tilt - vib, 2),
                    "at_deg": best[1], "roles": roles})
    worst = min((c["min_mm"] for c in out if c["min_mm"] is not None), default=None)
    return {"method": f"every tilt combination on a {grid} x {grid} grid (ends included), minus both vibration "
                      "amplitudes", "pairs": out, "min_mm": worst, "touching": worst is not None and worst <= 0.0}


def design_clearance(design, stroke, grid=CLEAR_GRID):
    """clearance() for a design and a boxes stroke, outside a run."""
    import sorter
    levels = rocking.find_levels(design)[0]
    assets, tray = sorter.tray_xml(design)
    return clearance(design, levels, per_level(stroke, [L["zone"] for L in levels]), assets,
                     rocking.tray_geoms(design, tray), grid)


def pitch_needed(spec, stroke, clear_mm=0.0, lo=None, hi=300.0, tol=0.25):
    """Smallest pitch (box bottom to box bottom, mm) at which neighbouring boxes stay clear_mm apart under this
    motion, whatever their phases."""
    import designs

    def gap(p):
        g = design_clearance(designs.build(rocking.with_pitch(spec, p)), stroke)["min_mm"]
        return np.inf if g is None else g

    if lo is None:
        z0, z1 = designs.build(rocking.with_pitch(spec, 1000.0)).info["layers"][0]["holder_z_mm"]
        lo = z1 - z0 + 0.5
    if gap(hi) < clear_mm:
        raise ValueError(f"even {hi:g} mm doesn't clear {clear_mm:g} mm")
    while hi - lo > tol:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if gap(mid) < clear_mm else (lo, mid)
    return round(hi, 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("design", nargs="?", default="inserts:h2p85b1p15_across,h1p45b1p15_across,pitch=55,holder=seesaw")
    ap.add_argument("--stroke", default="deg=10,vib_mm=0.3", help="boxes keys, as after boxes: on the sorter.py line")
    ap.add_argument("--clear", type=float, default=3.0, help="clearance to find the pitch for, mm")
    ap.add_argument("--grid", type=int, default=CLEAR_GRID, help="tilts per level")
    args = ap.parse_args()
    import designs
    import sorter
    stroke = sorter.parse_kv(args.stroke)
    dsg = designs.build(args.design)
    c = design_clearance(dsg, stroke, args.grid)
    print(f"{dsg.name}, boxes:{args.stroke}: closest {c['min_mm']} mm over every phase combination"
          + ("  TOUCHING" if c["touching"] else ""))
    for p in c["pairs"]:
        print(f"    {p['upper']} over {p['lower']}: {p['min_mm']} mm (tilts alone {p['tilt_mm']} mm at "
              f"{p['at_deg']} deg, less {p['vib_mm']} mm of vibration; {p['roles']})")
    print(f"    pitch for {args.clear:g} mm clear: {pitch_needed(args.design, stroke, args.clear)} mm; "
          f"touching below {pitch_needed(args.design, stroke, 0.0)} mm")


if __name__ == "__main__":
    main()
