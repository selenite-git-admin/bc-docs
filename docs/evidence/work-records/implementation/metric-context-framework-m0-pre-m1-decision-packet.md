---
uid: metric-context-framework-m0-pre-m1-decision-packet
title: Metric Context Framework (MCF) — M0 Pre-M1 Operator Decision and Asset Disposition Packet
description: M0 prerequisite packet. Consolidates the nine operator-owned decisions (D1-D9) that must be locked before drafting the foundational MCF ADR (M1). Records explicit asset disposition for ~24 metric-era workflows / services / substrate items (keep / adapt / stale-deprecate / historical-only / gap). Provides exact proposed M1 ADR wording snippets per decision so M1 authoring becomes a near-mechanical exercise once the operator accepts the packet. Not the ADR. Not a build plan. Not a DBCP. Consumes the requirements (13f9bb6), inventory (d9b10d2), gap survey (0ba202b), reservoir/authority addendum (0e3644b), and build plan (40a9adc).
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: pre-adr-decision-packet
---

# Metric Context Framework (MCF) — M0 Pre-M1 Operator Decision and Asset Disposition Packet

## 1. Scope and method

### 1.1 Purpose

Gate M0 in the MCF build plan (`metric-context-framework-build-plan.md`, commit `40a9adc`) requires operator decisions on items 1, 2, 3, and 5 from build-plan §9 plus implicit consolidation of the locked positions (L1-L6) into ADR-ready wording. This packet:

- Consolidates **nine numbered operator decisions** (D1-D9) into a single review surface.
- Provides **exact proposed M1 ADR wording** per decision, so M1 authoring is paste-and-edit, not re-derive.
- Provides explicit **asset disposition** across ~24 metric-era workflows / services / substrate items, so the foundational ADR's "what survives, what doesn't" framing is unambiguous.

### 1.2 What this is not

- **Not the foundational MCF ADR.** M1 authoring follows operator acceptance of this packet.
- **Not a build plan.** Build plan is `40a9adc`.
- **Not an implementation DBCP.** Substrate column lists, indexes, triggers are gate-specific DBCPs that M2+ produces.
- **Not authority-creating.** Recommendations in this packet do not create authority until either (a) the operator explicitly accepts them in this packet's review, or (b) M1 ADR records them.

### 1.3 Method

- Consumes all five prior MCF chain documents.
- Recommendations cite source documents inline.
- Operator-owned positions are flagged with **OPERATOR DECISION** and have a recommendation but no implicit acceptance.
- ADR wording snippets are quoted in blockquotes and labeled `[MANDATORY]` or `[OPTIONAL]` for M1 scope.

### 1.4 MCF is not blank-slate

The MCF arc has been deliberate that MCF is greenfield in its authoring discipline but consumes existing metric-era substrate and services. The inventory (`d9b10d2`) classified ~73 artifacts; this packet collapses the asset-level inventory verdicts into a single review-friendly disposition table (§2), making the kept/adapted/retired/gap state explicit per asset.

### 1.5 Inputs cited

| Doc | Commit | Role in this packet |
|---|---|---|
| `metric-context-framework-requirements.md` | `13f9bb6` | Source for §7-§17 references in proposed ADR wording |
| `metric-context-framework-inventory.md` | `d9b10d2` | Asset verdicts in §2 disposition table |
| `metric-context-framework-gap-survey.md` | `0ba202b` | Live DB counts informing D1-D5 evidence |
| `metric-context-framework-candidate-reservoir-and-authority-classification.md` | `0e3644b` | 5-class classification + 7 guardrails for D2-D3 |
| `metric-context-framework-build-plan.md` | `40a9adc` | Gate sequencing referenced in D6-D9 and §15 |

---

## 2. Asset disposition summary

Twenty-four metric-era assets — workflows, services, substrate items, and planned MCF substrate — with explicit disposition for the MCF era. Disposition vocabulary:

| Disposition | Meaning |
|---|---|
| **keep** | Reusable as-is under MCF, no rework required |
| **adapt** | Useful under MCF but needs rework or guardrails |
| **stale-deprecate** | Obsolete / failed path / incompatible — replace entirely |
| **historical-only** | Substrate exists, MCF reads as reference only, never writes |
| **gap** | Required by MCF, does not exist today |

### 2.1 Disposition table

| # | Asset / workflow | Current role | Disposition | MCF-era role | Evidence source | Operator decision needed? |
|---|---|---|---|---|---|---|
| 1 | `contract.metric_contract` (table) | Active-substrate metric contract table | **historical-only** | Stays queryable; not authoritative; not migrated | Inventory F-CHAIN-3 + Gap survey Q-13 (778/780 archived) | **D1** |
| 2 | `contract.metric_contract_version` (table) | Active-substrate per-version body | **historical-only** | Stays queryable; not authoritative; not migrated | Inventory + Gap survey Q-14 (729 active MCVs on archived parents) | **D1** |
| 3 | `contract.metric_contract_approval` (table) | Decision audit trail | **stale-deprecate** | 0 rows; safe to retire; subsumed by `mcf.metric_publication_eligibility_result` | Inventory + Gap survey Q-1 (0 rows) | No (recommend M0 acceptance) |
| 4 | `metric.metric_binding` (table) | CC-grain binding helper | **historical-only** | MCF authors variable-grain `mcf.metric_variable_binding`; legacy table stays as join helper if any consumer needs it | Inventory F-BIND-2 | **D1** (folded in) |
| 5 | `metric.metric_definition` (table) | KPI catalog (1,241 rows) | **keep** | Candidate-intent reservoir per MCF §5; preserved KPI intent; not authority (PE-MC-1 excludes per §13) | Inventory F-CAT-1, F-CAT-2; Addendum §2.3 | No |
| 6 | `metric.metric_knowledge` (table) | Auxiliary narrative for KPI catalog | **keep** | Weak hint / prompt context per MCF §5 + addendum 5-class | Inventory F-KNOW-1; Addendum §2 | No |
| 7 | Mongo `bc_seed.seed_metrics` (collection, 12,501 docs) | Loosely-formed seed catalog | **keep** | Candidate-intent reservoir per addendum §2.3; stratified by confidence + source | Addendum §3.1 + §3.4 + §3.5 | **D2** + **D3** |
| 8 | `MetricEvaluationEngine` (service) | Runtime engine for snapshot production | **keep** at execution layer; **adapt** at input shape | MCF feeds AST input; engine resolves and applies; preserved per MCF §15.5 | Inventory F-EVAL-1, F-EVAL-2, F-EVAL-3, F-EVAL-4, F-EVAL-5 | No (D4 covers input-shape adapt) |
| 9 | `metric.metric_formula` + `metric_formula_variable` (tables) | Text formula storage + typed variables | **historical-only** | 1,216 text formulas remain as reference; MCF authors `mcf.metric_formula_ast` greenfield | Inventory F-FORM-1, F-FORM-3; Gap survey Q-9, Q-10, Q-11 | **D4** |
| 10 | `metric.metric_formula_verification` (table) | Maker/Checker/Moderator log | **stale-deprecate** | Predates workbench framing; new content goes to `mcf.metric_authoring_panel_run` + `mcf.metric_authoring_panel_transcript` | Inventory §3.1 + F-FORM-1 | No (recommend M0 acceptance) |
| 11 | `FormulaAuditService` (service, D315) | Text formula audit | **adapt** | Text-audit role retires; MCF AST taxonomy validity (PE-MC-5) replaces. 27 banned-function formulas (2.2%) addressed via taxonomy decision | Inventory F-FORM-1; Gap survey Q-16 | No (D4 covers) |
| 12 | Fiscal calendar stack: `master.dim_date` + `master.dim_fiscal_calendar` + `master.dim_fiscal_period` + `organization.fiscal_calendar_config` + `FiscalCalendarService` | Date and fiscal calendar substrate + service | **keep** | MCF computed-dimension resolver per §9; fixture resolver config substitutes at verification time | Inventory F-FISC-1, F-FISC-2 | No |
| 13 | `contract.canonical_contract.posting_date_field` (planned column per D365) | Not implemented | **gap** | Hard runtime prerequisite for MCF computed-dimension MCs; fixture resolver does not substitute at runtime | Gap survey Q-7 (column does not exist) | **D6** |
| 14 | `contract.chain_status` + `contract.chain_trace` + `ChainStatusService` | DEC-bebaec SSOT for chain completeness | **keep** | MCF consumes for L1-L7 chain completeness signals | Inventory F-CHAIN-1, F-CHAIN-2 | No |
| 15 | `IntegrityService` (deprecated per DEC-bebaec) | Pre-DEC-bebaec chain checker | **stale-deprecate** | Final removal pending consumer-map cleanup; not MCF scope to remove | Inventory F-CHAIN-1; CLAUDE.md | No (existing deprecation continues) |
| 16 | `metric.readiness_ledger` + `metric.mc_dependency` (D316) | Readiness scheduler substrate | **keep** | MCF reads as MLS 15-25 input signal | Inventory F-READY-1 | No |
| 17 | MLS substrate (`metric.mls_state` + `mls_state_event` + `mls_trigger_binding`) + services (`MlsStateRecorder`, `MlsProbeRegistry`, `MlsBackfillService`) | D389-D393 lifecycle ledger | **keep** | MCF integrates per §14; does not re-implement | Inventory F-MLS-1; Gap survey Q-5 | No |
| 18 | `Mls14ActivationGate` + `Mls14SignatureHashService` (D391) | Phased-v1 semantic activation gate | **keep** | Layered with PE-MC-10 (both-must-pass) per D5 | Inventory F-FORM-2, F-MLS-2 | **D5** |
| 19 | `contract.l_node_semantic_verdict` + `contract.l_node_semantic_trace` (tables) + L-node writer | Schema present; only L2 writer exists (per gap survey §2.3.2 refined finding); L1 + L3-L8 absent | **adapt** (substrate keep; service partial-gap) | MCF reads when present; D366 follow-on track owns the L1+L3-L8 writers | Inventory F-LNODE-1 refined; Gap survey §2.3.2; Q-5 | **D7** |
| 20 | `mc-onboarding.service.ts` (with header β-path / slice (0) plan) | MC envelope authoring path | **adapt** | Header β-path repair per SES-594568 before MCF reuses; SERVICES-ONLY discipline | Inventory F-FORM-3 | No (covered by build plan M11) |
| 21 | Helper scripts (160 surveyed per BCF E2) | Catalog of operator helper scripts | **adapt** (banded) | BCF E2 verdict reused wholesale; MCF does not introduce text-parser scripts | Inventory F-READY-3 | No |
| 22 | `MetricWizardService` (quarantined per BCF G15) | Free-form metric wizard | **stale-deprecate** | MCF AST builder UI is structural replacement | Inventory F-WIZ-1 | No |
| 23 | bc-admin metric catalog / read surfaces (readiness, chain-status, MLS, metric-catalog, metric-definitions pages) | Live consumers | **keep** | MCF read endpoints serve same surfaces; new MCF Detail surfaces add fields | Inventory §5; Build plan M16 | No |
| 24 | bc-admin metric authoring surfaces (formula AST builder, fixture authoring, panel run audit) | **gap** | Greenfield UI per MCF §18; build plan M17 | MCF requirements §18.2-18.4; Build plan M17 | **D8** (BCF density dependency) |
| 25 | `mcf.*` schema + all substrate tables per MCF §17.1 | **gap** | Greenfield; build plan M2-M6 + M9 + M11 + parts of M5 + M7 | MCF requirements §17.1; Build plan §4.2-4.3 | **D1** (table-name disposition) |
| 26 | Metric Authoring Panel workbench (three-model, closed-verdict, grounding) | **gap** | Greenfield; build plan M12 | MCF requirements §11.3; Build plan M12 | No (D2 + D4 cover input discipline) |
| 27 | Deterministic verifier + self-verification fixture system (`mcf.metric_self_verification_fixture` + `mcf.metric_self_verification_result` + verifier service) | **gap** | Greenfield; build plan M9 + M10 | MCF requirements §12; Build plan M9, M10 | **D5** (layering with MLS-14) |
| 28 | `envelope.metric_snapshot` (retiring per D369) | Runtime snapshot table | **adapt** | Dual-write transition with `fact.ms_*_v*`; MCF reads authoritative side TBD per M14/M15 sequencing | Inventory F-SNAP-1; Gap survey §3.1 | No (D369 owner schedules; out of M0 scope) |

### 2.2 Disposition counts

| Disposition | Count |
|---|---:|
| keep | 7 |
| adapt | 6 |
| stale-deprecate | 4 |
| historical-only | 4 |
| gap | 7 |
| **Total** | **28** |

(Counts exceed the 24 estimate because some operator-listed items resolved into multiple distinct assets — e.g. "fiscal calendar stack" is 1 line but 5 tables + 1 service.)

---

## 3. Decision D1 — Historical SQL metric-contract corpus

### 3.1 Recommended decision

Existing `contract.metric_contract`, `contract.metric_contract_version`, and `metric.metric_binding` are **historical-only / non-authoritative**. No migration into MCF substrate. The 2 non-archived MCs (`mc__revenue_collection_rate` and `mc__ar_growth_rate`, both 2026-05-14 drafts, both `audit_status_code='pending'`) are pre-MCF-retired or candidate-only; if still valuable, they must be re-authored from scratch as MCF MCs under MCF Framework Approval.

### 3.2 Rationale (from gap survey Q-13 + Q-14 + Q-15 + addendum §3.2)

- 778 of 780 `contract.metric_contract` rows are already archived (`archived_at IS NOT NULL`).
- 729 active MCVs reference archived parent MCs — a pre-existing data-state inconsistency, not introduced by MCF.
- The 2 non-archived MCs are recent draft experiments authored 2026-05-14, both still pending formula audit.
- The approval table (`contract.metric_contract_approval`) has 0 rows — the legacy approval path is unused.
- Substrate was built over now-gone BF/BO/CF/CM. Re-verifying any specific row's semantic content costs as much as authoring it greenfield. There is no salvage shortcut.

This recommendation does NOT violate MCF requirements §16 migration-free stance, because §16 was authored against quarantined / dropped substrate, and 778/780 of the legacy MC corpus is already archived — substantively in the same category.

### 3.3 Proposed M1 ADR wording — `[MANDATORY]`

> **Legacy SQL metric contract corpus disposition.** The existing `contract.metric_contract` (780 rows, 778 of which are archived), `contract.metric_contract_version` (1,022 rows), and `metric.metric_binding` (1,133 rows) substrate is historical-only under MCF. MCF does not migrate any row into its substrate. The two non-archived legacy MCs are operator-reviewed; if retained as candidates, they are re-authored from scratch under MCF Framework Approval, with no carryover of formula text, binding, or version history beyond an optional `provenance.legacy_mc_uid` reference field on the new MCF MC for operator orientation. The existing legacy tables remain queryable as historical reference. New MCF metric contracts live under `mcf.metric_contract` in the `mcf` schema.

### 3.4 Sub-decisions

| Sub-decision | Recommendation | Action |
|---|---|---|
| Disposition of the 2 non-archived legacy MCs | Operator-reviewed; archive or re-author candidate | **OPERATOR DECISION** at M0 |
| Explicit retirement marker on `contract.metric_contract` (table comment / README) | Yes — trivial cost, prevents future confusion | **OPERATOR DECISION** at M0 |
| Optional `provenance.legacy_mc_uid` reference column on `mcf.metric_contract` | Recommended for operator orientation; not load-bearing | **OPERATOR DECISION** at M0 or M2 DBCP |

---

## 4. Decision D2 — Candidate reservoirs vs authority

### 4.1 Recommended decision

**Reservoirs inform authoring; only BCF + MCF gates create authority.**

Candidate-intent reservoirs at MCF first-deployment:

- Mongo `bc_seed.seed_metrics` (12,501 docs)
- Preserved platform `metric.metric_definition` / `metric.metric_knowledge` (1,241 + 1,241 rows)
- Operator-direct authoring submissions

Authority creators:

- **Semantic authority** — BCF Registry (`concept_registry.entity` / `business_concept` / `characteristic` active rows). Created under BCF Framework Approval.
- **Binding authority** — `mcf.metric_variable_binding`. Created under MCF Framework Approval (panel + operator confirm).
- **Formula / package authority** — `mcf.metric_formula_ast` + passing `mcf.metric_self_verification_result`. Created under MCF AST authoring + deterministic verifier.

### 4.2 Rationale (from addendum §2.1 + §2.2)

Five-class classification distinguishes:

| Class | Authority? | Examples |
|---|---|---|
| Candidate intent | No | Three reservoirs above |
| Weak hint / prompt context | No | `metric_knowledge` prose; seed descriptions; legacy formula text; operator-attached business guidance |
| Semantic authority | Yes (BCF) | `concept_registry.*` active rows |
| Binding authority | Yes (MCF) | `mcf.metric_variable_binding` post-Framework-Approval |
| Formula authority | Yes (MCF) | `mcf.metric_formula_ast` + passing verifier result |

The discipline prevents: "we saw it in the seed catalog, therefore it's a real metric"; "it computed snapshots in the legacy SQL MC, therefore its formula is correct"; "it has APQC provenance, therefore its definition is grounded". None of those constitute authority claims under MCF.

### 4.3 Proposed M1 ADR wording — `[MANDATORY]`

> **Candidate reservoirs versus authority.** MCF candidate-intent reservoirs are (a) Mongo `bc_seed.seed_metrics` (12,501 docs), (b) the preserved platform `metric.metric_definition` / `metric.metric_knowledge` carve-out, and (c) operator-direct authoring submissions. All three are candidate-intent only; none carries authority. Inclusion in a reservoir does not create an MCF metric contract.
>
> BCF Registry (`concept_registry.*` active rows) is the sole semantic binding authority. MCF authoring under Framework Approval — three-model panel + operator confirm + deterministic verifier — is the sole binding-authority and formula-authority creator.
>
> **Reservoirs inform authoring; only BCF + MCF gates create authority.**

---

## 5. Decision D3 — Seed metric intake hygiene

### 5.1 Recommended decision

The reservoir-ingestion service (build plan M11) **strips the legacy `co_bindings` field** and any other BF/BO/CF/CM-derived fields from Mongo seed metric documents before any panel sees them. Reservoir provenance (the `sources[]`, `confidence`, `created_at`, `metric_name`, `description`, `function_code`, `subfunction_code` fields) is preserved.

### 5.2 Rationale (from addendum §3.1 + risk R-03 + R-14)

- 506 of 12,501 `seed_metrics` docs have `co_bindings IS NOT NULL` (4% of reservoir). These fields carry pre-D418-era binding fragments.
- The working rule binding in MCF requirements §1 forbids BF/BO/CF/CM as evidence, source, lineage, bridge, migration input, compatibility shim, design input, or inspiration.
- Relying on panel discipline alone to reject legacy-bound candidates is structurally weaker than removing them at ingestion. The ingestion-layer strip is the structural enforcement.
- Reservoir provenance fields are needed for PE-MC-1 grounding (APQC source qualifies as bc-seed lineage class b; internet source needs additional grounding per class d).

### 5.3 Proposed M1 ADR wording — `[MANDATORY]`

> **Reservoir intake hygiene.** The reservoir-ingestion path that conveys candidates from `bc_seed.seed_metrics` (or any future Mongo / Postgres reservoir) into the MCF intake queue strips the legacy `co_bindings` field and any other BF/BO/CF/CM-derived fragment fields at ingestion time. The reservoir-ingestion path strips legacy fragments before placing the candidate-intent reference in the panel's trigger queue. When the panel opens its workbench, the legacy fragments are absent from every read tool's response. The strip is enforced at the ingestion service; no other write path may insert into the intake queue. Reservoir provenance (source list, confidence band, original metric name, description, function/subfunction classification) is preserved and recorded as `mcf.metric_authoring_panel_run` provenance metadata for every candidate the panel considers.

---

## 6. Decision D4 — Formula authority

### 6.1 Recommended decision

**AST is authored and governed under MCF; legacy formula text is weak hint only and never authority.** The MCF formula AST authoring service accepts AST input only; no text-parsing entry point exists on the authoring path. A parser may exist as a separately-authorized Step 4 / Step 5 enrichment helper — strictly as proposal-seed input that flows through the MCF panel-proposes / operator-confirms / platform-verifies path. The parser is never a migration path and never an authority creator.

### 6.2 Rationale (from gap survey Q2 + addendum + risk R-02)

- 1,216 legacy `metric.metric_formula` rows carry text formulas (100% of population).
- 134 distinct text shapes across 1,216 rows. Top patterns: `O1 = (I1 / I2) * C1` (435), `O1 = I1 / I2` (252), `O1 = I1 - I2` (86), `O1 = I1` (80).
- Average formula length 18 chars — these are formal-symbol formulas in disguise, structurally close to AST already, but never authored as AST.
- 27 of 1,216 formulas (2.2%) use banned functions (ML_MODEL, QUALITATIVE_ASSESSMENT, STDDEV, SUM_BY_CATEGORY, WEIGHTED_AVG). MCF AST v1 taxonomy decision determines whether these get added or whether the affected MDs need new formulas.
- The structural risk: any path that parses legacy text into AST and treats the parsed AST as authority re-introduces the substrate-shape dependencies the parser cannot see.

### 6.3 Proposed M1 ADR wording — `[MANDATORY]`

> **Formula authority discipline.** Under MCF, a metric contract's formula is authored as an Abstract Syntax Tree (AST) from the closed taxonomy specified in MCF requirements §7.2. The authoring path accepts AST input only. Legacy formula text (the 1,216 rows in `metric.metric_formula` and any text-form formula material in reservoir candidates) is weak hint / prompt context for the authoring panel; it is never authority. A parser that converts legacy text into a proposed AST may exist only as a workbench read tool that exposes the legacy text as one weak-hint context among many. The panel reads it, reasons over it alongside other workbench reads, and proposes an AST. The parser produces no authority and writes no substrate. Its output enters MCF substrate only through the panel-proposes / operator-confirms / platform-verifies path. No code path is permitted to write a parsed AST directly into `mcf.metric_formula_ast`.

---

## 7. Decision D5 — MLS-14 and PE-MC-10 layering

### 7.1 Recommended decision

**Both MLS-14 and PE-MC-10 must pass independently for an MCF MC to reach active state.** MLS-14 (substrate-identity / semantic-signature gate per D391) and PE-MC-10 (deterministic package self-verification per MCF §13.10) check different surfaces; neither subsumes the other; neither weakens.

### 7.2 Rationale (from gap survey §2.3.3)

- MLS-14 catches substrate-identity collapse: two formula variables resolving to the same `(canonical_field, business_field, source_table, source_field, filter, grain_role, time_window)` signature. The MT-04971 specimen (`SUM(WRBTR)/SUM(WRBTR) = 1.0`) is the canonical case.
- PE-MC-10 catches executable-behavior errors: formula does not compute correctly given declared inputs; unit conversion off; window off-by-one; null-handling wrong.
- A formula could pass PE-MC-10 (correct given fixture inputs) yet fail MLS-14 (substrate collapse). Conversely, a formula could pass MLS-14 (signatures distinct) yet fail PE-MC-10 (compute error).
- The gates are complementary, not duplicative.

### 7.3 Proposed M1 ADR wording — `[MANDATORY]`

> **Layered activation gates: MLS-14 and PE-MC-10.** An MCF metric contract reaches active state only when (a) `chain_status.chain_verdict = 'complete'`, (b) MLS-14 semantic activation gate returns green (substrate-identity check per D391), and (c) PE-MC-1 through PE-MC-10 publication eligibility checks all pass, where PE-MC-10 cites a passing `mcf.metric_self_verification_result` whose bound `package_signature_hash` matches the MC's current hash. MLS-14 and PE-MC-10 check different surfaces; both apply; neither subsumes the other; neither weakens. Failure of either blocks activation.

---

## 8. Decision D6 — D365 `posting_date_field` prerequisite

### 8.1 Recommended decision

D365 implementation (add `posting_date_field` column to `contract.canonical_contract` + populate for the 56 existing CCs) is a **runtime prerequisite for any MCF metric contract that references a computed dimension** (fiscal_period, fiscal_year, fiscal_quarter, or any time_anchor_resolution AST node). D365 is **not** a blocker for M1 ADR or for Phase B/C substrate/service gates. It is a prerequisite specifically scoped to the M20 fiscal-period representative metric and any subsequent computed-dimension MC.

Recommended scheduling: D365 lands before M20, or M20 ships 9 of 10 representative metric classes with the fiscal-period class deferred to a M20 follow-on.

### 8.2 Rationale (from gap survey Q-7 + build plan §5.3)

- `contract.canonical_contract.posting_date_field` column does **not** exist in current schema (verified via `information_schema.columns`).
- D365 / DEC-a8e8fc was decided but never implemented at the table level. Phase 2 migration (TSK-53edc3) is blocked per memory `fiscal_calendar_architecture.md`.
- MCF §9.2 resolver fixture config (Section C of fixtures) substitutes for tenant config at **verification time**, not runtime. The fixture mechanism works without D365; runtime evaluation does not.
- D365 owner is not the MCF build plan owner (D365 lives in the fiscal-calendar stack track).

### 8.3 Proposed wording — `[OPTIONAL for M1 ADR; MANDATORY for build-plan prerequisite section]`

This decision is operationally a **build-plan prerequisite** more than an ADR commitment. If included in M1 ADR, recommended wording:

> **D365 `posting_date_field` runtime prerequisite.** Runtime evaluation of MCF metric contracts that reference a computed dimension (fiscal_period, fiscal_year, fiscal_quarter, or any `time_anchor_resolution` AST node) requires `contract.canonical_contract.posting_date_field` to be populated for the referenced canonical contracts. This is a non-MCF prerequisite (the column and its population belong to the D365 fiscal-calendar track). MCF substrate, service, and authoring gates (M2-M19 of the MCF build plan) do not block on D365. The MCF first-representative-metric program (M20) defers the computed-dimension representative metric until D365 lands, or that metric is replaced with a non-computed-dimension representative.

### 8.4 Alternative wording — `[RECOMMENDED]`

Keep D365 entirely out of M1 ADR; record it as a build-plan §5.3 prerequisite only. M1 ADR scope stays focused on MCF authority and substrate boundaries; D365 is a separable track that does not need ADR-grade commitment from M1.

---

## 9. Decision D7 — L-node ownership

### 9.1 Recommended decision

**L-node L1 + L3-L8 writer construction is a D366 follow-on track, not MCF-owned.** MCF reads L-node verdicts when present (the L2 writer that exists today is consumed as best-effort signal); MCF does not pretend L-node verdicts exist when they do not. MLS-14 + PE-MC-10 + `chain_status` carry the gating load; L-node verdicts add semantic-rigor signal where present but do not gate MCF activation.

### 9.2 Rationale (from gap survey §2.3.2)

- Live DB query (Q-5) shows: 202 `contract.l_node_semantic_verdict` rows + 25,237 `contract.l_node_semantic_trace` rows.
- Trace rows are L2-only (141 green + 25,096 not_applicable). L1 + L3-L8 are absent.
- Verdict rows date 2026-05-15 → 2026-05-17 (a recent backfill or partial writer; no continuous service).
- Inventory F-LNODE-1 was partially incorrect ("no service writer exists"); refined finding: partial-gap (L2 writer present, L1+L3-L8 absent).
- Per CLAUDE.md, the D366 session-close gate fails-open on infrastructure outages — consistent with this partial state.

### 9.3 Proposed M1 ADR wording — `[MANDATORY]`

> **L-node semantic gate integration.** MCF integrates with the D366 L-node semantic gate as a reader, not as an owner. The L-node verdict tables (`contract.l_node_semantic_verdict` + `contract.l_node_semantic_trace`) are read by MCF where present (L2 trace writer currently lives in a backfill / partial-service state per gap survey §2.3.2). MCF does not own the construction of L1 or L3 through L8 writers; that work lives in the D366 follow-on track. MCF authoring gates (PE-MC-1 through PE-MC-10) and runtime activation gates (`chain_status.chain_verdict='complete'` plus MLS-14) do not depend on L-node verdicts being complete; L-node verdicts are best-effort semantic-rigor signal layered above the load-bearing gates. MCF never asserts an L-node verdict exists when it does not.

---

## 10. Decision D8 — M1 before BCF enrichment

### 10.1 Recommended decision

**M1 foundational ADR proceeds before BCF enrichment lands.** Implementation gates that require actual BCF concept density for meaningful operator use (M17 operator console draft/AST/fixture authoring; M18 tenant binding console; M20 first representative metric program) remain blocked on minimum BCF density per build plan §5.1. All other gates (M2-M16 and M19, totaling 16 of 21 gates) can proceed in parallel with BCF enrichment.

### 10.2 Rationale (from build plan §5.1 + §5.2)

- M1 ADR establishes framework scope, actors, authority model, substrate boundaries. None of these require BCF concepts to exist; they require the BCF Registry to be referenceable (already true per D418 Gate 5.3 verification).
- M2-M16 + M19 are BCF-content-agnostic: substrate is shape, not concept-density-dependent; services operate on AST + fixtures + bindings (where binding *targets* are BCs, but service implementation is BCF-shape-aware not BCF-density-dependent).
- M17 / M18 / M20 are BCF-density-dependent (UI shows BCs in pickers; program authors against real BCs).

### 10.3 Proposed M1 ADR wording — `[OPTIONAL]`

This is a build-plan sequencing position more than an ADR commitment. If included:

> **MCF and BCF enrichment sequencing.** The foundational MCF ADR and the MCF substrate/service gates do not block on BCF concept-density enrichment. BCF enrichment for MCF (Step 4 of the MCF arc) runs in parallel with MCF Phase B (substrate) and Phase C (services). MCF authoring surfaces, tenant binding console, and the first-representative-metric program land after BCF enrichment provides the minimum concept density specified in MCF build plan §6.

### 10.4 Alternative wording — `[RECOMMENDED]`

Keep this out of M1 ADR; record as build-plan §5 sequencing only.

---

## 11. Decision D9 — BCF read access for Step 4

### 11.1 Recommended decision

Step 4 BCF enrichment planning is authorized to read `concept_registry.*` schema (BCF Registry) and BCF requirements / inventory / build-plan / gap-research documents. Access is **read-only** and is for enrichment scoping only; no BCF substrate writes are authorized under this decision (BCF Framework Approval owns BCF writes per the BCF arc).

### 11.2 Rationale (from gap survey §1.3 + addendum §8.4)

- `concept_registry` schema was outside the bc-postgres MCP allowlist for the Step 2 gap survey session.
- Step 4 enrichment cannot meaningfully scope minimum density without live `concept_registry` reads.
- BCF Framework Approval (DEC-149ab2 / D411) governs BCF writes; this decision does not extend any write authority into BCF.

### 11.3 Proposed Step 4 authorization wording — `[MANDATORY for Step 4 brief]`

> **Step 4 read access.** The MCF Step 4 BCF enrichment program is authorized read-only access to (a) the `concept_registry.*` schema in `bc_platform_dev` for live BCF Registry density inspection, and (b) the BCF requirements, inventory, build-plan, and gap-research documents under `bc-docs-v3/docs/implementation/`. This authorization is for enrichment scoping only. No BCF substrate writes are authorized; BCF Framework Approval per DEC-149ab2 / D411 governs all BCF writes.

### 11.4 Practical implementation

Update the bc-postgres MCP schema allowlist to include `concept_registry` for the Step 4 session(s). Revert after Step 4 if read-only-per-session is preferred over standing access.

---

## 12. Disposition-to-M1 mapping

### 12.1 What M1 ADR must declare

The M1 ADR is the **framework-establishing ADR**. Its mandatory scope:

1. **Framework scope** (MCF requirements §2): what MCF governs (metric meaning, formula AST, variable bindings, computed dimensions, MLS overlay, tenant binding) and what it does not (BCF scope, runtime evaluation, tenant onboarding workflow beyond MLS).
2. **Authority model**: Framework Approval definition per MCF §11; reservoirs vs authority per D2; MLS-14 + PE-MC-10 layering per D5.
3. **Substrate boundaries**: `mcf.*` schema commitment per D1; Foundation Governance Substrate sharing per MCF §17.3.
4. **Discipline rules**: AST authoring per D4; reservoir intake hygiene per D3; L-node integration boundary per D7; no migration per D1.
5. **Named structural sections**: the 5-class classification (addendum §2) and the 7 guardrails (addendum §5) as standalone amendable sections.

### 12.2 What stays in implementation-plan scope (build plan, not ADR)

- Gate sequencing M0-M20 (build plan §3-§4)
- Parallelization map (build plan §5)
- BCF enrichment interface (build plan §6)
- First-representative-metric criteria (build plan §7)
- Risk register (build plan §8)
- D365 sequencing (per D6 — recommended out of M1 ADR)
- M1-before-enrichment sequencing (per D8 — recommended out of M1 ADR)

### 12.3 What stays in future DBCP scope

- Column lists, indexes, triggers, constraints for `mcf.*` substrate (M2-M6 + M9 + parts of M5 + M7 DBCPs)
- Drizzle schema additions
- Read/write repository patterns
- Migration sequencing (greenfield create per MCF §16)
- Workbench tool-set v1 schemas (MCF §19.12 Q32)
- Evidence-source allowlist composition (MCF §19.12 Q33)
- Operator-confirm rule completeness (MCF §19.6 Q17)

### 12.4 What stays in operational program scope

- KPI catalog re-authoring rate / cadence (build plan M20; ongoing post-M17)
- Calibration sampling rate per stage (MCF requirements §11.3.x)
- Operator-confirm rule tuning over time
- Reservoir banding / quality-filter calibration

### 12.5 Authority-boundary discipline

M1 ADR records **authority boundaries** (who can do what, under what discipline, with what evidence). It does not record:

- Implementation details (those live in DBCPs).
- Sequencing details (those live in build plan).
- Operational tuning (those live in calibration program).

Keeping M1 ADR narrow makes it amendable per-decision later without re-deciding the whole framework.

---

## 13. Decision table

Consolidated D1-D9 with operator-actionable next steps.

| ID | Decision | Recommendation | Evidence source | Owner | Operator action needed | Consequence if not decided |
|---|---|---|---|---|---|---|
| **D1** | Historical SQL MC corpus disposition | Historical-only; no migration; 2 non-archived MCs operator-reviewed | Gap survey Q-13/14/15; addendum §3.2 | Operator (architecture owner) | **Accept** (with sub-decisions on 2 non-archived MCs + retirement marker) | M2 substrate DBCP cannot lock table-naming; M1 ADR has unresolved scope |
| **D2** | Reservoirs vs authority | 3-reservoir candidate-intent layer; BCF + MCF gates create authority | Addendum §6 | Operator | **Accept** (or revise wording) | M1 ADR has unresolved authority model; M11 reservoir-ingestion has unresolved scope |
| **D3** | Seed metric intake hygiene | Strip `co_bindings` at ingestion; preserve provenance | Addendum guardrail #3; risks R-03 + R-14 | Operator | **Accept** | M11 ingestion service has unresolved scope; legacy substrate leak risk persists |
| **D4** | Formula authority discipline | AST authored, never parsed-text-as-authority; parser as helper only | Gap survey Q2; addendum L4 | Operator | **Accept** (or revise to allow parser as service input — not recommended) | M7 AST service has unresolved input shape; risk R-02 (formula TEXT temptation) persists |
| **D5** | MLS-14 + PE-MC-10 layering | Both-must-pass; neither subsumes; neither weakens | Gap survey §2.3.3 | Operator | **Accept** | M13 PE-MC evaluator scope unclear; activation gate semantics ambiguous |
| **D6** | D365 prerequisite scoping | Runtime prerequisite for computed-dimension MCs only; not M2-M19 blocker; build-plan-scoped | Gap survey Q-7; build plan §5.3 | Operator (with D365 owner coordination) | **Accept** scope (and **schedule** D365 separately) | M20 fiscal-period metric may not ship; risk R-06 |
| **D7** | L-node ownership | D366 follow-on track owns L1+L3-L8 writers; MCF reads best-effort | Gap survey §2.3.2; inventory F-LNODE-1 refined | Operator | **Accept** boundary | M-gate ownership unclear; risk R-05 may escalate |
| **D8** | M1 before BCF enrichment | Yes; M2-M16+M19 parallel-safe; M17/M18/M20 blocked on enrichment | Build plan §5.1, §5.2 | Operator | **Accept** sequencing | Build plan sequencing ambiguous; risk of waiting unnecessarily |
| **D9** | BCF read access for Step 4 | Read-only access authorized on `concept_registry.*` + BCF docs | Gap survey §1.3; addendum §8.4 | Operator | **Authorize** (one-line allowlist update) | Step 4 cannot meaningfully scope BCF density; M20 deferred |

---

## 14. Proposed M1 ADR insertion list

Consolidated wording snippets, paste-and-edit ready for M1 ADR authoring. Marked `[MANDATORY]` if required for the framework-establishing ADR, `[OPTIONAL]` if better placed in build plan or follow-on.

### 14.1 `[MANDATORY]` — Five-class reservoir/authority classification (from addendum §2.1, expanded D2)

> **Five-class reservoir and authority classification.**
>
> | Class | Role | Creates authority? |
> |---|---|---|
> | Candidate intent | "This KPI is worth considering for MCF authoring" | No |
> | Weak hint / prompt context | Panel may reference for reasoning, never cite as grounding | No |
> | Semantic authority | "This business concept IS this in the vocabulary" | Yes — BCF Framework Approval |
> | Binding authority | "This MC variable binds to this business concept" | Yes — MCF Framework Approval |
> | Formula authority | "This is what this metric contract computes" | Yes — MCF AST authoring + deterministic verifier |
>
> Two operative rules. (1) Candidate intent triggers the panel to open a governed workbench; weak-hint sources are available to the panel through read tools within that workbench. Neither becomes authority. The panel's investigation through broad governed read awareness of governed platform surfaces produces a proposed package; the package is the panel's output, never its input. (2) No reservoir creates an MCF metric contract by inclusion.

### 14.2 `[MANDATORY]` — Reservoirs and authority decision (from §4.3)

> **Reservoirs inform authoring; only BCF + MCF gates create authority.**
>
> MCF candidate-intent reservoirs are (a) Mongo `bc_seed.seed_metrics`, (b) the preserved platform `metric.metric_definition` / `metric.metric_knowledge` carve-out, and (c) operator-direct submissions. BCF Registry (`concept_registry.*` active rows) is the sole semantic binding authority. MCF authoring under Framework Approval — three-model panel + operator confirm + deterministic verifier — is the sole binding-authority and formula-authority creator.
>
> The candidate-intent reservoir entry triggers panel authoring; it does not bound the panel's reasoning. The panel opens a governed workbench, reads broadly through allowed tools (active BCF Registry, candidate reservoirs, source reality summaries, fiscal calendar / computed-dimension config, prior MCF state, chain/readiness/MLS summaries), and proposes the package as the result of that investigation.

### 14.3 `[MANDATORY]` — Legacy SQL MC corpus disposition (from §3.3)

> See §3.3 for full wording.

### 14.4 `[MANDATORY]` — Reservoir intake hygiene (from §5.3)

> See §5.3 for full wording.

### 14.5 `[MANDATORY]` — Formula authority discipline (from §6.3)

> See §6.3 for full wording.

### 14.6 `[MANDATORY]` — Layered activation gates (from §7.3)

> See §7.3 for full wording.

### 14.7 `[MANDATORY]` — L-node integration boundary (from §9.3)

> See §9.3 for full wording.

### 14.8 `[MANDATORY]` — Seven guardrails (from addendum §5; verbatim, presented as a named structural section)

> **MCF foundational guardrails.**
>
> 1. **No candidate reservoir creates authority by inclusion.** Inclusion in a reservoir makes a KPI a *candidate*; MCF authoring under Framework Approval creates authority.
> 2. **BCF enrichment scope is operator + BCF-panel decided, not seed-wording driven.** Seeds inform priority order, not concept selection.
> 3. **Panel rejection of legacy-only grounding is mandatory.** Candidates whose only grounding traces to BF/BO/CF/CM are rejected at intake. The `co_bindings` field on `seed_metrics` is stripped at reservoir-ingestion time.
> 4. **Duplicate-intent detection is PE-MC-9 at draft → review.** Runs against `mcf.*`, against pending drafts in the queue, and across the five-class classification.
> 5. **Source-system assumptions must be made explicit before draft.** Implicit references to specific source systems route to operator confirm before draft.
> 6. **Reservoir provenance is a recorded panel-input field.** `mcf.metric_authoring_panel_run` records reservoir name, entry ID, provenance source(s), and confidence band.
> 7. **No SQL MC corpus migration; ever.** The two non-archived legacy MCs are operator-reviewed; if retained, re-authored from scratch.

### 14.9 `[MANDATORY]` — MCF panel operates as a governed workbench, not a packet consumer (NEW per M0 correction)

> **MCF panel operates as a governed workbench, not a packet consumer.**
>
> A candidate-intent reference (from a reservoir or from operator-direct submission) *triggers* the MCF Metric Authoring Panel to open a governed workbench. The candidate-intent reference is the *trigger*, not the *cage*. The panel investigates the governed platform broadly through a closed set of read tools and proposes a metric package as the result of that investigation. The package is the panel's output, never its input.
>
> **Allowed read tool surface (v1; ADR-amendable as a named section):**
>
> | Tool | Purpose |
> |---|---|
> | `bcf_registry.read_*` | Active BCF Entities, BusinessConcepts, Characteristics; reachability probes; lifecycle history |
> | `reservoir.read_seed_metric` | `bc_seed.seed_metrics` rows by id (post `co_bindings` strip per D3) |
> | `reservoir.read_metric_definition` | `metric.metric_definition` + `metric.metric_knowledge` rows by id |
> | `source_reality.summarize` | What source / admission / observation contracts emit for a tenant; what fields exist |
> | `fiscal_calendar.read_config` | Tenant fiscal calendar config and computed-dimension governing configs |
> | `mcf.read_drafts` | Current MCF drafts in intake / draft / review queues |
> | `mcf.read_active_packages` | Active MCF metric contracts (by id, by function, by grain entity) |
> | `panel_history.read` | Prior panel runs and rejection-log entries for the same candidate area |
> | `formula_library.read_patterns` | Catalog of legacy formula shapes (e.g. the 134 distinct shapes per gap survey Q-11) as weak-hint reference only |
> | `chain_status.read` | `chain_status` / `chain_trace` for a candidate's prospective bindings |
> | `readiness.read` | `readiness_ledger` / `mc_dependency` summaries |
> | `mls.read_state` | MLS state ledger summaries (MLS-13, MLS-14) |
> | `evidence.search` / `evidence.retrieve` | Allowed evidence corpora (standards, bc-seed, curated excerpts) |
>
> **Forbidden tool surfaces (load-bearing):**
>
> - Raw DB / SQL access
> - Tenant row-level raw data (admitted observation rows, source rows)
> - Any tool that writes to substrate (writes flow only through MCF Framework Approval: panel proposes → operator confirms → substrate service writes)
> - Any tool that touches dropped BF/BO/CF/CM substrate (physically gone post-D418; even if reintroduced, the working rule forbids)
> - Arbitrary application tables not on the read allowlist
> - Unscoped operator notes (operator-attached business guidance is a tracked workbench input — hashed into the workbench fingerprint, visible in transcripts — not a free-form data plane)
> - Arbitrary internet retrieval (citations must come from the evidence allowlist)
> - Tools that write `concept_registry.*` (BCF Framework Approval territory, not MCF panel scope)
> - Tools that bypass PE-MC-1 through PE-MC-10 gates
>
> **Transcript discipline.** Every tool call is logged in the per-agent transcript with input hash + output hash + timestamp. Tool calls are replayable as audit evidence; they are not re-used as authority unless the panel cites them correctly through PE-MC-1 grounding.

### 14.10 `[OPTIONAL]` — D365 runtime prerequisite note (from §8.3)

> See §8.3 for full wording. Recommended **NOT** included in M1 ADR; recorded in build plan §5.3 only.

### 14.11 `[OPTIONAL]` — MCF-before-BCF-enrichment sequencing (from §10.3)

> See §10.3 for full wording. Recommended **NOT** included in M1 ADR; recorded in build plan §5.1 only.

### 14.12 ADR structural recommendation

M1 ADR should organize the mandatory snippets as named structural sections (not buried in prose body) so each is independently amendable later:

```
ADR-mcf-{uid}.md
├── Frontmatter (uid, title, status: decided, date, project, domain, subdomain, focus)
├── Context (why MCF; relationship to BCF; post-D418 grounding)
├── Decision: Framework scope (per MCF §2)
├── Decision: Five-class reservoir/authority classification         ← §14.1
├── Decision: Reservoirs and authority                              ← §14.2
├── Decision: Legacy SQL MC corpus disposition                      ← §14.3
├── Decision: Reservoir intake hygiene                              ← §14.4
├── Decision: Formula authority discipline                          ← §14.5
├── Decision: Layered activation gates (MLS-14 + PE-MC-10)          ← §14.6
├── Decision: L-node integration boundary                           ← §14.7
├── Decision: MCF panel operates as a governed workbench            ← §14.9 (with allowed + forbidden tool surface tables as own subsections)
├── Foundational guardrails (seven, as a named section)             ← §14.8
├── Substrate commitment (mcf.* schema)
├── Reversal path / supersession
└── Consequences (downstream gates this enables)
```

Each Decision sub-heading is a standalone amendable unit. Future revisions to (say) §14.6 layering or §14.9 tool surface can be filed as an Errata against the named decision without re-opening the whole ADR.

**Mandatory snippet count: 9** (was 8 before this M0 correction). Optional snippet count: 2 (D365, MCF-before-BCF-enrichment — both recommended NOT in M1 ADR).

---

## 15. Recommended next step

### 15.1 If operator accepts D1-D9 (in this packet's review)

**Open M1 — Foundational MCF ADR.** M1 authors the ADR by inserting the §14 wording snippets into the structural template (§14.11). M1 is then a near-mechanical exercise: the decisions are made, the wording is drafted, M1 records and decides them via `devhub_decision_record`.

### 15.2 If operator revises some decisions

Re-issue this packet with revisions; do not open M1 until the revised packet is accepted.

### 15.3 If operator defers some decisions

Each deferred decision blocks specific downstream gates per §13:

- D1 deferred → M2 blocked
- D2 deferred → M1 blocked (authority model unresolved)
- D3 deferred → M11 blocked
- D4 deferred → M7 blocked
- D5 deferred → M13 PE-MC evaluator unresolved
- D6 deferred → M20 fiscal-period metric deferred only
- D7 deferred → no MCF gate blocked (L-node parallel track explicit)
- D8 deferred → build plan sequencing ambiguous; no specific gate blocked
- D9 deferred → Step 4 BCF enrichment cannot scope

Recommend operator accept D1, D2, D3, D4, D5, D7, D8, D9 as packaged (those are tight and well-evidenced); D6 may be coordinated separately with the D365 owner.

### 15.4 What NOT to open before M1

- **M2 substrate DBCP** — needs D1 + L1-L6 lock from M1
- **M7 AST service** — needs D4 lock from M1
- **M11 reservoir-ingestion** — needs D3 lock from M1
- **Step 4 BCF enrichment** — needs D9 (and benefits from M1 ADR scope clarity)

### 15.5 Suggested M1 session shape

- Operator opens M1 session with this packet as input.
- M1 authors the ADR file at `bc-docs-v3/docs/adrs/ADR-{uid}.md` via `devhub_decision_record`.
- Substantive content of M1 is the §14 snippets organized per §14.11 template, plus the Context section grounding the framework in post-D418 reality.
- Operator review and `status: decided` lock the ADR.
- Cross-references updated: MCF requirements §1.4 source-of-authority table adds the new ADR; build plan §2 locked positions are footnoted to the new ADR; this packet becomes the historical record of the decision pre-work.

---

## Document verification

- **All 15 sections present** (§1 Scope/method, §2 Asset disposition, §3-§11 Decisions D1-D9, §12 Disposition-to-M1 mapping, §13 Decision table, §14 Proposed M1 ADR insertion list, §15 Recommended next step).
- **Every decision (D1-D9) has** a Recommended decision, Rationale citing source documents, and Proposed M1 ADR wording (`[MANDATORY]` or `[OPTIONAL]` marked).
- **Asset disposition table includes** all minimum assets listed in the brief plus 4 additional that resolved into multiple distinct items (e.g. fiscal calendar stack expanded to 5 substrate items + service).
- **No recommendation is written as already-authoritative.** Operator-owned positions are flagged with **OPERATOR DECISION** or marked as recommendations in §13.
- **No code/DB/schema files changed.** Single doc commit to bc-docs-v3 main.

### Disposition counts (from §2.2)

| Disposition | Count |
|---|---:|
| keep | 7 |
| adapt | 6 |
| stale-deprecate | 4 |
| historical-only | 4 |
| gap | 7 |
| **Total** | **28** |
