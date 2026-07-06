---
uid: DEC-c3e57f
title: "Foundational Metric Context Framework (MCF) — sibling of BCF for metric meaning and metric-context packages"
description: "Establishes MCF as the AI-assisted governance discipline for metric meaning. Records 10 authority decisions (framework scope; post-D418 stance; reservoirs vs authority; reservoir intake hygiene; formula authority; MCF panel as governed workbench; layered MLS-14 + PE-MC-10 gates; BCF boundary; L-node and D365 boundary + implementation consequence; foundational guardrails). Sibling to BCF DEC-149ab2 / D411."
status: decided
date: 2026-05-26T07:04:15.417Z
project: bc-docs
domain: contracts
subdomain: catalog
focus: framework-establishment
---

# Foundational Metric Context Framework (MCF) — sibling of BCF for metric meaning and metric-context packages

## Rationale

Post-D418 the platform is greenfield with respect to metric authoring. BF/BO/CF/CM substrate is physically gone; the legacy SQL contract.metric_contract corpus is 778/780 archived; formula text storage is 100% legacy and 134 distinct shapes. Substrate consumers (engine, chain status, fiscal calendar, MLS, readiness) survive and are reusable. MCF establishes the framework-grade authoring discipline that BCF established for vocabulary (DEC-149ab2 / D411). Without this foundational ADR, every subsequent MCF gate (M2-M20 per build plan 40a9adc) lacks the authority anchor that justifies its substrate / service / UI commitments.

## Context

The Metric Context Framework (MCF) is the AI-assisted governance discipline for the platform's metric meaning. MCF is the sibling of BCF (DEC-149ab2 / D411): BCF governs business vocabulary (concept_registry.*); MCF governs metric computation context (Metric Contracts, formula AST, variable bindings, grain, temporal gates, computed-dimension resolution).

This ADR establishes MCF and records the authority decisions that govern it. It does not implement substrate, panel, verifier, UI, or BCF enrichment — those are gates M2-M20 per the MCF build plan (commit `40a9adc`).

**Arc artifacts consumed:** requirements (`13f9bb6`); inventory (`d9b10d2`); gap survey (`0ba202b`); reservoir/authority addendum (`0e3644b`); build plan (`40a9adc`); M0 packet (`5cd72c6`) + correction (`6ce9451`); BCF/MCF alignment note (`da8d9b7`).

## Decision 1 — Framework scope

MCF governs metric meaning / metric-context packages. MCF is upstream of the metric evaluation boundary. MCF authors grammar / configuration state under the `mcf` schema; it does not emit runtime Metric Snapshots, Evidence Objects, or Lineage Objects (those are produced only at evaluation boundaries per Foundation Invariants).

BCF governs business vocabulary. MCF consumes active BCF Registry ids for variable bindings, grain entity, and computed-dimension date sources. MCF does not author BCF substrate.

## Decision 2 — Post-D418 stance

The BF/BO/CF/CM substrate is physically gone (D418 Gate 5 closeout, May 2026). It cannot be used as evidence, lineage, migration input, bridge, compatibility shim, design input, or inspiration under MCF.

The existing SQL metric-contract corpus — `contract.metric_contract` (780 rows, 778 archived per live DB 2026-05-26), `contract.metric_contract_version` (1,022 rows including 729 active MCVs on archived parents), and `metric.metric_binding` (1,133 rows) — is **historical-only / non-authoritative** under MCF. No row is migrated.

The two non-archived legacy MCs (`mc__revenue_collection_rate` and `mc__ar_growth_rate`, both 2026-05-14 drafts, both pending audit) are pre-MCF-retired or candidate-only; if retained, they are re-authored from scratch under MCF Framework Approval with no carryover of formula text, binding, or version history beyond an optional `provenance.legacy_mc_uid` reference field.

Future MCF metric contracts live under `mcf.metric_contract`. Existing legacy tables remain queryable as historical reference.

## Decision 3 — Reservoirs vs authority

MCF candidate-intent reservoirs are (a) Mongo `bc_seed.seed_metrics` (~12,501 docs), (b) the preserved `metric.metric_definition` / `metric.metric_knowledge` carve-out (1,241 + 1,241 rows), (c) operator-direct submissions. All three are candidate-intent only; none carries authority.

**Five-class classification.** Candidate intent (no authority); weak hint / prompt context (no authority); semantic authority (BCF Framework Approval — `concept_registry.*`); binding authority (MCF Framework Approval — `mcf.metric_variable_binding`); formula authority (MCF AST authoring + deterministic verifier — `mcf.metric_formula_ast` + passing `mcf.metric_self_verification_result`).

**Two operative rules.** (1) Candidate intent triggers the panel to open a governed workbench; weak-hint sources are available through read tools within that workbench. Neither becomes authority. The panel's investigation through broad governed read awareness of governed platform surfaces produces a proposed package; the package is the panel's output, never its input. (2) No reservoir creates an MCF metric contract by inclusion.

**Reservoirs inform authoring; only BCF + MCF gates create authority.** BCF Registry is the sole semantic binding authority. MCF authoring under Framework Approval — three-model panel + operator confirm + deterministic verifier — is the sole binding-authority and formula-authority creator.

**Reservoir provenance is recorded.** `mcf.metric_authoring_panel_run` records reservoir name, entry ID, provenance source(s), and confidence band for every candidate the panel considers.

## Decision 4 — Reservoir intake hygiene

The reservoir-ingestion path **strips the legacy `co_bindings` field and any other BF/BO/CF/CM-derived fragment fields at ingestion time** before placing the candidate-intent reference in the panel's trigger queue. When the panel opens its workbench, the legacy fragments are absent from every read tool's response. The strip is enforced at the ingestion service; no other write path may insert into the intake queue. Reservoir provenance (source list, confidence band, original metric name, description, function/subfunction classification) is preserved.

Evidence: 506 of 12,501 `seed_metrics` docs have `co_bindings IS NOT NULL` (4%; live Mongo query 2026-05-26).

## Decision 5 — Formula authority discipline

A metric contract's formula is **authored as an Abstract Syntax Tree (AST)** from the closed taxonomy specified in MCF requirements §7.2. The authoring path accepts AST input only. Legacy formula text (1,216 rows in `metric.metric_formula`; 134 distinct shapes per gap survey) is weak hint / prompt context for the panel; it is **never authority**.

A parser that converts legacy text into a proposed AST may exist only as a workbench read tool that exposes the legacy text as one weak-hint context among many. The panel reads it, reasons over it alongside other workbench reads, and proposes an AST. The parser produces no authority and writes no substrate. No code path may write a parsed AST directly into `mcf.metric_formula_ast`.

Formula / package authority requires three independent conditions: (1) authored AST from the closed taxonomy; (2) composite `package_signature_hash` per MCF requirements §8.7 (hash over `formula_ast_hash + variable_binding_set_hash + grain_filter_temporal_dimension_signature_hash`); (3) passing self-verification fixture (PE-MC-10) bound to that exact package signature hash.

## Decision 6 — MCF panel operates as a governed workbench, not a packet consumer

A candidate-intent reference *triggers* the MCF Metric Authoring Panel to open a governed workbench. The candidate-intent reference is the *trigger*, not the *cage*. The panel investigates the governed platform broadly through a closed set of read tools and proposes a metric package as the result of that investigation. The package is the panel's output, never its input.

**Allowed read tool surface (v1; ADR-amendable as a named section):**

- `bcf_registry.read_*` — active BCF Entities, BusinessConcepts, Characteristics; reachability probes; lifecycle history
- `reservoir.read_seed_metric` — `bc_seed.seed_metrics` rows by id (post `co_bindings` strip per Decision 4)
- `reservoir.read_metric_definition` — `metric.metric_definition` + `metric.metric_knowledge` rows by id
- `source_reality.summarize` — what source / admission / observation contracts emit for a tenant; what fields exist
- `fiscal_calendar.read_config` — tenant fiscal calendar config and computed-dimension governing configs
- `mcf.read_drafts` — current MCF drafts in intake / draft / review queues
- `mcf.read_active_packages` — active MCF metric contracts (by id, by function, by grain entity)
- `panel_history.read` — prior panel runs and rejection-log entries for the same candidate area
- `formula_library.read_patterns` — catalog of legacy formula shapes as weak-hint reference only
- `chain_status.read` — `chain_status` / `chain_trace` for a candidate's prospective bindings
- `readiness.read` — `readiness_ledger` / `mc_dependency` summaries
- `mls.read_state` — MLS state ledger summaries (MLS-13, MLS-14)
- `evidence.search` / `evidence.retrieve` — allowed evidence corpora (standards, bc-seed, curated excerpts)

**Forbidden tool surfaces (load-bearing):**

- Raw DB / SQL access
- Tenant row-level raw data (admitted observation rows, source rows)
- Any tool that writes to substrate (writes flow only through MCF Framework Approval: panel proposes → operator confirms → substrate service writes)
- Any tool that touches dropped BF/BO/CF/CM substrate
- Arbitrary application tables not on the read allowlist
- Unscoped operator notes (operator-attached business guidance is a tracked workbench input — hashed into the workbench fingerprint, visible in transcripts — not a free-form data plane)
- Arbitrary internet retrieval (citations must come from the evidence allowlist)
- Tools that write `concept_registry.*` (BCF Framework Approval territory)
- Tools that bypass PE-MC-1 through PE-MC-10 gates

**Same-workbench rule + per-agent transcripts + workbench fingerprint are mandatory.** Three models (Maker / Checker / Moderator) operate against the same governed surfaces — same allowed tool set, same evidence-source allowlist, same registry snapshot id, same policy version, same operator-context hash — for their verdicts to constitute consensus. Each model produces an immutable per-agent transcript. The workbench fingerprint is the consensus-validity precondition. Every tool call is logged in the per-agent transcript with input hash + output hash + timestamp; citations must trace to transcript tool calls per PE-MC-1 grounding.

## Decision 7 — Layered activation gates: MLS-14 and PE-MC-10

An MCF metric contract reaches active state only when (a) `chain_status.chain_verdict = 'complete'`, (b) MLS-14 semantic activation gate returns green (substrate-identity check per D391 / DEC-b8b825), AND (c) PE-MC-1 through PE-MC-10 publication eligibility checks all pass, where PE-MC-10 cites a passing `mcf.metric_self_verification_result` whose bound `package_signature_hash` matches the MC's current hash.

**MLS-14 and PE-MC-10 are layered both-must-pass gates.** They check different surfaces (substrate-identity vs executable-behavior); both apply; neither subsumes; neither weakens. Failure of either blocks activation.

## Decision 8 — BCF boundary

Active BCF Registry (`concept_registry.*` rows in active lifecycle state) is the sole semantic binding authority for MCF.

MCF **cannot write `concept_registry.*`**. Those writes are BCF Framework Approval territory (DEC-149ab2 / D411). Any MCF panel tool that touches BCF substrate is read-only.

When an MCF authoring candidate requires a BC that does not yet exist in BCF Registry, the panel routes a request to BCF authoring. MCF does **not** invent BCs implicitly. Missing BC is a candidate-blocker, not an MCF-side workaround.

## Decision 9 — L-node and D365 boundary; implementation consequence

**D365 boundary.** D365 (`posting_date_field` on `contract.canonical_contract` + populated for the 56 existing CCs) is a runtime prerequisite for MCF metric contracts that reference a computed dimension (`fiscal_period` / `fiscal_year` / `fiscal_quarter` / any `time_anchor_resolution` AST node). D365 is **not** an M1 blocker and not an MCF substrate or service gate blocker. MCF Gates M2-M19 proceed without D365. Gate M20 defers its fiscal-period representative metric until D365 lands, or substitutes another metric class.

**L-node boundary.** MCF integrates with the D366 L-node semantic gate as a reader, not as an owner. The L-node verdict tables are read by MCF where present. As of 2026-05-26, only the L2 trace writer exists (141 verdicts, dated 2026-05-15 to 2026-05-17); L1 and L3-L8 writers are absent. MCF does **not** own the construction of those writers; that work lives in the D366 follow-on track. MCF authoring gates (PE-MC-1 through PE-MC-10) and runtime activation gates do not depend on L-node verdicts being complete. **MCF never asserts an L-node verdict exists when it does not.**

**Implementation consequence.** MCF build plan gates M2-M20 proceed per `metric-context-framework-build-plan.md` (commit `40a9adc`). This M1 ADR does not implement substrate, panel, verifier, UI, or BCF enrichment. Step 4 BCF enrichment remains separate and read-only-scoped (read access to `concept_registry.*` and BCF docs authorized; no BCF writes) until explicitly opened.

## Decision 10 — Foundational guardrails

Seven guardrails govern MCF. Presented as a named structural section so each is independently amendable later.

1. **No candidate reservoir creates authority by inclusion.** Inclusion makes a KPI a candidate; MCF authoring under Framework Approval creates authority.
2. **BCF enrichment scope is operator + BCF-panel decided, not seed-wording driven.** Seeds inform priority order, not concept selection. BCF concepts are authored against business reality, not seed metric `description` text.
3. **Panel rejection of legacy-only grounding is mandatory.** Candidates whose only grounding traces to BF/BO/CF/CM are rejected at intake. The `co_bindings` field on `seed_metrics` is stripped at reservoir-ingestion time (Decision 4).
4. **Duplicate-intent detection is PE-MC-9 at draft → review.** PE-MC-9 runs against `mcf.*`, against pending drafts in the queue, and across the five-class classification (Decision 3).
5. **Source-system assumptions must be made explicit before draft.** Implicit references to specific source systems route to operator confirm before draft.
6. **Reservoir provenance is a recorded panel-input field.** `mcf.metric_authoring_panel_run` records reservoir name, entry ID, provenance source(s), and confidence band.
7. **No SQL MC corpus migration; ever.** The two non-archived legacy MCs (Decision 2) go through MCF authoring as if greenfield.

## Substrate commitment

MCF authors new substrate under the `mcf` schema. Tables are enumerated in MCF requirements §17.1 and sequenced in build plan §4 (Gates M2-M6 for identity / lifecycle / publication / panel / tenant-binding substrate; Gates M8-M10 for package signature, fixture substrate, verifier; Gate M11 for reservoir ingestion). Foundation Governance Substrate sharing (`contract.certification_record`, `contract.framework_policy`, `contract.operator_confirm_rule`) follows MCF requirements §17.3 — MCF writes rows scoped by MCF `action_code` values; BCF writes its own; neither reads or mutates the other's.

## Reversal path

Foundation Invariant III applies: this ADR may be superseded by a future ADR. Individual decisions within this ADR (e.g. the tool surface in Decision 6 or the seven guardrails in Decision 10) are independently amendable via Errata against the named structural section without re-opening the whole ADR.

## Consequences

This ADR enables MCF build plan Gates M2-M20 to proceed under the recorded authority model. The MCF arc moves to **Gate M2 (identity substrate DBCP)** as the immediate next gate, subject to operator decision on legacy MC table retirement marker (M0 §9 item 1; recommended low-stakes table comment + README note).
