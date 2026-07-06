---
uid: DEC-ae0d33
title: "Source contracts pivot on SO Detail page, not standalone nav"
description: "Superseded: source contracts were shown on SO detail pages. Later replaced by dedicated Contract Registry nav group."
status: superseded
date: 2026-03-13
project: platform
domain: contracts
refs:
  - type: decision
    label: "D061"
authority: retired
migrated_from: legacy v2 archive
---


# Source contracts pivot on SO Detail page, not standalone nav

## Context

Superseded by D068. Source contracts now surface from Reader detail page (Reader-scoped), not SO detail page. SO detail page also removed from nav — SOs surface from Reader detail.

## Decision

Source-chain contracts (extraction, source, admission) are shown on the SO Detail page as a contract chain triplet, not as a standalone nav item. All 3 contracts are bound to the same source object type — showing them in context makes more sense than a flat contract list. Source Catalog nav has only Source References + Source Landscape (pure passive inventory). Source contracts remain accessible via deep link (/registry/contracts/source-chain) and from SO Detail page click-through to ContractDetailPage. SO Detail page shows: object identity, contract chain (extraction→source→admission with governance status), admission stats, recent observations with evidence. Supersedes D061.

## Options Considered

N/A

## Consequences

N/A
