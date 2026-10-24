# Assa Abloy Warehouse Redesign — DHL Supply Chain, Bemmel

**Project OTM** — a data-driven, end-to-end redesign of the Assa Abloy warehouse operation at
DHL Supply Chain, Bemmel (WH `NL_0032`), within a **7,000 m²** footprint and **12.2 m** height.
Covers receiving → storage → picking → shipping, with every decision traced back to the operational data.

> ⚠️ **Private repository** — contains confidential DHL/Assa Abloy data and customer PII (in `data/raw/`).
> If ever made public, re-exclude `data/raw/` in `.gitignore` first.

## 📦 Deliverables (the graded documents)
**Final portfolio (hand-in):** [`deliverables/portfolio/Portfolio_Group3_Final.docx`](deliverables/portfolio/Portfolio_Group3_Final.docx) (+ PDF) — the same file for all four students: the whole design (Part 1 Analysis, Part 2 Future state, Part 3 Performance overview), who owns which process (Vidhi – Receiving, Gleb – Storage, Arnau – Picking, Rachel – Shipping) with every section listed per person and the owner's name in each section heading, a check against the assessment form and test grid, and APA references. Word and PDF.

| # | Document | Status | Due |
|---|---|---|---|
| 1 | [`deliverables/Deliverable_1_Analysis.docx`](deliverables/Deliverable_1_Analysis.docx) — data analysis, design options, decision matrix | ✅ v2 (updated with D3) | 16-09-2026 |
| 2 | [`deliverables/Deliverable_2_Future_State.docx`](deliverables/Deliverable_2_Future_State.docx) — processes, docks, MHE, 3D layout, capacity plan | ✅ v3 | 07-10-2026 |
| 3 | [`deliverables/Deliverable_3_Performance_Overview.docx`](deliverables/Deliverable_3_Performance_Overview.docx) — KPIs, zone guide, storage (where + how), sorting, machinery review, CAPEX/OPEX, payback, sensitivity | ✅ v2 | 21-10-2026 |
| 3 | [`deliverables/Deliverable_3_Calculations.xlsx`](deliverables/Deliverable_3_Calculations.xlsx) — every cost as a live formula (change an input, totals update) | ✅ v1 | 21-10-2026 |
| – | [`deliverables/Presentation_Group3_Project_OTM.pptx`](deliverables/Presentation_Group3_Project_OTM.pptx) — final presentation for the client (DHL): 10 main slides in ~13 minutes + appendix for questions, DHL colours, answer first, value for DHL and a 3-step roadmap; takeaway titles, editable charts, source line per slide, speaker notes with presenter and timing (Gleb ~4:00, Arnau, Vidhi and Rachel ~3:00 each) | ✅ v2 | 24-10-2026 |

The Word files and the workbook are **generated** from the analysis by `analysis/build_report.py`,
`build_report_d2.py`, `build_report_d3.py` and `build_workbook_d3.py`, so they always match the underlying numbers.

## 📁 Repository structure
```
├── deliverables/        Final Word documents (the graded artifacts)
├── data/
│   ├── raw/             Source data (Assa Abloy Excel + project brief PDF) — confidential
│   ├── assumptions.json Assumption register (every estimate, with source & impact)
│   └── warehouse_config.json  Parameters for capacity model / future 3D
├── analysis/            Python: data loaders + all analysis & report builders
├── outputs/
│   ├── reports/         Working write-ups (phase*.md) + cached metrics (*.json)
│   ├── figures/         All charts & diagrams (PNG)
│   └── tables/          Result tables (CSV)
└── documentation/       Data dictionary, methodology, sources, project brief
```

## 🔬 Analysis modules (`analysis/`)
| Script | Purpose |
|---|---|
| `load_data.py` | Canonical loaders for the storage & outbound datasets |
| `data_quality.py` | Phase 0 data-quality assessment |
| `sku_analysis.py` · `inventory_analysis.py` · `order_analysis.py` | SKU / inventory / order profiling |
| `abc_analysis.py` · `peak_analysis.py` | Demand-based ABC & peak analysis |
| `capacity.py` | Storage-concept sizing vs the 7,000 m² / 12.2 m envelope |
| `decision_matrix.py` | Weighted option scoring + sensitivity |
| `capacity_plan.py` | Labour (FTE) plan, order-derived pick type, inbound receipts, corrected storage feasibility |
| `geometry.py` | Shared Option B layout geometry: zones, rack modules, doors, and the inside of the fast-pick area, container zone and packing |
| `references.py` | APA 7: turns source IDs into (author, year) citations and writes each report's reference list |
| `team.py` | Who owns which process and which report sections (owner tags in headings, responsibility tables) |
| `presentation_data.py` · `build_presentation.js` | Final presentation: numbers, citations and figure crops from the metrics (`presentation_data.json`), then the .pptx (Node + pptxgenjs, `npm install` once) |
| `build_portfolio.py` · `docx_to_pdf.py` | Final group portfolio (cover, responsibilities and sections per person, assessment check, D1–D3) and its PDF with a refreshed table of contents |
| `layout_draw.py` | Shared drawing of the layout and every zone's inside (used by the floor plan and all explanation figures) |
| `picking_plan.py` | Order volume segmentation, pick-time model (lines/h, FTE), picking equipment, tugger evaluation |
| `dock_mhe_plan.py` | Dock doors, trailer departure plan, Jungheinrich fleet, turning checks, machinery justification, container options, 08:00 release |
| `design_evaluation.py` | Week 3 alignment: U-shaped vs flow-through evaluation, COI slotting + affinity, lead time per region, class data checks, hazmat vs PGS 15, W3 KPIs |
| `warehouse_floorplan.py` | To-scale floor plan + order-flow figure; **single source for zone areas and counted rack positions** (`layout` metrics) |
| `flowcharts.py` · `flow_swimlane.py` | Process flowcharts and the swimlane |
| `putwall_design.py` | Put-to-light wall: where it is (whole layout + enlarged + key) and how it works (side view, 4 steps) |
| `storage_design.py` | Storage: where goods are stored (whole layout + enlarged racks/fast-pick + key) and how (rack and fast-pick side views, 4 steps) |
| `zones_design.py` | Zone guide (all nine zones numbered) and the receiving / container zone / returns enlarged |
| `performance_cost.py` | D3: KPIs (today vs future), per-order lead-time model, CAPEX/OPEX, unit costs, payback, sensitivity, 150–250% stress test |
| `build_report.py` · `build_report_d2.py` · `build_report_d3.py` · `build_workbook_d3.py` | Generate the Word deliverables and the D3 calculation workbook |
| `layout.py` | Legacy (D1 block plan, old 14,074 target) — superseded by `warehouse_floorplan.py`, not in the run order |
| `warehouse_model/*.py` | Blender 3D renders (`blender --background --python warehouse_model/main.py`; set `BLENDER_ENGINE=CYCLES` on machines without a GPU), then `python warehouse_model/annotate_render.py` |

## ▶️ Reproduce
Python 3.12+ with `pandas numpy openpyxl matplotlib python-docx docxcompose` (set `PYTHONIOENCODING=utf-8`); LibreOffice for the PDFs.
```bash
python analysis/data_quality.py       # Phase 0
python analysis/sku_analysis.py        # + inventory/order/abc/peak
python analysis/capacity.py            # storage concepts
python analysis/decision_matrix.py     # option selection
python analysis/warehouse_floorplan.py # floor plan, zones, counted positions (needed by the MHE checks)
python analysis/picking_plan.py        # order segments, pick-time model, picking equipment
python analysis/capacity_plan.py       # labour, pick type, inbound, feasibility
python analysis/dock_mhe_plan.py       # dock doors, MHE fleet, load checks, loose-container zone, order release
python analysis/design_evaluation.py   # W3: layout concepts, COI, lead time per region, KPIs
python analysis/flowcharts.py          # process flowcharts (+ flow_swimlane.py, warehouse_reports.py)
python analysis/putwall_design.py      # put-to-light wall figures
python analysis/storage_design.py      # storage figures (where + how)
python analysis/zones_design.py        # zone guide + inbound zones figure
python analysis/performance_cost.py    # D3: KPIs, CAPEX/OPEX, payback, sensitivity, stress test
python analysis/build_report.py        # Deliverable 1 .docx
python analysis/build_report_d2.py     # Deliverable 2 .docx
python analysis/build_report_d3.py     # Deliverable 3 .docx
python analysis/build_workbook_d3.py   # Deliverable 3 calculation workbook .xlsx
python analysis/build_portfolio.py     # final group portfolio (needs docxcompose)
python3 analysis/docx_to_pdf.py deliverables/portfolio/*.docx   # PDFs (system python3 with LibreOffice UNO)
npm install && npm run deck            # final presentation .pptx (Node 18+; runs presentation_data.py first)
```

## 🔑 Headline findings
- Peak **8,512 occupied locations** (pallet positions; 11,015 loads sit in them) → design target **~9,500** positions.
- Racks are **single-deep, back-to-back**: 11 modules give **8,960 counted positions** (incl. 320 long-goods positions in 4.5 m bays behind a 3.2 m aisle); layout uses **6,731 m² (96%)** incl. a 190 m² loose-container zone.
- **Small parts:** 2,657 slow SKUs with ≤ 50 L of stock move to 188 bin-shelving bays next to the put-wall (frees 1,005 pallet locations); Kardex lifts compared and kept as the upgrade path.
- **Fast-pick area:** 930 carton-flow lanes for the 888 most-picked fast movers (90% of their lines) + a wall row of shelves, long-item shelves and floor pallets → a pick face for all 1,409 A/B SKUs; refilled from the rear, picked from the front. Receiving doors: R2 in the north half (lent to container unpacking on big-container days), R3 in the south half.
- **Feedback checks:** 91% of containers fit their zone (97% when door R2 is lent); outbound staging needs ≤ 100 of 216 m²; packing 423 of 450 m²; max real length 2.05 m (115 longer loads are data errors); hazmat = 2,197 loads, mostly electronics with lithium cells → PGS 37-2.
- Demand is concentrated (**13% of SKUs = 80% of volume**); WMS slotting agrees with demand only **48.6%** → re-slot.
- Pick type **derived from the orders**: **75% each / 24% case / 1% full-pallet** lines; **50%** of orders single-line → batch/zone picking.
- The **08:00 pick peak is the order-release backlog** (orders arrive 15–17h, released 16–18h) → release in waves.
- Inbound: **2 shipments/day** from Assa Abloy factories, ~99 loads/day, **~41% loose in containers** — unpacked in their own zone at door R1.
- Docks (calculated): **3 receiving** (west, 1 container dock) + **5 shipping** (east, with carrier time slots).
- **Recommended concept: Option B** (hybrid density + velocity slotting + zone/batch picking).
- Picking split by **order size** (median order 7 L): 84% small orders → **trolley batch picking**; 16% large orders (88% of volume) → **pick-to-pallet**.
- Every storage aisle is **open at both ends** (front, middle, rear cross-aisles) → no U-turns.
- Trailers leave on a **departure plan** (14 trailer slots over 13 departure times); 3 pick waves planned backwards.
- DHL labour ≈ **4.7 FTE avg / 8.6 peak**; MHE (Jungheinrich, reviewed in D3) = **2× ETV 216i**, **3× EJE 120i**, **2× ERE 225** + **6 pick trolleys** (no telescopic forks; ECE 225 rejected; EZS 130 tugger not needed).
- **D3 (labour €20/h):** CAPEX **€1.63M** all-new (**€0.52M** with re-used racking; **€0.16M** for the process changes), OPEX **€342k/yr**, **€3.09 per order line**; picking 31 → 12 picker-h/day saves ~€101k/yr → process changes pay back in **1.6 yrs**; orders out within 24 h 37% → 65%.
- **Risk:** occupied locations grew 16%/quarter (Apr–Jun) → ~4 months of rack headroom; clear dead stock (21% of loads > 1 yr) and keep room for a 12th module.

## ❓ Open items (see `data/assumptions.json`)
- **A008** — is 7,000 m² the whole 4-client site or the Assa-only envelope? (Shifts B vs C.)
- **A006 / A014 / A030 / A038** — DHL labour cost (D3 uses €20/h from the teacher), real productivities, Jungheinrich lease quote.
- **A033** — type and condition of today's racking (re-use decides CAPEX €0.52M vs €1.63M).
- **A019 / A026** — container numbers; contractor price per container (worth it only below ~€128 at €20/h).
- **A020 / A027** — carriers accepting the departure slots.
- **A025** — pick-time standards to validate with DHL time studies.
- **A028** — UN numbers of the 138 flagged SKUs (likely lithium cells → PGS 37-2; hazmat section not in the budget).
- **A043** — clean the item lengths in the master data (115 loads recorded > 2.05 m).
