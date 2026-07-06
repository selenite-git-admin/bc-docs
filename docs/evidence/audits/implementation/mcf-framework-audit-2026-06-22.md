---
title: MCF Framework Audit — Findings
date: 2026-06-22
status: draft
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-framework-audit
scope: no substrate mutation; no runtime change; no MCF activation; no BCF / CC / OC mutation; no code patch; no DB write
briefing: bc-docs-v3/docs/implementation/mcf-framework-audit-brief-2026-06-22.md
session: SES-835a0b
---

# MCF Framework Audit — Findings

## 1. Executive synthesis

The Metric Context Framework's substrate gates (Identity / Lifecycle / Cert / Panel / AST / Fixture / Verifier / Reservoir-Ingestion) and its three behavioral stages (Metric Draft Review, Metric Contract Materialization, Publication Eligibility Evaluation) each closed on a credible **stage-local** proof — DDL applied, behavioral triggers fired, integration spec PASSED against `bc_platform_dev` under SAVEPOINT rollback. None of them closed on an **end-to-end portfolio** proof. The first metric to actually traverse the chain to Metric Activation (ARPI) reached that state through an ARPI-specific materialization controller; the second active metric (Billing Volume) brought a billing-volume-specific retry-unlock surface with it; the third (Cleared Invoice Amount) was authored against the same Customer Invoice canonical slice ARPI defined; the fourth (Invoice Processing Cycle Time) only activated after mid-flight authoring of a wholly new Observation Contract + Canonical Contract chain. Every additional metric activation attempt since has produced a new structural blocker, a new code patch, or a fresh chain authoring. The closeouts were not wrong — they were a happy-path survey, not a portfolio survey.

This is visible in three signals readable from the live substrate today:

1. **PE-MC evaluator has bumped five versions** (`mcf-m13-v2` → `mcf-m13-v6`) and the M14 activation evaluator has bumped twice (`mcf-m14-v1` → `mcf-m14-v2`) since the first metric reached Metric Activation on 2026-06-10. Three of those five bumps map directly to a metric whose activation surfaced something the evaluator had not seen. Every bump is, by Foundation Invariant V, an immutable append, not a correction — but the operational reality is that the framework is converging on its real semantics one metric at a time.
2. **Two of the seven Metric Contract Versions ever authored sit stuck in publication review with REJECT verdicts and no governed forward path.** Billing Cycle Time has `Source-Chain Resolvability Gate REJECT` and `Self-Verification Gate REJECT`. Paid Customer Invoice Count v2 has `Self-Verification Gate REJECT`. Both Metric Contract Versions are immutable; both parent Metric Contracts remain unarchived; the operator can soft-archive each parent (the abandon surface accepts `review` state, not just `draft` — this is a brief correction to the briefing) but doing so produces no new Metric Contract Version and conveys no semantic content about *why* the gate rejected. There is no "stuck-review doctrine" telling the operator what an abandon-then-rebind cycle is for, versus a Canonical Contract delta, versus a Verifier fix.
3. **The wall is invisible until a metric crashes into it.** Of the ten seed metrics the operator has explicitly queued for authoring since 2026-06-10, four have reached Metric Activation, two are stuck in publication review, three never produced a `consensus_payload_json.verdict_code = 'APPROVE_FOR_DRAFT'` panel run, and one (Invoice Processing Cycle Time) only activated after a new Observation Contract + Canonical Contract chain was authored mid-flight. The Source-Chain Resolvability Gate is the dominant gate exposing this — every queued Customer-Invoice-grain metric that needs a Business Concept the active Customer Invoice canonical slice does not declare hits the same wall. The wall is not visible from the metric authoring entry surface; it is only visible from the Publication Eligibility Evaluation verdict ledger.

The audit recommends the framework be re-declared closed only after a back-to-back portfolio covering a range of formula shapes and temporal gate shapes (the two orthogonal axes defined in [MMS doctrine §6.6](../../../operating-model/metric-management-system.md)) reaches Metric Activation with zero per-metric code patches and zero per-metric controller additions, every Metric Contract Version in the inventory in a non-stuck state, and the vocabulary lock in this document landed in code identifiers in at least one layer. The exact portfolio is proposed in §8.

The audit makes no recommendation about *whether* the framework should be re-declared closed, and no recommendation about the *order* in which the gaps in §6 should be closed. Those are operator decisions. The audit's role ends at making the gaps and their evidence visible. The substrate is correct under its own discipline; the framework around it is what is incomplete.

## 2. Vocabulary lock (in force throughout this document)

The lock from the briefing is binding here and is restated for the durable record. From this point in this document forward, semantic names stand alone; legacy codes appear in the lookup table below and at one further citation point per gap (§6) so the migration trail is legible.

### 2.1 Stages

| Semantic name | Legacy alias | What this stage does |
|---|---|---|
| Metric Draft Review | M12 | Panel (Maker / Checker / Moderator roles) proposes a metric candidate from an intake; produces a panel-run record and a candidate proposal envelope. |
| Metric Contract Materialization | M12.5 | Converts an approved panel proposal into a draft Metric Contract + Metric Contract Version + variable bindings + a seed fixture + a Self-Verification result; transitions intake to `consumed_by_panel`. |
| Self-Verification | M10 verifier | The engine runs the candidate metric's formula against its seed fixture and compares the result to the fixture's expected output; pass/fail is one of the gates in Publication Eligibility Evaluation. |
| Publication Eligibility Evaluation | M13 | Runs the full publication-eligibility gate matrix against a draft Metric Contract Version; on all-pass advances state draft → review → approved and stamps parent Metric Contract hash columns; on partial pass advances draft → review and stops. |
| Metric Activation | M14 | Transitions an approved Metric Contract Version to active and issues the activation certification record; gated on Publication Eligibility Evaluation having advanced state to approved and on parent Metric Contract hash columns being stamped. |
| Metric Supersession | M15 | Transitions an active Metric Contract Version to superseded; cert-bearing. |
| Business Concept Draft Review | B6 | Panel proposes a Business Concept candidate (admission to the concept registry). |
| Operator Certification | C5 | Operator confirms a Business Concept Draft Review proposal and mints the certification record. |
| Registry Write | F3 | The certification is applied to the registry as a fresh insert — the Business Concept lands as active. |
| Registry Transition | F3-like supersession / amend variants | The certification is applied as a state transition rather than a fresh registry insert. |

### 2.2 Gates

| Semantic name | Legacy alias | What this gate tests |
|---|---|---|
| Source-Chain Resolvability Gate | PE-MC-11 | Every variable binding's Business Concept must be declared by the resolved Canonical Contract's `field_selection` and reachable through the Source Contract / Admission Contract / Observation Contract chain. |
| Source-Vocabulary Discipline Gate | PE-MC-12 | Variable bindings stay within source vocabulary — no derived or synthesized fields posing as source-grade. |
| Self-Verification Gate | PE-MC-10 | The Self-Verification result for the candidate's seed fixture must be `pass` against the current package signature, with `stale_fixture_flag = false`. |
| Materialization Preconditions | L-V1* (a–i) | Read-only checks before Metric Contract Materialization may proceed: temporal-gate-shape-code validity (against the substrate enum on `mcf.metric_contract.temporal_gate_shape_code`), formula AST grammar, prior-materialization absence, collision avoidance, etc. |
| Draft Review Coverage Checks | C-FX-* | In-panel checks the Checker role runs to enforce that the Maker's proposal covers required structural and semantic dimensions (temporal grain, formula well-formedness, evidence binding, resolver mapping, fiscal-time handling, etc.). |

### 2.3 Discipline rule

Semantic names are primary. Legacy codes appear at first mention only, in the table above, or inside the migration appendix when the audit's own vocabulary-lock ADR draft (§7) is filed. Decision codes (`DEC-…` / `D…`) are unchanged — they identify *decisions*, not *processes*, and citation forms are unaltered.

## 3. Re-grade of prior closeouts (briefing §3.1)

Every closeout document in `bc-docs-v3/docs/implementation/mcf-m2…m13` was a substrate-side or stage-local success. The grade column below uses the briefing's three-value scale: `stage-local` (the stage's own unit tests + a single happy-path proof), `end-to-end` (the stage drove a real Metric Contract Version through to Metric Activation under realistic substrate), `mixed` (some end-to-end evidence, but the portfolio of failure modes the stage owns was not exercised). The `verified` column records what the closeout proved; the `assumed-away` column records what was tested under a happy path or substrate-empty assumption that subsequent metric authoring has since broken.

| Closeout | Stage owned | Grade | Failure modes verified | Failure modes assumed-away |
|---|---|---|---|---|
| `mcf-m2-ddl-apply-closeout.md` | Identity substrate (5 tables, hash columns, `candidate_source_ref_json` enum) | stage-local | DDL applied; 12/12 structural checks; tables empty | Hash regex stability across the formula-shape-by-temporal-gate-shape product (the M4 closeout later surfaced `mock-1.0.0` / `mcf-m4-verifier-v1` regression — both substrate-incompatible with `^mcf-[a-z-]+-v[0-9]+$`); no proof that 17 closed-enum CHECKs cover the formula-shape × temporal-gate-shape combination space |
| `mcf-m3-ddl-apply-closeout.md` | Lifecycle substrate (revision + supersession tables, state-transition triggers, immutability triggers) | stage-local | 6 trigger paths exercised under positive + negative synthetic rows (rolled back); `draft → review → approved` enforced; hash NOT NULL gate at approved enforced | Whether the trigger surface covers the descriptive-vs-identity-bearing column split correctly for every variation of the metric body (formula AST × bindings × filters × temporal gate shape — the two-axis vocabulary in MMS §6.6); the AST column amendment in `mcf-m7-m8-apply-closeout.md` later added a third IF to the descriptive-immutability function — a substrate gap latent until the AST column landed |
| `mcf-m3-cert-amendment-apply-closeout.md` | Foundation governance substrate (per-framework cert table + shared CHECK extensions) | stage-local | 4 behavioral exercises pass (synthetic mcv `approved → active` succeeds when cert present, fails when absent); regression check on `operator_confirm_rule.action_code` enum unchanged | No evidence that the framework_policy `mcf_v1` carries every policy field a real activation needs — every M14 / M15 path that surfaced later (defect-code registry pin in M5, vendor-allowlist seed in M12, role-grant audit table in subsequent expansion) extended the substrate or its seed rows |
| `mcf-m4-ddl-apply-closeout.md` | Cert writer + transition authority + publication-eligibility-result table + idempotency table | stage-local | 14/14 structural checks; 7/7 integration tests for cert writer (full lifecycle, demotion, archived-policy rejection, idempotency commit / cache-hit / mismatched-action / stuck-pending takeover) | The cert writer's portfolio of `action_code` × `from_state` × `to_state` was exercised on synthetic rows only; the first real `metric_transition` activation happened weeks later and immediately drove `mcf-m14-v1 → mcf-m14-v2` bump — i.e. the M14 evaluator changed shape between closeout and first real use |
| `mcf-m5-apply-closeout.md` | Panel substrate (panel_run + transcript + allowlists + deferred FK activations + policy extension) | stage-local | Substrate writes work; transcript immutability fires; jsonb-merge policy extension preserved existing keys; verifier-fix patch (#113) needed mid-gate to wrap each negative assertion in SAVEPOINT (false-negative recovery cycle) | No proof that a real panel run actually drives the substrate end-to-end (vendor adapters were shells; allowlists empty); no proof that the consensus payload schema accommodates the spectrum of formula shapes and temporal gate shapes (MMS §6.6) a panel would propose |
| `mcf-m7-m8-apply-closeout.md` | Formula AST canonicalization + hash bundle (`mcf-hash-v1`) + descriptive-immutability trigger amendment | stage-local | Column added; trigger amended in same `BEGIN/COMMIT`; 5 behavioral exercises pass (draft permit, review reject, approved Q1 lock, mixed state+AST reject, state-only transition permit); golden anchor hardcoded against tautology | The AST canonical form was proven on the ARPI / billing_volume / cleared_invoice_amount happy paths; on the **temporal gate shape** axis, `period_aggregate` is the only value exercised in production (five of the six substrate-enum values — `instantaneous`, `trailing_window`, `point_in_time`, `as_of`, `rolling_window` — remain untested); on the **formula shape** axis (MMS §6.6), `as-of balance`, `window / rolling`, and `bucket / status share` remain untested under real fixtures |
| `mcf-m9-apply-closeout.md` | Self-Verification Fixture substrate (16-column table, 5 hashes per row, immutability trigger, FKs) | stage-local | 13/13 post-apply checks pass on first attempt; 5 CHECK predicates byte-matched against `pg_get_constraintdef()`; 3-FK widened rejection probe; SAVEPOINT-protected from start (M5 lesson absorbed) | No verifier-engine fixture-portfolio proof — the closeout explicitly notes "the M9 arc is not complete until the M9-engine impl PR lands"; the deferred engine work (DBCP §18.1 items 5–8) shipped later as M10; the portfolio-per-formula-class question (§19.13 Q37 "minimum-fixture-coverage per formula class") was logged as open |
| `mcf-m10-apply-closeout.md` | Self-Verification Result substrate + verifier engine (sync v1) | stage-local | 16/16 checks; 7/7 cert-writer integration; M4-deferred FK activation; M4 doc-bug correction inline | The closeout records the verifier engine "live and dormant"; the first real Self-Verification ran weeks later under the ARPI happy path; two of the six live verifier runs have returned `verdict_code = 'fail'` (billing_cycle_time, paid_customer_invoice_count_v2) with `stale_fixture_flag = false` — i.e. the engine has shape-specific failure modes not surfaced in the closeout (this is gap §6.4) |
| `mcf-m11-apply-closeout.md` | Reservoir ingestion substrate (intake queue, 3-layer co_bindings enforcement) | stage-local | 15/15 checks; writer-side JSONB double-encoding bug surfaced mid-gate and patched in PR #121 (first time substrate exposed a writer-side wire-protocol bug that unit tests could not catch — a generalizable lesson the closeout itself records) | The intake-to-panel handoff was exercised only in the closeout-clean post-apply rerun; the operator-direct CLI ingestion path has been used productively but the seed-driven ingestion is the path the portfolio will exercise |
| `mcf-m12-implementation-closeout.md` | Metric Draft Review service (panel orchestration, vendor adapter shells, allowlists, defect registry, runtime AJV schema validation) | stage-local | Integration spec 2/2 PASS under SAVEPOINT rollback against `bc_platform_dev`; HA-1..HA-9 enforced; three-vendor rule asserted; vendor adapters shipped as shells | Vendor adapters were not exercised against real model APIs in the closeout; the structured-output defect tracked as `TSK-08461b` (Maker and Checker emit envelopes as inline text in `reasoning_trace`, persistence reads `candidate_proposal={}`, consensus fires `OPERATOR_REVIEW`) was not yet known; the defect blocks every seed → Metric Draft Review → Metric Contract Materialization path that is not already operator-direct ingested |
| `mcf-m12-5-implementation-closeout.md` | Metric Contract Materialization service | stage-local | Integration spec PASSED end-to-end against real Self-Verification + hash + fixture services under SAVEPOINT rollback; HA-1..HA-8 enforced; idempotent retry proven | The closeout is explicit: "no real operational materialization has executed against `bc_platform_dev`"; the first operational materialization happened later via ARPI under the per-metric materialization controller — i.e. the closeout did not exercise the generic surface, only the synthetic happy path |
| `mcf-m13-implementation-closeout.md` | Publication Eligibility Evaluation service | stage-local | 16/16 substrate probes; integration spec exercises 10 gate checks across happy + retry + REJECT + stale-package-retry scenarios; HA-1..HA-8 enforced; same-tx wiring contract proven; cert model locked at "zero certs from evaluator, M14 owns activation cert" | The evaluator was exercised against synthetic Metric Contract Versions only; the production evaluator has since bumped 5 versions (`v2 → v6`) under live use, surfacing per-metric semantics not covered by the closeout's exercises |

**Cross-cutting observation.** Every closeout records the substrate stays empty after its proof — the proof is the substrate's discipline under structural and synthetic-row exercises. None of the closeouts could have caught the gaps that have since emerged, because the gaps surface only when a portfolio spanning distinct formula shapes and temporal gate shapes (MMS §6.6) attempts publication against a shared and incomplete canonical vocabulary. The closeout discipline is not the failure mode; the closeout *scope* was the failure mode — each closeout was a stage-local closure, not a framework-level closure.

## 4. Metric Contract Version inventory by semantic lifecycle state (briefing §3.2)

Every row in `mcf.metric_contract_version` is listed. Semantic lifecycle state derives from `governance_state_code`, parent Metric Contract `archived_at`, latest Publication Eligibility Evaluation verdict snapshot, and Metric Activation cert presence. The "block reason" column reads against the live Source-Chain Resolvability Gate, Self-Verification Gate, and Source-Vocabulary Discipline Gate verdicts in `mcf.metric_publication_eligibility_result`.

| Metric Contract name | Metric Contract UID | Metric Contract Version UID | Version code | Legacy state code | Semantic lifecycle state | Latest Publication Eligibility verdicts | Path to advancement / block reason |
|---|---|---|---|---|---|---|---|
| average_revenue_per_invoice | 7453d4dc-70d9-4116-8ebb-9345cc9980b8 | ac960286-a453-4740-9d0b-5fe8395e471d | v1 | active | active / published | All gates PASS on `mcf-m13-v2` (Source-Vocabulary Discipline Gate not yet shipped at activation time, hence 10 gates); Metric Activation cert recorded under `mcf-m14-v1` | none — currently the only published metric of `ratio` formula shape |
| billing_volume | 1f142962-da1e-45c6-86e2-72613db57ded | 81ba6735-1356-4d9b-a900-1c187a4fedcd | v1 | active | active / published | All gates PASS on `mcf-m13-v3` (Source-Vocabulary Discipline Gate now present and PASS); Metric Activation cert under `mcf-m14-v2` | none — currently the only published metric of `count` formula shape on Customer Invoice grain |
| average_revenue_per_invoice__rebind_ac960286 | 4c1c7f89-0d1c-41a2-a856-c072433a7176 | e121613c-5891-4906-8f95-38b5471ff3d3 | v1 | review | superseded / abandoned (parent `archived_at` stamped 2026-06-11) | `mcf-m13-v3` — 10 gates PASS, Source-Chain Resolvability Gate PASS, **Duplicate-Intent Gate REJECT** (the candidate's identity tuple collides with the active ARPI Metric Contract) | terminal — the rebind attempt was abandoned via parent-archive once the duplicate-intent verdict landed; the Metric Contract Version row is immutable and remains in `review` state under the archived parent |
| cleared_invoice_amount | 2bda5252-5648-4e78-bcfd-6f8e3f98e155 | 57ea07d0-120d-484b-a099-fd43fdb008fe | v1 | active | active / published | All gates PASS on `mcf-m13-v4`; Metric Activation cert under `mcf-m14-v2` | none — currently the only published metric of `sum` formula shape |
| billing_cycle_time | 37b7e70a-7209-4db0-9c9c-ce50f9e4a89f | 995f90e3-70a0-4b0d-8f12-aa1f4619c2b5 | v1 | review | publication review (stuck) | `mcf-m13-v6` — **Source-Chain Resolvability Gate REJECT**, **Self-Verification Gate REJECT** (verifier returned `fail` on a fresh fixture with `stale_fixture_flag=false`), 10 other gates PASS | blocked — Maker bound `cycle_end_anchor` to Customer Invoice × sent date (BC `30a7afa5-…`) and `cycle_start_anchor` to Customer Invoice × document date BC (`8cbd57be-…`); the active Canonical Contract `cc__customer_invoice_arpi_slice v4.0.0` declares neither of those Business Concepts (its 9 `field_selection` entries cover net / gross / tax / clearing date / posting date / document type / status / currency / document number) — Source-Chain Resolvability cannot resolve; Self-Verification additionally fails (root cause not yet isolated from the substrate evidence — both gates need a separate forward path); no rollback (Invariant III); no re-evaluation without substrate change; only governed exit is parent-archive abandon |
| paid_customer_invoice_count_v2 | dd2567a4-09a3-4c7e-85eb-4e2e1c6a65dd | db3e1bd0-051b-401f-8278-e3cd84e622a7 | v1 | review | publication review (stuck) | `mcf-m13-v5` — **Self-Verification Gate REJECT**, 11 other gates PASS (including Source-Chain Resolvability — the candidate binds to Customer Invoice × document number `51482979-…` which IS in the active CC) | blocked — verifier returned `fail` on a fresh fixture with `stale_fixture_flag=false`; the rejection is engine-side not chain-side, so a Canonical Contract delta would not unblock; the engine path the verifier took on this metric's shape (`count_distinct` over `denominator_key` with no filter and `period_aggregate` temporal gate) has not been root-caused at this substrate evidence depth; only governed exit is parent-archive abandon |
| invoice_processing_cycle_time | 82545316-b016-4991-bcbd-30336252a5e4 | bb033fcf-9303-478e-8afb-e8278cd248f6 | v1 | review | superseded / abandoned (parent `archived_at` stamped 2026-06-21) | `mcf-m13-v6` — **Source-Chain Resolvability Gate REJECT**, 11 other gates PASS | terminal — the first IPCT attempt was abandoned once it became clear the Customer Invoice canonical slice could not declare the supplier-side cycle anchors; the operator authored a wholly new `cc__supplier_invoice_ipct_slice v1.0.0` canonical contract chain mid-flight and re-authored the metric on the Supplier Invoice grain |
| invoice_processing_cycle_time (Supplier Invoice grain) | a4412f05-d752-4d91-bdda-acb98cad3a86 | 0511925f-6eba-4a52-ba4e-ec3065726327 | v1 | active | active / published | First run `mcf-m13-v6` Source-Chain Resolvability Gate REJECT; second run `mcf-m13-v6` ALL PASS once the new CC chain was active; Metric Activation cert under `mcf-m14-v2` | none — first metric in the inventory to require a new Observation Contract + Canonical Contract chain to clear publication; first `average of delta` formula shape activated |

### 4.1 Inventory summary

- **Active / published:** 4 (ARPI, billing_volume, cleared_invoice_amount, invoice_processing_cycle_time-on-supplier-invoice). Four formula shapes covered: `ratio`, `count`, `sum`, `average of delta`. All four share the same temporal gate shape `period_aggregate`; the other five substrate-enum temporal gate shapes remain unexercised.
- **Stuck in publication review with no governed forward path:** 2 (billing_cycle_time, paid_customer_invoice_count_v2). Both fail Self-Verification; one additionally fails Source-Chain Resolvability.
- **Superseded / abandoned:** 2 (average_revenue_per_invoice__rebind_ac960286, the first invoice_processing_cycle_time attempt). Both terminal under parent-archive.
- **Authored draft (no Publication Eligibility Evaluation rows yet):** 0.
- **Materialized draft (Self-Verification result exists, no Publication Eligibility Evaluation rows yet):** 0.

### 4.2 Latest evaluator versions in use

| Evaluator algorithm version | Metric Contract Versions touched | First run | Last run |
|---|---|---|---|
| `mcf-m13-v2` | 1 (ARPI) | 2026-06-10 | 2026-06-10 |
| `mcf-m14-v1` | 1 (ARPI activation) | 2026-06-10 | 2026-06-10 |
| `mcf-m13-v3` | 2 (billing_volume + ARPI rebind attempt) | 2026-06-10 | 2026-06-11 |
| `mcf-m14-v2` | 3 (billing_volume + cleared_invoice_amount + supplier-grain IPCT activations) | 2026-06-11 | 2026-06-21 |
| `mcf-m13-v4` | 1 (cleared_invoice_amount) | 2026-06-13 | 2026-06-13 |
| `mcf-m13-v5` | 1 (paid_customer_invoice_count_v2) | 2026-06-15 | 2026-06-15 |
| `mcf-m13-v6` | 3 (both IPCT attempts + billing_cycle_time) | 2026-06-21 | 2026-06-22 |

Five Publication Eligibility Evaluation version bumps and two Metric Activation evaluator bumps over twelve days of live use. Each bump is, by Foundation Invariant V, an immutable append. The operational reading is that the evaluator's semantics are being refined per-metric, not portfolio-up-front.

## 5. Coverage matrix — near-term seed metrics (briefing §3.3)

Twenty-three seed metric rows are listed below: the ten seeds the operator has explicitly queued for authoring since 2026-06-10, plus the next thirteen seeds the operator has recently expressed intent on (most recent `status_updated_at` first, taking the top of the `candidate`-status queue). The columns predict whether each seed would clear publication today against the live Canonical Contract surface (`cc__customer_invoice_arpi_slice v4.0.0` on Customer Invoice grain, `cc__supplier_invoice_ipct_slice v1.0.0` on Supplier Invoice grain) and the active Business Concept vocabulary. The point is to make the Source-Chain Resolvability wall visible before the next activation attempt.

The required-Business-Concept inference is conservative: it names the minimum set of Business Concepts the formula hint would force the Maker to bind on a known grain. The Maker may bind additional Business Concepts; the matrix scopes only the minimum predictable-from-the-hint set.

| Seed metric name | Seed metric ID | Status | Inferred formula shape | Required Business Concepts (minimum) | Required-BC coverage by active Canonical Contract | Source-Chain resolvability | Predicted Publication Eligibility outcome | Recommended unblock |
|---|---|---|---|---|---|---|---|---|
| invoice_processing_cycle_time | 6408e0c8-… | queued | average of delta | Supplier Invoice × posting date, Supplier Invoice × invoice receipt date | covered (cc__supplier_invoice_ipct_slice v1.0.0) | reachable | would pass (already published — duplicate-intent rejection if re-submitted on same grain) | none — already active |
| paid_customer_invoice_gross_amount | 1014c099-… | candidate | sum (with `status = 'paid'` filter) | Customer Invoice × gross amount, Customer Invoice × status | covered (gross amount = `abe0d7d7-…`, status = `0a860227-…` both in v4.0.0) | reachable | would pass at Source-Chain Resolvability; Self-Verification outcome unknown — depends on engine handling of filter predicate against status code value set | proceed via Metric Draft Review + Metric Contract Materialization; verifier-engine outcome is the open question |
| paid_customer_invoice_count_v2 | 6b5e1fec-… | queued | count (with `status = 'paid'` filter) | Customer Invoice × document number, Customer Invoice × status | covered | reachable | already failed at Self-Verification Gate on `mcf-m13-v5`; would fail again at the same gate under the same evaluator | engine-side investigation required (see gap §6.4 — verifier portfolio stability); no chain change unblocks |
| paid_customer_invoice_count | 3a2f8f35-… | queued | count (with `status = 'paid'` filter) | Customer Invoice × document number, Customer Invoice × status | covered | reachable | would fail at Self-Verification Gate on the same engine path that rejected paid_customer_invoice_count_v2 | same as above — engine-side, not chain-side; effectively duplicate-intent with v2 |
| disputed_invoice_count | 7c118a93-… | candidate | count (with `status = 'in-dispute'` filter) | Customer Invoice × document number, Customer Invoice × status | covered | reachable | would pass at Source-Chain Resolvability; Self-Verification outcome unknown — same formula shape as paid_customer_invoice_count_v2 + paid_customer_invoice_count which both failed Self-Verification | depends on whether the engine-side failure on the count+filter formula shape is local to that fixture or systemic |
| invoice_dispute_rate | 25f80255-… | queued | ratio | Customer Invoice × document number, Customer Invoice × status (numerator filter `in-dispute` and denominator all) | covered | reachable | would pass at Source-Chain Resolvability; Self-Verification outcome unknown — the ratio formula shape is published (ARPI) but ARPI does not exercise a filter | proceed; engine-side filter+ratio interaction is the open question |
| billing_cycle_time | 8a824bba-… | queued | average of delta | Customer Invoice × document date, Customer Invoice × sent date | **not covered** (active CC declares neither `8cbd57be-…` nor `30a7afa5-…`; document_date canonical field name is bound to posting date BC `61e19048-…`, a latent misbinding from CC v3 carried forward by design) | unreachable | already failed at Source-Chain Resolvability Gate AND Self-Verification Gate on `mcf-m13-v6` | Canonical Contract delta — extend `cc__customer_invoice_arpi_slice` to declare sent date and the actual document date BC (or author a sibling slice); separately investigate Self-Verification engine failure on `average of delta` formula shape (see gap §6.4) |
| cleared_customer_payment_amount | fade681d-… | queued | sum (BLART = 'DZ' filter) | Customer Payment × payment amount, Customer Payment × status (or document type) | not covered — no active Customer Payment canonical slice declares payment amount + status; Customer Payment Business Concepts are admitted but no Canonical Contract on this grain exists | unreachable | would fail at Source-Chain Resolvability Gate | Canonical Contract authoring on Customer Payment grain |
| cleared_invoice_amount | a833261a-… | queued | sum (BLART = 'DR' filter) | Customer Invoice × gross amount, Customer Invoice × document type code | covered | reachable | already published | none — already active (note: this seed predates the activated MC; the seed remains in `queued` state under the substrate convention but its sibling is the live cleared_invoice_amount Metric Contract) |
| average_days_to_collect | b117c940-… | queued | average of delta | Customer Invoice × clearing date, Customer Invoice × due date | partial — clearing date `5fe49908-…` declared; due date `b49aa30e-…` is an active Business Concept but NOT declared by `cc__customer_invoice_arpi_slice v4.0.0` | unreachable | would fail at Source-Chain Resolvability Gate | Canonical Contract delta — extend the Customer Invoice slice to declare due date |
| billing_volume | 802a133c-… | queued | count | Customer Invoice × document number | covered | reachable | already published | none — already active |
| average_revenue_per_invoice | 2b789e9b-… | queued | ratio | Customer Invoice × net amount, Customer Invoice × document number | covered | reachable | already published | none — already active |
| absorption_costing_ratio | de81da54-… | candidate | ratio | manufacturing cost concepts × units produced — no active entity declares these | not covered — no Canonical Contract or Business Concepts on this domain | unreachable | would fail at Source-Chain Resolvability Gate | Business Concept Framework expansion before any chain authoring |
| available_cash_flow | 74fc13c5-… | candidate | sum-of-deltas | net income, depreciation, amortization, working capital change, capital expenditure, dividends — none of these Business Concepts exist as active | not covered | unreachable | would fail at Source-Chain Resolvability Gate | Business Concept Framework expansion |
| 360_degree_feedback_completion_rate | 6db1120f-… | candidate | ratio | HR domain — no active entity / Business Concept on this domain | not covered | unreachable | would fail at Source-Chain Resolvability Gate | out of scope for the finance pilot |
| vacancy_cost / time_on_market / tenant_turnover_cost / tenant_satisfaction_index / … (12 real-estate seeds, all `candidate`, `low` confidence band, formula_hints empty) | 2759683b-… and 11 siblings | candidate | unknown — no reference formula | not inferable | not covered (real-estate domain) | unreachable | would not reach the Maker — `formula_hints` empty | out of scope until the real-estate domain is admitted into the Business Concept Framework |

### 5.1 What the matrix makes visible

- Of the ten queued seed metrics, four are already active (ARPI, billing_volume, cleared_invoice_amount, IPCT — and the IPCT seed-row is on a different grain from the activated MC, but the seed is satisfied by the activation). Two are stuck (billing_cycle_time, paid_customer_invoice_count_v2). Four are unblocked-but-not-yet-attempted (paid_customer_invoice_count, invoice_dispute_rate, average_days_to_collect, cleared_customer_payment_amount).
- Of the four unblocked-but-not-yet-attempted seeds: two would fail at Source-Chain Resolvability today (average_days_to_collect on a Business Concept the CC doesn't declare; cleared_customer_payment_amount on a grain that has no Canonical Contract at all). One would clear Source-Chain Resolvability but is at risk on Self-Verification (paid_customer_invoice_count — same formula shape that already failed on v2). One would clear Source-Chain Resolvability but its filtered-ratio interaction is untested under Self-Verification (invoice_dispute_rate).
- The ten queued seeds together cover four formula shapes (count, sum, ratio, average of delta). The substrate has demonstrated four `period_aggregate` activations and one `period_aggregate average-of-delta` activation. No `as-of balance`, no `window / rolling`, no `bucket / status share` is exercised in production. The portfolio sample is shallower than the seed catalog implies.
- Beyond the queued seeds, the recently-candidate seeds (paid_customer_invoice_gross_amount, disputed_invoice_count) would clear Source-Chain Resolvability — those are the two cheapest tests of "can the framework activate a metric without requiring a canonical-contract delta or a code patch."

### 5.2 Wall summary

The Source-Chain Resolvability wall has two layers visible today:

1. **Inside the active Customer Invoice canonical slice.** Every metric whose formula needs sent date, document date BC (as opposed to the posting-date BC mis-bound to the `document_date` canonical field name), due date, payment terms, or any Business Concept not in the v4.0.0 nine-field selection fails the gate. Today that includes billing_cycle_time and average_days_to_collect at minimum.
2. **Outside the Customer Invoice slice.** Every metric whose grain is Customer Payment, Customer Invoice Line Item, Customer Invoice Adjustment, GL Account, Journal Entry, or any of the other eighteen active entities (the inventory in §4 enumerates only Customer Invoice and Supplier Invoice as having canonical contracts today) fails the gate by virtue of having no Canonical Contract at all on its grain. Today that includes cleared_customer_payment_amount.

The matrix is the visible wall. Each row blocked at Source-Chain Resolvability is a Canonical Contract authoring task; each row blocked at Self-Verification is a verifier-engine investigation task; the two are independent.

## 6. Framework gap inventory (briefing §3.4)

Five gaps were seeded by the briefing. All five are confirmed against substrate evidence. Two additional gaps surfaced from the inventory + matrix and are recorded under §6.6 and §6.7. The gaps are not ordered by priority — ordering is an operator decision.

### 6.1 Missing post-review recovery orchestration

**Legacy code reference.** Stage codes M12.5, M13, M14, M15.

**Source-confirmed prior state — generic surfaces that DO exist (correction to a prior draft of this finding).** A re-read of `bc-core/src/registry/mcf/` confirms multiple generic lifecycle surfaces are live and operating on any Metric Contract Version, not metric-named:
- `mcf-materialization.controller.ts:31` — `POST /mcf/panel-runs/:panelRunUid/materialize` (generic Metric Contract Materialization endpoint).
- `mcf-publication-eligibility.controller.ts:99` — `POST /mcf/metric-contracts/:metricContractUid/evaluate-pe-mc` (generic Publication Eligibility Evaluation endpoint).
- `mcf-publication-activation.controller.ts` — generic Metric Activation endpoint.
- `mcf-mcv-rebind.controller.ts:56` — `POST /mcf/metric-contract-versions/rebind` (generic draft-successor rebind).
- `mcf-mcv-abandon.controller.ts:50` — `POST /mcf/metric-contract-versions/:uid/abandon` (generic abandon; accepts `draft` OR `review` state per `readAbandonGates` in `mcf-cert-writer.service.ts`).
- `mcf-mcv-supersede.controller.ts` — generic supersession.
- `mcf-mcv-fixture-append.controller.ts` — generic post-hoc fixture attachment.

The gap is therefore not "the lifecycle surface is metric-specific." The gap is **orchestration / doctrine across those surfaces after a Metric Contract Version lands in publication review with REJECT verdicts**.

**Symptom (what the operator sees).** When Publication Eligibility Evaluation returns a partial-pass with REJECT verdicts, the Metric Contract Version sits in `review`. The operator faces five possible next actions and no governed routing between the inbound verdict and the chosen action:
1. Re-evaluate (substrate has changed since the last run, e.g. a Canonical Contract delta landed).
2. Restart from draft (create a new Metric Contract Version under the same parent with refined bindings).
3. Rebind (replace specific variable role bindings; the rebind controller already exists for this shape).
4. Abandon (soft-archive the parent Metric Contract; the abandon controller accepts `review` state).
5. Open a Canonical Contract delta intake (the chain side of the wall — see §6.3 for the existing Chain Enrichment scaffolding).
6. Open a verifier engine investigation (the engine side of the wall — see §6.4).

Two per-metric controllers remain in the tree as evidence that this orchestration gap forced earlier organic workarounds: `mcf-arpi-materialization.controller.ts` (ARPI's pre-generic materialization path, preserved while the generic surface stabilised) and `billing-volume-retry-unlock/billing-volume-retry-unlock.controller.ts` (a billing-volume-specific recovery path). These are symptoms, not the root cause; the generic surfaces have since landed.

**Root cause.** Each individual lifecycle surface knows its own transition semantics. None of them reads the latest Publication Eligibility Evaluation verdict ledger and answers "for this Metric Contract Version, given these REJECT reasons, which of the six actions above is the right next step?" The orchestration layer that would sequence the recovery path — and capture the operator decision durably — does not exist.

**Architectural fix recommendation.** A *post-review recovery orchestration* layer that consumes the Publication Eligibility Evaluation verdict ledger for a stuck Metric Contract Version and returns a structured "next-action" recommendation drawn from the six actions above. The orchestration does not need new HTTP surfaces for actions 1–4 (they exist); it needs (a) a read surface that classifies REJECT reasons into action categories, and (b) durable capture of the operator's chosen action so the audit trail records *why* a stuck Metric Contract Version moved to its chosen terminal state. Action 5 hooks into the Chain Enrichment scaffolding in §6.3; action 6 hooks into the verifier portfolio work in §6.4.

**Migration impact.** New read surface (no DDL); thin write surface for operator-decision capture (additive — may use existing rationale fields or extend with a small audit table); operator runbook chapter in `bc-docs-v3/docs/onboarding/`. The two per-metric controllers can be deprecated once the orchestration layer is stable.

**Owner layer.** New `mcf-post-review-orchestration.controller.ts` (proposed); reads from `mcf.metric_publication_eligibility_result`; routes to the existing rebind / abandon / fixture-append / Chain Enrichment surfaces; secondary impact on `mcf-cert-writer.service.ts` for operator-decision capture.

### 6.2 Missing stuck-review / abandon doctrine

**Legacy code reference.** Foundation Invariant III (append-only ledger); stage codes M13, M14, M15.

**Symptom.** Billing Cycle Time has Source-Chain Resolvability Gate REJECT and Self-Verification Gate REJECT. Paid Customer Invoice Count v2 has Self-Verification Gate REJECT. Both Metric Contract Versions are in `review` state. The Metric Contract Version row is immutable; the parent Metric Contract is unarchived. The operator can call the existing abandon endpoint (which accepts `review` per `mcf-cert-writer.service.ts` `readAbandonGates` — this is a minor correction to the briefing's wording that "abandon only works in draft state"). What the operator does not have is a *doctrine* answering three questions: (a) when do you abandon vs. when do you restart-from-draft vs. when do you wait for a Canonical Contract delta? (b) what evidence do you preserve from the rejected Metric Contract Version's REJECT verdicts so the next attempt does not repeat the failure? (c) what does the abandon mean to a downstream observer — is the metric "wrong" or "blocked-by-substrate"?

**Root cause.** The abandon surface exists at the substrate level. The doctrine framing it does not. The closeouts treated abandon as a substrate corner case; the live evidence shows it is the only governed forward path from a stuck-review state, and operators today have no chapter telling them when to use it.

**Architectural fix recommendation.** Write the doctrine. A short chapter that names, with worked examples from the live inventory:
- The four post-review verdicts: `re-evaluable` (substrate change can flip the gate), `engine-side defect` (verifier needs investigation; the metric is not at fault), `chain-side delta needed` (Canonical Contract or Observation Contract must extend), `superseded by alternative` (a different Metric Contract subsumes this one).
- The four actions: re-evaluate, restart-from-draft, abandon-and-leave-parked, abandon-and-supersede-with-new-metric.
- The mapping between verdict and action.

**Migration impact.** Documentation only at the doctrine level; a substrate addition for the post-archive note (a column or table that captures *why* a parent was archived, beyond the rationale text already required) is open for design.

**Owner layer.** `bc-docs-v3/docs/operating-model/` (new chapter); secondary impact on `bc-docs-v3/docs/onboarding/metric-registration.md` and on the operator console UI surfaces (M16 / M17 family).

### 6.3 Chain Enrichment v1 — extend to Canonical Contract delta from Publication Eligibility failure

**Legacy code reference.** Stage codes B6, C5, F3 family; Chain Enrichment Engine `cee-v0.2`.

**Source-confirmed prior scaffolding.** Re-read of `bc-core/src/registry/mcf/chain-enrichment/chain-enrichment.service.ts` (CEE planner version `cee-v0.2` at line 69) confirms a planner-only service already exists that emits gap plans for three chain layers:
- `source_contract_gap_plan` (v0)
- `admission_contract_gap_plan` (v0.1)
- `observation_contract_gap_plan` (v0.2)

`NEXT_GAP_AFTER_OC` (line 87-93) explicitly states: *"CC / metric-chain planning is deferred to CEE v1+."* The Chain Enrichment Engine is designed to host Canonical Contract delta planning as its v1 increment; today it stops at the OC layer. CEE writes only to `mcf.chain_enrichment_plan` — it is planner-only and never mutates business substrate.

**Symptom.** When the Source-Chain Resolvability Gate rejects (PE-MC-11 REJECT) because a variable binding's Business Concept is not declared by the active Canonical Contract's `field_selection`, there is no surface that turns that verdict into a Canonical Contract gap plan. Today the operator must either author a new Canonical Contract chain manually (the Invoice Processing Cycle Time path — `cc__supplier_invoice_ipct_slice v1.0.0` authored mid-flight) or abandon the metric (the ARPI rebind path). The decision is operator-judgment, with no surface capturing why the metric needed Business Concepts the active CC lacked.

**Root cause.** Two adjacent gaps. (a) The Source-Chain Resolvability Gate's REJECT verdict is a verdict, not a plan — it does not emit "CC v(n+1) should declare {X, Y, Z}." (b) The Chain Enrichment Engine's v1 increment, which is the natural host for that plan, has not been opened. The framework already conceives of CC delta planning as Chain Enrichment v1 work; the increment is deferred and unwired.

**Architectural fix recommendation.** Extend Chain Enrichment to v1 with a `canonical_contract_gap_plan` mode that:
- Consumes Publication Eligibility verdict evidence — specifically PE-MC-11 (Source-Chain Resolvability Gate) REJECT rows from `mcf.metric_publication_eligibility_result` — as the planner's input signal.
- Identifies the unresolvable Business Concepts referenced by the stuck Metric Contract Version's variable bindings and computes the minimum Canonical Contract delta (which CC to extend, which fields to add, which Business Concepts they bind to).
- Emits a `chain_enrichment_plan` row with `gap_kind = 'canonical_contract'` and a structured packet the existing harness v1.1 + CAS (D445) audit-first loop can apply and verify.
- Stays planner-only per CEE's existing discipline; the harness remains the executor.

The metric-chain planning case (a stuck Metric Contract Version that needs a Canonical Contract delta) is the natural first scope for CEE v1 because the operator already faces it weekly and the chain-side intake already exists in CEE v0/v0.1/v0.2 form.

**Migration impact.** Net extension of `chain-enrichment.service.ts` (add a fourth mode); new DTO + planner branch; reuse of the existing `mcf.chain_enrichment_plan` write surface; harness v1.1 needs a CC-apply branch (orthogonal to this audit's scope); operator runbook chapter in `bc-docs-v3/docs/onboarding/canonical-contract-creation.md`. No net-new controller family — CEE's existing controller surface receives the new mode.

**Owner layer.** `bc-core/src/registry/mcf/chain-enrichment/chain-enrichment.service.ts` (planner extension); `chain-enrichment.controller.ts` (new mode parameter); `bc-docs-v3/docs/onboarding/canonical-contract-creation.md` (operator runbook); ADR governing the v1 increment (CEE v1 doctrine — likely under DEC-e01fcf / D447 or a successor).

### 6.4 Verifier portfolio stability gap

**Legacy code reference.** Self-Verification Gate (PE-MC-10); Self-Verification (M10 verifier).

**Symptom.** The Self-Verification engine has produced `verdict_code = 'fail'` with `stale_fixture_flag = false` on two of the six live verifier runs. The two failures are billing_cycle_time (an `average of delta` formula shape on Customer Invoice grain with sent date / document date anchors not in the resolved Canonical Contract — so the engine may be running against a substrate it cannot actually source) and paid_customer_invoice_count_v2 (a `count_distinct` over a covered Business Concept with a `status = 'paid'` filter — a filtered-count formula shape the engine has not exercised under the published ARPI / billing_volume / cleared_invoice_amount / IPCT). A prior verifier fix landed at PR #344 (engine date-arithmetic fix); the live evidence suggests there are additional formula-shape-specific evaluation paths the engine has not been hardened against.

**Root cause.** The verifier is exercised on the metric's own fixture (one fixture per metric); the substrate's M9 closeout flagged "minimum-fixture-coverage per formula class" as open in DBCP §19.13 Q37. Today there is no portfolio of fixtures-by-formula-shape (per MMS §6.6) against which every engine change is regression-tested. The engine's per-formula-shape correctness is therefore proven one metric at a time, in production. (Temporal-gate-shape correctness is a separate axis — currently all live activations use `period_aggregate`, so non-`period_aggregate` temporal gate evaluation paths are also untested; the portfolio should cover both axes.)

**Architectural fix recommendation.** A verifier portfolio: one fixture per formula shape (`count`, `sum`, `average of delta`, `ratio`, `bucket / status share`, `as-of balance`, `window / rolling`, plus a `filtered` variant of each), each with a known-good expected output, exercised on every engine change before the engine version bumps. The portfolio lives in `bc-core/src/registry/mcf/` as a test suite; failures block the engine version bump. The two live `fail` verdicts on billing_cycle_time and paid_customer_invoice_count_v2 are root-caused in this work — either the engine is wrong for those shapes, or the fixtures are wrong, or the substrate evidence is incomplete; the portfolio investigation answers which.

**Migration impact.** Test-only at the substrate level; engine changes downstream may follow. No DDL; no service-surface change; no operator-facing change beyond verifier-version bumps being more honestly delayed.

**Owner layer.** `bc-core/src/registry/mcf/formula-execution.engine.spec.ts` (existing engine spec); new `bc-core/src/registry/mcf/verifier-portfolio.spec.ts`; verifier-engine implementation in `formula-execution.engine.ts`.

### 6.5 Operator-facing naming / code opacity

**Legacy code reference.** Stage codes M12, M12.5, M13, M14, M15, B6, C5, F3; gate codes PE-MC-1..12, L-V1*, C-FX-*.

**Symptom.** Every reader maintains a glossary. The closeouts, the controllers, the service methods, the runbooks, the audit artifacts, and the operator console UI all use the legacy codes. New session prompts repeat the glossary. The audit's own existence is partly a forcing function for this gap — re-grading the closeouts required translating between the build-plan code and the semantic intent of each stage.

**Root cause.** The build plan was numbered for sequencing convenience. The numbering then propagated into code identifiers, controller routes, service method names, database enum values, runbook headings, and audit artifact filenames. Every layer treats the build-plan number as the durable identifier.

**Architectural fix recommendation.** The vocabulary lock in §2 is the substantive fix. §7 below drafts the ADR that records it for the migration. The migration plan in §7 sequences the rename: doctrine first, then code identifiers and routes, then database enum values with transition-window aliases, then operator UI labels.

**Migration impact.** Each layer's rename is independently scoped — doctrine and audit artifact rename has zero substrate impact; code and route rename is a refactor of files in `bc-core/src/registry/mcf/`; database enum extension is additive (the existing values stay; new semantic names enter as aliases); UI label rename touches the operator console family.

**Owner layer.** ADR draft (in §7 below); migration owner is the operator and reaches every layer in turn.

### 6.6 Per-metric coupling between Maker and Canonical Contract (audit-surfaced)

**Symptom.** Three of the four published metrics (ARPI, billing_volume, cleared_invoice_amount) bind to Business Concepts that happen to be in the active Canonical Contract because the slice was authored by-and-around ARPI in the first place (the Canonical Contract's description records this: "ARPI Customer Invoice canonical slice"). When the Maker proposes a Business Concept the slice does not declare, the Source-Chain Resolvability Gate rejects. The Maker has no inbound signal naming which Business Concepts are in the active slice — its proposal can only be validated post-hoc. Three of the eight Metric Contract Versions ever authored have hit this wall (the ARPI rebind, the first IPCT attempt, and Billing Cycle Time).

**Root cause.** The Maker is independent of the active Canonical Contract surface. The Source-Chain Resolvability check is run after the Maker's proposal, not during it. The Maker proposes; the verdict rejects; the operator decides between Canonical Contract delta and metric abandon. There is no upstream Maker-side filter that says "of the Business Concepts available on this grain, the active Canonical Contract declares the following nine; if you propose outside that set, you are implicitly requesting a Canonical Contract delta."

**Architectural fix recommendation.** Either (a) feed the active Canonical Contract's `field_selection` Business-Concept set into the Maker as a Maker-side constraint, with explicit operator override required to propose outside the set; or (b) keep the Maker free but make the Source-Chain Resolvability Gate REJECT verdict route directly into the Chain Enrichment v1 `canonical_contract_gap_plan` intake (§6.3) without operator re-keying. The two are not mutually exclusive — (a) reduces gate-rejection noise while (b) closes the feedback loop when the Maker legitimately needs Business Concepts the active slice lacks.

**Migration impact.** Maker prompt extension (option a) is light; the Chain Enrichment v1 wiring (option b) is the increment described in §6.3. Both depend on the Maker's structured-output discipline being reliable (see §6.7 for the live state of that surface).

**Owner layer.** `bc-core/src/registry/mcf/m12-panel-maker.v1.md` (Maker role prompt); `MetricAuthoringPanelService` (panel orchestration); the Chain Enrichment v1 increment proposed in §6.3.

### 6.7 Structured-output failure lacks a semantically distinct verdict (audit-surfaced)

**Correction to a prior draft of this finding.** An earlier draft asserted that the `TSK-08461b` failure mode (Maker / Checker emitting envelopes as inline `reasoning_trace` text, persistence seeing `candidate_proposal={}`) currently blocks every seed → Metric Draft Review → Metric Contract Materialization path. Re-read of the live source disproves the blanket claim. The framework has since added explicit handling for the structured-output failure mode at two surfaces; the remaining gap is at the *verdict semantics* layer, not the routing layer.

**Source-confirmed prior scaffolding.**

- `bc-core/src/registry/mcf/metric-authoring-panel.service.ts` lines 528-549 — the panel service harvests the Maker's `candidate_proposal` whenever the Maker voted `APPROVE_FOR_DRAFT` and produced a `proposal_payload`, **even when the consensus downgrades to `OPERATOR_REVIEW`**. The comment cites `TSK-08461b` directly: "The operator needs to see the actual proposal alongside the downgrade reason to adjudicate without re-running the panel." Persistence therefore no longer always sees `candidate_proposal={}` on downgrade; it sees the harvested proposal when the Maker had one.
- `bc-core/src/registry/mcf/panel-agents/panel-envelope-finalization.ts` lines 91-119 — `buildEnvelopeNotSubmittedResult` synthesizes a `ParseSuccess` carrying an `envelope_not_submitted_via_tool` parser warning when Stage 2 finalization completes without the model invoking the structured-output tool. The role's verdict is forced to `OPERATOR_REVIEW`; the role's `operator_review_reason` becomes `structured_envelope_not_submitted`; the truncated raw text the model returned in place of the tool call is preserved for operator inspection.

**Live remaining gap.** Both safety nets converge on the same terminal verdict: `OPERATOR_REVIEW`. The verdict ledger therefore collapses two distinct failure classes into one signal:
- **Tool-call / structured-output failure** — the model did not produce a parseable envelope through the required tool surface; the metric proposal cannot be evaluated at all.
- **Substantive metric weakness** — the model produced a valid envelope but the proposal needs operator judgment (loose grounding, near-duplicate, ambiguous binding, etc.).

The operator reviewing a stuck Metric Contract Version sees `verdict_code = 'OPERATOR_REVIEW'` and must read the `operator_review_reason` text and the harvested proposal to discover which class applies. There is no top-level verdict distinguishing them, and the defect-code registry (`mcf-defect-registry-v1.ts`) does not yet carry a closed-enum value for the structured-output-failure class as a first-class verdict outcome.

**Root cause.** When the structured-output safety nets were added, the routing was chosen to be conservative (fall through to `OPERATOR_REVIEW`) to avoid silent drops. The verdict grammar was not extended to name the class as distinct. The persisted evidence is rich enough to disambiguate post-hoc, but the consumer surfaces (Publication Eligibility Evaluation, the operator console, the seed catalog status updaters) treat `OPERATOR_REVIEW` as a single category.

**Architectural fix recommendation.** Introduce a structured-output / admission-failure verdict classification distinct from substantive `OPERATOR_REVIEW`. Two cuts are possible and not mutually exclusive:
- A new top-level `verdict_code` value (e.g. `OPERATOR_REVIEW_STRUCTURED_FAILURE`) so downstream consumers can route differently — for instance, the seed catalog can re-queue the intake rather than mark it consumed, and the operator console can surface a "retry the panel" action rather than a "review this proposal" action.
- A new closed-enum `defect_code` in `mcf-defect-registry-v1.ts` paired with the existing `OPERATOR_REVIEW` verdict — preserving the current verdict grammar while giving consumers a precise tag to read on the defect_code field.

The second cut is the smaller change and is the recommended starting point; the first cut may follow if downstream consumers demand top-level routing distinctions.

**Migration impact.** Defect-registry extension (closed-enum addition); panel service routes the `envelope_not_submitted_via_tool` and similar parser-warning codes to the new defect_code; verdict-grammar extension (optional second cut) is additive at the database enum level; consumer-side routing updates in the seed catalog status updater and operator console; no DDL beyond the additive enum extension.

**Owner layer.** `bc-core/src/registry/mcf/mcf-defect-registry-v1.ts` (defect-code registry); `bc-core/src/registry/mcf/metric-authoring-panel.service.ts` (consensus computation); `bc-core/src/registry/mcf/panel-agents/panel-envelope-finalization.ts` (already emits the parser warning that the new defect code would route from); secondary impact on the seed catalog status updater and the operator console.

## 7. Vocabulary-lock ADR draft (briefing §3.5 — held proposal)

> **Forward pointer (added 2026-06-22).** The held draft below was filed as [ADR DEC-7a1c98](../../../governance/adrs/ADR-7a1c98.md) on 2026-06-22, then superseded the same day by **[DEC-54f221 / D449](../../../governance/adrs/ADR-54f221.md)** which locks a three-layer model (Interpretation Surfaces / Implementation Names / Compatibility Names) in place of this section's six-step sequence. The legacy-code scope, the DEC-/D-/ADR-UID exclusion, the migration appendix (Decision 6 below), the MMS hierarchy, and Foundation Invariant III are preserved verbatim by DEC-54f221. Decision 3 (inline source comments as a permanent alias context) is **changed** in DEC-54f221 — comments are renamed at Layer 1 with transition-window annotation only. Decision 4's six-step ordering and §7A.3 below are **replaced** by DEC-54f221's three-layer model. This held-proposal section is preserved as historical evidence per Foundation Invariant III; the live authority is DEC-54f221.

This is a held proposal, not a filed ADR. It is drafted here so the lock is canonically captured at the moment of the audit, and so the operator can file it (or revise it) without re-deriving the migration plan.

### 7.1 Context

The MCF build plan numbered its stages and gates by position in the build list. The numbers were a development sequencing convenience. They have since propagated into code identifiers, controller routes, service method names, runbook chapter headings, audit artifact filenames, the operator console UI, and the database enum values that participate in the cert and PE-MC verdict surfaces. Every reader of every artifact in `mcf-*` maintains a glossary translating those numbers into the behavioral intent of each stage or gate.

The first cost of this is opacity — every session prompt repeats the glossary, every audit re-derives it. The second cost is closer to a correctness risk — the build-plan numbering has occasionally drifted (the M-track build plan canonically integers 0–20, but the requirements document used a divergent numbering; the "M12.5" half-label is an interstitial half-stage), and downstream code has occasionally chased the wrong number. The third cost is operator-facing — the operator console UI displays the legacy codes; the operator has no way to discuss the framework's behavior without translating to its semantic intent.

This ADR locks the semantic vocabulary and sequences the migration.

### 7.2 Decision

Adopt the legacy → semantic mapping in §2 of the audit document as the canonical vocabulary for stages and gates. Semantic names are primary. Legacy codes appear (a) at first mention in any new artifact, alongside the semantic name in parentheses, and (b) in the migration appendix of this ADR. Decision codes (`DEC-…` / `D…`) are unchanged.

The vocabulary lock applies to all new artifacts. Existing artifacts are migrated in the order below.

### 7.3 Migration plan (each step gates the next)

> **Superseded by DEC-54f221 (2026-06-22).** The six-step sequence below is replaced by the three-layer model in [ADR DEC-54f221](../../../governance/adrs/ADR-54f221.md) — Interpretation Surfaces / Implementation Names / Compatibility Names. The legacy-code scope paragraph below remains valid (and is preserved verbatim by DEC-54f221); only the step ordering is replaced. Preserved as historical evidence per Foundation Invariant III.

**Scope of legacy codes covered by this migration.** This plan applies to the full **opaque workflow-code family** that has accumulated as semantic-name surrogates inside MCF and the adjacent BCF surfaces:

- **M-track process codes** — `M12`, `M12.5`, `M13`, `M14`, `M15`, and the broader M0–M20 sequence used as process names (per §7.6, the build-plan document itself may retain the M0–M20 integers as pure sequencing scaffolding; everywhere they function as **names for stages or processes**, they are renamed to the semantic names mapped in §2.1).
- **Publication / coverage / precondition codes** — `PE-MC-*` (gates inside Publication Eligibility Evaluation; mapped exhaustively in §4.3), `L-V1*` (Materialization Preconditions), `C-FX-*` (Fixture Structural Check codes inside Self-Verification).
- **BCF-style stage / action shorthand** — `B6` (Business Concept Draft Review panel), `C5` (Operator Certification), `F3` (Registry Write / Transition), and the `C1` / `C2` / `F1` / `F2` series **where they function as process names** (the same letters used as in-document section identifiers inside ADRs and chapters are out of scope; only the process-name uses are renamed).

**Identifiers that are NOT renamed.** Decision identifiers — `DEC-…`, `D-…`, ADR UIDs of any form — are unique identifiers of governed decisions, not process names. They are unchanged by this migration regardless of how often they appear alongside legacy process codes. Cross-references continue to cite the existing IDs verbatim.

**Staged sequence — six steps, each gating the next.** This is the canonical Controlled Semantic Refactor sequence per §7A.3 of this audit. The four-step framing carried in an earlier draft of this section is superseded. Filing this ADR lands **Step 1 only**; Steps 2 through 6 each require their own future operator authorization at the point of execution.

| Step | Layer | Scope | Owner |
|---|---|---|---|
| 1 | Doctrine + Vocabulary-Lock ADR | File this ADR (or the operator-revised version) and the migration appendix that records the full legacy ↔ semantic mapping for cross-reference. New doctrine chapters in `bc-docs-v3/docs/implementation/`, `docs/operating-model/`, and `docs/foundation/` adopt semantic names from the date of ADR filing. Doctrine landing has zero substrate impact; it is the reference every subsequent step cites. | Documentation |
| 2 | Operator-facing docs and UI labels | Rename runbook chapter titles in `bc-docs-v3/docs/onboarding/`, operator console labels, audit-artifact filenames (new artifacts only — historical artifact filenames are never rewritten per Foundation Invariant III), and the bc-admin Metric Lifecycle / Metric Chain surface labels. UI rename is operator-visible but reversible at the label layer. | Documentation + bc-admin |
| 3 | Code identifiers and class / service / controller names | Rename inside `bc-core/src/registry/mcf/` (and adjacent BCF code surfaces touched by `B6` / `C5` / `F3` shorthand) — class names, service method names, file names, type names. Each rename is a pure refactor (no behavior change); test suites pass against either the legacy or the new name during the transition window via re-export aliases. HTTP routes are NOT renamed in this step. | bc-core |
| 4 | HTTP route aliases | Add semantic routes (e.g. `POST /api/mcf/metric-contract-versions/:uid/recover-post-review`) alongside the existing legacy routes (`POST /api/mcf/metric-contract-versions/:uid/abandon` continues to work). Both routes resolve to the same handler. The legacy routes are deprecated in a later operator-authorized step once consumers migrate; the deprecation window length is an operator decision. | bc-core |
| 5 | Database enum and persisted-code aliases (additive only) | Extend `governance_state_code`, `verdict_code`, `pe_check_code`, `action_code`, and similar enum columns with semantic-named values alongside the existing legacy values. The writer side may emit either; the reader side accepts both. **Historical evidence is never rewritten** (Foundation Invariant III) — database rows already written under legacy values stay under those values forever. A future operator decision may deprecate the legacy aliases at the *writer* layer; the *reader* layer must continue to accept them for as long as historical rows exist. | bc-core + DDL |
| 6 | Per-metric controller quarantine / fold-in | After the semantic routes in Step 4 are stable, the per-metric controllers (`mcf-arpi-materialization.controller.ts`, `billing-volume-retry-unlock/`, and any sibling per-metric surfaces) are either folded into the generic Stage 4 / Stage 7 surfaces or moved to a `legacy/` directory and marked deprecated. This step is small but visible; doing it last keeps Steps 2–5 independently revertible. | bc-core |

Each step is independently scoped; later steps gate on earlier steps having landed without correction. **Filing this ADR authorizes only Step 1 — the doctrine and migration appendix.** Steps 2 through 6 each require their own operator authorization session at the point of execution.

### 7.4 Owner layer per renamed surface

| Renamed surface | Owner |
|---|---|
| `mcf-*.controller.ts` route names + filenames | bc-core / `src/registry/mcf/` |
| `McfPublicationEligibilityEvaluatorService` and sibling service names | bc-core / `src/registry/mcf/` |
| `governance_state_code` / `verdict_code` enum values | bc-core (DDL) |
| `pe_check_code` enum (`PE-MC-1..12`) | held — see §7.6 |
| Operator console labels | bc-admin |
| Runbook chapters in `bc-docs-v3/docs/onboarding/` | Documentation |
| ADR cross-references in `bc-docs-v3/docs/adrs/` | Documentation |

### 7.5 Migration impact summary (rough count)

| Layer | Files / routes / enum values / labels affected |
|---|---|
| Documentation | ~25 chapters and audit artifacts in `bc-docs-v3/docs/implementation/`, `docs/onboarding/`, `docs/operating-model/`; this number will grow as new chapters are written under the lock |
| bc-core code | ~30 controller and service files in `src/registry/mcf/`; ~50 spec files; ~10 type files |
| Database | 0 enum value removals; ~10 additive value pairs across `governance_state_code`, `verdict_code`, and the cert `action_code` family |
| bc-admin UI | the Metric Lifecycle and Metric Chain surfaces touch ~15 component-level labels |

### 7.6 Decisions left to operator

**Recommended discipline (tightened from a prior draft of this section).** Semantic names are primary in operator-facing code identifiers, controller and route names, runbook chapters, ADR bodies, operator console UI labels, and any new documentation. Legacy codes may survive as aliases in three specific places only:
- Inline comments in code (`// legacy: M12` style annotations on the semantic identifier, for at least one published portfolio activation cycle).
- Log metadata fields and emitted telemetry tags (so log-pipeline consumers built against the legacy codes do not need a same-day rewrite).
- Persisted historical evidence (database rows already written under legacy values are never rewritten — Foundation Invariant III) and the vocabulary-migration appendix that captures the mapping for cross-reference.

A prior draft of this section recommended that `PE-MC-N` numbering survive as the primary in-code gate identifier. That recommendation is withdrawn — it would half-solve the gap by keeping the numeric token in the load-bearing surface where it is most read. The amended recommendation is: introduce semantic gate identifiers (e.g. `source_chain_resolvability_gate`) as the primary in-code symbol and route fragment; `PE-MC-11` becomes the legacy alias allowed in comments, log metadata, the persisted `pe_check_code` column on `mcf.metric_publication_eligibility_result` for historical rows, and the migration appendix.

**Open decisions.**

- Whether the M-track build-plan integers (M0–M20) survive in the build-plan document itself or are also renamed (recommended: keep in the build plan, since the build plan is sequencing scaffolding; rename everywhere else).
- Whether the audit's "Source-Chain Resolvability Gate", "Source-Vocabulary Discipline Gate", and "Self-Verification Gate" names are the right semantic names, or whether further iteration produces better names. (The audit recommends adopting them as-is; the iteration cost is a separate ADR.)
- Whether the `pe_check_code` column on `mcf.metric_publication_eligibility_result` should accept both the legacy `PE-MC-N` values and the new semantic values during the transition window (recommended: yes, additive only; new rows may emit either; historical rows are never rewritten).

## 7A. Controlled semantic refactor — decision needed (not authorized by this document)

> **Forward pointer (added 2026-06-22).** The six-step sequence in §7A.3 below is **superseded** by [ADR DEC-54f221 / D449](../../../governance/adrs/ADR-54f221.md), filed 2026-06-22. DEC-54f221 replaces the six-step ordering with a three-layer model (Interpretation Surfaces / Implementation Names / Compatibility Names) and adds two preconditions the six-step model did not require: a bc-ai prompt-cluster regression gate inside Layer 1, and a telemetry / log / dashboard pre-inventory before Layer 3 opens. The §7A.3 content below is preserved as historical evidence per Foundation Invariant III; the live authority for refactor sequencing is DEC-54f221.

**This section captures a decision point, not a sanction to refactor.** Nothing in this section authorizes any code change, route rename, enum extension, UI relabel, or controller consolidation. The refactor named below is a *future* decision that the operator may take, defer, or reshape. The audit's role is to surface the decision while it is still cheap.

### 7A.1 Why the decision is being raised now

Names and code grew organically while the framework was being built — each stage's controllers, services, route fragments, and enum values were chosen at the point of that stage's first implementation, against the build-plan number that was load-bearing at the time. The result is the legacy-code opacity gap recorded in §6.5 and the half-finished surfaces noted in §6.1 (post-review orchestration sits across multiple controllers with no orchestration layer) and §6.3 (Chain Enrichment v1 is a known increment that has not been opened). A subset of artifacts also carry per-metric coupling (`mcf-arpi-materialization.controller.ts`, `billing-volume-retry-unlock/`) that the generic surfaces have since outgrown but not yet replaced.

The framework is still in development. No tenant runtime depends on the MCF surfaces in production yet. The cost of a controlled semantic refactor now is lower than the cost of the same refactor after the framework has been declared closed and downstream consumers (tenant runtime, the operator console, the bc-admin Metric Lifecycle surface) have bound to the legacy names. A big-bang rename is the wrong shape — it would risk silent breakage of in-flight code branches, audit artifacts, and persisted enum values. A staged refactor, sequenced so each step is independently verifiable and reversible, is the right shape.

### 7A.2 Recommendation (held for operator decision)

The controlled semantic refactor is recommended **only after** the audit amendments in §3–§8 are accepted and the vocabulary-lock ADR (§7) is filed. The refactor is its own work plan, scoped separately from the gap-repair work in §6. The two streams are independent: the gap-repair plan adds capabilities (post-review orchestration, Chain Enrichment v1, verifier portfolio, structured-output verdict semantics); the refactor renames what exists. Doing them together compounds risk; doing them in sequence keeps each step legible.

### 7A.3 Proposed staged sequence

Each step gates the next. No step authorizes a code or substrate change by itself — each step requires its own operator authorization at the point of execution.

1. **Doctrine / vocabulary ADR first.** File the ADR drafted in §7 (or a revised version operator chooses) and the migration appendix. Doctrine landing has zero substrate impact; it is the reference every subsequent step cites.
2. **Operator-facing docs and UI labels next.** Rename runbook chapter titles, operator console labels, audit-artifact filenames (new artifacts only — historical artifact filenames are never rewritten), and the bc-admin Metric Lifecycle surface labels. UI rename is operator-visible but reversible at the label layer.
3. **Code identifiers and class / service / controller names next, with behavior unchanged.** Rename inside `bc-core/src/registry/mcf/` — class names, service method names, file names, type names. Each rename is a pure refactor (no semantic change); the test suites pass against either the legacy or the new name during the transition window via re-export aliases.
4. **HTTP route aliases next.** Add semantic routes (e.g. `POST /mcf/metric-contract-versions/:uid/recover-post-review`) while preserving legacy routes temporarily (`POST /mcf/metric-contract-versions/:uid/abandon` continues to work). The route aliases are deprecated in a later step once consumers migrate; the deprecation window length is an operator decision.
5. **Database enum and persisted-code aliases last, additive only.** Extend `governance_state_code`, `verdict_code`, `pe_check_code`, `action_code` and similar enums with semantic-named values alongside the existing legacy values. The writer side may emit either; the reader side accepts both. **Historical evidence is never rewritten** (Foundation Invariant III). A future operator decision may deprecate the legacy aliases at the *writer* layer; the *reader* layer must continue to accept them for as long as historical rows exist.
6. **Quarantine or fold per-metric controllers last.** After the semantic routes in step 4 are stable, the per-metric controllers (`mcf-arpi-materialization.controller.ts`, `billing-volume-retry-unlock/`) are either folded into the generic surfaces or moved to a `legacy/` directory and marked deprecated. This step is small but visible; doing it last keeps the prior steps independently revertible.

### 7A.4 Hard rule

The controlled refactor is a **future** decision, not part of this edit, not part of the audit, and not authorized by either. This audit document captures the decision point and a suggested sequencing so the operator can choose to open the refactor work plan as its own session, with its own scope, its own approvals, and its own gates.

If the operator chooses to defer the refactor indefinitely, the audit's findings remain valid; the legacy-code opacity gap (§6.5) simply remains open. If the operator chooses to open the refactor immediately, the audit recommends starting with step 1 and stopping at the doctrine-only boundary before deciding on step 2.

## 8. MCF framework-ready exit criteria (briefing §3.6)

The framework should be re-declared closed when an outside observer can verify all five of the following against the live substrate:

### 8.1 Portfolio minimum

**Amended 2026-06-22 per [MMS doctrine §6.6](../../../operating-model/metric-management-system.md).** The portfolio is now expressed against **two orthogonal axes** that the prior draft conflated:

- **Formula shape** — operational classification of what arithmetic the metric performs. Derived from the formula AST. The seven shapes the verifier portfolio must cover: `count`, `sum`, `ratio`, `average of delta`, `as-of balance`, `window / rolling`, `bucket / status share`.
- **Temporal gate shape** — substrate enum on `mcf.metric_contract.temporal_gate_shape_code` (closed enum from `mc_temporal_gate_shape_chk` in `bc-core/src/database/schema/mcf/metric-contract.ts`). Six values: `instantaneous`, `trailing_window`, `period_aggregate`, `point_in_time`, `as_of`, `rolling_window`. Identity-bearing — different temporal gate shapes produce different `identity_tuple_hash` values on the parent Metric Contract.

The two axes cross-product to 42 combinations; the portfolio does not need full coverage. It needs the cells below — chosen because each one exercises a distinct failure-mode surface (verifier-engine path, temporal-grammar path, chain-coverage path, filter-interaction path, multi-grain authoring path).

The four already-active metrics on `bc_platform_dev` all share the **same temporal gate shape** (`period_aggregate`) across four different formula shapes (ARPI = ratio, billing_volume = count, cleared_invoice_amount = sum, IPCT = average of delta). The portfolio's chief unexercised territory is therefore the non-`period_aggregate` temporal gates — particularly `as_of` and `rolling_window` — which neither the verifier nor the chain has tested under real authoring.

**Portfolio cells (11) — Twelve metrics activated back-to-back across these eleven cells, with no per-metric code patch and no per-metric controller addition.**

| # | Cell description | Formula shape | Temporal gate shape | Filter dimension | Multi-grain? | Min count | Live evidence today |
|---|---|---|---|---|---|---|---|
| 1 | Unfiltered count | count | period_aggregate | none | no | 1 | billing_volume — covered |
| 2 | Status / type-filtered count | count | period_aggregate | status / type | no | 2 | none today (paid_customer_invoice_count_v2 is stuck on Self-Verification; paid_customer_invoice_count not yet attempted) |
| 3 | Unfiltered sum | sum | period_aggregate | none | no | 1 | none today — no published `sum` metric is unfiltered (see cell 4 on cleared_invoice_amount) |
| 4 | Status / type-filtered sum | sum | period_aggregate | doctype (`BLART`) | no | 1 | cleared_invoice_amount — covered (active version applies a `BLART = 'DR'` document-type filter) |
| 5 | Sum on a grain that has no active Canonical Contract today | sum | period_aggregate | none | yes (Customer Payment grain) | 1 | none today (e.g. cleared_customer_payment_amount). Purpose: force at least one Canonical Contract authoring beyond `cc__customer_invoice_arpi_slice` and `cc__supplier_invoice_ipct_slice` |
| 6 | Unfiltered ratio | ratio | period_aggregate | none | no | 1 | ARPI — covered |
| 7 | Status-filtered ratio | ratio | period_aggregate | status | no | 1 | none today (invoice_dispute_rate would be the candidate) |
| 8 | Average of delta | average of delta | period_aggregate | none | no | 2 | IPCT — partially covered (one activation on Supplier Invoice grain); the second is billing_cycle_time which is stuck on Source-Chain Resolvability + Self-Verification |
| 9 | As-of balance (exercises non-`period_aggregate` temporal gate) | as-of balance | as_of | none | possibly (depends on candidate) | 1 | none today (e.g. open_receivable_balance). Purpose: exercise the `as_of` temporal gate shape — currently unused by any active metric |
| 10 | Window / rolling (exercises non-`period_aggregate` temporal gate) | window / rolling | rolling_window (or trailing_window) | possibly | no | 1 | none today (e.g. trailing 90-day revenue). Purpose: exercise the `rolling_window` / `trailing_window` temporal gate shape — currently unused by any active metric |
| 11 | Bucket / status share | bucket / status share | period_aggregate | status (numerator) | no | 1 | none today |

Twelve activations spread across these eleven cells (cells 2 and 8 each carry minimum count 2). The recommendation is **twelve activations, eleven cells, seven formula shapes covered, three temporal gate shapes exercised (`period_aggregate` + `as_of` + `rolling_window`-or-`trailing_window`), no per-metric code patches**. The number is honest, not optimistic: at the current rate of two activations per ten days, this is at least two months of work even with the gaps closed.

### 8.2 Zero per-metric code patches during the portfolio run

Every patch needed during the portfolio surfaces *as a framework gap before the portfolio begins*, not during it. The Publication Eligibility Evaluation evaluator's version stays at the same value across the portfolio run (no `mcf-m13-v7` mid-portfolio); the Metric Activation evaluator stays at the same value; no per-metric controllers are added.

### 8.3 Every gap in §6 resolved before the portfolio begins

The five seeded gaps (missing post-review recovery orchestration, missing stuck-review doctrine, Chain Enrichment v1 canonical-contract delta extension, verifier portfolio stability, operator-facing naming) and the two audit-surfaced gaps (Maker / Canonical Contract coupling, structured-output failure verdict semantics) are each closed with a tracked artifact before the portfolio run starts.

### 8.4 Every Metric Contract Version in the inventory in a non-stuck state

The two stuck Metric Contract Versions (billing_cycle_time and paid_customer_invoice_count_v2) are each driven to one of three terminal states: `active / published` (after a Canonical Contract delta and a verifier-engine fix), `superseded / abandoned` (after a doctrine-guided abandon decision), or re-evaluated to `active / published` under a Canonical Contract that now declares their required Business Concepts.

### 8.5 Vocabulary lock landed in code identifiers in at least one layer

> **Reframed under DEC-54f221 (2026-06-22).** Under the three-layer model in [ADR DEC-54f221](../../../governance/adrs/ADR-54f221.md) (superseding DEC-7a1c98), this exit criterion is satisfied when **Layer 2 (Implementation Names)** has materially landed — semantic class / service / controller / method / filename identifiers inside `bc-core/src/registry/mcf/`, plus internal route aliases, plus the per-metric controller quarantine. Per DEC-54f221, Layer 2 cannot open until Layer 1 (Interpretation Surfaces — including doctrine, runbooks, UI copy, source comments, test descriptions, error messages, and the gated bc-ai prompt sub-cluster) is materially complete on the surfaces a Layer 2 rename touches.

The original Step 3 framing below is preserved as historical evidence per Foundation Invariant III.

> *(Original framing, superseded.)* The Step 3 rename in §7A.3 (code identifiers and class / service / controller names inside `bc-core/src/registry/mcf/`) lands. Doctrine (Step 1) lands first per the migration sequencing, followed by operator-facing docs / UI labels (Step 2). The Controlled Semantic Refactor in §7A is the canonical staged sequence; the older 4-step framing in §7.3 (inside the Vocabulary-Lock ADR draft) is superseded by §7A.3's 6-step refinement and is expected to be revised in line with §7A.3 when the ADR is filed.

### 8.6 Why this bar, honestly

A smaller bar (e.g. "five of five with three shapes") would close the framework on a wider sample of the same Customer Invoice ratio / sum / count happy paths. The portfolio's purpose is to exercise the *failure-mode surface*, not to multiply happy-path counts. Two formula shapes that have never been activated (`as-of balance`, `window / rolling`) are paired with non-`period_aggregate` temporal gate shapes (`as_of`, `rolling_window`) — neither the verifier nor the chain has been exercised against those substrate-enum values, so cells 9 and 10 are likely to surface temporal-grammar gaps. The `with filter` variants are likely to surface verifier-engine gaps the engine has not been hardened against. The multi-grain `sum` in cell 5 (e.g. cleared_customer_payment_amount on Customer Payment grain) is likely to surface a Canonical Contract authoring gap the framework has only crossed once. Twelve activations across eleven distinct cells covering seven formula shapes and three temporal gate shapes is the minimum honest sample.

The portfolio is not a closeout in the sense of "the framework has been declared closed and may not be reopened." It is a falsifiable target. If the portfolio runs and two metrics needed code patches mid-run, the framework was not yet closed and §3.4 grows with the gaps those patches named.

---

## Source-of-truth references

- Briefing: `bc-docs-v3/docs/implementation/mcf-framework-audit-brief-2026-06-22.md`
- Closeouts re-graded: `bc-docs-v3/docs/implementation/mcf-m2…m13` (12 documents listed individually in §3)
- ADR: `bc-docs-v3/docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422)
- Live MCF substrate state: `bc_platform_dev` schema `mcf` (22 tables; rowcounts captured 2026-06-22)
- Live PE verdict ledger: `mcf.metric_publication_eligibility_result` (147 rows across 7 distinct evaluator versions captured 2026-06-22)
- Live Canonical Contract surface: `contract.canonical_contract_version` where `governance_state_code='active'` (2 active contracts captured 2026-06-22)
