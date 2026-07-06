---
uid: DEC-4ca5a5
title: "Metric Landscape — single-page UI consolidation of three overlapping metric-lifecycle surfaces"
description: "Consolidates the bc-admin Lifecycle Funnel (Platform tab + Tenant tab) and Tenant Metrics pages into one canonical page at /catalog/metrics/landscape that mirrors the 7-stage canonical lifecycle ladder from DEC-a8b33e. Old routes redirect for one compatibility release. All counts read from MetricFunnelService.getLadder()."
status: decided
date: 2026-05-09T09:32:24.132Z
project: bc-admin
domain: metrics
subdomain: lifecycle-funnel
focus: ui
---

# Metric Landscape — single-page UI consolidation of three overlapping metric-lifecycle surfaces

## Context

Today bc-admin has three overlapping surfaces that each compute and display metric-lifecycle counts using divergent vocabularies: /catalog/metrics/funnel (Platform tab) uses MLS-frame names like Seeded/Registered/Classified/Contracted/Chain-Complete/Ready; /catalog/metrics/funnel (Tenant tab) uses MLS-19..25 stages (Contract bound/Fact tables ready/Source admitted/Canonical produced/Snapshot produced/Proof complete/KPI rendered); /catalog/metrics/tenant-metrics shows Catalog ready/Bound/Pilot health dials. The vocabularies overlap, the numbers don't always reconcile (the bound dial famously broke as 211 of 164 catalog-ready), and operators have to context-switch between three pages to answer 'where in its lifecycle is this metric for this tenant?'. DEC-a8b33e (D397) locked the canonical 7-stage ladder + MetricFunnelService.getLadder() as the truth source. This ADR consolidates the UI surface to match.

## The page

Single page at `/catalog/metrics/landscape` showing the canonical 7-stage funnel from DEC-a8b33e in one downward scroll. Platform stages (1–4) and Tenant stages (5–7) appear in the same flow, separated by a tenant selector. The narrative is Seed → Contracted → Active → Platform Ready → Tenant Ready → Tenant Evaluated → Live — one ladder, not two.

### Layout (top to bottom)

1. **Platform funnel** — 4 stage cards in horizontal flow (Seed → Contracted → Active → Platform Ready), with stage drops listed below as named side buckets (`contracting_backlog`, `draft_only_contracts`, `chain_incomplete`, `audit_failed`, `formula_unsupported`, `semantic_not_evaluated`, `semantic_failed`). Off-funnel `orphan_contracts` shown as separate small chip.

2. **Tenant selector + Tenant funnel** — 3 stage cards (Tenant Ready → Tenant Evaluated → Live) with side bucket drops (`stale_bindings`, `dispatch_gap`, `data_freshness_gap`).

3. **Metrics detail table** — DataTable with filters (Function, Subfunction, Stage, Drop bucket). Replaces the old per-MC table from tenant-metrics.

4. **Off-funnel collapsibles** — Catalog authoring (D283), Post-live surface checks (MLS-24/25), Recent transitions, Gate pass rates (D315). All real governance views; demoted from competing-with-the-ladder to clearly-named off-funnel diagnostics.

No Platform/Tenant tabs. The whole point is showing the ladder as one flow. If length becomes an issue, sticky anchor-link mini-nav is the remedy — not tabs.

## The three locks

### 1. Read from MetricFunnelService.getLadder() — no legacy reads

All cards, all stage counts, all side bucket counts, all detail-table filters MUST source from `GET /api/admin/registry/funnel-ladder` (DEC-a8b33e implementation step 2). Direct calls to `/api/admin/readiness/catalog`, `/api/admin/readiness/tenant`, `/api/admin/tenant-metrics/snapshot`, `/api/registry/metric-readiness/funnel` are forbidden in the new page. Those endpoints continue to exist (other consumers, backward compatibility) but the Landscape page does not consume them.

The detail table's row data still comes from a per-row endpoint (e.g. the existing tenant-metrics snapshot or a future replacement); the count totals in headers and filter chips read from getLadder().

### 2. Old routes redirect for one compatibility release

`/catalog/metrics/funnel` and `/catalog/metrics/tenant-metrics` are NOT removed in the same release that ships Landscape. They redirect to `/catalog/metrics/landscape` for one full release cycle. After that release, they 404.

The redirect carries any `tenant=...` query parameter forward so deep-links continue to work.

This grace period gives external bookmarks, internal docs, and any third-party automation time to update without a hard break.

### 3. Stage cards are clickable filters for the detail table

Clicking a stage card scrolls the page to the detail table and applies a Stage filter equal to that stage. Clicking a side bucket chip applies a Drop bucket filter (e.g. clicking `stale_bindings` filters the table to MCs that are bound but not platform-ready).

The old "Show producing only" toggle on tenant-metrics retires — that's now `Stage = Live` in the detail table filter.

## What retires (with grace period)

- `/catalog/metrics/funnel` route (Lifecycle Funnel page) — redirected, then removed.
- `/catalog/metrics/tenant-metrics` route (Tenant Metrics page) — redirected, then removed.
- MLS-frame stage names in UI: "Registered", "Classified", "Contract bound", "Fact tables ready", "Source admitted", "Canonical produced", "Snapshot produced", "Proof complete", "KPI rendered". The MLS state codes continue to live in the audit substrate (DEC-e7b7b3 / D392); they stop being top-level UI labels.
- "Catalog ready / Bound / Pilot health" dials. Numbers and meaning fold into the canonical stage cards (Platform Ready / Tenant Ready / Live respectively).
- "Show producing only" toggle on tenant-metrics. Becomes a Stage filter on the detail table.

## What survives

- The detail-table column structure (per-MC drill, sortable, paginated).
- Recent transitions (audit log; collapsible).
- D283 catalog authoring discipline view (5D / maturity funnel / gate pass rates) — collapsibles, off-funnel.
- Function/subfunction/tenant filters.
- Refresh button.

## Cross-references

- **IMPLEMENTS DEC-a8b33e** (D397 Metric Lifecycle Funnel canonical 7-stage ladder). This is the UI manifestation; data model + service ownership stay in that ADR.
- **AMENDS the implementation order** in DEC-a8b33e Section "Implementation order" — step 6 ("bc-admin UI label alignment") is replaced by this ADR's full consolidation plan.
- **AMENDS DEC-28b176** (D394 Readiness Toolkit Dials) further. The three dials retire as separate UI surface; their semantics survive as the Platform Ready / Tenant Ready / Live stage cards.
- **EXTENDS D316 Readiness Funnel** scope — the cumulative funnel at /catalog/metrics/funnel retires; D316's MetricReadinessService.computeCumulativeFunnel becomes a backend projection over getLadder() (DEC-a8b33e implementation step 5).

## Implementation order (subsequent sessions)

1. This ADR (decided on file).
2. Build `MetricLandscapePage.tsx` consuming `getLadder()`. New route `/catalog/metrics/landscape`. New nav entry. No URL collision with the existing pages.
3. Wire stage card clicks to detail table filters. Wire side bucket chip clicks similarly.
4. Add redirects from `/catalog/metrics/funnel` and `/catalog/metrics/tenant-metrics` to `/catalog/metrics/landscape` (preserving query params).
5. Remove the old pages from the nav (LeftSidebar / TopNavbar). The redirects keep deep links working.
6. After one compatibility release, replace the redirects with 404s and delete the old page components.

## Consequences

- Operators stop context-switching between three pages for the same question.
- Numbers across the page are guaranteed consistent by construction (single API source).
- The MLS-frame vocabulary that confuses operators retires from the UI; the MLS substrate keeps its detailed state machine for audit purposes.
- Old deep-links continue to work for one release.
- bc-admin loses one route + one component (the Funnel page was ~1000 lines; Landscape composes the same primitives more cleanly).

## Open follow-ups (not gating this ADR)

- Future TenantMetricsService.getSnapshot retirement (or migration to project from getLadder()) — DEC-a8b33e implementation step 4.
- D391/D392 verdict-writer ships → Stage 4 MLS-14 enforcement mode flips from observe-only to strict.
- bc-portal may need a parallel consolidation pass when its metric-lifecycle surfaces mature.
