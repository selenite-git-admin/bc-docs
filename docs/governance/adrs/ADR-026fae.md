---
uid: DEC-026fae
decision_code: D350
title: "bc-portal Naming Convention — route equals component equals nav label, no legacy suffixes"
description: "Three-layer naming alignment: route leaf = component filename = nav label. Bans Refined/New/Enhanced suffixes. Canonical vocabulary for all domain sections."
status: superseded
superseded_by: DEC-162de5
subdomain: bc-portal
focus: naming-convention
date: 2026-04-18
project: bc-portal
domain: frontend
refs:
  - type: document
    path: "dev-guides/bc-portal/audit-report-2026-04-18.md"
    label: "bc-portal Audit Report 2026-04-18"
migrated_from: legacy v2 archive
---

# bc-portal Naming Convention (D350)

## Context

The April 2026 audit found bc-portal has been renamed at least twice, leaving three or four naming generations coexisting in source. A single screen touches up to four different name layers:

```
URL path:         /data-sources/registered
Component name:   DataControlsConnectionsPageRefined   ← 2 generations old
Nav label:        "Data Sources"                        ← current
API endpoint:     /api/t/connectors-catalog             ← technical
```

Specific problems:
- `DataControlsConnectionsPageRefined` — "DataControls" is one generation old, "Refined" is an iteration suffix that should not survive a branch merge
- `GoldenDataOverview` — route uses `canonical-data`, component uses abandoned "GoldenData" term
- `CFOPackPage`, `CGOPackPage`, `CMOPackPage`, `COOPackPage` — nav labels are "Finance Metrics", "Sales Metrics" etc. — four different words for the same thing
- `FinancePageB` — "B" iteration suffix in production code
- `FormsDemoPageNew` — "New" suffix in production code
- 72 legacy redirect routes with no restoration tracking

## Decision

### Rule 1 — Three-layer alignment

Every page must have the same name across three layers:

| Layer | Format | Example |
|-------|--------|---------|
| Route path | kebab-case leaf segment | `/data-sources/registered` |
| Component filename | PascalCase + "Page" suffix | `DataSourcesRegisteredPage.tsx` |
| Nav label | Title Case, human-readable | "Registered Sources" |

The route leaf is the canonical anchor. Component name and nav label are derived from it.

**Derivation rule:**
- Route `/foo/bar-baz` → Component `FooBarBazPage` → Nav `"Bar Baz"` (or more descriptive if needed)

### Rule 2 — No iteration suffixes

These suffixes are **banned** in committed code: `Refined`, `New`, `Enhanced`, `V2`, `B`, `Old`, `Legacy`, `Updated`, `Improved`.

If you are iterating on a component, use a feature branch. Merge replaces — it does not append a suffix.

### Rule 3 — Domain vocabulary (canonical, enforced)

Use only the current-generation vocabulary. Old terms are banned in new code:

| Domain | Canonical term | Banned terms |
|--------|---------------|-------------|
| Tenant data contracts | `canonical-data` | `dataspace`, `golden-data`, `gdp` |
| Infrastructure & compliance | `data-infra` | `data-controls` |
| Source connections | `data-sources` | `data-systems`, `source-data` |
| KPI packs | Business function label | `CFO Pack`, `CGO Pack`, `CMO Pack`, `COO Pack` |

**CFO/CGO/CMO/COO note:** These are internal domain codes used in API and DB. Page names must use the business function label: Finance, Sales, Marketing, Operations. Component names follow the same rule: `FinanceMetricsPage`, not `CFOPackPage`.

### Rule 4 — Legacy redirect routes are will-restore

All 72 redirect routes in `AppRouter.tsx` are tagged `// legacy: will-restore`. They are not dead code — they represent pages temporarily removed from navigation that will return at their canonical positions. Do not delete a redirect route without a DevHub task that explicitly retires it.

When a domain section is next touched (feature work, bug fix, or refactor), apply naming convention Rule 1-3 to that domain's pages as part of the same PR.

### Rule 5 — Navigation config is the source of truth for display labels

Nav labels live in `Navigation.tsx`. They must match Rule 1 derivation. If a nav label and a component name disagree, update the component name to match the nav label — not the other way around (nav labels are the user-visible contract).

## Migration Strategy

**Not a big-bang sprint.** Rules apply to:
- **All new pages** — immediately on creation
- **Pages touched for any reason** — apply naming convention as part of that PR
- **Pure renames** — only scheduled when a domain section is prioritized for feature work

Track progress via the `naming-convention` tag in DevHub tasks.

## Consequences

- No new pages created with banned suffixes — enforced via code review
- `CFOPackPage` → `FinanceMetricsPage` when KPI Store is next touched
- `GoldenDataOverview` → `CanonicalDataOverviewPage` when Canonical Data is next touched
- `DataControlsConnectionsPageRefined` → `DataSourcesRegisteredPage` — already a planned task
- Navigation config remains authoritative for display labels
