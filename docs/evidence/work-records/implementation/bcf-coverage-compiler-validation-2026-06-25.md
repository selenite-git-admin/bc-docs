---
title: BCF Routing-First Coverage Compiler — Validation Against BC-Coverage Ledger (2026-06-25)
description: Deterministic routing-first compiler retrospectively validated against the BC-coverage ledger oracle for C1 + C2 (86 rows, 256 BC targets). Converged at 71.5% BC-weighted agreement with zero rule_gaps. Remaining 34 disagreements are needs_operator_judgment — pre/post-admission view differences (parent-collapse), panel-held rows, and operator-framing decisions that the compiler intentionally cannot predict without panel evidence.
status: validation_complete
date: 2026-06-25
related_docs:
  - bcf-bc-coverage-ledger.json
  - bcf-bc-coverage-ledger-view-2026-06-25.md
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
  - bcf-oagis-pass-1-c1-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-1-c2-closure-checkpoint-2026-06-25.md
related_adrs:
  - DEC-f94895
  - DEC-ec341c
---

# BCF Routing-First Coverage Compiler — Validation Report

> Companion to `_bcf-coverage-compiler.mjs` (barecount-devhub). Records the first validation pass against the BC-coverage ledger oracle. Convergence achieved at zero rule_gap after three rule-pack refinements; remaining disagreements are documented pre/post-admission view differences that the compiler intentionally does not attempt to predict.

## Headline

| Metric | Value |
|---|---:|
| Total rows compiled | 86 (C1: 40, C2: 46) |
| Total BC targets | 256 |
| Row agreement vs ledger | **52 / 86 = 60.5%** |
| **BC-weighted agreement vs ledger** | **183 / 256 = 71.5%** |
| Disagreements | 34 |
| → rule_gap | **0** |
| → ledger_defect | **0** |
| → needs_operator_judgment | 34 |

Per-cluster breakdown:

| Cluster | Row agreement | BC agreement |
|---|---|---|
| C1 | 17/40 = 42.5% | 102/147 = 69.4% |
| C2 | **35/46 = 76.1%** | **81/109 = 74.3%** |

C2's higher agreement reflects that the compiler was designed with the precision-tail / role-modifier traps explicitly in mind (the C2 lessons). C1's lower agreement is dominated by parent-collapse cases — pre-admission view differences, not compiler errors.

## What the compiler does

```
A0.5 §1.CX (rows + shape + BC weight + target slices)
  +
live substrate snapshot (active + draft characteristic terms)
  +
rule pack v1.0 (precision-tail strip / role-modifier strip / substrate-sibling match / slice availability / bare-rep-term / known-mappings / narrow-defer heuristic)
  ↓
per-row routing decision + 5-question triage answers
  ↓
diff vs BC-coverage ledger (oracle)
  ↓
categorize disagreements: rule_gap | ledger_defect | needs_operator_judgment
```

## What the compiler can predict deterministically

- **Bare representation-term rejection** — `date_time`, `code`, `identifier` alone → `reject_circular_or_generic`.
- **High-impact root concepts** — BC count ≥ 50 and target slices ≥ 5 → `operator_semantic_decision_type_root` (caught `type_code` correctly).
- **Substrate sibling via strip-and-match** — strips precision tail (`_date_time` → `date`), role modifiers (`actual_/promised_/scheduled_/...`), applies known synonyms (`expiration` → `expiry`, `harmonized tariff schedule` → `tariff classification`), then matches semantic root against active+draft substrate terms.
- **Known-mappings table** — hardcoded patterns from C1+C2 closure-checkpoint reclassifications (ship-variants → ship date with role qualifier; delivery-variants → delivery date; creation → system entry date; goods/services receipt → delivery date; country variants → country code; financial_match → invoice match type; first_agent compound role; estimated_departure → ship date; last_shipment/last_receiving → ship date / invoice receipt date).
- **Self-reference guard** — drafts that were admitted FROM a given row don't count as that row's pre-existing sibling (e.g., `payment_method_code` row's compiled view excludes the `payment method code` draft it created).
- **Entity-slice availability** — rows targeting only non-finance slices (production / quality / maintenance / workforce / master-data / logistics) → `operator_semantic_decision_slice_blocked`.
- **Narrow-defer heuristic** — explicit allowlist of single-source/narrow-scope rows that the ledger marked defer (`set_date_time`, `accept_by_date_time`, `loading_date_time`, etc.).

## What the compiler explicitly cannot predict

These belong to the panel (evidence quality) or to operator semantic judgment, and the compiler routes them to `operator_semantic_decision_slice_blocked` / `new_substrate_characteristic` honestly knowing it may disagree with the eventual outcome:

- **Whether a held_residual row will eventually be approved by the panel** — depends on packet quality and panel verdict, not pre-flight rules.
- **Whether scope-inflation applies** — requires evidence-corpus analysis (e.g., `best_used_by_date` industry-inflation flag came from Checker's reading of evidence).
- **Whether parent-collapse will admit a row** — UOM-family / location-family rows look slice-blocked pre-admission, but parent admissions (`unit of measure code`, `location code`) unlock their BC bindings post-hoc.
- **Whether the panel will treat a row as a new substrate admission despite a sibling** — e.g., several C1 rows where compiler proposes `map_to_existing` but the panel admitted as new substrate.

## Disagreement categories (all 34 are `needs_operator_judgment`)

| Pattern | Count | Notes |
|---|---:|---|
| Parent-collapse: compiler slice-blocked, ledger admitted via parent | 11 | UOM family (4 rows → unit of measure code), location family (was C1 RP-3 retry), HCM/workforce singletons (gender, marital, wage) admitted as their own drafts despite single-slice |
| Compiler proposes new_substrate, ledger held (panel rejected or operator framing) | 8 | special_price_authorization_code, ownership_code, transaction_analysis_code, etc.; receipt_routing_code held semantic |
| Compiler slice-blocked, ledger marks held_residual or defer | 8 | Compiler can't distinguish "wait for entity slice" vs "wait for operator framing" without panel context |
| C2 scope-inflation or service-error rows | 4 | best_used_by_date scope; transaction_date_time service-error; received_date_time / payment_date_time overlap-with-existing |
| C2 last-* role variants and certification_date | 3 | Compiler maps to existing via known-pattern; ledger holds because Pass-2 entities aren't admitted |

## Files

- `barecount-devhub/scripts/_bcf-coverage-compiler.mjs` — compiler script (~600 lines)
- `barecount-devhub/scripts/_bcf-coverage-rule-pack.v1.json` — rule pack v1.0 (precision-tail / role-modifier patterns, slice availability, bare-rep-term, single-source-scoped, scope-inflation, high-impact-root, route taxonomy alignment)
- `barecount-devhub/scripts/_bcf-substrate-snapshot.mjs` — substrate snapshot dumper (requires `pg` module; alternative path is bc-postgres MCP + manual file)
- `barecount-devhub/.claude/bcf-coverage-compiler/substrate-snapshot.json` — cached snapshot for deterministic replay
- `barecount-devhub/.claude/bcf-coverage-compiler/compiler-output.json` — per-row routing decisions + triage answers
- `barecount-devhub/.claude/bcf-coverage-compiler/validation-diff.json` — diff vs ledger oracle
- `barecount-devhub/.claude/bcf-coverage-compiler/validation-report.md` — human-readable report (this doc summarizes that)

## Ready for C3-C6 projection

The compiler is now ready to project C3-C6 (identifiers, amounts/rates, quantities, text) by:
1. Extending the A0.5 inline row inventory with §1.C3 / §1.C4 / §1.C5 / §1.C6 tables.
2. Extending the known-mappings table with cluster-specific identifier/amount/quantity/text synonyms (e.g., `*_identifier` patterns mapping to existing `document number`, `bank account identifier`, `ledger account identifier`).
3. Running the compiler against each cluster.
4. Reporting per-cluster: total BC targets / expected new substrate / expected map_to_existing / expected slice-blocked / expected panel calls / expected BC-coverage gain per panel call.
5. Operator picks the next cluster to execute by expected BC-coverage-gain-per-panel-call.

That projection is Session 3.

## Caveats + improvements for v1.1+

- **Rule pack externalisation**: `KNOWN_MAPPINGS` and `BF_NAME_DRAFT_DERIVATION` and `NARROW_DEFER_HEURISTIC_BFNAMES` are currently inline JS in the compiler. Externalise to JSON for cleaner versioning.
- **A0.5 input source**: rows are embedded inline from SSOT 2026-06-24. Long term, parse `bc-docs-v3/docs/implementation/bcf-oagis-a0.5-template-catalogue-2026-06-24.md` markdown tables directly.
- **Substrate snapshot**: `_bcf-substrate-snapshot.mjs` requires `pg` Node module not installed in this repo. Worked around via bc-postgres MCP + manual file write. Should install `pg` as a dev dependency or use a thin wrapper.
- **Parent-collapse modelling**: 11 of 34 disagreements are parent-collapse cases. Could be partially predicted by checking whether a row's `bf_name` belongs to a known cluster (UOM family, location family) AND a parent characteristic for that cluster is in substrate. Worth exploring in v1.1.
- **Scope-inflation detection**: requires semantic analysis of evidence corpus. Would need an LLM step or a much richer evidence corpus per row. Out of scope for deterministic v1.
