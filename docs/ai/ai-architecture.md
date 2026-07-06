---
id: ai-architecture
order: 27
title: "AI Architecture"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-authority-model, the-dual-layer-interaction-model, operating-model-overview, evidence-and-lineage, architecture, backend-services, auxiliary-services, audit-and-activity-logging]
governing_sources:
  - Foundation
  - The Dual-Layer Interaction Model
  - The Authority Model
  - Operating Model
  - Architecture
  - Backend Services
  - Auxiliary Services
  - Audit and Activity Logging
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus home; the AI section exists as a first-class peer to Implementation)
  - DEC-804874 (D366 L-node semantic gate; consumes AI verdicts at session close)
  - DEC-ebf0b4 (D268 Session Discipline and Data Integrity; the session-governance auditor reports against this discipline)
errata_referenced: []
v2_sources: []
diagrams: []
---

# AI Architecture

## Scope

This chapter records the architectural shape of the AI surface in its as-built state at the time of writing: the bc-ai service that hosts every AI-bearing path, the maker-checker-gate triplet pattern that every governed AI act follows, the housekeeping agent pattern that runs on-demand against DevHub, the session governance auditor that reviews session conduct, the routing model that decides which provider answers each call, the Mode Context Protocol surface that bc-ai exposes for diagnostic use, and the persistence and audit substrates that the AI surface relies on.

This chapter sits at the front of the AI section. It is the architectural binder for the chapters that follow. The chapter does not enumerate per-agent or per-act detail (deferred to AI Agents), the per-inference-profile and per-model substrate (deferred to Bedrock and Inference Profiles), the gate verdict authoring contract (deferred to AI Gates), the cross-family verification model (deferred to AI Trust and Verification), or the tenant-facing transparency surface (deferred to AI Usage Visibility). Where the chapter names a per-agent, per-model, or per-gate concern, the reader is routed to the chapter that owns it.

This chapter does not redefine Foundation invariants, the Authority Model, the Dual-Layer Interaction Model, or the Operating Model's contract grammar. Per the Dual-Layer Interaction Model, AI participation runs on the Conversation surface; the Trust surface (metrics, Canonical Objects, the proof chain) is authoritative and is not produced by AI. Where AI verdicts feed the Trust surface (the L-node semantic gate at session close per DEC-804874), the verdict is a recorded input that governs the surface's gates; the surface's authoritative state remains produced by the four governed boundary acts.

**Governing source.** Architecture; Backend Services; Auxiliary Services; outline.md §4.4.

## The bc-ai Service

bc-ai is the platform's single AI service. It is a Python service running FastAPI on uvicorn with a Pydantic v2 settings layer, a structlog structured-logging layer, and an aiosqlite-backed local store. The service hosts every AI-bearing path: the maker-checker-gate triplets, the housekeeping agents, the Gemini-based session governance auditor, the KPI decomposition and the KPI assistant, and the diagnostic Mode Context Protocol surface. Other platform services that need an AI verdict call bc-ai over HTTP; bc-ai does not reach back into the calling services.

The service's deployable shape (port assignment, AWS account, region, profile) is owned by Infrastructure and is not embedded in this chapter per pattern 85. The chapter records that bc-ai is a single Python service with a single HTTP surface and a single MCP diagnostic surface; its location and reachability are operational concerns owned elsewhere.

The service runs without a database server of its own. Local persistence is a single SQLite file holding evidence rows for every triplet run, draft-evidence rows for failed runs, a review queue for amber and red verdicts that need human attention, a budget log per call for cost accounting, and the housekeeping run records. Cross-service durability is handled by the calling service's own database; bc-ai is the verdict producer, not the verdict store of record beyond its local evidence trail.

**Governing source.** Backend Services; Auxiliary Services; `bc-ai/main.py`; `bc-ai/app/db/schema.sql`.

## The Maker-Checker-Gate Triplet Pattern

Every governed AI act at the time of writing is a triplet. The pattern composes three agent roles in sequence:

| Role | Responsibility | Provider in current registry |
|---|---|---|
| Maker | Produces a candidate output (a classification, a mapping, a verdict, a recommendation) plus a confidence score and a reasoning trace | Mixed by act: most makers use `nova-pro`, whose current profile resolves to Google/Gemini; `field-map` uses direct Anthropic `haiku` |
| Checker | Re-evaluates the maker candidate against the same input and produces an agreement or disagreement signal | Mixed by act: seven checkers use direct Anthropic `haiku`; five triplets retain same-family maker/checker pairings (`nova-pro` or `haiku`) |
| Gate | Combines the maker output and the checker signal into a final verdict and a routing decision (green, amber, or red) | Current gates use `nova-lite`, whose current profile resolves to Google/Gemini |

The pattern is implemented by `app/pipeline/orchestrator.py:run_pipeline()` and the agent base class at `app/agents/base.py`. Each role's class is registered in `app/agents/__init__.py` under an act identifier (the codebase's `flow_id` field); the orchestrator looks up the triplet for the requested act and executes the three roles in order. The orchestrator records evidence rows on success and draft-evidence rows on failure (a checker disagreement, a budget rejection, a parse failure, or a timeout).

The cross-family discipline (maker and checker from different model families) is the central reason the triplet exists. A single-model verdict can encode the model family's systematic biases without an independent counter-check; a cross-family triplet attempts to surface those biases as a checker disagreement. Current grounding shows partial realization: seven triplets pair a Gemini maker with a direct-Anthropic checker; four triplets pair Gemini maker and Gemini checker; `field-map` pairs direct-Anthropic maker and checker. The model registry also carries legacy `nova-*` labels that resolve to Gemini profile strings. AI Trust and Verification owns the trust ladder and records the remaining enforcement gap.

The verdict shape is a Pydantic model defined at `app/agents/base.py:55-82` (the `PipelineResult`): the maker's output, the checker's output, the gate's output, the combined confidence, the routing decision in `{green, amber, red}`, and the persisted evidence identifier. Routing thresholds default to green at confidence 0.85 and above, amber from 0.60 to 0.84, and red below 0.60; the gate is allowed to override the threshold-derived routing when its structured output explicitly asserts a different routing.

**Governing source.** `bc-ai/app/agents/base.py`; `bc-ai/app/pipeline/orchestrator.py`; `bc-ai/app/agents/__init__.py`; AI Trust and Verification.

## The Housekeeping Agent Pattern

The housekeeping agents are a separate pattern. Each housekeeping agent runs a three-phase sequence: an `assess()` phase that gathers state from DevHub via REST (no LLM call), a `recommend()` phase that classifies findings by severity (LLM optional, controlled by an `uses_llm` flag on the agent class), and an `act()` phase that executes auto-actions and collects per-finding recommendations (no LLM call). Eight housekeeping agents are registered: a documentation-staleness agent, a session-hygiene agent, a task-triage agent, a non-conformance-aging agent, a registry-refresh agent, a risk-review agent, a quality-audit-patrol agent, and a documentation-maintainer agent. The agent inventory is owned by AI Agents.

The housekeeping scheduler is disabled at the time of writing. Per a code note dated to D269, scheduled invocation has migrated to Claude Code scheduled tasks; the scheduler module remains in the repository but does not run in the active deployment. The agents continue to be invokable on demand through HTTP endpoints (`POST /api/ai/housekeeping/run` for all agents, `POST /api/ai/housekeeping/run/{agent_id}` for one). The reports persist to bc-ai's SQLite under `housekeeping_run` and `housekeeping_finding`, and the agents push relevant findings back to DevHub through the REST client at `app/housekeeping/client.py`.

The pattern is intentionally distinct from the maker-checker-gate triplet. Housekeeping agents have no checker counterpart and no cross-family verification; they are operational agents that read DevHub state, classify it, and act. Their output lives in DevHub and in bc-ai's local store; the platform's Trust surface is unaffected by housekeeping verdicts.

**Governing source.** `bc-ai/app/housekeeping/base.py`; `bc-ai/app/housekeeping/__init__.py`; `bc-ai/app/housekeeping/client.py`; AI Agents.

## The Session Governance Auditor

The session governance auditor is a third pattern. It is a Gemini-driven agent that reviews a Claude Code session's conduct against the session-discipline rules per DEC-ebf0b4 (D268) and the Standard Operating Procedures recorded in CLAUDE.md. The auditor accepts a session payload (session identifier, project, branch, commit hashes, files changed, checkpoints, the saved plan, the change-record plan and report, the session summary, the QA audit run state, the non-conformance count, the self-audit notes), runs a deterministic validator phase, renders a Jinja2 prompt against the payload plus any referenced SOP, invokes the Gemini model, parses the structured findings, computes a verdict (`pass`, `concerns`, or `fail`) and a verdict score, and posts the verdict and the per-finding rows to DevHub's `/api/process-audits` endpoint per Audit and Activity Logging.

The auditor uses a different model from the runtime triplets: Gemini 2.5 Pro rather than Gemini 2.5 Flash. The Pro model is reserved for the auditor because the auditor's prompt is large (full session context plus the SOP) and the session governance verdict warrants more expensive inference per call. The model selection lives in `app/auditor/config.py`.

The auditor is advisory at the time of writing. A `fail` verdict records into DevHub's `process_audit` table but does not block session close; only the L-node semantic gate per DEC-804874 is a hard close-blocker. Audit and Activity Logging records this advisory posture as drift; the chapter that follows owns the failure-mode analysis.

**Governing source.** `bc-ai/app/auditor/`; `bc-ai/main.py`; Audit and Activity Logging; DEC-ebf0b4; DEC-804874.

## Provider Branching and Routing

bc-ai's call path branches per call into one of three providers based on the model registry entry the requested role resolves to. The branching lives in `app/agents/base.py:run()`:

| Provider | Client | When used |
|---|---|---|
| Google (Gemini) | `app/clients/gemini.py` via the Google Generative AI SDK | Maker, gate, and KPI decomposition acts; the auditor uses Gemini 2.5 Pro |
| Anthropic API direct | `app/clients/anthropic_client.py` via the Anthropic Python SDK | Some checker roles for cross-family verification; KPI dual-model decomposition uses Haiku 4.5 Maker A and Sonnet 4.5 Maker B |
| AWS Bedrock | `app/clients/bedrock.py` via boto3's `bedrock-runtime` client | Available for registry entries that do not resolve to `google` or `anthropic-api`; no default role resolves to Bedrock in the readiness baseline |

The provider per role is fixed at act registration: an act's maker class names a model identifier; the model registry resolves the identifier to a provider; the registry entry's provider field decides which client the agent base class invokes. There is no per-call provider override; routing is per-act, not per-call. Bedrock and Inference Profiles records the model registry shape; AI Trust and Verification records the cross-family discipline that the pairings serve.

**Governing source.** `bc-ai/app/agents/base.py`; `bc-ai/app/models/registry.py`; Bedrock and Inference Profiles; AI Trust and Verification.

## The Mode Context Protocol Surface

bc-ai exposes a Mode Context Protocol server alongside its HTTP surface. The MCP server is a thin diagnostic surface: it provides four tools for inspecting service state and exercising one inference call manually, but it does not duplicate the full HTTP control plane. The four tools are `ai_health` (uptime plus model status plus current budget summary), `ai_models_status` (the model registry with per-model status), `ai_invoke` (a direct Bedrock invocation against a chosen model identifier with a prompt and a system message), and `ai_health_check_models` (a slow walk through every registered model running a lightweight invocation against each).

The MCP server is registered in the developer's Claude Code settings as a stdio server; it is not exposed over a network. The surface is read-and-test only: it does not run AI acts, run housekeeping agents, or invoke the auditor. The HTTP surface remains the full control plane.

**Governing source.** `bc-ai/app/mcp_server.py`; `bc-ai/mcp_main.py`.

## Persistence and Audit Substrates

bc-ai's persistence sits in three places, each owned by a distinct chapter and named here only at the architectural level.

| Substrate | Where it lives | Authority chapter |
|---|---|---|
| Triplet evidence (per-act maker, checker, gate outputs plus combined confidence and routing) | bc-ai local SQLite (`evidence` and `draft_evidence` tables) | AI Trust and Verification (the verdict trail); Audit and Activity Logging (the cross-service push boundary) |
| Housekeeping run records (per-run metadata plus per-finding rows, plus DevHub-side records that the housekeeping client posts) | bc-ai local SQLite (`housekeeping_run`, `housekeeping_finding`) plus DevHub via `/api/projects`, `/api/projects/{slug}/sessions`, `/api/tasks`, `/api/qa/audits/run`, and the documents endpoints | AI Agents; Audit and Activity Logging |
| Session governance audit verdicts | DevHub's `process_audit` and `process_audit_finding` tables; bc-ai posts the verdict and the findings via `/api/process-audits` | Audit and Activity Logging |

The persistence boundary is asymmetric: bc-ai is the producer; DevHub and bc-core are the consumers. bc-ai never writes to the platform PostgreSQL database; the L-node semantic verdict that bc-core writes per DEC-804874 is bc-core's act based on the AI verdict bc-ai returned. AI Trust and Verification names the verdict trail; Audit and Activity Logging names the cross-service push boundary.

**Governing source.** `bc-ai/app/db/schema.sql`; AI Trust and Verification; Audit and Activity Logging.

## Failure Modes

| Cause | System response |
|---|---|
| Daily budget limit reached during a triplet run | The Bedrock or Anthropic client raises `BudgetExceededException` before the model call; the orchestrator records a draft-evidence row with `failure_reason='budget_exceeded'`; the HTTP response is 429; the calling service receives a structured failure. Gemini budget enforcement is recorded as readiness-baseline drift until the provider path is brought under the same limiter. |
| Maker call times out | The orchestrator records a draft-evidence row; the response carries an error and a routing of `not_applicable`; the calling service decides whether to retry, fail closed, or proceed unverified |
| Checker disagrees with the maker | The gate combines the disagreement into a verdict; the routing typically lands amber or red; the verdict is recorded; the calling service applies its own gate-consumption policy (Quality Gates and Chain Integrity) |
| Provider returns malformed JSON that the agent's `parse_output()` cannot decode | The orchestrator retries up to the configured limit; on persistent failure the run records a draft-evidence row with the parse error |
| Bedrock unreachable (network failure or AWS-side outage) | The Bedrock client raises; the orchestrator either falls back to a registered alternate model or records a draft-evidence row depending on the registry's fallback chain |
| Housekeeping agent's DevHub call fails | The agent records the failure in its run record; the agent does not crash the broader run sequence; reports are still persisted to bc-ai SQLite |
| Auditor's Gemini call fails | The HTTP response carries the error; no `process_audit` row is posted to DevHub; session close is unaffected because the auditor is advisory |
| MCP `ai_invoke` request invokes a model the registry does not know | The tool returns an error; no SQLite row is written |

**Governing source.** `bc-ai/app/clients/`; `bc-ai/app/pipeline/orchestrator.py`; AI Trust and Verification.

## Drift Inventory

Per pattern 69, gaps between the design intent recorded above and the current state are surfaced explicitly.

| Gap | Severity | Detail |
|---|---|---|
| Cross-family discipline is registration discipline, not runtime assertion | Open | Current registry grounding shows seven cross-family triplets and five same-family maker/checker pairings; no shared runtime guard rejects same-family registrations |
| Legacy `nova-*` ids resolve to Gemini profile strings | Open | `app/models/registry.py` names `nova-pro`, `nova-lite`, and `nova-micro` while their profile IDs resolve to `gemini-2.5-flash`; the naming obscures current provider routing |
| The housekeeping scheduler is disabled | Low | Scheduling has migrated to Claude Code scheduled tasks per D269; the scheduler module remains in the repository but does not run in the active deployment |
| The session governance auditor is advisory only | Open | A `fail` verdict records but does not block session close; only the L-node semantic gate per DEC-804874 is a hard close-blocker. Audit and Activity Logging records this advisory posture |
| bc-ai has no cloud deployment posture | Open | The service runs locally on uvicorn; no Docker image, no infrastructure-as-code, no CI/CD; production AI surface depends on the local-only model not being the long-term posture (Auxiliary Services and Infrastructure record this) |
| KPI assistant request logs to structlog but not to a database | Open | Per-call tenant identifier and user identifier are emitted to stdout via structlog; no per-tenant usage record persists; AI Usage Visibility records the broader visibility gap |
| Gemini client does not write `budget_log` or enforce the daily cap | Open | `app/clients/gemini.py` logs token counts but does not call `get_daily_spend()` or `log_budget()`; Gemini-backed makers and gates are outside current cost controls |
| Pricing tables are static | Open | Provider price tables are static code snapshots; provider pricing changes require code update |

**Governing source.** Architecture; Backend Services; Auxiliary Services; AI Trust and Verification; AI Usage Visibility.

## Boundaries with Adjacent Chapters

Several adjacent chapters have surfaces that resemble parts of the AI architecture but are not part of this chapter's scope.

| Adjacent surface | Where it lives | Why it is not this chapter |
|---|---|---|
| Bedrock and Inference Profiles | AI section, next chapter | Owns the inference profile inventory, the model registry shape, the budget controls, and the per-provider client detail. This chapter records that bc-ai branches per provider; the next chapter records what each branch does |
| AI Agents | AI section | Owns the agent inventory at the cluster level (12 maker-checker-gate triplets, 8 housekeeping agents, the auditor) plus the per-agent act identifier and entity scope. This chapter records the patterns; AI Agents records the inventory |
| AI Gates | AI section | Owns the gate verdict authoring contract and the routing semantics that calling services consume. This chapter records that gate verdicts exist and where they land; AI Gates records what they mean |
| AI Trust and Verification | AI section | Owns the trust ladder, the cross-family discipline, the verdict aging policy, and the human-approval surface. This chapter records the cross-family pattern; AI Trust and Verification records the ladder |
| AI Usage Visibility | AI section | Owns the tenant-facing transparency surface: what AI did, what it suggested, the accept and reject trail. This chapter records that bc-ai logs per-call; AI Usage Visibility records the visibility gap |
| Backend Services | Implementation section | Owns bc-ai's deployable boundary at the service level. This chapter records bc-ai's role in the AI surface; Backend Services records bc-ai's deployable shape |
| Auxiliary Services | Implementation section | Owns bc-ai's lighter-deployable treatment alongside bc-core-dashboard, bc-sdg, and bc-website. This chapter records bc-ai's AI architecture; Auxiliary Services records its deployable posture |
| Audit and Activity Logging | Implementation section | Owns the operational governance trail substrate. This chapter records that bc-ai pushes process-audit verdicts to DevHub; Audit and Activity Logging records the substrate |
| Quality Gates and Chain Integrity | Operating Model | Owns the gate authority over runtime decisions. This chapter records that AI verdicts feed bc-core's L-node semantic gate; Quality Gates records the gate's authority |

**Governing source.** Operating Model; Implementation; outline.md §4.4.

## Governing Decisions

| Decision | Title | AI architecture impact |
|---|---|---|
| DEC-c06f41 | Spine expansion to eight sections plus home | The AI section exists as a first-class peer alongside Implementation per DEC-c06f41; this chapter is the section's architectural binder |
| DEC-804874 | D366 L-node semantic gate at session close | bc-core consumes the AI verdict bc-ai returns when computing the L-node semantic verdict; the gate per this ADR is the one hard close-blocker that depends on AI |
| DEC-ebf0b4 | D268 Session Discipline and Data Integrity (ten rules) | The session governance auditor reviews session conduct against these rules; the auditor is advisory, recording verdicts but not blocking close |

**Governing source.** The Authority Model.

## References

- Foundation: Scope and Non-Negotiability
- The Authority Model
- The Dual-Layer Interaction Model
- Operating Model: Overview
- Evidence and Lineage
- Architecture
- Backend Services
- Auxiliary Services
- Audit and Activity Logging
- Bedrock and Inference Profiles
- AI Agents
- AI Gates
- AI Trust and Verification
- AI Usage Visibility
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-804874: L-node semantic gate (D366)
- DEC-ebf0b4: Session Discipline and Data Integrity (D268)
- outline.md §4.4: AI
- Decisions: ADR Registry

