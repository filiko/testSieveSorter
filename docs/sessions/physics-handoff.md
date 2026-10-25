# Handoff: physics session (prompting mode) to a bypass-permissions session

Written 2026-10-25 ~06:05 PT by the main session. The first physics session ran in prompting mode and kept stopping for approvals, so a session in bypass mode takes over the same worktree (`testSieveSorter-physics`, branch `physics-bench`). Briefs: [physics.md](physics.md), [demo-rig.md](demo-rig.md) parts A and B.

## Done and on `main` (PR #2, merged 05:57)
- **Stroke direction `angle_deg`** in `sim/sorter.py`: 0 = along the design's flow axis, 90 = straight up. It works from the CLI (`--stroke sine:amp_mm=1.24,freq_hz=20,angle_deg=90`), `RunConfig.stroke` and sweep configs.
- **`inserts:5mm`** builds as the single-insert demo tray (zones `on_5mm`, `catch`). Smoke test: pasta=15, rice=40, 0° and 90°, both sort 100% in 3 s.
- **Instability detection:** MuJoCo silently resets `mjData` on a NaN/Inf. `results["unstable_resets"]` lists each reset, `sorter.py` prints `UNSTABLE`, and sweeps tag the run.
- `sim/instab.py` (probe), `sweep.py --workers`, `sim/stroke_from_video.py` (self-tested; Forum's clip shows the tool idle, so there's no stroke CSV), and the WSL notes in [README.md](README.md).
- **Speed:** the reference run takes 45 s in WSL, against 517 s on the old machine. Worker scaling: 1 worker 453 s, 8 workers 90 s, 16 workers 70 s, 22 workers 48 s.

## In the worktree, not committed yet
- `sim/PERF.md` (new): the machine, the reference run, worker scaling.
- `sim/instab.py`, `sim/sweep.py`: edits made after PR #2.
- **Vertical stability probe**, `out/instab/vertical.jsonl`, about 360 runs:
  - designs `inserts:5mm`, `inserts:mesh5,mesh2`, `pool:w5p0,t1p4`
  - mixes `demo`, `insects70`
  - strokes: sine 20 Hz at 1.242 / 2.485 / 4.970 mm, all at 90° (about 2 / 4 / 8 g peak); 2.485 mm at 45°; and the firmware constant-speed stroke
  - (dt, timeconst) settings 0.5/2, 0.25/0.5 and 0.125/0.5 ms
  - 4 seeds each, 2 s per run
  - The script is `vstab.sh` in the old session's scratchpad: `C:\Users\ajfil\AppData\Local\Temp\claude\C--Users-ajfil-Documents-Github-testSieveSorter-physics\958225d0-d302-4d21-bd84-b4b6458108f4\scratchpad\`. Earlier probes are `probe1.jsonl` and `probe2.jsonl` in the same `out/instab/` folder.
- **What the earlier probes found** (also used by `optimize.py`): 1056 runs, none unstable. The default dt 0.5 ms let particles sink a median 0.49 mm into the tray (max 0.81). That's more than the 0.15–0.3 mm clearance of the rice / quinoa tunnel. dt 0.25 ms with timeconst 0.5 ms gave a median 0.07 mm (max 0.18) for about 1.6x the wall time.

## Next steps
1. `git merge origin/main`. It doesn't touch `instab.py` or `sweep.py`.
2. **Read `vertical.jsonl`.** For vertical and angled strokes:
   - Which (dt, timeconst) stays stable, with penetration under 0.5x the gate clearance?
   - What does it cost in wall time?
3. **The comparison that answers the question** (demo-rig.md part A):
   - Setup: `inserts:5mm`, demo mix pasta + rice, **0°, 45° and 90° at the same peak acceleration**, all 3 friction sets, ≥3 seeds.
   - Report recovery, contamination, jams and t90 per class.
   - Write it up in **`sim/VERTICAL.md`**. Put the stroke ranges there too; they're plain assumptions, since the tool isn't modelled.
4. Commit `PERF.md`, `VERTICAL.md` and the `instab.py` / `sweep.py` edits. Open a PR to `main`; the main session merges it.
5. Then be the extra hand: help the optimizer (`docs/sessions/design-optimizer.md`) or the bambu session, whichever is blocked.

## Rules
- **Cores:** 24 in total, and the optimizer runs 16 workers. Use **`--workers 8` or fewer** while `optimize.py` is running (`ps aux | grep optimize.py` in WSL).
- Don't recreate `~/venvs/sieve`; add packages with `uv pip install --python ~/venvs/sieve/bin/python ...` and say so in the PR.
- Don't touch Smart App Control (it's one-way). Ask the user first.
- The sim models the tray, the grains and the shaking. Not the DeWalt tool.
