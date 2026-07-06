---
uid: DEC-d316mr
title: "D316 — Metric Readiness Scheduler"
description: "Event-driven metric evaluation via Readiness Ledger — resolves multi-reader dependencies, metric-to-metric cascading, per-tenant isolation"
status: decided
date: 2026-04-14
project: bc-core
domain: metrics
refs:
  - type: decision
    uid: DEC-d315ve
    label: "D315 — Metric Evaluation Verification Framework"
  - type: decision
    uid: ADR-c0290f
    label: "Metric Evaluation Engine — grain, formula, temporal gate"
  - type: decision
    uid: DEC-bebaec
    label: "D305 — Chain Completeness SSOT"
migrated_from: legacy v2 archive
devhub_registration: doc-registry indexed; decision-registry row absent. UID short form `d316mr` does not match the allocator regex [0-9a-f]{6}, so this UID can never be registered under the current `devhub_decision_record` allocator. Classified UID_FORMAT_NON_CANONICAL + FILE_ONLY_UNEXPLAINED per Decision-Registration Integrity Audit 2026-06-22 §4.3. File-side authority preserved; no re-mint, no rename.
---

# D316 — Metric Readiness Scheduler

> **Decision-registration integrity (2026-06-22).** Classified `FILE_ONLY_UNEXPLAINED` + `UID_FORMAT_NON_CANONICAL` in the [integrity audit](../../evidence/audits/implementation/devhub-decision-registration-integrity-audit-2026-06-22.md) §3.2 / §4.3 and preserved as a historical file-side exception in the [repair closeout](../../evidence/closeouts/implementation/devhub-decision-registration-integrity-repair-closeout-2026-06-22.md). The UID short form `d316mr` cannot be registered under the current allocator regex `[0-9a-f]{6}`. Inbound cross-references address this file by its non-canonical UID `DEC-d316mr`; preservation chosen over forced rename or successor minting per operator doctrine. Content below is preserved verbatim per Foundation Invariant III.

## Context

Today metric evaluation is manually triggered via `POST /metric-evaluation` with explicit CO IDs. There is no automatic evaluation when dependencies are satisfied.

**Current state:**
- 778 MCs (growing to 10K+)
- **348 MCs bind to multiple CCs** — need data from 2+ readers to evaluate
- **3 derived MCs** depend on upstream metric snapshots (metric-to-metric DAG)
- All grain: `company_code × fiscal_period` — period-aware
- Multi-tenant: each tenant has own readers, run schedule, data readiness
- 24 readers (only 1 active), 51 CCs, 1,133 bindings

**Problem scenarios that don't work today:**

1. **Multi-reader MC:** DSO needs AR data (Reader A) + Revenue data (Reader B). Reader A finishes — who checks if Reader B is done? Nobody.
2. **Metric cascade:** `profit_margin` needs `net_profit` snapshot. `net_profit` finishes — who triggers `profit_margin`? Nobody.
3. **Tenant isolation:** Tenant A has all readers running. Tenant B has only AR. Same MC set — different readiness per tenant.
4. **Re-run:** Reader A re-runs with corrected data for Q1. Existing metric snapshots for Q1 are now stale. Who re-evaluates? Nobody.
5. **Partial failure:** Reader A runs, produces 1,000 COs. Resolution fails on 50 records. MC evaluates on 950 COs — is that acceptable? Who decides?

## Decision

Implement a **Readiness Ledger** pattern (adapted from SAP BW Process Chains / Oracle EPM). Don't trigger MCs — let them subscribe to dependency state changes.

### Architecture

Three components:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Static Graph    │     │ Readiness Ledger │     │ Evaluation      │
│  (dependencies)  │────▶│ (per-tenant,     │────▶│ Worker          │
│                  │     │  per-period)     │     │ (advisory lock) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Component 1: Static Dependency Graph

Materializes the DAG of "what does each MC need?"

**Table: `metric.mc_dependency`** (platform-scope, computed from metric_binding + contract metadata)

| Column | Type | Description |
|--------|------|-------------|
| `mc_dependency_id` | uuid PK | |
| `metric_contract_id` | uuid FK | The dependent MC |
| `depends_on_type` | enum | `'canonical_contract'` or `'metric_snapshot'` |
| `depends_on_id` | uuid | CC ID or upstream MC ID |
| `binding_role` | text | `'primary'`, `'secondary'`, `'enrichment'` |

**Populated by:** Scan of `metric.metric_binding` (for CC deps) + contract envelope `co_bindings` (for metric-to-metric deps). Refreshed on MC activation.

**Circular dependency check:** Recursive CTE at write time — reject if cycle detected.

### Component 2: Readiness Ledger

Tracks "what data is available" per tenant, per period, per grain.

**Table: `metric.readiness_ledger`** (tenant-partitioned, high-write)

| Column | Type | Description |
|--------|------|-------------|
| `ledger_id` | uuid PK | |
| `tenant_id` | text | Tenant slug |
| `period_key` | text | e.g. `"2026-Q1"`, `"2026-03"` |
| `company_code` | text | Grain dimension (nullable for global metrics) |
| `source_type` | enum | `'reader_run'`, `'resolution'`, `'metric_snapshot'` |
| `source_id` | uuid | Reader ID, CC ID, or MC ID |
| `run_id` | uuid | The admission/resolution/evaluation run that produced the data |
| `record_count` | int | How many COs/snapshots were produced |
| `completed_at` | timestamptz | When the source finished |
| `superseded_at` | timestamptz | NULL = current; set when re-run replaces this entry |

**Upserted by:** Three event hooks (called after each boundary completes):
1. After reader execution → upsert `source_type = 'reader_run'`
2. After canonical resolution → upsert `source_type = 'resolution'`
3. After metric evaluation → upsert `source_type = 'metric_snapshot'`

**Key invariant:** Only completed, non-superseded runs appear. Partial/failed runs do NOT write to the ledger.

### Component 3: Readiness Resolution Query

After each ledger upsert, a lightweight query finds MCs whose dependencies are now fully satisfied:

```sql
-- Find MCs ready for evaluation for this tenant + period + grain
SELECT dep.metric_contract_id
FROM metric.mc_dependency dep
LEFT JOIN metric.readiness_ledger led
  ON led.source_id = dep.depends_on_id
  AND led.tenant_id = :tenant_id
  AND led.period_key = :period_key
  AND led.company_code = :company_code
  AND led.superseded_at IS NULL
LEFT JOIN metric.readiness_ledger existing_eval
  ON existing_eval.source_id = dep.metric_contract_id
  AND existing_eval.source_type = 'metric_snapshot'
  AND existing_eval.tenant_id = :tenant_id
  AND existing_eval.period_key = :period_key
  AND existing_eval.company_code = :company_code
  AND existing_eval.superseded_at IS NULL
GROUP BY dep.metric_contract_id
HAVING
  -- All dependencies satisfied
  COUNT(dep.mc_dependency_id) = COUNT(led.ledger_id)
  -- Not already evaluated (or inputs are newer than last evaluation)
  AND (MAX(existing_eval.completed_at) IS NULL
       OR MAX(led.completed_at) > MAX(existing_eval.completed_at))
```

### Execution Flow

```
1. Reader "accounts-receivable" completes for tenant "demo-selenite", period "2026-Q1"
   └─ Upsert readiness_ledger: source_type='reader_run', source_id=reader_id

2. Canonical resolution completes, produces 384 COs for CC "cc__receivable_hdr"
   └─ Upsert readiness_ledger: source_type='resolution', source_id=cc_id

3. Readiness check fires:
   └─ Query: which MCs depend on cc__receivable_hdr AND have ALL deps satisfied?
   └─ Result: mc__total_ar_balance (1 CC dep, satisfied)
              mc__dso (2 CC deps — cc__receivable_hdr ✓, cc__revenue_hdr ✗)
   └─ Queue: mc__total_ar_balance only

4. mc__total_ar_balance evaluates → snapshot created
   └─ Upsert readiness_ledger: source_type='metric_snapshot', source_id=mc_id

5. Readiness check fires again:
   └─ Query: which MCs depend on mc__total_ar_balance?
   └─ Result: mc__dso_to_payment_terms_ratio (derived, needs mc__total_ar_balance ✓)
   └─ Queue: mc__dso_to_payment_terms_ratio

6. Cascade continues until DAG is exhausted.
```

### Failure Handling

| Scenario | Behavior |
|----------|----------|
| **Reader fails** | No ledger upsert → MCs stay locked → no evaluation → safe |
| **Resolution partial failure** | Only upsert ledger if resolution completes (even with rejections). `record_count` reflects accepted COs. MC evaluates on what's available. |
| **Metric evaluation fails** | No snapshot → no ledger upsert → downstream MCs stay locked. Retry: re-trigger same MC (ledger shows inputs ready but no snapshot). |
| **Reader re-run (same period)** | New ledger entry supersedes old one (`superseded_at` set). Readiness query finds `led.completed_at > existing_eval.completed_at` → re-evaluates affected MCs. |
| **Circular dependency** | Rejected at `mc_dependency` write time (recursive CTE cycle check). Cannot happen at runtime. |
| **Thundering herd** | When base reader serves 500 MCs, don't evaluate all at once. Priority queue: Tier 1 (SOX-critical) → Tier 2 (operational) → Tier 3 (informational). |

### Re-run / Correction Protocol

When a reader re-runs for an already-completed period:

1. Mark old ledger entries as `superseded_at = now()` for that source + tenant + period
2. New reader run produces new COs
3. New resolution produces new COs
4. New ledger entries created (not superseded)
5. Readiness query detects: `max(led.completed_at) > max(existing_eval.completed_at)`
6. Affected MCs re-evaluate → new snapshots
7. Old snapshots remain in DB (audit trail) with `superseded_at` set
8. Cascade: downstream MCs of the re-evaluated MC also re-evaluate

### Temporal Gate Integration

The existing temporal gate (`required_periods`, `completeness_threshold`) stays as-is inside the engine. It's the **inner gate** (compute-time). The readiness scheduler is the **outer gate** (trigger-time).

```
Outer gate (scheduler):  "Are all dependencies present for this period?"
                         → YES → trigger evaluation
                         → NO  → wait

Inner gate (engine):     "Does the data meet the contract's quality bar?"
                         → YES → produce snapshot
                         → NO  → reject with evidence
```

For derived metrics that need "N periods of upstream snapshots" (rolling calculations):
- The readiness query checks `metric_snapshot` entries for the upstream MC across the required period range
- The temporal gate validates completeness inside the engine

### Per-Tenant Isolation

Every ledger entry is tenant-scoped. The readiness query always filters by `tenant_id`. This means:
- Tenant A can have all readers active → full metric evaluation
- Tenant B can have only AR reader → only AR-dependent MCs evaluate
- No cross-tenant contamination
- Each tenant has its own evaluation pace

### Scale Considerations (10K+ Metrics)

| Concern | Mitigation |
|---------|------------|
| **Ledger write volume** | One row per (tenant, period, company_code, source). Not per-CO. Bounded by: tenants × periods × companies × sources. |
| **Readiness query cost** | Index on `(tenant_id, period_key, source_id, superseded_at)`. Query runs once per source completion, not continuously. |
| **Cascade depth** | Typical DAG depth: 2-3 levels (reader → primary MC → derived MC). Deep cascades unlikely in finance. |
| **Worker throughput** | Evaluate in batches per grain group. Advisory lock (D315) prevents duplicate evaluation. |

## Options Considered

### Option A: Polling (rejected)

Periodically scan all MCs for readiness.

Rejected: At 10K MCs × multiple tenants × multiple periods, the scan becomes expensive. Most MCs won't be ready — wasted computation.

### Option B: Event-driven only (rejected)

Publish events from readers, consume in a queue.

Rejected: Events alone don't track state. If the consumer crashes, events are lost. Need persistent state to know "what's ready" after recovery.

### Option C: Readiness Ledger (chosen)

Persistent state table + event-triggered query. Combines the efficiency of events (only check after a source completes) with the reliability of state (ledger survives crashes).

## Consequences

### Positive
- **Automatic evaluation** — no manual triggering, MCs evaluate as soon as dependencies are met
- **Multi-reader MCs work** — 348 MCs with 2+ CC dependencies will evaluate correctly
- **Metric cascading works** — derived metrics auto-trigger when upstream snapshots appear
- **Re-runs are safe** — supersession model ensures corrected data flows through
- **Per-tenant isolation** — each tenant evaluates at its own pace
- **Crash-safe** — ledger is persistent; recovery is a readiness re-scan

### Negative
- New tables: `mc_dependency` + `readiness_ledger` (DB change — requires approval per protocol)
- Three event hooks to add (reader, resolution, metric evaluation)
- Readiness query adds ~5ms per source completion (negligible)
- Supersession logic adds complexity to re-run handling

### Risks
- **Granularity mismatch:** If one reader is daily and another monthly, the MC must wait for the monthly reader. Need clear period alignment rules.
- **Silent stalls:** If a reader never runs, dependent MCs never evaluate. Need monitoring/alerting for "expected but never satisfied" dependencies.
- **Thundering herd:** A base reader serving 500 MCs could trigger 500 evaluations simultaneously. Mitigation: priority queue + batch sizing.

## UI: Operations Page (bc-admin)

**Location:** bc-admin → Operations (new top-level nav item)
**Scope:** Platform-scope page with **tenant filter dropdown**

### Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Operations                          [Tenant: demo-selenite ▼]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌── Metric Readiness ──────────────────────────────────┐  │
│  │  Ready: 254   Waiting: 348   Stale: 0   Failed: 11  │  │
│  │  [████████████░░░░░░░░░░░░░░░░] 41% ready            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌── Dependency Status ─────────────────────────────────┐  │
│  │  Blocking Source          MCs Waiting    Action       │  │
│  │  cc__revenue_hdr          183            [Run Reader] │  │
│  │  cc__cost_center          92             [Run Reader] │  │
│  │  mc__net_profit            3             [Waiting]    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌── Recent Runs ───────────────────────────────────────┐  │
│  │  Time       Source              Records  Status       │  │
│  │  2m ago     AR Reader (ECC)     384      ✓ Complete   │  │
│  │  5m ago     Resolution (CC)     384      ✓ Resolved   │  │
│  │  5m ago     mc__total_ar_bal    203      ✓ Evaluated  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌── Formula Audit ─────────────────────────────────────┐  │
│  │  Pass: 254  Warn: 176  Fail: 348                     │  │
│  │  Top issues: field_not_in_cc (733), domain (27)      │  │
│  │  [View Full Audit →]                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Cards

1. **Metric Readiness** — summary bar showing ready/waiting/stale/failed counts for selected tenant. Source: readiness ledger.
2. **Dependency Status** — which CCs/MCs are blocking the most metrics. Actionable: "Run Reader" button triggers reader execution. Source: `mc_dependency` JOIN `readiness_ledger`.
3. **Recent Runs** — timeline of reader runs, resolutions, evaluations for the selected tenant. Source: `readiness_ledger` ordered by `completed_at`.
4. **Formula Audit** — platform-wide (not tenant-filtered). Shows audit pass/warn/fail counts. Link to drill-down. Source: `GET /registry/formula-audit/summary`.

### Tenant Filter

- Dropdown at page top, populated from `platform.tenant` (or equivalent)
- Default: first tenant or "All tenants" (aggregate)
- Cards 1-3 filter by selected tenant
- Card 4 (Formula Audit) is platform-scope, unaffected by tenant filter
- URL param: `?tenant=demo-selenite` for deep-linking

### Drill-Down Pages

- **MC Detail:** Click any MC → shows dependency graph, readiness state, evaluation history, formula, last snapshot values
- **Reader Detail:** Click any reader → shows run history, connected CCs, downstream MCs affected
- **Formula Audit Detail:** Click "View Full Audit" → full per-MC audit results with filtering

## Implementation Sequence

### Phase 1: Foundation (backend)
1. **Schema:** `mc_dependency` + `readiness_ledger` tables (DB change — needs approval)
2. **Dependency graph builder:** Scan `metric_binding` + contract envelopes → populate `mc_dependency`
3. **Cycle detection:** Recursive CTE on `mc_dependency` write

### Phase 2: Event hooks + resolver (backend)
4. **Ledger event hooks:** After reader completion, resolution, metric evaluation → upsert ledger
5. **Readiness resolver:** Query + queue logic after each ledger upsert
6. **Worker:** Dequeue + evaluate with advisory lock (D315)

### Phase 3: Operations UI (bc-admin)
7. **Operations page:** Readiness summary, dependency status, recent runs, formula audit cards
8. **Tenant filter:** Dropdown populated from tenant list, filters readiness/dependency/run cards
9. **MC drill-down:** Dependency graph, readiness state, evaluation history per MC

### Phase 4: Monitoring + MCP
10. **Stale dependency alerts:** Flag MCs ready for >N hours but not evaluated
11. **MCP tool:** `devhub_metric_readiness` for Claude sessions
12. **Scheduled verification:** Nightly sample re-evaluation (D315 Layer 3)
