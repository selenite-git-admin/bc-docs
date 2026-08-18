---
title: "Runtime Operations — engines, triggers, runs, campaigns, retirement"
description: "The operating doctrine for the four evaluation engines: trigger modes, run lifecycle, dry-run, campaigns, period close, failure routing, and the Retirement Register."
authority: authoritative
domain: operations
status: active
date: 2026-07-03
refs:
  - type: decision
    label: "DEC-9c0da7 (D481) — Runtime Doctrine (authority for this chapter)"
  - type: decision
    label: "DEC-5ea578 (D472) — governed metric runtime (implemented)"
  - type: decision
    label: "DEC-acce2b (D476) — CC-v2 canonical resolver (implemented)"
  - type: decision
    label: "DEC-20eefe (D212) — per-run evidence (decided, partially implemented)"
  - type: decision
    label: "DEC-26f75a (D480) — period_aggregate anchor_field (decided, engine support implemented)"
  - type: decision
    label: "DEC-01bd6b — Runtime Orchestration (two-axis Admission/Evaluation Orchestrators; explicit-command / no-read-trigger; target doctrine)"
  - type: decision
    label: "DEC-0d5b39 — Reader-definition / Runner-machine split; the runtime ecosystem map"
---

# Runtime Operations

**Authority:** ADR DEC-9c0da7 (D481). This chapter is the operating doctrine for the runtime — the answer to "how does data flow when nobody is typing." Program of record: DevHub plan PLN-360e58 v3 (Runtime Spine, gates R0–R8).

## The four engines

The platform evaluates at exactly four boundaries (Foundation, the-evaluation-boundaries.md; FND-ERR-006 holds the four-boundary reading — observation is *input to* admission, not a boundary). The engine inventory equals the boundary inventory:

| Engine | Boundary | Produces | Implementation (governed path) | Status |
|---|---|---|---|---|
| Admission engine | Admission | Source Objects | reader runtime → observation → admission (typed-fact writer) | live |
| Canonical engine | Canonical evaluation | Canonical Objects | CC-v2 resolver (DEC-acce2b) | live |
| Metric engine | Metric evaluation | Metric Snapshots | SS3 governed orchestrator + composite evaluator (DEC-5ea578, DEC-ada203, DEC-26f75a) | live |
| Action engine | Action evaluation | Action Objects | — does not exist; future authority DEC-3cc8a1 | absent (seam reserved) |

**The governed path is THE runtime.** The legacy execution path (OrchestratorService's resolution/metric chaining tail, the canonical_mapping resolver, the legacy metric/evaluation services) is **frozen**: no new consumers, no new capabilities. Its removal is governed by the Retirement Register below.

## Trigger modes

Every engine invocation carries exactly one declared trigger mode, recorded on the run row:

| Mode | Meaning | Status |
|---|---|---|
| `manual` | operator/API call | live in the readiness baseline |
| `test` | dry-run — see below | partial (admission only; R2 completes) |
| `scheduled` | cron-driven | R2; **scheduled admission is gated on watermark/delta discipline at fetch** (admission itself remains correctly non-idempotent — every admission is a distinct immutable observation act) |
| `event` | chained from an upstream engine's completion event via the persisted outbox | R2 |

**Orchestration doctrine (DEC-01bd6b, target).** A trigger mode names *how* an engine act is initiated; it is never an authority to evaluate on read. Under the accepted two-orchestrator model, two axis-orchestrators drive the engines by governed, version-pinned commands: the **Admission Orchestrator** on the **source axis** (source cycles coordinating admission runs) and the **Evaluation Orchestrator** on the **metric axis** (governed, target-pinned, command-triggered evaluation). **Reads never trigger evaluation** (ORCH-5/6; Invariant). The `scheduled` (cron) and `event` (outbox) mechanics above are the **as-built** initiation surface pending the DEC-01bd6b orchestration build — and the as-built differs from the target on three points: (1) mounted `scheduled` admission is **reader-keyed** (`RuntimeSchedulerService.runScheduledAdmissions` reads `BC_SCHEDULE_ADMISSION_READERS` = `readerId:flavorId` pairs and calls `ReaderRuntimeService.executeReader`); source-axis keying is DEC-01bd6b target doctrine, not the mounted identity. (2) the runtime **outbox does not invoke evaluation** — `RuntimeEventService.emit` persists the event and drives only the boundary-ticket and webhook consumers; no event consumer invokes canonical, metric, or campaign evaluation, so `event` is a trigger-mode/outbox vocabulary, not a mounted evaluation invoker. (3) the schedule *commands* an admission, but version-pinned command selection is target doctrine (see Campaigns). None of these mount the two-orchestrator model yet.

## Run lifecycle

States: `running → completed | failed | deferred_inputs_unavailable | abandoned | superseded`. Rules:

- **Scoped rule (source-filter design v9/v10, TSK-a83188):** the heartbeat + reaper lifecycle applies to the run surfaces that carry that substrate (e.g. the chain-authoring run's lease/epoch lifecycle) — it is **not** a universal property of every run row. Silent zombie runs remain a defect class (TSK-560481), not an accepted state, on the surfaces that have the substrate.
- **Admission runs are deliberately different:** `runtime.admission_run` has **no heartbeat, no reaper, and no auto-expiry**. Its states are `running → completed | failed` (internal runtime transitions), `cancelled` (dedicated operator operation), and `reconciled` (dedicated operator operation for crashed/stale runs). A stale `running` admission run **blocks reader binding flips** (the quiesce rule) until an operator records a reconciliation via the dedicated operation — actor-attributed, reason ≥ 40 characters, append-only disposition evidence written in the same transaction. The generic admission-run update surface has **no lifecycle authority**, and no automatic process ever finalizes an admission run. The no-auto-expiry rule is a rule, not an omission.
- Re-evaluating the same (metric, period) never mutates prior runs or snapshots — the earlier evaluation is superseded **on read** by the accepted evaluation selected for that period. Invariant III: history is never rewritten.
- `deferred_inputs_unavailable` is retried within the owning campaign once upstreams land — it is not a terminal state under a campaign.

## Dry-run (test mode)

A dry-run is **not a boundary act**: it computes and reports, but emits no progression object, no evidence, touches no watermark, and advances no state that downstream consumers read. Under the boundary-independent rules this is a diagnostic read. **As-built scope:** the mounted campaign dry-run is **metric-only** — it calls `MetricEvaluationOrchestrator.dryEvaluateMetricForPeriod`, and composites explicitly return `unsupported`; an end-to-end admission → canonical → metric chained dry-run is a **target**, not mounted. A `mode: test` campaign also **persists diagnostic campaign and per-item report rows** (`progression.evaluation_campaign` / `evaluation_campaign_run`) — that is the report — while emitting **no** boundary object, run, snapshot, Evidence, event, or watermark. Reproducible dry-runs require deterministic source state — the SDG dataset registry (R7).

A dry-run produces **no authoritative meaning** (Invariant I — meaning is produced only at its boundary): its computed values are diagnostic only, are never surfaced or read as a metric's value, and never substitute for a governed evaluation act. It is a read *about* the chain, not an evaluation of it; to make a value authoritative, a governed evaluation command must run and persist it.

## Campaigns

Multi-metric, multi-period evaluation is a first-class object (R1):

- Declares scope (metrics / families / all), period range, and mode.
- Executes DAG-ordered: base metrics before composites (metric_input edges).
- Writes a campaign row and per-run outcomes; retries deferred inputs in-campaign; resumable; idempotent per (campaign, metric, period).
- A campaign **names governed targets**. Under DEC-01bd6b it is the Evaluation Orchestrator's metric-axis unit and pins **fixed input versions** — but that version-pinning is **target** doctrine: the as-built `resolveScope` selects whichever Metric Contract **versions are active when the campaign begins** (scoped by all-metrics / MC UIDs / subfunction), `evaluation_campaign.scope_json` preserves only that scope, and `evaluation_campaign_run` stores the Metric Contract UID, period, status, and run id — **not** the selected MCV UID or exact input identities. A campaign that re-evaluates after a supersession (e.g. post-M15) issues **new forward evaluation acts** — never an in-place recompute and never a history rewrite (Invariant III); prior snapshots stand and are superseded on read.

## Period close

A fiscal period becomes **read-ready** per (tenant, period) via an explicit readiness object: sources admitted → canonical resolution complete → campaign complete → value audit green (R4). Read surfaces key on read-readiness, not on the existence of snapshot rows.

## Failure routing

Every engine failure/blocker/deferral raises a boundary ticket (governed-engine ticket surface, R2 — with flood discipline: aggregation windows + auto-resolve lifecycle) and publishes to the outbound webhook registry (HMAC-signed, retried, dead-lettered). Ticketing is the first consumer of the event stream; external stakeholder alerting attaches later without engine changes.

## NFR envelope

The runtime SLO envelope is governed by DEC-9c0da7 and related runtime decisions. Static doctrine records the obligations; benchmark measurements and retirement-event evidence are kept outside this chapter so they can evolve without rewriting operating doctrine.

- Admission must support sustained extraction through governed batch writes.
- Full-catalog campaigns must remain bounded at pilot scale.
- Period close produces read-ready state only after source admission, canonical resolution, campaign completion, and value audit are green.
- Evidence rows remain in RDS with WORM detail archives where archive-first retirement applies.

## Runtime Evidence Ledgers

- [Runtime retirement register](../evidence/ledgers/operations/runtime-retirement-register.md) — R8 operator decisions, retirement rows, measurement evidence, and volatile counts/dates preserved as evidence, not operating doctrine.
