"""
PICKING PLAN - picking method and picking equipment matched to the demand profile.

Teacher feedback (7-10-2026): a 2-pallet horizontal order picker (ECE 225, 2.4 m forks) does not
fit orders of 1-2 lines, cannot U-turn in 3 m aisles, and "how do we ensure the right volume for
240 x 80 cm in one trip?". So picking is designed from ORDER VOLUME and WEIGHT:

  1. Order cube / weight from the SKU master (each dimensions x picked qty).
  2. Segment orders: SMALL (fits a few totes) -> cluster picking on a manual pick trolley
                     LARGE (pallet-sized)      -> pick-to-pallet with a walkie pallet truck (EJE 120i)
                     full-pallet lines         -> reach truck (ETV 216i, sized in dock_mhe_plan.py)
  3. Pick-time model on the Option B layout (travel + pick + setup) -> lines/h, FTE, equipment.
  4. Tugger train (Jungheinrich EZS 130) evaluated against the volumes it would carry.
Run first in the chain (needs only raw data, geometry and the peak metrics).
"""
import json, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from load_data import combined_outbound, all_storage
from _util import save_table, save_fig, update_metrics, TABLES
from geometry import core_w, aisle_x, storage_aisle_len, fwd_h, rack_y0, cross_y, la, ra, FP_X0, FP_X1

M = json.load(open(os.path.join(os.path.dirname(__file__), "..", "outputs", "reports", "phase1_metrics.json"), encoding="utf-8"))
LINES_PEAKF = M["peak"]["lines"]["peak_over_avg"]
NET_H, MHE_UTIL = 7.5, 0.80
RED, YEL, INK, GREY, BLUE = "#D40511", "#FFCC00", "#262626", "#9aa7bd", "#2b6cb0"

# ------------------------------------------------ design parameters (A024 / A025)
TOTE_L, TOTE_KG = 40.0, 15.0          # 600x400x300 tote: ~40 L usable, <=15 kg for manual handling
TROLLEY_TOTES = 6                      # 3-tier trolley, 1,000 x 600 mm shelves, 2 totes per tier (S011)
SMALL_MAX_L, SMALL_MAX_KG = 4 * TOTE_L, 4 * TOTE_KG   # small order = fits <=4 totes
V_WALK = 0.8                           # m/s walking with a trolley
V_EJE = 5.6 / 3.6 * 0.65               # EJE 120i 5.6 km/h (S010), ~65% effective in aisles
T_LINE_SMALL, T_LINE_LARGE = 25.0, 40.0   # s per line: locate + pick + confirm (eaches vs cases onto pallet)
T_SETUP_SMALL, T_SETUP_LARGE = 90.0, 180.0  # s per tour: trolley+totes / empty pallet + label + drop-off
DELAY = 1.10                           # +10% for searching, congestion, waiting

# ------------------------------------------------ data
ob = combined_outbound(); ob["DATE"] = pd.to_datetime(ob["DATE"], errors="coerce")
n_days = ob["DATE"].dt.date.nunique()
st = pd.concat(all_storage().values(), ignore_index=True)
m = st.groupby("PART").agg(l=("EA LEN", "median"), w=("EA WID", "median"), h=("EA HGT", "median"),
                          kg=("EA WGT", "median"), paq=("PA QTY", "median"))
m["ea_l"] = (m.l * m.w * m.h / 1000).where(lambda s: s.between(0.001, 1000))      # litres per each
abc = pd.read_csv(os.path.join(TABLES, "abc_by_sku.csv")).set_index("PRTNUM")["ABC_vol"]

# ------------------------------------------------ small-parts storage (feedback 2: store small items efficiently)
# Small, slow SKUs whose whole stock fits in one tote (<= 50 L) still take a full pallet location today.
# They move to half-bins on static bin shelving next to the put-wall (zone "V"); a Kardex Shuttle XP 500 lift was
# compared and is the upgrade path (D3 §3.2). A/B small items stay in the fast-pick carton flow.
VLM_STOCK_L, VLM_EA_L, VLM_EA_KG, VLM_EA_CM = 50.0, 20.0, 15.0, 60.0
VLM_RATE = 50.0                        # lines per hour from bin shelving (S028: 50 lines/h in shelving)
SLOT_L, SHELF_SLOTS_BAY = 20.0, 21     # half-bin 300x400 (~20 L); bay 1.0 m x 0.6 m x 2.5 m, 7 levels x 3 half-bins
VLM_TRAYS, VLM_SLOTS_TRAY = 60, 24     # for the Kardex comparison: 4,050 x 813 mm trays (S027), 24 half-bins per tray
latest = all_storage()["ASSA STORAGE DETAILS (01-06-2025).xlsx"]
def _n(c):
    x = pd.to_numeric(latest[c], errors="coerce"); return x.where((x > 0) & (x < 9999))
lt_ = latest.assign(ea_l=_n("EA LEN") * _n("EA WID") * _n("EA HGT") / 1000, q=pd.to_numeric(latest["QTY"], errors="coerce"),
                    ew=_n("EA WGT"), el=_n("EA LEN"))
lt_["cube"] = lt_["q"] * lt_["ea_l"]
sk = lt_.groupby("PART").agg(cube=("cube", "sum"), ea_l=("ea_l", "median"), ew=("ew", "median"), el=("el", "max"))
sk["abc"] = abc.reindex(sk.index).fillna("none")
vlm_mask = (sk.cube <= VLM_STOCK_L) & (sk.ea_l <= VLM_EA_L) & (sk.ew <= VLM_EA_KG) & (sk.el <= VLM_EA_CM) & sk.abc.isin(["C", "none"])
VLM_SKUS = set(sk.index[vlm_mask])
rk = lt_[lt_["LOC TYPE"] == "RACK"]
freed_locs = int(rk.groupby("LOCATION")["PART"].apply(lambda p_: p_.isin(VLM_SKUS).all()).sum())
slots = int(np.ceil(sk.loc[vlm_mask, "cube"] / SLOT_L).clip(lower=1).sum())
vlm_units = int(np.ceil(slots * 1.15 / (VLM_TRAYS * VLM_SLOTS_TRAY)))          # Kardex lifts if chosen (+15% free slots)
shelf_bays = int(np.ceil(slots * 1.15 / SHELF_SLOTS_BAY))                       # bin-shelving bays (+15% free slots)
save_table(sk[vlm_mask].round(2), "small_parts_skus.csv")

L = ob[["ORDER NO", "PRTNUM", "PICKED QTY", "DATE"]].merge(m[["ea_l", "kg", "paq"]], left_on="PRTNUM",
                                                          right_index=True, how="left")
L["litres"] = L["PICKED QTY"] * L["ea_l"]
L["kgs"] = L["PICKED QTY"] * L["kg"]
L["full_pallet"] = L["paq"].gt(0) & L["PICKED QTY"].ge(L["paq"])
L["zone"] = np.where(L["PRTNUM"].isin(VLM_SKUS), "V",
                     np.where(L["PRTNUM"].map(abc).isin(["A", "B"]), "F", "C"))   # V = small-parts shelving, F = fast-pick, C = reserve
P = L[~L["full_pallet"]].copy()                                         # lines that are actually picked

o = P.groupby("ORDER NO").agg(lines=("PRTNUM", "size"), litres=("litres", "sum"), kg=("kgs", "sum"),
                              day=("DATE", "first"))
o["segment"] = np.where((o.litres <= SMALL_MAX_L) & (o.kg <= SMALL_MAX_KG), "small", "large")
o["totes"] = np.maximum(1, np.ceil(np.maximum(o.litres / TOTE_L, o.kg / TOTE_KG))).where(o.segment == "small")
P = P.join(o["segment"], on="ORDER NO")

seg = o.groupby("segment").agg(orders=("lines", "size"), lines=("lines", "sum"), litres=("litres", "sum"))
seg["orders_day"] = seg.orders / n_days; seg["lines_day"] = seg.lines / n_days
seg["pct_orders"] = seg.orders / seg.orders.sum() * 100
seg["pct_lines"] = seg.lines / seg.lines.sum() * 100
seg["pct_volume"] = seg.litres / seg.litres.sum() * 100
order_pct = {k: round(float((o.litres <= v).mean() * 100), 1) for k, v in
             [("1_tote", TOTE_L), ("4_totes", 4 * TOTE_L), ("1_pallet_1000L", 1000), ("2_pallets_2300L", 2300)]}

# ------------------------------------------------ travel models on the layout
L_F = FP_X1 - FP_X0                       # length of the fast-pick pick aisle (geometry.py)
A = len(aisle_x); SPAN = float(aisle_x[-1] - aisle_x[0])
def dist_F(n):                            # return routing along the module (P&D at east end, next to packing)
    return 0.0 if n <= 0 else 2 * L_F * n / (n + 1)
# Reserve zone: routing policies from the W3 lecture (S-shape, return, midpoint, largest gap) compared by Monte
# Carlo on the real aisle geometry (aisles open at both ends; P&D at the east end of the front cross-aisle).
LB = storage_aisle_len
X_PD = float(aisle_x[-1]) + 5.0
RNG = np.random.default_rng(7)
def _route(policy, aisles, ys):
    xs = aisle_x[aisles]; horiz = 2 * (X_PD - xs.min())
    picked = np.unique(aisles); k = len(picked)
    ymax = {a: ys[aisles == a].max() for a in picked}
    if policy == "Return" or (k == 1 and policy in ("Midpoint", "Largest gap")):
        return horiz + sum(2 * v for v in ymax.values())
    if policy == "S-shape":
        last = picked[-1]                                  # aisle nearest the P&D is done last
        return horiz + (k - 1 if k % 2 else k) * LB + (2 * ymax[last] if k % 2 else 0)
    vert = 2 * LB                                          # first and last picked aisles traversed fully
    for a in picked[1:-1]:
        y = np.sort(ys[aisles == a])
        if policy == "Midpoint":
            f, b = y[y <= LB / 2], y[y > LB / 2]
            vert += (2 * f.max() if len(f) else 0) + (2 * (LB - b.min()) if len(b) else 0)
        else:                                              # Largest gap: skip the biggest empty stretch
            gaps = np.diff(np.concatenate([[0], y, [LB]]))
            vert += 2 * (LB - gaps.max())
    return horiz + vert
POLICIES = ["S-shape", "Return", "Midpoint", "Largest gap"]
def route_compare(n, sims=3000):
    out = {p: [] for p in POLICIES}
    for _ in range(sims):
        m = max(1, RNG.poisson(n)) if n < 8 else int(round(n))
        a = RNG.integers(0, A, m); y = RNG.uniform(0, LB, m)
        for p in POLICIES:
            out[p].append(_route(p, a, y))
    return {p: float(np.mean(v)) for p, v in out.items()}
_route_cache = {}
def dist_C(n):                            # expected walk with the BEST policy for this tour size
    if n <= 0: return 0.0
    key = round(n, 1)
    if key not in _route_cache:
        _route_cache[key] = route_compare(n)
    return min(_route_cache[key].values())

# ------------------------------------------------ SMALL orders: zone BATCH picking on trolleys, sorted at the put-wall
# The WMS builds each trolley batch from the wave's lines in one zone, filled to the trolley's VOLUME and
# WEIGHT limit (from SKU cube data) - this is how "the right volume per trip" is guaranteed.
s_ord = o[o.segment == "small"]
orders_per_trolley = TROLLEY_TOTES / float(s_ord.totes.mean())      # if picked order-per-tote (cluster) instead
WAVES = 3
TROLLEY_L, TROLLEY_KG = TROLLEY_TOTES * TOTE_L * 0.8, 250 * 0.8      # fill to 80%
small_rows = []
for z in ["F", "C"]:
    lz = P[(P.segment == "small") & (P.zone == z)]
    lines_day = len(lz) / n_days
    n_vol = TROLLEY_L / max(float(lz.litres.mean()), 0.1)
    n_kg = TROLLEY_KG / max(float(lz.kgs.mean()), 0.1)
    n = float(min(n_vol, n_kg, lines_day / WAVES))                     # lines per tour (capacity- or wave-limited)
    d = dist_F(n) if z == "F" else dist_C(n)
    t_tour = (T_SETUP_SMALL + d / V_WALK + n * T_LINE_SMALL) * DELAY
    rate = n / t_tour * 3600
    small_rows.append({"Zone": "Fast-pick area (A/B)" if z == "F" else "Reserve low levels (C)",
                       "Lines/day": round(lines_day, 0), "Lines per tour": round(n, 1),
                       "Tour limited by": ["trolley volume", "trolley weight", "wave size"][int(np.argmin([n_vol, n_kg, lines_day / WAVES]))],
                       "Walk per tour (m)": round(d, 0), "Tour (min)": round(t_tour / 60, 1),
                       "Lines/h": round(rate, 0), "Tours/day": round(lines_day / n, 1),
                       "Picker-h avg": round(lines_day / rate, 2), "Picker-h peak": round(lines_day * LINES_PEAKF / rate, 2)})
small = pd.DataFrame(small_rows)

# ------------------------------------------------ LARGE orders: pick-to-pallet with EJE 120i (one order per pallet)
l_ord = o[o.segment == "large"]
lz = P[P.segment == "large"]
nF = (lz.zone == "F").sum() / len(l_ord); nC = (lz.zone == "C").sum() / len(l_ord); nV = (lz.zone == "V").sum() / len(l_ord)
d_large = dist_F(nF) + dist_C(nC)
t_order = (T_SETUP_LARGE + d_large / V_EJE + (nF + nC) * T_LINE_LARGE) * DELAY
large_orders_day = len(l_ord) / n_days
large = {"orders_day": round(large_orders_day, 1), "lines_per_order": round(float(nF + nC + nV), 1), "lines_vlm": round(float(nV), 1),
         "lines_fast_pick": round(float(nF), 1), "lines_reserve": round(float(nC), 1),
         "walk_per_order_m": round(d_large, 0), "min_per_order": round(t_order / 60, 1),
         "lines_per_h": round((nF + nC) / t_order * 3600, 0),
         "picker_h_avg": round(large_orders_day * t_order / 3600, 2),
         "picker_h_peak": round(large_orders_day * LINES_PEAKF * t_order / 3600, 2),
         "kg_median": round(float(l_ord.kg.median()), 0), "kg_p90": round(float(l_ord.kg.quantile(.9)), 0),
         "litres_median": round(float(l_ord.litres.median()), 0)}

# ------------------------------------------------ routing-policy comparison (W3) for the tours actually planned
n_small_C = float(small.loc[small.Zone.str.startswith("Reserve"), "Lines per tour"].iloc[0])
routing = []
for label, n_ in [("Small-order trolley tour (reserve zone)", n_small_C), ("Large-order pallet tour (reserve part)", float(nC))]:
    r_ = _route_cache.get(round(n_, 1)) or route_compare(n_)
    best = min(r_, key=r_.get)
    routing.append({"Tour": label, "Lines in reserve": round(n_, 1), **{k: round(v, 0) for k, v in r_.items()}, "Best": best})
save_table(pd.DataFrame(routing).set_index("Tour"), "picking_routing_policies.csv")

# ------------------------------------------------ small-parts shelving picking (next to the put-wall, all orders)
v_lines_day = float((P.zone == "V").sum() / n_days)
vlm = {"skus": int(len(VLM_SKUS)), "stock_m3": round(float(sk.loc[vlm_mask, "cube"].sum() / 1000), 1),
       "slots_needed": slots, "shelf_bays": shelf_bays, "slots_per_bay": SHELF_SLOTS_BAY,
       "lift_units": vlm_units, "trays": VLM_TRAYS, "slots_per_tray": VLM_SLOTS_TRAY,
       "freed_rack_locations": freed_locs, "lines_day": round(v_lines_day, 1), "rate_lines_h": VLM_RATE,
       "picker_h_avg": round(v_lines_day / VLM_RATE, 2), "picker_h_peak": round(v_lines_day * LINES_PEAKF / VLM_RATE, 2),
       "criteria": {"stock_l_max": VLM_STOCK_L, "each_l_max": VLM_EA_L, "each_kg_max": VLM_EA_KG, "each_cm_max": VLM_EA_CM,
                    "abc": "C or no demand in Q2"},
       "skus_small_ab_in_fast_pick": int(((sk.cube <= VLM_STOCK_L) & sk.abc.isin(["A", "B"])).sum())}

# ------------------------------------------------ people and equipment
small_h_avg, small_h_pk = small["Picker-h avg"].sum(), small["Picker-h peak"].sum()
pick_fte_avg = (small_h_avg + large["picker_h_avg"] + vlm["picker_h_avg"]) / NET_H
pick_fte_pk = (small_h_pk + large["picker_h_peak"] + vlm["picker_h_peak"]) / NET_H
small_pickers_pk = int(np.ceil(small_h_pk / NET_H))
trolleys = 2 * max(small_pickers_pk, 2) + 2                      # one picking + one at the put-wall per picker, +2 spare
eje_need = max(1, int(np.ceil(large["picker_h_peak"] / (NET_H * MHE_UTIL))))
equipment = [
    {"Item": "Pick trolley (3-tier, 6 totes)", "Use": "Small orders - cluster picking in zones",
     "Required": small_pickers_pk, "Planned": trolleys, "Why this number": "2 per picker (picking + at put-wall) + 2 spare"},
    {"Item": "Totes 600x400 (~40 L)", "Use": "One per small order (more if >40 L / >15 kg)",
     "Required": trolleys * TROLLEY_TOTES, "Planned": int(trolleys * TROLLEY_TOTES * 1.5), "Why this number": "trolleys x 6 + 50% in circulation at packing"},
    {"Item": "Jungheinrich EJE 120i walkie pallet truck", "Use": "Large orders - pick-to-pallet",
     "Required": eje_need, "Planned": eje_need + 1 if eje_need == 1 else eje_need,
     "Why this number": "peak hours / (7.5 h x 80%); no spare once 2+ trucks (one breakdown still covers an average day)"},
]

# ------------------------------------------------ tugger-train evaluation (Jungheinrich EZS 130)
y_front = (fwd_h + rack_y0) / 2
loop_m = 2 * (ra - la) + 2 * (cross_y - y_front)                 # front cross-aisle + perimeter + middle cross-aisle
v_tug = 10.5 / 3.6 * 0.5                                         # EZS 130 10.5 km/h (S012), ~50% with stops/turns
runs_day = int(NET_H * 60 / 20)                                  # a run every 20 min
t_run = loop_m / v_tug + 6 * 30                                  # + 6 P&D stops x 30 s
tug_h = runs_day * t_run / 3600
trolley_moves_day = float(small["Tours/day"].sum())
walk_saved_h = trolley_moves_day * 2 * 15 / V_WALK / 3600        # pickers would otherwise push ~15 m to the put-wall
tugger = {"loop_m": round(loop_m, 0), "runs_per_day": runs_day, "min_per_run": round(t_run / 60, 1),
          "driver_h_day": round(tug_h, 1), "driver_utilisation_pct": round(tug_h / NET_H * 100, 0),
          "trolleys_per_day": round(trolley_moves_day, 0), "trolleys_per_run": round(trolley_moves_day / runs_day, 1),
          "picker_walk_saved_h_day": round(walk_saved_h, 2),
          "verdict": "Not justified at current volume - keep as scale-up option"}

# ------------------------------------------------ put-to-light wall (sorting batch picks into orders)
# Each order gets one tote slot per tote it needs; slots open for the orders of one wave (peak day, +20%).
PW_LEVELS, PW_COL_W, PW_DEPTH, PW_WORK = 5, 0.45, 0.6, 1.5      # 5 levels 0.2-2.0 m; 450 mm per column; work strip each side
small_wave_pk = float(seg.loc["small", "orders_day"]) * LINES_PEAKF / WAVES
pw_slots = int(np.ceil(small_wave_pk * float(s_ord.totes.mean()) * 1.2 / 10) * 10)
pw_cols = int(np.ceil(pw_slots / PW_LEVELS))
PUTWALL = {"slots": pw_cols * PW_LEVELS, "columns": pw_cols, "levels": PW_LEVELS, "length_m": round(pw_cols * PW_COL_W, 1),
           "depth_m": PW_DEPTH, "area_m2": round(pw_cols * PW_COL_W * (PW_DEPTH + 2 * PW_WORK), 0),
           "small_orders_wave_avg": round(float(seg.loc["small", "orders_day"]) / WAVES, 0), "small_orders_wave_peak": round(small_wave_pk, 0),
           "put_s_per_line": 8.0}

# ------------------------------------------------ fast-pick faces: does every A/B item get a pick face? (storage check, A046)
# The carton-flow row (geometry.py) holds the most-picked A/B items that fit a lane; the top 1% get a second lane
# (duplicate face, peak_slotting.py). Across the pick aisle the wall row holds the rest: shelf slots for the other
# A/B items, long-item shelves (items lie lengthwise) and floor pallet faces for heavy or bulky cases. All of them
# face the same pick aisle, so the walk in the pick-time model (dist_F) does not change.
from geometry import FP_N_FLOW_BAYS, FP_FLOW_LEVELS, FP_FLOW_LANES, FP_X0, FP_X1, FP_PAL_W, FP_SHELF_W, FP_LONG_W
LANE_CM, LANE_KG = (28.0, 33.0, 60.0), 15.0               # fits a lane: each <= 28 x 33 x 60 cm and <= 15 kg
FP_SHELF_SLOTS, FP_LONG_SLOTS = 21, 12                    # shelving bay 7 levels x 3 slots (as small parts); long bay 6 x 2
fF = P[P.zone == "F"].groupby("PRTNUM").size().sort_values(ascending=False)          # A/B items picked in Q2, by lines
dims = np.sort(m.reindex(fF.index)[["l", "w", "h"]].astype(float).values, axis=1)   # smallest .. largest side (cm)
kg_f = m.reindex(fF.index)["kg"].astype(float).fillna(0).values
known = ~np.isnan(dims[:, 2])
lane_fit = known & (dims[:, 0] <= LANE_CM[0]) & (dims[:, 1] <= LANE_CM[1]) & (dims[:, 2] <= LANE_CM[2]) & (kg_f <= LANE_KG)
long_fp = known & ~lane_fit & (dims[:, 2] > LANE_CM[2])
bulky_fp = known & ~lane_fit & ~long_fp
lines_sku = P.groupby("PRTNUM").size().sort_values(ascending=False)
top1 = set(lines_sku.head(max(1, int(len(lines_sku) * 0.01))).index)                # extreme SKUs: a second face
n_lanes = FP_N_FLOW_BAYS * FP_FLOW_LEVELS * FP_FLOW_LANES
fit_ids = fF.index[lane_fit]                                                      # sorted by lines
dup = int(sum(1 for s_ in fit_ids[:n_lanes] if s_ in top1))
in_lane = fit_ids[: n_lanes - dup]
shelf_ids = fF.index[(lane_fit & ~fF.index.isin(in_lane)) | ~known]
fp_shelf_bays = int(np.ceil(len(shelf_ids) * 1.15 / FP_SHELF_SLOTS))             # +15% free slots, as the small parts
fp_long_bays = int(np.ceil(long_fp.sum() * 1.15 / FP_LONG_SLOTS))
fp_pal_faces = int(np.ceil(bulky_fp.sum() * 1.15))
wall_row_m = fp_pal_faces * FP_PAL_W + fp_shelf_bays * FP_SHELF_W + fp_long_bays * FP_LONG_W
assert wall_row_m <= FP_X1 - FP_X0, "fast-pick wall row too short for its faces"
def _share(ids):
    return round(float(fF.reindex(ids).sum() / fF.sum() * 100), 1)
fast_pick = {"skus": int(len(fF)), "lines_day": round(float(fF.sum() / n_days), 0),
             "share_of_picked_lines_pct": round(float(fF.sum() / len(P) * 100), 1),
             "flow_bays": FP_N_FLOW_BAYS, "flow_lanes": int(n_lanes), "skus_in_lanes": int(len(in_lane)), "duplicate_lanes": dup,
             "lane_lines_pct": _share(in_lane),
             "shelf_skus": int(len(shelf_ids)), "shelf_bays": fp_shelf_bays, "shelf_lines_pct": _share(shelf_ids),
             "long_skus": int(long_fp.sum()), "long_bays": fp_long_bays, "long_lines_pct": _share(fF.index[long_fp]),
             "bulky_skus": int(bulky_fp.sum()), "pallet_faces": fp_pal_faces, "bulky_lines_pct": _share(fF.index[bulky_fp]),
             "wall_row_m": round(wall_row_m, 1), "wall_row_available_m": round(FP_X1 - FP_X0, 1),
             "lane_limit_cm": list(LANE_CM), "lane_limit_kg": LANE_KG, "shelf_slots_bay": FP_SHELF_SLOTS, "long_slots_bay": FP_LONG_SLOTS}

# ------------------------------------------------ outputs
seg_out = seg[["orders_day", "lines_day", "pct_orders", "pct_lines", "pct_volume"]].round(1)
save_table(seg_out, "picking_segments.csv"); save_table(small.set_index("Zone"), "picking_small_orders.csv")
save_table(pd.DataFrame(equipment).set_index("Item"), "picking_equipment.csv")
update_metrics("picking", {
    "small_parts": vlm, "fast_pick": fast_pick,
    "params": {"tote_l": TOTE_L, "tote_kg": TOTE_KG, "trolley_totes": TROLLEY_TOTES, "small_max_l": SMALL_MAX_L,
               "small_max_kg": SMALL_MAX_KG, "v_walk": V_WALK, "v_eje": round(V_EJE, 2), "t_line_small": T_LINE_SMALL,
               "t_line_large": T_LINE_LARGE, "delay": DELAY},
    "order_volume": {"median_l": round(float(o.litres.median()), 1), "p75_l": round(float(o.litres.quantile(.75)), 0),
                     "p90_l": round(float(o.litres.quantile(.9)), 0), "median_kg": round(float(o.kg.median()), 1),
                     "pct_orders_fitting": order_pct,
                     "share_volume_orders_over_1m3_pct": round(float(o.litres[o.litres > 1000].sum() / o.litres.sum() * 100), 0)},
    "segments": seg_out.reset_index().to_dict("records"),
    "orders_per_trolley": round(orders_per_trolley, 1),
    "totes_per_small_order": round(float(s_ord.totes.mean()), 2),
    "putwall": PUTWALL,
    "small_order_totes_share": {int(k): round(float(v) * 100, 1) for k, v in s_ord.totes.value_counts(normalize=True).sort_index().items()},
    "small_orders": small.to_dict("records"), "large_orders": large,
    "pick_fte_avg": round(pick_fte_avg, 2), "pick_fte_peak": round(pick_fte_pk, 2),
    "equipment": equipment, "tugger": tugger, "routing": routing,
})

# figure: order volume -> which container fits
fig, ax = plt.subplots(figsize=(8.2, 3.5))
labels = ["1 tote\n(≤40 L)", "4 totes\n(≤160 L)", "1 pallet\n(≤1,000 L)", "2 pallets 240×80\n(≤2,300 L)"]
vals = [order_pct["1_tote"], order_pct["4_totes"], order_pct["1_pallet_1000L"], order_pct["2_pallets_2300L"]]
bars = ax.bar(labels, vals, color=[RED, RED, YEL, GREY], zorder=3, width=0.6)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.0f}%", ha="center", weight="bold", fontsize=10)
ax.set_ylim(0, 112); ax.set_ylabel("% of orders that fit")
ax.set_title(f"Typical order = {o.litres.median():.0f} litres - most orders fit in a tote, not on two pallets")
save_fig(fig, "picking_order_volume.png")

print("SEGMENTS\n", seg_out.to_string())
print("orders fitting:", order_pct, "| orders per trolley", round(orders_per_trolley, 1))
print("SMALL\n", small.to_string(index=False))
print("LARGE", large)
print(f"PICK FTE avg {pick_fte_avg:.2f} peak {pick_fte_pk:.2f}")
print("EQUIP", [(e['Item'], e['Required'], e['Planned']) for e in equipment])
print("TUGGER", tugger)
print("SMALL PARTS", vlm)
print("FAST-PICK FACES", fast_pick)
print("ROUTING"); [print(" ", r) for r in routing]
