---
uid: DEC-2c79c8
title: "Full per-tenant SQL isolation — all boundary + evidence tables move to tenant schemas"
description: "All 12 boundary tables and 3 evidence tables move from shared schema into per-tenant t_{slug} schemas"
status: implemented
subdomain: tenant-topology
focus: schema
date: 2026-03-17
project: bc-admin
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Full per-tenant SQL isolation — all boundary + evidence tables move to tenant schemas

## Context

All boundary and evidence data is tenant-scoped by origin (reader → connection → tenant). Keeping it in shared schemas with optional tenantId filtering is a data isolation risk. Full schema isolation aligns with ISO 27001 A.8.11 (data masking/segregation) and the existing schema-per-tenant architecture (D081, DEC-f82a8a).

## Decision

All 12 boundary tables and all 3 evidence tables move into per-tenant schemas (`t_{slug}`). No boundary/evidence data remains in the shared schema.

### Rationale
Every record in the execution chain originates from a tenant's connection → reader → contract. Observed records, source objects, and evidence are tenant data — the absence of tenantId on some tables was an implementation gap, not an architectural truth. Evidence hash-chains are already naturally partitioned by subjectRef (which traces to tenant-scoped objects).

### What moves to `t_{slug}`

**Boundary (9 tables):**
observed_record, source_object, admitted_record, evaluation, canonical_object, metric_evaluation, metric_snapshot, action_object, action_evaluation

**Evidence (3 tables):**
evidence_object, evidence_record, lineage_object

### Schema changes required
- Add `tenantId` (NOT NULL) to: observed_record, source_object, action_evaluation
- Make existing nullable `tenantId` NOT NULL on: admitted_record, evaluation, canonical_object, metric_evaluation, metric_snapshot, action_object

### Connection architecture change
- DataPlaneProvider (shared pool) → eliminated
- All boundary/evidence queries route through TenantConnectionService (per-tenant pools)
- Each tenant schema gets boundary + evidence tables via tenant migration

### Platform aggregation
- bc-admin cross-tenant stats (countSnapshotsByContract, etc.) served by a lightweight rollup mechanism in the registry schema, updated at each boundary crossing — NOT by querying across tenant schemas

### Supersedes
- Partially supersedes SES-e17d56 blast radius recommendation (which said "partial move only")
- Extends DEC-d7c1dd (hybrid isolation) — this is the standard-tier implementation

## Options Considered

N/A

## Consequences

N/A
