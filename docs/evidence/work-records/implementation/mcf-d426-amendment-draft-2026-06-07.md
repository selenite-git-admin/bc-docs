---
title: "DRAFT — D426 Amendment: Clean Single Published Metric-Contract Store"
description: Draft amendment to ADR DEC-3f093f / D426 (MCF Canonicality & Legacy Runtime Boundary). Proposes a single clean published metric-contract store (contract.metric_contract*) with MCF as the governed authoring framework, a raw Postgres seed reservoir, the panel as the enrichment mechanism, and legacy metric/contract data archived then wiped under a DBCP. DRAFT for operator review — NOT a filed ADR; no code, no DB changes; no materialization or wipe until amendment + DBCP are approved.
status: draft
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: catalog
focus: mcf-store-amendment
---

# DRAFT — D426 Amendment: "Clean Single Published Metric-Contract Store"

> **DRAFT for operator review — NOT a filed ADR.** When approved, file via `devhub_decision_record` as a new ADR that **amends DEC-3f093f / D426** (flip/annotate the affected D426 decisions). This draft implies **no code and no DB changes**. **No MCF materialization into `contract.*` and no legacy wipe occur until this amendment AND its implementing DBCP(s) are approved.**

## Context

- **D426 (DEC-3f093f, decided 2026-06-02)** made `mcf.metric_contract*` canonical for new MCs, **forbade** MCF writing legacy `metric.*`/`contract.*`, and contemplated only a future `mcf → NEW shadow` projection. Its goal was **anti-contamination**.
- **Operator direction (2026-06-07)** + the **panel-side-enrichment experiment** (`mcf-enrichment-experiment-2026-06-07.md`: E2 validated — the panel self-enriches from thin seeds) make a **single clean published store** the more maintainable way to reach the *same* anti-contamination goal. The wording is deliberately **"clean single published metric store," never "reuse legacy."**
- This amendment **changes the store mechanism**; it does not weaken D426's intent.

## What this amendment locks

1. **MCF = governed authoring framework.** Intake → M12 panel → PE-MC eligibility → certification → lifecycle. Unchanged in spirit; this is the irreducible MCF value.
2. **`mcf.seed_metric` = operational candidate reservoir** (raw Postgres), refreshed from `bc_seed.seed_metrics` (12,501) via a **governed import with count/hash/sample parity**; **Mongo / export = preserved upstream seed archive**; **MCF intake/runtime reads Postgres, not Mongo**. Raw/thin — *not* a new enriched catalog. (Per `mcf-seed-reservoir-postgres-design-2026-06-07.md`.)
3. **Panel = the enrichment mechanism.** Validated 2026-06-07: the panel self-enriches from a thin seed via BCF tool calls. **No batch pre-enrichment pipeline (E1) is adopted.** `metric_knowledge` is not required as a candidate source.
4. **`contract.metric_contract*` = the single clean published runtime metric-contract store (after clean-slate adoption).** Published MCs **materialize here**; the existing runtime engine consumes it **unchanged**. *(Document status is draft/proposed; the target architecture above is the decision — not conditional.)*
5. **Legacy metric/contract data archived/exported, then wiped under a DBCP** (golden snapshot + rollback) — *not before*. The wipe makes `contract.metric_contract*` a genuine clean slate (today: 780 headers / 2 active, 731 active versions — quarantine is moot once deleted).
6. **`metric_knowledge` preserved as historical reference, not future authority.** The 1,241 AI-enriched rows are **expensive historical work**: archive/export (PG dump and/or S3 JSONL) before any wipe; retained as reference/evidence only.
7. **Runtime engine remains UNCHANGED.** It already reads `contract.metric_contract_version.contract_json` → `progression.metric_evaluation` → typed `fact.*`. No engine logic change; materialization simply produces the contract rows it already consumes.
8. **D400 (grammar v1.1), D401 (open-item canonical), D427 (references) remain SEPARATE gates** — not resolved here. The enrichment experiment showed predicate/filter/as-of metrics correctly route to OPERATOR_REVIEW for *loose grounding* — those are grammar/filter/reference gaps, **distinct from enrichment**, and addressed on their own tracks.
9. **No MCF materialization into `contract.*` and no legacy wipe** until this amendment **and** the implementing DBCP(s) are approved.

## Relationship to D426 (what flips on ratification)

| D426 (decided) | This amendment |
|---|---|
| `mcf.metric_contract*` canonical; no legacy writes; future `mcf→shadow` only | `contract.metric_contract*` = single clean published store; MCF **materializes into it**; legacy **archived + wiped** |
| Legacy is the wired runtime (don't disturb) | **Kept** — runtime engine unchanged; legacy *data* is replaced by clean MCF-published rows in the same store |
| Anti-contamination via **separation** | Anti-contamination via **single clean store + single writer (MCF) + legacy quarantined-then-deleted** |

Same goal; more maintainable mechanism. On ratification: flip/annotate the affected D426 decisions and update `mcf-re-entry-index.md` §1 authority stack.

## Operator-locked sequence (2026-06-07)

1. Commit/fix re-entry docs *(done: `27b956e`, `acf7bb6`)*.
2. Novel thin-seed confirming run *(done: `panel_run 088e22f9`)*.
3. **This amendment** → ratify via `devhub_decision_record`.
4. **Gate 0** — create/import/wire the Postgres `mcf.seed_metric` reservoir (`mcf.seed_metric` DBCP + import from the Mongo/export seed archive **with count/hash/sample parity** + adapter repoint + ingest route, function-scoped) + live ingest→panel test.
5. Build **MCF materialization** into clean `contract.metric_contract*`.
6. **Only then wipe/reseed** — golden snapshots + rollback.

## Guardrails

- **No code. No DB writes. No wipe. No materialization.** Until amendment + DBCP approved.
- Wording discipline: **"clean single published metric store,"** never "reuse legacy."
- This draft is a finding/decision artifact; canonical MCF authority remains DEC-c3e57f/D422 + DEC-3f093f/D426 (as amended) + the build plan.
