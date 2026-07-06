---
id: tenant-entitlement-enforcement
order: 14.7
title: "Tenant Entitlement Enforcement"
status: drafting
authority: authoritative
depends_on: [sources-and-the-catalog, connectors-and-readers, admission-and-observation, canonical-evaluation, metric-evaluation, action-evaluation, metric-catalog, tenancy-and-binding, tenant-extensions-and-overrides]
governing_sources:
  - Foundation (scope and non-negotiability)
  - Sources and the Catalog
  - Metric Catalog
  - Tenancy and Binding
governing_adrs:
  - DEC-324d9e (Stripe Billing integration; four subscription tiers)
  - DEC-1392ee (Demo tier policy; 14-day auto-suspension)
  - DEC-4a515b (Four process chains from day one; catalog scope)
errata_referenced: []
v2_sources: []
---

# Tenant Entitlement Enforcement

## Scope

This chapter defines how contract-execution acts consult tenant entitlement state at runtime. It defines the Subscription record as a runtime input, the lifecycle states that gate contract execution, the catalog entitlement axes that scope a tenant's runtime reach, the operational envelope dimensions that the runtime applies on the tenant's behalf, the enforcement surfaces in contract execution at which entitlement is consulted, the pre-emission re-check requirement that prevents an in-flight act from emitting authoritative state under a state change, and the implementation-status declaration that records honestly whether a named enforcement surface is wired in the current platform release.

This chapter does not redefine the contract grammar, the runtime acts at the four boundaries (Admission and Observation through Canonical Evaluation, Metric Evaluation, and Action Evaluation), or the catalog (Sources and the Catalog and Metric Catalog). The Subscription record's tier categorization, hosting variant selection, billing integration, demo tier policy mechanism, Onboarding Record gate, and lifecycle state machine are commercial and operational concerns governed by platform tenant-lifecycle authoring acts described elsewhere; this chapter consumes the lifecycle state and the entitlement scope that those acts produce, without redefining the acts themselves.

This chapter is symmetric with Tenant Extensions and Overrides. Tenant Extensions and Overrides describes how contract execution consults tenant-side governance records that bound contract variation. This chapter describes how contract execution consults platform-side governance records that bound tenant entitled scope.

**Governing source.** Foundation; Tenancy and Binding; Sources and the Catalog; Metric Catalog.

## Subscription as Runtime Input

The Subscription is the platform-scoped governance record that holds tenant entitlement state. Each active tenant identity references exactly one Subscription record at a time. Contract execution consults the record as a read-only input at named enforcement surfaces; contract execution does not modify Subscription state.

The runtime-relevant properties of the Subscription record are defined here. Properties that are not runtime-relevant (tier categorization detail, hosting variant selection, billing integration, demo tier policy mechanism, Onboarding Record gate, the state machine that governs lifecycle transitions) are commercial and operational concerns governed by platform tenant-lifecycle authoring acts described elsewhere.

| Runtime-relevant property | Definition | Effect at runtime |
|---|---|---|
| Lifecycle state | Active, suspended, or terminated. The state set is closed; no other state is admissible at runtime. | Active permits contract execution subject to surface checks. Suspended and terminated reject contract execution at every consulting surface and at the pre-emission re-check. |
| Catalog entitlement | Reference set listing entitled process chains, functions, subfunctions, metrics, and Source Systems. References are to platform-cataloged identifiers per Sources and the Catalog and Metric Catalog. | Connection registration, admission invocation, metric evaluation invocation, and catalog browse consult the relevant entitlement axis. A non-entitled identifier rejects the act. |
| Operational envelope | Per-tenant runtime limits including admission rate limit, concurrent admission cap, evaluation rate limit, action emission cap, catalog browse rate limit, and proof-retention floor. The envelope is the authoritative source consulted at runtime; tier defaults influence the values held on the record but the record is what runtime reads. | Each surface that consumes an envelope dimension applies the rule per the consuming chapter's discipline. |

Read-only consumption is uniform: a contract-execution act does not write to the Subscription record, does not infer state from absence, and does not synthesize a default when the record is missing. A tenant identity without a referenced Subscription record cannot proceed past Connection registration; this is the same outcome as a terminated state.

**Governing source.** Foundation; Sources and the Catalog; Metric Catalog; Tenancy and Binding.

## Enforcement Surfaces in Contract Execution

Seven enforcement surfaces in contract execution consult the Subscription record. Each surface is a precondition check applied by the act that owns the surface, not a separate runtime layer.

| Surface | Subscription dimension consulted | Owning chapter or surface |
|---|---|---|
| Connection registration | Source System entitlement; lifecycle state | Connectors and Readers |
| Admission invocation | Source System entitlement; admission rate limit; concurrent admission cap; lifecycle state | Admission and Observation |
| Canonical evaluation invocation | Lifecycle state | Canonical Evaluation |
| Metric evaluation invocation | Metric entitlement; evaluation rate limit; lifecycle state | Metric Evaluation |
| Action emission | Action emission cap; lifecycle state | Action Evaluation |
| Catalog browse (tenant-facing) | Process chain, function, subfunction, metric, Source System entitlement; browse rate limit; lifecycle state | Tenant-facing browse surface |
| Tenant proof-retention authoring | Retention floor; lifecycle state | Tenancy and Binding (Proof Retention Policy) |

Each surface is owned by the chapter that defines the relevant act. This chapter names the surfaces; the consuming chapter governs the act and applies the precondition. A surface that does not consult the Subscription record applies no entitlement check; the implementation-status section below records the platform's readiness-baseline position.

Canonical evaluation consults lifecycle state only. Catalog entitlement is enforced at admission, so canonical evaluation cannot read Source Objects that admission did not produce; the catalog-entitlement check inherits transitively from admission. No envelope dimension is declared at the canonical evaluation surface in the readiness baseline.

The order of the precondition check is fixed within each act: the Subscription consultation occurs before the act produces authoritative state. A rejected precondition does not produce a Source Object, Canonical Object, Metric Snapshot, or Action Object.

**Governing source.** Connectors and Readers; Admission and Observation; Canonical Evaluation; Metric Evaluation; Action Evaluation; Tenancy and Binding.

## Envelope Dimensions Consumed at Runtime

The operational envelope on the Subscription record declares runtime limits. Each limit is consumed at a specific contract-execution surface.

| Envelope dimension | Surface that consumes it | Effect when the limit is reached |
|---|---|---|
| Admission rate limit | Admission invocation | Treatment per the consuming chapter (rejected, queued, or held until the declared window resets) |
| Concurrent admission cap | Admission invocation | Invocation is held until in-flight count drops below the cap, or rejected per the consuming chapter |
| Evaluation rate limit | Metric evaluation invocation | Treatment per the consuming chapter |
| Action emission cap | Action emission | Action emission is held per the consuming chapter until the declared window resets |
| Catalog browse rate limit | Catalog browse responses | The tenant-facing browse surface returns the appropriate rate-limit response per its discipline |
| Retention floor | Tenant proof-retention authoring | Authoring of a retention duration below the floor is rejected per Tenancy and Binding |

The envelope dimensions consumed at runtime do not include billing-related limits. Billing limits, where they exist, are governed by the external billing platform per DEC-324d9e and do not enter the contract-execution runtime.

A surface that names an envelope dimension but does not consult the Subscription record at the act applies no limit at that surface. This is the implementation-status concern recorded below.

**Governing source.** Connectors and Readers; Admission and Observation; Metric Evaluation; Action Evaluation; Tenancy and Binding.

## Lifecycle State Gating

The Subscription lifecycle state gates whether contract execution may proceed at all for the tenant. State transitions are governed by platform tenant-lifecycle authoring acts described elsewhere; this section records the runtime effect of each state.

| Lifecycle state | Effect on contract execution |
|---|---|
| Active | Contract execution proceeds subject to surface-level entitlement and envelope checks. |
| Suspended | New invocations are rejected at every enforcement surface that consults the record. In-flight invocations re-check lifecycle state at the pre-emission gate (defined below) and do not emit authoritative state if the state has flipped to suspended. |
| Terminated | New invocations are rejected. In-flight invocations re-check lifecycle state at the pre-emission gate and do not emit authoritative state if the state has flipped to terminated. Existing tenant-scoped authoritative state already emitted is not retroactively modified by termination; retention treatment is governed by Tenancy and Binding (Proof Retention Policy). |

Contract-execution acts treat the lifecycle state as a read at two points: at the act's precondition check, and at the pre-emission gate. A state change between the two reads is honored: the precondition check may pass, then the pre-emission gate may reject the same act if the state has flipped mid-flight.

### Pre-Emission Re-Check

Every contract-execution act re-reads the Subscription lifecycle state immediately before emitting authoritative state. The re-check prevents an in-flight act from producing a Source Object, Canonical Object, Metric Snapshot, or Action Object after the tenant has been suspended or terminated mid-flight.

| Property | Rule |
|---|---|
| Where applied | At every contract-execution act that emits authoritative state: admission, canonical evaluation, metric evaluation, action emission. |
| What is checked | The Subscription lifecycle state read at the moment immediately before authoritative-state emission. |
| Effect of a state flip to suspended or terminated | The act does not emit. The relevant Run record records a lifecycle-rejection outcome with the prior precondition outcome and the post-flip rejection outcome both preserved. Evidence is recorded for the rejected act per the proof discipline of the relevant chapter. |
| Effect on in-flight admission batch | Admission proceeds through validation but does not emit Source Objects when the pre-emission re-check rejects. The batch outcome is recorded as lifecycle-rejected, not as silently empty. |
| Relationship to precondition check | The pre-emission re-check is additional to the precondition check, not a replacement. Both reads must succeed for emission to occur. |

The re-check is a runtime invariant that protects against the time gap between precondition and emission. It applies regardless of envelope wiring or surface-level entitlement wiring; lifecycle state is honored at the emission gate as a matter of platform discipline.

Demo tier auto-suspension per DEC-1392ee is a special case of the suspended state. The runtime treats an auto-suspended demo tenant identically to any other suspended tenant at both the precondition check and the pre-emission re-check.

**Governing source.** Foundation; Tenancy and Binding; DEC-1392ee.

## Wiring Status

This section declares honestly what contract-execution surfaces consult the Subscription record in the current platform release. The architectural definition above is forward-looking; the table below is the platform's current operational position.

| Surface | Subscription dimension declared above | Wired in current release |
|---|---|---|
| Connection registration | Source System entitlement; lifecycle state | Not yet wired |
| Admission invocation | Source System entitlement; admission rate limit; concurrent admission cap; lifecycle state | Not yet wired |
| Canonical evaluation invocation | Lifecycle state | Not yet wired |
| Metric evaluation invocation | Metric entitlement; evaluation rate limit; lifecycle state | Not yet wired |
| Action emission | Action emission cap; lifecycle state | Not yet wired |
| Catalog browse (tenant-facing) | Process chain, function, subfunction, metric, Source System entitlement; browse rate limit; lifecycle state | Not yet wired |
| Tenant proof-retention authoring | Retention floor; lifecycle state | Not yet wired |
| Pre-emission re-check (all acts) | Lifecycle state | Not yet wired |

The platform does not represent any of these surfaces as enforced. Authoring acts that produce Subscription records and update lifecycle state may proceed as governed by tenant-lifecycle authoring elsewhere, but contract-execution acts in the current release do not consult those records as preconditions or at pre-emission.

The architectural definition in this chapter is the target. Each surface above is a tracked governance gap until it is wired. As wiring lands, the row's status flips to "Wired" with a release reference. A surface that has been wired in some environments and not others is recorded with the environment scope explicit; a surface is not represented as wired platform-wide until it is.

This honest declaration is platform-level. The table above is updated as a chapter-amendment governance act when status changes; consuming chapters do not silently override the platform-level status.

**Governing source.** Foundation.

## Constraints

Constraints below apply uniformly to entitlement enforcement at the contract-execution boundary.

| Constraint | Operational form |
|---|---|
| Subscription is read-only at runtime | Contract-execution acts consult the Subscription record. They do not modify it. State changes are governed by platform tenant-lifecycle authoring acts described elsewhere. |
| Enforcement is at the precondition and the pre-emission re-check | Subscription consultation occurs before the act produces authoritative state and again immediately before emission. A rejected precondition or a rejected re-check does not produce a Source Object, Canonical Object, Metric Snapshot, or Action Object. |
| Catalog entitlement references the platform catalog, not tenant content | Entitlement applies to platform-cataloged identifiers (Source Systems, metrics, process chains, functions, subfunctions). It does not apply to tenant Z-tables, Z-fields, or tenant-extension content; those are governed by Tenant Extensions and Overrides under the bound contract version. |
| Envelope limits are tier-influenced, not tier-derived | The envelope fields on the Subscription record are the authoritative source consulted at runtime. Tier defaults influence the values held on the record; the record itself is what the runtime reads. |
| Lifecycle state gates execution as a whole | A suspended or terminated state suppresses every consulting surface and every pre-emission re-check. Surface-level entitlement checks are not consulted when the lifecycle state already rejects execution. |
| Billing is external | Per DEC-324d9e, billing data and payment events do not enter contract-execution runtime. Billing-driven Subscription state changes are observed by contract execution only through the Subscription lifecycle state field. |

**Governing source.** Tenant Extensions and Overrides; Tenancy and Binding; DEC-324d9e.

## Failure Modes

Failures at the entitlement enforcement boundary occur at the surface that consults the Subscription record. Failure treatment is uniform.

| Failure | Detection point | Treatment |
|---|---|---|
| Connection registration against a non-entitled Source System | Connection registration | Rejected. The Connection is not persisted. |
| Admission invocation against a non-entitled Source System | Admission act precondition | Rejected. The Source Object emission does not occur. |
| Canonical evaluation invocation against a suspended or terminated tenant | Canonical evaluation act precondition | Rejected. The Canonical Object emission does not occur. |
| Metric evaluation invocation against a non-entitled metric | Metric evaluation act precondition | Rejected. The Metric Snapshot emission does not occur. |
| Action emission cap reached | Action emission | Held per the Action Evaluation chapter's discipline until the declared window resets. |
| Admission rate limit or concurrent admission cap reached | Admission act precondition | Treatment per Admission and Observation (rejected, queued, or held). |
| Catalog browse rate limit reached | Tenant-facing browse surface | Rate-limit response per the consuming surface's discipline. |
| Tenant proof-retention authoring below the retention floor | Tenancy and Binding (Proof Retention Policy) | Rejected at the authoring act. |
| Subscription state flipped to suspended or terminated mid-flight | Pre-emission re-check at any contract-execution act | Emission rejected. Authoritative state is not produced. The Run record records both the prior precondition outcome and the post-flip rejection outcome. |
| Subscription suspended or terminated | Any enforcement surface or pre-emission re-check | New invocations rejected. In-flight invocations are held through validation but do not emit if the pre-emission re-check rejects. |
| Tenant identity without a referenced Subscription record | Connection registration | Rejected at the same outcome as a terminated state. Subsequent contract-execution acts cannot proceed without a Subscription reference. |
| Surface declared as enforcement surface but not wired in current release | Tracked governance gap recorded in the Wiring Status section | The architectural definition remains authoritative; the platform does not represent the surface as enforced until the row flips to wired. |

Failures at this boundary are recorded as runtime outcomes on the relevant Run records (Admission Run, Canonical Evaluation Run, Metric Evaluation Run, Action Evaluation Run). Failures that lead to a Subscription state change are observed by contract execution only through the lifecycle state field on subsequent reads; contract execution does not author the state change.

**Governing source.** Connectors and Readers; Admission and Observation; Canonical Evaluation; Metric Evaluation; Action Evaluation; Tenancy and Binding.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model: The Object Model
- Sources and the Catalog: Sources and the Catalog
- Connectors and Readers: Connectors and Readers
- Admission and Observation: Admission and Observation
- Canonical Evaluation: Canonical Evaluation
- Metric Evaluation: Metric Evaluation
- Metric Catalog: Metric Catalog
- Action Evaluation: Action Evaluation
- Tenancy and Binding: Tenancy and Binding
- Tenant Extensions and Overrides: Tenant Extensions and Overrides
- DEC-324d9e: Stripe Billing integration; four subscription tiers
- DEC-1392ee: Demo tier policy; 14-day auto-suspension
- DEC-4a515b: Four process chains from day one
- Decisions: ADR Registry
