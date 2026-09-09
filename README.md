# Assa Abloy Warehouse Redesign — DHL Supply Chain, Bemmel

**Project OTM** — a data-driven, end-to-end redesign of the Assa Abloy warehouse operation at
DHL Supply Chain, Bemmel (WH `NL_0032`), within a **7,000 m²** footprint and **12.2 m** height.
Covers receiving → storage → picking → shipping, with every decision traced back to the operational data.

> ⚠️ **Private repository** — contains confidential DHL/Assa Abloy data and customer PII (in `data/raw/`).
> If ever made public, re-exclude `data/raw/` in `.gitignore` first.

## 📦 Deliverables (the graded documents)
| # | Document | Status | Due |
|---|---|---|---|
| 1 | [`deliverables/Deliverable_1_Analysis.docx`](deliverables/Deliverable_1_Analysis.docx) — data analysis, design options, decision matrix | ✅ draft | 16-09-2026 |
| 2 | [`deliverables/Deliverable_2_Future_State.docx`](deliverables/Deliverable_2_Future_State.docx) — processes, flowcharts, 3D layout, capacity plan | ✅ draft | 07-10-2026 |
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
| `capacity_plan.py` | Labour (FTE) & MHE plan |
| `flowcharts.py` · `layout.py` | Process flowcharts, 2D layout/order/worker flow, 3D massing |
| `build_report.py` · `build_report_d2.py` | Generate the Word deliverables |

## ▶️ Reproduce
Python 3.12 with `pandas numpy openpyxl matplotlib python-docx`.
```bash
python analysis/data_quality.py       # Phase 0
python analysis/sku_analysis.py        # + inventory/order/abc/peak
python analysis/capacity.py            # storage concepts
python analysis/decision_matrix.py     # option selection
python analysis/capacity_plan.py       # labour + MHE
python analysis/flowcharts.py          # process flowcharts
python analysis/layout.py              # layout + 3D + worker flow
python analysis/build_report.py        # Deliverable 1 .docx
python analysis/build_report_d2.py     # Deliverable 2 .docx
```

## 🔑 Headline findings
- ~**11,015** peak pallet positions, growing **+8%/quarter** → design target ≈ **14,000** positions.
- Wide-aisle racking **doesn't fit** 7,000 m² (144%); **double-deep** (91%) / **VNA** (72%) do.
- Demand is concentrated (**13% of SKUs = 80% of volume**); WMS slotting agrees with demand only **48.6%** → re-slot.
- Picking is **case-dominant** (83% of lifts); **50%** of orders are single-line → batch/zone picking.
- **Recommended concept: Option B** (hybrid density + velocity slotting + zone/batch picking).
- Labour ≈ **4 FTE avg / 7–8 peak**; MHE ≈ 2 reach trucks + 3 order pickers + 1 pallet truck.

## ❓ Open items (see `data/assumptions.json`)
- **A008** — is 7,000 m² the whole 4-client site or the Assa-only envelope? (Shifts B vs C.)
- **A006** — DHL labour rates, equipment prices, real productivities (needed for Deliverable 3).
