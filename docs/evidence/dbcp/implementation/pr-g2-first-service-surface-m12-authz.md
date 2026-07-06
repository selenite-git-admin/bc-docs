---
uid: pr-g2-first-service-surface-m12-authz
title: PR-G2 — authorize first local-dev service-surface M12 panel run after PR-G1.5
description: Narrow authorization DBCP for exactly one local-dev M12 panel-run invocation through bc-core POST /api/mcf/panel-runs, using the already-pending intake 4d849778-3989-4caf-8a71-7d44b782d98e and an operator token carrying mcf_author. This authorizes PR-E2 execution evidence only. It does not authorize M12.5 materialization, M13 evaluation, M14 publication, mcf_publisher grant, metric-contract publication, tenant DB access, DDL, or any broad cleanup/governance work.
status: proposed
date: 2026-05-31
project: bc-docs
domain: implementation
subdomain: mcf
focus: first-service-surface-m12-run
supersedes:
superseded_by:
---

# PR-G2 — First Service-Surface M12 Authorization

This DBCP authorizes one execution block: **PR-E2**, the first local-dev service-surface M12 panel run through bc-core HTTP.

The goal is to move toward a real MCF metric by exercising the actual service path after the role-gate work completed.

## 1. Authority Chain

| Artifact | Status |
|---|---|
| PR-C4 MCF controllers + module | bc-core `2a7a1e5` |
| PR-G1.1 MCF role-grant service | bc-core `f8e8042` |
| PR-CAT-1 runtime role catalog | bc-core `20a4269` |
| PR-BS-X super_admin evidence | bc-docs-v3 `6a6c680` |
| PR-G1.5 mcf_author grant evidence | bc-docs-v3 `4ba2cde` |
| PR #176 MCF intake read fix | bc-core `bb18da1` |

## 2. Exact Authorized Invocation

| Field | Value |
|---|---|
| Method | `POST` |
| URL | `http://localhost:3100/api/mcf/panel-runs` |
| Required role | `mcf_author` |
| Token requirement | fresh Cognito ID token whose decoded `custom:roles` contains `mcf_author` |
| Intake | `4d849778-3989-4caf-8a71-7d44b782d98e` |
| Candidate | `overdue_invoice_count` |
| Current intake status | `pending` |
| `allow_retry` | `false` |

Request body:

```json
{
  "intake_queue_uid": "4d849778-3989-4caf-8a71-7d44b782d98e",
  "allow_retry": false
}
```

No other intake is authorized by this DBCP.

## 3. Pre-Execution Checks

PR-E2 MUST capture before executing:

1. Fresh decoded token has `mcf_author`.
2. `GET /api/mcf/intakes/4d849778-3989-4caf-8a71-7d44b782d98e` returns `status_code = pending`.
3. `GET /api/mcf/panel-runs?limit=5` works through the same service surface.
4. Duplicate guard is clear: no existing `APPROVE_FOR_DRAFT` panel run for this reservoir entry and no panel run in the last 10 minutes for the same reservoir entry.
5. `mcf.metric_contract` and `mcf.metric_contract_version` row counts remain `0` before execution.

The May 31 preflight after PR #176 already verified #2 and #3 read-only; PR-E2 should re-check immediately before POST.

## 4. Expected Outcomes

The POST returns HTTP 201 with:

```ts
{
  panel_run_uid: string;
  verdict_code: 'APPROVE_FOR_DRAFT' | 'OPERATOR_REVIEW' | 'REJECT_DEFECT';
  defect_code: string | null;
  operator_review_reason: string | null;
}
```

Allowed verdicts:

- `APPROVE_FOR_DRAFT`: PR-E2 may proceed to evidence capture; M12.5 remains separately gated.
- `OPERATOR_REVIEW`: PR-E2 captures evidence and stops; operator decides whether another attempt is warranted later.
- `REJECT_DEFECT`: PR-E2 captures evidence and stops; no materialization.

## 5. PR-E2 Evidence Requirements

PR-E2 evidence MUST record:

- invocation timestamp
- sanitized decoded token roles (`mcf_author` present, raw token absent)
- request body
- response status/body
- new `panel_run_uid`
- rows added to `mcf.metric_authoring_panel_run` and `mcf.metric_authoring_panel_transcript`
- three transcript roles present: maker/checker/moderator
- post-run intake status
- post-run duplicate-guard state
- row counts for `mcf.metric_contract` and `mcf.metric_contract_version` proving M12.5 did not run
- if vendor APIs fail, the error response and proof no partial M12.5 materialization occurred

## 6. Hard Boundaries

This DBCP authorizes PR-E2 only. It does NOT authorize:

- `mcf_publisher` grant
- M12.5 materialization
- M13 PE-MC evaluation
- M14 publication
- metric-contract creation outside the M12 panel-run's own permitted M12 substrate writes
- tenant DB reads or writes
- DDL
- bc-admin / bc-portal / bc-infra / bc-ai source changes
- broad governance cleanup

## 7. Rollback / Stop Rules

No rollback is expected for a successful M12 panel-run row; panel-run and transcript rows are evidence-bearing append-only records.

Stop without retry if:

- HTTP 401/403 indicates the token lacks `mcf_author`.
- HTTP 409 indicates duplicate proposal or status conflict.
- Any response suggests M12.5 or metric-contract materialization occurred unexpectedly.
- Vendor failure prevents a terminal panel verdict; capture the failure and stop.

## 8. Sequencing

After PR-G2 merges:

1. PR-E2 executes the exact POST in §2.
2. PR-E2 evidence is committed.
3. Only if the verdict is `APPROVE_FOR_DRAFT`, a later M12.5 authorization/execution gate may be considered.

## 9. BCF §13 Trailers

BuildPlan: docs-only § PR-G2 first service-surface M12 authorization for one local-dev POST /api/mcf/panel-runs against intake 4d849778-3989-4caf-8a71-7d44b782d98e
Finding: PR-G1.5 evidence merged, mcf_author is present in fresh JWT, target intake is pending, and read-only service probes pass after bc-core PR #176; the next real metric step is one governed M12 panel-run execution
Rollback: revert this DBCP before PR-E2 to remove authorization; after PR-E2, rollback of this docs file does not delete append-only panel-run evidence rows
Phase0Impact: none
