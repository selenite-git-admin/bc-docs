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
  - Metric Readiness Toolkit (development)
governing_adrs:
  - DEC-a8b33e (D397 — Metric Lifecycle Funnel; binding is the Stage 4 → Stage 5 transition)
  - DEC-28b176 (D394 — Metric Readiness Model; AMENDED by DEC-a8b33e)
  - DEC-bebaec (D305 — Chain Completeness SSOT)
  - DEC-ebf0b4 (D268 — Session Discipline; bind operations require explicit approval per DB Change Protocol)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Tenant Metric Binding

How an operator binds metric contracts to a tenant — i.e. activates which MCs evaluate against which tenant's canonical-object data. Every binding is a platform-DB write and so falls under the [DB Change Protocol](../foundation/the-contract-grammar.md): present the list to the user, get explicit approval, only then execute.

**Canonical lifecycle context.** Per [DEC-a8b33e (D397)](../governance/adrs/ADR-a8b33e.md), binding is the **Stage 4 → Stage 5** transition in the metric lifecycle ladder: from Platform Ready (an MC that's chain-complete, formula-supported, audit-passing, and MLS-14-clean) to Tenant Ready (the same MC with an active `tenant.contract_binding` for the tenant). A binding to an MC that *isn't* Platform Ready does not move it into Stage 5 — it counts as a `staleBindings` side-bucket diagnostic instead. Verify Platform Readiness *before* binding (see [Metric Readiness Toolkit](../development/metric-readiness-toolkit.md) Dial 1) so newly-inserted bindings actually advance the ladder.

This chapter documents two paths: **curated binding** (you pick specific MCs) and **chain-walk binding** (you bind everything reachable from a connector). They are complementary; neither is a fallback for the other. The operational situation determines which path to take.

## When to bind metrics to a tenant

Three triggers:

| Trigger | Path |
|---|---|
| New tenant onboarding — the tenant should receive the full chain reachable from their connector | Chain-walk (`/schema-provisioner/onboard-connector`) |
| Demo / pilot — operator picks a curated subset of MCs to activate | Curated (`/admin/readiness/tenant/<slug>/bind`) |
| Existing tenant — adding one or more new metrics post-onboarding | Curated (binding-candidates → bind) |

Binding does not produce data on its own. It declares which MCs are scoped for evaluation in the tenant. The full sequence to actually see results is `bind` → **provision (owner-worker)** → `evaluate`.

## Path A: Curated binding (the daily-operator path)

Use when you want to activate a specific list of MCs. Common case: demo build-up, pilot expansion, or one-at-a-time additions.

### Step 1: Find the binding candidates

```
GET /api/admin/readiness/tenant/<slug>/binding-candidates
```

Returns the strict candidate list — unbound MCs whose every formula token passes the audit (`cc_field_mapping` resolves; BF data type is compatible; BF column is populated in the tenant). These are MCs that *will* produce on first evaluation if bound.

DevHub MCP wrapper: not yet wired. Use the curl path with an admin Cognito token.

The candidates are ranked by clarity: each entry has the MC's name, function/subfunction, version code, and the CC IDs it depends on. Pick the subset relevant to the operator's intent.

### Step 2: Present the list to the user, get explicit approval

Per DB Change Protocol, do **not** proceed without showing the operator the specific MC list and getting explicit approval. The DevHub MCP wrapper `devhub_tenant_bind_metrics` defaults to dry-run for this reason — calling without `confirm: true` returns the list that *would* be bound, plus the protocol instructions.

### Step 3: Bind

```
POST /api/admin/readiness/tenant/<slug>/bind
Body: { "metricContractIds": ["uuid-1", "uuid-2", ...] }
```

Idempotent. Returns `{ inserted, alreadyPresent, skipped }`. `inserted` lists newly-bound MCs; `alreadyPresent` means they were already bound (no change); `skipped` lists MCs that couldn't be bound (no active version, etc.) with a reason per skip.

Or via DevHub MCP:

```
devhub_tenant_bind_metrics tenant=<slug> metric_contract_ids=[...] confirm=true
```

### Step 4: Provision the fact tables (owner-worker, out-of-process)

The bind endpoint does not create `fact.ms_<mc-code>_v<version>` tables — the served process holds **no tenant DDL capability** (D575 Unit-3 F1). **`POST /api/schema-provisioner/nightly-reconcile` no longer exists** (removed): the nightly reconcile + activation-fanout safety net now runs inside the **owner-privileged provisioning worker** (`provisioning-worker-cli.ts --sweep`), never in a served endpoint.

As-built provisioning path:

1. **Enqueue** provisioning via `POST /api/schema-provisioner/onboard-metric` (tenant slug + the entitled MCF metric + environment) — returns **202 Accepted**; it reverse-walks the MCF metric to its Canonical/Source Contracts and enqueues a governed provisioning command per desired `fact.*` table. (For a whole connector, `POST /api/schema-provisioner/onboard-connector`.)
2. The **owner-privileged provisioning worker** (out-of-process; needs `TENANT_OWNER_DATABASE_URL`, absent from the served process) creates the tables, and runs the periodic sweep.
3. **Poll** `GET /api/schema-provisioner/tenants/<slug>/provisioning` — a read over the append-only command store; `ready` is true iff every *current* command is `provisioned` (obsolete/superseded commands stay visible but are not outstanding).
4. A `failed`/abandoned command is recovered through the governed `POST /api/schema-provisioner/provisioning/commands/<id>/reissue` (requires a rationale); the worker's next drain claims it.

Idempotent throughout: new fact tables are created where missing; existing ones stay.

### Step 5: Verify

```
GET /api/admin/readiness/tenant?tenant=<slug>
```

Or via MCP: `devhub_readiness_dial tenant=<slug>`.

The dial should show:
- `bound` (Stage 5, Tenant Ready) increased by the number of newly-inserted bindings *that hit Platform Ready MCs*. Bindings to non-Platform-Ready MCs land in `staleBindings` instead — verify with `staleBindings` not jumping unexpectedly.
- `producing` (Stage 7, Live) may or may not have moved (depends on whether the new MCs have already evaluated and whether snapshot rows linked through `metric_snapshot_index`).
- `wouldProduceIfBound` should drop by the number of newly-bound audit-clean MCs.

If the canonical funnel ladder is the source of truth you'd rather verify against directly: `GET /api/admin/registry/funnel-ladder?tenant=<slug>` returns `stages.tenantReady` (Stage 5), `stages.tenantEvaluated` (Stage 6), `stages.live` (Stage 7), and `sideBuckets.staleBindings` in one call.

To force-evaluate the newly-bound MCs and produce snapshots:

```
POST /api/admin/test-bench/evaluate-mc-for-tenant
Body: { "metricContractId": "<uuid>", "tenant": "<slug>" }
```

Per MC. After evaluation, the dial's `producing` count moves accordingly.

## Path B: Chain-walk binding (tenant onboarding)

Use when a new tenant is onboarding and should receive the full chain. The operator names the connector; the platform walks the chain forward, binds every reachable contract (source / canonical / metric), and reconciles the tenant DB in one call.

```
POST /api/schema-provisioner/onboard-connector
Body: { "tenantSlug": "<slug>", "connectorId": "<uuid>", "environment": "development" }
```

What happens:

1. The connector chain walker resolves all contracts reachable from the connector
2. `tenant.tenant_binding` rows are written for source contracts (per-environment)
3. `tenant.contract_binding` rows are written for canonical / metric / intervention contracts (`is_active=true`)
4. The onboarding **enqueues** a governed provisioning command per desired `fact.*` table (**202 Accepted**); the **owner-privileged provisioning worker** creates the tables out-of-process — poll `GET /api/schema-provisioner/tenants/<slug>/provisioning` for readiness (the served process holds no DDL — D575 Unit-3 F1). `nightly-reconcile` is not part of this path (removed; it lives in the worker `--sweep`).

This is the right path when the operator's intent is "give this tenant everything this connector can produce." It is **not** the right path when the operator wants to activate a specific subset — that's curated binding.

The path does not skip the DB Change Protocol — but the protocol is satisfied at the connector level, not the per-MC level. The operator approves "onboard this connector to this tenant" once; the binding fans out from there.

## Common gotchas

| Symptom | Cause | Fix |
|---|---|---|
| Bound MC doesn't produce | Provisioning didn't complete; `fact.ms_<code>_v<version>` table doesn't exist | Enqueue via `onboard-metric`; wait for the owner-worker (poll `tenants/<slug>/provisioning`); `reissue` any failed command; re-evaluate |
| Reconcile ran but MC still doesn't produce | The MC has unresolved formula-token issues (`null_in_tenant`, `type_mismatch`, or `no_mapping`) | `formula-token-audit` to identify; fix at the cc_field_mapping or source-data layer |
| `binding-candidates` returns empty list, but the operator expected MCs to be available | The audit filter may be too tight — every MC has at least one broken token | Run `formula-token-audit`; fix the highest-frequency broken CFs first |
| Bound but the user can't see it on Tenant Metrics page | Cognito user's `custom:tenant_id` doesn't match the bound tenant slug | Verify the user's profile claims |
| Binding "skipped" with `no_active_version` reason | The MC has no active `metric_contract_version` row | Activate the contract version first via the metric onboarding flow |

## Rollback

A binding's `is_active` flag is toggled through the **governed** endpoint — **never** a direct SQL `UPDATE` on `tenant.contract_binding` (raw DB-row hand-edits are prohibited by the Session Discipline / DB Change Protocol, DEC-ebf0b4/D268):

```
PATCH /api/function-admin/<functionCode>/metrics/<mcUid>/binding    (governed is_active toggle)
```

⚠ **Disable is cosmetic — it does NOT stop engine evaluation.** Per the endpoint's own contract, setting `is_active=false` is a catalog/display state, **not** an evaluation gate: it does not delete the binding row, drop the fact table, or remove existing snapshots, and it does **not** stop the metric evaluating for the tenant. **Do not rely on it to actually halt a metric.** (This corrects the prior wording, which wrongly claimed deactivation "stops the chain from evaluating.") The mechanism that genuinely halts evaluation for a tenant MC is **not** this toggle and is not yet established here — verify against the evaluation-scheduler / binding source before asserting a stop. A governed, evaluation-affecting unbind is a **documentation/verification gap** to close.

For chain-walk bindings, unwinding runs through the connector offboarding flow, not a per-MC toggle.

## When to use which path

| You want to … | Use |
|---|---|
| Activate one or two specific MCs for a tenant | Curated bind |
| Give a new tenant everything reachable from their connector | Chain-walk via onboard-connector |
| Build up a demo's metric set incrementally | Curated bind |
| Toggle a single MC's binding `is_active` flag (**cosmetic — does NOT stop evaluation**) | Governed `PATCH /function-admin/<fn>/metrics/<mcUid>/binding` (never a raw SQL UPDATE) |
| Disable an entire connector's reach for a tenant | Connector offboarding flow (out of scope here) |

## Cross-references

- [Metric Readiness Toolkit](../development/metric-readiness-toolkit.md) — the endpoint catalog this chapter operationalises
- [Tenancy and Binding](../operating-model/tenancy-and-binding.md) — the binding model in detail
- [MC Chain Integrity](../archive/onboarding/mc-chain-integrity.md) — verifying the MC chain is shippable before binding
- [Tenant Onboarding](tenant-onboarding.md) — the end-to-end flow that includes binding
- [ADR-a8b33e (D397 — Metric Lifecycle Funnel)](../governance/adrs/ADR-a8b33e.md) — the canonical 7-stage ladder; binding is the Stage 4 → 5 transition
- [ADR-28b176 (D394 — Metric Readiness Model)](../governance/adrs/ADR-28b176.md) — the readiness predicate behind `binding-candidates`; AMENDED by DEC-a8b33e
