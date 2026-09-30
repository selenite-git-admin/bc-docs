---
uid: DEC-c562d5
title: "Canonical bc-portal design: Dashboard and Workspace, with the Rooth canvas as its metric view"
description: "Of three incomplete bc-portal iterations, Dashboard/Workspace (surfaces/) is canonical; the Rooth canvas stays as its metric view; the Feb 2026 card-library generation is retired"
status: decided
date: 2026-09-30T10:28:47.692Z
project: bc-portal
domain: bc-portal
subdomain: bc-portal
focus: information-architecture
supersedes:
  - DEC-7e76b9
  - DEC-6cdceb
---

# Canonical bc-portal design: Dashboard and Workspace, with the Rooth canvas as its metric view

## Context

The Frontend Experience chapter recorded three incomplete bc-portal iterations with no canonical one. It could not leave stub status, and the Portal UI program (PLN-0527db) had no fixed target.

Why Dashboard and Workspace:
- It is what every customer sees first. `DashboardEntry.tsx` renders it unless `?mode=rooth` is set.
- It is the only design with a home for setup and data connections.
- The code has followed it since 2026-07-09 (`surfaces/SURFACE_MAP.md`, "Design Phase 1 is locked").

Why the Rooth canvas stays: it is the part that already reads governed metric values (DEC-a1290e). Keeping it as the dashboard's metric view preserves that without a rebuild.

Why the February generation is retired: it has no route and no importer.

Why the April ADRs are superseded: D360 and D361 were marked implemented, but the code diverged from them in July without a superseding record. This ADR closes that gap.

The comparison page presented to the operator: https://claude.ai/artifact/L2hZCkoh7WpuPFfh4ED3c4. The evidence is bc-portal b018178 and DevHub sessions SES-09e85f and SES-ad5b5b.

## Decision

The operator chose "Dashboard and Workspace" on 2026-09-30 (about 10:35Z, in chat with the Chief controller, who relayed it to the Customer Portal controller). This choice was Decision 6 in the controller charters.

1. **Canonical design.** The Dashboard and Workspace design (bc-portal `apps/web/src/surfaces/`, from 2026-07-08) is the canonical bc-portal design:
   - `/dashboard` is where a customer lands and reads their numbers;
   - `/workspace/*` holds tenant setup and governance: organisation, users and access, data connections, readers and datasets, the metric list, and the governance pages;
   - `/profile`, `/search`, `/help`, `/alerts` and `/support` are ordinary pages in the same shell.
2. **The Rooth canvas.** The canvas (`pages/beyond/`, `components/beyond/`, from 2026-04-19) is not a rival surface. It stays as the metric view inside the dashboard: `/dashboard?mode=rooth` and `/dashboard/metric/:mcUid`. Every governed metric link opens there. `/beyond` remains a redirect.
3. **The first iteration is retired.** The card-library dashboards from February 2026 are retired formally: `components/{card-library,widgets,kpi,kpis,kpi-visuals,cards,charts,dashboards,interventions}` (58 files, which no live surface imports) and their only dependant, `utils/kpiSimulationEngine.ts`. They move to the dated archive folder under `apps/web/src/_archived/` in a separate reviewed change.
4. **Supersedes DEC-7e76b9 (D360),** "a single Beyond surface, no dashboard". It also supersedes **DEC-6cdceb (D361)**, the three-surface split `/beyond`, `/settings/workspace` and `/settings/data-infra`. In its place is the two-family shell: Dashboard (reading, with the canvas as the metric view) and Workspace (setup, including data). D361's category logic still holds: reading and provenance on the dashboard side, forms and tables in Workspace, with no standalone canonical-data, evidence or lineage browsers.
5. **Unchanged.** DEC-2cf250 (D362, the visual language) is not affected. The display rule holds on every page: only governed tenant values are shown as real, and anything else is removed or labelled.
