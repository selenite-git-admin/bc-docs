---
uid: DEC-4aa2fd
title: "Subscription-plan-driven contract binding automation (metric entitlement is the control surface)"
description: "Plan's metric entitlement is the sole control input; tenant contract bindings + fact provisioning derive from it by reverse-walking each entitled MC's chain."
status: proposed
date: 2026-07-02T05:17:22.959Z
project: bc-core
domain: tenants
subdomain: tenants/subscription-binding
focus: governance
---

# Subscription-plan-driven contract binding automation (metric entitlement is the control surface)

## Context

The operator's product vision — "metric list controlled by subscription plans, rest follows" — is already the documented target architecture (Subscription catalog/metric entitlement + Contract Binding), but the connecting automation is a recorded drift-inventory gap. Locking the derivation model as an ADR before building prevents the two documented-but-disjoint halves (entitlement vs binding) from being wired ad-hoc per tenant. Reverse-walking from the entitled MC (rather than binding bottom-up from the connector) is what makes the metric list the single control surface; refcounted removal keeps shared chain nodes safe under plan changes.

## Context

The subscription/entitlement model is already documented but only partially implemented:

- **Subscription** (platform-scoped, one active per tenant) holds a **Catalog Entitlement** whose axes include **Metric entitlement** = "the subset of platform-registered metrics the tenant may evaluate" (operations/tenant-lifecycle-and-subscription.md; glossary: Subscription = "a tenant's entitlement to a metric or metric family"). Four tiers per DEC-324d9e; four default process chains per DEC-4a515b. Platform DB has a `pricing` schema.
- **Contract Binding** (operating-model/tenancy-and-binding.md) is a separate, tenant-owned artifact: the tenant adopts ONE platform contract version with bounded variation (no field removal, no rule change), one binding per version, not retroactively rebound. This is the wiring that makes the chain resolve and drives fact-table provisioning.
- **Tenant Entitlement Enforcement** consults the Subscription read-only at runtime surfaces (connection registration, admission, metric evaluation, catalog browse).

Today binding is manual and incomplete: `TenantBindingPopulatorService` populates from a connector reverse-walk that only reaches Source Contracts, so a tenant onboarded via `onboard-connector` gets `tenant.tenant_binding` (SC) rows but `tenant.contract_binding` = 0 (CC/MC/OC unbound). pilot1 is in exactly this state — SO facts persist (fact.so_*) but CC/MC are unbound so fact.co_*/fact.ms_* are unprovisioned and no metric can resolve. The tenant-lifecycle chapter's own Drift Inventory records the automation gap directly: "dedicated subscription lifecycle service not located" and "tier envelope registry not located".

## Decision (proposed — design lock; implementation deferred)

Establish a governed automated process in which the subscription plan's **metric entitlement** is the SOLE control surface, and the tenant's contract bindings + provisioning DERIVE from it. "The metric list is controlled by the subscription plan; the rest follows."

1. **Metric entitlement is the only thing operators curate.** The plan lists entitled Metric Contracts (a subset of platform-registered MCs, bounded by tier + entitled subfunctions). No chain node below the MC is ever hand-bound.

2. **Chain derivation by deterministic reverse-walk.** For each entitled MC the platform resolves its full dependency chain — MC → CC(s) it consumes (via metric_binding) → OC(s) → SC(s) → connector/reader — using the existing chain graph. D305 `contract.chain_status` remains the SSOT for completeness; derivation refuses to bind an incomplete chain (fail-closed, surfacing the L1–L7 break).

3. **Binding materialization stays governed.** Derived nodes are bound through the existing binding services into `tenant.tenant_binding` (SC) + `tenant.contract_binding` (CC/MC/OC) — one binding per version, bounded variation only per tenancy-and-binding.md. No raw INSERTs; the service enforces. `devhub_tenant_bind_metrics` (dry-run by default, candidates from /api/admin/readiness/tenant/<slug>/binding-candidates) is the governed MC-binding primitive this orchestrates.

4. **Provisioning is the existing SchemaProvisioner.** After binding, `SchemaProvisioner.reconcile(tenantSlug)` creates fact.co_*/fact.ms_* from the newly bound contracts. Already built — not re-implemented.

5. **Idempotent + refcounted removal.** Re-running is a no-op. Removing a metric from the plan archives (archived_at) bindings it EXCLUSIVELY required; a shared chain node stays bound while any other entitled metric still needs it (refcount by chain membership, never destructive delete).

6. **Single entitlement source for binding AND enforcement.** The same Subscription drives derivation (this ADR) and runtime gating (Tenant Entitlement Enforcement). One source of truth for "what this tenant may evaluate."

## Repair-location & Foundation

- **Location C (mapping/binding) + a thin orchestration layer above it.** The binding artifacts (tenant_binding/contract_binding) and provisioning (SchemaProvisioner) already exist; the new component is the derivation orchestrator that turns entitlement → bindings. NOT A/B (no contract or grammar change), NOT D (evaluation unchanged), NOT E (provisioning already built).
- **Invariant IV (references explicit):** the reverse-walk traverses explicit MC→CC→OC→SC references (metric_binding, cc_field_mapping, reader_binding) — no implicit derivation.
- **Invariant II (object ordering fixed):** binding + provisioning follow the fixed progression order.
- **Invariant I (meaning evaluated once):** entitlement gates ACCESS; it never re-evaluates meaning. This is not lower-layer compensation — the metric contracts are already sound; this only wires which sound metrics a tenant adopts.

## Interim (pilot1, now)

Until the orchestrator is built, pilot1 is bound MANUALLY through the same governed primitive (`devhub_tenant_bind_metrics`, confirm after explicit approval) for the AR Balance MC + arpi_slice CC chain, then `reconcile`. This is the hand-run stand-in for step 3–4 above and unblocks the canonical→AR-Balance metric proof (TSK-842ad5). It is governed (service-mediated, no raw inserts), just operator-triggered rather than plan-derived.
