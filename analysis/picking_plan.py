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
from geometry import core_w, aisle_x, storage_aisle_len, fwd_h, rack_y0, cross_y, la, ra

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

L = ob[["ORDER NO", "PRTNUM", "PICKED QTY", "DATE"]].merge(m[["ea_l", "kg", "paq"]], left_on="PRTNUM",
                                                          right_index=True, how="left")
L["litres"] = L["PICKED QTY"] * L["ea_l"]
L["kgs"] = L["PICKED QTY"] * L["kg"]
L["full_pallet"] = L["paq"].gt(0) & L["PICKED QTY"].ge(L["paq"])
L["zone"] = np.where(L["PRTNUM"].map(abc).isin(["A", "B"]), "F", "C")   # F = fast-pick area, C = reserve low levels
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
L_F = core_w - 4.0                        # usable length of the fast-pick module front
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
nF = (lz.zone == "F").sum() / len(l_ord); nC = (lz.zone == "C").sum() / len(l_ord)
d_large = dist_F(nF) + dist_C(nC)
t_order = (T_SETUP_LARGE + d_large / V_EJE + (nF + nC) * T_LINE_LARGE) * DELAY
large_orders_day = len(l_ord) / n_days
large = {"orders_day": round(large_orders_day, 1), "lines_per_order": round(float(nF + nC), 1),
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

# ------------------------------------------------ people and equipment
small_h_avg, small_h_pk = small["Picker-h avg"].sum(), small["Picker-h peak"].sum()
pick_fte_avg = (small_h_avg + large["picker_h_avg"]) / NET_H
pick_fte_pk = (small_h_pk + large["picker_h_peak"]) / NET_H
small_pickers_pk = int(np.ceil(small_h_pk / NET_H))
trolleys = 2 * max(small_pickers_pk, 2) + 2                      # one picking + one at the put-wall per picker, +2 spare
eje_need = max(1, int(np.ceil(large["picker_h_peak"] / (NET_H * MHE_UTIL))))
equipment = [
    {"Item": "Pick trolley (3-tier, 6 totes)", "Use": "Small orders - cluster picking in zones",
     "Required": small_pickers_pk, "Planned": trolleys, "Why this number": "2 per picker (picking + at put-wall) + 2 spare"},
    {"Item": "Totes 600x400 (~40 L)", "Use": "One per small order (more if >40 L / >15 kg)",
     "Required": trolleys * TROLLEY_TOTES, "Planned": int(trolleys * TROLLEY_TOTES * 1.5), "Why this number": "trolleys x 6 + 50% in circulation at packing"},
    {"Item": "Jungheinrich EJE 120i walkie pallet truck", "Use": "Large orders - pick-to-pallet",
     "Required": eje_need, "Planned": eje_need + 1, "Why this number": "peak hours / (7.5 h x 80%) + 1 spare"},
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

# ------------------------------------------------ outputs
seg_out = seg[["orders_day", "lines_day", "pct_orders", "pct_lines", "pct_volume"]].round(1)
save_table(seg_out, "picking_segments.csv"); save_table(small.set_index("Zone"), "picking_small_orders.csv")
save_table(pd.DataFrame(equipment).set_index("Item"), "picking_equipment.csv")
update_metrics("picking", {
    "params": {"tote_l": TOTE_L, "tote_kg": TOTE_KG, "trolley_totes": TROLLEY_TOTES, "small_max_l": SMALL_MAX_L,
               "small_max_kg": SMALL_MAX_KG, "v_walk": V_WALK, "v_eje": round(V_EJE, 2), "t_line_small": T_LINE_SMALL,
               "t_line_large": T_LINE_LARGE, "delay": DELAY},
    "order_volume": {"median_l": round(float(o.litres.median()), 1), "p75_l": round(float(o.litres.quantile(.75)), 0),
                     "p90_l": round(float(o.litres.quantile(.9)), 0), "median_kg": round(float(o.kg.median()), 1),
                     "pct_orders_fitting": order_pct,
                     "share_volume_orders_over_1m3_pct": round(float(o.litres[o.litres > 1000].sum() / o.litres.sum() * 100), 0)},
    "segments": seg_out.reset_index().to_dict("records"),
    "orders_per_trolley": round(orders_per_trolley, 1),
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
print("ROUTING"); [print(" ", r) for r in routing]
