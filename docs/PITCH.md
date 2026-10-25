# Pitch: 5-minute demo script

Physical AI for Science Hack, BioKEA track. Live demos 15:30–16:30, then demos and pitching 16:30–17:30. **Numbers are from the MuJoCo sim and uncalibrated. Say so once, clearly.** *Draft at 13:00; the main session refreshes the numbers at ~14:00.*

## 0:00 The problem (30 s)
- BioKEA images and DNA-barcodes insects from Malaise traps: thousands of mostly tiny flies in ethanol.
- The sample often arrives as a **clump**: tangled insects with leaves, twigs and dirt. Sieves only sort loose specimens, and pulling a clump apart by hand is slow and breaks legs.
- BioKEA's BugSorter (EntoSieve, upgraded) shakes a stack of glued-mesh trays. We kept its idea, a stack of sieves, and redesigned the parts it shakes.

## 0:30 What we built (60 s)
Show the CAD previews (`cad/out/*.png`) and the printed parts on the table.
1. **The breaker layer** goes on top: blunt pins on an 8 mm grid. The motion throws the clump onto the pins and the spray loosens it. Leaves stay on top, and freed specimens fall through.
2. **The seesaw stack:** separate trays one above the other (5 mm, 2 mm, catch). Each one seesaws about its own centre pivot, and neighbours rock in opposite directions, so whatever drops lands on a tray tilted the other way.
3. **Fixes the sim found before we printed:**
   - inserts with **ribs across the tilt**, because small grains rode ribs that ran along it;
   - a **centre-pivot holder**, which halves the drop between levels, the biggest impact force on specimens;
   - a **lipped catch pan**, because grains bounced out.

## 1:30 The simulation (90 s)
Play the replays (local `view.html`; see Assets).
- **The clump breaking up** on the seesaw tower: specimens held by bonds that snap under load and weaken when wet. *First run: 84% free in 0.4 s.* Refresh with CLUMPS.md.
- **All nine modelled grains sorting** (pasta, chickpea, four rices, quinoa, couscous, chia). Show what failed first: quinoa and chia parked on the ribs. Then what fixed it: the ribs-across inserts and a small vibration. *Refresh with SEESAW.md.*
- The tower frame around the trays is for display only; the physics is the trays, the particles, the motion and the spray.

## 3:00 The system designs its own parts (60 s)
Show `sim/opt/leaderboard.md` and `sim/opt/LOG.md`.
- The optimizer proposes printable designs, runs each across friction sets and seeds, and ranks them by the **worst** class. No design wins on one lucky setting.
- It writes down **why the losers lost** and invents new design families. Its own example: a mid-slot gated tower it came up with.
- It found that **gated containers can't sort on a symmetric seesaw**, which is why the stack uses plinko rods and inserts.
- The winners go straight to CAD and are sliced for the P1S: parameters to G-code with no hand-drawing.

## 4:00 Bench and honesty (30 s)
- Forum's bench prototype: a printed 5 mm tray on a handheld DeWalt tool, sorting pasta from rice.
- The sim **ranks** designs. Calibrating it takes 10 minutes of bench counts (`sim/BENCH.md`): grain calipers, the box spacing, the rock angle and period.

## 4:30 What's next (30 s)
- Calibrate against bench counts.
- Real Malaise insect mixes: the sim already has the real size shares, 57% under 1.5 mm.
- Spray tuning for clumps.
- Hand it to BioKEA as drop-in parts for their tower.

## Assets
| What | Where |
|---|---|
| Mascot / banner | `docs/assets/mascot.png` |
| CAD previews | `cad/out/breaker_*.png`, `cad/out/seesaw_*.png`, `cad/out/sieve_insert_*_across.png`, `cad/out/win*_tower.png` |
| Replays (local, gitignored) | the clump on the seesaw tower; the seesaw tower with all grains at ±5 / 10 / 15° (paths from the main session); final renders from the seesaw and bambu sessions |
| Clips (local `media/`, never committed) | the bambu session's hero clips, captioned "MuJoCo sim, uncalibrated" |
| Leaderboards | `sim/opt/leaderboard.md`, and `leaderboard_malaise.md` when it exists |
