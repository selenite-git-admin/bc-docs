---
title: "D432 Legacy Metric Contract Authoring Guard — implementation change proposal (code-only; NO DDL)"
description: Implementation proposal for DEC-7bdd03/D432 (D429 Step 3). A repository-layer refuse-to-author guard that blocks new legacy contract.metric_contract* create-authoring by default; escape requires BOTH BCCORE_ALLOW_LEGACY_METRIC_AUTHORING=1 and an explicit logged maintenanceApproval rationale. Service + repository + tests only; NO schema/DDL/migration/data change; no DB trigger; no activation gating.
status: draft
date: 2026-06-08
project: bc-core
domain: contracts
subdomain: metric-authoring
focus: governance
---

# D432 Legacy Metric Contract Authoring Guard — change proposal (code-only)

> Implements **DEC-7bdd03 / D432** (D429 Step 3). **Code change only — no DDL/schema/migration/data; no DB trigger (G3 deferred); no activation gating.** Scope: a repository-layer refuse-to-author guard at the legacy `contract.metric_contract*` **create** choke points. Grounding study: `legacy-metric-contract-authoring-guard-study-2026-06-07.md`.

## Decision recap (locked)
- **G2 only** — repository-layer refuse-to-author guard at the create choke points. No DB trigger.
- **Default = blocked.** Escape requires **both** `BCCORE_ALLOW_LEGACY_METRIC_AUTHORING=1` **and** an explicit, logged `maintenanceApproval` rationale.
- **Block create-authoring only.** Activation is not gated here (owned by D433, already merged).
- **Preserve** runtime reads, audit-metadata UPDATEs, tests/fixtures (test-env exempt), and the future MCF materialization writer.

## Change set

**New — `src/registry/legacy-metric-authoring.guard.ts`**
- `assertLegacyMetricAuthoringAllowed(opts?, env?)` — throws `ForbiddenException` unless permitted.
- Permitted when: test env (`NODE_ENV==='test'` or `VITEST==='true'`) → always; OR `allowFlag` (`BCCORE_ALLOW_LEGACY_METRIC_AUTHORING==='1'`) **and** a `maintenanceApproval` rationale ≥ 12 chars → allowed and **logged** (`console.warn`, audit).
- `env` is injectable (default = live `process.env`) so the block/allow logic is unit-testable despite the test-env exemption.

**Choke point 1 — `ContractMetricsRepository.createMinimalMetricContract`** (`contract-metrics.repository.ts`)
- Inserts `contract.metric_contract` (the legacy parent). Add optional `maintenanceApproval?` to the input; call the guard before the INSERT. Covers the script/seed-direct path (e.g. `d225-generate-phases-4-7.js`).

**Choke point 2 — `ContractVersionRepository.createVersion` (metric branch)** (`contract-version.repository.ts`)
- Generic across families; after `resolveFamilyOrDetect`, call the guard **only when `family === 'metric'`** (which also covers `intervention`/`ai`, both routed to the metric table per `resolveFamily`). Add optional `maintenanceApproval?` to the input. This is the envelope-create block (the API `POST /contracts/:id/versions` path, where `ContractService.createVersion` passes no `maintenanceApproval` → blocked by default).

**Tests — `legacy-metric-authoring.guard.spec.ts`**
- test-env allowed; no-flag/no-rationale blocked; flag-without-rationale blocked; rationale-without-flag blocked; short-rationale blocked; flag+valid-rationale allowed + logs.

## Why these two sites
Per the Step-3 study, legacy metric authoring reaches `contract.metric_contract*` via (a) the API version-create (envelope) and (b) the repo parent-create used by scripts/seeds. Guarding both closes new ungrounded-envelope authoring. The generic parent identity create (`createContract`) is not separately guarded because the **envelope** create (choke point 2) is the effective block — no `co_bindings` can be written without it.

## Preserve (unaffected)
- **Runtime reads** — read paths call no create method.
- **Audit-metadata UPDATEs** (`formula-audit` `audit_status_code` etc.) and **supersession** — these are UPDATEs, not creates; the guard is on create paths only.
- **MCF** — writes `mcf.*` (different tables); unaffected. The future MCF→`contract.metric_contract` materialization writer (Step 5) passes via the escape (flag + rationale) as an authorized writer.
- **Tests/fixtures** — test-env exemption keeps integration fixtures (e.g. `createMinimalMetricContract`) working.

## Out of scope
No DB trigger (G3); no activation gating; no D430/D431 implementation; no parent/version desync cleanup; no schema/DDL/DB/data; no MCF materialization.

## Gates / rollback
`tsc` + `eslint` + focused `vitest` (guard spec). Rollback = `git revert` (code-only; nothing in the DB).

## PR shape
Branch off main → guard module + 2 choke-point wirings + guard spec → gates → open PR **holding** (no merge).
