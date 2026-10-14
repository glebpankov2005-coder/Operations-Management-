"""
DESIGN EVALUATION - aligns the design with the Week 3 lecture (layouts, storage & picking systems).

  * W3 data checks (most-ordered product, heaviest / longest SKU, largest order, max pallets in stock)
  * Lead time per geographical region (W3 follow-up checklist)
  * Layout concept evaluation: U-shaped vs flow-through docks (Huertas et al., 2007), judged on
    travel distance and dock doors - "produce a few basic concepts, evaluate, select the best"
  * Slotting with the Cube-per-Order Index (COI) + item-affinity check (SLAP, Kofler et al., 2014)
  * Hazardous-goods quantity vs the PGS 15 threshold (legal aspects of pallet storage)
  * Expected performance on the W3 KPIs: dock-to-stock, put-away cycle time, pick rate, on-time shipment
Run after picking_plan.py, capacity_plan.py and dock_mhe_plan.py.
"""
import json, os
import numpy as np
import pandas as pd
from load_data import all_storage, combined_outbound
from _util import save_table, update_metrics, TABLES
from geometry import aisle_x, rack_y0, rack_y1, cross_y, la, ra, rvh, uh, fwd_h, DEPTH

M = json.load(open(os.path.join(os.path.dirname(__file__), "..", "outputs", "reports", "phase1_metrics.json"), encoding="utf-8"))
CP, DM, PK = M["capacity_plan"], M["dock_mhe"], M["picking"]
storage = all_storage(); latest = storage["ASSA STORAGE DETAILS (01-06-2025).xlsx"]
st_all = pd.concat(storage.values(), ignore_index=True)
ob = combined_outbound()
for c in ["DATE", "ORDER ARRIVE DATE", "TRAILER DISPATCED DATE"]:
    ob[c] = pd.to_datetime(ob[c], errors="coerce")
n_days = ob["DATE"].dt.date.nunique()
abc = pd.read_csv(os.path.join(TABLES, "abc_by_sku.csv")).set_index("PRTNUM")

# ============================================================ 1. W3 data checks (slide 6)
by_orders = ob.groupby("PRTNUM")["ORDER NO"].nunique().sort_values(ascending=False)
master = latest.drop_duplicates("PART").set_index("PART")
ea_w = pd.to_numeric(master["EA WGT"], errors="coerce"); ea_l = pd.to_numeric(master["EA LEN"], errors="coerce")
pa_w = pd.to_numeric(master["PA WGT"], errors="coerce"); pa_w = pa_w[(pa_w > 0) & (pa_w < 9999)]
lpo = ob.groupby("ORDER NO").size()
snaps = M["inventory"]["snapshots"]
checks = [
    {"Question (W3)": "Most ordered product", "Answer": f"{by_orders.index[0]} — in {by_orders.iloc[0]} orders",
     "Note": f"{int(ob[ob.PRTNUM == by_orders.index[0]]['PICKED QTY'].sum()):,} units picked in Q2"},
    {"Question (W3)": "Heaviest SKU (single item)", "Answer": f"{ea_w.idxmax()} — {ea_w.max():.1f} kg per piece",
     "Note": f"heaviest pallet (cleaned) {pa_w.max():,.0f} kg; p99 pallet {pa_w.quantile(.99):,.0f} kg"},
    {"Question (W3)": "Longest SKU", "Answer": f"{ea_l.idxmax()} — {ea_l.max():.0f} cm",
     "Note": f"{int((ea_l > 240).sum())} SKUs longer than 2.4 m -> cantilever racking"},
    {"Question (W3)": "Most lines in one order", "Answer": f"{int(lpo.max())} lines", "Note": f"median order = {lpo.median():.0f} line"},
    {"Question (W3)": "Max pallets in stock", "Answer": f"{max(s['loads_LODNUM'] for s in snaps):,} loads in "
     f"{max(s['occupied_locations'] for s in snaps):,} locations", "Note": "June 2025 snapshot (peak of the quarter)"},
]
save_table(pd.DataFrame(checks).set_index("Question (W3)"), "w3_data_checks.csv")

# ============================================================ 2. lead time per region (slide 5)
o = ob.drop_duplicates("ORDER NO").copy()
o["lt_h"] = (o["TRAILER DISPATCED DATE"] - o["ORDER ARRIVE DATE"]).dt.total_seconds() / 3600
o = o[o.lt_h.between(0, 24 * 30)]
lt = o.groupby("SHIP TO COUNTRY").agg(orders=("lt_h", "size"), median_h=("lt_h", "median"), mean_h=("lt_h", "mean"),
                                       p90_h=("lt_h", lambda x: x.quantile(.9)),
                                       within_48h=("lt_h", lambda x: (x <= 48).mean() * 100))
lt = lt[lt.orders >= 20].sort_values("orders", ascending=False).round(1)
save_table(lt, "leadtime_by_region.csv")

# ============================================================ 3. layout concept: U-shaped vs flow-through (slides 14-15)
y_front, y_rear = (fwd_h + rack_y0) / 2, (rack_y1 + DEPTH) / 2
XC = [y_front, cross_y, y_rear]
ys = np.concatenate([np.linspace(rack_y0 + 1, cross_y - 2.6, 14), np.linspace(cross_y + 2.6, rack_y1 - 1, 14)])
gx, gy = np.meshgrid(aisle_x, ys); gx, gy = gx.ravel(), gy.ravel()
def d_from(px, py):
    return np.min([abs(py - yc) + abs(px - gx) + abs(gy - yc) for yc in XC], axis=0)
rows = []
for name, s in storage.items():                      # inbound loads by ABC class
    snap = pd.to_datetime(s["DATE"].iloc[0]); add = pd.to_datetime(s["ADD DATE"], errors="coerce")
    w = s[(add >= snap - pd.Timedelta(days=14)) & (add < snap)].drop_duplicates("LODNUM")
    rows.append(w["PART"].map(abc["ABC_vol"]).fillna("C").value_counts())
inb = pd.concat(rows, axis=1).sum(axis=1); in_share = (inb / inb.sum()).to_dict()
pos_share = latest.drop_duplicates("LOCATION")["PART"].map(abc["ABC_vol"]).fillna("C").value_counts(normalize=True).to_dict()
rank = np.argsort(d_from(ra, y_front)); n = len(gx)  # class-based storage: A closest to the pick P&D (east, front)
cut = np.cumsum([pos_share.get("A", 0), pos_share.get("B", 0)])
cls_idx = {"A": rank[:int(n * cut[0])], "B": rank[int(n * cut[0]):int(n * cut[1])], "C": rank[int(n * cut[1]):]}
loads_day = CP["measured"]["inbound_loads_day"]
concepts = {}
for cname, pdp in [("Flow-through (receiving west, shipping east)", (la, rvh / 2)),
                   ("U-shaped (receiving + shipping on the east wall)", (ra, 30.0))]:
    d = d_from(*pdp)
    per = {k: float(d[v].mean()) for k, v in cls_idx.items()}
    concepts[cname] = {"putaway_one_way_m": round(sum(in_share.get(k, 0) * per[k] for k in per), 1),
                       "per_class_m": {k: round(v, 1) for k, v in per.items()}}
ft, us = list(concepts.values())
for c_ in concepts.values():
    c_["putaway_km_day"] = round(2 * c_["putaway_one_way_m"] * loads_day / 1000, 1)
saving_pct = (us["putaway_one_way_m"] - ft["putaway_one_way_m"]) / ft["putaway_one_way_m"] * 100
truck_min_saved = (ft["putaway_km_day"] - us["putaway_km_day"]) * 1000 / (11 / 3.6 * 0.6) / 60
doors_ft = DM["inbound_doors"]["doors_recommended"] + DM["outbound_doors"]["doors_recommended"]
doors_u = max(DM["departure_plan"]["plan_max_doors_busy"], 2) + 1 + 1   # shared: afternoon peak + container + spare
concept_table = [
    {"Criterion": "Put-away travel (reach truck, per load, one way)", "Flow-through": f"{ft['putaway_one_way_m']:.0f} m",
     "U-shaped": f"{us['putaway_one_way_m']:.0f} m ({saving_pct:+.0f}%)"},
    {"Criterion": "Reach-truck time saved per day", "Flow-through": "-", "U-shaped": f"~{truck_min_saved:.0f} min"},
    {"Criterion": "Picking travel (all picks start/end at packing, east)", "Flow-through": "same", "U-shaped": "same"},
    {"Criterion": "Dock doors", "Flow-through": f"{doors_ft} (separate in/out)",
     "U-shaped": f"~{doors_u} if inbound always arrives before noon (shared)"},
    {"Criterion": "Traffic and errors (Huertas et al.)", "Flow-through": "Inbound and outbound separated - less congestion, fewer mix-ups",
     "U-shaped": "Inbound, returns and outbound share one dock face"},
    {"Criterion": "Fit to our profile (Huertas et al.)", "Flow-through": "Suits high volume, long/narrow buildings",
     "U-shaped": "Suits strong ABC (ours: 13% of SKUs = 80%)"},
]
verdict = ("Keep flow-through. U-shaped saves only ~{:.0f}% put-away travel (~{:.0f} reach-truck minutes/day) because "
           "slow C items still bring {:.0f}% of inbound loads and picking travel is identical; its door saving depends on "
           "all inbound arriving before noon, which sea containers cannot guarantee. Flow-through keeps inbound, returns "
           "and outbound apart and fits the side-wall dock lengths.").format(abs(saving_pct), truck_min_saved, in_share.get("C", 0) * 100)
save_table(pd.DataFrame(concept_table).set_index("Criterion"), "layout_concept_evaluation.csv")

# ============================================================ 4. COI slotting + affinity (slides 22-25)
occ = st_all.drop_duplicates(["SNAPSHOT_DATE", "LOCATION"]).groupby("PART").size() / len(storage)   # avg locations held
freq = abc["pick_lines"]                                                                          # pick lines in Q2
coi = (occ.reindex(freq.index) / freq).dropna()
coi = coi[coi > 0].sort_values()
coi_df = pd.DataFrame({"COI": coi, "ABC": abc["ABC_vol"].reindex(coi.index), "lines": freq.reindex(coi.index)})
coi_df["COI_quintile"] = pd.qcut(coi_df["COI"].rank(method="first"), 5, labels=["Q1 (best)", "Q2", "Q3", "Q4", "Q5 (worst)"])
xtab = pd.crosstab(coi_df["COI_quintile"], coi_df["ABC"])
lines_by_q = coi_df.groupby("COI_quintile", observed=True)["lines"].sum() / coi_df["lines"].sum() * 100
bulky_A = coi_df[(coi_df.ABC == "A") & (coi_df.COI_quintile.isin(["Q4", "Q5 (worst)"]))]
small_C = coi_df[(coi_df.ABC == "C") & (coi_df.COI_quintile.isin(["Q1 (best)"]))]
fam = latest.drop_duplicates("PART").set_index("PART")["PART FAMILY"]
multi = ob.assign(fam=ob.PRTNUM.map(fam)).dropna(subset=["fam"])
multi = multi[multi.groupby("ORDER NO")["PRTNUM"].transform("size") >= 2]
same = []
for _, g in multi.groupby("ORDER NO"):
    f = g["fam"].values; k = len(f)
    if k >= 2:
        vc = pd.Series(f).value_counts().values
        same.append(((vc * (vc - 1)).sum(), k * (k - 1)))
same_rate = sum(a for a, _ in same) / sum(b for _, b in same)
p = multi["fam"].value_counts(normalize=True); baseline = float((p ** 2).sum())
single_line_pct = float((lpo == 1).mean() * 100)
coi_summary = {"skus_scored": int(len(coi_df)), "picks_in_best_quintile_pct": round(float(lines_by_q.iloc[0]), 0),
               "picks_in_best_two_quintiles_pct": round(float(lines_by_q.iloc[:2].sum()), 0),
               "A_skus_in_best_two_quintiles_pct": round(float(xtab.get("A", pd.Series(0)).iloc[:2].sum() / max(xtab.get("A", pd.Series(1)).sum(), 1) * 100), 0),
               "bulky_A_skus": int(len(bulky_A)), "small_fast_C_skus": int(len(small_C)),
               "same_family_rate_pct": round(same_rate * 100, 0), "random_baseline_pct": round(baseline * 100, 0),
               "single_line_orders_pct": round(single_line_pct, 0)}
save_table(xtab, "coi_vs_abc.csv")

# ============================================================ 5. hazardous goods vs PGS 15 (legal)
hz = latest.copy()
hz_flag = hz["HAZMAT"].astype(str).str.strip().str.upper()
hz = hz[~hz_flag.isin(["", "0", "N", "NAN", "NONE", "NO"])]
hz_kg = float((pd.to_numeric(hz["QTY"], errors="coerce") * pd.to_numeric(hz["EA WGT"], errors="coerce")).sum())
hazmat = {"skus": int(hz["PART"].nunique()), "loads": int(hz["LODNUM"].nunique()), "kg_in_stock": round(hz_kg, 0),
          "pgs15_threshold_kg": 10000, "above_threshold": bool(hz_kg > 10000)}

# ============================================================ 6. expected KPIs (slide 9)
cyc = {c["Move"]: c for c in DM["cycle_times"]}
t_put = cyc["Putaway (receiving -> reserve)"]["Cycle min"]; t_unl = cyc["Unload pallet (trailer -> receiving lane)"]["Cycle min"]
pal_trailer = CP["measured"]["inbound_loads_day"] * (1 - CP["measured"]["inbound_asia_origin_pct"] / 100)
etv_active = max(1, [f for f in DM["fleet"] if "ETV" in f["Model"]][0]["Units required (peak)"])
dock_to_stock_trailer = (20 + pal_trailer * max(t_unl, t_put / etv_active)) / 60
dock_to_stock_container = DM["inbound_doors"]["container_door_h"] + 0.5
small_h = sum(r["Picker-h avg"] for r in PK["small_orders"]); small_l = sum(r["Lines/day"] for r in PK["small_orders"])
lg = PK["large_orders"]; all_lines = small_l + lg["orders_day"] * lg["lines_per_order"]
pick_rate = all_lines / (small_h + lg["picker_h_avg"])
staged_late_today = 50.1
kpis = [
    {"KPI (W3)": "Dock-to-stock time", "Expected": f"~{dock_to_stock_trailer:.1f} h per palletised trailer; ~{dock_to_stock_container:.1f} h per loose container",
     "Basis": "unload ~1 min/pallet (ERE 225) while 2 reach trucks put away in parallel; container de-stuffed by contractor"},
    {"KPI (W3)": "Put-away cycle time", "Expected": f"{t_put:.1f} min per pallet (~{60 / t_put:.0f} per truck-hour)",
     "Basis": "ETV 216i cycle model on the Option B routes (S006)"},
    {"KPI (W3)": "Pick rate", "Expected": f"~{pick_rate:.0f} lines per picker-hour overall "
     f"(fast-pick {PK['small_orders'][0]['Lines/h']:.0f}, reserve {PK['small_orders'][1]['Lines/h']:.0f}, large orders {lg['lines_per_h']:.0f})",
     "Basis": "pick-time model, largest-gap routing, trolley batching"},
    {"KPI (W3)": "On-time shipment rate", "Expected": "target ≥ 98% staged before the booked departure",
     "Basis": f"waves end 45 min before each slot; today {staged_late_today}% of lines are staged 'LATE' (A005, definition to confirm)"},
]
save_table(pd.DataFrame(kpis).set_index("KPI (W3)"), "w3_kpis.csv")

update_metrics("design_evaluation", {
    "w3_checks": checks, "leadtime_by_region": lt.reset_index().to_dict("records"),
    "concepts": concepts, "concept_table": concept_table, "concept_verdict": verdict,
    "inbound_share_by_class_pct": {k: round(v * 100, 0) for k, v in in_share.items()},
    "doors_flow_through": doors_ft, "doors_u_shaped": doors_u,
    "coi": coi_summary, "coi_vs_abc": xtab.reset_index().to_dict("records"),
    "hazmat": hazmat, "kpis": kpis,
})
print("CHECKS"); [print(" ", c) for c in checks]
print("LEADTIME\n", lt.head(8).to_string())
print("CONCEPTS", json.dumps(concepts, indent=1)); print("doors", doors_ft, "vs", doors_u); print(verdict)
print("COI", coi_summary); print(xtab)
print("HAZMAT", hazmat)
print("KPIs"); [print(" ", k) for k in kpis]
