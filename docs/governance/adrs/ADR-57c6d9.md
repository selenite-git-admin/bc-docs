---
uid: DEC-57c6d9
title: "Platform metric trust strip ends at Activated; tenant-runtime stages move to bc-portal"
description: "Platform trust strip = 4 platform stages; bound/evaluated/producing are tenant-scoped and move to bc-portal (refines D438)"
status: decided
date: 2026-06-27T05:57:05.007Z
project: bc-core
domain: metrics
subdomain: mcf/trust-view
focus: read-model
---

# Platform metric trust strip ends at Activated; tenant-runtime stages move to bc-portal

## Context

Platform/tenant boundary (the recurring scope trap). bc-admin is platform-scoped; a metric's platform story is complete at activation. bound/evaluated/producing depend only on tenant data and vary per tenant, so answering them on a platform page is a scope error — it shows some tenant's state without a tenant context and breaks with multiple tenants. bc-portal is tenant-scoped by login, so it is the natural, selector-free home for runtime status. The stages were already non-live placeholders (hardcoded none), so removing them loses no real signal; it removes a misleading affordance. computeTrustRollup is independent of these stages, making the change behavior-neutral for the rollup.

## Decision

The MCF metric-detail trust view (refines D438 / DEC-1ac398, "two-strip trust view") Strip-1 lifecycle on the PLATFORM admin surface (bc-admin /catalog/metrics/governed/:uid) is reduced from 7 stages to the 4 platform-lifecycle stages: seed → contracted → panel_verified → activated.

The 3 tenant-runtime stages — bound, evaluated, producing — are removed from the platform strip. They are per-tenant DATA outcomes ("does this metric produce against a given tenant's data?"), differ tenant-to-tenant, are not platform-evidenceable, and were being rendered as always-grey placeholders (mcf-metric-detail.builders.ts hardcoded status:'none'). On a platform page they would silently reflect one tenant's state and break the moment a second tenant exists.

These three stages will be surfaced in the TENANT application (bc-portal) — a metric list/detail view that is inherently tenant-scoped by login (no tenant selector needed), so it naturally shows the correct tenant's runtime status. That view gets real data once Bar-2 crosses MCF metrics into tenant runtime (TSK-8abd14). Until then, the platform page honestly ends at Activated — looks "incomplete" (4 of 7 dots) but is correctly scoped.

Implementation: buildLifecycleStrip returns the 4 platform stages; the LifecycleStage.stage union is narrowed to the 4 platform stages (the platform builder is the only producer). computeTrustRollup does not read bound/evaluated/producing, so the rollup color is unchanged — behavior-neutral. Repair-location F (read-model/diagnostics); strengthens Invariant VI (render only emitted evidence, never placeholder).
