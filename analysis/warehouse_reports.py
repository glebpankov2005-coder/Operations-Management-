"""
Warehouse report assets (in-house equivalent of the dvcrn 'warehouse-chart-reports'
skill) built from OUR real ASSA data - no third-party code. Produces report-ready
charts + a KPI summary. Revenue/profit charts are intentionally omitted (no cost
data, A006); we substitute inventory-by-family and demand-based views instead.
"""
import os, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from load_data import all_storage, combined_outbound
from _util import FIGS, REPORTS

KPI = os.path.join(os.path.dirname(__file__), "..", "outputs", "kpis")
os.makedirs(KPI, exist_ok=True)
M = json.load(open(os.path.join(REPORTS, "phase1_metrics.json"), encoding="utf-8"))
BLUE = "#6c8eef"; PALETTE = ["#6c8eef", "#8fa9f2", "#e08a5b", "#9ad0a0", "#f2a6a6", "#c9a9e0", "#f4c58a", "#7fc8c0"]

storage = all_storage()
latest = storage[sorted(storage)[-1]]
ob = combined_outbound()
ob["PICKED QTY"] = pd.to_numeric(ob["PICKED QTY"], errors="coerce")

# ---------- 1. STOCK AGEING (days in stock) - exposes slow/dead stock ----------
snap = pd.to_datetime(latest["DATE"], errors="coerce").max()
add = pd.to_datetime(latest["ADD DATE"], errors="coerce")
age_days = (snap - add).dt.days
load_age = pd.DataFrame({"LODNUM": latest["LODNUM"], "age": age_days}).dropna().drop_duplicates("LODNUM")
buckets = pd.cut(load_age["age"], [-1, 30, 90, 180, 365, 730, 99999],
                 labels=["0–30 d", "31–90 d", "91–180 d", "181–365 d", "1–2 yr", ">2 yr"])
ageing = load_age.groupby(buckets, observed=False).size()
fig, ax = plt.subplots(figsize=(8, 4.5))
colors = ["#9ad0a0", "#8fa9f2", "#6c8eef", "#f4c58a", "#e08a5b", "#d40011"]
bars = ax.bar(ageing.index.astype(str), ageing.values, color=colors)
ax.set_title("Stock ageing — stored loads by time in stock (slow/dead-stock view)", weight="bold", fontsize=11)
ax.set_ylabel("stored loads")
tot_loads = ageing.sum()
for b, v in zip(bars, ageing.values):
    ax.text(b.get_x()+b.get_width()/2, v, f"{v:,}\n{v/tot_loads*100:.0f}%", ha="center", va="bottom", fontsize=8)
over1yr = int(ageing.get("1–2 yr", 0) + ageing.get(">2 yr", 0))
ax.text(0.99, 0.95, f"{over1yr:,} loads ({over1yr/tot_loads*100:.0f}%) in stock >1 year",
        transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#d40011", style="italic")
fig.savefig(os.path.join(FIGS, "report_stock_ageing.png"), dpi=115, bbox_inches="tight"); plt.close(fig)

# ---------- 2. INVENTORY BY PRODUCT FAMILY (top 10 by pallet positions) ----------
fam = latest.groupby("PART FAMILY")["LODNUM"].nunique().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(fam.index.astype(str)[::-1], fam.values[::-1], color=BLUE)
ax.set_title("Inventory by product family — top 10 (pallet positions / loads)", weight="bold", fontsize=11)
ax.set_xlabel("stored loads")
for i, v in enumerate(fam.values[::-1]):
    ax.text(v, i, f" {v:,}", va="center", fontsize=8)
fig.savefig(os.path.join(FIGS, "report_inventory_by_family.png"), dpi=115, bbox_inches="tight"); plt.close(fig)

# ---------- 3. TOP-20 PRODUCTS TABLE (by demand) ----------
dem = ob.groupby("PRTNUM").agg(picks=("PICKED QTY", "size"), units=("PICKED QTY", "sum")).sort_values("picks", ascending=False).head(20)
attrs = latest.groupby("PART").agg(**{
    "family": ("PART FAMILY", lambda s: s.dropna().mode().iat[0] if s.notna().any() else ""),
    "abc": ("PART ABCCOD", lambda s: s.dropna().mode().iat[0] if s.notna().any() else ""),
    "loads": ("LODNUM", "nunique"),
})
tbl = dem.join(attrs)
tbl_disp = tbl.reset_index().rename(columns={"PRTNUM": "SKU"})
tbl_disp = tbl_disp[["SKU", "family", "abc", "picks", "units", "loads"]]
tbl_disp["units"] = tbl_disp["units"].map(lambda x: f"{int(x):,}")
tbl_disp["picks"] = tbl_disp["picks"].map(lambda x: f"{int(x):,}")
tbl_disp["loads"] = tbl_disp["loads"].fillna(0).map(lambda x: f"{int(x):,}")
tbl_disp.to_csv(os.path.join(os.path.dirname(__file__), "..", "outputs", "tables", "report_top20_products.csv"), index=False)

fig, ax = plt.subplots(figsize=(9, 6.5)); ax.axis("off")
ax.set_title("Top 20 SKUs by demand (picks) — Q2 2025", weight="bold", fontsize=12, pad=14)
t = ax.table(cellText=tbl_disp.values, colLabels=["SKU", "Family", "ABC", "Picks", "Units", "Loads in stock"],
             cellLoc="center", loc="center")
t.auto_set_font_size(False); t.set_fontsize(8.5); t.scale(1, 1.35)
for (r, c), cell in t.get_celld().items():
    if r == 0:
        cell.set_facecolor(BLUE); cell.set_text_props(color="white", weight="bold")
    elif r % 2 == 0:
        cell.set_facecolor("#eef2fb")
    cell.set_edgecolor("white")
fig.savefig(os.path.join(FIGS, "report_top20_products.png"), dpi=115, bbox_inches="tight"); plt.close(fig)

# ---------- 4. KPI SUMMARY (text) ----------
s, ii, o, a, p = M["sku"], M["inventory"], M["orders"], M["abc"], M["peak"]
lt = o["delivery_leadtime_h_arrive_to_dispatch"]
lines = [
    "ASSA ABLOY @ DHL BEMMEL (NL_0032) - WAREHOUSE KPI SUMMARY (Q2 2025)",
    "=" * 62,
    "INVENTORY",
    f"  Active SKUs .................. {s['n_skus']:,}   (families: {s['n_families']})",
    f"  Peak pallet positions ....... {ii['peak_loads_snapshot']:,}   (+{ii['loads_growth_pct_q2']}%/quarter)",
    f"  Single-load SKUs ............ {ii['single_load_skus_pct']}%   (slow tail)",
    f"  Total cube (avg) ............ {ii['avg_total_cube_m3']:,.0f} m3",
    "DEMAND / ORDERS",
    f"  Order lines (Q2) ............ {o['n_order_lines']:,}   over {p['operating_days']} days",
    f"  Orders (Q2) ................. {o['n_orders']:,}",
    f"  Lines/order (mean/median) ... {o['lines_per_order']['mean']} / {o['lines_per_order']['median']:.0f}   ({o['lines_per_order']['single_line_pct']}% single-line)",
    f"  Pick mix (lines) ............ case/list {o['pick_class_pct']['case_or_list']}% | each {o['pick_class_pct']['each']}% | pallet {o['pick_class_pct']['full_pallet']}%",
    f"  Delivery lead time .......... avg {lt['mean']}h / median {lt['median']}h",
    "THROUGHPUT (per day)",
    f"  Order lines ................. avg {p['lines']['mean']:.0f} | PEAK {p['lines']['peak']:.0f} ({p['lines']['peak_over_avg']}x, {p['lines']['peak_date']})",
    f"  Units ....................... avg {p['units']['mean']:.0f} | PEAK {p['units']['peak']:.0f} ({p['units']['peak_over_avg']}x)",
    "ABC (demand-based)",
    f"  A / B / C SKUs .............. {a['abc_vol_counts'].get('A',0):,} / {a['abc_vol_counts'].get('B',0):,} / {a['abc_vol_counts'].get('C',0):,}",
    f"  Top 5% SKUs = {a['pareto_actual']['top_5pct_skus_do_qty_pct']}% of volume; WMS-ABC agreement {a['agreement_with_wms_pct']}%",
]
with open(os.path.join(KPI, "kpi_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("\n".join(lines))
print("\n[written] report_stock_ageing.png, report_inventory_by_family.png, report_top20_products.png, kpis/kpi_summary.txt")
