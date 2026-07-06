---
uid: DEC-0f15a7
title: "date_add — additive D330 compute function for net-due-date derivation"
description: "date_add — additive D330 compute function for net-due-date derivation"
status: decided
date: 2026-06-29T15:28:06.616Z
project: bc-core
domain: contracts
subdomain: contracts/canonical
focus: derivation-grammar
---

# date_add — additive D330 compute function for net-due-date derivation

## Context

No rationale recorded.

## Decision

Add date_add(base, days[, unit=days]) → date to the D330 derivation compute library, per D330-R3 (the library grows additively by ADR only). Implemented in compute-evaluator.ts (evalDateAdd + validateComputeSpec case + COMPUTE_FUNCTIONS) and the canonical-v2 schema derivations function enum. Inputs: role 'base' (a 1-hop directly-observed date BC) + role 'days' (a 1-hop directly-observed integer BC, OR a params.days constant); output_type 'date' (ISO YYYY-MM-DD); unit 'days' in v1. Purpose: enables due_date = date_add(baseline_date, payment_terms_days) as a 1-hop CC derivation (D462) on cc__customer_invoice_arpi_slice → unblocks three collections-delinquency metrics: Average Days Late (AVG(clearing − due)), overdue amount, overdue count. 6 unit tests added (compute-evaluator.spec.ts, 57/57 green). The OC must first observe ZFBDT (baseline) + ZBD1T (payment-terms days) — they exist in the source (SDG generates them) but are not yet mapped by oc__customer_invoice_cleared_item_bsad.</decision_text>
<parameter name="rationale_text">Net due date = baseline date + payment-terms days is the standard AR due-date computation. Deriving it at the canonical boundary from stamped inputs keeps the meaning produced once (Invariant I) and portable — any source providing a baseline date + payment terms yields due_date via the same date_add, with no metric-level or source-level compensation. date_diff/date_diff_as_of existed (date subtraction) but there was no date addition; date_add is the additive complement. The alternative (a precomputed net-due-date source field) bakes the computation into the source and is less portable. D330-R3 requires compute-library growth to be ADR-governed; this ADR is that governance.
