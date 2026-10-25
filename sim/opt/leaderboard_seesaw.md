# Leaderboard: Demo set on the rig's seesaw: each tray rocks about its middle (the ends tip), neighbours alternate, +/-5-15 deg (rocking.py)

Generated 2026-10-25 13:23 by `sim/optimize.py` (study `seesaw`). 24 candidates, 144 sim runs so far.

**The sim ranks designs; it does not predict real percentages.** It is uncalibrated until `calibrate.py` has bench counts, has no water, rigid particles, and about 80 particles per run. Sizes are simulated at the as-printed opening, nominal - 0.15 mm (ASSUMED until the hole gauge is measured).

Ranked by the robust score (mean - 1 sd) over 3 friction sets x 2 seeds at the full 16 s run. Score per run = min over classes of min(purity, recovery), minus 0.5 x jammed share, 1.0 x lost share and 0.05 x t90/duration. Failed (unstable) runs score -1. Only candidates promoted to the full run are ranked; screened-only ones are in the log. Solver: dt 0.25 ms, contact timeconst 0.5 ms (stiffer than sorter.py's default; see optimize.py). Friction sets: mu 0.3, mu 0.4, mu 0.5.

| # | id | family | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | design (CAD, nominal mm) | sim spec (as printed) | stroke |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | I-c7efd18f | inserts | **0.364** | 0.382 +/- 0.018 | 0.367 | 49% / 100% | 79% / 74% | 89% / 44% | 0.0 | 0.0 | - (0/6) | PEN 6/6 (clr 0.01, pen 0.283) | square holes 5 (bar 1.2) / 2 (bar 1) | `inserts:h4p85b1p35,h1p85b1p15,pitch=85` | seesaw +/-10 deg (ends tip, neighbours alternate), 2 s per cycle, constant speed |
| 2 | P-8e00372e | plinko | **0.345** | 0.400 +/- 0.055 | 0.350 | 57% / 100% | 80% / 91% | 100% / 45% | 0.0 | 0.0 | - (0/6) | ok | rods L1 gap 4.7 (rod 2.6 wide, 2.2 tall) / L2 gap 1.6 (rod 2.3, 3.2) | `plinko` | seesaw +/-10 deg (ends tip, neighbours alternate), 2 s per cycle, constant speed |
| 3 | P-19e01862 | plinko | **0.336** | 0.383 +/- 0.047 | 0.367 | 52% / 100% | 85% / 90% | 100% / 44% | 0.0 | 0.0 | - (0/6) | ok | rods L1 gap 4.8 (rod 3.9 wide, 3.6 tall) / L2 gap 1.5 (rod 2.4, 3.6) | `plinko` | seesaw +/-13.5 deg (ends tip, neighbours alternate), 2.5 s per cycle, sine |
| 4 | P-fd614143 | plinko | **0.297** | 0.322 +/- 0.025 | 0.317 | 58% / 100% | 76% / 89% | 95% / 37% | 0.0 | 0.0 | - (0/6) | ok | rods L1 gap 5.5 (rod 2.6 wide, 2 tall) / L2 gap 1.7 (rod 3, 2.6) | `plinko` | seesaw +/-13 deg (ends tip, neighbours alternate), 1.3 s per cycle, sine |
| 5 | I-f4dd9351 | inserts | **0.273** | 0.342 +/- 0.070 | 0.309 | 45% / 100% | 67% / 61% | 100% / 42% | 0.0 | 0.5 | - (0/6) | PEN 6/6 (clr 0.05, pen 0.364) | square holes 3.3 (bar 1.9) / 1.8 (bar 1) | `inserts:h3p15b2p05,h1p65b1p15,pitch=105` | seesaw +/-13 deg (ends tip, neighbours alternate), 2.5 s per cycle, sine |
| 6 | P-7064526e | plinko | **0.207** | 0.283 +/- 0.076 | 0.233 | 66% / 100% | 69% / 96% | 100% / 33% | 0.0 | 0.0 | - (0/6) | ok | rods L1 gap 5 (rod 2.4 wide, 3 tall) / L2 gap 1.4 (rod 2, 2.6) | `plinko` | seesaw +/-10 deg (ends tip, neighbours alternate), 2 s per cycle, constant speed |
| 7 | P-733bb414 | plinko | **0.099** | 0.217 +/- 0.117 | 0.167 | 44% / 100% | 76% / 80% | 100% / 27% | 0.0 | 0.0 | - (0/6) | ok | rods L1 gap 4.1 (rod 3.1 wide, 3.2 tall) / L2 gap 1.6 (rod 2.7, 3.4) | `plinko` | seesaw +/-9 deg (ends tip, neighbours alternate), 1.5 s per cycle, sine |
| 8 | I-5982e4bd | inserts | **0.039** | 0.078 +/- 0.039 | 0.067 | 41% / 100% | 56% / 61% | 100% / 13% | 0.0 | 0.0 | - (0/6) | BEYOND 1 (particles past an opening they can't fit); PEN 6/6 (clr 0.04, pen 0.202) | square holes 3.7 (bar 1.5) / 1.7 (bar 1.4) | `inserts:h3p55b1p65,h1p55b1p55,pitch=100` | seesaw +/-11.5 deg (ends tip, neighbours alternate), 4.7 s per cycle, sine |

## Best of each family (style)

| # | id | family | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | design (CAD, nominal mm) | sim spec (as printed) | stroke |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | P-8e00372e | plinko | **0.345** | 0.400 +/- 0.055 | 0.350 | 57% / 100% | 80% / 91% | 100% / 45% | 0.0 | 0.0 | - (0/6) | ok | rods L1 gap 4.7 (rod 2.6 wide, 2.2 tall) / L2 gap 1.6 (rod 2.3, 3.2) | `plinko` | seesaw +/-10 deg (ends tip, neighbours alternate), 2 s per cycle, constant speed |
| 2 | I-c7efd18f | inserts | **0.364** | 0.382 +/- 0.018 | 0.367 | 49% / 100% | 79% / 74% | 89% / 44% | 0.0 | 0.0 | - (0/6) | PEN 6/6 (clr 0.01, pen 0.283) | square holes 5 (bar 1.2) / 2 (bar 1) | `inserts:h4p85b1p35,h1p85b1p15,pitch=85` | seesaw +/-10 deg (ends tip, neighbours alternate), 2 s per cycle, constant speed |
| 1 | C-4a07a203 | current | **0.406** | 0.514 +/- 0.108 | 0.394 | 99% / 100% | 100% / 62% | 80% / 90% | 6.3 | 0.8 | - (0/6) | PEN 4/6 (clr 0.13, pen 0.204) | TODAY on the bench: glued mesh inserts mesh5 / mesh2, 85 mm apart, on the default seesaw (+/-10 deg, 2 s) | `inserts:mesh5,mesh2,pitch=85` | seesaw +/-10 deg (ends tip, neighbours alternate), 2 s per cycle, constant speed |

## References (fixed, not tuned)

| id | what | robust | mean +/- sd | worst mu set | big (pasta, chickpea) pur / rec | rice pur / rec | quinoa pur / rec | jammed | lost | t90 s | flags | spec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P-7064526e | plinko_layers.py as in the repo: rods 5.0 / 1.4, one box on the default seesaw (+/-10 deg, 2 s) | 0.207 | 0.283 +/- 0.076 | 0.233 | 66% / 100% | 69% / 96% | 100% / 33% | 0.0 | 0.0 | - (0/6) | ok | `plinko` |
| P-8e00372e | the demo study's leader P-b192da7c (rods 4.7 / 1.6, made for a 37 Hz tool) on the default seesaw | 0.345 | 0.400 +/- 0.055 | 0.350 | 57% / 100% | 80% / 91% | 100% / 45% | 0.0 | 0.0 | - (0/6) | ok | `plinko` |
| I-c7efd18f | DEMO RIG the team built: printed 5 mm / 2 mm trays, 85 mm apart, on the default seesaw (+/-10 deg, 2 s, neighbours alternate) | 0.364 | 0.382 +/- 0.018 | 0.367 | 49% / 100% | 79% / 74% | 89% / 44% | 0.0 | 0.0 | - (0/6) | PEN 6/6 (clr 0.01, pen 0.283) | `inserts:h4p85b1p35,h1p85b1p15,pitch=85` |
| C-4a07a203 | TODAY on the bench: glued mesh inserts mesh5 / mesh2, 85 mm apart, on the default seesaw (+/-10 deg, 2 s) | 0.406 | 0.514 +/- 0.108 | 0.394 | 99% / 100% | 100% / 62% | 80% / 90% | 6.3 | 0.8 | - (0/6) | PEN 4/6 (clr 0.13, pen 0.204) | `inserts:mesh5,mesh2,pitch=85` |

## Best per drive

BioKEA's stage can only run the firmware stroke (constant speed); the demo rig is a vibrating tool (sine). Best full-run design for each, whether or not it is flagged:

| drive | id | family | robust | flags | design (CAD, nominal mm) | stroke |
|---|---|---|---|---|---|---|

## Count matrices of the top 3 (summed over the 6 full runs)

**1. I-c7efd18f (inserts) square holes 5 (bar 1.2) / 2 (bar 1); sim `inserts:h4p85b1p35,h1p85b1p15,pitch=85`**

| class \ ended in | on_h4p85b1p35 | on_h1p85b1p15 | catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 96 | 0 | 0 | 0 | 0 |
| rice | 36 | 134 | 10 | 0 | 0 |
| quinoa | 64 | 37 | 79 | 0 | 0 |

**2. P-8e00372e (plinko) rods L1 gap 4.7 (rod 2.6 wide, 2.2 tall) / L2 gap 1.6 (rod 2.3, 3.2); sim `plinko`**

| class \ ended in | layer_1_rods | layer_2_rods | layer_3_catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 96 | 0 | 0 | 0 | 0 |
| rice | 17 | 163 | 0 | 0 | 0 |
| quinoa | 57 | 42 | 81 | 0 | 0 |

**3. P-19e01862 (plinko) rods L1 gap 4.8 (rod 3.9 wide, 3.6 tall) / L2 gap 1.5 (rod 2.4, 3.6); sim `plinko`**

| class \ ended in | layer_1_rods | layer_2_rods | layer_3_catch | between | lost |
|---|---|---|---|---|---|
| big (pasta, chickpea) | 96 | 0 | 0 | 0 | 0 |
| rice | 18 | 162 | 0 | 0 | 0 |
| quinoa | 71 | 30 | 79 | 0 | 0 |


Columns: purity = share of a bin's contents that belong to its class; recovery = share of a class that ends in its bin; jammed = particles per run stuck between bins (in a strip, slot or on a ledge); lost = out of the machine; t90 = seconds until 90% of the sample sits in its target bin (n/9 = runs that got there). Flags: FAIL = runs that went unstable or errored; PEN = particle-vs-gate overlap at or over 0.5 x the tightest gate clearance (near-size results untrustworthy); BEYOND = particles that ended past an opening their own size can't pass (soft contacts squeezed them through; should be 0, and is shown whenever it isn't).
