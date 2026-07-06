---
id: demo-operations
order: 30.5
title: "Demo Operations"
status: drafting
authority: authoritative
depends_on: [operations-overview, tenancy-and-binding, metric-evaluation, evidence-and-lineage]
governing_sources:
  - CFO Pack Demo Plan (operating-model)
  - CFO Pack Demo Storyboard (operating-model)
  - Metric Readiness Toolkit (development)
  - InfoSec and Access Control (compliance)
governing_adrs:
  - DEC-076521 (D396 — Apex Tenant Binds to SAP S/4HANA Reader Chain; bc-sdg as Profile-Parameterised SDG-SAP Service)
  - DEC-771baf (Tenant database architecture; platform-tenant one-way dependency — the structural barrier for the permanent demo invariant)
  - DEC-1918d0 (Database Rules; per-tenant SQL isolation)
  - DEC-28b176 (D394 — Metric Readiness Model; the diagnostic harness Demo Operations verifies against)
  - DEC-d2cdb9 (D384 — SAP API admission stance)
  - DEC-6cb4f3 (D385 — Source Systems framework)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Demo Operations

The demo is BareCount's permanent sales surface. It runs autonomously, refreshes its own data, monitors its own coherence, and is built on the same architectural rails as a real customer tenant — by design, never with a real customer's data. This chapter documents the operating model and the hard contracts implementations must meet. Implementation specifics (Lambda function names, EventBridge rule schedules, bc-sdg module structure, cost line items) live in Phase 1 and Phase 4 ADRs filed when those decisions land.

## Why a separate operations chapter

The CFO Pack Demo Plan and its Storyboard describe what the demo *is*. This chapter describes what keeps it running, what it must never do, and how the operating team knows it's healthy. Three concerns demand a separate home:

1. **Cadences** — emission, coherence checks, period rollover, story-event refresh — all happen on schedules that need explicit specification.
2. **Hard contracts** — the demo must never read across tenant boundaries, never write directly to fact tables, never use real client data. These are non-negotiable and need to be stated as contracts, not policies.
3. **Health visibility** — when the demo silently degrades (a coherence assertion drifts, a story-event pattern stops firing, a cost budget is breached), the operating team must learn within hours, not weeks.

Phase 4 of the Demo Plan implements this chapter. This document defines what success looks like.

## The demo's permanent shape

| Property | Value |
|---|---|
| Tenant | `apex` (separate from `sandbox1` dev tenant). Demo URL: `apex.barecount.app/beyond` |
| Source system identity | `s4hana` — the existing platform row. Trust Chain reports SAP S/4HANA Cloud. |
| Data origin | bc-sdg (the SDG-SAP service; profile-parameterised) only. Never any production tenant's data. |
| Data path | bc-core's SAP reader **pulls** from bc-sdg's 4200 OData server (S/4HANA Cloud landscape) on its own schedule. The single difference between apex and a real S/4HANA customer is `runtime.connection.endpoint_uri`. |
| Profile | `apex-motors` (auto-OEM industry, the first storyboard-driven profile). |
| Lifetime | Permanent. The demo continues to exist after BareCount has paying clients. |
| Refresh | Continuous regeneration of `sdg_world` data with quarterly story-event pattern refresh. The demo never feels frozen. |
| Pruning | Last 24 months kept hot in apex tenant DB; older periods archived to S3. |

The demo's permanence is a strategic decision documented in the [Demo Plan's Permanent Demo Invariant](../evidence/work-records/operating-model/demo-plan-cfo-pack.md#permanent-demo-invariant--client-data-access-is-denied-by-design) section. Marketing surfaces never use real client data because the architecture (DEC-771baf, DEC-1918d0) does not permit it — connections are isolated at the database, schema, and direction-of-dependency levels. Implementation in `bc-core/src/database/tenant-connection.service.ts`.

## Cadences

Five operational cadences keep the demo current.

| Cadence | Frequency | What happens |
|---|---|---|
| **Routine generation** | Daily | bc-sdg's apex-motors profile regenerates the day's BSEG/BKPF rows in `sdg_world` partition `profile_code='apex-motors'`. World-state advances by one business day. bc-core's SAP reader pulls these on its own schedule via the OData endpoint. |
| **Monthly close** | Monthly (last business day of demo's "current month") | Period totals roll up; intercompany clearing; close-day-N tracking refreshes; the storyboard's "close runs Day N" event fires per the period's pattern state |
| **Quarterly story-event refresh** | Quarterly | Story-event patterns advance — a new delinquent-customer arc starts; the previous one resolves; a new cost-center overrun selects its target; the next quarter's analyst-consensus variance is set |
| **Coherence check** | Hourly | The 8 storyboard coherence assertions are re-evaluated against the live apex tenant; any drift triggers an alert and a `demo_health` log row |
| **Period rollover** | Monthly (first business day) | "Demo current date" advances by one month; the oldest period that pushes outside the 24-month visible window is archived to S3; readiness dial verified at 36/36/0 |

Each cadence has an exit criterion that's checkable from the Readiness Toolkit:

- After routine emission: the emitted day's postings appear in `progression.admission` for the apex tenant.
- After monthly close: the period total in `GLT0` equals the sum of detail postings (`BSEG`) within the period.
- After quarterly story-event refresh: the new pattern's first event is observable in the relevant metric.
- After coherence check: all 8 assertions return passing within tolerance, or an alert fires.
- After period rollover: `devhub_readiness_dial tenant=apex` returns `producing: 36 / wouldProduceIfBound: 0`.

## Hard contracts (what the implementation must never do)

These are the non-negotiable invariants that demo implementation in any phase must satisfy. Violations are bugs of the highest severity.

| Contract | Why | How to detect a violation |
|---|---|---|
| **bc-core's SAP reader pulls from bc-sdg via OData only — no direct DB writes from bc-sdg into tenant tables** | The Trust Chain shown in the demo must reflect a real source-to-canonical-to-metric chain; direct writes would produce a fake chain | Audit: check that every fact row in `apex.fact.co_*` has a corresponding `progression.canonical_evaluation` row whose `admission_id` traces to a real `progression.admission` row sourced by the SAP S/4HANA Cloud reader (executor=`SapOdataV4Executor`) |
| **bc-sdg's `sdg_world` is only read by the SAP OData server; bc-sdg writes nowhere outside `bc_sdg.sdg_world.*`** | Cross-tenant writes would leak demo data into production surfaces | Audit: bc-sdg's connection string is hard-coded to `bc_sdg`; no configuration that would let it write to any tenant DB |
| **The demo's `runtime.connection` for apex is the only platform-DB row apex-emission depends on** | The Trust Chain's path is identical to a real S/4HANA customer's — only the connection endpoint differs | Audit: `runtime.connection` row with `tenant_id='apex'` and `source_system_name='s4hana'` exists; its endpoint_uri is the bc-sdg 4200 URL; nothing else in the catalog identifies apex as synthetic |
| **The coherence assertions cannot be silenced** | If an operator can disable a failing coherence check, the *"data settles"* claim erodes silently | Implementation: the coherence monitor's check list is read from a code-controlled file, not a runtime config flag |
| **Story-event patterns produce coherent state, not random noise** | A pattern that breaks coherence (e.g. emits a JE without a balancing entry) violates the bookkeeping correctness | Implementation: each pattern's emit step is wrapped in a transaction that includes the balancing posting; coherence check runs after every batch |
| **No marketing-surface tools ever read tenant data outside apex** | This is the Permanent Demo Invariant in operational form | Audit: any tool that produces a marketing artefact (case-study generator, screenshot tool, etc.) is implemented in a code path that lacks a connection string to any tenant other than apex; review at code-review time |

## Required surfaces

Three internal-facing surfaces support Demo Operations. None are visible to prospects.

### 1. Demo Health Dashboard (bc-admin internal)

A read-only page that shows, at any moment:

- Apex tenant readiness dial — must always be `bound: 36 / producing: 36 / wouldProduceIfBound: 0`
- The 8 coherence assertions — each green or red, with last-check timestamp
- Last-successful generation cycle (timestamp + batch size)
- Story-event pattern recency — each of the 7 patterns has fired within its expected window
- Period rollover state — current "demo current date", oldest visible period, next archive cycle
- Cost trailing 30 days vs budget

A glance at this page tells the operator whether the demo is healthy. Stale states are visible without searching.

### 2. Coherence Monitor Daemon

A scheduled job that:

- Reads the 8 storyboard coherence assertions from a code-controlled file
- Re-evaluates each against apex tenant DB
- Writes results to a `demo_health.coherence_check` log table (tenant DB)
- Alerts (Slack / email / page) on any assertion failure within tolerance

Alerts include the assertion that failed, the expected vs actual values, the run ID, and a link to the assertion's source. The operator's first action after an alert is to inspect — never to silence.

### 3. Cost Monitoring + Budget Alarms

Tracks:

- Lambda invocation count + duration for bc-sdg emitters
- EventBridge event count
- Apex tenant DB size (with growth rate)
- S3 archive size (post-rollover)

Budget alarms fire at configured threshold points against the monthly cap. Phase 1 sets the cap based on actual measured Phase 1 emission volume; Phase 4 wires the alarms.

## Period rollover semantics

"Demo current date" is a moving variable defined as `today() − 30 days` rounded to the last business day of the prior calendar month. Implications:

- A prospect viewing the demo in November 2027 sees October 2027 as "current cycle" (or whichever month-end the rollover landed on).
- The visible cycle is always the last completed month, never an in-progress month.
- All temporal references in Rooth's narration are relative to "demo current date", not literal dates baked into the storyboard.

The 24-month visible window means the demo always shows two calendar years of data — long enough for year-over-year comparisons, short enough to keep apex tenant DB size bounded. Older periods are archived to S3 in compressed form; if a future demo iteration needs a longer history, archives can be replayed.

## How Demo Operations interacts with the platform's other operational pillars

| Pillar | Relationship |
|---|---|
| [Readiness Toolkit](../development/metric-readiness-toolkit.md) | The Coherence Monitor uses `GET /api/admin/readiness/tenant/apex/formula-token-audit` and the readiness dial as its diagnostic primitives. It does not implement its own audit logic. |
| Tenant Metrics | Demo Health Dashboard surfaces the apex tenant's per-MC operational view alongside the dials, for drill-down when a coherence assertion fails. |
| Test Bench | Used during Phase 1 to validate emission shape; not part of the always-on operational loop. |
| Inspector | Used during incident response to walk a specific MC's chain and identify where coherence broke; not part of the always-on loop. |
| Schema Provisioner | The reconcile path is invoked once when the apex tenant is first provisioned. After that, demo-time changes to the catalog (rare; only for new hero KPIs) trigger a reconcile. |

The Readiness Toolkit is the diagnostic; Demo Operations is the operating model. They are complementary, not overlapping.

## Marketing playbook (post-clients) — operational reference

The full table of allowed/forbidden marketing patterns lives in the [Demo Plan's Permanent Demo Invariant](../evidence/work-records/operating-model/demo-plan-cfo-pack.md#permanent-demo-invariant--client-data-access-is-denied-by-design). Operationally, the rules collapse to:

- Anything that's a derived artefact of consented client interaction (case study, redacted screenshot, aggregate stat) — reviewed and approved before publication
- Anything that involves a production tenant's data being read by a marketing-surface tool — forbidden, full stop
- Live demos with prospects always run on apex; demo recordings are derived from apex; case studies describe outcomes without ever showing operational reads

The architectural barrier (DEC-771baf, DEC-1918d0) ensures the team cannot violate this even if pressured. The marketing process layer enforces the consent-management for the allowed patterns.

## What Phase 1 must deliver to make this chapter implementable

Phase 1 is bc-sdg's `apex-motors` profile under the SDG-SAP service, plus the apex tenant binding to the SAP S/4HANA reader chain. Per [DEC-076521](../governance/adrs/ADR-076521.md), from an operations standpoint Phase 1 must deliver:

- An `apex-motors` profile in bc-sdg's 4200 OData server profile system that regenerates `sdg_world` data on the cadences specified above
- The 7 story-event patterns wired to the quarterly refresh cadence
- A `runtime.connection` row for apex tenant pointing at bc-sdg's 4200 /s4cloud OData endpoint with `apex-motors` profile selector, plus a `runtime.reader_binding` linking the existing SAP S/4HANA Cloud reader to apex
- An emit log (timestamp, batch size, errors) in `sdg_world.emit_log` that the Coherence Monitor reads

After Phase 1, Phase 4 builds the always-on operational scaffolding: Coherence Monitor Daemon, Demo Health Dashboard, Cost Monitoring + Budget Alarms.

## Cross-references

- [CFO Pack Demo Plan](../evidence/work-records/operating-model/demo-plan-cfo-pack.md) — the four-phase plan; the Permanent Demo Invariant section
- [CFO Pack Demo Storyboard](../evidence/work-records/operating-model/demo-plan-cfo-pack-storyboard.md) — the locked narrative; the 8 coherence assertions
- [Metric Readiness Toolkit](../development/metric-readiness-toolkit.md) — the diagnostic primitives the Coherence Monitor uses
- [InfoSec and Access Control](../compliance/infosec-and-access-control.md) — the structural-isolation source
- [ADR-28b176 (D394 — Metric Readiness Model)](../governance/adrs/ADR-28b176.md) — the readiness model that backs the dials
