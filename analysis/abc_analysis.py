"""
PHASE 1 - DEMAND-BASED ABC.
Recompute ABC from actual outbound demand (by picked volume AND by pick frequency).
Compute the ACTUAL Pareto distribution (not assumed 80/20). Compare to WMS PART ABCCOD.
Writes tables + Pareto figure + metrics.
"""
import numpy as np
import pandas as pd
from load_data import combined_outbound, all_storage
from _util import save_table, save_fig, update_metrics
import matplotlib.pyplot as plt

ob = combined_outbound()
ob["PICKED QTY"] = pd.to_numeric(ob["PICKED QTY"], errors="coerce")

g = ob.groupby("PRTNUM").agg(
    picked_qty=("PICKED QTY", "sum"),
    pick_lines=("PICKED QTY", "size"),
    orders=("ORDER NO", "nunique"),
).sort_values("picked_qty", ascending=False)

total_qty = g["picked_qty"].sum()
total_lines = g["pick_lines"].sum()
g["cum_qty_pct"] = g["picked_qty"].cumsum() / total_qty * 100
g["cum_sku_pct"] = np.arange(1, len(g) + 1) / len(g) * 100

def abc_by(col_cum):
    return np.where(col_cum <= 80, "A", np.where(col_cum <= 95, "B", "C"))
g["ABC_vol"] = abc_by(g["cum_qty_pct"])

# by pick frequency
gf = g.sort_values("pick_lines", ascending=False).copy()
gf["cum_line_pct"] = gf["pick_lines"].cumsum() / total_lines * 100
gf["ABC_freq"] = abc_by(gf["cum_line_pct"])
g = g.join(gf[["ABC_freq"]])

save_table(g.round(2), "abc_by_sku.csv")

# actual Pareto points
def share_of_top(pct_skus):
    n = max(1, int(len(g) * pct_skus / 100))
    return round(float(g["picked_qty"].iloc[:n].sum() / total_qty * 100), 1)

pareto = {f"top_{p}pct_skus_do_qty_pct": share_of_top(p) for p in [5, 10, 20, 30, 50]}

# class summaries
def summ(col):
    s = g.groupby(col).agg(skus=("picked_qty", "size"),
                           qty=("picked_qty", "sum"),
                           lines=("pick_lines", "sum"))
    s["sku_pct"] = (s["skus"] / s["skus"].sum() * 100).round(1)
    s["qty_pct"] = (s["qty"] / s["qty"].sum() * 100).round(1)
    s["line_pct"] = (s["lines"] / s["lines"].sum() * 100).round(1)
    return s
vol_sum = summ("ABC_vol")
save_table(vol_sum, "abc_class_summary_volume.csv")

# compare to WMS ABC (from latest storage)
storage = all_storage()
latest = storage[sorted(storage)[-1]]
wms = latest.groupby("PART")["PART ABCCOD"].agg(lambda s: s.dropna().mode().iat[0] if s.notna().any() else np.nan)
cmp = g.join(wms.rename("WMS_ABC"))
cross = pd.crosstab(cmp["ABC_vol"], cmp["WMS_ABC"])
save_table(cross, "abc_vs_wms_crosstab.csv")
agree = float((cmp["ABC_vol"] == cmp["WMS_ABC"]).mean()) * 100

metrics = {
    "n_skus_shipped": int(len(g)),
    "pareto_actual": pareto,
    "class_summary_volume": vol_sum.reset_index().to_dict("records"),
    "abc_vol_counts": g["ABC_vol"].value_counts().to_dict(),
    "abc_freq_counts": g["ABC_freq"].value_counts().to_dict(),
    "agreement_with_wms_pct": round(agree, 1),
    "skus_shipped_not_in_stock": int(cmp["WMS_ABC"].isna().sum()),
}
update_metrics("abc", metrics)

# Pareto figure
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(g["cum_sku_pct"].values, g["cum_qty_pct"].values, color="#6c8eef")
ax.axhline(80, color="#e08a5b", ls="--", lw=1); ax.axvline(20, color="#999", ls=":", lw=1)
ax.set_title("Demand Pareto - cumulative picked qty vs SKUs")
ax.set_xlabel("% of SKUs (ranked)"); ax.set_ylabel("% of picked quantity")
ax.grid(alpha=0.3)
save_fig(fig, "abc_pareto.png")

print(f"SKUs shipped: {len(g):,}")
print(f"Actual Pareto: {pareto}")
print("Class summary (by volume):"); print(vol_sum.to_string())
print(f"ABC(vol) counts={metrics['abc_vol_counts']} | agreement with WMS ABC={agree:.1f}%")
print(f"SKUs shipped but not in latest stock: {metrics['skus_shipped_not_in_stock']}")
