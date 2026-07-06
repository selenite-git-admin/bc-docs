---
uid: metric-context-framework-m12-5-materialization-legacy-bridge-dbcp
title: MCF M12.5 Materialization + Legacy Bridge DBCP
description: Combined design-blueprint for MCF gate M12.5 (Materialization + Legacy Bridge) per operator-accepted preflight decisions D-M12.5-1..D-M12.5-12 + D-M12.5-AST + D-M12.5-MC-NAME-IDEMPOTENCY (polished preflight `57e828b`). Locks M12.5-A — single combined gate that converts an APPROVE_FOR_DRAFT panel proposal from `mcf.metric_authoring_panel_run.consensus_payload_json` into live MCF substrate via three short transactions (TX A = M4 `McfCertWriterService.createMetricDraft` with real canonical AST per AST-A; TX B = `mcf.metric_self_verification_fixture` INSERT with 6 computed hash columns; TX C = M10 `MetricSelfVerificationService.verifyFixture` + M11 `markConsumedByPanel` paired commit). M12.5 stops at `governance_state_code='draft'`; NO PE-MC writes; NO publication; NO supersession. Three already-shipped service deltas land in the impl PR: (i) M4 amendment per AST-A (optional `metricContractVersion.formulaAstCanonicalJson` field + `insertMcv()` pass-through; back-compatible); (ii) new `MetricAuthoringMaterializationService` orchestrator; (iii) `Sunset` HTTP header decorator on `MetricDefinitionController.create()` + `bulkCreate()` (operator-configured env var; no hardcoded default). One small DDL gate per MC-NAME-A — adds partial unique index `CREATE UNIQUE INDEX idx_mcf_mc_mc_name_active ON mcf.metric_contract(mc_name) WHERE archived_at IS NULL` (mirrors existing `idx_mcf_mc_identity_active` pattern; sub-30-second apply; reversible via single `DROP INDEX`). Idempotency is substrate-provided at every step (M4 `metric_cert_writer_idempotency` PK + fixture UNIQUE + verifier UNIQUE + intake CAS). Hard assertions HA-1..HA-8 as impl acceptance criteria. R-M12.5-1 RESOLVED from code reading — M10 verifier reads NOTHING from parent MC's `package_signature_hash` column; composes current package hash from MCV substrate via `FormulaCanonicalizationService` + `PackageSignatureService`; STALE CHECK passes deterministically when M12.5 stamps `bound_package_signature_hash` from the same MCV substrate at TX B. Legacy bridge is light-touch — Sunset header + read-fallback policy doc + operator runbook + CLAUDE.md note. NO HTTP 410 (M17), NO bc-admin changes (M16/M17), NO tenant runtime migration (M18+). NO bc-core implementation this session. NO DDL apply this session. NO real model API calls. NO MC / fixture / cert / verifier rows written. NO intake transitions. NO M13/M14+ work. NO BCF touches.
status: draft
date: 2026-05-28
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m12-5-materialization-legacy-bridge-dbcp
---

# MCF M12.5 Materialization + Legacy Bridge DBCP

## 0. PR-2 implementation addendum (post-operator-review)

**Effective from bc-core commit `77cd8a4` (PR-2 BLOCKER patches).** The shipped PR-2 differs from the original DBCP text in two ways below; the rest of the DBCP (TX A/B/C design, HA-1..HA-8, 6 fixture hash columns, M4 AST-A amendment, Sunset header, read-fallback policy) is implemented as authored.

1. **CLI scope reduced to preflight-only.** The DBCP authored a CLI invocation script `scripts/mcf-m12-5-materialize.mjs` that would invoke the materialization service end-to-end (per D-M12.5-7 / §10.3 / §18.1 row 11). Per operator review feedback, the shipped CLI is renamed to `scripts/mcf-m12-5-preflight.mjs` and is a READ-ONLY preflight verifier (5 substrate probes: mapr APPROVE_FOR_DRAFT, framework_policy exact-1-active, PR-1 index present, M11 intake state, HA-8 retry detection). Direct service invocation is wired through NestJS DI (the `MetricAuthoringMaterializationService` is registered in the MCF module alongside its 6 collaborators); a NestJS-bootstrap one-shot CLI for direct operator invocation is deferred to a follow-up PR. The integration spec wiring pattern (`bc-core/src/registry/mcf/metric-authoring-materialization.service.integration.spec.ts`) is the canonical reference for how to construct + invoke the service today.

2. **M4 cert-writer `insertMcvChildRows` bug fix (necessary precondition for HA-5).** The pre-existing M4 mapper used `variableCode` instead of the Drizzle schema's `variableRoleCode` (silently dropping every variable binding insert) and omitted required NOT NULL fields (`roleKindCode`, `structuralSortKey`) and the 3 binding snapshot fields. The bug was never hit because M4's own integration spec doesn't exercise variableBindings — M12.5 materialization is the first caller to write a binding row end-to-end. The fix (extended `VariableBindingInput` interface with 5 optional fields, back-compatible with pre-M12.5 callers; fixed mapper field names + derived `structuralSortKey`) is part of PR-2. References to "M4 amendment per AST-A" in this DBCP should be read as "M4 amendment per AST-A + insertMcvChildRows RCA fix per SES-8a7f5b".

The integration spec runs live against `bc_platform_dev` under SAVEPOINT rollback and PASSES end-to-end with all HA-1..HA-8 assertions + jsonb_typeof = 'object' proofs on every jsonb column written. Live DB confirmed unchanged after rollback.

## 1. Scope and grounding

Design the `MetricAuthoringMaterializationService` orchestrator + the small M4 cert-writer amendment + the one-index DDL gate + the legacy `Sunset` header — per the polished M12.5 preflight (`57e828b`) and the operator-accepted 14 decisions. The deliverable is the M12.5 implementation PR scope: M4 amendment per AST-A; new service file; bridge header + doc chapter + runbook + CLAUDE.md note; SAVEPOINT-rolled-back integration spec; DDL apply gate per MC-NAME-A.

**No substrate write at DBCP-author time. No DDL apply. No code change. No data write. No real model API call.**

### 1.1 Source documents consumed (with concrete citations)

| Source | Role | Reference |
|---|---|---|
| M12.5 preflight (polished) | 14 decisions; HA outline; M12.5-A scope qualifiers (AST-A + MC-NAME-A); R-M12.5-1 RESOLVED framing | `bc-docs-v3` `57e828b` `docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-preflight.md` |
| Pre-M12 wiring impact audit | M12.5 gate originating authority | `bc-docs-v3` `e725263` `docs/implementation/mcf-post-bcf-metric-workflow-wiring-impact.md` |
| M12 closeout | M12 substrate state (mapr+mapt+panel_output_record live; intake at 0; allowlists empty) | `bc-docs-v3` `4c47679` `docs/implementation/mcf-m12-implementation-closeout.md` |
| M12 DBCP | `consensus_payload_json` v1 schema (M12.5 input contract); HA-7 single-source schema literal | `bc-docs-v3` `0798692` `docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` §8 |
| M4 cert writer DBCP | `McfCertWriterService.createMetricDraft` semantics + NF1 all-or-none + idempotency table + `assertActiveMcfPolicy` requirement | `bc-docs-v3` `3983530` `docs/implementation/metric-context-framework-m4-lifecycle-certification-dbcp.md` |
| M7/M8 hash authority DBCP | `mcf-hash-v1` algorithm bundle; `FormulaCanonicalizationService` + `PackageSignatureService` interfaces | `bc-docs-v3` `62ec707` `docs/implementation/metric-context-framework-m7-m8-formula-hash-authority-dbcp.md` |
| M9 fixture substrate DBCP | Fixture substrate columns / CHECKs; `FixtureStructuralCheckService.runStructuralChecks` + `loadFixtureContext` interfaces | `bc-docs-v3` `620e11d` `docs/implementation/metric-context-framework-m9-fixture-substrate-dbcp.md` |
| M10 self-verification DBCP | `MetricSelfVerificationService.verifyFixture` 6-step pipeline; sync per D-M10-5 (caller's tx) | `bc-docs-v3` `ea8b708` `docs/implementation/metric-context-framework-m10-self-verification-result-dbcp.md` |
| M11 reservoir DBCP | `markConsumedByPanel(intakeQueueUid, deps)` signature + CAS guard pattern | `bc-docs-v3` `42f702b` `docs/implementation/metric-context-framework-m11-reservoir-ingestion-dbcp.md` |
| Live `McfCertWriterService` | `createMetricDraft` method body; `insertMcv()` private helper (column list); `assertActiveMcfPolicy` SQL | `bc-core/src/registry/mcf/mcf-cert-writer.service.ts:349` (class) + `:829` (`createMetricDraft`) + `:737` (`insertMcv`) + `:392` (`assertActiveMcfPolicy`) |
| Live `FormulaCanonicalizationService` | Three hash compute methods; placeholder-AST `InvalidAstError` guard | `bc-core/src/registry/mcf/formula-canonicalization.service.ts:631` (`computeFormulaIntentHash`) + `:652` (`computeVariableBindingSetHash`) + `:692` (`computeFilterSetHash`) + `:113-118` (placeholder guard) |
| Live `PackageSignatureService` | Fixture-hash + intermediate + package-signature compose methods | `bc-core/src/registry/mcf/package-signature.service.ts:240` (`computePackageSignatureHash`) + `:214` (`computeGrainFilterTemporalDimensionSignatureHash`) + `:291` (`computeSelfVerificationFixtureHash`) |
| Live `FixtureStructuralCheckService` | `runStructuralChecks(context, body)` + `loadFixtureContext` exported helper | `bc-core/src/registry/mcf/fixture-structural-check.service.ts:759` (`runStructuralChecks`) + `:802` (`loadFixtureContext` exported) |
| Live `MetricSelfVerificationService` | `verifyFixture(fixtureUid, deps)` + `computeCurrentPackageHash` (R-M12.5-1 evidence) | `bc-core/src/registry/mcf/metric-self-verification.service.ts:102` (`verifyFixture`) + `:210-222` (`computeCurrentPackageHash`) |
| Live `ReservoirIngestionService` | `markConsumedByPanel(uid, deps)` + `transitionStatus` CAS pattern | `bc-core/src/registry/mcf/reservoir-ingestion.service.ts:265` (`markConsumedByPanel`) + `:290` (`transitionStatus`) |
| Live legacy `MetricDefinitionController` | `POST /api/metric-catalog/definitions` + `/upload` route handlers (Sunset header targets) | `bc-core/src/registry/metric-definition.controller.ts:15` (`@Controller` + `@PlatformOnly`) + `:18` (`create()`) + `:47` (`bulkCreate()`) |
| Live `mcf.metric_contract` substrate | Index inventory — confirms NO unique on `mc_name`; partial unique on `(identity_tuple_hash, hash_algorithm_version)` | Verified via `bc-postgres` MCP (this DBCP session — see §2) |
| Live `contract.framework_policy` | mcf_v1 row active; `policy_version='1.0.0'`; `effective_to=NULL` | Verified via `bc-postgres` MCP (this DBCP session) |

### 1.2 Discipline assertions (this DBCP-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits this DBCP-author session | ✓ — design only |
| No DDL applied | ✓ |
| No data writes | ✓ |
| No seed runs | ✓ |
| No real model API calls | ✓ |
| No MC / MCV / fixture / cert / verifier rows | ✓ |
| No intake transitions | ✓ |
| No M13 / M14+ work | ✓ |
| No BCF data touched | ✓ |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) — read-only verification only |

---

## 2. Pre-DBCP empirical verification (read-only `bc-postgres` MCP at DBCP-author time)

| Probe | Result |
|---|---|
| bc-core main | `f3f527b8bc7a0b229a8548fd5014aeeeb8017a7e` (untouched since M12 evidence merge) |
| bc-docs-v3 main | `57e828b64cc3143395a9c850cf5461b39b833bfa` (polished preflight) |
| `contract.framework_policy` WHERE `policy_uid='mcf_v1'` | 1 row: `scope_code='mcf'`, `policy_version='1.0.0'`, `effective_from='2026-05-27T04:39:25.510Z'`, `effective_to=NULL` (active) |
| `mcf.metric_contract` indexes (5) | `metric_contract_pkey` (PK on `metric_contract_uid`); `idx_mcf_mc_archived_at_active` (partial btree); `idx_mcf_mc_grain_entity` (btree); `idx_mcf_mc_identity_active` (UNIQUE partial on `(identity_tuple_hash, hash_algorithm_version) WHERE archived_at IS NULL AND identity_tuple_hash IS NOT NULL`); `idx_mcf_mc_mc_name` (**non-unique** btree) — **confirms NO substrate-level `UNIQUE(mc_name)` currently exists; MC-NAME-A DDL is novel** |
| `mcf.metric_self_verification_fixture` schema | 16 columns (incl. 6 NOT-NULL hash columns + `rationale_text >= 40` + `hash_algorithm_version ~ '^mcf-[a-z-]+-v[0-9]+$'`); FKs `fk_msvf_mc` / `fk_msvf_mcv` / `fk_msvf_panel_run`; UNIQUE `uq_msvf_mcv_fixture_hash(metric_contract_version_uid, self_verification_fixture_hash)` |
| `mcf.metric_self_verification_result` schema | UNIQUE `uq_msvr_fixture_version_pkg_hash(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` — M10 idempotency surface |
| `mcf.certification_record` schema | `mcf_cert_action_code_chk` (`'metric_create' \| 'metric_transition' \| 'metric_supersede'`); `mcf_cert_state_transition_chk` (binds action_code to from/to_state); `mcf_cert_nf1_all_or_none_chk` (6 panel-attestation fields all-NULL or all-non-NULL); `fk_mcf_cert_panel_run` → `contract.panel_output_record(panel_run_uid)` ON DELETE RESTRICT |
| `mcf.metric_cert_writer_idempotency` schema | 6 cols; PK on `idempotency_key`; `mcwi_status_chk` (`'pending' \| 'committed' \| 'rolled_back'`) |
| `mcf.metric_contract_version` | `formula_ast_canonical_json jsonb NOT NULL DEFAULT '{"kind": "placeholder", "reason": "created_before_m7_apply"}'::jsonb` — confirms B1 placeholder-default condition addressed by AST-A |
| All 17 `mcf.*` tables | 0 rows (substrate dormant) |
| BCF preserved | `contract.panel_output_record = 24`; `contract.authoring_panel_rejection_log = 1` |

### 2.1 Code citations re-confirmed

| Citation | Evidence |
|---|---|
| M4 `CreateMetricDraftInput.metricContractVersion` has NO `formulaAstCanonicalJson` field today | `mcf-cert-writer.service.ts:163-173` — fields enumerated: `versionCode`, `versionSeq`, `descriptionText?`, `functionCode?`, `subfunctionCode?`, `ownerJson?`, `tags?`, `thresholdJson?`, `supersedesVersionUid?`. No `formulaAstCanonicalJson`. |
| M4 `insertMcv()` writes only the enumerated columns; `formula_ast_canonical_json` falls back to DDL default | `mcf-cert-writer.service.ts:737-755` — INSERT shape matches the input type; AST not stamped. |
| M4 integration spec workaround documents the gap verbatim | `mcf-cert-writer.service.integration.spec.ts:198-204` (`seedNonPlaceholderAst` raw UPDATE); test comment at `:226-229` says: *"createMetricDraft does not yet accept an AST parameter; future M5 panel work adds that"* |
| M7 `computeFormulaIntentHash` throws `InvalidAstError` on placeholder | `formula-canonicalization.service.ts:113-118` (inside `validateAndNormalizeAst`); called from `computeFormulaIntentHash` at `:640` |
| M10 `computeCurrentPackageHash` reads NOTHING from parent MC's `package_signature_hash` column | `metric-self-verification.service.ts:210-222` — composes from `FormulaCanonicalizationService.computeFormulaIntentHash/computeVariableBindingSetHash/computeFilterSetHash` + `PackageSignatureService.computePackageSignatureHash` |
| M11 `markConsumedByPanel(intakeQueueUid, deps): Promise<void>` | `reservoir-ingestion.service.ts:265-267` — single-method wrapper around `transitionStatus(uid, 'pending', 'consumed_by_panel', null, deps.tx)` |
| `transitionStatus` CAS guard | `reservoir-ingestion.service.ts:290-314` — SELECT-then-UPDATE-with-status-guard; throws `InvalidStatusTransitionError` if not pending |

---

## 3. Accepted operator decisions (14 — D-M12.5-1..D-M12.5-12 + D-M12.5-AST + D-M12.5-MC-NAME-IDEMPOTENCY)

| # | Decision | Locked |
|---|---|---|
| **D-M12.5-1** | M12.5 scope — exactly MC + MCV + bindings + filters + computed_dims + cert (via M4) + 1 fixture + 1 verifier result + 1 intake transition. NO PE-MC, NO publication, NO supersession | ACCEPTED |
| **D-M12.5-2** | Cert path — through `McfCertWriterService.createMetricDraft` ONLY (HA-2 in M12 released for M12.5) | ACCEPTED |
| **D-M12.5-3** | Fixture + verifier minimum — ≥1 fixture INSERT + 1 verifier result; any verdict (pass/fail/structural_reject) acceptable for declaring materialization complete | ACCEPTED |
| **D-M12.5-4** | Idempotency model — per-step substrate-provided (M4 idempotency table + fixture UNIQUE + verifier UNIQUE + intake CAS); `idempotencyKey = 'mcf-m12-5/' + panel_run_uid` | ACCEPTED |
| **D-M12.5-5** | Transaction boundary — 3 short TXs (A = M4-owned with AST-A; B = fixture hash computation + INSERT; C = verifier result + intake transition paired) | ACCEPTED |
| **D-M12.5-6** | Legacy bridge — Sunset HTTP header on legacy POST (operator-configured env var; NO hardcoded default); read-fallback policy doc; operator runbook; CLAUDE.md note. NO HTTP 410 (M17); NO bc-admin changes (M16/M17); NO tenant runtime migration (M18+) | ACCEPTED |
| **D-M12.5-7** | bc-admin / UI impact — NONE in M12.5; service-only + 1 controller header decorator; CLI script — per §0 PR-2 addendum the v1 surface is preflight-only (`scripts/mcf-m12-5-preflight.mjs`); NestJS-bootstrap direct-invocation CLI deferred | ACCEPTED (PR-2 implementation adjustment per §0) |
| **D-M12.5-8** | Readiness / chain-status / boundary metric wiring — UNCHANGED; tenant runtime MCF awareness ships M18+ | ACCEPTED |
| **D-M12.5-9** | Materialization validation — L-V1 precondition + L-V2 AJV schema + L-V3 M9 structural re-check; all BEFORE TX A opens; 6 fixture hash columns computed before TX B INSERT | ACCEPTED |
| **D-M12.5-10** | Evidence plan — SAVEPOINT-rolled-back integration spec mandatory for impl PR merge; first real materialization is operator-driven post-closeout | ACCEPTED |
| **D-M12.5-11** | Stop conditions / rollback — TX-level rollback only; substrate immutability preserved (Invariant III); retry resumes via idempotency surfaces; `markConsumedByPanel` only after TX C verifier result INSERT succeeds | ACCEPTED |
| **D-M12.5-12** | Gate sequencing — M13 BLOCKED until M12.5 closeout; M14 BLOCKED until M13 closeout | ACCEPTED |
| **D-M12.5-AST** | Option **AST-A** — amend `McfCertWriterService.createMetricDraft` to accept optional `metricContractVersion.formulaAstCanonicalJson`; `insertMcv()` writes real canonical AST during TX A; back-compatible; NO raw UPDATE workaround; NO separate AST stamping TX | ACCEPTED — **AST-A locked** |
| **D-M12.5-MC-NAME-IDEMPOTENCY** | Option **MC-NAME-A** — small DDL gate adding `CREATE UNIQUE INDEX idx_mcf_mc_mc_name_active ON mcf.metric_contract(mc_name) WHERE archived_at IS NULL` (mirrors `idx_mcf_mc_identity_active` pattern) | ACCEPTED — **MC-NAME-A locked** |

---

## 4. M12.5 ownership boundary

### 4.1 M12.5 MUST own  *(PR-1 = DDL/substrate; PR-2 = implementation/service; per patch M-2)*

| # | Deliverable | Location | PR |
|---|---|---|---|
| 1 | DDL file per MC-NAME-A | New `bc-core/docker/redesign/<NN>-mcf-m12-5-mc-name-unique-index.sql` | **PR-1** |
| 2 | Rollback DDL | New `bc-core/docker/redesign/<NN>R-mcf-m12-5-mc-name-unique-index-rollback.sql` (per repo convention) | **PR-1** |
| 3 | DDL dry-run verifier | New `bc-core/scripts/mcf-m12-5-dry-run.mjs` (per M11 / M9 / M5 / M4 / M3 pattern) | **PR-1** |
| 4 | DDL post-apply verifier | New `bc-core/scripts/mcf-m12-5-post-apply.mjs` (per same pattern; crash-safe BEGIN/ROLLBACK per patch M-3) | **PR-1** |
| 5 | DDL apply evidence artifacts | New `bc-core/scripts/audit-output/mcf-m12-5-dry-run-<timestamp>.{precondition.jsonl, planned-sql.sha256.txt, summary.md}` + `mcf-m12-5-post-apply-<timestamp>.{evidence.jsonl, summary.md}` (committed in PR-1 alongside scripts) | **PR-1** |
| 6 | `MetricAuthoringMaterializationService` orchestrator with `runMaterialization(panelRunUid, opts, deps): Promise<MaterializationResult>` | New `bc-core/src/registry/mcf/metric-authoring-materialization.service.ts` | **PR-2** |
| 7 | Unit spec for the materialization service | New `bc-core/src/registry/mcf/metric-authoring-materialization.service.spec.ts` (14 decision-coverage tests minimum) | **PR-2** |
| 8 | SAVEPOINT-rolled-back integration spec | New `bc-core/src/registry/mcf/metric-authoring-materialization.service.integration.spec.ts` (env-gated `BCCORE_INTEGRATION_DB=1`) | **PR-2** |
| 9 | M4 amendment per AST-A — optional `formulaAstCanonicalJson` field + `insertMcv()` pass-through + retire `seedNonPlaceholderAst` workaround | Edit `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` (`CreateMetricDraftInput.metricContractVersion` interface + `insertMcv()` body) + `bc-core/src/registry/mcf/mcf-cert-writer.service.integration.spec.ts` (remove helper + replace call sites with the new input field) | **PR-2** |
| 10 | `res.setHeader('Sunset', operatorConfiguredDate)` inside route-handler body (per patch L-2 — `@Header` decorator unsuitable because the value is read from env at runtime, not class-definition time) | Edit `bc-core/src/registry/metric-definition.controller.ts` (`create()` + `bulkCreate()` methods) | **PR-2** |
| 11 | CLI preflight verifier (scope reduced per §0 PR-2 addendum) | New `bc-core/scripts/mcf-m12-5-preflight.mjs` (read-only; 5 substrate probes; does NOT invoke materialization). Direct-invocation NestJS-bootstrap CLI deferred to follow-up PR. | **PR-2** |
| 12 | Bridge documentation chapter | New `bc-docs-v3/docs/operating-model/mcf-legacy-bridge.md` (read-fallback policy text per §12.2 + Sunset header semantics) | **PR-2** |
| 13 | Operator runbook update | Edit `bc-docs-v3/docs/onboarding/metric-registration.md` (add MCF intake → panel → materialization flow section) | **PR-2** |
| 14 | CLAUDE.md note | Edit `barecount-devhub/CLAUDE.md` (short bullet in MCF substrate section) | **PR-2** |

**PR ordering (per patch M-2 — matches M11 / M9 pattern):**
1. **PR-1 lands first.** DDL is dry-run + applied + post-apply-verified against `bc_platform_dev`. Then PR-1 merges to bc-core main.
2. **PR-2 lands after PR-1.** PR-2's `MetricAuthoringMaterializationService` depends on `idx_mcf_mc_mc_name_active` existing (for `DuplicateMcNameError` catch path); merging PR-2 before PR-1 is applied would leave the service silently producing duplicate MCs on concurrent runs.

### 4.2 M12.5 MUST NOT own

| # | Out-of-scope | Belongs to |
|---|---|---|
| 1 | PE-MC evaluation (`mcf.metric_publication_eligibility_result` writes) | M13 |
| 2 | Publication path (`approveForActivation` / `activateMetric` calls; review→approved→active state transitions) | M14 |
| 3 | Supersession (`supersedeMetric`) | M15 |
| 4 | Operator console UI (read or write) | M16 + M17 |
| 5 | HTTP 410 on legacy POST | M17 |
| 6 | bc-admin frontend metric API surface changes | M16 + M17 |
| 7 | Tenant runtime MCF awareness (`boundary/metric.service.ts`, `ReadinessLedgerService`, `chain-status.service.ts`) | M18+ |
| 8 | Legacy `metric.metric_definition` decommission | M19+ (if ever) |
| 9 | 9 seed loader retargeting to MCF intake | Separate operator-driven program (not a gate) |
| 10 | Real model vendor API calls | NEVER from M12.5; mocked agents in spec |
| 11 | BCF substrate writes (`contract.business_entity` / `business_concept` / `concept_registry.*` / `contract.panel_output_record`) | NEVER from M12.5; M12.5 reads `contract.panel_output_record` only via mapr FK navigation |
| 12 | Reservoir ingestion (M11) | M11 (already shipped) |
| 13 | M12 panel runs (M12) | M12 (already shipped) |
| 14 | M4 cert writer's other 4 methods (`submitForReview` / `approveForActivation` / `activateMetric` / `supersedeMetric`) | M14 / M15 |
| 15 | M9 fixture substrate amendment | NEVER from M12.5 (use existing substrate as-is) |
| 16 | M10 verifier algorithm change | NEVER from M12.5 (use M10 as-is) |
| 17 | M11 status enum extension | NEVER from M12.5 |

---

## 5. Execution flow (13 steps; 3 short TXs)

`MetricAuthoringMaterializationService.runMaterialization(panelRunUid, opts, deps)` executes the following sequence. **Critical**: the M4 amendment per AST-A is what makes Step 9 (TX A) stamp a real canonical AST into MCV — without that, Step 10's hash computation throws `InvalidAstError` at Step 10a.

```
Step  1: Read mapr row by panel_run_uid (no tx — read-only SELECT)
           - assert verdict_code = 'APPROVE_FOR_DRAFT' (else MaterializationPreconditionError)
Step  2: Read consensus_payload_json; extract candidate_proposal + intake_back_reference
Step  3: Read intake row by intake_back_reference.intake_queue_uid (no tx — read-only SELECT)
           - assert status_code = 'pending' (else MaterializationPreconditionError)
Step  4: L-V1 precondition checks (verdict, ≥1 fixture, Checker C-FX passed, intake pending)
Step  5: L-V2 AJV validate consensus_payload_json against panel-payload.schema.json
Step  6: L-V3 M9 structural re-check on proposed_fixtures[0]
Step  7: Runtime policy lookup (no tx — read-only SELECT)
           SELECT policy_version FROM contract.framework_policy
           WHERE policy_uid = 'mcf_v1' AND scope_code = 'mcf'
             AND (effective_to IS NULL OR effective_to > now())
           ORDER BY effective_from DESC                 -- deterministic latest-wins per patch M-1
           LIMIT 2                                      -- read 2 to detect overlap
           If 0 rows → throw FrameworkPolicyMissingError.
           If >1 rows → throw MultipleActivePoliciesError (strict fail-fast; operator must
             expire the stale row before M12.5 proceeds).
           If 1 row → capture row[0].policy_version as activeMcfPolicyVersion.
Step  8: Compose CreateMetricDraftInput from candidate_proposal + cert context
           - metricContractVersion.formulaAstCanonicalJson = candidate_proposal.formula_ast (AST-A)
           - cert.policyVersion = activeMcfPolicyVersion
           - cert.panelRunUid = mapr.panel_run_uid + 5 other NF1 fields populated together
           - idempotencyKey = 'mcf-m12-5/' + panelRunUid
Step  9: TX A (M4-owned): await certWriter.createMetricDraft(input)
           → { metricContractUid, metricContractVersionUid, certificationRecordId }
           - On unique_violation on idx_mcf_mc_mc_name_active → DuplicateMcNameError
           - On NF1 violation / framework_policy inactive / drizzle error → re-throw
Step 10: Compute 6 fixture hash columns from MCV substrate (reads inside a short tx OR Step 11's tx)
           - formulaIntentHash       = formulaCanon.computeFormulaIntentHash(mcvUid, { tx })
           - variableBindingSetHash  = formulaCanon.computeVariableBindingSetHash(mcvUid, { tx })
           - filterSetHash           = formulaCanon.computeFilterSetHash(mcvUid, { tx })
           - gftdSignatureHash       = packageSig.computeGrainFilterTemporalDimensionSignatureHash(
                                          mcvUid, { filterSetHash }, { tx })
           - boundPackageSigHash     = packageSig.computePackageSignatureHash(
                                          mcvUid,
                                          { formulaIntentHash, variableBindingSetHash, filterSetHash },
                                          { tx })
           - fixtureBodyHash         = packageSig.computeSelfVerificationFixtureHash(fixtureBody)
Step 11: TX B (M12.5-owned): INSERT mcf.metric_self_verification_fixture
           - Reads in Step 10 and the INSERT happen in the SAME tx for read consistency
           - Catch unique_violation on uq_msvf_mcv_fixture_hash → SELECT existing fixture_uid
           - Commit
Step 12: TX C (M12.5-owned; single tx wrapping both writes):
           (a) await verifier.verifyFixture(fixture_uid, { tx })
                → { verdict_code, verification_result_uid }
                - M10's STALE CHECK passes deterministically per R-M12.5-1 RESOLVED
                - M10 catches unique_violation internally → SELECT existing
           (b) await reservoir.markConsumedByPanel(intake_queue_uid, { tx })
                - Catch InvalidStatusTransitionError if already consumed → treat as no-op success
           Commit
Step 13: Return MaterializationResult
```

### 5.1 Per-step contract details

**Step 1 — Read mapr.** `SELECT panel_run_uid, workbench_fingerprint_hash, consensus_payload_json, reservoir_name, reservoir_entry_id FROM mcf.metric_authoring_panel_run WHERE panel_run_uid = ${panelRunUid}`. If 0 rows → `MaterializationPreconditionError("mapr not found")`. Assert `consensus_payload_json->>'verdict_code' = 'APPROVE_FOR_DRAFT'` else `MaterializationPreconditionError("not APPROVE_FOR_DRAFT")`.

**Step 2 — Extract candidate_proposal + intake_back_reference.** Parse `consensus_payload_json` per M12 DBCP §8.1 schema. Extract `candidate_proposal` (the Maker's proposal that the panel approved) + `intake_back_reference` (back-pointer to the M11 intake row that seeded this panel run).

**Step 3 — Read intake row.** `SELECT status_code, reservoir_name, reservoir_entry_id FROM mcf.metric_authoring_intake_queue WHERE intake_queue_uid = ${intake_back_reference.intake_queue_uid}`. If 0 rows → `IntakeRowNotFoundError`. Assert `status_code = 'pending'` else `MaterializationPreconditionError("intake already consumed/rejected/superseded")`.

**Step 4 — L-V1 precondition checks.** Four assertions:
- (a) `consensus_payload_json.verdict_code === 'APPROVE_FOR_DRAFT'` (re-assert from Step 1)
- (b) `candidate_proposal.proposed_fixtures.length >= 1`
- (c) `candidate_proposal.proposed_fixtures[0].checker_c_fx_result.passed === true`
- (d) intake.status_code === 'pending' (re-assert from Step 3)

Any failure → `MaterializationPreconditionError` with specific reason; no TX opens; no write happens.

**Step 5 — L-V2 AJV schema validation.** AJV (already wired in M12 panel service) validates `consensus_payload_json` against `bc-core/src/registry/mcf/panel-payload.schema.json` (HA-7 single-source). M12.5 imports the SAME schema literal — assert sha256 matches per HA-7 round-trip test. Failure → `ConsensusPayloadValidationError`.

**Step 6 — L-V3 M9 structural re-check.** Build a `FixtureContext` IN-MEMORY from `candidate_proposal` (we do NOT have MCV substrate yet — that comes from TX A): grain, temporal gate, formula AST, variable bindings, filter clauses, computed_dim refs all from `candidate_proposal`. **Per patch L-3**: since no MCV exists at Step 6 time, M12.5 supplies placeholder uuid values for `FixtureContext.mcvUid` + `FixtureContext.metricContractUid` (recommend `'00000000-0000-0000-0000-000000000000'` for both; or `crypto.randomUUID()` — either is fine). The M9 `runStructuralChecks(context, body)` function does NOT depend on these uuids for any of the C-FX-1..C-FX-11 check logic (they are metadata-only fields on the `FixtureContext` interface, used by callers that load context from substrate). Verified by inspecting M9 source — uuids appear only on the returned defect payloads, never as inputs to check predicates. Build `fixtureBody` from `candidate_proposal.proposed_fixtures[0].{section_a_inputs_json, section_b_expected_output_json, section_c_resolver_config_json}`. Call `structuralCheck.runStructuralChecks(context, fixtureBody)`. If `result.passed === false` → `FixtureStructuralCheckFailedError` with `result.defects[]`.

**Step 7 — Runtime policy lookup.** Single SELECT (no tx) with `ORDER BY effective_from DESC LIMIT 2` (read 2 to detect overlap). Captures `activeMcfPolicyVersion` from row[0] (currently `'1.0.0'`). Three outcomes:
- **0 rows** → throw `FrameworkPolicyMissingError` (operator must seed the row before M12.5 runs).
- **>1 rows** → throw `MultipleActivePoliciesError` (strict fail-fast per patch M-1). `contract.framework_policy_pk` is composite `(policy_uid, policy_version)`, so two simultaneously-active `mcf_v1` rows with different `policy_version` values (e.g. `'1.0.0'` and `'1.0.1'` both with `effective_to IS NULL`) are structurally possible. M12.5 refuses to proceed under that ambiguity — operator must expire the stale row before re-trying.
- **1 row** → use `row[0].policy_version`.

**Step 8 — Compose CreateMetricDraftInput.** Build the input per M4 DBCP shape + AST-A field:

```typescript
const createInput: CreateMetricDraftInput = {
  metricContract: {
    mcName: candidate_proposal.candidate_name,
    displayName: candidate_proposal.display_name,
    grainEntityId: candidate_proposal.grain.grain_entity_id,
    temporalGateShapeCode: candidate_proposal.temporal_gate.temporal_gate_shape_code,
    temporalGateParamsJson: candidate_proposal.temporal_gate.temporal_gate_params_json,
    candidateSourceRefJson: {
      source_type: 'operator_direct' | 'seed_metric' | 'metric_definition',
      panel_run_uid: panelRunUid,
      intake_queue_uid: intake.intake_queue_uid,
    },
    createdByName: opts.certifierEmail ?? 'mcf-m12-5-materializer',
  },
  metricContractVersion: {
    versionCode: 'v1',
    versionSeq: 1,
    descriptionText: candidate_proposal.description_text,
    functionCode: candidate_proposal.function_code ?? null,
    subfunctionCode: candidate_proposal.subfunction_code ?? null,
    ownerJson: candidate_proposal.owner_json ?? null,
    tags: candidate_proposal.tags ?? null,
    thresholdJson: candidate_proposal.threshold_json ?? null,
    supersedesVersionUid: null,
    formulaAstCanonicalJson: candidate_proposal.formula_ast,  // ← AST-A NEW FIELD
  },
  variableBindings: candidate_proposal.variable_bindings.map(b => ({...})),
  filterClauses: candidate_proposal.filter_clauses.map(f => ({...})),
  computedDimensionRefs: candidate_proposal.computed_dimension_refs.map(d => ({...})),
  cert: {
    certifierSub: opts.certifierSub,
    certifierRoleAtAction: 'system',
    certifierEmail: opts.certifierEmail,
    panelRunUid: panelRunUid,                           // NF1 all-or-none: 6 fields populated together
    promptVersion: consensus_payload_json.prompt_version,
    modelIdentityJson: {
      models: consensus_payload_json.per_role_summary.map(r => ({...})),
    },
    inputHash: mapr.workbench_fingerprint_hash,
    samplingStatus: 'not_sampled',
    groundingCheckResult: consensus_payload_json.grounding_check_passed ? 'pass' : 'quarantined',
    policyVersion: activeMcfPolicyVersion,
    gateResultsJson: {
      m12_panel_run_uid: panelRunUid,
      m12_consensus_verdict_code: 'APPROVE_FOR_DRAFT',
      m12_grounding_check_passed: consensus_payload_json.grounding_check_passed,
      m9_structural_check_passed: true,
      m12_5_l_v1_passed: true,
      m12_5_l_v2_passed: true,
      m12_5_l_v3_passed: true,
    },
    advisoryVerdictsJson: [],
    override: null,
    actionCode: 'metric_create',
    fromStateCode: null,
    toStateCode: 'draft',
  },
  idempotencyKey: `mcf-m12-5/${panelRunUid}`,
  dryRun: false,
};
```

**Step 9 — TX A (M4-owned).** `const result = await certWriter.createMetricDraft(createInput)`. M4's internal tx writes 6 rows atomically (MC + MCV + N bindings + N filters + N computed_dims + 1 cert). M4 idempotency table records `committed`. On `unique_violation` on `idx_mcf_mc_mc_name_active` → catch + throw `DuplicateMcNameError(mcName, existingMcUid)`. On any other error → re-throw (M4 marks `rolled_back`; M12.5 surfaces as `MaterializationCertWriterError`).

**Step 10 — Compute 6 fixture hashes.** All 6 computations read from MCV substrate that TX A just stamped. Per §5.2 below, these happen inside TX B (same tx as the fixture INSERT) so reads + writes share lock scope.

**Step 11 — TX B (M12.5-owned).** Single tx: hash compute reads + fixture INSERT. INSERT shape:

```typescript
await tx.insert(metricSelfVerificationFixture).values({
  metricContractUid:                          result.metricContractUid,
  metricContractVersionUid:                   result.metricContractVersionUid,
  sectionAInputsJson:                         fixtureBody.section_a_inputs,
  sectionBExpectedOutputJson:                 fixtureBody.section_b_expected_output,
  sectionCResolverConfigJson:                 fixtureBody.section_c_resolver_config,
  formulaIntentHash:                          formulaIntentHash,                   // sha256:...
  variableBindingSetHash:                     variableBindingSetHash,              // sha256:...
  grainFilterTemporalDimensionSignatureHash:  gftdSignatureHash,                   // sha256:...
  selfVerificationFixtureHash:                fixtureBodyHash,                     // sha256:...
  boundPackageSignatureHash:                  boundPackageSigHash,                 // sha256:...
  hashAlgorithmVersion:                       'mcf-hash-v1',
  rationaleText:                              composeRationaleText(consensus_payload_json),  // ≥40 chars
  authoredByName:                             `mcf-m12-panel/${makerTranscriptUid}`,
  panelRunUid:                                panelRunUid,
});
```

On `unique_violation` on `uq_msvf_mcv_fixture_hash` → SELECT existing `fixture_uid` (idempotent path). Any other error → re-throw.

**Step 12 — TX C (M12.5-owned; pair commit).** Single tx wrapping both:
- (a) `const verifyResult = await verifier.verifyFixture(fixture_uid, { tx })`. M10 reads fixture, computes current package hash from MCV substrate (SAME computation M12.5 did at Step 10 — STALE CHECK passes), runs C-FX checks, executes formula, compares output, INSERTs `metric_self_verification_result` with verdict ∈ {`pass`, `fail`, `structural_reject`}. M10's own substrate idempotency catches `unique_violation` on `uq_msvr_fixture_version_pkg_hash` → SELECTs existing.
- (b) `await reservoir.markConsumedByPanel(intake_queue_uid, { tx })`. M11's CAS guard: SELECT-then-UPDATE-with-status-guard. If intake already not pending → throws `InvalidStatusTransitionError`. M12.5 catches + treats as `intake_transitioned: false` (no-op success).
- Commit. Pair-commit semantics: either both writes persist or neither.

**Step 13 — Return.** `MaterializationResult` shape:

```typescript
return {
  panel_run_uid: panelRunUid,
  metric_contract_uid: result.metricContractUid,
  metric_contract_version_uid: result.metricContractVersionUid,
  certification_record_id: result.certificationRecordId,
  fixture_uid: fixture_uid,
  verification_result_uid: verifyResult.verification_result_uid,
  verifier_verdict: verifyResult.verdict_code,
  intake_queue_uid: intake.intake_queue_uid,
  intake_transitioned: intakeTransitionedThisInvocation,  // false on idempotent retry
};
```

### 5.2 Transaction scope summary

| Step | Transaction | Purpose | Duration |
|---|---|---|---|
| 1-8 | NO TX | Read mapr/intake + validate + runtime policy lookup + compose input | ms |
| 9 | TX A (M4-owned) | Atomic INSERT of MC + MCV (with AST) + bindings + filters + computed_dims + cert | ms |
| 10-11 | TX B (M12.5-owned) | Read MCV substrate + compute 6 hashes + INSERT fixture | ms |
| 12 | TX C (M12.5-owned) | Pair commit: verifier_result + intake transition | ms to seconds (verifier formula execution time) |
| 13 | NO TX | Return | n/a |

**Three short TXs match the M12 pattern.** No long-lived TX. No outer TX wrapping the three (would require nesting M4's internal tx or refactoring M4 — neither acceptable per §5.3 below).

### 5.3 Why three short TXs (not one outer TX)

M4's `createMetricDraft` opens its own tx via `this.db.transaction(...)`. Embedding it inside an M12.5 outer tx would require either:
- Calling M4's PRIVATE `createMetricDraftInTx(tx, ...)` directly — bypassing M4's idempotency claim acquire / mark-committed-in-tx protocol, breaking M4's contract
- Refactoring M4 to accept an external tx — out of M12.5 scope; risks regression in M4 cert writer tests

The 3-TX pattern matches M12's pattern (validate / atomic substrate / intake transition) and is the correct grain for a service that composes other services that own their own transactions.

### 5.4 Error semantics summary

| Failure mode | Substrate effect | Intake status | Return |
|---|---|---|---|
| L-V1 / L-V2 / L-V3 fails | None (no writes happened) | unchanged | throw specific error; no TX opened |
| Step 7 framework_policy lookup returns 0 rows | None | unchanged | throw `FrameworkPolicyMissingError` |
| TX A fails (cert writer error / NF1 violation / framework_policy inactive / drizzle error) | M4 tx rolls back atomically; M4 idempotency table records `rolled_back` | unchanged | throw `MaterializationCertWriterError` |
| TX A `unique_violation` on `idx_mcf_mc_mc_name_active` (D-M12.5-MC-NAME-IDEMPOTENCY) | None | unchanged | throw `DuplicateMcNameError(mcName, existingMcUid)` |
| TX A AST guard fires (`InvalidAstError` from FormulaCanonicalizationService at Step 10) | TX A succeeded; TX B fails before INSERT | unchanged | throw `InvalidAstError` — indicates AST-A amendment did not stamp the AST correctly (impossible in valid flow; integration spec guards against) |
| TX B fails (fixture INSERT error other than UNIQUE) | TX B rolls back the 1 fixture INSERT; MC + cert from TX A persist | unchanged | re-throw |
| TX C verifier fails (formula execution error / M10 internal error) | TX C rolls back verifier_result + intake transition; MC + cert + fixture from TX A+B persist | unchanged (pending) | re-throw |
| TX C intake transition fails (`InvalidStatusTransitionError` — already consumed by concurrent retry) | TX C rolls back verifier_result too; but verifier had its own idempotency catch which already SELECTed existing UID | as observed | catch + treat as `intake_transitioned: false`; return MaterializationResult |
| Process crash between TXs | After last completed TX | as observed | Retry → resumes from first incomplete step via idempotency catches |
| Successful flow | MC + MCV + bindings + filters + computed_dims + cert + fixture + verifier_result persisted; intake transitioned | `consumed_by_panel` | `MaterializationResult` |

---

## 6. M4 amendment per D-M12.5-AST (AST-A) — exact surface change

### 6.1 Surface change

**`bc-core/src/registry/mcf/mcf-cert-writer.service.ts`** — TWO changes:

**Change 1: extend `CreateMetricDraftInput.metricContractVersion` interface** (currently at lines `163-173`):

```typescript
metricContractVersion: {
  versionCode: string;
  versionSeq: number;
  descriptionText?: string | null;
  functionCode?: string | null;
  subfunctionCode?: string | null;
  ownerJson?: Record<string, unknown> | null;
  tags?: string[] | null;
  thresholdJson?: Record<string, unknown> | null;
  supersedesVersionUid?: string | null;
  /**
   * Optional canonical AST stamped into `mcf.metric_contract_version.formula_ast_canonical_json`
   * during TX A. When omitted, the substrate-level DDL default applies (placeholder JSON).
   * Per D-M12.5-AST / AST-A: M12.5 materialization MUST supply this from
   * `consensus_payload_json.candidate_proposal.formula_ast` so that subsequent fixture hash
   * computation via FormulaCanonicalizationService does NOT throw InvalidAstError on placeholder.
   * Back-compatible: existing callers that omit this field get the placeholder default
   * (unchanged behavior).
   */
  formulaAstCanonicalJson?: unknown;
};
```

**Change 2: extend `insertMcv()` body** (currently at lines `737-755`):

```typescript
private async insertMcv(tx: Tx, mcUid: string, input: CreateMetricDraftInput): Promise<string> {
  const [mcv] = await tx
    .insert(metricContractVersion)
    .values({
      metricContractUid: mcUid,
      versionCode: input.metricContractVersion.versionCode,
      versionSeq: input.metricContractVersion.versionSeq,
      descriptionText: input.metricContractVersion.descriptionText ?? null,
      functionCode: input.metricContractVersion.functionCode ?? null,
      subfunctionCode: input.metricContractVersion.subfunctionCode ?? null,
      ownerJson: input.metricContractVersion.ownerJson ?? null,
      tags: input.metricContractVersion.tags ?? null,
      thresholdJson: input.metricContractVersion.thresholdJson ?? null,
      supersedesVersionUid: input.metricContractVersion.supersedesVersionUid ?? null,
      governanceStateCode: 'draft',
      // AST-A — D-M12.5-AST: pass through if supplied; else substrate DDL default applies
      ...(input.metricContractVersion.formulaAstCanonicalJson !== undefined
        ? { formulaAstCanonicalJson: input.metricContractVersion.formulaAstCanonicalJson }
        : {}),
    })
    .returning({ metricContractVersionUid: metricContractVersion.metricContractVersionUid });
  return mcv.metricContractVersionUid;
}
```

**That's the entire M4 amendment.** Two changes: one interface field addition (optional) + one conditional spread in `insertMcv()`. ~5 lines of code total.

### 6.2 Back-compatibility guarantee

- The new field is **optional** — existing callers (M4 unit tests, M4 integration spec helpers) that omit it continue to get the DDL placeholder default. Behavior unchanged.
- M4's unit + integration tests stay green.
- The `seedNonPlaceholderAst` helper in `mcf-cert-writer.service.integration.spec.ts:198-204` becomes unnecessary. M12.5 impl PR removes the helper and replaces existing call sites with the new input field.

### 6.3 Files M12.5 impl PR changes for AST-A

| File | Change |
|---|---|
| `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` | Add optional `formulaAstCanonicalJson` field to `CreateMetricDraftInput.metricContractVersion`; conditional spread in `insertMcv()` |
| `bc-core/src/registry/mcf/mcf-cert-writer.service.spec.ts` | Add 1-2 unit tests covering: (a) field supplied → MCV gets real AST; (b) field omitted → MCV gets placeholder default (back-compat assertion) |
| `bc-core/src/registry/mcf/mcf-cert-writer.service.integration.spec.ts` | Remove `seedNonPlaceholderAst` helper at `:198-204`; replace each call site with the new input field; lines `:226-229` deprecation comment removed |

### 6.4 What AST-A is NOT

- NOT a new method on M4 (avoided AST-B / `stampFormulaAst`)
- NOT a substrate change (no DDL, no schema change)
- NOT a public-API behavior change (existing callers see no difference)
- NOT a coordination layer (no new tx boundary)

---

## 7. DDL apply plan per D-M12.5-MC-NAME-IDEMPOTENCY (MC-NAME-A)

### 7.1 Forward DDL

**File:** `bc-core/docker/redesign/<NN>-mcf-m12-5-mc-name-unique-index.sql` (NN = next available number per existing convention; current highest in `docker/redesign/` will be discovered at impl PR time).

**Content:**

```sql
-- MCF M12.5 — Materialization + Legacy Bridge
-- D-M12.5-MC-NAME-IDEMPOTENCY / MC-NAME-A
-- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md (<this commit>)
--
-- Adds partial unique index on mcf.metric_contract.mc_name for non-archived rows.
-- Mirrors existing idx_mcf_mc_identity_active partial-index pattern.
-- Substrate-level guard for concurrent M12.5 materialization producing duplicate mc_name.
-- M12.5 service catches unique_violation → DuplicateMcNameError.

CREATE UNIQUE INDEX IF NOT EXISTS idx_mcf_mc_mc_name_active
  ON mcf.metric_contract(mc_name)
  WHERE archived_at IS NULL;

COMMENT ON INDEX mcf.idx_mcf_mc_mc_name_active IS
  'Partial unique index on mc_name for active (non-archived) MCs. Per M12.5 DBCP D-M12.5-MC-NAME-IDEMPOTENCY MC-NAME-A. Mirrors idx_mcf_mc_identity_active pattern.';
```

**Apply expected duration:** sub-30 seconds (live MC count is 0; partial-index build over empty table is trivial).

**Apply blast radius:** zero — no existing data; no concurrent writers; no impact on existing indexes; no impact on `idx_mcf_mc_identity_active` (different column set + non-overlapping predicate).

### 7.2 Rollback DDL

**File:** `bc-core/docker/redesign/<NN>R-mcf-m12-5-mc-name-unique-index-rollback.sql` (per existing repo rollback-file convention).

**Content:**

```sql
-- Rollback for MCF M12.5 D-M12.5-MC-NAME-IDEMPOTENCY MC-NAME-A
-- Reverses idx_mcf_mc_mc_name_active partial unique index addition.

DROP INDEX IF EXISTS mcf.idx_mcf_mc_mc_name_active;
```

**Rollback duration:** sub-1 second.

**Rollback blast radius:** zero — removing an index that has been created on an empty table; no data loss.

### 7.3 Dry-run verifier plan

**Script:** `bc-core/scripts/mcf-m12-5-dry-run.mjs` (mirrors M11 / M9 / M5 / M4 / M3 dry-run pattern).

**Pre-conditions** (assertions before any planned-SQL execution):

| # | Probe | Expected |
|---|---|---|
| 1 | `mcf.metric_contract` exists | TRUE |
| 2 | `idx_mcf_mc_mc_name_active` does NOT yet exist on `mcf.metric_contract` | TRUE (first apply); SKIP-with-note (subsequent — DDL is idempotent via `IF NOT EXISTS`) |
| 3 | `mcf.metric_contract` rowcount | 0 (substrate dormant) |
| 4 | `contract.framework_policy WHERE policy_uid='mcf_v1' AND effective_to IS NULL` exists | TRUE (apply-time requirement; M12.5 service depends on this) |
| 5 | `mcf.workspace_tool_allowlist` rowcount | irrelevant for DDL apply; sanity-check only |
| 6 | bc-core main SHA | recorded for evidence |
| 7 | bc-docs-v3 main SHA | recorded for evidence |
| 8 | DDL file sha256 | computed + recorded |
| 9 | Rollback file sha256 | computed + recorded |

**Planned-SQL hash output:** sha256 of the DDL file bytes; written to `scripts/audit-output/mcf-m12-5-dry-run-<timestamp>.planned-sql.sha256.txt`.

**Pre-condition output:** JSONL to `scripts/audit-output/mcf-m12-5-dry-run-<timestamp>.precondition.jsonl` — one entry per probe with `{probe_name, expected, actual, status: PASS|FAIL|SKIP, at: <ISO>}`.

**Summary output:** markdown to `scripts/audit-output/mcf-m12-5-dry-run-<timestamp>.summary.md` — verdict + table of probe results + planned-SQL hash + apply instructions.

**Stop-on-fail:** if any probe FAILs (other than #2 SKIP-allowed condition), dry-run aborts with non-zero exit; operator inspects + resolves before apply.

### 7.4 Post-apply verifier plan

**Script:** `bc-core/scripts/mcf-m12-5-post-apply.mjs` (mirrors M11 / M9 / M5 / M4 / M3 post-apply pattern).

**Post-conditions** (assertions after `psql -f <DDL file>`):

| # | Probe | Expected |
|---|---|---|
| 1 | `idx_mcf_mc_mc_name_active` exists on `mcf.metric_contract` | TRUE |
| 2 | Index is UNIQUE | TRUE (per `pg_index.indisunique`) |
| 3 | Index has WHERE clause `WHERE archived_at IS NULL` | TRUE (per `pg_get_indexdef(.., true)`) |
| 4 | Index covers exactly column `mc_name` | TRUE (per `pg_index.indkey` → `mc_name`) |
| 5 | `mcf.metric_contract` rowcount | 0 (no rows added by DDL apply) |
| 6 | `contract.panel_output_record` rowcount | 24 (BCF preserved) |
| 7 | `contract.authoring_panel_rejection_log` rowcount | 1 (BCF preserved) |
| 8 | All 17 mcf.* tables rowcount | 0 |
| 9 | Index COMMENT matches DBCP citation | TRUE |
| 10 | DDL file sha256 matches the dry-run-recorded hash | TRUE |
| 11 | Existing indexes preserved | 5 indexes pre-apply + 1 new = 6 indexes total on `mcf.metric_contract` |
| 12 | **Crash-safe duplicate-detection probe** (per patch M-3 — single transaction wraps INSERT + duplicate test; ROLLBACK undoes both regardless of crash): `BEGIN; INSERT mc_name='m12_5_post_apply_test' (succeeds); INSERT same mc_name (expected unique_violation on idx_mcf_mc_mc_name_active); ROLLBACK;` — verifies the partial unique index rejects duplicates without leaving phantom rows on script crash | TRUE (both INSERTs behave as expected; ROLLBACK leaves substrate untouched) |
| 13 | Post-rollback assertion: `mcf.metric_contract` rowcount returns to 0 (no phantom rows from probe 12) | TRUE |
| 14 | bc-core / bc-docs-v3 SHAs recorded for evidence | TRUE |

**Evidence output:** JSONL + summary markdown to `scripts/audit-output/mcf-m12-5-post-apply-<timestamp>.evidence.jsonl` + `.summary.md`.

**Stop-on-fail:** if any probe FAILs, operator must rollback (apply `<NN>R-...-rollback.sql`) and investigate.

**Crash-safe pattern (per patch M-3).** Probes 12-13 use the SAVEPOINT-style `BEGIN ... ROLLBACK` pattern (mirroring the M5 / M9 / M11 integration spec convention). The wrapping transaction guarantees that no test row persists in production substrate regardless of where the script crashes — the ROLLBACK undoes the INSERT atomically. The original (pre-patch) `INSERT + procedural DELETE` design had a phantom-row risk if the script crashed between INSERT and DELETE; the transaction wrapper closes that gap by construction.

Concrete probe-12 SQL:

```sql
BEGIN;

-- Sub-probe 12a: INSERT first row succeeds
INSERT INTO mcf.metric_contract (mc_name, grain_entity_id, temporal_gate_shape_code)
VALUES ('m12_5_post_apply_test', gen_random_uuid(), 'instantaneous');
-- assert: INSERT succeeded (verifier captures rowcount = 1)

-- Sub-probe 12b: INSERT duplicate raises unique_violation
DO $$
BEGIN
  INSERT INTO mcf.metric_contract (mc_name, grain_entity_id, temporal_gate_shape_code)
  VALUES ('m12_5_post_apply_test', gen_random_uuid(), 'instantaneous');
  RAISE EXCEPTION 'M12.5 MC-NAME-A post-apply probe 12 FAILED: expected unique_violation on idx_mcf_mc_mc_name_active, got success';
EXCEPTION WHEN unique_violation THEN
  -- expected behavior; verifier records sub-probe 12b PASS
  NULL;
END $$;

ROLLBACK;  -- atomic undo; no phantom row regardless of crash
```

Then probe 13 separately confirms `SELECT count(*) FROM mcf.metric_contract` returns `0` post-ROLLBACK.

### 7.5 Apply sequence (operator-driven)

1. Operator runs `node bc-core/scripts/mcf-m12-5-dry-run.mjs` → reviews summary.md → confirms PASS.
2. Operator records dry-run planned-SQL hash.
3. Operator runs `AWS_PROFILE=barecount psql ${DATABASE_URL} -f bc-core/docker/redesign/<NN>-mcf-m12-5-mc-name-unique-index.sql`.
4. Operator runs `node bc-core/scripts/mcf-m12-5-post-apply.mjs` → reviews evidence + summary.md → confirms 14/14 PASS.
5. Operator commits the DDL file + dry-run + post-apply artifacts to bc-core (separate PR from impl PR per existing M11 / M9 pattern).

---

## 8. Three-layer pre-write validation (L-V1 / L-V2 / L-V3)

### 8.1 L-V1 — Eligibility precondition

Four assertions executed in M12.5 service Steps 1-4. All BEFORE TX A opens:

| # | Assertion | Failure |
|---|---|---|
| L-V1a | `consensus_payload_json.verdict_code === 'APPROVE_FOR_DRAFT'` | `MaterializationPreconditionError("not APPROVE_FOR_DRAFT verdict")` |
| L-V1b | `candidate_proposal.proposed_fixtures.length >= 1` | `MaterializationPreconditionError("no proposed fixtures")` |
| L-V1c | `candidate_proposal.proposed_fixtures[0].checker_c_fx_result.passed === true` | `MaterializationPreconditionError("Checker C-FX failed at panel time")` |
| L-V1d | intake.status_code === 'pending' (re-asserts at Step 3) | `MaterializationPreconditionError("intake already consumed/rejected/superseded")` |

### 8.2 L-V2 — AJV schema validation

AJV (`ajv` package — already in bc-core dependencies per M12 closeout) validates `consensus_payload_json` against `bc-core/src/registry/mcf/panel-payload.schema.json` (HA-7 single-source schema literal shared with M12 panel service).

Failure → `ConsensusPayloadValidationError(ajvErrors)`. Log full AJV error list.

**HA-7 enforcement (per patch L-5 — rewritten).** M12.5 imports the schema literal `panel-payload.schema.json` from the SAME file path as the M12 panel service (`bc-core/src/registry/mcf/panel-payload.schema.json` — single-source-of-truth). The unit test imports the schema via BOTH services' resolved import paths, computes sha256 at test time on both imports, and asserts byte-equality. **No external "expected hash" is recorded** — the assertion is path identity + computed-at-test-time byte-equality. If a future PR accidentally creates a divergent copy at a different path and either service's import resolves to a different file, the byte-equality assertion fails immediately.

### 8.3 L-V3 — M9 structural re-check (defense-in-depth)

Build a `FixtureContext` IN-MEMORY from `candidate_proposal` (cannot read from MCV substrate yet — MCV gets created at TX A). Build `fixtureBody` from `proposed_fixtures[0]`. Call `FixtureStructuralCheckService.runStructuralChecks(context, fixtureBody)`.

If `result.passed === false` → `FixtureStructuralCheckFailedError(result.defects)`.

**Placeholder uuids (per patch L-3).** `FixtureContext` requires `mcvUid: string` + `metricContractUid: string` on its interface — but at L-V3 time, no MCV exists yet (TX A hasn't opened). M12.5 supplies placeholder uuids (recommend `'00000000-0000-0000-0000-000000000000'` for both). The M9 `runStructuralChecks(context, body)` function does NOT depend on these uuid values for any of the C-FX-1..C-FX-11 check predicates — they are metadata-only fields used by `loadFixtureContext` callers that hydrate context from substrate. Confirmed by inspecting M9 source: uuids appear only on returned defect payloads (forensic identifier) and never as inputs to structural checks.

**Purpose:** even though the Checker model claimed `c_fx_result.passed === true` at panel time, M12.5 re-runs the structural check on the platform side. Catches Maker-Checker drift / fabricated Checker verdicts. Defense-in-depth alongside L-V1c.

---

## 9. Fixture hash computation contract (6 columns + 1 upstream input)

`mcf.metric_self_verification_fixture` has 6 NOT-NULL hash-bearing columns. M12.5 computes each from MCV substrate (which TX A just stamped, including the real AST per AST-A):

| Fixture row column | Computed by | Input dependency | Service file |
|---|---|---|---|
| `formula_intent_hash` | `FormulaCanonicalizationService.computeFormulaIntentHash(mcvUid, deps)` | Reads MCV `formula_ast_canonical_json` — REQUIRES non-placeholder AST per AST-A | `formula-canonicalization.service.ts:631-642` |
| `variable_binding_set_hash` | `FormulaCanonicalizationService.computeVariableBindingSetHash(mcvUid, deps)` | Reads `mcf.metric_variable_binding` rows written by TX A; sorted by `variable_role_code` | `formula-canonicalization.service.ts:652-681` |
| `grain_filter_temporal_dimension_signature_hash` | `PackageSignatureService.computeGrainFilterTemporalDimensionSignatureHash(mcvUid, {filterSetHash}, deps)` | Requires `filterSetHash` precomputed; reads parent MC grain + temporal gate | `package-signature.service.ts:214-230` |
| `bound_package_signature_hash` | `PackageSignatureService.computePackageSignatureHash(mcvUid, {formulaIntentHash, variableBindingSetHash, filterSetHash}, deps)` | Composes 3 contributing hashes + reads parent MC grain + temporal gate. **STAMPS THE VALUE M10's STALE CHECK WILL RECOMPUTE AT VERIFY TIME** — both M12.5 and M10 compute from the SAME MCV substrate; deterministic equality (R-M12.5-1 RESOLVED). | `package-signature.service.ts:240-256` |
| `self_verification_fixture_hash` | `PackageSignatureService.computeSelfVerificationFixtureHash(fixtureBody)` | Pure function — fixture body only; no DB reads | `package-signature.service.ts:291-302` |
| `hash_algorithm_version` | Constant `'mcf-hash-v1'` | Per M7/M8 D-M9-A1 forever-lock; satisfies substrate CHECK `msvf_hash_algorithm_version_chk: ~ '^mcf-[a-z-]+-v[0-9]+$'` | — |

**Upstream input not stored on fixture:** `filter_set_hash` (via `FormulaCanonicalizationService.computeFilterSetHash(mcvUid, deps)` at `formula-canonicalization.service.ts:692-720`). M12.5 computes it once and feeds it into `computeGrainFilterTemporalDimensionSignatureHash` AND `computePackageSignatureHash`.

**Order of computation in M12.5 service (Step 10):**

```typescript
// Inside TX B
const formulaIntentHash       = await formulaCanon.computeFormulaIntentHash(mcvUid, { tx });
const variableBindingSetHash  = await formulaCanon.computeVariableBindingSetHash(mcvUid, { tx });
const filterSetHash           = await formulaCanon.computeFilterSetHash(mcvUid, { tx });
const gftdSignatureHash       = await packageSig.computeGrainFilterTemporalDimensionSignatureHash(
                                  mcvUid, { filterSetHash }, { tx });
const boundPackageSigHash     = await packageSig.computePackageSignatureHash(
                                  mcvUid,
                                  { formulaIntentHash, variableBindingSetHash, filterSetHash },
                                  { tx });
const fixtureBodyHash         = packageSig.computeSelfVerificationFixtureHash(fixtureBody);
```

Then the INSERT at Step 11 supplies all 6 + `hash_algorithm_version='mcf-hash-v1'`.

---

## 10. Service interface

### 10.1 Class shape (TypeScript)

```typescript
// bc-core/src/registry/mcf/metric-authoring-materialization.service.ts

import { Inject, Injectable } from '@nestjs/common';
import type { PostgresJsDatabase } from 'drizzle-orm/postgres-js';
import { CONTROL_PLANE_DB } from '../../database/db-tokens';
import { McfCertWriterService, type CreateMetricDraftInput } from './mcf-cert-writer.service';
import { MetricSelfVerificationService } from './metric-self-verification.service';
import { FixtureStructuralCheckService } from './fixture-structural-check.service';
import { FormulaCanonicalizationService } from './formula-canonicalization.service';
import { PackageSignatureService } from './package-signature.service';
import { ReservoirIngestionService } from './reservoir-ingestion.service';

// ─── Errors ────────────────────────────────────────────────────────────────

export class MaterializationPreconditionError extends Error { ... }
export class ConsensusPayloadValidationError extends Error { ... }
export class FixtureStructuralCheckFailedError extends Error { ... }
export class FrameworkPolicyMissingError extends Error { ... }
/** Per patch M-1: strict fail-fast when >1 active mcf_v1 framework_policy row exists. */
export class MultipleActivePoliciesError extends Error {
  constructor(public readonly policyVersions: string[]) {
    super(`MCF M12.5: multiple active mcf_v1 framework_policy rows (${policyVersions.join(', ')}); operator must expire the stale row before M12.5 proceeds`);
  }
}
export class DuplicateMcNameError extends Error {
  constructor(public readonly mcName: string, public readonly existingMcUid?: string) { ... }
}
export class MaterializationCertWriterError extends Error { ... }
export class IntakeRowNotFoundError extends Error { ... }

// ─── Input + Result ────────────────────────────────────────────────────────

export interface RunMaterializationOpts {
  certifierSub: string;
  certifierEmail?: string;
  /** Optional override for `authored_by_name` on the fixture row */
  authoredByName?: string;
  /** Optional override for `rationaleText` (≥40 chars) on the fixture row */
  rationaleText?: string;
}

export interface MaterializationResult {
  panel_run_uid: string;
  metric_contract_uid: string;
  metric_contract_version_uid: string;
  certification_record_id: string;
  fixture_uid: string;
  verification_result_uid: string;
  verifier_verdict: 'pass' | 'fail' | 'structural_reject';
  intake_queue_uid: string;
  intake_transitioned: boolean;
}

// ─── Service ───────────────────────────────────────────────────────────────

@Injectable()
export class MetricAuthoringMaterializationService {
  constructor(
    @Inject(CONTROL_PLANE_DB) private readonly db: PostgresJsDatabase<...>,
    private readonly certWriter: McfCertWriterService,
    private readonly verifier: MetricSelfVerificationService,
    private readonly structuralCheck: FixtureStructuralCheckService,
    private readonly formulaCanon: FormulaCanonicalizationService,
    private readonly packageSig: PackageSignatureService,
    private readonly reservoir: ReservoirIngestionService,
  ) {}

  async runMaterialization(
    panelRunUid: string,
    opts: RunMaterializationOpts,
  ): Promise<MaterializationResult> {
    // Steps 1-13 per §5
  }

  // Private helpers (one per pure unit; max-lines-per-function ≤ 60 per QA shift-left)
  private async readMaprAndValidate(panelRunUid: string): Promise<...> { ... }
  private async readIntakeAndValidate(intakeQueueUid: string): Promise<...> { ... }
  private validateConsensusPayloadSchema(payload: unknown): void { ... }
  private runStructuralRecheckInMemory(candidateProposal: ..., fixtureBody: ...): void { ... }
  private async lookupActiveMcfPolicyVersion(): Promise<string> { ... }
  private composeCreateMetricDraftInput(...): CreateMetricDraftInput { ... }
  private composeRationaleText(consensus: ...): string { ... }
  private async insertFixtureInTx(tx: Tx, ..., hashes: {...}): Promise<string> { ... }
  private async runVerifierAndTransitionIntake(tx: Tx, ...): Promise<...> { ... }
}
```

### 10.2 Constructor injection

All 6 collaborators are existing services from M4 / M7-M8 / M9 / M10 / M11. M12.5 wires them via NestJS DI in the existing MCF module. No new DI tokens.

### 10.3 No new REST / MCP endpoint

Per D-M12.5-7, M12.5 ships ZERO REST endpoints. Per §0 PR-2 addendum, operator invocation in v1 is: (a) preflight verification via `scripts/mcf-m12-5-preflight.mjs` (read-only, 5 substrate probes), (b) service invocation through NestJS DI (the service is registered in the MCF module). NestJS-bootstrap direct-invocation one-shot CLI is deferred to a follow-up PR.

---

## 11. Idempotency + collision-detection surfaces  *(split per patch L-1)*

### 11.1 Idempotency surfaces (substrate-provided per step) — "second call with same input returns cached result"

| Step | Idempotency surface | Key | Re-invocation behavior |
|---|---|---|---|
| Step 9 (TX A) | `mcf.metric_cert_writer_idempotency` PK | `idempotencyKey = 'mcf-m12-5/' + panel_run_uid` | M4 returns cached `{metricContractUid, metricContractVersionUid, certificationRecordId}` from row's `result_json`; pending → poll per M4 protocol; rolled_back → reclaim. AST stamping happens inside this same TX (AST-A); no separate stamping TX |
| Step 11 (TX B) | `mcf.metric_self_verification_fixture` UNIQUE `(metric_contract_version_uid, self_verification_fixture_hash)` (`uq_msvf_mcv_fixture_hash`) | `(mcv_uid, sha256(canonical(section_a+b+c)))` | Re-INSERT catches `unique_violation` → SELECT existing `fixture_uid`; idempotent |
| Step 12a (verifier) | M10's built-in idempotent insert on UNIQUE `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` (`uq_msvr_fixture_version_pkg_hash`) | M10-owned | M10 already catches `unique_violation` + SELECTs existing — no M12.5 code change needed |
| Step 12b (intake) | M11 `markConsumedByPanel` CAS guard `WHERE intake_queue_uid = ${uid} AND status_code = 'pending'` | `intake_queue_uid` | If already `consumed_by_panel`, throws `InvalidStatusTransitionError`; M12.5 catches + treats as "already done" (`intake_transitioned: false`) |

**Concurrent invocation safety (same `panel_run_uid`).** Two operators triggering M12.5 for the same `panel_run_uid` race on TX A (M4 idempotency claim polling — first writer wins; second waits + returns cached). TX B races on substrate UNIQUE. TX C step (a) races on M10 substrate UNIQUE. TX C step (b) races on M11 CAS.

**Crash recovery.** Process crash between TXs leaves committed work persisted + uncommitted work rolled back by Postgres. Retry resumes from the first incomplete step.

**Inherited M11 quirk (per patch L-4).** M11's `transitionStatus` private helper (`reservoir-ingestion.service.ts:290-314`) uses a SELECT-then-UPDATE pattern. The UPDATE has the CAS guard `WHERE intake_queue_uid = ${uid} AND status_code = ${expectedCurrent}`, but the M11 service does NOT inspect the UPDATE's affected-row count. If a concurrent tx transitioned the intake row between M11's SELECT (which saw 'pending') and M11's UPDATE (which now matches 0 rows because status moved to `consumed_by_panel`), M11 silently returns success without raising. M12.5 then reports `intake_transitioned: true` even though the actual transition was performed by the concurrent writer. **Practical impact: benign** — the intake IS in `consumed_by_panel` state at TX C commit time; only M12.5's reported `intake_transitioned` boolean is overly optimistic. Fixing the M11 quirk requires an M11 amendment (out of M12.5 scope). M12.5 inherits the behavior.

### 11.2 Collision detection (NOT idempotency) — "second call with DIFFERENT input but conflicting identity"

`mc_name` partial unique index is **collision detection, not idempotency**. The semantic distinction: idempotency means "same input → same cached output"; collision detection means "different inputs with conflicting identity → error". Two DIFFERENT panels approving the SAME `mc_name` carry different `panel_run_uid` values, so M4's idempotency table (keyed on `'mcf-m12-5/' + panel_run_uid`) does NOT see them as duplicates — both M4 invocations proceed to INSERT. The substrate-level guard catches the conflict.

| Collision | Detection surface | Trigger | Behavior |
|---|---|---|---|
| Two different panels approve same `mc_name` (different `panel_run_uid` values) | `idx_mcf_mc_mc_name_active` partial unique index per D-M12.5-MC-NAME-IDEMPOTENCY MC-NAME-A (added by PR-1 DDL gate) | Second TX A INSERT raises `unique_violation` (first INSERT already committed an MC with the same `mc_name` AND `archived_at IS NULL`) | M12.5 catches + throws `DuplicateMcNameError(mcName, existingMcUid)` → operator inspects + decides supersession path (M15 territory) |

---

## 12. Legacy bridge contract

### 12.1 `Sunset` HTTP header on legacy POST

**File:** `bc-core/src/registry/metric-definition.controller.ts` (currently at `:15-:47`).

**Change:**

```typescript
import { Controller, Get, Post, Patch, Param, Query, Body, Res, Header } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Controller('metric-catalog/definitions')
@PlatformOnly()
export class MetricDefinitionController {
  private readonly sunsetDate: string | null;

  constructor(
    private readonly service: MetricDefinitionService,
    private readonly config: ConfigService,
  ) {
    this.sunsetDate = this.config.get<string>('BCCORE_MCF_LEGACY_SUNSET_DATE') ?? null;
  }

  @Post()
  @ApiOperation({ summary: 'Create a single metric definition (auto-queues AI enrichment) — DEPRECATED per MCF M12.5; use MCF intake + panel + materialization' })
  create(@Body() body: {...}, @Res({ passthrough: true }) res: Response) {
    if (this.sunsetDate) {
      res.setHeader('Sunset', this.sunsetDate);
    }
    return this.service.create(body);
  }

  @Post('upload')
  @ApiOperation({ summary: 'Bulk create from CSV data. DEPRECATED per MCF M12.5; use MCF intake + panel + materialization' })
  bulkCreate(@Body() body: {...}, @Res({ passthrough: true }) res: Response) {
    if (this.sunsetDate) {
      res.setHeader('Sunset', this.sunsetDate);
    }
    return this.service.bulkCreate(body.entries, { enrichAfterCreate: body.enrichAfterCreate });
  }
}
```

**Operator procurement.** Operator MUST set env var `BCCORE_MCF_LEGACY_SUNSET_DATE` to an RFC 9745 date (e.g. `'Wed, 31 Dec 2026 23:59:59 GMT'`) before deployment. If unset, header is OMITTED (failsafe).

**DBCP requires** the operator to commit a concrete Sunset date before the M12.5 implementation PR merges. Default in `bc-core/.env.example` is empty + comment `# BCCORE_MCF_LEGACY_SUNSET_DATE=Wed, 31 Dec 2026 23:59:59 GMT  # Set per M12.5 closeout`.

### 12.2 Read-fallback policy

**New chapter:** `bc-docs-v3/docs/operating-model/mcf-legacy-bridge.md`.

**Locked text:**

> **MCF-legacy MC read fallback (effective from M12.5 closeout):**
>
> 1. When a read consumer asks for "MC by `metric_code` X", the canonical resolution order is:
>    - **MCF authority** — `SELECT mc.metric_contract_uid FROM mcf.metric_contract mc WHERE mc.mc_name = ${metric_code}` AND there exists an `mcf.metric_contract_version mcv` row with `mcv.metric_contract_uid = mc.metric_contract_uid` AND `mcv.governance_state_code IN ('draft','review','approved','active')` (i.e. not `superseded`)
>    - **Legacy fallback** — `SELECT md.metric_definition_id FROM metric.metric_definition md WHERE md.metric_name = ${metric_code}` only if MCF returned no rows
> 2. If both authorities return a row for the same `metric_code`, **MCF wins**. Readers SHOULD log a `legacy_mc_shadowed_by_mcf` warning event for operator awareness; readers MUST return the MCF row.
> 3. New read services authored after M12.5 closeout MUST implement this fallback. Existing read services may continue to read legacy-only until their respective migration gates (M18+).
> 4. The `Sunset` header on `POST /api/metric-catalog/definitions` signals the legacy write path's deprecation date; the read fallback policy stays in effect until ALL read services have migrated (no fixed date — driven by tenant runtime migration).

### 12.3 Operator runbook update

**File:** `bc-docs-v3/docs/onboarding/metric-registration.md` (existing chapter).

**Change:** add a new section after the existing intro:

> ## MCF M12.5 — new authoring path
>
> Effective from MCF M12.5 closeout (`<sha>`), new metric authoring follows the MCF intake + panel + materialization sequence:
>
> 1. **M11 intake** — operator submits candidate via `ReservoirIngestionService.ingestOperatorDirectSubmission(...)` (CLI), or candidates flow in from seed_metrics / metric_definition adapters.
> 2. **M12 panel** — three-model panel (Maker / Checker / Moderator) produces a consensus proposal; operator reviews via M16 audit UI (when shipped).
> 3. **M12.5 materialization** — per §0 PR-2 addendum: operator first runs `node bc-core/scripts/mcf-m12-5-preflight.mjs --panel-run-uid <uuid>` (read-only preflight; 5 substrate probes), then invokes `MetricAuthoringMaterializationService.runMaterialization(panelRunUid, opts)` via NestJS DI to materialize an APPROVE_FOR_DRAFT panel into MCF substrate.
>
> The legacy `POST /api/metric-catalog/definitions` endpoint remains LIVE during the Sunset window (per `BCCORE_MCF_LEGACY_SUNSET_DATE`) for backward compatibility, but carries a `Sunset` HTTP header. **New authoring should NOT use the legacy endpoint.**
>
> Tenant runtime migration (boundary/metric.service.ts, ReadinessLedgerService, chain-status.service.ts) ships in M18+; until then, runtime evaluation continues against the legacy `metric.metric_definition` corpus.

### 12.4 CLAUDE.md note

**File:** `barecount-devhub/CLAUDE.md` MCF substrate section.

**Change:** add one bullet:

> - **MCF M12.5 — materialization + legacy bridge** — `MetricAuthoringMaterializationService.runMaterialization(panelRunUid, opts)` converts APPROVE_FOR_DRAFT panel proposals into draft MCF substrate (MC + MCV + bindings + filters + computed_dims + cert + fixture + verifier result). Legacy `POST /api/metric-catalog/definitions` carries `Sunset` header per `BCCORE_MCF_LEGACY_SUNSET_DATE`. Read-fallback policy: MCF wins when both authorities hold the same `metric_code`. See `bc-docs-v3/docs/operating-model/mcf-legacy-bridge.md` for the policy text. M13 PE-MC evaluator + M14 publication remain CLOSED until M12.5 closeout.

---

## 13. Hard assertions HA-1..HA-8

The verification harness is one composite integration test that runs `runMaterialization` against a synthetic mapr + intake row inside a SAVEPOINT, asserts the assertions, then sentinel-throws to rollback.

| # | Assertion | Primary enforcement | Test verification |
|---|---|---|---|
| **HA-1** | M12.5 service does NOT import `MetricDefinitionService` / `MetricDefinitionRepository` / any other legacy `metric.*` writer. M12.5 does NOT write to `metric.metric_definition` / `metric_knowledge` / `metric_binding` / `enrichment_job` | Source code import allowlist + ESLint rule | Static import-graph audit; integration test asserts post-run rowcount delta on `metric.metric_definition` / `metric_knowledge` / `metric_binding` == 0 |
| **HA-2** | M12.5 service DOES import `McfCertWriterService` and calls ONLY `createMetricDraft` (NOT `submitForReview` / `approveForActivation` / `activateMetric` / `supersedeMetric`) | Source code grep; unit test asserts the service module's source text contains exactly one call site to `certWriter.createMetricDraft` and zero call sites to the other 4 methods | Same |
| **HA-3** | M12.5 service does NOT write to `mcf.metric_publication_eligibility_result` / `mcf.metric_supersession` / `mcf.metric_contract_revision` | Service source has no INSERT into these tables | Integration test asserts 0-row delta on these 3 tables |
| **HA-4** | M12.5 service does NOT write to BCF (`contract.business_entity` / `contract.business_concept` / any `concept_registry.*` table) and does NOT write to `contract.panel_output_record` (only reads via mapr FK navigation if at all) | Source code structure | Integration test asserts BCF preserved exactly (24 + 1) post-test |
| **HA-5** | M12.5 service writes ONLY to: `mcf.metric_contract` (+1), `mcf.metric_contract_version` (+1), `mcf.metric_variable_binding` (+N), `mcf.metric_filter_clause` (+N), `mcf.metric_computed_dimension_ref` (+N), `mcf.certification_record` (+1), `mcf.metric_cert_writer_idempotency` (+1 status flip), `mcf.metric_self_verification_fixture` (+1), `mcf.metric_self_verification_result` (+1), `mcf.metric_authoring_intake_queue` (UPDATE only). NO other table is written | Service code structure | Integration test asserts post-run rowcount on every other `mcf.*` / `contract.*` / `metric.*` table == 0-row delta |
| **HA-6** | The MCV created by M12.5 has `governance_state_code='draft'` (NOT `review`, `approved`, `active`, or `superseded`). M12.5 does NOT advance the lifecycle state | Already HA-2 (no submit/approve/activate/supersede calls) | Integration test asserts `SELECT governance_state_code FROM mcf.metric_contract_version WHERE metric_contract_version_uid = ${mcv_uid}` returns `'draft'` |
| **HA-7** | M12.5 reads `consensus_payload_json` UNCHANGED from its M12-DBCP-§8 schema. No M12.5-side schema modification. Schema literal `panel-payload.schema.json` is shared between M12 panel service and M12.5 materialization service (single-source file path `bc-core/src/registry/mcf/panel-payload.schema.json`) | Single-source-of-truth import path locked in DBCP §8.2 + §10 service interface; no divergent copy | **(per patch L-5)** Unit test imports the schema literal via BOTH M12 panel service's import path AND M12.5 materialization service's import path; computes sha256 of both at test time; asserts byte-equality. No pre-existing external "expected hash" referenced — the assertion is path identity + computed-at-test-time byte-equality |
| **HA-8** | Materialization is idempotent under retry. Re-invoking `runMaterialization(panelRunUid, opts)` with the same `panelRunUid` returns a `MaterializationResult` referencing the SAME `metric_contract_uid` + `metric_contract_version_uid` + `certification_record_id` + `fixture_uid` + `verification_result_uid` as the first successful invocation. Substrate rowcount delta on the second invocation == 0 | Service code idempotency via the 4 substrate surfaces | Integration test: run materialization once, capture all 5 UIDs; run again with same panel_run_uid + opts; assert (a) same 5 UIDs returned, (b) `intake_transitioned === false` second time, (c) rowcount delta == 0 across all 9 tables in HA-5 |

---

## 14. Test plan

### 14.1 Unit tests (`metric-authoring-materialization.service.spec.ts`)

Minimum **14 decision-coverage tests** (one per D-M12.5-1..D-M12.5-12 + AST + MC-NAME) plus error-path coverage:

| # | Test name | Asserts |
|---|---|---|
| 1 | `D-M12.5-1: writes the 8-row materialization surface` | After successful run, asserts mc + mcv + bindings + filters + computed_dims + cert + fixture + verifier_result all present |
| 2 | `D-M12.5-2: calls only createMetricDraft, never submit/approve/activate/supersede` | Spies on certWriter; asserts only `createMetricDraft` invoked |
| 3 | `D-M12.5-3: completes with verifier_verdict=pass`, ditto `fail`, ditto `structural_reject` | Three parameterized cases; all three return `MaterializationResult` (no throw) |
| 4 | `D-M12.5-4: idempotent under retry with same panel_run_uid` | Run twice; asserts same UIDs returned + intake_transitioned=false on 2nd |
| 5 | `D-M12.5-5: uses 3 short TXs (not 1 long TX)` | Inspect tx invocation; assert 3 distinct `db.transaction(...)` calls |
| 6 | `D-M12.5-6: Sunset header is operator-configured (no default)` | Spy on controller; assert header NOT set when env unset |
| 7 | `D-M12.5-7: no new REST endpoint exposed` | Asserts module has no new controller route |
| 8 | `D-M12.5-8: readiness/chain-status unchanged` | Spy on ReadinessLedger; assert NO fan-out invoked by M12.5 |
| 9 | `D-M12.5-9: L-V1 / L-V2 / L-V3 all fire before TX A` | Throw on each; assert NO M4 invocation occurred |
| 10 | `D-M12.5-10: SAVEPOINT integration spec pattern documented` | (meta-test — asserts integration spec exists) |
| 11 | `D-M12.5-11: TX-level rollback; substrate immutability preserved` | Force TX B failure; assert TX A persisted; retry succeeds |
| 12 | `D-M12.5-12: HA-3 — no PE-MC / supersession / revision writes` | Asserts 0-row delta on these 3 tables |
| 13 | `D-M12.5-AST: passes formulaAstCanonicalJson into M4 createMetricDraft input` | Spy on M4; assert input.metricContractVersion.formulaAstCanonicalJson == candidate_proposal.formula_ast |
| 14 | `D-M12.5-MC-NAME-IDEMPOTENCY: catches unique_violation on idx_mcf_mc_mc_name_active → DuplicateMcNameError` | Mock M4 to throw unique_violation on the index; assert DuplicateMcNameError surfaced |

Plus error-path tests:
- `MaterializationPreconditionError on non-APPROVE verdict`
- `MaterializationPreconditionError on intake already consumed`
- `FrameworkPolicyMissingError on missing mcf_v1 row`
- `ConsensusPayloadValidationError on invalid AJV schema`
- `FixtureStructuralCheckFailedError on L-V3 failure`
- `InvalidAstError caught from M7 if AST stamping failed somehow` (defensive)

### 14.2 Integration spec (`metric-authoring-materialization.service.integration.spec.ts`)

Env-gated `BCCORE_INTEGRATION_DB=1`. Pattern mirrors M12 panel integration spec.

```typescript
describe.skipIf(!INTEGRATION_ENABLED)('MetricAuthoringMaterializationService integration', () => {
  it.skipIf(!INTEGRATION_ENABLED)('runs materialization end-to-end inside SAVEPOINT', async () => {
    if (!substrateReady || !policyReady) return;
    await pgClient.begin(async (sql) => {
      // Setup: seed framework_policy mcf_v1 if not present; seed M11 intake row; seed M12 mapr+mapt
      await seedIntakeAndPanel(sql, panelRunUid, intakeQueueUid);

      // Pre-test row counts
      const before = await snapshotRowCounts(sql);

      // Run materialization
      const result = await svc.runMaterialization(panelRunUid, defaultOpts);

      // Assert deltas inside SAVEPOINT (per HA-5)
      const after = await snapshotRowCounts(sql);
      expect(after.mc - before.mc).toBe(1);
      expect(after.mcv - before.mcv).toBe(1);
      // ... 8 more assertions per HA-5

      // Assert HA-6: MCV at draft
      const mcv = await sql`SELECT governance_state_code FROM mcf.metric_contract_version WHERE metric_contract_version_uid = ${result.metric_contract_version_uid}`;
      expect(mcv[0].governance_state_code).toBe('draft');

      // Assert HA-8: idempotent retry
      const retry = await svc.runMaterialization(panelRunUid, defaultOpts);
      expect(retry.metric_contract_uid).toBe(result.metric_contract_uid);
      expect(retry.intake_transitioned).toBe(false);
      const after2 = await snapshotRowCounts(sql);
      expect(after2).toStrictEqual(after);  // 0 delta

      // Sentinel throw to rollback SAVEPOINT
      throw sentinelRollbackError();
    }).catch((err) => {
      if (!isSentinelRollback(err)) throw err;
    });

    // Post-rollback: assert all 17 mcf.* tables back to 0 rows; BCF preserved (24+1)
    await assertAllMcfZeroAndBcfPreserved(pgClient);
  }, 30_000);
});
```

### 14.3 Test fixtures

- Synthetic `candidate_proposal` with simple `variable_ref` formula AST (matches M4 integration spec's `seedNonPlaceholderAst` minimal AST)
- Synthetic `proposed_fixtures[0]` with valid Section A/B/C per M9 fixture shape
- Synthetic mapr `consensus_payload_json` with verdict_code='APPROVE_FOR_DRAFT' + grounding_check_passed=true
- Synthetic M11 intake row with status_code='pending'
- Mocked vendor identities in panel_output_record (already written by M12 panel before M12.5 runs)

---

## 15. Implementation PR file list

**Per patch M-2: split into PR-1 (DDL / substrate) + PR-2 (implementation / service). PR-1 lands first; DDL is applied to `bc_platform_dev` before PR-2 merges.**

#### PR-1 — DDL / substrate (bc-core only)

| File | Action | Approx LOC | Note |
|---|---|---|---|
| `bc-core/docker/redesign/<NN>-mcf-m12-5-mc-name-unique-index.sql` | NEW | ~15 | Forward DDL per §7.1 |
| `bc-core/docker/redesign/<NN>R-mcf-m12-5-mc-name-unique-index-rollback.sql` | NEW | ~5 | Rollback DDL per §7.2 |
| `bc-core/scripts/mcf-m12-5-dry-run.mjs` | NEW | ~200 | DDL dry-run verifier per §7.3 |
| `bc-core/scripts/mcf-m12-5-post-apply.mjs` | NEW | ~250 | DDL post-apply verifier per §7.4 (crash-safe BEGIN/ROLLBACK pattern per patch M-3) |
| `bc-core/scripts/audit-output/mcf-m12-5-dry-run-<timestamp>.{precondition.jsonl, planned-sql.sha256.txt, summary.md}` | NEW | (variable) | Dry-run apply-time evidence — committed in PR-1 alongside scripts after operator runs dry-run + apply locally |
| `bc-core/scripts/audit-output/mcf-m12-5-post-apply-<timestamp>.{evidence.jsonl, summary.md}` | NEW | (variable) | Post-apply apply-time evidence — same |

**PR-1 LOC estimate:** ~470 lines (excluding evidence artifacts).

#### PR-2 — implementation / service (bc-core + bc-docs-v3 + barecount-devhub)

| File | Action | Approx LOC | Note |
|---|---|---|---|
| `bc-core/src/registry/mcf/metric-authoring-materialization.service.ts` | NEW | ~400 | Service per §10 |
| `bc-core/src/registry/mcf/metric-authoring-materialization.service.spec.ts` | NEW | ~600 | 14 decision-coverage + error paths per §14.1 |
| `bc-core/src/registry/mcf/metric-authoring-materialization.service.integration.spec.ts` | NEW | ~300 | SAVEPOINT-rolled-back per §14.2 |
| `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` | EDIT | +6/-0 | AST-A per §6.1 |
| `bc-core/src/registry/mcf/mcf-cert-writer.service.spec.ts` | EDIT | +20/-0 | 2 new tests per §6.3 |
| `bc-core/src/registry/mcf/mcf-cert-writer.service.integration.spec.ts` | EDIT | +5/-20 | Remove `seedNonPlaceholderAst` helper + replace call sites |
| `bc-core/src/registry/metric-definition.controller.ts` | EDIT | +15/-2 | `res.setHeader('Sunset', ...)` inside route handler body per §12.1 (per patch L-2; `@Header` decorator unsuitable for runtime-configured values) |
| `bc-core/scripts/mcf-m12-5-preflight.mjs` | NEW | ~180 | CLI preflight verifier per §0 PR-2 addendum + §10.3 (read-only; 5 substrate probes). Direct-invocation NestJS CLI deferred to follow-up PR. |
| `bc-core/.env.example` | EDIT | +2/-0 | Add commented `BCCORE_MCF_LEGACY_SUNSET_DATE=` per §12.1 |
| `bc-docs-v3/docs/operating-model/mcf-legacy-bridge.md` | NEW | ~80 | Read-fallback policy per §12.2 |
| `bc-docs-v3/docs/onboarding/metric-registration.md` | EDIT | +30/-0 | Operator runbook update per §12.3 |
| `barecount-devhub/CLAUDE.md` | EDIT | +5/-0 | MCF M12.5 bullet per §12.4 |

**PR-2 LOC estimate:** ~1700 lines.

**Total estimated diff across PR-1 + PR-2:** ~2200 lines across 3 repos. PR-2 spans bc-core + bc-docs-v3 + barecount-devhub (coordinated; bc-docs-v3 / barecount-devhub edits can land in separate PRs in those repos if operator prefers — bc-core PR-2 is the critical gate).

**PR ordering (per patch M-2):**
1. **PR-1 (DDL substrate) lands first.** Sequence: operator runs `mcf-m12-5-dry-run.mjs` → reviews 9-probe summary → confirms PASS → applies DDL via `psql` → runs `mcf-m12-5-post-apply.mjs` → reviews 14-probe summary → confirms PASS → commits all PR-1 files + apply evidence → merges PR-1.
2. **PR-2 (implementation service) lands after PR-1 is applied.** The `MetricAuthoringMaterializationService.runMaterialization()` path catches `unique_violation` on `idx_mcf_mc_mc_name_active` and surfaces `DuplicateMcNameError`. If PR-2 merged before PR-1 applied, the unique index would not exist; concurrent materialization would silently produce duplicate MCs (no exception raised; no error surfaced).

---

## 16. Evidence plan

### 16.1 Implementation PR evidence (mandatory for merge)

| # | Evidence | Mechanism |
|---|---|---|
| 1 | ESLint clean on M12.5 service + spec + M4 amendment + controller edit + scripts (`--max-warnings 0`) | Standard `npx eslint --max-warnings 0 <files>` |
| 2 | tsc filtered to M12.5 + amended files: 0 errors | Standard `npx tsc --noEmit` + grep filter |
| 3 | Unit tests pass: `metric-authoring-materialization.service.spec.ts` + amended `mcf-cert-writer.service.spec.ts` (existing tests stay green; new tests pass) | `npx vitest run` |
| 4 | Integration spec pass: `metric-authoring-materialization.service.integration.spec.ts` env-gated `BCCORE_INTEGRATION_DB=1` with SAVEPOINT rollback (per §14.2) | PowerShell + env vars |
| 5 | M4 integration spec stays green after `seedNonPlaceholderAst` retirement | `mcf-cert-writer.service.integration.spec.ts` runs end-to-end |
| 6 | Live DB read-only confirmation: 17 mcf.* tables = 0 rows post-test (SAVEPOINT rolled back); BCF preserved (24 + 1) | `bc-postgres` MCP |
| 7 | No real model API calls; verifier formula execution uses M10's pure formula engine (no external network) | Code review + spec assertion |

### 16.2 DDL apply evidence (separate from impl PR, per existing M11 / M9 pattern)

| # | Evidence | Mechanism |
|---|---|---|
| 1 | Dry-run summary: 9/9 PASS (per §7.3) | `node scripts/mcf-m12-5-dry-run.mjs` output |
| 2 | DDL planned-SQL hash recorded | `scripts/audit-output/mcf-m12-5-dry-run-<timestamp>.planned-sql.sha256.txt` |
| 3 | Apply succeeds; psql exit 0 | `psql -f bc-core/docker/redesign/<NN>-mcf-m12-5-mc-name-unique-index.sql` |
| 4 | Post-apply summary: 14/14 PASS (per §7.4) | `node scripts/mcf-m12-5-post-apply.mjs` output |
| 5 | Index `idx_mcf_mc_mc_name_active` present + UNIQUE + partial on `WHERE archived_at IS NULL` | Live DB verification via `bc-postgres` MCP |
| 6 | Substrate state preserved: all 17 mcf.* tables 0 rows; BCF 24+1 unchanged | Same |

### 16.3 Closeout evidence (mandatory for closeout)

Mirrors M12 closeout pattern:
- JSONL evidence log: `scripts/audit-output/mcf-m12-5-evidence-<timestamp>.integration-pass.jsonl`
- Summary markdown: `scripts/audit-output/mcf-m12-5-evidence-<timestamp>.summary.md`
- bc-docs-v3 closeout chapter: `bc-docs-v3/docs/implementation/mcf-m12-5-implementation-closeout.md`

### 16.4 Post-closeout operator-driven (NOT in M12.5 closeout evidence)

1. Allowlist seed run (if not already done post-M12) — `node scripts/mcf-m12-seed-allowlists.mjs`
2. Vendor adapter real-API smoke run — operator-driven
3. First real panel run (M11 intake → M12 panel → APPROVE_FOR_DRAFT consensus) — operator-driven
4. First real M12.5 materialization — per §0 PR-2 addendum: operator-driven via (a) `node scripts/mcf-m12-5-preflight.mjs --panel-run-uid <uuid>` for read-only verification, then (b) NestJS-DI invocation of `MetricAuthoringMaterializationService.runMaterialization(panelRunUid, opts)`; produces evidence artifact `scripts/audit-output/mcf-m12-5-first-materialization-<timestamp>.summary.md`
5. Operator sets `BCCORE_MCF_LEGACY_SUNSET_DATE` env var in deployed bc-core config and confirms Sunset header appears in legacy POST responses

---

## 17. R-M12.5-1 RESOLVED — recorded outcome

Per polished preflight §11 R-M12.5-1 + §4.9, code reading shows:

- M10 verifier's `computeCurrentPackageHash` (`metric-self-verification.service.ts:210-222`) reads NOTHING from `mcf.metric_contract.package_signature_hash` column.
- It composes the hash from MCV substrate via `FormulaCanonicalizationService.computeFormulaIntentHash/computeVariableBindingSetHash/computeFilterSetHash` + `PackageSignatureService.computePackageSignatureHash`.
- M12.5 computes the SAME hash from the SAME MCV substrate at Step 10 (per §9 enumeration) and stamps it on the fixture's `bound_package_signature_hash`.
- Between TX B (fixture INSERT) and TX C (verifier run), MCV substrate is immutable (M3 immutability trigger + no concurrent MCV writers in M12.5).
- Therefore M10's STALE CHECK at `metric-self-verification.service.ts:115-117` passes by deterministic equality.

**Parent MC hash columns** (`mcf.metric_contract.formula_intent_hash`, `variable_binding_set_hash`, `filter_set_hash`, `identity_tuple_hash`, `package_signature_hash`) **stay NULL until M14** `approveForActivation`. Correct per the M2/M4/M14 lifecycle.

**The original three options** (M10 handles NULL / M12.5 stamps parent hash / M12.5 skips verifier) **are SUPERSEDED** — the code answers the question definitively.

---

## 18. What stays closed (gate boundary)

| | |
|---|---|
| M13 PE-MC evaluator | CLOSED — gated on M12.5 closeout |
| M14 publication path (`approveForActivation` / `activateMetric`) | CLOSED — gated on M13 closeout |
| M15 supersession (`supersedeMetric`) | CLOSED — gated on M14 |
| M16 operator console (read) | CLOSED — gated on M14 |
| M17 operator console (write) + HTTP 410 on legacy POST | CLOSED — gated on M16 |
| M18+ tenant runtime MCF awareness (`boundary/metric.service.ts`, `ReadinessLedgerService`, `chain-status.service.ts`) | CLOSED — gated on M14 |
| Legacy `metric.metric_definition` decommission | CLOSED — gated on M18+ |
| 9 seed loader retargeting | Independent — operator-driven; not gated |
| Real model API calls | CLOSED — impl PR uses mocks |
| Real MCF metric contracts in substrate | CLOSED — substrate stays empty until M12.5 first-real-materialization (operator-driven; post-closeout) |
| Fixture rows | CLOSED — same |
| Verifier result rows | CLOSED — same |
| Cert rows | CLOSED — same |
| BCF data changes | CLOSED — 24 panel + 1 rejection log preserved across MCF arc |
| Legacy `POST /api/metric-catalog/definitions` write path | LIVE — Sunset header is advisory only; behavior unchanged |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

---

## 19. Operator approvals required  *(split into PR-1 / PR-2 phases per patch M-2)*

### 19.1 Approvals required BEFORE PR-1 (DDL substrate gate) opens

| # | Approval | Status |
|---|---|---|
| 1 | All 14 decisions D-M12.5-1..D-M12.5-12 + D-M12.5-AST + D-M12.5-MC-NAME-IDEMPOTENCY per polished preflight §15 | (operator confirms) |
| 2 | Option M12.5-A (combined gate) + AST-A (M4 amendment) + MC-NAME-A (small DDL) | (operator confirms) |
| 3 | **DDL apply gate per §7** — operator authorization to run `mcf-m12-5-dry-run.mjs` + apply DDL + run `mcf-m12-5-post-apply.mjs` against `bc_platform_dev` | (operator confirms) |
| 4 | **PR-1 file list per §15** (DDL forward + rollback + dry-run script + post-apply script + apply evidence) | (operator confirms) |
| 5 | Post-apply verifier uses crash-safe BEGIN/ROLLBACK pattern per patch M-3 (no procedural cleanup; no phantom-row risk) | (operator confirms) |

### 19.2 Approvals required BEFORE PR-2 (implementation service gate) opens

PR-2 cannot open until PR-1 is merged and DDL has been applied to `bc_platform_dev` (per patch M-2 ordering).

| # | Approval | Status |
|---|---|---|
| 6 | **PR-2 file list per §15** (MetricAuthoringMaterializationService + M4 amendment per AST-A + Sunset header + bridge doc + runbook + CLAUDE.md note + integration spec) | (operator confirms) |
| 7 | M4 amendment per AST-A — back-compatible optional `formulaAstCanonicalJson` field; existing M4 tests stay green; retire `seedNonPlaceholderAst` workaround | (operator confirms) |
| 8 | Sunset date for `BCCORE_MCF_LEGACY_SUNSET_DATE` env var (e.g. `'Wed, 31 Dec 2026 23:59:59 GMT'`) — operator-procured before bc-core deployment | (operator commits) |
| 9 | Runtime policy lookup behavior per patch M-1: `ORDER BY effective_from DESC LIMIT 2`; throw `MultipleActivePoliciesError` on >1 active row (strict fail-fast) | (operator confirms) |
| 10 | HA-1..HA-8 as merge-gate assertions | (operator confirms) |
| 11 | Evidence plan per §16 (impl PR + closeout) | (operator confirms) |

---

## 20. Discipline confirmation (this DBCP-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ |
| No DDL applied | ✓ |
| No data writes | ✓ |
| No seed runs | ✓ |
| No real model API calls | ✓ |
| No M12.5 implementation | ✓ — design only |
| No M13 / M14+ work | ✓ |
| No BCF data changes | ✓ |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) — read-only verification only |
| bc-core main | `f3f527b8bc7a0b229a8548fd5014aeeeb8017a7e` (untouched) |
| bc-docs-v3 main advance | this DBCP + companion to polished preflight `57e828b` |
