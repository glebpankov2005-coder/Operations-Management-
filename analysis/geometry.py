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

# ---- receiving doors (west wall). R1 = container dock at the container zone. R2 sits in the NORTH half of receiving:
# on a big-container day R2 is blocked and that half (131 m2, dock_mhe_plan.py) becomes extra unpacking space, while
# trailers keep using R3 in the SOUTH half - so the two uses never overlap.
R_DOORS = {"R1": rvh + 3.2, "R2": rvh * 0.75, "R3": rvh * 0.25}
S_DOOR_PITCH = 4.3                              # shipping doors S1-S5 on the east wall, centred on outbound staging
S_DOORS = {f"S{i + 1}": uh / 2 + (i - 2) * S_DOOR_PITCH for i in range(5)}

# ---- fast-pick band internals (south band of the storage core) ----
# South -> north: WALL ROW (floor pallet faces, shelving, long-item shelves) | PICK AISLE | CARTON-FLOW ROW | REFILL STRIP,
# then the front cross-aisle. The carton flow is refilled from the REAR (refill strip; the reach truck stays in the
# cross-aisle) and picked from the FRONT (pick aisle): pickers and reach trucks never share a face.
FP_X0, FP_X1 = cx0 + 2.0, cx1 - 2.0             # 63.6 m of pick faces (= the fast-pick length in picking_plan.py)
FP_WALL_Y0, FP_PAL_D, FP_SHELF_D = 0.2, 1.2, 0.6   # wall row: pallets 1.2 m deep, shelving 0.6 m deep
FP_AISLE_Y0 = FP_WALL_Y0 + FP_PAL_D             # pick aisle 1.4 - 4.0 m (2.6 m: trolley and EJE 120i pass)
FP_FLOW_Y0, FP_FLOW_D = 4.0, 1.8                # carton-flow lanes 1.8 m deep: pick face at 4.0 m, rear at 5.8 m
FP_REFILL_Y0 = FP_FLOW_Y0 + FP_FLOW_D           # refill strip 5.8 m - fwd_h (~1.6 m)
FP_AISLE_Y = (FP_AISLE_Y0 + FP_FLOW_Y0) / 2     # where pickers walk
FP_FLOW_BAY, FP_FLOW_LEVELS, FP_FLOW_LANES = 2.0, 5, 6   # 2 m bay, 5 sloping levels x 6 lanes (lane ~0.33 m wide)
FP_N_FLOW_BAYS = int((FP_X1 - FP_X0) // FP_FLOW_BAY)
FP_PAL_W, FP_SHELF_W, FP_LONG_W = 0.9, 1.0, 2.2  # widths along the wall: pallet face, shelving bay, long-item bay

# ---- container zone internals (dock_mhe_plan.py sizes the parts) ----
LZ_Y0 = rvh                                     # container zone: y = rvh .. rvh + lzh, x = 0 .. left_w
CONV_Y, CONV_LEN = R_DOORS["R1"], 10.5           # extendable roller conveyor from door R1 into the zone
BUILD_W = 1.6                                   # build spot 1.6 x 1.6 m (pallet + working space), 6 each side of the conveyor
WRAP_XY = (left_w - 4.4, rvh + lzh - 4.4)        # label / scan / stretch-wrap station 4 x 4 m, next to the left aisle

# ---- packing area internals (east column): one place for the floor plan and the put-wall figures ----
# South part: put-to-light wall with the PICK side facing west (right perimeter aisle, where pickers arrive)
# and the PACK side facing east (pack stations, then roll cages per carrier). North part: small-parts shelving.
PK_Y0 = DEPTH - PACK / right_w              # south edge of packing (outbound staging lies directly south of it)
PW_X0, PW_DEPTH, PW_LEN = rax + 2.2, 0.6, 10.8   # wall: 24 columns x 0.45 m = 10.8 m (picking_plan.py sizes 120 slots)
PW_Y0 = PK_Y0 + 5.0                         # 5 m strip south of the wall: large-order pallets, stretch wrapper
BENCH_X0, BENCH_W, N_BENCH = PW_X0 + PW_DEPTH + 1.5, 1.8, 4
CAGE_X0 = BENCH_X0 + BENCH_W + 0.4          # roll cages per carrier, east of the pack stations
SHELF_Y0 = PW_Y0 + PW_LEN + 3.0             # small-parts shelving rows start 3 m north of the wall (empty totes, walkway)
