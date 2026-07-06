---
uid: DEC-7e76b9
title: "Retire v2 dashboards entirely — single Beyond surface, no toggle"
description: "v2 dashboard pages (kpi-store, functions, function-admin console) removed in full; no dashboard toggle; Beyond canvas is the single bc-portal surface"
status: implemented
subdomain: bc-portal
focus: dashboard-retirement
date: 2026-04-19T14:23:55.876Z
project: bc-portal
domain: bc-portal
supersedes: DEC-2e801a
migrated_from: legacy v2 archive
---

# Retire v2 dashboards entirely — single Beyond surface, no toggle

## Context

Two reasons to delete rather than toggle:

1. **Product clarity.** A toggle signals "we're not sure" and dilutes the Beyond thesis (DEC-2e801a / D358 locked Beyond as the post-dashboard canvas). Hedging costs more than it buys — v2 was already below the usage bar ("almost non-existing" per user).

2. **Maintenance cost.** The 30 v2 files carry their share of the 331 pre-existing ESLint warnings blocking the --max-warnings 0 hook. Keeping them behind a flag means paying that lint debt forever. Git history preserves v2 — a resurrection is cheap if product ever needs it.

Supersedes the "archive to v2/" step of DEC-2e801a (D358), which was the transitional move; this is the terminal decision.

## Decision

Delete `apps/web/src/pages/v2/` in bc-portal and all references to it (router entries, page-registry, design-system re-exports, nav links). Do NOT add a "I love dashboards" toggle or keep v2 behind a feature flag. /beyond is the single customer-portal surface.

Concretely removed:
- 30 files under `pages/v2/` (kpi-store: 16; functions: 3; admin: 2; tabs: 9)
- 19 lazy imports + 17 route declarations in `components/AppRouter.tsx`
- `KPILogsTab` re-export in `components/design-system/index.ts`
- 13 KPI-store entries in `config/page-registry.ts`
- v2 links in LeftSidebar, Navigation, GlobalSearch, LegacyPagesPage

legacy v2 archive references (7 files) are left for a separate pass — they are historical ADR/SOP content, not live links.
