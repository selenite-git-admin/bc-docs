---
uid: DEC-e7b7b3
title: "MLS State Substrate — current ledger, append-only event log, declarative trigger binding, queue-based recorder"
description: "Locks the platform substrate that turns Metric Lifecycle States from documentation into a queryable runtime artifact: metric.mls_state (current verdict per state × subject), metric.mls_state_event (append-only history), metric.mls_trigger_binding (declarative event→state mapping with subject/value/code derivation), MlsStateRecorderService (hybrid record/recordImmediate — queue-based for hot paths, sync for governance acts). MLS is a read model layered on per-domain SSOTs, not a competing source of truth. Includes monotonicity rule, polymorphic subject_kind, \"missing artifact\" as a legitimate verdict, enumerateSubjects-based reconcile, and PII-bounded evidence."
status: decided
date: 2026-05-03T05:56:33.913Z
project: bc-core
domain: governance
subdomain: metric-lifecycle-states
focus: state-substrate
---

# MLS State Substrate — current ledger, append-only event log, declarative trigger binding, queue-based recorder

## Context

DEC-c9e623 (D389, MLS Framework — renamed from OLS on 2026-05-03) defined 25 numbered states and a 17-column ledger schema, but explicitly deferred the substrate decision: "the state ledger may live as documentation in a v3 chapter first, become a real platform table later when probe-write coverage warrants." That deferral is now the bottleneck. MLS state today lives scattered across artifacts (chain_status, progression rows, contract_binding, governance_state_code, evidence_object.proof_status, activity log, platform_inspection_audit_log). There is no consolidated view; Inspector synthesizes one by reading many sources, which is exactly the role overload the framework was created to eliminate. Without a substrate, Inspector cannot stop being a synthesizer; new probes have nowhere to write; cross-cutting questions ("show me all MLS rows that flipped red in the last hour for tenant X") have no surface that can answer them. This ADR closes that gap with the smallest substrate that can carry the framework — one current-state table, one event-log table, one wiring spec, one recorder service.

## Context

Sibling to DEC-c9e623 (D389, MLS Framework — renamed from OLS on 2026-05-03), DEC-9d7a5c (D390, MLS Failure Vocabulary), DEC-b8b825 (D391, MLS-14 Semantic Activation Gate). Closes the deferred substrate question.

The framework defined the 25 states and the columns that should describe each. It deferred the question of where state values actually live. Today they're scattered:

| Signal source | MLS row(s) | How read today |
|---|---|---|
| `contract.chain_status` | MLS-13 | direct query |
| `contract.chain_trace` | MLS-02/04/06/07/08/09 (via L-nodes) | direct query |
| `progression.admission.status` | MLS-21 | direct query |
| `progression.canonical_evaluation` | MLS-22 | direct query |
| `progression.metric_evaluation` | MLS-23 | direct query |
| `tenant.contract_binding` row presence | MLS-19 | de facto signal, no explicit verdict |
| schema-provisioner reconcile_result | MLS-20 | log line, not durable |
| `metric_contract_version.governance_state_code` | MLS-14 | direct query (no gate writes it today per DEC-b8b825) |
| `evidence_object.proof_status` | MLS-24 | direct query (D387) |
| `operations.activity_log` | every governance act | indirect; needs synthesis |
| `operations.platform_inspection_audit_log` | Inspector reads | indirect |

Inspector (DEC-f0e78e / D388) synthesizes a consolidated view by reading many sources — the role overload the framework was created to eliminate. Substrate ends the synthesis.

## Decisions

### D-1. Two tables — current ledger + append-only event log

Both tables live in the platform DB under the `metric` schema (neighbor to `metric.mls_failure_code` from DEC-9d7a5c).

#### `metric.mls_state` — current verdict per (state × subject)

One row per (mls_state_id, subject_key). Latest truth. Updated atomically by the recorder.

| Column | Type | Notes |
|---|---|---|
| `mls_state_id` | text | `MLS-01` … `MLS-25` |
| `mc_version_id` | uuid nullable | NULL for catalog/connector states (MLS-01, MLS-02) |
| `tenant_slug` | text nullable | NULL for Platform MLS (1–14); required for Tenant MLS (15–25) |
| `subject_kind` | text | `connector` / `source_field` / `mc_version` / `metric_definition` / `binding` / `snapshot` etc. |
| `subject_key` | text | **Deterministic identity** produced by the recorder via the trigger binding's `subject_key_template`. Examples: `mc_version:019d762a:1.0.0`, `binding:tenant=sandbox1:mc=mc__ar_dso:v=1.0.0`. Stable, debuggable, queryable. **Identity does NOT depend on jsonb canonicalization.** |
| `subject_ref` | jsonb | Inspection-only frozen reference. Not queried by content. |
| `current_value` | text | `green` / `red` / `yellow` / `unknown` (CHECK constraint) |
| `current_code` | text nullable | FK to `metric.mls_failure_code.code` when not green |
| `current_evidence_json` | jsonb nullable | Per registry's `evidence_schema` for `current_code`. **Metadata, refs, hashes, counts — NOT raw payloads** (see Evidence constraint below) |
| `last_observed_at` | timestamptz | The `observed_at` of the event that produced the current row. Used for monotonicity guard (D-3) |
| `last_transition_at` | timestamptz | When `current_value` last changed. May be earlier than `last_observed_at` if a re-observation confirmed the existing state |
| `last_event_id` | uuid | FK to most recent `mls_state_event.event_id` |
| `last_writer` | text | Service that wrote the latest event |
| `created_at` / `updated_at` | timestamptz | audit |

**Unique key:**

```
UNIQUE(mls_state_id,
       COALESCE(mc_version_id::text, ''),
       COALESCE(tenant_slug, ''),
       subject_kind,
       subject_key)
```

No `md5(jsonb)`. Identity is in `subject_key`; `subject_ref` is inspection only.

**Indexes:** `(tenant_slug, last_transition_at desc)`, `(mls_state_id, current_value)`, `(current_code)`.

#### `metric.mls_state_event` — append-only history

One row per state-change event. Never updated, never deleted. Latest event per (key) becomes the ledger's current row.

| Column | Type | Notes |
|---|---|---|
| `event_id` | uuid PK | |
| `mls_state_id` | text | |
| `mc_version_id` | uuid nullable | same key shape as ledger |
| `tenant_slug` | text nullable | |
| `subject_kind` | text | |
| `subject_key` | text | |
| `subject_ref` | jsonb | |
| `transition_from` | text nullable | `green` / `red` / `yellow` / `unknown`; **NULL on first event** for this subject (no special "(none)" sentinel) |
| `transition_to` | text | `green` / `red` / `yellow` / `unknown` |
| `code` | text nullable | failure code emitted (NULL if going green) |
| `evidence_json` | jsonb nullable | per registry's evidence_schema |
| `observed_at` | timestamptz | when the underlying signal happened |
| `source_event_kind` | text | `contract_activation` / `admission` / `chain_status_recompute` / `gate_refusal` / `drift_detected` / `nightly_reconcile` / `reconcile_drift` / `reconcile_insert` |
| `source_event_ref` | text | UID/ID of the source event (e.g., `admission_id`, `change_record_uid`) |
| `writer` | text | service that recorded the event |
| `recorded_at` | timestamptz default now() | wall clock of the OLS write |

**CHECK constraint:** `transition_from IN ('green','red','yellow','unknown') OR transition_from IS NULL`; `transition_to IN ('green','red','yellow','unknown')`.

**Indexes:** `(mls_state_id, observed_at desc)`, `(tenant_slug, observed_at desc)`, `(source_event_kind, observed_at desc)`. No FK to ledger — events are independent of the rolled-up state row.

**Why both tables (rather than view-over-events):** Inspector reads are read-heavy; latest-row-per-key SQL is expensive at scale. A separate ledger table is small (≤ 25 × MC-count × tenant-count rows in practice) and indexed for direct access. The event log is the audit trail and the cascade-replay source. Two-table cost is one extra write per recorder cycle — negligible.

### D-2. Declarative trigger binding — `metric.mls_trigger_binding`

The wiring from runtime event sources to MLS state writes is **a config table, not scattered code**. Adding a new state or a new event source is a row insert, not a code change in N emitters.

| Column | Type | Notes |
|---|---|---|
| `binding_id` | uuid PK | |
| `source_event_kind` | text | e.g., `admission` / `chain_status_recompute` / `contract_activation` / `gate_refusal` / `drift_detected` |
| `mls_state_id` | text | which MLS state this event affects |
| `subject_kind` | text | declares the artifact class the event maps to |
| `subject_key_template` | text | template the recorder evaluates against the source event payload to produce `subject_key`. E.g. `binding:tenant={tenant_slug}:mc={mc_id}:v={version_code}` |
| `subject_selector_json` | jsonb | optional bag of JSONPath/expressions for extracting structured subject fields when template alone is insufficient |
| `effect_kind` | text | `direct_write` / `recompute_via_probe` / `cascade_to_dependents` |
| `value_map_json` | jsonb | maps source-event values to MLS values. Example for chain_status: `{"complete":"green","partial":"yellow","broken":"red","unlinked":"red"}`. Required for `direct_write` |
| `code_map_json` | jsonb nullable | maps source-event reasons to registry codes. Example: `{"L4":"MLS-07.bf_unmapped_in_oc","L7":"MLS-02.source_field_not_in_catalog"}` |
| `probe_service` | text nullable | required for `recompute_via_probe` (e.g., `ChainStatusService.probe`) |
| `dependency_resolver_service` | text nullable | required for `cascade_to_dependents` — service that returns list of (subject_kind, subject_key) tuples to recompute |
| `cascade_to_state_ids` | text[] nullable | which downstream states get recomputed (subjects expanded by `dependency_resolver_service`) |
| `enabled` | boolean default true | switch-off without deleting the row |
| `governing_decision` | text | DEC-xxxxxx |
| `created_at` / `updated_at` | timestamptz | |

`cascade_to_state_ids` is `text[]` (not jsonb) because it is queryable ("which bindings cascade to MLS-19?") with a GIN index.

**Effect-kind semantics:**

- `direct_write` — source emitter knows the new verdict; recorder writes the event with the verdict it was given. Used for `admission` (status field is the verdict), `chain_status_recompute` (chain_verdict is the verdict)
- `recompute_via_probe` — recorder calls `probe_service` for the affected (state, subject), gets a verdict, writes the event. Used when the source event signals "something changed but I don't know the verdict"
- `cascade_to_dependents` — recorder, after writing the primary event, schedules recomputes for the listed downstream MLS states

Seed bindings ship with the implementation task; bindings are not enumerated in this ADR. What the ADR locks is the shape and the rule that bindings are config rows, not code branches.

### D-3. `MlsStateRecorderService` — queue-based, async, hybrid policy + monotonicity

Direct synchronous calls from runtime hot paths to the recorder are rejected: a Postgres hiccup on `mls_state` would block admission, evaluation, snapshot writes. MLS state-keeping is **best-effort** for runtime; runtime never waits on MLS.

The recorder runs as an in-process service with an in-memory queue + drain worker:

| Concern | Design |
|---|---|
| Queue | Lightweight in-memory FIFO (per-process). Emitters publish synchronously (constant-time push); recorder drains async |
| Drain cadence | Configurable; default tick every 250 ms or queue-depth threshold of 100 events |
| Backpressure | If queue depth exceeds high-water-mark (default 10,000), recorder logs `OPS.mls_recorder_queue_overflow` and starts dropping oldest events. Runtime continues unaffected |
| Persistence | None across process restart. Lost events leave the ledger stale; the next reconcile (D-5) catches them |
| Failure mode | If `mls_state` / `mls_state_event` writes fail, recorder logs `OPS.mls_recorder_write_failed` and continues processing. Runtime never blocked |
| Hybrid for governance acts | Governance acts (contract activation, gate refusal, decision recording) use `recordImmediate(event)` — synchronous call that bypasses the queue and writes directly. These paths can tolerate the latency and benefit from immediate consistency. Hot paths (admission, evaluation) use `record(event)` (queued) |

**Two recorder methods:**

- `record(event)` — queued, async, runtime-safe, at-most-once delivery (best-effort)
- `recordImmediate(tx?, event)` — synchronous; when `tx` is passed (same-DB governance acts), the recorder write joins the source act's transaction; without `tx` (cross-DB / external acts), synchronous best-effort with reconcile fallback (see D-8)

**Monotonicity rule (locked):** A `metric.mls_state` row may only be advanced by an event whose `observed_at >= last_observed_at`, **unless** the event was written by `recordImmediate` for governance repair (in which case the new value wins regardless of order).

Recorder enforcement (pseudocode):

```sql
UPDATE metric.mls_state
SET current_value = $new_value, ..., last_observed_at = $event.observed_at
WHERE mls_state_id = $1 AND ... AND subject_key = $5
  AND (last_observed_at <= $event.observed_at OR $is_immediate_repair = true)
```

If the UPDATE matches zero rows, the event is dropped from the ledger but **still written to `mls_state_event`** (the history retains it as out-of-order; queryable for forensic). Recorder logs `OPS.mls_event_out_of_order` for observability.

This closes the "old queued red overwrites newer green" failure mode. Governance repair via `recordImmediate` retains the authority to correct stale ledger rows.

**Same-value events:** If `transition_to == current_value`, the recorder updates `last_observed_at`, `last_event_id`, `last_writer`, and `current_evidence_json`, but **does NOT update `last_transition_at`**. The transition timestamp records the moment of value change; same-value events are re-observations, not transitions.

### D-4. Probe interface — unchanged from DEC-c9e623

Probe Services remain read-only as DEC-c9e623 D-5 locked. This ADR adds:

- The recorder may call any registered probe service via `effect_kind='recompute_via_probe'` — the call is read-only from the probe's perspective; the recorder writes the result
- Probes are exposed via a uniform interface `MlsProbeRegistry.probe(mls_state_id, subject_key)` — used by Inspector for ad-hoc reads and by the recorder for trigger bindings
- A probe failure (timeout, exception) results in an event with `transition_to='unknown'` and code `OPS.probe_unavailable` — never blocks the recorder

### D-5. Reconcile — enumerate expected subjects, probe, insert missing, correct stale

Because the recorder is best-effort, the ledger can drift from reality (lost events on restart, dropped events on overflow, missed source-event-kind bindings). A reconcile pass corrects this in **two phases**:

**Phase 1 — Discovery.** For each MLS state with a registered probe, call `MlsProbeRegistry.enumerateSubjects(mls_state_id, scope)` to obtain the **expected** set of (subject_kind, subject_key, mc_version_id?, tenant_slug?) tuples. Scope is configurable (per-tenant, per-MC-version, full).

**Phase 2 — Reconcile.** For each enumerated subject:
- If absent from ledger → call probe → write a reconcile event with `source_event_kind='reconcile_insert'` → ledger gains the row
- If present in ledger → call probe → if probe verdict differs from ledger value → write a reconcile event with `source_event_kind='reconcile_drift'` → ledger updated

The enumerator is per-MLS-state. Examples:

| MLS state | `enumerateSubjects` returns |
|---|---|
| MLS-13 | every `(mc_version_id)` from `metric_contract_version` where `governance_state_code IN ('active', 'review', 'approved')` |
| MLS-19 | cross-product of `tenant.tenants WHERE status_code='active'` × every active MC version |
| MLS-21 | every `(tenant_slug, mc_version_id)` with at least one `progression.admission` row in the last N hours |
| MLS-23 | every `(tenant_slug, mc_version_id)` with at least one `metric_snapshot_index` row |

**The enumerator is also the backfill entry point** (see Implementation tracking — initial substrate population task).

The reconcile pass surfaces `OPS.mls_ledger_drift_detected` (count of corrected rows) + `OPS.mls_ledger_orphans_detected` (count of inserts) for observability. Runs nightly alongside `NightlyReconcilerService` (DEC-95687d / D369).

### D-6. MLS as read model, not competing SSOT (load-bearing)

> **The MLS substrate is a read model + history surface for state, not a competing source of truth.** Where a per-domain SSOT exists, the SSOT wins; MLS reads from it via Probe Service and reconciles. The MLS ledger answers "what is the current MLS-keyed view of state across the platform"; per-domain SSOTs answer "what does the domain authoritatively know."

| MLS row | Source-of-truth | MLS substrate role |
|---|---|---|
| MLS-13 | `contract.chain_status` (DEC-bebaec) | read model + history; reconciled via `ChainStatusService.probe` |
| MLS-14 | `metric_contract_version.governance_state_code` (DEC-c9e623 + DEC-b8b825 gate) | read model + history; reconciled via `MlsActivationGateService.probe` |
| MLS-19 | `tenant.contract_binding` row presence (governance act records via `recordImmediate`) | read model + history |
| MLS-21/22/23 | `progression.admission` / `progression.canonical_evaluation` / `progression.metric_evaluation` | read model + history |
| MLS-24 | `evidence_object.proof_status` (D387) | read model + history |

If the ledger and SSOT disagree, the SSOT wins. Reconcile pass corrects the ledger from the SSOT, never the other way around. This is the rule that prevents future "which table wins?" drift.

**"Missing artifact" is a legitimate MLS verdict.** Where an upstream artifact (MD without MC, MC without binding, binding without snapshot) is expected to exist for the chain to complete, its absence is recorded as `current_value='red'` with code `MLS-NN.no_artifact_kind_for_parent` keyed at the parent's grain. The substrate represents non-existence as a positive state, not as a missing row. `subject_kind` may differ across rows for the same `mls_state_id` — the unique key already handles this. Examples: MLS-11 keys to `metric_definition` when no MC version exists, and to `mc_version` when one or more exist; MLS-19 keys to `(tenant, mc_version)` for "binding missing" with verdict red. The `enumerateSubjects` for upstream MLS states must walk the *expected* subject set (every MD, every (tenant, MD) tuple), not just artifacts that exist — this is what makes "missing" detectable.

### D-7. Migration of existing emitters — rule + examples

The migration rule:

> Every existing emitter that mutates a per-domain SSOT gains one call: `recordImmediate(tx, event)` if the mutation is a governance act in the same DB transaction; `record(event)` (queued) otherwise.

Two examples (full per-emitter list in Implementation tracking):

```typescript
// Hot path: admission accept (queued, best-effort)
await this.persistAcceptedAdmission(...);
this.mlsStateRecorder.record({
  source_event_kind: 'admission',
  source_event_ref: admittedRecordId,
  observed_at: new Date(),
  payload: { tenant_slug, mc_version_id, status: 'admitted' },
});

// Governance act: contract activation (immediate, transactional in same TX)
await this.db.transaction(async (tx) => {
  await this.versionRepo.updateGovernanceState(tx, mcId, vCode, 'active');
  await this.mlsStateRecorder.recordImmediate(tx, {
    source_event_kind: 'contract_activation',
    source_event_ref: changeRecordUid,
    observed_at: new Date(),
    payload: { mc_id: mcId, version_code: vCode, governance_state: 'active' },
  });
});
```

### D-8. Transactional clarification — same-DB only

`recordImmediate` is "transactional" only when the source emitter passes a transaction handle to the recorder and the OLS write happens in the same DB transaction. This applies to platform-DB governance acts (contract activation, gate refusal, decision recording).

Cross-DB acts (e.g., a tenant-DB event triggering an MLS write to platform DB) and external acts (e.g., S3 archive completion) use `recordImmediate` for **synchronous best-effort with visible failure + reconcile fallback** — not truly fail-closed. If the OLS write fails after the source act succeeds, the source act stays committed; recorder logs `OPS.mls_recorder_immediate_write_failed` and reconcile pass corrects on next cycle.

Same-DB acts get atomic guarantees; cross-DB / external acts get synchronous best-effort with reconcile as the safety net.

## Evidence constraint

Evidence payloads carry **proof metadata**: identifiers (UUIDs, codes), reason details, counts, hashes, references to runtime evidence rows. They do **not** carry:

- Raw source payloads (those live in `observed_payload_json` on `progression.admission` or in S3 archives)
- PII (`subject_extras` etc. fields that could carry tenant data)
- Large blobs (anything over ~4KB belongs in S3 with a reference)

Where a runtime act produces both runtime evidence (in `evidence_object` per D387) and an MLS event, the MLS event's `evidence_json` carries `{evidence_object_ref: "EVI-..."}` rather than duplicating the evidence body. The registry's `evidence_schema` for runtime-derived codes is REQUIRED to include an `evidence_object_ref` field.

This keeps MLS event size bounded and keeps PII out of the governance substrate.

## Inspector consumption

Once the substrate is in place, Inspector's per-MLS-row reads become:

```sql
SELECT current_value, current_code, current_evidence_json, last_transition_at, last_event_id
FROM metric.mls_state
WHERE mls_state_id = $1 AND mc_version_id = $2 AND tenant_slug = $3
```

Plus a join to `metric.mls_failure_code` for the `message_template`. The synthesis-from-many-sources logic in `admin-inspection.service.ts` is replaced by a thin reader. This is a follow-up migration task; Inspector continues to work with its current synthesis until the migration lands.

## Consequences

**Positive:**
- One queryable surface for all MLS state — Inspector, audit, dashboards, automation all read the same shape
- Cross-cutting queries become trivial ("which tenants have MLS-23 red right now?", "what flipped in the last hour?")
- Adding a new MLS state or new event source is a config + one-liner, not a service rewrite
- The probe-vs-gate invariant from DEC-c9e623 is preserved — recorder only reads probes, never writes via probes
- Runtime hot paths protected from MLS state-keeping failure (queue + best-effort)
- "Missing artifact" verdicts make the e2e operator narrative complete (concept → KPI funnel covers non-existence too)

**Negative:**
- Two new tables to maintain. Index management on `mls_state` matters at scale
- In-memory queue means events lost on process restart; the reconcile pass closes the gap eventually but introduces a window
- Trigger-binding config table adds one more place where wiring lives — ops must understand both code and config to debug an MLS event flow
- Initial seed of trigger bindings will reveal gaps in the existing event-source landscape (some events we want don't exist as typed events yet — e.g., schema-provisioner reconcile doesn't emit a typed event today)

**Neutral:**
- The substrate doesn't auto-write anything until the migration tasks land per-emitter. Until then, MLS state remains synthesized by Inspector. The substrate is opt-in adoption
- Reconcile pass adds nightly load comparable to existing `NightlyReconcilerService`
- This ADR does not promote individual probe service interfaces (separate work per MLS row). It locks the registry shape

## Implementation tracking

Filed as separate DevHub tasks against this ADR:

1. DDL — `metric.mls_state` + `metric.mls_state_event` + `metric.mls_trigger_binding` tables (requires explicit founder approval per Database Change Protocol)
2. `MlsStateRecorderService` + `MlsProbeRegistry` + queue + drain worker
3. **Backfill — populate `metric.mls_state` from existing probes/SSOTs before any consumer reads from it.** Calls `enumerateSubjects` for every registered MLS state, probes each subject, inserts ledger rows. **Blocking task before Inspector cutover (task 7) can begin**
4. Seed initial trigger bindings (one row per migration target)
5. Per-emitter migrations — separate task per service (admission, canonical-resolution, metric, evidence, ChainStatusService, ContractActivationService, SchemaProvisionerService, MLS-14 gate, runtime drift detector). Each is small and independently shippable
6. Reconcile pass — daily enumerate + probe + reconcile, surfaces `OPS.mls_ledger_drift_detected` + `OPS.mls_ledger_orphans_detected`
7. Inspector migration — cut over from synthesis to direct reads from `metric.mls_state`. Depends on (3)
8. Metric Lifecycle UI wiring (bc-admin) — Platform tab consumes `mls_state` reads; Tenant tab depends on substrate population for cross-tenant aggregation. Designed in mockup form during SES-5f806e

Tasks 1 → 2 → 3 are blocking sequence. Tasks 4-6 can land in parallel once 2 lands. Tasks 7-8 depend on 3.

## Out of scope (separate decisions)

- Specific seed trigger bindings — implementation detail, captured in task 4
- New probe services for MLS rows that don't have one yet (MLS-10, MLS-12) — separate ADRs per state
- Cross-process recorder (multi-instance bc-core) — current design assumes single-process; a future ADR addresses durable queue (Redis Streams or similar) when bc-core becomes multi-instance
- Retention policy for `mls_state_event` — out of scope; defaults to indefinite; future ADR if storage matters
- ESLint rule that requires emitters to call the recorder — discipline-level item, deferred

## References

- DEC-c9e623 (D389) — MLS Framework (renamed from OLS — see ADR errata 2026-05-03) — defines the 25 states this substrate operationalizes
- DEC-9d7a5c (D390) — MLS Failure Vocabulary (renamed from OLS) — defines `metric.mls_failure_code` that this ADR's `current_code` and `event.code` columns reference
- DEC-b8b825 (D391) — MLS-14 Activation Gate (renamed from OLS-14) — primary near-term consumer of `recordImmediate(event)`
- DEC-bebaec (D305) — Chain Completeness SSOT — `ChainStatusService` is a Probe Service called via trigger binding
- DEC-f0e78e (D388) — Inspector — primary read consumer of `metric.mls_state`
- DEC-95687d (D369) — Nightly Reconciler — pattern reference; reconcile pass added in D-5 follows the same cadence model
- DEC-ebb3cd (D387) — Evidence and Lineage Write Semantics — `proof_status` becomes an MLS-24 source event
