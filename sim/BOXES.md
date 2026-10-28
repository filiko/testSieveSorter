# Each box on its own

Per-box session, 2026-10-27. The user: "the boxes are individually shaking it doesnt matter that theyre synced what matters is the sifting". So each tray box gets its own motion, with nothing locking it to its neighbours, and the optimizer searches for the motion and screens that sift best. Code: `boxes.py`, `screens.py`, small hooks in `sorter.py` and `designs_holder.py`, the `sift` study in `optimize.py`.

**The motion is kinematic.** Each box follows its prescribed path exactly. No actuator, motor, spring, mount or frame is modelled, so nothing here says whether a real actuator can drive a loaded box along that path.

**The sim ranks designs. It isn't calibrated, so it doesn't predict real percentages** (SYSTEM.md §5).

## What changed from the seesaw

| | seesaw (`rocking.py`, unchanged) | boxes (`boxes.py`) |
|---|---|---|
| tilt | one profile for the tower; neighbours locked in opposite phase | each level its own amplitude, period, shape and phase |
| vibration | one shared translation of the whole tower, applied as a pseudo-force | each level its own amplitude, frequency, direction and phase, through its own slide joints |
| joints per level | 1 (hinge about Y) | 4 (slides X, Y, Z in the lab, then the hinge about Y through the moved pivot) |
| frame | lab, plus the shared buzz frame | lab only (`tray_d` = 0) |
| clearance | over one cycle of the locked motion | over every combination of the levels' phases (a lower bound) |

## The motion model

Each holder box of an `inserts:` tower, the catch pan included, is one MuJoCo body. Its pivot is x = y = 0, half way up the box, as in `rocking.py`. Before every step, `boxes.py` writes every joint's `qpos` and `qvel` from the level's own motion. Time t counts from the end of the settle; nothing moves during the settle.

| quantity | formula |
|---|---|
| tilt, level k | θ_k(t) = e(t) · deg_k · f_k(t / period_s_k + phase_k) |
| profile f | `constant_speed`: a triangle wave with its reversals rounded over `ramp_s` (the same profile as `rocking.py`, to 4e-4); `sine`: sin 2πu. Both in [−1, 1], level and tipping +X down at u = 0 |
| vibration, level k | s_k(t) = e(t) · vib_mm_k · sin 2π(vib_hz_k t + vib_phase_k) · u_k |
| direction u_k | (cos a cos b, cos a sin b, sin a), a = `vib_angle_deg` (0 along X, 90 up), b = `vib_az_deg` |
| ease-in e(t) | smoothstep from 0 to 1 over `ramp_in_s`, so a box that starts mid-cycle doesn't jump |
| where a rest point x of level k is | s_k + p_k + R_y(θ_k)(x − p_k), p_k its pivot |

Two details keep the drive honest:
- **Feed-forward.** Writing `qvel` each step only gives a box a velocity jump between steps; the contact solve never sees it accelerate. So `drive()` also applies the generalized force (diagonal mass × prescribed acceleration) that gives each joint its prescribed acceleration during the step. Without it, the seesaw's motion replayed through the boxes leaked more rice than the seesaw itself (rice recovery 0.90 ± 0.04 against 0.98 ± 0.03, 8 seeds; Checks below). With it the two agree.
- **Gravity compensation.** Each level is 1e6 g with its mass on its pivot, so particles can't push it. `gravcomp` cancels its weight, so it doesn't sag between writes: without it the Z slide falls at g/2 within a step.

ASSUMED:
- the vibration direction is fixed in the lab, not in the tilted box (a box-mounted shaker at 12° of tilt would point 12° off);
- the pivot is half way up the box, as for the seesaw;
- tray-tray contacts are off (the trays are driven), so a touching config doesn't show in the physics; the clearance check flags it.

### Stroke options (`--stroke boxes:k=v,...`)

A per-level key takes one value for every level, or a slash list top to bottom with the catch pan last. `inserts:a,b` has 3 levels: a, b, catch.

| key | per | default | meaning |
|---|---|---|---|
| `deg` | level | 0 | tilt amplitude either side of level, degrees; 0 is no tilt |
| `period_s` | level | 2 | one tilt cycle, s |
| `shape` | level | `constant_speed` | `constant_speed` (constant angular speed, reversals rounded over `ramp_s`) or `sine` |
| `phase` | level | 0 | where in its tilt cycle the level starts, fraction of a cycle |
| `ramp_s` | level | 0.02 | reversal time of `constant_speed`, s |
| `vib_mm` | level | 0 | vibration amplitude, mm; 0 is off. Peak acceleration vib_mm · (2π vib_hz)² |
| `vib_hz` | level | 40 | vibration frequency, Hz |
| `vib_angle_deg` | level | 90 | vibration direction in the XZ plane: 0 along X (the tilt direction), 90 straight up |
| `vib_az_deg` | level | 0 | turns the vibration's horizontal part from X toward Y, degrees |
| `vib_phase` | level | 0 | where in its vibration cycle the level starts, fraction of a cycle |
| `ramp_in_s` | tower | 0.2 | ease every level in from rest over this long after the settle, s |

```
wsl: python sorter.py --design inserts:r2p85b1p15_across,s1p05x11p85b0p95_across,pitch=70,holder=seesaw \
    --mix insect_malaise_lt2=24,insect_malaise_2to6=24,insect_malaise_gt6=12 \
    --stroke boxes:deg=8/5/0,period_s=2/1.5/2,phase=0/0.33/0,vib_mm=0.3/0.4/0,vib_hz=40/60/40,vib_angle_deg=90/60/90 \
    --duration 12 --dt 0.000125 --timeconst 0.00025 --out out/runs/boxes
```

### Recording and the replay

- `traj.npz` → `level_q` (frames × levels × 4, w x y z) as for the seesaw, plus **`level_p`** (frames × levels × 3, mm): each level body's origin in the lab. A rest point x of level k is drawn at `level_p[k] + R(level_q[k]) x`.
- `scene.json` → `levels[k]` as for the seesaw, plus `motion` (that level's stroke options).
- `results.json` → `boxes`: the per-level motion, the peak acceleration of each vibration (`vib_peak_g`), the pitch and the clearance check.
- `viewer.py` and `viewer_template.html` read `level_p` when it's there, and fall back to turning each level about its pivot when it isn't, so seesaw replays draw as before. The zone boxes are drawn at rest; the sim tests each zone in its own level's moving frame (`rocking.Seesaw.zone_frames`, which uses the body's position as well as its turn).
- **Checked in headless Chrome** (`record_view.Page`) on a run with exaggerated slow motion (top box ±10° plus 6 mm at 1 Hz along X; catch pan 5 mm at 1.5 Hz up and down). At t = 1.25 s and 1.75 s the top box has the same 5° tilt and sits 12 mm apart along X; the middle box has changed its tilt; the catch pan sits 3.5 mm higher than at rest.

## Do neighbouring boxes touch?

With independent actuators the levels' phases drift, so over a long run every combination of phases comes up. `boxes.clearance()` doesn't sample time. It poses each pair of neighbours at every combination of their two tilts, on a 9 × 9 grid from −deg to +deg with the ends included, and takes MuJoCo's closest distance (`mj_geomDistance`) between the two boxes' frame, wall and floor geoms. The screens sit inside the boxes and the lids are invisible, so both are left out. Then the vibrations can move the two boxes together by at most vib_mm_k + vib_mm_k+1 (triangle inequality), and that is subtracted.

So `min_mm` is a **lower bound over any phases**. Every run reports it, and prints `TOUCHING` at or under 0.

| tower (ribs-across inserts, `holder=seesaw`) | motion | closest, mm | note |
|---|---|---|---|
| pitch 55 | ±10° on every level, no vibration | 6.07 | the same as `rocking.py`'s locked seesaw, whose opposite-phase pose is the worst case |
| pitch 55 | the same, 41 × 41 grid | 6.07 | the gap closes monotonically toward full opposite tilts, so the grid's corners set it |
| pitch 55 | ±10°, 0.3 mm on every level | 5.47 | 6.07 − 0.6 |
| pitch 55 | screens ±12°, 1 mm each, catch still | −0.56 | TOUCHING; 58.6 mm pitch for 3 mm clear, touching below 55.7 mm |

The `pitch_needed` equivalent is `boxes.pitch_needed(spec, stroke, clear_mm)`, a bisection on the bound. At ±10° with no vibration it gives 48.96 mm to touch and 52.04 mm for 3 mm clear, the same as `rocking.py`.

```
wsl: python boxes.py inserts:h2p85b1p15_across,h1p45b1p15_across,pitch=55,holder=seesaw --stroke deg=12/12/0,vib_mm=1/1/0 --clear 3
```

## Screens: round holes and slots (`screens.py`)

A square hole passes a flat item corner to corner: a 2 mm square is 2.83 mm across its diagonal. That's why rice leaks through the 2 mm tray. Two more screen kinds, for any level of an `inserts:` tower, on either frame:

| spec | screen | ideal-zone rule | geoms |
|---|---|---|---|
| `h<hole>b<bar>[_across]` | square holes (unchanged) | fits the square at its best tilt | one bar per row and column |
| `r<hole>b<bar>[_across]` | round holes on a square grid, modelled as **regular octagons** `<hole>` across the flats: 1.082 × hole corner to corner, against 1.414 × for a square | fits the octagon at its best turn (`screens.fits_round`) | the square grid's bars, plus a box turned 45° about Z at every node, whose four edges are the four holes' corner cuts, and a small one at each hole corner on the window edge: about one box per hole |
| `s<width>x<length>b<bar>[_across]` | slots along X (the tilt direction), square ends | thickness ≤ width (as the existing `slot` rule) | one bar per row and column |

Sizes are as modelled, with p for the point, as for `h<hole>b<bar>`. The screen is 1.6 mm thick for openings of 3 mm and up, else 1.4. The octagon is an ASSUMED stand-in for a round hole: MuJoCo collides convex pieces, and a plate with round holes isn't convex. The corner fills have no relief taper; the top surface is still the narrowest section.

Checked by probing the top surface on a 41 × 41 grid around an interior hole, a window-corner hole and a window-edge hole, for 1.05, 2.85 and 4.35 mm holes (the last with corner cuts wider than its 0.95 mm bars): none of 15,129 points disagrees with the octagon beyond 0.01 mm of its edge. The corner fills are boxes rather than convex meshes because legs are capsules, which MuJoCo collides with boxes analytically: that cut a round-hole insect run from 110 s to 98 s.

Every level's opening is free, so a tower of 3–5 levels (2–4 screens and the catch pan) can have any sizes and any mix of kinds. Builds: `inserts:r4p85b1p35_across,h2p25b1p15_across,s1p6x12b1p0_across,r1p25b0p95_across,pitch=60,holder=seesaw` (5 levels) has 2,927 geoms and compiles in 0.1 s. The finest round screen the search allows, `r0p55b0p95`, has about 4,800 geoms per insert and compiles in 0.4 s.

## Checks

| check | result |
|---|---|
| **Regression: `--stroke seesaw:` unchanged.** `inserts:5mm_across,2mm_across,pitch=55,holder=seesaw`, pasta 6 / rice 10 / quinoa 10, `seesaw:deg=10,period_s=2,vib_mm=0.3,vib_hz=40`, 3 s, dt 0.125 ms, seed 3, run on `main`'s code and on this branch | **bitwise identical**: every `traj.npz` array, `scene.json`, and `results.json` but the wall time. A translation run (`inserts:5mm,h1p85b1p15,pitch=65`, sine 20 Hz up) is identical too |
| Old optimizer studies (demo, insects, seesaw, smoke): cache keys, set labels and scores, HEAD's `optimize.py` against this branch's, on every reference and 9 proposals per study at 5 fidelities | 2,745 jobs: identical keys and tags; `run_score` identical |
| Profile: `boxes` tilt against `rocking.profile` | `constant_speed` with 0.02 s reversals: within 4.5e-4 (the box filter's discretization); without reversals, and `sine`: exact |
| `qvel` and the feed-forward acceleration against finite differences of `qpos` and `qvel` | within 0.3% of peak, except single steps at the profile's corners |
| The seesaw's motion reproduced by boxes (`phase=0/0.5/0`, `ramp_in_s=0`, the buzz on every level in sync), 5 mm / 2 mm ribs-across trays, pasta 8 / rice 14 / quinoa 14, 6 s | 0.3 mm at 40 Hz up, 8 seeds: rice recovery 0.98 ± 0.03 (seesaw) and 0.98 ± 0.03 (boxes). 0.4 mm at 48 Hz, 30° up, 16 seeds: 0.37 ± 0.17 and 0.36 ± 0.13. Pasta and quinoa within 0.01 |
| Cost of the box drive | 2–10% more wall time per step than the seesaw on the same grain run (the four joints per level, and the motion evaluated 4,096 steps at a time) |
| **Cost of an insect tower** (60 stratified Malaise specimens, 12 s + 1 s settle, dt 0.125 ms, one core, 2–3 runs at once) | square / square screens 55–60 s; round / round 98 s (110 s with meshed corner fills); round / slot 89 s (meshed). Round holes cost about 1.8× square |

## The optimizer: the `sift` study

`python optimize.py run --study sift` searches separate trays with each box moving on its own, on the real Malaise mix (EXPLORATORY: the insects are generated, see INSECT_AUDIT.md).

- **Mix and classes.** `insects.MALAISE_MIX_STRATIFIED`: 24 specimens under 2 mm, 24 at 2–6 mm, 12 over 6 mm, in BugPicker's body-length classes (the `insects` study's). Screen 1 should hold > 6 mm, screen 2 the 2–6 mm, the catch the rest.
- **Weighted to the real mix.** Each class's row of the count matrix is weighted to its real share (`insects.MALAISE_SHARES`: 71.0 / 26.6 / 2.4%), so purity, jammed and lost are what a real sample would see. Recovery is within a class, so weights don't change it.
- **Design.** `inserts:<L1>,<L2>,pitch=<P>,holder=seesaw` on the ribs-across frame. Per screen: square, round or slot; the opening; the bar. Slots are 12 mm long (ASSUMED, from LAYERS.md's wild-rice note; not searched).
- **Motion per screen box.** The catch pan stays still.

| parameter | range | step | note |
|---|---|---|---|
| `shape1`, `shape2` | square / round / slot | | |
| `a1` | 1.8–7.0 mm | 0.1 | nominal; the sim builds nominal − 0.15. Widened from 1.8–4.5 on Oct 27: wet specimens lie flat and holes cut by body length (ENTOSIEVE.md), so the > 6 mm cut can need a hole near 5–6 mm |
| `a2` | 0.7–2.6 mm | 0.1 | widened from 0.7–1.9, for the same reason (the 2 mm cut) |
| `bar1`, `bar2` | 0.8–2.0, 0.8–1.6 mm | 0.1 | nominal; the sim builds + 0.15 |
| `pitch` | 55–110 mm | 5 | |
| `tshape` | constant_speed / sine | | one tilt profile for both boxes |
| `tilt1`, `tilt2` | none / tilt | | "no tilt" is a choice of its own |
| `deg1`, `deg2` | 2–12° | 0.5 | used when tilting |
| `period1`, `period2` | 0.5–6 s | 0.1 | |
| `vib_g1`, `vib_g2` | 0–10 g | 0.1 | peak acceleration; the amplitude follows: vib_mm = vib_g · g / (2π vib_hz)² |
| `vib_hz1`, `vib_hz2` | 15–120 Hz | 1 | |
| `vib_angle1`, `vib_angle2` | 0–90° | 5 | 0 along X, 90 straight up |

- **Constraints** (a draw that breaks one is redrawn):
  - opening 1 at least 0.3 mm above opening 2;
  - bars at least 0.8 mm (two print lines);
  - vibration amplitude ≤ 1.0 mm (the brief's actuator stroke);
  - peak acceleration ≤ 10 g. ASSUMED: what one small actuator gives a box. Searching vib_mm and vib_hz on their own put 60% of draws over it, hence the vib_g parameter;
  - neighbouring boxes at least 3 mm apart at every phase combination (`boxes.clearance`, ASSUMED margin). A run whose boxes can touch also fails in the child.
- **Robustness.** Every candidate runs on every friction set (0.3 / 0.4 / 0.5) × every liquid set × the seeds; ranked by mean − sd, as the other studies. **Each seed draws its own phase for every box's tilt and vibration** (fixed by the seed, so runs repeat): independent actuators don't hold a phase, so a design must sift whatever the phases.
- **Wet, the way BugSorter runs.** The trays are in air. The specimens start fully wet, straight out of the sample's ethanol (`spray.py` `wet0` = 1), and the design's two fixed jets spray ethanol from 60 mm above the top screen. Wet specimens cling to the screens and to each other (capillary adhesion), and how hard is unknown, so every candidate runs at a light cling (`adhesion_scale` 0.1) and a strong one (0.5): `STUDIES["sift"]["liquid_sets"]`, each set multiplying the runs. Not under a bath: submerged, the < 2 mm specimens sink at about 1.4 mm/s and a 12 s run would only measure sinking ([LIQUID.md](LIQUID.md), "A bath is slow"). A set can be a `RunConfig.liquid` dict, None (dry) or `{"cfg": {RunConfig fields}}`; override with `--liquid-sets '<json>'`. Cache keys leave out a `liquid` of None, so no earlier study's cache changed. Wet runs cost about 2.2× a dry one (16 s of wall per simulated second, 4 at a time).
- **References.** LAYERS.md's insect-cut trays (square 3.0 / 1.6 nominal, 55 mm apart) with each box rocking ±10° at 2 s plus its own 1.9 g, 40 Hz buzz; the same with no tilt; the same with round holes; round holes at the body-length cuts, as EntoSieve's plates (5.0 / 2.0); and **COUPLED**: the same trays on `rocking.py`'s seesaw (neighbours locked, catch pan rocking, one shared buzz).
- **Budget.** Screen 6 s on 1 seed, full 12 s on 2 seeds, at dt 0.125 ms and contact time constant 0.25 ms (insects need the stiff contacts). Round 0: 16 Latin-hypercube candidates and 4 references; later rounds 10 cross-entropy candidates.

## The dry pilot

`python optimize.py run --study sift_pilot --rounds 1 --workers 8`: the sift study cut down to a 2 s screen and a 4 s full run on 1 seed, with 6 Latin-hypercube candidates, 2 references and COUPLED. Dry. 42 runs, 2 min on 8 workers. **A pilot, not a result:** 4 s is too short for insects to work through two trays. Leaderboard: `opt/leaderboard_sift_pilot.md`; the log entry: `opt/LOG.md`, "sift_pilot round 0".

What it proved:

| step | what happened |
|---|---|
| proposals | of 40 test draws, 29 pass the constraints; 10 need more than the 1 mm stroke and 1 has its openings in the wrong order. The clearance check costs about 35 ms per new pitch and tilt combination, cached |
| child runs | boxes strokes with each seed's own phases; COUPLED on the old seesaw path; square, round and slot screens on both levels |
| scoring | weighted purity, leaderboard, count matrices, winners, state and the auto log entry |
| failures | 1 of 42 runs went unstable (Known issues), scored −1 as in every study |

What the numbers say (4 s, 3 runs each; direction only):

| candidate | robust | > 6 mm pur / rec | 2–6 mm pur / rec | < 2 mm pur / rec |
|---|---|---|---|---|
| S-2997a7b5: square 3.0 / 1.6, no tilt, each box its own 1.9 g buzz | 0.087 | 19% / 100% | 40% / 39% | 99% / 67% |
| S-88c31ccf: slot 3.8 / round 1.1, 55 mm | 0.081 | 18% / 86% | 33% / 79% | 100% / 22% |
| C-1cfae593: COUPLED, the same trays on the old seesaw | 0.069 | 20% / 100% | 49% / 39% | 99% / 67% |
| S-71d846e7: the same trays, each box ±10° plus its own buzz, phases free | 0.064 | 19% / 100% | 50% / 51% | 99% / 68% |
| S-10cb4529: round 4.3 / slot 1.4, 105 mm | 0.035 | 15% / 100% | 59% / 31% | 98% / 79% |

- Every design keeps the > 6 mm specimens on tray 1 (31–36 of 36), and tray 1 also keeps 15–28 of the 72 specimens of 2–6 mm. Weighted to the real mix, that bin is only 15–20% > 6 mm, because 2–6 mm specimens are 11 times as common. So the first cut sets the score, and the full study should work on tray 1.
- Up to a third of the 2–6 mm specimens end `between`: sunk into a tray's holes, legs caught (as LAYERS.md saw).
- Independent boxes and the coupled seesaw score the same at 4 s (0.064 and 0.069), within the noise of 3 runs.

**Cost per run** under 8 workers: 5.1–10.8 s of wall per simulated second, mean 7.2 (square / square 6.7, the coupled seesaw 6.2, the highest with a round-hole tray). So a full sift run (12 s plus the 1 s settle) takes about 1.5 min with square screens and up to about 2.3 min with fine round holes. `optimize.py plan` uses the mean.

## Running the full study (after the liquid branch merges)

Put the liquid's uncertain parameters in `STUDIES["sift"]["liquid_sets"]` (labels and `RunConfig.liquid` dicts with `sim/liquid.py`'s keys), or pass them on every command:

```
wsl: cd sim
python optimize.py plan --study sift --workers 8 --liquid-sets '[["dry", null], ["<label>", {<RunConfig.liquid>}], ...]'
python optimize.py run --study sift --rounds 5 --workers 8 --liquid-sets '<the same>'
```

| liquid sets | round 0 (20 candidates) | each later round (10) | 5 rounds |
|---|---|---|---|
| 1 (dry) | 2.1 CPU-hours, 16 min on 8 workers | 0.7 CPU-hours, 5 min | 5 CPU-hours, about 40 min |
| 4 (e.g. 2 bath levels × 2 `entrain`) | 8.4 CPU-hours, 63 min | 2.9 CPU-hours, 22 min | 20 CPU-hours, about 2.5 h |

These are at 7.2 s of wall per simulated second, before whatever the liquid adds per step. Check memory first (`free -g`, back off under 3 GB free).

## Known issues

- **Small specimens can spin up and blow up.** Two cases, both a specimen's own spin, not the box drive:
  - a 0.3 mm specimen (the Malaise fit's floor: 1.3 µg, inertia 1e-8 g mm², legs at the 0.06 mm stability floor) landed in the catch pan, which wasn't moving, spinning at about 4,000 rad/s. That is 0.5 rad per 0.125 ms step, and the integrator blew up 0.05 s later (a test run with square 2.85 / 1.05 mm trays, seed 1);
  - a 1.45 mm long-legged specimen on the finest round-hole tray (0.65 mm) reached 94,000 rad/s under a mild 2.1 g buzz (1 of the pilot's 42 runs).

  MuJoCo resets the state and the run is invalid. The optimizer scores it −1, as in every study, so it adds noise unrelated to the design. Liquid drag should stop such spins once the liquid branch is in. Otherwise: a smaller dt, or a floor above 0.3 mm in `insects.MALAISE_KINDS` (the physics session's call).
- The vibration direction is fixed in the lab; the octagon stands in for a round hole; slots are 12 mm; the catch pan is still in the search; 10 g and 3 mm are assumed limits. All ASSUMED, all easy to change in `optimize.py`.
- The sift family has two screens, one per class boundary. `inserts:` takes 2–4 screens with any sizes, but the scoring maps one bin per class; a tower with more screens than boundaries would need a bin-to-class map first.
- Don't edit `optimize.py` while a study runs: each run's child process imports it afresh. The pilot's first attempt lost 7 full runs that way; they were deleted from the cache and rerun.
- SYSTEM.md §3 still says neighbours alternate. The user's note above supersedes that for the motion; SYSTEM.md is the main session's to update.
