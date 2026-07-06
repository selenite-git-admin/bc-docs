---
uid: DEC-40c29f
title: "Control Plane / Data Plane DB Split — Registry to Platform, Boundary+Evidence to Tenant"
description: "Platform DB holds registry/contract tables (control plane). Tenant DB holds boundary+evidence data (data plane)"
status: implemented
subdomain: tenant-topology
focus: ddl
date: 2026-03-15
project: bc-admin
domain: database
refs:
  - type: decision
    label: "D022"
  - type: decision
    label: "D020"
  - type: decision
    label: "D072"
authority: authoritative
migrated_from: legacy v2 archive
---


# Control Plane / Data Plane DB Split — Registry to Platform, Boundary+Evidence to Tenant

## Context

Founder decision: fix it now (option A). Design for AWS deployment from day one so the runtime sprint builds on the correct topology. If built against wrong DB layout, AWS migration later is a full rewrite of every database call. Getting topology right now means AWS deployment is just infrastructure — no code changes.

## Decision (DECIDED — supersedes proposed version)

Split bc-core database into control plane (platform) and data plane (tenant) scopes. Design for AWS deployment topology from day one.


## Options Considered

N/A

## Target Schema Layout

### Platform DB (Control Plane — shared, single instance)
- `public` — tenants, audit_log, idempotency_keys
- `platform` — master_domain, master_subdomain, master_currency, master_country, master_status, library
- `registry` — contract, contract_version, approval, lineage_edge, connector, connection, reader, flavor, source_catalog (provider, system, version, module, object, field), source_reference, discovery, kpi_spec, metric_binding, metric_reference, standard_field, mapping_binding (platform templates)

### Tenant DB (Data Plane — per tenant, isolated)
- `boundary` — observed_record, source_object, admitted_record, evaluation, canonical_object, metric_evaluation, metric_snapshot, action_evaluation, action_object
- `evidence` — evidence_object, evidence_record, lineage_object
- `tenant` — users, tenant_override, tenant_binding, mapping_binding (tenant-specific overrides)

## Connection Pattern
- `platform-connection.ts` → public + platform + registry schemas (single shared connection pool)
- `tenant-connection.ts` → boundary + evidence + tenant schemas (per-tenant connection pool via search_path)
- Registry services → platform connection
- Boundary services → tenant connection
- Evidence services → tenant connection

## AWS Target Topology
- Platform DB: One RDS PostgreSQL instance (shared across all tenants)
- Tenant DB: Schema-per-tenant in shared RDS (SMB) or dedicated RDS per tenant (enterprise)
- bc-core: ECS Fargate, single service, two DB connection configs
- bc-admin/bc-portal: S3 + CloudFront (static SPAs)

## Migration Approach
1. Restructure Drizzle schema files to match control/data plane split
2. Update DrizzleProvider to expose platform connection explicitly
3. Update TenantConnectionService to handle boundary + evidence schemas
4. Update all registry services to use platform connection
5. Update all boundary/evidence services to use tenant connection
6. Migration script: move existing data if needed (currently single DB, schema reorganization)
7. Verify all endpoints via test suite

## Alignment
- D022: Shared registry + control plane, isolated boundary data
- D020: Keep monolith, split at DB level not service level
- D072: Single service, guard decorators for scope enforcement
- Tenancy architecture docs: Hybrid model (shared control plane, isolated data plane)

## Consequences

N/A
