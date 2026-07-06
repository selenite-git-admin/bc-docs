---
uid: DEC-5cef91
title: "Navigation IA v5 — Final locked structure (AUTHORITATIVE)"
description: "Final locked nav: Source Catalog (2), Readers (3), Canonical Map (4), Metric Chain (4), Operations, Platform. Supersedes all prior IA decisions."
status: implemented
subdomain: navigation-ia
focus: bc-admin-nav
date: 2026-03-14
project: platform
domain: database
refs:
  - type: decision
    label: "D049"
  - type: decision
    label: "D059"
  - type: decision
    label: "D060"
  - type: decision
    label: "D061"
  - type: decision
    label: "D062"
  - type: decision
    label: "D067"
  - type: decision
    label: "D055"
authority: authoritative
migrated_from: legacy v2 archive
---


# Navigation IA v5 — Final locked structure (AUTHORITATIVE)

## Context

Multiple sessions of discussion revealed architectural misalignments in prior IA versions. Key insights: (1) Extraction + Admission contracts are Reader-scoped per the foundation spec — showing them under Source Catalog was a category error. (2) Source Objects are Reader output — a standalone SO page forces users to mentally reconnect things that are naturally together on the Reader detail page. (3) The three contract types (Extraction, Source, Admission) aren't even the same scope — Extraction and Admission are Reader-scoped, Source is SO-scoped — so grouping them as a triplet in nav was architecturally wrong. (4) Grouping contracts by provider was wrong because Readers are business-object-centric (ar-invoice-reader), not provider-centric (SAP contracts). This decision is FINAL and AUTHORITATIVE — all prior IA decisions are superseded.

Supersedes ALL prior IA decisions: D049, D059, D060 (IA v3), D061, D062 (SO contracts), D067 (IA v4).

## Final Locked Navigation Structure

**Source Catalog** (2 items — passive inventory):
1. Source Landscape — per-source reference indexes (SAP tables, CDS views, etc.)
2. Source Catalog — all providers, single page with category filter chips (Enterprise/Third Party/Public/Synthetic). Defaults to Enterprise + ERP selected on load.

**Source Chain** (2 items — active execution):
1. Connectors — adapter registry
2. Readers — UinBAT reader definitions

**Canonical Map** (3 items — wiring layer, CO at center):
1. Canonical Objects — CO definitions
2. Field Bindings — SO→CO field mapping
3. Metric Bindings — CO→MO metric binding

**Metric Chain** (2 items — metric-specific):
1. Metric References — reference data
2. Metric Objects — MO definitions

## What was REMOVED from nav and WHY

**Source Contracts** — REMOVED. Extraction and Admission contracts are Reader-scoped (per D055). Source Contract is 1:1 per SO. Grouping by provider was architecturally wrong because (a) Readers are business-object-centric not provider-centric, (b) SAP SE has 8 systems — "SAP SE contracts" is meaningless, (c) the same Reader serves multiple providers via flavors. Contracts surface from **Reader detail page** where they architecturally belong.

**Source Objects** — REMOVED from standalone nav. SOs are the output of Readers. Every SO is produced by a specific Reader via a specific flavor. SOs surface from the **Reader detail page** showing what the reader has produced. No standalone SO listing page needed.

**Contracts column** — REMOVED from source system detail page object table. Contracts are Reader-scoped, not source-scoped. The object table shows: Object/Field, Type, Fields, Status. No contracts column.

## Architectural principles enforced

1. Contracts live with their architectural owner (Reader detail page), not in standalone nav
2. Source Objects are Reader output — surface from Reader, not as independent nav
3. No duplication — source detail page already has module→object→field drill-down
4. CO Map visualization belongs on CO detail page as a section, not standalone nav
5. Consistent naming: Field Bindings + Metric Bindings (allowed vocabulary: "bind")
6. Each group is lean (2-3 items) and architecturally honest — no padding

## Consequences

N/A
