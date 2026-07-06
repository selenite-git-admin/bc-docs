---
title: BCF × OAGIS Pass-1 Retrofit Scoping Ledger (2026-06-25)
description: Read-only per-row decision ledger for Pass-1 rows newly unblocked by E1 (Item) + E2 (Asset, Maintenance Order). 20 rows / 34 BC newly eligible; 0 source from `equipment-master` OAGIS noun; 0 have direct map-to-existing siblings in active substrate; 1 row (`asset_type`) flagged as soft-trigger for Equipment-aware operator review. Output is a ranked candidate ledger and a first-retrofit-batch recommendation (5 item-master Item-bound text/descriptor rows with multi-source standards anchors). No transport, no panels, no substrate writes.
status: held_operator_gate
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-retrofit-scoping
related_docs:
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
  - bcf-bc-coverage-ledger.json
  - bcf-c3-c6-projection-2026-06-25.md
  - bcf-oagis-pass-2-e1-item-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-2-e2-asset-maintenance-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-2-e2-equipment-operator-decision-packet-2026-06-25.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
---

# BCF × OAGIS Pass-1 Retrofit Scoping Ledger

> Operator scope 2026-06-25: "Scope the retrofit candidates first, no transport and no panels. Produce a small decision ledger, not packets yet. The session should first tell us which rows are deterministic bindings / map-to-existing, which need new BC authoring, and which still hit Equipment or another missing entity. Then we pick the smallest high-confidence batch."

> No transport. No panel calls. No substrate writes.

> Key distinction enforced: "newly eligible ≠ transport-ready."

## 1. Headline

| Metric | Value |
|---|---:|
| Newly-unblocked rows post-E1/E2 | **20** |
| Total BC newly eligible | **34** |
| Rows binding to Item (master-data-root) | 8 / 17 BC |
| Rows binding to Maintenance Order | 10 / 14 BC |
| Rows binding to Asset | 2 / 3 BC |
| Rows binding to BOM (production-composite — held) | 1 / 3 BC (alt-route via master-data-root available) |
| Rows sourcing from `equipment-master` OAGIS noun | **0** |
| Rows with direct map-to-existing sibling in active substrate | **0** |
| Rows flagged as soft-trigger for Equipment-aware review | **1** (`asset_type`) |

**Three-bucket classification per operator scope:**

| Bucket | Count | BC | Posture |
|---|---:|---:|---|
| **I. Deterministic / map-to-existing** (no panel needed) | 0 | 0 | None — all 20 candidate rows need new BC authoring |
| **II. New BC authoring** (panel needed) | 19 | 31 | Standard Pass-1 panel path under Checker-First Preflight |
| **III. Hits missing entity** (held / trigger) | 1 | 3 | `asset_type` flagged but NOT held — see §5 |

Recommended first retrofit batch: **5 item-master rows / 10 BC** — single entity (Item), single OAGIS source path (`item-master.item-master.*`), multi-source standards anchors available (GS1, ISO 22000, ISO/IEC 15459, GS1 lot/batch, FDA traceability). See §6.

## 2. Inputs read

- `bcf-oagis-a0.5-template-catalogue-2026-06-24.md` (per-row OAGIS source path, target slice, AMBER/RED class)
- `bcf-bc-coverage-ledger.json` `.records[]` (Pass-1 C1+C2 coverage oracle — 86 records, used to verify no asset-maintenance-simple row was Equipment-specific)
- `barecount-devhub bcf-c3-c6-projection-2026-06-25` branch — `projection-c3-c6.json` `.compiled_rows[]` (131 rows / per-row routing decisions / target_slices / triage / compiler_reason)
- Live substrate via `GET /api/bcf/registry/characteristics?limit=200&includeAllStates=true` — 82 characteristics (62 active + 20 draft); used for substrate-sibling check
- Live substrate via `GET /api/bcf/registry/entities?limit=200&includeAllStates=true` — 29 active entities (Item / Asset / Maintenance Order admitted; Equipment held per PR #65)

## 3. Equipment dependency screen (per operator scope)

| Question | Answer | Source |
|---|---|---|
| Does any candidate row name Equipment in its OAGIS source path? | **No.** 20 source paths checked: 7 from `item-master.item-master.*`, 10 from `maintenance-order.maintenance-order-header.*`, 2 from `asset.asset.*`, 1 from `bom.bom-item-data.*`. None from `equipment-master.*`. | A0.5 + projection per_row |
| Does any candidate row's binding require Equipment as the target entity? | **No.** Item, MO, and Asset are admitted; rows bind to one of those three. The `bom` row routes to Item via the master-data-root slice (alt slice) since `production-composite` (parent) is held. | A0.5 target_slices |
| Does any candidate row force the Equipment decision packet to reopen? | **One soft-trigger: `asset_type`.** Authoring `asset_type` as a characteristic does NOT lock Option A vs B (the values it admits at runtime do); but operator may want to defer authoring until Equipment is decided to avoid setting precedent. See §5. | §5 |

**Net Equipment screen:** 0 hard triggers; 1 soft-trigger; 19 rows are Equipment-independent and can proceed under any Equipment decision.

## 4. Per-row decision ledger

Columns per operator scope:
- **Target entity** — the active entity the row would bind to under current substrate
- **BC need** — the characteristic family the new BC requires; whether it exists in substrate
- **Route type** — the projection's compiler route; updated for post-E1/E2 substrate where the slice was missing then but is available now
- **BC gain** — `used_by_bc_target_count` from the projection
- **Panel needed?** — Yes if new substrate characteristic; No only if direct map-to-existing
- **Equipment dep?** — Y / N / soft-trigger
- **Confidence** — H / M / L based on (single entity ✓ + single source path ✓ + standards anchor available)

### 4.1 Item-master sourced — 8 rows / 17 BC

| # | bf_name | Shape | Target entity | BC need (substrate sibling?) | Route type | BC gain | Panel? | Eq dep? | Conf |
|---:|---|---|---|---|---|---:|---|---|---|
| 1 | `uom_group_identifier` | identifier\|string\|identifier | Item | No "uom group identifier" sibling; closest substrate root: none (unit identifiers exist in OAGIS extract as `unit-of-measure-code` shape, not group-id shape) | new_substrate_characteristic | 2 | Yes | N | M |
| 2 | `product_name` | text\|string\|descriptor | Item | No "product name" sibling; substrate has generic `description` only | new_substrate_characteristic | 2 | Yes | N | **H** |
| 3 | `brand_name` | text\|string\|descriptor | Item | No "brand name" sibling | new_substrate_characteristic | 2 | Yes | N | **H** |
| 4 | `variety_name` | text\|string\|descriptor | Item | No "variety name" sibling | new_substrate_characteristic | 2 | Yes | N | M |
| 5 | `serial_number_specification_description` | text\|string\|descriptor | Item | No sibling; ISO/IEC 15459 standards anchor | new_substrate_characteristic | 2 | Yes | N | **H** |
| 6 | `lot_number_specification` | text\|string\|descriptor | Item | No sibling; GS1 lot/batch + FDA traceability standards anchor | new_substrate_characteristic | 2 | Yes | N | **H** |
| 7 | `shelf_life_duration` | text\|string\|descriptor | Item | No sibling; ISO 22000 food safety + FDA standards anchor | new_substrate_characteristic | 2 | Yes | N | **H** |

Subtotal: 8 rows / 17 BC, 5 H-conf (with multi-source standards anchors), 3 M-conf.

### 4.2 Maintenance-order sourced — 10 rows / 14 BC

| # | bf_name | Shape | Target entity | BC need (substrate sibling?) | Route type | BC gain | Panel? | Eq dep? | Conf |
|---:|---|---|---|---|---|---:|---|---|---|
| 8 | `parent_maintenance_order_identifier` | identifier\|string\|identifier | MO | No "maintenance order identifier" sibling; recursive parent-of-MO shape | new_substrate_characteristic + role_qualifier=parent | 1 | Yes | N | M |
| 9 | `job_plan_identifier` | identifier\|string\|identifier | MO | No sibling | new_substrate_characteristic | 1 | Yes | N | L (BC=1 narrow) |
| 10 | `preventive_maintenance_identifier` | identifier\|string\|identifier | MO | No sibling | new_substrate_characteristic | 1 | Yes | N | L (BC=1 narrow) |
| 11 | `calendar_identifier` | identifier\|string\|identifier | MO | No sibling; generic calendar | new_substrate_characteristic | 1 | Yes | N | L (BC=1 narrow + cross-cutting concept) |
| 12 | `planner_identifier` | identifier\|string\|identifier | MO | No sibling; possible map-to Person/Party identifier — but Person/Party not yet admitted | new_substrate_characteristic | 1 | Yes | N | L |
| 13 | `supervisor_identifier` | identifier\|string\|identifier | MO | No sibling; same Person/Party concern as `planner_identifier` | new_substrate_characteristic | 1 | Yes | N | L |
| 14 | `budgeted_amount` | amount\|number\|measure | MO | Substrate amount-family present (`gross amount`, `net amount`, `payment amount`, `posted amount`, `entry amount`, …) but no "budgeted amount" sibling. Risk: Checker may park if MO-amount semantics overlap. | new_substrate_characteristic OR amount-family map-to-existing (uncertain) | 2 | Yes | N | M |
| 15 | `estimated_duration` | text\|string\|descriptor | MO | No sibling; substrate has `lead time` + `cycle time` for time-related fields. ISO 8601 duration anchor. | new_substrate_characteristic | 2 | Yes | N | M |
| 16 | `actual_duration` | text\|string\|descriptor | MO | Same as #15 | new_substrate_characteristic | 2 | Yes | N | M |
| 17 | `remaining_duration` | text\|string\|descriptor | MO | Same as #15 | new_substrate_characteristic | 2 | Yes | N | M |

Subtotal: 10 rows / 14 BC, 5 M-conf, 5 L-conf (BC=1 narrow — high Checker-park risk per C2 calibration).

### 4.3 Asset sourced — 2 rows / 3 BC

| # | bf_name | Shape | Target entity | BC need (substrate sibling?) | Route type | BC gain | Panel? | Eq dep? | Conf |
|---:|---|---|---|---|---|---:|---|---|---|
| 18 | `initial_amount` | amount\|number\|measure | Asset | No sibling; substrate amount-family present | new_substrate_characteristic OR amount-family map-to-existing (uncertain) | 2 | Yes | N | M |
| 19 | **`asset_type`** | **text\|string\|descriptor** | **Asset** | **No sibling. Type-code-family present in substrate (`account class code`, `account type code`, `document type code`, `rate source code`, …) — `asset_type` would extend the family.** | **new_substrate_characteristic** | **1** | **Yes** | **soft-trigger** | **L (BC=1) + Equipment-aware operator gate recommended** | 

Subtotal: 2 rows / 3 BC.

### 4.4 BOM sourced — 1 row / 3 BC

| # | bf_name | Shape | Target entity | BC need (substrate sibling?) | Route type | BC gain | Panel? | Eq dep? | Conf |
|---:|---|---|---|---|---|---:|---|---|---|
| 20 | `required_percent` | rate\|number\|measure | Item (via master-data-root alt-route) | No "required percent" sibling; substrate has `tax rate`, `exchange rate`, `interest rate` — different role | new_substrate_characteristic | 3 | Yes | N | M |

Subtotal: 1 row / 3 BC. Cross-routing flag: this row's primary OAGIS source is `bom.bom-item-data.required-percent` (BOM Item Data context). BOM is in `production-composite` slice (RED, held). Alt-routing via master-data-root requires operator framing that the binding is to **Item** as the percent target, not to BOM as the parent. Surfaced explicitly here.

## 5. The `asset_type` soft-trigger explained

Row #19 (`asset_type` from `asset.asset.asset-type`) is the row that interacts with the Equipment operator-decision packet (PR #65 §6) as a **soft-trigger**.

| Concern | Detail |
|---|---|
| Why it interacts with Equipment | If operator picks Option B (Equipment as Asset discriminator), the discriminator carrier is most naturally `asset_type` with values like 'equipment' / 'building' / 'vehicle'. Authoring `asset_type` now and admitting it as active substrate sets the type-family precedent. |
| Why it does NOT lock in Option B | The characteristic admission itself does not constrain which values it admits at runtime. Under Option A (Equipment as peer entity), `asset_type` carries values like 'building' / 'vehicle' / 'infrastructure' but NOT 'equipment' (Equipment would be its own entity, not a value). Under Option B, it carries 'equipment' as one of the values. The set of admissible values is a runtime / canonical-resolution decision, not an entity-admission decision. |
| Why it's still flagged | Per Foundation Hard Rule, no lower-layer compensation for upper-layer semantic gaps. If operator hasn't decided Equipment (Option A vs B vs C), authoring `asset_type` ahead of that decision is not wrong, but it normalises the type-discriminator pattern on Asset — making Option B feel cheaper later than it should. The operator should be aware. |
| Recommendation | **Do NOT bundle `asset_type` into the first retrofit batch.** Hold it until either Equipment is decided OR a dedicated Asset-discriminator-family decision packet authorises it. This is the cleanest separation of concerns. |

The 19 other rows are Equipment-independent and can proceed regardless of Equipment decision.

## 6. First-retrofit-batch recommendation

### 6.1 Selection criteria (operator scope: "smallest high-confidence batch")

The 5-row subset is selected by these criteria, applied in order:
1. **Single source entity** — one OAGIS noun, one BareCount target entity. Reduces panel-side semantic search.
2. **Multi-source standards anchor available** — passes C1+C2 calibration's empirical predictor of low Checker-park risk.
3. **Equipment-independent** — does not interact with held PR #65 decision.
4. **BC count ≥ 2** — avoids the BC=1 single-slice narrow-risk subset that C2 calibration showed ~70% Checker-park rate.

### 6.2 Proposed first batch — 5 item-master rows / 10 BC

| # | bf_name | Standards anchors | Why this batch |
|---:|---|---|---|
| 2 | `product_name` | GS1 GTIN + product master; ISO/IEC 8000 master-data; ANSI X12 / EDIFACT product-name conventions | All 5 rows bind to Item, single OAGIS path `item-master.item-master.*`, single Pass-3 binding family. |
| 3 | `brand_name` | GS1 brand owner registry; ISO 22005 traceability | Multi-source standards anchors reduce Checker-park risk significantly. |
| 5 | `serial_number_specification_description` | ISO/IEC 15459 unique identifier; ASTM E2129 serialisation | High-confidence rows from C2 calibration: BC≥2 + multi-source anchor + single entity. |
| 6 | `lot_number_specification` | GS1 batch / lot; FDA 21 CFR 211.130 traceability | Each row is independently bindable — no inter-row coupling. |
| 7 | `shelf_life_duration` | ISO 22000 food safety; FDA / EU food regulations | If 1 row Checker-parks, others survive. |

Total: 5 panels, ~10 BC expected gain, ~8–12 min wall-clock at concurrency 2–3.

### 6.3 Why NOT the larger 19-row batch in one shot

- C2 calibration: BC=1 single-slice rows have ~70% Checker-park rate. 5 of 19 rows are BC=1 (`job_plan_identifier`, `preventive_maintenance_identifier`, `calendar_identifier`, `planner_identifier`, `supervisor_identifier`). Including them would dilute the batch's success rate.
- Mixed entity binding (Item, MO, Asset, BOM) raises Pass-3 binding-family complexity if all are admitted in one panel session.
- Operator scope explicitly said "smallest high-confidence batch" — the 5-row item-master subset is the operator-scope-aligned choice.

### 6.4 Subsequent retrofit waves (not authorised; proposed sequence)

Once batch 1 lands:

| Wave | Rows | BC | Why this order |
|---|---:|---:|---|
| Batch 2 — MO duration triplet | `estimated_duration`, `actual_duration`, `remaining_duration` | 6 | Single entity (MO), single shape, ISO 8601 anchor; tests duration-family pattern |
| Batch 3 — MO planner / supervisor person-bound | `planner_identifier`, `supervisor_identifier` | 2 | Surfaces Party/Person admission question (E3 master-data) as a prerequisite |
| Batch 4 — amount-family rows | `budgeted_amount`, `initial_amount` | 4 | Amount-family decision (per C4 projection's bare-`amount` operator gate) sets precedent for naming |
| Batch 5 — remaining MO identifiers | `parent_maintenance_order_identifier`, `job_plan_identifier`, `preventive_maintenance_identifier`, `calendar_identifier` | 4 | Higher-risk BC=1 batch; could be deferred if low priority |
| Batch 6 — uom_group + variety_name + required_percent | `uom_group_identifier`, `variety_name`, `required_percent` | 7 | Cross-cutting concepts; group at the end |
| Held | `asset_type` | 1 | Until Equipment decision lands |

Total across batches 1–6: 19 rows / 31 BC. Held: 1 row / 3 BC.

## 7. Open questions for operator

1. **Confirm first batch composition** — 5 item-master rows as proposed, or different cut?
2. **Confirm asset_type hold posture** — defer until Equipment decision lands (recommended), or treat as Equipment-independent and include in a later retrofit wave under the operator-aware framing?
3. **Confirm subsequent-wave sequencing** — proposed order in §6.4, or different priority?
4. **For batch 1 transport (when authorised)**: should the 5 packets run under Pass-2 entry note v2 Checker-First Preflight 6-Q discipline? Pass-1 used the 5-Q rubric pre-PR #62; Q-F adds the fast-lane-acceptable check which is Pass-2-entity-specific and arguably does not apply to characteristic admission. Operator framing welcome.

## 8. Scope locks honoured

- 0 panel calls.
- 0 substrate writes.
- 0 transport script invocations.
- 0 DDL changes.
- 0 ADR authoring.
- 0 changes to BC-coverage ledger.
- 0 changes to A0.5 catalogue.
- 0 changes to active entity / characteristic definitions.

Source coverage: A0.5 catalogue read fresh from bc-docs-v3 SSOT; BC-coverage ledger read fresh from bc-docs-v3 SSOT; projection JSON read from barecount-devhub branch `bcf-c3-c6-projection-2026-06-25` (origin); substrate state queried via live bc-core API at `localhost:3100`.

The §6 first-batch recommendation is falsifiable per the operator's Equipment-packet framing (§7 explicit alternatives). The §5 soft-trigger flag preserves operator agency on the Equipment-Asset discriminator question.

Held. Awaiting operator decision on first batch composition + asset_type posture.
