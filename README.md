# Assa Abloy Warehouse Redesign — DHL Supply Chain, Bemmel

University warehouse-design project: develop a more efficient, effective **alternative
warehouse design** for the Assa Abloy operation at DHL Bemmel (WH `NL_0032`), based on
actual operational data. Data-driven and end-to-end (receiving → storage → picking → shipping),
within a **7,000 m²** footprint and **12.2 m** height.

## Status
- ✅ **Phase 0 — Data ingestion** complete: data inventory, dictionary, quality assessment, gap analysis, initial requirements. See [`outputs/reports/phase0_summary.md`](outputs/reports/phase0_summary.md).
- ⏳ Phase 1 — Analysis (SKU / inventory / ABC / order / peak / capacity) — next.

## Data (Q2 2025)
- **Storage snapshots** ×3 (01-04/05/06) — inventory details, ~16.6k–17.3k records each.
- **Outbound** ×3 months — 39,069 order lines, 8,781 orders, 61 ship-days.

> ⚠️ **Raw data is confidential** (DHL/Assa Abloy operational data + customer PII). It is
> stored in `data/raw/` **only because this repository is private**. If the repo is ever
> made public, re-exclude `data/raw/` in `.gitignore` before pushing.

## Layout
```
data/           raw (ignored), processed, config + assumptions, scenarios
analysis/       python: load_data, data_quality, + phase-1 scripts to come
warehouse_model/ parametric Blender model (later phases)
outputs/        figures, tables, kpis, blender, reports
documentation/  data_dictionary, methodology, sources, assumptions
```

## Run
```bash
# Python 3.12 with pandas, numpy, openpyxl, matplotlib
python analysis/data_quality.py   # regenerates the Phase 0 quality report + metrics
```

## Deliverables & dates
| Deliverable | Due |
|---|---|
| Analysis | 16-09-2026 |
| Future state | 07-10-2026 |
| Performance overview | 21-10-2026 |
| Project completion | 31-10-2026 |
