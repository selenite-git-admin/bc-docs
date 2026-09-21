---
id: tenant-metric-binding
order: 65
title: "Tenant Metric Binding"
status: drafting
authority: authoritative
depends_on: [the-contract-grammar, tenancy-and-binding, metric-catalog, metric-evaluation, mc-chain-integrity]
governing_sources:
  - Tenancy and Binding (operating-model)
  - Metric Catalog (operating-model)
governing_adrs:
  - DEC-b049f6 (retires the legacy readiness/binding/funnel HTTP surface as explicit 410 Gone; M17/D547 pattern — legacy-metric binding corpus empty since M17)
  - DEC-95687d (D369 — Connector Onboarding: chain-walk → populate-bindings → enqueue-provisioning)
  - DEC-ebf0b4 (D268 — Session Discipline; bind operations require explicit approval per DB Change Protocol; no raw DB-row hand-edits)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Tenant Metric Binding

How an operator binds metric contracts to a tenant — i.e. activates which MCs evaluate against which tenant's canonical-object data — and provisions the tenant fact tables that hold the results. Every binding is a platform-DB write and falls under the [DB Change Protocol](../foundation/the-contract-grammar.md): present the scope to the user, get explicit approval, only then execute. Raw SQL `UPDATE`/`INSERT` on `tenant.contract_binding` is **prohibited** (DEC-ebf0b4/D268) — go through the governed services below.

> **As-built note (verified against bc-core `53bb1115`, 2026-09-21).** The current binding+provisioning path is the **MCF entitlement-driven onboarding flow** on the Schema Provisioner. The **legacy curated `/admin/readiness/...` binding workflow is RETIRED** — every one of its endpoints now returns **410 Gone** (see [Retired surface](#retired-surface-410-gone)). This chapter documents the live path and marks the retired one so operators don't follow a dead route.

## What binding does — and doesn't

Binding declares which MCs are scoped for evaluation in a tenant; it does not itself produce data. The sequence to actually see results is **bind → provision (owner-worker) → evaluate**. Binding also does **not** move a metric's platform lifecycle: an MC must already be Platform Ready (chain-complete, formula-supported, audit-passing, MLS-14-active) for a tenant binding to be meaningful. **Provisioning readiness is not tenant MLS completion** — a provisioned fact table means the table exists, not that the metric has evaluated or that any tenant MLS rung is satisfied.

## The live path: MCF onboarding (Schema Provisioner)

All routes are platform-scoped (`@PlatformOnly`, `platform_admin`) under `/api/schema-provisioner`. Two entry points; both **enqueue** governed provisioning commands and return **202 Accepted** — the served process holds **no tenant DDL capability** (D575 Unit-3 F1); the owner-privileged worker creates the tables.

### Bind one MCF metric — `POST /schema-provisioner/onboard-metric`

```
POST /api/schema-provisioner/onboard-metric
Body: { "tenantSlug": "<slug>", "metricContractUid": "<mcf-mc-uid>", "environmentCode": "development" }
```

Reverse-walks the entitled MCF metric to the Canonical Contract (and upstream Source Contracts) it depends on, writes `tenant.contract_binding` (CC/MC) + `tenant.tenant_binding` (SC), and **enqueues** a provisioning command per desired `fact.co_*/fact.so_*/fact.ms_*` table (the metric's `fact.ms_*` is in the MCF namespace). Idempotent. Returns **202**; poll provisioning status (below).

### Bind a whole connector chain — `POST /schema-provisioner/onboard-connector`

```
POST /api/schema-provisioner/onboard-connector
Body: { "tenantSlug": "<slug>", "connectorId": "<uuid>", "environmentCode": "development" }
```

The D369 primary trigger for tenant onboarding: walks the connector chain forward, populates `tenant_binding` (source) + `contract_binding` (canonical/metric/intervention), and **enqueues** a provisioning command per desired `fact.*` table. Idempotent. Returns **202** — it does **not** create tables or "reconcile in one call"; completion requires the worker (below) and is confirmed only by the status read. Use this when the intent is "give this tenant everything reachable from this connector"; the DB Change Protocol is satisfied at the connector level (the operator approves the connector onboard once; binding fans out from there).

### Provision the fact tables — the owner-privileged worker (out-of-process)

The served endpoints only enqueue. Tables are created by the **provisioning worker CLI** (`provisioning-worker-cli.ts`), which runs **outside** the served process with owner privileges (needs `TENANT_OWNER_DATABASE_URL`, absent from the API process). It is a **one-shot CLI**, not a periodic scheduler:

- **drain** (default): consumes **every claimable** provisioning command (CAS-claim → validate coordinate → create table), across whatever is outstanding — not scoped to a single MC. After draining it signals **readiness resolution** (`pending_provisioning → active`) unless `--no-readiness`.
- **`--sweep`**: the relocated nightly graph (`ProvisioningSweepService`) — activation-fanout + repair/retry/reclaim + per-tenant reconcile across **every active tenant**, then drain + readiness.

Because a drain/sweep affects work beyond the metric an operator just onboarded (all claimable commands; `--sweep` spans all tenants), running the worker requires its **own bounded authority** — approving a metric onboard does not authorize a fleet-wide sweep. Invocation and any external scheduling are a deployment/runbook concern and are not asserted here.

### Check provisioning status — `GET /schema-provisioner/tenants/<slug>/provisioning`

A read over the append-only command store (no side effect). Each command carries its state (`pending | provisioning | provisioned | failed`) and obligation (`current | obsolete` — an obsolete coordinate is superseded/no-longer-provisionable: visible and counted, but **not** outstanding). **`ready` is true iff at least one *current* command is `provisioned` AND zero *current* commands are non-provisioned** — an empty or obsolete-only set is **not** ready. An unreadable registry leaves commands current (fail-closed).

### Recover a stuck command

Two distinct mechanisms — do not conflate:

- **Operator reissue** — `POST /schema-provisioner/provisioning/commands/<id>/reissue` (requires a trimmed rationale ≥ 8 chars). Governed operator recovery for a command whose **current attempt is `failed`** (beyond the worker's automatic retry cap). Append-only: it opens attempt N+1; the DB attempt fence refuses any other state (**409**), and an obsolete coordinate is refused. It marks nothing provisioned — the worker's next drain claims the new attempt.
- **Worker reclaim** — an **abandoned/expired lease** (a command stuck in `provisioning` after its lease lapsed) is reclaimed **only by the worker sweep**, which holds the tenant execution lock while it does so. Operators do **not** reissue these; reissue from `provisioning` state is refused (409).

### Verify readiness

Use the current readiness surface — `GET /api/registry/mcf/readiness-projection` (the legacy `/admin/readiness/...` dial and `/registry/funnel-ladder` are retired, below). Cross-check the fact table exists and evaluation has run before treating a metric as producing.

## Rollback / unbind

There is **no verified served governed endpoint** in the current tree for deactivating a tenant metric binding. A `PATCH .../metrics/:mcUid/binding` handler exists in `FunctionAdminController` source, but it is **not present in the served route snapshot** and its "disable" is documented as **cosmetic — it does NOT stop engine evaluation** — so it must **not** be relied on to halt a metric. Do **not** deactivate via a raw SQL `UPDATE` on `tenant.contract_binding` either (prohibited DB-row hand-edit, DEC-ebf0b4/D268).

**Consequence:** a governed, evaluation-affecting unbind for a tenant MC is a **documentation/verification gap** — the mechanism that genuinely halts evaluation is not established here and must be verified against the evaluation-scheduler/binding source before it is documented or relied upon. For chain-walk bindings, unwinding is intended to run through the connector offboarding flow (out of scope here), not a per-MC toggle.

## Retired surface (410 Gone)

Per **DEC-b049f6** (M17/D547 retirement pattern; the legacy-metric binding corpus has been empty since M17), the following are retained only as explicit **410 Gone** refusals — **do not use them**:

| Retired route | Replacement |
|---|---|
| `GET /admin/readiness/catalog` | — (legacy metric catalog retired) |
| `GET /admin/readiness/tenant` (dial) | `GET /registry/mcf/readiness-projection` |
| `GET /admin/readiness/tenant/:slug/binding-candidates` | MCF entitlement drives onboarding; no candidate-audit endpoint |
| `POST /admin/readiness/tenant/:slug/bind` | `POST /schema-provisioner/onboard-metric` (or `onboard-connector`) |
| `GET /admin/readiness/tenant/:slug/formula-token-audit` | — (predicate tables dropped at R3) |
| `GET /registry/funnel-ladder` | `GET /registry/mcf/readiness-projection` |

## Common gotchas

| Symptom | Cause | Fix |
|---|---|---|
| Bound MC doesn't produce | Provisioning didn't complete; `fact.ms_<code>_v<version>` table doesn't exist | Enqueue via `onboard-metric`; run the owner-worker; poll `tenants/<slug>/provisioning`; `reissue` any `failed`-current command; then re-evaluate |
| Status never reaches `ready` | Outstanding current command in `pending`/`provisioning`/`failed` | Ensure the worker ran; `reissue` `failed` commands; abandoned (`provisioning`, lease expired) commands need the worker **sweep**, not reissue |
| Followed a `/admin/readiness/...` or `funnel-ladder` step and got 410 | That surface is retired (DEC-b049f6) | Use the MCF onboarding flow + `readiness-projection` per this chapter |
| Bound but the user can't see it on the Tenant Metrics page | Cognito user's `custom:tenant_id` doesn't match the bound tenant slug | Verify the user's profile claims |

## Cross-references

- [Tenant Onboarding](tenant-onboarding.md) — the end-to-end flow that includes binding
- [Tenancy and Binding](../operating-model/tenancy-and-binding.md) — the binding model in detail
- DEC-b049f6 — retirement of the legacy readiness/binding/funnel HTTP surface (410 pattern)
- DEC-95687d (D369) — Connector Onboarding orchestrator (chain-walk → populate-bindings → enqueue-provisioning)
- D575 Unit-3 F1 — served process holds no tenant DDL; owner-privileged provisioning worker creates fact tables out-of-process
