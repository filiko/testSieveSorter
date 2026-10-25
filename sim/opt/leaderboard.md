# Leaderboard: Demo set: surrogate grains (pasta + chickpea / rice / quinoa)

Generated 2026-10-25 06:51 by `sim/optimize.py` (study `demo`). 78 candidates, 990 sim runs so far.

**The sim ranks designs; it does not predict real percentages.** It is uncalibrated until `calibrate.py` has bench counts, has no water, rigid particles, and about 80 particles per run. Sizes are simulated at the as-printed opening, nominal - 0.15 mm (ASSUMED until the hole gauge is measured).

Ranked by the robust score (mean - 1 sd) over 3 friction sets x 3 seeds at the full 30 s run. Score per run = min over classes of min(purity, recovery), minus 0.5 x jammed share, 1.0 x lost share and 0.05 x t90/duration. Failed (unstable) runs score -1. Only candidates promoted to the full run are ranked; screened-only ones are in the log. Solver: dt 0.25 ms, contact timeconst 0.5 ms (stiffer than sorter.py's default; see optimize.py). Friction sets: mu 0.3, mu 0.4, mu 0.5.

| # | id | family | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | design (CAD, nominal mm) | sim spec (as printed) | stroke |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | P-63092ca9 | plinko | **0.915** | 0.953 +/- 0.038 | 0.918 | 99% / 100% | 96% / 100% | 100% / 96% | 0.0 | 0.0 | 1.7 (9/9) | ok | rods L1 gap 5.6 (rod 2.1 wide, 2.6 tall) / L2 gap 1.6 (rod 1.6, 3.4) | `plinko` | firmware 10 mm at 50 mm/s, along the tray |
| 2 | P-cbe7dbec | plinko | **0.891** | 0.929 +/- 0.038 | 0.913 | 99% / 100% | 97% / 97% | 97% / 96% | 0.0 | 0.0 | 4.1 (9/9) | ok | rods L1 gap 5.1 (rod 1.4 wide, 1.6 tall) / L2 gap 1.7 (rod 1.9, 3.2) | `plinko` | firmware 14 mm at 41 mm/s, along the tray |
| 3 | P-7e49fbec | plinko | **0.860** | 0.906 +/- 0.045 | 0.886 | 98% / 100% | 93% / 100% | 100% / 91% | 0.0 | 0.0 | 2.6 (9/9) | ok | rods L1 gap 4.4 (rod 1.5 wide, 3.2 tall) / L2 gap 1.6 (rod 1.8, 3) | `plinko` | firmware 8.5 mm at 42 mm/s, along the tray |
| 4 | P-2aaaaec0 | plinko | **0.850** | 0.907 +/- 0.058 | 0.868 | 97% / 100% | 95% / 97% | 97% / 93% | 0.0 | 0.0 | 4.4 (9/9) | PEN 1/9 (clr 0.14, pen 0.094) | rods L1 gap 3.7 (rod 2 wide, 1.8 tall) / L2 gap 1.7 (rod 1.5, 2.4) | `plinko` | firmware 7.5 mm at 41 mm/s, along the tray |
| 5 | P-e4035f89 | plinko | **0.840** | 0.902 +/- 0.063 | 0.846 | 97% / 100% | 93% / 96% | 97% / 91% | 0.0 | 0.0 | 7.4 (9/9) | PEN 2/9 (clr 0.14, pen 0.098) | rods L1 gap 3.1 (rod 1.9 wide, 2.8 tall) / L2 gap 1.7 (rod 2.3, 2.6) | `plinko` | firmware 10 mm at 38 mm/s, along the tray |
| 6 | I-f660966d | inserts | **0.714** | 0.824 +/- 0.110 | 0.729 | 89% / 100% | 98% / 88% | 89% / 92% | 0.0 | 0.0 | 7.7 (6/9) | PEN 9/9 (clr 0.01, pen 0.178) | square holes 5 (bar 1.2) / 2 (bar 1) | `inserts:h4p85b1p35,h1p85b1p15` | firmware 10 mm at 50 mm/s, along the tray |
| 7 | P-99a23702 | plinko | **0.670** | 0.810 +/- 0.141 | 0.721 | 100% / 100% | 86% / 100% | 100% / 83% | 0.0 | 0.0 | 6.2 (7/9) | PEN 2/9 (clr 0.16, pen 0.093) | rods L1 gap 5 (rod 2.4 wide, 3 tall) / L2 gap 1.4 (rod 2, 2.6) | `plinko` | firmware 10 mm at 50 mm/s, along the tray |
| 8 | I-08d1890b | inserts | **0.565** | 0.638 +/- 0.072 | 0.626 | 71% / 100% | 88% / 93% | 99% / 70% | 0.0 | 0.0 | 27.5 (2/9) | BEYOND 1 (particles past an opening they can't fit); PEN 9/9 (clr 0.10, pen 0.176) | square holes 4.8 (bar 1.2) / 1.9 (bar 1) | `inserts:h4p65b1p35,h1p75b1p15` | firmware 13 mm at 28 mm/s, along the tray |
| 9 | I-197107d4 | inserts | **0.197** | 0.280 +/- 0.082 | 0.250 | 65% / 100% | 66% / 90% | 99% / 33% | 0.0 | 0.0 | - (0/9) | PEN 9/9 (clr 0.03, pen 0.156) | square holes 5.1 (bar 1.4) / 1.8 (bar 1) | `inserts:h4p95b1p55,h1p65b1p15` | firmware 6 mm at 15 mm/s, along the tray |
| 10 | G-331e7311 | gated | **0.071** | 0.264 +/- 0.193 | 0.037 | 45% / 100% | 82% / 78% | 99% / 34% | 0.7 | 0.0 | - (0/9) | ok | L1 t5.4 / L2 t1.7; slope 3.2 deg, tunnel width 11.4, tooth 1.2, slot 7.6 | `gated:3.2,t5p25,t1p55,tw=11.25,tooth=1.35,slot=7.6` | firmware 5.5 mm at 50 mm/s, along the tray |

## Best of each family (style)

| # | id | family | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | design (CAD, nominal mm) | sim spec (as printed) | stroke |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11 | G-331e7311 | gated | **0.071** | 0.264 +/- 0.193 | 0.037 | 45% / 100% | 82% / 78% | 99% / 34% | 0.7 | 0.0 | - (0/9) | ok | L1 t5.4 / L2 t1.7; slope 3.2 deg, tunnel width 11.4, tooth 1.2, slot 7.6 | `gated:3.2,t5p25,t1p55,tw=11.25,tooth=1.35,slot=7.6` | firmware 5.5 mm at 50 mm/s, along the tray |
| 1 | P-63092ca9 | plinko | **0.915** | 0.953 +/- 0.038 | 0.918 | 99% / 100% | 96% / 100% | 100% / 96% | 0.0 | 0.0 | 1.7 (9/9) | ok | rods L1 gap 5.6 (rod 2.1 wide, 2.6 tall) / L2 gap 1.6 (rod 1.6, 3.4) | `plinko` | firmware 10 mm at 50 mm/s, along the tray |
| 6 | I-f660966d | inserts | **0.714** | 0.824 +/- 0.110 | 0.729 | 89% / 100% | 98% / 88% | 89% / 92% | 0.0 | 0.0 | 7.7 (6/9) | PEN 9/9 (clr 0.01, pen 0.178) | square holes 5 (bar 1.2) / 2 (bar 1) | `inserts:h4p85b1p35,h1p85b1p15` | firmware 10 mm at 50 mm/s, along the tray |
| 9 | C-243bf513 | current | **0.523** | 0.608 +/- 0.085 | 0.575 | 100% / 100% | 100% / 67% | 78% / 94% | 3.2 | 0.0 | 5.0 (1/9) | PEN 6/9 (clr 0.12, pen 0.153) | TODAY on the bench: glued mesh inserts mesh5 / mesh2, firmware cap stroke | `inserts:mesh5,mesh2` | firmware 10 mm at 50 mm/s, along the tray |

## References (fixed, not tuned)

| id | what | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | spec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G-c0121ff0 | README final design: gated, 2 deg, existing strips w5.0 / t1.4, firmware cap stroke | -0.074 | -0.035 +/- 0.039 | -0.059 | 29% / 100% | 66% / 39% | 44% / 3% | 2.8 | 0.0 | - (0/9) | ok | `gated:2,w4p85x7p85,t1p25,tw=7.85,tooth=2.15,slot=7` |
| G-e1861ffb | gatecalc plan (skill): gated, t3.8 / t1.6 nominal (its t1.55 on the 0.1 mm grid), firmware cap | -0.024 | 0.051 +/- 0.074 | -0.019 | 31% / 100% | 79% / 51% | 89% / 11% | 1.0 | 0.0 | - (0/9) | ok | `gated:2,t3p65,t1p45,tw=7.85,tooth=2.15,slot=7` |
| P-99a23702 | plinko_layers.py as in the repo: rods 5.0 / 1.4, firmware cap stroke | 0.670 | 0.810 +/- 0.141 | 0.721 | 100% / 100% | 86% / 100% | 100% / 83% | 0.0 | 0.0 | 6.2 (7/9) | PEN 2/9 (clr 0.16, pen 0.093) | `plinko` |
| I-f660966d | printed inserts as in the repo: 5 mm / 2 mm square holes, firmware cap stroke | 0.714 | 0.824 +/- 0.110 | 0.729 | 89% / 100% | 98% / 88% | 89% / 92% | 0.0 | 0.0 | 7.7 (6/9) | PEN 9/9 (clr 0.01, pen 0.178) | `inserts:h4p85b1p35,h1p85b1p15` |
| C-243bf513 | TODAY on the bench: glued mesh inserts mesh5 / mesh2, firmware cap stroke | 0.523 | 0.608 +/- 0.085 | 0.575 | 100% / 100% | 100% / 67% | 78% / 94% | 3.2 | 0.0 | 5.0 (1/9) | PEN 6/9 (clr 0.12, pen 0.153) | `inserts:mesh5,mesh2` |

## Count matrices of the top 3 (summed over the 9 full runs)

**1. P-63092ca9 (plinko) rods L1 gap 5.6 (rod 2.1 wide, 2.6 tall) / L2 gap 1.6 (rod 1.6, 3.4); sim `plinko`**

| class \ ended in | layer_1_rods | layer_2_rods | layer_3_catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 144 | 0 | 0 | 0 | 0 |
| rice | 0 | 270 | 0 | 0 | 0 |
| quinoa | 1 | 11 | 258 | 0 | 0 |

**2. P-cbe7dbec (plinko) rods L1 gap 5.1 (rod 1.4 wide, 1.6 tall) / L2 gap 1.7 (rod 1.9, 3.2); sim `plinko`**

| class \ ended in | layer_1_rods | layer_2_rods | layer_3_catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 144 | 0 | 0 | 0 | 0 |
| rice | 0 | 262 | 8 | 0 | 0 |
| quinoa | 2 | 10 | 258 | 0 | 0 |

**3. P-7e49fbec (plinko) rods L1 gap 4.4 (rod 1.5 wide, 3.2 tall) / L2 gap 1.6 (rod 1.8, 3); sim `plinko`**

| class \ ended in | layer_1_rods | layer_2_rods | layer_3_catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 144 | 0 | 0 | 0 | 0 |
| rice | 0 | 270 | 0 | 0 | 0 |
| quinoa | 3 | 21 | 246 | 0 | 0 |


Columns: purity = share of a bin's contents that belong to its class; recovery = share of a class that ends in its bin; jammed = particles per run stuck between bins (in a strip, slot or on a ledge); lost = out of the machine; t90 = seconds until 90% of the sample sits in its target bin (n/9 = runs that got there). Flags: FAIL = runs that went unstable or errored; PEN = particle-vs-gate overlap at or over 0.5 x the tightest gate clearance (near-size results untrustworthy); BEYOND = particles that ended past an opening their own size can't pass (soft contacts squeezed them through; should be 0, and is shown whenever it isn't).
