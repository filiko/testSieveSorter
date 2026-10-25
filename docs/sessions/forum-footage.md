# Task: use Forum's BugSorter footage (stroke + side-by-side)

Forum Shah emailed photos and video of the real BugSorter: "Fwd: Bug sorter videos n pics", sent to ajfiliko on Sat Oct 24 at 8:33 PM. The files go in

`C:\Users\ajfil\Documents\Github\testSieveSorter\media\forum-2026-10-24\`

That's the main checkout, not your worktree. Read them from there. `media/` is **gitignored**: the footage is local reference only, so never commit anything from it.

**What's there:** 4 photos (`IMG_1315/1316/1318/1320.JPG`, 640×480) and 1 video, `IMG_1319.MOV`: 1920×1080 h264 at 30 fps, **1.1 s long, 33 frames** (recorded 2026-10-25 01:29 UTC). That's short. It may not show a full stroke, and at 30 fps it can't resolve `ramp_s` (about 33 ms per frame). Say what the clip can and can't show; don't stretch it.

## Findings so far (physics session, checked against the photos)
- **The drive is a handheld DeWalt 20V MAX cordless tool** (it looks like a compact reciprocating saw; the model isn't readable) with the printed square-grid tray bolted on. It isn't the stepper firmware stroke the sim models.
- **In the clip the tool is idle.** The only motion is about ±1–2 mm of handheld wobble, so there's no stroke to extract, and `stroke_forum.csv` was **not** written. `sim/stroke_from_video.py` is built and self-tested, ready for a clip with the tool running.
- **What's needed from the team:** the tool's model (rated strokes/min and stroke length give a better stroke than the firmware guess), plus a clip with the tool running: on a tripod, side-on, with a ruler in frame, in slow motion if possible.
- **For Part 2 (bambu):** don't pair the idle clip with a shaking sim; it would mislead. Use a photo of the real rig (a still) next to the sim replay, labelled as such, until a running clip exists.

Camera or vision simulation is **not** a track requirement. BioKEA judges three clean size classes. The footage is for two things, and the user chose both. Deadline: submission Sun Oct 25 at 2:30 PM PT.

## Part 1: real stroke from the video (physics session, `physics-bench`)

`sim/BENCH.md` step 1 calls the stroke "the most important measurement". The sim guesses `ramp_s = 0.01` s.

1. Look at the photos and the clip, and note what each one shows in `sim/bench/README_forum.md`. That file is committed; the media itself isn't.
2. Write `sim/stroke_from_video.py`:
   - `ffmpeg` pipes grayscale frames of a cropped region.
   - Track a high-contrast feature on the tray (an edge or a pull tab) along the stroke axis, using an intensity-weighted centroid or 1-D cross-correlation.
   - Scale px to mm from a known part in frame: an insert is 131.4 mm long (`cad/WORKING_DIMENSIONS.md`).
   - Numpy is fine on Windows. If you want OpenCV, use the WSL venv, and record the install in `docs/sessions/README.md`.
3. Write `sim/bench/stroke_forum.csv`. Use the format of `stroke_example.csv`: `t_s,x_mm`, and lines starting with `#` are comments. Report amplitude, speed, period and `ramp_s`.
4. **Be honest about resolution.** At 30 fps nothing under about 33 ms resolves. Report `ramp_s` as an upper bound unless the clip is slow-motion.
5. Say whether the stroke is **horizontal or vertical** (the README's open question: the firmware implies a vertical top/bottom stroke, but the team was told horizontal), and whether there's any vertical bounce.
6. Check: overlay the tracked point on 3 frames, and plot x(t) as a PNG. Compare against the firmware default (2 cm stroke, 0.5 cm/s).
7. Rerun the reference case with `stroke_profile=csv` and put the before/after numbers in `sim/PERF.md`.

## Part 2: real-vs-sim side-by-side clip (bambu/viz session, `bambu-viz`)

This doesn't need MuJoCo. The recorded run `sim/out/runs/current_mesh/` (`traj.npz`, `scene.json`, `view.html`) is in the main checkout; copy it into your worktree's `sim/out/runs/`, which is gitignored. The viewer is three.js, and `viewer.py` needs only numpy, which loads on Windows.

1. Edit `sim/viewer_template.html` (this session now owns that file; physics won't touch it):
   - Read the camera from URL params: `?cam=x,y,z&target=x,y,z&fov=..`. The auto-fit is at about line 672, at `(0.25,-1,0.8)`.
   - Add a **Copy camera** button, so the angle can be matched by eye against Forum's photo and pasted back.
   - Add a **Record** button: `canvas.captureStream()` + `MediaRecorder`. It plays the replay once and downloads a `.webm`.
2. Rebuild the page: run `..\.venv\Scripts\python.exe viewer.py out/runs/current_mesh --open` from `sim\`.
3. Use `ffmpeg` to scale both clips to the same height, `hstack` them, and label them **"Real BugSorter"** and **"MuJoCo sim, uncalibrated"**. Write `media/demo_side_by_side.mp4` in the main checkout. It's local only (gitignored); it's for the demo, not the repo. The real clip is only 1.1 s, so loop it or show a still from the photos next to the sim.
4. Check: the page opens at the pasted angle, the webm plays, the final mp4 plays with both halves in sync, and the labels are readable.
5. Once the physics session has `stroke_forum.csv` and a new run on `main`, re-record the sim half from that run.

## Both
- Work on your own branch and open a PR into `main` on https://github.com/filiko/testSieveSorter.
- Don't edit `docs/sessions/README.md` again in this task; both branches already change it.
