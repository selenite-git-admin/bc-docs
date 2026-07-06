---
uid: DEC-f0c0f7
title: "No Hardcoded Enums — All Dropdowns Must Be API-Driven"
description: "Frontend dropdowns must consume master data API endpoints — no hardcoded enum arrays in .tsx/.ts files"
status: implemented
subdomain: qa-standards
focus: api-driven-enums
date: 2026-04-05
decision_code: D287
project: bc-qa
domain: platform
refs:
  - type: decision
    uid: DEC-388129
    label: "D236: Domain Taxonomy as Platform Master"
  - type: decision
    uid: DEC-ee6018
    label: "Power of Ten — BareCount Coding Rules"
  - type: document
    path: "system/platform/P10-master-data/index.md"
    label: "P10: Master Data Module"
migrated_from: legacy v2 archive
---

# No Hardcoded Enums — All Dropdowns Must Be API-Driven

## Context

ADR-388129 (D236) established that domain taxonomy is platform master data and that "all consumers read from the API instead of local copies." The P10 Master Data module provides `GET /masters/*` endpoints backed by the `master` schema (8+ reference tables).

However, there was no enforcement mechanism. Nothing prevented a developer from writing `const STATUS_OPTIONS = [{ value: 'active', label: 'Active' }, ...]` in a React component. Over time this creates:

- **Drift** — backend adds a new enum value, frontend doesn't show it until someone notices
- **Inconsistency** — labels, sort order, or descriptions differ between backend and frontend
- **Redeployment tax** — changing a dropdown label requires a frontend build+deploy instead of a DB update
- **Governance bypass** — master data changes should go through the master data module, not scattered frontend PRs

bc-admin already has `src/api/masters.ts` with React Query hooks (`useMasterFunctions()`, `useMasterStatuses()`, etc.) and components like `MasterStatusBadge.tsx` that correctly consume API data. The pattern exists — it just needs to be mandatory.

## Decision

**All enum-like values displayed in UI components (dropdowns, selects, radio groups, filter chips, badge maps) MUST come from master data API endpoints, not from hardcoded const arrays in frontend code.**

### Rules

1. **Dropdown/select options** — must be fetched from `/masters/*` endpoints via React Query hooks
2. **Status badge maps** — must use `useMasterStatuses()` or equivalent, not inline color maps
3. **Filter chip lists** — must come from API, not hardcoded arrays
4. **New enum types** — add a master table + API endpoint + React Query hook before using in UI

### Exceptions (require explicit comment)

The following are acceptable as static values with a `// qa-approved: static-enum` comment:

- **UI-only enums** that don't correspond to any backend data (e.g., sort direction: asc/desc, view mode: grid/list)
- **Boolean toggles** (yes/no, enabled/disabled)
- **Framework constants** (HTTP methods, MIME types)
- **Test fixtures** in `*.test.*` or `*.spec.*` files

### Enforcement

| Layer | Mechanism | Severity |
|-------|-----------|----------|
| QA audit | `check-hardcoded-enums.sh` in bc-qa | warn (bc-admin, bc-portal), skip (bc-core, bc-ai, devhub) |
| Code review | Checklist item: "All dropdowns API-driven?" | Manual |
| Pre-commit | Future: ESLint rule `@barecount/no-hardcoded-selects` | Planned |

### Escape hatch

Add `// qa-approved: static-enum` on the line with the array declaration. The QA check will skip that line. Misuse is caught in code review.

## Options Considered

### Option A: QA check + code review checklist (chosen)

Lightweight enforcement via shell script pattern matching + manual review. Catches obvious violations without complex AST parsing. False positives handled by escape hatch comment.

### Option B: Custom ESLint rule (deferred)

AST-based detection would be more precise but requires building and maintaining a custom ESLint plugin. Deferred to a future iteration once the shell-based check proves the pattern.

### Option C: No enforcement, rely on convention (rejected)

Conventions without enforcement erode over time, especially as the team grows. The existing codebase already has the API-driven pattern — enforcement prevents regression.

## Consequences

### Positive
- Single source of truth for all enum values (master schema)
- Dropdown changes via DB update, no frontend redeployment
- Consistent labels and sort order across all consumers
- Governance-compliant — changes go through master data module

### Negative
- API dependency for rendering dropdowns (mitigated by React Query caching with 5-min stale time)
- QA check may produce false positives on legitimate static arrays (mitigated by escape hatch)

### Risks
- **False positives** — Non-enum const arrays flagged. Mitigation: specific pattern matching + `qa-approved` escape hatch.
- **API unavailability** — If `/masters` is down, dropdowns render empty. Mitigation: React Query retry + staleTime keeps last-known values.
