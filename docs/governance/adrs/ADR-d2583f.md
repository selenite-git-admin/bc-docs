---
uid: DEC-d2583f
title: "Dev-phase green slate: clear stale dev tenant bindings to activate CC successors; the provisioning fanout gates future tenants"
description: "Green-slate dev phase: stale dev tenant source-bindings are cleared (reversible), not provisioned, to activate CC successors pre-first-tenant; the provisioning fanout gates future tenants. E3-A/kaveri precedent."
status: decided
date: 2026-10-29T16:27:48.406Z
project: platform
domain: tenants
subdomain: tenants/dev-phase
focus: green-slate activation-provisioning
---

# Dev-phase green slate: clear stale dev tenant bindings to activate CC successors; the provisioning fanout gates future tenants

## Context

The platform is in the pre-first-real-tenant DEV phase ("green slate"): zero production tenants exist, so no live tenant-wide evaluation depends on the shared customer-invoice-family grains. Flipping `cc-das36` to v4.0.0 (`canonical_id_v1`, per-legal-entity) is therefore the intended DEC-ffbc24 realization with no live regression. Clearing a reversible dev binding is proportionate to a green slate and avoids tenant-schema provisioning that would contradict the dev-phase, no-tenant stance.

This was forced to a decision by the E3-A proof on 2026-10-29: activating `cc-das36` v4.0.0 to global `active` enqueued provisioning (`pending_provisioning`) because the governed activation fanout (`onCanonicalActivated` → `findSourceContractsForCanonical` → `findTenantsBoundToSources`) reverse-walked the contract's single source (`019fe42b` v1.0.0) and found an active dev `kaveri` tenant binding.

## Decision

During the pre-first-real-tenant DEV phase (green slate), a stale DEV tenant source-binding that gates a canonical-contract successor activation is **cleared** via the governed, reversible unbind (`POST /api/tenant-bindings/deactivate`, `effective_to=now`) — it is **not** provisioned.

Precedent (E3-A, 2026-10-29): the operator ruled `kaveri` a stale dev binding and authorized clearing it. Because the unbind is **source-keyed** (tenant × source × version × env), not CC-keyed, clearing `kaveri ↔ 019fe42b` also detached `kaveri` from the other two shared customer-invoice-family canonicals on that source (`cc-7174p`, `cc-dh5d9`). The operator accepted this wider scope as green-slate-consistent and reversible. `cc-das36` v4.0.0 is now `active`; v3.0.0 is superseded.

## Consequences and safety nets

- **Structural safety net (already proved itself here):** the governed activation/provisioning fanout *gates* any CC-version activation on provisioning every bound **active** tenant. A future real tenant bound to these sources cannot silently break — it must be provisioned on the v4.0.0 per-LE shape first. (TSK-24eb5a: document this in the tenant-onboarding SOP; re-binding `kaveri` is `POST /api/tenant-bindings`, reversible.)
- **Follow-up (the real fix):** a demo/platform-plane proof should not require a **global** CC activation that reaches into tenant source-bindings at all. Plane-scoped CC-version resolution is the design fix (TSK-66ef36, Architect) — it would let a demo-plane proof resolve the intended CC version on that plane without a global activation.

## References

- DEC-c220e4 — entitlement record live before the first tenant
- DEC-89db41 — the Demoed demo runtime plane
- DEC-470a41 — RuntimePlane on the evaluation read path
- DEC-ffbc24 — opaque per-legal-entity id (`canonical_id_v1`)
