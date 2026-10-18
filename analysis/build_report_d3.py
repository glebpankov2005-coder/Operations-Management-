"""
Build the Deliverable 3 (Performance overview: KPIs + CAPEX/OPEX) Word document.
Reads outputs/reports/phase1_metrics.json (performance_cost, dock_mhe, layout, picking, capacity_plan sections),
figures and data/assumptions.json; writes deliverables/Deliverable_3_Performance_Overview.docx.
Run performance_cost.py first.
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
    if t.rstrip().endswith(":"): p.paragraph_format.keep_with_next = True   # lead-in stays with its table
    p.paragraph_format.space_after = Pt(sa); return p


def bullets(items):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        for i, seg in enumerate(it.split("**")):
            r = p.add_run(seg); r.bold = (i % 2 == 1); r.font.size = Pt(10.5)


def table(headers, rows, widths=None, arr=1, bold_last=False):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Light Grid Accent 1"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        t.rows[0].cells[i].text = ""; r = t.rows[0].cells[i].paragraphs[0].add_run(str(h)); r.bold = True; r.font.size = Pt(9.5)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; p = cells[i].paragraphs[0]; r = p.add_run(str(v)); r.font.size = Pt(9.5)
            r.bold = bold_last and ri == len(rows) - 1
            if i >= arr: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if widths:
        t.autofit = False
        grid = t._tbl.tblGrid
        for i, w in enumerate(widths):
            grid.gridCol_lst[i].w = Cm(w)                      # grid widths: honoured by Word and LibreOffice
            for row in t.rows: row.cells[i].width = Cm(w)
    for ri, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
        if ri < len(t.rows) - 1:
            for c in row.cells:
                for p in c.paragraphs: p.paragraph_format.keep_with_next = True
    doc.add_paragraph().paragraph_format.space_after = Pt(2); return t


def figure(name, cap, w=15.5):
    p = os.path.join(FIGS, name)
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    doc.add_picture(p, width=Cm(w)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.paragraphs[-1].paragraph_format.keep_with_next = True
    para(cap, size=8.5, color=GREY, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=10)


def footer():
    f = doc.sections[0].footer.paragraphs[0]; f.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = f.add_run("Project OTM — Assa Abloy @ DHL Bemmel  ·  Deliverable 3 (Performance overview)  ·  Page")
    run.font.size = Pt(8); run.font.color.rgb = GREY
    fld = OxmlElement("w:fldSimple"); fld.set(qn("w:instr"), "PAGE"); run._r.addnext(fld)


def eur(v, k=False):
    return f"€{v / 1000:,.0f}k" if k else f"€{v:,.0f}"


PC = M["performance_cost"]; DM = M["dock_mhe"]; LAY = M["layout"]; PK = M["picking"]; CP = M["capacity_plan"]
Q = PC["quantities"]; LT = PC["leadtime"]; SORT = PC["sorting"]; STO = PC["storage"]; LZ = DM["loose_zone"]
fleet = {f["Model"].replace("Jungheinrich ", ""): f for f in DM["fleet"]}
seg = {r["segment"]: r for r in PK["segments"]}
kp = {k["KPI"]: k for k in PC["kpis"]}
LC = DM["load_checks"]
PTL_COST = sum(r["Total EUR"] for r in PC["capex_table"] if r["Item"].startswith("Put-to-light"))

# ================================================================ COVER
doc.add_paragraph().paragraph_format.space_before = Pt(55)
para("PROJECT OTM", size=13, color=RED, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=2)
para("Performance Overview — KPIs, CAPEX & OPEX", size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, sa=2)
para("Assa Abloy operation · DHL Supply Chain, Bemmel (NL_0032)", size=12, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER, sa=26)
table(["Field", "Detail"], [
    ["Deliverable", "3 — Performance overview including financial analysis"],
    ["Due date", "21-10-2026"],
    ["Concept", "Option B — single-deep racks, fast-pick area, zone + batch picking, wave release"],
    ["Envelope", f"≤ 7,000 m² · ≤ 12.2 m (design uses {LAY['total_area_m2']:,} m²)"],
    ["Team", "Group 3 — Gleb, Rachel Selvarathnam, Arnau, Vidhi"],
    ["Supporting files", "Deliverable_3_Calculations.xlsx (all cost formulas) · Deliverables 1 and 2 (updated) · analysis/*.py"],
], widths=[4.5, 11], arr=9)
para("Expected performance and cost of the Option B design. Volumes are measured in the Assa Abloy Q2-2025 data; "
     "prices are public benchmarks or labelled assumptions (Section 7), never quotes. Every number can be rebuilt with "
     "analysis/performance_cost.py and checked in the calculation workbook.", size=9, color=GREY, italic=True)
doc.add_page_break()

doc.add_heading("Contents", level=1)
_p = doc.add_paragraph()
_fld = OxmlElement("w:fldSimple"); _fld.set(qn("w:instr"), 'TOC \\o "1-2" \\h \\z \\u')
_r = OxmlElement("w:r"); _t = OxmlElement("w:t")
_t.text = "(In Word: right-click → Update Field to build the table of contents.)"
_r.append(_t); _fld.append(_r); _p._p.append(_fld)
doc.add_page_break()

# ================================================================ SUMMARY
doc.add_heading("Summary", level=1)
para("What the design delivers, what it costs, and what to watch:", sa=4)
table(["", "Result"], [
    ["Picking effort", f"{PC['pick_today_staffed_h']:.0f} → {PC['pick_future_h']:.0f} picker-hours a day (batching, fast-pick area, wave release)"],
    ["Order lead time", f"orders out within 24 h: {LT['today_within_24h_pct']:.0f}% → {LT['future_within_24h_pct']:.0f}%; "
                        f"slowest 10% wait {LT['today_p90_h']:.0f} h → {LT['future_p90_h']:.0f} h"],
    ["Trailers at the doors", f"{DM['outbound_doors']['current_drop_trailer_concurrent_p90']:.0f} parked at once → max "
                              f"{DM['departure_plan']['plan_max_doors_busy']} of {DM['outbound_doors']['doors_recommended']} doors"],
    ["Storage", f"{LAY['positions_total']:,} single-deep positions in {LAY['total_area_m2']:,} m² ({LAY['pct_of_7000']:.0f}% of 7,000 m²)"],
    ["People and trucks", f"{STO['fte_avg']:.1f} FTE on an average day, {STO['fte_peak']:.1f} on the peak day; "
                          f"{Q['etv']} ETV 216i, {Q['eje']} EJE 120i, {Q['ere']} ERE 225, {Q['trolleys']} trolleys"],
    ["One-off investment (CAPEX)", f"{eur(PC['capex_total'], True)} as all-new equipment; {eur(PC['capex_reuse_racking'], True)} if today's racking can be re-used"],
    ["Running cost (OPEX)", f"{eur(PC['opex_total'], True)} a year ({PC['unit_cost']['labour_share_pct']:.0f}% of the yearly cost is labour); "
                            f"{eur(PC['annual_cost'], True)} incl. depreciation"],
    ["Cost per unit", f"€{PC['unit_cost']['per_order_line']:.2f} per order line · €{PC['unit_cost']['per_order']:.2f} per order"],
    ["Saving and payback", f"~{eur(PC['saving_year'], True)} a year in picking labour → payback {PC['payback_reuse_years']:.1f} years "
                           f"(re-used racking) or {PC['payback_years']:.1f} years (all new)"],
], widths=[4.4, 11.6], arr=9)
bullets([
    "**The biggest win is in picking and planning, not in steel.** Batching small orders, a fast-pick area for the best-sellers "
    "and releasing work in waves cut the picking hours by about two thirds. The racking is the biggest cost but saves little labour on its own.",
    f"**Watch the storage space.** Occupied locations grew {STO['growth_per_quarter_pct']:.0f}% a quarter between April and June. If that "
    f"continues, the {LAY['positions_total']:,} positions are full in about {STO['months_headroom']:.0f} months. Clearing dead "
    "stock (21% of loads have been in stock for more than a year, D1) and keeping room for a 12th rack module are part of the plan.",
    f"**Machinery was checked again:** single-deep racks need no telescopic forks; with a full-service lease no spare trucks are "
    f"needed, so the fleet goes from 3 to {Q['etv']} reach trucks and from 4 to {Q['eje']} pallet trucks (Section 4).",
    f"**Loose containers get their own {LZ['area_planned_m2']} m² zone** at door R1. A DHL crew costs about "
    f"€{PC['loose_cost_per_container']:,.0f} per container; a contractor is only worth it below that price.",
])
doc.add_page_break()

# ================================================================ 1 WHAT CHANGED
doc.add_heading("1. What changed since Deliverable 2", level=1)
para("Feedback and a final check of the design led to these changes. Deliverables 1 and 2 were regenerated so all three "
     "documents use the same numbers.", sa=4)
table(["Topic", "Before (D1 / D2)", "Now", "Why"], [
    ["Racking", "Double-deep, telescopic forks", f"Single-deep, back-to-back ({LAY['positions_total']:,} positions)",
     "Team decision: no two-deep racks; every pallet now directly reachable"],
    ["Loose containers", "Unpacked at door R1", f"Own {LZ['area_planned_m2']} m² zone behind R1",
     "Feedback from the last meeting: a separate zone for loose containers"],
    ["Reach trucks", "3 × ETV 216i", f"{Q['etv']} × ETV 216i", "2 cover the peak day; lease includes repair"],
    ["Pallet trucks", "4 × EJE 120i", f"{Q['eje']} × EJE 120i", "3 cover the peak day"],
    ["Floor area", "6,541 m² (93%)", f"{LAY['total_area_m2']:,} m² ({LAY['pct_of_7000']:.0f}%)", "+190 m² container zone"],
    ["Lead time", "counted per order line (median 52 h)", f"counted per order (median {LT['today_median_h']:.0f} h)",
     "an order is what the customer waits for"],
], widths=[2.8, 3.8, 4.2, 5.2], arr=9)
figure("layout_orderflow.png", "Fig 1. Updated floor plan with the loose-container zone (C) and the main order flow (1–6).", 16.5)

# ================================================================ 2 KPIs
doc.add_heading("2. KPIs — how we will measure the design", level=1)
para("We chose KPIs that cover every part of the operation and that DHL can measure with its own WMS. They follow the "
     "W3 lecture list (dock-to-stock, put-away time, pick rate, on-time shipment, S017) and add space, people, machinery, "
     "cost and safety. Each KPI has a clear way to measure it, today's value where the data shows it, the value we expect "
     "from the design, and a target.", sa=4)
for grp in ["Space", "Inbound", "Picking", "Service", "Docks", "People", "Machinery", "Cost", "Safety"]:
    rows = [[k["KPI"], k["How it is measured"], k["Today (data)"], k["Future (design)"], k["Target / benchmark"]]
            for k in PC["kpis"] if k["Group"] == grp]
    if not rows:
        continue
    para(f"**{grp}**", sa=2).paragraph_format.keep_with_next = True
    table(["KPI", "How it is measured", "Today (data)", "Future (design)", "Target"], rows,
          widths=[3.0, 3.6, 3.0, 3.8, 2.6], arr=9)

doc.add_heading("2.1 Order lead time", level=2)
figure("d3_leadtime.png", "Fig 2. Share of orders shipped within X hours — today (measured) vs future (wave plan, modelled).", 15)
bullets([
    f"**Today (measured, {LT['orders']:,} orders):** median {LT['today_median_h']:.0f} h, average {LT['today_mean_h']:.0f} h, "
    f"slowest 10% {LT['today_p90_h']:.0f} h or more. Only {LT['today_within_24h_pct']:.0f}% of orders leave within 24 hours.",
    "**Future (modelled on the same orders):** an order received before 12:00 is picked in wave 3 and leaves on the same "
    "afternoon's trailer of its carrier; a later order is picked in the first wave next morning and leaves on that day's "
    "first slot of its carrier. Weekends are skipped.",
    f"**Result:** {LT['future_within_24h_pct']:.0f}% within 24 hours and the slowest 10% at {LT['future_p90_h']:.0f} h. "
    f"The median moves less ({LT['today_median_h']:.0f} → {LT['future_median_h']:.0f} h) because 55% of orders arrive "
    "between 15:00 and 17:00 and still leave the next day — the gain is that no order waits for a second or third day.",
])
doc.add_heading("2.2 Picking effort — where the saving comes from", level=2)
figure("d3_levers.png", "Fig 3. Picker-hours per average day: today's way of working (modelled) vs the design.", 15)
lv = PC["levers"]
table(["Lever", "Today h/day", "Future h/day", "Saved h/day", "Saved per year"],
      [[r["Lever"], f"{r['Today h/day']:.1f}", f"{r['Future h/day']:.1f}", f"{r['Saved h/day']:.1f}", eur(r["Saved EUR/yr"])] for r in lv],
      widths=[6.6, 2.2, 2.2, 2.2, 2.8])
para("Today is modelled with the same pick-time model and rates as the design (D2 §6.2), but the way the data says the "
     "site works now: one order per tour, stock not placed by demand (the WMS class agrees with demand for only 48.6% of "
     f"SKUs), and all orders released in the evening so the morning starts at {DM['order_release']['pick_peak_over_mean_active_hour']}× "
     "the average workload. It is a model, not a measurement — DHL's real pick hours would confirm it (A006).", size=9.5, color=GREY)

doc.add_heading("2.3 Storage space — the main risk", level=2)
bullets([
    f"**Positions:** {LAY['positions_total']:,} against a peak of {STO['occupied_peak']:,} occupied locations "
    f"({STO['occupied_peak'] / LAY['positions_total']:.0%} full at the peak, {STO['occupied_mean'] / LAY['positions_total']:.0%} on average).",
    f"**Growth:** occupied locations rose from 7,715 (April) to 8,512 (June), +{STO['growth_per_quarter_pct']:.0f}% per quarter. "
    f"At that speed the racks are full in ~{STO['months_headroom']:.0f} months. Three months of data cannot tell whether this is a "
    "season or a trend, so DHL should track the KPI monthly.",
    "**What we do about it:** (1) clear dead stock — 21% of loads are older than one year (D1 Fig 2b); (2) the core has room for a "
    "12th rack module (+864 positions); (3) the remaining ~270 m² of the 7,000 m² envelope stays free.",
])
doc.add_heading("2.4 Stress test — 150%, 200% and 250% volume", level=2)
para("Promised in D2 §3.1: what happens when volume grows? Workload scales with volume; the layout and doors are checked "
     "against the same rules as in D2.", sa=4)
figure("d3_stress.png", "Fig 4. Direct FTE and trucks needed on the peak day at higher volumes.", 13.5)
table(["Volume", "Direct FTE (peak day)", "ETV 216i", "EJE 120i", "ERE 225", "Outbound doors", "Pickers in busiest wave"],
      [[s["Volume"], f"{s['Direct FTE (peak day)']:.1f}", s["ETV 216i needed"], s["EJE 120i needed"], s["ERE 225 needed"],
        s["Outbound doors (busiest hour)"], s["Pickers in the busiest wave"]] for s in PC["stress"]],
      widths=[2.0, 2.8, 1.8, 1.8, 1.8, 2.4, 3.0])
bullets([
    f"**Up to 150%** the design runs as planned: one extra reach truck and pallet truck, and all 5 shipping doors in use.",
    "**At 200% and more** the 5 shipping doors are not enough in the busiest hour; the departure plan would need more spread "
    "(more slots before 12:00) or a 6th door — and storage would need the 12th module and a dead-stock clean-up first.",
    "**Pickers per zone stay low** (≤ 7 in the busiest wave at 250%), so congestion in the aisles is not the limit.",
])

# ================================================================ 3 SORTING
doc.add_heading("3. Sorting — what, how and when", level=1)
para("Sorting means putting goods into the right group for the next step. In our design it happens in four places. "
     "Each one is simple, uses a scan to check the item, and happens at a fixed moment in the day.", sa=4)
table(["Where", "What is sorted", "How", "When", "Equipment"], [
    ["1. Loose-container zone (door R1)", "Cartons from a container → one pallet per SKU",
     f"Cartons roll out on the conveyor; the worker scans each carton and puts it on the build spot of its SKU (a container has "
     f"{SORT['container_skus_median']:.0f} SKUs on average, so {SORT['build_spots']} build spots are enough). Full pallet → wrap, label, putaway.",
     "Morning, when the container arrives (~3 h)", "Roller conveyor, RF scanner, stretch wrapper"],
    ["2. Put-to-light wall (packing)", "Picked items → customer orders",
     f"Pickers collect the items of many small orders in one trolley tour (~{SORT['lines_per_tour']:.0f} lines). At the wall the packer "
     f"scans an item, a light shows the order's slot, the item goes in and the button is pressed. A full slot lights up → pack.",
     f"During each wave (3 a day, ~{SORT['small_orders_wave_avg']:.0f} small orders per wave)", f"Wall with {SORT['ptl_slots']} slots"],
    ["3. Carrier lanes (outbound)", "Packed parcels and pallets → trailer",
     f"The label says the carrier and departure slot. Parcels go into roll cages per carrier, pallets into the staging lane of "
     f"their trailer ({SORT['staging_lanes']} trailer slots a day).", "All afternoon, until each trailer's departure",
     f"{SORT['roll_cages']} roll cages, floor lanes"],
    ["4. Returns", "Returned goods → restock / rework / scrap", "Inspect and grade, then each group goes to its own cage.",
     "When a return arrives", "Returns area, RF scanner"],
], widths=[2.8, 2.8, 5.6, 2.6, 2.2], arr=9)
figure("d3_sorting_timeline.png", "Fig 5. When the sorting points are busy during a normal day.", 16)
bullets([
    f"**Why a put-to-light wall and not sorting by hand:** {seg['small']['pct_orders']:.0f}% of orders are small (median "
    f"{PK['order_volume']['median_l']:.0f} litres). Picking them one by one would mean ~{SORT['small_orders_day']:.0f} walks a day; "
    "picking them together and sorting at the wall is about twice as fast (D2 §6.2).",
    f"**Why not an automatic sorter:** ~{SORT['small_orders_day']:.0f} small orders a day is far too little for a sorter "
    f"machine to pay off; the wall costs about {eur(PTL_COST, True)} (Section 5).",
    "**Large orders are not sorted:** each one is picked straight onto its own pallet, so it goes directly to packing.",
])

# ================================================================ 4 MACHINERY
doc.add_heading("4. Machinery — is everything fit and justified?", level=1)
para("Each machine was checked against three questions: does it have a job every day, does it fit the loads and the "
     "aisles, and is the number right?", sa=4)
mach = [
    ["ETV 216i reach truck", "Putaway, refill fast-pick area, full pallets", f"3 → {Q['etv']}",
     f"{fleet['ETV 216i']['Utilisation avg %']:.0f}%", "Yes: 10.7 m lift for the 10.0 m top beam; single-deep → standard forks",
     "Keep. 2 cover the peak day; a breakdown still leaves enough for an average day."],
    ["EJE 120i pallet truck", "Large orders picked onto a pallet", f"4 → {Q['eje']}",
     f"{fleet['EJE 120i']['Utilisation avg %']:.0f}%", "Yes: 0.72 m wide, no U-turns needed", "Keep 3 (peak need)."],
    ["ERE 225 rider pallet truck", "Unload / load trailers, container-zone pallets", f"2 → {Q['ere']}",
     f"{fleet['ERE 225']['Utilisation avg %']:.0f}%", "Yes: 2.5 t, carries the few heavy loads", "Keep 1 per dock side: docks are 96 m apart and both are busy 10:30–14:00. Low use — could drop to 1 if DHL accepts the walk."],
    ["Pick trolley + totes", "Small orders, batch picking", f"{Q['trolleys']}", "—", "Yes: 250 kg, 6 totes", "Keep (cheap, flexible)."],
    ["Put-to-light wall", "Sort batch picks into orders", f"{Q['ptl_slots']} slots", "—", f"Peak wave ~{SORT['small_orders_wave_peak']:.0f} small orders + 20%", "Keep."],
    ["Roller conveyor + 2 stretch wrappers", "Unpack containers; wrap new and outgoing pallets", "new", "—",
     "Yes: no heavy carrying out of the container", "Add (D3)."],
    ["RF terminals", "Scan every move", f"{Q['rf_units']}", "—", "One per person at the peak + 20%", "Keep."],
    ["Telescopic forks", "(double-deep)", "dropped", "—", "Not needed with single-deep racks", "Removed."],
    ["ECE 225 order picker", "(2-pallet picking)", "rejected (D2)", "—", "Too long for 3.0 m aisles; orders too small", "Rejected."],
    ["EZS 130 tugger train", "(trolley transport)", "not planned (D2)", "—", f"Driver would be ~{PK['tugger']['driver_utilisation_pct']:.0f}% busy",
     "Option if small orders triple."],
]
table(["Machine", "Job", "Units", "Use (avg day)", "Fits?", "Verdict"], mach, widths=[2.8, 2.8, 1.6, 1.4, 3.6, 3.8], arr=9)
para("Do the loads fit the racks and the trucks? Checked on all 11,015 loads in stock (01-06-2025):", sa=4).paragraph_format.keep_with_next = True
table(["Check", "Data", "Result"], [
    ["Weight", f"{LC['weight']['over_1000']} loads > 1 t, {LC['weight']['over_1600']} > 1.6 t (actual qty × unit weight)",
     "ETV 216i lifts 1.6 t → the few heavier loads go to floor positions, moved with the ERE 225 (2.5 t)"],
    ["Length", f"{LC['long']['loads_over_1_9m']} loads 1.9–2.4 m (XLONG / CONS), {LC['long']['loads_over_2_4m']} longer than 2.4 m",
     "1.9–2.4 m pallets lie crosswise in the odd/long modules (1 per bay, forks under the long side); > 2.4 m on cantilever"],
    ["Height", f"{LC['tall']['loads_1_16_to_1_68']} loads 1.16–1.68 m tall, {LC['tall']['loads_over_1_68']} taller; "
               f"{LC['tall']['height_missing']} have no height in the WMS",
     f"tall loads use the top level ({LC['tall']['top_level_positions']:,} positions with ~1.7 m free); the tallest stand on the floor"],
    ["Aisles", "3.0 m storage aisles, 3.2 m cross-aisles", "ETV needs 2.63–2.79 m, EJE 1.79–1.94 m → OK"],
], widths=[2.0, 6.2, 7.8], arr=9)

# ================================================================ 5 COSTS
doc.add_heading("5. Costs — CAPEX and OPEX", level=1)
para("The capacity plan (D2 §6) is turned into money in three steps: (1) count what the design needs (positions, bays, "
     "trucks, people), (2) multiply by a price from a public source or a labelled assumption (Section 7), (3) add it up per "
     "year. Trucks are leased with full service (repairs included), so they are OPEX, not CAPEX. The building, dock "
     "levellers, sprinklers and the hazmat compartment are outside the project scope and not included.", sa=6)
doc.add_heading("5.1 One-off investment (CAPEX)", level=2)
figure("d3_capex.png", f"Fig 6. CAPEX by group — total {eur(PC['capex_total'], True)}.", 13.5)
rows = [[r["Item"], f"{r['Qty']:,.0f} {r['Unit']}", eur(r["Unit price EUR"]) if r["Unit price EUR"] >= 10 else f"€{r['Unit price EUR']:.2f}",
         eur(r["Total EUR"]), r["Source"]] for r in PC["capex_table"]]
rows.append(["Total CAPEX", "", "", eur(PC["capex_total"]), ""])
table(["Item", "Quantity", "Unit price", "Total", "Source"], rows, widths=[6.0, 2.8, 2.0, 2.4, 2.8], arr=2, bold_last=True)
bullets([
    f"**Racking is {PC['capex_by_group']['Storage'] / PC['capex_total']:.0%} of the investment.** If the racking already standing in "
    f"Bemmel can be taken down and rebuilt in the new layout (about €25 per position), the investment drops to "
    f"{eur(PC['capex_reuse_racking'], True)}. DHL must confirm the type and condition of today's racks.",
    f"**Depreciation:** {eur(PC['depreciation_year'])} a year (racking 15 years, equipment 7, IT 5).",
])
doc.add_heading("5.2 Running cost (OPEX)", level=2)
figure("d3_opex.png", f"Fig 7. OPEX by group — total {eur(PC['opex_total'], True)} per year.", 13.5)
rows = [[r["Item"], f"{r['Qty / yr']:,.0f} {r['Unit']}", f"€{r['Unit cost EUR']:,.2f}" if r["Unit cost EUR"] < 10 else eur(r["Unit cost EUR"]),
         eur(r["Total EUR/yr"]), r["Source"]] for r in PC["opex_table"]]
rows.append(["Total OPEX per year", "", "", eur(PC["opex_total"]), ""])
rows.append(["+ depreciation of CAPEX", "", "", eur(PC["depreciation_year"]), "A041"])
rows.append(["Total yearly cost", "", "", eur(PC["annual_cost"]), ""])
table(["Item", "Quantity / year", "Unit cost", "Per year", "Source"], rows, widths=[6.0, 2.8, 2.0, 2.4, 2.8], arr=2, bold_last=True)
para(f"Labour hours come from the capacity plan: {STO['fte_avg']:.1f} FTE on an average day × 8 paid hours × "
     f"{PC['cost_register']['days_year']['value']} working days. Peak days are covered by flexible staff at the same hourly cost.",
     size=9.5, color=GREY)
doc.add_heading("5.3 Cost per unit", level=2)
uc = PC["unit_cost"]; vy = PC["volumes_year"]
table(["Per …", "Volume per year", "Cost"], [
    ["Order line", f"{vy['lines']:,.0f}", f"€{uc['per_order_line']:.2f}"],
    ["Order", f"{vy['orders']:,.0f}", f"€{uc['per_order']:.2f}"],
    ["Inbound pallet", f"{vy['inbound_pallets']:,.0f}", f"€{uc['per_inbound_pallet']:.2f}"],
    ["Pallet position per month", f"{LAY['positions_total']:,}", f"€{uc['per_position_month']:.2f}"],
], widths=[5.0, 4.0, 3.0])
para("These are full costs (OPEX + depreciation) split over the volume — useful for DHL to compare with the price "
     "agreed with Assa Abloy.", size=9.5, color=GREY)
doc.add_heading("5.4 Today vs future — saving and payback", level=2)
table(["", "All-new equipment", "Re-use today's racking"], [
    ["One-off investment", eur(PC["capex_total"]), eur(PC["capex_reuse_racking"])],
    ["Labour saved per year (Section 2.2)", eur(PC["saving_year"]), eur(PC["saving_year"])],
    ["Simple payback", f"{PC['payback_years']:.1f} years", f"{PC['payback_reuse_years']:.1f} years"],
], widths=[6.0, 4.5, 4.5])
bullets([
    "**Only labour savings are counted.** Shorter lead times, fewer parked trailers, fewer picking errors and a safer "
    "layout have value too, but no reliable price.",
    "**The saving is the part DHL can prove fastest:** wave release and batching need almost no investment (WMS set-up, "
    "trolleys, the put-to-light wall). They can start before the racks are rebuilt.",
])
doc.add_heading("5.5 What if our cost assumptions are wrong?", level=2)
figure("d3_tornado.png", "Fig 8. Yearly cost (OPEX + depreciation) when each assumption moves to the low or high end of its range.", 15)
bullets([
    "**Labour rate and productivity matter most** — labour is about two thirds of the yearly cost. DHL's real hourly cost "
    "and time studies (A006, A025) are the most valuable inputs to get.",
    "**Racking price is the biggest one-off uncertainty**, but spread over 15 years its effect on the yearly cost is smaller.",
    "**The truck lease price hardly matters**: only 7 trucks are leased.",
    f"**Loose containers:** a DHL crew costs ~€{PC['loose_cost_per_container']:,.0f} per container "
    f"({Q['containers_year']:.0f} containers a year). If a contractor quotes less, use the contractor in the same zone.",
])

# ================================================================ 6 SUPPORTING DOCUMENTS
doc.add_heading("6. Supporting documents", level=1)
table(["Document", "What it contains"], [
    ["Deliverable 1 — Analysis (updated)", "Data analysis, concept choice and decision matrix; now single-deep racks and per-order lead time"],
    ["Deliverable 2 — Future state (v3)", "Processes, flowcharts, layout and 3D, docks, picking, machinery and capacity plan; now with the loose-container zone and the reviewed fleet"],
    ["Deliverable_3_Calculations.xlsx", "Every price, quantity and formula of this report; change an input and all totals update"],
    ["data/assumptions.json", "All assumptions A001–A041, each with reason, source and impact"],
    ["documentation/sources.md", "All sources S001–S025 with links and what they support"],
    ["analysis/*.py", "Scripts that turn the raw data into every table and figure (run order in README.md)"],
], widths=[5.4, 10.6], arr=9)

# ================================================================ 7 ASSUMPTIONS
doc.add_heading("7. Cost assumptions and open points", level=1)
para("New assumptions for Deliverable 3 (full register in data/assumptions.json):", sa=4)
rows = [[a["id"], a["assumption"], a["value"], a["source"]] for a in ASSUM["assumptions"] if a["id"] >= "A030"]
table(["ID", "Assumption", "Value", "Source"], rows, widths=[1.2, 3.6, 7.4, 3.8], arr=9)
para("Sources for prices and benchmarks:", sa=4)
src = {
    "S018": "CBS — labour cost per worked hour 2024 (transport & storage)",
    "S019": "Cao Beroepsgoederenvervoer — wage scales 2025",
    "S020": "IndexBox / T-Racking — pallet racking price per position",
    "S021": "Dutch reach-truck lease and rental offers (Liftlease, Beekmans, Itolang, Solid Lift)",
    "S022": "Eurostat nrg_pc_205 — NL non-household electricity price H1 2025",
    "S023": "WERC DC Measures 2024/2025 — pick accuracy and dock-to-stock benchmarks",
    "S024": "Prestatie — loose-load container unloading (2–4 h, fixed price per container)",
    "S025": "Public equipment listings (trolley, tote, wrapper, conveyor, carton flow, put-to-light, RF terminal)",
}
table(["ID", "Source"], [[k, v] for k, v in src.items()], widths=[1.4, 14.6], arr=9)
bullets([
    "**To get from DHL:** real hourly labour cost and pick/pack times (A006, A025, A030); type and condition of today's racking "
    "(re-use); container numbers per week (A019).",
    "**To get from suppliers:** Jungheinrich lease quote for 2 ETV 216i, 3 EJE 120i, 2 ERE 225 (A038); racking quote for "
    f"{LAY['positions_total']:,} single-deep positions (A033); contractor price per loose container (A026).",
    "**To get from Assa Abloy:** the hazard class of the 138 flagged SKUs — it decides the hazmat section, which is not in this budget (A028).",
])

footer()
DELIV = os.path.join(BASE, "deliverables"); os.makedirs(DELIV, exist_ok=True)
out = os.path.join(DELIV, "Deliverable_3_Performance_Overview.docx")
doc.save(out)
print("Saved:", out)
