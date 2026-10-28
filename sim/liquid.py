"""Liquid bath for the sorter sim: buoyancy, drag, added mass and wetting on every particle body. Units mm, g, s.

Malaise specimens sit in ethanol and BugSorter sorts wet. In liquid a specimen of 1.05 g/cm^3 weighs 5 % (water) or
23 % (ethanol) of its dry weight (INSECT_AUDIT.md 2.4), so drag and inertia of the liquid, not friction, decide how it
moves. This module adds that
to sorter.py. Validation and limits: LIQUID.md. Run `python liquid.py` for the per-element summary of one specimen.

The bath (RunConfig.liquid, CLI --liquid ethanol:level_mm=...,entrain=...):
    liquid      water | ethanol (96 % v/v)                           LIQUIDS below, sources in LIQUID.md
    level_mm    the free surface, a horizontal plane fixed in the LAB (design frame at rest). Omitted or "full":
                everything is submerged. In a tray-frame run the lab moves by -tray_d relative to the trays, so
                in sim coordinates the surface sits at level_mm - tray_d_z(t).
    entrain     0..1. Inside a box (a holder box, the catch pan, a sieve container) the liquid moves with that
                box by this fraction: lab velocity of the liquid = entrain * (velocity of the box material point).
                0 = a still bath, 1 = the liquid moves rigidly with the box. Outside every box the bath is still.
                Real liquid in a shaken perforated box is somewhere in between: treat it as UNCERTAIN (LIQUID.md).
    rho, mu     override the liquid's density (g/mm^3) and viscosity (g/(mm s))
    added_mass  1: added mass on (default), 0: off          munk     scale of the Munk moment (1 = potential flow)
    drag_scale  multiplies every drag coefficient           adhesion_scale, dry_tau_s: see Wetness below
    screen_flow 0 (default) or 1: EXPLORATORY flow through round-hole screens (ScreenFlow below, unvalidated)

Each particle body is split into ELEMENTS, each an ellipsoid: the body's bulk geoms (head, thorax, abdomen; a grain;
a dirt ball) merged into one CORE ellipsoid, plus every slender geom (legs, antennae: capsules, as prolate spheroids
of the same length and volume) and every thin geom (wings, a leaf) on its own. Merging the bulk segments avoids
double-counting drag on touching segments (two touching spheres in Stokes flow have 1.3-1.4 x, not 2 x, one sphere's
drag); appendages are spread out and get their own drag, so a long-legged specimen is not modelled as a bare body.
Per element and step, with w its velocity relative to the local liquid and s its submerged fraction:
  - submerged fraction: exact for an ellipsoid cut by a horizontal plane (an affine image of a sphere cap):
    s = (1 + delta)^2 (2 - delta) / 4, delta = (z_surface - z_centre) / (vertical half extent). Buoyancy acts at the
    cap's centroid, so a body floating through the surface gets a righting moment.
  - buoyancy and pressure gradient (Froude-Krylov): F = rho V_b s (a_liquid - g), V_b the element's REAL volume.
    Thin parts are thickened for contact stability (legs to r >= 0.06 mm, wings to 80 um) with their density lowered
    to keep their mass (insects.py); their real volume is mass / tissue density, so a wing does not float the fly.
  - drag: F = -s K w, K = R diag(k_i) R^T in the element's principal axes. k_i = mu G_i f_i(Re): G_i is the exact
    Stokes resistance of the ellipsoid along axis i (Oberbeck 1876, Carlson integrals), so tilted bodies glide as
    they should; f_i(Re) is the inertial correction: Schiller & Naumann's sphere factor 1 + 0.15 Re^0.687, times the
    shape effect of Hoelzer & Sommerfeld (2008) for that orientation (their C_D over its Stokes terms, divided by the
    same ratio for a sphere). Re = rho |w| d_v / mu, d_v the volume-equivalent diameter. A sphere follows
    Schiller-Naumann exactly; a thin disc moving face-on keeps H-S's projected-area drag.
  - rotational drag: exact Stokes torque of the ellipsoid on its spin relative to the liquid's (Jeffery 1922).
    Off-centre elements' drag adds most of a multi-element body's rotational damping.
  - added mass: the potential-flow added mass and moment of inertia of each ellipsoid (Tuckerman 1925, the
    coefficients MuJoCo's own ellipsoid model uses), summed over the body's elements (parallel axis for the
    rotation), go into the inertia of the body's free joint (dof_armature, or dof_M0 for MuJoCo's "simple" bodies):
    translation along the world axes (the diagonal of the rotated tensor), rotation about the body axes. So the
    solver integrates the added mass implicitly, as part
    of the body's inertia, including in contacts. The liquid's own acceleration enters as the force
    Arm (a_liquid - a_frame). MuJoCo's built-in fluid model omits the acceleration term (it calls
    mj_addedMassForces with no accelerations), which is why it is not used here.
  - Munk moment: (M_a w) x w, the potential-flow torque that turns a body broadside to its relative velocity.
  - stiffness: the diagonal of each body's drag matrix about its origin goes into dof_damping, which the implicitfast
    integrator treats implicitly, and the same amount is added back explicitly. Net force: the full drag at this
    step's velocity, stable for the smallest specimens whose drag time constant nears the time step.

Frames. sorter.py's tray-frame runs move the trays by tray_d(t) along the stroke and apply gravity minus the tray
acceleration A to every body. With M_a the added mass, the body's equation in the tray frame becomes
    (m + M_a) a_sim = m (g - A) + M_a (a_L - A) + rho V (a_L - g) + drag + contact,
with a_L the liquid's LAB acceleration: entrain * (A + box acceleration) inside a box, 0 outside. MuJoCo supplies the
first term (opt.gravity) and the M_a a_sim term (armature); this module adds the rest. Checks: with entrain 1
the extra terms reduce to -rho V (g - A), MuJoCo's gravcomp, and a neutral body rides along with the box; with
entrain 0 a neutral body stays still in the lab while the box moves around it. Seesaw runs (rocking.py) are in the
lab frame plus the buzz, a translation applied the same way; their levels are hinged bodies, and the liquid inside
level k turns with that level by entrain.

Wetness. A body's liquid wetness is max(previous * exp(-dt / dry_tau_s), submerged fraction): it is fully wet once
submerged, and dries slowly once out. With --spray the larger of the two wetnesses counts. clumps.py reads it to
weaken bonds. Capillary adhesion (spray.py's geom_adhesion model: adhesion_scale * 2 pi gamma R_eff w per contact)
acts only on the part of a body that is out of the liquid: under liquid there is no meniscus.
Left out (LIQUID.md): any flow solver (no sloshing, no jets through holes, no wakes, no particle-particle
hydrodynamics), history (Basset) forces, lift, and surface tension at the free surface.
"""
import re
import time

import mujoco
import numpy as np
from scipy.special import elliprd, elliprf

G = 9810.0                      # mm/s^2
GRAV = np.array([0.0, 0.0, -G])
# g/mm^3, g/(mm s) (1e-3 = 1 mPa s), g/s^2 (= mN/m), at 20 C. Sources and the ethanol viscosity estimate: LIQUID.md
LIQUIDS = {
    "water": {"rho": 0.998e-3, "mu": 1.002e-3, "gamma": 72.8},
    "ethanol": {"rho": 0.807e-3, "mu": 1.4e-3, "gamma": 22.4},     # 96 % v/v (93.8 % w/w); mu ASSUMED, see LIQUID.md
}
DEFAULTS = {"liquid": "ethanol", "level_mm": None, "entrain": 0.0, "rho": None, "mu": None, "added_mass": 1.0,
            "munk": 1.0, "drag_scale": 1.0, "adhesion_scale": 0.1, "dry_tau_s": 30.0, "implicit": 1, "screen_flow": 0}
THIN = 0.35         # an ellipsoid or box whose smallest semi-axis is under THIN x its middle one is a thin part
BOX_TO_ELL = (6 / np.pi) ** (1 / 3)     # a box as the ellipsoid of the same volume and proportions
_I1, _I2 = [1, 2, 0], [2, 0, 1]


def parse(s):
    """'ethanol:level_mm=200,entrain=0.5' -> RunConfig.liquid dict ('water' alone: fully immersed, still)."""
    import sorter
    name, _, rest = s.partition(":")
    kv = sorter.parse_kv(rest)
    if name and "=" in name:            # 'level_mm=..' with no liquid name
        kv, name = sorter.parse_kv(s), DEFAULTS["liquid"]
    spec = {"liquid": name or DEFAULTS["liquid"], **kv}
    check(spec)
    return spec


def check(spec):
    unknown = set(spec) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"unknown liquid option(s) {sorted(unknown)}: use {sorted(DEFAULTS)}")
    if spec.get("liquid", DEFAULTS["liquid"]) not in LIQUIDS:
        raise ValueError(f"liquid {spec['liquid']!r}: use one of {list(LIQUIDS)}")
    e = spec.get("entrain", 0.0)
    if not 0.0 <= float(e) <= 1.0:
        raise ValueError(f"entrain {e}: use a value in [0, 1]")


def _cross(a, b):
    return a[..., _I1] * b[..., _I2] - a[..., _I2] * b[..., _I1]


def quat2mat(q):
    """(n, 4) wxyz -> (n, 3, 3)."""
    w, x, y, z = q[:, 0], q[:, 1], q[:, 2], q[:, 3]
    n = 1.0 / (w * w + x * x + y * y + z * z)
    R = np.empty((len(q), 3, 3))
    R[:, 0, 0] = 1 - 2 * n * (y * y + z * z)
    R[:, 0, 1] = 2 * n * (x * y - w * z)
    R[:, 0, 2] = 2 * n * (x * z + w * y)
    R[:, 1, 0] = 2 * n * (x * y + w * z)
    R[:, 1, 1] = 1 - 2 * n * (x * x + z * z)
    R[:, 1, 2] = 2 * n * (y * z - w * x)
    R[:, 2, 0] = 2 * n * (x * z - w * y)
    R[:, 2, 1] = 2 * n * (y * z + w * x)
    R[:, 2, 2] = 1 - 2 * n * (x * x + y * y)
    return R


# ---------- ellipsoid hydrodynamics (per unit viscosity / density) ----------
def ellipsoid_coeffs(a):
    """For semi-axes a (n, 3): Stokes translational resistance G (F_i = mu G_i U_i), rotational resistance Gr
    (T_i = mu Gr_i Omega_i), and Tuckerman's added-mass coefficients kappa (n, 3).
    chi = int dl / D = 2 R_F(a1^2, a2^2, a3^2); alpha_i = int dl / ((a_i^2 + l) D) = 2/3 R_D(a_j^2, a_k^2, a_i^2),
    D = sqrt(prod(a^2 + l)). G_i = 16 pi / (chi + alpha_i a_i^2) (Oberbeck 1876),
    Gr_i = 16 pi (a_j^2 + a_k^2) / (3 (a_j^2 alpha_j + a_k^2 alpha_k)) (Jeffery 1922), kappa_i = a1 a2 a3 alpha_i."""
    a = np.asarray(a, float).reshape(-1, 3)
    s = a * a
    chi = 2.0 * elliprf(s[:, 0], s[:, 1], s[:, 2])
    alpha = np.stack([2.0 / 3.0 * elliprd(s[:, _I1[i]], s[:, _I2[i]], s[:, i]) for i in range(3)], axis=1)
    G = 16 * np.pi / (chi[:, None] + alpha * s)
    Gr = np.stack([16 * np.pi * (s[:, _I1[i]] + s[:, _I2[i]])
                   / (3 * (s[:, _I1[i]] * alpha[:, _I1[i]] + s[:, _I2[i]] * alpha[:, _I2[i]])) for i in range(3)], axis=1)
    kappa = a.prod(axis=1)[:, None] * alpha
    return G, Gr, kappa


def added_mass(a, kappa):
    """Added mass per unit liquid density, along each axis (mm^3), and added moment of inertia (mm^5), for
    ellipsoids a (n, 3) (Tuckerman 1925, as in MuJoCo's fluid docs)."""
    V = 4 / 3 * np.pi * a.prod(axis=1)
    mA = V[:, None] * kappa / (2 - kappa)
    IA = np.zeros_like(a)
    s = a * a
    for i in range(3):
        j, k = _I1[i], _I2[i]
        num = (s[:, j] - s[:, k]) ** 2 * (kappa[:, k] - kappa[:, j])
        den = 2 * (s[:, j] - s[:, k]) + (s[:, j] + s[:, k]) * (kappa[:, j] - kappa[:, k])
        ok = np.abs(den) > 1e-12 * (s[:, j] + s[:, k])
        IA[ok, i] = V[ok] / 5 * num[ok] / den[ok]
    return mA, np.maximum(IA, 0.0)


def ellipsoid_area(a):
    """Surface area (Knud Thomsen's formula, within about 1 %)."""
    p = 1.6075
    ap = a ** p
    return 4 * np.pi * ((ap[:, 0] * ap[:, 1] + ap[:, 0] * ap[:, 2] + ap[:, 1] * ap[:, 2]) / 3) ** (1 / p)


def hs_coeffs(a):
    """Hoelzer & Sommerfeld (2008) inertial correction per principal axis: f_i(Re) = 1 + c1_i Re^0.5 + c2_i Re,
    the ratio of their C_D = 8/(Re sqrt(phi_perp)) + 16/(Re sqrt(phi)) + 3/(sqrt(Re) phi^0.75)
    + 0.42 10^(0.4 (-log phi)^0.2) / phi_perp to its two Stokes terms (lengthwise sphericity taken as phi_perp, as
    they suggest). phi: sphericity, phi_perp,i: crosswise sphericity for flow along axis i. Also d_v."""
    V = 4 / 3 * np.pi * a.prod(axis=1)
    dv = (6 * V / np.pi) ** (1 / 3)
    phi = np.minimum(np.pi * dv ** 2 / ellipsoid_area(a), 1.0)
    proj = np.pi * np.stack([a[:, 1] * a[:, 2], a[:, 0] * a[:, 2], a[:, 0] * a[:, 1]], axis=1)
    pp = np.pi * dv[:, None] ** 2 / 4 / proj
    S = 8 / np.sqrt(pp) + 16 / np.sqrt(phi)[:, None]
    c1 = (3 / phi ** 0.75)[:, None] / S
    c2 = 0.42 * 10 ** (0.4 * (-np.log10(phi)) ** 0.2)[:, None] / pp / S
    return dv, phi, c1, c2


def cap_fraction(delta):
    """Volume fraction of a unit ball below the plane z = delta, and that part's centroid height."""
    d = np.clip(delta, -1.0, 1.0)
    f = (1 + d) ** 2 * (2 - d) / 4
    zbar = np.where(f > 1e-12, -3 * (1 - d * d) ** 2 / (4 * np.maximum((1 + d) ** 2 * (2 - d), 1e-12)), -1.0)
    return f, zbar


# ---------- geometry of the particle bodies ----------
_GT = {k: int(getattr(mujoco.mjtGeom, f"mjGEOM_{k}")) for k in ("SPHERE", "CAPSULE", "CYLINDER", "ELLIPSOID", "BOX")}


class _T:            # geom type ids as plain ints (pybind enums don't compare equal to numpy ints inside `in`)
    mjGEOM_SPHERE, mjGEOM_CAPSULE, mjGEOM_CYLINDER = _GT["SPHERE"], _GT["CAPSULE"], _GT["CYLINDER"]
    mjGEOM_ELLIPSOID, mjGEOM_BOX = _GT["ELLIPSOID"], _GT["BOX"]


def geom_volume(gtype, size):
    T, gtype = _T, int(gtype)
    r, h = size[0], size[1]
    if gtype == T.mjGEOM_SPHERE:
        return 4 / 3 * np.pi * r ** 3
    if gtype == T.mjGEOM_CAPSULE:
        return np.pi * r * r * 2 * h + 4 / 3 * np.pi * r ** 3
    if gtype == T.mjGEOM_CYLINDER:
        return np.pi * r * r * 2 * h
    if gtype == T.mjGEOM_ELLIPSOID:
        return 4 / 3 * np.pi * size[0] * size[1] * size[2]
    if gtype == T.mjGEOM_BOX:
        return 8 * size[0] * size[1] * size[2]
    raise ValueError(f"liquid: particle geom type {gtype} not supported")


def geom_ellipsoid(gtype, size):
    """Semi-axes (in the geom's frame) of the ellipsoid that stands in for a geom, and its kind."""
    T, gtype = _T, int(gtype)
    if gtype == T.mjGEOM_SPHERE:
        return np.full(3, size[0]), "bulk"
    if gtype in (T.mjGEOM_CAPSULE, T.mjGEOM_CYLINDER):
        c = size[1] + (size[0] if gtype == T.mjGEOM_CAPSULE else 0.0)      # same length
        a = np.sqrt(3 * geom_volume(gtype, size) / (4 * np.pi * c))          # same volume
        return np.array([a, a, c]), "slender"
    s = np.array(size[:3], float) * (BOX_TO_ELL if gtype == T.mjGEOM_BOX else 1.0)
    srt = np.sort(s)
    return s, ("thin" if srt[0] < THIN * srt[1] else "bulk")


def xml_densities(xml):
    """Density of every <geom> in a particle's XML, in order (None where unset)."""
    out = []
    for tag in re.findall(r"<geom\b[^>]*>", xml):
        mm = re.search(r'density="([^"]+)"', tag)
        out.append(float(mm.group(1)) if mm else None)
    return out


def merge_core(parts):
    """One ellipsoid for a body's bulk geoms [(centre, R, semi-axes, volume)]: principal axes of their combined second
    moment, semi-axes from their extents along those axes. Returns centre, R (columns = axes), semi-axes."""
    V = np.array([p[3] for p in parts])
    c = np.array([p[0] for p in parts])
    cbar = (V[:, None] * c).sum(0) / V.sum()
    S = np.zeros((3, 3))
    for (ci, Ri, ai, Vi) in parts:
        S += Ri @ np.diag(Vi * ai * ai / 5) @ Ri.T + Vi * np.outer(ci - cbar, ci - cbar)
    _, U = np.linalg.eigh(S)
    U = U[:, ::-1]
    if np.linalg.det(U) < 0:
        U[:, 2] *= -1
    centre, semi = cbar.copy(), np.zeros(3)
    for i in range(3):
        u = U[:, i]
        hi = max((ci - cbar) @ u + np.linalg.norm(ai * (Ri.T @ u)) for ci, Ri, ai, _ in parts)
        lo = max(-(ci - cbar) @ u + np.linalg.norm(ai * (Ri.T @ u)) for ci, Ri, ai, _ in parts)
        semi[i] = (hi + lo) / 2
        centre += (hi - lo) / 2 * u
    return centre, U, semi


def boxes_for(design, rock=None):
    """The boxes whose liquid is entrained: [{"body": level body id or 0 (the sim frame), "lo": xyz, "hi": xyz}],
    each in its body's frame. Holder towers: the inside of every holder box and of the catch pan, one per level body
    in a seesaw run. Other designs: design.info["liquid_boxes"] if given, else the design's whole extent."""
    info = design.info
    zones = {z["name"]: z["box"] for z in design.zones}
    layers = info.get("layers", [])
    if layers and all("holder_z_mm" in L for L in layers) and "catch_z_mm" in info:
        H = layers[0]["holder_z_mm"][1] - layers[0]["holder_z_mm"][0]
        boxes = {}
        for L in layers:
            x0, x1, y0, y1 = zones[L["zone"]][:4]
            boxes[L["zone"]] = ([x0, y0, L["holder_z_mm"][0]], [x1, y1, L["holder_z_mm"][1]])
        x0, x1, y0, y1 = zones["catch"][:4]
        boxes["catch"] = ([x0, y0, info["catch_z_mm"][0]], [x1, y1, H])
        if rock is not None and getattr(rock, "body", None) is not None:
            out = []
            for L, b in zip(rock.levels, rock.body):
                lo, hi = boxes[L["zone"]]
                out.append({"body": int(b), "lo": np.array(lo, float), "hi": np.array(hi, float)})
            return out
        return [{"body": 0, "lo": np.array(lo, float), "hi": np.array(hi, float)} for lo, hi in boxes.values()]
    if "liquid_boxes" in info:
        return [{"body": 0, "lo": np.array(b[0::2], float), "hi": np.array(b[1::2], float)} for b in info["liquid_boxes"]]
    pts = []
    for g in design.geoms:
        if g["role"] == "lid":
            continue
        if g["type"] == "mesh":
            pts += list(g["vertices"])
        else:
            r = max(g["size"]) if g["type"] in ("capsule", "cylinder", "sphere") else None
            half = np.full(3, r) if r is not None else np.array(g["size"][:3])
            pts += [np.array(g["pos"]) - half, np.array(g["pos"]) + half]
    pts = np.array(pts, float)
    return [{"body": 0, "lo": pts.min(0), "hi": pts.max(0)}]


class Liquid:
    """One run's bath: build with Liquid(spec, boxes), then bind() to the compiled model, then step() before every
    mj_step (after the caller has zeroed xfrc_applied)."""

    @classmethod
    def of(cls, cfg, design, rock=None):
        """A Liquid for a RunConfig with cfg.liquid set, else None."""
        spec = getattr(cfg, "liquid", None)
        if not spec:
            return None
        lq = cls(parse(spec) if isinstance(spec, str) else dict(spec), boxes_for(design, rock))
        if lq.spec["screen_flow"]:
            lq.flow = ScreenFlow(design, rock, float(lq.spec["screen_flow"]))
        return lq

    def __init__(self, spec, boxes=()):
        check(spec)
        self.spec = {**DEFAULTS, **spec}
        p = self.spec
        lq = LIQUIDS[p["liquid"]]
        self.rho = float(p["rho"] if p["rho"] is not None else lq["rho"])
        self.mu = float(p["mu"] if p["mu"] is not None else lq["mu"])
        self.gamma = lq["gamma"]
        lev = p["level_mm"]
        self.level = np.inf if lev in (None, "full", "none", "") else float(lev)
        self.e = float(p["entrain"])
        self.boxes = list(boxes)
        self.wall = 0.0
        self.n_steps = 0
        self.s_sum = 0.0
        self.flow = None                 # ScreenFlow, exploratory (screen_flow=1)

    # ---------- setup ----------
    def bind(self, m, d, particles, names, sp=None):
        """particles: the run's common.Particle list; names: their root body names (sorter.run's p000, ...)."""
        T = mujoco.mjtJoint
        self.sp = sp
        self.dt = m.opt.timestep
        roots = np.array([m.body(n).id for n in names])
        pb = np.flatnonzero(np.isin(m.body_rootid, roots) & (np.arange(m.nbody) > 0))
        if len(pb) != len(roots):
            raise NotImplementedError("liquid: particles with child bodies are not supported (single rigid bodies only)")
        jnt = m.body_jntadr[roots]
        if np.any(m.body_jntnum[roots] != 1) or np.any(m.jnt_type[jnt] != T.mjJNT_FREE):
            raise NotImplementedError("liquid: every particle needs exactly one free joint")
        self.roots, self.nb = roots, len(roots)
        self.qadr, self.dadr = m.jnt_qposadr[jnt], m.jnt_dofadr[jnt]
        self.dofs = (self.dadr[:, None] + np.arange(6)).ravel()
        self.ipos = m.body_ipos[roots].copy()
        self.mass = m.body_mass[roots].copy()
        # MuJoCo 3.17 builds the inertia of a "simple" body (centre of mass at its origin, principal axes along its
        # own) from the constant dof_M0, which includes the armature at compile time; other bodies read dof_armature
        # every step. So the added mass is written to whichever of the two the solver reads.
        self.arm0 = m.dof_armature[self.dofs].copy()
        self.M00 = m.dof_M0[self.dofs].copy()
        self.simple = m.dof_simplenum[self.dofs] > 0
        self.damp0 = m.dof_damping[self.dofs].copy()

        E = {k: [] for k in ("body", "c", "R", "a", "Vb", "cb", "geoms")}
        geoms_all, geom_elem = [], []
        self.rho_body = np.zeros(self.nb)
        for j, (b, part) in enumerate(zip(roots, particles)):
            gl = np.flatnonzero(m.geom_bodyid == b)
            dens = xml_densities(part.xml)
            if len(dens) != len(gl) or any(x is None for x in dens):
                dens = [None] * len(gl)
            vols = np.array([geom_volume(m.geom_type[g], m.geom_size[g]) for g in gl])
            if dens[0] is None:                          # uniform: every geom at the body's mean density
                dens = [m.body_mass[b] / vols.sum()] * len(gl)
            dens = np.array(dens)
            if abs((dens * vols).sum() - m.body_mass[b]) > 1e-3 * m.body_mass[b]:
                raise RuntimeError(f"liquid: geom masses of {names[j]} don't add up to the body mass")
            rho_ref = dens.max()
            self.rho_body[j] = rho_ref
            vb = vols * dens / rho_ref                   # real volume: a thickened thin part keeps its true volume
            info = []
            for g, v, vbg in zip(gl, vols, vb):
                a, kind = geom_ellipsoid(m.geom_type[g], m.geom_size[g])
                Rg = np.zeros(9)
                mujoco.mju_quat2Mat(Rg, m.geom_quat[g])
                info.append((g, m.geom_pos[g].copy(), Rg.reshape(3, 3), a, kind, v, vbg))
            bulk = [x for x in info if x[4] == "bulk"] if len(info) > 1 else info
            rest = [x for x in info if x not in bulk] if len(info) > 1 else []
            if len(bulk) > 1:
                c, R, a = merge_core([(x[1], x[2], x[3], 4 / 3 * np.pi * x[3].prod()) for x in bulk])
                vbe = sum(x[6] for x in bulk)
                cb = sum(x[6] * x[1] for x in bulk) / vbe        # centre of buoyancy: real-volume weighted
                elems = [(c, R, a, vbe, cb, [x[0] for x in bulk])]
            else:
                elems = [(x[1], x[2], x[3], x[6], x[1], [x[0]]) for x in bulk]
            elems += [(x[1], x[2], x[3], x[6], x[1], [x[0]]) for x in rest]
            for c, R, a, vbe, cb, gs in elems:
                for g in gs:
                    geoms_all.append(g)
                    geom_elem.append(len(E["body"]))
                for k, v in zip(("body", "c", "R", "a", "Vb", "cb", "geoms"), (j, c, R, a, vbe, cb, gs)):
                    E[k].append(v)
        self.e_body = np.array(E["body"])
        self.e_c = np.array(E["c"])
        self.e_R = np.array(E["R"])
        self.e_a = np.array(E["a"])
        self.e_Vb = np.array(E["Vb"])
        self.e_cb = np.array(E["cb"])
        self.ne = len(self.e_body)
        self.starts = np.flatnonzero(np.r_[True, self.e_body[1:] != self.e_body[:-1]])
        self.first = self.starts                         # each body's first element: its core
        self.e_G, self.e_Gr, kappa = ellipsoid_coeffs(self.e_a)
        self.e_mA, self.e_IA = added_mass(self.e_a, kappa)
        self.e_dv, _, self.e_c1, self.e_c2 = hs_coeffs(self.e_a)
        # constants in the body frame, so a step needs no per-element rotation matrices: for each element axis e_i,
        # its outer product (for body-frame tensors), its square (diagonal of a tensor along it) and (c x e_i)^2
        # (the parallel-axis diagonal at the element's centre c)
        ax = np.transpose(self.e_R, (0, 2, 1))           # (ne, axis i, xyz)
        self.e_EE = (ax[:, :, :, None] * ax[:, :, None, :]).reshape(self.ne, 3, 9)
        self.e_E2 = ax * ax
        self.e_X = _cross(np.repeat(self.e_c[:, None, :], 3, axis=1), ax) ** 2
        rho = self.rho
        self.e_Mb = (rho * self.e_mA[:, :, None] * self.e_EE).sum(1)                  # added-mass tensor, body frame
        self.e_Mr = (rho * self.e_mA[:, :, None] * self.e_X).sum(1) + (rho * self.e_IA[:, :, None] * self.e_E2).sum(1)
        self.pg = np.array(geoms_all)
        self.pg_elem = np.array(geom_elem)
        import spray
        _, self.reff = spray.shape_coeffs(m.geom_type[self.pg], m.geom_size[self.pg], m.geom_aabb[self.pg, 3:])
        self.wet = np.zeros(m.nbody)
        self._wl = np.zeros(self.nb)
        self.s_body = np.zeros(self.nb)
        self.s_elem = np.ones(self.ne)
        self._box_prev = {}
        if self.spec["adhesion_scale"] > 0:
            m.flg_adhesion = True
        return self

    # ---------- every step ----------
    def _box_kinematics(self, d, b, dt):
        """Pose of box body b, and a function giving its material velocity and acceleration (sim frame) at points."""
        if b == 0:
            return None
        x, R = d.xpos[b].copy(), d.xmat[b].reshape(3, 3).copy()
        w = d.cvel[b, :3].copy()
        v0 = d.cvel[b, 3:] + np.cross(w, x - d.subtree_com[b])      # velocity of the body origin
        prev = self._box_prev.get(b)
        al, a0 = ((w - prev[0]) / dt, (v0 - prev[1]) / dt) if prev is not None else (np.zeros(3), np.zeros(3))
        self._box_prev[b] = (w, v0)
        return x, R, w, v0, al, a0

    def _liquid_motion(self, d, p, V, A):
        """Liquid velocity (sim frame) and LAB acceleration, angular velocity and acceleration at points p (n, 3)."""
        n = len(p)
        uL = np.tile(-V, (n, 1))
        aL, wL, alL = np.zeros((n, 3)), np.zeros((n, 3)), np.zeros((n, 3))
        free = np.ones(n, bool)
        e = self.e
        for bx in self.boxes:
            kin = self._box_kinematics(d, bx["body"], self.dt) if bx["body"] else None
            if kin is None:
                loc = p
            else:
                x, R, w, v0, al, a0 = kin
                loc = (p - x) @ R
            inside = free & np.all((loc >= bx["lo"]) & (loc <= bx["hi"]), axis=1)
            if not inside.any():
                continue
            free &= ~inside
            if kin is None:
                uL[inside] = (e - 1.0) * V
                aL[inside] = e * A
            else:
                r = p[inside] - x
                vb = v0 + np.cross(w, r)
                ab = a0 + np.cross(al, r) + np.cross(w, np.cross(w, r))
                uL[inside] = e * vb + (e - 1.0) * V
                aL[inside] = e * (A + ab)
                wL[inside] = e * w
                alL[inside] = e * al
        return uL, aL, wL, alL

    def step(self, m, d, i=None, tray_d=(0.0, 0.0, 0.0), tray_v=(0.0, 0.0, 0.0), tray_a=(0.0, 0.0, 0.0)):
        """Forces, armature and damping for this step. tray_d, tray_v, tray_a: the sim frame's displacement, velocity
        and acceleration in the lab (sorter.py: x[i] * axis etc.; zero in a pure lab-frame run)."""
        t0 = time.perf_counter()
        D, V, A = (np.asarray(v, float) for v in (tray_d, tray_v, tray_a))
        rho, mu, sp = self.rho, self.mu, self.spec
        eb = self.e_body
        q = d.qpos[self.qadr[:, None] + np.arange(7)]
        pos, Rb = q[:, :3], quat2mat(q[:, 3:])
        qv = d.qvel[self.dadr[:, None] + np.arange(6)]
        v, wl = qv[:, :3], qv[:, 3:]                      # origin velocity (world), angular velocity (body axes)
        ww = _mv(Rb, wl)
        Rbe, eR = Rb[eb], self.e_R
        r = _mv(Rbe, self.e_c)                            # element centre relative to the body origin, world
        p = pos[eb] + r

        # submerged fraction and the submerged part's centroid offset
        if np.isfinite(self.level):
            zs = self.level - D[2]
            az = self.e_a * _mtv(eR, Rb[:, 2, :][eb])     # A^T e_z, A = element axes x diag(a), in element axes
            h = np.sqrt((az * az).sum(1))
            s, zbar = cap_fraction((zs - p[:, 2]) / h)
            off = (zbar / h)[:, None] * _mv(Rbe, _mv(eR, self.e_a * az))
        else:
            s, off = np.ones(self.ne), np.zeros((self.ne, 3))
        self.s_elem = s

        uL, aL, wLq, alL = self._liquid_motion(d, p, V, A)
        if self.flow is not None:                         # exploratory: flow through round-hole screens
            uL = self.flow.adjust(d, p, uL)
        # drag on each element's velocity relative to the liquid, in its principal axes
        w = v[eb] + _cross(ww[eb], r) - uL
        wloc = _mtv(eR, _mtv(Rbe, w))
        Re = rho * np.sqrt((w * w).sum(1)) * self.e_dv / mu
        rr = np.sqrt(Re)
        sph = (1 + 0.15 * Re ** 0.687) / (1 + rr / 8 + 0.0175 * Re)       # Schiller-Naumann over H-S, for a sphere
        k = (mu * sp["drag_scale"]) * self.e_G * ((1 + self.e_c1 * rr[:, None] + self.e_c2 * Re[:, None]) * sph[:, None])
        k *= s[:, None]
        Fd = -_mv(Rbe, _mv(eR, k * wloc))
        kr = (mu * sp["drag_scale"]) * self.e_Gr * s[:, None]
        Tr = -_mv(Rbe, _mv(eR, kr * _mtv(eR, wl[eb] - _mtv(Rbe, wLq))))
        Fb = (rho * s * self.e_Vb)[:, None] * (aL - GRAV)
        rb = _mv(Rbe, self.e_cb)                         # centre of buoyancy (real-volume weighted)
        T = _cross(r, Fd) + _cross(rb + off, Fb) + Tr
        if sp["munk"] and sp["added_mass"]:
            P = _mv(Rbe, _mv(eR, (rho * sp["added_mass"]) * self.e_mA * s[:, None] * wloc))
            T += sp["munk"] * _cross(P, w)
        F = np.add.reduceat(Fd + Fb, self.starts, axis=0)
        Tb = np.add.reduceat(T, self.starts, axis=0)

        # added mass -> armature (translation: world-axis diagonal; rotation: body-axis diagonal, parallel axis)
        if sp["added_mass"]:
            Mb = np.add.reduceat(s[:, None] * self.e_Mb, self.starts, axis=0).reshape(-1, 3, 3) * sp["added_mass"]
            arm_t = ((Rb @ Mb) * Rb).sum(2)
            arm_r = np.add.reduceat(s[:, None] * self.e_Mr, self.starts, axis=0) * sp["added_mass"]
            F += arm_t * (aL[self.first] - A)
            Tb += _mv(Rb, arm_r * _mtv(Rb, alL[self.first]))
            arm = np.concatenate([arm_t, arm_r], axis=1).ravel()
            m.dof_armature[self.dofs] = self.arm0 + arm
            m.dof_M0[self.dofs[self.simple]] = self.M00[self.simple] + arm[self.simple]
        # implicit part of the drag: the diagonal of each body's drag matrix about its origin
        if sp["implicit"]:
            Kb = np.add.reduceat(np.einsum("ni,nij->nj", k, self.e_EE), self.starts, axis=0).reshape(-1, 3, 3)
            dt_ = ((Rb @ Kb) * Rb).sum(2)
            dr = np.add.reduceat(np.einsum("ni,nij->nj", k, self.e_X) + np.einsum("ni,nij->nj", kr, self.e_E2),
                                 self.starts, axis=0)
            m.dof_damping[self.dofs] = self.damp0 + np.concatenate([dt_, dr], axis=1).ravel()
            F += dt_ * v
            Tb += _mv(Rb, dr * wl)
        # wrench about the origin -> xfrc_applied at the centre of mass
        com_arm = _mv(Rb, self.ipos)
        d.xfrc_applied[self.roots, :3] += F
        d.xfrc_applied[self.roots, 3:] += Tb - _cross(com_arm, F)

        # wetness, and capillary adhesion only where the body is out of the liquid
        Vb = np.add.reduceat(self.e_Vb, self.starts)
        self.s_body = np.add.reduceat(self.e_Vb * s, self.starts) / Vb
        self._wl = np.maximum(self._wl * np.exp(-self.dt / sp["dry_tau_s"]), self.s_body)
        wet = self._wl if self.sp is None else np.maximum(self._wl, self.sp.wet[self.roots])
        self.wet[self.roots] = wet
        if sp["adhesion_scale"] > 0:
            wg = wet[eb[self.pg_elem]] * (1.0 - s[self.pg_elem])
            m.geom_adhesion[self.pg] = sp["adhesion_scale"] * 2 * np.pi * self.gamma * self.reff * wg
        self.s_sum += float(self.s_body.mean())
        self.n_steps += 1
        self.wall += time.perf_counter() - t0

    # ---------- reporting ----------
    def summary(self):
        return {"spec": {k: v for k, v in self.spec.items()}, "rho_g_mm3": self.rho, "mu_g_mm_s": self.mu,
                "gamma_mN_m": self.gamma, "level_mm": None if not np.isfinite(self.level) else self.level,
                "entrain": self.e, "n_elements": int(self.ne), "n_bodies": int(self.nb),
                "mean_submerged": round(self.s_sum / max(self.n_steps, 1), 4),
                "boxes": [{"body": b["body"], "lo": [round(float(x), 3) for x in b["lo"]],
                           "hi": [round(float(x), 3) for x in b["hi"]]} for b in self.boxes],
                "wall_s": round(self.wall, 3), "ms_per_step": round(1000 * self.wall / max(self.n_steps, 1), 4)}

    def scene(self):
        """For the replay page: the bath's free surface (lab z, mm) and colour."""
        return {"liquid": self.spec["liquid"], "level_mm": None if not np.isfinite(self.level) else self.level,
                "entrain": self.e}


def _mv(M, v):
    """M v for stacks of 3x3 matrices and vectors (two-operand einsum is the fastest numpy option at this size)."""
    return np.einsum("nij,nj->ni", M, v)


def _mtv(M, v):
    """M^T v for stacks of 3x3 matrices and vectors."""
    return np.einsum("nji,nj->ni", M, v)


class ScreenFlow:
    """EXPLORATORY, off by default (spec screen_flow=1): the liquid's flow through a round-hole screen, ENTOSIEVE.md.

    The bath model above moves the liquid in a box uniformly, so a plate moving through the liquid sees the same
    relative flow over holes and over solid. Real flow through a perforated plate goes through the holes: at relative
    normal speed U the jets in the holes run at U / phi (phi the open fraction), the flow over solid parts turns
    sideways into the nearest hole, and the field evens out within about a hole radius. This is a kinematic sketch of
    that, divergence-free in each hole's cell (a circle of radius R_c = R / sqrt(phi) round a hole of radius R), with
    h the distance from the plate face and lam = R (ASSUMED):
        u_z = U + dU exp(-h / lam),   dU = U (1 / phi - 1) over a hole, -U over solid (no flow into the plate)
        u_r = side * U exp(-h / lam) * (R_c^2 - r^2) / (2 lam r)  over solid (toward the hole upstream, away below)
              side * U (1 / phi - 1) exp(-h / lam) r / (2 lam)     over a hole
    U is the relative normal velocity the bath model gives at the point. Specimens don't block holes: one lying on a
    hole feels the full jet, which stands in for the suction that would press it into the hole. Unvalidated: no data
    or flow solution was used to check it."""

    def __init__(self, design, rock=None, lam_scale=1.0):
        from scipy.spatial import cKDTree
        self.screens = []
        zone_body = {}
        if rock is not None and getattr(rock, "body", None) is not None:
            zone_body = {L["zone"]: int(b) for L, b in zip(rock.levels, rock.body)}
        for L in design.info.get("layers", []):
            if L.get("rule") != "round" or not L.get("hole_centres_mm"):
                continue
            c = np.array(L["hole_centres_mm"], float)
            tree = cKDTree(c)
            pitch = float(np.median(tree.query(c, k=2)[0][:, 1])) if len(c) > 1 else 2 * L["opening_mm"]
            R = L["opening_mm"] / 2
            phi = np.pi * R * R / (pitch * pitch * np.sqrt(3) / 2)       # 60 deg staggered lattice
            self.screens.append({"tree": tree, "c": c, "R": R, "phi": phi, "Rc": R / np.sqrt(phi),
                                 "lam": lam_scale * R, "z0": L["surface_z_mm"][0], "z1": L["surface_z_mm"][1],
                                 "lo": c.min(0) - pitch, "hi": c.max(0) + pitch, "body": zone_body.get(L["zone"], 0)})

    def adjust(self, d, p, uL):
        """uL (sim frame) at points p, with the flow through every screen added near it."""
        uL = uL.copy()
        for sc in self.screens:
            if sc["body"]:
                x, R = d.xpos[sc["body"]], d.xmat[sc["body"]].reshape(3, 3)
                w = d.cvel[sc["body"], :3]
                v0 = d.cvel[sc["body"], 3:] + np.cross(w, x - d.subtree_com[sc["body"]])
                loc = (p - x) @ R
            else:
                x, R, w, v0 = np.zeros(3), np.eye(3), np.zeros(3), np.zeros(3)
                loc = p
            band = 3 * sc["lam"]
            near = np.flatnonzero((loc[:, 2] > sc["z0"] - band) & (loc[:, 2] < sc["z1"] + band)
                                  & np.all((loc[:, :2] > sc["lo"]) & (loc[:, :2] < sc["hi"]), axis=1))
            if not len(near):
                continue
            vplate = v0 + np.cross(w, p[near] - x)                 # the screen's own velocity at the points
            rel = (uL[near] - vplate) @ R                          # relative liquid velocity, screen axes
            U = rel[:, 2]
            dist, idx = sc["tree"].query(loc[near, :2])
            rvec = loc[near, :2] - sc["c"][idx]
            r = np.maximum(dist, 1e-6)
            z = loc[near, 2]
            side = np.where(z >= sc["z1"], 1.0, np.where(z <= sc["z0"], -1.0, 0.0))
            h = np.where(side > 0, z - sc["z1"], np.where(side < 0, sc["z0"] - z, 0.0))
            e = np.exp(-h / sc["lam"])
            hole = r < sc["R"]
            k = 1.0 / sc["phi"] - 1.0
            uz = U + np.where(hole, U * k, -U) * e
            ur = side * e * np.where(hole, U * k * r / (2 * sc["lam"]),
                                     U * np.maximum(sc["Rc"] ** 2 - r * r, 0.0) / (2 * sc["lam"] * r))
            rel[:, 2] = uz
            rel[:, :2] += (ur / r)[:, None] * rvec
            uL[near] = vplate + rel @ R.T
        return uL


def settling_report(kind="insect_malaise_2to6", liquid="water", n=3, seed=0):
    """Print the elements of a few specimens and their net weight and drag in the liquid."""
    import sorter
    rng = np.random.default_rng(seed)
    parts = [sorter.make_particle(kind, rng) for _ in range(n)]
    body = "".join(f'<body name="p{i:03d}" pos="{20 * i} 0 50"><freejoint/>{p.xml}</body>' for i, p in enumerate(parts))
    m = mujoco.MjModel.from_xml_string(f'<mujoco><option timestep="1e-4" gravity="0 0 {-G}" integrator="implicitfast"/>'
                                       f'<worldbody>{body}</worldbody></mujoco>')
    d = mujoco.MjData(m)
    lq = Liquid({"liquid": liquid}).bind(m, d, parts, [f"p{i:03d}" for i in range(n)])
    for j, p in enumerate(parts):
        sel = lq.e_body == j
        mass = lq.mass[j]
        vb = lq.e_Vb[sel].sum()
        print(f"{p.xml.split()[1]:9s} L {p.dims['length']:.2f} mm, mass {mass * 1e3:.4f} mg, elements {sel.sum()}, "
              f"net weight in {liquid} {100 * (1 - lq.rho * vb / mass):.1f} % of dry, core semi-axes "
              f"{np.round(lq.e_a[lq.first[j]], 3)}, added mass (core, x y z) {np.round(lq.rho * lq.e_mA[lq.first[j]] * 1e3, 4)} mg")


if __name__ == "__main__":
    settling_report()
