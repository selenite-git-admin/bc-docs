---
uid: DEC-5fa096
title: "Landscape vs Catalog: superset/subset with promotion-approval workflow"
description: "Landscape is the full universe, Catalog is the registered subset. Objects/fields promoted via approval workflow. Superseded by D091."
status: superseded
date: 2026-03-18
project: bc-core
domain: database
authority: retired
migrated_from: legacy v2 archive
---


# Landscape vs Catalog: superset/subset with promotion-approval workflow

## Context

Superseded by D091 (DEC-05140c). Landscape/Catalog duality replaced by unified Source Catalog with status-driven approval.

**Landscape** is the universe — everything that exists externally. **Catalog** is the subset registered/available in BareCount.

## Identity rules by tier:
- **Providers + Systems** — identical in both Landscape and Catalog. No validation required at these levels.
- **Modules** — can be validated with deep research. Present in both.
- **Objects (tables + views) + Fields** — must be **promoted** from Landscape → Catalog individually via a promotion-approval workflow.

## Promotion-approval workflow:
1. Object/field is promoted from Landscape to Catalog as **Review Pending**.
2. SME confirms validity and **approves**. Only approved objects proceed further.
3. Not all objects of a module need approval at the same time — individual promotion.
4. Same for fields — individual promotion per field.

## Contract auto-creation on approval:
- For the 6-tier chain (pivoted on object): when an object is approved, **source + admission contracts can be auto-created** subject to their meta-schema.
- When new fields are added to an approved object → same promotion-approval process → **minor version bump** (MAJOR.MINOR.PATCH per contract-registry.md).

## Current state (issues):
- Both Landscape and Catalog pages have grown organically into something conflicting with this model.
- Contracts are ill-formed (known — TSK-d73148).
- Some canonical and metric contracts are already active/tested — must be preserved carefully.
- This is a careful rework, not a clean-slate rebuild.

## Consequences

N/A
