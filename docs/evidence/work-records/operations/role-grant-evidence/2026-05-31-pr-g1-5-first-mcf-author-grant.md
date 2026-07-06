---
uid: pr-g1-5-first-mcf-author-grant-2026-05-31
title: PR-G1.5 evidence — first local-dev service-driven mcf_author grant for anant@selenite.co
description: Post-execution evidence for PR-G1.5. Local bc-core POST /api/admin/mcf/role-grants granted mcf_author to anant@selenite.co through the PR-G1.1 service surface, under PR-LO-1 local-only operating mode, after PR-BS-X super_admin bootstrap evidence merged. Evidence records local bc-core readiness, AWS caller identity, service response, Cognito after-state, mcf.role_grant_audit row, CloudTrail cross-correlation, and a fresh decoded JWT proving mcf_author appears after token refresh. This evidence does NOT authorize or execute mcf_publisher, M11, M12, M12.5, M13, M14, or metric-contract action.
status: committed_post_execution_evidence
date: 2026-05-31
project: bc-docs
domain: operations
subdomain: role-grant-evidence
focus: pr-g1-5-first-mcf-author-grant
supersedes:
superseded_by:
---

# PR-G1.5 Evidence — First Service-Driven `mcf_author` Grant

This file records the first local-dev service-driven MCF role grant through bc-core's live `POST /api/admin/mcf/role-grants` endpoint.

The grant added `mcf_author` to `anant@selenite.co` in Cognito user pool `ap-south-1_bM5xehxIx`. It did not grant `mcf_publisher` and did not invoke M11 / M12 / M12.5 / M13 / M14.

---

## 1. Authority

- **PR-G1 design DBCP**: bc-docs-v3 `d60a742`
- **PR-G1.0 implementation DBCP**: bc-docs-v3 `ec7053d`
- **PR-G1.1 service implementation**: bc-core `f8e8042`
- **Platform Role Catalog + PR-CAT-1 runtime implementation**: bc-docs-v3 `b2d693d` + bc-core `20a4269`
- **PR-BS-1 super_admin bootstrap DBCP**: bc-docs-v3 `656ac77`
- **PR-BS-X bootstrap evidence**: bc-docs-v3 `6a6c680`
- **PR-LO-1 local-only operating model**: bc-docs-v3 `5acdd73`

This file fulfills PR-LO-1 §5.1 local-dev PR-G1.5 evidence requirements.

## 2. Pre-Execution State

| Field | Value |
|---|---|
| `local_bc_core_base_url` | `http://localhost:3100` |
| `bc-core_ready_at` | `2026-05-31T12:17:25Z` |
| `auth_middleware_check` | unauthenticated POST returned HTTP 401; auth middleware loaded |
| `postgres_status` | local Docker Postgres running (`bc-postgres`) |
| `redis_status` | local Docker Redis running (`bc-redis`) |
| `mcf.role_grant_audit_baseline_count` | `0` rows |

A first POST attempt before the final service invocation failed because the already-running local bc-core process did not have the expected AWS profile context for Cognito. The failure occurred before any write: Cognito still lacked `mcf_author`, and `mcf.role_grant_audit` remained at `0` rows. The local bc-core process was then restarted with explicit local AWS SDK context (`AWS_PROFILE=barecount`, `AWS_SDK_LOAD_CONFIG=1`, `AWS_REGION=ap-south-1`) before the successful invocation below.

## 3. AWS Caller Identity

Captured from the local-dev AWS profile used by bc-core and by the evidence checks:

```json
{
  "UserId": "AIDAX6QHEHYVM636VFELH",
  "Account": "546549546538",
  "Arn": "arn:aws:iam::546549546538:user/Claude.Assistant"
}
```

The operator previously resolved the principal provenance in PR-BS-X evidence: `Claude.Assistant` is an operator-controlled local-dev AWS principal configured under the operator's `barecount` profile.

## 4. Invocation Request

| Field | Value |
|---|---|
| `invocation_started_at` | `2026-05-31T13:11:27Z` |
| `invocation_completed_at` | `2026-05-31T13:11:28.547Z` |
| `method` | `POST` |
| `url` | `http://localhost:3100/api/admin/mcf/role-grants` |
| `auth` | ID token carrying `super_admin`; raw token not recorded |

Request body:

```json
{
  "target_user_uid": "8bdb9bd0-8827-4cc8-b640-2087658f1eb6",
  "desired_mcf_roles": ["mcf_author"],
  "reason_text": "Enable first local-dev service-surface MCF authoring run after PR-BS-X bootstrap evidence.",
  "source_pr_or_dbcp_text": "PR-G1 design DBCP d60a742; PR-G1.0 impl DBCP ec7053d; PR-G1.1 service f8e8042; PR-LO-1 local-only model 5acdd73; PR-BS-X evidence 6a6c680"
}
```

## 5. Service Response

| Field | Value |
|---|---|
| `service_response_status` | HTTP 201 success |
| `mcf_role_grant_audit_row_uid` | `4ca4767f-0afb-4577-9f49-c8af99d5bf87` |
| `cognito_request_id` | `85d12606-c0be-41e6-8d3f-eccc2c045f6a` |

Full response body:

```json
{
  "data": {
    "role_grant_uid": "4ca4767f-0afb-4577-9f49-c8af99d5bf87",
    "target_user_uid": "8bdb9bd0-8827-4cc8-b640-2087658f1eb6",
    "target_email_snapshot": "anant@selenite.co",
    "roles_before": [
      "platform_admin",
      "schema_author",
      "operator",
      "analyst",
      "super_admin"
    ],
    "roles_after": [
      "analyst",
      "mcf_author",
      "operator",
      "platform_admin",
      "schema_author",
      "super_admin"
    ],
    "mcf_roles_added": [
      "mcf_author"
    ],
    "mcf_roles_removed": [],
    "granted_at": "2026-05-31T13:11:28.505Z",
    "granted_by_email_snapshot": "anant@selenite.co",
    "note": "Re-fetch your Cognito ID token (via devhub_get_cognito_token or by signing out and back in) to obtain a new token carrying the granted role. Cached tokens issued before this grant will continue to lack the role until they expire (Cognito default: 1 hour). The grant has been applied to Cognito and recorded in the audit row above; the only remaining client-side action is the token refresh."
  },
  "timestamp": "2026-05-31T13:11:28.547Z"
}
```

## 6. Cognito After-State

Read after the service response:

```json
{
  "observed_at": "2026-05-31T13:13:42Z",
  "target_user_uid": "8bdb9bd0-8827-4cc8-b640-2087658f1eb6",
  "target_user_email_snapshot": "anant@selenite.co",
  "roles_after_observed": [
    "analyst",
    "mcf_author",
    "operator",
    "platform_admin",
    "schema_author",
    "super_admin"
  ],
  "user_last_modified_date": "2026-05-31T18:41:28.957+05:30"
}
```

Diff:

```json
{
  "mcf_roles_added": ["mcf_author"],
  "mcf_roles_removed": [],
  "non_mcf_roles_added": [],
  "non_mcf_roles_removed": []
}
```

## 7. Audit Row

`mcf.role_grant_audit` row count after PR-G1.5: `1`.

Query output for `role_grant_uid = '4ca4767f-0afb-4577-9f49-c8af99d5bf87'`:

```text
role_grant_uid: 4ca4767f-0afb-4577-9f49-c8af99d5bf87
granted_at: 2026-05-31 13:11:28.505105+00
granted_by_user_uid: 8bdb9bd0-8827-4cc8-b640-2087658f1eb6
granted_by_email_snapshot: anant@selenite.co
target_user_uid: 8bdb9bd0-8827-4cc8-b640-2087658f1eb6
target_email_snapshot: anant@selenite.co
roles_before_json: ["platform_admin", "schema_author", "operator", "analyst", "super_admin"]
roles_after_json: ["analyst", "mcf_author", "operator", "platform_admin", "schema_author", "super_admin"]
mcf_roles_added_json: ["mcf_author"]
mcf_roles_removed_json: []
reason_text: Enable first local-dev service-surface MCF authoring run after PR-BS-X bootstrap evidence.
source_pr_or_dbcp_text: PR-G1 design DBCP d60a742; PR-G1.0 impl DBCP ec7053d; PR-G1.1 service f8e8042; PR-LO-1 local-only model 5acdd73; PR-BS-X evidence 6a6c680
cognito_request_id: 85d12606-c0be-41e6-8d3f-eccc2c045f6a
```

## 8. CloudTrail Cross-Correlation

Read-only CloudTrail lookup found the Cognito write event matching the audit row's `cognito_request_id`:

```json
{
  "EventId": "ed240aa1-2404-4a40-ac48-0abd944ebd94",
  "EventTime": "2026-05-31T18:41:28+05:30",
  "EventName": "AdminUpdateUserAttributes",
  "Username": "HIDDEN_DUE_TO_SECURITY_REASONS",
  "RequestId": "85d12606-c0be-41e6-8d3f-eccc2c045f6a",
  "EventSource": "cognito-idp.amazonaws.com",
  "AwsRegion": "ap-south-1"
}
```

## 9. Fresh JWT Verification

A fresh Cognito ID token was fetched after the grant and decoded locally. The raw token and signature segment are not recorded.

| Field | Value |
|---|---|
| `jwt_refresh_at` | `2026-05-31T13:17:06Z` |
| `mcf_author_in_refreshed_token` | `true` |
| `super_admin_in_refreshed_token` | `true` |
| `signature_segment` | `"<redacted>"` |

Decoded header:

```json
{
  "kid": "T6F8HUHAdVeEEoZkrkZjEvIwPZ99IYlZ62ZcPE+wz5A=",
  "alg": "RS256"
}
```

Decoded payload, sanitized:

```json
{
  "sub": "8bdb9bd0-8827-4cc8-b640-2087658f1eb6",
  "email": "anant@selenite.co",
  "custom:display_name": "<redacted>",
  "custom:tenant_id": "demo-selenite",
  "custom:roles": "[\"analyst\",\"mcf_author\",\"operator\",\"platform_admin\",\"schema_author\",\"super_admin\"]",
  "token_use": "id",
  "iss": "https://cognito-idp.ap-south-1.amazonaws.com/ap-south-1_bM5xehxIx",
  "aud": "5sn94c6o5timitiujjalv3uv11",
  "auth_time": 1780233426,
  "exp": 1780237026,
  "iat": 1780233426
}
```

## 10. Operator Attestation

Operator authorization and execution note:

> I am `anant@selenite.co`, the invoking operator. I authorized Codex/Claude in this local session to execute PR-G1.5 actions on my behalf after upgrading PowerShell, using my local bc-core process and my operator-controlled `barecount` AWS profile. I confirm the local bc-core process at `http://localhost:3100` used those credentials to call Cognito Admin APIs, that before/after roles were empirically verified, that `mcf_author` was added to the target's `custom:roles`, that no other MCF role was added, and that no non-MCF role was modified. I understand future platform role grants must go through the appropriate service surface and not direct AWS-side mutation.
>
> Signed: anant@selenite.co via explicit in-thread authorization at 2026-05-31T13:17:06Z

## 11. Redaction Sweep

Evidence file must not contain raw credentials or raw tokens. Pre-commit sweep covered:

- `Bearer`
- `Authorization:`
- JWT-looking `eyJ` fragments
- `AKIA` / `ASIA`
- `aws_access_key` / `aws_secret_access_key` / `aws_session_token`
- `console.aws.amazon.com`
- raw bc-core `.env` contents

Allowed expected content:

- Cognito service issuer URL (`https://cognito-idp.ap-south-1.amazonaws.com/...`) inside decoded JWT payload
- IAM `UserId` / `Account` / `Arn` from `sts get-caller-identity`
- App Client ID in JWT `aud` claim (not a client secret)

## 12. Hard Boundaries

This PR-G1.5 execution did:

- ✓ invoke `POST /api/admin/mcf/role-grants` exactly once successfully
- ✓ add only `mcf_author` to the target user
- ✓ write exactly one `mcf.role_grant_audit` row
- ✓ verify Cognito after-state and fresh JWT after-state

This PR-G1.5 execution did NOT:

- ❌ grant `mcf_publisher`
- ❌ grant any non-MCF role
- ❌ invoke M11 / M12 / M12.5 / M13 / M14
- ❌ create, modify, evaluate, publish, or supersede any metric contract
- ❌ touch tenant databases
- ❌ apply DDL
- ❌ modify bc-core / bc-admin / bc-portal / bc-infra / bc-ai source code
- ❌ call vendor LLM APIs

## 13. Sequencing Impact

PR-G1.5 is now complete after this evidence merges.

Next execution block toward a real metric:

1. **PR-G2** — authorize the first service-surface M12 panel-run under the now-refreshed `mcf_author` role.
2. **PR-E2** — execute `POST /api/mcf/panel-runs` through local bc-core, capture panel-run evidence, and evaluate whether the run can advance toward M12.5 materialization.

No M12 or metric-contract action is performed by this evidence file.

## 14. BCF §13 Trailers

BuildPlan: docs-only § PR-G1.5 post-execution evidence for first local-dev service-driven mcf_author grant through bc-core POST /api/admin/mcf/role-grants; records service response, Cognito after-state, audit row, CloudTrail event, and fresh JWT verification
Finding: PR-BS-X bootstrap evidence merged and local-only prerequisites were satisfied; bc-core service grant added only mcf_author to anant@selenite.co, wrote audit row 4ca4767f-0afb-4577-9f49-c8af99d5bf87, and fresh JWT verification confirms mcf_author is present
Rollback: revert this docs evidence PR only removes the evidence artifact; it does not undo the Cognito role grant. Functional rollback requires a separately authorized service-mediated role grant setting desired_mcf_roles to [] for the same target, with its own evidence.
Phase0Impact: none

