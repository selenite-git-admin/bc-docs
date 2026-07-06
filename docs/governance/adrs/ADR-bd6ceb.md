---
uid: DEC-bd6ceb
title: "Platform M14 activation does not gate on PE-MC-8 default-mode (Model A)"
description: "PE-MC-8 default-mode OPERATOR_REVIEW is PASS-equivalent at M13 approval and platform M14 activation; tenant-runtime-readiness enforcement belongs to M18+/tenant binding."
status: decided
date: 2026-06-09T02:32:42.545Z
project: bc-core
domain: metrics
subdomain: mcf-publication-eligibility
focus: governance
---

# Platform M14 activation does not gate on PE-MC-8 default-mode (Model A)

## Context

No rationale recorded.

## Decision

Lock Model A. PE-MC-8 ("default-pass-pending-m18+") is a tenant/runtime-readiness placeholder, not a metric-package check. Its default-mode OPERATOR_REVIEW verdict is treated as PASS-equivalent by the M13 §4.5 aggregation rule at BOTH the M13 approval transition (draft -> review -> approved) AND the platform M14 activation gate (approved -> active). It therefore gates NEITHER M13 approval NOR platform M14 activation.

Rationale of placement: platform activation establishes the metric definition as canon; runtime-readiness is a tenant-runtime concern enforced at tenant binding (M18+ / MLS-15-25), not at platform activation. Per ADR DEC-c3e57f (D422) Decision 7, eligibility (approved) and activation (active) are distinct layered gates; PE-MC-8 belongs to neither platform gate.

Only a future explicit `operator-reject` mode (PE-MC-8 evidence mode='operator-reject', currently unimplemented per M13 DBCP §4.3 D-M13-10b / R-M13-5) would emit VERDICT_REJECT and block aggregation at both gates. When real runtime-readiness checks land (tenant binding / M18+), they replace the default-pass placeholder at the tenant layer, not at platform M13/M14.

This corrects and supersedes the inaccurate claim in the D434 editorial-rebind DBCP §4 that PE-MC-8 "will continue to block auto-approve" — corrected in the same change set. NO code change is required: the implemented behavior already matches Model A (evaluator runPeMc8RuntimeReadinessIntent + aggregateApproveEligible at M13; McfPublicationActivationController.assertActivationGate / checkPeMc8Verdict at M14).

Consequence for ARPI: the approved successor b1933c30 can be activated (M14) today under Model A with only an operator rationale; no PE-MC-8 acknowledgement or override is required.</decision_text>
<parameter name="rationale_text">Grounded read-only against the SSOT during the D434 ARPI repair. The M13 evaluator (metric-publication-eligibility-evaluator.service.ts: runPeMc8RuntimeReadinessIntent always returns OPERATOR_REVIEW mode='default-pass-pending-m18+'; the §4.5 aggregation treats it as PASS-equivalent) and the M14 controller (mcf-publication-activation.controller.ts: assertActivationGate -> checkPeMc8Verdict accepts default-mode as PASS-equivalent) both treat PE-MC-8 default-mode as non-blocking — intentional and unit-test-locked. The D434 DBCP §4 claim that it "blocks auto-approve" contradicted this and the M13 §4.5 / M14 §6 DBCPs. PE-MC-8 is "runtime-readiness intent" (the MCV declares preconditions M18+ tenant runtime will require); for a platform metric not yet tenant-bound, runtime-readiness is premature, so the correct enforcement point is tenant binding. Model A keeps the platform/tenant boundary clean. The alternative (Model B: platform M14 blocks on PE-MC-8 unless acknowledged) was considered and rejected as conflating a tenant-runtime concern with platform activation; it would also be a net-new code change rather than a correction.
