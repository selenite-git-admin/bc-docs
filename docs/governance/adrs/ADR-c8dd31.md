---
uid: DEC-c8dd31
title: "Reference-to-Source Catalog promotion — governed copy with draft status"
description: "Promotion from Reference Landscape to Source Catalog is a governed platform-team action. Two entry paths (known systems, tenant tickets) both land in draft."
status: implemented
subdomain: source-catalog
focus: promotion-flow
date: 2026-03-10
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Reference-to-Source Catalog promotion — governed copy with draft status

## Context

Copy ensures the source catalog has a locked version suitable for contract authoring — contracts reference a stable schema. Draft status prevents premature contracting against unreviewed objects. Platform-team-only governance prevents uncontrolled catalog growth.

**Two entry paths into Source Catalog (both governed, both land in draft):**

**Path 1 — Known systems (default):** Reference Landscape → promote (platform team, copy, fields > 0) → Source Catalog (draft) → expert review/approve → active. For SAP tables, Salesforce standard objects, ECB datasets, etc.

**Path 2 — Tenant-specific objects (ticket-driven):** Tenant raises ticket → platform team creates entry with tenant metadata → Source Catalog (draft) → expert review/approve → active. For custom SAP Z-tables, custom Salesforce objects, proprietary systems. Not in any reference catalog.

Both paths converge at Source Catalog (draft). Everything downstream (source contracts, reader binding, admission) is identical regardless of entry path. Future Phase 2/3: discovery (reader probes connected system, finds custom objects) could automate Path 2, but governance gate (draft → review → approve) stays.

## Decision

**Promotion** from Reference Landscape to Source Catalog is a governed platform team action:

- **Who:** Platform team only. Not tenant admins.
- **Precondition:** Object must have fields > 0 in the reference catalog.
- **Result:** Creates Source Catalog entries (Provider → System → Version → Module → Object → Fields) in **draft** status. An expert must review and approve before the object is active.
- **Mechanism:** Copy, not link. Source catalog owns its data — locked snapshot at promotion time. Reference catalog updates (e.g., new SAP version adds a field) do NOT propagate automatically. That's a new version in the source catalog.
- **Post-promotion:** Object is eligible for source contract creation (ObjectContractChain), reader binding, and admission contracting — but only after review/approval moves it out of draft.

## Options Considered

N/A

## Consequences

N/A
