---
id: ai-usage-visibility
order: 32
title: "AI Usage Visibility"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-authority-model, the-dual-layer-interaction-model, operating-model-overview, frontend-experience, audit-and-activity-logging, ai-architecture, ai-agents, ai-gates, ai-trust-and-verification]
governing_sources:
  - Foundation
  - The Dual-Layer Interaction Model
  - The Authority Model
  - Operating Model
  - Frontend Experience
  - Audit and Activity Logging
  - AI Architecture
  - AI Agents
  - AI Gates
  - AI Trust and Verification
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus home; this chapter exists in the AI section)
errata_referenced: []
v2_sources: []
diagrams: []
---

# AI Usage Visibility

## Scope

This chapter records the platform's tenant-facing AI transparency surface in its readiness-baseline state: the bc-admin AI Assistant Drawer that surfaces KPI question-and-answer to platform-scope operators, the queued AI Log and AI Verification tabs in bc-admin whose data hooks are disabled, the tenant-side surface in bc-portal (absent in the readiness baseline), the per-tenant usage records (absent at the database level), the accept-and-reject trail (absent), the per-tenant configuration to opt in or out of AI participation (absent), and the gaps the chapter records as drift.

This chapter sits at the back of the AI section. It is the section's tenant-facing surface chapter. AI Architecture, AI Agents, AI Gates, and AI Trust and Verification record what the platform's AI substrate does; this chapter records what end users (operators in bc-admin, tenant users in bc-portal) see of that substrate.

This chapter does not redefine the maker-checker-gate triplet pattern (deferred to AI Architecture), the agent inventory (deferred to AI Agents), the gate verdict consumption posture (deferred to AI Gates), the trust ladder (deferred to AI Trust and Verification), or the per-tenant binding model that governs which AI features a tenant has access to (deferred to Tenant Entitlement Enforcement in Operating Model and Tenant Lifecycle and Subscription in Operations). The chapter records what is visible; the chapter does not record what is happening underneath the visible surface.

**Governing source.** AI Architecture; Frontend Experience; outline.md §4.4.

## What Tenants See In The Readiness Baseline

Almost nothing in the readiness baseline. The platform's AI surface is largely platform-admin-facing; the tenant-facing transparency surface is queued. The chapter records the as-built honestly per pattern 81: the surface is at an early phase, and the design intent (what AI did, what it suggested, the accept-and-reject trail) is recorded in CLAUDE.md as a known concern but is not realized in code.

| Concern | Tenant-facing state |
|---|---|
| What AI did on a tenant's behalf | Not visible to the tenant; the platform records call-level state in bc-ai's local SQLite plus per-tenant `structlog` logs that go to standard output, but no tenant-visible surface aggregates the activity |
| What AI suggested for a tenant's data | Not visible to the tenant; the maker-checker-gate triplets that operate against tenant data run in operator-driven procedures in bc-admin, not in tenant-driven procedures in bc-portal |
| The accept-and-reject trail | Absent; the platform does not record which tenant accepted which suggestion or rejected which alternative; the bc-ai `review_queue` table is operator-side only |
| Per-tenant AI usage and cost | Not aggregated per tenant; bc-ai's `budget_log` records per-call cost for Bedrock-mediated and direct-Anthropic invocations but does not capture Gemini durable cost in the readiness baseline (Gemini logs tokens and duration via `structlog` only — see Drift Inventory below and Security Operations for the canonical narrowing). The aggregated total that exists is visible to operators only and does not split by tenant. |
| Per-tenant opt-in or opt-out | Absent; no `ai_enabled`, `ai_consent`, or `ai_opt_in` configuration column on tenant-side tables; AI invocation is governed by role and entitlement, not by per-tenant AI policy |

The chapter records this state as the as-built. The CLAUDE.md memory note records the gap explicitly: tenant-facing AI usage visibility (what AI did, what it suggested, the accept-and-reject trail) is a known concern that remains unimplemented in production. This chapter is the documentation home for that gap.

**Governing source.** `bc-ai/app/db/schema.sql`; Frontend Experience; CLAUDE.md.

## bc-admin: The AI Assistant Drawer

The one wired tenant-adjacent surface in the readiness baseline is the AI Assistant Drawer in bc-admin. The Drawer is a non-modal right-hand-side panel mounted globally in bc-admin's app shell; the operator opens it from any page and asks a KPI question. The Drawer calls bc-ai's `POST /api/ai/kpi/ask` endpoint, receives the answer plus citations plus a confidence score plus a screen suggestion, and renders the response read-only with a privacy disclaimer ("Answers within your enterprise boundary; not saved; not used for training").

The Drawer is the platform's first AI transparency surface. The chapter records its readiness-baseline scope: question-and-answer over the KPI catalog, scoped to the operator's authenticated identity, citations to platform documents, no persistence of the conversation, no accept-and-reject UI, no thumbs-up or thumbs-down, no per-message rating. The conversation resets when the operator navigates between entities; there is no conversation history.

The Drawer's audience is platform-admin (`PLATFORM_TENANT='selenite'`, `PLATFORM_ROLE='cfo'` per the source); it is not tenant-facing. A future hardening would surface the Drawer or an analogous Q-and-A surface to tenant users in bc-portal. AI Trust and Verification records that the Q-and-A is single-model (Claude Haiku 4.5 direct); the trust posture is communicated to users only through the privacy disclaimer, not through an explicit trust-level badge.

**Governing source.** `bc-admin/src/components/ai/AiAssistantDrawer.tsx`; Frontend Experience; AI Trust and Verification.

## bc-admin: The Queued AI Tabs

bc-admin carries three AI-related tab components whose UI is implemented and whose data hooks are disabled. The components are visible in the source but render empty states in the running app because the hooks return empty arrays unconditionally.

| Tab | Source location | Anchor purpose |
|---|---|---|
| LogTab | `bc-admin/src/components/ai/LogTab.tsx` | Chronological feed of AI decomposition actions with the verdict column (`agree`, `reconciled`, `disputed`, `failed`) |
| VerificationTab | `bc-admin/src/components/ai/VerificationTab.tsx` | Side-by-side Maker A vs Maker B vs Moderator outputs from KPI decomposition |
| ChatTab | `bc-admin/src/components/ai/ChatTab.tsx` | KPI Assistant answer history with confidence badges, latency, and screen suggestions |

The hooks at `bc-admin/src/api/ai-assistant.ts` (the `useAiActionLog` and `useFormulaVerifications` hooks) carry `enabled: false` query options at the time of writing; the React Query layer does not call the underlying endpoints. The Drawer's KPI Assistant call is the only wired call. A future hardening would land the back-end endpoints, enable the hooks, and surface the historical data in the tabs; the chapter records the queued state.

**Governing source.** `bc-admin/src/components/ai/`; `bc-admin/src/api/ai-assistant.ts`; Frontend Experience.

## bc-portal: Absent

bc-portal has no AI-facing surface at the time of writing. No AI Assistant Drawer, no per-page suggestion surface, no accept-and-reject UI, no AI activity feed. The KPI Assistant in bc-admin is platform-admin-only; tenant users do not have an analogous surface in bc-portal.

The Frontend Experience chapter records that bc-portal carries three incomplete UI iterations under active redesign; the AI surface is not part of any of the three. A future iteration could add an AI surface; the chapter records the absence explicitly per pattern 81 (substrate-canonicality scope at lead matches drift inventory).

**Governing source.** Frontend Experience.

## Per-Tenant Records and Cost Aggregation

The platform's AI substrate does not aggregate per tenant at the database level. bc-ai's `budget_log` records cost per call with the act identifier and the model identifier but no tenant identifier; bc-ai's `evidence` records per-act verdicts with an entity type and an entity identifier but no tenant identifier; bc-core's `l_node_semantic_trace` records per-MC verdicts but the tenant scoping is implicit in the metric contract's tenant binding rather than carried as an explicit column on the trace.

The platform's `structlog` instrumentation does carry a tenant identifier in the per-call log context (the KPI Assistant logs `tenant=request.tenant_id` and `user=request.user_id`); the logs are emitted to standard output and consumed by CloudWatch (when running in AWS) or by a log aggregator. The logs are not durable in a database table; they are observability state, not platform record-of-truth state.

A reader who wants per-tenant AI usage in the readiness baseline reconstructs it from `structlog` aggregation. The reader cannot read it from a platform database query. The drift inventory below records this as Open; a per-tenant AI usage table is queued.

**Governing source.** `bc-ai/app/db/schema.sql`; `bc-ai/app/kpi_assistant/orchestrator.py`; AI Architecture.

## The Accept-and-Reject Trail

The platform does not record which tenant accepted which AI suggestion or rejected which alternative. Two reasons:

First, the tenant-facing surface that would expose suggestions to tenants does not exist (per the bc-portal section above). With no surface, there are no accept-and-reject events to record.

Second, the operator-facing surface that does exist (bc-admin's AI Assistant Drawer plus the queued AI tabs) is read-only. The Drawer's Q-and-A returns answers; there is no UI to mark an answer as accepted or rejected. The KPI decomposition's verdict (`agree`, `reconciled`, `disputed`, `failed`) is the moderator's reconciliation verdict, not an operator's accept-or-reject signal.

bc-ai's `review_queue` table holds amber and red verdicts that need human review; an operator can mark an entry as approved or rejected, and the status updates the queue. The queue is operator-side, not tenant-side; it is the platform's internal QA gate, not a tenant transparency surface. A future hardening would extend the review queue (or build an analogous tenant-side substrate) so tenants can see and act on suggestions made on their behalf; the chapter records the gap.

**Governing source.** `bc-ai/app/db/schema.sql` (the `review_queue` table); `bc-ai/app/kpi/decompose.py`; AI Architecture.

## Per-Tenant Configuration

There is no per-tenant configuration to opt in or out of AI participation in the readiness baseline. The platform's AI invocation is governed by role and entitlement (a platform admin can invoke the AI Assistant Drawer; a tenant user cannot, because the Drawer is platform-scope) rather than by per-tenant AI policy.

A tenant cannot say "do not use AI on my data" or "use only cross-family-verified suggestions on my data" or "flag any AI-bearing record before it lands in my tenant database" in the readiness baseline. The control plane that would carry such a policy does not exist; no `tenant.ai_settings` table holds the per-tenant preference, no enforcement layer reads such a preference, no UI exposes the preference for the tenant to set.

The drift inventory records this. A future Tenant Entitlement Enforcement extension may carry per-tenant AI policy alongside the existing tier scope; the chapter routes the future surface to that chapter.

**Governing source.** AI Architecture; Operating Model: Tenant Entitlement Enforcement.

## Failure Modes

| Cause | System response |
|---|---|
| AI Assistant Drawer call fails (bc-ai unreachable, budget exceeded, model error) | The Drawer renders the error inline in the conversation; the operator sees the failure and can retry; no durable record of the failure surfaces in bc-admin |
| The queued AI tabs' data hooks are called against unimplemented endpoints | The hooks return empty arrays per the disabled query option; the tab renders an empty state; no error surfaces |
| `structlog` per-tenant log is lost (CloudWatch unreachable or log file deletion) | The per-tenant usage state is unrecoverable from the platform; the daily total in `budget_log` survives but the per-tenant split does not |
| An operator wants to check which AI suggestions affected a tenant's data | The operator cannot read this from a platform database query; the operator must reconstruct from `structlog` aggregation or from per-MC trace inspection plus per-tenant binding lookup |

**Governing source.** `bc-admin/src/components/ai/AiAssistantDrawer.tsx`; `bc-ai/app/db/schema.sql`; AI Architecture.

## Drift Inventory

Per pattern 69, gaps between the design intent recorded above and the readiness baseline are surfaced explicitly.

| Gap | Severity | Detail |
|---|---|---|
| Tenant-facing AI surface in bc-portal is absent | Open | No AI Assistant Drawer, per-page suggestion surface, accept-and-reject UI, or activity feed in bc-portal; tenant users have no tenant-facing AI visibility in the readiness baseline |
| Queued bc-admin AI tabs (LogTab, VerificationTab, ChatTab) have disabled data hooks | Open | Components implemented; hooks return empty arrays per `enabled: false`; underlying endpoints not yet built |
| Per-tenant AI usage records are absent at the database level | Open | bc-ai's `budget_log` and `evidence` tables have no tenant column; per-tenant aggregation reconstructs from `structlog` only |
| Accept-and-reject trail is absent | Open | No platform substrate records which tenant accepted which suggestion or rejected which alternative; bc-ai's `review_queue` is operator-side only |
| Per-tenant AI opt-in or opt-out configuration is absent | Open | No `tenant.ai_settings` substrate; tenants cannot decline AI participation, restrict to cross-family-verified verdicts, or otherwise constrain AI on their data in the readiness baseline |
| Trust posture is not surfaced to users | Open | bc-admin's AI Assistant Drawer carries a privacy disclaimer but no trust-level badge; the Q-and-A is single-model and the user reads it without an explicit trust indicator |
| KPI Assistant per-call cost is not visible to the calling user | Low | The cost is recorded in bc-ai's `budget_log` and surfaced to operators through the budget endpoint; it is not surfaced in the Drawer |
| KPI decomposition verdicts (`agree`, `reconciled`, `disputed`, `failed`) are not surfaced anywhere | Open | The verdicts are recorded in bc-ai but bc-admin's LogTab is queued; no operator-facing or tenant-facing surface displays them |
| The AI Assistant Drawer's audience is hardcoded to platform-admin | Low | `PLATFORM_TENANT` and `PLATFORM_ROLE` are constants; broadening the surface to tenant scope requires a code change plus the absent bc-portal-side surface |
| Gemini durable budget capture is absent | Low | bc-ai's `budget_log` is written by the Bedrock client (`bc-ai/app/clients/bedrock.py`) and the direct-Anthropic client (`bc-ai/app/clients/anthropic_client.py`); the Gemini client (`bc-ai/app/clients/gemini.py`) returns token metadata and emits a `gemini_invoke` structured log line but does not call `evidence_store.log_budget`. Gemini cost is reconstructable from `structlog` aggregation only, not from a platform DB query. Mirrors Security Operations' canonical narrowing of the `budget_log` surface to Bedrock + direct-Anthropic. A future hardening would either (a) add Gemini cost estimation + a `budget_log` write in the Gemini client, or (b) document the structured-log path as a permanent secondary surface for Gemini cost. |

**Governing source.** Frontend Experience; AI Architecture; AI Trust and Verification; Security Operations (canonical `budget_log` narrowing).

## Boundaries with Adjacent Chapters

| Adjacent surface | Where it lives | Why it is not this chapter |
|---|---|---|
| AI Architecture | AI section | Owns the maker-checker-gate triplet pattern. This chapter records the visibility surface; AI Architecture records the substrate that the visibility surface should expose |
| AI Agents | AI section | Owns the agent inventory. This chapter records that no surface aggregates per-agent activity for the tenant; AI Agents records the agents whose activity would be aggregated |
| AI Gates | AI section | Owns the verdict consumption posture. This chapter records that the verdict is not surfaced to the tenant; AI Gates records the verdict |
| AI Trust and Verification | AI section | Owns the trust ladder. This chapter records that the trust posture is not visible to users; AI Trust and Verification records the ladder that should be exposed |
| Frontend Experience | Implementation section | Owns the bc-admin and bc-portal surfaces at the design-rationale level. This chapter records the tenant-facing AI surface specifically; Frontend Experience records the broader frontend |
| Audit and Activity Logging | Implementation section | Owns the operational governance trail substrate. This chapter records the absence of per-tenant AI activity persistence; Audit and Activity Logging records the operational substrate that exists |
| Tenant Entitlement Enforcement | Operating Model | Owns the tier scope and the per-tenant catalog visibility model. This chapter records that per-tenant AI policy is queued; Tenant Entitlement Enforcement is where the policy may eventually land |
| Tenant Lifecycle and Subscription | Operations section | Owns the Subscription artifact and the tier-policy substrate. A per-tenant AI policy may attach as a tier dimension; the chapter is named here as the candidate home |
| Notifications and Webhooks | Implementation section | Owns the notification surface (scaffolds only in the readiness baseline). A future tenant notification when an AI verdict affects the tenant's data would land here; the chapter routes the concern |

**Governing source.** Implementation; Operating Model; outline.md §4.4.

## Governing Decisions

| Decision | Title | AI usage visibility impact |
|---|---|---|
| DEC-c06f41 | Spine expansion to eight sections plus home | The AI Usage Visibility chapter exists in the AI section per DEC-c06f41 |

**Governing source.** The Authority Model.

## References

- AI Architecture
- AI Agents
- Bedrock and Inference Profiles
- AI Gates
- AI Trust and Verification
- Frontend Experience
- Audit and Activity Logging
- The Dual-Layer Interaction Model
- DEC-c06f41: Spine expansion to eight sections plus home
- outline.md §4.4: AI
- Decisions: ADR Registry

