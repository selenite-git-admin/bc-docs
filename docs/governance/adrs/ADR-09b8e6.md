---
uid: DEC-09b8e6
title: "Unified Source Catalog — status-driven 6-tier hierarchy with object/view support"
description: "Provider-System-Version-Module-Object-Field hierarchy with CSV seed manifests. 245K+ objects seeded from scraper output."
status: implemented
subdomain: source-catalog
focus: unified-6-tier
date: 2026-03-18
project: bc-core
domain: database
refs:
  - type: decision
    label: "D091"
  - type: decision
    label: "D019"
authority: authoritative
migrated_from: legacy v2 archive
---


# Unified Source Catalog — status-driven 6-tier hierarchy with object/view support

## Context

Original rationale plus:

## Seed System (part of D091)
CSV manifests + runner, not JSON. JSON too bulky for 245K+ objects.

**Structure:**
- Small tiers (Provider→Module): hand-maintained CSV, git-tracked, PR-reviewable
- Large tiers (Object, Field): generated from scraper output, uniform D091 shape only — no provider-specific columns
- Masters (domains, currencies, countries): separate CSVs

**Manifest layout:**
```
seed/manifests/{providers,systems,versions,modules}.csv  — hand-maintained
seed/manifests/objects.csv — generated, 245K rows
seed/manifests/fields.csv — generated, large
seed/masters/{domains,currencies,countries}.csv
seed/runner.ts — orchestrator, reads CSV, upserts in FK order
```

**FK resolution:** composite lookup key in CSV (e.g. `sap:s4hana:on-premise-2023:FI`) resolved to UUID at runtime. No UUIDs in seed files.

**Commands:** `npm run seed` (full), `npm run seed:masters`, `npm run seed:catalog`, `npm run seed:catalog:objects`

**Idempotency:** UPSERT on natural unique keys, never by UUID. Run 10 times, same result.

## D091: Unified Source Catalog

### Core Principle
One catalog, not two. Drop the Landscape/Catalog split. Every member of the 6-tier hierarchy lives in the Source Catalog. The difference between "known" and "verified" is **status**, not location.

### 6-Tier Hierarchy (unchanged)
```
Provider → System → Module → Object → Field
```
(Version sits between System and Module per existing D019 design.)

### Status Lifecycle — every tier member
```
registered → approved → deregistered
```
- **Providers, Systems**: seeded as `approved` (verifiably exist — SAP SE, Salesforce, ECB)
- **Modules, Objects, Fields**: seeded as `registered` (known from reference data, not yet validated)
- **Only `approved` members** are eligible for contract creation and bindings
- New fields added to an approved object: enter as `registered`, go through approval, trigger minor version bump on the object

### Scope Attribute — every tier member
```
scope_code: 'platform' | 'tenant'
```
- Platform = universal, applies to all tenants (SAP BKPF, ECB exchange rates)
- Tenant = tenant-specific discovery (custom Z-tables, tenant-specific fields)
- Discovered objects/fields enter the same catalog with `scope = tenant`, `status = registered`
- On approval they stay in catalog — no "move" needed

### Object Type — Tier 5
```
object_type_code: 'table' | 'view'
```
- Views (CDS views, DB views, Oracle views) are first-class objects at Tier 5
- Universal — not SAP-specific. Any system that renders views is covered
- Views may expose fields that overlap with underlying tables — this is a fact about the source, not redundancy

### Uniform Shape
- No provider-specific columns on catalog tables (no `sap_package`, `delivery_class`, etc.)
- All providers follow the same structure — that's the key
- SAP-specific reference data (`sap_table_reference`, `sap_cds_reference`) absorbed into catalog tables; extra columns dropped

### Contract Auto-Creation
When an object is approved, source + admission contracts can be auto-created subject to their meta-schema (6-tier chain pivots on object).

### What This Supersedes
- Separate Landscape pages/routes (`/sources/landscape`) — merged into `/sources/catalog`
- `sap_table_reference` and `sap_cds_reference` as separate tables — absorbed
- The Landscape/Catalog conceptual split

## Consequences

N/A
