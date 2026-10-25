# testSieveSorter

Hackathon work on BioKEA's **BugSorter**, the size-sorting module at the front of their insect barcoding line (Physical AI for Science, Track A, Oct 2026).

## Bottom line

**Gates are a reasonable experiment, not the backbone.**
- **Build first:** removable perforated inserts over sealed collectors on BioKEA's existing actuator, coarse insert above fine. Run a small gate coupon beside it for comparison.
- **What decides it:** whether water moves through the openings in one direction. Put a drop into an isolated collector after every separator, so nothing gets carried back on the return stroke.
- **Before building:** check on the bench which firmware and which stroke direction the unit really has. The public firmware is a constant-speed vertical top/bottom stroke capped at 5 cm/s, with an uncalibrated steps-per-cm value. The team was told the motion is horizontal with water jets.

Full reasoning, tests and targets: [docs/gates-verdict.md](docs/gates-verdict.md)

## Docs

| File | What it is |
|---|---|
| [docs/gates-verdict.md](docs/gates-verdict.md) | Verdict on the gates idea, how to make the back-and-forth work, the three-hour build, tests, scoring, and where the three reviewers (Claude, Fable 5.1, Codex Astra) agreed and disagreed |
| [docs/current-system-vs-our-idea.md](docs/current-system-vs-our-idea.md) | BioKEA's current system, with a source link on every claim, side by side with our idea, plus questions to check on the bench |
| [docs/codex-astra-brief.md](docs/codex-astra-brief.md) | The question sent to Codex Astra |
| [docs/codex-astra-answer.md](docs/codex-astra-answer.md) | Codex Astra's answer, verbatim |
| [docs/bugsorter-line-breakdown.html](docs/bugsorter-line-breakdown.html) | Earlier report: all five modules and the BugSorter-to-BugDisperser handoff. Its pantry stand-ins (chia, couscous, noodles) predate the switch to rice, pasta and quinoa. |

## Key sources

- Track A deck: https://docs.google.com/presentation/d/1SxKytbrSBqIaxMuh4jCn2J_zIUmfZpnH/preview
- BugSorter firmware: https://github.com/BioKEA/BugSorter
- BugPicker: https://github.com/BioKEA/BugPicker
- EntoSieve paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC12225705/ (build files: https://osf.io/6t25n/)
- Elbrecht et al. 2021, wet sieving: https://pmc.ncbi.nlm.nih.gov/articles/PMC8500090

## Sieve system CAD (`cad/`)

Every part is exactly the size of a 24-well plate (127.76 × 85.47 × 20.27 mm), so it drops into any plate holder, plate shaker or plate gripper. A 3 mm lip under each part nests into the part below. The lip sits inside the 20.27 mm height.

**Stack, top to bottom:**

| Part | What it does |
|---|---|
| `lid` | Keeps grains from bouncing out |
| `tray_coarse_5p0` | 5.0 mm round holes. Pasta stays on top; rice and quinoa pass. |
| `tray_fine_2p3` | 2.3 mm round holes, for short-grain rice vs. quinoa |
| `tray_fine_slot_1p3` | 1.3 × 12 mm slots, which sort by thickness. Use this one for long-grain rice vs. quinoa. |
| `collector` | Sealed bin for whatever passes the fine tray (about 177 mL) |

**Also:**

| Part | What it does |
|---|---|
| `tray_open` + `clamp_ring` | Frame for a 121.2 × 78.9 mm piece cut from the kit's metal sheets. Clip the corners, drop it on the ledge, press the ring on top. |
| `gate_coupon_2p3`, `gate_coupon_5p0` | The gates idea, to run beside a perforated tray. Grains start on a raised deck, pass between tapered posts, and drop 5 mm into a pocket. Shake along the long side. |

**Design notes:**
- Every hole and slot widens 8° downward, so near-size grains fall through instead of wedging.
- Inner corners are rounded.
- Each part's label is debossed on its +X end wall.

**Build:** from `cad\`, run `..\..\..\BioKEA-hack\.venv\Scripts\python.exe sieve_system.py`, or name specific parts after the command.
- STL and STEP files land in `cad\out\` but aren't committed: rebuilding them takes about 2 min.
- Previews (`.png`) and checks (`_checks.json`) are committed.
- Print `hole_gauge.py` first and pour each grain over it, so the aperture numbers match what your printer actually makes.

**Changing sizes:** every dimension is a named parameter at the top of `sieve_system.py`. `cadkit.py`, `hole_gauge.py` and `slice.py` are copies from `Documents\BioKEA-hack\cad`.
