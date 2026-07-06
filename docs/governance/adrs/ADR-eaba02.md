---
uid: DEC-eaba02
title: "Validation Status — Tenant-Scoped Execution Proof for Catalog Objects"
description: "Add 'validated' status meaning a reader actually found the object in a live system. Tenant-scoped via separate object_validation table."
status: implemented
subdomain: validation-lifecycle
focus: tenant-validation-proof
date: 2026-03-22
project: platform
domain: database
authority: evolving
migrated_from: legacy v2 archive
---


# Validation Status — Tenant-Scoped Execution Proof for Catalog Objects

## Context

The current catalog lifecycle (registered→approved) is belief-based — seeded from vendor docs, confirmed by AI. But the ultimate proof is execution: did a UinBAT Reader actually find this table/entity in a live system? This distinction matters for: (1) customer confidence — showing validated counts proves real coverage, (2) gap analysis — identifying objects that exist in docs but not in their system, (3) tenant scoping — SAP ECC at MegaCorp may have PM module, SmallCo may not.

## Decision

Add a `validated` status to the catalog verification lifecycle. Unlike `registered` (seeded from docs) and `approved` (AI + human confirmed), `validated` means a reader actually connected to a live system and found the object. Validation is tenant-scoped — different tenants have different system configurations. Proposed: separate `source.object_validation` table with tenant_id, validated_at, validated_by (reader/connection), field_count_found, evidence_json. Platform catalog stays registered→approved (universal). Tenant validation records which objects exist per customer.

## Options Considered

N/A

## Consequences

N/A
