---
uid: mcf-m13-implementation-closeout
title: MCF M13 — Implementation Closeout
description: Closeout record for MCF gate M13 (PE-MC Evaluator) per ADR DEC-c3e57f / D422 + DBCP `e7a2507`. Locks the post-merge state of the four M13 PRs on bc-core (PR #128 PR-1 substrate gate → main `36f61b8`; PR #129 PR-2 evaluator service → main `318e03c`; PR #130 same-tx wiring → main `854c317`; PR #131 hygiene cleanup → main `c027ff1`) and the verification evidence that supports M13's code-live + substrate-proof status. Status is **code-live + substrate-proof complete + first operational evaluation pending**: the evaluator service is shipped and proven via the live integration spec (real M7/M8/M9/M10 chain against `bc_platform_dev` under SAVEPOINT rollback, all 10 PE-MC checks exercised across happy + retry + REJECT + stale-package retry scenarios, all HA-1..HA-8 enforced, evidence-ledger discipline proven, post-rollback substrate identical to baseline), but no real operational first evaluation has been executed because no eligible draft MCV exists in `bc_platform_dev` (M13 is the read-side consumer of M12.5 materialization output, and the first operational M12.5 materialization itself remains blocked on the missing `consensus_payload_json.verdict_code = 'APPROVE_FOR_DRAFT'` panel row). M14 publication remains CLOSED gated on M13 first operational evaluation. No DDL applied during closeout. No BCF writes. No bc-admin, controller, DI module, or tenant-runtime changes. `bc-postgres` MCP `allow_write=false` throughout.
status: draft
date: 2026-05-28
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m13-implementation-closeout
---

# MCF M13 — Implementation Closeout

## 1. Authority

- ADR: `bc-docs-v3/docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) — MCF Build Plan
- ADR: `bc-docs-v3/docs/adrs/ADR-f8f925.md` line 145 — PE-MC-1..PE-MC-10 canonical definition per MCF requirements §13
- DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m13-pe-mc-evaluator-dbcp.md` (`e7a2507`)
- Upstream gate (M12.5): `bc-docs-v3/docs/implementation/mcf-m12-5-implementation-closeout.md`
- Substrate gate (M3): `bc-docs-v3/docs/implementation/mcf-m3-cert-amendment-apply-closeout.md`
- M4 cert writer DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m4-lifecycle-certification-dbcp.md` (`3983530`)
- M7/M8 hash authority DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m7-m8-formula-hash-authority-dbcp.md` (`62ec707`)
- M9 fixture DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m9-fixture-substrate-dbcp.md` (`620e11d`)
- M10 verifier DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m10-self-verification-result-dbcp.md` (`ea8b708`)

## 2. Status

**M13 status: code-live + substrate-proof complete + first operational evaluation pending (blocked on M12.5 first materialization).**

- **Code-live:** All four M13 PRs merged to `bc-core` main. The substrate index `idx_mcf_mper_mcv_check_eval_pkg` is applied to `bc_platform_dev`. The evaluator service `MetricPublicationEligibilityEvaluatorService` exposes `evaluate(mcvUid, opts)`, `findExistingEvaluation()`, and a private `composeIdempotencyKey()` reserved for future M4 API expansion.

- **Substrate-proof complete:** PR-1 post-apply behavioral probes recorded **16/16 PASS** (artifact `bc-core/scripts/audit-output/mcf-m13-post-apply-2026-05-28T11-37-38-025Z.summary.md`). The partial expression UNIQUE index correctly permits stale-package retry (different `current_package_signature_hash` → new row permitted) AND rejects true duplicates (same 4-tuple → UNIQUE violation). The PR-2 live integration spec exercises the production service end-to-end against `bc_platform_dev` under SAVEPOINT rollback with real M7/M8/M9/M10 services and passes all 10 PE-MC checks across 4 scenarios (happy + idempotent retry + REJECT + stale-package retry with `superseded_by_stale_package_change` audit chain).

- **First operational evaluation pending:** No real operational evaluation has executed against `bc_platform_dev`. M13 evaluates a MCV that M12.5 has materialized; with `mcf.metric_contract_version` rowcount = 0 there is nothing to evaluate. Per the M12.5 closeout, M12.5's first operational materialization itself remains blocked on the missing `consensus_payload_json.verdict_code = 'APPROVE_FOR_DRAFT'` panel row.

- **M14 status:** CLOSED, gated on M13's first operational evaluation.

## 3. Repo SHAs (post-merge, locked)

| Repo | main SHA | M13 commit stack |
|---|---|---|
| `bc-core` | `c027ff1fc8851d4cef491080f2b47aa11fda69d9` | PR #128 (`36f61b8`) → PR #129 (`318e03c`) → PR #130 (`854c317`) → PR #131 (`c027ff1`) |
| `bc-docs-v3` | `e7a2507eee61d1f0c834d4299a887477ad1ddc21` | (DBCP authored pre-PR-1 baseline; this closeout doc opens against `e7a2507`) |
| `barecount-devhub` | `2ea9efc53cc9a3b83c9b4bf8e5a3936c54398566` | (M13 stack required no devhub CLAUDE.md changes — substrate + service path is in-repo) |

Per-PR HEAD SHAs (merged via `gh pr merge --squash --match-head-commit --delete-branch`):

| PR | HEAD SHA | Squash commit | What landed |
|---|---|---|---|
| #128 | `e3d99f6` (or equivalent) | `36f61b8` | PR-1 substrate gate — `idx_mcf_mper_mcv_check_eval_pkg` partial expression UNIQUE index applied to `bc_platform_dev`, 16/16 post-apply probes PASS |
| #129 | `29c3b22` | `318e03c` | PR-2 evaluator service — `MetricPublicationEligibilityEvaluatorService` with 10 PE-MC checks + same-tx integration spec |
| #130 | `10babec` | `854c317` | Same-tx wiring — M4 `submitForReviewInTx` / `approveForActivationInTx` promoted to public; M13 calls them with own tx |
| #131 | `586a8f0` | `c027ff1` | Hygiene cleanup — M4 wrapper validation single-sourced, M13 `dryRun` fail-fast, test queue + doc polish |

## 4. DB before/after row deltas

This closeout gate is read-only. **No row deltas occurred** because:
- No operational M13 evaluation ran.
- No operational M12.5 materialization ran.
- All verification gates execute under SAVEPOINT rollback (integration specs) or in-memory mocks (unit specs).

### 4.1 Closeout-time live state (== pre-test baseline)

| Object | Pre-gate | Post-gate | Delta |
|---|---|---|---|
| `mcf.metric_contract` | 0 | 0 | 0 |
| `mcf.metric_contract_version` | 0 | 0 | 0 |
| `mcf.metric_variable_binding` | 0 | 0 | 0 |
| `mcf.metric_filter_clause` | 0 | 0 | 0 |
| `mcf.metric_computed_dimension_ref` | 0 | 0 | 0 |
| `mcf.metric_contract_revision` | 0 | 0 | 0 |
| `mcf.metric_supersession` | 0 | 0 | 0 |
| `mcf.certification_record` | 0 | 0 | 0 |
| `mcf.metric_publication_eligibility_result` | 0 | 0 | 0 |
| `mcf.metric_cert_writer_idempotency` | 0 | 0 | 0 |
| `mcf.metric_authoring_panel_run` | 0 | 0 | 0 |
| `mcf.metric_authoring_panel_transcript` | 0 | 0 | 0 |
| `mcf.workspace_tool_allowlist` | 0 | 0 | 0 |
| `mcf.evidence_source_allowlist` | 0 | 0 | 0 |
| `mcf.metric_self_verification_fixture` | 0 | 0 | 0 |
| `mcf.metric_self_verification_result` | 0 | 0 | 0 |
| `mcf.metric_authoring_intake_queue` | 0 | 0 | 0 |
| `contract.panel_output_record` | 24 | 24 | 0 |
| `contract.authoring_panel_rejection_log` | 1 | 1 | 0 |
| `idx_mcf_mc_mc_name_active` exists | yes (M12.5 PR-1) | yes | unchanged |
| `idx_mcf_mper_mcv_check_eval_pkg` exists | yes (M13 PR-1) | yes | unchanged |
| `contract.framework_policy` mcf_v1 active | 1 | 1 | unchanged |

## 5. PE-MC check inventory (per DBCP §4.2)

| Check | Predicate | Verdict semantics |
|---|---|---|
| **PE-MC-1** | Provenance grounding (BCF `panel_output_record.grounding_check_result='pass'` AND MAPR `consensus_payload_json.grounding_check_passed=true`) | PASS / REJECT |
| **PE-MC-2** | Grain coherence — every input/output binding's BC is reachable to `mc.grain_entity_id` via `concept_registry.business_concept.entity_id` | PASS / REJECT |
| **PE-MC-3** | Binding completeness — every formula variable role has a corresponding `mcf.metric_variable_binding` row | PASS / REJECT |
| **PE-MC-4** | Type + unit coherence — `representation_term_snapshot`, `unit_code_snapshot`, `data_type_snapshot` align with body declaration | PASS / REJECT |
| **PE-MC-5** | Self-verification fixture presence — `mcf.metric_self_verification_fixture` row exists for MCV with required body sections | PASS / REJECT |
| **PE-MC-6** | Temporal-gate shape well-formedness — `mc.temporal_gate_shape_code` ∈ 6 known shapes; `temporal_gate_params_json` parses against shape schema | PASS / REJECT / OPERATOR_REVIEW |
| **PE-MC-7** | Computed-dimension coherence — every `metric_computed_dimension_ref.source_business_concept_id` reachable to grain AND role referenced in AST | PASS / REJECT |
| **PE-MC-8** | Runtime-readiness intent (deferred-pass until M18+) — emits `VERDICT_OPERATOR_REVIEW` with `mode='default-pass-pending-m18+'`; the operator-reject `mode='operator-reject'` branch is deferred (DBCP §4.3 D-M13-10b open) and unit-test-locked against silent regression | OPERATOR_REVIEW (always; never REJECT today) |
| **PE-MC-9** | Duplicate-intent detection — delegates to M8 `PackageSignatureService.computeIdentityTupleHash()` (canonical 6-element tuple); REJECT iff any non-archived MC has the same `identity_tuple_hash` stamped | PASS / REJECT |
| **PE-MC-10** | Self-verification fixture pass — latest `mcf.metric_self_verification_result` ordered by `executed_at`: `verdict_code='pass'` AND `stale_fixture_flag=false` AND `bound_package_signature_hash_at_run` matches M13-computed `current_package_signature_hash` | PASS / REJECT |

Aggregation rule (§4.5): `approve_eligible = all of PE-MC-{1,2,3,4,5,6,7,9,10} PASS AND PE-MC-8 ∈ {PASS, OPERATOR_REVIEW with default-pass-pending-m18+}`.

## 6. HA-1..HA-8 outcome

| HA | Statement | Enforcement | Status |
|---|---|---|---|
| HA-1 | M13 has zero call sites to `activateMetric` / `supersedeMetric` / publishing methods | Unit grep test; integration spec asserts MCV cannot reach `active` via M13 | ✓ enforced |
| HA-2 | M13 has zero imports of tenant-runtime modules | Unit import-list assertion | ✓ enforced |
| HA-3 | M13 has zero imports of `MetricDefinitionService` / `MetricDefinitionRepository` | Unit import-list assertion; integration spec asserts legacy `metric.*` row counts preserved | ✓ enforced |
| HA-4 | M13 writes no rows to `contract.*` tables | Integration spec asserts `contract.panel_output_record` + `contract.authoring_panel_rejection_log` row counts exact-preserved across the rolled-back tx | ✓ enforced |
| HA-5 | M13 emits 0 `mcf.certification_record` rows from `evaluate()` itself | Per-evaluate snapshot/delta asserts cert delta = 0 across all 3 evaluate calls (happy + reject + stale); seed's `createMetricDraft` cert writes excluded by snapshot positioning | ✓ enforced |
| HA-6 | Parent MC hash stamping happens BEFORE `review → approved` UPDATE in the same tx | Substrate trigger rejects synthetic "approve without hashes" (negative test) — substrate-side enforcement | ✓ enforced |
| HA-7 | Idempotent retry returns same `pe_result_uid[]` + `retry_mode=true` + no new writes | Integration spec second `evaluate(mcvUid, ...)` call asserts identical UID array + same MCV state + 0 row delta | ✓ enforced |
| HA-8 | Failed PE-MC → MCV transitions `draft → review` but NOT to `approved` | Unit test asserts; integration REJECT scenario asserts MCV `governance_state_code='review'` post-evaluate | ✓ enforced |

All 8 hard assertions enforced and live-verified via the integration spec running against `bc_platform_dev`.

Additionally, the integration spec asserts per-evaluate forbidden-table deltas = 0 on:
`mcf.certification_record`, `metric_authoring_panel_run`, `metric_authoring_panel_transcript`, `metric_authoring_intake_queue`, `metric_self_verification_fixture`, `metric_self_verification_result` (6 tables × 3 evaluate calls = 18 assertions). Cumulative forbidden-table deltas = 0 on `mcf.metric_supersession` and `metric.metric_definition`.

## 7. Cert model (final, locked)

Per DBCP §0bis corrective addendum (substrate-enforced authority model):

- **M13 emits 0 `mcf.certification_record` rows.** The substrate `mcf_cert_state_transition_chk` CHECK enumerates exactly 3 cert shapes (`metric_create` / `metric_transition` for active / `metric_supersede`). M13's `draft → review` and `review → approved` transitions are intentional uncertified eligibility milestones.
- **PE rows are M13's evidence ledger.** Every PE row M13 writes carries `certification_record_id = NULL`. The integration spec asserts `allPeRowsHaveNullCertId === true` across both happy and reject paths.
- **M14 owns the activation cert.** When M14 ships, it will write a `metric_transition` cert at the `approved → active` transition and may either re-evaluate or re-cite M13's PE rows. M13 emits "pre-approve" PE rows with NULL cert id; M14 will emit "activation" PE rows linked to its cert id per DBCP §4.6.

## 8. Same-transaction wiring contract (PR #130)

M13's `evaluate()` opens an outer transaction via `this.db.transaction(...)` and holds `FOR UPDATE` locks on the MCV + parent MC. Inside that tx, M13 calls **only** the M4 cert writer's **InTx variants**:

- `certWriter.submitForReviewInTx(tx, ...)` — runs draft→review state UPDATE on M13's outer tx (no internal `db.transaction()`)
- `certWriter.approveForActivationInTx(tx, ...)` — runs parent MC hash stamp + PE row INSERTs + MCV state UPDATE on M13's outer tx

Both InTx variants are public on `McfCertWriterService`, self-validate input (`InvalidInputError` thrown before any tx work in the wrapper path; thrown inside the InTx body when called directly), and do not call `this.db.transaction(...)` internally. The atomicity guarantee no longer depends on the human convention of constructing M4 with M13's db handle. The pre-existing public wrappers `submitForReview(input)` / `approveForActivation(input)` remain for backward compat and continue to open `this.db.transaction(...)`.

Unit-level proof: M13 unit spec asserts reference-equal tx forwarding into both InTx calls (`mocks.tx === submitCall[0] === approveCall[0]`); the non-InTx variants are wired as throwing mocks to catch any regression. M4 unit spec adds 4 tests for the InTx variants: 2 happy-path tests assert `fake.txOpened === false` (proving InTx does not open its own transaction); 2 validation tests assert `InvalidInputError` thrown from the InTx body.

## 9. dryRun semantics (PR #131)

`RunEvaluationOpts.dryRun = true` causes `evaluate()` to throw `EvaluationPreconditionError("M13 evaluate dryRun is not implemented; use integration SAVEPOINT or read-only preflight instead.")` BEFORE opening any transaction or calling any M4 InTx method. The field is reserved on the `RunEvaluationOpts` type for forward-compatibility with a future caller-managed dry-run pattern (caller owns the outer tx and rolls back), but the runtime refuses silent ignoring. No production caller passes `dryRun=true` today.

Unit test asserts: `dryRun=true` → throws, `mocks.db.transaction` not called, `mocks.certWriter.submitForReviewInTx` not called, `mocks.certWriter.approveForActivationInTx` not called.

## 10. First operational evaluation status

**Status: PENDING — blocked on upstream M12.5 first materialization.**

Closeout-gate query against `bc_platform_dev` (read-only):

```
mcv_total                             = 0   ← M13 input prerequisite missing
mc_total                              = 0
panel_run_apqc_total                  = 0
panel_run_approve_for_draft           = 0   (also blocks M12.5 first run)
intake_pending                        = 0   (also blocks M12.5 first run)
panel_output_record_total             = 24  (BCF-side; not coupled to MCF mcv)
framework_policy_mcf_v1_active        = 1
```

The 24 `contract.panel_output_record` rows are from prior M12 integration testing. They were written to BCF without writing the parallel MCF `mcf.metric_authoring_panel_run` substrate (M12 unit/integration tests stopped at BCF), so they cannot be consumed by M12.5 — and therefore no MCV exists for M13 to evaluate.

**Prerequisite chain for M13's first operational evaluation:**

1. **M11 intake row** in `pending` state (currently 0) — requires `scripts/mcf-m11-operator-direct-ingest.mjs` invocation (seed-script class)
2. **M12 panel run** producing `consensus_payload_json.verdict_code = 'APPROVE_FOR_DRAFT'` (currently 0) — requires real model API calls for the three-model consensus
3. **M12.5 first materialization** writing 1 MC + 1 MCV + 1 binding + 1 cert + 1 fixture + 1 verifier_result (currently 0) — requires (1) + (2)
4. **M13 evaluate(mcvUid)** against the newly-materialized MCV (currently 0 eligible MCVs) — this closeout step

All four prerequisites fall under the closeout gate's "do not" list (no seed scripts unless authorized; no real model API calls; no operational M12.5 materialization). None were attempted.

## 11. Unblocking paths for the first operational evaluation (separate authorization required)

| Path | Description | Trade-off |
|---|---|---|
| **(a) Synthetic first evaluation** | Operator authorizes (i) inserting a hand-crafted `consensus_payload_json` directly into `mcf.metric_authoring_panel_run`, (ii) M12.5 first materialization, (iii) M13 first evaluation against the materialized MCV | Proves M13 service path only against synthetic upstream; does NOT prove M11 → M12 → M12.5 → M13 end-to-end |
| **(b) Real M12 panel run** | Operator authorizes M11 intake submission + a real-model M12 panel run; M12.5 materializes; M13 evaluates | Full evidence chain; requires real-model budget + operator-procured model tokens |
| **(c) Cached-transcript replay** | If a panel transcript can be replayed without re-invoking models (M12 design TBD), operator authorizes the replay path | Lower-cost evidence chain; depends on M12 transcript-replay capability |

Each path is operator-authorized in isolation; this closeout doc does not propose one over another.

## 12. First-evaluation artifact (deliberately NOT written)

The M-series post-apply / first-run convention reserves the `mcf-m13-first-evaluation-<ts>.{summary.md,evidence.jsonl}` filename for an artifact documenting an actual operational run with real DB writes. **No such run occurred**; therefore, no `mcf-m13-first-evaluation-*` artifact has been written. The corresponding closeout-gate state is documented in `bc-core/scripts/audit-output/mcf-m13-closeout-readiness-2026-05-28T14-01-39-509Z.summary.md`. When the operational evaluation happens, the first-evaluation artifact will be written at that point.

## 13. Verification gates (bc-core)

| Gate | Result |
|---|---|
| ESLint `--max-warnings 0` on `metric-publication-eligibility-evaluator.service.ts` + `mcf-cert-writer.service.ts` | exit 0 |
| Filtered `tsc --noEmit` for M13 + M4 files | CLEAN |
| M13 unit spec (`metric-publication-eligibility-evaluator.service.spec.ts`) | **42/42 PASS** |
| M4 unit spec (`mcf-cert-writer.service.spec.ts`) | **39/39 PASS** |
| M13 live integration spec (`BCCORE_INTEGRATION_DB=1`) | **1/1 PASS** (happy + retry + REJECT + stale-package retry; 18 forbidden-table per-evaluate deltas all 0; all PE rows carry `certification_record_id=NULL`) |
| M4 live integration spec (`BCCORE_INTEGRATION_DB=1`) | **7/7 PASS** |
| Full `vitest run src/registry/mcf/` | **473 PASS / 11 skipped** (0 regressions; skipped = integration tests requiring `BCCORE_INTEGRATION_DB=1`) |

All gates green. Post-test DB baseline identical to pre-test (SAVEPOINT rolled back).

## 14. Scope discipline

- No operational M13 evaluation run.
- No operational M12.5 materialization run.
- No synthetic M11/M12/M12.5 data created.
- No seed scripts run.
- No DDL applied during closeout.
- No bc-admin, tenant runtime, controllers, or DI modules touched.
- M14 remains CLOSED.
- `bc-postgres` MCP `allow_write=false` throughout.

## 15. Next operator-authorized step

M13 is ready to ship operational evaluation as soon as the upstream prerequisite chain produces an eligible MCV. The next operator-authorized step is one of the unblocking paths listed in §11. Once an eligible MCV exists, a single `evaluate(mcvUid, { actorSub, actorRoleAtAction })` call against the production wiring will produce the first-evaluation artifact.

M14 (publication / `activateMetric`) remains CLOSED pending M13 first operational evaluation closeout.
