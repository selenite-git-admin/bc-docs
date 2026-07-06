---
uid: DEC-049cb1
title: "Apex Generator Architecture for Permanent CFO Pack Demo"
description: "Locks bc-sdg's apex-tenant generator architecture: new src/apex/ module, 5 components (world-state RDS, pattern engine, bookkeeping-correct posting, bc-core push, Lambda+EventBridge), confirms Decisions A+B from the prior thread."
status: superseded
superseded_by: DEC-076521
date: 2026-05-08T08:37:43.157Z
project: bc-synth
domain: metrics
subdomain: synthetic-data
focus: architecture
---

> **SUPERSEDED by [DEC-076521 (D396)](ADR-076521.md)** on 2026-05-08.
>
> The architecture this ADR locked diverged from the canonical SAP S/4HANA pattern
> already documented in [`source-systems/sap-s4hana.md`](../../reference/source-systems/sap-s4hana.md)
> (authored ten days before this ADR). DEC-076521 corrects to: apex tenant uses
> `source_system='s4hana'` + existing `SapOdataV4Executor` + bc-sdg's 4200 OData
> server as the data origin under a profile-parameterised SDG-SAP framing.
> Components A / B / C semantic content preserved; Component D shrunk dramatically;
> the custom `ApexSnapshotExecutor`, `/snapshot` endpoint, and `apex-emitter`
> source_system are abandoned. See DEC-076521's §4 for the complete revert map.

# Apex Generator Architecture for Permanent CFO Pack Demo

## Context

The CFO Pack Demo is BareCount's permanent sales surface, anchored on the architectural isolation in DEC-771baf and DEC-1918d0. It must run autonomously, refresh its own data, monitor its own coherence, and use the same reader/admission/canonical/metric path a real customer's data would. Three properties drive the architecture:

1. Coherence by construction, not patch-up. The 8 storyboard coherence assertions are identity-level (Σ BSEG = GLT0; CCC = DSO + DIO − DPO; xPress same-party net = vendor balance − NBFC loan). A demo number that doesn't tie out kills the pitch. The posting generator must satisfy these by construction; the coherence Lambda verifies but does not fix.

2. Story patterns, not random noise. Random data produces uninteresting demos. Story-event PATTERNS instantiated quarterly produce fresh narratives that prospects can poke at without the named entities ever feeling stale. Patterns must be code-controlled — Demo Operations hard contract: "cannot be silenced".

3. Real reader runs, not simulated provenance. The Trust Chain shown in the demo must reflect real reader run IDs, real timestamps, real evidence rows. Pushing through bc-core's standard reader API (rather than bc-sdg writing directly to fact tables) is the only way to produce authentic provenance and keep the demo on the same architectural rails as a paying customer's tenant.

The five-component decomposition is non-overlapping by design. World-state is the ground truth for entity identity and pattern arcs. Pattern engine is the only writer to pattern state. Posting generator is the only writer to admission rows. Push layer is the only outbound caller. Lambda+EventBridge is the only orchestrator. Coherence check is read-only. Each component owns one verb.

The placement decision (new src/apex/ module, separate from both existing simulators) is defensive against debt. The existing simulators have known consolidation debt (TSK-5f16b0); apex must not inherit it. Apex is single-tenant, single-profile, push-mode; the existing simulators are multi-profile pull-mode. Conflating them would force premature consolidation.

The Lambda decomposition (5 functions, not 1) is also defensive. The cadences have different SLAs (emit daily; coherence hourly; rollover monthly) and different IAM scopes (rollover writes S3; emit calls bc-core API). Independent failure surfaces matter for the always-on demo — a coherence-check bug must not break the next day's emission.

Cost lock at ~$10–15/mo is well within the $10–30 target; Lambda free tier dominates; RDS is the only meaningful line item.

The implementation choice between push-mode-emulation (D-A) and push-executor (D-B) in the bc-core integration is explicitly deferred — both satisfy the architect-level lock; the sub-choice depends on bc-core's executor-registry shape and is a Phase 1 spike, not an ADR-level decision.

Lock the architecture for the bc-sdg apex generator that powers the permanent CFO Pack demo on the `apex` tenant. NO CODE in this session — this ADR is the architect-level lock. Implementation in subsequent bc-sdg sessions.

## 0. Module placement

A new top-level module `bc-sdg/src/apex/` houses the apex generator. It is NOT an extension of the existing 6100 in-memory simulator (in-memory ⇒ stateless across cycles, incompatible with continuous emission) NOR an extension of the 4200 DB-backed server (multi-profile pull-mode ⇒ wrong I/O direction; story-event semantics would entangle with stochastic profile generators). The Apex Motors profile (5 BUs, 4 plants, NBFC arm, ~9,500 customers, ~3,200 vendors, ~₹42,000 Cr revenue) lives at `src/profiles/apex.ts` extending the existing `ProfileDef`. Shared primitives in `src/core/` (event-graph, document-balancer, master-data-pool, seeded-random, number-range, event-history) and `src/scheduler/calendar.ts` + `src/scheduler/patterns.ts` are reused. The existing 6100 + 4200 simulators stay as-is for the sandbox1 dev tenant; the simulator-consolidation debt (TSK-5f16b0) is OUT OF SCOPE for Phase 1.

## 1. World-state persistence layer (Component A)

PostgreSQL schema `apex_world` in the existing `bc_sdg` cluster (port 5435) using Drizzle (already wired in bc-sdg). Tables:

- `entity` — generic master (customer / vendor / material / cost_center / plant / BU / NBFC borrower); ~13K rows total.
- `entity_relationship` — fleet-segment, MSME flag, NBFC-loan-to-borrower (xPress Logistics same-party).
- `price` — current + history per BU; FX rates by date.
- `period_state` — moving "demo current date" (today() − 30 days, last business day of prior month); visible vs archived periods.
- `pattern_state` — per-pattern state machine (pattern_id, current_arc_step, selected_entity_code, arc_started_on, arc_ends_on).
- `gl_chart`, `cost_center`, `standard_cost` — bookkeeping reference (incl. 1100-PLT Plating standard).
- `balance_snapshot` — per-(BU, period) running balances for coherence-by-construction.
- `emit_log` — batch_id, business_date, push_status, reader_run_id, error (read by Demo Health Dashboard).
- `coherence_check` — assertion-result history (read by Demo Health Dashboard).

DynamoDB rejected: relational shape + analytical queries (coherence checks must filter "all customers in delinquency arc step 4") are awkward in DynamoDB.

S3 used only for archived periods (`s3://barecount-apex-archive/period={yyyy-mm}/`) and Lambda layer artifacts. Coherence-assertion code is in source, not config — per Demo Operations hard contract ("cannot be silenced").

DB Change Protocol applies to all `apex_world` DDL — present to user before any execution.

## 2. Story-event pattern engine (Component B)

Each pattern is a code-defined state machine with: `id`, `cadence`, `arcLength`, `template` (storyboard template with named-entity slots), `selector` (rotates entity per arc), `affectedKpis`. State persists in `apex_world.pattern_state`. The 7 storyboard patterns (delinquent fleet customer, plating cost-center overrun, xPress same-party AR/AP, after-hours JE, group-consolidation delay, MSME 45-day exposure, quarterly-results variance) are defined in code, not config — per Demo Operations hard contract.

Engine ticks daily under the `apex-emitter` Lambda; each pattern checks "is it my time to advance"; if yes, the day's portion of the arc emits (e.g. delinquent-customer pattern day-15: skip the second payment cycle for the rotating selected fleet customer).

The named entities and amounts in the storyboard ("MetroLink State Transport ₹15 Cr") are TEMPLATES — what the pattern selector instantiates for the current arc. Rooth's narration reads from `pattern_state` for the current entity-of-record per pattern, so the storyboard remains coherent quarter-to-quarter without ever feeling frozen.

## 3. Bookkeeping-correct posting generator (Component C)

Reuses `core/document-balancer.ts` (`assertBalanced` already enforces SE-1: Σ debits = Σ credits per BKPF). Extends to:

- **5-BU intercompany clearing** (BU3 International → group elimination on consolidation; ₹89 Cr open is a pattern-driven story event)
- **Multi-currency** (BU3 INR ↔ IDR / USD with hedge book; FX rates from `apex_world.price`)
- **Cost-center actuals** (1100-PLT actual = standard + variance traced to chemical-bath event under the plating overrun pattern)
- **NBFC sub-ledger** (Apex Financial Services portfolio for xPress same-party flag)
- **After-hours JE** (BKPF.cputm + USNAM.U7341 for the Sep-14 23:47 IST anomaly under the after-hours-JE pattern)
- **Period totals** (GLT0 derived as Σ BSEG by construction — never asserted post-hoc)

The 8 storyboard coherence assertions hold by construction, not by patch-up. The coherence Lambda verifies; it does not fix.

## 4. Push-to-bc-core layer (Component D)

Apex pushes through bc-core's per-tenant reader-runtime endpoint surface: `POST /t/readers/:readerId/execute` (`bc-core/src/boundary/reader-runtime/reader-execution.controller.ts`) and the admission-run lifecycle in `bc-core/src/boundary/reader-runtime/`. A new `apex-emitter` reader (or family of per-source-family readers — FI, AR-AP, MM, SD, CO) is registered in bc-core under the apex tenant. Two implementation paths satisfy the lock:

- **(D-A) Pull-mode emulation**: bc-sdg exposes an HTTP "current snapshot" endpoint per emitter; the bc-core reader executes by fetching from it (consistent with the existing 6100 simulator pattern).
- **(D-B) Push executor**: extend `bc-core/src/boundary/reader-runtime/executor-registry.service.ts` to support a "push" executor that accepts payload-in-request as admission rows directly.

Choice deferred to Phase 1 implementation (quick spike at Phase 1 start, then locked). Both yield real reader runs, real run IDs, real evidence rows in the apex tenant DB. Both honour the Demo Operations hard contract "no direct DB writes". Both satisfy the locked Decision A.

Authentication: Cognito JWT scoped to apex tenant. Idempotency: each batch keyed by `(emitter_id, business_date)`.

## 5. Lambda decomposition + EventBridge scheduling (Component E)

**Five Lambdas, not one big function:**

| Lambda | Cadence (EventBridge cron) | Purpose |
|---|---|---|
| `apex-emitter` | Daily, 02:00 IST | Emit the day's posting batch; advance world-state; push to bc-core |
| `apex-close` | Last business day of demo month, 03:00 IST | Period totals; intercompany clearing; close-day-N tracking |
| `apex-pattern-refresh` | First day of each demo quarter, 04:00 IST | Advance patterns; select new entities for next-quarter arcs |
| `apex-coherence` | Hourly at minute 15 | Re-evaluate 8 storyboard assertions; write `coherence_check`; Slack/email on drift |
| `apex-rollover` | First business day of calendar month, 05:00 IST | Advance "demo current date"; archive oldest period to S3 |

**Justification for decomposition:** different timeouts (emit ~5min, coherence ~1min, rollover ~10min); different memory (emit ~1GB world-state load, coherence ~256MB); different IAM scopes (rollover writes S3, emit calls bc-core API); independent failure surfaces (coherence failure must not break next-day emission); cleaner CloudWatch streams per concern.

**Packaging:** zip + esbuild bundle (esbuild already in bc-sdg deps); single `.js` per Lambda < 50MB. Lambda layer for the Drizzle world-state client. The `src/scheduler/calendar.ts` + `src/scheduler/patterns.ts` primitives are reused inside Lambda handlers — but bc-sdg's existing always-on scheduler process is NOT used for apex (its multi-profile pull-mode shape is wrong for the apex single-tenant push case).

**Cost order-of-magnitude:**
- Lambda: ~1,650 invocations/mo, ~5K Lambda-min — comfortably within free tier.
- RDS: shared `bc_sdg` cluster or db.t4g.micro (~$10/mo).
- S3: a few MB/mo archive (~$0.01/mo).
- EventBridge: ~$1/mo.
- **Total: ~$10–15/mo**, within the $10–30 target.

## 6. Validation of locked decisions against bc-sdg's actual shape

- **Decision A (reader API push)**: CONFIRMED. bc-core's `boundary/reader-runtime/` module exposes the surface; the existing 6100 OData simulator stays for sandbox1; apex uses the new push path. Two paths cohabit, do not merge.
- **Decision B (Lambda + EventBridge)**: CONFIRMED with one wrinkle. bc-sdg has an existing process-resident scheduler (`src/scheduler/runner.ts`) designed for multi-profile pull-mode. Apex's cadence (episodic, mostly idle) fits Lambda better than always-on. The scheduler's calendar + pattern primitives are reused inside Lambda handlers; the scheduler process itself is not.

## 7. What this ADR does NOT lock (deferred to Phase 1 implementation)

- Push-mode (D-A) vs push-executor (D-B) sub-choice in Component D — Phase 1 spike
- Per-pattern emission logic — per-Lambda-build work
- Sub-phase breakdown within Phase 1 — implementation cadence
- `apex_world` schema DDL — subject to DB Change Protocol
- Apex tenant DB provisioning — subject to DB Change Protocol
- Cognito user provisioning for the 5 storyboard logins (meera/anil/suresh/pradeep/rajesh @ apex.in)

## 8. Cross-references

- `bc-docs-v3/docs/operating-model/demo-plan-cfo-pack.md` (Demo Plan)
- `bc-docs-v3/docs/operating-model/demo-plan-cfo-pack-storyboard.md` (Storyboard, 7 patterns, 8 coherence assertions)
- `bc-docs-v3/docs/operations/demo-operations.md` (operating model + hard contracts)
- `bc-docs-v3/docs/development/metric-readiness-toolkit.md` (diagnostic harness Phase 1 verifies against)
- ADR DEC-28b176 (D394) — Metric Readiness Model
- ADR DEC-771baf — Tenant database architecture (permanent-invariant barrier)
- ADR DEC-1918d0 — Database Rules (per-tenant SQL isolation)
- `bc-sdg/CLAUDE.md` — dual-simulator context
