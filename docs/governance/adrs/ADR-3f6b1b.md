---
uid: DEC-3f6b1b
title: "Plane-scoped canonical-contract version resolution: a demo/platform-plane proof resolves its CC version on the plane, without a global activation"
description: "Plane-scoped canonical-contract version resolution: a demo/platform-plane proof resolves its CC version on the plane, without a global activation"
status: proposed
date: 2026-10-31T10:15:23.096Z
project: bc-core
domain: contracts
subdomain: contracts/canonical
focus: plane-scoped-resolution
---

# Plane-scoped canonical-contract version resolution: a demo/platform-plane proof resolves its CC version on the plane, without a global activation

## Context

Verified at source (bc-core @7011f655): loadActiveCc (ccv2-canonical-resolver.service.ts:649-656) and CoCandidateReader.enumerateOnPlane->readActiveCcDeclarations+pickGrainCc (co-candidate-reader.ts:313-316,136) select the grain CC version purely by global governance_state_code='active'; RuntimePlane (DEC-470a41) scopes only the fact/CO DATA reads (factReader.legalEntityIdOfCode/listCanonicalObjects), and DEC-470a41 §2.4 #4 deliberately left CONTROL_PLANE_DB (the CC-declaration read) global. To make the demo-plane AR-Balance proof resolve cc-das36 v4.0.0 the version had to be flipped GLOBALLY active, which fired onCanonicalActivated->findSourceContractsForCanonical->findTenantsBoundToSources, reverse-walked the shared source 019fe42b into an active kaveri binding, and stuck at pending_provisioning; the only path-A lever (governed unbind) is SOURCE-keyed and 019fe42b feeds three active canonicals, so clearing detaches kaveri from all three. Foundation diagnosis (Inv I, meaning evaluated once): the global active flag overloads two meanings — the version tenants are SERVED from vs the version this evaluation plane PINS and proves against; a Demoed proof needs the second without the first. Repair at C (an explicit per-plane CC-version binding) + the plane-parametric resolution read, extending a declaration DEC-470a41 already made; NOT at the tenant source-binding layer (the SOURCE-keyed unbind was the forbidden lower-layer compensation). A/B (the CC contract semantics) are correct and unchanged. Design act (DEC-c48b0f). Invariants I/IV/V honored; tenant path unchanged.

## Decision

Make canonical-contract version resolution plane-parametric, extending DEC-470a41's RuntimePlane from data-plane acquisition to CC-version selection. On a demo (and by the same rule a non-tenant platform) plane, the grain CC version is resolved from a governed, explicit, per-plane CC-version binding — (demo_world_version) -> {canonical_contract -> version_code}, e.g. (ar-balance-demo) -> {cc-das36 -> 4.0.0} — NEVER from the global governance_state_code='active' flag and NEVER by reaching into tenant source-bindings or provisioning. Tenant-plane resolution is byte-identical to today (keeps the global active-version selection). The plane binding is governed, explicit, immutable per frozen world (storage home — a demo-plane governed manifest vs a control-plane plane-scoped column keyed by (plane, demo_world_version) — is a bounded build choice to settle with Chief/DB; the ruling is plane-scoped+governed+explicit). The selection becomes plane-aware at BOTH enforcement points so neither diverges: CoCandidateReader.enumerateOnPlane (plane!=tenant -> resolve the pinned (cc,version) from the plane binding then pickGrainCc over exactly that; plane==tenant -> readActiveCcDeclarations unchanged) and CcV2CanonicalResolverService.loadActiveCc (same plane branch). Resolution is SELECT-only, reads/sets/requires no governance_state_code, and fires NO activation fanout. Hard constraints: tenant behaviour byte-identical; no global activation required for a demo/platform-plane proof; tenant activation stays a separate governed act with its own provisioning+grant; governed+explicit never a caller claim (fail-closed when no plane binding exists, never a silent fall-back to global active); fits DEC-470a41, no parallel plane concept. Full draft: artifacts/architect/DRAFT-ADR-plane-scoped-cc-version-resolution-TSK-66ef36-2026-10-31.md.
