---
uid: DEC-faef79
title: "Customer data isolation — data plane architecture"
description: "Hybrid model: shared registry/control plane, isolated data plane per tenant. Boundary data (SOs, COs, metrics, evidence) is tenant-isolated."
status: implemented
subdomain: tenant-isolation
focus: hybrid-model-foundational
date: 2026-03-02
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Customer data isolation — data plane architecture

## Context

DECIDED (direction, detail deferred): Hybrid model — shared registry/control plane, isolated data plane per tenant. Contracts, taxonomy, and platform metadata are shared. Boundary data (SOs, COs, metrics, AOs, evidence) is tenant-isolated. Exact isolation mechanism (schema-per-tenant vs DB-per-tenant vs row-level with RLS) to be determined in a dedicated session before multi-tenant production. Does not affect current single-tenant development — tenant_id column filtering is sufficient for now.

## Decision

How is customer (tenant) data isolated in the data plane? Current model uses tenant_id columns with row-level filtering. Need to decide: (1) shared schema + tenant_id filtering (current), (2) schema-per-tenant in same DB, (3) database-per-tenant, (4) hybrid — shared registry/metadata, isolated boundary data. This affects security posture, compliance (SOX, data residency), performance isolation, and operational cost.

## Options Considered

N/A

## Consequences

N/A
