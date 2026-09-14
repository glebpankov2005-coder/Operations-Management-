"""
PEAK-AWARE SLOTTING analysis (applies Gadeyne, 'How to slot a warehouse during
peak season', LinkedIn). During peak, congestion - not walk distance - dominates.
This quantifies how concentrated our picks are and sizes the mitigations:
spread fast movers across zones + duplicate the extreme SKUs (multiple pick faces).
"""
import pandas as pd
from load_data import combined_outbound
from _util import save_table, update_metrics

ob = combined_outbound()
ob["DATE"] = pd.to_datetime(ob["DATE"], errors="coerce")
PEAK_DAY = "2025-05-27"

# picks (order lines) per SKU: whole quarter and on the peak day
g = ob.groupby("PRTNUM").size().sort_values(ascending=False).rename("picks_q2")
pk = ob[ob["DATE"].dt.date.astype(str) == PEAK_DAY].groupby("PRTNUM").size().rename("picks_peakday")
df = pd.concat([g, pk], axis=1).fillna(0).sort_values("picks_q2", ascending=False)
n = len(df)
tot = df["picks_q2"].sum()

def top_share(k_pct):
    k = max(1, int(n * k_pct / 100))
    return round(df["picks_q2"].iloc[:k].sum() / tot * 100, 1)

conc = {f"top_{p}pct_SKUs_share_of_picks": top_share(p) for p in [0.5, 1, 2, 5, 10]}

# "extreme" SKUs = top 1% by pick frequency -> candidates for duplicate pick faces
k1 = max(1, int(n * 0.01))
extreme = df.head(k1).copy()
extreme_share = round(extreme["picks_q2"].sum() / tot * 100, 1)

# congestion proxy: if ALL A-class picks sit in ONE zone vs balanced across 3 zones
# A-class from abc: top ~13% SKUs = ~80% of volume; here use picks.
A_k = int(n * 0.13)
A_picks = df["picks_q2"].iloc[:A_k].sum()
peak_day_lines = int(df["picks_peakday"].sum())
# assume 3 pick zones; clustered = all A in zone 1; balanced = A spread evenly
clustered_share = round(A_picks / tot * 100, 1)
balanced_per_zone = round(A_picks / 3 / tot * 100, 1)

save_table(extreme.reset_index().rename(columns={"index": "PRTNUM"}).head(30), "peak_slotting_extreme_skus.csv")

metrics = {
    "peak_day": PEAK_DAY,
    "peak_day_lines": peak_day_lines,
    "pick_concentration": conc,
    "extreme_top1pct_skus": int(k1),
    "extreme_top1pct_share_picks": extreme_share,
    "A_class_share_picks": clustered_share,
    "A_class_share_if_spread_3_zones": balanced_per_zone,
    "duplicate_face_candidates": extreme.index.tolist()[:15],
}
update_metrics("peak_slotting", metrics)

print(f"SKUs shipped: {n:,} | peak-day ({PEAK_DAY}) lines: {peak_day_lines:,}")
print("Pick concentration:", conc)
print(f"Extreme (top 1% = {k1} SKUs) do {extreme_share}% of all picks -> duplicate these across zones")
print(f"A-class picks = {clustered_share}% of total; if clustered in ONE zone that zone carries {clustered_share}% of picks,")
print(f"  vs {balanced_per_zone}% per zone if A is spread across 3 zones (congestion cut ~3x).")
print("Top duplicate-face candidates:", extreme.index.tolist()[:10])
