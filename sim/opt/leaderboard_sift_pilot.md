# Leaderboard: PILOT (dry, short, not a result): the sift study's machinery

Generated 2026-10-27 19:48 by `sim/optimize.py` (study `sift_pilot`). 9 candidates, 42 sim runs so far.

**EXPLORATORY.** No real specimen has been measured: the insects are generated from textbook sizes (`sim/insects.py`), and the classes use body length, which no gate cuts directly.

**Separate trays, each moving on its own** (`boxes.py`, `sim/BOXES.md`): each box has its own tilt and vibration, prescribed kinematically (no actuator dynamics), and each seed draws its own phase for every box, since independent actuators don't hold a phase. The catch pan stays still.

**Weighted to the real mix.** The sample is stratified (24 / 24 / 12 specimens under 2 mm, 2-6 mm and over 6 mm); purity, jammed and lost are weighted to the real shares (71.0% / 26.6% / 2.4%, `insects.MALAISE_SHARES`). Recovery is per class, so the weights don't change it. Count matrices are raw counts.

Robustness sets: every friction set x every liquid set (dry: none) x 1 seeds.

**The sim ranks designs; it does not predict real percentages.** It is uncalibrated until `calibrate.py` has bench counts, has no water, rigid particles, and about 80 particles per run. Sizes are simulated at the as-printed opening, nominal - 0.15 mm (ASSUMED until the hole gauge is measured).

Ranked by the robust score (mean - 1 sd) over 3 friction sets x 1 seeds at the full 4 s run. Score per run = min over classes of min(purity, recovery), minus 0.5 x jammed share, 1.0 x lost share and 0.05 x t90/duration. Failed (unstable) runs score -1. Only candidates promoted to the full run are ranked; screened-only ones are in the log. Solver: dt 0.125 ms, contact timeconst 0.25 ms (stiffer than sorter.py's default; see optimize.py). Friction sets: mu 0.3, mu 0.4, mu 0.5.

| # | id | family | robust | mean +/- sd | worst mu set | > 6 mm pur / rec | 2-6 mm pur / rec | < 2 mm pur / rec | jammed | lost | t90 s | flags | design (CAD, nominal mm) | sim spec (as printed) | stroke |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | S-2997a7b5 | sift | **0.087** | 0.104 +/- 0.018 | 0.091 | 19% / 100% | 40% / 39% | 99% / 67% | 7.5 | 0.6 | 1.1 (3/3) | PEN 2/3 (clr 0.28, pen 0.370) | L1 square 3 (bar 1) / L2 square 1.6 (bar 1); boxes 55 mm apart | `inserts:h2p85b1p15_across,h1p45b1p15_across,pitch=55,holder=seesaw` | each box on its own (constant speed tilts): L1 0.295 mm at 40 Hz, 90 deg up (1.9 g); L2 0.295 mm at 40 Hz, 90 deg up (1.9 g); catch still |
| 2 | S-88c31ccf | sift | **0.081** | 0.101 +/- 0.020 | 0.078 | 18% / 86% | 33% / 79% | 100% / 22% | 0.6 | 4.1 | 0.5 (3/3) | PEN 3/3 (clr 0.07, pen 0.224) | L1 slot 3.8 x 12 (bar 0.8) / L2 round 1.1 (bar 1.4); boxes 55 mm apart | `inserts:s3p65x11p85b0p95_across,r0p95b1p55_across,pitch=55,holder=seesaw` | each box on its own (sine tilts): L1 0.096 mm at 94 Hz, 25 deg up (3.4 g); L2 tilt +/-7 deg / 3.3 s + 0.241 mm at 98 Hz, 70 deg up (9.3 g); catch still |
| 3 | S-71d846e7 | sift | **0.064** | 0.109 +/- 0.045 | 0.068 | 19% / 100% | 50% / 51% | 99% / 68% | 5.1 | 1.8 | 1.0 (3/3) | ok | L1 square 3 (bar 1) / L2 square 1.6 (bar 1); boxes 55 mm apart | `inserts:h2p85b1p15_across,h1p45b1p15_across,pitch=55,holder=seesaw` | each box on its own (constant speed tilts): L1 tilt +/-10 deg / 2 s + 0.295 mm at 40 Hz, 90 deg up (1.9 g); L2 tilt +/-10 deg / 2 s + 0.295 mm at 40 Hz, 90 deg up (1.9 g); catch still |
| 4 | S-10cb4529 | sift | **0.035** | 0.068 +/- 0.033 | 0.044 | 15% / 100% | 59% / 31% | 98% / 79% | 7.1 | 0.6 | 1.4 (3/3) | PEN 1/3 (clr 0.32, pen 0.429) | L1 round 4.3 (bar 1.6) / L2 slot 1.4 x 12 (bar 0.8); boxes 105 mm apart | `inserts:r4p15b1p75_across,s1p25x11p85b0p95_across,pitch=105,holder=seesaw` | each box on its own (sine tilts): L1 0.151 mm at 48 Hz, 85 deg up (1.4 g); L2 0.255 mm at 55 Hz, 5 deg up (3.1 g); catch still |

## Best of each family (style)

| # | id | family | robust | mean +/- sd | worst mu set | > 6 mm pur / rec | 2-6 mm pur / rec | < 2 mm pur / rec | jammed | lost | t90 s | flags | design (CAD, nominal mm) | sim spec (as printed) | stroke |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | S-2997a7b5 | sift | **0.087** | 0.104 +/- 0.018 | 0.091 | 19% / 100% | 40% / 39% | 99% / 67% | 7.5 | 0.6 | 1.1 (3/3) | PEN 2/3 (clr 0.28, pen 0.370) | L1 square 3 (bar 1) / L2 square 1.6 (bar 1); boxes 55 mm apart | `inserts:h2p85b1p15_across,h1p45b1p15_across,pitch=55,holder=seesaw` | each box on its own (constant speed tilts): L1 0.295 mm at 40 Hz, 90 deg up (1.9 g); L2 0.295 mm at 40 Hz, 90 deg up (1.9 g); catch still |
| 3 | C-1cfae593 | coupled | **0.069** | 0.084 +/- 0.015 | 0.071 | 20% / 100% | 49% / 39% | 99% / 67% | 10.9 | 0.6 | 1.3 (3/3) | PEN 2/3 (clr 0.28, pen 0.378) | COUPLED, the old seesaw: the same insect-cut trays 55 mm apart on rocking.py's seesaw (+/-10 deg, 2 s, neighbours locked in opposite phase, catch pan rocking) with one shared 0.3 mm buzz at 40 Hz | `inserts:h2p85b1p15_across,h1p45b1p15_across,pitch=55,holder=seesaw` | seesaw +/-10 deg (ends tip, neighbours alternate), 2 s per cycle, constant speed + 0.3 mm buzz at 40 Hz |

## References (fixed, not tuned)

| id | what | robust | mean +/- sd | worst mu set | > 6 mm pur / rec | 2-6 mm pur / rec | < 2 mm pur / rec | jammed | lost | t90 s | flags | spec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S-71d846e7 | LAYERS.md's insect-cut trays (square 3.0 / 1.6, ribs across, 55 mm apart), each box rocking +/-10 deg at 2 s with its own 40 Hz, 1.9 g buzz (0.3 mm) straight up, phases free; catch pan still | 0.064 | 0.109 +/- 0.045 | 0.068 | 19% / 100% | 50% / 51% | 99% / 68% | 5.1 | 1.8 | 1.0 (3/3) | ok | `inserts:h2p85b1p15_across,h1p45b1p15_across,pitch=55,holder=seesaw` |
| S-2997a7b5 | the same trays and buzz, no tilt | 0.087 | 0.104 +/- 0.018 | 0.091 | 19% / 100% | 40% / 39% | 99% / 67% | 7.5 | 0.6 | 1.1 (3/3) | PEN 2/3 (clr 0.28, pen 0.370) | `inserts:h2p85b1p15_across,h1p45b1p15_across,pitch=55,holder=seesaw` |
| C-1cfae593 | COUPLED, the old seesaw: the same insect-cut trays 55 mm apart on rocking.py's seesaw (+/-10 deg, 2 s, neighbours locked in opposite phase, catch pan rocking) with one shared 0.3 mm buzz at 40 Hz | 0.069 | 0.084 +/- 0.015 | 0.071 | 20% / 100% | 49% / 39% | 99% / 67% | 10.9 | 0.6 | 1.3 (3/3) | PEN 2/3 (clr 0.28, pen 0.378) | `inserts:h2p85b1p15_across,h1p45b1p15_across,pitch=55,holder=seesaw` |

## Count matrices of the top 3 (summed over the 3 full runs)

**1. S-2997a7b5 (sift) L1 square 3 (bar 1) / L2 square 1.6 (bar 1); boxes 55 mm apart; sim `inserts:h2p85b1p15_across,h1p45b1p15_across,pitch=55,holder=seesaw`**

| class \ ended in | on_h2p85b1p15_across | on_h1p45b1p15_across | catch | between | lost |
|---|---|---|---|---|---|
| > 6 mm | 36 | 0 | 0 | 0 | 0 |
| 2-6 mm | 28 | 28 | 1 | 15 | 0 |
| < 2 mm | 0 | 16 | 48 | 7 | 1 |

**2. S-88c31ccf (sift) L1 slot 3.8 x 12 (bar 0.8) / L2 round 1.1 (bar 1.4); boxes 55 mm apart; sim `inserts:s3p65x11p85b0p95_across,r0p95b1p55_across,pitch=55,holder=seesaw`**

| class \ ended in | on_s3p65x11p85b0p95_across | on_r0p95b1p55_across | catch | between | lost |
|---|---|---|---|---|---|
| > 6 mm | 31 | 4 | 0 | 1 | 0 |
| 2-6 mm | 15 | 57 | 0 | 0 | 0 |
| < 2 mm | 4 | 44 | 16 | 1 | 7 |

**3. S-71d846e7 (sift) L1 square 3 (bar 1) / L2 square 1.6 (bar 1); boxes 55 mm apart; sim `inserts:h2p85b1p15_across,h1p45b1p15_across,pitch=55,holder=seesaw`**

| class \ ended in | on_h2p85b1p15_across | on_h1p45b1p15_across | catch | between | lost |
|---|---|---|---|---|---|
| > 6 mm | 36 | 0 | 0 | 0 | 0 |
| 2-6 mm | 27 | 37 | 1 | 7 | 0 |
| < 2 mm | 0 | 14 | 49 | 6 | 3 |


Columns: purity = share of a bin's contents that belong to its class; recovery = share of a class that ends in its bin; jammed = particles per run stuck between bins (in a strip, slot or on a ledge); lost = out of the machine; t90 = seconds until 90% of the sample sits in its target bin (n/9 = runs that got there). Flags: FAIL = runs that went unstable or errored; PEN = particle-vs-gate overlap at or over 0.5 x the tightest gate clearance (near-size results untrustworthy); BEYOND = particles that ended past an opening their own size can't pass (soft contacts squeezed them through; should be 0, and is shown whenever it isn't).
