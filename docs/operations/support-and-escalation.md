---
id: support-and-escalation
order: 37
title: "Support and Escalation"
status: drafting
authority: authoritative
depends_on: [the-authority-model, tenant-lifecycle-and-subscription, incident-and-change-management, observability-and-telemetry]
governing_sources:
  - The Authority Model
  - Tenant Lifecycle and Subscription
  - Incident and Change Management
governing_adrs:
  - DEC-324d9e (Stripe billing; four subscription tiers)
  - DEC-1392ee (Demo tier policy)
  - DEC-b97390 (Embedded documentation reader in bc-admin with native React implementation)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Support and Escalation

## Scope

This chapter records the operational view of platform support and escalation. It states the per-tier support posture that derives from DEC-324d9e (the four subscription tiers and their commercial categorization), the demo-tier support boundary per DEC-1392ee, the platform-side escalation path that routes a tenant-surfaced concern back to the platform team, the incident-class scope (the subset of incidents that constitute customer-facing support events versus the broader incident set that Incident and Change Management governs), the customer-communication surfaces in the readiness baseline, and the queued surfaces that a mature support function will demand. It records the boundary between Support and Escalation and the platform-side change governance (Incident and Change Management). It records the as-built drift between the procedure and the platform's readiness-baseline support posture, which is largely aspirational against a mature support function.

This chapter does not redefine the Subscription artifact or the lifecycle state machine (Tenant Lifecycle and Subscription), the platform-side incident response (Incident and Change Management), or the audit substrate that records support events (Audit and Activity Logging in Implementation).

The chapter records the readiness baseline honestly per pattern 81. Most of the customer-facing support surface is queued; the chapter does not present an aspirational SLA-and-on-call posture as if it were real.

**Governing source.** outline.md §4.7; Tenant Lifecycle and Subscription.

## Per-Tier Support Posture

Per DEC-324d9e, the platform recognizes four subscription tiers. Each tier carries an implicit support posture, recorded here as the chapter's interpretation of the tier model rather than as a separate SLA artifact (no SLA artifact is part of the readiness baseline).

| Tier | Implicit support posture |
|---|---|
| Demo | Self-service signup; auto-suspend at Day 14 per DEC-1392ee; data retained 30 days then purged. No support beyond documentation; the demo tenant is exploration substrate, not a supported runtime |
| Starter | Self-service via external billing platform; community or async-support channel implicit; no on-call commitment |
| Professional | Self-service or sales-assisted; the chapter interprets the tier as carrying business-hours support without on-call commitment; the actual support arrangement is per-customer at Subscription authoring time |
| Enterprise | Sales-led with invoice billing; the chapter interprets the tier as carrying contractual support arrangements per the Order Form; the platform-side response is per-customer per-contract |

The chapter does not assert SLA hours, response-time guarantees, or escalation-tier definitions. None of these are codified in the readiness baseline; the per-customer Subscription authoring at Tier Professional or Enterprise is the place where the per-customer commitment lives if any.

**Governing source.** Tenant Lifecycle and Subscription; DEC-324d9e; DEC-1392ee.

## Customer Surfaces In The Readiness Baseline

| Surface | Form |
|---|---|
| The bc-admin documentation reader | Per DEC-b97390; the bc-admin embedded reader serves the platform's documentation under JWT-guarded access; the customer reads the same documentation the platform team reads |
| Email to the platform team | The general support inbox; no automated triage or ticketing surface in the readiness baseline |
| The bc-portal customer frontend | The customer's day-to-day operational surface; not a support surface per se but the place the customer surfaces concerns through the in-app behavior |

A customer ticketing system (ServiceDesk, Zendesk, Intercom, Front, or equivalent) is not part of the readiness baseline. A customer concern arrives through the email inbox or through direct sales-led channels for Professional and Enterprise tiers.

**Governing source.** Tenant Lifecycle and Subscription.

## Platform-Side Escalation Path

When a customer concern surfaces, the platform-side response runs through the same DevHub session substrate that governs every platform action.

| Step | Form |
|---|---|
| 1. Triage | The platform team reviews the customer concern; classifies it as a support question (documentation), a configuration concern (Tenant Onboarding or Connection authoring), an incident (chain regression, AI verdict anomaly, infrastructure failure), or a change request (new feature, contract migration, threshold update) |
| 2. Open a session | The platform team opens a DevHub session against the relevant project (`bc-core`, `bc-admin`, `bc-portal`, `bc-ai`, etc.) per CLAUDE.md session protocol |
| 3. Save plan | The session plan records the customer concern, the proposed response, the affected files, the risks |
| 4. Run the response | The session runs the response; mid-session checkpoints record progress |
| 5. Close session with change record | The session close writes the change record; the report-side carries the verification, the followup tasks, and the customer-facing communication |
| 6. Communicate to the customer | The platform team responds to the customer through the channel the concern arrived on |

The discipline is the same as for any platform change. The customer concern is the trigger; the change-record substrate is the audit trail.

**Governing source.** Incident and Change Management; CLAUDE.md (Session Protocol section).

## Incident-Class Scope

Not every incident the platform's Incident and Change Management chapter governs is a customer-facing support event. The scope of customer-facing support events is narrower:

| Incident class | Customer-facing? |
|---|---|
| Tenant database unreachable | Yes; the customer notices |
| Tenant chain status regression (one or more MCs drop from full to partial) | Yes; the customer notices on the bc-admin Metric Readiness page |
| Tenant Connection credential drift | Yes; the customer's source data stops admitting |
| Platform-wide bc-core outage | Yes; every tenant is affected |
| AI provider rate limit hitting maker-checker-gate runs | Sometimes; the affected gates are visible in the AI evidence trail; the customer may notice as latency or as missing AI-suggested actions |
| Per-MC formula evaluation regression | Sometimes; the customer notices if the metric value changes unexpectedly |
| Internal schema migration | Rarely; the customer should not notice if the migration is correctness-preserving |
| Internal contract creation drift | Rarely; the customer notices only if the drift surfaces in the chain status SSOT |

The customer-facing classification is operator judgment per concern. The chapter records the classes; the per-incident decision lives in the session that responds.

**Governing source.** Incident and Change Management; Observability and Telemetry.

## Customer Communication Cadence

The readiness-baseline cadence for platform-side communication to the customer:

| Event | Communication form | Cadence |
|---|---|---|
| Subscription tier change | Stripe billing email (per DEC-324d9e); platform-side email confirms | Per change |
| Demo tier auto-suspend approaching | The platform's auto-suspend task (queued) may send an email; the readiness baseline relies on operator-driven communication for the warning | Per Day 14 milestone |
| Tenant onboarding milestone | Operator-driven; no automated milestone email in the readiness baseline | Per onboarding step |
| Incident notification (when wired) | No automated path in the readiness baseline; operator-driven email | Per incident |
| Documentation update | The bc-admin reader serves the active documentation set on every page load; no separate update notification | Continuous |
| Major release | No automated release-notification surface in the readiness baseline | No automated cadence |

The chapter records the absence honestly. A mature support function will need automated communication for tier changes, milestones, incidents, and major releases; the platform's queued path is to wire these communications through the Notifications and Webhooks surface that Implementation governs, with the slim baseline recorded in the Notifications and Webhooks drift inventory.

**Governing source.** Tenant Lifecycle and Subscription; Notifications and Webhooks (Implementation).

## Aspirational Surfaces

| Surface | Form |
|---|---|
| Customer ticketing system | No ServiceDesk, Zendesk, Intercom, Front, or equivalent integration; email inbox is the substitute |
| Tier-based SLA codification | No SLA artifact per tier; per-customer arrangements live in Subscription authoring (Professional, Enterprise) only |
| On-call rotation (customer-facing) | No on-call schedule for customer-facing support; the platform team responds during business hours |
| Status page (public or tenant-facing) | No status.example.com; the platform's chain status SSOT is operator-facing only |
| Customer health score | No per-tenant health score that aggregates chain status, AI verdict mix, Connection liveness, login frequency |
| In-app customer support widget | No widget in bc-portal or bc-admin that opens a support conversation [^residual-bc-portal] |
| Knowledge base separate from documentation | No FAQ or "how do I" library separate from the chapter-by-chapter documentation; the documentation is the knowledge base |
| Per-customer escalation contact list | No per-customer contact registry; sales-led tier customers have implicit contacts via the Account Executive relationship; self-service tier customers have only the support inbox |

**Governing source.** Tenant Lifecycle and Subscription; Notifications and Webhooks.

## Failure Modes

| Cause | System response |
|---|---|
| Customer email arrives outside business hours | No on-call response; the email queues until the next business day |
| Customer reports chain regression | Operator opens a session; runs MC Chain Integrity diagnostic; remediates; communicates back |
| Customer reports tenant DB unreachable | Operator inspects the tenant database connectivity; the per-tenant database isolation makes this a per-tenant question; remediates per the failure cause |
| Customer reports AI suggestion looks wrong | Operator inspects the bc-ai evidence trail for the affected agent; per AI Trust and Verification, the maker-checker-gate verdict surfaces the issue; remediates per the underlying cause (prompt drift, model regression, source data drift) |
| Customer reports unexpected metric value | Operator opens a session; runs the MC Chain Integrity diagnostic; if the value is correct, the customer's expectation is mismatched and the response is documentation-driven; if the value is wrong, the diagnostic identifies the preceding-layer gap and the remediation runs through the appropriate Onboarding chapter |
| Customer disputes a Subscription tier or billing event | Operator engages the billing platform's surface (Stripe per DEC-324d9e) to inspect; the platform-side response runs through Tenant Lifecycle and Subscription |

**Governing source.** Tenant Lifecycle and Subscription; Incident and Change Management; MC Chain Integrity.

## Drift Inventory

| Drift item | Form |
|---|---|
| No formal support function | The platform has no dedicated support team, no ticketing system, no on-call rotation; the platform team handles support directly during business hours |
| No SLA codification | Per-tier SLA is implicit, not codified; per-customer arrangements at Professional and Enterprise live in Subscription authoring without machine-readable form |
| No automated communication | Subscription tier changes, demo-tier suspensions, incidents, and major releases all rely on operator-driven email |
| No status page | No public or tenant-facing status surface |
| No customer health score | No per-tenant aggregation of chain status, AI verdict mix, Connection liveness |
| No in-app support widget | bc-portal and bc-admin have no embedded support entry point [^residual-bc-portal] |
| No knowledge base separate from chapter documentation | The documentation is the knowledge base; no FAQ or "how do I" library |
| No per-customer escalation registry | Per-customer contact information is sales-led for Professional and Enterprise; self-service tier has only the support inbox |
| Customer notification queued through Notifications and Webhooks | The Notifications and Webhooks chapter (Implementation) records the slim "not-yet-built" state of the notification surface; customer notifications are blocked behind that surface's realization |

**Governing source.** Tenant Lifecycle and Subscription; Notifications and Webhooks.

## Boundary with Other Operations Chapters

| Chapter | Relationship |
|---|---|
| Tenant Lifecycle and Subscription | Owns the Subscription tier model that this chapter consumes for per-tier support posture |
| Deployment Topology | Independent at the support layer |
| Security Operations | Customer-reported security incidents route through this chapter's escalation path; the platform-side response runs through Security Operations |
| Upgrade and Migration | Customer-affecting migrations are communicated through this chapter's customer-communication cadence |
| Observability and Telemetry | Provides the substrate this chapter reads for customer-affecting incidents |
| Performance and Scale | Customer-reported performance concerns route through this chapter's escalation path |
| Incident and Change Management | Provides the platform-side substrate; this chapter is the customer-side complement |

**Governing source.** The owning Operations chapters; outline.md §4.7.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-324d9e | Establishes the four subscription tiers; this chapter interprets the tier model for support posture |
| DEC-1392ee | Establishes the demo tier policy; this chapter records the demo-tier support boundary (no support beyond documentation) |

**Governing source.** Decisions: ADR Registry.

| DEC-b97390 | Establishes the bc-admin embedded documentation reader as the customer-facing surface that serves the same documentation the platform team reads; this chapter records the reader as one of the three readiness-baseline customer surfaces |

## References

- The Authority Model
- Tenant Lifecycle and Subscription
- Incident and Change Management
- Observability and Telemetry
- Security Operations
- Upgrade and Migration
- Performance and Scale
- Notifications and Webhooks (Implementation)
- MC Chain Integrity
- Chain Completeness and Verdict
- DEC-324d9e: Stripe billing; four subscription tiers
- DEC-1392ee: Demo tier policy
- CLAUDE.md (Session Protocol section)
- outline.md §4.7: Operations

[^residual-bc-portal]: **Residual risk (audit GAP-010).** bc-portal and BareCount-Customer-Portal repos were not readable in the referenced platform code/docs gap audit. Claims about bc-portal frontend behavior, design system, tenant override, embedded widgets, and information architecture rest on prior grounding, not on this-pass verification. Treat as unverified until a dedicated readable bc-portal pass confirms the frontend state. Source: `bc-docs/reports/platform-code-doc-gap-report.md` GAP-010.


