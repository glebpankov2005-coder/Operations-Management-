"""Extra Phase 1 extremes requested: max pallets in stock, longest SKU, biggest order."""
import pandas as pd
from load_data import all_storage, combined_outbound

st = all_storage()
print("=== MAX PALLETS IN STOCK ===")
for fn, d in st.items():
    print(f"  {fn[:30]}: total loads (LODNUM) = {d['LODNUM'].nunique():,}")
latest = st[sorted(st)[-1]]
print("  -> PEAK total pallets in warehouse (June snapshot):", f"{latest['LODNUM'].nunique():,}")
loads_by_sku = latest.groupby("PART")["LODNUM"].nunique().sort_values(ascending=False)
print("  Single SKU holding most pallets:", loads_by_sku.index[0], "=", int(loads_by_sku.iloc[0]), "loads")
print("  top 5 SKUs by pallets:", [(k, int(v)) for k, v in loads_by_sku.head().items()])

print("\n=== LONGEST SKU ===")
for col in ["EA LEN", "PA LEN", "CS LEN"]:
    s = pd.to_numeric(latest[col], errors="coerce")
    i = s.idxmax()
    print(f"  max {col} = {s.max():.1f} cm  (PART {latest.loc[i,'PART']}, family {latest.loc[i,'PART FAMILY']}, asset {latest.loc[i,'ASSET TYPE']})")
ea = pd.to_numeric(latest["EA LEN"], errors="coerce")
print("  SKUs with each-length > 120 cm:", int((ea > 120).sum()), "| > 240 cm:", int((ea > 240).sum()))
top_ea = ea.sort_values(ascending=False).head()
print("  top 5 EA LEN:", [(latest.loc[i, "PART"], round(float(ea[i]), 0)) for i in top_ea.index])

print("\n=== BIGGEST ORDER (most lines) ===")
ob = combined_outbound()
lpo = ob.groupby(["SOURCE_FILE", "ORDER NO"]).size().sort_values(ascending=False)
top = lpo.index[0]
print("  max lines in one order:", int(lpo.iloc[0]), "-> ORDER", top[1], "in", top[0][:22])
print("  top 5 orders by lines:", [(int(o[1]), int(n)) for o, n in lpo.head().items()])
print("  max PICKED QTY on a single line:", int(pd.to_numeric(ob["PICKED QTY"], errors="coerce").max()))
