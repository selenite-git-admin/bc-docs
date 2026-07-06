---
uid: super-admin-bootstrap-evidence-2026-05-31
title: super_admin bootstrap evidence — anant@selenite.co — operator-executed local-dev bootstrap
description: Post-execution evidence for PR-BS-X. The operator executed the one-time `super_admin` bootstrap authorized by PR-BS-1 (bc-docs-v3 `656ac77`) under the local-only operating model clarified by PR-LO-1 (bc-docs-v3 `5acdd73`). Evidence records the operator-controlled local-dev AWS principal, before/after Cognito roles, cleanup of the temporary CLI artifact, CloudTrail lookup fallback, and a fresh decoded Cognito ID token proving `super_admin` appears after sign-in. This evidence does NOT authorize or perform `mcf_author`, PR-G1.5, M12, M12.5, M13, M14, or metric-contract action.
status: committed_post_execution_evidence
date: 2026-05-31
project: bc-docs
domain: operations
subdomain: role-bootstrap-evidence
focus: super-admin-bootstrap-execution
supersedes:
superseded_by:
---

# super_admin Bootstrap Evidence — PR-BS-X

This file records the one-time operator-executed bootstrap that added `super_admin` to `anant@selenite.co` in Cognito user pool `ap-south-1_bM5xehxIx`.

This evidence is intentionally narrow. It proves only that the bootstrap authorized by PR-BS-1 was executed and that the resulting fresh Cognito token carries `super_admin`. It does NOT grant `mcf_author`, does NOT invoke PR-G1.5, and does NOT execute M11 / M12 / M12.5 / M13 / M14.

---

## 1. Authority

This evidence file fulfills the §6 + §8.2 deliverable obligation of the merged Super-Admin Bootstrap DBCP:

- **PR-BS-1 DBCP**: `bc-docs-v3/docs/implementation/super-admin-bootstrap-dbcp.md` (merged `656ac77`, PR #38; supersedes earlier draft at `da095e6` via amendment v2 `10ee6fe`)
- **PR-LO-1 DBCP**: `bc-docs-v3/docs/implementation/local-only-operating-model-dbcp.md` (merged `5acdd73`, PR #41; local-dev path means bc-infra R12 is not a current blocker)
- **Schema source**: PR-BS-1 §6.1 (18 required fields)
- **Attestation source**: PR-BS-1 §6.2 (≥100 chars with 6 confirmations)
- **Rollback source**: PR-BS-1 §7 (procedure + §7.2 invariant + §7.3 evidence)
- **Hard rules**: PR-BS-1 §10 HR-BS-1 through HR-BS-7

This file does NOT supersede, amend, or replace any prior governance document. It is the one-shot evidence artifact for the one-shot bootstrap authorized by PR-BS-1.

## 2. Pre-flight (operator runs BEFORE any AWS-side mutation)

### 2.1 Target identity confirmation

These fields are LOCKED by PR-BS-1 §3 and SHOULD NOT be changed:

| Field | Value |
|---|---|
| target_user_email | `anant@selenite.co` |
| target_user_sub | `8bdb9bd0-8827-4cc8-b640-2087658f1eb6` |
| target_user_display_name | (operator-supplied; not material) |

### 2.2 Cognito environment confirmation

LOCKED by PR-BS-1 §4:

| Field | Value |
|---|---|
| aws_account_id | `546549546538` |
| aws_region | `ap-south-1` |
| aws_cli_profile | `barecount` |
| cognito_user_pool_id | `ap-south-1_bM5xehxIx` |
| environment | `dev` |

### 2.3 Operator AWS identity check (operator runs)

Operator MUST confirm before-state matches expected account/identity:

```
$ aws sts get-caller-identity --profile barecount
{
  "UserId": "AIDAX6QHEHYVM636VFELH",
  "Account": "546549546538",
  "Arn": "arn:aws:iam::546549546538:user/Claude.Assistant"
}
```

Operator records: Account matched `546549546538`.

Operator principal note: the `barecount` local AWS profile resolves to IAM principal `arn:aws:iam::546549546538:user/Claude.Assistant`. The operator explicitly confirmed this is an operator-controlled local-dev AWS principal and authorized continuing PR-BS-X using it, provided the evidence states the principal explicitly and confirms the operator personally executed the mutation command.

Audit reference: `TSK-3ccf80` was filed earlier this session when Step 1 (`sts get-caller-identity`) first surfaced that `barecount` resolves to the `Claude.Assistant` IAM user rather than a personally-named operator principal. The operator resolved the task by confirming this is an operator-controlled local-dev AWS principal (operator-administered automation user under their AWS account) and authorizing PR-BS-X to proceed under it. The §9 attestation below restates that personal-execution confirmation.

### 2.4 Optional pool-wide pre-check (PR-BS-1 §12 OQ-BS-1)

```
$ AWS_PROFILE=barecount aws cognito-idp list-users \
    --user-pool-id ap-south-1_bM5xehxIx \
    --region ap-south-1 | \
  jq -r '.Users[] | select(.Attributes[]? | select(.Name=="custom:roles" and (.Value | contains("super_admin"))))'
```

| Field | Value |
|---|---|
| no_other_super_admin_confirmed_at | `not_run_optional_check` |
| no_other_super_admin_stdout | `not_run_optional_check` |

(Per PR-BS-1 §12: this check is recommended but not mandatory; the canonical pre-state verification is the target-user before_roles_observed capture in §3 below.)

## 3. Before-state (operator captures empirically)

### 3.1 Before-roles via Console OR CLI

**If Console path**: operator navigates to Cognito → User pools → `ap-south-1_bM5xehxIx` → Users → `anant@selenite.co` → "User attributes" tab → copy `custom:roles` JSON string verbatim.

**If CLI path**:
```
$ AWS_PROFILE=barecount aws cognito-idp admin-get-user \
    --user-pool-id ap-south-1_bM5xehxIx \
    --username 8bdb9bd0-8827-4cc8-b640-2087658f1eb6 \
    --region ap-south-1
```
Operator extracts the `UserAttributes[]` entry where `Name == "custom:roles"` and copies the `Value` JSON string verbatim.

| Field | Value |
|---|---|
| before_roles_observed | `["platform_admin","schema_author","operator","analyst"]` |
| before_roles_expected | `["platform_admin","schema_author","operator","analyst"]` (per Catalog DBCP `b2d693d` §2.3) |
| before_observed_matches_expected | `true` |

Additional before-state fields captured by read-only `admin-get-user`: target user email `anant@selenite.co`; display name `<redacted>`; `custom:tenant_id` `demo-selenite`; user enabled `true`; status `CONFIRMED`.

## 4. Mutation (operator executes ONLY after §2 + §3 confirm)

### 4.1 Mechanism + timing

| Field | Value |
|---|---|
| bootstrap_started_at | `2026-05-31T11:01:28Z` |
| mechanism_used | `aws-cli` |
| cli_form_used | `windows-cli-input-json` |

### 4.2 If CLI path (Windows --cli-input-json form per PR-BS-1 §5.2 Windows note)

Operator saves the following to `update-roles.json` (the file SHOULD be deleted after evidence is captured):

```json
{
  "UserPoolId": "ap-south-1_bM5xehxIx",
  "Username": "8bdb9bd0-8827-4cc8-b640-2087658f1eb6",
  "UserAttributes": [
    {
      "Name": "custom:roles",
      "Value": "[\"platform_admin\",\"schema_author\",\"operator\",\"analyst\",\"super_admin\"]"
    }
  ]
}
```

Operator runs:
```
$ AWS_PROFILE=barecount aws cognito-idp admin-update-user-attributes \
    --cli-input-json file://update-roles.json \
    --region ap-south-1
```

### 4.3 If CLI path (Linux/macOS shorthand per PR-BS-1 §5.2)

```
$ AWS_PROFILE=barecount aws cognito-idp admin-update-user-attributes \
    --user-pool-id ap-south-1_bM5xehxIx \
    --username 8bdb9bd0-8827-4cc8-b640-2087658f1eb6 \
    --user-attributes 'Name=custom:roles,Value=["platform_admin","schema_author","operator","analyst","super_admin"]' \
    --region ap-south-1
```

### 4.4 If Console path

Operator edits `custom:roles` value to: `["platform_admin","schema_author","operator","analyst","super_admin"]` (or whatever before_roles_observed was, with `super_admin` appended). Operator saves.

### 4.5 Mutation evidence

| Field | Value |
|---|---|
| bootstrap_completed_at | `2026-05-31T11:10:29Z` (derived from Cognito `UserLastModifiedDate` after successful CLI mutation; immediate CLI completion timestamp was not captured) |
| aws_request_id | `not_captured_from_cli` |
| cli_exit_code | `0` |
| update_roles_json_path | `C:\Users\anant\update-roles.json` |
| update_roles_json_deleted | `true` |
| update_roles_json_deleted_at | `2026-05-31T11:29:00Z` |

## 5. After-state (operator captures empirically)

Operator re-reads the attribute via Console OR same `admin-get-user` CLI as §3.1:

| Field | Value |
|---|---|
| after_roles_observed | `["platform_admin","schema_author","operator","analyst","super_admin"]` |
| after_roles_expected | `["platform_admin","schema_author","operator","analyst","super_admin"]` |
| roles_diff_added | `["super_admin"]` |
| roles_diff_removed | `[]` |

After-state was verified twice: once by operator-pasted `admin-get-user` output immediately after the mutation, and once by a read-only `admin-get-user` check at `2026-05-31T11:32:09Z`.

## 6. CloudTrail cross-correlation (operator runs ~5 min after mutation)

| Field | Value |
|---|---|
| cloudtrail_event_id | `not_found_within_5_min` |
| cloudtrail_event_time | `not_found_within_5_min` |
| cloudtrail_lookup_window_start | `2026-05-31T11:05:00Z` |
| cloudtrail_lookup_window_end | `2026-05-31T11:25:00Z` |

(Note: CloudTrail event delivery lag is typically 5-15 minutes for management events; the AWS RequestId from §4.5 remains the primary forensic key.)

## 7. Token re-fetch (operator runs after mutation; mandatory per HR-BS-5)

Operator MUST sign out of all bc-portal / bc-admin sessions, sign back in, decode the new JWT, and verify `super_admin` lands in `custom:roles`.

| Field | Value |
|---|---|
| token_refetch_at | `2026-05-31T11:32:41Z` |
| token_decoded_header_json | `{"kid":"T6F8HUHAdVeEEoZkrkZjEvIwPZ99IYlZ62ZcPE+wz5A=","alg":"RS256"}` |
| token_decoded_payload_json | See JSON block below |
| token_signature_segment | `"<redacted>"` (literal; raw signature MUST NEVER be committed per PR-BS-1 §6.3) |
| custom_roles_in_refetched_token | `["platform_admin","schema_author","operator","analyst","super_admin"]` |

Decoded ID-token payload, captured locally with the raw token not printed:

```json
{
  "sub": "8bdb9bd0-8827-4cc8-b640-2087658f1eb6",
  "custom:roles": "[\"platform_admin\",\"schema_author\",\"operator\",\"analyst\",\"super_admin\"]",
  "email_verified": true,
  "iss": "https://cognito-idp.ap-south-1.amazonaws.com/ap-south-1_bM5xehxIx",
  "cognito:username": "8bdb9bd0-8827-4cc8-b640-2087658f1eb6",
  "custom:tenant_id": "demo-selenite",
  "custom:display_name": "<redacted>",
  "aud": "5sn94c6o5timitiujjalv3uv11",
  "token_use": "id",
  "email": "anant@selenite.co"
}
```

## 8. Rollback (§8.A if NOT used; §8.B if used)

### 8.A — Rollback NOT used (default)

| Field | Value |
|---|---|
| rollback_invoked | `false` |
| rollback_evidence_file | `n/a` |

(If the operator decides post-bootstrap to revert, switch this section to §8.B and author a SEPARATE evidence file at `docs/operations/role-bootstrap-evidence/<rollback-date>-super-admin-bootstrap-rollback.md` per PR-BS-1 §7.3. Do NOT commit rollback evidence in this file.)

(Note: the §8.B template block from the scaffold is intentionally removed in this post-execution evidence — rollback was not invoked. If a future operator needs to record a rollback, they author a separate rollback evidence file per the path above.)

## 9. Operator attestation (PR-BS-1 §6.2 — MANDATORY, ≥100 chars, 6 confirmations)

I am anant@selenite.co, the operator authorized by Catalog DBCP `b2d693d` §2.3. I executed this bootstrap action under my own operator-controlled local-dev AWS credentials linked to AWS profile `barecount`; that profile resolves on this workstation to IAM principal `arn:aws:iam::546549546538:user/Claude.Assistant`. I personally executed the Cognito mutation command that added `super_admin`. I verified the before-roles empirically before mutating and the after-roles empirically after mutating. I confirm only `super_admin` was added; all 4 pre-existing roles are preserved. I confirm no other identity was modified during this bootstrap. I understand subsequent role grants, including my own future grants, MUST go through `POST /api/admin/mcf/role-grants` or its successor service; this bootstrap exception is one-time only.

Signed: anant@selenite.co at `2026-05-31T11:33:00Z`

## 10. MUST-NOT-CONTAIN reminder (PR-BS-1 §6.3 + §6.4)

Before committing PR-BS-X, the operator MUST scan this file and confirm NONE of the following appear:

- ❌ Raw JWT (header.payload.signature 3-segment string) — only the decoded header + payload as JSON; signature replaced with literal `"<redacted>"`
- ❌ Raw refresh token, access token, or ID token in any form
- ❌ AWS access key ID, secret access key, or session token
- ❌ Cognito client secret OR Cognito user pool secret
- ❌ Cognito Console URLs in any capture form (screenshots, copy-paste, terminal redirect logs, browser-history exports, command output captures); URL substrings MUST be redacted before commit
- ❌ Screenshots of the AWS Console session (URLs in screenshots leak federation state)
- ❌ Arbitrary undocumented Cognito custom attributes (the `custom:tenant_id` field is acceptable since it's documented in PR-BS-1 §3; other custom attributes — if any — MUST NOT be exposed)
- ❌ Operator's OS username, machine hostname, or IP address from terminal prompts (acceptable to leave generic `$` prompt; specific identifiers MUST be redacted)
- ❌ Anything that wasn't explicitly authorized for evidence capture in PR-BS-1 §6.1-§6.4

The operator's review SHOULD include a `grep -i` sweep of this file for substrings like `Bearer`, `eyJ`, `AKIA`, `aws_access_key`, `cognito-idp.ap-south-1.amazonaws.com`, `console.aws.amazon.com` before committing.

Leak sweep result at PR-BS-X evidence authoring: no raw JWT, access token, refresh token, AWS key, Authorization header, or Console URL was found. The only matches were the reminder substrings in this section and the non-secret Cognito issuer URL in the decoded token payload.

## 11. Sequencing — what this evidence unlocks

Once this file is filled in, attested, and merged as PR-BS-X:

1. **PR-G1.5 local-dev prerequisite satisfied** (bootstrap executed; see PR-BS-1 §8.4 and PR-LO-1 `5acdd73`)
2. Under PR-LO-1 local-only mode, bc-infra R12 IAM is dormant/future-facing and is NOT a current local-dev PR-G1.5 blocker.
3. After this evidence file merges, the operator may invoke local bc-core `POST /api/admin/mcf/role-grants` with target `anant@selenite.co`, `desired_mcf_roles: ["mcf_author"]`, ≥20-char rationale, and authorizing-DBCP citation (PR-G1.5). That invocation remains separate and is NOT performed by this evidence file.

## 12. Hard boundaries on this evidence PR

This PR is **docs-only evidence** after operator execution.

- ✓ AWS calls were limited to the one operator-executed Cognito bootstrap mutation plus read-only evidence capture (`sts`, `admin-get-user`, `admin-initiate-auth` token fetch, and CloudTrail lookup)
- ✓ Cognito modification was limited to adding `super_admin` to the single target identity `anant@selenite.co`
- ✓ No role grants
- ✓ No DDL applied
- ✓ No substrate mutation
- ✓ No tenant DB touch
- ✓ No M11 / M12 / M12.5 / M13 / M14 invocation
- ✓ No bc-core / bc-admin / bc-portal / bc-infra change
- ✓ No new npm or pip dependency
- ✓ No supersession of any prior DBCP, ADR, or governance artifact

This evidence file does not execute PR-G1.5 or any MCF action. The one-time bootstrap has been executed by the operator; no subsequent role grant has been executed.

BuildPlan: docs-only § PR-BS-X post-execution evidence for operator-executed super_admin bootstrap per merged PR-BS-1 (656ac77) §6 and PR-LO-1 (5acdd73) local-only mode
Finding: operator executed the one-time bootstrap adding only super_admin to anant@selenite.co; before/after Cognito role state and fresh decoded ID token confirm the role is present; PR-G1.5 remains separate and unexecuted
Rollback: if this evidence is found invalid before merge, close this PR unmerged; if rollback of Cognito state is required, execute PR-BS-1 §7 and author a separate rollback evidence file
Phase0Impact: none

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
