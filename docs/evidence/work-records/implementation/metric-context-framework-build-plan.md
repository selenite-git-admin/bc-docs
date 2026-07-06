---
uid: metric-context-framework-build-plan
title: Metric Context Framework (MCF) — Build Plan
description: Step 3 of the MCF arc. Mechanics document — names gates, dependencies, rough scope, and evidence inputs. Not an authority document, not a substrate DBCP, not a code-level estimate. Consumes the requirements (commit 13f9bb6), inventory (d9b10d2), gap survey (0ba202b), and reservoir/authority addendum (0e3644b). Locks six operator-approved positions from prior steps; flags remaining operator decisions. Produces a 21-gate sequence (M0-M20) with bidirectional mapping to MCF requirements §20, plus parallelization map, BCF enrichment interface, first-representative-metric criteria, risk register, and verification protocol per gate.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: build-plan
---

# Metric Context Framework (MCF) — Build Plan

## 1. What this is / is not

### 1.1 What this is

A mechanics document that turns the MCF requirements + inventory + gap survey + reservoir/authority addendum into a sequenced implementation roadmap. It names gates, their dependencies, rough scope, and required verification. It is the bridge between specification and execution.

### 1.2 What this is not

- **Not an authority document.** No new architecture. No new rules. Where the plan references a rule, it cites the source (requirements §X, inventory F-X, gap survey Q-X, addendum §X).
- **Not a substrate DBCP.** Substrate column lists, indexes, triggers, migrations are gate-specific DBCPs that this plan *enumerates* but does not *contain*.
- **Not a code-level estimate.** T-shirt sizes (S/M/L/XL) are rough; per-gate calendar time is operator-decided.
- **Not an MCF ADR.** Gate M1 produces the foundational ADR; this build plan is its input.
- **Not a substitute for operator approval.** Several positions still require operator lock — flagged in §9.

### 1.3 Inputs

| Input | Commit / status |
|---|---|
| `metric-context-framework-requirements.md` | `13f9bb6` (proposed) |
| `metric-context-framework-inventory.md` | `d9b10d2` (draft) |
| `metric-context-framework-gap-survey.md` | `0ba202b` (draft) |
| `metric-context-framework-candidate-reservoir-and-authority-classification.md` | `0e3644b` (draft) |
| ADRs cited by the above | per individual citations |

### 1.4 Sibling reference (BCF arc)

The BCF arc shipped a comparable artifact chain (requirements + inventory + gap research + build sequencing). MCF Step 3 mirrors that pattern. Where MCF gates inherit BCF mechanics (e.g. panel discipline, cert-backed authority, console UI-S1..S5 pattern), the gate references the BCF source rather than re-deriving.

---

## 2. Locked positions consumed by the plan

These positions are treated as **locked for build-plan purposes**. Each is sourced to a prior commit; the operator has either explicitly locked it (per this Step 3 brief) or the prior step recommended it without rejection.

| # | Locked position | Source | Implication |
|---|---|---|---|
| L1 | **Reservoirs inform authoring; only BCF + MCF gates create authority.** | Addendum §6 (operator-approved Step 3 brief) | Plan treats `bc_seed.seed_metrics`, `metric.metric_definition`, and operator-direct as candidate-intent reservoirs, never as authority. |
| L2 | **SQL MC corpus historical-only; no migration.** Existing `contract.metric_contract` / `metric_contract_version` / `metric_binding` rows are not migrated into MCF. The 2 non-archived legacy MCs are pre-MCF-retired / candidate-only. | Gap survey Q1 Option C + Step 3 brief lock #1 | M2 substrate plans `mcf.metric_contract` as new table; legacy tables stay queryable as historical reference. No migration gate exists. |
| L3 | **Seed `co_bindings` field is stripped at reservoir-ingestion.** | Addendum guardrail #3 + Step 3 brief lock #2 | M11 reservoir-ingestion service includes the strip step as a discipline-non-optional step. The legacy field is not visible to the panel. |
| L4 | **AST is authored/governed, never parsed from legacy text as authority.** | Gap survey Q2 + Step 3 brief lock | M7 AST service accepts AST input only. Legacy text formula corpus is historical reference. Step 4 may use a parser as a one-shot helper to seed panel proposals, but never as authority. |
| L5 | **MLS-14 and PE-MC-10 are layered both-must-pass gates.** | Gap survey Q3 sub-decision + Step 3 brief lock | M13 PE-MC evaluator does not subsume MLS-14; both gates apply at activation. Neither weakens. |
| L6 | **Future MCF contracts live under `mcf.*`.** | Gap survey Q1 + Step 3 brief lock | M2 creates new `mcf` schema. All `mcf.*` tables enumerated in MCF requirements §17.1 are MCF-owned. Foundation Governance Substrate (cert/policy/operator-confirm-rule) shared per MCF §17.3. |

Positions **not** locked here (handled in §9 Operator decisions still required): the seven guardrails from addendum §5 (text for ADR), disposition mechanics for the 2 non-archived legacy MCs, D365 scheduling, L-node ownership, first-10-metric selection, BCF Registry read authorization, exact MCF ADR wording.

---

## 3. Phase model

### 3.1 Phases by dependency order

Twenty-one gates organized into four phases. Within each phase, gates are partially ordered; the gate table (§4) shows exact dependencies.

| Phase | Gates | Purpose | Operator-decision dependency |
|---|---|---|---|
| **Phase A — Foundation** | M0, M1 | Prerequisites + foundational ADR | Operator must approve §9 items 1, 5, 6, 7 before M1 |
| **Phase B — Substrate** | M2, M3, M4, M5, M6 | All `mcf.*` substrate tables + Foundation Governance Substrate integration | M2 needs Q1 disposition locked in M1 |
| **Phase C — Services** | M7, M8, M9, M10, M11, M12, M13, M14, M15 | AST authoring, package-signature, fixture, verifier, reservoir-ingestion, panel, PE-MC evaluator, publication, supersession | M7 needs Q2 working rule locked in M1 |
| **Phase D — Surfaces and program** | M16, M17, M18, M19, M20 | Operator console + cross-framework + first-representative-metric program | M17, M18, M20 need BCF enrichment landed |

### 3.2 Mapping to MCF requirements §20 gates

The build plan gate IDs diverge from MCF requirements §20 because:
- The build plan adds M0 (prerequisites) and M11 (reservoir ingestion) — neither was in §20.
- M8 (package signature service) is split out from §20 M2/M7 to make the composite-hash computation an explicit gate.
- §20 M15+M16+M17 (three operator-console gates) collapse into build-plan M17 (combined) to match the natural shipping unit.

Bidirectional mapping table:

| Build plan gate | MCF requirements §20 gate | Notes |
|---|---|---|
| M0 Prerequisites / cleanup | (new) | Added per gap survey coordination items |
| M1 Foundational MCF ADR | §20 M1 | Same |
| M2 Identity substrate | §20 M2 | Same |
| M3 Lifecycle / cert substrate | §20 M3 | Same |
| M4 PE substrate | §20 M4 | Same |
| M5 Panel / workbench substrate | §20 M5 | Same; M5 substrate adds reservoir-provenance fields per addendum guardrail #6 |
| M6 Tenant binding substrate | §20 M6 | Same |
| M7 Formula AST service | §20 M7 | Same |
| M8 Package signature service | (split from §20 M2 + M7) | New — composite `package_signature_hash` computation; substrate column lives on `mcf.metric_contract_version` (§20 M2) but the computation logic is its own gate |
| M9 Self-verification fixture substrate | §20 M8 | Same |
| M10 Deterministic verifier service | §20 M9 | Same |
| M11 Reservoir ingestion / candidate intake | (new) | Added per addendum §7 |
| M12 Metric Authoring Panel workbench | §20 M10 | Same |
| M13 PE-MC evaluator | §20 M11 | Same |
| M14 Publication path | §20 M12 | Same |
| M15 Supersession path | §20 M13 | Same |
| M16 Operator console read/detail | §20 M14 | Same |
| M17 Operator console draft/AST/fixture authoring | §20 M15 + M16 + M17 (collapsed) | The brief collapses three §20 gates into one shipping unit; substrate impact unchanged |
| M18 Tenant binding console | §20 M18 | Same |
| M19 Cross-framework coordination | §20 M19 | Same |
| M20 First representative metric re-authoring program | §20 M20 | Same; scope refined per addendum reservoir-ingestion path |

Cross-document references should cite either the build-plan gate ID or the §20 gate ID with explicit context. MCF requirements §20 is updated at the next requirements revision pass to reflect the build-plan numbering (out of Step 3 scope).

---

## 4. Gate table

Per-gate scope, inputs, outputs, dependencies, BCF-enrichment dependency, t-shirt size, primary risk, required verification.

### 4.1 Phase A — Foundation

#### Gate M0 — Prerequisites / cleanup

| Attribute | Value |
|---|---|
| **Scope** | Prerequisite work that must complete (or be operator-deferred with explicit acceptance) before MCF ADR. Bundles: (a) operator disposition of the 2 non-archived legacy MCs (E2 in addendum §3.2); (b) bc-postgres schema allowlist expansion to include `concept_registry` for BCF Registry read access (needed for Q4 enumeration); (c) L-node ownership decision (parallel D366 track vs MCF-owned); (d) D365 `posting_date_field` scheduling decision (separately scoped per §5.3). |
| **Inputs** | Addendum §3.2 (legacy MC list); gap survey §3.5 (D365 status); gap survey §2.3.2 (L-node finding) |
| **Outputs** | Operator decisions documented in a short pre-M1 memo (could append to addendum, could be a memo). No code/DB changes from M0 itself. |
| **Dependencies** | None |
| **BCF-enrichment dependency** | No |
| **T-shirt size** | S |
| **Primary risk** | Operator decisions deferred without explicit acceptance → M1 ADR has unresolved scope |
| **Verification** | All four sub-items have a recorded operator decision (lock or explicit-defer with named follow-on owner) |

#### Gate M1 — Foundational MCF ADR

| Attribute | Value |
|---|---|
| **Scope** | Author and decide the foundational MCF ADR (analogue of BCF DEC-149ab2 / D411). Must include: framework scope (per MCF requirements §2); actors (Metric Authoring Panel, operators); disciplines (per MCF §11); Framework Approval as the configured authority within MCF scope; relationship to dropped substrate (§16: no migration); explicit five-class reservoir/authority classification (addendum §2); the seven guardrails (addendum §5) as a named structural section of the ADR (so they're amendable without touching the rest); locked decision wording from addendum §6 or operator-revised. |
| **Inputs** | All four MCF docs; M0 operator decisions |
| **Outputs** | One ADR (`bc-docs-v3/docs/adrs/ADR-mcf-{uid}.md`), status `decided`. Linked from MCF requirements §1.4 source-of-authority table. |
| **Dependencies** | M0 |
| **BCF-enrichment dependency** | No |
| **T-shirt size** | M |
| **Primary risk** | ADR scope creep — operator wants to bundle other MCF decisions into this single ADR; better to ship the framework-establishing ADR narrow and follow with topic-specific ADRs as needed |
| **Verification** | ADR has status `decided`; cross-referenced from MCF requirements; addendum guardrails appear as a named section; 5-class classification appears as a named section |

### 4.2 Phase B — Substrate

#### Gate M2 — Identity substrate

| Attribute | Value |
|---|---|
| **Scope** | Create `mcf` schema. Tables: `mcf.metric_contract` (identity-tuple UNIQUE per MCF §4.2); `mcf.metric_contract_version` (column shape from MCF §17.1, including `package_signature_hash` column populated by M8); `mcf.metric_variable_binding` (variable-grain, not CC-grain per gap survey §2.3.1); `mcf.metric_filter_clause` (set-semantic for identity); `mcf.metric_computed_dimension_ref` (governing-config link). Immutability triggers on identity-bearing columns when `lifecycle_state='active'`. |
| **Inputs** | M1 ADR (Q1 disposition locked); MCF requirements §4, §6, §17.1 |
| **Outputs** | Substrate DBCP with column lists, constraints, triggers, indexes; Drizzle schema additions; read/write repositories. |
| **Dependencies** | M1; BCF Registry stable (already true per CLAUDE.md) |
| **BCF-enrichment dependency** | No |
| **T-shirt size** | L |
| **Primary risk** | Identity tuple definition drift between substrate UNIQUE and MCF §4.2 spec; misalignment surfaces only at runtime collision |
| **Verification** | All identity tuples UNIQUE-enforced in DB; immutability triggers tested with positive + negative cases; Drizzle schemas typecheck-clean; read repository returns canonical shapes |

#### Gate M3 — Lifecycle / certification substrate

| Attribute | Value |
|---|---|
| **Scope** | `mcf.metric_contract_revision` (descriptive-only revisions per MCF §4.6); `mcf.metric_supersession` (predecessor → successor edges per §10.5); immutability triggers per Foundation Invariant III; cert reuse pattern for MCF `action_code='metric_create'` on `contract.certification_record` (Foundation Governance Substrate per MCF §17.3). |
| **Inputs** | M2; MCF requirements §10, §11.5, §17.3 |
| **Outputs** | Substrate DBCP; cert writer for MCF action_codes |
| **Dependencies** | M2 |
| **BCF-enrichment dependency** | No |
| **T-shirt size** | M |
| **Primary risk** | Supersession edge cases (successor invalidates predecessor fixture per §12.7); test coverage gap |
| **Verification** | Supersession edge tests; cert rows queryable by MCF action_code |

#### Gate M4 — Publication eligibility substrate

| Attribute | Value |
|---|---|
| **Scope** | `mcf.metric_publication_eligibility_result` (per MCF §17.1; per-publication PE-MC-1..PE-MC-10 results; PE-MC-10 row cites the satisfying `mcf.metric_self_verification_result` from M9/M10); cert reuse for MCF `action_code='metric_transition'`; operator-confirm rule policy entries for high-risk MCF actions (per MCF §11.4). |
| **Inputs** | M3; MCF requirements §13, §17.1 |
| **Outputs** | Substrate DBCP; operator-confirm rule rows seeded for high-risk actions |
| **Dependencies** | M3 |
| **BCF-enrichment dependency** | No |
| **T-shirt size** | M |
| **Primary risk** | PE-MC-10 row foreign key to `mcf.metric_self_verification_result` requires M9/M10 to land before PE evaluator (M13) can write — sequencing must ensure |
| **Verification** | Schema test: PE-MC-10 row insert without backing verification result is rejected at FK level |

#### Gate M5 — Panel / workbench substrate

| Attribute | Value |
|---|---|
| **Scope** | `mcf.metric_authoring_panel_run` (run uid, prompt version, policy version, workbench fingerprint hash, per-model transcript uids, per-model verdicts, consensus computation result, grounding-check result per claim — per MCF §17.1; **plus reservoir-provenance fields per addendum guardrail #6: reservoir name, reservoir entry ID, reservoir provenance source(s), reservoir confidence band**); `mcf.metric_authoring_panel_transcript` (per-model immutable transcript); `mcf.workspace_tool_allowlist` (versioned tools the workspace exposes); `mcf.evidence_source_allowlist` (versioned evidence sources for citation); framework_policy entries for MCF panel discipline. |
| **Inputs** | M4; MCF requirements §11.3, §17.1; addendum guardrail #6 |
| **Outputs** | Substrate DBCP; allowlist seed rows |
| **Dependencies** | M4 |
| **BCF-enrichment dependency** | No |
| **T-shirt size** | L |
| **Primary risk** | Workbench fingerprint algorithm specification drift between substrate and panel implementation; addendum guardrail #6 fields not coupled to ingestion service in M11 |
| **Verification** | Substrate accepts a sample panel-run row with all reservoir-provenance fields; transcript content stored verbatim and readback-identical |

#### Gate M6 — Tenant binding / MLS integration substrate

| Attribute | Value |
|---|---|
| **Scope** | `mcf.tenant_binding` (per MCF §14; MLS 15-25 state integration with D392 substrate). |
| **Inputs** | M5; MCF requirements §14, §17.1; D392 substrate (already live per inventory) |
| **Outputs** | Substrate DBCP; integration tests with `metric.mls_state` ledger |
| **Dependencies** | M5; MLS substrate stable per D392 |
| **BCF-enrichment dependency** | No |
| **T-shirt size** | M |
| **Primary risk** | Boundary-confusion between MCF's `mcf.tenant_binding` and D392's `metric.mls_state` — must specify which is SSOT for which fact |
| **Verification** | Read-then-write integration test confirms boundary discipline; MLS 15-25 transition events route correctly |

### 4.3 Phase C — Services

#### Gate M7 — Formula AST service

| Attribute | Value |
|---|---|
| **Scope** | `mcf.metric_formula_ast` substrate (serialized canonical AST + formula identity hash per MCF §7-§8); authoring service that constructs valid ASTs, runs normalization (per §8.2), computes `formula_intent_hash` (per §8.4), performs bind-time checks (per §6.3). Accepts AST input only — locked by L4 (no text-parsing entry point). |
| **Inputs** | M2; M1 ADR (L4 lock); MCF requirements §7, §8 |
| **Outputs** | Substrate + authoring service; closed AST node taxonomy implementation; normalization implementation; identity-hash service (algorithm-versioned `mcf-formula-hash-v1`) |
| **Dependencies** | M2 |
| **BCF-enrichment dependency** | No (operates on AST + bindings, not BCF concept content) |
| **T-shirt size** | XL |
| **Primary risk** | AST taxonomy v1 closure is operator-decided (open question Q4 in MCF §19.2); shipping an incomplete taxonomy forces back-and-forth |
| **Verification** | AST type-checker tests across taxonomy; normalization round-trip tests; identity-hash determinism tests; bind-time check tests covering MCF §6.3 checks 1-5 |

#### Gate M8 — Package signature service

| Attribute | Value |
|---|---|
| **Scope** | Composite `package_signature_hash` computation per MCF §8.7: hash over (formula_ast_hash + variable_binding_set_hash + grain_filter_temporal_dimension_signature_hash). Substrate column lives on `mcf.metric_contract_version` (created in M2); the computation logic is its own gate to make algorithm versioning explicit. |
| **Inputs** | M7 (formula AST hash); M2 (variable bindings + grain + filter + temporal substrate) |
| **Outputs** | Hash service (algorithm-versioned `mcf-package-hash-v1`); auto-population trigger on `mcf.metric_contract_version` write |
| **Dependencies** | M2, M7 |
| **BCF-enrichment dependency** | No |
| **T-shirt size** | S |
| **Primary risk** | Composite hash sensitivity — any inputs added later (e.g. new filter clause types) require algorithm version bump |
| **Verification** | Hash determinism tests (same inputs → same hash); algorithm-version round-trip; substrate trigger-fires on every relevant column update |

#### Gate M9 — Self-verification fixture substrate

| Attribute | Value |
|---|---|
| **Scope** | `mcf.metric_self_verification_fixture` (per MCF §12 + §17.1; per-MC-version fixture body Section A inputs + Section B expected output + Section C resolver fixture config; bound `package_signature_hash` + `self_verification_fixture_hash`); structural-check engine implementing C-FX-1..C-FX-11 (per MCF §12.5); stale-fixture rule enforcement (per §12.7). |
| **Inputs** | M2, M7, M8 |
| **Outputs** | Substrate + structural-check engine; rejection rows emitted as `structural_reject` verification results |
| **Dependencies** | M2, M7, M8 |
| **BCF-enrichment dependency** | No |
| **T-shirt size** | L |
| **Primary risk** | Structural checks not exhaustive — a fixture passes C-FX but the verifier fails on a corner case; iterate via M10 evidence |
| **Verification** | C-FX-1..C-FX-11 each have positive + negative tests; stale-fixture rule tested by changing package_signature_hash mid-lifecycle |

#### Gate M10 — Deterministic verifier service

| Attribute | Value |
|---|---|
| **Scope** | `mcf.metric_self_verification_result` substrate (append-only per Invariant V; pass / fail / structural_reject verdicts; per-row diff trace on fail); verifier service that reads package by `package_signature_hash`, reads fixture by `self_verification_fixture_hash`, runs C-FX-1..C-FX-11, executes the package against Section A inputs with Section C resolver fixture configs, compares against Section B expected output, emits result. Algorithm-versioned (`mcf-verifier-v1`), reproducibility-tested. |
| **Inputs** | M9 |
| **Outputs** | Substrate + service; deterministic verdict per (package, fixture, verifier-version) |
| **Dependencies** | M9 |
| **BCF-enrichment dependency** | No (operates on fixture inputs, not BCF concept content) |
| **T-shirt size** | L |
| **Primary risk** | Underbuilding the verifier — shipping a version that handles ratio metrics but fails on windowed / computed-dimension / bucket-assign formulas. Mitigation: M10 acceptance criteria include all formula AST node types from §7.2 |
| **Verification** | Verifier handles every AST node type from §7.2; reproducibility tests (same inputs → same verdict across executor instances); rejected-fixture tests; resolver-config sensitivity tests |

#### Gate M11 — Reservoir ingestion / candidate intake

| Attribute | Value |
|---|---|
| **Scope** | New service (not in MCF requirements §20). Ingestion path from three reservoirs (addendum §2.3): `bc_seed.seed_metrics` (Mongo); `metric.metric_definition` / `metric.metric_knowledge` (Postgres carve-out); operator-direct authoring submissions. Per-ingestion: strip the legacy `co_bindings` field (L3 lock; addendum guardrail #3); apply confidence + provenance filtering (e.g. start with high-confidence + apqc subset per addendum §3.5); route candidate to panel intake queue with reservoir-provenance fields recorded for the panel-run (M5 substrate). |
| **Inputs** | M5 (panel substrate); addendum classification + guardrails |
| **Outputs** | Ingestion service; intake-queue rows (where intake queue lives is a sub-decision — could be `mcf.intake_queue` table or in-memory queue with substrate-backed audit; substrate DBCP for M11 decides) |
| **Dependencies** | M5 |
| **BCF-enrichment dependency** | No (operates on reservoir content, not BCF) |
| **T-shirt size** | M |
| **Primary risk** | `co_bindings` stripping bypass — if any code path ingests without going through M11, legacy fragments leak. Mitigation: enforce single ingestion service; reject direct intake-queue writes from any other path |
| **Verification** | Ingestion test confirms `co_bindings` always absent on intake-queue rows even when source row has them; reservoir-provenance fields populated for every ingestion; confidence/provenance filter respects operator-configured threshold |

#### Gate M12 — Metric Authoring Panel workbench

| Attribute | Value |
|---|---|
| **Scope** | Three-model panel (Maker / Checker / Moderator) per MCF §11.3 + BCF Chapter 7 workbench framing (commit `1d7d209`). Closed-enum verdicts (APPROVE_FOR_DRAFT / OPERATOR_REVIEW / REJECT_*). PE-MC-1 grounding (every claim traces to a tool call that retrieved an allowed source). Defect-code taxonomy implementation. Panel-side fixture proposal capability against the verifier service (M10). |
| **Inputs** | M5, M7, M10, M11 |
| **Outputs** | Panel service; per-run records to `mcf.metric_authoring_panel_run` + per-agent transcripts to `mcf.metric_authoring_panel_transcript`; workbench fingerprint algorithm implementation |
| **Dependencies** | M5, M7, M10, M11 |
| **BCF-enrichment dependency** | Partial — panel can run on any BCF density, but produces meaningful proposals only when concepts exist to bind to. Acceptable to ship M12 ahead of BCF enrichment; meaningful operator runs begin post-enrichment |
| **T-shirt size** | XL |
| **Primary risk** | Overbuilding panel scope — adding capabilities beyond the three-model + closed-verdicts + grounding scope. Mitigation: explicit gate scope as listed; future capabilities are separate gates |
| **Verification** | Panel produces consensus verdict on a test candidate; workbench fingerprint computed correctly; per-agent transcripts append-only; grounding check rejects fabrication |

#### Gate M13 — PE-MC evaluator

| Attribute | Value |
|---|---|
| **Scope** | Deterministic publication-gate evaluator for PE-MC-1 through PE-MC-10 per MCF §13. PE-MC-10 evaluation reads a passing `mcf.metric_self_verification_result` whose bound `package_signature_hash` matches the candidate's current hash (per §12.7 stale-fixture rule). Both MLS-14 and PE-MC-10 must pass independently (L5 lock). |
| **Inputs** | M10 (verifier results), M12 (panel outputs) |
| **Outputs** | Evaluator service; per-publication PE-MC-1..PE-MC-10 result rows on `mcf.metric_publication_eligibility_result` |
| **Dependencies** | M10, M12; existing `Mls14ActivationGate` (already live per inventory F-MLS-2) |
| **BCF-enrichment dependency** | No (the evaluator's logic is BCF-content-agnostic) |
| **T-shirt size** | M |
| **Primary risk** | PE-MC failure-routing logic — wrong code routes to REJECT instead of OPERATOR_REVIEW; calibration data poisoned |
| **Verification** | Per-PE-MC positive + negative tests; failure-routing-code tests; MLS-14 + PE-MC-10 both-must-pass integration test |

#### Gate M14 — Publication path (Fork-i / Fork-ii)

| Attribute | Value |
|---|---|
| **Scope** | Two-phase request → operator confirm path for `metric_transition` action_code (BCF B10 analogue per MCF §11.3). Step A evidence bundle re-render (PE-MC-1..PE-MC-10 results, bindings, formula, package signature hash, satisfying verification result for PE-MC-10); Step B operator rationale ≥40 chars; Step C semantic-finality affirmation if MCF §10.6 adopted. |
| **Inputs** | M13 |
| **Outputs** | Publication endpoint(s) + cert writer |
| **Dependencies** | M13 |
| **BCF-enrichment dependency** | No |
| **T-shirt size** | M |
| **Primary risk** | Step A bundle composition errors (operator sees wrong PE-MC-10 result, wrong fixture cite) |
| **Verification** | Step A bundle integration test against fixture-pass and fixture-fail cases; Fork-ii idempotency test on duplicate cert |

#### Gate M15 — Supersession path

| Attribute | Value |
|---|---|
| **Scope** | Operator-initiated supersession with successor pointer; cross-framework supersession from BCF (BCF BC supersession invalidates dependent MCF MC bindings — coordination per MCF §3.8); supersession invalidates predecessor's fixture per §12.7 stale-fixture rule and requires a fresh passing fixture for the successor before PE-MC-10. |
| **Inputs** | M3, M14 |
| **Outputs** | Supersession endpoint; cert writer for `metric_supersede` action_code; fixture-stale-rule enforcement at supersession boundary |
| **Dependencies** | M3, M14 |
| **BCF-enrichment dependency** | No |
| **T-shirt size** | M |
| **Primary risk** | Predecessor's snapshots / dependent artifacts unhandled — supersession leaves dangling references |
| **Verification** | Supersession test confirms predecessor's fixture goes stale; PE-MC-10 refuses successor until fresh fixture passes |

### 4.4 Phase D — Surfaces and program

#### Gate M16 — Operator console read/detail

| Attribute | Value |
|---|---|
| **Scope** | MC List (read; filterable by function/owner/grain/bound tenants); MC Detail (read; surfaces identity tuple, formula AST visualization, variable bindings, temporal gate, filter set, **package signature hash**, PE-MC-1..PE-MC-10 results, **fixture list with verifier verdicts**, panel run history, cert history, tenant bindings) per MCF §18.2. Read-only — no write surfaces. |
| **Inputs** | M5 (panel run audit data), M10 (fixture verdicts) |
| **Outputs** | bc-admin pages + bc-core read endpoints |
| **Dependencies** | M5, M10 |
| **BCF-enrichment dependency** | No (read-only of whatever exists) |
| **T-shirt size** | L |
| **Primary risk** | Detail page exposes substrate columns not intended for operator (e.g. internal hash values without context); over-detail |
| **Verification** | bc-admin pages render against empty MCF substrate; render against populated substrate; PE-MC-10 + fixture-verdict surfacing renders correctly |

#### Gate M17 — Operator console draft / AST builder / fixture authoring

| Attribute | Value |
|---|---|
| **Scope** | MC Draft Edit with formula AST builder per MCF §18.4 (visual tree composition; type-aware variable binding picker; aggregate scoping; real-time identity hash; canonical AST read-back; **no free text input**). MC Self-Verification Fixture Authoring per MCF §18.2 (Section A/B/C composition; C-FX-1..C-FX-11 live structural-check feedback; panel-proposed fixtures presented for operator review). MC Self-Verification Run (verifier verdict + per-row diff trace on fail). MC Publication Confirm (Step A/B/C with PE-MC-10 evidence; semantic-finality affirmation if §10.6 adopted). |
| **Inputs** | M7, M9, M10, M14, M16 |
| **Outputs** | bc-admin write pages + bc-core write endpoints |
| **Dependencies** | M7, M9, M10, M14, M16 |
| **BCF-enrichment dependency** | **Yes** — AST builder shows BCs in pickers; fixture authoring shows variable rowsets keyed by BC representation terms. Empty BCF density = empty pickers = unauthorable UI |
| **T-shirt size** | XL |
| **Primary risk** | AST builder UI complexity — the closed-taxonomy structural composition is novel UI work. Risk: under-spec produces unusable builder; over-spec produces shipping delay |
| **Verification** | Operator can compose an AST for each MCF §7.2 taxonomy node type; structural-check feedback updates live; fixture authoring tests against all 10 representative-metric classes from §7 |

#### Gate M18 — Tenant binding console

| Attribute | Value |
|---|---|
| **Scope** | Tenant Binding List (per-tenant view of which MCs are bound, MLS state, drift status); Tenant Binding Detail (per-binding view; manual intervention dialogs: acknowledge drift, request re-evaluation, supersede binding); MLS Operations view (Platform MLS 1-14 + per-tenant MLS 15-25 progression). |
| **Inputs** | M6, M17 |
| **Outputs** | bc-admin pages + bc-core endpoints |
| **Dependencies** | M6, M17 |
| **BCF-enrichment dependency** | Indirect — needs M17 which needs BCF enrichment |
| **T-shirt size** | L |
| **Primary risk** | MLS visualization complexity — 25-state ladder rendering risks operator confusion if not designed against feedback_metric_lifecycle_states discipline |
| **Verification** | Per-tenant view renders against MLS substrate; manual intervention dialogs route correctly |

#### Gate M19 — Cross-framework coordination (BCF/MCF events)

| Attribute | Value |
|---|---|
| **Scope** | Event mechanics per MCF §3.8: BCF events (BC supersession, registry transitions) that affect MCF (e.g. MC bindings to superseded BCs); MCF events (MC supersession that affects BCF consumer-count UI). Mechanics options: event bus / polling / subscription (MCF §19.8 Q21 — implementation DBCP decides). |
| **Inputs** | M15, plus corresponding BCF event-emission readiness |
| **Outputs** | Event mechanics implementation; BCF-MCF integration tests |
| **Dependencies** | M15; BCF event-emission readiness (out of MCF scope) |
| **BCF-enrichment dependency** | No |
| **T-shirt size** | M |
| **Primary risk** | BCF and MCF event-mechanics technology divergence — if BCF chooses one pattern and MCF chooses another, cross-framework coordination requires bridging |
| **Verification** | BC supersession event triggers MCF dependent-MC binding invalidation flow; MCF supersession event triggers BCF consumer-count refresh |

#### Gate M20 — First representative metric re-authoring program

| Attribute | Value |
|---|---|
| **Scope** | Operational program (not a substrate gate) to author 10 representative MCF MCs per §7 selection criteria. Includes: reservoir-source selection (Step 4 hands off); panel runs through M12; fixture authoring through M17; publication through M14; tenant binding through M18 for at least 1 demonstration tenant. |
| **Inputs** | All prior gates + BCF enrichment (Step 4 deliverable) |
| **Outputs** | 10 MCF MCs in active state with passing fixtures; demonstration evidence for foundational MCF ADR's operational claims |
| **Dependencies** | M17, M18; **M0/D365 (only if any of the 10 metrics uses a computed dimension — see §5.3)** |
| **BCF-enrichment dependency** | **Yes** — hard dependency on Step 4 deliverable |
| **T-shirt size** | L (program-level; per-metric XS) |
| **Primary risk** | First-metric authoring cost exceeds projection — each metric requires panel + operator confirm + fixture + verifier pass; if any of these surfaces friction, the 10 ship slowly. Mitigation: start with simplest classes (ratio, amount aggregation) before tackling fiscal-period + filtered + windowed |
| **Verification** | All 10 metrics in active state; each carries passing self-verification fixture; at least 1 fiscal-period metric demonstrates resolver-fixture-config end-to-end; at least 1 binding to a demonstration tenant in MLS 15-25 progression |

---

## 5. Parallelization map

### 5.1 Classification

| Class | Gates |
|---|---|
| **Foundational — can start immediately** | M0 (sequenced sub-items per operator availability), M1 (after M0 sub-items resolved) |
| **Parallel-safe with BCF enrichment** | M2, M3, M4, M5, M6 (substrate); M7, M8, M9, M10, M11, M12, M13, M14, M15 (services); M16 (read console); M19 (cross-framework). All of these have no BCF concept-density dependency. |
| **Blocked on minimum BCF Registry density** | M17 (draft / AST builder / fixture authoring UI); M18 (tenant binding console — indirect via M17); M20 (re-authoring program — hard dependency) |
| **Blocked on operator decision (must be resolved in M0 or M1)** | M2 (Q1 disposition for table naming); M7 (Q2 working rule); M11 (reservoir-ingestion `co_bindings` strip pre-authorization per L3 — already covered by Step 3 brief); M20 (first-10 selection — Step 4 deliverable) |
| **Blocked on non-MCF prerequisite (scoped narrowly)** | M20 only — specifically, **only the computed-dimension representative metric within M20 is blocked on D365 `posting_date_field` implementation**. The other 9 representative metric classes from §7 are not D365-dependent. |

### 5.2 Parallel work envelope

After M1 lands, the build can proceed on three parallel tracks:

**Track 1 — Substrate (M2 → M3 → M4 → M5 → M6).** Linear dependency chain. Substrate DBCPs are the slowest path; landing them in parallel with services is desirable but constrained by substrate's strict ordering.

**Track 2 — Services (M7 → M8 → M9 → M10; M11 in parallel with M7-M10; then M12 → M13 → M14 → M15).** Services have a longer dependency chain but can start once their substrate predecessor lands (M7 after M2, M8 after M7, etc.).

**Track 3 — BCF enrichment (Step 4, owned outside this build plan).** Runs in parallel with Tracks 1 and 2; converges at M17 + M18 + M20.

Once Tracks 1 + 2 land and Track 3 produces the minimum BCF density, Phase D (surfaces + program) executes sequentially: M16 → M17 → M18 → M20, with M19 in parallel.

### 5.3 D365 narrow scoping

D365 `posting_date_field` is **only** blocking for runtime evaluation of computed-dimension MCs. Specifically:

- M20 representative-metric #5 (fiscal-period computed-dimension metric per §7) **cannot run end-to-end without D365**.
- M9 + M10 fixture/verifier mechanics **can be tested without D365** because the resolver fixture config (per MCF §9.2 + §12.4 Section C) substitutes for tenant config at verification time.
- M2 substrate `mcf.metric_computed_dimension_ref` **can be built without D365** — the table stores the governing-config link; runtime lookup is what needs the column.

Recommendation: M0 includes D365 scheduling as a sub-item; D365 implementation owner is **not** the MCF build plan owner (it's the D365 owner — likely the same person operationally, but the dependency is documented as cross-track).

If D365 cannot be scheduled before M20, M20's fiscal-period metric is operator-deferred and replaced with another metric class (e.g. a second filtered metric) to keep the 10-metric demonstration intact.

### 5.4 L-node L1+L3-L8 parallel-track explicit

Per gap survey §2.3.2 + addendum, L-node L1 + L3-L8 writers do not exist (L2 writer exists per Q-5 finding). MCF build plan **does not own** L-node writer construction. If those writers land before M14 publication path, MCF reads them as best-effort signal. If they do not land, MLS-14 + PE-MC-10 + chain_status carry the gating load — none of M1-M20 fails because L-node verdicts are partial.

Recommendation: L-node L1+L3-L8 work tracks under D366 governance and is out of scope for this plan.

---

## 6. BCF enrichment interface

### 6.1 What Step 4 must provide for MCF

Step 4 (BCF enrichment for MCF seed cases) is the operator-owned BCF program that produces the minimum BCF density MCF needs for M17 / M18 / M20.

**Minimum Entity / BusinessConcept / Characteristic density** (carries forward from addendum §2.4):

- ~30 BusinessConcepts spanning ~3-5 Entity families.
- At least one date-BC per scope (for fiscal-period / time-anchor).
- At least one currency-BC for ratio + amount metrics.
- At least one count-BC for count metrics.
- At least one duration-BC for duration / lead-time metrics.
- At least one negative-test case (an unreachable BC for grain-reachability check).

**Concept classes needed for formula variables, dimensions, temporal anchors, filters** (mapped from MCF §6 + §7 + §9):

| MCF mechanic | Required BCF input |
|---|---|
| `variable_ref` (MCF §7.2) | At least 2 BCs whose representation term + unit are compatible with each variable position the metric declares |
| Grain entity (MCF §4.3, §6.5) | At least 1 Entity that is identity-bearing and reachable from the bindings |
| Time-anchor variable (MCF §4.4 + §7.2 `time_anchor_resolution`) | At least 1 BC bound to `time_anchor` role on a date/timestamp representation |
| Filter input (MCF §4.5) | At least 1 BC for each filter clause's referenced field |
| Computed-dimension reference (MCF §9.2) | The governing-config artifact (e.g. tenant fiscal calendar config) — separate from BCF, but BCF date-BC is the source for computed-dimension input |

### 6.2 Acceptance criteria — "enough BCF to author first 10 MCF cases"

Step 4 deliverable is accepted when:

1. At least 10 candidate seed metrics (from the high-confidence + apqc subset per addendum §3.5) have been operator-selected.
2. For each selected seed, the BCF Registry contains the BCs needed for the metric's formula AST (variables + filters + grain + temporal anchor + computed-dimension sources).
3. The BCF panel has reached consensus on every concept the 10 metrics reference; no MCF MC waits on a BC in `draft` or `review` state.
4. At least one BC per representation term class (currency, count, duration, date, identifier) exists in active state.

### 6.3 Guardrail (carried from addendum guardrail #2)

**BCF enrichment is informed by seed priorities but judged by business reality, not by seed wording.** Step 4 selects which concepts to enrich first based on metric demand (which MCF MCs operator wants to author first); the concepts themselves are authored under BCF Framework Approval discipline against business reality + bc-seed catalog + standards. Seed metric `description` text is reference material for BCF, not authoritative naming.

---

## 7. First representative metric program (M20 selection criteria)

### 7.1 Ten metric classes to exercise

Per addendum §2.4.3 — the 10 representative metrics must collectively exercise:

| # | Metric class | What it tests | Locked-form pattern reference |
|---|---|---|---|
| 1 | Simple aggregation | Basic AST + variable binder + fixture | `O1 = SUM(I1)` (legacy `O1 = I1` pattern; 80 instances per gap survey Q-11) |
| 2 | Ratio metric | Two variables + constant; formula audit + fixture binding | `O1 = (I1 / I2) * C1` (435 instances) |
| 3 | Difference metric | Same family as ratio | `O1 = I1 - I2` (86 instances) |
| 4 | Passthrough metric | Trivial AST | `O1 = I1` |
| 5 | Windowed metric | `window` AST node + temporal gate + window parameter | Trailing 30-day SUM |
| 6 | Fiscal-period computed-dimension metric | `time_anchor_resolution` AST node + Section C resolver fixture config | `SUM(amount) GROUP BY fiscal_period` |
| 7 | Bucket-assign metric | `bucket_assign` AST node | DSO age buckets |
| 8 | Positive cross-coherence metric | Two distinct concepts bound to the same Entity; grain-alignment check pass | A ratio where I1 and I2 are different BCs on the same Entity |
| 9 | Failure-case (semantic) | Deliberately built to fail PE-MC-10 or MLS-14 | A ratio with I1 = I2 (MT-04971 specimen class) |
| 10 | Stale-fixture failure case | Supersede formula AST after fixture passes; PE-MC-10 should refuse | Mutate AST on metric (2) after its fixture passes |

### 7.2 Selection criteria (per addendum §2.4.4)

- Each metric maps to ≥1 already-existing BCF Entity (Sales Order Line, unit-price BC, lead time, cycle time are confirmed active per CLAUDE.md).
- The 10 collectively span ≥3 Entity families.
- At least 1 metric uses a date BC.
- At least 1 metric exercises each AST node taxonomy class.
- At least 1 metric has a known legacy parallel (text formula in `metric.metric_formula`) so the comparison-vs-legacy is visible (operator gets a "look, MCF authored cleaner" demonstration).
- At least 2 metrics are deliberately built to fail (one PE-MC-10, one MLS-14).

### 7.3 What this plan does not select

Final 10 specific metrics — Step 4 selection is operator-owned, informed by the high-confidence + apqc seed subset (~200-300 candidates per addendum §3.5). This plan defines the classes, not the rows.

---

## 8. Risk register

Risks aggregated from all four input docs + new risks surfaced by sequencing.

| # | Risk | Severity | Owning gate | Mitigation |
|---|---|---|---|---|
| **R-01** | **`contract.metric_contract` naming collision.** New `mcf.metric_contract` vs existing `contract.metric_contract`. | High | M0 (decision) + M2 (substrate) | Q1 Option C narrow-scope (L2 lock). Existing table stays as historical. New table in `mcf` schema. Cross-doc references use schema-qualified names. |
| **R-02** | **Formula TEXT temptation.** Engineer or panel takes the path of least resistance and parses legacy `formula_text` into AST, contaminating MCF authoring with substrate-shape-dependent semantics. | High | M7 + M11 | L4 working rule lock. M7 AST service rejects text input. M11 ingestion service does not pass formula text as authoritative. |
| **R-03** | **Legacy `co_bindings` resurrection.** 506 seed rows carry pre-D418 `co_bindings`. Panel consumes uncritically. | High | M11 | L3 lock + addendum guardrail #3. M11 strips `co_bindings` at ingestion. Reservoir tests confirm field is absent on intake-queue rows. |
| **R-04** | **Seed-driven BCF shape contamination.** Step 4 BCF enrichment scope is driven by seed wording rather than business reality. Loose seed descriptions become loose BCF concepts. | High | Step 4 + addendum guardrail #2 | BCF enrichment judged by business reality (BCF panel + operator), not seed wording. Seed informs priority order only. |
| **R-05** | **L-node partial implementation.** L2 writer exists; L1+L3-L8 are gaps (per inventory F-LNODE-1 refined in gap survey §2.3.2). | Medium | (not MCF-owned) | L-node parallel track under D366 governance. MCF reads L-node verdicts as best-effort signal. MLS-14 + PE-MC-10 + chain_status carry the gating load. |
| **R-06** | **D365 `posting_date_field` missing.** Confirmed in gap survey Q-7. Hard prerequisite for runtime evaluation of any computed-dimension MC. | Medium | M0 (scheduling) + M20 (fiscal-period metric) | M0 includes D365 scheduling as sub-item. M20 fiscal-period metric deferred if D365 not scheduled. |
| **R-07** | **Typed projection / `metric_snapshot` transition.** Per inventory F-SNAP-1 + gap survey §3.1. Dual-write transition in flight. | Medium | M15 + M17 | Step 3 build plan specifies that MCF reads `fact.ms_*_v*` where it exists; falls back to `envelope.metric_snapshot`. Implementation in M14/M15/M17 confirms which side is authoritative. |
| **R-08** | **Helper-script trust failure.** Per inventory F-READY-3 + BCF E2 banding. | Medium | All gates | BCF E2 verdict reused wholesale. MCF does not introduce text-parser helper scripts (L4 lock prevents). |
| **R-09** | **Overbuilding panel before substrate.** M12 panel scope creeps to include capabilities beyond three-model + closed verdicts + grounding. | Medium | M12 | M12 acceptance criteria explicit: three-model + closed verdicts + grounding + workbench fingerprint — nothing more. Additional capabilities are separate gates. |
| **R-10** | **Underbuilding verifier before publication.** M10 ships handling ratios; fails on windowed / computed-dimension / bucket-assign. M13 PE-MC-10 evaluator accepts the verifier output blindly; production breaks. | High | M10 | M10 acceptance criteria include all AST node types from §7.2. M10 reproducibility tests cover every taxonomy class. M11 reservoir-ingestion does not surface candidates whose AST class exceeds verifier capability. |
| **R-11** | **Workbench-fingerprint algorithm drift.** M5 substrate defines fingerprint shape; M12 panel implements computation. Drift causes consensus-validity false positives or false negatives. | Medium | M5 + M12 | Fingerprint algorithm specified in MCF ADR (M1) and locked. Substrate and panel share a single algorithm-version constant. |
| **R-12** | **Substrate ownership boundary confusion (MCF vs MLS).** Per inventory + gap survey: `metric.mls_state` (D392) vs `mcf.tenant_binding` (M6). | Medium | M6 | M6 acceptance criteria specify which is SSOT for which fact. Integration test validates boundary. |
| **R-13** | **Foundation Governance Substrate write coupling.** Both BCF and MCF write to `contract.certification_record` / `contract.framework_policy` / `contract.operator_confirm_rule`. Coordination required. | Medium | M3, M4, M5 | MCF writes rows scoped by MCF action_codes / scope_codes. BCF writes its own. Neither reads or mutates the other's. Already locked in MCF §17.3. |
| **R-14** | **Reservoir-ingestion bypass.** Any code path that writes intake-queue rows without going through M11 bypasses `co_bindings` strip + provenance recording. | High | M11 | M11 substrate enforces single ingestion path. Other paths rejected at substrate level (or via service-layer policy). |
| **R-15** | **First-metric authoring cost overrun.** M20 per-metric calendar cost exceeds projection. | Medium | M20 | Start with simplest classes (ratio, amount aggregation) before tackling fiscal-period + filtered + windowed. Defer demonstrably hard cases to post-M20 follow-on. |
| **R-16** | **Operator-confirm fatigue.** PE-MC pattern routes many cases to OPERATOR_REVIEW. Operator confirm queue overwhelms operator capacity. | Medium | M12 + M13 | Calibration sampling discipline per BCF chapter 10 NF7 transferred to MCF: track override rate per scope per stage; tune sampling rate per policy. Initial state: defaults from BCF NF7. |
| **R-17** | **MCF requirements §20 vs build-plan gate numbering drift.** Cross-doc references confuse the reader. | Low | (cross-doc) | Bidirectional mapping table in §3.2. MCF requirements §20 updated at next revision pass to reflect build-plan numbering. |

---

## 9. Operator decisions still required

These items are explicitly NOT locked by this build plan and require operator sign-off before the gates that depend on them can proceed.

| # | Decision | Blocks | Notes |
|---|---|---|---|
| 1 | **Final disposition mechanics for historical SQL MC tables.** Q1 Option C narrow-scope is locked (L2), but: (a) explicit retirement marker on `contract.metric_contract` (table comment, ADR-grade note); (b) handling of the 729 active-MCV-on-archived-MC inconsistency (leave as data anomaly vs document explicit "historical-only" status). | M2 substrate DBCP (only needs to know whether to add a `legacy_mc_uid` provenance column on `mcf.metric_contract` for operator orientation) | Low-stakes; can be decided in M0 or as part of M1 ADR scope |
| 2 | **D365 `posting_date_field` scheduling.** Owner-assignment + landing date. | M20 fiscal-period metric only | Recommend M0 sub-item; not blocking M2-M19 |
| 3 | **L-node ownership lock.** Confirm: L1+L3-L8 writer construction is D366-owned, not MCF-owned. Build plan recommendation is "parallel track, not MCF". | None (build plan proceeds without L-node); but operator confirmation locks the boundary | Recommend M0 sub-item; low-stakes |
| 4 | **First 10 representative metric selection.** Step 4 produces the operator-selected list from high-confidence + apqc seed subset (~200-300 candidates per addendum §3.5). Selection criteria locked here (§7); specific row selection is operator-owned. | M20 | Step 4 deliverable; not blocking Phases A-C |
| 5 | **BCF enrichment authorization / `concept_registry` read access.** Currently outside bc-postgres allowlist for this Claude session. Enrichment program needs read access. | Step 4 (and consequently M17, M18, M20) | Recommend M0 sub-item; needed before Step 4 opens |
| 6 | **Exact MCF ADR wording approval.** Addendum §6 recommended wording; operator may revise. The seven guardrails (addendum §5) may be revised. The 5-class classification (addendum §2) may be revised. | M1 | M1 cannot ship without this |
| 7 | **Foundational MCF ADR ID + filename.** UID generated by `devhub_decision_record` at ADR creation time; nickname D-code allocated atomically. Operator does not pre-assign; this is procedural. | M1 | Procedural; happens at M1 execution |

---

## 10. Recommended next step

### 10.1 Immediate next: M0 prerequisites cleanup

Recommend the operator open M0 as a small focused session that resolves:

- §9 item 1 (legacy MC table retirement marker)
- §9 item 2 (D365 scheduling — owner + target landing)
- §9 item 3 (L-node ownership lock)
- §9 item 5 (BCF Registry read authorization)

Items 4 (first-10 selection) and 6 (ADR wording approval) are coupled with later gates (Step 4 + M1 respectively) and are not M0 candidates.

After M0 lands, **M1 foundational MCF ADR** is the immediate next gate. The ADR must include:

1. Framework scope per MCF §2.
2. Actors (Metric Authoring Panel, operators).
3. Disciplines per MCF §11.
4. Framework Approval as configured authority within MCF scope.
5. Relationship to dropped substrate (MCF §16: no migration).
6. **Five-class reservoir/authority classification** (addendum §2) as a named structural section.
7. **The seven guardrails** (addendum §5) as a named structural section.
8. **Locked decision wording** from addendum §6 or operator-revised.

### 10.2 D365 sequencing recommendation

If D365 `posting_date_field` cannot be scheduled before M2, the recommendation is:

- M2-M19 proceeds without D365 (none of them have D365 dependency).
- M20 fiscal-period metric is deferred to a M20-follow-on track.
- M20 ships with 9 of 10 metric classes covered; the fiscal-period class is added when D365 lands.

This avoids D365 becoming a hard blocker for the entire MCF build.

### 10.3 Cleaner-M1 prerequisite

The M1 ADR is cleanest if it has the following resolved at intake:

- Addendum guardrails text reviewed (operator may want to refine wording).
- Addendum decision wording reviewed.
- 5-class classification accepted (or revised).

A short pre-M1 operator-review session of the addendum (without writing the ADR) would surface any operator-preferred refinements before the ADR session attempts to encode them. This is optional but recommended.

### 10.4 What NOT to do next

- **Do not open M2 substrate DBCP design before M1 ADR.** M1 locks the table-naming convention, the Foundation Governance Substrate boundaries, the action_code namespace. M2 without M1 risks substrate that has to be rewritten.
- **Do not open Step 4 BCF enrichment before M0 BCF read authorization.** Enrichment selection without live `concept_registry` read access is guessing.
- **Do not open M7 AST service before M1.** Q2 working rule lock lives in the M1 ADR. M7 without M1 risks a service that has to be re-scoped.

---

## Document verification

- **All 10 required sections present** (§1 What this is, §2 Locked positions, §3 Phase model, §4 Gate table, §5 Parallelization map, §6 BCF enrichment interface, §7 First representative metric program, §8 Risk register, §9 Operator decisions still required, §10 Recommended next step).
- **Every gate has dependencies and verification.** §4 gate table includes Dependencies and Verification rows for all 21 gates.
- **Plan cites all four inputs.** MCF requirements, inventory, gap survey, reservoir/authority addendum all cited.
- **No operator-owned unresolved decision is written as already-decided.** §9 enumerates 7 pending items; each is explicitly flagged.
- **No code/DB/schema files changed.** This is a docs-only commit.
