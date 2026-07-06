---
uid: mcf-m12-implementation-closeout
title: MCF M12 Metric Authoring Panel — Implementation Closeout
description: Closeout of the MCF M12 Metric Authoring Panel implementation gate. Documents DBCP authorities (preflight 193c602, DBCP 0798692 with 7-area review patch, wiring audit e725263), impl PR #123 squash merge a91811f, the live rolled-back integration spec PASS (2/2 with SAVEPOINT rollback per DBCP §18.2), evidence PR #124, post-evidence DB state (17 mcf.* tables all 0 rows + BCF preserved at 24 panel + 1 rejection log), and the post-M12 status — code-live + runtime-dormant, awaiting operator-driven steps (allowlist seed via mcf-m12-seed-allowlists.mjs; real vendor adapter smoke-run session; first real panel run; M12.5 materialization + legacy bridge gate). HA-1..HA-9 all enforced via source-grep + integration delta assertions + AJV runtime schema validation in service path. Records the integration-spec patch lessons (it.skipIf collection-time + JSON.stringify $N::jsonb double-encoding) carried forward from prior closeouts. Records that M12.5 is the next required architecture gate per wiring audit; no M13 PE-MC evaluator work until M12.5 closes; no BCF touches across the entire MCF M12 arc.
status: draft
date: 2026-05-28
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m12-implementation-closeout
---

# MCF M12 Metric Authoring Panel — Implementation Closeout

## 1. Scope and grounding

This closes the MCF M12 Metric Authoring Panel implementation gate. The gate sequence followed the established preflight → wiring audit → DBCP → DBCP review patch → impl PR → impl PR review patch → integration spec → evidence PR pattern. A mid-gate **architecture audit** (`mcf-post-bcf-metric-workflow-wiring-impact.md`) interceded between preflight and DBCP to validate that M12-B + M12.5 sequencing was sound before any code was written; this closeout records that audit's conclusions as locked.

| Authority | Reference |
|---|---|
| ADR | `bc-docs-v3/docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) |
| Preflight (amended) | `bc-docs-v3/docs/implementation/metric-context-framework-m12-authoring-panel-preflight.md` (`193c602`) |
| Wiring impact audit | `bc-docs-v3/docs/implementation/mcf-post-bcf-metric-workflow-wiring-impact.md` (`e725263`) |
| DBCP | `bc-docs-v3/docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` (`0798692`) |
| Impl PR | bc-core PR #123 squash commit `a91811f12d94fa8c84bec9857360cff1ffa579d1` |
| Evidence PR | bc-core PR #124 (`mcf-m12-evidence` branch; head `8fcecb689cdbdd266459870435989f656ce25011`) — pending operator merge |
| Integration spec | `bc-core/src/registry/mcf/metric-authoring-panel.service.integration.spec.ts` — 2/2 PASS with SAVEPOINT rollback |

## 2. Implementation timeline

### 2.1 M12 preflight (`3124207`) → amended (`193c602`)

Initial preflight recommended M12-B (proposal-only panel; ZERO new substrate). Amended per wiring-impact audit `e725263` to insert M12.5 (materialization + legacy bridge) as a new gate between M12 closeout and M13 PE-MC evaluator. Operator accepted D-M12-1..D-M12-11. Hard assertions HA-1..HA-8 added; HA-9 added to lock the defect-code registry pin.

### 2.2 M12 DBCP (`6c89d3b`) → review patch (`0798692`)

DBCP shipped at `6c89d3b` with 22 sections including 12-step execution flow, canonical consensus_payload_json schema, mcf-workbench-v1 fingerprint algorithm, 10-tool surface, vendor-shell adapter pattern, and HA-1..HA-9.

Review identified 1 BLOCKER + 3 MEDIUM + 3 LOW findings:

| # | Finding | Resolution |
|---|---|---|
| B1 | `contract.panel_output_record` was incorrectly listed forbidden — but M5 1:1 composition + active FK `fk_mapr_panel_run` REQUIRE it to be written first | DBCP review patch rewrote §5 as 12 steps with 3 short TXs; HA-5 updated with expected +1 delta on panel_output_record |
| M1 | Allowlist seed mechanism unspecified | §11.6 added — idempotent `mcf-m12-seed-allowlists.mjs` script with `ON CONFLICT DO NOTHING` |
| M2 | Templated `'REJECT_<defect_code>'` vs single-token `'REJECT_DEFECT'` divergence vs M5 §12.2 | Schema converged on single-token + separate `defect_code` field |
| M3 | Defect-code registry pin not enforced at service init | HA-9 added |
| L1 | `FOR UPDATE` lock held across 30-180s agent calls | Replaced with §5.4 in-flight guard (10-min window + APPROVE_FOR_DRAFT check) |
| L2 | Vendor SDK CodeArtifact installability not gated | §21.3 acceptance criterion #1 |
| L3 | Spec file count cosmetic | §21.1 cleaned |

DBCP review re-review verified all 7 patches landed cleanly with no new blockers.

### 2.3 Impl PR #123 squash merge (`a91811f`)

PR shipped:
- `MetricAuthoringPanelService` orchestrator (~570 lines; 12-step execution flow per DBCP §5)
- 4 pure helpers: `workspace-fingerprint.ts` (`mcf-workbench-v1`), `panel-consensus.ts`, `panel-grounding-check.ts`, `panel-checker-fixture-context.builder.ts`
- 3 vendor adapter SHELLS: `anthropic-agent.adapter.ts`, `openai-agent.adapter.ts`, `google-agent.adapter.ts` (all `.run()` throws on invocation)
- 3 role prompt templates: `m12-panel-{maker,checker,moderator}.v1.md`
- Type files: `panel-payload.types.ts`, `panel-tool-surface.types.ts`, `panel-role-agent.interface.ts`
- JSON Schema literal: `panel-payload.schema.json`
- Defect registry: `mcf-defect-registry-v1.ts` (11 closed-enum codes)
- Seed script: `scripts/mcf-m12-seed-allowlists.mjs` (idempotent; not yet executed against bc_platform_dev)
- 13 spec files (76+ new test cases)
- Vendor SDK deps added via CodeArtifact: `openai@^6.39.0` + `@google/generative-ai@^0.24.1` (`@anthropic-ai/sdk@^0.79.0` pre-existing)

Per impl PR rigorous review: 1 BLOCKER (panel_output_record FK — already addressed in DBCP) + 2 MEDIUM:

| # | Finding | Resolution |
|---|---|---|
| M1 | HA-7 AJV schema validation not wired in service code (schema file existed but unused) | Patch wired `ajv.compile()` at module init + `assertConsensusPayloadShape()` called BEFORE Step 7b mapr INSERT; throws `ConsensusPayloadValidationError` |
| M2 | Integration spec missing per DBCP §18.2 | Patch added `metric-authoring-panel.service.integration.spec.ts` with `BCCORE_INTEGRATION_DB=1` env gate + SAVEPOINT rollback + mocked agents |

Re-review verified both MEDIUM patches resolved cleanly.

### 2.4 Integration spec live-run patch (`7c253cb`)

Two test-only bugs discovered when running the integration spec from native PowerShell:

| Bug | Root cause | Fix |
|---|---|---|
| Spec persistently skipped even with env set | `it.skipIf(!substrateReady || !policyReady)` evaluates at COLLECTION time, before `beforeAll` populates the flags. So substrateReady=false always at evaluation → skip. | Match M4 cert-writer pattern: `it.skipIf(!INTEGRATION_ENABLED)` at collection time + body-level `if (!substrateReady || !policyReady) return;` early-return |
| HA-8 reservoir-provenance assertion failed (expected object, received escaped JSON string) | Test passed `JSON.stringify(obj)` as `$N::jsonb` param → postgres-js auto-JSON-encoded the already-stringified value → JSONB STRING value not JSONB OBJECT. Exact same bug fixed in M11 patch. | Pass JS objects directly to `$N::jsonb` params (4 callsites: tool_metadata_json, source_metadata_json, reservoir_provenance_source_json, normalized_candidate_json) |

Post-patch: integration spec **2/2 PASS** in 189ms with SAVEPOINT rollback verified.

### 2.5 Impl PR #123 squash merge (`a91811f`)

Operator authorized merge. Branch deleted; local main synced.

### 2.6 Evidence PR #124 opened (`8fcecb6`)

Captured: 4 quick gates PASS + live integration spec PASS + CodeArtifact vendor SDK confirmation + final DB state. Two artifact files only (`summary.md` + `integration-pass.jsonl`); no stale audit-output rolled in. Pending operator merge.

## 3. Live rolled-back integration proof (DBCP §18.2)

Command:

```powershell
$env:BCCORE_INTEGRATION_DB="1"
$env:DATABASE_URL="postgresql://barecount:barecount_dev@localhost:5435/bc_platform_dev"
npx vitest run src/registry/mcf/metric-authoring-panel.service.integration.spec.ts
```

Result: ✅ **2/2 PASS** in 189ms.

### 3.1 Assertions verified inside SAVEPOINT

| Assertion | Result |
|---|---|
| `contract.panel_output_record` delta = +1 (Step 7a per active FK) | PASS |
| `mcf.metric_authoring_panel_run` delta = +1 (Step 7b) | PASS |
| `mcf.metric_authoring_panel_transcript` delta = +3 (Step 7c) | PASS |
| 12 forbidden mcf.* surfaces delta = 0 (HA-5) | PASS |
| `contract.authoring_panel_rejection_log` delta = 0 | PASS |
| HA-8: 4 reservoir-provenance fields copied intake → mapr byte-for-byte (object form, not escaped string) | PASS |
| HA-6: intake stays `pending` on OPERATOR_REVIEW (markConsumedByPanel not called) | PASS |
| 3 mapt rows linked by `panel_run_uid` with `model_role_code IN ('maker','checker','moderator')` | PASS |

### 3.2 Post-rollback baseline assertion

All 17 mcf.* table rowcounts unchanged; BCF `panel_output_record` preserved at 24; `authoring_panel_rejection_log` preserved at 1.

## 4. Final live DB state

| Object | State |
|---|---|
| bc-core main | `a91811f12d94fa8c84bec9857360cff1ffa579d1` |
| bc-docs-v3 main | `0798692` (will advance by this closeout commit) |
| All 17 mcf.* tables | **0 rows** (substrate dormant) |
| `contract.panel_output_record` (BCF) | **24** (preserved across entire MCF arc) |
| `contract.authoring_panel_rejection_log` (BCF) | **1** (preserved) |
| `mcf.workspace_tool_allowlist` | **0** (seed script pending operator-run) |
| `mcf.evidence_source_allowlist` | **0** (same) |
| `mcf.metric_authoring_intake_queue` | **0** (M11 substrate dormant) |
| `mcf.metric_authoring_panel_run` / `_transcript` | **0** (M5 substrate dormant; M12 service ready but no real panel run yet) |

## 5. M12 status — code-live + runtime-dormant

| Capability | Status |
|---|---|
| `MetricAuthoringPanelService.runPanel()` callable | ✅ code-live on main |
| 3 short TXs (validate / substrate writes / intake transition) | ✅ verified live |
| Workspace fingerprint `mcf-workbench-v1` deterministic | ✅ 16 unit + integration tests pass |
| Consensus computation + grounding check pure functions | ✅ 17 unit tests pass |
| HA-7 AJV runtime schema validation | ✅ wired into `insertMaprRow`; 6 unit tests pass |
| HA-8 reservoir-provenance copy | ✅ verified live via integration spec |
| HA-9 defect-code registry pin (`mcf_v1.consensus_requirement_json.panel_discipline.defect_code_registry_version='v1'`) | ✅ asserted at service-init `createFromPolicy`; live policy row confirmed |
| Single-token verdict_code (`REJECT_DEFECT`) byte-matched across `contract.panel_output_record` + mapr + mapt | ✅ verified live |
| Three-vendor rule (Maker / Checker / Moderator from 3 distinct vendors) | ✅ asserted at service init; `VendorConfigurationError` on violation |
| In-flight / duplicate-proposal guard | ✅ §5.4 implemented; `opts.allowRetry` operator override |
| `markConsumedByPanel` forbidden in source | ✅ HA-6 enforced via comment-stripped source-grep |
| Vendor adapters | ⚠️ **SHELLS** — `.run()` throws; real-API wiring deferred to operator-authorized smoke run |
| Allowlists seeded | ⚠️ **NOT YET** — `mcf-m12-seed-allowlists.mjs` script ready; operator runs separately |
| Production panel run | ⚠️ **NONE YET** — substrate dormant; no production caller exists |

**M12 is production-ready as substrate-side discipline + orchestration framework. Real-model invocation is a separate operator-authorized gate.**

## 6. Discipline confirmation across the M12 arc

- ✅ NO bc-core source edits outside the impl PR + integration spec patch
- ✅ NO DDL (D-M12-11 Option A locked — zero new substrate)
- ✅ NO real model API calls (vendor adapters are shells; tests use mocks)
- ✅ NO persistent allowlist seed execution (script ready, not run)
- ✅ NO panel rows written outside SAVEPOINT-rolled-back integration test
- ✅ NO reservoir data ingested
- ✅ NO MC / MCV / bindings / filters / computed_dim_refs / fixtures / verification results / certs / PE-MC rows
- ✅ NO legacy `metric.metric_definition` / `metric_knowledge` / `metric_binding` writes
- ✅ NO BCF concept-registry writes
- ✅ NO `contract.authoring_panel_rejection_log` writes (D-M12-11 Option A)
- ✅ NO M12.5 / M13 / M14+ work
- ✅ BCF preserved across entire arc: `contract.panel_output_record` = 24 unchanged; `authoring_panel_rejection_log` = 1 unchanged
- ✅ `bc-postgres` MCP `allow_write=false` throughout

## 7. Established pattern reinforced

This is the seventh MCF gate to use the verifier-fix discipline (M-M5-1 → M9 M1 → M11 review L6 → M11 patch L1 → M12 DBCP B1 → M12 PR M1/M2 → M12 integration patch). Recurring lessons:

| Lesson | First seen | Reapplied in M12 |
|---|---|---|
| SAVEPOINT-protected behavioral tests | M-M5-1 | Integration spec wraps all writes in `pgClient.begin()` with sentinel-throw rollback |
| Substrate verification rests on closeout, not impl PR | M9 / M10 | M12 has no substrate to apply; M5 closeout's verification carries forward |
| `it.skipIf` + body-level guard pattern for env-gated integration | M4 cert-writer | M12 integration spec matched |
| Pass JS objects (not `JSON.stringify(obj)`) to `$N::jsonb` params | M11 patch | M12 integration spec patch (test code) |
| Comment-stripped source-grep for HA assertions (not literal substring) | M12 impl review | M12 patch |
| Vendor SDK CodeArtifact-only install | bc-core convention | M12 DBCP §21.3 acceptance criterion |

## 8. Next required gate — M12.5 materialization + legacy bridge

Per wiring impact audit (`e725263`) §5: **M12.5 is the next required architecture gate**. It owns:

| In scope | Out of scope |
|---|---|
| `MetricAuthoringMaterializationService` reads M12 `consensus_payload_json` + calls `McfCertWriterService.createMetricDraft(...)` with `panel_run_uid` as authoring evidence | Operator console UI (M16) |
| Writes `mcf.metric_contract` + version + bindings + filters + computed_dim_refs + first proposed fixture + `certification_record(action_code=metric_create)` in one TX (M4 cert writer already does this) | PE-MC-1..PE-MC-10 evaluation (M13) |
| Invokes M9 `FixtureStructuralCheckService.runStructuralChecks` + M10 `MetricSelfVerificationService.verifyFixture` | Publication path (M14) |
| Calls `ReservoirIngestionService.markConsumedByPanel(intake_queue_uid)` AFTER substrate write succeeds | Supersession (M15) |
| Defines explicit legacy-bridge contract for `POST /api/metric-catalog/definitions` deprecation | Tenant runtime migration (separate gate) |

**M13 PE-MC evaluator is BLOCKED until M12.5 closes.** Without materialization, M13 has no MC rows to evaluate.

## 9. What stays closed

| | |
|---|---|
| M12 evidence PR #124 | open; pending operator merge |
| Allowlist seed script execution | NOT executed — operator-driven step (idempotent script ready) |
| Vendor adapter real-API smoke run | DEFERRED — operator-authorized session |
| First real panel run | DEFERRED — requires seed + adapters + intake row |
| **M12.5 materialization + legacy bridge** | CLOSED — gated on this closeout + operator authorization |
| M13 PE-MC evaluator | CLOSED — gated on M12.5 |
| M14 publication path | CLOSED |
| M15 supersession | CLOSED |
| M16+ operator console | CLOSED |
| Legacy `POST /api/metric-catalog/definitions` deprecation | LIVE during M12; deprecation handling lands in M12.5 |
| bc-admin frontend metric API surfaces | LIVE during M12; migration lands in M16 (read) + M17 (write) |
| Real MCF metric contracts | CLOSED — substrate stays empty |
| Real reservoir ingestion rows | CLOSED — M11 substrate dormant |
| BCF substrate changes | NEVER — MCF §3.8 no-cross-framework-write-coupling |
| `contract.authoring_panel_rejection_log` extension | NEVER — D-M12-11 Option A locked; Option C explicitly rejected |
