---
uid: DEC-9c0da7
title: "Runtime Doctrine — four engines, trigger modes, run lifecycle, period close, dry-run, campaigns (Runtime Spine R0)"
description: "Runtime Spine R0: four engines = four boundaries (Action absent/reserved); governed path is THE runtime, legacy frozen; trigger modes manual|test|scheduled|event; run lifecycle w/ reaper; dry-run = non-boundary-act; campaigns; period-close readiness; NFR envelope; failure routing"
status: decided
date: 2026-07-03T03:08:35.253Z
project: bc-core
domain: metrics
subdomain: runtime/doctrine
focus: runtime-spine
---

# Runtime Doctrine — four engines, trigger modes, run lifecycle, period close, dry-run, campaigns (Runtime Spine R0)

## Context

SES-0422da grounded study: the mechanics are correct (value-proven by SES-b54f06 + the 1,215-run backfill) but nothing runs without a hand-thrown POST; integrity governance points at empty tables; the only automated chaining routes through the legacy path with empty contracts; the DAG runner exists only as a session scratchpad. BCF/MCF have doctrine; the runtime had none. This ADR is that doctrine — the R0 gate of PLN-360e58 v3, recorded as decided under the operator's 2026-07-03 autonomous-run authorization. It absorbs the surviving intent of DEC-5ea578 (flipped to implemented in the same sweep: the governed runtime, run object, and transactional evaluation act are built and cited as authority throughout src/boundary; its unfinished legacy-envelope retirement transfers to the Retirement Register).

## Decision

**1. Engine inventory = boundary inventory.** The platform has exactly four evaluation engines, one per Foundation boundary (the-evaluation-boundaries.md; FND-ERR-006 four-boundary reading): the **Admission engine** (reader runtime → observation → admission; produces Source Objects), the **Canonical engine** (CC-v2 resolver, DEC-acce2b; produces Canonical Objects), the **Metric engine** (governed SS3 orchestrator + composite evaluator, DEC-5ea578/DEC-ada203; produces Metric Snapshots), and the **Action engine** (does not exist; future authority DEC-3cc8a1; OUT of the Runtime Spine program scope with its trigger seam reserved on campaigns). No fifth engine: observation is input to admission. Engine names are the doctrine vocabulary; services implementing them cite their engine.

**2. The governed path is THE runtime.** The legacy execution path — OrchestratorService's resolution/metric chaining tail, canonical-resolution.service (canonical_mapping), metric.service/evaluation.service legacy evaluation — is FROZEN: no new consumers, no new capabilities; its live ticket hooks are ported to the governed engines before its removal (Retirement Register, R2→R5). bc-qa guard rules enforce the freeze mechanically as retirements land.

**3. Trigger modes.** Every engine invocation carries exactly one declared trigger mode: `manual` (operator/API call — today's only mode), `test` (dry-run, see 5), `scheduled` (cron-driven; PRECONDITION for scheduled admission: watermark/delta discipline at fetch — admission itself remains correctly non-idempotent), `event` (chained from an upstream engine's completion event via the persisted outbox, R2). Trigger mode is recorded on the run row.

**4. Run lifecycle.** Run states: `running → completed | failed | deferred_inputs_unavailable | abandoned | superseded`. Every run row carries a heartbeat; a reaper finalizes stale `running` rows to `abandoned` (fixes the TSK-560481 class). A re-evaluation of the same (metric, period) does not mutate prior runs — the prior evaluation is superseded ON READ (latest accepted evaluation per period), never rewritten (Invariant III).

**5. Dry-run is not a boundary act.** Every engine offers a dry-run: it computes and reports but emits NO progression object, NO evidence, touches NO watermark, and advances NO run state that downstream consumers read. Under the boundary-independent rules this is a diagnostic read (F-layer), which is exactly why it is safe at every engine and chainable end-to-end (campaign mode:test → a report, not persistence).

**6. Campaigns.** Multi-metric, multi-period evaluation is a first-class object: a campaign declares scope (metrics/families/all), period range, and mode; executes DAG-ordered (bases before composites); records a campaign row + per-run outcomes; retries deferred inputs within the campaign once upstreams land; is resumable and idempotent by (campaign, metric, period). Campaigns are the unit the scheduler and the event spine invoke (R1 builds this).

**7. Period-close semantics.** A fiscal period becomes read-ready per (tenant, period) via an explicit readiness object: sources admitted → canonical resolution complete → campaign complete → value audit green (R4). Read surfaces key on read-readiness, not on the mere existence of snapshot rows.

**8. NFR envelope (decided now, built later).** Admission: 1M rows/extraction sustained (DEC-4472ca batch-write model is the decided direction, implementation in R2); full-catalog campaign (≈100 metrics × 1 period) ≤ 10 min wall-clock at pilot scale; period-close → read-ready ≤ 1 h from last source admission; evidence retained per D212 (per-run RDS + S3 WORM detail); one-way-door implementation choices in R1/R2 (outbox vs in-process, worker vs in-request) are made against these numbers.

**9. Failure routing.** Every engine failure/blocker/deferral raises a boundary ticket via the governed-engine ticket surface (R2 ports BoundaryTicketService beyond the legacy paths) with flood discipline; ticket-worthy events also publish to the outbound webhook registry (ticketing is the first consumer; external stakeholder alerting attaches later without engine changes).

Authoritative doc: bc-docs-v3 docs/operations/runtime-operations.md (created with this ADR) — including the Retirement Register.
