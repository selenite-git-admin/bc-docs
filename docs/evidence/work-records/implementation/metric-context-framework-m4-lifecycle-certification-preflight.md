---
uid: metric-context-framework-m4-lifecycle-certification-preflight
title: MCF M4 Lifecycle Certification / Transition Authority — Preflight
description: Preflight design framing for MCF Gate M4 (lifecycle certification + transition authority — the service that writes contract.certification_record rows for metric_create, metric_transition, and metric_supersede action codes and wraps cert-write + state UPDATE in single DB transactions so the M3 substrate triggers see the cert at the moment of the state change). Reads MCF requirements §10 + §11.5 + §13 + §17.3, the build plan §4.2 Gate M4 / Gate M14 / Gate M15 rows, the M3 preflight + DBCP + apply closeout, the live contract.certification_record + framework_policy + operator_confirm_rule schemas in bc_platform_dev, and the M3 trigger definitions in docker/redesign/05-mcf-lifecycle-substrate.sql. Locks the M4 responsibility boundary — three cert writers (metric_create at intake → draft, metric_transition at approved → active, metric_supersede at active → superseded), one transition service that wraps cert + state UPDATE in single tx, hash-population delegation to M7/M8 services, PE-MC eligibility result recording surface (table; computation owned by M11 panel later), operator-confirm rule seeding for MCF action codes. Explicitly excludes M5 (panel substrate), M7 (formula AST), M8 (package signature), M9 (fixture substrate), M11/M12/M14 publication panel + endpoint surfaces, PE-MC check execution, REST/MCP endpoint design, MCF authoring UI, and BCF data writes. Recommends docs-only DBCP design as the next gate. Enumerates the operator decisions required before the M4 DBCP can be authored. No DDL applied; no bc-core schema edited; no MCF metric contracts created; no certification rows written.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m4-preflight
---

# MCF M4 — Lifecycle Certification / Transition Authority Preflight

## 1. Scope and grounding

### 1.1 Purpose

Frame Gate M4 of the MCF arc **before** any DBCP design or bc-core implementation begins. M4 is the lifecycle certification + transition authority — the service that writes `contract.certification_record` rows for MCF action codes and wraps each cert-write together with its corresponding `mcf.metric_contract_version.governance_state_code` UPDATE in a single database transaction, so the M3 substrate trigger (`mcf.fn_mcv_state_transition_check()`) sees the required cert at the moment of the state change.

Without M4, the M3 substrate is operationally dormant: no `mcf.metric_contract_version` row can legitimately reach `'active'` because no path exists today to write the `metric_transition` cert that the M3 state-transition trigger requires.

This preflight identifies what M4 owns, what it doesn't, what design tensions must be resolved before DBCP authoring, and what operator decisions are required.

### 1.2 What this preflight is and is not

| | This preflight |
|---|---|
| Is | A docs-only framing of the M4 service boundary, transition semantics, cert-writing patterns, and operator decisions required before DBCP authoring. |
| Is | An explicit recommendation on the M4 path forward (docs-only DBCP design → implementation PR → service merge). |
| Is not | The M4 DBCP design itself. Method signatures, exact transaction shape, error semantics, and test plans are DBCP scope. |
| Is not | An M4 implementation. No bc-core source file is edited. No service code is written. No DDL applied. |
| Is not | An API/MCP endpoint design. REST surface and MCP tool surface are later-gate concerns (M14 for publication endpoint; M15 for supersession endpoint per the build plan). |
| Is not | A revisit of M1, M2, or M3. ADR DEC-c3e57f / D422 is the authority; M2 substrate is live; M3 substrate is live with 7 triggers attached. This preflight cites them but does not re-decide. |

### 1.3 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — read-only this session |
| No DDL applied | ✓ — no apply gate in this preflight |
| No MCF metric contracts created | ✓ — `mcf.metric_contract*` tables remain empty per M3 apply closeout |
| No M5 / M7 / M8 / M9 / M11 / M12 design | ✓ — references-only |
| No REST / MCP endpoint design | ✓ — service contract only, no external surface |
| No BCF writes | ✓ — `concept_registry.*` untouched |
| No `contract.certification_record` rows written | ✓ — preflight reads schema; writes nothing |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

### 1.4 Source documents consumed

| Source | Role | Commit / location |
|---|---|---|
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority; locks 5-state lifecycle + cert reuse via Foundation Governance Substrate + operator-confirm at `approved → active` | `bc-docs-v3/docs/adrs/ADR-c3e57f.md` |
| MCF requirements §10, §11.4, §11.5, §13, §17.3 | Lifecycle states, transition actor matrix, operator-confirm rules, PE-MC-1..PE-MC-10 publication eligibility, Foundation Governance Substrate cert reuse | `metric-context-framework-requirements.md` |
| MCF build plan §4.2 — Gates M4 / M14 / M15 | Scope of publication eligibility substrate (M4), publication path + `metric_transition` cert writer (M14), supersession path + `metric_supersede` cert writer (M15); risk table R-13 (Foundation Governance Substrate write coupling) | `metric-context-framework-build-plan.md` |
| M3 preflight | Cert reuse pattern; cert writer recommendation for `metric_create` | `metric-context-framework-m3-lifecycle-substrate-preflight.md` (`9e472cb`) |
| M3 DBCP §6.3, §8.3, §9 | Live trigger logic for `metric_transition` cert lookup; `metric_create` cert is service-contract-only; cert reuse model | `metric-context-framework-m3-lifecycle-substrate-dbcp.md` (`3147bd4`+`938fb0f`) |
| M3 apply closeout | M3 substrate live state | `mcf-m3-ddl-apply-closeout.md` (`d1f67d0`) |
| Live `contract.certification_record` schema | Column shape confirmed via `pg_query` this session (27 columns) | `bc_platform_dev` |
| Live `contract.framework_policy` + `contract.operator_confirm_rule` schemas | Operator-confirm seed shape confirmed (rule_uid / scope / transition / action_code / rationale_required) | `bc_platform_dev` |
| M3 lifecycle DDL | The 7 triggers M4 service must compose with | `bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql` |

### 1.5 Scope clarification — operator framing vs. build plan split

**Operator framing (this preflight):** "M4 = lifecycle certification / transition authority" — a logical bundle covering all cert writing + state-transition orchestration across MCF action codes (`metric_create`, `metric_transition`, `metric_supersede`).

**Build plan §4.2 split:**
- **Gate M4** — Publication eligibility substrate (`mcf.metric_publication_eligibility_result` table + operator-confirm rule seeding).
- **Gate M14** — Publication path (two-phase request → operator confirm) + `metric_transition` cert writer.
- **Gate M15** — Supersession path + `metric_supersede` cert writer.

This is one of the named operator decisions (D-1 below): keep M4 narrow per the build plan, or bundle the cert-writing concerns under one logical gate. The preflight is authored under the operator's bundled framing — DBCP design and implementation may still split into multiple PRs for sequencing — but the boundary is presented as a single concern.

---

## 2. Current live M2 + M3 substrate recap

Per the M3 apply closeout (`bc-docs-v3 d1f67d0`) + M3 evidence PR (`bc-core` PR #104 / `a6a3e64`):

| Asset | State |
|---|---|
| `mcf` schema | present in `bc_platform_dev` |
| `mcf.metric_contract` (17 cols, 0 rows) | identity-bearing parent; hash columns nullable in M2; trigger `trg_mcf_mc_active_immutability` rejects identity column mutations when any version past-draft |
| `mcf.metric_contract_version` (15 cols, 0 rows) | descriptive body + `governance_state_code` (5-state CHECK enum); 3 triggers attached |
| `mcf.metric_variable_binding` (13 cols, 0 rows) | per-variable bindings; 1 trigger (BEFORE UPDATE OR DELETE rejects when parent past-draft) |
| `mcf.metric_filter_clause` (9 cols, 0 rows) | mirror; 1 trigger |
| `mcf.metric_computed_dimension_ref` (9 cols, 0 rows) | mirror; 1 trigger |
| `mcf.metric_contract_revision` (9 cols, 0 rows) | descriptive revision audit (emitted by `trg_mcf_mcv_revision_emit` AFTER UPDATE) |
| `mcf.metric_supersession` (11 cols, 0 rows) | predecessor → successor edges; FK to `contract.certification_record` via `certification_record_id` |
| `mcf.fn_mcv_state_transition_check()` | M3 trigger function; enforces forward-only state graph + hash NOT-NULL at `→ approved` + `metric_transition` cert lookup at `→ active` + supersession-row + active-successor check at `→ superseded` |
| `mcf.fn_mc_active_immutability_check()` | M3 trigger function; rejects identity column mutations on parent |
| `mcf.fn_mcv_descriptive_immutability_check()` | M3 trigger function; Q1 LOCKED — rejects all non-state mutations at `'approved'` or `'superseded'`; permits descriptive UPDATEs at `'active'` (which fire revision-emit) |
| `mcf.fn_mvb_active_immutability_check()` + 2 siblings | M3 trigger functions; reject child UPDATE/DELETE when parent past-draft |
| `mcf.fn_mcv_revision_emit()` | M3 trigger function; AFTER UPDATE emits revision row when prior state was `'active'` and descriptive columns changed |
| `contract.certification_record` (27 cols) | Foundation Governance Substrate — accepts MCF rows by virtue of open `action_code` text column |
| `contract.framework_policy` (12 cols) | Policy version + scope + operator-confirm rule list per framework |
| `contract.operator_confirm_rule` (7 cols) | Per-transition operator-confirm rules; default `rationale_required = TRUE` |

M3 wrote behavioral substrate that is **structurally complete but operationally dormant**: the triggers exist, but no service path exists to write a cert that satisfies the trigger at `→ active`, and no service path exists to insert a supersession row + cert that satisfies the trigger at `→ superseded`. M4 builds that path.

---

## 3. Why M4 is needed

### 3.1 What blocks today

| Concern | Blocking factor | Resolved by M4? |
|---|---|---|
| First MC creation (`intake → draft`) | No service writes the `metric_create` cert. The M3 DBCP §8.3 specified this as "service-contract-only at INSERT" — i.e. atomically written in the same tx as the MC + MCV row INSERTs. PR #103 shipped DDL but not the writer service. | **Yes — M4 ships the `metric_create` cert writer.** |
| MC progression `draft → review` | No cert required by substrate. Service-only state UPDATE. | **Partially — M4 may ship a thin transition method; or M11 panel may UPDATE directly.** Either path is substrate-correct. |
| MC progression `review → approved` | No cert required by substrate. But parent's 6 hash columns must be NOT NULL — the M3 trigger rejects otherwise. M7 (formula AST) + M8 (package signature) own hash computation. | **Partially — M4 transition service can UPDATE the state once hashes are populated. M4 does NOT compute hashes (M7/M8 do).** |
| MC progression `approved → active` | M3 trigger requires a `metric_transition` cert row in `contract.certification_record` with `primitive_type='metric_contract_version'`, `primitive_id=<mcv_uid>`, `action_code='metric_transition'`, `from_state_code='approved'`, `to_state_code='active'`, `is_archived_after IS NOT TRUE`. No service writes this. | **Yes — M4 ships the `metric_transition` cert writer + transition orchestrator that wraps cert-write + state UPDATE in a single tx.** |
| MC supersession `active → superseded` | M3 trigger requires a matching `mcf.metric_supersession` row whose successor version is `'active'` + `is_current=TRUE`. The supersession row's `certification_record_id` FK points to a `metric_supersede` cert. No service writes either. | **Yes — M4 ships the `metric_supersede` cert writer + supersession orchestrator that wraps cert-write + supersession-row INSERT + predecessor state UPDATE in a single tx.** |
| PE-MC-1..PE-MC-10 evaluation result recording | Per build plan §4.2 Gate M4, `mcf.metric_publication_eligibility_result` records per-publication PE-MC results. PE-MC execution itself is panel-side (M11); PE-MC result table + insertion is M4. | **Yes — M4 ships the PE eligibility result writer.** |
| Operator-confirm rule rows for MCF action codes | `contract.operator_confirm_rule` carries per-transition rules. MCF entries don't exist yet. | **Yes — M4 seeds MCF operator-confirm rules.** |

### 3.2 Why M4 cannot be skipped or deferred

The M3 substrate gates are non-negotiable: no row reaches `'active'` without a `metric_transition` cert. M4 is the only thing standing between an empty `mcf.*` and the first published metric. Skipping M4 means the entire MCF arc (M11+ metric authoring, M14 publication path, M15 supersession, M20 first metric) is blocked.

Deferring M4 means M11 (panel) is also blocked — the panel needs an authority surface to write its proposed cert. So M4 is the next functional gate after M3.

### 3.3 Why M4 cannot include too much

M4 must not:
- Compute formula AST hashes (M7).
- Compute package signature hashes (M8).
- Execute PE-MC checks (M11 panel-side; M4 only records results).
- Author panel-run substrate (M5).
- Expose REST or MCP endpoints (M14 / M15 endpoint surfaces).
- Drive UI (M12 authoring panel UI).
- Touch BCF substrate.

The boundary is the **service contract** that wraps cert-write + state UPDATE. The implementation is a TypeScript service in `bc-core/src/registry/mcf/` (per BCF pattern) that downstream callers (M11 panel, M14 publication endpoint, M15 supersession endpoint) invoke when they need to write a cert and advance state.

---

## 4. M4 responsibility boundary

### 4.1 What M4 owns (5 concerns)

| # | Responsibility | Source |
|---:|---|---|
| 1 | **Cert writer for `metric_create`** — service helper that INSERTs into `contract.certification_record` with the right column population when an `intake → draft` write occurs. Wrapped atomically with the MC + MCV + bindings INSERT in a single transaction by the caller. | MCF §11.5; build plan §4.2 Gate M3 (helper specified, deferred to M4); M3 DBCP §3.11 (D-11) + §8.3 |
| 2 | **Cert writer for `metric_transition`** — service method that INSERTs the `metric_transition` cert row AND issues the `mcf.metric_contract_version.governance_state_code` UPDATE from `'approved'` to `'active'` in a single transaction. The M3 state-transition trigger fires during the UPDATE and sees the cert. | MCF §11.4; build plan §4.2 Gate M14; M3 DBCP §6.3 (trigger body) |
| 3 | **Cert writer for `metric_supersede`** — service method that INSERTs the `metric_supersede` cert row, INSERTs the `mcf.metric_supersession` edge row (referencing the cert by `certification_record_id`), AND issues the predecessor's state UPDATE from `'active'` to `'superseded'` in a single transaction. The M3 trigger fires during the predecessor UPDATE and sees the supersession row + active successor. | MCF §10.5, §11.4; build plan §4.2 Gate M15; M3 DBCP §5 + §6.3 |
| 4 | **PE-MC eligibility result substrate** — new table `mcf.metric_publication_eligibility_result` that records per-publication PE-MC-1..PE-MC-10 results. Each row references the cert it was evaluated for. The PE-MC-10 row carries a citation to the satisfying `mcf.metric_self_verification_result` (which M9 ships later). | Build plan §4.2 Gate M4; MCF §13, §17.1 |
| 5 | **Operator-confirm rule seeding** — INSERT rows into `contract.operator_confirm_rule` for MCF transitions that require operator confirmation (`metric_transition`, `metric_supersede`, optionally `metric_create` if operator opts in). | MCF §11.4; build plan §4.2 Gate M4 |

### 4.2 What M4 explicitly does NOT own

| # | Out of M4 | Belongs to |
|---:|---|---|
| 1 | Formula AST canonicalization, parsing, identity-hash computation | M7 |
| 2 | Package signature hash composition (formula + bindings + grain + filters + temporal + computed-dim) | M8 |
| 3 | Self-verification fixture substrate + `mcf.metric_self_verification_result` | M9 |
| 4 | Deterministic verifier service that runs fixtures | M10 |
| 5 | Metric Authoring Panel + Publication Panel substrate + execution | M5 (substrate) + M11 (authoring panel) + M12 (publication panel) |
| 6 | PE-MC-1..PE-MC-10 evaluation logic (the checks themselves) | M11 panel-side (computation); M4 only persists results |
| 7 | REST or MCP endpoint surface for `request-publication` / `confirm-publication` / `request-supersession` | M14 (publication endpoint) + M15 (supersession endpoint) |
| 8 | bc-admin authoring UI | M12 UI gate (separate track) |
| 9 | Hash population at `review → approved` — M4 calls into M7/M8 services to compute hashes, but does NOT compute them itself | M7 + M8 |
| 10 | Tenant binding lifecycle (MLS 15-25) | M6 + D392 substrate |
| 11 | Reservoir intake hygiene (`co_bindings` strip) | M11 reservoir ingestion path |
| 12 | Any BCF write | BCF arc |

### 4.3 Why these boundaries

M4 is the **service-level enforcement layer** that composes with the M3 substrate-level enforcement. M3 says "no `'active'` row without a cert"; M4 says "here's how to write the cert correctly". The split is:

- **M3 (substrate):** physical contracts (triggers + tables + constraints + FKs).
- **M4 (service):** transactional orchestration that produces rows that satisfy the M3 contracts.
- **M5+ (panel):** the proposing actor that calls M4's transition methods.
- **M11+ (panel implementation):** PE-MC execution + workbench fingerprint.
- **M14/M15 (endpoints):** external REST/MCP surface that operators interact with.

Each layer is independently testable and independently shippable. M4 can ship and stabilize before M11/M14/M15 — its only consumer at first is the M3 post-apply verifier's synthetic-row test substrate, plus a small set of unit tests.

---

## 5. Transition inventory and state graph

### 5.1 Five-state graph (locked by MCF §10.1; M3 trigger enforces)

```
draft → review → approved → active → superseded
```

Forward-only. No skips. No reverse transitions. The M3 trigger rejects any UPDATE that violates this graph.

### 5.2 Transition × action matrix

| Transition | Default actor | M4 service method (sketch) | Cert written? | Action code | Operator confirm? | Notes |
|---|---|---|---|---|---|---|
| `intake → draft` (first INSERT) | AI by default (panel APPROVE) | `createMetricDraft(spec, operatorContext)` | YES | `metric_create` | **Operator decision (D-9 below)** | Cert + MC + MCV + child INSERTs wrapped in single tx. M3 substrate has NO trigger enforcing this cert — service-contract discipline only (M3 DBCP §8.3). |
| `draft → review` | AI by default | `submitForReview(mcv_uid, operatorContext)` | NO | n/a | NO (AI-default) | Service issues simple state UPDATE; M3 trigger validates state graph only. No cert in M3 design. **Decision D-10: include a `metric_intake_review` cert anyway for audit symmetry?** Recommend NO. |
| `review → approved` | AI by default (panel returns APPROVE + PE-MC-1..PE-MC-9 pass) | `approveForActivation(mcv_uid, hashesProvider, peResults, operatorContext)` | NO | n/a | NO (AI-default per MCF §11.4) | M4 calls M7/M8 hash providers BEFORE issuing the state UPDATE. M3 trigger enforces hash NOT-NULL on parent at `→ approved`. PE-MC results from M11 panel passed in for storage. |
| `approved → active` | **Operator confirm (always)** | `activateMetric(mcv_uid, peEligibilityBundle, operatorRationale, operatorContext)` | YES | `metric_transition` | **YES (always; ≥40 char rationale per MCF §11.4)** | Cert INSERT + state UPDATE in single tx. M3 trigger reads the cert at UPDATE-time. M3 trigger also flips `is_current = TRUE` and demotes prior current to FALSE. |
| `active → superseded` | **Operator only** | `supersedeMetric(predecessor_mcv_uid, successor_mcv_uid, correctionClass, rationale, operatorContext)` | YES | `metric_supersede` | **YES (always; ≥40 char rationale per MCF §11.4)** | Cert INSERT + supersession-row INSERT + predecessor state UPDATE all in single tx. Successor must already be `'active'` + `is_current=TRUE`. M3 trigger reads supersession row at UPDATE-time. |

### 5.3 Transition guards (substrate-enforced, not M4)

| Guard | Enforced by | M4 must respect by |
|---|---|---|
| Forward-only state graph | `mcf.fn_mcv_state_transition_check()` | Never issuing a skip/reverse UPDATE |
| Parent hashes NOT NULL at `→ approved` | Same trigger | Populating hashes BEFORE issuing the state UPDATE (calling M7/M8 first) |
| `metric_transition` cert exists at `→ active` | Same trigger | INSERTing the cert in the same tx as the state UPDATE |
| Supersession row + active successor at `→ superseded` | Same trigger | INSERTing the supersession row (with FK to a fresh `metric_supersede` cert) in the same tx as the state UPDATE |
| Identity-bearing column immutability on parent | `mcf.fn_mc_active_immutability_check()` | Never UPDATEing identity columns after any version is past-draft |
| Descriptive immutability on approved/superseded versions (Q1 LOCKED) | `mcf.fn_mcv_descriptive_immutability_check()` | Never UPDATEing descriptive columns on `'approved'` or `'superseded'` versions |
| Child-table immutability when parent past-draft | `mcf.fn_mvb/mfc/mcdr_active_immutability_check()` | Never UPDATEing/DELETEing child rows when parent version past-draft |
| Revision audit emission on active-state descriptive UPDATEs | `mcf.fn_mcv_revision_emit()` (AFTER UPDATE) | Permitting active-state descriptive UPDATEs through M4 (revision row auto-emitted by substrate) |

---

## 6. Transaction discipline options

### 6.1 The core problem

The M3 state-transition trigger checks for cert existence using a `SELECT EXISTS (...)` against `contract.certification_record` at UPDATE-time. The cert must be **visible** to the trigger when it runs. PostgreSQL trigger semantics: a trigger sees the current transaction's pending changes (the cert INSERT done earlier in the same tx is visible).

### 6.2 Option A — Single transaction (RECOMMENDED)

The cert INSERT and the `governance_state_code` UPDATE happen in the same DB transaction, in that order:

```typescript
// pseudo-code (DBCP will refine signatures)
await db.transaction(async (tx) => {
  // 1. INSERT cert row
  const cert = await tx.insert(contractCertificationRecord).values({...}).returning();

  // 2. UPDATE state — M3 trigger fires here, sees the cert
  await tx.update(mcfMetricContractVersion)
    .set({ governanceStateCode: 'active' })
    .where(eq(mcfMetricContractVersion.metricContractVersionUid, mcvUid));
});
```

**Pro:** Atomicity. Either both succeed or both roll back — no orphan cert, no half-transitioned MCV.
**Pro:** Trigger semantics naturally support this (same-tx visibility).
**Pro:** No idempotency-token mechanism needed.
**Con:** A long-running cert composition (PE-MC result assembly, signature computation) holds the tx open. **Mitigation:** caller assembles the cert payload BEFORE opening the tx; the tx only does the INSERT + UPDATE.

### 6.3 Option B — Two transactions with idempotency tokens

Cert INSERT in tx1; state UPDATE in tx2:

```typescript
const cert = await db.insert(contractCertificationRecord).values({...idempotencyToken}).returning();
await db.update(mcfMetricContractVersion).set({ governanceStateCode: 'active' }).where(...);
```

**Pro:** Shorter individual tx lifetimes.
**Con:** Between tx1 commit and tx2 start, an outside reader could see a cert with no corresponding active MCV — an orphan from the audit-trail perspective.
**Con:** If tx2 fails, cert persists as orphan. Cleanup requires either manual archival or an `is_archived_after` flip (but then the cert is wasted).
**Con:** Idempotency-token logic adds surface area and corner cases (what if tx2 retries with a different token?).

### 6.4 Recommendation

**Option A — single transaction.** All M4 service methods (`activateMetric`, `supersedeMetric`, etc.) open a single tx, assemble + INSERT cert, then UPDATE state. PE-MC result assembly happens BEFORE the tx (in M11 panel-side code); M4 service accepts the assembled payload.

The single-tx pattern is also what the M3 supersession trigger requires: the supersession row, the cert (referenced by supersession's FK), and the predecessor state UPDATE must all be in one tx, because the M3 trigger checks for the supersession row at UPDATE-time.

### 6.5 Operator decision

| # | Decision | Recommendation |
|---:|---|---|
| D-2 | Single tx (Option A) vs. two tx with idempotency (Option B) | Option A |
| D-3 | Should M4 service methods support a `dryRun: boolean` parameter that returns "would this transition succeed?" without writing? | Recommend YES for development ergonomics; can be a simple wrapper that issues the cert + UPDATE inside a tx and rolls back. Mirror of the M3 post-apply verifier pattern. |

---

## 7. Hash population responsibility options

### 7.1 The 6 parent MC hash columns

At `review → approved`, the M3 state-transition trigger requires these 6 columns on `mcf.metric_contract` to be NOT NULL:

- `formula_intent_hash`
- `variable_binding_set_hash`
- `filter_set_hash`
- `identity_tuple_hash`
- `package_signature_hash`
- `hash_algorithm_version`

The algorithms for these hashes are specified in MCF requirements §8.7 (composite signature) and §4.2 (identity tuple). They reference:

- Formula AST canonicalization (M7 territory).
- Variable bindings composition (M2 + M7 territory).
- Filter clauses composition (M2 + M7 territory).
- Grain entity + temporal gate canonicalization (M2 territory).
- Computed-dimension references composition (M2 + M7 territory).

### 7.2 Option A — M4 service computes hashes

M4 imports the hash algorithm implementations (presumably from a `bc-core/src/registry/mcf/hash/*` module) and computes the 6 hashes inline during `approveForActivation`:

```typescript
const hashes = await mcfHashComputer.compute({ metricContractUid, metricContractVersionUid });
await tx.update(mcfMetricContract).set(hashes).where(...);
await tx.update(mcfMetricContractVersion).set({ governanceStateCode: 'approved' }).where(...);
```

**Pro:** Single service owns the hash population at the right moment.
**Con:** Couples M4 to M7/M8 implementation. If hash algorithm spec is incomplete, M4 cannot ship.

### 7.3 Option B — Separate hash-computer service called by M4 (RECOMMENDED)

A separate service (`mcfHashComputer`, owned by M7/M8 in their respective gates) computes hashes. M4 calls it before issuing the state UPDATE:

```typescript
// hash computer lives in bc-core/src/registry/mcf/hash/  (M7/M8 ship these)
const hashes = await mcfHashComputer.computeAllForApproval({ metricContractUid });

// M4 just composes the operation
await db.transaction(async (tx) => {
  await tx.update(mcfMetricContract).set(hashes).where(...);
  await tx.update(mcfMetricContractVersion).set({ governanceStateCode: 'approved' }).where(...);
});
```

**Pro:** Clean separation. M7/M8 own the algorithm; M4 owns the orchestration.
**Pro:** M4 can ship NOW with a `MockMcfHashComputer` that returns placeholder hashes for synthetic-row testing. When M7/M8 ship the real implementation, M4 service contract doesn't change.
**Con:** Two gates to fully land (M4 + M7/M8) before real metric authoring works. **But** this is already the build plan's sequencing (M4 → M5 → M7 → M8 → M11+).

### 7.4 Option C — Block `review → approved` until M7/M8 ship

M4 ships without any `approveForActivation` method. The state UPDATE from `'review'` to `'approved'` is deferred until M7/M8 ship. M4 only handles `createMetricDraft`, `submitForReview`, `activateMetric`, `supersedeMetric`.

**Pro:** Minimal M4 surface; no hash dependency.
**Con:** Asymmetric service contract; the lifecycle has a gap that confuses callers. M11 panel cannot test the full chain without M7/M8 also being live.
**Con:** Defers the `'approved'` state behavior to later gates, when the substrate is already capable.

### 7.5 Recommendation

**Option B — separate hash-computer service called by M4.** M4 declares the interface (`McfHashComputer`) in its DBCP; the implementation ships in M7/M8 gates. M4 includes a `MockMcfHashComputer` for unit/integration tests against synthetic rows.

This keeps M4's service contract complete and stable, while honoring the gate boundary.

### 7.6 Operator decision

| # | Decision | Recommendation |
|---:|---|---|
| D-4 | Hash population responsibility: M4 (Option A) / separate service called by M4 (Option B) / block until M7/M8 (Option C) | Option B |
| D-5 | Mock hash computer for M4 test fixtures: include in M4 PR? | YES — needed for synthetic-row tests since M7/M8 not yet shipped |

---

## 8. Operator-confirm boundary options

### 8.1 Per-transition operator-confirm decision

| Transition | MCF §11.4 stance | Recommendation |
|---|---|---|
| `intake → draft` (creation) | Not explicitly listed in §11.4 as always-confirm | **Operator decision D-9**: include operator-confirm at intake (audit symmetry, every authoring act is operator-stamped) OR rely on panel-APPROVE only (lighter touch). **Recommend NO operator-confirm at intake** — the panel APPROVE is the authoring authority; operator-confirm is reserved for high-risk authority-bearing transitions. |
| `draft → review` | AI by default | NO operator-confirm. Service-only state UPDATE. |
| `review → approved` | AI by default (PE-MC-1..PE-MC-9 pass + panel APPROVE) | NO operator-confirm. Service-only state UPDATE after hashes populated. |
| `approved → active` | **Operator confirm (always)** | YES — ≥40 char rationale required. Authority-bearing publication moment. |
| `active → superseded` | **Operator only** | YES — ≥40 char rationale required. Retires read authority + points to successor. |

### 8.2 How operator-confirm is enforced

Two layers:

1. **`contract.operator_confirm_rule` rows** define what requires confirmation. M4 seeds these rows at apply-time (or ships them as part of the M4 PR's seed data):

| rule_uid | scope | transition | action_code | rationale_required |
|---|---|---|---|---|
| `mcf_metric_transition` | `mcf` | `approved->active` | `metric_transition` | TRUE |
| `mcf_metric_supersede` | `mcf` | `active->superseded` | `metric_supersede` | TRUE |
| `mcf_metric_create` (optional) | `mcf` | `intake->draft` | `metric_create` | FALSE (or per D-9) |

2. **`contract.framework_policy` rows** define the active policy version for `scope='mcf'` and reference the operator-confirm rule UIDs. M4 may need to seed an `mcf` framework_policy entry.

### 8.3 Service contract implication

M4 service methods that correspond to operator-confirm transitions take a mandatory `operatorRationale: string` (validated `length >= 40` at the service layer; also CHECK'd by `contract.operator_confirm_rule.rationale_required` if extended to substrate). The cert's `certifier_sub`, `certifier_role_at_action`, and (optionally) `certifier_email` are populated from the operator JWT context.

For AI-default transitions (`draft → review`, `review → approved`), no rationale is required; the service method takes a lighter context object with the panel's actor identity.

### 8.4 Operator decision

| # | Decision | Recommendation |
|---:|---|---|
| D-6 | Per-transition operator-confirm matrix (§8.1 table) | Confirmed per MCF §11.4: always-confirm at `approved → active` and `active → superseded`; AI-default elsewhere |
| D-7 | Where to seed `operator_confirm_rule` rows for MCF? In M4 PR DDL? Or runtime service seed? | Recommend M4 PR ships DDL INSERT statements alongside service code, as part of M4 apply (separate operator-authorized DCP gate, mirroring M2 + M3 pattern) |
| D-8 | Should M4 seed a `framework_policy` row for `scope='mcf'`? | YES — required for cert's `policy_version` column to have a valid reference |
| D-9 | Operator-confirm at `intake → draft`? | Recommend NO (panel APPROVE is authoring authority; operator-confirm is for publication moments) |

---

## 9. Cert row contract over `contract.certification_record`

### 9.1 Column shape (live, confirmed via `pg_query` this session)

27 columns. Key columns M4 must populate per action code:

| Column | metric_create | metric_transition | metric_supersede |
|---|---|---|---|
| `certification_record_id` | auto (gen_random_uuid()) | auto | auto |
| `primitive_type` | `'metric_contract_version'` | `'metric_contract_version'` | `'metric_contract_version'` |
| `primitive_id` | new MCV uid | the MCV uid being activated | predecessor MCV uid |
| `action_code` | `'metric_create'` | `'metric_transition'` | `'metric_supersede'` |
| `from_state_code` | NULL | `'approved'` | `'active'` |
| `to_state_code` | `'draft'` | `'active'` | `'superseded'` |
| `is_archived_after` | NULL (active) | NULL (active) | NULL (active) |
| `gate_results_json` | PE-MC-1..PE-MC-9 panel results from M11 (assembled into JSONB) | PE-MC-1..PE-MC-10 results (incl. PE-MC-10 verification result citation) | PE-MC reassessment results for successor + correction-class metadata |
| `advisory_verdicts_json` | panel advisory verdicts | panel advisory verdicts | panel advisory verdicts (if AI-proposed) |
| `override_gate_code` | NULL or operator override target gate | NULL or override target | NULL or override target |
| `override_rationale_text` | NULL or operator override rationale | NULL or override rationale | NULL or override rationale |
| `override_followup_task_uid` | NULL or DevHub task UID | same | same |
| `certifier_sub` | panel APPROVE certifier (panel sub) | operator Cognito sub | operator Cognito sub |
| `certifier_role_at_action` | `'panel'` or `'operator'` | `'operator'` | `'operator'` |
| `certifier_email` | optional | optional | optional |
| `supersedes_primitive_id` | NULL | NULL | predecessor MCV uid (also in `primitive_id`; this column captures the "what is being superseded" relationship explicitly) |
| `created_at` | auto (now()) | auto | auto |
| `panel_run_uid` | M11 panel run UID | M11 publication panel run UID (or NULL if operator-initiated re-cert) | M11 supersession panel run UID (or NULL if operator-initiated) |
| `prompt_version` | from M11 panel context | same | same |
| `model_identity_json` | three-model identity per M11 | same | same |
| `input_hash` | M11 workbench fingerprint | same | same |
| `policy_version` | from active `mcf` framework_policy | same | same |
| `sampling_status` | from M11 panel sampling decision | same | same |
| `grounding_check_result` | M11 PE-MC-1 no-fabrication outcome | same | same |
| `governance_scope` | `'mcf'` | `'mcf'` | `'mcf'` |
| `subject_kind` | `'metric_contract_version'` | `'metric_publication'` | `'metric_supersession'` |
| `target_registry_id` | NULL (MCF-internal) | NULL | NULL |

### 9.2 What M4 service receives as input

The caller (M11 panel, M14 endpoint, M15 endpoint) provides a `certPayload` object containing:

- `primitiveType` (`'metric_contract_version'`)
- `primitiveId` (the MCV uid)
- `actionCode` (one of three)
- `fromStateCode` / `toStateCode`
- `gateResults` (PE-MC results JSONB)
- `advisoryVerdicts` (advisory JSONB)
- `override` (optional override gate code + rationale + followup task)
- `certifier` (sub + role + optional email)
- `supersedesPrimitiveId` (only for `metric_supersede`)
- `panel` (panel_run_uid + prompt_version + model_identity + input_hash + sampling + grounding)
- `policyVersion` (lookup from framework_policy)
- `governanceScope` = `'mcf'`
- `subjectKind` (varies by action)

M4 fills in the auto columns (id, created_at) and writes the row.

### 9.3 Validation

M4 service validates BEFORE the INSERT:

- `governanceScope === 'mcf'`
- `actionCode IN ('metric_create', 'metric_transition', 'metric_supersede')`
- `primitiveType === 'metric_contract_version'`
- For `metric_transition`: `fromStateCode === 'approved'` && `toStateCode === 'active'`
- For `metric_supersede`: `fromStateCode === 'active'` && `toStateCode === 'superseded'` && `supersedesPrimitiveId !== null`
- `certifier.sub` is a non-empty string; for operator-confirm transitions, `certifier.role === 'operator'`
- `gateResults` is JSONB-serializable
- `policyVersion` references an existing `framework_policy` row with `scope_code = 'mcf'`

Validation failures throw before the INSERT — no half-written cert.

---

## 10. Service contract sketch — no endpoints

### 10.1 Location

`bc-core/src/registry/mcf/` (matches BCF's `bc-core/src/registry/bcf/` pattern).

| File | Purpose |
|---|---|
| `mcf-cert-writer.service.ts` | The cert writer + transition orchestrator |
| `mcf-cert-writer.service.spec.ts` | Unit + integration tests (against synthetic mcv rows) |
| `mcf-hash-computer.interface.ts` | Interface that M7/M8 implement; M4 imports |
| `mcf-hash-computer.mock.ts` | Mock for M4-shipped tests |
| `mcf-operator-confirm-seed.ts` | Seed rows for `contract.operator_confirm_rule` + `contract.framework_policy` |

### 10.2 Service methods (no endpoints)

```typescript
// SKETCH — DBCP will refine. No method bodies; signatures only.

export class McfCertWriterService {
  constructor(
    private readonly db: PlatformDb,
    private readonly hashComputer: McfHashComputer,  // injected; M7/M8 provide
  ) {}

  /**
   * Atomic intake → draft creation. Wraps MC + MCV + bindings + metric_create cert in single tx.
   * Called by M11 panel run service when a panel APPROVE candidate enters substrate.
   */
  async createMetricDraft(input: CreateMetricDraftInput): Promise<{
    metricContractUid: string;
    metricContractVersionUid: string;
    certificationRecordId: string;
  }>;

  /**
   * draft → review transition. Simple state UPDATE; no cert.
   * Validates current state = 'draft' (M3 trigger enforces; service double-checks for clear errors).
   */
  async submitForReview(input: SubmitForReviewInput): Promise<void>;

  /**
   * review → approved transition. Populates parent hashes via M7/M8 hash computer, then state UPDATE.
   * Records PE-MC-1..PE-MC-9 results in mcf.metric_publication_eligibility_result.
   * No cert (per §10.7 the cert is at approved → active, not at review → approved).
   */
  async approveForActivation(input: ApproveForActivationInput): Promise<{
    peEligibilityResultUid: string;
  }>;

  /**
   * approved → active transition. THE authority-bearing publication moment.
   * Writes metric_transition cert + state UPDATE in single tx.
   * Operator-confirm: rationale >= 40 chars enforced.
   * M3 trigger reads the cert and flips is_current discipline.
   */
  async activateMetric(input: ActivateMetricInput): Promise<{
    certificationRecordId: string;
  }>;

  /**
   * active → superseded transition. Writes metric_supersede cert + mcf.metric_supersession row +
   * predecessor state UPDATE in single tx. Successor must already be 'active' + is_current=TRUE.
   * Operator-confirm: rationale >= 40 chars enforced.
   */
  async supersedeMetric(input: SupersedeMetricInput): Promise<{
    certificationRecordId: string;
    supersessionUid: string;
  }>;
}

export interface McfHashComputer {
  computeAllForApproval(input: { metricContractUid: string }): Promise<{
    formulaIntentHash: string;
    variableBindingSetHash: string;
    filterSetHash: string;
    identityTupleHash: string;
    packageSignatureHash: string;
    hashAlgorithmVersion: string;
  }>;
}
```

### 10.3 What M4 service does NOT expose

- No HTTP/REST routes.
- No MCP tool wrappers.
- No CLI commands.
- No bc-admin UI integration.
- No bc-portal integration.

External surfaces are M14 (publication endpoint), M15 (supersession endpoint), M12 (UI), and downstream MCP gates (separate operator decisions).

### 10.4 Operator decision

| # | Decision | Recommendation |
|---:|---|---|
| D-10 | Service location: `bc-core/src/registry/mcf/` | YES (BCF pattern) |
| D-11 | Service language: TypeScript via Drizzle ORM | YES |
| D-12 | One service class or split into per-action services (e.g. `McfCertWriterService` + `McfTransitionService`)? | Recommend ONE class for now. Split later if surface grows. |
| D-13 | M4 ship test substrate: synthetic mcv rows in a setup helper that the integration tests use? | YES (mirrors M3 post-apply verifier pattern with INSERT-then-ROLLBACK discipline) |

---

## 11. Non-responsibilities (recap)

M4 explicitly does **NOT** ship:

- Formula AST canonicalization or parsing (M7).
- Package signature hash composition (M8).
- Self-verification fixture substrate (M9) or verifier engine (M10).
- Metric Authoring Panel substrate (M5) or execution (M11).
- Metric Publication Panel substrate or execution (M12).
- PE-MC-1..PE-MC-10 check logic (M11; M4 only persists results).
- REST or MCP endpoints (M14 / M15 / separate endpoint gates).
- bc-admin authoring UI (M12 UI gate).
- bc-portal integration.
- Tenant binding lifecycle / MLS 15-25 substrate (M6 + D392).
- Reservoir intake hygiene (M11).
- BCF writes (BCF arc).
- `bc-postgres` MCP write-access widening.
- Hash algorithm implementation (M7/M8; M4 only declares the interface).
- Validation that a panel actually ran (M11 substrate ownership).
- Validation that an `operator_confirm_rule` matches the transition (substrate-level; M3 trigger + future M4 substrate may add).

---

## 12. Risks and stop conditions

### 12.1 Risks

| # | Risk | Severity | Mitigation |
|---:|---|---|---|
| R-1 | Hash algorithm not yet specified at M4 ship time. M4 ships with `MockMcfHashComputer` only; real authoring blocked until M7/M8. | Medium | Acceptable per §7.3 — M4 ships the interface; M7/M8 ship the implementation. Document the dependency clearly in M4 DBCP. |
| R-2 | Cross-framework cert coupling: BCF + MCF both write to `contract.certification_record`. If column shape diverges (e.g. BCF needs a field MCF doesn't, or vice versa), the shared shape breaks. | Medium (per build plan R-13) | MCF writes rows scoped by `governance_scope = 'mcf'`. No new columns added by M4. If shape gap surfaces at M11+ panel implementation, revisit per MCF §19.10 Q26. |
| R-3 | `contract.operator_confirm_rule` schema is BCF-shared; MCF seed rows may conflict with BCF rules if naming collides. | Low | Use `mcf_*` prefix in `rule_uid`; specify `scope = 'mcf'` in every MCF rule row. |
| R-4 | Transaction lifetime: holding a DB tx open while assembling PE-MC results (which could query large evidence corpora) could starve connection pool. | Medium | M4 service contract requires caller to pre-assemble the cert payload BEFORE invoking the M4 method. M4 only writes; it doesn't compose. |
| R-5 | Idempotency: a retry of `activateMetric` after a network blip but before the client knows the tx committed could try to write a duplicate cert. The M3 trigger would still succeed (it just needs ONE matching cert) but operator audit shows two. | Low | Recommend M4 service accept an optional `idempotencyKey` that, if present, prevents duplicate certs. DBCP will refine. |
| R-6 | M11 panel substrate (M5) doesn't exist yet. M4 cert writes for `metric_create` have a `panel_run_uid` column that has no FK target yet. | Low | Column is already nullable on `contract.certification_record`. No FK at M4. When M5 ships and `mcf.metric_authoring_panel_run` exists, a future amendment can add the FK. |
| R-7 | Hash population sequencing: M4 calls `computeAllForApproval()` BEFORE the state UPDATE; if the hash computer throws between hashes-written and state-update, parent has new hashes but state stays `'review'`. | Low | Wrap hash UPDATE + state UPDATE in single tx — both succeed or both roll back. M4 service contract enforces. |
| R-8 | Supersession atomicity: predecessor state UPDATE + supersession-row INSERT + successor state check all in one tx. If successor is concurrently being un-activated (e.g. another supersession-of-successor running), the trigger could see a flipping state. | Medium | Use `SELECT FOR UPDATE` on successor MCV row at the start of `supersedeMetric` tx to serialize against other ops on the same successor. |
| R-9 | PE-MC eligibility result table (`mcf.metric_publication_eligibility_result`) shape is M4-owned; the PE-MC check execution that fills it lives in M11. If M11 emits results in a shape M4 doesn't accept, panel runs are blocked. | Medium | M4 DBCP specifies the table schema explicitly; M11 must match. Coordination between M4 + M11 DBCPs. |
| R-10 | `metric_create` cert is service-contract-only (no M3 trigger enforces). A buggy non-M4 writer could create MCs without certs, producing un-audited rows. | Medium (per M3 DBCP §8.3) | M11 panel run service is the only intended writer; its tests must cover the cert-write step. Discipline-only; no substrate gate. |

### 12.2 Stop conditions

DBCP authoring (the next gate) should STOP and re-frame if any of these surface:

- Hash algorithm spec turns out to require M4 to know things M7/M8 haven't published (e.g. a hash composition that depends on data only M4 has access to). Re-decide whether M4 owns hash population (Option A from §7).
- Operator-confirm rule schema turns out to require predicate AST evaluation that M4 substrate doesn't support. Defer to a separate operator-confirm engine gate.
- PE-MC eligibility result table requires references to substrate that doesn't exist yet (`mcf.metric_self_verification_result` from M9). Recommendation: ship M4 with the table + the PE-MC-10 row's reference column nullable; tighten when M9 ships.
- The single-tx pattern breaks under load testing (long-running cert composition holds the tx open). Re-decide Option A vs Option B.

---

## 13. Operator decisions required before M4 DBCP

These are the named decisions from §§1-10 that the operator must take before the DBCP design can be authored. Numbered for ease of reference.

### 13.1 Scope decisions

| # | Decision | Recommendation | Source |
|---:|---|---|---|
| D-1 | M4 scope: narrow per build plan (PE eligibility substrate + operator_confirm_rule seeding only) OR bundled per operator framing (PE substrate + all 3 cert writers + transition service + operator_confirm seeding) | **Bundled** — preflight authored under this framing. DBCP may still split implementation into multiple sub-PRs for sequencing. | §1.5 |

### 13.2 Transaction discipline decisions

| # | Decision | Recommendation |
|---:|---|---|
| D-2 | Cert INSERT + state UPDATE: single tx (Option A) or two tx with idempotency (Option B) | Option A — single tx |
| D-3 | Service methods support `dryRun: boolean` parameter? | YES — for development ergonomics, mirrors M3 verifier pattern |

### 13.3 Hash population decisions

| # | Decision | Recommendation |
|---:|---|---|
| D-4 | Hash population: M4 computes (A) / separate service called by M4 (B) / block until M7/M8 (C) | Option B — separate service via `McfHashComputer` interface |
| D-5 | M4 PR includes `MockMcfHashComputer` for test fixtures? | YES |

### 13.4 Operator-confirm decisions

| # | Decision | Recommendation |
|---:|---|---|
| D-6 | Per-transition operator-confirm matrix (§8.1) | Always-confirm at `approved → active` + `active → superseded`; AI-default elsewhere |
| D-7 | Seed `operator_confirm_rule` rows in M4 PR DDL vs runtime service seed | M4 PR ships DDL INSERT statements (apply via separate DCP gate) |
| D-8 | Seed `framework_policy` row for `scope='mcf'`? | YES — required for cert's `policy_version` reference |
| D-9 | Operator-confirm at `intake → draft`? | NO — panel APPROVE is authoring authority |
| D-10 | Include a non-cert audit row at `draft → review` for symmetry? | NO — review-entry is a low-risk state UPDATE; no audit needed |

### 13.5 Service contract decisions

| # | Decision | Recommendation |
|---:|---|---|
| D-11 | Service location: `bc-core/src/registry/mcf/` | YES (BCF pattern) |
| D-12 | Service language: TypeScript + Drizzle | YES |
| D-13 | Single service class or per-action split | Single class (`McfCertWriterService`) |
| D-14 | M4 ships test substrate (synthetic mcv rows in setup helper) | YES (mirrors M3 verifier pattern) |

### 13.6 Substrate decisions

| # | Decision | Recommendation |
|---:|---|---|
| D-15 | `mcf.metric_publication_eligibility_result` table shape: per-PE-MC-row or single-JSONB-blob row? | Recommend per-PE-MC-row (10 rows per publication) — finer query granularity; matches `gate_results_json` audit needs |
| D-16 | Foreign key from `mcf.metric_publication_eligibility_result` to `mcf.metric_self_verification_result` (PE-MC-10) — defer until M9 ships? | YES — column nullable + FK-less at M4; tighten when M9 ships |
| D-17 | Should M4 add an index on `contract.certification_record (governance_scope, action_code, primitive_id)` for MCF query support? | Recommend YES — enables fast lookup of "all metric_transition certs for this MCV". Verify with `pg_describe_table` whether existing indexes cover this. |

### 13.7 Cross-framework decisions (deferred)

| # | Decision | Notes |
|---:|---|---|
| D-18 | Should MCF rules in `contract.operator_confirm_rule` be prefixed (`mcf_*`) and scope-tagged to avoid collision with BCF? | Working position: YES — `rule_uid` carries `mcf_` prefix; `scope = 'mcf'`. DBCP can refine. |
| D-19 | Cert reuse holds at M4 (confirms M3 D-12 stance) — `contract.certification_record` is shared; no `mcf.certification_record` sibling | YES — affirms M3 D-12. Re-decide only if column-shape gap surfaces at M11+. |
| D-20 | Override discipline: M4 service accepts `override_gate_code` / `override_rationale_text` / `override_followup_task_uid` from caller? | YES — mirror BCF pattern; cert columns already exist |

---

## 14. Recommended next gate

### 14.1 Recommendation: docs-only DBCP design next

**Next gate: open MCF M4 DBCP design as a docs-only operator-authorized session.** Deliverable: `bc-docs-v3/docs/implementation/metric-context-framework-m4-lifecycle-certification-dbcp.md`, modeled on the M3 DBCP doc.

DBCP scope (the design doc, not this preflight):
- Resolution of all 20 decisions D-1 through D-20 (preflight defaults can carry forward unless operator decides otherwise)
- Exact column list for `mcf.metric_publication_eligibility_result` table
- Exact TypeScript interface for `McfCertWriterService` methods (including precise input/output types)
- Exact transaction shape for each method (Drizzle ORM idiom)
- `McfHashComputer` interface specification (what M7/M8 must provide)
- DDL for new index on `contract.certification_record` if D-17 accepts
- DDL for `operator_confirm_rule` + `framework_policy` seed rows
- Service-level validation rules per cert action code
- Test plan (positive + negative cases per method; mock hash computer test substrate)
- Migration/apply ordering (DDL apply via separate DCP; service merge via PR)
- Rollback story

### 14.2 Why this matches M2 + M3 pattern

M2 + M3 ran as: preflight → DBCP → execution PR → DDL apply across four discrete operator gates. M4 is at least as complex (service code + DDL for one new table + seed rows + interface + test substrate; 20 operator decisions in this preflight). Following the same four-gate pattern preserves the discipline that worked.

### 14.3 What follows DBCP design

When the DBCP design is signed off (all 20 decisions resolved + design accepted):

1. **bc-core implementation PR** — new files under `src/registry/mcf/` (cert writer service + interface + mock + spec) + new DDL file (`docker/redesign/06-mcf-publication-eligibility.sql` or similar) for the PE result table + seed rows + verifier script. PR carries `NO DB APPLY` discipline matching M2 + M3 pattern. **NOT OPENED in this preflight.**
2. **DDL apply** — separate operator-authorized Database Change Protocol session (matching M2 + M3 apply gates). **NOT OPENED in this preflight.**
3. **Post-apply audit artifacts** — committed to bc-core (matching M2 PR #102 + M3 PR #104 pattern). **NOT OPENED in this preflight.**
4. **Synthetic-row service test** — once substrate is live, M4 service can be exercised against synthetic mcv rows (INSERT-then-ROLLBACK pattern) to confirm cert + state UPDATE composes correctly with M3 triggers. **Part of the implementation PR's test plan, not a separate gate.**

### 14.4 What stays closed

- **M4 DBCP design** — operator authorizes next; not opened here.
- **M4 implementation PR** — pending DBCP sign-off.
- **M4 DDL apply** — pending implementation PR.
- **M5** (panel substrate) — depends on M4.
- **M7-M10** (formula AST, package signature, fixture, verifier) — sequenced after M4.
- **M11/M12** (authoring + publication panel execution) — depends on M5 + M7 + M8 + M9 + M4.
- **M14 / M15** (publication + supersession endpoint surfaces) — depend on M4 + M11.
- **Step-4-bis** (Metrics 3 + 6 BCF enrichment) — parallel workstream; not in this gate.
- **MCF metric contracts** — none authored; tables stay empty until M11 ships.
- **BCF data** — untouched.
- **bc-postgres MCP write access** — unchanged (`allow_write: false`).
- **`PGMCP_SCHEMAS` `mcf` addition** — deferred until a session actually queries `mcf.*` through bc-postgres MCP.

---

## Document verification

- **All 14 required sections present** (§1 Scope and grounding; §2 Current live M2 + M3 substrate recap; §3 Why M4 is needed; §4 M4 responsibility boundary; §5 Transition inventory and state graph; §6 Transaction discipline options; §7 Hash population responsibility options; §8 Operator-confirm boundary options; §9 Cert row contract over contract.certification_record; §10 Service contract sketch, no endpoints; §11 Non-responsibilities; §12 Risks and stop conditions; §13 Operator decisions required before M4 DBCP; §14 Recommended next gate).
- **Discipline assertions hold** (§1.3) — zero DDL, zero bc-core schema edits, zero MCF metric contracts, no M5/M7/M8/M9/M11/M12 design, no REST/MCP endpoint design, no BCF writes, no cert rows written.
- **All 20 operator decisions enumerated** (§13) with recommended defaults — D-1 through D-20.
- **M4 boundary explicit** (§4) — 5 owned responsibilities + 12 explicit non-responsibilities.
- **Scope clarification preserved** (§1.5) — operator's bundled framing vs. build plan's M4/M14/M15 split presented as D-1 decision.
- **Recommendation unambiguous** (§14) — docs-only DBCP design next; mirror M2 + M3 four-gate pattern.
- **No code changes, no DDL, no DB writes, no schema modifications.** Doc-only commit to bc-docs-v3 main.
