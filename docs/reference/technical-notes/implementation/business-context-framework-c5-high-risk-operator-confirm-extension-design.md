---
uid: business-context-framework-c5-high-risk-operator-confirm-extension-design
title: Business Context Framework — C5 high-risk Registry operator-confirm extension design note
description: Design note for the C5 extension that gives the Registry-shape certification path a high-risk tier — an operator-confirm fork on issueRegistryShapeCertification, so a high-risk Registry authoring operation is confirmed by an operator rather than auto-issued under deemed approval or refused. Prerequisite for F4-v2 governed vocabulary expansion. Specification only — design-only, no code.
status: accepted
date: 2026-05-22
project: bc-docs
domain: contracts
subdomain: framework-approval
focus: governance
---

# Business Context Framework — C5 high-risk Registry operator-confirm extension design note

> **What this is.** A design note for the **C5 high-risk tier** — the
> operator-confirm fork on the Registry-shape certification path
> (`FrameworkApprovalService.issueRegistryShapeCertification`). Today that path
> auto-issues a *low-risk* Registry authoring operation under deemed approval
> (Model C) and **refuses** anything high-risk. This note designs the fork that
> turns a high-risk Registry operation into an operator-confirmed issuance
> instead of a refusal. It is a **design note, not an ADR** — it elaborates
> DEC-02f5a9 (B6 Model C risk tiering, D3/D4) and DEC-149ab2 (BCF Framework
> Approval). It is the **prerequisite** for the F4-v2 governed-vocabulary
> expansion note: F4-v2's `registerCharacteristic` is the first high-risk
> Registry operation, and it cannot be issued until this fork exists.

## Scope

This note covers the high-risk fork on the Registry-shape certification path
and the operator-confirm seam that completes it. It does **not** cover the B6
panel, the recommendation validator, the orchestrator, F3, or the
characteristic vocabulary — those are F4-v2's note. It changes no contract
grammar and no Foundation invariant. It is design-only: no code, no branch, no
DDL is proposed here.

## 1. Current state — the Registry path has no high-risk tier

`FrameworkApprovalService.issueRegistryShapeCertification` is the C5 path that
turns a B6 panel `APPROVE_FOR_DRAFT` into a Registry-shape `certification_record`
(DEC-02f5a9 Model C, "deemed approval"). Today it does exactly two things:

- **Low-risk → auto-issue.** It runs the vocabulary-agnostic panel-evidence
  checks (panel found / stage `authoring` / grounding pass / verdict
  `APPROVE_FOR_DRAFT` / `policy_version` match), resolves the active `registry`
  `framework_policy`, and writes one born-null Registry-shape cert row with
  `gate_results_json.deemed_approval.disposition = 'auto_issued'`.
- **Anything else → refuse.** If the active `registry` policy carries **any**
  operator-confirm rule, it returns `not_issued` with reason
  `operator_confirm_rules_present` — "B6-S1 deemed approval requires zero". The
  service comment names this explicitly: *"the high-risk operator-confirm tier
  is the later C5 extension fork."*

The risk tier is already a locked, intrinsic property of the action code.
`classifyRegistryRiskTier` (`framework-approval/types.ts`) returns `low` only
for `REGISTRY_LOW_RISK_ACTION_CODES = ['registry_create', 'registry_add_version']`
and `high` for every other `registry_*` action code — **including
`registry_author_vocabulary`** (characteristic authoring). B6-S1 deliberately
enabled the low-risk tier only.

**The machinery for an operator confirm already exists — on the other C5 path.**
The BF/BO `decide()` path carries the full pattern: `OperatorConfirmPort`
evaluation (C6), the `confirm_required` / `operator_review` / `no_match`
outcomes, `confirmOperatorConfirm()` re-entry (C7), `gate_results_json.operator_confirm`
provenance, and the stale-rule re-confirm guard (Invariant V — non-replayable).
The Phase A Bucket-1 DBCP already extended `operator_confirm_rule.scope` to
admit `registry`. This note **ports that proven pattern** to the Registry-shape
issuance path; it does not invent it.

## 2. The high-risk fork

A high-risk Registry operation becomes a **two-step issuance**: the panel
proposes, then an operator confirms. The panel run and the operator confirm are
two distinct human-gated acts — the confirm is never the panel re-running.

### 2.1 First call — `issueRegistryShapeCertification` returns confirm-required

When the requested operation is high-risk (`classifyRegistryRiskTier(actionCode)
=== 'high'`), the path runs the same panel-evidence checks, then **forks**:

- **Low-risk** — unchanged. Auto-issue, `disposition: 'auto_issued'`.
- **High-risk** — the path does **not** write a cert row. It returns a new
  outcome kind, `operator_confirm_required`, carrying the `panelRunUid`, the
  `actionCode` / `subjectKind`, the governing `registry` policy identity, and a
  confirm deadline. No `certification_record` exists yet — there is nothing for
  F3 to verify, so F3 cannot write, so the Registry stays unchanged until the
  operator acts.

The current `operator_confirm_rules_present` refusal is **removed for the
high-risk tier**: a high-risk operation is *expected* to need a confirm, so the
presence of operator-confirm rules is no longer a reason to refuse — it is the
reason to fork. (For the low-risk tier the zero-rules expectation is retained:
a low-risk action governed by a policy that carries confirm rules still routes
to the confirm fork rather than auto-issuing — fail-safe, never auto-issue past
an unmet rule.)

### 2.2 Second call — `confirmRegistryShapeCertification` issues the cert

A new service method, `confirmRegistryShapeCertification(input)`, is the
operator-confirm seam — the Registry analogue of `confirmOperatorConfirm`. It
takes the `panelRunUid`, the confirming operator's Cognito `sub`, and an
operator rationale (DTO-validated ≥ 40 characters, mirroring C7 and the D366
override pattern). It **re-enters** the issuance:

- **Duplicate-cert guard — fail closed.** Because the first high-risk fork
  writes no pending row, a confirm has no pending row to consume — so the
  confirm method must itself refuse a second issuance. Before any write it
  asserts that **no Registry-shape `certification_record` already exists** for
  the same `(panel_run_uid, action_code, subject_kind)` tuple. If one does — a
  retry, a double-click, two operators racing — the confirm fails closed: no
  second cert row is written. One panel run authorizes one Registry write.
- It re-runs **all** panel-evidence checks (Invariant V — non-replayable): a
  confirm that arrives after the panel evidence has changed can legitimately
  now yield `not_issued`. A confirm is not a replay token.
- On all-pass it writes the born-null Registry-shape cert row, with
  `gate_results_json.deemed_approval.disposition = 'operator_confirmed'` (not
  `auto_issued`) and a `gate_results_json.operator_confirm` block. Because v1
  confirmation is **risk-tier based, not rule-predicate based**, the block
  records: the confirming `sub`, the rationale, the timestamp,
  `basis: 'registry_high_risk_action_code'`, and the `action_code` /
  `subject_kind`. `rule_uid` is **omitted (null) in v1** — it is populated only
  once an actual `operator_confirm_rule` predicate is evaluated (the deferred
  enrichment, C5-HR-7). This is the honest evidence that an operator confirmed,
  and on what basis (Invariant VI — evidence emitted, not inferred).

The cert row that results is identical in shape to a low-risk auto-issued cert;
only the `gate_results_json` disposition distinguishes how it was approved. F3
verifies and stamps it exactly as today — F3 needs no change.

### 2.3 Rule-predicate evaluation deferred

The BF/BO path evaluates `operator_confirm_rule` predicates to decide *whether*
a confirm is required. For the Registry high-risk tier, **whether** is already
answered by the action-code risk tier — a high-risk action always confirms — so
v1 of this fork does **not** evaluate rule predicates. The
`operator_confirm_rule.scope='registry'` surface already exists (Phase A DBCP);
a future enrichment may use it to add confirm requirements to a *low-risk*
Registry action or to vary the confirm by predicate. v1 keeps the fork small
and correct: high action-code tier ⇒ mandatory operator confirm.

## 3. Decisions to lock

| # | Decision | Proposed lock |
|---|---|---|
| **C5-HR-1** | What makes an operation high-risk | The intrinsic action-code tier — `classifyRegistryRiskTier`. Already locked (B6 D4); this note builds the *handling*, not the tier. |
| **C5-HR-2** | High-risk outcome | A new `operator_confirm_required` issuance outcome — no cert row, no F3 write, until the operator confirms. The `operator_confirm_rules_present` refusal is removed for the high-risk tier. |
| **C5-HR-3** | The confirm is a second human act | Panel proposes; operator confirms via `confirmRegistryShapeCertification`. Two distinct acts. The confirm is never the panel re-running. |
| **C5-HR-4** | Non-replayable re-entry | The confirm call re-runs all panel-evidence checks (Invariant V). A stale confirm can legitimately fail. |
| **C5-HR-5** | Honest provenance | `disposition: 'operator_confirmed'` + an `operator_confirm` block in `gate_results_json` — sub, rationale ≥ 40 chars, timestamp, `basis: 'registry_high_risk_action_code'`, `action_code`, `subject_kind`; `rule_uid` null in v1 (Invariant VI). The block makes explicit that v1 confirmation is risk-tier based, not rule-predicate based. |
| **C5-HR-6** | No DDL | `operator_confirm_rule.scope='registry'` already exists; confirm provenance lands in the existing `gate_results_json` jsonb, exactly as C7 did for BF/BO. To be re-confirmed at build. |
| **C5-HR-7** | Rule-predicate evaluation | Deferred. v1 = action-code tier drives a mandatory confirm; no `operator_confirm_rule` predicate evaluation for Registry scope yet. |
| **C5-HR-8** | Duplicate-cert guard | `confirmRegistryShapeCertification` fails closed if a Registry-shape `certification_record` already exists for the same `(panel_run_uid, action_code, subject_kind)` tuple — no double-issued cert from a retry, double-click, or racing operators. One panel run authorizes one Registry write. |

## 4. Slice plan

C5-HR is T-shirt **S–M**. Three slices, each its own gate.

- **C5-HR-S1 — this design note.** Gate: operator review-back accepts C5-HR-1…8.
- **C5-HR-S2 — the service fork (one bc-core PR).** Add the
  `operator_confirm_required` outcome type; fork `issueRegistryShapeCertification`
  on `classifyRegistryRiskTier`; add `confirmRegistryShapeCertification` with
  non-replayable re-entry and the `gate_results_json` provenance. Unit + integration
  tests: low-risk still auto-issues; high-risk returns confirm-required and
  writes no cert; confirm issues; a stale confirm fails closed. Gate: PR review.
- **C5-HR-S3 — the operator-confirm endpoint (one bc-core PR).** One
  platform-auth bc-core endpoint that calls `confirmRegistryShapeCertification`
  — the operator surface seam. Gate: PR review.

## 5. Boundaries / non-scope

- **No B6 panel / validator / orchestrator change** — F4-v2's note. This note
  defines only the C5 service contract (the new outcome + the confirm method)
  that F4-v2's orchestrator will consume.
- **No F3 change** — F3 verifies and stamps the resulting cert unchanged.
- **No vocabulary work** — the characteristic grammar and the
  `createCharacteristic` operation are F4-v2.
- **No new low-risk behaviour change** — a low-risk operation under a
  zero-rule policy auto-issues exactly as today.
- **No DDL proposed** — to be re-confirmed at C5-HR-S2 build (C5-HR-6).

## Status

`accepted` — operator review-back 2026-05-22 accepted C5-HR-1…8, including the
duplicate-cert guard (C5-HR-8) and the risk-tier-based confirm provenance
(C5-HR-5). The C5-HR build opens as the next implementation gate, on the
operator's go. F4-v2 depends on this note.
