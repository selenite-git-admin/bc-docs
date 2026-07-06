---
uid: metric-context-framework-m12-5-materialization-legacy-bridge-preflight
title: MCF M12.5 Materialization + Legacy Bridge — Preflight
description: Pre-DBCP design framing for MCF gate M12.5 (Materialization + Legacy Bridge) per the wiring impact audit `e725263` (which introduced M12.5 as a new gate between M12 closeout and M13 PE-MC evaluator) + the M12 closeout (`4c47679`). M12.5 converts an APPROVE_FOR_DRAFT panel proposal into live MCF substrate rows by reading `mcf.metric_authoring_panel_run.consensus_payload_json` and orchestrating three already-live services (M4 `McfCertWriterService.createMetricDraft` → MC+MCV+bindings+filters+computed_dims+cert in one M4-owned TX; first proposed-fixture INSERT into `mcf.metric_self_verification_fixture`; M10 `MetricSelfVerificationService.verifyFixture`) and finally transitions the M11 intake row to `consumed_by_panel`. M12.5 is the gate where the post-BCF metric workflow / wiring transition lands in the codebase: legacy `POST /api/metric-catalog/definitions` gets a Sunset deprecation header, the legacy-vs-MCF read-fallback policy is locked, and HA-2 from M12 (panel forbidden to import `McfCertWriterService`) is released — M12.5 IS the gate authorized to import it. M12.5 does NOT publish (no `approveForActivation` / `activateMetric` calls — those belong to M13 PE-MC + M14). NO PE-MC writes. NO BCF writes. NO legacy `metric.*` writes. NO bc-admin frontend changes. Locks 14 decisions D-M12.5-1..D-M12.5-12 + D-M12.5-AST + D-M12.5-MC-NAME-IDEMPOTENCY + 8 hard assertions HA-1..HA-8 + recommends Option **M12.5-A** (single combined gate; zero new tables; idempotency from existing M4 + fixture UNIQUE + M10 UNIQUE + M11 CAS guards) with Option M12.5-B (small ledger table) reserved as forensics escalation and Option M12.5-C (split materialization + bridge into 2 gates) reserved as scope-expansion escalation. PATCHED 2026-05-28 per review (SES-85dfa0) — adds D-M12.5-AST (locks AST-A: amend M4 `createMetricDraft` to accept optional `metricContractVersion.formulaAstCanonicalJson` so MCV gets a real canonical AST inside TX A — the placeholder DDL default would otherwise cause `FormulaCanonicalizationService.validateAndNormalizeAst` to throw `InvalidAstError` at hash compute time, blocking fixture INSERT); resolves R-M12.5-1 (M10 verifier reads NOTHING from parent MC hash columns — computes from MCV substrate via M7+M8 services; bound_package_signature_hash stamped from same substrate makes STALE CHECK pass deterministically; parent MC hash columns stay NULL until M14 `approveForActivation`); corrects false claim that `mcf.metric_contract` has `UNIQUE(mc_name)` (only `idx_mcf_mc_mc_name` non-unique btree + `idx_mcf_mc_identity_active` unique partial on `identity_tuple_hash WHERE NOT NULL` — the latter fires only at approve-time); adds D-M12.5-MC-NAME-IDEMPOTENCY (recommend small partial unique index DDL `CREATE UNIQUE INDEX ON mcf.metric_contract(mc_name) WHERE archived_at IS NULL` as the v1 path; service-level pre-check as fallback); corrects §5.4 policy_version coordination (`mcf_v1` is the `policy_uid`, NOT the `policy_version`; M12.5 must look up active row's `policy_version` at runtime — currently `'1.0.0'`); expands §4.9 / §6 / §7 with the 6 fixture-row hash columns M12.5 must compute (formula_intent_hash + variable_binding_set_hash + grain_filter_temporal_dimension_signature_hash + bound_package_signature_hash + self_verification_fixture_hash + hash_algorithm_version constant) plus the upstream filter_set_hash input; corrects risk register R-M12.5-3 wording (the M12.5-time AST guard is `FormulaCanonicalizationService.validateAndNormalizeAst` raising `InvalidAstError`, not M4's `assertNonPlaceholderAst` which fires only at `approveForActivation` / M14); removes unjustified Sunset header default `2026-12-31` in favour of operator-configured env var `BCCORE_MCF_LEGACY_SUNSET_DATE` (no default; DBCP locks operator-procurement). Discipline confirmation throughout: no bc-core implementation; no DDL; no data writes; no seed script execution; no real model API calls; no M13/M14 work; no BCF touches; `bc-postgres` MCP `allow_write=false`.
status: draft
date: 2026-05-28
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m12-5-materialization-legacy-bridge-preflight
---

# MCF M12.5 Materialization + Legacy Bridge — Preflight

## 0. Why this preflight exists

The M12 closeout (`4c47679`) shipped a proposal-only panel: a panel run writes `contract.panel_output_record` + `mcf.metric_authoring_panel_run` + 3 × `mcf.metric_authoring_panel_transcript` and stops. The consensus payload is a *proposal*, not a *contract*. No `mcf.metric_contract` row exists yet. No fixture. No verifier result. No certification.

The wiring-impact audit (`e725263`) is explicit that the gap between "panel approved a proposal" and "MCF authority now holds the metric contract" is its own gate — **M12.5 Materialization + Legacy Bridge** — and that skipping it leaves three architectural failures:

1. **No authoritative MCF substrate row** despite an approved proposal — operator cannot point at a `metric_contract_uid` and say "this is the metric we agreed to."
2. **Intake row stuck** at `status_code='pending'` forever — M12 forbids `markConsumedByPanel` (HA-6) precisely because `consumed_by_panel` must mean "materialized into MCF substrate," not "panel approved a proposal."
3. **Legacy dual-authority risk** — `POST /api/metric-catalog/definitions` and `MetricDefinitionService.create()` remain the operator's habitual write paths; without an explicit bridge contract, MCF and legacy authoring run side-by-side with no deprecation signal.

M12.5 closes those three gaps in one focused gate. It does **NOT** open publication (PE-MC eligibility evaluation is M13; `approved → active` transition is M14). M12.5 stops at `governance_state_code='draft'` with one or more passing fixtures attached.

This is the preflight. No DBCP yet, no code, no DDL, no writes. Single output: this design note + 14 locked decisions + 8 hard assertions + the recommended option, ready for operator review before the M12.5 DBCP gate opens.

---

## 0.1. Patch log

**2026-05-28 — patch per review (SES-85dfa0):**

| # | Change | Sections affected |
|---|---|---|
| P1 | **BLOCKER B1 resolved.** Added decision **D-M12.5-AST** locking option **AST-A** — amend M4 `McfCertWriterService.createMetricDraft` input to accept optional `metricContractVersion.formulaAstCanonicalJson`; M4's `insertMcv()` writes the real canonical AST during TX A. Without this, the DDL default placeholder (`{"kind":"placeholder",...}`) would cause `FormulaCanonicalizationService.validateAndNormalizeAst` to throw `InvalidAstError` at hash compute time, blocking fixture INSERT. M4 currently does NOT accept the AST parameter (verified in `mcf-cert-writer.service.ts:163-173` + integration spec workaround `mcf-cert-writer.service.integration.spec.ts:198-204` `seedNonPlaceholderAst` raw UPDATE). No raw `UPDATE mcf.metric_contract_version` workaround in M12.5; no separate AST stamping TX. | New §4.13; updates to §3.4, §4.4 (D-M12.5-4), §4.5 (D-M12.5-5), §6, §7, §11 |
| P2 | **R-M12.5-1 resolved.** Replaced open-question framing with resolved finding: M10 verifier (`metric-self-verification.service.ts:210-222`) does NOT read parent `mcf.metric_contract.package_signature_hash` column. It recomputes current package hash from MCV substrate via `FormulaCanonicalizationService.computeFormulaIntentHash/computeVariableBindingSetHash/computeFilterSetHash` + `PackageSignatureService.computePackageSignatureHash`. Parent MC hash columns may stay NULL until M14 `approveForActivation`. M12.5 stamps fixture `bound_package_signature_hash` by computing the SAME hash from MCV substrate; STALE CHECK passes deterministically when AST + bindings + filters + grain + temporal gate match. The original three options (M10 handles NULL / stamp parent hash / skip verifier) are SUPERSEDED — code is unambiguous. | §11 (R-M12.5-1), §13 |
| P3 | **MEDIUM M1 corrected.** Removed false claim that `mcf.metric_contract` has `UNIQUE(mc_name)`. Live DB shows only non-unique btree `idx_mcf_mc_mc_name` + unique PARTIAL index `idx_mcf_mc_identity_active` on `(identity_tuple_hash, hash_algorithm_version) WHERE archived_at IS NULL AND identity_tuple_hash IS NOT NULL` — fires only at approve-time when hashes get stamped. Added decision **D-M12.5-MC-NAME-IDEMPOTENCY**: recommend small DDL `CREATE UNIQUE INDEX ... ON mcf.metric_contract(mc_name) WHERE archived_at IS NULL` as v1 path; service-level pre-check as fallback. **This changes M12.5-A from "zero new substrate" to "zero new tables; one small partial unique index DDL."** | New §4.14; updates to §3.4, §5.1, §5.3, §11 (R-M12.5-4), §14 |
| P4 | **MEDIUM M2 corrected.** Replaced hardcoded `policyVersion = 'mcf_v1'` (which is the `policy_uid` column, NOT the `policy_version` column) with runtime-lookup pattern: `SELECT policy_version FROM contract.framework_policy WHERE policy_uid='mcf_v1' AND scope_code='mcf' AND (effective_to IS NULL OR effective_to > now())`. Returned value (currently `'1.0.0'`) is passed as `cert.policyVersion` to `McfCertWriterService.createMetricDraft`. Avoids stale hardcoding when M14 bumps the policy version. | §5.4, §6 |
| P5 | **MEDIUM M3 expanded.** Added the 6-fixture-hash-column enumeration table to §4.9 — explicit list of which fixture-row hash column M12.5 must compute, which service computes it, and the AST-A prerequisite for `formula_intent_hash`. | §4.9, §6 step 9 |
| P6 | **LOW L1 corrected.** Replaced risk-register reference to `assertNonPlaceholderAst` (M4 cert writer's guard inside `approveForActivationInTx`) with `FormulaCanonicalizationService.validateAndNormalizeAst` raising `InvalidAstError` — the actual M12.5-time guard. M4's `assertNonPlaceholderAst` belongs to M14 approval, not M12.5. | §11 (R-M12.5-3) |
| P7 | **LOW L2 fixed.** Removed unjustified Sunset header default `'2026-12-31'`. Sunset date is operator-configured via env var `BCCORE_MCF_LEGACY_SUNSET_DATE` (no default; DBCP §X requires the operator to set it explicitly before deployment). | §6 D-M12.5-6 table, §9.1 |

**Net architectural delta vs original preflight:**
- Recommendation remains **M12.5-A** (combined materialization + bridge gate).
- "Zero new substrate" → **"zero new tables; one small partial unique index DDL"** (D-M12.5-MC-NAME-IDEMPOTENCY recommendation). M12.5 DBCP includes a small-DDL gate analogous to the M11 pattern. Option to escalate to service-level pre-check (no DDL) if operator prefers; documented in D-M12.5-MC-NAME-IDEMPOTENCY.
- AST-A adds one small M4 amendment scope. M12.5 implementation PR now includes an M4 cert-writer change (`CreateMetricDraftInput.metricContractVersion.formulaAstCanonicalJson?: unknown` optional addition + `insertMcv()` pass-through) alongside the new `MetricAuthoringMaterializationService`. M4's existing tests stay green (the field is optional + back-compatible).
- 3-TX design preserved (TX A = M4-owned create-draft-with-AST-and-cert; TX B = fixture INSERT; TX C = verifier result + intake transition). No extra TX boundary.
- The 4 idempotency surfaces unchanged.
- Decision count grows from 12 to 14.

---

## 1. Scope and grounding

### 1.1 Live state at preflight-author time (read-only verified via `bc-postgres` MCP)

| | |
|---|---|
| bc-core main | `f3f527b8bc7a0b229a8548fd5014aeeeb8017a7e` (M12 evidence merged via PR #124) |
| bc-docs-v3 main | `4c47679c28db441fd430464ad9d1884f3419e7c0` (M12 closeout) |
| `mcf.*` tables | **17 present, all 0 rows** |
| `mcf.metric_authoring_intake_queue` | 0 rows (M11 substrate dormant) |
| `mcf.metric_authoring_panel_run` (mapr) | 0 rows (M5 / M12 substrate dormant; SAVEPOINT-rolled-back integration spec verified live per M12 evidence) |
| `mcf.metric_authoring_panel_transcript` (mapt) | 0 rows (same) |
| `mcf.workspace_tool_allowlist` / `evidence_source_allowlist` | 0 rows (operator-driven seed script `mcf-m12-seed-allowlists.mjs` not yet run) |
| `mcf.metric_contract` / `metric_contract_version` / `metric_variable_binding` / `metric_filter_clause` / `metric_computed_dimension_ref` | 0 rows (substrate present; no service writes yet) |
| `mcf.metric_self_verification_fixture` / `metric_self_verification_result` | 0 rows (M9 / M10 services live, dormant) |
| `mcf.certification_record` | 0 rows (M4 cert writer live, dormant) |
| `mcf.metric_cert_writer_idempotency` | 0 rows (M4 idempotency table; PK `idempotency_key`) |
| `mcf.metric_publication_eligibility_result` | 0 rows (PE-MC substrate; M13 territory) |
| `mcf.metric_supersession` | 0 rows (M15 territory) |
| `contract.panel_output_record` (BCF + MCF shared) | **24 rows** (preserved across MCF arc; M12 evidence integration spec rolled back its 1 insert) |
| `contract.authoring_panel_rejection_log` (BCF-only consumer today) | **1 row** (preserved) |
| Legacy `metric.metric_definition` | **1,241 rows** (live KPI corpus; populated by 9 seed loaders) |
| Legacy `metric.metric_binding` | **1,133 rows** (`canonical_contract_id` FK; CC-binding shape) |
| Legacy `metric.metric_knowledge` | **1,241 rows** (1:1 with metric_definition; enrichment payloads) |
| Legacy `contract.metric_contract` | **780 rows** (historical / archived; pre-MCF) |
| Legacy `POST /api/metric-catalog/definitions` | **LIVE** in bc-core (`MetricDefinitionController.create` + `bulkCreate`) — operator's habitual MC author endpoint; no Sunset header |

### 1.2 Source documents consumed (with concrete citations)

| Source | Role | Reference |
|---|---|---|
| Pre-M12 wiring impact audit | Originating authority for M12.5 gate — defines scope + boundary | `bc-docs-v3` `e725263` `docs/implementation/mcf-post-bcf-metric-workflow-wiring-impact.md` §5 (M12.5 insertion + §5.2 scope table) |
| M12 closeout | M12 substrate state; locks the consensus_payload_json as M12.5's input contract | `bc-docs-v3` `4c47679` `docs/implementation/mcf-m12-implementation-closeout.md` |
| M12 DBCP §8.3 | M12.5 consumption contract explicitly enumerated (6 steps) | `bc-docs-v3` `0798692` `docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` §8.3 |
| M12 preflight §9 step 8 | M12.5 scope sketch (read consensus → cert writer → fixture INSERT → M10 verifier → `markConsumedByPanel`) | `bc-docs-v3` `193c602` `docs/implementation/metric-context-framework-m12-authoring-panel-preflight.md` §9 step 8 |
| M4 cert writer DBCP | `McfCertWriterService.createMetricDraft` semantics — atomic MC+MCV+bindings+filters+computed_dims+cert + built-in `mcf.metric_cert_writer_idempotency` table (PK `idempotency_key`) | `bc-docs-v3` `3983530` `docs/implementation/metric-context-framework-m4-lifecycle-certification-dbcp.md` |
| M9 fixture substrate DBCP | C-FX-1..C-FX-11 engine; `FixtureStructuralCheckService.runStructuralChecks(context, body)` read-only; fixture substrate UNIQUE `(metric_contract_version_uid, self_verification_fixture_hash)` | `bc-docs-v3` `620e11d` `docs/implementation/metric-context-framework-m9-fixture-substrate-dbcp.md` |
| M10 verifier DBCP | `MetricSelfVerificationService.verifyFixture(fixtureUid, deps)` 6-step pipeline; substrate UNIQUE `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)`; sync per D-M10-5 (caller owns tx) | `bc-docs-v3` `ea8b708` `docs/implementation/metric-context-framework-m10-self-verification-result-dbcp.md` |
| M11 reservoir ingestion DBCP | `ReservoirIngestionService.markConsumedByPanel(intakeQueueUid, deps)` CAS guard `WHERE intake_queue_uid = ${uid} AND status_code = 'pending'` | `bc-docs-v3` `42f702b` `docs/implementation/metric-context-framework-m11-reservoir-ingestion-dbcp.md` |
| Live `McfCertWriterService` | Public surface: `createMetricDraft` / `submitForReview` / `approveForActivation` / `activateMetric` / `supersedeMetric` — only `createMetricDraft` is called by M12.5 | `bc-core/src/registry/mcf/mcf-cert-writer.service.ts:349` (class export) + `:829` (method `createMetricDraft`) |
| Live `MetricSelfVerificationService` | `verifyFixture` method; built-in idempotent INSERT-then-catch-SELECT on `uq_msvr_fixture_version_pkg_hash` | `bc-core/src/registry/mcf/metric-self-verification.service.ts:86` (class) + `:102` (`verifyFixture`) + `:319` (idempotent insert) |
| Live `ReservoirIngestionService` | `markConsumedByPanel` method + status-CAS pattern | `bc-core/src/registry/mcf/reservoir-ingestion.service.ts:265` (method) + `:290` (`transitionStatus` private helper) |
| Live `FixtureStructuralCheckService` | M9 engine — read-only structural check for fixture body validation BEFORE M12.5 INSERT | `bc-core/src/registry/mcf/fixture-structural-check.service.ts` |
| Legacy `MetricDefinitionService` (still active) | `metric.metric_definition` write path with auto-queued `metric.enrichment_job`; the surface M12.5 must Sunset | `bc-core/src/registry/metric-definition.service.ts:12` (class) |
| Legacy `MetricDefinitionController` | `POST /api/metric-catalog/definitions` + `/upload` endpoints; `@PlatformOnly()` scoped | `bc-core/src/registry/metric-definition.controller.ts:15` (class) + `:18` (`create`) + `:47` (`bulkCreate`) |
| MCF requirements §11.5 + §12 | Cert-backed authority (M4 cert writer is the authoritative substrate writer) + Self-verification fixture discipline (panel proposes, platform verifies; AI assertion is not proof) | `bc-docs-v3/docs/implementation/metric-context-framework-requirements.md` §11.5, §12 |

### 1.3 Discipline assertions (this preflight session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — design only |
| No DDL applied | ✓ |
| No data writes | ✓ |
| No seed script execution | ✓ (`mcf-m12-seed-allowlists.mjs` exists but not run) |
| No real model API calls | ✓ |
| No M12.5 implementation | ✓ — preflight only |
| No M13 / M14+ work | ✓ |
| No BCF data changes | ✓ |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) — read-only verification only |

---

## 2. Core question

> **How do we safely convert an M12 consensus proposal into live MCF substrate rows and bridge / deprecate legacy metric authoring paths, without opening PE-MC publication yet?**

The answer this preflight develops:

- **Materialization** = read `consensus_payload_json.candidate_proposal` from an `APPROVE_FOR_DRAFT` mapr row + delegate the 5-row substrate write to the already-live M4 cert writer + INSERT first proposed fixture + invoke M10 verifier + transition M11 intake to `consumed_by_panel`. **Three short transactions** (matching the M12 pattern) — TX A = M4 cert writer's atomic 5-row INSERT; TX B = fixture INSERT; TX C = verifier-result INSERT + intake transition. **Idempotency is substrate-provided** at each step (M4 idempotency_key + fixture UNIQUE + verifier UNIQUE + intake CAS).
- **Legacy bridge** = light-touch in M12.5 — `Sunset` HTTP header on `POST /api/metric-catalog/definitions` + read-fallback policy lock ("MCF wins when both authorities hold a metric with the same name") + operator runbook. **NO HTTP 410, NO bc-admin changes, NO tenant runtime migration** — those land in M16 (audit UI) / M17 (write-deprecation) / M18+ (tenant binding).
- **Publication stays closed** — M12.5 does not call `McfCertWriterService.approveForActivation` or `activateMetric`. The MCV stays at `governance_state_code='draft'`. PE-MC evaluation is M13. Publication is M14.

---

## 3. Three options on the table

### 3.1 M12.5-A — Single combined gate; zero new tables; one small partial unique index DDL (**RECOMMENDED**)  *(scope qualified per patch P3)*

| | |
|---|---|
| Scope | Materialization + legacy bridge in one PR + M4 amendment per D-M12.5-AST AST-A + 1 small DDL gate per D-M12.5-MC-NAME-IDEMPOTENCY MC-NAME-A |
| New tables | **None** — all idempotency comes from existing substrate (M4 `metric_cert_writer_idempotency` PK on `idempotency_key`; fixture `UNIQUE(metric_contract_version_uid, self_verification_fixture_hash)`; verifier `UNIQUE(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)`; intake CAS `WHERE status_code='pending'`) |
| New indexes | **One small partial unique index per MC-NAME-A** — `CREATE UNIQUE INDEX idx_mcf_mc_mc_name_active ON mcf.metric_contract(mc_name) WHERE archived_at IS NULL` (mirrors existing `idx_mcf_mc_identity_active` pattern); operator may escalate to MC-NAME-B (service-level pre-check) to ship zero DDL |
| Substrate writes | MC + MCV + bindings + filters + computed_dims + cert (via M4 cert writer TX) + 1 fixture + 1 verifier result + intake status flip — exactly the surface the wiring audit `e725263` §5.2 already enumerated |
| Bridge work | Sunset header on legacy controller; read-fallback policy doc; CLAUDE.md / runbook update; **no HTTP 410, no bc-admin changes** |
| T-shirt | M (smaller than M12; reuses 4 already-live services; new code is the materialization orchestrator + bridge header + 1 integration spec + small M4 cert-writer amendment per AST-A + 1 small partial-index DDL per MC-NAME-A) |
| Risk profile | Low. Each step's idempotency is already proven by its owning gate's evidence. The only new failure surface is the orchestrator's TX boundary discipline — addressed by §7 transaction design |

### 3.2 M12.5-B — Add a small `mcf.metric_materialization_run` ledger / idempotency table

| | |
|---|---|
| Scope | Same as M12.5-A plus a new substrate table tracking per-materialization-attempt outcome |
| New tables | 1 new mcf.* table — `mcf.metric_materialization_run(materialization_run_uid PK, panel_run_uid FK, intake_queue_uid, outcome_code ENUM('succeeded','failed_at_cert','failed_at_fixture','failed_at_verifier','failed_at_intake'), error_text, created_metric_contract_uid?, created_fixture_uid?, created_verification_result_uid?, created_at)` |
| Pros | Single-source query surface for forensics ("show me all incomplete materializations" becomes a single SELECT); explicit per-attempt audit trail beyond M4's idempotency table |
| Cons | + 1 DDL gate; partially-duplicates information already reachable via JOINs across `metric_cert_writer_idempotency` + `certification_record` + `metric_self_verification_fixture` + `metric_self_verification_result`; widens the substrate without a concrete query pattern that A cannot serve |
| When to escalate | If, during M12.5 DBCP authoring, we discover a concrete forensics / operator-query need (e.g. M16 audit UI requires materialization-attempt timeline view) that JOINing the 4 existing tables cannot serve, escalate to Option B |
| T-shirt | M + DDL gate |
| Risk profile | Medium. Adds a substrate decision that needs its own DBCP review + apply + closeout — repeating the M11 pattern for what may be a phantom requirement |

### 3.3 M12.5-C — Split materialization and legacy bridge into two gates

| | |
|---|---|
| Scope | Gate 1 = materialization (service + tests + integration spec); Gate 2 = legacy bridge (deprecation header + read-fallback policy + runbook) |
| New tables | None (Option A subset, sequenced) |
| Pros | Materialization ships faster; bridge ships independently if it expands in scope (e.g. operator decides to start the tenant runtime migration immediately, which would expand bridge well beyond a Sunset header) |
| Cons | Two gates of overhead for what is genuinely one architectural transition; risk that materialization ships without the deprecation signal on the legacy path, leaving dual-authority gap open between gate 1 closure and gate 2 closure; the bridge is genuinely light-touch (no migration, no UI, no DB writes) so doesn't warrant its own gate |
| When to escalate | If operator decides to expand bridge to include `metric.metric_definition` retargeting OR bc-admin frontend migration OR tenant runtime migration during M12.5 DBCP authoring |
| T-shirt | M + S (sequenced) |
| Risk profile | Medium. The hidden cost is the gap between gate closures — an MCF MC could be authored while the legacy POST endpoint is still un-Sunset, signalling dual authority |

### 3.4 Recommendation: **M12.5-A** (with two qualifications)

Three reasons:

1. **Each step's idempotency is already substrate-provided.** M4 has its `metric_cert_writer_idempotency` table (PK on `idempotency_key`); fixture has `UNIQUE(mcv_uid, fixture_hash)`; verifier has `UNIQUE(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)`; intake has CAS on `status_code='pending'`. A new ledger table would duplicate information already retrievable by JOIN. The forensics need that justifies M12.5-B has not been identified empirically — defer it to escalation.

2. **The bridge work is genuinely light-touch.** Sunset HTTP header on `POST /api/metric-catalog/definitions` + a doc-only read-fallback policy lock + a runbook entry for operators. None of these justify a separate gate. Splitting (Option C) creates a window where MCF substrate could hold an authored metric while the legacy POST endpoint signals "nothing has changed" — that is the dual-authority gap the audit `e725263` §1 warned against.

3. **Foundation Invariant V (non-replayable evaluation) is intact.** M4 cert writer's TX is atomic; fixture INSERT is atomic; verifier result INSERT is atomic; intake CAS is atomic. A retry under same `panel_run_uid` produces the same result deterministically. No new mutable state, no new replay vector.

**Two qualifications added per patch (P1, P3):**

1. **Small M4 amendment in scope.** Per D-M12.5-AST (§4.13), Option AST-A — M4 `createMetricDraft` extended to accept optional `metricContractVersion.formulaAstCanonicalJson` so MCV gets the real canonical AST inside TX A. M12.5 implementation PR therefore ships TWO code changes: (i) the M4 amendment (optional field + `insertMcv()` pass-through; back-compatible — existing tests stay green; releases the integration-spec workaround), and (ii) the new `MetricAuthoringMaterializationService`. This keeps the 3-TX design intact (no extra TX A.5 for AST stamping).

2. **"Zero new substrate" → "zero new tables; one small partial unique index DDL"** per D-M12.5-MC-NAME-IDEMPOTENCY (§4.14). The substrate gains one new index (`CREATE UNIQUE INDEX ... ON mcf.metric_contract(mc_name) WHERE archived_at IS NULL`) — no new tables, no new columns, no new constraints. The DDL gate is small and analogous to M11's pattern. Operator may escalate to service-level pre-check (no DDL) if they prefer purer service-only delivery; documented in D-M12.5-MC-NAME-IDEMPOTENCY as the Option-B fallback.

**Escalation paths**: M12.5-B if the M12.5 DBCP query-pattern audit surfaces a concrete forensics need; M12.5-C if the bridge expands beyond a Sunset header during DBCP authoring. Default for v1 is **A** with the two qualifications above.

---

## 4. Fourteen decisions for operator review (D-M12.5-1..D-M12.5-12 + D-M12.5-AST + D-M12.5-MC-NAME-IDEMPOTENCY)

### 4.1 D-M12.5-1 — M12.5 scope (the materialization surface)

**Question.** What exactly does M12.5 write into MCF substrate from an `APPROVE_FOR_DRAFT` panel proposal?

**Recommendation.** Exactly the surface the wiring audit `e725263` §5.2 enumerates + the M12 DBCP §8.3 input contract:

1. `mcf.metric_contract` — parent MC (1 row)
2. `mcf.metric_contract_version` — MCV at `governance_state_code='draft'` (1 row)
3. `mcf.metric_variable_binding` — one per `candidate_proposal.variable_bindings[]` (N rows)
4. `mcf.metric_filter_clause` — one per `candidate_proposal.filter_clauses[]` (N rows)
5. `mcf.metric_computed_dimension_ref` — one per `candidate_proposal.computed_dimension_refs[]` (N rows)
6. `mcf.certification_record` — 1 row with `action_code='metric_create'`, `from_state_code=NULL`, `to_state_code='draft'`, `panel_run_uid` populated (+ the 5 other NF1 panel-attestation fields)
7. `mcf.metric_self_verification_fixture` — 1 row from `candidate_proposal.proposed_fixtures[0]` with `panel_run_uid` FK populated
8. `mcf.metric_self_verification_result` — 1 row from `MetricSelfVerificationService.verifyFixture(...)` invocation

Plus one M11 intake transition: `mcf.metric_authoring_intake_queue.status_code` from `pending` → `consumed_by_panel` via `ReservoirIngestionService.markConsumedByPanel(intake_queue_uid)`.

**Out of scope (locked):** PE-MC evaluation (M13), publication path `approved → active` (M14), supersession (M15), operator console (M16/M17), tenant runtime migration (M18+), legacy `metric.metric_definition` retargeting (separate operator-driven program).

### 4.2 D-M12.5-2 — Certification path: through M4 cert writer only

**Question.** Does M12.5 write `mcf.certification_record` directly, or delegate to `McfCertWriterService.createMetricDraft`?

**Recommendation.** **Delegate to M4 cert writer only.** Specifically `McfCertWriterService.createMetricDraft(...)` — the existing M4-owned method that already writes MC + MCV + bindings + filters + computed_dims + cert atomically in one M4-owned DB transaction, with built-in idempotency via `mcf.metric_cert_writer_idempotency`, NF1 all-or-none enforcement on the 6 panel-attestation fields, and active `framework_policy` validation.

**Rationale.** M4 is the cert-write authority per MCF requirements §11.5. M12.5 importing M4's repository / schema directly would re-implement the M4 cert-issuance logic and risk drift between two cert-writer code paths. The single-import discipline keeps cert-issuance authority in M4.

**Implication for HA-2 in M12 DBCP.** M12 forbade importing `McfCertWriterService`. **M12.5 IS the gate authorized to import it.** This release is explicit; no other gate (yet) imports M4 cert writer at runtime.

### 4.3 D-M12.5-3 — Fixture + verifier minimum (at least 1 fixture, at least 1 passing verifier result)

**Question.** What is the minimum fixture / verifier evidence required before materialization is declared complete?

**Recommendation.** **At least 1 proposed fixture written + at least 1 verifier result whose `verdict_code ∈ {pass, fail, structural_reject}` exists.** M12.5 does NOT require `verdict_code='pass'` to declare materialization complete — a `fail` or `structural_reject` verifier result is still a complete materialization (it just means the metric is now in MCF substrate with a known-failing fixture; the operator decides next steps via the future M16 audit UI).

**Why not require `pass`.** If we required `pass` to declare materialization complete, a `fail` result would either:
- Roll back the MC + cert + fixture writes — losing the audit trail of what the panel proposed and what the verifier saw
- Or leave the substrate in a partial state — which is worse

The clean discipline: **materialization writes happen unconditionally** (panel approved a proposal; M12.5 records it in substrate); **the verifier result is part of the evidence**; operator inspects via M16 and either supersedes (M15) or proceeds to PE-MC (M13). MC stays at `draft` until M13 + M14.

**M12 DBCP §3.6 D-M12-6 anchor.** Panel must include `≥ 1 proposed fixture that passes C-FX-1..C-FX-11 structurally` before `APPROVE_FOR_DRAFT`. M12.5 enforces this as a pre-condition: if `consensus_payload_json.candidate_proposal.proposed_fixtures.length === 0`, throw `MaterializationPreconditionError` before opening any TX.

### 4.4 D-M12.5-4 — Idempotency model

**Question.** How does M12.5 stay idempotent under retry (operator re-triggers same panel_run_uid; partial failure between TXs; concurrent invocations)?

**Recommendation.** **Per-step substrate-provided idempotency, keyed by `panel_run_uid`.** No new bridge table (per Option A §3.1). Specifically:

| Step | Idempotency surface | Key | Re-invocation behavior |
|---|---|---|---|
| TX A (M4 cert writer; with AST per D-M12.5-AST) | `mcf.metric_cert_writer_idempotency` PK | `idempotencyKey = 'mcf-m12-5/' + panel_run_uid` | Cached → returns `(metric_contract_uid, metric_contract_version_uid, certification_record_id)` from row's `result_json`; pending → poll per M4 protocol; rolled_back → reclaim. AST stamping happens inside this same TX via the amended M4 input field (per AST-A); no separate stamping TX is needed |
| TX B (fixture INSERT) | `mcf.metric_self_verification_fixture` UNIQUE `(metric_contract_version_uid, self_verification_fixture_hash)` | `(mcv_uid, sha256(canonical(section_a+b+c)))` | Re-INSERT catches unique_violation `uq_msvf_mcv_fixture_hash` → SELECT existing `fixture_uid` |
| TX C step 1 (verifier result INSERT) | M10 service's built-in idempotent insert on UNIQUE `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` | M10-owned (`uq_msvr_fixture_version_pkg_hash`) | M10 already catches `unique_violation` + SELECTs existing — no M12.5 code change needed |
| TX C step 2 (intake transition) | `markConsumedByPanel` CAS guard `WHERE intake_queue_uid = ${uid} AND status_code = 'pending'` | `intake_queue_uid` | If already `consumed_by_panel`, throws `InvalidStatusTransitionError`; M12.5 catches + treats as "already done" (no-op success) |

**Concurrent invocation safety.** Two operators triggering M12.5 for the same `panel_run_uid` race on TX A (M4 cert writer's `acquireIdempotencyClaim` polling protocol — first writer wins; second waits for terminalization + returns cached result). TX B (fixture) races on substrate UNIQUE — first writer wins; second catches unique_violation. TX C step 1 (verifier) races on M10 substrate UNIQUE — first writer wins. TX C step 2 (intake) races on CAS — first writer wins; second catches `InvalidStatusTransitionError`.

**Why this is sufficient without a new ledger.** A retry of `runMaterialization(panel_run_uid)` either:
- Finds all 4 steps already cached / present → returns the same `MaterializationResult` (idempotent success)
- Finds partial progress → resumes from the first incomplete step (because each prior step's idempotency surface returns the existing UID instead of failing)
- Has no progress → executes all 4 steps fresh

There is no state that "an incomplete materialization started but never finished" could leave that a retry cannot recover from — except a process crash between TX boundaries, which is the same recovery story.

### 4.5 D-M12.5-5 — Transaction boundary: 3 short TXs (matching M12)

**Question.** Single long-lived TX wrapping all materialization, or staged short TXs with compensation?

**Recommendation.** **Three short TXs, mirroring M12's 3-TX pattern** (TX A atomic substrate / TX B atomic substrate / TX C verifier + intake):

```
TX A: M4 cert writer's internal TX (5 rows: MC + MCV + bindings + filters + computed_dims + cert)
       — opened/committed by McfCertWriterService.createMetricDraft
       — atomic; M4-owned; M4 idempotency key check
       — MCV's formula_ast_canonical_json is stamped HERE with the real canonical AST
         (per D-M12.5-AST / AST-A: M4 amended to accept optional
         CreateMetricDraftInput.metricContractVersion.formulaAstCanonicalJson;
         insertMcv() passes it through; if absent, DDL placeholder default applies)
       — NO M12.5 outer TX — M12.5 calls the public M4 method which opens its own tx
       — NO separate AST stamping TX — AST-A collapses what would otherwise be a
         TX A.5 into TX A
       — Duration: ms

TX B: Fixture INSERT (1 row into mcf.metric_self_verification_fixture)
       — opened/committed by M12.5 service
       — M12.5 computes all 6 fixture hash columns BEFORE INSERT via M7/M8 services
         reading the MCV substrate that TX A just stamped (per §4.9 patch P5)
       — atomic; uses substrate UNIQUE for idempotency
       — Duration: ms

TX C: Verifier result INSERT (1 row into mcf.metric_self_verification_result)
        + intake transition (UPDATE mcf.metric_authoring_intake_queue.status_code)
       — opened/committed by M12.5 service
       — M10's verifyFixture(fixtureUid, deps) is sync per D-M10-5 — caller passes deps.tx
       — markConsumedByPanel also accepts deps.tx
       — atomic; CAS guard on intake; UNIQUE on verifier result
       — Duration: ms to seconds (verifier formula execution time)
```

**Why not one long TX.** Wrapping all three TXs in a single outer TX would require either (a) nesting M4 cert writer's TX inside M12.5's TX (requires M4 service refactor — out of M12.5 scope and risks M4 regression), or (b) duplicating M4's logic in M12.5 (re-implementation, drift risk). Neither is acceptable.

**Why not compensation logic.** Per D-M12.5-4 idempotency, partial failure between TXs is recoverable by retry — no compensating writes needed. The only state that survives a partial failure is correctly-half-completed substrate, which a same-`panel_run_uid` retry resumes from.

**Why intake transition lives in TX C (not its own TX D).** Per M10 D-M10-5, verifyFixture is sync inside caller's tx. Pairing verifier result + intake transition in the same TX makes "verifier ran AND intake transitioned" a single atomic commit. The pair is safe because both writes are CAS-protected — concurrent retry of TX C catches existing verifier result + existing intake state independently.

### 4.6 D-M12.5-6 — Legacy bridge: what M12.5 ships, what it defers

**Question.** What does M12.5 do at the legacy bridge? What is explicitly deferred?

**Recommendation.**

**M12.5 ships:**

| Bridge item | Mechanism | Effect |
|---|---|---|
| `Sunset` HTTP header on `POST /api/metric-catalog/definitions` + `POST /api/metric-catalog/definitions/upload` | `@Header('Sunset', operatorConfiguredDate)` decorator on the existing `MetricDefinitionController` route handlers; value read from env var `BCCORE_MCF_LEGACY_SUNSET_DATE` (**no default — operator MUST set explicitly**; if unset, header is OMITTED). See [RFC 9745](https://www.rfc-editor.org/rfc/rfc9745.html) for header semantics. DBCP §X locks operator-procurement requirement | Operators / API clients receive Sunset notice on every legacy POST response when env var is set. No HTTP 410, no behavior change. No header shipped if operator hasn't agreed to a date |
| Legacy-vs-MCF read-fallback policy lock (doc-only) | Add §X to `bc-docs-v3/docs/foundation/the-contract-grammar.md` or new chapter `docs/operating-model/mcf-legacy-bridge.md`: "When consumer asks for `MC by metric_code`, MCF authority wins if a `mcf.metric_contract.mc_name = ${metric_code}` row exists with non-archived MCV; otherwise fall back to legacy `metric.metric_definition.metric_name = ${metric_code}`. Readers SHOULD migrate to MCF-aware lookup within the Sunset window." | Locks the dual-authority semantics. No code change yet (readers migrate in M16/M17). Just makes the rule explicit so future read services know which authority to consult first |
| Operator runbook update | Add to `bc-docs-v3/docs/onboarding/metric-registration.md` (or new `mcf-metric-onboarding-via-panel.md`): "New metric authoring should now use M11 intake → M12 panel → M12.5 materialization. Legacy `POST /api/metric-catalog/definitions` remains live during the Sunset window for backward compatibility; new authoring should not use it." | Operator-facing signal that the path has changed |
| CLAUDE.md note | Add a short bullet in `barecount-devhub/CLAUDE.md` "MCF M12.5 — legacy `POST /api/metric-catalog/definitions` carries `Sunset` header per M12.5 closeout `<sha>`; new MC authoring → MCF intake + panel + materialization" | Future sessions see the bridge contract |

**M12.5 explicitly defers:**

| Deferred item | Owning gate | Why deferred |
|---|---|---|
| HTTP 410 Gone on legacy POST | **M17** | Write-deprecation needs operator console for MCF write surface first |
| bc-admin frontend metric-author migration | **M16 / M17** | Audit UI ships read-side first (M16); write surface migration is M17 |
| 9 seed loader retargeting (legacy `metric-kpi-*.ts` → `ReservoirIngestionService.ingestFromSeedMetrics`) | **Separate operator-driven program**, not a gate | Per audit `e725263` §7.3 + M12 DBCP §4.2 #12; M11 already supports the retargeted path |
| Tenant runtime migration (boundary/metric.service.ts; ReadinessLedgerService) | **M18+** | Tenant binding ships after publication path is live; cannot migrate runtime to read from MCF authority while the publication state machine is unfinished |
| chain-status.service.ts MCF awareness | **M18+** | Same as above |
| Legacy `metric.metric_definition` decommission (data migration) | **M19+** | Separate cutover gate; legacy corpus stays for historical reference indefinitely |

### 4.7 D-M12.5-7 — bc-admin / UI: NONE in M12.5

**Question.** Does M12.5 expose any UI or new REST endpoint?

**Recommendation.** **None.** M12.5 is service-only (`MetricAuthoringMaterializationService`) + 1 controller change (add `Sunset` header to the legacy controller). No new REST endpoint. No new bc-admin page. No new MCP tool.

**Operator invocation in v1** (per PR-2 implementation addendum in DBCP §0): `MetricAuthoringMaterializationService.runMaterialization(panelRunUid, opts)` is wired through NestJS DI in the MCF module. The shipped v1 surface is (a) `scripts/mcf-m12-5-preflight.mjs` — a READ-ONLY preflight verifier (5 substrate probes) that does NOT itself invoke the service, plus (b) operator-driven NestJS-context invocation per the integration spec wiring pattern. A direct-invocation NestJS-bootstrap one-shot CLI is deferred to a follow-up PR. **Audit UI (M16) replaces these with a button later.**

### 4.8 D-M12.5-8 — Readiness / chain-status / boundary metric wiring: unchanged

**Question.** What changes in the readiness ledger, chain-status (D305), and tenant boundary metric reads?

**Recommendation.** **Nothing changes in M12.5.** Per wiring audit `e725263` §1.1:

- `boundary/metric.service.ts` continues to read from legacy `metric.metric_definition` + `contract.metric_contract` corpus
- `ReadinessLedgerService` continues to fan out for legacy MC events
- `chain-status.service.ts` (D305 SSOT) continues to report L1-L7 chain completeness against legacy MC bindings

This is intentional. M12.5 produces ZERO live tenant MCs in M12.5 — the materialized MC sits at `governance_state_code='draft'` with no PE-MC eligibility evaluation, no `is_current=TRUE`, no publication. The tenant runtime has nothing to consume from MCF yet.

**MCF-aware read paths** (chain-status reading from `mcf.metric_contract` for MCF-authored metrics; boundary/metric.service reading MCF authority) ship in **M18+** (tenant runtime migration). M12.5 explicitly does not touch these.

### 4.9 D-M12.5-9 — Materialization validation (what runs before any write)

**Question.** What pre-write validations does M12.5 perform on `candidate_proposal` before opening TX A?

**Recommendation.** Three layers of validation, all BEFORE TX A opens:

| Layer | Check | Failure mode |
|---|---|---|
| **L-V1 — Eligibility precondition** | (a) `consensus_payload_json.verdict_code === 'APPROVE_FOR_DRAFT'`; (b) `candidate_proposal.proposed_fixtures.length >= 1`; (c) `candidate_proposal.proposed_fixtures[0].checker_c_fx_result.passed === true`; (d) intake row exists + `status_code='pending'` (not yet consumed; not rejected; not superseded) | `MaterializationPreconditionError` — no TX opens, no write happens |
| **L-V2 — Schema validation** | AJV validates `consensus_payload_json` against M12 DBCP §8.1 `panel-payload.schema.json` (HA-7 contract) — should already be valid since M12 panel service validates BEFORE INSERT; M12.5 re-validates as defense-in-depth | `ConsensusPayloadValidationError` — log + throw; no TX |
| **L-V3 — M9 structural re-check (defense in depth)** | Build `FixtureContext` from `candidate_proposal` (variable_bindings + filter_clauses + computed_dim_refs + temporal_gate + grain + formula_ast); re-run `FixtureStructuralCheckService.runStructuralChecks(context, fixtureBody)` on `proposed_fixtures[0]`; assert `result.passed === true` | `FixtureStructuralCheckFailedError` — surfaces drift between Checker's C-FX result and platform's re-check; no TX |

**Parent MC hashes stay NULL until M14** (per M4 DBCP). The 5 hash columns on `mcf.metric_contract` (`formula_intent_hash`, `variable_binding_set_hash`, `filter_set_hash`, `identity_tuple_hash`, `package_signature_hash`) are computed by `McfCertWriterService.approveForActivation` (review → approved transition). They are nullable; M12.5's MC ends up with NULL hashes. This is correct per the lifecycle state machine — draft MCs do not have hashes stamped on the parent MC row.

**Fixture row hashes ARE computed at TX B** (substrate requires non-NULL). `mcf.metric_self_verification_fixture` has 6 hash-bearing NOT-NULL columns. M12.5 computes each from MCV substrate (which TX A just stamped, including the real AST per D-M12.5-AST). The table below enumerates the M12.5 → fixture-row hash computation contract:

| Fixture row column | Computed by | Input dependency | Patch refs |
|---|---|---|---|
| `formula_intent_hash` | `FormulaCanonicalizationService.computeFormulaIntentHash(mcvUid, deps)` | Reads MCV `formula_ast_canonical_json` — REQUIRES non-placeholder AST per D-M12.5-AST | P1 (AST-A); P5 (enumeration) |
| `variable_binding_set_hash` | `FormulaCanonicalizationService.computeVariableBindingSetHash(mcvUid, deps)` | Reads `mcf.metric_variable_binding` rows written by TX A | P5 |
| `grain_filter_temporal_dimension_signature_hash` | `PackageSignatureService.computeGrainFilterTemporalDimensionSignatureHash(mcvUid, {filterSetHash}, deps)` | Requires `filterSetHash` precomputed (via `FormulaCanonicalizationService.computeFilterSetHash(mcvUid, deps)`); reads parent MC grain + temporal gate | P5 |
| `bound_package_signature_hash` | `PackageSignatureService.computePackageSignatureHash(mcvUid, {formulaIntentHash, variableBindingSetHash, filterSetHash}, deps)` | Composes the 3 contributing hashes; reads parent MC grain + temporal gate. **Stamps the value M10's STALE CHECK will recompute at verify time** (per R-M12.5-1 RESOLVED — both compute from same MCV substrate; deterministic equality) | P2 (R-M12.5-1); P5 |
| `self_verification_fixture_hash` | `PackageSignatureService.computeSelfVerificationFixtureHash(fixtureBody)` | Pure function — fixture body only; no DB reads | P5 |
| `hash_algorithm_version` | Constant `'mcf-hash-v1'` | Per M7/M8 D-M9-A1 forever-lock; satisfies substrate CHECK `msvf_hash_algorithm_version_chk: ~ '^mcf-[a-z-]+-v[0-9]+$'` | P5 |

`filter_set_hash` (via `FormulaCanonicalizationService.computeFilterSetHash(mcvUid, deps)`) is NOT a fixture column — it is an upstream input to two of the fixture's hash columns. M12.5 computes it once and feeds it into both `grain_filter_temporal_dimension_signature_hash` and `bound_package_signature_hash` calls.

**M12.5-time AST guard.** The guard that fires if M12.5 ever reaches hash computation with a placeholder AST in MCV is `FormulaCanonicalizationService.validateAndNormalizeAst` raising `InvalidAstError` (per `formula-canonicalization.service.ts:113-118`). This is invoked inside every `computeFormulaIntentHash` call. Per D-M12.5-AST / AST-A, the AST is stamped to a real value inside TX A, so this guard should never fire in a valid M12.5 flow — it acts as defense-in-depth against substrate corruption / out-of-band MCV writes.

> Note: M4's `assertNonPlaceholderAst` guard (in `mcf-cert-writer.service.ts`) fires only inside `approveForActivationInTx` — i.e. at M14 approval, not at M12.5 materialization. It is the parallel guard at the next gate, not the M12.5-time guard.

**Verifier invocation works deterministically against draft MCs** (per R-M12.5-1 RESOLVED). M10's `computeCurrentPackageHash` (`metric-self-verification.service.ts:210-222`) reads NOTHING from parent `mcf.metric_contract.package_signature_hash`. It composes the hash from MCV substrate via the same `FormulaCanonicalizationService` + `PackageSignatureService` services M12.5 uses to stamp `bound_package_signature_hash`. As long as MCV is immutable between TX B and TX C (which it is — M3 immutability triggers + no concurrent MCV writers), both hashes are equal and M10's STALE CHECK passes by deterministic equality.

### 4.10 D-M12.5-10 — Evidence plan (first materialization)

**Question.** First materialization run after impl PR ships — synthetic / rolled-back or live?

**Recommendation.** **Mirror M12's two-step evidence pattern.**

| Step | What | Where |
|---|---|---|
| 1 | SAVEPOINT-rolled-back integration spec (matching `metric-authoring-panel.service.integration.spec.ts` pattern) | `bc-core/src/registry/mcf/metric-authoring-materialization.service.integration.spec.ts` — env-gated `BCCORE_INTEGRATION_DB=1`; SAVEPOINT rollback via sentinel throw; mocked verifier (or real verifier with synthetic fixture body computed from substrate per R-M12.5-1 RESOLVED — STALE CHECK passes deterministically); asserts row deltas inside SAVEPOINT |
| 2 | Live first-materialization run AFTER operator approves (and only after allowlist seed run + 1 real panel run that produces APPROVE_FOR_DRAFT) | Sandbox `bc_platform_dev`; produces 1 MC + 1 MCV + N bindings + 1 fixture + 1 verifier result + intake transition; recorded as evidence artifact `scripts/audit-output/mcf-m12-5-first-materialization-<timestamp>.summary.md` |

**Step 1 is mandatory for impl PR merge.** Step 2 is operator-driven and post-merge (analogous to "operator-driven seed script run" from M12). M12.5 closeout requires step 1 evidence; step 2 lands in the M12.5 first-real-materialization closeout (separate document, later).

### 4.11 D-M12.5-11 — Stop conditions + rollback semantics

**Question.** What halts materialization mid-flight? What rollback happens?

**Recommendation.**

| Failure | Stop point | Rollback effect | Recovery |
|---|---|---|---|
| L-V1 / L-V2 / L-V3 fails | Before TX A | None (no writes happened) | Operator inspects panel run + fixes proposal OR re-runs panel; new `panel_run_uid` |
| TX A fails (cert writer error / NF1 violation / framework_policy inactive / drizzle error) | Mid TX A | M4 cert writer's own tx rolls back atomically; M4 idempotency table records `rolled_back` status | Retry with same `panel_run_uid` → M4 reclaims rolled_back row + re-runs |
| TX B fails (fixture INSERT error other than UNIQUE) | Mid TX B | TX B rolls back the 1 fixture INSERT; MC + cert from TX A persist | Retry with same `panel_run_uid` → TX A cached, TX B retries fresh |
| TX C verifier fails (formula execution error / M10 internal error) | Mid TX C | TX C rolls back verifier_result + intake transition; MC + cert + fixture from TX A+B persist | Retry → TX A cached, TX B cached (fixture exists), TX C retries fresh |
| TX C intake transition fails (`InvalidStatusTransitionError` because already consumed) | After verifier_result INSERT succeeded in TX C | TX C rolls back verifier_result too (because intake transition is in same TX) — but verifier INSERT had idempotency catch which returned existing UID anyway | Retry → all three TXs cached / idempotent |
| Process crash between TXs | After last completed TX | None — committed work persists; uncommitted work rolled back by Postgres | Retry → resumes from first incomplete step via idempotency catches |

**Hard rule: M12.5 never deletes substrate rows for rollback.** Foundation Invariant III (immutability) — committed substrate is permanent. Rollback only means "abandon the uncommitted work in the current TX." The next retry uses substrate idempotency to skip already-committed work and continue.

**Hard rule: NO `markConsumedByPanel` if any prior step failed.** If TX A or TX B fails, intake stays at `pending` — operator can retrigger materialization. Only after TX C verifier_result INSERT succeeds AND intake transition succeeds does the intake row leave `pending`.

### 4.12 D-M12.5-12 — Gate sequencing (downstream blocks)

**Question.** What downstream gates are blocked until M12.5 closes?

**Recommendation.** Explicitly lock the following blocks in M12.5 DBCP:

| Gate | Status while M12.5 open | Status after M12.5 closeout |
|---|---|---|
| M13 — PE-MC eligibility evaluator | **BLOCKED** — no MCs exist yet at `governance_state_code='draft'` to evaluate; PE-MC operates on draft+ MCs | UNBLOCKED — M13 preflight can open; M13 reads draft MCs + writes `mcf.metric_publication_eligibility_result` rows (which `McfCertWriterService.approveForActivation` consumes at M14) |
| M14 — Publication path (`approved → active`) | **BLOCKED** — gated on M13 (PE-MC results required by `approveForActivation`) | BLOCKED (still gated on M13 closeout, not M12.5) |
| M15 — Supersession | BLOCKED — gated on M14 | BLOCKED (still gated on M14) |
| M16 — Operator console (read) | BLOCKED — gated on M14 (no live MCs to display) | BLOCKED |
| M17 — Operator console (write) — deprecates `POST /api/metric-catalog/definitions` HTTP 410 | BLOCKED — gated on M16 + bc-admin migration | BLOCKED |
| M18+ — Tenant runtime MCF awareness (chain-status, boundary/metric, ReadinessLedger) | BLOCKED — gated on M14 (publication state machine must exist) | BLOCKED |
| Legacy `metric.metric_definition` decommission | BLOCKED — gated on M18+ tenant migration | BLOCKED |
| Seed loader retargeting program | Independent — can start anytime; not gate-blocked | Independent |

**Critical confirmation per operator scope:**
- **M13 BLOCKED until M12.5 closeout** ✓ — PE-MC evaluator has nothing to evaluate without materialized draft MCs
- **M14 BLOCKED until M13 closeout** ✓ — `approveForActivation` requires PE-MC results

### 4.13 D-M12.5-AST — How M12.5 ensures the real canonical AST lives in MCV before fixture INSERT  *(added per patch P1)*

**Question.** M4 `McfCertWriterService.createMetricDraft` (as currently shipped on bc-core `f3f527b`) does NOT accept `formula_ast_canonical_json` in its input. `insertMcv()` (`mcf-cert-writer.service.ts:737-755`) only writes the enumerated columns; `formula_ast_canonical_json` falls back to the DDL default `'{"kind": "placeholder", "reason": "created_before_m7_apply"}'::jsonb` (verified live via `information_schema.columns`). The M4 integration spec documents the gap verbatim (`mcf-cert-writer.service.integration.spec.ts:226-229`): *"createMetricDraft does not yet accept an AST parameter; future M5 panel work adds that. Today, integration tests patch the AST directly so approveForActivation does not trip the guard."* The spec's workaround is a raw `pgClient.unsafe('UPDATE mcf.metric_contract_version SET formula_ast_canonical_json = $1::jsonb ...')` at line 200–202.

Without a real AST in MCV, M12.5 cannot compute fixture row hashes — `FormulaCanonicalizationService.validateAndNormalizeAst` (`formula-canonicalization.service.ts:113-118`) throws `InvalidAstError` when it encounters `kind === 'placeholder'`. Fixture INSERT cannot be prepared. The entire M12.5 design collapses at TX B.

Three options on the table:

| Option | Mechanism | Trade-off |
|---|---|---|
| **AST-A** (**RECOMMENDED, LOCKED**) | Amend `McfCertWriterService.createMetricDraft` to accept optional `metricContractVersion.formulaAstCanonicalJson: unknown` in `CreateMetricDraftInput`. M4's `insertMcv()` writes the supplied AST during TX A (back-compatible: omitted field falls back to existing DDL placeholder default). M12.5 passes the real AST from `consensus_payload_json.candidate_proposal.formula_ast`. Releases the integration-spec workaround | Smallest M4 change; collapses what would otherwise be TX A.5 into TX A; clean encapsulation; back-compatible with existing M4 tests (field is optional) |
| AST-B | Add new M4 method `stampFormulaAst(mcvUid, ast, deps)` callable from M12.5 inside a new TX A.5 between TX A and TX B | Adds a TX boundary; adds a new M4 method; M12.5 needs careful tx coordination |
| AST-C | M12.5 issues raw `UPDATE mcf.metric_contract_version SET formula_ast_canonical_json = ${ast} WHERE metric_contract_version_uid = ${mcvUid}` between TX A and TX B (mirrors the integration spec workaround) | Bypasses M4 encapsulation; M12.5 service touches M4-owned table directly via raw SQL; adds 4th TX boundary; least clean |

**Recommendation.** **Option AST-A — locked.** The M4 amendment is genuinely small (one optional field in input type + one pass-through line in `insertMcv()`); it is back-compatible (the existing integration spec's `seedNonPlaceholderAst` helper becomes unnecessary and can be retired in the same M12.5 PR); it preserves the 3-TX design with no extra TX boundary; and it removes the substrate-touch (raw UPDATE) that AST-C would require. The M12.5 implementation PR ships TWO code changes in one PR: (i) M4 cert writer amendment (the field + pass-through), and (ii) new `MetricAuthoringMaterializationService`.

**Implication for HA-1..HA-8.** No HA wording changes. The AST-A amendment is back-compatible; M4's other behavior is unchanged. HA-2 already permits M12.5 to import `McfCertWriterService` and call `createMetricDraft` — this remains the only M4 method called.

**Substrate impact of AST-A.** ZERO. No DDL. The MCV column already exists; default still applies when field omitted. AST-A is purely a service-layer extension.

**Why not just rely on the M4 integration spec's `seedNonPlaceholderAst` workaround.** Two reasons: (1) raw UPDATE outside M4 tx breaks M3 trigger semantics — `mcf.fn_mcv_descriptive_immutability_check` permits AST updates only when state stays unchanged or transitions are limited (per M7/M8 DBCP §13.2.1); a raw UPDATE works empirically but is contractually fragile, and (2) keeping the workaround alive permanently means M12.5 inherits the AST-stamping responsibility outside the cert writer's discipline — wrong owner.

### 4.14 D-M12.5-MC-NAME-IDEMPOTENCY — How M12.5 prevents concurrent materialization producing two MCs with the same `mc_name`  *(added per patch P3)*

**Question.** The original preflight implicitly assumed `mcf.metric_contract` has `UNIQUE(mc_name)`. Live DB inspection shows otherwise. Indexes present on `mcf.metric_contract`:

| Index | Definition | Behavior |
|---|---|---|
| `metric_contract_pkey` | UNIQUE on `metric_contract_uid` | Always enforced |
| `idx_mcf_mc_mc_name` | btree on `mc_name` | **NOT unique** — just a lookup index |
| `idx_mcf_mc_grain_entity` | btree on `grain_entity_id` | Lookup |
| `idx_mcf_mc_identity_active` | UNIQUE on `(identity_tuple_hash, hash_algorithm_version) WHERE archived_at IS NULL AND identity_tuple_hash IS NOT NULL` | Partial — fires only when `identity_tuple_hash IS NOT NULL` (i.e. after M14 `approveForActivation` stamps hashes) |
| `idx_mcf_mc_archived_at_active` | btree on `archived_at` filtered | Lookup |

So a draft MC has no substrate uniqueness on `mc_name`. Two concurrent M12.5 runs CAN create two `mcf.metric_contract` rows with the same `mc_name`, both at draft, both proceeding through fixture + verifier independently. The identity-active unique partial index only catches the collision at approve-time (M14) — which is a much harder cleanup than catching it at materialization time.

Two options:

| Option | Mechanism | Trade-off |
|---|---|---|
| **MC-NAME-A** (**RECOMMENDED**) | Small DDL: `CREATE UNIQUE INDEX idx_mcf_mc_mc_name_active ON mcf.metric_contract(mc_name) WHERE archived_at IS NULL`. Mirrors the existing `idx_mcf_mc_identity_active` partial-index pattern. M12.5's TX A INSERT raises `unique_violation` on the partial index when concurrent materialization tries to create a second MC with the same `mc_name` while the first is still un-archived. M12.5 catches the violation + surfaces `DuplicateMcNameError` to operator for resolution | One small DDL gate (analogous to M11 pattern); substrate-level guard; concurrent-safe by design; no service-level coordination needed; changes M12.5-A from "zero new substrate" to "zero new tables; one small partial unique index DDL" |
| MC-NAME-B | M12.5 service-level pre-check inside TX A: `SELECT metric_contract_uid FROM mcf.metric_contract WHERE mc_name = ${mcName} AND archived_at IS NULL FOR UPDATE` before INSERT; raise `DuplicateMcNameError` if non-empty. Requires careful tx coordination because the pre-check must run inside the SAME tx as the INSERT or the race window remains | No DDL; pure service-layer fix; preserves "zero new substrate"; race window between SELECT and INSERT is collapsed only if both happen inside the same M4-owned tx — requires M4 amendment OR an outer tx wrapping M4 (defeats the 3-TX design) |

**Recommendation.** **MC-NAME-A — locked** (per operator patch guidance "small DDL if DBCP accepts a DDL gate; otherwise service-level pre-check as v1 with explicit race risk"). Operator should accept the small DDL gate — it is substrate-honest (the discipline is "uniqueness lives in substrate; service catches the violation") and matches the existing `idx_mcf_mc_identity_active` precedent. M12.5 DBCP includes a small DDL gate analogous to the M11 / M5 pattern: dry-run + apply + verify.

**Fallback path.** If the operator decides during DBCP authoring that they prefer no new DDL in M12.5, escalate to MC-NAME-B (service-level pre-check). MC-NAME-B requires either (a) the M4 amendment to take an "uniqueness pre-check" callback (heavy), or (b) M12.5 doing the SELECT outside the M4 tx and accepting an explicit race window where two truly-concurrent invocations could both pass the pre-check then both INSERT (the second's UPDATE on tx commit would not raise because there's no substrate constraint). Document the race risk in the DBCP if MC-NAME-B is chosen.

**Substrate impact summary updated.** M12.5-A v1 with this decision: **ZERO new tables; ZERO new columns; ZERO new CHECK constraints; ONE new partial unique index** (per MC-NAME-A). All other writes target existing substrate from M2 / M3 / M4 / M9 / M10 / M11.

---

## 5. Substrate impact (M12.5-A v1)

### 5.1 No new tables; one new partial unique index (per D-M12.5-MC-NAME-IDEMPOTENCY)

M12.5-A ships **zero new tables, zero new columns, zero new CHECK constraints**. Per D-M12.5-MC-NAME-IDEMPOTENCY (§4.14), the recommended path adds **one small partial unique index**:

```sql
CREATE UNIQUE INDEX idx_mcf_mc_mc_name_active
  ON mcf.metric_contract(mc_name)
  WHERE archived_at IS NULL;
```

This mirrors the existing `idx_mcf_mc_identity_active` partial-index pattern (which fires only when `identity_tuple_hash IS NOT NULL`). The new index is the substrate-level uniqueness guard for `mc_name` on live (non-archived) MCs.

If operator escalates D-M12.5-MC-NAME-IDEMPOTENCY to MC-NAME-B (service-level pre-check), this index is NOT added and M12.5 ships zero DDL — see §4.14 for the trade-off.

All other substrate writes target existing tables, all from M2 / M3 / M4 / M9 / M10 / M11:

| Table | First introduced | M12.5 row count delta per materialization |
|---|---|---|
| `mcf.metric_contract` | M2 | +1 |
| `mcf.metric_contract_version` | M2 | +1 |
| `mcf.metric_variable_binding` | M2 | +N (per `candidate_proposal.variable_bindings.length`) |
| `mcf.metric_filter_clause` | M2 | +N (per `candidate_proposal.filter_clauses.length`; can be 0) |
| `mcf.metric_computed_dimension_ref` | M2 | +N (per `candidate_proposal.computed_dimension_refs.length`; can be 0) |
| `mcf.certification_record` | M3 (D-19 reversed → cert per framework) | +1 (`action_code='metric_create'`) |
| `mcf.metric_cert_writer_idempotency` | M4 | +1 (status flips from `pending` → `committed`) |
| `mcf.metric_self_verification_fixture` | M9 | +1 |
| `mcf.metric_self_verification_result` | M10 | +1 |
| `mcf.metric_authoring_intake_queue` | M11 | 0 inserts (UPDATE only: `status_code` flip) |

Total: ~7+N+M new rows + 1 status flip per successful materialization. All writes happen across 3 short TXs (one M4-owned, two M12.5-owned).

### 5.2 No changes to existing JSON-schema validators

`consensus_payload_json` schema (M12 DBCP §8 `panel-payload.schema.json`) is consumed unchanged. M12.5 imports the same schema literal for re-validation (L-V2). HA-7 from M12 (input contract locked) is the M12.5-side guarantee.

### 5.3 No new substrate constraints

Reuses existing CHECKs / FKs / UNIQUEs. The 4 idempotency surfaces per §4.4 are all already-shipped substrate features:

- `mcf.metric_cert_writer_idempotency` PK on `idempotency_key` (M4)
- `mcf.metric_self_verification_fixture` UNIQUE `(metric_contract_version_uid, self_verification_fixture_hash)` — verified live via `bc-postgres` MCP as `uq_msvf_mcv_fixture_hash`
- `mcf.metric_self_verification_result` UNIQUE `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` — verified live as `uq_msvr_fixture_version_pkg_hash`
- `mcf.metric_authoring_intake_queue` substrate-level CAS via the M11 service's `transitionStatus` private helper

### 5.4 policy_version runtime lookup  *(corrected per patch P4)*

M4 cert writer's `assertActiveMcfPolicy` (`mcf-cert-writer.service.ts:392-409`) requires `cert.policyVersion` to match `contract.framework_policy.policy_version` for the active mcf row. **`mcf_v1` is the `policy_uid` column (M12 panel reads `WHERE policy_uid = 'mcf_v1'` for its HA-9 discipline pin), NOT the `policy_version` column** (which currently holds `'1.0.0'`). The two columns are different. Hardcoding `'mcf_v1'` as `policyVersion` would cause M4 to query `WHERE policy_version = 'mcf_v1'`, find no matching row, and throw `InvalidInputError: policyVersion='mcf_v1' does not reference an active mcf framework_policy row`.

**Locked pattern.** M12.5 looks up the active `policy_version` at runtime:

```sql
SELECT policy_version
FROM contract.framework_policy
WHERE policy_uid = 'mcf_v1'
  AND scope_code = 'mcf'
  AND (effective_to IS NULL OR effective_to > now())
LIMIT 1
```

The returned value (currently `'1.0.0'`) is passed as `cert.policyVersion` to `McfCertWriterService.createMetricDraft`. This avoids stale hardcoding when M14 bumps the policy version (e.g. to `'1.0.1'`).

**M12.5 DBCP §X verifies via `bc-postgres` MCP at DBCP-write time that exactly one active `(policy_uid='mcf_v1', scope_code='mcf')` row exists** — confirmed live at preflight-patch time: `policy_uid='mcf_v1'`, `policy_version='1.0.0'`, `effective_to=NULL`.

**Naming overlap note.** `contract.panel_output_record.policy_version` (which M12 panel writes as `'mcf-panel-v1'`) carries the PANEL ALGORITHM version — a different field from `contract.framework_policy.policy_version` (which carries the FRAMEWORK policy version, currently `'1.0.0'`). M12.5's `cert.policyVersion` parameter maps to the latter.

---

## 6. Service shape sketch (DBCP scope)

`MetricAuthoringMaterializationService` interface (DBCP details):

```typescript
class MetricAuthoringMaterializationService {
  constructor(
    private readonly db: PostgresJsDatabase<DbSchema>,
    private readonly certWriter: McfCertWriterService,           // M4 — TX A
    private readonly verifier: MetricSelfVerificationService,    // M10 — TX C
    private readonly structuralCheck: FixtureStructuralCheckService, // M9 — L-V3
    private readonly packageSig: PackageSignatureService,        // M7/M8 — fixture hash
    private readonly reservoir: ReservoirIngestionService,       // M11 — TX C intake
  ) {}

  async runMaterialization(
    panelRunUid: string,
    opts: {
      certifierSub: string;
      certifierEmail?: string;
      rationaleText?: string; // optional (createMetricDraft does not require it)
    },
  ): Promise<MaterializationResult>;
}

interface MaterializationResult {
  panel_run_uid: string;
  metric_contract_uid: string;
  metric_contract_version_uid: string;
  certification_record_id: string;
  fixture_uid: string;
  verification_result_uid: string;
  verifier_verdict: 'pass' | 'fail' | 'structural_reject';
  intake_queue_uid: string;
  intake_transitioned: boolean; // true if this invocation flipped pending → consumed_by_panel; false if already consumed
}
```

**Internal flow:**

```
 1. Read mapr row by panel_run_uid; assert verdict_code='APPROVE_FOR_DRAFT'.
 2. Read consensus_payload_json; extract candidate_proposal + intake_back_reference.
 3. Read intake row by intake_queue_uid; assert status_code='pending'.
 4. L-V1: precondition checks (verdict, ≥1 fixture, Checker C-FX passed, intake pending).
 5. L-V2: AJV validate consensus_payload_json against panel-payload.schema.json.
 6. L-V3: M9 structural re-check on proposed_fixtures[0].
 7. Runtime policy lookup (per §5.4 patch P4): SELECT policy_version FROM contract.framework_policy
    WHERE policy_uid='mcf_v1' AND scope_code='mcf' AND (effective_to IS NULL OR effective_to > now()).
    Capture as activeMcfPolicyVersion (currently '1.0.0').
 8. Compose CreateMetricDraftInput from candidate_proposal + cert context.
    Per D-M12.5-AST (AST-A), include metricContractVersion.formulaAstCanonicalJson =
      candidate_proposal.formula_ast — the M4 amendment ensures TX A stamps the real
      canonical AST into MCV (NOT the DDL placeholder).
    cert.policyVersion = activeMcfPolicyVersion from step 7.
    cert.panelRunUid + 5 other NF1 panel-attestation fields from mapr / consensus_payload.
    Set idempotencyKey = 'mcf-m12-5/' + panelRunUid.
 9. TX A: await certWriter.createMetricDraft(input)
    → { metricContractUid, metricContractVersionUid, certificationRecordId }.
    (MCV now has real AST per AST-A; bindings, filters, computed_dims, cert all persisted atomically.)
10. Compute the 6 fixture row hashes (per §4.9 enumeration table) reading from MCV substrate:
       formulaIntentHash       = formulaCanon.computeFormulaIntentHash(mcvUid, { tx })
       variableBindingSetHash  = formulaCanon.computeVariableBindingSetHash(mcvUid, { tx })
       filterSetHash           = formulaCanon.computeFilterSetHash(mcvUid, { tx })
       gftdSignatureHash       = packageSig.computeGrainFilterTemporalDimensionSignatureHash(
                                   mcvUid, { filterSetHash }, { tx })
       boundPackageSigHash     = packageSig.computePackageSignatureHash(
                                   mcvUid,
                                   { formulaIntentHash, variableBindingSetHash, filterSetHash },
                                   { tx })
       fixtureBodyHash         = packageSig.computeSelfVerificationFixtureHash(fixtureBody)
    All hash computations happen inside TX B, alongside the fixture INSERT, to avoid
    an extra TX boundary.
11. TX B: INSERT mcf.metric_self_verification_fixture with:
       panel_run_uid FK,
       formula_intent_hash, variable_binding_set_hash, grain_filter_temporal_dimension_signature_hash,
       bound_package_signature_hash, self_verification_fixture_hash, hash_algorithm_version='mcf-hash-v1',
       section_a_inputs_json, section_b_expected_output_json, section_c_resolver_config_json,
       rationale_text (≥40 chars per substrate CHECK), authored_by_name.
    Catch unique_violation on uq_msvf_mcv_fixture_hash → SELECT existing fixture_uid (idempotent).
12. TX C (single tx): pass tx to BOTH:
       (a) verifier.verifyFixture(fixture_uid, { tx })
           → { verdict_code, verification_result_uid }
           (M10's STALE CHECK passes deterministically — M10 recomputes the same
            bound_package_signature_hash from the same MCV substrate per R-M12.5-1 RESOLVED.)
       (b) reservoir.markConsumedByPanel(intake_queue_uid, { tx })
           — catch InvalidStatusTransitionError if already consumed (treat as no-op success).
    Commit.
13. Return MaterializationResult.
```

Failure handling and idempotency per §4.4 + §4.11.

---

## 7. Transaction boundary design (matches M12 3-TX pattern)

| TX | Owner | Operations | Atomic? | Idempotency surface |
|---|---|---|---|---|
| **TX A** | M4 cert writer (internal; with AST per D-M12.5-AST) | INSERT mc + INSERT mcv **(with real `formula_ast_canonical_json` from `candidate_proposal.formula_ast` per AST-A; NOT the DDL placeholder default)** + INSERT bindings + INSERT filters + INSERT computed_dims + INSERT cert | YES (M4-owned) | `mcf.metric_cert_writer_idempotency.idempotencyKey = 'mcf-m12-5/' + panel_run_uid` |
| **TX B** | M12.5 service | Compute 6 fixture hashes from MCV substrate via M7+M8 services + INSERT 1 fixture row | YES | `UNIQUE(metric_contract_version_uid, self_verification_fixture_hash)` |
| **TX C** | M12.5 service | INSERT 1 verifier result + UPDATE intake status_code | YES (pair commit) | verifier UNIQUE + intake CAS |

**Why not 1 outer TX wrapping all 3.** M4's `createMetricDraft` opens its own tx (`this.db.transaction(...)`); embedding it inside an outer tx would require either:
- Calling M4's private `createMetricDraftInTx(tx, ...)` directly — bypassing M4's idempotency claim acquire / mark-committed-in-tx protocol, breaking M4's contract
- Refactoring M4 to accept an external tx — out of M12.5 scope; risks regression in M4 cert writer tests

The 3-TX pattern matches M12's pattern (validate / atomic substrate / intake transition) and is the correct grain for a service that composes other services that own their own transactions.

**Why TX C pairs verifier_result + intake transition.** Per M10 D-M10-5, `verifyFixture` accepts caller's `deps.tx`. Pairing the verifier result write with the intake transition keeps both writes atomic — either "verifier ran AND intake moved" or "neither" — without introducing a 4th TX boundary. Retry safety is preserved because both writes have their own idempotency / CAS.

---

## 8. Idempotency story (substrate-provided per step)

(Already enumerated in §4.4 D-M12.5-4 + §5.3 + §7. Summarized here for cross-reference.)

| Operation | Substrate constraint | Behavior on duplicate |
|---|---|---|
| M4 `createMetricDraft` | `mcf.metric_cert_writer_idempotency` PK (`idempotency_key`) | Returns cached `result_json` (no re-INSERT of MC + MCV + ...) |
| Fixture INSERT | `mcf.metric_self_verification_fixture` UNIQUE `(mcv_uid, self_verification_fixture_hash)` | M12.5 catches `unique_violation` on `uq_msvf_mcv_fixture_hash` → SELECT existing `fixture_uid` |
| Verifier result INSERT | `mcf.metric_self_verification_result` UNIQUE `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` | M10 service itself catches `unique_violation` on `uq_msvr_fixture_version_pkg_hash` → SELECT existing |
| Intake transition | M11 service CAS `WHERE intake_queue_uid = ${uid} AND status_code = 'pending'` | UPDATE returns 0 rows OR M11 SELECT shows non-pending → throws `InvalidStatusTransitionError`; M12.5 catches + treats as no-op success |

**No new idempotency code in M12.5.** All four surfaces are pre-existing substrate features verified live.

---

## 9. Legacy bridge contract (light-touch in M12.5)

### 9.1 What the bridge ships

| Item | Location | Mechanism |
|---|---|---|
| `Sunset` HTTP header | `bc-core/src/registry/metric-definition.controller.ts` `create()` + `bulkCreate()` methods | NestJS `@Header('Sunset', operatorConfiguredDate)` decorator; **no default** (operator MUST set env var `BCCORE_MCF_LEGACY_SUNSET_DATE` before deployment); if env var unset, the header is OMITTED (failsafe — better to omit than to ship a hardcoded date the operator hasn't agreed to). DBCP §X locks the operator-procurement requirement |
| Read-fallback policy lock | New chapter `bc-docs-v3/docs/operating-model/mcf-legacy-bridge.md` | Doc-only; specifies "MCF wins" semantics for the dual-authority window |
| Operator runbook | Update `bc-docs-v3/docs/onboarding/metric-registration.md` | Doc-only; redirects new authoring flow |
| CLAUDE.md note | `barecount-devhub/CLAUDE.md` "MCF substrate" section | Short bullet directing future sessions |

### 9.2 What the bridge does NOT ship

| Item | Why deferred | Owning gate |
|---|---|---|
| HTTP 410 on legacy POST | Operator must have a UI for MCF authoring first | M17 |
| bc-admin Metric Lifecycle page migration | UI surface migration is its own work | M16 (read) + M17 (write) |
| `boundary/metric.service.ts` MCF-aware reads | Tenant runtime migration needs publication state machine | M18+ |
| `ReadinessLedgerService` MCF fan-out | Same | M18+ |
| `chain-status.service.ts` MCF-aware reporting | Same | M18+ |
| Legacy `metric.metric_definition` data migration | Indefinite retention of legacy corpus | M19+ (if ever) |
| Legacy `metric.enrichment_job` decommission | Enrichment is now panel-side via tool calls; queue can wind down separately | M17 or independent program |

### 9.3 Read-fallback policy text (draft for DBCP authoring)

> **MCF-legacy MC read fallback (effective from M12.5 closeout):**
>
> 1. When a read consumer asks for "MC by `metric_code` X", the canonical resolution order is:
>    - **MCF authority** — `SELECT mc.metric_contract_uid FROM mcf.metric_contract mc WHERE mc.mc_name = ${metric_code}` AND there exists an `mcf.metric_contract_version mcv` row with `mcv.metric_contract_uid = mc.metric_contract_uid` AND `mcv.governance_state_code IN ('draft','review','approved','active')` (i.e. not `superseded`)
>    - **Legacy fallback** — `SELECT md.metric_definition_id FROM metric.metric_definition md WHERE md.metric_name = ${metric_code}` only if MCF returned no rows
> 2. If both authorities return a row for the same `metric_code`, **MCF wins**. Readers SHOULD log a `legacy_mc_shadowed_by_mcf` warning event for operator awareness; readers MUST return the MCF row.
> 3. New read services authored after M12.5 closeout MUST implement this fallback. Existing read services may continue to read legacy-only until their respective migration gates (M18+).
> 4. The `Sunset` header on `POST /api/metric-catalog/definitions` signals the legacy write path's deprecation date; the read fallback policy stays in effect until ALL read services have migrated (no fixed date — driven by tenant runtime migration).

The DBCP locks the exact text; this preflight establishes the policy shape.

---

## 10. Hard assertions for M12.5 DBCP (HA-1..HA-8)

Mirror the M12 HA pattern: each assertion is enforced by service-code structure + tests; some are also enforced by substrate constraints. The verification harness is one composite integration test that runs `runMaterialization` against a synthetic mapr + intake row and asserts the assertions.

| # | Assertion | Primary enforcement | Test verification |
|---|---|---|---|
| **HA-1** | M12.5 service does NOT import `MetricDefinitionService` / `MetricDefinitionRepository` / any other legacy `metric.*` writer. M12.5 does NOT write to `metric.metric_definition` / `metric_knowledge` / `metric_binding` / `enrichment_job` | Source code import allowlist + ESLint rule | Static import-graph audit; integration test asserts post-run rowcount delta on `metric.metric_definition` / `metric_knowledge` / `metric_binding` == 0 |
| **HA-2** | M12.5 service DOES import `McfCertWriterService` and calls ONLY `createMetricDraft` (NOT `submitForReview` / `approveForActivation` / `activateMetric` / `supersedeMetric`) | Source code grep + unit test asserts the service module's source text contains exactly one call site to `certWriter.createMetricDraft` and zero call sites to the other 4 methods | |
| **HA-3** | M12.5 service does NOT write to `mcf.metric_publication_eligibility_result` / `mcf.metric_supersession` / `mcf.metric_contract_revision` (PE-MC + supersession + revision are M13+ territory) | Service source has no INSERT into these tables; integration test asserts 0-row delta | |
| **HA-4** | M12.5 service does NOT write to BCF (`contract.business_entity` / `contract.business_concept` / any `concept_registry.*` table) and does NOT write to `contract.panel_output_record` (BCF + MCF shared; M12 panel writes it; M12.5 only reads it via mapr FK navigation if at all) | Source code structure; integration test asserts BCF preserved exactly (24 + 1) | |
| **HA-5** | M12.5 service writes ONLY to: `mcf.metric_contract` (+1), `mcf.metric_contract_version` (+1), `mcf.metric_variable_binding` (+N), `mcf.metric_filter_clause` (+N), `mcf.metric_computed_dimension_ref` (+N), `mcf.certification_record` (+1), `mcf.metric_cert_writer_idempotency` (+1 status flip), `mcf.metric_self_verification_fixture` (+1), `mcf.metric_self_verification_result` (+1), `mcf.metric_authoring_intake_queue` (UPDATE only). NO other table is written | Integration test asserts post-run rowcount on every other `mcf.*` / `contract.*` / `metric.*` table == 0-row delta | |
| **HA-6** | The MCV created by M12.5 has `governance_state_code='draft'` (NOT `review`, `approved`, `active`, or `superseded`). M12.5 does NOT advance the lifecycle state | Service source has no `submitForReview` / `approveForActivation` / `activateMetric` / `supersedeMetric` call sites (already HA-2); integration test asserts `SELECT governance_state_code FROM mcf.metric_contract_version WHERE metric_contract_version_uid = ${mcv_uid}` returns `'draft'` | |
| **HA-7** | M12.5 reads `consensus_payload_json` UNCHANGED from its M12-DBCP-§8 schema. No M12.5-side schema modification. Schema literal `panel-payload.schema.json` is shared between M12 panel service (write-side validation) and M12.5 materialization service (read-side re-validation) | DBCP §X locks the shared schema literal location; M12.5 imports the same literal; unit test asserts the literal's sha256 matches the M12 panel service's expected hash | |
| **HA-8** | Materialization is idempotent under retry. Re-invoking `runMaterialization(panelRunUid, opts)` with the same `panelRunUid` returns a `MaterializationResult` referencing the SAME `metric_contract_uid` + `metric_contract_version_uid` + `certification_record_id` + `fixture_uid` + `verification_result_uid` as the first successful invocation. Substrate rowcount delta on the second invocation == 0 | Integration test: run materialization once, capture all 5 UIDs; run again with same panel_run_uid + opts; assert (a) same 5 UIDs returned, (b) `intake_transitioned === false` second time, (c) rowcount delta == 0 across all 9 tables in HA-5 | |

---

## 11. Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| **R-M12.5-1** | ~~M10 verifier requires non-NULL `package_signature_hash`~~ — **RESOLVED per patch P2 (review SES-85dfa0). Reading the code shows M10's `computeCurrentPackageHash` (`metric-self-verification.service.ts:210-222`) reads NOTHING from `mcf.metric_contract.package_signature_hash` — it composes the hash from MCV substrate via `FormulaCanonicalizationService.computeFormulaIntentHash/computeVariableBindingSetHash/computeFilterSetHash` + `PackageSignatureService.computePackageSignatureHash`. Same services M12.5 uses to stamp `bound_package_signature_hash` at TX B (per §4.9). Parent MC hash columns stay NULL until M14 — that is correct per the M2/M4/M14 lifecycle. The STALE CHECK passes deterministically when MCV substrate is unchanged between TX B and TX C (which it is — M3 immutability triggers).** The three original options (M10 handles NULL gracefully / M12.5 stamps parent hash / M12.5 skips verifier) are SUPERSEDED — the code answers the question definitively | RESOLVED | n/a |
| **R-M12.5-2** | Dual-authority race — operator uses legacy `POST /api/metric-catalog/definitions` for `metric_code=X` while M12.5 materializes a panel-approved `metric_code=X` from MCF | Medium | Sunset header makes operator aware; read-fallback policy gives MCF precedence; legacy POST does not block MCF write (different substrates entirely). Operator inspection at materialization time catches the case via `legacy_mc_shadowed_by_mcf` log event |
| **R-M12.5-3** | The M12.5-time AST guard `FormulaCanonicalizationService.validateAndNormalizeAst` (`formula-canonicalization.service.ts:113-118`) raises `InvalidAstError` if the MCV's `formula_ast_canonical_json` is still the DDL placeholder when M12.5 invokes `computeFormulaIntentHash` at TX B | Low | Per D-M12.5-AST (AST-A), M4 amendment ensures TX A stamps the real AST into MCV — guard should never fire in a valid M12.5 flow. Defense-in-depth: integration spec asserts MCV `formula_ast_canonical_json -> 'kind' <> 'placeholder'` after TX A. **Note**: M4's `assertNonPlaceholderAst` guard (in `mcf-cert-writer.service.ts`'s `approveForActivationInTx`) is the parallel guard at M14 approval, NOT the M12.5-time guard — corrected per patch P6 |
| **R-M12.5-4** | Concurrent materialization of two different panels approving SAME `metric_code` (different `panel_run_uid` values, same `mc_name`) | Medium | **Corrected per patch P3.** `mcf.metric_contract` has NO `UNIQUE(mc_name)` constraint (only non-unique btree `idx_mcf_mc_mc_name` + unique partial `idx_mcf_mc_identity_active` on `identity_tuple_hash WHERE NOT NULL` — fires only after M14 stamps hashes). Per D-M12.5-MC-NAME-IDEMPOTENCY (§4.14): MC-NAME-A recommended — adds small DDL partial unique index `CREATE UNIQUE INDEX idx_mcf_mc_mc_name_active ON mcf.metric_contract(mc_name) WHERE archived_at IS NULL`. With MC-NAME-A in place, first materialization wins; second's TX A raises `unique_violation` on the new partial index; M12.5 surfaces as `DuplicateMcNameError`. MC-NAME-B fallback (service-level pre-check) has an explicit race window if operator escalates |
| **R-M12.5-5** | Cert writer NF1 all-or-none fails because M12.5 supplies only some of the 6 panel-attestation fields | Low | M12.5 source code populates all 6 fields from mapr + consensus_payload + service constants; unit test asserts `validateNf1PanelAttestation` always passes for valid `runMaterialization` calls |
| **R-M12.5-6** | Verifier formula execution exceeds operator-configurable timeout, blocks TX C for minutes | Medium | M10 verifier has its own timeout discipline per M10 DBCP; M12.5 inherits; document timeout in M12.5 DBCP + operator runbook |
| **R-M12.5-7** | Operator forgets to seed allowlists before first real materialization → panel won't run → no APPROVE_FOR_DRAFT exists → M12.5 has nothing to materialize | Low | Documented in M12 closeout + operator runbook; not a M12.5 failure mode (M12.5 just sees an empty mapr) |
| **R-M12.5-8** | Forensics — `WHERE is the materialization for this panel_run_uid?` query requires JOINing 4 tables (mcf.metric_cert_writer_idempotency + mcf.certification_record + mcf.metric_self_verification_fixture + mcf.metric_self_verification_result) | Low | If forensics burden proves high during M16 audit-UI build, escalate to M12.5-B (add ledger table) via amendment. Until then, the JOIN is the answer |
| **R-M12.5-9** | Bridge text mis-aligns with a future M16 / M17 contract decision | Low | Bridge text is doc-only; can be revised. The Sunset header is a soft signal (RFC 9745) — can be removed / extended without breaking changes |
| **R-M12.5-10** | M12.5 service inadvertently advances MCV beyond `draft` | High | HA-2 + HA-6 + integration test; the only way to advance is to call `submitForReview` / `approveForActivation` / `activateMetric`, and M12.5 source has zero call sites to these (HA-2). Defense in depth via HA-6 substrate-level state assertion |
| **R-M12.5-11** | M11 intake row's `intake_queue_uid` referenced in `consensus_payload_json.intake_back_reference` no longer exists at materialization time (e.g. operator deleted intake row between M12 panel + M12.5 materialization) | Low | Foundation Invariant III (immutability) — substrate is append-only; intake rows are NOT deleted (only status-flipped). If this happens (substrate corruption), M12.5 throws `IntakeRowNotFoundError` from M11's `markConsumedByPanel` — no MCF writes happen because validation is before TX A |
| **R-M12.5-12** | The verifier's `verdict_code='structural_reject'` outcome on the first proposed fixture is treated as materialization success per D-M12.5-3 — operator interprets a `structural_reject` MC as "ready for PE-MC" | Medium | Documentation: operator runbook explicitly notes that `verdict_code` other than `pass` requires operator action (supersede via future M15, OR amend fixture body OR re-run panel); M16 audit UI surfaces non-pass results prominently |

---

## 12. Evidence plan

### 12.1 Impl PR evidence (mandatory for merge)

| # | Evidence | Mechanism |
|---|---|---|
| 1 | ESLint clean on M12.5 service + spec files (`--max-warnings 0`) | Standard |
| 2 | tsc filtered to M12.5 files: 0 errors | Standard |
| 3 | Unit tests pass on `metric-authoring-materialization.service.spec.ts` (mocked services; 14 decision-coverage tests minimum) | vitest |
| 4 | Integration spec pass on `metric-authoring-materialization.service.integration.spec.ts` env-gated `BCCORE_INTEGRATION_DB=1` with SAVEPOINT rollback (per §4.10 step 1) | vitest |
| 5 | Live DB read-only confirmation: 17 mcf.* tables = 0 rows post-test (SAVEPOINT rolled back); BCF preserved (24 + 1) | `bc-postgres` MCP |
| 6 | No real model API calls; verifier formula execution uses M10's pure formula engine (no external network) | Code review + ESLint rule banning network calls in spec files |

### 12.2 Closeout evidence (mandatory for closeout)

Mirrors M12 closeout pattern:
- JSONL evidence log: `scripts/audit-output/mcf-m12-5-evidence-<timestamp>.integration-pass.jsonl`
- Summary markdown: `scripts/audit-output/mcf-m12-5-evidence-<timestamp>.summary.md`
- bc-docs-v3 closeout chapter: `bc-docs-v3/docs/implementation/mcf-m12-5-implementation-closeout.md`

### 12.3 Post-closeout operator-driven (NOT in M12.5 closeout evidence)

1. Allowlist seed run (if not already done post-M12) — `node scripts/mcf-m12-seed-allowlists.mjs`
2. Vendor adapter real-API smoke run — operator-driven
3. First real panel run (M11 intake → M12 panel → APPROVE_FOR_DRAFT consensus) — operator-driven
4. First real M12.5 materialization — operator-driven; produces evidence artifact `scripts/audit-output/mcf-m12-5-first-materialization-<timestamp>.summary.md`

---

## 13. Open questions for DBCP  *(updated per patch P2)*

The original R-M12.5-1 question (M10 verifier handling of NULL parent MC hashes) is **RESOLVED from code** — see §11 R-M12.5-1 + §4.9 patch P2. It is no longer an open question for the DBCP. Remaining open questions for DBCP authoring:

1. **`contract.framework_policy` mcf_v1 active row** — DBCP §X verifies via `bc-postgres` MCP that exactly one active `(policy_uid='mcf_v1', scope_code='mcf')` row exists at apply time (M4 cert writer's `assertActiveMcfPolicy` requirement). Confirmed at preflight-patch time: `policy_uid='mcf_v1'`, `policy_version='1.0.0'`, `effective_to=NULL`. M12.5 looks up `policy_version` at runtime per §5.4.
2. **`authored_by_name` value for fixture INSERT** — DBCP §X locks: derive from `consensus_payload_json` (e.g. `'mcf-m12-panel/' + per_role_summary[role='maker'].transcript_uid`) OR pass via `runMaterialization` opts. Substrate requires NOT NULL.
3. **`rationale_text` value for fixture INSERT** — substrate CHECK `msvf_rationale_min_length_chk` requires >= 40 chars. DBCP §X locks: compose from Maker proposal's `description_text` OR pass via opts OR construct from per-role summary.
4. **`hash_algorithm_version` for fixture INSERT** — locked at `'mcf-hash-v1'` per M7/M8 D-M9-A1 forever-lock. Satisfies substrate CHECK `msvf_hash_algorithm_version_chk: ~ '^mcf-[a-z-]+-v[0-9]+$'`. DBCP confirms.
5. **Verifier `executor_identity_text`** — M10 service constructor takes this. DBCP §X locks default `'mcf-m12-5-materializer@${hostname}'`.
6. **Single-fixture vs all-fixtures materialization** — currently the design materializes only `candidate_proposal.proposed_fixtures[0]`. Should M12.5 materialize ALL proposed fixtures? DBCP §X decides. Default recommendation: first fixture only in v1; remaining fixtures land via separate operator-driven program post-materialization.
7. **Cert writer's `idempotencyKey` collision** — if operator uses a different idempotency-key scheme (e.g. workspace-level), the M12.5-chosen prefix `'mcf-m12-5/'` keeps M12.5's keys distinct from any future caller's. DBCP §X documents the convention.
8. **`gateResultsJson` value for cert** — M4 cert writer requires `cert.gateResultsJson: Record<string, unknown>`. DBCP §X locks: include `{m12_panel_run_uid, m12_consensus_payload_summary, m9_structural_check_passed: true, ...}`.
9. **M4 amendment scope confirmation (D-M12.5-AST AST-A)** — DBCP §X confirms the exact M4 amendment surface: (a) `CreateMetricDraftInput.metricContractVersion.formulaAstCanonicalJson?: unknown` optional field added; (b) `insertMcv()` passes the field through to `metricContractVersion` schema's `formulaAstCanonicalJson`; (c) when field omitted, DDL placeholder default applies (back-compatible); (d) M4 unit + integration tests stay green; (e) the `seedNonPlaceholderAst` helper in `mcf-cert-writer.service.integration.spec.ts` becomes unnecessary and can be retired in the same PR.
10. **DDL gate confirmation (D-M12.5-MC-NAME-IDEMPOTENCY MC-NAME-A)** — DBCP §X confirms: (a) DDL statement `CREATE UNIQUE INDEX idx_mcf_mc_mc_name_active ON mcf.metric_contract(mc_name) WHERE archived_at IS NULL`; (b) dry-run + apply + verify flow analogous to M11; (c) M12.5 catches `unique_violation` on the new index + surfaces `DuplicateMcNameError`.

---

## 14. Sequencing per established pattern

1. **M12.5 preflight** ← THIS DOC (patched 2026-05-28 per review)
2. Operator review of D-M12.5-1..D-M12.5-12 + D-M12.5-AST + D-M12.5-MC-NAME-IDEMPOTENCY (and confirms recommended Option M12.5-A vs B vs C, and confirms AST-A + MC-NAME-A vs fallbacks)
3. M12.5 DBCP (full design — service interface + M4 amendment surface per AST-A + per-step pre-conditions + per-TX commit/rollback semantics + per-step idempotency proof + bridge header configuration (operator env var) + read-fallback policy text + HA-1..HA-8 hard assertions + open-question resolutions)
4. **DDL apply gate** for `idx_mcf_mc_mc_name_active` partial unique index per MC-NAME-A — analogous to M11 pattern (dry-run + apply + verify). CONDITIONAL: if operator escalates to MC-NAME-B (service-level pre-check), this gate is skipped. Optional escalation: M12.5-B `mcf.metric_materialization_run` ledger table — also requires its own DDL gate
5. M12.5 implementation PR — TWO code changes in one PR: (a) **M4 amendment** per AST-A (`CreateMetricDraftInput.metricContractVersion.formulaAstCanonicalJson?` optional addition + `insertMcv()` pass-through + retire integration-spec `seedNonPlaceholderAst` workaround); (b) new `MetricAuthoringMaterializationService` + Sunset header on legacy controller + bridge doc chapter + SAVEPOINT-rolled-back integration spec; NO real model calls; mocked agents
6. M12.5 evidence PR (smoke run + SAVEPOINT-rolled-back integration spec)
7. M12.5 closeout
8. **Then**: M13 PE-MC evaluator (now has draft MCs to evaluate)
9. **Then**: M14 publication path (gated on M13 closeout)
10. **Then**: M15 supersession; M16+ operator console; M17 write-deprecation HTTP 410; M18+ tenant runtime migration

---

## 15. Operator approval surface

Before opening the M12.5 DBCP gate, operator confirms D-M12.5-1..D-M12.5-12 + D-M12.5-AST + D-M12.5-MC-NAME-IDEMPOTENCY + Option recommendation:

| # | Decision | Recommendation |
|---|---|---|
| D-M12.5-1 | M12.5 scope (materialization surface) | MC + MCV + bindings + filters + computed_dims + cert + 1 fixture + 1 verifier result + intake transition; NO PE-MC, NO publication, NO supersession |
| D-M12.5-2 | Cert path | Through `McfCertWriterService.createMetricDraft` only |
| D-M12.5-3 | Fixture + verifier minimum | ≥ 1 fixture INSERT + 1 verifier result; any verdict (pass/fail/structural_reject) acceptable for declaring materialization complete |
| D-M12.5-4 | Idempotency model | Per-step substrate-provided (M4 idempotency table + fixture UNIQUE + verifier UNIQUE + intake CAS); idempotencyKey = `'mcf-m12-5/' + panel_run_uid` |
| D-M12.5-5 | Transaction boundary | 3 short TXs (A = M4-owned with AST stamping per AST-A; B = fixture; C = verifier + intake); NOT one long TX; NO compensation logic |
| D-M12.5-6 | Legacy bridge | Sunset HTTP header on legacy POST (operator-configured env var, NO hardcoded default); read-fallback policy lock (doc-only); operator runbook + CLAUDE.md note; NO HTTP 410, NO bc-admin changes |
| D-M12.5-7 | bc-admin / UI impact | None — service-only + 1 controller header change |
| D-M12.5-8 | Readiness / chain-status / boundary metric wiring | Legacy-backed; M12.5 changes nothing; tenant runtime MCF awareness ships M18+ |
| D-M12.5-9 | Materialization validation | L-V1 precondition + L-V2 AJV schema + L-V3 M9 structural re-check; all BEFORE TX A opens. 6 fixture hash columns computed by M7+M8 services before TX B (per enumeration table in §4.9) |
| D-M12.5-10 | Evidence plan | SAVEPOINT-rolled-back integration spec (mandatory for impl PR merge); first real materialization is operator-driven post-closeout |
| D-M12.5-11 | Stop conditions / rollback | TX-level rollback only; substrate immutability preserved; retry resumes via idempotency surfaces; `markConsumedByPanel` only after verifier result INSERT succeeds |
| D-M12.5-12 | Gate sequencing | M13 BLOCKED until M12.5 closeout; M14 BLOCKED until M13 closeout |
| **D-M12.5-AST** | **How M12.5 ensures real canonical AST lives in MCV before fixture INSERT** | **AST-A** — amend M4 `createMetricDraft` input to accept optional `metricContractVersion.formulaAstCanonicalJson`; M4's `insertMcv()` writes the real canonical AST during TX A; back-compatible (existing M4 tests stay green); NO raw `UPDATE mcf.metric_contract_version` workaround; NO separate AST stamping TX |
| **D-M12.5-MC-NAME-IDEMPOTENCY** | **How M12.5 prevents concurrent materialization producing two MCs with the same `mc_name`** | **MC-NAME-A** — small DDL gate adding partial unique index `CREATE UNIQUE INDEX idx_mcf_mc_mc_name_active ON mcf.metric_contract(mc_name) WHERE archived_at IS NULL`. Mirrors existing `idx_mcf_mc_identity_active` pattern. M12.5 catches `unique_violation` → `DuplicateMcNameError`. Fallback: MC-NAME-B (service-level pre-check with documented race window) |
| **Option** | **M12.5-A vs M12.5-B vs M12.5-C** | **M12.5-A** (single combined gate; zero new tables; one small partial unique index DDL per MC-NAME-A); escalate to B if forensics need surfaces during DBCP; escalate to C if bridge expands |

Operator may accept all, accept-with-modifications, or override individual recommendations. M12.5 DBCP gate opens after this set is locked.

---

## 16. What stays closed (gate boundary)

| | |
|---|---|
| M12.5 DBCP | NOT opened by this preflight |
| M12.5 implementation PR | NOT opened (will include M4 amendment per D-M12.5-AST AST-A + new MetricAuthoringMaterializationService + Sunset header on legacy controller) |
| M12.5 DDL apply gate | **Expected** per D-M12.5-MC-NAME-IDEMPOTENCY MC-NAME-A (one partial unique index on `mcf.metric_contract(mc_name) WHERE archived_at IS NULL`); analogous to M11 DDL gate pattern. NOT opened by this preflight. Operator may escalate to MC-NAME-B (service-level pre-check) to ship zero DDL — documented in §4.14 |
| **M13 PE-MC evaluator** | CLOSED — gated on M12.5 closeout |
| **M14 publication path** | CLOSED — gated on M13 closeout |
| M15 supersession | CLOSED — gated on M14 |
| M16 operator console (read) | CLOSED — gated on M14 |
| M17 operator console (write) + HTTP 410 on legacy POST | CLOSED — gated on M16 |
| M18+ tenant runtime MCF awareness | CLOSED — gated on M14 |
| Legacy `metric.metric_definition` decommission | CLOSED — gated on M18+ |
| Real model API calls | CLOSED — design phase only; impl PR uses mocks |
| Real MCF metric contracts in substrate | CLOSED — substrate stays empty until M12.5 first-real-materialization (operator-driven; post-closeout) |
| Fixture rows | CLOSED — same |
| Verifier result rows | CLOSED — same |
| Cert rows | CLOSED — same |
| BCF data changes | CLOSED — 24 panel + 1 rejection log preserved across MCF arc |
| Legacy `POST /api/metric-catalog/definitions` write path | LIVE — Sunset header is advisory only; behavior unchanged |
| 9 seed loaders writing `metric.metric_definition` | LIVE — independent operator-driven retargeting program; not M12.5 scope |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

---

## 17. Discipline confirmation (this preflight)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ |
| No DDL applied | ✓ |
| No data writes | ✓ |
| No seed script execution | ✓ |
| No real model API calls | ✓ |
| No M12.5 implementation | ✓ — design only |
| No M13 / M14+ work | ✓ |
| No BCF data changes | ✓ |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) — read-only verification only |
| bc-core main | `f3f527b8bc7a0b229a8548fd5014aeeeb8017a7e` (untouched) |
| bc-docs-v3 main advance | this preflight only |
