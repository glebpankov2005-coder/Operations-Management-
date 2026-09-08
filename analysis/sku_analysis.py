"""
PHASE 1 - SKU PROFILE.
Builds a SKU master from the latest storage snapshot: dimensions, weight, cube,
units/cases per pallet, pallet type, family, WMS ABC. One row per PART.
Writes outputs/tables/sku_master.csv + summary metrics.
"""
import numpy as np
import pandas as pd
from load_data import all_storage
from _util import save_table, save_fig, update_metrics
import matplotlib.pyplot as plt

storage = all_storage()
latest = sorted(storage.keys())[-1]
df = storage[latest].copy()

num = ["EA LEN", "EA WID", "EA HGT", "EA WGT", "CS QTY", "CS LEN", "CS WID", "CS HGT",
       "CS WGT", "PA QTY", "PA LEN", "PA WID", "PA HGT", "PA WGT", "QTY"]
for c in num:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# each & case & pallet cube in m3
df["EA_CUBE_M3"] = (df["EA LEN"] * df["EA WID"] * df["EA HGT"]) / 1e6
df["CS_CUBE_M3"] = (df["CS LEN"] * df["CS WID"] * df["CS HGT"]) / 1e6

# collapse to SKU (PART) level - take median of numeric attrs, mode of categoricals
def mode_first(s):
    s = s.dropna()
    return s.mode().iat[0] if len(s) else np.nan

agg = {
    "EA LEN": "median", "EA WID": "median", "EA HGT": "median", "EA WGT": "median",
    "EA_CUBE_M3": "median",
    "CS QTY": "median", "CS_CUBE_M3": "median", "CS WGT": "median",
    "PA QTY": "median", "PA WGT": "median", "PA LEN": "median", "PA HGT": "median",
}
sku = df.groupby("PART").agg(agg)
sku["PART FAMILY"] = df.groupby("PART")["PART FAMILY"].apply(mode_first)
sku["PART ABCCOD"] = df.groupby("PART")["PART ABCCOD"].apply(mode_first)
sku["ASSET TYPE"] = df.groupby("PART")["ASSET TYPE"].apply(mode_first)
sku["HAZMAT"] = df.groupby("PART")["HAZMAT"].apply(mode_first)
sku["cases_per_pallet"] = sku["PA QTY"] / sku["CS QTY"]

# storage-type hint by pallet quantity size (physical), not demand
sku["units_per_pallet"] = sku["PA QTY"]

save_table(sku.round(4), "sku_master.csv")

metrics = {
    "source_snapshot": latest,
    "n_skus": int(sku.shape[0]),
    "ea_cube_m3": {
        "median": round(float(sku["EA_CUBE_M3"].median()), 5),
        "mean": round(float(sku["EA_CUBE_M3"].mean()), 5),
        "p95": round(float(sku["EA_CUBE_M3"].quantile(0.95)), 5),
        "max": round(float(sku["EA_CUBE_M3"].max()), 5),
    },
    "ea_weight_kg": {
        "median": round(float(sku["EA WGT"].median()), 3),
        "mean": round(float(sku["EA WGT"].mean()), 3),
        "p95": round(float(sku["EA WGT"].quantile(0.95)), 3),
        "max": round(float(sku["EA WGT"].max()), 3),
    },
    "units_per_pallet": {
        "median": float(sku["PA QTY"].median()),
        "mean": round(float(sku["PA QTY"].mean()), 1),
        "p95": float(sku["PA QTY"].quantile(0.95)),
    },
    "pallet_weight_kg": {
        "median": round(float(sku["PA WGT"].median()), 1),
        "mean": round(float(sku["PA WGT"].mean()), 1),
        "p95": round(float(sku["PA WGT"].quantile(0.95)), 1),
        "max": round(float(sku["PA WGT"].max()), 1),
    },
    "wms_abc_counts": sku["PART ABCCOD"].value_counts().to_dict(),
    "asset_type_counts": sku["ASSET TYPE"].value_counts().head(8).to_dict(),
    "n_families": int(sku["PART FAMILY"].nunique()),
    "hazmat_skus": int((pd.to_numeric(sku["HAZMAT"], errors="coerce").fillna(0) > 0).sum()),
    "skus_with_case_pack": int(sku["CS QTY"].notna().sum()),
    "skus_each_only": int(sku["CS QTY"].isna().sum()),
}
update_metrics("sku", metrics)

# figure: pallet weight distribution
fig, ax = plt.subplots(figsize=(7, 4))
pw = sku["PA WGT"].dropna()
pw = pw[pw < pw.quantile(0.99)]
ax.hist(pw, bins=40, color="#6c8eef")
ax.set_title("Pallet weight distribution (SKU level, <p99)")
ax.set_xlabel("kg per pallet"); ax.set_ylabel("SKUs")
save_fig(fig, "sku_pallet_weight_hist.png")

print(f"SKU master: {metrics['n_skus']} SKUs | families={metrics['n_families']} | "
      f"case-pack SKUs={metrics['skus_with_case_pack']} each-only={metrics['skus_each_only']}")
print(f"Units/pallet median={metrics['units_per_pallet']['median']} mean={metrics['units_per_pallet']['mean']}")
print(f"Pallet wgt median={metrics['pallet_weight_kg']['median']}kg p95={metrics['pallet_weight_kg']['p95']}kg max={metrics['pallet_weight_kg']['max']}kg")
print(f"EA cube median={metrics['ea_cube_m3']['median']}m3 | WMS ABC={metrics['wms_abc_counts']}")
