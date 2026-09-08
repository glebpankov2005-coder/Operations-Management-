"""
PHASE 1 - ORDER & PICKING PROFILE + DELIVERY LEAD TIME.
From combined outbound: orders/day, lines/order, units/line, pick-method mix,
full-pallet vs case vs each split, order-type & carrier mix, delivery lead time.
Writes tables + metrics + figures.
"""
import numpy as np
import pandas as pd
from load_data import combined_outbound
from _util import save_table, save_fig, update_metrics
import matplotlib.pyplot as plt

ob = combined_outbound()
for c in ["PICKED QTY", "PALL FLAG", "LIST FLAG", "TROLLEY FLAG",
          "PALL LIFTS", "LIST LIFTS", "TROLLEY LIFTS"]:
    ob[c] = pd.to_numeric(ob[c], errors="coerce")
for c in ["ORDER ARRIVE DATE", "PICK DATE", "STAGED DATE", "TRAILER DISPATCED DATE", "DATE"]:
    ob[c] = pd.to_datetime(ob[c], errors="coerce")

n_lines = len(ob)
n_orders = ob["ORDER NO"].nunique()

# ---- lines per order / units per line / units per order ----
lpo = ob.groupby("ORDER NO").size()
upl = ob["PICKED QTY"]
upo = ob.groupby("ORDER NO")["PICKED QTY"].sum()

# ---- pick-method mix (by lines & by lifts) ----
method_lines = {
    "pallet": int((ob["PALL FLAG"] == 1).sum()),
    "list_case": int((ob["LIST FLAG"] == 1).sum()),
    "trolley_each": int((ob["TROLLEY FLAG"] == 1).sum()),
}
method_lifts = {
    "pallet": int(ob["PALL LIFTS"].sum()),
    "list_case": int(ob["LIST LIFTS"].sum()),
    "trolley_each": int(ob["TROLLEY LIFTS"].sum()),
}

# ---- full-pallet vs case vs each classification of a line ----
def classify(row):
    if row["PALL FLAG"] == 1:
        return "full_pallet"
    if row["TROLLEY FLAG"] == 1:
        return "each"
    if row["LIST FLAG"] == 1:
        return "case_or_list"
    return "other"
ob["PICK_CLASS"] = ob.apply(classify, axis=1)
pick_class = ob["PICK_CLASS"].value_counts().to_dict()

# ---- delivery lead time: order arrive -> dispatched (brief: received -> sent) ----
lt_disp = (ob["TRAILER DISPATCED DATE"] - ob["ORDER ARRIVE DATE"]).dt.total_seconds() / 3600
lt_disp = lt_disp[(lt_disp >= 0) & (lt_disp < 24 * 30)]
lt_pick = (ob["PICK DATE"] - ob["ORDER ARRIVE DATE"]).dt.total_seconds() / 3600
lt_pick = lt_pick[(lt_pick >= 0) & (lt_pick < 24 * 30)]

# ---- order type & carrier mix ----
otype = ob["ORDER TYPE"].value_counts().head(10).to_dict()
carrier = ob["CARRIER NAME"].value_counts().head(10).to_dict()
country = ob["SHIP TO COUNTRY"].value_counts().head(10).to_dict()

# lines/order table
lpo_tab = pd.DataFrame({
    "metric": ["lines_per_order", "units_per_line", "units_per_order"],
    "mean": [lpo.mean(), upl.mean(), upo.mean()],
    "median": [lpo.median(), upl.median(), upo.median()],
    "p95": [lpo.quantile(.95), upl.quantile(.95), upo.quantile(.95)],
    "max": [lpo.max(), upl.max(), upo.max()],
}).set_index("metric")
save_table(lpo_tab.round(2), "order_profile.csv")

metrics = {
    "n_order_lines": int(n_lines),
    "n_orders": int(n_orders),
    "lines_per_order": {"mean": round(float(lpo.mean()), 2), "median": float(lpo.median()),
                         "p95": float(lpo.quantile(.95)), "max": int(lpo.max()),
                         "single_line_pct": round(float((lpo == 1).mean()) * 100, 1)},
    "units_per_line": {"mean": round(float(upl.mean()), 2), "median": float(upl.median()),
                        "p95": float(upl.quantile(.95)), "max": int(upl.max()),
                        "single_unit_pct": round(float((upl == 1).mean()) * 100, 1)},
    "units_per_order": {"mean": round(float(upo.mean()), 1), "median": float(upo.median()),
                         "p95": float(upo.quantile(.95)), "max": int(upo.max())},
    "pick_method_lines": method_lines,
    "pick_method_lifts": method_lifts,
    "pick_class_lines": pick_class,
    "pick_class_pct": {k: round(v / n_lines * 100, 1) for k, v in pick_class.items()},
    "delivery_leadtime_h_arrive_to_dispatch": {
        "median": round(float(lt_disp.median()), 1), "mean": round(float(lt_disp.mean()), 1),
        "p90": round(float(lt_disp.quantile(.90)), 1), "n": int(lt_disp.notna().sum())},
    "leadtime_h_arrive_to_pick": {
        "median": round(float(lt_pick.median()), 1), "p90": round(float(lt_pick.quantile(.90)), 1)},
    "order_type_mix": otype,
    "carrier_mix": carrier,
    "country_mix": country,
}
update_metrics("orders", metrics)

# figure: pick class split
fig, ax = plt.subplots(figsize=(6, 4))
k = list(pick_class.keys()); v = list(pick_class.values())
ax.bar(k, v, color="#6c8eef")
ax.set_title("Order lines by pick type"); ax.set_ylabel("order lines")
for i, val in enumerate(v):
    ax.text(i, val, f"{val:,}\n{val/n_lines*100:.0f}%", ha="center", va="bottom", fontsize=9)
save_fig(fig, "order_pick_class.png")

print(f"Orders={n_orders:,} lines={n_lines:,}")
print(f"Lines/order mean={lpo.mean():.2f} median={lpo.median():.0f} p95={lpo.quantile(.95):.0f} "
      f"single-line={metrics['lines_per_order']['single_line_pct']}%")
print(f"Units/line mean={upl.mean():.2f} single-unit={metrics['units_per_line']['single_unit_pct']}% "
      f"p95={upl.quantile(.95):.0f} max={upl.max():.0f}")
print(f"Pick class %: {metrics['pick_class_pct']}")
print(f"Pick lifts: {method_lifts}")
print(f"Delivery lead time (arrive->dispatch) median={lt_disp.median():.1f}h p90={lt_disp.quantile(.90):.1f}h")
print(f"Order types: {list(otype.items())[:5]}")
print(f"Top countries: {list(country.items())[:5]}")
