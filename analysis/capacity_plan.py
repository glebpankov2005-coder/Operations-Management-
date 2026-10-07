"""
PHASE 5 - CAPACITY PLAN (labour) for the recommended Option B.

Workload drivers are MEASURED from the data. Productivities are documented
BENCHMARK assumptions (A014, to validate with DHL). Computes FTE per process at
AVERAGE and PEAK day.

Design rules applied (teacher / Rogier feedback):
  * Pick type is derived from what the client ORDERED (line qty vs the SKU's
    case and pallet quantity) - NOT from DHL's historical pick-type flags.
  * Inbound volume is the measured number of loads received (ADD DATE in the
    storage snapshots), arriving as 2 shipments/day from Assa Abloy factories,
    partly palletised and partly LOOSE in sea containers (de-stuffed by hand).
Machinery (MHE) and dock doors are sized separately in dock_mhe_plan.py.
"""
import numpy as np
import pandas as pd
from load_data import combined_outbound, all_storage
from _util import save_table, save_fig, update_metrics
import matplotlib.pyplot as plt
import json, os

M = json.load(open(os.path.join(os.path.dirname(__file__), "..", "outputs", "reports", "phase1_metrics.json"), encoding="utf-8"))
lines_peakf = M["peak"]["lines"]["peak_over_avg"]   # 1.83
units_peakf = M["peak"]["units"]["peak_over_avg"]   # 2.85
lines_avg = M["peak"]["lines"]["mean"]              # 640
units_avg = M["peak"]["units"]["mean"]              # 22,269

ASIA = {"CN", "TW", "KR", "VN", "JP", "IN", "TH", "MY", "ID", "HK", "PH", "SG"}

# ---------------------------------------------------------------- load data
ob = combined_outbound()
ob["DATE"] = pd.to_datetime(ob["DATE"], errors="coerce")
n_days = ob["DATE"].dt.date.nunique()
storage = all_storage()
st_all = pd.concat(storage.values(), ignore_index=True)

# ------------------------------------------- ORDER-DERIVED pick type (Rogier)
master = st_all.groupby("PART").agg(paq=("PA QTY", "median"), csq=("CS QTY", "median"))
L = ob[["PRTNUM", "PICKED QTY", "DATE"]].merge(master, left_on="PRTNUM", right_index=True, how="left")
q = L["PICKED QTY"]
full = L["paq"].gt(0) & q.ge(L["paq"])
case = ~full & L["csq"].gt(1) & q.ge(L["csq"])
L["pick_type"] = np.select([full, case], ["full pallet", "case"], default="each")
L.loc[L["paq"].isna() & L["csq"].isna(), "pick_type"] = "each"   # no master data -> treat as each (slowest, conservative)
share_lines = (L["pick_type"].value_counts(normalize=True) * 100).round(1).to_dict()
share_units = (L.groupby("pick_type")["PICKED QTY"].sum() / L["PICKED QTY"].sum() * 100).round(1).to_dict()
n_no_master = int((ob["PRTNUM"].isin(master.index) == False).sum())

lines_each = lines_avg * share_lines.get("each", 0) / 100
lines_case = lines_avg * share_lines.get("case", 0) / 100
lines_pallet = lines_avg * share_lines.get("full pallet", 0) / 100

# forward/pick-location replenishment: pallet-equivalents consumed by case+each picking per day
pick_units = L[L["pick_type"] != "full pallet"].groupby("PRTNUM")["PICKED QTY"].sum()
paq = master["paq"].reindex(pick_units.index)
replen_pallets_day = float((pick_units / paq.where(paq > 0)).sum() / n_days)

# ------------------------------------------------ outbound pallets (measured)
ship = ob.drop_duplicates("SHIPMENT ID")
ship_pallets = pd.to_numeric(ship["SHIPMENT PACKED PALLETS"], errors="coerce").fillna(0)
ship_cartons = pd.to_numeric(ship["SHIPMENT PACKED CARTONS"], errors="coerce").fillna(0)
outbound_pallets_day = float(ship_pallets.sum() / n_days)
outbound_cartons_day = float(ship_cartons.sum() / n_days)
pal_by_day = ship.assign(p=ship_pallets).groupby(ship["DATE"].dt.date)["p"].sum()

# -------------------------------------------- inbound loads received (measured)
# Loads booked in during the 14 days before each snapshot (ADD DATE). Loads already
# shipped out before the snapshot are invisible, so this is a LOWER BOUND.
win_rows = []
for name, s in storage.items():
    snap = pd.to_datetime(s["DATE"].iloc[0])
    add = pd.to_datetime(s["ADD DATE"], errors="coerce")
    w = s[(add >= snap - pd.Timedelta(days=14)) & (add < snap)].copy()
    w["ADD"] = pd.to_datetime(w["ADD DATE"], errors="coerce")
    w = w.drop_duplicates("LODNUM")
    per_day = w.groupby(w["ADD"].dt.date)["LODNUM"].nunique()
    asia = w["ORGCOD"].astype(str).isin(ASIA).mean() * 100
    win_rows.append({"snapshot": str(snap.date()), "receiving_days": int(per_day.size),
                     "loads": int(per_day.sum()), "loads_per_day": round(float(per_day.mean()), 1),
                     "max_day": int(per_day.max()), "asia_origin_pct": round(float(asia), 1)})
win = pd.DataFrame(win_rows)
inbound_loads_day = float(win["loads_per_day"].mean())
inbound_max_day = float(win["max_day"].max())
inbound_peakf = inbound_max_day / inbound_loads_day
asia_pct = float(win["asia_origin_pct"].mean())

# ---------------------------------------------- inbound arrival pattern (A018/A019)
INBOUND_ARRIVALS_DAY = 2          # teacher / DHL: 2 inbound shipments per day from Assa Abloy factories
CONTAINERS_AVG = 1                # ~41% of loads are Asian-origin (sea containers) -> ~1 of the 2 arrivals
CONTAINERS_PEAK = 2               # worst case: both arrivals are loose-loaded containers
DESTUFF_CREW, DESTUFF_H = 2, 3.0  # 2-person crew, 3 h per loose 40' container (A019; source S005: 1-2 h unload only)
loose_loads_share = asia_pct / 100

# ------------------------------------------------- BENCHMARK productivities (A014)
PROD = {   # process: (unit, rate per person-hour, driver avg/day, peak factor)
    "Receiving - palletised (unload+check)": ("pallets", 25, inbound_loads_day * (1 - loose_loads_share), inbound_peakf),
    "Receiving - loose container de-stuff":  ("person-h", None, CONTAINERS_AVG * DESTUFF_CREW * DESTUFF_H, CONTAINERS_PEAK / CONTAINERS_AVG),
    "Putaway (reach truck)":                 ("pallets", 20, inbound_loads_day, inbound_peakf),
    "Replenishment (reach truck)":           ("pallets", 18, replen_pallets_day, units_peakf),
    "Each picking":                          ("lines",   55, lines_each, lines_peakf),
    "Case picking":                          ("lines",   80, lines_case, lines_peakf),
    "Full-pallet picking":                   ("pallets", 22, lines_pallet, lines_peakf),
    "Packing / consolidation":               ("lines",   45, lines_each + lines_case, lines_peakf),
    "Shipping / loading":                    ("pallets", 30, outbound_pallets_day, units_peakf),
}
NET_H = 7.5   # productive hours per FTE per shift (A015)

rows = []
for fn, (unit, rate, drv_avg, pf) in PROD.items():
    drv_peak = drv_avg * pf
    h_avg = drv_avg if rate is None else drv_avg / rate
    h_peak = drv_peak if rate is None else drv_peak / rate
    rows.append({"Process": fn, "Driver/day (avg)": round(drv_avg, 1), "Unit": unit,
                 "Rate/h": "-" if rate is None else rate, "Peak factor": round(pf, 2),
                 "Hours (avg)": round(h_avg, 1), "Hours (peak)": round(h_peak, 1),
                 "FTE avg": round(h_avg / NET_H, 2), "FTE peak": round(h_peak / NET_H, 2),
                 "FTE (ceil peak)": int(np.ceil(h_peak / NET_H))})
plan = pd.DataFrame(rows).set_index("Process")
save_table(plan, "capacity_plan_labour.csv")
save_table(win.set_index("snapshot"), "inbound_receipts_windows.csv")

metrics = {
    "measured": {
        "inbound_loads_day": round(inbound_loads_day, 1),
        "inbound_max_day": round(inbound_max_day, 0),
        "inbound_peak_factor": round(inbound_peakf, 2),
        "inbound_asia_origin_pct": round(asia_pct, 1),
        "outbound_pallets_day": round(outbound_pallets_day, 1),
        "outbound_pallets_p90": round(float(pal_by_day.quantile(.9)), 0),
        "outbound_pallets_max": round(float(pal_by_day.max()), 0),
        "outbound_cartons_day": round(outbound_cartons_day, 1),
        "replen_pallets_day": round(replen_pallets_day, 1),
        "lines_each_day": round(lines_each, 0), "lines_case_day": round(lines_case, 0),
        "lines_pallet_day": round(lines_pallet, 1),
    },
    "inbound_windows": win_rows,
    "inbound_pattern": {"arrivals_per_day": INBOUND_ARRIVALS_DAY, "containers_avg": CONTAINERS_AVG,
                        "containers_peak": CONTAINERS_PEAK, "destuff_crew": DESTUFF_CREW, "destuff_h": DESTUFF_H},
    "pick_type_order_derived": {"share_lines_pct": share_lines, "share_units_pct": share_units,
                                "lines_without_master": n_no_master},
    "assumptions_productivity": {k: {"unit": v[0], "rate_per_h": v[1]} for k, v in PROD.items()},
    "net_hours_per_fte": NET_H,
    "total_fte_avg": round(float(plan["FTE avg"].sum()), 1),
    "total_fte_peak": round(float(plan["FTE peak"].sum()), 1),
    "total_fte_ceil_peak": int(plan["FTE (ceil peak)"].sum()),
    "labour_table": plan.reset_index().to_dict("records"),
}
# -------------------- storage feasibility at the CORRECTED target (A004/A010) --------------------
peak_positions = max(s_["occupied_locations"] for s_ in M["inventory"]["snapshots"])   # 8,512
target_positions = int(round(peak_positions / 0.90 / 500.0) * 500)                       # ~9,500
NON_STORAGE = 0.35                                                                       # share of total area (capacity.py model)
feas = []
for c in M["capacity"]["concepts"]:
    total = c["m2_per_position"] * target_positions / (1 - NON_STORAGE)
    feas.append({"Concept": c["concept"].split(" (")[0], "MHE": c["mhe"], "Levels": c["levels"],
                 "Total area m2": int(round(total, -1)), "% of 7,000 m2": round(total / 7000 * 100, 0),
                 "Fits": "YES" if total <= 7000 * 0.85 else ("TIGHT" if total <= 7000 else "NO")})
feas_df = pd.DataFrame(feas).set_index("Concept")
save_table(feas_df, "capacity_concepts_corrected.csv")
metrics["storage_basis"] = {"peak_occupied_locations": int(peak_positions), "target_positions": target_positions,
                            "peak_loads": int(max(s_["loads_LODNUM"] for s_ in M["inventory"]["snapshots"])),
                            "old_target_retired": M["capacity"]["design_positions_target"]}
metrics["feasibility_corrected"] = feas_df.reset_index().to_dict("records")

update_metrics("capacity_plan", metrics)

# figure: feasibility at corrected target
fig, ax = plt.subplots(figsize=(8.0, 3.6))
yy = np.arange(len(feas_df))[::-1]
cols = ["#D40511" if n.startswith("Double") else "#9aa7bd" for n in feas_df.index]
ax.barh(yy, feas_df["% of 7,000 m2"], color=cols, height=0.6, zorder=3)
ax.axvline(100, color="#262626", ls="--", lw=1.3)
ax.text(100, len(feas_df) - 0.35, "7,000 m² envelope", ha="center", fontsize=8.5, weight="bold")
for y_, v in zip(yy, feas_df["% of 7,000 m2"]):
    ax.text(v + 1.5, y_, f"{v:.0f}%", va="center", fontsize=9, weight="bold")
ax.set_yticks(yy); ax.set_yticklabels(feas_df.index, fontsize=9)
ax.set_xlim(0, 125); ax.grid(axis="x"); ax.grid(axis="y", visible=False)
ax.set_xlabel(f"% of the 7,000 m² envelope (target ~{target_positions:,} positions, incl. 35% working areas)")
ax.set_title("Floor area needed at the corrected position target")
save_fig(fig, "capacity_feasibility_corrected.png")

# figure: order-derived pick type (lines vs units)
fig, ax = plt.subplots(figsize=(7.6, 3.0))
cats = ["each", "case", "full pallet"]
x = np.arange(len(cats)); w = 0.38
lv = [share_lines.get(c, 0) for c in cats]; uv = [share_units.get(c, 0) for c in cats]
ax.bar(x - w / 2, lv, w, color="#D40511", label="% of order lines", zorder=3)
ax.bar(x + w / 2, uv, w, color="#FFCC00", label="% of units", zorder=3)
for i in range(len(cats)):
    ax.text(x[i] - w / 2, lv[i] + 1.5, f"{lv[i]:.0f}%", ha="center", fontsize=9, weight="bold")
    ax.text(x[i] + w / 2, uv[i] + 1.5, f"{uv[i]:.0f}%", ha="center", fontsize=9, weight="bold")
ax.set_xticks(x); ax.set_xticklabels(["Each (below one case)", "Case (≥ case qty)", "Full pallet (≥ pallet qty)"])
ax.set_ylim(0, 90); ax.set_ylabel("%"); ax.legend(frameon=False)
ax.set_title("Pick type derived from what customers ordered (line qty vs case / pallet qty)")
save_fig(fig, "order_pick_type_derived.png")

# ------------------------------------------------------------------ figure
fig, ax = plt.subplots(figsize=(8.6, 4.4))
y = np.arange(len(plan))
ax.barh(y - 0.2, plan["FTE avg"], height=0.4, label="Average day", color="#FFCC00")
ax.barh(y + 0.2, plan["FTE peak"], height=0.4, label="Peak day", color="#D40511")
ax.set_yticks(y); ax.set_yticklabels(plan.index, fontsize=8.5)
ax.invert_yaxis(); ax.grid(axis="x"); ax.grid(axis="y", visible=False)
ax.set_xlabel("FTE (7.5 productive h per shift)")
ax.set_title("Labour requirement by process — Option B")
ax.legend(loc="lower right")
save_fig(fig, "capacity_plan_fte.png")

print(f"PICK TYPE (order-derived, % lines): {share_lines} | % units: {share_units}")
print(f"INBOUND {inbound_loads_day:.1f} loads/day (max {inbound_max_day:.0f}, x{inbound_peakf:.2f}), Asia-origin {asia_pct:.0f}%")
print(f"OUTBOUND {outbound_pallets_day:.1f} pallets/day + {outbound_cartons_day:.0f} cartons/day | replen {replen_pallets_day:.1f} pallets/day")
print(plan[["Driver/day (avg)", "Rate/h", "Hours (peak)", "FTE avg", "FTE peak"]].to_string())
print(f"TOTAL FTE avg {plan['FTE avg'].sum():.1f}  peak {plan['FTE peak'].sum():.1f}")
