# The system: read this first

The one description of what we're building that every session works from. **If a brief, a doc or the code disagrees with this file, this file wins.** Tell the main session (or the user) instead of working around it. Facts come from the user and the team's photos, as of Oct 25 ~10:30 PT. Assumptions are marked.

## 1. The job
- **Input:** a Malaise-trap sample. It's thousands of mostly tiny flies in ethanol, and often a **compacted clump**: a ball or mound of tangled insects, mixed with **leaves, twigs and dirt**.
- **Step 1, the real point of the system:** **break the clump apart, gently.** Specimens go on to imaging and DNA barcoding, so crushed bodies or snapped legs are failures.
- **Step 2:** **size-sort** the freed specimens into classes. BugPicker's are > 6 mm, 2–6 mm and < 2 mm. Leaves are held back on top; dirt goes to the bottom.
- Pasta, rice and quinoa are the bench surrogates for the size classes.

Details: [docs/sessions/clump-breakup.md](sessions/clump-breakup.md).

## 2. The hardware: separate trays, one above the other
- **The stack:** separate holder boxes (about 140 × 104 × 25 mm), each holding one sieve insert (131.4 × 95.4 mm). Coarse is on top, finer below, and a catch pan at the bottom. The breaker layer (step 1) goes on top.
- **The boxes are separate**, stacked one above the other. They aren't one block, and they aren't side by side.

## 3. How a box is held, and why it rocks
- **Each box is attached at ONE short end only:** its **mounting tab on the +X end**, the width side. It's **not** held along its length.
  - On BioKEA's bench unit, the boxes hang from rods through their +X tabs in an extrusion frame.
  - On the team's demo, the tray is bolted by its tab onto a handheld DeWalt 20V MAX tool.
  - In both, the rest of the box **overhangs**. That's visible in Forum's photos (IMG_1315 / 1316 / 1318 / 1320, kept locally in `media/`).
- **So the motion is rocking, not a rigid up-and-down translation.** From the user (10:40): the box is **clamped at the tab and flexes**, about **20–30° at most, either side, in yaw**.
  - The free −X end swings side to side (±Y), rotating about a **vertical axis through the +X tab**, on top of the drive's stroke at the mount.
  - At 30° and ~130 mm of overhang, the free end sweeps about ±65 mm sideways. Near the mount the box barely moves, so particles near the free end get thrown hardest.
  - **Yaw is the default.** The sim should also support **pitch** (free end up and down, about Y through the tab) and a mix of the two, in case the flex has both. "Yaw" is the user's word; if the team meant tipping up and down, it's one parameter.
- **Not known yet (ASSUMED until measured):**
  - the exact rocking angle within 0–30° (sweep it);
  - the stroke at the mount;
  - the phase between the two;
  - the frequency. The DeWalt's real motion is unmeasured; a side-on video of it running would settle it, and `sim/stroke_from_video.py` can track it.
  - Sweep these in the sim; don't fix one guess.
  - **Keep it physical:** a flex of ±30° can't also run at the tool's tens of Hz. At 20 Hz that's about 100 g at the free end. So sweep the angle and the frequency together, and keep the free end's peak acceleration in a plausible range (report it; about 1–10 g). The big-angle wobble is presumably a slower flex mode, with the tool's fast, small stroke on top.
- **Pure translation strokes** (the 0° / 45° / 90° `angle_deg` runs, the firmware constant-speed stroke) are **simplifications**. Results from them (VERTICAL.md, the leaderboards made before rocking existed) need re-checking under rocking before the pitch uses them.

## 4. Liquid
Samples are in ethanol, and the rig sprays from fixed jets above. `sim/spray.py` models push, wetting and capillary adhesion. Wetting should also weaken clump bonds.

## 5. What the sim models, and what it doesn't
- **Modelled:** the trays (with their real mount point and rocking), the particles (specimens, grains, clumps, debris), the stroke and the spray.
- **Not modelled:** the tool, the motor, the frame, the hand. The frame in the replay (`sim/rig.py`) is display only.
- **Rocking in the sim:** keep the tray-fixed frame and add the full non-inertial forces of a frame that rotates about the mount axis while the mount translates:
  - per particle: `-m(a_pivot + α × r + ω × (ω × r) + 2 ω × v_rel)`, with ω along Z for yaw, Y for pitch, or any axis through the tab for a mix;
  - plus gravity rotated into the tray frame;
  - applied per body through `xfrc_applied`.
  - The current uniform-gravity trick is exact only for pure translation.
- **The sim ranks designs; it does not predict real percentages until it's calibrated against bench counts.**

## Who owns what
| Area | Session |
|---|---|
| `sim/sorter.py` (stroke, rocking, clumps, debris, metrics) | physics (`physics-bench`) |
| `sim/optimize.py`, `sim/designs_*.py` for searched families, `sim/opt/` | optimizer (`design-opt`) |
| `cad/`, slicing, `sim/viewer*`, `sim/rig.py`, replays and clips | bambu (`bambu-viz`) |
| `README.md`, `docs/`, this file, merging PRs | main |
