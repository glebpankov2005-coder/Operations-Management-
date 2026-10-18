# Assa Abloy Warehouse Redesign — DHL Supply Chain, Bemmel

**Project OTM** — a data-driven, end-to-end redesign of the Assa Abloy warehouse operation at
DHL Supply Chain, Bemmel (WH `NL_0032`), within a **7,000 m²** footprint and **12.2 m** height.
Covers receiving → storage → picking → shipping, with every decision traced back to the operational data.

> ⚠️ **Private repository** — contains confidential DHL/Assa Abloy data and customer PII (in `data/raw/`).
> If ever made public, re-exclude `data/raw/` in `.gitignore` first.

## 📦 Deliverables (the graded documents)
| # | Document | Status | Due |
|---|---|---|---|
| 1 | [`deliverables/Deliverable_1_Analysis.docx`](deliverables/Deliverable_1_Analysis.docx) — data analysis, design options, decision matrix | ✅ v2 (updated with D3) | 16-09-2026 |
| 2 | [`deliverables/Deliverable_2_Future_State.docx`](deliverables/Deliverable_2_Future_State.docx) — processes, docks, MHE, 3D layout, capacity plan | ✅ v3 | 07-10-2026 |
| 3 | [`deliverables/Deliverable_3_Performance_Overview.docx`](deliverables/Deliverable_3_Performance_Overview.docx) — KPIs, sorting, machinery review, CAPEX/OPEX, payback, sensitivity | ✅ v1 | 21-10-2026 |
| 3 | [`deliverables/Deliverable_3_Calculations.xlsx`](deliverables/Deliverable_3_Calculations.xlsx) — every cost as a live formula (change an input, totals update) | ✅ v1 | 21-10-2026 |

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
| `geometry.py` | Shared Option B layout geometry for the travel / cycle-time models |
| `picking_plan.py` | Order volume segmentation, pick-time model (lines/h, FTE), picking equipment, tugger evaluation |
| `dock_mhe_plan.py` | Dock doors, trailer departure plan, Jungheinrich fleet, turning checks, machinery justification, container options, 08:00 release |
| `design_evaluation.py` | Week 3 alignment: U-shaped vs flow-through evaluation, COI slotting + affinity, lead time per region, class data checks, hazmat vs PGS 15, W3 KPIs |
| `warehouse_floorplan.py` | To-scale floor plan + order-flow figure; **single source for zone areas and counted rack positions** (`layout` metrics) |
| `flowcharts.py` · `flow_swimlane.py` | Process flowcharts and the swimlane |
| `performance_cost.py` | D3: KPIs (today vs future), per-order lead-time model, CAPEX/OPEX, unit costs, payback, sensitivity, 150–250% stress test |
| `build_report.py` · `build_report_d2.py` · `build_report_d3.py` · `build_workbook_d3.py` | Generate the Word deliverables and the D3 calculation workbook |
| `layout.py` | Legacy (D1 block plan, old 14,074 target) — superseded by `warehouse_floorplan.py`, not in the run order |
| `warehouse_model/*.py` | Blender 3D renders (`blender --background --python warehouse_model/main.py`; set `BLENDER_ENGINE=CYCLES` on machines without a GPU), then `python warehouse_model/annotate_render.py` |

## ▶️ Reproduce
Python 3.12+ with `pandas numpy openpyxl matplotlib python-docx` (set `PYTHONIOENCODING=utf-8`).
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
python analysis/performance_cost.py    # D3: KPIs, CAPEX/OPEX, payback, sensitivity, stress test
python analysis/build_report.py        # Deliverable 1 .docx
python analysis/build_report_d2.py     # Deliverable 2 .docx
python analysis/build_report_d3.py     # Deliverable 3 .docx
python analysis/build_workbook_d3.py   # Deliverable 3 calculation workbook .xlsx
```

## 🔑 Headline findings
- Peak **8,512 occupied locations** (pallet positions; 11,015 loads sit in them) → design target **~9,500** positions.
- Racks are **single-deep, back-to-back**: 11 modules give **9,504 counted positions**; layout uses **6,731 m² (96%)** incl. a 190 m² loose-container zone.
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
- **D3:** CAPEX **€1.63M** all-new (**€0.46M** if today's racking is re-used), OPEX **€455k/yr**, **€3.78 per order line**; picking 31 → 11 picker-h/day saves ~€144k/yr → payback **3.2 yrs** (re-used racking) / 11.3 yrs (all new); orders out within 24 h 37% → 65%.
- **Risk:** occupied locations grew 16%/quarter (Apr–Jun) → ~2 months of rack headroom; clear dead stock (21% of loads > 1 yr) and keep room for a 12th module.

## ❓ Open items (see `data/assumptions.json`)
- **A008** — is 7,000 m² the whole 4-client site or the Assa-only envelope? (Shifts B vs C.)
- **A006 / A014 / A030 / A038** — DHL labour cost, real productivities, Jungheinrich lease quote (D3 uses sourced benchmarks).
- **A033** — type and condition of today's racking (re-use decides CAPEX €0.46M vs €1.63M).
- **A019 / A026** — container numbers; contractor price per container (worth it only below ~€179).
- **A020 / A027** — carriers accepting the departure slots.
- **A025** — pick-time standards to validate with DHL time studies.
- **A028** — hazard class of the 138 flagged SKUs (hazmat section not in the budget).
