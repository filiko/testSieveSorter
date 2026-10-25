# EXPLORATORY: clump break-up leaderboard (study malaise)

Updated 2026-10-25 13:03 by `sim/opt_malaise.py` (15 candidates, 45 runs).

**EXPLORATORY. The sim ranks designs; it isn't calibrated against bench counts.** The clump's bond strengths are assumed (clumps.py) and so is the 5 mN damage line. Read the scores as a ranking, not as percentages.

**The clump is the bench-demo grain surrogate, not insects.** Every insect clump (`insect_malaise` and its class kinds, `insect_compact` + `insect_elongate`) blew up in `clumps.pack`'s pre-sim at 12:55 (QACC NaN), so the real Malaise clump waits for that fix.

- **Clump:** rice 30, quinoa 20, pasta 4, leaf 1, twig 2, dirt 6. Robust = mean - sd over the three bond sets (weak / medium / strong) at friction 0.4, seed 0, 4 s of seesaw after a 1 s settle, no spray (dry bonds: the hardest case).
- **Tower:** the breaker in a holder box on top of the demo rig's trays (5mm over 2mm over the catch pan), 85 mm apart. Every level rocks on its own hinge across its middle, and neighbours alternate (rocking.py).
- **Score per run:** 0.5 x break-up (0.75 x free share + 0.25 x speed from t90) + 0.3 x gentleness (half: share never over 5 mN while still in the clump; half: the peak-force p90 on a log scale, 1 at 5 mN, 0 at 500 mN) + 0.2 x sort (specimens in their ideal zone). A failed run scores -1.

## Top 10

| # | id | design and stroke | robust | mean | free | break | gentle | sort | largest cluster | peak force p90 (mN) | fails |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | B-32a7c82c | grid 11.4 mm (bars 2.3), pins 1.4 x 6.8 mm round every ~8 mm; seesaw +/-12 deg, 2.5 s + 0.35 mm buzz at 40 Hz | 0.638 | 0.726 | 97% | 0.94 | 29% | 85% | 1.7 | 236.98 | 0 |
| 2 | B-9759b7ac | grid 5.3 mm (bars 2.1), pins 3.8 x 4.8 mm round every ~9.9 mm; seesaw +/-6.5 deg, 5.1 s + 0.35 mm buzz at 40 Hz | 0.516 | 0.695 | 87% | 0.84 | 37% | 81% | 7.7 | 160.84 | 0 |
| 3 | B-50e62e6e | grid 5.2 mm (bars 1.9), pins 1.6 x 5 mm flat every ~14.3 mm; seesaw +/-9.5 deg, 5.3 s + 0.3 mm buzz at 40 Hz | 0.457 | 0.648 | 82% | 0.80 | 34% | 75% | 9.3 | 148.42 | 0 |
| 4 | B-bdf45f39 | grid 6.6 mm (bars 1.2), pins 2 x 9.6 mm flat every ~12.9 mm; seesaw +/-14 deg, 5 s + 0.4 mm buzz at 40 Hz | 0.441 | 0.635 | 85% | 0.83 | 32% | 62% | 9.0 | 174.44 | 0 |
| 5 | B-485029d3 | grid 8.3 mm (bars 1.1), pins 2.4 x 13 mm flat every ~10.1 mm; seesaw +/-10.5 deg, 3.5 s + 0.3 mm buzz at 40 Hz | 0.440 | 0.644 | 83% | 0.83 | 31% | 69% | 9.7 | 226.26 | 0 |
| 6 | B-2c750812 | grid 7.8 mm (bars 0.9), pins 2.2 x 14.4 mm flat every ~14.6 mm; seesaw +/-13 deg, 2.3 s + 0.3 mm buzz at 40 Hz | 0.385 | 0.628 | 82% | 0.78 | 34% | 69% | 10.3 | 143.87 | 0 |
| 7 | B-7d849a0a | grid 10 mm (bars 2), pins 2 x 15.2 mm flat every ~11.6 mm; seesaw +/-9.5 deg, 0.9 s + 0.15 mm buzz at 40 Hz | 0.343 | 0.580 | 80% | 0.76 | 42% | 38% | 11.3 | 118.92 | 0 |
| 8 | B-d99c7fda | grid 8 mm (bars 1), pins 1.6 x 9.8 mm flat every ~17.2 mm; seesaw +/-5.5 deg, 4.2 s + 0.2 mm buzz at 40 Hz | 0.331 | 0.563 | 75% | 0.68 | 39% | 52% | 13.3 | 120.99 | 0 |
| 9 | B-b42cc72b | grid 7.7 mm (bars 1.5), pins 3.4 x 9 mm round every ~6.3 mm; seesaw +/-6.5 deg, 4 s | 0.292 | 0.506 | 75% | 0.69 | 39% | 22% | 13.3 | 126.62 | 0 |
| 10 | B-92fb3697 | grid 6.6 mm (bars 1), pins 3.3 x 8 mm flat every ~18 mm; seesaw +/-8 deg, 2.9 s + 0.2 mm buzz at 40 Hz | 0.274 | 0.497 | 66% | 0.62 | 40% | 34% | 18.7 | 100.66 | 0 |

## References

| # | id | design and stroke | robust | mean | free | break | gentle | sort | largest cluster | peak force p90 (mN) | fails |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | B-5405ea9b | NO BREAKER: the clump straight onto the demo rig's 5 mm / 2 mm trays, default seesaw (+/-10 deg, 2 s) | 0.217 | 0.419 | 31% | 0.32 | 76% | 17% | 36.3 | 33.98 | 0 |
| 2 | B-75f277ad | cad/breaker_layer.py default (open 8, pins 2.5 x 12 every 10, round) on the default seesaw | 0.287 | 0.507 | 65% | 0.65 | 46% | 22% | 19.0 | 155.67 | 0 |
| 3 | B-9dcf5153 | the CAD default breaker, default seesaw + 0.3 mm buzz at 40 Hz (1.9 g, the tool's) | 0.479 | 0.672 | 85% | 0.84 | 35% | 75% | 8.7 | 131.46 | 0 |

## Per bond set, top 3 and the no-breaker reference

**B-32a7c82c**: grid 11.4 mm (bars 2.3), pins 1.4 x 6.8 mm round every ~8 mm; seesaw +/-12 deg, 2.5 s + 0.35 mm buzz at 40 Hz

| bond | score | free | t50 (s) | t90 (s) | largest | over 5 mN | in the clump over 5 mN | sort | lost | debris |
|---|---|---|---|---|---|---|---|---|---|---|
| weak | 0.837 | 100% | 0.02 | 0.03 | 1 | 100% | 17% | 87% | 0 | leaf: on_5mm 1; twig: on_5mm 2; dirt: catch 6 |
| medium | 0.719 | 100% | 0.05 | 0.17 | 1 | 100% | 67% | 83% | 2 | leaf: on_5mm 1; twig: on_5mm 1, on_2mm 1; dirt: catch 6 |
| strong | 0.621 | 91% | 0.42 | 1.73 | 3 | 100% | 96% | 83% | 1 | leaf: on_breaker 1; twig: on_breaker 1, on_2mm 1; dirt: catch 5, on_2mm 1 |

**B-9759b7ac**: grid 5.3 mm (bars 2.1), pins 3.8 x 4.8 mm round every ~9.9 mm; seesaw +/-6.5 deg, 5.1 s + 0.35 mm buzz at 40 Hz

| bond | score | free | t50 (s) | t90 (s) | largest | over 5 mN | in the clump over 5 mN | sort | lost | debris |
|---|---|---|---|---|---|---|---|---|---|---|
| weak | 0.857 | 100% | 0.02 | 0.06 | 1 | 100% | 11% | 87% | 1 | leaf: on_breaker 1; twig: on_breaker 2; dirt: catch 5, lost 1 |
| medium | 0.784 | 100% | 0.05 | 0.39 | 1 | 100% | 52% | 96% | 1 | leaf: on_breaker 1; twig: on_breaker 1, on_5mm 1; dirt: catch 5, lost 1 |
| strong | 0.445 | 61% | 0.75 | - | 21 | 98% | 91% | 59% | 0 | leaf: on_breaker 1; twig: on_breaker 1, on_5mm 1; dirt: catch 1, on_breaker 5 |

**B-50e62e6e**: grid 5.2 mm (bars 1.9), pins 1.6 x 5 mm flat every ~14.3 mm; seesaw +/-9.5 deg, 5.3 s + 0.3 mm buzz at 40 Hz

| bond | score | free | t50 (s) | t90 (s) | largest | over 5 mN | in the clump over 5 mN | sort | lost | debris |
|---|---|---|---|---|---|---|---|---|---|---|
| weak | 0.832 | 100% | 0.02 | 0.05 | 1 | 100% | 17% | 85% | 0 | leaf: on_breaker 1; twig: on_breaker 2; dirt: catch 5, on_2mm 1 |
| medium | 0.727 | 91% | 0.05 | 0.50 | 3 | 100% | 61% | 89% | 0 | leaf: on_breaker 1; twig: on_breaker 2; dirt: catch 4, on_breaker 1, on_2mm 1 |
| strong | 0.385 | 56% | 1.55 | - | 24 | 100% | 100% | 50% | 0 | leaf: on_breaker 1; twig: on_breaker 1, on_5mm 1; dirt: on_breaker 6 |

**B-5405ea9b**: no breaker; seesaw +/-10 deg, 2 s

| bond | score | free | t50 (s) | t90 (s) | largest | over 5 mN | in the clump over 5 mN | sort | lost | debris |
|---|---|---|---|---|---|---|---|---|---|---|
| weak | 0.704 | 93% | 0.04 | 0.19 | 2 | 94% | 28% | 35% | 0 | leaf: on_5mm 1; twig: on_5mm 1, on_2mm 1; dirt: catch 6 |
| medium | 0.258 | 2% | - | - | 53 | 20% | 19% | 7% | 0 | leaf: on_5mm 1; twig: on_5mm 1, on_2mm 1; dirt: on_5mm 6 |
| strong | 0.295 | 0% | - | - | 54 | 11% | 11% | 7% | 0 | leaf: on_5mm 1; twig: on_5mm 2; dirt: on_5mm 6 |

## Why the losers lost

- free at the end: top half 0.86, bottom half 0.68
- gentleness: top half 0.33, bottom half 0.42
- in the ideal zone: top half 0.73, bottom half 0.30
- largest cluster left: top half 7.94, bottom half 16.89
- peak force p90, mN: top half 181.80, bottom half 106.13
- rank correlation with the robust score (+ helps): vib_mm +0.84, ss_period +0.56, bar +0.43, ss_deg +0.31, tip=round +0.20, tip=flat -0.20
