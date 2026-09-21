---
uid: DEC-ce3e7a
title: "bc-core authentication — no auth-bypass; real Cognito only (backfill)"
description: "Backfill decision record (SI-B-1 / D619) for the bc-core-scoped auth-bypass prohibition, which is in-force operational doctrine (CLAUDE.md) with no bc-core ADR. Real Cognito auth only; no bypass chains or env hacks. Cites the bc-portal auth-policy history (DEC-04dade, superseded by DEC-6cdceb) as precedent; records no auth behaviour change."
status: decided
date: 2026-09-21T11:16:59.857Z
project: platform
domain: platform
subdomain: auth
focus: security
---

# bc-core authentication — no auth-bypass; real Cognito only (backfill)

## Context

See decision text below.

## Context

The prohibition on authentication bypass in bc-core is in-force **operational doctrine** (recorded in CLAUDE.md) but has **no bc-core-scoped ADR**. The only related ADR is `DEC-04dade` ("bc-portal architecture & patterns"), which is **`status: superseded`, `superseded_by: DEC-6cdceb`** — a bc-portal decision, cited here as **precedent/history**, not current authority. This backfill was surfaced by the Structural Integrity program (DEC-027ef6/D619), package SI-B-1. It records existing doctrine; **no authentication behaviour changes** with this ADR.

## Decision

**bc-core uses real Cognito authentication. Auth-bypass chains and environment hacks are prohibited.**
- No `VITE_BYPASS_AUTH`-style flags, no bypass chains, no disabling the global auth guards to "work around" auth failures. When auth fails, debug the real auth flow.
- Credentials are real Cognito config in `.env` (COGNITO_USER_POOL_ID / CLIENT_ID / ISSUER_URL); the demo tenant/user path uses real login.
- **This is a backend (bc-core) rule.** Frontend `VITE_*` / `useAuth` bypass semantics are **not** imported into the backend; bc-portal's own auth pattern is governed by DEC-6cdceb (successor to DEC-04dade), cited here only as precedent.

**Boundary of the rule.** The prohibition applies to the **authenticated application surface**. **Legitimate unauthenticated or service-auth cases** — health/liveness endpoints, explicitly public routes, and service-to-service or test authentication paths — are **not** bypasses; each such case is declared and **separately reviewed**, not silently exempted.

**Rationale note.** The "~30% of past session time consumed by auth-bypass errors" figure in CLAUDE.md is an **attributed recollection**, not a measured metric; it motivates the rule but is not asserted as verified data.

## Consequence

bc-core has a single, ADR-backed auth stance: real Cognito, no bypass, with an explicit boundary for legitimate public/service/test auth. Future auth work cites this ADR rather than CLAUDE.md.
