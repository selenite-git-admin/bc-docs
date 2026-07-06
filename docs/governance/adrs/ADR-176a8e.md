---
uid: DEC-176a8e
title: "Contracts are platform-only — tenant customization via contract_binding"
description: "Removed tenant_id from all contract families. Contracts are platform templates. Tenants customize via tenant.contract_binding with override_json."
status: implemented
subdomain: tenant-architecture
focus: platform-tenant-split
date: 2026-03-25
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Contracts are platform-only — tenant customization via contract_binding

## Context

Storing full contract copies per tenant (self-ref pattern) scales linearly and duplicates data. Platform owns the contract, tenant owns the delta. contract_binding is lightweight and indexed.

## Decision

Removed tenant_id and platform_master_id from all 5 contract families + business_field + canonical_mapping. Contracts are platform-level templates. Tenants customize via tenant.contract_binding (replaces tenant_override). contract_binding supports all 6 families with override_json for opaque deltas.

## Options Considered

N/A

## Consequences

N/A
