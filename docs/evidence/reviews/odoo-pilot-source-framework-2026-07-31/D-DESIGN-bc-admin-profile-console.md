# Design — bc-admin Profile Console (read-only)

**Status:** DRAFT. The read model (repair-location F) for the Odoo Target-Company Framework.
Read-only v1. No Track-C. Companion to `FRAMEWORK-odoo-target-company-profiles.md` §8.
**Three-part shape:** bc-pilot artifacts (SSOT) → bc-core profile registry + endpoint
(serving) → bc-admin pages (UI). bc-admin reads bc-core; bc-core owns the registry;
bc-pilot is the source of truth an importer syncs from.

---

## 1. Data model — the profile registry (fact-safe: derived from `bc-pilot/profiles/*/profile.json`)

A **profile** is a synthetic-tenant *fixture* — neither a source-system (Odoo the software,
which the Source Catalog registers) nor yet a tenant (onboarding is Track-C). So it gets its
own lightweight registry, keyed to the committed artifacts.

**`profile` (one row per target-company profile):**

| Column | From `profile.json` | Notes |
|---|---|---|
| `profile_code` (PK) | `profile_code` | e.g. `mfg-in` |
| `display_name` | `display_name` | |
| `profile_number` | `profile_number` | ordering |
| `archetype_json` | `archetype` | industry/buyer_type/geography/standard/size/entities/currency/FY — opaque display payload (Rule 1: JSONB is fine for non-queried display config) |
| `window_start`, `window_horizon_fy` | `window.*` | |
| `systems_realized` | `systems_realized[]` | which vendor systems this profile is built in (odoo, later bc/oracle) |
| `function_coverage_json` | `function_coverage` | function → status map |
| `ami_id` | `ami` | the durable snapshot |
| `last_built_at` | (build time) | |
| `gate_status` | (from gate run) | green / amber / red |

**`profile_gate_result` (historized, one row per gate run) — optional v1.1:**
`profile_code` (FK) · `run_at` · `gate` (integrity/benchmarks/coverage/regression) ·
`status` · `detail_json` (the gate output).

**Anomaly register + benchmark envelope** are served as artifact blobs (from
`anomalies.json` and `master.json#benchmarks`) — not normalized in v1; the endpoint returns
them for the detail view. (They are *display/answer-key* data, not queried.)

**Registry authority:** bc-pilot `profile.json` + gate output is SSOT; the bc-core registry
is a **projection** an importer keeps in sync (same discipline as D526: docket/registry =
projection of the artifact). The importer is idempotent, keyed on `profile_code`.

---

## 2. bc-core — serving layer  (cited; **build approach = clone the `library` module**)

The smallest proven end-to-end platform registry is `src/platform/library` — clone it.

**Table** — new `platform.pilot_profile`, sibling to
`src/database/schema/platform/library.ts` on `pgSchema('platform')`
(`schema/platform/pg-schema.ts:8`), ISO 11179 naming, exported from
`schema/platform/index.ts`. Columns = §1 model (`profile_code` PK; `display_name`;
`profile_number`; `archetype_json`; `window_start`/`window_horizon_fy`;
`systems_realized`; `function_coverage_json`; `ami_id`; `last_built_at`; `gate_status`),
index on `profile_code`/`gate_status`. Tiny enough that the `master-status.ts` composite-PK
reference-table variant (no cursor) is also a fair template if we skip pagination.
⚠ **Before cloning, resolve the flagged naming drift** in the template: `library.ts:33`
declares `library_status` but `library.repository.ts:24,89,96` reads `statusCode` — wire the
new `gate_status` column consistently (verify current, don't inherit the drift).

**Repository / Service / Controller** — clone `library.repository.ts` (injects
`PLATFORM_DB` from `database/db-tokens`; `cols` select-map + `toApiRow()` ISO→API name
translation; `listX` with `eq`/`ilike` conditions), `library.service.ts`
(`buildCursorPage` → `{items,cursor,hasMore}` envelope the frontend expects), and
`library.controller.ts`:
- `@PlatformOnly() @Controller('pilot-profiles')` (decorator `common/decorators/scope.decorator.ts:11`; global `ScopeGuard` enforces via Cognito ID-token `aud`→scope, so **no tenant header, no method guard** — read-only is by *convention*: just omit `@Post/@Patch/@Delete`, like `masters.controller.ts`).
- `GET /pilot-profiles` → list · `GET /pilot-profiles/stats` → counts · `GET /pilot-profiles/:code` → detail (registry row + benchmark envelope + anomaly register + latest gate result, the last two returned as artifact blobs).
- Wire into `src/platform/platform.module.ts` (providers repo+service+IdService; register controller).

**Importer (the one write path).** bc-core cannot read bc-pilot files at runtime, so
profiles are *pushed*: a thin `POST /pilot-profiles` upsert (guarded `@PlatformOnly` +
`super_admin`, importer-only — the console never calls it), invoked by a small bc-pilot
`publish-profile.py` that POSTs `profile.json` + gate results. Keeps bc-pilot SSOT, registry
a projection (D526 discipline). *(Alt: a bc-core seed for v1 if we don't want a write
endpoint yet.)*

**DBCP prerequisite:** `platform.pilot_profile` is a platform DB change → **Database Change
Protocol (present table + explicit approval) before build.** Design only here.

---

## 3. bc-admin — UI  (cited; **build approach = clone the `LibrariesPage` + `libraries.ts` pair**)

**API layer** — new `src/api/profiles.ts` mirroring `src/api/libraries.ts`: types + `apiFetch`
hooks `useProfiles(filters)` → list, `useProfile(code)` (`enabled:!!code`) → detail,
`useProfileStats()`. `apiFetch` (`src/api/client.ts:26-60`) attaches the Cognito Bearer ID
token and unwraps the `{data}` envelope automatically — platform scope is proven by the
admin Cognito app-client, **no x-tenant-id** (CLAUDE.md:91 is stale on this).

**Pages** (clone `LibrariesPage.tsx`, the read-only list+stats+filter+row→detail idiom; or
`MastersPage.tsx` for the simpler tabbed read-only shell):
- **`ProfilesPage`** — `PageHeader` → StatCards (profiles, functions covered, gates green)
  → `DataTable<Profile>` (`components/ui/data-table.tsx`) with columns: code, display_name,
  archetype summary, `systems_realized` badges, function-coverage summary, `gate_status`
  via `MasterStatusBadge`, AMI; `onRowClick` → `navigate('/platform/profiles/:code')`.
- **`ProfileDetailPage`** — archetype block · function-coverage map · benchmark panel
  (per-FY common-size vs envelope) · gate results · anomaly register (the answer key).

**Routing + nav (3 registration points — all required):**
1. Route — `components/AppRouter.tsx`: add `platform/profiles` → `ProfilesPage` and
   `platform/profiles/:code` → `ProfileDetailPage` (mirror the `platform/libraries[/:id]`
   pair at `:260-261`).
2. Top-nav — `components/TopNavbar.tsx`: add to the `platformItems` array (`:119-123`).
3. Left sidebar — `components/LeftSidebar.tsx`: add to `SECTIONS.platform.items`
   (`:143-153`), item shape `{label,path,icon}`.

**Constraints:** any enum (industry/function/status) via the `useMaster*` hooks
(`src/api/masters.ts`) — **no hardcoded enum arrays**; reuse `DataTable` +
`MasterStatusBadge`; read-only (no mutation hooks). React Query v5, `staleTime 5min`.

> **CLAUDE.md is stale in two load-bearing spots** (design against source, not the doc):
> the route map (`:126-157`, predates the `platform/*` restructure) and the `x-tenant-id`
> claim (`:91`,`:105` — `client.ts` sends none). Worth a follow-up CLAUDE.md fix.

---

## 4. v1 scope (bounded, read-only)

Profile catalog + mfg-in detail (archetype · function-coverage · benchmark panel · gate
results · anomaly register), served from the registry projection. **Out of v1:** live Odoo
rows (link out to the Odoo UI instead); any write/trigger-build surface (that drives
EC2 + generators — a later, different risk class).

## 5. Boundaries
Reads the framework; not a platform-integration surface. Shows source-richness, never
implies metric realization. No Track-C.

## 6. Build sequence & prerequisites (when we build it)
1. **DBCP** — present `platform.pilot_profile` (§2) for explicit approval. *Blocks everything.*
2. **bc-core** — clone the `library` module → schema + repo + service + read controller
   (`pilot-profiles`), wire `platform.module.ts`. Resolve the `library.ts` status-naming
   drift first. Verify with the existing platform test pattern.
3. **Importer** — `POST /pilot-profiles` upsert (super_admin) + bc-pilot `publish-profile.py`
   (or a bc-core seed for v1). Load Profile #1 (mfg-in) from `profile.json` + gate results.
4. **bc-admin** — `src/api/profiles.ts` + `ProfilesPage` + `ProfileDetailPage`; register
   route + top-nav + sidebar (3 points). Enums via `useMaster*`.
5. **Verify** — Playwright/browser_snapshot against localhost:3010 `platform/profiles`.

**Each bc-core + bc-admin change follows the audit-program review flow** (package →
disposition → operator merge); no self-merge. **Follow-up (separate):** fix the two stale
CLAUDE.md spots (route map, x-tenant-id).
