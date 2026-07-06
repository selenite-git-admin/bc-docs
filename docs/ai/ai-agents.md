---
id: ai-agents
order: 29
title: "AI Agents"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-authority-model, operating-model-overview, audit-and-activity-logging, ai-architecture, bedrock-and-inference-profiles]
governing_sources:
  - Foundation
  - The Authority Model
  - Operating Model
  - Audit and Activity Logging
  - AI Architecture
  - Bedrock and Inference Profiles
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus home; this chapter exists in the AI section)
  - DEC-ebf0b4 (D268 Session Discipline and Data Integrity; the auditor agent reports against this discipline)
  - DEC-804874 (D366 L-node semantic gate; consumes the cc-field-audit triplet's verdict)
errata_referenced: []
v2_sources: []
diagrams: []
---

# AI Agents

## Scope

This chapter records the AI agent inventory at the cluster level: the twelve maker-checker-gate triplets that bc-core consumes for governed verdicts, the eight housekeeping agents that run against DevHub state, the session governance auditor that runs against Claude Code session payloads, and the KPI decomposition and KPI assistant acts that surface in bc-admin. Per pattern 67 and pattern 74, the chapter is the cluster-level inventory; per-agent prompt content, per-agent input shape, and per-agent output schema are owned by the agent source files in bc-ai and by the queued AI Agent Inventory reference (analogous to the queued Screen Registry reference per outline §4.9). The chapter records what kinds of agents exist, what role each kind plays, and how each is invoked.

This chapter sits between Bedrock and Inference Profiles and AI Gates. Bedrock and Inference Profiles records the model substrate; this chapter records the agents the substrate serves; AI Gates records the gate verdict authoring contract that bc-core consumes from the triplets recorded here.

This chapter does not redefine the maker-checker-gate triplet pattern (deferred to AI Architecture), the model registry shape (deferred to Bedrock and Inference Profiles), the gate verdict authoring contract (deferred to AI Gates), the cross-family verification model (deferred to AI Trust and Verification), or the tenant-facing transparency surface (deferred to AI Usage Visibility). Where this chapter names an agent, the per-agent prompt and the per-agent decision rules are owned by the agent's source file at `bc-ai/app/agents/` or `bc-ai/app/housekeeping/agents/`.

**Governing source.** AI Architecture; outline.md §4.4.

## The Twelve Maker-Checker-Gate Triplets

bc-ai registers twelve governed AI acts at the time of writing. Each act is a maker-checker-gate triplet per the pattern AI Architecture records. The acts are registered in the `FLOWS` dictionary at `bc-ai/app/agents/__init__.py:21-34`. Each act has an act identifier (the codebase's `flow_id`), an entity scope, and a triplet of agent classes.

| Act identifier | Entity scope | Anchor purpose |
|---|---|---|
| `bf-pii-classify` | `business_field` | Classify a candidate Business Field's PII sensitivity |
| `bf-dedup` | `business_field` | Detect duplicate Business Field candidates against the existing master |
| `bo-suggest` | `business_object` | Suggest a Business Object composition from a set of candidate Business Fields |
| `bo-dedup` | `business_object` | Detect duplicate Business Object candidates against the existing master |
| `field-map` | `field_mapping` | Suggest a Source Field to Business Field mapping |
| `metric-trace` | `metric` | Trace a metric's lineage through the contract chain |
| `eval-advise` | `canonical_object` | Advise on Canonical Object field-by-field evaluation |
| `cc-field-audit` | `cc_field_mapping` | Audit a CC field mapping change for honesty against the Business Field source of truth |
| `chain-audit` | `metric_chain` | Audit a metric chain's L-node completeness and semantic correctness |
| `table-verify` | `source_table` | Validate a Source Table candidate against the source-system metadata |
| `source-verify` | `source_system` | Validate a Source System provider, name, and version |
| `metric-verify` | `metric_definition` | Validate a metric definition's grain, formula, and semantic shape |

Each triplet declares a maker class, a checker class, and a gate class. The current registry only partially realizes the cross-family pattern AI Trust and Verification records: seven triplets pair Gemini makers with direct-Anthropic checkers; five retain same-family maker/checker pairings. The per-agent class lives at `bc-ai/app/agents/<flow-name>.py`; the chapter routes the reader to the source file rather than enumerating the class shape.

The triplets are exposed via HTTP at `POST /api/ai/suggest/<flow-id>`. A bulk endpoint at `POST /api/ai/bulk` orchestrates a batch of acts in a single request. The verdict shape is the `PipelineResult` model AI Architecture records: maker output, checker output, gate output, combined confidence, routing in `{green, amber, red}`, and the persisted evidence identifier.

The cc-field-audit triplet is the only triplet wired into bc-core's L-node semantic gate at the time of writing (per AI Gates). The other eleven triplets exist but are invoked by direct callers (operator-driven verification through bc-admin, ad-hoc bulk runs); their integration into a governed gate that runs at a boundary act is queued.

**Governing source.** `bc-ai/app/agents/__init__.py`; `bc-ai/app/agents/`; AI Architecture; AI Trust and Verification.

## The Eight Housekeeping Agents

bc-ai registers eight housekeeping agents at the time of writing. Each agent runs the three-phase pattern AI Architecture records: an `assess()` phase that gathers DevHub state, a `recommend()` phase that classifies findings (with or without an LLM call per the agent's `uses_llm` flag), and an `act()` phase that executes auto-actions and collects per-finding recommendations. The agents are registered at `bc-ai/app/housekeeping/__init__.py:27-51`.

| Agent identifier | Uses LLM | Anchor purpose |
|---|---|---|
| `doc-staleness` | yes | Detect stale documents in DevHub's document index; classify staleness severity; mark or archive per the agent's policy |
| `session-hygiene` | yes | Review recent sessions for hygiene issues (orphaned sessions, missing change records, missing self-audit, sessions with anomalous duration); propose triage actions |
| `task-triage` | yes | Review the task backlog for stale tasks, malformed priorities, or missing fields; propose triage actions |
| `nc-aging` | yes | Review the QA non-conformance register for aging items; classify severity; propose escalation |
| `registry-refresh` | no | Walk the bc-docs and DevHub registry indices and refresh derived state; pure automation, no LLM |
| `risk-review` | yes | Review the risk register for state transitions, mitigations, or aging items |
| `qa-patrol` | no | Run QA audit sweeps on repositories that are due for audit per the seven-day cadence; trigger DevHub's QA audit endpoint |
| `mkdocs-maintainer` | no | Walk the bc-docs MkDocs build artifacts; flag broken cross-references and stale generated pages |

The housekeeping scheduler is disabled at the time of writing per a code note dated to D269; agents are invoked on demand through HTTP endpoints (`POST /api/ai/housekeeping/run` for all agents, `POST /api/ai/housekeeping/run/{agent_id}` for one). The reports persist to bc-ai's local SQLite under `housekeeping_run` and `housekeeping_finding`; the agents push relevant findings back to DevHub through the REST client at `bc-ai/app/housekeeping/client.py`.

The cross-service push surface is named here at the architectural level: the housekeeping client posts to DevHub's `/api/projects`, `/api/projects/{slug}/sessions`, `/api/tasks`, `/api/qa/audits/run`, and the documents endpoints. Per pattern 82, the cross-service push has been verified at both ends in a recent audit cycle; the QA audit endpoint mismatch that was recorded as drift in the Audit and Activity Logging chapter has been closed (bc-ai commit `8ff8e44`). Audit and Activity Logging records the substrate.

**Governing source.** `bc-ai/app/housekeeping/__init__.py`; `bc-ai/app/housekeeping/agents/`; `bc-ai/app/housekeeping/client.py`; Audit and Activity Logging.

## The Session Governance Auditor

The session governance auditor is a single agent at the time of writing. It accepts a session payload at `POST /api/ai/audit/session`, runs a deterministic validator phase (rule-based checks against the session-discipline rules per DEC-ebf0b4), renders a Jinja2 prompt against the payload plus any referenced SOP, invokes Gemini 2.5 Pro, parses the structured findings, computes a verdict (`pass`, `concerns`, or `fail`) and a verdict score, and posts the verdict and the per-finding rows to DevHub's `/api/process-audits` endpoint. The auditor's source code lives at `bc-ai/app/auditor/`; the prompt template lives at `bc-ai/app/prompts/process-audit/v1.0/audit.md`.

The auditor uses Gemini 2.5 Pro rather than Gemini 2.5 Flash because the session payload is large (full plan, full report, checkpoints, files changed, commits) and because the verdict warrants more capable inference per call. The auditor's model is reserved at registration; the chapter routes to `bc-ai/app/auditor/config.py` for the per-call configuration.

The auditor is advisory at the time of writing. A `fail` verdict records into DevHub's `process_audit` table but does not block session close; only the L-node semantic gate per DEC-804874 is the hard close-blocker. The gate semantics live in AI Gates; the audit substrate lives in Audit and Activity Logging.

**Governing source.** `bc-ai/app/auditor/`; `bc-ai/main.py`; Audit and Activity Logging; DEC-ebf0b4; DEC-804874.

## KPI Decomposition and the KPI Assistant

bc-ai exposes two KPI-related acts that do not follow the maker-checker-gate triplet pattern. The first is KPI decomposition (`POST /api/ai/kpi/decompose`): a metric definition request is decomposed into candidate Business Fields and contract bindings using direct Anthropic calls: Haiku 4.5 as Maker A, Sonnet 4.5 as Maker B, and Haiku 4.5 as moderator. The act records the decomposition with a verdict in `{agree, reconciled, disputed, failed}`; the verdict surfaces in bc-admin's AI Log tab when the corresponding endpoints land (the bc-admin tabs are present but the data hooks are disabled per the AI Usage Visibility drift inventory).

The second is the KPI Assistant (`POST /api/ai/kpi/ask`): a question-and-answer surface that bc-admin's AI Assistant Drawer consumes (per Frontend Experience). The KPI Assistant is a single-act flow (no triplet); it invokes Claude Haiku 4.5 against a tenant-scoped prompt, returns the answer with citations and a confidence score, and logs the request to `structlog` (no database persistence per AI Usage Visibility's drift inventory).

Neither act is wired into a governed gate. They are operator-driven and tenant-driven verification surfaces; their verdicts inform humans rather than running gates.

**Governing source.** `bc-ai/app/kpi/decompose.py`; `bc-ai/app/kpi_assistant/orchestrator.py`; `bc-ai/main.py`; AI Usage Visibility.

## Per-Agent Detail Is Routed, Not Enumerated

Per pattern 67 and pattern 74, the chapter does not enumerate per-agent prompt content, per-agent decision rules, per-agent confidence thresholds, or per-agent failure modes. Each agent's source file is the authoritative reading for those facts; the queued AI Agent Inventory reference (when it exists) will surface the inventory at the per-agent level the same way the Data Dictionary reference surfaces per-table detail. The chapter's role is to record the agents at the cluster level so a reader can locate the agent that handles a given concern.

A reader who needs the per-agent detail for `cc-field-audit` reads `bc-ai/app/agents/cc_field_audit.py`. A reader who needs the per-agent detail for `task-triage` reads `bc-ai/app/housekeeping/agents/task_triage.py`. A reader who needs the auditor's prompt reads `bc-ai/app/prompts/process-audit/v1.0/audit.md`. The chapter does not duplicate the source files.

**Governing source.** `bc-ai/app/agents/`; `bc-ai/app/housekeeping/agents/`; `bc-ai/app/prompts/`.

## Failure Modes

| Cause | System response |
|---|---|
| A maker-checker-gate triplet's checker disagrees with the maker | The gate combines the disagreement; routing typically lands amber or red; the calling service applies its own gate-consumption policy |
| A housekeeping agent's DevHub call fails | The agent records the failure in its run record; the agent does not crash the broader run sequence; reports are still persisted to bc-ai's local SQLite |
| The session governance auditor's Gemini call fails | The HTTP response carries the error; no `process_audit` row is posted to DevHub; session close is unaffected because the auditor is advisory |
| KPI decomposition's two Makers produce wildly different candidates that the Moderator cannot reconcile | The verdict is `disputed`; the act surfaces the dispute to the calling user; no automated retry |
| KPI Assistant's tenant-scoped prompt returns a low-confidence answer | The answer is returned with the confidence score; the calling surface (bc-admin) decides whether to surface the low confidence to the user |
| An agent's `parse_output()` cannot decode the model's response | The orchestrator retries up to the configured limit; on persistent failure the run records a draft-evidence row with the parse error |

**Governing source.** `bc-ai/app/agents/`; `bc-ai/app/housekeeping/`; `bc-ai/app/auditor/`; `bc-ai/app/kpi/`; `bc-ai/app/kpi_assistant/`.

## Drift Inventory

Per pattern 69, gaps between the design intent recorded above and the current state are surfaced explicitly.

| Gap | Severity | Detail |
|---|---|---|
| Only `cc-field-audit` is wired into a governed bc-core gate | Open | The other eleven triplets are operator-driven; integration into governed gates at boundary acts (admission, canonical, metric, action) is queued. AI Gates records the gate-consumption posture |
| The housekeeping scheduler is disabled | Low | Scheduling has migrated to Claude Code scheduled tasks per D269; the scheduler module remains in the repository but does not run in the active deployment |
| The session governance auditor is advisory only | Open | A `fail` verdict records but does not block session close; only the L-node semantic gate per DEC-804874 is a hard close-blocker. Audit and Activity Logging records this advisory posture |
| KPI decomposition verdicts are not surfaced in bc-admin | Open | bc-admin has the AI Log and AI Verification tabs but the data hooks are disabled (AI Usage Visibility records the broader gap) |
| The AI Agent Inventory reference is queued | Low | Per-agent prompt content, decision rules, and confidence thresholds live in source files; a generated reference surface (analogous to Data Dictionary) is queued |
| No per-agent ownership or maturity column in the registry | Low | The agent registry does not declare which team owns each agent or the maturity stage (alpha, beta, production); the `status` field in the model registry covers model health, not agent health |

**Governing source.** AI Architecture; AI Gates; AI Usage Visibility.

## Boundaries with Adjacent Chapters

| Adjacent surface | Where it lives | Why it is not this chapter |
|---|---|---|
| AI Architecture | AI section | Owns the maker-checker-gate triplet pattern, the housekeeping agent pattern, and the auditor pattern. This chapter records the agent inventory; AI Architecture records the patterns |
| Bedrock and Inference Profiles | AI section | Owns the model substrate that the agents consume. This chapter records the agents; Bedrock and Inference Profiles records the substrate |
| AI Gates | AI section | Owns the gate verdict authoring contract and the bc-core consumption posture. This chapter records that `cc-field-audit` is the only triplet wired into a governed gate; AI Gates records the consumption posture |
| AI Trust and Verification | AI section | Owns the trust ladder and the cross-family discipline. This chapter records the triplet inventory and current pairing drift; AI Trust and Verification records what cross-family pairing buys |
| AI Usage Visibility | AI section | Owns the tenant-facing transparency surface. This chapter records that KPI Assistant logs to `structlog` only; AI Usage Visibility records the broader visibility gap |
| Audit and Activity Logging | Implementation section | Owns the operational governance trail. This chapter records that the auditor posts to `/api/process-audits`; Audit and Activity Logging records the substrate |
| Quality Gates and Chain Integrity | Operating Model | Owns the gate authority over runtime decisions. This chapter records the agent inventory; Quality Gates records which gates run when |

**Governing source.** Operating Model; Implementation; outline.md §4.4.

## Governing Decisions

| Decision | Title | AI agent impact |
|---|---|---|
| DEC-c06f41 | Spine expansion to eight sections plus home | The AI Agents chapter exists in the AI section per DEC-c06f41 |
| DEC-ebf0b4 | D268 Session Discipline and Data Integrity (ten rules) | The session governance auditor reviews session conduct against these rules; the auditor is advisory, recording verdicts but not blocking close |
| DEC-804874 | D366 L-node semantic gate at session close | The cc-field-audit triplet's verdict is consumed by bc-core's L-node semantic gate per this ADR; the gate is the one hard close-blocker that depends on AI |

**Governing source.** The Authority Model.

## References

- AI Architecture
- Bedrock and Inference Profiles
- AI Gates
- AI Trust and Verification
- AI Usage Visibility
- Audit and Activity Logging
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-ebf0b4: Session Discipline and Data Integrity (D268)
- DEC-804874: L-node semantic gate (D366)
- outline.md §4.4: AI
- Decisions: ADR Registry



