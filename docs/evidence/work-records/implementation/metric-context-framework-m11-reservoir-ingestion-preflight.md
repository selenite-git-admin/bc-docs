---
uid: metric-context-framework-m11-reservoir-ingestion-preflight
title: MCF M11 Reservoir Ingestion Preflight
description: Docs-only preflight framing the M11 Reservoir Ingestion gate per build plan §M11 + addendum §2.3 + §3.5. M11 ships the candidate-intake path that routes operator-vetted metric proposals from 3 reservoirs (Mongo bc_seed.seed_metrics + Postgres carve-out metric.metric_definition/metric_knowledge + operator-direct submissions) into a panel-ready intake queue with full reservoir provenance for M5 mapr binding. Enforces hard guardrails — legacy co_bindings strip (L3 lock + addendum guardrail #3), single-ingestion-service enforcement, confidence + provenance filtering (v1 high-confidence + APQC subset per addendum §3.5). Outputs panel-ready candidates with reservoir_name + reservoir_entry_id + reservoir_provenance_source_json + reservoir_confidence_band fields that M12 panel will copy into the mcf.metric_authoring_panel_run row at panel-open time. Recommendation M11-B (single mcf-owned mcf.metric_authoring_intake_queue durable table) — auditable per Invariant V, replayable, FK-able from M12, mirrors M9/M10 single-table substrate pattern. 8 operator decisions enumerated. Docs-only. No bc-core edits. No DDL. No Mongo connection attempts. No data writes. No M12/M13/M14+ work.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m11-reservoir-ingestion-preflight
---

# MCF M11 Reservoir Ingestion Preflight

## 1. Scope and grounding

Frame the M11 Reservoir Ingestion gate per build plan §M11. M11 is the first gate that produces **content flow** into the MCF substrate — it routes vetted candidate metric proposals from upstream reservoirs into the panel-ready intake queue that M12 will consume.

This is **docs-only preflight**. No DBCP. No DDL. No bc-core edits. No Mongo connection attempts. No M12/M13/M14+ work.

### 1.1 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ read-only |
| No DDL applied or drafted | ✓ |
| No Mongo connection attempts | ✓ |
| No real MCF metric contracts | ✓ substrate empty post-M10 apply |
| No fixture / result rows | ✓ M9 + M10 substrates dormant |
| No M12 / M13 / M14+ work | ✓ downstream gates |
| No BCF data touches | ✓ |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

### 1.2 Source documents (referenced from prior context — not re-read here)

- ADR DEC-c3e57f / D422 (MCF M1 foundational)
- MCF build plan §M11 (scope: 3 reservoirs + co_bindings strip + confidence filter + intake queue; T-shirt M; primary risk: co_bindings strip bypass)
- MCF addendum §2.3 (reservoir taxonomy) + §3.5 (confidence + APQC filter discipline) + guardrail #3 (co_bindings L3 lock)
- M5 DBCP (`bc-docs-v3 00435c0`) §6 — `mcf.metric_authoring_panel_run` has 4 reservoir-provenance fields (`reservoir_name` + `reservoir_entry_id` + `reservoir_provenance_source_json` + `reservoir_confidence_band`) with all-or-none CHECK enforced; M12 panel populates these at panel-open time per addendum guardrail #6
- M5 apply closeout (`bc-docs-v3 7800437`) — M5 substrate live; mapr table empty
- M10 apply closeout (`bc-docs-v3 d70f863`) — substrate chain M2→M10 closed; 16 mcf.* tables; all empty

---

## 2. Current live substrate state

After bc-core `67124e5` + bc-docs-v3 `d70f863`:

| | |
|---|---|
| bc-core main | `67124e5` (M10 evidence merged) |
| bc-docs-v3 main | `d70f863` (M10 apply closeout) |
| `mcf.*` tables | **16 present, all 0 rows** (10 pre-M5 + 4 M5 + 1 M9 + 1 M10) |
| M2→M10 services | live (M3 triggers + M4 cert writer + M5 panel substrate dormant + M7/M8 hash services + M9 fixture engine + M10 verifier engine) |
| M5 mapr provenance fields | `reservoir_name`, `reservoir_entry_id`, `reservoir_provenance_source_json`, `reservoir_confidence_band` — all live; all-or-none CHECK enforced; **nullable** (M12 panel populates when reservoir-attributed) |
| `bc_seed.seed_metrics` (Mongo) | external reservoir; not yet read by any MCF code |
| `metric.metric_definition` + `metric.metric_knowledge` (Postgres carve-out) | external reservoir tables; addendum-defined; not yet read by MCF code |
| BCF | untouched (24 panel + 1 rejection log) |

---

## 3. Why M11 is next

| Reason | Detail |
|---|---|
| **M12 panel needs candidates to author against** | Without ingestion, the panel has nothing to draft fixtures + propose MC versions against; M12 implementation would be vacuous |
| **Substrate chain M2→M10 is complete** | Foundation spine done; M11 is the first content-flow gate (substrate → content) |
| **Build-plan-recommended sequence** | M11 → M12 → M13 per the operator's reasoning + build plan ordering (M11 depends only on M5 which is live) |
| **No fixture/result dependency** | M11 doesn't touch M9/M10 substrates — it feeds the panel intake queue, which is independent of fixture/verifier work |
| **T-shirt size M** | Smaller than M9/M10 L; substrate-side likely one new table + ingestion service (single PR feasible) |

---

## 4. M11 ownership boundary

### 4.1 M11 MUST own

| # | Deliverable |
|---|---|
| 1 | Intake-queue substrate (per recommended M11-B — `mcf.metric_authoring_intake_queue` table; see §8) |
| 2 | `ReservoirIngestionService` (orchestrator + per-source adapters); single ingestion path |
| 3 | Mongo reader for `bc_seed.seed_metrics` (or reuse existing bc-core Mongo client per D-M11-2) |
| 4 | Postgres reader for `metric.metric_definition` + `metric.metric_knowledge` carve-out |
| 5 | Operator-direct submission interface (REST endpoint OR CLI script — per D-M11-4) |
| 6 | Candidate normalization — per-reservoir adapter produces a normalized `IntakeCandidate` payload with reservoir provenance + confidence band + APQC subset metadata |
| 7 | `co_bindings` strip enforcement (per addendum guardrail #3 — L3 lock); substrate-level rejection AND service-level strip (defense in depth per D-M11-5) |
| 8 | Confidence-band filter (v1 thresholds per D-M11-6) |
| 9 | APQC subset filter (per D-M11-7) |
| 10 | Idempotency / deduplication (per D-M11-8) |
| 11 | Substrate DDL + Drizzle schema (if M11-B/C); dry-run + post-apply verifier scripts |
| 12 | Reservoir-provenance handoff to M12 — intake-queue row carries provenance fields that M12 copies into `mcf.metric_authoring_panel_run` at panel-open time |

### 4.2 M11 MUST NOT own

| # | Out-of-scope | Belongs to |
|---|---|---|
| 1 | Panel authoring / three-model consensus / fixture proposal | **M12** Metric Authoring Panel |
| 2 | Operator-confirm flow / cert event emission | **M14** publication path |
| 3 | PE-MC evaluation | **M13** |
| 4 | Verifier execution | **M10** (already live) |
| 5 | Fixture body authoring | **M12** |
| 6 | Real MC versions written to `mcf.metric_contract` | gated on M12+M14 |
| 7 | Real verification results | gated on M9+M10+M12+operator runs |
| 8 | BCF concept enrichment | NEVER in MCF gates |
| 9 | Mongo schema changes to `bc_seed.seed_metrics` | external reservoir |
| 10 | Postgres carve-out schema changes to `metric.metric_definition` | external reservoir |
| 11 | Confidence-band re-grading after ingestion | downstream M12 panel decides; M11 just records what the source asserted |

---

## 5. Reservoir source inventory

### 5.1 Source 1 — Mongo `bc_seed.seed_metrics`

Per addendum §2.3:
- Source: MongoDB collection `bc_seed.seed_metrics` (existing; populated outside MCF arc)
- Format: per-document metric definition with name + formula prose + APQC linkage + confidence indicators
- Access: requires Mongo client connection (operator decision per D-M11-2 — reuse existing bc-core Mongo client or new dedicated reader)
- Volume: large catalog (operator-managed; M11 doesn't import all; filters via confidence + APQC subset)

### 5.2 Source 2 — Postgres carve-out `metric.metric_definition` + `metric.metric_knowledge`

Per addendum §2.3:
- Source: bc-core's existing Postgres `metric` schema (pre-MCF legacy substrate)
- Tables: `metric.metric_definition` (canonical metric authoring records) + `metric.metric_knowledge` (auxiliary documentation/context)
- Access: same DB connection as MCF (bc_platform_dev)
- **Carries `co_bindings` field** — legacy data; M11 MUST strip this on ingestion (addendum guardrail #3 + L3 lock)
- Volume: ~hundreds of entries per the current bc-core state

### 5.3 Source 3 — Operator-direct submissions

Per addendum §2.3:
- Source: operator-authored metric proposals not in any reservoir
- Format: structured submission with same `IntakeCandidate` shape as adapter outputs (i.e. normalized via the same code path)
- Access: REST endpoint vs CLI script vs panel-side direct write (per D-M11-4)
- Volume: small; one-off operator proposals
- Confidence: operator self-asserts; subject to the same filter discipline as adapter-sourced candidates

### 5.4 What all 3 sources share (normalized output)

Regardless of source, every ingested candidate becomes a normalized `IntakeCandidate` carrying:
- `candidate_name` (proposed MC name)
- `candidate_description_text` (prose)
- `reservoir_name` (`seed_metrics` / `metric_definition` / `operator_direct`)
- `reservoir_entry_id` (source-specific identifier)
- `reservoir_provenance_source_json` (full source payload + ingestion metadata)
- `reservoir_confidence_band` (`high` / `medium` / `low` — source-asserted)
- `apqc_subset_classification_text` (APQC taxonomy assignment if applicable)
- `co_bindings_stripped_flag` (true if source carried co_bindings; substrate-level enforcement)
- (substrate-decided status fields — see §8)

These map 1:1 to M5 mapr reservoir-provenance fields when M12 binds a panel run to an intake-queue row.

---

## 6. Candidate normalization and provenance

### 6.1 IntakeCandidate shape (target normalized form)

```typescript
interface IntakeCandidate {
  // Source-agnostic identity
  candidate_name: string;
  candidate_description_text: string;

  // Reservoir provenance (maps 1:1 to M5 mapr.reservoir_* fields at panel-open time)
  reservoir_name: 'seed_metrics' | 'metric_definition' | 'operator_direct';
  reservoir_entry_id: string;       // source-specific (Mongo _id, Postgres metric_definition_id, operator submission uid)
  reservoir_provenance_source_json: Record<string, unknown>; // full source payload + ingestion metadata
  reservoir_confidence_band: 'high' | 'medium' | 'low';

  // Classification + filter discipline
  apqc_subset_classification_text: string | null; // APQC taxonomy entry if matched

  // Guardrail compliance
  co_bindings_stripped_flag: boolean;  // true if source had co_bindings (substrate-level CHECK enforces strip)
}
```

### 6.2 Handoff to M12 panel

M11 writes intake-queue rows; M12 panel reads them when opening a panel run. M12 then **copies** the reservoir-provenance fields into the `mcf.metric_authoring_panel_run` row per addendum guardrail #6 + M5 §6 NF1 all-or-none CHECK enforcement.

**M11 does NOT write to `mcf.metric_authoring_panel_run`.** M11's substrate is intake-queue only; M12 owns the mapr write path.

### 6.3 Confidence + APQC filter discipline (per addendum §3.5)

- **Confidence band filter** — v1 defaults TBD per D-M11-6 (recommendation: `high` only for the first batch; expand to `high+medium` after operator validation)
- **APQC subset filter** — restricts the candidate population to a specific APQC taxonomy subset (per D-M11-7); narrows the first-cohort scope so the panel sees a tractable initial set
- Both filters apply at INGESTION TIME, not at panel-open time — rejected candidates never reach the intake queue; substrate stays clean

---

## 7. Guardrails and forbidden inputs

### 7.1 Hard guardrail: `co_bindings` strip (per addendum guardrail #3 + L3 lock)

Per build plan §M11 primary risk: *"`co_bindings` stripping bypass — if any code path ingests without going through M11, legacy fragments leak. Mitigation: enforce single ingestion service; reject direct intake-queue writes from any other path."*

**Three enforcement layers** (defense in depth per D-M11-5):
1. **Substrate-level JSONB CHECK** on the intake-queue row's normalized payload — rejects rows where any field still contains the `co_bindings` key
2. **Service-level strip + assert** — adapter strips `co_bindings` before constructing the IntakeCandidate; final assertion that `co_bindings_stripped_flag` matches actual strip outcome
3. **Single-ingestion-service convention** — only `ReservoirIngestionService` may INSERT into the intake-queue table; no other code path admitted (enforced by service-side discipline; substrate-level GRANT restriction is operational, not in M11 substrate scope)

### 7.2 Hard guardrail: single ingestion service

All 3 source paths route through ONE `ReservoirIngestionService` — no direct writes to the intake-queue from other code paths. This guarantees:
- co_bindings strip is universally applied
- Confidence + APQC filters are universally applied
- Provenance fields are populated for every row (no NULL provenance — substrate CHECK enforces if M11-B substrate chosen)
- Idempotency / dedup is universally enforced

### 7.3 Soft guardrails (v1 filter discipline)

- Confidence-band filter (v1 default per D-M11-6)
- APQC subset filter (v1 default per D-M11-7)
- Both relaxable in future amendments as operator validation progresses

### 7.4 Forbidden inputs

| Forbidden | Why |
|---|---|
| Any payload carrying `co_bindings` | L3 lock + addendum guardrail #3 |
| Confidence-band outside the v1 enum | substrate CHECK enforces |
| Reservoir-provenance fields all-NULL | addendum guardrail #6 + M5 all-or-none pattern |
| Direct INSERTs into intake-queue from non-`ReservoirIngestionService` paths | single-service discipline |

---

## 8. Intake substrate design options

### 8.1 M11-A — no new substrate; service emits candidate payloads to M12 only

ReservoirIngestionService produces in-memory `IntakeCandidate` objects; M12 panel pulls candidates directly via service call (no durable queue).

**Pros:** zero DDL; minimal substrate footprint.

**Cons:**
- **Violates Invariant V** (evidence emitted, not inferred) — no audit trail of what was ingested
- No replay path — if a panel run fails, the candidate must be re-fetched from the reservoir (which may have moved)
- Confidence-filter rejections leave no record — operators can't audit why a candidate was rejected
- M12 panel can't FK against ingestion provenance (no row to reference)
- No idempotency / dedup substrate — service-side memory only

**Rejected.** Foundational Invariant V violation.

### 8.2 M11-B — single mcf-owned `mcf.metric_authoring_intake_queue` durable table (RECOMMENDED per §11)

New table `mcf.metric_authoring_intake_queue`:
- 1 PK (`intake_queue_uid uuid`)
- 1 UNIQUE on `(reservoir_name, reservoir_entry_id)` for dedup / idempotency
- 4 reservoir-provenance columns matching M5 mapr shape (so M12 can copy by name)
- 1 JSONB column carrying full normalized IntakeCandidate payload
- 1 status enum (`pending` / `consumed_by_panel` / `rejected` / `superseded`)
- Audit columns (`ingested_at`, `ingested_by_name`)
- Substrate-level CHECK enforcing `co_bindings` strip (rejects rows where the JSONB payload contains the key)
- ~10-12 columns total

**Pros:**
- Auditable per Invariant V
- Replayable (M12 panel can re-consume a `pending` row if its first attempt failed)
- Confidence-filter rejections recorded with `rejected` status + reason
- M12 panel can FK against `intake_queue_uid` for provenance traceability
- Substrate-side idempotency via UNIQUE
- Mirrors established M9/M10 single-table substrate pattern

**Cons:** one new table (small DDL surface; ~10-12 cols; ~7 constraints; ~3 indexes)

**Recommended.**

### 8.3 M11-C — source-specific staging tables

Three tables: `mcf.intake_seed_metrics_staging` + `mcf.intake_metric_definition_staging` + `mcf.intake_operator_direct_staging`.

**Pros:** per-source schema can be source-specific; clearer source provenance.

**Cons:**
- 3 tables instead of 1
- Complicates query patterns (M12 has to UNION across 3)
- Redundant with M11-B + normalized candidate shape (normalized shape already carries `reservoir_name` discriminator)
- Per-source schema variation is a fix-the-cause-at-adapter problem, not a substrate problem
- Scope creep

**Defer.** Source-specific tables can be added in a future amendment if operator queries demand per-source schemas. v1 normalizes everything into a single table.

---

## 9. Service / adapter design options

### 9.1 Single service with 3 source methods (RECOMMENDED for v1 simplicity)

```typescript
class ReservoirIngestionService {
  async ingestFromSeedMetrics(deps, filter): Promise<IngestSummary>
  async ingestFromMetricDefinition(deps, filter): Promise<IngestSummary>
  async ingestOperatorDirectSubmission(deps, submission): Promise<IngestSummary>
}
```

**Pros:** simple class shape; one entry point for the single-ingestion-service guardrail; easier to test.

**Cons:** if reservoir-specific logic grows, the class will need splitting.

### 9.2 Coordinator + 3 adapter classes (more flexible)

```typescript
class ReservoirIngestionCoordinator {
  constructor(private readonly seedAdapter, private readonly metricDefAdapter, private readonly operatorAdapter) {}
  async ingestAll(deps): Promise<IngestSummary>
}
class SeedMetricsAdapter { read(): IntakeCandidate[] }
class MetricDefinitionAdapter { read(): IntakeCandidate[] }
class OperatorDirectAdapter { accept(submission): IntakeCandidate }
```

**Pros:** per-adapter testability; easier to add a 4th source later (e.g. a new reservoir).

**Cons:** more code surface for v1; 4 classes vs 1.

**Recommendation per D-M11-3:** **single service with 3 methods for v1** (simplicity); refactor to coordinator+adapters if a 4th source emerges.

---

## 10. Idempotency and deduplication

### 10.1 Per-(reservoir_name, reservoir_entry_id) UNIQUE — RECOMMENDED

UNIQUE constraint on `(reservoir_name, reservoir_entry_id)` in the intake-queue table — re-ingesting the same source row raises `unique_violation`; service catches + returns existing row (idempotent retry).

Same pattern as M10's `uq_msvr_fixture_version_pkg_hash` idempotency design.

### 10.2 Content-hash dedup (alternative)

Hash the normalized IntakeCandidate payload; UNIQUE on hash. Catches semantic duplicates (same content from different sources or with cosmetic-only source changes).

**Trade-off:** more aggressive dedup; but reservoir-entry-id is the simpler + more auditable key for v1. Content-hash can be added later as a derived column.

### 10.3 Status-driven re-ingestion

If an intake-queue row's status is `rejected` or `superseded`, re-ingestion of the same `(reservoir_name, reservoir_entry_id)` MAY be admitted (writes a new row with a fresh `intake_queue_uid` and reason). Sub-decision per D-M11-8.

---

## 11. Recommendation

**M11-B** (single mcf-owned `mcf.metric_authoring_intake_queue` durable table) with **single ReservoirIngestionService** (3 source methods) per §8.2 + §9.1.

| Aspect | Decision |
|---|---|
| Substrate | 1 new table `mcf.metric_authoring_intake_queue` (~10-12 cols) |
| Constraints | ~7 (PK + 4 reservoir-provenance NOT NULL + status enum CHECK + 1 UNIQUE on (reservoir_name, reservoir_entry_id) + 1 JSONB-CHECK rejecting `co_bindings` key) |
| Indexes | ~3 (status / reservoir_name / ingested_at) |
| Service | `ReservoirIngestionService` (single class, 3 methods) |
| Adapters | inline within service for v1 |
| Mongo connection | reuse existing bc-core Mongo client per D-M11-2 (if one exists) |
| co_bindings enforcement | substrate JSONB CHECK + service-side strip + service-side assert (3 layers per D-M11-5) |
| Confidence-band v1 default | `high` only (per D-M11-6 recommendation; expand to `high+medium` after operator validation) |
| APQC subset v1 default | configurable via env var or service config; first-batch operator picks (per D-M11-7) |
| Idempotency key | `(reservoir_name, reservoir_entry_id)` UNIQUE per D-M11-8 |
| Operator-direct interface | CLI script for v1 (per D-M11-4 recommendation); REST endpoint deferred to M12 panel-side write path |

---

## 12. Risks and stop conditions

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-M11-1 | **`co_bindings` strip bypass** — direct writes to intake-queue from non-`ReservoirIngestionService` paths | Medium (per build plan §M11 primary risk) | 3-layer enforcement (substrate JSONB CHECK + service-side strip + service-side assert); GRANT restriction on production DB role as operational follow-up |
| R-M11-2 | **Mongo connection / availability** — bc-core may not have a live Mongo client; ingestion service can't proceed if Mongo is unreachable | Medium | Per D-M11-2 — reuse existing bc-core Mongo client OR new dedicated reader; either way, M11 impl PR includes connection-health check + graceful degradation (fall back to Postgres-only ingestion if Mongo unreachable) |
| R-M11-3 | **Confidence-band semantics drift** — source-asserted confidence may not match operator's actual confidence | Low | M11 records what the source says; M12 panel re-grades during three-model consensus; no semantic drift at ingestion |
| R-M11-4 | **APQC subset filter over-restrictive** — first-cohort filter excludes important metrics | Low | Operator-configurable per D-M11-7; relax in v2 |
| R-M11-5 | **Idempotency key under-discriminates** — same Mongo `_id` reused across collections or namespaces | Low | UNIQUE on `(reservoir_name, reservoir_entry_id)` discriminates by source; collisions only across reservoirs require operator review |
| R-M11-6 | **JSONB CHECK rejecting `co_bindings` performance** at scale | Low | JSONB key-presence check is cheap; intake-queue is bounded (hundreds of rows, not millions) |
| R-M11-7 | **Reservoir schema drift** — upstream `bc_seed.seed_metrics` or `metric.metric_definition` evolves | Medium | Per-adapter normalizer absorbs source-schema changes; service-side translation layer; M11 impl PR includes schema-snapshot test for each source |
| R-M11-8 | **Operator-direct submission abuse** — operator bypasses confidence filter via direct submission | Low (operator self-discipline) | All 3 sources go through the same filter; operator-direct still subject to `reservoir_confidence_band` declaration + APQC filter; CLI script for v1 caps the abuse surface |

### Stop conditions

The M11 implementation PR STOPS and re-frames if:
- Mongo client unavailable AND no fallback is acceptable to operator (D-M11-2 decision)
- §19.13 Q-style operator questions emerge mid-implementation that affect reservoir filter design
- bc_seed schema is undocumented enough that the seed adapter can't normalize reliably (escalates to a separate "reservoir schema audit" gate)

---

## 13. Operator decisions needed before M11 DBCP can open

| # | Decision |
|---|---|
| **D-M11-1** | ACCEPT M11-B (single `mcf.metric_authoring_intake_queue` durable table) over M11-A (no substrate — Invariant-V-rejected) and M11-C (source-specific staging — deferred) |
| **D-M11-2** | Mongo client — reuse existing bc-core Mongo client (if one exists; needs inventory check at DBCP time) vs new dedicated reader |
| **D-M11-3** | Per-reservoir adapter shape — single `ReservoirIngestionService` with 3 source methods (recommended for v1 simplicity) vs coordinator + 3 separate adapter classes |
| **D-M11-4** | Operator-direct submission interface — CLI script (recommended for v1) vs REST endpoint vs panel-side direct write (defer to M12) |
| **D-M11-5** | `co_bindings` strip enforcement — 3-layer (substrate JSONB CHECK + service-side strip + service-side assert) — recommended; vs lighter 2-layer or service-only |
| **D-M11-6** | Confidence-band v1 default — `high` only (recommended) vs `high+medium` vs operator-configurable threshold |
| **D-M11-7** | APQC subset filter — single fixed subset for v1 vs configurable via env/config vs filter-from-table (where the filter list lives in a config table) |
| **D-M11-8** | Idempotency key — `(reservoir_name, reservoir_entry_id)` UNIQUE (recommended) vs content-hash UNIQUE vs both |

---

## 14. Recommended next gate

Combined M11 DBCP per the established pattern (substrate + ingestion service in one document).

**Suggested filename:** `metric-context-framework-m11-reservoir-ingestion-dbcp.md`

**Suggested PR title for impl PR (NO DB APPLY):** `feat(mcf): M11 Reservoir Ingestion — intake queue substrate + ingestion service (NO DB APPLY)`

Sequencing per established pattern:
1. M11 DBCP → operator review → operator-accepted decisions D-M11-1..D-M11-8
2. M11 implementation PR (NO DB APPLY)
3. M11 small-DDL apply gate (separate operator-authorized session)
4. M11 evidence PR + bc-docs-v3 closeout

**Parallel-eligible with M12 preflight** (M12 depends on M11 substrate for the intake-queue table being defined; M12 preflight design can proceed in parallel with M11 impl PR once M11 DBCP lands).

---

## 15. What stays closed

| | |
|---|---|
| M11 DBCP | not opened by this preflight |
| M11 impl PR | pending DBCP |
| M11 DDL apply | pending impl PR |
| M11 evidence PR | pending apply |
| **M12 Metric Authoring Panel implementation** | CLOSED — gated on M11 + M9 + M10 + M5 + M7 |
| **M13 PE-MC evaluator** | CLOSED — gated on M11 + M12 + M10 |
| **M14+** | CLOSED |
| **Real MCF metric contracts** | CLOSED — substrate stays empty pending M11+M12+operator runs |
| **Real fixtures + verification results** | CLOSED |
| **BCF data changes** | CLOSED — 24 BCF panel + 1 rejection log untouched throughout MCF arc |
| **Mongo schema changes** | NEVER — external reservoir |
| **Postgres `metric.*` carve-out schema changes** | NEVER — external reservoir |
| **M11-C source-specific staging tables** | DEFERRED |
| **M11-A no-substrate option** | REJECTED (Invariant V violation) |
| **Confidence-band re-grading at ingestion** | CLOSED — M12 panel re-grades; M11 records source-asserted band |
| **REST endpoint for operator-direct submission** | DEFERRED to M12 panel-side write path (per D-M11-4 recommendation) |
| **Reservoir schema audit** | OPEN — may emerge as a separate gate if bc_seed schema is under-documented |
