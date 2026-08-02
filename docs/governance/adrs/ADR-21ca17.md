---
uid: DEC-21ca17
title: "Pre-C8 legacy-active disposition — cohort demotion to audit_pending as raw material; named residue; pre-launch stopping condition"
description: "The 257 never-audited pre-C8 legacy actives are dispositioned: 226 demoted active→audit_pending through the governed C7 reintake machinery (executed 2026-08-02, batch 89952e2c, manifest bb8cf013); 31 named residue (unresolvable directory-member identity) remain active pending member minting + a second manifest; disposition must complete before the first real tenant onboards."
status: implemented
date: 2026-08-02T16:52:10.824Z
project: bc-core
domain: metrics
subdomain: metric-lifecycle/certification
focus: lifecycle
---

# Pre-C8 legacy-active disposition — cohort demotion to audit_pending as raw material; named residue; pre-launch stopping condition

## Context

The lifecycle authority study established that the meaning of `active` widened by consumer accretion (F-030) and that the no-grandfathering mandate had been decided twice and lost in supersession twice (F-037). Codex's Phase-1 ratification required the population not be silently called certified nor silently withdrawn. This act is the explicit third option both reviews converged on: recorded cohort demotion into the honest state, with the residue named rather than hidden. Executing while pre-production makes it cheap and reversible-by-certification; the stopping condition prevents the window from silently closing.

## Decision

EXECUTED OPERATOR ONE-TIME ACT (2026-08-02), closing the standing question the lifecycle authority study named F-009/F-024/F-037.

1. THE POPULATION AND ITS MEANING. The never-audited pre-C8 legacy actives — MCVs whose `active` traces to a live D426-era M14 `metric_transition` cert, with no effective audit decision and no live audit-cycle cert — are RAW MATERIAL for the certification lane, not certified-grade actives owing a debt. Operator ruling (recorded in the Phase-1 register at devhub 2481ac2): the population is known-contaminated — the certification mechanics were built because of it — and carries no tenant exposure (dev stage, no active tenants). The state they occupy, not the rows, was the problem: `active` asserts certification under D541; feedstock may not occupy it.

2. THE ACT. Cohort demotion `active → audit_pending` ("awaiting certification" — the state IS the standing class; no new vocabulary) through the EXISTING governed C7 reintake machinery, never a bespoke writer: accepted-manifest authority → pinned members → operator-authorized batch (cohort_scope `eligible_later_batch`, the DB's own closed-vocabulary name for successive eligible batches) → per-member audit_reintake cert + transition_evidence + guarded state flip (migrations 48/53 + C7 backstop). Executed against bc_platform_dev: manifest canonical_set_hash sha256:bb8cf013ff2441b95f7746ad483a53e42b2777c77d3316ae14b4e99088ab7303 (257 members), batch 89952e2c-49bd-44a5-bad7-8987cc5a1816, 226 demoted, policy_version bc-legacy-active-cohort-demotion-v2, certifier anant@selenite.co. M14 metric_transition history untouched (it asserts the 2026-06 publication act, not certification). Post-apply substrate verification: 226/226/226/226 (certs/evidence/batch members/state), total actives 311→85.

3. THE NAMED RESIDUE. 31 members remain active because the member-keyed C7 gate cannot form their accepted tuple: 5 have no directory member (write_off_amount, cleared_customer_payment_amount, cash_collection_efficiency_ratio, total_credit_sales, credit_sales_ratio), 26 have a member without a member_version row. They are pinned in the manifest under excluded cohort `pre_c8_member_identity_unresolvable` with rationale — an auditable record, not silence. Follow-up: mint their directory identities through the governed directory surfaces, then a second small manifest completes the demotion. No gate bypass, no sentinel identities, no DDL widening for their sake.

4. STOPPING CONDITION (a19428 pattern). This disposition — including the 31-residue follow-up — must be COMPLETE before the first real tenant onboards. That event permanently expires the dev-feedstock justification. Operators watching tenancy state have one explicit trigger.

5. RE-ENTRY SEMANTICS. The demoted 226 re-enter `active` only through the D541 certification lane (panel → decision → C8-gated audit_admit), like any other audit_pending member. No mass re-activation path exists or is authorized.

Review trail: bc-core PR #629 (r1 CHANGES REQUIRED — bespoke writer could not satisfy the live gate; r2 recomposed onto ReintakeService; r2-P1 rerun-stability fixed in r3; r4 ACCEPTED WITH BOUNDARY after clone rehearsal). Clone rehearsal on bc_demotion_scratch proved the real triggers end-to-end incl. idempotent rerun (identical hash, 0 re-intakes, 226 proof-reconciled). Authorization artifact: devhub artifacts/metric-audit/DISPOSITION-authorization-pre-C8-legacy-active-2026-08-02.md (sha256 53146af…). Evidence: devhub artifacts/metric-audit/demotion-rehearsal-* (e27c183) + demotion-production-* (0edd90b).
