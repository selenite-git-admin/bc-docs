---
uid: DEC-01bd6b
title: "Runtime Orchestration"
description: "Two axis-orchestrators (admission on the source axis, evaluation on the metric axis); pull-first plus fully-specified push admission; governed version-pinned selection; reads never trigger evaluation."
status: decided
date: 2026-08-18
project: bc-core
domain: runtime
subdomain: orchestration
focus: architecture
---

# Runtime Orchestration

## Context

The reader-model ADR defines the machines but not what *drives* them. Without a governed orchestration model the four machines are open to misinterpretation — the live `RuntimeSchedulerService` schedules admission by `readerId:flavorId` pairs (the wrong abstraction). This ADR fixes the abstraction axes, the run/cycle identities, the selection governance, the trigger discipline, and both admission modes (pull and push), so neither the model nor push is left to future interpretation. Only build order is phased.

## Predecessor authority lineage (valid whole/partial mechanics)

This ADR conflicts with live runtime doctrine; each is reconciled by valid mechanics (whole-supersede via `superseded_by`, or an in-body amendment note while the predecessor stays `decided`/`implemented`). Reconciling chapters alone does not neutralize decided/implemented ADR text.

| Predecessor | Conflict with this ADR | Effect | Mechanism |
|---|---|---|---|
| `DEC-9c0da7` (Runtime Doctrine) | Action engine "does not exist / out of spine"; "latest accepted evaluation per period" **on read**; dry-run as a diagnostic read that **computes** | **Partial amendment** — the four-boundary spine (incl. Action), the no-read-trigger rule, and governed exact selection amend those clauses | in-body amendment note on `DEC-9c0da7`; stays `decided`; the amended clauses named in this ADR body |
| `DEC-c0290f` (Metric Evaluation Engine, `status: implemented`) | schedule-driven orchestration + `best_effort` "evaluate with whatever is available" + downstream Step Functions DAG | **Partial amendment** — governed version-pinned selection (Decision 5) replaces `best_effort`; the two-orchestrator model supersedes the single-engine orchestration; schedule survives as one governed trigger among several | in-body amendment note; **stays `implemented`**; amended clauses named here |

(The composite-runtime authority `DEC-ada203` is reconciled via the reader-model ADR lineage matrix + register E6 — the Metric boundary's exact-Snapshot proof. `performance-and-scale.md` is reconciled in the reconciliation plan on its **full** conflict scope: the cron-as-trigger (→ governed scheduled commands, this ADR's Decision 6), the same-row/supersede-on-value-change snapshot mutability (→ every evaluation act yields a **new immutable** Snapshot version), and the verifier-re-evaluates behavior (→ verification reads preserved state).)

## Decision

### 1. Two axis-orchestrators, not one integrated manager
- **Admission Orchestrator** — drives the **Runner**, on the **source axis**.
- **Evaluation Orchestrator** — drives the **Canonical, Metric, and Action Evaluators**, on the **metric/group/sub-function axis** (a *batching scope*, not an evaluation identity or authority — see Decision 5).

They are **loosely coupled by preserved progression data, not control**: evaluation reads governed, version-pinned inputs (never "whatever exists") and never triggers admission; nothing cascade-recomputes. They run over **shared infra primitives** (scheduling, queuing, observability). **The Reader is the orchestration unit for neither** — anchored per Entity, admission orchestrates per source, evaluation orchestrates per metric group.

### 2. Source cycle vs Admission Runs (ORCH-2)
`runtime.admission_run` requires one `reader_id` + one contract coordinate, so it **cannot** represent a Connection-wide act spanning many Entity-anchored Readers. Therefore:

- A **source cycle** is an **outer coordination record** — one Connection instance, one intended as-of intent — over **N independently-proven Admission Runs** beneath it (one per participating `(Reader, Flavor, source entity)`). The source cycle is *not itself* an Admission Run and produces no progression object; each Admission Run remains the boundary act with its own proof (Invariant II preserved).
- **Coordination receipts are NOT boundary Evidence.** The source-cycle record is a **coordination / audit receipt** (a non-boundary record), never Foundation boundary Evidence. Boundary Evidence + Lineage belong **only** to the Admission Runs/acts that actually occur. A pre-run refused chain (which produced no Admission Run) receives the **separately named coordination refusal receipt**, not boundary Evidence — unless an existing governed refusal *act* is explicitly identified as the emitter.
- **Whole-vs-partial cycle (operator decision — default atomic):** the default is **atomic chain resolution before any fetch** — if any participating chain fails to resolve, the whole cycle refuses (recording a coordination refusal receipt) and no Admission Run starts. A source may instead be declared **partial-tolerant**, in which case each admitted chain's Admission Run carries its own boundary Evidence and each refused chain carries a coordination refusal receipt.
- **Chain resolution alone does not establish coherence.** Even in atomic mode, a coherent source as-of exists **only** where the source/connector contract supplies a snapshot token or transaction boundary (Decision 8 / ORCH-4); successful chain resolution is necessary but not sufficient.
- Physical run substrate/DDL is deferred (register §H); the **logical identities (source cycle ⊃ N Admission Runs; coordination receipt ≠ boundary Evidence) are fixed here.**

### 3. Admission PULL (built first)
The Admission Orchestrator polls a source on a governed **cadence** and advances **per-entity watermarks** within one source cycle. Chain resolution runs once before fetch (per Decision 2). Each admitted transaction becomes one immutable Source Object + Evidence + Lineage; rejected observations emit **Evidence only**.

### 4. Transport dedup vs admission non-replay (ORCH-3)
Two distinct layers, never conflated:
- **Transport dedup — before admission.** Watermark advancement and a recognized transport replay (same event-key/sequence already processed) are suppressed at the *transport* layer; a recognized replay creates **no** admission act.
- **Admission non-replay — Invariant V.** Once an observation is *presented* to an admission act, a repeated observed state is a **distinct act yielding a distinct Source Object**. There is no re-admission suppression by observed-state identity at the admission boundary.

### 5. Governed evaluation selection (ORCH-1, ORCH-5, FND-R2-3)
Every Evaluator invocation **names a governed target** (Metric/Canonical/Intervention Contract version), an **evaluation parameter/window**, and either **fixed input versions** or a **versioned governed-selection artifact** (DEC-c4c742 governed selection); the **resolved object set is recorded in Lineage**. "Reads whatever Canonical Objects exist" / "latest/current" selection is prohibited — query convenience is not reference authority.

### 6. Triggers — explicit commands/events only; reads never trigger (ORCH-5, FND-R2-2)
- **Reads never trigger evaluation.** A read displays preserved state or readiness only. (The "dashboard open evaluates" language is removed.)
- **Schedule** (built first) — a governed scheduled *command* invokes canonical/metric evaluation for a named target/window with pinned selection.
- **Explicit demand** (built first) — an authorized *command* (separate from the read) may create new boundary acts, pinning exact input versions.
- **Freshness** (later, register C6) — a governed *event* (new Canonical Objects for a target) may enqueue a command; still not an implicit read or Lineage traversal, and never a cascade recompute.

### 7. Action triggering is an explicit boundary invocation (ORCH-6)
A governed command/event invokes **the Action Evaluator** against a **named Intervention Contract version**, **fixed Metric Snapshot IDs**, and a **fixed evaluation context/window**. The **Action Evaluator itself applies the Intervention Contract condition** and either emits **one Action Object** (with synchronous Evidence + exact Lineage; Metric Snapshot references fixed at creation) or terminates with **failure / no Action Object**. There is **no separate unnamed pre-evaluator** — introducing one would risk a fifth boundary or an ungoverned gating act. The Action Evaluator must not watch an implicit "current/latest" snapshot or turn a read into an Action act.

### 8. Admission PUSH (defined now, built later — register C4/P3)
Push is a first-class admission mode, specified so it is never reinvented; it changes the *trigger*, never the admission semantics (same per-entity AC/OC act, same immutable Source Object, same Evidence/Lineage).
- **Ingress + auth.** A Connection declares `ingress_mode ∈ {pull, push, both}`; a push Connection has a governed receive endpoint; event authenticity is verified against the Connection's external-secret credential reference before any admission act.
- **Event identity + ordering.** Each event carries a **durable source-assigned or governed-derived event identity**, an **ordering coordinate** (source sequence/version), a **conflict rule**, and defined **refusal + Evidence** behavior. Transport replay is deduped per Decision 4; it never mutates an existing Source Object (Invariant III).
- **Coherence is declared, not manufactured (ORCH-4).** A push micro-batch supplies a **processing cutoff/window**, *not* automatically a coherent source as-of — especially with late/out-of-order events. The source contract declares **watermark, allowed lateness, window close/reopen, and correction behavior**; a coherent as-of exists only where the source/connector contract supplies a snapshot token or transaction boundary.
- **Completeness is declared per source, not assumed (ORCH-4).** "Push lossy / pull complete" is **not** universal (CDC may capture what snapshot polling misses; a pull API may be partial). Each **source contract declares** the completeness semantics of pull, push, and any reconciliation sweep, and the **evidence** that establishes them. A reconciliation sweep is a backstop only where the source contract says it is.

## Consequences
- **Retires** the reader-centric `RuntimeSchedulerService` abstraction (register C8); reconciles the authoritative Operations chapters (register B4).
- **Constrains** deferred physical infra (register §H): it must preserve two orchestrators, the source-cycle ⊃ N-Admission-Runs identity, governed selection, boundary-act independence, and per-source completeness/coherence contracts.
- **Deferred (named):** push build (P3), freshness trigger (later), Runner hardening (§G), physical infra (§H).

## Foundation gate
- **Repair location:** the deferred runtime-component/orchestration layer. **Design act.** Inherits — does not restate — the four boundaries and Invariants II/IV/V; adds no execution-plane net.
- **Invariant check:** Decision 5 pins governed version-selection into Lineage (IV/VI); Decision 6 removes read-triggering (boundary-independent rule); Decision 2 preserves per-run boundary-act independence (II); Decision 4 preserves non-replay (V).
