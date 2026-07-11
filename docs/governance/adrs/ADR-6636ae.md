---
uid: DEC-6636ae
title: "Canonical derivation 'group_sum_where' — grain-group-scoped conditional aggregation for co-located plan/actual fields"
description: "Canonical derivation 'group_sum_where' — grain-group-scoped conditional aggregation for co-located plan/actual fields"
status: decided
date: 2026-07-11T07:05:29.078Z
project: bc-core
domain: data-platform
subdomain: contract-grammar
focus: schema
---

# Canonical derivation 'group_sum_where' — grain-group-scoped conditional aggregation for co-located plan/actual fields

## Context

No rationale recorded.

## Decision

Additive extension of the canonical-v2 derivation grammar (sibling of DEC-585edb/D516, complementing DEC-36913d/D514): new derivation function 'group_sum_where' — evaluated at the GRAIN-GROUP level rather than row-locally. Semantics: for one grain group (all source rows sharing the CC grain key), value = Σ over rows matching a DECLARED raw-field predicate of Σ over the DECLARED raw columns. Declaration shape: inputs = raw {source_table, source_field} columns (the summed columns, e.g. HSL01..16); params = { filter: FilterExpr over raw source fields (same AST as D330 sum_where: eq/ne/in/is_null/and/or/not), absent_as: 'null' | 'zero' }. absent_as declares the no-matching-rows value: 'null' marks scope absence (e.g. an account with no plan rows — enabling is_not_null scope filters downstream), 'zero' declares economic zero (e.g. no actual postings = zero spend). Fail-closed constraints: (1) all summed columns AND every filter field must be observable in the OC so_schema (D431 raw-input observability, same rule as D513/D516); (2) group_sum_where outputs cannot chain into further derivations (D462 1-hop rule unchanged); (3) rows with null/non-numeric column values are skipped within the sum (D516 null semantics). Invariants: meaning (which rows belong to which side, e.g. RRCTY=1 plan vs RRCTY=0 actual) is produced ONCE at the canonical boundary via the declared predicate (Invariant I); the predicate and columns are explicit contract declarations (Invariant IV); evaluation stays within one grain group during resolution — no cross-CO reads, no read-triggered evaluation (boundary-independent rules respected). Motivation: SAP New GL (FAGLFLEXT) stores plan and actual as SEPARATE rows per account; a faithful budget variance requires per-account co-location of plan_amount and actual_amount on one CO row so that scope-matching (variance over planned accounts) becomes an expressible filter instead of an inexpressible semi-join — the gap that blocked budget_variance/attainment/utilization (TSK-1b2852). Also the primitive for future record-type-split substrates (target vs actual, statistical vs operational). Row-local functions (linear_sum, sum_where, classify, fiscal_period_end_date, classify_by_binding) are unchanged.
