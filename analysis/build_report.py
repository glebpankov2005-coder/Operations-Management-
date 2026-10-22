"""
Build the Word deliverable from analysis outputs.
Deliverable 1 (Analysis) - DRAFT. Reads outputs/reports/phase1_metrics.json,
data/assumptions.json and outputs/figures/*.png; writes a formatted .docx.

Regenerate any time the analysis changes:
    python analysis/build_report.py
"""
import os
import json
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
M2 = M  # capacity + decision sections are written into the same metrics file by _util
ASSUM = json.load(open(os.path.join(DATA, "assumptions.json"), encoding="utf-8"))

RED = RGBColor(0xD4, 0x00, 0x11)      # DHL red accent
DARK = RGBColor(0x22, 0x22, 0x22)
GREY = RGBColor(0x66, 0x66, 0x66)

doc = Document()
from references import cite_text, add_reference_list
from team import TEAM, team_line, tag_headings, update_fields_on_open, responsibility_box as _rbox
responsibility_box = lambda which: _rbox(doc, which)
USED = set()                                   # APA: works cited in this document

# ---- base style ----
normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(10.5)
normal.font.color.rgb = DARK

for lvl, sz in [("Heading 1", 15), ("Heading 2", 12.5), ("Heading 3", 11)]:
    st = doc.styles[lvl]
    st.font.name = "Calibri"
    st.font.size = Pt(sz)
    st.font.color.rgb = RED if lvl == "Heading 1" else DARK
    st.font.bold = True


def para(text, size=10.5, color=DARK, bold=False, italic=False, align=None, space_after=6):
    """Paragraph; '**text**' segments are bold (markers are not printed). Source IDs become APA citations."""
    text = cite_text(text, USED)
    p = doc.add_paragraph()
    for i, seg in enumerate(text.split("**")):
        if not seg:
            continue
        r = p.add_run(seg)
        r.font.size = Pt(size); r.font.color.rgb = color; r.bold = bold or (i % 2 == 1); r.italic = italic
    if align:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p


def bullets(items):
    for it in items:
        it = cite_text(it, USED)
        p = doc.add_paragraph(style="List Bullet")
        # allow simple **bold:** prefix
        if "**" in it:
            parts = it.split("**")
            for i, seg in enumerate(parts):
                r = p.add_run(seg); r.bold = (i % 2 == 1); r.font.size = Pt(10.5)
        else:
            r = p.add_run(it); r.font.size = Pt(10.5)


def table(headers, rows, widths=None, align_right_from=1):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        r = hdr[i].paragraphs[0].add_run(str(h)); r.bold = True; r.font.size = Pt(9.5)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            r = p.add_run(cite_text(str(v), USED)); r.font.size = Pt(9.5)
            if i >= align_right_from:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if widths:
        t.autofit = False
        grid = t._tbl.tblGrid
        for i, w in enumerate(widths):
            grid.gridCol_lst[i].w = Cm(w)                          # grid widths: honoured by Word and LibreOffice
            for row in t.rows:
                row.cells[i].width = Cm(w)
    for ri, row in enumerate(t.rows):                              # rows never split; the table stays together
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        if ri < len(t.rows) - 1:
            for c in row.cells:
                for q in c.paragraphs:
                    q.paragraph_format.keep_with_next = True
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def figure(name, caption, width_cm=15.5):
    path = os.path.join(FIGS, name)
    if os.path.exists(path):
        doc.add_picture(path, width=Cm(width_cm))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = para(caption, size=8.5, color=GREY, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)


def page_number_footer():
    footer = doc.sections[0].footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Project OTM — Assa Abloy @ DHL Bemmel  ·  Deliverable 1 (Analysis)  ·  Page ")
    run.font.size = Pt(8); run.font.color.rgb = GREY
    fld1 = OxmlElement("w:fldSimple"); fld1.set(qn("w:instr"), "PAGE")
    run._r.addnext(fld1)


# ============================ COVER ============================
sp = doc.add_paragraph(); sp.paragraph_format.space_before = Pt(60)
para("PROJECT OTM", size=13, color=RED, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
para("Warehouse Design — Analysis & Policy Pre-selection", size=22, color=DARK, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
para("Assa Abloy operation · DHL Supply Chain, Bemmel (NL_0032)", size=12, color=GREY,
     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=30)

table(["Field", "Detail"], [
    ["Deliverable", "1 — Analysis of data, pre-selection & justification of policies"],
    ["Due date", "16-09-2026"],
    ["Data period analysed", "Q2 2025 (01 Apr – 30 Jun)"],
    ["Site constraints", "≤ 7,000 m² footprint · ≤ 12.2 m height"],
    ["Scope", "Receiving · Storage · Picking · Shipping (end-to-end)"],
    ["Team", team_line()],
    ["Version", "Final portfolio version — analysis, operations strategy, design options, policies & recommendation"],
], widths=[4.5, 11])

para("This draft covers Deliverable 1 end-to-end: data analysis, storage-capacity feasibility, three "
     "design options, policy pre-selection, equipment, and a recommended concept with a decision matrix. "
     "All figures are measured from the provided Assa Abloy data or computed by the analysis scripts; "
     "nothing is fabricated, and open assumptions are listed in Section 16. Sources are cited in APA 7 (reference list at the end).",
     size=9, color=GREY, italic=True, space_after=6)
responsibility_box("D1")
doc.add_page_break()

# ============================ CONTENTS ============================
doc.add_heading("Contents", level=1)
_p = doc.add_paragraph()
_fld = OxmlElement("w:fldSimple"); _fld.set(qn("w:instr"), 'TOC \\o "1-2" \\h \\z \\u')
_r = OxmlElement("w:r"); _t = OxmlElement("w:t")
_t.text = "(In Word: right-click → Update Field to build the table of contents.)"
_r.append(_t); _fld.append(_r); _p._p.append(_fld)
doc.add_page_break()

# ============================ 1. INTRODUCTION ============================
doc.add_heading("1. Introduction & scope", level=1)
para("DHL Supply Chain previously ran warehouse operations for four clients in Tiel and recently "
     "relocated to a new site in Bemmel under significant time pressure. The Operations Manager "
     "considers the current (post-move) design sub-optimal. The objective of this project is to "
     "develop an alternative, more efficient and effective warehouse design for the Assa Abloy "
     "operation, based on a thorough analysis of the operational data (S001).")
para("The design covers four processes end-to-end — receiving, storage, picking and shipping — "
     "with all choices aligned across them. Facility architecture is out of scope; legal aspects "
     "(fire safety, compliance) are considered. The site envelope is a maximum footprint of "
     "7,000 m² and a maximum height of 12.2 m (S001). Each process has one owner in the team (table on the cover page); "
     "the choices across the four processes were made together.")

# ============================ 2. DATA & METHOD ============================
doc.add_heading("2. Data sources & method", level=1)
inv = M["inventory"]["snapshots"]
o = M["orders"]
para("Two datasets from the Assa Abloy operation (warehouse NL_0032) form the primary source of truth (S002):")
table(["Dataset", "Files", "Grain", "Volume"], [
    ["Storage / inventory", "3 snapshots (01-04/05/06-2025)", "Inventory detail (DTLNUM)",
     f"{inv[0]['detail_records']:,}–{inv[-1]['detail_records']:,} records"],
    ["Outbound shipping & picking", "3 months (Apr–Jun 2025)", "Order line",
     f"{o['n_order_lines']:,} lines · {o['n_orders']:,} orders"],
], widths=[3.8, 4.6, 3.6, 3.5])
para("Analysis is performed in Python (pandas). Every headline number is reproducible from the "
     "scripts in /analysis and cached in outputs/reports/phase1_metrics.json. Data-quality issues "
     "are flagged (Section 10), not silently corrected. The design approach follows the structured warehouse-design steps "
     "of the Week 3 lecture (S017, S032).", size=9.5, color=GREY, italic=True)

# ============================ 3. SKU PROFILE ============================
doc.add_heading("3. SKU profile", level=1)
s = M["sku"]
bullets([
    f"**{s['n_skus']:,} SKUs** in stock across **{s['n_families']} product families**.",
    f"**{s['skus_with_case_pack']:,} SKUs have a case pack; {s['skus_each_only']:,} are each-only** "
    f"(≈{round(s['skus_each_only']/s['n_skus']*100)}%) — confirming real each-pick demand.",
    f"Each size is small: median cube {s['ea_cube_m3']['median']} m³ (~500 cm³) — typical for locks, "
    f"cylinders and fittings.",
    f"Units per pallet: median **{s['units_per_pallet']['median']:.0f}** (mean skewed by high-count small parts).",
    f"Pallet weight: median **{s['pallet_weight_kg']['median']:.0f} kg** — realistic for a EURO pallet "
    f"(see data-quality flag on sentinel maxima).",
    f"Pallet-type mix (SKU level): EURO {s['asset_type_counts'].get('EURO',0):,}, "
    f"K3 {s['asset_type_counts'].get('K3',0):,}, XLONGPALLET {s['asset_type_counts'].get('XLONGPALLET',0):,} "
    f"(long goods), plus K1/K2/K5/CONS.",
    f"Hazardous SKUs: {s['hazmat_skus']} — require segregation/compliance consideration.",
])
figure("sku_pallet_weight_hist.png", "Fig 1. Pallet-weight distribution at SKU level (<p99).", 12)

# ============================ 4. INVENTORY ============================
doc.add_heading("4. Inventory & storage-position requirement", level=1)
table(["Snapshot", "Detail recs", "Loads", "Occupied locations", "Active SKUs", "Cube (m³)"],
      [[r["snapshot"], f"{r['detail_records']:,}", f"{r['loads_LODNUM']:,}",
        f"{r['occupied_locations']:,}", f"{r['active_skus']:,}", f"{r['total_cube_m3']:,.0f}"]
       for r in inv], widths=[2.7, 2.4, 3.0, 3.2, 2.2, 2.0])
ii = M["inventory"]
sb = M["capacity_plan"]["storage_basis"]
bullets([
    f"Occupied locations (pallet positions) grew **{inv[0]['occupied_locations']:,} → "
    f"{inv[-1]['occupied_locations']:,}** over the quarter; loads grew +{ii['loads_growth_pct_q2']}% "
    f"({inv[0]['loads_LODNUM']:,} → {inv[-1]['loads_LODNUM']:,}); cube +15%.",
    f"**Peak pallet positions ≈ {sb['peak_occupied_locations']:,} occupied locations** → the storage baseline. "
    f"The {sb['peak_loads']:,} loads sit in those locations (some locations hold more than one load), so loads "
    f"overstate the positions needed (A004).",
    f"Loads per SKU: mean {ii['loads_per_sku']['mean']}, median {ii['loads_per_sku']['median']:.0f}, "
    f"max {ii['loads_per_sku']['max']:.0f}; **{ii['single_load_skus_pct']}% of SKUs occupy a single load** "
    f"— a long slow-moving tail one pallet deep.",
    "Eaches held roughly flat (~2.9M) while loads rose → stock is fragmenting into more, less-full "
    "locations: a current-design inefficiency to target.",
])
figure("inventory_trend.png", "Fig 2. Inventory footprint trend, Q2 2025 (loads and occupied locations).", 13)
figure("report_stock_ageing.png", "Fig 2b. Stock ageing — 21% of loads have been in stock >1 year (dead-stock signal).", 13)

# ============================ 5. INBOUND PROFILE (RECEIVING) ============================
doc.add_heading("5. Inbound profile (receiving)", level=1)
CPM = M["capacity_plan"]["measured"]; LZ = M["dock_mhe"]["loose_zone"]; LCK = M["dock_mhe"]["load_checks"]
para("No receiving file was provided, so receipts are measured from the storage snapshots: loads with an ADD DATE in the "
     "14 days before each snapshot (A007). Loads that already left before the snapshot are not visible, so these are lower bounds.",
     space_after=4)
table(["Snapshot", "Receiving days", "Loads booked in", "Loads / day", "Busiest day", "From Asia"],
      [[w["snapshot"], w["receiving_days"], f"{w['loads']:,}", f"{w['loads_per_day']:.0f}", w["max_day"], f"{w['asia_origin_pct']:.0f}%"]
       for w in M["capacity_plan"]["inbound_windows"]], widths=[2.8, 2.6, 2.8, 2.4, 2.4, 2.4])
bullets([
    f"**~{CPM['inbound_loads_day']:.0f} loads are received per working day; the busiest day reached {CPM['inbound_max_day']:.0f} "
    f"(×{CPM['inbound_peak_factor']:.2f}).** Two shipments a day come straight from Assa Abloy factories (S004).",
    f"**~{CPM['inbound_asia_origin_pct']:.0f}% of loads come from Asia and arrive loose in sea containers** — cartons stacked on "
    f"the container floor. A container brings a median of {LZ['loads_per_container_median']:.0f} pallets of "
    f"{LZ['skus_per_container_median']:.0f} SKUs (p75: {LZ['loads_per_container_p75']:.0f} pallets, {LZ['skus_per_container_p75']:.0f} SKUs) "
    f"that must be unpacked, sorted per SKU and palletised.",
    f"**Pallet mix:** EURO, K3 and XLONG pallets; {LCK['long']['loads_long_capped']} loads are 1.3–2.05 m long, "
    f"{LCK['weight']['over_1000']} loads weigh over 1 t and {LCK['tall']['loads_over_1_68']} are taller than 1.68 m.",
    f"**Hazardous goods:** {M['design_evaluation']['hazmat']['loads']:,} loads carry the hazmat flag — they must be identified "
    "at receiving and stored by the rules (Section 10, D2 §5.3).",
    "**Requirement for receiving:** two trailer doors plus one container door; a separate zone to unpack containers; a check "
    "bench and pallet labels; capacity for a 1.7× busy day.",
])

# ============================ 6. ORDER PROFILE ============================
doc.add_heading("6. Order & picking profile and lead time", level=1)
lpo, upl = o["lines_per_order"], o["units_per_line"]
ptl = M["capacity_plan"]["pick_type_order_derived"]["share_lines_pct"]
ptu = M["capacity_plan"]["pick_type_order_derived"]["share_units_pct"]
table(["Metric", "Mean", "Median", "p95", "Max"], [
    ["Lines per order", lpo["mean"], f"{lpo['median']:.0f}", f"{lpo['p95']:.0f}", lpo["max"]],
    ["Units per line", upl["mean"], f"{upl['median']:.0f}", f"{upl['p95']:.0f}", upl["max"]],
    ["Units per order", o["units_per_order"]["mean"], f"{o['units_per_order']['median']:.0f}",
     f"{o['units_per_order']['p95']:.0f}", o["units_per_order"]["max"]],
], widths=[4.5, 2.5, 2.5, 2.5, 3.0])
lt = o["delivery_leadtime_h_arrive_to_dispatch"]
LTO = M["performance_cost"]["leadtime"]                                   # per-order lead time (performance_cost.py)
bullets([
    f"**{o['n_orders']:,} orders / {o['n_order_lines']:,} lines**; **{lpo['single_line_pct']}% single-line** "
    f"orders and **{upl['single_unit_pct']}% single-unit** lines — a small-order-heavy profile.",
    f"**Pick type is derived from what the client ordered** (A022) — each line's quantity is compared with the "
    f"SKU's case and pallet quantity: **{ptl.get('each', 0):.0f}% each-pick lines, {ptl.get('case', 0):.0f}% case "
    f"lines, {ptl.get('full pallet', 0):.0f}% full-pallet lines** (by units: {ptu.get('case', 0):.0f}% case, "
    f"{ptu.get('each', 0):.0f}% each, {ptu.get('full pallet', 0):.0f}% pallet).",
    f"**Picking is each-dominant by line count** (the labour driver) and case-dominant by volume. DHL's "
    f"historical pick flags (case/list {o['pick_class_pct']['case_or_list']}%, each {o['pick_class_pct']['each']}%, "
    f"{o['pick_class_pct']['other']}% unflagged) reflect past practice and are not used for design.",
    f"Delivery lead time (order received → trailer leaves), **per order: median {LTO['today_median_h']:.0f} h, "
    f"average {LTO['today_mean_h']:.0f} h, p90 {LTO['today_p90_h']:.0f} h**; {LTO['today_same_day_pct']:.0f}% of orders leave the same day. "
    f"Counted per order line instead the median is {lt['median']:.0f} h, because big multi-line orders wait longest. "
    "Measured as last TRAILER DISPATCED DATE − ORDER ARRIVE DATE of each order.",
    f"Channel mix (order type): " + ", ".join(f"{k} {v:,}" for k, v in list(o['order_type_mix'].items())[:5]) + ".",
    f"Geography: " + ", ".join(f"{k} {v:,}" for k, v in list(o['country_mix'].items())[:5]) +
    " — an NL hub serving Western Europe.",
])
figure("order_pick_type_derived.png", "Fig 3. Pick type derived from the orders (line quantity vs case / pallet quantity).", 13)
DE = M["design_evaluation"]
para("Delivery lead time per region (order received → trailer dispatched), countries with ≥ 20 orders:", space_after=4)
table(["Country", "Orders", "Median h", "Mean h", "p90 h", "≤ 48 h"],
      [[r["SHIP TO COUNTRY"], f"{int(r['orders']):,}", f"{r['median_h']:.0f}", f"{r['mean_h']:.0f}", f"{r['p90_h']:.0f}",
        f"{r['within_48h']:.0f}%"] for r in DE["leadtime_by_region"]], widths=[2.6, 2.4, 2.4, 2.4, 2.4, 2.4])
bullets(["**NL, BE, DE, LU and FR ship in about a day** (median 8–25 h); **Switzerland (~140 h) and Poland (~120 h) take 5–6 "
         "days**, pointing at customs or weekly consolidation for export — a service question to raise with DHL."])

# ============================ 7. OUTBOUND PROFILE (SHIPPING) ============================
doc.add_heading("7. Outbound profile (shipping)", level=1)
OD = M["dock_mhe"]["outbound_doors"]
para("Measured from the 912 outbound trailers in Q2 2025 (trailer number and dispatch time per order line, S002):", space_after=4)
table(["Measure", "Value"], [
    ["Trailers per day (mean / p90 / max)", f"{OD['trailers_per_day_mean']:.0f} / {OD['trailers_per_day_p90']:.0f} / {OD['trailers_per_day_max']}"],
    ["Load per trailer (mean)", f"{OD['pallets_per_trailer_mean']} pallets + {OD['cartons_per_trailer_mean']:.0f} cartons"],
    ["Trailers without any pallet (parcel only)", f"{OD['share_trailers_zero_pallets_pct']:.0f}%"],
    ["Dock time per trailer (mean / p90)", f"{OD['dock_min_mean']:.0f} / {OD['dock_min_p90']:.0f} min"],
    ["Trailers in the busiest hour (p90 / max)", f"{OD['busiest_hour_trailers_p90']:.0f} / {OD['busiest_hour_trailers_max']}"],
    ["Trailers parked at the doors at the same time today (median / p90)",
     f"{OD['current_drop_trailer_concurrent_median']:.0f} / {OD['current_drop_trailer_concurrent_p90']:.0f}"],
], widths=[10.0, 5.0])
bullets([
    "**Shipping is parcel-heavy:** most trailers carry a few cartons for a parcel network (DHL Parcel, DSV, DHL4YOU …) and "
    "only about one pallet — so packing and sorting cartons per carrier matter more than pallet loading.",
    f"**Today trailers wait at the doors all day** (p90 {OD['current_drop_trailer_concurrent_p90']:.0f} at once): goods are loaded "
    "whenever they are ready, so doors are blocked and the departure time is not planned.",
    "**Requirement for shipping:** a fixed departure plan per carrier, staging lanes so goods wait on the floor and not in "
    "trailers, enough doors for the busiest hour, and carton sorting per carrier.",
])

# ============================ 8. ABC ============================
doc.add_heading("8. Demand-based ABC classification", level=1)
a = M["abc"]
para("ABC is recomputed from actual outbound demand (picked quantity), not assumed. The distribution "
     "is steeper than the classic 80/20 rule:")
table(["Top X% of SKUs", "% of picked volume"],
      [[k.replace('top_', '').replace('pct_skus_do_qty_pct', '% of SKUs'), f"{v}%"]
       for k, v in a["pareto_actual"].items()], widths=[6, 6], align_right_from=1)
para("A/B/C by demand volume (A ≤ 80% cumulative, B ≤ 95%, C remainder):", space_after=4)
table(["Class", "SKUs", "% SKUs", "% volume", "% pick-lines"],
      [[c["ABC_vol"], f"{c['skus']:,}", f"{c['sku_pct']}%", f"{c['qty_pct']}%", f"{c['line_pct']}%"]
       for c in a["class_summary_volume"]], widths=[2.5, 2.5, 3, 3, 3.5])
bullets([
    "**~13% of SKUs drive 80% of volume**, yet C-class is 67% of SKUs and still 28% of picks → "
    "forward-pick / fast-lane slotting is high-value.",
    f"**Demand-ABC agrees with the WMS classification on only {a['agreement_with_wms_pct']}% of SKUs** "
    "→ strong evidence the current slotting is misaligned with real demand (re-slot).",
    f"{a['n_skus_shipped']:,} SKUs shipped in Q2; {a['skus_shipped_not_in_stock']:,} shipped were not in "
    "the latest stock snapshot (transient/cross-dock — to confirm).",
])
figure("abc_pareto.png", "Fig 4. Demand Pareto — cumulative picked quantity vs ranked SKUs.", 13)
figure("report_top20_products.png", "Fig 4b. Top-20 SKUs by demand — note several high-demand items still WMS-classed C.", 15)

# ============================ 7. PEAK ============================
doc.add_heading("9. Peak activity analysis", level=1)
p = M["peak"]
rl = M["dock_mhe"]["order_release"]
table(["Metric", "Average / day", "PEAK / day", "Peak ÷ Avg", "Peak date"], [
    ["Order lines", f"{p['lines']['mean']:.0f}", f"{p['lines']['peak']:.0f}", f"{p['lines']['peak_over_avg']}×", p['lines']['peak_date']],
    ["Units", f"{p['units']['mean']:.0f}", f"{p['units']['peak']:.0f}", f"{p['units']['peak_over_avg']}×", p['units']['peak_date']],
    ["Orders", f"{p['orders']['mean']:.0f}", f"{p['orders']['peak']:.0f}", f"{p['orders']['peak_over_avg']}×", p['orders']['peak_date']],
    ["Shipments", f"{p['shipments']['mean']:.0f}", f"{p['shipments']['peak']:.0f}", f"{p['shipments']['peak_over_avg']}×", p['shipments']['peak_date']],
], widths=[3.2, 3.2, 3.0, 2.6, 3.0])
bullets([
    "**Design to peak, not average.** Units peak (2.85×) is far spikier than lines (1.83×), so sizing "
    "on lines alone understates pick/pack surges.",
    f"Weekly peak {p['weekly_lines']['peak']:.0f} lines (week of {p['weekly_lines']['peak_week']}) vs "
    f"~{p['weekly_lines']['mean']:.0f} average.",
    f"**The {p['peak_hour']:02d}:00 intraday peak is caused by the order-release routine, not by customers** "
    f"(A023): {rl['orders_arrive_15_17_pct']:.0f}% of orders arrive 15:00–17:00, are released 16:00–18:00 and are "
    f"picked the next morning, so the backlog hits the floor at shift start ({rl['pick_peak_over_mean_active_hour']}× "
    "the average hour). Monday–Friday only, weekdays fairly even.",
])
figure("throughput_daily.png", "Fig 5. Daily shipped order-lines with average and peak.", 15)
figure("order_release_profile.png", "Fig 6. Order arrival vs release vs picking by hour — the 08:00 peak is the "
       "release backlog.", 15)

# ============================ 8. DATA QUALITY ============================
doc.add_heading("10. Data-quality flags", level=1)
para("Raised, not silently corrected:")
bullets([
    f"**PA WGT sentinel/impossible values** — median {s['pallet_weight_kg']['median']:.0f} kg is fine, "
    f"but p95 = {s['pallet_weight_kg']['p95']:.0f} kg and max = {s['pallet_weight_kg']['max']:.0f} kg are "
    "impossible for one pallet (9,999 looks like a placeholder). To be cleaned before rack load-rating.",
    f"**units_per_pallet extreme mean** ({s['units_per_pallet']['mean']:.0f} vs median "
    f"{s['units_per_pallet']['median']:.0f}) — use robust statistics.",
    f"**\"Other\" pick class = {o['pick_class_pct']['other']}% of lines** — no PALL/LIST/TROLLEY flag set. "
    "Resolved for the design: the pick type is derived from order quantities instead of these flags (A022).",
    f"**Stock vs demand mismatch** — {a['skus_shipped_not_in_stock']:,} shipped-not-stocked; a further set "
    "of stocked-not-shipped SKUs are dead-stock candidates. To confirm handling (cross-dock vs obsolete).",
])
para("Data checks requested in class (Week 3):", space_after=4)
table(["Question", "Answer", "Note"], [[c["Question (W3)"], c["Answer"], c["Note"]] for c in M["design_evaluation"]["w3_checks"]],
      widths=[4.2, 5.4, 6.4], align_right_from=9)

# ============================ 11. OPERATIONS STRATEGY ============================
PCo = M["performance_cost"]; LTO = PCo["leadtime"]; STO = PCo["storage"]; OD = M["dock_mhe"]["outbound_doors"]
RLS = M["dock_mhe"]["order_release"]; n_days = round(o["n_order_lines"] / p["lines"]["mean"])
web = sum(v for k, v in o["order_type_mix"].items() if k.startswith("WEB")) / o["n_order_lines"] * 100
doc.add_heading("11. Operations strategy — process types, performance objectives and current alignment", level=1)
para("Before choosing a design, this section asks what the operation is, what it must be good at for its customer, and whether "
     "it is good at that today. It uses the operations-strategy concepts of Slack et al.: the four V's, process types, the five "
     "performance objectives and order winners versus qualifiers (S031).")
doc.add_heading("11.1 The four processes and their type", level=2)
para("The warehouse transforms inputs (pallets and containers from the factories, orders from customers) into outputs "
     "(complete orders on the right trailer). It is a chain of four processes, each with an owner:", space_after=4)
table(["Process (owner)", "Input → output", "Process type", "What drives its performance"], [
    [f"Receiving ({TEAM['Receiving']})", "trailers and containers → checked pallets ready for putaway",
     "batch: work arrives in loads, twice a day", f"~{CPM['inbound_loads_day']:.0f} loads/day, 41% loose in containers"],
    [f"Storage ({TEAM['Storage']})", "pallets → stock in the right place, fast-pick faces filled", "stock (buffer) process",
     f"{STO['occupied_peak']:,} occupied locations at the peak, {a['n_skus_shipped']:,} SKUs shipped"],
    [f"Picking ({TEAM['Picking']})", "orders → picked items", "high-volume repetitive work with very high variety",
     f"~{p['lines']['mean']:.0f} lines/day, {ptl.get('each', 0):.0f}% each-picks"],
    [f"Shipping ({TEAM['Shipping']})", "picked items → packed orders on the booked trailer", "scheduled batch: by trailer departure",
     f"~{OD['trailers_per_day_mean']:.0f} trailers/day, {OD['share_trailers_zero_pallets_pct']:.0f}% parcel-only"],
], widths=[3.4, 4.6, 3.8, 4.2], align_right_from=9)
doc.add_heading("11.2 The four V's of the Assa Abloy operation", level=2)
table(["Dimension", "Measured (Q2 2025)", "Level", "What it means for the design"], [
    ["Volume", f"~{p['lines']['mean']:.0f} order lines and ~{o['n_orders'] / n_days:.0f} orders a day; ~{CPM['inbound_loads_day']:.0f} "
     f"inbound loads; ~{OD['trailers_per_day_mean']:.0f} trailers", "medium", "repeatable tasks → standard methods, scanning and batching pay off"],
    ["Variety", f"{a['n_skus_shipped']:,} SKUs shipped, {s['n_skus']:,} in stock; small parts to 2 m long pallets; each, case and "
     f"pallet picks; pallets and loose containers; {s['hazmat_skus']} hazardous SKUs", "high",
     "several storage types and picking by order size; no single automated system fits all items"],
    ["Variation", f"peak day {p['lines']['peak_over_avg']}× lines and {p['units']['peak_over_avg']}× units; 08:00 peak "
     f"{RLS['pick_peak_over_mean_active_hour']}× the average hour; stock +{STO['growth_per_quarter_pct']:.0f}% per quarter", "high (partly self-made)",
     "level the self-made peak with waves; flexible staff; storage headroom"],
    ["Visibility", f"business customers and web shops ({web:.0f}% of lines are web orders) see only the result: complete, "
     "correct and on time", "low", "efficiency can be designed in the back office, but the dispatch promise must be kept"],
], widths=[2.2, 6.0, 2.2, 5.6], align_right_from=9)
para("**Process type:** high variety with medium volume of small, repetitive tasks puts the operation between a batch and a "
     "mass process on the product–process matrix (S031). That matches a people-based process supported by scanners, carton flow "
     "and a put-to-light wall (Option B), not full automation (Option C), which suits high volume with low variety.")
doc.add_heading("11.3 What the operation must be good at — performance objectives", level=2)
para("For DHL, the Assa Abloy contract is won and kept on its service and its cost. We rank the five performance objectives "
     "(S031) as follows — this ranking is our judgement, based on the data in the table:", space_after=4)
table(["Rank", "Objective", "What it means here", "Order winner or qualifier", "Evidence (data)"], [
    ["1", "Dependability", "every order leaves on the agreed trailer, every day", "order winner",
     f"orders arrive 15:00–17:00 ({RLS['orders_arrive_15_17_pct']:.0f}%) and are expected out the next day"],
    ["2", "Speed", "short time from order to trailer", "order winner",
     f"today only {LTO['today_within_24h_pct']:.0f}% of orders leave within 24 h"],
    ["3", "Quality", "right item, right quantity, safe and legal storage", "qualifier",
     f"benchmark pick accuracy ≥ 99.3% (S023); {M['design_evaluation']['hazmat']['loads']:,} hazardous loads"],
    ["4", "Cost", "low cost per order line for the contract", "order winner at contract renewal",
     "labour is the largest cost; the 08:00 peak forces over-staffing"],
    ["5", "Flexibility", "absorb peaks, growth and new items", "qualifier",
     f"peak day {p['lines']['peak_over_avg']}× lines; stock +{STO['growth_per_quarter_pct']:.0f}% per quarter"],
], widths=[1.1, 2.4, 4.4, 3.0, 5.1], align_right_from=9)
doc.add_heading("11.4 Is the current operation aligned with these objectives?", level=2)
table(["Objective", "Today (measured or modelled)", "Gap", "Design response"], [
    ["Dependability", f"all orders released in the evening → 08:00 peak of {RLS['pick_peak_over_mean_active_hour']}× the average hour; "
     f"trailers parked at the doors (p90 {OD['current_drop_trailer_concurrent_p90']:.0f} at once)", "large",
     "3 waves planned backwards from a fixed trailer departure plan (D2 §4.5)"],
    ["Speed", f"median {LTO['today_median_h']:.0f} h, slowest 10% {LTO['today_p90_h']:.0f} h; {LTO['today_within_24h_pct']:.0f}% within 24 h",
     "large", f"same-day wave for orders before 12:00 → {LTO['future_within_24h_pct']:.0f}% within 24 h (D3)"],
    ["Quality", f"slotting agrees with demand for only {a['agreement_with_wms_pct']}% of SKUs; master-data errors (Section 10)",
     "medium", "slotting by demand, a scan at every move, the put-to-light wall checks every item"],
    ["Cost", f"~{PCo['pick_today_staffed_h']:.0f} picker-hours a day (modelled: one order per tour, peak staffing)", "large",
     f"batch picking from a fast-pick area → ~{PCo['pick_future_h']:.0f} h a day (D3 §2.2)"],
    ["Flexibility", f"21% of loads older than one year; racks would be full in ~{STO['months_headroom']:.0f} months at the "
     "April–June growth", "medium", "dead-stock clean-up, a reserved 12th rack module, flexible staff"],
], widths=[2.4, 6.0, 1.6, 6.0], align_right_from=9)
bullets([
    "**Conclusion:** the current operation is organised around storing (positions filled after a rushed move) instead of "
    "around the flow the customer pays for: dispatch on time, fast, at low cost. The biggest gaps are dependability, speed and "
    "cost — all three are caused by how work is released and picked, not by a lack of space.",
    "**So the design aims first at flow** (waves, fast-pick area, batch picking, departure plan) and then at storage density. "
    "Section 12 turns these objectives into requirements per process; Deliverable 3 measures them with KPIs.",
])

# ============================ 12. DESIGN REQUIREMENTS ============================
doc.add_heading("12. Design requirements per process (input to design options)", level=1)
para("The data (Sections 3–10) and the performance objectives (Section 11) give these requirements. Each process owner "
     "checked that the design meets them:", space_after=4)
table(["Process (owner)", "Requirement", "From"], [
    [f"Receiving ({TEAM['Receiving']})", f"~{CPM['inbound_loads_day']:.0f} loads/day, {CPM['inbound_max_day']:.0f} on the busiest day; "
     "2 trailer doors + 1 container door; a zone to unpack and palletise containers", "Section 5"],
    [f"Storage ({TEAM['Storage']})", f"~{sb['peak_occupied_locations']:,} pallet positions at the peak → target ~{sb['target_positions']:,} "
     f"(÷ 0.90); room for long pallets up to 2.05 m; {ii['single_load_skus_pct']}% single-load SKUs; re-slot to demand "
     f"(only {a['agreement_with_wms_pct']}% agreement today); within 7,000 m² and 12.2 m", "Sections 3, 4, 8"],
    [f"Picking ({TEAM['Picking']})", f"{ptl.get('each', 0):.0f}% each-pick lines and half of the orders single-line → batch picking "
     f"from a fast-pick area; capacity for {p['lines']['peak']:.0f} lines on the peak day; level the 08:00 peak", "Sections 6, 8, 9"],
    [f"Shipping ({TEAM['Shipping']})", f"~{OD['trailers_per_day_mean']:.0f} trailers/day, mostly parcels; a departure plan per carrier; "
     "staging lanes instead of parked trailers; doors for the busiest hour", "Section 7"],
    ["All (group)", "dependability and speed first, then quality and cost (Section 11); choices aligned across the four processes",
     "Section 11"],
], widths=[3.4, 10.2, 2.4], align_right_from=9)

# ============================ 13. CAPACITY FEASIBILITY ============================
doc.add_heading("13. Storage capacity feasibility", level=1)
cap = M2["capacity"]
para(f"Design target: peak **{sb['peak_occupied_locations']:,} occupied locations ÷ 0.90 working utilisation ≈ "
     f"{sb['target_positions']:,} pallet positions** (A010). This replaces the earlier "
     f"{sb['old_target_retired']:,} (loads × 1.15 buffer), which overstated the need by counting loads instead of "
     f"positions. Measured pallet+load height is low (p90 {cap['measured']['pa_hgt_p90_cm']:.0f} cm), giving a "
     f"{cap['level_pitch_m']} m level pitch and up to {cap['base_levels_height_limited']} levels under 12.2 m.")
para("Bottom-up floor area needed to hold that target, by storage concept:")
fc = M["capacity_plan"]["feasibility_corrected"]
table(["Concept", "MHE", "Levels", "Total area m² *", "% of 7,000 m²", "Fits?"],
      [[r["Concept"], r["MHE"], str(r["Levels"]), f"{r['Total area m2']:,}", f"{r['% of 7,000 m2']:.0f}%", r["Fits"]]
       for r in fc], widths=[4.0, 3.3, 1.5, 2.6, 2.4, 1.8])
para("* includes a 35% allowance for receiving, staging, pick, pack, ship, offices and circulation.",
     size=8.5, color=GREY, italic=True)
pct = {r["Concept"]: r["% of 7,000 m2"] for r in fc}
bullets([
    f"**At the corrected target several concepts fit:** double-deep {pct['Double-deep']:.0f}%, narrow-aisle "
    f"selective {pct['Selective - narrow aisle']:.0f}%, VNA {pct['VNA']:.0f}%. Wide-aisle ({pct['Selective - wide aisle']:.0f}%) "
    f"and drive-in ({pct['Drive-in']:.0f}%) are tight.",
    "→ Space alone no longer decides the concept. The choice is driven by travel and labour, slotting "
    "flexibility, growth headroom and cost — compared in the options and decision matrix below.",
])
figure("capacity_feasibility_corrected.png", "Fig 7. Floor area to hold the corrected position target, by concept, "
       "vs the 7,000 m² envelope.", 14)

# ============================ 11. DESIGN OPTIONS ============================
doc.add_heading("14. Design options", level=1)
para("Three end-to-end options (storage × picking × MHE × policies), each aligned across the four processes. Storage "
     "systems and picking methods are taken from the Week 3 lecture and the order-picking literature (S017, S014).")

doc.add_heading("Option A — Conventional+ (improve the current concept)", level=2)
bullets([
    f"**Storage:** selective single-deep, narrow-aisle (reach), 7 levels; two-zone ABC. ≈{pct['Selective - narrow aisle']:.0f}% "
    "of the envelope.",
    "**Picking:** RF-directed discrete + simple batch; case pick from pick-face; pallet from reserve.",
    "**MHE:** reach trucks, low-level order pickers, pallet trucks, RF scanners.",
    "**Verdict:** cheapest and simplest, but the most aisles, travel and labour.",
])
doc.add_heading("Option B — Hybrid density + velocity slotting + zone/batch picking  (recommended)", level=2)
bullets([
    "**Storage:** single-deep pallet racking placed back-to-back (one pallet each side of the rack, every pallet "
    "directly reachable from an aisle), 3.0 m reach-truck aisles, 8 levels; selective racks for irregular SKUs + a "
    f"forward-pick module (carton-flow / shelving) for fast case/each; a long-goods module for XLONG pallets; bin shelving for small slow parts. "
    f"≈{pct['Selective - narrow aisle']:.0f}% of the envelope for storage + working areas.",
    "**Update (Deliverable 3):** first drafted as double-deep; changed to single-deep back-to-back (team decision: no two-deep racks). "
    f"The drawn layout holds {M['layout']['positions_total']:,} positions; moving {M['picking']['small_parts']['skus']:,} small slow "
    f"parts to bins frees {M['picking']['small_parts']['freed_rack_locations']:,} locations, so the peak need fits — and no telescopic forks are needed.",
    "**Picking:** zone + batch/wave picking (batches the 50% single-line orders); A-movers in a golden-zone "
    "forward pick; voice/RF; put-to-light consolidation at pack.",
    "**MHE:** reach trucks with standard forks (Jungheinrich ETV 216i), pick trolleys for small orders and walkie "
    "pallet trucks (EJE 120i) for large orders, rider pallet trucks (ERE 225) at the docks, voice/RF, print-and-apply "
    "— sized in Deliverable 2.",
    "**Policies:** velocity (demand-ABC) slotting, hybrid random-within-zone storage, min/max replenishment, "
    "FIFO via FIF DATE where relevant.",
    "**Verdict:** fits the envelope, materially lower travel/labour than A thanks to slotting and batching, moderate CAPEX — strongest business case.",
])
doc.add_heading("Option C — High-density / semi-automated", level=2)
bullets([
    "**Storage:** VNA (man-up turret) for reserve + automated small-parts store (shuttle/AutoStore-style) for "
    f"the large C each-pick tail. ≈{pct['VNA']:.0f}% of the envelope (densest).",
    "**Picking:** goods-to-person / pick-to-light for smalls; VNA combined storage+pick; automated sortation.",
    "**MHE:** VNA turret trucks + guidance, automation modules, minimal manual MHE.",
    "**Verdict:** densest and lowest labour, but highest CAPEX and complexity; ROI depends on labour cost.",
])

# ============================ 12. DECISION MATRIX ============================
doc.add_heading("15. Decision matrix & recommendation", level=1)
dec = M2["decision"]
wt = dec["weighted_totals"]
order = dec["ranking"]
table(["Option", "Weighted score (max 5)", "Result"],
      [[o, f"{wt[o]:.2f}", "RECOMMENDED" if o == dec["winner"] else ("Strong alternative" if wt[o] >= 3.5 else "Baseline")]
       for o in order], widths=[6.0, 4.5, 4.5])
para("Weight-sensitivity (robustness):", space_after=4)
sens = dec["sensitivity"]
table(["Option", "Base", "Cost-driven", "Space-driven"],
      [[o, f"{sens[o]['base']:.2f}", f"{sens[o]['cost_driven']:.2f}", f"{sens[o]['space_driven']:.2f}"] for o in order],
      widths=[6.0, 3.0, 3.0, 3.0])
figure("decision_matrix.png", "Fig 8. Weighted decision-matrix scores.", 12)
bullets([
    f"**Recommended: {dec['winner']}.** It wins on base and cost-driven weightings; C overtakes only when "
    "space is the dominant criterion — likely if A008 resolves to a small Assa-only envelope.",
    f"**Why (data):** single-deep reach racking holds the corrected target in ≈{pct['Selective - narrow aisle']:.0f}% of the envelope "
    f"with every pallet directly accessible (no honeycombing); {ptl.get('each', 0):.0f}% of order lines are each-picks "
    "and 50% of orders single-line → batch/zone picking from a fast-pick area is the biggest labour lever; 48.6% "
    "ABC mismatch → velocity slotting is a cheap, high-value win; 73% single-load tail → dense reserve.",
    "**Conditions before locking:** confirm the 7,000 m² scope (A008); obtain labour/equipment costs (A006) to "
    "confirm B vs C in the financial model (done in Deliverable 3); the EURO/K3/XLONG pallet mix was checked against the "
    "single-deep racks in Deliverable 3 (long pallets up to 2.05 m in 4.5 m bays behind a 3.2 m aisle).",
])
para("Recommended concept preview (detailed layout and 3D in Deliverable 2):", size=9.5, color=GREY, italic=True, space_after=4)
figure("layout_floorplan.png", "Fig 9. Recommended Option B — warehouse floor plan (rack-level, to scale).", 16)

# ============================ 13. ASSUMPTIONS ============================
doc.add_heading("16. Assumptions & open questions", level=1)
para("Logged in data/assumptions.json. Items that materially affect the design:")
rows = [[a_["id"], a_["assumption"], a_["impact"].upper()]
        for a_ in ASSUM["assumptions"] if a_["impact"] == "high"]
table(["ID", "Assumption / open question", "Impact"], rows, widths=[1.5, 11.5, 2.0], align_right_from=2)

add_reference_list(doc, USED)
tag_headings(doc, "D1")
update_fields_on_open(doc)

page_number_footer()

DELIV = os.path.join(BASE, "deliverables"); os.makedirs(DELIV, exist_ok=True)
out = os.path.join(DELIV, "Deliverable_1_Analysis.docx")
doc.save(out)
print("Saved:", out)
