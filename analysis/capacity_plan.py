"""
PHASE 5 - CAPACITY PLAN (labour + MHE) for the recommended Option B.
Workload drivers are MEASURED from the data; productivities are documented
BENCHMARK assumptions (A014+, to validate with DHL). Computes FTE and MHE per
process at AVERAGE and PEAK day.
"""
import numpy as np
import pandas as pd
from load_data import combined_outbound
from _util import save_table, save_fig, update_metrics
import matplotlib.pyplot as plt
import json, os

M = json.load(open(os.path.join(os.path.dirname(__file__), "..", "outputs", "reports", "phase1_metrics.json"), encoding="utf-8"))
peakf = M["peak"]["lines"]["peak_over_avg"]        # 1.83 lines peak factor
units_peakf = M["peak"]["units"]["peak_over_avg"]  # 2.85 units peak factor
lines_avg = M["peak"]["lines"]["mean"]             # 640
units_avg = M["peak"]["units"]["mean"]             # 22,269
pick_pct = M["orders"]["pick_class_pct"]           # case_or_list/each/full_pallet/other %
upp = M["sku"]["units_per_pallet"]["median"]       # 1000 units/pallet (forward replen driver)

# ---- outbound pallets/day (MEASURED: dedupe shipments) ----
ob = combined_outbound()
ob["DATE"] = pd.to_datetime(ob["DATE"], errors="coerce")
ship = ob.drop_duplicates("SHIPMENT ID")
ship_pallets = pd.to_numeric(ship["SHIPMENT PACKED PALLETS"], errors="coerce").fillna(0)
n_days = ob["DATE"].dt.date.nunique()
outbound_pallets_day = float(ship_pallets.sum() / n_days)

# net inventory growth (loads/day) from snapshots
snaps = M["inventory"]["snapshots"]
net_growth_day = (snaps[-1]["loads_LODNUM"] - snaps[0]["loads_LODNUM"]) / (2 * 30.0)  # ~2 months

# ---- daily workload drivers ----
lines_case = lines_avg * (pick_pct["case_or_list"] + pick_pct["other"]) / 100.0  # treat 'other' as case
lines_each = lines_avg * pick_pct["each"] / 100.0
lines_pallet = lines_avg * pick_pct["full_pallet"] / 100.0
replen_pallets_day = units_avg / upp                       # forward-pick replen
inbound_pallets_day = outbound_pallets_day + net_growth_day

# ---- BENCHMARK productivities (units/person-hour) - ASSUMPTIONS A014 ----
PROD = {
    "Receiving (unload+check)": ("pallets", 25, inbound_pallets_day),
    "Putaway (reach)":          ("pallets", 20, inbound_pallets_day),
    "Replenishment":            ("pallets", 18, replen_pallets_day),
    "Case picking":             ("lines",   80, lines_case),
    "Each picking":             ("lines",   55, lines_each),
    "Full-pallet picking":      ("pallets", 22, lines_pallet),
    "Packing/consolidation":    ("lines",   45, lines_case + lines_each),
    "Shipping/loading":         ("pallets", 30, outbound_pallets_day),
}
PROD_PEAK_DRIVER = {  # which peak factor scales each driver
    "Receiving (unload+check)": units_peakf, "Putaway (reach)": units_peakf,
    "Replenishment": units_peakf, "Case picking": peakf, "Each picking": peakf,
    "Full-pallet picking": peakf, "Packing/consolidation": peakf, "Shipping/loading": units_peakf,
}
NET_H = 7.5          # productive hours per FTE per shift (from 8h incl PF&D/breaks)
MHE_UTIL = 0.80      # equipment availability/utilisation

rows = []
tot_fte_avg = tot_fte_peak = 0
for fn, (unit, rate, drv_avg) in PROD.items():
    drv_peak = drv_avg * PROD_PEAK_DRIVER[fn]
    h_avg, h_peak = drv_avg / rate, drv_peak / rate
    fte_avg, fte_peak = h_avg / NET_H, h_peak / NET_H
    tot_fte_avg += fte_avg; tot_fte_peak += fte_peak
    rows.append({
        "Process": fn, "Driver/day (avg)": round(drv_avg, 0), "Unit": unit,
        "Rate/h": rate, "Hours (avg)": round(h_avg, 1), "Hours (peak)": round(h_peak, 1),
        "FTE avg": round(fte_avg, 2), "FTE peak": round(fte_peak, 2),
        "FTE (ceil peak)": int(np.ceil(fte_peak)),
    })
plan = pd.DataFrame(rows).set_index("Process")
save_table(plan, "capacity_plan_labour.csv")

# ---- MHE from equipment-hours ----
def eq_hours(procs): return sum(plan.loc[p, "Hours (peak)"] for p in procs)
mhe = {
    "Reach truck (putaway/replen/pallet pick)": ["Putaway (reach)", "Replenishment", "Full-pallet picking"],
    "Low-level order picker (case/each)":        ["Case picking", "Each picking"],
    "Pallet truck (receiving/shipping)":         ["Receiving (unload+check)", "Shipping/loading"],
}
mhe_rows = []
for m, procs in mhe.items():
    h = eq_hours(procs)
    units_needed = int(np.ceil(h / (NET_H * MHE_UTIL)))
    mhe_rows.append({"Equipment": m, "Peak equip-hours/day": round(h, 1), "Units (peak)": max(1, units_needed)})
mhe_df = pd.DataFrame(mhe_rows).set_index("Equipment")
save_table(mhe_df, "capacity_plan_mhe.csv")

metrics = {
    "measured": {
        "outbound_pallets_day": round(outbound_pallets_day, 1),
        "inbound_pallets_day": round(inbound_pallets_day, 1),
        "net_growth_loads_day": round(net_growth_day, 1),
        "replen_pallets_day": round(replen_pallets_day, 1),
        "lines_case_day": round(lines_case, 0), "lines_each_day": round(lines_each, 0),
    },
    "assumptions_productivity": {k: {"unit": v[0], "rate_per_h": v[1]} for k, v in PROD.items()},
    "net_hours_per_fte": NET_H, "mhe_util": MHE_UTIL,
    "total_fte_avg": round(tot_fte_avg, 1), "total_fte_peak": round(tot_fte_peak, 1),
    "total_fte_ceil_peak": int(plan["FTE (ceil peak)"].sum()),
    "labour_table": plan.reset_index().to_dict("records"),
    "mhe_table": mhe_df.reset_index().to_dict("records"),
}
update_metrics("capacity_plan", metrics)

# figure: FTE by process avg vs peak
fig, ax = plt.subplots(figsize=(8, 4))
y = np.arange(len(plan))
ax.barh(y - 0.2, plan["FTE avg"], height=0.4, label="avg", color="#8fa9f2")
ax.barh(y + 0.2, plan["FTE peak"], height=0.4, label="peak", color="#6c8eef")
ax.set_yticks(y); ax.set_yticklabels(plan.index, fontsize=8)
ax.set_xlabel("FTE"); ax.set_title("Labour requirement by process (Option B)"); ax.legend()
save_fig(fig, "capacity_plan_fte.png")

print(f"MEASURED: outbound {outbound_pallets_day:.1f} pallets/day, inbound ~{inbound_pallets_day:.1f}, "
      f"replen {replen_pallets_day:.1f}, net growth {net_growth_day:.1f} loads/day")
print(plan.to_string())
print(f"\nTOTAL FTE  avg={tot_fte_avg:.1f}  peak={tot_fte_peak:.1f}  (sum of per-process ceil peak = {int(plan['FTE (ceil peak)'].sum())})")
print("\nMHE:"); print(mhe_df.to_string())
