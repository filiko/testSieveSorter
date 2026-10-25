# Leaderboard: Demo set: surrogate grains (pasta + chickpea / rice / quinoa)

Generated 2026-10-25 08:48 by `sim/optimize.py` (study `demo`). 168 candidates, 2322 sim runs so far.

**The sim ranks designs; it does not predict real percentages.** It is uncalibrated until `calibrate.py` has bench counts, has no water, rigid particles, and about 80 particles per run. Sizes are simulated at the as-printed opening, nominal - 0.15 mm (ASSUMED until the hole gauge is measured).

Ranked by the robust score (mean - 1 sd) over 3 friction sets x 3 seeds at the full 30 s run. Score per run = min over classes of min(purity, recovery), minus 0.5 x jammed share, 1.0 x lost share and 0.05 x t90/duration. Failed (unstable) runs score -1. Only candidates promoted to the full run are ranked; screened-only ones are in the log. Solver: dt 0.25 ms, contact timeconst 0.5 ms (stiffer than sorter.py's default; see optimize.py). Friction sets: mu 0.3, mu 0.4, mu 0.5.

| # | id | family | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | design (CAD, nominal mm) | sim spec (as printed) | stroke |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | P-ae394887 | plinko | **0.999** | 0.999 +/- 0.000 | 0.999 | 100% / 100% | 100% / 100% | 100% / 100% | 0.0 | 0.0 | 0.4 (9/9) | PEN 1/9 (clr 0.26, pen 0.153) | rods L1 gap 3.7 (rod 2.6 wide, 1.6 tall) / L2 gap 1.5 (rod 1.8, 2.4) | `plinko` | tool sine 48 Hz, 2.2 g (0.24 mm), 20 deg up |
| 2 | P-668db784 | plinko | **0.998** | 0.998 +/- 0.000 | 0.998 | 100% / 100% | 100% / 100% | 100% / 100% | 0.0 | 0.0 | 0.9 (9/9) | PEN 3/9 (clr 0.24, pen 0.205) | rods L1 gap 3.5 (rod 3.7 wide, 2 tall) / L2 gap 1.6 (rod 2.9, 2.2) | `plinko` | tool sine 14 Hz, 2.0 g (2.54 mm), along the tray |
| 3 | G-a1ecf9bb | gated_mid | **0.985** | 0.988 +/- 0.003 | 0.987 | 100% / 100% | 100% / 100% | 100% / 100% | 0.0 | 0.0 | 7.1 (9/9) | ok | L1 t3.5 / L2 t1.6; slope 2.7 deg, tunnel width 5, tooth 0.8, L1 gate at x 22.2 with slot 8.1, L2 at x 53, unflipped | `gated:2.7,t3p35,t1p45,tw=4.85,tooth=0.95,slot=8.1/7,gx=22.2/53,flip=0` | tool sine 48 Hz, 3.7 g (0.40 mm), 30 deg up |
| 4 | G-060cecb0 | gated_mid | **0.955** | 0.972 +/- 0.017 | 0.965 | 100% / 100% | 100% / 99% | 99% / 100% | 0.0 | 0.0 | 7.8 (9/9) | PEN 9/9 (clr 0.04, pen 0.130) | L1 w3.1x3.1 / L2 t1.8; slope 0.3 deg, tunnel width 8.3, tooth 1.1, L1 gate at x 31.8 with slot 7.4, L2 at x 53, unflipped | `gated:0.3,w2p95x2p95,t1p65,tw=8.15,tooth=1.25,slot=7.4/7,gx=31.8/53,flip=0` | tool sine 28 Hz, 4.3 g (1.36 mm), 10 deg up |
| 5 | P-fdf86953 | plinko | **0.937** | 0.966 +/- 0.029 | 0.966 | 100% / 100% | 100% / 97% | 97% / 100% | 0.0 | 0.0 | 0.2 (9/9) | ok | rods L1 gap 5.1 (rod 2.4 wide, 3.4 tall) / L2 gap 1.7 (rod 2.3, 3.2) | `plinko` | tool sine 50 Hz, 1.8 g (0.18 mm), 25 deg up |
| 6 | P-547508e5 | plinko | **0.937** | 0.966 +/- 0.029 | 0.966 | 100% / 100% | 100% / 97% | 97% / 100% | 0.0 | 0.0 | 0.5 (9/9) | PEN 1/9 (clr 0.14, pen 0.098) | rods L1 gap 3.1 (rod 2.8 wide, 1.8 tall) / L2 gap 1.7 (rod 2.3, 1.8) | `plinko` | tool sine 46 Hz, 1.3 g (0.15 mm), 35 deg up |
| 7 | P-ba5dd6b3 | plinko | **0.929** | 0.960 +/- 0.031 | 0.929 | 99% / 100% | 97% / 100% | 100% / 97% | 0.0 | 0.0 | 2.2 (9/9) | ok | rods L1 gap 5.6 (rod 1.8 wide, 2.6 tall) / L2 gap 1.6 (rod 2.2, 2.8) | `plinko` | firmware 9.5 mm at 47 mm/s, 5 deg up |
| 8 | P-d6f1a484 | plinko | **0.925** | 0.958 +/- 0.033 | 0.954 | 98% / 100% | 100% / 96% | 97% / 100% | 0.0 | 0.0 | 0.8 (9/9) | PEN 2/9 (clr 0.14, pen 0.096) | rods L1 gap 3.8 (rod 3 wide, 3 tall) / L2 gap 1.7 (rod 2, 2.6) | `plinko` | tool sine 50 Hz, 1.5 g (0.15 mm), 5 deg up |
| 9 | P-63092ca9 | plinko | **0.915** | 0.953 +/- 0.038 | 0.918 | 99% / 100% | 96% / 100% | 100% / 96% | 0.0 | 0.0 | 1.7 (9/9) | ok | rods L1 gap 5.6 (rod 2.1 wide, 2.6 tall) / L2 gap 1.6 (rod 1.6, 3.4) | `plinko` | firmware 10 mm at 50 mm/s, along the tray |
| 10 | P-cbe7dbec | plinko | **0.891** | 0.929 +/- 0.038 | 0.913 | 99% / 100% | 97% / 97% | 97% / 96% | 0.0 | 0.0 | 4.1 (9/9) | ok | rods L1 gap 5.1 (rod 1.4 wide, 1.6 tall) / L2 gap 1.7 (rod 1.9, 3.2) | `plinko` | firmware 14 mm at 41 mm/s, along the tray |

## Best of each family (style)

| # | id | family | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | design (CAD, nominal mm) | sim spec (as printed) | stroke |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 15 | G-5798ec1f | gated | **0.742** | 0.834 +/- 0.092 | 0.775 | 91% / 100% | 92% / 96% | 100% / 89% | 0.1 | 0.0 | 21.3 (7/9) | ok | L1 t5.4 / L2 t1.5; slope 1.8 deg, tunnel width 8.1, tooth 1.1, slot 9.6 | `gated:1.8,t5p25,t1p35,tw=7.95,tooth=1.25,slot=9.6` | tool sine 33 Hz, 3.3 g (0.75 mm), along the tray |
| 3 | G-a1ecf9bb | gated_mid | **0.985** | 0.988 +/- 0.003 | 0.987 | 100% / 100% | 100% / 100% | 100% / 100% | 0.0 | 0.0 | 7.1 (9/9) | ok | L1 t3.5 / L2 t1.6; slope 2.7 deg, tunnel width 5, tooth 0.8, L1 gate at x 22.2 with slot 8.1, L2 at x 53, unflipped | `gated:2.7,t3p35,t1p45,tw=4.85,tooth=0.95,slot=8.1/7,gx=22.2/53,flip=0` | tool sine 48 Hz, 3.7 g (0.40 mm), 30 deg up |
| 1 | P-ae394887 | plinko | **0.999** | 0.999 +/- 0.000 | 0.999 | 100% / 100% | 100% / 100% | 100% / 100% | 0.0 | 0.0 | 0.4 (9/9) | PEN 1/9 (clr 0.26, pen 0.153) | rods L1 gap 3.7 (rod 2.6 wide, 1.6 tall) / L2 gap 1.5 (rod 1.8, 2.4) | `plinko` | tool sine 48 Hz, 2.2 g (0.24 mm), 20 deg up |
| 16 | I-f660966d | inserts | **0.714** | 0.824 +/- 0.110 | 0.729 | 89% / 100% | 98% / 88% | 89% / 92% | 0.0 | 0.0 | 7.7 (6/9) | PEN 9/9 (clr 0.01, pen 0.178) | square holes 5 (bar 1.2) / 2 (bar 1) | `inserts:h4p85b1p35,h1p85b1p15` | firmware 10 mm at 50 mm/s, along the tray |
| 23 | C-243bf513 | current | **0.523** | 0.608 +/- 0.085 | 0.575 | 100% / 100% | 100% / 67% | 78% / 94% | 3.2 | 0.0 | 5.0 (1/9) | PEN 6/9 (clr 0.12, pen 0.153) | TODAY on the bench: glued mesh inserts mesh5 / mesh2, firmware cap stroke | `inserts:mesh5,mesh2` | firmware 10 mm at 50 mm/s, along the tray |
| 24 | D-e018f15d | demo_rig | **0.499** | 0.499 +/- 0.000 | 0.499 | 100% / 100% | 50% / 100% | 50% / 100% | 0.0 | 0.0 | 0.6 (9/9) | ok | one level of the demo rig: the 5 mm tray alone over a catch pan, up and down (sine 20 Hz, 2 g, 90 deg). The full rig is the stacked baseline above | `inserts:5mm` | tool sine 20 Hz, 2.0 g (1.24 mm), 90 deg up |

## References (fixed, not tuned)

| id | what | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | spec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G-c0121ff0 | README final design: gated, 2 deg, existing strips w5.0 / t1.4, firmware cap stroke | -0.074 | -0.035 +/- 0.039 | -0.059 | 29% / 100% | 66% / 39% | 44% / 3% | 2.8 | 0.0 | - (0/9) | ok | `gated:2,w4p85x7p85,t1p25,tw=7.85,tooth=2.15,slot=7` |
| G-e1861ffb | gatecalc plan (skill): gated, t3.8 / t1.6 nominal (its t1.55 on the 0.1 mm grid), firmware cap | -0.024 | 0.051 +/- 0.074 | -0.019 | 31% / 100% | 79% / 51% | 89% / 11% | 1.0 | 0.0 | - (0/9) | ok | `gated:2,t3p65,t1p45,tw=7.85,tooth=2.15,slot=7` |
| P-99a23702 | plinko_layers.py as in the repo: rods 5.0 / 1.4, firmware cap stroke | 0.670 | 0.810 +/- 0.141 | 0.721 | 100% / 100% | 86% / 100% | 100% / 83% | 0.0 | 0.0 | 6.2 (7/9) | PEN 2/9 (clr 0.16, pen 0.093) | `plinko` |
| I-f660966d | printed inserts as in the repo: 5 mm / 2 mm square holes, firmware cap stroke | 0.714 | 0.824 +/- 0.110 | 0.729 | 89% / 100% | 98% / 88% | 89% / 92% | 0.0 | 0.0 | 7.7 (6/9) | PEN 9/9 (clr 0.01, pen 0.178) | `inserts:h4p85b1p35,h1p85b1p15` |
| C-243bf513 | TODAY on the bench: glued mesh inserts mesh5 / mesh2, firmware cap stroke | 0.523 | 0.608 +/- 0.085 | 0.575 | 100% / 100% | 100% / 67% | 78% / 94% | 3.2 | 0.0 | 5.0 (1/9) | PEN 6/9 (clr 0.12, pen 0.153) | `inserts:mesh5,mesh2` |
| D-e018f15d | one level of the demo rig: the 5 mm tray alone over a catch pan, up and down (sine 20 Hz, 2 g, 90 deg). The full rig is the stacked baseline above | 0.499 | 0.499 +/- 0.000 | 0.499 | 100% / 100% | 50% / 100% | 50% / 100% | 0.0 | 0.0 | 0.6 (9/9) | ok | `inserts:5mm` |

## Stress test: the leaders under the two biggest unknowns

**Stroke reversal.** The firmware reverses at constant speed with no ramp; how sharp the real reversal is depends on the stage and is unmeasured (sweep.py FIRMWARE assumes 0.01 s). Transport depends on it. **Print size.** Openings are simulated at nominal - 0.15 mm (assumed); a printer that makes them 0.1 mm tighter or looser shifts every cut. Each column reruns the design with one of these changed (full length, same 3 friction sets x 3 seeds; robust score). A design whose score holds across columns is safer to print.

| id | family | as ranked (ramp 0.01 s, undersize 0.15 mm) | ramp 0.005 s | ramp 0.02 s | undersize 0.05 mm | undersize 0.25 mm | worst | design |
|---|---|---|---|---|---|---|---|---|
| P-ae394887 | plinko | 0.999 | - | - | 0.978 | 0.997 | **0.978** | rods L1 gap 3.7 (rod 2.6 wide, 1.6 tall) / L2 gap 1.5 (rod 1.8, 2.4) |
| P-668db784 | plinko | 0.998 | - | - | 0.937 | 0.997 | **0.937** | rods L1 gap 3.5 (rod 3.7 wide, 2 tall) / L2 gap 1.6 (rod 2.9, 2.2) |
| G-a1ecf9bb | gated_mid | 0.985 | - | - | 0.925 | 0.965 | **0.925** | L1 t3.5 / L2 t1.6; slope 2.7 deg, tunnel width 5, tooth 0.8, L1 gate at x 22.2 with slot 8.1, L2 at x 53, unflipped |
| P-fdf86953 | plinko | 0.937 | - | - | 0.650 | 0.977 | **0.650** | rods L1 gap 5.1 (rod 2.4 wide, 3.4 tall) / L2 gap 1.7 (rod 2.3, 3.2) |
| P-ba5dd6b3 | plinko | 0.929 | 0.971 | 0.892 | 0.930 | 0.870 | **0.870** | rods L1 gap 5.6 (rod 1.8 wide, 2.6 tall) / L2 gap 1.6 (rod 2.2, 2.8) |
| I-f660966d | inserts | 0.714 | 0.729 | 0.655 | 0.599 | 0.710 | **0.599** | square holes 5 (bar 1.2) / 2 (bar 1) |
| P-99a23702 | plinko | 0.670 | 0.934 | 0.530 | 0.799 | 0.485 | **0.485** | rods L1 gap 5 (rod 2.4 wide, 3 tall) / L2 gap 1.4 (rod 2, 2.6) |
| C-243bf513 | current | 0.523 | 0.518 | 0.522 | 0.523 | 0.523 | **0.518** | TODAY on the bench: glued mesh inserts mesh5 / mesh2, firmware cap stroke |
| D-e018f15d | demo_rig | 0.499 | - | - | 0.499 | 0.499 | **0.499** | one level of the demo rig: the 5 mm tray alone over a catch pan, up and down (sine 20 Hz, 2 g, 90 deg). The full rig is the stacked baseline above |
| G-e1861ffb | gated | -0.024 | -0.062 | -0.073 | -0.028 | -0.065 | **-0.073** | L1 t3.8 / L2 t1.6; slope 2 deg, tunnel width 8, tooth 2, slot 7 |
| G-c0121ff0 | gated | -0.074 | -0.067 | -0.074 | -0.055 | -0.078 | **-0.078** | L1 w5x8 / L2 t1.4; slope 2 deg, tunnel width 8, tooth 2, slot 7 |

## Verification of flagged leaders at stiffer contacts

Rerun at dt 0.125 ms and contact timeconst 0.25 ms (half the overlap of the standard solver), same 3 friction sets x 3 seeds, 30 s. A design that comes back with no flagged or failed run counts as clean for `winners.json`, ranked by the lower of its two scores.

| id | family | robust (standard) | flags (standard) | robust (stiff) | flags (stiff) | verdict | design |
|---|---|---|---|---|---|---|---|
| P-ae394887 | plinko | 0.999 | PEN 1/9 (clr 0.26, pen 0.153) | 0.999 | ok | clean | rods L1 gap 3.7 (rod 2.6 wide, 1.6 tall) / L2 gap 1.5 (rod 1.8, 2.4) |
| P-668db784 | plinko | 0.998 | PEN 3/9 (clr 0.24, pen 0.205) | 0.998 | PEN 1/9 (clr 0.24, pen 0.125) | still flagged | rods L1 gap 3.5 (rod 3.7 wide, 2 tall) / L2 gap 1.6 (rod 2.9, 2.2) |
| G-060cecb0 | gated_mid | 0.955 | PEN 9/9 (clr 0.04, pen 0.130) | 0.934 | PEN 9/9 (clr 0.04, pen 0.083) | still flagged | L1 w3.1x3.1 / L2 t1.8; slope 0.3 deg, tunnel width 8.3, tooth 1.1, L1 gate at x 31.8 with slot 7.4, L2 at x 53, unflipped |
| P-547508e5 | plinko | 0.937 | PEN 1/9 (clr 0.14, pen 0.098) | 0.937 | ok | clean | rods L1 gap 3.1 (rod 2.8 wide, 1.8 tall) / L2 gap 1.7 (rod 2.3, 1.8) |

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

**3. G-a1ecf9bb (gated_mid) L1 t3.5 / L2 t1.6; slope 2.7 deg, tunnel width 5, tooth 0.8, L1 gate at x 22.2 with slot 8.1, L2 at x 53, unflipped; sim `gated:2.7,t3p35,t1p45,tw=4.85,tooth=0.95,slot=8.1/7,gx=22.2/53,flip=0`**

| class \ ended in | L1 | L2 | catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 144 | 0 | 0 | 0 | 0 |
| rice | 0 | 270 | 0 | 0 | 0 |
| quinoa | 0 | 0 | 270 | 0 | 0 |


Columns: purity = share of a bin's contents that belong to its class; recovery = share of a class that ends in its bin; jammed = particles per run stuck between bins (in a strip, slot or on a ledge); lost = out of the machine; t90 = seconds until 90% of the sample sits in its target bin (n/9 = runs that got there). Flags: FAIL = runs that went unstable or errored; PEN = particle-vs-gate overlap at or over 0.5 x the tightest gate clearance (near-size results untrustworthy); BEYOND = particles that ended past an opening their own size can't pass (soft contacts squeezed them through; should be 0, and is shown whenever it isn't).
