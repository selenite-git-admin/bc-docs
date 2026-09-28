---
uid: DEC-6fd09d
title: "Evaluation-context inputs: metric variables that take governed fiscal-calendar facts (calendar_context), and fiscal-period rolling windows"
description: "A general calendar_context variable kind (first code window_days = calendar days of the metric's declared window) and a rolling_window in fiscal-period units, both resolved by the evaluation boundary from the governed calendar and recorded in evidence; realizes DEC-fa7c63 D-6 without literals."
status: proposed
governing_task: TSK-b1e89a
related_adrs: [DEC-fa7c63, DEC-83fda0, DEC-ada203, DEC-c48b0f]
date: 2026-09-28T05:52:35.848Z
project: bc-core
domain: metrics
subdomain: metrics/contract-grammar
focus: evaluation-context-inputs
---

# Evaluation-context inputs: metric variables that take governed fiscal-calendar facts (calendar_context), and fiscal-period rolling windows

## Context

DEC-fa7c63 (D631, decided, N = 3) requires DSO = ar_balance / billed(W) × days(W), with days(W) from the governed calendar and never a literal. Today's grammar cannot say that: mcf.metric_variable_binding admits only input / output / constant / metric_input, so a day count can only be a constant (the forbidden literal), and a rolling window in fiscal periods throws ("period-ordinal window predicate pending declaration"). Having a metric snapshot carry calendar facts for another metric to read was rejected as a hidden derivation (Invariant IV). Foundation placement: B (contract grammar) plus D (the evaluation boundary resolves the calendar; the engine compares stamped ordinals only). It is a design act (DEC-c48b0f). The DB change is minimal and reversible: one nullable column and two widened CHECKs. Proven on a throwaway copy of the live table (740 rows validate; the rollback restores byte-identical constraints; the ledger goes applied → rolled_back). Arc PLN-c96901, W9 U9.3b (TSK-b1e89a).

## Decision

**D-1. The window is declared once, on the metric's own temporal gate.** rolling_window gains the unit fiscal_period: {duration: N, unit: fiscal_period} = the N trailing fiscal periods ending with the period that contains P. The evaluation boundary (the orchestrator) resolves, from the governed fiscal calendar (D623, the same calendar rows that fix P), the window's first period as a stamped ordinal (fiscal_year, period_number). The engine compares each candidate's stamped ordinal with [first, P] and never consults the calendar at evaluation (the DEC-83fda0 rule). Day and week units keep today's behaviour.

**D-2. A general calendar_context variable kind.** A metric variable binding may have role_kind_code = calendar_context with a calendar_context_code naming WHICH governed-calendar fact the boundary supplies. It carries no concept, entity, upstream metric, constant or snapshot-selection rule. First and only code today: window_days = the count of calendar days in the evaluating metric's own declared window (D-1), summed from the resolved calendar periods and respecting D623's half-open period boundaries. The code list is general, not DSO-specific: later codes (for example, for DPO and DIO in the coverage arc) are added by widening the same enumeration in their own act. No literal day count is ever a valid substitute.

**D-3. Explicit in evidence (Invariants IV and VI).** Every calendar_context value used by an evaluation is recorded next to the metric inputs in the evaluation's input references: the code, the value, N, and the exact calendar rows (calendar config id, fiscal_year and period_number of each period, their start and end dates). It is an explicit, referenced input, never a hidden derivation.

**D-4. One window, both operands.** For a composite (for example, DSO = ar_balance / billing_W × window_days), the composite's declared window and the upstream flow metric's declared window must be the same N over the same calendar. This is checked at authoring where both are known, and at evaluation from the upstream snapshot's recorded window; a mismatch is refused, not computed (the scope-equality rule of W9 U9.3b).

**D-5. Substrate.** mcf.metric_variable_binding gains one nullable column, calendar_context_code (its 20th column, the DB-rule ceiling), and the role-kind and role-target CHECKs are widened for the new kind: bc-db migration 0024_mcf_variable_calendar_context, with a guarded rollback. N needs no new column: it lives in the existing temporal_gate_params_json of the metric's gate.
