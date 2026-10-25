# Working dimensions

Adopted 2026-10-24 as the team's working numbers. All values are in mm.

- **Source of truth:** `frame_holder.py` and `sieve_insert.py`. This page mirrors them; if you change a number, change it in the script, rebuild, then update this page.
- **Inserts follow the holder:** if a measured part disagrees, fix the holder first. The inserts take their outside size from the holder pocket.

## Holder box (`frame_holder.py`)

| What | Value |
|---|---|
| Body | 140 × 104 × 25 |
| Overall with tab | 162 × 104 × 25 |
| Side wall | 4.0 |
| Ledge thickness (bottom) | 3.0 |
| Pocket above the ledge | 132 × 96 |
| Open centre through the bottom | 122 × 82 |
| Ledge width | 5 at the ends, 7 along the sides |
| Finger notches | one U in the middle of each long wall, 34 wide × 21.5 deep from the top (round bottom, radius 17) |
| Mounting tab (+X end) | 22 long × 4.5 thick × 25 tall |
| Mounting hole | 6 diameter, centre 6.5 from the tab's end, at mid-height |

## Sieve inserts (`sieve_insert.py`)

| What | Value |
|---|---|
| Outside | 131.4 × 95.4 × 3.0 (the pocket less 0.6 total clearance); rests on the 3 mm ledge |
| Border | 10 |
| Ribs | 3 |
| Windows | 3 × 2, each 35.1 × 36.2 |
| Pull tabs | 2, centred on the long edges, flush with the outside: 20 along the edge × 6 thick × 18 above the frame |
| Hole taper | holes widen 8° downward |
| Label | hole size debossed on top of the +Y tab |

| Insert | Square hole | Bar | Screen thickness | Holes |
|---|---|---|---|---|
| `sieve_insert_5mm` | 5.0 | 1.2 | 1.6 | 150 |
| `sieve_insert_2mm` | 2.0 | 1.0 | 1.4 | 726 |

The plinko layers (`plinko_layers.py`) use the same 131.4 × 95.4 outside size.

## Gated container (`gated_container.py`), the final design

Same footprint as the sieve inserts, shaken longways (X).

| What | Value |
|---|---|
| Outside | 131.4 × 95.4; walls 2 thick, 16 tall |
| Pull tabs | 20 × 6, top at 21 above the container's bottom: 1 below the box rim, so boxes stack rim on rim; grip them through the box's finger notches |
| Floor | solid, 2 thick at the gate end; slopes 2° up away from the gate (rises 4.06 over the length) |
| Gate strip position | centre at x = 53, held by two rails per side with a 2.3 groove |
| Drop slot | x 54 to 61 (7 long), y ±40, over the box's open bottom; 45° ramp from 61 to the end wall |
| Tower | flip the container 180° on every other level |

| Gate strip | Openings | Count |
|---|---|---|
| Size of every strip | 91.0 × 18 × 2, printed flat | — |
| `gate_w5p0`, `gate_w3p0`, `gate_w2p0` | width gaps 5.0 / 3.0 / 2.0, 8 tall | 11 / 15 / 19 |
| `gate_t1p2`, `gate_t1p4`, `gate_t1p6` | tunnels 8 wide, 1.2 / 1.4 / 1.6 tall | 7 each |

Teeth between openings are 2 wide.
