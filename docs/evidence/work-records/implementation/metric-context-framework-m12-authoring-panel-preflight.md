---
uid: metric-context-framework-m12-authoring-panel-preflight
title: MCF M12 Metric Authoring Panel — Preflight
description: Pre-DBCP design framing for MCF gate M12 (Metric Authoring Panel workbench) per MCF requirements §11.3 + build plan §M12. Establishes the scope-narrow recommendation that v1 ships orchestration only (three-model consensus + per-model transcripts + workspace fingerprint + grounding check + closed-enum verdicts + intake-status transitions), with no substrate writes to metric_contract / fixture / verification_result / certification_record. Locks 11 decisions D-M12-1..D-M12-11 for operator review before the DBCP gate opens. Recommends M12-B (proposal-only panel; materialization deferred to NEW gate M12.5 — see §7). AMENDED 2026-05-27 (per audit `e725263`) to (1) insert M12.5 (materialization + legacy bridge) between M12 closeout and M13 PE-MC evaluator, (2) correct D-M12-8 so M12 calls markRejected only on all-reject and leaves intake at `pending` on APPROVE_FOR_DRAFT / OPERATOR_REVIEW (M12.5 owns markConsumedByPanel after materialization), (3) add D-M12-11 (rejection log venue — 3 options; default = Option A reuse mapr + mapt + intake reason text, no new table), (4) add 8 hard assertions HA-1..HA-8 for M12 DBCP, (5) add the Post-BCF Metric Workflow Wiring Boundary section asserting legacy metric.* writes stay live until M12.5 closeout and M12 must not import legacy MetricDefinitionService / McfCertWriterService / MetricSelfVerificationService, (6) confirm SC/AC have no structural change and require explicit no-op grep/test assertions in the M12 DBCP. Discipline confirmation throughout: no bc-core implementation in this gate; no DDL apply; no reservoir ingestion; no metric contracts / fixtures / results / panel runs created; no M13/M14+ work; no BCF touches.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m12-authoring-panel-preflight
---

# MCF M12 Metric Authoring Panel — Preflight

## 1. Scope and grounding

Design the M12 Metric Authoring Panel workbench per MCF requirements §11.3 + build plan §M12. The panel is the first **AI-active** gate in the MCF arc: every prior gate (M2 → M11) built substrate or read-only computation; M12 introduces the three-model consensus engine that proposes candidate metric contracts from reservoir intake. This preflight establishes the narrowest viable v1 scope that still produces meaningful evidence and locks 10 decisions before the DBCP gate opens.

### 1.1 Live state

| | |
|---|---|
| bc-core main | `c359dc8` (M11 evidence merged) |
| bc-docs-v3 main | `8f18664` (M11 closeout) |
| `mcf.*` tables | **17 present, all 0 rows** |
| `mcf.metric_authoring_intake_queue` | live + dormant (per M11) |
| `mcf.metric_authoring_panel_run` (mapr) | live, 0 rows (per M5; reservoir-provenance fields confirmed nullable, all-or-none CHECK active) |
| `mcf.metric_authoring_panel_transcript` (mapt) | live, 0 rows (per M5) |
| `mcf.workspace_tool_allowlist` / `evidence_source_allowlist` | live, 0 rows (per M5; tool / source / version columns ready) |
| `mcf.certification_record` | live, 0 rows (Foundation Governance Substrate; M4 cert writer available) |
| `mcf.metric_self_verification_fixture` / `metric_self_verification_result` | live, 0 rows (M9 + M10) |
| BCF | untouched (24 panel + 1 rejection log) |

### 1.2 Source documents consumed

| Source | Role |
|---|---|
| MCF requirements §11 (Authority Model) | Three-model rule, same-workspace rule, no-fabrication grounding, transcript immutability |
| MCF requirements §11.3 (Metric Authoring Panel) | Three-model panel + 10 tool surfaces + 11 defect codes + 3 closed-enum verdicts + workspace fingerprint |
| MCF requirements §11.5 (Cert-backed authority) | Cert table is Foundation Governance Substrate; MCF writes cert rows scoped by MCF action codes |
| MCF requirements §12 (Self-Verification Fixtures) | Panel may propose fixtures; platform verifies; AI assertion of fixture passage is not proof |
| Build plan §M12 (Gate M12) | T-shirt XL; primary risk R-09 (overbuilding); explicit scope: three-model + closed verdicts + grounding + workbench fingerprint — nothing more |
| Build plan §R-09 | Mitigation: M12 acceptance criteria explicit; future capabilities are separate gates |
| Build plan §R-11 | Workbench-fingerprint algorithm drift risk between M5 substrate and M12 implementation |
| M5 panel substrate DBCP (`00435c0`) | Live shape of mapr / mapt / workspace_tool_allowlist / evidence_source_allowlist |
| M9 fixture substrate DBCP (`620e11d`) | C-FX-1..C-FX-11 structural checks; panel-side fixture proposal vs platform-side fixture INSERT |
| M10 verifier DBCP (`ea8b708`) | Deterministic verifier service interface; called separately from panel; not invoked from panel orchestration |
| M11 reservoir ingestion DBCP (`42f702b`) | Intake queue + status-transition methods (`markConsumedByPanel` / `markRejected` / `markSuperseded`); 3-layer co_bindings discipline |

### 1.3 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits this session | ✓ — read-only |
| No DDL applied | ✓ |
| No reservoir data ingested | ✓ |
| No real MCF metric contracts | ✓ — substrate stays empty |
| No fixture rows | ✓ |
| No result rows | ✓ |
| No panel runs written | ✓ — M12 ships in a later DBCP gate |
| No BCF data touched | ✓ |
| No M13 / M14+ work | ✓ |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

---

## 2. Recommended sequencing

### 2.1 Three options on the table

| Option | Scope | T-shirt | Risk profile |
|---|---|---|---|
| **M12-A** | Panel produces dormant MCF metric package (`metric_contract` + version + bindings + filters + computed_dim_refs) + ≥ 1 self-verification fixture + cert (intake → draft) + self-verification_result row. No publication eligibility. | XL (single ambitious PR) | High R-09; many substrate-write surfaces in one gate |
| **M12-B** | Panel produces proposal payload only (`metric_authoring_panel_run` + per-model `metric_authoring_panel_transcript` rows + intake status transition). NO writes to MC / MCV / bindings / filters / computed_dim_refs / fixture / verification_result / cert. Proposal payload is the consensus JSON; materialization is a later gate. | M (focused; substrate already in M5) | Lowest R-09; smallest blast radius; substrate already verified per M5 closeout |
| **M12-C** | Same scope as M12-A but split across two PRs: panel orchestration first, materialization (cert + MC + fixture writes) second. | M + M (sequenced) | Medium; same total surface as A but staged; PR-1 = M12-B essentially |

### 2.2 Recommendation: **M12-B**

M12-B is the smallest scope that produces meaningful evidence:

- **The substrate is already live and verified.** M5 mapr + mapt + allowlists are dormant + behaviorally verified per M5 closeout. M12-B's only substrate writes are to those tables.
- **The panel orchestration is the genuinely novel work.** Three-model parallelism + workspace fingerprint computation + grounding check + tool-call transcript capture + consensus computation are XL-effort in their own right. Adding MC/fixture/cert writes in the same PR compounds R-09 risk.
- **Materialization couples to existing services.** MC writes go through the (future) MC writer; fixture writes go through the (future) fixture-authoring service that invokes M10 verifier; cert writes go through the existing M4 cert writer. Each coupling deserves its own DBCP review.
- **Reversibility.** A proposal-payload-only panel produces no MC rows; aborting / re-architecting is cheap. A panel that wrote MC + fixture + cert in one shot is much harder to unwind.
- **Foundation Invariant V is intact either way.** Per-model transcripts are append-only; consensus payload is immutable; intake status transitions are governed by M11's already-shipped guarded methods. M12-B inherits that safety without adding new write surfaces.

The materialization gate (M12-bis / M13 / amendment — operator decides naming) opens after M12-B is closed. Until then, "panel APPROVED" means the consensus payload exists and the intake row is `consumed_by_panel`; downstream materialization to MC + fixture + cert is operator-confirmed in a later gate.

### 2.3 What stays closed in M12-B v1

- No `mcf.metric_contract` / `metric_contract_version` writes
- No `mcf.metric_variable_binding` / `metric_filter_clause` / `metric_computed_dimension_ref` writes
- No `mcf.metric_self_verification_fixture` writes (panel may include proposed fixture shapes in consensus payload as descriptive content, not as INSERTs)
- No `mcf.metric_self_verification_result` writes (no verifier invocation)
- No `mcf.certification_record` writes
- No `mcf.metric_publication_eligibility_result` writes
- No BCF writes
- No PE-MC evaluator invocation
- No publication-time semantic-finality work
- **Only writes (M12-B v1)**: `mcf.metric_authoring_panel_run` + `mcf.metric_authoring_panel_transcript` + `mcf.workspace_tool_allowlist` / `evidence_source_allowlist` (initial seeding) + `mcf.metric_authoring_intake_queue.status_code` (via M11 `ReservoirIngestionService.markConsumedByPanel` / `markRejected` / `markSuperseded`)

---

## 3. Eleven decisions for operator review (D-M12-1..D-M12-11)  *(D-M12-11 added 2026-05-27 per audit `e725263`)*

### 3.1 D-M12-1 — Panel execution model

**Question.** Synchronous operator-triggered run vs async queue?

**Recommendation.** **Synchronous, operator-triggered.** A single panel run executes three models in parallel; expected wall-clock is bounded (~30–180 seconds depending on tool calls). Operator invokes via service method (and later CLI / REST in the materialization gate). No background worker, no queue, no retry orchestration in v1. If a run exceeds an operator-configurable timeout, it returns `OPERATOR_REVIEW` with reason `panel_timeout`; intake row stays `pending`.

**Rationale.** R-09 mitigation: queueing infrastructure is overbuilding for v1. Per-run synchronous semantics match BCF B6 panel patterns. Adds zero new substrate surfaces. Async queue is a future amendment if call volume demands it.

### 3.2 D-M12-2 — Intake source

**Question.** Consume `mcf.metric_authoring_intake_queue` pending rows only, vs allow operator-direct panel run (no intake row)?

**Recommendation.** **Pending-row consumption only.** M12 v1 panel runs are always triggered by an intake row UID. Operator-direct submission already exists via the M11 CLI; it lands the candidate in the intake queue first; then M12 picks it up. Single code path.

**Rationale.** Single intake discipline keeps panel runs traceable to a reservoir-provenance row (addendum guardrail #6 satisfied via M11 → M12 mapr provenance copy). Operator-direct-without-intake adds a second path with no provenance — defeats addendum guardrail #6.

### 3.3 D-M12-3 — Three-model role contract

**Question.** Fixed roles / model IDs / transcript capture / consensus payload shape?

**Recommendation.** Three roles per build plan §M12 line 282: **Maker / Checker / Moderator**.

- **Maker** proposes the candidate MC structure (formula AST + bindings + grain + filters + temporal gate + computed_dimension_refs + proposed fixture shapes).
- **Checker** independently re-derives a proposal from the same workspace + verifies grounding citations + checks defect codes.
- **Moderator** computes consensus (3-way verdict aggregation) + adjudicates when Maker + Checker diverge.
- Model identity v1: one model per role, three distinct vendors per `MCF requirements §11.3.5` ("three-vendor model identity per panel run"). Operator-configurable via service constructor + env vars. v1 defaults: Maker=Anthropic/claude-opus-4.7, Checker=OpenAI/gpt-5, Moderator=Google/gemini-2.5-pro. Vendor + version + tier captured in `model_identity_json`.
- Transcript capture: per-role `mcf.metric_authoring_panel_transcript` row with full tool-call trace + each tool's response + per-step reasoning + verdict + defect_code (if rejected). One transcript row per model per run; 3 rows per panel run.
- Consensus payload shape (`mcf.metric_authoring_panel_run.consensus_payload_json`): `{verdict_code, defect_code, per_role_verdicts: [{role, verdict, defect, grounding_claims: [...]}], grounding_check_passed, workspace_fingerprint_hash, candidate_summary: {...}}`. Schema locked in DBCP §7.

### 3.4 D-M12-4 — Output scope for M12 v1

**Question.** Create `metric_contract` + `metric_contract_version` + binding rows + M9 fixtures + cert, or stop at certified proposal payload pending later gates?

**Recommendation.** **Stop at proposal payload + intake status transition.** Per M12-B recommendation (§2.2). No MC / MCV / fixture / cert writes. The consensus payload IS the proposal artifact; materialization is a deferred gate.

The consensus payload includes everything the materialization gate needs as input: the proposed formula AST, the proposed bindings, the proposed grain, the proposed filters, the proposed temporal gate, the proposed computed_dimension_refs, the proposed fixture shapes (Section A/B/C structure per §12.4 — values descriptive, not authoritative), and the panel's verdict + defect codes + grounding citations. Materialization reads this payload + invokes the (future) MC writer + the (future) fixture-authoring service + the existing M4 cert writer.

### 3.5 D-M12-5 — Certification boundary

**Question.** Does M12 write `certification_record` directly or delegate to the existing M4 cert writer?

**Recommendation.** **Out of M12 v1 scope.** Per §3.4. When materialization lands, it delegates to M4 cert writer (already live with `createMetricDraft` / `approveForActivation` / `activateMetric` / `supersedeMetric` methods). M12 v1 does NOT call cert writer; M12 v1 does NOT write to `mcf.certification_record`.

Hand-off shape (for materialization-gate spec): materialization service reads `consensus_payload_json` from the panel run row + calls `McfCertWriterService.createMetricDraft(...)` with the panel run uid as the cert's `panel_run_uid`. Cert action code = `metric_create`. The cert binds the new MC + MCV to the panel run as the authoring evidence.

### 3.6 D-M12-6 — Fixture authoring

**Question.** Required minimum fixture count and use of M9 C-FX engine before INSERT?

**Recommendation.** **Panel PROPOSES fixture shapes in the consensus payload; does NOT INSERT.** Per §12.2 "panel proposes, platform verifies": the panel may include `proposed_fixtures: [{section_a, section_b, section_c}, ...]` in `consensus_payload_json` as descriptive content. The Maker model uses `source_reality.summarize` + `evidence.search` tools to draft realistic fixture rows. The Checker validates the proposed fixture against the proposed package signature using the M9 `FixtureStructuralCheckService.runStructuralChecks` engine (read-only invocation — no INSERT) and includes the structural-check result in its transcript.

Minimum fixture count for `APPROVE_FOR_DRAFT`: **≥ 1 proposed fixture** that passes C-FX-1..C-FX-11 structurally. Materialization later writes the fixture row + invokes M10 verifier.

For `OPERATOR_REVIEW` and `REJECT_*`, fixture proposal is optional.

### 3.7 D-M12-7 — Verifier invocation

**Question.** Does M12 call M10 verifier immediately after fixture INSERT, or defer to a later gate?

**Recommendation.** **Defer to a later gate.** Per §3.4 + §3.6, M12 v1 does not INSERT fixtures, so there is no fixture row to verify. The M10 verifier service (live + dormant) is invoked by the materialization gate after it writes the fixture row.

Read-only invocation of M9 `FixtureStructuralCheckService.runStructuralChecks(context, body)` is permitted inside the panel for Checker validation (per §3.6) — this does not require M10 verifier and produces no result row.

### 3.8 D-M12-8 — Failure / rejection logging  *(amended 2026-05-27 per audit `e725263`)*

**Question.** Use existing panel-transcript / mapr patterns; status update on M11 intake row?

**Recommendation.**

- **Per-model REJECT_***: captured in `mcf.metric_authoring_panel_transcript.transcript_payload_json` with `verdict_code` + `defect_code` (one of the 11 closed-enum codes per §11.3.4: `MC_DEFECT_GRAIN_INCOHERENT` / `MC_DEFECT_VARIABLE_UNBINDABLE` / `MC_DEFECT_FORMULA_TYPE_MISMATCH` / `MC_DEFECT_UNIT_PROMOTION` / `MC_DEFECT_CROSS_GRAIN_AGGREGATION` / `MC_DEFECT_IDENTITY_COLLISION` / `MC_DEFECT_TEMPORAL_GATE_INCOHERENT` / `MC_DEFECT_COMPUTED_DIMENSION_UNRESOLVED` / `MC_DEFECT_BC_SUPERSEDED` / `MC_DEFECT_PE_MC_1_UNGROUNDED` / `MC_DEFECT_TRANSCRIPT_FABRICATION`).
- **Aggregate consensus verdict**: written to `mcf.metric_authoring_panel_run.consensus_payload_json` with `verdict_code` ∈ {`APPROVE_FOR_DRAFT`, `OPERATOR_REVIEW`, `REJECT_<code>`}.
- **Intake row status transition** (via M11 `ReservoirIngestionService`) — **corrected per audit**:
  - All three models `REJECT_*` → `markRejected(intake_queue_uid, "Panel rejected: <consensus defect_code>. <≥ 20 char reason>")`
  - `APPROVE_FOR_DRAFT` → intake row **stays at `pending`**; M12.5 materialization service calls `markConsumedByPanel(intake_queue_uid)` only AFTER `McfCertWriterService.createMetricDraft(...)` succeeds. The intake row's `consumed_by_panel` status must mean *"materialized into MCF substrate"*, not *"panel approved a proposal"* — otherwise the status is misleading when materialization is deferred.
  - `OPERATOR_REVIEW` → intake row stays at `pending`; operator inspects panel run in audit UI (M16) and decides next action. **No automatic state transition.**
  - Mixed (e.g. 2 APPROVE, 1 REJECT; or grounding check fail at panel-level) → intake row stays at `pending`; treated as `OPERATOR_REVIEW`.
- **Mid-run failure** (e.g. tool error, model timeout): partial transcripts written for whichever models completed; aggregate verdict = `OPERATOR_REVIEW` with reason `panel_failure_<cause>`; intake row STAYS at `pending`. Operator can re-trigger.

**Hard rule (lock at DBCP):** `markConsumedByPanel` is **FORBIDDEN** in M12 v1 service code (see HA-6 in §6). The only intake-status writes M12 v1 may perform are `markRejected` (on all-reject) and no-op (otherwise). M12.5 owns `markConsumedByPanel`.

### 3.9 D-M12-9 — Idempotency / retry model

**Question.** Idempotent behavior for panel runs + intake consumption?

**Recommendation.**

- **Panel runs are immutable per Invariant V** (already enforced by M5 substrate triggers `trg_mapr_immutability` + `trg_mapt_immutability`).
- **Per-intake-row idempotency** comes for free from M11's status transition guards: `ReservoirIngestionService.markConsumedByPanel` raises `InvalidStatusTransitionError` if the intake row is not `pending`. So a second panel run against an already-consumed intake row fails fast at transition time.
- **Service-level method idempotency**: `MetricAuthoringPanelService.runPanel(intakeQueueUid)` reads intake row at start; throws `InvalidStatusTransitionError` if status ≠ `pending`. Concurrent invocations race on the M11 transition guard; first writer wins.
- **No retry orchestration in v1.** Mid-run failure → operator manually re-triggers. Substrate's append-only discipline preserves the failed run's transcripts as historical evidence; the new run gets a new `panel_run_uid`.

### 3.10 D-M12-10 — Safety gates

**Question.** Explicit no-go list?

**Recommendation.** Hard rules enforced in M12 v1 (service-side discipline + DBCP §X explicit prohibitions):

| Forbidden write | Enforcement |
|---|---|
| `mcf.metric_contract` / `metric_contract_version` / `metric_variable_binding` / `metric_filter_clause` / `metric_computed_dimension_ref` | M12 v1 service does NOT import the (future) MC writer; substrate writes excluded by code |
| `mcf.metric_self_verification_fixture` / `metric_self_verification_result` | M12 v1 service does NOT import fixture writer; M10 verifier service NOT invoked |
| `mcf.certification_record` / `mcf.metric_publication_eligibility_result` | M12 v1 service does NOT import M4 cert writer or PE-MC evaluator |
| BCF substrate (`concept_registry.*`) | MCF reads BCF via bcf.* tools only; never writes |
| `contract.panel_output_record` (BCF panel rows) | MCF reads only |

Verifiable post-apply via integration test that asserts row counts in all the above tables == 0 after a M12 panel run.

### 3.11 D-M12-11 — Rejection log venue  *(added 2026-05-27 per audit `e725263`)*

**Question.** Where do MCF panel rejections live? BCF uses `contract.authoring_panel_rejection_log` with `scope_code IN ('bf_bo', 'cf', 'mapping')` — the enum lacks `mc`. Three options.

| Option | Scope | New DDL | Pros | Cons |
|---|---|---|---|---|
| **A — Reuse existing M5 substrate** (recommended default) | All-reject case: aggregate REJECT verdict + defect_code in `mapr.consensus_payload_json`; per-model defect codes in `mapt.transcript_payload_json`; intake row carries `markRejected` reason text (already required ≥ 20 chars by M11 substrate) | None | Zero substrate change; M5 closeout already verified the rapr/mapt immutability + 0-row dormancy; intake substrate already has rejected-reason CHECK; preserves audit trail across 3 tables without adding a 4th | Requires query joins across mapr + mapt + intake to reconstruct "all panel rejections by defect" reports |
| **B — Create `mcf.metric_authoring_panel_rejection_log`** | New mcf-scoped sibling table for rejection-summary queries | 1 new mcf.* table (small DDL gate similar to M11) | Single-source query surface; MCF-independent lifecycle | Adds 1 table + 1 DDL gate; M5 substrate already captures the same data — risk of duplication / dual-source-of-truth |
| **C — Widen `contract.authoring_panel_rejection_log` enum** | Add `'mc'` to scope_code | Substrate amendment to BCF-shared table | Single shared rejection-log convention | **Not recommended** — conflicts with MCF requirements §3.8 (no-cross-framework-write-coupling); BCF M5 closeout treated this table as BCF-scoped; widening reverses that decision |

**Recommendation.** **Option A** — reuse the M5 substrate. M5 already captures everything needed: `mapr.consensus_payload_json` for the aggregate verdict + `defect_code`; per-model `mapt.transcript_payload_json` for per-model defects + grounding violations; `mcf.metric_authoring_intake_queue.status_reason_text` for the operator-readable rejection summary (already CHECK-constrained ≥ 20 chars). **If** the M12 DBCP analysis surfaces a concrete query / audit need that Option A cannot satisfy, fall back to Option B (small DDL gate, mcf-scoped sibling). **Never** pick Option C.

Defer Option-B-vs-Option-A binary decision to M12 DBCP §X after a concrete query-pattern audit. The default for v1 is Option A.

---

## 4. Substrate impact (M12-B v1)

### 4.1 No new tables

M12-B v1 ships **zero new tables**. All writes target existing substrate from M5 + M11.

### 4.2 Possible additions to consensus_payload_json schema

The M5 mapr `consensus_payload_json` column is already `jsonb NOT NULL`. M12 DBCP defines the canonical v1 schema. Candidate top-level fields:

- `panel_algorithm_version` (e.g. `mcf-panel-v1`)
- `verdict_code` enum
- `defect_code` (when applicable; one of the 11 closed enum codes)
- `per_role_verdicts: [{role: 'maker'|'checker'|'moderator', verdict, defect, grounding_claims: [...], tool_call_count}]`
- `grounding_check_passed: bool`
- `grounding_violations: [...]` (if check failed)
- `candidate_summary: {formula_ast_sketch, grain_entity_id, variable_count, filter_count, temporal_gate_shape, proposed_fixtures_count, kpi_catalog_source_seed: {function_code, subfunction_code, metric_name}}`
- `intake_queue_uid` (back-reference for traceability)

No CHECK constraints required at substrate level for the JSON shape — DBCP service-side schema validation only. Substrate-side JSONB CHECKs are reserved for safety enforcement (per M11 `co_bindings` pattern), not schema typing.

### 4.3 Possible additions to transcript_payload_json schema

Per-model transcripts (`mcf.metric_authoring_panel_transcript.transcript_payload_json`) schema:

- `tool_calls: [{tool_code, tool_version, request, response, latency_ms, called_at}]`
- `reasoning_trace: [...]` (per-step model reasoning)
- `verdict_code` + `defect_code` (per-model)
- `proposal_payload: {formula_ast, bindings, grain, filters, temporal_gate, computed_dim_refs, proposed_fixtures}` (Maker only; Checker writes `verification_payload`; Moderator writes `consensus_payload`)
- `model_call_metadata: {model_id, model_version, total_tokens, finish_reason, etc.}`

Same: no substrate CHECK on shape; DBCP service-side schema validation.

### 4.4 Workspace fingerprint algorithm

Per M5 mapr `workbench_fingerprint_hash` column + build plan R-11 (algorithm drift risk). DBCP defines `mcf-workbench-v1` algorithm:

```
sha256(
  tool_allowlist_snapshot_hash    ||  // sha256 over rows in workspace_tool_allowlist active at run start
  evidence_allowlist_snapshot_hash ||  // sha256 over rows in evidence_source_allowlist active at run start
  bcf_registry_snapshot_id        ||  // BCF snapshot id at run start (read-only handle from BCF)
  operator_context_text_hash      ||  // sha256 over operator-supplied free-text guidance
  policy_version                  ||  // mcf-panel-v1 string
  prompt_version                     // operator-controlled prompt revision id
)
```

All three model transcripts in a single panel run MUST carry an identical `workbench_fingerprint_hash`. Mismatch → consensus invalid → `OPERATOR_REVIEW`. Algorithm constant is shared between M5 substrate (no enforcement) and M12 service (computation + comparison).

---

## 5. Service shape sketch (DBCP scope)

`MetricAuthoringPanelService` interface (DBCP details):

```typescript
class MetricAuthoringPanelService {
  async runPanel(
    intakeQueueUid: string,
    opts: { operatorContextText?: string; promptVersion?: string },
    deps: { tx, reservoirIngestionService, fixtureStructuralCheckService, ... }
  ): Promise<{ panel_run_uid: string; verdict_code: PanelVerdict; consensus_payload: ConsensusPayload }>;
}
```

Internal flow:

1. Read intake row by UID; assert `status_code = 'pending'` (M11 guard pattern).
2. Compute `workbench_fingerprint_hash` from allowlists + BCF snapshot + operator context.
3. Initialize three model agents (Maker / Checker / Moderator) with role-scoped prompts + closed tool set.
4. **Parallel execution** (per §3.3 D-M12-3): all three models run concurrently against the workspace. Each model's tool calls are captured to its own transcript. Per `MCF requirements §11.3.6` Q35 — parallel + independent transcripts.
5. After all three return verdicts, run grounding check: every claim in each model's proposal MUST trace to a tool call in that model's transcript. Failure → grounding_check_passed = false → consensus `OPERATOR_REVIEW`.
6. Compute consensus per §3.3 (Moderator's aggregation): if all three `APPROVE_FOR_DRAFT` + grounding pass → consensus `APPROVE_FOR_DRAFT`. If all three `REJECT_*` → consensus `REJECT_<majority_defect>`. Otherwise → `OPERATOR_REVIEW`.
7. INSERT `mcf.metric_authoring_panel_run` with consensus_payload + workbench_fingerprint + intake_queue_uid + 4 reservoir-provenance fields copied from intake row (satisfies M5 NF1 all-or-none CHECK + addendum guardrail #6).
8. INSERT 3 × `mcf.metric_authoring_panel_transcript` rows.
9. Transition intake status per amended §3.8: call `markRejected` ONLY when all three models REJECT (with composed status_reason_text ≥ 20 chars); leave intake at `pending` on `APPROVE_FOR_DRAFT` / `OPERATOR_REVIEW` / mid-run failure. **Never** call `markConsumedByPanel` (HA-6). M12.5 owns that transition after materialization.
10. Return panel_run_uid + verdict.

---

## 6. Hard assertions for M12 DBCP (HA-1..HA-8)  *(added 2026-05-27 per audit `e725263`)*

To prevent building a dead-end panel that collides with the still-live legacy metric authoring path or prematurely materializes substrate, the M12 DBCP must lock the following hard assertions. Each is enforced by service-code structure + integration tests; HA-5 + HA-8 are also enforced by substrate constraints already shipped in M5 + M11.

| # | Assertion | Primary enforcement | Test verification |
|---|---|---|---|
| **HA-1** | M12 v1 panel service does **NOT** import `MetricDefinitionService` / `MetricDefinitionRepository` / any other legacy `metric.*` writer | Service code import allowlist + ESLint rule | Static import-graph audit in CI; unit test that introspects `require.cache` shows no legacy import |
| **HA-2** | M12 v1 panel service does **NOT** import `McfCertWriterService` (materialization is M12.5; cert writes belong to M12.5) | Same | Same |
| **HA-3** | M12 v1 panel service does **NOT** import `MetricSelfVerificationService` (no M10 verifier invocation at panel time; only read-only invocation of M9 `FixtureStructuralCheckService` is allowed for Checker structural validation) | Same | Same |
| **HA-4** | M12 v1 panel reads BCF concepts **ONLY** via the `bcf.*` tool surface (`bcf.search_entity` / `search_business_concept` / `read_entity` / `read_business_concept` / `reachability_check`) — never raw SQL against `concept_registry.*` | Tool surface is the only import path for BCF reads | Integration test that monitors DB query log and asserts zero direct `concept_registry.*` SELECTs from the panel service stack |
| **HA-5** | M12 v1 panel writes **ONLY** to `mcf.metric_authoring_panel_run` + `mcf.metric_authoring_panel_transcript` (plus optional `mcf.metric_authoring_panel_rejection_log` IF D-M12-11 escalates to Option B). Plus intake-status transition via `markRejected` only (per HA-6). No other `mcf.*` / `contract.*` / `metric.*` table is written | Service code structure | Integration test asserts post-panel-run rowcount on `mcf.metric_contract` / `metric_contract_version` / `metric_variable_binding` / `metric_filter_clause` / `metric_computed_dimension_ref` / `metric_self_verification_fixture` / `metric_self_verification_result` / `certification_record` / `metric_publication_eligibility_result` / `metric_supersession` / `contract.panel_output_record` / `contract.authoring_panel_rejection_log` / `metric.metric_definition` / `metric.metric_knowledge` / `metric.metric_binding` == **0 row delta** |
| **HA-6** | `markConsumedByPanel` is **FORBIDDEN** in M12 v1 service code. Only `markRejected` (all-reject path) may be invoked from M12. M12.5 owns `markConsumedByPanel` after successful materialization | Service code grep + import audit | Unit test asserts the panel service module's source text contains no `markConsumedByPanel` call site |
| **HA-7** | Panel `consensus_payload_json` schema is locked in M12 DBCP §X and consumed unchanged by the future M12.5 materialization service. Schema changes are version-bumped (`panel_algorithm_version: mcf-panel-v1` → `v2`); no breaking-shape changes within a major version | DBCP §X explicit JSON Schema document + service-side validation at write time | Round-trip test: produce a known-shape `consensus_payload_json`, hand to a mock materialization service that asserts every expected field is reachable |
| **HA-8** | M12 v1 panel reads reservoir-provenance from M11 intake row + copies all 4 fields (`reservoir_name`, `reservoir_entry_id`, `reservoir_provenance_source_json`, `reservoir_confidence_band`) into `mapr.reservoir_*` columns (addendum guardrail #6). M5 substrate's `mapr_reservoir_all_or_none_chk` CHECK already enforces all-or-none | Substrate CHECK + service code | Integration test asserts mapr rows have all 4 fields populated when the panel run originates from a M11 intake row |

Verification harness (DBCP §X): one composite integration test that runs the M12 panel against a synthetic intake row, asserts (a) only the 2–3 allowed tables get written; (b) all other tables in HA-5's list are 0-row delta; (c) intake row is `pending` (APPROVE / REVIEW path) or `rejected` (all-reject path), never `consumed_by_panel`; (d) mapr carries the 4 reservoir-provenance fields copied from intake.

---

## 7. Post-BCF Metric Workflow Wiring Boundary  *(added 2026-05-27 per audit `e725263`)*

This section establishes the hard boundary between M12 (panel proposal-only) and the broader metric-authoring transition that the BCF → MCF arc requires. M12 itself does NOT execute the transition; M12.5 does. M12 must not leak across the boundary.

### 7.1 Legacy metric writes — status during M12

| Surface | Status during M12 | Status after M12.5 closeout |
|---|---|---|
| `POST /api/metric-catalog/definitions` (legacy author endpoint) | **LIVE** — unchanged; operators may continue authoring via legacy until M12.5 ships the bridge | Deprecation header (`Sunset: <date>; use MCF intake + panel + materialization`); eventual HTTP 410 in M17 |
| `MetricDefinitionService.create()` direct writes to `metric.metric_definition` | **LIVE** — unchanged | Production-side disabled (allowed only in seed loader paths) |
| `metric.enrichment_job` queue | **LIVE** — unchanged | Decommissioned (enrichment becomes panel-side via tool calls) |
| 9 seed loaders (`src/registry/seed/metric-kpi-*.ts`) writing `metric.metric_definition` | **LIVE** — unchanged; re-targeting to M11 intake is operator-driven (not a gate) | Optionally re-targeted to `ReservoirIngestionService.ingestFromSeedMetrics` (already supported by M11) |
| Direct INSERT into legacy `contract.metric_contract` (780-row historical table) | Already forbidden by convention (DEC-c3e57f Decision 2); no service does this today | Same |
| bc-admin metric API surfaces (5 files; `metric-definitions.ts` / `metric-catalog.ts` / `metric-reference.ts` / `metric-verification.ts` / `seed-metrics.ts`) | **LIVE** — unchanged; bc-admin must NOT invoke any MCF panel API in M12 v1 | Migration to MCF read endpoints lands in M16 (audit UI); write surface migration lands in M17 |

### 7.2 Legacy metric reads — preserve during M12 + M12.5

Reads continue during the dual-authority transition:

- `GET /api/metric-catalog/definitions` (legacy KPI catalog reads) — preserved until bc-admin migration (M16+)
- `boundary/metric.service.ts` legacy MC reads — preserved (tenant runtime evaluation must not break)
- `ReadinessLedgerService` fan-out for legacy MCs — preserved
- `chain-status.service.ts` D305 SSOT reads — preserved (chain reporting must continue working across the transition)

### 7.3 M12 owns NONE of the bridge work

The following are explicitly **out of M12 scope** and live in M12.5:

- Deprecation handling on `POST /api/metric-catalog/definitions`
- Legacy-vs-MCF read fallback policy ("when consumer asks for MC by name, which table is authoritative?")
- Tenant runtime migration from legacy MC reads to MCF MC reads
- bc-admin frontend changes
- 9 seed loader re-targeting decisions
- Dual-write reconciliation (none planned — MCF authors net-new MCs; legacy corpus is historical-only)

### 7.4 SC / AC — no structural change in this audit

Codebase exploration confirmed (per audit `e725263` §2.4 + §2.5):

- `contract.source_contract` has **no** metric-related columns / FKs / joins
- `contract.admission_contract` has **no** metric-related columns / FKs / joins

M12 v1 must not introduce any SC / AC reads or writes. M12 DBCP must include **explicit no-op grep/test assertions**:

- Grep assertion in CI: panel service source text contains zero matches for `source_contract` / `admission_contract` / `SourceContract*Service` / `AdmissionContract*Service` / `sc.*` table-name patterns
- Integration test assertion: rowcount delta on `contract.source_contract` + `contract.admission_contract` + any SC/AC ledger tables == 0 after a panel run

If a future M12 design iteration discovers an SC/AC coupling requirement (none anticipated), it must be raised as a new decision and reviewed before DBCP — not silently added.

### 7.5 OC / CC — no structural change; binding shape change deferred to M12.5

Per audit:

- OC: no FK to metric; event-driven coupling via `ReadinessLedgerService` (untouched)
- CC: no FK to metric; legacy `metric.metric_binding.canonical_contract_id` FK remains informational/historical-only

MCF MC-to-BCF concept binding uses `mcf.metric_variable_binding.bound_business_concept_id` (uuid; NOT a physical FK to `concept_registry.*` — confirmed by live substrate inspection, only FK on the table is `fk_mvb_mcv` to `metric_contract_version`) plus optional `bound_entity_id` (uuid; same — no physical FK). The unenforced-uuid pattern is intentional: BCF is the authority on concept lifecycle; MCF substrate does not lock a cross-framework FK (per MCF requirements §3.8 no-cross-framework-write-coupling).

M12 panel proposals will populate `bound_business_concept_id` + `bound_entity_id` as uuids resolved via the `bcf.*` tool surface. **M12.5** (not M12) does the actual INSERT.

---

## 8. Risks (preflight-time; DBCP refines)

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-M12-1 | Three-model parallel execution: real-world model latency variance causes long runs | Medium | Operator-configurable per-model timeout; partial-transcript capture on timeout; consensus `OPERATOR_REVIEW` on any timeout |
| R-M12-2 | Workspace fingerprint algorithm drift (build plan R-11) | Medium | M5 substrate + M12 service share a single algorithm-version constant; DBCP locks the byte-canonical input order |
| R-M12-3 | Grounding check false-negatives (claim ≠ tool call due to fuzzy match) | Medium | DBCP specifies exact claim-to-tool-call matching algorithm; calibration sampling against known-grounded fixtures |
| R-M12-4 | Tool surface drift (new tool added without ADR) | Low | `workspace_tool_allowlist` table is authoritative; tools not in allowlist are blocked at service-init time |
| R-M12-5 | Defect-code taxonomy v1 incompleteness | Low | 11 codes enumerated per §11.3.4; DBCP adds `MC_DEFECT_OTHER` only with operator approval; v2 amendment if patterns emerge |
| R-M12-6 | Model vendor outages | Low | Per-vendor degradation: if one vendor's model fails, panel run returns `OPERATOR_REVIEW` (cannot meet three-vendor rule); intake row stays `pending` for retry |
| R-M12-7 | Cost ceiling (three models × tokens × parallel calls) | Medium | DBCP locks per-run token budget + operator-configurable monthly ceiling; over-budget run aborts to `OPERATOR_REVIEW` |
| R-M12-8 | BCF Registry snapshot read pattern | Low | M12 reads BCF via bcf.* tool surface only; snapshot id captured in workbench fingerprint |
| R-M12-9 | Premature materialization pressure (operator wants MC rows in v1) | High | M12-B recommendation locks v1 to proposal-only; materialization is a separate operator-authorized gate |
| R-M12-10 | Operator-direct submission bypass attempt | Low | M11 CLI is the only operator-direct path; intake row required for panel run (per D-M12-2) |

---

## 9. Sequencing per established pattern  *(amended 2026-05-27 per audit `e725263`)*

1. **M12 preflight** ← THIS DOC
2. Operator review of D-M12-1..D-M12-11
3. M12 DBCP (full design — service + tests + 3-vendor model fallback story + workspace fingerprint algorithm spec + consensus payload schema + transcript schema + grounding-check algorithm + HA-1..HA-8 hard assertions per §6)
4. M12 implementation PR (NO actual model calls in test suite; mocked agents)
5. **No DDL apply gate** — M12-B writes only to existing M5 substrate tables; no new DDL (Option A for D-M12-11). If DBCP escalates D-M12-11 to Option B, then 1 small-DDL gate is added for the new mcf-scoped rejection table.
6. M12 evidence PR (smoke run vs `bc_platform_dev` with mocked agents; 0 real model calls; verify substrate writes + intake transitions; HA-5 row-count assertion confirmed)
7. M12 closeout
8. **NEW GATE — M12.5 materialization + legacy bridge.** Preflight → DBCP → impl PR → apply → evidence → closeout. M12.5 owns: `MetricAuthoringMaterializationService` reads M12 panel `consensus_payload_json` and calls `McfCertWriterService.createMetricDraft(...)` with `panel_run_uid` as authoring evidence; writes `mcf.metric_contract` + version + bindings + filters + computed_dim_refs + first proposed fixture + `certification_record(action_code=metric_create)` in one TX (M4 cert writer already does this); invokes M9 `FixtureStructuralCheckService.runStructuralChecks` + M10 `MetricSelfVerificationService.verifyFixture`; calls `ReservoirIngestionService.markConsumedByPanel(intake_queue_uid)` after substrate write succeeds; defines explicit legacy-bridge contract (deprecation header on `POST /api/metric-catalog/definitions`; legacy-vs-MCF read fallback policy). M12.5 is where the post-BCF workflow / wiring transition actually lands in the codebase.
9. **Then**: M13 PE-MC evaluator (gated on M12.5 + M10) — now has real materialized MCs to evaluate
10. **Then**: M14 publication path; M15 supersession; M16+ console

---

## 10. What unblocks after M12-B

- Real consensus payloads exist in `mcf.metric_authoring_panel_run` with full per-model transcripts
- Operator can audit panel reasoning end-to-end (read mapr + 3 mapt rows)
- Intake queue can drain (`pending` → `consumed_by_panel` / `rejected`)
- Materialization gate becomes the next operator-authorized gate, with the proposal payload as its input contract
- M13 PE-MC evaluator can be specified against the proposal-payload shape

---

## 11. Open questions for DBCP

1. Exact prompt template per role (Maker / Checker / Moderator) — locked in DBCP §X.
2. Exact tool-call response schema per tool (10 tools) — locked in DBCP §X.
3. Grounding-check claim-extraction algorithm (regex / structured / semantic) — locked in DBCP §X.
4. Cost ceiling defaults — locked in DBCP §X.
5. Calibration sampling rate v1 default (per MCF requirements §11.3.6 Q33) — locked in DBCP §X.
6. Per-vendor fallback behavior on outage (degrade vs hard-fail) — locked in DBCP §X.
7. Test strategy for three-model parallel agents (record + replay vs full mock vs canned consensus fixtures) — locked in DBCP §X.

---

## 12. Operator approval surface  *(amended 2026-05-27 per audit `e725263`)*

Before opening the M12 DBCP gate, operator confirms D-M12-1..D-M12-11:

| # | Decision | Recommendation |
|---|---|---|
| D-M12-1 | Panel execution model | Synchronous operator-triggered |
| D-M12-2 | Intake source | Pending intake-queue rows only |
| D-M12-3 | Three-model roles | Maker / Checker / Moderator (3 vendors) |
| D-M12-4 | Output scope v1 | Proposal payload only (M12-B); materialization is **NEW gate M12.5** (§9 step 8) |
| D-M12-5 | Certification boundary | Deferred to M12.5 |
| D-M12-6 | Fixture authoring | Panel proposes shapes; no INSERT |
| D-M12-7 | Verifier invocation | Deferred to M12.5 |
| D-M12-8 | Failure / rejection logging | **AMENDED**: `markRejected` only on all-reject; otherwise no-op; `markConsumedByPanel` is M12.5's (per HA-6) |
| D-M12-9 | Idempotency / retry | Inherited from M11 status guards + M5 immutability triggers |
| D-M12-10 | Safety gates | Hard prohibition list per §3.10; verified by HA-1..HA-8 (§6) |
| **D-M12-11** | **Rejection log venue** (3 options A / B / C) | **NEW**: default Option A (reuse mapr + mapt + intake reason text; zero new substrate); escalate to Option B only if M12 DBCP query-pattern audit proves Option A insufficient; never Option C |

Operator may accept all, accept-with-modifications, or override individual recommendations. M12 DBCP gate opens after this set is locked.

---

## 13. What stays closed (gate boundary)  *(amended 2026-05-27 per audit `e725263`)*

| | |
|---|---|
| M12 DBCP | not opened by this preflight |
| M12 implementation PR | not opened |
| **M12.5 (materialization + legacy bridge)** | CLOSED — gated on M12-B closeout + operator authorization |
| M13 PE-MC evaluator | CLOSED — gated on M12.5 |
| M14 publication path | CLOSED |
| M15 supersession | CLOSED |
| M16+ operator console | CLOSED |
| Real model API calls | CLOSED — design phase only |
| Real MCF metric contracts | CLOSED — substrate stays empty |
| Fixture rows | CLOSED |
| Verification result rows | CLOSED |
| Certification record rows | CLOSED |
| Reservoir data ingestion | CLOSED — M11 substrate dormant per closeout |
| BCF data changes | CLOSED — 24 panel + 1 rejection log preserved across the MCF arc |
| Legacy metric write paths (`POST /api/metric-catalog/definitions`; `MetricDefinitionService.create`; `metric.enrichment_job`) | LIVE during M12 (legacy authoring continues unchanged); deprecation handling lands in M12.5 — NOT in M12 |
| bc-admin frontend metric API surfaces | LIVE during M12 (no MCF endpoint exposed by M12 v1); migration lands in M16 (read) + M17 (write) |
| SC / AC reads from panel | CLOSED — zero metric coupling confirmed; M12 DBCP must include grep + integration-test assertions per §7.4 |
