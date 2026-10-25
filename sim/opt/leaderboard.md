# Leaderboard: Demo set: surrogate grains (pasta + chickpea / rice / quinoa)

Generated 2026-10-25 06:36 by `sim/optimize.py` (study `demo`). 51 candidates, 666 sim runs so far.

**The sim ranks designs; it does not predict real percentages.** It is uncalibrated until `calibrate.py` has bench counts, has no water, rigid particles, and about 80 particles per run. Sizes are simulated at the as-printed opening, nominal - 0.15 mm (ASSUMED until the hole gauge is measured).

Ranked by the robust score (mean - 1 sd) over 3 friction sets x 3 seeds at the full 30 s run. Score per run = min over classes of min(purity, recovery), minus 0.5 x jammed share, 1.0 x lost share and 0.05 x t90/duration. Failed (unstable) runs score -1. Only candidates promoted to the full run are ranked; screened-only ones are in the log. Solver: dt 0.25 ms, contact timeconst 0.5 ms (stiffer than sorter.py's default; see optimize.py). Friction sets: mu 0.3, mu 0.4, mu 0.5.

| # | id | family | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | design (CAD, nominal mm) | sim spec (as printed) | stroke |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | P-cbe7dbec | plinko | **0.891** | 0.929 +/- 0.038 | 0.913 | 99% / 100% | 97% / 97% | 97% / 96% | 0.0 | 0.0 | 4.1 (9/9) | ok | rods L1 gap 5.1 (rod 1.4 wide, 1.6 tall) / L2 gap 1.7 (rod 1.9, 3.2) | `plinko` | 14 mm, 41 mm/s |
| 2 | P-2aaaaec0 | plinko | **0.850** | 0.907 +/- 0.058 | 0.868 | 97% / 100% | 95% / 97% | 97% / 93% | 0.0 | 0.0 | 4.4 (9/9) | PEN 1/9 (clr 0.14, pen 0.094) | rods L1 gap 3.7 (rod 2 wide, 1.8 tall) / L2 gap 1.7 (rod 1.5, 2.4) | `plinko` | 7.5 mm, 41 mm/s |
| 3 | P-e4035f89 | plinko | **0.840** | 0.902 +/- 0.063 | 0.846 | 97% / 100% | 93% / 96% | 97% / 91% | 0.0 | 0.0 | 7.4 (9/9) | PEN 2/9 (clr 0.14, pen 0.098) | rods L1 gap 3.1 (rod 1.9 wide, 2.8 tall) / L2 gap 1.7 (rod 2.3, 2.6) | `plinko` | 10 mm, 38 mm/s |
| 4 | I-f660966d | inserts | **0.714** | 0.824 +/- 0.110 | 0.729 | 89% / 100% | 98% / 88% | 89% / 92% | 0.0 | 0.0 | 7.7 (6/9) | PEN 9/9 (clr 0.01, pen 0.178) | square holes 5 (bar 1.2) / 2 (bar 1) | `inserts:h4p85b1p35,h1p85b1p15` | 10 mm, 50 mm/s |
| 5 | P-99a23702 | plinko | **0.670** | 0.810 +/- 0.141 | 0.721 | 100% / 100% | 86% / 100% | 100% / 83% | 0.0 | 0.0 | 6.2 (7/9) | PEN 2/9 (clr 0.16, pen 0.093) | rods L1 gap 5 (rod 2.4 wide, 3 tall) / L2 gap 1.4 (rod 2, 2.6) | `plinko` | 10 mm, 50 mm/s |
| 6 | I-197107d4 | inserts | **0.197** | 0.280 +/- 0.082 | 0.250 | 65% / 100% | 66% / 90% | 99% / 33% | 0.0 | 0.0 | - (0/9) | PEN 9/9 (clr 0.03, pen 0.156) | square holes 5.1 (bar 1.4) / 1.8 (bar 1) | `inserts:h4p95b1p55,h1p65b1p15` | 6 mm, 15 mm/s |
| 7 | G-e1861ffb | gated | **-0.024** | 0.051 +/- 0.074 | -0.019 | 31% / 100% | 79% / 51% | 89% / 11% | 1.0 | 0.0 | - (0/9) | ok | L1 t3.8 / L2 t1.6; slope 2 deg, tunnel width 8, tooth 2, slot 7 | `gated:2,t3p65,t1p45,tw=7.85,tooth=2.15,slot=7` | 10 mm, 50 mm/s |
| 8 | G-617e6c8a | gated | **-0.025** | 0.079 +/- 0.105 | -0.043 | 33% / 100% | 68% / 37% | 73% / 17% | 4.6 | 0.0 | - (0/9) | PEN 6/9 (clr 0.02, pen 0.075) | L1 t2.7 / L2 t1.9; slope 3.7 deg, tunnel width 10.9, tooth 1.9, slot 6.4 | `gated:3.7,t2p55,t1p75,tw=10.75,tooth=2.05,slot=6.4` | 5 mm, 39 mm/s |
| 9 | I-59959b5e | inserts | **-0.050** | -0.050 +/- 0.000 | -0.050 | 91% / 100% | 51% / 100% | 0% / 0% | 0.0 | 0.0 | - (0/9) | PEN 2/9 (clr 0.24, pen 0.149) | square holes 5.6 (bar 1) / 1.5 (bar 0.9) | `inserts:h5p45b1p15,h1p35b1p05` | 7.5 mm, 42 mm/s |
| 10 | G-3f2e5464 | gated | **-0.056** | -0.043 +/- 0.014 | -0.050 | 24% / 100% | 78% / 25% | 33% / 1% | 0.6 | 0.0 | - (0/9) | ok | L1 t3.4 / L2 t1.6; slope 1.6 deg, tunnel width 10.6, tooth 2.1, slot 6.2 | `gated:1.6,t3p25,t1p45,tw=10.45,tooth=2.25,slot=6.2` | 14.5 mm, 41 mm/s |

## Best of each family (style)

| # | id | family | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | design (CAD, nominal mm) | sim spec (as printed) | stroke |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8 | G-e1861ffb | gated | **-0.024** | 0.051 +/- 0.074 | -0.019 | 31% / 100% | 79% / 51% | 89% / 11% | 1.0 | 0.0 | - (0/9) | ok | L1 t3.8 / L2 t1.6; slope 2 deg, tunnel width 8, tooth 2, slot 7 | `gated:2,t3p65,t1p45,tw=7.85,tooth=2.15,slot=7` | 10 mm, 50 mm/s |
| 1 | P-cbe7dbec | plinko | **0.891** | 0.929 +/- 0.038 | 0.913 | 99% / 100% | 97% / 97% | 97% / 96% | 0.0 | 0.0 | 4.1 (9/9) | ok | rods L1 gap 5.1 (rod 1.4 wide, 1.6 tall) / L2 gap 1.7 (rod 1.9, 3.2) | `plinko` | 14 mm, 41 mm/s |
| 4 | I-f660966d | inserts | **0.714** | 0.824 +/- 0.110 | 0.729 | 89% / 100% | 98% / 88% | 89% / 92% | 0.0 | 0.0 | 7.7 (6/9) | PEN 9/9 (clr 0.01, pen 0.178) | square holes 5 (bar 1.2) / 2 (bar 1) | `inserts:h4p85b1p35,h1p85b1p15` | 10 mm, 50 mm/s |
| 6 | C-243bf513 | current | **0.523** | 0.608 +/- 0.085 | 0.575 | 100% / 100% | 100% / 67% | 78% / 94% | 3.2 | 0.0 | 5.0 (1/9) | PEN 6/9 (clr 0.12, pen 0.153) | TODAY on the bench: glued mesh inserts mesh5 / mesh2, firmware cap stroke | `inserts:mesh5,mesh2` | 10 mm, 50 mm/s |

## References (fixed, not tuned)

| id | what | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | spec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G-c0121ff0 | README final design: gated, 2 deg, existing strips w5.0 / t1.4, firmware cap stroke | -0.074 | -0.035 +/- 0.039 | -0.059 | 29% / 100% | 66% / 39% | 44% / 3% | 2.8 | 0.0 | - (0/9) | ok | `gated:2,w4p85x7p85,t1p25,tw=7.85,tooth=2.15,slot=7` |
| G-e1861ffb | gatecalc plan (skill): gated, t3.8 / t1.6 nominal (its t1.55 on the 0.1 mm grid), firmware cap | -0.024 | 0.051 +/- 0.074 | -0.019 | 31% / 100% | 79% / 51% | 89% / 11% | 1.0 | 0.0 | - (0/9) | ok | `gated:2,t3p65,t1p45,tw=7.85,tooth=2.15,slot=7` |
| P-99a23702 | plinko_layers.py as in the repo: rods 5.0 / 1.4, firmware cap stroke | 0.670 | 0.810 +/- 0.141 | 0.721 | 100% / 100% | 86% / 100% | 100% / 83% | 0.0 | 0.0 | 6.2 (7/9) | PEN 2/9 (clr 0.16, pen 0.093) | `plinko` |
| I-f660966d | printed inserts as in the repo: 5 mm / 2 mm square holes, firmware cap stroke | 0.714 | 0.824 +/- 0.110 | 0.729 | 89% / 100% | 98% / 88% | 89% / 92% | 0.0 | 0.0 | 7.7 (6/9) | PEN 9/9 (clr 0.01, pen 0.178) | `inserts:h4p85b1p35,h1p85b1p15` |
| C-243bf513 | TODAY on the bench: glued mesh inserts mesh5 / mesh2, firmware cap stroke | 0.523 | 0.608 +/- 0.085 | 0.575 | 100% / 100% | 100% / 67% | 78% / 94% | 3.2 | 0.0 | 5.0 (1/9) | PEN 6/9 (clr 0.12, pen 0.153) | `inserts:mesh5,mesh2` |

## Count matrices of the top 3 (summed over the 9 full runs)

**1. P-cbe7dbec (plinko) rods L1 gap 5.1 (rod 1.4 wide, 1.6 tall) / L2 gap 1.7 (rod 1.9, 3.2); sim `plinko`**

| class \ ended in | layer_1_rods | layer_2_rods | layer_3_catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 144 | 0 | 0 | 0 | 0 |
| rice | 0 | 262 | 8 | 0 | 0 |
| quinoa | 2 | 10 | 258 | 0 | 0 |

**2. P-2aaaaec0 (plinko) rods L1 gap 3.7 (rod 2 wide, 1.8 tall) / L2 gap 1.7 (rod 1.5, 2.4); sim `plinko`**

| class \ ended in | layer_1_rods | layer_2_rods | layer_3_catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 144 | 0 | 0 | 0 | 0 |
| rice | 1 | 261 | 8 | 0 | 0 |
| quinoa | 3 | 15 | 252 | 0 | 0 |

**3. P-e4035f89 (plinko) rods L1 gap 3.1 (rod 1.9 wide, 2.8 tall) / L2 gap 1.7 (rod 2.3, 2.6); sim `plinko`**

| class \ ended in | layer_1_rods | layer_2_rods | layer_3_catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 144 | 0 | 0 | 0 | 0 |
| rice | 2 | 260 | 8 | 0 | 0 |
| quinoa | 3 | 20 | 247 | 0 | 0 |


Columns: purity = share of a bin's contents that belong to its class; recovery = share of a class that ends in its bin; jammed = particles per run stuck between bins (in a strip, slot or on a ledge); lost = out of the machine; t90 = seconds until 90% of the sample sits in its target bin (n/9 = runs that got there). Flags: FAIL = runs that went unstable or errored; PEN = particle-vs-tray overlap at or over 0.5 x the tightest gate clearance (near-size results untrustworthy).
