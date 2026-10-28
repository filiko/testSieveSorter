# EntoSieve in the sim: dry and wet, against the paper

EntoSieve sorted real Malaise samples by body length in water ([Ascenzi et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12225705/); build files, firmware and raw counts on [OSF](https://osf.io/6t25n/)). It is published physical data on wet insects going through holes, so it is the best check the wet sim ([LIQUID.md](LIQUID.md)) can get. This file rebuilds that setup, runs it dry and wet, and compares per-class efficiency with the paper's. Nothing was tuned to match.

## Summary

- **The length cut comes out, dry and wet.** On every plate, specimens narrower than the hole but longer than it stay on it. Dry: 0 of 567 such specimen-plate pairs passed. Wet: 6-9 of 567 (1-1.6 %) in 8 strokes, four distinct specimens, two of them within 2 % of the hole size; 6 of 127 (4.7 %) in 40 strokes. The paper also has no specimen in a finer fraction than its class. The sim's reason: specimens lie flat on the plate (83-90 % of them with the long axis within 20° of it, 3-4 % more than 45°), and nothing in a gentle up-and-down stroke stands them on end. So INSECT_AUDIT's open question is answered for this regime: **holes cut by body length because the specimens lie flat** (with rigid legs: section 4).
- **The efficiencies don't.** The paper's test 1 gives 95.6 / 97.6 / 98.4 / 100 % for A / B / C / D after 6 min (127 strokes) per plate. The sim, in water with the liquid in the container still (entrain 0, the closest setting for EntoSieve):
  - after 8 strokes: 14.9 / 29.9 / 31.7 / 88.2 % (9 runs); dry: 14.3 / 37.1 / 31.7 / 100 %;
  - after 40 strokes: 28.2 / 55.8 / 40.0 / 81.4 % (2 runs). Passage levels off after about 20 strokes, so running longer won't close the gap. Extrapolating the first 8 strokes' rate would have predicted 94 / 99 / 99 %; the 40-stroke runs show that extrapolation is wrong.
- **Dry, the stroke does nothing.** Everything that passes dry passes as the specimens are first set down. Wet, the water lifts them off the plate every stroke and passage goes on for about 20 strokes.
- **What limits passage in the sim:**
  - **no stirring:** the plate moves straight up and down and the sim's liquid moves uniformly, so nothing moves a specimen sideways. A specimen over a hole goes through the same hole down and up every stroke; one over solid metal lands on the same spot every stroke;
  - **no sinking:** the smallest specimens (span under 1.5 mm, settling at a fraction of a mm/s) hang near the surface and never get below the plate's lowest position: 0 of 54 passed in 8 strokes at entrain 0 and 0.5;
  - **rigid legs:** specimens under 1.5 mm long whose legs span over 4 mm never passed, dry or wet (0 of 18);
  - EntoSieve's plate drives the water through its holes as jets (the plate speed over the open fraction, about 320 mm/s for the 1.5 mm plate). An exploratory hole-flow sketch (section 5) roughly doubles to triples passage per stroke (A 39 % after 8 strokes instead of 15 %), so the missing flow is a large part of the gap.

## 1. What EntoSieve did (from the paper and its OSF files)

| Item | Value | Source |
|---|---|---|
| Container | 3D-printed sieve bucket, bore 138.2 mm, 100 mm tall; the plate rests on a ledge 15 mm above the bottom, inner radius 66.7 mm (open plate 133.4 mm across) | `bucket.stl` on OSF, measured with trimesh |
| Plates | aluminium perforated plates, **1 mm** thick, cut to 138 mm discs | paper §2.1 |
| Holes | round, **1.5 mm** (MA), **3 mm** (MB), **5 mm** (MC) | paper §2.3, Table 2 |
| Hole pitch | not given | ASSUMED: the common punched-plate layouts Rv 1.5-3, Rv 3-5, Rv 5-8 (60° staggered; open area 23 %, 33 %, 35 %) |
| Order | smallest plate first: MA, then the retained fraction on MB, then on MC | paper §2.3 |
| Classes | body length, front of head to tip of last tergite: **A < 1.5, B 1.5-3, C 3-5, D > 5 mm** | paper §2.3, §2.3.2 |
| Motion | straight up and down; a stepper on a lead screw | paper §2.1 |
| Speed | 34-104 mm/s, "we recommend setting it to the maximum" | paper §2.2 |
| Firmware | FlexyStepper, acceleration **100 mm/s²**, speed knob mapped to 25-100 mm/s, stroke knob from 25 mm to the axis length | `EntoSive_v1_1.ino` on OSF |
| Stroke | set "so that the sieve container fully emerges with each oscillation", so water flushes up through the holes as it descends | paper §2.2 |
| Water | 30-50 mm above the plate at the lowest position, 3.5-4.0 L | paper §2.2 |
| Duration | test 1: 6 min per plate; test 2: 20 min per plate (MC 10 min) | paper §2.3, §3.1 |
| Sample | Malaise samples in 96 % ethanol, poured into the water; specimens over 30 mm removed by hand | paper §2.2-2.3 |
| Efficiency | per class X: 100 - intruders × 100 / specimens of X, intruders = specimens of X counted in another fraction | paper §2.3.1 |

**Results, test 1 (sample 1, 10,276 specimens, 6 min per plate):** A 95.56 %, B 97.57 %, C 98.39 %, D 100 %; mean 97.88 % (paper Table 3; confirmed against `EntoSieve_tests.xlsx`, sheet Table_S1_efficiency). **Test 2** (sample 2, 20 min per plate): 78.32 / 96.0 / 94.65 / 100 %; leafhoppers that float were most of the A intruders.

**Every intruder the paper lists sits in a *coarser* fraction** (Table S1: A in B 191, A in C 50, A in D 13, B in C 54, B in D 13, C in D 20 for test 1). There is no row for a specimen in a finer fraction than its class, for example a 2.5 mm fly that went through the 1.5 mm holes. So the paper's numbers say two things: almost every specimen shorter than a hole went through it within 6 min, and almost none longer than the hole did, although a 2-3 mm fly is narrower than 1.5 mm.

## 2. The setup in the sim

| Item | Sim | Status |
|---|---|---|
| Container | `entosieve:<plate>` (`designs_entosieve.py`): 48-segment cylinder, bore 138.2 mm, wall to 85 mm above the plate | from `bucket.stl` |
| Plates | 1 mm thick, round holes as 12-gons of the circle's area on a 60° staggered grid, only whole holes inside the 133.4 mm opening: `r1p5b1p5` (1,749 holes, 22 % open, 22,892 geoms), `r3b2` (622 holes, 31 %, 8,199 geoms), `r5b3` (230 holes, 32 %, 3,079 geoms) | pitch ASSUMED (above) |
| Stroke | `flexy`: 50 mm up and down, 100 mm/s² to at most 100 mm/s, so 71 mm/s peak and 2.83 s per cycle | stroke ASSUMED: 40 mm of water + 10 mm out |
| Water | lab-fixed surface 40 mm over the plate at its lowest position; the plate comes 10 mm out at the top | ASSUMED mid of 30-50 mm |
| Liquid in the container | `entrain` 0 (still bath: water drains through the plate at the plate's speed), 0.5, 1 (moves with the container) | uncertain by design ([LIQUID.md](LIQUID.md)) |
| Specimens | `MALAISE_MIX_STRATIFIED` (24 + 24 + 12, 0.3-20 mm), weighted to the real shares with `MALAISE_SHARES`; the same 60 specimens on all three plates (same seed) | |
| Passed | the specimen's root goes below the plate's lowest position (lab z). The plate never comes back there, so a specimen that has sunk that far can't be swept back up; one still inside the 50 mm the plate sweeps can | |
| Catch | a floor 60 mm under the plate that moves with the container (EntoSieve's bowl stands still) | ASSUMED; it only holds passed specimens |
| Sequence | each plate is its own run with all 60 specimens; a specimen's fraction is the first plate it passed (MA, then MB, then MC) | the 3 mm plate sees the fine specimens too, at low load this barely matters |
| Contacts | dt 0.125 ms, timeconst 0.25 ms (the insect setting) | |
| Runs | 3 plates × 3 seeds × 3 friction sets (0.3, 0.4, 0.5) × {dry, water entrain 0, 0.5, 1} = 108 runs of 8 strokes; plus 6 runs of 40 strokes (water, entrain 0, seeds 0-1, friction 0.4) and 9 exploratory hole-flow runs (section 5) | |
| Time | 8 cycles (22.6 s) per plate, against 127 cycles (6 min) in test 1; 40 cycles for one condition | compute |
| Load | 60 specimens on the plate against 10,276 | compute |

Run it: `python entosieve.py run --workers 8 --cycles 8`, then `python entosieve.py report --cycles 8` (tables below). One recorded run for the replay page: `python entosieve.py one --plate MC --condition water_e0 --cycles 2 --out out/runs/ento_MC`.

## 3. Results: sim against the paper

Per-class efficiency (%), the share of each length class that ends in its own fraction, weighted to the real class shares. ± is the spread of one run's value over the 3 seeds × 3 friction sets. The sim ran 8 strokes per plate; the paper ran 127 (test 1) and about 420 (test 2).

| | A < 1.5 mm | B 1.5-3 | C 3-5 | D > 5 | Mean |
|---|---|---|---|---|---|
| **Paper, test 1** (6 min per plate) | **95.6** | **97.6** | **98.4** | **100** | **97.9** |
| Paper, test 2 (20 min per plate) | 78.3 | 96.0 | 94.7 | 100 | 92.2 |
| Sim, dry | 14.3 ± 6.7 | 37.1 ± 7.2 | 31.7 ± 18.3 | 100.0 ± 0.0 | 45.8 |
| Sim, water, entrain 0 | 14.9 ± 7.5 | 29.9 ± 7.3 | 31.7 ± 16.0 | 88.2 ± 16.2 | 41.2 |
| Sim, water, entrain 0.5 | 12.5 ± 6.5 | 23.3 ± 11.0 | 28.6 ± 21.4 | 91.4 ± 15.1 | 38.9 |
| Sim, water, entrain 1 | 14.9 ± 9.7 | 11.9 ± 4.5 | 28.6 ± 15.4 | 88.8 ± 14.0 | 36.0 |

Specimens per condition: A 168, B 189, C 63, D 120 (9 runs × 60). As run, the sim is far below the paper on A, B and C. It ran 6 % of the paper's sieving time; the tables below show how passage grows with time, and the 40-stroke runs show that it levels off well short of the paper.

**Share of each class through each plate** (weighted, all runs):

| Condition | Plate | A | B | C | D |
|---|---|---|---|---|---|
| dry | 1.5 mm | 14 % | 0 % | 0 % | 0 % |
| dry | 3 mm | 45 % | 37 % | 0 % | 0 % |
| dry | 5 mm | 46 % | 27 % | 32 % | 0 % |
| water e0 | 1.5 mm | 15 % | 0 % | 0 % | 0 % |
| water e0 | 3 mm | 16 % | 30 % | 3 % | 1 % |
| water e0 | 5 mm | 28 % | 32 % | 35 % | 11 % |
| water e0.5 | 1.5 mm | 12 % | 0 % | 0 % | 0 % |
| water e0.5 | 3 mm | 11 % | 23 % | 3 % | 1 % |
| water e0.5 | 5 mm | 23 % | 33 % | 32 % | 7 % |
| water e1 | 1.5 mm | 15 % | 0 % | 0 % | 0 % |
| water e1 | 3 mm | 30 % | 12 % | 0 % | 0 % |
| water e1 | 5 mm | 44 % | 22 % | 29 % | 11 % |

**Efficiency over time** (a specimen counts once it has passed by then):

| Condition | Strokes | A | B | C | D |
|---|---|---|---|---|---|
| dry | 1 / 2 / 4 / 8 | 13.7 / 14.3 / 14.3 / 14.3 | 34.0 / 35.0 / 35.3 / 37.1 | 30.2 / 30.2 / 30.2 / 31.7 | 100 throughout |
| water e0 | 1 / 2 / 4 / 8 | 0.6 / 3.6 / 8.3 / 14.9 | 7.2 / 13.6 / 19.2 / 29.9 | 15.9 / 17.5 / 20.6 / 31.7 | 92.5 / 92.5 / 91.4 / 88.2 |
| water e0.5 | 1 / 2 / 4 / 8 | 0.6 / 5.4 / 7.1 / 12.5 | 3.6 / 9.2 / 16.7 / 23.3 | 15.9 / 22.2 / 25.4 / 28.6 | 98.9 / 95.7 / 94.5 / 91.4 |
| water e1 | 1 / 2 / 4 / 8 | 1.8 / 7.7 / 14.9 / 14.9 | 4.7 / 10.5 / 10.5 / 11.9 | 20.6 / 25.4 / 28.6 / 28.6 | 88.8 throughout |

- **Dry, the stroke does nothing.** Everything that passes, passes while the specimens are first set down on the plate. After that the plate's 0.01 g accelerations (100 mm/s² of a FlexyStepper) leave dry specimens lying still. The dry D of 100 % is the same effect: nothing moves.
- **Wet at entrain 0 and 0.5, passage keeps going.** Each stroke the plate rises through the specimens suspended in the still water, lifts them out, and on the way back the water flushing up through it lifts them off again, as the paper describes. Over strokes 2-8, about 2-4 % of the specimens that fit and haven't passed yet pass per stroke.
- **At entrain 1 it stalls.** The water in the container moves with it, so nothing lifts the specimens off the plate, and passage stops after 2-4 strokes, close to the dry case. EntoSieve's container has closed walls and comes out of the water every stroke, so all of its water must drain through the plate: entrain near 0 is the physically closest setting for it.

**If the per-stroke rate held** (an extrapolation with an ASSUMED constant rate over strokes 2-8, not a sim result; tested over 40 strokes below):

| Condition | Plate | Class | Through after 1 stroke | After 8 | Per-stroke rate | After 127 strokes (6 min), extrapolated | Paper |
|---|---|---|---|---|---|---|---|
| water e0 | 1.5 mm | A | 1 % | 15 % | 2.2 % | 94 % | 95.6 % |
| water e0 | 3 mm | B | 7 % | 30 % | 3.9 % | 99 % | 97.6 % |
| water e0 | 5 mm | C | 16 % | 35 % | 3.6 % | 99 % | 98.4 % |
| water e0.5 | 1.5 / 3 / 5 mm | A / B / C | 1 / 4 / 16 % | 12 / 23 / 32 % | 1.8 / 3.2 / 2.9 % | 90 / 98 / 98 % | |
| water e1 | 1.5 / 3 / 5 mm | A / B / C | 2 / 5 / 21 % | 15 / 12 / 29 % | 2.0 / 1.1 / 1.5 % | 93 / 77 / 88 % | |
| dry | 1.5 / 3 / 5 mm | A / B / C | 14 / 34 / 30 % | 14 / 37 / 32 % | 0.1 / 0.7 / 0.3 % | 24 / 72 / 54 % | |

**Tested over 40 strokes: the rate does not hold.** Water, entrain 0, seeds 0 and 1, friction 0.4, 40 strokes (113 s) per plate. Share of each class through each plate (weighted; `entosieve.py curve`):

| Strokes | 1.5 mm plate: A | 3 mm plate: A / B / C / D | 5 mm plate: A / B / C / D |
|---|---|---|---|
| 1 | 0 % | 0 / 8 / 0 / 3 % | 0 / 11 / 27 / 16 % |
| 4 | 8 % | 10 / 22 / 7 / 3 % | 21 / 24 / 27 / 16 % |
| 8 | 10 % | 13 / 24 / 7 / 3 % | 21 / 35 / 40 / 16 % |
| 12 | 18 % | 23 / 34 / 13 / 3 % | 33 / 45 / 53 / 19 % |
| 20 | 28 % | 33 / 54 / 20 / 3 % | 41 / 64 / 60 / 19 % |
| 30 | 28 % | 49 / 56 / 20 / 3 % | 49 / 70 / 60 / 19 % |
| 40 | 28 % | 56 / 56 / 20 / 3 % | 51 / 72 / 60 / 19 % |

Per-class efficiency after 40 strokes: **A 28.2, B 55.8, C 40.0, D 81.4 %** (2 runs; the paper: 95.6 / 97.6 / 98.4 / 100). Passage levels off after about 20 strokes: the fitting specimens that are left never pass. No B ever went through the 1.5 mm plate, and D through 5 mm stays at 19 % (weighted: a 5.09 mm spider and a 7.95 mm parasitoid wasp).

**Why it levels off.** Traced in the 40-stroke runs (`t_pass` and the trajectories):
- **No lateral mixing.** The plate moves straight up and down and the sim's liquid moves uniformly, so a suspended specimen keeps its x-y position, and so does the hole pattern. A small specimen hanging over a hole goes down through that hole on every up-stroke and back up through it on every down-stroke (a 0.52 mm fly, standing on end 9 mm under the surface, did so on every stroke traced); one over solid metal is lifted out every stroke and set back on the same spot. EntoSieve's water does the opposite: the paper calls it "stirring", and its users also turn the container 45° by hand.
- **No sinking.** The smallest specimens settle at a fraction of a mm/s, so they never get below the plate's lowest position (30-40 mm under where they hang) within the run.
- **Rigid legs.** Fitting specimens left on the 3 mm plate after 40 strokes have a median span of 4.5-6.1 mm, against 3.0-3.3 mm for those that passed.

So the sim's plateau is set by the missing flow structure (jets, stirring) and rigid legs, not by the time it ran.

## 4. Does the hole cut by length? (INSECT_AUDIT's open question)

**Specimens longer than the hole but narrower than it**, every plate (8 strokes unless marked):

| Condition | Specimen-plate pairs | Passed |
|---|---|---|
| dry | 567 | 0 |
| water e0 | 567 | 9 (1.6 %) |
| water e0.5 | 567 | 8 (1.4 %) |
| water e1 | 567 | 6 (1.1 %) |
| water e0, 40 strokes | 127 | 6 (4.7 %) |
| water e0 with the exploratory hole flow (section 5) | 189 | 3 (1.6 %) |

The 8-stroke wet passes are four specimens, each in several conditions: a 3.03 mm spider through 3 mm holes and a 5.09 mm spider through 5 mm holes (both within 2 % of the hole), a 6.55 mm ant through 5 mm holes and a 7.95 mm parasitoid wasp (2.4 mm wide) through 3 mm holes, end first. In the 40-stroke runs two more slender parasitoid wasps (3.4 mm long, 0.9 mm wide) went through 3 mm holes end first, after 34-40 s; the paper's authors report the same of Ichneumonidae, which pass "based on their body height rather than their length". On the 1.5 mm plate, specimens 1.5-5 mm long and under 1.5 mm wide never passed (0 %, dry and every wet condition, 8 and 40 strokes; one 1.80 mm fly did with the exploratory hole flow). The paper lists no specimen in a finer fraction than its class (Table S1).

**How they lie.** On the 1.5 mm plate at the top of each stroke (out of the water), specimens within 3 mm of the plate, weighted:

| Condition | Long axis within 20° of the plate | More than 45° (end up) |
|---|---|---|
| dry | 83 % | 4 % |
| water e0 | 90 % | 3 % |
| water e0.5 | 87 % | 4 % |
| water e1 | 90 % | 3 % |

So in the sim, as in the paper, round holes sort by body length, and the reason is that specimens lie flat and nothing stands them up. Three cautions:
- **Rigid legs.** Generated legs can't fold, so specimens span a median 1.8-4.6 times their body length, by body plan (INSECT_AUDIT §1). Short specimens with long legs never pass (0 of 18 under 1.5 mm long with a span over 4 mm), which is the length cut's mirror image: a too-wide outline. Real ethanol-preserved legs are brittle and fold or break. The length cut for narrow specimens with tucked or trailing legs is not a leg effect: their outline is their body.
- **Uniform liquid.** The sim has no jets through the holes. Suction into a hole (section 5) is the one force that could stand a slender specimen up and pull it through end first, as the paper reports for Ichneumonidae ("based on their body height rather than their length").
- **Load.** 60 specimens, not 10,000: no crowding, no entangling, no film of floaters (leafhoppers, aphids) on the surface.

## 5. Exploratory: flow through the holes (not validated)

`liquid.ScreenFlow` (`--liquid water:screen_flow=1`, off by default) sketches the flow a perforated plate forces on the liquid: at relative speed U the holes carry jets of U/φ (φ the open fraction, so about 320 mm/s through the 1.5 mm plate), the flow over solid parts turns sideways into the nearest hole, and the field evens out within one hole radius (ASSUMED). It is a kinematic field, divergence-free per hole cell, with no blocking by specimens. It was written to see how much the missing flow matters, not tuned, and not checked against any flow data. Water, entrain 0, 8 strokes, seeds 0-2, friction 0.4:

| | A | B | C | D | Mean |
|---|---|---|---|---|---|
| Paper, test 1 | 95.6 | 97.6 | 98.4 | 100 | 97.9 |
| Sim, entrain 0, uniform liquid (9 runs) | 14.9 | 29.9 | 31.7 | 88.2 | 41.2 |
| Sim, entrain 0, with hole flow (3 runs) | 39.3 ± 3.2 | 59.5 ± 3.1 | 52.4 ± 13.6 | 88.8 ± 14.0 | 60.0 |

| Hole flow | Plate | A | B | C | D |
|---|---|---|---|---|---|
| through each plate | 1.5 mm | 39 % | 3 % | 0 % | 0 % |
| | 3 mm | 54 % | 62 % | 0 % | 0 % |
| | 5 mm | 73 % | 78 % | 52 % | 11 % |

- Passage per stroke roughly doubles to triples (class A on the 1.5 mm plate: 6.6 % of the remaining per stroke, against 2.2 %), so the missing flow is a large part of the gap to the paper.
- The length cut mostly survives the suction: 6 % (weighted) of the specimens 1.5-2 mm long and under 1.5 mm wide went through the 1.5 mm holes (none longer than 2 mm), against 0 % without it.
- Whether it levels off like the uniform-liquid runs was not tested (40 strokes cost 45 min per run).


## 6. What this means for the sim

- **Credible:** the wet sim reproduces the paper's qualitative result: a body-length cut on round holes, with the same direction of error (small specimens held back, not large ones let through: 1-1.6 % of oversize-but-narrow specimens passed wet in 8 strokes and 4.7 % in 40, none dry). It also reproduces that a gentle up-and-down stroke only sieves wet: dry, nothing moves after the first landing.
- **Not credible as a rate or an efficiency:** after 40 strokes the sim levels off at A 28 / B 56 / C 40 % against the paper's 96 / 98 / 98 %. The causes are known and are the model's, not the time it ran: no stirring or jets in a uniformly moving liquid, slow-settling specimens that never leave the plate's sweep, and rigid legs. A sorter design that relies on the liquid's flow (draining, jets, stirring) will be under-rated by the sim; one that relies on specimens lying flat against a cut will be rated about right.
- **For the optimizer:** rank designs on the wet sim, but don't quote its efficiencies as predictions. Treat `entrain` as uncertain over 0-1 (LIQUID.md); for a closed-wall container that leaves the bath, 0-0.2. Expect insect classes to be cut by length when specimens lie flat, not by width, so the end-first rule in gatecalc and `passability.md` overstates passage for elongate specimens in this gentle wet regime.
- **Unknown, and what would settle it:** a bench run of BugSorter's own trays wet, with a counted subsample (INSECT_AUDIT proposal 4); the settling speed of real Malaise specimens in water and ethanol (2 h of video); and, for the flow, either a CFD solution of one hole cell or a dye/particle video through a perforated plate, to replace the ScreenFlow sketch.

## 7. Differences from EntoSieve that remain

| | EntoSieve | Sim |
|---|---|---|
| Sieving time | 6 min per plate (test 1) | 22.6 s (8 strokes); 113 s (40) for one condition |
| Specimens | 10,276 on one plate | 60 |
| Taxa | real Malaise, incl. floating leafhoppers and aphids | 8 generated body plans, rigid, no floaters |
| Specimen density | real, after ethanol storage | 1.05 g/cm³ (ASSUMED, insects.py) |
| Flow | jets through the holes, draining, stirring | uniform liquid in the container (LIQUID.md) |
| Surface tension | the draining film | left out |
| Sequence | the retained fraction moves to the next plate | every plate sees all 60 specimens |
| Catch | stands still under the container | moves with it, 60 mm down |
| Length | measured from photos, front of head to last tergite | the generated body length |
