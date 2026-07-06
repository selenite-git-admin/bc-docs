---
uid: pr-e2-first-service-surface-m12-2026-05-31
title: PR-E2 evidence — first local-dev service-surface M12 panel run
description: Post-execution evidence for PR-E2. Local bc-core POST /api/mcf/panel-runs was invoked once under PR-G2 authorization against intake 4d849778-3989-4caf-8a71-7d44b782d98e using a fresh token carrying mcf_author. The endpoint returned HTTP 201 and wrote one mcf.metric_authoring_panel_run row plus three transcript rows. Verdict was OPERATOR_REVIEW with operator_review_reason vendor_outage. No M12.5 materialization, M13, M14, metric-contract row, tenant DB touch, or DDL occurred.
status: committed_post_execution_evidence
date: 2026-05-31
project: bc-docs
domain: operations
subdomain: mcf-panel-run-evidence
focus: pr-e2-first-service-surface-m12
supersedes:
superseded_by:
---

# PR-E2 Evidence — First Service-Surface M12 Panel Run

This file records the first local-dev service-surface M12 panel-run invocation through bc-core HTTP after PR-G1.5 granted `mcf_author`.

Result: the service path executed and persisted M12 evidence rows, but the panel verdict was `OPERATOR_REVIEW` due to `vendor_outage`. This is not an `APPROVE_FOR_DRAFT` and does not unblock M12.5.

## 1. Authority

- **PR-G2 authorization DBCP**: bc-docs-v3 `c6e68b2`
- **PR-G1.5 role grant evidence**: bc-docs-v3 `4ba2cde`
- **MCF read-surface substrate fix**: bc-core `bb18da1`
- **Target intake**: `4d849778-3989-4caf-8a71-7d44b782d98e`

This file does not supersede any prior document. It records the execution authorized by PR-G2.

## 2. Prechecks

Captured immediately before POST:

```json
{
  "precheck_at": "2026-05-31T13:49:26Z",
  "intake_pre_status_code": 200,
  "intake_pre_status": "pending",
  "panel_runs_pre_status_code": 200,
  "panel_runs_pre_count": 2,
  "db_pre": [
    "panel_run_count=2",
    "transcript_count=6",
    "metric_contract_count=0",
    "metric_contract_version_count=0",
    "duplicate_approve_count=0",
    "recent_duplicate_window_count=0"
  ]
}
```

A prior wrapper attempt in PowerShell failed before producing an HTTP result because of response-object handling. A database check immediately afterward confirmed no panel-run row was created by that attempt: panel-run count remained `2`, transcript count remained `6`.

## 3. Invocation

| Field | Value |
|---|---|
| `invocation_started_at` | `2026-05-31T13:49:27Z` |
| `invocation_completed_at` | `2026-05-31T13:49:27Z` |
| `method` | `POST` |
| `url` | `http://localhost:3100/api/mcf/panel-runs` |
| `auth` | fresh Cognito ID token carrying `mcf_author`; raw token not recorded |
| `powershell_version` | `7.5.5` |

Request body:

```json
{
  "intake_queue_uid": "4d849778-3989-4caf-8a71-7d44b782d98e",
  "allow_retry": false
}
```

## 4. Service Response

```json
{
  "status_code": 201,
  "body": {
    "data": {
      "panel_run_uid": "b372a0e0-4f95-4bd5-8f59-e9ce6ba6bca5",
      "verdict_code": "OPERATOR_REVIEW",
      "defect_code": null,
      "operator_review_reason": "vendor_outage"
    },
    "timestamp": "2026-05-31T13:49:27.467Z"
  }
}
```

Interpretation:

- The M12 HTTP service path was reached.
- The controller returned HTTP 201 with a terminal panel-run response.
- The verdict is `OPERATOR_REVIEW`, not `APPROVE_FOR_DRAFT`.
- M12.5 remains closed.

## 5. Persisted Panel Row

```text
panel_run_uid: b372a0e0-4f95-4bd5-8f59-e9ce6ba6bca5
created_at: 2026-05-31 13:49:27.304044+00
reservoir_name: operator_direct
reservoir_entry_id: pr-28-section-4-3-first-real-intake-2026-05-30T07-18-38-395Z
reservoir_confidence_band: medium
verdict_code: OPERATOR_REVIEW
defect_code: null
operator_review_reason: vendor_outage
```

Consensus payload summary:

```json
{
  "defect_code": null,
  "verdict_code": "OPERATOR_REVIEW",
  "prompt_version": "m12-panel-v1",
  "per_role_summary": [
    {
      "role": "maker",
      "claim_count": 0,
      "defect_code": null,
      "verdict_code": "OPERATOR_REVIEW",
      "transcript_uid": "c8cd0e91-f37c-4ce2-8f39-cc8963c7f531",
      "tool_call_count": 0
    },
    {
      "role": "checker",
      "claim_count": 0,
      "defect_code": null,
      "verdict_code": "OPERATOR_REVIEW",
      "transcript_uid": "29a47c3c-4bbe-4dd3-882d-1b565da0d003",
      "tool_call_count": 0
    },
    {
      "role": "moderator",
      "claim_count": 0,
      "defect_code": null,
      "verdict_code": "OPERATOR_REVIEW",
      "transcript_uid": "dbf348bd-c299-4b88-8434-8dd253821e6b",
      "tool_call_count": 0
    }
  ],
  "candidate_proposal": {},
  "grounding_violations": [],
  "grounding_check_passed": true,
  "operator_review_reason": "vendor_outage",
  "panel_algorithm_version": "mcf-panel-v1",
  "defect_code_registry_version": "v1"
}
```

## 6. Transcript Rows

Three transcript rows were written:

| Role | Transcript UID | Vendor | Status | Verdict |
|---|---|---|---|---|
| maker | `c8cd0e91-f37c-4ce2-8f39-cc8963c7f531` | anthropic | `vendor_failure` | `OPERATOR_REVIEW` |
| checker | `29a47c3c-4bbe-4dd3-882d-1b565da0d003` | openai | `vendor_failure` | `OPERATOR_REVIEW` |
| moderator | `dbf348bd-c299-4b88-8434-8dd253821e6b` | google | `vendor_failure` | `OPERATOR_REVIEW` |

Per-role transcript payloads had empty `claims`, empty `tool_calls`, empty `reasoning_trace`, and `panel_algorithm_version = mcf-panel-v1`.

## 7. Post-Execution Counts

```json
{
  "panel_run_count": 3,
  "transcript_count": 9,
  "metric_contract_count": 0,
  "metric_contract_version_count": 0
}
```

The target intake remains `pending` after this `OPERATOR_REVIEW` verdict, matching MCF-ERR-001 verdict-aware status semantics.

## 8. Boundary Confirmation

This PR-E2 execution did:

- ✓ invoke `POST /api/mcf/panel-runs` exactly once successfully after prechecks
- ✓ write one `mcf.metric_authoring_panel_run` row
- ✓ write three `mcf.metric_authoring_panel_transcript` rows
- ✓ preserve `mcf.metric_contract` at zero rows
- ✓ preserve `mcf.metric_contract_version` at zero rows

This PR-E2 execution did NOT:

- ❌ produce `APPROVE_FOR_DRAFT`
- ❌ invoke M12.5 materialization
- ❌ invoke M13 PE-MC evaluation
- ❌ invoke M14 publication
- ❌ create or publish a metric contract
- ❌ grant `mcf_publisher`
- ❌ touch tenant databases
- ❌ apply DDL
- ❌ change bc-core / bc-admin / bc-portal / bc-infra / bc-ai source code

## 9. Next Execution Block

The next real blocker is not identity anymore. It is vendor execution: all three panel roles persisted `vendor_failure`, producing `OPERATOR_REVIEW / vendor_outage`.

Before retrying M12, inspect the vendor adapter failure path and local process environment. A retry should be separately authorized because the successful PR-E2 row is append-only evidence and the current intake remains pending.

## 10. BCF §13 Trailers

BuildPlan: docs-only § PR-E2 post-execution evidence for first local-dev service-surface M12 panel run through bc-core POST /api/mcf/panel-runs
Finding: PR-G2 authorized one service-surface M12 run; bc-core returned HTTP 201 and persisted panel_run_uid b372a0e0-4f95-4bd5-8f59-e9ce6ba6bca5 plus three transcripts, but verdict was OPERATOR_REVIEW with vendor_outage, so M12.5 remains closed
Rollback: revert this evidence PR only removes the documentation artifact; persisted M12 panel-run and transcript rows are append-only evidence and are not rolled back by docs reversion
Phase0Impact: none
