# Parallel sessions

Three Claude Code sessions work on this repo at the same time. Each has its own git worktree and branch, so none of them edits another's files. Merge into `main` through PRs on https://github.com/filiko/testSieveSorter.

| Session | Folder | Branch | Brief |
|---|---|---|---|
| Main / GitHub / coordination | `Documents\Github\testSieveSorter` | `main` | — |
| Bambu + visualization / 3D modeling | `Documents\Github\testSieveSorter-bambu` | `bambu-viz` | [bambu.md](bambu.md) |
| Physics engine test on the new laptop | `Documents\Github\testSieveSorter-physics` | `physics-bench` | [physics.md](physics.md) |

**Shared venv.** There is one venv, `testSieveSorter\.venv` (Python 3.12, from `requirements.txt`). Each worktree has a `.venv` junction that points at it, so `..\.venv\Scripts\python.exe` works from `cad\` and `sim\` in any folder. A `pip install` in one session changes the venv for all three, so say so in the PR.

## Blocker shared by both [P] sessions: Smart App Control

This laptop (Lenovo 83F3, Windows 11) has **Smart App Control ON** (`VerifiedAndReputablePolicyState = 1`). It blocks the unsigned native DLLs in three wheels:

| Package | Status | Error |
|---|---|---|
| numpy, trimesh | OK | — |
| mujoco 3.17.0 | blocked | `DLL load failed while importing _specs: An Application Control policy has blocked this file.` |
| cadquery 2.8.0 (OCP) | blocked | same, on `OCP` |
| vtk 9.6.2 | blocked | same, on `vtkWebCore` |

Options; the user decides which one:
1. **WSL2 (Ubuntu) venv.** SAC doesn't apply inside WSL. Run the sim and CAD there and keep the repo on the Windows side (`/mnt/c/...`), or clone it inside WSL for speed. This needs no change to the Windows security policy. It's the recommended first try.
2. **Turn off Smart App Control** (Windows Security > App & browser control). It's **one-way**: it can't be turned back on without reinstalling Windows. Ask the user first.
3. Conda-forge builds. Probably also unsigned, so they'd likely be blocked too. Only worth a quick check.

Whichever option is chosen, record it here so the other session doesn't redo the work.
