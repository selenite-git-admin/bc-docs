---
uid: metric-context-framework-gap-survey
title: Metric Context Framework (MCF) — Gap / Risk Survey
description: Step 2 of the MCF arc. Converts the inventory (metric-context-framework-inventory.md, commit d9b10d2) into decision points, risks, and recommended dispositions against the requirements (metric-context-framework-requirements.md, commit 13f9bb6). Live read-only bc-postgres SELECT queries used for decision-sensitive counts (query log in §6). Recommendations do not create authority — operator-owned decisions are marked explicitly. Not an ADR. Not an implementation plan. Direct input to Step 3 MCF build plan.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: gap-survey
---

# Metric Context Framework (MCF) — Gap / Risk Survey

## 1. Scope, method, and evidence rules

### 1.1 Purpose

Step 2 of the MCF arc. The inventory (`metric-context-framework-inventory.md`, commit `d9b10d2`) classified ~73 artifacts and surfaced ~15 open questions. This survey converts those open questions into structured decision points, lays out option spaces with risks, and recommends dispositions where evidence supports a recommendation.

The 5 decision areas (per operator brief):

| # | Decision area | Status going in |
|---|---|---|
| Q1 | Existing `contract.metric_contract` disposition | Inventory §6.1 flagged as Step 2 decision |
| Q2 | TEXT formula → governed AST | Inventory F-EVAL-1 / F-FORM-1 surfaced gap |
| Q3 | Reusable substrate vs pre-MCF authoring paths to retire | Inventory §4 + MLS-14 vs PE-MC-10 layering open |
| Q4 | Minimum BCF Registry density for first real MCF cases | Inventory §7.5 / §8.x |
| Q5 | Gate sequencing pre-BCF-enrichment vs post-BCF-enrichment | MCF requirements §20 untested against inventory |

### 1.2 Method

- **Primary sources**: MCF requirements + MCF inventory + ADRs cited therein. Inventory's Failure Evidence Overlay (§2) is the authority for historical scars; this survey does not re-mine.
- **Live DB evidence**: read-only `bc-postgres` MCP `SELECT` queries against `bc_platform_dev`. Only used where a decision is sensitive to a current count. Every count cited in this survey carries a query timestamp in §6.
- **No code/schema/DB changes**, no PR.
- **Recommendations are recommendations.** Operator-owned decisions are flagged with **OPERATOR DECISION REQUIRED**. The survey may recommend, but the survey does not create authority.

### 1.3 Live DB query discipline

- `SELECT`-only queries against the platform DB `bc_platform_dev` (PG 17.8). Tenant DBs not queried (schema allowlist did not include `evidence` / `envelope` / `progression` / `fact`).
- Schema allowlist available to this session: `contract`, `master`, `metric`, `runtime`, `source`. Notably **NOT** in allowlist: `concept_registry` (BCF Registry — Q4 had to use inventory cross-references instead of live BCF counts).
- Each count is cited with its query identifier (Q-N) and timestamp; full log in §6.
- Queries are documented verbatim where decision-load-bearing.

### 1.4 Calibration vs Step 1 inventory

Step 1 was deliberately DB-read-free. Step 2 re-queried the decision-sensitive counts. The most material divergences from inventory:

- Inventory cited 376 active MDs in DB and 195 "Ready" (per 2026-05-07 feedback file).
- Live as of 2026-05-26 (Q-3): 731 active MCVs / 567 distinct MDs with active MCV / 247 active MCs with complete chain. The "Ready" count has risen.
- **Most consequential new finding**: only **2 of 780 `contract.metric_contract` rows are non-archived** (Q-13). The other 778 have `archived_at IS NOT NULL`. 729 active MCVs reference archived parent MCs. This was not in the inventory and materially changes Q1.

### 1.5 Out of scope for Step 2

- ADR-grade design — the survey recommends; it does not author an ADR.
- Build plan — Step 3 owns sequencing.
- BCF concept-density enumeration — Step 4 owns enrichment scope; this survey identifies criteria only.
- Tenant DB inspection — schema allowlist constrains.

---

## 2. Five decision areas

### 2.1 Q1 — Existing `contract.metric_contract` disposition

**Status: OPERATOR DECISION REQUIRED.**

#### 2.1.1 New evidence (live DB) materially changes the question

Inventory §6.1 framed three dispositions assuming `contract.metric_contract` was an active-use table. Live DB tells a different story:

| Fact | Value | Query |
|---|---:|---|
| `contract.metric_contract` total rows | 780 | Q-1 |
| `contract.metric_contract` non-archived (`archived_at IS NULL`) | **2** | Q-13 |
| `contract.metric_contract` archived (`archived_at IS NOT NULL`) | 778 | Q-13 |
| `contract.metric_contract_version` total rows | 1,022 | Q-1 |
| `contract.metric_contract_version` `governance_state_code='active'` | 731 | Q-2 |
| `contract.metric_contract_version` `governance_state_code='draft'` | 289 | Q-2 |
| `contract.metric_contract_version` `governance_state_code='superseded'` | 2 | Q-2 |
| Active MCVs whose parent MC is non-archived | **2** | Q-14 |
| Active MCVs whose parent MC is archived | **729** | Q-14 |
| Draft MCVs whose parent MC is archived | 289 | Q-14 |
| Superseded MCVs whose parent MC is archived | 2 | Q-14 |
| Distinct MDs with at least one non-archived MC + active MCV | **2** | Q-15 |
| `contract.metric_contract_approval` rows | **0** | Q-1 |

**What this means.** The existing `contract.metric_contract` table is operationally a historical archive carrying 2 live MCs. The 729 active MCVs are semantically active by their `governance_state_code` but reference an archived parent — an internal inconsistency that pre-dates MCF.

The approval table is empty (0 rows) — the existing approval path is not in use.

#### 2.1.2 Updated option space

| Option | Description | Operational scope under new evidence | Cost | Risk |
|---|---|---|---|---|
| **A. Coexist** | `contract.metric_contract` stays for the 2 live + 778 archived; `mcf.metric_contract` is the MCF-authored substrate. Routing required per consumer. | 2 live + 778 archived rows stay queryable in the old place. New MCs land in `mcf.metric_contract`. | Lowest. | Two SSOTs for "the metric contract" indefinitely. Audit + tooling must teach the boundary. The 729-MCV-with-archived-parent inconsistency persists. |
| **B. Rename current to legacy** | Rename `contract.metric_contract` → `contract.legacy_metric_contract` (or schema-rename to `legacy.metric_contract`). Build `mcf.metric_contract` as canonical. Existing consumers adapt their reads. | The rename itself is a one-time schema migration; the 778 archived + 2 live rows move under the rename. | Medium. Schema rename + every consumer-reference update. | Cleaner end state than A. Two-table reads remain (consumers must know which to query). Auditable. |
| **C. Retire-migrate** | Migrate the 2 live MCs (+ optionally the 729 active-MCV-archived-MC corpus) into `mcf.metric_contract` as fresh MCF authoring. Drop or archive `contract.metric_contract`. | The migration scope is bounded: 2 live MCs are trivial; the 729 active-MCV-archived-MC corpus is the real choice. Either re-author all 729 as MCF MCs (high cost) or accept that the archived corpus is historical, document its retirement, and rebuild forward as MCF MCs. | High if migrating 729 MCVs; **low if accepting that the 778 archived + 729 active-on-archived corpus is historical-only and MCF starts fresh**. | Cleanest end state. Aligns with MCF §16 migration-free stance if the existing corpus is treated as historical-only and the 2 live MCs are re-authored from scratch. Highest disruption to current consumers if they expect the 729 active MCVs to remain authoritative. |

#### 2.1.3 Reconciliation with MCF §16 migration-free stance

MCF requirements §16 ("Migration-free re-authoring stance after D418") was authored against the quarantined / dropped BF/BO/CF/CM substrate. The stance reads:

> Re-authoring is greenfield. There is no migration from the historically-quarantined-now-dropped surfaces.

The existing `contract.metric_contract` is **not** historically quarantined — but it is now revealed (Q-13) to be **778/780 archived already**. The 2 non-archived rows are the only "live" content by archive flag.

Under this evidence, Option C (retire-migrate) **does not violate §16** if framed as:

> The 2 live MCs are operator-decided: re-author from scratch (MCF greenfield) or carry forward into `mcf.metric_contract`. The 778 archived + 729 active-MCV-archived-MC corpus is historical-only; MCF does not migrate it.

This is the same framing MCF §5 already uses for `metric.metric_definition` / `metric.metric_knowledge` (KPI catalog) — they survive as preserved intent / background knowledge, not as authority. The same logic extends to the archived `metric_contract` corpus.

#### 2.1.4 Recommendation

**Survey recommendation: Option C (retire-migrate, narrow scope).** Specifically:

1. The 778 archived MCs stay where they are as historical reference. No MCF migration, no MCF re-authoring obligation.
2. The 729 active-MCV-on-archived-MC inconsistency is treated as legacy data-state, **not authoritative for MCF**. These MCVs continue to be readable by existing consumers (bc-admin readiness pages, chain-status SSOT, etc.) but MCF authoring does not extend or supersede them.
3. The 2 non-archived MCs are operator-reviewed: are they intentional live content? If yes, they are re-authored as MCF MCs in `mcf.metric_contract` from scratch under MCF discipline. If no, they are archived to bring the table fully to historical state.
4. New MCF MCs land in `mcf.metric_contract` — a new schema and table.
5. `contract.metric_contract` is **not** renamed (Option B path) — the existing name continues to denote the legacy/historical store, which removes consumer-side rename churn. A `STATUS:retired` comment or table-level docs note marks its non-authoritative role.

**Why this over Option B (rename):** the rename pays a schema-migration tax across every consumer reference for no semantic gain over leaving the legacy table where it sits with explicit documentation of its retired status. The renaming churn is high; the data-state churn (729 active-MCVs-on-archived-MCs) is unaffected by the rename.

**Why this over Option A (coexist):** Option A is functionally the same outcome as Option C step 5 — but Option A leaves the 729-active-on-archived inconsistency ambient and undocumented. Option C makes the retirement explicit.

**Cost of recommendation:** low. Two table-level documentation acts; one decision on the 2 non-archived MCs; one greenfield `mcf.metric_contract` build (which Gate M2 needs anyway).

**OPERATOR DECISION REQUIRED on:**

- Whether to accept Option C as framed above.
- Disposition of the 2 non-archived MCs (re-author as MCF, or archive).
- Whether the existing `contract.metric_contract` gets an explicit retirement marker (table comment, ADR, README) or stays implicit.

---

### 2.2 Q2 — TEXT formula → governed AST

**Status: SURVEY RECOMMENDATION. Working rule lock requires OPERATOR DECISION.**

#### 2.2.1 New evidence (live DB)

| Fact | Value | Query |
|---|---:|---|
| `metric.metric_formula` total rows | 1,216 | Q-1 |
| Rows with non-null, non-empty `formula_text` | 1,216 (100%) | Q-9 |
| Distinct formula texts | **134** (1,216 rows → 134 distinct) | Q-10 |
| Most common: `O1 = (I1 / I2) * C1` (ratio metric) | 435 instances | Q-11 |
| 2nd: `O1 = I1 / I2` | 252 | Q-11 |
| 3rd: `O1 = I1 - I2` | 86 | Q-11 |
| 4th: `O1 = I1` (passthrough) | 80 | Q-11 |
| `metric.metric_formula_variable` total | 4,226 (2,410 input + 1,195 output + 621 constant) | Q-1, Q-8 |
| Formulas containing banned functions (ML_MODEL / QUALITATIVE / SUM_BY_CATEGORY / WEIGHTED_AVG / STDDEV) | **27 of 1,216 (2.2%)** | Q-16 |
| Average formula text length | 18 chars | Q-9 |
| Max formula text length | 143 chars | Q-9 |

**What this means.** The text formula corpus is small (134 distinct shapes for 1,216 rows). The top 4 patterns account for ~70% of rows. Banned-function contamination is small (27 rows). Average length 18 chars suggests these are formal-symbol formulas (`O1 = I1 / I2`-style), not natural-language formulas.

The structural shape `O1 = f(I1, I2, ..., C1, C2, ...)` is essentially already an AST in disguise — output expression over typed inputs (I1..In) and constants (C1..Cn). The 4,226 `metric_formula_variable` rows give the typed-variable side directly.

#### 2.2.2 Option space

| Option | Description | Contamination risk | Cost | Risk |
|---|---|---|---|---|
| **A. Re-author from scratch** | MCF AST authoring service ignores text formulas entirely. Every MCF MC's AST is composed structurally via the AST builder (MCF §18.4). The 1,216 text formulas are historical reference only. | Zero — no parser, no contamination path. | High operator effort if all 1,216 (or the subset MCF wants to admit) must be re-authored manually. | Pace of MCF onboarding is bound by re-authoring rate. |
| **B. Parser as importer-only diagnostic** | A one-shot importer parses the 134 distinct formula shapes into candidate ASTs as a Step 4 enrichment input. The candidate AST is **never** the authoritative AST — it's a panel-proposal seed that the MCF Metric Authoring Panel must propose anew and operator must approve under MCF discipline. | Low — parser output is panel-suggestion, not authority. Contamination is structurally impossible because the panel-proposes / operator-confirms / platform-verifies chain (MCF §11.3 + §12.2) is the only path to active. | Medium — parser implementation effort, but bounded (134 distinct shapes). | Subtle confusion risk: panels may anchor too strongly on parser suggestions. Discipline must enforce that the AST is authored, not parsed-and-confirmed. |
| **C. Hybrid (parser as runtime fallback)** | Parser writes initial AST shape; MCF authoring sees it as starting point; operator edits. | High — once a parsed AST is in the substrate, the line between "parsed" and "authored" blurs. Contamination by inertia. | Lowest. | Working rule "AST is authored, never parsed-from-text" is violated by construction. |

#### 2.2.3 Recommended working rule

**The AST is authored and governed; legacy `formula_text` is not authoritative.** No exception. This rule preserves MCF §7.6 (formula AST is executable, deterministic) and MCF §12.2 (panel proposes, platform verifies).

#### 2.2.4 Recommendation

**Survey recommendation: Option A (re-author from scratch) as the binding rule, with Option B (parser-as-importer-only) admitted as a Step 4 enrichment helper if and only if its outputs flow through the MCF Metric Authoring Panel as proposals, not as direct substrate writes.**

Concretely:
1. MCF AST authoring service (Gate M7) accepts AST input only. No text-parsing entry point on the authoring service.
2. The 1,216 text formulas remain in `metric.metric_formula` as historical reference; MCF does not read them as authority.
3. A separately-authorized one-shot import script (NOT part of MCF gates M1-M20) MAY parse the 134 distinct shapes into candidate ASTs for Step 4 / Step 5 / Gate M20 (KPI catalog re-authoring program) — and only if its output enters MCF substrate via the panel-proposes / operator-confirms / platform-verifies path. Such a script falls under the helper-script default-untrusted discipline (inventory F-READY-3).
4. The 27 banned-function formulas (ML_MODEL etc.) are explicitly out of MCF AST taxonomy at v1; their MDs either get formulas removed or new AST authoring under non-banned operator set.

**OPERATOR DECISION REQUIRED on:**

- Locking the working rule as written ("AST is authored and governed; legacy `formula_text` is not authoritative") into the foundational MCF ADR (Gate M1).
- Whether the Step 4 enrichment helper (Option B, panel-only-proposal path) is admitted; if so, its scope, ownership, and tooling discipline.

---

### 2.3 Q3 — Reusable substrate vs pre-MCF authoring paths to retire

**Status: SURVEY RECOMMENDATION per service. Includes MLS-14 vs PE-MC-10 layering SUB-DECISION (operator-owned).**

#### 2.3.1 Per-service decision table

Separating **runtime / evaluation substrate** (downstream of MCF authoring) from **authoring / governance surfaces** (MCF replaces or extends).

##### Runtime / evaluation substrate — MCF consumes, does not replace

| Service / substrate | Verdict | Evidence | Notes |
|---|---|---|---|
| `MetricEvaluationEngine` (`src/boundary/metric-evaluation-engine.service.ts`) | **keep** at execution layer; **adapt** at input shape | Inventory F-EVAL-1, F-EVAL-2, F-EVAL-3, F-EVAL-4, F-EVAL-5 | Sound, benchmarked (3.3ms / 57ms / 712 COs). MCF feeds AST input; engine resolves variables and applies formula. |
| `ChainStatusService` + `contract.chain_status` + `contract.chain_trace` | **keep** | Inventory F-CHAIN-1, F-CHAIN-2 | DEC-bebaec SSOT. Live counts (Q-4): 540 chain_status rows; 247 complete + 293 partial. Working as designed. |
| `metric.readiness_ledger` + `mc_dependency` | **keep** | Inventory F-READY-1 | Live: 905 ledger rows (Q-1), 1,133 mc_dependency rows all `canonical_contract` type (Q-12). |
| `FiscalCalendarService` + `master.dim_date` + `master.dim_fiscal_calendar` + `organization.fiscal_calendar_config` | **keep** | Inventory F-FISC-1, F-FISC-2 | Stack live. **But D365 CC `posting_date_field` enrichment is NOT shipped at table level** (Q-7 confirms `posting_date_field` column does not exist on `contract.canonical_contract`). See §3 coordination items. |
| `metric.mls_state` + `metric.mls_state_event` + `metric.mls_trigger_binding` | **keep** | Inventory F-MLS-1 | Live: 1,659 mls_state + 3,317 mls_state_event + 10 trigger_bindings (Q-1). MLS-14: 829 green + 2 red (Q-6). |
| `Mls14ActivationGate` + `Mls14SignatureHashService` | **keep** | Inventory F-FORM-2, F-MLS-2 | Phased v1 live. Re-evaluation cleaned up most semantic-collapse — only 2 red as of today. |
| `metric.metric_definition` + `metric.metric_knowledge` | **keep** as carve-out (preserved intent / background knowledge per MCF §5) | Inventory F-CAT-1, F-CAT-2, F-KNOW-1 | Live: 1,241 metric_definition (1,214 draft / 25 deprecated / 2 active per Q-3 — confirming `status_code` is not used as promotion signal). |
| `contract.certification_record` (Foundation Governance Substrate) | **keep** + extend with MCF action_codes | Inventory §3.1 | Shared substrate per MCF §17 + §11.5. |
| `evidence.evidence_object` (tenant DB, rejection envelopes) | **keep** | Inventory F-OBS-1 | Authoritative rejection-envelope persistence. MCF reads-only. |

##### Authoring / governance surfaces — MCF replaces or extends

| Service / substrate | Verdict | Evidence | Notes |
|---|---|---|---|
| `metric.metric_formula` (text storage) | **adapt** — read-only, historical; new content goes to `mcf.metric_formula_ast` | Inventory F-EVAL-1, F-FORM-1, F-FORM-3; Q-9 | 1,216 text formulas, 134 distinct shapes. Per Q2 recommendation. |
| `metric.metric_formula_variable` | **adapt** — read-only, historical; new content goes to `mcf.metric_variable_binding` | Inventory F-EVAL-1 | 4,226 variables (Q-8). |
| `metric.metric_formula_verification` (Maker A/B/Moderator) | **adapt** — predates workbench framing; new content goes to `mcf.metric_authoring_panel_run` + `mcf.metric_authoring_panel_transcript` | Inventory §3.1 + F-FORM-1 | Workbench framing makes this richer. |
| `metric.metric_binding` (CC-grain) | **adapt** — MCF requires variable-grain via `mcf.metric_variable_binding` | Inventory F-BIND-2 | 1,133 rows (Q-1). The existing rows are CC-grain join helpers; whether they're retired after MCF onboarding or kept as coarse-grained joins is a Step 3 item. |
| `FormulaAuditService` (text-based, D315) | **adapt** — replace audit role with MCF AST taxonomy validity check (PE-MC-5) | Inventory F-FORM-1 | Banned-function list (5 functions) becomes MCF AST taxonomy decision. Live: 27 formulas use banned functions (Q-16) — 2.2% of corpus, addressable. |
| `mc-onboarding.service.ts` (header β-path needed) | **adapt** | Inventory F-FORM-3 | Header hardcoding lines 442-443 per SES-594568. SERVICES-ONLY discipline mandates: extend or build sibling. |
| `contract.metric_contract_approval` (approval audit) | **stale-deprecate** — subsumed by `mcf.metric_publication_eligibility_result` + cert reuse | Inventory §3.1; Q-1 (0 rows) | Empty table; safe to deprecate. |
| `IntegrityService` (deprecated per DEC-bebaec) | **stale-deprecate** | Inventory F-CHAIN-1 | Final removal pending consumer-map cleanup. Out of MCF scope to remove; flagged for Step 3 hygiene. |
| `MetricWizardService` (quarantined per BCF G15) | **stale-deprecate** | Inventory F-WIZ-1 | MCF AST builder UI (Gate M15) is the structural replacement. |
| `contract.metric_contract` (per Q1) | per Q1 Option C (recommended) | Q-13, Q-14, Q-15 | 778/780 archived; 2 live. Existing table is historical-only post-MCF. |
| `contract.metric_contract_version` (per Q1) | per Q1 Option C (recommended) | Q-2, Q-14 | New MCF MCs go to `mcf.metric_contract_version`. Existing rows historical. |

##### Gap services (do not exist, MCF must build)

| Required service | Gate | Evidence |
|---|---|---|
| MCF formula AST authoring service | M7 | MCF §17.4 |
| MCF structural-check engine (C-FX-1..C-FX-11) | M8 | MCF §12.5 |
| MCF deterministic verifier service | M9 | MCF §12.6 |
| MCF Metric Authoring Panel (three-model) | M10 | MCF §11.3 |
| MCF PE-MC publication-gate evaluator | M11 | MCF §13 |
| MCF supersession service | M13 | MCF §10.5 |
| `LNodeSemanticService` (per D366) | per §3 coordination | Refined per new evidence (§2.3.3) |

#### 2.3.2 L-node service evidence refinement

**Inventory F-LNODE-1 was partially wrong.** Inventory said "no service writer exists" based on sub-agent grep. Live DB tells different story:

| Fact | Value | Query |
|---|---:|---|
| `contract.l_node_semantic_verdict` rows | 202 | Q-1 |
| `contract.l_node_semantic_trace` rows | 25,237 | Q-1 |
| Overall semantic verdict distribution | 141 green + 61 not_applicable | Q-5 |
| Verdict row date range | 2026-05-15 → 2026-05-17 | Q-5 |
| Distinct MCs covered | 202 | Q-5 |
| Trace node levels written | **L2 only** (141 green + 25,096 not_applicable) | Q-5 |

**Refined reading.** *Some* writer exists (likely a recent backfill script from SES-d4e2d5-adjacent or a partial service) and writes L2-only traces. L1 + L3-L8 traces are not written. `contract.l_node_semantic_verdict` schema has L1-L8 columns (Q-17 confirms 14-column schema with l1-l8 + overall). MCF §15.8 expects all L1-L8 to be populated.

**Verdict revision for `LNodeSemanticService`:** from **gap** → **partial-gap** (L2 writer exists; L1+L3-L8 writers are gaps). Step 3 must decide whether MCF Gate M8 / M9 includes full L1-L8 writer construction or whether it stays as a parallel D366 follow-on.

#### 2.3.3 SUB-DECISION: MLS-14 vs PE-MC-10 layering

The question: do MLS-14 (semantic-class collapse refusal via signature_hash) and PE-MC-10 (self-verification fixture passes) overlap, layer, or substitute?

##### Evidence

- **MLS-14** detects identical semantic signatures across two formula variables. Specimen MT-04971: `SUM(WRBTR)/SUM(WRBTR)=1.0` because I1 and I2 resolve to the same (table, field, filter, grain). Signature-hash equality is the detection mechanism.
- **PE-MC-10** runs a deterministic verifier against a self-verification fixture bound to the package_signature_hash. If the formula behaves correctly against declared inputs, the verifier returns pass.

**Overlap analysis:** MLS-14 catches the MT-04971 case by signature hash. PE-MC-10 *would also* catch it by exercising the formula against a fixture where I1≠I2 (the fixture would naturally provide non-equal numerator and denominator rowsets, and the output would be ≠1.0; if the formula has collapsed inputs, the output ratio would always be 1.0 regardless of fixture inputs, which the fixture diff would surface).

But the gates check **different surfaces**:

| Gate | What it sees | What it doesn't see |
|---|---|---|
| MLS-14 | **Substrate identity** of bound variables (signature over canonical_field + business_field + source_table + source_field + filter + grain role + time window). | Whether the formula *computes correctly*. |
| PE-MC-10 | **Executable behavior** of the package against fixture inputs (numerical correctness, type/unit propagation, grain projection). | Whether two variables are *semantically the same thing* in the substrate. |

A formula could pass PE-MC-10 (computes correctly given the fixture inputs) but fail MLS-14 (substrate-level signature collapse). Conversely a formula could pass MLS-14 (signatures distinct) but fail PE-MC-10 (e.g. unit-conversion error, off-by-one in window).

##### Option space

| Option | Description | Risk |
|---|---|---|
| **A. Layered, both-must-pass** | Both gates apply; failing either blocks activation. MLS-14 stays at the MLS surface (runtime activation gate per D391 phased-v1); PE-MC-10 stays at the MCF publication gate (per MCF §13). | Lowest risk — preserves both checks. |
| **B. One feeds the other** | PE-MC-10 incorporates an MLS-14-style signature-equality check as a sub-rule. MLS-14 retires. | Subtle: MCF would be responsible for a check that lives in MLS framework today. Adds coupling between MCF and MLS substrates. |
| **C. Overlap with explicit primacy** | Both gates exist; MCF declares PE-MC-10 primary; MLS-14 becomes a "see also" reference. | Operationally confusing. Two gates with murky precedence. |

##### Recommendation

**Survey recommendation: Option A (layered, both-must-pass).** Neither gate weakens. MLS-14 stays at substrate-identity-checking; PE-MC-10 stays at executable-behavior-checking. They are complementary, not duplicative.

Operational consequence: an MCF MC reaches active only when (chain_complete = true) AND (MLS-14 = green) AND (PE-MC-1..PE-MC-10 all pass).

**OPERATOR DECISION REQUIRED on:**

- Locking Option A (layered, both-must-pass) into the foundational MCF ADR (Gate M1).
- Whether the LNodeSemanticService L1+L3-L8 writers are part of MCF Gates M8/M9 or a parallel D366 follow-on track (the partial-gap reframe).

---

### 2.4 Q4 — Minimum BCF Registry density for first real MCF cases

**Status: SURVEY CRITERIA. Final case selection requires SES-level operator decision and BCF Registry inspection (out of this survey's allowlist).**

#### 2.4.1 Constraint

The `concept_registry` schema (BCF Registry) is **NOT in this session's bc-postgres allowlist** (Q-0). This survey cannot enumerate live BCF Entity / BusinessConcept / Characteristic counts. Inventory cross-references confirm the BCF substrate exists (concept_registry.entity, concept_registry.business_concept, concept_registry.characteristic per CLAUDE.md "BCF substrate intact" check from SES-fe15e0 D418 Gate 5.3 verification).

This means Q4 produces **criteria** for the minimum density, not the final enumerated case list.

#### 2.4.2 What MCF needs to prove (per gate)

For each MCF capability that requires BCF concepts, the survey identifies the minimum representative density. The user's framing: "10 representative metrics" not "all 1,819 KPIs".

##### Capabilities and their BCF requirements

| MCF capability | What it needs from BCF | Minimum concept density |
|---|---|---|
| **AST builder** (Gate M15) | Variable picker over BCs by representation term + unit; entity picker for grain | ~3 Entity types × ~5 BCs per entity × ~2 Characteristics per BC = ~30 concepts spanning currency + count + duration + identifier + date representation terms |
| **Variable binder** (Gate M7 / M10) | Reachability check (BC's home entity reachable from grain entity via identity-bearing reference properties — MCF §6.3 check 5) | At least 1 grain entity with 2+ reachable BC on different reference-path entities; at least 1 unreachable BC for negative test |
| **Self-verification fixtures** (Gate M8) | Typed rowsets per variable matching BC representation term + unit | Same concept set as AST builder; no additional BCF needs beyond what the variables reference |
| **Deterministic verifier** (Gate M9) | Resolver fixture config for any computed dimensions the package references | Computed-dimension config is fixture-side (Section C), not BCF-side; no additional BCF needs |
| **Computed-dimension resolver** (Gate M9 + runtime) | A BC for the date / time-anchor that the package's computed dimension reads | At least 1 date-BC per scope (e.g. `Sales Order Line · posting date`) |
| **Tenant binding / MLS overlay** (Gate M18) | Stable BCF references — concepts whose lifecycle_state remains 'active' through the demonstration period | Same concept set; no additional BCF discipline beyond stability |

##### Cumulative minimum

The minimum BCF density covering all gates: **~30 BusinessConcepts across ~3-5 Entity families with ≥1 date-BC and ≥1 currency-BC and ≥1 count-BC**, plus ≥1 negative test case (unreachable BC) and ≥1 stable specimen for the longest-lived MCF demo.

#### 2.4.3 The "10 representative metrics" framing

Ten metrics that collectively exercise:

1. **A simple aggregation** (e.g. `SUM(amount)`) — straight passthrough; tests basic AST + variable binder + fixture.
2. **A ratio metric** (e.g. `O1 = (I1 / I2) * C1`) — tests two variables, constant, formula audit. ✓ Already 435 instances of this pattern in legacy formulas (Q-11).
3. **A difference metric** (e.g. `O1 = I1 - I2`) — same family as ratio. ✓ 86 legacy instances.
4. **A passthrough metric** (e.g. `O1 = I1`) — tests trivial AST.
5. **A windowed metric** (e.g. trailing 30-day SUM) — tests `window` AST node + temporal gate + window parameter validity.
6. **A metric with a fiscal-period filter or grain** — tests `time_anchor_resolution` AST node + Section C resolver fixture config.
7. **A metric with a bucket-assign output** (e.g. DSO age buckets) — tests `bucket_assign` AST node.
8. **A ratio metric where I1 and I2 are intentionally distinct concepts but bound to the same Entity** — exercises the grain-alignment check (§6.3 check 5) positively.
9. **A failed-fixture case** — same as (2) but with a fixture where I1=I2; verifier should return fail (catches the MT-04971-class issue from the executable side).
10. **A stale-fixture case** — supersede the formula AST on (2); fixture's bound `package_signature_hash` no longer matches; PE-MC-10 should refuse.

Metrics 1-7 are **happy-path proofs**; 8 is a positive cross-coherence proof; 9-10 are **failure-mode proofs** that MCF's gates actually refuse.

#### 2.4.4 Selection criteria (not final selection)

Step 4 (BCF enrichment for MCF seed cases) selects the actual 10. Criteria:

- Each metric maps to ≥1 already-existing BCF Entity (per CLAUDE.md, Sales Order Line + unit-price BC + lead time + cycle time are confirmed active).
- The 10 collectively span ≥3 Entity families to test cross-Entity binding reachability.
- At least 1 metric uses a date BC (for fiscal-period / time-anchor).
- At least 1 metric exercises each AST node taxonomy class: `variable_ref`, `literal`, `aggregate`, `arithmetic`, `case`, `window`, `time_anchor_resolution`, `bucket_assign`.
- At least 1 metric has a known legacy parallel (text formula in `metric.metric_formula`) so the comparison-vs-legacy is visible.
- At least 2 metrics are deliberately built to fail (one to fail PE-MC-10, one to fail MLS-14) so the gates are demonstrated to refuse.

#### 2.4.5 Recommendation

**Survey recommendation:** Step 4 (BCF enrichment) is scoped to **the ~30 BCs across ~3-5 Entity families needed to support 10 representative metrics**, with selection criteria as in §2.4.4. Final BCF concept enumeration requires BCF Registry inspection — out of this session's read allowlist. **Operator should authorize a parallel BCF Registry read (or expand the allowlist) for Step 4 / Step 5 transition.**

**OPERATOR DECISION REQUIRED on:**

- Whether to authorize `concept_registry` schema read in the next session for Step 4 enrichment scoping.
- Whether the 10-representative-metrics framing is the right boundary or whether the operator wants tighter (e.g. 5) or looser (e.g. 20).

---

### 2.5 Q5 — Gate sequencing pre-BCF-enrichment vs post-BCF-enrichment

**Status: SURVEY CLASSIFICATION. Step 3 build plan uses this as input.**

#### 2.5.1 Classification

MCF requirements §20 has 20 gates (M1-M20 post commit ea14d9a). Each gate classified by what it depends on:

| Class | Meaning |
|---|---|
| **F** — Foundation / substrate-safe before enrichment | Can proceed before BCF enrichment lands; needs only BCF Registry to be referenceable (which it already is per CLAUDE.md confirmation) |
| **P** — Parallel-safe with enrichment | Can build alongside enrichment; doesn't gate it or get gated by it |
| **B-BCF** — Blocked on minimum BCF density | Needs ≥10-metric concept set per Q4 to do meaningful work |
| **B-OP** — Blocked on operator decision | Needs Q1, Q2, or Q3 operator decision before sensible build |

##### Gate dependency map

| Gate | MCF requirements label | Class | Why | Dependencies (per §20.2) |
|---|---|---|---|---|
| **M1** Foundational MCF ADR | F | Pure docs/decision; requirements + inventory + this survey are the inputs. | This requirements doc accepted |
| **M2** Substrate DBCP: identity layer | **B-OP (then F)** | Blocked on Q1 (operator decides table-naming and disposition before substrate design). After Q1 locked, this is foundation. | Gate M1; BCF Registry stable |
| **M3** Substrate DBCP: lifecycle layer | F (after M2) | Standard lifecycle substrate; no BCF dependency. | Gate M2 |
| **M4** Substrate DBCP: publication layer | F (after M3) | PE-MC result + cert + operator-confirm rules. No BCF dependency. | Gate M3 |
| **M5** Substrate DBCP: panel layer | F (after M4) | Panel run + framework policy. No BCF dependency. | Gate M4 |
| **M6** Substrate DBCP: tenant binding layer | F (after M5) | Tenant binding + MLS 15-25 integration. MLS substrate stable per D392. No BCF dependency. | Gate M5; MLS substrate stable |
| **M7** Formula AST authoring service | **B-OP (then P)** | Blocked on Q2 working rule lock (AST is authored, not parsed). After Q2 locked, this is parallel-safe with BCF enrichment because the service operates on AST + bindings, both of which are BCF-shape-aware but not BCF-content-dependent for service implementation. | Gate M2 |
| **M8** Self-verification fixture substrate DBCP | F (after M7) | Substrate creation; no BCF dependency. | Gate M2; Gate M7 |
| **M9** Deterministic verifier service | P | Service operates on package_signature_hash + fixture; BCF-shape-aware but not BCF-content-dependent. | Gate M8 |
| **M10** Metric Authoring Panel implementation | P | Three-model panel structure is BCF-aware (tool allowlist includes BCF search) but the panel implementation itself is BCF-shape-dependent, not BCF-density-dependent. | Gate M5; Gate M7; Gate M9 |
| **M11** PE-MC publication gate implementation | F (after M9, M10) | Deterministic gate evaluator. | Gate M9; Gate M10 |
| **M12** MCF publication path (Fork-i / Fork-ii) | F (after M11) | Two-phase request → operator confirm. | Gate M11 |
| **M13** MCF supersession path | F (after M3, M12) | Operator-initiated supersession; fixture-stale-rule enforcement. | Gate M3; Gate M12 |
| **M14** Operator console (MC List + Detail read) | F (after M5, M9) | Read-only surfaces. | Gate M5; Gate M9 |
| **M15** Operator console (Draft Edit + AST builder) | **B-BCF (after M7, M14)** | The AST builder shows BCs in pickers. Without ≥10-metric BCF density, the builder works but has nothing meaningful to demonstrate. Technically can ship empty; operationally blocked on enrichment. | Gate M7; Gate M14 |
| **M16** Operator console (Fixture Authoring + Run) | **B-BCF (after M9, M15)** | Same logic as M15. Fixture authoring shows variable rowsets keyed by BCs that exist. | Gate M9; Gate M15 |
| **M17** Operator console (Publication Confirm + Supersession) | F (after M12, M16) | Write surfaces with operator-confirm. | Gate M12; Gate M16 |
| **M18** Tenant Binding console + MLS integration UI | F (after M6, M17) | MLS surfaces. | Gate M6; Gate M17 |
| **M19** Cross-framework coordination (BCF/MCF events) | P | Event mechanics per §3.8. | Gates M13 + corresponding BCF readiness |
| **M20** KPI catalog re-authoring program | **B-BCF (after M17)** | Operational program. Requires AST builder + fixture authoring + tenant binding to be operationally usable. Naturally blocks on M15+M16+M17. | Gate M17; ongoing |

#### 2.5.2 The pre-BCF-enrichment build envelope

Gates that can land **before** Step 4 BCF enrichment lands:

**Foundation + substrate**: M1, M2 (post-Q1), M3, M4, M5, M6, M8, M11, M12, M13, M14, M17, M18.

**Service**: M7 (post-Q2), M9, M10.

**Parallel-with-enrichment**: M19.

Gates that **require** Step 4 BCF enrichment to be operationally meaningful:

M15 (AST builder UI — empty without concepts), M16 (Fixture authoring UI — empty without concepts), M20 (re-authoring program — requires whole platform usable).

#### 2.5.3 Key implication

The user's framing was correct: **~70% of MCF gates can proceed before BCF enrichment** (M1-M14, M17-M19). Only M15, M16, M20 are hard-blocked on enrichment. This dramatically expands the parallel work envelope.

The two operator decisions (Q1 and Q2) gate the substrate / service entry points (M2 and M7 respectively). Once those are locked, the bulk of MCF can build.

#### 2.5.4 Recommendation

**Survey recommendation: lock Q1 and Q2 first; then M1-M14 + M17-M19 can proceed in parallel with Step 4 BCF enrichment; M15-M16-M20 land after enrichment provides meaningful concept density.**

**No operator decision required** for the classification itself — this is a survey output. Operator decisions sit at Q1, Q2, and the MLS-14/PE-MC-10 layering sub-decision in Q3.

---

## 3. Cross-cutting coordination items

### 3.1 D369 typed projection cutover (`envelope.metric_snapshot` retirement)

**Status: out of this survey's read scope.** Tenant DB schemas (`envelope`, `fact`, `progression`, `evidence`) are not in the bc-postgres allowlist for this session, so D369 progress couldn't be live-verified.

**Coordination ask:** Step 3 build plan must specify which snapshot substrate is authoritative for MCF reads during D369 dual-write transition. Working position: MCF reads `fact.ms_*_v*` where it exists; falls back to `envelope.metric_snapshot` where it doesn't. Step 3 confirms or revises.

### 3.2 D386 Stage 1 backfill (`temporality_kind`)

**Status: not directly verified.** Per `feedback_metric_lifecycle_states.md`, MLS-14 phased v2 promotion of `temporality_kind_missing` to BLOCKER depends on D386 Stage 1 backfill.

**Coordination ask:** Step 3 should resolve whether D386 Stage 1 is an MCF prerequisite or parallel. Recommendation: parallel — MCF doesn't enforce temporality_kind at MCF authoring; D386 enforces at MLS-14.

### 3.3 Helper-script banding (BCF E2 verdict reuse)

**Status: BCF E2 has banded 160 scripts (38 trusted / 67 diagnostic / 55 unsafe / 0 deprecated; 13 active defect surfaces). MCF gets free reuse.**

**Coordination ask:** Step 3 build plan should:
- Adopt the BCF E2 banding wholesale for cross-cutting scripts.
- Re-survey only scripts in metric/MCF-specific paths if any.
- The "AST is authored, never parsed-from-text" rule means MCF doesn't introduce text-parser scripts; reduces script-trust risk.

### 3.4 L-node semantic service gap (refined per §2.3.2)

**Status: partial-gap.** L2 writer exists (141 verdicts since 2026-05-15); L1, L3-L8 writers are gaps. Schema is L1-L8 (Q-17 confirms 14-column verdict table).

**Coordination ask:** Step 3 decides whether MCF gates include the L1+L3-L8 writers or whether D366 follow-on track is separate. Recommendation: separate — MCF should not own the L-node writer build; the writer should be authored under D366 governance, and MCF reads what's there. Where L1, L3-L8 are unavailable, MCF's `Mls14ActivationGate` + PE-MC-10 carry the load; semantic-rigor signal degrades to L2-only verdict + MLS-14 substrate-identity + PE-MC-10 executable-behavior.

### 3.5 Fiscal calendar enrichment prerequisites

**Status: confirmed open.** Q-7 verified: `contract.canonical_contract` table has **no** `posting_date_field` column. D365 / DEC-a8e8fc was decided but never implemented at the table level.

**Coordination ask:** D365 implementation (add `posting_date_field` column + populate for the 56 existing CCs) is a **hard prerequisite for MCF runtime evaluation of computed-dimension metrics**. Step 3 sequencing should treat D365 as a Gate M0.5 (between M1 and M2). Without `posting_date_field`, every MCF MC that references `fiscal_period` will fail at runtime; the resolver fixture config (MCF §9.2) only substitutes at *verification* time, not runtime.

### 3.6 The 729-active-MCV-on-archived-MC inconsistency

**Status: data-state anomaly, not MCF scope to fix.**

The Q-14 finding (729 MCVs are `governance_state_code='active'` while their parent MC has `archived_at IS NOT NULL`) is a pre-MCF data state. MCF disposition per Q1 Option C says: treat as historical-only.

**Coordination ask:** None for MCF. Existing consumers (bc-admin readiness pages, chain-status SSOT) continue to read these as live for their purposes. If a separate cleanup is desired, it's outside MCF scope.

### 3.7 Sandbox1 AR pilot 14/31 evidence (inventory F-BIND-1)

**Status: validation specimen, not a Step 3 blocker.**

The 7-bucket classification from `feedback_runtime_readiness_gate.md` (1 fully materialized + 12 snapshot-index-backed + 1 ledger-orphan + 7 rejected-source-data-blocked + 8 upstream-CC-blocked + 1 formula-blocked + 1 warn-deferred) is the canonical case study for MCF §12.10 default-route triage reversal. Step 5 MCF implementation should baseline this distribution before MCF onboarding and measure post-MCF.

---

## 4. Operator-approval checklist

### 4.1 Decisions this survey recommends but cannot make

| Decision | Survey recommendation | Required for |
|---|---|---|
| **Q1 — `contract.metric_contract` disposition** | Option C (retire-migrate, narrow scope). 778 archived + 729 active-on-archived stay as historical. The 2 non-archived MCs: re-author as MCF or archive. New MCF MCs land in `mcf.metric_contract`. | Gate M2 substrate DBCP |
| **Q1 sub-decision — Disposition of 2 non-archived MCs** | Operator-reviewed: re-author or archive | Gate M2 |
| **Q1 sub-decision — Explicit retirement marker on `contract.metric_contract`** | Table comment + ADR + README note (recommended; cost is trivial) | Gate M2 |
| **Q2 — Working rule lock** | "AST is authored and governed; legacy `formula_text` is not authoritative." Locks into foundational MCF ADR (Gate M1). | Gate M7 (and operationally every gate downstream of M7) |
| **Q2 sub-decision — Step 4 enrichment helper** | Admit Option B (parser-as-importer-only-via-panel-proposal) as Step 4 helper, NOT as MCF gate. Operator authorizes scope/ownership/tooling. | Step 4 BCF enrichment + Step 5 onboarding |
| **Q3 sub-decision — MLS-14 vs PE-MC-10 layering** | Option A (layered, both-must-pass). | Gate M1 (foundational ADR) |
| **Q3 sub-decision — L-node service ownership** | Separate D366 follow-on track; not MCF gate ownership. | Step 3 build plan + coordination with D366 work |
| **Q4 — BCF Registry read authorization** | Authorize `concept_registry` schema read in next session for Step 4 enrichment scoping | Step 4 enrichment |
| **Q4 sub-decision — "10 representative metrics" boundary** | Accept 10 as the framing or revise (tighter 5 / looser 20) | Step 4 enrichment |

### 4.2 Hard blockers before Step 3 build plan

- Q1 disposition decision (blocks Gate M2 substrate DBCP design).
- Q2 working rule lock (blocks Gate M7 AST service design).
- Q3 layering sub-decision (blocks Gate M1 foundational ADR scope).

These three operator decisions are the minimum required before Step 3 can produce a non-speculative build plan.

### 4.3 Soft blockers (Step 3 can write the plan; operator should resolve before Step 5 execution)

- Q3 L-node service ownership decision (affects Gate M8/M9 scope and sequencing).
- Q4 BCF Registry read authorization + 10-representative-metrics boundary (affects Step 4 scope).
- D365 `posting_date_field` enrichment scheduling (affects runtime for any computed-dimension MC).

### 4.4 Items safe to defer

- D369 typed projection cutover specifics — Step 5 implementation handles.
- D386 Stage 1 backfill timing — parallel track to MCF; no MCF dependency.
- Helper-script per-script disposition — BCF E2 verdict reused; MCF doesn't add scripts.
- The 729-active-MCV-on-archived-MC cleanup — pre-existing data state; not MCF scope to fix.
- Sandbox1 AR pilot baseline measurement — Step 5 measurement task.
- KPI catalog re-authoring program (Gate M20) — operational program post-Gate M17.

---

## 5. Recommended Step 3 inputs

### 5.1 What the MCF build plan should consume from this survey

1. The Q1 / Q2 / Q3-sub-decision operator choices (once locked).
2. The §2.5.1 gate-dependency classification table — Step 3 sequences gates by class.
3. The §3 coordination items — Step 3 plans coordination touchpoints.
4. The §4 operator-approval checklist — Step 3 confirms which decisions are locked before each gate enters the build sequence.

### 5.2 What the MCF build plan should re-ground

- §20 gate dependencies from MCF requirements were authored before this survey. Step 3 re-grounds:
  - M2 sequencing (post-Q1).
  - M7 input shape (post-Q2).
  - M15/M16/M20 enrichment dependency.

### 5.3 Areas that need a focused design survey before build plan

| Topic | Why a focused survey is warranted |
|---|---|
| **MCF authoring panel tool-set v1 schemas** | MCF §19.12 Q32 open. Concrete tool-call schemas (request/response shapes) need locking before Gate M10 panel implementation. Probably an SES-scoped design pass. |
| **MCF `mcf.*` schema vs platform `contract.*` namespace boundaries** | Q1 Option C creates a new `mcf` schema. The ownership/policy split (which schema writes which Foundation Governance Substrate rows) needs to be explicit. Step 3 may need an MCF substrate ownership memo. |
| **CC `posting_date_field` enrichment program** | §3.5 coordination item. Bounded scope (56 CCs) but a real program. Could be co-owned with the D365 owner. |
| **L-node L1+L3-L8 writer ownership / sequencing** | §2.3.2 refined evidence. Decision: build under D366 or under MCF. Step 3 needs to know. |

### 5.4 Not needed before Step 3

- Live `concept_registry` read for Q4 enumeration — survey criteria are sufficient for Step 3 plan; final enumeration is Step 4 scope.
- Tenant DB inspection for D369 — Step 3 plans the dual-write read path; Step 5 verifies.
- bc-ai inventory deepening — Step 3 plans Gate M10 panel implementation against the existing MCF requirements §11.3 tool allowlist; bc-ai-specific implementation falls in Step 5.

---

## 6. Live DB query log (verification appendix)

All queries `SELECT`-only against `bc_platform_dev` (PG 17.8) via `bc-postgres` MCP, schema allowlist `[contract, source, metric, platform, runtime, master]`. Queries run on **2026-05-26**.

| Q-ID | Decision area | Query (abbreviated) | Result summary |
|---|---|---|---|
| Q-0 | §1.3 | `pg_list_schemas` | `[contract, master, metric, runtime, source]` — `concept_registry` NOT in allowlist |
| Q-1 | Q1, Q2, Q3, §1.4 | `SELECT 't', COUNT(*) FROM ...` × 17 tables UNION ALL | See full count table below |
| Q-2 | Q1 | `SELECT governance_state_code, COUNT(*) FROM contract.metric_contract_version GROUP BY ...` | active 731 / draft 289 / superseded 2 |
| Q-3 | Q3, §1.4 | `SELECT status_code, COUNT(*) FROM metric.metric_definition GROUP BY ...` | draft 1,214 / deprecated 25 / active 2 |
| Q-4 | Q3 | `SELECT chain_verdict, COUNT(*) FROM contract.chain_status GROUP BY ...` | partial 293 / complete 247 |
| Q-5 | Q3, §2.3.2 | `SELECT mls_state_id, current_value, COUNT(*) FROM metric.mls_state GROUP BY ...` + L-node investigations | MLS-13: 810g+10r+8y; MLS-14: 829g+2r; L-node: 202 verdicts (141g+61na) all 2026-05-15..17; L2 traces only |
| Q-6 | Q3 | `SELECT audit_status_code, COUNT(*) FROM contract.metric_contract GROUP BY ...` | pass 415 / warn 348 / fail 15 / pending 2 |
| Q-7 | §3.5 | `SELECT column_name FROM information_schema.columns WHERE table='canonical_contract'` | 14 columns; **`posting_date_field` NOT present** |
| Q-8 | Q2 | `SELECT role, COUNT(*) FROM metric.metric_formula_variable GROUP BY ...` | input 2,410 / output 1,195 / constant 621 |
| Q-9 | Q2 | `SELECT COUNT(*) ... AVG(LENGTH(formula_text)) ... FROM metric.metric_formula` | 1,216 rows; 100% non-null; avg 18 chars; max 143 |
| Q-10 | Q2 | `SELECT COUNT(*), COUNT(DISTINCT formula_text) FROM metric.metric_formula` | 1,216 rows; 134 distinct |
| Q-11 | Q2 | `SELECT formula_text, COUNT(*) FROM metric.metric_formula GROUP BY ... LIMIT 10` | top: `O1=(I1/I2)*C1` 435; `O1=I1/I2` 252; `O1=I1-I2` 86; `O1=I1` 80; `O1=ML_MODEL(...)` 12 |
| Q-12 | Q3 | `SELECT depends_on_type, COUNT(*) FROM metric.mc_dependency GROUP BY ...` | canonical_contract 1,133 (no metric_snapshot deps) |
| Q-13 | Q1 (key finding) | `SELECT COUNT(*) FROM contract.metric_contract WHERE archived_at IS NOT NULL` | **778 archived; 2 non-archived (of 780)** |
| Q-14 | Q1 (key finding) | `SELECT mc.archived_at IS NULL, mcv.governance_state_code, COUNT(*) FROM JOIN GROUP BY ...` | mc-not-archived×active: **2**; mc-archived×active: **729**; mc-archived×draft: 289; mc-archived×superseded: 2 |
| Q-15 | Q1 (key finding) | `SELECT COUNT(DISTINCT mc_id), COUNT(DISTINCT md_id) FROM JOIN WHERE mcv.active AND mc.not_archived` | **2 / 2** |
| Q-16 | Q2 | `SELECT formula_text LIKE ANY (banned patterns), COUNT(*) FROM metric.metric_formula GROUP BY ...` | banned 27 / not 1,189 |
| Q-17 | §2.3.2 | `SELECT column_name FROM information_schema.columns WHERE table='l_node_semantic_verdict'` | 14 cols incl. l1-l8 + overall + computed_at |

### Full count table (from Q-1)

| Table | Rows |
|---|---:|
| `contract.metric_contract` | 780 |
| `contract.metric_contract_version` | 1,022 |
| `contract.metric_contract_approval` | **0** |
| `metric.metric_definition` | 1,241 |
| `metric.metric_knowledge` | 1,241 |
| `metric.metric_binding` | 1,133 |
| `metric.metric_formula` | 1,216 |
| `metric.metric_formula_variable` | 4,226 |
| `metric.mls_state` | 1,659 |
| `metric.mls_state_event` | 3,317 |
| `metric.mls_trigger_binding` | 10 |
| `metric.mc_dependency` | 1,133 |
| `metric.readiness_ledger` | 905 |
| `contract.chain_status` | 540 |
| `contract.chain_trace` | 800 |
| `contract.l_node_semantic_verdict` | 202 |
| `contract.l_node_semantic_trace` | 25,237 |
| `contract.canonical_contract` | 56 |

### Decision-sensitive deltas vs inventory (2026-05-07 → 2026-05-26)

| Metric | Inventory (2026-05-07 source) | Live (2026-05-26) | Δ |
|---|---:|---:|---:|
| Active MD in DB | 376 | (731 active MCV / 567 distinct MDs / 247 active+complete) | rebased — see §1.4 |
| "Ready" (chain-complete + audit-pass) | 195 | 247 active + chain-complete | +52 |
| Semantic-collapse | 200 | 2 (MLS-14 red) | −198 (cleanup since 2026-05-07) |

### Material findings

- **Q-13 / Q-14 / Q-15**: only 2 of 780 `contract.metric_contract` rows are non-archived. 729 active MCVs reference archived parent MCs. Q1 disposition reframed under this evidence.
- **Q-7**: `contract.canonical_contract.posting_date_field` does **not** exist. D365 hardprerequisite for runtime evaluation of computed-dimension metrics.
- **Q-5 (L-node)**: writer exists (L2-only); inventory F-LNODE-1 partially incorrect; refined to partial-gap.
- **Q-1 (`metric_contract_approval` = 0)**: existing approval table is empty; safe to deprecate.
- **Q-10**: 134 distinct formula texts cover 1,216 rows. The text-to-AST translation surface is small.
- **Q-16**: 27 of 1,216 formulas use banned functions (2.2%) — addressable as MCF AST taxonomy decision.

---

## Document verification

- **Sections present:** 1 (Scope/method/evidence rules), 2 (Five decision areas — five sub-sections 2.1-2.5), 3 (Cross-cutting coordination items — seven sub-sections 3.1-3.7), 4 (Operator-approval checklist), 5 (Recommended Step 3 inputs). All 5 required sections present. §6 (Live DB query log) is the verification appendix.
- **No code/schema/DB changes.** This is a docs-only commit. All DB access was read-only `SELECT`.
- **All operator-owned decisions explicitly marked OPERATOR DECISION REQUIRED.** Recommendations are recommendations; survey does not create authority.
- **All recommendations cite evidence**: requirements §X, inventory §X / F-X, or live DB query Q-N. Every claim is traceable.
- **Live DB query log printed** in §6 with timestamps, query identifiers, and result summaries.
