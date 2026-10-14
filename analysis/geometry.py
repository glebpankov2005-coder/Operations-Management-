"""
Option B layout geometry (metres) - single source for the travel / cycle-time models.
Mirrors warehouse_floorplan.py: zones sized from areas, double-deep rack modules with 3.0 m
reach aisles, and THREE cross-aisles (front, middle, rear) so every storage aisle is open at
both ends - trucks and pickers drive through instead of making U-turns.
"""
import numpy as np

DEPTH = 70.0
RECV, OFF, RET, PACK, OUTB, FWD = 262, 250, 180, 450, 216, 500
dd_area, sel_area, CIRC = 3505, 728, 450
left_w = (OFF + RET + RECV) / DEPTH
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
pitch = BLOCK + AISLEW
n_mod = int((core_w - AISLEW) // pitch)
start = cx0 + (core_w - (n_mod * pitch - AISLEW)) / 2
aisle_x = np.array([start + m * pitch + BLOCK + AISLEW / 2 for m in range(n_mod - 1)])   # storage aisle centres
la, ra = left_w + aisle / 2, cx1 + aisle / 2                                            # perimeter aisles
rvh, uh = RECV / left_w, OUTB / right_w
storage_aisle_len = rack_y1 - rack_y0                                                   # one aisle, both runs
LEVELS, PITCH_M, BASE_M = 8, 1.41, 0.15
lvl_h = BASE_M + PITCH_M * np.arange(LEVELS)
mean_h, top_beam = float(lvl_h.mean()), float(lvl_h.max())
