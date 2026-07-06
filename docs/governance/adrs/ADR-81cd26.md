---
uid: DEC-81cd26
title: "Connections are platform-scoped — reverse D163 for connection tables"
description: "Connection tables moved back to platform DB (runtime schema). D163 incorrectly put them in tenant DB. Add tenant_id for filtering."
status: implemented
subdomain: bc-core-architecture
focus: connection-scope-reversal
date: 2026-03-26
project: bc-infra
domain: database
refs:
  - type: decision
    label: "D163"
authority: authoritative
migrated_from: legacy v2 archive
---


# Connections are platform-scoped — reverse D163 for connection tables

## Context

1. Connectors are platform — connections are children of connectors, FK integrity requires same DB (D162 Rule 3). 2. Follows D164 contract pattern: platform-level resource with tenant ownership via column, not separate DB. 3. bc-admin needs cross-tenant visibility without fan-out queries. 4. Reader runtime resolves connections without tenant context — cross-DB lookup adds circular dependency. 5. Connections are low-volume config (5-20 per tenant), not high-volume execution data.

## Decision

Connection, connection_config, and connection_check tables belong in platform DB (runtime schema), not tenant DB. D163 incorrectly moved connections to tenant DB. Connections are infrastructure/configuration (same category as connectors, readers, contracts) — not execution data. Add tenant_id column for ownership filtering. Admission runs remain in tenant DB (execution data).

## Options Considered

N/A

## Consequences

N/A
