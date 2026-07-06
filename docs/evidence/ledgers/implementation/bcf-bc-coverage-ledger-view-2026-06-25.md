---
title: BCF Pass 1 C1+C2 BC Coverage Ledger View (2026-06-25)
description: BC-target-weighted retrospective ledger for C1 and C2. Reframes platform coverage as routing of future Business Concept targets, not only draft characteristic count.
status: generated_ledger_view
authority: bc-docs-v3 SSOT synthesis
date: 2026-06-25
related_docs:
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
  - bcf-oagis-pass-1-c1-operator-decision-packet-2026-06-25.md
  - bcf-oagis-pass-1-c1-closure-checkpoint-2026-06-25.md
  - bcf-oagis-pass-1-c2-closure-checkpoint-2026-06-25.md
---

# BCF Pass 1 C1+C2 BC Coverage Ledger View

> Generated companion view for `bcf-bc-coverage-ledger.json`. The objective is platform coverage: how many future BC targets now have a governed route to a substrate characteristic, an existing characteristic, a future entity-slice dependency, an operator decision, or a rejection/defer bucket.

## Headline

- C1+C2 source rows: **86**.
- C1+C2 BC target references using live A0.5 weights: **256**.
- Addressed BC targets (new substrate/parent-enabled + map_to_existing): **119 / 256 = 46.5%**.
- Draft-count-only view remains misleading: C1+C2 produced **17 program drafts**, but the BC coverage view shows **119 routed BC targets**.

## Coverage Status

### C1

| Coverage status | Rows | BC targets | % of cluster |
|---|---:|---:|---:|
| operator_decision | 1 | 61 | 41.5% |
| addressed | 26 | 61 | 41.5% |
| held_residual | 11 | 23 | 15.6% |
| not_addressed | 2 | 2 | 1.4% |

Addressed coverage: **61 / 147 = 41.5%**

### C2

| Coverage status | Rows | BC targets | % of cluster |
|---|---:|---:|---:|
| addressed | 16 | 58 | 53.2% |
| blocked_until_entity_slice | 21 | 29 | 26.6% |
| not_addressed | 7 | 11 | 10.1% |
| held_residual | 1 | 6 | 5.5% |
| operator_decision | 1 | 5 | 4.6% |

Addressed coverage: **58 / 109 = 53.2%**

### Combined C1+C2

| Coverage status | Rows | BC targets | % of cluster |
|---|---:|---:|---:|
| addressed | 42 | 119 | 46.5% |
| operator_decision | 2 | 66 | 25.8% |
| held_residual | 12 | 29 | 11.3% |
| blocked_until_entity_slice | 21 | 29 | 11.3% |
| not_addressed | 9 | 13 | 5.1% |

Addressed coverage: **119 / 256 = 46.5%**

## Route-Type Detail

### C1

| Route type | Rows | BC targets | % of cluster |
|---|---:|---:|---:|
| operator_semantic_decision_type_root | 1 | 61 | 41.5% |
| new_substrate_or_parent_enabled | 23 | 56 | 38.1% |
| held_residual_panel_or_reprep | 9 | 20 | 13.6% |
| map_to_existing_characteristic | 3 | 5 | 3.4% |
| operator_semantic_decision_held | 2 | 3 | 2.0% |
| defer_or_reject | 2 | 2 | 1.4% |

### C2

| Route type | Rows | BC targets | % of cluster |
|---|---:|---:|---:|
| map_to_existing_characteristic | 15 | 56 | 51.4% |
| operator_semantic_decision_slice_blocked | 21 | 29 | 26.6% |
| defer_insufficient_evidence | 6 | 9 | 8.3% |
| service_error_held | 1 | 6 | 5.5% |
| operator_semantic_decision_scope | 1 | 5 | 4.6% |
| reject_circular_or_generic | 1 | 2 | 1.8% |
| new_substrate_characteristic | 1 | 2 | 1.8% |

### Combined C1+C2

| Route type | Rows | BC targets | % of cluster |
|---|---:|---:|---:|
| operator_semantic_decision_type_root | 1 | 61 | 23.8% |
| map_to_existing_characteristic | 18 | 61 | 23.8% |
| new_substrate_or_parent_enabled | 23 | 56 | 21.9% |
| operator_semantic_decision_slice_blocked | 21 | 29 | 11.3% |
| held_residual_panel_or_reprep | 9 | 20 | 7.8% |
| defer_insufficient_evidence | 6 | 9 | 3.5% |
| service_error_held | 1 | 6 | 2.3% |
| operator_semantic_decision_scope | 1 | 5 | 2.0% |
| operator_semantic_decision_held | 2 | 3 | 1.2% |
| defer_or_reject | 2 | 2 | 0.8% |
| reject_circular_or_generic | 1 | 2 | 0.8% |
| new_substrate_characteristic | 1 | 2 | 0.8% |

## Notes

- The live A0.5 C1 matrix sums to **147** BC targets. A retrospective pasted note used **145**; this generated ledger intentionally follows the live bc-docs-v3 matrix.
- C1 source-row accounting and characteristic-term accounting are not additive. The C1 operator-decision packet explicitly warns that source rows, parent characteristics, and substrate writes answer different questions.
- The largest unresolved coverage lever is still `type_code`: **61** BC targets. The prior operator packet rejected generic `type code`; the coverage lens marks it as a high-impact operator decision if the team wants to reopen root-vs-role strategy.
- C2 proves the need for routing-first preflight: post-panel precision-tail parks were recoverable as map_to_existing rows, but should have been caught before transport.

## Next Use

Use this ledger as Session 2 validation input for the routing-first compiler. The compiler should reproduce these final route decisions for C1/C2 before any C3-C6 panel transport.
