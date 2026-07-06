---
uid: DEC-d2eeb8
title: "Schema namespace reorganization + table pluralization — sequence with tenant isolation"
description: "Reorganize bc-core schemas from catch-all registry.* into domain-aligned namespaces. Pluralization rejected by D078 — ISO 11179 uses singular."
status: superseded
date: 2026-03-15
project: bc-infra
domain: database
refs:
  - type: decision
    label: "D078"
authority: retired
migrated_from: legacy v2 archive
---


# Schema namespace reorganization + table pluralization — sequence with tenant isolation

## Context

Superseded by D089 (DEC-1918d0) and D078 (DEC-69f09e). Schema reorganization is complete (11 schemas). Table pluralization was explicitly rejected by D078 — ISO 11179 uses singular.

Reorganize bc-core PostgreSQL schema namespaces from the current layout (where `registry.*` is a 30+ table catch-all) into domain-aligned namespaces. Pluralize all table names for D078 compliance. Sequence implementation with tenant DB isolation to avoid migrating tables twice.

## Proposed schema layout

```
platform.*        — masters (domain, currency, country, status, subdomain), library, tenants, audit_log, idempotency_keys
boundary.*        — observed_records, source_objects, admitted_records, evaluations, canonical_objects, metric_evaluations, metric_snapshots, action_objects, action_evaluations
evidence.*        — evidence_objects, evidence_records, lineage_objects
contract.*        — contracts, contract_versions, approvals, lineage_edges, bindings
source.*          — source_providers, source_systems, source_versions, source_modules, source_objects, source_fields, connectors, connections, connection_checks, sap_table_references, sap_cds_references, sap_cds_field_mappings
reader.*          — readers, reader_flavors, reader_bindings, admission_runs
metric.*          — kpi_specs, metric_bindings, metric_references, standard_fields
mapping.*         — mapping_bindings, mapping_binding_versions, tenant_bindings, tenant_overrides
discovery.*       — discovery_scans, discovered_objects, discovered_fields, discovery_diffs
{tenant_schema}.* — users, future tenant-scoped tables
```

## Table pluralization

All table names use plural snake_case per D078 technical naming standard:
- `connector` → `connectors`
- `connection` → `connections`
- `reader` → `readers`
- `contract` → `contracts`
- `evaluation` → `evaluations`
- `binding` → `bindings`
- `approval` → `approvals`
- `library` → `libraries`

Tables already plural remain unchanged: `tenants`, `users`, `idempotency_keys`.

## Scope

- Structural migration: tables move between schemas, all queries and joins update
- Combined with tenant DB isolation planning to avoid double-migration
- D078 (column renames) proceeds independently — no blocking dependency
- Implementation requires a single coordinated migration + all service/repository updates

## Open questions (require discussion)

1. Should connectors/connections live in `source.*` or `reader.*`? (Connectors define source system adapters, connections are instances — arguably source-domain. But readers consume connections — arguably reader-domain.)
2. Should `standard_fields` live in `metric.*` or its own `vocabulary.*` schema? (Standard fields govern observation vocabulary, not just metrics.)
3. Tenant isolation model: separate PostgreSQL schemas (current approach via search_path) vs separate databases vs row-level security? This affects how many schemas we create.
4. Should `platform.*` absorb `public.*` entirely, or keep `public` for truly shared infrastructure (audit, idempotency)?

## Consequences

N/A
