# DATA DICTIONARY — ASSA ABLOY @ DHL Bemmel (NL_0032)

Primary source of truth: raw files in `data/raw/`. Two datasets.
All figures below are measured from the actual files (see `outputs/reports/phase0_metrics.json`).

- **Warehouse:** `NL_0032` (DHL Supply Chain, Bemmel)
- **Client:** `CID003739NL` (Assa Abloy)
- **Period covered:** 01 Apr 2025 – 30 Jun 2025 (Q2 2025)

---

## DATASET A — STORAGE / INVENTORY SNAPSHOTS

Three month-start snapshots: `01-04-2025`, `01-05-2025`, `01-06-2025`.
**Grain:** one row = one inventory **detail record** (`DTLNUM`, unique) = a quantity of a
`PART` on a load (`LODNUM`) at a `LOCATION` on the snapshot `DATE`.
Row counts: 16,575 / 16,793 / 17,290. Header sits on the **2nd row** (title banner above it).

| Variable | Meaning | Unit | Time period | How it will be used |
|---|---|---|---|---|
| DATE | Snapshot date | date | 1st of month | Time key; inventory trend across 3 months |
| WAREHOUSE | Facility code (NL_0032) | code | — | Scope confirm |
| CLIENT | Client id (CID003739NL) | code | — | Scope confirm |
| AREA | Functional area (STGAREA, STGL, PACK, PND, RCVL, HOP, SHIP) | category | snapshot | Space/zone reconstruction of current state |
| AISLE | Aisle number | code | snapshot | Current layout reconstruction; travel proxy |
| STORAGE ZONE ID / CODE | Storage zone (e.g. HI-RA-SZ-D) | code | snapshot | Zoning analysis |
| PICK ZONE ID / CODE | Pick zone (e.g. HI-RA-PZ-D) | code | snapshot | Picking zone analysis |
| DTLNUM | Inventory detail id (unique) | id | snapshot | Record key; count of inventory details |
| SUBNUM / LODNUM | Sub-load / load (license plate) id | id | snapshot | **Pallet/load counting** → storage positions |
| LOCATION | Physical location id (e.g. 062-059-C) | code | snapshot | Occupied-location count; current capacity |
| LOC TYPE | RACK, S_STAGING, SF_STAGING, PACK, PND, SHIP … | category | snapshot | Separate storage vs staging vs pack/ship |
| LOC CATEGORY / VELOCITY | Location class / velocity band | category | snapshot | Current slotting logic |
| LOC LENGTH / HEIGHT / WIDTH | Location envelope | cm | snapshot | Rack geometry, usable height check |
| PART | SKU / article number | id | snapshot | **SKU master key** |
| PART FAMILY | Product family (numeric code) | code | snapshot | Family grouping / slotting |
| COMPONENT CODE | HS/commodity-style code | code | snapshot | Grouping, hazard/trade context |
| PART FIT / STYLE | Product attributes | category | snapshot | Family/affinity grouping |
| HAZMAT | Hazardous flag | 0/1/code | snapshot | Safety & segregation requirements |
| UOM | Base unit of measure (EA) | code | snapshot | Unit normalisation |
| PART VELOCITY | Movement class (letter) | category | snapshot | Cross-check vs demand-derived ABC |
| PART ABCCOD | ABC class held in WMS (A/B/C) | category | snapshot | Compare to our recomputed ABC |
| FOOT PRINT | Footprint/storage template code | code | snapshot | Storage-type mapping |
| ORGCOD | Origin country | code | snapshot | Inbound origin context |
| LOTNUM / FIF DATE / ADD DATE | Lot, FIFO date, date added to stock | date | snapshot | Age of stock; FIFO/FEFO; inbound proxy |
| INVSTS | Inventory status | code | snapshot | Available vs held/blocked stock |
| QTY | On-hand quantity (base UOM/eaches) | eaches | snapshot | Inventory volume, cube, ABC by qty |
| PA QTY | Units per pallet | eaches/pallet | snapshot | **Eaches→pallets conversion** |
| PA LEN / HGT / WID | Pallet dimensions | cm | snapshot | Pallet cube, rack level height |
| PA WGT | Pallet weight | kg | snapshot | Rack load limits, MHE capacity |
| CS QTY / LEN / HGT / WID / WGT | Case pack + case dims/weight | mixed | snapshot | Case picking, carton flow sizing |
| EA LEN / HGT / WID / WGT | Each dimensions + weight | cm / kg | snapshot | Each-pick sizing, forward-pick slotting |
| RECEIVE KEY / INBOUND TRUCK NO | Inbound receipt reference | id | snapshot | **Receiving proxy** (no separate inbound file) |
| ASSET TYPE | Pallet/carrier type (EURO, K3, XLONGPALLET, K1/2/5, CONS) | category | snapshot | Pallet-type mix → rack/opening design |

**Measured highlights (latest snapshot 01-06-2025):** LOC TYPE RACK = 15,890 of 17,290;
ABCCOD C=10,346 / A=3,816 / B=3,128; ASSET TYPE EURO=11,140, K3=4,318, XLONGPALLET=339.

---

## DATASET B — OUTBOUND / SHIPPING + PICKING TRANSACTIONS

Three monthly files: `202504`, `202505`, `202506`.
**Grain:** one row = one **order line** picked and shipped.
Row counts: 12,868 / 13,061 / 13,140 → **39,069 order lines**, 8,781 orders, 4,354 parts, 61 ship-days.

| Variable | Meaning | Unit | How it will be used |
|---|---|---|---|
| DATE | Ship/close date bucket | date | Daily throughput, peak analysis |
| TRAILER ID / ARRIVE / CLOSE / DISPATCED DATE | Outbound trailer + milestones | id/datetime | Dock/shipping throughput, trailer counts |
| ORDER ARRIVE DATE | Order received into WMS | datetime | Order inflow; lead-time start |
| CALC / EARLY / LATE SHIP DATE | Planned & SLA ship window | datetime | **Service level / on-time** analysis |
| ALOCATE DATE | Stock allocation time | datetime | Process timing |
| PICK DATE | Pick completion time | datetime | Picking throughput, pick lead time, peak hour |
| STAGED DATE / STATUS | Staged time + OK/LATE flag | datetime/flag | **On-time staging KPI** (LATE = 50.1%) |
| CARRIER CODE / NAME | Carrier | code | Outbound profile, dock assignment |
| SHIPMENT ID | Shipment grouping | id | Consolidation, cartons/pallets per shipment |
| SERVICE LVL | Service level code | code | Service segmentation (SLA to confirm) |
| SHIP TO NAME/ADDRESS/CITY/POSTAL/COUNTRY | Destination | text | Customer/geo profile, order affinity |
| ORDER TYPE | Order category (AMADE, NLD …) | code | Channel mix (e.g. Amazon vs distribution) |
| ORDER NO / LINE | Order + line number | id | Order & line counts, lines/order |
| UNIT PRICE | Line unit price | currency | Value profile (not a cost input) |
| PRTNUM | SKU shipped | id | Join to storage PART; demand by SKU |
| PICKED QTY | Units picked on the line | eaches | Demand volume, units/line, pick effort |
| PALL/LIST/TROLLEY FLAG·LINES·LIFTS | Pick method + workload counters | count | **Picking method mix & lifts** (labour driver) |
| SHIPMENT PACKED CARTONS/PALLETS | Cartons & pallets packed | count | Pack & outbound pallet volume |
| SHIPMENT STAGED PALLETS | Pallets staged | count | Outbound staging space |
| RE-LABEL | Re-label flag | 0/1 | Rework indicator |
| CPOTYP | Customer PO type | code | Order-type nuance |

**Always-empty columns (both datasets’ irrelevant fields):** `APP START DATE`, `SERVICE LVL NAME`
(100% null in outbound); `LOC ABCCOD`, `PART COLOR/SIZE`, `SUP LOTNUM`, `MAN DATE`, `EXPIRE DATE`,
`SUPNUM`, `CUSTOMES TYPE` (≈100% null in storage). These are dropped from analysis.
