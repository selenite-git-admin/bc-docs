---
uid: metric-context-framework-service-ification-dbcp
title: MCF — Service-Ification DBCP (PR-S1; define HTTP/API + bc-admin UI + standing authorization to prevent “library-of-services-invoked-by-scripts” end state)
description: Governance DBCP authored alongside the MCF Panel-Framework Calibration arc (PR-G1 merge `4a241eba`) to lock the path from “MCF engine services invoked only by one-off scripts + per-run DBCPs” to “MCF authoring as a real platform service.” Records current truth that MCF engine services exist as NestJS classes (M11 ReservoirIngestionService, M12 MetricAuthoringPanelService, M12.5 MetricAuthoringMaterializationService, M13 MetricPublicationEligibilityEvaluatorService, M10 MetricSelfVerificationService, McfCertWriterService, ProductionPanelToolSurface) but the invocation path is still script + per-run authorization DBCP per the PR #28 → PR #168 bootstrap pattern. That pattern is correct for first-real-* runs (provenance proof, trust-path lock-in) but is NOT the routine operator workflow. Defines the service surface: HTTP/REST controllers wrapping the engine services; bc-admin UI pages for intake queue + panel-run inspector + draft review + materialization actions; NestJS `McfModule` consolidating per-gate services for DI; standing operator authorization model (role-based + per-action audit) replacing per-run DBCPs for routine use. Locks the cutover criterion (when per-run DBCPs stop being required) and the sequencing alongside the calibration arc (PR-G1 / PR-C1 / PR-C2 / PR-C3 remain valid engine work; new PR-S1 / PR-C4 / PR-A1 add service surface). Explicitly does NOT downgrade governance: DBCPs remain required for architectural changes, first-of-kind gates, and exceptional overrides; the service path is for ROUTINE MCF authoring after cutover. **NOT EXECUTED** — docs-only governance DBCP. No bc-core code change, no bc-admin code change, no provider calls, no `runPanel()`, no M12.5 / M13 / M14, no metric contract, no rollback, no tenant DB, no substrate mutation.
status: proposed
date: 2026-05-30
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-service-ification
supersedes:
superseded_by:
---

# MCF — Service-Ification DBCP (PR-S1)

> Parallel to the MCF Panel-Framework Calibration arc. Does NOT supersede PR-G1 (merge `4a241eba`) — extends it.
>
> Adds three new PRs to the arc: this one (PR-S1, governance), PR-C4 (bc-core controllers + McfModule), and PR-A1 (bc-admin MCF pages). Existing PR-G1 / PR-C1 / PR-C2 / PR-C3 are unchanged.

## 1. Scope

### 1.1 Question this DBCP answers

> The MCF engine services exist as NestJS classes inside `bc-core/src/registry/mcf/` (M11 / M12 / M12.5 / M13 / M10 / cert writer / production tool surface / 10+ pure helpers). They are well-typed, DI-friendly, and (after PR-C2 + PR-C3) will be approval-capable. But the only way to invoke them today is via one-off scripts (e.g. `scripts/mcf-m12-first-real-run.mjs`) authorized by per-run bc-docs-v3 DBCPs (PR #29 pattern). The calibration arc PR-G1 → PR-G3 preserves the same script + per-run-DBCP pattern at PR-E1 / PR-G2 / PR-E2 / PR-G3. **Without service-ification, the MCF arc ships an engine that nobody can invoke routinely.** What is the path to add HTTP / bc-admin / standing-authorization service surface alongside the calibration arc, and what is the cutover criterion that stops the per-run-DBCP requirement?

### 1.2 In scope

- Current-truth statement about the MCF service surface gap at bc-core merge `16cf3781` (post PR #168)
- The HTTP / REST API surface for MCF authoring (M11 intake / M12 panel / M12.5 materialization / M13 PE-MC / panel-run + transcript reads)
- The bc-admin UI surface (intake queue page, panel-run inspector, draft review, materialization actions, blocked-gate visualization)
- The NestJS `McfModule` shape consolidating M11/M12/M12.5/M13 services for app-wide DI
- The standing operator authorization model — role + per-action audit, replacing per-run DBCPs for routine use
- The cutover criterion that defines when the script + per-run-DBCP pattern stops being required for routine MCF authoring
- The interaction with the calibration arc — what PR-S1 / PR-C4 / PR-A1 add; what PR-G1 / PR-C1 / PR-C2 / PR-C3 / PR-E1 / PR-G2 / PR-E2 / PR-G3 still do
- The non-goals (M16 / M17 / M18 tenant-runtime migration; legacy `POST /api/metric-catalog/definitions` shutdown)
- The risk register

### 1.3 Explicit non-scope

- ❌ No bc-core code authored or modified by this DBCP — bc-core stays at `16cf3781` (or whatever the head is when this DBCP merges)
- ❌ No bc-admin code authored or modified
- ❌ No `runPanel()` invocation; no writer standalone invocation
- ❌ No M12.5 / M13 / M14 invocation
- ❌ No provider API calls
- ❌ No metric contract creation
- ❌ No rollback
- ❌ No tenant DB touch
- ❌ No DDL, no DML, no substrate mutation
- ❌ No supersession of PR-G1 calibration DBCP — PR-S1 is additive, not substitutive
- ❌ No supersession of decision α — service-ification preserves α (build the approval-capable panel) and adds an operator-callable invocation layer
- ❌ No M16 / M17 / M18 (tenant runtime cutover, legacy POST HTTP 410, tenant runtime MCF awareness) — those are separately governed per `docs/operating-model/mcf-legacy-bridge.md`
- ❌ No re-scoping of M12 to advisory (γ stays rejected)
- ❌ No standing authorization for M12.5 / M13 / M14 in this DBCP — those gates remain per-run-authorized until separately specified
- ❌ No bc-admin implementation detail in this DBCP — PR-A1 will author the UI; PR-S1 specifies its shape only
- ❌ No commitment to a specific authentication mechanism beyond reusing the existing bc-admin Cognito JWT pattern (bc-admin is PLATFORM scope; no `x-tenant-id` header per memory `feedback_platform_scope_trap`)
- ❌ No commitment to a specific schedule — locks SCOPE, not SCHEDULE

## 2. Authority anchors

| Anchor | Reference | Role |
|---|---|---|
| PR-G1 calibration DBCP | bc-docs-v3 main `4a241eba` (`docs/implementation/metric-context-framework-m12-panel-framework-calibration-dbcp.md`) | Parallel arc — PR-S1 extends, does not supersede |
| PR-C1 production `PanelToolSurface` | bc-core PR #169 head `c31d72c` (open at authoring time) | First service-grade PR in calibration arc; class is DI-friendly and ready for `McfModule` wire-up |
| PR #168 first-real-M12 execution evidence | bc-core main `16cf3781` | Bootstrap proof — exercised the engine via script |
| PR #29 first-real-M12 authorization DBCP | bc-docs-v3 main `a18d6e3c` | Pattern for per-run DBCP authorization that PR-S1 replaces for routine use post-cutover |
| PR #31 disposition + calibration follow-up | bc-docs-v3 main `42f74fc9` | Operator-side single-use discipline preserved by PR-S1's standing authorization (per-action audit) |
| MCF-ERR-001 (PR #30) | bc-docs-v3 main `3926d021` | Verdict-aware intake-status semantics preserved by PR-S1 endpoints |
| MCF bridge ADR | `docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) | Architectural foundation preserved |
| Stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) | Per-gate operator authorization stance; PR-S1 distinguishes ROUTINE (standing) from EXCEPTIONAL (per-run DBCP) |
| Session discipline ADR | `docs/adrs/ADR-ebf0b4.md` (DEC-ebf0b4 / D268) | One-then-many — PR-E2 still proves the first calibrated run; routine runs follow |
| MCF Legacy Bridge | `docs/operating-model/mcf-legacy-bridge.md` | Coexistence window during the service-ification cutover; legacy `POST /api/metric-catalog/definitions` remains the alternate authoring path until M17 |
| Memory: platform scope | `feedback_platform_scope_trap.md` — bc-admin is PLATFORM, no `x-tenant-id` header | PR-S1 endpoints are platform-scoped per this convention |
| Memory: authentication | bc-core auth via real Cognito JWT — no bypass | PR-S1 endpoints sit under existing auth guard pattern |

## 3. Current truth (gap analysis at bc-core merge `16cf3781`)

### 3.1 Engine services that exist

Inside `bc-core/src/registry/mcf/`:

| Service | Type | Role |
|---|---|---|
| `ReservoirIngestionService` | `@Injectable()` | M11 intake creation + status transitions (markRejected, markSuperseded; markConsumedByPanel called by M12.5) |
| `MetricAuthoringPanelService` | `@Injectable()` | M12 orchestrator — `runPanel(intakeQueueUid, opts, deps)` returns `RunPanelResult` |
| `MetricAuthoringMaterializationService` | `@Injectable()` | M12.5 — `runMaterialization(panelRunUid, opts)` writes `mcf.metric_contract` + version + bindings + cert + fixture + verifier result on APPROVE_FOR_DRAFT only |
| `MetricPublicationEligibilityEvaluatorService` | `@Injectable()` | M13 PE-MC evaluator |
| `MetricSelfVerificationService` | `@Injectable()` | M10 verifier |
| `McfCertWriterService` | `@Injectable()` | Certification record writer |
| `ProductionPanelToolSurface` (PR-C1) | DI-friendly class | F4 — 10-tool surface; injectable |
| `M12PanelRunWriterService` | `@Injectable()` | M12 substrate writer (orchestrator-owned via O1 Adapter) |
| Plus ~10 pure helpers (`panel-consensus.ts`, `panel-grounding-check.ts`, `formula-canonicalization.service.ts`, `formula-execution.engine.ts`, `package-signature.service.ts`, `mcf-jcs.ts`, `mcf-defect-registry-v1.ts`, `mcf-hash-computer-coordinator.service.ts`, `output-comparator.ts`, `fixture-structural-check.service.ts`) | Plain classes / pure functions | Plumbing |

**The engine services are real.** They are well-typed, DI-ready, individually-testable, and (after PR-C2 + PR-C3) approval-capable.

### 3.2 Service surface that does NOT exist

| Surface | State | Consequence |
|---|---|---|
| HTTP controllers for MCF authoring (M11 / M12 / M12.5 / M13) | ❌ NONE | External callers (bc-admin, operators, scripts) cannot invoke via REST |
| `McfModule` consolidating the engine services for app-wide DI | ❌ NONE — each service stands alone or wires per-script | NestJS `AppModule` does not provide them as a coherent module |
| bc-admin pages for intake queue / panel-run inspector / draft review / materialization actions | ❌ NONE | Operators cannot author / inspect / materialize MCs through UI |
| Standing operator authorization model (role + per-action audit) | ❌ NONE | Every run requires a fresh bc-docs-v3 DBCP |
| Operator workflow not requiring a DBCP per run | ❌ NONE | Workflow today: author DBCP → merge → set env-gate → run script → capture evidence → author closeout |
| Observability / audit-trail integration with standard log/metric/trace pipelines | ❌ NONE specific to MCF authoring | Evidence files in `scripts/audit-output/` are the audit record |

Note: bc-core has plenty of HTTP controllers in OTHER areas — `metric-catalog.controller.ts`, `metric-definition.controller.ts`, `chain-status.controller.ts`, `formula-audit.controller.ts`, `metric-funnel.controller.ts`, `metric-readiness.controller.ts`, etc. — for the **legacy** metric path. The MCF path has no controllers because PR #28 → PR #168 focused exclusively on provenance scaffolding.

### 3.3 Why this matters now

The calibration arc PR-G1 → PR-G3 builds the approval-capable engine but does NOT ship a service surface. PR-E2 (calibrated M12 evidence run) is still a script + per-run authorization DBCP (PR-G2). PR-G3 (M12.5 next-gate) is still a per-run authorization DBCP.

**If the arc completes as currently locked**, the steady state is:
- Engine: approval-capable, well-tested, DI-ready
- Invocation: only via one-off scripts authorized by per-run DBCPs
- Operator UX: author a DBCP per attempt; no UI; no standing authorization

That is what the operator's question (recorded at PR-S1 §1.1) flags: **"are we doing services or just scripts with too many gets?"** The current arc ships the former at the engine layer and the latter at the invocation layer. Without PR-S1 / PR-C4 / PR-A1, the operator never gets a "click 'Author new MC' in bc-admin" workflow.

PR-S1 is the governance lock that prevents this end state.

## 4. The service surface

### 4.1 HTTP / REST API surface (PR-C4 implementation target)

The MCF service surface lives under `/api/mcf/*`. All endpoints are PLATFORM-scoped (no `x-tenant-id` header per the `feedback_platform_scope_trap` convention). All endpoints sit under the existing bc-core Cognito JWT auth guard.

#### 4.1.1 M11 — intake queue

| Method | Path | Purpose | Engine service |
|---|---|---|---|
| POST | `/api/mcf/intakes` | Create new M11 intake row (operator_direct reservoir). Body carries candidate metadata + reservoir_provenance_source_json. Returns `intake_queue_uid` + `reservoir_name` + `reservoir_entry_id`. | `ReservoirIngestionService.ingestOperatorDirect` (existing or extracted from `operator-direct-adapter.ts`) |
| GET | `/api/mcf/intakes` | List intakes with filters: `status_code`, `reservoir_name`, `reservoir_confidence_band`, pagination. | New query method on `ReservoirIngestionService` or a new `MetricAuthoringIntakeReadService` |
| GET | `/api/mcf/intakes/:intakeQueueUid` | Read one intake. | Same |
| PATCH | `/api/mcf/intakes/:intakeQueueUid/reject` | Operator-driven rejection with reason. Calls `markRejected` with operator-supplied reason text (≥20 chars). | `ReservoirIngestionService.markRejected` |

#### 4.1.2 M12 — panel run

| Method | Path | Purpose | Engine service |
|---|---|---|---|
| POST | `/api/mcf/panel-runs` | Run M12 panel against an eligible intake (intake `status_code='pending'`; not in-flight; allowlists active). Body: `intake_queue_uid`, optional `allowRetry`, optional `prompt_version`. Returns `panel_run_uid` + verdict + defect_code. **Synchronous in v1** — operator waits for the panel response (~30–60 seconds expected); v2 may make this async with a job queue. | `MetricAuthoringPanelService.runPanel` |
| GET | `/api/mcf/panel-runs` | List panel runs with filters: `verdict_code`, `reservoir_name`, date range, pagination. | New query method or a new `PanelRunReadService` |
| GET | `/api/mcf/panel-runs/:panelRunUid` | Read one panel run (mapr row + linked bcf.panel_output_record). | Same |
| GET | `/api/mcf/panel-runs/:panelRunUid/transcripts` | Read the 3 per-role mapt transcripts for inspection. Returns vendor identity (model_id, vendor_request_id, hashes), reasoning_trace, claims, tool_calls per role. | Same |

#### 4.1.3 M12.5 — materialization

| Method | Path | Purpose | Engine service |
|---|---|---|---|
| GET | `/api/mcf/panel-runs/:panelRunUid/materialization-preflight` | Read-only preflight: returns whether the mapr satisfies M12.5 preconditions (verdict_code === APPROVE_FOR_DRAFT; no prior materialization; allowlists still active). | New method on `MetricAuthoringMaterializationService` (preflight only; no writes) |
| POST | `/api/mcf/panel-runs/:panelRunUid/materialize` | Invoke M12.5 materialization. Writes `mcf.metric_contract` + `metric_contract_version` (+ bindings, filters, computed dims, cert, fixture, verifier result). Idempotent under retry with same panel_run_uid (HA-8). Operator action; subject to standing authorization (§4.3). | `MetricAuthoringMaterializationService.runMaterialization` |

**Per-run governance DBCP is NOT required for M12.5 invocations once cutover (§4.5) is reached.** Until cutover, per-run DBCPs remain in effect.

#### 4.1.4 M13 — publication eligibility

| Method | Path | Purpose | Engine service |
|---|---|---|---|
| GET | `/api/mcf/metric-contracts/:metricContractUid/pe-mc-status` | Read PE-MC evaluation status for an MC (PE-MC-1..10 per `mcf.metric_publication_eligibility_result`). | `MetricPublicationEligibilityEvaluatorService` |
| POST | `/api/mcf/metric-contracts/:metricContractUid/evaluate-pe-mc` | Trigger PE-MC evaluation for an MC. Writes `mcf.metric_publication_eligibility_result`. Idempotent per (mc, version). | Same |

#### 4.1.5 M14 — publication

**Out of scope for PR-C4.** M14 (publication) endpoint is deferred. Once authored, it will require its own next-gate DBCP per the existing pattern. The service surface does not yet expose a "publish" action.

### 4.2 NestJS module / controller shape (PR-C4 implementation target)

#### 4.2.1 `McfModule`

New module at `src/registry/mcf/mcf.module.ts` consolidating all MCF engine services as providers:

```
@Module({
  imports: [
    // existing modules for CONTROL_PLANE_DB token, RegistryReadModule (BCF reads),
    // and the auth-guard provider
  ],
  providers: [
    ReservoirIngestionService,
    MetricAuthoringPanelService,
    M12PanelRunWriterService,
    MetricAuthoringMaterializationService,
    MetricPublicationEligibilityEvaluatorService,
    MetricSelfVerificationService,
    McfCertWriterService,
    FixtureStructuralCheckService,
    FormulaCanonicalizationService,
    PackageSignatureService,
    McfHashComputerCoordinatorService,
    PanelAgentFactoryImpl,
    {
      provide: 'PanelToolSurface',
      useFactory: (registryRead: RegistryReadService, db: PostgresJsDatabase<any>) =>
        new ProductionPanelToolSurface({ registryRead, db }),
      inject: [RegistryReadService, CONTROL_PLANE_DB],
    },
  ],
  controllers: [
    McfIntakeController,
    McfPanelRunController,
    McfMaterializationController,
    McfPublicationEligibilityController,
  ],
  exports: [
    // services that other modules might consume
  ],
})
export class McfModule {}
```

#### 4.2.2 Controllers

Four controllers, one per surface group:

- `src/registry/mcf/mcf-intake.controller.ts` — M11 intake endpoints
- `src/registry/mcf/mcf-panel-run.controller.ts` — M12 panel + transcript endpoints
- `src/registry/mcf/mcf-materialization.controller.ts` — M12.5 preflight + materialize
- `src/registry/mcf/mcf-publication-eligibility.controller.ts` — M13 PE-MC endpoints

#### 4.2.3 Controllers MUST call existing services — no logic duplication

Per HA-1 (existing M12 hard rule extended), controllers MUST delegate to the engine services. Controllers handle: HTTP/JSON serialization, validation (Zod / class-validator), auth-guard wiring, error→HTTP-status mapping. They MUST NOT:
- Construct panel transcripts or consensus payloads directly
- Issue substrate writes outside the engine services
- Bypass the verdict-aware semantics (MCF-ERR-001)
- Invoke vendor APIs directly

#### 4.2.4 Scripts become bootstrap / evidence tools, not routine paths

After PR-C4 lands:
- `scripts/mcf-m12-first-real-run.mjs` and PR-E2's equivalent stay in the repo as evidence-capture tools for governance-bootstrapped runs (first-of-kind, calibration proof, etc.)
- Routine operator runs use the HTTP endpoints
- Existing per-run-DBCP authorization pattern (PR #29 / PR-G2) remains required for evidence-capture script runs; the HTTP path uses standing authorization

### 4.3 Authorization model

#### 4.3.1 Standing operator role + per-action audit (routine path)

A new role `mcf_author` (or similar; final name decided in PR-C4 review) authorizes:

| Action | Required role | Per-action audit |
|---|---|---|
| Create intake (`POST /api/mcf/intakes`) | `mcf_author` | `mcf.intake_audit` (new table or extend `mcf.metric_authoring_intake_queue` with audit columns) |
| List / read intakes | `mcf_reader` (subset of `mcf_author`) | Read-only; no audit row |
| Run panel (`POST /api/mcf/panel-runs`) | `mcf_author` | Existing `mcf.metric_authoring_panel_run` row IS the audit; add `triggered_by_user_id` column (DBCP-approved in PR-C4) |
| Reject intake (`PATCH /api/mcf/intakes/:uid/reject`) | `mcf_author` | Existing `status_reason_text` column; add `rejected_by_user_id` (DBCP-approved in PR-C4) |
| Run materialization (`POST /api/mcf/panel-runs/:uid/materialize`) | `mcf_publisher` (broader role; can transition draft MC → publication track) | New `mcf.materialization_audit` table; or extend `mcf.metric_contract_version` with `created_by_user_id` (DBCP-approved in PR-C4) |
| Run PE-MC evaluation | `mcf_publisher` | Existing `mcf.metric_publication_eligibility_result` row IS the audit |

#### 4.3.2 Cognito JWT + role mapping

Reuse bc-core's existing Cognito JWT auth guard. Map Cognito groups to MCF roles in a config file (`mcf-auth.config.ts`) under PR-C4 — operator-configurable per environment.

#### 4.3.3 DBCPs remain required for non-routine actions

The standing authorization replaces per-run DBCPs ONLY for routine operator actions on the HTTP endpoints. **DBCPs remain required for:**

- Architectural changes to MCF design (e.g. revisiting decision α / β / γ, M-series gate semantics, substrate schema changes)
- First-of-kind gates (first real provider/vendor adapter; first new tool added to PanelToolSurface; first new defect code added to MCF_DEFECT_REGISTRY)
- Exceptional overrides (e.g. operator-forced retry against a "rejected" intake; bypassing in-flight guard for an emergency rerun; bulk-disposition of stuck intakes)
- Standing authorization model changes (adding a new MCF role; reassigning permissions across roles)
- Cross-tenant or tenant-runtime cutover events (M16 / M17 / M18 — separately governed)

The DBCP path remains the architectural-change authority. PR-S1 narrows when DBCPs are MANDATORY (routine ops out, architectural changes in).

#### 4.3.4 Single-use semantics preserved by per-action audit

PR #29 §6 (single-use authorization per run) and MCF-ERR-001 (operator-side single-use enforcement) survive PR-S1 as: each HTTP action is audited; the audit row is the per-action authorization record. The operator workflow shifts from "author DBCP → consume single use" to "make API call → row stamped with user_id + timestamp." The audit trail is denser and auto-captured, not sparser.

### 4.4 bc-admin UI shape (PR-A1 implementation target)

PR-A1 adds the following pages under `/catalog/metrics/mcf/*` in bc-admin:

#### 4.4.1 Intake queue page (`/catalog/metrics/mcf/intake-queue`)

- DataTable showing all `mcf.metric_authoring_intake_queue` rows
- Columns: `intake_queue_uid` (short), `reservoir_name`, `reservoir_entry_id`, `candidate_name`, `status_code`, `reservoir_confidence_band`, `created_at`, action buttons
- Filter row: `status_code` (pending / consumed_by_panel / rejected / superseded), reservoir_name, confidence_band
- "Author new intake" button → modal form (candidate_name, description, normalized_candidate_json — JSON editor) → calls `POST /api/mcf/intakes`
- Row action "Run panel" (when `status_code='pending'`) → confirmation dialog → `POST /api/mcf/panel-runs` → navigate to panel-run inspector
- Row action "Reject" (when `status_code='pending'`) → reason input modal (≥20 chars) → `PATCH /api/mcf/intakes/:uid/reject`

#### 4.4.2 Panel-run inspector (`/catalog/metrics/mcf/panel-runs/:panelRunUid`)

- Header: panel_run_uid, intake back-reference, verdict_code, defect_code, operator_review_reason, grounding_check_passed, panel_algorithm_version, prompt_version
- Three side-by-side panes — one per role (maker / checker / moderator)
- Each pane: vendor identity (vendor, model_id, vendor_request_id, prompt_hash, raw_response_hash, latency_ms, usage), verdict_code, defect_code, reasoning_trace (collapsible), claims (table with supporting_tool_call_ids links), tool_calls (table with request/response JSON viewers), candidate_proposal / verification_payload / consensus_payload (role-dependent)
- Footer: "Run M12.5 materialization" button visible only when `verdict_code === 'APPROVE_FOR_DRAFT'` AND user has `mcf_publisher` role AND M12.5 preflight passes
- "View provenance" link → audit details
- "View errata" link → MCF-ERR-001 if `verdict_code = OPERATOR_REVIEW`

#### 4.4.3 Draft metric contract review (`/catalog/metrics/mcf/drafts`)

- DataTable showing `mcf.metric_contract` rows where the latest `mcf.metric_contract_version.governance_state_code = 'draft'`
- Columns: metric_contract_uid (short), mc_name, display_name, grain_entity_id (linked), candidate_source (link back to panel run), draft created_at, action buttons
- Row action "Inspect MC" → MC detail page (formula AST, variable bindings, filters, computed dims, temporal gate, fixture, certification record, verifier result)
- Row action "Submit for review" / "Submit for approval" (lifecycle transitions per M-series gates; UI surfaces are M14-scoped — deferred until M14 ships)

#### 4.4.4 Visible blocked / downstream gate states

Every page surfaces the current gate state for the path the page covers:
- Intake queue page: "M12 ready to run?" indicator per row (active allowlists, no in-flight conflict)
- Panel-run inspector: "M12.5 unlocked?" indicator + "M13 ready?" + "M14 status (deferred)"
- Draft review: "PE-MC status" per draft

UI MUST NOT hide provenance or gate state. The MCF Legacy Bridge `legacy_mc_shadowed_by_mcf` warning event surfaces in the UI as a banner on affected MCs.

### 4.5 Cutover criterion

**The per-run-DBCP requirement for routine MCF authoring is LIFTED when ALL of the following hold:**

1. PR-S1 (this DBCP) merged
2. PR-C1 (production `PanelToolSurface`) merged
3. PR-C2 (adapter rewrites) merged + adapter test suite green
4. PR-C3 (consensus hardening) merged + test suite green
5. PR-C4 (controllers + `McfModule`) merged + e2e tests green
6. PR-E1 (new M11 intake row evidence) merged AND additionally proved via HTTP endpoint round-trip (`POST /api/mcf/intakes` returns same intake_queue_uid as the script-created one — or, equivalently, PR-E1 uses the HTTP endpoint instead of the script)
7. PR-G2 (fresh first-real-M12 authorization DBCP) merged — preserved as governance for the FIRST run under the calibrated framework
8. PR-E2 (calibrated M12 evidence run) merged AND additionally exercised the HTTP `POST /api/mcf/panel-runs` endpoint — the calibrated proof traverses BOTH the script path (provenance / D8 condition evidence) AND the HTTP path (service-surface validation)
9. PR-A1 (bc-admin MCF pages) merged + visual smoke proven
10. A final operator attestation in a brief bc-docs-v3 closeout PR (PR-S2) records the cutover event and lists the actions now routed via standing authorization

After PR-S2 lands, the per-run-DBCP pattern is no longer mandatory for: `POST /api/mcf/intakes`, `GET /api/mcf/intakes`, `GET /api/mcf/panel-runs`, `GET /api/mcf/panel-runs/:uid/transcripts`, `POST /api/mcf/panel-runs` (routine), `PATCH /api/mcf/intakes/:uid/reject`, `GET /api/mcf/panel-runs/:uid/materialization-preflight`, `POST /api/mcf/panel-runs/:uid/materialize` (routine), `GET /api/mcf/metric-contracts/:uid/pe-mc-status`, `POST /api/mcf/metric-contracts/:uid/evaluate-pe-mc`.

The per-run-DBCP pattern REMAINS mandatory for: any action in §4.3.3.

### 4.6 Interaction with calibration arc (sequencing)

PR-S1 / PR-C4 / PR-A1 sit alongside the existing PR-G1 → PR-G3 arc:

| # | PR | Type | Status | Sequencing |
|---|---|---|---|---|
| 1 | PR-G1 calibration DBCP | Governance (bc-docs-v3) | ✅ MERGED `4a241eba` | — |
| 2 | PR-C1 production PanelToolSurface | Code (bc-core) | OPEN (PR #169) | gates PR-C2; PR-S1 can land in parallel |
| **3** | **PR-S1 service-ification DBCP (this)** | **Governance (bc-docs-v3)** | **OPEN — authored by this commit** | **Lands in parallel with PR-C1; gates PR-C4** |
| 4 | PR-C2 adapter rewrites | Code (bc-core) | blocked by PR-C1 | SHOULD land after PR-S1 so that adapter DI surface aligns with `McfModule`-providable shape |
| 5 | PR-C3 consensus hardening | Code (bc-core) | blocked by PR-C2 | — |
| **6** | **PR-C4 MCF controllers + McfModule** | **Code (bc-core)** | blocked by PR-C3 (or late PR-C2 if DI readiness) | **Adds the HTTP / module surface** |
| 7 | PR-E1 new M11 intake | Evidence (bc-core) | blocked by PR-C3 (logical) and PR-C4 (service path) | SHOULD exercise BOTH script + HTTP paths per cutover §4.5 step 6 |
| 8 | PR-G2 fresh M12 authorization | Governance (bc-docs-v3) | blocked by PR-E1 | per-run DBCP for the FIRST calibrated run only |
| 9 | PR-E2 calibrated M12 evidence | Evidence (bc-core) | blocked by PR-G2 | SHOULD exercise BOTH script + HTTP paths per cutover §4.5 step 8 |
| **10** | **PR-A1 bc-admin MCF pages** | **Code (bc-admin)** | blocked by PR-C4 | **Adds the UI** |
| 11 | PR-G3 M12.5 next-gate (CONDITIONAL on PR-E2 = APPROVE_FOR_DRAFT) | Governance (bc-docs-v3) | blocked by PR-E2 | per-run DBCP for the FIRST M12.5 only |
| **12** | **PR-S2 cutover closeout** | **Governance (bc-docs-v3)** | **CONDITIONAL — only after §4.5 cutover criterion satisfied** | **Lifts the per-run-DBCP requirement for routine ops** |

PR-S1 SHOULD land before PR-C2 goes too deep so that the adapter rewrite DI shape aligns with the `McfModule` providers list in §4.2.1. If PR-C2 lands first, PR-C4 absorbs whatever DI shape PR-C2 commits to.

PR-A1 (bc-admin) can be authored in parallel with PR-C4 once the §4.1 endpoint shapes are locked here.

PR-E2 SHOULD exercise both the script path AND the HTTP path to give the cutover §4.5 step 8 its proof. If PR-E2 chooses to exercise only one, the cutover criterion is partially satisfied and PR-S2 must record which path was deferred and why.

## 5. Non-goals

- ❌ No M16 / M17 / M18 tenant-runtime cutover
- ❌ No legacy `POST /api/metric-catalog/definitions` shutdown (HTTP 410) — that is M17
- ❌ No M12.5 invocation by this DBCP
- ❌ No metric contract creation by this DBCP
- ❌ No bc-admin implementation in this DBCP (PR-A1 implements; PR-S1 specifies shape only)
- ❌ No substrate mutation
- ❌ No supersession of DEC-c3e57f / D422 — MCF architecture stance preserved
- ❌ No supersession of decision α — α (build the approval-capable panel) is preserved; PR-S1 adds an invocation layer
- ❌ No supersession of MCF-ERR-001 — verdict-aware mapping preserved
- ❌ No supersession of PR-G1 — calibration arc PR-G1 / PR-C1 / PR-C2 / PR-C3 / PR-E1 / PR-G2 / PR-E2 / PR-G3 all still stand
- ❌ No change to the per-gate operator authorization stance (DEC-7f9597) for architectural changes — standing authorization is for ROUTINE actions only
- ❌ No change to AI-consensus-constitutes-Framework-Approval (MCF Requirements §1.3) — service surface invokes the same panel; it does not replace consensus with operator override
- ❌ No automatic migration of legacy `metric.metric_definition` rows into `mcf.metric_contract` — per MCF Legacy Bridge, MCs are re-authored, not copied
- ❌ No cross-tenant authoring — the service surface is PLATFORM-only; tenant binding remains a separate concern (M18+)

## 6. Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **R1** | Scripts become permanent — PR-S2 cutover never lands, operators continue authoring per-run DBCPs indefinitely | medium | high | Cutover criterion §4.5 is concrete (10 items); PR-S2 is conditional but UNGATED — operator can author it as soon as criterion holds; calibration arc PRs explicitly list service-path exercises as criterion items |
| **R2** | Duplicate authorization paths — both DBCP and HTTP routes exist, leading to confusion about which is authoritative | medium | medium | §4.3.3 EXPLICITLY narrows the DBCP requirement to architectural-change / first-of-kind / exceptional / standing-authz-change cases; routine ops are HTTP-only post-cutover; bc-admin UI is the operator-facing entry point |
| **R3** | API bypassing governance — controllers added without DBCP-level scope locking, allowing scope creep into engine logic | low | high | §4.2.3 mandates controllers MUST delegate to engine services; PR-C4 review focuses on this; no controller can construct transcripts / consensus / writes directly |
| **R4** | UI hiding provenance — bc-admin UI shows verdicts but hides per-role transcripts / claims / tool_calls / hashes / vendor_request_ids | medium | high | §4.4.4 mandates UI surfaces gate state + provenance; PR-A1 review focuses on per-role transcript pane completeness; integration tests verify provenance round-trip via UI |
| **R5** | Premature M12.5 exposure — `POST /materialize` endpoint authored before PR-G3 (first M12.5 next-gate DBCP) lands | medium | high | PR-C4 ships the endpoint but it remains guarded by: (a) APPROVE_FOR_DRAFT precondition at the engine layer, (b) `mcf_publisher` role check at the controller layer, (c) PR-G3 mandatory before ANY operator invocation that would create the first `mcf.metric_contract`; the endpoint EXISTS pre-PR-G3 but no operator is authorized to call it until PR-G3 |
| **R6** | Tenant runtime confusion — operators or developers conflate the platform-side MCF service with tenant-runtime metric evaluation (boundary/*) | medium | medium | §4.1 explicitly notes endpoints are PLATFORM-scoped; bc-admin pages display "Platform" badge; MCF Legacy Bridge §"What M12.5 does NOT change" reinforces; tenant-runtime cutover is M18+ separately governed |
| **R7** | Over-broad permissions — `mcf_author` role granted to too many users; spam intakes; cost explosion (real vendor calls) | medium | medium | Per-action audit (§4.3.1) provides per-user attribution; cost-ceiling per panel run (DBCP §10 R-M12-3 + existing `CostCeilingExceededError`); intake creation does NOT trigger a panel run; rate-limit policy on `POST /api/mcf/panel-runs` per user (operator-configurable in PR-C4 review) |
| **R8** | Dual-authority drift — legacy `POST /api/metric-catalog/definitions` continues to receive writes while MCF service surface receives parallel writes; same metric_code in both authorities | low | medium | MCF Legacy Bridge already locks "MCF wins" semantics with `legacy_mc_shadowed_by_mcf` warning event; UI surfaces the warning; cutover criterion §4.5 step 10 (PR-S2) records the state; M17 eventual HTTP 410 closes the dual-authority window |
| **R9** | Standing authorization captured in code (config file) drifts from intended governance — role definitions change without architectural review | low | medium | Standing authorization model changes are explicitly in §4.3.3's MANDATORY-DBCP list; CI lint can later verify the `mcf-auth.config.ts` file is referenced by a recorded ADR |
| **R10** | Synchronous panel-run endpoint timeouts under load — `POST /api/mcf/panel-runs` blocks for 30–60s per call, exhausting connection pool | medium | medium | v1 explicitly synchronous per §4.1.2; per-vendor timeout already capped (`DEFAULT_VENDOR_TIMEOUT_MS = 60_000`); aggregate panel-run timeout = ~3× vendor timeout; v2 async job-queue path is a future ADR if needed; v1 rate-limits at the controller layer |

## 7. Standing gate state

### 7.1 Pre-DBCP (current state)

| Item | State |
|---|---|
| bc-docs-v3 main | `4a241eba` (after PR-G1) |
| bc-core main | `16cf3781` (after PR #168) |
| Calibration arc PRs | PR-G1 merged; PR-C1 open at `c31d72c` |
| MCF engine services | exist in bc-core; not wired as a module |
| HTTP controllers for MCF authoring | NONE |
| bc-admin MCF pages | NONE |
| Standing authorization | NONE — every run uses per-run DBCP |
| Service-ification cutover criterion | UNDEFINED |

### 7.2 Post-DBCP (this PR merges)

| Item | State |
|---|---|
| bc-docs-v3 main | advances by one squash commit |
| bc-core main | UNCHANGED |
| Service-ification scope | LOCKED |
| §4.1 HTTP/API surface | LOCKED |
| §4.2 NestJS module/controller shape | LOCKED |
| §4.3 Authorization model | LOCKED |
| §4.4 bc-admin UI shape | LOCKED |
| §4.5 Cutover criterion | LOCKED |
| §4.6 PR-C4 + PR-A1 | AUTHORIZED to be authored as separate PRs |
| Per-run DBCP requirement for routine ops | STILL ACTIVE (until §4.5 cutover) |

### 7.3 Post-arc (after PR-S2 cutover closeout)

| Item | State |
|---|---|
| Per-run DBCP requirement for routine ops | LIFTED |
| DBCP requirement for §4.3.3 actions | UNCHANGED — still mandatory |
| MCF authoring routine workflow | bc-admin UI → HTTP endpoint → engine service → substrate; auto-audited |
| Operator UX | "click 'Author new MC' → fill form → review verdict → materialize" |

## 8. Hard-rule mapping + non-execution confirmation

### 8.1 Hard-rule mapping

| Rule | Application here |
|---|---|
| **HR1 (real vendor calls only)** | Preserved by PR-C4 — controllers delegate to engine services; engine services call real adapters; provenance contract from PR #28 §11.4 survives the HTTP wrapping unchanged |
| **HR2 (writer reached via orchestrator outer tx)** | Preserved — `POST /api/mcf/panel-runs` calls `MetricAuthoringPanelService.runPanel` which calls the writer inside its tx; no standalone writer invocation |
| **HR3 (no `contract.*` writes)** | Preserved — A4 freeze unaffected by HTTP surface |
| **HR4 (no tenant DB touch)** | Preserved — PR-S1 service surface is PLATFORM-only; controllers operate against CONTROL_PLANE_DB; production tool surface (PR-C1) ALREADY does not read `TENANT_DATABASE_URL` |
| **HR5 (production COMMIT path)** | Preserved — PR-C4 controllers commit via existing engine-service transactions |
| **DEC-7f9597 / D423 (operator authorization per gate)** | NARROWED for routine ops to standing role + per-action audit; PRESERVED for §4.3.3 architectural / first-of-kind / exceptional cases |
| **DEC-ebf0b4 / D268 (one-then-many; prove before scaling)** | Preserved — PR-E2 still proves the first calibrated run; PR-S2 cutover requires the first run to be proven via BOTH script and HTTP paths |
| **MCF-ERR-001 verdict-aware mapping** | Preserved — controllers MUST NOT bypass verdict-aware semantics; intake-row transitions stay code-true |

### 8.2 Explicit non-execution confirmation

| Item | Status |
|---|---|
| Code changed | ❌ NONE — bc-docs-v3 docs-only |
| bc-core code change | ❌ NONE — bc-core stays at `16cf3781` |
| bc-admin code change | ❌ NONE — bc-admin stays at its current main |
| Provider API calls | ❌ NONE |
| `runPanel()` invocation | ❌ NONE |
| Writer standalone invocation | ❌ NONE |
| M12.5 / M13 / M14 invocation | ❌ NONE |
| Metric contract created | ❌ `mcf.metric_contract` Δ=0, `mcf.metric_contract_version` Δ=0 |
| Rollback | ❌ NONE |
| Tenant DB touch | ❌ NONE — read-only `pg_query` against `bc_platform_dev` for substrate re-verification only |
| Substrate mutation | ❌ NONE — 9 invariants identical to PR #168 evidence |
| New M11 intake row | ❌ NONE — PR-E1 forward-looking |
| Fresh first-real-M12 authorization | ❌ NONE — PR-G2 forward-looking |
| M12.5 next-gate DBCP | ❌ NONE — PR-G3 conditional |
| Service-ification cutover closeout | ❌ NONE — PR-S2 conditional on §4.5 criterion |
| Standing authorization activated | ❌ NONE — activates only after PR-S2 |
| Supersession of any prior decision | ❌ NONE — PR-S1 is additive |
| Lowering of M12 scope to advisory | ❌ NONE — γ stays rejected |
| Tenant-runtime migration | ❌ NONE — M18+ separately governed |

## 9. References

- `docs/implementation/metric-context-framework-m12-panel-framework-calibration-dbcp.md` (PR-G1; bc-docs-v3 main `4a241eba`) — parallel arc this DBCP extends
- `docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` — M12 design (consensus payload, verdict semantics, tool surface)
- `docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md` — M12.5 design
- `docs/implementation/metric-context-framework-m12-first-real-run-authorization-dbcp.md` (PR #29) — per-run DBCP pattern PR-S1 replaces for routine use
- `docs/implementation/metric-context-framework-m12-first-real-run-disposition.md` (PR #31) — bootstrap disposition pattern
- `docs/errata/MCF-ERR-001.md` (PR #30) — verdict-aware mapping preserved by PR-S1
- `docs/operating-model/mcf-legacy-bridge.md` — coexistence window during cutover
- `docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) — MCF architecture, preserved
- `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) — operator-authz stance, narrowed for routine ops
- `docs/adrs/ADR-ebf0b4.md` (DEC-ebf0b4 / D268) — one-then-many discipline, preserved
- bc-core PR #169 — PR-C1 production `PanelToolSurface` (open at authoring time; head `c31d72c`)
- bc-core PR #168 merge `16cf3781` — first-real-M12 execution evidence
- bc-core `src/registry/mcf/` — existing engine services (M10 / M11 / M12 / M12.5 / M13 / cert writer / production tool surface / helpers)
- bc-core existing controller pattern — `src/registry/{metric-catalog,metric-definition,metric-binding,chain-status,formula-audit,metric-funnel,metric-readiness}.controller.ts`
- bc-admin existing PLATFORM-scoped page pattern — Metric Lifecycle / Chain integrity / Readiness / Funnel pages
- Memory: `feedback_platform_scope_trap.md` — bc-admin = PLATFORM (no `x-tenant-id` header)
- Memory: `credentials_cognito.md` — operator auth path reused by PR-C4 controllers
