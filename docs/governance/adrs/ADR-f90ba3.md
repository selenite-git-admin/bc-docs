---
uid: DEC-f90ba3
title: "MCF Onboarding Orchestration Schema — DevHub-side queue for 12K metric reservoir"
description: "Dedicated DevHub tables to track per-candidate onboarding pipeline state across sessions — replaces manual cookbook/memory state management at 12K scale"
status: superseded
superseded_by: DEC-b5c7ff
date: 2026-07-06T11:28:03.905Z
project: barecount-devhub
domain: metrics
subdomain: mcf/onboarding-orchestration
focus: schema
---

# MCF Onboarding Orchestration Schema — DevHub-side queue for 12K metric reservoir

## Context

At 85 active MCs, manual state tracking (cookbook run log + DevHub sessions + memory files + ad-hoc substrate queries) is manageable. At the 12K target, every session spends 10-20 min on spin-up archaeology: what's next, what's blocked, what was tried, what failed. The seed_metric table in bc-core tracks disposition (candidate/superseded/published) but not the per-step pipeline state (preflight result, panel verdict, materialization outcome, PE-MC result, activation cert, runtime eval result). The D492 metric_workflow table in DevHub tracks a single session's chain steps but is per-session, not per-candidate across sessions. Neither surface answers "show me all candidates that passed preflight but haven't been panelled yet" or "which families are blocked on CB-007" without multi-table grep archaeology across two databases.

## Context

The MCF metric-enrichment program (PLN-457cd0) targets ~12,440 candidate metrics in `mcf.seed_metric`. The current onboarding process is a 7-step governed chain per candidate: preflight → intake → panel → materialize → PE-MC → activate → runtime-eval. State is tracked across:

- **bc-core `mcf.seed_metric`**: disposition only (candidate/superseded/published/deferred) with back-pointers to last intake/MC/MCV UIDs
- **DevHub `metric_workflow` + `metric_workflow_step`**: per-session step-gate (D492) — not cross-session, not queryable as a queue
- **Cookbook run log**: manual text entries per run — not queryable
- **DevHub sessions/checkpoints**: narrative state per session — not structured
- **Memory files**: accumulated learnings — not operational state

At 85 MCs this works. At 12K scale, session spin-up cost (10-20 min archaeology per session) and lack of queryable queue state become the primary bottleneck.

## Decision

Add a dedicated **onboarding orchestration schema** to DevHub's SQLite database with three tables:

### 1. `onboarding_candidate` — per-candidate pipeline state

```sql
CREATE TABLE IF NOT EXISTS onboarding_candidate (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_uid TEXT UNIQUE NOT NULL,           -- gen'd by DevHub (OBC-xxxxxx)
  seed_metric_id TEXT NOT NULL,                 -- FK to mcf.seed_metric (UUID, cross-DB)
  metric_name TEXT NOT NULL,
  family_code TEXT,                             -- e.g. 'ar_aging', 'ap_payment', 'credit'
  wave_code TEXT,                               -- e.g. 'wave-1-ar', 'wave-2-ap'
  class_code TEXT CHECK(class_code IN ('base', 'derived', 'composite')),
  priority_code TEXT DEFAULT 'normal' CHECK(priority_code IN ('now', 'next', 'normal', 'deferred')),
  pipeline_state TEXT NOT NULL DEFAULT 'queued'
    CHECK(pipeline_state IN (
      'queued',           -- in reservoir, not yet triaged
      'triaged',          -- authorability assessed, ready for preflight
      'preflight_pass',   -- D492 preflight passed
      'preflight_fail',   -- D492 preflight failed (blocker reason in notes)
      'intake_created',   -- intake queue entry exists
      'panel_submitted',  -- panel run in flight
      'panel_approved',   -- APPROVE_FOR_DRAFT
      'panel_rejected',   -- REJECT or OPERATOR_REVIEW (needs intervention)
      'materialized',     -- M12.5 done, MC+MCV exist as draft
      'pe_mc_pass',       -- PE-MC gates passed
      'pe_mc_fail',       -- PE-MC failed (which check in notes)
      'activated',        -- MCV active
      'runtime_verified', -- runtime eval completed on at least one tenant
      'blocked',          -- waiting on an external dependency
      'superseded',       -- semantic dup of another candidate or active MC
      'abandoned'         -- dropped for stated reason
    )),
  blocker_code TEXT,                            -- e.g. 'cb-007', 'ap-cc-succession', 'class-3'
  blocker_description TEXT,
  -- Back-pointers to MCF substrate (nullable, filled as pipeline advances)
  intake_queue_uid TEXT,
  panel_run_uid TEXT,
  panel_verdict_code TEXT,
  metric_contract_uid TEXT,
  metric_contract_version_uid TEXT,
  activation_cert_uid TEXT,
  -- Cost tracking
  panel_cost_usd REAL,
  panel_duration_sec INTEGER,
  -- Metadata
  last_session_uid TEXT,                        -- which DevHub session last touched this
  notes_text TEXT,                              -- freeform (preflight warnings, panel defects, etc.)
  created_ts DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_ts DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_obc_pipeline ON onboarding_candidate(pipeline_state);
CREATE INDEX IF NOT EXISTS idx_obc_family ON onboarding_candidate(family_code);
CREATE INDEX IF NOT EXISTS idx_obc_wave ON onboarding_candidate(wave_code);
CREATE INDEX IF NOT EXISTS idx_obc_blocker ON onboarding_candidate(blocker_code) WHERE blocker_code IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_obc_seed ON onboarding_candidate(seed_metric_id);
```

### 2. `onboarding_step_log` — per-step evidence trail

```sql
CREATE TABLE IF NOT EXISTS onboarding_step_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id INTEGER NOT NULL REFERENCES onboarding_candidate(id),
  step_code TEXT NOT NULL,                      -- matches pipeline_state transitions
  outcome_code TEXT NOT NULL CHECK(outcome_code IN ('pass', 'fail', 'skip', 'retry')),
  evidence_json TEXT,                           -- structured: {verdict, checks, cost, duration, error}
  session_uid TEXT,
  recorded_ts DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_osl_candidate ON onboarding_step_log(candidate_id);
CREATE INDEX IF NOT EXISTS idx_osl_step ON onboarding_step_log(step_code);
```

### 3. `onboarding_blocker` — shared dependency registry

```sql
CREATE TABLE IF NOT EXISTS onboarding_blocker (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  blocker_code TEXT UNIQUE NOT NULL,            -- e.g. 'cb-007', 'ap-cc-succession', 'currency-adr'
  title_text TEXT NOT NULL,
  description_text TEXT,
  status_code TEXT NOT NULL DEFAULT 'open' CHECK(status_code IN ('open', 'resolved', 'wont_fix')),
  resolution_text TEXT,
  task_uid TEXT,                                -- DevHub task tracking the resolution
  candidate_count INTEGER DEFAULT 0,            -- how many candidates this blocks (derived)
  created_ts DATETIME DEFAULT CURRENT_TIMESTAMP,
  resolved_ts DATETIME
);

CREATE INDEX IF NOT EXISTS idx_ob_status ON onboarding_blocker(status_code);
```

### MCP Tools (new)

| Tool | Purpose |
|---|---|
| `devhub_onboarding_queue` | List candidates by pipeline_state, family, wave, blocker — the "what's next" query |
| `devhub_onboarding_advance` | Move a candidate forward (validates state transition, writes step_log) |
| `devhub_onboarding_block` | Mark candidate(s) as blocked with a blocker_code |
| `devhub_onboarding_stats` | Dashboard: counts by pipeline_state, family, wave; cost totals; blocker impact |
| `devhub_onboarding_import` | Bulk import from `mcf.seed_metric` — initial population + periodic reconciliation |
| `devhub_onboarding_blocker` | CRUD on the blocker registry |

### Session Integration

- `devhub_metric_workflow` (D492) continues to gate per-session steps — it does NOT change
- `devhub_onboarding_advance` is called at each workflow step completion to update the cross-session queue
- Session boot can show "Onboarding: X queued, Y in-flight, Z blocked" alongside project stats
- `devhub_onboarding_queue` replaces the manual triage grep at session start

### Population Strategy

1. **Initial load**: `devhub_onboarding_import` walks `mcf.seed_metric` and creates one `onboarding_candidate` per `candidate`-status seed. Back-fills `superseded`/`published`/`deferred` from existing status. Sets `class_code` from seed `raw_json` where available.
2. **Family/wave assignment**: manual or semi-automated — assign `family_code` based on `subfunction_code` + metric name patterns; `wave_code` based on priority and dependency ordering.
3. **Blocker pre-population**: create entries for known blockers (CB-007, AP CC succession, currency ADR, Class-3 capability gap).
4. **Reconciliation**: periodic `devhub_onboarding_import` diffs seed_metric against onboarding_candidate, updates dispositions, flags new candidates.

### What This Schema Does NOT Do

- **Does not replace `mcf.seed_metric`** — seed_metric remains the bc-core SSOT for seed disposition. DevHub is the orchestration layer.
- **Does not replace `metric_workflow`** — D492 per-session step-gating continues. This adds the cross-session queue view.
- **Does not write to bc-core** — DevHub reads MCF substrate for reconciliation; it never writes governed state. All MC/MCV/cert creation goes through the governed API chain.
- **Does not enforce governance** — the PE-MC evaluator, panel, and Foundation gate remain authoritative. This schema tracks outcomes, not rules.

### Authority Split (absolute, per D492)

DevHub onboarding schema = **orchestration state** (what to do next, what's blocked, cost tracking).
bc-core MCF substrate = **governed truth** (contracts, versions, certs, evaluations).
DevHub has zero authority over governed artifacts. It is a task queue with evidence pointers.

## Alternatives Considered

1. **bc-core `mcf.onboarding_*` tables**: Closer to substrate, FK integrity to MCs/MCVs. Rejected: adds DBCP overhead, mixes orchestration state with governed truth, requires bc-core restart for schema changes. DevHub's SQLite is instantly mutable.

2. **Extend `mcf.seed_metric` with more columns**: Already has back-pointers. Rejected: seed_metric is bc-core governed state; adding orchestration columns (panel_cost, blocker_code, wave) violates the authority split. Also requires DBCP for every column addition.

3. **File-based tracking (cookbook/JSON)**: Current approach. Rejected at scale: not queryable, not structured, manual maintenance, session-local.

4. **Extend DevHub `metric_workflow`**: Currently per-session. Could be extended to be per-candidate. Rejected: different lifecycle — workflow is "this session's chain run", onboarding_candidate is "this candidate's lifetime across all sessions." Conflating them muddies the D492 step-gate semantics.
