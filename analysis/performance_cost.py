"""
DELIVERABLE 3 - PERFORMANCE OVERVIEW: KPIs, CAPEX, OPEX, today vs future, sensitivity, volume stress test.

Every number comes from the earlier analysis (phase1_metrics.json) or from the cost register below
(COST, mirrored in data/assumptions.json A030-A045 with sources S018-S025). Nothing here is a quote:
all prices are public benchmarks or labelled assumptions, to be replaced by DHL / supplier quotes.

Run after warehouse_floorplan.py, picking_plan.py, capacity_plan.py, dock_mhe_plan.py, design_evaluation.py.
Outputs: outputs/tables/d3_*.csv, outputs/figures/d3_*.png, metrics section "performance_cost".
"""
import json, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from load_data import combined_outbound
from _util import save_table, save_fig, update_metrics, REPORTS
from geometry import aisle_x, storage_aisle_len, core_w, LEVELS

M = json.load(open(os.path.join(REPORTS, "phase1_metrics.json"), encoding="utf-8"))
CP, DM, PK, LAY, DE = M["capacity_plan"], M["dock_mhe"], M["picking"], M["layout"], M["design_evaluation"]
MEAS = CP["measured"]
BLUE, ORANGE, AQUA, YELLOW, GREY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#a3abb8", "#1f2937"

# ======================================================================= cost register
# value, low, high, unit, assumption id, source / basis
COST = {
    "labour_rate":   (20.0, 20.0, 28.0, "EUR per paid hour (operative)", "A030",
                      "teacher feedback (S026): EUR 20/h for a warehouse operator; high end EUR 28/h = CAO wage (S019) x employer "
                      "premiums (S018) x holiday pay x paid-not-worked time"),
    "lead_rate":     (27.0, 27.0, 38.0, "EUR per paid hour (team leader)", "A030", "operator rate x 1.35 (CAO scale F-G vs B-C, S019)"),
    "admin_rate":    (24.0, 24.0, 33.0, "EUR per paid hour (inventory control / admin)", "A030", "operator rate x 1.2"),
    "paid_h_shift":  (8.0, 8.0, 8.0, "paid hours per shift", "A015", "7.5 productive + breaks"),
    "days_year":     (244, 244, 244, "working days per year", "A031", "61 operating days measured in Q2 2025 x 4"),
    "indirect_fte":  (1.5, 1.0, 2.0, "FTE", "A032", "1 team leader (span ~1:9 at peak) + 0.5 inventory control / WMS admin"),
    "rack_pp":       (130.0, 80.0, 200.0, "EUR per pallet position, installed", "A033",
                      "EU selective racking EUR 80-140/position equipment (S020) + 30-50% install; installed 75-150 (S020); 12 m frames -> upper half"),
    "long_bay_pp":   (160.0, 100.0, 250.0, "EUR per long-goods position (4.5 m beams)", "A033", "assumption: ~1.25x a standard position (longer, heavier beams)"),
    "shelf_bay":     (200.0, 153.0, 245.0, "EUR per bin-shelving bay (1.0 x 0.6 x 2.5 m)", "A042", "Manutan shelving EUR 153-245 per section (S030)"),
    "vlm_unit":      (60000.0, 48000.0, 90000.0, "EUR per Kardex Shuttle XP 500 incl. installation (compared option)", "A042",
                      "new Shuttle XP 500 (2,450 x 864 trays) EUR 48,000 (S027); 4,050 mm trays + installation -> EUR 60,000 assumed"),
    "vlm_slot":      (8.0, 6.0, 12.0, "EUR per half-bin slot (bin + divider)", "A042", "half of a 600x400 tote EUR 14.56-19.95 (S025)"),
    "vlm_integr":    (10000.0, 5000.0, 20000.0, "EUR one-off", "A042", "assumption: WMS link to the lift controller + light pointer"),
    "rack_reuse":    (25.0, 15.0, 40.0, "EUR per position to dismantle + re-assemble existing racking", "A033",
                      "assumption: ~20% of a new installed position; only if today's racking fits the new layout (to confirm with DHL)"),
    "rack_protect":  (0.05, 0.03, 0.08, "share of racking cost", "A033", "end-of-aisle guards, upright protectors, load signs (EN 15635, S015)"),
    "flow_bay":      (1800.0, 1100.0, 2300.0, "EUR per carton-flow bay (2 m, 5 levels)", "A034",
                      "new USD 1,200-2,500 per bay (S025) at ~0.9 EUR/USD; used EUR 650/bay (S025) = floor"),
    "ptl_slot":      (150.0, 60.0, 200.0, "EUR per put-to-light slot", "A035", "USD 60-200 per station (S025)"),
    "ptl_integr":    (12000.0, 5000.0, 30000.0, "EUR one-off", "A035", "installation + WMS integration USD 3,000-18,000 + software (S025)"),
    "rf_unit":       (1500.0, 450.0, 2300.0, "EUR per RF terminal incl. cradle", "A036", "Zebra MC3300 listings EUR 435-2,326 + cradle EUR 182 (S025)"),
    "pack_station":  (2500.0, 1500.0, 4000.0, "EUR per pack station", "A036", "assumption: bench, scale, label printer"),
    "trolley":       (433.0, 280.0, 600.0, "EUR per pick trolley", "A036", "Fetra picking trolley EUR 432.86 net (S025)"),
    "tote":          (16.0, 14.0, 20.0, "EUR per tote 600x400x320", "A036", "EUR 14.56-19.95 (S025)"),
    "wrapper":       (3849.0, 3000.0, 9000.0, "EUR per semi-automatic stretch wrapper", "A036", "Vogel Starter EUR 3,849 new (S025)"),
    "conveyor":      (1250.0, 1000.0, 2500.0, "EUR per extendable roller conveyor (4.5 m)", "A036", "Cromwell GBP 1,049 ex VAT (S025)"),
    "roll_cage":     (150.0, 100.0, 250.0, "EUR per roll cage", "A036", "assumption"),
    "wms_config":    (25000.0, 10000.0, 50000.0, "EUR one-off", "A037", "assumption: WMS set-up of waves, put-wall, slotting & putaway rules (~25 consultant days)"),
    "contingency":   (0.10, 0.05, 0.20, "share of CAPEX", "A037", "planning allowance"),
    "lease_etv":     (900.0, 495.0, 1550.0, "EUR per month, full-service lease", "A038",
                      "Dutch reach-truck lease offers EUR 350-495/month all-in (72 months) up to rental EUR 1,100-1,550/month (S021); "
                      "10.7 m Li-ion truck -> upper half"),
    "lease_eje":     (150.0, 100.0, 250.0, "EUR per month, full-service lease", "A038", "assumption: Li-ion pallet truck new ~EUR 2,500-3,500 (S025) over 72 months + service"),
    "lease_ere":     (350.0, 250.0, 500.0, "EUR per month, full-service lease", "A038", "assumption: rider pallet truck, between pallet truck and reach truck"),
    "kwh_truck_h":   (4.0, 3.0, 6.0, "kWh per truck operating hour (ETV); 1.5 for pallet trucks", "A039", "assumption"),
    "power_price":   (0.2046, 0.17, 0.25, "EUR per kWh", "A039", "Eurostat nrg_pc_205, NL non-household 500-2,000 MWh, H1 2025 (S022)"),
    "rack_inspect":  (2500.0, 1500.0, 4000.0, "EUR per year", "A040", "assumption: 1 expert inspection per year (EN 15635, S015)"),
    "it_support":    (0.15, 0.10, 0.20, "share of IT CAPEX per year", "A040", "assumption: device repair, licences, spares"),
    "life_rack":     (15, 15, 15, "years", "A041", "straight-line depreciation"),
    "life_equip":    (7, 7, 7, "years", "A041", "straight-line depreciation"),
    "life_it":       (5, 5, 5, "years", "A041", "straight-line depreciation"),
}
C = {k: v[0] for k, v in COST.items()}
DAYS = C["days_year"]

# ======================================================================= quantities from the design
POS = LAY["positions_total"]; POS_LONG = LAY["positions_long"]
VLM = PK["small_parts"]                          # small-parts storage (bin shelving; Kardex lift compared)
fleet = {f["Model"].replace("Jungheinrich ", ""): f for f in DM["fleet"]}
n_etv, n_eje, n_ere = (fleet[m]["Units recommended"] for m in ("ETV 216i", "EJE 120i", "ERE 225"))
tro = [e for e in PK["equipment"] if e["Item"].startswith("Pick trolley")][0]["Planned"]
totes = [e for e in PK["equipment"] if e["Item"].startswith("Totes")][0]["Planned"]
labour = pd.DataFrame(CP["labour_table"]).set_index("Process")
dhl = labour[labour["DHL staff"]]
fte_avg, fte_pk = float(dhl["FTE avg"].sum()), float(dhl["FTE peak"].sum())
seg = {r["segment"]: r for r in PK["segments"]}
LINES_PEAKF = M["peak"]["lines"]["peak_over_avg"]
WAVES = len(DM["departure_plan"]["waves"])

# fast-pick faces: one row of 2 m carton-flow bays along the module front (A/B items), 5 levels x ~6 lanes
flow_bays = int((core_w - 4.0) // 2.0)
flow_lanes = flow_bays * 5 * 6
# put-to-light wall: one slot per small order open in a wave on the peak day (+20%)
small_orders_wave_pk = seg["small"]["orders_day"] * LINES_PEAKF / WAVES
ptl_slots = int(np.ceil(small_orders_wave_pk * 1.2 / 10) * 10)
# RF terminals: one per person on the peak day + 20% spare
rf_units = int(np.ceil(np.ceil(fte_pk + C["indirect_fte"]) * 1.2))
pack_stations = int(np.ceil(float(labour.loc["Packing / consolidation", "FTE peak"])))
roll_cages = int(np.ceil(MEAS["outbound_cartons_day"] * M["peak"]["units"]["peak_over_avg"] / 20 * 1.25))
loose = DM["loose_zone"]
containers_year = CP["inbound_pattern"]["containers_avg"] * DAYS

# ======================================================================= CAPEX
capex_rows = [
    ("Storage", "Single-deep pallet racking (incl. installation)", POS - POS_LONG, "positions", C["rack_pp"], "A033 / S020"),
    ("Storage", "Long-goods racking, 4.5 m bays (2.05 m pallets)", POS_LONG, "positions", C["long_bay_pp"], "A033"),
    ("Storage", "Rack protection, end guards, load signs", 1, "lot", C["rack_protect"] * POS * C["rack_pp"], "A033 / S015"),
    ("Small-item storage", "Bin shelving for small parts (next to the put-wall)", VLM["shelf_bays"], "bays", C["shelf_bay"], "A042 / S030"),
    ("Small-item storage", "Half-bins and dividers", VLM["shelf_bays"] * VLM["slots_per_bay"], "slots", C["vlm_slot"], "A042 / S025"),
    ("Picking", "Carton-flow bays, fast-pick area", flow_bays, "bays", C["flow_bay"], "A034 / S025"),
    ("Picking", "Pick trolleys (3-tier, 6 totes)", tro, "trolleys", C["trolley"], "S011 / S025"),
    ("Picking", "Totes 600 x 400", totes, "totes", C["tote"], "S025"),
    ("Sorting & packing", "Put-to-light wall (slots)", ptl_slots, "slots", C["ptl_slot"], "A035 / S025"),
    ("Sorting & packing", "Put-to-light installation + WMS link", 1, "lot", C["ptl_integr"], "A035 / S025"),
    ("Sorting & packing", "Pack stations (bench, scale, label printer)", pack_stations, "stations", C["pack_station"], "A036"),
    ("Sorting & packing", "Stretch wrapper (packing)", 1, "units", C["wrapper"], "S025"),
    ("Sorting & packing", "Roll cages for parcels", roll_cages, "cages", C["roll_cage"], "A036"),
    ("Loose-container zone", "Extendable roller conveyor (into the container)", 2, "units", C["conveyor"], "S025"),
    ("Loose-container zone", "Stretch wrapper (newly built pallets)", 1, "units", C["wrapper"], "S025"),
    ("IT", "RF terminals with cradles", rf_units, "units", C["rf_unit"], "A036 / S025"),
    ("IT", "WMS set-up: waves, put-wall, slotting, putaway rules", 1, "lot", C["wms_config"], "A037"),
]
# one-off move-in: every load in stock is moved once into its new slot (ETV cycle + driver)
t_put = {c["Move"]: c for c in DM["cycle_times"]}["Putaway (receiving -> reserve)"]["Cycle min"]
loads_now = max(s["loads_LODNUM"] for s in M["inventory"]["snapshots"])
move_h = loads_now * t_put / 60
move_cost = move_h * (C["labour_rate"] + C["lease_etv"] * 12 / (DAYS * 7.5))
capex_rows.append(("One-off", "Move-in / re-slotting (each load moved once)", loads_now, "loads",
                   move_cost / loads_now, "ETV cycle model + A030"))
subtotal = sum(r[2] * r[4] for r in capex_rows)
capex_rows.append(("Contingency", f"Contingency {C['contingency']:.0%}", 1, "lot", subtotal * C["contingency"], "A037"))
capex = pd.DataFrame(capex_rows, columns=["Group", "Item", "Qty", "Unit", "Unit price EUR", "Source"])
capex["Total EUR"] = capex["Qty"] * capex["Unit price EUR"]
CAPEX = float(capex["Total EUR"].sum())
life = {"Storage": C["life_rack"], "Small-item storage": C["life_equip"], "Picking": C["life_equip"], "Sorting & packing": C["life_equip"],
        "Loose-container zone": C["life_equip"], "IT": C["life_it"], "One-off": C["life_equip"], "Contingency": C["life_equip"]}
capex["Life (yrs)"] = capex["Group"].map(life)
capex["Depreciation EUR/yr"] = capex["Total EUR"] / capex["Life (yrs)"]
DEPR = float(capex["Depreciation EUR/yr"].sum())
it_capex = float(capex.loc[capex["Group"] == "IT", "Total EUR"].sum() + capex.loc[capex["Item"].str.startswith("Put-to-light"), "Total EUR"].sum())
save_table(capex.set_index("Item"), "d3_capex.csv")
capex_groups = capex.groupby("Group", sort=False)["Total EUR"].sum()

# ======================================================================= OPEX (per year)
def paid_hours(prod_h_day):
    return prod_h_day / 7.5 * C["paid_h_shift"] * DAYS
dir_h_day = float(dhl["Hours (avg)"].sum())
loose_h_day = loose["crew"] * loose["hours_per_container"] * CP["inbound_pattern"]["containers_avg"]
etv_h = fleet["ETV 216i"]["Equip-h/day avg"]; pt_h = fleet["EJE 120i"]["Equip-h/day avg"] + fleet["ERE 225"]["Equip-h/day avg"]
opex_rows = [
    ("Labour", "Direct DHL labour (receiving, putaway, replenishment, picking, packing, loading)",
     paid_hours(dir_h_day), "paid h", C["labour_rate"], "capacity plan (D2 §6) x A030"),
    ("Labour", "Loose-container zone crew (2 people x 3 h per container)", paid_hours(loose_h_day), "paid h",
     C["labour_rate"], "A019 x A030 (or contractor fee, see break-even)"),
    ("Labour", "Team leader + inventory control / admin", C["indirect_fte"] * C["paid_h_shift"] * DAYS, "paid h",
     (C["lead_rate"] + 0.5 * C["admin_rate"]) / 1.5, "A032 x A030"),
    ("Machinery", f"ETV 216i reach truck lease ({n_etv})", n_etv * 12, "truck-months", C["lease_etv"], "A038 / S021"),
    ("Machinery", f"EJE 120i pallet truck lease ({n_eje})", n_eje * 12, "truck-months", C["lease_eje"], "A038"),
    ("Machinery", f"ERE 225 rider pallet truck lease ({n_ere})", n_ere * 12, "truck-months", C["lease_ere"], "A038"),
    ("Machinery", "Electricity for trucks", (etv_h * C["kwh_truck_h"] + pt_h * 1.5) * DAYS, "kWh", C["power_price"], "A039 / S022"),
    ("Upkeep", "Rack inspection (EN 15635) and repairs", 1, "per year", C["rack_inspect"], "A040 / S015"),
    ("Upkeep", "IT support, licences, device spares", 1, "per year", C["it_support"] * it_capex, "A040"),
]
opex = pd.DataFrame(opex_rows, columns=["Group", "Item", "Qty / yr", "Unit", "Unit cost EUR", "Source"])
opex["Total EUR/yr"] = opex["Qty / yr"] * opex["Unit cost EUR"]
OPEX = float(opex["Total EUR/yr"].sum())
save_table(opex.set_index("Item"), "d3_opex.csv")
opex_groups = opex.groupby("Group", sort=False)["Total EUR/yr"].sum()
ANNUAL = OPEX + DEPR

lines_y = M["peak"]["lines"]["mean"] * DAYS
orders_y = M["peak"]["orders"]["mean"] * DAYS
inb_y = MEAS["inbound_loads_day"] * DAYS
unit_cost = {"per_order_line": ANNUAL / lines_y, "per_order": ANNUAL / orders_y,
             "per_inbound_pallet": ANNUAL / inb_y, "per_position_month": ANNUAL / POS / 12,
             "labour_share_pct": float(opex_groups.get("Labour", 0) / ANNUAL * 100)}
loose_cost_container = float(opex.loc[opex["Item"].str.startswith("Loose"), "Total EUR/yr"].iloc[0]) / containers_year

# ======================================================================= today vs future (main design levers)
# Same pick-time model and rates as D2; 'today' = how the data says the operation runs now:
#   * no batching - one order per tour, * stock not placed by demand (WMS class agrees with demand for only
#   48.6% of SKUs) -> picks spread over the whole reserve, * all orders released at once -> staff for the 08:00 peak.
pp = PK["params"]
A = len(aisle_x); LB = storage_aisle_len; X_PD = float(aisle_x[-1]) + 5.0
RNG = np.random.default_rng(11)
def walk_spread(n, sims=4000):
    """Expected walk (m) for a tour of n picks spread over all reserve aisles; best of S-shape / return."""
    out = []
    for _ in range(sims):
        m_ = max(1, RNG.poisson(n)) if n < 8 else int(round(n))
        a_ = RNG.integers(0, A, m_); y_ = RNG.uniform(0, LB, m_)
        xs = aisle_x[a_]; horiz = 2 * (X_PD - xs.min()); picked = np.unique(a_); k = len(picked)
        ymax = {a: y_[a_ == a].max() for a in picked}
        ret = horiz + sum(2 * v for v in ymax.values())
        s_ = horiz + (k - 1 if k % 2 else k) * LB + (2 * ymax[picked[-1]] if k % 2 else 0)
        out.append(min(ret, s_))
    return float(np.mean(out))
n_small = seg["small"]["lines_day"] / seg["small"]["orders_day"]
n_large = PK["large_orders"]["lines_per_order"]
t_small_today = (pp.get("t_setup_small", 90.0) + walk_spread(n_small) / pp["v_walk"] + n_small * pp["t_line_small"]) * pp["delay"]
t_large_today = (180.0 + walk_spread(n_large) / pp["v_eje"] + n_large * pp["t_line_large"]) * pp["delay"]
pick_today_h = (seg["small"]["orders_day"] * t_small_today + seg["large"]["orders_day"] * t_large_today) / 3600
pick_future_h = sum(r["Picker-h avg"] for r in PK["small_orders"]) + PK["large_orders"]["picker_h_avg"] + VLM["picker_h_avg"]
peak_ratio = DM["order_release"]["pick_peak_over_mean_active_hour"]
pick_today_staffed_h = pick_today_h * peak_ratio                        # staffed for the 08:00 release peak
levers = pd.DataFrame([
    {"Lever": "Batch picking + demand-based slotting (fast-pick area)", "Today h/day": pick_today_h, "Future h/day": pick_future_h},
    {"Lever": "Wave release instead of one evening release (no 08:00 peak staffing)",
     "Today h/day": pick_today_staffed_h - pick_today_h, "Future h/day": 0.0},
])
levers["Saved h/day"] = levers["Today h/day"] - levers["Future h/day"]
levers["Saved EUR/yr"] = levers["Saved h/day"].apply(paid_hours) * C["labour_rate"]
SAVING = float(levers["Saved EUR/yr"].sum())
PAYBACK = CAPEX / SAVING if SAVING > 0 else float("inf")
# if DHL can re-use the racking already standing in Bemmel (re-assembled to the new layout), only the rest is new
rack_items = capex["Item"].str.startswith(("Single-deep pallet racking", "Long-goods racking", "Rack protection"))
CAPEX_REUSE = float((capex.loc[~rack_items & (capex["Group"] != "Contingency"), "Total EUR"].sum()
                     + POS * C["rack_reuse"]) * (1 + C["contingency"]))
PAYBACK_REUSE = CAPEX_REUSE / SAVING if SAVING > 0 else float("inf")
# the labour saving comes from the PROCESS changes (batching, fast-pick area, put-wall, waves); racks and lifts are
# capacity (needed to store the stock), so the process part is paid back on its own
proc_items = capex["Item"].str.startswith(("Carton-flow", "Pick trolleys", "Totes", "Put-to-light", "WMS set-up", "RF terminals"))
CAPEX_PROCESS = float(capex.loc[proc_items, "Total EUR"].sum() * (1 + C["contingency"]))
PAYBACK_PROCESS = CAPEX_PROCESS / SAVING if SAVING > 0 else float("inf")

# ---- small-item storage: compare the options for the slow small SKUs (feedback 2: Kardex or other high-density)
SHELF_M2, SHELF_RATE, LIFT_RATE = 1.1, 50.0, 75.0                     # m2 per bay incl. aisle; lines/h shelving / lift (S028)
slots_ = VLM["slots_needed"]; lines_v = VLM["lines_day"]; bays = VLM["shelf_bays"]
def lab(rate): return paid_hours(lines_v / rate) * C["labour_rate"]
small_opts = pd.DataFrame([
    {"Option": "Keep in pallet racks (today)", "Floor m²": round(VLM["freed_rack_locations"] * LAY["dd_area_m2"] / POS, 0),
     "Pallet positions used": VLM["freed_rack_locations"], "CAPEX EUR": VLM["freed_rack_locations"] * C["rack_pp"],
     "Pick rate lines/h": PK["small_orders"][1]["Lines/h"], "Picking EUR/yr": lab(PK["small_orders"][1]["Lines/h"]),
     "Notes": "one 1 m³ pallet location for a few litres of stock; long walks in the reserve aisles"},
    {"Option": "Bin shelving next to the put-wall (chosen)", "Floor m²": round(bays * SHELF_M2, 0), "Pallet positions used": 0,
     "CAPEX EUR": bays * C["shelf_bay"] + bays * VLM["slots_per_bay"] * C["vlm_slot"], "Pick rate lines/h": SHELF_RATE, "Picking EUR/yr": lab(SHELF_RATE),
     "Notes": f"{bays} bays, 2.5 m high; cheapest; fits in the packing area's spare floor; items go straight into the put-wall"},
    {"Option": "Kardex Shuttle XP 500 lifts", "Floor m²": round(VLM["lift_units"] * 22.0, 0), "Pallet positions used": 0,
     "CAPEX EUR": VLM["lift_units"] * C["vlm_unit"] + VLM["lift_units"] * VLM["trays"] * VLM["slots_per_tray"] * C["vlm_slot"] + C["vlm_integr"],
     "Pick rate lines/h": LIFT_RATE, "Picking EUR/yr": lab(LIFT_RATE),
     "Notes": f"{VLM['lift_units']} lifts ~10 m high; 3x denser, light pointer; but busy only ~{lines_v / (VLM['lift_units'] * 7.5 * LIFT_RATE):.0%} of the day"},
])
small_opts["Yearly cost EUR"] = small_opts["CAPEX EUR"] / C["life_equip"] + small_opts["Picking EUR/yr"]
save_table(small_opts.set_index("Option"), "d3_small_item_options.csv")
save_table(levers.set_index("Lever"), "d3_levers.csv")

# ======================================================================= order lead time: today (measured) vs future (modelled)
ob = combined_outbound()
for c_ in ["ORDER ARRIVE DATE", "TRAILER DISPATCED DATE"]:
    ob[c_] = pd.to_datetime(ob[c_], errors="coerce")
od = ob.groupby("ORDER NO").agg(arr=("ORDER ARRIVE DATE", "min"), disp=("TRAILER DISPATCED DATE", "max"),
                                carrier=("CARRIER NAME", "first")).dropna(subset=["arr"])
od["today_h"] = (od["disp"] - od["arr"]).dt.total_seconds() / 3600
od.loc[(od["today_h"] < 0) | (od["today_h"] > 24 * 30), "today_h"] = np.nan
def slots_for(carrier):
    c_ = str(carrier).upper()
    if "EXWORK" in c_: return [10.5, 13.5, 14.0]
    if "DSV" in c_: return [11.0, 14.5]
    if "DACH" in c_: return [16.0]
    if "CONNECT" in c_: return [16.5]
    if "BEL" in c_: return [16.5]
    if "EDC" in c_: return [16.75]
    if "DHL4YOU" in c_: return [16.25]
    if "PARCEL" in c_: return [14.0, 16.25]
    return [15.0]                                                     # customer carriers
WAVE_END = {"W1": 9.5, "W2": 12.75, "W3": 15.25}
PACK_H = 0.75                                                         # pack + stage after the wave
def next_workday(d):
    d = d + pd.Timedelta(days=1)
    while d.weekday() >= 5: d += pd.Timedelta(days=1)
    return d
def future_dispatch(arr, carrier):
    day = arr.normalize(); h = arr.hour + arr.minute / 60
    if day.weekday() >= 5 or h >= 12.0:                               # weekend or after 12:00 -> next working day, wave 1
        day = next_workday(day) if not (day.weekday() >= 5 and False) else day
        while day.weekday() >= 5: day += pd.Timedelta(days=1)
        wave = "W1"
    elif h < 6.0: wave = "W1"
    elif h < 9.5: wave = "W2"
    else: wave = "W3"
    ready = WAVE_END[wave] + PACK_H
    for _ in range(10):
        later = [s for s in slots_for(carrier) if s >= ready]
        if later:
            return day + pd.Timedelta(hours=later[0])
        day = next_workday(day); ready = 0
    return pd.NaT
od["future_disp"] = [future_dispatch(a, c_) for a, c_ in zip(od["arr"], od["carrier"])]
od["future_h"] = (od["future_disp"] - od["arr"]).dt.total_seconds() / 3600
def same_day(arr, disp): return (disp.dt.normalize() == arr.dt.normalize())
lt = {"orders": int(od["today_h"].notna().sum()),
      "today_median_h": round(float(od["today_h"].median()), 1), "today_mean_h": round(float(od["today_h"].mean()), 1),
      "today_p90_h": round(float(od["today_h"].quantile(.9)), 1),
      "today_same_day_pct": round(float(same_day(od["arr"], od["disp"])[od["today_h"].notna()].mean() * 100), 0),
      "today_within_24h_pct": round(float((od["today_h"] <= 24).mean() * 100), 0),
      "future_median_h": round(float(od["future_h"].median()), 1), "future_mean_h": round(float(od["future_h"].mean()), 1),
      "future_p90_h": round(float(od["future_h"].quantile(.9)), 1),
      "future_same_day_pct": round(float(same_day(od["arr"], od["future_disp"]).mean() * 100), 0),
      "future_within_24h_pct": round(float((od["future_h"] <= 24).mean() * 100), 0)}

# ======================================================================= KPI set (our own design KPIs + the W3 standard ones)
snaps = M["inventory"]["snapshots"]
occ_mean = float(np.mean([s["occupied_locations"] for s in snaps])); occ_peak = max(s["occupied_locations"] for s in snaps)
growth_q = (snaps[-1]["occupied_locations"] / snaps[0]["occupied_locations"]) ** (3 / 2) - 1   # 2 months -> per quarter
rack_need = occ_peak - VLM["freed_rack_locations"]                    # small slow SKUs leave the racks for the lifts
months_headroom = np.log(POS / rack_need) / np.log(1 + growth_q) * 3
months_headroom_12 = np.log((POS + LAY["positions_12th_module"]) / rack_need) / np.log(1 + growth_q) * 3
w3 = {k["KPI (W3)"]: k for k in DE["kpis"]}
picked_lines = seg["small"]["lines_day"] + seg["large"]["lines_day"]
pick_rate = picked_lines / pick_future_h
direct_lph = M["peak"]["lines"]["mean"] / dir_h_day
outd = DM["outbound_doors"]; LZ = DM["loose_zone"]; OA = DM["outbound_area"]
etv_u, eje_u, ere_u = (fleet[m]["Utilisation avg %"] for m in ("ETV 216i", "EJE 120i", "ERE 225"))
lg_ = PK["large_orders"]
fast_lines = PK["small_orders"][0]["Lines/day"] + lg_["lines_fast_pick"] * lg_["orders_day"]
fast_hit = fast_lines / picked_lines
walk_m = (sum(r["Walk per tour (m)"] * r["Tours/day"] for r in PK["small_orders"]) + lg_["walk_per_order_m"] * lg_["orders_day"])
walk_per_line = walk_m / picked_lines
lift_area = VLM["shelf_bays"] * SHELF_M2
sku_density_lift = VLM["skus"] / lift_area
sku_density_rack = VLM["freed_rack_locations"] / (VLM["freed_rack_locations"] * LAY["dd_area_m2"] / POS) * 1.0   # 1 SKU per location
lift_util = VLM["lines_day"] / VLM["rate_lines_h"]                  # picker-hours per day at the shelving
cont_h = DM["inbound_doors"]["container_door_h"]
kpis = [
    # group, KPI, type, how we calculate it, today (data), future (design), target
    ("Space", "Rack fill at peak", "own", "pallet locations used at the peak ÷ rack positions",
     f"{occ_peak:,} locations used", f"{rack_need / POS:.0%} ({rack_need:,} of {POS:,}; small parts moved to bin shelving)", "≤ 90%"),
    ("Space", "Storage headroom", "own", "months until the racks are full at the Apr–Jun growth rate",
     f"+{(snaps[-1]['occupied_locations'] / snaps[0]['occupied_locations'] - 1):.0%} locations in 2 months",
     f"~{months_headroom:.0f} months (~{months_headroom_12:.0f} with a 12th module)", "≥ 12 months"),
    ("Space", "Small-item density", "own", "SKUs stored per m² of floor",
     f"~{sku_density_rack:.1f} SKUs/m² (one pallet location each)", f"~{sku_density_lift:.0f} SKUs/m² in bin shelving", "≥ 5× better"),
    ("Space", "Floor area used", "own", "zones + aisles ÷ 7,000 m²", "—", f"{LAY['total_area_m2']:,} m² ({LAY['pct_of_7000']:.0f}%)", "≤ 7,000 m²"),
    ("Inbound", "Dock-to-stock time", "W3", "truck at the door → pallet in its location",
     "big China receipts take 1–3 days to book in", w3["Dock-to-stock time"]["Expected"], "< 3.5 h (S023)"),
    ("Inbound", "Containers unpacked inside their zone", "own", "% of containers whose unpacking fits the 190 m² zone",
     "—", f"{LZ['share_fit_zone_pct']:.0f}% (another {LZ['share_fit_with_r2_pct'] - LZ['share_fit_zone_pct']:.0f}% by lending door R2)", "≥ 90%"),
    ("Inbound", "Container door time", "own", "dock-on + unpack + palletise per 40 ft container", "—", f"~{cont_h:.1f} h", "≤ 4 h"),
    ("Inbound", "Put-away cycle time", "W3", "minutes per pallet, reach truck", "—", w3["Put-away cycle time"]["Expected"], "≤ 3 min"),
    ("Picking", "Pick rate", "W3", "order lines per picker-hour", "—",
     f"~{pick_rate:.0f} lines/h (fast-pick {PK['small_orders'][0]['Lines/h']:.0f}, reserve {PK['small_orders'][1]['Lines/h']:.0f}, "
     f"large orders {lg_['lines_per_h']:.0f}, small-parts shelving {VLM['rate_lines_h']:.0f})", "≥ 50 lines/h"),
    ("Picking", "Fast-pick hit rate", "own", "lines picked in the fast-pick area ÷ all picked lines", "—", f"{fast_hit:.0%}", "≥ 60%"),
    ("Picking", "Walking per picked line", "own", "metres walked in all tours ÷ picked lines", "—", f"~{walk_per_line:.0f} m", "≤ 15 m"),
    ("Picking", "Trolley fill", "own", "volume or weight filled per trolley tour", "—", "80% (batch closed at 80%)", "75–85%"),
    ("Picking", "Small-parts picking time", "own", "small-parts lines ÷ 50 lines/h", "—", f"{lift_util:.1f} h/day for {VLM['lines_day']:.0f} lines", "≤ 2 h/day"),
    ("Picking", "Picking hours per day", "own", "picker-hours, average day",
     f"~{pick_today_staffed_h:.0f} h (modelled: single-order picking, staffed for the 08:00 peak)", f"{pick_future_h:.1f} h", "—"),
    ("Picking", "Pick accuracy", "W3", "% of orders without a picking error",
     "not in the data", "≥ 99.7% (scan every pick + put-to-light check)", "median 99.3%, best 99.68% (S023)"),
    ("Service", "Order lead time (per order)", "own", "order received → trailer leaves",
     f"median {lt['today_median_h']:.0f} h, p90 {lt['today_p90_h']:.0f} h", f"median {lt['future_median_h']:.0f} h, p90 {lt['future_p90_h']:.0f} h", "p90 ≤ 72 h"),
    ("Service", "Orders out within 24 h", "own", "% of orders", f"{lt['today_within_24h_pct']:.0f}%", f"{lt['future_within_24h_pct']:.0f}%", "≥ 60%"),
    ("Service", "On-time shipment", "W3", "% of lines staged before the planned departure",
     "49.9% (50.1% 'LATE', A005)", "≥ 98% (every wave ends ≥ 45 min before its trailers leave)", "≥ 98%"),
    ("Docks", "Trailers at the doors at once", "own", "busy day, p90",
     f"{outd['current_drop_trailer_concurrent_p90']:.0f} (parked all day)", f"max {DM['departure_plan']['plan_max_doors_busy']} of {outd['doors_recommended']} doors (time slots)", "≤ 5"),
    ("Docks", "Outbound staging fill", "own", "staging m² needed on the busiest afternoon ÷ 216 m²", "—",
     f"{OA['need_m2_max'] / OA['planned_m2']:.0%} (p90 day {OA['need_m2_p90'] / OA['planned_m2']:.0%})", "≤ 80%"),
    ("People", "Direct labour", "own", "FTE, average / peak day", "not in the data", f"{fte_avg:.1f} / {fte_pk:.1f} FTE + {C['indirect_fte']:.1f} indirect", "—"),
    ("People", "Labour productivity", "own", "order lines per direct labour hour", "—", f"{direct_lph:.1f} lines/h", "—"),
    ("Machinery", "Truck utilisation (average day)", "own", "operating h ÷ (units × 7.5 h)", "—",
     f"ETV {etv_u:.0f}% · EJE {eje_u:.0f}% · ERE {ere_u:.0f}%", "peak day ≤ 80%"),
    ("Cost", "Cost per order line", "own", "(OPEX + depreciation) ÷ lines", "—", f"€{unit_cost['per_order_line']:.2f}", "—"),
    ("Cost", "Cost per order", "own", "(OPEX + depreciation) ÷ orders", "—", f"€{unit_cost['per_order']:.2f}", "—"),
    ("Safety", "Trucks and pickers separated", "own", "pick faces without reach-truck traffic", "—",
     "100% (trucks refill from the rear and use the perimeter + cross-aisles)", "0 lost-time incidents"),
]
kpi_df = pd.DataFrame(kpis, columns=["Group", "KPI", "Type", "How it is measured", "Today (data)", "Future (design)", "Target / benchmark"])
save_table(kpi_df.set_index("KPI"), "d3_kpis.csv")

# ======================================================================= volume stress test (D2 §3.1 promise)
avail = 7.5 * 0.80
stress = []
for f_ in [1.0, 1.5, 2.0, 2.5]:
    pk_h_pick = (sum(r["Picker-h peak"] for r in PK["small_orders"]) + PK["large_orders"]["picker_h_peak"]) * f_
    stress.append({"Volume": f"{f_:.0%}",
                   "Direct FTE (peak day)": round(fte_pk * f_, 1),
                   "ETV 216i needed": int(np.ceil(fleet["ETV 216i"]["Equip-h/day peak"] * f_ / avail)),
                   "EJE 120i needed": int(np.ceil(fleet["EJE 120i"]["Equip-h/day peak"] * f_ / avail)),
                   "ERE 225 needed": int(np.ceil(fleet["ERE 225"]["Equip-h/day peak"] * f_ / avail)),
                   "Outbound doors (busiest hour)": int(np.ceil(outd["formula_doors_p90_hour"] * f_)),
                   "Pickers in the busiest wave": int(np.ceil(pk_h_pick / WAVES / 2.75))})
stress = pd.DataFrame(stress)
save_table(stress.set_index("Volume"), "d3_stress_test.csv")

# ======================================================================= sensitivity (annual cost = OPEX + depreciation)
def annual_cost(**over):
    k = dict(C); k.update(over)
    lab = (paid_hours(dir_h_day) * k.get("_lab_f", 1) + paid_hours(loose_h_day)) * k["labour_rate"] \
        + C["indirect_fte"] * C["paid_h_shift"] * DAYS * (k["lead_rate"] + 0.5 * k["admin_rate"]) / 1.5
    mhe = 12 * (n_etv * k["lease_etv"] + n_eje * k["lease_eje"] + n_ere * k["lease_ere"])
    rack_d = POS * k["rack_pp"] * (1 + C["rack_protect"]) * (1 + C["contingency"]) / C["life_rack"]
    other = ANNUAL - (float(opex_groups["Labour"]) + 12 * (n_etv * C["lease_etv"] + n_eje * C["lease_eje"] + n_ere * C["lease_ere"])
                      + POS * C["rack_pp"] * (1 + C["rack_protect"]) * (1 + C["contingency"]) / C["life_rack"])
    return lab + mhe + rack_d + other
base_cost = annual_cost()
sens_rows = []
for name, lo, hi in [("Labour rate (€20–28/h)", {"labour_rate": COST["labour_rate"][1]}, {"labour_rate": COST["labour_rate"][2]}),
                     ("Productivity ±20% (labour hours)", {"_lab_f": 0.8}, {"_lab_f": 1.2}),
                     ("Reach-truck lease (€495–1,550/month)", {"lease_etv": COST["lease_etv"][1]}, {"lease_etv": COST["lease_etv"][2]}),
                     ("Racking price (€80–200/position)", {"rack_pp": COST["rack_pp"][1]}, {"rack_pp": COST["rack_pp"][2]})]:
    sens_rows.append({"Driver": name, "Low EUR/yr": annual_cost(**lo), "High EUR/yr": annual_cost(**hi)})
sens = pd.DataFrame(sens_rows)
sens["Swing EUR/yr"] = sens["High EUR/yr"] - sens["Low EUR/yr"]
sens = sens.sort_values("Swing EUR/yr")
save_table(sens.set_index("Driver"), "d3_sensitivity.csv")

# ======================================================================= sorting facts (for the plain-language section)
sorting = {"small_orders_day": round(seg["small"]["orders_day"], 0), "small_orders_wave_avg": round(seg["small"]["orders_day"] / WAVES, 0),
           "small_orders_wave_peak": round(small_orders_wave_pk, 0), "ptl_slots": ptl_slots,
           "trolley_tours_day": round(sum(r["Tours/day"] for r in PK["small_orders"]), 0),
           "lines_per_tour": round(PK["small_orders"][0]["Lines per tour"], 0),
           "staging_lanes": DM["departure_plan"]["trailers_planned"], "roll_cages": roll_cages, "containers_day": CP["inbound_pattern"]["containers_avg"],
           "container_skus_median": loose["skus_per_container_median"], "container_skus_p75": loose["skus_per_container_p75"],
           "container_loads_median": loose["loads_per_container_median"], "build_spots": loose["build_spots"]}

# ======================================================================= figures
def bar_h(series, title, xlabel, name, color=BLUE, fmt="€{:,.0f}k", w=8.4):
    s_ = series.sort_values()
    fig, ax = plt.subplots(figsize=(w, 0.5 * len(s_) + 1.4))
    ax.barh(range(len(s_)), s_.values, color=color, height=0.62, zorder=3)
    for i, v in enumerate(s_.values):
        ax.text(v + s_.max() * 0.012, i, fmt.format(v / 1000), va="center", fontsize=9, color=INK)
    ax.set_yticks(range(len(s_))); ax.set_yticklabels(s_.index, fontsize=9.5)
    ax.set_xlim(0, s_.max() * 1.2); ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    ax.set_xlabel(xlabel); ax.set_title(title, loc="left")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"€{v / 1000:,.0f}k"))
    save_fig(fig, name)

bar_h(capex_groups, f"One-off investment (CAPEX): €{CAPEX / 1000:,.0f}k", "EUR", "d3_capex.png")
bar_h(opex_groups.rename(index={"Labour": "Labour", "Machinery": "Machinery (lease + power)", "Upkeep": "Upkeep (racks, IT)"}),
      f"Running cost (OPEX): €{OPEX / 1000:,.0f}k per year", "EUR per year", "d3_opex.png", color=AQUA)

# lead time: share of orders shipped within X hours (today vs future)
fig, ax = plt.subplots(figsize=(8.6, 3.9))
xs = np.arange(0, 121, 1)
for col, lab, colr in [("today_h", "Today (measured)", GREY), ("future_h", "Future (wave plan, modelled)", BLUE)]:
    v = od[col].dropna()
    ax.plot(xs, [(v <= x_).mean() * 100 for x_ in xs], color=colr, lw=2.4, label=lab)
for x_ in (24, 48):
    ax.axvline(x_, color="#d5d9e0", lw=1, zorder=0)
ax.text(24.8, 6, "24 h", fontsize=8.5, color="#6b7280"); ax.text(48.8, 6, "48 h", fontsize=8.5, color="#6b7280")
ax.set_xlim(0, 120); ax.set_ylim(0, 102); ax.set_xticks(range(0, 121, 12))
ax.set_xlabel("Hours from order received to trailer leaving"); ax.set_ylabel("% of orders shipped")
ax.legend(loc="lower right"); ax.grid(axis="x", visible=False)
ax.set_title(f"Order lead time: median {lt['today_median_h']:.0f} h today → {lt['future_median_h']:.0f} h with the wave plan", loc="left")
save_fig(fig, "d3_leadtime.png")

# today vs future picking hours (levers)
fig, ax = plt.subplots(figsize=(8.4, 3.4))
cats = ["Today (modelled)", "Future design"]
pick_b = [pick_today_h, pick_future_h]; peak_b = [pick_today_staffed_h - pick_today_h, 0]
ax.barh([1, 0], pick_b, color=[GREY, BLUE], height=0.55, zorder=3)
ax.barh([1, 0], peak_b, left=pick_b, color="#d5d9e0", height=0.55, zorder=3, hatch="///", edgecolor="white")
ax.text(pick_b[0] / 2, 1, f"picking {pick_b[0]:.0f} h", ha="center", va="center", color="white", fontsize=9.5, weight="bold")
ax.text(pick_b[0] + peak_b[0] / 2, 1, f"+{peak_b[0]:.0f} h\n08:00 peak", ha="center", va="center", color=INK, fontsize=8.5)
ax.text(pick_b[1] / 2, 0, f"{pick_b[1]:.0f} h", ha="center", va="center", color="white", fontsize=9.5, weight="bold")
ax.set_yticks([1, 0]); ax.set_yticklabels(cats); ax.grid(axis="y", visible=False); ax.grid(axis="x")
ax.set_xlabel("Picker-hours per average day")
ax.set_title(f"Picking: {pick_today_staffed_h:.0f} → {pick_future_h:.0f} picker-hours a day "
             f"(≈ €{SAVING / 1000:,.0f}k a year)", loc="left")
save_fig(fig, "d3_levers.png")

# tornado
fig, ax = plt.subplots(figsize=(8.6, 3.4))
for i, r in enumerate(sens.itertuples()):
    ax.barh(i, r._2 - base_cost, left=base_cost, color=AQUA, height=0.55, zorder=3)
    ax.barh(i, r._3 - base_cost, left=base_cost, color=ORANGE, height=0.55, zorder=3)
    ax.text(min(r._2, r._3) - 2000, i, f"€{min(r._2, r._3) / 1000:,.0f}k", ha="right", va="center", fontsize=8.5)
    ax.text(max(r._2, r._3) + 2000, i, f"€{max(r._2, r._3) / 1000:,.0f}k", ha="left", va="center", fontsize=8.5)
ax.axvline(base_cost, color=INK, lw=1.2)
ax.set_yticks(range(len(sens))); ax.set_yticklabels(sens["Driver"], fontsize=9)
span = (sens["High EUR/yr"].max() - sens["Low EUR/yr"].min())
ax.set_xlim(sens["Low EUR/yr"].min() - span * 0.25, sens["High EUR/yr"].max() + span * 0.25)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"€{v / 1000:,.0f}k"))
ax.grid(axis="y", visible=False); ax.grid(axis="x")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=AQUA, label="low value"), Patch(color=ORANGE, label="high value")], loc="lower right", fontsize=8.5)
ax.set_title(f"What moves the yearly cost? (base €{base_cost / 1000:,.0f}k incl. depreciation)", loc="left")
save_fig(fig, "d3_tornado.png")

# stress test: direct FTE at 100-250% volume
fig, ax = plt.subplots(figsize=(8.0, 3.4))
xv = np.arange(len(stress))
ax.bar(xv, stress["Direct FTE (peak day)"], color=BLUE, width=0.55, zorder=3)
for i, r in stress.iterrows():
    ax.text(i, r["Direct FTE (peak day)"] + 0.4, f"{r['Direct FTE (peak day)']:.0f} FTE\n{r['ETV 216i needed']} ETV · {r['EJE 120i needed']} EJE",
            ha="center", fontsize=8.5, color=INK)
ax.set_xticks(xv); ax.set_xticklabels([f"{v} volume" for v in stress["Volume"]])
ax.set_ylim(0, stress["Direct FTE (peak day)"].max() * 1.35); ax.set_ylabel("Direct FTE on the peak day")
ax.set_title("Stress test: the layout holds, people and trucks scale with volume", loc="left")
save_fig(fig, "d3_stress.png")

# sorting timeline: where and when things are sorted during the day
fig, ax = plt.subplots(figsize=(10.0, 3.3))
rows_ = [("Inbound: container zone\n(cartons → pallets per SKU)", [(6.0, 9.3)], ORANGE),
         ("Picking waves\n(W1 · W2 · W3)", [(6.0, 9.5), (9.5, 12.75), (12.75, 15.25)], GREY),
         ("Put-to-light wall\n(items → orders)", [(6.5, 10.0), (10.0, 13.25), (13.25, 15.75)], BLUE),
         ("Carrier lanes\n(parcels/pallets → trailers)", [(10.0, 16.75)], AQUA)]
for i, (lab, spans, colr) in enumerate(rows_[::-1]):
    for a_, b_ in spans:
        ax.barh(i, b_ - a_, left=a_, color=colr, height=0.5, edgecolor="white", linewidth=2, zorder=3)
ax.set_yticks(range(len(rows_))); ax.set_yticklabels([r[0] for r in rows_[::-1]], fontsize=8.8)
ax.set_ylim(-0.8, len(rows_) - 0.5); ax.set_xlim(6, 17.2); ax.set_xticks(range(6, 18)); ax.set_xticklabels([f"{h:02d}:00" for h in range(6, 18)], fontsize=8.5)
ax.grid(axis="y", visible=False); ax.grid(axis="x")
for t_, lab in [(10.5, "first departures"), (16.75, "last parcel trailer")]:
    ax.axvline(t_, color=INK, lw=1, ls="--"); ax.text(t_ - 0.06, -0.62, lab, fontsize=7.8, color=INK, ha="right")
ax.set_title("When sorting happens during a normal day", loc="left")
save_fig(fig, "d3_sorting_timeline.png")

# ======================================================================= metrics
update_metrics("performance_cost", {
    "cost_register": {k: {"value": v[0], "low": v[1], "high": v[2], "unit": v[3], "id": v[4], "basis": v[5]} for k, v in COST.items()},
    "quantities": {"positions": POS, "flow_bays": flow_bays, "flow_lanes": flow_lanes, "ptl_slots": ptl_slots, "rf_units": rf_units,
                   "pack_stations": pack_stations, "roll_cages": roll_cages, "trolleys": tro, "totes": totes,
                   "etv": n_etv, "eje": n_eje, "ere": n_ere, "containers_year": containers_year, "move_hours": round(move_h, 0)},
    "capex_total": round(CAPEX, 0), "capex_by_group": {k: round(v, 0) for k, v in capex_groups.items()},
    "capex_table": capex.round(2).to_dict("records"), "depreciation_year": round(DEPR, 0),
    "opex_total": round(OPEX, 0), "opex_by_group": {k: round(v, 0) for k, v in opex_groups.items()},
    "opex_table": opex.round(2).to_dict("records"), "annual_cost": round(ANNUAL, 0),
    "unit_cost": {k: round(v, 2) for k, v in unit_cost.items()},
    "volumes_year": {"lines": round(lines_y, 0), "orders": round(orders_y, 0), "inbound_pallets": round(inb_y, 0)},
    "loose_cost_per_container": round(loose_cost_container, 0),
    "levers": levers.round(2).to_dict("records"), "saving_year": round(SAVING, 0), "payback_years": round(PAYBACK, 1),
    "capex_reuse_racking": round(CAPEX_REUSE, 0), "payback_reuse_years": round(PAYBACK_REUSE, 1),
    "capex_process": round(CAPEX_PROCESS, 0), "payback_process_years": round(PAYBACK_PROCESS, 2),
    "small_item_options": small_opts.round(0).to_dict("records"),
    "pick_today_h": round(pick_today_h, 3), "pick_today_staffed_h": round(pick_today_staffed_h, 3), "pick_future_h": round(pick_future_h, 3),
    "leadtime": lt, "kpis": kpi_df.to_dict("records"), "stress": stress.to_dict("records"),
    "sensitivity": sens.round(0).to_dict("records"), "sensitivity_base": round(base_cost, 0),
    "storage": {"occupied_peak": occ_peak, "occupied_mean": round(occ_mean, 0), "growth_per_quarter_pct": round(growth_q * 100, 1),
                "months_headroom": round(float(months_headroom), 1), "months_headroom_12": round(float(months_headroom_12), 1),
                "rack_need_peak": int(rack_need), "fast_hit_pct": round(fast_hit * 100, 0), "walk_per_line_m": round(walk_per_line, 1),
                "small_parts_h_day": round(lift_util, 2), "sku_density_lift": round(sku_density_lift, 0), "sku_density_rack": round(sku_density_rack, 1), "fte_avg": round(fte_avg, 1), "fte_peak": round(fte_pk, 1)},
    "sorting": sorting,
})

print(capex[["Group", "Item", "Qty", "Unit price EUR", "Total EUR"]].to_string(index=False))
print(f"CAPEX €{CAPEX:,.0f} | depreciation €{DEPR:,.0f}/yr")
print(opex[["Item", "Qty / yr", "Unit cost EUR", "Total EUR/yr"]].to_string(index=False))
print(f"OPEX €{OPEX:,.0f}/yr | annual incl. depreciation €{ANNUAL:,.0f} | unit {unit_cost}")
print(f"loose zone in-house €{loose_cost_container:,.0f}/container")
print(small_opts.to_string(index=False)); print(f"process CAPEX €{CAPEX_PROCESS:,.0f} payback {PAYBACK_PROCESS:.2f} yrs")
print(levers.to_string(index=False)); print(f"saving €{SAVING:,.0f}/yr, payback {PAYBACK:.1f} yrs | reuse racking: CAPEX €{CAPEX_REUSE:,.0f}, payback {PAYBACK_REUSE:.1f} yrs")
print("LEAD TIME", lt)
print(stress.to_string(index=False)); print(sens.to_string(index=False))
print("SORTING", sorting); print("headroom months", round(float(months_headroom), 1), "growth/q", round(growth_q * 100, 1))
