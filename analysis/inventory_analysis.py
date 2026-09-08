"""
PHASE 1 - INVENTORY & PALLET/POSITION REQUIREMENT.
Across the 3 snapshots: total on-hand, loads (LODNUM), occupied locations, cube.
Per-SKU inventory avg/min/max/variability. Pallet positions required (A004: 1 load = 1 pos).
Writes outputs/tables/inventory_by_sku.csv + metrics + trend figure.
"""
import numpy as np
import pandas as pd
from load_data import all_storage
from _util import save_table, save_fig, update_metrics
import matplotlib.pyplot as plt

storage = all_storage()
snaps = sorted(storage.keys())

# ---- per-snapshot totals ----
rows = []
for fn in snaps:
    d = storage[fn].copy()
    d["QTY"] = pd.to_numeric(d["QTY"], errors="coerce")
    d["EA_CUBE_M3"] = (pd.to_numeric(d["EA LEN"], errors="coerce") *
                        pd.to_numeric(d["EA WID"], errors="coerce") *
                        pd.to_numeric(d["EA HGT"], errors="coerce")) / 1e6
    d["LINE_CUBE_M3"] = d["QTY"] * d["EA_CUBE_M3"]
    snap = pd.to_datetime(d["DATE"], errors="coerce").dt.date.mode().iat[0]
    rack = d[d["LOC TYPE"] == "RACK"]
    rows.append({
        "snapshot": str(snap),
        "detail_records": len(d),
        "loads_LODNUM": int(d["LODNUM"].nunique()),
        "occupied_locations": int(d["LOCATION"].nunique()),
        "active_skus": int(d["PART"].nunique()),
        "total_eaches": int(d["QTY"].sum()),
        "total_cube_m3": round(float(d["LINE_CUBE_M3"].sum()), 1),
        "rack_loads": int(rack["LODNUM"].nunique()),
        "rack_locations": int(rack["LOCATION"].nunique()),
    })
trend = pd.DataFrame(rows).set_index("snapshot")
save_table(trend, "inventory_trend.csv")

# ---- per-SKU inventory across snapshots ----
per = []
for fn in snaps:
    d = storage[fn].copy()
    d["QTY"] = pd.to_numeric(d["QTY"], errors="coerce")
    g = d.groupby("PART").agg(qty=("QTY", "sum"),
                              loads=("LODNUM", "nunique"),
                              locs=("LOCATION", "nunique"))
    g["snapshot"] = fn
    per.append(g.reset_index())
allsku = pd.concat(per, ignore_index=True)

inv = allsku.groupby("PART").agg(
    avg_qty=("qty", "mean"), min_qty=("qty", "min"), max_qty=("qty", "max"),
    avg_loads=("loads", "mean"), max_loads=("loads", "max"),
    avg_locs=("locs", "mean"), max_locs=("locs", "max"),
)
inv["qty_cv"] = allsku.groupby("PART")["qty"].std().div(inv["avg_qty"]).replace([np.inf, -np.inf], np.nan)
save_table(inv.round(3), "inventory_by_sku.csv")

# positions required: use max loads per SKU (peak), summed
peak_positions_by_sku = inv["max_loads"].sum()
avg_positions = trend["loads_LODNUM"].mean()
peak_positions_snapshot = trend["loads_LODNUM"].max()

metrics = {
    "snapshots": trend.reset_index().to_dict("records"),
    "loads_growth_pct_q2": round(float((trend["loads_LODNUM"].iloc[-1] /
                                        trend["loads_LODNUM"].iloc[0] - 1) * 100), 1),
    "avg_loads_per_snapshot": round(float(avg_positions), 0),
    "peak_loads_snapshot": int(peak_positions_snapshot),
    "sum_peak_loads_by_sku": int(peak_positions_by_sku),
    "avg_total_cube_m3": round(float(trend["total_cube_m3"].mean()), 1),
    "loads_per_sku": {
        "mean": round(float(inv["avg_loads"].mean()), 2),
        "median": float(inv["avg_loads"].median()),
        "p95": round(float(inv["avg_loads"].quantile(0.95)), 1),
        "max": float(inv["max_loads"].max()),
    },
    "single_load_skus_pct": round(float((inv["max_loads"] <= 1).mean()) * 100, 1),
}
update_metrics("inventory", metrics)

# figure: loads & locations trend
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(trend.index, trend["loads_LODNUM"], "o-", label="Loads (pallet positions)", color="#6c8eef")
ax.plot(trend.index, trend["occupied_locations"], "s-", label="Occupied locations", color="#e08a5b")
ax.set_title("Inventory footprint trend (Q2 2025)")
ax.set_ylabel("count"); ax.legend(); ax.grid(alpha=0.3)
save_fig(fig, "inventory_trend.png")

print(trend.to_string())
print(f"\nLoads growth Q2: {metrics['loads_growth_pct_q2']}% | peak loads(snapshot)={peak_positions_snapshot:,} | "
      f"sum of per-SKU peak loads={peak_positions_by_sku:,}")
print(f"Loads/SKU mean={metrics['loads_per_sku']['mean']} median={metrics['loads_per_sku']['median']} "
      f"max={metrics['loads_per_sku']['max']} | single-load SKUs={metrics['single_load_skus_pct']}%")
