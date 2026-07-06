---
uid: DEC-d7c1dd
title: "Hybrid tenant isolation — schema-per-tenant standard, database-per-tenant premium"
description: "Two-tier isolation: schema-per-tenant (default) on shared DB, database-per-tenant reserved for enterprise compliance. Same TenantConnectionService abstraction."
status: superseded
superseded_by: DEC-1cdc5e
subdomain: tenant-isolation
focus: tier-model
date: 2026-03-17
project: bc-core
domain: database
refs:
  - type: decision
    label: "D084"
authority: authoritative
migrated_from: legacy v2 archive
---


# Hybrid tenant isolation — schema-per-tenant standard, database-per-tenant premium

## Context

Schema-per-tenant handles current needs with minimal operational overhead. Database-per-tenant reserved for enterprise customers with compliance requirements. Building it now would add migration complexity (run per DB) without a customer driving the requirement. The provisioning abstraction supports both modes when needed.

## Decision

Two-tier tenant isolation model:

1. **Standard tier (default):** Schema-per-tenant on shared `barecount` database. Tenant schemas (`t_{slug}`) created automatically on tenant provisioning (D084). Covers majority of customers.

2. **Enterprise tier (future):** Database-per-tenant. Dedicated logical database on same RDS instance. Used when customer contract requires full isolation (compliance, data residency, portability SLA). Not implemented yet — built when first customer requires it.

Both tiers use the same TenantConnectionService abstraction — the provisioning service decides whether to create a schema or a database.

## Options Considered

N/A

## Consequences

N/A
