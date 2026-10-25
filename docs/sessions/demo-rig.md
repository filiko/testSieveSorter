# Task: simulate the demo tray, with up-and-down shaking

**What the user wants (Oct 25, ~05:50 PT).** This replaces the stroke-measurement idea in `forum-footage.md`.
1. **Forum's photos are the demo example.** The rig: a white 3D-printed square-grid sieve tray, with ribbed windows and a pull tab (it looks like `cad/sieve_insert.py`'s 5 mm insert), bolted onto a handheld DeWalt 20V MAX cordless tool. It sorts tube pasta (ditalini) from rice and darker grains.
   **The sim models only the tray, the grains and the shaking motion. Do NOT model the tool:** no drill or saw geometry, no motor, no handheld dynamics. The tool is just what moves the tray, and in the sim that's the stroke (a translation of the tray).
2. **The video shows the motion we want: up and down.** Today the sim shakes along the tray's flow axis, horizontally. Adding vertical motion, and combined angled "throwing" motion like lab vibratory sieve shakers use, is the big improvement.

Photos: `C:\Users\ajfil\Documents\Github\testSieveSorter\media\forum-2026-10-24\` (local only, gitignored). Deadline: submission at 2:30 PM PT.

## A. Vertical and angled strokes (physics session, `physics-bench`)
- **Already there:** `sorter.py` takes `stroke["axis"]`, a 3-vector (line ~247), and sets tray-frame gravity to `-a(t)·axis - g·z`. That's exact for any pure translation, so vertical is `axis = (0,0,1)`.
- **The gap:** the CLI's `--stroke profile:k=v,...` can't pass a vector. Add `angle_deg`: 0 = along the design's flow axis, 90 = straight up, in between = angled throw. Keep `axis` for the Python API.
- **Stability:** vertical impacts raise contact speeds. Check penetration against the gate clearance, and QACC warnings, with the `instab.py` tooling. If a smaller dt is needed, say what it costs in runtime.
- **The comparison that answers the question:** on the demo tray (B below) with the demo mix, compare 0°, 45° and 90° at the **same peak acceleration**. Report recovery, contamination, jams and t90 per class across the 3 friction sets. Write it up in `sim/VERTICAL.md`.
- **Get A onto `main` early** (PR). The optimizer and bambu sessions both depend on it.

## B. Demo-tray design spec (physics, small)
- Make sure a single 5 mm printed insert builds as a design, e.g. `inserts:5mm`. Add it if only two-insert stacks build today.
- Demo mix: pasta (ditalini, already in `grains.py`) + rice. Add a dark rice variant only if it changes anything physically; colour alone doesn't matter to the sim.
- Stroke ranges (amplitude, frequency) are plain assumptions; the tool itself isn't modelled. Write them in `sim/VERTICAL.md`.

## C. Optimizer (optimizer session, `design-opt`)
- Once A is on `main`, add **stroke angle (0–90°)** to the search space, alongside amplitude and frequency, and rank designs × shake directions together.
- Include the demo tray (`inserts:5mm`) as a baseline row on the leaderboard, so the winners are measured against what the team actually built.

## D. Demo visual (bambu session, `bambu-viz`)
- In the sim viewer: the demo tray only (5 mm square-grid insert, no tool) with the pasta + rice mix, shaken **up and down** once A lands. Until then, use the horizontal run.
- Viewer work as before: camera from URL params, a **Copy camera** button, and a **Record** button (`canvas.captureStream()` + `MediaRecorder`) in `sim/viewer_template.html`.
- Match the viewer camera to one of Forum's photos (`IMG_1316.JPG` shows the tray on the tool from the side; `IMG_1318.JPG` is top-down).
- **Side-by-side:** Forum's photo (a still) next to the sim replay, labelled "Bench prototype" and "MuJoCo sim, uncalibrated". Write it to `media/demo_side_by_side.mp4` in the main checkout. It's local only and never committed.
