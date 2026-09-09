"""
PHASE 2 - CAPACITY / STORAGE-CONCEPT SIZING (bottom-up).
Computes, for several storage concepts, how many rack levels fit under 12.2 m,
the floor area needed to hold the design pallet-position target, and the % of a
7,000 m2 envelope that consumes. Feeds the design-options comparison.

All assumptions are explicit here and mirrored into data/assumptions.json.
No fabricated data: pallet dimensions/heights are measured from the storage snapshots.
"""
import json
import numpy as np
import pandas as pd
from load_data import all_storage
from _util import save_table, save_fig, update_metrics
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------
# 1. MEASURED INPUTS (from latest storage snapshot)
# ----------------------------------------------------------------------------
storage = all_storage()
latest = storage[sorted(storage)[-1]]
pa_hgt = pd.to_numeric(latest["PA HGT"], errors="coerce")      # pallet+load height, cm
pa_hgt = pa_hgt[(pa_hgt > 20) & (pa_hgt < 300)]                # drop impossible
loc_hgt = pd.to_numeric(latest["LOC HEIGHT"], errors="coerce")
loc_hgt = loc_hgt[(loc_hgt > 20) & (loc_hgt < 400)]

measured = {
    "pa_hgt_median_cm": round(float(pa_hgt.median()), 1),
    "pa_hgt_p90_cm": round(float(pa_hgt.quantile(0.90)), 1),
    "pa_hgt_p95_cm": round(float(pa_hgt.quantile(0.95)), 1),
    "loc_height_mode_cm": float(loc_hgt.mode().iat[0]),
}

# peak concurrent loads (positions in use) from inventory analysis
peak_loads = int(max(pd.to_numeric(s["LODNUM"].astype(str).factorize()[0], errors="coerce").max() + 1
                     if False else s["LODNUM"].nunique() for s in storage.values()))

# ----------------------------------------------------------------------------
# 2. DESIGN ASSUMPTIONS  (explicit, tunable)
# ----------------------------------------------------------------------------
A = {
    "clear_height_m": 12.2,
    "top_clearance_m": 0.5,          # sprinkler / roof steel clearance below 12.2
    "floor_level_base_m": 0.15,      # first beam off floor
    "pallet_euro_face_m": 0.8,       # 800 mm face to aisle
    "pallet_depth_m": 1.2,           # 1200 mm deep
    "pallet_pitch_m": 0.9,           # face + side clearance between pallets on beam
    "rack_depth_single_m": 1.1,      # beam-to-beam single-deep incl overhang
    "beam_plus_clear_m": 0.25,       # beam height + vertical load clearance per level
    "level_load_height_m": None,     # set below from measured p90
    "growth_safety_buffer": 1.15,    # peak + 15% growth/safety
    "target_utilisation": 0.90,      # design to 90% max occupancy (putaway headroom)
    "footprint_envelope_m2": 7000,   # A008 - to confirm whole-site vs Assa-only
    "non_storage_share": 0.35,       # receiving+staging+pick+pack+ship+office+circulation
}
# level pitch from measured p90 pallet height (so ~90% of pallets fit a standard opening)
A["level_load_height_m"] = round(measured["pa_hgt_p90_cm"] / 100.0, 2)
level_pitch = A["level_load_height_m"] + A["beam_plus_clear_m"]
usable_h = A["clear_height_m"] - A["top_clearance_m"] - A["floor_level_base_m"]
base_levels = int(usable_h // level_pitch)

# design target positions
required_loads = peak_loads * A["growth_safety_buffer"]
design_positions = required_loads / A["target_utilisation"]

# ----------------------------------------------------------------------------
# 3. STORAGE CONCEPTS
#    aisle_m = operating aisle width; deep = pallets stored in depth;
#    util = location/selectivity utilisation (honeycombing losses);
#    levels_cap = max reachable levels for that MHE (min with height-limited base)
# ----------------------------------------------------------------------------
concepts = {
    "Selective - wide aisle (counterbalance)": dict(aisle=3.7, deep=1, util=0.95, levels_cap=6, mhe="Counterbalance FLT"),
    "Selective - narrow aisle (reach truck)":  dict(aisle=2.9, deep=1, util=0.95, levels_cap=7, mhe="Reach truck"),
    "Double-deep (reach + deep forks)":        dict(aisle=2.9, deep=2, util=0.80, levels_cap=7, mhe="Reach truck (deep)"),
    "VNA (man-up turret)":                     dict(aisle=1.8, deep=1, util=0.97, levels_cap=8, mhe="VNA turret truck"),
    "Drive-in (block)":                        dict(aisle=3.7, deep=4, util=0.65, levels_cap=5, mhe="Counterbalance FLT"),
}

rows = []
for name, c in concepts.items():
    levels = min(base_levels, c["levels_cap"])
    # ground module: one aisle serves two facing rows.
    # per-row ground strip depth = rack_depth*deep ; aisle shared = aisle/2
    row_depth = A["rack_depth_single_m"] * c["deep"]
    ground_strip_m = row_depth + A["aisle"] / 2 if False else row_depth + c["aisle"] / 2
    # ground footprint per pallet column (along beam) = pitch
    ground_area_per_column = ground_strip_m * A["pallet_pitch_m"]
    positions_per_column = levels * c["deep"] * c["util"]
    area_per_position = ground_area_per_column / positions_per_column
    storage_area = design_positions * area_per_position
    total_area = storage_area / (1 - A["non_storage_share"])
    rows.append({
        "concept": name,
        "mhe": c["mhe"],
        "levels": levels,
        "deep": c["deep"],
        "util_%": int(c["util"] * 100),
        "aisle_m": c["aisle"],
        "m2_per_position": round(area_per_position, 3),
        "storage_area_m2": int(storage_area),
        "total_area_m2 (incl 35% non-storage)": int(total_area),
        "% of 7,000 m2": round(total_area / A["footprint_envelope_m2"] * 100, 0),
        "fits_7000": "YES" if total_area <= A["footprint_envelope_m2"] else "TIGHT/NO",
    })

df = pd.DataFrame(rows).set_index("concept")
save_table(df, "capacity_concepts.csv")

metrics = {
    "measured": measured,
    "peak_loads": peak_loads,
    "assumptions": A,
    "level_pitch_m": round(level_pitch, 2),
    "base_levels_height_limited": base_levels,
    "required_loads_peak_plus_buffer": int(required_loads),
    "design_positions_target": int(design_positions),
    "concepts": df.reset_index().to_dict("records"),
}
update_metrics("capacity", metrics)

# figure: total area by concept vs envelope
fig, ax = plt.subplots(figsize=(8, 4))
areas = [r["total_area_m2 (incl 35% non-storage)"] for r in rows]
names = [r["concept"].split(" (")[0].replace(" - ", "\n") for r in rows]
bars = ax.bar(names, areas, color="#6c8eef")
ax.axhline(7000, color="#e08a5b", ls="--", lw=1.5, label="7,000 m² envelope")
ax.set_ylabel("total floor area needed (m²)")
ax.set_title(f"Floor area to hold {int(design_positions):,} pallet positions, by storage concept")
ax.legend()
for b, a_ in zip(bars, areas):
    ax.text(b.get_x() + b.get_width()/2, a_, f"{a_:,}", ha="center", va="bottom", fontsize=8)
plt.xticks(fontsize=7)
save_fig(fig, "capacity_concepts.png")

print(f"Measured pallet height: median {measured['pa_hgt_median_cm']} cm, p90 {measured['pa_hgt_p90_cm']} cm")
print(f"Level pitch {level_pitch:.2f} m -> height-limited base levels = {base_levels}")
print(f"Peak loads {peak_loads:,} -> required (peak +15%) {int(required_loads):,} -> "
      f"design positions @90% util = {int(design_positions):,}")
print()
print(df.to_string())
