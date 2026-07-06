---
uid: DEC-a8b33e
title: "Metric Lifecycle Funnel — canonical 7-stage ladder + single-service ownership"
description: "Locks a 7-stage funnel ladder (Seed → Contracted → Active → Platform Ready → Tenant Ready → Tenant Evaluated → Live) with strict subset semantics, named side buckets per drop, and one MetricFunnelService.getLadder() as the truth source."
status: decided
date: 2026-05-09T08:50:03.404Z
project: bc-core
domain: metrics
subdomain: lifecycle-funnel
focus: governance
---

# Metric Lifecycle Funnel — canonical 7-stage ladder + single-service ownership

## Context

Today's metric-counting surfaces (D305 chain status, D316 cumulative funnel, D389 MLS framework, D394 readiness toolkit, the bc-admin tenant-metrics page) each compute their counts independently. The audit (SES-349aa6) traced a confidence-eroding failure ('Bound: 211 of 164 catalog-ready' on bc-admin) to the lack of a locked subset discipline across surfaces. No ADR currently locks how the surfaces compose. This ADR fixes that at the root: one canonical ladder, one service that owns it, every other count surface is a projection. Subset discipline becomes structural, not vigilance-maintained.

## The 7-stage ladder

Each stage is a strict subset of the previous. Side buckets capture drop-outs by named gap.

| # | Stage | Predicate | Side bucket on drop |
|---|---|---|---|
| 1 | Seed Metrics | `metric.metric_definition WHERE status_code != 'deprecated'` | — |
| 2 | Contracted Metrics | Stage 1 ∩ `contract.metric_contract WHERE archived_at IS NULL` ∩ has resolvable `metric_definition_id` | `orphan_contracts` |
| 3 | Active Metrics | Stage 2 ∩ ≥1 `metric_contract_version.governance_state_code='active'` | `draft_only_contracts` |
| 4 | Platform Ready Metrics | Stage 3 ∩ `chain_status.chain_verdict='complete'` ∩ formula uses supported primitives ∩ `audit_status_code != 'fail'` ∩ MLS-14 passes under current enforcement mode | `chain_incomplete`, `audit_failed`, `semantic_not_evaluated` |
| 5 | Tenant Ready Metrics | Stage 4 ∩ `tenant.contract_binding` active for resolved/current version | `stale_bindings` (= `active_bindings_raw − tenant_ready`) |
| 6 | Tenant Evaluated Metrics | Stage 5 ∩ latest `progression.metric_evaluation` for current version `status='accepted'` | `dispatch_gap` |
| 7 | Live Metrics | Stage 6 ∩ fresh fact rows linked via `progression.metric_snapshot_index` to that accepted evaluation | `data_freshness_gap` |

## Stage 4 MLS-14 phrasing

Stage 4's MLS-14 clause is a predicate, not a direct table dependency. Three states:
- **passes** → counted in Platform Ready
- **fails** → side bucket `audit_failed` (or sibling, depending on failure class)
- **not evaluated** → side bucket `semantic_not_evaluated`

Under **observe-only** enforcement mode (today, while D391/D392 ship the verdict writer), `semantic_not_evaluated` is treated as pass — the ladder ramps as if MLS-14 didn't exist. Under **strict** mode (post-rollout), `semantic_not_evaluated` is treated as fail. The mode is a platform config; flipping it changes the Stage 4 count without code changes elsewhere.

## Single-service ownership

`MetricFunnelService.getLadder(tenantSlug?)` is the sole owner of the ladder's truth. Every other count surface — the three readiness dials (D394), `TenantMetricsService.getSnapshot`, `MetricReadinessService.computeCumulativeFunnel` (D316), the bc-admin Lifecycle Funnel page — becomes a projection over `getLadder()`.

Subset discipline becomes structural: by construction, no surface can return inconsistent counts because each stage is defined as a filter over the previous stage's set, computed in one place.

## Diagnostic gap names

| Drop | Side bucket | Remediation owner |
|---|---|---|
| Stage 1 → 2 | `orphan_contracts`, contracting backlog | platform team (authoring) |
| Stage 2 → 3 | `draft_only_contracts` | platform team (governance flip) |
| Stage 3 → 4 | `active_in_db_drift`: `chain_incomplete` + `audit_failed` + (`semantic_not_evaluated` in strict mode) | platform team (chain/audit fixes) |
| Stage 4 → 5 | `stale_bindings`, `unbound_eligible` | tenant operator |
| Stage 5 → 6 | `dispatch_gap` | platform/runtime |
| Stage 6 → 7 | `data_freshness_gap` | platform/data |

## Cross-references

- **AMENDS DEC-28b176** (D394 Readiness Toolkit Dials). The Bound dial counts `tenant_ready` (Stage 5), not raw active bindings. `active_bindings_raw` and `stale_bindings` survive as side diagnostics so the cleanup queue is visible and actionable.
- **EXTENDS DEC-c9e623** (D389 MLS Framework). MLS substates collapse to funnel stages: MLS-04..14 → Stage 4, MLS-19 → Stage 5, MLS-21..23 → Stage 6, MLS-24..25 → Stage 7.
- **INTEGRATES DEC-bebaec** (D305 Chain Status SSOT). Stage 4's chain-completeness predicate reads `contract.chain_status` — the same SSOT D305 locks. No competing source.
- **CONFIRMS DEC-ebf0b4** (D268 Session Discipline). This ADR is the "consistency from roots" answer — locking subset discipline structurally rather than fixing it case-by-case.

## Consequences

1. The bc-admin three dials migrate to projections of `getLadder()`. Same numbers; different source.
2. `TenantMetricsService.getSnapshot` projects from the ladder + adds the per-row blocker derivation inline.
3. `MetricReadinessService.computeCumulativeFunnel` (D316's 6-gate funnel) retires into a projection over `getLadder()`.
4. New side-bucket counts surface in operations UI: `orphan_contracts`, `stale_bindings`, `dispatch_gap`, `data_freshness_gap`.
5. MLS-14 enforcement mode becomes a platform config (observe-only by default during D391/D392 rollout).
6. `execution.chain_status` (parallel to `contract.chain_status`) needs investigation and likely deprecation. Flagged as a follow-up; not a precondition for this ADR.

## Implementation order (separate sessions)

1. This ADR (decided on file).
2. `MetricFunnelService.getLadder()` + side-bucket helpers in bc-core. Composes the existing `MetricCatalogReader` primitives + a new MLS-14 predicate helper.
3. Migrate the three dial endpoints (`/api/admin/readiness/*`) to projections.
4. Migrate `TenantMetricsService.getSnapshot` to a projection.
5. Retire `MetricReadinessService.computeCumulativeFunnel` into a projection (or thin wrapper).
6. bc-admin UI label alignment — dial labels match canonical stage names.

## Open follow-ups (not gating this ADR)

- ~~Resolve `execution.chain_status` vs `contract.chain_status` duality.~~ **Resolved 2026-05-09 / 2026-05-10:** `execution.chain_status` renamed to `execution.boundary_progression` (DEC-bebaec errata); legacy `/api/execution/chain-status` HTTP alias retired in the 2026-05-10 compat-window cleanup commit.
- MLS-14 verdict writer (D391/D392) — current enforcement mode stays `observe-only` until that ships.
- Apex tenant has ~33 stale bindings as of 2026-05-09. Cleanup or grace-period decision is a tenant-onboarding concern, not this ADR's.

## Errata

### 2026-05-09 — post-filing clarifications (SES-cb79d7)

Founder-reviewed the just-filed ADR and surfaced four naming/semantic precision issues to lock before implementation begins. The original body remains authoritative; these errata refine where the body was loose.

#### 1. Stage 4 side buckets — add `formula_unsupported`

The Stage 4 predicate includes "formula uses supported primitives", but the side-bucket column listed only `chain_incomplete`, `audit_failed`, `semantic_not_evaluated`. Add a fourth:

> `formula_unsupported` — MCs whose formula uses unsupported primitives (e.g. `SUM_BY_CATEGORY`, `ML_MODEL`). Distinct from `audit_failed` (D315 audit verdict on the MC overall) and from `semantic_not_evaluated` (MLS-14 absence).

The Stage 3 → 4 diagnostic gap row for `active_in_db_drift` therefore reads: `chain_incomplete` + `audit_failed` + `formula_unsupported` + (`semantic_not_evaluated` in strict mode).

#### 2. MLS-14 failure → `semantic_failed`, not `audit_failed`

The original wording "fails → side bucket `audit_failed` (or sibling, depending on failure class)" is muddy. Lock:

> MLS-14 hard-failure → side bucket `semantic_failed` (preserving refusal codes from the verdict). NOT `audit_failed`.

`audit_failed` and `semantic_failed` are distinct gates with distinct sources:

- `audit_failed` ← `metric_contract.audit_status_code = 'fail'` (D315 formula audit)
- `semantic_failed` ← MLS-14 verdict explicitly red, with refusal codes preserved (D391)

The two can co-occur; they are reported separately. An MC failing both lands in both buckets.

#### 3. MLS-21..25 mapping refinement

The original cross-reference said MLS-21..23 → Stage 6, MLS-24..25 → Stage 7. Refine:

- **Stage 6 (Tenant Evaluated) ← MLS-23 specifically** (latest accepted `progression.metric_evaluation` for the current MC version).
- **MLS-21 (SO produced)** and **MLS-22 (CO produced)** are upstream runtime prerequisites / subdiagnostics for Stage 6 — they describe how the chain reached MLS-23, not the stage itself.
- **Stage 7 (Live) ← fresh fact rows linked via `metric_snapshot_index`.**
- **MLS-24 (proof complete)** and **MLS-25 (KPI rendered in bc-portal)** are post-live surface checks layered on top of Stage 7. They live downstream of the funnel; an MC can be Live without being MLS-25 ready (e.g. permission/render issue in the portal). Track them separately as "post-live surface health".

Replace the body's Cross-references EXTENDS clause with the refined mapping when the ADR is next consolidated.

#### 4. Stage 1 → 2 funnel drop is `contracting_backlog`, not `orphan_contracts`

The original stage table listed `orphan_contracts` as the Stage 2 side bucket. That's wrong direction. Lock:

- **Stage 1 → 2 funnel drop = `contracting_backlog`** — definitions in Stage 1 that haven't yet been contracted (the real subset shrinkage).
- `orphan_contracts` are contracts without a resolvable `metric_definition_id` — they flow the wrong way (a contract appearing without a definition above it). They are an **off-funnel governance health** concern, not a stage drop. Track on a separate surface.

The Diagnostic gap names table in the original body correctly named both; the per-stage "Side bucket on drop" column conflated them. Reading order to lock:

| Drop | Side bucket | Notes |
|---|---|---|
| Stage 1 → 2 | `contracting_backlog` | Funnel subset drop |
| (Off-funnel) | `orphan_contracts` | Governance health, separate surface |

The implementation in `MetricFunnelService.getLadder()` returns `contracting_backlog` as the Stage 1 → 2 side bucket and exposes `orphan_contracts` as a sibling field on the response (not part of the stage chain).
