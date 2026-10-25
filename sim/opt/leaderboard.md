# Leaderboard: Demo set: surrogate grains (pasta + chickpea / rice / quinoa)

Generated 2026-10-25 08:04 by `sim/optimize.py` (study `demo`). 136 candidates, 1593 sim runs so far.

**The sim ranks designs; it does not predict real percentages.** It is uncalibrated until `calibrate.py` has bench counts, has no water, rigid particles, and about 80 particles per run. Sizes are simulated at the as-printed opening, nominal - 0.15 mm (ASSUMED until the hole gauge is measured).

Ranked by the robust score (mean - 1 sd) over 3 friction sets x 3 seeds at the full 30 s run. Score per run = min over classes of min(purity, recovery), minus 0.5 x jammed share, 1.0 x lost share and 0.05 x t90/duration. Failed (unstable) runs score -1. Only candidates promoted to the full run are ranked; screened-only ones are in the log. Solver: dt 0.25 ms, contact timeconst 0.5 ms (stiffer than sorter.py's default; see optimize.py). Friction sets: mu 0.3, mu 0.4, mu 0.5.

| # | id | family | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | design (CAD, nominal mm) | sim spec (as printed) | stroke |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | P-ae394887 | plinko | **0.999** | 0.999 +/- 0.000 | 0.999 | 100% / 100% | 100% / 100% | 100% / 100% | 0.0 | 0.0 | 0.4 (9/9) | PEN 1/9 (clr 0.26, pen 0.153) | rods L1 gap 3.7 (rod 2.6 wide, 1.6 tall) / L2 gap 1.5 (rod 1.8, 2.4) | `plinko` | tool sine 48 Hz, 2.2 g (0.24 mm), 20 deg up |
| 2 | P-668db784 | plinko | **0.998** | 0.998 +/- 0.000 | 0.998 | 100% / 100% | 100% / 100% | 100% / 100% | 0.0 | 0.0 | 0.9 (9/9) | PEN 3/9 (clr 0.24, pen 0.205) | rods L1 gap 3.5 (rod 3.7 wide, 2 tall) / L2 gap 1.6 (rod 2.9, 2.2) | `plinko` | tool sine 14 Hz, 2.0 g (2.54 mm), along the tray |
| 3 | G-060cecb0 | gated_mid | **0.955** | 0.972 +/- 0.017 | 0.965 | 100% / 100% | 100% / 99% | 99% / 100% | 0.0 | 0.0 | 7.8 (9/9) | PEN 9/9 (clr 0.04, pen 0.130) | L1 w3.1x3.1 / L2 t1.8; slope 0.3 deg, tunnel width 8.3, tooth 1.1, L1 gate at x 31.8 with slot 7.4, L2 at x 53, unflipped | `gated:0.3,w2p95x2p95,t1p65,tw=8.15,tooth=1.25,slot=7.4/7,gx=31.8/53,flip=0` | tool sine 28 Hz, 4.3 g (1.36 mm), 10 deg up |
| 4 | P-547508e5 | plinko | **0.937** | 0.966 +/- 0.029 | 0.966 | 100% / 100% | 100% / 97% | 97% / 100% | 0.0 | 0.0 | 0.5 (9/9) | PEN 1/9 (clr 0.14, pen 0.098) | rods L1 gap 3.1 (rod 2.8 wide, 1.8 tall) / L2 gap 1.7 (rod 2.3, 1.8) | `plinko` | tool sine 46 Hz, 1.3 g (0.15 mm), 35 deg up |
| 5 | P-ba5dd6b3 | plinko | **0.929** | 0.960 +/- 0.031 | 0.929 | 99% / 100% | 97% / 100% | 100% / 97% | 0.0 | 0.0 | 2.2 (9/9) | ok | rods L1 gap 5.6 (rod 1.8 wide, 2.6 tall) / L2 gap 1.6 (rod 2.2, 2.8) | `plinko` | firmware 9.5 mm at 47 mm/s, 5 deg up |
| 6 | P-63092ca9 | plinko | **0.915** | 0.953 +/- 0.038 | 0.918 | 99% / 100% | 96% / 100% | 100% / 96% | 0.0 | 0.0 | 1.7 (9/9) | ok | rods L1 gap 5.6 (rod 2.1 wide, 2.6 tall) / L2 gap 1.6 (rod 1.6, 3.4) | `plinko` | firmware 10 mm at 50 mm/s, along the tray |
| 7 | P-cbe7dbec | plinko | **0.891** | 0.929 +/- 0.038 | 0.913 | 99% / 100% | 97% / 97% | 97% / 96% | 0.0 | 0.0 | 4.1 (9/9) | ok | rods L1 gap 5.1 (rod 1.4 wide, 1.6 tall) / L2 gap 1.7 (rod 1.9, 3.2) | `plinko` | firmware 14 mm at 41 mm/s, along the tray |
| 8 | P-7e49fbec | plinko | **0.860** | 0.906 +/- 0.045 | 0.886 | 98% / 100% | 93% / 100% | 100% / 91% | 0.0 | 0.0 | 2.6 (9/9) | ok | rods L1 gap 4.4 (rod 1.5 wide, 3.2 tall) / L2 gap 1.6 (rod 1.8, 3) | `plinko` | firmware 8.5 mm at 42 mm/s, along the tray |
| 9 | P-2aaaaec0 | plinko | **0.850** | 0.907 +/- 0.058 | 0.868 | 97% / 100% | 95% / 97% | 97% / 93% | 0.0 | 0.0 | 4.4 (9/9) | PEN 1/9 (clr 0.14, pen 0.094) | rods L1 gap 3.7 (rod 2 wide, 1.8 tall) / L2 gap 1.7 (rod 1.5, 2.4) | `plinko` | firmware 7.5 mm at 41 mm/s, along the tray |
| 10 | P-e4035f89 | plinko | **0.840** | 0.902 +/- 0.063 | 0.846 | 97% / 100% | 93% / 96% | 97% / 91% | 0.0 | 0.0 | 7.4 (9/9) | PEN 2/9 (clr 0.14, pen 0.098) | rods L1 gap 3.1 (rod 1.9 wide, 2.8 tall) / L2 gap 1.7 (rod 2.3, 2.6) | `plinko` | firmware 10 mm at 38 mm/s, along the tray |

## Best of each family (style)

| # | id | family | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | design (CAD, nominal mm) | sim spec (as printed) | stroke |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 21 | G-331e7311 | gated | **0.071** | 0.264 +/- 0.193 | 0.037 | 45% / 100% | 82% / 78% | 99% / 34% | 0.7 | 0.0 | - (0/9) | ok | L1 t5.4 / L2 t1.7; slope 3.2 deg, tunnel width 11.4, tooth 1.2, slot 7.6 | `gated:3.2,t5p25,t1p55,tw=11.25,tooth=1.35,slot=7.6` | firmware 5.5 mm at 50 mm/s, along the tray |
| 3 | G-060cecb0 | gated_mid | **0.955** | 0.972 +/- 0.017 | 0.965 | 100% / 100% | 100% / 99% | 99% / 100% | 0.0 | 0.0 | 7.8 (9/9) | PEN 9/9 (clr 0.04, pen 0.130) | L1 w3.1x3.1 / L2 t1.8; slope 0.3 deg, tunnel width 8.3, tooth 1.1, L1 gate at x 31.8 with slot 7.4, L2 at x 53, unflipped | `gated:0.3,w2p95x2p95,t1p65,tw=8.15,tooth=1.25,slot=7.4/7,gx=31.8/53,flip=0` | tool sine 28 Hz, 4.3 g (1.36 mm), 10 deg up |
| 1 | P-ae394887 | plinko | **0.999** | 0.999 +/- 0.000 | 0.999 | 100% / 100% | 100% / 100% | 100% / 100% | 0.0 | 0.0 | 0.4 (9/9) | PEN 1/9 (clr 0.26, pen 0.153) | rods L1 gap 3.7 (rod 2.6 wide, 1.6 tall) / L2 gap 1.5 (rod 1.8, 2.4) | `plinko` | tool sine 48 Hz, 2.2 g (0.24 mm), 20 deg up |
| 12 | I-f660966d | inserts | **0.714** | 0.824 +/- 0.110 | 0.729 | 89% / 100% | 98% / 88% | 89% / 92% | 0.0 | 0.0 | 7.7 (6/9) | PEN 9/9 (clr 0.01, pen 0.178) | square holes 5 (bar 1.2) / 2 (bar 1) | `inserts:h4p85b1p35,h1p85b1p15` | firmware 10 mm at 50 mm/s, along the tray |
| 17 | C-243bf513 | current | **0.523** | 0.608 +/- 0.085 | 0.575 | 100% / 100% | 100% / 67% | 78% / 94% | 3.2 | 0.0 | 5.0 (1/9) | PEN 6/9 (clr 0.12, pen 0.153) | TODAY on the bench: glued mesh inserts mesh5 / mesh2, firmware cap stroke | `inserts:mesh5,mesh2` | firmware 10 mm at 50 mm/s, along the tray |
| 18 | D-e018f15d | demo_rig | **0.499** | 0.499 +/- 0.000 | 0.499 | 100% / 100% | 50% / 100% | 50% / 100% | 0.0 | 0.0 | 0.6 (9/9) | ok | DEMO RIG the team built: one 5 mm printed insert, up and down (sine 20 Hz, 2 g, 90 deg; assumed tool motion, sim/VERTICAL.md) | `inserts:5mm` | tool sine 20 Hz, 2.0 g (1.24 mm), 90 deg up |

## References (fixed, not tuned)

| id | what | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | spec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G-c0121ff0 | README final design: gated, 2 deg, existing strips w5.0 / t1.4, firmware cap stroke | -0.074 | -0.035 +/- 0.039 | -0.059 | 29% / 100% | 66% / 39% | 44% / 3% | 2.8 | 0.0 | - (0/9) | ok | `gated:2,w4p85x7p85,t1p25,tw=7.85,tooth=2.15,slot=7` |
| G-e1861ffb | gatecalc plan (skill): gated, t3.8 / t1.6 nominal (its t1.55 on the 0.1 mm grid), firmware cap | -0.024 | 0.051 +/- 0.074 | -0.019 | 31% / 100% | 79% / 51% | 89% / 11% | 1.0 | 0.0 | - (0/9) | ok | `gated:2,t3p65,t1p45,tw=7.85,tooth=2.15,slot=7` |
| P-99a23702 | plinko_layers.py as in the repo: rods 5.0 / 1.4, firmware cap stroke | 0.670 | 0.810 +/- 0.141 | 0.721 | 100% / 100% | 86% / 100% | 100% / 83% | 0.0 | 0.0 | 6.2 (7/9) | PEN 2/9 (clr 0.16, pen 0.093) | `plinko` |
| I-f660966d | printed inserts as in the repo: 5 mm / 2 mm square holes, firmware cap stroke | 0.714 | 0.824 +/- 0.110 | 0.729 | 89% / 100% | 98% / 88% | 89% / 92% | 0.0 | 0.0 | 7.7 (6/9) | PEN 9/9 (clr 0.01, pen 0.178) | `inserts:h4p85b1p35,h1p85b1p15` |
| C-243bf513 | TODAY on the bench: glued mesh inserts mesh5 / mesh2, firmware cap stroke | 0.523 | 0.608 +/- 0.085 | 0.575 | 100% / 100% | 100% / 67% | 78% / 94% | 3.2 | 0.0 | 5.0 (1/9) | PEN 6/9 (clr 0.12, pen 0.153) | `inserts:mesh5,mesh2` |
| D-e018f15d | DEMO RIG the team built: one 5 mm printed insert, up and down (sine 20 Hz, 2 g, 90 deg; assumed tool motion, sim/VERTICAL.md) | 0.499 | 0.499 +/- 0.000 | 0.499 | 100% / 100% | 50% / 100% | 50% / 100% | 0.0 | 0.0 | 0.6 (9/9) | ok | `inserts:5mm` |

## Verification of flagged leaders at stiffer contacts

Rerun at dt 0.125 ms and contact timeconst 0.25 ms (half the overlap of the standard solver), same 3 friction sets x 3 seeds, 30 s. A design that comes back with no flagged or failed run counts as clean for `winners.json`, ranked by the lower of its two scores.

| id | family | robust (standard) | flags (standard) | robust (stiff) | flags (stiff) | verdict | design |
|---|---|---|---|---|---|---|---|
| P-ae394887 | plinko | 0.999 | PEN 1/9 (clr 0.26, pen 0.153) | 1.000 | ok | clean | rods L1 gap 3.7 (rod 2.6 wide, 1.6 tall) / L2 gap 1.5 (rod 1.8, 2.4) |
| P-668db784 | plinko | 0.998 | PEN 3/9 (clr 0.24, pen 0.205) | 1.000 | PEN 1/9 (clr 0.24, pen 0.125) | still flagged | rods L1 gap 3.5 (rod 3.7 wide, 2 tall) / L2 gap 1.6 (rod 2.9, 2.2) |
| G-060cecb0 | gated_mid | 0.955 | PEN 9/9 (clr 0.04, pen 0.130) | 0.940 | PEN 9/9 (clr 0.04, pen 0.083) | still flagged | L1 w3.1x3.1 / L2 t1.8; slope 0.3 deg, tunnel width 8.3, tooth 1.1, L1 gate at x 31.8 with slot 7.4, L2 at x 53, unflipped |
| P-547508e5 | plinko | 0.937 | PEN 1/9 (clr 0.14, pen 0.098) | 0.927 | ok | clean | rods L1 gap 3.1 (rod 2.8 wide, 1.8 tall) / L2 gap 1.7 (rod 2.3, 1.8) |

## Best per drive

BioKEA's stage can only run the firmware stroke (constant speed); the demo rig is a vibrating tool (sine). Best full-run design for each, whether or not it is flagged:

| drive | id | family | robust | flags | design (CAD, nominal mm) | stroke |
|---|---|---|---|---|---|---|
| firmware (BioKEA's stage) | P-ba5dd6b3 | plinko | 0.929 | ok | rods L1 gap 5.6 (rod 1.8 wide, 2.6 tall) / L2 gap 1.6 (rod 2.2, 2.8) | firmware 9.5 mm at 47 mm/s, 5 deg up |
| vibrating tool (demo rig) | P-ae394887 | plinko | 0.999 | PEN 1/9 (clr 0.26, pen 0.153) | rods L1 gap 3.7 (rod 2.6 wide, 1.6 tall) / L2 gap 1.5 (rod 1.8, 2.4) | tool sine 48 Hz, 2.2 g (0.24 mm), 20 deg up |

## Count matrices of the top 3 (summed over the 9 full runs)

**1. P-ae394887 (plinko) rods L1 gap 3.7 (rod 2.6 wide, 1.6 tall) / L2 gap 1.5 (rod 1.8, 2.4); sim `plinko`**

| class \ ended in | layer_1_rods | layer_2_rods | layer_3_catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 144 | 0 | 0 | 0 | 0 |
| rice | 0 | 270 | 0 | 0 | 0 |
| quinoa | 0 | 0 | 270 | 0 | 0 |

**2. P-668db784 (plinko) rods L1 gap 3.5 (rod 3.7 wide, 2 tall) / L2 gap 1.6 (rod 2.9, 2.2); sim `plinko`**

| class \ ended in | layer_1_rods | layer_2_rods | layer_3_catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 144 | 0 | 0 | 0 | 0 |
| rice | 0 | 270 | 0 | 0 | 0 |
| quinoa | 0 | 0 | 270 | 0 | 0 |

**3. G-060cecb0 (gated_mid) L1 w3.1x3.1 / L2 t1.8; slope 0.3 deg, tunnel width 8.3, tooth 1.1, L1 gate at x 31.8 with slot 7.4, L2 at x 53, unflipped; sim `gated:0.3,w2p95x2p95,t1p65,tw=8.15,tooth=1.25,slot=7.4/7,gx=31.8/53,flip=0`**

| class \ ended in | L1 | L2 | catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 144 | 0 | 0 | 0 | 0 |
| rice | 0 | 266 | 4 | 0 | 0 |
| quinoa | 0 | 0 | 270 | 0 | 0 |


Columns: purity = share of a bin's contents that belong to its class; recovery = share of a class that ends in its bin; jammed = particles per run stuck between bins (in a strip, slot or on a ledge); lost = out of the machine; t90 = seconds until 90% of the sample sits in its target bin (n/9 = runs that got there). Flags: FAIL = runs that went unstable or errored; PEN = particle-vs-gate overlap at or over 0.5 x the tightest gate clearance (near-size results untrustworthy); BEYOND = particles that ended past an opening their own size can't pass (soft contacts squeezed them through; should be 0, and is shown whenever it isn't).
