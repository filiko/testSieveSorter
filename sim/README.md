# Sorter sim

A MuJoCo simulation of grains and preserved insects moving through the team's sorters. Grains (rice, quinoa, chickpeas, pasta) are the calibration set: count them on the bench, then tune the sim until it matches. Insects are the real target. A three.js page replays every recorded run in the browser.

Status: first build, 2026-10-24. Nothing here is calibrated yet. Until the bench numbers in [BENCH.md](BENCH.md) are in, results rank designs against each other but don't predict real percentages.

## How it works

- **Engine.** MuJoCo 3.17 on the CPU. Units are mm, g and s.
- **Shaking.** The sim runs in the tray's own frame. The shake is applied as an extra force on every particle: gravity minus the tray's acceleration. This is exact for a tray that slides without rotating. Jets stay fixed in the lab while the tray moves under them.
- **Geometry.** Built from the same parameters as the CAD in `..\cad\`, so the sim follows the CAD when it changes.
- **Contacts.** Soft: a pressed grain sinks a little into the tray, and the tightest gates leave only 0.15–0.3 mm of room (quinoa in a 1.4 mm tunnel). `RunConfig`'s default (2 ms contact time constant at a 0.5 ms step) lets grains sink about 0.5 mm, so pass the settings from [PERF.md](PERF.md) explicitly, or let `contact_rule.py` pick them from the design's tightest clearance and the stroke (see [VERTICAL.md](VERTICAL.md), Contact rule). Each run reports its worst overlap, so you can check it against the clearance.

## Files

| File | What it is |
|---|---|
| `sorter.py` | Core: builds the scene, shakes it, records it, and counts where everything ends up |
| `designs.py` | Pool sorter, plus the registry for every design spec |
| `designs_holder.py` | BioKEA's holder tower with sieve inserts (glued mesh or printed), and the plinko layers |
| `grains.py` | Rice, quinoa, chickpeas, pasta |
| `insects.py` | Generated preserved specimens: compact, elongate, long-legged |
| `spray.py` | Fixed jets: push, wetting, wet friction and capillary cling |
| `viewer.py` | Builds a standalone three.js replay page for a run |
| `record_view.py` | Renders a run's replay page to a frame-exact MP4 through headless Chrome |
| `side_by_side.py` | Real footage next to a sim clip, scaled, labelled and synced, for the demo |
| `sweep.py` | Batches of runs in parallel, with a report |
| `calibrate.py` | Fits contact parameters to bench counts, then checks them on a held-out run |
| `instab.py` | Stability probe: short runs that stop at the first MuJoCo reset and record the worst overlap, tray-wide and on gates only |
| `contact_rule.py` | Picks the timestep and contact time constant from a design's tightest gate clearance and the stroke |
| `verify.py` | Second opinion on the optimizer's winners: fresh seeds, a heavy load, per-design contacts; writes `opt/VERIFY.md` |
| [BENCH.md](BENCH.md) | What to measure on the bench, and which template each number goes in |

## Run

From `sim\`, with the repo venv (`..\.venv\Scripts\python.exe`):

```
python sorter.py --design pool:w5p0,t1p4 --mix rice=30,quinoa=30,chickpea=8,pasta=8 --stroke sine:amp_mm=3,freq_hz=10 --duration 10 --out out/runs/pool_demo
python viewer.py out/runs/pool_demo --open
```

Outputs go in `sim\out\`, which is not committed.

### Camera, recording and the real-vs-sim clip

The replay page reads its camera from the URL: `view.html?cam=x,y,z&target=x,y,z&fov=35&aspect=16:9` (mm, lab frame; FOV is vertical). Set the angle by eye against a photo (the **Frame** menu sets the aspect ratio, **FOV** dollies so the tray keeps its size), then **Copy camera** copies the URL. **Record** plays the run once in real time and downloads a `.webm` with the zone labels and the sim clock drawn in; its frame rate depends on the machine. For the demo clip, render frame-exact instead and put it next to Forum's photo of the bench prototype (demo-rig.md part D):

```
wsl: python sorter.py --design inserts:5mm --mix pasta=15,rice=40 --stroke sine:amp_mm=1.24,freq_hz=20,angle_deg=90 --duration 10 --dt 0.00025 --timeconst 0.0005 --fps 240 --out out/runs/demo_vertical
python viewer.py out/runs/demo_vertical
python record_view.py out/runs/demo_vertical --view "?cam=116.5,-209.7,180.4&target=5,0,32&fov=45&aspect=3:4" --speed 0.2 --start 0 --duration 2.2 --height 960 -o out/runs/demo_vertical/sim_demo_0p2x.mp4
python side_by_side.py --real ../../testSieveSorter/media/forum-2026-10-24/IMG_1316.JPG --sim out/runs/demo_vertical/sim_demo_0p2x.mp4 --height 960 --real-label "Bench prototype" --sim-label "MuJoCo sim, uncalibrated" --caption "Sim at 1/5 speed. Grains are poured in; from t 1 s the tray shakes up and down (20 Hz, ±1.24 mm, assumed).\nRice falls through the 5 mm grid into the catch; the pasta stays on top."
```

- **The run** is VERTICAL.md's viewer run, recorded at 240 fps. At the default 30 fps a 20 Hz shake aliases into a slow wobble that isn't there.
- **The camera** is matched by eye to `IMG_1316.JPG`, the side view on the tool: the long wall faces the camera, the mounting-tab end is on the right, and the frame is 3:4 portrait. The camera sits higher (32°) than the photo so the grid and the catch show.
- **The clip** shows sim t = 0–2.2 s at 1/5 speed (11 s). The pour runs to t = 1 s, with no shaking. From there the shake clears the rest of the rice by t = 2.0, and nothing changes after that. At 1/5 speed the 20 Hz shake plays as a visible 4 Hz bounce.
- **Forum's photos and the clip stay local:** `media/` is gitignored. Copy the clip into the main checkout's `media/`.

`side_by_side.py` writes `..\media\demo_side_by_side.mp4`, capped under 19 MB. A photo as `--real` is held for the whole sim clip. A video works too (`--slow`, `--loops`). It also takes a Record-button `.webm` and fixes Chrome's colour-range tagging (light greys would otherwise clip to white).
