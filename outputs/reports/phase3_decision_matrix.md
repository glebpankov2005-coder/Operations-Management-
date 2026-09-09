# PHASE 3 — DECISION MATRIX & RECOMMENDED CONCEPT (Deliverable 1)

Reproducible scoring in `analysis/decision_matrix.py` → `outputs/tables/decision_matrix.csv`.
Scores are documented **assessments** (1 = worst … 5 = best); space scores are anchored to the
Phase 2 capacity model. Weights are stated and sensitivity-tested.

## Criteria & weights
| Criterion | Weight | Why it matters |
|---|--:|---|
| Space fit (7,000 m²) | 20% | Hard constraint; some concepts don't fit |
| Labour efficiency | 20% | Biggest OPEX driver (case picking = 83% of lifts) |
| CAPEX (lower better) | 15% | Racking + MHE + automation investment |
| Travel / throughput | 15% | Drives peak-day capability & cost per line |
| Flexibility | 10% | Volume +8%/qtr, mix may shift |
| Simplicity / low risk | 10% | Implementation feasibility |
| Peak resilience | 10% | Must hold 1,171 lines / 63,469 units day |

## Weighted result
| Option | Weighted total | Verdict |
|---|--:|---|
| **B — Hybrid density** | **3.75** | ✅ Recommended |
| C — Semi-automated | 3.70 | Strong alternative |
| A — Conventional+ | 3.05 | Baseline, not preferred |

## Weight-sensitivity (robustness check)
| Option | Base | Cost-driven | Space-driven |
|---|--:|--:|--:|
| A — Conventional+ | 3.05 | 3.35 | 3.55 |
| **B — Hybrid** | **3.75** | **3.65** | 4.75 |
| C — Semi-automated | 3.70 | 3.35 | **4.85** |

- **B is the robust choice** — it wins under base *and* cost-driven weightings.
- **C overtakes only when space is the dominant criterion** — which becomes likely **if A008 resolves to a small Assa-only envelope**. So the automation case is real and should be kept alive pending the 7,000 m² answer and the labour-cost inputs (A006).
- **A never wins** — it's cheapest but borderline on space and worst on labour/travel.

## Recommendation — Option B (Hybrid density + velocity slotting + zone/batch picking)

**WHAT:** double-deep reach racking for A/B reserve + selective single-deep for irregular SKUs +
a forward-pick module (carton-flow / shelving) for the case- and each-heavy demand; velocity-based
(demand-ABC) slotting; zone + batch/wave picking with voice/RF.

**WHY (data):**
- Space: double-deep fits at **91%** of the envelope (~6,000–6,400 m²) with buffer, where wide-aisle (144%) does not.
- Labour: **83% of lifts are case picking** and **50% of orders are single-line** → **batch/zone picking + a forward-pick module** is the single biggest labour lever.
- Slotting: WMS ABC agrees with real demand only **48.6%** → velocity slotting is high, low-cost value.
- Tail: **73% single-load / 67% C-class** → dense reserve for the tail, fast forward pick for the **13% of SKUs = 80% of volume**.
- Risk: avoids the high CAPEX and implementation risk of full automation (Option C) while capturing most of the density and labour gains.

**HOW:** velocity-based putaway to zones; min/max forward-pick replenishment; wave release by carrier
cut-off; batch single-line/single-unit orders; put-to-light consolidation at pack; FIFO via `FIF DATE`
where relevant; cantilever for XLONG goods.

**IMPACT:** fits the envelope with growth headroom, materially lower travel and labour than today,
moderate CAPEX, and flexible to volume growth — the strongest overall business case.

## Conditions / next checks before locking
1. **A008** — confirm the 7,000 m² scope. If Assa-only and tight, shift toward **Option C** (VNA/automation).
2. **A006** — obtain labour rates & equipment prices; the financial model (Deliverable 3) will confirm B vs C.
3. Validate double-deep suitability against the pallet-type mix (EURO/K3/XLONG) and SKU-per-location depth.

_Next: Phase 4 — detail Option B's future-state processes, then Phase 5 capacity/labour/MHE plan (Deliverable 2)._
