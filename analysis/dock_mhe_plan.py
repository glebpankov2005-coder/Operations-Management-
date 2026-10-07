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
    "ETV 216i": {"role": "Reach truck - putaway, replenishment, full-pallet picks (double-deep via telescopic forks)",
                 "capacity_kg": 1600, "load_centre_mm": 600, "max_lift_mm": 10700, "ext_mast_mm": 11700,
                 "ast_mm": "2,631-2,785", "width_mm": 1270, "v_travel_kmh": 11, "v_travel_max_kmh": 14,
                 "v_lift_laden": 0.59, "v_lift_empty": 0.81, "v_lower": 0.56, "v_reach": 0.24, "reach_mm": 616,
                 "accel_s": 4.6, "battery": "Li-ion 51.2 V / 360 Ah, opportunity charging", "src": "S006"},
    "ECE 225":  {"role": "Horizontal order picker - batch picking onto 2 pallets / roll cages",
                 "capacity_kg": 2500, "fork_mm": 2400, "length_mm": 3670, "width_mm": 810,
                 "v_travel_kmh": 12.5, "battery": "24 V", "src": "S007"},
    "ERE 225":  {"role": "Rider pallet truck - unloading/loading trailers & containers, dock moves",
                 "capacity_kg": 2500, "fork_mm": 1000, "v_travel_kmh": 14, "battery": "Li-ion option (ERE 225i)",
                 "src": "S008"},
}

# ====================================================== Option B geometry (as warehouse_floorplan.py)
DEPTH = 70.0
RECV, OFF, RET, PACK, OUTB, FWD = 262, 250, 180, 450, 216, 500
dd_area, sel_area, CIRC = 3505, 728, 450
left_w = (OFF + RET + RECV) / DEPTH; right_w = (PACK + OUTB) / DEPTH
core_w = (dd_area + sel_area + FWD) / DEPTH; aisle = CIRC / (2 * DEPTH)
cx0 = left_w + aisle; cx1 = cx0 + core_w
fwd_h = FWD / core_w; rack_y0, rack_y1 = fwd_h + 1.5, DEPTH - 1.5
cross_y = (rack_y0 + rack_y1) / 2
BLOCK, AISLEW = 2.6, 3.0; pitch = BLOCK + AISLEW
n_mod = int((core_w - AISLEW) // pitch); start = cx0 + (core_w - (n_mod * pitch - AISLEW)) / 2
aisle_x = np.array([start + m * pitch + BLOCK + AISLEW / 2 for m in range(n_mod - 1)])
la, ra = left_w + aisle / 2, cx1 + aisle / 2              # perimeter aisles (truck routes)
rvh, uh = RECV / left_w, OUTB / right_w
LEVELS, PITCH_M, BASE_M = 8, 1.41, 0.15                   # A011
lvl_h = BASE_M + PITCH_M * np.arange(LEVELS)              # fork heights per level
mean_h = float(lvl_h.mean()); top_beam = float(lvl_h.max())

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
    """Reach-truck cycle (s): fixed handling + travel round trip + lift/lower + reach + double-deep."""
    e = JH["ETV 216i"]
    v = e["v_travel_kmh"] / 3.6
    t_travel = 2 * d_oneway / v + 4 * e["accel_s"]        # 2 legs each way, accel/decel penalty per leg
    t_lift = mean_h / e["v_lift_laden"] + mean_h / e["v_lower"]
    t_reach = 2 * 2 * (e["reach_mm"] / 1000) / e["v_reach"]  # reach out + in, at pick-up and at deposit
    t_dd = 0.5 * 12.0                                       # 50% rear positions: telescopic fork +12 s (A021)
    t_fixed = 45.0                                          # scan, fork entry, fine positioning, confirm (A021)
    return t_fixed + t_travel + t_lift + t_reach + t_dd

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
lab = {r["Process"]: r for r in CP["labour_table"]}
ECE_h = lab["Each picking"]["Hours (peak)"] + lab["Case picking"]["Hours (peak)"]
ECE_h_avg = lab["Each picking"]["Hours (avg)"] + lab["Case picking"]["Hours (avg)"]
cont_pallets_pk = MEAS["inbound_loads_day"] * loose * INP["containers_peak"] / max(INP["containers_avg"], 1)
out_pal_pk = MEAS["outbound_pallets_max"]
ERE_h = (pal_peak * t_unload + cont_pallets_pk * t_unload
         + out_pal_pk * t_load + np.ceil(MEAS["outbound_cartons_day"] * M["peak"]["units"]["peak_over_avg"] / 20) * t_cage) / 60
ERE_h_avg = (pal_avg * t_unload + MEAS["inbound_loads_day"] * loose * t_unload
             + MEAS["outbound_pallets_day"] * t_load + np.ceil(MEAS["outbound_cartons_day"] / 20) * t_cage) / 60
avail = NET_H * MHE_UTIL
fleet = []
for model, h_avg, h_pk, task, spare in [
    ("ETV 216i", ETV_h_avg, ETV_h, "Putaway + replenishment + full-pallet picks", 1),
    ("ECE 225", ECE_h_avg, ECE_h, "Case & each batch picking (2 pallets/roll cages per trip)", 0),
    ("ERE 225", ERE_h_avg, ERE_h, "Unload trailers/containers, load outbound, dock moves", 1)]:   # +1: one per dock side
    need = max(1, int(np.ceil(h_pk / avail)))
    fleet.append({"Model": f"Jungheinrich {model}", "Task": task,
                  "Equip-h/day avg": round(h_avg, 1), "Equip-h/day peak": round(h_pk, 1),
                  "Units required (peak)": need, "Units recommended": need + spare})
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
st = all_storage()["ASSA STORAGE DETAILS (01-06-2025).xlsx"].drop_duplicates("PART")
w = pd.to_numeric(st["PA WGT"], errors="coerce"); w = w[(w > 0) & (w < 9999)]
fit = pd.DataFrame([
    {"Check": "Working aisle (reach aisle 3.0 m)", "Requirement": "ETV 216i Ast 2,631-2,785 mm", "Result": "OK - 0.2-0.4 m margin"},
    {"Check": f"Top beam {top_beam:.2f} m (8 levels x {PITCH_M} m)", "Requirement": "Max lift 10.7 m", "Result": f"OK - {10.7 - top_beam:.2f} m spare"},
    {"Check": "Clear height 12.2 m", "Requirement": "Extended mast 11.7 m at max lift", "Result": "OK - 0.5 m clearance"},
    {"Check": f"Pallet weight p95 {w.quantile(.95):.0f} kg / p99 {w.quantile(.99):.0f} kg", "Requirement": "1,600 kg @ 600 mm", "Result": f"OK for {100 * (w <= 1600).mean():.1f}% of SKUs; >1 t pallets slotted on low levels"},
    {"Check": "Batch picking 2 orders per trip", "Requirement": "ECE 225: 2,400 mm forks, 2,500 kg", "Result": "OK - 2 EUR pallets / roll cages"},
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
    "order_release": release,
})

print("CYCLE TIMES"); print(cycle.to_string(index=False))
print("\nINBOUND DOORS"); print(inbound.to_string(index=False)); print("-> base needs", IN_NEEDED_BASE, "| recommended", IN_DOORS)
print("\nOUTBOUND", json.dumps(out_summary, indent=1, default=float))
print("\nFLEET"); print(fleet.to_string(index=False))
print("\nRELEASE", release)
