---
id: notifications-and-webhooks
order: 24
title: "Notifications and Webhooks"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-authority-model, operating-model-overview, architecture, backend-services, internal-modules, infrastructure, api-surface, frontend-experience]
governing_sources:
  - Foundation
  - The Authority Model
  - Operating Model
  - Architecture
  - Backend Services
  - Internal Modules
  - Infrastructure
  - API Surface
  - Frontend Experience
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus home; this chapter exists in the reshaped Implementation section)
  - DEC-324d9e (Subscription tiers and hosting variants; anticipates a Stripe webhook receiver)
  - DEC-1918d0 (Deployment and database architecture; ten normalization rules; referenced for the FK and soft-delete drift on the scaffold tables)
  - DEC-771baf (Tenant database topology; platform-tenant one-way dependency)
  - DEC-3395bc (v3 documentation structure; bc-core JWT-guarded /api/docs/* and the structured JSONL audit log; cross-referenced for the access-log boundary)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Notifications and Webhooks

## Scope

This chapter records the platform's notifications and webhooks surface in the readiness baseline: the database scaffolds in the `infrastructure` schema, the navigation-chrome stubs in the two frontends, the aspirational webhook receivers anticipated by governing decisions, and an explicit accounting of what is wired, what is scaffolded, what is anticipated, and what is absent. The chapter records reality and the gaps; it does not describe an aspirational delivery surface.

The platform does not send outbound notifications, expose inbound webhook receivers, or emit outbound webhooks to caller-configured URLs in the readiness baseline. The chapter exists in the spine because a future build is anticipated and because the architectural invariants any future implementation must honor are worth governing before implementation. Per pattern 69, the in-flight state is recorded honestly rather than implied to be more complete than it is.

This chapter sits between Frontend Experience and Audit and Activity Logging. Frontend Experience records the consumers of bc-core's API surface; Audit and Activity Logging (queued) records the immutable platform-side fact for governance and compliance. The relation between this chapter and Audit and Activity Logging is the same fact, two surfaces: Audit and Activity Logging records the fact for preservation and external attestation; Notifications and Webhooks (when built) surfaces selected facts to humans through a notification channel or to external systems through a webhook emitter.

This chapter does not redefine Foundation invariants, the Authority Model, or the Architecture chapter's commitments. It does not enumerate the fact-emission acts that would feed notifications (those are the boundary acts owned by Operating Model: Admission and Observation, Canonical Evaluation, Metric Evaluation, Action Evaluation), the gate verdicts that might surface as notifications (deferred to Quality Gates and Chain Integrity), the AI activations that might produce notifications (deferred to AI Gates and AI Trust and Verification when drafted in the AI section), the contracted source-system observation surface that is sometimes confused with inbound webhooks (deferred to Connectors and Readers; a tenant-bound source connector is not a webhook receiver), or the Stripe billing artifact whose webhook receiver is anticipated (deferred to Tenant Lifecycle and Subscription).

**Governing source.** Architecture; Backend Services; Infrastructure; outline.md §4.3.

## Wired In The Readiness Baseline

Nothing. The platform has no wired outbound notification surface, no wired inbound webhook receiver, and no wired outbound webhook emitter in the readiness baseline.

| Concern | State |
|---|---|
| Outbound email | Absent. No SMTP client, no AWS SES integration, no SendGrid or Mailgun client, no `@nestjs-modules/mailer` registration in bc-core's `app.module.ts` |
| Outbound in-app notifications | Absent as a durable surface. Sonner toasts in both frontends provide transient feedback only and are not durable notification records |
| Outbound SMS, push, Slack, Teams, or Discord | Absent. No Twilio, no SNS push, no `web-push`, no `firebase-admin`, no POSTs to `hooks.slack.com`, `webhook.office.com`, or `discord.com/api/webhooks` |
| Inbound webhook receivers | Absent. No routes matching `/webhook`, `/webhooks`, `/hooks`, `/integrations`, or `/callbacks`; no HMAC signature verification (`crypto.createHmac`, `timingSafeEqual`, `stripe-signature`, `x-hub-signature-256`); no raw-body middleware in `main.ts` to support signature-verifiable receivers |
| Outbound webhook emitters | Absent. No POST loops to caller-configured URLs, no signing of outbound payloads, no retry queue or dead-letter queue |
| Event plumbing | Absent. No `@nestjs/event-emitter`, no `EventEmitter2` instances, no `@OnEvent` decorators in bc-core |

The surface is not stubbed-with-disabled-deliveries; it is structurally absent. There is no bc-core module that, if a feature flag flipped, would begin sending or receiving.

**Governing source.** `bc-core/package.json`; `bc-core/src/app.module.ts`; `bc-core/src/main.ts`.

## Schema Scaffolds

The `infrastructure` schema in the platform database carries three tables that anticipate a future notification and integration surface. They are defined in `bc-core/docker/redesign/02-platform-tables/09-infrastructure.sql` and exported from `bc-core/src/database/schema/infrastructure/`. None of the three is queried by any service at the time of writing; they exist only as schema.

| Table | Shape | Anticipated role |
|---|---|---|
| `infrastructure.email_template` | `template_code` (UNIQUE), `display_name`, `subject_text`, `body_html`, `body_text`, `variables_json`, `status_code` in `{draft, active, deprecated}` | Template authoring for outbound email; tenant-scoped templates would require an additional column |
| `infrastructure.notification_log` | `template_code` (text reference, no FK), `channel_code` in `{email, in_app, webhook}`, `recipient_ref`, `tenant_id`, `subject_text`, `status_code` in `{pending, sent, delivered, failed, bounced}`, `error_detail`, `sent_at`; indexed on template, recipient, tenant-and-time, status | Append-only delivery record; the `channel_code` enum is the platform's first commitment that webhook delivery is one of three notification channels rather than a separate concept |
| `infrastructure.idempotency_keys` | `key` (PK), `method`, `path`, `request_hash`, `status_code`, `response_body` | General-purpose idempotency surface; would support inbound webhook receivers that need request-replay protection, though the table is also reachable for any other request-deduplication concern |

Two scaffold drifts are recorded explicitly. First, `notification_log.template_code` is a text reference to `email_template.template_code` rather than a foreign key. Per DEC-1918d0 Rule 3 (FK constraints mandatory; every reference to another table's primary key must have an explicit FK), the constraint is missing. The constraint must be added before delivery records are written, so that template renames or deletions do not orphan delivery rows. Second, neither table carries `archived_at` per DEC-1918d0 Rule 8 (soft deletes use `archived_at`); for a delivery log this is operationally fine (delivery rows are append-only, and the absence of soft delete is correct), but for `email_template` a future implementation that retires templates without deleting their delivery history will need either `archived_at` on `email_template` or the `status_code = 'deprecated'` mechanism the table already declares.

**Governing source.** `bc-core/docker/redesign/02-platform-tables/09-infrastructure.sql`; `bc-core/src/database/schema/infrastructure/`; DEC-1918d0.

## Frontend Stubs

Both browser shells render notification chrome that does not yet connect to any backend surface. The stubs are honest placeholders rather than disabled live surfaces.

| Frontend | Stub | Behavior |
|---|---|---|
| bc-portal | Bell icon in the top navigation bar; routes to `/alerts` | Prior grounding reported an "under development" placeholder with no badge count, notification fetch, or real-time channel; this review could not independently verify the bc-portal path |
| bc-portal | Top-bar messages icon; routes to `/messages` | Prior grounding reported the same placeholder pattern as `/alerts`; this review could not independently verify the bc-portal path |
| bc-admin | Bell icon in the top navigation bar | Verified in `bc-admin/src/components/TopNavbar.tsx`: the button has no click handler, no badge count, no dropdown, and no destination route |

Sonner toasts are present in both frontends and are fully functional, but toasts are transient UI feedback for the immediate user action, not durable notifications. The chapter does not classify toasts as part of the notification surface.

When the notification surface is built, the existing bell-icon chrome is a plausible attachment point for a durable notification view. The current chapter does not bind the future route shape, query strategy, real-time strategy, or storage placement; those choices remain subject to the implementing decision and to the platform-tenant boundary recorded in this chapter.

**Grounding caveat.** The bc-portal rows rest on prior grounding inherited from Frontend Experience. During this review, `C:\MyProjects\bc-portal` and `C:\MyProjects\BareCount-Customer-Portal` were not readable, so the bc-portal-specific stub claims remain residual risk until the canonical portal path is available to reviewers.

**Governing source.** Frontend Experience; `bc-admin/src/components/TopNavbar.tsx`.

## Anticipated Receiving Surface

DEC-324d9e (Subscription tiers and hosting variants) commits the platform to Stripe billing as the external billing system: the four subscription tiers (Demo, Starter, Professional, Enterprise) are billed externally; bc-core integrates via the Stripe SDK and Stripe webhooks. The webhook receiver itself is not implemented in the readiness baseline. Stripe is the first concrete inbound webhook surface the platform anticipates; it is named here so the architectural commitment is recorded, not so this chapter can enumerate the implementation.

When the Stripe webhook receiver is built, it lives in bc-core under a route guarded by Stripe's HMAC signature verification (`stripe-signature` header; `webhooks.constructEvent` against the signing secret). The endpoint must be exempt from JWT authentication (Stripe is the caller, not a Cognito user) but must remain bounded to a single endpoint with a narrow allowlist of accepted event types. The receiver writes Subscription state changes to the platform database through a governed authoring act, the same way every other platform-side state change is governed; the webhook is the trigger, not the authority for the state change.

A second anticipated inbound surface is the AI service callback. bc-ai may post audit reports back to DevHub in the readiness baseline (one HTTP POST in `bc-ai/app/auditor/reporter.py`); a future surface that posts AI gate verdicts or housekeeping run results to bc-core for tenant-visible notification would land here. The shape is anticipated but not committed by an ADR in the readiness baseline.

No outbound webhook emitter is anticipated by a current ADR. A future tenant-side webhook subscription surface (tenant authors a webhook URL plus signing secret; the platform POSTs metric verdicts or activity events to it) is plausible given the platform's contract architecture, but no decision authorizes it.

**Governing source.** DEC-324d9e; `bc-ai/app/auditor/reporter.py`.

## Architectural Invariants Any Implementation Must Honor

These invariants govern any future notification or webhook implementation regardless of the specific technology, the channel, or the trigger. They are stated here because the absence of code is the cheapest moment to lock the constraints.

| Invariant | What it requires |
|---|---|
| Tenant scope | Notification records that surface tenant data are tenant-scoped; the `notification_log.tenant_id` column is honored as the scoping field. Cross-tenant notifications are not admissible. The platform-scope surface (operator alerts, system-health pages) is the only notification scope that may exclude `tenant_id` |
| Governed authoring | Inbound webhook receivers do not write authoritative state directly; the receiver dispatches to the same governed authoring acts that every other state change uses. A webhook receiver is a trigger surface, not an authority |
| Authentication boundary | JWT authentication remains the request boundary for all routes except inbound webhook endpoints, which authenticate by signature verification against the sender's signing secret. The exemption is per-route and is recorded explicitly; no general bypass of JwtAuthGuard is admissible |
| Idempotency | Inbound webhook receivers are idempotent; the `infrastructure.idempotency_keys` surface or an equivalent is consulted before a side-effecting handler runs. Replay is a foreseeable failure, not an exceptional one |
| Append-only delivery record | The `notification_log` row is the append-only record of a delivery attempt; the `status_code` may transition through `pending` → `sent` → `delivered` or `failed`, but the row is not re-purposed for a different notification, and the row is not deleted on failure |
| Proof emission for governed triggers | Where a notification is triggered by a governed boundary act (a Metric Snapshot crossing a threshold; a Quality Gate failing; an Action Object firing), the trigger preserves the link to the originating act so the notification's authority chain back to Evidence and Lineage is reconstructible |
| Channel-agnostic delivery semantics | The delivery contract (template, recipient, tenant, channel, status) is the same shape for email, in-app, and webhook. The transport differs; the record does not |
| Sender authentication for outbound webhooks | When the platform POSTs to a tenant-configured URL, the payload is HMAC-signed using a tenant-bound secret. The recipient verifies; the platform does not retry signing-mismatch failures |
| Two-database respect | Tenant-bound notification rows live where the tenant scope demands. The current `infrastructure.notification_log` is in the platform database; if per-tenant notification preservation is required for compliance, the column placement is revisited rather than the platform-tenant boundary |

**Governing source.** Foundation; The Authority Model; DEC-1918d0; DEC-771baf.

## Boundaries with Adjacent Chapters

Several adjacent chapters have surfaces that resemble notifications or webhooks but are not part of this chapter's scope.

| Adjacent surface | Where it lives | Why it is not this chapter |
|---|---|---|
| Audit and Activity Logging | Implementation section, queued | Records the immutable platform-side fact. This chapter records selected facts surfaced to humans or external systems; the underlying fact is owned by the audit chapter |
| Quality Gates and Chain Integrity | Operating Model | Gate verdicts may produce notifications, but the gate's authority and the verdict's preservation belong to the gate chapter |
| AI Gates and AI Trust and Verification | AI section, queued | AI activations may produce notifications, but the activation contract and the trust model belong to the AI section |
| Connectors and Readers | Operating Model | Tenant-bound source connectors observe a contracted source; an inbound webhook receiver is an ad-hoc external callback that updates platform state. The two surfaces use the same network primitive (HTTP POST inbound) but are not the same concept; a webhook receiver is not a Reader |
| Tenant Lifecycle and Subscription | Operations section | Owns the Stripe billing artifact; the Stripe webhook receiver, when built, is wired in this chapter but its event taxonomy and the Subscription state machine are owned there |
| Sonner toasts in the frontends | Frontend Experience | Transient UI feedback; not a durable notification record |
| Documentation reader access log | Backend Services (the structured JSONL audit log per DEC-3395bc) | A tenant-visible delivery record of who read what would be a future notification surface; the access log itself is governance, not notification |

**Governing source.** Operating Model; Frontend Experience; outline.md §4.

## Drift Inventory

Per pattern 69, gaps between the design intent recorded above and the current state are surfaced explicitly.

| Gap | Severity | Detail |
|---|---|---|
| The chapter is structurally complete but the surface is empty | Open | A non-stub treatment requires the first delivery to ship. Until then, the chapter records scaffolds, stubs, anticipations, and invariants only |
| `notification_log.template_code` lacks an FK to `email_template.template_code` | Low | DEC-1918d0 Rule 3 violation; the constraint must be added before the first delivery is written |
| `notification_log.tenant_id` is `text`, not a foreign key to `tenant.tenants.tenant_id` | Low | The column shape matches the platform-side text-based tenant identifier convention but lacks the explicit FK |
| `notification_log.recipient_ref` is opaque | Open | The `recipient_ref` column is a free text reference; for an email channel a future implementation may want a structured recipient model (user identifier plus addressed email plus delivery preference reference) rather than a single text field |
| Bell-icon stubs in both frontends route to placeholder pages | Open | bc-portal `/alerts` and `/messages`; bc-admin's bell button has no destination |
| Stripe webhook receiver is anticipated by DEC-324d9e but not implemented | Open | The architectural commitment is in place; the route, the signature verification, and the Subscription state-change handler are all absent |
| Outbound webhook emitter has no current ADR | Open | A tenant-configured webhook subscription surface is plausible but not authorized; no decision exists |
| `main.ts` has no raw-body middleware | Low | A future signature-verifiable receiver requires raw-body availability on its specific route; the global Express adapter does not preserve raw bodies in the readiness baseline |
| Event plumbing is absent | Low | `@nestjs/event-emitter` is not installed; a future implementation that uses domain events to trigger notifications must add the dependency and decide between in-memory dispatch and a queue |
| The `channel_code` enum commits the platform to three channels (`email`, `in_app`, `webhook`) | Low | Future channels (SMS, push, Slack, Teams) require an enum extension; the choice between extending the enum and replacing it with a master table is deferred to the first implementation |

**Governing source.** Architecture; Backend Services; Infrastructure.

## Governing Decisions

| Decision | Title | Notification and webhook impact |
|---|---|---|
| DEC-c06f41 | Spine expansion to eight sections plus home | The Notifications and Webhooks chapter exists as a first-class platform-feature chapter in the reshaped Implementation section per DEC-c06f41, distinct from generic API or service treatment |
| DEC-324d9e | Subscription tiers and hosting variants | Anticipates a Stripe webhook receiver as the inbound integration for billing event ingress; the receiver is named here as an architectural commitment, not as a built feature |
| DEC-1918d0 | Deployment and database architecture; ten normalization rules | Governs the FK and soft-delete shape of the scaffold tables; two drift items are recorded |
| DEC-771baf | Tenant database topology; platform-tenant one-way dependency | Governs where tenant-bound notification rows may live and the asymmetric ownership rule that any future tenant-side notification preservation must respect |
| DEC-3395bc | v3 documentation structure | Governs the adjacent documentation reader access-log boundary only; it does not authorize a notification or webhook surface |

**Governing source.** The Authority Model.

## References

- Foundation: Scope and Non-Negotiability
- The Authority Model
- Operating Model: Overview
- Architecture
- Backend Services
- Internal Modules
- Infrastructure
- API Surface
- Frontend Experience
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-324d9e: Subscription tiers and hosting variants
- DEC-1918d0: Deployment and database architecture
- DEC-771baf: Tenant database topology
- DEC-3395bc: v3 documentation structure
- outline.md §4.3: Implementation
- Decisions: ADR Registry
