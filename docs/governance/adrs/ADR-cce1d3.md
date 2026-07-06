---
uid: DEC-cce1d3
decision_code: D348
title: "bc-portal Architecture and Patterns — routing, state, data-fetching, auth, error handling"
description: "Locks forward-going architectural patterns for bc-portal: single QueryClient, lazy routes, opt-in mock, DOMPurify, no auth bypass"
status: superseded
superseded_by: DEC-04dade
subdomain: frontend-architecture
focus: pattern-lock
date: 2026-04-18
project: bc-portal
domain: frontend
refs:
  - type: document
    path: "dev-guides/bc-portal/audit-report-2026-04-18.md"
    label: "bc-portal Audit Report 2026-04-18"
migrated_from: legacy v2 archive
---

# bc-portal Architecture and Patterns (D348)

## Context

The April 2026 audit (SES-92dc4e) identified several architectural inconsistencies and security issues that had accumulated without a locked convention:
- Two `QueryClient` instances (App.tsx + AppRouter.tsx) causing cache incoherence
- `VITE_BYPASS_AUTH` structurally wired into `ProtectedRoute.tsx` as a permanent "temporary" bypass
- `VITE_USE_MOCK` defaulting to `true` (opt-out) — mock data enters production bundle by default
- `dangerouslySetInnerHTML` used in 6 locations without sanitization
- No consistent error boundary strategy
- 80 routes statically imported (no lazy loading, large initial bundle)

## Decision

### Routing
- **React Router v6** — current, keep
- **Route-level code splitting** — all page imports in `AppRouter.tsx` wrapped in `React.lazy(() => import(...))`, routes wrapped in `<Suspense fallback={<PageSkeleton />}>`
- **Legacy redirect routes** — tagged `will-restore`, retained indefinitely; do not delete without updating DevHub task

### State Management
- **Server state** — TanStack React Query v5 only. No direct `useState` for async server data.
- **UI/local state** — React Context for cross-component UI state (sidebar, auth, dashboard config). `useState` for component-local state.
- **Forms** — React Hook Form. No raw controlled inputs for multi-field forms.
- **Single QueryClient** — one instance, created in `App.tsx`, provided via `<QueryClientProvider>`. No secondary `QueryClient` anywhere else in the tree.

### Data Fetching
- **All API calls via `src/api/client.ts`** — this is the only place that adds `Authorization: Bearer` and `x-tenant-id` headers.
- **Mock mode** — `VITE_USE_MOCK === 'true'` (opt-in, not opt-out). Missing env var = real API mode.
- **Mock data isolation** — mock data modules must be behind `if (import.meta.env.DEV)` guards or loaded only when `env.useMock === true`. `src/data/` imports forbidden in production code paths.

### Authentication
- **Cognito via `amazon-cognito-identity-js`** — no alternatives
- **`VITE_BYPASS_AUTH` removed** — `ProtectedRoute.tsx` must not contain any bypass code path. No env var, no flag, no conditional.
- **Token storage** — Cognito SDK default (`localStorage`) accepted for now with CSP mitigation. Migration to memory/cookie storage is a future task.
- **Mock auth** — isolated behind `env.useMock`, never bleeds into production build. No hardcoded credentials in source.

### Security
- **`dangerouslySetInnerHTML`** — requires `DOMPurify.sanitize(content)` wrapping at every callsite, no exceptions.
  ```tsx
  // Wrong
  <div dangerouslySetInnerHTML={{ __html: content }} />
  // Correct
  import DOMPurify from 'dompurify';
  <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(content) }} />
  ```
- **SVG injection** — no raw SVG strings in `dangerouslySetInnerHTML`. Use React SVG components or `<img>` tags.
- **Content-Security-Policy** — must be configured (meta tag or proxy header). Blocks inline script execution.
- **API URL default** — `VITE_API_URL` is required for non-dev environments. Default must be `http://localhost:3100`, not a production URL.

### Error Handling
- **Root `ErrorBoundary`** in `App.tsx` — keep (catches catastrophic failures)
- **Per-route `ErrorBoundary`** — required for every top-level route. Prevents one route's error from crashing the whole app.
- **React Query error states** — every `useQuery` must handle `isError` state in the component. Do not assume queries always succeed.

### TypeScript
- `strict: true` — required, must not be weakened
- `noUnusedLocals: true`, `noUnusedParameters: true` — must be enabled (currently disabled; remediate as part of mock-to-API migration)
- No `@ts-ignore` in `src/`. Use `@ts-expect-error` with a comment explaining the reason.
- Explicit `any` count must not increase above current baseline (125 as of April 2026).

## Consequences

- `VITE_BYPASS_AUTH` removal — DevHub task TSK-32249d (pre-existing)
- `useMock` default inversion — DevHub task TSK-05c41e
- DOMPurify addition — DevHub task TSK-0b1eae
- Dual QueryClient fix — DevHub task TSK-c4956c
- Route-level lazy loading — DevHub task TSK-96b56b
- tsconfig flags — DevHub task TSK-fba03b
