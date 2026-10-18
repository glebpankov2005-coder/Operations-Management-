"""
DOCK DOORS + MATERIAL-HANDLING EQUIPMENT (MHE) for Option B.

Inbound  : 2 shipments/day direct from Assa Abloy factories (teacher/DHL input, A018),
           mixed: palletised road trailers (Europe) and LOOSE floor-loaded sea
           containers (Asia) that are de-stuffed and palletised by hand (A019).
Outbound : measured trailer-by-trailer from the outbound files (TRAILER ID,
           arrive/dispatch timestamps, pallets & cartons per shipment).
MHE      : Jungheinrich models selected and sized from their published technical
           data (S006-S008) using a cycle-time model on the Option B layout.
Also     : the 08:00 pick peak is shown to come from the ORDER-RELEASE routine.

Run after capacity_plan.py (reads its measured drivers from phase1_metrics.json).
"""
import json, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from load_data import combined_outbound, all_storage
from _util import save_table, save_fig, update_metrics

M = json.load(open(os.path.join(os.path.dirname(__file__), "..", "outputs", "reports", "phase1_metrics.json"), encoding="utf-8"))
CP = M["capacity_plan"]; MEAS = CP["measured"]; INP = CP["inbound_pattern"]
NET_H, MHE_UTIL, DOOR_UTIL = 7.5, 0.80, 0.85        # A015 + door planning utilisation (A020)
RED, YEL, INK, GREY = "#D40511", "#FFCC00", "#262626", "#9aa7bd"

# ====================================================== Jungheinrich data (S006-S008)
JH = {
    "ETV 216i": {"role": "Reach truck - putaway, replenishment, full-pallet picks (single-deep racks: standard forks)",
                 "capacity_kg": 1600, "load_centre_mm": 600, "max_lift_mm": 10700, "ext_mast_mm": 11700,
                 "ast_mm": "2,631-2,785", "width_mm": 1270, "v_travel_kmh": 11, "v_travel_max_kmh": 14,
                 "v_lift_laden": 0.59, "v_lift_empty": 0.81, "v_lower": 0.56, "v_reach": 0.24, "reach_mm": 616,
                 "accel_s": 4.6, "battery": "Li-ion 51.2 V / 360 Ah, opportunity charging", "src": "S006"},
    "EJE 120i": {"role": "Walkie pallet truck - large orders picked onto a pallet",
                 "capacity_kg": 2000, "load_centre_mm": 610, "length_mm": 1575, "width_mm": 720,
                 "wa_mm": "1,414-1,464", "ast_mm": "1,787-1,936", "v_travel_kmh": 5.6,
                 "battery": "Li-ion 25.6 V", "src": "S010"},
    "EZS 130":  {"role": "Tow tractor for a small-parts tugger train (evaluated, not planned)",
                 "tow_kg": 3000, "length_mm": 1315, "width_mm": 600, "wa_mm": "~1,080 (secondary source)",
                 "v_travel_kmh": 10.5, "battery": "24 V, Li-ion option", "src": "S012"},
    "Pick trolley": {"role": "Manual 3-tier trolley, 6 totes - small orders, zone batch picking",
                 "shelf_mm": "1,000 x 600", "capacity_kg": 250, "per_tier_kg": 80, "src": "S011"},
    "ERE 225":  {"role": "Rider pallet truck - unloading/loading trailers & containers, dock moves",
                 "capacity_kg": 2500, "fork_mm": 1000, "v_travel_kmh": 14, "battery": "Li-ion option (ERE 225i)",
                 "src": "S008"},
}

# ====================================================== Option B geometry (shared module)
from geometry import (rack_y0, rack_y1, cross_y, aisle_x, la, ra, rvh, uh, PITCH_M, mean_h, top_beam)

# reserve slot grid (aisle face x, position y) for travel distances
ys = np.concatenate([np.linspace(rack_y0 + 1, cross_y - 2.6, 12), np.linspace(cross_y + 2.6, rack_y1 - 1, 12)])
gx, gy = np.meshgrid(aisle_x, ys)
# Reach trucks keep to the perimeter aisles + cross-aisle (traffic kept out of the pick zone):
# P&D(receiving) -> up left aisle -> along cross-aisle -> into storage aisle -> slot
pd_in = (la, rvh / 2)
d_put = np.abs(cross_y - pd_in[1]) + np.abs(gx - pd_in[0]) + np.abs(gy - cross_y)
d_rep = np.abs(gy - rack_y0)                               # same aisle down to the fast-pick rear input
pd_out = (ra, uh / 2)
d_fp = np.abs(gy - cross_y) + np.abs(gx - pd_out[0]) + np.abs(cross_y - pd_out[1])

def etv_cycle(d_oneway):
    """Reach-truck cycle (s): fixed handling + travel round trip + lift/lower + reach (single-deep: no telescopic fork time)."""
    e = JH["ETV 216i"]
    v = e["v_travel_kmh"] / 3.6
    t_travel = 2 * d_oneway / v + 4 * e["accel_s"]        # 2 legs each way, accel/decel penalty per leg
    t_lift = mean_h / e["v_lift_laden"] + mean_h / e["v_lower"]
    t_reach = 2 * 2 * (e["reach_mm"] / 1000) / e["v_reach"]  # reach out + in, at pick-up and at deposit
    t_fixed = 45.0                                          # scan, fork entry, fine positioning, confirm (A021)
    return t_fixed + t_travel + t_lift + t_reach

t_put = etv_cycle(float(d_put.mean())) / 60
t_rep = etv_cycle(float(d_rep.mean())) / 60
t_fp = etv_cycle(float(d_fp.mean())) / 60

def ere_move(d_oneway, fixed_s):
    v = JH["ERE 225"]["v_travel_kmh"] / 3.6 * 0.5            # short dock legs: ~50% of max speed (A021)
    return (fixed_s + 2 * d_oneway / v) / 60
TRAILER_HALF = 13.6 / 2                                     # avg depth into a 13.6 m trailer
t_unload = ere_move(12 + TRAILER_HALF, 40)                  # dock -> receiving lane + scan/check
t_load = ere_move(12 + TRAILER_HALF, 55)                    # staging lane -> trailer, positioning in trailer
t_cage = ere_move(12 + TRAILER_HALF, 30)                    # roll cage of parcels (~20 cartons) push-in

# ====================================================== INBOUND dock doors
loose = MEAS["inbound_asia_origin_pct"] / 100
pal_avg = MEAS["inbound_loads_day"] * (1 - loose)
pal_peak = pal_avg * MEAS["inbound_peak_factor"]
DOCK_FIX_IN = 20 / 60                                       # dock-on, seal check, ASN/paperwork (A020)
door_trailer = DOCK_FIX_IN + pal_avg * t_unload / 60
door_trailer_pk = DOCK_FIX_IN + pal_peak * t_unload / 60
door_container = DOCK_FIX_IN + INP["destuff_h"]
door_container_hi = DOCK_FIX_IN + 4.0
RECV_WINDOW = 8.0                                           # 06:00-14:00 receiving window
cap_in = RECV_WINDOW * DOOR_UTIL
in_scen = [
    ("Average day: 1 palletised trailer + 1 loose container", door_trailer + door_container, 2),
    ("Peak day: palletised volume x1.7 + 1 loose container", door_trailer_pk + door_container, 2),
    ("Worst case: 2 loose containers (4 h de-stuff each)", 2 * door_container_hi, 2),
    ("Sensitivity: ~8 smaller trucks/day (WMS truck IDs)", 8 * (DOCK_FIX_IN + (MEAS["inbound_loads_day"] / 8) * t_unload / 60), 3),
]
in_rows = []
for name, door_h, simult in in_scen:
    by_capacity = int(np.ceil(door_h / cap_in))
    in_rows.append({"Scenario": name, "Door-hours/day": round(door_h, 1),
                    "Doors by capacity": by_capacity, "Simultaneous arrivals": simult,
                    "Doors needed": max(by_capacity, simult)})
inbound = pd.DataFrame(in_rows)
IN_NEEDED_BASE = int(inbound["Doors needed"].iloc[0])       # teacher scenario: 2 arrivals/day
IN_DOORS = int(max(inbound["Doors needed"].max(), IN_NEEDED_BASE + 1))   # covers all scenarios; base +1 resilience
save_table(inbound.set_index("Scenario"), "dock_inbound.csv")

# ====================================================== OUTBOUND dock doors (trailer-level simulation)
ob = combined_outbound()
for c in ["TRAILER ARRIVE DATE", "TRAILER DISPATCED DATE", "ORDER ARRIVE DATE", "ALOCATE DATE", "PICK DATE"]:
    ob[c] = pd.to_datetime(ob[c], errors="coerce")
sh = ob.drop_duplicates("SHIPMENT ID").copy()
sh["pal"] = pd.to_numeric(sh["SHIPMENT PACKED PALLETS"], errors="coerce").fillna(0)
sh["ctn"] = pd.to_numeric(sh["SHIPMENT PACKED CARTONS"], errors="coerce").fillna(0)
tr = (ob.drop_duplicates("TRAILER ID").set_index("TRAILER ID")
        [["CARRIER NAME", "TRAILER ARRIVE DATE", "TRAILER DISPATCED DATE"]]
        .join(sh.groupby("TRAILER ID")[["pal", "ctn"]].sum()).dropna(subset=["TRAILER DISPATCED DATE"]))
tr = tr[tr["TRAILER DISPATCED DATE"] >= tr["TRAILER ARRIVE DATE"].fillna(tr["TRAILER DISPATCED DATE"])]
DOCK_FIX_OUT = 15.0                                          # dock-on, paperwork, seal (min, A020)
cages = np.ceil(tr["ctn"] / 20.0)                            # parcels staged on roll cages (~20 cartons)
tr["dock_min"] = DOCK_FIX_OUT + tr["pal"] * t_load + cages * t_cage
tr["day"] = tr["TRAILER DISPATCED DATE"].dt.date

def max_concurrent(starts, ends):
    ev = sorted([(s, 1) for s in starts] + [(e, -1) for e in ends], key=lambda x: (x[0], x[1]))
    n = best = 0
    for _, d in ev:
        n += d; best = max(best, n)
    return best

fut, cur = [], []
for day, g in tr.groupby("day"):
    end = g["TRAILER DISPATCED DATE"]
    fut.append(max_concurrent(list(end - pd.to_timedelta(g["dock_min"], unit="m")), list(end)))
    gg = g.dropna(subset=["TRAILER ARRIVE DATE"])
    cur.append(max_concurrent(list(gg["TRAILER ARRIVE DATE"]), list(gg["TRAILER DISPATCED DATE"])))
fut, cur = pd.Series(fut), pd.Series(cur)
per_day = tr.groupby("day").size()
busiest_hour = tr.groupby("day")["TRAILER DISPATCED DATE"].agg(lambda x: x.dt.floor("h").value_counts().max())
# Standard method (size to the busiest hour): doors = trailers/peak-hour x dock time / (60 min x utilisation).
# Requires carrier collection TIME SLOTS. WMS dispatch stamps are clerk batch-closes (60% of afternoon
# dispatches <2 min apart), so the trailer-level simulation (fut) is kept only as a "no time slots" sensitivity.
gaps = tr["TRAILER DISPATCED DATE"].sort_values()
gaps = gaps[gaps.dt.hour.between(14, 16)].diff().dt.total_seconds().div(60)
batch_close_pct = float((gaps < 2).mean() * 100)
formula_doors = busiest_hour.quantile(.9) * tr["dock_min"].mean() / 60 / DOOR_UTIL
formula_doors_max = busiest_hour.max() * tr["dock_min"].mean() / 60 / DOOR_UTIL
OUT_NEEDED = int(np.ceil(formula_doors))
OUT_DOORS = OUT_NEEDED + 1                                   # +1 resilience (unannounced ex-works pickups, breakdowns)
out_summary = {
    "trailers_per_day_mean": round(float(per_day.mean()), 1), "trailers_per_day_p90": float(per_day.quantile(.9)),
    "trailers_per_day_max": int(per_day.max()),
    "pallets_per_trailer_mean": round(float(tr["pal"].mean()), 1), "cartons_per_trailer_mean": round(float(tr["ctn"].mean()), 1),
    "share_trailers_zero_pallets_pct": round(float((tr["pal"] == 0).mean() * 100), 0),
    "dock_min_mean": round(float(tr["dock_min"].mean()), 0), "dock_min_p90": round(float(tr["dock_min"].quantile(.9)), 0),
    "busiest_hour_trailers_p90": float(busiest_hour.quantile(.9)), "busiest_hour_trailers_max": int(busiest_hour.max()),
    "current_drop_trailer_concurrent_median": float(cur.median()), "current_drop_trailer_concurrent_p90": float(cur.quantile(.9)),
    "future_liveload_concurrent_median": float(fut.median()), "future_liveload_concurrent_p90": float(fut.quantile(.9)),
    "future_liveload_concurrent_max": int(fut.max()), "formula_doors_p90_hour": round(float(formula_doors), 1),
    "formula_doors_max_hour": round(float(formula_doors_max), 1), "wms_batch_close_pct": round(batch_close_pct, 0),
    "doors_needed": OUT_NEEDED, "doors_recommended": OUT_DOORS,
}
carriers = (tr.groupby("CARRIER NAME").size() / per_day.size).sort_values(ascending=False).round(2)
save_table(carriers.rename("trailers_per_day").to_frame(), "dock_outbound_carriers.csv")

# ====================================================== MHE fleet sizing
ETV_h = (MEAS["inbound_loads_day"] * MEAS["inbound_peak_factor"] * t_put
         + MEAS["replen_pallets_day"] * M["peak"]["units"]["peak_over_avg"] * t_rep
         + MEAS["lines_pallet_day"] * M["peak"]["lines"]["peak_over_avg"] * t_fp) / 60
ETV_h_avg = (MEAS["inbound_loads_day"] * t_put + MEAS["replen_pallets_day"] * t_rep + MEAS["lines_pallet_day"] * t_fp) / 60
PK = M["picking"]
EJE_h, EJE_h_avg = PK["large_orders"]["picker_h_peak"], PK["large_orders"]["picker_h_avg"]
cont_pallets_pk = MEAS["inbound_loads_day"] * loose * INP["containers_peak"] / max(INP["containers_avg"], 1)
out_pal_pk = MEAS["outbound_pallets_max"]
ERE_h = (pal_peak * t_unload + cont_pallets_pk * t_unload
         + out_pal_pk * t_load + np.ceil(MEAS["outbound_cartons_day"] * M["peak"]["units"]["peak_over_avg"] / 20) * t_cage) / 60
ERE_h_avg = (pal_avg * t_unload + MEAS["inbound_loads_day"] * loose * t_unload
             + MEAS["outbound_pallets_day"] * t_load + np.ceil(MEAS["outbound_cartons_day"] / 20) * t_cage) / 60
avail = NET_H * MHE_UTIL
fleet = []
# Spare rule (D3 machinery review): a spare is added only where one breakdown would stop a process.
# With >= 2 units of a type, one breakdown still leaves enough for an average day; full-service lease
# contracts include repair (S021). ERE 225: one per dock side (west receiving + container zone, east shipping).
for model, h_avg, h_pk, task in [
    ("ETV 216i", ETV_h_avg, ETV_h, "Putaway + replenishment + full-pallet picks"),
    ("EJE 120i", EJE_h_avg, EJE_h, "Large orders: pick-to-pallet (one order per pallet)"),
    ("ERE 225", ERE_h_avg, ERE_h, "Unload trailers/containers, load outbound, dock moves")]:
    need = max(1, int(np.ceil(h_pk / avail)))
    need_avg = max(1, int(np.ceil(h_avg / avail)))
    planned = 2 if model == "ERE 225" else (need + 1 if need == 1 else need)
    fleet.append({"Model": f"Jungheinrich {model}", "Task": task,
                  "Equip-h/day avg": round(h_avg, 1), "Equip-h/day peak": round(h_pk, 1),
                  "Units required (avg)": need_avg, "Units required (peak)": need, "Units recommended": planned,
                  "Utilisation avg %": round(h_avg / (planned * NET_H) * 100, 0)})
tro = [e for e in PK["equipment"] if e["Item"].startswith("Pick trolley")][0]
fleet.append({"Model": "Pick trolley (3-tier, 6 totes) + totes", "Task": "Small orders: zone batch picking, sorted at the put-wall",
              "Equip-h/day avg": round(sum(r["Picker-h avg"] for r in PK["small_orders"]), 1),
              "Equip-h/day peak": round(sum(r["Picker-h peak"] for r in PK["small_orders"]), 1),
              "Units required (avg)": tro["Required"], "Units required (peak)": tro["Required"], "Units recommended": tro["Planned"],
              "Utilisation avg %": None})
fleet = pd.DataFrame(fleet)
save_table(fleet.set_index("Model"), "mhe_fleet.csv")

cycle = pd.DataFrame([
    {"Move": "Putaway (receiving -> reserve)", "Truck": "ETV 216i", "Avg one-way m": round(float(d_put.mean()), 0), "Cycle min": round(t_put, 2), "Moves/h": round(60 / t_put, 1)},
    {"Move": "Replenishment (reserve -> fast-pick rear)", "Truck": "ETV 216i", "Avg one-way m": round(float(d_rep.mean()), 0), "Cycle min": round(t_rep, 2), "Moves/h": round(60 / t_rep, 1)},
    {"Move": "Full-pallet pick (reserve -> outbound)", "Truck": "ETV 216i", "Avg one-way m": round(float(d_fp.mean()), 0), "Cycle min": round(t_fp, 2), "Moves/h": round(60 / t_fp, 1)},
    {"Move": "Unload pallet (trailer -> receiving lane)", "Truck": "ERE 225", "Avg one-way m": round(12 + TRAILER_HALF, 0), "Cycle min": round(t_unload, 2), "Moves/h": round(60 / t_unload, 1)},
    {"Move": "Load pallet (staging -> trailer)", "Truck": "ERE 225", "Avg one-way m": round(12 + TRAILER_HALF, 0), "Cycle min": round(t_load, 2), "Moves/h": round(60 / t_load, 1)},
])
save_table(cycle.set_index("Move"), "mhe_cycle_times.csv")

# ====================================================== fit checks (layout vs truck data)
st_all = all_storage()
snap = st_all["ASSA STORAGE DETAILS (01-06-2025).xlsx"]
st = snap.drop_duplicates("PART")
w = pd.to_numeric(st["PA WGT"], errors="coerce"); w = w[(w > 0) & (w < 9999)]
# actual load weight = sum(qty x unit weight) per load (the SKU's PA WGT is a full-pallet master value)
act = (pd.to_numeric(snap["QTY"], errors="coerce") * pd.to_numeric(snap["EA WGT"], errors="coerce")).groupby(snap["LODNUM"]).sum()
LW = {"over_1000": int((act > 1000).sum()), "over_1600": int((act > 1600).sum()), "loads": int(act.size)}
ld = snap.drop_duplicates("LODNUM")
def _num(c):
    x = pd.to_numeric(ld[c], errors="coerce"); return x.where((x > 0) & (x < 9999))     # 9999 = missing in the WMS
plen, phgt = _num("PA LEN"), _num("PA HGT")
LG = {"loads_over_1_9m": int(((plen > 190) & (plen <= 240)).sum()), "loads_over_2_4m": int((plen > 240).sum())}
from geometry import LEVELS as _LV
_pos = json.load(open(os.path.join(os.path.dirname(__file__), "..", "outputs", "reports", "phase1_metrics.json"), encoding="utf-8"))["layout"]["positions_total"]
TL = {"loads_1_16_to_1_68": int(((phgt > 116) & (phgt <= 168)).sum()), "loads_over_1_68": int((phgt > 168).sum()),
      "height_missing": int(phgt.isna().sum()), "top_level_positions": int(_pos / _LV)}
fit = pd.DataFrame([
    {"Check": "Working aisle (reach aisle 3.0 m)", "Requirement": "ETV 216i Ast 2,631-2,785 mm", "Result": "OK - 0.2-0.4 m margin"},
    {"Check": f"Top beam {top_beam:.2f} m (8 levels x {PITCH_M} m)", "Requirement": "Max lift 10.7 m", "Result": f"OK - {10.7 - top_beam:.2f} m spare"},
    {"Check": "Clear height 12.2 m", "Requirement": "Extended mast 11.7 m at max lift", "Result": "OK - 0.5 m clearance"},
    {"Check": f"Pallet weight p95 {w.quantile(.95):.0f} kg / p99 {w.quantile(.99):.0f} kg", "Requirement": "1,600 kg @ 600 mm", "Result": f"OK for {100 * (w <= 1600).mean():.1f}% of SKUs; >1 t pallets slotted on low levels"},
    {"Check": f"Actual load weight in stock (qty x unit weight): {LW['over_1000']} loads > 1 t, {LW['over_1600']} > 1.6 t", "Requirement": "1,600 kg @ 600 mm",
     "Result": "OK - the few loads > 1.6 t go to floor positions, moved with the ERE 225 (2.5 t)"},
    {"Check": "Single-deep (back-to-back) racks", "Requirement": "every pallet reachable from an aisle", "Result": "OK - standard forks; no telescopic attachment, no residual-capacity loss"},
    {"Check": f"Long pallets: {LG['loads_over_1_9m']} loads 1.9-2.4 m (XLONG/CONS), {LG['loads_over_2_4m']} > 2.4 m", "Requirement": "fit the rack and the 3.0 m aisle",
     "Result": "OK - 1.9-2.4 m pallets stored crosswise, 1 per 2.7 m bay in the odd/long modules (forks enter the long side); > 2.4 m on cantilever"},
    {"Check": f"Tall loads: {TL['loads_1_16_to_1_68']} loads 1.16-1.68 m, {TL['loads_over_1_68']} > 1.68 m", "Requirement": "1.41 m level pitch",
     "Result": f"OK - top level (~1.7 m free under the roof clearance) has {TL['top_level_positions']:,} positions; > 1.68 m on the floor"},
    {"Check": f"Large orders up to p90 {PK['large_orders']['kg_p90']:.0f} kg", "Requirement": "EJE 120i 2,000 kg", "Result": "OK - picked onto one pallet"},
    {"Check": "Small orders (median 7 L)", "Requirement": "Trolley 6 totes, 250 kg", "Result": f"OK - ~{PK['small_orders'][0]['Lines per tour']:.0f} lines per tour"},
    {"Check": "Charging", "Requirement": "Li-ion opportunity charging", "Result": "No battery room; chargers at P&D points"},
])
save_table(fit.set_index("Check"), "mhe_fit_checks.csv")

# ====================================================== 08:00 = order-release routine
orders = ob.drop_duplicates("ORDER NO")
prof = pd.DataFrame({
    "Orders arrive": orders["ORDER ARRIVE DATE"].dt.hour.value_counts(normalize=True),
    "Orders released (allocated)": orders["ALOCATE DATE"].dt.hour.value_counts(normalize=True),
    "Lines picked": ob["PICK DATE"].dt.hour.value_counts(normalize=True),
}).fillna(0).sort_index() * 100
prof = prof[prof.index.notna()]; prof.index = prof.index.astype(int)
prof = prof.loc[[h for h in prof.index if 5 <= h <= 19]]
picks_h = ob["PICK DATE"].dt.hour.value_counts().sort_index()
active = picks_h[(picks_h.index >= 6) & (picks_h.index <= 14)]
peak_hour = int(active.idxmax()); peak_ratio = float(active.max() / active.mean())
release = {"orders_arrive_15_17_pct": round(float(prof.loc[[15, 16], "Orders arrive"].sum()), 0),
           "allocated_16_18_pct": round(float(prof.loc[[16, 17], "Orders released (allocated)"].sum()), 0),
           "pick_peak_hour": peak_hour, "pick_peak_over_mean_active_hour": round(peak_ratio, 2),
           "picker_capacity_saving_if_levelled_pct": round((1 - 1 / peak_ratio) * 100, 0)}

# ====================================================== turning / aisle check (all picking & handling machines)
turning = pd.DataFrame([
    {"Machine": "ETV 216i reach truck", "Size (L x W)": "2,419 x 1,270 mm", "Turning / aisle needed": "Wa 1,665 mm; aisle 2,631-2,785 mm",
     "Where it drives": "Perimeter + cross-aisles; storage aisles", "Narrowest aisle": "3.0 m", "Result": "OK - turns 90° in the 3.2 m cross-aisles; drives through or reverses out"},
    {"Machine": "EJE 120i pallet truck", "Size (L x W)": "1,575 x 720 mm", "Turning / aisle needed": "Wa 1,414-1,464 mm; aisle 1,787-1,936 mm",
     "Where it drives": "Fast-pick area, storage aisles, cross-aisles", "Narrowest aisle": "3.0 m", "Result": "OK - aisles open at both ends, so no U-turn needed"},
    {"Machine": "Pick trolley (manual)", "Size (L x W)": "1,000 x 600 mm", "Turning / aisle needed": "pushed by hand",
     "Where it drives": "Everywhere in the pick zones", "Narrowest aisle": "3.0 m", "Result": "OK"},
    {"Machine": "ERE 225 rider pallet truck", "Size (L x W)": "rider truck, 1,000 mm forks", "Turning / aisle needed": "dock work only",
     "Where it drives": "Dock strips and staging lanes (west + east)", "Narrowest aisle": "open dock area", "Result": "OK - no aisle driving"},
    {"Machine": "EZS 130 tugger (option)", "Size (L x W)": "1,315 x 600 mm + carts", "Turning / aisle needed": "Wa ~1,080 mm (tractor)",
     "Where it drives": "Loop on perimeter + cross-aisles only", "Narrowest aisle": "3.2 m", "Result": "OK for a short train; not planned (low volume)"},
    {"Machine": "ECE 225 order picker (dropped)", "Size (L x W)": "3,670 x 810 mm, 2,400 mm forks", "Turning / aisle needed": "too long for 3.0 m aisles",
     "Where it drives": "-", "Narrowest aisle": "3.0 m", "Result": "Rejected - cannot turn or U-turn in the aisles; 2 pallets far too big"},
])
save_table(turning.set_index("Machine"), "mhe_turning_check.csv")

# ====================================================== why each machine (justification)
ov = PK["order_volume"]; lg = PK["large_orders"]; seg = {r["segment"]: r for r in PK["segments"]}
def units(key):
    return int(fleet.loc[fleet.Model.str.contains(key), "Units recommended"].iloc[0])
just = pd.DataFrame([
    {"Machine": "ETV 216i reach truck", "Process": "Putaway, replenishment, full-pallet picks",
     "Why (data)": f"Pallets stored up to the 8th level (top beam {top_beam:.1f} m) - needs 10.7 m lift; single-deep racks, so standard forks; {LW['loads'] - LW['over_1600']:,} of {LW['loads']:,} loads ≤ 1.6 t",
     "How it is used": f"Perimeter + cross-aisles; ~{60 / t_put:.0f} putaways/h; feeds fast-pick lanes from the rear", "Units": units("ETV")},
    {"Machine": "EJE 120i pallet truck", "Process": "Large orders: pick-to-pallet",
     "Why (data)": f"{seg['large']['pct_orders']:.0f}% of orders ({seg['large']['orders_day']:.0f}/day) are pallet-sized: median {lg['litres_median']:.0f} L, {lg['kg_median']:.0f} kg (p90 {lg['kg_p90']:.0f} kg) - too big/heavy for a trolley",
     "How it is used": f"One order per pallet; ~{lg['lines_per_order']:.0f} lines in ~{lg['min_per_order']:.0f} min; drops the pallet at packing", "Units": units("EJE")},
    {"Machine": "Pick trolley + totes", "Process": "Small orders: zone batch picking",
     "Why (data)": f"{seg['small']['pct_orders']:.0f}% of orders are small (median order {ov['median_l']:.0f} L; {ov['pct_orders_fitting']['1_tote']:.0f}% fit in one tote)",
     "How it is used": f"WMS fills each trolley to its volume/weight limit (~{PK['small_orders'][0]['Lines per tour']:.0f} lines per tour); put-to-light wall sorts per order", "Units": units("trolley")},
    {"Machine": "ERE 225 rider pallet truck", "Process": "Unloading and loading trailers",
     "Why (data)": f"~{MEAS['inbound_loads_day']:.0f} inbound loads/day in the morning + outbound pallets in the afternoon; rider = less walking, 2.5 t",
     "How it is used": "One per dock side (west receiving, east shipping)", "Units": units("ERE")},
    {"Machine": "EZS 130 tugger train", "Process": "Transport picked trolleys to packing (option)",
     "Why (data)": f"Fits zone picking, but only ~{PK['tugger']['trolleys_per_day']:.0f} trolley trips/day; a driver would be {PK['tugger']['driver_utilisation_pct']:.0f}% busy to save ~{PK['tugger']['picker_walk_saved_h_day'] * 60:.0f} min walking",
     "How it is used": "Not planned now; adopt if small-order volume ~triples or packing moves away from the pick zones", "Units": 0},
])
save_table(just.set_index("Machine"), "mhe_justification.csv")

# ====================================================== loose-container zone (teacher feedback: separate zone for loose containers)
# Sized from the Asian-origin receipts in the stock data (INBOUND TRUCK NO with >= 10 loads ~ one container):
# how many different SKUs (= pallets being built at the same time) and how many pallets one container gives.
ASIA = {"CN", "TW", "KR", "VN", "JP", "IN", "TH", "MY", "ID", "HK", "PH", "SG"}
rc = []
for s_ in st_all.values():
    a_ = s_.drop_duplicates("LODNUM"); a_ = a_[a_["ORGCOD"].astype(str).isin(ASIA)]
    rc.append(a_.groupby("INBOUND TRUCK NO").agg(loads=("LODNUM", "nunique"), skus=("PART", "nunique")))
rc = pd.concat(rc); rc = rc[rc["loads"] >= 10]
PALLET_FLOOR = 1.9                                          # m2 per floor-staged pallet incl. access (as receiving)
build_spots = int(np.ceil(rc["skus"].quantile(.75))) + 1    # one build spot per SKU in a typical-large container (+1 mixed/rest)
buffer_pal = int(np.ceil(rc["loads"].quantile(.75)))        # finished pallets of a typical-large container waiting for putaway
zone_parts = {"Unload lane with extendable roller conveyor (12 x 2 m)": 24.0,
              f"Pallet build spots ({build_spots} x 3 m2)": build_spots * 3.0,
              f"Finished-pallet buffer ({buffer_pal} x {PALLET_FLOOR} m2)": buffer_pal * PALLET_FLOOR,
              "Label / scan / stretch-wrap station": 16.0}
zone_net = sum(zone_parts.values()); zone_need = zone_net * 1.3          # +30% walkways
from geometry import LOOSE as LOOSE_M2
loose_zone = {"containers_sampled": int(len(rc)), "loads_per_container_median": float(rc["loads"].median()),
              "loads_per_container_p75": float(rc["loads"].quantile(.75)), "loads_per_container_max": int(rc["loads"].max()),
              "skus_per_container_median": float(rc["skus"].median()), "skus_per_container_p75": float(rc["skus"].quantile(.75)),
              "skus_per_container_max": int(rc["skus"].max()),
              "build_spots": build_spots, "buffer_pallets": buffer_pal,
              "parts_m2": {k: round(v, 0) for k, v in zone_parts.items()},
              "area_needed_m2": round(zone_need, 0), "area_planned_m2": LOOSE_M2,
              "crew": INP["destuff_crew"], "hours_per_container": INP["destuff_h"]}

# ====================================================== loose containers: who does the work in the zone
cont = pd.DataFrame([
    {"Option": "In-house DHL crew", "How": "2 DHL staff unpack each container in the loose-container zone at door R1",
     "DHL labour": f"{INP['destuff_crew'] * INP['destuff_h']:.0f} person-h per container", "Door": f"R1 ~{door_container:.1f} h/day",
     "Pros": "Full control, flexible timing", "Cons": "Heavy manual handling, training, peak days need 2 crews"},
    {"Option": "On-site specialist contractor", "How": "Contractor crew unpacks and palletises in the same zone, paid per container",
     "DHL labour": "none", "Door": f"R1 ~{door_container:.1f} h/day",
     "Pros": "No own labour or peak staffing; specialist speed and safety; cost scales with containers", "Cons": "Per-container fee (no public price - quote needed); booking coordination"},
    {"Option": "Port / CFS devanning", "How": "Container unpacked and palletised near the port; arrives as a palletised trailer",
     "DHL labour": "none", "Door": "standard trailer",
     "Pros": "Simplest receiving - everything palletised", "Cons": "Extra transport and handling cost; ~1 day longer lead time; less control"},
])
save_table(cont.set_index("Option"), "container_options.csv")

# ====================================================== trailer departure plan (when trailers leave) + backward waves
SLOT_MIN = 25                                       # dock window: p90 dock time 22 min + buffer
DEP = [  # (time, carrier, trailers) - set around today's median departure per carrier (data), booked as slots
    ("10:30", "Ex-works pickup (AM)", 1), ("11:00", "DHL DSV run 1", 1),
    ("13:30", "Ex-works pickup (PM)", 1), ("14:00", "DHL Parcel NL run 1", 1), ("14:00", "Ex-works pickup (PM)", 1),
    ("14:30", "DHL DSV run 2", 1), ("15:00", "Customer carriers", 2),
    ("16:00", "DHL Parcel NL DACH", 1), ("16:15", "DHL Parcel NL run 2", 1), ("16:15", "DHL4YOU", 1),
    ("16:30", "DHL Connect & Return", 1), ("16:30", "DHL Parcel BE & LU", 1), ("16:45", "DHL Parcel EDC", 1),
]
def hm(t):
    h_, mm_ = t.split(":"); return int(h_) + int(mm_) / 60
win_list = []
for t, c, n in DEP:
    for _ in range(n):
        win_list.append((hm(t) - SLOT_MIN / 60, hm(t), c))
win_list.sort()
doors_free = [0.0] * OUT_DOORS; assign = []
for a, b, c in win_list:                            # greedy door assignment
    d = min(range(OUT_DOORS), key=lambda i: (doors_free[i] > a, doors_free[i]))
    assign.append((d, a, b, c)); doors_free[d] = max(doors_free[d], b)
plan_max = max_concurrent([w_[0] for w_ in win_list], [w_[1] for w_ in win_list])
WAVES = [("W1", "06:00", "09:30", "afternoon orders from the day before"),
         ("W2", "09:30", "12:45", "rest of the backlog + morning orders"),
         ("W3", "12:45", "15:15", "orders received before 12:00 (same-day parcel)")]
before_noon = float((orders["ORDER ARRIVE DATE"].dt.hour < 12).mean() * 100)
departures = pd.DataFrame([{"Departure": t, "Carrier": c, "Trailers": n,
                            "Fed by wave": "W1" if hm(t) < 12 else ("W2" if hm(t) < 15.5 else "W3")} for t, c, n in DEP])
save_table(departures.set_index("Departure"), "departure_plan.csv")

fig, ax = plt.subplots(figsize=(10.5, 4.2))
wc = {"W1": "#9db4fb", "W2": "#FFCC00", "W3": "#f2a6a6"}
for w_, a, b, txt in WAVES:
    ax.barh(OUT_DOORS + 0.9, hm(b) - hm(a), left=hm(a), height=0.7, color=wc[w_], edgecolor="white")
    ax.text((hm(a) + hm(b)) / 2, OUT_DOORS + 0.9, f"{w_} pick wave {a}-{b}", ha="center", va="center", fontsize=8.5, weight="bold")
for d, a, b, c in assign:
    col = RED if ("Parcel" in c or "DHL4YOU" in c or "Connect" in c) else ("#2b6cb0" if "DSV" in c else "#2f855a")
    ax.barh(d, b - a, left=a, height=0.55, color=col, edgecolor="white")
    short = {"Ex-works pickup (AM)": "Ex-works", "Ex-works pickup (PM)": "Ex-works", "DHL DSV run 1": "DSV", "DHL DSV run 2": "DSV",
             "DHL Parcel NL run 1": "NL", "DHL Parcel NL run 2": "NL", "DHL Parcel NL DACH": "DACH", "DHL4YOU": "4YOU",
             "DHL Connect & Return": "C&R", "DHL Parcel BE & LU": "BE-LU", "DHL Parcel EDC": "EDC", "Customer carriers": "Cust."}[c]
    ax.text((a + b) / 2, d + 0.40, short, ha="center", va="bottom", fontsize=6.8)
ax.set_yticks(list(range(OUT_DOORS)) + [OUT_DOORS + 0.9])
ax.set_yticklabels([f"Door S{i + 1}" for i in range(OUT_DOORS)] + ["Picking"], fontsize=9)
ax.set_xlim(6, 18.3); ax.set_xticks(range(6, 19)); ax.set_xticklabels([f"{h_:02d}:00" for h_ in range(6, 19)], fontsize=8)
ax.grid(axis="x"); ax.grid(axis="y", visible=False)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=RED, label="DHL Parcel routes"), Patch(color="#2b6cb0", label="DHL DSV"),
                   Patch(color="#2f855a", label="Ex-works / customer carriers")], loc="lower left", fontsize=8, frameon=False)
ax.set_ylim(-0.6, OUT_DOORS + 1.5)
ax.set_title(f"When trailers leave: departure slots on {OUT_DOORS} shipping doors, planned backwards into 3 pick waves "
             f"(max {plan_max} doors busy at once)", fontsize=10)
save_fig(fig, "departure_plan.png")
departure = {"slot_min": SLOT_MIN, "plan_max_doors_busy": plan_max, "trailers_planned": int(sum(n for _, _, n in DEP)),
             "waves": [{"wave": w_, "start": a, "end": b, "content": t} for w_, a, b, t in WAVES],
             "orders_before_noon_pct": round(before_noon, 0), "departures": departures.to_dict("records")}

# ====================================================== figures
fig, ax = plt.subplots(figsize=(8.6, 3.9))
x = np.arange(len(prof)); bw = 0.27
for i, (col, c) in enumerate(zip(prof.columns, [GREY, YEL, RED])):
    ax.bar(x + (i - 1) * bw, prof[col], bw, label=col, color=c, edgecolor="white", zorder=3)
ax.set_xticks(x); ax.set_xticklabels([f"{h:02d}:00" for h in prof.index], fontsize=8.5)
ax.set_ylabel("% of daily total"); ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.set_title("Orders arrive in the afternoon, are released at 16:00-17:00, and are picked next morning")
ax.annotate("08:00 pick peak =\nbacklog released at shift start", xy=(list(prof.index).index(8) + bw, prof.loc[8, "Lines picked"]),
            xytext=(list(prof.index).index(10), prof["Lines picked"].max() * 1.05),
            fontsize=8.5, arrowprops=dict(arrowstyle="->", color=INK), color=INK)
save_fig(fig, "order_release_profile.png")

fig, ax = plt.subplots(figsize=(8.2, 3.8))
cats = ["Today:\ntrailers parked at doors all day", "Future, no time slots:\nload just before collection",
        "Future, with carrier time slots:\nstage, then live-load"]
vals = [cur.quantile(.9), fut.quantile(.9), formula_doors]
cols = [GREY, YEL, RED]
xx = np.arange(3)
ax.bar(xx, vals, 0.55, color=cols, zorder=3, edgecolor="white")
for i, v in enumerate(vals):
    ax.text(xx[i], v + 0.3, f"{v:.0f}" if i < 2 else f"{v:.1f}", ha="center", fontsize=11, weight="bold", color=INK)
ax.axhline(OUT_DOORS, color=INK, ls="--", lw=1.2)
ax.text(2.42, OUT_DOORS + 0.3, f"{OUT_DOORS} doors planned (incl. 1 spare)", fontsize=9, ha="right", weight="bold")
ax.set_xticks(xx); ax.set_xticklabels(cats, fontsize=8.8); ax.set_ylabel("Doors busy at the same time (busy day, p90)")
ax.set_ylim(0, max(vals) * 1.25)
ax.set_title("Outbound doors needed — measured from 912 trailers (Q2 2025)")
save_fig(fig, "dock_outbound_doors.png")

update_metrics("dock_mhe", {
    "jungheinrich": JH, "geometry": {"mean_fork_height_m": round(mean_h, 2), "top_beam_m": round(top_beam, 2)},
    "cycle_times": cycle.to_dict("records"), "fleet": fleet.to_dict("records"), "fit_checks": fit.to_dict("records"),
    "inbound_doors": {"scenarios": in_rows, "doors_recommended": IN_DOORS, "doors_needed_base": IN_NEEDED_BASE,
                      "receiving_window_h": RECV_WINDOW, "door_util": DOOR_UTIL,
                      "trailer_door_h": round(door_trailer, 2), "container_door_h": round(door_container, 2)},
    "outbound_doors": out_summary, "carriers_trailers_per_day": carriers.head(10).to_dict(),
    "order_release": release, "turning_check": turning.to_dict("records"), "justification": just.to_dict("records"),
    "container_options": cont.to_dict("records"), "departure_plan": departure, "loose_zone": loose_zone,
    "load_checks": {"weight": LW, "long": LG, "tall": TL},
})

print("CYCLE TIMES"); print(cycle.to_string(index=False))
print("\nINBOUND DOORS"); print(inbound.to_string(index=False)); print("-> base needs", IN_NEEDED_BASE, "| recommended", IN_DOORS)
print("\nOUTBOUND", json.dumps(out_summary, indent=1, default=float))
print("\nFLEET"); print(fleet.to_string(index=False))
print("\nRELEASE", release)
print("\nLOOSE ZONE", loose_zone)
print("LOAD CHECKS", LW, LG, TL)
