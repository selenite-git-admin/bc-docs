---
uid: metric-context-framework-m12-authoring-panel-dbcp
title: MCF M12 Metric Authoring Panel DBCP
description: Combined design-blueprint for MCF gate M12 (Metric Authoring Panel workbench) per operator-accepted preflight decisions D-M12-1..D-M12-11 (preflight amended `193c602`; wiring impact audit `e725263`). AMENDED 2026-05-27 per review patch (review verdict on `6c89d3b`) — (B1) `contract.panel_output_record` is shared substrate that M12 MUST write to (per active FK `fk_mapr_panel_run` + M5 §5 1:1 composition); §5 execution flow rewritten as 12 steps with 3 short TXs (validation + 5-row atomic substrate INSERTs + conditional intake transition); HA-5 expected-delta amended (panel_output_record +1, mapr +1, mapt +3); (M2) verdict_code converges on M5 single-token `'REJECT_DEFECT'` + separate `defect_code` field; (M1) §11.6 specifies idempotent allowlist seed script (`mcf-m12-seed-allowlists.mjs`); (M3) HA-9 added — service-init asserts `mcf_v1.consensus_requirement_json.panel_discipline.defect_code_registry_version='v1'`; (L1) `FOR UPDATE` row lock removed — concurrency safety via Step-1 in-flight guard + M11 status-transition CAS; (L2) pre-merge CodeArtifact installability acceptance criterion for vendor SDKs; (L3) spec file count clarified. Locks M12-B proposal-only — service-only PR (plus 1 seed script), ZERO new substrate by default (D-M12-11 Option A), three-model Maker / Checker / Moderator consensus with per-model immutable transcripts, workspace-fingerprint algorithm `mcf-workbench-v1`, canonical `consensus_payload_json` schema as input contract for M12.5 materialization. Strict no-writes: no `mcf.metric_contract` / `metric_contract_version` / `metric_variable_binding` / `metric_filter_clause` / `metric_computed_dimension_ref` / `metric_self_verification_fixture` / `metric_self_verification_result` / `certification_record` / `metric_publication_eligibility_result` / `metric_supersession` writes; no BCF concept-registry writes; no `contract.authoring_panel_rejection_log` writes; no legacy `metric.metric_definition` / `metric_knowledge` / `metric_binding` writes; M9 `FixtureStructuralCheckService` reused read-only for Checker validation only; M10 `MetricSelfVerificationService` NOT invoked; M11 `ReservoirIngestionService.markConsumedByPanel` FORBIDDEN in M12 v1 (M12.5 owns it after substrate write); `markRejected` only on all-reject. Hard assertions HA-1..HA-9 as implementation acceptance criteria. Materialization (MC + fixture + cert writes + legacy bridge) is the next gate M12.5 — explicitly scoped OUT here. NO bc-core edits this session. NO DDL apply this session. NO real model API calls. NO panel rows written. NO reservoir data ingested. NO M12.5 / M13 / M14+ work.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m12-authoring-panel-dbcp
---

# MCF M12 Metric Authoring Panel DBCP

## 1. Scope and grounding

Design the M12 panel orchestration service per the amended M12 preflight (`193c602`) + the wiring impact audit (`e725263`). The deliverable is `MetricAuthoringPanelService` — a synchronous, operator-triggered, three-model consensus engine that reads an M11 intake row and produces an immutable `mcf.metric_authoring_panel_run` + 3 × `mcf.metric_authoring_panel_transcript` rows. **No substrate write outside those two tables. No metric_contract write. No cert write. No fixture write. No verifier invocation. No legacy metric write.**

### 1.1 Source documents consumed (with concrete citations)

| Source | Role | Reference |
|---|---|---|
| M12 preflight (amended) | Decisions D-M12-1..D-M12-11; HA-1..HA-8; Post-BCF wiring boundary | `bc-docs-v3` `193c602` `docs/implementation/metric-context-framework-m12-authoring-panel-preflight.md` |
| Pre-M12 wiring audit | Legacy / MCF surface inventory + bridge boundary | `bc-docs-v3` `e725263` `docs/implementation/mcf-post-bcf-metric-workflow-wiring-impact.md` |
| MCF requirements §11.3 | Three-model panel pattern + 10-tool surface + 11 defect codes | `bc-docs-v3/docs/implementation/metric-context-framework-requirements.md` §11.3 (lines 860–953) |
| MCF requirements §11.3.6 Q35 | Parallel + independent transcripts (working position) | Same doc, line 1676 |
| MCF requirements §12.2 | Panel proposes fixtures; platform verifies; AI assertion of passage is not proof | Same doc, line 1014 |
| MCF requirements §3.8 | No-cross-framework-write-coupling (BCF / MCF substrate isolation) | Same doc |
| Build plan §M12 | T-shirt XL; R-09 (overbuilding); R-11 (workbench fingerprint algorithm drift) | `bc-docs-v3/docs/implementation/metric-context-framework-build-plan.md` lines 278–289 + 531 + 533 |
| M5 panel substrate DBCP | Live mapr / mapt shape; allowlists; substrate immutability triggers | `bc-docs-v3` `00435c0` `docs/implementation/metric-context-framework-m5-panel-substrate-dbcp.md` |
| M9 fixture substrate DBCP | Live `FixtureStructuralCheckService` for read-only Checker validation | `bc-docs-v3` `620e11d` `docs/implementation/metric-context-framework-m9-fixture-substrate-dbcp.md` |
| M10 verifier DBCP | Verifier service interface; explicitly NOT called from M12 | `bc-docs-v3` `ea8b708` `docs/implementation/metric-context-framework-m10-self-verification-result-dbcp.md` |
| M11 reservoir DBCP | Intake queue substrate + status transition methods | `bc-docs-v3` `42f702b` `docs/implementation/metric-context-framework-m11-reservoir-ingestion-dbcp.md` |
| M11 closeout | M11 substrate live + dormant; bc-core main `c359dc8` | `bc-docs-v3/docs/implementation/mcf-m11-apply-closeout.md` |
| Live `mcf.metric_authoring_panel_run` shape | 8 cols / 3 CHECKs / FK to substrate | Verified empirically via `bc-postgres` MCP at DBCP-write time (see §3.1) |
| Live `mcf.metric_authoring_panel_transcript` shape | 6 cols / 1 CHECK on `model_role_code IN ('maker','checker','moderator')` | Same |
| Live `mcf.workspace_tool_allowlist` shape | 6 cols (tool_uid PK + tool_code + tool_version + effective_from/to + metadata) | Same |
| Live `mcf.evidence_source_allowlist` shape | 6 cols (evidence_source_uid PK + source_code + source_version + effective_from/to + metadata) | Same |
| BCF orchestrator (PATTERN-ONLY reference) | `RegistryAuthoringOrchestrator` post-panel cert-then-dispatch — M12 reuses the read-panel-then-decide shape but DOES NOT call cert / dispatch | `bc-core/src/registry/registry-authoring-panel/registry-authoring-orchestrator.service.ts:44` (class) + `:58` (`runS1`) + `:274` (`readPanel`) |
| Live `ReservoirIngestionService` | M11 status transition methods + `REJECTED_REASON_MIN_LENGTH = 20` | `bc-core/src/registry/mcf/reservoir-ingestion.service.ts` (350 lines; class `ReservoirIngestionService`; methods `markConsumedByPanel` / `markRejected` / `markSuperseded`) |
| Live `FixtureStructuralCheckService` | M9 service for Checker C-FX-1..C-FX-11 read-only validation | `bc-core/src/registry/mcf/fixture-structural-check.service.ts` (866 lines; exports `FixtureContext` / `FixtureStructuralCheckResult` / `MissingMcvContextError`) |
| Live `MetricSelfVerificationService` | M10 verifier — NOT invoked from M12 (HA-3) | `bc-core/src/registry/mcf/metric-self-verification.service.ts` (373 lines) |
| Live `McfCertWriterService` | M4 cert writer — NOT invoked from M12 (HA-2); reserved for M12.5 | `bc-core/src/registry/mcf/mcf-cert-writer.service.ts:349` (class export) |
| Live `MetricDefinitionService` (legacy) | NOT imported from M12 (HA-1) | `bc-core/src/registry/metric-definition.service.ts` |
| Live `MetricDefinitionRepository` (legacy) | NOT imported from M12 (HA-1) | `bc-core/src/registry/metric-definition.repository.ts` |

### 1.2 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits this DBCP-author session | ✓ — design only |
| No DDL applied | ✓ |
| No real model API calls | ✓ — design only |
| No reservoir data ingested | ✓ — substrate dormant |
| No panel runs written | ✓ — substrate stays empty |
| No MC / fixture / cert / PE-MC / supersession rows | ✓ |
| No BCF data touched | ✓ |
| No M12.5 / M13 / M14+ work | ✓ |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

---

## 2. Accepted operator decisions (D-M12-1..D-M12-11)

| # | Decision | Locked |
|---|---|---|
| **D-M12-1** | Panel execution model — synchronous, operator-triggered (no async queue) | ACCEPTED |
| **D-M12-2** | Intake source — pending `mcf.metric_authoring_intake_queue` rows only; operator-direct submissions land via M11 CLI which writes to intake first | ACCEPTED |
| **D-M12-3** | Three-model role contract — Maker / Checker / Moderator; three distinct vendors; parallel transcripts | ACCEPTED |
| **D-M12-4** | Output scope v1 — proposal payload only (M12-B); no MC / fixture / cert writes | ACCEPTED |
| **D-M12-5** | Certification boundary — deferred to M12.5 (M4 cert writer NOT called from M12) | ACCEPTED |
| **D-M12-6** | Fixture authoring — panel proposes fixture shapes in consensus payload; NO INSERT; Checker reuses M9 `FixtureStructuralCheckService` read-only for C-FX validation | ACCEPTED |
| **D-M12-7** | Verifier invocation — M10 `MetricSelfVerificationService` NOT called from M12 | ACCEPTED |
| **D-M12-8** | Failure / rejection logging — `markRejected` only on all-reject; otherwise leave intake at `pending`; `markConsumedByPanel` FORBIDDEN in M12 v1 (M12.5 owns it after substrate write) | ACCEPTED |
| **D-M12-9** | Idempotency / retry — inherited from M11 status guards + M5 immutability triggers; no new retry orchestration | ACCEPTED |
| **D-M12-10** | Safety gates — hard prohibition list verified by HA-1..HA-8 | ACCEPTED |
| **D-M12-11** | Rejection log venue — **Option A** (reuse mapr `consensus_payload_json` + mapt `transcript_payload_json` + intake `status_reason_text`; ZERO new substrate); Option B only if DBCP query-pattern audit proves Option A insufficient; Option C forbidden | ACCEPTED — **Option A confirmed** for v1 (see §15) |

---

## 3. Current live substrate state

### 3.1 Verified empirically at DBCP-write time via `bc-postgres` MCP

After bc-core `c359dc8` + bc-docs-v3 `193c602`:

| Object | State |
|---|---|
| bc-core main | `c359dc8` (M11 evidence merged) |
| bc-docs-v3 main | `193c602` (M12 preflight amended) |
| `mcf.*` tables | **17 present, all 0 rows** |
| `mcf.metric_authoring_panel_run` | 8 cols (`panel_run_uid` PK + `workbench_fingerprint_hash` + `consensus_payload_json` + 4 reservoir-provenance fields + `created_at`); 3 CHECKs (`mapr_workbench_fp_hash_fmt_chk: ~ '^sha256:[0-9a-f]{64}$'`; `mapr_reservoir_all_or_none_chk`; `mapr_reservoir_confidence_band_chk: IN ('high','medium','low')`); FK to `contract.panel_output_record`; immutability trigger `trg_mapr_immutability` |
| `mcf.metric_authoring_panel_transcript` | 6 cols (`transcript_uid` PK + `panel_run_uid` FK + `model_role_code` + `model_identity_json` + `transcript_payload_json` + `created_at`); 1 CHECK (`mapt_model_role_chk: IN ('maker','checker','moderator')`); immutability trigger `trg_mapt_immutability` |
| `mcf.workspace_tool_allowlist` | 6 cols (`tool_uid` PK + `tool_code` + `tool_version` + `effective_from` + `effective_to` + `tool_metadata_json`); 0 rows (DBCP §11 specifies v1 tool seed) |
| `mcf.evidence_source_allowlist` | 6 cols (same shape as tool allowlist); 0 rows (DBCP §11 specifies v1 source seed) |
| `mcf.metric_authoring_intake_queue` | live + dormant per M11 closeout |
| `mcf.metric_self_verification_fixture` / `result` | live + dormant per M9 / M10 closeouts |
| `mcf.certification_record` | live + dormant per M4; 0 rows |
| BCF | `contract.panel_output_record` = 24 rows; `contract.authoring_panel_rejection_log` = 1 row (preserved) |

### 3.2 Substrate fitness for M12-B

All M12 writes target tables that already exist + have verified-PASS post-apply discipline per M5 closeout. **Zero new tables required for Option A.** Schema additions are inside existing JSONB columns (`consensus_payload_json`, `transcript_payload_json`) and are governed at service-side schema validation; no substrate CHECK on JSON shape (consistent with M5 substrate posture).

---

## 4. M12 ownership boundary

### 4.1 M12 MUST own

| # | Deliverable | Location |
|---|---|---|
| 1 | `MetricAuthoringPanelService` orchestrator with `runPanel(intakeQueueUid, opts, deps): Promise<RunPanelResult>` method | New `bc-core/src/registry/mcf/metric-authoring-panel.service.ts` |
| 2 | Role agent factories (Maker / Checker / Moderator) — model-provider-agnostic interface; mocked in tests; real model bindings injected via DI | New `bc-core/src/registry/mcf/panel-role-agent.interface.ts` + 3 role-specific factories |
| 3 | Workspace fingerprint algorithm `mcf-workbench-v1` (§10) — pure function | New `bc-core/src/registry/mcf/workspace-fingerprint.ts` |
| 4 | Consensus computation function — pure | New `bc-core/src/registry/mcf/panel-consensus.ts` |
| 5 | Grounding check function — pure | New `bc-core/src/registry/mcf/panel-grounding-check.ts` |
| 6 | Tool surface contracts (10 tools per MCF requirements §11.3.3) — interface only; implementations injected via DI | New `bc-core/src/registry/mcf/panel-tool-surface.types.ts` |
| 7 | `consensus_payload_json` + `transcript_payload_json` schema types + JSON-Schema validation | New `bc-core/src/registry/mcf/panel-payload.types.ts` |
| 8 | Per-vendor agent adapters (Anthropic / OpenAI / Google) — minimal v1; testable via in-process mocks | New `bc-core/src/registry/mcf/panel-agents/<vendor>-agent.adapter.ts` (3 files) |
| 9 | Unit + integration spec files | New `*.spec.ts` per service / pure-function / adapter |
| 10 | (CONDITIONAL on D-M12-11 escalation to Option B) DDL forward + rollback for `mcf.metric_authoring_panel_rejection_log` | NOT shipped by default; only if §15 escalation triggered |

### 4.2 M12 MUST NOT own

| # | Out-of-scope | Belongs to |
|---|---|---|
| 1 | MC / MCV / variable_binding / filter_clause / computed_dimension_ref writes | **M12.5** |
| 2 | Fixture INSERT (`mcf.metric_self_verification_fixture`) | M12.5 |
| 3 | Verification result INSERT (`mcf.metric_self_verification_result`) | M12.5 (after fixture INSERT) |
| 4 | Certification record INSERT (`mcf.certification_record`) | M12.5 (delegates to `McfCertWriterService`) |
| 5 | PE-MC evaluation (`mcf.metric_publication_eligibility_result`) | M13 |
| 6 | Publication path (`active` transition) | M14 |
| 7 | Supersession | M15 |
| 8 | Operator console (read or write) | M16 + M17 |
| 9 | Legacy metric write path deprecation (`POST /api/metric-catalog/definitions`) | M12.5 |
| 10 | Legacy / MCF read-fallback policy | M12.5 |
| 11 | bc-admin frontend metric API surface changes | M16 + M17 |
| 12 | Seed loader re-targeting from legacy to M11 intake | Separate operator-driven program (not a gate) |
| 13 | Real model vendor API key management beyond `.env` reads | Out of M12 scope; standard env-var pattern |
| 14 | `markConsumedByPanel` invocation | M12.5 |
| 15 | BCF substrate writes | NEVER (MCF reads BCF via `bcf.*` tool surface only) |

---

## 5. Execution flow (12 steps)  *(amended 2026-05-27 per B1 review patch)*

`MetricAuthoringPanelService.runPanel(intakeQueueUid, opts, deps)` executes the following sequence. **Critical**: per M5 §5 (1:1 composition) + active FK `fk_mapr_panel_run`, `contract.panel_output_record` MUST be written BEFORE `mcf.metric_authoring_panel_run`. M12 panel writes BOTH rows with the SAME `panel_run_uid`.

```
Step  1: SHORT TX (#A) — validate intake + in-flight guard
           - Read intake row by UID; assert status_code = 'pending'
           - Query existing mapr rows for same (reservoir_name, reservoir_entry_id)
             to detect in-flight or approved proposal (per §5.4 duplicate policy)
           - Generate new panel_run_uid (uuid)
           - COMMIT short tx
Step  2: Compute workspace fingerprint (workspace-fingerprint.ts) — pure, no tx
Step  3: Initialize 3 role agents (Maker / Checker / Moderator) with role-scoped prompts + tool-surface DI
Step  4: Parallel execution — all 3 agents run concurrently OUTSIDE any DB tx;
         each produces a transcript. No row locks held during agent calls.
Step  5: Run grounding check across all 3 transcripts (panel-grounding-check.ts) — pure
Step  6: Compute consensus (panel-consensus.ts) — produces verdict_code + defect_code (pure)
Step  7: SHORT TX (#B) — substrate writes (panel evidence)
           Step  7a: INSERT contract.panel_output_record
                       (panel_run_uid, stage_code='authoring', verdict_code per M5
                        convention single-token, verdict_payload_json BCF-shaped summary,
                        model_identity_json, agent_outputs_json, grounding_check_result,
                        quarantined mirror, sampling_status, policy_version, prompt_version)
           Step  7b: INSERT mcf.metric_authoring_panel_run with SAME panel_run_uid
                       (workspace_fingerprint_hash + consensus_payload_json
                        + 4 reservoir-provenance fields copied from intake row)
           Step  7c: INSERT 3 × mcf.metric_authoring_panel_transcript (one per role)
           COMMIT short tx (atomic; all 5 rows persist together or none)
Step  8: SHORT TX (#C) — intake status transition (only on all-reject)
           - if consensus.verdict_code = 'REJECT_DEFECT' → ReservoirIngestionService.markRejected(uid, reason, {tx})
           - else (APPROVE_FOR_DRAFT / OPERATOR_REVIEW / mid-run failure) → no-op
           - markConsumedByPanel is FORBIDDEN (HA-6) — M12.5 owns it
           COMMIT short tx
Step  9: Return { panel_run_uid, verdict_code, defect_code, consensus_payload }
```

**Why three SHORT transactions (not one long-lived tx):** model calls in Step 4 may take 30–180 seconds per role. Holding any DB transaction (or row lock) across that window blocks the connection pool + creates the long-tx anti-pattern. Splitting into tx #A (validation) → external work → tx #B (substrate writes) → tx #C (intake transition) keeps DB transactions short while preserving correctness via the in-flight guard (§5.4) + M11 status-transition CAS guard (`WHERE status_code = 'pending'` in the UPDATE) + intake `status_code` still being `'pending'` at Step 8 time (verified by `markRejected`'s own internal SELECT).

### 5.1 Per-step contract details  *(amended)*

**Step 1 — SHORT TX (#A): validate intake + in-flight guard.** Inside a brief Drizzle tx (`deps.txFactory.shortTx(...)`):
- `SELECT status_code, reservoir_name, reservoir_entry_id, ... FROM mcf.metric_authoring_intake_queue WHERE intake_queue_uid = ${uid}` (no row lock — concurrency safety comes from M11's status-transition CAS guard)
- If `status_code ≠ 'pending'`, throw `InvalidStatusTransitionError` (re-export from M11)
- **In-flight / duplicate-proposal guard** per §5.4: query `mcf.metric_authoring_panel_run` for rows where `(reservoir_name, reservoir_entry_id) = (intake.reservoir_name, intake.reservoir_entry_id)` AND `consensus_payload_json->>'verdict_code'` is `'APPROVE_FOR_DRAFT'` or any other open/in-flight indicator; refuse if any exists unless `opts.allowRetry === true`
- Generate `panel_run_uid = crypto.randomUUID()`
- COMMIT short tx
- No `FOR UPDATE` lock is held — replaced by the in-flight guard (§5.4) + M11's CAS guard at Step 8.

**Step 2 — Workspace fingerprint.** Compute `mcf-workbench-v1` hash per §10. Pure function; no DB tx. Substrate constraint `mapr_workbench_fp_hash_fmt_chk` requires `^sha256:[0-9a-f]{64}$` — algorithm output format must match byte-for-byte.

**Step 3 — Initialize agents.** Three agents per `deps.agentFactory` — DI ensures testability. Each agent receives:
- Role-scoped prompt (Maker / Checker / Moderator; templates in `prompts/m12-panel-{role}.v1.md` — DBCP §7.2)
- Tool surface (`PanelToolSurface` interface from `panel-tool-surface.types.ts`)
- Operator context text (from `opts.operatorContextText`)
- Intake candidate payload (from Step 1 result)
- Token budget (per-vendor; see §7.5)
- Per-vendor timeout

**Step 4 — Parallel execution OUTSIDE any DB tx.** `Promise.allSettled([maker.run(), checker.run(), moderator.run()])`. `allSettled` (not `all`) so a single vendor failure doesn't abort the other two. Each agent returns `RoleTranscript` per §9. Per-vendor timeout enforced inside the agent's `run()` method. **No DB connection held, no row lock held, no tx open during this step.**

**Step 5 — Grounding check.** Pure function. For each role transcript, every `claim` in the agent's proposal MUST trace to a tool-call entry in the agent's `transcript_payload_json.tool_calls`. Mismatch → `grounding_check_passed = false` + per-violation entry in `grounding_violations`. Algorithm specified in `panel-grounding-check.ts` per §7.4.

**Step 6 — Consensus.** Pure function. Per MCF requirements §11.3.5 + role contract §7 + M5 verdict convention (§8.1):
- All 3 `APPROVE_FOR_DRAFT` AND grounding pass → consensus `verdict_code='APPROVE_FOR_DRAFT'`, `defect_code=null`
- All 3 `REJECT_DEFECT` → consensus `verdict_code='REJECT_DEFECT'`, `defect_code=<majority MC_DEFECT_*>` (ties broken by Maker → Checker → Moderator priority for deterministic reproduction)
- Otherwise (mixed / grounding fail / any timeout / partial transcripts) → consensus `verdict_code='OPERATOR_REVIEW'`, `defect_code=null`, `operator_review_reason ∈ {mixed_verdicts, grounding_check_failed, partial_transcripts, vendor_timeout, vendor_outage, cost_ceiling_exceeded, workspace_fingerprint_mismatch}`

**Step 7 — SHORT TX (#B): substrate writes (atomic).** Single Drizzle tx that COMMITs all 5 rows together OR rolls back. The 1:1 composition (M5 §5 line 183) + active `fk_mapr_panel_run` FK make this an atomicity requirement:

**Step 7a — INSERT `contract.panel_output_record`** (MANDATORY; written BEFORE mapr per active FK):
- `panel_run_uid` = generated in Step 1
- `stage_code` = `'authoring'` (per `panel_output_record_stage_code_chk` active enum + matches the 24 live BCF rows' convention)
- `verdict_code` ∈ (`'APPROVE_FOR_DRAFT'`, `'OPERATOR_REVIEW'`, `'REJECT_DEFECT'`) per M5 §12.2 single-token convention. **Not** the legacy BCF `'REJECT'` (which would trigger `panel_output_record_reject_defect_code_chk` requiring a BCF defect code from `DEF_PLACEHOLDER`/`IDENT_*`/`PROV_*`/`STRUCT_*` — incompatible with MCF defect codes per D-M5-7).
- `verdict_payload_json` = BCF-shaped summary per M5 §12.2: `{per_model_verdicts:[{model_role_code, verdict_code, defect_codes[], confidence_score?}], consensus:{verdict_code, consensus_method, rationale_text:≥40 chars}, grounding:{claims_total, claims_grounded, claims_quarantined}}`. MCF-specific defect detail does NOT live here; MCF defect detail lives in `mcf.metric_authoring_panel_run.consensus_payload_json` per D-M5-7 + §8 of this DBCP.
- `model_identity_json` = `{models:[<vendor identity per role>]}` (3 entries; see §7.3 for shape)
- `agent_outputs_json` = summary of per-role outputs (full transcripts go to mapt, not here)
- `grounding_check_result` ∈ (`'pass'`, `'quarantined'`) per `panel_output_record_grounding_chk`; `quarantined = (grounding_check_result = 'quarantined')` per `panel_output_record_quarantine_mirror_chk`
- `sampling_status` ∈ (`'not_sampled'`, `'sampled_for_calibration'`, `'sample_routed_to_operator'`) per `panel_output_record_sampling_chk`
- `policy_version` = `'mcf-panel-v1'`
- `prompt_version` = `'m12-panel-v1'`

**Step 7b — INSERT `mcf.metric_authoring_panel_run`** (with same `panel_run_uid`):
- `workbench_fingerprint_hash` from Step 2 (must match `^sha256:[0-9a-f]{64}$`)
- 4 reservoir-provenance fields all-NOT-NULL (copied from intake row; satisfies `mapr_reservoir_all_or_none_chk` + addendum guardrail #6)
- `reservoir_confidence_band` ∈ (`'high'`, `'medium'`, `'low'`) (already enforced by intake substrate; passed through)
- `consensus_payload_json` schema validated service-side BEFORE INSERT per §8

**Step 7c — INSERT 3 × `mcf.metric_authoring_panel_transcript`** (one per role):
- `mapt_model_role_chk` already requires `model_role_code IN ('maker','checker','moderator')`
- `panel_run_uid` FK references the mapr row written in Step 7b
- `transcript_payload_json` schema validated service-side BEFORE INSERT per §9

**Step 7 commits atomically** — either all 5 rows persist (1 panel_output_record + 1 mapr + 3 mapt) or none.

**Step 8 — SHORT TX (#C): intake status transition (only on all-reject).** New brief Drizzle tx:
- All-reject (consensus `verdict_code='REJECT_DEFECT'`): `await reservoirIngestionService.markRejected(intakeQueueUid, composeRejectionReason(consensus), { tx })` — reason text must be ≥ 20 chars per M11 substrate CHECK `maiq_rejected_status_requires_reason_chk`. M11's internal SELECT-then-UPDATE-with-status-guard handles concurrency safety; if intake has already been transitioned (e.g. by a concurrent panel run that won the race), `markRejected` raises `InvalidStatusTransitionError` and the panel evidence (Step 7 rows) is preserved regardless.
- All other outcomes: no-op (intake stays at `pending`)
- **NEVER call `markConsumedByPanel`** (HA-6). Service code must not contain this call site.
- COMMIT short tx

**Step 9 — Return.** Service returns `{ panel_run_uid, verdict_code, defect_code, consensus_payload }` for caller (test / integration / future M12.5 service).

### 5.2 Transaction scope summary

| Step | Transaction | Purpose | Duration |
|---|---|---|---|
| 1 | SHORT TX #A | Validate intake + in-flight guard + generate uuid | ms (single SELECT + COMMIT) |
| 2-6 | NO TX | Workspace fingerprint + agent calls + grounding + consensus (pure / external) | up to 180s × 3 (parallel) |
| 7 | SHORT TX #B | Atomic INSERT of 5 rows (panel_output_record + mapr + 3 × mapt) | ms |
| 8 | SHORT TX #C | Conditional `markRejected` only on all-reject | ms |
| 9 | NO TX | Return result | n/a |

**No DB transaction is open during agent calls (Step 4).** This is intentional — model-API latency variance must not block the connection pool. Concurrency safety is provided by the in-flight guard (§5.4) + M11 status-transition CAS guard, not by row locks.

### 5.3 Error semantics summary  *(amended)*

| Failure mode | Substrate effect | Intake status | Return |
|---|---|---|---|
| Invalid intake (status ≠ pending) | None | unchanged | throw `InvalidStatusTransitionError` (Step 1) |
| In-flight / duplicate-approved proposal (per §5.4) | None | unchanged | throw `DuplicateProposalInFlightError` (Step 1; unless `opts.allowRetry === true`) |
| Workspace fingerprint compute error | None | unchanged | throw `WorkspaceFingerprintError` (Step 2) |
| All 3 agents timeout / vendor outage | panel_output_record + mapr + mapt × 3 INSERTed at Step 7 with `verdict_code='OPERATOR_REVIEW'` + `operator_review_reason='vendor_outage'`; partial transcripts captured | unchanged (pending) | return verdict |
| Single agent failure | panel_output_record + mapr + mapt × ≤ 3 INSERTed; missing role has `transcript_payload_json.status_code='vendor_failure'` | unchanged | return `OPERATOR_REVIEW` |
| Cost ceiling exceeded mid-run | Same as agent failure | unchanged | `OPERATOR_REVIEW` |
| Grounding check fail (claim ≠ tool call) | panel_output_record + mapr + mapt × 3 INSERTed; `grounding_check_passed=false` + violations | unchanged | `OPERATOR_REVIEW` |
| Successful all-approve + grounding pass | panel_output_record + mapr + mapt × 3 INSERTed; verdict_code=`APPROVE_FOR_DRAFT` | unchanged (M12.5 will transition) | `APPROVE_FOR_DRAFT` |
| Successful all-reject | panel_output_record + mapr + mapt × 3 INSERTed; verdict_code=`REJECT_DEFECT`; intake transitioned to `rejected` via `markRejected` | `rejected` | `REJECT_DEFECT` + `defect_code` |
| Step 7 FK violation (panel_output_record row missing) | Impossible in M12 — Step 7a writes it before Step 7b; FK is satisfied by construction | unchanged | n/a |

### 5.4 In-flight / duplicate-proposal policy  *(new sub-section; replaces FOR UPDATE)*

Because Steps 4–6 happen outside any DB tx and intake status stays `pending` on `APPROVE_FOR_DRAFT` and `OPERATOR_REVIEW`, a naive race could produce two simultaneous panel runs against the same intake row.

**Guard at Step 1** (before launching agents):

```sql
SELECT panel_run_uid, consensus_payload_json->>'verdict_code' AS verdict
FROM mcf.metric_authoring_panel_run
WHERE reservoir_name = ${intake.reservoir_name}
  AND reservoir_entry_id = ${intake.reservoir_entry_id}
ORDER BY created_at DESC
LIMIT 5
```

Refuse the new panel run if ANY of the following is true (unless `opts.allowRetry === true`):
- An existing mapr row has `verdict_code = 'APPROVE_FOR_DRAFT'` (proposal exists; pending M12.5 materialization)
- An existing mapr row was created in the last 600 seconds (10-minute in-flight window; covers worst-case 3 × 180s agent runs + buffer)

Throw `DuplicateProposalInFlightError` with the existing `panel_run_uid` for forensic lookup.

**`opts.allowRetry === true`** is the explicit operator override for legitimate re-runs (e.g. after a vendor-outage `OPERATOR_REVIEW` result that the operator wants to re-attempt). This flag is exposed in the future M16 audit-UI / M12.5 service; M12 v1's service constructor accepts it.

**Why this guard works**: the M5 mapr is append-only (`trg_mapr_immutability`), so historical rows are the authoritative concurrency signal. The 10-minute window catches in-flight runs without needing distributed locking. APPROVE_FOR_DRAFT rows persist until M12.5 materializes (and then `markConsumedByPanel` transitions intake to `consumed_by_panel`, removing it from future panel eligibility per Step 1's status assert).

---

## 6. BCF panel pattern reuse boundary

### 6.1 Reuse — pattern only, not code

The BCF orchestrator (`bc-core/src/registry/registry-authoring-panel/registry-authoring-orchestrator.service.ts:44`) provides the **read-panel-then-decide** template. M12 inherits the shape but not the actions:

| BCF pattern | M12 inheritance | Reason |
|---|---|---|
| `RegistryAuthoringOrchestrator.readPanel(panelRunUid)` (line 274) reads `contract.panel_output_record` verdict + payload | M12 reads `mcf.metric_authoring_intake_queue` + initiates a NEW panel run; does NOT read pre-existing panel runs | Different timing — BCF reads existing panel verdicts; M12 creates them |
| `runS1` (line 58) post-panel cert issuance + F3 dispatch | M12 does NOT call cert writer; does NOT dispatch F3 ops | M12-B is proposal-only (D-M12-4) |
| `completeHighRiskConfirm` (line 155) | NOT inherited — no high-risk operator-confirm in M12 (publication is M14) | |
| Closed-enum verdict shape (`APPROVE` / `OPERATOR_REVIEW` / `REJECT_*`) | INHERITED in form; MCF uses `APPROVE_FOR_DRAFT` (not `APPROVE`); MCF defect codes per MCF requirements §11.3.4 | Vocabulary differs |
| Per-agent transcript pattern | INHERITED in shape; M12 writes to `mcf.metric_authoring_panel_transcript` (not `contract.panel_output_record.agent_outputs_json`); 3 rows per run | M5 substrate is MCF-scoped per requirements §3.8 |
| Workspace-fingerprint discipline | INHERITED; M12 implements `mcf-workbench-v1` (§10) | R-11 in build plan |

### 6.2 Forbidden BCF carryovers (HA enforcement)

| BCF pattern | Why forbidden in M12 | Enforced by |
|---|---|---|
| Writing to `contract.panel_output_record` with BCF-only `verdict_code='REJECT'` + BCF defect codes | MCF uses single-token `'REJECT_DEFECT'` per M5 §12.2 — bypasses the BCF defect-code CHECK; MCF defect detail goes to `mapr.consensus_payload_json` per D-M5-7. Writing the shared panel-substrate row itself with MCF-scoped `stage_code='authoring'` + MCF verdict_code IS allowed and required by FK | M5 §12.2; B1 review patch |
| Writing to `contract.authoring_panel_rejection_log` | BCF-scoped enum (no `mc` member); D-M12-11 chose Option A reuse-of-mapr/mapt | HA-5; D-M12-11 §15 |
| BCF C5 cert layer (`FrameworkApprovalService.issueRegistryShapeCertification`) | MCF cert is M4 (different action_codes); M12-B writes no certs anyway | HA-2 |
| BCF F3 dispatch (`createEntity` / `createBusinessConcept` / `registerCharacteristic`) | MCF substrate writes happen in M12.5 via `McfCertWriterService.createMetricDraft` in one TX, not via F3-style per-op dispatch | M12 does not import F3 dispatch |
| BCF v1 packet-in / verdict-out model | MCF requirements §11.3 explicitly rejects this; MCF is workbench-doctrine from start | DBCP §5 execution flow uses workbench tools, not bundled input |
| BCF tool surface (`bcf.registry_collision_probe` / alias probes / lifecycle history) | These are vocabulary-authoring tools; MCF tools per §11 are different | §11 enumerates MCF tool surface |

### 6.3 NO BCF concept-registry / rejection-log writes from M12 — locked  *(amended per B1 review patch)*

`contract.panel_output_record` is **shared substrate** (per M5 D-M5-B hybrid composition + active FK `fk_mapr_panel_run` requiring 1:1 composition per M5 §5). M12 panel runs MUST write to it (with `stage_code='authoring'` + M5 single-token verdict_code convention; MCF-specific defect detail stays in `mcf.metric_authoring_panel_run.consensus_payload_json` per D-M5-7). This is NOT a BCF write — it is a write to the SHARED panel-substrate that BCF and MCF both use, scoped via the `stage_code` enum.

M12 v1 panel service does NOT write to:
- `contract.business_entity` / `contract.business_concept` / any `concept_registry.*` table (BCF concept writes — FORBIDDEN)
- `contract.authoring_panel_rejection_log` (BCF rejection log; MCF uses `mapr.consensus_payload_json` per D-M12-11 Option A)
- BCF certification_record rows (MCF cert is M4-scoped action_codes; M12 writes none anyway)
- BCF lifecycle tables (registry transitions are BCF's)

Enforced by HA-4 (BCF reads only via `bcf.*` tool surface) + amended HA-5 (writes only to expected surfaces; see §16).

---

## 7. Three-model role contract

### 7.1 Roles + responsibilities (Maker / Checker / Moderator)

| Role | Responsibility | Output in transcript |
|---|---|---|
| **Maker** | Propose the candidate MC: formula AST + variable bindings + grain + filters + temporal gate + computed_dim_refs + ≥ 1 proposed fixture (when proposing APPROVE_FOR_DRAFT) | `proposal_payload` (full MC sketch) + per-claim grounding citations + verdict + defect_code (if rejected) |
| **Checker** | Independently re-derive a proposal from the same workspace; verify Maker's grounding citations; validate proposed fixture C-FX-1..C-FX-11 structurally via M9 `FixtureStructuralCheckService.runStructuralChecks(context, body)` (read-only) | `verification_payload` (Checker's independent proposal + cross-check vs Maker + C-FX result for proposed fixture) + per-claim grounding citations + verdict + defect_code |
| **Moderator** | Aggregate Maker + Checker; produce final consensus verdict + defect code; document divergence if Maker ≠ Checker | `consensus_payload` (final verdict + tie-break rationale + per-role role-summary) + per-claim grounding citations + verdict + defect_code |

### 7.2 Per-role prompt templates

| File | Purpose |
|---|---|
| `bc-core/src/registry/mcf/prompts/m12-panel-maker.v1.md` | Maker system prompt — emphasize proposal completeness + grounding |
| `bc-core/src/registry/mcf/prompts/m12-panel-checker.v1.md` | Checker system prompt — emphasize independent re-derivation + grounding verification + fixture C-FX |
| `bc-core/src/registry/mcf/prompts/m12-panel-moderator.v1.md` | Moderator system prompt — emphasize consensus computation + tie-break determinism |

Prompt version is captured in `consensus_payload_json.prompt_version` (e.g. `m12-panel-v1`). Bump on any wording change. The prompt-version string is part of the workspace fingerprint (§10).

### 7.3 Vendor identity capture

`mcf.metric_authoring_panel_transcript.model_identity_json` schema:

```jsonc
{
  "vendor": "anthropic" | "openai" | "google",
  "model_id": "claude-opus-4.7" | "gpt-5" | "gemini-2.5-pro",
  "model_version": "<vendor-provided version string>",
  "api_endpoint": "<obfuscated; first 30 chars only>",
  "tier": "standard" | "enterprise",
  "request_timestamp": "<ISO 8601>",
  "response_timestamp": "<ISO 8601>",
  "total_tokens_used": 12345,
  "finish_reason": "stop" | "length" | "tool_calls" | "error",
  "vendor_request_id": "<vendor request id for forensic lookup>"
}
```

v1 default vendor assignment (operator-configurable via env vars `MCF_M12_MAKER_MODEL` / `MCF_M12_CHECKER_MODEL` / `MCF_M12_MODERATOR_MODEL`):
- Maker = Anthropic / claude-opus-4.7
- Checker = OpenAI / gpt-5
- Moderator = Google / gemini-2.5-pro

Three-vendor rule per MCF requirements §11.3.5 — DBCP enforces 3 DISTINCT vendors at service-init time; if 2 roles use the same vendor (operator misconfiguration), service throws `ConfigurationError` (re-export from `mcf-cert-writer.service.ts:86`).

### 7.4 Transcript status codes (per-role outcomes)

| `status_code` (in `transcript_payload_json.status_code`) | Meaning |
|---|---|
| `completed_with_verdict` | Agent ran to completion + produced a verdict |
| `vendor_timeout` | Agent timed out per-vendor timeout (default 180s; operator-configurable) |
| `vendor_failure` | Vendor API returned non-2xx / connection failure / rate limit |
| `cost_ceiling_exceeded` | Agent stopped mid-run because cumulative token use hit per-vendor budget |
| `tool_call_failure` | A tool call returned an unrecoverable error; agent could not proceed |
| `grounding_check_skipped` | Agent returned APPROVE_FOR_DRAFT but transcript had zero claims (degenerate; routes to OPERATOR_REVIEW at consensus) |

### 7.5 Cost ceiling + timeout behavior

- **Per-vendor timeout (default 180s)**: configurable via `MCF_M12_VENDOR_TIMEOUT_MS`. Agent's `run()` enforces internally via `Promise.race([agentWork, timeoutPromise])`.
- **Per-run token budget (default 100,000 tokens per role)**: configurable via `MCF_M12_PER_ROLE_TOKEN_BUDGET`. Agent tracks cumulative tokens; exceeds → `status_code='cost_ceiling_exceeded'`.
- **Per-month service budget (default 10,000,000 tokens total)**: tracked in-memory by service singleton + persisted to operator-readable counter. Exceeded → service refuses new `runPanel` calls with `CostCeilingExceededError`.
- **Three-vendor failure mode**: if all 3 roles produce non-`completed_with_verdict` status → mapr writes `verdict_code='OPERATOR_REVIEW'`, `operator_review_reason='vendor_outage'`, mapt × 3 capture whatever partial transcripts exist.

---

## 8. `consensus_payload_json` schema (canonical v1 — locked)

This is the **input contract for M12.5** (HA-7). Schema changes are version-bumped via `panel_algorithm_version`; no breaking-shape changes within a major version.

### 8.1 Top-level shape

```jsonc
{
  "panel_algorithm_version": "mcf-panel-v1",
  "prompt_version": "m12-panel-v1",
  "verdict_code": "APPROVE_FOR_DRAFT" | "OPERATOR_REVIEW" | "REJECT_DEFECT",
  "defect_code": "MC_DEFECT_GRAIN_INCOHERENT" | "MC_DEFECT_VARIABLE_UNBINDABLE" | "MC_DEFECT_FORMULA_TYPE_MISMATCH" | "MC_DEFECT_UNIT_PROMOTION" | "MC_DEFECT_CROSS_GRAIN_AGGREGATION" | "MC_DEFECT_IDENTITY_COLLISION" | "MC_DEFECT_TEMPORAL_GATE_INCOHERENT" | "MC_DEFECT_COMPUTED_DIMENSION_UNRESOLVED" | "MC_DEFECT_BC_SUPERSEDED" | "MC_DEFECT_PE_MC_1_UNGROUNDED" | "MC_DEFECT_TRANSCRIPT_FABRICATION" | null,
  "defect_code_registry_version": "v1",
  "operator_review_reason": "mixed_verdicts" | "grounding_check_failed" | "partial_transcripts" | "vendor_timeout" | "vendor_outage" | "cost_ceiling_exceeded" | "workspace_fingerprint_mismatch" | null,
  "grounding_check_passed": true | false,
  "grounding_violations": [
    {
      "role": "maker" | "checker" | "moderator",
      "claim_id": "<uuid>",
      "claim_text": "<verbatim claim>",
      "reason": "no_matching_tool_call" | "tool_response_did_not_contain_cited_value" | "..."
    }
  ],
  "per_role_summary": [
    {
      "role": "maker" | "checker" | "moderator",
      "verdict_code": "APPROVE_FOR_DRAFT" | "OPERATOR_REVIEW" | "REJECT_DEFECT",
      "defect_code": "MC_DEFECT_*" | null,
      "tool_call_count": 12,
      "claim_count": 8,
      "transcript_uid": "<uuid — FK to mapt row for forensic lookup>"
    }
  ],
  "candidate_proposal": { /* per §8.2 — empty object {} when verdict ≠ APPROVE_FOR_DRAFT */ },
  "intake_back_reference": {
    "intake_queue_uid": "<uuid>",
    "reservoir_name": "seed_metrics" | "metric_definition" | "operator_direct",
    "reservoir_entry_id": "<source-specific id>",
    "reservoir_confidence_band": "high" | "medium" | "low"
  }
}
```

### 8.1a Verdict code convention — single-token per M5  *(amended per M2 review patch)*

Per M5 DBCP §12.2 (lines 700–720), MCF verdict codes use the **single-token convention** everywhere — `'APPROVE_FOR_DRAFT'` / `'OPERATOR_REVIEW'` / `'REJECT_DEFECT'`. The defect detail goes in a SEPARATE `defect_code` field whose value is drawn from the MC defect registry (`MC_DEFECT_GRAIN_INCOHERENT` etc. per MCF requirements §11.3.4) pinned at registry version `'v1'` per `mcf_v1.consensus_requirement_json.panel_discipline.defect_code_registry_version`.

**Why single-token (not templated `'REJECT_<defect_code>'`)**:
- `contract.panel_output_record_reject_defect_code_chk` fires ONLY when `verdict_code = 'REJECT'` (exact); MCF's `'REJECT_DEFECT'` token bypasses it, allowing MCF defect codes to live in `consensus_payload_json` instead of the BCF-only `verdict_payload_json` enum
- M5 §12.2 already specifies this for the shared substrate; M12 must align
- Forensic queries (`WHERE verdict_code = 'REJECT_DEFECT' AND defect_code = 'MC_DEFECT_GRAIN_INCOHERENT'`) are cleaner than parsing templated tokens
- The value MUST match BYTE-FOR-BYTE in both `contract.panel_output_record.verdict_code` and `mcf.metric_authoring_panel_run.consensus_payload_json->>'verdict_code'`

The Step 7a INSERT writes `contract.panel_output_record.verdict_code = consensus.verdict_code` directly (single token). The same value appears in `mapr.consensus_payload_json.verdict_code` (Step 7b). Per-role transcripts (`mapt.transcript_payload_json.verdict_code`) also use the single-token form.

### 8.2 `candidate_proposal` (Maker's accepted proposal; empty when verdict ≠ APPROVE_FOR_DRAFT)

```jsonc
{
  "candidate_name": "days_sales_outstanding",
  "display_name": "Days Sales Outstanding",
  "description_text": "<operator-readable prose>",
  "formula_ast": { /* §7.2 of MCF requirements — closed taxonomy */ },
  "variable_bindings": [
    {
      "variable_role_code": "numerator",
      "role_kind_code": "ratio_numerator",
      "bound_business_concept_id": "<uuid; resolved via bcf.* tool surface; NO physical FK to concept_registry per §3.8>",
      "bound_entity_id": "<uuid; same>",
      "constant_value_json": null,
      "representation_term_snapshot": "amount",
      "unit_code_snapshot": "USD",
      "data_type_snapshot": "decimal"
    }
    /* ... one entry per variable; column names match mcf.metric_variable_binding live schema verified empirically */
  ],
  "filter_clauses": [
    /* per mcf.metric_filter_clause shape */
  ],
  "computed_dimension_refs": [
    /* per mcf.metric_computed_dimension_ref shape */
  ],
  "temporal_gate": {
    "temporal_gate_shape_code": "instantaneous" | "trailing_window" | "as_of" | "...",
    "temporal_gate_params_json": { /* per mcf.metric_contract_version */ }
  },
  "grain": {
    "grain_entity_id": "<uuid; bcf.* tool-resolved>"
  },
  "proposed_fixtures": [
    {
      "fixture_label": "primary_pass_fixture",
      "section_a_inputs_json": { /* per MCF requirements §12.4 */ },
      "section_b_expected_output_json": { /* per §12.4 */ },
      "section_c_resolver_config_json": { /* per §12.4 */ },
      "checker_c_fx_result": {
        "passed": true | false,
        "defects": [ /* per FixtureStructuralCheckResult.defects */ ]
      }
    }
    /* ≥ 1 fixture required for APPROVE_FOR_DRAFT per D-M12-6 */
  ],
  "grounding_evidence": [
    {
      "claim_id": "<uuid>",
      "claim_text": "<from agent's proposal>",
      "tool_call_id": "<from agent's transcript>",
      "tool_code": "evidence.retrieve" | "bcf.read_business_concept" | "...",
      "source_uri": "<from tool response>"
    }
  ],
  "unresolved_questions": [
    /* Optional: items the panel surfaces for operator review when consensus = APPROVE_FOR_DRAFT but ambiguity remains */
  ]
}
```

### 8.3 M12.5 consumption contract

**`candidate_proposal` is what M12.5 reads.** M12.5's `MetricAuthoringMaterializationService` will:
1. SELECT `consensus_payload_json` from `mcf.metric_authoring_panel_run` where `verdict_code='APPROVE_FOR_DRAFT'`
2. Read `candidate_proposal.{formula_ast, variable_bindings, filter_clauses, computed_dimension_refs, temporal_gate, grain}`
3. Call `McfCertWriterService.createMetricDraft(...)` with that data + `panel_run_uid` as authoring evidence
4. Write the first `proposed_fixtures[0]` row as `mcf.metric_self_verification_fixture`
5. Invoke `MetricSelfVerificationService.verifyFixture(fixtureUid, deps)` — write result row
6. THEN call `ReservoirIngestionService.markConsumedByPanel(intake_queue_uid)` to transition intake

DBCP §X for M12.5 specifies this; M12 DBCP only locks the input contract here.

### 8.4 Schema validation discipline

- Service-side: JSON-Schema validator runs on `consensus_payload_json` BEFORE INSERT. Schema literal lives in `bc-core/src/registry/mcf/panel-payload.schema.json` (loaded at service init).
- Substrate-side: NO CHECK on JSON shape (consistent with M11 / M5 substrate posture — substrate CHECKs reserved for safety, not typing).
- Test-side: HA-7 enforced via round-trip test (produce known shape; mock materialization deserializes successfully).

---

## 9. `transcript_payload_json` schema (per-role)

`mcf.metric_authoring_panel_transcript.transcript_payload_json` (one row per role per panel run; immutability enforced by `trg_mapt_immutability`):

```jsonc
{
  "panel_algorithm_version": "mcf-panel-v1",
  "role": "maker" | "checker" | "moderator",
  "status_code": "completed_with_verdict" | "vendor_timeout" | "vendor_failure" | "cost_ceiling_exceeded" | "tool_call_failure" | "grounding_check_skipped",
  "tool_calls": [
    {
      "tool_call_id": "<uuid>",
      "tool_code": "bcf.search_entity" | "bcf.read_business_concept" | "evidence.retrieve" | "..." (10 tools per MCF requirements §11.3.3),
      "tool_version": "<from workspace_tool_allowlist.tool_version>",
      "request_json": { /* tool-specific request shape */ },
      "response_json": { /* tool-specific response shape */ },
      "started_at": "<ISO 8601>",
      "completed_at": "<ISO 8601>",
      "latency_ms": 234,
      "error": null | { "code": "...", "message": "..." }
    }
  ],
  "reasoning_trace": [
    {
      "step_id": "<int monotonic>",
      "reasoning_text": "<verbatim model output>",
      "associated_tool_call_ids": [/* references */]
    }
  ],
  "verdict_code": "APPROVE_FOR_DRAFT" | "OPERATOR_REVIEW" | "REJECT_DEFECT",
  "defect_code": "MC_DEFECT_*" | null,
  "claims": [
    {
      "claim_id": "<uuid>",
      "claim_text": "<verbatim>",
      "supporting_tool_call_ids": [/* references — used by grounding check */]
    }
  ],
  /* Role-specific payload — exactly ONE of the next 3 keys is populated per role */
  "proposal_payload": { /* Maker only — see §8.2 candidate_proposal shape (per-Maker draft) */ },
  "verification_payload": { /* Checker only — independent proposal + cross-check vs Maker + C-FX result */ },
  "consensus_payload": { /* Moderator only — final verdict + tie-break rationale + per-role summary */ }
}
```

### 9.1 Schema validation

Same discipline as §8.4 — service-side JSON-Schema (`panel-transcript.schema.json`); no substrate JSON CHECK; HA-validated via round-trip test.

---

## 10. Workspace fingerprint algorithm `mcf-workbench-v1`

### 10.1 Canonical inputs (locked byte-order)

The fingerprint is the sha256 of the concatenated JCS-canonical (`mcf-jcs.ts`) UTF-8 bytes of the following 7-element ORDERED JSON array. The order is normative — changing it breaks reproducibility.

```jsonc
[
  /* 0 */ "mcf-workbench-v1",
  /* 1 */ "<tool_allowlist_snapshot_hash>",       // sha256 of (rows in workspace_tool_allowlist where effective_to IS NULL OR effective_to > now()), ordered by tool_code ASC then tool_version ASC, JCS-canonicalized
  /* 2 */ "<evidence_allowlist_snapshot_hash>",   // sha256 of (rows in evidence_source_allowlist where effective_to IS NULL OR effective_to > now()), ordered by source_code ASC then source_version ASC, JCS-canonicalized
  /* 3 */ "<bcf_registry_snapshot_id>",           // BCF-provided snapshot id at run start (string handle; read-only)
  /* 4 */ "<operator_context_text_hash>",         // sha256 of UTF-8 bytes of opts.operatorContextText ?? "" (empty string allowed; hash of empty string is well-defined)
  /* 5 */ "<policy_version>",                     // "mcf-panel-v1" — bumped when authority model changes
  /* 6 */ "<prompt_version>"                      // "m12-panel-v1" — bumped when any of the 3 role prompts change
]
```

### 10.2 Output format

```
sha256:<64-lowercase-hex-chars>
```

Matches substrate constraint `mapr_workbench_fp_hash_fmt_chk` (`^sha256:[0-9a-f]{64}$`) byte-for-byte.

### 10.3 Determinism contract

Given identical inputs (same allowlist rows + same BCF snapshot + same operator context + same versions), the fingerprint is invariant across runs / processes / machines. Mismatch across the 3 roles in a single panel run → consensus invalid → `OPERATOR_REVIEW` with reason `workspace_fingerprint_mismatch` (additional reason added to §5.3 enum).

### 10.4 R-11 mitigation

`mcf-workbench-v1` is the SINGLE algorithm constant. Both substrate (no enforcement — JSONB) and service (write-time computation) reference this string. Algorithm v2 would require a new constant string + DBCP amendment; M5 substrate constraint `mapr_workbench_fp_hash_fmt_chk` is algorithm-version-agnostic (only checks `sha256:` prefix format).

### 10.5 Implementation file

`bc-core/src/registry/mcf/workspace-fingerprint.ts` exports:

```typescript
export const WORKBENCH_FINGERPRINT_ALGORITHM_VERSION = 'mcf-workbench-v1';
export function computeWorkspaceFingerprint(
  toolAllowlistRows: ToolAllowlistRow[],
  evidenceAllowlistRows: EvidenceAllowlistRow[],
  bcfRegistrySnapshotId: string,
  operatorContextText: string,
  policyVersion: string,
  promptVersion: string,
): string;
```

Pure function. Unit test against known fixtures (golden vectors per M9 M1 lesson — hardcoded literal SHA256 captured via one-off script + locked).

---

## 11. Evidence + tool allowlist — usage discipline

### 11.1 Tool surface (closed set, v1 per MCF requirements §11.3.3)

10 tools, all read-only against BCF / evidence / source-reality / KPI catalog / MC substrate metadata:

| Tool code | Purpose | Backed by |
|---|---|---|
| `bcf.search_entity` | Search BCF Entities by name / family / domain | BCF read endpoint |
| `bcf.search_business_concept` | Search BCs on an Entity by kind / representation term / unit | BCF read endpoint |
| `bcf.read_entity` | Read a specific Entity by id | BCF read endpoint |
| `bcf.read_business_concept` | Read a specific BC by id (kind / unit / lifecycle state) | BCF read endpoint |
| `bcf.reachability_check` | Verify identity-reference DAG path between grain entity and BC's home entity | BCF read endpoint |
| `evidence.search` | Search allowed evidence corpora for a metric topic | Evidence corpus read |
| `evidence.retrieve` | Retrieve a specific evidence document by URI (must be in allowlist) | Evidence corpus read; URI filter against `evidence_source_allowlist` |
| `source_reality.summarize` | Summarize tenant's source / admission / observation contracts + emitted fields | bc-core SC/AC/OC read |
| `kpi_catalog.read_intent` | Read KPI catalog row as background-knowledge seed (explicitly **non-citable** per MCF §5.2 + §11.3.1) | `metric.metric_definition` read (legacy reservoir; explicitly tagged in tool response as non-citable) |
| `mc.identity_probe` | Check whether a candidate identity tuple would collide with an existing active MC | `mcf.metric_contract` read (substrate dormant; will return empty result during M12 v1; ready for M12.5+) |

### 11.2 Allowlist seeding (v1)

The M12 implementation PR seeds 10 rows into `mcf.workspace_tool_allowlist` (one per tool above) + an initial seed of `mcf.evidence_source_allowlist` (operator-defined list — DBCP §11.3). Seeds are inserted via the impl PR (no DDL gate; data rows only). Seeding is the only write to these 2 tables in M12 v1.

### 11.3 Initial `evidence_source_allowlist` seed (operator confirms in DBCP review)

Recommended v1 seed (operator may adjust before merge):
- `source_code='gaap'`, `source_version='2024'`
- `source_code='ifrs'`, `source_version='2024'`
- `source_code='xbrl_us_gaap'`, `source_version='2023'`
- `source_code='oagis'`, `source_version='10.6'`
- `source_code='isa95'`, `source_version='2010'`
- `source_code='bc_seed_metric_definitions'`, `source_version='2026-q2'`

### 11.4 Tool surface enforcement

`PanelToolSurface` interface is the only import path for any tool call. Tool implementations:
- HA-4: implementations call BCF / evidence / source-reality read APIs via service injection — never raw SQL against `concept_registry.*`
- Tools not in active `workspace_tool_allowlist` at service-init throw `ToolNotAllowlistedError` (panel run cannot start)
- Tool surface drift detection: integration test snapshot of the 10 tool codes asserts the count + names are stable

### 11.5 No legacy metric writer imports

`MetricAuthoringPanelService` source MUST NOT contain:
- `import { ... } from '../metric-definition.service'`
- `import { ... } from '../metric-definition.repository'`
- Any reference to `metric.metric_definition` / `metric.metric_knowledge` / `metric.metric_binding` / `contract.metric_contract` (legacy MC tables)

Enforced by HA-1 (CI grep + import-graph audit).

### 11.6 Allowlist seeding mechanism  *(new sub-section per M1 review patch)*

**Mechanism**: idempotent standalone seed script shipped in the M12 implementation PR.

| Item | Spec |
|---|---|
| Path | `bc-core/scripts/mcf-m12-seed-allowlists.mjs` |
| Format | Pure `.mjs` script (no TS build dependency) — same pattern as `bc-core/scripts/mcf-m11-operator-direct-ingest.mjs` |
| Auth / env | Reads `DATABASE_URL` from env (per established M5/M9/M10/M11 script pattern); refuses if unset |
| INSERT discipline | Each row inserted via `INSERT ... ON CONFLICT (tool_code, tool_version) DO NOTHING` (or equivalent for evidence sources) — **idempotent**; re-running the script produces 0 new rows after first successful run |
| Substrate guarantee | NO DDL; data rows only. Tables already exist per M5 closeout (`mcf.workspace_tool_allowlist` + `mcf.evidence_source_allowlist` live at 0 rows on bc-core `c359dc8`) |
| When run | (a) **Manually by operator after M12 impl PR merge**, before any panel run is attempted. Documented in impl PR README. (b) **Integration test setup hook** (vitest `beforeAll`) — invokes the same script logic against the test DB to populate the 10 tools + N evidence sources; uses the same `ON CONFLICT DO NOTHING` discipline so repeat test runs don't fail. (c) **Pre-merge dry-simulation in impl PR evidence**: operator runs the script against `bc_platform_dev` and captures the post-run row counts as evidence-PR artifact (matches M11 evidence pattern) |
| Idempotency test | `mcf-m12-seed-allowlists.spec.mjs` (or covered by the integration test's `beforeAll`): run the script twice, assert (a) first run inserts N + M rows; (b) second run inserts 0 new rows; (c) final rowcount = N + M |
| Expected count assertion | After seed: `mcf.workspace_tool_allowlist` rowcount = 10 (one per §11.1 tool); `mcf.evidence_source_allowlist` rowcount = 6 (per §11.3 default seed) |
| Roll-back | None needed — seeds are additive only. If operator wants to deactivate a tool/source, set `effective_to` (M5 versioned-row pattern), don't delete. |

**Script content shape** (informational; impl PR finalizes):

```javascript
#!/usr/bin/env node
// scripts/mcf-m12-seed-allowlists.mjs
import 'dotenv/config';
import postgres from 'postgres';
const sql = postgres(process.env.DATABASE_URL, { max: 2, prepare: false });

const TOOLS = [
  { tool_code: 'bcf.search_entity',          tool_version: 'v1', metadata: {...} },
  { tool_code: 'bcf.search_business_concept', tool_version: 'v1', metadata: {...} },
  // ... 10 total per §11.1
];
const EVIDENCE_SOURCES = [
  { source_code: 'gaap',         source_version: '2024', metadata: {...} },
  // ... 6 total per §11.3
];

for (const t of TOOLS) {
  await sql`
    INSERT INTO mcf.workspace_tool_allowlist (tool_code, tool_version, effective_from, tool_metadata_json)
    VALUES (${t.tool_code}, ${t.tool_version}, now(), ${sql.json(t.metadata)})
    ON CONFLICT (tool_code, tool_version) DO NOTHING
  `;
}
for (const s of EVIDENCE_SOURCES) {
  await sql`
    INSERT INTO mcf.evidence_source_allowlist (source_code, source_version, effective_from, source_metadata_json)
    VALUES (${s.source_code}, ${s.source_version}, now(), ${sql.json(s.metadata)})
    ON CONFLICT (source_code, source_version) DO NOTHING
  `;
}
// log final counts; exit 0
await sql.end();
```

**Note on the ON CONFLICT clause**: this requires a UNIQUE constraint on `(tool_code, tool_version)` and `(source_code, source_version)`. The M5 substrate ships these as composite UNIQUE indexes per M5 DBCP §13 (verifier-test #4 + #5). If verification at impl-PR time shows the UNIQUE is missing, escalate to a small DDL gate (would be the FIRST DBCP escalation for M12 — outside the default scope; operator authorization required).

**Impl PR scope**: the seed script IS part of the M12 impl PR per §21 (added to the recommended file list).

---

## 12. M9 C-FX reuse — read-only validation only

### 12.1 What M12 uses from M9

Per D-M12-6, the Checker role validates proposed fixtures structurally **before** the panel approves. M12 imports:

```typescript
import {
  FixtureStructuralCheckService,
  type FixtureContext,
  type FixtureStructuralCheckResult,
  type FixtureDefect,
} from './fixture-structural-check.service';
// Path: bc-core/src/registry/mcf/fixture-structural-check.service.ts
// Exports per lines 95-123 of that file (verified empirically)
```

Checker invokes:

```typescript
const result: FixtureStructuralCheckResult = fixtureStructuralCheckService.runStructuralChecks(
  context,     // FixtureContext built from the proposed MC package signature
  body,        // FixtureBodyForHash built from the proposed Section A/B/C
);
```

Per MCF requirements §12.5 (C-FX-1..C-FX-11 checks). `runStructuralChecks` is a **pure function** (no DB writes; substrate dormant). The result is captured in:

- Per-Checker mapt row: `transcript_payload_json.verification_payload.checker_c_fx_result`
- Per-fixture entry in `consensus_payload_json.candidate_proposal.proposed_fixtures[].checker_c_fx_result`

### 12.2 No fixture INSERT

M12 does NOT call any service that INSERTs into `mcf.metric_self_verification_fixture`. The proposed fixture is a Section A/B/C structure inside `consensus_payload_json` — descriptive content; not a row.

Fixture INSERT is M12.5's responsibility (after M12.5 reads `consensus_payload_json.candidate_proposal.proposed_fixtures[0]` and calls a future `FixtureAuthoringService.createFixture(...)` which doesn't exist yet — it's the second piece M12.5 specifies).

### 12.3 Loader pattern

M9 also exports `loadFixtureContext(mcvUid, deps)` for loading the MCV context from substrate. M12 does NOT use this (no MCV exists yet during panel run — that's M12.5). Instead, M12's Checker builds `FixtureContext` synthetically from the Maker's proposed MC structure (the bindings exist as candidate_proposal.variable_bindings, not as substrate rows). DBCP §12.4 specifies the synthetic-context builder.

### 12.4 Synthetic FixtureContext builder

```typescript
// New helper in bc-core/src/registry/mcf/panel-checker-fixture-context.builder.ts
export function buildSyntheticFixtureContext(
  candidateProposal: CandidateProposal,
): FixtureContext;
```

Constructs an in-memory `FixtureContext` shape that matches what `loadFixtureContext` would produce post-materialization — except sourced from the panel's in-flight proposal instead of substrate rows. This lets the Checker run C-FX against a not-yet-existing MC package.

---

## 13. M10 verifier — explicitly NOT called in M12

Per D-M12-7 and HA-3:

- `MetricSelfVerificationService` (`bc-core/src/registry/mcf/metric-self-verification.service.ts`, 373 lines) is **NOT imported** by `MetricAuthoringPanelService` or any of its helpers
- No fixture rows exist for the verifier to consume during M12 (the fixture is proposed-but-not-INSERTed)
- M12 v1 produces ZERO `mcf.metric_self_verification_result` rows
- M12.5 will: write fixture row → invoke verifier → write verification_result row → only then call `markConsumedByPanel`

Static enforcement: `MetricAuthoringPanelService` source file's import block does not include `metric-self-verification.service`. CI grep enforces.

---

## 14. Intake status + rejection behavior

Per amended D-M12-8 and HA-6:

| Panel verdict | Intake status action | Reason text (if any) |
|---|---|---|
| `APPROVE_FOR_DRAFT` | **NO-OP** — intake stays `pending`; M12.5 will call `markConsumedByPanel` after MC + fixture + cert write succeeds | — |
| `OPERATOR_REVIEW` (any reason) | **NO-OP** — operator inspects panel run via audit UI (M16) | — |
| `REJECT_DEFECT` (consensus all-reject; `defect_code` carried in separate field per M5 §12.2) | Call `ReservoirIngestionService.markRejected(intakeQueueUid, reason, { tx })` | `composeRejectionReason(consensus)` — ≥ 20 chars per M11 `maiq_rejected_status_requires_reason_chk`. Format: `"Panel rejected: <defect_code>. <per-role summary line>"` |
| Mid-run failure (vendor outage / timeout / cost ceiling) | **NO-OP** (treated as OPERATOR_REVIEW) | — |

### 14.1 `markConsumedByPanel` forbidden — HA-6 enforcement

`MetricAuthoringPanelService` source file MUST NOT contain the substring `markConsumedByPanel` anywhere. Enforced:
- CI grep step in pre-merge gate
- Unit test asserts the imported `reservoirIngestionService` object's `markConsumedByPanel` method is never called (vi.fn spy)
- Integration test verifies intake row status post-panel-run is `pending` (not `consumed_by_panel`) on APPROVE_FOR_DRAFT path

### 14.2 Reason composer

```typescript
function composeRejectionReason(consensus: ConsensusPayload): string {
  const defectCode = consensus.defect_code ?? 'MC_DEFECT_UNKNOWN';
  const perRoleLines = consensus.per_role_summary
    .map((r) => `${r.role}=${r.verdict_code}/${r.defect_code ?? 'none'}`)
    .join('; ');
  const text = `Panel rejected: ${defectCode}. Roles: ${perRoleLines}.`;
  // M11 substrate requires ≥ 20 chars; the above template guarantees >= 20 for any non-empty consensus
  return text;
}
```

---

## 15. D-M12-11 rejection log venue — Option A default

### 15.1 Option A is the default (no new substrate)

**Decision per D-M12-11 (amended preflight §3.11): Option A confirmed for v1.**

Rejection data lives across 3 existing substrate surfaces:

| Surface | What it carries | Already enforced by |
|---|---|---|
| `mcf.metric_authoring_panel_run.consensus_payload_json` | Aggregate `verdict_code = 'REJECT_DEFECT'` (single-token per M5) + separate `defect_code = 'MC_DEFECT_*'` + `per_role_summary` (3-entry array) + `grounding_violations` | M5 substrate immutability trigger; service-side JSON-Schema |
| `mcf.metric_authoring_panel_transcript.transcript_payload_json` (× 3) | Per-role `verdict_code` + `defect_code` + full tool-call trace + reasoning + claims | M5 substrate immutability trigger; mapt_model_role_chk |
| `mcf.metric_authoring_intake_queue.status_reason_text` | Operator-readable rejection summary (≥ 20 chars) | M11 `maiq_rejected_status_requires_reason_chk` |

Query pattern for "all panel rejections by defect_code, last 30 days":

```sql
SELECT
  mapr.panel_run_uid,
  mapr.consensus_payload_json->>'defect_code' AS defect_code,
  mapr.created_at,
  intake.candidate_name,
  intake.status_reason_text
FROM mcf.metric_authoring_panel_run mapr
JOIN mcf.metric_authoring_intake_queue intake
  ON intake.intake_queue_uid = (mapr.consensus_payload_json->'intake_back_reference'->>'intake_queue_uid')::uuid
WHERE mapr.consensus_payload_json->>'verdict_code' LIKE 'REJECT_%'
  AND mapr.created_at >= NOW() - INTERVAL '30 days'
ORDER BY mapr.created_at DESC;
```

This query is supported by existing substrate; no new table needed.

### 15.2 Escalation to Option B (rare; explicit operator authorization required)

Option B (`mcf.metric_authoring_panel_rejection_log`) only ships if:
- A concrete query pattern surfaces during M12 evidence runs that Option A cannot satisfy efficiently, AND
- Operator explicitly authorizes a small-DDL gate amendment

If escalated, the table shape per audit `e725263` §5.4:
- `rejection_log_uid` (PK) / `panel_run_uid` (FK to mapr) / `defect_code` / `rejection_summary_text` / `decided_at` / `decided_by_name`

No DDL forward / rollback file is shipped in the M12 impl PR unless this escalation is authorized. Default: zero new DDL.

### 15.3 Option C is forbidden (per D-M12-11)

Widening `contract.authoring_panel_rejection_log.scope_code` enum to include `'mc'` is REJECTED — violates MCF requirements §3.8 (no-cross-framework-write-coupling); reverses BCF M5 closeout scope decision. Not selectable by M12 DBCP.

---

## 16. Hard assertions HA-1..HA-8 — implementation acceptance criteria

Each HA is both a code-discipline requirement AND a test requirement. Both must pass before M12 merges.

| # | Code discipline | Test verification |
|---|---|---|
| **HA-1** | `metric-authoring-panel.service.ts` and all helper files do NOT contain `from '../metric-definition.service'` / `from '../metric-definition.repository'` / any other legacy `metric.*` writer | (a) Unit test: import-graph audit asserts panel module's transitive imports exclude legacy paths; (b) CI grep step (`grep -r "metric-definition" src/registry/mcf/metric-authoring-panel.service.ts && exit 1 \|\| true`) |
| **HA-2** | Panel service does NOT import `McfCertWriterService` | (a) CI grep on panel service source; (b) Integration test asserts post-panel-run rowcount on `mcf.certification_record` == 0 |
| **HA-3** | Panel service does NOT import `MetricSelfVerificationService` | (a) CI grep; (b) Integration test asserts post-panel-run rowcount on `mcf.metric_self_verification_result` == 0 |
| **HA-4** | All BCF reads go through `PanelToolSurface` injected interface; no raw SQL against `concept_registry.*` | (a) CI grep for `from 'drizzle-orm'` + raw SQL referencing concept_registry; (b) Integration test monitors query log during a panel run and asserts zero direct `concept_registry.*` SELECTs |
| **HA-5** | Panel writes ONLY to the expected substrate surfaces per amended Step 7 + Step 8: (a) `contract.panel_output_record` +1 (Step 7a; MANDATORY per active FK); (b) `mcf.metric_authoring_panel_run` +1 (Step 7b); (c) `mcf.metric_authoring_panel_transcript` +3 (Step 7c; one per role); (d) `mcf.metric_authoring_intake_queue.status_code` UPDATE via M11 service on all-reject path only (no row count delta — it's an UPDATE, not INSERT). Allowlist seed rows are written by the seed script (§11.6), NOT by the panel service itself. | Integration test: synthetic intake row → panel run → assert **expected deltas**: `contract.panel_output_record` = **+1**, `mcf.metric_authoring_panel_run` = **+1**, `mcf.metric_authoring_panel_transcript` = **+3**; and assert **forbidden 0-row deltas** on `mcf.metric_contract`, `mcf.metric_contract_version`, `mcf.metric_variable_binding`, `mcf.metric_filter_clause`, `mcf.metric_computed_dimension_ref`, `mcf.metric_self_verification_fixture`, `mcf.metric_self_verification_result`, `mcf.certification_record`, `mcf.metric_publication_eligibility_result`, `mcf.metric_supersession`, `mcf.metric_contract_revision`, `mcf.metric_cert_writer_idempotency`, `contract.authoring_panel_rejection_log` (BCF-scoped per D-M5-7), `concept_registry.*` (every BCF table), `metric.metric_definition`, `metric.metric_knowledge`, `metric.metric_binding`, `contract.metric_contract` (legacy 780-row baseline preserved) |
| **HA-6** | `markConsumedByPanel` string MUST NOT appear in panel service source | (a) Unit test asserts source text via `fs.readFileSync(__filename, 'utf8').includes('markConsumedByPanel') === false`; (b) Integration test asserts intake row status is `pending` (not `consumed_by_panel`) post-APPROVE_FOR_DRAFT run |
| **HA-7** | `consensus_payload_json` schema is locked in `panel-payload.schema.json` and validated at write time | (a) Round-trip test: panel produces a known-shape `consensus_payload_json`; mock materialization service reads + asserts every expected field is present; (b) Schema diff test: any change to `panel-payload.schema.json` requires bumping `panel_algorithm_version` |
| **HA-8** | All 4 reservoir-provenance fields copied from intake row to mapr | (a) Substrate CHECK already enforces all-or-none; (b) Integration test asserts mapr row has all 4 fields populated AND matches the intake row's values byte-for-byte |
| **HA-9** *(new per M3)* | Service-init reads `contract.framework_policy WHERE policy_uid='mcf_v1'` and asserts `consensus_requirement_json->'panel_discipline'->>'defect_code_registry_version' = 'v1'`. Mismatch refuses startup with `PolicyVersionMismatchError`. All emitted `MC_DEFECT_*` codes from `panel-consensus.ts` MUST be drawn from the v1 registry (TS const `MCF_DEFECT_REGISTRY_V1` enumerating the 11 codes per MCF requirements §11.3.4). Future taxonomy changes require operator-authorized `mcf_v1` policy version bump (per M5 §12.3); not a mid-flight change. | (a) Unit test: service constructor with mock policy reader; asserts startup throws when `defect_code_registry_version ≠ 'v1'`; (b) Unit test: `panel-consensus.ts` rejects defect codes not in the v1 registry; (c) Integration test: read live `mcf_v1` policy row + assert pin value matches expected `'v1'` |

Test file convention: HA-* tests live in `metric-authoring-panel.service.spec.ts` + `metric-authoring-panel.service.integration.spec.ts` with `describe('HA-N: <name>', ...)` blocks for explicit traceability to acceptance criteria.

---

## 17. Drizzle / DDL impact

### 17.1 Default (D-M12-11 Option A)

**ZERO new tables. ZERO new Drizzle schemas. ZERO DDL files.** M12 v1 impl PR is service + tests only.

### 17.2 Conditional (D-M12-11 Option B — only if operator authorizes)

If escalated mid-DBCP-review to Option B, the impl PR adds:
- `bc-core/docker/redesign/12-mcf-panel-rejection-log.sql` (forward DDL)
- `bc-core/docker/redesign/12-mcf-panel-rejection-log-rollback.sql` (rollback with row-count guard)
- `bc-core/src/database/schema/mcf/metric-authoring-panel-rejection-log.ts` (Drizzle schema)
- Update `bc-core/src/database/schema/mcf/index.ts` (re-export)
- `bc-core/scripts/mcf-m12-dry-run.mjs` + `mcf-m12-post-apply-verification.mjs` (mirror M5/M9/M10/M11 pattern)

Otherwise, none of the above ships.

---

## 18. Test plan

### 18.1 Unit tests (target: ~70 cases)

| File | Coverage |
|---|---|
| `workspace-fingerprint.spec.ts` | Determinism (5 runs, same inputs, same output); golden vector lock (hardcoded literal SHA256 per M9 M1 lesson); per-input mutation (changing any of the 7 ordered inputs changes the hash) |
| `panel-consensus.spec.ts` | All 8 consensus outcomes (3-approve / 3-reject / mixed / tie-break / etc.); tie-break determinism (Maker > Checker > Moderator) |
| `panel-grounding-check.spec.ts` | Per-claim match against tool calls; false-positive rejection (claim text differs slightly from response); empty-claim degenerate case |
| `panel-checker-fixture-context.builder.spec.ts` | Synthetic FixtureContext construction; round-trip with M9 `runStructuralChecks` |
| `panel-payload.types.spec.ts` | JSON-Schema validation of `consensus_payload_json` + `transcript_payload_json` against valid + invalid fixtures |
| `panel-role-agent.spec.ts` (× 3 vendor adapters) | Per-vendor request shape + response parsing + error / timeout / cost-ceiling behavior; uses vendor SDK mocks |
| `metric-authoring-panel.service.spec.ts` | Full `runPanel` orchestration with mocked agents; covers all 8 outcome paths per §5.3; HA-1, HA-2, HA-3, HA-6 import + grep + spy assertions |

### 18.2 Integration tests (target: ~10 cases)

| File | Coverage |
|---|---|
| `metric-authoring-panel.service.integration.spec.ts` | Full panel run against `bc_platform_dev` (synthetic intake row inserted in test setup; SAVEPOINT-rolled back after); HA-4, HA-5, HA-7, HA-8 assertions including the 15-table 0-row-delta check |

### 18.3 Expected + forbidden row deltas (per amended HA-5)

**Expected per-panel-run deltas** (panel produces evidence):
- `contract.panel_output_record` = **+1** (Step 7a — MANDATORY per active FK `fk_mapr_panel_run` + M5 §5 1:1 composition)
- `mcf.metric_authoring_panel_run` = **+1** (Step 7b)
- `mcf.metric_authoring_panel_transcript` = **+3** (Step 7c — one per role)
- `mcf.metric_authoring_intake_queue` status = transitions `pending → rejected` on all-reject path only (UPDATE, not INSERT; no row count delta)

**Forbidden 0-row deltas** (M12 must NOT write to):
- `mcf.metric_contract`
- `mcf.metric_contract_version`
- `mcf.metric_variable_binding`
- `mcf.metric_filter_clause`
- `mcf.metric_computed_dimension_ref`
- `mcf.metric_self_verification_fixture`
- `mcf.metric_self_verification_result`
- `mcf.certification_record`
- `mcf.metric_publication_eligibility_result`
- `mcf.metric_supersession`
- `mcf.metric_contract_revision`
- `mcf.metric_cert_writer_idempotency`
- `contract.authoring_panel_rejection_log` (BCF-scoped per D-M5-7; MCF rejections go to mapr/mapt/intake per D-M12-11 Option A)
- `concept_registry.*` (every BCF concept-registry table — listed individually by the test for explicit traceability)
- `metric.metric_definition`
- `metric.metric_knowledge`
- `metric.metric_binding`
- `contract.metric_contract` (legacy 780-row baseline preserved)

**Allowlist rowcounts** (NOT touched by the panel service itself; written only by the seed script per §11.6):
- `mcf.workspace_tool_allowlist` = unchanged from test-setup baseline (seed runs in `beforeAll`, not in per-test setup)
- `mcf.evidence_source_allowlist` = unchanged from test-setup baseline (same)

### 18.4 BCF pattern fakes (per operator instruction §12)

`metric-authoring-panel.service.spec.ts` includes one test `it('does not invoke BCF cert layer; mocks FrameworkApprovalService and asserts zero calls', ...)` that proves M12 inherits the post-panel shape from BCF but does NOT call `FrameworkApprovalService.issueRegistryShapeCertification` or `RegistryAuthoringOrchestrator.runS1` (BCF cert + dispatch). Verifies §6.2 forbidden carryovers.

### 18.5 Workspace fingerprint determinism

Standalone deterministic test: same allowlist snapshot + same BCF snapshot id + same operator context + same versions → same hash across 5 invocations. Mutation test: change any of the 7 ordered inputs → hash changes.

### 18.6 No real model API calls in any test

All vendor agent adapters are mocked. Tests run without network access. Per-vendor adapter unit tests use canned response fixtures committed to the repo.

---

## 19. Risks and mitigations

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-M12-1 | Three-model parallel execution: real-world model latency variance causes long runs | Medium | Per-vendor timeout (§7.5); `Promise.allSettled` (not `all`); consensus OPERATOR_REVIEW on any timeout |
| R-M12-2 | Workspace fingerprint algorithm drift (build plan R-11) | Medium | Single algorithm constant `mcf-workbench-v1` (§10); golden-vector unit test locks output; substrate format CHECK guards format |
| R-M12-3 | Grounding check false-negatives (claim ≠ tool call due to fuzzy match) | Medium | Exact match algorithm specified in `panel-grounding-check.ts` §7.4; calibration sampling against known-grounded fixtures in test suite |
| R-M12-4 | Tool surface drift (new tool added without ADR) | Low | `workspace_tool_allowlist` is the authoritative list; service-init refuses tools not in allowlist; integration test snapshot locks the 10-tool count |
| R-M12-5 | Defect-code taxonomy v1 incompleteness | Low | 11 codes enumerated per MCF requirements §11.3.4; DBCP forbids ad-hoc codes; v2 amendment if patterns emerge |
| R-M12-6 | Model vendor outages | Low | Three-vendor rule + `Promise.allSettled` + OPERATOR_REVIEW fallback; no panel run hangs the system |
| R-M12-7 | Cost ceiling drift (per-run × per-month) | Medium | Per-vendor token budget + per-month service budget (§7.5); over-budget run aborts cleanly to OPERATOR_REVIEW |
| R-M12-8 | BCF Registry snapshot read pattern | Low | M12 reads BCF via bcf.* tool surface only (HA-4); snapshot id captured in workbench fingerprint |
| R-M12-9 | Premature materialization pressure (operator wants MC rows in v1) | High | M12-B locked; HA-1..HA-3 + HA-6 enforce; materialization is M12.5 gate |
| R-M12-10 | Operator-direct submission bypass | Low | D-M12-2 locks intake-only path; M11 CLI is operator-direct ingestion entry |
| R-M12-11 | Schema drift between M12 produced `consensus_payload_json` and M12.5 consumer | Medium | HA-7 round-trip test; `panel_algorithm_version` versioning; schema literal committed to repo |
| R-M12-12 | Substrate immutability bypass attempt | Low | M5 mapr/mapt immutability triggers already live; integration test would fail loudly |
| R-M12-13 | Vendor SDK breaking change between PR open and merge | Low | Vendor SDK versions pinned in `package.json`; adapter tests use canned fixtures (no network) |
| R-M12-14 | Per-role prompt regression (subtle wording change degrades panel output) | Medium | Prompt files versioned (`*.v1.md`); any change bumps `prompt_version` which changes workspace fingerprint; integration test against known-good intake row fixture catches regression |

### 19.1 Stop conditions

- D-M12-11 escalates to Option B mid-DBCP review → impl PR scope grows by 1 small DDL gate; pause for operator authorization before proceeding
- Real vendor SDK + API key procurement is blocked (no production keys yet) → ship impl PR with mocked-only agent adapters; gate real-vendor smoke run to a separate operator session

---

## 20. Operator approvals for implementation PR (O-M12-1..O-M12-12)

Before the M12 implementation PR opens, the operator approves these 12 items:

| # | Approval item |
|---|---|
| **O-M12-1** | Confirm M12-B locked (proposal-only; ZERO new tables by default per D-M12-11 Option A) |
| **O-M12-2** | Confirm 10-step execution flow per §5 |
| **O-M12-3** | Confirm BCF pattern reuse boundary per §6 (read-panel-then-decide shape only; no cert / no dispatch / no BCF writes) |
| **O-M12-4** | Confirm three-vendor role assignment defaults per §7.3 (Anthropic Maker / OpenAI Checker / Google Moderator); operator-configurable via env |
| **O-M12-5** | Confirm `consensus_payload_json` v1 schema per §8 as M12.5 input contract |
| **O-M12-6** | Confirm `transcript_payload_json` v1 schema per §9 |
| **O-M12-7** | Confirm `mcf-workbench-v1` 7-element ordered input list per §10.1 |
| **O-M12-8** | Confirm initial `evidence_source_allowlist` seed per §11.3 |
| **O-M12-9** | Confirm D-M12-11 Option A (default); operator may pre-authorize Option B escalation OR explicitly forbid escalation |
| **O-M12-10** | Confirm HA-1..HA-8 as both code discipline + test requirements per §16 |
| **O-M12-11** | Confirm test plan per §18 including 18-table 0-row-delta integration assertion |
| **O-M12-12** | Approve the next gate: M12 implementation PR (service + tests; ZERO DDL by default; ZERO scripts unless dry-simulation justified — see §21) |

---

## 21. Recommended implementation PR shape

### 21.1 Files to add (service + helpers + types + prompts + seed script)  *(amended)*

| Path | Lines (estimate) | Purpose |
|---|---|---|
| `bc-core/src/registry/mcf/metric-authoring-panel.service.ts` | ~450 | Orchestrator class (3 short TXs per §5) |
| `bc-core/src/registry/mcf/panel-role-agent.interface.ts` | ~80 | Agent contract |
| `bc-core/src/registry/mcf/panel-tool-surface.types.ts` | ~150 | 10-tool interface contracts |
| `bc-core/src/registry/mcf/panel-payload.types.ts` | ~200 | TypeScript types for consensus + transcript JSON |
| `bc-core/src/registry/mcf/panel-payload.schema.json` | ~250 | JSON-Schema validator literal |
| `bc-core/src/registry/mcf/workspace-fingerprint.ts` | ~80 | Pure function |
| `bc-core/src/registry/mcf/panel-consensus.ts` | ~120 | Pure function |
| `bc-core/src/registry/mcf/panel-grounding-check.ts` | ~150 | Pure function |
| `bc-core/src/registry/mcf/panel-checker-fixture-context.builder.ts` | ~100 | Synthetic FixtureContext builder for Checker |
| `bc-core/src/registry/mcf/mcf-defect-registry-v1.ts` | ~40 | TS const enumerating 11 MC_DEFECT_* codes (HA-9 source of truth) |
| `bc-core/src/registry/mcf/panel-agents/anthropic-agent.adapter.ts` | ~180 | Vendor adapter (with mockable interface) |
| `bc-core/src/registry/mcf/panel-agents/openai-agent.adapter.ts` | ~180 | Same |
| `bc-core/src/registry/mcf/panel-agents/google-agent.adapter.ts` | ~180 | Same |
| `bc-core/src/registry/mcf/prompts/m12-panel-maker.v1.md` | ~80 | Maker prompt template |
| `bc-core/src/registry/mcf/prompts/m12-panel-checker.v1.md` | ~80 | Checker prompt template |
| `bc-core/src/registry/mcf/prompts/m12-panel-moderator.v1.md` | ~80 | Moderator prompt template |
| `bc-core/scripts/mcf-m12-seed-allowlists.mjs` *(new per §11.6)* | ~120 | Idempotent allowlist seeding script (ON CONFLICT DO NOTHING) |
| Plus matching `*.spec.ts` files (~13 specs) | ~1600 | Unit + integration tests including seed-script idempotency spec |

**Total estimate**: ~4,000 lines new + ~1,600 lines test = ~5,600 lines.

**Spec file count** *(per L3 cleanup)*: 13 specs total — 11 specs for the service / pure-function / vendor adapter files listed above (1 spec per source file) + 1 integration spec (`metric-authoring-panel.service.integration.spec.ts`) + 1 seed-script spec (`mcf-m12-seed-allowlists.spec.mjs`).

### 21.2 Files NOT shipped (default — D-M12-11 Option A)

- No DDL files (Option A default; only triggered if D-M12-11 escalates to Option B which adds 1 small DDL gate for `mcf.metric_authoring_panel_rejection_log`)
- No `mcf-m12-dry-run.mjs` or `mcf-m12-post-apply-verification.mjs` since M12-B writes only to existing M5 substrate tables (substrate-side verification rests on M5 closeout); the integration test serves the same verification function
- No Drizzle schema file
- No `index.ts` re-export change

### 21.3 Pre-merge acceptance criteria  *(amended per L2)*

| # | Criterion |
|---|---|
| 1 | **CodeArtifact installability**: the 3 vendor SDKs (`@anthropic-ai/sdk`, `openai`, `@google/generative-ai` — or operator-chosen equivalents) install successfully via the `barecount/npm-mirror` CodeArtifact repo. **No direct public-npm install permitted** per CLAUDE.md npm registry discipline. PR checklist requires `AWS_PROFILE=barecount aws codeartifact login ... && npm install` succeeds against the chosen vendor SDK versions before review. |
| 2 | All HA-1..HA-9 assertions pass (import-graph audit + CI greps + integration test 0-row-delta assertions) |
| 3 | Seed script idempotency proven (run script twice; first run inserts; second run no-op; final rowcount matches expected) |
| 4 | Workspace fingerprint determinism test passes (5 invocations with same inputs → same hash; 7 mutation tests show each input affects hash) |
| 5 | Zero real model API calls in any test (vendor SDK mocks + canned fixtures) |
| 6 | Verdict-code single-token convention verified across mapr `consensus_payload_json.verdict_code` + `contract.panel_output_record.verdict_code` + mapt `transcript_payload_json.verdict_code` (all three sources show same enum) |
| 7 | All 3 vendor SDKs are MOCK-ONLY in tests; integration spec uses mocked agents, never live network |

### 21.4 No DDL apply gate (default)

M12 v1 is a code-only PR (impl PR + seed script). After merge, the operator runs `mcf-m12-seed-allowlists.mjs` against `bc_platform_dev` once. No separate DDL apply session needed unless D-M12-11 escalates to Option B mid-DBCP-review. The M12 integration test (against `bc_platform_dev`) is the evidence run. An **M12 evidence PR** captures: (a) integration-test artifacts (synthetic-run summary + expected-delta / forbidden-0-delta proof); (b) seed script idempotency run output; (c) post-seed allowlist rowcount snapshot.

### 21.5 Dry-simulation script — NOT justified for v1

Per operator instruction §13: "no scripts unless a dry-simulation script is justified." Justification analysis: M12 v1 has no DDL to dry-run; the integration test serves the same verification function. The seed script (§11.6 / `mcf-m12-seed-allowlists.mjs`) is operationally necessary (one-shot data population) and IS shipped. A **smoke-run script** against real vendor APIs is NOT shipped in v1 — mocked agents cover the orchestration paths.

### 21.6 Suggested PR title

`feat(mcf): M12 Metric Authoring Panel — three-model consensus + transcripts (writes panel_output_record + mapr + 3× mapt only; M12.5 owns materialization)`

### 21.7 Sequencing per established pattern

1. M12 DBCP (this doc — amended per B1/M1/M2/M3/L1/L2/L3 review patches) → operator review → 12 approvals O-M12-1..O-M12-12 ← **THIS DBCP**
2. M12 implementation PR (service + tests + seed script; ZERO DDL by default)
3. Operator runs `mcf-m12-seed-allowlists.mjs` against `bc_platform_dev` (one-shot; idempotent)
4. M12 evidence PR (integration-test artifacts + seed-run output + post-seed rowcount snapshot)
5. M12 closeout
6. **THEN**: M12.5 preflight (materialization + legacy bridge)

---

## 22. What stays closed  *(amended per B1 review patch)*

| | |
|---|---|
| M12 impl PR | not opened by this DBCP |
| M12 DDL apply | NOT NEEDED (Option A default); only triggered if D-M12-11 escalates to Option B |
| M12 evidence PR | pending impl PR |
| **M12.5 (materialization + legacy bridge)** | CLOSED — gated on M12 closeout |
| M13 PE-MC evaluator | CLOSED — gated on M12.5 |
| M14+ | CLOSED |
| Real MCF metric contracts | CLOSED — substrate stays empty |
| Real intake-queue rows beyond M11 dormancy | CLOSED |
| Real model API calls | CLOSED — design phase; impl phase uses mocked vendors only |
| Real BCF reads beyond test-fake bcf.* tool surface | CLOSED |
| Legacy metric write paths | LIVE during M12 (legacy authoring continues unchanged); deprecation handling lands in M12.5 |
| bc-admin frontend metric API surfaces | LIVE during M12 (no MCF endpoint exposed by M12 v1); migration lands in M16 (read) + M17 (write) |
| SC / AC reads from panel | CLOSED — zero metric coupling per audit `e725263` §2.4 + §2.5; HA-style grep + integration-test assertions required |
| Cert writes | CLOSED — M4 cert writer NOT invoked in M12 (HA-2) |
| Fixture INSERTs / verification result rows | CLOSED (HA-3) |
| `markConsumedByPanel` invocation | CLOSED — FORBIDDEN in M12 v1 (HA-6); M12.5 owns it |
| **`contract.panel_output_record` writes** | **EXPECTED** — M12 MUST write 1 row per panel run (Step 7a; per active FK `fk_mapr_panel_run` + M5 §5 1:1 composition). NOT a BCF write — shared panel substrate scoped via `stage_code='authoring'`. MCF-specific defect detail stays in `mapr.consensus_payload_json` per D-M5-7. |
| BCF concept-registry writes (`concept_registry.*` / `contract.business_entity` / `contract.business_concept` / etc.) | NEVER — MCF requirements §3.8 no-cross-framework-write-coupling; HA-4 enforces BCF reads only via bcf.* tool surface |
| `contract.authoring_panel_rejection_log` writes | NEVER — BCF-scoped enum per D-M5-7; MCF rejections live in mapr + mapt + intake.status_reason_text per D-M12-11 Option A |
| Option C (widen `contract.authoring_panel_rejection_log` scope enum) | CLOSED — explicitly rejected per D-M12-11 |
| Templated `'REJECT_<defect_code>'` verdict-code form | CLOSED per M2 patch — use single-token `'REJECT_DEFECT'` + separate `defect_code` field; converges with M5 §12.2 |
| Long-lived row locks during agent execution | CLOSED per L1 patch — `FOR UPDATE` removed; concurrency safety via Step-1 in-flight guard (§5.4) + M11 status-transition CAS guard |
| Direct public-npm install for vendor SDKs | NEVER — CodeArtifact-only per CLAUDE.md npm registry discipline; pre-merge acceptance criterion (§21.3) |
