# PHASE 2 — WAREHOUSE DESIGN OPTIONS (Deliverable 1)

**Project OTM — Assa Abloy @ DHL Bemmel (NL_0032).** Options are aligned end-to-end
(storage × picking × MHE × policies) and grounded in the Phase 1 analysis and the
Phase 2 capacity model (`analysis/capacity.py`, `outputs/reports/phase2_metrics.json`).

## Design requirements this must satisfy (from Phase 1)
| Requirement | Value | Source |
|---|--:|---|
| Design pallet positions (peak 11,015 +15% buffer ÷ 90% util) | **~14,000** | `capacity.py` |
| Height-limited rack levels (p90 load 1.16 m, pitch 1.41 m) | up to **8** | `capacity.py` |
| Peak throughput | **1,171 lines / 63,469 units per day** | `peak_analysis.py` |
| Pick-effort mix (lifts) | case/list **83%**, each 16%, pallet <3% | `order_analysis.py` |
| Order shape | 50% single-line, 24% single-unit | `order_analysis.py` |
| Demand concentration | 13% of SKUs = 80% of volume | `abc_analysis.py` |
| Slow tail | 73% of SKUs single-load; 67% C-class | `inventory_analysis.py` |
| ABC vs WMS mismatch | only 48.6% agreement | `abc_analysis.py` |

**Space reality (capacity model):** a conventional **wide-aisle** layout needs ~10,100 m²
(144% of 7,000) and does **not** fit; **narrow-aisle** single-deep is borderline (107%);
**double-deep** (91%) and **VNA** (72%) fit. Density is therefore not optional.

---

## OPTION A — "Conventional+" (improve the current concept)
*Lowest cost, simplest — the baseline to beat.*
- **Storage:** selective single-deep, **narrow-aisle (reach truck)**, 7 levels. Two-zone ABC (ground-level forward pick + reserve above). ~7,500 m² (⚠️ borderline over envelope).
- **Picking:** RF-directed **discrete + simple batch** for single-line orders; case pick from pick-face; pallet pick from reserve.
- **MHE:** reach trucks, low-level order pickers (LLOP), powered pallet trucks, hand/ring RF scanners.
- **Policies:** ABC 2-class slotting, directed putaway, min/max forward-pick replenishment, S-shape routing.
- **WHAT/WHY/HOW/IMPACT:** keeps today's methods but re-slots and tightens aisles. *Why:* cheapest, low risk. *Impact:* only just fits, highest travel & labour, little peak headroom.

## OPTION B — "Hybrid density + velocity slotting + zone/batch picking"  ⭐ recommended candidate
*Balances space, labour and cost — strongest business case.*
- **Storage:** **double-deep** reach racking for A/B pallet reserve (dense, 91% of envelope) + a slice of selective single-deep for irregular/low-rotation SKUs + a dedicated **forward-pick module** (carton-flow + shelving/light mezzanine) for fast case/each SKUs. XLONG goods on cantilever.
- **Picking:** **zone + batch/wave picking**. Batch the 50% single-line / 24% single-unit orders into multi-order picks (big labour win); wave by carrier cut-off; A-movers in a golden-zone forward pick near dispatch. Pick-to-cart / **voice or RF**; put-to-light sort at pack.
- **MHE:** reach trucks (deep-reach), LLOPs / order pickers, pallet trucks, voice/RF, print-and-apply at pack.
- **Policies:** **velocity-based (demand-ABC) slotting** — fixes the 48.6% mismatch; hybrid random-within-zone storage; family/affinity grouping; min/max replenishment; FIFO via `FIF DATE` where relevant.
- **WHAT/WHY/HOW/IMPACT:** density where it pays (A/B reserve), selectivity where needed, and a forward-pick that cuts travel for the case-heavy workload. *Impact:* fits with buffer, materially lower travel/labour than A, moderate CAPEX.

## OPTION C — "High-density / semi-automated"
*Lowest labour & footprint, highest CAPEX & complexity.*
- **Storage:** **VNA (man-up turret)** for reserve/selective (72% of envelope — lots of spare) **+ automated small-parts** store (shuttle / AutoStore-style) for the large C each-pick tail; goods-to-person stations.
- **Picking:** **goods-to-person / pick-to-light** for smalls; VNA combined storage+pick for the rest; automated sortation to pack.
- **MHE:** VNA turret trucks + wire/rail guidance, automation modules, minimal manual MHE.
- **Policies:** system-directed slotting & replenishment, dynamic (chaotic) storage in the automation, wave release.
- **WHAT/WHY/HOW/IMPACT:** best density and lowest picking labour for the 16% each / long C tail. *Impact:* high CAPEX, longer implementation, less flexible if volumes/mix shift; automation ROI depends on labour cost (to be tested in the financial model).

---

## Cross-option summary
| Dimension | A — Conventional+ | B — Hybrid ⭐ | C — Semi-automated |
|---|---|---|---|
| Storage footprint | ~7,500 m² (tight) | ~6,000–6,400 m² | ~5,000 m² |
| Fits 7,000 m² | Borderline | Yes, with buffer | Yes, easily |
| CAPEX | Low | Medium | High |
| Labour / travel | High | Medium (batching+slotting) | Low |
| Peak resilience | Weak | Good | Good |
| Flexibility | High | High | Lower (automation) |
| Complexity / risk | Low | Medium | High |

Detailed scoring and the recommendation are in `phase3_decision_matrix.md`.

## Open dependencies
- **A008** (7,000 m² whole-site vs Assa envelope) shifts every "fits?" verdict — if Assa gets <7,000 m², Option A is out and B/C become necessary.
- Automation ROI (Option C) needs the labour-rate / cost inputs still to be sourced (**A006**).
