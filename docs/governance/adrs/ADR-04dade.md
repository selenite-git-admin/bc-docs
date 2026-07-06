---
uid: DEC-04dade
title: "bc-portal architecture & patterns"
description: "Lock the forward patterns for bc-portal after the 2026-04-18 organic-growth audit. Single QueryClient, React.lazy routing, no auth bypass, opt-in mock, DOMPurify, CSP."
status: superseded
subdomain: bc-portal
focus: pattern-lock
superseded_by: DEC-6cdceb
date: 2026-04-18
project: bc-portal
domain: platform
code: D355
refs:
  - type: document
    path: "dev-guides/bc-portal/audit-report-2026-04-18.md"
    label: "Audit report (source findings)"
  - type: document
    path: "dev-guides/bc-portal/design-system-inventory.md"
    label: "DS inventory"
  - type: decision
    uid: DEC-9a3c6a
    label: "D356 — DS governance (companion)"
  - type: decision
    uid: DEC-162de5
    label: "D357 — naming convention (companion)"
migrated_from: legacy v2 archive
---

# bc-portal architecture & patterns (D355)

## Context

bc-portal has been built organically over the past year. The 2026-04-18 audit surfaced two BLOCKERs (committed Cognito credentials, live `VITE_BYPASS_AUTH` bypass) and ten HIGH findings spanning architecture, security, and code quality. The root cause is that patterns were never formally declared — each feature picked its own approach. Before any further feature work, the patterns need to be locked so new code stops drifting.

The original "rules and methods" ask from the user was scoped to: set architecture patterns, set security rules, set DS governance, set naming convention. This ADR covers architecture and security. D356 covers DS. D357 covers naming.

## Decision

### Authentication

1. **No auth bypass.** `VITE_BYPASS_AUTH` is removed from `env.ts`, `ProtectedRoute.tsx`, `api/client.ts`, `vite-env.d.ts`, and `.env.example`. There is no env var, no build flag, no conditional that skips `useAuth`.
2. **Real Cognito only.** Login goes through `amazon-cognito-identity-js`. Session state comes from `AuthContext`.
3. **No hardcoded credentials in source.** Mock mode accepts any non-empty email/password and derives the display name from the email prefix. The strings `admin@barecount.com` and `admin123` do not appear in source code outside `.env.example` placeholders.
4. **Token storage is localStorage today**, mitigated by CSP (see Security below). Long-term migration to in-memory or httpOnly cookie storage is tracked as a followup — not blocking this ADR.

### Data fetching & server state

1. **Single `QueryClient`** — instantiated once in `App.tsx`. No other file creates a new `QueryClient`. Cache is globally coherent.
2. **TanStack React Query v5** is the canonical server-state library. Raw `fetch` inside components is forbidden.
3. **All requests go through `api/client.ts`** which adds the `Authorization` bearer token and `x-tenant-id` header automatically.
4. **Opt-in mock mode.** `env.useMock` is `VITE_USE_MOCK === 'true'` — opt-in only. Default is real API. A misconfigured production build cannot silently serve mock data.

### Routing & performance

1. **All page imports in `AppRouter.tsx` use `React.lazy()`** wrapped in `<Suspense>`. 81 pages converted on 2026-04-18. Initial bundle no longer ships every page.
2. **Legacy redirect routes** are tagged `will-restore` until explicitly retired. The `/legacy` index page is the catalog.
3. **Route-level error boundaries** — root `<ErrorBoundary>` in App.tsx + dashboard boundary. Per-route boundaries should be added for trust-critical pages (connection setup, payment flows when added).

### HTML sanitization

1. **Every `dangerouslySetInnerHTML` MUST pass through `DOMPurify.sanitize()`.** No exceptions.
2. **SVG injection** uses `DOMPurify.sanitize(svg, { USE_PROFILES: { svg: true, svgFilters: true } })`.
3. **Preferred alternative:** use a library that returns React elements (e.g., `react-markdown`) instead of HTML strings.

### Content-Security-Policy

1. **Baseline CSP in `index.html`** allows only known origins: Google Fonts, Iconify, Cognito, bc-core local dev. Dev-safe (permits Vite HMR via `unsafe-inline`/`unsafe-eval`).
2. **Production CSP** should be set at the CDN/reverse-proxy layer with stricter rules (nonce-based, no `unsafe-inline`/`unsafe-eval`). Tracked as followup.
3. **New external origins** require updating the CSP meta tag.

### TypeScript discipline

1. **`strict: true` stays on.** Do not disable any strict-mode sub-option.
2. **No `@ts-ignore` in production code.** Use `@ts-expect-error` with a justification comment.
3. **Explicit `any` is discouraged.** Existing count at audit: 125 in 42 files. Treat this as a baseline — do not increase.
4. **`noUnusedLocals` / `noUnusedParameters`** are currently off. Enabling them is tracked — will be turned on after a cleanup sprint.

### Code style

1. **No `console.log/debug/info/trace` in `src/`.** Only `console.warn` / `console.error` allowed. Service methods waiting for implementation should use `console.warn` with a clear "not yet implemented" message.
2. **No hardcoded production URLs as dev fallbacks.** API URL falls back to `http://localhost:3100`, not `https://api.barecount.com`.

## Options Considered

### Option A: Codify rules now, migrate opportunistically (CHOSEN)

Lock patterns. Enforce on new code. Existing violations are tracked as baselines and migrated when the surrounding code is touched.

**Why chosen:** bc-portal has an active demo tenant (demo-selenite) and 15 MCs producing. A big-bang migration would stall the demo unlock arc. Opportunistic migration keeps the product moving while stopping the bleeding.

### Option B: Rewrite-first

Full refactor of the 133-page codebase against the new rules before any new features land.

**Rejected:** Too disruptive for current product momentum. Unrealistic effort estimate. User explicitly chose opportunistic migration.

### Option C: Document only, no enforcement

Write the ADR but add no ESLint rules, no audit gates, no review checks.

**Rejected:** Without enforcement, patterns drift again. The organic-growth problem reproduces.

## Consequences

### Positive

- Single `QueryClient` eliminates silent cache incoherence that duplicated queries
- No auth bypass means no one-env-var path to full unauthentication
- Opt-in mock means production builds cannot accidentally serve synthetic data
- DOMPurify eliminates the most realistic XSS attack surface
- Route-level lazy loading reduces initial bundle size
- ESLint rule (D356) catches new DS violations at commit time

### Negative

- 135 grandfathered DS hex violations now show as ESLint warnings on every lint run (noise during migration)
- 31 of 32 console.logs removed in the audit session — the one JSDoc remnant is intentional
- `noUnusedLocals` not yet enabled — dead code can still accumulate in the interim

### Risks

- **Risk:** A developer disables the ESLint rule in a PR to unblock urgent work.
  **Mitigation:** Require `// eslint-disable-next-line no-restricted-syntax` with a justification comment. Code review checks for these.
- **Risk:** The CSP blocks a new external integration at runtime without a clear error.
  **Mitigation:** CSP violations appear in browser devtools. Dev guide mentions this. New origins must be added to index.html.
- **Risk:** DOMPurify has CVEs over time.
  **Mitigation:** Covered by standard dependency audits (`npm audit`). DOMPurify is widely deployed and patched quickly.

## Migration status

| Rule | Audit baseline | Status as of 2026-04-18 |
|------|---------------|------------------------|
| VITE_BYPASS_AUTH removed | Active in code | Complete |
| Single QueryClient | 2 instances | Complete (single in App.tsx) |
| Mock opt-in | Default true | Complete (default false, opt-in) |
| DOMPurify | Missing | Complete (3 sites sanitized) |
| React.lazy routes | 0 / 80 | Complete (81 / 81) |
| Credential leak in ConnectionSetupPage | Active | Complete |
| Mock hardcoded credentials | Active | Complete |
| CSP | Missing | Baseline in place |
| Console.log in src/ | 32 | 1 (JSDoc example) |
| ESLint DS rule | Missing | Active (D356) |
| API URL prod fallback | Hardcoded | Complete (localhost) |
| noUnusedLocals | Off | Deferred (sprint task) |
| 125 explicit any | Baseline | No increase allowed |

## Enforcement

- **PR review** checks the self-check list in `playbooks/bc-portal-feature-sop.md` Step 10
- **ESLint rules** (D356) fail new violations
- **bc-qa audit** runs cross-repo gates — `no-eval`, console.log detection, type safety baselines
- **Audit re-run** at 6-month intervals to verify patterns stay locked
