---
uid: mcf-post-bcf-metric-workflow-wiring-impact
title: MCF — Post-BCF Metric Workflow & Wiring Impact (pre-M12-DBCP audit)
description: Architecture audit performed before opening the M12 DBCP gate. Examines whether the M12-B proposal-only panel design has properly accounted for the metric workflow / wiring changes that BCF arrival forces — specifically what changes per artifact (SC / AC / OC / CC / MC), which legacy metric write paths must be forbidden or redirected, which reads can stay legacy-backed temporarily, and whether the planned MCF gate sequence (M12 → M13 PE-MC → M14 publication) needs an interposed materialization-plus-bridge gate (M12.5) before M13. Confirms M12-B as the right next gate. Recommends adding M12.5 (materialization + legacy bridge) between M12-B closeout and M13 PE-MC evaluator, with the substantive insight that MCF materialization is not a small follow-up to the panel — it is the gate where legacy authoring becomes forbidden and bc-admin / readiness ledger / CC binding paths get explicit bridge contracts. Eight hard assertions for the M12 DBCP are surfaced to prevent building a dead-end panel.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-pre-m12-dbcp-wiring-audit
---

# MCF — Post-BCF Metric Workflow & Wiring Impact

## 0. Why this note exists

The M12 preflight (`3124207`) recommends M12-B (proposal-only panel) as the next gate. Before opening the M12 DBCP, an operator question: *"after BCF, metric-related workflows/wiring will change, especially OC, CC, and MC. Have we taken proper cognizance of that before M12?"*

The answer this note develops: **yes for the panel shape itself; partially-no for the gate sequence after M12-B**. M12-B is still the right next gate, but M13 (PE-MC evaluator) should not run immediately after it. Between them, there is a real materialization + legacy-bridge gate (call it **M12.5**) that converts a panel proposal into a live `mcf.metric_contract` row, and that gate is where the *workflow* changes that BCF/MCF have always assumed actually land in the codebase. Skipping it leaves the legacy authoring path live + dual-authority risk + bc-admin orphaned.

This note is the audit. It is design + recommendation only. No code, DDL, data, or BCF edits.

---

## 1. What is live today (pre-M12)

### 1.1 Legacy metric authoring path (STILL ACTIVE on bc-core main `c359dc8`)

Confirmed via codebase exploration:

| Layer | Artifact | Behavior |
|---|---|---|
| Frontend (bc-admin) | `src/api/metric-definitions.ts`, `metric-catalog.ts`, `metric-reference.ts`, `metric-verification.ts`, `seed-metrics.ts` | 5 metric API surfaces — all targeting **legacy** `/api/metric-catalog/*` endpoints |
| API (bc-core) | `MetricDefinitionController.create()` / `bulkCreate()` | `POST /api/metric-catalog/definitions` — accepts new MC authoring requests |
| Service | `MetricDefinitionService.create()` | Writes `metric.metric_definition` + queues `metric.enrichment_job` |
| Substrate | `metric.metric_definition` (~1,241 rows) + `metric.metric_knowledge` + `metric.metric_binding` (`canonical_contract_id` FK to CC) + `contract.metric_contract` (780 rows: 778 archived + 2 drafts) | Legacy "MC corpus" |
| Seed loaders | `src/registry/seed/metric-kpi-*.ts` (9 files), `metric-taxonomy.ts`, `generate-metric-contracts.ts` | Populate legacy `metric.metric_definition` from KPI catalog |
| Runtime | `boundary/metric.service.ts` + `boundary/canonical-resolution.service.ts` + `ReadinessLedgerService` + `readiness-evaluation-dispatcher` | Event-driven metric evaluation — fires on OC/AC resolution; no cron; reads legacy MC corpus |
| Chain status | `registry/chain-status.service.ts` (D305 SSOT) | Reports L1-L7 chain completeness against legacy MC bindings |

### 1.2 MCF (NEW) — what M2-M11 already shipped

| Live MCF service | Status | Purpose |
|---|---|---|
| `McfCertWriterService` (M4) | live, dormant (0 cert rows) | `createMetricDraft` / `submitForReview` / `approveForActivation` / `activateMetric` / `supersedeMetric` — TX-atomic substrate + cert writes |
| `mcf.metric_authoring_panel_run` + `panel_transcript` + 2 allowlists (M5) | live, dormant | Panel-run record + per-agent transcripts; M5 mapr.consensus_payload_json + workbench_fingerprint_hash ready |
| `FixtureStructuralCheckService` (M9) | live, dormant | C-FX-1..C-FX-11 structural checks; pure function — no DB writes |
| `MetricSelfVerificationService` (M10) | live, dormant | Verifier engine; reads fixture + executes formula; writes `mcf.metric_self_verification_result` |
| `ReservoirIngestionService` (M11) | live, dormant | Intake queue writes + 3 status-transition methods; substrate dormant |

### 1.3 BCF (the other framework)

`RegistryAuthoringOrchestrator` already implements the **panel → cert → F3-dispatch** pattern for BCF authoring (`createEntity` / `createBusinessConcept` / `registerCharacteristic`). The cert layer is `FrameworkApprovalService.issueRegistryShapeCertification`. Panel rejections go to `contract.authoring_panel_rejection_log` with `scope_code IN ('bf_bo', 'cf', 'mapping')` — **BCF-scoped enum, no `mc` member today**.

`contract.panel_output_record` is shared infrastructure but currently BCF-only consumer (24 rows, all BCF).

---

## 2. Which metric workflows / wiring change after BCF — answered by artifact

### 2.1 OC — Observation Contract — **structural change: NONE**

OCs continue to be emit specs. The change is downstream: metrics consuming OC outputs become MCF-authored instead of legacy-authored. The OC → metric coupling is event-driven via `ReadinessLedgerService` (no FK; no schema dependency). The same fan-out fires for legacy MC and MCF MC consumers.

Action: **none** for SC/AC/OC at substrate; runtime listener fan-out gets one new consumer type (MCF MC) when materialization ships.

### 2.2 CC — Canonical Contract — **structural change: NONE; binding shape changes**

CC tables (`contract.canonical_contract`, `contract.cc_field_mapping`) are untouched. The change is in **how metrics bind to CC fields**:

| Era | Binding shape |
|---|---|
| Legacy | `metric.metric_binding.canonical_contract_id` (FK to CC) + `metric.metric_binding.cc_field` (string column) |
| MCF | `mcf.metric_variable_binding.business_concept_uid` (FK to BCF BusinessConcept; BC has its own mapping to CC field via canonical-field resolution); MC never references CC directly |

Implication: under MCF, a metric variable does NOT name a CC field directly — it names a BCF BusinessConcept (which has a canonical-field resolution path). This is the **clean path** mandated by the working rule (no name binding; binding by id, via BCF). The legacy `metric.metric_binding.canonical_contract_id` FK becomes informational/historical-only.

Action: **none** for CC at substrate. The CC-binding shape transition is captured in the **materialization** gate (§3), not in M12 panel.

### 2.3 MC — Metric Contract — **STRUCTURAL CHANGE: authority migrates from legacy to MCF**

This is the big one. MCF authority is `mcf.metric_contract` (new substrate); legacy `metric.metric_definition` becomes "candidate-intent reservoir" only (per `metric-context-framework-candidate-reservoir-and-authority-classification.md` and DEC-c3e57f Decision 2). Legacy `contract.metric_contract` (780 historical rows) is read-only / archived.

The writeable surface changes:

| Path | Pre-MCF | Post-MCF (target) |
|---|---|---|
| New MC author | `POST /api/metric-catalog/definitions` → `MetricDefinitionService.create()` → `metric.metric_definition` | M11 intake → M12 panel proposal → M12.5 materialization → `mcf.metric_contract` (via `McfCertWriterService.createMetricDraft`) |
| MC read for evaluation | `boundary/metric.service.ts` reads legacy `metric.metric_definition` + `contract.metric_contract` | Reads `mcf.metric_contract` for MCF-authored MCs; reads legacy for un-migrated MCs (dual-read transitional period) |
| MC binding | `metric.metric_binding.canonical_contract_id` (FK) | `mcf.metric_variable_binding.business_concept_uid` (FK to BCF) |
| Cert | none in legacy | `mcf.certification_record` (per M4) |
| Lifecycle states | implicit in `metric.metric_definition.status` | `mcf.metric_contract.governance_state_code` (5-state per M3) |

### 2.4 SC — Source Contract — **structural change: NONE; confirmed zero metric FK**

Confirmed by codebase exploration: `contract.source_contract` has no metric-related columns / FKs / joins. SC defines schema + admissibility rules at admission boundary; metrics are downstream consumers of resolved data. **No SC change before/during/after M12.**

### 2.5 AC — Admission Contract — **structural change: NONE; confirmed zero metric FK**

Same as SC. No metric coupling. **No AC change.**

---

## 3. Legacy metric write paths — forbidden vs redirected vs preserved-read

### 3.1 Eventually FORBIDDEN (post-materialization)

| Path | Action | When |
|---|---|---|
| `POST /api/metric-catalog/definitions` (create-new-metric) | HTTP 410 Gone OR redirect to MCF intake | After **M12.5 materialization** ships AND bc-admin migrates write surface (M17 territory) |
| `MetricDefinitionService.create()` direct writes to `metric.metric_definition` (outside seed loaders) | Production-side disabled (allowed only in seed scripts) | M12.5 |
| `metric.enrichment_job` queue | Decommissioned | M12.5 (enrichment is now panel-side via tool calls) |
| Direct INSERT into `contract.metric_contract` (legacy 780-row table) | Forbidden | Already true per DEC-c3e57f; not enforced at substrate; no service does this today |
| Seed loaders writing `metric.metric_definition` as "new MC" | Re-targeted to `mcf.metric_authoring_intake_queue` | Already supported by M11 `ReservoirIngestionService.ingestFromSeedMetrics` |

### 3.2 Temporarily PRESERVED-READ (dual-read transitional period)

| Path | Why preserve | Until |
|---|---|---|
| `GET /api/metric-catalog/definitions` (read legacy KPI catalog) | bc-admin still consumes; tenants still query via existing surfaces | bc-admin migrates to MCF read endpoints (M16+) |
| `metric.metric_definition` reads from `boundary/metric.service.ts` | Legacy MC evaluation must not break tenant runtime | Until all live metrics migrate to MCF authority |
| Readiness ledger fan-out for legacy MC | Tenant onboarding depends on it | Same as above |
| `chain-status.service.ts` reads against legacy MC bindings | D305 SSOT for L1-L7 chain reporting | Same as above |

### 3.3 Already SAFE (no change needed)

- SC/AC writes (zero metric coupling)
- OC writes (zero metric FK; event-driven coupling only)
- CC writes (zero metric FK; binding is via BCF concepts in MCF era)
- BCF writes (separate framework; no MCF coupling)
- `contract.panel_output_record` (BCF-only consumer today; MCF will INSERT under separate stage_code if MCF adopts BCF's shared panel substrate — TBD by M12 DBCP)

---

## 4. Does M12-B remain the right next gate? — **YES**

M12-B (proposal-only panel) becomes **more** correct in light of the wiring audit, not less. Three reasons:

1. **Materialization is not a trivial follow-up.** It bundles MC writes + cert writes + legacy-bridge decisions + bc-admin coupling design + tenant runtime impact assessment. Doing that inside M12 would compound R-09 (overbuilding) and likely produce dual-authority bugs.

2. **The legacy authoring path is still live.** Writing MCF MCs while `POST /api/metric-catalog/definitions` remains the operator's habitual endpoint would create silent dual-authority. The materialization gate is where that endpoint gets deprecation handling.

3. **bc-admin has zero MCF surface today.** Materialization without a consumer (operator console for read of mapr / mapt / consensus payload, then later confirm of draft MC) is materialization no one can verify. The audit UI is M16 territory.

M12-B's proposal payload is the *natural input contract* for the M12.5 materialization service. Keeping them separate keeps each gate inspectable + reversible.

---

## 5. Recommended gate insertion: **M12.5 — Materialization + Legacy Bridge**

### 5.1 Where M12.5 sits

```
M11 (intake)  →  M12 (panel proposal-only)  →  ★ M12.5 ★  →  M13 (PE-MC)  →  M14 (publication)
```

### 5.2 M12.5 scope

| In scope | Out of scope |
|---|---|
| `MetricAuthoringMaterializationService` reads M12 panel `consensus_payload_json` from `mcf.metric_authoring_panel_run` and calls `McfCertWriterService.createMetricDraft(...)` with `panel_run_uid` as authoring evidence | Operator console UI (M16) |
| Writes `mcf.metric_contract` + `metric_contract_version` + `variable_binding` + `filter_clause` + `computed_dimension_ref` + first proposed fixture row + `certification_record(action_code=metric_create)` IN ONE TX (M4 cert writer already does this) | PE-MC-1..PE-MC-10 evaluation (M13) |
| Invokes `FixtureStructuralCheckService.runStructuralChecks` (M9) + `MetricSelfVerificationService.verifyFixture` (M10) for the proposed fixture | Publication path `approved → active` (M14) |
| Sets M11 intake row status via `ReservoirIngestionService.markConsumedByPanel(intake_queue_uid)` — moved from M12 panel (where the preflight currently placed it) into materialization | Supersession (M15) |
| **Legacy bridge contract**: define explicit read-fallback policy — when a consumer asks for "MC by metric_code", is the lookup mcf-first / legacy-first / mcf-only? Lock the answer | Frontend changes (M17) |
| Deprecation header on `POST /api/metric-catalog/definitions` ("Sunset: 2026-Qn; use MCF intake + panel + materialization") | Tenant runtime migration (separate gate) |
| Tests: panel-payload → MC + fixture + cert + verifier-pass smoke (small DDL apply may be needed for any new bridge table if introduced; TBD by M12.5 DBCP) | Real model API calls (mocked in tests) |

### 5.3 Implication for D-M12-8 in the preflight

The current preflight (`3124207` §3.8) has the M12 panel itself calling `ReservoirIngestionService.markConsumedByPanel`. **Revise**: M12 panel should call `markConsumedByPanel` only when the panel verdict is `APPROVE_FOR_DRAFT` AND the operator has committed to materialization. Two cleaner options for M12 DBCP:

- **Option α**: M12 panel sets intake status to a new sub-state `proposal_accepted_pending_materialization` (requires M11 enum extension); M12.5 transitions from there to `consumed_by_panel` after MC write succeeds
- **Option β**: M12 panel leaves intake at `pending` even on `APPROVE_FOR_DRAFT`; M12.5 transitions to `consumed_by_panel` on successful materialization. Simpler — no enum extension. **Recommended.**

This is a real correction to the preflight that M12 DBCP must absorb.

### 5.4 Implication for rejection logging

Current preflight has rejections going to `mcf.metric_authoring_panel_transcript` per model + aggregate to `mapr.consensus_payload_json`. BCF analogue uses `contract.authoring_panel_rejection_log` (scope_code in `bf_bo` / `cf` / `mapping`). **Two paths for MCF**:

- Add `mc` to the existing enum (single shared rejection log; small substrate amendment)
- Create `mcf.metric_authoring_panel_rejection_log` (mcf-scoped sibling)

This decision belongs in M12 DBCP — not deferred. The preflight should be amended to call this out as **D-M12-11**.

---

## 6. BCF panel patterns — safe reuse vs do-not-carry-over

### 6.1 Safe reuse (already factored into M5 substrate)

- Closed-enum verdict shape (`APPROVE_FOR_DRAFT` / `OPERATOR_REVIEW` / `REJECT_<defect_code>`)
- Per-agent transcript pattern (mapr + mapt schema is BCF-shaped)
- Workspace-fingerprint discipline (algorithm version constant, single source per substrate + service)
- Panel → cert-issue → substrate-write sequence (BCF `RegistryAuthoringOrchestrator` is the template; MCF version dispatches to `McfCertWriterService` instead of F3 dispatch — but only at M12.5 time, NOT in M12-B)
- `contract.panel_output_record` may be shared if M12 DBCP locks an MCF-specific `stage_code` value

### 6.2 Must NOT carry over

- **BCF v1 packet-in / verdict-out function model** — MCF requirements §11.3 explicitly rejects this. MCF is workbench-doctrine from the start.
- **BCF C5 cert layer (`registry_shape_certification`)** — BCF-specific. MCF uses M4 `mcf.certification_record` with MCF action_codes (`metric_create` / `metric_transition` / `metric_supersede`).
- **BCF tool surface** (`bcf.registry_collision_probe` / alias probes / lifecycle history) — these are vocabulary-authoring tools. MCF tool surface is different per requirements §11.3.3: `bcf.search_entity` / `bcf.search_business_concept` / `bcf.read_entity` / `bcf.read_business_concept` / `bcf.reachability_check` / `evidence.search` / `evidence.retrieve` / `source_reality.summarize` / `kpi_catalog.read_intent` / `mc.identity_probe`.
- **BCF assumption that legacy metric tables are authority** — BCF never made this assumption; this audit confirms BCF docs and code do not depend on `metric.metric_definition` being authoritative. MCF can take over without coordinating with BCF.
- **BCF F3 dispatch model** (`createEntity` etc.) — MCF substrate writes go through the M4 cert writer in one TX, not via per-operation dispatch. (M12.5 service IS the dispatch; M4 cert writer IS the substrate writer.)

### 6.3 Rejection log scope_code enum is the seam

BCF `contract.authoring_panel_rejection_log.scope_code` is the most concrete BCF assumption that pre-dates MCF. The enum lacks `mc`. The M12 DBCP decides whether to widen the enum or create an MCF-scoped sibling. See §5.4 D-M12-11.

---

## 7. Implications for M12 DBCP

The M12 DBCP must absorb the following amendments to the preflight (`3124207`):

### 7.1 New decision: D-M12-11 — Rejection log venue

Add: choose between widening `contract.authoring_panel_rejection_log.scope_code` enum to include `mc`, vs creating `mcf.metric_authoring_panel_rejection_log`. **Recommendation**: create the mcf-scoped sibling — keeps MCF rejection lifecycle independently governable; avoids cross-framework write coupling (per MCF requirements §3.8); adds 1 new mcf.* table (small DDL).

### 7.2 Revision to D-M12-8: Failure / rejection logging

Replace "M12 panel sets intake status via markConsumedByPanel" with **"M12 panel sets intake status via markRejected (on all-reject) or leaves at pending (on APPROVE or OPERATOR_REVIEW); only M12.5 materialization advances to consumed_by_panel after MC write succeeds."** This keeps the intake row's status truthful — `consumed_by_panel` should mean "materialized into MCF substrate", not just "panel approved."

### 7.3 Eight hard assertions to add to M12 DBCP §X

To prevent building a dead-end panel:

| # | Assertion | Enforced by |
|---|---|---|
| HA-1 | M12 v1 panel service does NOT import `MetricDefinitionService` / `MetricDefinitionRepository` / any legacy `metric.*` writer | Service code structure + ESLint rule + integration test |
| HA-2 | M12 v1 panel service does NOT import `McfCertWriterService` (materialization is M12.5) | Same |
| HA-3 | M12 v1 panel service does NOT import `MetricSelfVerificationService` (no verifier invocation at panel time) | Same |
| HA-4 | M12 v1 panel reads BCF concepts ONLY via the `bcf.*` tool surface — never raw SQL against `concept_registry.*` | Tool surface is the only import; integration test |
| HA-5 | M12 v1 panel writes ONLY to `mcf.metric_authoring_panel_run` + `metric_authoring_panel_transcript` (+ optionally `mcf.metric_authoring_panel_rejection_log` per D-M12-11) — no other mcf.* / contract.* / metric.* table | Post-run integration test asserts row counts on all other tables == 0 |
| HA-6 | Intake status transitions: `markRejected` (all-reject case) or no-op (APPROVE / OPERATOR_REVIEW); `markConsumedByPanel` is forbidden in M12 v1 (M12.5 owns it) | Service code does not call `markConsumedByPanel` |
| HA-7 | Panel `consensus_payload_json` schema is locked in M12 DBCP §X and consumed unchanged by the future M12.5 materialization service | Schema lock + integration test that asserts a known shape can be deserialized by the materialization-service mock |
| HA-8 | M12 v1 panel reads reservoir-provenance from M11 intake row + copies all 4 fields into `mapr.reservoir_*` (addendum guardrail #6); satisfies M5 NF1 all-or-none CHECK | Substrate CHECK already enforces; service test asserts the copy happens |

### 7.4 Frontend handoff note for M12 DBCP

Add explicit note: **bc-admin must NOT invoke M12 panel API until M12.5 + M16 (audit UI) ship**. M12 v1 is service-only + integration tests only. There is no operator console for M12 in v1. Any frontend exposure before M12.5 + M16 is a foot-gun.

### 7.5 Seed loader handoff note

Add explicit note: existing seed loaders (`src/registry/seed/metric-kpi-*.ts`) writing `metric.metric_definition` are **NOT** changed by M12. M11 already supports a separate path for reservoir population (`ReservoirIngestionService.ingestFromSeedMetrics`). The seed loaders' migration is a separate operator-driven program (not a gate).

---

## 8. Updated gate sequence

```
[CLOSED]  M2-M11                MCF substrate + services
[OPEN]    M12   preflight       3124207
[NEXT]    M12   DBCP            absorbs §7 amendments (D-M12-11 + revised D-M12-8 + HA-1..HA-8)
          M12   impl PR         service + tests + (possibly) 1 new mcf.* table for rejection log
          M12   evidence + closeout
[NEW]     M12.5 preflight       materialization + legacy bridge
          M12.5 DBCP            MetricAuthoringMaterializationService spec
          M12.5 impl PR         service + tests; first MC + fixture + cert + verifier write end-to-end
          M12.5 evidence + closeout
[THEN]    M13   PE-MC evaluator (now has materialized MCs to evaluate)
          M14   publication path
          M15   supersession
          M16   operator console (read; ALSO unblocks bc-admin audit of M12 panel runs)
          M17   operator console (write; deprecates POST /api/metric-catalog/definitions)
          M18+  tenant binding
```

Net change: **one new gate (M12.5) inserted between M12 closeout and M13**. The total gate count grows by 1; the per-gate scope stays small.

---

## 9. Recommendation summary

| | |
|---|---|
| **Is M12-B still the right next gate?** | **YES.** The audit confirms it. |
| **Does M13 need to include workflow/wiring migration?** | **NO.** Inserting that into M13 would expand PE-MC scope and re-introduce R-09 risk. |
| **Insert a new gate?** | **YES — M12.5 (materialization + legacy bridge).** Between M12 closeout and M13 PE-MC. |
| **Amendments to M12 preflight before DBCP?** | **YES — three small ones:** add D-M12-11 (rejection log venue); revise D-M12-8 (intake status transitions); add HA-1..HA-8 hard assertions. |
| **Frontend impact in M12 v1?** | **NONE.** bc-admin does not invoke M12 panel API until M12.5 + M16 ship. |
| **SC / AC / OC / CC changes in M12 v1?** | **NONE.** Confirmed zero metric coupling for SC/AC; OC/CC behaviorally unchanged. |
| **Legacy metric path status during M12 + M12.5?** | **LIVE-AS-READ; new-write path moves to MCF intake + panel + materialization at M12.5; legacy write path forbidden after M12.5 closeout via deprecation header.** |
| **Risk if we proceed straight to M13 after M12?** | **HIGH** — dual authority (legacy + MCF MCs simultaneously authoritative for evaluation); bc-admin orphaned; intake rows stuck at `pending`; PE-MC evaluator has nothing to evaluate. |

---

## 10. Scope confirmation

- ✅ Design / audit note only — no bc-core implementation
- ✅ No DDL
- ✅ No data writes
- ✅ No M12 DBCP yet (this note prepares for it; does not open the gate)
- ✅ No BCF edits
- ✅ bc-core main `c359dc8` untouched
- ✅ bc-docs-v3 main advances by this note only
- ✅ `bc-postgres` MCP `allow_write=false` throughout
