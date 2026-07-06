---
uid: DEC-c0290f
title: "Metric Evaluation Engine — Universal Formula Engine with Schedule-Driven Orchestration"
description: "Engine speaks contract-native formula+variables; grain-aware GROUP BY; schedule-driven triggering solves last-trigger problem; extractable to Lambda/Fargate; Step Functions for chain orchestration"
status: implemented
date: 2026-04-11
project: bc-core
domain: metrics
refs:
  - type: decision
    uid: DEC-3d6e11
    label: "D203: DAG Support — Derived CO + Secondary Metric"
  - type: decision
    uid: DEC-a25931
    label: "D208: JSONB-first transient storage"
  - type: decision
    uid: DEC-2658ff
    label: "D210v3: Typed tables + S3 archive"
  - type: decision
    uid: DEC-1918d0
    label: "D162: Database architecture — no JSONB for queryable data"
  - type: decision
    uid: DEC-24f6da
    label: "Temporal values are absolute — cron + timezone"
  - type: decision
    uid: DEC-01419c
    label: "MC Body Purity — Formula as Object"
migrated_from: legacy v2 archive
devhub_registration: doc-registry indexed; decision-registry PATH_MISMATCH **RESOLVED 2026-06-22** via the audit-driven `devhub_decision_update` extension (title_text + file_path now mutable). Registry row DEC-c0290f: title="Metric Evaluation Engine — Universal Formula Engine with Schedule-Driven Orchestration", file_path=docs/adrs/ADR-c0290f.md — both aligned with this file. DEC-637072 remains the separate "Derived Canonical Fields" registration. Original drift recorded in Decision-Registration Integrity Audit 2026-06-22 §3.1 and Repair Closeout (same date).
---

# Metric Evaluation Engine — Universal Formula Engine with Schedule-Driven Orchestration

> **Decision-registration integrity (2026-06-22).** Originally classified `PATH_MISMATCH` in the [integrity audit](../../evidence/audits/implementation/devhub-decision-registration-integrity-audit-2026-06-22.md) §3.1 — **resolved the same day** via the audit-driven `devhub_decision_update` tool extension. The registry row `DEC-c0290f` now correctly carries title "Metric Evaluation Engine — Universal Formula Engine with Schedule-Driven Orchestration" with `file_path: docs/adrs/ADR-c0290f.md`. `DEC-637072` remains the separate "Derived Canonical Fields" registration (no duplicate doctrine in the registry post-repair). See the [repair closeout](../../evidence/closeouts/implementation/devhub-decision-registration-integrity-repair-closeout-2026-06-22.md) for the full pre-repair vs post-repair record. Content below is preserved verbatim per Foundation Invariant III.

## Context

The MetricEvaluationEngine in bc-core's `src/boundary/` evaluated metrics using a hardcoded `computation.operations[]` array format from the TypeScript KPI seed path. However, the official MC creation path (mc-onboarding.service.ts) produces contracts with `body.formula` + `body.variables` — the contract-native format defined in `barecount/metric/v1` schema. The engine couldn't understand contracts created through the official path, producing `metricValueJson: {}`.

Additionally, the engine:
- Flattened all input COs into one pool (no grain-aware GROUP BY)
- Ignored `temporal_gate` (required in metric-v1.json schema)
- Had no DAG support for derived metrics
- Had no scheduling/triggering mechanism for production
- Created one snapshot per evaluation (not per grain group)

## Decision

### D1: Contract is the complete instruction set

The engine takes **two inputs only**: MC envelope (contract) + CO payloads. Every parameter the engine needs — formula, variables, grain, thresholds, quality rules, temporal gate — comes from the contract. No external config, no environment variables, no hardcoded defaults.

### D2: Formula + variables is the PRIMARY computation path

The engine's `computeMetric()` dispatcher checks formula+variables first (contract-native), falls back to `computation.operations` (legacy). The recursive descent parser handles:

- Aggregation functions: `SUM()`, `COUNT()`, `AVG()`, `MIN()`, `MAX()`
- Arithmetic operators: `+`, `-`, `*`, `/`
- Parentheses: full nesting
- Variable references: input (from CO payloads), output (result target), constant
- Both naming conventions: `var_code`/`field_code` (mc-onboarding) and `var`/`field_name` (seed-v2 enrichment)

Formulas like `O1 = SUM(I1)`, `O1 = I1 / I2`, `O1 = ((I1 - I2) / I2) * C1` all parse and evaluate correctly.

### D3: Grain-aware GROUP BY with per-grain snapshots

When the contract declares `grain` (e.g., `["company_code", "period_date"]`), the engine:

1. Groups CO payloads by grain key combinations
2. Evaluates formula independently per group
3. Runs quality validation + threshold evaluation per group
4. Returns `grainResults[]` — one per grain key combination
5. MetricService creates one `metric_snapshot` per grain group (1:N from metric_evaluation)

Backward compatibility: top-level `metricValueJson`/`businessKey` mirror the first grain group.

### D4: Schedule-driven triggering (not event-driven)

**The "last trigger" problem:** A metric depending on COs from multiple sources (SAP + Salesforce) can't be triggered by data events — you don't know which event is "last."

**Solution:** MC declares `temporal_gate.schedule.cron`. EventBridge fires at scheduled time. Temporal Gate Lambda checks `readiness_gate`:

- `wait_for_all`: ALL upstream COs/snapshots must exist within `lookback_window`
- `wait_for_quorum`: at least `quorum_min` of dependencies ready
- `best_effort`: evaluate with whatever's available

If not ready → Step Functions Wait state (retry up to `readiness_gate.timeout`). If timeout → fail with evidence.

Data events are irrelevant to triggering — they populate CO tables that the readiness check queries. Optional: EventBridge on CO creation for early readiness check.

### D5: Engine is extractable to Lambda/Fargate

`MetricEvaluationEngine` is stateless, zero dependencies, no DB access. Extract to standalone TypeScript package for Lambda/Fargate deployment. `MetricService` stays in bc-core as boundary orchestrator (DB, evidence, snapshots).

### D6: Step Functions for chain orchestration

```
State 1: Reader (Lambda/ECS)
State 2: Admission (Lambda)
State 3: Canonical Resolution (Lambda)
State 4: Temporal Gate Check (Lambda) — readiness + lookback
State 5: Metric Evaluation (Lambda/Fargate) — fan-out per MC
State 6: DAG Check (Choice) — re-enter State 4 for downstream metrics
State 7: Write Results + Evidence (Lambda)
```

### D7: Future formula capabilities

| Capability | Approach | Phase |
|---|---|---|
| ABS() | Built-in parser function | Phase 1 |
| IF/conditional | Ternary function in parser | Phase 2 |
| Multi-output (O1+O2) | Multiple formulas per MC | Phase 2 |
| Rolling/window | Prior snapshots as secondary inputs + WINDOW keyword | Phase 4 |
| DAG inputs | Upstream snapshots injected by orchestrator as input alias | Phase 3 |

### D8: Grain and temporal_gate are mandatory

Enforced at two levels:
1. MC onboarding rejects creation if grain or temporalGate missing
2. Engine rejects evaluation if envelope has no grain

## Options Considered

### Option A: Translate formula to operations in normalizeEnvelope (rejected)

Add formula→operations translator in the adapter layer. Rejected because: the contract IS the instruction set. The engine must speak the contract language, not require translation. Also, `operations` can't express compound formulas like `(I1 - I2) / I2`.

### Option B: Engine understands formula natively (chosen)

Recursive descent parser evaluates formula+variables directly. No translation layer. Engine reads what the contract says.

### Option C: Event-driven metric triggering (rejected)

Trigger metric evaluation when new COs arrive. Rejected because: can't determine which data event is "last" when multiple sources feed a metric. Schedule-driven with readiness checks solves this cleanly.

### Option D: Schedule-driven with readiness gates (chosen)

Cron trigger → readiness check → evaluate if ready → wait if not. Clean separation of "when to check" (schedule) and "what to check" (readiness gate).

## Consequences

### Positive
- Engine speaks the contract language — no format translation needed
- Any formula expressible in the KPI algebra evaluates correctly
- Grain-aware computation produces semantically correct per-group metrics
- Schedule-driven triggering eliminates the "last trigger" race condition
- Engine extractable to Lambda/Fargate for independent scaling
- Step Functions provide visual execution trace, built-in retry, natural state machine

### Negative
- `computation.operations` is now legacy — existing TypeScript KPI seed contracts still use it
- 1:N metric_evaluation → metric_snapshot changes the DB relationship
- Temporal gate implementation is Phase 1 work, not yet done
- Schedule-driven means slight delay vs. event-driven (metrics evaluate at next scheduled time, not instantly)

### Risks
- **Formula parser coverage:** Edge cases (absolute value, conditionals) need incremental parser extensions. Mitigated by phased rollout (Phase 1-4).
- **Grain explosion:** Very high grain cardinality (10K+ groups) could create too many snapshots. Mitigated by max_grain_groups threshold in engine.
- **DAG cycles:** Circular metric dependencies. Mitigated by topological sort validation at MC onboarding time.
- **D210 typed tables:** Current JSONB storage is transient. When D210 activates, per-grain snapshots must also populate typed tables. Tracked for Phase 4.

## Implementation Status

**Done (this session):**
- Formula + variables parser in MetricEvaluationEngine
- Grain-aware GROUP BY with per-grain GrainResult
- Per-grain snapshot creation in MetricService
- normalizeEnvelope lifts formula/variables from body
- 240/240 boundary tests pass

**Phase 1 (next session):**
- Make grain mandatory, add ABS(), constant value field, temporal gate pre-check, per-grain rejection evidence

**Phase 2-4:** Extract to Lambda, Step Functions, DAG, rolling calculations, D210 typed tables
