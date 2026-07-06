---
uid: DEC-3a6f74
title: "Platform/Tenant: Keep single service, formalize with guard decorators"
description: "Do NOT split bc-core into separate platform and tenant services. In-process separation via middleware is sufficient"
status: implemented
subdomain: platform-tenant-split
focus: service-topology
date: 2026-03-15
project: bc-infra
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Platform/Tenant: Keep single service, formalize with guard decorators

## Context

Architecture audit shows platform/tenant separation is already clean at middleware + DB schema level. Splitting into two services would add complexity without solving any current problem. Formalize with decorators instead.

## Decision

Do NOT split bc-core into separate platform and tenant services. The current in-process separation (middleware + schema-level isolation) is clean and sufficient.


## Options Considered

N/A

## Current State

- Platform scope: detected via JWT `aud` claim (adminClientId)
- Tenant scope: detected via `x-tenant-id` header + JWT `aud` claim (portalClientId)
- DB isolation: separate PostgreSQL schemas (`public`/`platform` vs `registry`/`tenant`/`boundary`/`evidence`)
- Connection pools: global pool for platform, per-tenant pools for tenant schemas

## What to Formalize

1. Add `@PlatformOnly()` decorator for platform-scoped controllers — fails with 403 if scope != platform
2. Add `@TenantRequired()` decorator for tenant-scoped controllers — fails with 403 if no tenant context
3. Add `@UseGuards(JwtAuthGuard, RolesGuard)` to ALL boundary controllers (currently missing)
4. Document scope classification for every controller in a table

## Why Not Split

- Shared services (evidence, audit, contract validation) would require cross-service calls
- Double deployment complexity for zero customer benefit at current scale
- Boundary module needs both platform contracts (master) and tenant bindings in the same execution context
- In-process function calls > network calls for evaluation engine performance

## When to Reconsider

- If tenant count exceeds 50 and noisy-neighbor issues emerge
- If platform ops team needs independent deploy cadence from tenant features
- If regulatory requirements mandate physical isolation

## Consequences

N/A
