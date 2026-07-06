---
uid: DEC-26f75a
title: "period_aggregate anchor_field — event-date period membership for flow metrics (temporal grammar ADR #2)"
description: "period_aggregate gains optional anchor_field (event-date period membership); default = stamped posting fiscal_period; fixes the clearing-date-declared flow metrics (audit SES-b54f06); completes the D472-deferred ADR #2"
status: decided
date: 2026-07-03T01:05:28.857Z
project: bc-core
domain: metrics
subdomain: metric-runtime/temporal-grammar
focus: temporal-gate
---

# period_aggregate anchor_field — event-date period membership for flow metrics (temporal grammar ADR #2)

## Context

SES-b54f06 audited all 82 active finance MCVs and independently recomputed values: metrics declaring clearing-date-in-period semantics evaluate on posting fiscal_period because period_aggregate has no way to say which date defines membership — the engine comment itself names this the deferred ADR #2. The grammar fix is minimal (one optional param, symmetric with as_of's existing anchor vocabulary), the engine seam already exists (period bounds returned by the fiscal calendar; scoping isolated in CoCandidateReader), and the default preserves every existing MC bit-for-bit. Alternatives rejected: (1) stamping a second clearing-fiscal_period column on COs (E-layer compensation, meaning moves out of the contract); (2) per-metric read filters (F, prohibited); (3) D400-style per-variable input_selection (heavier; this defect is per-METRIC population membership, not per-variable frames — D400 remains the balance-metric arc). Recorded as proposed for operator lock; engine implementation and the M15 re-mint wave follow separately.

## Decision

The `period_aggregate` temporal gate gains one OPTIONAL declaration parameter, `anchor_field`, completing the per-gate period predicate that DEC-5ea578 (D472) explicitly deferred ("ADR #1 identity gate — the per-input period predicate is ADR #2's").

**B (grammar).** `temporal_gate_params_json` for `period_aggregate` may declare `anchor_field`: the canonical date field of the grain CC whose value must fall within the evaluation period for a CO to be a member of the metric's population. Absent (default) = membership by the canonical-resolution-stamped `fiscal_period` (posting-period; today's behavior — every existing MC is untouched). This mirrors the `as_of` gate's existing `anchor_field`/`closing_field` vocabulary: one grammar word, one meaning — which declared date field anchors temporal membership.

**D (engine).** CoCandidateReader's period-scoping (the documented ADR-#1 interim, co-candidate-reader.ts) becomes: when the gate declares `anchor_field`, scope candidates by `periodStart <= payload[anchor_field] <= periodEnd` (bounds already returned by FiscalCalendarService.resolve — FiscalPeriod.periodStart/periodEnd); otherwise keep the stamped-fiscal_period equality. No change to as_of, no change to selection rules, no change to snapshot writing.

**Validation (activation-time).** A `period_aggregate` MC declaring `anchor_field` must reference a date-typed field present in the grain CC's resolved_schema; validated in the publication-eligibility family (extends the PE-MC-14 alignment style). Fail-closed: an unresolvable anchor_field blocks activation, never silently degrades to posting-period.

**Remediation path (NOT this ADR's implementation).** The four audit-confirmed mis-bucketed MCs — cleared_invoice_amount, paid_customer_invoice_gross_amount, paid_customer_invoice_count (AR), paid_supplier_invoice_amount (AP) — declare clearing/paid-in-period in prose but evaluate on posting-period (SES-b54f06 evidence: FY2025-26/P06 snapshot 19,019,959.32 = posting-period total vs 19,123,415.79 clearing-in-period). They are re-minted with `anchor_field: clearing_date` in the same supersession wave as the CB-013/CB-016 document-kind re-mint (TSK-b96796) — both gated on M15. cleared_customer_payment_amount is included for declaration hygiene (DZ clearing==posting makes it numerically indistinguishable today).

**Foundation gate.** Repair location B+D. Why here: the contract cannot currently express event-date membership (B underspecified), and the boundary's scoping is a declared interim (D). Why not upper: source emits correct clearing dates; mappings sound. Why not lower: bucketing corrections at SDG (A), fact rows (E), or read filters (F) are Invariant-I compensation and prohibited. Invariants: I satisfied (meaning declared at B, evaluated once at D); III untouched (existing snapshots remain; corrections arrive as new MC versions via M15); IV strengthened (anchor_field is an explicit declared reference, validated fail-closed); V/VI unchanged.
