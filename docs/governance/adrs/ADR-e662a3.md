---
uid: DEC-e662a3
title: "Demo-plane proof-grid dispatch by the runtime's actual currency partition; a non-currency-partitioned metric (count) proves on the (legal entity, period) grid"
description: "The demo Demoed proof selects its grid from the runtime's actual currencyPartition(spec); a count (empty partition) proves on the (legal entity, period) grid on the non-ccy OracleReferee lane, with an LE-period-on-5.1.0 emit sibling. Supersedes DEC-49b574, which the engine dry-eval reversed."
status: decided
date: 2026-11-10T03:39:02.571Z
project: bc-core
domain: metrics
subdomain: contracts/metric-demo-plane
focus: runtime-dispatch
supersedes: DEC-49b574
---

# Demo-plane proof-grid dispatch by the runtime's actual currency partition; a non-currency-partitioned metric (count) proves on the (legal entity, period) grid

## Context

The build-phase engine dry-eval (SES-8eb1f5, #1040 preflight) empirically reversed ruling (A) of the prior count-proof memo and its PROPOSED companion DEC-49b574, which held that a `document_currency` COUNT partitions by currency (via the assembler) and proves on the v5 currency grid. At source (bc-core `811744df`), `isCurrencyDenominated(spec)` is false for a count (its only variable is `temporal_anchor`), so `currencyPartition` returns `[]` and the runtime yields a single un-keyed grain (69), not 63/6; the assembler's `currencySnapshotKey` keys the snapshot identity on policy alone and disagrees with the runtime, which wins at evaluation. Dispatching the proof grid from the runtime's own `currencyPartition` makes the oracle grid equal the evaluated grain by construction and is robust to the spurious `aggregation_currency_code`.

Codex design review (gen-5c2892, Lane: platform) accepted the direction across its 2-round cap; the two findings it raised (the #1040 referee's currency-coupling; the header-vs-line posted-state predicate) were verified at source and corrected in `ed218ece`. The operator accepted the corrected memo directly (recorded decision relayed by Chief SES-7decb4, option A — direct acceptance, no reopen grant, no round 3).

This ADR **extends** DEC-e8dd2d (oracle-authoring provenance / the non-ccy `OracleReferee` lane) and **consumes** DEC-1bb88e act D (res.currency normalization — the count does not use the currency join) and act H (the metric-version world binding). It **supersedes** PROPOSED DEC-49b574. The revised D1–D5 build delta is a separate builder unit commissioned from this ADR; #1040 is untouched here. Foundation gate (DEC-79b62f): repair location F (the proof grid/dispatch) mirroring the engine's B/D output shape — the grid follows the runtime's partition, never imposes one; no lower-layer compensation; invariants I/IV/VI preserved.

## Decision

The demo-plane Demoed proof selects its cell grid from the metric's ACTUAL runtime partition — `governed-metric-runtime.currencyPartition(spec)` — never from the metric declaration, the `metric-spec-assembler.currencySnapshotKey`, or the plane's CC-version alone. When `currencyPartition(spec)` is non-empty (document_currency policy with a currency field) the proof uses the (legal entity, ISO currency, period) v5 grid; when empty (a unitless COUNT; also a `single_currency_required` or `local_currency` SUM) it uses the currency-agnostic (legal entity, period) grid. Because the dispatch selector IS the runtime function that shapes the evaluated grains, the oracle grid and the engine's evaluated grain can never disagree; a spec whose partition neither grid represents is refused by name.

Realised as the corrected D1–D5 design at barecount-devhub `artifacts/architect/DESIGN-count-proof-grid-and-dispatch-correction-2026-11-10.md` @`ed218ece` (sha256 `60728e48`):

- **D1** — bc-core dispatch (`demoProofEmitRoutineFor` + the e3 CLI) selects the grid from `currencyPartition(spec)`.
- **D2** — the LE-period computor carries an inverse grain guard: refuse by name any grain carrying a `currency_code` (symmetric to `currencyOfGrain`).
- **D3** — a bc-db 0059-sibling `demo.fn_emit_demo_proof_period_v5`: the LE-period emit on the 5.1.0 CO store `demo.co_cc_das36_v5_1_0` with the same-plane lineage/custody/privilege/catalog gates, reusing the existing `demo.oracle_custody` / `ms_snapshot` / `metric_proof_pin` (the existing `fn_emit_demo_proof` is hard-wired to the 4.0.0 store).
- **D4** — the LE-period count oracle is authored on the NON-ccy `OracleReferee` / `DemoOracleAuthorService` lane → `demo.oracle_custody` (not `AdmittedSoCcyReferee`/`oracle_custody_ccy`). The recompute is `count(*)` over the invoice-HEADER basis `moves = demo.so_sc_929yc_v1_0_0` with `move_type='out_invoice' AND state='posted'` (the header posted-state column; NOT the line `parent_state`, which would overcount), per (legal entity, period), with no res.currency join/GROUP BY so a currency-less invoice is still counted; set-equality against the metric's evaluated invoice population is proven BEFORE any custody row is authored. The dry-eval value 69 is a candidate, not a verified oracle until that recompute succeeds.
- **D5** — the #1040 G1 recipe `compileLeaf` needs an LE-period variant (drop the res.currency join + ISO GROUP BY); the `count_rows` strategy is retained with the currency-free grain shape.

Two non-blocking governed corrections, out of scope here and owned by the metric controller (never a DB row edit): (a) `customer_invoice_volume` (mcv `7285ce98`) declares `aggregation_currency_code=document_currency` on a unitless count — a declaration defect (contradicts the output); correct via a governed MCV successor to `not_applicable`. (b) the count MCV pins Customer-Invoice entity version `127c57af` while cc-das36/AR pin `bfc739fe` (same entity `e3963e45`, identical definition) — no proof impact; reconcile via a governed re-pin. Separately, bc-core engine hardening: align `metric-spec-assembler.currencySnapshotKey` to `isCurrencyDenominated` so served `ms_*` snapshot identity and runtime partition agree for counts.
