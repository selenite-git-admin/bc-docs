---
title: BCF C3-C6 Routing-First Projection (2026-06-25)
description: Read-only projection using the Session 2 coverage compiler (rule pack v1.0 — validated at 71.5% BC-weighted agreement on C1+C2). No panels, no writes, no substrate mutations. Per-cluster routing decisions for the 131 remaining Pass-1 rows (58 C3 identifiers + 31 C4 amounts/rates + 8 C5 quantities + 34 C6 text/descriptor) with BC-coverage gain per expected panel call, slice-blocked breakdown by missing entity slice, and avoidable-panel-risk warnings. Includes recommendation: next executing cluster + Pass 2 forward-bring assessment.
status: projection
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-c3-c6-projection
related_docs:
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
  - bcf-bc-coverage-ledger.json
  - bcf-bc-coverage-ledger-view-2026-06-25.md
  - bcf-coverage-compiler-validation-2026-06-25.md
  - bcf-oagis-pass-1-c1-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-1-c2-closure-checkpoint-2026-06-25.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
---

# BCF C3-C6 Routing-First Projection

> Companion to the Session 2 coverage compiler (calibrated at 71.5% BC-weighted agreement vs ledger on C1+C2). Read-only projection of the 131 remaining Pass-1 rows under the same rule pack. **No panels, no writes, no substrate mutations performed.**

## 1. Headline

| Cluster | Rows | BC targets | Expected panels | Expected BC gain | BC-gain per panel | Slice-blocked BC | Rejected BC |
|---|---:|---:|---:|---:|---:|---:|---:|
| **C3** identifiers | 58 | 150 | 24 | 114 | **4.75** | 36 | 0 |
| **C4** amounts/rates | 31 | 79 | 19 | 54 | **2.84** | 12 | 13 (bare `amount`) |
| **C5** quantities | 8 | 26 | 4 | 22 | **5.50** | 3 | 1 (bare `measure`) |
| **C6** text/descriptor | 34 | 61 | 4 | 18 | **4.50** | 43 | 0 |
| **C3-C6 total** | **131** | **316** | **51** | **208** | **4.08** | **94** | **14** |

Total Pass-1 catalogue across all 6 clusters: 217 rows / 572 BC targets (40+46+58+31+8+34 = 217; 147+109+150+79+26+61 = 572). C1+C2 addressed so far: 17 substrate writes covering ~119 BC. C3-C6 projected to add up to **208 BC** of additional addressed coverage via 51 expected panel calls — bringing program addressable to ~327/572 BC = **57%** of the full Pass-1 catalogue under current substrate.

## 2. Ranking by BC-coverage-gain per expected panel call

| Rank | Cluster | Panels | Gain | BC-gain/panel | Notes |
|---:|---|---:|---:|---:|---|
| 1 | **C5** | 4 | 22 | 5.50 | Small high-confidence batch — weight/measure variants, mostly existing-finance + logistics target slices |
| 2 | **C3** | 24 | 114 | 4.75 | Large batch — highest absolute gain but ~30% panel risk (7 narrow-scope warnings); also includes `gl_entity_identifier` (BC=13, top BC weight in cluster) |
| 3 | **C6** | 4 | 18 | 4.50 | Small batch — text/descriptor rows mostly slice-blocked (70.5% of cluster BC) |
| 4 | **C4** | 19 | 54 | 2.84 | Large batch with heavy panel-risk dilution (13 of 19 panels are BC≤2 single-slice — likely Checker-park) |

## 3. Per-cluster detail

### C3 — identifiers (58 rows / 150 BC)

| Route | Rows | BC | % cluster BC |
|---|---:|---:|---:|
| `new_substrate_characteristic` | 24 | 100 | 66.7% |
| `operator_semantic_decision_slice_blocked` | 30 | 36 | 24.0% |
| `map_to_existing_characteristic` | 4 | 14 | 9.3% |

**Map-to-existing (compiler-detected siblings):**
- `ledger_identifier` → `ledger account identifier` (substrate synonym; rule extended this session)
- 3 others via substring-after-strip matching

**Slice-blocked by missing entity slice:**
| Missing slice | Rows | BC |
|---|---:|---:|
| `master-data` | 8 | 10 |
| `asset-maintenance-simple` | 7 | 8 |
| `quality-composite` | 5 | 7 |
| `logistics` | 5 | 6 |
| `production-simple` | 3 | 4 |
| others (master-data-root / reference-warranty-budget / production-composite / quality-simple) | 4 | 5 |

**Avoidable-panel-risk (7 rows / 11 BC):** `dock_identifier`, `tracking_identifier`, `pro_number_identifier`, `ship_unit_sequence_identifier`, `ship_unit_total_identifier`, `freight_charge_account_number_identifier`, `bill_of_lading_identifier` — all BC≤2 + single existing-finance slice. Per C1+C2 calibration, these will likely Checker-park unless paired with multi-source standards anchors (UN/EDIFACT shipment-identifier conventions, ISO container codes, etc.) at packet-prep time. Recommend operator pre-review of this subset before transport.

### C4 — amounts/rates (31 rows / 79 BC)

| Route | Rows | BC | % cluster BC |
|---|---:|---:|---:|
| `new_substrate_characteristic` | 19 | 51 | 64.6% |
| **`reject_circular_or_generic`** | **1** | **13** | **16.5%** |
| `operator_semantic_decision_slice_blocked` | 8 | 12 | 15.2% |
| `map_to_existing_characteristic` | 3 | 3 | 3.8% |

**Critical: bare `amount` rejected — 13 BC stuck behind an operator decision.** Same pattern as `type_code` in C1 (61 BC, smaller magnitude). Operator must decide: admit a Global `amount` parent characteristic with role qualifiers, or require each amount variant to carry its own substantive head noun. Until resolved, those 13 BCs (across asset-maintenance-simple, existing-finance, logistics, master-data, reference-warranty-budget) have no governed route.

**Avoidable-panel-risk (13 of 19 panels):** `total_charge_amount`, `total_allowance_amount`, `declared_value_amount`, `receiving_service_charge_amount`, `open_item_amount`, `order_amount`, `approved_order_amount`, `available_amount`, `order_limit_amount`, `total_credit_limit_amount`, `estimated_freight_charge_amount`, `freight_cost_amount`, `sale_price_amount`, `shipment_total_amount`. All BC≤2 + single existing-finance slice. **This is 68% of the C4 panel pool** — projecting 2-5 substrate writes from 19 panels at the C1+C2 rate. Strong recommendation: operator pre-review with consolidation to fewer broader concepts before transport.

### C5 — quantity/measure (8 rows / 26 BC)

| Route | Rows | BC | % cluster BC |
|---|---:|---:|---:|
| `new_substrate_characteristic` | 4 | 22 | 84.6% |
| `operator_semantic_decision_slice_blocked` | 3 | 3 | 11.5% |
| `reject_circular_or_generic` | 1 | 1 | 3.8% |

The smallest cluster. 4 panel-ready rows: `dunnage_weight_measure` (BC=7), `tare_weight_measure` (BC=7), `estimated_weight_measure` (BC=4), `loading_weight_measure` (BC=4). All target existing-finance + logistics slices. Standards anchors are available (UN/CEFACT TDED for weight measurements, ISO container weight codes). Bare `measure` correctly rejected.

### C6 — text/descriptor (34 rows / 61 BC)

| Route | Rows | BC | % cluster BC |
|---|---:|---:|---:|
| **`operator_semantic_decision_slice_blocked`** | **28** | **43** | **70.5%** |
| `new_substrate_characteristic` | 4 | 14 | 23.0% |
| `map_to_existing_characteristic` | 2 | 4 | 6.6% |

**Heavily slice-blocked.** 70.5% of cluster BC is locked behind Pass 2 entity admissions. Only 4 rows actually panel-eligible right now (`shipping_instructions`, `inco_terms_place_name`, `special_handling_note`, `general_ledger_nominal_account` — though latter two have avoidable-panel-risk).

**Map-to-existing:** `lead_time_duration` → `lead time` (this session's rule extension); `short_name` → `description` (via substring-after-strip).

## 4. Pass-2 forward-bring assessment

The cumulative slice-blocked count across C3-C6 (94 BC) plus C1+C2 residuals (~29 BC slice-blocked per ledger) means **~123 BC of Pass-1 work is gated on Pass-2 entity admissions**. The most-blocking missing slices, ranked by Pass-1 BC unlock potential:

| Missing slice | C1+C2 slice-blocked BC (from ledger) | C3-C6 slice-blocked BC (projected) | Total BC unlock | Entities to admit (per A0.5 §5) | Class |
|---|---:|---:|---:|---|---|
| `asset-maintenance-simple` | small | 34 | ~34+ | Asset, Equipment, Maintenance Order | all AMBER |
| `master-data` | small | 22 | ~22+ | Business Partner, Cost Centre, Location, Org Unit, Party, Price List, Price List Item, Project | all AMBER |
| `master-data-root` | small | 17 | ~17+ | Item | AMBER (single entity) |
| `production-simple` | minor | 12 | ~12+ | BOM, Manufacturing Process, Production Confirmation, Production Schedule, Routing, Work Centre, Work Order | all AMBER |
| `logistics` | minor | 11 | ~11+ | Delivery, Pick List, Pick List Line, Shipment Request, Shipment Unit, Three-Way Match Document, Three-Way Match Document Line | all AMBER |
| `quality-composite` | minor | 10 | ~10+ | Inspection Lot, Test Result | all-RED (composite-identity packets) |
| `production-composite` | minor | 9 | ~9+ | BOM Line, Operation, Work Order Operation | all-RED |
| `quality-simple` | minor | 9 | ~9+ | Certificate, Corrective Action, Nonconformance, Test Method | all AMBER |
| `maintenance-composite` | — | 6 | ~6+ | Maintenance Order Operation | RED |

**Highest-value, lowest-friction Pass-2 admissions:**
1. **`master-data-root` / Item** — single AMBER entity, ~17 BC unlock. Best per-entity value.
2. **`asset-maintenance-simple` / Asset + Equipment + Maintenance Order** — 3 AMBER entities, ~34 BC unlock. ~11 BC per entity.
3. **`master-data` / 8 AMBER entities** — ~22 BC unlock. ~3 BC per entity (lower per-entity value but unlocks many master-data rows).

**Friction-locked unlocks:** quality-composite (10 BC), production-composite (9 BC), maintenance-composite (6 BC) each require RED composite-identity packets per A0.5 §7 — operator-decision-packets per entity, not panel-admissible. 25 BC of Pass-1 work is gated on those.

## 5. Recommendation

Three options, ranked by expected operator time + cost + value:

### Option A (recommended) — Execute C5 first; bring Pass 2 forward; then C3 + C4 + C6 retrofitted

1. **Execute C5 now** (4 panels, 22 BC, ~10-15 min wall-clock).  
   Clean low-cost win. All targets in existing-finance + logistics slices. Multi-source standards anchors available.

2. **Then bring Pass 2 forward** — admit the AMBER entity slices in priority order:
   - Item (master-data-root) → unlocks 17 BC
   - Asset, Equipment, Maintenance Order (asset-maintenance-simple) → unlocks 34 BC
   - Master-data 8 AMBER entities → unlocks 22 BC
   
   These three admissions together unlock ~73 BC of C3-C6 slice-blocked rows, plus carry-forward unlocks for C1+C2 residuals.

3. **Then return to C3 + C4 + C6** with retrofitted slice availability + the C2 Checker-First Preflight discipline:
   - C3 with Pass-2 slices: an additional 25 BC routable (~13 rows that were slice-blocked become map_to_existing or new_substrate)
   - C4 with operator decision on bare `amount` + pre-transport consolidation of the 13 narrow-risk rows: ~30-45 BC gain depending on consolidation aggressiveness
   - C6 with Pass-2 slices: an additional 35-40 BC routable (28 currently-blocked rows reopened)

**Total under Option A**: ~22 (C5) + 73 (Pass 2 unlock) + 25-45 (C3 post-unlock) + 30-45 (C4 with consolidation) + 35-40 (C6 post-unlock) ≈ **185-225 BC across 5-7 operator-attended sessions** vs the naive serial C3→C4→C5→C6 which would yield 208 BC across 4 sessions but leave ~94 BC slice-blocked indefinitely until Pass 2.

### Option B — Stay in Pass 1; execute C5 → C3 → C6 → C4 in BC-gain-per-panel order

Total 208 BC of addressable coverage now; ~51 panel calls. Leaves 94 BC slice-blocked indefinitely until Pass 2 happens later. C4 in particular wastes ~13 panels on the avoidable-risk subset.

### Option C — Defer all Pass-1 cluster execution; do Pass 2 first

Skip C3-C6 entirely until Pass-2 entities are admitted. Then a single retrofit pass over all 131 rows could route up to ~300 BC under the now-larger slice availability. Drawbacks: ignores the 208 BC currently addressable; defers all C3-C6 substrate to weeks/months out; doesn't capture quick wins like C5.

### Strongest case for Option A

Two reasons:
1. **C5 is the cheapest quick win** in the entire program (5.50 BC-gain-per-panel — better than any C1+C2 session). 4 panels, ~10 min wall-clock, high standards-anchor density.
2. **Pass-2 unlock multiplier** — admitting 4 high-impact AMBER entities (Item + Asset + Equipment + Maintenance Order) unlocks ~50 BC of C3-C6 work AND retrofits a substantial fraction of C1+C2 residuals. This is the highest BC-per-operator-decision lever available in the entire Pass-1 program after `type_code` (61 BC) and bare `amount` (13 BC).

**Open operator questions (Pass-2 entry preparation):**

- Confirm Pass-2 entry — does DEC-f94895 program authorization extend to it, or does Pass 2 require its own A1-A5 authorization?
- Confirm priority order — Item first (single entity, 17 BC) or asset-maintenance-simple first (3 entities, 34 BC)?
- Confirm panel-vs-direct-author for entities — entities go through F4-v2 too, or a different surface?
- The RED composite-identity packets (Bill of Materials Line, Inspection Lot, Inventory Position, Maintenance Order Operation, Operation, Test Result, Work Order Operation) are out-of-scope for Option A's Pass-2 admission wave. They remain held until separate operator decision packets are authored.

## 6. Compiler caveats

- **`gl_entity_identifier` correctly routes to new_substrate** (BC=13, 5 slices) but does NOT hit the high-impact-root threshold (≥50 BC). The compiler's threshold was calibrated against `type_code` (61 BC). `gl_entity_identifier` is a substantial cross-finance concept worth careful operator framing — its admission as Global vs role-qualified at BC binding will set precedent for many other identifier rows.
- **C4 bare `amount` (BC=13) correctly rejected** as bare-rep-term per the rule pack, surfacing the operator decision similar to `type_code`.
- **`uid` and `glnid` (C3, identifier|string|descriptor)** route to slice-blocked. The shape pattern (descriptor, not identifier) suggests these may be system-narrow rather than business identifiers — operator should confirm.
- **Compiler-routed map_to_existing is conservative.** Only 9 of 131 C3-C6 rows mapped to existing substrate (4 C3 + 3 C4 + 0 C5 + 2 C6). Real substrate matches may exist that the compiler missed via substring-after-strip heuristic; a panel run would surface them as Checker rejections (the C2 Trap 7 pattern). The 13-row avoidable-panel-risk subset in C4 is the most likely subset to surface this.

## 7. Discipline state

- 0 panel calls performed.
- 0 C5 confirms performed.
- 0 substrate writes performed.
- 0 transport scripts run.
- 0 DDL changes.
- 0 changes to BC-coverage ledger (used as oracle only).
- 0 changes to A0.5 (read fresh from bc-docs-v3 SSOT).
- Substrate verified unchanged at session-start state: 26 active entities / 62 active characteristics / 18 draft characteristics / 194 active value BCs.
- Branch: `bcf-c3-c6-projection-2026-06-25` (off `bcf-coverage-compiler-2026-06-25`). PR opened, NOT merged.

**No panels / no writes performed.**

## 8. Files

- `barecount-devhub/scripts/_bcf-coverage-compiler.mjs` — compiler extended with C3-C6 A0.5 inventory + projection mode + 2 known-mapping extensions.
- `barecount-devhub/.claude/bcf-coverage-compiler/projection-c3-c6.json` — machine-readable projection (per-cluster aggregates + per-row routing).
- `barecount-devhub/.claude/bcf-coverage-compiler/projection-c3-c6.md` — machine-generated projection report (this doc consolidates + adds recommendation).

## 9. Next-session shape (when operator authorizes)

If Option A: separate session for C5 execution (small focused batch, transport + confirm + closeout), THEN separate session for Pass-2 Item admission planning, THEN separate sessions per entity admission wave.

If Option B: serial sessions per cluster in ranked order.

If Option C: pivot directly to Pass-2 entry planning.

Held. Awaiting operator decision on A / B / C.
