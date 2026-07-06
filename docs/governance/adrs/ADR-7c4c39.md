---
uid: DEC-7c4c39
title: "Source Catalog Status Lifecycle — 4-state catalog_status"
description: "Every catalog entity uses catalog_status with 4 states: registered, approved, active, deprecated. Approval flows top-down from parent."
status: implemented
subdomain: validation-lifecycle
focus: catalog-status-4-state
date: 2026-03-22
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Source Catalog Status Lifecycle — 4-state catalog_status

## Context

The v1/v2 schema split created 6 conflicting layers (DDL, DB, Drizzle v1, Drizzle v2, API, frontend) with no agreement on status column name or values. This decision establishes a single lifecycle model that works across all 6 source tiers, with clear governance semantics (registered vs approved gate) and standard soft-delete pattern (archived). The 4-state model covers all real scenarios: bulk enrichment (registered), platform review (approved), end-of-life (deprecated), and removal (archived).

## Decision

Every source catalog entity (provider, system, version, module, object, field) uses a `catalog_status` column with exactly 4 states:

1. **registered** — Added to catalog (enrichment, discovery, manual). Not yet cleared for production use. Can create children. Cannot bind contracts or configure readers.

2. **approved** — Platform team reviewed and cleared for production. Can bind contracts, configure readers, create children. Approval flows top-down: parent must be approved before child can be approved.

3. **deprecated** — Phasing out. Existing contracts survive, no new contracts or readers. Cannot create new children. Still visible in UI with warning indicator.

4. **archived** — Soft-deleted. Not visible in UI (admin-only). No contracts, no readers. Cascades down: archiving a parent archives all children.

**Column name:** `catalog_status` (not `status_code` — too generic).

**CHECK constraint:** `CHECK (catalog_status IN ('registered', 'approved', 'deprecated', 'archived'))`

**Cascade rules:**
- `archived` cascades down to all children
- `deprecated` does NOT cascade — children keep their own status
- Approval flows top-down: child cannot be `approved` if parent is only `registered`
- Registration can happen bottom-up (discovery finds objects before parent is reviewed)

**Replaces:** The old `status_code` column with values `draft|planned|active|deprecated` and the never-deployed `catalog_status` with values `registered|approved|deregistered`.

## Options Considered

N/A

## Consequences

N/A
