---
uid: metric-context-framework-m13-pe-mc-evaluator-dbcp
title: MCF M13 PE-MC Evaluator DBCP
description: Design blueprint for MCF gate M13 — the Publication Eligibility / Metric-Contract (PE-MC) evaluator that consumes M12.5-materialized substrate (draft MCV + cert + fixture + verifier_result) and runs the 10 PE-MC checks (PE-MC-1 provenance, PE-MC-2 grain coherence, PE-MC-3 binding completeness, PE-MC-4 type/unit coherence, PE-MC-5 formula AST validity, PE-MC-6 temporal gate well-formedness, PE-MC-7 computed-dimension coherence, PE-MC-8 runtime-readiness intent, PE-MC-9 definition discipline, PE-MC-10 self-verification fixture pass — per MCF requirements §13 + ADR-f8f925). M13 is read-side from M12.5; it does not invoke M12.5 and does not require the M12.5 first operational run to have occurred. M13 computes the 6 parent-MC hash columns (formula_intent_hash, variable_binding_set_hash, filter_set_hash, identity_tuple_hash, package_signature_hash, hash_algorithm_version) and stamps them on `mcf.metric_contract` BEFORE the `review → approved` state transition (substrate trigger `mcf.fn_mcv_state_transition_check` enforces this hard). M13 owns MCV state transitions `draft → review → approved`; it does NOT do `approved → active` (M14) or `active → superseded` (M15) or tenant runtime publication (M18+). M13's substrate work delegates to the existing M4 `McfCertWriterService.submitForReview` + `approveForActivation` which already implements parent-hash stamping + PE row INSERT + state UPDATE atomically; M13 is the orchestrator + check engine. Idempotency mirrors M12.5: substrate-level UNIQUE on PE result rows + service-level retry detection by (MCV uid, evaluator version, package signature hash). 8 HA assertions HA-1..HA-8 locked. NO operational materialization. NO synthetic M11/M12 data. NO seed runs. NO real model API calls. NO BCF writes. NO legacy `metric.*` writes. NO tenant runtime writes. NO bc-admin changes. `bc-postgres` MCP `allow_write=false`. DBCP-only — no bc-core code, no DDL apply, no DB write.
status: draft
date: 2026-05-28
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m13-pe-mc-evaluator-dbcp
---

# MCF M13 PE-MC Evaluator DBCP

## 0. Scope and discipline

DBCP-only design pass. No bc-core implementation, no DDL apply, no DB write, no seed run, no real model API call, no operational materialization. `bc-postgres` MCP `allow_write=false` throughout.

**Baseline at DBCP-author time:**
- `bc-core` main = `2da35d05447c16b2297e18acc1ccfebdc5d0559f`
- `bc-docs-v3` main = `8cf850e33ee4b5dbbeb5b9cd7b474f8b1b825f03`
- `barecount-devhub` main = `2ea9efc53cc9a3b83c9b4bf8e5a3936c54398566`
- All 17 `mcf.*` tables = 0; `contract.panel_output_record = 24`; `contract.authoring_panel_rejection_log = 1`; `idx_mcf_mc_mc_name_active` present.

## 0bis. Substrate-enforced authority model — corrective addendum (2026-05-28)

**Effective from this addendum.** Post-M12.5 independent architectural assessment surfaced framing errors in §2.7 HA-5, §3 D-M13-8/9, §5.1 `RunEvaluationOpts`, §5.2 Step 6b, and §7 HA-5/HA-8 of the originally-drafted DBCP. The underlying architecture is unchanged; the wording is corrected to align with what the substrate already enforces.

**The substrate-enforced cert chain (one decisive piece of evidence).** The CHECK constraint `mcf_cert_state_transition_chk` on `mcf.certification_record` enumerates exactly three permitted cert shapes — no others are storable:

```sql
CHECK (
  (action_code = 'metric_create'      AND from_state_code IS NULL     AND to_state_code = 'draft')
  OR (action_code = 'metric_transition' AND from_state_code = 'approved' AND to_state_code = 'active')
  OR (action_code = 'metric_supersede'  AND from_state_code = 'active'   AND to_state_code = 'superseded')
)
```

Combined with `mcf_cert_subject_kind_chk` (subject_kind ∈ {`metric_contract_version`, `metric_publication`, `metric_supersession`}), this enumerates exactly **three authority events**, each with its own subject:

| Authority event | Cert (action_code → subject_kind) | Gate owner |
|---|---|---|
| Authority CREATED | `metric_create` → `metric_contract_version`; `from=NULL → to=draft` | M12.5 |
| Authority PUBLISHED | `metric_transition` → `metric_publication`; `from=approved → to=active` | M14 |
| Authority SUPERSEDED | `metric_supersede` → `metric_supersession`; `from=active → to=superseded` | M15 |

**M13 emits NO certification record.** The substrate `mcf_cert_state_transition_chk` REFUSES to store any cert for `draft → review` or `review → approved`. These two transitions are intentional **uncertified eligibility milestones** on the MCV's `governance_state_code` column. The substrate column comment on `mcf.metric_publication_eligibility_result.certification_record_id` corroborates this: *"NULL for pre-approve checks (approveForActivation records PE-MC-1..PE-MC-9 results before any cert is written)"*.

**M13's audit ledger is the PE-MC row, not a cert.** Two PE-row subtypes coexist by substrate design:

| Subtype | Writer | `certification_record_id` | Records what |
|---|---|---|---|
| **Pre-approve evidence** | M13 (this DBCP) | `NULL` | The 10 PE-MC verdicts at the time M13 ran. Independent of any later authority event. |
| **Activation evidence** | M14 (`activateMetric`) | populated with the activation cert id (`metric_transition` → `metric_publication`) | The 10 PE-MC verdicts cited at the publish event. M14 DBCP chooses whether to re-evaluate or re-cite M13's verdicts. |

`mcf.metric_publication_eligibility_result` carries no immutability trigger (verified by reading `pg_trigger` for the table — none with `BEFORE DELETE OR UPDATE`); both subtypes coexist append-only by service-side discipline + the substrate's lack of an UPDATE/DELETE pathway from M13's flow. M13 NEVER mutates an existing PE row.

**M13's actual write surface (corrected from §2.7 / §7 HA-5).** Per evaluation:

- `mcf.metric_contract` 6-hash UPDATE on one row (parent MC hashes stamped by M4 inside `approveForActivationInTx` BEFORE the MCV state transition; required by trigger `mcf.fn_mcv_state_transition_check`'s `review → approved` precondition).
- Up to 10 `mcf.metric_publication_eligibility_result` rows INSERT, each with `certification_record_id = NULL`.
- 2 `mcf.metric_contract_version` UPDATEs (governance_state_code: `draft → review`, then `review → approved` only if eligible).
- **0** `mcf.certification_record` rows. Substrate constraint forbids them for M13's transitions.

**Why the original §2.7 / §7 HA-5 was wrong.** It claimed "≤ 1 cert (M4-emitted)". Live M4 source verifies:

- `submitForReviewInTx` (`bc-core/src/registry/mcf/mcf-cert-writer.service.ts:922-935`): only UPDATEs `governanceStateCode='review'`. Zero `insertCert` calls.
- `approveForActivationInTx` (`bc-core/src/registry/mcf/mcf-cert-writer.service.ts:1064-1126`): UPDATE parent MC hashes → `insertPeResultRows(tx, mcv, null, peResults)` (note `null` certId on line 1108) → UPDATE MCV state. Zero `insertCert` calls.
- The cert at activation is emitted only by `activateMetricInTx` (`:1213-1269`), which is M14's territory.

**Implication for the rest of the DBCP.** The HA-5 row (both §2.7 and §7) is corrected to "0 certs" (see corrected statements below). The `RunEvaluationOpts` interface in §5.1 drops `certifierSub` / `certifierEmail` (M4's `submitForReview` and `approveForActivation` consume `actorSub` + `actorRoleAtAction` only). D-M13-8 + D-M13-9 are jointly resolved as follows:

- **D-M13-9 (evaluator_version column placement + bump policy).** Stamp `verifier_version=<current M13_EVALUATOR_VERSION>` on all 10 PE rows; PE-MC-10 additionally records the M10 verifier's version inside `evidence_json.verdict_signals.m10_verifier_version` to preserve the M10-vs-M13 actor split without a new column. Current value: **`'mcf-m13-v2'`** (was `'mcf-m13-v1'` through PR #206; bumped to v2 in PR #207 / DEC-3f093f / D426 after PE-MC-1 + PE-MC-6 semantic changes — see the full D-M13-9 row in §3 for the version-bump policy).
- **D-M13-8 (substrate UNIQUE).** The unique key MUST include `current_package_signature_hash` (which lives in `evidence_json`) — otherwise §6.3 stale-package retry contradicts §10.1 PR-1 by attempting to INSERT rows that would violate a 3-tuple unique (same MCV / check / evaluator, only package_hash differs). The corrected PR-1 DDL uses a **partial expression unique index**: `CREATE UNIQUE INDEX idx_mcf_mper_mcv_check_eval_pkg ON mcf.metric_publication_eligibility_result(metric_contract_version_uid, pe_check_code, verifier_version, COALESCE(evidence_json->>'current_package_signature_hash', '')) WHERE verifier_version IS NOT NULL`. This permits stale-package retry to emit new rows (different `evidence_json->>'current_package_signature_hash'`) while still rejecting true duplicates (same all four). Mirrors M10's `uq_msvr_fixture_version_pkg_hash` pattern (fixture + verifier_version + bound_package_signature_hash_at_run).

§5.2 Step 6b clarifies that the "NOT approve_eligible" branch INSERTs PE rows via `tx.insert(metricPublicationEligibilityResult).values(...)` directly — no `recordEligibility` helper exists on M4.

The body of the DBCP below is updated in place to reflect these corrections. Where wording carries through unchanged, the corrected interpretation supersedes.

## 1. Authority

- ADR: `bc-docs-v3/docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) — MCF Build Plan
- ADR: `bc-docs-v3/docs/adrs/ADR-f8f925.md` line 145 — PE-MC-1..PE-MC-10 canonical definition per MCF requirements §13
- M12.5 DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md` (`52fb8bc` + §0 PR-2 implementation addendum at `aa12b04`) — upstream gate; locks the substrate M13 consumes
- M12.5 closeout: `bc-docs-v3/docs/implementation/mcf-m12-5-implementation-closeout.md` (`8cf850e3`) — code-live + substrate-proof complete + first-operational-run pending
- Post-M12.5 architecture audit (this session) — locks the 6 audit-derived constraints (read-side; parent-MC hash stamping; state transitions limited; substrate trigger respect; PE-MC result semantics; idempotency model)
- M4 cert writer DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m4-lifecycle-certification-dbcp.md` (`3983530`) — `submitForReview` + `approveForActivation` are M4's existing capabilities that M13 reuses
- M7/M8 hash authority DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m7-m8-formula-hash-authority-dbcp.md` (`62ec707`) — hash computation services M13 uses to stamp parent MC
- M9 fixture DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m9-fixture-substrate-dbcp.md` (`620e11d`) — `FixtureStructuralCheckService.runStructuralChecks` for PE-MC-5 re-assertion
- M10 verifier DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m10-self-verification-result-dbcp.md` (`ea8b708`) — `MetricSelfVerificationService.verifyFixture` output is the substrate PE-MC-10 consumes

## 2. Audit-derived constraints locked

The 6 constraints below are imported from the post-M12.5 architecture audit and become DBCP gates.

### 2.1 M13 is read-side from M12.5 outputs (Audit Invariant I)

M13 service code:
- MUST NOT import `MetricAuthoringMaterializationService`
- MUST NOT invoke `runMaterialization`
- MUST NOT write `mcf.metric_authoring_panel_run`, `mcf.metric_authoring_panel_transcript`, `mcf.metric_authoring_intake_queue`, `mcf.metric_self_verification_fixture`, `mcf.metric_self_verification_result`
- MUST NOT write `contract.panel_output_record` or `contract.authoring_panel_rejection_log` (BCF)
- MUST NOT write any legacy `metric.*` table
- MUST be runnable starting from substrate populated by M12.5 (does NOT assume a prior operational first run; M13 unit + integration specs synthesize M12.5 outputs via the M4 cert writer service path under SAVEPOINT rollback)

### 2.2 M13 owns parent MC hash stamping (Audit L-1)

Parent `mcf.metric_contract` columns NULL after M12.5:
- `formula_intent_hash`
- `variable_binding_set_hash`
- `filter_set_hash`
- `identity_tuple_hash`
- `package_signature_hash`
- `hash_algorithm_version`

M13 computes these via the M7/M8 services (already used by M12.5 at TX B):
- `FormulaCanonicalizationService.computeFormulaIntentHash(mcvUid, deps)`
- `FormulaCanonicalizationService.computeVariableBindingSetHash(mcvUid, deps)`
- `FormulaCanonicalizationService.computeFilterSetHash(mcvUid, deps)`
- `PackageSignatureService.computePackageSignatureHash(mcvUid, {formulaIntentHash, variableBindingSetHash, filterSetHash}, deps)` — composes the package_signature_hash
- An identity-tuple-hash computer (per M7/M8 §10) — composes from the 6 identity inputs (formula_intent_hash + variable_binding_set_hash + filter_set_hash + grain_entity_id + temporal_gate_shape_code + temporal_gate_params_kernel)
- `hash_algorithm_version` constant = `'mcf-hash-v1'` (per D-M9-A1 forever-lock)

M13 stamps these via M4 cert writer's existing `approveForActivation`, which already computes hashes via `this.hashComputer.computeAllForApproval` (`mcf-cert-writer.service.ts:1086-1089`) and writes them in the same tx as the `review → approved` MCV UPDATE. M13 does NOT write hashes directly — it invokes M4 with the PE results.

### 2.3 M13 state transitions are limited (Audit Invariant II + L-2)

M13 owns:
- `draft → review` via `McfCertWriterService.submitForReview`
- `review → approved` via `McfCertWriterService.approveForActivation` (passes `peEligibilityResults`)

M13 MUST NOT:
- `approved → active` — M14 owns this (`activateMetric`)
- `active → superseded` — M15 owns this (`supersedeMetric`)
- Create `mcf.metric_supersession` rows
- Publish to tenant runtime — M18+ owns this; tenant runtime continues to read legacy `metric.metric_definition` corpus per `bc-docs-v3/docs/operating-model/mcf-legacy-bridge.md`

### 2.4 M13 must respect substrate trigger `mcf.fn_mcv_state_transition_check` (Audit Invariant III)

Live trigger behavior (read from substrate at DBCP-author time via `bc-postgres` MCP):

```
INSERT path: NEW.governance_state_code must be 'draft' — else CHECK violation.

UPDATE path on governance_state_code:
  draft → review        — permitted unconditionally
  review → approved     — permitted ONLY IF parent MC's 6 hash columns are all NOT NULL:
                          formula_intent_hash, variable_binding_set_hash, filter_set_hash,
                          identity_tuple_hash, package_signature_hash, hash_algorithm_version
                          (else CHECK violation)
  approved → active     — permitted ONLY IF matching metric_transition cert exists in
                          mcf.certification_record with from_state_code='approved',
                          to_state_code='active' (M14's concern, not M13)
  active → superseded   — permitted ONLY IF mcf.metric_supersession row exists with
                          successor at state='active' AND is_current=TRUE (M15's concern)

Any other transition: rejected with 'invalid mcf state transition: <old> -> <new>'.
```

M13's submitForReview triggers the trigger BEFORE INSERT OR UPDATE OF governance_state_code; the trigger's UPDATE-path branch is satisfied because draft → review is permitted unconditionally. M13's approveForActivation triggers it AGAIN; the trigger checks that parent MC's 6 hash columns are stamped (M4 stamps them in the same tx, BEFORE the state UPDATE — `approveForActivationInTx` ordering verified in `mcf-cert-writer.service.ts:1093-1115`).

M13 DBCP test plan §11 includes negative tests proving substrate rejects illegal transitions (premature approval without hashes, skip-state, reverse-state).

### 2.5 M13 PE-MC result semantics

| Field | Substrate column | M13 source |
|---|---|---|
| Verdict codes | `mcf.metric_publication_eligibility_result.verdict_code` enum {PASS, REJECT, OPERATOR_REVIEW} | M13 computes per check; substrate enforces via `mper_verdict_code_chk` |
| Check codes | `mcf.metric_publication_eligibility_result.pe_check_code` enum {PE-MC-1, …, PE-MC-10} | M13 emits per check; substrate enforces via `mper_pe_check_code_chk` |
| Inputs hashed | Composed per check (see §4.4) | Captured into `evidence_json.input_hash` for audit |
| Result payload | `mcf.metric_publication_eligibility_result.evidence_json` | M13 populates with check-specific evidence schema (see §4.4) |
| MC eligibility | Verdict aggregation across all 10 PE-MC rows (see §4.5) | M13 computes; only "all PASS" advances MCV to approved |
| Failed PE-MC preservation | PE result rows are append-only (substrate-side) per Invariant V; failed verdicts remain as historical evidence | M13 NEVER deletes or overwrites prior PE rows |

**Per §0bis corrective addendum — PE-row dual subtype.** Two PE-row subtypes coexist by substrate design:

| Subtype | Writer | `certification_record_id` | Records what |
|---|---|---|---|
| **Pre-approve evidence** (M13's surface) | M13 (this DBCP) | `NULL` | The 10 PE-MC verdicts at the time M13 ran; independent of any later authority event |
| **Activation evidence** (out of M13 scope) | M14 (`activateMetric`) | populated with the activation cert id | The 10 PE-MC verdicts cited at publish; M14 DBCP decides whether to re-evaluate or re-cite M13's verdicts |

M13 writes only the pre-approve subtype. The activation subtype is M14's territory. Both subtypes coexist append-only.

PE-MC failure semantics:
- One or more REJECT verdicts ⇒ MCV stays at `review`; M13 does NOT call `approveForActivation`. Operator inspects evidence; remediation path is supersession (M15) — NOT amendment of the MCV.
- One or more OPERATOR_REVIEW verdicts ⇒ MCV stays at `review`; operator inspects evidence + decides PASS or REJECT. M13 may re-run (idempotent retry per §6) once operator-supplied additional inputs are present. No state change in the substrate until M13 re-runs and the verdicts flip to all-PASS; the new run emits a fresh set of PE rows per §6.3 stale-package retry semantics. **No cert is emitted at this step** (per §0bis — M13 never writes `mcf.certification_record`).
- All PASS ⇒ M13 calls `approveForActivation`; MCV transitions to `approved`; parent MC hashes stamped; PE rows persisted in same tx as the MCV UPDATE.

### 2.6 M13 idempotency model

Mirrors M12.5's pattern of substrate-level UNIQUE + service-level retry detection. **Three idempotency surfaces:**

1. **Service-level retry detection (mirrors `findExistingMaterialization`).** M13 service exposes `findExistingEvaluation(mcvUid, evaluatorVersion, packageSignatureHash)` which queries the existing PE rows for this MCV that match the (evaluator_version, package_signature_hash) tuple. If 10 PE rows already exist for this triple, return existing `pe_result_uid[]` + verdicts without re-running.
2. **Substrate-level idempotency for the M4 `approveForActivation` invocation.** M4 already has the `mcf.metric_cert_writer_idempotency` table for `approveForActivation`-style calls (per M4 DBCP §11.5); M13 passes an `idempotencyKey` of the form `mcf-m13-pe-mc/<mcv_uid>/<evaluator_version>/<package_signature_hash>` so the M4 layer catches double-submits transparently.
3. **PE row substrate UNIQUE — 4-tuple including package hash (per §10.1 PR-1).** The unique key MUST include `current_package_signature_hash` so that stale-package retry (which emits NEW rows for a NEW hash on the same MCV/check/evaluator) is permitted while true duplicates (same MCV/check/evaluator/hash) are rejected. Since `current_package_signature_hash` lives inside `evidence_json` (not its own column), the substrate uniqueness uses a **partial expression unique index** on `(metric_contract_version_uid, pe_check_code, verifier_version, COALESCE(evidence_json->>'current_package_signature_hash', ''))` WHERE `verifier_version IS NOT NULL`. M13 catches the UNIQUE violation + SELECTs existing per the M12.5 PR-1 / `idx_mcf_mc_mc_name_active` pattern.

**Why the package_hash is part of the uniqueness surface (rationale).** A 3-tuple `(mcv, check, evaluator_version)` unique constraint would block stale-package retry (§6.3) because the MCV/check/evaluator triple is identical across the prior and the new evaluation; only the package hash differs. Including the package hash in the unique surface makes the substrate distinguish "true duplicate" from "new evaluation against a changed substrate." This is the same conceptual move as M10's `uq_msvr_fixture_version_pkg_hash` which keys verifier results by `(fixture, verifier_version, bound_package_signature_hash_at_run)` — same pattern, applied to PE rows.

**Stale-substrate handling (per MCF §12.7 stale-fixture rule):** if M13 re-runs and the current `package_signature_hash` (recomputed from MCV substrate) differs from the previously-recorded `package_signature_hash` in the prior PE row, the prior PE rows are considered stale. M13 emits NEW PE rows with the new `package_signature_hash` + records the prior result's `pe_result_uid[]` in `evidence_json.superseded_by_stale_package_change`. Prior rows are NOT mutated (Invariant V — append-only). The 4-tuple expression unique index above permits this exactly.

### 2.7 M13 HA assertions

| HA | Statement | Enforcement |
|---|---|---|
| HA-1 | No activation / publication writes | M13 service does NOT call `activateMetric` / `supersedeMetric`; unit test asserts; integration spec asserts MCV stops at `approved`, not `active` |
| HA-2 | No tenant runtime writes | M13 does NOT touch `boundary/metric.service.ts`, `ReadinessLedgerService`, `chain-status.service.ts`, or any `tbc_*` schema |
| HA-3 | No legacy `metric.*` writes | M13 source has zero imports of `MetricDefinitionService` / `MetricDefinitionRepository`; integration spec asserts legacy `metric.metric_definition` / `metric.metric_knowledge` / `metric.metric_binding` row counts preserved |
| HA-4 | No BCF writes | M13 source has zero INSERT/UPDATE/DELETE against `contract.*` tables; integration spec asserts `contract.panel_output_record` + `contract.authoring_panel_rejection_log` row counts preserved exactly |
| HA-5 | Exact MCF write surface per evaluation: parent MC hash UPDATE (6 cols) + up to 10 PE result rows (each with `certification_record_id=NULL`) + 2 MCV state UPDATEs (`draft→review` then `review→approved` if eligible) + **0 certification records** (substrate `mcf_cert_state_transition_chk` forbids certs for these transitions; see §0bis) | Integration spec asserts row deltas: `mcf.metric_publication_eligibility_result` += {1..10}; `mcf.metric_contract` 6-col UPDATE on one row; `mcf.metric_contract_version` governance_state UPDATE on one row (transitions through 2 states); `mcf.certification_record` += 0 (asserted exact-zero) |
| HA-6 | Parent hash stamping happens BEFORE `review → approved` state UPDATE in the same tx | M4 `approveForActivationInTx` ordering verified live (`mcf-cert-writer.service.ts:1093-1115`): UPDATE parent MC hashes → INSERT PE rows → UPDATE MCV state. Integration spec proves substrate trigger rejects out-of-order via negative test |
| HA-7 | Idempotent retry returns existing PE results | `findExistingEvaluation` short-circuits with cached UIDs + intake unchanged; integration spec asserts same `pe_result_uid[]` returned on second call |
| HA-8 | Failed PE-MC preserves audit trail; does NOT revert MC/MCV substrate | PE rows are append-only via Invariant V; failed verdicts persist; MCV stays at `review` (M4 trigger `trg_mcf_mcv_descriptive_immutability` rejects any reverting UPDATE) |

### 2.8 M12.5 NestJS DI gap — explicitly out of M13 scope

Per the post-M12.5 architecture audit M-1 finding, the 7 MCF services (`McfCertWriterService`, `MetricAuthoringMaterializationService`, `MetricSelfVerificationService`, `FormulaCanonicalizationService`, `PackageSignatureService`, `FixtureStructuralCheckService`, `ReservoirIngestionService`) are not currently registered in any NestJS module. This is documentation-vs-implementation drift on M12.5's operator-facing surface; it does NOT block M13 design because M13's substrate consumption is via direct service construction (per the integration spec wiring pattern) + M4's existing `approveForActivation` API.

**M13 DBCP does NOT include NestJS module registration in PR-1/PR-2 scope.** A separate operator-authorized cleanup gate would add `bc-core/src/registry/mcf/mcf.module.ts` registering the 7 services + M13's own service. Until then, M13 operational invocation uses the same direct-construction pattern as M12.5's integration spec.

## 3. Open decisions (D-M13-1 .. D-M13-N) — operator review required

| # | Decision | Default | Alternatives |
|---|---|---|---|
| **D-M13-1** | M13 service shape: standalone class or extension of M4 cert writer | **Standalone** `MetricPublicationEligibilityEvaluatorService` in `bc-core/src/registry/mcf/`; delegates substrate writes to M4 cert writer | Extension (add `evaluateAndApprove` method directly on `McfCertWriterService`) — rejected; M4's role is substrate write, not check engine |
| **D-M13-2** | PE-MC check engine: per-check class or single class with 10 methods | **Single class with 10 private check methods** (`runPeMc1`, `runPeMc2`, …, `runPeMc10`) — mirrors M9 `FixtureStructuralCheckService` pattern | Per-check class (10 files) — rejected; over-decomposition for 10 cohesive checks on the same MCV substrate |
| **D-M13-3** | PE-MC-1 (provenance) substrate-side citation check | **Service-layer + M12 panel transcript hash assertion** — read `contract.panel_output_record.verdict_payload_json.grounding` + assert claims_total > 0 + claims_grounded == claims_total (no quarantined) | Substrate trigger reading transcript URIs — rejected; out of M13 scope per ADR-6c57e2 §144 (hardening follow-on) |
| **D-M13-4** | PE-MC-5 (formula AST validity) re-run: full M9 structural re-check or AST taxonomy guard only | **Full M9 `FixtureStructuralCheckService.runStructuralChecks` + `FormulaCanonicalizationService.validateAndNormalizeAst`** re-run inside M13 tx | AST guard only — rejected; M9 catches binding-vs-AST defects M7 alone cannot |
| **D-M13-5** | PE-MC-9 (duplicate-intent detection) scope: textual / semantic / hash-based | **`identity_tuple_hash` match against other MCs** — if a non-archived MC has the same `identity_tuple_hash`, verdict REJECT; otherwise PASS | Semantic LLM-based — rejected; non-deterministic; out of M13 scope |
| **D-M13-6** | PE-MC-10 (verifier pass) freshness window: any prior pass OR latest-only OR fresh-only | **Latest-only**: read `mcf.metric_self_verification_result` ordered by `evaluated_at` DESC LIMIT 1 for this MCV's fixture(s); verdict_code must be `'pass'` AND `bound_package_signature_hash_at_run` must equal the M13-computed current `package_signature_hash` (else stale per MCF §12.7) | Any prior pass — rejected (stale-fixture rule); fresh-only (re-run M10 inside M13 tx) — rejected (operator may choose to wire M13 + M10 re-run as a separate gate option) |
| **D-M13-7** | M13 idempotency-key scheme | **`mcf-m13-pe-mc/<mcv_uid>/<evaluator_version>/<package_signature_hash>`** | Per-check key (`mcf-m13-pe-mc/<mcv_uid>/PE-MC-<n>`) — rejected; M13's atomic unit is the 10-check batch, not per check |
| **D-M13-8** | New DDL (PR-1) needed for M13 | **Yes — partial expression unique index** keyed by `(mcv_uid, pe_check_code, verifier_version, COALESCE(evidence_json->>'current_package_signature_hash', '')) WHERE verifier_version IS NOT NULL`. The 4-tuple including the package hash from `evidence_json` is REQUIRED for the §6.3 stale-package retry to be permitted: a 3-tuple unique (MCV, check, evaluator) would reject the new rows because only the package hash differs across runs. Joint with D-M13-9: M13 stamps `verifier_version=<current M13_EVALUATOR_VERSION>` on all 10 PE rows, so the partial-WHERE covers every M13-written row. Crucially the index keys on `verifier_version` as a column (not on any literal value), so old `'mcf-m13-v1'` rows and new `'mcf-m13-v2'` rows coexist freely for the same `(mcv_uid, pe_check_code)` after an evaluator version bump (D-M13-9 policy) — old rows are not deleted; they remain as immutable historical evaluation evidence (Invariant V). Mirrors M10's `uq_msvr_fixture_version_pkg_hash` (fixture + verifier_version + bound_package_signature_hash_at_run). See §10.1 PR-1 DDL for the full statement. | (a) 3-tuple unique without package_hash — **rejected**, contradicts §6.3 stale-package retry. (b) No DDL (service-level idempotency only) — rejected; misses substrate-side guard against concurrent-retry duplicates. |
| **D-M13-9** | M13's `evaluator_version` constant + column placement + bump policy | **Current value: `'mcf-m13-v2'`** stamped on `mcf.metric_publication_eligibility_result.verifier_version` for **ALL 10 PE-MC rows** (PE-MC-1..PE-MC-10, not just PE-MC-10). Per §0bis corrective addendum: the column is named `verifier_version` historically but holds the **M13 evaluator version** for M13's pre-approve PE rows. To preserve the M10-vs-M13 actor split for PE-MC-10 (which cites a real M10 verifier_result), the underlying M10 verifier's version is recorded in `evidence_json.verdict_signals.m10_verifier_version` on the PE-MC-10 row only. No new substrate column needed; the dual stamping is documented in §4.4 evidence_json schema.  **Version history**: `mcf-m13-v1` (initial M13 PR-1/PR-2 through bc-core PR #206) → **`mcf-m13-v2`** (bc-core PR #207 / DEC-3f093f / D426 — PE-MC-1 changed to MCF-first grounding read with legacy `contract.panel_output_record` as fallback; PE-MC-6 changed to delegate well-formedness to `projectTemporalGateKernel` SSOT; PE-MC-8 unchanged). **Version-bump policy: any semantic change to PE-MC predicates (`runPeMc1`..`runPeMc10`) or to the §4.5 aggregation rule MUST bump `M13_EVALUATOR_VERSION` so cached PE rows from the prior semantic are not reused by `findExistingEvaluation`'s idempotency short-circuit.** The triplet `(mcv_uid, verifier_version, current_package_signature_hash)` is the idempotency cache key (see §6.2 + the M13 service `findExistingEvaluation` body); if either the substrate (package hash) or the evaluator semantics (version) changes, the cache must miss. Old PE rows under the prior version remain in-place as immutable historical evaluation evidence (Invariant V); M13 has zero DELETE statements against `mcf.metric_publication_eligibility_result`. The substrate partial unique index `idx_mcf_mper_mcv_check_eval_pkg` (D-M13-8) keys on `verifier_version` as a column so v1 and v2 rows coexist for the same `(mcv_uid, pe_check_code)` without conflict. **Naming convention** (cross-MCF): `<scope>-<module>-v<integer>` kebab-case; integer-only suffix (no `.1`, no date, no hash). Future bumps follow `vN → v(N+1)`. | Add new column `evaluator_version` — rejected; requires DDL beyond §10.1 minimal change; the JSON-path co-location works because PE-MC-10's evidence_json already carries verdict-specific signals. Reuse `'mcf-m13-v1'` after semantic change — **rejected**; would cause `findExistingEvaluation` to return cached pre-change verdicts for any MCV whose `package_signature_hash` did not also change, defeating the purpose of the new evaluator semantic. |
| **D-M13-10** | Service / DI registration | **Out of scope** per §2.8; M13 service exists in source but NestJS module registration is a separate operator-authorized cleanup gate | Include in PR-2 — rejected; expands scope; mirrors M12.5's stop-point |

## 4. PE-MC check engine — semantic specification

Each check produces exactly one PE row per evaluation. The 10 checks are mutually independent — none short-circuit; M13 always emits all 10 rows (verdict per row) so failed evaluations still record a full audit ledger. **Aggregation rule** (§4.5) decides whether M13 calls `approveForActivation` based on the 10 verdicts.

### 4.1 Substrate read surface (snapshot under outer tx)

M13 reads, all under one outer transaction with `FOR UPDATE` locks on parent MC + MCV (mirrors M4's `lockParentMcAndChildRows` pattern):

| Table | Purpose | Source service |
|---|---|---|
| `mcf.metric_contract_version` | MCV identity + AST + state | direct SQL |
| `mcf.metric_contract` | Parent MC identity + grain + temporal gate + null-hash columns | direct SQL |
| `mcf.metric_variable_binding` | All bindings of MCV | direct SQL + M7 read |
| `mcf.metric_filter_clause` | All filters of MCV | direct SQL + M7 read |
| `mcf.metric_computed_dimension_ref` | All computed dim refs of MCV | direct SQL + M8 read |
| `mcf.metric_self_verification_fixture` | Fixtures bound to this MCV | direct SQL |
| `mcf.metric_self_verification_result` | Verifier results for those fixtures | direct SQL |
| `mcf.certification_record` | Cert for this MCV's metric_create action | direct SQL via `primitive_id = mcv_uid AND action_code='metric_create'` |
| `contract.panel_output_record` | M12 panel run record (BCF) for PE-MC-1 grounding | direct SQL via `cert.panel_run_uid` |
| `mcf.metric_authoring_panel_run` | M12 panel run record (MCF mapr) for PE-MC-1 grounding cross-check | direct SQL |

### 4.2 PE-MC checks (canonical per MCF requirements §13 + ADR-f8f925 line 145)

| # | Check | Predicate (verdict PASS iff) | Predicate (verdict REJECT iff) | Verdict OPERATOR_REVIEW when |
|---|---|---|---|---|
| **PE-MC-1** | Provenance / grounding | `contract.panel_output_record.verdict_payload_json.grounding.claims_total > 0` AND `claims_grounded == claims_total` AND `claims_quarantined == 0` AND mapr `consensus_payload_json.grounding_check_passed == true` AND mapr `grounding_violations == []` | Any of: `claims_total == 0`, `claims_grounded < claims_total`, `claims_quarantined > 0`, `grounding_check_passed == false`, `grounding_violations.length > 0` | (none — deterministic) |
| **PE-MC-2** | Grain coherence (**dependency flag: see R-M13-8**) | All bindings whose `role_kind_code IN ('input', 'output')` resolve to BCs whose declared `entity_uid` is reachable from `mc.grain_entity_id` per BCF entity graph (or binding sets `bound_entity_id` matching `grain_entity_id` directly for grain bindings) | At least one input/output binding's BC entity is unreachable from grain | Entity graph reachability cannot be determined (BCF read fails) — fail closed |
| **PE-MC-3** | Binding completeness (AST `variable_ref.role` ↔ MCV `variable_role_code`) | Every AST `variable_ref` node's `role` field (per `formula-canonicalization.service.ts:149` — `node.role as string`) matches a row in `mcf.metric_variable_binding.variable_role_code` for this MCV | At least one AST `variable_ref.role` has no matching binding row | (none) |
| **PE-MC-4** | Type / unit coherence | All bindings' `representation_term_snapshot` + `unit_code_snapshot` + `data_type_snapshot` agree with M7-derived AST type expectations (e.g. arithmetic node requires numeric data_type on operands; comparison requires comparable types) | Snapshot disagrees with AST-derived type expectation | (none) |
| **PE-MC-5** | Formula AST validity | `FormulaCanonicalizationService.validateAndNormalizeAst` does NOT throw AND `FixtureStructuralCheckService.runStructuralChecks` returns `{passed: true, defects: []}` against fixture[0] of this MCV | `validateAndNormalizeAst` throws `InvalidAstError` OR structural check returns defects | (none) |
| **PE-MC-6** | Temporal gate well-formedness | `mc.temporal_gate_shape_code` is one of the 6 known shapes; `mc.temporal_gate_params_json` parses against the shape's expected param schema | Shape unknown OR params fail shape-specific schema | Shape valid but params have operator-supplied optionals that need review (e.g. anchor field overrides) |
| **PE-MC-7** | Computed-dimension coherence | Every `mcf.metric_computed_dimension_ref.source_business_concept_id` is reachable from `mc.grain_entity_id` AND `role_in_formula_code` matches a referenced node in the AST | Either source BC unreachable OR role not referenced in AST | (none) |
| **PE-MC-8** | Runtime-readiness intent — **DEFERRED-PASS until M18+** | MCV declares all the runtime-readiness preconditions M18+ tenant runtime will require (operator-asserted via cert.gate_results_json or candidate_proposal annotations); per current scope M13 emits PASS by default with `evidence_json.verdict_signals.mode='default-pass-pending-m18+'` since tenant runtime is M18+. **Real binding deferred to M18+ runtime gate.** Operator should treat any MCV that reaches `approved` today as having an unverified PE-MC-8. | (operator-supplied explicit reject signal in cert via `mode='operator-reject'` with reason) | (default mode = `default-pass-pending-m18+`) — flagged for operator confirmation; does NOT block aggregation today; tracked in R-M13-5 |
| **PE-MC-9** | Definition discipline / duplicate-intent detection | No other non-archived `mcf.metric_contract` row has the same `identity_tuple_hash` (after M13 computes the candidate identity_tuple_hash) | Another non-archived MC has the same `identity_tuple_hash` | (none) |
| **PE-MC-10** | Self-verification fixture pass | Latest `mcf.metric_self_verification_result` for this MCV's fixture(s): `verdict_code == 'pass'` AND `stale_fixture_flag == false` AND `bound_package_signature_hash_at_run` matches M13-computed current `package_signature_hash` | verdict != 'pass' OR stale_fixture_flag=true OR hash mismatch (MCF §12.7 stale-fixture rule) | (none) |

### 4.3 OPERATOR_REVIEW handling

- M13 emits OPERATOR_REVIEW for a check only when the check has structural ambiguity that can't be auto-resolved (e.g. PE-MC-2 BCF entity-graph read failure; PE-MC-6 operator-supplied param overrides). The aggregation rule (§4.5) routes OPERATOR_REVIEW to "no transition" — same effect as REJECT for state-progression purposes — but the evidence_json carries the ambiguity signal so the operator can supply additional inputs and re-run.
- Default-mode OPERATOR_REVIEW (PE-MC-8 pending M18+ binding) does NOT block aggregation per §4.5 (treated as PASS for aggregation; flagged in evidence_json for operator awareness). This default is reviewable in D-M13-10b (open).

### 4.4 evidence_json schema (per check)

Each PE row's `evidence_json` follows this top-level schema:

```jsonc
{
  "check_code": "PE-MC-<n>",
  "evaluator_version": "mcf-m13-v2",
  "evaluator_inputs_hash": "sha256:<...>",       // JCS-canonical hash of the inputs the check read
  "current_package_signature_hash": "sha256:<...>", // M13-computed; for stale detection on retry
  "verdict_signals": {                            // check-specific structured signals
    // PE-MC-1: { claims_total, claims_grounded, claims_quarantined, grounding_violations }
    // PE-MC-2: { unreachable_bindings: [...], grain_entity_id }
    // PE-MC-3: { missing_roles: [...], ast_referenced_roles: [...] }
    // PE-MC-4: { type_mismatches: [...], ast_derived_expectations: {...} }
    // PE-MC-5: { ast_validation_error?: string, structural_defects: [...] }
    // PE-MC-6: { shape, params_schema_violations: [...] }
    // PE-MC-7: { unreachable_dim_refs: [...], unreferenced_roles: [...] }
    // PE-MC-8: { mode: 'default-pass-pending-m18+' | 'operator-reject', operator_reject_reason?: string }
    // PE-MC-9: { colliding_mc_uids: [...] }
    // PE-MC-10: { fixture_uid, verifier_result_uid, verdict_code, stale_fixture_flag, bound_hash, current_hash }
  },
  "ran_at": "2026-05-28T...",
  "superseded_by_stale_package_change"?: [/* prior pe_result_uid[] if stale-retry */]
}
```

Substrate constraint: `evidence_json` is jsonb NOT NULL with default `'{}'::jsonb`. M13 always emits an object (no JSONB STRING corruption — per M11 PR #121 / M12.5 RCA; uses Drizzle `tx.insert(...).values({...})` which Drizzle auto-serializes; OR uses raw SQL with `${JSON.stringify(obj)}::jsonb` for any sql.template path per M12.5 B2 patch).

**Per-check `evaluator_inputs_hash` JCS-canonical input shapes.** Each check hashes (`hashJcs(...)`) over its specific input set. The hashed input is the deterministic, ordered tuple of substrate fields the check actually read (mirrors M7's `computeVariableBindingSetHash` pattern of "what was looked at, in canonical order"):

| Check | JCS input tuple |
|---|---|
| **PE-MC-1** | `[panel_run_uid, grounding.claims_total, grounding.claims_grounded, grounding.claims_quarantined, sorted(grounding_violations), mapr.grounding_check_passed]` |
| **PE-MC-2** | `[grain_entity_id, sorted(input_binding_role + bc_uid + entity_uid + reachable_flag) per binding]` |
| **PE-MC-3** | `[sorted(ast_referenced_roles), sorted(mcv_binding_roles)]` |
| **PE-MC-4** | `[sorted(role + representation_term + unit_code + data_type + ast_derived_type) per binding]` |
| **PE-MC-5** | `[formula_intent_hash, sorted(structural_defect_codes if any)]` |
| **PE-MC-6** | `[temporal_gate_shape_code, jcs(temporal_gate_params_json)]` |
| **PE-MC-7** | `[sorted(dim_class_code + source_bc_uid + role_in_formula + reachable_flag) per computed_dim_ref]` |
| **PE-MC-8** | `[mode]` (deferred-pass; minimal hash until M18+) |
| **PE-MC-9** | `[candidate_identity_tuple_hash, sorted(colliding_mc_uids)]` |
| **PE-MC-10** | `[fixture_uid, verifier_result_uid, verdict_code, bound_package_signature_hash_at_run, current_package_signature_hash]` |

The `current_package_signature_hash` field is identical across all 10 rows of a single evaluation (M13 computes it once per `evaluate()` call). It serves as the retry-detection key in §6.2.

### 4.5 Aggregation rule (verdict → state transition)

```
Let V[i] = verdict of PE-MC-i for i in {1..10}.

Define:
  PASS_REQUIRED  = {1, 2, 3, 4, 5, 6, 7, 9, 10}     // 9 checks
  PASS_OR_DEFAULT_OR = {8}                           // PE-MC-8 default pass; explicit-reject only

approve_eligible(V) := 
  all i in PASS_REQUIRED:    V[i] == PASS
  AND V[8] in {PASS, OPERATOR_REVIEW with mode='default-pass-pending-m18+'}

If approve_eligible(V):
  M13 calls McfCertWriterService.approveForActivation(...)
  → MCV transitions to 'approved' AND parent MC hashes stamped IN SAME TX
Else:
  No state transition. MCV remains at 'review'.
  Operator inspects evidence_json. Remediation path:
    - For REJECT: supersession (M15)
    - For OPERATOR_REVIEW: operator-supplied additional input + M13 re-run (idempotent retry per §6)
```

## 5. Architecture — service shape

```
src/registry/mcf/metric-publication-eligibility-evaluator.service.ts        — new (~600 LOC)
src/registry/mcf/metric-publication-eligibility-evaluator.service.spec.ts   — new (~700 LOC; 25-30 unit tests)
src/registry/mcf/metric-publication-eligibility-evaluator.service.integration.spec.ts — new (~500 LOC; live integration under SAVEPOINT rollback)
```

### 5.1 Public API

```typescript
class MetricPublicationEligibilityEvaluatorService {
  constructor(
    private readonly db: PostgresJsDatabase<any>,
    private readonly certWriter: McfCertWriterService,        // existing M4
    private readonly formulaCanon: FormulaCanonicalizationService, // existing M7
    private readonly packageSig: PackageSignatureService,      // existing M8
    private readonly structuralCheck: FixtureStructuralCheckService, // existing M9
    private readonly verifier: MetricSelfVerificationService,  // existing M10 (read-only role here)
    private readonly evaluatorVersion: string = 'mcf-m13-v2',
  ) {}

  async evaluate(
    mcvUid: string,
    opts: RunEvaluationOpts,
  ): Promise<EvaluationResult>;
}

interface RunEvaluationOpts {
  actorSub: string;
  actorRoleAtAction: 'panel' | 'operator' | 'system';
  // Per §0bis: M13 emits NO cert. Fields below match M4's existing
  // SubmitForReviewInput + ApproveForActivationInput exactly (see
  // mcf-cert-writer.service.ts:223-228, 236-242). No `certifierSub` /
  // `certifierEmail` because M13 produces no certification record;
  // PE-MC rows are the audit ledger.
  dryRun?: boolean;
}

interface EvaluationResult {
  mcv_uid: string;
  pe_result_uids: string[];                          // 10 UIDs, one per check
  verdicts: Record<'PE-MC-1' | … | 'PE-MC-10', 'PASS' | 'REJECT' | 'OPERATOR_REVIEW'>;
  approved: boolean;                                  // true iff approveForActivation invoked
  parent_mc_hashes?: ParentHashes;                    // populated iff approved=true
  new_governance_state_code: 'review' | 'approved';
  evaluation_signature_hash: string;                  // JCS hash of (mcv_uid, evaluator_version, verdicts, evidence digests)
  retry_mode: boolean;                                // true iff findExistingEvaluation short-circuited
}
```

### 5.2 Transactions

```
TX outer (M13-owned; opens at evaluate() entry):
  Step 1: SELECT … FOR UPDATE on mcf.metric_contract_version + mcf.metric_contract for mcvUid
          (mirrors M4's lockParentMcAndChildRows pattern)
  Step 2: Read full MCV substrate context (bindings/filters/computed_dims/fixtures/verifier_results/cert/mapr)
  Step 3: findExistingEvaluation(mcvUid, evaluatorVersion, packageSignatureHash) — if 10 PE rows exist
          for this triple AND current package hash matches stored, return idempotent retry result
  Step 4: Run PE-MC-1..PE-MC-10 (10 in-tx checks; no DB writes during check execution)
  Step 5: Compose 10 PeEligibilityResultInput rows
  Step 6: If aggregation says approve_eligible:
            Step 6a: certWriter.submitForReview(...) — transitions draft → review
            Step 6b: certWriter.approveForActivation({ peEligibilityResults: <10 rows>, ... }) — 
                     stamps parent MC hashes + INSERTs PE rows + transitions review → approved
                     ALL IN A NESTED TX (Drizzle SAVEPOINT inside M13's outer tx)
          Else (NOT approve_eligible):
            Step 6a: certWriter.submitForReview(...) — transitions draft → review (only if state==draft)
            Step 6b: M13 INSERTs the 10 PE rows directly via
                       tx.insert(metricPublicationEligibilityResult).values([...])
                     (no M4 `recordEligibility` helper exists — `insertPeResultRows` is
                     M4-internal; M13 writes its own evidence ledger). All 10 rows carry
                     `certification_record_id = NULL`. MCV stays at `review` (does NOT
                     advance to `approved`). Parent MC hashes remain NULL. No cert emitted.
  Step 7: Compose EvaluationResult and return
```

The TX A approach (single outer tx wrapping M4's nested tx) follows M12.5's nested-tx pattern: M4's `db.transaction(...)` opens a SAVEPOINT inside M13's outer tx (Drizzle nested-tx semantics).

### 5.3 No M10 verifier re-run inside M13 (D-M13-6: latest-only)

PE-MC-10 reads the existing `mcf.metric_self_verification_result` rows; it does NOT re-execute M10 verifier inside M13. This decouples M13 from M10 re-run cost. If the operator wants a re-run before approval, the operator invokes M10 verifier separately (or via a separate "M13 + M10 re-run" composition gate).

## 6. Idempotency model — full specification

### 6.1 First-call path

`findExistingEvaluation(mcvUid, evaluatorVersion, packageSignatureHash)` returns null. M13 runs the 10 checks, INSERTs 10 PE rows, optionally calls `approveForActivation`. Result includes `retry_mode: false`.

### 6.2 Retry path — same substrate

Second call with same `mcvUid`. M13 computes current `package_signature_hash` from MCV substrate via M7/M8 (read-only). `findExistingEvaluation` queries:

```sql
SELECT pe_result_uid, pe_check_code, verdict_code, evidence_json
FROM mcf.metric_publication_eligibility_result
WHERE metric_contract_version_uid = $mcvUid
  AND verifier_version = $evaluatorVersion
  AND evidence_json->>'current_package_signature_hash' = $currentHash
ORDER BY evaluated_at DESC
```

If 10 rows match (one per PE-MC-<n>), return the cached UIDs + verdicts + `retry_mode: true`. No writes. MCV state unchanged.

### 6.3 Retry path — stale substrate (package hash changed)

Substrate has changed since prior evaluation (e.g. external supersession scenario — should not happen during normal flow, but design is robust). `findExistingEvaluation` finds prior PE rows but `current_package_signature_hash` doesn't match. M13 emits NEW PE rows with the new hash. Prior rows preserved (Invariant V). The new rows' `evidence_json.superseded_by_stale_package_change` references the prior `pe_result_uid[]`.

**Substrate-side enforcement.** The partial expression unique index `idx_mcf_mper_mcv_check_eval_pkg` keys on `(mcv_uid, pe_check_code, verifier_version, COALESCE(evidence_json->>'current_package_signature_hash', ''))` (per §10.1 PR-1 / D-M13-8). This permits stale-package retry exactly: the new rows have a different `evidence_json->>'current_package_signature_hash'` value, so the unique 4-tuple doesn't collide with the prior rows — both sets coexist. A naive 3-tuple unique on `(mcv, check, evaluator)` would have BLOCKED this behavior; the expression-index design is the substrate-level half of the stale-package retry contract.

### 6.4 Partial-state retry

Prior evaluation crashed mid-INSERT (e.g. server died between PE-MC-3 row INSERT and PE-MC-4). `findExistingEvaluation` finds < 10 matching rows → returns null → first-call path runs. Optional substrate UNIQUE (D-M13-8 / §10.1 PR-1) catches per-row duplicates on the retry, SELECTing existing.

## 7. HA-1..HA-8 hard assertions (M13 acceptance criteria)

| HA | Statement | Spec test |
|---|---|---|
| HA-1 | M13 source has zero call sites to `activateMetric` / `supersedeMetric` / publishing methods | Unit: grep test in suite; integration: assert MCV cannot reach `active` via M13 |
| HA-2 | M13 service has zero imports of tenant-runtime modules | Unit: import-list assertion |
| HA-3 | M13 service has zero imports of `MetricDefinitionService` / `MetricDefinitionRepository` | Unit: import-list assertion; integration: legacy `metric.*` row counts preserved |
| HA-4 | M13 service writes no rows to `contract.*` tables | Integration: `contract.panel_output_record` + `contract.authoring_panel_rejection_log` row counts exact-preserved across rolled-back tx |
| HA-5 | Exact write surface: parent MC 6-hash UPDATE + ≤ 10 PE rows (each with `certification_record_id=NULL`) + 2 MCV state UPDATEs (`draft→review`, `review→approved` if eligible) + **0 certs** (substrate `mcf_cert_state_transition_chk` forbids certs for these transitions per §0bis) | Integration: 0-delta on forbidden tables (`mcf.certification_record`, `mcf.metric_supersession`, `mcf.metric_self_verification_fixture`, `mcf.metric_self_verification_result`, `mcf.metric_authoring_*`) inside rolled-back tx |
| HA-6 | Parent hash stamping happens BEFORE the `review → approved` UPDATE in the same tx | Integration: substrate trigger rejects synthetic "approve without hashes" attempt (negative test) — proves substrate-side enforcement |
| HA-7 | Idempotent retry returns same `pe_result_uid[]` + `retry_mode=true` + no new writes | Integration: second `evaluate(mcvUid, ...)` call asserts identical UID array + same MCV state + 0 row delta |
| HA-8 | Failed PE-MC (any REJECT verdict) preserves audit trail; MCV transitions `draft → review` but does NOT advance to `approved`; no substrate reversion | Integration: synthetic REJECT scenario asserts 10 PE rows persisted with mixed verdicts + MCV final state is `review` (was `draft` pre-call) + parent MC hashes NULL + zero certs emitted |

## 8. Risk register (R-M13-N)

| Risk | Severity | Mitigation |
|---|---|---|
| **R-M13-1** | M13 misinterprets the entity-graph reachability rule for PE-MC-2 / PE-MC-7 | MEDIUM | DBCP §4.2 locks the reachability algorithm via BCF `concept_registry` entity-graph read; integration spec includes synthetic non-reachable binding to assert REJECT |
| **R-M13-2** | M13 picks a stale `mcf.metric_self_verification_result` row for PE-MC-10 | HIGH | D-M13-6: latest-only ordering + stale_fixture_flag + hash-match triple-check; DBCP §4.2 spells this out; integration spec includes a stale-fixture scenario |
| **R-M13-3** | M13's `identity_tuple_hash` for PE-MC-9 collides with a legacy `metric.metric_definition` row that has the same business intent | LOW | M13 reads only `mcf.metric_contract`, not legacy `metric.*`. Per audit, MCF / legacy is dual-authority during the transition window. Legacy collisions are M17+ concerns |
| **R-M13-4** | M13's nested-tx (Drizzle SAVEPOINT) interaction with M4's idempotency table causes phantom rows under rollback | MEDIUM | M4 already uses the same nested-tx pattern via `db.transaction(...)`; M12.5 PR-2 integration spec proved this works. M13 inherits the proven pattern + adds its own integration tests |
| **R-M13-5** | M13 default-PASS on PE-MC-8 (runtime-readiness intent) silently masks an M18+ binding requirement | LOW | DBCP §4.3 marks PE-MC-8 default-mode as "flagged for operator confirmation pending M18+ binding"; operator reviews the `evidence_json.verdict_signals.mode='default-pass-pending-m18+'` flag |
| **R-M13-6** | M13's `evaluator_version` reuse of column `verifier_version` confuses M14+ audit consumers | LOW | DBCP §3 D-M13-9 locks `verifier_version` column semantic carries forward; new DDL deferred. M14 design awareness |
| **R-M13-7** | M13's idempotency key collides with M12.5's idempotency keys in `mcf.metric_cert_writer_idempotency` | LOW | M12.5 prefix `mcf-m12-5/`; M13 prefix `mcf-m13-pe-mc/`. Distinct namespaces. |
| **R-M13-8** | PE-MC-2 / PE-MC-7 BCF entity-graph reachability — no existing BCF reader service identified as M13 dependency | MEDIUM | M13 PR-2 design must either (a) identify an existing BCF concept_registry reader and inject it as a service constructor dep, or (b) implement direct SQL graph traversal on `contract.concept_registry.*` within M13 (couples M13 to BCF substrate schema). DBCP §5.1 will be updated in PR-2 design to lock the choice. Until then, PE-MC-2 + PE-MC-7 implementations are pending BCF-reader resolution. |

## 9. Operator authorizations required BEFORE PR-1 opens

| # | Authorization | Why |
|---|---|---|
| 1 | D-M13-1..D-M13-10 decisions accepted | DBCP locks |
| 2 | PR-1 DDL (partial unique index per §10.1) reviewed + DDL dry-run authorization | Substrate change |
| 3 | M12.5 first operational run NOT required as M13 PR-1 prerequisite (but if first operational run lands before M13 PR-2, M13 PR-2 integration spec should be re-run against that real data) | Scope clarification |

## 10. Proposed files

### 10.1 PR-1 — substrate gate (partial unique index)

| File | Type | Rationale |
|---|---|---|
| `bc-core/docker/redesign/13-mcf-m13-pe-mc-uniqueness-index.sql` | NEW DDL | **Partial expression unique index** (4-tuple including package hash from `evidence_json`): `CREATE UNIQUE INDEX idx_mcf_mper_mcv_check_eval_pkg ON mcf.metric_publication_eligibility_result(metric_contract_version_uid, pe_check_code, verifier_version, COALESCE(evidence_json->>'current_package_signature_hash', '')) WHERE verifier_version IS NOT NULL`. The 4-tuple — MCV + check + evaluator_version + package_hash-from-jsonb — distinguishes true duplicates (same all four → reject) from stale-package retry (same MCV/check/evaluator but new package_hash → permitted per §6.3). The `COALESCE(..., '')` deflates NULL `current_package_signature_hash` values to a deterministic empty string so PostgreSQL's NULL-distinct semantics don't silently bypass the uniqueness when M13 implementation drops the key. The partial `WHERE verifier_version IS NOT NULL` continues to cover all M13-written PE rows (M13 stamps the current `M13_EVALUATOR_VERSION` — `'mcf-m13-v2'` as of PR #207; previously `'mcf-m13-v1'`) and excludes any legacy NULL-verifier_version rows from M4 spec tests (pre-M13). The index keys on `verifier_version` as a column, so v1 + v2 rows coexist freely for the same `(mcv_uid, pe_check_code)`; old v1 rows remain as immutable historical evaluation evidence under Invariant V (D-M13-9). Sub-30-second apply on an empty table. Reversible via single `DROP INDEX`. |
| `bc-core/docker/redesign/13R-mcf-m13-pe-mc-uniqueness-index-rollback.sql` | NEW DDL | Rollback (`DROP INDEX IF EXISTS …`). |
| `bc-core/scripts/mcf-m13-dry-run.mjs` | NEW | Per M11 / M9 / M5 / M4 / M3 / M12.5 PR-1 dry-run pattern. |
| `bc-core/scripts/mcf-m13-post-apply.mjs` | NEW | Per same pattern; crash-safe BEGIN/ROLLBACK probes. |
| `bc-core/scripts/audit-output/mcf-m13-dry-run-<ts>.{precondition.jsonl, planned-sql.sha256.txt, summary.md}` | NEW evidence | Committed in PR-1 alongside scripts. |
| `bc-core/scripts/audit-output/mcf-m13-post-apply-<ts>.{evidence.jsonl, summary.md}` | NEW evidence | Committed in PR-1 after apply. |

### 10.2 PR-2 — service implementation

| # | Deliverable | Location |
|---|---|---|
| 1 | M13 evaluator service | NEW `bc-core/src/registry/mcf/metric-publication-eligibility-evaluator.service.ts` (~600 LOC) |
| 2 | Unit spec (25-30 tests; one per PE-MC check + idempotency + HA assertions) | NEW `bc-core/src/registry/mcf/metric-publication-eligibility-evaluator.service.spec.ts` (~700 LOC) |
| 3 | Integration spec (live against `bc_platform_dev` under SAVEPOINT rollback; uses real M7/M8/M9/M10 services + M4 cert writer; synthesizes M12.5 outputs in-tx via `McfCertWriterService.createMetricDraft` + direct fixture/verifier_result INSERTs) | NEW `bc-core/src/registry/mcf/metric-publication-eligibility-evaluator.service.integration.spec.ts` (~500 LOC) |
| 4 | Optional: preflight CLI (read-only; verifies an MCV has all prerequisites for PE-MC evaluation: cert exists, fixture exists, verifier_result exists, no stale-package, etc.) | NEW `bc-core/scripts/mcf-m13-preflight.mjs` (~150 LOC) — mirrors M12.5 preflight CLI pattern |

PR-2 does NOT add NestJS module registration (per §2.8). Operational invocation uses the integration spec wiring pattern.

## 11. Test plan

### 11.1 Unit spec (25-30 tests)

| Group | Tests | Acceptance |
|---|---|---|
| Per-PE-MC-check predicate (10 tests) | one positive + one negative each (20 tests minimum) | Each predicate correctly emits PASS / REJECT / OPERATOR_REVIEW given synthetic inputs |
| Aggregation rule | mixed-verdict cases (5 tests) | `approve_eligible` returns correct boolean |
| Idempotency | first-call / retry / partial-state / stale-package (4 tests) | Returns expected `pe_result_uid[]` + `retry_mode` |
| HA-1..HA-8 assertions | (8 tests) | Each HA tested by direct service-source inspection or mocked-substrate scenario |

### 11.2 Integration spec (live against `bc_platform_dev` under SAVEPOINT rollback)

Mirrors M12.5 integration spec wiring:
- Real `FormulaCanonicalizationService`, `PackageSignatureService`, `MetricSelfVerificationService`, `FixtureStructuralCheckService`, `McfCertWriterService`
- Synthesizes M12.5 outputs in-tx: `seedMcvWithRealAst` (via `createMetricDraft`), `seedFixture` (raw INSERT into `mcf.metric_self_verification_fixture` with real M7/M8-computed hashes), `seedVerifierResult` (raw INSERT into `mcf.metric_self_verification_result`)
- Test cases:
  1. Happy path: 10 PE-MC checks all PASS → approveForActivation → MCV transitions `review → approved` → parent MC's 6 hash cols stamped → 10 PE rows persisted
  2. REJECT path (any check fails): MCV stays at `review`; PE rows persisted; parent hashes NULL
  3. OPERATOR_REVIEW path (PE-MC-6 op-supplied params): MCV stays at `review`
  4. Idempotent retry: same call returns same UIDs + `retry_mode=true`
  5. Stale-package retry: substrate hash changed → new PE rows emitted referencing prior; old rows preserved
  6. Negative: synthetic "skip review" attempt asserts substrate trigger rejects (HA-6 substrate-side enforcement)
  7. Negative: synthetic "approve without parent hash stamping" asserts substrate trigger rejects
- All assertions inside an outer Drizzle tx; throw `SentinelRollbackError` to roll back; post-rollback live DB confirmed identical to baseline

### 11.3 Substrate trigger negative tests (HA-6 enforcement)

Inside the rolled-back outer tx, attempt:
1. `UPDATE mcf.metric_contract_version SET governance_state_code='approved' WHERE …` with parent MC hashes NULL → expect CHECK violation `mcf state transition to approved requires all 6 hash columns NOT NULL on parent mcf.metric_contract`
2. `UPDATE mcf.metric_contract_version SET governance_state_code='active' WHERE …` from draft directly → expect CHECK violation `invalid mcf state transition`
3. `DELETE FROM mcf.metric_publication_eligibility_result WHERE …` → expect trigger or RESTRICT FK rejection (depending on substrate; verify behavior)

### 11.4 Verification gates (CI)

- ESLint `--max-warnings 0` on M13 touched files
- `tsc --noEmit` filtered to M13 files → 0 errors
- `vitest run src/registry/mcf/` (no env) → all M13 unit tests pass
- `vitest run` integration spec with `BCCORE_INTEGRATION_DB=1` → 1 PASSED end-to-end

## 12. Evidence plan

### 12.1 PR-1 artifacts (substrate apply)

- `bc-core/scripts/audit-output/mcf-m13-dry-run-<ts>.summary.md` — DDL dry-run summary
- `bc-core/scripts/audit-output/mcf-m13-dry-run-<ts>.planned-sql.sha256.txt` — planned SQL hash
- `bc-core/scripts/audit-output/mcf-m13-dry-run-<ts>.precondition.jsonl` — precondition probes
- `bc-core/scripts/audit-output/mcf-m13-post-apply-<ts>.evidence.jsonl` — post-apply probes
- `bc-core/scripts/audit-output/mcf-m13-post-apply-<ts>.summary.md` — post-apply summary

### 12.2 PR-2 artifacts (service ship + closeout readiness)

- `bc-core/scripts/audit-output/mcf-m13-pr2-verification-<ts>.summary.md` — full verification (ESLint / tsc / vitest no-env / live integration)
- `bc-docs-v3/docs/implementation/mcf-m13-implementation-closeout.md` — closeout doc (when PR-2 lands)

### 12.3 First operational evaluation (separate operator authorization)

After PR-1 + PR-2 ship, an operator-authorized first operational M13 evaluation against a real M12.5-materialized MCV produces:

- `bc-core/scripts/audit-output/mcf-m13-first-evaluation-<ts>.summary.md`
- `bc-core/scripts/audit-output/mcf-m13-first-evaluation-<ts>.evidence.jsonl` — per-PE-row verdicts + evidence_json

This step requires the first operational M12.5 materialization to have occurred (currently blocked per M12.5 closeout doc §8 — operator chooses one of (a) synthetic / (b) real M12 panel / (c) cached transcript replay).

## 13. M14+ handoff readiness

After M13 closeout:

| Consumable for M14 | Source | Notes |
|---|---|---|
| Approved MCV (state='approved') | `mcf.metric_contract_version.governance_state_code='approved'` | M14 transitions `approved → active` |
| Parent MC hash columns (6 NOT NULL) | `mcf.metric_contract` | M14 reads as identity authority |
| PE rows (10 PASS verdicts) | `mcf.metric_publication_eligibility_result` | M14 cites via `cert.gate_results_json` |
| Approve cert | `mcf.certification_record.action_code='metric_transition'`, `from='review'`, `to='approved'` | M14 reads for evidence chain |

M14 then writes a NEW cert with `action_code='metric_transition'`, `from='approved'`, `to='active'`, which (per the substrate trigger) enables the `approved → active` transition. M14 also emits PE-MC-10 result rows at activation time per existing M4 `activateMetric` API.

## 14. Cross-cutting discipline (this DBCP gate)

| Constraint | Status this gate |
|---|---|
| `bc-postgres` MCP `allow_write` | unchanged (false) — read-only verification only |
| BCF writes | none |
| DDL applied | none (PR-1 ships under separate authorization) |
| Seed scripts run | none |
| Real model API calls | none |
| bc-admin touched | no |
| Tenant runtime touched | no |
| Persistent DB writes | none |
| M13 implementation | NOT started |
| M14+ work | NOT started |
| M12.5 NestJS DI patch | NOT in scope (per §2.8) |
| Additional commits beyond this DBCP doc | none |

## 15. See also

- ADR `bc-docs-v3/docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) — MCF Build Plan
- ADR `bc-docs-v3/docs/adrs/ADR-f8f925.md` — PE-MC-1..PE-MC-10 canonical definition
- M12.5 DBCP `bc-docs-v3/docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md`
- M12.5 closeout `bc-docs-v3/docs/implementation/mcf-m12-5-implementation-closeout.md`
- M4 cert writer source `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` (`approveForActivationInTx` lines 1064-1126; `lockParentMcAndChildRows` pattern)
- M7/M8 hash services `bc-core/src/registry/mcf/formula-canonicalization.service.ts` + `package-signature.service.ts`
- M9 fixture check `bc-core/src/registry/mcf/fixture-structural-check.service.ts`
- M10 verifier `bc-core/src/registry/mcf/metric-self-verification.service.ts`
- M12.5 materialization service `bc-core/src/registry/mcf/metric-authoring-materialization.service.ts` — reference for nested-tx + idempotency pattern
- Substrate trigger function `mcf.fn_mcv_state_transition_check` — substrate-enforced state machine M13 must respect
- Substrate trigger function `mcf.fn_mcv_descriptive_immutability_check` — substrate-enforced immutability invariant
