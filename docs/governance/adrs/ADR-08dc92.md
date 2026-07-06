---
uid: DEC-08dc92
title: "Platform/Tenant Route Isolation — /api/* vs /api/t/* with schema-per-tenant DB fence"
description: "Strict 3-layer isolation: /api/* for platform (bc-admin), /api/t/* for tenant (bc-portal), schema-per-tenant DB fence, infra fence future."
status: implemented
subdomain: platform-tenant-split
focus: route-isolation
date: 2026-03-16
project: bc-admin
domain: database
refs:
  - type: decision
    label: "D028"
authority: authoritative
migrated_from: legacy v2 archive
---


# Platform/Tenant Route Isolation — /api/* vs /api/t/* with schema-per-tenant DB fence

## Context

1. Recurring platform-scope trap has wasted multiple sessions — bc-admin calls endpoints that TenantMiddleware blocks because it can't resolve a tenant. Fragile JWT audience sniffing is not reliable enough.
2. Customer onboarding requires bc-admin (platform) and bc-portal (tenant) to work cleanly without ambiguity.
3. URL-level isolation makes scope visible — no guessing, self-documenting APIs. Firewall rules, logging, audit all become trivial.
4. Schema-per-tenant isolation ensures tenant A can never see tenant B's boundary data. Matches D022 hybrid model (shared registry, isolated data plane).
5. Each layer can be tightened independently — route fence today, DB fence today, infra fence later.
6. Aligns with contract scoping model (D054): Pattern C artifacts (canonical contracts) are platform-only, Pattern A/B artifacts have platform masters + tenant instances.

## Decision

Strict platform/tenant isolation at three layers:

### Layer 1 — Route Fence
- `/api/*` routes are platform-scoped (`@PlatformOnly`). Only bc-admin calls these. TenantMiddleware skips tenant resolution.
- `/api/t/*` routes are tenant-scoped (`@TenantScoped`). Only bc-portal calls these. TenantMiddleware enforces tenant resolution via JWT/header.
- No undecorated controllers. Every controller explicitly declares its scope.

### Layer 2 — Database Fence
- `CONTROL_PLANE_DB` (shared): public, platform, registry schemas. Contracts, connectors, readers, connections, admission_run telemetry, source catalog, discovery, bindings, masters, libraries.
- `DATA_PLANE_DB` (schema-per-tenant via `TenantConnectionService`): boundary + evidence schemas. Observed records, source objects, admitted records, evaluations, canonical objects, metric snapshots, action objects, evidence, lineage.
- Tenant schema naming: `t_{slug}` (e.g., `t_selenite`). Auto-created on tenant provisioning.

### Layer 3 — Infrastructure Fence (future, not today)
- Single Aurora cluster with schema-per-tenant (multi-tenant default).
- Can upgrade to database-per-tenant (D028) or account-per-tenant without architectural change.

### Split Write Pattern (not dual write)
The OrchestratorService writes to BOTH pools in a single execution cycle — this is correct:
- Admission run telemetry (counts, duration, status) → `registry.admission_run` in CONTROL_PLANE_DB
- Business data (observed records, source objects, admitted records, evidence) → `t_{slug}.boundary.*` / `t_{slug}.evidence.*` in DATA_PLANE_DB

### Controller Classification
- 25 existing controllers → `@PlatformOnly` (registry, catalog, platform, auth, health)
- 10 existing boundary controllers → `@TenantScoped`, move to `/api/t/*` prefix
- ~5 new thin tenant read-view controllers under `/api/t/` (contracts, readers, metrics, discovery, mappings) — same service layer, tenant-filtered
- bc-portal API base: `/api/t`
- bc-admin API base: `/api`

## Options Considered

N/A

## Consequences

N/A
