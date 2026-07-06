---
uid: DEC-cc8fd9
title: "E2E Chain Test Bench — Tenant-Publishes-to-Platform QA Architecture"
description: "Dedicated qa-bench tenant runs full chain e2e (Reader through MS/AO). Report collector publishes timing, accuracy, invariant results to platform test_bench schema. bc-admin Operations page for UI. Accumulate + purge + reset data lifecycle."
status: implemented
date: 2026-04-11
project: bc-core
domain: platform
refs:
  - type: decision
    uid: DEC-d72560
    label: "Canonical Field as 3rd Contract Primitive (D301)"
  - type: decision
    uid: DEC-ee6018
    label: "QA tooling in bc-qa repo"
  - type: decision
    uid: DEC-1918d0
    label: "Database rules (D162)"
  - type: document
    path: "architecture/contract-chain-assembly.md"
    label: "Contract chain assembly spine"
  - type: document
    path: "assets/diagrams/DG-D303-test-bench-architecture.drawio"
    label: "Test bench architecture diagram"
migrated_from: legacy v2 archive
---

# E2E Chain Test Bench — Tenant-Publishes-to-Platform QA Architecture

## Context

The contract chain for finance metrics (SC -> AC -> OC -> CC -> MC) is nearing completion. Before production, we need to pressure-test the full e2e data flow for:

1. **Volume** -- Can the chain handle 10K+ source records through all boundaries in a single evaluation cycle?
2. **Speed** -- How long does canonical evaluation (grain reduction via resolution rules) take at scale?
3. **Accuracy** -- Do the 12 invariants (R1-R12) hold under volume? Do resolution rules produce correct aggregates?

The existing `test-full-lifecycle.ts` proves correctness for a single metric but is not a pressure test. No load generation, no timing instrumentation, no accumulated test history.

### Tenant Isolation Constraint

BareCount enforces strict tenant isolation -- the platform (bc-admin) cannot access tenant databases directly. This is non-negotiable for ISO 27001 compliance. A "test tenant" where the platform reads the tenant DB directly would be a loophole, not a solution.

The test bench must respect the same boundaries as production: tenant does the work, platform sees the results.

## Decision

### Architecture: Tenant-Publishes-to-Platform

The test bench operates as a **real tenant** (`qa-bench`) that runs the full chain identically to production. A report collector captures timing, counts, and accuracy at each boundary, then publishes results to the platform DB via the platform API. bc-admin reads results from the platform DB only.

See diagram: `DG-D303-test-bench-architecture.drawio`

**Key invariant:** The platform never touches `t_qa_bench` directly. The chain runs identically to production. The only difference is that a report collector instruments each boundary and publishes results upward.

### Data Model -- Platform Side

New `test_bench` schema in `bc_platform_dev` (12th schema).

#### test_bench_scenario

Defines what to test. Reusable across runs.

| Column | Type | Notes |
|--------|------|-------|
| scenario_id | UUID PK | gen_random_uuid() |
| scenario_name | TEXT NOT NULL | e.g., "Finance AR DSO 10K" |
| description_text | TEXT | What this scenario proves |
| tenant_slug | TEXT NOT NULL | "qa-bench" |
| volume_target | INTEGER NOT NULL | Number of source records to generate |
| contracts_json | JSONB NOT NULL | { sc_id, ac_id, oc_id, cc_id, mc_id } |
| expected_json | JSONB NOT NULL | { co_count_range, metric_value_range, invariants } |
| timing_limits_json | JSONB | { admission_max_ms, canonical_max_ms, metric_max_ms } |
| sdg_profile | TEXT | bc-sdg profile slug for data generation |
| is_active | BOOLEAN DEFAULT true | Soft disable |
| created_at | TIMESTAMPTZ DEFAULT now() | |
| updated_at | TIMESTAMPTZ DEFAULT now() | |

#### test_bench_run

One row per test execution.

| Column | Type | Notes |
|--------|------|-------|
| run_id | UUID PK | gen_random_uuid() |
| scenario_id | UUID NOT NULL FK | References test_bench_scenario |
| triggered_by | TEXT NOT NULL | "admin:user@example.com" or "cli:manual" |
| run_status | TEXT NOT NULL | CHECK: pending, running, completed, failed, cancelled |
| verdict | TEXT | CHECK: pass, fail, inconclusive (set on completion) |
| started_at | TIMESTAMPTZ | |
| ended_at | TIMESTAMPTZ | |
| total_duration_ms | INTEGER | ended_at - started_at |
| total_records_in | INTEGER | Source records fed |
| total_records_out | INTEGER | Metric snapshots produced |
| error_detail | TEXT | If failed, why |
| run_config_json | JSONB | Snapshot of scenario config at run time |
| created_at | TIMESTAMPTZ DEFAULT now() | |

#### test_bench_run_step

Per-boundary instrumentation. One row per boundary per run.

| Column | Type | Notes |
|--------|------|-------|
| step_id | UUID PK | gen_random_uuid() |
| run_id | UUID NOT NULL FK | References test_bench_run |
| boundary_code | TEXT NOT NULL | admission, observation, canonical, metric, action |
| step_order | INTEGER NOT NULL | 1-6 execution order |
| record_count_in | INTEGER | Records entering this boundary |
| record_count_out | INTEGER | Records emitted |
| duration_ms | INTEGER | Wall-clock time for this boundary |
| pass | BOOLEAN | Did this boundary meet timing + correctness criteria? |
| error_count | INTEGER DEFAULT 0 | Rejection/failure count |
| detail_json | JSONB | Boundary-specific detail |
| created_at | TIMESTAMPTZ DEFAULT now() | |

#### test_bench_run_metric

Per-metric accuracy validation.

| Column | Type | Notes |
|--------|------|-------|
| metric_id | UUID PK | gen_random_uuid() |
| run_id | UUID NOT NULL FK | References test_bench_run |
| metric_contract_id | UUID NOT NULL | Which MC was evaluated |
| metric_name | TEXT | Human-readable metric name |
| expected_value_json | JSONB | From scenario expected_json |
| actual_value_json | JSONB | From metric snapshot |
| variance_pct | NUMERIC(10,4) | Percentage deviation |
| verdict | TEXT NOT NULL | CHECK: pass, fail, within_tolerance, not_evaluated |
| invariant_results_json | JSONB | R1-R12 per-invariant pass/fail |
| evidence_chain_valid | BOOLEAN | Evidence chain integrity check |
| created_at | TIMESTAMPTZ DEFAULT now() | |

### Data Lifecycle -- Three Gears

| Gear | Action | When to Use |
|------|--------|-------------|
| **Accumulate** (default) | Each run adds SOs/COs/MSs to t_qa_bench. Run history preserved. | Normal operation. Reveals performance degradation. |
| **Purge Run** | Deletes tenant-side artifacts for a specific run_id. Platform run record marked purged. | Surgical cleanup after analyzing a failed run. |
| **Reset Tenant** | Truncates all boundary + evidence tables in t_qa_bench. Platform history preserved. | Clean slate after contract structure changes. |

### Tenant: qa-bench

Created as a real tenant in the platform DB:

- **Slug:** qa-bench
- **Schema:** t_qa_bench
- **Tenant ID:** 5c94cc80-dd8b-4b69-8955-68e6fca8ce58
- **Status:** active
- **Tables:** 13 (9 boundary + 3 evidence + 1 users)

### Data Source: bc-sdg (Pre-generated)

| Tier | Volume | Use Case |
|------|--------|----------|
| T1 | 1,000 records | Correctness, basic timing |
| T2 | 10,000 records | Volume stress, boundary timing |
| T3 | 100,000 records | Scale limits, performance profiling |

Reader consumes OData from bc-sdg (port 4200) with date-range filters to control volume.

### UI: bc-admin Operations Section

New page at `/operations/test-bench`:

1. **Scenario List** -- Cards with run counts, last run status
2. **Run Trigger** -- Select scenario, click Run
3. **Run History** -- Table with status, verdict, duration, expandable detail
4. **Run Detail** -- Per-boundary waterfall chart, per-metric accuracy, invariant checklist
5. **Data Management** -- Purge run, Reset tenant

### Trigger Flow

1. Admin clicks "Run Scenario" in bc-admin
2. `POST /api/test-bench/runs` creates run record (status: pending)
3. bc-core orchestrator starts chain in qa-bench tenant context
4. Each boundary runs normally; report collector wraps with timing
5. Results published via `POST /api/test-bench/runs/:runId/steps` and `/metrics`
6. Run status updated to completed/failed with verdict
7. bc-admin polls/SSE for completion

### Scope Phasing

| Phase | Scope | Proves |
|-------|-------|--------|
| P1 | Finance AR, DSO metric, 1K records | Chain correctness, basic timing |
| P2 | Finance AR, DSO, 10K + 100K | Volume limits, performance profile |
| P3 | Template any function/metric | Reusability |
| P4 | Multi-metric concurrent runs | Parallelism, contention |

## Options Considered

### Option A: Platform reads tenant DB directly (rejected)

Rejected: violates tenant isolation (ISO 27001 finding), creates precedent for platform-to-tenant DB access, different code path than production.

### Option B: Test bench as separate service in bc-qa (rejected)

Rejected: cannot instrument boundary internals (timing per boundary), requires external DB access for validation, adds another service.

### Option C: Tenant-publishes-to-platform (chosen)

Chosen: respects tenant isolation (ISO-grade), chain runs identically to production, results are platform-scoped, reuses all existing boundary services, accumulation model reveals performance degradation.

## Consequences

### Positive

- ISO 27001 compliant -- tenant isolation preserved, auditor-safe
- Production-identical chain execution -- no separate test code paths
- Performance regression detection via accumulated history
- Reusable for any metric/function once templated (P3)

### Negative

- Requires report collector instrumentation in boundary services (minimal code)
- Pre-generated bc-sdg data limits dynamic volume testing initially
- One more schema in platform DB (12th)

### Risks

- **bc-sdg data staleness:** Pre-generated data may drift from contract fields. Mitigation: regenerate after schema changes, track generation date.
- **Accumulation bloat:** Unbounded growth in tenant DB. Mitigation: Reset button + size monitoring.
- **Report collector overhead:** Timing instrumentation could skew results. Mitigation: wall-clock outside boundary calls, lightweight wrapper.
