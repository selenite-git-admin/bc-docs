---
uid: DEC-1b32a9
title: "Canonical contracts are source-agnostic — not part of Source Chain"
description: "Corrects D022: canonical contracts are source-agnostic, bridging Source Chain and Metric Chain but belonging to neither."
status: implemented
subdomain: contract-primitive
focus: vocabulary
date: 2026-03-09
project: platform
domain: database
refs:
  - type: decision
    label: "D022"
  - type: decision
    label: "D044"
authority: authoritative
migrated_from: legacy v2 archive
---


# Canonical contracts are source-agnostic — not part of Source Chain

## Context

D022 placed canonical in Source Chain (extraction → source → admission → canonical). But D044 already split canonical into universal contract (source-agnostic) and tenant-scoped mapping binding (source-specific). Keeping canonical in Source Chain contradicts its source-agnostic nature and the D044 split.

## Decision

Corrects D022's chain model. Canonical contracts are source-agnostic and do not belong to the Source Chain.

Revised chain model:
- Source Chain: extraction → source → admission (source-bound, admits SOs)
- Canonical: standalone, source-agnostic (defines CO shape, universal business vocabulary)
- Metric Chain: metric → intervention (CO-bound, computes KPIs)
- AI Chain: ai (CO + metric bound, intelligence)

Canonical is the bridge between Source Chain and Metric Chain but belongs to neither. A canonical contract defines "what does a Vendor Invoice CO look like" regardless of whether data comes from SAP, SFDC, or Oracle. The mapping binding (D044, tenant-scoped) bridges source to canonical.

This aligns with Data Object Model §100: COs are "domain-scoped, referentially stable" and "do not reference raw source systems."

## Options Considered

N/A

## Consequences

N/A
