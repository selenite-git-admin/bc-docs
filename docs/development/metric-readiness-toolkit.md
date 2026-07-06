---
id: metric-readiness-toolkit
order: 41
title: "Metric Readiness Toolkit"
status: drafting
authority: authoritative
depends_on: [devhub, decision-and-change-procedure]
governing_sources:
  - Tenancy and Binding (operating-model)
  - Metric Catalog (operating-model)
  - Quality Gates and Chain Integrity (operating-model)
governing_adrs:
  - DEC-a8b33e (D397 — Metric Lifecycle Funnel; canonical 7-stage ladder is the truth source every dial in this chapter projects from)
  - DEC-4ca5a5 (D398 — Metric Landscape; the bc-admin UI consolidation that retired the Lifecycle Funnel + Tenant Metrics pages)
  - DEC-28b176 (D394 — Metric Readiness Model — three independent dials + per-formula-token audit; AMENDED by DEC-a8b33e)
  - DEC-bebaec (D305 — Chain Completeness SSOT; the readiness toolkit reads chain_status, never recomputes)
  - DEC-ebf0b4 (D268 — Session Discipline; bind operations require explicit approval per DB Change Protocol)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Metric Readiness Toolkit

The set of bc-core endpoints, bc-admin surfaces, and DevHub MCP tools that answer the operator's daily questions about the metric catalog and a tenant's pilot:

- *How many MCs in the catalog are end-to-end shippable?*
- *How many are bound to this tenant?*
- *How many are producing?*
- *Why isn't this MC producing — chain bug, mapping bug, or missing source data?*
- *Which unbound MCs would produce immediately if bound?*
- *Which authoring-shape bugs (type-mismatch / no-mapping) does the catalog still carry?*

Every endpoint is read-only except the binding endpoint, which requires explicit approval per the [DB Change Protocol](../foundation/the-contract-grammar.md).

## Five pillars, one verb each

The toolkit lives across five non-overlapping pillars. Each owns one operational question:

| Pillar | Owns | Surface |
|---|---|---|
| **Readiness** | "Is the platform/tenant ready" | `/api/admin/readiness/*` |
| **Tenant Metrics** | "Per-MC operational drill for one tenant" | `/api/admin/tenant-metrics/*` |
| **Test Bench** | "Explicit invocation primitive" | `/api/admin/test-bench/*` and `/api/t/test-bench/*` |
| **Inspector** | "Read-only chain provenance per MC" | `/api/admin/inspection/*` |
| **Schema Provisioner** | "Chain-walk-driven onboarding + reconcile" | `/api/schema-provisioner/*` |

The Readiness pillar (the subject of this chapter) is the daily diagnostic. Tenant Metrics is the per-MC drill that the dials link into. Test Bench is the explicit invocation primitive when an operator wants to actually run the chain or evaluate one metric. Inspector is the per-MC chain-provenance view (read-only). Schema Provisioner is the automated onboarding path; the Readiness `bind` endpoint is its curated counterpart.

## Canonical 7-stage funnel — the truth source these dials project from

[DEC-a8b33e (D397)](../governance/adrs/ADR-a8b33e.md) locked one canonical metric-lifecycle ladder owned by `MetricFunnelService.getLadder()` and exposed at `GET /api/admin/registry/funnel-ladder`. Every count in this chapter — every dial, every per-MC drill — is a projection of that single source. Reading the dials below as standalone numbers is a mental model that pre-dates DEC-a8b33e; the dials are window panes on the same underlying ladder.

The seven stages, each a strict subset of the previous:

| # | Stage | Predicate (summary) |
|---|---|---|
| 1 | Seed Metrics | non-deprecated `metric.metric_definition` |
| 2 | Contracted Metrics | Stage 1 ∩ non-archived `contract.metric_contract` with resolvable definition |
| 3 | Active Metrics | Stage 2 ∩ ≥1 `metric_contract_version.governance_state_code='active'` |
| 4 | Platform Ready Metrics | Stage 3 ∩ chain complete ∩ formula uses supported primitives ∩ audit not failed ∩ MLS-14 passes |
| 5 | Tenant Ready Metrics | Stage 4 ∩ active `tenant.contract_binding` for current version |
| 6 | Tenant Evaluated Metrics | Stage 5 ∩ gate-read `progression.metric_evaluation` accepted |
| 7 | Live Metrics | Stage 6 ∩ fresh fact rows linked through `metric_snapshot_index` |

Stages 1-4 are platform-wide; stages 5-7 are tenant-scoped. Side buckets capture every stage drop plus one off-funnel concern (`orphan_contracts`).

How the dials below project onto the ladder:

| Dial field | Canonical stage | Source expression |
|---|---|---|
| `Catalog Readiness.totalMcs` | Stage 3 (Active) | `ladder.stages.active` |
| `Catalog Readiness.chainComplete` | Stage 3 minus `chainIncomplete` side bucket | `ladder.stages.active - ladder.sideBuckets.chainIncomplete` |
| `Catalog Readiness.formulaSupported` | Stage 3 minus `formulaUnsupported` side bucket | `ladder.stages.active - ladder.sideBuckets.formulaUnsupported` |
| `Catalog Readiness.ready` | Stage 4 (Platform Ready) | `ladder.stages.platformReady` |
| `Tenant Readiness.bound` | Stage 5 (Tenant Ready) | `ladder.stages.tenantReady` |
| `Tenant Readiness.producing` | Stage 7 (Live) | `ladder.stages.live` |
| `Tenant Readiness.activeBindingsRaw` | Stage 5 + `staleBindings` side bucket | `ladder.stages.tenantReady + ladder.sideBuckets.staleBindings` |
| `Tenant Readiness.staleBindings` | Stage 4→5 drop | `ladder.sideBuckets.staleBindings` |
| `Tenant Readiness.wouldProduceIfBound` | Off-funnel formula-token diagnostic | per-token audit walk (not part of the ladder) |
| `tenant-metrics/snapshot.rows[].stage` | Per-row Stage 5/6/7 classification | `FunnelMembership` from `getLadder({ includeMembership: true })` |

By construction, no dial can return numbers inconsistent with another. The endpoints that follow are the operator's day-to-day surface; the canonical ladder endpoint above is the underlying truth source if a count looks wrong. The bc-admin UI surfaces all of this on a single page at `/catalog/metrics/landscape` per [DEC-4ca5a5 (D398)](../governance/adrs/ADR-4ca5a5.md).

## The three dials (Readiness pillar)

Background and rationale: [DEC-28b176 (D394)](../governance/adrs/ADR-28b176.md).

### Dial 1 — Catalog Readiness

```
GET /api/admin/readiness/catalog
→ { totalMcs, chainComplete, formulaSupported, ready }
```

Platform-wide. No tenant. **Canonical projection**: `ready` ≡ Stage 4 (Platform Ready); `totalMcs` ≡ Stage 3 (Active); `chainComplete` and `formulaSupported` derive from Stage 3 minus the relevant side bucket. The endpoint is a thin wrapper over `MetricFunnelService.getLadder()` per DEC-a8b33e. `ready = chainComplete AND formulaSupported`. Sample shape:

```json
{
  "computedAt": "2026-05-08T02:00:00Z",
  "totalMcs": 376,
  "chainComplete": 376,
  "formulaSupported": 360,
  "ready": 360
}
```

### Dial 2 — Tenant Pilot Scope

```
GET /api/admin/readiness/tenant?tenant=<slug>
→ { bound, producing, wouldProduceIfBound, activeBindingsRaw, staleBindings }
```

Per-tenant. **Canonical projection**: `bound` ≡ Stage 5 (Tenant Ready); `producing` ≡ Stage 7 (Live, strict — fresh fact rows linked through `metric_snapshot_index` to the accepted evaluation selected for the read, per DEC-a8b33e). `activeBindingsRaw` and `staleBindings` are side diagnostics: `activeBindingsRaw = bound + staleBindings` is the prior dial's number (active rows in `tenant.contract_binding`); `staleBindings` are bindings to MCs that aren't Platform Ready (Stage 4∉ladder) and form the cleanup queue. `wouldProduceIfBound` is the strict per-formula-token clean-and-unbound count and lives off-funnel because it asks a different question (would it produce *if bound*) from the ladder (does it produce for the requested read).

### Dial 3 — Pilot Health

**Canonical projection**: ratio of Stage 7 to Stage 5 (`live / tenant_ready`). The third tile on the bc-admin Tenant Metrics page, folded into the Landscape page per DEC-4ca5a5. Computed from Dial 2 (`producing / bound`) with `+N would produce if bound` as the sub-label. Movement here means data flowed for a bound MC (or a CC mapping was repaired).

## Per-formula-token audit (strict diagnostic)

```
GET /api/admin/readiness/tenant/<slug>/formula-token-audit
→ { totals, topBrokenCfs, bySubfunction, rows: [{ metricContractName, overall, tokens: [...] }] }
```

The audit underlies `wouldProduceIfBound`. For every active MC, every input variable's `field_code` is classified:

| Status | Reason | Class |
|---|---|---|
| `clean` | `populated (bf=<bf_name>)` | every gate passed |
| `broken` | `no_mapping` | no `contract.cc_field_mapping` row for this CF on any bound CC |
| `broken` | `type_mismatch (op=SUM, bf=<bf>, bf_type=date)` | numeric op (`SUM/AVG/MIN/MAX/ABS`) on a non-numeric BF (date/string/code/timestamp/boolean) |
| `broken` | `null_in_tenant (bf=<bf>, cc=<cc>)` | mapping + type compatible, but the BF column has zero non-null values in the tenant's CC fact table |

An MC is `overall: clean` only when every input field passes all three gates AND the formula text uses only supported primitives (`SUM/AVG/MIN/MAX/COUNT/COUNT_DISTINCT/ABS`).

Shape-only rollup example for a tenant catalog:

```
totals: { totalMcs: <count>, cleanMcs: <count>, brokenMcs: <count> }
broken-token reasons:
  null_in_tenant   <count>   ← upstream source-data emission gap
  type_mismatch    <count>   ← authoring-shape bug, repointable
  no_mapping       <count>   ← CF unmapped, easy fix
```

The reason categorization is the prioritization. When `null_in_tenant` dominates, the work is in source-data emission (bc-sdg / SAP simulator), not chain authoring. Use the endpoint for live counts; this chapter preserves the interpretation shape only.

## Curated binding (Readiness pillar's only writer)

```
GET /api/admin/readiness/tenant/<slug>/binding-candidates
→ list of unbound, audit-clean MCs (= the wouldProduceIfBound set, enumerated)

POST /api/admin/readiness/tenant/<slug>/bind
  body: { metricContractIds: string[] }
→ { inserted, alreadyPresent, skipped }
```

This path is **curated**: the operator picks a subset and binds explicitly. It's the right shape for demo work and for tightly-scoped pilots where the operator wants to control which metrics are activated.

The complementary path is Schema Provisioner's `POST /api/schema-provisioner/onboard-connector`, which walks the chain forward from a connector and binds everything reachable. It's the right shape for tenant onboarding when the tenant should activate the full chain.

After binding, a separate reconcile call provisions `fact.ms_*_v*` tables: `POST /api/schema-provisioner/nightly-reconcile` (idempotent; affects all tenants that need provisioning).

## When to use which

| Question | Endpoint |
|---|---|
| "Is the catalog shippable?" | `GET /admin/readiness/catalog` |
| "What's this tenant's pilot health?" | `GET /admin/readiness/tenant?tenant=<slug>` |
| "Which MCs would produce if I bound them?" | `GET /admin/readiness/tenant/<slug>/binding-candidates` |
| "Why is this catalog broken — authoring or source data?" | `GET /admin/readiness/tenant/<slug>/formula-token-audit` |
| "I want to bind these specific MCs to this tenant" | `POST /admin/readiness/tenant/<slug>/bind` |
| "Show me the per-MC drill for this tenant" | `GET /admin/tenant-metrics/snapshot?tenant=<slug>` |
| "Run this metric for this tenant on demand" | `POST /admin/test-bench/evaluate-mc-for-tenant` |
| "Show me the chain provenance for this MC" | `GET /admin/inspection/header/...` (and other Inspector views) |
| "Onboard this connector to this tenant (full chain)" | `POST /schema-provisioner/onboard-connector` |

## DevHub MCP wrappers

Three tools wrap the Readiness pillar so Claude sessions don't need curl-with-token plumbing:

| Tool | Wraps |
|---|---|
| `devhub_readiness_dial` | `GET /admin/readiness/{catalog,tenant}` |
| `devhub_formula_token_audit` | `GET /admin/readiness/tenant/<slug>/formula-token-audit` |
| `devhub_tenant_bind_metrics` | `POST /admin/readiness/tenant/<slug>/bind` (with explicit approval gate per [D268](../governance/adrs/ADR-ebf0b4.md)) |

The bind tool defaults to dry-run (returns the candidates that *would* be bound) and requires `confirm: true` to execute. This honours the DB Change Protocol — bindings are platform-DB writes that need approval. `evaluate-mc-for-tenant` is not yet wrapped; use the curl path until it is.

## Deprecations

`GET /api/admin/test-bench/survey-mcs` (introduced SES-61f2f6) was a per-subfunction 8-layer audit. It is subsumed by the Readiness pillar:

- The 8-layer breakdown is redundant with the four-gate audit (no_mapping / type_mismatch / null_in_tenant / structural)
- The per-MC operational view is `/admin/tenant-metrics/snapshot`
- The binding-candidates view is `/admin/readiness/tenant/<slug>/binding-candidates`

The route is removed in commit `<filled at deprecation time>`; the `ArSurveyService` source file is also dropped.

## Operating cadence

- **Per session (Claude or operator)**: open session → call `devhub_readiness_dial` for the relevant tenant → if a number is wrong, call `devhub_formula_token_audit` to see why → fix or bind → re-call dial to verify movement → close session.
- **Weekly**: re-run `devhub_formula_token_audit` for each tenant; watch the `null_in_tenant / type_mismatch / no_mapping` breakdown for drift; file follow-ups when reason categories change unexpectedly.
- **Per change**: when an MC, CC, or BF is added or modified, the audit is the verification. Don't trust the engine's "evaluation accepted" alone — check the audit too, because the engine accepts numerically-coerced strings (e.g. `Number("2025") = 2025`) which the audit correctly flags as `type_mismatch`.

## Cross-references

- ADR: [DEC-28b176 (D394)](../governance/adrs/ADR-28b176.md) — full design rationale and the predicate-tightening journey
- Operating model: [Tenancy and Binding](../operating-model/tenancy-and-binding.md) — what `tenant.contract_binding` is and how it relates to the chain
- Operating model: [Metric Catalog](../operating-model/metric-catalog.md) — the catalog primitives the toolkit reads from
- Demo plan: [CFO Pack Demo Plan](../evidence/work-records/operating-model/demo-plan-cfo-pack.md) — the toolkit's role in delivering the CFO Pack demo
