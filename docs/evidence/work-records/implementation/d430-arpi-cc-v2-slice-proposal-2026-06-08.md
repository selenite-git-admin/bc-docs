---
title: ARPI canonical-v2 CC slice — read-only proposal (mini-DBCP)
status: locked
date: 2026-06-08
project: bc-core
domain: implementation
governs: DEC-a6258b (D430 canonical-v2) · DEC-4a17e0 (D431 O↔C)
depends_on: active OC-v2 slice oc__customer_invoice_arpi_slice_type_sd_s_map (v1.0.0)
---

# ARPI canonical-v2 CC slice — read-only proposal (mini-DBCP)

**This is a proposal only. No CC is authored or activated. No DB writes.** Field names **locked by
operator 2026-06-08** (§3); held pending separate authoring approval, mirroring the D431 OC-v2 slice flow.

## Grounding (live, read-only — 2026-06-08, main @ beeab0c)

| Fact | Value |
|---|---|
| Active OC-v2 slice | `oc__customer_invoice_arpi_slice_type_sd_s_map` v1.0.0 (active) |
| OC-v2 declares observable (concept identity) | `1a2ac2f2`, `51482979`, `61e19048` |
| Grain entity (shared by all 3 concepts) | `e3963e45-ad13-4f6c-a1c3-fa56d8fd6446` — **active** |
| BCF concept `1a2ac2f2` | representation_term=`amount`, unit=`∅`, data_type=`decimal`, **active**, entity `e3963e45` |
| BCF concept `51482979` | representation_term=`identifier`, unit=`∅`, data_type=`string`, **active**, entity `e3963e45` |
| BCF concept `61e19048` | representation_term=`date`, unit=`∅`, data_type=`date`, **active**, entity `e3963e45` |
| canonical-v2 versions (any) | **0** |
| active canonical-v2 versions | **0** (the 83 active CC versions are legacy v1; the D430 C1 guard counts only active **v2**) |
| CC headers named customer_invoice | **0** |
| canonical-v2 meta-schema (v=2) | `field_selection` item requires `canonical_field`,`business_concept_id`,`representation_term`,`data_type` (+ optional `unit`) |

## 1. Exact target CC-v2 purpose
A **source-agnostic** canonical Customer Invoice ARPI slice: one canonical-v2 contract on the
Customer Invoice grain (`e3963e45`) whose `field_selection` selects the **same three BCF concepts**
now proven observable by the active OC-v2 slice. It declares canonical *meaning* (concept identity +
frozen snapshot) with **no source reference** — the O↔C check links it to the OC by concept identity,
not by naming a source. This is the canonical (C) counterpart to the already-active observation (O).

## 2. Exact `field_selection` candidates
Three entries, snapshots **copied from the live BCF concept** (D430 §1a.5 — never invented):

| canonical_field (proposed) | business_concept_id | representation_term | unit | data_type |
|---|---|---|---|---|
| `amount` | `1a2ac2f2-a502-41c1-ad14-d08d2b976e83` | amount | (null) | decimal |
| `document_number` | `51482979-9715-429f-949c-8961f82f436f` | identifier | (null) | string |
| `document_date` | `61e19048-d1c8-477b-a321-88fad1c28542` | date | (null) | date |

## 3. Canonical field names — LOCKED (operator, 2026-06-08)
Business/canonical, source-agnostic, and **concept-aligned**: the canonical field name mirrors the live
BCF concept's `representation_term`; we do **not** impose a narrower business meaning than the anchor carries.
- `amount` → concept `1a2ac2f2` (anchor representation_term = `amount`; **not** `net_amount` — the concept
  is the unqualified `amount`, so the canonical field stays unqualified and concept-aligned)
- `document_number` → concept `51482979` (anchor representation_term = `identifier`)
- `document_date` → concept `61e19048` (anchor representation_term = `date`)

None reference NETWR/VBELN/FKDAT. CC name: **`cc__customer_invoice_arpi_slice`** (no source token).

## 4. Required CC-v2 envelope shape
- `$contract = barecount/canonical/v2`
- **Grain entity = Customer Invoice `e3963e45`** — **derived**, not declared: the resolver computes it as
  the single shared `entity_id` of the selected concepts (the body carries no `grain_entity_id`).
- `body.field_selection` = the three entries above (concept_id + frozen snapshot triple).
- `body.business_object_code = customer_invoice` (mirrors the OC).
- Remaining meta-schema body fields (`grain`, `temporal_gate`, `resolution_rules`, `resolved_schema`,
  `semantic_rules`, `evaluation_tier`, `posting_date_field`) — minimal, per the v2 meta-schema, exactly
  as the OC slice used a minimal `so_schema`.
- Proposed CC name: **`cc__customer_invoice_arpi_slice`** — deliberately **no** source token (a CC is
  source-agnostic, unlike the OC's `_type_sd_s_map`).
- Authoring path (when approved): SERVICES-ONLY via `ContractService` — `createContract(category='canonical')`
  → `createVersion` (runs D430 integrity + D431 O↔C at authoring) → `submitForReview` → `approveVersion`
  → `activateVersion` (re-runs D430 integrity + one-active-CC-per-grain + D431 O↔C at activation).

## 5. D430 integrity expectations (will be asserted at authoring + activation)
- All three concepts **exist and are `active`** → ✅ (verified live).
- All three on the **same grain entity `e3963e45`** → ✅ (verified live; `entityIds.size === 1`).
- Concepts **unique** within the CC (no duplicate `business_concept_id`) → ✅ (three distinct).
- **Snapshots equal the live BCF triple** (representation_term/unit/data_type) → ✅ (matches §2).
- **One active CC per grain entity (C1)** → ✅ clear: 0 active canonical-v2 contracts exist, so none
  claims `e3963e45`.

## 6. D431 O↔C expectation
- Each selected concept must be **declared observable from a source by ≥1 active observation-v2 mapping**.
- The active OC-v2 slice declares exactly `{1a2ac2f2, 51482979, 61e19048}` observable → all three CC
  concepts are covered → ✅.
- This is **concept identity** (set membership in `observedConceptIds`), **not** OC identity — the CC never
  names the OC or a source; it only requires that the concept be observable *somewhere* active.

## 7. Stop conditions (evaluated against current live state)
| # | Condition | Live verdict |
|---|---|---|
| 7a | An active canonical-v2 CC already claims Customer Invoice grain → **stop** | **CLEAR** — 0 active v2 CCs |
| 7b | Any concept anchor missing / inactive / superseded → **stop** | **CLEAR** — all 3 active |
| 7c | O↔C observability does not see the active OC-v2 → **stop** | **CLEAR** — OC-v2 declares all 3 |
| 7d | Proposed canonical field names are source-specific → **stop** | **CLEAR** — `amount`/`document_number`/`document_date` (concept-aligned) |

All four stop conditions are currently clear. (They will be re-checked at author/activate time; if the
OC-v2 were superseded or a concept deactivated before then, authoring would fail-closed.)

## 8. Explicit exclusions
- No CC authoring yet · no ARPI MC rebind · no MCF materialization · no direct DB writes · no force activation.
