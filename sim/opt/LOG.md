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

