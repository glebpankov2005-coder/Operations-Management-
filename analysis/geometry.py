"""
Option B layout geometry (metres) - single source for the travel / cycle-time models.
Mirrors warehouse_floorplan.py: zones sized from areas, SINGLE-DEEP back-to-back rack modules (one pallet
each side of the rack, 2 x 1.2 m rows = 2.6 m block) with 3.0 m reach aisles, and THREE cross-aisles (front, middle, rear) so every storage aisle is open at
both ends - trucks and pickers drive through instead of making U-turns.
"""
import numpy as np

DEPTH = 70.0
RECV, OFF, RET, PACK, OUTB, FWD = 262, 250, 180, 450, 216, 500
LOOSE = 190                                 # loose-container zone next to door R1 (teacher feedback); sized in dock_mhe_plan.py
dd_area, sel_area, CIRC = 3505, 728, 450
left_w = (OFF + RET + LOOSE + RECV) / DEPTH
right_w = (PACK + OUTB) / DEPTH
core_w = (dd_area + sel_area + FWD) / DEPTH
aisle = CIRC / (2 * DEPTH)                  # perimeter aisle width (~3.2 m)
cx0 = left_w + aisle; cx1 = cx0 + core_w; rax = cx1 + aisle
L = rax + right_w
fwd_h = FWD / core_w                        # fast-pick module depth along the south wall
END_AISLE = 3.2                             # front + rear cross-aisles
rack_y0, rack_y1 = fwd_h + END_AISLE, DEPTH - END_AISLE
cross_y = (rack_y0 + rack_y1) / 2           # middle cross-aisle centre (3.2 m wide)
BLOCK, AISLEW = 2.6, 3.0
LONG_AISLE = 3.2                            # aisle in front of the long-goods module: 2.05 m loads crosswise need ~3.0 m (D3 check)
pitch = BLOCK + AISLEW
n_mod = 11                                  # 9 standard + 1 odd/irregular + 1 long-goods module (fits: see D3 long-item check)
aisle_w = [AISLEW] * (n_mod - 2) + [LONG_AISLE]                                       # aisle i lies right of module i
span = n_mod * BLOCK + sum(aisle_w)
start = cx0 + (core_w - span) / 2
mod_x = np.array([start + m * BLOCK + sum(aisle_w[:m]) for m in range(n_mod)])           # left edge of each module
aisle_x = np.array([mod_x[m] + BLOCK + aisle_w[m] / 2 for m in range(n_mod - 1)])       # storage aisle centres
LONG_BAY, LONG_PER_BAY = 4.5, 2             # long-goods bays: 4.5 m beams hold two 2.05 m pallets
la, ra = left_w + aisle / 2, cx1 + aisle / 2                                            # perimeter aisles
rvh, uh = RECV / left_w, OUTB / right_w
lzh = LOOSE / left_w                        # loose-container zone depth (sits directly north of receiving)
storage_aisle_len = rack_y1 - rack_y0                                                   # one aisle, both runs
LEVELS, PITCH_M, BASE_M = 8, 1.41, 0.15
lvl_h = BASE_M + PITCH_M * np.arange(LEVELS)
mean_h, top_beam = float(lvl_h.mean()), float(lvl_h.max())

# ---- packing area internals (east column): one place for the floor plan and the put-wall figures ----
# South part: put-to-light wall with the PICK side facing west (right perimeter aisle, where pickers arrive)
# and the PACK side facing east (pack stations, then roll cages per carrier). North part: small-parts shelving.
PK_Y0 = DEPTH - PACK / right_w              # south edge of packing (outbound staging lies directly south of it)
PW_X0, PW_DEPTH, PW_LEN = rax + 2.2, 0.6, 10.8   # wall: 24 columns x 0.45 m = 10.8 m (picking_plan.py sizes 120 slots)
PW_Y0 = PK_Y0 + 5.0                         # 5 m strip south of the wall: large-order pallets, stretch wrapper
BENCH_X0, BENCH_W, N_BENCH = PW_X0 + PW_DEPTH + 1.5, 1.8, 4
CAGE_X0 = BENCH_X0 + BENCH_W + 0.4          # roll cages per carrier, east of the pack stations
SHELF_Y0 = PW_Y0 + PW_LEN + 3.0             # small-parts shelving rows start 3 m north of the wall (empty totes, walkway)
