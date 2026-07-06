---
uid: DEC-58bf7f
title: "Platform vs Tenant API Scope — Role-Based Middleware Bypass"
description: "Platform admin endpoints skip tenant middleware via JWT platform role claim. Superseded by @PlatformOnly() decorator."
status: superseded
date: 2026-03-12
project: bc-admin
domain: contracts
authority: retired
migrated_from: legacy v2 archive
---


# Platform vs Tenant API Scope — Role-Based Middleware Bypass

## Context

Superseded by D072 (DEC-3a6f74) @PlatformOnly() guards and D081 (DEC-08dc92) /api/* vs /api/t/* route isolation. JWT scope mechanism was not adopted.

## Decision

Use JWT role/scope claim to distinguish platform access (bc-admin) from tenant access (bc-portal). The tenant middleware checks the JWT for a `platform` scope/role — if present, tenant identification is NOT required and the request proceeds without tenant context. Tenant-scoped requests (bc-portal) continue to require x-tenant-id header.

Implementation:
1. Add `scope` or `role` claim to Cognito JWT (or derive from Cognito group membership)
2. Tenant middleware checks: if JWT has platform role → skip tenant requirement
3. bc-admin users get platform role via Cognito user group
4. bc-portal users get tenant role, must provide x-tenant-id
5. Services that need tenant filtering check CLS context (already works)
6. Platform-scoped services (kpi-specs, metric-catalog, registry CRUD) work without tenant

This applies to ALL resources, not just kpi-specs. Contracts, connectors, readers, sources, mappings — all are platform-level resources managed by bc-admin.

Evaluated alternatives:
- Route prefix split (/api/platform/*): Rejected — duplicates routes or forces re-pathing
- Expand exclusion list: Rejected — fragile, grows with every new resource, no auth distinction

## Options Considered

N/A

## Consequences

N/A
