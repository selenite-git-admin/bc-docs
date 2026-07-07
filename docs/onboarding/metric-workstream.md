---
id: metric-workstream
order: 62
title: "Metric Workstream Playbook"
status: drafting
authority: reference
depends_on: [the-invariants, the-evaluation-boundaries, the-contract-grammar, metric-contract-creation, metric-registration, mc-chain-integrity]
governing_sources:
  - bc-docs/docs/foundation/the-invariants.md
  - bc-docs/docs/foundation/the-evaluation-boundaries.md
  - bc-docs/docs/foundation/the-contract-grammar.md
governing_adrs:
  - DEC-ebf0b4 (D268 — Session Discipline Rules)
  - DEC-804874 (D366 — L-Node Semantic Gate)
governing_sops:
  - bc-docs/docs/onboarding/metric-contract-creation.md
  - bc-docs/docs/onboarding/metric-registration.md
  - bc-docs/docs/onboarding/mc-chain-integrity.md
errata_referenced: []
diagrams: []
---

# Metric Workstream Playbook

## Scope and authority

This playbook is reference guidance for metric work; Foundation chapters, ADRs, contracts, and authoritative onboarding SOPs prevail on conflict.

This chapter is an **operational overlay**. It frames metric work as a disciplined flow over the existing authoritative chapters and ADRs. It does not replace them, restate Foundation, or hold peer authority with the foundational invariants or the existing onboarding SOPs.

**Where this chapter conflicts with another source, that source wins.** The conflict order is:

1. `bc-docs/docs/foundation/the-invariants.md` (and the rest of the Foundation chapters).
2. ADRs in `bc-docs/docs/adrs/`.
3. The authoritative onboarding SOPs — primarily `metric-contract-creation.md`, `metric-registration.md`, `mc-chain-integrity.md`, plus their siblings.
4. `barecount-devhub/CLAUDE.md` Foundation Invariant Check (operational reminder of Foundation).
5. This chapter.

When you reach for this playbook, you are looking for *workstream discipline* — what kind of metric work you are doing, what gate applies, what order to investigate, what records to leave behind. Substantive procedure (how to author an MC body, how to register a metric definition, how to run chain-integrity) lives in the SOPs.

## 1. Metric work types

Every metric task fits exactly one of the seven types below. Naming the type before acting is the first move. The work type controls which SOP governs, which gate applies, and whether a Metric Work Record (see §11) is mandatory.

| Type | Description | Primary SOP | Record (§11) |
|---|---|---|---|
| **New MC** | Author a metric contract that did not exist | `metric-contract-creation.md` | Mandatory |
| **MC version bump** | New version on an existing MC (formula, variables, grain, temporal, thresholds, or constants) | `metric-contract-creation.md` + governed version flow | Mandatory if formula/variables/grain/temporal/thresholds change |
| **Tenant or system onboarding** | Bind an existing MC to a new tenant or source system | `metric-contract-creation.md` §boundary; `tenant-metric-binding.md` (sibling) | Mandatory per (tenant, MC) onboarding |
| **Rejected-evaluation investigation** | Understand why a metric evaluation rejected or produced unexpected values | `mc-chain-integrity.md` | Mandatory when the investigation concludes with a decision (including "no change") |
| **Grammar or evaluator extension** | Extend metric-v* schema or `MetricEvaluationEngine` capability | A new ADR is also required | Mandatory |
| **Projection or storage bug** | Bug in `fact.ms_*`, snapshot index, dual-write semantics, or read filters | The relevant bc-core code path; no SOP in the readiness baseline | Mandatory if it changed semantic behavior, optional if pure plumbing |
| **Stale measurement cleanup** | Cleanup of stale metric snapshots, orphaned fact rows, or measurement-state drift | DBCP if no service surface; otherwise the relevant service | Mandatory whenever a DBCP is authored, applied or not |

If a task feels like it spans two work types, split it. Each split has its own gate and its own record.

## 2. Foundation Gate for metric work

This section is **derivative of `CLAUDE.md` §Foundation Invariant Check** (which is itself derivative of `the-invariants.md`). It is reproduced here for usability so an operator working through this playbook gets a self-contained gate. If this text drifts from CLAUDE.md or Foundation, the upstream sources win.

### Apply this gate before any metric work in the seven types above

| Question | Form |
|---|---|
| **Which boundary does the work touch?** | Always Metric evaluation — the third of four boundaries in `the-evaluation-boundaries.md`. Adjacent boundaries (Canonical, Action) may also be touched in tenant onboarding or DAG work. |
| **What is the repair location?** | One of: A (source / SDG), B (contract semantics), C (mapping / binding), D (evaluation boundary implementation), E (storage / projection), F (read model / diagnostics). Pair allowed (e.g. B+D). |
| **Why this location?** | What is wrong or missing at this layer. |
| **Why not upper layers?** | If chosen layer is C–F, confirm A and B are not underspecified. If A or B is underspecified, the fix at C–F is compensation — stop. |
| **Why not lower layers?** | If chosen layer is A–B, confirm no working implementation is being bypassed. |

### Six invariants pre-check (text from `the-invariants.md`)

| # | Invariant | Question for metric work |
|---|---|---|
| I | Meaning is evaluated once | Will the proposed change produce, modify, or reinterpret meaning outside the metric evaluation boundary? If yes, stop. |
| II | Object ordering is fixed | Will the metric snapshot derive from anything other than preserved Canonical Object versions (or governed upstream Metric Snapshots)? If yes, stop. |
| III | All state is immutable | Will the change rewrite an existing Metric Snapshot, MC version, or evaluation in place? If yes, stop and ship a new MC version instead. |
| IV | All references are explicit | Does every reference name a specific contract version, CO version, anchor expression — no implicit head-of-stream or wall-clock references? |
| V | Evaluation is non-replayable | Will re-evaluating the same inputs at a later moment yield a new Metric Snapshot version with its own Evidence and Lineage? |
| VI | Evidence is emitted, not inferred | Does the new behavior emit Evidence + Lineage synchronously with the evaluation act? Audit relies on preserved proof, not reconstruction. |

### Hard rules — derived from the invariants, restated for metric work

- **No SDG / source compensation.** Do not tune the SDG generator, alter source observation, or shape admission to make a metric land at a target number. SDG emits source reality; tuning it produces meaning at the wrong boundary (Invariant I). If the metric is "wrong" by storyboard, the gap is in B (contract semantics) or upstream availability of inputs, not in source reality.
- **No fact / read-model compensation.** Do not add a filter to `FactReaderService`, an inspector projection, or an admin endpoint to alter the value the metric appears to have. Reads do not produce meaning (`the-evaluation-boundaries.md` §boundary-independent rules). If the value is wrong at the surface, fix the producing boundary.
- **No raw DB edits.** No `UPDATE`, `INSERT`, `DELETE`, or `TRUNCATE` against `metric.*`, `progression.metric_*`, `fact.ms_*`, or `contract.metric_*` outside a governed service call. If a service does not exist, propose the smallest DBCP for explicit approval — never apply unilaterally.
- **If the fix would violate Foundation, stop and present the violation** rather than the fix. The override path (D366-style: ≥40-char rationale in `self_audit_json.foundation_gate_override` plus an auto-spawned follow-up task) records a violation or accepted exception; it does not make the behavior foundationally correct.

### Gate output

State the gate result before starting work. The Metric Work Record template (§11) captures it in a structured form.

## 3. Metric Work Sequence

Every piece of metric work, regardless of which of the seven types it falls under, runs through this ordered sequence. The earlier steps gate the later ones. Skipping a step is the most common shape of the anti-patterns enumerated in §10.

1. **Define metric meaning first.** What does the metric measure, in business vocabulary? What is the unit, the direction, the cadence? The semantic must be expressible without referencing any specific source-system shape, fact-table column, or tenant. If the definition reads naturally only against Apex/SAP, the meaning is too narrow — generalize before continuing.

2. **Find existing artifacts before creating or changing fields.** Before authoring a new Canonical Field, Business Field, Business Object, `cc_field_mapping` row, `metric_binding` row, or MC variant, search the registry exhaustively. Most metric needs are served by reuse, not authoring.
   - Existing Metric Contracts that already compute this or an adjacent semantic: `contract.metric_contract` + `metric_contract_version.contract_json`.
   - Existing Canonical Fields by intent: `contract.canonical_field` filtered by `function_code` / `subfunction_code` / `role` / name regex.
   - Existing Business Fields by intent: `contract.business_field` filtered the same way.
   - Existing `cc_field_mapping` coverage on the candidate CCs.
   - Existing `metric_binding` rows linking MCs to CCs.
   - Existing `evidence.evidence_object` entries that may already explain a prior decision on the same field or metric.

3. **Before changing any CF / BF / mapping, run impact analysis.** Treat field-level changes as architectural. Every change has downstream consequences that may render existing snapshots untruthful or break active bindings.
   - Every MC referencing the field (`metric_binding` + `contract_json.body.variables` + `contract_json.body.co_bindings.fields_used`).
   - Every CC mapping the field (`cc_field_mapping`).
   - Every active tenant binding consuming any of the above (`tenant.contract_binding` where `is_active=true`).
   - Existing `progression.metric_evaluation` and `progression.metric_snapshot_index` rows that were produced under the current semantic.
   - Dashboards, reports, and the active storyboard that reference the metric.
   - Whether old snapshots remain *truthful* — i.e., would they have computed differently if produced under the proposed change? If yes, the change is a semantic mutation; the old version must be preserved and a new version authored (Invariant III).

4. **Check whether the declared MC grammar baseline can express the metric.** Read `metric-v1.schema.json` and `MetricEvaluationEngine`'s operator set. If the metric requires a temporal window, an as-of anchor, a per-variable selection, or any operator outside the grammar/engine baseline, the work is a grammar/evaluator extension (work type 5) — not an MC authoring task. Authoring an MC that declares semantics the engine cannot honestly evaluate is the anti-pattern in §10.

5. **Check whether the mapped CCs truly produce the declared semantic.** The MC's variables reference CFs (DEC-d72560). Each CF must be produced by at least one bound CC's `cc_field_mapping` *and* the mapping's `resolution_rule_code` must produce the value the CF's semantic actually means. A CF named `outstanding_receivables_amount` mapped from `receivable_hdr_amount` with rule `sum` over an append-only CC yields cumulative-through-anchor, not outstanding. Honest semantic alignment is the gate before evaluation, not after.

6. **Only after 1–5, consider where the work belongs.** Source / SDG (A), contract semantics (B), mapping / binding (C), evaluation boundary (D), storage / projection (E), read model / diagnostics (F). The Foundation Gate (§2) names the repair location. If 1–5 surfaced a gap above the originally suspected layer, the layer changes — and a Metric Work Record is mandatory for the layer-redirect (§11 trigger 7).

7. **Prove on one tenant / MC / version before scaling.** D268 Rule 4 in operational form for metric work: a change must produce a verified end-to-end result for one (tenant, MC, version) tuple before the same change is applied across many. Bulk MC authoring, bulk tenant binding, and bulk re-evaluation are all D268 Rule 1 violations until the one-then-many proof is in hand.

8. **Leave a Metric Work Record when thresholds are met.** See §11. The record is the orientation artifact for whoever picks up the same metric next — including a future AI assistant working without conversation history.

The sequence is invariant. The work types in §1 differ in *which steps they emphasize*, not in whether the steps apply.

## 4. Contract-first rules

Foundation makes one claim that drives every metric workstream: **business meaning is produced at the metric evaluation boundary by applying a Metric Contract to preserved Canonical Object versions.** Everything else is preservation, projection, or display.

| Rule | Statement |
|---|---|
| **MC grammar owns metric meaning** | The MC body is the contract for what the metric means. Body keys: `input_type`, `formula`, `variables`, `co_bindings`, `temporal_gate`, `unit`, `direction_code`, `thresholds`, `grain` (per `metric-contract-creation.md` §body keys). Meaning lives here. |
| **MC variables reference Canonical Fields, never source/fact columns** | Per DEC-d72560: `variables[].field_code` is a registered CF name. BF names, fact-table column names, and source-system technical names are not admissible at the MC layer. |
| **Fact tables are projection, not semantic authority** | `fact.ms_<mc>_v<ver>` is a typed, queryable projection of preserved Metric Snapshots. Its column shape is derived from the MC version (output → `value`; grain → grain columns). The MC does not get changed to match what the fact table is shaped like; the fact table is rebuilt when the MC's grain or output changes. |
| **SDG emits source reality** | The synthetic generator's job is to emit deterministic, contract-compliant source state. It is not the platform's compensating layer. The same MC must work on any source system that produces equivalent semantic inputs — the cross-system portability test. |
| **New meaning requires a new MC version** | A change to formula, variables, grain, temporal semantics, or threshold values is a new MC version (Invariant III). Active versions are immutable. The platform supports D305 deferred-supersession (48h window) for safe rollover. |
| **Aggregation is owned by the formula** | Per DEC-35b34b, the metric formula owns aggregation. `cc_field_mapping.resolution_rule_code` is documentary at the MC layer. The MC author reads CC mapping rules as canonical-evaluation discipline; the metric value comes from the formula. |
| **Grain is explicit on the MC** | Per CR-MC-008, grain is declared on the MC body; it is never implicit from the CC. The MC may be coarser than the CC (quarterly MC from monthly CC) but never finer. |

## 5. Live Metric Contract Safety Workflow

A live MC version is one that has been activated (`governance_state_code = 'active'`) for any tenant, has produced at least one Metric Snapshot, and is referenced by at least one consumer (dashboard, report, storyboard, alert, downstream metric DAG, or audit). The platform's caller surface and historical evidence chain depend on its semantic remaining exactly what it was at activation.

The Live MC safety rules are derived directly from Invariant III (immutability), Invariant IV (explicit references), and DEC-d72560 / D305 / D366.

### Hard rules for live MCs

- **No in-place semantic mutation.** The following are *semantic* and may not change in place: formula text, variables (codes, roles, field_codes, values, descriptions of intent), grain (keys, sources, field_codes), temporal semantics (temporal_gate, any input_selection field once that grammar lands), unit, direction_code, threshold values, threshold operators, and co_bindings (canonical contracts, roles, fields_used). Cosmetic-only changes — display_name, owner metadata, tag list, description prose that does not change meaning — are permitted on the existing version's header only by the explicit metadata-update path.
- **New meaning requires a new MC version.** The smallest semantic change ships as a new version via the governed createVersion + activate flow (`metric-contract-creation.md` step 9). D305 deferred-supersession (48h window) covers the rollover; prior versions are superseded, not deleted.
- **Tenant-specific fixes must not alter shared MC semantics.** A bug surfaced by one tenant does not justify mutating the MC for all tenants. Three paths are available: (a) per-tenant override via `tenant.contract_binding.override_json` for the keys the schema marks as `x-governance: overridable`; (b) a new MC version that all tenants opt into through new bindings; (c) a tenant-specific MC if the semantic genuinely differs (rare; usually a smell). Mutating the active MC in place is never one of the paths.
- **No retroactive re-evaluation of historical snapshots.** Per Invariants III and V, prior Metric Snapshots remain valid as authored. If they are wrong by some new standard, the new standard ships as a new MC version and produces new snapshots going forward. The old snapshots are not rewritten.

### Required workflow when modifying anything about a live MC

This workflow runs before any authoring action that touches the contract version itself or a binding that consumes it.

1. **Confirm liveness.** Query the active version(s) (`contract.metric_contract_version` where `governance_state_code='active'`). Identify the consumer surfaces: active tenant bindings (`tenant.contract_binding`), referenced storyboards / dashboards / alerts, downstream secondary metrics whose `input_type='secondary'` references this MC's output.
2. **Run impact analysis across:**
   - Active `tenant.contract_binding` rows for this MC + version.
   - `progression.metric_evaluation` and `progression.metric_snapshot_index` rows in every bound tenant DB — counts, max evaluated_at, distribution by status.
   - `fact.ms_<mc>_v<ver>` row counts per tenant + most recent snapshot dates.
   - Dashboards / reports / storyboards referencing the metric (search storyboard docs and bc-portal/bc-admin sources).
   - ADRs and Metric Work Records that bind to this MC.
   - Existing rejection patterns on this MC (`evidence.evidence_object` where `evidence_type='metric_rejected'`).
3. **Reproduce on one tenant or system first.** Pick the tenant most likely to surface the issue. Walk the change through the new MC version flow on that tenant only. Verify via `admin/test-bench/evaluate-mc-for-tenant` that the new version produces the intended result.
4. **Verify non-regression on at least one already-working tenant.** Run the new MC version against a tenant where the metric was already producing accepted snapshots under the prior version. Confirm the new version still produces accepted snapshots (the value may differ — that is intended — but rejection or evaluation errors are not acceptable as regression).
5. **Stage the rollover.** Activate the new version. D305 sets the prior version's `supersede_after = now() + 48h`. During the window, both versions remain queryable; downstream consumers using version-pinned bindings can roll forward at their own cadence.
6. **Leave a Metric Work Record (§11).** Mandatory for any version bump that touches formula, variables, grain, temporal semantics, or threshold values. Cosmetic-only metadata bumps are exempt.

### What this workflow forbids

- Editing `metric_contract_version.contract_json` directly via DB or service to "fix" a live version.
- Mass-binding a new version across all tenants in one move before the one-tenant proof is recorded.
- Treating a tenant's binding change as a substitute for a new MC version when the semantic is shifting.
- Backfilling prior snapshots under the new semantic (Invariant III).
- Closing the session without recording which tenants are assigned to the new version and which remain on the prior version during the D305 window.

The workflow is heavier than authoring a brand-new MC. That weight is the price of preserving historical truth — every prior snapshot remains exactly what it meant when produced.

## 6. Service-first diagnostic order

When investigating a metric — rejection, unexpected value, missing snapshot, drift — the inquiry walks down the stack from operator-facing service surfaces toward raw storage. Raw SQL is the last step, and read-only unless approved.

| Order | Surface | What it answers | Notes |
|---|---|---|---|
| 1 | `POST /api/admin/test-bench/evaluate-mc-for-tenant` | Did the metric evaluate? Status `accepted` / `rejected` / `errored`? How many input COs? Snapshots produced? | The fastest end-to-end check for a tenant-bound MC. |
| 2 | `evidence.evidence_object` (tenant DB) | What did the engine actually decide? Rejection reasons, failed checks, per-grain detail, grainResults, rejectedGroups. | The authoritative evaluation outcome record. Per Invariant VI, this is *primary* — not a debugging log. |
| 3 | `metric.readiness_ledger` (platform DB) | Did the readiness ledger record a metric_snapshot for this (MC, tenant, period)? Was it superseded? | Confirms the cross-run dispatch path saw the work. |
| 4 | `contract.chain_status` + `contract.l_node_semantic_verdict` (D305 + D366) | Is the chain structurally complete? Are L-node semantic verdicts green? | Catches contract-side breaks (missing CF, broken binding, semantic-family violation) before drilling further. |
| 5 | `progression.metric_evaluation` + `progression.metric_snapshot_index` (tenant DB) | What progression rows exist for this MC + tenant? Do they match the fact rows? | Verifies the snapshot-index ↔ fact alignment closed by commit `3969849`. |
| 6 | `fact.ms_<mc>_v<ver>` (tenant DB) | What did the projection actually store? Value column populated? Grain columns populated? | Verification, not authority. If fact disagrees with evidence, evidence wins; the gap is a projection bug. |
| 7 | Read-only SQL into `progression.canonical_evaluation`, admission, source admission | Did the upstream COs arrive at all? Were they accepted? | Final fallback when service surfaces are inconclusive. **Read-only.** |

**Raw SQL writes (UPDATE / DELETE / INSERT) are forbidden without a governed-service check first.** If a service does not exist, the next step is a DBCP draft for explicit user approval — never an applied write.

## 7. Runtime readiness gate

A metric is *contract-eligible* (passes the 16 CR-QG-MC-001 checks) the moment it is authored. A metric is *runtime-ready* only when six additional conditions hold for the (tenant, MC, version) tuple. Confusing the two is a common drift; this gate is the antidote.

| # | Condition | How to check |
|---|---|---|
| 1 | **Tenant binding active** | `tenant.contract_binding` has an active row for (tenant_id, contract_id=mc_id, version_code, contract_family='metric'). |
| 2 | **Upstream CC accepted COs exist** | For every CC referenced by `metric_binding`, at least one accepted CO exists in the tenant's `progression.canonical_evaluation` for the period of interest. |
| 3 | **Fact table provisioned** | `fact.ms_<mc_code>_v<ver>` exists in the tenant DB. Provisioned by `POST /api/schema-provisioner/nightly-reconcile` after MC activation. |
| 4 | **Engine supports the formula/operator set** | Every operator and grammar feature referenced by the MC envelope is implemented by `MetricEvaluationEngine`. New grammar = grammar/evaluator extension work type (§1). |
| 5 | **Rejection evidence is recoverable** | Rejected evaluations write `evidence.evidence_object` with structured failed-check detail; the dual-write writes nothing to `fact.ms_*` (Invariant VI + commit `3969849`). |
| 6 | **Prior rejections understood** | If the MC has been evaluated before and rejected, the rejection reason is captured in a Metric Work Record (§11) before the next evaluation attempt — no "re-run until green". |

A metric that fails any of #1–#5 is **not runtime-ready** regardless of its contract eligibility. Onboarding-time confirmation of all six is part of the Tenant/system onboarding work type.

## 8. Balance vs flow measures — temporal discipline

This section captures the lesson that the DSO design surfaced. It generalizes; DSO is the worked example.

### Two kinds of measure

| Kind | Meaning at a point in time | Aggregation rule |
|---|---|---|
| **Flow** | A flow accumulates events over a window. The window has a start and an end; the value is "how much happened in (start, end]". | Sum (or other flow-friendly aggregator) over events whose timestamp falls in the window. |
| **Balance** | A balance is a point-in-time state. It has only an *as-of* anchor, not a window. The value is "what was true at the anchor". | Selection of records *authoritatively open* at the anchor. Not a sum over events. |

Sales, expenses, payments, units shipped, support tickets opened, hours worked — flow.

Accounts receivable balance, inventory on hand, accounts payable balance, cash position, open headcount, unresolved tickets — balance.

A metric that mixes the two — DSO is the canonical example, also DPO, DIO, cash conversion cycle, AR aging ratios, inventory turnover — needs both temporal semantics declared at the variable level.

### Honest rules

- **Same-period ratio is not a balance metric.** `(SUM(receivable) / SUM(invoice))` per fiscal_period collapses both sides to the same flow shape. For DSO the result is structurally `≈ per-row AR/invoice ratio × days_in_period` (≈35–38 days for typical tax/markup ratios), regardless of arrears distribution. This is what `mc__days_sales_outstanding` v1.2.0 computes.
- **`posting_date ≤ anchor` is cumulative-through-anchor, not open-at-anchor.** A cumulative-through-anchor sum includes paid items if the CC is append-only and there is no clearing event. For balance metrics this is wrong.
- **`over_trailing_window` is valid for flow measures.** Credit sales, expenses, ticket open events — all flow. A trailing 90-day window is well-defined: events whose `posting_date ∈ (anchor − 90d, anchor]`. Engine implementation is straightforward.
- **`at_period_end` for balance measures requires upstream open/as-of semantics.** Three paths can carry the semantic:
  1. **Open-item CC family** — a separate CC (e.g. `cc__receivable_open_item`) whose COs *are* the open positions, not the underlying postings. Clearing emits a different CO (cleared item) in a separate family.
  2. **Clearing-by-supersession** — clearing is a new CO version whose Lineage references the original. The engine resolves "open at anchor" by checking each candidate CO against its supersession chain at the anchor date.
  3. **Bitemporal effective_from / effective_to** — CCs carry effective-dating columns. Selection is `effective_from ≤ anchor < effective_to`. Standard bitemporal pattern.
- **No `Date.now()`, no implicit head-of-stream semantics.** The anchor expression is contract-declared (`grain.<key>.{start,end}` or `evaluation_period.{start,end}`). Wall-clock and read-time-current are out of bounds (Invariants IV and V).
- **Evidence must record temporal selection.** Per-variable: `kind`, `anchor_expression`, resolved `anchor_date`, `window_start`/`window_end` (for windows), `selected_co_count`, the `selector_rule` applied. Rejected groups carry the same block when rejection is selection-driven.

### Boxed lesson

> **Phase-1 of any temporal-metric grammar extension may add `over_trailing_window` for flow measures. Realistic balance metrics (DSO, DPO, DIO, inventory-on-hand, cash position) remain blocked until open-item / as-of semantics exist on the upstream canonical contract.**
>
> Do not market a metric as "realistic DSO / DPO / DIO" if the as-of side is computed by `posting_date ≤ anchor` over append-only CCs without clearing semantics. The number it produces is cumulative-through-anchor, which is mathematically distinct from open-balance-at-anchor.
>
> Storyboard numbers that depend on the balance interpretation cannot be delivered by the grammar alone. They require the open-item canonical-contract work tracked in the relevant successor ADR.

This box generalizes to every balance measure on every storyboard. DSO is the first case we ran into; it will not be the last.

## 9. Checklists

The lists below are *operational* — they don't replace the SOPs' procedural steps. They are the per-workstream gate questions an operator answers before, during, and after.

### 9.1 New MC checklist

- [ ] Metric definition registered (per `metric-registration.md`).
- [ ] Foundation Gate completed: layer B; six invariants pre-check passed.
- [ ] Variables reference registered CFs (DEC-d72560). No BF or source-column names.
- [ ] Output BF registered with `source_standard: computed` (per `metric-contract-creation.md` Step 4).
- [ ] Grain declared explicitly on the MC body (CR-MC-008).
- [ ] Temporal-window semantics, if any, declared in `input_selection` (post-phase-1 grammar) — not in formula text or constants.
- [ ] If a balance measure: confirmed that an open-item / as-of CC exists for the binding. If not, escalate — this is a B+A predecessor problem.
- [ ] All 16 CR-QG-MC-001 quality gates pass at preview.
- [ ] Tenant binding plan documented (which tenants get this MC, when).
- [ ] Metric Work Record (§11) drafted.

### 9.2 MC version bump checklist

- [ ] Foundation Gate: layer B; new version is a new contract version, not in-place mutation (Invariant III).
- [ ] Change scope identified: formula / variables / grain / temporal / thresholds / constants / metadata-only.
- [ ] D305 deferred-supersession path used (48h window). Prior version is superseded, not deleted.
- [ ] Compatibility check at `POST /api/contracts/{id}/versions` — meta-schema, compatibility, version-increment.
- [ ] Activation path: `POST /api/contracts/{id}/versions/{v}/activate` — passes integrity gate (D305) and L-node gate (D366).
- [ ] If grain or output changed: new fact table provisioned by `nightly-reconcile` before first eval.
- [ ] Tenant bindings reviewed: does the new version need explicit binding rows, or is the binding version-pinned?
- [ ] Metric Work Record (§11) drafted if the change is formula / variables / grain / temporal / thresholds (skip for cosmetic-only).

### 9.3 Tenant or system onboarding checklist

- [ ] Foundation Gate: usually layer C (binding). Confirm A and B aren't blocking — does the source system actually emit the data the MC's CFs need?
- [ ] All six Runtime Readiness conditions (§7) achievable for this (tenant, MC).
- [ ] Source / Reader / Admission contracts active in the tenant's environment.
- [ ] Upstream CC contracts active and emitting COs for the tenant.
- [ ] `cc_field_mapping` coverage verified for every variable's CF in every bound CC.
- [ ] `tenant.contract_binding` row created.
- [ ] Fact table `fact.ms_<mc>_v<ver>` provisioned (`nightly-reconcile`).
- [ ] First evaluation run via `admin/test-bench/evaluate-mc-for-tenant`; result inspected.
- [ ] Metric Work Record (§11) drafted, including a cross-system portability note for the new source-system shape.

### 9.4 Metric rejection investigation checklist

- [ ] Capture the `metric_evaluation_id` and `evidence.evidence_object` row for the rejection.
- [ ] Read structured rejection reasons + failed checks directly from evidence — do not reconstruct from logs.
- [ ] Walk the service-first diagnostic order (§6) from step 1 → step 7; stop at the first surface that explains it.
- [ ] Classify the cause: input-availability (A), contract semantics (B), binding (C), engine (D), projection (E), read (F).
- [ ] If the cause is contract semantics gap (B): do not retry-until-green. Author MC version bump or escalate to grammar extension.
- [ ] Confirm prior rejections for this (MC, tenant) are also explained, not stacked.
- [ ] Metric Work Record (§11) drafted, even if the decision is "no change — this is correct behavior".

### 9.5 Grammar or evaluator extension checklist

- [ ] Foundation Gate: layer B+D (contract grammar + engine implementation).
- [ ] ADR drafted in `bc-docs/docs/adrs/` — grammar extensions are always architecturally significant.
- [ ] New grammar fields are additive and version-gated (`$contract: barecount/metric/v<major>.<minor>`); existing MCs unaffected.
- [ ] No `Date.now()`, no implicit head-of-stream reference; every reference is contract-declared.
- [ ] Engine extension behind the same version gate; v1.0 evaluation path bit-identical to the readiness baseline.
- [ ] Evidence enrichment is additive; existing JSON consumers unaffected.
- [ ] Test plan covers v1.0 regression + new grammar features + cross-system portability + Foundation-Gate validation (grep for `Date.now()`, replay determinism).
- [ ] Metric Work Record (§11) drafted, linked to the ADR.

### 9.6 Temporal metric checklist

Use this whenever a metric's semantic involves a window, an anchor, or a balance-vs-flow distinction.

- [ ] Each input variable classified as flow or balance.
- [ ] Flow variables use `over_period` (default) or `over_trailing_window` selection.
- [ ] Balance variables require upstream open-item / as-of semantics. If not yet available, the metric is not phase-1-evaluable; escalate to ADR-tracked predecessor work.
- [ ] Anchor expressions reference declared grain or evaluation_period only.
- [ ] Window length is contract-declared (integer days); no defaults that read from elsewhere.
- [ ] Evidence records per-variable selection block (§8).
- [ ] Cross-system portability check: does the same MC produce the right semantic on a second source system, or does it implicitly depend on Apex/SAP shape?

## 10. Anti-patterns / stop conditions

If you observe yourself doing one of these, stop and surface the violation. Each maps to an invariant or hard rule.

| Anti-pattern | Why it is wrong | Right move |
|---|---|---|
| Tuning the SDG generator to make a metric land at a storyboard number | Produces meaning at the source layer (Invariant I). The metric becomes correct only against tuned data. Cross-system portability collapses. | Fix the contract (B). If the metric is "wrong", the gap is in semantics, not in source values. |
| Writing a metric formula that names a fact-table column or source-system column | Couples the metric to one source system's shape. The same MC can no longer onboard a second source. | Use a Canonical Field (DEC-d72560). If no CF expresses the needed semantic, register one or pick an existing one whose semantic fits. |
| Adding a read filter on `FactReaderService` or admin endpoints to change the value the metric appears to have | Read-time computation produces meaning at the surface layer (Invariant I, §boundary-independent rules). | The producing boundary is wrong. Fix it. |
| Drafting and applying a DBCP without checking whether a service surface exists | Bypasses governed mutation (D162, Database Change Protocol). | Map the desired change to a service first. DBCP is the last resort, requires explicit user approval, and is recorded. |
| Re-running an evaluation until it returns `accepted`, treating green as success | Ignores Evidence; trades correctness for status (Invariant VI). | Read the rejection reason in `evidence.evidence_object` and address it. |
| Treating `progression.metric_snapshot_index` as if it were value storage | The index is a lookup helper; the fact row is the projection; the evidence row is the authority. Confusing them masks gaps. | Use the service-first diagnostic order (§6): evidence first, ledger next, index/fact for verification. |
| Using cumulative-through-anchor as a stand-in for open-balance-at-anchor | A flow approximation of a balance metric. Mathematically distinct. Honest only if labelled and constrained. | If the metric needs balance semantics, do not ship until open-item / as-of semantics exist upstream. |
| Adding grammar the engine cannot honestly evaluate | A declared semantic with no implementation is a false advertisement; the engine will silently approximate or quietly fall back. | Grammar and engine extensions land together (B+D pair). Phase-gate by `$contract` version. |
| Closing a session with "tests pass" but Foundation Gate violations un-recorded | D268 Rule 7 + D366 override mechanic exist precisely so violations are visible. | Record the override (≥40-char rationale) and auto-spawn the follow-up task; do not bury. |

## 11. Metric Work Records

A Metric Work Record is a short, structured orientation document that lets a future operator, support engineer, or AI assistant understand what happened in a piece of metric work *without replaying chat history*.

### What a record is — and is not

| | |
|---|---|
| **Is** | A metric-indexed orientation summary. Links to canonical artifacts. Captures the Foundation Gate result, the findings, the decision, the non-decisions, and the follow-ups. |
| **Is not** | An ADR. Does not override contracts or Foundation. Does not replace DevHub session change records or evidence objects. If a record contains a decision that changes architecture, an ADR is also required. |

Canonical sources of truth remain: DevHub session change records (operational), ADRs in `bc-docs/docs/adrs/` (architectural), commits (code state), `evidence.evidence_object` rows (evaluation outcomes), `contract.metric_contract_version` rows (contract state). A Metric Work Record is the metric-indexed *pointer view* into those.

### Storage location

```
bc-docs/docs/onboarding/metric-work-records/<metric_slug>/YYYY-MM-DD-<work_type>-<session_uid>.md
```

Where:
- `<metric_slug>` is the metric's stable machine name minus the `mc__` prefix (e.g., `days_sales_outstanding`, `ap_turnover_ratio`). For cross-metric work that does not pivot on one metric, use `_cross/`.
- `YYYY-MM-DD` is the calendar date the record was authored.
- `<work_type>` is one of: `new-mc`, `version-bump`, `tenant-onboarding`, `rejection-investigation`, `grammar-extension`, `projection-bug`, `cleanup`.
- `<session_uid>` is the DevHub session UID (e.g., `SES-b7db1a`) that produced the record.

Example: `metric-work-records/days_sales_outstanding/2026-05-11-grammar-extension-SES-b7db1a.md`

### Required frontmatter

```yaml
---
metric: mc__days_sales_outstanding
metric_version: 1.2.0          # the version being investigated / produced; "n/a" for grammar work
tenant: apex                    # tenant slug, or "platform" for tenant-independent work
source_system: sap_ecc          # source system slug, or "n/a"
work_type: grammar-extension    # one of the seven types in §1
session_uid: SES-b7db1a         # DevHub session UID
date: 2026-05-11
status: decision-pending        # draft | decision-pending | decided | superseded | abandoned
related_commits: []             # SHAs
related_tasks: []               # TSK-xxxxxx
related_adrs: []                # DEC-xxxxxx
related_change_records: []      # CHG-xxxxxx (DevHub canonical)
repair_location: B+D            # A | B | C | D | E | F | or pair like B+D
affected_boundary: metric_evaluation
foundation_gate: passed         # passed | passed-with-override | violated-and-stopped
---
```

All keys are required. Use `n/a` for fields that don't apply (e.g., `metric_version: n/a` for grammar work that isn't a version bump).

### Required sections

A record follows this structure. Each section may be short (one paragraph or list). The goal is orientation, not exhaustive prose.

Records covering new meaning, semantic disputes, grammar/evaluator design, live-MC changes, or rejection diagnosis must additionally include the logic-study sections — `Metric Logic Studied`, `Assumptions`, `Rejected Interpretations`, `Drift / Damage Risks`, `Guardrails For Future Work` — per the template at `metric-work-records/_template.md`. See `metric-work-records/README.md` "When the logic-study sections are mandatory" for the precise trigger list.

```markdown
## Summary

One paragraph: what work was done, why, and what was decided.

## Foundation Gate Result

- **Repair location:** <A/B/C/D/E/F or pair>
- **Affected boundary:** <metric_evaluation / canonical / admission / action>
- **Six-invariant pre-check:** <pass / fail with which invariant>
- **Why not other layers:** <one line per layer that was considered and rejected>
- **Override?** <none | text rationale linked to follow-up task>

## Findings

Numbered list. What was learned. Cite sources (commit SHAs, evidence row IDs,
DevHub session UIDs). Do not speculate; if a finding was not verified, mark it.

## Decision / Recommendation

What was decided. Or "no decision — escalated to <X>". Or "no change required —
this is correct behavior". One paragraph maximum.

## Evidence

Pointers to canonical artifacts. Do not paste full contents. Link or name:
- `evidence.evidence_object` row IDs
- DevHub change records (CHG-uid)
- ADR files
- Commit SHAs with brief description
- Test results

## Non-decisions

What was explicitly NOT decided in this work. Examples: "did not change SDG",
"did not touch contracts", "did not propose a new CF". The discipline value of
naming non-decisions is high — see D268 Rule 2.

## Follow-ups

Tasks that should be filed (or were filed) as a result. `TSK-xxxxxx` if filed.
Open items if not yet ticketed.
```

### When a record is MANDATORY

A record is required whenever any of the following holds. List from §1 expanded:

1. A new Metric Contract is authored (new-mc work type).
2. An MC version bump changes formula, variables, grain, temporal semantics, or threshold values. Cosmetic / metadata-only bumps are optional.
3. A tenant or source-system onboarding lands for an existing MC (one record per (tenant, MC) pair).
4. A rejection investigation concludes with a decision, including "no change — this is correct behavior". Inconclusive investigations that explicitly punt may skip the record but should file a follow-up task.
5. A grammar or evaluator extension is designed, scoped, or implemented. (Always paired with an ADR.)
6. Stale-data cleanup is decided, including any DBCP authored — applied or not.
7. A Foundation Gate concludes the fix belongs outside the originally suspected layer. Especially: when the operator's reflex was "fix in SDG / fact / read model" and the gate redirected to B (contract semantics) or A (source modeling).

### When a record is OPTIONAL

- Pure read-only audits that produced no decision (use the DevHub session close summary instead).
- Plan-only sessions that didn't change state.
- Tool or diagnostic improvements not tied to a specific metric.

### Relationship to other artifacts

| Artifact | Authority | What the Metric Work Record adds |
|---|---|---|
| DevHub session change record (CHG-uid) | Canonical operational record; ISO 27001 audit trail | Metric-pivoted orientation; cross-session continuity |
| ADR (DEC-uid) | Architectural decision; authoritative going forward | Record links back; if the work *required* a new ADR, the record's `related_adrs` lists it |
| `evidence.evidence_object` | Authoritative evaluation outcome (Invariant VI) | Record cites evidence row IDs as orientation, never as content |
| Commit (SHA) | Code state | Record cites SHA and one-line description |
| DevHub task (TSK-uid) | Follow-up ownership | Record's `related_tasks` enumerates open items |
| Foundation chapters / SOPs | Authoritative procedure / principle | Record links when relevant; never restates |

If a record and any of the above disagree, the canonical source wins. The record is corrected to reflect canonical state, not the other way.

### Template

A reusable template lives at `bc-docs/docs/onboarding/metric-work-records/_template.md`. Copy it for a new record. The companion README at `bc-docs/docs/onboarding/metric-work-records/README.md` carries operating notes for the directory.

---

## Boundary with other onboarding chapters

| Chapter | Relationship |
|---|---|
| `metric-contract-creation.md` | Procedural authority for authoring MCs. This playbook frames *which work type* is being done and adds Foundation-Gate discipline around the procedure. |
| `metric-registration.md` | Procedural authority for promoting metrics from seed catalog through AI gates to platform. This playbook references it as a prerequisite for the new-MC work type. |
| `mc-chain-integrity.md` | Procedural authority for chain integrity diagnostics. This playbook's §6 service-first order includes chain_status / L-node gates as a diagnostic step. |
| `tenant-metric-binding.md` | Sibling SOP for tenant-binding work. Owned procedurally there; this playbook adds the runtime-readiness gate. |
| `business-field-and-business-object-onboarding.md`, `canonical-field-seeding.md`, `canonical-contract-creation.md`, `observation-contract-creation.md` | Upstream chain prerequisites. This playbook does not redefine them; rejection investigations may surface gaps that escalate to these procedures. |

## References

- `bc-docs/docs/foundation/the-invariants.md` — six invariants
- `bc-docs/docs/foundation/the-evaluation-boundaries.md` — four boundaries + boundary-independent rules
- `bc-docs/docs/foundation/the-contract-grammar.md` — twelve grammar artifacts
- `bc-docs/docs/adrs/ADR-ebf0b4.md` (D268) — Session Discipline Rules
- `bc-docs/docs/adrs/ADR-804874.md` (D366) — L-Node Semantic Gate; override mechanic
- `bc-docs/docs/adrs/ADR-chain-invariants.md` — machine-checkable chain invariants
- `bc-docs/docs/onboarding/metric-contract-creation.md`
- `bc-docs/docs/onboarding/metric-registration.md`
- `bc-docs/docs/onboarding/mc-chain-integrity.md`
- `barecount-devhub/CLAUDE.md` §Foundation Invariant Check
