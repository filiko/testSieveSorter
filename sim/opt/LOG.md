# Design optimizer log

One section per round. Sections marked "auto" are written by `sim/optimize.py` after each round; sections marked "notes" are the optimizer session's reading of them: what failed and why, the next hypothesis, and structural proposals that parameters can't express.

Tags: **executed** = a sim run in this log; **cited** = from another file, named; **assumed** = a placeholder until measured.

## Setup (notes, 2026-10-25 06:00)

**What is being optimized.** A design is a family plus its CAD parameters plus the stroke. Every family maps one to one onto CAD numbers that already exist, so a winner can be built without new geometry:

| Family | CAD | Searched |
|---|---|---|
| `gated` | `cad/gated_container.py` (README's final design) | floor slope 0.5-4 deg; L1 strip: width gap (with its own gap height, i.e. a "window") or tunnel; L2 tunnel; tunnel width; tooth; drop-slot length |
| `plinko` | `cad/plinko_layers.py` LAYERS | rod gap, rod top width, rod height (Z, 0.2 mm steps) for both rod layers |
| `inserts` | `cad/sieve_insert.py` INSERTS | square hole and bar for both inserts |
| all | BioKEA firmware | constant speed 15-50 mm/s (cap 50), amplitude 5-15 mm; ramp 0.01 s (assumed, sweep.py FIRMWARE) |

References, never tuned: the README design with the existing strips (w5.0 / t1.4, 2 deg), gatecalc's plan (t3.8 / t1.6), plinko and printed inserts as in the repo, and today's glued mesh inserts (`inserts:mesh5,mesh2`, not printable, so never a winner).

**Classes (demo study).** big = pasta + chickpea (L1), rice (L2), quinoa (catch), from the skill's sample spec (cited: `.claude/skills/sieve-gate-design/templates/sample-spec.toml`). Bins are the design's zones in flow order. Score = worst class of min(purity, recovery), minus jams, losses and a small t90 term; unstable runs score -1; ranked by mean - 1 sd over 3 friction sets x 3 seeds (details in the `optimize.py` docstring).

**The sim's gated tower** (new, `sim/designs_gated.py`). One holder box per level, rim on rim, container on the ledge, alternate levels flipped 180 deg, catch pan below. The sample is poured on the top container's high end. Every dimension is read from `gated_container.py` and `frame_holder.py`.

**Assumptions and settings.**
- Openings are simulated at the as-printed size, nominal - 0.15 mm (assumed undersize, from the skill; replace with `hole_gauge.py` data). Teeth and rods get 0.15 mm wider by the same token.
- Solver: dt 0.25 ms, contact timeconst 0.5 ms, not sorter.py's 0.5 / 2 ms. Cited: the physics session's instability probe (`testSieveSorter-physics/sim/out/instab/probe*.jsonl`, 1056 one-second runs, none unstable): the default let particles sink a median 0.49 mm (max 0.81) into the tray, more than the 0.15-0.3 mm clearance between rice, quinoa and the tunnel; 0.25 / 0.5 ms gave a median 0.07 mm (max 0.18) for about 1.6x the wall time. I'll switch to `sim/PERF.md`'s settings when physics commits them.
- The penetration flag uses the overlap against gate and screen geoms only (strip teeth, rods, screens), measured after the settle. Landing on a floor after a 25 mm drop between levels sinks deeper but can't push anything through an opening.
- An unstable run is detected by checking MuJoCo's BADQACC warning counter every 50 steps (MuJoCo resets and carries on otherwise, so the run would look fine). It scores -1.
- No new packages were added to `~/venvs/sieve`.

**Found while building (for the bambu session).**
- **Tab clash (executed geometry check, from the CAD numbers):** `gated_container.py` TAB_TOP = 25 mm above the container bottom. The container sits on the 3 mm ledge, so the tab top is at 28 mm in box coordinates, 3 mm above the 25 mm box rim. In a rim-on-rim stack, the tabs (y 41.7-47.7) run into the ledge of the box above (|y| 41-48). Either TAB_TOP <= 22 mm, or the boxes need 3 mm spacers. The sim cuts the tabs at 22 mm.
- **Rice parks crosswise at the w5 gate (executed: `gated:2,w5p0,t1p4`, 4 s, recorded).** The first rice reached the L1 strip after about 2 s and sat against the teeth at x 51.3 (strip face at 52) for the rest of the run: a 6.5 mm grain lying across the flow can't enter a 5 mm gap until it turns end-first.
- **Transport is slow on a 2 deg floor (same run).** At 50 mm/s and 10 mm amplitude, rice drifted toward the gate at about 7 mm/s on average and quinoa at about 4 mm/s. The poured sample starts 60-110 mm from the L1 strip, and what drops to L2 lands at its far end, 110 mm from the L2 strip. So 30 s may not finish the sort. That is why the 8 s screen ranks sorting progress, not the strict score.

**First hypotheses.**
1. The gated tower is transport-limited at today's 2 deg; the search will push slope and speed up, and a steeper floor eats into the 16 mm wall above the high end.
2. A window gate (w gap with a capped height) or a tunnel at L1 should beat the 8 mm tall w5 gap: pasta (6.5 x 6.0) can roll on edge through tall gaps once the gap is wider than 6.
3. Plinko should sort fastest (each grain only has to fall through a layer, not travel 110 mm), but rice may lie across the 1.4 mm rods and bridge them, and the drop from layer to layer is short.
4. Square-hole inserts cannot split rice from quinoa (same width, cited: `docs/gates-verdict.md`); they are in the search to show how far behind they are.

## Structural test: ratchet floor and steeper slope (notes, 2026-10-25 06:15)

**Hypothesis.** The gated tower is transport-limited. Sawtooth ribs across the floor (gentle face rising toward the gate, steep face on the gate side) should turn the symmetric stroke into one-way transport, as on a vibratory conveyor.

**Test (executed).** README design at the as-printed sizes (`gated:2,w4p85x7p85,t1p25,...`), firmware cap stroke (10 mm, 50 mm/s, ramp 0.01 s), mu 0.4, seed 0, dt 0.25 ms / timeconst 0.5 ms, 15 s shake. Runs in `sim/out/opt/ab/`, script `sim/out/opt/ab.sh`.

| variant | rice: L1 / L2 / catch / between at 15 s | quinoa: L1 / L2 / catch / between |
|---|---|---|
| A: 2 deg floor (README) | 20 / 8 / 0 / 2 | 24 / 5 / 0 / 1 |
| B: + ribs 0.8 tall, pitch 6, steep 0.15 | 30 / 0 / 0 / 0 | 30 / 0 / 0 / 0 |
| C: + ribs 0.6 tall, pitch 4, steep 0.15 | 30 / 0 / 0 / 0 | 30 / 0 / 0 / 0 |
| D: 3.5 deg floor, no ribs | 16 / 12 / 0 / 2 | 19 / 5 / 3 / 3 |

**Result: the ratchet floor stops transport completely.** The firmware stroke is constant speed with hard reversals. With the assumed 0.01 s reversal (`sweep.py` FIRMWARE ramp_s, a guess until the stroke is filmed) the tray's acceleration is a pulse of about 2 x 50 / 0.01 = 10 m/s^2 (1 g) for 10 ms at each reversal, and is zero in between. On a flat floor that slides a grain about 0.5 mm per reversal (relative speed gained (1 - mu) g x 10 ms, about 60 mm/s, then friction stops it). That's the slow drift seen in A. A rib's gentle face is several mm long, so a grain climbs a fraction of it and slides back into the valley. **Rejected; the ribs are not in the search.** The geometry stays available as `rib=<h>x<pitch>x<steep>` in `designs_gated.py`, should the measured stroke turn out to reverse much harder.

**What this says about transport.** Only gravity along the slope (tan 2 deg = 0.035 g) biases the random sliding, so a steeper floor helps (D vs A). But it costs wall height: at 4 deg the high end's floor is 8 mm up a 16 mm wall.

**Key unknown, flagged for the physics session:** the real reversal time. Transport scales with the reversal jolt, so a 2-5 ms reversal would change the gated tower's numbers a lot. The optimizer can't tune it (firmware hard-codes constant speed), but its winners should be rechecked once the stroke CSV from the video exists.

**Next structural hypothesis (mid-slot tower).** Today a grain travels the length of L1 to its gate, then drops onto the far, high end of the flipped L2 and travels the length of L2 again: about 220 mm in total at a few mm/s. Moving L1's gate and drop slot to mid-length, with L2 unflipped and its gate at the end, would land L1's passers about 25-60 mm upstream of L2's gate and roughly halve the total travel. The floor downstream of L1's slot then has to slope back into the slot. Implement as a family if round 0 confirms that the gated tower loses on transport.

## Structural test: mid-slot tower (notes, 2026-10-25 06:30)

**Hypothesis** (from the previous note). Put L1's gate and slot at mid-length and stop flipping L2. What passes L1 then lands just upstream of L2's gate, which should roughly halve the travel.

**Test (executed).** `designs_gated.py` options `gx=<x1>/<x2>` (gate position per level), `slot=<l1>/<l2>` and `flip=0`. Beyond a mid-length slot a 30 deg wedge fills the container and slopes back into the slot. The strip and rails must clear the pull tabs (|x| >= 13.15 mm). Same stroke, friction, seed and solver as the ratchet test; 15 s.

| variant | rice L1 / L2 / catch / between | quinoa L1 / L2 / catch / between |
|---|---|---|
| A: today, 2 deg | 20 / 8 / 0 / 2 | 24 / 5 / 0 / 1 |
| D: today, 3.5 deg | 16 / 12 / 0 / 2 | 19 / 5 / 3 / 3 |
| E: L1 gate at x 25, slot 8, L2 unflipped, 2 deg | 19 / 9 / 0 / 2 | 19 / 6 / 2 / 3 |
| F: as E at 3.5 deg | 20 / 8 / 0 / 2 | 16 / 9 / 1 / 4 |
| G: L1 gate at x 35, 2 deg | 22 / 8 / 0 / 0 | 22 / 4 / 0 / 4 |

**Result: no clear gain** (one seed, so weak evidence). Two thirds of the rice and quinoa are still on L1 after 15 s in every variant, so L1's own drift (a random walk of about 0.5 mm per reversal, biased only by the slope) is the bottleneck, not L2's travel. The mid-slot layouts also jam a few more quinoa (3-4 "between": on the ledges beside the shorter slot, or the wedge). **Rejected; not in the search.** The options stay in `designs_gated.py`.

**What would fix the gated tower's transport:** a harder stroke reversal (unknown until filmed; see the stress test on the leaderboard), a steeper floor (needs taller container walls, or it eats the 16 mm wall at the high end), or a different motion (an asymmetric stroke, which the firmware doesn't do). None of these is a gate-geometry change. **Plinko doesn't need transport at all:** a grain only hops across rods until it tips into a gap. That is why it leads the 8 s screen (rice 97%, quinoa 90% recovered, almost no leaks).

## demo round 0 (2026-10-25 06:34, auto)

**Tried:** gated: 30 (baseline, lhs); plinko: 13 (baseline, lhs); inserts: 7 (baseline, lhs); current: 1 (current). 603 runs, 35 min wall.

**Leader so far:** P-cbe7dbec (plinko, round 0) rods L1 gap 5.1 (rod 1.4 wide, 1.6 tall) / L2 gap 1.7 (rod 1.9, 3.2), stroke 14 mm at 41 mm/s: robust 0.891 (mean 0.929 +/- 0.038); big (pasta, chickpea) 99% pure / 100% recovered, rice 97% pure / 97% recovered, quinoa 97% pure / 96% recovered; ok.

**Screen results this round (8 s, progress score), best per family:**

- gated: best G-617e6c8a screen robust 0.368; median 0.331; failures in 0 of 30 candidates
- plinko: best P-2aaaaec0 screen robust 0.911; median 0.745; failures in 0 of 13 candidates
- inserts: best I-f660966d screen robust 0.735; median 0.608; failures in 0 of 7 candidates
- current: best C-243bf513 screen robust 0.590; median 0.590; failures in 0 of 1 candidates

**Why the losers failed** (particles per run, over this round's screened candidates in the bottom half of each family; the most common modes):

- gated: quinoa: held upstream -> L1 on the floor (28.1 in 15 cands); rice: held upstream -> L1 on the floor (25.5 in 15 cands); rice: held upstream -> L1 at the gate (within 10 mm) (3.4 in 15 cands); quinoa: held upstream -> L1 at the gate (within 10 mm) (1.2 in 12 cands); quinoa: held upstream -> L2 on the floor (0.7 in 10 cands); rice: between -> L1 in the strip (0.5 in 14 cands)
- plinko: rice: leaked downstream -> layer_3_catch (11.1 in 5 cands); quinoa: held upstream -> layer_2_rods (7.1 in 7 cands); quinoa: held upstream -> layer_1_rods (3.1 in 7 cands); rice: held upstream -> layer_1_rods (2.4 in 6 cands)
- inserts: quinoa: held upstream -> on_h1p55b1p35 (22.6 in 1 cands); rice: held upstream -> on_h2p65b0p95 (22.4 in 1 cands); quinoa: held upstream -> on_h1p55b1p25 (22.2 in 1 cands); quinoa: held upstream -> on_h1p45b1p25 (21.8 in 1 cands); rice: held upstream -> on_h3p15b1p35 (14.2 in 1 cands); rice: held upstream -> on_h3p55b1p85 (8.8 in 1 cands)
- current: rice: leaked downstream -> catch (6.6 in 1 cands); quinoa: between -> in the floor of on_mesh5 (2.0 in 1 cands); rice: between -> in the floor of on_mesh5 (1.6 in 1 cands); quinoa: held upstream -> on_mesh2 (0.6 in 1 cands); quinoa: between -> in the floor of on_mesh2 (0.2 in 1 cands)

**Leaders' remaining losses** (full runs, top 3):

- P-cbe7dbec: quinoa: held upstream -> layer_2_rods 1.1; rice: leaked downstream -> layer_3_catch 0.9; quinoa: held upstream -> layer_1_rods 0.2
- P-2aaaaec0: quinoa: held upstream -> layer_2_rods 1.7; rice: leaked downstream -> layer_3_catch 0.9; quinoa: held upstream -> layer_1_rods 0.3; rice: held upstream -> layer_1_rods 0.1
- P-e4035f89: quinoa: held upstream -> layer_2_rods 2.2; rice: leaked downstream -> layer_3_catch 0.9; quinoa: held upstream -> layer_1_rods 0.3; rice: held upstream -> layer_1_rods 0.2

**Parameters at a bound among each family's elite** (the range may be too narrow):

- gated: k1 w 0.17/t 0.83
- plinko: none
- inserts: none

**Next hypothesis (auto):** 0.9 particles per run leak through a gate they should not pass: tighten that gate or cap the gap height (window gate)


## demo round 0: reading (notes, 2026-10-25 06:45)

**What won and why.** Plinko, clearly. The best candidate, P-cbe7dbec, has rods 5.1 / 1.7 nominal and a 14 mm stroke at 41 mm/s. It sorts 97% of rice and 96% of quinoa into their bins at 97% purity, with no jams and no flags, and reaches t90 in about 4 s. Plinko needs no transport: a grain hops across the rods until it tips into a gap, a few mm away. The gated tower must walk every grain 100+ mm per level, and at the firmware's ~1 g reversal pulses no gated candidate got its quinoa through in 30 s (best quinoa recovery 11%, gatecalc's t3.8 / t1.6).

**Why the losers failed** (auto section above, read):
- **gated:** 25-28 of 30 rice and quinoa still on L1's floor after 8 s, 10+ mm from the gate. That is transport, not gate size. Its elite still learned something real: 83% chose a tunnel at L1 rather than a width gap. A tunnel cuts by thickness, so pasta can't roll through on edge (gatecalc's L1 pick too).
- **plinko:** the bottom half leaks rice to the catch (about 11 per run; the L2 gap is wider than rice is thick) or holds quinoa on layer 2 (about 7 per run; the gap is too tight for quinoa to tip into). Every top-3 plinko candidate chose an L2 gap of 1.7 nominal (1.55 as printed) between those two.
- **inserts:** square holes can't split rice from quinoa (same width). The repo's 5 / 2 mm inserts score 0.714, but only because rice's corner-to-corner diagonal (1.86 mm) is 0.01 mm wider than the as-printed 1.85 mm hole. All 9 runs are flagged; 0.1 mm of print tolerance leaks rice. Every other insert size either holds all quinoa or leaks rice.
- **today's glued mesh** (reference): 0.523. Rice 100% pure but only 67% recovered: 3.2 particles per run stick in the 5 mm mesh, and some rice leaks to the catch.

**Leaders' remaining losses.** About 1 quinoa per run stays on layer 2 and about 1 rice per run reaches the catch. The rice that leaks is the thin tail of the sim's rice (thickness 1.7 mm +/- 7%, so about 10% of rice is under the 1.55 mm gap). That overlap is in the material, not the machine. Real rice needs measuring (`sim/bench/grain_dims.csv`) before this matters.

**Winners rule (changed after seeing results; recorded here).** Before the first full results I set the rule: top 3 among candidates with no failed and no flagged run, filled with marked flagged ones only if fewer than 3 qualify. Applied to round 0, it put two gated designs into places 2 and 3, and both score below 0 (they sort almost nothing in 30 s). It skipped plinko designs scoring 0.85, whose only issue was 1-2 of 9 runs with a gate overlap of 0.094-0.098 mm against a 0.07 mm threshold. A winner has to be a working sorter, so I added a floor: robust score >= 0.5. The floor removes non-working designs; it doesn't favour a particular one. The flagged winners stay marked, with their overlap numbers, in `winners.json`.

**For the bambu session (print risk):** winner #1's layer-1 rods are 1.4 mm wide on top and 1.6 mm tall, tapering 8 deg to 0.95 mm at the bottom, over 43 mm spans between the rib and the wall. They're printable, but may be floppy. If they are, tell me the minimum rod size and I'll make it a constraint.

**Next hypothesis.**
1. Plinko's L2 gap is the critical number, and it sits 0.14 mm under the sim's rice thickness. The stress test reruns the top 3 with the printer making openings 0.1 mm tighter or looser, and with sharper or softer stroke reversals (0.005 / 0.02 s).
2. Rounds 1-2 (cross-entropy) refine plinko's rods and stroke. Expect the stroke amplitude to matter: the top 3 use 7.5-14 mm.
3. The gated tower stays in the search for completeness, but no gate geometry will fix its transport (see the two structural tests above).

## demo round 1 (2026-10-25 06:49, auto)

**Tried:** gated: 16 (ce); plinko: 8 (ce); inserts: 3 (ce). 306 runs, 14 min wall.

**Leader so far:** P-63092ca9 (plinko, round 1) rods L1 gap 5.6 (rod 2.1 wide, 2.6 tall) / L2 gap 1.6 (rod 1.6, 3.4), stroke 10 mm at 50 mm/s: robust 0.915 (mean 0.953 +/- 0.038); big (pasta, chickpea) 99% pure / 100% recovered, rice 96% pure / 100% recovered, quinoa 100% pure / 96% recovered; ok.

**Screen results this round (8 s, progress score), best per family:**

- gated: best G-331e7311 screen robust 0.429; median 0.335; failures in 0 of 16 candidates
- plinko: best P-63092ca9 screen robust 0.943; median 0.882; failures in 0 of 8 candidates
- inserts: best I-08d1890b screen robust 0.756; median 0.662; failures in 0 of 3 candidates

**Why the losers failed** (particles per run, over this round's screened candidates in the bottom half of each family; the most common modes):

- gated: quinoa: held upstream -> L1 on the floor (28.8 in 8 cands); rice: held upstream -> L1 on the floor (26.6 in 8 cands); rice: held upstream -> L1 at the gate (within 10 mm) (2.8 in 8 cands); quinoa: held upstream -> L1 at the gate (within 10 mm) (0.8 in 6 cands); quinoa: held upstream -> L2 on the floor (0.4 in 6 cands); rice: between -> L1 in the strip (0.5 in 3 cands)
- plinko: rice: leaked downstream -> layer_3_catch (4.4 in 4 cands); quinoa: held upstream -> layer_2_rods (3.0 in 4 cands); quinoa: held upstream -> layer_1_rods (1.8 in 4 cands); rice: held upstream -> layer_1_rods (0.5 in 4 cands)
- inserts: quinoa: held upstream -> on_h1p45b1p05 (26.3 in 1 cands); quinoa: held upstream -> on_h1p65b1p25 (15.4 in 1 cands); quinoa: held upstream -> on_h4p85b1p55 (6.3 in 1 cands); rice: held upstream -> on_h4p85b1p55 (4.6 in 1 cands); quinoa: held upstream -> on_h5p15b1p25 (2.8 in 1 cands); rice: held upstream -> on_h5p15b1p25 (0.3 in 1 cands)

**Leaders' remaining losses** (full runs, top 3):

- P-63092ca9: quinoa: held upstream -> layer_2_rods 1.2; quinoa: held upstream -> layer_1_rods 0.1
- P-cbe7dbec: quinoa: held upstream -> layer_2_rods 1.1; rice: leaked downstream -> layer_3_catch 0.9; quinoa: held upstream -> layer_1_rods 0.2
- P-7e49fbec: quinoa: held upstream -> layer_2_rods 2.3; quinoa: held upstream -> layer_1_rods 0.3

**Parameters at a bound among each family's elite** (the range may be too narrow):

- gated: k1 w 0.15/t 0.85
- plinko: none
- inserts: none

**Next hypothesis (auto):** the leader sorts cleanly; refine for robustness and throughput.


## demo round 1: reading, and the stroke-angle update (notes, 2026-10-25 06:55)

**What changed in the leader.** Cross-entropy moved plinko's layer-2 gap from 1.7 to 1.6 nominal (1.45 as printed). The new leader, P-63092ca9 (rods 5.6 / 1.6, robust 0.915), leaks no rice to the catch (round 0's leaders leaked 0.9 per run). It pays with about 1.2 quinoa per run left on layer 2. That is the right trade: rice now has 0.25 mm of margin over the gap and quinoa 0.35 mm under it, both above the 0.14 mm of the round 0 leaders. A wider margin also survives print tolerance better (the stress test will tell). It runs on **the firmware's own cap stroke**, 10 mm at 50 mm/s, so BioKEA's machine needs no new motion for it.

**Gated:** the best is now 0.071 (3.2 deg floor, tunnels 5.4 / 1.7, quinoa 34% recovered at 30 s). Still the same failure: 27-29 grains per run on L1's floor.

**Brief update (main, 05:50 and 06:05): stroke angle and the demo rig.** I merged `origin/main` (physics' `angle_deg`, `unstable_resets`, PERF.md: production solver dt 0.25 ms / timeconst 0.5 ms, the same as this optimizer already uses). Changes from round 2 on:
- **Two drives in the search.**
  - *firmware*: BioKEA's stage, constant speed 15-50 mm/s, 5-15 mm amplitude.
  - *tool*: a vibrating tool like the demo rig's, a sine at 10-50 Hz with 1-5 g peak acceleration.
  - Both take a stroke angle of 0-90 deg (0 = along the tray, 90 = straight up). Old candidates count as firmware at 0 deg, so their results stand.
  - Families that gained these parameters get an extra Latin hypercube batch to explore them, besides the cross-entropy proposals.
- **Demo-rig reference row:** `inserts:5mm`, shaken up and down as in the video (sine 20 Hz, 2 g, 90 deg, the motion physics assumed in `sim/VERTICAL.md`). It has two bins, so rice and quinoa share its catch, and the 3-class score shows exactly that.
- `sorter.py`'s own reset detection now also fails a run, besides the BADQACC counter.

**Structural hypothesis, revived by the angle: the unflipped mid-slot tower (`gated_mid`).** An angled throw is how a vibratory conveyor moves material in one direction, and it could cure the gated tower's transport problem. But the throw conveys toward the same end of every level, while today's tower flips every other level, so L2's grains would be conveyed away from L2's gate. The mid-slot layout tested at 06:30 keeps every gate at +X (L1's gate at mid-length with its drop slot, L2 unflipped at the end). It was useless under the firmware stroke, but it is the layout a directional throw needs. Round 2 adds it as the family `gated_mid` (Latin hypercube, 16 candidates): L1 gate x 14-38 mm (the strip has to clear the pull tabs) with a 6-14 mm slot ending at least 7 mm upstream of L2's strip, plus the whole stroke space.

## Constraint from the bambu session: rods and teeth at least two print lines (notes, 2026-10-25 07:00)

Bambu's `cad/build_winners.py` (branch `bambu-viz`, PR #4) flags rods, teeth and bars narrower than 0.8 mm (two 0.4 mm extrusion lines) as fragile, and openings under 0.8 mm as likely to close up on the first layer. Plinko rods taper 8 deg, so a tall, thin rod gets narrow at the bed. I adopted this as a hard constraint (`MIN_LINES`): a rod's width at the bed, top width - 2 x height x tan 8 deg, must be at least 0.8 mm. Winner selection re-checks every candidate against today's constraints.

Effect: two of round 1's top 3 drop out of `winners.json`, but stay on the leaderboard. P-63092ca9 (0.915) has layer-2 rods 1.6 wide and 3.4 tall, 0.64 mm at the bed. P-7e49fbec (0.860) has layer-1 rods 1.5 wide and 3.2 tall, 0.60 mm at the bed. Both have feasible neighbours (shorter rods), which round 3's proposals will find. The insect study's smallest openings go up from 0.6 to 0.8 mm for the same reason.

The `gated_mid` CAD block now keeps `GATE_X` scalar (L2, what today's script builds) and puts L1's position in `mid_slot_PROPOSAL`, so `build_winners.py` doesn't break on it. A mid-slot winner needs new L1 geometry first (`buildable_with_todays_cad: false`).

## demo round 2 (2026-10-25 07:12, auto)

**Tried:** demo_rig: 1 (current); gated: 20 (ce, lhs); gated_mid: 16 (lhs); plinko: 16 (ce, lhs); inserts: 5 (ce, lhs). 648 runs, 22 min wall.

**Leader so far:** P-ae394887 (plinko, round 2) rods L1 gap 3.7 (rod 2.6 wide, 1.6 tall) / L2 gap 1.5 (rod 1.8, 2.4), stroke tool sine 48 Hz, 2.2 g (0.24 mm), 20 deg up: robust 0.999 (mean 0.999 +/- 0.000); big (pasta, chickpea) 100% pure / 100% recovered, rice 100% pure / 100% recovered, quinoa 100% pure / 100% recovered; PEN 1/9 (clr 0.26, pen 0.153).

**Screen results this round (8 s, progress score), best per family:**

- demo_rig: best D-e018f15d screen robust 0.995; median 0.995; failures in 0 of 1 candidates
- gated: best G-0c6843ad screen robust 0.659; median 0.341; failures in 0 of 20 candidates
- gated_mid: best G-060cecb0 screen robust 0.876; median 0.333; failures in 0 of 16 candidates
- plinko: best P-668db784 screen robust 1.000; median 0.882; failures in 0 of 16 candidates
- inserts: best I-90aad5db screen robust 0.854; median 0.688; failures in 0 of 5 candidates

**Why the losers failed** (particles per run, over this round's screened candidates in the bottom half of each family; the most common modes):

- demo_rig: rice: held upstream -> on_5mm (0.1 in 1 cands)
- gated: quinoa: held upstream -> L1 on the floor (28.0 in 10 cands); rice: held upstream -> L1 on the floor (25.7 in 10 cands); rice: held upstream -> L1 at the gate (within 10 mm) (2.6 in 10 cands); quinoa: held upstream -> L1 at the gate (within 10 mm) (1.0 in 10 cands); quinoa: held upstream -> L2 on the floor (0.7 in 8 cands); quinoa: held upstream -> L2 at the gate (within 10 mm) (0.5 in 7 cands)
- gated_mid: quinoa: held upstream -> L1 on the floor (27.6 in 8 cands); rice: held upstream -> L1 on the floor (25.9 in 8 cands); rice: held upstream -> L1 at the gate (within 10 mm) (3.7 in 8 cands); quinoa: held upstream -> L1 at the gate (within 10 mm) (2.7 in 4 cands); quinoa: held upstream -> L2 in the drop slot (0.9 in 5 cands); quinoa: between -> L1 in the strip (0.3 in 4 cands)
- plinko: quinoa: held upstream -> layer_2_rods (8.1 in 7 cands); quinoa: held upstream -> layer_1_rods (4.8 in 7 cands); rice: held upstream -> layer_1_rods (6.6 in 5 cands); rice: leaked downstream -> layer_3_catch (7.6 in 3 cands); rice: between -> in the floor of layer_1_rods (0.8 in 2 cands); quinoa: between -> in the floor of layer_1_rods (0.7 in 1 cands)
- inserts: rice: held upstream -> on_h2p45b1p45 (28.6 in 1 cands); rice: held upstream -> on_h4p15b1p75 (18.9 in 1 cands); quinoa: held upstream -> on_h4p15b1p75 (17.7 in 1 cands); quinoa: held upstream -> on_h1p85b1p65 (10.8 in 1 cands); quinoa: held upstream -> on_h1p75b1p15 (10.3 in 1 cands); quinoa: held upstream -> on_h2p45b1p45 (8.4 in 1 cands)

**Leaders' remaining losses** (full runs, top 3):

- P-ae394887: none
- P-668db784: none
- G-060cecb0: rice: leaked downstream -> catch 0.4

**Parameters at a bound among each family's elite** (the range may be too narrow):

- gated: k1 w 0.22/t 0.78, drive firmware 0.78/tool 0.22, angle low (5.15)
- gated_mid: k1 w 0.50/t 0.50, drive firmware 0.14/tool 0.86
- plinko: drive firmware 0.74/tool 0.26, angle low (4.20)
- inserts: drive firmware 0.86/tool 0.14, angle low (0.87)

**Next hypothesis (auto):** the leader's near-size results are flagged (overlap vs clearance): check it at a smaller dt or stiffer contacts before trusting it


## demo round 2: reading (notes, 2026-10-25 07:20)

**The stroke matters more than the geometry.** Round 2 was the first with the vibrating-tool drive (sine) and the stroke angle. All three top designs use it:
- P-ae394887, plinko, rods 3.7 / 1.5, sine 48 Hz at 2.2 g (0.24 mm amplitude), 20 deg up: **0.999**. Every class 100% pure and recovered in all 9 runs, t90 0.4 s.
- P-668db784, plinko, rods 3.5 / 1.6, sine 14 Hz at 2.0 g, along the tray: 0.998.
- G-060cecb0, **gated_mid**, L1 window w3.1 x 3.1 at x 31.8, L2 t1.8, sine 28 Hz at 4.3 g, 10 deg up: **0.955**.

The best on BioKEA's firmware stroke is P-ba5dd6b3, plinko 5.6 / 1.6 at 9.5 mm and 47 mm/s, 5 deg up: 0.929. A small, fast vibration keeps every grain hopping over the rods or slots, so each gets many chances at a gap per second. The firmware stroke gives at most a ~1 g jolt 2.5 times a second.

**The structural hypothesis held.** Under the firmware stroke the gated tower couldn't move grain (best 0.07). The unflipped mid-slot layout with an angled throw sorts at 0.955, with 99-100% recovery per class and t90 7.8 s. The throw conveys every level toward +X, and only the unflipped layout has every gate at +X. Today's flipped tower with a tool-drive throw scored -0.05 at best: all 4 such candidates were run at full length, at angles of 10-55 deg, and sorted almost nothing (checked against the run cache). L2's grains are conveyed away from its gate.

**Why the losers failed (auto section above).**
- **gated and gated_mid** bottom halves: 26-28 grains still on L1's floor. They are mostly firmware-drive candidates, so transport again.
- **plinko** bottom half: quinoa held on layer 2 (8 per run) or rice leaking to the catch (8 per run), the same gap-size trade as before. Some rice is also held on layer 1 at the slower strokes.
- **inserts:** still can't split rice from quinoa.
- **The demo rig** (reference, 0.499): pasta and chickpea 100% on the screen, rice and quinoa all in the catch together. That is perfect at what it was built for (pasta vs rice). It has no second bin, so the 3-class score caps it near 0.5.

**Flags on the leaders.** P-ae394887 has 1 of 9 runs flagged (gate overlap 0.153 mm against a 0.13 threshold), P-668db784 has 3 of 9, and G-060cecb0 has 9 of 9. Its window gate is within 0.04 mm of a grain size, so its clearance is tiny. By the winners rule, none of them can be a winner yet. `winners.json` is P-ba5dd6b3 and P-cbe7dbec (firmware plinko, clean) and G-a48f4670 (gated_mid, sine 37 Hz at 2.5 g, 45 deg up, clean, 0.835).

**Next hypothesis and actions.**
1. **Verify the flagged leaders with stiffer contacts.** A new `verify` step reruns them at dt 0.125 ms and timeconst 0.25 ms (half the overlap, about 2x the time). A design that comes back unflagged and still scores well counts as clean in the winners rule. This resolves the untrustworthiness with a better solver; it doesn't loosen the rule. Queued after the insect round.
2. **Recommend per drive.** BioKEA's stage can only do the firmware stroke, while the demo rig is a vibrating tool, so `winners.json` gets a best-per-drive entry as well as the overall top 3.
3. **gated_mid** gets the next cross-entropy round (its elite is 86% tool drive).

## insects round 0 (2026-10-25 07:59, auto)

**Tried:** gated: 11 (baseline, lhs); plinko: 9 (baseline, lhs); inserts: 4 (baseline, lhs); current: 1 (current); gated_mid: 8 (lhs). 396 runs, 47 min wall.

**Leader so far:** P-8d6849ce (plinko, round 0) rods L1 gap 3.1 (rod 2.4 wide, 2.4 tall) / L2 gap 1.3 (rod 2.6, 3.4), stroke tool sine 32 Hz, 4.0 g (0.97 mm), 75 deg up: robust 0.351 (mean 0.470 +/- 0.119); > 6 mm 74% pure / 57% recovered, 2-6 mm 89% pure / 78% recovered, < 2 mm 78% pure / 92% recovered; PEN 9/9 (clr 0.05, pen 0.706).

**Screen results this round (8 s, progress score), best per family:**

- gated: best G-127ae062 screen robust 0.468; median 0.333; failures in 0 of 11 candidates
- plinko: best P-2a281144 screen robust 0.612; median 0.394; failures in 0 of 9 candidates
- inserts: best I-88c112b1 screen robust 0.509; median 0.430; failures in 0 of 4 candidates
- current: best C-243bf513 screen robust 0.133; median 0.133; failures in 0 of 1 candidates
- gated_mid: best G-c46df8f7 screen robust 0.649; median 0.333; failures in 0 of 8 candidates

**Why the losers failed** (particles per run, over this round's screened candidates in the bottom half of each family; the most common modes):

- gated: 2-6 mm: held upstream -> L1 on the floor (26.4 in 6 cands); < 2 mm: held upstream -> L1 on the floor (13.4 in 6 cands); 2-6 mm: held upstream -> L1 at the gate (within 10 mm) (29.1 in 2 cands); < 2 mm: held upstream -> L2 on the floor (12.2 in 2 cands); < 2 mm: held upstream -> L1 at the gate (within 10 mm) (6.6 in 2 cands); 2-6 mm: between -> L1 in the strip (1.9 in 2 cands)
- plinko: 2-6 mm: held upstream -> layer_1_rods (8.7 in 5 cands); < 2 mm: held upstream -> layer_2_rods (5.8 in 5 cands); 2-6 mm: between -> in the floor of layer_2_rods (3.4 in 5 cands); 2-6 mm: leaked downstream -> layer_3_catch (5.7 in 3 cands); < 2 mm: held upstream -> layer_1_rods (3.9 in 3 cands); 2-6 mm: between -> in the floor of layer_1_rods (2.2 in 5 cands)
- inserts: 2-6 mm: held upstream -> on_h2p35b1p35 (30.7 in 1 cands); 2-6 mm: held upstream -> on_h1p95b1p35 (28.3 in 1 cands); < 2 mm: held upstream -> on_h2p35b1p35 (12.2 in 1 cands); < 2 mm: held upstream -> on_h1p15b0p95 (5.3 in 1 cands); 2-6 mm: between -> in the floor of on_h1p95b1p35 (4.4 in 1 cands); < 2 mm: held upstream -> on_h1p25b1p15 (3.7 in 1 cands)
- current: 2-6 mm: leaked downstream -> catch (8.0 in 1 cands); 2-6 mm: between -> in the floor of on_mesh5 (7.4 in 1 cands); 2-6 mm: between -> in the floor of on_mesh2 (6.7 in 1 cands); 2-6 mm: held upstream -> on_mesh5 (2.1 in 1 cands); > 6 mm: between -> in the floor of on_mesh5 (1.6 in 1 cands); < 2 mm: between -> in the floor of on_mesh5 (1.3 in 1 cands)
- gated_mid: 2-6 mm: held upstream -> L1 on the floor (35.8 in 4 cands); < 2 mm: held upstream -> L1 on the floor (18.8 in 4 cands); 2-6 mm: held upstream -> L1 at the gate (within 10 mm) (7.2 in 1 cands); < 2 mm: held upstream -> L2 in the drop slot (1.9 in 1 cands); < 2 mm: held upstream -> L1 at the gate (within 10 mm) (1.6 in 1 cands); < 2 mm: held upstream -> L2 on the floor (0.8 in 1 cands)

**Leaders' remaining losses** (full runs, top 3):

- P-8d6849ce: 2-6 mm: leaked downstream -> layer_3_catch 5.0; > 6 mm: leaked downstream -> layer_2_rods 2.6; 2-6 mm: held upstream -> layer_1_rods 2.2; < 2 mm: held upstream -> layer_2_rods 1.2; 2-6 mm: between -> in the floor of layer_2_rods 1.0
- P-2ee377b0: 2-6 mm: held upstream -> layer_1_rods 4.1; < 2 mm: held upstream -> layer_2_rods 4.1; 2-6 mm: between -> in the floor of layer_2_rods 3.9; 2-6 mm: leaked downstream -> layer_3_catch 3.0; < 2 mm: between -> in the floor of layer_2_rods 1.7
- P-2a281144: 2-6 mm: held upstream -> layer_1_rods 12.3; < 2 mm: held upstream -> layer_2_rods 8.2; 2-6 mm: between -> in the floor of layer_1_rods 1.8; > 6 mm: between -> in the floor of layer_1_rods 0.7; < 2 mm: between -> in the floor of layer_2_rods 0.3

**Parameters at a bound among each family's elite** (the range may be too narrow):

- gated: k1 w 0.15/t 0.85, drive firmware 0.38/tool 0.62, k2 w 0.85/t 0.15
- plinko: drive firmware 0.38/tool 0.62
- inserts: drive firmware 0.38/tool 0.62
- gated_mid: k1 w 0.62/t 0.38, drive firmware 0.15/tool 0.85, k2 w 0.38/t 0.62

**Next hypothesis (auto):** 7.6 particles per run leak through a gate they should not pass: tighten that gate or cap the gap height (window gate); 2.1 particles per run jam between bins: see where in the losses list; the leader's near-size results are flagged (overlap vs clearance): check it at a smaller dt or stiffer contacts before trusting it


## insects round 0: reading (notes, 2026-10-25 08:05) -- EXPLORATORY

The insects are the generated specimens of `sim/insects.py`, with textbook sizes and none measured. The classes are BugPicker's body lengths: > 6 mm (L1), 2-6 mm (L2), < 2 mm (catch).

**Result: no design sorts these classes well, and the reason is structural.**
- The best is P-8d6849ce, plinko 3.1 / 1.3 on a sine at 32 Hz and 4 g, 75 deg up: robust 0.351. Recovery is 57% for > 6 mm, 78% for 2-6 mm and 92% for < 2 mm. gatecalc predicted about the same (10 / 45 / 98% recovery with its gates t2.9 / w1.2, from `gatecalc.py plan` on the malaise template with these length classes, run at 06:00). Gates cut width and thickness, and body length overlaps between the classes in both.
- No candidate reaches the 0.5 working-sorter floor, so `winners_insects.json` lists none.
- **Today's glued mesh jams 17 specimens per run** (legs caught in the mesh; it scores 0.168). That matches the warning in `docs/gates-verdict.md` about woven mesh as a fence.

**Every insect result is flagged.** Legs (capsules down to 0.06 mm radius) sink 0.4-1.25 mm into the rods and gates, while the clearances are about 0.05 mm, because some specimen is always near-size. One more reason these numbers rank but don't predict.

**Hypothesis (a question for the team, not for the optimizer):** BugPicker's real constraint is whether a specimen fits a 96-well, which is width-driven (`.claude/skills/sieve-gate-design/references/well-fit.md`). Gates can cut width; nothing in the stack cuts length. Classes defined by width, or "fits a well / doesn't", would be sortable. That's the team's call. Until then the insect study gets the leftover compute: one cross-entropy round after demo round 4.

## Verification of the flagged demo leaders (notes, 2026-10-25 08:10)

`verify` reran the four best flagged designs at dt 0.125 ms and timeconst 0.25 ms (half the contact softness), 3 friction sets x 3 seeds, 30 s:

| id | standard: robust, flags | stiff: robust, flags | verdict |
|---|---|---|---|
| P-ae394887 plinko 3.7 / 1.5, sine 48 Hz 2.2 g 20 deg | 0.999, 1/9 flagged | **1.000**, none (max gate overlap 0.077 mm, threshold 0.13) | **clean** |
| P-668db784 plinko 3.5 / 1.6, sine 14 Hz 2.0 g | 0.998, 3/9 | 1.000, 1/9 | still flagged |
| G-060cecb0 gated_mid, window 3.1 x 3.1 | 0.955, 9/9 | 0.940, 9/9 | still flagged |
| P-547508e5 plinko 3.1 / 1.7, sine 46 Hz 1.3 g 35 deg | 0.937, 1/9 | 0.927, none | **clean** |

The scores barely move with stiffer contacts, so the ranking wasn't an artefact of soft contacts. P-ae394887 and P-547508e5 become eligible. G-060cecb0 stays flagged for a real reason: its 2.95 mm window is within 0.04 mm of a grain dimension, so any print error flips that grain's routing. That's a sim-trust flag and a printability warning in one.

**winners.json now:**
1. P-ae394887, plinko, vibrating tool;
2. P-ba5dd6b3, plinko, firmware stroke;
3. P-547508e5, plinko, vibrating tool.

Best per drive: firmware P-ba5dd6b3 (0.929), vibrating tool P-ae394887 (1.000 verified).

**Next:** demo round 3 (running); then the stress test of these winners (reversal time 0.005 / 0.02 s for the firmware one, printer undersize 0.05 / 0.25 mm for all); then round 4.

