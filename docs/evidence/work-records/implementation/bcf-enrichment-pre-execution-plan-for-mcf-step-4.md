---
uid: bcf-enrichment-pre-execution-plan-for-mcf-step-4
title: BCF Enrichment Pre-Execution Plan for MCF Step 4
description: Pre-execution plan that grounds the Step 4 BCF enrichment slice (mcf-step-4-first-representative-metrics-and-bcf-enrichment-slice.md, f08b1ee) against live concept_registry.* coverage queried 2026-05-26 with bc-postgres MCP under expanded schema allowlist. Maps the slice's required entities, business concepts, and characteristics against what is already authored, identifies the load-bearing operator decision on `outstanding amount` (F4-S1 §6 deferral) as three options with exact enrichment impact, and produces an execution-ready Phase A / B / C / D plan that BCF panel operators can run without re-derivation. Re-checks BCF v1 packet sufficiency against the live-evidenced slice and confirms no B6-v2 trigger fires. No enrichment writes performed; no concept_registry.* create or modify; no MCF M2 DDL apply; no MCF M3 open; no MC creation.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: enrichment-pre-execution
---

# BCF Enrichment Pre-Execution Plan for MCF Step 4

## 1. Scope, grounding, and discipline

### 1.1 Purpose

Step 4 (`mcf-step-4-first-representative-metrics-and-bcf-enrichment-slice.md`, commit `f08b1ee`) selected 10 representative candidate-intent metrics and derived a bounded BCF enrichment slice. Step 4 §7.3 + §10.1 + §1.3 left two acts as Step 4 enrichment session prerequisites:

1. Authorize `concept_registry` schema on the bc-postgres MCP allowlist so the operator can verify per-row characteristic lifecycle state and live coverage before authoring.
2. Resolve the `outstanding amount` characteristic operator decision (F4-S1 §6 deferral revisit; Step 4 §5.x options a / b / c).

This pre-execution plan completes the first act and frames the second. It produces an execution-ready BCF enrichment plan grounded in live `concept_registry.*` evidence as of 2026-05-26.

### 1.2 What this plan is and is not

| | This plan |
|---|---|
| Is | A doc that maps Step 4's slice against live registry coverage and orders the enrichment acts under each option for the operator decision on `outstanding amount`. |
| Is | The operator-ready inputs for the next session that *actually authors* BCF panel runs. |
| Is not | A BCF enrichment act. No `createEntity`, no `createBusinessConcept`, no `createCharacteristic` runs are executed. |
| Is not | An MCF M2 DDL apply, M3 open, or MC creation. All MCF gates remain where MCF M0 + M1 left them. |
| Is not | A B6-v2 retrofit. No hard trigger fires under the live-evidenced slice (re-checked in §8). |
| Is not | A revision of Step 4 selection. The 10 representative metrics from Step 4 §4 are preserved as-is; §5 of this plan only resolves the characteristic ambiguity the metric bindings depend on. |

### 1.3 Inputs read

| Class | Source | Role |
|---|---|---|
| Step 4 selection + per-metric BCF needs | `mcf-step-4-first-representative-metrics-and-bcf-enrichment-slice.md` (`f08b1ee`) | The 10 metrics + slice scope this plan grounds |
| BCF enrichment preflight | `bcf-enrichment-preflight-for-mcf-seed-cases.md` (`3495739`) | v1 packet sufficiency mechanics + trigger conditions |
| BCF/MCF alignment note | `bcf-mcf-panel-workbench-alignment-note.md` (`da8d9b7`) | v1 packet vs B6-v2 workbench distinction |
| MCF M1 foundational ADR | `ADR-c3e57f.md` (D422) + Decisions 7 / 9 / 10 | Candidate-vs-authority discipline; BCF as sole semantic-binding authority; operator-confirm guardrails |
| BCF F4-S1 v1 characteristic seed list | `business-concept-registry-f4-s1-characteristic-seed-list.md` (accepted 2026-05-21) | The 24-characteristic baseline + §6 deferral of `outstanding amount` |
| BCF B10 publication lifecycle design | `business-concept-registry-b10-publication-lifecycle-design.md` line 84 | `draft` characteristic invisible to BCF binding; activation is operator-gated |
| Live `concept_registry.*` reads | bc-postgres MCP `pg_query` 2026-05-26 (this session) | The empirical coverage map §3 grounds |

### 1.4 Discipline assertions

| Assertion | Status |
|---|---|
| No enrichment writes performed this session | ✓ — `allow_write: false` confirmed on `pg_server_info` (§2.1); only `pg_query` SELECTs against `concept_registry.*`. |
| No concept_registry.* create or modify | ✓ — every read cited inline is a SELECT. |
| No MCF M2 DDL apply, no M3 open, no MC creation | ✓ — none of those gates is touched. |
| No B6-v2 open | ✓ — re-checked sufficient in §8; no hard trigger fires. |
| Live coverage claims grounded in cited SELECTs | ✓ — §3 cites the exact SELECT for each table inline. |

---

## 2. Verification gates passed before reading the registry

### 2.1 bc-postgres MCP allowlist + write-discipline

Per Step 4 §10.1 / BCF preflight §7.1 / MCF M0 §9 item 5, BCF Registry read access on the bc-postgres MCP allowlist was the prerequisite for live verification. The allowlist change shipped before this session opened (operator edit in `barecount-devhub/.claude/settings.json` + worktree settings; `PGMCP_SCHEMAS` extended from `contract,source,metric,platform,runtime,master` to `contract,source,metric,platform,runtime,master,concept_registry`). `PGMCP_ALLOW_WRITE` remains absent; per `bc-pg-mcp/src/config.ts` writes stay disabled unless the env var is literally `true`.

`pg_server_info` 2026-05-26 (this session):

```
schemas:           [concept_registry, contract, master, metric, runtime, source]
allow_write:       false
schema_allowlist:  [contract, source, metric, platform, runtime, master, concept_registry]
```

Both checks pass:
- `concept_registry` is in `schema_allowlist`.
- `allow_write` is `false`.

### 2.2 bc-pg-mcp tool-bug note (workaround applied)

`pg_count` and `pg_list_tables` both fail across all schemas with `column "tablename" does not exist`. This is a bc-pg-mcp internal bug (likely a `pg_tables`/`information_schema.tables` column-name mix-up in the helper queries). It is not an allowlist issue; the schema is correctly admitted. This session worked around the bug by issuing the equivalent SELECTs through `pg_query`. The bug is logged here for follow-up by the bc-pg-mcp owner; it does not block enrichment-time work because `pg_query` is the operational read path.

### 2.3 What was NOT loosened

- No additional schemas added.
- `allow_write` left untouched.
- `concept_registry` write tools (createEntity / createBusinessConcept / createCharacteristic) remain inside the bc-core RegistryAuthoringService boundary — bc-postgres MCP cannot reach them and is not intended to.

---

## 3. Live concept_registry coverage (evidence)

All counts and rows below are from live SELECT on 2026-05-26. The SELECT statements are cited inline so a future reader can reproduce.

### 3.1 Aggregate counts

```sql
SELECT 'entity', COUNT(*) FROM concept_registry.entity
UNION ALL SELECT 'business_concept', COUNT(*) FROM concept_registry.business_concept
UNION ALL SELECT 'characteristic', COUNT(*) FROM concept_registry.characteristic
UNION ALL SELECT 'representation_term', COUNT(*) FROM concept_registry.representation_term
UNION ALL SELECT 'alias', COUNT(*) FROM concept_registry.alias
UNION ALL SELECT 'entity_version', COUNT(*) FROM concept_registry.entity_version
UNION ALL SELECT 'business_concept_version', COUNT(*) FROM concept_registry.business_concept_version
UNION ALL SELECT 'entity_supersession', COUNT(*) FROM concept_registry.entity_supersession
UNION ALL SELECT 'business_concept_supersession', COUNT(*) FROM concept_registry.business_concept_supersession
UNION ALL SELECT 'characteristic_supersession', COUNT(*) FROM concept_registry.characteristic_supersession
UNION ALL SELECT 'supersession_proposal', COUNT(*) FROM concept_registry.supersession_proposal;
```

| table | rows |
|---|---:|
| entity | 1 |
| business_concept | 1 |
| characteristic | 26 |
| representation_term | 15 |
| alias | 0 |
| entity_version | 1 |
| business_concept_version | 1 |
| entity_supersession | 0 |
| business_concept_supersession | 0 |
| characteristic_supersession | 0 |
| supersession_proposal | 0 |

### 3.2 Entity (1 row, active)

```sql
SELECT e.entity_id, e.lifecycle_state, ev.canonical_name, ev.definition, e.created_at, e.created_by
FROM concept_registry.entity e
LEFT JOIN concept_registry.entity_version ev ON ev.entity_version_id = e.active_version_id;
```

| entity_id | lifecycle_state | canonical_name | created_at | created_by |
|---|---|---|---|---|
| `e974a6cd-…fe71` | `active` | Sales Order Line | 2026-05-22T07:31:59Z | bcf-registry-authoring-panel |

Definition (verbatim): *"A line item within a sales order that records a specific product or service, quantity, pricing, and fulfillment-relevant details."*

### 3.3 Business concept (1 row, active)

```sql
SELECT bc.concept_id, bc.lifecycle_state, bc.kind, bc.identity_role, ev.canonical_name AS entity_name,
       c.term AS characteristic_term, bc.representation_term, bcv.definition
FROM concept_registry.business_concept bc
LEFT JOIN concept_registry.entity_version ev ON ev.entity_id = bc.entity_id
LEFT JOIN concept_registry.characteristic c ON c.characteristic_id = bc.characteristic_id
LEFT JOIN concept_registry.business_concept_version bcv ON bcv.concept_version_id = bc.active_version_id;
```

| concept_id | lifecycle_state | kind | identity_role | entity_name | characteristic | rep term |
|---|---|---|---|---|---|---|
| `f66642ad-…f5c3` | `active` | value | descriptive | Sales Order Line | unit price | amount |

Definition (verbatim): *"The price charged for one unit of the product or service on a sales order line, before multiplication by quantity."*

### 3.4 Characteristics (26 rows, all active)

```sql
SELECT term, lifecycle_state, created_at FROM concept_registry.characteristic ORDER BY term;
```

| # | term | lifecycle_state | created_at | F4-S1 cohort? |
|---:|---|---|---|---|
| 1 | credit limit | active | 2026-05-21 | F4-S1 |
| 2 | cycle time | active | 2026-05-24 | post-F4-S1 |
| 3 | delivered quantity | active | 2026-05-21 | F4-S1 |
| 4 | description | active | 2026-05-21 | F4-S1 |
| 5 | discount | active | 2026-05-21 | F4-S1 |
| 6 | document date | active | 2026-05-21 | F4-S1 |
| 7 | due date | active | 2026-05-21 | F4-S1 |
| 8 | effective date | active | 2026-05-21 | F4-S1 |
| 9 | exchange rate | active | 2026-05-21 | F4-S1 |
| 10 | expiry date | active | 2026-05-21 | F4-S1 |
| 11 | freight charge | active | 2026-05-21 | F4-S1 |
| 12 | gross weight | active | 2026-05-21 | F4-S1 |
| 13 | interest rate | active | 2026-05-21 | F4-S1 |
| 14 | lead time | active | 2026-05-22 | post-F4-S1 |
| 15 | line number | active | 2026-05-21 | F4-S1 |
| 16 | net weight | active | 2026-05-21 | F4-S1 |
| 17 | note | active | 2026-05-21 | F4-S1 |
| 18 | ordered quantity | active | 2026-05-21 | F4-S1 |
| 19 | payment terms | active | 2026-05-21 | F4-S1 |
| 20 | posting date | active | 2026-05-21 | F4-S1 |
| 21 | quantity on hand | active | 2026-05-21 | F4-S1 |
| 22 | reason | active | 2026-05-21 | F4-S1 |
| 23 | status | active | 2026-05-21 | F4-S1 |
| 24 | tax | active | 2026-05-21 | F4-S1 |
| 25 | tax rate | active | 2026-05-21 | F4-S1 |
| 26 | unit price | active | 2026-05-21 | F4-S1 |

24 of 26 carry `2026-05-21` create timestamps — the F4-S1 v1 cohort. 2 carry post-F4-S1 dates: `lead time` (2026-05-22 11:40Z) and `cycle time` (2026-05-24 06:19Z), both `active`. Neither is in the 10-metric slice.

### 3.5 Representation terms (15 rows)

```sql
SELECT term FROM concept_registry.representation_term ORDER BY term;
```

| amount | code | count | date | date_time | duration | identifier | indicator | measure | name | percentage | quantity | rate | ratio | text |

### 3.6 Aliases, supersessions, proposals — empty

- `alias`: 0 rows. No synonyms / surface aliases are authored yet.
- `entity_supersession` / `business_concept_supersession` / `characteristic_supersession`: 0 rows. No retired-and-replaced concepts.
- `supersession_proposal`: 0 rows. No F3 proposals in flight.

Implication for Step 4: zero risk of name-collision with a previously-superseded concept during Phase A entity authoring; zero risk of authoring a concept whose F3 supersession has been proposed and is awaiting decision.

---

## 4. Coverage versus Step 4 assumptions

This section cross-checks Step 4's per-metric BCF needs (§5 and §7.2 of `mcf-step-4-first-representative-metrics-and-bcf-enrichment-slice.md`) against the live evidence in §3.

### 4.1 What Step 4 assumed vs what is live

| Step 4 assumption | Live state | Delta |
|---|---|---|
| Entity: Sales Order Line — active | confirmed (`e974a6cd-…fe71`, `active`) | none |
| BC: Sales Order Line · Unit Price — active | confirmed (`f66642ad-…f5c3`, `active`) | none |
| 15 representation terms — seeded + active | confirmed (15 rows) | none |
| "24 F4-S1 v1 characteristics" (Step 4 §7.1) | 26 active — 24 F4-S1 cohort + `lead time` + `cycle time` (both post-F4-S1, both active) | **+2 (positive)** — additional capacity beyond the slice need; neither in the slice |
| F4-S1 characteristics lifecycle "per-row activation needs verification" (Step 4 §7.3) | All 24 F4-S1 cohort rows are `active` 2026-05-26 | **resolved positive** — no B10 activation acts are prerequisite to Step 4 enrichment |
| `outstanding amount` characteristic — gap, F4-S1 §6-deferred | confirmed absent | none — gap as expected |
| `recognized amount`, `billed amount`, `invoice amount` characteristics — gap, F4-S1 §6-deferred | confirmed absent (no rows with these terms) | none — gap as expected |
| Entity: Customer Invoice — gap | confirmed absent (`entity` table has only 1 row) | none — gap as expected |
| Entity: third (negative-test) — gap | confirmed absent | none — gap as expected |
| BCs on Customer Invoice (6-9 BCs) | confirmed absent (`business_concept` table has only 1 row, on Sales Order Line) | none — gap as expected |
| BCs on Sales Order Line (discount, ordered quantity, negative-test BC) | confirmed absent (only Unit Price BC on Sales Order Line) | none — gap as expected |

### 4.2 The seven characteristics the slice depends on — all active

Step 4 §7.2 + §7.3 named seven F4-S1 characteristics that "must be active before the Customer Invoice BCs that depend on them can be authored". The live check confirms all seven are `active`:

| # | Characteristic | Used by metrics | Live state |
|---:|---|---|---|
| 1 | due date | 2, 5, 7 | active |
| 2 | posting date | 3, 5, 6 | active |
| 3 | effective date | 4 | active |
| 4 | status | 4 | active |
| 5 | discount | 8 | active |
| 6 | ordered quantity | 8 | active |
| 7 | unit price | 8 | active (and Sales Order Line · Unit Price BC already authored) |

**Consequence:** Step 4 §7.3's contingent prerequisite ("If any of the seven is still `draft`, that B10 activation is a Step 4 prerequisite act") does not fire. **Phase B of the enrichment plan does NOT require any B10 activation runs.** This is a positive delta from Step 4's hedged assumption.

### 4.3 The `outstanding amount` gap — Step 4's stated scope is internally inconsistent

Step 4 §5.x stated:

> "Three characteristics are intent-load-bearing for Metrics 1, 3, 6 but are not in the F4-S1 24-approved list … `outstanding amount` … `recognized amount` … `billed amount` / `invoice amount` … This ambiguity is the load-bearing operator decision Step 4 enrichment surfaces. It is not blocking for Step 4 *planning*; it is blocking for Step 4 *execution* on Metrics 1, 3, 6 specifically. Metrics 2, 4, 5, 7, 8, 9, 10 are not affected (their BCs map to F4-S1-seeded characteristics)."

Cross-checking Step 4 §5 (per-metric BCF needs tables) against this claim:

| Metric | Does the per-metric needs table (§5) actually bind to `outstanding amount`? |
|---:|---|
| 1 | Yes — `BC: Customer Invoice · outstanding amount` (§5 Metric 1 row 2) |
| 2 | Yes — `BC: Customer Invoice · outstanding amount` for both I1 (overdue subset) and I2 (total) |
| 3 | No directly — uses `recognized amount` / `billed amount` |
| 4 | No |
| 5 | No |
| 6 | No — uses `invoice amount` |
| 7 | Yes — `BC: Customer Invoice · outstanding amount` for the bucket-aggregate value |
| 8 | No (Sales Order Line only) |
| 9 | Yes — `BC: Customer Invoice · outstanding amount` (deliberately identical binding for MLS-14 collapse) |
| 10 | Yes (inherits Metric 2's bindings) |

**True dependency on `outstanding amount`: Metrics 1, 2, 7, 9, 10 — five metrics, not three.** Metrics 3 and 6 depend on the *other* deferred characteristics (`recognized amount`, `billed amount`, `invoice amount`).

This means Step 4 §5.x's parenthetical "Metrics 2, 4, 5, 7, 8, 9, 10 are not affected" is wrong about Metrics 2, 7, 9, 10. Only Metrics 4, 5, 8 are independent of every F4-S1-deferred characteristic.

This finding materially changes the Option C arithmetic (§5.3 below). It is a pre-execution correction, not a Step 4 revision: Step 4 §5 is the authoritative per-metric needs table; Step 4 §5.x's affected-metric list was a parenthetical that did not propagate through the per-metric tables.

### 4.4 Aliases not yet authored

Step 4 §1.3 listed "aliases / synonyms if available" as an input class. Live: 0 alias rows. Step 4 enrichment proceeds with **no incoming alias evidence**. This is not a blocker; the alias surface (`concept_registry.alias`) is for canonical-name / surface-name distinctions that the panel can author later as concepts are renamed or surfaced in different UI contexts. No alias authoring is in scope for Step 4.

### 4.5 Collision risk surface

The 26 live characteristic terms are the duplicate-detection surface for any `createCharacteristic` panel run. New characteristic candidates checked against this list:

| Proposed new term | Closest live term | Collision risk |
|---|---|---|
| `outstanding amount` | none semantically close; `credit limit` shares "amount-y" semantics but different concept | Low |
| `posted amount` | none | Low |
| `recognized amount` | none | Low |
| `billed amount` | none | Low |
| `invoice amount` | none | Low |
| `clearing date` | `effective date` (existing) — has overlap if operator decides clearing = effective | **Medium** — panel may judge this an alias or a fresh characteristic |
| `cleared indicator` | none (indicator rep term exists; no characteristic) | Low |

For new entity names:
- `Customer Invoice` — no existing entity; no `Invoice`, `Bill`, `Receivable` etc. in the 1-row entity table. Low collision risk.
- Negative-test entity (operator names) — should pick a deliberately non-collisional name (e.g. `Test Negative Entity`).

---

## 5. The `outstanding amount` operator decision

This is the load-bearing decision Step 4 §5.x and §10.1 surfaced. The decision is taken at the opening of the Step 4 enrichment session, not in this pre-execution plan. This section enumerates the three options the operator chooses among, with exact enrichment impact derived from the live coverage in §3 and the corrected dependency in §4.3.

### 5.1 Why this is the decision

`outstanding amount` was explicitly deferred during the F4-S1 v1 characteristic seed-list content lock on 2026-05-21:

> "Aggregate / net position, not v1 raw characteristic; sits at metric / canonical layer; deferred to … carefully framed concept authored after Registry is live." — F4-S1 §6 decision 1.

The Registry IS now live (post-D418 Gate 5 verification, F4-S1 accepted, BCF v1 panel shipping). The trigger for the "carefully framed concept" revisit is met. The operator decides whether to reopen the deferral now, work around it, or defer the affected metrics.

The decision also affects the three other F4-S1-deferred characteristics (`recognized amount`, `billed amount`, `invoice amount`) that Metrics 3 and 6 depend on. For coherence, this section treats all four as one operator decision, since the framing argument is the same.

### 5.2 Option A — Author `outstanding amount` (and the three sibling characteristics) under F4-v2 with operator-confirm

Author all four F4-S1-deferred characteristics via the F4-v2 createCharacteristic path. Each is high-risk (non-`global` Vocabulary Admission Checklist classification likely; operator-confirm-required). Authoring formally reverses the F4-S1 §6 deferral on the operator-recorded ground that the Registry is now live and the panel + operator can author them "carefully framed" with explicit definitions and grounding evidence.

**Enrichment impact:**

| Phase | Acts under Option A |
|---|---|
| A. Entities | 2 createEntity runs (Customer Invoice + negative-test third entity) |
| B. Characteristics | 4 F4-v2 createCharacteristic runs, each operator-confirm-required: `outstanding amount`, `recognized amount`, `billed amount`, `invoice amount`. Plus 0 B10 activation runs (all 7 slice-required F4-S1 chars are already active per §4.2). |
| C. Business Concepts | 12 createBusinessConcept runs: 9 on Customer Invoice (incl. the 3 conditional BCs whose characteristics Option A authored) + 2 on Sales Order Line (discount, ordered quantity) + 1 negative-test BC |
| D. Acceptance | All 10 Step 4 metrics' bindings resolvable; AST node coverage 7-of-N exercised |

**Metrics unblocked:** 10 of 10.

**Cost:** 4 F4-v2 createCharacteristic runs (each operator-confirm-required). Requires operator to record the F4-S1 §6 deferral reversal rationale on each createCharacteristic run.

**Risk:** The F4-S1 §6 concern stands — `outstanding amount` is conceptually a derived net position, not a raw characteristic. Authoring it as a primitive characteristic embeds a derivation rule in BCF vocabulary that may be hard to revise later. The same concern applies (in weaker form) to `recognized amount` / `billed amount` / `invoice amount`, which are accounting-conceptual aggregates rather than source-system primitives.

### 5.3 Option B — Avoid direct authoring, compose from rawer primitives

Express `outstanding amount` semantics via an MCF AST filter clause over a rawer "posted amount" characteristic. The substantive proposal is:

- Author one new characteristic: `posted amount` (the per-line debit/credit amount as recorded in the source-system ledger — likely classified `industry_specific` finance under F4-v2 Vocabulary Admission Checklist; operator-confirm-required).
- Reuse the existing `effective date` characteristic for "clearing date" semantics (panel decides whether this overload is acceptable, or whether to author `clearing date` as a separate characteristic — Medium collision risk per §4.5).
- Express "outstanding" at MCF AST time as `SUM(posted amount) WHERE clearing date IS NULL OR clearing date > observation_date`. The "outstandingness" lives in the MCF filter, not in BCF vocabulary.

This honors F4-S1 §6's principle (outstanding amount is metric-layer concern, not characteristic-layer) while preserving the operational metric.

For `recognized amount` / `billed amount` / `invoice amount` (Metrics 3 and 6), Option B requires a similar reframing. Realistic options:

- Metric 3 (unbilled revenue = recognized − billed): may be expressible as `SUM(posted amount) FILTER (revenue account) − SUM(posted amount) FILTER (AR account)` at MCF AST time, given a per-line account classification. This requires `account code` characteristic (or similar) — not in the 26 active. Additional createCharacteristic run.
- Metric 6 (recognized revenue per fiscal_period): same shape — `SUM(posted amount) FILTER (revenue account) GROUP BY fiscal_period`. Same characteristic gap.

**Enrichment impact:**

| Phase | Acts under Option B |
|---|---|
| A. Entities | 2 createEntity runs (Customer Invoice + negative-test third entity) |
| B. Characteristics | 1 F4-v2 createCharacteristic for `posted amount` (operator-confirm-required). Plus conditional 1-2 more if Metrics 3 + 6 are kept in scope (e.g. `account code`). Plus 0 B10 activation runs (per §4.2). |
| C. Business Concepts | 9-11 createBusinessConcept runs: 6-8 on Customer Invoice (depending on Metric 3 + 6 handling; minimum is `posted amount`, `due date`, `posting date`, `status`, `effective date`, `invoice id`) + 2 on Sales Order Line (discount, ordered quantity) + 1 negative-test |
| D. Acceptance | All 10 (or 8 if Metrics 3 + 6 deferred) Step 4 metrics' bindings resolvable |

**Metrics unblocked:** 10 of 10 if `account code` (or equivalent) is authored for Metrics 3 + 6; 8 of 10 if Metrics 3 + 6 are deferred to Step-4-bis.

**Cost:** 1 F4-v2 createCharacteristic run (minimum) + Medium collision-risk panel decision on `effective date` overload for clearing-date semantics. Establishes a filter-based AR pattern that scales beyond Step 4 (future AR metrics inherit the filter convention rather than depending on more `*_amount` characteristics).

**Risk:** Pushes complexity into MCF AST per metric (every AR metric carries a `WHERE clearing IS NULL` filter). May overload `effective date` semantically if the panel does not author a separate `clearing date` characteristic. Metrics 3 + 6 may still need explicit characteristic authoring (`account code` or similar), which partially defeats Option B's stated avoidance.

### 5.4 Option C — Defer affected AR metrics to Step-4-bis

Do not author any of the four F4-S1-deferred characteristics. Author only the entities, BCs, and existing-F4-S1-characteristic-backed BCs the unaffected metrics need. Defer the affected metrics to a Step-4-bis enrichment session after the operator + BCF panel reach consensus on the characteristic question independently.

**Affected metrics under the corrected dependency map (§4.3):** Metrics 1, 2, 3, 6, 7, 9, 10 — seven of ten — depend on at least one F4-S1-deferred characteristic.

**Unblocked metrics under Option C:** 4, 5, 8 — three of ten.

**Enrichment impact:**

| Phase | Acts under Option C |
|---|---|
| A. Entities | 2 createEntity runs (Customer Invoice for Metrics 4 + 5; negative-test third entity) — Customer Invoice still required because Metrics 4 + 5 are Customer-Invoice-grained |
| B. Characteristics | 0 F4-v2 createCharacteristic runs. 0 B10 activation runs. |
| C. Business Concepts | 6 createBusinessConcept runs: 3 on Customer Invoice (status + effective date + invoice id, for Metric 4) + 1 on Customer Invoice (posting date already needed; due date for Metric 5) + 2 on Sales Order Line (discount, ordered quantity) + 1 negative-test. Net minimum: 6 BCs across 3 entities. |
| D. Acceptance | Only 3 of 10 metrics' bindings resolvable. AST node coverage drops: `bucket_assign` (Metric 7), `time_anchor_resolution` (Metric 6) are not exercised; `window` (Metric 5) and basic nodes are still exercised. Failure cases 9 + 10 also drop (both depend on `outstanding amount`). |

**Metrics unblocked:** 3 of 10. Failure cases drop. AST coverage: basic + window only.

**Cost:** Smallest immediate enrichment footprint, but the Step 4 acceptance criteria are not met (≥10 metric bindings resolved, 7 AST nodes exercised, ≥2 failure cases). A Step-4-bis is mandatory afterward. Effectively splits Step 4 into two enrichment sessions; the second session's scope is whatever Option A or Option B would have done.

### 5.5 Recommendation

**Recommended option: Option B (compose `outstanding` via MCF AST filter over `posted amount`), with Metrics 3 + 6 deferred to Step-4-bis.**

Rationale:
- Honors F4-S1 §6 directly — outstanding amount stays at metric / canonical layer, not characteristic layer. The operator does not have to reverse the F4-S1 §6 deferral rationale.
- Adds the minimum new vocabulary (`posted amount` — one F4-v2 run), staying within the BCF v1 packet capacity envelope (§8).
- Unblocks 8 of 10 Step 4 metrics (Metrics 1, 2, 4, 5, 7, 8, 9, 10) including both failure cases (9 + 10) and the `bucket_assign` AST node (Metric 7). Defers only Metrics 3 + 6.
- Establishes a future-proof AR pattern: every AR metric inherits the `clearing IS NULL OR clearing > as_of` filter idiom, rather than each AR metric requiring its own pre-aggregated characteristic.
- Avoids the conceptual error of treating a derived position as a primitive characteristic.

Conditions for the recommendation to hold:
- Panel + operator agree that `posted amount` is admissible as `industry_specific` finance under F4-v2 Vocabulary Admission Checklist.
- Panel + operator agree on how to express clearing semantics: either author `clearing date` as a separate characteristic (cleaner, +1 createCharacteristic run) or overload `effective date` (lighter, but Medium collision risk per §4.5).
- Operator accepts deferring Metrics 3 + 6 to Step-4-bis. The AST node loss is `time_anchor_resolution` (Metric 6 only); Metric 3 added no new AST node.

If any of those conditions does not hold, fall back to Option A and reverse the F4-S1 §6 deferral with explicit rationale (Registry is live; raw atomic primitives seeded; F4-v2 panel + operator can frame the derived characteristics carefully).

Option C is not recommended in isolation. Under the corrected dependency map (§4.3), Option C unblocks only 3 of 10 metrics and drops both failure cases — too thin to be useful as a one-time pre-execution plan. If the operator chooses C, treat it as Step 4 partial + a planned Step-4-bis (effectively combining C with a later A or B).

The decision is operator's. The remainder of this plan (§6) is parameterized so that any of A, B, C can be executed without re-derivation.

---

## 6. Execution-ready enrichment plan

This section is structured so the operator picks an option from §5 at session opening and the corresponding cells light up. Phase ordering follows BCF preflight §6.7 (Entities → Characteristics + activations → BCs → Acceptance).

### 6.1 Phase A — Entities (common across A / B / C)

Two `createEntity` panel runs. Both required regardless of option.

| Order | Entity | Required candidate evidence (`candidateEvidence`) | Notes |
|---:|---|---|---|
| A1 | Customer Invoice | Operator citation — recommended: APQC business architecture entry for billing / customer invoicing; or IFRS 15 contract liability / contract asset definition; or operator's bounded-domain definition of the AR invoice entity. Minimum: definition + source label + cited text. | The entity grain for 9 of 10 Step 4 metrics. |
| A2 | Negative-test entity | Operator citation — recommended: an explicit operator-supplied definition declaring the entity's negative-test role (e.g. "Test Negative Entity — exists to confirm MCF Gate M11 / PE-MC-2 grain-coherence check refuses cross-entity bindings"). | Operator picks the canonical name. Recommended: a deliberately non-collisional name like `Test Negative Entity` to avoid future-author collisions. |

Sufficient packet shape for both: BCF v1 `createEntity` packet (§3.1 of `bcf-enrichment-preflight-for-mcf-seed-cases.md`). Both runs are operator-driven; panel mechanically refuses if `entityNameMatches` is non-empty (per §4.5 collision risk is Low for both proposed names).

### 6.2 Phase B — Characteristics (option-dependent)

**B10 activation runs:** None required. All 7 slice-required F4-S1 characteristics are already `active` per §4.2.

**F4-v2 createCharacteristic runs:**

| | Option A | Option B (recommended) | Option C |
|---|---|---|---|
| `outstanding amount` | ✓ (1 run, operator-confirm) | — | — |
| `recognized amount` | ✓ (1 run, operator-confirm) | conditional (defer Metric 3 to Step-4-bis) | — |
| `billed amount` | ✓ (1 run, operator-confirm) | conditional (defer Metric 3 to Step-4-bis) | — |
| `invoice amount` | ✓ (1 run, operator-confirm) | conditional (defer Metric 6 to Step-4-bis) | — |
| `posted amount` | — | ✓ (1 run, operator-confirm, `industry_specific`-likely classification) | — |
| `clearing date` | — | optional (1 run, alternative to overloading `effective date`) | — |
| **Total** | **4 runs** | **1–2 runs (1 minimum)** | **0 runs** |

All createCharacteristic runs route through F4-v2 with C5 `operator_confirm_required` per BCF preflight §3.3. Each run carries a structured Vocabulary Admission Checklist answer in the recommendation per F4-v2 §M1-M10.

For each run, the operator supplies `candidateEvidence` citing the grounding source (recommended: APQC + relevant accounting standard for the option-A finance characteristics; SAP-OData published documentation or equivalent ERP reference for `posted amount`).

### 6.3 Phase C — Business Concepts (option-dependent count, common shape)

`createBusinessConcept` runs, one per BC. Packet per BCF preflight §3.2 carries `selectedEntity`, `existingConceptsForEntity`, `entityPlacementCandidates`, `activeCharacteristics`, `representationTerms`.

The full set of BCs the Step 4 slice references is enumerated below. The "Status under each option" columns indicate which BCs are authored under each operator decision.

| # | Entity | BC name | Characteristic | Rep term | Used by metrics | A | B | C |
|---:|---|---|---|---|---|:-:|:-:|:-:|
| 1 | Customer Invoice | outstanding amount | `outstanding amount` (new under A) | amount | 1, 2, 7, 9, 10 | ✓ | — | — |
| 1B | Customer Invoice | posted amount | `posted amount` (new under B) | amount | 1, 2, 7, 9, 10 (via filter) | — | ✓ | — |
| 2 | Customer Invoice | due date | `due date` (active) | date | 2, 5, 7 | ✓ | ✓ | — (Metric 5 yes, but Metric 5 in C only needs `posting date`+`due date`) |
| 3 | Customer Invoice | posting date | `posting date` (active) | date | 3, 5, 6 | ✓ | ✓ | ✓ (Metric 5) |
| 4 | Customer Invoice | status | `status` (active) | code | 4 | ✓ | ✓ | ✓ |
| 5 | Customer Invoice | status change date / effective date | `effective date` (active) | date | 4 | ✓ | ✓ | ✓ |
| 6 | Customer Invoice | invoice id | identifier role (panel decision; could use `line number` characteristic if document-position semantics; more likely a new identifier-role BC with no characteristic) | identifier | 4 | ✓ | ✓ | ✓ |
| 7 | Customer Invoice | invoice amount | `invoice amount` (new under A) | amount | 6 | ✓ | conditional (defer 6) | — |
| 8 | Customer Invoice | recognized revenue amount | `recognized amount` (new under A) | amount | 3 | ✓ | conditional (defer 3) | — |
| 9 | Customer Invoice | billed amount | `billed amount` (new under A) | amount | 3 | ✓ | conditional (defer 3) | — |
| 10 | Customer Invoice | clearing date | `clearing date` (new conditional under B) OR overload `effective date` | date | (under B's filter idiom) | — | conditional | — |
| 11 | Sales Order Line | discount | `discount` (active) | amount | 8 | ✓ | ✓ | ✓ |
| 12 | Sales Order Line | ordered quantity | `ordered quantity` (active) | quantity | 8 | ✓ | ✓ | ✓ |
| 13 | Negative-test Entity | (panel-decided, deliberately unreachable from any Step 4 metric grain) | (panel-decided) | identifier | none (negative test) | ✓ | ✓ | ✓ |

**Per-option BC counts:**

| Option | Customer Invoice BCs | Sales Order Line BCs | Negative-test BC | Total |
|---|---:|---:|---:|---:|
| A | 9 | 2 | 1 | **12** |
| B (minimum: Metrics 3 + 6 deferred, no separate `clearing date` BC) | 6 (rows 1B, 2, 3, 4, 5, 6) | 2 | 1 | **9** |
| B (maximum: Metrics 3 + 6 in scope, `clearing date` authored separately) | 10 (rows 1B, 2, 3, 4, 5, 6, 7, 8, 9, 10) | 2 | 1 | **13** |
| C | 4 (rows 3, 4, 5, 6) | 2 | 1 | **7** |

Each `createBusinessConcept` run is independent (one panel run per BC); per-run sequencing within Phase C does not matter once Phase A and Phase B prerequisites have landed.

### 6.4 Phase D — Acceptance checks

The slice is accepted when all of the following hold. Acceptance is the operator-recorded close criterion for the Step 4 enrichment session.

| # | Acceptance criterion | Source |
|---:|---|---|
| D1 | All Phase A entities are in `lifecycle_state = active` (B10-activated). | BCF B10 design + Step 4 §7.3 |
| D2 | All Phase B characteristics authored under the chosen option are in `lifecycle_state = active`. | Same |
| D3 | All Phase C BCs are in `lifecycle_state = active`. | Same |
| D4 | Every Step 4 §4 metric whose bindings the chosen option unblocks resolves cleanly: every variable_ref in the per-metric needs table (§5 of `mcf-step-4-first-representative-metrics-and-bcf-enrichment-slice.md`) names a live BC; every grain entity is live; every time-anchor source BC is live. | Step 4 §6.7 D criterion (a) + (c) |
| D5 | ≥1 BC per representation class required by the chosen option's unblocked metrics is in active state (amount, date, identifier, quantity; per option B add filter-handling for clearing-related BCs). | BCF preflight §6.2 + Step 4 §6.5 |
| D6 | The negative-test BC is live and is **NOT** in the bindings of any of the unblocked Step 4 metrics — confirms its negative-test purpose. | Step 4 §6.4 |
| D7 | No `concept_registry.supersession_proposal` row was created by any Phase A / B / C run (i.e. no existing concept was retired-and-replaced during enrichment). | BCF F3 substrate; live count 0 (§3.1) |
| D8 | The bc-postgres MCP allowlist + write discipline (§2.1) is unchanged after the session. | Operator verification at session close |

A live SELECT after Phase C completion against `entity`, `business_concept`, `characteristic` filtered by `lifecycle_state = 'active'` and the option's expected counts produces the acceptance evidence.

### 6.5 Slice scope summary (any option)

| Quantity | Option A | Option B (rec, min) | Option B (max) | Option C |
|---|---:|---:|---:|---:|
| Entities to author | 2 | 2 | 2 | 2 |
| Characteristics to author | 4 | 1 | 3 | 0 |
| BCs to author | 12 | 9 | 13 | 7 |
| Metrics unblocked | 10 | 8 | 10 | 3 |
| Failure cases unblocked (Metrics 9 + 10) | 2 | 2 | 2 | 0 |
| Total panel runs | 18 | 12 | 18 | 9 |

All four totals are well within the BCF preflight's stated envelope (~30 BCs across 3-5 entity families). See §8 for the v1 packet sufficiency re-check.

---

## 7. AST node coverage under each option

Cross-checks the chosen option against the Step 4 §4.x AST-node coverage summary (7-of-N nodes target).

| AST node | Metric exercising it | Option A | Option B (rec) | Option C |
|---|---|:-:|:-:|:-:|
| variable_ref / literal / aggregate / arithmetic | all metrics 1-10 | ✓ | ✓ | ✓ (subset) |
| window | Metric 5 | ✓ | ✓ | ✓ |
| time_anchor_resolution | Metric 6 | ✓ | conditional (defer 6 in min) | — |
| bucket_assign | Metric 7 | ✓ | ✓ | — |
| (case, others) | not exercised in Step 4 slice | — | — | — |

| Option | AST nodes exercised | Coverage vs Step 4 target |
|---|---|---|
| A | 7 of N (variable_ref, literal, aggregate, arithmetic, window, time_anchor_resolution, bucket_assign) | meets |
| B (min) | 6 of N (drops time_anchor_resolution) | acceptable; meet via Step-4-bis Metric 6 |
| C | 5 of N (drops time_anchor_resolution + bucket_assign + failure-case AST mechanics for Metrics 9 + 10) | does not meet; mandates Step-4-bis |

---

## 8. BCF v1 packet sufficiency re-check + B6-v2 trigger monitoring

Re-runs the BCF preflight §5 + §8 sufficiency check against the live-evidenced slice. Verdict carries from preflight: **v1 packet is sufficient**, with the same trigger conditions monitored during enrichment.

### 8.1 Per-operation sufficiency (carried + spot-checked against live evidence)

| Operation | Live counts to be sent per packet | Per-run packet capacity | Sufficiency |
|---|---|---|---|
| `createEntity` (Phase A1, A2) | `entityNameMatches` for "Customer Invoice" and the negative-test name — expected 0 each (per §3.2 + §4.5 collision check). | Carries candidate + entityNameMatches only. Packet size: < 5 KB. | ✓ |
| `createBusinessConcept` (Phase C) | `selectedEntity` + `existingConceptsForEntity` (target entity has 0-1 existing BCs in the live registry) + `entityPlacementCandidates` (0 expected) + `activeCharacteristics` (26 rows × ~150 chars ≈ 4 KB) + `representationTerms` (15 rows × ~60 chars ≈ 1 KB). Packet size: < 20 KB. | Bounded; well within v1 envelope. | ✓ |
| `createCharacteristic` (Phase B) | `activeCharacteristics` (26 rows) + `representationTerms` (15 rows). Packet size: < 10 KB. | Bounded. | ✓ |

The largest packet (`createBusinessConcept` ~20 KB) is comfortably under any wire threshold. T-H3 (active characteristic vocabulary >50 × wire bloat) does not fire even after the maximum-Option-A run (26 + 4 = 30 characteristics).

### 8.2 Hard-trigger re-check (BCF preflight §5.1)

| # | Hard trigger | Status under live-evidenced slice |
|---|---|---|
| T-H1 | Cross-entity disambiguation load-bearing | NOT TRIGGERED — Customer Invoice BCs are clearly per-entity; Sales Order Line BCs are clearly per-line. |
| T-H2 | Source-reality grounding PE-MC-1-mandatory for the BC class | NOT TRIGGERED — Step 4 proceeds with operator-supplied candidateEvidence per BC. |
| T-H3 | Active characteristic vocabulary wire-size threshold | NOT TRIGGERED — 26 active today; max post-A = 30. |
| T-H4 | bc-ai acquires free-query Registry tool | NOT TRIGGERED — L1 lock preserved this session. |

### 8.3 Soft triggers — none surfaced

T-S1 through T-S4 (BCF preflight §5.2) — none surfaced under the live-evidenced slice.

### 8.4 Verdict

**BCF v1 bounded packet is sufficient for the Step 4 enrichment slice under any of Option A / B / C.** No B6-v2 workbench retrofit is required to open Step 4 enrichment.

### 8.5 Trigger monitoring during enrichment

During Step 4 enrichment, the operator monitors for any of:

- A `createBusinessConcept` proposal where the operator-chosen `targetEntityId` is non-obvious — i.e. the proposed BC could plausibly belong to two of the slice's entities. (T-H1)
- A characteristic-class-wide operator decision that every BC of that class must cite a specific source contract / OC field in `candidateEvidence`. (T-H2)
- A characteristic vocabulary growth that pushes packet size past comfort (unlikely; would require ≥50 active chars). (T-H3)
- Any proposal to give bc-ai a free Registry query path. (T-H4)

If any of these surfaces, **stop enrichment and open B6-v2** before continuing.

---

## 9. Risks and stop conditions

Carried + updated from Step 4 §9 to reflect live findings.

### 9.1 Risks updated against live coverage

| # | Risk (carried from Step 4 §9 or new this plan) | Updated severity | Mitigation |
|---|---|---|---|
| R-A | `outstanding amount` F4-S1 §6 deferral is load-bearing for Metrics 1, 2, 7, 9, 10 (corrected count vs Step 4 §5.x). | High | §5 operator decision; recommendation is Option B. |
| R-B | F4-S1 24 characteristics' per-row lifecycle state may be `draft` — blocks BC authoring. | **RESOLVED POSITIVE** (§4.2): all 24 F4-S1 cohort rows + 2 post-F4-S1 are `active`. No Phase B activation prerequisite. |
| R-C | `invoice id` representation-term + characteristic choice ambiguous. | Low | Panel decision at Phase C / BC #6 createBusinessConcept run; `line number` characteristic is a candidate, but identifier-role with panel-judged characteristic is more likely correct. |
| R-D | Metric 6 (fiscal_period) depends on D365 `posting_date_field` landing. | Medium for Metric 6 only | Per Option B (recommended), Metric 6 is deferred to Step-4-bis; D365 readiness is checked at Step-4-bis opening. |
| R-E | Negative-test entity naming collisions with future-author entities. | Low | Operator names with deliberately non-collisional name (e.g. `Test Negative Entity`). |
| R-F | `recognized amount` / `billed amount` / `invoice amount` Vocabulary Admission Checklist may route to operator-confirm and slow Step 4. | Medium under Option A; bypassed under recommended Option B. | Operator anticipates the routing under A; B avoids by deferring 3 + 6. |
| R-G (new) | Step 4 §5.x "Metrics 2, 4, 5, 7, 8, 9, 10 are not affected" parenthetical was incorrect (corrected in §4.3 of this plan to Metrics 4, 5, 8 only). Operators reading Step 4 alone may pick Option C expecting 7-of-10 coverage. | Medium | This plan §4.3 + §5.3 + §6.5 makes the corrected arithmetic explicit. Option C under-delivers (3-of-10) and is not recommended in isolation. |
| R-H (new) | bc-postgres MCP `pg_count` / `pg_list_tables` tool bug (§2.2) could mislead a future operator into thinking the schema is not allowlisted. | Low (workaround documented). | `pg_query` works correctly; bc-pg-mcp owner should fix. |
| R-I (new) | `clearing date` semantics under Option B may be overloaded onto existing `effective date` characteristic (Medium collision risk per §4.5). | Medium under Option B | Operator + panel decide whether to author `clearing date` separately (+1 createCharacteristic run) or overload `effective date`. |

### 9.2 Hard stop conditions during enrichment

Carry directly from BCF preflight §5.1 + Step 4 §9.2. If any T-H trigger fires during enrichment, **stop enrichment and open B6-v2 retrofit** before continuing.

### 9.3 What this plan explicitly does NOT recommend

- Does **not** recommend opening MCF M3.
- Does **not** recommend applying MCF M2 DDL.
- Does **not** recommend opening B6-v2 retrofit (no hard trigger fires under any option).
- Does **not** recommend skipping the Phase A → B → C → D order.
- Does **not** recommend authoring any concept this session — `concept_registry.*` writes remain disabled.

---

## 10. Recommended next gate

### 10.1 Immediate next: open Step 4 enrichment session

The two acts Step 4 §10.1 named as session-openers are both resolved:

| Step 4 opener act | Status |
|---|---|
| bc-postgres allowlist expansion to include `concept_registry` | ✓ landed before this session opened |
| Operator decision on §5.x (`outstanding amount`) | Framed in §5 of this plan with 3 options + recommendation + exact per-option enrichment impact; operator records decision at Step 4 enrichment session opening |

When the operator opens Step 4 enrichment:

1. Operator records the §5 option chosen (A / B / C).
2. Phase A: 2 `createEntity` runs per §6.1.
3. Phase B: F4-v2 `createCharacteristic` runs per §6.2 column for the chosen option (4 / 1-3 / 0 runs).
4. Phase C: `createBusinessConcept` runs per §6.3 column for the chosen option (12 / 9-13 / 7 runs).
5. Phase D: acceptance checks per §6.4 (D1-D8).

### 10.2 What follows Step 4 enrichment

When Step 4 enrichment lands and acceptance D1-D8 passes:

- If Option B (recommended) and Metrics 3 + 6 deferred: open **Step-4-bis** to author the deferred metrics under either A-shaped or B-shaped enrichment for the missing characteristics.
- If Option C: open **Step-4-bis** to author the 7 deferred metrics under A-shaped or B-shaped enrichment.
- If Option A: no Step-4-bis required; move to **MCF M2 DDL apply** (separate operator-authorized session under Database Change Protocol) and then **MCF M3 onwards** per build plan §4.

### 10.3 What stays closed after this pre-execution plan commits

- **MCF M3** — closed per operator instruction; stays closed.
- **MCF M2 DDL apply** — closed; stays closed until operator approval under Database Change Protocol (separate session).
- **BCF B6-v2 retrofit** — closed; no hard trigger fires (§8.2).
- **Step 4 enrichment itself** — closed until operator authorizes a Step 4 enrichment session.
- **`concept_registry.*` writes** — disabled per `pg_server_info` (§2.1); stay disabled.
- **MC creation** — closed; MCF authoring is downstream of Step 4 + later MCF gates.

---

## Document verification

- **All 10 required sections present** (§1 Scope; §2 Verification gates; §3 Live coverage; §4 Coverage vs Step 4 assumptions; §5 `outstanding amount` operator decision; §6 Execution-ready enrichment plan; §7 AST node coverage; §8 BCF v1 packet sufficiency re-check; §9 Risks and stop conditions; §10 Recommended next gate).
- **Live evidence cited inline** — every coverage claim in §3 cites the exact SELECT executed this session against `concept_registry.*` under the expanded allowlist.
- **Three-option operator decision framed** — §5 enumerates A (author), B (compose, recommended), C (defer) with exact per-option enrichment impact in Phase A / B / C / D run counts (§6.5).
- **Recommendation explicit** — Option B (compose `outstanding` via MCF AST filter; author `posted amount` as the one new characteristic; defer Metrics 3 + 6 to Step-4-bis). Conditions for the recommendation to hold are listed (§5.5).
- **Discipline assertions all hold** (§1.4) — no writes performed; no `concept_registry.*` create or modify; no MCF M2 DDL apply; no MCF M3 open; no B6-v2 open; no MC creation.
- **BCF v1 packet sufficiency re-checked** against live counts and verdict carried from preflight (§8.4): v1 sufficient under any option; no B6-v2 trigger fires.
- **Pre-execution corrections recorded** — Step 4 §5.x's "Metrics 2, 4, 5, 7, 8, 9, 10 are not affected" parenthetical is corrected in §4.3 against Step 4 §5's per-metric needs tables. Step 4 §7.3's contingent-B10-activation prerequisite is resolved positive in §4.2.
- **Tool-bug note** — bc-pg-mcp `pg_count` / `pg_list_tables` `column "tablename" does not exist` bug logged (§2.2); workaround via `pg_query` documented.
- **No code changes, no DDL, no DB writes.** Doc-only commit.
