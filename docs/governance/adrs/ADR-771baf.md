---
uid: DEC-771baf
title: "Tenant Database Architecture — 4 schemas, platform→tenant one-way dependency, all contracts platform-owned"
description: "Tenant DB has 4 schemas (boundary, record, evidence, operational). Platform owns ALL contracts. Tenant owns ALL data. Platform never contacts tenant DB. Discovery is platform-only."
status: implemented
subdomain: tenant-topology
focus: ddl
date: 2026-03-30
project: bc-docs
domain: tenants
authority: authoritative
migrated_from: legacy v2 archive
---


# Tenant Database Architecture — 4 schemas, platform→tenant one-way dependency, all contracts platform-owned

## Context

Tenant contract storage was considered (Pattern D) but rejected as a band-aid — it duplicates the definition source of truth. The principle "contracts are definitions, data is instances" resolves all cases including tenant-specific Z-tables. Platform never contacts tenant DB enforces clean security boundary.

## Context

The tenant database (`tbc_{slug}_dev`) stores execution-time data for each tenant. The platform database (`bc_platform_dev`) stores all design-time definitions. A clear separation is needed to enforce security boundaries, data residency, and architectural clarity.

Key constraints discovered during D230 documentation audit:
1. Platform services must NEVER write to tenant databases (one-way dependency)
2. ALL contract definitions are platform property — including contracts for tenant-specific source objects (Z-tables, custom objects)
3. Business data is the tenant's property — SO, CO, MO, AO, evidence
4. Discovery is a platform activity (enriches source catalog), not a tenant activity
5. Contract-typed payload tables (D210) will create dynamic tables in tenant DB, requiring a dedicated schema

## Decision

### Principle: Contracts are platform. Data is tenant.

A contract is a DEFINITION (class). Data is an INSTANCE (object). Definitions belong to the platform regardless of how many tenants use them. Instances belong to the tenant that produced them.

Tenant-specific source objects (SAP Z-tables, Salesforce custom objects) are contracted in the platform. The contract is platform knowledge ("this table exists and has this schema"). The data extracted from it is tenant property. Visibility is controlled via `tenant.contract_binding`.

### Tenant DB: 4 schemas

```
tbc_{slug}_dev/
  boundary/      — Execution envelopes (FIXED, ~13 tables)
                   observed_record, source_object, admitted_record,
                   evaluation, canonical_object,
                   metric_evaluation, metric_snapshot,
                   action_object, action_evaluation,
                   admission_run, canonical_run, metric_run, action_run

  record/        — Typed business data (DYNAMIC, managed by Schema Provisioner)
                   Tables created per activated contract:
                   so_bkpf_v1, co_journal_entry_v1, ms_dpo_v1, etc.
                   Covers ALL object types: SO, CO, MO, AO, evidence detail

  evidence/      — Provenance envelopes (FIXED, 3 tables)
                   evidence_object, evidence_record, lineage_object

  operational/   — Tenant operations (FIXED, ~8 tables)
                   connection, connection_config, connection_check,
                   goal, users, activity_log, intervention_definition
                   NO discovery tables (discovery is platform-only)
```

### One-way dependency

```
Platform ──X──► Tenant DB    (FORBIDDEN)
Tenant   ────► Platform API  (reads contract definitions)
Tenant   ────► Tenant DB     (writes own data)
```

### Service responsibilities

| Service | Runs In | Reads From | Writes To |
|---------|---------|------------|-----------|
| Discovery Scanner | Platform | Source systems | Platform operations.discovery_* |
| Contract Creator | Platform | Platform operations | Platform contract.* |
| Contract Binder | Platform | Platform contract | Platform tenant.contract_binding |
| Schema Provisioner | Tenant | Platform API (contracts + bindings) | Tenant record.* (DDL) |
| Boundary Executor | Tenant | Platform API (contracts) + source systems | Tenant boundary.* + record.* + evidence.* |

### Discovery flow for tenant-specific objects

1. Platform Discovery Scanner scans tenant's source system → writes to platform `operations.discovery_*`
2. User reviews discoveries in bc-admin (platform UI)
3. User says "contract this" → platform creates contracts + binding
4. Tenant Schema Provisioner detects new binding → creates typed tables in tenant `record` schema
5. Tenant Boundary Executor runs → reads contract from platform API → writes data to tenant DB

### Why `record` schema is separate

The `record` schema holds the enterprise's actual business data. It:
- Grows explosively (100+ tables per tenant, millions of rows)
- Is subject to data residency laws (GDPR, DPDP, SOX)
- Needs independent backup/restore granularity
- Has different access control (role-gated per business domain)
- Has different performance profile (read-heavy queries vs write-heavy boundary execution)
- Is managed by Schema Provisioner (dynamic DDL), not static migrations

### Contract binding and overrides

`tenant.contract_binding` in platform DB controls which contracts a tenant uses. `override_json` on the binding allows tenant-specific parameterization (e.g., threshold values) without duplicating the contract definition. Runtime merges: `effectiveContract = merge(platformContract, binding.override_json)`.


## Options Considered

N/A

## Consequences

- Remove discovery tables from tenant DDL (03-tenant-db.sql)
- Add empty `record` schema to tenant DDL
- Schema Provisioner is a tenant-side service (not platform)
- Platform API must expose contract read endpoints for tenant services
- D054 Pattern A/B/C unchanged — all patterns store contracts in platform only
- No "Pattern D" needed — tenant-originated contracts still go to platform
