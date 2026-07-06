---
uid: DEC-162de5
title: "bc-portal naming convention — one name, three places"
description: "Component name = route leaf = nav label. No version suffixes. Exec titles are not page names. Legacy redirects tagged will-restore until explicitly retired."
status: implemented
subdomain: bc-portal
focus: naming-convention
date: 2026-04-18
project: bc-portal
domain: platform
code: D357
refs:
  - type: document
    path: "dev-guides/bc-portal/audit-report-2026-04-18.md"
    label: "Audit report (naming mismatch section)"
  - type: decision
    uid: DEC-04dade
    label: "D355 — bc-portal architecture & patterns (companion)"
  - type: decision
    uid: DEC-9a3c6a
    label: "D356 — DS governance (companion)"
migrated_from: legacy v2 archive
---

# bc-portal naming convention — one name, three places (D357)

## Context

The 2026-04-18 audit found four generations of naming coexisting in bc-portal:

| Layer | Example (actual) |
|-------|-----------------|
| URL path | `/data-sources/registered` |
| Component file/class | `DataControlsConnectionsPageRefined` (two renames behind) |
| Nav label | `"Data Sources"` |
| API endpoint | `/api/t/connectors-catalog` |

A developer sees four different words for the same screen. Routes have been migrated twice (`DataControls` → `DataInfra` → `Data Sources`; `Dataspace` → `GoldenData` → `CanonicalData`). Each rename updated routes and nav labels, but component files, service files, and ADR references kept the old terminology. One component (`DataControlsConnectionsPageRefined`) is used by TWO different routes in two different business domains — no one can infer which is which.

Additionally, the KPI Store uses executive titles as page names (`CFOPackPage`, `CGOPackPage`, `CMOPackPage`, `COOPackPage`) but the navigation labels them by business function (`Finance Metrics`, `Sales Metrics`, `Marketing Metrics`, `Operations Metrics`). The relationship is not learnable.

The user flagged naming as the biggest long-term risk ("sure case for confusion later") and chose: **ADR + lint rule now, rename opportunistically as pages are touched.**

## Decision

### R1: One name, three places

For any user-facing page:

| Layer | Form | Example |
|-------|------|---------|
| Route path (leaf) | kebab-case | `/data-sources/registered` |
| Page component name | PascalCase, matches the leaf with `Page` suffix | `RegisteredSourcesPage` |
| Nav label | Title Case, matches the component semantically | `"Registered Sources"` |

The three MUST be derivable from each other. A developer reading `RegisteredSourcesPage` should be able to guess `/data-sources/registered` and `"Registered Sources"`.

### R2: No version suffixes

Banned suffixes: `Refined`, `Enhanced`, `New`, `V2`, `B`, `Beta`, `Next`.

If you iterate on a page, work in a git branch. Do NOT ship `FooPage` and `FooPageNew` side-by-side. If both must exist temporarily (migration period), name the target destination cleanly and give the old one `_deprecated` suffix with `isDeprecated: true` in ComponentRegistry.

Existing violations: `DataControlsConnectionsPageRefined`, `FinancePageB`, `FormsDemoPageNew`. Migrate when touched.

### R3: Executive titles are internal codes, not page names

| Internal code | Page component name | Nav label |
|--------------|-------------------- |-----------|
| cfo | `FinanceMetricsPage` | "Finance Metrics" |
| cgo | `SalesMetricsPage` | "Sales Metrics" |
| cmo | `MarketingMetricsPage` | "Marketing Metrics" |
| coo | `OperationsMetricsPage` | "Operations Metrics" |

Exec title codes MAY appear in URL slugs as domain identifiers (`/kpi-store/cfo-pack`) because they're concise and stable. They MUST NOT appear as component names or nav labels.

### R4: Component/service/adapter mapping documented in JSDoc

The page component file must have a JSDoc header naming the chain:

```tsx
/**
 * Registered Sources page.
 * Route: /data-sources/registered
 * Nav label: "Registered Sources"
 * Service: datasource.service.ts (getRegisteredSources)
 * Adapter: sourcedata.adapter.ts (BcCoreConnector → DataSource)
 * API endpoint: GET /api/t/connectors-catalog
 */
export function RegisteredSourcesPage() { ... }
```

This documents the 4-level translation for readers.

### R5: Legacy redirects are tagged will-restore

The 72 legacy redirect routes in `AppRouter.tsx` (lines ~363–428) stay in place. They are tagged `// legacy: will-restore — TARGET` for pages the user intends to restore, and `// legacy: retired — DATE` for those explicitly retired. The default is `will-restore` until a page is explicitly retired.

Pages under the `/legacy` index page (`LegacyPagesPage.tsx`) are treated the same way — existence is preserved; navigation entry is deferred until the page earns a home.

### R6: Migration is opportunistic

No rename sprint. When touching a page for any other reason (bug, feature, refactor), apply the rename as part of the same PR. Rules:

1. New file name + update imports everywhere
2. Update ComponentRegistry entry (path + componentId)
3. Update route in AppRouter.tsx
4. Add the OLD route as a legacy redirect to the NEW route (so bookmarks don't break)
5. Update nav label in Navigation.tsx if needed
6. Update JSDoc header

The old component name MUST NOT remain as an alias. Rename = rename.

### R7: API endpoint naming is its own concern

API endpoints are governed by bc-core conventions (see bc-core ADRs). This ADR does NOT try to align endpoint names with page names — service/adapter layer handles translation. What it DOES require: the JSDoc chain in R4 makes the mapping visible.

## Options Considered

### Option A: ADR + lint rule + opportunistic rename (CHOSEN)

Lock the convention. Block new violations. Migrate as pages are touched.

**Why chosen:** Big-bang rename would stall product work and risk regressions. Opportunistic migration is slower but sustainable. User explicitly chose this.

### Option B: Big-bang rename sprint

Schedule a dedicated sprint. Rename ~40 mismatched components in one go. Branch aggressively.

**Rejected:** Rename of ~40 pages with their tests, imports, and routes is risky and touches the whole codebase. Would need to freeze other work. User rejected.

### Option C: Document only, no lint rule

Write the convention, don't enforce it.

**Rejected:** Without enforcement, new code drifts again. The four-generation problem reproduces within a year.

## Enforcement

### ESLint-style check (deferred — custom rule needed)

A custom ESLint rule is needed to flag component names matching banned suffixes. For now, enforce via:

1. **PR review** — reviewers check the self-check in `bc-portal-feature-sop.md` Step 3 (Name the feature)
2. **Manual scan** — quarterly grep for `Refined|Enhanced|PageNew|PageB|PageV2` in `src/pages/` — raise a DevHub task for each hit found

The custom rule is a followup task.

### ComponentRegistry governance

New entries MUST have a `name` that matches R1. Reviewer rejects any entry with a banned suffix unless there's a `// temp-rename: migrating-to-X` comment.

## Consequences

### Positive

- Readers of any single layer (URL, component, nav) can predict the other two
- The "DataControls vs DataInfra vs Data Sources" confusion dissolves over 12 months of natural code churn
- Exec-title page names go away — Sales team no longer sees a `CGOPackPage` and wonders why Growth = Sales

### Negative

- Some pages stay wrongly named for a long time (years, if never touched)
- 4-level JSDoc headers add noise to component files
- Code archaeology during the transition is harder — grep for old names still finds results

### Risks

- **Risk:** Opportunistic migration never completes — worst offenders are rarely touched.
  **Mitigation:** Quarterly grep + DevHub tasks. If a page hasn't been renamed in 12 months, make it a proactive task.
- **Risk:** A rename breaks a bookmarked URL because the redirect wasn't added.
  **Mitigation:** SOP step explicitly requires legacy redirect entry.
- **Risk:** The JSDoc chain (R4) goes stale when service/adapter layer changes independently.
  **Mitigation:** Accept the drift — JSDoc is best-effort, not enforced. Audit catches the egregious cases.

## Migration tracking

| Page pattern | Count | Status |
|-------------|-------|--------|
| `*Refined` components | 1+ | Tracked (DataControlsConnectionsPageRefined → RegisteredSourcesPage) |
| `*PageNew` / `*PageB` | 2+ | Tracked (FormsDemoPageNew, FinancePageB) |
| `CFO/CGO/CMO/COO*Page` | 4 | Tracked (rename to `Finance/Sales/Marketing/Operations MetricsPage`) |
| `GoldenData*` using /canonical-data/ routes | multiple | Tracked (rename to `CanonicalData*`) |
| `DataControls*` in /data-infra/ or /data-sources/ | multiple | Tracked (rename case-by-case to domain) |

Each pattern becomes a DevHub task with tag `naming-migration,D357`. Task status = `later` unless a feature PR touches the file, then status → `wip` in that PR.

## Reference

- Audit report: `legacy-v2/docs/dev-guides/bc-portal/audit-report-2026-04-18.md` — the naming mismatch table
- Feature SOP: `legacy-v2/docs/playbooks/bc-portal-feature-sop.md` — Step 3 enforces R1/R2/R3 on new work
