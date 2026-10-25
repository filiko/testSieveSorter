# Vertical and angled strokes on the demo tray

Physics session, 2026-10-25. Task: `docs/sessions/demo-rig.md` parts A and B. Raw runs are in `sim\out\sweeps\vertical*\` (gitignored); each folder has `report.html` and `summary.csv`.

## What changed

- **`angle_deg` on the stroke** (`sorter.py`, function `stroke_axis`). 0 means along the design's flow axis, which is the old behaviour. 90 means straight up. Anything in between is an angled throw, as in lab vibratory sieve shakers. It works anywhere a stroke dict goes:
  - CLI: `--stroke sine:amp_mm=1.24,freq_hz=20,angle_deg=90`
  - Python, sweeps and the optimizer: `{"profile": "sine", "amp_mm": 1.24, "freq_hz": 20, "angle_deg": 45}`
  - `stroke["axis"]` (a 3-vector) still works from Python. Giving both is an error.

  The tray-frame gravity is `-a(t)*axis - g*z`, which is exact for any translation of the tray. So a vertical stroke only needs the axis; nothing else changed.
- **The demo tray is `inserts:5mm`**: one holder box with the 5 mm printed square-hole insert (`cad/sieve_insert.py`), on a catch pan. Zones are `on_5mm` (pasta should stay here) and `catch` (rice should end here). It already built; nothing was added.
- **`sweep.py vertical`**: the comparison below. `--mix` overrides the demo mix; `--quick` runs 2 seeds of 2 s.
- **Only the tray, the grains and the stroke are modelled.** The DeWalt tool isn't: no geometry, motor or hand dynamics. It's just what moves the tray.

## Assumptions (not measurements)

| | Value | Why |
|---|---|---|
| Profile | sine, 20 Hz | A smooth throw, like a vibratory sieve shaker (those run at about 50 Hz, 1–3 mm). The tool's real motion at the tray is unknown, and Forum's clip shows the tool idle. |
| Peak acceleration | 2 g and 4 g | Above 1 g a vertical stroke throws the grains off the screen. 2–4 g is the usual sieve-shaker range. |
| Amplitude | 1.24 mm (2 g), 2.48 mm (4 g) | `amp = peak * g / (2 pi f)^2` |
| Equal peak acceleration across directions | yes | Within a block, every direction gets the same sine, so any difference comes from the direction. |
| Demo mix | pasta (ditalini) 15 + rice 40 | Forum's photos. The heavy load (pasta 30 + rice 150) is the heap seen in IMG_1315. |
| Dark grains | not modelled | Colour doesn't matter to the sim. If they're wild rice (long and thin, about 1.5–2 mm thick), they pass a 5 mm hole like rice. |
| Grain sizes | `grains.py` typical values | rice 6.5 x 2.0 x 1.7 mm; ditalini 6.5 mm across x 6.0 mm long. Not yet caliper-measured. |
| Contact | dt 0.25 ms, timeconst 0.5 ms; friction 0.3 / 0.4 / 0.5 | Production settings. There's no `calibration.json` yet, so the three friction sets are the defaults. |
| Run | 1 s settle, then 10 s shake, 6 seeds per friction set | 108 runs |

## Result: demo tray, demo mix (pasta 15 + rice 40)

Every one of the 108 runs ends with **pasta 1.00 and rice 1.00 recovery**, with no jams, no losses, no contamination and no unstable resets. The 5 mm holes leave a lot of room either way: rice is about 2 mm across, and ditalini are at least 6 mm, which is over 1 mm too big for the hole at any tilt. So direction can only show up in speed and contact overlap.

t50 and t90 are seconds from the start of the shake until 50% / 90% of the rice is in the catch. Values are means over 18 runs (6 seeds x 3 friction sets). "Overlap" is the largest particle-into-tray overlap per run, as a mean.

| Peak accel. | Direction | t50 rice | t90 rice (sd) | t90 at friction 0.3 / 0.4 / 0.5 | Overlap, tray | Overlap, particle-particle |
|---|---|---|---|---|---|---|
| 2 g | 0° along the flow axis | 0.03 s | **0.21 s** (0.02) | 0.22 / 0.20 / 0.20 | 0.14 mm | 0.05 mm |
| 2 g | 45° throw | 0.03 s | 0.28 s (0.06) | 0.28 / 0.28 / 0.27 | 0.14 mm | 0.13 mm |
| 2 g | 90° straight up | 0.09 s | 0.62 s (0.12) | 0.60 / 0.58 / 0.67 | 0.17 mm | 0.13 mm |
| 4 g | 0° along the flow axis | 0.04 s | **0.33 s** (0.08) | 0.35 / 0.32 / 0.33 | 0.14 mm | 0.10 mm |
| 4 g | 45° throw | 0.06 s | 0.93 s (0.43) | 0.78 / 0.90 / 1.10 | 0.22 mm | 0.22 mm |
| 4 g | 90° straight up | 0.07 s | 0.71 s (0.26) | 0.65 / 0.62 / 0.85 | 0.24 mm | 0.19 mm |

What this says:
1. **On the demo tray, the shake direction doesn't change the outcome.** Every direction sorts perfectly within about 1 s. Most rice falls through during the 1 s settle, before the shake starts, which is why t50 is near 0. The demo insert is very forgiving for pasta vs rice.
2. **Along the flow axis is fastest at clearing the last rice:** 2–3x quicker t90 than vertical at the same peak acceleration, and the least sensitive to friction. Sliding sweeps stray rice grains over holes. A vertical throw lifts them and drops them back about where they were.
3. **More acceleration doesn't help here:** at 4 g the 45° and 90° strokes get slower and more spread (t90 sd 0.26–0.43 s), because grains spend longer in the air.
4. **Vertical strokes press harder into the tray:** the overlap is 0.22–0.24 mm at 4 g, against 0.14 mm for horizontal. That's harmless on the 5 mm demo insert. For tight gates, see Stability below.
5. **Answer for the demo:** up-and-down shaking (as in the video) works for pasta vs rice on the 5 mm insert. It's just slower to clear the last grains than shaking along the tray. If the demo shows the motion from the video, the sim agrees it will sort.

## Result: heavy load (pasta 30 + rice 150)

The heap from Forum's IMG_1315: 180 particles, 1 s settle + 5 s shake, 4 seeds x 3 friction sets = 12 runs per row, 72 runs in all. There were 0 resets and 0 errors.

| Peak accel. | Direction | Recovery rice / pasta | t90 rice (sd) | t90 at friction 0.3 / 0.4 / 0.5 | Rice left on the screen (contamination of `on_5mm`) | Stuck in holes (`between`, per run) | Overlap tray / particle-particle |
|---|---|---|---|---|---|---|---|
| 2 g | 0° | 1.00 / 1.00 | **0.23 s** (0.05) | 0.23 / 0.25 / 0.23 | 0.00 | 0.00 | 0.18 / 0.13 mm |
| 2 g | 45° | 0.99 / 1.00 | 0.35 s (0.10) | 0.30 / 0.33 / 0.42 | 0.04 | 0.00 | 0.17 / 0.14 mm |
| 2 g | 90° | 1.00 / 1.00 | 0.59 s (0.07) | 0.60 / 0.57 / 0.60 | 0.00 | 0.00 | 0.18 / 0.17 mm |
| 4 g | 0° | 1.00 / 1.00 | **0.40 s** (0.04) | 0.38 / 0.42 / 0.40 | 0.00 | 0.00 | 0.18 / 0.13 mm |
| 4 g | 45° | 0.99 / 1.00 | 1.06 s (0.40) | 0.93 / 0.85 / 1.40 | 0.03 | 0.00 | 0.21 / 0.24 mm |
| 4 g | 90° | 1.00 / 1.00 | 0.83 s (0.13) | 0.78 / 0.75 / 0.97 | 0.01 | 0.08 | 0.25 / 0.26 mm |

Four times the load gives the same ranking, with the first imperfections:
- **Along the flow axis** stays perfect and fastest, and is barely slowed by the bigger heap (t90 0.23 s against 0.21 s).
- **The 45° throw leaves about 1% of the rice on the screen** with the pasta after 5 s. A likely cause, not checked frame by frame, is that grains thrown forward and up keep landing back in the pasta layer. It's also the most friction-sensitive stroke (t90 0.85–1.40 s at 4 g).
- **Straight up at 4 g** occasionally wedges a rice grain in a hole (0.08 per run) and has the highest overlap.

So the answer holds: **direction doesn't decide whether the demo sorts, but along the tray is the best stroke for it.** Up-and-down shaking works, at 2–3x the time to clear the last rice. A 45° throw is the worst choice for this insert.

## Stability under vertical impacts

Probe: `instab.py`. The run stops at the first MuJoCo state reset, and the per-run maximum overlap is recorded. **0 resets in 840 runs**:
- 384 runs with the old horizontal stroke across 4 designs x 3 mixes x 4 solver settings. These used the first version of the probe, which watched only the QACC warning; the other 456 runs catch any reset.
- 360 runs with vertical 2/4/8 g, a 45° 4 g throw and the horizontal baseline, on `inserts:5mm`, `inserts:mesh5,mesh2` and `pool:w5p0,t1p4` (the 1.4 mm tunnel, 0.3 mm quinoa clearance), with the demo and insect mixes;
- 96 runs of vertical strokes with stiffer contacts.

Vertical strokes don't go unstable, but they push contacts deeper. Median per-run maximum overlap with the tray (8 runs per cell, demo and insect mixes):

| Stroke | dt 0.5 ms, tc 2 ms (old default) | dt 0.25 ms, tc 0.5 ms (production) | dt 0.125 ms, tc 0.5 ms | dt 0.125 ms, tc 0.25 ms | dt 0.0625 ms, tc 0.125 ms |
|---|---|---|---|---|---|
| horizontal firmware, 50 mm/s | 0.47 | 0.10 | 0.10 | | |
| vertical 2 g | 0.44–0.75 | 0.15–0.19 | 0.12–0.15 | 0.08 | 0.04–0.05 |
| vertical 4 g | 0.89–0.96 | 0.22–0.27 (p90 up to 0.74) | 0.19 | 0.12–0.13 | 0.06–0.08 |
| vertical 8 g | 1.55 | 0.47 | 0.42 | | |

- **The contact time constant controls the overlap, not dt.** Halving dt at the same tc barely helps. tc has to stay at least 2 dt, so stiffer contacts cost a smaller dt.
- **Cost:** each halving of dt costs about 2.3–2.7x wall time (run alone: 8.4 s to 22.6 s per 3 s demo run at 4 g).
- **Recommendation:**
  - The demo tray (`inserts:5mm`, at least 1 mm of slack) and mesh or rice-scale gates are fine at production settings (dt 0.25 ms, tc 0.5 ms).
  - Tight gates, where the clearance is about 0.3 mm or less (the 1.4 mm tunnel for quinoa), need **dt 0.125 ms, tc 0.25 ms** for vertical strokes up to 4 g. That brings the median overlap to about 0.12 mm, at about 2.5x the runtime.
  - Never use the old default (0.5 ms / 2 ms) with vertical strokes: about 1 mm of overlap would let grains squeeze through gates they can't pass.
  - 8 g is too violent for tight gates at any setting tried.
- **Unstable runs are no longer silent:** each MuJoCo reset is listed in `results["unstable_resets"]`, `sorter.py` prints `UNSTABLE`, and the sweep log tags the run (see `PERF.md`).

## Reproduce (from `sim\` in the WSL venv; see `docs/sessions/README.md`)

```
python sweep.py vertical --dt 0.00025 --timeconst 0.0005
python sweep.py vertical --mix pasta=30,rice=150 --seeds 4 --duration 5 --dt 0.00025 --timeconst 0.0005 --name vertical_heavy
python instab.py --seeds 4 --duration 2 --designs "inserts:5mm;inserts:mesh5,mesh2;pool:w5p0,t1p4" --mixes demo,insects70 \
  --strokes "sine:amp_mm=1.242,freq_hz=20,angle_deg=90;sine:amp_mm=2.485,freq_hz=20,angle_deg=90;sine:amp_mm=4.970,freq_hz=20,angle_deg=90;sine:amp_mm=2.485,freq_hz=20,angle_deg=45;constant_speed:amp_mm=10,speed_mm_s=50,ramp_s=0.01" \
  --solver "0.0005,0.002;0.00025,0.0005;0.000125,0.0005" --out out/instab/vertical.jsonl
python sorter.py --design inserts:5mm --mix pasta=15,rice=40 --stroke sine:amp_mm=1.24,freq_hz=20,angle_deg=90 \
  --duration 10 --dt 0.00025 --timeconst 0.0005 --out out/runs/demo_vertical     (a run for the viewer)
```

## For the optimizer

- `angle_deg` from 0 to 90 is a plain stroke key, so it can go into the search space next to `amp_mm` and `freq_hz`.
- Compare at equal peak acceleration (`amp * (2 pi f)^2`), or the angle gets confounded with how hard the tray is shaken.
- If a candidate has a gate clearance under about 0.3 mm and a vertical component, run it at dt 0.125 ms / tc 0.25 ms. Check `results["unstable_resets"]` and drop or flag any run that has resets.
- The demo baseline (`inserts:5mm`, pasta + rice) is saturated at recovery 1.00. Rank on t90 there, or use a harder mix.
