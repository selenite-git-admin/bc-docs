---
uid: DEC-f8f925
title: "Foundational Metric Context Framework (MCF) — sibling of BCF for metric meaning and metric-context packages"
description: "REVERSED — duplicate-allocation artifact. Canonical MCF foundational ADR is DEC-c3e57f (D422). DEC-f8f925 was allocated when devhub_decision_record returned a client-side fetch error before the response landed; the registry row and ADR file were written but the caller had no UID to report. A retry allocated DEC-c3e57f. This row is kept as audit trail per Foundation Invariant III (no destructive history)."
status: reversed
superseded_by: DEC-c3e57f
date: 2026-05-26T06:55:02.275Z
project: bc-docs
domain: contracts
subdomain: catalog
focus: framework-establishment
---

# Foundational Metric Context Framework (MCF) — sibling of BCF for metric meaning and metric-context packages

> **REVERSED — duplicate-allocation artifact.** The canonical MCF foundational ADR is **DEC-c3e57f (D422)**, file `ADR-c3e57f.md` in this same directory. This row (DEC-f8f925) was allocated when an earlier `devhub_decision_record` call returned a client-side `fetch failed` error before the response landed; the registry row and this file were written, but the caller had no UID to report. A retry with the same payload allocated DEC-c3e57f, which is the canonical decision. This file is preserved as audit trail per Foundation Invariant III (no destructive history); its content is superseded by DEC-c3e57f's body. Do not read the content below as MCF authority — read DEC-c3e57f instead.

## Context

The post-D418 platform is greenfield with respect to metric authoring: BF/BO/CF/CM substrate is physically gone; the legacy SQL `contract.metric_contract` corpus is 778/780 archived; formula text storage is 100% legacy and 134 distinct shapes; substrate consumers (engine, chain status, fiscal calendar, MLS, readiness) survive and are reusable. MCF establishes the framework-grade authoring discipline that BCF established for vocabulary (DEC-149ab2 / D411). MCF differs from BCF in scope (metric meaning vs vocabulary) and in starting position (greenfield panel implementation vs BCF v1 packet retrieval). The framework-grade authority model — panel-proposes / operator-confirms / platform-verifies under closed read-tool workbench — is the shared sibling pattern. Without this foundational ADR, every subsequent MCF gate (M2-M20 per build plan 40a9adc) lacks the authority anchor that justifies its substrate / service / UI commitments.

## Context

The Metric Context Framework (MCF) is the AI-assisted governance discipline for the platform's metric meaning — what a metric IS, what it measures, over what grain, against what context, using what formula, under what runtime conditions, evaluated against what data. MCF is the sibling of the Business Context Framework (BCF, DEC-149ab2 / D411): BCF governs business vocabulary (Entities, BusinessConcepts, Characteristics on `concept_registry.*`); MCF governs metric computation context (Metric Contracts, formula AST, variable bindings, grain declarations, temporal gates, computed-dimension resolution).

This ADR establishes MCF and records the authority decisions that govern it. It does not implement substrate, panel, verifier, UI, or BCF enrichment — those are gates M2-M20 per the MCF build plan.

**Arc artifacts consumed:**

- `bc-docs-v3/docs/implementation/metric-context-framework-requirements.md` (commit `13f9bb6`)
- `bc-docs-v3/docs/implementation/metric-context-framework-inventory.md` (commit `d9b10d2`)
- `bc-docs-v3/docs/implementation/metric-context-framework-gap-survey.md` (commit `0ba202b`)
- `bc-docs-v3/docs/implementation/metric-context-framework-candidate-reservoir-and-authority-classification.md` (commit `0e3644b`)
- `bc-docs-v3/docs/implementation/metric-context-framework-build-plan.md` (commit `40a9adc`)
- `bc-docs-v3/docs/implementation/metric-context-framework-m0-pre-m1-decision-packet.md` (commit `5cd72c6` + correction `6ce9451`)
- `bc-docs-v3/docs/implementation/bcf-mcf-panel-workbench-alignment-note.md` (commit `da8d9b7`)

## Decision 1 — Framework scope

MCF governs metric meaning / metric-context packages. MCF is upstream of the metric evaluation boundary (per Foundation `the-evaluation-boundaries.md`). MCF authors grammar / configuration state (`mcf.*` substrate); it does not emit runtime Metric Snapshots, Evidence Objects, or Lineage Objects (those are produced only at evaluation boundaries per Foundation Invariants).

BCF governs business vocabulary. MCF consumes active BCF Registry ids (`concept_registry.entity.entity_id`, `concept_registry.business_concept.business_concept_id`, `concept_registry.characteristic.characteristic_id`) for variable bindings, grain entity, and computed-dimension date sources. MCF does not author BCF substrate.

## Decision 2 — Post-D418 stance

The BF/BO/CF/CM substrate is physically gone (D418 Gate 5 closeout, May 2026; 7 quarantined tables dropped). It cannot be used as evidence, lineage, migration input, bridge, compatibility shim, design input, or inspiration under MCF (per working rule established in MCF requirements §1).

The existing SQL metric-contract corpus — `contract.metric_contract` (780 rows, 778 archived per live DB query 2026-05-26), `contract.metric_contract_version` (1,022 rows including 729 active MCVs on archived parents), and `metric.metric_binding` (1,133 rows) — is **historical-only / non-authoritative** under MCF. No row is migrated into MCF substrate.

The two non-archived legacy MCs (`mc__revenue_collection_rate` and `mc__ar_growth_rate`, both 2026-05-14 drafts, both `audit_status_code='pending'`) are pre-MCF-retired or candidate-only; if retained as candidates, they are re-authored from scratch under MCF Framework Approval with no carryover of formula text, binding, or version history beyond an optional `provenance.legacy_mc_uid` reference field on the new MCF MC for operator orientation.

Future MCF metric contracts live under `mcf.metric_contract` in the new `mcf` schema. Existing legacy tables remain queryable as historical reference.

## Decision 3 — Reservoirs vs authority

MCF candidate-intent reservoirs are:
- (a) Mongo `bc_seed.seed_metrics` (~12,501 docs)
- (b) the preserved platform `metric.metric_definition` / `metric.metric_knowledge` carve-out (1,241 + 1,241 rows)
- (c) operator-direct authoring submissions

All three are candidate-intent only; none carries authority. Inclusion in a reservoir does not create an MCF metric contract.

**Five-class classification:**

| Class | Role | Creates authority? |
|---|---|---|
| Candidate intent | "This KPI is worth considering for MCF authoring" | No |
| Weak hint / prompt context | Panel may reference for reasoning, never cite as grounding | No |
| Semantic authority | "This business concept IS this in the vocabulary" | Yes — BCF Framework Approval |
| Binding authority | "This MC variable binds to this business concept" | Yes — MCF Framework Approval |
| Formula authority | "This is what this metric contract computes" | Yes — MCF AST authoring + deterministic verifier |

**Two operative rules.** (1) Candidate intent triggers the panel to open a governed workbench; weak-hint sources are available to the panel through read tools within that workbench. Neither becomes authority. The panel's investigation through broad governed read awareness of governed platform surfaces produces a proposed package; the package is the panel's output, never its input. (2) No reservoir creates an MCF metric contract by inclusion.

**Reservoirs inform authoring; only BCF + MCF gates create authority.**

BCF Registry (`concept_registry.*` active rows) is the sole semantic binding authority. MCF authoring under Framework Approval — three-model panel + operator confirm + deterministic verifier — is the sole binding-authority and formula-authority creator. The candidate-intent reservoir entry triggers panel authoring; it does not bound the panel's reasoning. The panel opens a governed workbench, reads broadly through allowed tools, and proposes the package as the result of that investigation.

**Reservoir provenance is recorded.** `mcf.metric_authoring_panel_run` records reservoir name, reservoir entry ID, reservoir provenance source(s), and reservoir confidence band for every candidate the panel considers.

## Decision 4 — Reservoir intake hygiene

The reservoir-ingestion path that conveys candidates from `bc_seed.seed_metrics` (or any future Mongo / Postgres reservoir) into the MCF intake queue **strips the legacy `co_bindings` field and any other BF/BO/CF/CM-derived fragment fields at ingestion time**. The reservoir-ingestion path strips legacy fragments before placing the candidate-intent reference in the panel's trigger queue. When the panel opens its workbench, the legacy fragments are absent from every read tool's response. The strip is enforced at the ingestion service; no other write path may insert into the intake queue. Reservoir provenance (source list, confidence band, original metric name, description, function/subfunction classification) is preserved.

Evidence: 506 of 12,501 `seed_metrics` docs have `co_bindings IS NOT NULL` (4% of reservoir; live Mongo query 2026-05-26).

## Decision 5 — Formula authority discipline

Under MCF, a metric contract's formula is **authored as an Abstract Syntax Tree (AST)** from the closed taxonomy specified in MCF requirements §7.2. The authoring path accepts AST input only. Legacy formula text (the 1,216 rows in `metric.metric_formula` and any text-form formula material in reservoir candidates) is weak hint / prompt context for the authoring panel; it is **never authority**.

A parser that converts legacy text into a proposed AST may exist only as a workbench read tool that exposes the legacy text as one weak-hint context among many. The panel reads it, reasons over it alongside other workbench reads, and proposes an AST. The parser produces no authority and writes no substrate. Its output enters MCF substrate only through the panel-proposes / operator-confirms / platform-verifies path. No code path is permitted to write a parsed AST directly into `mcf.metric_formula_ast`.

Formula / package authority requires three independent conditions:
1. Authored AST from the closed taxonomy.
2. Composite `package_signature_hash` per MCF requirements §8.7 (hash over `formula_ast_hash + variable_binding_set_hash + grain_filter_temporal_dimension_signature_hash`).
3. Passing self-verification fixture (PE-MC-10) bound to that exact package signature hash.

## Decision 6 — MCF panel operates as a governed workbench, not a packet consumer

A candidate-intent reference (from a reservoir or from operator-direct submission) *triggers* the MCF Metric Authoring Panel to open a governed workbench. The candidate-intent reference is the *trigger*, not the *cage*. The panel investigates the governed platform broadly through a closed set of read tools and proposes a metric package as the result of that investigation. The package is the panel's output, never its input.

**Allowed read tool surface (v1; ADR-amendable as a named section):**

| Tool | Purpose |
|---|---|
| `bcf_registry.read_*` | Active BCF Entities, BusinessConcepts, Characteristics; reachability probes; lifecycle history |
| `reservoir.read_seed_metric` | `bc_seed.seed_metrics` rows by id (post `co_bindings` strip per Decision 4) |
| `reservoir.read_metric_definition` | `metric.metric_definition` + `metric.metric_knowledge` rows by id |
| `source_reality.summarize` | What source / admission / observation contracts emit for a tenant; what fields exist |
| `fiscal_calendar.read_config` | Tenant fiscal calendar config and computed-dimension governing configs |
| `mcf.read_drafts` | Current MCF drafts in intake / draft / review queues |
| `mcf.read_active_packages` | Active MCF metric contracts (by id, by function, by grain entity) |
| `panel_history.read` | Prior panel runs and rejection-log entries for the same candidate area |
| `formula_library.read_patterns` | Catalog of legacy formula shapes (134 distinct per gap survey Q-11) as weak-hint reference only |
| `chain_status.read` | `chain_status` / `chain_trace` for a candidate's prospective bindings |
| `readiness.read` | `readiness_ledger` / `mc_dependency` summaries |
| `mls.read_state` | MLS state ledger summaries (MLS-13, MLS-14) |
| `evidence.search` / `evidence.retrieve` | Allowed evidence corpora (standards, bc-seed, curated excerpts) |

**Forbidden tool surfaces (load-bearing):**

- Raw DB / SQL access
- Tenant row-level raw data (admitted observation rows, source rows)
- Any tool that writes to substrate (writes flow only through MCF Framework Approval: panel proposes → operator confirms → substrate service writes)
- Any tool that touches dropped BF/BO/CF/CM substrate (physically gone post-D418; even if reintroduced, the working rule forbids)
- Arbitrary application tables not on the read allowlist
- Unscoped operator notes (operator-attached business guidance is a tracked workbench input — hashed into the workbench fingerprint, visible in transcripts — not a free-form data plane)
- Arbitrary internet retrieval (citations must come from the evidence allowlist)
- Tools that write `concept_registry.*` (BCF Framework Approval territory, not MCF panel scope)
- Tools that bypass PE-MC-1 through PE-MC-10 gates

**Same-workbench rule + per-agent transcripts + workbench fingerprint are mandatory.** The three models (Maker / Checker / Moderator) operate against the same governed surfaces — same allowed tool set, same evidence-source allowlist, same registry snapshot id, same policy version, same operator-context hash — for their verdicts to constitute consensus. Each model produces an immutable per-agent transcript. The workbench fingerprint (hash over the five axes above) is the consensus-validity precondition.

**Transcript discipline.** Every tool call is logged in the per-agent transcript with input hash + output hash + timestamp. Tool calls are replayable as audit evidence; they are not re-used as authority unless the panel cites them correctly through PE-MC-1 grounding.

## Decision 7 — Layered activation gates: MLS-14 and PE-MC-10

An MCF metric contract reaches active state only when:
- (a) `chain_status.chain_verdict = 'complete'`,
- (b) MLS-14 semantic activation gate returns green (substrate-identity check per D391 / DEC-b8b825), AND
- (c) PE-MC-1 through PE-MC-10 publication eligibility checks all pass, where PE-MC-10 cites a passing `mcf.metric_self_verification_result` whose bound `package_signature_hash` matches the MC's current hash.

**MLS-14 and PE-MC-10 are layered both-must-pass gates.** They check different surfaces (substrate-identity vs executable-behavior); both apply; neither subsumes the other; neither weakens. Failure of either blocks activation.

PE-MC-1 through PE-MC-9 are the existing publication eligibility checks per MCF requirements §13 (provenance, grain coherence, binding completeness, type/unit coherence, formula AST validity, temporal gate well-formedness, computed-dimension coherence, runtime-readiness intent, definition discipline). PE-MC-10 is the self-verification fixture pass check added per MCF requirements §13.10 (commit `ea14d9a`).

## Decision 8 — BCF boundary

Active BCF Registry (`concept_registry.entity / business_concept / characteristic` rows in active lifecycle state) is the sole semantic binding authority for MCF.

MCF **cannot write `concept_registry.*`**. Those writes are BCF Framework Approval territory (DEC-149ab2 / D411). Any MCF panel tool that touches BCF substrate is read-only.

When an MCF authoring candidate requires a BC that does not yet exist in BCF Registry, the panel routes a request to BCF authoring (operator decision: open a BCF authoring run for the missing BC). MCF does **not** invent BCs implicitly. The discipline: missing BC is a candidate-blocker, not an MCF-side workaround.

## Decision 9 — L-node and D365 boundary; implementation consequence

**D365 `posting_date_field` boundary.** D365 (add `posting_date_field` column to `contract.canonical_contract` + populate for the 56 existing CCs) is a runtime prerequisite for MCF metric contracts that reference a computed dimension (`fiscal_period` / `fiscal_year` / `fiscal_quarter` / any `time_anchor_resolution` AST node). D365 is **not** an M1 blocker. D365 is **not** an MCF substrate or service gate blocker. It is scoped narrowly to the runtime evaluation of computed-dimension metrics. MCF Gates M2-M19 proceed without D365. The MCF first-representative-metric program (Gate M20) defers its fiscal-period representative metric until D365 lands, or substitutes another metric class.

**L-node integration boundary.** MCF integrates with the D366 L-node semantic gate as a reader, not as an owner. The L-node verdict tables (`contract.l_node_semantic_verdict` + `contract.l_node_semantic_trace`) are read by MCF where present. As of live verification 2026-05-26, only the L2 trace writer exists (141 green + 25,096 not_applicable verdicts; verdict rows dated 2026-05-15 to 2026-05-17). L1 and L3-L8 writers are absent. MCF does **not** own the construction of L1 or L3 through L8 writers; that work lives in the D366 follow-on track. MCF authoring gates (PE-MC-1 through PE-MC-10) and runtime activation gates (`chain_status.chain_verdict='complete'` plus MLS-14) do not depend on L-node verdicts being complete; L-node verdicts are best-effort semantic-rigor signal layered above the load-bearing gates. **MCF never asserts an L-node verdict exists when it does not.**

**Implementation consequence.** MCF build plan gates M2-M20 proceed per `metric-context-framework-build-plan.md` (commit `40a9adc`). This M1 ADR does not implement substrate, panel, verifier, UI, or BCF enrichment. Step 4 BCF enrichment remains separate and read-only-scoped (read access to `concept_registry.*` and BCF docs authorized; no BCF writes) until explicitly opened. Step 4 selection of the 10 representative metrics is operator-owned and informed by the high-confidence + APQC seed subset per addendum §3.5.

## Decision 10 — Foundational guardrails

Seven guardrails govern MCF. These are presented as a named structural section so they are independently amendable later.

1. **No candidate reservoir creates authority by inclusion.** Inclusion in a reservoir makes a KPI a *candidate*; MCF authoring under Framework Approval creates authority.
2. **BCF enrichment scope is operator + BCF-panel decided, not seed-wording driven.** Seeds inform priority order, not concept selection. BCF concepts are authored under BCF Framework Approval against business reality, not against seed metric `description` text.
3. **Panel rejection of legacy-only grounding is mandatory.** Candidates whose only grounding traces to BF/BO/CF/CM are rejected at intake. The `co_bindings` field on `seed_metrics` is stripped at reservoir-ingestion time (Decision 4).
4. **Duplicate-intent detection is PE-MC-9 at draft → review.** PE-MC-9 (definition uniqueness) runs against `mcf.*`, against pending drafts in the queue, and across the five-class classification (Decision 3).
5. **Source-system assumptions must be made explicit before draft.** If a candidate references "the CRM" or "the SAP system" implicitly, the panel surfaces the assumption via `source_reality.summarize` and routes to operator confirm before draft.
6. **Reservoir provenance is a recorded panel-input field.** `mcf.metric_authoring_panel_run` records reservoir name, reservoir entry ID, reservoir provenance source(s), and reservoir confidence band. Auditable forever.
7. **No SQL MC corpus migration; ever.** The 2 non-archived legacy MCs (Decision 2) go through MCF authoring as if greenfield. No carryover of formula text, binding, or version history beyond an optional `provenance.legacy_mc_uid` reference field on the new MCF MC for operator orientation.

## Substrate commitment

MCF authors new substrate under the `mcf` schema. Tables are enumerated in MCF requirements §17.1 and sequenced in build plan §4 (Gates M2-M6 for identity / lifecycle / publication / panel / tenant-binding substrate; Gates M8-M10 for package signature, fixture substrate, verifier; Gate M11 for reservoir ingestion).

Foundation Governance Substrate sharing (`contract.certification_record`, `contract.framework_policy`, `contract.operator_confirm_rule`) follows MCF requirements §17.3 — MCF writes rows scoped by MCF `action_code` values; BCF writes its own; neither reads or mutates the other's.

## Reversal path

Foundation Invariant III applies: this ADR may be superseded by a future ADR. Supersession is the change mechanism; no in-place edit alters the recorded decisions. Individual decisions within this ADR (e.g. the tool surface in Decision 6 or the seven guardrails in Decision 10) are independently amendable via Errata against the named structural section without re-opening the whole ADR.

## Consequences

This ADR enables MCF build plan Gates M2-M20 to proceed under the recorded authority model. Specifically:
- Gate M2 substrate DBCP design knows the table-naming convention (`mcf.*`), the historical-only status of `contract.metric_contract`, and the reservoir-provenance field requirements on `mcf.metric_authoring_panel_run`.
- Gate M7 AST service design knows the authored-only formula-input discipline (Decision 5).
- Gate M11 reservoir-ingestion service design knows the `co_bindings` strip requirement (Decision 4) and the reservoir-provenance preservation requirement (Decision 3 + guardrail 6).
- Gate M12 panel design knows the workbench tool surface (Decision 6) and the same-workbench / per-agent transcript / fingerprint discipline.
- Gate M13 PE-MC evaluator design knows the MLS-14 + PE-MC-10 layered both-must-pass requirement (Decision 7).
- Step 4 BCF enrichment scope is bounded by the operator-decided concept selection criteria, not by seed wording (guardrail 2).

The MCF arc moves to **Gate M2 (identity substrate DBCP)** as the immediate next gate after this ADR is decided, subject to operator-decision on legacy MC table retirement marker (M0 §9 item 1; recommended low-stakes table comment + README note).
