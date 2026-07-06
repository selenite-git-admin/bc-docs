---
id: metric-onboarding-case-book
order: 37
title: "Metric Onboarding Case Book"
status: evidence
authority: evidentiary
depends_on: [the-invariants, the-evaluation-boundaries, the-contract-grammar, incident-and-change-management, decision-and-change-procedure]
governing_sources:
  - The Invariants (the six gates)
  - The Evaluation Boundaries (repair-location taxonomy A-F)
  - Decision and Change Procedure (errata / ADR graduation)
  - Incident and Change Management (DevHub change-record substrate)
governing_adrs:
  - DEC-ebf0b4 (D268 Session Discipline and Data Integrity Rules)
  - DEC-bc6be2 (D461 Canonical Reduction — the first metric whose onboarding seeded this book)
  - DEC-7d2f8c (D462 Derivation home — CC body 1-hop; cross-concept comparison at the metric boundary)
  - DEC-4a17e0 (D431 Observation field identity / O-to-C consistency)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Metric Onboarding Case Book

> Evidence note: This case book is preserved as a work record. It is not part of the primary Operations reader flow and should not be treated as current operating doctrine.

## Scope

This is a **living register of the gaps surfaced while onboarding metrics one at a time**. It exists because foundation corrections should be **evidence-driven, not speculative**: a single blocker is anecdote — you cannot tell a one-off implementation bug from a structural gap — but *N* blockers across *N* metrics form a dataset, and patterns in that dataset justify a foundation- or path-level correction at the right altitude, addressing a whole class instead of patching one symptom.

It is the living, systematic form of the "worked examples from recent sessions" table in the CLAUDE.md Foundation gate. Each case is keyed to the same governance the platform already uses — the **repair-location taxonomy A-F** (The Evaluation Boundaries) and the **six invariants** (The Invariants) — so the book is a *queryable* dataset, not just a readable log.

This chapter does not redefine the invariants, the boundary taxonomy, the change procedure (Decision and Change Procedure), or the DevHub change-record substrate (Incident and Change Management). It records cases and the patterns across them; foundation-class cases **graduate** to errata, path/impl cases to ADRs or fixes.

## How it works — the operating loop

Build a finance metric end-to-end. When it blocks:

1. **Classify** the case — repair-location (A-F), invariant(s) touched, and **class**: `foundation` | `path-critical` | `impl-bug` | `tooling`.
2. **Park or patch, by class** — *"move forward" never means "skip the fix":*
   - A **safe local unblock** exists (small, correct, in-scope) → apply it, log the case `patched`, finish the metric.
   - The block is **structural** with no safe local fix → **park the metric**, log the case `parked`, move to the next metric that is not blocked by the same gap.
3. **Log** the case here (light template below) + link its DevHub session, where the full detail already lives. Optionally open a DevHub task tagged `case-book` for each *open* case so it is on the work backlog.
4. **Synthesize** periodically (after ~every 5 metrics, or when a `pattern-tag` recurs) — cluster, then correct.

**This is a correction pipeline, not a junk drawer.** Every parked case carries a disposition, and foundation/path-critical cases carry a committed fix. "Log it and move on" must never become "defer it forever."

### Two graduation triggers

- **Foundation / path-critical** cases get an errata or ADR **immediately, even at N=1** — they are structural by inspection (e.g. an ontology gap, a multi-point gate inconsistency). They unblock a *class*, so they are usually `fix-now`, not `parked`.
- **Impl-bug** cases are patched locally and accumulate; when a `pattern-tag` recurs **≥3 times** they earn a holistic sweep (one ADR for the class) rather than N more band-aids.

## Case entry template

Keep it light — ~5 minutes, so logging never slows the metric work.

```
### CB-NNN — <short title>
- **Metric / driver:** <which metric we were building>
- **Session:** SES-xxxxxx (<date>) — full detail there
- **Where it blocked:** <exact gate / check / endpoint / error string>
- **Repair location:** <A-F> (consuming <A-F> grammar, if applicable)
- **Invariant(s):** <I-VI, or "grammar/contract">
- **Class:** foundation | path-critical | impl-bug | tooling
- **Local unblock vs real fix:** <the minimal local patch, if any> | <the structural correction>
- **Disposition:** parked | patched | fixed | adjudicated | open
- **Pattern-tag:** <kebab-tag to cluster related cases>
- **Graduates to:** <errata-xxx / ADR-xxx / commit / none-yet>
```

## Classification reference

**Repair locations (A-F)** — see The Evaluation Boundaries. A = source reality / admission; B = contract semantics / grammar; C = mapping / binding; D = evaluation-boundary implementation (readers, resolution service, metric engine, **gates**); E = storage / projection; F = read model / diagnostics.

**Invariants (I-VI)** — see The Invariants. I = meaning evaluated once at its boundary; II = object ordering fixed; III = state immutable; IV = references explicit; V = evaluation non-replayable; VI = evidence emitted, not inferred.

**Class** — `foundation` (an invariant/ontology gap), `path-critical` (a structural impl gap that blocks a *class* of metrics), `impl-bug` (a local defect), `tooling` (operational friction; logged in the appendix, kept out of the foundation dataset so it does not pollute pattern analysis).

**Disposition** — `parked` (metric set aside, gap unresolved), `patched` (safe local fix applied), `fixed` (structural correction landed), `adjudicated` (operator decision resolved it), `open` (awaiting work).

## Pattern register

| Pattern-tag | Cases | Status |
|---|---|---|
| `d431-multi-enforcement` | CB-001 | **fixed** (SES-d09b6d) — one shared observability resolver across all 3 enforcement points; **D462: 1-hop, not transitive** |
| `derived-canonical-ontology` | CB-002 | adjudicated → candidate errata |
| `derived-canonical-declaration-home` | CB-003 | **re-resolved (D462)** — CC body, **not** `canonical_mapping` (which is superseded) |
| `withdraw-frees-name` | CB-004 | patched |
| `source-slice-missing-derivation-inputs` | CB-005 | **resolved-by-design (D462)** — `due` = 1-hop CC field from observed `baseline`+`terms`; the subtraction moves to the metric DAG |
| `compute-library-date-add` | CB-006 | **reframed (D462)** — `date_add` needed as a **1-hop CC** compute for `due`; the 2-hop-at-canonical reading is withdrawn (metric DAG does the subtraction) |
| `conditional-aggregation-unlocks-ratios` | CB-010 | **resolved-by-expressibility (SES-469bf4)** — status AND date-comparison predicate ratios are authorable via `case/when` in the metric formula AST (NOT as filters); proven live (write_off_rate, on_time_payment_rate) |
| `cross-temporal-balance-over-period` | CB-007 | **RESOLVED-by-D467 (SES-bc6576/SES-06cef2, 2026-06-30)** — the secondary-metric DAG (DEC-0f3e57) is live; DSO + AR Turnover authored as governed divisions of live primary snapshots; **CEI now LIVE too** (SES-4c06b4) — the `prior_period_end` beginning-balance selection rule was added (migration 22) + PE-MC-14 alignment, and CEI (8b57d7f0, 4 inputs incl. prior_period_end) is active. Whole sub-class done. |
| `customer-reference-axis` | CB-008 | **RESOLVED-by-D468/D469/D471 (SES-7581df verification, 2026-07-02)** — reference-stamping + reference-dimension grouping + cross-entity grain alignment shipped; 4 customer-axis metrics active and 3 of 4 producing snapshots on pilot1 (per_customer_credit_limit_utilization awaits the customer-master CO runtime read) |
| `source-bcf-not-observed` | CB-009, CB-014 | **blocked, quantified (SES-7581df)** — AR-scope study: ~64 of 152 AR seeds need unobserved concepts; a 9-seed subset re-classed **widening-authorable** (raw BSAD/KURGV columns exist, OC just doesn't observe them; pilot1 SDG emits NULLs). **AP scope added (SES-c1d359, 2026-07-02):** ~55–60 of 129 AP seeds in the same class; a widening-authorable subset (payment method ZLSCH, payment block ZLSPR, discount terms ZBD1P/ZBD2T/SKNTO) exists on BSAK/BSIK |
| `nested-secondary-composition` | CB-012 | **parked** — per-customer ratios / utilization series / roll rates need secondary-DAG inputs that are themselves grouped or secondary snapshots; unproven capability |
| `mixed-document-kind-population` | CB-013, CB-016 | **open (2026-07-02)** — arpi_slice holds DR invoices + DZ payments; wave-1 flow metrics sum both (gross_invoiced 19.0M vs DR-true 8.3M; DSO ~half true value); as_of family clean; remediation needs M15 supersession. **Payable-side twin identified at authoring time (CB-016, SES-c1d359):** BSAK carries vendor payments/credit memos alongside invoices — same exposure for the AP flow family, no tenant data resolved yet |
| `cross-document-match-family` | CB-015 | **parked (SES-c1d359, 2026-07-02)** — 3-way match / GR-IR / no-PO-rate AP metrics need the purchasing-document chain (EKPO/EKBE/MSEG + RSEG line grain) and cross-document references; not expressible on the header slice |
| `two-population-ratio-needs-dag` | CB-011 | **RESOLVED-by-D467 (SES-06cef2, 2026-06-30)** — the secondary-metric DAG is live; past_due_ar_percentage, overdue_invoice_ratio, collection_effectiveness_ratio + the aging-concentration / composition family authored as governed divisions of two distinct live as_of/period snapshots. 17 secondary metrics active total. |
| `rowset-join-empty-grain-keys` | CB-017 | **patched + wave-1 re-run DONE (SES-eaab9d, 2026-07-02; commit pending)** — the engine joins rowset pairs by grain_keys, but the governed path stamped partition keys ({} for ungrouped metrics) so ALL multi-variable joins collapsed onto one arbitrary row; fixed by stamping the CO reference per row in buildSectionA. Corrected wave-1 values (all hand-verified): on_time_payment_rate 100→81.081081, late_payment_frequency 0→18.918919, average_days_delinquent null→8.380952, average_days_to_collect 14.297→−0.297297 (honest early-payment mean) |
| `composite-selection-rule-not-honored` | CB-018 | **patched (SES-eaab9d, 2026-07-02; commit pending)** — the composite resolver ignored snapshot_selection_rule semantics: as_of_period_end read the globally-latest snapshot (any period) and prior_period_end fell through to current-period matching; fixed with exact-period scoping + a prior-period label resolver (fail-closed); ar_growth_rate flipped from +1.0038 (inverted) to the hand-exact −0.993804; DSO/turnover regression-clean, CEI now reads a true prior-period begin balance |

---

## Cases

### CB-001 — D431 O-to-C is enforced at multiple points; only one was made transitive
- **Metric / driver:** Average Days to Collect (the first derived-canonical-field metric; D461).
- **Session:** SES-61d08f (2026-06-27/28) — checkpoints #1-#7; DBCP `d461-canonical-reduction-derived-field-dbcp` §0.
- **Where it blocked:** CC-version creation refused `403 D431 O↔C: business_concept 850f69d4 … not declared observable … (canonical-v2 authoring); refused (DEC-4a17e0)` at `contract.service.ts:395` (`ObservationConceptResolverService.assertConceptsObservableFromSource`).
- **Repair location:** D (the D431 enforcement checks) consuming the B grammar (the `canonical_mapping` compute resolution that declares the derivation).
- **Invariant(s):** IV (references explicit), VI (evidence emitted, not inferred) — the chain must *prove* every CO concept is producible.
- **Class:** path-critical — it blocks the entire **class** of derived-canonical-field metrics, not just this one.
- **Local unblock vs real fix:** no safe local unblock. Real fix: extend the transitive-observability treatment (a derived concept is producible iff its compute inputs are observable) to **all** D431 enforcement points — CC-authoring `assertConceptsObservableFromSource` and the OC/CC activation path (`transitionState`) — reusing `isConceptObservable` from `mcf-chain-resolution.ts`. The PE-MC-11 gate (`buildOcNode`) was already made transitive (CS-3, SES-61d08f).
- **Disposition:** open → **fix-now** (SES-d09b6d).
- **Pattern-tag:** `d431-multi-enforcement`.
- **Graduates to:** the D461 commit (CS-3 gate + this extension) + a note in DEC-4a17e0/D431 that O↔C enforcement points must share one resolver.
- **2026-06-28 (D462) update:** CB-001's *lesson* stands (the enforcement points must share **one** resolver, or they drift). What the shared resolver *says* is corrected: **1-hop, not transitive.** The Foundation re-read (Invariant II "no hidden derivation"; CC resolves "across Source Objects") forbids an intra-CO derivation chain — a derived field's compute inputs must be **directly** observed, never themselves derived. The earlier transitive recursion + cycle guard were too permissive (they admitted exactly the chain the anti-pipeline model forbids). `isConceptObservable` is tightened to 1-hop; multi-hop composition lives at the **metric** boundary (secondary-metric DAG). See DEC-7d2f8c.

### CB-002 — Is a computed-at-canonical value a base concept or a metric-layer construct?
- **Metric / driver:** Average Days to Collect (D461).
- **Session:** SES-61d08f — authentic B6 panel run `d7500d06` surfaced it (Maker: derived/metric-layer; Checker: base single-instance duration).
- **Where it blocked:** the panel split + routed to `OPERATOR_REVIEW`; the registry had no clean slot for a "derived canonical concept" (BCF governs observables, MCF governs computed metrics).
- **Repair location:** B (concept semantics / the BCR ontology).
- **Invariant(s):** I (meaning evaluated once, at its boundary).
- **Class:** foundation.
- **Local unblock vs real fix:** operator adjudication. Resolution: **`collection_lag` is a BASE concept whose PRODUCTION is source-dependent** — directly *observed* where a source emits it, *canonically computed* where the source emits only the inputs. The registry describes a concept's *meaning* (base), not its *production*; the source-agnostic Canonical Object lets the metric bind one concept and never learn the path. This validates D461 + CS-3 (a concept is provable if observable **or** derivable).
- **Disposition:** adjudicated.
- **Pattern-tag:** `derived-canonical-ontology`.
- **Graduates to:** candidate errata — "base concept, source-dependent production" as the canonical reading for computed-at-canonical base-grain values (extends the base-vs-derived grain test).

### CB-003 — Where does a derived-canonical-field declaration live, post-BCR?
- **Metric / driver:** Average Days to Collect (D461).
- **Session:** SES-61d08f — research phase; DBCP §1-§4.
- **Where it blocked:** D330's `compute_json` lived on `cc_field_mapping`, physically retired (D417/D418); the post-BCR `canonical-v2` grammar has no derivation key; `canonical_mapping` is empty/vestigial for MCF slices.
- **Repair location:** B (grammar) + C (declaration home).
- **Invariant(s):** grammar/contract.
- **Class:** design.
- **Local unblock vs real fix:** resolved by D461 L2 — declare the derivation as a `compute` field-resolution on the surviving platform-scoped `canonical_mapping` (no CC-body grammar bump; re-homes D330's mechanism). The compute-evaluator module survived and is reused.
- **Disposition:** resolved (operator-locked) → **re-resolved (D462)**.
- **Pattern-tag:** `derived-canonical-declaration-home`.
- **Graduates to:** the D461 DBCP / ADR.
- **2026-06-28 (D462) update:** L2's answer (`canonical_mapping` `compute` resolution) was **wrong** — `canonical_mapping` is **superseded** (DEC-02f5a9); field-resolution "survives within the Observation and Canonical Contract bodies." The correct home is the **Canonical Contract body** (a `compute` resolution element in `resolution_rules`/`field_selection`), authored through the existing `POST /api/contracts/:id/versions` envelope path — which also dissolves the "no governed write path for `canonical_mapping`" friction (there is no `canonical_mapping` to write). The OC may **not** host it (the grammar forbids an OC declaring canonical evaluation logic; Invariant I). See DEC-7d2f8c.

### CB-004 — A withdrawn characteristic permanently blocks its own term
- **Metric / driver:** Average Days to Collect (D461) — surfaced while re-authoring vocabulary panel-clean.
- **Session:** SES-61d08f — checkpoint #6; fix proven live.
- **Where it blocked:** re-authoring `collection lag` returned `409 F3 name conflict` even though the prior characteristic was withdrawn. `withdrawCharacteristic` sets `archived_at` but leaves `lifecycle_state='active'`, and `name-conflict.checker.ts assertCharacteristicTermAvailable` matched the term with **no `archived_at` filter**.
- **Repair location:** F (the name-conflict checker / diagnostics).
- **Invariant(s):** III (immutable/archival semantics — an archived row is not part of the live name-space).
- **Class:** impl-bug.
- **Local unblock vs real fix:** local fix applied — added `isNull(characteristic.archivedAt)` to the term query; a withdrawn term ("admitted in error", DEC-1fbaf1) is now reusable, matching the characteristic table's own "live" partial-index predicate. 15/15 spec green; proven by the live re-author succeeding.
- **Disposition:** patched (commit with D461).
- **Pattern-tag:** `withdraw-frees-name`.
- **Graduates to:** the D461 commit. Watch for siblings (alias name-space; entity name-space) with the same missing-`archived_at`-filter shape — if ≥3, sweep them together.

### CB-005 — A source slice does not model the inputs a derivation needs
- **Metric / driver:** Average Days to Collect (D461) — **parked** here.
- **Session:** SES-d09b6d (2026-06-28).
- **Where it blocked:** building the BSAD slice for `collection_lag` (= clearing − due), the BSAD OC `so_schema` models `AUGDT` (clearing), `BLDAT` (document date), `BUDAT` (posting date) — but **no due-date input**. SAP BSAD has no stored due date; it is `baseline date (ZFBDT) + payment terms (ZBD1T net days / ZTERM)`. The source contract `sc__ecc__bsad` *does* carry all 182 fields incl. `ZFBDT` / `ZBD1T` / `ZTERM`; the OC simply did not select them.
- **Repair location:** A (source observability — what the OC slice admits) → B (new concepts).
- **Invariant(s):** IV (references explicit — a derivation's inputs must be observable).
- **Class:** design / onboarding (patchable; not a structural gap).
- **Local unblock vs real fix:** patchable — author `baseline date` + `net due days` (payment-terms-days) concepts (panel-backed, per CB-002's base-concept reading), widen the BSAD OC to observe `ZFBDT → baseline` and `ZBD1T → net-due-days`. Then the due date becomes derivable.
- **Disposition:** parked (operator chose to prove CB-001 on a clean 1-hop metric first) → **resolved-by-design (D462)**.
- **Pattern-tag:** `source-slice-missing-derivation-inputs`.
- **Graduates to:** the Avg-Days-to-Collect build when resumed.
- **2026-06-28 (D462) update:** the path is now clean and Foundation-legal. Widen the BSAD OC to observe `ZFBDT → baseline` and `ZBD1T → net-due-days` (field selection — the OC's proper job). The **CC** then derives `due = date_add(baseline, terms)` as a **1-hop** canonical field (both inputs directly observed). The `clearing − due` subtraction (where `due` is derived) is **not** a canonical field — it is a **metric** op (secondary-metric DAG). No source compensation, no observation-boundary derivation. See DEC-7d2f8c.

### CB-006 — The compute library lacks `date_add` for a multi-hop date derivation
- **Metric / driver:** Average Days to Collect (D461) — **parked** here.
- **Session:** SES-d09b6d (2026-06-28).
- **Where it blocked:** for BSAD, `due_date = baseline + terms` (a computed date), so `collection_lag = clearing − (baseline + terms)` is a **2-hop** derivation. Computing the due date needs `date_add(start_date, N_days) → date`. The compute-evaluator library has `date_diff` / `date_diff_as_of` / `row_count` / `sum_where` — but **no `date_add`**.
- **Repair location:** B (compute grammar / library) + D (the evaluator).
- **Invariant(s):** I (meaning evaluated once, at the canonical boundary).
- **Class:** path-critical — `date_add` unblocks a **class**: any metric whose derivation adds days to a date (due dates, SLA deadlines, as-of windows).
- **Local unblock vs real fix:** add `date_add` to `compute-evaluator.ts` (small, additive, mirrors `date_diff`) + its validator entry + an additive ADR (D330 library extension, ADR-gated per D330-R3).
- **Disposition:** parked (batched with CB-005) → **reframed (D462)**.
- **Pattern-tag:** `compute-library-date-add`.
- **Graduates to:** an additive ADR + the Avg-Days build.
- **2026-06-28 (D462) update:** the framing "`collection_lag ← due ← {baseline, terms}` is a 2-hop derivation the transitive gate handles" is **withdrawn** — a 2-hop chain at the canonical boundary is forbidden (Invariant II; 1-hop only). `date_add` is still needed, but as a **1-hop CC** compute producing `due` from observed `baseline`+`terms` (one hop). The *second* hop — `clearing − due` — is a **metric** op (secondary-metric DAG), not a canonical compute. So `date_add` lands as a single-hop canonical function; the chain never exists at the canonical boundary. See DEC-7d2f8c.

### CB-007 — Cross-temporal AR ratios need average-balance-over-period
- **Metric / driver:** DSO / days_sales_outstanding, receivables/accounts_receivable_turnover, collection_effectiveness_index, average_collection_period, cash_conversion, days_in_accounts_receivable (~10 AR seed metrics).
- **Session:** SES-469bf4 (2026-06-29) — autonomous AR coverage batch triage.
- **Where it blocked:** formula needs `(Average Accounts Receivable / Net Credit Sales) × Days` — an **average balance over a period** (or a beginning/ending two-point) divided by a flow over the same period. The single-metric AST + the `as_of` gate produce a **point-in-time** balance at P, not an average-over-period; and the metric boundary has no secondary-metric DAG to combine a balance metric with a flow metric across the period.
- **Repair location:** B (grammar — a trailing-window/average-balance temporal shape, or a secondary-metric DAG) + D (evaluator).
- **Invariant(s):** I (meaning produced once at its boundary) — the cross-temporal combination has no single boundary today.
- **Class:** path-critical — blocks a **class** (~10 high-value AR metrics: DSO, turnover, CEI, collection period).
- **Local unblock vs real fix:** no safe local fix. Real fix = the secondary-metric / cross-temporal design (DEC-483f1e step-4 snapshot-population secondary metric) — combine the live as_of balance metrics + period flow metrics into a governed ratio.
- **Disposition:** **RESOLVED-by-D467** (2026-06-30). The secondary-metric DAG ADR this case graduated to was built + shipped (DEC-0f3e57/D467, the metric_input role-kind reading upstream Metric Snapshots via governed selection). **days_sales_outstanding** (db373d5b) + **accounts_receivable_turnover** (069a188d) are live — governed divisions of `as_of_period_end` balance ÷ `period_matched` flow. **CEI now LIVE** (SES-4c06b4) — the `prior_period_end` selection rule was added (additive enum extension, migration 22 + PE-MC-14 alignment + harness RULE_GATE), and collection_effectiveness_index (8b57d7f0) is active: ((Begin AR@prior_period_end + Sales − End Total AR) / (Begin AR + Sales − (End Total AR − Overdue))) × 100, verifier=96, PE-MC 15/15. Only average_collection_period is intentionally skipped (DSO with a 365-day constant — near-duplicate). **Sub-class fully resolved.**
- **Pattern-tag:** `cross-temporal-balance-over-period`.
- **Graduates to:** the secondary-metric DAG ADR (DEC-0f3e57/D467) — **shipped + live**.

### CB-008 — Customer-axis AR ratios need a Customer reference edge
- **Metric / driver:** top_10_customer_ar_concentration, accounts_receivable_concentration_risk, customer_credit_limit_utilization, credit_line_utilization_by_customer, customer_payment_performance_score, cross_aging_percentage (~17 AR seed metrics).
- **Session:** SES-469bf4 (2026-06-29).
- **Where it blocked:** the formula groups or ranks by **customer** (or needs a customer credit limit), but the Customer Invoice grain carries no governed reference to a Customer entity. BCF has no active Customer entity nor an invoice→customer reference business_concept (the finance-ar-gap-matrix Wave-1 Customer entity is draft, not active; the bill-to reference is `needs_operator_review`).
- **Repair location:** B (concept — a Customer entity + reference BC) + C (binding).
- **Invariant(s):** IV (references explicit) — a customer-axis metric must bind an explicit customer reference.
- **Class:** path-critical — blocks the entire customer-axis cohort (~17).
- **Local unblock vs real fix:** real fix = activate the Customer entity + author the invoice→customer reference edge (D427 reference layer; operator-deferred).
- **Disposition:** parked → **re-resolved (2026-06-30)**: the substrate gap is closed; the real blocker is deeper (see update).
- **Pattern-tag:** `customer-reference-axis`.
- **Graduates to:** an MCF reference-dimension / cross-entity metric-grammar ADR (NOT the D427 reference DBCP — that part is done).
- **2026-06-30 (SES-469bf4) update:** the assumed blocker was **wrong**. The **Customer entity is already active** (`705f47e1`) with credit limit + customer account identifier + payment terms, and the **Customer Invoice → Customer reference edge was authored this session** (`56a5f975`, identity_bearing, role=customer, active). So the *substrate* is complete. But the customer-axis metrics **still cannot be authored**, because the metric engine has **no reference-dimension / cross-entity capability**: verified live — `metric_computed_dimension_ref` = 0 rows, **0** metric variable bindings to reference-kind concepts, all 28 metrics on the single Customer Invoice grain, only `role_kind_code='input'`. The class needs **group-by-reference** (rank/aggregate invoices by customer) and/or **cross-entity** binding (invoice AR ÷ the customer's credit limit on a different entity) — neither exists. **Repair location corrected to B (metric grammar: a reference/group dimension + cross-entity binding) + D (evaluator)**, not A/C. The reference edge is correct groundwork that the future capability will consume.
- **2026-07-02 (SES-7581df) update — RESOLVED.** The missing capability was built as the CB-008 A/B/C component arc: **D468** (DEC-7f2e73, reference-stamping — `bill_to_customer` is stamped on the CO, live in `co_customer_invoice_arpi_slice_v9_4_0`), **D469** (DEC-2c2849, reference-dimension grouping + top-N rank spec), **D471** (DEC-2f0967, cross-entity governed selection via PE-MC-2/11 grain alignment). Runtime resolution landed on `feat/tenant-views-mcf-bridge` (grouping-dimension resolution, commit `986347db`; grain-alignment fail-closed gate, commit `040613da`). Verified live on pilot1 this session: `per_customer_overdue_amount_0_30` (12 snapshot rows), `top5_customers_by_gross_invoiced_amount` (10), `top_10_customer_ar_concentration` (20) — grouped metrics author AND produce. Residual: `per_customer_credit_limit_utilization` is authored+active but has no snapshot yet — the cross-entity **runtime read of the customer-master CO** is the remaining piece (customer-master COs are not produced on pilot1; deferred to the SDG/customer-chain runtime phase). Compositions that require grouped or secondary snapshots as *inputs* to further secondary metrics are split out as **CB-012**.

### CB-009 — Many AR metrics need source concepts not observed on the invoice slice
- **Metric / driver:** electronic/automated/self-service invoice rates, payment_method_diversity, collection_call_effectiveness + collection-activity counts, credit_application/credit_hold/credit_review metrics, dispute_resolution_time, unbilled_revenue/revenue_leakage, credit-vs-cash-sales splits, early_payment_discount_utilization (~23 AR seed metrics).
- **Session:** SES-469bf4 (2026-06-29).
- **Where it blocked:** the formula needs a concept the Customer Invoice slice does not observe — e.g. a delivery-channel code, payment-method code, collection-activity event, credit-application entity, dispute-start date, unbilled-revenue, or a credit-vs-cash sale-type flag. `document_type_code` exists but is `semanticRole=diagnostic` with no canonical value set, so it cannot discriminate credit notes as a filter (PE-MC-12).
- **Repair location:** A (source observability — widen the OC, or new source) + B (new concepts).
- **Invariant(s):** IV (references explicit) — the input must be observable.
- **Class:** design / onboarding (each is patchable by observing the concept; not a single structural gap).
- **Local unblock vs real fix:** author the missing value/reference BCs + widen the OC where the source emits them; some need new entities (Payment, Collection Activity) or are genuinely not in the source.
- **Disposition:** parked (per-concept onboarding; not in the current invoice-slice scope).
- **Pattern-tag:** `source-bcf-not-observed`.
- **Graduates to:** per-concept BCF/OC onboarding (finance-ar-gap-matrix Batch 2/3).
- **2026-07-02 (SES-7581df) update — quantified + widening subset split out.** Full AR-scope seed study (152 seeds: finance/accounts_receivable 94 + credit_and_collections 35 + billing 23) puts this class at **~64 seeds** — collections-workflow events (~14), cost/staff/ROI (~14), e-invoicing/channel/error flags (~12), credit-application/review workflow (~6), SD-module concepts (unbilled/leakage/time-to-bill/O2C, ~5), GL provisions (~3), surveys (2), recovery/refinance (3), cohort-retention (3), PoD (1), intercompany (1). Within the original CB-009 list a **9-seed subset is re-classed widening-authorable, NOT blocked**: the raw source columns already land in `fact.so_bsad_v1_0_0` / `fact.so_kurgv_v1_0_0` but no OC observes them — cash-discount terms/taken (`zbd1p`/`zbd2p`/`sknto`/`wskto` → early_payment_discount_utilization), payment method (`zlsch` → payment_method_diversity), customer credit-risk category (KURGV `ctlpc` → high_risk_customer_ar_exposure), credit-memo/reversal document types (`blart` DG / `xstov` → credit_note_volume, credit_note_issuance_rate, reversal_credit_note_ratio, invoice_adjustment_ratio), dunning level/date (`manst`/`madat`/`mansp` → ar_without_recent_follow_up, proactive_collection_actions). Repair location for the subset: B (author the value BCs) + A (widen the BSAD/KURGV OCs — field selection, the OC's proper job, per the CB-005 precedent). Data caveat (verified live): pilot1 SDG emits NULL/empty for all these columns and only BLART ∈ {DR, DZ} exists — so the subset is authorable to **chain-complete** but runtime proof waits on SDG emitting the fields (A-layer generator realism, a legitimate SDG-phase task — not metric-driven calibration).

### CB-010 — Status + temporal-predicate ratios are expressible via conditional aggregation (NOT blocked)
- **Metric / driver:** write_off_rate, on_time_payment_rate (proven live); the class also covers payment_term_compliance_rate, late_payment_frequency, percentage_of_past_due_invoices, status proportions, and amount-weighted status ratios.
- **Session:** SES-469bf4 (2026-06-29) — autonomous AR coverage batch.
- **Where it surfaced:** the initial triage parked these as "blocked by PE-MC-12" (a late/on-time/past-due predicate cannot be a **filter** — filters bind status/dimension roles only, never temporal/diagnostic). But the metric **formula AST** supports `case/when/comparison` (the live Invoice Dispute Rate uses `avg(case when status==in-dispute then 1 else 0)`), and the comparison accepts **two variable_refs with `lte`/`gt`** — so the predicate lives in the formula, not a filter. Proven live: `write_off_rate` = `100 × sum(case when status='written-off' then gross)/sum(gross)` (28f088aa); `on_time_payment_rate` = `100 × avg(case when clearing ≤ due then 1 else 0)` over paid (a6ef3cc0). Both verifier_verdict=pass, PE-MC 11/12.
- **Repair location:** none — F (read of the grammar) corrected; the expressibility already existed.
- **Invariant(s):** none violated — the predicate is produced once in the formula at the metric boundary (Invariant I), not pushed to a filter or a lower layer.
- **Class:** tooling / doctrine (a triage misconception, not a platform gap).
- **Local unblock vs real fix:** none needed — use conditional aggregation in the formula. The status-ratio + temporal-predicate-ratio classes are an open authorable backlog, not blocked.
- **Disposition:** resolved (by expressibility).
- **Pattern-tag:** `conditional-aggregation-unlocks-ratios`.
- **Graduates to:** a doctrine note — "temporal/derived predicates that cannot be filters (PE-MC-12) are expressible as `case/when` conditional aggregation in the metric formula; the denominator stays the full population."

### CB-011 — Two-population (same-time, different-population) ratios need a secondary-metric DAG
- **Metric / driver:** overdue_ar / past_due_balance_percentage (overdue amount / total AR balance), collection_efficiency (collected / receivables), percentage_of_current_ar, percentage_of_past_due_invoices (~several AR seed metrics).
- **Session:** SES-469bf4 (2026-06-29) — autonomous AR coverage batch.
- **Where it blocked:** unlike CB-010 (one population, predicate in `case/when`), these divide **two distinct populations resolved by different temporal gates** — e.g. overdue% = `as_of(anchor=due)` overdue amount ÷ `as_of(anchor=document)` total AR balance. A single metric has **one** grain + temporal gate + selection, so it cannot resolve two different as_of selections; conditional aggregation can't express it either (the denominator population differs from the numerator's, not just a predicate over the same rows).
- **Repair location:** B (grammar — a secondary-metric DAG that composes two published metrics into a governed ratio) + D (evaluator).
- **Invariant(s):** I (each population's meaning is produced once at its own boundary; the ratio composes them) — no single boundary exists today.
- **Class:** path-critical — blocks a small but high-value cluster (overdue%, collection efficiency, current-AR%).
- **Local unblock vs real fix:** no safe local fix; real fix = the secondary-metric DAG (same DEC-483f1e step-4 design as CB-007). The two component metrics already exist live (Overdue Invoice Amount, AR Balance) — the DAG just needs to divide them.
- **Disposition:** **RESOLVED-by-D467** (2026-06-30). The secondary-metric DAG is live (DEC-0f3e57/D467); the two-population ratios are governed divisions of two distinct live snapshots selected by different rules. Live: **past_due_ar_percentage** (94616611 = overdue_invoice_amount ÷ ar_balance ×100), **overdue_invoice_ratio** (count), **collection_effectiveness_ratio**, **ar_current_percentage**, **within_terms_invoice_percentage**, the aging-concentration family (0-30/31-60/61-90/90+), and the overdue-composition family — 17 secondary metrics active total.
- **Pattern-tag:** `two-population-ratio-needs-dag`.
- **Graduates to:** the secondary-metric DAG ADR (DEC-0f3e57/D467) — **shipped + live**.

### CB-012 — Compositions over grouped or secondary snapshots (nested-secondary) are unproven
- **Metric / driver:** cross_aging_percentage (per-customer past-due ÷ per-customer total AR), credit_line_incremental_utilization (utilization at P vs P−1, where utilization is itself a cross-entity secondary), roll_rate_analysis_of_delinquencies (aging bucket at P ÷ prior bucket at P−1) — 3 AR seed metrics.
- **Session:** SES-7581df (2026-07-02) — AR seed-pool expansion study.
- **Where it blocked:** not yet attempted; classified at study time. D467's secondary-metric DAG reads **primary** metric snapshots via versioned selection rules (`as_of_period_end`, `period_matched`, `prior_period_end`). These three need inputs that are themselves **grouped** snapshots (one row per customer per period, D469) or **secondary** snapshots (utilization) — i.e. secondary-over-grouped and secondary-over-secondary composition. Whether the DAG's governed selection + snapshot identity (`snapshotKeyColumns = [fiscal_period, …groupingDimensions]`) supports a partitioned input, and whether a secondary metric may cite another secondary as input, is undeclared in DEC-0f3e57.
- **Repair location:** B (secondary-metric grammar — declare input-eligibility: primary-only vs any published snapshot; partition-aware selection) + D (evaluator) if a gap is confirmed; possibly resolves by expressibility like CB-010.
- **Invariant(s):** I (each composition level's meaning produced once at its own boundary), IV (the input snapshot reference must be explicit, including its partition key).
- **Class:** path-critical if confirmed (blocks the per-customer-ratio + trend/roll-rate cluster); may be a triage misconception — probe with ONE metric (one-then-many, D268) before concluding.
- **Local unblock vs real fix:** none attempted. Probe: author cross_aging_percentage via the panel and observe which PE-MC gate or evaluator step rejects; graduate to a grammar note or an additive ADR accordingly.
- **Disposition:** parked (study-time classification; no live attempt yet).
- **Pattern-tag:** `nested-secondary-composition`.
- **Graduates to:** none-yet.

### CB-013 — Mixed document kinds in the Customer Invoice slice contaminate the period-flow metric family
- **Metric / driver:** wave-2 `cleared_customer_payment_amount` (DZ payment-side) — surfaced while hand-computing its target value (R5 verify-payload discipline) during the TSK-8ab894 run.
- **Session:** SES-eaab9d (2026-07-02).
- **Where it blocked:** not a gate — a live-value audit. `fact.co_customer_invoice_arpi_slice_v9_4_0` holds **761 DR (invoice) + 955 DZ (payment)** documents as Customer Invoice COs. No wave-1 metric discriminates document kind: `document type code` (f10afed1) is `semantic_role=diagnostic` → PE-MC-12 forbids filtering on it, and no formula used case/when. Verified: `ms_gross_invoiced_amount` FY2025-26/P06 = 19,019,959.32 = DR 8,301,329.27 + **DZ 10,718,630.05** — "gross invoiced" includes customer payments. Published DSO 48.77d ≈ half the DR-true ~111.7d. **The as_of/open-item family is clean** (all 62 open items at 2025-09-30 are DR; ar_balance 10,306,696.90 exact) because DZ items are all cleared in this data — a data coincidence, not a guarantee.
- **Repair location:** B (MC population semantics — flow metrics on this slice must declare document-kind discrimination, CB-010 case/when pattern) with two open B/A questions: (1) should `document type code`'s semantic role be re-adjudicated diagnostic→dimension (BCF governance, would legalize filters); (2) should DZ documents resolve as *Customer Invoice* COs at all, or does the model want a Customer Payment entity/slice (A+B, larger).
- **Invariant(s):** I (meaning produced once — "gross invoiced amount" cannot mean invoices+payments; the declared name and the resolved population disagree).
- **Class:** path-critical — contaminates the flow-family metrics (gross_invoiced_amount, cleared_invoice_amount, billing_volume, paid_* amounts/counts, average_revenue_per_invoice, average_paid_invoice_amount, …) and every composite binding them (DSO, turnover, CEI, ratios). Exact affected list to be enumerated in the remediation task.
- **Local unblock vs real fix:** wave-2 metrics are authored correct-by-construction (case/when on document type; `net_payment_term_days > 0` for credit sales — empirically DR-only). Real fix = re-mint the affected wave-1 MCVs with discrimination — **blocked on the M15 supersession path** (next governed MCF gate; not yet generalized). No hand-edits, no silent re-pointing.
- **Disposition:** open (operator decision needed on remediation scope + the two B/A questions).
- **Pattern-tag:** `mixed-document-kind-population`.
- **Graduates to:** none-yet (remediation task filed; candidate ADR once M15 lands).

### CB-014 — AP seed classes not observed on the Supplier Invoice slice (payable-side CB-009)
- **Metric / driver:** ~55–60 of the 129 `mcf.seed_metric` accounts_payable candidates — e-invoicing/OCR/EDI channel rates, approval-workflow cycle times, T&E family, AP staff/FTE/cost metrics, `ML_MODEL(...)` predictors, vendor-survey scores, fraud/duplicate detection.
- **Session:** SES-c1d359 (2026-07-02) — AP onboarding study + wave W0–W2 execution; full triage in the session checkpoints.
- **Where it blocked:** study-time classification (not attempted). The concepts these metrics bind (submission channel, approval events, expense reports, department cost, model outputs, survey responses) are not observed on any Supplier Invoice observation slice and mostly have no SAP-table carrier in the registered source catalog at all.
- **Repair location:** A (source expansion — new sources/tables) + B (new BCF concepts) per sub-family; a **widening-authorable subset** exists exactly like CB-009's: payment method (BSIK/BSAK `ZLSCH`), payment block / hold reasons (`ZLSPR`), discount terms (`ZBD1P`, `ZBD2T`, `SKNTO`) are raw columns on the already-registered vendor secondary indexes — OC widening + BC authoring unlocks the payment-method-mix, hold-mix and early-payment-discount families without new sources.
- **Invariant(s):** none violated — the concepts simply are not observed (grammar/contract coverage gap).
- **Class:** path-critical for the affected families; not a platform gap.
- **Local unblock vs real fix:** none | per-family source/BCF onboarding; start with the widening-authorable subset (checker-first preflight per concept).
- **Disposition:** parked.
- **Pattern-tag:** `source-bcf-not-observed`.
- **Graduates to:** none-yet.

### CB-015 — AP match-family metrics need the purchasing-document chain
- **Metric / driver:** 3_way_match_exception_rate, gr_ir_imbalance, no_po_invoice_rate, percentage_of_invoices_linked_to_pos, percentage_of_invoice_line_items_matched_with_a_purchase_order, po_and_invoice_reconciliation_rate (+ the ~10 line-item approval-method percentages) — the AP match family in the seed pool.
- **Session:** SES-c1d359 (2026-07-02) — AP onboarding study.
- **Where it blocked:** study-time classification (not attempted). Match semantics live across documents: invoice line ↔ purchase order line (RSEG `EBELN`/`EBELP`), goods receipt (MSEG/EKBE), GR/IR clearing. The active AP chain observes the Supplier Invoice **header** (BSAK accounting view + RBKP receipt view); there is no Supplier Invoice Line observation slice, no PO/GR observation slices, and no cross-document reference edges (Supplier Invoice Line → Purchase Order Line, → Goods Receipt) in BCF beyond the line→header reference.
- **Repair location:** A (register/observe EKPO/EKBE/MSEG; RSEG SC is already active) + B (Supplier Invoice Line/PO Line/GR concepts + reference edges) + C (line-grain OC/CC slices). The Supplier Invoice Line and Purchase Order Line entities already exist in BCF with identity — the entity layer is ready; the observation/canonical chain is not.
- **Invariant(s):** IV (the match is a set of explicit cross-document references — must be declared, never inferred at read time).
- **Class:** path-critical (blocks the whole match/automation family — high-value AP-operations metrics).
- **Local unblock vs real fix:** none safe | line-grain chain build (new OC/CC family at Supplier Invoice Line grain + PO/GR slices + reference stamping), then the family authors via existing conditional-aggregation and grouping capabilities.
- **Disposition:** parked.
- **Pattern-tag:** `cross-document-match-family`.
- **Graduates to:** none-yet (candidate umbrella task when the AP line-grain wave is scheduled).

### CB-016 — Mixed vendor document kinds in the Supplier Invoice slice (payable-side CB-013)
- **Metric / driver:** the AP W1 period-flow family authored 2026-07-02 — gross_payables_invoiced_amount, supplier_invoice_volume, paid_supplier_invoice_amount (and every W2 composite binding them: days_payable_outstanding, accounts_payable_turnover).
- **Session:** SES-c1d359 (2026-07-02) — identified **at authoring time** from CB-013's evidence, before any tenant data exists for the AP slice.
- **Where it blocked:** not a gate — a by-construction exposure. BSAK/BSIK (`Accounting: Secondary Index for Vendors`) carry **all** vendor accounting documents: invoices (KR/RE), vendor payments (KZ/ZP), credit memos (KG). The AP OC/CC do not discriminate document kind; `document type code` (aac341c6) is observed but — mirroring the AR twin — will be filter-illegal if its semantic role is adjudicated diagnostic (PE-MC-12). When a tenant resolves BSAK into Supplier Invoice COs, the flow metrics will sum payments and credit memos into "invoiced" amounts exactly as CB-013 measured on the AR side (DZ contamination ≈ 56% of the AR period flow). The as_of family is structurally safer (mirrors AR) but that is a data coincidence, not a guarantee — a KZ payment open at P would count into ap_balance.
- **Repair location:** B (population semantics: flow metrics must declare document-kind discrimination via case/when per CB-010, or `document type code` must be re-adjudicated diagnostic→dimension to legalize filters) with the same open A/B question as CB-013: should vendor payments resolve as Supplier Invoice COs at all, or does the model want a Vendor Payment slice (the BCF Vendor Payment entity already exists with identity).
- **Invariant(s):** I (declared meaning "supplier invoices" vs resolved population "all vendor documents").
- **Class:** path-critical (same class as CB-013; the two sides should be remediated by the same M15-supersession wave and the same document-kind adjudication).
- **Local unblock vs real fix:** future AP metrics author discrimination in-formula from birth (CB-010 case/when) | joint AR+AP remediation once M15 supersession is generalized; single operator adjudication of `document type code` semantics covers both sides.
- **Disposition:** open (deliberately pre-logged so the AP side is not "discovered" again at runtime-data time).
- **Pattern-tag:** `mixed-document-kind-population`.
- **Graduates to:** none-yet (joins CB-013's remediation).

### CB-017 — Engine rowset joins collapse when Section-A rows carry no identity (empty grain_keys)
- **Metric / driver:** `cleared_customer_payment_amount` (wave-2 TSK-8ab894 metric #1) — the first case/when metric evaluated over a genuinely discriminating population.
- **Session:** SES-eaab9d (2026-07-02).
- **Where it blocked:** not a gate — R5 payload verification. First governed evaluation returned **5,371,852.77** against the hand-computed **10,718,630.05** (SUM of gross over the 61 DZ documents in FY2025-26/P06). Selection was verified CORRECT (input_references_json resolved exactly the 111 P06 COs); the formula evaluation lost value.
- **Repair location:** D (governed evaluation runtime) honoring the engine's declared join semantic. `FormulaExecutionEngine` joins rowset pairs by `grainKeysHash(grain_keys)` (rowset×rowset arithmetic, per-row comparison, case/when then-branches). Self-verification fixtures carry per-CO grain keys (e.g. `document_number`), so the declared row identity is the Canonical Object. But the governed path's `buildSectionA` stamped `grain_keys = pickGrain(payload, partitionKeys)` — and for an ungrouped per-period metric `partitionKeys = []`, so **every row hashed to `{}` and all multi-variable joins collapsed onto one arbitrary row** (Map last-wins).
- **Invariant(s):** IV (references explicit — a rowset row must carry its object identity for any cross-variable reference), VI (the wrong value carried no evidence of the collapse).
- **Class:** impl-bug, but **path-critical in effect** — every live multi-variable-formula metric evaluated through the governed path is suspect: `average_days_to_collect` (AVG(clearing − due), rowset×rowset arithmetic), `average_days_delinquent`, `on_time_payment_rate`, `late_payment_frequency`, `within_terms_invoice_percentage`. Their published values (100 / 0 / etc.) were degenerate enough on pilot1 data to mask the defect; single-variable aggregates and secondary (metric_input) composites are unaffected.
- **Local unblock vs real fix:** the fix IS structural and small: `buildSectionA` stamps each row's `grain_keys` with the CO's explicit reference (`__co_ref: candidate.ref`) in addition to the partition keys — joins align per Canonical Object; partitioning (which hashes payload columns, not row grain_keys) is untouched; the fixture path (which supplies its own grain keys) is untouched. Operator approved applying it in-session. Re-evaluation after the fix: **10,718,630.05 exact**. `governed-metric-runtime.spec` green; the 10 `metric-spec-assembler.spec` failures were verified pre-existing on clean main (PR #385 fixture drift — separate task).
- **Disposition:** patched (bc-core working tree; **commit pending operator go**). Wave-1 re-run DONE same session — corrected values, all hand-verified against the live COs: `on_time_payment_rate` 100 → **81.081081**, `late_payment_frequency` 0 → **18.918919** (complement exact), `average_days_delinquent` null → **8.380952**, `average_days_to_collect` 14.297297 → **−0.297297** (honest per its declared avg(clearing − due); negative mean = average early payment — naming interpretation, not a value defect). Unchanged (shape-unaffected): `average_clearance_time`, `write_off_rate` (honest-0 numerator), `within_terms_invoice_percentage`.
- **Pattern-tag:** `rowset-join-empty-grain-keys`.
- **Graduates to:** the fix commit (pending) + this delta record.

### CB-018 — Composite resolver did not honor snapshot_selection_rule semantics
- **Metric / driver:** `accounts_receivable_growth_rate` (wave-2 TSK-8ab894 metric #4) — the first secondary metric binding the SAME upstream MC twice with different selection rules (as_of_period_end + prior_period_end).
- **Session:** SES-eaab9d (2026-07-02).
- **Where it blocked:** R5 payload verification — first evaluation returned **+1.0037791%** against the hand-computed **−0.993804%**: exactly (prior − end)/end, i.e. the two inputs swapped. Root cause in `CompositeMetricEvaluationService.resolveUpstream`: `as_of_period_end` selected the globally-latest accepted snapshot with **no period predicate** (my fresh P05 evaluation became the "period-end" value), and `prior_period_end` fell into the default branch = **current-period** matching. The DEC-0f3e57 selection-rule semantics were declared in the bindings but not implemented in the resolver; DSO/CEI never exposed it because their inputs bind distinct MCs and (until today) only current-period snapshots existed.
- **Repair location:** D (composite evaluation runtime) honoring B (the binding's declared `snapshot_selection_rule_code`).
- **Invariant(s):** I (the selection rule IS the declared meaning of the input; the runtime substituted a different selection), VI (no evidence distinguished which period each input actually read).
- **Class:** impl-bug, path-critical in effect — every prior_period_end composite (CEI's begin-balance) and any as_of_period_end input evaluated after a different-period snapshot existed was exposed.
- **Local unblock vs real fix:** the fix is the real fix: every rule scopes to an EXACT fiscal period (`as_of_period_end`/`period_matched` → the evaluation period; `prior_period_end` → the immediately preceding period via a label resolver `FY..../Pnn` with FY rollover, fail-closed to DEFER on parse failure or missing snapshot). Verified after fix: ar_growth_rate = **−0.9938035** (hand-exact); regression: DSO 48.769963 and AR turnover 1.845398 unchanged; CEI 96.018833 now reads the true P05 begin balance.
- **Disposition:** patched (bc-core working tree; **commit pending operator go**, same commit as CB-017). Noted: the composite service has NO unit spec file — test-debt task filed.
- **Pattern-tag:** `composite-selection-rule-not-honored`.
- **Graduates to:** the fix commit (pending).

### CB-019 — Declared composite grain identity is not unique over the resolved CO population
- **Metric / driver:** `billing_volume` (COUNT_DISTINCT document number = 95) vs `ar_open_invoice_count` (row count = 62) — surfaced by the SES-b54f06 full-catalog value audit while explaining why two "count" metrics on the same slice use different denominators.
- **Session:** SES-b54f06 (2026-07-02).
- **Where it blocked:** not a gate — a live-population audit. `fact.co_customer_invoice_arpi_slice_v9_4_0` holds **1,716 rows over 887 distinct (document_number, document_fiscal_year) identities** (BSAD line items — e.g. doc 0100000020/2025 ×3, all DR); even the open set at 2025-09-30 is 62 rows / 52 identities. The CC declares grain {issuing_legal_entity, document_number, document_fiscal_year}; the resolver groups by identity but each ADMISSION resolves to its own CO (UNIQUE(admission_id)), so line-item multiplicity survives into the CO population. Every metric then chooses a counting convention implicitly: COUNT_DISTINCT (billing_volume 95, AP `supplier_invoice_volume` counts rows = 64 vs 53 distinct — the SAME divergence on the payable slice), row-count (open counts), SUM (unaffected arithmetic but header-vs-line meaning shifts).
- **Repair location:** B (grain declaration must match the resolved population — either add the line-item discriminator to the grain, or declare header grain WITH explicit line aggregation in resolution) with D consequences (resolver grouping); feeds F1-B1 (TSK-ca5dd3, OC/CC 3.0.0 successors).
- **Invariant(s):** II (object ordering/identity — the declared identity tuple does not uniquely identify the objects), IV (references to "an invoice" are ambiguous between header and line).
- **Class:** path-critical for every count/average-per-document metric on both invoice slices; silent, because sums still verify.
- **Local unblock vs real fix:** wave metrics were authored self-consistently (each declares its own count basis) | real fix = one grain decision at B (F1-B1), then one counting convention per entity, contract-side; also see TSK-bd0c07 (open-invoice-count identity semantics).
- **Disposition:** open (operator decision: line grain vs header grain + aggregation).
- **Pattern-tag:** `grain-identity-not-unique`.
- **Graduates to:** TSK-c03522 / F1-B1 (TSK-ca5dd3).

### CB-020 — period_aggregate cannot declare which date defines period membership (clearing-date flow metrics bucket on posting period)
- **Metric / driver:** `cleared_invoice_amount`, `paid_customer_invoice_gross_amount`, `paid_customer_invoice_count` (AR), `paid_supplier_invoice_amount` (AP) — SES-b54f06 value audit.
- **Session:** SES-b54f06 (2026-07-02); ADR filed SES-57f670 (2026-07-03).
- **Where it blocked:** live-value audit. The MCs declare "clearing date falls in the evaluation period" but FY2025-26/P06 snapshots = **19,019,959.32 = the posting-period total** (identical to gross_invoiced_amount) vs 19,123,415.79 clearing-in-period. Root: `period_aggregate` performs no temporal selection (DEC-5ea578 ADR-#1 identity gate); the caller scopes candidates by the canonical-resolution-stamped `fiscal_period` (posting date) — the grammar has no word for "member by clearing date". The engine's own comment defers this to "ADR #2".
- **Repair location:** B (grammar: gate param) + D (candidate scoping honors it) — **ADR DEC-26f75a (D480, proposed)**: `period_aggregate` gains optional `anchor_field`; default = stamped fiscal_period (all existing MCs unchanged); activation-time fail-closed validation against the grain CC resolved_schema.
- **Invariant(s):** I (declared meaning "cleared in P" vs evaluated meaning "posted in P").
- **Class:** grammar-gap, path-critical for realization/settlement-flow metrics and every composite binding them.
- **Local unblock vs real fix:** none taken (no SDG/fact/read compensation — Foundation-prohibited) | real fix = D480 engine support + re-mint the four MCs with `anchor_field: clearing_date` in the same M15 supersession wave as CB-013/CB-016 (TSK-b96796).
- **Disposition:** ADR proposed (operator lock pending); re-mint M15-gated.
- **Pattern-tag:** `period-membership-anchor-undeclared`.
- **Graduates to:** ADR DEC-26f75a (D480).


---

## Appendix — operational / tooling friction (not foundation cases)

Kept out of the case dataset so it does not distort pattern analysis. Logged for operational improvement only.

- **bcf schema not in the bc-postgres read allowlist; panel-output-record + cert-confirm controllers are POST-only.** Blocked reading panel reasoning / cert ids. Resolved: added `concept_registry,bcf` to `PGMCP_SCHEMAS`; meanwhile read `bcf.*` via direct node-postgres. (SES-61d08f.)
- **`devhub_session_close` rejects the call when `self_audit_json` is supplied** (nested object alongside long string fields → `state`/`next` parsed as undefined). Workaround: close without it; record the D268 self-audit in the change-record `report_json`. (SES-61d08f.)
- **M12 panel: Maker/Checker period-anchor encoding divergence → `approve_with_loose_grounding` OPERATOR_REVIEW.** On non-plain-SUM period_aggregate candidates the paid Checker re-derives the period anchor as an `anchor_field` gate param — a shape the substrate kernel (DBCP §9.3) does not even carry (only `period_type` survives) — and the Judge escalates the unresolved convention. Resolution: state the convention explicitly in the candidate docket (`description_text` + `measurement_approach`): *"the period anchor is bound as a `temporal_anchor` variable binding (role_kind `input`), not a gate param"*. 4/4 affected AP specs passed on retry with the note. Candidate permanent fix = one sentence in the Checker prompt. (SES-c1d359.)
- **M12 Judge envelope schema violation: `duplicate_review.outcome='new_metric'` with non-null `primary_match_mc_uid`** → parser coerces to OPERATOR_REVIEW (TSK-08461b observability path). Fires stochastically when similar metrics exist to near-match (grows more likely as the catalog fills). Treatment: plain re-run. Candidate permanent fix = Judge prompt: on `new_metric`, `primary_match_mc_uid` MUST be null. (SES-c1d359.)
- **Writing files into bc-core while `npm run start:dev` (--watch) is live restarts the server mid-panel-run** → ECONNRESET on the in-flight `with-maker` call and ECONNREFUSED for the rest of a sequential batch. Generate all spec files BEFORE starting a batch; never write into the watched repo mid-batch. (SES-c1d359.)
