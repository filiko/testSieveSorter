# Task: use Forum's BugSorter footage (stroke + side-by-side)

Forum Shah emailed photos and video of the real BugSorter: "Fwd: Bug sorter videos n pics", sent to ajfiliko on Sat Oct 24 at 8:33 PM. The files go in

`C:\Users\ajfil\Documents\Github\testSieveSorter\media\forum-2026-10-24\`

That's the main checkout, not your worktree. Read them from there. **The folder is empty until the user saves the attachments into it.** No session can download them: the Google connector returns only the email text, and the ajfiliko IMAP app password is revoked. Until the files land, do the parts that don't need them.

Camera or vision simulation is **not** a track requirement. BioKEA judges three clean size classes. The footage is for two things, and the user chose both. Deadline: submission Sun Oct 25 at 2:30 PM PT.

## Part 1: real stroke from the video (physics session, `physics-bench`)

`sim/BENCH.md` step 1 calls the stroke "the most important measurement". The sim guesses `ramp_s = 0.01` s.

1. Run `ffprobe` on each clip and record fps, resolution and duration. List the files in `media/README.md`: what each one shows, and what camera took it.
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
3. Use `ffmpeg` to scale both clips to the same height, `hstack` them, and label them **"Real BugSorter"** and **"MuJoCo sim, uncalibrated"**. Write `media/demo_side_by_side.mp4`. Keep it under about 20 MB so it can be committed.
4. Check: the page opens at the pasted angle, the webm plays, the final mp4 plays with both halves in sync, and the labels are readable.
5. Once the physics session has `stroke_forum.csv` and a new run on `main`, re-record the sim half from that run.

## Both
- Work on your own branch and open a PR into `main` on https://github.com/filiko/testSieveSorter.
- Don't edit `docs/sessions/README.md` again in this task; both branches already change it.
