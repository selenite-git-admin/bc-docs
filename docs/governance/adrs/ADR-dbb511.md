---
uid: DEC-dbb511
title: "DB role separation — barecount_app vs barecount_ops, executed at pre-staging provisioning"
description: "Two Postgres roles (app vs ops scripts) instead of one shared credential; decided now, executed at pre-staging provisioning; pre-commit guard against new direct-DB scripts already live"
status: decided
date: 2026-07-03T09:06:02.048Z
project: bc-core
domain: infrastructure
subdomain: database-access
focus: governance
---

# DB role separation — barecount_app vs barecount_ops, executed at pre-staging provisioning

## Context

Audit during the bc-core Hardening & Governance Program (SES-ea54ee/SES-560a52, 2026-07-03) found ~190 files under bc-core/scripts/ connecting directly with the app's own DATABASE_URL/TENANT_DATABASE_URL — bypassing the governed API/service layer entirely, with zero privilege distinction between the running service and a scratch script written the same afternoon. Today this is dev-only (localhost:5435), but it is exactly the pattern that becomes dangerous once staging/prod exist with real customer data: it structurally defeats CLAUDE.md's SERVICES-ONLY and No-DB-hand-edits mandates rather than merely violating them case-by-case. Role separation makes the boundary a property of the database, not an honor-system rule. Deferring execution to pre-staging provisioning was the operator-approved recommendation: the payoff is real when real customer data exists, and creating local roles now would add bootstrap-script migration steps for limited near-term benefit. Operator approved 2026-07-03.

## Decision

Split the single Postgres role (barecount, full read/write on bc_platform_dev's 11 schemas and every tbc_{slug}_dev tenant DB, shared verbatim by the bc-core service process AND every ad-hoc script) into two roles:

1. barecount_app — the role bc-core's NestJS process uses. Grants scoped to what the application needs (full read/write across platform + tenant schemas — the app legitimately owns its domain; the point is not restricting the app but not handing the SAME credential to arbitrary scripts).
2. barecount_ops — a separate credential for one-time/operational scripts, with narrower grants (at minimum a distinct credential so a leaked or misused script credential does not imply app-level access and vice versa; ideally no DROP/ALTER on core tables without a session-scoped grant).

Execution is DEFERRED to the pre-staging/prod DB provisioning checkpoint (the R8 AWS-spend decision list from the Runtime Spine Program) — not applied to the current dev DB in isolation. The change itself is CREATE ROLE + GRANT only: no schema, table, or data changes.

Already in force (no DB change needed): the bc-qa pre-commit hook (shared template + bc-core local) blocks NEW files outside src/database/, src/config/, *.spec.ts, scripts/archive/ from referencing DATABASE_URL/TENANT_DATABASE_URL — stopping new backdoor-script accumulation immediately. The ~190 existing direct-access scripts in bc-core/scripts/ are grandfathered and migrate to barecount_ops when it exists.
