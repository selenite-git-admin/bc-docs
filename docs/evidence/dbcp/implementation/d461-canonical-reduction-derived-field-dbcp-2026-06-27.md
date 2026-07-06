---
uid: d461-canonical-reduction-derived-field-dbcp-2026-06-27
title: D461 Canonical Reduction — Derived Canonical Fields (post-BCR re-home of D330)
description: Design proposal for the canonical-reduction capability — derived canonical fields (date_diff / date_diff_as_of) produced at the canonical boundary, re-homing the orphaned D330 compute mechanism onto the surviving canonical_mapping, with a transitively-observability-aware PE-MC-11 / D431 gate. Proposes; applies nothing. No DDL.
status: draft
date: 2026-06-27
project: bc-core
domain: contracts
subdomain: canonical-reduction
focus: derived-canonical-field
governing_adrs:
  - DEC-bc6be2 (D461) — canonical-reduction capability authorization (sequencing override of DEC-a7fe72; "the later time is now")
  - DEC-637072 (D330) — Derived Canonical Fields / compute (implemented, host table retired)
  - DEC-02f5a9 — Business Concept Registry (field_selection / metric_binding retargeted to Business Concepts; Canonical Mapping identity layer eliminated; resolution logic survives in contract bodies)
  - DEC-6c57e2 (D417) + DEC-a19428 (D418) — Gate 5.2 retirement of BF/BO/CF/cc_field_mapping
  - DEC-1002c9 (D439) — G3 Source-Chain Resolvability Gate (legacy PE-MC-11)
  - DEC-4a17e0 (D431) — Observation field identity (O↔C consistency)
  - DEC-a6258b (D430) — Canonical field semantic identity
depends_on:
  - the-invariants
  - the-evaluation-boundaries
  - the-contract-grammar
  - canonical-evaluation
governing_sources:
  - bc-docs-v3/docs/foundation/the-evaluation-boundaries.md (Canonical evaluation boundary; boundary-independent rules)
  - bc-docs-v3/docs/operating-model/canonical-evaluation.md (Resolution rules at runtime; "reduce one or more mapped Business Field inputs into one resolved value per selected Canonical Field")
---

# D461 Canonical Reduction — Derived Canonical Fields (post-BCR re-home of D330)

> Implements toward **DEC-bc6be2 / D461** — the canonical-reduction capability. Re-homes the **proven-but-orphaned** D330 compute mechanism (`compute-evaluator.ts`, already merged + unit-tested) into the post-BCR substrate, so a Canonical Object can carry a field whose value is **computed from observed fields at the canonical boundary** (e.g. `collection_lag_days = clearing_date − due_date`; `days_past_due = as_of − due_date`), while the metric engine continues to see a plain numeric column.
> Grounding: `docs/foundation/the-evaluation-boundaries.md` (canonical boundary "resolves semantic state"), `docs/operating-model/canonical-evaluation.md` (resolution "reduce[s] one or more mapped Business Field inputs into one resolved value per selected Canonical Field").
> **This document PROPOSES. It applies no code, no DDL, no data. Operator LOCK required before any PR.**

> ## ⚠ FOUNDATION CORRECTION — DEC-7d2f8c (D462), 2026-06-28 — READ BEFORE EVERYTHING BELOW
>
> A 100%-Foundation re-read (the-invariants, the-evaluation-boundaries, the-contract-grammar, in full) found that **L2 and L3 below, and DEC-bc6be2's observation-boundary `date_offset` mechanism, contradict the Foundation.** Neither was implemented, so the correction is clean. **DEC-7d2f8c (D462) is the authority; where this doc disagrees, D462 wins.**
>
> 1. **Derivation home = the Canonical Contract body, not `canonical_mapping` (superseded, DEC-02f5a9) and not the Observation Contract.** Invariant I: meaning is produced once **at the canonical boundary, by the CC**. The grammar lists "an Observation Contract declares canonical evaluation logic" as a **disallowed** behavior — so DEC-bc6be2's "due date derived at the observation boundary" is an Invariant-I violation. The OC observes (`baseline`, `terms`); the **CC** derives. **L2 is superseded.**
> 2. **One hop only at the canonical boundary.** A derived canonical field's compute inputs must be **directly observed** Business Concepts — never themselves derived ("resolution across Source Objects"; Invariant II "no hidden derivation"; anti-pipeline). The CS-3 gate is **1-hop, not transitive** (drop the recursion + cycle guard). **L3 is superseded.**
> 3. **Cross-concept comparison where an input is itself derived → the metric boundary**, via the Foundation-sanctioned **secondary-metric DAG**. `collection_lag = date_diff(clearing, due)` with `due` derived is a **metric** op, not a canonical field. `due = date_add(baseline, terms)` is a valid **1-hop CC** derived field.
> 4. **Worked split:** `clearance_time = date_diff(clearing, document)` — both inputs directly observed → **1-hop canonical field + plain AVG metric** (the clean first proof). `collection_lag` — `due` derived → **1-hop canonical `due` + metric DAG** for the subtraction/average (resolves CB-005/CB-006 without canonical chaining).
>
> L1 holds only for the 1-hop case; the 2-hop case is a metric op (3). L4 (D330 library) holds. The mechanism sections below (CS-1 `canonical_mapping`, CS-3 transitive) are **superseded by D462** — re-read them as: CS-1 → a `compute` resolution element **in the CC body**; CS-3 → **1-hop** input-observability.

## 0. Build status + findings (2026-06-28 — build paused mid-step-3 for a careful fresh-session completion)

**Locked + partially built. Three findings refine the design below — read this section first.**

**DONE + VERIFIED:**
- **CS-3 (PE-MC-11 gate)** — transitive-observability built in `mcf-chain-resolution.ts` (`isConceptObservable`, cycle-guarded) + reader (`readActiveCanonicalComputeResolutions`) + evaluator wiring + fingerprint. **116 mcf unit tests green.**
- **Name-check defect fix** — `name-conflict.checker.ts` `assertCharacteristicTermAvailable` lacked an `archived_at IS NULL` filter, so a **withdrawn characteristic permanently blocked its own term**. Fixed (added `isNull(characteristic.archivedAt)`); 15/15 spec green; proven live. Standalone bug; commit with D461.
- **Panel-backed vocabulary (rigorous, per operator choice)** — authentic B6 panel run `d7500d06` (improved genus/differentia definition + external SAP BSAD evidence). Active: characteristic `collection lag` = `03bf4ac3`, concept `collection_lag_days` = **`850f69d4`** (`value`/`descriptive`/`measure`/`integer`/`days`, entity `e3963e45`). The earlier operator-direct attempts (`aad0f03f`/`a6b55479`) are archived. **Use `850f69d4` downstream.**

**FINDING A — architecture refinement (operator-adjudicated).** The B6 panel split on base-vs-derived (Maker: metric-layer DSO-shape; Checker: base single-instance duration). The operator adjudicated: **`collection_lag` is a BASE concept whose PRODUCTION is source-dependent** — directly *observed* where a source emits it, *canonically computed* (the D461 reduction) where the source emits only the inputs (SAP BSAD). This is the source-agnostic Canonical Object: the metric binds one concept and never learns the production path. The registry describes the concept's *meaning* (base), not its *production*. This sharpens L1 and is the strongest justification for D461 + CS-3 (which proves a concept observable-**or**-derivable).

**FINDING B (CRITICAL) — CS-3 / L3 is INCOMPLETE.** The D431 O↔C rule ("every CC field concept must be observable from an active OC") is enforced at **multiple points**; CS-3 only made the **PE-MC-11 gate** transitive. The **CC-authoring path has its own D431 check** — `contract.service.ts:395` `this.observationResolver.assertConceptsObservableFromSource(this.canonicalConceptIds(body), 'canonical-v2 authoring')` (`ObservationConceptResolverService`) — which is **not** transitive and **refused** the derived field at CC-version creation (`403 D431 O↔C: business_concept 850f69d4 … not declared observable … refused (DEC-4a17e0)`). **L3 is hereby widened: the transitive treatment must extend to ALL D431 enforcement points** — (1) **CC-authoring** `assertConceptsObservableFromSource` [REQUIRED, not yet done], (2) PE-MC-11 `buildOcNode` [DONE], (3) **audit** the OC/CC activation path (`contract.service.ts transitionState`) for a third point. Reuse the `isConceptObservable` transitive logic verbatim. This is integrity-critical governance code — extend it carefully + tested.

**FINDING C — corrected build order.** The compute resolution must exist *and* `due_date` must be observable **before** the CC-authoring check runs. The real order is:
1. Slice-widen `due_date` (`b49aa30e`) into the BSAD OC (`019ebef7`, new OC version) → `due` observable.
2. Author the compute resolution in `canonical_mapping` (`collection_lag_days 850f69d4 = date_diff(end=clearing 5fe49908, start=due b49aa30e, unit=days)`).
3. **Extend the CC-authoring D431 check to be transitive** (Finding B) + audit activation.
4. Author **CC v6** of `cc__customer_invoice_arpi_slice` (`019eaf31`, v5 has 9 fields) — `field_selection += collection_lag_days` — via `POST /api/contracts/:id/versions` (full envelope) → submit → approve → activate.
5. Re-author **MCV `3de1770a`** (currently `avg(minus(clearing, due))`) → `avg(collection_lag_days)` binding `850f69d4` (`mcf-mcv-supersede`).
6. Re-run PE-MC (`POST /api/mcf/metric-contracts/8135363f/evaluate-publication-eligibility`) → expect OC leg PASS via the transitive proof → **activate** with independent verification.

**Commit all D461 code together** (CS-3 gate + name-check fix + the new CC-authoring transitive extension). All code is currently **uncommitted**.

## 1. Decision recap (operator-locked 2026-06-27)

- **L1** — The per-row date arithmetic (`clearing − due`, `as_of − due`) is a **canonical derived field**, not a metric-formula computation. (Foundation: a per-invoice collection-lag is canonical-grain business meaning; D330 Option C — date math in MC formula — was rejected as source-coupling.)
- **L2** — The derivation is declared **via `canonical_mapping`** as a new `compute` field-resolution kind. **No CC-body grammar version bump** ("no new grammar"). This re-homes D330's `compute_json` from the retired `cc_field_mapping` onto the surviving platform-scoped `canonical_mapping`.
- **L3** — The PE-MC-11 / D431 chain-integrity gate becomes **transitively observability-aware**: a derived canonical concept is proven not by appearing in an OC, but by its **compute inputs each being observable**. The gate change **preserves** the integrity guarantee (the chain can produce every CO concept) — it does not relax it.
- **L4** — The compute function library is **exactly D330's** (`date_diff`, `date_diff_as_of`, `row_count`, `row_count_where`, `sum_where`), grows additively by ADR only. The evaluator is the already-merged `src/registry/compute-evaluator.ts`.

## 1a. Locked grammar shape (D462) — CC-body `derivations[]` (built 2026-06-28)

Per D462 the derivation lives in the **Canonical Contract body**, as a new **optional, additive** `derivations[]` element in `canonical-v2.schema.json` (master shape; backward-compatible — existing CCs omit it). It is **distinct from `resolution_rules`** (which resolves conflicts when N SOs contribute the *same* field): a derivation produces a *new* field from *other* fields. The derived field's concept **also** appears in `field_selection` (identity anchor); `derivations[]` declares how it is produced. Worked shape for the clearance_time proof:

```jsonc
"field_selection": [ /* … existing fields …, plus: */
  { "canonical_field": "clearance_time", "business_concept_id": "<clearance_time concept>",
    "representation_term": "measure", "unit": "days", "data_type": "integer" }
],
"derivations": [
  {
    "canonical_field": "clearance_time",
    "output_business_concept_id": "<clearance_time concept>",   // == the field_selection entry's concept
    "function": "date_diff",                                    // ∈ D330 library (L4)
    "inputs": [
      { "role": "end",   "business_concept_id": "<clearing date concept 5fe49908>" },   // directly observed
      { "role": "start", "business_concept_id": "<document date concept 8cbd57be>" }    // directly observed
    ],
    "output_type": "integer",
    "params": { "unit": "days" }
  }
]
```

**1-hop gate (CS-3, built + verified):** the shared `isConceptObservable` (`src/registry/concept-observability.ts`) proves `clearance_time` producible iff **every** input concept (`clearing`, `document`) is **directly** in an active OC — no recursion, no chasing a derived input. Both compute readers (`mcf-chain-declaration-reader.readActiveCanonicalComputeResolutions`, `observation-concept-resolver.computeResolutionsByOutput`) now read `contract_json->body->derivations` from the active CC, **not** `canonical_mapping`. Unit-verified: 56 gate/resolver specs + 80 evaluator specs green; `tsc` clean.

## 2. Live substrate grounding (read-only, 2026-06-27, `bc_platform_dev`)

| Surface | Live fact | Source |
|---|---|---|
| Active Customer Invoice CC | `cc__customer_invoice_arpi_slice` v5.0.0 — 9 `field_selection` fields; declares `clearing_date` (concept `5fe49908…`), **does NOT declare `due_date`** | `contract.canonical_contract_version` |
| `due date` concept | **active**, `value`/`descriptive`, `date`, on the Customer Invoice entity `e3963e45…` — concept `b49aa30e…`. Directly observable; simply not selected. | `concept_registry.business_concept` ⨝ `characteristic` |
| `clearing date` concept | active, concept `5fe49908…`, same entity; selected by CC and mapped by OC | same |
| Active Customer Invoice OCs | `oc__…_cleared_item_bsad` v3 maps `clearing_date` (`5fe49908`) but **NOT `due_date`** (`b49aa30e`); `oc__…_type_sd_s_map` v3 maps neither | `contract.observation_contract_version` |
| `canonical_mapping_version` | **0 rows (empty)** — vestigial for MCF slices; the OC→CC concept chain is body-resident by shared `business_concept_id` (DEC-02f5a9) | `contract.canonical_mapping_version` |
| `mapping_json` column | `jsonb NOT NULL`, **no structural CHECK constraint** — a `compute` field-resolution is additive JSON content | `pg_describe_table` |
| D330 evaluator | `src/registry/compute-evaluator.ts` present, unit-tested, **NOT wired** into `canonical-resolution.service.ts` (only a hard-coded `total_debit`/`total_credit`/`is_balanced` stub) — orphaned when `cc_field_mapping` was retired (D417/D418) | code read |
| PE-MC-11 gate reads | CC `field_selection` concepts + ⋃ OC `field_mappings` concepts, from contract **bodies** — never reads `canonical_mapping` | `mcf-chain-declaration-reader.ts` |

### 2a. ⚠ The two gaps are at different layers — do not conflate

"Average Days to Collect" = `AVG(clearing_date − due_date)` is blocked by **two distinct gaps**:

1. **Slice-widening (observable):** `due_date` is an **active, directly-observable** concept the BSAD source carries — it is just not selected into the OC + CC. Producing it by a *reduction* would be lower-layer compensation for an observable (**Invariant I**; gate Q3). **Fix = ordinary onboarding** (map `b49aa30e` in the BSAD OC `field_mappings`; select it in the CC `field_selection`). This is the F1-B1 invoice-slice widening (TSK-ca5dd3) and is a precondition, not part of the new capability.
2. **The derivation (genuinely computed):** the *duration* `clearing − due` (and the moment-dependent `as_of − due`) is not expressible in any current grammar. **This** is the capability D461 builds.

## 3. Orphaned-capability context (why this is a re-home, not an invention)

D330 (DEC-637072, *implemented* 2026-04-15) built derived canonical fields: a `compute` resolution rule + `compute_json` on `cc_field_mapping`, a typed function library, evaluation at canonical-resolution time, and a chain-integrity extension proving compute inputs ∈ `field_selection`. Gate 5.2 (D417/D418) **physically retired `cc_field_mapping`**; DEC-02f5a9 replaced the BF/CF/mapping layer with the Business Concept Registry and **eliminated the Canonical Mapping identity layer**, but explicitly preserved the *intent* (§2: "reduction over grain … remain[s] authored content within the Observation and Canonical Contracts"). **No successor mechanism was ever specified.** The evaluator module survived as an orphan. D461 re-homes the capability; the evaluator and its input-observability validator are reused verbatim.

## 4. Change set (proposed — nothing applied here)

The capability splits into **Phase 1 (declaration + gate → unblocks activation)** and **Phase 2 (runtime evaluator → produces numbers)**. The immediate "Average Days to Collect" blocker is *activation* (PE-MC-11 reject), which Phase 1 alone clears. Phase 2 is coordinated with the Bar-2 / D429 runtime crossing.

### CS-1 — `compute` field-resolution grammar in `canonical_mapping.mapping_json` (repair-location **B/C**) · Phase 1

Extend the `mapping_json.field_resolutions[]` vocabulary with a `compute` resolution that produces a derived canonical field's concept from input concepts:

```jsonc
{
  "resolution_kind": "compute",
  "output_canonical_field": "collection_lag_days",
  "output_business_concept_id": "<derived concept uuid>",   // the CC field_selection concept it produces
  "function": "date_diff",                                   // ∈ D330 library (L4)
  "inputs": [
    { "role": "end",   "business_concept_id": "<clearing date concept>" },
    { "role": "start", "business_concept_id": "<due date concept>" }
  ],
  "output_type": "integer",
  "params": { "unit": "days" }
}
```

- Inputs reference **business_concept_ids** (post-BCR vocabulary), not BF names (D330 used BF names on the retired `cc_field_mapping`). The evaluator's per-row payload is keyed by canonical_field; a thin adapter resolves concept_id → the payload key the OC produced.
- `output_business_concept_id` MUST be a concept the CC `field_selection` selects, and MUST NOT appear in any OC `field_mappings` (it is derived, not observed — see CS-3).
- Additive JSON content. **No DDL** (`mapping_json` is unconstrained `jsonb`). **No CC-body grammar change.**

### CS-2 — derived-concept representation in the BCR (repair-location **B**) · Phase 1

The derived field needs a governed concept so (a) the CC `field_selection` can select it and (b) the Metric Contract can bind it (DEC-02f5a9: metrics bind concepts). **It is a plain `value`/`descriptive` concept** (e.g. `collection lag days`, `integer`, unit `days`) — **no new BCR `kind`, no new BCR grammar.** "Derived vs observed" is **not** a property of the concept (the BCR describes *meaning*); it is a property of the **contract layer** — the concept is the output of a CS-1 compute resolution and is absent from every OC. Authored via the governed BCR authoring / operator-direct path (same surface as the finance identity work), never raw SQL.

### CS-3 — transitive-observability PE-MC-11 / D431 gate (repair-location **D**) · Phase 1 · **the integrity-critical change**

Today `buildOcNode` (`mcf-chain-resolution.ts`) rejects unless **every** CC `field_selection` concept ∈ `activeOcConceptIds`. A derived concept is never in an OC → false reject. Make the gate transitive:

1. `McfChainDeclarationReader` gains `readActiveCanonicalComputeResolutions()` → `Map<outputConceptId, inputConceptIds[]>` read from active `canonical_mapping` `compute` resolutions. (This is the one place the gate must read `canonical_mapping`; justified because a derived concept's producibility is undeclarable from the bodies alone.)
2. `buildOcNode` computes the **required-observable set**:
   `required = (all CC field concepts) − (compute output concepts) ∪ (compute input concepts)`
   and asserts `required ⊆ activeOcConceptIds`. A derived concept is dropped from the requirement **only when** its inputs are themselves in the requirement (recursively closed; reject on any compute whose output is selected but whose inputs are not transitively observable).
3. **Per-OC tightening (correctness, not optional):** the runtime computes a derived field from one source payload, so a compute's inputs must be observable in the **same OC** that carries the compute, not merely in the global ⋃. CS-3 verifies inputs against the OC the `canonical_mapping` binds, not the union. (Current `readActiveOcConceptIds` returns the global ⋃; CS-3 adds a per-OC variant for compute inputs.)

**Guarantee preserved (L3):** after CS-3, every concept a CO carries is either directly observable (in its OC) or computed from concepts that are — the proof is *transitive*, never dropped. Failure modes still REJECT (Q1 lock: no amber/review at this layer).

### CS-4 — runtime evaluator wiring (repair-location **D**) · Phase 2 (Bar-2 / D429-coordinated)

Wire `evaluateCompute` into the canonical resolution runtime so the derived field materializes per-row before metric aggregation (D330-R4 execution order). In the legacy boundary service this generalizes `canonical-resolution.service.ts::computeDerivedFields` (replacing the hard-coded debit/credit stub with a `compute`-resolution-driven call). **Whether MCF metrics resolve through this service or the nascent D429 projection path is unconfirmed** — Phase 2 is explicitly gated on that crossing and is out of scope for the activation unblock. Phase 1 does not depend on CS-4.

### CS-5 — governed write path for `compute` resolutions (repair-location **C**) · Phase 1

A governed onboarding surface to author a `compute` field-resolution into `canonical_mapping` (D330-R5 analog: no raw SQL, versioned, audited). Scope: one resolution at a time, one-then-many discipline.

## 5. Why no DDL (scope fidelity)

`canonical_mapping_version.mapping_json` is unconstrained `jsonb`; the `compute` resolution is additive content. The derived concept is authored through the governed BCR path (existing tables, existing service). The CC and OC bodies gain field selections / mappings for **existing or newly-authored concepts** — JSONB content, not schema. **Zero `CREATE`/`ALTER`/`DROP`, zero migration file, zero Drizzle change, zero trigger, zero direct data write.**

## 6. Database Change Protocol classification

**Code + governed-write only. No schema change.** Per the Database Change Protocol this still requires **no DDL approval** because there is no DDL; all substrate writes (the derived concept, the OC/CC field edits, the compute resolution) go through governed services with quality gates. No DB hand-edits, no backdoor inserts.

## 7. Proof slice — "Average Days to Collect" (one-then-many)

1. **Precondition (slice-widen, §2a.1):** map `due date` (`b49aa30e`) in `oc__customer_invoice_cleared_item_bsad` `field_mappings`; select it in `cc__customer_invoice_arpi_slice` `field_selection`. Verify `due_date` now ∈ `activeOcConceptIds`.
2. **CS-2:** author the `collection lag days` derived concept (integer/days) on the Customer Invoice entity; activate.
3. **CS-1 + CS-5:** author the `compute` resolution `collection_lag_days = date_diff(end=clearing_date, start=due_date, unit=days)` for the BSAD mapping.
4. **CS-3:** re-run PE-MC-11 for the Average Days MCV (live id to confirm: **3de1770a**) — the OC leg must now pass via the transitive proof (clearing + due observable ⇒ collection_lag_days producible).
5. **Activate** the MCV. Independent verification: read the persisted PE-MC result + the chain-status row; do not treat script output as proof.
6. **Confirm the rejected MCV's actual bindings first** (it may bind the two observed concepts and subtract in-formula, or bind the derived concept). If it currently subtracts in-formula, re-author it to `AVG(collection_lag_days)` per L1. *(MCV body lives in `mcf.*`, outside the read-only DB allowlist — pull via the bc-core MCF API before building.)*

## 8. Foundation gate

- **Repair location: B (primary)** — the canonical grammar cannot *express* a derived field (canonical-v2 has no derivation declaration; D330's was orphaned). CS-1/CS-2 add the missing declaration grammar + vocabulary. Secondary **C** (declaration home = `canonical_mapping`) and **D** (gate + runtime).
- **Q1 — why here:** the meaning "collection lag / days past due" is *produced* at the canonical boundary (Invariant I: meaning evaluated once, at its boundary). It is neither admitted (the source does not emit it — for `as_of` it *cannot*) nor a population metric.
- **Q2 — why not upper layers:** the *observable* part (`due_date`) **is** fixed upstream by slice-widening (A/B) — not compensated by a reduction. Only the genuinely-derived duration is fixed at B/C/D. A and B are not underspecified for the observable; they are underspecified for the *derivation*, which is exactly what we add.
- **Q3 — why not lower layers:** computation is **not** pushed into SDG (A) or fact rows (E) — D330 Option D rejected that (moment-dependency for `as_of`; source-coupling; ownership boundary). The reduction belongs at the canonical boundary.
- **Hard rule honored:** no lower-layer compensation for an upper-layer semantic gap — the B-grammar gap is fixed *at B*, and the gate change (CS-3) **proves inputs are observable** rather than dropping the proof.
- **Invariants:** I (meaning once, at the canonical boundary) ✓; II/IV (inputs are declared upstream concepts; references explicit) ✓; VI (evidence emitted at the evaluation act; the gate is read-only and triggers no evaluation) ✓.

## 9. Gates / rollback

- **Gates:** `npx vitest run` (compute-evaluator already covered; add CS-3 transitive-gate cases incl. the reject-when-inputs-unobservable and per-OC cases); `tsc` + ESLint (pipeline-dir limits: gate code is registry/mcf, 60-line/3-depth; canonical-resolution is `boundary/` — 40-line/2-depth/zero-console if CS-4 touched). No mock-heavy tests (D082).
- **Rollback:** Phase 1 is code + governed JSON content — `git revert` the gate/grammar PR; un-author the compute resolution + derived concept via the governed supersede/withdraw path. No schema to roll back. The slice-widening (§7.1) is independently reversible and independently valuable.

## 10. Out of scope

- **Terms-code → days conversion / lookup joins** (SD/billing `Z001` → 30 days) — D330 explicitly forbade lookups in v1; the SD path cannot source a due date by arithmetic and is not addressed here.
- **Cross-CC / CO-from-CO (Tier-2) derivation** — `canonical-evaluation.md` defers it pending a Foundation update; D461 is Tier-1 intra-source reduction only.
- **The MCF runtime crossing itself** (Bar-2 / D429 projection) — CS-4 depends on it; Phase 1 does not.
- **Rolling-window / population aggregations** — metric-engine territory.

## 11. Locked decisions (2026-06-27)

| # | Decision | Status |
|---|---|---|
| L1 | Date arithmetic is a canonical derived field, not MC-formula math | **AMENDED by D462** — true only for the **1-hop** case (all inputs directly observed). Cross-concept comparison with a *derived* input is a **metric** op (secondary-metric DAG). |
| L2 | Declared via `canonical_mapping` `compute` resolution; no CC-grammar bump | **SUPERSEDED by D462** — derivation lives in the **CC body** (`canonical_mapping` is superseded, DEC-02f5a9; OC may not declare canonical logic). |
| L3 | Gate becomes transitively observability-aware; guarantee preserved | **SUPERSEDED by D462** — gate is **1-hop**: a derived field's compute inputs must be **directly** observed, never themselves derived. |
| L4 | Function library = D330's, evaluator reused verbatim | LOCKED |
| — | Phase split (declaration+gate = activation unblock; runtime = Bar-2) | proposed — confirm at review |
| D462 | Derivation home = CC body, 1-hop; cross-concept-with-derived-input = metric boundary (DAG); corrects DEC-bc6be2 + L2/L3 | **LOCKED** (DEC-7d2f8c) |

## 12. PR shape (after final review)

Branch off `main`. **Phase 1 PR:** CS-2 (derived concept, governed) → CS-1 grammar + CS-5 write path → CS-3 transitive gate + tests → proof slice §7 (slice-widen, author compute, re-PE-MC, activate) with independent verification. **Phase 2 PR (separate, Bar-2-gated):** CS-4 runtime evaluator wiring. Companion: coordinate with TSK-ca5dd3 (F1-B1 widening) so §7.1 is not duplicated.
