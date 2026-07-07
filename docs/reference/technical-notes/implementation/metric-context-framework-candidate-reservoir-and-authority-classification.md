---
uid: metric-context-framework-candidate-reservoir-and-authority-classification
title: Metric Context Framework (MCF) — Candidate Reservoir and Authority Classification (Step 2 Addendum)
description: Step 2 addendum to the MCF gap/risk survey. Locks the reservoir-vs-authority discipline before Step 3 build plan. Defines five classes (candidate intent / weak hint / semantic authority / binding authority / formula authority), evidence-grounded with live samples from bc_seed.seed_metrics (~12.5k loosely-formed candidates), the 2 non-archived contract.metric_contract rows, and spot-checks of 10 active+chain-complete legacy MCs. Records 7 architectural risks and 7 guardrails to encode in the foundational MCF ADR (Gate M1). Recommends a single decision wording for operator lock. Not an ADR. Not a build plan. Direct precondition for Step 3.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: gap-survey-addendum
---

# Metric Context Framework (MCF) — Candidate Reservoir and Authority Classification

## 1. Scope, method, and link to gap survey

### 1.1 Purpose

The MCF gap/risk survey (`metric-context-framework-gap-survey.md`, commit `0ba202b`) resolved Q1 (`contract.metric_contract` disposition), Q2 (TEXT formula → AST), Q3 (per-service reuse + MLS-14/PE-MC-10 layering), Q4 (BCF density criteria), Q5 (gate sequencing). It did **not** address a load-bearing question that becomes load-bearing the moment Step 3 build plan opens:

> **What does MCF authoring propose FROM? What is the difference between a source that informs authoring and a source that creates authority?**

Architecture discussion (this conversation, post commit `0ba202b`) confirmed:
- The existing SQL `contract.metric_contract` corpus is non-authority by class (substrate it was built on is gone).
- `metric.metric_definition` / `metric.metric_knowledge` are preserved as candidate intent, not authority (MCF requirements §5 + §13).
- The Mongo `bc_seed.seed_metrics` collection (~12.5k loosely-formed candidate metrics) is a peer candidate-intent reservoir.
- BCF Registry creates semantic authority. MCF's gated authoring path creates binding + formula authority. Nothing else.

This addendum records the discipline, the evidence behind it, and the guardrails the foundational MCF ADR must encode.

### 1.2 Why an addendum, not an inline edit to the gap survey

- The gap survey is commit-stable; retroactive surgery is avoided.
- This decision is single-topic — clean as its own doc.
- The classification is independently citable from the foundational MCF ADR (Gate M1) and from Step 3 build plan.

### 1.3 Method

- Read-only inspection across bc-docs, bc-core (gap survey already covered), `bc_platform_dev` (bc-postgres MCP), `bc_seed` Mongo (Node.js read-only via bc-seed's `mongodb` dependency).
- Five operator-approved evidence checks (E1-E5) executed in this session — log in §8.
- Recommendations cite evidence inline.
- Operator-owned decision items flagged explicitly.

### 1.4 Working hypothesis under test

The hypothesis the architecture review affirmed:

| # | Statement | Status going in |
|---|---|---|
| H1 | Existing SQL MC corpus = historical/failure evidence only | Affirmed in arch review with sharpened wording |
| H2 | SQL metric_definition / metric_knowledge = preserved KPI intent, not authority | Affirmed; locked in MCF §5 + §13 |
| H3 | Mongo seed metrics = candidate-intent reservoir, peer to (H2), not authority | Affirmed |
| H4 | BCF Registry = semantic binding authority | Affirmed; locked in MCF §6 |
| H5 | MCF panel + deterministic verifier = formula/package authority | Affirmed; locked in MCF §11 + §12 |
| H6 | Future MCF contracts live under `mcf.*`, no migration | Affirmed in gap survey Q1 Option C |

This addendum produces the discipline and evidence to lock the hypothesis.

---

## 2. The five-class classification

### 2.1 Classes

| Class | Role | Creates authority? | What flows through it |
|---|---|---|---|
| **Candidate intent** | "This KPI is worth considering for MCF authoring" | **No** | A name + description in a reservoir. Inclusion does not create an MCF MC. |
| **Weak hint / prompt context** | Panel may *reference for reasoning*, never *cite as grounding* | **No** | `metric_knowledge` prose; seed `description` / `measurement_approach` / `reference_formula` text; legacy SQL formula text shapes; operator-attached business guidance per MCF §11.3.5 |
| **Semantic authority** | "This BC IS this thing in the business vocabulary" | **Yes — BCF Framework Approval** | `concept_registry.entity / business_concept / characteristic` active rows |
| **Binding authority** | "This MC variable binds to this BC" | **Yes — MCF Framework Approval** | `mcf.metric_variable_binding` after PE-MC-1..PE-MC-10 pass + operator confirm |
| **Formula authority** | "This is what this MC computes" | **Yes — MCF AST authoring + deterministic verifier** | `mcf.metric_formula_ast` (authored as AST) + passing `mcf.metric_self_verification_result` |

### 2.2 The two operative rules

**Rule 1.** *Candidate and weak-hint sources FLOW IN to the workbench as inputs; AUTHORITY is CREATED by MCF's gated authoring path. No source is authoritative by virtue of being in a reservoir.*

**Rule 2.** *No reservoir creates an MCF MC by inclusion. Authoring takes a candidate, runs the workbench, produces a draft, and progresses under PE-MC-1..PE-MC-10 + operator confirm. The act of authoring is the act that creates authority.*

These two rules together prevent:
- "We saw it in the seed catalog, therefore it's a real metric."
- "It computed snapshots in the legacy SQL MC, therefore its formula is correct."
- "It has APQC provenance, therefore its definition is grounded."

None of those are authority claims under MCF.

### 2.3 Reservoir registry

Three candidate-intent reservoirs at MCF first-deployment time:

| Reservoir | Size (today) | Provenance | Discipline level |
|---|---:|---|---|
| `bc_seed.seed_metrics` (Mongo) | 12,501 docs | `sources[]`: internet (71%) / apqc (33%) / cfo-pack (6%); see §3.4 | Loose — see §3.1, §3.4, §3.5 |
| `metric.metric_definition` (Postgres, platform) | 1,241 rows | Operator-authored or imported; carve-out per MCF §5 | Variable — see §3.3 |
| Operator-direct submission | n/a | Operator authoring tool (MCF §6 operator surfaces, planned) | Highest — operator-attached intent |

**No fourth reservoir.** Legacy SQL `contract.metric_contract` rows are NOT a reservoir; they are historical artifact (per gap survey Q1 Option C).

---

## 3. Evidence

### 3.1 E1 — `bc_seed.seed_metrics` schema and quality

**Sample** (5 random docs, via `$sample` aggregation on 2026-05-26). Representative shape across the collection:

Each document carries: `metric_name`, `display_name`, `description`, `function_code`, `subfunction_code`, `industry_category_code`, `industry_code`, `tier_code`, `direction`, `bsc_perspective`, `reference_formula`, `measurement_approach`, `thresholds`, `co_bindings`, `related_metrics`, `search_tags`, `sources[]`, `confidence`, `created_at`, `updated_at`.

**Field completeness across all 12,501 docs:**

| Field | Populated | % |
|---|---:|---:|
| `description` | 12,501 | 100% |
| `subfunction_code` | 9,668 | 77% |
| `reference_formula` | 8,785 | 70% |
| `measurement_approach` | 7,696 | 62% |
| `bsc_perspective` | 7,344 | 59% |
| `co_bindings` | 506 | 4% |
| `direction` | 340 | 3% |
| `thresholds` | 0 | **0%** |

**Quality observations:**

- Definitions range from substantive ("the percentage of tax returns filed on time and accurately") to vague ("Metric within Produce/Assemble/Test product"). Quality varies; the `confidence` field stratifies (see §3.5).
- `reference_formula` when present is **natural language** ("(Number of Compliant Tax Filings / Total Tax Filings Required) * 100", "Total Number of Contract Compliance Breaches"). Not formal, not parsable as AST.
- `co_bindings` is null in 96% of docs. The 4% that have it carry pre-D418-era bindings — must be treated as historical-only per the working rule (no BF/BO/CF/CM as evidence).
- `thresholds` is universally NULL — no metric in the reservoir carries threshold semantics.
- `direction` is rarely set (3%) — most seeds do not declare higher-is-better vs lower-is-better.

**Implication for MCF:** seeds carry *intent* (this KPI is conceptually worth measuring), prose *context* (a description, sometimes a measurement approach), and *category tags* (function, subfunction, bsc_perspective). They do **not** carry formula authority, binding authority, threshold authority, or direction authority. All of those must be created by MCF authoring against BCF.

### 3.2 E2 — The 2 non-archived `contract.metric_contract` rows

| `metric_contract_id` | `metric_contract_name` | `display_name` | `function_code` | `subfunction_code` | `audit_status_code` | `created_at` |
|---|---|---|---|---|---|---|
| `019e25b7-2ee0-7f8a-96c9-e5843f81b3dd` | `mc__revenue_collection_rate` | Mc — Revenue Collection Rate | finance | accounts_receivable | pending | 2026-05-14 09:00 |
| `019e2613-fc7a-7755-b76f-6b1433ab247b` | `mc__ar_growth_rate` | Mc — Ar Growth Rate | finance | accounts_receivable | pending | 2026-05-14 10:41 |

Both authored 2026-05-14 during SES-594568. Both `audit_status_code='pending'` (never passed formula audit). Both in finance / accounts_receivable.

**Implication for MCF:** these two MCs are recent draft-state authoring experiments, not operationally-live KPIs. They have **no special carry-over claim**; MCF can re-author them from scratch (or archive them) per gap survey Q1 Option C without disrupting any live consumer.

**OPERATOR DECISION (low-stakes):** archive these two before MCF M2 substrate cutover, or carry them as candidate intent for re-authoring.

### 3.3 E3 — Spot-check of 12 active + chain-complete legacy MCs

| `metric_contract_name` | Formula text | Variable count |
|---|---|---:|
| `mc__accounts_payable_turnover_ratio` | `O1 = I1 / I2` | 3 |
| `mc__accounts_receivable_turnover_ratio` | `O1 = I1 / I2` | 3 |
| `mc__adjustment_resolution_time` | `O1 = I1 - I2` | 3 |
| `mc__aged_dispute_count_30_plus_days` | `O1 = I1` | 2 |
| `mc__ar_to_sales_ratio` | `O1 = I1 / I2` | 3 |
| `mc__ar_turnover` | `O1 = I1 / I2` | 3 |
| `mc__arpa` | `O1 = I1 / I2` | 3 |
| `mc__arpu` | `O1 = I1 / I2` | 3 |
| `mc__arpu_by_segment` | `O1 = I1 / I2` | 3 |
| `mc__asset_management_training_investment` | `O1 = I1` | 2 |
| `mc__asset_utilization_ratio` | `O1 = I1 / I2` | 3 |
| `mc__audit_adjustments_count` | `O1 = I1` | 2 |

**Observations:**
- All 12 are simple shape patterns (`O1 = I1 / I2`, `O1 = I1 - I2`, `O1 = I1`). Confirmed gap survey Q-11 distribution.
- Variable counts of 2 or 3 — no rich multi-variable formulas in the spot-checked subset.
- Names look semantically distinct (`accounts_payable_turnover_ratio` vs `accounts_receivable_turnover_ratio` are different concepts).
- **But the formula tells us nothing about what they compute.** `O1 = I1 / I2` could be revenue/cost, AR/sales, capex/depreciation. The semantic content lives in the variable bindings (in `metric_formula_variable`), not the formula. And those bindings were built over BF/BO/CF/CM substrate which is gone.

**Implication for MCF:** even the operationally-validated subset has formula-shape only. The semantic content (what I1 / I2 actually were) was substrate-resolved at runtime and is no longer reconstructable from these rows alone. **Re-authoring under MCF (with operator + BCF panel deciding what I1 and I2 should bind to in the post-D418 Registry) is the same cost as starting from a seed catalog candidate** — both routes require the operator + panel to think the binding through. There is no salvage shortcut from the legacy MC corpus.

### 3.4 E4 — `seed_metrics` provenance

Sources distribution (12,501 docs, multi-source allowed):

| Source | Count | Notes |
|---|---:|---|
| `internet` | 8,860 | Loose — likely scraped or LLM-generated from web sources. Lowest-trust provenance. |
| `apqc` | 4,085 | American Productivity & Quality Center — legitimate KPI taxonomy publisher. Higher-trust provenance. |
| `cfo-pack` | 771 | Internal CFO playbook content. Higher-trust within the BareCount-curated subset. |

**Provenance classification for PE-MC-1 evidence class:**

| Source | PE-MC-1 class (per MCF §13.1) | Notes |
|---|---|---|
| `apqc` | (b) bc-seed catalog entry with verified provenance lineage | bc_seed.seed_metrics rows tagged `apqc` qualify as bc-seed lineage |
| `cfo-pack` | (c) operator-authored bounded-domain definition with explicit business justification | Operator-curated; defensible as bounded-domain |
| `internet` | (d) source-system observation provisional — or fails PE-MC-1 entirely | Loose; needs operator-confirm at draft time and likely standard-ref re-grounding |

**Implication for MCF:** the seed reservoir is **stratified**. APQC-sourced and cfo-pack-sourced seeds are PE-MC-1-eligible immediately. Internet-sourced seeds (71% of reservoir) need additional grounding — they cannot pass PE-MC-1 on their own provenance alone.

### 3.5 E5 — Dedupe signal + quality stratification

**Exact-match dedupe by `metric_name`:**

| Metric | Value |
|---|---:|
| Total docs | 12,501 |
| Distinct `metric_name` | 12,501 |
| Exact-match duplicate rows | **0** |

**Confidence stratification:**

| Confidence | Count | % |
|---|---:|---:|
| `medium` | 10,967 | 88% |
| `low` | 1,137 | 9% |
| `high` | **397** | **3%** |

**Function distribution (top 10):**

| Function | Count |
|---|---:|
| operations | 1,868 |
| finance | 1,281 |
| (null) | 1,186 |
| human_resources | 1,175 |
| supply_chain | 1,099 |
| it_operations | 991 |
| marketing | 973 |
| executive | 849 |
| risk_compliance | 777 |
| sales | 554 |

**Implications:**
- **Exact-match dedupe is clean** — no two rows share the same `metric_name`. This makes the `metric_name` a safe primary key for reservoir-side reference.
- **Semantic dedupe is unverified** — two rows with different names may carry the same intent ("days_sales_outstanding" vs "dso" vs "avg_collection_period"). MCF panel must catch this; reservoir does not pre-deduplicate.
- **Quality is stratified** — only 397 rows (3%) are high-confidence. **The 397 high-confidence + apqc-sourced subset is the natural Step 4 + Step 5 starting pool** (estimate: ~250-300 rows after the intersection — small enough to triage manually, large enough to cover 10 representative metrics with operator selection room).
- 1,186 docs (9%) have NULL function_code — these need function classification before reservoir consumption.

---

## 4. Architectural risks

Carried forward from the architecture review; refined per E1-E5 evidence.

| # | Risk | Severity (now) | Mitigation belongs in |
|---|---|---|---|
| **R1** | **Seed-driven BCF shape contamination.** Step 4 BCF enrichment scope being driven by seed wording rather than business reality. Loose seed descriptions become loose BCF concepts. | **High** | MCF ADR Gate M1 + Step 4 brief |
| **R2** | **Duplicate-intent fan-out.** Two reservoir entries (e.g. "days_sales_outstanding" vs "avg_collection_period") with same intent produce two MCF MC drafts unless the panel recognizes the duplicate. Exact-match dedupe is clean (E5) — semantic dedupe is the open risk. | Medium | MCF panel discipline (PE-MC-9 uniqueness + de-dup heuristic) |
| **R3** | **Hidden source-system assumptions.** A seed for "CLV" may have been authored assuming a specific CRM; the panel binds without surfacing the assumption. | Medium | Panel tool surface includes `source_reality.summarize`; PE-MC-1 grounding requires explicit source-system citation where applicable |
| **R4** | **Weak-definition admission.** 88% of seeds are medium-confidence; some descriptions are vague ("Metric within Produce/Assemble/Test product" per E1). Thin seeds may pass into draft. | Medium | Pre-panel intake quality filter (rule-based, not AI) — minimum description length + non-template heuristic |
| **R5** | **Backdoor legacy semantics.** A seed authored while looking at BF/BO/CF/CM artifacts (or carrying the 4% `co_bindings` from E1 — 506 docs in the reservoir have pre-D418 binding fragments). Panel consumes uncritically; dead semantics return. | **High** | Working rule binding (MCF requirements §1 / CLAUDE.md): no BF/BO/CF/CM as evidence. Panel rejects any candidate whose only grounding is legacy primitives. **Plus: reservoir-side filter — strip `co_bindings` field from seeds before panel ingestion.** |
| **R6** | **Scale-of-reservoir overwhelm.** 12,501 seeds + 1,241 metric_definitions = ~13.7k candidates. Sequential consumption is decades of operator time. | Medium | Step 4 selection criteria (start with 397 high-confidence + apqc-sourced ≈ 250-300 rows). Step 5 cadence model. |
| **R7** | **Provenance-thin candidates.** 71% of seeds are `internet`-sourced (E4) — fail PE-MC-1 on their own provenance. | Medium | PE-MC-1 (d) operator-confirm-required path applies; internet-sourced seeds need additional grounding before activation |

---

## 5. Guardrails for the foundational MCF ADR (Gate M1)

These seven guardrails encode the discipline above into the foundational MCF ADR scope.

1. **No candidate reservoir creates authority by inclusion.** Inclusion in `bc_seed.seed_metrics`, `metric.metric_definition`, or any future reservoir makes a KPI a *candidate*. The act of MCF authoring under Framework Approval is the act that creates authority. Stated explicitly in the ADR body.

2. **BCF enrichment scope is operator + BCF-panel decided, not seed-wording driven.** Step 4 BCF enrichment selects concepts based on business reality (operator judgment, BCF panel grounding); seeds inform priority order, not concept selection.

3. **Panel rejection of legacy-only grounding is mandatory.** A candidate whose only grounding traces to BF/BO/CF/CM artifacts is rejected at intake. The `co_bindings` field on seed_metrics docs (4% / 506 rows) is **stripped at reservoir-ingestion time** before any panel sees it — the working rule cannot rely on panel discipline alone.

4. **Duplicate-intent detection is PE-MC-9 at draft → review.** PE-MC-9 (definition uniqueness) runs against `mcf.*` AND against pending drafts in the queue AND against the 5-class classification (a draft cannot share intent with another draft from the same reservoir).

5. **Source-system assumptions must be made explicit before draft.** If a candidate references "the CRM" or "the SAP system" implicitly, the panel surfaces the assumption via `source_reality.summarize` and routes to operator confirm before draft.

6. **Reservoir provenance is a recorded panel-input field.** `mcf.metric_authoring_panel_run` records: reservoir name (`bc_seed.seed_metrics` / `metric.metric_definition` / `operator_direct`), reservoir entry ID, reservoir provenance source(s), reservoir confidence band. Auditable forever.

7. **No SQL MC corpus migration; ever.** Gap survey Q1 Option C narrow-scope is locked. The 2 non-archived MCs go through MCF authoring as if greenfield (no carryover of formula text, binding, or version history beyond an optional `provenance.legacy_mc_uid` reference field on the new MCF MC for operator orientation).

---

## 6. Recommended decision wording

**For operator review and ADR-grade adoption** at Gate M1:

> **MCF candidate-intent reservoirs are `bc_seed.seed_metrics` (Mongo) and the preserved platform `metric_definition` / `metric_knowledge` carve-out, plus operator-direct authoring submissions. All three are candidate-intent only; none carries authority. Inclusion in a reservoir does not create an MCF MC.**
>
> **BCF Registry (`concept_registry.*` active rows) is the sole semantic binding authority. MCF authoring under Framework Approval — three-model panel + operator confirm + deterministic verifier — is the sole binding-authority and formula-authority creator.**
>
> **No legacy SQL `contract.metric_contract` / `metric_contract_version` / `metric_binding` row is migrated into MCF substrate. The existing tables remain queryable as historical reference. The 2 non-archived legacy MCs are operator-reviewed and, if retained as candidates, re-authored under MCF from scratch.**
>
> **Reservoirs inform authoring; only BCF + MCF gates create authority.**

The last sentence is the discipline in one line, suitable for repetition across CLAUDE.md, build plan, and panel prompts.

**OPERATOR DECISION REQUIRED on:**

- Locking this wording (or an operator-revised version) into the foundational MCF ADR (Gate M1).
- Locking the seven guardrails (§5) into the foundational MCF ADR.
- Disposition of the 2 non-archived legacy MCs (E2): archive or re-author as candidate.
- Pre-authorizing Step 4 reservoir-ingestion to strip the legacy `co_bindings` field from seed_metrics docs (guardrail #3 implementation).

---

## 7. Step 3 build plan — what to consume from this addendum

The Step 3 MCF build plan should consume this addendum at three points:

1. **Gate M1 ADR scope.** The recommended decision wording (§6) and the seven guardrails (§5) belong in the foundational ADR. Step 3 plans Gate M1 to include them.
2. **Gate M2 substrate scope.** `mcf.metric_authoring_panel_run` (already in MCF §17.1) must carry the reservoir-provenance recording fields per guardrail #6. Step 3 confirms.
3. **Step 4 / Step 5 reservoir-ingestion service.** A new service (not in MCF §20 gate list today) is needed: reservoir-ingestion path that strips `co_bindings`, applies confidence + provenance filtering, and routes candidates to the panel intake queue. Step 3 either adds this as a new gate (e.g. M7.5 or M10.5) or scopes it as a Step 4 program prerequisite.

### 7.1 Out of Step 3 scope (defer)

- Semantic-dedupe heuristic implementation — Step 5 with operator-tuned thresholds.
- Reservoir-confidence calibration — Step 5+ as operator data accumulates.
- Future reservoir additions (e.g. cfo-pack v2, new APQC release) — operator-decision at the time.

---

## 8. Evidence appendix — query log (verification)

All evidence read on **2026-05-26**.

### 8.1 bc-postgres MCP queries (read-only SELECT)

| Q-ID | Purpose | Result summary |
|---|---|---|
| EQ-1 | E2 — identify 2 non-archived legacy MCs | `mc__revenue_collection_rate` (2026-05-14) + `mc__ar_growth_rate` (2026-05-14); both finance/AR; both `audit_status_code='pending'` |
| EQ-2 | E3 — spot-check 12 active+chain-complete MCs | All 12 follow `O1 = I1 / I2` or `O1 = I1 - I2` or `O1 = I1` patterns; 2-3 variables each; semantic content was substrate-resolved (BF/BO/CF/CM era, now gone) |
| EQ-3 | E3 — formula text + variable count for above 10 | Confirmed shallow formula corpus across the spot-checked subset |

### 8.2 Mongo (`bc_seed`) read-only sampling

Connection via bc-seed repo's MongoDB driver, env `MONGODB_URI=mongodb://localhost:27017/bc_seed`. No writes.

| Q-ID | Purpose | Result summary |
|---|---|---|
| MQ-0 | List all databases / collections | bc_seed (37 MB); `seed_metrics: 12,501`; plus seed_tables (46,921), seed_xbrl_us_gaap (16,819), seed_xbrl_gaap (11,378), seed_oagis_components (158), etc. |
| MQ-1 (E1) | 5-doc `$sample` of seed_metrics | Schema captured; examples ranged substantive → vague; `co_bindings` null in 4/5 |
| MQ-2 (E4) | Sources distribution (multi-source unwind) | internet 8,860 / apqc 4,085 / cfo-pack 771 |
| MQ-3 (E5) | Confidence distribution | medium 10,967 / low 1,137 / high **397** |
| MQ-4 | Function distribution | top: operations 1,868 / finance 1,281 / (null) 1,186 / HR 1,175 / supply_chain 1,099. 20 distinct functions |
| MQ-5 (E5) | Exact-match dedupe | 12,501 distinct `metric_name` out of 12,501 docs — **zero duplicates** by exact name match |
| MQ-6 (E1 cont) | Field completeness | description 100% / reference_formula 70% / measurement_approach 62% / bsc_perspective 59% / co_bindings 4% / direction 3% / thresholds 0% |

### 8.3 Decision-sensitive intersections

| Subset | Estimated size | Note |
|---|---:|---|
| Seeds with `confidence='high'` | 397 | E5 |
| Seeds with `apqc` in sources[] | 4,085 | E4 |
| Seeds with `confidence='high'` AND `apqc` in sources[] | (not directly queried; expected ≈ 200-300 rows by overlap rate) | The natural Step 4 + Step 5 starting pool |
| Seeds with `co_bindings IS NOT NULL` (must be stripped per guardrail #3) | 506 | E1 + R5 |
| Seeds with NULL function_code (need classification before ingest) | 1,186 | MQ-4 |

### 8.4 Source-access limitations

- **`concept_registry` schema still not in bc-postgres allowlist.** Q4 from gap survey remains: Step 4 / Step 5 transition needs operator-authorized BCF Registry read for concept-density scoping.
- **bc_seed collections other than seed_metrics not deeply sampled.** seed_oagis_components, seed_xbrl_us_gaap, seed_xbrl_gaap, seed_ifrs_taxonomy may be candidate-intent reservoirs for other artifact families (likely BCF, not MCF). Out of MCF addendum scope.
- **Semantic dedupe not run.** Would require an LLM pass over the 12,501 names + descriptions. Step 5 concern; not Step 3 blocker.

---

## Document verification

- **Sections 1-7 present** plus §8 evidence appendix.
- **No code/schema/DB changes.** Only read-only Mongo + bc-postgres SELECT queries.
- **Operator-owned decisions explicitly marked OPERATOR DECISION REQUIRED.** Recommendations are recommendations; survey does not create authority.
- **All recommendations cite evidence** (E1-E5 results, gap survey reference, requirements section, or memory).
- **One-line discipline lock**: "Reservoirs inform authoring; only BCF + MCF gates create authority."
