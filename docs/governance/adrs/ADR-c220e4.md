---
uid: DEC-c220e4
title: "A tenant's metric scope: every active tenant gets every active metric until the Subscription model is built; the entitlement record must be live before the first tenant for a prospect or client; DEC-4aa2fd split"
description: "States the rule in force (every active tenant may see and evaluate every active platform metric on its own data), keeps the Subscription metric entitlement as the declared target, sets the trigger by which that record and its two checks must be live, and supersedes DEC-4aa2fd by splitting it into its implemented onboarding walk and its deferred entitlement control."
status: decided
date: 2026-10-01T05:35:58.507Z
project: bc-docs
domain: tenants
subdomain: tenants/metric-scope
focus: governance
supersedes: DEC-4aa2fd
---

# A tenant's metric scope: every active tenant gets every active metric until the Subscription model is built; the entitlement record must be live before the first tenant for a prospect or client; DEC-4aa2fd split

> **Decided 2026-10-01.** The operator decided the rule, the trigger and the split in these words: desk grant `2026-10-01T05-33-56-929Z-ce64ce72` (text SHA-256 `ce64ce72bb4d6fc6ddcff3cf879723643e506bcfdb6765ec6229ec58835d0509`, recorded 2026-10-01T05:33:56Z, request 146): "Yes: until the subscription model is built, every active tenant may see and evaluate every active platform metric on its own data, and the metric entitlement record with its evaluation and catalog checks must be live before a second customer tenant is activated or a plan narrower than the whole catalog is sold. The Architect records this as an ADR, which also splits DEC-4aa2fd into its implemented onboarding walk and its deferred entitlement control. Anant". **Trigger wording corrected the same day:** desk grant `2026-10-01T05-45-59-134Z-c9e0356a` (text SHA-256 `c9e0356a854ea0435f6c09899991901b81be0af2e00bbe9e973ed218aa527e49`, recorded 2026-10-01T05:45:59Z, request 148): "Yes: correct the trigger in ADR DEC-c220e4. Kaveri is the pilot tenant and is not counted as a customer. The metric entitlement record with its evaluation and catalog checks must be live before the first tenant for a prospect or client is activated, on any source system, or before a plan narrower than the whole catalog is sold. This replaces the words second customer tenant in my grant of 1 October 2026 ending ce64ce72. Anant". The Decision section restates the two grants, with the trigger in the words of the second, and adds nothing to them. The sections after it are the Architect's reading, rulings and design notes under its charter; they are marked as such.

## Context

The Platform Controller found that nothing checks whether a metric is bound to a tenant (DevHub TSK-5e7ae4), and the Chief routed the question to the Architect as a design act (TSK-c5e6f7). The study behind this record is barecount-devhub `artifacts/architect/STUDY-tenant-metric-scope-2026-10-01.md` (PR 184). Its facts were read on 2026-10-01 at bc-docs `origin/main` e047e22, bc-core `origin/main` 4f163044 and the live platform database, read-only.

**What was already declared.**

- A tenant's metric scope is the metric entitlement on its Subscription record: "the subset of platform-registered metrics the tenant may evaluate" (`docs/operations/tenant-lifecycle-and-subscription.md`, "Catalog Entitlement").
- Metric evaluation and the tenant's catalog view consult that entitlement, and every surface is declared "Not yet wired": "the platform does not represent any of these surfaces as enforced" (`docs/operating-model/tenant-entitlement-enforcement.md`, "Wiring Status").
- The tenant metric list shows all active metrics; "subscription-plan entitlement (DEC-4aa2fd/D475) is a deferred overlay, not a gate" (DEC-a1290e, decided).
- Pricing and subscription are deferred by decision: "v1 = single flat band, no subscription instantiated" (`docs/implementation/platform-readiness-program.md`, lane S4).
- DEC-4aa2fd proposed metric entitlement as the one control surface. It was closed as `reversed` on 2026-08-22 in the operator's ruling on stuck proposals (bc-docs commit 5c6d2ac), with the note "reverse or re-propose when subscription enforcement (TSK-f16257) is scheduled".
- Foundation does not define entitlement: Subscription is an Operations governance record that operates around Foundation-defined artifacts (`docs/foundation/foundation-overview.md`).

**What was built.**

- No Subscription or entitlement table exists in the platform database. `pricing.package` exists; nothing ties a tenant to a plan or to a metric.
- The one active tenant, `kaveri`, holds seven canonical rows and no metric rows in `tenant.contract_binding`. Sixteen metrics were set up for it by the governed onboarding act (sixteen `metric` commands in `schema_provisioner.provisioning_command`). The platform has 82 metrics with a current active version.
- Governed evaluation loads any active metric by its id with no tenant check (bc-core `src/boundary/metric-spec-loader.ts`); the tenant comes from the signed-in user's claim. The tenant list returns every active metric and sets `activated: true` on each row (`src/tenant-views/beyond-metrics.service.ts`).
- Tenant identity is enforced (`src/auth/guards/tenant-claim.guard.ts`); no data crosses tenants.
- The onboarding walk of DEC-4aa2fd is live, and its code names that reversed record as its authority (`src/schema-provisioner/metric-onboarding.service.ts`).

**What was wrong.** No invariant was broken. Three statements were untrue: the binding chapter's "Binding declares which MCs are scoped for evaluation in a tenant" (`docs/onboarding/tenant-metric-binding.md`); a reversed decision named as the authority of live code; and `activated: true` on every row of the tenant list, where no record holds an activation. And the rule the platform ran under was written nowhere as a rule.

## Decision

1. **The rule in force until the Subscription model is built.** Every active tenant may see and evaluate every active platform metric, on its own data only. No metric-level check stands between an active tenant and an active Metric Contract version. Tenant identity and tenant data isolation are unchanged and stay enforced (DEC-f0e78e, DEC-771baf): this rule opens the catalog, never another tenant's data.

2. **The declared target stands.** A tenant's metric scope is the metric entitlement on its Subscription record, authored under `docs/operations/tenant-lifecycle-and-subscription.md` and consulted at the surfaces named in `docs/operating-model/tenant-entitlement-enforcement.md`. This record changes neither chapter's target. Their "Not yet wired" rows remain the true status, and this record is the decision those rows rest on.

3. **The trigger.** The metric entitlement record, with its check before metric evaluation and its check on the tenant's catalog view, must be live before either of these acts: (a) the first tenant for a prospect or client is activated, on any source system; (b) a plan narrower than the whole catalog is sold. Kaveri is the pilot tenant and is not counted as a customer. Either act without the record live breaks this decision; it is not a scheduling slip. Until the record is live, no surface derives a tenant's metric scope from anything else: not from contract bindings, not from provisioning commands, not from past evaluations.

4. **DEC-4aa2fd is split, and this record supersedes it.**
   - (a) **The onboarding walk: implemented.** Given a tenant and a metric, the governed onboarding act walks back from the metric to the canonical and source contracts it depends on, records the canonical and source bindings, and enqueues the tenant's provisioning (DEC-4aa2fd items 2 to 4, as built in bc-core `MetricOnboardingService`). It is live, and this record is its authority from this date. The walk sets a metric up for a tenant. It does not entitle the tenant to the metric, and nothing reads it as entitlement.
   - (b) **The entitlement control: deferred.** The plan's metric entitlement as the one thing operators curate, refcounted removal, and one entitlement source for both binding and enforcement (DEC-4aa2fd items 1, 5 and 6) are not built and are not decided here. They are re-proposed as their own ADR when the Subscription work is scheduled (TSK-f16257). Item 3 sets the latest moment for that.

## Reading of the terms (Architect)

- **Active tenant, active metric:** a tenant whose registry status is active; a Metric Contract that is not archived and whose current version is in governance state `active`.
- **Pilot tenant:** `kaveri`. It proves the mechanism and is not counted as a customer.
- **Tenant for a prospect or client:** any tenant activated for a party outside BareCount, whatever its source system. Disposable proof tenants are not such tenants.
- **Live:** the record exists in the platform database under a governed authoring act, the evaluation precondition refuses a metric outside it, the catalog view shows only what is inside it, and the two rows of the "Wiring Status" table are flipped with a release reference.

## Rationale

The documents declared a per-tenant metric scope that nothing enforces, and the rule the platform actually runs under was written nowhere as a rule. Writing it down makes documents and code agree without building one axis of the Subscription model in isolation, which is the piecemeal wiring DEC-4aa2fd was written to prevent. With one live tenant the open scope harms no one, because identity and data isolation are enforced. The trigger turns "later" into a condition on the act that would make the gap matter. Splitting DEC-4aa2fd gives the live onboarding code an authority in force and keeps the unbuilt half visible as deferred, not rejected.

A filter added to the evaluation route or the list before the record exists would have to take the scope from something else, such as the provisioning commands. A provisioning command records that a table was requested. It does not record that a tenant is allowed a metric. Reading a permission out of a side effect is the lower-layer compensation the Foundation gate stops (DEC-79b62f, hard rules).

## Options considered

1. **Keep the flat band until a named trigger, and write the rule down.** Chosen.
2. **Build the metric entitlement record now:** a platform table of tenant and metric, written by the onboarding act, checked before evaluation and by the list. Not chosen: it needs a schema change and three build units, and it pulls one axis of the Subscription design forward on its own.
3. **Filter the list to what was provisioned.** Rejected: compensation, as above, and it would leave evaluation open while the list looked closed.

## Consequences

Each is a follow-up under its owner's own unit. None is done by this record.

- **`docs/onboarding/tenant-metric-binding.md`** stops claiming that binding scopes evaluation, describes the onboarding act as setting a metric up for a tenant, and cites this record in place of D475 (Docs Controller).
- **`docs/operating-model/metric-catalog.md`, "Tenant View",** gains an as-built note: until the entitlement record is live, the tenant view shows all active metrics under this record and DEC-a1290e (Docs Controller).
- **bc-core `metric-onboarding.service.ts`** cites this record, item 4(a), as its authority (Platform Controller).
- **bc-core `beyond-metrics.service.ts`** stops asserting `activated: true` (Platform Controller, with the Customer Portal Controller for the portal's use of the field).
- **DEC-4aa2fd** is `superseded` by this record, flipped in the same commit.

## What a tenant-facing surface may show meanwhile (Architect's ruling)

- It may list every active platform metric: DEC-a1290e and item 1 allow it.
- It does not call a metric "activated", "enabled", "subscribed" or "yours". No record says so for any metric.
- It may show data state from accepted evaluations in the tenant's own database (`snapshotBacked` and the snapshot).
- Removing a false label is a truth fix at the read model. It is not a scope filter and needs no entitlement record.

## Design constraints for the deferred half (Architect; not built, not decided here)

The ADR that re-proposes the entitlement control starts from these, and may change them only by saying so:

1. The record lives in the platform database on the Subscription side and is authored only by a governed platform act. It is never derived from bindings, provisioning commands or evaluations.
2. One resolver answers "may this tenant run this metric at this time". Evaluation and the catalog view both call it; neither works the answer out for itself.
3. Evaluation calls it as a precondition of the act, before any authoritative state is produced, and records a refusal on the run, as `tenant-entitlement-enforcement.md` already requires. It is not a filter in a controller.
4. A schema change for the record follows the Database Change Protocol (DEC-4c1396) with the operator's explicit yes.

## The readiness model this trigger serves (context, not decision)

On 2026-10-01 the operator described to the Chief what the pilot is for: `kaveri` proves the mechanism and a defined set of metrics; a new tenant on the same source system gets the proven metrics according to its data profile; a tenant with more data or an explicit need widens the portfolio for every later client; a new source system needs its contracts and mapping built once, with the engine unchanged. The Chief recorded those words the same day.

The trigger in item 3(a) is the moment that model calls onboarding a client. The Architect's reading, for the future ADR: at that moment the entitlement record is what carries "the proven metrics, by data profile" to the new tenant as a named, governed set, so that what a client may run is declared and not inferred from what happened to be provisioned.

## Non-goals

No change to Foundation, to the six invariants or to any evaluation boundary. No schema change. No change to tenant identity or data isolation. No pricing, tier or billing decision. No decision on whether a tenant follows a metric's new version at once (DevHub TSK-6d13d7). No supersession of DEC-a1290e, which stays in force.

## References

- DEC-4aa2fd (superseded by this record), DEC-a1290e, DEC-79b62f, DEC-f0e78e, DEC-771baf, DEC-324d9e, DEC-4c1396
- `docs/operations/tenant-lifecycle-and-subscription.md`; `docs/operating-model/tenant-entitlement-enforcement.md`; `docs/operating-model/metric-catalog.md`; `docs/operating-model/tenancy-and-binding.md`; `docs/onboarding/tenant-metric-binding.md`; `docs/implementation/platform-readiness-program.md`
- barecount-devhub `artifacts/architect/STUDY-tenant-metric-scope-2026-10-01.md` (PR 184); DevHub TSK-c5e6f7, TSK-5e7ae4, TSK-f16257, TSK-6d13d7
