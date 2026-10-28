# Evidence: what we know works, and what we don't yet

The honest status of the design, claim by claim. Update this page whenever a print or a bench run lands.

## Bottom line (Oct 27, 2026)

- **The concept is proven, but not by us.**
  - EntoSieve, the published system BugSorter upgrades, sorts real Malaise insects into body-length classes at 92–99% with a stack of round-hole sieves.
  - Forum's printed 5 mm tray sorts pasta from rice on a handheld tool.
- **Our parts are printable, but none has been tested.**
  - Every part passes its geometry checks, and the breaker is sliced.
  - Nothing printed from this repo has been measured or run. All seven bench CSVs in `sim/bench/` still hold only their example rows.
- **Every number we quote for the breaker and the sorting is from an uncalibrated sim.** It ranks designs. It doesn't predict bench percentages.
  - It now models the liquid: a bath with buoyancy, drag and added mass, checked against published settling data.
  - It doesn't model the liquid's flow. Rebuilt in the sim, EntoSieve gets the right body-length cut, but only 28–81% per class against the paper's 96–100%.
- **A day of bench work turns this into a yes or a no.** See [The path to "it works"](#the-path-to-it-works).

## Claim by claim

| Claim | Evidence | Kind | How strong |
|---|---|---|---|
| A stack of sieves sorts Malaise insects by size | EntoSieve ([Ascenzi et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12225705/)): round holes of 1.5, 3 and 5 mm gave 95.6 / 97.6 / 98.4 / 100% per length class, in water, with a gentle up-and-down stroke | Published, physical | Strong for the concept. It isn't our parts or our motion. |
| A printed screen can replace glued mesh | Forum's bench prototype: a printed 5 mm square-grid tray on a DeWalt 20V MAX tool sorts ditalini from rice (photos and video in `media/`, local only) | Physical, qualitative | Real, but no counts, one tray, grain surrogates only |
| The sim's liquid behaves like water and ethanol | Settling speeds within 4% of the standard sphere curve and within 12.5% of the ellipsoid correlations. Floating and neutral bodies match Archimedes (`sim/LIQUID.md`, checks 1–5). | Sim against published data | Good for one body in still liquid. There's no flow: no jets through the holes, no sloshing. |
| The sim reproduces EntoSieve | **The cut, yes.** Specimens lie flat on the plate (83–90%), and none narrower than a hole but longer than it passed dry (0 of 567; 1–1.6% wet), as in the paper. **The efficiencies, no.** After 40 strokes the sim levels off at 28 / 56 / 40 / 81% per class against 96 / 98 / 98 / 100% (`sim/ENTOSIEVE.md`). | Sim against published physical data | The sim's sorting rule is right. How fast specimens get through the holes isn't, and the missing flow is a large part of the gap. Nothing was tuned to match. |
| Our parts print as designed | CadQuery checks for every part: minimum feature vs two 0.4 mm lines, overhangs, bed fit (`cad/out/*_checks.json`). Bambu Studio slices: the breaker takes 57 min and 19.6 g (`sim/opt/print_plan_malaise.md`). | Software check | Good for printability. The printed apertures are unmeasured; `cad/hole_gauge.py` exists for that. |
| Our parts fit BugSorter's holder boxes | The box is rebuilt from a drawing that was itself reconstructed from four photos (`cad/frame_holder.py`). `WALL` and `LEDGE_T` are guesses adopted as working values. | None | **Unknown.** Calipers on one real box settle it in 10 minutes. |
| The breaker frees a clump | Sim (`sim/CLUMPS.md`). Insect clump, 35 specimens + leaf, twig and dirt: 9% freed without a breaker, 100% with breaker B-164f355a + buzz + spray (90% by 5 s). Real Malaise size mix on the same breaker: 25% dry, 90% with spray, in 4 s, one seed. | Sim | Ranking only. Bond strengths are invented: the sets bracket the clump's own loads by construction. Insect clumps were run on few seeds. **Under liquid it's different:** a Malaise clump on the seesaw, with no breaker, barely breaks under ethanol (0–10 of 190 bonds, against 80 dry), because it weighs a quarter as much (`sim/LIQUID.md` check 8). Run the breaker sprayed, not submerged, until the bench says otherwise. |
| The optimizer's breaker beats a hand-designed one | 0.630 vs 0.452, re-checked on freshly packed clumps; round 2's 0.700 leader fell to 0.42 on that check (`sim/opt/leaderboard_malaise.md`) | Sim | A fair ranking under the same assumptions. It used a grain-surrogate clump. |
| Separate seesawing trays sort the classes | Sim. On the seesaw alone, the demo rig scores robust 0.36: quinoa rides the 5 mm ribs (`sim/opt/VERIFY_SEESAW.md`). With ribs-across inserts and a 0.35 mm buzz, 44 of 45 fines reach the catch, but plain rice shakes through 2 mm. The best separate-tray design scores 0.630, and contact-penetration flags fire on it (`sim/opt/leaderboard_seesaw.md`). | Sim | **Weak.** The architecture the product uses is the one the sim rates lowest. |
| A seesaw sorts at 99.8% | Sim: plinko rods 4.7 / 1.5 mm, ±14° + buzz (`sim/opt/leaderboard_seesaw.md`). It's **one box rocking as one piece**, not alternating trays. | Sim | Not re-run on fresh seeds: the verification batch stopped for memory. Plinko scores were shown to lean on soft contacts (robust 0.929 → 0.746 as contacts stiffen, `sim/opt/VERIFY.md`). |
| BugSorter's stage can drive the alternating seesaw | Geometry only: two push rods, R = 56.7 mm, turn the firmware's default 2 cm stroke into ±10°. Clearances were checked on the real solids at both ends of the stroke: 6.1 mm between boxes, 1.5 mm rod to lug (`cad/product.py`, `cad/PRODUCT.md`). | CAD | Never built. The stage's real stroke is unknown: `STEPS_PER_CM` is an uncalibrated placeholder in the firmware. **The drive assumes the stage moves vertically, but the team was told the bench unit moves horizontally.** If it does, the drive needs a bell crank, which isn't designed. |
| The buzz reaches the trays as in the sim | The sim's best runs shake the whole tower straight up by 0.35 mm at 40 Hz. In the build, the puck sits on the yoke, so the boxes get a ±0.35° rock instead. | None | **Unknown.** The stage's lead screw may stop the puck moving the yoke at all. Measure a box rim with a phone accelerometer. Moving the puck to the base plate would match the sim. |
| Specimens come out undamaged | The sim logs impact loads and found that the drops between levels hit hardest, which led to the centre-pivot holder. No damage threshold is validated. | Sim | None for legs and antennae. Only a bench run with real specimens answers it. |

## Known gaps in the sim

| Gap | Why it matters | Where it's written up |
|---|---|---|
| **No flow in the liquid** | The bath (`sim/liquid.py`) gives buoyancy, drag and added mass. But the liquid in each box just moves with the box by a fixed fraction (`entrain`, unknown, 0–1): no jets through the holes, no sloshing, no stirring. The EntoSieve rebuild shows the cost. The `sift` study scores every design at entrain 0, 0.5 and 1. | `sim/LIQUID.md`, `sim/ENTOSIEVE.md` |
| Wet clump bonds | The bond strengths were set from dry loads. Under liquid there's no meniscus, so only entanglement holds a clump, and nobody has measured it. | `sim/LIQUID.md` check 8 |
| Clump bond strengths are assumed | Nobody has measured what holds a Malaise clump together. The weak, medium and strong sets are tied to loads in the sim itself. | `sim/CLUMPS.md` |
| Friction uncalibrated | Every score is averaged over three assumed friction sets (0.3 / 0.4 / 0.5). `sim/calibrate.py` waits for bench counts. | `sim/BENCH.md` |
| Soft contacts | Tight gaps (0.05–0.3 mm of room) are close to the contact softness. Some winners lose points with stiffer contacts. | `sim/opt/VERIFY.md`, `sim/PERF.md` |
| End-first passage | Answered for a gentle wet stroke: in the EntoSieve rebuild, specimens lie flat and the holes cut by body length, as in the paper. Not checked yet under faster tilts and buzzes. | `sim/ENTOSIEVE.md` |
| Insect bodies | Shapes, densities and damage rates are textbook values, not measured specimens | `sim/INSECT_AUDIT.md` |
| Seesaw profile | Constant angular speed vs a sine, and the period: both assumed | `docs/SYSTEM.md` §3 |

## The path to "it works"

In order. Each step can stop the project or redirect it, so do them in this order.

| # | Step | Time | Passes if | Record in |
|---|---|---|---|---|
| 1 | **Measure.** Calipers on a real holder box, insert and stage tab. Command a 2 cm stroke and measure it. | 30 min | Parts fit after updating `frame_holder.py` (the inserts and breaker follow) | `cad/WORKING_DIMENSIONS.md` |
| 2 | **Print the gauge and the breaker.** `hole_gauge.py`, then B-164f355a. | ~1.5 h | Printed apertures within 0.1 mm of nominal | `sim/bench/openings.csv` |
| 3 | **Breaker go / no-go.** Three clumps, with and without the breaker, spray on. Film from above. | 45 min | Clearly faster break-up with the breaker, and no more broken legs than teasing by hand | `sim/bench/clump_breakup.csv` (BENCH.md step 10) |
| 4 | **Sorting counts.** Grain surrogates first, then a real sample: BENCH.md steps 3–4 | 1 h | Counts per zone for 3 configurations × 3 repeats | `sim/bench/bench_counts.csv` |
| 4b | **How much the liquid moves with a box** (proposed). Shake one tray under ethanol with a pinch of ground pepper in the liquid, and film it from the side in slow motion. If the flecks ride along with the tray, entrain is near 1; if they hang still while the tray moves, it's near 0. | 15 min | A number for `entrain`, the sim's biggest wet unknown | `sim/opt/LOG.md` |
| 5 | **Calibrate and hold one out.** `sim/calibrate.py`, then BENCH.md step 5 | 30 min | The sim, fitted on two configurations, ranks the third correctly | `sim/opt/LOG.md` |
| 6 | **Build the drive** (`cad/PRODUCT.md`) only after steps 3–5 pass | half a day | Neighbours alternate at the commanded angle, and nothing binds | `cad/PRODUCT.md` |

What "works" should mean, proposed:
- **Breaking up:** at least 90% of specimens freed within 60 s, with no more damage than teasing by hand.
- **Sorting:** match EntoSieve's 92–99% per class on a real Malaise sample.

If step 3 fails, the breaker is the thing to fix, and the optimizer can search again with the measured clump behaviour. If step 5 fails, the sim's rankings can't be trusted until the flow gap is closed. `sim/LIQUID.md` has a first, unvalidated sketch of the flow through the holes (`screen_flow=1`).
