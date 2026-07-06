---
uid: DEC-f0e78e
title: "Platform/tenant authority boundary — distinct classes; narrow platform-inspection carve-out"
description: "Distinct identity classes (platform-admin XOR tenant-member); /api/t/* tenant route boundary unchanged; new /api/admin/inspection/* read-only platform family with explicit tenant parameter and synchronous audit; amends ADR-952faa D-4."
status: decided
date: 2026-04-29T05:51:07.179Z
project: bc-core
domain: security
subdomain: authority-boundary
focus: governance
---

# Platform/tenant authority boundary — distinct classes; narrow platform-inspection carve-out

## Context

The D386 Stage 2 smoke (SES-0c5010, 2026-04-29) attempted to read tenant-scoped Inspector data from a platform-admin user via x-tenant-id header. ScopeGuard correctly rejected the attempt (403 "requires 'tenant' scope (your scope: 'platform')") so no data leaked, but the attempt itself revealed two coupled issues: (1) the Cognito user pool admits identities that simultaneously carry platform_admin in custom:roles AND custom:tenant_id, allowing one JWT to encode both authorities; (2) ADR-952faa D-4's "operator drilldown" wording implied a platform admin could satisfy tenant scope by adding a header — which would have been a bypass on a foundation-level boundary if implemented.

Founder decision: reject the shared boundary. Authority classes are distinct, /api/t/* stays tenant-only, and platform inspection is its own narrowly named, read-only, audited carve-out — not impersonation. ScopeGuard is unchanged on the tenant dimension; the carve-out lives on a separate route family that is explicitly platform-admin-guarded, never available to routine platform services, never to write verbs, and never reachable via x-tenant-id on tenant routes.

This is recorded as proposed pending procedural review of the recorded artifact; founder direction has been accepted on the substantive content.

## Context

ADR-952faa D-4 (D386 Stage 2 Metric Inspector) specified an "operator drilldown surface" used from bc-admin (a platform-only application) to read per-tenant metric chain state. The wording implied an operator could pivot to any tenant via an `x-tenant-id` header on tenant-scoped routes.

Live JWT inspection during SES-0c5010 (2026-04-29) showed:

1. The Cognito user pool `ap-south-1_bM5xehxIx` admits identities that hold both `platform_admin` (in `custom:roles`) and `custom:tenant_id`. Both `anant@selenite.co` (intended platform admin) and `anant+sandbox1@selenite.co` (intended sandbox1 operator) carried this dual shape.
2. ScopeGuard correctly rejected platform-scoped users on `/api/t/*` routes with `403 "This endpoint requires 'tenant' scope (your scope: 'platform')"`. So no tenant-private data was leaked. But the spec carried an unsafe assumption that, if pursued, would have introduced a platform-to-tenant bypass on tenant routes.

Founder direction (2026-04-29): reject the shared boundary. Lock authority classes as distinct.

## Decision

### D-1. Authority classes are distinct and mutually exclusive at the identity-provider level

A Cognito identity is platform-admin XOR tenant-member. Mutual exclusion is enforced at provisioning. No JWT carries both `platform_admin` and `custom:tenant_id`.

- **Platform-side roles** live only on platform identities: `platform_admin`, `schema_author`, and any future platform-operational roles.
- **Tenant-side roles** live only on tenant identities: `operator`, `analyst`, and other intra-tenant roles.
- `schema_author` is **platform-side**. If tenant-local authoring is later needed, a distinct tenant-side role name is created. `schema_author` is not reused across the boundary.
- A human who legitimately needs both authorities holds **two distinct Cognito identities**, signs in twice, and never blends them in a single request. One JWT carries one authority class.

### D-2. The tenant-scoped route family `/api/t/...` is for tenant identities only. ScopeGuard is unchanged on this dimension

ScopeGuard does **not** learn that `platform_admin` satisfies tenant scope. There is **no** "platform-admin-on-behalf-of-tenant" mode on tenant routes. `x-tenant-id` from a platform identity is rejected. The existing 403 with body `"This endpoint requires 'tenant' scope (your scope: 'platform')"` is the correct runtime contract and stays.

### D-3. Inspector reads are served via a new platform-inspection route family — narrowly carved, read-only, audited, attestation-mediated for tenant data

**Amended 2026-04-29** by founder ruling (Option 2 §2a — see Errata).

Mount point: `/api/admin/inspection/...`, platform-admin-guarded, read-only.

The inspection target is an **explicit query/path parameter**, not a header:

```
GET /api/admin/inspection/metrics/:metricDefinitionId/header        ?tenant=<slug>
GET /api/admin/inspection/metrics/:metricDefinitionId/chain         ?tenant=<slug>
GET /api/admin/inspection/metrics/:metricDefinitionId/monitor       ?tenant=<slug>
GET /api/admin/inspection/metrics/:metricDefinitionId/semantics     ?tenant=<slug>
GET /api/admin/inspection/metrics/:metricDefinitionId/audit         ?tenant=<slug>
GET /api/admin/inspection/metrics/:metricDefinitionId/tenants                   (no tenant param — pivot across all)
GET /api/admin/inspection/metrics/:metricDefinitionId/cross-pivots              (no tenant param — platform-wide)
```

**Tenant data is accessed only via the bounded attestation contract defined in D-6, never via direct platform-side reads of tenant tables.** The platform-inspection module (`AdminInspectionModule`) does not import `TenantConnectionService`, does not hold tenant DB credentials, and runs no SQL against tenant DBs. For sections that need tenant data (Header, Chain spine, Monitor pane), the module calls an internal `AttestationClient`. Tenant DB access lives entirely in `AttestationModule`, which is the only module with `TenantConnectionService` as a dependency. Sections that need no tenant data (Tenant pivot, Semantic checks, Audit log, Cross-pivots) do not call the attestation; they read platform DB only.

The attestation contract returns bounded scalar/summary results — never raw rows, never row arrays, never unbounded SELECTs — per D-6.

Response payloads carry an `inspection_meta` envelope `{ operator_user_id, target_tenant, observed_at }` so the surface is self-evidently a platform read, not a tenant request.

The route family is **read-only**. No write verbs ever live under `/api/admin/inspection`.

**Deployment topology.** Same-process is acceptable as the v1 implementation (§2a in the 2026-04-29 decision packet) provided the code boundary above is enforced — `AdminInspectionModule` and `AttestationModule` are distinct NestJS modules with independently auditable dependency graphs. Process split (§2b — separate tenant-runtime container without platform DB credentials, separate platform-inspection container without tenant DB credentials) is a future deployment-only change available without code rework if compliance posture demands it.

### D-4. The Inspector implementation in TSK-614ff6's local checkpoint commits is rework, not just rebase

Routes move from `/api/t/metrics/:uid/inspector/*` + `/api/metrics/:uid/inspector/*` to `/api/admin/inspection/metrics/:uid/*`. The bc-admin tenant-slug header injector is replaced by an explicit tenant query param — which also removes the misleading "tenant slug input" UX (it was a header injector pretending to be a tenant context). Pure-helper unit tests (`semantic-checks.spec.ts`) survive unchanged.

The local checkpoint commits (`a04720f` on bc-core, `d84ebf4` on bc-admin) stay as historical snapshot of the rejected design and are not pushed.

### D-5. Every platform-inspection read is audit-logged synchronously

New table **`platform.platform_inspection_audit`** (DDL change — requires explicit user approval per Database Change Protocol). Columns:

```
audit_id            uuid pk
actor_user_id       uuid                 -- Cognito sub
actor_email         text                 -- denormalised for forensic readability, captured at write time
route               text                 -- e.g. /api/admin/inspection/metrics/:uid/header
target_tenant_slug  text                 -- nullable for tenant-pivot/cross-pivot reads
target_resource_id  text                 -- e.g. metric_definition_id
request_id          text                 -- correlation id
result_state        text                 -- 'ok' | 'unavailable' | 'broken'  (NOT the payload)
observed_at         timestamptz
```

Indexes: `(observed_at desc)` and `(actor_user_id, observed_at desc)`. Platform DB only.

**Audit-failure rule (fail closed):** if `platform_inspection_audit` cannot be written, the inspection read returns `state: 'broken'` with `reason_code: 'audit_log_unavailable'`. No silent reads. No unaudited footprint.

Retention and rotation are **out of scope for this ADR** — deferred to a separate operations/compliance decision. Durable audit rows and the indexes above are required by this ADR; lifecycle is not.

### D-6. Tenant attestation contracts (bounded summaries, never raw rows)

**Added 2026-04-29** by founder ruling (Option 2 §2a — see Errata).

Three attestation operations cover every tenant-data dependency of the seven Inspector sections. Each returns scalars or short summaries with enumerated fields. None returns row arrays. None returns raw payloads, evidence blobs, or formula evaluations.

#### `GetMetricLatestEvaluationSummary(tenant_slug, metric_contract_id)`

```
{
  has_any_evaluation: boolean,
  proof_status:       'complete' | 'partial' | 'degraded' | null,
  evaluated_at:       ISO-8601 timestamp | null,
  run_id:             string | null,
  status:             'accepted' | 'rejected' | null,
}
```

Used by Inspector Header (`proof_status`, `evaluated_at`, `run_id`) and Inspector Monitor pane (`latest_evaluation`).

#### `GetMetricRuntimePresenceSummary(tenant_slug, metric_contract_id)`

```
{
  metric_snapshot_count:           non-negative integer,
  canonical_object_accepted_count: non-negative integer,
}
```

Used by Inspector Chain spine.

#### `GetMetricMonitorCounts(tenant_slug, metric_contract_id)`

```
{
  evaluation_count: non-negative integer,
  snapshot_count:   non-negative integer,
}
```

Used by Inspector Monitor pane.

#### Implementation rules

- **AttestationModule is the only module with tenant-DB access** (via `TenantConnectionService`). `AdminInspectionModule` does not import `TenantConnectionService`. Nothing else in bc-core's platform-inspection surface reaches into tenant DBs except via the three operations above.
- **`AttestationClient`** is the public surface inside `AdminInspectionModule`. It is the bridge between the route handler and the tenant-side runtime. Implementation may be in-process method calls (§2a) or RPC (§2b); the contract is identical.
- **Audit (D-5) is written by the platform-inspection handler**, not by the attestation. Each inspection request produces exactly one `operations.platform_inspection_audit_log` row, regardless of whether attestation was called.
- **No section is allowed to make additional tenant-side calls outside the three operations above.** Adding a new attestation operation is an ADR-level change (amendment to D-6).
- **Combining MAY happen internally.** The implementation may merge `GetMetricMonitorCounts` and the count fields of `GetMetricLatestEvaluationSummary` into a single combined monitor attestation if cleaner. The external contract — three operations with the field shapes above — is the audit-reviewable surface and is not changed by such an implementation refactor.
- **Sections that need no tenant data (Tenant pivot, Semantic checks, Audit log, Cross-pivots) do not call the attestation.** Attempting to do so is a bug, not an architectural option.

#### What attestation responses NEVER contain

- Row arrays (no list of evaluations, snapshots, COs, observation rows, etc.)
- Raw payloads, evidence blobs, formula evaluations, intermediate values
- Tenant-private data not enumerated in the three contract shapes above
- JSON blobs containing tenant-side row data

#### Failure handling

If `AttestationClient` throws (tenant runtime down, timeout, schema mismatch, contract version skew), the affected section returns `state: 'unavailable'` (preferred — known failure mode) or `state: 'broken'` (unknown failure mode) with a reason code. The audit row (D-5) is still written and records the section's `result_state`.

## Identity-provisioning remediation (decision lists corrections; runbook is a separate task)

Per D-1, applied to current Cognito pool `ap-south-1_bM5xehxIx`:

| User | Current claims | Required claims |
|---|---|---|
| `anant+sandbox1@selenite.co` | `custom:roles=["platform_admin","schema_author","operator","analyst"]`, `custom:tenant_id=sandbox1` | Strip `platform_admin` and `schema_author` (both platform-side per D-1). Keep tenant-side roles (e.g. `operator`, `analyst`). Keep `custom:tenant_id=sandbox1`. |
| `anant@selenite.co` | `custom:roles=["platform_admin","schema_author","operator","analyst"]`, `custom:tenant_id=demo-selenite` (stale) | Keep `platform_admin` and `schema_author` (both platform-side). Strip `operator` and `analyst` (both tenant-side per D-1). Unset `custom:tenant_id` entirely. |

Dual-authority humans (e.g. founder needing both views): allowed only as **two separate Cognito identities**. Never one JWT carrying both authority classes. Remediation runbook includes a split-account path where needed.

The remediation task starts with a pool-wide claim audit; unknown how many other users currently hold dual shape.

## What this ADR explicitly does NOT do

- Does **not** introduce a "platform admin reading on behalf of a tenant" mode on tenant routes
- Does **not** change ScopeGuard's tenant-scope enforcement
- Does **not** allow tenant impersonation; the new routes never assert "the operator is acting as the tenant"
- Does **not** open `/api/admin/inspection/*` to write verbs
- Does **not** silently degrade audit (audit failure → fail closed)
- Does **not** make the `/api/admin/inspection/*` carve-out available to routine platform services — it is reserved for explicit platform-admin inspection use only

## Compliance

- **Preserves the `/api/t/*` tenant route boundary unchanged.** ScopeGuard's tenant-scope enforcement on `/api/t/*` is the runtime contract and is not weakened.
- **Rejects tenant impersonation and shared-scope requests.** No request carries both authority classes. No platform identity passes for a tenant identity by adding a header.
- **Amends/clarifies D232/D368** ("Platform NEVER queries tenant DB") with a **single named, read-only, audited platform-inspection carve-out** living under `/api/admin/inspection/*`. The carve-out is **not available to routine platform services**, **not available to write verbs**, and **not available through `x-tenant-id` on tenant routes**.
- **Amends ADR-952faa D-4.** ADR-952faa as a whole stays; only D-4's implicit shared-boundary phrasing is corrected here. ADR-952faa D-1, D-2, D-3, and D-5+ are unaffected.
- Aligns with foundation authority class separation. Cognito invariant `(platform_admin in roles) XOR (tenant_id is set)` becomes a checkable rule, auditable in one query.

## Consequences

**Positive:**
- Foundation `/api/t/*` boundary preserved with no exception clauses
- Single, narrow, named platform-inspection carve-out — easy to audit in code search and access logs
- Inspector responses self-evidently platform reads via `inspection_meta` envelope
- Cognito invariant is checkable; provisioning regressions detectable

**Negative:**
- Inspector v1 work in commits `a04720f` (bc-core) and `d84ebf4` (bc-admin) is rework, not rebase
- Cognito remediation requires a coordinated push (no users left with mismatched JWTs in transient state)
- New audit table is a DDL change (Database Change Protocol — explicit approval required before DDL)
- Pool-wide claim audit needed to scope remediation effort

## Out of scope (separate decisions / tasks)

- Audit retention and rotation policy
- Mapping of intra-tenant roles (`operator`, `analyst`, etc.) — outside the platform/tenant boundary question
- Inspection redaction policy (mask tenant PII in operator views) — separate ADR if substantial
- bc-portal regression check after Cognito remediation — tracked as a follow-up task

## Errata

### 2026-04-29 — Q1: physical schema and table name

D-5 specifies a new audit table written as `platform.platform_inspection_audit`. The physical artifact landed in TSK-6e8174 under a different name to align with existing platform-DB conventions:

- **Physical table:** `operations.platform_inspection_audit_log`

`bc_platform_dev` has no `platform` schema; `01-platform-schemas.sql` declares twelve schemas (`contract`, `metric`, `source`, `runtime`, `master`, `tenant`, `users`, `operations`, `execution`, `pricing`, `infrastructure`, `support`). Per D089 convention, audit-style tables (`operations.audit_log`, `operations.activity_log`, `operations.catalog_verification_log`, `operations.bo_enrichment_log`, `operations.nullification_action`, etc.) live in the `operations` schema. The `_log` suffix follows the same convention.

**D-5 semantics are preserved unchanged.** The synchronous-audit-on-every-read rule, the fail-closed-on-audit-failure rule, the columns enumerated in D-5, the two indexes, and the platform-DB-only constraint all hold against the renamed physical artifact. Only the schema and table identifiers differ from the literal D-5 wording, which the founder ruling treats as descriptive intent rather than a load-bearing physical contract.

Implementation references in TSK-6e8174:

- DDL forward: `bc-core/docker/redesign/migrations/20260429-d388-platform-inspection-audit.sql`
- DDL revert: `bc-core/docker/redesign/migrations/20260429-d388-platform-inspection-audit.revert.sql`
- Drizzle schema: `bc-core/src/database/schema/operations/platform-inspection-audit-log.ts`
- Service shape: `bc-core/src/admin-inspection/platform-inspection-audit.service.ts`

Founder ruling 2026-04-29 (Q1 → option A: convention-aligned name).

### 2026-04-29 (later) — D-3 amended, D-6 added (attestation model)

Founder ruling 2026-04-29 on the decision packet "platform-vs-tenant boundary for D386 Inspector" (Option 2 §2a):

D-3's original wording said "Server-side, tenant-target sections open the tenant DB only inside this route family, via `TenantConnectionService.forTenantData(dbName)`." That mechanism is **rejected** for D386 Inspector. D-3 is replaced with attestation-mediated tenant access; D-6 is added defining the three bounded attestation contracts.

**Why the change.** Customer/compliance posture is materially stronger when platform-side code holds no tenant DB credentials and tenant data flows out only as bounded summaries through a defined contract. The original direct-DB-read mechanism — even framed as a narrow carve-out — would have left the platform process holding both sets of credentials with discipline as the only boundary. The amended D-3 + new D-6 enforce a code-level boundary (`AdminInspectionModule` cannot import `TenantConnectionService`) that survives external compliance scrutiny and customer DPA disclosure.

**§2a deployment is the v1 starting point.** Same-process, two-module split: `AdminInspectionModule` calls `AttestationClient`; `AttestationModule` is the only code with tenant DB access. Real code boundary; light deploy cost. Migration to §2b (separate process for tenant-runtime) is a deployment-only change, not a code change, and is an available future option if compliance posture demands it. §2b is not committed; it is recorded here as the next available step on the same architectural line.

**Discovery finding that informed the choice.** Trace of every Inspector section showed that 4 of 7 sections (Tenant pivot, Semantic checks, Audit log, Cross-pivots) need no tenant data at all, and the 3 that do (Header, Chain spine, Monitor pane) need at most one summary row + a few counts each. No section needs raw tenant rows. The attestation contracts in D-6 are sized to that finding.

**Effect on TSK-da749e.** Rescoped: implement `/api/admin/inspection/*` + `AttestationModule` + `AttestationClient` per the amended D-3 / new D-6. Direct-tenant-DB-read variant is rejected. `AdminInspectionModule` must not import `TenantConnectionService`. Audit every read; fail closed on audit failure (D-5 unchanged).

**Effect on TSK-831aa2.** Scope reduces to platform-only-section SQL fixes (the `Tenant pivot` and `Cross-pivots` queries that hit `tenant.contract_binding` / `contract.observation_field_map` with stale column names). The tenant-side query bugs that were also in the rejected service (`progression.metric_evaluation`, `progression.metric_snapshot_index`) become moot — those queries do not exist in the new architecture; their data flows through the D-6 attestation contracts instead.

**Effect on TSK-296271 (future).** When the deferred chain-status `proof_degraded` integration is implemented, it consumes attestation outputs (or future projection outputs), not direct tenant DB reads from `ChainStatusService`. No work in this turn.

**Decision packet of record.** "Platform-vs-tenant boundary for D386 Inspector" — produced 2026-04-29, founder ruling same day. Option 1 (direct DB read) and Option 3 (projection) considered and rejected for this stage. Option 3 may become the right model later if compliance/staleness tradeoffs change; this amendment does not foreclose it.

### 2026-04-29 (later still) — Tenant pivot eligibility + selector UX clarification

Founder ruling 2026-04-29 (post-PR-review of bc-admin Inspector tab):

The Inspector's **Tenant pivot** section is **platform-only**. It does not call attestation. It returns the list of tenants the platform-admin operator may inspect for the metric in question. Eligibility is defined as **all active tenants in the platform tenant registry** — i.e. `SELECT … FROM tenant.tenants WHERE status_code = 'active'`. Per-tenant items include a `hasExplicitBinding` boolean flagging whether `tenant.contract_binding` carries an active row for this metric's contract; this flag is **informational, not an eligibility filter**.

Why option C (all active tenants) rather than option A (only explicitly-bound tenants) or option B (only tenants with runtime evaluations):
- Option A would have hidden every tenant from the operator whenever `contract_binding` was empty (which it is for many real metrics today). That contradicts the operator-surface posture of bc-admin.
- Option B (filter by runtime presence in tenant DB) requires per-tenant attestation fan-out at request time. Expensive, and orthogonal to the "is this a tenant the platform admin may inspect" question.
- Option C (all active tenants) is honest about the platform's state. Tenant-target sections then honestly return `ok` / `unavailable` / `broken` based on the selected tenant's attestation result. The operator decides whether to inspect; the platform doesn't pre-gate.

The bc-admin tenant selector UX is constrained accordingly:
- Selector is populated **from the Tenant pivot response**, not hardcoded.
- A freeform slug input is **not** an acceptable primary path. (Pre-amendment placeholder UX shipped a `useState<string>('sandbox1')` default and a freeform `<Input>`. Both are removed in the amendment.)
- One eligible tenant → pre-select with visible identification.
- Multiple eligible tenants → render as a dropdown.
- Zero eligible tenants → tenant-target sections render `state: 'unavailable'` with a clear reason; the inspection does not silently fall back to a guessed slug.

Audit semantics are unchanged: every read writes one row; `target_tenant_slug` reflects the operator's selection (now driven by Tenant pivot, not by a hardcoded default).

This clarification does not modify D-3, D-5, or the D-6 attestation contracts. Tenant pivot was already platform-only by D-3; this errata records what "eligible tenants" means for that section's response shape and how the bc-admin selector consumes it.

Effect on TSK-da749e implementation: amendments pushed to PR #6 (bc-core) and PR #2 (bc-admin) carry the option-C tenant pivot response shape and the selector-driven UX. No re-rework of the attestation boundary or the audit pipeline.
