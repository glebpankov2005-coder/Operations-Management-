# Storage — briefing for the final presentation (Gleb)

Everything about storage in one place: what the data shows, what we designed and why, every number with how we got it, the risks, and the questions you may get. All numbers come from the project's own analysis (Deliverables 1–3 and the deck), so they match the slides.

---

## 0. The 60-second version — remember this

1. **The need.** At the June 2025 peak, **8,512** pallet places were in use (measured). We move **2,657 small, slow items** to bin shelving, which frees **1,005** places, so the design needs **7,507** places.
2. **The design.** **8,960** places in **single-deep, back-to-back racks**: every pallet can be taken out directly, with no pallet in front of it. 8 levels, 10 aisles of 3.0 m, one reach-truck type (Jungheinrich ETV 216i).
3. **The fill.** 7,507 ÷ 8,960 = **84% full** at the peak, below our 90% working limit.
4. **The risk.** Stock grew **~16% per quarter** (April → June). At that speed the racks are full in **~4 months** (3.6), or ~5.5 with the reserved 12th module. **21% of loads are over a year old**, so clearing dead stock is the first lever.
5. **The fast-pick link.** Storage also keeps the **fast-pick area** full: 31 carton-flow bays (930 lanes) are refilled **from behind** by the reach truck. Pickers work the front, so trucks and pickers never share an aisle.

---

## 1. Your part in the presentation

| Slide | What | Time | Notes |
|---|---|---|---|
| 1 | Cover — open for the group | 0:15 | introduce the four owners |
| 2 | Executive summary | 0:50 | answer first; hand over to Arnau |
| **7** | **Storage** | **1:30** | your process slide |
| 11 | Roadmap + decisions from DHL | 1:00 | close, then Q&A |
| Appendix 13 | "How we calculated: storage" | Q&A | jump here if asked about the numbers |
| Appendix 23 | Open points (stock growth = yours) | Q&A | |

Total speaking time is about **3:35**. The full script is in the speaker notes of each slide.

**Storage slide script (1:30):**
> Storage keeps every pallet and keeps the pick faces full. At the June peak 8,512 pallet places were in use. We move 2,657 small, slow items to bin shelving, which frees 1,005 places, so the design needs 7,507 of its 8,960 places — 84% full. All racks are single-deep, so every pallet can be reached without moving another. The fast-pick area is refilled from behind, so reach trucks and pickers never share an aisle — good for safety. The risk for DHL: stock grew about 16% in one quarter, so at that rate the racks are full in about 4 months. Clearing dead stock with Assa Abloy is the first lever; a 12th rack module is kept in reserve.

**On the slide:**
- left: a bar chart (8,512 / 7,507 / 8,960) and the yellow risk box
- right: three "how it works" points and the cross-section of the fast-pick area
- bottom: the grey "How we calculated it" strip

---

## 2. What the data shows today (measured)

Source: three stock snapshots from the WMS (1 April, 1 May, 1 June 2025) and the order lines April–June 2025.

| | 1 Apr | 1 May | 1 Jun |
|---|---|---|---|
| Occupied pallet places (locations) | 7,715 | 8,149 | **8,512** |
| Loads (pallets / LPNs) | 10,176 | 10,534 | 11,015 |
| Active SKUs | 5,164 | 5,273 | 5,291 |
| Stock volume (m³) | 3,209 | 3,434 | 3,679 |

What it means:
- **Places, not loads, are the real need.** The 11,015 loads sit in 8,512 places, because some places hold more than one load. Counting loads overstated the need.
- **Growth is fast.** Places +10.3% in two months, which is **+15.9% per quarter**. Volume grew +15% in the quarter, while the number of pieces stayed flat at ~2.9 million. Stock is spreading over more, less-full places.
- **A long, slow tail.** 72.7% of SKUs have only one load. Median 1 load per SKU, average 2.07, maximum 337.
- **Dead stock.** **21% of loads** have been in stock for more than a year: their booking-in date is more than 365 days before the 1 June snapshot.
- **The WMS slotting doesn't follow demand.** Our demand-based ABC class agrees with the WMS class for only **48.6%** of SKUs.

**Demand ABC** (by picked quantity: A = first 80%, B = next 15%, C = last 5%):

| Class | SKUs | % of SKUs | % of picked volume | % of pick lines |
|---|---|---|---|---|
| A | 565 | 13.0% | 80% | 41.8% |
| B | 858 | 19.7% | 15% | 29.9% |
| C | 2,931 | 67.3% | 5% | 28.3% |

Steeper than 80/20: the top 5% of SKUs carry 58.9% of the volume, and the top 20% carry 88.1%.

**What is stored:**
- 5,291 SKUs in 11 product families: locks, cylinders, fittings and more.
- Most items are small: the median item is ~500 cm³, about the size of a coffee mug.
- Pallet types (count of SKUs): EURO 2,864 · K3 2,040 · long pallets (XLONG) 168 · others.
- **Load heights:** median 0.96 m, p90 1.16 m, p95 1.32 m.
- **Weight:** the median pallet is 431 kg. 10 loads are over 1 t and 3 are over 1.6 t. The heaviest single item is 90 kg.
- **Length:** the longest real item is ~2 m, about the size of a door. 115 loads are recorded as longer than 2.05 m (up to an "11 m" item weighing 0.5 kg). These are data errors, capped at 2.05 m, which leaves **255 long loads**.
- **Hazardous:** 138 SKUs, 2,197 loads (20% of loads), ~385 t. See section 5.

---

## 3. What we designed

### 3.1 The racks

- **Single-deep, back-to-back pallet racking.** One pallet each side of the rack, so every pallet is directly reachable from an aisle.
- **11 rack modules, 10 storage aisles:** 9 standard modules, 1 odd-items module and 1 long-goods module.
- **Aisles:** 3.0 m storage aisles. 3.2 m for the long-goods aisle and for the cross-aisles and perimeter. Every aisle is open at both ends, with front, middle and rear cross-aisles, so there are no dead ends and no U-turns. Each aisle is ~56 m, split by the middle cross-aisle into two runs of ~26.5 m.
- **Bays:** 3 EUR pallets per 2.7 m bay, with the 800 mm side to the aisle. Long goods: 2 long pallets per 4.5 m bay.
- **Height:** 8 levels with a 1.41 m pitch. That is the p90 load height of 1.16 m plus 0.25 m for the beam and clearance.
  - The top beam is at 10.02 m, and the ETV 216i lifts to 10.7 m.
  - The top load stays ~1 m under the 12.2 m roof, which leaves room for the sprinklers.
- **Racks take 3,505 m²**, 52% of the building. The odd-items and long-goods modules take another 728 m².

### 3.2 The places — 8,960

| Place | What is stored | Places |
|---|---|---|
| Standard modules (9) | full pallets of every item (reserve) and the pick places of slow items | **7,776** = 9 × 18 bays × 3 pallets × 8 levels × 2 sides |
| Odd-items module | loads that are not a standard pallet | **864** |
| Long-goods module | pallets 1.3–2.05 m long (255 loads → 80% full) | **320** = 10 bays × 2 × 8 × 2 |
| **Total** | | **8,960** |
| Reserved 12th module | first expansion; fits in the core | +864 |

### 3.3 Small parts in bins, not on pallets

- **The rule:** C-class items, or items with no demand in Q2, with whole stock ≤ 50 L and each item ≤ 20 L, ≤ 15 kg and ≤ 60 cm.
- **Which items:** 2,657 SKUs, only 31.7 m³ of stock in total. Yet on their own they fill **1,005 pallet places** of ~1 m³ each.
- **Where they go:** 3,424 half-bins (300 × 400 mm, ~20 L) + 15% spare → **188 shelving bays** × 21 bins (7 levels × 3). The shelving takes 207 m² in the packing area, next to the put-to-light wall.
- **Picking:** ~93 lines a day at 50 lines an hour = **1.9 picker-hours** a day.
- **Three options compared** (yearly cost = one-off cost spread over 7 years + picking labour):

| Option | Floor | Pallet places used | One-off | Pick rate | Cost per year |
|---|---|---|---|---|---|
| Keep in pallet racks (today) | 393 m² | 1,005 | €130,650 | 49 lines/h | €28,576 |
| **Bin shelving (chosen)** | 207 m² | 0 | **€69,184** | 50 lines/h | **€19,597** |
| Kardex Shuttle XP 500 lifts (3) | 66 m² | 0 | €224,560 | 75 lines/h | €38,555 |

**Why shelving:** it's the cheapest, it frees 1,005 places, and picked items go straight into the put-to-light wall.

**Why not Kardex now:** it costs ~€19k a year more, and at ~93 lines a day the lifts would stand still most of the day. It's the upgrade path if floor space runs out or small-part volume grows; the bins fit the lift trays.

### 3.4 The fast-pick area — storage keeps it full

There are 1,409 fast movers (A and B items), and every one has a pick face:

| Pick face | Items | Share of fast-pick lines |
|---|---|---|
| Carton-flow lanes: 31 bays × 5 levels × 6 lanes = 930 lanes | 888 (+42 second lanes for the busiest) | 89.5% |
| Shelves (wall row, 26 bays) | 462 | 5.6% |
| Long-item shelves (5 bays) | 42 | 2.0% |
| Floor pallets, heavy or bulky (20 places) | 17 | 2.9% |

- **Which items get a lane:** a lane takes an item up to 28 × 33 × 60 cm and up to 15 kg.
- **Wall row:** 55 of 64 m is used, so 9 m is left for new items.
- **Result:** **71%** of all picked lines come from the fast-pick area, with ~14 m of walking per line. That number is Arnau's KPI, but your slotting makes it possible.

---

## 4. How storage works day to day

### 4.1 Putaway: where does a pallet go?

The scanner decides, not the driver. When a pallet is scanned at receiving, the WMS gives it a place by fixed rules:

| Load | Goes to |
|---|---|
| Long pallet (1.3–2.05 m) | long-goods module, via its 3.2 m aisle |
| Odd load | odd-items module |
| Reserve pallet of a fast mover | racks near the front cross-aisle (short refill trips) |
| Slow mover | further back |
| Small slow part | not the racks: its cartons go into the bins |
| Over 1 t (10 loads) | lowest level |
| Tall load 1.16–1.68 m (940 loads) | top level (1,120 places with ~1.7 m free height) |
| Over 1.6 t (3 loads) or taller still (42 loads) | floor positions, moved with the ERE 225 (2.5 t) |

- **Route:** from the pick-up point in receiving, north on the left perimeter aisle, along a cross-aisle, into the storage aisle. The truck never enters the fast-pick area.
- **Volume:** ~99 pallets a day. One putaway takes **2.4 min** (~25 an hour, from the ETV cycle model). The labour plan uses a safer 20 an hour, which is ~4.9 truck-hours a day.

### 4.2 Refilling the fast-pick area

1. Each lane has a minimum. When a pick takes it below that, the WMS creates a refill task. This is a pull system with min/max.
2. The reach truck takes a reserve pallet down the aisle and puts it in the **refill strip behind the lanes**.
3. The driver slides the cases into the lane from the back. They roll forward, so the oldest cases are always picked first (FIFO by design).
4. **~24 refill pallets a day**, about 1.3 hours of work, mostly between the waves.
5. The wall row is refilled by hand, and floor pallets are swapped with the EJE 120i pallet truck between the waves.

### 4.3 Slotting: which item goes where

- **By demand, not by the old WMS class.** We use demand ABC plus the **cube-per-order index (COI)**: the space an item needs ÷ how often it is picked. A low COI (small item, picked often) means it goes closest to packing.
  - COI confirms ABC: the best fifth of items by COI carries 55% of all picks, the best two fifths 72%.
  - COI corrects ABC in two places. 129 bulky A items go on pallet faces at ground level near packing, not in carton flow. 121 tiny but often-picked C items go into fast-pick shelving.
- **Peak-aware.** The top 1% of items (~43) do 15% of all picks, and A items do 60%. If all fast movers sat in one zone, that zone would jam. So fast movers are spread over the zones (~20% of picks each), and the ~43 busiest items get a second face.
- **Affinity:** 62% of item pairs in multi-line orders share a product family (40% would be chance), so families are slotted together.
- **Re-slot every month**, and add second lanes for the busiest 1% before the peak season.

### 4.4 Stock control and capacity: planning and control (D2 §7.2)

| Activity | How | Why (data) |
|---|---|---|
| Putaway | system-directed by fixed rules; 2 reach trucks | ~99 pallets/day, ~25 per truck-hour |
| Replenishment | min/max per lane (pull), between waves | ~24 refills/day, 930 lanes |
| Slotting | monthly re-slot on ABC + COI | WMS matches demand for only 48.6% |
| Stock control | cycle counts: A every month, B every quarter, C once a year; a quarterly list of loads over 1 year old for Assa Abloy to clear | 21% of loads over a year old; master-data errors |
| Capacity | count occupied places every month; **order the 12th module at 90% full** | +16% per quarter |

### 4.5 Storage KPIs (you own these)

| KPI | Today | Design | Target | Status |
|---|---|---|---|---|
| Rack fill at peak | 8,512 places used | **84%** | ≤ 90% | meets |
| **Storage headroom** | +10% in 2 months | **~4 months** (~5.5 with the 12th module) | ≥ 12 months | **gap** |
| Small-item density | ~2.6 SKUs/m² (one pallet place each) | ~13 SKUs/m² in bins | ≥ 5× better | meets |
| Put-away cycle time | — | 2.4 min per pallet | ≤ 3 min | meets |

---

## 5. Equipment, safety and legal

**Reach truck: Jungheinrich ETV 216i × 2**

| Spec | Value |
|---|---|
| Capacity | 1,600 kg at a 600 mm load centre |
| Lift height | 10.7 m (top beam 10.02 m) |
| Width | 1,270 mm |
| Aisle needed | 2.63–2.79 m (ours: 3.0 m) |
| Battery | Li-ion, opportunity charging |
| Forks | standard; single-deep racks mean no telescopic forks |

- **Why 2 trucks:** peak-day work is 9.2 truck-hours ÷ (7.5 h × 80%) = 1.53, so 2. Average use is 33%, so one breakdown still leaves enough for an average day.
- **Long goods:** a 2.05 m pallet turned crosswise needs a 2,976 mm aisle (VDI formula with ETV data), which is why the long-goods aisle is 3.2 m. Forks go under the long side, so the load centre is ~400 mm and the truck can lift the full 1.6 t.
- **Storage labour:** putaway, refills and full-pallet picks come to ~0.9 FTE on an average day and ~1.7 FTE at the peak.

**Safety:**
- Reach trucks work only in the racks and behind the lanes; pickers work only in the pick aisle and at the lowest rack levels. People and trucks never share a pick face. This is Jungheinrich's "clear traffic guidance".
- In the main aisles trucks drive one way: west up with putaways, east down to packing.

**Legal (EN 15512 / EN 15635):**
- Racks are designed to EN 15512.
- A trained employee does a visual check every week, and an expert inspects at least every 12 months.
- Damage is classed green, amber or red, and every bay shows a load sign.
- The inspection cost is in the budget: €2,500 a year.

**Hazardous goods:**
- 138 SKUs, 2,197 loads (20%), ~385 t.
- 97% are electronic security products: safes, locks, alarms, cameras, readers. They most likely have lithium cells inside (UN3481/UN3091, class 9), so the Dutch rule is **PGS 37-2**, not PGS 15. The thresholds are 333 kg, or 1,000 kg for small cells.
- Only the lubricants (6 loads) fall under PGS 15.
- 33 loads of cardboard boxes are probably a wrong flag.
- A separate hazmat section is reserved. Its size and fire separation wait for the **UN numbers from Assa Abloy**, and it's not in the budget.

> Heads-up: the hazmat sections in the reports carry your name (D2 §5.3, D3 §6.5), but the deck's open-points slide gives the follow-up (asking Assa Abloy for UN numbers) to Vidhi. Agree beforehand who answers a hazmat question.

---

## 6. Every storage number and how we got it

| Number | Calculation | Type |
|---|---|---|
| 8,512 places at the peak | highest of the 3 snapshots (7,715 · 8,149 · 8,512) | measured |
| 1,005 places freed | rack places that hold only small slow items (rule in 3.3) | data + rule |
| 7,507 places needed | 8,512 − 1,005 | calculated |
| 8,960 places | counted on the drawing: 7,776 + 864 + 320 | design |
| 84% fill | 7,507 ÷ 8,960 = 83.8% | calculated |
| +15.9% per quarter | (8,512 ÷ 7,715)^1.5 − 1 → 2 months of growth turned into 3 | calculated |
| 3.6 months headroom | ln(8,960 ÷ 7,507) ÷ ln(1.159) × 3 | calculated |
| 5.5 months with the 12th module | ln(9,824 ÷ 7,507) ÷ ln(1.159) × 3 | calculated |
| 21% dead stock | loads booked in > 365 days before 1 June ÷ all 11,015 loads | measured |
| 1.41 m level pitch → 8 levels | p90 load 1.16 m + 0.25 m beam/clearance; 8 × 1.41 under 12.2 m | calculated |
| 2 reach trucks | 9.2 peak truck-hours ÷ (7.5 h × 80%) = 1.53 → 2 | calculated |
| 2.4 min per putaway | ETV cycle model on our routes (speed, lift, average fork height 5.1 m) | calculated |

**Explaining "3.6 months" in plain words:** stock grows ~16% every three months. Going from 7,507 to 8,960 is +19%, a bit more than one quarter of growth, so 3.6 months. The logarithm just does that exactly.

**Explaining "^1.5":** we only have two months of growth (April → June). Raising it to the power 3/2 turns two months into a quarter.

**Why 90% and not 100% full:** a warehouse needs free places to put pallets away, re-slot and absorb peaks. 90% is our working limit (assumption A010).

---

## 7. What storage costs

| Item | Calculation | € |
|---|---|---|
| Single-deep racking | 8,640 places × €130 (installed) | 1,123,200 |
| Long-goods racking | 320 places × €160 | 51,200 |
| Rack protection, end guards, load signs | 5% of racking | 58,240 |
| **Storage total** | **76% of all investment (before contingency)** | **1,232,640** |
| Small-parts shelving | 188 bays × €200 + 3,948 half-bins × €8 | 69,184 |
| Move-in / re-slotting | each of the 11,015 loads moved once | 11,317 |
| Depreciation, racks | €1,232,640 ÷ 15 years | 82,176 a year |
| Rack inspection | EN 15635 | 2,500 a year |

**Price basis:**
- Racking costs €80–140 per place for the equipment (benchmark), plus 30–50% to install. Our 12 m frames put it in the upper half, so we used **€130**.
- The range tested is **€80–200**. It changes the yearly cost by **€83k**, the second-biggest uncertainty after the labour rate (€86k).

**Re-using today's racking:**
- At ~€25 per place to dismantle and re-assemble, the full design costs **€0.52M** instead of €1.63M, with a payback of ~5 years instead of ~16.
- €25 is an assumption (~20% of a new place). DHL has to confirm the existing racks fit the new layout.

---

## 8. Risks and what we do about them

| Risk | Why it matters | What we do |
|---|---|---|
| **Stock growth** (+16%/quarter) | full in ~4 months; target ≥ 12 | (1) clear dead stock with Assa Abloy (21% of loads > 1 year); (2) 12th module ordered at 90% full (+864 places); (3) ~270 m² of the 7,000 m² stays free |
| Growth may be a season, not a trend | only 3 months of data | track occupied places every month (KPI) |
| Racking price | benchmark, not a quote | get quotes; decide re-use vs new last (roadmap step 3) |
| Data quality | 115 impossible lengths; 493 loads with no height | lengths capped at 2.05 m; check master data at receiving |
| Hazardous goods | class unconfirmed | UN numbers from Assa Abloy → size the hazmat section |

---

## 9. Questions you may get — and answers

**"Your target was 9,500 places. Why does the design have only 8,960?"**
9,500 was 8,512 ÷ 90% before we moved the small parts. Taking 2,657 small items out of the racks frees 1,005 places, so the need is 7,507. 7,507 ÷ 90% = 8,341 places, and we have 8,960, so it's 84% full at the peak.

**"Earlier you had 14,074 positions. What changed?"**
That number counted loads (11,015 × 1.15 buffer ÷ 0.90). Loads overstate the need, because several loads share one place. After feedback we sized on occupied places (8,512).

**"Why single-deep and not double-deep? Double-deep is denser."**
- 73% of items have only one pallet. In double-deep the back pallet would usually be a different item, so the truck often has to move the front pallet first: extra moves and slower putaway.
- Single-deep gives direct access to every pallet, works with standard forks (no telescopic forks), keeps FIFO simple, and still fits: the whole design uses 6,731 of 7,000 m².
- First drafted as double-deep, we changed it as a team decision.

**"The racks are full in four months. Isn't the design too small?"**
- It isn't a size problem: at the peak we are at 84%. The risk is growth.
- 21% of loads are over a year old, so clearing dead stock is the fastest lever and costs nothing to build.
- The 12th module (+864 places) is reserved and fits in the core, and ~270 m² of the building stays free.
- Three months of data can't tell a season from a trend, so DHL should track the number monthly.

**"How did you get 16% per quarter?"**
Occupied places went from 7,715 (1 April) to 8,512 (1 June): +10.3% in two months. To the power 1.5 that gives a quarter: +15.9%.

**"How did you get the 1,005 freed places?"**
We counted rack places in the 1 June snapshot whose contents are only small, slow items (≤ 50 L of stock, each item ≤ 20 L, 15 kg and 60 cm, class C). Those 2,657 items go to bins.

**"Why not a Kardex lift for the small parts?"**
- We compared it: three lifts would cost €224,560 against €69,184 for shelving, and €38,555 a year against €19,597.
- With ~93 small-part lines a day the lifts would mostly stand still.
- It's the upgrade path if space runs out or volume grows, and the bins fit the lift trays.

**"Who decides where a pallet goes?"**
The WMS, by fixed rules: long pallets to the long module, heavy ones low, tall ones on top, fast movers' reserve near the front, slow movers at the back. The driver scans and follows.

**"Why 8 levels?"**
Measured load heights: 90% of loads are 1.16 m or lower. With 0.25 m for the beam and clearance that gives 1.41 m per level, and 8 levels fit under the 12.2 m roof with ~1 m to spare for sprinklers. The ETV 216i lifts 10.7 m and the top beam is at 10.02 m.

**"What about pallets heavier than the truck can lift?"**
Only 3 loads are over 1.6 t. They go to floor positions and are moved with the ERE 225 (2.5 t). The 10 loads over 1 t go on the lowest level.

**"How do you store the long items?"**
- 255 long loads (1.3–2.05 m) go in their own module with 320 places in 4.5 m bays.
- The aisle is 3.2 m, because turning a 2.05 m pallet crosswise needs 2,976 mm.
- Forks go under the long side, so the truck can lift its full 1.6 t.

**"How is the fast-pick area refilled? Isn't that dangerous?"**
From behind. The reach truck drops the pallet in the refill strip behind the lanes and the cases roll forward to the pickers. Trucks and pickers never share an aisle or a pick face.

**"Why two reach trucks?"**
- On the peak day there are 9.2 truck-hours of putaway, refills and full-pallet picks. At 7.5 h × 80% use per truck that needs 2.
- Average use is 33%, so a breakdown still leaves enough for an average day.

**"How do you keep stock accurate?"**
Cycle counts by class: A every month, B every quarter, C once a year. A scan at every move, and a quarterly list of old loads for Assa Abloy.

**"Why slot by demand instead of the WMS class?"**
The WMS class matches real demand for only 48.6% of items: many best-sellers are classed C. We recompute ABC from what was actually picked, and use COI so small, often-picked items sit closest to packing.

**"What does storage cost?"**
- €1.23M of the €1.63M investment is racking: 8,640 places × €130 + long-goods racking + protection.
- These are benchmark prices, €80–200 per place. If DHL can re-use today's racks, the whole design costs €0.52M.

**"What about hazardous goods?"**
- 2,197 loads (20%), mostly electronic security products with lithium cells. That puts them under PGS 37-2, not PGS 15.
- A separate section is reserved. We need the UN numbers from Assa Abloy to size it.

**"Is the storage area big enough for growth in volume, not just stock?"**
In the stress test, 150% volume needs 3 reach trucks instead of 2, still through the same 5 outbound doors; only at double volume do the doors become the limit. More stock (not more flow) is covered by the 12th module and dead-stock clearing.

---

## 10. Where to find it

| Topic | Where |
|---|---|
| SKU profile, stock snapshots, dead stock | D1 §3, §4 (Fig 2b) |
| Demand ABC, WMS mismatch | D1 §8 |
| Storage concepts and the 9,500 target | D1 §13 |
| Putaway, replenishment | D2 §2.1, §2.2 |
| Policies, peak slotting, COI | D2 §3, §3.1, §3.2 |
| Rack and aisle configuration | D2 §5.2 |
| Legal, hazardous goods | D2 §5.3, D3 §6.5 |
| Planning and control | D2 §7.2 |
| Storage space and growth | D3 §2.3 |
| Where and how goods are stored (figures) | D3 §4, §4.1–4.3 |
| Small parts and Kardex | D3 §5.2 |
| Machinery, long goods | D3 §6.1, §6.2 |
| Costs | D3 §7, `Deliverable_3_Calculations.xlsx` |
| Slides | deck slide 7; appendix "How we calculated: storage" and "Open points" |
| Code | `analysis/storage_design.py`, `performance_cost.py`, `picking_plan.py`, `capacity.py` |

---

## 11. Cheat sheet — numbers to know by heart

| | |
|---|---|
| Places in use at the peak (1 June) | **8,512** |
| Places freed by small parts | **1,005** (2,657 items → 188 shelving bays) |
| Places needed | **7,507** |
| Places in the design | **8,960** (7,776 + 864 odd + 320 long) |
| Fill at the peak | **84%** (limit 90%) |
| Growth | **+16% per quarter** |
| Headroom | **~4 months** (3.6); ~5.5 with the 12th module (+864) |
| Dead stock | **21%** of loads over a year old |
| Racks | single-deep, back-to-back · 8 levels × 1.41 m · 10 aisles × 3.0 m · long aisle 3.2 m |
| Reach trucks | **2 × ETV 216i** (1.6 t, 10.7 m lift), 33% average use |
| Putaway | ~99 pallets/day, 2.4 min each |
| Refills | ~24 pallets/day, from behind the lanes |
| Fast-pick | 1,409 items · 930 lanes in 31 bays · 71% of lines |
| Demand ABC | 13% of items = 80% of volume; WMS matches demand for only 48.6% |
| Hazmat | 138 SKUs, 2,197 loads, ~385 t → PGS 37-2 (lithium) |
| Storage investment | **€1.23M** of €1.63M (racks €130/place); re-use option → €0.52M total |
