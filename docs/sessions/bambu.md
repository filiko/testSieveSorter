# [P] Bambu download + visualization / 3D modeling

> **Read [docs/SYSTEM.md](../SYSTEM.md) first** (added 10:30). It's the one description of the system: the input is a clump; the rig is separate trays one above the other, each held at its +X tab and overhanging, so they **rock**. It overrides this brief where they differ.

Worktree `Documents\Github\testSieveSorter-bambu`, branch `bambu-viz`. Read [README.md](README.md) first for the shared venv and the Smart App Control blocker.

## Scope
- **Install Bambu Studio** on this laptop. `cad\slice.py` expects it at `C:\Program Files\Bambu Studio\bambu-studio.exe`, with its profiles under `resources\profiles\BBL`. It isn't installed yet. The printer on the bench is a P1S (the default).
- **Get the CAD building again.** `cad\*.py` uses cadquery, which SAC blocks on Windows (see README.md). STL and STEP files go to `cad\out\` and aren't committed. Previews (`.png`) and `_checks.json` are.
- **Visualization and 3D modeling.** Previews, the assembled-stack views, and iterating on the current design: the gated container (`gated_container.py`), the inserts, and the holder (`frame_holder.py`). Dimensions are in `cad\WORKING_DIMENSIONS.md`. The `sieve-gate-design` skill in `.claude\skills\` goes from a sample spec to gate sizes.
- Then run `slice.py <part>` for print time and grams per iteration, and `hole_gauge.py` first so the openings match this printer.

## Not this session
- MuJoCo, `sim\`, timing and benchmarks: that's the physics session. `sim\viewer.py` (three.js replay) can be shared. Coordinate before changing `sim\viewer_template.html`.

## Done when
Bambu Studio is installed, `slice.py hole_gauge` prints an estimate, the gated-container parts rebuild, and their previews are updated in a PR.
