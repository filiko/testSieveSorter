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

CAD for the trays lives separately in `Documents\BioKEA-hack\cad` (CadQuery scripts that export STEP and STL).
