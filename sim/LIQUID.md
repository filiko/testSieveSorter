# Liquid: wet specimens in the sim

Malaise samples sit in ethanol, and BugSorter sorts wet. In liquid a specimen weighs only 5-23 % of its dry weight, and drag at stroke speeds is several times that ([INSECT_AUDIT.md](INSECT_AUDIT.md) §2.4). So dry insect results don't carry over. `liquid.py` puts the sorter in a bath. This file says how it is modelled, how it was checked, and what it leaves out. The EntoSieve replication, the physical check, is in [ENTOSIEVE.md](ENTOSIEVE.md).

**In short:**
- Settling speeds: spheres within 4 % of the standard drag curve (Re 3-1000); ellipsoids held broadside, end-on, face-on or edge-on within 12.5 % of the orientation-specific correlation; freely falling ellipsoids within 8 % of a free-fall fit, except thin discs above Re ≈ 100 (+32-34 %). Stokes limit within 0.1 %.
- Floating, neutral bodies and the non-inertial tray frame come out exactly (Archimedes to 0.001; a neutral sphere rides with the box at entrain 1 and stays still in the lab at entrain 0).
- In a box shaken at 40 Hz, `entrain` decides everything: at 1 the specimens sit still, at 0 the floor taps them every cycle. Added mass changes the hops by about a quarter to a third.
- No new MuJoCo resets at the insect time step; the liquid costs about 0.8-1.2 ms per step for 60 specimens (+50-150 %).
- Wet, a Malaise clump on the seesaw doesn't break up (dry: 80 of 190 bonds in 4 s), because it loses three quarters of its weight in ethanol.
- EntoSieve: the length cut comes out, the efficiencies don't (no stirring or jets in a uniformly moving liquid).

## Use

```
python sorter.py ... --liquid ethanol:level_mm=200,entrain=0.5
python sorter.py ... --liquid water                      (everything submerged, still bath)
```

| Option | Meaning | Default |
|---|---|---|
| liquid | `water` or `ethanol` (96 % v/v) | ethanol |
| level_mm | the free surface: a horizontal plane fixed in the **lab** (design frame at rest). Above the top box = fully immersed | omitted = everything submerged |
| entrain | 0-1: inside a box (holder box, catch pan, sieve container) the liquid moves with that box by this fraction. 0 = still bath, 1 = moves with the box. Outside every box the bath is still | 0 |
| rho, mu | override density (g/mm³) and viscosity (g/(mm·s)) | from the table below |
| added_mass, munk, drag_scale | 1 / 0 switches and scales for the sensitivity checks | 1, 1, 1 |
| adhesion_scale, dry_tau_s | capillary cling out of the liquid (spray.py's model) and drying time | 0.1, 30 s |
| screen_flow | 1: an **exploratory, unvalidated** sketch of the flow through round-hole screens (`ScreenFlow`; ENTOSIEVE.md §5) | 0 |

`RunConfig.liquid` takes the same keys as a dict. `results.json` gets `config.liquid` and a `liquid` summary (mean submerged fraction, ms per step). `scene.json` gets `liquid` (the surface level), and the replay page draws the surface as a blue plane. A dry run is unchanged: same seed, byte-identical `traj.npz`, and `results.json` identical except `wall_s` (checked on a buzzed insect run, a spray run and a seesaw clump run).

## Liquids

| | Density g/cm³ | Viscosity mPa·s | Surface tension mN/m | Source |
|---|---|---|---|---|
| Water, 20 °C | 0.998 | 1.002 | 72.8 | handbook values ([NIST WebBook](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=4)) |
| Ethanol 96 % v/v (93.8 % w/w), 20 °C | 0.807 | **1.4, ASSUMED (1.2-1.6)** | 22.4 | density: [Lange's table, 93-94 % w/w](https://en.wikipedia.org/wiki/Ethanol_(data_page)); surface tension: same page, pure ethanol at 25 °C |

The ethanol viscosity is not tabulated where I could check it. Pure ethanol is 1.144 mPa·s at 20 °C ([data page](https://en.wikipedia.org/wiki/Ethanol_(data_page))). Water raises it: one compiled table gives 1.20 mPa·s at 100 wt % and 1.88 at 80 wt % ([PMC6150737, Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC6150737/), at its own temperature). Interpolating to 93.8 wt % gives about 1.4. INSECT_AUDIT assumed 1.2. Terminal speeds in the validation scale roughly as mu^-0.5 to mu^-1, so ±15 % in viscosity moves them by 7-15 %.

Specimen density stays `insects.RHO` = 1.05 g/cm³ (ASSUMED in insects.py; air-free tissue in liquid). A specimen then weighs 4.9 % of its dry weight in water and 23 % in ethanol.

## The model

Each particle body is split into **elements**, each an ellipsoid:

| Element | From | Why |
|---|---|---|
| core | the body's bulk geoms (head, thorax, abdomen; a whole grain) merged into one ellipsoid: principal axes of their second moment, semi-axes from their extents | touching segments don't each get a sphere's drag: two touching spheres in Stokes flow have 1.3-1.4 x one sphere's drag, not 2 x |
| slender | each capsule (legs, antennae, twigs) as the prolate spheroid of the same length and volume | legs dominate drag at low Re for long-legged specimens; a single body ellipsoid would miss them |
| thin | each thin ellipsoid or box (wings, an open elytron, a leaf) | very different area face-on and edge-on |

A Malaise specimen has 13-20 elements; 60 specimens about 930.

Per element and step, with w its velocity relative to the local liquid and s its submerged fraction:

| Effect | Formula | Notes |
|---|---|---|
| Submerged fraction | s = (1 + δ)²(2 − δ)/4, δ = (z_surface − z_centre)/h | exact for an ellipsoid cut by a plane (an affine image of a sphere cap); h is its vertical half-extent. Buoyancy acts at the cap's centroid, so a floating body gets a righting moment |
| Buoyancy + pressure gradient | F = ρ V_b s (a_liquid − g) | V_b is the **real** volume. Thin parts are thickened for contact stability (legs r ≥ 0.06 mm, wings 80 µm, insects.py) with their density lowered to keep their mass; their real volume is mass / tissue density, so a thickened wing doesn't float the fly |
| Drag | F = −s R diag(k_i) Rᵀ w, k_i = μ G_i f_i(Re) | G_i: exact Stokes resistance of the ellipsoid along principal axis i (Oberbeck 1876, via Carlson's elliptic integrals; checked against Happel & Brenner's closed forms below), so a tilted body glides. f_i: Schiller-Naumann's sphere factor 1 + 0.15 Re^0.687, times the shape effect of [Hölzer & Sommerfeld 2008](https://doi.org/10.1016/j.powtec.2007.08.021) for flow along axis i (their C_D over its Stokes terms, over the same ratio for a sphere). Re = ρ\|w\|d_v/μ |
| Rotational drag | T = −s R diag(μ Gr_i) Rᵀ (Ω − Ω_liquid) | exact Stokes torque of the ellipsoid ([Jeffery 1922](https://doi.org/10.1098/rspa.1922.0078)); off-centre elements' drag adds most of a body's rotational damping |
| Added mass | Tuckerman's potential-flow coefficients per ellipsoid, as in [MuJoCo's fluid model](https://mujoco.readthedocs.io/en/stable/computation/fluid.html) | summed per body and put into the free joint's inertia (below) |
| Munk moment | T = (M_a w) × w | the potential-flow torque that turns a body broadside to its relative velocity |

**Why explicit forces and not MuJoCo's fluid model.** MuJoCo's ellipsoid model uses one global `wind` and density, so it can't give the liquid in each box its own velocity or switch off above the surface, and its buoyancy needs `gravcomp`, which is only right when the liquid moves with the tray. It also leaves out the acceleration term of added mass: `engine_passive.c` calls `mj_addedMassForces(lvel, NULL, ...)` with no accelerations. So `liquid.py` writes `xfrc_applied` itself.

**Stiffness.** For the smallest specimens with clamped legs, the rotational drag time constant comes within a few time steps of dt. The diagonal of each body's drag matrix (about its origin: translation along the world axes, rotation about the body axes, parallel-axis terms included) goes into `dof_damping`, which `implicitfast` integrates implicitly, and the same amount is added back as an explicit force. The net force is the full drag at this step's velocity, and a 10⁵ g/s damper on a 1 g body decays by exactly the implicit-Euler factor (checked).

### Frames

The bath is fixed in the lab. sorter.py's translation runs move the trays by d(t) along the stroke and apply gravity minus the tray acceleration A to every body. With M_a the added mass and a_L the liquid's **lab** acceleration, the body's equation in the tray frame is

  (m + M_a) a_sim = m (g − A) + M_a (a_L − A) + ρV (a_L − g) + drag + contact.

MuJoCo supplies the first term (`opt.gravity`) and M_a a_sim (the armature); `liquid.py` adds the rest.

| Case | a_L | What the equation gives |
|---|---|---|
| entrain 1, inside a box | A | the extra terms reduce to −ρV (g − A), MuJoCo's `gravcomp`: a neutral body rides along with the box |
| entrain 0 | 0 | −M_a A − ρV g: a neutral body stays still in the lab while the box moves round it |
| outside every box | 0 | still bath |
| seesaw level k (rocking.py, lab frame + buzz) | entrain × (A + α_k × r + ω_k × (ω_k × r)) | the liquid in level k turns with that level; its velocity is entrain × the level's material velocity at the point |

The liquid's velocity in sim coordinates is entrain × (box velocity) − (1 − entrain) × V inside a box and −V outside, V the tray velocity. The surface sits at level_mm − d_z(t) in sim coordinates. Box bodies are read from MuJoCo's state, so levels that move on their own (per-box shaking) work as long as `boxes_for()` lists their bodies; `Liquid(spec, boxes=[{"body": id, "lo": xyz, "hi": xyz}])` takes them directly.

### Added mass: included

At 40 Hz and 0.35 mm the box accelerates at 2.25 g. A near-neutral specimen's response is set by its inertia against the liquid's. In water the net weight is 5 % of the mass, while the added mass of a 2 mm fly's body ellipsoid is 0.06 / 0.32 / 0.56 mg along its length / width / thickness, against a body mass of 0.55 mg, and each spread 2 × 0.8 mm wing moving face-on adds another 0.57 mg. Leaving it out changes how hard the floor must push a specimen and how long it coasts (drag time constant (m + M_a)/c, up to 2-3 x longer with it). So it is in, as an implicit inertia:

- MuJoCo 3.17 reads `dof_armature` every step for most bodies, but builds a "simple" body's inertia (centre of mass at its origin, principal axes along its own) from the constant `dof_M0`, which includes the armature from compile time. `liquid.py` writes whichever the solver reads (checked: an armature of 1 on a unit mass halves its acceleration).
- Translation: the diagonal, along the world axes, of the rotated added-mass tensor of the whole body. Rotation: the diagonal about the body's own axes, with parallel-axis terms. The off-diagonal coupling is left out; it is small when the body lies flat (the common case), largest for a tilted wing.
- The measured effect is in the shaken-box table below (with and without added mass).

### Wetness and surface tension

- A body's liquid wetness is max(previous × e^(−dt/dry_tau_s), submerged fraction): fully wet once submerged, drying slowly once out. With `--spray` the larger of the two counts. `clumps.py` reads it, so bonds weaken by k_wet under liquid.
- Capillary adhesion (spray.py's `adhesion_scale × 2πγR_eff w` per contact) acts only on the part of a body that is out of the liquid: under liquid there is no meniscus. It works with or without `--spray`.
- **Surface tension at the free surface is left out.** A specimen crossing the surface feels only the change in buoyancy. Real ethanol-preserved specimens are wetted by ethanol and sink through the surface, but in water some taxa float on it: EntoSieve names leafhoppers (most of test 2's A intruders) and aphids, which form a water-repellent film. None of the generated body plans is such a floater.

## Validation

All from `liquid_check.py`; the full settling table is in the appendix. Nothing below was tuned.

### 1. Stokes drag of ellipsoids (`liquid_check.py stokes`)

The ellipsoid integrals in `liquid.py` against the closed-form Stokes drag of spheroids ([Happel & Brenner 1983](https://doi.org/10.1007/978-94-009-8352-6); Chwang & Wu 1975), per unit μU:

| Semi-axes (a along the axis) | Motion | Closed form | liquid.py | Difference |
|---|---|---|---|---|
| 1, 1, 1 (sphere) | any | 18.850 (6π) | 18.850 | 0.00 % |
| 3, 1, 1 (prolate) | along / across | 26.474 / 32.565 | 26.474 / 32.565 | 0.00 % |
| 10, 1, 1 (needle) | along / across | 49.897 / 71.846 | 49.897 / 71.846 | 0.00 % |
| 0.3, 1, 1 (oblate) | along / across | 16.474 / 13.286 | 16.474 / 13.286 | 0.00 % |
| 0.05, 1, 1 (near disc) | along / across | 16.018 / 11.116 | 16.018 / 11.116 | 0.00 % |

The thin-disc limits come out at 16 μaU face-on and 32/3 μaU edge-on, as they should.

### 2. Settling in still water and ethanol (`liquid_check.py settle`)

A single body released from rest in an unbounded still bath, orientation held (Munk moment off), terminal velocity against standard correlations. Long axis 0.5-6 mm, densities 1.05 and 1.15 g/cm³ in water and 1.05 in ethanol: Re 0.3-980, the range of 0.5-6 mm specimens.

| Shape | Orientation | Re range | Error vs reference | Reference | Error vs second reference |
|---|---|---|---|---|---|
| sphere | - | 2.7-984 | -3.1 to +3.9 % | Clift, Grace & Weber 1978 standard curve (experimental fit) | |
| prolate 3:1:1 | broadside | 0.3-167 | -12.5 to -5.2 % | Hölzer & Sommerfeld 2008 (orientation-specific) | +0.9 to -19.8 % (Ganser 1993) |
| prolate 3:1:1 | end-on | 0.4-264 | -11.1 to -1.2 % | Hölzer & Sommerfeld | +1.7 to +23.5 % (Ganser) |
| oblate 1:1:0.3 | face-on | 0.7-238 | -10.4 to -3.0 % | Hölzer & Sommerfeld | +2.0 to -24.5 % (Ganser) |
| oblate 1:1:0.3 | edge-on | 0.9-417 | -10.5 to +1.2 % | Hölzer & Sommerfeld | +4.7 to +32.1 % (Ganser) |
| all five, at 1000 x water's viscosity | | Re < 0.001 | -0.10 to -0.02 % | exact Stokes closed form | |

- Spheres are within 4 % of the experimental standard curve everywhere.
- Non-spheres are within 12.5 % of Hölzer & Sommerfeld, the orientation-specific correlation, and always slightly slower: the model's sphere factor is Schiller-Naumann's, which gives about 10 % more drag than H&S's own sphere at Re 10-100.
- Ganser's correlation has no orientation in its Newton term (only sphericity), so it can't follow a body held broadside or end-on at Re > 30; the 20-32 % gaps are there.

### 3. Free fall (`liquid_check.py freefall`)

Released 45° tilted, Munk moment on, against [Bagheri & Bonadonna 2016](https://arxiv.org/abs/1810.08787), Eq. 34, a fit to freely falling particles of many shapes (5 % mean error):

| Shape | Fluid, ρ_b | Long axis mm | Final orientation | Re | v sim mm/s | v B&B mm/s | Error |
|---|---|---|---|---|---|---|---|
| prolate 3:1:1 | water, 1.05 | 1 / 2 / 4 | long axis horizontal | 2.0 / 10.5 / 42 | 4.23 / 10.9 / 21.9 | 4.22 / 10.8 / 22.9 | +0.4 / +0.7 / -4.6 % |
| prolate 3:1:1 | water, 1.15 | 1 / 2 / 4 | long axis horizontal | 4.9 / 22 / 81 | 10.2 / 22.9 / 42.2 | 10.1 / 23.3 / 45.7 | +1.4 / -1.7 / -7.6 % |
| prolate 3:1:1 | ethanol, 1.05 | 1 / 2 / 4 | long axis horizontal | 3.5 / 17 / 63 | 12.7 / 30.0 / 56.9 | 12.6 / 30.2 / 60.9 | +1.1 / -0.7 / -6.7 % |
| oblate 1:1:0.3 | water, 1.05 | 1 / 2 / 4 | face-on (0 / 0 / 32° tilt) | 4.2 / 18 / 68 | 6.22 / 13.5 / 25.4 | 5.86 / 12.7 / 23.9 | +6.0 / +6.2 / +6.6 % |
| oblate 1:1:0.3 | water, 1.15 | 1 / 2 / 4 | face-on, face-on, **73° (edge-on)** | 9.2 / 35 / 157 | 13.7 / 26.4 / 59.0 | 12.8 / 25.6 / 44.8 | +7.4 / +3.1 / **+31.7 %** |
| oblate 1:1:0.3 | ethanol, 1.05 | 1 / 2 / 4 | face-on, face-on, **83° (edge-on)** | 6.8 / 27 / 127 | 17.7 / 35.4 / 82.2 | 16.5 / 34.0 / 61.2 | +7.1 / +4.2 / **+34.3 %** |

- Elongate bodies turn broadside and fall within 8 % of the free-fall correlation.
- Flat bodies settle face-on and within 7.4 % up to Re about 70. The two 4 mm discs at Re 130-160 tip over and fall edge-on, 32-34 % too fast. Real discs start to flutter about there, but here the potential-flow Munk moment overshoots instead (Limits).

### 4. Neutral and buoyant bodies (`liquid_check.py neutral`)

| Check | Result | Expected |
|---|---|---|
| 2 mm sphere at the liquid's density, still bath, 2 s | moved 0 mm | 0 |
| 2 mm sphere, ρ_b 0.90 in water, released 5 mm under the surface | rises and floats; submerged fraction 0.902, last 0.5 s within 0.001 mm | 0.902 (Archimedes) |
| prolate 3:1:1, 3 mm, ρ_b 0.90 | floats, submerged 0.902, steady | 0.902 |
| oblate 1:1:0.3, 3 mm, ρ_b 0.90 | floats flat (0° tilt), submerged 0.901, steady | 0.902 |
| 2 mm sphere, ρ_b 0.70 | floats, submerged 0.701, steady | 0.701 |

### 5. Frames: a neutral sphere in a shaken box (`liquid_check.py frames`)

A 1 mm sphere at the liquid's density, inside a box (the sim frame) shaken straight up and down at 40 Hz and 0.35 mm, no contacts, released moving with the liquid:

| entrain | Added mass | Motion relative to the box, amplitude mm | Motion in the lab, amplitude mm | Expected |
|---|---|---|---|---|
| 1 | on / off | 0.0000 / 0.0000 | 0.3500 / 0.3500 | rides with the box |
| 0.5 | on / off | 0.175 / 0.175 | 0.175 / 0.175 | half way |
| 0 | on / off | 0.3498 / 0.3496 | 0.0004 / 0.0005 | stays still in the lab |

So buoyancy, the pressure gradient and the added mass are right in the non-inertial tray frame, with the bath fixed in the lab.

### 6. Specimens in a box shaken at 40 Hz (`liquid_check.py box`)

12 Malaise specimens (6 under 2 mm, 6 of 2-6 mm) resting on the solid floor of a box (`entosieve:solid,drop=12`), shaken straight up and down at 40 Hz and 0.35 mm (peak 88 mm/s, 2.25 g) for 1 s through sorter.py's tray-frame path, 2 seeds. "Rise" is each specimen's centre of mass above its own lowest point (5th percentile); "off the floor" is the time it spends more than 0.05 mm above that.

| Condition | Rise p50 / p95 mm | Off the floor | Lateral travel mm/s | Speed relative to the box, rms mm/s |
|---|---|---|---|---|
| dry | 0.23 / 0.74 | 66 % | 2.3 | 68 |
| water, entrain 0 | 0.51 / 1.23 | 90 % | 0.28 | 63 |
| water, entrain 0.5 | 0.28 / 0.78 | 86 % | 0.34 | 32 |
| water, entrain 1 | 0.007 / 0.28 | 18 % | 0.17 | 1.1 |
| ethanol, entrain 0 | 0.46 / 1.03 | 88 % | 0.89 | 64 |
| ethanol, entrain 0.5 | 0.25 / 0.55 | 84 % | 0.98 | 35 |
| ethanol, entrain 1 | 0.008 / 0.12 | 10 % | 0.18 | 4.1 |
| water, entrain 0, **no added mass** | 0.40 / 0.81 | 86 % | 0.40 | 63 |
| water, entrain 0, no Munk moment | 0.52 / 1.40 | 89 % | 0.39 | 63 |

Why, and why it is physically sensible:
- **Dry**, the floor's downward acceleration (2.25 g) exceeds g for part of each cycle, so specimens are thrown and hop (0.2-0.7 mm) and wander sideways at about 2 mm/s.
- **Entrain 1**, the liquid moves with the box. In the box frame a specimen feels gravity minus the box's acceleration times (m − ρV)/(m + M_a), about 3 % of it in water and 17 % in ethanol (for an added mass of half the displaced liquid). The floor never pulls away fast enough to throw it: it stays put (relative speed 1-4 mm/s). A box whose liquid follows it doesn't agitate its specimens at all.
- **Entrain 0**, the liquid stays still in the lab. The specimen is held by it and barely moves in the lab, so the floor moves ±0.35 mm under it: it is off the floor 90 % of the time and the floor taps it every cycle at up to 88 mm/s (relative speed = the box's own, 62 mm/s rms). But it hardly moves sideways (0.3-0.9 mm/s), because the liquid damps it.
- **Entrain 0.5** sits between, with half the relative speed, as it should.
- **Added mass matters:** without it the hops are 22 % lower at the median and 34 % lower at p95 (0.40 against 0.51 mm, 0.81 against 1.23 mm). A specimen with added mass is harder to stop once the floor has launched it, and coasts further against the drag. That is the error of leaving it out, about a quarter to a third in this regime.
- The Munk moment changes little here (the specimens mostly move straight up and down).

So under liquid, how hard a shaken box agitates its specimens is set by `entrain`, which nobody has measured.

### 7. Stability and cost (`liquid_check.py cost`)

60 Malaise specimens (`MALAISE_MIX_STRATIFIED`) at dt 0.125 ms and timeconst 0.25 ms, 1 s settle + 2 s (tower) or 4 s (seesaw), 2 seeds each. Tower: `inserts:5mm,2mm` shaken straight up and down at 40 Hz, 0.35 mm (tray frame). Seesaw: `inserts:5mm_across,2mm_across,pitch=55,holder=seesaw`, ±10°, 2 s period, with the 0.3 mm 40 Hz buzz (lab frame plus the buzz). Bath fully over the trays.

| Scene | Condition | MuJoCo resets | Worst overlap on the tray mm | ms per step | of which liquid | Overhead |
|---|---|---|---|---|---|---|
| tower | dry | 0 | 0.17 | 1.24 | - | - |
| tower | ethanol, entrain 0 / 0.5 / 1 | 0 / 0 / 0 | 0.14 | 1.87 / 1.91 / 2.06 | 0.86-0.92 | +51 / +54 / +67 % |
| tower | water, entrain 0 | 0 | 0.01 | 1.80 | 0.87 | +46 % |
| seesaw | dry | 0 | 0.32 | 0.62 | - | - |
| seesaw | ethanol, entrain 0 / 0.5 / 1 | 0 / 0 / 0 | 0.12-0.14 | 1.50 / 1.50 / 1.55 | 1.09-1.12 | +142 / +143 / +151 % |
| seesaw | water, entrain 0 | 0 | 0.01 | 1.14 | 0.88 | +85 % |

- **No new resets**, and the worst overlaps are no larger than dry (the liquid slows impacts).
- **The liquid costs about 0.8 ms per step** for 60 specimens (933 elements) on an idle core, and 0.9-1.2 ms when 6-8 runs share the machine (memory bandwidth); 0.3 ms for 12 specimens. It is pure numpy and doesn't depend on the scene. Relative to MuJoCo that is +50-67 % on the buzzed tower and +85-150 % on the seesaw, whose MuJoCo step is cheap. In the EntoSieve runs (22,892 plate geoms) a wet run costs about what a dry one does (3.0 against 3.5 ms per step on the 1.5 mm plate), because suspended specimens make fewer contacts.
- The EntoSieve work adds 90 wet runs of about 193,000 steps and 6 of 920,000, all without a reset (ENTOSIEVE.md).
- A caution found on the way: sorter.py counts a reset when `d.time` goes backwards, so a state that blows up on **every** step (time stuck at 0.0001 s) is never counted. A bug in an early version of `liquid.py` did exactly that. Every run above reached its full simulated time, so none was affected; a cheap guard would be to also check `results["sim_s"]` against the run's length.

### 8. A Malaise clump, dry against wet (`liquid_check.py clump`)

A clump of 40 `insect_malaise` specimens with a leaf, two twigs and 10 dirt grains, medium bonds (clumps.py), on `inserts:5mm,2mm,pitch=85` seesawing ±10° with a 2 s period, 1 s settle + 4 s, dt 0.0625 ms (CLUMPS.md's setting for insect clumps), 2 seeds. Wet: the whole tower under 96 % ethanol, so every body is fully wet and its bonds are at 40 % strength (k_wet 0.6).

| Condition | Seed | Free at the end | Largest cluster | Bonds broken | Peak contact force over 5 mN | MuJoCo resets | ms/step |
|---|---|---|---|---|---|---|---|
| dry | 0 | 20 % | 32 of 40 | 80 / 190 | 68 % | 0 | 3.1 |
| dry (not valid: resets) | 1 | 12 % | 31 | 80 / 189 | 62 % | **4** | 4.0 |
| ethanol, entrain 0.5 | 0 | 0 % | 40 | 0 / 190 | 20 % | 0 | 3.5 |
| ethanol, entrain 0.5 | 1 | 0 % | 40 | 6 / 189 | 32 % | 0 | 4.7 |
| ethanol, entrain 0 | 0 | 0 % | 40 | 0 / 190 | 20 % | 0 | 3.5 |
| ethanol, entrain 0 | 1 | 0 % | 40 | 10 / 189 | 32 % | 0 | 4.7 |

- **Wet, the clump doesn't break**, although its bonds are 2.5 x weaker. In ethanol the clump weighs about a quarter of its dry weight and the liquid damps its tumbling, so the loads that break bonds dry (sliding, rolling over, landing) mostly go away. The share of specimens hit by more than 5 mN drops from 68 % (the clean dry run) to 20-32 %: gentler, and no break-up.
- This matches the direction the literature reports (clumping is more common in wet sieving, [Elbrecht et al. 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8500090)), but the bond strengths themselves were set from **dry** loads (CLUMPS.md) and k_wet is ASSUMED. Under liquid a capillary bond has no meniscus at all, so only entanglement holds; nobody has measured it.
- For design: a breaker that relies on the clump's weight (tumbling, dropping) does far less in liquid. Under liquid, flow (jets, the spray, a draining stroke) has to do the work, and the sim models flow only crudely (Limits).
- The wet runs had no resets. One dry run had 4 (at the insect-clump time step clumps.py asks for), so its numbers are not valid: a reset sets the clock back, which is also why 39 of its bond breaks are logged "in the settle". The other dry run is clean.

## Limits

- **No flow solver.** The liquid in a box moves rigidly with it by the entrain fraction; outside it is still. No sloshing, no jets through the holes (the real flow through a perforated plate is concentrated in the holes, at the plate speed over the open fraction), no wakes, no boundary layers at walls. The EntoSieve replication shows what that costs: with nothing to move specimens sideways, a plate moving straight up and down keeps meeting each specimen at the same spot, and passage levels off at 28-60 % instead of the paper's 96-98 % (ENTOSIEVE.md). `screen_flow=1` is a first, unvalidated sketch of the hole flow.
- **No particle-particle hydrodynamics.** Each element sees the undisturbed liquid: no shielding, no hindered settling in a crowd, no lubrication forces between near-touching bodies.
- **No history forces** (Basset), no lift (Saffman, Magnus), no wake-induced torque other than the Munk moment.
- **The Munk moment is potential flow.** It is the right order at Re 10-100 and too strong below Re 1, where real bodies keep their orientation. A thin 4 mm disc in ethanol flutters edge-on in the sim (free-fall table), which real discs do only above Re ≈ 100.
- **Added mass** keeps only the diagonal of each body's tensor (above).
- **Surface tension at the free surface** is left out (above).
- **Thin parts** keep their clamped geometry for drag: legs at r = 0.06 mm instead of 0.02-0.04 overstate leg drag by about 10-15 % at low Re (slender-body drag depends on ln(L/d)); wings are fine (drag of a thin plate doesn't depend on its thickness).
- **The optimizer's legacy `rocking()` wrapper** (optimize.py) assigns `xfrc_applied` for root bodies inside mj_step and would overwrite the liquid's forces; run seesaw cases through rocking.py (`--stroke seesaw:...`) instead.

## What the optimizer should treat as uncertain

| Parameter | Range | Why |
|---|---|---|
| entrain | 0-1 per box type; for closed-wall containers whose rim stays out of the liquid (EntoSieve) 0-0.2; for open perforated trays fully under the surface and shaken at 40 Hz, 0-1 | nobody has measured it; it decides whether a shaken box agitates its specimens at all (shaken-box table) |
| ethanol viscosity | 1.2-1.6 mPa·s | not found in a checked table (above) |
| specimen density | 1.05-1.15 g/cm³ | INSECT_AUDIT; sets the net weight, which is 5-13 % (water) or 23-30 % (ethanol) of the dry weight |
| drag_scale | 0.85-1.15 | the settling errors against the correlations above |
| munk | 0-1 | potential-flow torque; too strong at low Re |
| adhesion_scale | 0-1 | spray.py's open question; under liquid it doesn't act |

## Sources

- Ascenzi et al. 2025, EntoSieve: [PMC12225705](https://pmc.ncbi.nlm.nih.gov/articles/PMC12225705/)
- Clift, Grace & Weber 1978, *Bubbles, Drops, and Particles*, Table 5.2 (standard sphere drag curve), as transcribed in [pychemqt](https://pychemqt.readthedocs.io/en/latest/_modules/lib/drag.html)
- Hölzer & Sommerfeld 2008, Powder Technology 184:361-365, and Ganser 1993, Powder Technology 77:143-152, as given in Table 2 of [Bagheri & Bonadonna 2016](https://arxiv.org/abs/1810.08787), Powder Technology 301:526-544 (whose Eq. 34 is the free-fall reference)
- Happel & Brenner 1983, *Low Reynolds number hydrodynamics*; Chwang & Wu 1975, J. Fluid Mech. 67:787 (Stokes drag of spheroids)
- Tuckerman 1925, NACA Report 210 (added mass of ellipsoids); [MuJoCo fluid docs](https://mujoco.readthedocs.io/en/stable/computation/fluid.html) and `engine_passive.c`

## Appendix: settling, every case

Orientation held (Munk moment off). HS = Hölzer & Sommerfeld 2008 with the lengthwise sphericity taken as the crosswise one, as they suggest; Ganser 1993 with the orientation's exact Stokes factor and his sphericity-based Newton factor.

| Shape | Orientation | Fluid | ρ_b g/cm³ | Long axis mm | Re | v sim mm/s | v reference mm/s | Error | v second reference mm/s | Error |
|---|---|---|---|---|---|---|---|---|---|---|
| sphere | any | water | 1.05 | 0.5 | 2.71 | 5.45 | 5.47 (Clift) | -0.4 % |  |  |
| sphere | any | water | 1.05 | 1 | 14.5 | 14.6 | 14.2 (Clift) | +2.5 % |  |  |
| sphere | any | water | 1.05 | 2 | 62.9 | 31.6 | 31.3 (Clift) | +1.0 % |  |  |
| sphere | any | water | 1.05 | 4 | 241 | 60.4 | 62.3 (Clift) | -3.1 % |  |  |
| sphere | any | water | 1.05 | 6 | 512 | 85.6 | 86.2 (Clift) | -0.7 % |  |  |
| sphere | any | water | 1.15 | 0.5 | 6.64 | 13.3 | 13.2 (Clift) | +1.2 % |  |  |
| sphere | any | water | 1.15 | 1 | 31.6 | 31.7 | 30.9 (Clift) | +2.7 % |  |  |
| sphere | any | water | 1.15 | 2 | 127 | 63.8 | 64.4 (Clift) | -1.0 % |  |  |
| sphere | any | water | 1.15 | 4 | 468 | 118 | 119 (Clift) | -1.2 % |  |  |
| sphere | any | water | 1.15 | 6 | 984 | 165 | 158 (Clift) | +3.9 % |  |  |
| sphere | any | ethanol | 1.05 | 0.5 | 4.74 | 16.5 | 16.4 (Clift) | +0.6 % |  |  |
| sphere | any | ethanol | 1.05 | 1 | 23.6 | 40.9 | 39.6 (Clift) | +3.3 % |  |  |
| sphere | any | ethanol | 1.05 | 2 | 97.3 | 84.4 | 84.6 (Clift) | -0.2 % |  |  |
| sphere | any | ethanol | 1.05 | 4 | 363 | 157 | 161 (Clift) | -2.2 % |  |  |
| sphere | any | ethanol | 1.05 | 6 | 766 | 221 | 217 (Clift) | +1.9 % |  |  |
| prolate 3:1:1 | broadside | water | 1.05 | 0.5 | 0.304 | 1.27 | 1.34 (HS) | -5.2 % | 1.26 (Ganser) | +0.9 % |
| prolate 3:1:1 | broadside | water | 1.05 | 1 | 2.03 | 4.23 | 4.57 (HS) | -7.5 % | 4.23 (Ganser) | +0.0 % |
| prolate 3:1:1 | broadside | water | 1.05 | 2 | 10.5 | 10.9 | 12.3 (HS) | -11.4 % | 11.6 (Ganser) | -5.7 % |
| prolate 3:1:1 | broadside | water | 1.05 | 4 | 41.9 | 21.9 | 25 (HS) | -12.4 % | 25.7 (Ganser) | -14.7 % |
| prolate 3:1:1 | broadside | water | 1.05 | 6 | 88.2 | 30.7 | 34.4 (HS) | -10.9 % | 37.7 (Ganser) | -18.7 % |
| prolate 3:1:1 | broadside | water | 1.15 | 0.5 | 0.83 | 3.47 | 3.69 (HS) | -6.0 % | 3.44 (Ganser) | +0.8 % |
| prolate 3:1:1 | broadside | water | 1.15 | 1 | 4.9 | 10.2 | 11.3 (HS) | -9.6 % | 10.5 (Ganser) | -2.2 % |
| prolate 3:1:1 | broadside | water | 1.15 | 2 | 21.9 | 22.9 | 26.2 (HS) | -12.5 % | 25.6 (Ganser) | -10.4 % |
| prolate 3:1:1 | broadside | water | 1.15 | 4 | 80.9 | 42.2 | 47.5 (HS) | -11.2 % | 51.7 (Ganser) | -18.3 % |
| prolate 3:1:1 | broadside | water | 1.15 | 6 | 167 | 58 | 63.1 (HS) | -8.1 % | 72.3 (Ganser) | -19.8 % |
| prolate 3:1:1 | broadside | ethanol | 1.05 | 0.5 | 0.567 | 4.1 | 4.34 (HS) | -5.6 % | 4.06 (Ganser) | +0.9 % |
| prolate 3:1:1 | broadside | ethanol | 1.05 | 1 | 3.52 | 12.7 | 13.9 (HS) | -8.7 % | 12.9 (Ganser) | -1.2 % |
| prolate 3:1:1 | broadside | ethanol | 1.05 | 2 | 16.6 | 30 | 34.1 (HS) | -12.2 % | 32.8 (Ganser) | -8.5 % |
| prolate 3:1:1 | broadside | ethanol | 1.05 | 4 | 63 | 56.9 | 64.5 (HS) | -11.8 % | 68.6 (Ganser) | -17.2 % |
| prolate 3:1:1 | broadside | ethanol | 1.05 | 6 | 131 | 78.6 | 86.6 (HS) | -9.3 % | 97.8 (Ganser) | -19.7 % |
| prolate 3:1:1 | end-on | water | 1.05 | 0.5 | 0.369 | 1.54 | 1.56 (HS) | -1.2 % | 1.52 (Ganser) | +1.7 % |
| prolate 3:1:1 | end-on | water | 1.05 | 1 | 2.45 | 5.13 | 5.36 (HS) | -4.4 % | 4.92 (Ganser) | +4.3 % |
| prolate 3:1:1 | end-on | water | 1.05 | 2 | 13.2 | 13.8 | 15.3 (HS) | -9.7 % | 12.9 (Ganser) | +7.4 % |
| prolate 3:1:1 | end-on | water | 1.05 | 4 | 58.7 | 30.6 | 34.3 (HS) | -10.6 % | 27.5 (Ganser) | +11.4 % |
| prolate 3:1:1 | end-on | water | 1.05 | 6 | 132 | 46 | 49.8 (HS) | -7.7 % | 39.7 (Ganser) | +16.0 % |
| prolate 3:1:1 | end-on | water | 1.15 | 0.5 | 1 | 4.19 | 4.29 (HS) | -2.4 % | 4.07 (Ganser) | +2.9 % |
| prolate 3:1:1 | end-on | water | 1.15 | 1 | 6.02 | 12.6 | 13.6 (HS) | -7.2 % | 11.9 (Ganser) | +5.9 % |
| prolate 3:1:1 | end-on | water | 1.15 | 2 | 29.1 | 30.4 | 34.2 (HS) | -11.1 % | 27.8 (Ganser) | +9.2 % |
| prolate 3:1:1 | end-on | water | 1.15 | 4 | 120 | 62.8 | 68.4 (HS) | -8.1 % | 54.5 (Ganser) | +15.3 % |
| prolate 3:1:1 | end-on | water | 1.15 | 6 | 264 | 92 | 95 (HS) | -3.1 % | 74.5 (Ganser) | +23.5 % |
| prolate 3:1:1 | end-on | ethanol | 1.05 | 0.5 | 0.686 | 4.95 | 5.04 (HS) | -1.8 % | 4.84 (Ganser) | +2.4 % |
| prolate 3:1:1 | end-on | ethanol | 1.05 | 1 | 4.3 | 15.5 | 16.5 (HS) | -6.1 % | 14.7 (Ganser) | +5.3 % |
| prolate 3:1:1 | end-on | ethanol | 1.05 | 2 | 21.6 | 39 | 43.7 (HS) | -10.8 % | 35.9 (Ganser) | +8.5 % |
| prolate 3:1:1 | end-on | ethanol | 1.05 | 4 | 91.6 | 82.6 | 91.1 (HS) | -9.3 % | 72.7 (Ganser) | +13.5 % |
| prolate 3:1:1 | end-on | ethanol | 1.05 | 6 | 203 | 122 | 129 (HS) | -5.0 % | 102 (Ganser) | +20.1 % |
| oblate 1:1:0.3 | face-on | water | 1.05 | 0.5 | 0.708 | 2.12 | 2.19 (HS) | -3.0 % | 2.08 (Ganser) | +2.0 % |
| oblate 1:1:0.3 | face-on | water | 1.05 | 1 | 4.15 | 6.22 | 6.66 (HS) | -6.6 % | 6.29 (Ganser) | -1.2 % |
| oblate 1:1:0.3 | face-on | water | 1.05 | 2 | 18 | 13.5 | 15 (HS) | -9.9 % | 15.3 (Ganser) | -11.4 % |
| oblate 1:1:0.3 | face-on | water | 1.05 | 4 | 64 | 24 | 26.6 (HS) | -9.8 % | 30.7 (Ganser) | -21.8 % |
| oblate 1:1:0.3 | face-on | water | 1.05 | 6 | 129 | 32.3 | 34.9 (HS) | -7.6 % | 42.8 (Ganser) | -24.5 % |
| oblate 1:1:0.3 | face-on | water | 1.15 | 0.5 | 1.83 | 5.48 | 5.74 (HS) | -4.6 % | 5.41 (Ganser) | +1.3 % |
| oblate 1:1:0.3 | face-on | water | 1.15 | 1 | 9.15 | 13.7 | 15 (HS) | -8.6 % | 14.6 (Ganser) | -5.9 % |
| oblate 1:1:0.3 | face-on | water | 1.15 | 2 | 35.2 | 26.4 | 29.5 (HS) | -10.4 % | 31.9 (Ganser) | -17.4 % |
| oblate 1:1:0.3 | face-on | water | 1.15 | 4 | 119 | 44.6 | 48.5 (HS) | -7.9 % | 59 (Ganser) | -24.4 % |
| oblate 1:1:0.3 | face-on | water | 1.15 | 6 | 238 | 59.6 | 62.2 (HS) | -4.2 % | 77.8 (Ganser) | -23.4 % |
| oblate 1:1:0.3 | face-on | ethanol | 1.05 | 0.5 | 1.28 | 6.63 | 6.9 (HS) | -3.9 % | 6.52 (Ganser) | +1.8 % |
| oblate 1:1:0.3 | face-on | ethanol | 1.05 | 1 | 6.82 | 17.7 | 19.2 (HS) | -7.9 % | 18.4 (Ganser) | -3.8 % |
| oblate 1:1:0.3 | face-on | ethanol | 1.05 | 2 | 27.4 | 35.4 | 39.5 (HS) | -10.3 % | 41.8 (Ganser) | -15.2 % |
| oblate 1:1:0.3 | face-on | ethanol | 1.05 | 4 | 93.9 | 60.8 | 66.7 (HS) | -8.8 % | 79.8 (Ganser) | -23.7 % |
| oblate 1:1:0.3 | face-on | ethanol | 1.05 | 6 | 188 | 81.4 | 86.3 (HS) | -5.6 % | 107 (Ganser) | -24.2 % |
| oblate 1:1:0.3 | edge-on | water | 1.05 | 0.5 | 0.865 | 2.59 | 2.64 (HS) | -1.6 % | 2.48 (Ganser) | +4.7 % |
| oblate 1:1:0.3 | edge-on | water | 1.05 | 1 | 5.21 | 7.82 | 8.34 (HS) | -6.2 % | 7.16 (Ganser) | +9.2 % |
| oblate 1:1:0.3 | edge-on | water | 1.05 | 2 | 24.8 | 18.6 | 20.8 (HS) | -10.3 % | 16.6 (Ganser) | +12.0 % |
| oblate 1:1:0.3 | edge-on | water | 1.05 | 4 | 99.6 | 37.4 | 40.8 (HS) | -8.4 % | 32.4 (Ganser) | +15.4 % |
| oblate 1:1:0.3 | edge-on | water | 1.05 | 6 | 215 | 53.7 | 56 (HS) | -4.2 % | 44.1 (Ganser) | +21.7 % |
| oblate 1:1:0.3 | edge-on | water | 1.15 | 0.5 | 2.25 | 6.74 | 7 (HS) | -3.7 % | 6.3 (Ganser) | +7.1 % |
| oblate 1:1:0.3 | edge-on | water | 1.15 | 1 | 12 | 18 | 19.7 (HS) | -8.9 % | 16.2 (Ganser) | +10.9 % |
| oblate 1:1:0.3 | edge-on | water | 1.15 | 2 | 51.6 | 38.7 | 43.1 (HS) | -10.2 % | 34.2 (Ganser) | +13.2 % |
| oblate 1:1:0.3 | edge-on | water | 1.15 | 4 | 196 | 73.6 | 77.3 (HS) | -4.8 % | 61 (Ganser) | +20.7 % |
| oblate 1:1:0.3 | edge-on | water | 1.15 | 6 | 417 | 104 | 103 (HS) | +1.2 % | 78.8 (Ganser) | +32.1 % |
| oblate 1:1:0.3 | edge-on | ethanol | 1.05 | 0.5 | 1.57 | 8.13 | 8.36 (HS) | -2.8 % | 7.65 (Ganser) | +6.2 % |
| oblate 1:1:0.3 | edge-on | ethanol | 1.05 | 1 | 8.77 | 22.7 | 24.7 (HS) | -7.9 % | 20.6 (Ganser) | +10.3 % |
| oblate 1:1:0.3 | edge-on | ethanol | 1.05 | 2 | 39.2 | 50.7 | 56.7 (HS) | -10.5 % | 45.1 (Ganser) | +12.6 % |
| oblate 1:1:0.3 | edge-on | ethanol | 1.05 | 4 | 152 | 98.2 | 105 (HS) | -6.4 % | 83.1 (Ganser) | +18.2 % |
| oblate 1:1:0.3 | edge-on | ethanol | 1.05 | 6 | 323 | 140 | 141 (HS) | -1.0 % | 110 (Ganser) | +27.5 % |

Stokes limit (1000 x water's viscosity, 2 mm bodies, ρ_b 1.15):

| Shape | Orientation | Re | v sim mm/s | v closed form mm/s | Error |
|---|---|---|---|---|---|
| sphere | any | 0.00066 | 0.3310 | 0.3314 | -0.10 % |
| prolate 3:1:1 | broadside | 6.1e-05 | 0.06392 | 0.06393 | -0.02 % |
| prolate 3:1:1 | end-on | 7.5e-05 | 0.07861 | 0.07864 | -0.04 % |
| oblate 1:1:0.3 | face-on | 0.00015 | 0.1137 | 0.1137 | -0.03 % |
| oblate 1:1:0.3 | edge-on | 0.00019 | 0.1409 | 0.1410 | -0.07 % |
