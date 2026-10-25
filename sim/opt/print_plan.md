# Print plan: demo winners

Built 2026-10-25 09:52 from `sim/opt/winners.json`, sliced for the P1S (Bambu Studio's default process, PLA). Made by `cad/winners.py`.

**Caveat:** sim ranking only; uncalibrated; openings simulated at nominal - 0.15 mm (ASSUMED undersize). The CAD is drawn at the nominal sizes; the sim assumed openings print 0.15 mm small. Check that against `hole_gauge` before trusting a gate size to 0.1 mm.

## Winner 1: plinko

- Sim spec: `plinko`, robust score 0.999
- Stroke to set on the Pi: tool sine 48 Hz, 2.2 g (0.24 mm), 20 deg up (profile sine, amp_mm 0.2373, freq_hz 48, angle_deg 20)
- Tower preview: `cad/out/win1_tower.png`

| Part | Time | Filament | Checks |
|---|---|---|---|
| `win1_layer_1_rods_3p7` | 37 min | 22.3 g | ok |
| `win1_layer_2_rods_1p5` | 47 min | 25.0 g | ok |
| `win1_layer_3_catch` | 47 min | 33.3 g | ok |
| **Total, one of each** | **130 min** | **80.6 g** | |

**One plate, ready to print:** 124 min, 80.5 g, all parts arranged on one P1S plate: `cad/out/slice/win1_plate.gcode.3mf` (local, not committed).

No printability flags.

## Winner 2: plinko

- Sim spec: `plinko`, robust score 1.000
- Stroke to set on the Pi: tool sine 37 Hz, 2.1 g (0.38 mm), 25 deg up (profile sine, amp_mm 0.3812, freq_hz 37, angle_deg 25)
- Tower preview: `cad/out/win2_tower.png`

| Part | Time | Filament | Checks |
|---|---|---|---|
| `win2_layer_1_rods_4p7` | 39 min | 24.1 g | ok |
| `win2_layer_2_rods_1p6` | 54 min | 31.4 g | ok |
| `win2_layer_3_catch` | 47 min | 33.3 g | ok |
| **Total, one of each** | **139 min** | **88.9 g** | |

**One plate, ready to print:** 133 min, 88.7 g, all parts arranged on one P1S plate: `cad/out/slice/win2_plate.gcode.3mf` (local, not committed).

No printability flags.

## Winner 3: gated_mid

- Sim spec: `gated:2.7,t3p35,t1p45,tw=4.85,tooth=0.95,slot=8.1/7,gx=22.2/53,flip=0`, robust score 0.985
- Stroke to set on the Pi: tool sine 48 Hz, 3.7 g (0.40 mm), 30 deg up (profile sine, amp_mm 0.3991, freq_hz 48, angle_deg 30)
- Tower preview: `cad/out/win3_tower.png`
- Assembly, top first:
  - L1 (top): gate_t3p5 at x 22.2, drop slot 8.1 mm, wedge beyond
  - L2 (NOT flipped): gate_t1p6 at x 53, standard slot and ramp
  - catch pan under L2

| Part | Time | Filament | Checks |
|---|---|---|---|
| `win3_gated_container_L1` | 70 min | 48.6 g | ok |
| `win3_gated_container_L2` | 72 min | 48.9 g | ok |
| `win3_gate_t3p5` | 6 min | 3.2 g | ok |
| `win3_gate_t1p6` | 6 min | 3.5 g | ok |
| **Total, one of each** | **154 min** | **104.1 g** | |

**One plate, ready to print:** 152 min, 103.8 g, all parts arranged on one P1S plate: `cad/out/slice/win3_plate.gcode.3mf` (local, not committed).

No printability flags.

Checks: valid single solid, watertight mesh, fits the bed. A tower needs one holder box per level plus the catch pan; the holder (`frame_holder`) isn't repeated here.
