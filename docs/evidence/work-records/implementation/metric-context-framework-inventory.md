---
uid: metric-context-framework-inventory
title: Metric Context Framework (MCF) — Implementation Inventory
description: Inventory pass against the post-D418 metric/fiscal/MLS/chain/readiness/L-node/formula implementation surface in bc-core, bc-admin, bc-ai, DevHub change records, and local memory/feedback files. Step 1.0 mines a Failure Evidence Overlay so the document's verdicts are informed by observed scars, not just by current existence. Step 1.1 then classifies each artifact as keep / adapt / stale-deprecate / gap against the MCF requirements (metric-context-framework-requirements.md, post commit 13f9bb6). Companion to that requirements doc; informs the Step 2 gap/risk survey and the Step 3 MCF build plan.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: inventory
---

# Metric Context Framework (MCF) — Implementation Inventory

## 1. Scope, method, and sources

### 1.1 Purpose

Companion to `metric-context-framework-requirements.md` (MCF requirements, post commit 13f9bb6). This inventory classifies the existing post-D418 implementation surface that MCF will either reuse, rework, retire, or replace. It is the input to Step 2 (gap/risk survey) and Step 3 (MCF build plan).

The deliberate sequencing per operator instruction:

- **Step 1.0 — Failure Evidence Overlay.** Mine ADR/session/change-record/memory evidence for observed failure modes per artifact family, before classification. The BCF arc showed that classifying scarred components as "reusable" merely because they still exist produces fantasy build plans.
- **Step 1.1 — Implementation Inventory.** Classify each artifact with one verdict, citing the relevant Failure Evidence Overlay entries inline.

### 1.2 Verdict bins (per operator instruction)

| Verdict | Meaning |
|---|---|
| **keep** | Reusable as-is, no unresolved evidence issue, MCF requirements compatible without rework. |
| **adapt** | Useful but needs rework or guardrails to satisfy MCF requirements (vocabulary, AST shape, package-signature hash discipline, fixture binding, panel-proposes-platform-verifies pattern, authoring-record emission). |
| **stale-deprecate** | Obsolete, failed path, or incompatible with post-D418 / MCF — replace entirely. |
| **gap** | Required by MCF requirements but absent — needs to be built from scratch. |

### 1.3 Important discipline

- **Prior failure evidence is not automatically a current defect.** Many scarred artifacts have been substantively repaired since the evidence date. Each Failure Evidence row separates historical scar from current status where verifiable.
- **Missing evidence is an evidence gap, not proof of safety.** Artifacts that do not appear in the overlay may simply have escaped session-level scrutiny; their absence does not certify them.
- **No architecture is proposed in the evidence sweep.** Architecture lives in MCF requirements (§7-§17). This document does not re-derive it.
- **Read-only inspection across bc-docs-v3, bc-core, bc-admin, bc-ai, DevHub, and memory files.** No code, DB, schema, or PR changes.

### 1.4 Out of scope

- BCF artifacts already inventoried in `business-context-framework-inventory.md` (read for boundary clarity; not re-inventoried here).
- All four evaluation boundaries' runtime apparatus *qua* runtime — MCF reads do not trigger evaluation (MCF requirements §15.2). Inventory covers them only as "surfaces MCF will reference at evaluation time".
- Tenant-facing UI (bc-portal). bc-admin metric surfaces are inventoried only as a consumer map (§5), not as a UI design target.
- SC, AC, OC, CC composition — these are out-of-MCF-scope per MCF requirements §2.

### 1.5 Source list

#### ADR files inspected (mapped from D-numbers per operator brief)

| D-number / decision | Hex UID | ADR file |
|---|---|---|
| D068 metric architecture | DEC-ecec75 | `ADR-ecec75.md` |
| D162 DB rules | DEC-1918d0 | `ADR-1918d0.md` |
| D268 session discipline | DEC-ebf0b4 | `ADR-ebf0b4.md` |
| D363 fiscal grain mismatch | DEC-1efa47 | `ADR-1efa47.md` |
| D364 fiscal calendar stack | DEC-d7e7a0 | `ADR-d7e7a0.md` |
| D365 CC posting_date_field | DEC-a8e8fc | `ADR-a8e8fc.md` |
| D366 L-node semantic gate | DEC-804874 | `ADR-804874.md` |
| D389 MLS framework | DEC-c9e623 | `ADR-c9e623.md` |
| D390 MLS failure vocab | DEC-9d7a5c | `ADR-9d7a5c.md` |
| D391 MLS-14 gate | DEC-b8b825 | `ADR-b8b825.md` |
| D392 MLS substrate | DEC-e7b7b3 | `ADR-e7b7b3.md` |
| D393 runtime drift | DEC-29f134 | `ADR-29f134.md` |
| Chain Status SSOT | DEC-bebaec | `ADR-bebaec.md` |
| D411 BCF framework approval | DEC-149ab2 | `ADR-149ab2.md` |
| D415 immutable characteristic atoms | DEC-26b6e2 | `ADR-26b6e2.md` |
| D417 quarantine | DEC-6c57e2 | `ADR-6c57e2.md` |
| D418 retirement | DEC-a19428 | `ADR-a19428.md` |
| D419 historical FK sink | DEC-f48f99 | `ADR-f48f99.md` |

D314, D315, D316, D323, D329 ADR files were not surfaced directly by hex-UID grep against the seed list (the D-codes are conversational nicknames; the UID list in CLAUDE.md is canonical per D334). Session memory files (§1.5.3 below) carry the substantive content of these decisions and have been used as the citation source instead.

#### DevHub records

- `devhub_decision_list` (985-line catalog inspected; spot-checked against the hex UIDs above and matches the table).
- `devhub_change_record_list` filtered for bc-core — 377 records returned; recent metric-touching sessions identified by SES-UID match against the failure-evidence seed list.
- `devhub_session_get_context` for project `bc-core` — most recent closed session SES-fe15e0 (D418 Gate 5.3 disposed-state verification) confirms substrate state used in §3.

#### Session histories (memory file reads)

- `session_metric_chain_completeness.md` (SES-Apr 11) — bypasses removed; INV-X2 = 237 BFs without OC coverage.
- `session_metric_engine_apr12.md` (SES-Apr 12) — engine built (DEC-c0290f); benchmark 3.3ms/57ms; CR-QG-MC-GRAIN gate.
- `session_chain_gap_apr13.md` (SES-08c9c6 + 7 others Apr 13) — 309→551 L7 MCs; CO payload inflation bug found.
- `session_d314_d316_apr14.md` (SES-Apr 14) — D314 CO fix, D315 engine hardening + formula audit, D316 readiness scheduler; chain_complete=0 bottleneck identified.
- `session_d323_greenfield_oc_enrichment.md` (SES-96339f Apr 14) — greenfield wipe; 15/93 MCs producing; 80 rejected with breakdown.
- `session_chain_readiness_apr12.md` — adjacent.
- `session_d317_d322_apr14.md` — adjacent.
- `session_d335_ui_apr15.md` — adjacent.
- `session_d340_definition_canonical.md` — adjacent (definition-canonical relationship locked).
- Plus session summary embedded at conversation start: SES-594568 (May 14 2026) — MC body / D329 constants / seed thinness / header divergence / SERVICES-ONLY discipline.

#### Memory feedback files

- `feedback_runtime_readiness_gate.md` — 5-condition runtime-readiness; sandbox1 AR pilot 14/31; helper-script trust model.
- `feedback_metric_lifecycle_states.md` — MLS framework, 25 states, MT-04971 specimen, phased enforcement v1 shipped.
- `feedback_no_placeholders.md` — empty > fake data.
- `feedback_funnel_padding.md` — 81-CFs-to-1-NETWR pattern; graduated to MLS-14 structural rule.
- `feedback_zero_claims_policy.md` — zero claims without first-hand proof; SAP S/4HANA not yet proven.
- `feedback_test_discipline.md` — D082, no skipped failures, mock-heavy tests prohibited.

#### Implementation source

- Drizzle schema files under `bc-core/src/database/schema/` (sub-agent report; verified table inventory).
- Service files under `bc-core/src/` (sub-agent report; module-level coverage).
- bc-admin metric-related routes inferred from sub-agent report on `src/api/*.ts` consumers.

### 1.6 Query basis

Substrate facts in §3-§4 reflect Drizzle schema source state at the worktree head at time of drafting. Live DB counts (the "1,241 definitions, 589 contracts, 195 ready" figures from `feedback_metric_lifecycle_states.md`) are point-in-time 2026-05-07 unless otherwise noted; later sessions may have moved these.

---

## 2. Failure Evidence Overlay

Evidence-only. Organized by artifact family. Each row captures:

- **Evidence source** — ADR, session, change record, or memory file ID.
- **Affected artifact tag** — from the operator-supplied list.
- **Failure mode** — descriptive; what went wrong or what was found.
- **Historical evidence summary** — what was observed at the time.
- **Current status if known** — resolved / open / abandoned / workaround in place.
- **Unresolved risk if any** — what could still bite MCF.
- **Inventory implication** — how this evidence informs a §3-§4 verdict.

### 2.1 Metric evaluation engine

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-EVAL-1** SES-Apr 12 (metric_engine_apr12) | Engine had no closed-set formula taxonomy; supported "~1800 KPI formula patterns" via recursive descent. | DEC-c0290f locked engine to SUM/COUNT/AVG/MIN/MAX, ABS(), arithmetic, parens, constants, bare variables. Benchmark 3.3ms / 57ms on 712 COs. | Resolved at engine level. Formula text is parsed; AST is internal-only. | MCF requirements §7 mandate formula authored *as AST*, not parsed from text. Current engine accepts text; this is the load-bearing gap between current state and MCF. | `MetricEvaluationEngine`: **keep** at the execution layer. The text-parsing input shape: **adapt** (replace text input with AST input). See §4. |
| **F-EVAL-2** SES-45e3ba (referenced via prior session memory) | Alias mismatch between `metric.repository` fact-write key and table column inflated DSO to 115/230 days. | Resolved via engine-boundary repair. Foundation gate classification: D (engine-side repair). | Resolved. | Engine boundary remains permissive on column-alias hygiene; MCF AST + bind-time checks (§6.3) would have caught this earlier. | Engine: **keep**. Validates MCF's bind-time check 5 (grain alignment) requirement. |
| **F-EVAL-3** SES-cd4f80 (referenced via prior session memory) | Typed-fact writer silently dropped a row. | Contract sound; data shape sound; engine boundary permissive. Resolved. | Resolved. | Same family as F-EVAL-2 — engine permissiveness is a long-standing pattern. | Engine: **keep**. Validates MCF requirement for explicit per-row rejection envelopes (preserved in `evidence.evidence_object` per F-OBS-1). |
| **F-EVAL-4** SES-f10b35 (halted at Foundation gate) | DSO temporal arc 38→47 not expressible. MC grammar can't express as-of balance or trailing window. | Foundation gate caught it: would have required SDG calibration (A-layer compensation) for a missing B-layer expressiveness. Halted before code. | Halted; deferred to MCF MC grammar work. | The expressiveness gap is the direct motivator for MCF §7 closed AST node taxonomy with `window`, `time_anchor_resolution`, `bucket_assign`. MCF requirements address this; no current implementation does. | Engine: **adapt** at the temporal layer. MCF must add window/time-anchor/bucket nodes to AST taxonomy before the engine can serve as-of and trailing-window semantics. |
| **F-EVAL-5** SES-Apr 13 (chain_gap_apr13) | CO payload inflation bug: `applyBfToCf()` copied each BF value to ALL CFs mapped via `cc_field_mapping` (81 CFs received the same NETWR value). | `net_credit_sales = ar_aging = number_of_ar_staff = sum(NETWR)` for the same period. | Resolved in D314 (SES-Apr 14): `applyBfToCf()` removed from resolution path; BF→CF translation moved to metric evaluation. | The architectural lesson — `cc_field_mapping` is *metric engine instructions, not resolution-time copy rules* — must remain enforced through MCF's binding layer (§6). MCF formula AST `variable_ref` nodes to BCF BCs are the right model; do not regress. | `CanonicalResolutionService`: **keep** post-D314 fix. `cc_field_mapping` mapping interpretation: MCF makes it explicit via §6 variable binding to BCs. |

### 2.2 Formula / rule audit

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-FORM-1** D315 / SES-Apr 14 (d314_d316) | 357 of 778 MC formulas failed audit; top failure `field_not_in_cc` (733 instances) — formulas referenced CFs not mapped in the MC's CC. | 240 pass / 181 warn / 357 fail. Top defects: 7 SUM*SUM patterns, 15 unsupported functions (ML_MODEL, QUALITATIVE_ASSESSMENT, STDDEV, SUM_BY_CATEGORY, WEIGHTED_AVG). ~40 needed domain corrections (cycle times SUM→AVG; provisions to weighted avg). | `FormulaAuditService` shipped (D315). `audit_status_code` persisted to `contract.metric_contract`. Readiness resolver excludes failed MCs. Fail-closed on cold start. | Audit operates on text, not AST. MCF requirements §7.2 require closed AST node taxonomy with type-checking at bind time — this is a structural replacement for text-based audit. The 5 banned functions remain in real seed metrics; MCF must decide whether to add them to AST taxonomy or to reject MCs that need them. | `FormulaAuditService`: **adapt** (text-based; MCF AST replaces it). The banned-function list is MCF Q4 input (open question in MCF requirements §19.2). |
| **F-FORM-2** feedback_funnel_padding + DEC-b8b825 (MLS-14) | 81 CFs all mapping to one source column (NETWR) — same numeric output under different metric names. Specimen `mc__ar_staff_productivity` v1.0.0 (MT-04971): `SUM(WRBTR)/SUM(WRBTR) = 1.0`. | All probes (ChainStatusService, Inspector, IntegrityService) returned green. Only human inspection caught it. Operator intercept: "we just do not want to bump the numbers we want it real and honest." | Resolved structurally via MLS-14 Semantic Activation Gate (D391, shipped 2026-05-04→05-07 in SES-7e37a8). Re-evaluation downgraded 289 of 828 active MCs to draft. 200 MDs in semantic-collapse state. | MLS-14 is the structural answer. MCF must inherit this gate or replicate it — the rule cannot be relaxed back. MCF PE-MC-10 (self-verification fixture) is an additional independent gate that would also detect this case (running `SUM(I1)/SUM(I2)` against a fixture where I1≠I2 would yield ≠1.0; equality at runtime is a tell). | `Mls14ActivationGate` + `Mls14SignatureHashService`: **keep**. MCF AST `variable_ref` discipline must preserve the semantic signature distinction. |
| **F-FORM-3** SES-594568 (May 14 2026) | MC body header divergence: `mc-onboarding.service.ts` lines 442-443 hardcode `tags`-as-varcodes and formulaic descriptions in the envelope. Live master-shape authority is `bc-core/src/registry/meta-schemas/metric-v1.schema.json` (NOT the stale `legacy-v2/.../metric-v1.json`). Body permits D329 `value` property in `variables[].items`. `co_bindings.minItems: 1` is enforced. `direction_code` enum is kebab-case in body (`higher-is-better`), snake_case on seed. | Live lifecycle uses only `{draft, active, superseded}` — `review`/`approved` never used. Seed `status_code` is unused as a promotion signal — all 1,216 non-deprecated seeds carry `draft`. KNOWN_CONSTANTS TS map is transitional only, not runtime SoT. | TSK-1f4988 (governed constant registry) and TSK-9ecaee (4 catalog populations cleanup) filed. Slice (0) plan in bc-docs-v3 onboarding work records. | MCF requirements §5.1 and §7 implicitly assume body content matches schema; the header-shape hardcoding is a `mc-onboarding.service.ts` defect that MCF must either fix at adapt time or replace with a fresh AST-authoring service. | `mc-onboarding.service.ts`: **adapt** (header β-path / slice (0) plan); see §4. SERVICES-ONLY discipline (no raw INSERT) per CLAUDE.md mandates this be repaired in the service, not bypassed in MCF. |

### 2.3 Chain status / chain completeness

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-CHAIN-1** ADR-bebaec (SES-Apr 11/12/13) | `IntegrityService` was stateless (1,341 lines), recomputed chain status from scratch every session, with 5 known bugs and 5 different sessions reporting 5 different numbers (100% / 30% / 86% / 22% / 237 BF gaps) — all "correct" measuring different dimensions. | DEC-bebaec locked: 7-link L1-L7 per-variable definition + per-contract C1-C5 + end-to-end E1-E3. Persisted SSOT in `contract.chain_status` + `contract.chain_trace`. ChainStatusService computes write-through; IntegrityService deprecated. | Resolved. `ChainStatusService` is canonical; deprecation noted in CLAUDE.md ("IntegrityService is DEPRECATED — kept for activation gates and per-MC detail views only"). | Some bc-admin call sites may still hit IntegrityService for per-MC detail views — needs verification before MCF onboards. | `ChainStatusService` + `contract.chain_status` + `contract.chain_trace`: **keep**. `IntegrityService`: **stale-deprecate** (final removal pending consumer-map cleanup). |
| **F-CHAIN-2** SES-Apr 14 (d314_d316) | Even after chain definition was locked, `chain_complete = 0` was the funnel bottleneck for demo-selenite: 583 MCs were "partial", top gaps L4/L6/L7. | Top L7 break: source field not traced to catalog (99 MCs blocked). L6: 167 MCs blocked on draft readers. L4: 104 MCs blocked on OC field_mapping. | Substantively unblocked across Apr 13-14 (309→551 L7 MCs, 94.5%). 32 MCs remained with breaks (BUCHW computed, location_area, employee_work_schedule). | The L7 governance gate ("source field traced to catalog") is a chain check, not an MCF gate. MCF inherits this via §6.3 check 5 (grain alignment). | `chain_status` substrate: **keep**. The L1-L7 model is the right SSOT for MCF to consume. |
| **F-CHAIN-3** SES-594568 (May 14 2026) | Live lifecycle on contract.metric_contract_version uses only `{draft, active, superseded}` — Foundation-defined `review` / `approved` never used. `governance_state_code='active'` set without a gate in many historical cases (the MT-04971 specimen reached active despite being collapsed). | MLS-14 re-evaluation pass (2026-05-06) downgraded 213 unjustified actives. Phased v1 enforcement live. | Phased v1 BLOCKER codes [semantic_class_collapse, chain_not_complete] downgrading. Codes [temporality_kind_missing, formula_audit_not_run] visibility-only. | MCF requirements §4.6 + §10.5 require Foundation `draft → review → approved → active → superseded`. Current state is partial. MCF must either retrofit `review` / `approved` transitions or document the skip explicitly. | `metric_contract_version` lifecycle: **adapt** (state skip needs explicit MCF disposition). |

### 2.4 Readiness ledger + readiness scheduler

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-READY-1** D316 / SES-Apr 14 (d314_d316) | Pre-D316 there was no readiness model — "what data is available for which MC?" was a query per session. | `metric.mc_dependency` (1,133 CC deps) + `metric.readiness_ledger` shipped. Event hooks on reader/resolution/metric evaluation auto-upsert ledger. | Live and in-use. Funnel API + MC-list API consume it. | `readiness_ledger.source_type` is text without CHECK constraint (only 3 valid values: reader_run, resolution, metric_snapshot). Failures don't touch ledger (only completed runs write). | `readiness_ledger` + `mc_dependency`: **keep**. MCF requirements §14 readiness consumption is well-served by current substrate. CHECK constraint is a follow-up hygiene item, not blocker. |
| **F-READY-2** feedback_runtime_readiness_gate (Apr 29 2026) | 5-condition runtime-readiness rule: contract-gate eligible ≠ runtime-ready. "15 audit-pass eligible" collapsed under preflight to 0 producing — 7 silently rejected the prior day, 8 depended on zero-row CCs. | Sandbox1 AR pilot ceiling locked at 14/31. 7-bucket classification published (fully materialized 1 / snapshot-index-backed 12 / ledger-orphan 1 / rejected-source-data-blocked 7 / upstream-CC-blocked 8 / formula-blocked 1 / warn-deferred 1). | Standing rule in CLAUDE.md and memory. | The 5 conditions are an MCF authoring concern — every MCF MC must declare its runtime-readiness intent (MCF requirements §8 PE-MC-8). Working position is PE-MC-8 is publication-deferred (open question Q24 in MCF §19.7). | Validates MCF MLS overlay (§14) decision. PE-MC-8 publication-deferred stance is consistent with this evidence. |
| **F-READY-3** feedback_runtime_readiness_gate | Helper-script trust model violation: `bc-core/scripts/evaluate-ready-mcs.mjs` hardcoded to `tbc_selenite_dev` / `'demo-selenite'` / `boundary.canonical_object` (pre-DEC-f02230 schema); claimed `--mc`/`--limit`/`--tenant` flags that don't exist. Would have posted evaluations for every ready MC against the wrong tenant DB. | Standing rule: helper scripts untrusted until source verified in same turn. | Standing prohibition pending repair. | MCF authoring scripts and tools will face the same trap. MCF requirements §11.3 governed workbench framing addresses this via tool allowlist + audit transcript. | Validates MCF panel-as-workbench architecture (no free script execution; tool-set v1 schemas required, open question Q32). |

### 2.5 MLS (Metric Lifecycle States) framework

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-MLS-1** feedback_metric_lifecycle_states + DEC-c9e623 | Six prior approaches (IntegrityService, ChainStatusService, Readiness ledger, L-node verifier, Inspector, contract_binding) each told a partial truth about activation; none was the activation primitive. Probes overlapped on some rows and were silent on others. | DEC-c9e623 locked MLS framework: 25-step ladder (Platform MLS 1-14 + Tenant MLS 15-25). Probe-vs-gate separation invariant. Cross-boundary failures use stable codes. MT-04971 is canonical drift specimen. | Substrate live (D392). MLS-14 gate live (D391 phased v1). Backfill done (1,658 rows in `metric.mls_state`). | MLS substrate exists but `LNodeSemanticService` does not (schema-only per bc-core inventory §A). MLS rows MLS-21/22/23 (tenant) depend on probes that may not all exist. Phase 2 enforcement (BLOCKER promotion of temporality_kind_missing + formula_audit_not_run) parked pending D386 Stage 1 backfill. | `metric.mls_state` + `metric.mls_state_event` + `metric.mls_trigger_binding`: **keep**. `MlsStateRecorderService` + `MlsProbeRegistry` + `MlsBackfillService`: **keep**. `Mls14ActivationGate`: **keep**. L-node service: **gap**. |
| **F-MLS-2** DEC-b8b825 (MT-04971 specimen) | MT-04971 walked end-to-end during SES-c37208: governance_state_code='active' set without a gate; chain_status='complete'; last_validated_at=NULL; both formula variables resolved to identical (BSID, WRBTR) signature; every existing probe returned green. | Caught by human reading metric name + resolved fields side-by-side. | MLS-14 phased v1 enforcement now flips this class draft on re-evaluation. 200 MDs in semantic-collapse state. | MCF must inherit the MLS-14 discipline — and add an independent verification mechanism (PE-MC-10 self-verification fixture) that catches `SUM(I1)/SUM(I2)=constant` shape collapses by exercising the formula against bound inputs where I1≠I2. | Validates MCF requirements §12 self-verification fixture as a second independent gate beyond MLS-14 signature-hash. |
| **F-MLS-3** feedback_metric_lifecycle_states (May 3 2026) | "Missing artifact is a legitimate MLS verdict" — where an upstream artifact is expected to exist for the chain to complete, its absence is recorded as `current_value='red'` with code `MLS-NN.no_artifact_kind_for_parent`. | Locked rule in D389. Substrate represents non-existence as a positive state, not as a missing row. | Locked. | MCF requirements §14 binding readiness must respect this — a missing fixture for an MCF MC must surface as a positive verdict, not as substrate silence. | Validates MCF requirements §12.6 verifier emitting `structural_reject` rows (which is the "missing fixture / stale fixture" positive verdict pattern). |

### 2.6 L-node semantic gate

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-LNODE-1** D366 (DEC-804874) + bc-core inventory §A | L-node semantic verdict + trace tables exist as schema; **`LNodeSemanticService` does NOT exist**. Service references in comments only. Per CLAUDE.md "D366 L-Node Semantic Gate" is governance-active per session-close gate but no writer found in bc-core. | Tables: `contract.l_node_semantic_verdict` + `contract.l_node_semantic_trace`. Schema columns include `inputHash`, `computedAt`, `agentFlowId`, `verdict`, `verdictDetailJson`. No service writes to them. | Scaffolded only. CLAUDE.md describes the session-close gate as enforcing `contract.l_node_semantic_verdict` rows; if no service writes, the gate effectively fails-open on infrastructure outages (consistent with CLAUDE.md description). | MCF requirements §15.8 cites D366 as integration point. With no service, MCF cannot read meaningful L-node verdicts; would need to either build the service or live with degraded semantic verification. | `l_node_semantic_verdict` + `l_node_semantic_trace`: **keep** (schema sound). `LNodeSemanticService`: **gap**. Adjacent to MCF §14 binding readiness; MCF can ship without it but with reduced semantic-rigor signal. |

### 2.7 Fiscal calendar stack

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-FISC-1** D363 (DEC-1efa47) | Grain key-source mismatch: engine conflated business calendar period with engine runtime context. Fiscal period was being derived from CO.evaluatedAt or scheduler timestamp, not from posting_date resolved via tenant fiscal calendar per legal_entity. | Specimen problem caused incorrect fiscal_period stamping on snapshots; downstream metric aggregations grouped by wrong period. | Resolved at design level via D363+D364+D365 stack. Phase 1 of engine source-awareness shipped (PR #3). | D364 calendar stack + D365 CC enrichment work tasks (TSK-4b22ad, TSK-38365a) are still open per memory `fiscal_calendar_architecture.md`; Phase 2 migration TSK-53edc3 blocked on both. | `FiscalCalendarService`: **keep** (per Phase 1). The remaining D364/D365 work is an MCF prerequisite, not MCF scope per se. Validates MCF requirements §9 computed-dimension resolver-fixture-config requirement. |
| **F-FISC-2** D364 (DEC-d7e7a0) + bc-core inventory §A | The fiscal calendar stack went live: `master.dim_date` (platform), `master.dim_fiscal_calendar` (named catalog), `master.dim_fiscal_period` (per-instance rows), `organization.fiscal_calendar_config` (tenant DB, per legal entity). | Renamed `date_dim` → `dim_date` per D367. `organization.fiscal_calendar_config` moved from platform `tenant.fiscal_calendar_binding` to tenant DB per D368 (tenant self-description is tenant metadata). | Substrate live. `FiscalCalendarService` resolves date into tenant fiscal period across platform + tenant DB. Supports regular, 4-4-5, 4-5-4, 5-4-4, custom variants. | No FK from `organization.fiscal_calendar_config` to `master.dim_fiscal_calendar` (cross-DB soft ref only). No FK to `dim_legal_entity` (deferred to Phase 3). | All fiscal tables: **keep**. `FiscalCalendarService`: **keep**. Cross-DB soft-ref absence is the well-known platform/tenant boundary, not an MCF issue. |
| **F-FISC-3** D365 (DEC-a8e8fc) | CC must declare `posting_date_field` so canonical resolution can stamp `fiscal_period` + `fiscal_year` on payload. Pre-D365, this was missing. | CC enrichment task TSK-38365a covers the CC change. | Decided; implementation status partial (Phase 2 migration TSK-53edc3 still blocked). | If CC `posting_date_field` is not populated for all CCs that MCF MCs will reference, MCF computed-dimension references (§9.2) will fail at runtime. | CC `posting_date_field` enrichment: **adapt** (MCF prerequisite). MCF requirements §9.2 resolver fixture config substitutes for tenant config at verification time but does not replace runtime CC declaration. |

### 2.8 Tenant onboarding / metric binding

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-BIND-1** feedback_runtime_readiness_gate + 7-bucket classification | Sandbox1 AR pilot 14/31 split: 1 fully materialized + 13 snapshot-index-backed + 7 rejected-source-data-blocked + 8 upstream-CC-blocked + 1 formula-blocked + 1 warn-deferred. | The 7 rejected MCs failed on `No values for SUM('<time-elapsed CF>')`; bc-sdg `real-estate-co` profile doesn't generate the time-elapsed source fields these MCs consume. Remediation is SDG profile extension, not CF/BF mismatch fix. | Standing classification. | This evidence is the canonical case study for MCF requirements §12.10 onboarding-triage default-route reversal: package-internal proof (PE-MC-10 fixture pass) limits the search space — failures are most likely outside the formula layer. | Validates MCF requirements §12.10 as not-just-rhetoric — the bucket distribution literally maps to MCF's "tenant data / source / binding / readiness" layers. |
| **F-BIND-2** session_chain_gap_apr13 (Apr 13) | `mc_dependency` table referenced CC names (version-ambiguous) at one point; activation didn't auto-supersede the previous active version. | Resolved via D305/DEC-bebaec version-aware tracing + supersession enforcement. | Resolved. | MCF requirements §4.2 identity tuple + §10.5 supersession discipline encode this rule structurally. | Validates MCF identity discipline (§4) as the right anchor for version reference. |

### 2.9 Metric catalog / metric definition

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-CAT-1** SES-594568 (May 14 2026) | `metric_definition.status_code` is unused as a promotion signal — all 1,216 non-deprecated seeds carry `draft`. The signal "is this promoted to platform?" must be derived via join `contract.metric_contract.metric_definition_id`. | Live lifecycle uses only `{draft, active, superseded}`. Slice (0) plan: persist constants as `body.variables[].value`; KNOWN_CONSTANTS TS map is transitional. | Open: TSK-1f4988 (governed constant registry) and TSK-9ecaee (4 catalog populations cleanup) filed. | MCF requirements §5.2 "metric intent as preserved knowledge" needs to define how it consumes `metric_definition` rows — currently the field is a misleading status signal. | `metric_definition.status_code`: **adapt** (definition of "is promoted" must change). MCF requirements §5 already handles this conceptually via "join to active MC". |
| **F-CAT-2** session_d340_definition_canonical (referenced via memory) | Pre-D340, the metric_definition ↔ metric_contract relationship was ambiguous; multiple contracts per definition was possible. | DEC-ecec75 / D068 + D340 locked: one contract per KPI (714, not per module 80). Forward FK on `metric_contract.metric_definition_id`. Partial unique index for one active per definition. | Resolved. | MCF requirements §4.6 expects this structural relationship; current substrate is compliant. | `metric_contract.metric_definition_id` FK: **keep**. |

### 2.10 Metric knowledge

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-KNOW-1** feedback_no_placeholders + (CLAUDE.md "No Placeholders") | Generic placeholders (`numerator_value`, `denominator_value`) were appearing in `metric_knowledge` fields, looking like real data while carrying zero information. | Standing rule: empty/null > fake. The maturity pipeline exists to fill these gaps properly. | Standing. | MCF requirements §5.2 treats `metric_knowledge` as background knowledge, not authority evidence (not citable as PE-MC-1). The no-placeholder rule must propagate to MCF authoring: panel-proposed content must not include generic templates. | `metric_knowledge`: **keep** (substrate sound). Discipline rule must transfer to MCF panel prompts. |

### 2.11 Metric snapshot (envelope schema, retiring)

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-SNAP-1** bc-core inventory §A + D369 (TSK-b01ab3) | `envelope.metric_snapshot` is retiring; `fact.ms_*_v*` typed projections are replacement per D369. Dual-write period ongoing. | One row per (MC, evaluation, grain bucket). 1:1 with `metric_evaluation`. | Migration in-flight. Comments in source note read-only carve-out + tenant-metric-catalog overlay. | MCF requirements §15 runtime references metric snapshot as evaluation output; needs to specify which table family is authoritative during dual-write. | `envelope.metric_snapshot`: **adapt** (dual-write transition; MCF must declare authoritative side). `fact.ms_*_v*`: **keep** as future authoritative. |

### 2.12 Metric repository (and adjacent fact tables)

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-REPO-1** SES-45e3ba (F-EVAL-2 reference) | `metric.repository` fact-write key alias mismatch with table column. | Resolved (engine fix). | Resolved. | The naming `metric.repository` doesn't appear in current schema (per bc-core inventory §E — not found). The fact-write tables now live as `fact.ms_*_v*` per D369. | No live `metric_repository` table. Historical reference only. |

### 2.13 Metric wizard

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-WIZ-1** BCF inventory G15 reference | `MetricWizardService` was quarantined at controller and service layers (per BCF inventory gap research §9.1). | Verified per BCF inventory gap research. Not promoted to live BCF gap (G15 stays parked). | Quarantined. | MCF requirements §18 operator console explicitly does NOT include a free-form wizard; the formula AST builder (§18.4) is the structurally-composed replacement. | `MetricWizardService`: **stale-deprecate** (no MCF role). Verified retired per BCF G15 disposition. |

### 2.14 Observability of rejections

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-OBS-1** feedback_runtime_readiness_gate (updated 2026-04-29 forensics) | Rejection reasons are persisted to `evidence.evidence_object` (NOT `evidence.evidence_record` — a thin link table that does not hold rejection detail). Earlier 2026-04-29 forensics that called `evidence.evidence_record` the rejection target were wrong. | Sandbox1's 8 historical `metric_rejected` rows live in `evidence.evidence_object` with concrete reasons recovered. `progression.metric_evaluation.archive_key=NULL` is NOT a defect — S3 archiving is env-var-gated. | Substrate is correct. **Unmet:** operator/tooling discoverability — no Inspector field surfaces latest rejection reason; no view joins `progression.metric_evaluation` to its evidence envelope. | MCF requirements §12.6 verifier emits `mcf.metric_self_verification_result` with diff trace. MCF must NOT regress by mirroring the historical evidence_record/evidence_object confusion — should pick one persistence path and stick to it. | `evidence.evidence_object` (for runtime rejections): **keep**. The operator-tooling discoverability gap is bc-admin scope, surfaced in §5. |

### 2.15 Test discipline (cross-cutting)

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-TEST-1** feedback_test_discipline (D082) | Mock-heavy service/controller tests prohibited — they test wiring, not behavior. Test failures must never be ignored as "pre-existing". | Standing rule. | Standing. | MCF requirements §12 self-verification fixture mechanism is precisely an anti-mock pattern — it exercises the package against deterministic inputs, not mocked dependencies. | Validates MCF requirements §12 fixture mechanism as consistent with test discipline. |
| **F-TEST-2** feedback_zero_claims_policy (Apr 28 2026) | No external capability claim unless proven first-hand end-to-end. Specifically: SAP S/4HANA not yet proven via real Published-OData reader chain producing real snapshots. | Standing rule. | Standing. | MCF panel proposes / platform verifies discipline (§12.2) is the structural enforcement of this. PE-MC-10 makes "proven" computable. | Validates MCF requirements §12.2 "AI assertion is not proof" as the right standing posture. |

### 2.16 Session discipline (cross-cutting)

| Source | Failure mode | Historical evidence | Current status | Unresolved risk | Inventory implication |
|---|---|---|---|---|---|
| **F-DISC-1** D268 / DEC-ebf0b4 | 10 session discipline rules locked: no bulk contract chain generation; no cosmetic status changes; one-then-many; independent verification; self-audit at every session close. | Standing. Self-audit at `devhub_session_close`. | Live. | MCF onboarding work must comply: no bulk MC promotions; verify-one-then-many; AI assertion not proof. | Validates MCF panel-proposes-operator-confirms-platform-verifies pattern. |

---

## 3. Substrate inventory

Per-table verdicts. Citations into §2 Failure Evidence Overlay are in the **Cites** column.

### 3.1 Tables MCF requirements §17 plans to use (or proximate analogues already exist)

| Table | Schema | Drizzle path | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|---|---|
| `metric_definition` | `metric` | `src/database/schema/metric/metric-definition.ts` | **keep** | §5 metric intent; §15 (out of MCF scope as carve-out) | F-CAT-1, F-CAT-2 | MCF reads only (background knowledge per §5). `status_code` semantics need clarification (F-CAT-1) but the row shape is sound. |
| `metric_knowledge` | `metric` | (same file) | **keep** | §5 carve-out | F-KNOW-1 | 1:1 FK to metric_definition. No-placeholder discipline transfers to MCF. |
| `metric_contract` | `contract` | `src/database/schema/contract/metric-contract.ts` | **adapt** | §17.1 `mcf.metric_contract` (planned new table) | F-CHAIN-3 | **Naming collision risk — see §6.** MCF plans `mcf.metric_contract` as a new table; existing `contract.metric_contract` covers similar territory. Disposition decision needed: rename / retire / coexist. |
| `metric_contract_version` | `contract` | (same file) | **adapt** | §17.1 `mcf.metric_contract_version` (planned) | F-CHAIN-3 | Versioning substrate sound. Same disposition question as `metric_contract`. Live lifecycle uses only {draft, active, superseded} — F-CHAIN-3. |
| `metric_contract_approval` | `contract` | (same file) | **adapt** | §17.1 implicit (panel run records) | F-CHAIN-3 | Approval audit trail. MCF's `mcf.metric_authoring_panel_run` is richer; this table may be retired or adapted. |
| `metric_binding` | `metric` | `src/database/schema/metric/metric-binding.ts` | **adapt** | §17.1 `mcf.metric_variable_binding` (planned) | F-BIND-2 | Maps CO↔MC; MCF requires variable-level binding to BCF BCs (§6), not CC-level. Existing table is CC-grain; MCF will need finer-grain variable bindings — either extend this table or supersede with a new MCF table. |
| `mc_dependency` | `metric` | `src/database/schema/metric/mc-dependency.ts` | **keep** | §17 external substrate (readiness scheduler owns) | F-READY-1 | MCF authoring registers dependency edges via the scheduler API (per MCF §17 "Tables MCF does NOT need"). Substrate is sound. |
| `mls_state` | `metric` | `src/database/schema/metric/mls-state.ts` | **keep** | §14 MLS substrate integration; D389-D393 absorbed | F-MLS-1, F-MLS-2, F-MLS-3 | D392 ledger live with 1,658 backfilled rows. MCF integrates, not re-implements. |
| `mls_state_event` | `metric` | `src/database/schema/metric/mls-state.ts` (companion) | **keep** | §14 | F-MLS-1 | History table per D392. |
| `mls_trigger_binding` | `metric` | `src/database/schema/metric/mls-trigger-binding.ts` | **keep** | §14 | F-MLS-1 | Declarative wiring. New states are row inserts, not code changes. |
| `intentional_reuse_pattern` | `metric` | (per D391 / Mls14ActivationGate) | **keep** | §14 / MLS-14 inheritance | F-FORM-2 | 3 patterns seeded. MCF AST `variable_ref` must respect this registry. |
| `metric_contract_version_activation_log` | `metric` | (per D391) | **keep** | §14 | F-FORM-2, F-CHAIN-3 | FK to MCV ON DELETE RESTRICT. refusal_codes text[] with GIN index. |
| `readiness_ledger` | `metric` | `src/database/schema/metric/readiness-ledger.ts` | **keep** | §17 external substrate (readiness scheduler owns) | F-READY-1, F-READY-2 | D316 ledger. MCF reads as MLS 15-25 input signal. |
| `chain_status` | `contract` | `src/database/schema/contract/chain-status.ts` | **keep** | §17 external substrate (chain status SSOT owns) | F-CHAIN-1, F-CHAIN-2 | DEC-bebaec lock. 7-link L1-L7 definition. |
| `chain_trace` | `contract` | (same file) | **keep** | §17 external substrate | F-CHAIN-1, F-CHAIN-2 | Per-variable-per-CC-version detail. signature_hash + intentional_reuse_token columns extend for MLS-14. |
| `l_node_semantic_verdict` | `contract` | `src/database/schema/contract/l-node-semantic-verdict.ts` | **keep (scaffold)** | §15.8 D366 integration | F-LNODE-1 | Schema sound; no service writer exists. Verdict storage is ready; activation requires service work (gap). |
| `l_node_semantic_trace` | `contract` | `src/database/schema/contract/l-node-semantic-trace.ts` | **keep (scaffold)** | §15.8 | F-LNODE-1 | Same — schema ready, no writer. |
| `metric_formula` | `metric` | `src/database/schema/metric/metric-formula.ts` | **adapt** | §7 formula AST (planned `mcf.metric_formula_ast`) | F-EVAL-1, F-FORM-1, F-FORM-3 | Stores formula TEXT, not AST. MCF requires structural AST authoring. Migration path: text → AST. |
| `metric_formula_variable` | `metric` | (same file) | **adapt** | §6 variable binding | F-EVAL-1, F-FORM-3 | Stores varCode + role + constantValue (D329). MCF variable bindings are typed and bind-time-checked against BCF. |
| `metric_formula_verification` | `metric` | (same file) | **adapt** | §11.3 panel run + §12 self-verification fixture | F-FORM-1 | Stores Maker-A/Maker-B/Moderator outputs + verdictCode. Close to MCF's `mcf.metric_authoring_panel_run` shape but predates the workbench framing — MCF version adds workbench fingerprint, per-agent transcript uids, etc. |
| `dim_date` | `master` | `src/database/schema/master/dim-date.ts` | **keep** | §9 computed dimensions | F-FISC-2 | D364/D367. Static reference; 2000-2100 seeded. |
| `dim_fiscal_calendar` | `master` | `src/database/schema/master/dim-fiscal-calendar.ts` | **keep** | §9 | F-FISC-2 | Named catalog of calendars. |
| `dim_fiscal_period` | `master` | (referenced by dim-fiscal-calendar) | **keep** | §9 | F-FISC-2 | Per-instance period rows. |
| `fiscal_calendar_config` | `organization` (tenant DB) | `src/database/schema/tenant-db/organization/fiscal-calendar-config.ts` | **keep** | §9 + tenant binding | F-FISC-2 | D368 moved to tenant DB. No FK to master.dim_fiscal_calendar (cross-DB soft ref). |
| `metric_snapshot` | `envelope` (tenant DB) | `src/database/schema/envelope.ts` | **adapt** | §15 runtime evaluation output | F-SNAP-1 | Retiring per D369 / TSK-b01ab3. Dual-write with `fact.ms_*_v*` projections. MCF must specify authoritative read path during transition. |
| `metric_evaluation` | `envelope` + `progression` | (multiple paths) | **keep** | §15 runtime evaluation | F-EVAL-2, F-EVAL-3, F-OBS-1 | 1:N to `metric_snapshot` per ADR-c0290f D8. Rejection envelopes land in `evidence.evidence_object` per F-OBS-1. |
| `evidence_object` | `evidence` (tenant DB) | (per F-OBS-1) | **keep** | §15 implicit (rejection observability) | F-OBS-1 | Hash-chained, append-only. Rich rejection envelopes. MCF reads only. |
| `evidence_record` | `evidence` (tenant DB) | (per F-OBS-1) | **keep** | §15 implicit | F-OBS-1 | Thin context-binding link table — intentionally does NOT hold rejection detail. Common confusion target; MCF must not regress this distinction. |
| `fact.ms_*_v*` | `fact` (tenant DB) | (generated per D210/ADR-2658ff) | **keep** | §15 typed projections | F-SNAP-1 | Future authoritative snapshot store. Generated on contract activation, populated alongside JSONB. |
| `contract.certification_record` | `contract` | (per D283 / per BCF inventory) | **keep** | §11.5 cert-backed authority; §17 Foundation Governance Substrate | F-CHAIN-3 | Shared with BCF as Foundation Governance Substrate. MCF writes rows scoped by MCF `action_code` values per MCF §11.5. |

### 3.2 Tables MCF requirements §17 plans to introduce (do not exist today — gaps)

| Planned table (per MCF §17) | Verdict | Notes |
|---|---|---|
| `mcf.metric_contract` | **gap** | Naming collision with existing `contract.metric_contract` — see §6. |
| `mcf.metric_contract_version` | **gap** | Naming collision risk — see §6. |
| `mcf.metric_contract_revision` | **gap** | New table per MCF §17. Descriptive-only revisions; does not bump identity. |
| `mcf.metric_supersession` | **gap** | Predecessor → successor edges + correction class + operator sub + rationale + panel run uid. Safety net for the immutable-atom model per MCF §10.5. |
| `mcf.metric_variable_binding` | **gap** | Per-MC-per-variable binding to BCF (Entity or BC by id, role, bind-time check results) per MCF §6. Existing `metric_binding` is CC-grain, not variable-grain. |
| `mcf.metric_formula_ast` | **gap** | Serialized canonical AST + formula identity hash per MCF §7-§8. Existing `metric_formula` stores text. |
| `mcf.metric_filter_clause` | **gap** | Per-filter row, set-semantic for identity per MCF §4.5. |
| `mcf.metric_computed_dimension_ref` | **gap** | When an MC references a computed dimension, the governing-config link per MCF §9. |
| `mcf.metric_package_signature` | **gap** | Composite signature hash per MCF §8.7 — added in commit ea14d9a for self-verification fixture binding. |
| `mcf.metric_self_verification_fixture` | **gap** | Per-MC-version fixture body per MCF §12. Added in commit ea14d9a. |
| `mcf.metric_self_verification_result` | **gap** | Per-(fixture, package_signature_hash, verifier_version) deterministic verification record. Added in commit ea14d9a. |
| `mcf.tenant_binding` | **gap** | Per-tenant binding to active MC per MCF §14. MLS 15-25 state integration with D392 substrate. |
| `mcf.metric_publication_eligibility_result` | **gap** | Per-publication PE-MC-1..PE-MC-10 evaluation results per MCF §13. |
| `mcf.metric_authoring_panel_run` | **gap** | Panel run record (workbench fingerprint hash, per-model transcript uids, etc.) per MCF §11.3. |
| `mcf.metric_authoring_panel_transcript` | **gap** | Per-model immutable transcript per MCF §11.3.5. |
| `mcf.workspace_tool_allowlist` | **gap** | Versioned allowlist of tools the workspace exposes per MCF §11.3.3. |
| `mcf.evidence_source_allowlist` | **gap** | Versioned allowlist of evidence sources per MCF §11.3.3. |

---

## 4. Services inventory

### 4.1 Metric evaluation engine

| Service / file | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `src/boundary/metric-evaluation-engine.service.ts` | **keep** (execution layer) + **adapt** (input shape) | §7.6 executable AST + §15.5 (engine preserved) | F-EVAL-1, F-EVAL-2, F-EVAL-3, F-EVAL-4, F-EVAL-5 | Engine itself is sound and benchmarked (3.3ms / 57ms). Input is text-parsed today; MCF requires AST input. Adapt path: accept AST as primary input; preserve text-parsing as legacy fallback. |
| `src/boundary/metric.service.ts` | **keep** + **adapt** | §15 | F-EVAL-1 | Boundary orchestrator — envelope normalization, lookback window, snapshot creation, evidence. Adapt: snapshot creation must hand off to `fact.ms_*_v*` projections post-D369. |
| `src/boundary/metric-evaluation-engine.service.spec.ts` | **keep** | §15.5 | F-EVAL-1 | 241/241 tests pass. Valuable regression coverage. |
| `src/boundary/metric.controller.ts` | **keep** | §15 | — | HTTP surface for `/api/metrics/*`. |

### 4.2 Formula / rule audit

| Service / file | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `src/registry/formula-audit.service.ts` | **adapt** | §7 AST taxonomy + §13 PE-MC-5 | F-FORM-1 | Text-based audit. D315. Banned list: ML_MODEL, QUALITATIVE_ASSESSMENT, STDDEV, SUM_BY_CATEGORY, WEIGHTED_AVG. MCF AST replaces text scan; banned-function decision becomes AST taxonomy decision. |
| `src/registry/formula-deterministic-evaluator.ts` | **adapt** | §7 + §12 deterministic verifier (planned) | F-EVAL-1 | Deterministic AST evaluation logic. Close to MCF requirements §12.6 verifier; reuse with structural-check + fixture-binding wrappers. |

### 4.3 Chain status SSOT

| Service / file | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `src/registry/chain-status.service.ts` | **keep** | §13 PE-MC chain-completeness signals; §15 external substrate | F-CHAIN-1, F-CHAIN-2 | D305 SSOT. Write-through computation. Replaces IntegrityService. |
| `src/registry/chain-status.controller.ts` | **keep** | §15 | F-CHAIN-1 | `/api/registry/chain-status/summary`, `/funnel`, `/list`, `/:metricContractId`, `/refresh`. |
| `src/integrity/IntegrityService` (per CLAUDE.md) | **stale-deprecate** | — | F-CHAIN-1 | Deprecated per DEC-bebaec. Kept for activation gates + per-MC detail views only. Final removal pending consumer-map cleanup. |

### 4.4 Readiness scheduler

| Service / file | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `src/readiness/readiness.service.ts` | **keep** | §14 binding readiness | F-READY-1, F-READY-2 | Three dials: catalog, tenant, binding-candidates. Spec locked SES-b4538a. |
| `src/readiness/readiness.controller.ts` | **keep** | §14 | F-READY-1 | `/api/admin/readiness/catalog`, `/tenant`, etc. |

### 4.5 MLS framework

| Service / file | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `src/mls/mls-state-recorder.service.ts` | **keep** | §14 | F-MLS-1 | D392/D-3 in-process queue + drain worker. record() / recordImmediate(). |
| `src/mls/mls-state-recorder.repository.ts` | **keep** | §14 | F-MLS-1 | Writes to metric.mls_state. Conditional WHERE + read-then-decide. |
| `src/mls/mls-trigger-binding-resolver.service.ts` | **keep** | §14 | F-MLS-1 | Resolves trigger bindings; cascades to dependents. |
| `src/mls/mls-probe-registry.service.ts` | **keep** | §14 | F-MLS-1 | Probe registry for verdict recomputation. |
| `src/mls/mls-backfill.service.ts` | **keep** | §14 | F-MLS-1 | Backfill for MLS substrate. 1,658 rows live. |
| `src/mls/gate/Mls14ActivationGate` + `Mls14SignatureHashService` | **keep** | §14 + §13 implicit (MLS-14 is a runtime gate, not a PE-MC) | F-FORM-2, F-MLS-2 | D391 phased v1 live. 6 of 8 ADR codes emitted. MCF respects this gate. |
| `src/mls/mls-backfill.controller.ts` | **keep** | §14 | F-MLS-1 | `/api/mls/backfill`, `/state-buckets`, `/recent-transitions`, gate evaluate/reevaluate endpoints. |

### 4.6 L-node semantic gate

| Service / file | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `src/l-node/LNodeSemanticService` | **gap** | §15.8 | F-LNODE-1 | Schema exists (l_node_semantic_verdict, l_node_semantic_trace) but no service writer. Per CLAUDE.md the D366 session-close gate fails-open on infrastructure outages — consistent with this gap. |

### 4.7 Fiscal calendar

| Service / file | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `src/registry/fiscal-calendar.service.ts` | **keep** | §9 + §15 | F-FISC-1, F-FISC-2, F-FISC-3 | D364/D368 FiscalCalendarService. Resolves date into tenant fiscal period across platform + tenant DB. Supports regular, 4-4-5, 4-5-4, 5-4-4, custom. MCF computed-dimension resolver fixture config (§9.2) substitutes for tenant config at verification time. |

### 4.8 Onboarding services

| Service / file | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `src/registry/mc-onboarding.service.ts` | **adapt** | §6 binding + §7 AST + §11.3 panel | F-FORM-3 | CR-QG-MC-GRAIN gate works. Header β-path / slice (0) plan filed per SES-594568 — hardcoded tags-as-varcodes and formulaic descriptions at lines 442-443 must be removed before MCF reuses this service. SERVICES-ONLY discipline mandates: extend the service, do not bypass. |
| `src/registry/cc-onboarding.service.ts` | **wrap** (per BCF inventory §2.4) | Out of MCF scope per §2; MCF reads CC version refs | F-FORM-3 | CC composition out of MCF scope. BCF inventory carries the disposition. |
| `src/registry/oc-onboarding.service.ts` | **keep** | Out of MCF scope | F-CHAIN-2 (L4 OC field_mapping gaps) | OC field_map is the L4 chain dependency. Out of MCF scope per MCF §2; the L4 dependency surfaces via chain_status reads. |
| `src/registry/mc-envelope-governance/` (module) | **adapt** | §11.4 operator-confirm + §13 PE-MC | F-FORM-3 | MC envelope validation + approval service (DEC-a17d0f / DEC-b7affa / DEC-889238). MCF's `mcf.metric_authoring_panel_run` + PE-MC publication-gate evaluator subsume this. |

### 4.9 Metric catalog / business catalog

| Service / file | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `src/registry/metric-catalog-reader.repository.ts` | **keep** | §5 metric intent (read-only carve-out) | F-CAT-1, F-CAT-2 | Reads metric catalog: active MCs, definitions, bindings, versions, formulas. MCF reads only. |
| `src/registry/business-catalog.service.ts` | **keep** | §5 | — | Function/subfunction taxonomy. |
| `src/registry/business-catalog.controller.ts` | **keep** | §5 | — | `/api/registry/business-catalog/*`. |
| `src/registry/metric-funnel.service.ts` | **keep** | §14 + MLS overlay | F-MLS-1 | Metric lifecycle funnel; tracks MD→MC progression. Canon source per DEC-a8b33e (not the MLS frame). |
| `src/registry/metric-catalog.controller.ts` | **keep** | §5 | — | `/api/registry/metric-readiness/*`. |

### 4.10 Tenant metrics

| Service / file | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `src/tenant-metrics/tenant-metrics.service.ts` | **keep** | §14 tenant binding | F-BIND-1 | Tenant-side metric catalog. MCF reads as MLS 15-25 input. |

### 4.11 Progression / snapshot index

| Service / file | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `src/progression/metric-evaluation-progression.repository.ts` | **keep** | §15 | F-OBS-1, F-SNAP-1 | Reads/writes progression.metric_evaluation. Mirrors envelope.metric_evaluation (retiring). |
| `src/progression/metric-snapshot-index.repository.ts` | **keep** | §15 | F-SNAP-1 | Indexes metric snapshots for tenant-metric-catalog. |

### 4.12 Metric wizard

| Service / file | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `MetricWizardService` (per BCF inventory G15) | **stale-deprecate** | §18.4 AST builder replaces wizards | F-WIZ-1 | Quarantined per BCF inventory. MCF formula AST builder is the structural replacement. |

### 4.13 Helper scripts (cross-cutting)

| Surface | Verdict | MCF requirements ref | Cites | Notes |
|---|---|---|---|---|
| `bc-core/scripts/*` (160 surveyed per BCF E2) | **default-untrusted** (BCF E2 verdict) | §11.3.3 governed tool allowlist | F-READY-3 | BCF E2 banded into trusted/diagnostic/unsafe/deprecated. MCF must not rely on helper scripts as evidence sources — they fail the per-source-verification rule. Workbench tool allowlist is the structural answer. |

### 4.14 New services MCF requires (gaps)

| Required service (per MCF §17.4 / §20) | Verdict | Notes |
|---|---|---|
| MCF formula AST authoring service (Gate M7) | **gap** | Constructs valid ASTs, runs normalization, computes formula identity hash + composite package signature hash, performs bind-time checks. |
| MCF structural-check engine (Gate M8) | **gap** | C-FX-1..C-FX-11 per MCF §12.5. |
| MCF deterministic verifier service (Gate M9) | **gap** | Executes packages against fixtures, emits `pass | fail | structural_reject` to `mcf.metric_self_verification_result`. Algorithm-versioned. |
| MCF Metric Authoring Panel (Gate M10) | **gap** | Three-model panel; closed-enum verdicts; PE-MC-1 grounding; defect-code taxonomy. |
| MCF PE-MC publication-gate evaluator (Gate M11) | **gap** | Deterministic evaluator for PE-MC-1 through PE-MC-10. |
| MCF supersession service (Gate M13) | **gap** | Operator-initiated supersession with successor pointer; cross-framework from BCF; invalidates predecessor fixture per §12.7. |
| LNodeSemanticService (per D366 / §15.8) | **gap** | Schema exists; service does not (F-LNODE-1). MCF can ship without it with reduced semantic-rigor signal. |

---

## 5. bc-admin / bc-ai consumer map

Identify live callers only; no UI redesign proposed.

### 5.1 bc-admin → bc-core consumer map

| bc-admin surface | bc-core endpoint | Notes |
|---|---|---|
| Readiness pages | `/api/admin/readiness/catalog`, `/api/admin/readiness/tenant?tenant=<slug>` | Live. D316 / SES-b4538a. |
| Chain Status / Funnel | `/api/registry/chain-status/summary`, `/funnel`, `/list`, `/:metricContractId` | Live. DEC-bebaec. |
| Metric Catalog / KPI | `/api/registry/metric-readiness/funnel`, `/mc-list`, `/definition-list`, `/orphan-contracts`, `/chain-detail/:mcId`, `/tenant-data-detail/:mcId?tenant=:tenant` | Live. |
| MLS Substrate Health | `/api/mls/state-buckets`, `/mls/activation-violations` | Live. D392. |
| Metric Definitions | `/api/metric-catalog/definitions`, `/metric-definitions/:contractId`, `/metric-definitions/stats` | Live. MetricRegistrationPage writes here per recent D418 Gate 5.2-C work. |
| Domains / Functions | `/api/metric-catalog/domains/:businessFunction` | Live. |
| Metric Evaluation Stats | `/api/metric-evaluation/stats` | Live. Platform-scope rollup. |
| Seed Catalog | `/api/seed-catalog/metrics/functions`, `/seed-catalog/metrics/stats` | Live. |
| bc-admin Metric Lifecycle page | `/api/mls/platform-funnel` | Live (PlatformTab). Tenant tab + per-MD action list still mock pending Tenant probes. |

### 5.2 bc-admin live callers (file paths)

| bc-admin file | Hooks |
|---|---|
| `src/api/chain-status.ts` | useChainStatusSummary, useChainStatusFunnel, useChainStatusList, useChainStatusDetail, useRefreshChainStatus |
| `src/api/formula-audit.ts` | useFunnelReadiness, useMcListReadiness, useDefinitionReadinessListPages, useOrphanContracts, useChainDetailReadiness, useTenantDataDetail, useTenantFunnelReadiness |
| `src/api/readiness.ts` | useCatalogReadiness, useTenantReadiness, useBindingCandidates, useBind, useFormulaTokenAudit |
| `src/api/mls.ts` (inferred) | useMlsPlatformFunnel, state-buckets, activation-violations |

### 5.3 bc-ai metric consumers

- bc-ai field-map agent (D307) validated against seed catalog data. Not a direct MCF consumer; produces L4 OC field_map enrichment proposals consumed by bc-core OC onboarding flow.
- bc-ai BO verification agent (D201) — BCF scope; not MCF.
- No bc-ai service currently writes to MCF substrate; MCF Metric Authoring Panel (gap, Gate M10) is the planned three-model AI consumer.

### 5.4 Dead-end / quarantined surfaces

- `MetricWizardService` (F-WIZ-1) — quarantined; bc-admin has no live wizard surface.
- `IntegrityService` per-MC detail view path (F-CHAIN-1) — may have residual bc-admin callers; needs verification before MCF onboards. Out of scope for this inventory.
- bc-admin canonical-fields page — retired in D418 Gate 5.2-C (bc-admin PR #15).

---

## 6. Naming-collision risks

### 6.1 Critical collision: `contract.metric_contract` vs `mcf.metric_contract`

**The problem.**

- Today's substrate: `contract.metric_contract` (table) + `contract.metric_contract_version` (table) + `contract.metric_contract_approval` (table). All in the `contract` schema.
- MCF requirements §17.1 plan: `mcf.metric_contract` + `mcf.metric_contract_version` + `mcf.metric_contract_revision` + others. All in a new `mcf` schema.

Both refer conceptually to the same primitive ("the metric contract artifact"). Both will be live simultaneously during any MCF rollout unless explicit retirement is sequenced.

**The three dispositions, descriptively:**

| Disposition | What it means | Cost | Risk |
|---|---|---|---|
| **(a) Coexist with explicit reads/writes routing** | `contract.metric_contract` stays for legacy KPI catalog; `mcf.metric_contract` is the MCF-authored artifact. ChainStatusService and readers must route to the right one per consumer. | Lowest implementation cost. | Persistent confusion. Every consumer must know which contract surface to read. Two SSOTs for "the metric contract". |
| **(b) Rename current to legacy, build new MCF as canonical** | Rename `contract.metric_contract` → `contract.legacy_metric_contract` (or similar). Build `mcf.metric_contract` as the going-forward canonical. Existing services adapt to read both, write only to `mcf.metric_contract` for new content. | Medium. Requires Drizzle rename + service adapt. | Two-table reads are clean and audit-friendly. |
| **(c) Retire current, MCF substrate replaces** | Migrate the meaningful subset of `contract.metric_contract` rows (the 195 "Ready" MDs per F-FORM-2 / 376 active MDs depending on cutoff) into `mcf.metric_contract`. Drop `contract.metric_contract`. Strict greenfield for everything else per MCF §16 migration-free stance. | High. Requires migration script + cutover. Violates MCF §16 "no migration" stance unless framed as "preserve KPI catalog intent only". | Cleanest end state. Single SSOT. Highest disruption. |

**MCF requirements §16 stance.** "There is no migration from the historically-quarantined-now-dropped surfaces." This stance was authored against BF/BO/CF/CM. The `contract.metric_contract` table is NOT historically quarantined — it is in active use today. Strict §16 reading would forbid disposition (c) and require either (a) or (b).

**This inventory's verdict: gap (decision required).** Disposition is a Step 2 / Step 3 decision, not a Step 1 verdict. The disposition affects every Gate from M2 onward and must be locked before substrate-DBCP work begins.

### 6.2 Adjacent collisions

| Existing | MCF planned | Risk level | Disposition note |
|---|---|---|---|
| `metric.metric_binding` (CC-grain) | `mcf.metric_variable_binding` (variable-grain) | Medium | Different grain — can coexist if MCF binding is a strict refinement. Open question: is `metric.metric_binding` retired or kept as a coarse-grained join helper? |
| `metric.metric_formula` (text) | `mcf.metric_formula_ast` (AST) | Medium | Same as F-FORM-1 / F-EVAL-1. Text-to-AST migration path needed. |
| `metric.metric_formula_verification` (Maker A/B/Moderator outputs) | `mcf.metric_authoring_panel_run` + `mcf.metric_authoring_panel_transcript` (workbench-shaped) | Medium | Predates workbench framing. MCF tables are richer. Migration path: archive existing verification rows; new content goes to MCF tables. |
| `contract.metric_contract_approval` (decision audit) | `mcf.metric_publication_eligibility_result` + cert reuse | Low | Approval audit subsumed by PE-MC result records + cert table. Existing rows are historical only. |
| `envelope.metric_snapshot` (retiring per D369) | `fact.ms_*_v*` (typed) | Already in flight | Independent of MCF — D369 disposition continues. MCF requirements §15 must specify which is authoritative during transition. |

### 6.3 Schema-namespace risk

MCF plans a new `mcf` schema. Confirm no name clash with any existing schema:

- Existing schemas in bc-core platform DB: `contract`, `metric`, `runtime`, `source`, `master`, `operations`, `evidence`, `concept_registry`, `mcf`?
- Drizzle path check needed: does `src/database/schema/mcf/*` exist today? Per bc-core inventory §A, no `mcf/*` schema directory was reported. Confirmed clean for greenfield creation.

### 6.4 Service / module name collisions

| Existing | MCF planned | Risk |
|---|---|---|
| `MetricEvaluationEngine` | (MCF reuses) | None — engine is reused per §15.5. |
| `FormulaAuditService` | MCF AST authoring service (Gate M7) | The text-audit role retires when AST is the canonical input. Service path can be renamed or kept as legacy. |
| `MetricWizardService` (quarantined per F-WIZ-1) | MCF AST builder UI (Gate M15) | Quarantined service can be safely removed; MCF UI is greenfield. |
| `mc-onboarding.service.ts` | (MCF extends or supersedes) | Per F-FORM-3, header β-path is needed. MCF authoring service can either be a sibling or a replacement. |

---

## 7. MCF requirement assumptions not yet built — gap surface for Step 2

This list is the input to Step 2 (gap / risk survey). Each item is a thing MCF requirements assume that no current artifact provides.

### 7.1 Formula AST (MCF §7)

- **AST-1.** Closed AST node taxonomy with `variable_ref`, `literal`, `aggregate`, `arithmetic`, `comparison`, `case`, `window`, `time_anchor_resolution`, `bucket_assign`. No current implementation provides this — `metric_formula.formula_text` is text only.
- **AST-2.** Per-node type signature with type-promotion rules (currency × number → currency, etc.). Not implemented at AST level today.
- **AST-3.** AST-shaped storage with serialized canonical form (replaces text storage in `metric_formula`).
- **AST-4.** AST validity gate (PE-MC-5) — deterministic check that AST conforms to taxonomy + type-checks across the AST.

### 7.2 Formula normalization + identity hash (MCF §8)

- **HASH-1.** Normalization rules (commutative operator ordering, constant folding, variable-rename invariance, De Morgan canonicalization, CASE branch ordering, empty-filter elimination, aggregate operand canonicalization). Not implemented.
- **HASH-2.** Structural sort key for commutative-operand ordering.
- **HASH-3.** `formula_intent_hash` substrate-computed + algorithm-versioned (`mcf-formula-hash-v1`).
- **HASH-4.** Composite `package_signature_hash` over (formula AST + variable bindings + grain/filter/temporal/dimension signature). Not implemented; MCF §8.7 introduces.

### 7.3 Self-verification fixtures (MCF §12)

- **FIX-1.** `mcf.metric_package_signature` substrate.
- **FIX-2.** `mcf.metric_self_verification_fixture` substrate.
- **FIX-3.** `mcf.metric_self_verification_result` substrate.
- **FIX-4.** Structural-check engine (C-FX-1..C-FX-11).
- **FIX-5.** Deterministic verifier service (algorithm-versioned).
- **FIX-6.** Stale-fixture rule enforcement (per §12.7).
- **FIX-7.** Resolver fixture config for every computed dimension class (per §9.2 + §12.4 Section C).

### 7.4 PE-MC publication gate (MCF §13)

- **PE-1.** Deterministic evaluator for PE-MC-1 through PE-MC-10.
- **PE-2.** PE-MC-1 grounding (every MC claim cites an authorized source).
- **PE-3.** PE-MC-10 evaluator — cites a passing `mcf.metric_self_verification_result`.

### 7.5 Workbench / Metric Authoring Panel (MCF §11)

- **PANEL-1.** Three-model panel (Maker / Checker / Moderator) with closed-enum verdicts.
- **PANEL-2.** Workbench tool allowlist (per MCF §11.3.3).
- **PANEL-3.** Evidence-source allowlist (per MCF §11.3.3).
- **PANEL-4.** Workbench fingerprint algorithm.
- **PANEL-5.** Per-agent immutable interactive transcript.
- **PANEL-6.** Consensus computation logic on workbench fingerprint equality (per MCF §11.3 + Q34).
- **PANEL-7.** Grounding-check per claim (every claim traces to a tool call in the citing agent's transcript).

### 7.6 Substrate — MCF schema

- **SUB-1.** `mcf.*` schema creation.
- **SUB-2.** `mcf.metric_contract` + identity-tuple UNIQUE per MCF §4.2.
- **SUB-3.** `mcf.metric_contract_version` + immutability trigger on identity-bearing columns when `lifecycle_state='active'`.
- **SUB-4.** `mcf.metric_contract_revision` (descriptive-only revisions).
- **SUB-5.** `mcf.metric_supersession` (predecessor → successor edges).
- **SUB-6.** `mcf.metric_variable_binding` (per-MC-per-variable to BCF Entity or BC).
- **SUB-7.** `mcf.metric_formula_ast` (serialized canonical AST).
- **SUB-8.** `mcf.metric_filter_clause` (per-filter row, set-semantic for identity).
- **SUB-9.** `mcf.metric_computed_dimension_ref` (governing-config link).
- **SUB-10.** `mcf.tenant_binding` (per-tenant + MLS 15-25 integration).
- **SUB-11.** `mcf.metric_publication_eligibility_result` (PE-MC results).
- **SUB-12.** `mcf.metric_authoring_panel_run` + `mcf.metric_authoring_panel_transcript`.
- **SUB-13.** `mcf.workspace_tool_allowlist` + `mcf.evidence_source_allowlist`.

### 7.7 Operator console (MCF §18)

- **UI-1.** MC List (read).
- **UI-2.** MC Detail (read) — surfaces package signature hash + fixture verdicts.
- **UI-3.** MC Draft Edit (formula AST builder).
- **UI-4.** MC Self-Verification Fixture Authoring (Section A/B/C composition; C-FX live feedback).
- **UI-5.** MC Self-Verification Run (verifier verdict + per-row diff trace).
- **UI-6.** MC Publication Confirm (Step A/B/C with PE-MC-10 evidence).
- **UI-7.** MC Supersession.
- **UI-8.** Tenant Binding List + Detail.
- **UI-9.** Panel Run Audit.
- **UI-10.** Cert Audit (MCF action_codes).
- **UI-11.** MLS Operations (Platform + Tenant tabs).

### 7.8 LNodeSemanticService (MCF §15.8)

- **LNODE-1.** Service that writes to `l_node_semantic_verdict` + `l_node_semantic_trace`. Schema exists; service does not (F-LNODE-1). MCF can ship without it with reduced semantic-rigor signal; the D366 session-close gate will continue to fail-open.

### 7.9 Cross-cutting

- **CC-1.** SERVICES-ONLY discipline applied to MCF — no raw INSERTs into `mcf.*` per F-FORM-3 / CLAUDE.md.
- **CC-2.** Helper-script trust model per F-READY-3 — MCF authoring tools must satisfy workbench tool allowlist discipline (no free-form scripts).
- **CC-3.** Test discipline per F-TEST-1 — MCF self-verification fixtures replace mock-heavy service tests.
- **CC-4.** Zero-claims policy per F-TEST-2 — PE-MC-10 makes "proven" computable; no MC may be published without a passing fixture.
- **CC-5.** Foundation invariant preservation per MCF §20.3 — every gate must satisfy I-VI.

---

## 8. Open questions for Step 2 gap/risk survey

Items the inventory surfaces that Step 2 must resolve.

### 8.1 Disposition of `contract.metric_contract`

The single most consequential question. Per §6.1, three dispositions exist:
(a) Coexist with explicit routing, (b) Rename current to legacy, build new MCF as canonical, (c) Retire current, MCF substrate replaces.

MCF §16 migration-free stance was authored against quarantined surfaces, not against this in-use surface. Step 2 must reconcile. **Recommended for Step 2 attention first.**

### 8.2 Fate of `metric.metric_binding`

CC-grain vs MCF's variable-grain binding. Coexist as refinement? Retire after MCF onboarding completes?

### 8.3 Fate of `metric.metric_formula` (text storage)

Strict MCF reading: text storage retires; AST is canonical. Practical reading: text storage may stay as legacy fallback for the engine during transition. Step 2 decides.

### 8.4 LNodeSemanticService — build or defer?

Schema is ready (F-LNODE-1). MCF can ship without it. D366 session-close gate already fails-open. Step 2 decides whether MCF Gate M9 or M10 includes LNode service construction or whether it stays as a separate parallel work.

### 8.5 MLS-14 gate vs PE-MC-10 — overlap or layered?

MLS-14 detects semantic-class collapse via signature_hash. PE-MC-10 detects formula correctness via fixture exercise. Both can detect the MT-04971 case (signature equal + SUM(I1)/SUM(I2)=1 for any I1=I2 inputs).

Layering question: does MCF PE-MC-10 supplement MLS-14 (both gates, both must pass), or does MLS-14 retire in favor of PE-MC-10? Working position: layered (both gates check different surfaces). Step 2 should lock.

### 8.6 D369 envelope.metric_snapshot retirement timeline

MCF §15 must declare authoritative read path during dual-write. Step 2 should coordinate with D369 TSK-b01ab3 cutover schedule.

### 8.7 D386 Stage 1 backfill (temporality_kind)

Per F-MLS-1, MLS-14 phased v2 promotion of `temporality_kind_missing` to BLOCKER depends on D386 Stage 1 backfill. Is this MCF prerequisite or parallel? Step 2 decides.

### 8.8 Helper scripts — band per MCF vs adopt BCF E2 verdicts wholesale?

BCF E2 surveyed 160 scripts and banded them (trusted 38 / diagnostic 67 / unsafe 55 / deprecated 0). 13 active defect surfaces. MCF should either adopt the same banding or do a focused MCF-scope re-survey. Step 2 decides.

### 8.9 bc-admin / bc-ai consumer migration sequencing

The bc-admin readiness, chain-status, MLS, and metric-catalog pages are live consumers. When MCF authoring service goes live, do they continue to read from `metric.*` and `contract.*` substrates, or migrate to read from `mcf.*`? Sequencing matters for cutover risk.

### 8.10 Naming convention for MCF MCs vs legacy MCs

If disposition (a) or (b) per §6.1 is chosen, operators and consumers need a clear naming convention to distinguish MCF-authored MCs from legacy MCs. Working position: `mc__*` continues; provenance is in the substrate (`mcf.*` vs `contract.*`). Step 2 may revisit.

### 8.11 KPI catalog re-authoring program (Gate M20)

MCF §20 Gate M20 is "operational program (not a substrate gate) to re-author KPI intents into MCF MCs". Of the ~1,819 KPIs in `metric_definition`, how many become MCF MCs? What's the prioritization? What's the rate? Step 2 surfaces this; Step 3 plans cadence.

### 8.12 Cross-tenant fixture sensitivity (MCF §19.13 Q42)

For MCs that reference `fiscal_period` (computed dimension), does a single fixture suffice or does each per-tenant fiscal calendar need its own fixture? Working position is per-tenant fiscal-calendar divergence is tenant-binding concern (MLS 15-25). Step 2 may revisit.

### 8.13 Existing `metric_formula_verification` rows — archive or migrate?

These predate workbench framing (F-FORM-3 in spirit). MCF panel run records are richer. Disposition: archive in place + new content goes to `mcf.metric_authoring_panel_run`. Step 2 may revisit.

### 8.14 The 200 MDs in semantic-collapse state (F-FORM-2)

Per `feedback_metric_lifecycle_states`, mdSemanticCollapse 200 as of 2026-05-07. These are pre-MCF and need re-authoring under MCF. Are they part of the M20 re-authoring program scope, or a separate cleanup?

### 8.15 The 7 source-data-blocked + 8 upstream-CC-blocked MCs (F-BIND-1)

Sandbox1 AR pilot 14/31 evidence. These are bc-sdg profile / CC chain coverage issues, not MCF authoring issues. But they are evidence of where MCF's onboarding-triage default-route (per §12.10) will fire repeatedly. Step 2 may want to baseline the count before MCF onboarding to measure the improvement.

---

## 9. Recommended next step

### 9.1 Immediate next: Step 2 gap / risk survey

This inventory is the input. Step 2 should:

1. Take the gap surface (§7) and risk surface (§6, §8) into a structured matrix:
   - Per gap: scope estimate (substrate / service / UI), prerequisite gates, blocker class (foundational / dependent / parallel).
   - Per risk: severity (high / medium / low), likelihood (certain / probable / possible), mitigation pattern.
2. Resolve the disposition of `contract.metric_contract` (§6.1) — this is foundational for every M2+ gate.
3. Resolve the layering of MLS-14 and PE-MC-10 (§8.5).
4. Confirm the D369 cutover schedule (§8.6) and D386 backfill dependency (§8.7).
5. Produce `metric-context-framework-gap-survey.md` in `bc-docs-v3/docs/implementation/` (sibling of this inventory and the requirements doc).

### 9.2 Then: Step 3 MCF build plan

Step 3 converts requirements (1,800 lines) + inventory (this doc) + gap survey into a sequenced build plan. The plan should:

1. Re-ground MCF §20 gates M1-M20 against the actual substrate state and disposition decisions from Step 2.
2. Identify parallelizable gates (the user's framing: M2 identity layer + M7 AST service + M8 fixture substrate + M9 verifier can proceed without rich BCF concept coverage).
3. Flag gates that depend on BCF enrichment (per Step 4): first-real-MC authoring requires BCF concept density.
4. Produce `metric-context-framework-build-plan.md`.

### 9.3 Then: Step 4 BCF enrichment for MCF seed cases

Per the user's framing — bounded by MCF needs, not open-ended. The seed cases are deferrable until the gap survey surfaces what concept density MCF actually requires.

### 9.4 Then: Step 5 MCF implementation

Following the Step 3 build plan, gate by gate.

---

## Document verification

- **Sections present:** 1 (Scope/method/sources), 2 (Failure Evidence Overlay), 3 (Substrate inventory), 4 (Services inventory), 5 (bc-admin/bc-ai consumer map), 6 (Naming-collision risks), 7 (MCF requirement assumptions not yet built), 8 (Open questions for Step 2), 9 (Recommended next step). All 9 required sections present.
- **No code/DB/schema files changed.** This is a docs-only commit.
- **Verdict count summary** (see §10 below).
- **Source-access limitations** (see §11 below).

## 10. Verdict count summary (compact)

### Substrate (§3.1)

| Verdict | Count |
|---|---:|
| keep | 18 |
| keep (scaffold) | 2 |
| adapt | 7 |
| stale-deprecate | 0 |
| gap (planned MCF tables, §3.2) | 17 |

### Services (§4)

| Verdict | Count |
|---|---:|
| keep | 13 |
| adapt | 6 |
| stale-deprecate | 2 (IntegrityService, MetricWizardService) |
| gap | 7 (formula AST service, structural-check engine, verifier service, panel, PE-MC evaluator, supersession service, LNodeSemanticService) |
| default-untrusted (BCF E2 verdict, scripts) | 1 category |

### Total artifacts classified: ~73

## 11. Source-access limitations

- **`devhub_decision_list` output exceeded token limit** (100,502 chars across 985 lines) and was saved to a temp file. Hex-UID mapping was done against the operator-supplied D-number seed list; the temp file was not chunked-read because the operator's seed list (D068/D162/D314/D315/D316/D323/D329/D363/D364/D365/D366/D389-D393/DEC-bebaec/D411/D415/D417/D418/D419) covers the MCF-relevant scope and the hex-UID Glob succeeded against bc-docs-v3 `docs/adrs/`.
- **D314, D315, D316, D323, D329 ADR files** were not surfaced by hex-UID Glob against the seed list. These D-codes are conversational nicknames per the D-code-vs-DEC-UID distinction (D334 / DEC-633b2a in CLAUDE.md); the canonical UIDs are not in the operator's seed list. Substantive content of these decisions was sourced from session memory files (`session_d314_d316_apr14.md`, `session_d323_greenfield_oc_enrichment.md`, `session_metric_engine_apr12.md`) which are point-in-time but cover the same decisions.
- **Session memory files are 23-70 days old.** Reads carry the system reminder "Memories are point-in-time observations, not live state — claims about code behavior or file:line citations may be outdated. Verify against current code before asserting as fact." Inventory verdicts that cite memory-only evidence carry this caveat implicitly; the bc-core implementation inventory (sub-agent report) provides current-state grounding for the substrate and services sections.
- **No live DB query was performed.** Counts cited from `feedback_metric_lifecycle_states.md` (1,241 definitions / 589 contracts / 195 ready / 200 semantic-collapse) are 2026-05-07 point-in-time. Step 2 should re-query if precision matters.
- **bc-ai inventory was not deeply explored.** Only the BO verification agent (D201) and field-map agent (D307) were noted. A focused bc-ai inventory may be warranted in Step 3 when the Metric Authoring Panel build approaches.
- **bc-admin inventory was consumer-map-only** per operator instruction. Component-level UI inventory (which React components consume which APIs) was not produced; Step 3 may need this for UI gates.
- **`l_node_semantic_verdict` schema details** were not directly read in this session beyond the sub-agent report. F-LNODE-1 evidence is sourced from the sub-agent's bc-core inventory; LNode-schema-vs-MCF-§15.8 verification at column level is a Step 2 item.
- **Test discipline cross-cutting (F-TEST-1, F-TEST-2)** was sourced from memory feedback files. A live test-coverage scan in bc-core was not performed; out of scope for this inventory.
