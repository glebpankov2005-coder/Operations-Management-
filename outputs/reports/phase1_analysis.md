# PHASE 1 — ANALYSIS (Deliverable 1 core)

**Project OTM — Assa Abloy @ DHL Bemmel (NL_0032).** Data window: Q2 2025 (Apr–Jun).
All figures measured by `analysis/*.py`; cached in `outputs/reports/phase1_metrics.json`;
tables in `outputs/tables/`, figures in `outputs/figures/`. Nothing fabricated.

---

## 1. SKU PROFILE  (`sku_analysis.py` → `sku_master.csv`)
- **5,291 SKUs** in stock (latest snapshot), across **11 product families**.
- **3,115 SKUs have a case pack; 2,176 are each-only** (≈41% each-only → real each-pick demand).
- **Each size:** median cube 0.0005 m³ (~500 cm³) — mostly small hardware (locks, cylinders, fittings).
- **Units per pallet:** median **1,000**/pallet (mean skewed by high-count small parts).
- **Pallet weight:** median **431 kg** (realistic for EURO). ⚠️ see DQ flag on sentinel values.
- **WMS ABC (stock):** A=454, B=870, C=3,967 SKUs.

## 2. INVENTORY & POSITION REQUIREMENT  (`inventory_analysis.py`)
| Snapshot | Detail recs | Loads (positions) | Occupied locations | Active SKUs | Total eaches | Cube (m³) |
|---|--:|--:|--:|--:|--:|--:|
| 2025-04-01 | 16,575 | 10,176 | 7,715 | 5,164 | 2,898,322 | 3,209 |
| 2025-05-01 | 16,793 | 10,534 | 8,149 | 5,273 | 2,876,129 | 3,434 |
| 2025-06-01 | 17,290 | 11,015 | 8,512 | 5,291 | 2,890,698 | 3,679 |

- **Loads (≈ pallet positions) grew +8.2% in one quarter** (10,176 → 11,015). Cube +15%.
- **Peak concurrent loads = 11,015** → baseline storage-position requirement (before growth buffer & honeycombing losses).
- **Loads/SKU:** mean 2.07, median 1, **max 337**; **72.7% of SKUs occupy a single load** → a very long slow-moving tail sitting one-pallet-deep.
- Eaches held roughly flat (~2.9M) while loads rose → stock **fragmenting into more, less-full locations** (a current-design inefficiency to target).

## 3. ORDER & PICKING PROFILE  (`order_analysis.py` → `order_profile.csv`)
- **8,781 orders / 39,069 lines** over the quarter.
- **Lines/order:** mean 4.45, median **1**, p95 19, max 191 — **50.5% are single-line orders**.
- **Units/line:** mean 34.8, median … , **23.6% single-unit**, p95 150, max 12,020.
- **Pick-type split (by lines):** case/list **60.8%**, each **16.0%**, full-pallet **2.6%**, unflagged/"other" 20.6% (⚠️ DQ).
- **Pick effort (lifts):** case/list **279,669** vs each 30,165 vs pallet 27,801 → **case picking is the dominant labour driver** (~83% of lifts).
- **Delivery lead time (order received → dispatched):** median **52.4 h (~2.2 days)**, p90 **166.9 h (~7 days)**.
- **Channel mix (order type):** NLD 20,944 · EDC 4,703 · BEL 4,596 · DIRECT 4,003 · AMADE (Amazon) 2,216.
- **Geography:** NLD 22,510 · BEL 6,386 · DEU 3,534 · FRA 1,041 · POL 911 → NL hub serving W-Europe.

## 4. DEMAND-BASED ABC  (`abc_analysis.py` → `abc_*.csv`, `abc_pareto.png`)
Actual Pareto (by picked quantity) — **steeper than the classic 80/20**:

| Top X% of SKUs | % of volume |
|---|--:|
| 5% | 58.9% |
| 10% | 74.5% |
| 20% | 88.1% |
| 30% | 94.0% |

**A/B/C by demand volume (thresholds 80/95%):**

| Class | SKUs | % SKUs | % volume | % pick-lines |
|---|--:|--:|--:|--:|
| A | 565 | 13.0% | 80.0% | 41.8% |
| B | 858 | 19.7% | 15.0% | 30.0% |
| C | 2,931 | 67.3% | 5.0% | 28.3% |

- **~13% of SKUs drive 80% of volume**, but **C-class = 67% of SKUs and still 28% of the picks** → forward-pick/fast-lane slotting matters a lot.
- **Agreement between actual-demand ABC and the WMS `PART ABCCOD` is only 48.6%** → the current slotting is misaligned with real demand for ~half of SKUs. **Strong evidence for re-slotting.**
- **4,354 SKUs shipped in Q2**; ~**937 in stock were not shipped** in Q2 (slow/dead candidates) and **855 shipped were not in the latest stock snapshot** (transient/cross-dock/drop-ship — to confirm).

## 5. PEAK ANALYSIS  (`peak_analysis.py` → `throughput_daily.csv`)
| Metric | Average/day | PEAK/day | Peak÷Avg | Peak date |
|---|--:|--:|--:|---|
| Order lines | 640 | **1,171** | 1.83× | 2025-05-27 |
| Units | 22,269 | **63,469** | **2.85×** | 2025-05-27 |
| Orders | 144 | 250 | 1.74× | 2025-04-29 |
| Shipments | — | — | — | — |

- **Design to peak, not average.** Units peak is far spikier (2.85×) than lines (1.83×) → sizing on lines alone understates pick/pack surges.
- **Weekly peak** 3,563 lines (week of 01-Jun) vs ~2,791 avg.
- **Intraday:** morning-loaded, peak around **08:00**; Mon–Fri only (no weekend ops), weekdays fairly even (569–688 lines).

---

## DATA-QUALITY FLAGS RAISED IN PHASE 1 (not silently corrected)
1. **`PA WGT` sentinel/impossible values** — median 431 kg is fine, but p95 = 9,999 kg and max = 60,423 kg are impossible for a single pallet (9,999 looks like a placeholder). Must be capped/cleaned before rack load-rating calcs. *(A rack bay/weight analysis will use cleaned values + flag affected SKUs.)*
2. **`units_per_pallet` extreme mean** (15,171 vs median 1,000) — driven by tiny high-count parts and/or bad `PA QTY`; use robust statistics.
3. **"Other" pick class = 20.6% of lines** — lines with none of PALL/LIST/TROLLEY flags set; method needs definition (query DHL/WMS).
4. **Stock vs demand mismatch** — 937 stocked-not-shipped and 855 shipped-not-stocked; confirm dead stock vs cross-dock handling.

## HEADLINE DESIGN REQUIREMENTS (input to Phase 2 options)
- **Storage:** ~**11,000 pallet positions** today, **growing ~+8%/quarter** → design target ≈ 12,000–13,000 positions incl. buffer *(to finalise with growth & honeycomb assumptions, within the 12.2 m height / 7,000 m² envelope — A008)*.
- **Long slow tail:** 67% C-SKUs, 73% single-load SKUs → reserve/deep or high-density storage for the tail; fast-lane forward pick for A/B.
- **Picking is case-dominant** (83% of lifts) with meaningful each (16% of lines) and minor full-pallet (2.6%) → mixed pick methods; case-pick productivity is the key labour lever.
- **Re-slot to demand:** only 48.6% ABC agreement today.
- **Capacity to peak:** 1,171 lines / 63,469 units on the peak day; ~08:00 intraday peak.

_Next: Phase 2 — develop ≥3 aligned design options (storage concept × picking method × MHE), then a decision matrix (Phase 3)._
