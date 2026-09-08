# METHODOLOGY

Data-driven, end-to-end warehouse redesign. The 3D layout is the **output** of the
analysis, not the starting point. Development follows the brief's phase sequence.

## Principles
1. **Data is the source of truth.** Nothing is fabricated. Gaps become logged, sourced assumptions with sensitivity analysis.
2. **End-to-end consistency.** Receiving ↔ storage ↔ picking ↔ shipping decisions are aligned; no local optimisation that harms another process.
3. **Average vs Peak kept separate.** Design holds peak; averages are labelled as such.
4. **Traceability.** Every headline number traces back through calculation → dataset → raw file.

## Phases
- **P0 Ingestion** ✅ data inventory, dictionary, quality, gaps, initial requirements. *(this stage)*
- **P1 Analysis** — SKU, inventory, ABC, order, peak, pallet/position requirements, current-state reconstruction.
- **P2 Design options** — ≥3 storage/picking/MHE concepts grounded in the data.
- **P3 Selection** — decision matrix → recommended concept with justification.
- **P4 Future state** — process, policy, slotting, equipment, labour.
- **P5 Capacity plan** — bottom-up space, positions, labour, MHE, throughput.
- **P6 3D model** — parametric Blender model from `data/warehouse_config.json`.
- **P7 Performance** — KPIs, CAPEX, OPEX, current-vs-future.
- **P8 Validation** — QC + sensitivity + risk.
- **P9 Documentation** — report-ready tables, figures, diagrams.

## Environment
- Python 3.12 (`C:\Users\glebp\AppData\Local\Programs\Python\Python312\python.exe`) with pandas / numpy / openpyxl / matplotlib.
- Analysis scripts in `analysis/`; reusable metrics cached in `outputs/reports/phase0_metrics.json`.
- 3D in Blender (free) via Blender-Python, driven by the config JSON.
