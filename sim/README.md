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
