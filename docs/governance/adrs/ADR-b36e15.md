---
uid: DEC-b36e15
title: "Platform-plane pool-readiness binds to the authoritative canonical-contract declaration, not the tenant-provisioned 'active' state"
description: "Platform-plane pool-readiness binds to the authoritative canonical-contract declaration, not the tenant-provisioned 'active' state"
status: decided
date: 2026-10-05T13:37:21.367Z
project: platform
domain: platform
subdomain: canonical-contract-lifecycle
focus: plane separation (platform vs tenant) for metric directory pool-readiness
---

# Platform-plane pool-readiness binds to the authoritative canonical-contract declaration, not the tenant-provisioned 'active' state

## Context

See decision text below.

# Platform-plane pool-readiness binds to the authoritative canonical-contract declaration, not the tenant-provisioned 'active' state

**Status:** decided. Authority: the operator approved the plane-split repair, relayed by the Chief Controller, 2026-10-05 (if a desk grant was recorded for this decision, cite its grant_id here for parity with DEC-ec1434). Author: Architect SES-b9b0ef. Grounding study: barecount-devhub `artifacts/architect/clean-directory-2026-10-03/RULING-plane-clean-platform-pool-vs-tenant-provisioning-2026-10-05.md` @3a313592.

## Context

The Oct-2 objective (metric pool → Certified/Released) is a PLATFORM-plane act (define → certify → release; it never produces a value). Phase A cleans the metric directory to entry-ready/clean terminal states platform-side; tenant evaluation/reporting is the tenant plane (Phase C+).

The canonical-v2 lifecycle makes a FACT-PRODUCING canonical contract version's `governance_state_code = 'active'` depend on every AFFECTED (bound) tenant being provisioned — the provisioning-readiness mechanism labelled **D575 Unit-3 F1** in bc-core `contract.service.ts` (distinct from **ADR-09fb2f**, which is the related D575 platform prerequisite: tenant evidence-chain immutability + runtime identity separation). A target of `active` is redirected to `pending_provisioning`, and `pending_provisioning → active` is fail-closed until the provisioning worker has provisioned every affected tenant (bc-core `contract.service.ts:946-1067`; `provisioning-readiness.service.ts:6-23`, which rules "zero affected tenants ⇒ ready"; affected tenants are a reverse-walk via `contract_binding`, `contract-activation.service.ts:70,89-90`). The 0036 entry gate's G4 and certification/release bind to `'active'` (`ccv2-canonical-resolver.service.ts:584`).

For a grain NOT bound to a live tenant the CC reaches `active` with no provisioning. For a grain bound to a live tenant (customer_invoice ↔ Kaveri), platform-plane pool-readiness is held hostage to tenant provisioning — a plane-clean violation. The operator: "no Oct-2 objective up to Released should need a tenant."

## Decision

Platform-plane pool-readiness — the 0036 entry gate G4 "grain has a canonical contract", certification, and release — binds to the canonical contract version being DECLARATION-AUTHORITATIVE, defined by an **evidenced approval**: the version has a recorded approval (it reached the `approved` milestone; `contract.canonical_contract_approval`). This is **not** raw `governance_state_code` membership. The declared `field_selection`/`resolved_schema` G4 reads is locked at `approved` and provisioning never changes it.

In state terms, declaration-authoritative corresponds to `governance_state_code ∈ {approved, pending_provisioning, active}` **only under the lifecycle invariant that `pending_provisioning` and fact-producing `active` are reachable only from `approved`**. The current lifecycle does NOT yet guarantee that: bc-core `contract.service.ts:49-60` permits `draft → pending_provisioning` and `draft → active`, and a fact-producing `active` request is redirected to `pending_provisioning` at `:946-960` — so a never-approved draft could reach `pending_provisioning` and be wrongly treated as authoritative. Therefore:

- **Until the lifecycle is tightened, the evaluator MUST test the evidenced approval** (the recorded `approved` milestone / `canonical_contract_approval`), not raw state membership.
- **Companion requirement, named here:** tighten the canonical-contract lifecycle so `pending_provisioning` and fact-producing `active` require a prior `approved` (close the `draft →` skip paths), proven red-first. Once proven, the state set `{approved, pending_provisioning, active}` is equivalent to the approval predicate and the evaluator may use it directly. This is a Platform bc-core + DB (lifecycle CHECK/guard) unit, platform lane, not a caveat left to implementer discretion.

D575 Unit-3 F1's provisioning-gated `'active'` is RETAINED UNCHANGED as the TENANT/evaluation-plane readiness (fact production). The plane split: platform-plane declaration-authoritative readiness (evidenced `approved`) vs tenant-plane provisioned-active readiness.

## Foundation

Repair location B (contract semantics / the plane boundary), not a lower-layer (0036/D) compensation (Foundation gate Q2: the upper layer was underspecified — `'active'` carried two meanings). No lower-layer compensation. Certification rests on validity, not production (DEC-793e13, DEC-c48b0f). Platform metrics exist independent of tenants (DEC-c220e4). The Canonical Contract is a platform-plane declaration (the-evaluation-boundaries.md); producing Canonical Objects is the tenant-plane act. Invariants III/IV/V/VI preserved.

## Consequences

- The directory members, including those on live-bound grains, reach entry-ready/clean platform-side without tenant provisioning; Phase-A proving units need not avoid live-bound grains.
- customer_invoice 1.1.1 (`pending_provisioning`) is platform-ready **if it has an evidenced approval** (reached `approved`); Metric/DB confirm its path. Either way there is no restoration action and no Kaveri drain for Phase A (the drain is Phase C so Kaveri can evaluate).
- The evaluator binding change (G4 binds the evidenced-approval predicate; equivalently the `{approved, pending_provisioning, active}` state set once the lifecycle is tightened) is a Platform bc-core code unit via the normal review flow (platform lane, Codex), dispatched on this DEC-uid. It carries the companion lifecycle-tightening requirement above.
- No 0036 migration bytes change: the grain-CC state G4 reads is evaluator logic, not DDL. The 0036 design §4 is updated to match.

## References

ADR-09fb2f (D575 platform prerequisite: tenant evidence-chain immutability + runtime identity separation); the D575 Unit-3 F1 provisioning-readiness mechanism in bc-core `contract.service.ts` / `provisioning-readiness.service.ts`; `contract.canonical_contract_approval` (the approval record); DEC-ca8943 (entry gate G1–G5); DEC-c220e4; DEC-793e13; DEC-c48b0f; `foundation/the-evaluation-boundaries.md`; `foundation/the-invariants.md`.
