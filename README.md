# Assa Abloy Warehouse Redesign — DHL Supply Chain, Bemmel

**Project OTM** — a data-driven, end-to-end redesign of the Assa Abloy warehouse operation at
DHL Supply Chain, Bemmel (WH `NL_0032`), within a **7,000 m²** footprint and **12.2 m** height.
Covers receiving → storage → picking → shipping, with every decision traced back to the operational data.

> ⚠️ **Private repository** — contains confidential DHL/Assa Abloy data and customer PII (in `data/raw/`).
> If ever made public, re-exclude `data/raw/` in `.gitignore` first.

## 📦 Deliverables (the graded documents)
| # | Document | Status | Due |
|---|---|---|---|
| 1 | [`deliverables/Deliverable_1_Analysis.docx`](deliverables/Deliverable_1_Analysis.docx) — data analysis, design options, decision matrix | ✅ v2 | 16-09-2026 |
| 2 | [`deliverables/Deliverable_2_Future_State.docx`](deliverables/Deliverable_2_Future_State.docx) — processes, docks, MHE, 3D layout, capacity plan | ✅ v2 | 07-10-2026 |
| 3 | Performance overview — KPIs + CAPEX/OPEX financials | ⏳ to do | 21-10-2026 |

The Word files are **generated** from the analysis by `analysis/build_report.py` and
`analysis/build_report_d2.py`, so they always match the underlying numbers.

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
| `dock_mhe_plan.py` | Dock-door calculation (inbound & outbound), Jungheinrich MHE fleet, 08:00 order-release analysis |
| `warehouse_floorplan.py` | To-scale floor plan + main order-flow figure (docks, aisles, arrows) |
| `flowcharts.py` · `layout.py` | Process flowcharts, 2D layout/order/worker flow, 3D massing |
| `build_report.py` · `build_report_d2.py` | Generate the Word deliverables |

## ▶️ Reproduce
Python 3.12 with `pandas numpy openpyxl matplotlib python-docx`.
```bash
python analysis/data_quality.py       # Phase 0
python analysis/sku_analysis.py        # + inventory/order/abc/peak
python analysis/capacity.py            # storage concepts
python analysis/decision_matrix.py     # option selection
python analysis/capacity_plan.py       # labour, pick type, inbound, feasibility
python analysis/dock_mhe_plan.py       # dock doors + Jungheinrich MHE + order release
python analysis/flowcharts.py          # process flowcharts
python analysis/layout.py              # layout areas
python analysis/warehouse_floorplan.py # floor plan + main order-flow figure
python analysis/build_report.py        # Deliverable 1 .docx
python analysis/build_report_d2.py     # Deliverable 2 .docx
```

## 🔑 Headline findings
- Peak **8,512 occupied locations** (pallet positions; 11,015 loads sit in them) → design target **~9,500** positions.
- At that target double-deep needs **~61%** of the 7,000 m² envelope (narrow-aisle 72%, VNA 48%) — space no longer decides the concept.
- Demand is concentrated (**13% of SKUs = 80% of volume**); WMS slotting agrees with demand only **48.6%** → re-slot.
- Pick type **derived from the orders**: **75% each / 24% case / 1% full-pallet** lines; **50%** of orders single-line → batch/zone picking.
- The **08:00 pick peak is the order-release backlog** (orders arrive 15–17h, released 16–18h) → release in waves.
- Inbound: **2 shipments/day** from Assa Abloy factories, ~99 loads/day, **~41% loose in containers** (de-stuffed by hand).
- Docks (calculated): **3 receiving** (west, 1 container dock) + **5 shipping** (east, with carrier time slots).
- **Recommended concept: Option B** (hybrid density + velocity slotting + zone/batch picking).
- Labour ≈ **5.4 FTE avg / 10.1 peak**; MHE (Jungheinrich) = **3× ETV 216i** reach truck, **4× ECE 225** order picker, **2× ERE 225** pallet truck.

## ❓ Open items (see `data/assumptions.json`)
- **A008** — is 7,000 m² the whole 4-client site or the Assa-only envelope? (Shifts B vs C.)
- **A006 / A014** — DHL labour rates, equipment prices, real productivities (needed for Deliverable 3).
- **A019 / A020** — container share & de-stuff time; carrier acceptance of collection time slots.
- **A021** — Jungheinrich to confirm telescopic-fork residual capacity at height.
