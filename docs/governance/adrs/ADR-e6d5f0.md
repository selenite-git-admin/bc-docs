---
uid: DEC-e6d5f0
title: "Platform-scoped tenant-readiness projection"
description: "bc-admin surfaces a tenant's downstream onboarding readiness (connections, readers, first metric snapshot) as a thin platform-scoped read model with an explicit tenant subject, composed from existing platform-side SSOTs and the sanctioned attestation bridge — never faked, and never a metric-page scope error (reconciles DEC-57c6d9)."
status: proposed
subdomain: tenant-onboarding
focus: readiness-read-model
date: 2026-09-16
project: platform
domain: tenants
refs:
  - type: decision
    uid: DEC-7df811
    label: "Tenant onboarding state model — the onboarding_record this projection reads alongside"
  - type: decision
    uid: DEC-57c6d9
    label: "Platform metric trust strip ends at Activated; tenant-runtime stages are tenant-scoped — reconciled here"
  - type: decision
    uid: DEC-b049f6
    label: "MCF-native readiness projection — the thin-read-model-over-SSOTs precedent this follows"
  - type: decision
    uid: DEC-b1a286
    label: "Schema source of truth — the platform DB is the control plane this reads"
---

# Platform-scoped tenant-readiness projection

## Context

The tenant-onboarding design names a backend requirement (implementation/tenant-onboarding.md §Handoff / §"Readiness surfaces", W2 §13.4): bc-admin must **show** each tenant's downstream onboarding progress — source connections configured, readers paired, and the first metric snapshot produced — per tenant, and the readiness view **must not be faked from the platform layer**. This is the "platform-scoped tenant-readiness projection" placed in W2 of the Platform DB Foundation program.

The requirement was written against an assumed constraint: "per-tenant reads are tenant-scoped and are not callable from the platform side." The current architecture only partially matches that assumption, and the design must be grounded in what actually exists:

- **Connections and readers are already platform-side.** `runtime.connection` (and `runtime.reader` / `runtime.reader_binding`) live in the **platform** database — the control-plane search_path includes `runtime` — and each carries a `tenant_id` with a per-tenant index. They are directly and correctly readable platform-side, filtered by tenant, via `CONTROL_PLANE_DB`. No scope-wall crossing is needed for two of the three signals.
- **The first metric snapshot is a tenant-DB outcome.** Its authoritative state lives in the tenant DB (`progression.metric_snapshot_index`), reachable only through the **one sanctioned platform→tenant read bridge**, `AttestationService` / `ATTESTATION_CLIENT` (bounded, summary-only, swappable to RPC). Tenant runtime *also* writes a per-tenant `metric.readiness_ledger` row (`source_type = 'metric_snapshot'`) on the platform side, but that write is **best-effort** (`MetricService` calls `upsertLedger(...).catch(...)` and proceeds), so the ledger is an observation aid, **not** authoritative proof of a first snapshot — its absence does not mean none was produced.
- **The tenant-scope wall is real and multi-layered** (route-prefix scope in the tenant middleware; `ScopeGuard` on `@PlatformOnly()` / `@TenantScoped()`; a fail-closed request-scoped `TENANT_DATA_DB` provider; and an AST-based CI inventory gate that refuses any unclassified `forTenantData` consumer). `AttestationService` is the single classified crossing; everything else platform-side reads only the control plane.
- **`tenant.onboarding_record`** (DEC-7df811 §2, delivered to the platform DB by the spine) already records the onboarding lifecycle (`initiated → in_progress → ready → activated | cancelled`).

There is also a governance boundary to respect. **DEC-57c6d9** removed the tenant-runtime stages (bound / evaluated / producing) from the platform **metric** trust strip, because a metric-centric platform page has *no tenant context* — it would "silently reflect one tenant's state and break the moment a second tenant exists." That decision is about a metric page. It is not a prohibition on a tenant page.

## Decision

bc-admin surfaces tenant readiness as a **thin, platform-scoped read model with an explicit tenant subject** — a `TenantReadinessProjectionService` exposed at a `@PlatformOnly()` endpoint keyed by tenant (e.g. `GET /admin/tenants/:idOrSlug/readiness`). It composes the readiness view from **existing sources of truth only**, adds **no new tenant-DB crossing and no new sync/outbox**, and never renders a placeholder as a signal.

The projection, for a given tenant:

1. **Connections configured** — read from the platform-side `runtime.connection` filtered by `tenant_id` (counts, and active/last-checked state from `runtime.connection_check`). Platform read, no bridge.
2. **Readers paired** — read from platform-side `runtime.reader` / `runtime.reader_binding` for the tenant. Platform read, no bridge.
3. **First metric snapshot produced** — answered by a **single fail-closed source: a bounded, tenant-wide snapshot-presence operation on the sanctioned `AttestationService` bridge** (the sole platform→tenant crossing), added as a new `ATTESTATION_CLIENT` contract method (e.g. `getTenantSnapshotPresence(tenantSlug)`). It is a bounded existence read over the tenant DB's `progression.metric_snapshot_index` — **tenant-wide** (has this tenant produced *any* metric snapshot; no per-metric-contract selection, so no selection ambiguity) — returning a **three-state** result: `produced` (≥1 snapshot), `none` (the bridge answered; zero snapshots), or `unavailable` (the bridge errored or was unreachable). **`unavailable` is surfaced as _unknown_ and is never conflated with `none`.** There is **no** direct `TENANT_DATA_DB` read from the platform surface. The platform-side `metric.readiness_ledger` is **explicitly non-authoritative** for this signal: its `metric_snapshot` rows are written best-effort (`MetricService` calls `upsertLedger(...).catch(...)` and proceeds), so a snapshot can exist with no ledger row — **ledger absence is not evidence of "no snapshot"** and must never be reported as `none`. The ledger MAY appear only as a clearly-labelled, non-authoritative observation hint that never determines the `produced`/`none`/`unknown` verdict.
4. **Lifecycle context** — join `tenant.onboarding_record` (and `tenant.tenants.status_code`) so the onboarding stage and the downstream readiness signals are surfaced together for the operator.

Every field is a real read of a declared SSOT or the sanctioned bridge — a `GROUP BY` or a bounded attestation call — following the same "a projection may never verdict; every number is a read, so substrate changes break loudly at review time" discipline as DEC-b049f6's `McfReadinessProjectionService`. It is a **display read model, never a gate**: it informs the operator's handoff view; it does not decide activation.

### Reconciliation with DEC-57c6d9 (the scope trap)

DEC-57c6d9 forbids tenant-runtime stages on a platform **metric** page because that page has no tenant context. This projection is a platform **tenant** page: the tenant is the explicit subject of every request (`:idOrSlug`), so it never "silently reflects one tenant's state" and never breaks with multiple tenants — the tenant context is the key. Surfacing a *named tenant's* downstream progress on a *tenant-subject* page is precisely the correctly-scoped placement DEC-57c6d9 pointed at ("bc-portal is tenant-scoped by login" for the metric case; here the platform onboarding view is tenant-scoped by subject). This decision therefore **refines**, and does not reverse, DEC-57c6d9: tenant-runtime outcomes stay off tenant-*less* platform pages, and are surfaced only where a tenant subject makes them correctly scoped.

## Alternatives considered

- **A new tenant→platform readiness sync / outbox / projection table.** Rejected. Connections/readers are already platform-side and the authoritative snapshot state is reachable via the sanctioned bridge; a new sync would duplicate existing SSOTs and add a drift surface for no new capability — the opposite of the one-SSOT-per-data-class goal.
- **Treating `metric.readiness_ledger` as the authoritative first-snapshot signal.** Rejected. Its writes are best-effort (`upsertLedger(...).catch(...)`), so ledger-absence can coexist with a real snapshot; reporting that as "no snapshot" would fake a negative — violating the no-faking premise. The ledger is retained only as a non-authoritative hint; the authoritative answer is the bounded tenant-wide attestation operation.
- **Direct platform-side reads of the tenant database on the request path.** Rejected. It breaches the tenant-scope wall (route/guard/provider/CI-gate); `AttestationService` is the only sanctioned crossing and already provides the bounded snapshot signal.
- **Faking readiness from provisioning state alone** (e.g. inferring "ready" from `tenant.tenants.status_code = active` or from schema-provisioning completion). Rejected. Provisioning completeness is not downstream data progress; the onboarding design (FR-21) forbids the UI promising what the foundation cannot evidence. The projection reports real connection/reader/snapshot signals, not a proxy.
- **Extending the platform metric trust strip to show runtime stages.** Rejected — that is exactly the metric-page scope error DEC-57c6d9 removed.

## Consequences

1. bc-admin gains an honest, per-tenant onboarding-readiness view assembled from existing SSOTs — no new mechanism, no new tenant-DB crossing, no faked signal.
2. The tenant-scope wall is preserved: two signals are native platform reads; the third uses the single sanctioned attestation bridge. The AST CI inventory gate continues to hold (no new `forTenantData` consumer is introduced on the platform surface).
3. `build == dump == live` and the SSOT model are unaffected: the projection reads, it does not write or verdict.
4. The onboarding operator view (lifecycle from `onboarding_record` + downstream readiness) is unified without conflating platform lifecycle authority with tenant runtime outcomes.

## Not decided here

- The exact endpoint shape, field names, and DTO — a follow-on bc-core implementation unit under review. That unit must **build and prove the settled first-snapshot contract above**: the new bounded tenant-wide `getTenantSnapshotPresence` attestation operation, its three-state (`produced`/`none`/`unavailable`) fail-closed semantics, and that `unavailable` never renders as `none` and ledger-absence never renders as `none`.
- Any bc-admin UI beyond the existing onboarding surface consuming this endpoint.
- Anything requiring a live database write or a gate crossing — this is a read model.
