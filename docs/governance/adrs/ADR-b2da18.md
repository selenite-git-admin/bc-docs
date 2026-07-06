---
uid: DEC-b2da18
title: "bc-portal Architecture and Patterns"
description: "Lock canonical patterns for bc-portal: routing, state, data fetching, auth, error boundaries, folder structure, testing. Stops organic drift."
status: superseded
superseded_by: DEC-04dade
subdomain: bc-portal
focus: pattern-lock
date: 2026-04-18
project: bc-portal
domain: frontend
refs:
  - type: decision
    uid: DEC-142237
    label: "D352 — DS Governance"
  - type: decision
    uid: DEC-705f76
    label: "D353 — Naming Convention"
  - type: document
    path: "dev-guides/bc-portal/audit-report-2026-04-18.md"
    label: "Full audit report (SES-92dc4e)"
migrated_from: legacy v2 archive
---

# D351 — bc-portal Architecture and Patterns

## Context

bc-portal grew organically. Audit SES-92dc4e (2026-04-18) found:

- 140+ components, 81 routes, 200+ mock data files in `src/data/`
- Dual `QueryClient` instances (App.tsx + AppRouter.tsx) → incoherent cache
- Inverted mock-mode default (`VITE_USE_MOCK !== 'false'` meant `true` by default)
- `VITE_BYPASS_AUTH` wired into `ProtectedRoute.tsx`
- 125 explicit `any` types across 42 files
- `noUnusedLocals` + `noUnusedParameters` disabled despite `strict: true`
- Direct mock data imports in 35+ pages, blocking real-API migration
- Three duplicate KPICard components

Organic evolution worked for speed but stopped working for scale. A canonical pattern lock is needed before the next drift cycle.

## Decision

### Routing

- **Library:** React Router v6, `BrowserRouter`
- **Structure:** Hierarchical paths, not flat (e.g., `/data-sources/registered`, not `/data-sources-registered`)
- **Code splitting:** Every page component lazy-loaded via `React.lazy()` + `Suspense`. Implemented in TSK-96b56b (81 pages converted).
- **File organization:** `src/pages/<domain>/<Name>Page.tsx`. No flat `src/pages/` — group by domain.

### State Management

| Kind | Library / Pattern | Where |
|------|-------------------|-------|
| Server state | TanStack React Query v5 | Hooks in `src/hooks/use*.ts` |
| Global UI state | React Context | `src/contexts/*Context.tsx` (Auth, LeftSidebar, RightSidebar, AIAssistant, Dashboard) |
| Form state | React Hook Form | In-place within page components |
| URL state | React Router `useSearchParams`, `useParams` | Direct |

**One QueryClient.** Defined in `App.tsx`. Do not instantiate a second one anywhere. Fixed in TSK-c4956c.

No Redux, no Zustand, no MobX. Scope does not warrant them.

### Data Fetching

```
Page/hook → services/*.service.ts → api/client.ts → fetch
```

- **`src/api/client.ts`** is the only fetch wrapper. Adds `Authorization: Bearer <token>` + `x-tenant-id` headers. On 401, redirects to `/login`.
- **Services** (`src/services/<domain>.service.ts`) wrap the client with typed methods. Mock-mode branch uses dynamic `import('../data/...')` behind `env.useMock` guard.
- **Hooks** (`src/hooks/use<Domain>.ts`) wrap services with React Query (`useQuery`, `useMutation`, keys in `src/lib/queryKeys.ts`).

### Authentication

- **Real Cognito only.** No bypass flags. `VITE_BYPASS_AUTH` removed (TSK-32249d).
- **Token handling:** Cognito SDK stores tokens in `localStorage` (known trade-off). Mitigated by CSP (TSK-f62c8e).
- **Mock mode:** `VITE_USE_MOCK=true` opt-in (TSK-05c41e). Accepts any non-empty email/password in mock mode. Never the default.
- **Protected routes:** `ProtectedRoute` wrapper gates all authenticated routes; redirects to `/login` if not authenticated.

### Error Boundaries

- **Root:** `ErrorBoundary` component in `App.tsx` catches any uncaught render error.
- **Dashboard:** `DashboardErrorBoundary` for dashboard routes (independent failure domain).
- **Per-route:** Optional, add if a route has a specific recoverable error mode.

### Folder Structure

```
src/
├── api/              # client.ts (only fetch wrapper)
├── adapters/         # type adapters between backend shapes and UI types
├── components/
│   ├── ui/           # shadcn/ui primitives (D352 — unmodified)
│   ├── common/       # mid-level reusable abstractions (cards, layouts, tables)
│   ├── design-system/ # ComponentRegistry + DS utilities
│   ├── <feature>/    # feature-specific components (charts, widgets, viewers, etc.)
│   ├── layouts/      # AppLayout, AuthLayout
│   └── routing/      # AppRouter, ProtectedRoute, RouteGenerator
├── config/           # env.ts, navigation.ts (future — D353)
├── contexts/         # React Contexts for global UI state
├── data/             # mock data (DEV-ONLY — will migrate out per TSK-c96ab5)
├── hooks/            # React Query hooks
├── lib/              # constants, queryKeys, utils
├── pages/            # one file per route, grouped by domain
│   └── <domain>/     # e.g., auth/, workspace/, kpi-store/, dataspace/
├── services/         # service modules wrapping api/client
├── styles/           # globals.css (D352 — single token source)
└── utils/            # pure utility functions
```

### TypeScript

- `strict: true` — mandatory
- `noUnusedLocals: false`, `noUnusedParameters: false` — **temporarily** disabled. Will be enabled in Phase C (post-consolidation) after rename/delete passes stabilize the file set.
- `allowJs: true` — current; revisit in Phase C.
- `explicit any` — 125 current. Ban new introductions (bc-qa rule). Reduce opportunistically; ConnectionSetupPage.tsx is the P1 target (30 `any` alone).

### Testing

- **Unit + component:** Vitest + React Testing Library
- **E2E:** Playwright with Edge browser (per memory: `credentials_cognito.md`)
- **Coverage thresholds:** Not enforced in Phase A. Revisit after rename pass.

### Build

- **Vite 6** — current
- **Tailwind 4** zero-config (tokens injected from globals.css via `@theme inline`)
- **CodeArtifact npm registry** — `.npmrc` routes all installs through `barecount/npm-mirror`

## Options Considered

### Option A: Canonical pattern lock (chosen)

Fix the drift now, stop new drift. Migrate existing divergences opportunistically.

### Option B: Introduce Zustand for global state (rejected)

React Query + Context covers current needs. Zustand adds another pattern without a forcing function. Reconsider if cross-cutting non-server state grows.

### Option C: Migrate to React Router v7 file-based routing (rejected)

Migration cost (81 routes) not justified. Current structure works; the problem was cache + lazy-loading, not the router.

### Option D: Accept status quo + document the chaos (rejected)

This is how it got here.

## Consequences

### Positive

- Stops drift: new developers have a yardstick; code review references this ADR.
- Cache coherence restored (single QueryClient).
- Mock mode no longer default — production safety improved.
- Code splitting reduces initial bundle size (measure after Phase C).

### Negative

- ~35 pages still import from `src/data/` directly. Migration to real-API hooks is a Phase C cost (TSK-c96ab5, TSK-df848a).
- `noUnusedLocals`/`noUnusedParameters` enable deferred — dead code accumulates until Phase C.
- ComponentRegistry drift (~72 unregistered) persists until Phase C.

### Risks

- **Cleanup sweep surfacing many errors.** Mitigation: sequence rename (Phase B) before type-cleanup (Phase C); scope each batch.
- **Developers circumventing the pattern via `any` or `eslint-disable`.** Mitigation: review gate per D352; bc-qa audit.

## Implementation Status

Completed in SES-92dc4e (2026-04-18):
- ✅ Dual QueryClient removed (TSK-c4956c)
- ✅ `VITE_BYPASS_AUTH` removed (TSK-32249d)
- ✅ Mock mode opt-in (TSK-05c41e)
- ✅ API URL fallback corrected (TSK-6bb5ad)
- ✅ CSP baseline added (TSK-f62c8e)
- ✅ DOMPurify applied (TSK-0b1eae)
- ✅ React.lazy for all 81 page routes (TSK-96b56b)
- ✅ 31 of 32 console.logs removed (TSK-a80cef)

Deferred to Phase B (consolidation):
- Rename pass (D353)
- Nav manifest (D353)
- Delete obsolete pages

Deferred to Phase C (cleanup):
- `noUnusedLocals` enable
- `any` reduction
- Mock data layer migration
- ComponentRegistry catch-up
