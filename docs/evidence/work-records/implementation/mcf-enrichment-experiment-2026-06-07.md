---
title: MCF Candidate-Enrichment Experiment — Panel-Side vs Batch
description: Records the complete recovered MCF picture (store/runtime boundary, candidate-source bottleneck, enrichment fork), the objective of the panel-side-enrichment experiment, and its decisive result — the M12 panel authored a complete, correct metric contract from a THIN un-enriched seed by self-enriching via BCF tool calls, validating panel-side enrichment (E2) and removing the need for a batch pre-enrichment pipeline (E1).
status: draft
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: catalog
focus: mcf-enrichment-experiment
---

# MCF Candidate-Enrichment Experiment — Panel-Side vs Batch (2026-06-07)

> **One-line result:** the M12 panel authored a complete, correct metric contract from a **thin, un-enriched seed** by grounding itself in the BCF substrate via tool calls — **panel-side enrichment (E2) works; a batch pre-enrichment pipeline (E1) is not required.**

---

## 1. Context — the complete recovered picture

This experiment is the culmination of a session that reconstructed the real MCF architecture from **ground truth (live DB + running code), not documentation** — after the docs were repeatedly found stale. The chain of verified findings:

### 1.1 Store / runtime boundary
- **D426 (DEC-3f093f, decided 2026-06-02)** governs the metric-contract store: `mcf.*` is canonical for new MCs; MCF must **not** write legacy `metric.*`/`contract.*`; the only projection contemplated is `mcf → NEW shadow tables` (unbuilt). *(The earlier re-entry index omitted D426 — a navigation bug, since fixed.)*
- **Operator direction = "Good B via clean slate":** make `contract.metric_contract*` the **single published metric-contract store** (clean slate), MCF the **governed authoring framework** that materializes published metrics into it, legacy `metric.*`/`contract.*` **wiped**, the tested runtime **untouched**. This **amends D426** (formal amendment required — not a shortcut).

### 1.2 Runtime ground truth (verified)
- Tenant `tbc_sandbox1_dev`: typed `fact.ms_*` tables are **live and populated** (e.g. `ms_days_sales_outstanding=42`, `ms_total_ar_balance=187`); `envelope.metric_snapshot=0`. Typed-first storage shipped despite its ADR (DEC-95687d) still reading `proposed`.
- **All** tenant runtime facts were produced by the **legacy** metric-evaluation engine (45 legacy `contract.metric_contract` ids, evaluated 2026-04-28…05-07). **MCF has produced zero tenant facts.** The engine reads contract envelopes **only** from `contract.metric_contract_version.contract_json`.
- `contract.metric_contract`: 780 rows, **2 active / 778 archived** (headers); but `contract.metric_contract_version`: **731 `active` versions** — a half-done quarantine. Moot under clean-slate (delete, don't reconcile).

### 1.3 BCF↔MCF binding (verified real)
- The 5 `mcf.metric_contract` specimens bind **real** `concept_registry` business concepts (e.g. grain entity `e3963e45` Customer Invoice; concepts for amount/date/identifier), authored via `bcf-registry-authoring-panel`. Authoring-time binding is **real and exercised**; runtime evaluation through those bindings has **never** run (consistent with §1.2).

### 1.4 The candidate-source bottleneck (the "bigger problem")
- The MCF reservoir (`ReservoirIngestionService`) has **three** source adapters: `seed_metrics` (Mongo `bc_seed.seed_metrics`), `metric_definition` (Postgres), `operator_direct`.
- Only **`metric_definition` (1,241 rows)** + operator-direct are **wired to a live surface**. The **`seed_metrics` path is dormant** — `McfModule` injects no Mongo collection and no route calls `ingestFromSeedMetrics`. All 5 MCs were authored via the `metric_definition` carve-out.
- The full metric universe is **`bc_seed.seed_metrics` = 12,501 docs** (verified). So MCF, as wired, **caps at ~1,242 candidates** then has nothing to author.

### 1.5 The enrichment fork (what the experiment resolves)
- The 1,241 `metric.metric_definition` rows are **AI-enriched** (`metric_knowledge`: `definition_summary`, `formula_explanation`, `stakeholders`, `drivers`, …; produced by a batch `metric_enrichment_job` — 1,141 jobs). The raw 12,501 Mongo seeds are **thin** (one-line description + prose formula only).
- The Maker consumes the enrichment. So the candidate-source bottleneck is really an **enrichment** problem: can the other ~11,260 thin seeds become MCF-quality candidates?
  - **E1 — batch pre-enrich:** re-run the AI enrichment pipeline on the raw seeds (reuses the proven, but operator-distrusted, batch path).
  - **E2 — panel-side enrichment:** the panel enriches at authoring time from the BCF substrate (the documented M17 intent).
- **Operator lean: E2** — "batch pre-enrich is not reliable; that is why we created panels." This experiment tests it.

---

## 2. Objective

**Decide E1 vs E2 empirically:** can the MCF M12 panel author a *quality* metric contract from a **thin, un-enriched seed**?

- If **yes** → the panel self-enriches; **E2** holds; no batch pipeline needed; standing up the **Postgres `mcf.seed_metric` operational reservoir** (from the Mongo/export seed archive) is sufficient; `metric.metric_definition` is not needed as a candidate source.
- If **no** → enrichment must precede authoring; **E1** (or equivalent) required.

**Design (isolates the enrichment variable):** feed a **thin** operator-direct candidate for `average_revenue_per_invoice` — built from the raw Mongo seed fields only (one-line description + prose formula `Total Revenue / Total Number of Invoices Issued`; **no** `definition_summary`/`formula_explanation`/`stakeholders`/`drivers`/`thresholds`). Its **enriched** twin already produced the active ARPI MC, so grain, bindings, and grammar are known-good — the **only** difference from the successful enriched run is the **absence of enrichment**. Run the live M12 panel and inspect the Maker's proposal.

*(Operator-direct is a faithful proxy for the dormant `seed_metrics` path: both produce a `normalized_candidate_json` of raw seed fields stripped of `co_bindings`.)*

---

## 3. Result — **E2 validated**

`panel_run b85186ef-eaba-42d6-af6b-d3425e3f976b` on thin intake `23331839-3861-46a0-90de-4ef95d0c9eb1`. All three vendor models ran clean; `defect_code: null`; `grounding_check_passed: true`.

| Role | Model | Verdict | Behavior on the thin seed |
|---|---|---|---|
| **Maker** | `claude-opus-4-7` (anthropic) | **APPROVE_FOR_DRAFT** | **6 BCF tool calls** → discovered grain = Customer Invoice (`e3963e45`); bound **net amount** (`342669f7`, amount/decimal) as numerator, **document number** (`51482979`, identifier) as count-distinct denominator, **posting date** (`61e19048`) as period anchor; verified all three reachable at depth=1. 5 grounded claims. |
| **Checker** | `deepseek.v3.2` (bedrock) | **APPROVE_FOR_DRAFT** | **10 independent tool calls** — re-confirmed the entity + concepts. |
| **Judge** | `gpt-5.5` (openai) | OPERATOR_REVIEW | **`near_duplicate_requires_review`** vs active ARPI (`49cdde1a`): *"name, display, grain, formula, filters, and temporal gate align, but variable concept IDs differ."* |

**Interpretation:** from a thin seed with no pre-baked enrichment, the Maker **self-enriched at authoring time by grounding in the BCF substrate via tool calls**, and produced a complete, well-formed MC — grain + `divide(sum(numerator), count_distinct(denominator))` formula + period_aggregate temporal gate + three real BCF concept bindings — **structurally identical** to the MC that ARPI obtained from a fully *enriched* candidate. The Checker independently confirmed it. The OPERATOR_REVIEW verdict is **correct governance routing** (the proposal *matches* an existing active MC), not an enrichment failure — and is itself proof that a thin seed reconstructed the enriched metric's identity.

**Conclusion: the panel is the enrichment mechanism — _validated enough to proceed with Gate 0_, not proven across the full 12,501-seed corpus (see §5). E1 (batch pre-enrich) is not required for this path. The operator's lean was correct.**

### 3.1 Second run — novel seed (confirming, 2026-06-07)

To remove the near-duplicate confound, a **second thin run** used a *novel* seed (no existing MC twin): `percentage_of_invoices_sent_on_time` = `(Number of Invoices Sent on Time / Total Number of Invoices Issued) * 100` — intake `93136dd5`, `panel_run 088e22f9`.

| Role | Verdict | Self-grounding from thin seed |
|---|---|---|
| Maker | OPERATOR_REVIEW | 6 claims, **5 BCF tool calls** |
| Checker | OPERATOR_REVIEW | **8 tool calls** |
| Judge | OPERATOR_REVIEW | reason: **`approve_with_loose_grounding`** |

`defect_code: null`.

**This supports E2.** The panel again **self-enriched from thin input** (Maker 6 claims + 5 tool calls; Checker 8 tool calls) — the thin seed never blocked authoring. It then **correctly routed the metric to OPERATOR_REVIEW for loose grounding**: "sent on time" requires a *sent-date-vs-due-date* predicate the current substrate/grammar cannot cleanly express, so the panel **withheld auto-approval rather than rubber-stamp it** — the governance behaviour panels exist for.

**Critical distinction — enrichment failure vs grammar/filter/reference insufficiency:** the OPERATOR_REVIEW here is **not** an enrichment failure (the panel enriched fine from thin input). It is a **grammar/filter insufficiency** — the *metric* needs a predicate the platform doesn't yet express (same class as **D400** as-of/window, the filter substrate, **D427** references). Enrichment (E2) is settled; these are *separate, already-identified gates*.

**Net of both runs:** E2 (panel-side enrichment from a thin seed) is **validated enough to proceed with Gate 0**. A clean novel `APPROVE_FOR_DRAFT` end-state is **not yet captured** (run 1 = near-duplicate; run 2 = loose-grounding predicate) — both correct governance outcomes. It will appear when a *grammar-fitting* metric (pure simple aggregation) is authored, which is Gate-1 work — **not** a precondition for the enrichment decision.

---

## 4. Implications / what this unblocks

1. **The "MCF caps at 1,242" bottleneck dissolves.** The panel can author from the raw **12,501**-seed corpus — it enriches per-metric from BCF. **Gate 0 = create/import/wire the Postgres `mcf.seed_metric` operational reservoir** (from the Mongo/export seed archive, with count/hash/sample parity; breadth only). No batch enrichment pipeline.
2. **`metric.metric_definition` (1,241 enriched) is not required as a candidate source.** The operational reservoir is **Postgres `mcf.seed_metric`** (imported from the Mongo/export seed archive, 12,501); the **panel** is the enricher. ⚠ **But do not wipe its enrichment casually:** `metric_knowledge` (1,241 AI-enriched rows — `definition_summary`/`formula_explanation`/`stakeholders`/`drivers`) is **expensive historical work**. Archive/export it before any clean-slate wipe — retained as reference/evidence, not runtime authority.
3. **"Good B via clean slate" is coherent end-to-end:** PG `mcf.seed_metric` reservoir (from the Mongo/export seed archive) → panel self-enrichment → author into a clean single published store (`contract.metric_contract*`) → existing runtime evaluates → typed `fact.*`.

---

## 5. Caveats (honest scope; n=2)

- **Two runs, two metrics** (run 1 near-duplicate; run 2 novel-with-predicate). The *mechanism* — panel tool-call self-enrichment from thin input — is **proven on both runs**. **A clean novel `APPROVE_FOR_DRAFT` end-state has not yet been captured:** run 1 hit near-duplicate (governance), run 2 hit loose-grounding (a predicate the substrate can't cleanly express). Both are **correct governance outcomes, not enrichment failures**. A clean novel APPROVE needs a metric that fits the *current* grammar (pure simple aggregation — no predicate/filter/balance/reference); most finance seeds carry one of those, which is the **D400 / filter-substrate / D427** gap map — **separate from enrichment**.
- Says **nothing** about metrics that need **references (D427)** or **as-of-balance / trailing-window (D400)** — those remain separate, unrelated gates. Enrichment was never their blocker.
- The thin candidate was submitted via the **operator-direct** endpoint as a faithful proxy; the actual `seed_metrics` Mongo path still needs wiring + a live ingest test (Gate 0).

---

## 6. Evidence

- **Intake:** `23331839-3861-46a0-90de-4ef95d0c9eb1` (`operator_direct`, thin `normalized_candidate_json` = raw seed fields only). Now `consumed_by_panel`.
- **Panel run:** `b85186ef-eaba-42d6-af6b-d3425e3f976b`. Transcripts: maker `7aae09b5`, checker `61b406e5`, judge `9b2a58c4`.
- **Matched active MC:** ARPI `49cdde1a-8bb3-41ad-9f67-9bb05d9f18a0`.
- **Seed source:** `bc_seed.seed_metrics` doc `average_revenue_per_invoice` (description = *"The average amount of revenue generated per invoice…"*; `reference_formula` = *"Total Revenue / Total Number of Invoices Issued"*; no enrichment fields).
- **Run 2 (novel, 2026-06-07):** seed `percentage_of_invoices_sent_on_time`; intake `93136dd5-8f34-4aaa-8519-9fe733a94f14`; `panel_run 088e22f9-8444-451a-86d8-fd13b31443b3`; verdict OPERATOR_REVIEW / `approve_with_loose_grounding`; Maker 6 claims + 5 tool calls, Checker 8 tool calls, Judge — all `defect_code: null`.
- **Substrate footprint (both runs):** +2 intakes, +2 panel_runs, +6 transcripts. **0 metric contracts created** (both OPERATOR_REVIEW; neither materialized).

---

## 7. Agreed sequence (operator-locked, 2026-06-07)

> **Store-decision note:** E2 settles *candidate enrichment*, **not** "Good B" by itself — but it makes the target coherent: **Mongo `seed_metrics` → MCF panel enriches/authors → clean published `contract.metric_contract*` store → existing runtime.** Call it the **"clean single published metric store,"** never "reuse legacy" — that wording keeps the future-engineer mental model clean.

1. **Commit/fix the re-entry docs** so D426 + this experiment are both visible.
2. **One novel thin-seed confirming run** (if cheap) — capture the clean `APPROVE_FOR_DRAFT` end-state, remove the near-duplicate caveat.
3. **D426 amendment — "Clean Single Published Metric-Contract Store"** (not "reuse legacy"). Five locks: (a) MCF = governed authoring framework; (b) raw Postgres `mcf.seed_metric` = operational candidate reservoir (Mongo/export = preserved upstream seed archive); (c) panel = enrichment mechanism; (d) `contract.metric_contract*` = the single clean published runtime metric-contract store; (e) legacy Postgres metric data (incl. `metric_knowledge`) **archived/exported, then wiped under DBCP**.
4. **Gate 0** — create/import/wire the Postgres `mcf.seed_metric` reservoir: a DBCP to create the table + import the 12,501 from the Mongo/export seed archive (with count/hash/sample parity); PG-backed adapter/repoint + ingest route/job (filter by `function_code`); live ingest→panel test. MCF intake/runtime reads Postgres, not Mongo.
5. **Build MCF materialization** into clean `contract.metric_contract*`.
6. **Only then wipe/reseed** — golden snapshots + rollback.

> Authority context: this doc is a finding/decision record. Canonical MCF authority remains **DEC-c3e57f/D422** + **DEC-3f093f/D426** + the build plan; orientation via `mcf-re-entry-index.md` (which should link this report).
