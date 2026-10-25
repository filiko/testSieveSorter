# Sorter sim

A MuJoCo simulation of grains and preserved insects moving through the team's sorters. Grains (rice, quinoa, chickpeas, pasta) are the calibration set: count them on the bench, then tune the sim until it matches. Insects are the real target. A three.js page replays every recorded run in the browser.

Status: first build, 2026-10-24. Nothing here is calibrated yet. Until the bench numbers in [BENCH.md](BENCH.md) are in, results rank designs against each other but don't predict real percentages.

## How it works

- **Engine.** MuJoCo 3.17 on the CPU. Units are mm, g and s.
- **Shaking.** The sim runs in the tray's own frame. The shake is applied as an extra force on every particle: gravity minus the tray's acceleration. This is exact for a tray that slides without rotating. Jets stay fixed in the lab while the tray moves under them.
- **Geometry.** Built from the same parameters as the CAD in `..\cad\`, so the sim follows the CAD when it changes.
- **Contacts.** A 2 ms contact time constant at a 0.5 ms step. In the worst case, a particle sinks about 0.2 mm into the tray during an impact. The tightest gate leaves 0.3 mm of room (quinoa in a 1.4 mm tunnel). Each run reports its worst overlap, so you can check it against that.

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
| [BENCH.md](BENCH.md) | What to measure on the bench, and which template each number goes in |

## Run

From `sim\`, with the repo venv (`..\.venv\Scripts\python.exe`):

```
python sorter.py --design pool:w5p0,t1p4 --mix rice=30,quinoa=30,chickpea=8,pasta=8 --stroke sine:amp_mm=3,freq_hz=10 --duration 10 --out out/runs/pool_demo
python viewer.py out/runs/pool_demo --open
```

Outputs go in `sim\out\`, which is not committed.

### Camera, recording and the real-vs-sim clip

The replay page reads its camera from the URL: `view.html?cam=x,y,z&target=x,y,z&fov=35&aspect=16:9` (mm, lab frame; FOV is vertical). Set the angle by eye against a photo (the **Frame** menu sets the aspect ratio, **FOV** dollies so the tray keeps its size), then **Copy camera** copies the URL. **Record** plays the run once in real time and downloads a `.webm` with the zone labels and the sim clock drawn in; its frame rate depends on the machine. For a clip to commit, render it frame-exact instead and put it next to the real footage:

```
python record_view.py out/runs/current_mesh --view "?cam=92.7,-78.3,240.3&target=15,5,58&fov=66&aspect=9:16" --speed 0.25 --start 2.0 --duration 1.1 -o out/runs/current_mesh/sim_forum_q.mp4
python side_by_side.py --real ../../testSieveSorter/media/forum-2026-10-24/IMG_1319.MOV --sim out/runs/current_mesh/sim_forum_q.mp4 --slow 4 --loops 3 --height 1080 --caption "Both at 1/4 speed: the same 1.1 s of shaking, looped. Sim stroke not yet fitted to this video."
```

These two lines made `media/demo_side_by_side.mp4`. Forum's clip (`IMG_1319.MOV`) is a 1.1 s Live Photo, so both halves are slowed 4x over the same 1.1 s of physical time, and the pair is looped. The camera was matched by eye to that clip. Sim t = 2.0 s was chosen because the sort there is in the same state as the video: pasta on the top mesh, small grains already through. For a run with the fitted stroke, change the run dir and keep the rest.

`side_by_side.py` writes `..\media\demo_side_by_side.mp4`, capped under 19 MB. It also takes a Record-button `.webm` and fixes Chrome's colour-range tagging (light greys would otherwise clip to white).
