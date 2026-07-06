---
uid: super-admin-bootstrap-dbcp
title: Super-Admin Bootstrap DBCP — one-time AWS-side provisioning of the first super_admin role on anant@selenite.co (PR-BS-1; sibling of Catalog DBCP PR-4; prerequisite of PR-G1.5 service-first first-grant; bc-infra R12 IAM and PR-G1.5 execution explicitly out of scope)
description: One-shot governance document authorizing the operator to grant the literal `super_admin` role to a single named identity via the operator's own AWS credentials (Cognito Console or AWS CLI). Required because no `super_admin` exists in the Cognito user pool today, which means no application endpoint (`POST /api/admin/mcf/role-grants` guarded by `SuperAdminGuard`) can be invoked. This is the genuine exception to the service-first discipline locked in Catalog DBCP PR-4 + PR-G1 D-6 + Catalog HR1; every subsequent role grant — including all 11 non-super-admin roles and any future super_admin promotion — MUST go through the service.
status: proposed
date: 2026-05-31
project: bc-docs
domain: contracts
subdomain: catalog
focus: super-admin-bootstrap
supersedes:
superseded_by:
---

## 1. Authority + scope

### 1.1 Authority chain

| Authority | Where | What it locks |
|---|---|---|
| Platform Role Catalog DBCP PR-4 | `docs/implementation/platform-role-catalog-dbcp.md` §3 PR-4 (merged `b2d693d`, PR #36) + §5.1 alignment (merged `b359d11`, PR #37) | First `super_admin` MUST be provisioned via a SEPARATE bootstrap DBCP that names target, attestation, AWS-side action, and evidence destination |
| Catalog DBCP §6 | same file, lines 312-322 | The required sections this DBCP must carry |
| PR-G1 design DBCP §D-6 | `docs/implementation/mcf-role-grant-service-dbcp.md` (merged `d60a742`, PR #34) | `super_admin` bootstrap is "separate-DBCP-territory"; the role-grant service does not bootstrap itself |
| Catalog DBCP §10 sequencing | same Catalog DBCP, §10 (Sequencing update, lines 377-409) | PR-BS-1 = this DBCP, named AFTER PR-CAT-1 (line 388); PR-BS-X = evidence commit; PR-G1.5 may only fire after BOTH |
| Catalog DBCP HR1 (service-first generalized) | Catalog DBCP §8 HR1 | Carves the one-time-bootstrap exception; this DBCP is the one and only invocation of that exception |

This DBCP is **subordinate** to all of the above. It does not supersede, does not amend, does not introduce new HR rules at the catalog level. It is a one-shot governance artifact whose useful life ends after PR-BS-X (evidence commit) merges.

### 1.2 In scope

- Authorize the operator to grant the literal `super_admin` role to ONE named Cognito identity via the operator's own AWS credentials
- Specify the allowed AWS-side mechanism (Cognito Console OR AWS CLI `admin-update-user-attributes`)
- Specify evidence requirements (before-roles, after-roles, timestamp, attestation, token re-fetch, redaction)
- Specify rollback procedure (remove only `super_admin`; preserve all pre-existing roles)
- Specify sequencing relative to bc-infra R12 IAM and PR-G1.5

> **Note on document length.** This DBCP is ~480 lines, exceeding the ~50-150 line estimate in Catalog DBCP §3 PR-4. The overrun is intentional: this is a one-time identity-bootstrap runbook covering two execution paths (AWS Console + AWS CLI with platform-specific safe forms), 18-field evidence schema, full rollback procedure, bc-infra R12 IAM dependency clarification, 7 hard rules, 12-risk register, and 3 deferred open questions. The structure mirrors the Catalog DBCP's own pattern (HR block + risk register + sequencing). Each section is operationally necessary for a bootstrap action that cannot be safely re-run; the document is read once before execution and once during evidence review.

### 1.3 Explicitly out of scope

- **Any role other than `super_admin`** — `admin`, `tenant_admin`, `platform_admin`, `schema_*`, `operator`, `analyst`, `viewer`, `mcf_author`, `mcf_publisher` are NOT granted here under any circumstance
- **M11 / M12 / M12.5 / M13 / M14** — no metric intake, no panel-run, no materialization, no evaluator, no publication invocation
- **Any metric-contract action** — no MC create / update / publish / supersede / certify; no metric_definition mutation
- **bc-infra IAM PR (R12)** — the bc-core service-role IAM policy that lets the role-grant SERVICE call Cognito at runtime is a SEPARATE bc-infra concern. This DBCP uses the OPERATOR'S OWN AWS credentials (not the service's IAM role)
- **PR-G1.5 invocation** — the post-bootstrap first service-driven grant is a separate operator action gated on BOTH bootstrap-executed AND bc-infra R12 IAM merged
- **bc-core code changes** — no source modification, no schema migration, no DDL
- **bc-admin / bc-portal changes** — no UI work
- **Any tenant DB mutation** — `tbc_apex_dev` and any other tenant DB untouched
- **Bootstrap of a second `super_admin`** — if a second super_admin is ever needed, it MUST go through the service (`POST /api/admin/mcf/role-grants` extended OR a new service surface); this DBCP authorizes the one-time exception ONLY

## 2. Why bootstrap is the exception, not the rule

Per Catalog DBCP §8 HR1, every platform role grant MUST go through a bc-core service. The one and only carve-out is the first `super_admin` grant — because:

1. `POST /api/admin/mcf/role-grants` is guarded by `SuperAdminGuard` (bc-core `src/auth/guards/super-admin.guard.ts`, merged in PR-G1.1 / `f8e8042`)
2. `SuperAdminGuard.canActivate()` returns `user.roles.includes('super_admin')` (no admin bypass per Catalog DBCP PR-7)
3. No Cognito identity currently carries `super_admin` (operator verified empirically; Catalog DBCP §2.3 confirms anant carries `["platform_admin", "schema_author", "operator", "analyst"]`)
4. Therefore the endpoint cannot be called by anyone

This is a bootstrap problem: the role-grant service exists, but the role needed to call it does not exist. Bootstrap is the externally-supplied first cause that lets the service take over.

After this DBCP's bootstrap executes:
- The operator's JWT carries `super_admin`
- `POST /api/admin/mcf/role-grants` becomes callable (subject to bc-infra R12 IAM landing first)
- All future role grants — including the operator's own `mcf_author` for PR-G1.5 — go through the service
- This DBCP's useful life ends; it becomes an archived historical artifact

## 3. Target identity

The bootstrap MUST land on exactly ONE Cognito identity:

| Field | Value | Source |
|---|---|---|
| email | `anant@selenite.co` | Catalog DBCP §2.3 + PR-E1 JWT decode evidence (bc-core `3adacbd`, PR #173) |
| sub (Cognito UUID) | `8bdb9bd0-8827-4cc8-b640-2087658f1eb6` | Catalog DBCP §2.3 + PR-E1 JWT decode evidence |
| display_name | (operator-supplied; not material to bootstrap) | — |
| tenant_id (custom:tenant_id) | `demo-selenite` | Catalog DBCP §2.3 (note: legacy slug; demo tenant apex switchover per memory `demo_tenant_apex.md` does not affect this bootstrap) |

### 3.1 Expected current roles (operator MUST verify and attest at execution)

Per Catalog DBCP §2.3 (PR-E1 JWT decode evidence), the operator's current `custom:roles` attribute is expected to be:

```
["platform_admin", "schema_author", "operator", "analyst"]
```

**The operator MUST empirically verify this at execution time** (via Cognito Console OR `aws cognito-idp admin-get-user`) and record the actual observed value in evidence as the "before-roles" snapshot. If the observed roles differ from the expected list above, the operator MUST stop, surface the discrepancy via a session note, and authorize a new path before proceeding — silent drift correction is not allowed.

### 3.2 Expected after-roles

After bootstrap, the operator's `custom:roles` MUST be:

```
["platform_admin", "schema_author", "operator", "analyst", "super_admin"]
```

Exact membership: existing 4 + `super_admin` literal appended (order is not contractually material; ECMAScript Set iteration preserves insertion order in the JWT consumer's parse logic per Catalog DBCP §5.1, but the platform does not enforce a canonical role order).

**Invariant**: the bootstrap MUST add `super_admin` and MUST NOT remove or modify any of the 4 pre-existing roles. The before-vs-after diff is the primary structural check on the bootstrap action.

## 4. Cognito environment

| Field | Value | Notes |
|---|---|---|
| AWS Account | `546549546538` | per CLAUDE.md §AWS — barecount account |
| AWS Region | `ap-south-1` | per CLAUDE.md §AWS — region |
| AWS CLI Profile | `barecount` | per CLAUDE.md §AWS — never use default profile |
| Cognito User Pool ID | `ap-south-1_bM5xehxIx` | per bc-core auth config + cognito-admin.service.spec.ts |
| Environment | `dev` | bootstrap targets the dev pool; prod/staging bootstrap is a separate future DBCP if/when prod pool is provisioned |

The operator's own AWS credentials (associated with the `barecount` profile) are used to authenticate the AWS-side action. The bc-core service-role IAM policy (R12) is NOT involved in this bootstrap — that's the SERVICE's identity, not the operator's identity. They are distinct concerns.

## 5. Allowed bootstrap mechanism

Two equivalent paths. Operator chooses one.

### 5.1 Path A — AWS Cognito Console (recommended for first-time)

1. Sign in to AWS Console with credentials linked to AWS profile `barecount` (account `546549546538`, region `ap-south-1`)
2. Navigate: Cognito → User pools → `ap-south-1_bM5xehxIx` → Users
3. Locate `anant@selenite.co` (or search by sub `8bdb9bd0-8827-4cc8-b640-2087658f1eb6`)
4. Open user → "User attributes" tab
5. Locate `custom:roles` attribute; copy the current JSON string verbatim into evidence as "before-roles" raw value
6. Edit `custom:roles` to the after-state JSON: `["platform_admin","schema_author","operator","analyst","super_admin"]`
7. Save changes; capture the ISO 8601 UTC timestamp of save into evidence
8. Re-read the attribute and copy the new JSON string verbatim into evidence as "after-roles" raw value
9. Proceed to §6 token re-fetch verification

### 5.2 Path B — AWS CLI

Prerequisites:
- `aws` CLI installed (Operator's machine: confirm with `aws --version`)
- AWS profile `barecount` configured (confirm with `aws configure list --profile barecount`)
- Operator session token valid (`aws sts get-caller-identity --profile barecount` returns account `546549546538`)

**Read current roles (before-state):**

```bash
AWS_PROFILE=barecount aws cognito-idp admin-get-user \
  --user-pool-id ap-south-1_bM5xehxIx \
  --username 8bdb9bd0-8827-4cc8-b640-2087658f1eb6 \
  --region ap-south-1
```

Capture the `UserAttributes` array entry for `Name: custom:roles` into evidence as before-roles raw value.

**Write super_admin (mutating step):**

**Linux / macOS bash (single-quoted shorthand works as-is):**

```bash
AWS_PROFILE=barecount aws cognito-idp admin-update-user-attributes \
  --user-pool-id ap-south-1_bM5xehxIx \
  --username 8bdb9bd0-8827-4cc8-b640-2087658f1eb6 \
  --user-attributes 'Name=custom:roles,Value=["platform_admin","schema_author","operator","analyst","super_admin"]' \
  --region ap-south-1
```

> **⚠ Windows note (MANDATORY for operator-on-Windows execution).** The AWS CLI shorthand form `--user-attributes 'Name=custom:roles,Value=[...]'` is **unsafe/unreliable on Windows**: `aws.exe` is a Windows-native executable that uses Windows command-line argument parsing (`CommandLineToArgvW`) regardless of which shell invokes it (PowerShell, cmd.exe, OR git bash / MINGW). Embedded JSON arrays with double-quotes inside single-quoted shell args can be silently stripped or partially parsed, producing a malformed `custom:roles` Value that **wipes pre-existing roles** — this is risk R-BS-1 in concrete form. The operator MUST use the `--cli-input-json` form on Windows. Save the following JSON to a file `update-roles.json`, then invoke the CLI with `--cli-input-json file://update-roles.json`:
>
> ```json
> {
>   "UserPoolId": "ap-south-1_bM5xehxIx",
>   "Username": "8bdb9bd0-8827-4cc8-b640-2087658f1eb6",
>   "UserAttributes": [
>     {
>       "Name": "custom:roles",
>       "Value": "[\"platform_admin\",\"schema_author\",\"operator\",\"analyst\",\"super_admin\"]"
>     }
>   ]
> }
> ```
>
> ```bash
> AWS_PROFILE=barecount aws cognito-idp admin-update-user-attributes \
>   --cli-input-json file://update-roles.json \
>   --region ap-south-1
> ```
>
> The JSON-file form is universally safe across all shells and platforms; no quoting layer parses the embedded array. **MUST preserve all 4 pre-existing roles verbatim; MUST add only the literal `super_admin`.** A typo in the file is the operator's only remaining risk and is caught by the §6.1 `before_roles_observed` vs `after_roles_observed` diff. The file SHOULD be deleted after evidence is captured (it contains the role list but no credentials).

Capture the operation ISO 8601 UTC timestamp + the `ResponseMetadata.RequestId` from the AWS CLI debug output into evidence.

**Read after-state:**

Re-run the admin-get-user command above and capture the new `custom:roles` value into evidence as after-roles raw value.

### 5.3 What is NOT allowed

- ❌ `POST /api/admin/mcf/role-grants` — does not exist on the call-graph because no super_admin exists yet (chicken-and-egg)
- ❌ Any other bc-core endpoint — none have a bootstrap path
- ❌ Any bc-admin UI action — bc-admin is a frontend; it would call the bc-core endpoint, which is not callable
- ❌ Direct DB INSERT/UPDATE against any Cognito-mirrored table — Cognito is the source of truth for identity attributes; bc-core does not maintain a Cognito mirror
- ❌ Cognito-side bulk import — only the single named identity is in scope
- ❌ Any AWS action against any non-dev pool (no staging, no prod, no test)
- ❌ Operator-written AWS SDK scripts (boto3, aws-sdk-js, aws-sdk-go, etc.) OR MCP-mediated raw AWS calls (e.g., `mcp__AWS_API_MCP_Server__call_aws`) for this bootstrap — only the §5.1 Console path or §5.2 CLI path is authorized. SDK-based or MCP-based execution would bypass the operator-attestation surface this DBCP relies on; a future bootstrap-class DBCP could authorize an SDK path explicitly, but this one does not.

## 6. Evidence requirements

The operator MUST commit an evidence file at:

```
bc-docs-v3/docs/operations/role-bootstrap-evidence/<YYYY-MM-DD>-super-admin-bootstrap.md
```

Where `<YYYY-MM-DD>` is the UTC date of bootstrap execution. The file is the deliverable of PR-BS-X (separate evidence-commit PR).

### 6.1 Required evidence fields

| Field | Format | Source |
|---|---|---|
| `bootstrap_started_at` | ISO 8601 UTC timestamp | operator's local clock at start of execution |
| `bootstrap_completed_at` | ISO 8601 UTC timestamp | operator's local clock at completion |
| `aws_account_id` | `546549546538` | verbatim from `aws sts get-caller-identity` |
| `aws_region` | `ap-south-1` | verbatim |
| `cognito_user_pool_id` | `ap-south-1_bM5xehxIx` | verbatim |
| `target_user_email` | `anant@selenite.co` | verbatim |
| `target_user_sub` | `8bdb9bd0-8827-4cc8-b640-2087658f1eb6` | verbatim |
| `mechanism_used` | `aws-console` OR `aws-cli` | operator records which §5 path was taken |
| `before_roles_observed` | JSON array (raw from admin-get-user or Console copy) | empirical capture at start |
| `before_roles_expected` | JSON array `["platform_admin","schema_author","operator","analyst"]` | per Catalog DBCP §2.3 |
| `before_observed_matches_expected` | `true` OR `false` (with explanation if false) | operator's check |
| `after_roles_observed` | JSON array (raw from admin-get-user or Console copy) | empirical capture at end |
| `after_roles_expected` | JSON array `["platform_admin","schema_author","operator","analyst","super_admin"]` | computed |
| `roles_diff_added` | `["super_admin"]` (must be exactly this) | computed |
| `roles_diff_removed` | `[]` (must be empty) | computed |
| `aws_request_id` (CLI path only) | string | from CLI `--debug` output OR ResponseMetadata |
| `cloudtrail_event_id` | string (best-effort) | operator queries CloudTrail for the `AdminUpdateUserAttributes` event within 5 minutes; if not found, record `"not_found_within_5_min"` |
| `operator_attestation_text` | string ≥ 100 chars | see §6.2 |
| `token_refetch_evidence` | decoded JWT payload (signature redacted) | see §6.3 |

### 6.2 Operator attestation block

The evidence MUST include a free-text attestation block ≥ 100 characters in length, signed by the operator (email + UTC timestamp), confirming:

- "I am `anant@selenite.co`, the operator authorized by Catalog DBCP §2.3"
- "I executed this bootstrap action under my own AWS credentials linked to AWS profile `barecount`"
- "I verified the before-roles empirically before mutating and the after-roles empirically after mutating"
- "I confirm only `super_admin` was added; all 4 pre-existing roles are preserved"
- "I confirm no other identity was modified during this bootstrap"
- "I understand subsequent role grants (including my own future grants) MUST go through `POST /api/admin/mcf/role-grants` or its successor service; this bootstrap exception is one-time only"

### 6.3 Token re-fetch evidence

After bootstrap, the operator MUST:

1. Sign out of any existing bc-portal / bc-admin session
2. Sign back in to obtain a fresh Cognito ID token
3. Decode the JWT payload (via `devhub_get_cognito_token` MCP tool OR `jwt.io` paste OR `aws cognito-idp admin-initiate-auth` followed by JWT decode)
4. Copy the decoded payload into evidence — **with the JWT signature redacted** (replace the third base64-segment with the literal string `"<redacted>"`)
5. Confirm `custom:roles` in the decoded payload contains the string `"super_admin"`

**Redaction discipline**: the raw JWT (header.payload.signature) MUST NEVER be committed. Only the decoded payload (header + payload as JSON) is acceptable, with the signature segment redacted. AWS access keys, session tokens, or any other secret material MUST be absent from the evidence file. The `aws_request_id` and `cloudtrail_event_id` are non-secret and acceptable.

### 6.4 What evidence MUST NOT contain

- ❌ Raw JWT signature segment
- ❌ AWS access key / secret key / session token
- ❌ Cognito client secret
- ❌ Cognito Console URLs in any capture form — including screenshots, copy-pasted URLs, terminal redirect logs, browser-history exports, OR command output captures. Cognito Console URLs carry session-identifier query parameters that can leak federation context. If the operator captures any artifact that contains a Console URL substring, the URL portion MUST be redacted before commit.
- ❌ Any custom attribute other than `custom:roles` from the operator's Cognito record (e.g., `custom:tenant_id` is acceptable since already documented; arbitrary undocumented custom attributes MUST NOT be exposed)

## 7. Rollback

If, post-bootstrap and pre-PR-G1.5, the operator decides to revert (reasons may include: suspected compromise, identity-switch decision, rollback test, change of authorization):

### 7.1 Procedure

The operator executes a second `admin-update-user-attributes` call (Console or CLI), restoring `custom:roles` to the pre-bootstrap value captured in §6.1 evidence as `before_roles_observed`.

**Linux / macOS bash CLI form:**

```bash
AWS_PROFILE=barecount aws cognito-idp admin-update-user-attributes \
  --user-pool-id ap-south-1_bM5xehxIx \
  --username 8bdb9bd0-8827-4cc8-b640-2087658f1eb6 \
  --user-attributes 'Name=custom:roles,Value=<before_roles_observed JSON verbatim>' \
  --region ap-south-1
```

> **⚠ Windows safe form (per §5.2 Windows note).** On Windows (PowerShell / cmd.exe / git bash), the shorthand above is unsafe. Save the following JSON to `rollback-roles.json` (where `<before_roles_observed JSON verbatim>` is the literal pre-bootstrap value captured in §6.1 evidence), then invoke:
>
> ```json
> {
>   "UserPoolId": "ap-south-1_bM5xehxIx",
>   "Username": "8bdb9bd0-8827-4cc8-b640-2087658f1eb6",
>   "UserAttributes": [
>     { "Name": "custom:roles", "Value": "<before_roles_observed JSON verbatim, with inner quotes escaped>" }
>   ]
> }
> ```
>
> ```bash
> AWS_PROFILE=barecount aws cognito-idp admin-update-user-attributes \
>   --cli-input-json file://rollback-roles.json \
>   --region ap-south-1
> ```
>
> **MUST restore the exact 4 pre-existing roles; MUST NOT add any role not present in `before_roles_observed`; MUST remove only the `super_admin` literal.** The §7.2 invariant + §7.3 evidence diff (`roles_diff_removed: ["super_admin"]`, `roles_diff_added: []`) are the structural checks; a typo here would surface as a non-`[]` diff.

**Console form**: navigate to the user attribute, paste the `before_roles_observed` JSON verbatim, save.

### 7.2 Rollback invariant

Rollback MUST restore the exact pre-bootstrap state. Specifically:

- Remove ONLY the `super_admin` literal
- Preserve all 4 pre-existing roles in their original membership
- Do not add any role not present in `before_roles_observed`
- Do not modify any other Cognito attribute

### 7.3 Rollback evidence

If rollback is invoked, the operator MUST commit a separate evidence file at:

```
bc-docs-v3/docs/operations/role-bootstrap-evidence/<YYYY-MM-DD>-super-admin-bootstrap-rollback.md
```

With the same §6.1 schema applied to the rollback action:
- `before_roles_observed` = the post-bootstrap state (carries `super_admin`)
- `after_roles_observed` = the post-rollback state (no `super_admin`)
- `roles_diff_added` = `[]`
- `roles_diff_removed` = `["super_admin"]`
- Token re-fetch + signature redaction same as §6.3
- Attestation block same as §6.2 with rollback rationale appended (≥ 50 chars on rationale alone)

### 7.4 Post-rollback state

PR-G1.5 cannot fire after rollback (no super_admin). To proceed again, a NEW PR-BS-1' DBCP MUST be authored (this one cannot be re-used; one-time means one-time).

## 8. Sequencing

```
PR-CAT-1   bc-core      MERGED `20a4269`      — satisfied predecessor (per Catalog DBCP §10 line 388:
                                                  "PR-BS-1 AFTER PR-CAT-1"); KNOWN_PLATFORM_ROLES catalog +
                                                  JWT filter + DTO module-load assertion live on bc-core main
↓
PR-BS-1    bc-docs-v3   THIS DBCP             — proposed → review → merge
↓
[operator executes bootstrap per §5; captures evidence per §6]
↓
PR-BS-X    bc-docs-v3   evidence commit       — proposed → review → merge
↓ (independent — can land before, during, or after PR-BS-X but NOT after PR-G1.5)
bc-infra R12  bc-infra  IAM policy PR for     — proposed → review → merge
              the bc-core service role to
              call Cognito at runtime
↓ (gate: BOTH PR-BS-X merged AND bc-infra R12 merged)
PR-G1.5    bc-core      first service-driven   — operator invokes
                        role grant via
                        POST /api/admin/mcf/role-grants
                        (target: anant@selenite.co,
                        desired_mcf_roles: ["mcf_author"])
```

### 8.1 PR-BS-1 (this DBCP)

- Status: proposed
- Predecessor gate: PR-CAT-1 (bc-core PR #175, merged at `20a4269`) — **satisfied**, per Catalog DBCP §10 line 388 ("PR-BS-1 AFTER PR-CAT-1"). The KNOWN_PLATFORM_ROLES catalog, JWT filter, and DTO module-load assertion are live on bc-core main, so a JWT carrying the post-bootstrap `super_admin` role will pass the catalog filter cleanly (the literal `super_admin` is in the 12-entry Set).
- Authority: Catalog DBCP PR-4 + §6 (Bootstrap path, lines 312-322)
- Deliverable: this single docs file
- Merge gate: 3-agent strict review (same pattern as PR #34 / #35 / #36 / #172 / #174 / #175)
- Phase0Impact: none

### 8.2 PR-BS-X (evidence commit)

- Status: NOT EXPECTED until operator executes
- Authority: this DBCP (PR-BS-1)
- Deliverable: `bc-docs-v3/docs/operations/role-bootstrap-evidence/<YYYY-MM-DD>-super-admin-bootstrap.md`
- Merge gate: structural-completeness check (all §6.1 fields present + attestation ≥ 100 chars + signature redacted)
- Phase0Impact: none (docs-only commit of post-action evidence)

### 8.3 bc-infra R12 IAM PR (separate repo)

- Status: NOT YET STARTED — surfaced by Catalog DBCP §11 R12 + PR-G1.0 R12
- Authority: PR-G1.0 R12 + Catalog DBCP §11 R12
- Deliverable: bc-infra repo PR adding the IAM policy that grants the bc-core service role permission to call `cognito-idp:AdminGetUser` + `cognito-idp:AdminUpdateUserAttributes` against pool `ap-south-1_bM5xehxIx`
- Independence: this IAM PR is orthogonal to PR-BS-1 / PR-BS-X (operator uses own credentials, not the service role); BOTH bootstrap-executed AND IAM-merged are required before PR-G1.5

### 8.4 PR-G1.5 (first service-driven grant)

- Status: gated on §8.2 AND §8.3
- Authority: PR-G1 design DBCP + PR-G1.0 implementation DBCP + PR-G1.1 service code (merged `f8e8042`)
- Action: operator POSTs to `/api/admin/mcf/role-grants` with target `anant@selenite.co`, desired_mcf_roles `["mcf_author"]`, reason_text ≥ 20 chars, source_pr_or_dbcp_text citing PR-G1 + this DBCP
- Expected effect: Cognito custom:roles attribute on anant updated to add `mcf_author`; audit row written to `mcf.role_grant_audit`; 201 response with `NOTE_TEXT_ON_GRANT_SUCCESS` per PR-G1.0 §I-7
- Phase0Impact: none (does not touch Phase 0 substrate)

## 9. bc-infra R12 IAM dependency clarification

**R12 from Catalog DBCP §11 + PR-G1.0 R12 remains required and unchanged.**

Bootstrap (this DBCP) uses the OPERATOR'S AWS credentials directly. The operator's IAM identity already has Cognito-admin permissions because they administer the AWS account. No additional IAM grant is needed for this DBCP.

PR-G1.5 (post-bootstrap first service grant) uses the BC-CORE SERVICE's IAM role (whichever role the bc-core ECS task / EC2 instance / Lambda assumes at runtime). The service role does NOT currently have permission to call `cognito-idp:AdminUpdateUserAttributes`. Without that permission, `POST /api/admin/mcf/role-grants` will return `CognitoServiceFailureError` at the SDK boundary (per PR-G1.1 F-D fail-closed enforcement, merged `f8e8042`).

The R12 IAM PR — separate, in bc-infra repo — adds:
- `cognito-idp:AdminGetUser` on resource `arn:aws:cognito-idp:ap-south-1:546549546538:userpool/ap-south-1_bM5xehxIx`
- `cognito-idp:AdminUpdateUserAttributes` on same resource

This DBCP does NOT author the R12 IAM policy. This DBCP does NOT block on R12 either — bootstrap can execute before, during, or after R12 merges. PR-G1.5 cannot fire until BOTH bootstrap-executed AND R12-merged.

## 10. Hard rules (HR-BS-1 through HR-BS-7)

### HR-BS-1 — One-time exception

This bootstrap path is invoked exactly ONCE. After PR-BS-X (evidence) merges, this DBCP enters archived-historical state and CANNOT be re-invoked. Subsequent `super_admin` grants — including bootstrap-class needs in staging / prod pools — require a NEW PR-BS-1' DBCP authored against the new pool / identity, OR (preferred) extension of the service surface to handle bootstrap-class grants.

### HR-BS-2 — Single literal granted

Only the literal `super_admin` string is added to `custom:roles`. The DBCP does not authorize granting `admin`, `mcf_author`, `mcf_publisher`, `tenant_admin`, `platform_admin` (already present), `schema_*`, `operator` (already present), `analyst` (already present), `viewer`, or any future role.

### HR-BS-3 — Operator credentials only

The AWS-side action uses the operator's own AWS credentials linked to profile `barecount`. The bc-core service IAM role, bc-admin client credentials, and any other identity are NOT used.

### HR-BS-4 — Evidence is mandatory

Bootstrap is not "complete" until PR-BS-X merges. The operator MUST NOT claim PR-G1.5 readiness until evidence is committed and merged. A bootstrap executed without subsequent evidence commit is a discipline violation per Catalog DBCP §8 HR rules.

### HR-BS-5 — Token re-fetch is mandatory

The operator MUST sign out + sign in + decode the new JWT + verify `super_admin` is in the payload. Cached tokens issued before bootstrap continue to lack `super_admin` until they expire (Cognito ID-token default TTL: 1 hour). Skipping the re-fetch leaves PR-G1.5 callable only after token expiry — a subtle source of confusion the re-fetch eliminates.

### HR-BS-6 — Rollback evidence if invoked

If rollback is exercised, a separate evidence file MUST be committed per §7.3. A silent rollback without evidence is a discipline violation.

### HR-BS-7 — No bootstrap-by-AI

Claude (this assistant) MUST NOT execute the bootstrap. The bootstrap is operator-executed end-to-end. Claude may:
- Author this DBCP (the present action)
- Help draft the evidence-file scaffolding (text only; no AWS calls)
- Review the committed evidence for structural completeness

Claude MUST NOT:
- Run `aws cognito-idp admin-update-user-attributes` under any circumstance
- Open the Cognito Console
- Fetch the operator's JWT for them
- Decode the JWT and commit the decoded payload (operator decodes + commits — preserves attestation chain)

## 11. Risks

| ID | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R-BS-1 | Operator typo strips pre-existing roles | Medium | §6.1 mandates before-roles capture + before-vs-after diff in evidence; §3.1 mandates verify-and-attest before mutating |
| R-BS-2 | Bootstrap binds wrong identity (e.g., test user) | Low | §3 locks target sub + email; mechanism §5 uses sub-as-username (not display name) |
| R-BS-3 | Concurrent edit race (another admin edits simultaneously) | Very low | Only one operator authorized (anant); no other admins on dev account |
| R-BS-4 | JWT cache not refreshed; operator believes bootstrap failed | Medium | HR-BS-5 mandates explicit re-fetch; §6.3 mandates decoded-payload evidence |
| R-BS-5 | Bootstrap used to grant additional roles beyond super_admin | Low | HR-BS-2 + §6.1 `roles_diff_added` MUST equal `["super_admin"]` exactly |
| R-BS-6 | Evidence not redacted; JWT signature leaks | Medium | §6.3 redaction discipline + §6.4 explicit prohibitions |
| R-BS-7 | Operator uses bootstrap procedure when service exists for subsequent grants | Medium | HR-BS-1 one-time framing; Catalog DBCP HR1 service-first generalized; this DBCP enters archived state after PR-BS-X |
| R-BS-8 | bc-infra R12 IAM not landed before PR-G1.5 attempt | High | §8 sequencing makes R12 a gate alongside bootstrap; PR-G1.5 cannot fire without it; PR-G1.1 F-D enforcement throws CognitoServiceFailureError if IAM missing |
| R-BS-9 | Operator runs CLI from wrong AWS profile and mutates wrong pool | Low | §5.2 requires verification via `aws sts get-caller-identity` before mutation; profile name explicit in every CLI step |
| R-BS-10 | CloudTrail event not found within 5 min | Low | §6.1 allows `"not_found_within_5_min"` literal; the AWS RequestId is the primary correlation key |
| R-BS-11 | Wrong Cognito pool (staging / prod) targeted | Very low | §4 locks `ap-south-1_bM5xehxIx` dev pool; CLI commands carry pool ID inline; Console path requires deliberate pool selection |
| R-BS-12 | Bootstrap executed but evidence delayed indefinitely | Medium | HR-BS-4 mandates evidence; session-close discipline (D268) catches if operator forgets |

## 12. Open questions (deferred)

### OQ-BS-1 — How to confirm no other super_admin exists at execution time

Catalog DBCP §3 PR-4 states "If no `super_admin` exists in the Cognito user pool, no one can call any platform role-grant endpoint." How does the operator confirm this empirically?

**Suggested check (operator runs at execution):**

The platform uses Cognito custom-attribute `custom:roles` (a JSON-array string), NOT Cognito Groups; the canonical pre-check is therefore a pool-wide scan of `custom:roles` for any user already carrying the `super_admin` literal. (Note: an earlier draft of this DBCP included a `list-users-in-group --group-name super_admin` snippet with a guessed grep pattern — that block was removed in amendment v2 because: (a) Cognito Groups are orthogonal to `custom:roles` and the platform doesn't use them, and (b) the grep pattern did not match Cognito's actual `ResourceNotFoundException` text, which would produce a false-positive "GROUP EXISTS" alarm on first run.)

```bash
AWS_PROFILE=barecount aws cognito-idp list-users \
  --user-pool-id ap-south-1_bM5xehxIx \
  --region ap-south-1 | \
  jq -r '.Users[] | select(.Attributes[]? | select(.Name=="custom:roles" and (.Value | contains("super_admin"))))'
```

Empty result = no super_admin currently exists in the pool. Non-empty = STOP and investigate (someone other than the bootstrap target already carries the role; bootstrap may be unnecessary OR a governance surprise needs surfacing).

**Decision**: deferred to PR-BS-X execution. The operator MAY perform this check and record the outcome in evidence as a §6.1 extension field `no_other_super_admin_confirmed_at: <ISO timestamp>` along with the literal stdout (empty array OR list of offending sub UUIDs). Not mandatory per Catalog DBCP §6 (which mandates pre-state verification of the NAMED TARGET only — covered by §3.1 + §6.1 `before_roles_observed`), but recommended for completeness on this single execution.

### OQ-BS-2 — Two-person authorization

Should the bootstrap require attestation from TWO operators (separation of duties)?

**Current stance**: NO. The platform has one operator (founder); SoD is impractical at this stage. Service-driven future grants are audited via `mcf.role_grant_audit` with `granted_by_*` fields, which provides a different chain-of-custody guarantee.

**Re-evaluation trigger**: when bc-core scales to multi-operator (any second operator joins), update Catalog DBCP §3 PR-7 to require SoD for super_admin grants, and grandfather this DBCP's single-attestation scheme as the v1 baseline.

### OQ-BS-3 — Prod / staging bootstrap

Out of scope here (Catalog DBCP §1.3). When prod pool is provisioned, a separate PR-BS-1' DBCP MUST be authored against that pool. This DBCP is dev-pool-specific.

## 13. Hard boundaries (non-execution of this PR)

This PR (PR-BS-1) is **docs-only**.

This PR does NOT:
- Call AWS
- Modify Cognito
- Grant any role
- Apply any DDL
- Mutate any substrate
- Touch any tenant DB
- Invoke M11 / M12 / M12.5 / M13 / M14
- Modify bc-core, bc-admin, bc-portal, or bc-infra
- Author or modify any ADR
- Add any npm or pip dependency
- Supersede any prior DBCP, ADR, or governance artifact

It introduces the procedural authority for a future operator action. The action itself happens in a separate session (PR-BS-X). The action's evidence merges in a separate PR.

## 14. References

- Platform Role Catalog DBCP: `docs/implementation/platform-role-catalog-dbcp.md` (merged `b2d693d`, PR #36; §5.1 amended `b359d11`, PR #37). §3 PR-4 names this bootstrap. §6 lists the required sections. §10 sequences PR-BS-1 → PR-BS-X → PR-G1.5 (line 388 explicitly: "PR-BS-1 AFTER PR-CAT-1"). §8 HR1 service-first generalized. §2.3 operator roles baseline.
- PR-G1 design DBCP: `docs/implementation/mcf-role-grant-service-dbcp.md` (merged `d60a742`, PR #34). §D-6 names super_admin bootstrap as separate-DBCP-territory.
- PR-G1.0 implementation DBCP: `docs/implementation/mcf-role-grant-service-implementation-dbcp.md` (merged `ec7053d`, PR #35). R12 (bc-infra IAM dependency) remains required.
- PR-G1.1 (bc-core MCF role-grant service): bc-core merge `f8e8042` (PR #174). `SuperAdminGuard` lives in `src/auth/guards/super-admin.guard.ts`; F-D fail-closed enforcement in `cognito-admin.service.ts`.
- PR-CAT-1 (bc-core catalog enforcement): bc-core merge `20a4269` (PR #175). `KNOWN_PLATFORM_ROLES` catalog + JWT filter; the JWT post-bootstrap will carry `super_admin` and pass through the catalog cleanly because `super_admin` is in the 12-entry Set.
- PR-E1 (bc-core readiness evidence): bc-core merge `3adacbd` (PR #173). JWT decode evidence is the §3.1 expected-roles baseline.
- AWS account / region / profile policy: CLAUDE.md §AWS.
- Cognito user pool ID: bc-core `src/auth/cognito-admin/cognito-admin.service.spec.ts` + `bc-core/.env.example`.
- Session discipline ADR (D268): `docs/adrs/ADR-ebf0b4.md`. Bootstrap evidence skipped = D268 violation.

BuildPlan: docs-only § super_admin bootstrap DBCP for one-time AWS-side first-grant per Catalog DBCP PR-4
Finding: Catalog DBCP §2.2 gap "No bootstrap path for super_admin"; Catalog DBCP §3 PR-4 names this DBCP as the closure; PR-G1 §D-6 deferred to separate DBCP
Rollback: revert this PR; bootstrap remains un-authorized; PR-G1.5 remains blocked on the catalog-named gap (no behavioral regression on main; pure procedural removal)
Phase0Impact: none

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
