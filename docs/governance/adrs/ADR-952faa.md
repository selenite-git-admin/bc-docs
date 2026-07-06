---
uid: DEC-952faa
title: "Metric Temporality Class & Inspector — close the semantic gap and lock a first-class trust surface"
description: "Five decisions: (1) add temporality_kind axis to metric_definition (instantaneous | flow_per_period | stock_at_period_end | cumulative_to_date), (2) authoring/activation gate that refuses flow primitives on stock-class metrics, (3) stock-class formula primitives (BALANCE_AS_OF + siblings), (4) Metric Inspector as a first-class bc-admin surface — drill-down spine + cross-pivots + live samples — not a debug route, (5) cross-cutting invariant: every chain-complete MC must be navigable from the Inspector or it isn't trusted."
status: decided
date: 2026-04-28T15:44:34.923Z
project: bc-core
domain: metrics
subdomain: metric-semantics
focus: temporality-and-inspector
---

# Metric Temporality Class & Inspector — close the semantic gap and lock a first-class trust surface

## Context

After a long chain-build arc landed structurally sound on a demo tenant, a finance-flavoured metric labeled "Total AR Balance" was observed on the monitor page rendering a value that — to a finance reader — reads as a balance at a point in time, but was in fact computed as `SUM(<amount>) GROUP BY fiscal_period` over the open-items source: a **flow** shape labeled with a **stock** semantic. The contract model expressed the formula identically to a legitimate flow metric (e.g. monthly billing volume); no audit caught the mismatch because the platform has no representation of metric *temporality class*.

> See **Incident evidence** at the bottom of this ADR for the dated record of what was observed.

Three patterns made this invisible until a human read the rendered value with domain knowledge:

1. **Contract model expresses rules, not semantics.** `metric_contract.formula = "O1 = SUM(I1)"` is identical for "Total Sales" (flow) and "Total AR Balance" (stock). The contract carries no axis distinguishing them. The engine has no basis to reject one shape for one class.
2. **Pre-D335 cc_field_mapping cruft.** 23 rows of shape `fiscal_period ← <bf>_document_date_time (rule=latest)` polluted the platform — pre-D363 thinking that conflated calendar date with fiscal period. Today's cleanup removed them; the same audit gate would have caught them years earlier had it existed.
3. **Past chain-visibility surfaces have been flat catalogs, not inspectors.** The Metric Catalog (D024), Metric Readiness (D316), Chain Status (D305), L-node verification (D366) all surface per-MC verdicts — "complete", "partial", "broken". None of them walk a human from one metric down through every layer to the literal source field on the literal source table for a real tenant, with the actual data flowing through. Chain-green is necessary; semantic-correct is necessary; both visible to a human is necessary. We currently have only the first.

User reviewed the gap and chose Option B (full platform fix over pivot to flow-only metrics) AND added the requirement: "I want something persistent in UI to view/review/audit/monitor each metric e2e per source/reader. In bc-admin. We tried many approaches but none was sufficient. These mishaps shake my confidence further down."

This ADR locks the WHAT for the missing semantic axis AND the missing operator surface together, because either alone is insufficient. A temporality classification with no place to inspect a metric against its own data is invisible. An inspector with no semantic axis to verify is a debug tool. Both, together, make the platform's chain-completeness claim resilient to semantic drift — and recoverable when drift sneaks in anyway.

## Decisions

### D-1 — Add `temporality_kind` to `metric_definition` as a required, non-null axis

Four enumerated values:

| Value | Meaning | Example | Aggregation primitive |
|---|---|---|---|
| `instantaneous` | Point-in-time observation, no time-axis aggregation | Current employee count pulled live | None — value passes through |
| `flow_per_period` | Flow attributed to the period of its event | Monthly billing volume, daily transaction count | `SUM`, `COUNT`, `AVG` over period transactions |
| `stock_at_period_end` | Balance/level at the boundary of a period | AR balance, inventory on hand, headcount as-of | `BALANCE_AS_OF` (D-3) |
| `cumulative_to_date` | Running total from a fixed start | YTD revenue, lifetime customer value | `CUMULATIVE_SUM` (D-3) over flow input |

The axis is **required**: a `metric_definition` row may not be created without it, and existing rows backfill before any new authoring is allowed (Stage 3 in the implementation tracking below).

Where it lives: **`metric.metric_definition.temporality_kind text NOT NULL`** (verified live: `metric_definition` is in the `metric` schema; `contract` schema only carries the FK on `metric_contract.metric_definition_id`). Add a CHECK constraint enumerating the four values. Stored values are the raw enum strings; UI/translation is bc-admin's concern. The axis is on `metric_definition` (not `metric_contract`) because temporality is a property of the *concept* the metric measures, not of the formula version that computes it. A `metric_contract` version inherits the kind from its parent definition via the existing FK.

**P2.4 — coexistence with the existing 5D `temporality_code`.** The `metric_definition` table already carries `temporality_code` as one of the five mandatory classification dimensions of the Metric Specification Framework (DEC-9dce29 / D281). Replacing it would be too much blast-radius for this ADR. Instead, `temporality_kind` is added as a **finer, computational** axis next to the existing 5D `temporality_code`, with explicit compatibility rules — neither column dominates; both must be filled, and contradictions are rejected at authoring/activation:

| `temporality_kind` | Compatible `temporality_code` values |
|---|---|
| `instantaneous` | `point_in_time`, `as_of` |
| `flow_per_period` | `period`, `interval`, `recurring` |
| `stock_at_period_end` | `point_in_time`, `as_of`, `period` (when reporting cadence is period-end) |
| `cumulative_to_date` | `cumulative`, `period` (with running-total semantics in `temporality_code`'s description) |

Authoring/activation gate (D-2) extends to: a metric whose `temporality_kind` is **not** in the compatible-set of its `temporality_code` is **rejected** at the same boundary as primitive-class mismatch. Audit message names both columns and the compatible-set. Both columns are required; neither has a default. The eventual normalization (whether one column subsumes the other) is left to a follow-up audit ADR after Stage 3 backfill reveals real-world value distributions across the catalog.

### D-2 — Authoring + activation gate refusing primitive-class mismatch

Metric authoring (`POST /api/registry/metric-contracts`) and activation (governance state → 'active') validate formula primitives against `temporality_kind`:

- `temporality_kind=stock_at_period_end` → primitives `SUM`, `COUNT`, `AVG`, `MIN`, `MAX` are **rejected**. Stock metrics MUST use a stock-class primitive (`BALANCE_AS_OF` initially; D-3 lists siblings).
- `temporality_kind=flow_per_period` → primitives `BALANCE_AS_OF`, `SNAPSHOT_DELTA` are **rejected**. Flow metrics MUST use flow primitives.
- `temporality_kind=cumulative_to_date` → only `CUMULATIVE_SUM` is allowed; raw `SUM` is rejected (the engine must walk forward through periods, not aggregate one period's bucket).
- `temporality_kind=instantaneous` → no period-bucketed primitive; passthrough.

Gate runs at two boundaries:

1. **Authoring** — refuses creation of an MC version with a mismatched formula. Message names the temporality_kind, the offending primitive, and the allowed set.
2. **Activation** — a separate gate at the `governance_state → active` transition catches MCs whose temporality_kind was changed after authoring (either retroactively classified or the formula was patched in place — neither path should bypass the gate).

The audit is **structural**, not opt-in. The existing `contract.chain_status.chain_verdict` enum stays at its current four values (`complete | partial | broken | unlinked`) — verified live against the CHECK constraint on `contract.chain_status`. This ADR does **not** amend the verdict taxonomy or the Chain Completeness chapter (`bc-docs-v3/docs/operating-model/chain-completeness-and-verdict.md`). Instead:

- An existing chain-complete MC that fails the temporality_kind ↔ primitive gate is rolled up to `chain_verdict = 'broken'` (or `'partial'` if other variables remain green) per the existing rollup rules in the Chain Completeness chapter.
- The reason carrying the semantic cause is encoded in **`chain_status.break_summary_json.reason_code`** (existing column; structured payload), with the new value `semantic_class_mismatch` for D-2 and `inspector_unreachable` for D-5. Both reason codes are platform-wide structured strings; they don't require any new enum/check constraint.
- ChainStatusService extends `break_summary_json` to include the reason code, the offending primitive, the metric's temporality_kind, and the temporality_code at the time of compute. Reason codes are documented in the Chain Completeness chapter as a *non-exhaustive* set, allowing future additions (governance, drift) without ADR overhead per code.

This keeps schema churn at zero and reuses the rollup machinery the chain status service already runs.

### D-3 — Stock-class and cumulative formula primitives

Engine-level primitives that read from a snapshot-aligned source path, not the period-bucketed transaction path used today:

- `BALANCE_AS_OF(input)` — for each grain at each period boundary, evaluate the balance. Source pattern requirement (Stage 5 in tracking) is either (a) dated snapshots of the open-items source ingested at end-of-period, or (b) reconstruction from base-source + delta-source + clearing dates replayed forward. Either pattern is recorded on the OC; the engine reads which pattern applies and dispatches accordingly.
- `SNAPSHOT_DELTA(input)` — period-over-period change in a stock value. Composes on `BALANCE_AS_OF`.
- `CUMULATIVE_SUM(input)` — running total of a flow input, from a declared fiscal-year-start (or other declared anchor). Composes on flow primitives.
- `WEIGHTED_AVG_OVER(input, weight)` — average weighted by another field across a period; useful for things like "average days outstanding weighted by amount."

D-3 only locks the *names and shapes*; engine implementation lands per-primitive in Stage 4.

**Two-gate activation rule** (closes P2.3 of the Codex review):

| Gate | Allows | Rejects |
|---|---|---|
| **Authoring** (`POST /api/registry/metric-contracts`) | Primitive ∈ `allowed_by_class[temporality_kind]`. May reference a not-yet-implemented primitive — MC stays at `governance_state='proposed'`. | Mismatched-class primitive (per D-2). |
| **Activation** (`governance_state → active`) | Primitive ∈ `allowed_by_class[temporality_kind]` **AND** primitive ∈ `engine.implemented_primitives` (runtime registry). | Either condition fails. Activation refused until the primitive lands. |

This closes the failure mode where an MC could pass class-compatibility but be unevaluable at runtime — `chain_status` would say `complete` while the engine throws "primitive not yet implemented" on every dispatch. With the two-gate rule, an unimplemented primitive blocks activation and therefore blocks `chain_complete`. The Inspector's D-5 invariant remains intact.

The list of `engine.implemented_primitives` is a runtime-introspected set (queries the metric engine's primitive registry); not a static config. New primitives become activation-eligible the moment they land, no separate metadata flip required.

### D-4 — Metric Inspector as a first-class bc-admin surface

A persistent bc-admin route — **placed as a tab on the existing metric-definition detail page** at `/catalog/metrics/definition/:id` (e.g. `/catalog/metrics/definition/:id?tab=inspector` or `/catalog/metrics/definition/:id/inspector`, depending on the bc-admin tab convention at implementation time). This aligns with the existing Metric Catalog route family — there is no `/admin/...` prefix in the current bc-admin router, and creating a new route family for one surface would add navigation friction without benefit. Inspector becomes the operator-focused tab next to the existing Definition / Knowledge / Chain tabs on the same page; users land here from a catalog row → definition detail → Inspector tab. Not a developer tool, not under `/debug`, but also not a separate top-level URL.

**Required sections:**

| Section | Contents |
|---|---|
| Header | metric name, temporality_kind, formula text, current chain verdict, last evaluation timestamp + run id |
| Tenant pivot | which tenants have this MC bound? for each, latest values + chain-status verdict |
| Chain spine (drilldown) | top-to-bottom: Metric Definition → Metric Contract + version → Canonical Contract + Canonical Mapping → Observation Contract + field map → Reader Flavor + Connector → Source Catalog (table + fields). Each row clickable to expand: live counts, 5 sample rows, governance state, last activated, supersession chain, drift cases. |
| Audit log | every change to MC/CC/CM/OC/SC, who, when, ADR ref, supersession links. Reads from devhub change records + activity_log. |
| Monitor pane | last evaluation per period, snapshot count, dispatcher activity, readiness ledger entries. Reads from progression.* + readiness_ledger. |
| Semantic checks | temporality_kind ↔ formula primitive match (from D-2 gate), grain alignment with temporality_kind, source-pattern fitness for the metric class, OC body ↔ index drift, posting_date_field ↔ resolved_schema completeness. Each check has pass/fail + evidence link. |
| Cross-pivots | (a) "what other metrics consume from any of this metric's source fields?" — change-impact lens. (b) "if I change source X.Y, what metrics break?" — same lens, opposite direction. |

**Required behaviors:**

- All data shown is **for the chosen tenant**, with a clear tenant switcher. No "platform-only" mode that hides tenant-runtime evidence; this is the operator's surface, not a registry browser.
- Every numeric value shown links to its **source rows** — clicking the metric snapshot value walks back to the COs that fed it, then to the SOs that fed those, to the source-table rows that produced those. Reproducible audit, not just attestation.
- The page **survives chain breaks** — if a layer is broken, the inspector shows the break with evidence rather than 404'ing. A broken metric is precisely when the inspector is most needed.

The Inspector is **not** the bc-admin Metric Catalog. The catalog is for browsing; the Inspector is for verifying. Both surfaces persist; users navigate from catalog row → definition detail page → Inspector tab.

**Backend read contract** (closes P1.3 + P2.2 of the Codex review):

The Inspector mixes platform-DB and tenant-DB reads. The two stores are **never** joined in a single query; the API surface composes them per section, with explicit scope per endpoint.

| Section | Backend endpoint (proposed) | Scope guard | Source store(s) |
|---|---|---|---|
| Header | `GET /api/t/metrics/{uid}/inspector/header` | `@TenantScoped()` | platform: `metric.metric_definition`, `metric.metric_contract` (latest version), `contract.chain_status` |
| Tenant pivot | `GET /api/metrics/{uid}/inspector/tenants` | `@PlatformOnly()` (cross-tenant read; admin role only) | platform: `tenant.contract_binding` + `contract.chain_status` |
| Chain spine (drilldown) | `GET /api/t/metrics/{uid}/inspector/chain` | `@TenantScoped()` | platform: `contract.chain_trace`, `contract.contract_lineage`, contract registry tables, `metric.mc_dependency`; tenant: live counts via `progression.*` + sample rows via `FactReader` for `fact.so_*`/`co_*`/`ms_*` |
| Audit log | `GET /api/t/metrics/{uid}/inspector/audit` | `@TenantScoped()` (with platform-only filter for cross-tenant changes) | DevHub MCP (`change_record`, `activity_log`) + `contract.contract_release_note` |
| Monitor pane | `GET /api/t/metrics/{uid}/inspector/monitor` | `@TenantScoped()` | platform: `metric.readiness_ledger`, `metric.mc_dependency`; tenant: `progression.metric_evaluation`, `progression.metric_run`, `progression.metric_snapshot_index` |
| Semantic checks | `GET /api/t/metrics/{uid}/inspector/semantics` | `@TenantScoped()` | platform: `metric.metric_definition` (kind/code), `contract.chain_status` (break_summary_json), engine primitive registry |
| Cross-pivots | `GET /api/metrics/{uid}/inspector/cross-pivots` | `@PlatformOnly()` (no tenant data) | platform: `contract.contract_lineage`, `contract.cc_field_mapping`, `contract.observation_field_map`, source catalog |

**Two stores, never joined:**

- **Platform DB (single connection):** `contract.metric_contract`, `contract.chain_status`, `contract.chain_trace`, `contract.contract_lineage`, `contract.observation_field_map`, `contract.cc_field_mapping`, `metric.metric_definition`, `metric.readiness_ledger`, `metric.mc_dependency`, `tenant.contract_binding`, `runtime.reader`, `runtime.reader_flavor`, `source.*`.
- **Tenant DB (per-tenant connection):** `progression.admission`, `progression.canonical_evaluation`, `progression.metric_evaluation`, `progression.metric_snapshot_index`, `progression.metric_run`, `evidence.evidence_object`, `evidence.lineage_object`, `fact.so_*`, `fact.co_*`, `fact.ms_*` (via `FactReader`).

**Tenant selector:** every `@TenantScoped()` endpoint reads the tenant slug from the `x-tenant-id` header (the SoT post-prior-fix; DTO body fields no longer carry tenantId). Cross-tenant pivot endpoints are `@PlatformOnly()` and require admin role.

**Fail-closed-per-section, not fail-closed-per-page:** every section returns a structured response of shape `{ state: 'ok' | 'unavailable' | 'broken', reason_code?: string, evidence?: object, payload?: object }`. A missing layer (e.g. `fact.co_*` table not provisioned for the tenant) yields `state: 'unavailable'` with a `reason_code` for that section only — the rest of the page renders. A 404 on the whole page is reserved for a metric_definition_id that doesn't exist; everything else degrades section-by-section.

**Read budget:** the chain-spine drilldown is the heaviest section (worst case: 6 layers × 1–5 sample rows × per-tenant per-version metadata). Per-section endpoints let bc-admin lazy-load: render Header + Tenant pivot first, fetch heavier sections on tab/expand interaction. ADR doesn't lock the loading order — that's an Inspector implementation-ADR concern (see Out of Scope).

### D-5 — Cross-cutting trust invariant: chain-complete ⇒ inspectable

Every metric whose `chain_status.chain_verdict = 'complete'` MUST be navigable from the Inspector and surface non-empty data at every section. A chain-complete metric that cannot render in the Inspector is a contradiction; the chain status rolls up to `'broken'` per existing rules (or `'partial'` if other variables remain green), and `chain_status.break_summary_json.reason_code = 'inspector_unreachable'` carries the cause. No new verdict enum value is introduced; the Chain Completeness chapter's four-verdict taxonomy stays intact.

> **Dependency on D387 (DEC-ebb3cd) — Evidence and Lineage Write Semantics.** The Inspector reads `proof_status` and surfaces `degraded` as a non-throwing per-section state. The section remains renderable, but degraded proof is not green: a snapshot whose evidence or lineage write failed cannot contribute to `chain_verdict='complete'` and rolls up to `'partial'` with `reason_code='proof_degraded'` per D387.

Practical effect:

- A new metric class that the Inspector doesn't yet know how to render cannot have its MCs go chain-complete until the Inspector handles it.
- A Inspector regression that breaks a section for a metric class downgrades every chain-complete MC of that class until the regression is fixed.
- Trust isn't claimed by the chain-status table alone; trust is claimed by the chain-status + Inspector together. The chain says "structurally sound"; the Inspector says "and here's what's flowing."

This is the strongest of the five decisions because it makes the Inspector unbypassable. Without it, the Inspector becomes another debug page that gets out of sync with reality. With it, every claim of metric correctness flows through the same surface.

## Implementation tracking

Five tasks, one per stage. Each is filed in DevHub linked to this ADR. Sequencing:

1. **Stage 1 — temporality_kind axis + authoring gate.** Schema migration on `contract.metric_definition`, a refusal-gate in the metric-contract authoring service, the gate at activation. ~1–2 sessions. Required before any other work.
2. **Stage 2 — Metric Inspector first cut.** bc-admin tab at the locked route (D-4) with the required sections, populated from existing data sources via the per-section API contract (D-4 backend read contract). Reads are split cleanly by store — platform-DB sources (`contract.chain_status`, `contract.chain_trace`, `contract.contract_lineage`, contract/metric/source registry tables, `metric.readiness_ledger`, `metric.mc_dependency`) and tenant-DB sources (`progression.*`, `evidence.*`, `fact.so_*`/`co_*`/`ms_*` via `FactReader`). One read path per scope, no accidental cross-store joins. Iterates beyond first cut, but the surface contract is locked.
3. **Stage 3 — Catalog backfill.** Tag every existing metric_definition with its temporality_kind. AI-assisted classification with maker-checker (bc-ai); manual review for edge cases. Surfaces every misaligned formula in the platform — that triage feeds Stages 4 and 5. ~2–3 sessions.
4. **Stage 4 — Stock + cumulative formula primitives.** Engine implementations of `BALANCE_AS_OF`, `CUMULATIVE_SUM`, `SNAPSHOT_DELTA`, `WEIGHTED_AVG_OVER`. Each is small individually; sequenced by demand from the Stage 3 triage. ~1 session per primitive.
5. **Stage 5 — Source pattern for historical stock reconstruction.** Either extend bc-sdg to emit dated snapshots of open-items sources, or extend the source pattern to ingest BSAD-class cleared-items sources + clearing-date replay. The only stage that's substantial across multiple repos. Scope locked when Stage 3 reveals the actual demand. Multi-week.

Stages 1, 2, 3 can run in parallel. Stage 4 starts when Stage 3 names a primitive that's needed by a real metric. Stage 5 is the longest and is gated by a separate ADR before scoping begins.

## Consequences

- **chain_status verdicts roll up the same way; reasons get richer.** No new enum values. `break_summary_json.reason_code = 'semantic_class_mismatch'` (D-2) and `'inspector_unreachable'` (D-5) carry the cause; the Chain Completeness chapter documents these as the *first* in a non-exhaustive set. Existing chain-complete MCs that fail the new gates will roll up to `broken` or `partial` per existing rules — that's the platform telling the truth, not a regression. Stage 3 backfill will produce real downgrades across the catalog.
- **Authoring gets stricter.** New MCs must declare both `temporality_code` and `temporality_kind` (and the two must be compatible per the table in D-1) and use a class-compatible primitive that is also engine-implemented (D-3 two-gate rule). Authors will need new docs in `bc-docs-v3/docs/onboarding/metric-registration.md` covering the four kinds and their compatibility with the existing 5D code. SOP gate updates accompany Stage 1.
- **Source-pattern demand surfaces from below.** Stage 3 will reveal how many metrics need stock primitives, which feeds Stage 5's scope. The demo cannot ship a stock metric like "Total AR Balance" honestly until Stage 5 lands; the truthful pivot in the meantime is to flow-class metrics only (DSO, billing volume, late-payment counts).
- **Operator authority shifts.** The Inspector becomes the canonical surface for "is this metric working." Past surfaces — chain-status dashboard, metric monitor page, debug logs — stay as supporting views. Anything claiming metric correctness without the Inspector is suspect.
- **D382 D-4 (chain_status governance compute) and D383 D-1 (drift inventory) gain a presentation layer.** They produce signals; the Inspector is where those signals reach a human. The two ADRs become more valuable when this one lands.
- **One ADR can't fix authoring practice alone.** A misuse-resistant catalog (Stage 3 + Stage 4 + the gate) is necessary; a culture of "look at the Inspector before you trust the number" is the human side. Both have to land. This ADR locks the structural side.

## Out of scope (separate ADRs)

- **Stage 5 source-pattern design.** Whether sandbox1 (and future tenants) source historical stock via dated snapshots or via base + delta + clearing-date replay is a separate decision. Both approaches are compatible with `BALANCE_AS_OF`; the choice has implications for connector design, throughput, and source-system load that deserve their own analysis.
- **Inspector implementation details.** This ADR locks the surface contract (must exist, must be first-class, must do the seven things in D-4). The implementation can land iteratively. A focused implementation ADR will cover URL structure beyond the root, state-management approach, drilldown loading strategy, etc.
- **Action / Intervention parallel.** The same audit pattern likely applies to interventions (action_object) — flow vs stock semantics, action-class temporality, intervention inspector. Out of scope here; the principles transfer when intervention chain matures.
- **Backfill strategy for the metric catalog.** Stage 3 mentions AI-assisted classification with maker-checker review. The mechanics (which AI agent, what prompts, what review SLA, how disagreements escalate) are a Stage-3 internal design decision, captured in the Stage 3 task plan rather than here.

## Tracking

This ADR is the gate. While it sits at `proposed`:

- No code lands for any of the five stages.
- Five DevHub tasks (one per stage) are filed in `parked` state, linked to this ADR's UID.
- The tasks become `planned` only when the ADR flips to `decided` and the user explicitly authorizes per stage.

Once `decided`:

- Stage 1 task moves to `now`.
- Stages 2 and 3 tasks move to `next` (parallelizable with Stage 1).
- Stages 4 and 5 stay `later` until upstream stages reveal demand and scope.

Reversal path: if the temporality_kind taxonomy is wrong on review (e.g. four kinds is too few; five is the right count), this ADR is set to `reversed` and a successor ADR records the corrected taxonomy. Tasks remain as design-exploration record.

## Incident evidence

(Historical — not living state. Quoted to anchor the lesson, not the numbers.)

> **Date:** 2026-04-28
> **Session:** SES-9c9206 (preceding the SES-a9ab9c ADR-drafting session)
> **Tenant:** sandbox1 (demo)
> **What was observed:** After a long chain-build arc landed structurally sound (admission counts, canonical evaluations, fact tables, fiscal_period stamping all reconciled), the metric `mc__total_ar_balance` was clicked on the monitor page. The displayed value was a large number labeled "Total AR Balance · FY2025-26/P12 · company_code=1000". A finance-domain reading of the label expects an end-of-period AR balance. The value was actually `SUM(receivable_hdr_amount) GROUP BY fiscal_period` over the open-items source filtered to invoices still in BSID at extraction time — billing volume per posting-month with a still-open filter, not a balance. Identical formula primitive (`SUM`) is correct for "Total Sales (Mar 2026)" (a flow) and incorrect for "Total AR Balance · Mar 2026" (a stock); the platform had no axis to distinguish them.
>
> **Why no audit caught it:** The `metric_contract.formula` text did not differ between the two semantic classes. `chain_status` reported `complete`. The Metric Catalog and the Monitor page both displayed the value without a class assertion. Past chain-visibility surfaces showed verdict states, not what was actually flowing through the chain to a literal source row for a real tenant.
>
> **Direct user quote:** "It is going insane. We are doing mechanical corrections one after another. Look at the name of the metric and tell me what we are showing making any sense for user?" / "These mishaps shake my confidence further down."

This evidence motivates the ADR. Stages 1–5 describe the structural fixes; the Inspector (D-4) is the surface that prevents this exact phenotype from recurring silently — a class mismatch becomes visible in the Semantic Checks section before the user has to read the rendered value with domain knowledge.

## Review history

| Date | Reviewer | Outcome |
|---|---|---|
| 2026-04-28 | Codex (P1+P2+P3 review) | 7 items raised; all addressed in this revision per user direction. P1.1 schema target corrected to `metric.metric_definition`. P1.2 chose option (b) — encode reason via `chain_status.break_summary_json.reason_code`, leave the 4-verdict enum intact. P1.3 added explicit per-section backend read contract in D-4. P2.1 placed Inspector as a tab under existing `/catalog/metrics/definition/:id` route family. P2.2 made platform vs tenant DB split explicit in D-4 + Stage 2. P2.3 added two-gate activation rule (allowed-by-class AND engine-implemented). P2.4 added explicit `temporality_kind` ↔ `temporality_code` compatibility table; the two columns coexist, neither replaces the other. P3 moved live counts/dates into this Incident evidence block; durable sections describe shape, not numerals. |
| 2026-04-28 | Audit follow-up (`reports/platform-code-doc-gap-report.md` GAP-001/GAP-002) | Added D-5 dependency block referencing **D387 (DEC-ebb3cd)** — Evidence and Lineage Write Semantics. D387 introduces `proof_status` per authoritative object and `reason_code = 'proof_degraded'` so a silently-failed evidence/lineage write cannot contribute to `chain_verdict = 'complete'`. Closes the silent-failure mode under D-5. No structural change to D386's other decisions. |
| 2026-04-28 | User verdict pass (Q1–Q6) | Q4 amendment: rewrote the D-5 dependency block with explicit non-throwing-vs-not-green distinction. The Inspector section remains renderable on degraded proof (no hard-fail, no 404), but degraded proof is **not** green — it cannot contribute to `chain_verdict='complete'` and rolls up to `'partial'` with `reason_code='proof_degraded'`. Q5 flip: status `proposed` → `decided` after Q4 wording landed. D386 is decided as of this entry. Q6 sequencing: strict-serial — D386 Stage 1 (TSK-9a0d7b) runs before D387 Stage 1; both Stage 1 tasks remain `parked` until explicit user authorization. |
