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

## Run lifecycle

States: `running → completed | failed | deferred_inputs_unavailable | abandoned | superseded`. Rules:

- Every run row carries a heartbeat; a reaper finalizes stale `running` rows to `abandoned`. Silent zombie runs are a defect class (TSK-560481), not an accepted state.
- Re-evaluating the same (metric, period) never mutates prior runs or snapshots — the earlier evaluation is superseded **on read** by the accepted evaluation selected for that period. Invariant III: history is never rewritten.
- `deferred_inputs_unavailable` is retried within the owning campaign once upstreams land — it is not a terminal state under a campaign.

## Dry-run (test mode)

A dry-run is **not a boundary act**: it computes and reports, but emits no progression object, no evidence, touches no watermark, and advances no state that downstream consumers read. Under the boundary-independent rules this is a diagnostic read, which is why it is safe at every engine and chainable: a campaign in `mode: test` walks admission → canonical → metric end-to-end and produces a report instead of persistence. Reproducible chain dry-runs require deterministic source state — the SDG dataset registry (R7).

## Campaigns

Multi-metric, multi-period evaluation is a first-class object (R1):

- Declares scope (metrics / families / all), period range, and mode.
- Executes DAG-ordered: base metrics before composites (metric_input edges).
- Writes a campaign row and per-run outcomes; retries deferred inputs in-campaign; resumable; idempotent per (campaign, metric, period).
- Campaigns are the unit the scheduler and the event spine invoke — and the vehicle for re-evaluation waves (e.g. post-M15 re-mints).

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
