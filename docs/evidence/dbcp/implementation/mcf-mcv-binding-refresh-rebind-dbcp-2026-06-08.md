---
title: MCF MCV binding-refresh / rebind service — mini-DBCP (zero DDL)
status: locked
date: 2026-06-08
project: bc-core
domain: implementation
governs: DEC-c3e57f (D422 MCF) · DEC-a6258b (D430) · DEC-4a17e0 (D431)
kind: zero-DDL governed-write-path DBCP
parent: mcf-arpi-mc-rebind-proposal-2026-06-08.md
---

# MCF MCV binding-refresh / rebind service — mini-DBCP (zero DDL)

**Draft for review. Do not implement.** This is a **zero-DDL** governed-write-path DBCP: no schema
change; it adds a service/endpoint that composes **existing** MCF write primitives so that an MCV's
variable bindings can be refreshed (superseded BCF concept → active successor) **without** re-running an
M12 panel and **without** any direct `mcf.*` writes by operator/script.

## Purpose
A governed path for **identity-preserving** Metric Contract Version binding refresh: same metric identity,
same formula, same grain, same temporal gate; only the variable bindings move from superseded BCF concepts
to their active successors; the predecessor MCV is superseded. Driving case: ARPI (`average_revenue_per_invoice`).

## Grounding (read-only, main @ `b0f0399`)
- **Active ARPI MCV `8c088f55`** (parent MC `49cdde1a`, v1, `governance=active`, `is_current=true`),
  formula `divide(sum(numerator_source), count_distinct(denominator_key))`, grain `e3963e45`. Its three
  bindings point at **superseded** concepts (`a42d3fc0/095afe86/d05f24b3`); active successors are
  `1a2ac2f2/51482979/61e19048` (the active OC-v2/CC-v2 anchors).
- **MCF tables (exist; no DDL):** `mcf.metric_contract`, `metric_contract_version`,
  `metric_variable_binding`, `metric_supersession`, `certification_record` (+ idempotency/eligibility).
- **Existing primitives in `mcf-cert-writer.service.ts`:**
  - `createMetricDraft(input: CreateMetricDraftInput)` (L913) — **panel-agnostic**: writes a new parent MC
    + MCV (`metric_contract_version`) + `metric_variable_binding` rows + cert, in one tx. Its input already
    carries `metricContractVersion.supersedesVersionUid` (L827) — the materialization path passes `null`.
  - `supersedeMetric(input: SupersedeMetricInput)` (L1525) — records `metric_supersession`; validates
    predecessor & successor both `governance_state_code='active'` + `is_current=true`, on **different parent
    MCs**; `correctionClassCode ∈ {editorial, meaning_bearing}`.
  - M13 PE-MC eligibility (`metric-publication-eligibility-evaluator`) + M14 activation
    (`POST mcf/metric-contract-versions/:mcvUid/activate`).
- **D430/D431 resolvers** (active): `CanonicalConceptResolverService.resolve(grain, concept)` → active CC-v2
  field; `ObservationConceptResolverService.isConceptObservableFromSource(concept)` → active OC-v2.
- The gap is **only** an orchestrator that feeds `createMetricDraft` the copied predecessor
  formula/grain/temporal + the rebound bindings + `supersedesVersionUid=8c088f55`, then drives M13/M14 +
  `supersedeMetric`. No new table, no hand-written SQL.

## 1. Service / API surface
- **New service** `MetricMcvRebindService` (registry/mcf), **platform/admin-only** (same guard surface as
  the M14 activation controller; not tenant-scoped).
- **Endpoint:** `POST /mcf/metric-contract-versions/rebind` (thin pass-through controller + DTO).
- **Input:**
  - `predecessorMcvUid` (e.g. `8c088f55`)
  - `bindings`: array of `{ variable_role_code, new_business_concept_id }` (the role→new-concept map)
  - `operatorRationaleText` (≥ N chars) + certifier identity (from the authenticated platform principal)
  - `correctionClassCode` — **locked `editorial`** (meaning-preserving anchor refresh; O-B)
- **Output: a DRAFT successor MCV only.** The endpoint does **not** publish, activate, or supersede — M13,
  M14, and supersession are explicit separate governed steps afterward (O-A).
- **General service (O-C):** no hardcoded metric / UUIDs; ARPI is the first *payload* only. Works for any
  MCV whose predecessor roles are rebound to active BCF concepts under the same formula/grain/temporal contract.
- **Refuses** (400) if the request implies any change to formula AST, grain entity, temporal gate, filter
  set, or role kinds — it is **binding-only**. The successor `mc_name` is **not** copied: it is a
  deterministic **technical** name (§A); the predecessor `display_name` is copied **exactly**. Snapshots
  are **not** operator input; they are copied from the live BCF concept (see §3).

## 2. Transaction — the rebind endpoint creates a DRAFT successor MCV only (all-or-none)
Per **O-A**, the endpoint's transaction is **steps 1–3** and stops at a draft successor. **M13, M14, and
supersession (steps 4–5) are separate explicit governed steps**, invoked afterward via existing endpoints —
**never** inside the rebind call.
1. Load predecessor (e.g. `8c088f55`): `formula_ast_canonical_json`, grain entity, temporal-gate, filters, roles.
2. Build `CreateMetricDraftInput` with **copied** formula/grain/temporal/filters (verbatim) + the **rebound**
   `metric_variable_binding` rows (new `bound_business_concept_id` per role; snapshot copied from the live BCF
   concept) + `metricContractVersion.supersedesVersionUid = <predecessorMcvUid>` (records the supersedes
   *intent* on the draft; the formal supersession link is written later, in step 5). The parent MC `mc_name`
   is the **derived technical name** (§A); `display_name` is **copied** from the predecessor unchanged.
3. `createMetricDraft(input)` → new parent MC uid + successor MCV (`governance=draft`), bindings written,
   `variable_binding_set_hash` / `identity_tuple_hash` recomputed by the existing writer, draft cert recorded.
   **The endpoint returns here (the draft successor MCV uid).**

**Subsequent SEPARATE governed steps (NOT part of the rebind endpoint — O-A):**
4. **M13** PE-MC eligibility on the successor MCV; **M14** `activate` → successor `active` / `is_current`.
5. `supersedeMetric({ predecessorMetricContractVersionUid, successorMetric{Contract,ContractVersion}Uid,
   correctionClassCode: 'editorial', cert })` → writes `metric_supersession`, demotes predecessor
   `is_current=false`. (`supersedeMetric` requires both active + is_current — hence only after M14.)

## 3. Gates (all must pass; refuse otherwise)
- **Predecessor active + immutable:** `8c088f55` is `active`/`is_current`; never UPDATEd (a new MCV is minted).
- **New concepts active:** each `new_business_concept_id` `lifecycle_state='active'` (rejects superseded —
  the existing bind-time check).
- **Meaning-preserving (O-B):** each new concept's `representation_term` AND `data_type` equal the
  predecessor role's snapshot (the editorial guarantee). Unit MAY refresh from the live successor (ARPI
  numerator USD → null). Same grain is enforced via the grain-scoped D430 resolver. Lineage in
  `business_concept_supersession` is **not** required (O-C general): the new concept need only be active,
  on-grain, observable, and of the same `representation_term`/`data_type`.
- **Snapshots copied from live BCF:** `representation_term/unit/data_type` snapshot == the live concept
  (D430/D431 §snapshot rule) — not operator-supplied.
- **D430 resolver:** `resolve(e3963e45, concept)` returns the active CC-v2 field for all three.
- **D431 O↔C:** each concept observable via the active OC-v2.
- **Formula / grain / temporal-gate UNCHANGED:** assert the successor's copied values byte-equal the
  predecessor's (the binding-only guarantee).
- **M13/M14 still required:** publication-eligibility + activation are not bypassed.
- **Technical successor mc_name available (§A):** the parent MC `mc_name` is a deterministic technical
  derivative (predecessor `display_name` copied). **Refuse** (409) if a non-archived `mcf.metric_contract`
  already holds the derived `mc_name` (the M12.5 `idx_mcf_mc_mc_name_active` would otherwise abort with 23505).

## 4. ARPI payload (the first invocation)
- `predecessorMcvUid = 8c088f55`
- `bindings`:
  - `numerator_source` → `1a2ac2f2` (snapshot amount/null/decimal)
  - `denominator_key` → `51482979` (snapshot identifier/null/string)
  - `temporal_anchor` → `61e19048` (snapshot date/null/date)
- supersedes active MCV **`8c088f55`** → exactly one active ARPI MCV after publication.

## 5. Proof target (this DBCP's acceptance)
**Static O→C→M identity trace only** — no runtime evaluation:
- each MC variable concept → CC-v2 canonical field via the D430 resolver (non-null × 3),
- each concept declared observable by the active OC-v2 (D431),
- chain_status / M13 / M14 gates report complete for the successor MCV.
- **No** runtime evaluation · **no** tenant fact writes · **no** `metric_snapshot` · **no** `contract.*`
  materialization.

## 6. Rollback
- **Before activation/publication (successor still draft):** abandon the draft successor MCV via the
  existing governed draft-abandon/reject path; predecessor `8c088f55` remains active untouched. No raw delete.
- **After activation + supersession:** reversal is a **governed follow-up** (mint a corrected MCV that
  supersedes the new one, or a governed un-supersede) — **never** a raw `DELETE`/`UPDATE` on `mcf.*`.
  Immutability (Invariant III) holds: history is appended, not rewritten.

## 7. Explicit exclusions
- **No DDL** · no M12 panel rerun · no formula edits · no grain edits · no temporal-gate edits ·
  no OC/CC changes · no MCF materialization (M12.5) · no runtime evaluation · no fact/snapshot/`contract.*` writes.

## Locked decisions (operator, 2026-06-08)
- **O-A — draft-only endpoint:** the rebind endpoint creates a **draft successor MCV only**; it must NOT
  publish, activate, or supersede in the same call. M13, M14, and supersession remain explicit **separate**
  governed steps after draft creation.
- **O-B — `correctionClassCode = editorial`:** a meaning-preserving binding refresh — formula, grain,
  temporal gate, variable roles, and metric identity unchanged; only stale BCF anchors refreshed to active
  successors.
- **O-C — general service:** implemented as a **general role→concept rebind** service — **no hardcoded ARPI
  UUIDs**. ARPI is the first governed *payload* (§4); the service supports any MCV whose predecessor's
  variable roles are rebound to active BCF concepts under the same formula/grain/temporal contract.

## §A — Amendment (2026-06-08): Option A — technical successor mc_name (no DDL)

**Why (live grounding):** `mcf.metric_contract` carries a partial-unique index
`idx_mcf_mc_mc_name_active = UNIQUE (mc_name) WHERE archived_at IS NULL`, added by
`docker/redesign/12-mcf-m12-5-mc-name-unique-index.sql` per the M12.5 DBCP `D-M12.5-MC-NAME-IDEMPOTENCY`
(decision MC-NAME-A: **one live MC per `mc_name`**). `createMetricDraft` always inserts a **new** parent MC,
so reusing the predecessor's `mc_name` while the predecessor is non-archived → two non-archived rows →
Postgres **23505**. The conflict also bites at **M14 activation** (both active, non-archived, same name),
and `supersedeMetric` does **not** archive the predecessor (it only flips the MCV to `superseded`). So a
*same-named* rebind→activate→supersede is structurally blocked.

**Decision (Option A, operator 2026-06-08) — zero DDL:**
- The successor MC `mc_name` is a **deterministic technical name**:
  `deriveRebindMcName(predecessor.mc_name, predecessorMcvUid) = ${mc_name}__rebind_${first 8 hex of the
  predecessor MCV uid}`. It is validated/normalized (non-empty, ≤ 255 chars, `^[A-Za-z0-9_]+$`).
- The predecessor `display_name` is **copied exactly** (`display_name` is not under the unique index and is
  not identity-bearing — the parent-MC immutability trigger does not lock it).
- Before `createMetricDraft`, the service **refuses** (409) if a non-archived `mcf.metric_contract` already
  holds the derived `mc_name` — a clear message instead of a raw 23505; a deterministic re-run is caught.
- **Provenance:** both `predecessor_mc_name` and `successor_technical_mc_name` are recorded in the cert
  `gateResultsJson` **and** the MC `candidate_source_ref_json`. The endpoint result returns `successorMcName`.
- Rationale for safety: `mc_name` is **MCF-internal** (D430/D431 resolution + the legacy bridge key on
  concept-id / `metric_code`, never `mc_name`); identity is the hash tuple; lineage is `metric_supersession`
  (name-independent). The human-facing name lives in `display_name`, which stays canonical.

**Out of scope here (Option C — NOT in this PR):** any DDL / index change, or reconciling the M12.5
`mc_name` invariant with the M15 supersession handoff so the active successor can carry the canonical
`mc_name`. That is a separate governed item (DDL + DBCP amendment) if/when desired.
