# PHASE 0 — DATA INGESTION: SUMMARY & INITIAL FINDINGS

**Project:** Alternative warehouse design for Assa Abloy @ DHL Supply Chain, Bemmel (WH `NL_0032`, client `CID003739NL`)
**Constraints:** ≤ 7,000 m² footprint, ≤ 12.2 m height. Internal operational design only.
**Data window:** 01 Apr – 30 Jun 2025 (Q2). No design has been produced yet — this is analysis groundwork.

---

## 1. DATA INVENTORY

| # | Dataset | Files | Grain | Volume |
|---|---|---|---|---|
| A | Storage / inventory snapshots | 3 (01-04, 01-05, 01-06 2025) | 1 row = inventory detail (`DTLNUM`) | 16,575 / 16,793 / 17,290 records |
| B | Outbound shipping + picking | 3 (202504/05/06) | 1 row = order line | 39,069 lines · 8,781 orders · 61 ship-days |

Both are the **primary source of truth**. Loaders: `analysis/load_data.py`. Full metrics: `outputs/reports/phase0_metrics.json`.

## 2. DATA DICTIONARY
Delivered in full at `documentation/data_dictionary.md` (every meaningful variable → meaning, unit, period, use).

## 3. DATA QUALITY ASSESSMENT
Full report: `outputs/reports/phase0_data_quality.md`. Headlines:

- **Storage is clean at the key level:** `DTLNUM` unique (0 duplicates), `QTY` 0 missing / 0 ≤ 0, pallet dims present on all but 6 rows, each (EA) dims present on 100% of rows.
- **Case data is partial:** `CS QTY` missing on 7,535 / 17,290 (44%) — these are each-pick SKUs with no case pack (expected, not an error).
- **`PART VELOCITY` missing on 1,866** rows; `AISLE`/zone blank on 1,400 (loose/staging stock).
- **Outbound is complete on core fields;** `PICK DATE` missing on a small share, `UNIT PRICE` occasionally blank.
- **Inventory is growing:** occupied locations 7,715 → 8,149 → 8,512; loads 10,176 → 11,015 over the quarter (+8%). Trend matters for capacity.
- ⚠️ **`STAGED STATUS = LATE` on 50.1% of Q2 order lines** — flagged, definition to be confirmed (see §6).

## 4. MISSING DATA (relative to a full design brief)

| Needed for | Missing item | Mitigation |
|---|---|---|
| Receiving design | No dedicated inbound/receipt transaction file | Proxy from `ADD DATE`, `RECEIVE KEY`, `INBOUND TRUCK NO` + snapshot growth (A007) |
| Labour plan | No productivity (picks/putaway per hour), no FTE | Benchmark w/ sources + sensitivity (A006) |
| Equipment plan | No current MHE fleet list | Infer from workload; benchmark specs (A006) |
| Financials | No CAPEX/OPEX, labour rates, rack prices | Sourced market rates + transparent assumptions (A006) |
| Current layout | No rack counts / aisle widths / drawings | Reconstruct current state from `LOCATION`, `AISLE`, `LOC` dims |
| Service | No explicit SLA thresholds | Derive from `EARLY/LATE SHIP DATE`; confirm definition (A005) |

## 5. INITIAL WAREHOUSE REQUIREMENTS (directional — to be firmed in Phase 1)

- **Storage positions:** current occupancy ≈ **8,500 locations / 11,000 loads** and rising ~+4%/month in Q2 → design target must include a growth buffer, not just today's peak.
- **Storage is rack-dominated:** 15,890 / 17,290 (92%) of stock sits in RACK; staging/pack/ship make up the rest → conventional/selective pallet racking is the backbone to beat.
- **Mixed pallet population:** EURO (64%) + K3 (25%) + XLONGPALLET/K1/K2/K5 → rack openings must accommodate more than one pallet footprint incl. long goods.
- **Dual-mode picking:** 23.6% of lines are single-unit and median lines/order = 1 (many small each/case orders), yet max 191 lines/order and full-pallet flags exist → design must serve **both** each/case pick and full-pallet pick.
- **Throughput to size to:** mean **640 order-lines/day**, **peak 1,171/day (1.83×)** on 27 May → capacity plan must hold peak, not average.
- **ABC skew (WMS codes):** A=3,816 / B=3,128 / C=10,346 records → large C tail; a velocity-based forward-pick + reserve split is promising (to be confirmed with our own demand-based ABC in Phase 1).

## 6. QUESTIONS / ASSUMPTIONS TO CONFIRM
Logged in `data/assumptions.json`. The ones that materially change the design:

1. **Is Q2 representative, or is there seasonal peak elsewhere?** (A003) Designing on Q2 peak alone is risky if Sep–Dec is higher.
2. **What exactly does `STAGED STATUS = LATE` measure**, and what is the contractual SLA / order cut-off? (A005) 50% "late" either signals a real service problem to fix or a mislabeled internal threshold.
3. **Any labour productivity / MHE fleet / cost figures available from DHL?** (A006) If yes we use them; if not, everything financial becomes a sourced benchmark + sensitivity.
4. **Confirm 1 load = 1 pallet position** and how multi-detail loads/mixed pallets should be counted (A004).
5. **Is a separate inbound/receiving dataset available?** (A007) It would materially improve the receiving & dock design.

## 7. RECOMMENDED NEXT ANALYTICAL STEPS (Phase 1)

1. **SKU profile** — dims/weight/cube per PART, units & cases per pallet, storage-type classification (pallet vs case vs each).
2. **Inventory analysis** — on-hand per SKU across the 3 snapshots (avg/max/min/variability), cube, load & position counts, growth trend.
3. **Demand-based ABC** — recompute ABC from actual outbound `PICKED QTY` & pick frequency; compare to WMS `PART ABCCOD`; test the real distribution (not assumed 80/20).
4. **Order profile** — lines/order, units/line, order-type & carrier mix, full-pallet vs case vs each split, order affinity.
5. **Peak analysis** — daily/weekly throughput, peak day/week, peak hour from `PICK DATE`, peak inventory position count.
6. **Pallet & storage-position requirement** — bottom-up from inventory + pallet conversion, incl. reserve vs forward-pick split and growth buffer.
7. **Current-state reconstruction** — occupied locations, aisles, zones, LOC dimensions → baseline to compare the future design against.

_Deliverable 1 (Analysis) is due 16-09-2026. Phases 2+ (design options, selection, future state, capacity, 3D, KPIs, finance) follow the sequence in the brief._
