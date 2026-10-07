"""
Build the Deliverable 2 (Future State) Word document from analysis outputs.
Reads outputs/reports/phase1_metrics.json (capacity_plan, dock_mhe, layout, peak_slotting
sections) + figures + data/assumptions.json; writes deliverables/Deliverable_2_Future_State.docx.
Run capacity_plan.py and dock_mhe_plan.py first.
"""
import os, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.join(os.path.dirname(__file__), "..")
REPORTS = os.path.join(BASE, "outputs", "reports")
FIGS = os.path.join(BASE, "outputs", "figures")
DATA = os.path.join(BASE, "data")
M = json.load(open(os.path.join(REPORTS, "phase1_metrics.json"), encoding="utf-8"))
ASSUM = json.load(open(os.path.join(DATA, "assumptions.json"), encoding="utf-8"))

RED = RGBColor(0xD4, 0x00, 0x11); DARK = RGBColor(0x22, 0x22, 0x22); GREY = RGBColor(0x66, 0x66, 0x66)
doc = Document()
normal = doc.styles["Normal"]; normal.font.name = "Calibri"; normal.font.size = Pt(10.5); normal.font.color.rgb = DARK
for lvl, sz in [("Heading 1", 15), ("Heading 2", 12.5), ("Heading 3", 11)]:
    st = doc.styles[lvl]; st.font.name = "Calibri"; st.font.size = Pt(sz)
    st.font.color.rgb = RED if lvl == "Heading 1" else DARK; st.font.bold = True


def para(t, size=10.5, color=DARK, bold=False, italic=False, align=None, sa=6):
    """Paragraph; '**text**' segments are bold (markers are not printed)."""
    p = doc.add_paragraph()
    for i, seg in enumerate(t.split("**")):
        if not seg:
            continue
        r = p.add_run(seg)
        r.font.size = Pt(size); r.font.color.rgb = color; r.bold = bold or (i % 2 == 1); r.italic = italic
    if align: p.alignment = align
    p.paragraph_format.space_after = Pt(sa); return p


def bullets(items):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        if "**" in it:
            for i, seg in enumerate(it.split("**")):
                r = p.add_run(seg); r.bold = (i % 2 == 1); r.font.size = Pt(10.5)
        else:
            p.add_run(it).font.size = Pt(10.5)


def table(headers, rows, widths=None, arr=1):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Light Grid Accent 1"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        t.rows[0].cells[i].text = ""; r = t.rows[0].cells[i].paragraphs[0].add_run(str(h)); r.bold = True; r.font.size = Pt(9.5)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; p = cells[i].paragraphs[0]; r = p.add_run(str(v)); r.font.size = Pt(9.5)
            if i >= arr: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows: row.cells[i].width = Cm(w)
    # keep small tables on one page: rows can't split, each row keeps with the next
    for ri, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
        if ri < len(t.rows) - 1:
            for c in row.cells:
                for p in c.paragraphs: p.paragraph_format.keep_with_next = True
    doc.add_paragraph().paragraph_format.space_after = Pt(2); return t


def figure(name, cap, w=15.5):
    p = os.path.join(FIGS, name)
    if os.path.exists(p):
        doc.add_picture(p, width=Cm(w)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        para(cap, size=8.5, color=GREY, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=10)


def footer():
    f = doc.sections[0].footer.paragraphs[0]; f.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = f.add_run("Project OTM — Assa Abloy @ DHL Bemmel  ·  Deliverable 2 (Future State)  ·  Page")
    run.font.size = Pt(8); run.font.color.rgb = GREY
    fld = OxmlElement("w:fldSimple"); fld.set(qn("w:instr"), "PAGE"); run._r.addnext(fld)


cp = M["capacity_plan"]; lay = M["layout"]; cap = M["capacity"]
dm = M["dock_mhe"]; meas = cp["measured"]; pt = cp["pick_type_order_derived"]
ind, outd, rel = dm["inbound_doors"], dm["outbound_doors"], dm["order_release"]
fleet = {f["Model"].replace("Jungheinrich ", ""): f for f in dm["fleet"]}
sl = pt["share_lines_pct"]; su = pt["share_units_pct"]
POS_PEAK, POS_TARGET = 8512, 9500
N_IN, N_OUT = ind["doors_recommended"], outd["doors_recommended"]

# COVER
doc.add_paragraph().paragraph_format.space_before = Pt(55)
para("PROJECT OTM", size=13, color=RED, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=2)
para("Future-State Operational Design", size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=2)
para("Assa Abloy operation · DHL Supply Chain, Bemmel (NL_0032)", size=12, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER, sa=26)
table(["Field", "Detail"], [
    ["Deliverable", "2 — Proposed future state for the in-scope processes"],
    ["Due date", "07-10-2026"],
    ["Concept", "Option B — Hybrid density + velocity slotting + zone/batch picking"],
    ["Envelope", "≤ 7,000 m² · ≤ 12.2 m"],
    ["Team", "Group 3 — Gleb, Rachel Selvarathnam, Arnau, Vidhi"],
    ["Version", "v2 — adds inbound (loose containers), dock-door calculation, Jungheinrich MHE, order release"],
], widths=[4.5, 11], arr=9)
para("Future-state design for the recommended Option B (Deliverable 1). Workload drivers are measured "
     "from the Assa Abloy Q2-2025 data; equipment data come from Jungheinrich; productivities and handling "
     "allowances are documented assumptions (Section 7) to be validated with DHL. Reproducible from analysis/*.py.",
     size=9, color=GREY, italic=True)
doc.add_page_break()

# CONTENTS
doc.add_heading("Contents", level=1)
_p = doc.add_paragraph()
_fld = OxmlElement("w:fldSimple"); _fld.set(qn("w:instr"), 'TOC \\o "1-2" \\h \\z \\u')
_r = OxmlElement("w:r"); _t = OxmlElement("w:t")
_t.text = "(In Word: right-click → Update Field to build the table of contents.)"
_r.append(_t); _fld.append(_r); _p._p.append(_fld)
doc.add_page_break()

# 1 CONCEPT RECAP
doc.add_heading("1. Recommended concept and what changed", level=1)
para("Option B was selected in Deliverable 1. It combines two-deep (double-deep) reserve racking, selective + "
     "cantilever racking for irregular and long goods, and a fast-pick area (carton-flow / shelving) for the "
     "best-sellers, run with demand-based slotting and zone + batch picking. This version builds in the points "
     "agreed with the teacher and DHL:")
table(["Topic", "Before", "Now (this version)"], [
    ["Storage basis", "14,074 positions (11,015 loads + buffer)",
     f"~{POS_TARGET:,} positions: peak {POS_PEAK:,} occupied locations ÷ 0.90"],
    ["Pick method", "DHL's historical pick flags (61% case)",
     f"Derived from the orders: {sl.get('each', 0):.0f}% each / {sl.get('case', 0):.0f}% case / "
     f"{sl.get('full pallet', 0):.0f}% full-pallet lines"],
    ["Inbound", "Estimated from flow balance",
     f"Measured ~{meas['inbound_loads_day']:.0f} loads/day; 2 shipments/day from Assa Abloy factories, "
     f"pallets + loose containers"],
    ["Dock doors", "3 + 3 assumed", f"Calculated: {N_IN} receiving (west, 1 container dock) + {N_OUT} shipping (east)"],
    ["Equipment", "Generic truck types",
     f"Jungheinrich ETV 216i ×{fleet['ETV 216i']['Units recommended']}, ECE 225 ×{fleet['ECE 225']['Units recommended']}, "
     f"ERE 225 ×{fleet['ERE 225']['Units recommended']} — sized from their technical data"],
    ["08:00 peak", "Treated as customer demand", "Caused by the order-release routine → release in waves"],
], widths=[3.0, 5.0, 8.0], arr=9)

# 2 FUTURE-STATE PROCESSES
doc.add_heading("2. Future-state processes", level=1)
para("Each process below states the steps, the system transaction, the physical movement, the equipment, and "
     "where the Deliverable-1 design choices are applied. The swimlane (Fig 1) gives the end-to-end overview; "
     "per-process flowcharts follow.")
figure("flow_swimlane.png", "Fig 1. End-to-end future-state process — cross-functional swimlane.", 17)
doc.add_heading("2.1 Receiving & putaway", level=2)
bullets([
    f"**What arrives:** 2 shipments a day straight from Assa Abloy factories (S004). Trailers from the European "
    f"plants arrive palletised; sea containers from Asia (~{meas['inbound_asia_origin_pct']:.0f}% of loads) arrive "
    f"loose — cartons stacked on the container floor.",
    "**Palletised trailer (doors R2–R3):** dock → unload with ERE 225 pallet truck → RF-scan against the ASN → "
    "quantity/quality check → register the load (LPN) → system-directed putaway with an ETV 216i reach truck → confirm.",
    f"**Loose container (door R1, container dock):** dock → 2-person crew de-stuffs the cartons → sort by SKU on the "
    f"dock → build and wrap pallets, print LPN labels → scan against the ASN → putaway. About "
    f"{cp['inbound_pattern']['destuff_h']:.0f} h per 40 ft container (A019, S005).",
    "**Policy applied:** demand-based directed putaway (A/B close to their fast-pick faces, C further away); "
    "pallets over 1 t on low levels; cantilever for extra-long goods.",
    "**Truck route:** reach trucks use the left perimeter aisle and the cross-aisle, never the fast-pick area — "
    "Jungheinrich's 'clear traffic guidance' principle (S009).",
])
figure("flow_receiving_putaway.png", "Fig 2. Receiving & putaway flow.", 12)
doc.add_heading("2.2 Replenishment", level=2)
bullets([f"**Steps:** fast-pick face below minimum → WMS replenishment task → ETV 216i takes the reserve pallet down "
         f"the storage aisle → feeds the carton-flow lane from the rear → confirm (~{meas['replen_pallets_day']:.0f} "
         f"pallets/day on average).",
         "**Policy applied:** min/max replenishment; FIFO via FIF DATE where relevant. Pickers work the front of the "
         "lanes and trucks the rear, so people and reach trucks never share a face."])
figure("flow_replenishment.png", "Fig 3. Replenishment flow.", 11)
doc.add_heading("2.3 Picking (zone + batch / wave)", level=2)
bullets([
    f"**Pick method follows the orders (A022):** comparing each line's quantity with the SKU's case and pallet "
    f"quantity gives {sl.get('each', 0):.0f}% each-pick lines, {sl.get('case', 0):.0f}% case lines and "
    f"{sl.get('full pallet', 0):.0f}% full-pallet lines (by units: {su.get('case', 0):.0f}% case, "
    f"{su.get('each', 0):.0f}% each, {su.get('full pallet', 0):.0f}% pallet). Picking is each-dominant by line count.",
    "**Steps:** orders released in waves (not one 08:00 backlog, Section 4.2) → batch single-line orders → picker "
    "on an ECE 225 collects 2 orders' roll cages/pallets per trip → full pallets by ETV 216i → to consolidation.",
    "**Where:** A/B fast movers in the fast-pick area; C items at the low levels of the reserve aisles (zones 2–3).",
])
figure("flow_picking.png", "Fig 4. Picking flow (zone + batch/wave).", 12)
doc.add_heading("2.4 Consolidation, packing & shipping", level=2)
bullets([
    "**Steps:** picked roll cages → put-to-light sort by order → pack, print-and-apply → parcel cartons onto roll "
    "cages by carrier / pallets wrapped → stage by carrier → live-load at the booked time → dispatch.",
    f"**Measured outbound:** {outd['trailers_per_day_mean']:.0f} trailers/day (p90 {outd['trailers_per_day_p90']:.0f}), "
    f"carrying on average only {outd['pallets_per_trailer_mean']} pallets + {outd['cartons_per_trailer_mean']:.0f} "
    f"cartons; {outd['share_trailers_zero_pallets_pct']:.0f}% of trailers carry no pallets at all (DHL Parcel routes).",
    f"**Policy applied:** carriers book collection time slots; goods wait in the outbound staging lanes, not in "
    f"parked trailers; {N_OUT} shipping doors on the east wall (Section 4.4).",
])
figure("flow_pack_ship.png", "Fig 5. Consolidation, packing & shipping flow.", 12)
doc.add_heading("2.5 Returns (reverse logistics)", level=2)
bullets([
    "**Steps:** customer return arrives through the receiving doors → receive & scan (RMA) → inspect and grade in "
    "the Returns area → sellable: restock · reworkable: rework, then restock · otherwise scrap / return to vendor "
    "→ update inventory and credit.",
    "**Policy applied:** returns re-enter through the same demand-based putaway, so graded stock rejoins the reserve.",
])
figure("flow_returns.png", "Fig 6. Returns / reverse-logistics flow.", 12)

# 3 POLICIES
doc.add_heading("3. Warehouse policies", level=1)
table(["Policy", "Decision", "Why (data)"], [
    ["Storage", "Random within velocity zones; fixed fast-pick faces + random reserve", "73% single-load tail; 48.6% ABC mismatch"],
    ["Slotting", "Demand-ABC; fast movers spread across zones, extreme SKUs duplicated; heavy low",
     "13% SKUs = 80% volume; A = 60% of picks (S003)"],
    ["Zoning", "Fast-pick (A/B) vs reserve; truck routes kept out of the pick zone",
     f"{sl.get('each', 0):.0f}% of order lines are each-picks; safety (S009)"],
    ["Batching", "Batch single-line / single-unit orders", "50% single-line, 24% single-unit"],
    ["Order release", "Waves through the shift instead of one 08:00 release",
     f"08:00 = {rel['pick_peak_over_mean_active_hour']}× the mean hour (A023)"],
    ["Routing", "S-shape / return within aisles", "reduce travel in reserve"],
    ["Putaway", "System-directed, velocity-based to zone", "align stock to demand"],
    ["Replenishment", "Min/max top-up from the rear of the lanes", "keep faces filled at peak"],
    ["Dock scheduling", "Carrier time slots; stage, then live-load; 1 container dock",
     f"{outd['trailers_per_day_mean']:.0f} trailers/day, {outd['share_trailers_zero_pallets_pct']:.0f}% parcel-only; "
     f"~{meas['inbound_asia_origin_pct']:.0f}% loose inbound"],
    ["FIFO / FEFO", "FIFO via FIF DATE where relevant", "parts mostly not date-critical"],
], widths=[3.0, 7.5, 5.5], arr=9)

ps = M.get("peak_slotting", {})
doc.add_heading("3.1 Peak-season slotting (congestion control)", level=2)
para("At peak, congestion — not walk distance — becomes the dominant cost (Gadeyne, S003). Because the peak "
     "is spiky (1.83× lines / 2.85× units) and picks are concentrated, clustering all fast movers in one golden "
     "zone would jam a single area. We therefore adopt peak-aware slotting:")
bullets([
    f"**Picks are concentrated:** the top 1% of SKUs (~{ps.get('extreme_top1pct_skus', '43')}) do "
    f"~{ps.get('extreme_top1pct_share_picks', '15')}% of all picks, and A-class SKUs ~"
    f"{ps.get('A_class_share_picks', '60')}% of picks.",
    f"**Spread fast movers across all pick zones** (balanced on peak-day pick frequency): one zone would carry "
    f"~{ps.get('A_class_share_picks', '60')}% of picks; spread over 3 zones each carries "
    f"~{ps.get('A_class_share_if_spread_3_zones', '20')}%.",
    f"**Duplicate the extreme SKUs** (~{ps.get('extreme_top1pct_skus', '43')} items) in different zones to allow "
    "parallel picking.",
    "**Levers in priority order** (S003): slotting → order batching → wave-release timing → pick-path sequencing.",
    "**Validate by simulation** at 150% / 200% / 250% of normal volume (Deliverable 3).",
])

# 4 INBOUND, ORDER RELEASE & DOCKS
doc.add_heading("4. Inbound, order release & dock doors", level=1)
doc.add_heading("4.1 What comes in", level=2)
para("No separate receiving file was provided, so receipts are measured from the storage snapshots: loads with an "
     "ADD DATE in the 14 days before each snapshot (A007). Loads already shipped before the snapshot are not "
     "visible, so these are lower bounds.")
table(["Snapshot", "Receiving days", "Loads booked in", "Loads / day", "Busiest day", "From Asia %"],
      [[w["snapshot"], w["receiving_days"], f"{w['loads']:,}", f"{w['loads_per_day']:.0f}", w["max_day"],
        f"{w['asia_origin_pct']:.0f}%"] for w in cp["inbound_windows"]], widths=[3.0, 2.6, 2.8, 2.4, 2.4, 2.4])
bullets([
    f"**~{meas['inbound_loads_day']:.0f} loads are received per working day; the busiest day reached "
    f"{meas['inbound_max_day']:.0f} (×{meas['inbound_peak_factor']:.1f}).**",
    "**2 shipments a day, direct from Assa Abloy factories** (teacher/DHL, S004) — in China, Germany, Romania, the "
    "Netherlands, Spain, Finland and others.",
    f"**~{meas['inbound_asia_origin_pct']:.0f}% of loads come from Asia** and arrive loose in sea containers. The "
    "largest receipts (70–100 loads, all from China) take 1–3 days to book in — consistent with de-stuffing and "
    "palletising by hand.",
])
doc.add_heading("4.2 Why picking peaks at 08:00", level=2)
figure("order_release_profile.png", "Fig 7. Orders arrive in the afternoon, are released at 16:00–17:00 and are "
       "picked the next morning — the 08:00 peak is the release backlog.", 15.5)
bullets([
    f"**{rel['orders_arrive_15_17_pct']:.0f}% of orders arrive between 15:00 and 17:00**, and ~"
    f"{rel['allocated_16_18_pct']:.0f}% are released (allocated) between 16:00 and 18:00.",
    f"**Picking starts at 06:00 and peaks at 08:00** at {rel['pick_peak_over_mean_active_hour']}× the average "
    "working hour: the whole afternoon backlog lands on the floor at the start of the shift (A023).",
    f"**Future state:** release work in waves (e.g. 06:00, 09:30, 12:00 plus a same-day wave for early orders). "
    f"Levelling the load frees ~{rel['picker_capacity_saving_if_levelled_pct']:.0f}% of peak-hour picker "
    "capacity without any change in customer service.",
])
doc.add_heading("4.3 Inbound dock doors", level=2)
para(f"Doors needed = the larger of (a) door-hours ÷ (receiving window {ind['receiving_window_h']:.0f} h × "
     f"{ind['door_util']:.0%} utilisation) and (b) the number of arrivals that can be at the dock at the same time. "
     f"A palletised trailer occupies a door ~{ind['trailer_door_h']:.1f} h (unload with ERE 225 at ~1 min per pallet "
     f"+ 20 min dock-on and paperwork); a loose container ~{ind['container_door_h']:.1f} h.")
table(["Scenario", "Door-hours / day", "Doors by capacity", "Arrivals at once", "Doors needed"],
      [[s["Scenario"], f"{s['Door-hours/day']:.1f}", s["Doors by capacity"], s["Simultaneous arrivals"],
        s["Doors needed"]] for s in ind["scenarios"]], widths=[7.4, 2.4, 2.4, 2.2, 2.0], arr=1)
para(f"**Result: {N_IN} receiving doors on the west wall** — R1 a container dock (leveller with the range for "
     f"container chassis), R2–R3 for trailers. The two daily shipments need 2 doors so a 3-hour container never "
     f"blocks a trailer; the third door covers the 'many smaller trucks' case, customer returns and breakdowns.",
     bold=True, sa=4)
doc.add_heading("4.4 Outbound dock doors", level=2)
para(f"Sized trailer by trailer from the 912 outbound trailers in Q2. Dock time per trailer = 15 min dock-on and "
     f"paperwork + loading of its actual pallets and roll cages with an ERE 225 (mean "
     f"{outd['dock_min_mean']:.0f} min, p90 {outd['dock_min_p90']:.0f} min). Doors are sized on the busiest hour: "
     f"p90 {outd['busiest_hour_trailers_p90']:.0f} trailers × {outd['dock_min_mean']:.0f} min ÷ (60 min × 85%) = "
     f"{outd['formula_doors_p90_hour']} → {outd['doors_needed']} doors, plus 1 spare.")
figure("dock_outbound_doors.png", "Fig 8. Outbound doors needed today vs in the future state (busy day, p90).", 14)
table(["Measure", "Value"], [
    ["Trailers per day (mean / p90 / max)",
     f"{outd['trailers_per_day_mean']:.0f} / {outd['trailers_per_day_p90']:.0f} / {outd['trailers_per_day_max']}"],
    ["Load per trailer (mean)", f"{outd['pallets_per_trailer_mean']} pallets + {outd['cartons_per_trailer_mean']:.0f} cartons"],
    ["Trailers with no pallets (parcel only)", f"{outd['share_trailers_zero_pallets_pct']:.0f}%"],
    ["Trailers dispatched in the busiest hour (p90 / max)",
     f"{outd['busiest_hour_trailers_p90']:.0f} / {outd['busiest_hour_trailers_max']}"],
    ["Today: trailers parked at the doors at once (p90)", f"{outd['current_drop_trailer_concurrent_p90']:.0f}"],
    ["Future without time slots (p90)", f"{outd['future_liveload_concurrent_p90']:.0f}"],
    ["Future with carrier time slots", f"{outd['formula_doors_p90_hour']} → {N_OUT} doors incl. 1 spare"],
], widths=[10.0, 6.0], arr=9)
car = list(dm["carriers_trailers_per_day"].items())[:6]
def carrier_name(n):
    n = n.title().replace("Dhl", "DHL").replace("Dsv", "DSV").replace("Edc", "EDC").replace("Bel And Lux", "BE & LU")
    return {"Exworks": "Ex-works (customer pickup)", "DHL4You": "DHL4YOU", "DHL Parcel Netherlands Dach": "DHL Parcel NL DACH"}.get(n, n)
bullets([
    f"**Result: {N_OUT} shipping doors on the east wall**, next to outbound staging and packing.",
    "**Carrier time slots are a condition of this design.** WMS dispatch times are closed in batches (60% of "
    "afternoon dispatches are under 2 minutes apart); without booked slots up to "
    f"{outd['future_liveload_concurrent_p90']:.0f} doors would be needed, and today's all-day parked trailers "
    f"would need ~{outd['current_drop_trailer_concurrent_p90']:.0f}.",
    "**Main carriers (trailers/day):** " + ", ".join(f"{carrier_name(k)} {v:.1f}" for k, v in car) + ".",
])

# 5 LAYOUT & ZONING (3D)
doc.add_heading("5. Layout & zoning (3-dimensional)", level=1)
para(f"Zones are sized from the measured volumes and laid out as a straight-through flow: goods come in on the "
     f"west side and leave on the east side. Building ≈ {lay['building_L_m']:.0f} m × {lay['building_depth_m']:.0f} m.")
table(["Zone", "Area m²", "% of building"],
      [[z["Zone"], f"{z['Area m2']:,}", z["% of building"]] for z in lay["zones"]], widths=[8.5, 3.5, 3.5])
para(f"**Total floor area {lay['total_area_m2']:,} m² = {lay['pct_of_7000']:.0f}% of the 7,000 m² envelope.**",
     bold=True, sa=4)
geo = dm["geometry"]
bullets([
    f"**Storage:** target ~{POS_TARGET:,} positions (peak {POS_PEAK:,} occupied locations ÷ 0.90). Rack frames take up "
    f"to 8 beam levels under 12.2 m (top beam {geo['top_beam_m']:.1f} m, within the ETV 216i's 10.7 m lift); beams are "
    "installed for the target and extra levels absorb growth without more floor space.",
    f"**Working areas sized from measured volumes:** inbound ~{meas['inbound_loads_day']:.0f} loads/day (peak "
    f"{meas['inbound_max_day']:.0f}); outbound {meas['outbound_pallets_day']:.0f} pallets + "
    f"{meas['outbound_cartons_day']:.0f} cartons/day.",
    f"**Docks:** {N_IN} receiving (west, R1 = container dock) and {N_OUT} shipping (east). A trailer door needs ~4.3 m "
    "of wall — the 9.9 m receiving and 9.5 m outbound columns are too narrow on the south wall, so the doors sit on "
    "the side walls. This also separates inbound and outbound truck traffic.",
    "**Aisles:** 3.0 m reach aisles ≥ the ETV 216i working aisle of 2.63–2.79 m (S006); reach trucks travel the "
    "perimeter aisles and the cross-aisle.",
])
figure("layout_floorplan.png", "Fig 9. Detailed warehouse floor plan (rack-level, to scale) — racks, aisles, docks, dimensions.", 17)
figure("layout_orderflow.png", "Fig 10. Main flow on the floor plan: in (R1) → put away → refill → pick → pack → "
       "out (S2). Arrows follow the real truck and picker routes.", 16)
figure("layout_3d_render.png", "Fig 11. Option B in 3D (Blender): rack rows, fast-pick area, zones, 3 receiving doors "
       "(west) and 5 shipping doors (east).", 16)
figure("layout_worker_render.png", "Fig 12. Worker and truck movement (Blender, top-down): pickers on ECE 225, reach "
       "trucks ETV 216i via perimeter and cross-aisle, ERE 225 to the shipping doors.", 16)

# 6 CAPACITY PLAN
doc.add_heading("6. Capacity plan — labour & equipment", level=1)
doc.add_heading("6.1 Labour", level=2)
para(f"Workload drivers are measured: inbound ~{meas['inbound_loads_day']:.0f} loads/day, outbound "
     f"{meas['outbound_pallets_day']:.0f} pallets + {meas['outbound_cartons_day']:.0f} cartons/day, "
     f"{meas['lines_each_day']:.0f} each lines and {meas['lines_case_day']:.0f} case lines/day, replenishment "
     f"~{meas['replen_pallets_day']:.0f} pallets/day. Productivity rates are benchmarks (A014); loose containers are "
     "planned as crew-hours (A019).")
table(["Process", "Rate / h", "Peak ×", "FTE avg", "FTE peak"],
      [[r["Process"], r["Rate/h"], r["Peak factor"], f"{r['FTE avg']:.2f}", f"{r['FTE peak']:.2f}"]
       for r in cp["labour_table"]], widths=[7.0, 2.0, 2.0, 2.4, 2.4])
para(f"**Direct labour ≈ {cp['total_fte_avg']:.1f} FTE on an average day and {cp['total_fte_peak']:.1f} FTE on the "
     f"peak day** (single shift, 7.5 productive hours). Cross-training covers the peak; supervision and admin "
     "come on top.", bold=True, sa=4)
figure("capacity_plan_fte.png", "Fig 13. Labour requirement by process (average vs peak day).", 14)

doc.add_heading("6.2 Machinery — Jungheinrich fleet", level=2)
para("Truck models were chosen from Jungheinrich (as advised) to match the layout and loads, and sized with a "
     "cycle-time model built from their published speeds on the Option B routes (A021).")
table(["Model", "Task", "Equip-h/day avg", "Equip-h/day peak", "Needed", "Planned"],
      [[f["Model"].replace("Jungheinrich ", ""), f["Task"], f"{f['Equip-h/day avg']:.1f}", f"{f['Equip-h/day peak']:.1f}",
        f["Units required (peak)"], f["Units recommended"]] for f in dm["fleet"]],
      widths=[2.2, 6.6, 2.0, 2.0, 1.6, 1.6], arr=2)
bullets([
    "**ETV 216i reach truck (S006):** 1,600 kg, lift 10.7 m, working aisle 2.63–2.79 m, Li-ion. "
    f"{fleet['ETV 216i']['Units required (peak)']} cover the peak; a 3rd keeps putaway and replenishment running "
    "during service. Double-deep storage uses a telescopic-fork attachment (the truck has auxiliary hydraulics, "
    "150 bar / 20 l/min); residual capacity at height to be confirmed with Jungheinrich.",
    "**ECE 225 horizontal order picker (S007):** 2,500 kg, 2.4 m forks — carries 2 pallets or roll cages, so one "
    "trip serves 2 orders (batch picking).",
    "**ERE 225 rider pallet truck (S008):** 2,500 kg, built for loading and unloading trailers and containers; "
    "one per dock side (west and east).",
    "**Charging:** Li-ion opportunity charging — no battery room is needed; chargers sit at the P&D points.",
    "**Plus:** RF / voice terminals per picker, print-and-apply at packing, roll cages for parcel staging.",
])
table(["Move", "Truck", "Avg one-way (m)", "Cycle (min)", "Moves / h"],
      [[c["Move"], c["Truck"], f"{c['Avg one-way m']:.0f}", f"{c['Cycle min']:.2f}", f"{c['Moves/h']:.0f}"]
       for c in dm["cycle_times"]], widths=[6.6, 2.2, 2.6, 2.2, 2.2], arr=2)
para("Fit checks — layout and loads against the truck data:", sa=4)
table(["Check", "Requirement", "Result"],
      [[f["Check"], f["Requirement"], f["Result"]] for f in dm["fit_checks"]], widths=[5.6, 4.6, 5.8], arr=9)

# 7 ASSUMPTIONS
doc.add_heading("7. Assumptions & open questions", level=1)
para("Full register in data/assumptions.json; sources in documentation/sources.md. High-impact items:")
rows = [[a["id"], a["assumption"], a["impact"].upper()] for a in ASSUM["assumptions"] if a["impact"] == "high"]
table(["ID", "Assumption / open question", "Impact"], rows, widths=[1.5, 11.5, 2.0], arr=2)
bullets([
    "**To confirm with DHL:** labour productivity and costs (A006/A014); the 7,000 m² scope (A008); container "
    "share and de-stuff time (A019); whether carriers accept collection time slots (A020).",
    "**To confirm with Jungheinrich:** telescopic-fork residual capacity at 10 m and ECE 225 turning space at aisle "
    "ends (A021).",
])

footer()
DELIV = os.path.join(BASE, "deliverables"); os.makedirs(DELIV, exist_ok=True)
out = os.path.join(DELIV, "Deliverable_2_Future_State.docx")
doc.save(out)
print("Saved:", out)
