# EXPLORATORY: clump break-up leaderboard (study malaise)

Updated 2026-10-25 13:07 by `sim/opt_malaise.py` (23 candidates, 69 runs).

**EXPLORATORY. The sim ranks designs; it isn't calibrated against bench counts.** The clump's bond strengths are assumed (clumps.py) and so is the 5 mN damage line. Read the scores as a ranking, not as percentages.

**The clump is the bench-demo grain surrogate, not insects.** Every insect clump (`insect_malaise` and its class kinds, `insect_compact` + `insect_elongate`) blew up in `clumps.pack`'s pre-sim at 12:55 (QACC NaN), so the real Malaise clump waits for that fix.

- **Clump:** rice 30, quinoa 20, pasta 4, leaf 1, twig 2, dirt 6. Robust = mean - sd over the three bond sets (weak / medium / strong) at friction 0.4, seed 0, 4 s of seesaw after a 1 s settle, no spray (dry bonds: the hardest case).
- **Tower:** the breaker in a holder box on top of the demo rig's trays (5mm over 2mm over the catch pan), 85 mm apart. Every level rocks on its own hinge across its middle, and neighbours alternate (rocking.py).
- **Score per run:** 0.5 x break-up (0.75 x free share + 0.25 x speed from t90) + 0.3 x gentleness (half: share never over 5 mN while still in the clump; half: the peak-force p90 on a log scale, 1 at 5 mN, 0 at 500 mN) + 0.2 x sort (specimens in their ideal zone). A failed run scores -1.

## Top 10

| # | id | design and stroke | robust | mean | free | break | gentle | sort | largest cluster | peak force p90 (mN) | fails |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | B-87f42099 | grid 8.9 mm (bars 1.2), pins 2 x 7.6 mm flat every ~11.8 mm; seesaw +/-8 deg, 3.5 s + 0.35 mm buzz at 40 Hz | 0.683 | 0.756 | 100% | 0.97 | 31% | 90% | 1.0 | 274.79 | 0 |
| 2 | B-c5be78ea | grid 10.7 mm (bars 1.9), pins 3.6 x 4 mm flat every ~11.4 mm; seesaw +/-10 deg, 4.3 s + 0.3 mm buzz at 40 Hz | 0.641 | 0.725 | 98% | 0.92 | 31% | 87% | 1.3 | 231.82 | 0 |
| 3 | B-32a7c82c | grid 11.4 mm (bars 2.3), pins 1.4 x 6.8 mm round every ~8 mm; seesaw +/-12 deg, 2.5 s + 0.35 mm buzz at 40 Hz | 0.638 | 0.726 | 97% | 0.94 | 29% | 85% | 1.7 | 236.98 | 0 |
| 4 | B-8a2ce165 | grid 10.2 mm (bars 2.1), pins 2.7 x 8.8 mm round every ~9.8 mm; seesaw +/-8.5 deg, 1.2 s + 0.35 mm buzz at 40 Hz | 0.619 | 0.729 | 96% | 0.92 | 32% | 87% | 1.7 | 216.99 | 0 |
| 5 | B-9759b7ac | grid 5.3 mm (bars 2.1), pins 3.8 x 4.8 mm round every ~9.9 mm; seesaw +/-6.5 deg, 5.1 s + 0.35 mm buzz at 40 Hz | 0.516 | 0.695 | 87% | 0.84 | 37% | 81% | 7.7 | 160.84 | 0 |
| 6 | B-e672c94b | grid 5 mm (bars 2.4), pins 3.7 x 6 mm flat every ~9.7 mm; seesaw +/-9 deg, 1.5 s + 0.35 mm buzz at 40 Hz | 0.504 | 0.683 | 87% | 0.85 | 34% | 78% | 7.7 | 191.63 | 0 |
| 7 | B-b2df0d7b | grid 7.9 mm (bars 2.2), pins 1.7 x 11.8 mm flat every ~11.5 mm; seesaw +/-10.5 deg, 2.4 s + 0.25 mm buzz at 40 Hz | 0.461 | 0.648 | 84% | 0.83 | 32% | 70% | 9.3 | 187.30 | 0 |
| 8 | B-50e62e6e | grid 5.2 mm (bars 1.9), pins 1.6 x 5 mm flat every ~14.3 mm; seesaw +/-9.5 deg, 5.3 s + 0.3 mm buzz at 40 Hz | 0.457 | 0.648 | 82% | 0.80 | 34% | 75% | 9.3 | 148.42 | 0 |
| 9 | B-bdf45f39 | grid 6.6 mm (bars 1.2), pins 2 x 9.6 mm flat every ~12.9 mm; seesaw +/-14 deg, 5 s + 0.4 mm buzz at 40 Hz | 0.441 | 0.635 | 85% | 0.83 | 32% | 62% | 9.0 | 174.44 | 0 |
| 10 | B-485029d3 | grid 8.3 mm (bars 1.1), pins 2.4 x 13 mm flat every ~10.1 mm; seesaw +/-10.5 deg, 3.5 s + 0.3 mm buzz at 40 Hz | 0.440 | 0.644 | 83% | 0.83 | 31% | 69% | 9.7 | 226.26 | 0 |

## References

| # | id | design and stroke | robust | mean | free | break | gentle | sort | largest cluster | peak force p90 (mN) | fails |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | B-5405ea9b | NO BREAKER: the clump straight onto the demo rig's 5 mm / 2 mm trays, default seesaw (+/-10 deg, 2 s) | 0.217 | 0.419 | 31% | 0.32 | 76% | 17% | 36.3 | 33.98 | 0 |
| 2 | B-75f277ad | cad/breaker_layer.py default (open 8, pins 2.5 x 12 every 10, round) on the default seesaw | 0.287 | 0.507 | 65% | 0.65 | 46% | 22% | 19.0 | 155.67 | 0 |
| 3 | B-9dcf5153 | the CAD default breaker, default seesaw + 0.3 mm buzz at 40 Hz (1.9 g, the tool's) | 0.479 | 0.672 | 85% | 0.84 | 35% | 75% | 8.7 | 131.46 | 0 |

## Per bond set, top 3 and the no-breaker reference

**B-87f42099**: grid 8.9 mm (bars 1.2), pins 2 x 7.6 mm flat every ~11.8 mm; seesaw +/-8 deg, 3.5 s + 0.35 mm buzz at 40 Hz

| bond | score | free | t50 (s) | t90 (s) | largest | over 5 mN | in the clump over 5 mN | sort | lost | debris |
|---|---|---|---|---|---|---|---|---|---|---|
| weak | 0.831 | 100% | 0.02 | 0.05 | 1 | 100% | 13% | 89% | 1 | leaf: on_breaker 1; twig: on_breaker 1, on_5mm 1; dirt: catch 5, on_5mm 1 |
| medium | 0.779 | 100% | 0.06 | 0.12 | 1 | 100% | 46% | 93% | 0 | leaf: on_breaker 1; twig: on_breaker 1, on_5mm 1; dirt: catch 6 |
| strong | 0.657 | 100% | 0.44 | 1.39 | 1 | 100% | 96% | 89% | 1 | leaf: on_breaker 1; twig: on_5mm 2; dirt: catch 6 |

**B-c5be78ea**: grid 10.7 mm (bars 1.9), pins 3.6 x 4 mm flat every ~11.4 mm; seesaw +/-10 deg, 4.3 s + 0.3 mm buzz at 40 Hz

| bond | score | free | t50 (s) | t90 (s) | largest | over 5 mN | in the clump over 5 mN | sort | lost | debris |
|---|---|---|---|---|---|---|---|---|---|---|
| weak | 0.821 | 100% | 0.02 | 0.05 | 1 | 100% | 17% | 83% | 1 | leaf: on_5mm 1; twig: on_breaker 1, on_5mm 1; dirt: catch 5, lost 1 |
| medium | 0.738 | 100% | 0.06 | 0.21 | 1 | 100% | 63% | 89% | 1 | leaf: on_5mm 1; twig: on_breaker 1, on_5mm 1; dirt: catch 5, on_5mm 1 |
| strong | 0.617 | 93% | 0.46 | 2.75 | 2 | 100% | 91% | 89% | 0 | leaf: on_5mm 1; twig: on_5mm 2; dirt: catch 5, on_5mm 1 |

**B-32a7c82c**: grid 11.4 mm (bars 2.3), pins 1.4 x 6.8 mm round every ~8 mm; seesaw +/-12 deg, 2.5 s + 0.35 mm buzz at 40 Hz

| bond | score | free | t50 (s) | t90 (s) | largest | over 5 mN | in the clump over 5 mN | sort | lost | debris |
|---|---|---|---|---|---|---|---|---|---|---|
| weak | 0.837 | 100% | 0.02 | 0.03 | 1 | 100% | 17% | 87% | 0 | leaf: on_5mm 1; twig: on_5mm 2; dirt: catch 6 |
| medium | 0.719 | 100% | 0.05 | 0.17 | 1 | 100% | 67% | 83% | 2 | leaf: on_5mm 1; twig: on_5mm 1, on_2mm 1; dirt: catch 6 |
| strong | 0.621 | 91% | 0.42 | 1.73 | 3 | 100% | 96% | 83% | 1 | leaf: on_breaker 1; twig: on_breaker 1, on_2mm 1; dirt: catch 5, on_2mm 1 |

**B-5405ea9b**: no breaker; seesaw +/-10 deg, 2 s

| bond | score | free | t50 (s) | t90 (s) | largest | over 5 mN | in the clump over 5 mN | sort | lost | debris |
|---|---|---|---|---|---|---|---|---|---|---|
| weak | 0.704 | 93% | 0.04 | 0.19 | 2 | 94% | 28% | 35% | 0 | leaf: on_5mm 1; twig: on_5mm 1, on_2mm 1; dirt: catch 6 |
| medium | 0.258 | 2% | - | - | 53 | 20% | 19% | 7% | 0 | leaf: on_5mm 1; twig: on_5mm 1, on_2mm 1; dirt: on_5mm 6 |
| strong | 0.295 | 0% | - | - | 54 | 11% | 11% | 7% | 0 | leaf: on_5mm 1; twig: on_5mm 2; dirt: on_5mm 6 |

## Why the losers lost

- free at the end: top half 0.90, bottom half 0.74
- gentleness: top half 0.32, bottom half 0.38
- in the ideal zone: top half 0.78, bottom half 0.46
- largest cluster left: top half 5.83, bottom half 14.13
- peak force p90, mN: top half 204.95, bottom half 136.25
- rank correlation with the robust score (+ helps): vib_mm +0.68, bar +0.48, pin_h -0.34, ss_period +0.31, open +0.23, pin_d +0.13
