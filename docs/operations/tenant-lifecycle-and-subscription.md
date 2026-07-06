---
id: tenant-lifecycle-and-subscription
order: 30
title: "Tenant Lifecycle and Subscription"
status: drafting
authority: authoritative
depends_on: [the-authority-model, the-object-model, tenancy-and-binding, tenant-entitlement-enforcement]
governing_sources:
  - Foundation (scope and non-negotiability)
  - The Authority Model
  - Tenancy and Binding
governing_adrs:
  - DEC-324d9e (Stripe Billing integration; four subscription tiers)
  - DEC-1392ee (Demo tier policy; AWS Shared only, 14-day trial, 30-day data retention)
  - DEC-a67518 (Tenant Onboarding Gate; BYO-DB and BC-Agent prerequisite)
  - DEC-771baf (Tenant database architecture; ownership boundary)
  - DEC-2c79c8 (Per-tenant SQL isolation)
  - DEC-f02230 (Tenant DB schema organization)
  - DEC-4a515b (Four process chains from day one; default catalog scope)
errata_referenced: []
v2_sources: []
---

# Tenant Lifecycle and Subscription

## Scope

This chapter defines the platform-side governance of tenant lifecycle and Subscription. It defines the Subscription record as the platform-scoped artifact that holds tenant entitled scope, the four-tier tier model and the four hosting variants paired with it, the catalog entitlement and operational envelope recorded on the Subscription, the Onboarding Record that gates tenant creation for hosting variants requiring real-world prerequisite work, the Subscription state machine that governs lifecycle transitions, the tenant lifecycle acts that produce and modify these records, and the external billing integration that handles payment without entering platform runtime.

This chapter does not define the contract-execution runtime acts that consult Subscription state at admission, evaluation, and action emission; those are governed by Tenant Entitlement Enforcement in Operating Model. This chapter does not redefine tenant identity or the tenant ownership boundary (Tenancy and Binding), the Authority Model's governance ladder (The Authority Model), the relational storage layout for Subscription records (Data Model and Schema), or the API surface for Subscription administration (API Surface).

This chapter is the authority owner for Subscription as an artifact. Tenant Entitlement Enforcement consumes the Subscription record read-only at named runtime surfaces; the Subscription record is authored, transitioned, and terminated under the acts defined here.

**Governing source.** Foundation; The Authority Model; Tenancy and Binding.

## Subscription Artifact

Subscription is a platform-scoped governance record. It is not authoritative state in the sense of the four progression objects (Source Object, Canonical Object, Metric Snapshot, Action Object); it is platform-side governance metadata about tenant entitled scope.

| Property | Operational form |
|---|---|
| Scope | Platform-scoped. The record lives in the platform database. The tenant does not author its own Subscription. |
| Cardinality | One active Subscription per tenant at any time. Subscription succession transitions the prior record to a terminal state and creates the new record; both records remain readable as historical governance. |
| Authoring authority | Subscription records are authored by platform-side governance acts under the Authority Model's discipline. Self-service tier acts (signup, tier change, suspension, resumption) are recorded as platform-governed events; sales-led acts (Enterprise creation, Onboarding Record activation) are recorded the same way. |
| Reference grain | A tenant identity record references one Subscription record. Operating Model acts that consult Subscription state read through the tenant identity. |
| Lifecycle | Active, suspended, or terminated. Transitions are governed acts; the runtime reads the state but does not author transitions. |

The Subscription record holds five governed bodies of content: tier and hosting variant, catalog entitlement, operational envelope, lifecycle state, and references to associated Onboarding Records and external billing identifiers. The bodies are described in the sections that follow.

**Governing source.** Foundation; The Authority Model; Tenancy and Binding; DEC-771baf.

## Tier and Hosting Variant

Per DEC-324d9e, the platform recognizes four subscription tiers. Per DEC-1392ee and the platform's infrastructure governance, four hosting variants exist. Tier and hosting variant are paired on the Subscription record; the tier constrains which hosting variants are admissible.

| Tier | Hosting variants admissible | Activation path | Governing source |
|---|---|---|---|
| Demo | AWS Shared only | Self-service signup; auto-suspend at Day 14; data retained 30 days then purged | DEC-1392ee |
| Starter | AWS Shared | Self-service via external billing platform | DEC-324d9e |
| Professional | AWS Shared or AWS Separate | Self-service or sales-assisted via external billing platform | DEC-324d9e |
| Enterprise | BYO-DB or BC-Agent | Sales-led with invoice billing; Onboarding Record prerequisite | DEC-324d9e; DEC-a67518 |

| Hosting variant | Tenant database placement | Activation prerequisites |
|---|---|---|
| AWS Shared | Auto-provisioned tenant database on shared infrastructure under the platform's AWS account | None; lightweight provisioning at signup |
| AWS Separate | Per-tenant dedicated database on platform-managed infrastructure under the platform's AWS account | None at the tenant lifecycle level; infrastructure provisioning is a deployment concern |
| BYO-DB | Tenant-managed database in the customer's own infrastructure, accessed by the platform under negotiated connectivity | Onboarding Record in `ready` state per DEC-a67518 |
| BC-Agent | Local agent runtime executed in the customer's environment, with data movement governed by the agent | Onboarding Record in `ready` state per DEC-a67518 |

The hosting variant on the Subscription record selects the tenant database architecture for the tenant. Tenant database scope, ownership, and isolation remain governed by Tenancy and Binding (DEC-771baf, DEC-2c79c8, DEC-f02230). The Subscription does not redefine the tenant ownership boundary; it selects the infrastructure shape under which the boundary is realized.

A Subscription record carrying a tier and hosting variant pair that the tier does not admit is rejected at the authoring act. A tier change that requires a hosting variant the prior tier did not admit may require an associated infrastructure transition; that transition is a deployment concern outside the scope of this chapter.

**Governing source.** DEC-324d9e; DEC-1392ee; DEC-a67518; Tenancy and Binding.

## Catalog Entitlement

The Subscription record's catalog entitlement records which subset of platform-cataloged content the tenant may operate against. The catalog itself is governed by Sources and the Catalog and Metric Catalog; this chapter records the entitlement as a reference set against platform-cataloged identifiers.

| Entitlement axis | What it admits | Default for new Subscription |
|---|---|---|
| Process chain entitlement | The set of process chains the tenant may operate against. Per DEC-4a515b, the platform delivers four process chains from day one (P2P, O2C, R2R, Plan-to-Produce); a Subscription names the subset the tenant has entitled. | Tier-default subset; for Demo and Starter the subset is platform-declared; for Professional and Enterprise the subset is recorded explicitly per Subscription. |
| Function and subfunction entitlement | The subset of functions and subfunctions within entitled process chains the tenant may operate against. | Inherited from process chain entitlement unless explicit narrowing is recorded. |
| Metric entitlement | The subset of platform-registered metrics the tenant may evaluate. Where a tenant has entitled a function or subfunction, metric entitlement may be expressed as full inclusion or as a named subset. | Full inclusion within entitled subfunctions unless explicit narrowing is recorded. |
| Source System entitlement | The subset of platform-cataloged Source Systems the tenant may register Connections against. | Tier-default subset; explicit per-Subscription recording for Professional and Enterprise. |

Catalog entitlement is a reference set against platform-cataloged identifiers. Entitlement to a non-existent catalog entry is not admissible; the platform Source Catalog and Metric Catalog are the authoritative sources of admissible identifiers.

Catalog entitlement is consulted at the runtime enforcement surfaces governed by Tenant Entitlement Enforcement (Connection registration, admission invocation, metric evaluation invocation, catalog browse). This chapter authors the entitlement; Operating Model consumes it.

**Governing source.** DEC-4a515b; Tenancy and Binding.

## Operational Envelope

The operational envelope records the runtime limits that apply on the tenant's behalf. The envelope is recorded on the Subscription record. Tier sets default values; explicit per-Subscription variation is admissible within tier-permitted ranges.

| Envelope dimension | What it bounds | Tier default behavior |
|---|---|---|
| Admission rate limit | Per-Connection admission invocation rate over a declared window | Tier-default value; explicit variation admissible within tier-permitted range |
| Concurrent admission cap | Number of admission invocations that may be active concurrently for the tenant | Tier-default value; explicit variation admissible within tier-permitted range |
| Evaluation rate limit | Metric evaluation invocation rate over a declared window | Tier-default value |
| Action emission cap | Maximum number of Action Objects emitted per declared window | Tier-default value |
| Catalog browse rate limit | Tenant-facing catalog API request rate over a declared window | Tier-default value |
| Retention floor | Minimum retention duration for proof artifacts; the tenant proof-retention policy may set durations at or above this floor, not below | Tier-default value; Compliance treatment may impose additional minimums |

The envelope's per-tier default values and the per-tier variation ranges are governed values held in the platform's tier-policy registry. A Subscription record carrying envelope values outside the tier-permitted range is rejected at the authoring act.

The envelope is consulted at the runtime enforcement surfaces governed by Tenant Entitlement Enforcement. The envelope is not consulted by external billing; billing tracks usage signals through its own integration without entering runtime decisions.

**Governing source.** DEC-324d9e; Tenancy and Binding.

## Onboarding Record

Per DEC-a67518, hosting variants that require real-world preparation (BYO-DB and BC-Agent) require a completed Onboarding Record before tenant creation is admitted. The Onboarding Record is the prerequisite gate.

**Purpose.** The Onboarding Record records the readiness of a tenant for activation under a hosting variant whose preparation cannot be completed by the platform alone. It tracks tier-specific checklist items (sales agreement, infrastructure readiness, connectivity verification, technical sign-off) and records the status that the tenant-creation act consults.

**Scope.** Onboarding Records apply to BYO-DB and BC-Agent hosting variants. AWS Shared and AWS Separate are self-service variants; tenant creation under those variants does not require an Onboarding Record per DEC-a67518.

**Lifecycle states.** The Onboarding Record progresses through declared states: `initiated`, `in_progress`, `ready`, `activated`, `cancelled`. Tenant creation against BYO-DB or BC-Agent admits only when the linked Onboarding Record is in `ready`. Activation moves the record to `activated` and is terminal under successful activation. A cancelled record cannot be re-used; a new Onboarding Record is required for a subsequent tenant-creation attempt.

**Cardinality.** An Onboarding Record is associated with at most one tenant. A tenant created under an `activated` Onboarding Record retains the reference for audit; if the tenant is later terminated, the Onboarding Record remains in `activated` state as historical governance.

**Constraints.**

- The Onboarding Record does not authorize tenant data movement before the tenant exists. It records prerequisite readiness only.
- The Onboarding Record's `ready` state is not transitive across tiers. A record prepared for BYO-DB does not satisfy BC-Agent readiness.
- The Onboarding Record does not bypass Subscription tier rules. A tenant created from a `ready` Onboarding Record still consults the Subscription tier and hosting variant constraints.
- The Onboarding Record is not an entitlement record. Entitlement remains the Subscription's responsibility.

**Failure modes.** Tenant creation against BYO-DB or BC-Agent without a linked `ready` Onboarding Record is rejected. An attempt to re-use an `activated` or `cancelled` Onboarding Record for a second tenant-creation is rejected. An Onboarding Record whose checklist is incomplete cannot transition to `ready`.

**Governing source.** DEC-a67518; Tenancy and Binding.

## Subscription State Machine

The Subscription lifecycle state set is closed: `active`, `suspended`, `terminated`. Transitions are governed acts under the Authority Model's discipline.

| Transition | From | To | Trigger | Reversible |
|---|---|---|---|---|
| Activation | (none) | `active` | Tenant creation act with an admitted tier and hosting variant pair, plus an Onboarding Record in `ready` where required | Reversible by suspension or termination |
| Suspension | `active` | `suspended` | Governance act (administrative, billing-driven, or compliance-driven) | Reversible by resumption |
| Resumption | `suspended` | `active` | Governance act recording the resolution of the cause for suspension | Reversible by suspension |
| Termination | `active` or `suspended` | `terminated` | Governance act under the platform's termination discipline | Not reversible; a terminated Subscription does not return to `active` |

Suspended and terminated states reject contract execution at every Tenant Entitlement Enforcement surface. The runtime does not author lifecycle transitions; transitions are platform-side governance acts that produce updated Subscription records that the runtime then reads.

Demo tier auto-suspension is a special case of the suspension transition, governed by DEC-1392ee. The transition is triggered by the Day 14 platform-governed act; the resulting suspended state is identical in runtime effect to any other suspended state. Demo conversion to a paid tier is a tier-change act on the suspended record that activates the Subscription as a Starter or higher tier.

**Constraints.**

- A Subscription record cannot transition between non-adjacent states in one act. Activation comes from no prior state; resumption comes only from `suspended`; termination is terminal.
- A terminated Subscription record is not modified after termination. Subsequent Subscription authoring for the same tenant produces a new Subscription record with its own identity.
- Lifecycle transitions are recorded as governance events on the Subscription record. The transition history is preserved for audit.

**Governing source.** DEC-324d9e; DEC-1392ee; The Authority Model.

## Tenant Lifecycle Acts

The tenant lifecycle is the set of platform-governed acts that produce, modify, and terminate the records this chapter defines. Each act has a recorded outcome under the Authority Model's discipline.

| Act | Inputs | Effects | Governing source |
|---|---|---|---|
| Tenant creation | Tier; hosting variant; Onboarding Record (where required); external billing reference (where applicable) | Creates the tenant identity record per Tenancy and Binding; creates the Subscription record in `active` state; provisions the tenant database under the chosen hosting variant; records the creation in the tenant-side change log | DEC-324d9e; DEC-1392ee; DEC-a67518; Tenancy and Binding |
| Tier change | Existing Subscription; target tier; hosting variant for the target tier | Updates the Subscription record's tier and hosting variant fields; resets envelope defaults to the new tier's values where the prior values fall outside the new tier's range; records the change as a governance event | DEC-324d9e |
| Subscription suspension | Existing `active` Subscription; cause (administrative, billing-driven, compliance-driven, demo auto-suspension) | Transitions the Subscription to `suspended` state; preserves all entitlement and envelope content unchanged; records the cause and transition timestamp | DEC-324d9e; DEC-1392ee |
| Subscription resumption | Existing `suspended` Subscription; resolution of the cause for suspension | Transitions the Subscription back to `active` state; records the resolution and transition timestamp | DEC-324d9e |
| Subscription termination | Existing `active` or `suspended` Subscription; cause (cancellation, non-payment, compliance termination) | Transitions the Subscription to `terminated` state; records the cause and transition timestamp; triggers tenant-side data retention treatment per the tenant proof-retention policy | DEC-324d9e; Tenancy and Binding |
| Onboarding Record creation | Hosting variant requiring Onboarding (BYO-DB or BC-Agent); tenant identifying detail | Creates the Onboarding Record in `initiated` state with the tier-specific checklist | DEC-a67518 |
| Onboarding Record state transition | Existing Onboarding Record; target state | Transitions the record per the lifecycle states section above; records the transition as a governance event | DEC-a67518 |
| Catalog entitlement update | Existing Subscription; revised entitlement reference set | Updates the Subscription record's catalog entitlement fields; records the change as a governance event; takes effect for subsequent runtime consultations | This chapter; Sources and the Catalog; Metric Catalog |
| Operational envelope update | Existing Subscription; revised envelope values | Updates the Subscription record's envelope fields, subject to tier-permitted ranges; records the change as a governance event | This chapter |

Tenant lifecycle acts are platform-side governance acts. They are not Operating Model acts in the contract-execution sense; they do not produce Source Objects, Canonical Objects, Metric Snapshots, or Action Objects. They produce updated Subscription records and updated Onboarding Records that runtime acts subsequently read.

**Governing source.** The Authority Model; DEC-324d9e; DEC-1392ee; DEC-a67518; Tenancy and Binding.

## External Billing Integration

Per DEC-324d9e, billing, payment instruments, and invoicing are governed by an external billing platform. Payment data and payment events do not enter the contract-execution runtime.

| Property | Operational form |
|---|---|
| Boundary | The external billing platform handles payment collection, recurring billing, self-service customer portal, and invoicing. It does not produce Subscription records; it produces billing events that platform-side acts consume to author Subscription state changes. |
| Reference | The Subscription record carries an external billing reference identifier so that platform-side acts can correlate Subscription state changes with billing events for audit. The reference is opaque to the runtime; it is governance metadata for reconciliation purposes. |
| Triggered transitions | Billing events (payment failure, subscription cancellation, plan change) are observed by platform-side governance acts that may trigger Subscription suspension, termination, or tier change. The transition itself is a platform-governed act recorded on the Subscription; the billing event is the cause, not the act. |
| No payment data in the platform | Card data, payment instrument metadata, and invoicing detail do not enter the platform database. The external billing platform is the merchant processor and the system of record for those records. |

The external billing platform is integrated through an SDK and a webhook endpoint at the platform-side governance surface. The integration is administrative; it is not part of the contract-execution runtime and does not enter the chapters in Operating Model.

**Governing source.** DEC-324d9e.

## Boundary: What Tenant Lifecycle and Subscription Is Not

Three concepts have been confused with this chapter's scope in earlier readings. The boundary makes each distinction explicit.

| Concept | Relation to this chapter |
|---|---|
| Contract-execution runtime consumption of Subscription | Tenant Entitlement Enforcement in Operating Model defines how runtime acts consult Subscription state at named enforcement surfaces. This chapter authors the artifact; that chapter consumes it. The two chapters interlock and must remain consistent, but they are not the same chapter. |
| Tenant identity registration | Tenancy and Binding defines tenant identity as a platform-scoped record and the tenant ownership boundary per DEC-771baf. This chapter references the tenant identity but does not redefine it. Tenant identity is the anchor; Subscription is one of several artifacts associated with that identity. |
| Authoritative-state production | The four contract-execution boundary acts produce authoritative state (Source Objects, Canonical Objects, Metric Snapshots, Action Objects). This chapter does not produce authoritative state; it produces governance records that gate, scope, and bound the conditions under which authoritative-state production may proceed. |

The boundaries are uniform. A Subscription record that contains authoritative-state content is a category error. A runtime act that authors Subscription state from inside the contract-execution runtime is a category error. A tenant lifecycle act that produces a Source Object or other authoritative-state artifact is a category error.

**Governing source.** Foundation; The Object Model; Tenant Entitlement Enforcement.

## Constraints

The constraints below apply uniformly to Subscription records, Onboarding Records, and the tenant lifecycle acts that produce them.

| Constraint | Operational form |
|---|---|
| Platform-scoped artifact | The Subscription record and the Onboarding Record live in the platform database, not in the tenant database. The tenant does not author either record. |
| One active Subscription per tenant | A tenant identity references at most one active Subscription at any time. Subscription succession transitions the prior record to a terminal state and creates a new record; both remain readable. |
| Authority discipline | Tenant lifecycle acts are governed under the Authority Model. Self-service acts are governed under the same discipline as sales-led acts; the difference is the actor, not the governance surface. |
| Closed lifecycle state set | Subscription state is `active`, `suspended`, or `terminated`. Onboarding Record state is `initiated`, `in_progress`, `ready`, `activated`, or `cancelled`. No other states are admissible. |
| Tier-permitted ranges bound the envelope | Operational envelope values must satisfy the tier's permitted range. Variation outside the range is rejected at the authoring act. |
| Catalog entitlement references the platform catalog | Entitlement applies to platform-cataloged identifiers only. Tenant Z-tables, Z-fields, and tenant-extension content are governed by Tenant Extensions and Overrides, not by Subscription entitlement. |
| External billing is out of platform runtime | Payment data and billing events do not enter the contract-execution runtime. The Subscription record observes billing-driven state changes through governance acts only. |
| Termination is terminal | A terminated Subscription record is not modified after termination. A new Subscription for the same tenant produces a new Subscription record with its own identity. |

**Governing source.** The Authority Model; DEC-324d9e; DEC-771baf; Tenancy and Binding.

## Drift Inventory

| Gap | Current state | Risk |
| --- | --- | --- |
| Dedicated subscription lifecycle service not located | Readable bc-core source exposes package/catalog and tenant registry surfaces, but not a full subscription state service. | Lifecycle semantics can become procedural unless the service boundary is implemented. |
| Onboarding record persistence not located | The chapter describes the operating object; readable source did not show a durable onboarding-record table or service. | Sales-to-tenant traceability remains partly manual. |
| External billing integration not active | Stripe and invoicing remain integration boundaries, not active governors of tenant authority. | Commercial state can diverge from platform entitlement state. |
| Tier envelope registry not located | Tier and hosting semantics are documented, but a single runtime envelope registry was not found. | Operators may enforce limits by convention rather than source-backed policy. |
## Failure Modes

Failures at this boundary occur at the authoring act that produces or modifies the record. Failures are recorded as governance events; they do not produce Subscription records in the failed state.

| Failure | Detection point | Treatment |
|---|---|---|
| Tier and hosting variant inconsistent | Tenant creation or tier change | Rejected at the authoring act. The Subscription is not persisted in the inconsistent state. |
| Tenant creation against BYO-DB or BC-Agent without `ready` Onboarding Record | Tenant creation | Rejected. Tenant creation is held until the Onboarding Record reaches `ready`. |
| Catalog entitlement references a non-existent catalog entry | Subscription authoring or update | Rejected. Entitlement to a non-existent platform-cataloged identifier is not admissible. |
| Operational envelope value outside the tier-permitted range | Subscription authoring or update | Rejected. The envelope variation is outside the tier's permitted range. |
| Subscription state transition between non-adjacent states | Subscription state-change act | Rejected. Activation, suspension, resumption, and termination follow the state machine's adjacency rules. |
| Re-use of `activated` or `cancelled` Onboarding Record for a second tenant creation | Tenant creation | Rejected. A new Onboarding Record is required. |
| Tenant identity without a referenced Subscription record | Detected at runtime by Tenant Entitlement Enforcement | Operating Model treats this as equivalent to a terminated state and rejects contract-execution acts. The platform-side governance gap is recorded for remediation. |
| Demo tier auto-suspension reached | Day 14 platform-governed act | Subscription transitions to `suspended`; data is retained 30 days per DEC-1392ee; runtime invocations are rejected during the retention window per Tenant Entitlement Enforcement. |
| Billing-driven suspension or termination | Platform-side governance act consuming a billing event | Subscription transitions per the billing event's classification. The billing event is the cause; the platform-governed act is the transition. |
| Tier change requiring infrastructure transition that has not completed | Tier change | Held. The Subscription update is not persisted until the infrastructure transition is recorded as complete. |

Failure modes are recorded as governance events on the Subscription record where the failure relates to that record, and on the Onboarding Record where the failure relates to that record. The platform does not silently absorb a rejected authoring act; rejection is a governance outcome with audit trail.

**Governing source.** DEC-324d9e; DEC-1392ee; DEC-a67518; The Authority Model.

## Governing Decisions

| Decision | Operational effect |
| --- | --- |
| DEC-324d9e | Customer notification remains queued context; lifecycle docs must not imply active webhook or message delivery. |
| DEC-1392ee | Keeps lifecycle authority attached to tenant entitlement rather than ad hoc commercial state. |
| DEC-a67518 | Bounds lifecycle notification language to operational intent until notification surfaces are active. |
| DEC-771baf | Keeps onboarding and lifecycle gates explicit rather than hidden in scripts. |
| DEC-2c79c8 | Defines the managed self-hosting variant considered by tier and hosting posture. |
| DEC-f02230 | Separates platform-managed deployment posture from tenant commercial lifecycle. |
| DEC-4a515b | Preserves the four default chain entitlement as catalog posture without using it as billing implementation. |
## References

- Foundation: Scope and Non-Negotiability
- The Object Model: The Object Model
- The Authority Model: The Authority Model
- Sources and the Catalog: Sources and the Catalog
- Metric Catalog: Metric Catalog
- Tenancy and Binding: Tenancy and Binding
- Tenant Extensions and Overrides: Tenant Extensions and Overrides
- Tenant Entitlement Enforcement: Tenant Entitlement Enforcement
- DEC-324d9e: Stripe Billing integration; four subscription tiers
- DEC-1392ee: Demo tier policy; AWS Shared only, 14-day trial, 30-day data retention
- DEC-a67518: Tenant Onboarding Gate; BYO-DB and BC-Agent prerequisite
- DEC-771baf: Tenant database architecture and one-way dependency
- DEC-4a515b: Four process chains from day one
- Decisions: ADR Registry



