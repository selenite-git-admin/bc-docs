---
uid: PLAN-pilot-e2e-readiness-2026-07-01
title: "Pilot E2E Readiness — Consolidated Plan"
description: "Single master plan tying the two governance-parity programs (metric evaluation boundary + UniBAT Reader boundary) into a sequenced path to the first pilot E2E: fine-tuned SDG → pilot1 → the active AR-family metric suite → Metric Snapshots. Consolidates the state, the precise pilot target (31 base metrics reachable by binding BSAD+KURGV), the critical path, and the ADR sequences."
status: active
authority: plan
date: 2026-07-01
project: bc-core
domain: platform
---

# Pilot E2E Readiness — Consolidated Plan

## 0. The goal

**First pilot E2E:** a fine-tuned SDG feeds `tbc_pilot1_dev` → the UniBAT Reader admits AR source data → Source Objects → Canonical Objects → the active AR-family metric suite → Metric Snapshots. The chain is `SDG → Reader → SO → CO → Metric → MS`. For it to *mean* anything, every boundary must be at governance parity, and the chain must be coherent per source entity.

## 1. Where we are (state, 2026-07-01)

### Two governance-parity programs, both studied + independently audited
- **Metric evaluation boundary** — study `metric-evaluation-boundary-governance-parity-study-2026-07-01.md`, ADR **DEC-5ea578 (D472)**. The pure core is **built + live-proven + Codex-audited-and-hardened**: run object, admissibility deferral, atomic idempotent persistence, period stamping, concept-identity binding resolution, spec assembly. The loader loads **19/51** active metrics to runnable specs against live substrate (rest fail-closed). Branch `feat/mcf-as-of-authoring` (bc-core `96ca3907..ad2d69ad`). **Remaining: SS3** (entry orchestration + Nest module wiring + end-to-end).
- **UniBAT Reader boundary** — study `reader-boundary-governance-parity-study-2026-07-01.md`, two axes, double-Codex-audited. **Part 1 (runtime):** governed admission gate over an organically-evolved runtime; pre-pilot gaps = admission-run resumability/idempotency + flavor active-gating. **Part 2 (authoring):** no governed creation surface (thin CRUD + seed); the OC is under-modeled (single flavor field, 0 wired) and must be **per-entity**. Slice-0 baseline test restored (bc-core `56093f64`, branch `feat/reader-boundary-slice0`).

### The precise pilot target (quantified)
- **All 51 active metrics are AR-family** (35 `accounts_receivable` + 3 `billing` + 13 `credit_and_collections`) → `accounts-receivable-reader` is the AR-family container.
- The AR metrics bind **10 distinct concepts, all 10 covered by active OCs**. Concept-observability: **31 RESOLVABLE, 1 BLOCKED** (`average_clearance_time`), **19 NO-CONCEPT** (composites → ADR #3).
- **The gap is a small reader-admission misalignment:** the 10 concepts come from `BSAD` (7), `TYPE_SD_S_MAP` (3), `KURGV` (1). The reader binds `TYPE_SD_S_MAP` but **not `BSAD`/`KURGV`**, and binds 7 entities providing zero needed concepts.
- **Corrected target:** bind `BSAD` + `KURGV` + wire their per-entity OCs → **31 base AR metrics resolvable**; composites follow (ADR #3); only `average_clearance_time` needs an OC.

## 2. The critical path (dependency order)

```
[P0 verify open/cleared] → [P1 Reader: authoring surface + admit BSAD/KURGV + per-entity OC + runtime resumability]
    → [P2 Metric: SS3 loop closure] → [P3 pilot1 bring-up + SDG fine-tune] → [P4 SDG E2E: 31 base metrics]
    → [P5 second wave: composites (ADR #3) + average_clearance_time OC + temporal model (ADR #2)]
```
Data flows entry→exit, so the Reader (P1) precedes the metric loop's real feed; SS3 (P2) can be built in parallel on constructed COs. The whole E2E needs P1 + P2 + P3.

## 3. Execution phases

### P0 — Verify (gates the target) — ✅ DONE, PASSED (2026-07-01)
- **Open/cleared semantic — correct; the 31-metric target holds.** Two families, verified separately (precision corrected per Codex F2):
  - **Clearing-date / open-at-P family** (`ar_balance`, `ar_aging_*`, open-invoice-count) — PROVEN. `as_of` with `closing_field=clearing_date` over `BSAD` computes open-at-P (an item now cleared *was open* at any P before its `clearing_date` — the SAP bitemporal pattern). `BSAD` supplies `BLDAT→document_date`, `AUGDT→clearing_date`, `WRBTR→gross_amount` directly. `BSAD` is the correct source; the reader's `BSID` binding is vestigial.
  - **Due-date-anchored family** (`overdue_*`, past-due, days-delinquent) — depends on a DERIVED canonical field, not a raw column. Active `cc__customer_invoice_arpi_slice` v8 derives `due_date = date_add(posting_date, net_payment_term_days)`; `BSAD` supplies the inputs (`BUDAT→posting_date`, `ZBD1T→net_payment_term_days`). Latent redundancy to reconcile in the AR OC-authoring pass: `oc__receivable_posting_bsad`'s `ZFBDT→"due date"` is a baseline-vs-due mislabel — the authoritative due_date is the CC derivation.
- **Residual nuance (scoping, not a fix):** `BSAD` = cleared history, complete for a **closed historical pilot period**. Currently-open items live in `BSID` (no OC) — a *current*-period pilot would undercount open AR and would need a `BSID` OC. **Pilot first-target = a closed historical period**, where `BSAD` is complete.

### P1 — Reader foundation (the governed entry)
- **ADR — Reader authoring surface & the four-layer model** (per-entity `(flavor, source_entity) → OC` binding + completeness + chain-resolvability activation gates + the 6 policies). *The most foundational ADR.* Design-first, then DBCP for the per-entity OC table.
- **Align AR admission through the surface:** bind `BSAD` + `KURGV`, wire per-entity OCs (`TYPE_SD_S_MAP`, `BSAD`, `KURGV`), pin the AR flavor, pass the resolvability gate.
- **ADR — Admission-run resumability & idempotency** (port the metric-run pattern; **pre-pilot**).
- Flavor active-gating + the reader-evidence completeness + status-honesty items (Part 1 §9 ADRs) — resumability is pre-pilot, the rest can trail.

### P2 — Metric loop closure (parallelizable)
- **SS3** — entry orchestration (`loader → listCanonicalObjects → fiscalCalendar period → evaluate → persist`) + Nest module wiring (provide `GOVERNED_METRIC_PERSISTENCE`). Provable on constructed COs (rollback integration test) independent of P1.
- **SS1b integration transaction test.** Loader `tenantId → tenantSlug` naming (Codex P3).

### P3 — pilot1 bring-up
- `pilot1` AR reader binding (env), fiscal-calendar config for `pilot1` (D364/D368), tenant provisioning.
- **SDG fine-tuning** for AR: emit `BSAD` / `KURGV` / `TYPE_SD_S_MAP` shapes that admit into valid SOs (SDG conforms to the SC/AC — SDG-blind).

### P4 — The SDG E2E (the culminating test)
- Run `SDG → Reader → SO → CO → 31 base AR metrics → MS` on `pilot1`. Verify snapshots + evidence. This is the pilot's honest first claim: **31 base AR metrics end-to-end**.

### P5 — Second wave (post-base)
- **ADR #3 — composite (metric DAG) execution** → the 19 NO-CONCEPT composite metrics (DSO, CEI, ratios).
- `average_clearance_time` — author the 1 missing OC.
- **ADR #2 — the metric temporal model** — the per-input period predicate (multi-period `period_aggregate` correctness; today single-period-scoped candidates are the caller precondition).

## 4. Parallel ADR sequences

**Metric boundary (DEC-5ea578 sequence):** #1 wiring ✓(core) · #2 temporal model + admissibility · #3 composite DAG · #4 evidence + serving · #5 error taxonomy + rule book · #6 change-safety · #7 observability · #8 orchestrator.

**Reader boundary (new sequence):** #R1 authoring surface + four-layer model (per-entity OC + gates) — **filed: DEC-17112b (D473), `proposed`, design-only** · #R2 admission-run resumability/idempotency · #R3 reader evidence + version stamping · #R4 run-status honesty + failure taxonomy.

The pilot's critical path touches: metric #1 (done) + SS3, and Reader #R1 + #R2. The rest are governance completeness, not pilot blockers.

## 5. Risks & gates

- **G-semantic (P0):** ✅ CLEARED — open-vs-cleared verified correct (BSAD via `clearing_date` as_of = open-at-P). The residual is scope, not mismatch: pilot first-target = a **closed historical period** (BSAD complete); a current-period pilot would need a `BSID` OC.
- **G-resumability (pre-pilot):** a partial-admission run with no idempotent re-admission is a data-trust hazard in a real pilot; #R2 lands before the pilot ships, not just before the E2E test.
- **STOP AT CHAIN INTEGRITY** is deliberately *lifted* for pilot bring-up (P3/P4 mint real SOs/COs/MSs on `pilot1`) — that is the pilot, and it is expected.
- **SDG-blindness** must be preserved everywhere (SDG conforms to SC/AC; no SDG-awareness in Reader/engine/evidence).

## 6. Committed state & branches

- bc-core `feat/mcf-as-of-authoring` — metric boundary (Change A, SS1, SS1b, SS2a/b, audit fixes), `96ca3907..ad2d69ad`, pushed.
- bc-core `feat/reader-boundary-slice0` — Reader Slice-0 baseline test, `56093f64`.
- bc-docs `docs/the-governed-selection` — both studies + this plan + ADR-5ea578, pushed.
- ADR **DEC-5ea578** filed (`proposed`, metric boundary). ADR **DEC-17112b (D473)** filed (`proposed`, Reader #R1 authoring surface — design-only). Reader ADRs #R2–#R4 not yet filed.

## 7. Recommended immediate next step

**P0 is done and passed (§3).** The 31-metric target is confirmed sound. The two parallelizable fronts now open:
- **P1 — Reader authoring ADR (#R1) + BSAD/KURGV admission alignment.** The most foundational ADR (per-entity `(flavor, source_entity) → OC` binding + resolvability activation gate + the 6 policies), then DBCP for the per-entity OC table, then bind `BSAD`+`KURGV` and wire their OCs.
- **P2 — SS3 metric-loop closure.** Provable on constructed COs independent of P1.

Recommended order: start **P1** (it's the critical-path entry the pilot feed depends on and the larger design surface) while **P2** proceeds in parallel. Pilot period target = a **closed historical period** (P0 nuance).
