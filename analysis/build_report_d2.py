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
        t.autofit = False
        grid = t._tbl.tblGrid
        for i, w in enumerate(widths):
            grid.gridCol_lst[i].w = Cm(w)                      # grid widths: honoured by Word and LibreOffice
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
PK = M["picking"]; segs = {r["segment"]: r for r in PK["segments"]}; dep = dm["departure_plan"]
DE = M["design_evaluation"]
LZ = dm["loose_zone"]; SP = PK["small_parts"]; LGC = dm["load_checks"]["long"]
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
    ["Version", "v3 (with Deliverable 3) — single-deep back-to-back racks, loose-container zone, machinery review"],
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
para("Option B was selected in Deliverable 1. It combines single-deep pallet racking placed back-to-back (one pallet "
     "each side, every pallet reachable from an aisle), a module for odd items, a long-goods module with 4.5 m bays, "
     "bin shelving for small slow parts, and a fast-pick area (carton-flow / shelving) for the "
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
    ["Equipment", "Generic truck types (then ECE 225 for picking)",
     f"Jungheinrich ETV 216i ×{fleet['ETV 216i']['Units recommended']}, EJE 120i ×{fleet['EJE 120i']['Units recommended']}, "
     f"ERE 225 ×{fleet['ERE 225']['Units recommended']} + {fleet['Pick trolley (3-tier, 6 totes) + totes']['Units recommended']} pick trolleys; "
     "ECE 225 dropped (too long for the aisles, 2 pallets far too big for the orders)"],
    ["Picking", "One method for all orders", f"Split by order size: {segs['small']['pct_orders']:.0f}% small orders on trolleys "
     f"(batch), {segs['large']['pct_orders']:.0f}% large orders picked onto a pallet"],
    ["Aisles", "Racks run to 1.5 m from the wall (dead ends)", "Front + rear cross-aisles: every aisle open at both ends — no U-turns"],
    ["Trailers", "Leave whenever loaded", f"Departure plan by carrier ({dep['trailers_planned']} slots); 3 pick waves planned backwards"],
    ["Loose containers", "Unpacked at the dock door", f"Own {LZ['area_planned_m2']} m² loose-container zone at door R1: unpack, sort per SKU, build pallets"],
    ["Racking", "Double-deep (telescopic forks)", f"Single-deep back-to-back: {lay['positions_total']:,} positions incl. {lay['positions_long']} long-goods, standard forks"],
    ["Small parts", "A pallet location each", f"{SP['skus']:,} slow small SKUs in half-bins on {SP['shelf_bays']} shelving bays next to the put-wall"],
    ["08:00 peak", "Treated as customer demand", "Caused by the order-release routine → release in waves"],
], widths=[3.0, 5.0, 8.0], arr=9)

para("The design follows the steps of the Week 3 design approach (Baker & Canessa, 2009, S017) and was iterated "
     "after each feedback round:", sa=4)
table(["Design step (W3)", "Where it is done"], [
    ["Define requirements and objective", "D1 §9 requirements; brief limits 7,000 m² / 12.2 m"],
    ["Collect and analyse data", "D1 §3–8 (SKUs, stock, orders, ABC, peaks); D2 §4.1 inbound"],
    ["Process flows, handling, storage and throughput", "D2 §2 processes; §4 docks, departures, order release"],
    ["Equipment, storage and handling systems, policies", "D2 §3 policies and COI slotting; §6.2–6.3 picking and machinery"],
    ["Layout, zones and flows", "D2 §5, incl. the U-shaped vs flow-through evaluation"],
    ["Evaluate (cost, performance)", "D2 §6 capacity and W3 KPIs; Deliverable 3 CAPEX/OPEX"],
    ["Iterate", "14,074 → 9,500 positions; ECE 225 → trolleys + EJE 120i; front/rear cross-aisles; docks to side walls"],
], widths=[6.0, 10.0], arr=9)

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
    f"**Loose container (door R1, next to the loose-container zone):** dock → a 2-person crew rolls the cartons out on "
    f"an extendable roller conveyor, sorts them by SKU and builds pallets on the build spots → stretch-wrap, print LPN "
    f"labels, scan against the ASN → the pallet goes to normal putaway. About {cp['inbound_pattern']['destuff_h']:.0f} h "
    f"per 40 ft container (A019, A026, Section 4.6).",
    "**Policy applied:** demand-based directed putaway (A/B close to their fast-pick faces, C further away); "
    "pallets over 1 t on low levels; long goods (up to 2.05 m) in the long-goods module via its 3.2 m aisle.",
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
ov = PK["order_volume"]
bullets([
    f"**The order decides the method (A022, A024).** The typical order is only {ov['median_l']:.0f} litres "
    f"({ov['pct_orders_fitting']['1_tote']:.0f}% fit in one tote), while the biggest orders carry most of the volume. "
    "At release the WMS computes each order's volume and weight from the SKU data and sends it down one of three routes:",
    f"**Small orders → pick trolley ({segs['small']['pct_orders']:.0f}% of orders, {segs['small']['pct_lines']:.0f}% of lines):** "
    f"zone batch picking — a picker per zone fills a 6-tote trolley with the wave's lines up to its volume/weight "
    f"limit (~{PK['small_orders'][0]['Lines per tour']:.0f} lines per tour); the put-to-light wall sorts them per order.",
    f"**Large orders → pick-to-pallet with an EJE 120i ({segs['large']['pct_orders']:.0f}% of orders, "
    f"{segs['large']['pct_volume']:.0f}% of volume):** one order per pallet (median {PK['large_orders']['litres_median']:.0f} L, "
    f"{PK['large_orders']['kg_median']:.0f} kg), dropped at packing.",
    f"**Full-pallet lines ({sl.get('full pallet', 0):.0f}% of lines) → ETV 216i** straight from reserve to outbound.",
    f"**Small slow parts ({SP['skus']:,} SKUs, ~{SP['lines_day']:.0f} lines/day) → bin shelving next to the put-wall:** the item "
    "is picked into the order's tote and goes straight into the put-wall — no walk into the reserve aisles.",
    "**Where:** A/B items in the fast-pick area (zone 1); other C items at the low levels of the reserve aisles (zones 2–3). "
    "Aisles are open at both ends, so pickers and pallet trucks walk straight through — no U-turns.",
    "**Why not the ECE 225:** 3.7 m long with 2.4 m forks, it cannot turn in 3.0 m aisles, and its 2 pallets "
    f"(~2,300 L) would need ~{2300 / ov['median_l']:.0f} typical orders to fill one trip (Section 6.3).",
])
figure("flow_picking.png", "Fig 4. Picking flow (zone + batch/wave).", 12)
doc.add_heading("2.4 Consolidation, packing & shipping", level=2)
bullets([
    "**Steps:** picked roll cages → put-to-light sort by order → pack, print-and-apply → parcel cartons onto roll "
    "cages by carrier / pallets wrapped → stage by carrier → live-load at the booked time → dispatch.",
    f"**Measured outbound:** {outd['trailers_per_day_mean']:.0f} trailers/day (p90 {outd['trailers_per_day_p90']:.0f}), "
    f"carrying on average only {outd['pallets_per_trailer_mean']} pallets + {outd['cartons_per_trailer_mean']:.0f} "
    f"cartons; {outd['share_trailers_zero_pallets_pct']:.0f}% of trailers carry no pallets at all (DHL Parcel routes).",
    f"**Policy applied:** carriers book collection time slots from a fixed departure plan (Section 4.5); goods wait in "
    f"the outbound staging lanes, not in parked trailers; {N_OUT} shipping doors on the east wall (Section 4.4).",
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
    ["Storage", "Random within velocity zones; fixed fast-pick faces + random reserve; small slow parts in bins, not on pallets",
     f"73% single-load tail; 48.6% ABC mismatch; {SP['skus']:,} SKUs have ≤ 50 L of stock"],
    ["Slotting", "Demand-ABC; fast movers spread across zones, extreme SKUs duplicated; heavy low",
     "13% SKUs = 80% volume; A = 60% of picks (S003)"],
    ["Zoning", "Fast-pick (A/B) vs reserve; truck routes kept out of the pick zone",
     f"{sl.get('each', 0):.0f}% of order lines are each-picks; safety (S009)"],
    ["Batching", "Small orders: zone batch picking, trolley filled to volume/weight; large: one order per pallet",
     f"median order {ov['median_l']:.0f} L; {segs['large']['pct_volume']:.0f}% of volume in large orders"],
    ["Order release", "3 waves (06:00, 09:30, 12:45) planned backwards from trailer departures",
     f"08:00 = {rel['pick_peak_over_mean_active_hour']}× the mean hour (A023)"],
    ["Routing", "Largest gap in the reserve aisles; return route in the fast-pick area",
     "shortest walk of 4 W3 policies tested (Section 6.2)"],
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

co = DE["coi"]
doc.add_heading("3.2 Slotting by Cube-per-Order Index (COI) and affinity", level=2)
para("W3 key principle: the racking configuration should match each product's turnover, using the COI = storage space "
     "a SKU needs ÷ how often it is picked (S017). Low COI = little space, many picks → closest to packing.", sa=4)
table(["COI quintile", "A SKUs", "B SKUs", "C SKUs"],
      [[r["COI_quintile"], r.get("A", 0), r.get("B", 0), r.get("C", 0)] for r in DE["coi_vs_abc"]], widths=[4.0, 3.0, 3.0, 3.0])
bullets([
    f"**COI confirms the ABC slotting:** the best COI fifth of SKUs carries {co['picks_in_best_quintile_pct']:.0f}% of all "
    f"picks, the best two fifths {co['picks_in_best_two_quintiles_pct']:.0f}% — these fill the fast-pick area first.",
    f"**COI corrects ABC in two places:** {co['bulky_A_skus']} A items are bulky (poor COI) → kept on pallet faces at ground level "
    f"near packing, not in carton-flow; {co['small_fast_C_skus']} C items are tiny but picked often (best COI) → moved into the fast-pick shelving.",
    f"**Affinity:** in multi-line orders, {co['same_family_rate_pct']:.0f}% of item pairs share a product family vs "
    f"{co['random_baseline_pct']:.0f}% by chance → families are slotted together within each zone. Half of all orders are "
    "single-line, so affinity refines COI rather than replacing it.",
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
    "**Future state:** release work in 3 waves — " + ", ".join(f"{w_['wave']} at {w_['start']}" for w_ in dep["waves"]) +
    " (W3 is the same-day wave for orders received before 12:00, Section 4.5). "
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
doc.add_heading("4.5 When trailers leave — departure plan", level=2)
para("Trailers get fixed departure slots, set close to each carrier's current median departure time (measured), and "
     "the picking waves are planned backwards from them: every wave finishes at least 45 minutes before the departure "
     "time of the trailers it feeds, leaving time to pack and stage.")
figure("departure_plan.png", f"Fig 9. Departure slots on the {N_OUT} shipping doors and the 3 pick waves that feed them "
       f"(max {dep['plan_max_doors_busy']} doors busy at once).", 17)
table(["Departure", "Carrier", "Trailers", "Fed by wave"],
      [[d_["Departure"], d_["Carrier"], d_["Trailers"], d_["Fed by wave"]] for d_ in dep["departures"]],
      widths=[2.6, 7.0, 2.2, 3.0], arr=9)
bullets([
    "**Waves:** " + "; ".join(f"{w_['wave']} {w_['start']}–{w_['end']} ({w_['content']})" for w_ in dep["waves"]) + ".",
    f"**Same-day service becomes possible:** {dep['orders_before_noon_pct']:.0f}% of orders arrive before 12:00 and can "
    "go out on the afternoon parcel trailers via wave 3; later orders leave the next day.",
    f"**Doors:** at most {dep['plan_max_doors_busy']} of the {N_OUT} doors are in use at once (25-minute slots), leaving one free "
    "for ex-works pickups that arrive late or early.",
])
doc.add_heading("4.6 Loose containers — their own zone", level=2)
para(f"After the last feedback meeting, loose containers get their own {LZ['area_planned_m2']} m² zone directly behind door R1, "
     "between receiving and returns, so unpacking cartons does not share space with pallet receiving. The zone is sized from "
     f"{LZ['containers_sampled']} Asian receipts in the stock data: a container brings a median of "
     f"{LZ['loads_per_container_median']:.0f} pallets of {LZ['skus_per_container_median']:.0f} SKUs (p75: "
     f"{LZ['loads_per_container_p75']:.0f} pallets, {LZ['skus_per_container_p75']:.0f} SKUs).", sa=4)
table(["Part of the zone", "m²"], [[k, f"{v:.0f}"] for k, v in LZ["parts_m2"].items()] +
      [["+30% walkways → needed", f"{LZ['area_needed_m2']:.0f}"], ["Planned in the layout", f"{LZ['area_planned_m2']}"]],
      widths=[11.0, 3.0])
table(["Who does the work", "How", "DHL labour", "Pros", "Cons"],
      [[c_["Option"], c_["How"], c_["DHL labour"], c_["Pros"], c_["Cons"]] for c_ in dm["container_options"]],
      widths=[3.2, 3.8, 2.2, 3.6, 3.4], arr=9)
para(f"**Is that enough for a big container?** Unpacking spreads cartons over the floor while they are sorted. "
     f"A median container needs ~{LZ['need_m2_median']:.0f} m², the p90 container ~{LZ['need_m2_p90']:.0f} m² and the largest "
     f"({LZ['loads_per_container_max']} pallets, {LZ['skus_per_container_max']} SKUs) ~{LZ['need_m2_max']:.0f} m². "
     f"{LZ['share_fit_zone_pct']:.0f}% of containers fit the zone.", sa=4)
bullets([
    f"**Big containers borrow door R2 (A044):** receiving needs at most ~{LZ['recv_need_m2']:.0f} m² of its 262 m², because "
    f"the two reach trucks put pallets away while the trailer is unloaded (peak ~{LZ['recv_staged_pallets_peak']:.0f} pallets waiting). "
    f"On a big-container day R2 is blocked and the north half of receiving ({LZ['r2_lend_m2']:.0f} m²) becomes extra unpacking "
    f"space: {LZ['area_with_r2_m2']:.0f} m² in total, enough for {LZ['share_fit_with_r2_pct']:.0f}% of containers.",
    f"**Doors still fit:** with R2 blocked, R1 (container) and R3 (trailers) remain — the base and peak scenarios need "
    f"{LZ['doors_needed_base']} doors. R2 is only blocked when the booked arrivals show no second trailer that day.",
    "**The few largest containers** (more SKUs than build spots) are sorted in two passes: first the SKUs with the most "
    "cartons, then the rest from mixed pallets.",
])
PC = M.get("performance_cost", {})
para(f"**Decision rule:** the zone is the same in both cases. A DHL crew costs about €{PC.get('loose_cost_per_container', 0):,.0f} "
     "per container (Deliverable 3); an on-site contractor is chosen only if its fixed price per container is lower (S024). "
     "Port devanning stays the fall-back if containers ever need to arrive palletised.", sa=6)

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
    f"**Storage:** {lay['positions_total']:,} single-deep positions, counted on the drawing ({lay['rack_modules']} back-to-back rack "
    f"modules × 2 rows × {lay['bays_per_row']} bays × 3 pallets × {lay['levels']} levels) against a target of ~{POS_TARGET:,} "
    f"(peak {POS_PEAK:,} occupied locations ÷ 0.90). Top beam {geo['top_beam_m']:.1f} m, within the ETV 216i's 10.7 m lift; "
    f"one module ({lay['positions_odd']:,} positions) holds odd items and one long-goods module holds {lay['positions_long']} pallets "
    f"of up to 2.05 m (4.5 m bays, two pallets each). Small slow parts leave the racks for bin shelving, which frees "
    f"{SP['freed_rack_locations']:,} locations: the peak need drops to ~{POS_PEAK - SP['freed_rack_locations']:,} locations "
    f"({(POS_PEAK - SP['freed_rack_locations']) / lay['positions_total']:.0%} of the racks).",
    f"**Working areas sized from measured volumes:** inbound ~{meas['inbound_loads_day']:.0f} loads/day (peak "
    f"{meas['inbound_max_day']:.0f}); outbound {meas['outbound_pallets_day']:.0f} pallets + "
    f"{meas['outbound_cartons_day']:.0f} cartons/day.",
    f"**Docks:** {N_IN} receiving (west: R1 = container dock beside the loose-container zone, R2–R3 for trailers) and {N_OUT} shipping (east). A trailer door needs ~4.3 m "
    "of wall — the 9.9 m receiving and 9.5 m outbound columns are too narrow on the south wall, so the doors sit on "
    "the side walls. This also separates inbound and outbound truck traffic.",
    "**Aisles open at both ends:** three 3.2 m cross-aisles (front, middle, rear) break up the racking, so no truck or "
    "picker ever needs a U-turn. Storage aisles are 3.0 m — wider than the ETV 216i needs (2.63–2.79 m, S006) and "
    f"far wider than the EJE 120i (1.79–1.94 m, S010); the aisle in front of the long goods is 3.2 m (Section 5.2).",
])
figure("layout_floorplan.png", "Fig 10. Detailed warehouse floor plan (rack-level, to scale) — racks, aisles, docks, dimensions.", 17)
figure("layout_orderflow.png", "Fig 11. Main flow on the floor plan: in (R1) → put away → refill → pick → pack → "
       "out (S2). Arrows follow the real truck and picker routes.", 16)
figure("layout_3d_render.png", "Fig 12. Option B in 3D (Blender): rack rows, fast-pick area, zones, 3 receiving doors "
       "(west) and 5 shipping doors (east).", 16)
figure("layout_worker_render.png", "Fig 13. Worker and truck movement (Blender, top-down): pickers with trolleys in "
       "zones 1–3, reach trucks ETV 216i via perimeter and cross-aisle, ERE 225 to the shipping doors.", 16)

doc.add_heading("5.1 Layout concept: U-shaped or flow-through?", level=2)
para("W3 asks to produce a few basic concepts, evaluate them on travel distance and select the best. The two dock "
     "configurations of Huertas et al. (2007) were compared on the Option B layout, with class-based storage and the "
     "measured inbound mix:", sa=4)
table(["Criterion", "Flow-through (chosen)", "U-shaped"],
      [[r["Criterion"], r["Flow-through"], r["U-shaped"]] for r in DE["concept_table"]], widths=[5.0, 5.5, 5.5], arr=9)
para(f"**Verdict:** {DE['concept_verdict']}", sa=6)
doc.add_heading("5.2 Rack and aisle configuration — the W3 design questions", level=2)
dc = {c["Question (W3)"]: c for c in DE["w3_checks"]}
table(["Question (W3)", "Our answer", "Why"], [
    ["How many aisles?", "10 storage aisles between 11 rack modules", "9 standard modules + 1 odd-items + 1 long-goods module"],
    ["How long is each aisle?", "~56 m, split into two runs of ~26.5 m", "middle cross-aisle halves the walk to any face"],
    ["Cross-aisles — where, how many?", "3: front, middle, rear (3.2 m)", "aisles open at both ends → largest-gap routing, no U-turns; costs ~6% rack length"],
    ["How do pallets go into the racking?", "EUR 800×1200 with the 800 mm side to the aisle, 3 per 2.7 m bay; one pallet deep per side, racks back-to-back; long pallets (≤ 2.05 m) 2 per 4.5 m bay", "standard forks on the ETV 216i; long pallets forked on the long side (load centre 400 mm → full 1.6 t)"],
    ["How wide is the aisle?", "3.0 m storage, 3.2 m for long goods and cross/perimeter", f"ETV 216i needs 2.63–2.79 m; with a 2.05 m load crosswise {LGC['ast_long_crosswise_mm']:.0f} mm (VDI formula on S006 data)"],
    ["1-way or 2-way traffic?", "storage aisles: one truck at a time; main aisles: trucks one-way (west up with put-aways, east down to packing)", "pickers stay in their zones; fewer crossings"],
    ["How high is each level? All the same?", "1.41 m pitch → 8 levels; taller loads on the top level", "p90 load height 1.16 m + 0.25 m beam/clearance; top load ~1 m under the roof"],
    ["Product characteristics?", f"heaviest item {dc['Heaviest SKU (single item)']['Answer'].split('— ')[-1]}; pallets > 1 t low; longest real item ~2 m",
     f"mechanical handling only for heavy items; {LGC['loads_over_2_05m_data_error']} loads recorded longer than 2.05 m (up to an '11 m' item of 0.5 kg) are data errors"],
], widths=[3.6, 6.2, 6.2], arr=9)
hzd = DE["hazmat"]
doc.add_heading("5.3 Legal aspects of pallet storage", level=2)
bullets([
    "**Racking (EN 15512 / EN 15635, S015):** racks designed to EN 15512; in use, a trained employee inspects visually every "
    "week and a competent expert at least every 12 months; damage is classed green/amber/red and every bay shows a load sign.",
    "**Fire safety:** the top of the highest load stays ~1 m below the 12.2 m roof (sprinkler clearance assumed ≥ 0.5 m, A011 — "
    "to confirm against the sprinkler design).",
    f"**Hazardous goods (rechecked, A028):** {hzd['skus']} SKUs, {hzd['loads']:,} loads ({hzd['share_loads_pct']:.0f}% of loads), "
    f"~{hzd['kg_in_stock'] / 1000:.0f} t gross — counted per load, the same way in all three snapshots "
    f"({', '.join(f'{x['loads']:,}' for x in hzd['by_snapshot'])} loads). The customs codes show what they are (table below): "
    f"{hzd['pgs37_share_loads_pct']:.0f}% are electronic safes, locks, alarms, cameras and readers — most likely lithium cells built "
    "into the product (UN3481/UN3091, class 9). Those fall under PGS 37-2 (lithium energy carriers, from 333 kg; 1,000 kg for "
    "small cells, S029), not PGS 15. Only the lubricants (possibly aerosols) fall under PGS 15 (S016). A separate hazmat "
    "section is reserved; its fire separation follows PGS 37-2 once Assa Abloy confirms the UN numbers.",
    "**Manual handling:** totes are limited to 15 kg (A024); items up to 90 kg each are only moved with pallet trucks or lift aids.",
])
table(["Customs code", "What it is", "Likely hazard", "Dutch rule", "SKUs", "Loads", "Tonnes"],
      [[c["HS"], c["What it is"], c["Likely hazard"], c["Dutch rule"], c["SKUs"], f"{c['Loads']:,}", f"{c['t']:.0f}"] for c in hzd["classes"]],
      widths=[1.6, 3.6, 4.2, 1.8, 1.2, 1.4, 1.4], arr=4)
OA, PA = dm["outbound_area"], dm["packing_area"]
doc.add_heading("5.4 Are the outbound staging and packing areas big enough?", level=2)
para(f"**Outbound staging (216 m²):** the goods of all afternoon trailers wait at the same time after wave 3. Measured per day "
     f"(pallets × 1.9 m² + roll cages × 1.0 m², +30% lanes): median {OA['need_m2_median']:.0f} m², p90 {OA['need_m2_p90']:.0f} m², "
     f"busiest day {OA['need_m2_max']:.0f} m². 216 m² holds every day of Q2 with room for 2× the volume (stress test, D3).", sa=4)
para(f"**Packing (450 m²)** — what has to fit:", sa=4)
table(["Part", "m²"], [[k, f"{v:.0f}"] for k, v in PA["parts_m2"].items()] +
      [["Total incl. 30% walkways (shelving already incl. aisles)", f"{PA['need_m2']:.0f}"], ["Planned", "450"]], widths=[12.0, 2.0])

# 6 CAPACITY PLAN
doc.add_heading("6. Capacity plan — labour & equipment", level=1)
doc.add_heading("6.1 Labour", level=2)
para(f"Workload drivers are measured: inbound ~{meas['inbound_loads_day']:.0f} loads/day, outbound "
     f"{meas['outbound_pallets_day']:.0f} pallets + {meas['outbound_cartons_day']:.0f} cartons/day, "
     f"{meas['lines_each_day']:.0f} each lines and {meas['lines_case_day']:.0f} case lines/day, replenishment "
     f"~{meas['replen_pallets_day']:.0f} pallets/day. Picking hours come from the pick-time model in Section 6.2; other "
     "rates are benchmarks (A014). Unpacking loose containers is shown on its own line and not counted in the DHL FTE "
     "below, because it can be done by a DHL crew or a contractor (A026, costed in Deliverable 3).")
table(["Process", "Rate / h", "Peak ×", "FTE avg", "FTE peak"],
      [[r["Process"], r["Rate/h"], r["Peak factor"], f"{r['FTE avg']:.2f}", f"{r['FTE peak']:.2f}"]
       for r in cp["labour_table"]], widths=[7.0, 2.0, 2.0, 2.4, 2.4])
para(f"**Direct DHL labour ≈ {cp['total_fte_avg']:.1f} FTE on an average day and {cp['total_fte_peak']:.1f} FTE on the "
     f"peak day** (single shift, 7.5 productive hours; loose-container unpacking excluded). Cross-training covers the peak; supervision and admin "
     "come on top.", bold=True, sa=4)
figure("capacity_plan_fte.png", "Fig 14. Labour requirement by process (average vs peak day).", 14)

doc.add_heading("6.2 Picking — how many people, how efficient", level=2)
para("The picking method is matched to the demand profile — small, light orders with a few lines, plus a minority of "
     "pallet-sized orders — using the standard order-picking choices: picker-to-parts, low-level picking, batching and "
     "zoning (S014). Pick times are modelled on the Option B layout: walking (return route in the fast-pick area; in the reserve "
     "aisles the best of the four W3 routing policies, which is largest gap) + picking + setup, with a 10% delay allowance (A025).")
figure("picking_order_volume.png", "Fig 15. Share of orders that fit each carrier: one tote, four totes, one pallet, two pallets (240×80).", 14)
table(["Segment", "Orders / day", "Lines / day", "% orders", "% lines", "% volume"],
      [[r["segment"].title(), f"{r['orders_day']:.0f}", f"{r['lines_day']:.0f}", f"{r['pct_orders']:.0f}%",
        f"{r['pct_lines']:.0f}%", f"{r['pct_volume']:.0f}%"] for r in PK["segments"]], widths=[3.0, 2.6, 2.6, 2.4, 2.4, 2.4])
table(["Small orders — zone", "Lines / day", "Lines / tour", "Walk / tour (m)", "Lines / h", "Picker-h peak"],
      [[r["Zone"], f"{r['Lines/day']:.0f}", f"{r['Lines per tour']:.0f}", f"{r['Walk per tour (m)']:.0f}",
        f"{r['Lines/h']:.0f}", f"{r['Picker-h peak']:.1f}"] for r in PK["small_orders"]], widths=[4.6, 2.2, 2.2, 2.6, 2.0, 2.4])
lgo = PK["large_orders"]
bullets([
    f"**Large orders (EJE 120i):** {lgo['orders_day']:.0f} orders/day, ~{lgo['lines_per_order']:.0f} lines each "
    f"({lgo['lines_fast_pick']:.0f} in the fast-pick area, {lgo['lines_reserve']:.0f} in the reserve), ~{lgo['walk_per_order_m']:.0f} m "
    f"and ~{lgo['min_per_order']:.0f} min per order → {lgo['lines_per_h']:.0f} lines/h.",
    f"**Picking needs {PK['pick_fte_avg']:.1f} FTE on an average day and {PK['pick_fte_peak']:.1f} on the peak day.** "
    "Trolley batching makes small-order picking about twice as fast as one-order-per-tote picking in the reserve zone.",
    "**How the volume per trip is ensured:** each trolley batch is closed at 80% of its volume (240 L) or weight (250 kg), "
    "computed from SKU dimensions — so no trip is overloaded and none runs nearly empty.",
])
table(["Item", "Use", "Needed", "Planned", "Why this number"],
      [[e["Item"], e["Use"], e["Required"], e["Planned"], e["Why this number"]] for e in PK["equipment"]],
      widths=[4.2, 4.4, 1.6, 1.6, 4.2], arr=2)
tg = PK["tugger"]
para(f"**Tugger train (Jungheinrich EZS 130) — evaluated, not planned now.** It fits zone picking (pickers stay in their "
     f"zone and a train collects the trolleys), and the EZS 130 is built for small-parts tow trains (600 mm wide, tows 3 t, "
     f"S012). But with batching there are only ~{tg['trolleys_per_day']:.0f} trolley trips a day: a {tg['loop_m']:.0f} m loop "
     f"every 20 minutes would keep a driver ~{tg['driver_utilisation_pct']:.0f}% busy to save pickers ~"
     f"{tg['picker_walk_saved_h_day'] * 60:.0f} minutes of walking, because both pick zones end next to packing. "
     "It becomes worthwhile if small-order volume roughly triples or packing moves away from the pick zones.", sa=8)

para("Routing policy (W3) — expected walk per tour in the reserve zone, by policy:", sa=4)
table(["Tour", "Lines in reserve", "S-shape", "Return", "Midpoint", "Largest gap", "Best"],
      [[r["Tour"], f"{r['Lines in reserve']:.0f}", f"{r['S-shape']:.0f} m", f"{r['Return']:.0f} m", f"{r['Midpoint']:.0f} m",
        f"{r['Largest gap']:.0f} m", r["Best"]] for r in PK["routing"]], widths=[4.6, 1.8, 1.8, 1.8, 1.8, 2.0, 2.2], arr=1)
para("Largest-gap routing is used in the reserve aisles (possible because the aisles are open at both ends); the fast-pick "
     "area is a single long face worked with a return route from packing.", sa=6)
para("Data-handling hardware (W3):", sa=4)
table(["Option", "Fit with our profile", "Decision"], [
    ["Paper pick lists", "5,291 SKUs, many look-alike parts, half the orders single-line → error-prone, no live stock", "Not used"],
    ["RF handheld / ring scanner", "scan-to-confirm location and item; works for receiving, put-away, trolleys and pallets", "Used in all processes"],
    ["Voice picking", "hands-free, good for heavy case picking, but item check still needs a scan", "Option for large-order picking"],
    ["Pick-to-light", "fastest per pick, but a light on thousands of faces is costly for ~640 lines/day", "Not used in pick zones"],
    ["Put-to-light wall", f"sorts batch-picked small orders ({segs['small']['pct_orders']:.0f}% of orders) into orders at packing", "Used at packing"],
], widths=[3.6, 8.4, 4.0], arr=9)

doc.add_heading("6.3 Machinery — Jungheinrich fleet", level=2)
para("Truck models were chosen from Jungheinrich (as advised) to match the layout and loads, and sized with a "
     "cycle-time model built from their published speeds on the Option B routes (A021).")
table(["Model", "Task", "Equip-h/day avg", "Equip-h/day peak", "Needed", "Planned"],
      [[f["Model"].replace("Jungheinrich ", ""), f["Task"], f"{f['Equip-h/day avg']:.1f}", f"{f['Equip-h/day peak']:.1f}",
        f["Units required (peak)"], f["Units recommended"]] for f in dm["fleet"]],
      widths=[2.2, 6.6, 2.0, 2.0, 1.6, 1.6], arr=2)
bullets([
    "**ETV 216i reach truck (S006):** 1,600 kg, lift 10.7 m, working aisle 2.63–2.79 m, Li-ion. "
    f"{fleet['ETV 216i']['Units required (peak)']} cover the peak day and one is enough on an average day, so a breakdown "
    "never stops putaway (no spare needed; the lease includes repair). The racks are single-deep, so the truck uses "
    "standard forks — no telescopic attachment and no loss of capacity at height.",
    "**EJE 120i walkie pallet truck (S010):** 2,000 kg, only 1.58 m long and 0.72 m wide — picks large orders onto a "
    "pallet and moves through the aisles without turning problems.",
    "**Pick trolleys (S011):** 3-tier, 1,000 × 600 mm, 250 kg, 6 totes — for the small orders.",
    "**ERE 225 rider pallet truck (S008):** 2,500 kg, built for loading and unloading trailers and containers; "
    "one per dock side (west and east).",
    "**Charging:** Li-ion opportunity charging — no battery room is needed; chargers sit at the P&D points.",
    "**Plus:** RF / voice terminals per picker, print-and-apply at packing, roll cages for parcel staging.",
])
para("Why each machine, and how it is used:", sa=4).paragraph_format.keep_with_next = True
table(["Machine", "Process", "Why (data)", "How it is used", "Units"],
      [[j_["Machine"], j_["Process"], j_["Why (data)"], j_["How it is used"], j_["Units"]] for j_ in dm["justification"]],
      widths=[2.8, 2.8, 4.8, 4.4, 1.2], arr=4)
para("Truck dimensions and turning — can every machine move where it has to?", sa=4).paragraph_format.keep_with_next = True
table(["Machine", "Size (L × W)", "Turning / aisle needed", "Where it drives", "Result"],
      [[t_["Machine"], t_["Size (L x W)"], t_["Turning / aisle needed"], t_["Where it drives"], t_["Result"]]
       for t_ in dm["turning_check"]], widths=[3.0, 2.8, 3.2, 3.4, 3.6], arr=9)
table(["Move", "Truck", "Avg one-way (m)", "Cycle (min)", "Moves / h"],
      [[c["Move"], c["Truck"], f"{c['Avg one-way m']:.0f}", f"{c['Cycle min']:.2f}", f"{c['Moves/h']:.0f}"]
       for c in dm["cycle_times"]], widths=[6.6, 2.2, 2.6, 2.2, 2.2], arr=2)
para("Fit checks — layout and loads against the truck data:", sa=4).paragraph_format.keep_with_next = True
table(["Check", "Requirement", "Result"],
      [[f["Check"], f["Requirement"], f["Result"]] for f in dm["fit_checks"]], widths=[5.6, 4.6, 5.8], arr=9)

doc.add_heading("6.4 Expected performance on the W3 KPIs", level=2)
para("W3 names the KPIs that layout, storage and picking design drive. Expected values for Option B (Deliverable 3 adds cost "
     "and the full KPI set):", sa=4).paragraph_format.keep_with_next = True
table(["KPI (W3)", "Expected", "Basis"],
      [[k["KPI (W3)"], k["Expected"], k["Basis"]] for k in DE["kpis"]], widths=[3.4, 6.2, 6.4], arr=9)

# 7 ASSUMPTIONS
doc.add_heading("7. Assumptions & open questions", level=1)
para("Full register in data/assumptions.json; sources in documentation/sources.md. High-impact items:")
rows = [[a["id"], a["assumption"], a["impact"].upper()] for a in ASSUM["assumptions"] if a["impact"] == "high"]
table(["ID", "Assumption / open question", "Impact"], rows, widths=[1.5, 11.5, 2.0], arr=2)
bullets([
    "**To confirm with DHL:** labour productivity and pick-time standards (A006/A014/A025); the 7,000 m² scope (A008); "
    "container share and contractor quotes (A019/A026); whether carriers accept the departure slots (A020/A027).",
    "**To confirm with Jungheinrich:** a lease quote for 2 ETV 216i, 3 EJE 120i and 2 ERE 225 (A038).",
    "**To confirm with Assa Abloy:** the hazard class of the 138 flagged SKUs, which decides the hazmat section (A028).",
])

footer()
DELIV = os.path.join(BASE, "deliverables"); os.makedirs(DELIV, exist_ok=True)
out = os.path.join(DELIV, "Deliverable_2_Future_State.docx")
doc.save(out)
print("Saved:", out)
