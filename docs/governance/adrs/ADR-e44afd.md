---
uid: DEC-e44afd
decision_code: D346
title: "Function Admin Console — decentralized RBAC and tabbed envelope for function-scoped governance"
description: "Establish /admin/functions/{function_code} in bc-portal as the function head's governance console. RBAC: single function_admin role scoped by function_code, assigned by tenant admin only. v1 ships Metrics tab (readiness + enable/disable); Freshness/Quality/Access are defined as tab envelope contracts for follow-up ADRs."
status: decided
subdomain: rbac
focus: function-console-envelope
date: 2026-04-17
project: bc-portal
domain: rbac
refs:
  - type: decision
    uid: DEC-6ee36c
    label: "D345 — Metric discipline taxonomy"
  - type: decision
    uid: DEC-e8a4d2
    label: "D344 — Definition is the canonical parent of MC"
  - type: decision
    uid: DEC-bebaec
    label: "D305 — Chain completeness SSOT"
migrated_from: legacy v2 archive
---

# Function Admin Console — decentralized RBAC and tabbed envelope

## Context

BareCount governance is decentralized by function. Every tenant has independent function heads — CFO owns finance metrics, CHRO owns hr, COO owns ops — and no tenant super-admin manages all functions as their day-to-day. The product needs an admin surface that reflects this ownership reality:

- Finance Console for the CFO and their delegates, scoped to `finance`.
- HR Console for the CHRO and their delegates, scoped to `hr`.
- And so on for every function.

Two specific asks drove this ADR:

1. **Route and page shape.** The surface must be one implementation driven by a dynamic `function_code` parameter, not a hand-coded page per function. Adding a new function (e.g. `legal`) must not require a new page.
2. **Authorization model.** A finance admin must not see hr's metrics, and hr admin cannot toggle finance metrics. Scope must be explicit, enforced server-side, and granted only by the tenant admin (not self-granted, not peer-granted).

D345 (metric discipline taxonomy) provides the grouping layer the console uses inside each tab. D344 establishes `metric_definition` as the canonical parent that MCs fold under. D305 is the SSOT for chain completeness (readiness signal).

## Decision

### 1. Route and page

**Route:** `/admin/functions/{function_code}` in bc-portal.

- Single React page component parameterized by `function_code`.
- Page title: `{Function Display Name} Console` (e.g. "Finance Console", "HR Console"). Rendered dynamically from `master.function.display_name`.
- Navigation surface: bc-portal top-nav shows a "Consoles" item that expands into the list of functions the current user has `function_admin` scope for. Users without any scope do not see the item at all.
- Direct URL access to `/admin/functions/{function_code}` for a function the user lacks scope for → 403 page, not 404 (403 is the honest answer; hiding existence is not our threat model).

**Not chosen:** `/settings/functions/{function_code}`. Rejected because this surface is for *administering* a function, not editing personal settings. `/admin` signals admin intent and aligns with how bc-admin already names similar surfaces.

### 2. RBAC model — single role with function scope

> **⚠ IMPLEMENTATION DEFERRED — target architecture only.**
> Platform RBAC is deferred as a platform-level decision. This section documents the target end-state; v1 of the Function Admin Console ships without per-function scope (see §2a below). The `tenant.function_admin_scope` table and `requireFunctionAdmin()` middleware described here are **not** built in v1. This section is re-activated when the platform RBAC ADR lands.

**Role:** `function_admin` — one platform role.

**Scope storage:** explicit junction table. No JSONB (D162 Rule 1 — scope is queryable on every request).

```
tenant.function_admin_scope
  tenant_id        uuid        NOT NULL   FK → tenant.tenants(id)
  user_id          uuid        NOT NULL   FK → users.platform_user(user_id)
  function_code    text        NOT NULL   FK → master.master_function(slug)
  granted_by       uuid        NOT NULL   FK → users.platform_user(user_id)
  granted_at       timestamptz NOT NULL DEFAULT now()
  effective_from   timestamptz NOT NULL DEFAULT now()   -- D162 Rule 9
  effective_to     timestamptz                          -- NULL = open-ended
  revoked_at       timestamptz                          -- immediate termination (IAM semantic)
  revoked_by       uuid                                 -- FK → users.platform_user(user_id)
  note_text        text
  PRIMARY KEY (tenant_id, user_id, function_code)
```

**Soft-delete + temporal model:** `revoked_at` (immediate termination, IAM-standard term) coexists with `effective_from`/`effective_to` (scheduled window, D162 Rule 9). A grant is active iff `revoked_at IS NULL AND now() >= effective_from AND (effective_to IS NULL OR now() < effective_to)`. `revoked_at` supersedes `effective_to` — a revoke terminates the grant regardless of any future expiry.

**Naming note:** `revoked_at` deviates from D162 Rule 8's prescribed `archived_at`. Kept because revocation is a distinct IAM concept (immediate permissions termination) with its own industry convention. Pairing with `effective_from`/`effective_to` fully honors D162 Rule 9.

**Authorization check:** bc-core middleware `requireFunctionAdmin(function_code)` joins the current user's JWT subject against this table and evaluates the active-grant predicate.

**Who grants:** tenant admin role only. No peer-grant, no self-grant. Bootstrap path: BareCount support (platform super-admin) assigns the first tenant admin; tenant admin then assigns function admins. This matches how existing tenant-admin bootstraps already work.

**Not chosen:**

- Per-function roles (`finance_admin`, `hr_admin`, …). Rejected: role-table bloat as functions grow, no gain in expressiveness. One role with scope is cleaner and matches the AWS IAM / GCP IAM pattern of role + resource scope.
- Scope in JWT claims. Rejected for v1: scope changes (grant/revoke) take effect next login, which is stale. Simpler to query the table per request with a short-lived cache. JWT claim injection can be layered in later as a perf optimization if it becomes a hot path.
- Discipline-level scope (e.g. user admin for `finance.working_capital` only). Rejected for v1: administrative burden without clear demand. Revisit if a customer requests it.

### 2a. v1 interim gate — no per-function RBAC

Because platform RBAC is deferred, v1 of the Console uses the coarsest existing authorization:

- Access gated by existing tenant-admin check (or equivalent currently enforced).
- Every tenant admin sees every function in `/admin/functions/{function_code}`.
- No `function_admin_scope` table, no `requireFunctionAdmin()` middleware, no grant/revoke flow.
- Decentralization described in §1 ("CFO ≠ CHRO") is a conceptual goal, not enforced in v1.
- Nav visibility: Console menu shown to all tenant admins; function list is all active functions (not filtered by scope).
- Direct URL to a function with no metric_definitions — still renders empty state; no 403.

**Why this is acceptable:** early customers (starting with demo-selenite) have one admin doing everything. Decentralized governance is a future need, not a current gap. When the platform RBAC ADR lands, §2 activates and §2a is removed — a straightforward migration because the Console code already speaks in function_code-scoped terms (just with a wider allow-list).

### 3. Tab envelope — four tabs, one ships now

The console is one page with four tabs. This ADR defines the envelope; individual tabs are delivered in separate ADRs except Metrics which ships in v1.

| Tab | Purpose | API surface | ADR |
|---|---|---|---|
| **Metrics** | Discipline-grouped list of MCs with readiness badge and enable/disable toggle. | `GET /api/admin/functions/{fc}/metrics`, `PATCH /api/admin/functions/{fc}/metrics/{mc_uid}/binding` | **v1 — this ADR** |
| Freshness | Per-metric last-snapshot lag vs SLA, source-side timing breaches. | `GET /api/admin/functions/{fc}/freshness` | Follow-up ADR |
| Quality | Aggregate of `quality_signals_json` per MC, threshold violations, anomaly rate. | `GET /api/admin/functions/{fc}/quality` | Follow-up ADR |
| Access | Viewers scoped to this function's dashboards, grant/revoke view access. | `GET /api/admin/functions/{fc}/access`, `POST`, `DELETE` | Follow-up ADR |

The envelope is fixed — future tabs do not get to invent new top-level concepts. If a need doesn't fit one of these four, it goes elsewhere in the product.

### 4. Metrics tab v1 — contract

**Read:** `GET /api/admin/functions/{function_code}/metrics`

Response groups metrics by `discipline` (from D345), then `subfunction` (current taxonomy retained), then `metric_definition`, then `metric_contract`. Each row carries:

```
{
  function_code: 'finance',
  discipline_code: 'working_capital',
  discipline_display_name: 'Working Capital',
  subfunction_code: 'accounts_receivable',
  metric_definition: { id, name, display_name },
  mc_uid, mc_version,
  readiness: {
    chain_verdict: 'complete' | 'partial' | 'unlinked',
    snapshot_count: int,
    latest_snapshot_at: timestamp | null,
    freshness_days: int | null,
    badge: 'live' | 'thin' | 'not_ready' | 'disabled'   // computed server-side
  },
  is_active: boolean,                                  // from tenant.contract_binding
  binding_effective_from, binding_effective_to
}
```

Badge rule (fixed in this ADR to prevent client drift):

Thresholds are **per-metric**, read from `metric.metric_definition.readiness_min_snapshots` and `metric.metric_definition.readiness_max_freshness_days`. Rationale: readiness is a property of the individual metric (DSO refreshes daily, an annual Credit Facility review is quarterly — forcing one threshold per discipline would misclassify most metrics). D162 Rule 4 — one source of truth per value.

When either column is NULL, the API applies a **system fallback**: `min_snapshots=30`, `max_freshness_days=7`. Fallback is the last resort, not the default state — admin UI surfaces NULL as "use system default" distinct from an explicit admin-set value, so "intentionally tuned" is discoverable.

Resolved threshold per metric:
```
effective_min_snapshots      = COALESCE(md.readiness_min_snapshots, 30)
effective_max_freshness_days = COALESCE(md.readiness_max_freshness_days, 7)
```

Badge:
- `disabled` — `is_active=false`. Takes precedence over all readiness.
- `live` — `chain_verdict=complete` AND `snapshot_count >= effective_min_snapshots` AND `freshness_days < effective_max_freshness_days`.
- `thin` — `chain_verdict=complete` AND `snapshot_count>=1` AND not live.
- `not_ready` — everything else (no snapshots, or chain partial/unlinked).

**Write:** `PATCH /api/admin/functions/{function_code}/metrics/{mc_uid}/binding`

Body: `{ is_active: true | false }`. Upserts `tenant.contract_binding` for the current tenant + MC + current version. Effect: dashboard query layer filters by `is_active`. Evaluation engine does **not** read this flag — evaluation continues regardless. Disable is cosmetic by design (scoped to dashboard display).

Audit: every toggle writes an activity row capturing `user_id`, `tenant_id`, `function_code`, `mc_uid`, `old_value`, `new_value`, `timestamp`. This is the audit trail for "who disabled the Cash Ratio metric on finance" questions.

**Authorization:** both endpoints gated by `requireFunctionAdmin(function_code)` (§2).

### 5. UI shape — Metrics tab v1

The page renders:

```
[Finance Console]                                    [tenant: demo-selenite]
 Metrics | Freshness | Quality | Access             [disabled tabs for v1]

▼ Working Capital (193 metrics)
  ▼ Accounts Receivable (31)
     DSO                              [🟢 Live]     [On ●○]    1,558 snaps · 2d ago
     Collection Effectiveness Index   [🟡 Thin]     [On ●○]    7 snaps · 2d ago
     Disputed Invoice Rate            [🔴 Not Ready][Off ○●]   0 snaps
  ▶ Accounts Payable (98)
  ▶ Cash Flow Management (13)
  ...
▶ P&L (125)
▶ Close & Control (112)
▶ Planning (67)
▶ Others (90)
```

- Collapsible discipline groups, collapsed by default except the first discipline.
- Subfunction shown as second-level grouping inside each discipline.
- Search/filter bar at top scopes across the tab: by name, by readiness state, by active/inactive.
- Bulk actions (enable/disable all in a discipline) deferred — single-row toggle only in v1 to prevent footguns.

### 6. Empty states

- **Function with zero metric_definitions:** page renders discipline headers with "No metrics yet for this discipline" and a note. Does not 404 or show error.
- **User with function_admin scope but tenant has no MCs bound:** same as above per discipline.
- **Function with only `others` populated:** rendered normally. `others` is a first-class discipline per D345.

## Options Considered

### Option A: Dynamic `/admin/functions/{function_code}` + single role with scope (chosen)

Pros: one implementation serves all functions; RBAC scales without role-table changes; matches IAM precedent; explicit scope table makes audits trivial.
Cons: server-side scope lookup on every request (mitigable via short-lived cache).

### Option B: Per-function routes (`/admin/finance`, `/admin/hr`) + per-function roles (rejected)

Pros: role names read naturally in UI.
Cons: new function = new route + new role + nav changes. Fails the "one implementation, many functions" goal. Role table grows linearly with function count.

### Option C: Scope embedded in JWT claims, no scope table (rejected for v1)

Pros: fast authorization check (no DB hit).
Cons: grant/revoke not effective until next login. Security-sensitive scope changes should take effect immediately. The scope table is the system of record; JWT injection can be added later as a cache, not as the source of truth.

### Option D: Fold Access Control into a separate "Permissions" area outside the Function Console (rejected)

Pros: clean separation of admin concerns.
Cons: breaks the "one pane for the function head" product concept. Function admin's job is ownership of their data product — access is part of that ownership.

## Consequences

### Positive

- Decentralized governance model matches enterprise buyer reality (CFO ≠ CHRO).
- One console codebase covers all functions, present and future.
- Scope table is a simple, auditable artifact; grants/revokes leave a record.
- Tab envelope prevents feature sprawl — all governance-ish asks map to one of four known homes.
- Metrics v1 is implementable against data we already have (chain_status SSOT + snapshot counts + contract_binding).

### Negative

- Per-request scope lookup adds one join to every `/api/admin/functions/*` call. Acceptable at current scale; cache if it becomes hot.
- Onboarding a tenant requires an extra step (tenant admin assigns function admin scopes). Needs documenting in tenant-onboarding SOP.
- The four-tab envelope commits us philosophically — if a future need genuinely doesn't fit, we need a supersession ADR rather than adding a fifth tab ad-hoc.

### Risks

- **Scope grants drift out of sync with the people actually doing the work.** A CFO leaves, scope is not revoked, new CFO can't see metrics. Mitigation: document a tenant-admin quarterly review of active scopes. Soft-delete (`revoked_at`) makes the history auditable.
- **Tenant admin is a single point of grant authority.** If the only tenant admin loses access, no one can re-grant. Mitigation: tenant onboarding SOP must require at least two tenant admins per tenant. Not this ADR's scope but flagged as a related dependency.
- **Disable toggle misused to hide broken metrics.** A function admin could hide a failing metric to avoid accountability. Mitigation: the audit log on every toggle is the countermeasure. Disable is visible in the activity feed; tenant admin can spot patterns.
- **Enable/disable is cosmetic only** (§4). Some stakeholders may expect disable to also stop engine compute for that metric. Mitigation: console UI copy must make this explicit ("Disable hides this metric from dashboards. The platform continues to evaluate it."). If compute-gating becomes a real need, it is a follow-up ADR that introduces a separate `is_evaluated` flag — not a reinterpretation of `is_active`.

## Follow-ups (tracked as separate ADRs / tasks)

- **ADR-B.1** — Freshness tab: SLA model, breach detection, per-discipline SLA defaults.
- **ADR-B.2** — Quality tab: quality_signals aggregation, threshold model, anomaly surfacing.
- **ADR-B.3** — Access tab: viewer role model, grant/revoke UX, inheritance from `function_admin` (do admins auto-view? Probably yes).
- **Task** — seed finance discipline data (from D345) before Metrics tab can render.
- **Blocked on platform RBAC ADR** — implement `tenant.function_admin_scope` table + migration. Deferred per platform decision.
- **Blocked on platform RBAC ADR** — bc-core middleware `requireFunctionAdmin(fc)`. v1 uses existing tenant-admin check instead.
- **Task (v1)** — bc-portal nav: "Consoles" menu visible to tenant admins, lists all active functions (no scope filter until RBAC lands).
- **Task** — activity-log helper for binding toggles (independent of RBAC).
- **Blocked on platform RBAC ADR** — tenant-onboarding SOP update: add step "assign function admins". Deferred.

## Out of scope

- Discipline-level RBAC (admin for only WC inside finance) — deferred; revisit on customer request.
- Bulk enable/disable in v1 — single-row toggles only.
- Cross-function aggregate views (CEO dashboard that spans all functions) — different surface, different ADR.
- Evaluation-engine gating via `is_active` — explicitly rejected per §4; future ADR would introduce a distinct flag if needed.
- Role delegation (function admin granting to sub-admins) — explicitly rejected per §2; tenant admin is the sole grant authority.
