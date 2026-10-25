# Picking — briefing for the final presentation (Arnau)

Everything you need for your part: where our numbers come from, today's problem, how picking works in our design, every number with how we got it, the risks, and the questions you may get. The words that may be new are explained in the glossary at the end. All numbers come from our reports (Deliverables 1–3) and the deck, so they match the slides.

---

## 0. The 60-second version — remember this

1. **The orders are small.** About **640 order lines and 144 orders a day**. **Half the orders have only one line**, and **75% of lines are single pieces** ("each" picks), not full cases.
2. **Today's problem.** **55% of orders arrive between 15:00 and 17:00.** They are all released at once in the evening, so picking peaks at **08:00 the next morning**, **1.31×** the average hour. Staff is planned for that peak.
3. **Today's cost.** In our model, today's way of working takes **~31 picker-hours a day**: 23.8 h of work, because every tour picks one order across the whole building, plus 7.4 h of extra staff for the 08:00 peak.
4. **Our design.** Split orders by size. Pick small orders **in batches on a trolley** from a **fast-pick area** with the **1,409 best-sellers**, and sort them at a **put-to-light wall**. Release work in **3 waves**. Result: **~11.7 picker-hours a day**.
5. **The saving.** **19.4 hours a day less**, about **€101k a year**. These times are **modelled**, so we propose a time study before go-live.

---

## 1. Your part in the presentation

| Slide | What | Time | Notes |
|---|---|---|---|
| 3 | Where our numbers come from | 0:45 | you take over from Gleb after the executive summary |
| 4 | Today: the problem | 1:30 | hand over to Vidhi at the end |
| 8 | Picking | 1:30 | you take over from Gleb; hand over to Rachel |
| Appendix 14 | "How we calculated: picking" | Q&A | if asked how the picker-hours were calculated |
| Appendix 19 | Operation profile (four V's) | Q&A | if asked what kind of operation this is |
| Appendix 23 | Open points: pick times are modelled (yours) | Q&A | |

Total speaking time is about **3:45**. The full script is also in the speaker notes of each slide.

**Slide 3 script (0:45):**
> Before the results, where do our numbers come from? First, data: the warehouse system's own records for April to June 2025 — 39,069 order lines, three stock snapshots and the trailer times. Second, assumptions: where the data has no answer, for example how many seconds a pick takes or what an hour of labour costs, we wrote the assumption down with its source — 46 of them. Third, models: simple calculations on the same data. For example, we re-timed all 8,774 real orders with our new wave plan. Fourth, checks: we compare today and the design on the same orders, and we tested the biggest uncertainties. On every slide we show the calculation at the bottom, and the appendix has every step.

**Slide 4 script (1:30):**
> This chart is the core of the problem. The grey bars show when orders arrive: 55% come in between three and five in the afternoon. They are all released in one go in the evening, so the red line — picking — peaks at eight the next morning. For DHL this costs on three fronts. Service: only 49.9% of lines are staged on time and 37% of orders leave within 24 hours — both measured in the data. Cost: about 31 picker-hours a day, which we modelled. Space: the racks are almost full. The cause is the way work is released and picked, so that is what our design changes. Vidhi shows the solution.

**Slide 8 script (1:30):**
> Today picking is the biggest block of labour. In our model it takes about 31.1 picker-hours a day: 23.8 hours of work, because every tour picks one order across the whole building, plus 7.4 hours of extra staff for the eight o'clock peak. Our design needs 11.7 hours. Orders are split by size: 84% are small and go on a trolley, large ones go straight onto a pallet. The 1,409 best-sellers sit in the fast-pick area, where 71% of lines are picked. One tour picks for many orders, and the put-to-light wall sorts them and checks every item, which protects accuracy. And work is released in three waves, so the morning peak disappears. These times are modelled, so we propose a time study before go-live.

**What is on your slides:**
- **Slide 3:**
  - four steps: Data (measured) → Assumptions (written down) → Models (calculated) → Checks (tested)
  - one big number per step: **39,069** order lines · **46** assumptions · **8,774** orders re-timed · **+€86k** a year if labour costs €28 instead of €20 an hour
  - bottom line: how to read our numbers (**measured** = straight from the data · **modelled** = our calculation · **target** = what the design is built to reach)
- **Slide 4:**
  - left: a chart of orders arriving (grey bars) and lines picked (red line) per hour of the day
  - right: three boxes (Service · Cost · Space)
  - bottom: the "How we calculated it" strip
- **Slide 8:**
  - left: a bar chart of picker-hours (today 31.1 = 23.8 work + 7.4 peak staff; design 11.7)
  - right: four "how it works" points
  - bottom: the calculation strip

### The whole presentation — who says what

| # | Slide | Presenter | Time |
|---|---|---|---|
| 1 | Cover | Gleb | 0:15 |
| 2 | Executive summary | Gleb | 0:50 |
| 3 | **Where our numbers come from** | **Arnau** | 0:45 |
| 4 | **Today: the problem** | **Arnau** | 1:30 |
| 5 | Our solution (layout) | Vidhi | 1:30 |
| 6 | Receiving | Vidhi | 1:30 |
| 7 | Storage | Gleb | 1:30 |
| 8 | **Picking** | **Arnau** | 1:30 |
| 9 | Shipping | Rachel | 1:30 |
| 10 | Value for DHL | Rachel | 1:30 |
| 11 | Roadmap and decisions | Gleb | 1:00 |
| 12 | Questions | all | — |

The total is about 13½ minutes, which leaves time for the handovers.

---

## 2. Where our numbers come from (slide 3)

| Step | What it means | Examples |
|---|---|---|
| 1 Data (measured) | the warehouse system's own records (WMS), April–June 2025 | 39,069 order lines; 8,781 orders over 61 working days; 3 stock snapshots, up to 11,015 loads in 8,512 places; ~15 outbound trailers a day with arrive and dispatch times |
| 2 Assumptions (written down) | where the data has no answer, we wrote down a value with its reason and source: 46 in the register | 25 seconds per picked line, walking 0.8 m/s, +10% for delays; €20 an hour for an operator (course teacher); racking €130 per place (benchmark €80–200) |
| 3 Models (calculated) | simple calculations on the same data | pick time per tour = set-up + walking + time per line; storage growth from the three snapshots; every cost formula in the D3 workbook |
| 4 Checks (tested) | we compare today and the design on the same orders, and test what happens if an assumption is wrong | labour €20 → €28 an hour = +€86k a year; racking price and productivity ±20%; stress test at 150–250% volume |

**The biggest uncertainties** (how much the yearly cost of €483k changes):

| What we change | Range | Change in yearly cost |
|---|---|---|
| Labour rate | €20 → €28 an hour | +€85,784 (the "+€86k" on the slide) |
| Racking price | €80 → €200 per place | €82,790 between low and high |
| Productivity | ±20% labour hours | €73,291 between low and high |
| Reach-truck lease | €495 → €1,550 a month | €25,320 between low and high |

**Data we did not trust** (flagged, not quietly fixed):
- Pallet weights of 9,999 kg are placeholders.
- 76 items are recorded as longer than 2.05 m. Those are data errors, e.g. 10.95 m for a 0.5 kg item.
- 20.6% of lines have no pick flag. So we worked out the pick type ourselves from the ordered quantity (see 3.2).

---

## 3. What the data shows (measured)

### 3.1 The orders

| Measure | Average | Median | p95 | Max |
|---|---|---|---|---|
| Lines per order | 4.45 | 1 | 19 | 191 |
| Units per line | 34.8 | 5 | 150 | 12,020 |
| Units per order | 155 | 8 | 575 | 20,480 |

- **8,781 orders and 39,069 order lines** in 61 working days. That's **~144 orders and ~640 lines a day**.
- **50.5% of orders have one line**, and 23.6% of lines are a single unit.
- **Order size:** the median order is only **7 litres and 5 kg**. **75% of orders fit in one tote**, 89% in four totes, and 98% on one pallet.

### 3.2 What kind of pick

We compared each line's quantity with the item's case and pallet quantity:

| Pick type | Share of lines | Share of units |
|---|---|---|
| Each (single pieces, less than a case) | 75% | 26% |
| Case (full boxes) | 24% | 61% |
| Full pallet | 1% | 13% |

- Picking is **"each" work by number of lines.** Lines drive the labour.
- By volume it's mostly **cases**.
- DHL's old pick flags reflect past practice, so we did not use them for the design.

### 3.3 Peaks

| Measure | Average day | Busiest day | Busiest ÷ average |
|---|---|---|---|
| Order lines | 640 | 1,171 (27 May 2025) | **1.83×** |
| Units | 22,269 | 63,469 (27 May 2025) | **2.85×** |
| Orders | 144 | 250 (29 April 2025) | 1.74× |

- **The 08:00 peak is self-made.** 55% of orders arrive 15:00–17:00, about 43% are released between 16:00 and 18:00, and they are picked the next morning. The whole backlog lands on the floor at the start of the shift: the 08:00 hour is **1.31×** the average picking hour.
- Levelling this load frees **~24%** of peak-hour picker capacity.
- Work is Monday–Friday only, and the weekdays are fairly even.

### 3.4 Where the stock sits today

The WMS class (A/B/C) of an item agrees with its real demand for only **48.6%** of items. Fast items are spread over all aisles, so pickers walk far.

---

## 4. How picking works in our design

### 4.1 Step 1 — split orders by size

| Segment | Orders a day | Lines a day | % of orders | % of lines | % of volume | How it's picked |
|---|---|---|---|---|---|---|
| **Small** (up to 160 L and 60 kg = 4 totes) | 120 | 291 | **84%** | 46% | 12% | trolley with 6 totes, batch picking |
| **Large** | 23 | 343 | **16%** | 54% | **88%** | straight onto a pallet with the EJE 120i pallet truck, one order per pallet |

### 4.2 Step 2 — best-sellers close by (the fast-pick area)

- The **1,409 best-sellers** (A and B items) get a pick face in the **fast-pick area** next to packing:
  - **31 carton-flow bays** with **930 lanes** hold 888 items, plus 42 second lanes for the top 1%
  - across the pick aisle, a wall row: **26 shelving bays** (462 items), **5 long-item bays** (42 items up to ~2 m) and **20 floor pallet faces** (17 heavy or bulky items)
- **71% of all picked lines** come from this area.
- **Gleb's reach truck refills the lanes from behind**, so pickers never wait for a truck and never share an aisle with one.
- **Small, slow parts** (2,657 items) sit in **bin shelving** next to the put-to-light wall: about **93 lines a day** at 50 lines an hour.

### 4.3 Step 3 — batch, then sort (put-to-light wall)

1. The WMS fills a **trolley** (3 shelves, 6 totes of 40 L) with lines from many small orders. It closes the batch at **80% of the trolley's volume (240 L) or weight (250 kg)**, so no trip is overloaded and none runs nearly empty. That's about **31 lines for ~4.4 orders** per tour.
2. Tours are per zone. A **fast-pick tour** walks the fast-pick area with a **return route** (in and back out the same way). A **reserve tour** picks slow items from the low levels of the reserve aisles with the **largest-gap route** (see 4.5). Every pick is scanned.
3. At the **put-to-light wall** (120 slots, 24 columns × 5 levels, 10.8 m long) the picker scans each item. A light shows which slot (= which order) it goes in. That takes about **8 seconds per line**.
4. When an order is complete, its slot lights up. The packer takes it out, packs it and puts it in the roll cage of its carrier. The wall only releases **complete, correct orders**, so it also checks every item.

**Large orders:**
- One order per pallet on the **EJE 120i** pallet truck.
- About 15 lines: ~12 in the fast-pick area and ~2 in the reserve; small parts are picked separately at the shelving.
- About **279 m** and **18 minutes** per order.
- The pallet is dropped at packing, wrapped and staged.

### 4.4 Step 4 — three waves a day

| Wave | Time | What's in it |
|---|---|---|
| W1 | 06:00–09:30 | the afternoon orders from the day before |
| W2 | 09:30–12:45 | the rest of the backlog + morning orders |
| W3 | 12:45–15:15 | orders received before 12:00, which leave the same day |

- The waves are planned **backwards from the trailer departures** (Rachel's plan). Each wave ends at least **45 minutes before** its trailers leave.
- Each wave is about **213 lines** on an average day. Pickers per wave = the wave's lines ÷ the pick rate of each zone. The busiest wave needs about **3 pickers**.
- **Order of work** inside a wave: earliest departure first. Small orders are batched per zone; large orders go one per pallet.
- **Control:** lines picked are checked against the plan every hour. A wave that runs late gets a picker from another zone, and its orders for the earliest departures are picked first.

### 4.5 Routing — which way the picker walks

In the reserve aisles we compared four standard routes for a trolley tour with 16 lines:

| Route | What the picker does | Walk per tour |
|---|---|---|
| S-shape | walks through every aisle that has a pick, from end to end | 572 m |
| Return | goes into each aisle and comes back out the same end | 682 m |
| Midpoint | picks the front half from the front and the back half from the back | 488 m |
| **Largest gap (chosen)** | in each aisle, skips the biggest empty stretch between picks and turns back there | **471 m** |

- Largest gap only works because **every aisle is open at both ends**.
- The fast-pick area is one long face, so it uses a simple return route from packing.

### 4.6 Equipment for picking

| Item | Needed | Planned | Why this number |
|---|---|---|---|
| Pick trolley (3 shelves, 6 totes) | 1 | 6 | 2 per picker (one picking, one at the wall) + 2 spare |
| Totes 600 × 400 mm (~40 L) | 36 | 54 | trolleys × 6 + 50% in circulation at packing |
| EJE 120i walkie pallet truck | 3 | 3 | peak hours ÷ (7.5 h × 80% use) |
| Put-to-light wall | 120 slots | 120 slots | busiest wave ~73 small orders × 1.35 totes + 20% |
| RF scanners | — | 14 (whole site) | one per person at the peak + 20% |

**About the EJE 120i (Jungheinrich):**
- carries 2 tonnes
- only 1.58 m long and 0.72 m wide
- the aisles are open at both ends, so it never needs a U-turn
- busy about 31% of an average day

**What we looked at and did not choose:**

| Option | Why not |
|---|---|
| Paper pick lists | 5,291 items, many look-alike parts → error-prone, and no live stock |
| Pick-to-light on every pick face | fastest per pick, but a light on thousands of faces costs too much for ~640 lines a day |
| Voice picking | hands-free, but the item still needs a scan; kept as an option for large orders |
| Tugger train (EZS 130) | only ~9 trolley trips a day: a driver would be 26% busy to save pickers ~6 minutes of walking. Worth it if small orders roughly triple |
| ECE 225 order picker | 3.67 m long, too long to turn in the 3.0 m aisles |

### 4.7 Your KPIs

| KPI | How we calculate it | Today | Design | Target |
|---|---|---|---|---|
| Picking hours per day | picker-hours on an average day | ~31 h (modelled) | **11.7 h** | — |
| Pick rate | order lines ÷ picker-hours | — | **~54 lines/h** | ≥ 50 |
| Fast-pick hit rate | lines from the fast-pick area ÷ all lines | — | **71%** | ≥ 60% |
| Walking per picked line | metres walked ÷ lines picked | — | **~14 m** | ≤ 15 m |
| Trolley fill | volume or weight used per tour | — | **80%** | 75–85% |
| Small-parts picking time | small-parts lines ÷ 50 lines/h | — | **1.9 h a day** | ≤ 2 h |
| Pick accuracy | % of orders without a picking error | not in the data | **≥ 99.7%** (target) | benchmark median 99.3%, best 99.68% |

Pick accuracy is a **target**: every pick is scanned and the put-to-light wall checks every item. We can't calculate it from the data.

---

## 5. Every picking number and how we got it

**The formula for every tour:**
time per tour = (set-up + walking distance ÷ walking speed + lines × seconds per line) × 1.10 for delays

| Input | Small orders (trolley) | Large orders (pallet truck) |
|---|---|---|
| Set-up per tour | 90 s | 180 s |
| Speed | 0.8 m/s walking | 1.01 m/s with the EJE 120i |
| Time per line | 25 s | 40 s |
| Delays | +10% | +10% |

| # | Step | Calculation | Result | Type |
|---|---|---|---|---|
| 1 | Today: one tour per order | 120 small orders (2.4 lines) + 23 large orders (14.9 lines) a day, picks spread over all 10 reserve aisles | 23.77 h | model |
| 2 | Today: staffed for the peak | 23.77 × 1.31 (08:00 hour ÷ average picking hour, measured) | **31.1 h** | model |
| 3 | Fast-pick trolley tour | (90 + 123 m ÷ 0.8 + 30.7 lines × 25) × 1.10 = 18.5 min → 99 lines/h; 188 lines ÷ 99 | 1.9 h | model |
| 4 | Reserve trolley tour | (90 + 471 ÷ 0.8 + 16 × 25) × 1.10 = 19.8 min → 49 lines/h; 50 lines ÷ 49 | 1.0 h | model |
| 5 | Large orders | (180 + 279 ÷ 1.01 + 13.1 × 40) × 1.10 = 18 min per order; 23 orders × 18 min | 6.9 h | model |
| 6 | Small-parts shelving | 93 lines ÷ 50 lines/h (benchmark for shelving) | 1.9 h | model |
| 7 | Design total | 1.9 + 1.0 + 6.9 + 1.9 | **11.7 h** | model |
| 8 | Hours saved a day | 31.1 − 11.7 = 12.1 h (batching + fast-pick area) + 7.4 h (no peak staffing) | **19.4 h** | model |
| 9 | Saving in euros | 19.443 h ÷ 7.5 productive h × 8 paid h × 244 days × €20 | **€101,208 a year** | model + assumption |

**Example in words (step 3):**
- A trolley tour in the fast-pick area picks 30.7 lines and walks 123 m.
- Set-up 90 s, walking 123 ÷ 0.8 = 154 s, picking 30.7 × 25 = 768 s. Together that's 1,011 s; plus 10% = 1,112 s = **18.5 minutes**.
- 30.7 lines in 18.5 minutes = **99 lines an hour**.
- 188 lines a day ÷ 99 = **1.9 hours**.

**Where the €101k comes from:**

| Change | Today h/day | Design h/day | Saved h/day | Saved a year |
|---|---|---|---|---|
| Batch picking + slotting by demand (fast-pick area) | 23.8 | 11.7 | 12.1 | €62,846 |
| Three waves instead of one evening release (no 08:00 peak staffing) | 7.4 | 0 | 7.4 | €38,362 |
| **Total** | 31.1 | 11.7 | 19.4 | **€101,208** |

**If someone adds up the rounded numbers:** 23.8 + 7.4 looks like 31.2, and 12.1 + 7.4 like 19.5. The model uses exact hours: 23.77 + 7.37 = 31.14 today, and 12.07 + 7.37 = 19.44 saved. So 31.1 and 19.4 are right.

**Pickers needed:**
- **1.6 FTE** on an average day (11.7 h ÷ 7.5 productive hours).
- **2.9 FTE** on the peak day (lines × 1.83).

**Other numbers on your slides:**

| Number | How we got it | Type |
|---|---|---|
| 55% of orders arrive 15:00–17:00 | orders with an arrival time in the 15:00 or 16:00 hour ÷ all orders | measured |
| 1.31× at 08:00 | picks in the 08:00 hour ÷ the average picking hour | measured |
| 49.9% of lines on time | order lines the WMS did not flag "LATE" (definition to confirm with DHL, A005) | measured |
| 37% of orders within 24 h | trailer left − order received, per order (8,774 orders) | measured |
| p90 102 h | the slowest 10% of orders take 102 hours or more | measured |
| Racks full in ~4 months | stock grew 16% a quarter (Gleb's part) | model |
| 49% slotting match | WMS class = demand class for 48.6% of items | measured |
| 71% hit rate | 453 of ~634 lines a day are picked in the fast-pick area | model |
| 84% / 16% | orders up to 160 L and 60 kg (4 totes) count as small | measured, split by our rule |

---

## 6. What kind of operation this is (appendix 19)

**The four V's** (Slack et al., 2022):

| V | Measured | Level | What it means for the design |
|---|---|---|---|
| Volume | ~640 lines and ~144 orders a day | medium | repeatable tasks, so standard methods, scanning and batching pay off |
| Variety | 4,354 items shipped, 5,291 in stock; small parts to 2 m pallets; each, case and pallet picks | high | several storage types; pick by order size; no single machine fits all |
| Variation | busiest day 1.83× lines; 08:00 peak 1.31×; stock +16% a quarter | high (partly self-made) | level the self-made peak with waves; keep storage headroom |
| Visibility | customers see only the result (5% of lines are web orders) | low | efficiency can be designed in the back office, but the dispatch promise must be kept |

**So:** high variety at medium volume sits between a batch and a mass process. People with scanners, carton flow and a put-to-light wall fit better than full automation.

**What the operation must be good at** (our ranking):
1. **Dependability:** every order on the agreed trailer (order winner).
2. **Speed:** short time from order to trailer (order winner).
3. **Quality:** right item, right quantity, safe storage (qualifier).
4. **Cost:** low cost per order line (order winner when the contract is renewed).
5. **Flexibility:** cope with peaks and growth (qualifier).

Today the biggest gaps are dependability, speed and cost. All three come from **how work is released and picked**, not from a lack of space.

---

## 7. Risks and open points

| Open point | Why it matters | What we do |
|---|---|---|
| **Pick times are modelled** (yours on the open-points slide) | they set the staff per wave; labour is the biggest running cost | time study on the current floor; recalculate pickers per wave |
| DHL's real pick hours are not in the data | today's 31 h is a model, not a measurement | ask DHL for real hours (A006) |
| Real labour cost | €20 or €28 an hour changes the yearly cost by €86k | ask DHL for the real hourly cost |
| Carriers must accept fixed slots | the waves are planned back from the departures | Rachel agrees the slots with the carriers |
| Slotting goes stale | best-sellers change over time | re-slot every month from the demand data |

---

## 8. Questions you may get — and answers

**"Is the 31 hours measured?"**
- No, it's modelled. DHL's real pick hours were not in the data.
- We used the same formula and the same orders for today and the design, so the comparison is fair.
- We propose a time study to confirm it.

**"Where does the 25 seconds per line come from?"**
It's an assumption, written down in our register (A025), and the open-points slide plans a time study to measure it. The saving mainly comes from less walking, fewer tours and no peak staffing, so a different pick time changes both sides. Productivity ±20% changes the yearly cost by about €73k.

**"Why batch picking?"**
84% of orders are small and half have only one line. If every tour picks one order, the picker walks a long way for one or two lines. A batch tour picks about 31 lines for ~4 orders in one trip.

**"How does the put-to-light wall work?"**
- The picker scans an item, a light shows the slot of its order, and the picker puts it in and confirms (about 8 seconds).
- When an order is complete, its slot lights up for the packer.
- It only releases complete, correct orders, so it checks every item too.

**"Why 120 slots?"**
The busiest wave has about 73 small orders, each using 1.35 totes on average. Plus 20% spare: 73 × 1.35 × 1.2 ≈ 118, so 120.

**"How does the 08:00 peak disappear?"**
Today everything is released at once, so the first hours are overloaded and staff is planned for that. In the design, the WMS releases work in three fixed waves sized to the pickers we have. Each hour gets about the same amount of work, which removes the 7.4 h of peak staffing.

**"Why these wave times?"**
They are planned backwards from the trailer departures. Every wave ends at least 45 minutes before its trailers leave, so there is time to pack and stage. W3 takes the orders that arrived before noon, so they leave the same day.

**"What is largest-gap routing?"**
In each aisle the picker goes in from the nearest end and turns back at the biggest empty stretch between two picks, instead of walking the whole aisle. In our reserve aisles it gives the shortest walk: 471 m against 572 m for S-shape. It works because every aisle is open at both ends.

**"Why not pick-to-light or automation?"**
At ~640 lines a day, a light on thousands of pick faces costs too much for the time it saves. Full automation (option C) scored lower overall, costs much more and copes badly with items from small parts to 2 m pallets.

**"Why not a tugger train?"**
With batching there are only about 9 trolley trips a day. A driver would be busy 26% of the time to save pickers about 6 minutes of walking, because both pick zones end next to packing. It's an option if small orders roughly triple.

**"How many pickers do you need?"**
1.6 FTE on an average day and 2.9 on the busiest day. The busiest wave needs about 3 pickers. Cross-trained staff cover the peak days.

**"What happens when the volume grows?"**
In the stress test, pickers in the busiest wave go from 3 to 4 at 150% and 6 at 250%. Aisle congestion is not the limit; the outbound doors are, at 200% and more.

**"How do you guarantee accuracy?"**
Every pick is scanned, and the put-to-light wall checks each item again before an order is released. Our target is at least 99.7% of orders without error; the benchmark median is 99.3%.

**"How do you know which items are best-sellers?"**
From demand in the order data: the A and B items by quantity picked, which together make up 95% of everything picked (1,409 items). The WMS class agreed with real demand for only 48.6% of items, so we re-slot by demand and update it every month.

**"What are your 46 assumptions? Which matter most?"**
They're in data/assumptions.json, each with a reason, a source and an impact rating. The ones that matter most are the labour rate (€86k a year), the racking price (€83k), productivity (€73k) and the truck lease (€25k).

---

## 9. Where to find it

| Topic | Where |
|---|---|
| Order and picking profile | D1 §6 |
| Demand ABC (best-sellers) | D1 §8 |
| Picking process flow | D2 §2.3 |
| Peaks, 08:00 peak | D1 §9, D2 §4.2 |
| Four V's, performance objectives, alignment | D1 §11 |
| Labour per process | D2 §6.1 |
| Picking model, equipment, routing, hardware | D2 §6.2 |
| Waves, loading, sequencing, control | D2 §7.3, §7.5 |
| KPIs | D3 §2 |
| Where the saving comes from | D3 §2.2 |
| Stress test | D3 §2.4 |
| A pick face for every best-seller | D3 §4.3 |
| Put-to-light wall: where and how | D2 §2.4, D3 §5.1 |
| Slides | deck slides 3, 4 and 8; appendix "How we calculated: picking", "Operation profile", "KPI scorecard", "Planning and control" |

---

## 10. Cheat sheet — numbers to know by heart

| | |
|---|---|
| Orders / lines a day | **~144 / ~640** (busiest day 1,171 lines = 1.83×) |
| Single-line orders | **50.5%** |
| Pick type (lines) | **75% each** · 24% case · 1% pallet |
| Orders arriving 15:00–17:00 | **55%** → 08:00 peak **1.31×** |
| Small / large orders | **84% / 16%** (large = 88% of volume) |
| Best-sellers in the fast-pick area | **1,409** → **71%** of lines |
| Trolley tour | ~**31 lines**, ~4.4 orders, closed at 80% full |
| Put-to-light wall | **120 slots** |
| Waves | **06:00 · 09:30 · 12:45** |
| Picker-hours a day | **31.1 → 11.7** (−19.4 h) |
| Saving | **€101k a year** (€63k batching + €38k waves) |
| Pick rate | **~54 lines/h** · fast-pick 99 · reserve 49 · large orders 44 |
| Pickers | **1.6 FTE** average · 2.9 peak |
| Assumptions | **46** · biggest: labour €20 vs €28 = **€86k** a year |

---

## 11. Glossary — the words in plain language

### Picking words

| Word | What it means |
|---|---|
| Each / case / pallet pick | each = single pieces (less than a full box); case = full boxes; pallet = a whole pallet |
| Single-line order | an order with only one order line |
| Tour | one trip of a picker: start, all pick places, back to packing |
| Batch picking | one tour picks lines for several orders at once; they are sorted into orders afterwards |
| Trolley and tote | a cart with 3 shelves and 6 plastic boxes (totes) of about 40 litres each |
| Pick face | the place where a picker takes an item |
| Carton flow | sloped roller shelves: cases are loaded from the back and roll forward to the picker at the front |
| Slotting | deciding which item goes in which place; "by demand" = best-sellers in the best places |
| ABC classification | A = the items that make up 80% of the picked quantity, B = the next 15%, C = the last 5% |
| Hit rate | the share of all picked lines that come from the fast-pick area |
| Pick rate | order lines picked per picker-hour |
| Routing | the path a picker walks through the aisles: return, S-shape, midpoint or largest gap (section 4.5) |
| Order release | the moment the WMS gives orders to the floor to be picked |
| Refill (replenishment) | the reach truck topping up a pick face from the reserve |
| RF scanner | a handheld scanner linked to the WMS by radio; every pick is scanned |
| Pick-to-light / voice picking | lights on each pick face / a headset that tells the picker what to pick |
| Tugger train | a small tractor that pulls carts in a loop; we looked at it and did not choose it |
| Time study | measuring real working times on the floor, e.g. seconds per pick |
| Pick accuracy | the share of orders picked without any error |
| Order winner / qualifier | order winner = what makes the customer choose you; qualifier = what you must have to be considered at all |

### General words (the same in all four briefings)

| Word | What it means |
|---|---|
| WMS | the warehouse management system: the computer system that knows where every pallet is and tells people what to do. Almost all our data comes from it |
| Item (SKU) | one specific product, e.g. one type of lock. There are 5,291 in stock |
| Load | one pallet (or other carrier) of stock with its own number in the WMS |
| Order / order line | an order is what one customer asks for; each different item on it is one order line |
| Average vs median | the average adds everything up and divides; the median is the middle value (half are lower, half higher), so a few extreme values don't pull it up |
| p90 / p95 | the value that 90% (or 95%) of cases stay under. "The slowest 10%" means everything above p90 |
| 1.83× (peak factor) | the busiest day divided by an average day |
| FTE | full-time equivalent: one person working a full day (7.5 productive hours out of 8 paid) |
| Picker-hours | hours of picking work in a day; 11.7 picker-hours is about 1.6 people |
| KPI | key performance indicator: a number we track to see if the operation works as planned |
| Measured / modelled / assumption / benchmark / target | measured = straight from Assa Abloy's data; modelled = our calculation on that data; assumption = a value we chose and wrote down with its reason; benchmark = a typical value from a public source; target = what the design is built to reach |
| Assumption register | our list of 46 assumptions (data/assumptions.json), each with its reason, source and impact |
| Option A / B / C | the three designs we compared: A = today's way tidied up; B = hybrid (chosen); C = semi-automated |
| Four V's | volume, variety, variation and visibility: four ways to describe an operation (Slack et al., 2022) |
| Fast-pick area | the zone along the south wall where the 1,409 best-sellers each have a pick face, close to packing |
| Reserve (pallet racks) | the high racks where full pallets are stored until they are needed |
| Single-deep rack | a rack with one pallet behind each face, so every pallet can be taken out without moving another |
| Wave | a portion of the day's orders released to the floor together; we use 3 a day |
| Put-to-light wall | a wall of 120 slots with lights at packing; it sorts batch-picked items into their orders |
| Staging lane | floor area in front of a shipping door where goods wait for their trailer |
| R1–R3 / S1–S5 | the receiving doors (west wall) / the shipping doors (east wall) |
| ETV 216i | Jungheinrich reach truck: puts pallets away in the racks (lifts up to 10.7 m) and refills the fast-pick area |
| EJE 120i | Jungheinrich walkie pallet truck (the operator walks with it): used to pick large orders onto a pallet |
| ERE 225 | Jungheinrich rider pallet truck (the operator stands on it): used to unload and load trailers |
| CAPEX | one-off investment: racks, equipment, set-up |
| OPEX | running cost every year: staff, truck lease, energy, upkeep |
| Depreciation | the investment spread over the years it lasts (racks 15 years, equipment 7, IT 5) |
| Payback | how many years of savings it takes to earn back an investment |
| Sensitivity | how much the result changes if an assumption is wrong (e.g. labour at €28 instead of €20 an hour) |
| Stress test | checking the design at 150%, 200% and 250% of today's volume |
