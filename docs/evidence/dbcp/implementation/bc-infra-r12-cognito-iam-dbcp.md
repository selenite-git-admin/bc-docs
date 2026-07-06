---
uid: bc-infra-r12-cognito-iam-dbcp
title: bc-infra R12 Cognito IAM DBCP — least-privilege Cognito Admin permissions for bc-core runtime role to enable PR-G1.5 service-driven role grants (dev pool only; staging/prod out of scope; no wildcards; two locked actions; bc-core source + bc-infra implementation PR separate; this DBCP is the governance lock, not the apply)
description: One-shot governance DBCP authorizing a future bc-infra repo PR that attaches a least-privilege IAM policy statement to the bc-core deployed runtime role (ECS task / Lambda / EC2 — exact infra identifier to be confirmed in the bc-infra implementation PR). The policy grants ONLY `cognito-idp:AdminGetUser` + `cognito-idp:AdminUpdateUserAttributes` on the single dev pool ARN. Without this IAM grant, the live `CognitoAdminService` in bc-core (per PR-G1.1 merge `f8e8042`) will fail closed with `CognitoServiceFailureError` at the SDK boundary when `POST /api/admin/mcf/role-grants` is invoked by an operator carrying `super_admin`. PR-G1.5 is gated on this DBCP-merged + bc-infra implementation merged AND deployed AND IAM-propagated, AND on PR-BS-X merged (operator-executed bootstrap evidence per PR-BS-1 `656ac77`). The two gates are parallel-capable.
status: proposed
date: 2026-05-31
project: bc-docs
domain: infrastructure
subdomain: iam
focus: bc-core-runtime-cognito-admin
supersedes:
superseded_by:
---

## 1. Authority + scope

### 1.1 Authority chain

| Authority | Where | What it locks |
|---|---|---|
| PR-G1.0 R12 | `docs/implementation/mcf-role-grant-service-implementation-dbcp.md` (merged `ec7053d`, PR #35) | R12 surfaces the bc-infra cross-repo dependency: the bc-core runtime needs Cognito-write IAM separately from the service-code change |
| Catalog DBCP §11 R12 | `docs/implementation/platform-role-catalog-dbcp.md` (merged `b2d693d`, PR #36; §5.1 amended `b359d11`, PR #37) | Catalog DBCP §11 R12 carries the bc-infra dependency forward; declares it required for PR-G1.5 |
| PR-BS-1 §9 | `docs/implementation/super-admin-bootstrap-dbcp.md` (merged `656ac77`, PR #38) | §9 clarifies operator-identity (bootstrap) vs service-identity (R12) are distinct concerns; this DBCP closes the service-identity side |
| PR-G1.1 `CognitoAdminService` | bc-core merge `f8e8042` (PR #174); files `src/auth/cognito-admin/cognito-admin.service.ts` + `src/auth/cognito-admin/cognito-admin.errors.ts` | The live SDK wrapper that will receive the IAM-denied error in absence of this policy; F-D fail-closed via `CognitoServiceFailureError` |

This DBCP is **subordinate** to all of the above. It does not supersede, does not amend, does not introduce new HR rules at the catalog level. It is a one-shot governance artifact whose useful life ends after the bc-infra implementation PR merges + the IAM is applied + smoke-tested via a PR-G1.5 invocation.

### 1.2 In scope

- Authorize attaching a least-privilege IAM policy statement to the bc-core deployed runtime role for the dev environment
- Lock the exact IAM Actions: `cognito-idp:AdminGetUser` + `cognito-idp:AdminUpdateUserAttributes`
- Lock the exact Resource ARN: dev pool only (`arn:aws:cognito-idp:ap-south-1:546549546538:userpool/ap-south-1_bM5xehxIx`)
- Specify the implementation expectations the bc-infra PR must meet (policy form, plan/diff evidence, rollback)
- Specify sequencing relative to PR-BS-X and PR-G1.5
- Specify the risk register (13 entries) the bc-infra PR must address or accept

### 1.3 Explicitly out of scope

- **Any IAM Action other than the 2 locked**: NO `cognito-idp:*` wildcard; NO `AdminCreateUser` / `AdminDeleteUser` / `AdminAddUserToGroup` / `AdminRemoveUserFromGroup` / `AdminConfirmSignUp` / `AdminInitiateAuth` / `AdminRespondToAuthChallenge` / `AdminResetUserPassword` / `AdminSetUserPassword` / `AdminUserGlobalSignOut` / `AdminListUserAuthEvents` / `AdminLinkProviderForUser` / `AdminDisableUser` / `AdminEnableUser` / `AdminListGroupsForUser` / any other Admin* API
- **Any Resource other than the dev pool ARN**: NO wildcard ARN; NO staging pool; NO prod pool; NO other AWS account
- **Any non-Cognito permission**: NO IAM passthrough; NO STS AssumeRole grants; NO Secrets Manager; NO SSM
- **Operator's user IAM**: NOT modified by this DBCP; operator uses own credentials for PR-BS-1 bootstrap (per PR-BS-1 §4)
- **bc-admin / bc-portal IAM**: NOT in scope; this is bc-core runtime only
- **CI/CD IAM**: NOT in scope; this is the runtime role, not the deployment role
- **Trust policy changes**: this DBCP authorizes the *permission policy* (resource-based or identity-based attachment), NOT the trust policy of the runtime role (which is upstream; if the trust policy is misconfigured, the runtime cannot assume the role — but trust policy work is a separate bc-infra concern)
- **AWS execution**: this PR is docs-only; the apply happens in the bc-infra PR
- **PR-G1.5 invocation**: this PR is the IAM-side gate; PR-G1.5 fires later after both IAM applied + PR-BS-X merged
- **M11 / M12 / M12.5 / M13 / M14**: explicitly NOT authorized; metric-contract action is out of scope here
- **Substrate mutation**: NO DDL; NO `bc_platform_dev` writes; NO tenant DB touch
- **Wider service-role permission cleanup**: if the bc-core service role has unrelated stale permissions, this DBCP does NOT authorize removing them — out-of-band cleanup is a separate bc-infra concern

## 2. Why this DBCP is needed (rationale chain)

1. **Live service exists, IAM does not.** `CognitoAdminService` is live on bc-core main `f8e8042` (PR-G1.1, PR #174). The constructor reads `AWS_REGION` + `auth.cognito.userPoolId` from `ConfigService`; the SDK call is `AdminUpdateUserAttributesCommand` against the user pool.

2. **Fail-closed at SDK boundary — two distinct error paths.** The bc-core service distinguishes two failure modes at the SDK boundary, mapping each to a distinct typed error class and HTTP response code:

   - **IAM denial path** (the relevant one for this DBCP). When the runtime role lacks the required `cognito-idp:*` permission, AWS SDK v3 raises `AccessDeniedException` with a populated `$metadata.requestId`. The bc-core `mapAwsError` handler at `cognito-admin.service.ts:148-151` maps this to `CognitoAccessDeniedError` (defined at `cognito-admin.errors.ts:19-25`). The `mcf-role-grant.controller.ts:91-97` maps `CognitoAccessDeniedError` to **HTTP 500 with `code: cognito_access_denied`**. In absence of the IAM policy this DBCP authorizes, every `POST /api/admin/mcf/role-grants` invocation that reaches Step 5 (the write call) will return HTTP 500 `cognito_access_denied`. Pre-write reads at Step 2 (`AdminGetUser`) would surface the same error if `AdminGetUser` permission is also missing.

   - **F-D missing-requestId path** (PR-G1.0 §I-3 + amendment v2 F-D). The F-D guard at `cognito-admin.service.ts:128-135` fires when the AWS response to `AdminUpdateUserAttributes` succeeds at the API layer but `$metadata.requestId` is undefined or empty (a network corruption / SDK config edge case). The service throws `CognitoServiceFailureError`, controller maps to **HTTP 500 with `code: cognito_service_failure`**. This is NOT the IAM-denied path — IAM denials have a populated requestId and arrive via `mapAwsError`, not the F-D guard.

   The two codes share HTTP 500 but the operator distinguishes by the `code` field in the response body. The service does not silently retry or bypass either path.

3. **Operator bootstrap uses operator's credentials, NOT the service role.** PR-BS-1 §4 + §9 lock the operator-identity vs service-identity boundary. The operator's `barecount` AWS profile carries admin permissions; the bc-core runtime role does not. PR-BS-1 bootstrap (operator-executed, AWS Console or `--cli-input-json` CLI) requires only operator IAM. PR-G1.5 (service-driven first-grant) requires service IAM — this DBCP authorizes that.

4. **Three-vendor M12 transcript evidence exists, but the service-discipline path is separately gated.** Bc-core's `scripts/audit-output/` carries three M12 first-real-run transcript evidence files dated 2026-05-30 (`mcf-m12-first-real-run-2026-05-30T08-33-58-901Z.evidence.jsonl`, `mcf-m12-first-real-run-2026-05-30T08-34-48-343Z.evidence.jsonl`, `mcf-m12-first-real-run-2026-05-30T08-35-19-117Z.evidence.jsonl`). Those artifacts are three-vendor transcript captures — they do NOT, on this DBCP's read, prove that the M12 service path has produced a real `APPROVE_FOR_DRAFT` verdict against live substrate via a JWT-carried `mcf_author` role grant. The live substrate state, verdict status, and binding to this DBCP's chain require independent re-verification before PR-G1.5 is invoked. This DBCP does NOT claim or rely on `APPROVE_FOR_DRAFT` being guaranteed for any specific panel-run.

5. **Bc-infra is a separate repo with separate review discipline.** The IAM policy JSON, the role attachment mechanism (Terraform / CloudFormation / CDK / Pulumi — to be confirmed in the implementation PR), the plan/diff artifacts, and the apply evidence all live in bc-infra. This DBCP locks the *scope* of the change at the governance level; the bc-infra PR locks the *form*.

## 3. Target environment

### 3.1 Locked values

| Field | Value | Source |
|---|---|---|
| AWS Account | `546549546538` | per CLAUDE.md §AWS — barecount account |
| AWS Region | `ap-south-1` | per CLAUDE.md §AWS |
| Cognito User Pool ID | `ap-south-1_bM5xehxIx` | per bc-core auth config + `cognito-admin.service.spec.ts` |
| Cognito User Pool ARN | `arn:aws:cognito-idp:ap-south-1:546549546538:userpool/ap-south-1_bM5xehxIx` | derived from account + region + pool ID per AWS ARN format |
| Environment | `dev` | Cognito pool `ap-south-1_bM5xehxIx` is the dev pool; staging/prod are separate future DBCPs |

### 3.2 Target runtime principal

The IAM policy attaches to the **bc-core deployed task/service runtime role**. The exact infra identifier (role name, ARN, attachment mechanism) is **TO BE CONFIRMED IN THE BC-INFRA IMPLEMENTATION PR** and verified against the answer to OQ-R12-1 (see §9).

Candidate identifiers (operator confirms which applies):

- ECS task role: `arn:aws:iam::546549546538:role/bc-core-dev-task` (if bc-core dev runs on ECS Fargate / EC2)
- EC2 instance profile: `arn:aws:iam::546549546538:instance-profile/bc-core-dev-ec2` (if bc-core dev runs on EC2 with instance metadata-based IAM)
- Lambda execution role: `arn:aws:iam::546549546538:role/bc-core-dev-lambda-exec` (if bc-core dev is serverless)
- ECS task execution role (separate from task role): NOT the right principal for application-level IAM; the *task* role is correct for the runtime API call

The bc-infra implementation PR MUST cite the exact ARN it attaches the policy to and MUST verify (via `aws iam get-role` or equivalent) that the runtime container/process actually assumes that role at execution time. A mis-attached policy is risk R-R12-1.

## 4. IAM actions (locked)

### 4.1 Allowed actions

```
cognito-idp:AdminGetUser
cognito-idp:AdminUpdateUserAttributes
```

These two actions are necessary and sufficient for the PR-G1.1 `CognitoAdminService` flow:

- `AdminGetUser` — pre-read of `custom:roles` (D-4 preservation formula: `final = (current ∖ MCF_ALLOWLIST) ∪ (desired ∩ MCF_ALLOWLIST)` requires reading current before computing final)
- `AdminUpdateUserAttributes` — write of the computed `custom:roles` value to Cognito

The post-read (verify-after-write) is a second `AdminGetUser` call in the same transaction; the action permission covers both invocations.

### 4.2 Explicitly forbidden actions

The policy MUST NOT include ANY of the following, regardless of phrasing:

- `cognito-idp:*` (wildcard — never)
- `AdminCreateUser` / `AdminDeleteUser` (identity creation/destruction — out of scope)
- `AdminAddUserToGroup` / `AdminRemoveUserFromGroup` (Cognito Groups are orthogonal per PR-BS-1 §12 OQ-BS-1)
- `AdminConfirmSignUp` (account confirmation flow)
- `AdminInitiateAuth` / `AdminRespondToAuthChallenge` / `AdminUserGlobalSignOut` (auth/session control)
- `AdminResetUserPassword` / `AdminSetUserPassword` (credential mutation)
- `AdminListUserAuthEvents` (auth event read — privacy-sensitive)
- `AdminLinkProviderForUser` (federation linkage)
- `AdminDisableUser` / `AdminEnableUser` (lifecycle control)
- `AdminListGroupsForUser` (Cognito Groups read — orthogonal)
- Any `cognito-identity:*` action (different service — Cognito Identity Pools, not User Pools)
- Any `sso:*` / `iam:*` / `sts:*` action

### 4.3 Reference policy template

This template is **REFERENCE ONLY**. The actual policy lands in the bc-infra implementation PR and MUST be reviewed against §4.1, §4.2, and §3 verbatim.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BcCoreMcfRoleGrantCognitoAdmin",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:AdminGetUser",
        "cognito-idp:AdminUpdateUserAttributes"
      ],
      "Resource": "arn:aws:cognito-idp:ap-south-1:546549546538:userpool/ap-south-1_bM5xehxIx"
    }
  ]
}
```

The `Sid` value `BcCoreMcfRoleGrantCognitoAdmin` is a recommended convention for cross-correlation with this DBCP UID; the bc-infra PR MAY choose a different Sid for IaC tool reasons but SHOULD document the mapping.

### 4.4 What this policy does NOT grant

Even with this policy attached, the bc-core runtime role CANNOT:

- Read or modify any Cognito user attribute on any pool other than `ap-south-1_bM5xehxIx`
- Create, delete, or disable any Cognito identity
- Modify any user's password, MFA configuration, or session state
- Add or remove users from Cognito Groups
- Federate identities or alter SSO configuration
- Read CloudTrail or any other AWS service

If the bc-core service code attempts any of those, the AWS SDK call returns `AccessDeniedException` with a populated `$metadata.requestId`. The `mapAwsError` handler at `cognito-admin.service.ts:148-151` maps this to `CognitoAccessDeniedError` (NOT `CognitoServiceFailureError` — the F-D guard is for a different failure mode; see §2 #2). The controller at `mcf-role-grant.controller.ts:91-97` maps `CognitoAccessDeniedError` to HTTP 500 with `code: cognito_access_denied`. This is the same fail-closed path as if the policy were absent.

## 5. Implementation expectations (for the bc-infra PR)

The bc-infra repo PR that implements this DBCP MUST include the following sections. The bc-infra PR description SHOULD reference this DBCP's merge SHA (set after this PR merges).

### 5.1 Required content of the bc-infra PR

1. **Policy form**: actual policy JSON inline OR as a tracked file, matching §4.3 byte-for-byte (modulo Sid convention noted in §4.3)
2. **Attachment mechanism**: explicit declaration of the IaC tool (Terraform / CloudFormation / CDK / Pulumi) and the resource block that attaches the policy
3. **Target role identifier**: the exact ARN of the runtime role being modified, validated against the OQ-R12-1 answer
4. **Plan / diff evidence**: `terraform plan` output OR `cloudformation describe-change-set` OR equivalent — committed as an evidence artifact in the PR (NOT as a separate apply)
5. **Apply-side evidence**: separate evidence PR or commit after the apply, showing:
   - The CloudTrail event ID for the `AttachRolePolicy` (or equivalent) action
   - `aws iam list-attached-role-policies --role-name <role>` output showing the policy attached
   - `aws iam simulate-principal-policy` output confirming the role CAN call the two allowed actions (`cognito-idp:AdminGetUser` + `cognito-idp:AdminUpdateUserAttributes` against the dev pool ARN, both `Decision: allowed`) AND CANNOT call at least one representative forbidden action (e.g., `cognito-idp:AdminCreateUser` against the same ARN, `Decision: implicitDeny` — confirming no wildcard or accidental broadening leaked into the policy). The bc-infra PR MUST cite the simulated action names verbatim in the evidence so a reviewer can audit which forbidden action(s) were checked.
6. **Rollback procedure**: explicit steps to detach the policy + verify the runtime role no longer has Cognito permissions; reference §7 rollback below

### 5.2 Smoke verification (operator runs after apply)

After the bc-infra PR merges + applies + IAM propagates (~30-60s for IAM propagation per AWS), operator runs the following smoke check from a bc-core dev environment with super_admin role in JWT:

```
$ curl -X POST https://<bc-core-dev-host>/api/admin/mcf/role-grants \
    -H "Authorization: Bearer <fresh-jwt-with-super_admin>" \
    -H "Content-Type: application/json" \
    -d '{
      "target_user_uid": "<operator-self-or-dedicated-test-target>",
      "desired_mcf_roles": [],
      "reason_text": "IAM smoke verification per bc-infra R12 IAM DBCP §5.2 — no-op grant to confirm SDK boundary returns 2xx not 500",
      "source_pr_or_dbcp_text": "bc-infra-r12-cognito-iam-dbcp.md merge SHA <set after merge>"
    }'
```

**Target constraint**: `target_user_uid` MUST be a Cognito user carrying ZERO MCF roles (no `mcf_author`, no `mcf_publisher`) at smoke time. If the target already carries any MCF role, `desired_mcf_roles: []` would trigger a removal, not a no-op, and would exercise the write path with mutation — turning the smoke into a real grant + revert sequence rather than a non-mutating probe. The operator's own sub `8bdb9bd0-8827-4cc8-b640-2087658f1eb6` satisfies the zero-MCF-roles constraint per Catalog DBCP §2.3 (anant's current roles are `["platform_admin","schema_author","operator","analyst"]`).

Expected response: HTTP 409 with `code: "no_op_grant"`.

**What the 409 proves and what it does NOT prove**:

- ✓ Proves `AdminGetUser` permission is correctly attached. The no-op path at `mcf-role-grant.service.ts:76-83` reaches Step 2 (pre-read via `getUserAttributes` → `AdminGetUserCommand`) successfully and then short-circuits at Step 4 with `NoOpGrantError`.
- ✗ Does NOT prove `AdminUpdateUserAttributes` permission is correctly attached. The no-op path EXITS BEFORE Step 5 (the AWS write via `updateCustomRoles` → `AdminUpdateUserAttributesCommand`). A runtime role with `AdminGetUser` but missing `AdminUpdateUserAttributes` would STILL return 409 on this smoke.
- ✗ Does NOT write an audit row. The throw at Step 4 aborts the transaction before Step 8's audit INSERT at line 98. The 409 response carries the `current_state` payload from `NoOpGrantError`, NOT a `role_grant_uid` referencing an audit row. By design.

**`AdminUpdateUserAttributes` permission coverage** comes from two other sources:

1. §5.1 #5 apply-side `aws iam simulate-principal-policy` evidence — a static check that the role's effective policy authorizes `cognito-idp:AdminUpdateUserAttributes` on the dev pool ARN AND denies a representative forbidden action.
2. The first real PR-G1.5 invocation — a runtime check that actually exercises the write. PR-G1.5 should be invoked with full evidence capture (per PR-G1.0 §I-7 audit row format) so a failure surfaces as `cognito_access_denied` in the response code with the operator inspecting the audit row's absence (no audit row written on AWS-denied path either, per F-D).

**Failure-mode diagnosis** if smoke returns non-409:

| HTTP status + code | Likely cause | Operator action |
|---|---|---|
| HTTP 500 `code: cognito_access_denied` | IAM policy is not attached, not propagated yet, or attached to wrong role | Wait 60s and retry; if persists, check §5.1 apply evidence + verify role identifier per OQ-R12-1 |
| HTTP 500 `code: cognito_service_failure` | F-D missing-requestId path; rare network/SDK edge case; NOT an IAM issue | Investigate AWS SDK config + CloudTrail; not the typical IAM-missing symptom |
| HTTP 404 `code: target_user_not_found` | `target_user_uid` does not exist in the dev pool | Confirm the sub UUID is correct; check pool ID |
| HTTP 403 (Bearer rejected) | JWT is missing super_admin OR token expired OR audience mismatch | Re-fetch JWT post-bootstrap; verify catalog filter pass-through |
| HTTP 500 with no specific `code` | Unknown error reached ProblemDetailFilter | Inspect bc-core logs |

### 5.3 Hard non-execution constraints for the bc-infra PR

The bc-infra PR itself MUST NOT:

- Attach a wider policy than this DBCP authorizes (any wildcard is a violation of §4.2)
- Apply to staging or prod pool ARNs (this DBCP locks dev only)
- Modify the trust policy of the runtime role (separate concern)
- Add or remove any other IAM principal
- Touch Cognito directly (no Console click, no `aws cognito-idp *` call from the bc-infra PR; the IAM apply is via IaC only)
- Modify any bc-core code, schema, or DDL
- Modify any bc-docs-v3 doc (the bc-infra PR may *reference* this DBCP; it does not amend it)

## 6. Sequencing

```
PR-R12-1    bc-docs-v3    THIS DBCP                — proposed → review → merge
  ↓
bc-infra    impl PR       IAM policy attach via    — proposed → review → merge + APPLY + propagation wait
            (separate     IaC; plan + apply
             repo)        evidence committed
  ↓
[smoke verification per §5.2 — operator runs no-op grant; expects 409 no_op_grant, NOT 500 cognito_service_failure]
  ↓
(parallel) PR-BS-1 §5 bootstrap execution → PR-BS-X evidence merge
  ↓
[gate: BOTH bc-infra R12 IAM applied + smoke-passed AND PR-BS-X merged]
  ↓
PR-G1.5     bc-core       first service-driven      — operator invokes
            (runtime)     mcf_author grant for      POST /api/admin/mcf/role-grants
                          self
```

### 6.1 PR-R12-1 (this DBCP)

- Status: proposed
- Predecessor gate: NONE (this DBCP is parallel-capable with PR-BS-X execution; it does not depend on the operator-side bootstrap)
- Authority: PR-G1.0 R12 + Catalog DBCP §11 R12 + PR-BS-1 §9
- Deliverable: this single docs file
- Merge gate: 3-agent strict review (same pattern as PR #34 / #35 / #36 / #37 / #38)
- Phase0Impact: none

### 6.2 bc-infra implementation PR (separate repo)

- Status: NOT YET STARTED; opens in bc-infra repo after this DBCP merges
- Authority: this DBCP (PR-R12-1)
- Deliverable: IAM policy attachment via IaC + plan/diff evidence + apply evidence + rollback procedure (per §5.1)
- Merge gate: bc-infra repo's own review discipline (separate from bc-docs-v3 / bc-core)
- Phase0Impact: none (IAM-only; no Phase 0 substrate impact)

### 6.3 PR-BS-X (operator-side bootstrap evidence)

Parallel-capable with the bc-infra PR. Per PR-BS-1 §9: operator bootstrap uses operator's own AWS credentials; the bc-infra R12 IAM policy is for the service role at runtime, a distinct concern. PR-BS-X scaffold is already opened as DRAFT at bc-docs-v3 PR #39 (head `e17f971`).

### 6.4 PR-G1.5

Status: gated on §6.2 (bc-infra R12 IAM applied + smoke-passed) AND §6.3 (PR-BS-X merged). PR-G1.5 fires when both gates clear, NOT before. The two gates are parallel; the order in which they land does not change PR-G1.5's readiness.

## 7. Hard rules (HR-R12-1 through HR-R12-8)

### HR-R12-1 — Two actions only

The IAM policy authorizes EXACTLY `cognito-idp:AdminGetUser` and `cognito-idp:AdminUpdateUserAttributes`. Any third action in the same policy statement OR in a sibling statement attached to the same role is a violation. The bc-infra PR reviewer MUST `grep -i "cognito-idp:" <policy-file>` and confirm only the two actions appear.

### HR-R12-2 — One specific pool ARN

The IAM Resource is the exact ARN `arn:aws:cognito-idp:ap-south-1:546549546538:userpool/ap-south-1_bM5xehxIx`. Any wildcard form (`*`, `arn:aws:cognito-idp:*:*:userpool/*`, etc.) is a violation. A second Resource (even a sibling pool ARN) is also a violation — this DBCP authorizes the dev pool only.

### HR-R12-3 — Dev pool only

Staging and prod pools, when provisioned, require SEPARATE per-environment R12 DBCPs (PR-R12-2, PR-R12-3 — naming convention TBD). This DBCP authorizes nothing about non-dev pools.

### HR-R12-4 — bc-core runtime role only

The policy attaches to the bc-core runtime role (per §3.2). It MUST NOT attach to:

- The operator's IAM user
- Any bc-admin or bc-portal role
- Any service-user role (e.g., CI/CD deployer)
- **The ECS task EXECUTION role** (used by the ECS agent for ECR image pulls + CloudWatch Logs delivery — NOT for application-level AWS API calls; §3.2 distinguishes this from the bc-core task role)
- The Cognito service-linked role (which Cognito manages internally)
- A shared cross-service role (each service gets its own least-privilege role)

### HR-R12-5 — No password / session / federation APIs

The forbidden-actions list in §4.2 is exhaustive at the time of authoring. Future Cognito Admin APIs that touch credentials, sessions, or federation are implicitly forbidden until a new DBCP authorizes them.

### HR-R12-6 — No CloudTrail tampering

The bc-infra PR MUST NOT modify CloudTrail configuration, event selectors, log retention, or trail status. CloudTrail is the cross-correlation backbone for PR-G1.5 audit chain (per PR-BS-1 §6.1 `cloudtrail_event_id`); compromising it would weaken the entire audit story.

### HR-R12-7 — No bypass-by-AI

Claude (this assistant) MUST NOT:

- Run any `aws iam *` command against the dev or any other account
- Open the AWS IAM Console
- Modify the bc-core service code to call IAM APIs at startup (e.g., self-attach the policy)
- Apply the IaC change from a Claude-driven session

Claude MAY:

- Author this DBCP (the present action)
- Help draft the bc-infra PR description and the policy JSON template
- Help draft the smoke-verification curl command and expected-response documentation
- Review the bc-infra PR diff for structural compliance against §4 + §5

### HR-R12-8 — One-shot scope

This DBCP authorizes ONE policy attachment to ONE role on ONE pool in ONE environment. Subsequent changes (add a third action, expand to a second pool, attach to a second role) require a SEPARATE DBCP authoring + merge cycle. There is no "amendment" path that quietly broadens scope.

## 8. Risk register (R-R12-1 through R-R12-13)

| ID | Risk | Likelihood | Severity | Mitigation |
|---|---|---|---|---|
| R-R12-1 | Wrong role attached (e.g., attached to ECS task execution role instead of task role, or to a wrong-environment role) | Medium | High | §3.2 mandates the bc-infra PR cites exact ARN + validates via `aws iam get-role`; §5.2 smoke verification would surface the mis-attachment as a 500 response from PR-G1.5 attempt |
| R-R12-2 | Wildcard Resource creep (`*` instead of specific pool ARN) | Medium | Very High | HR-R12-2 + §4.3 reference template + bc-infra PR reviewer grep for `"Resource":` substring |
| R-R12-3 | Wildcard Action creep (`cognito-idp:*` instead of the 2 allowlisted) | Medium | Very High | HR-R12-1 + §4.2 explicit forbidden list + bc-infra PR reviewer grep |
| R-R12-4 | Applied to prod pool instead of dev pool | Low | Catastrophic | HR-R12-3 + §3.1 locks the dev pool ARN + bc-infra PR reviewer cross-checks the ARN |
| R-R12-5 | Policy merged in bc-infra repo but NOT applied to AWS (IaC merge ≠ apply for some workflows) | Medium | High | §5.1 mandates apply-side evidence as separate commit; §5.2 smoke verification fails if apply hasn't happened |
| R-R12-6 | PR-G1.5 attempted before IAM has propagated (AWS IAM eventual consistency, typically 30-60s after apply but can be longer) | Medium | Low (recoverable) | §5.2 smoke verification includes retry guidance; operator waits and retries |
| R-R12-7 | CloudTrail correlation missing (event not visible within expected window) | Low | Low | §5.1 mandates CloudTrail event ID capture in apply evidence; same `"not_found_within_5_min"` fallback pattern as PR-BS-1 §6.1 |
| R-R12-8 | Trust policy on the runtime role does not allow the deployed task/service to assume it | Low | High | §1.3 declares trust policy out of scope; if the runtime cannot assume the role, the policy attachment is moot; bc-infra PR SHOULD verify trust policy independently |
| R-R12-9 | Permission boundary on the runtime role restricts `cognito-idp:*` even though the policy is attached | Low | High | bc-infra PR MUST check for a permissions boundary on the role: run `aws iam get-role --role-name <runtime-role>` and inspect `Role.PermissionsBoundary.PermissionsBoundaryArn` (NULL = no boundary attached, no further action; non-NULL = boundary exists). If a boundary ARN is present, then `aws iam get-policy --policy-arn <boundary-arn>` (to find DefaultVersionId) followed by `aws iam get-policy-version --policy-arn <boundary-arn> --version-id <DefaultVersionId>` reveals the boundary's effective document. If the boundary blocks `cognito-idp:AdminGetUser` or `cognito-idp:AdminUpdateUserAttributes`, it must be widened OR a different role chosen. Note: `aws iam get-role-policy --policy-name` is for INLINE policies, NOT permissions boundaries — using it for boundary inspection would return `NoSuchEntity` and mislead the operator. |
| R-R12-10 | Multi-environment policy collision (e.g., same role used in dev + staging + prod with environment-conditional policies) | Low | Medium | HR-R12-3 + HR-R12-4 mandate per-environment per-role isolation; bc-infra PR SHOULD confirm one role per environment |
| R-R12-11 | Policy applied but bc-core service deployment cached old config and doesn't pick up new IAM (e.g., ECS task using cached temporary credentials) | Low | Medium | §5.2 smoke verification at the actual deployed endpoint surfaces this; remediation is a service restart or wait-for-credential-refresh |
| R-R12-12 | Concurrent PR-G1.5 attempts during IAM propagation cause inconsistent outcomes | Very low | Low | Single operator; PR-G1.5 is a single-shot first-grant; not a sustained workload |
| R-R12-13 | AWS Organizations Service Control Policy (SCP) at the account or OU level denies `cognito-idp:*` despite the identity-based policy this DBCP authorizes being correctly attached | Low | High | `aws iam simulate-principal-policy` does NOT evaluate SCPs (per AWS docs) — the §5.1 #5 evidence is a false positive if a denying SCP exists. The bc-infra PR MUST verify SCP state: if the barecount account `546549546538` is in an AWS Organization, run `aws organizations list-policies-for-target --target-id <account-id> --filter SERVICE_CONTROL_POLICY` (and same for each parent OU up to the root) to enumerate applicable SCPs, then read each policy via `aws organizations describe-policy --policy-id <scp-id>` and confirm none denies `cognito-idp:AdminGetUser` or `cognito-idp:AdminUpdateUserAttributes` on the dev pool ARN. If the account is NOT in an Organization (standalone account), the bc-infra PR MUST record that fact explicitly (`aws organizations describe-organization` returns AWSOrganizationsNotInUseException). Without this check, the §5.1 #5 simulate evidence is structurally incomplete. |

## 9. Open questions (deferred)

### OQ-R12-1 — Exact bc-core runtime role identifier

The bc-infra PR MUST cite the exact role name and ARN. This DBCP cannot pre-commit the identifier without inspecting the bc-infra repo and the deployed infrastructure. Candidate forms listed in §3.2. The bc-infra PR's reviewer MUST verify the runtime-time IAM identity (e.g., `aws sts get-caller-identity` from within a bc-core dev container) matches the cited role.

### OQ-R12-2 — Should `AdminGetUser` be split to a separate read-only policy statement?

Argument for: separation of concerns; future-proofing for read-only-but-cannot-write scenarios.

Argument against: simpler operationally; both calls are part of the same transactional flow in `grantMcfRoles`; splitting adds IaC complexity without operational benefit.

**Current stance**: keep both actions in a single statement (per §4.3 template). Revisit when a future R12 DBCP authorizes a read-only auditor role.

### OQ-R12-3 — CloudTrail event selectors for cross-correlation

Should the bc-infra PR include CloudTrail event selector configuration to ensure `cognito-idp:AdminUpdateUserAttributes` calls are captured as data events?

**Current stance**: out of scope here. CloudTrail event selector is part of HR-R12-6 (no CloudTrail tampering); the assumption is that the existing CloudTrail trail captures management events including `AdminUpdateUserAttributes` by default. If subsequent investigation shows AUE is not captured, a separate CloudTrail DBCP is needed.

### OQ-R12-4 — Whether the staging / prod pool R12 should be batched

When staging/prod pools are provisioned, should each get a separate per-environment DBCP (PR-R12-2, PR-R12-3) OR should one DBCP authorize all three environments?

**Current stance**: separate per environment (HR-R12-3). Different environments have different blast radius, different propagation windows, and different change-window discipline; batching them in one DBCP would weaken the per-environment governance.

## 10. Hard boundaries (non-execution of this PR)

This PR (PR-R12-1) is **docs-only**.

- ✓ No AWS calls
- ✓ No IAM apply (no `aws iam *` invocation; no IaC `apply`; no CloudFormation `update-stack`; no Terraform `apply`)
- ✓ No Cognito modification
- ✓ No role grants
- ✓ No PR-G1.5 invocation
- ✓ No M11 / M12 / M12.5 / M13 / M14 invocation
- ✓ No metric-contract creation, modification, or evaluation
- ✓ No DDL applied
- ✓ No substrate mutation (`bc_platform_dev` untouched)
- ✓ No tenant DB touch (`tbc_apex_dev` and any other tenant DB untouched)
- ✓ No bc-core / bc-admin / bc-portal code change
- ✓ No bc-infra change (the bc-infra implementation PR is SEPARATE and lands in the bc-infra repo, NOT in bc-docs-v3)
- ✓ No new npm or pip dependency
- ✓ No supersession of any prior DBCP, ADR, or governance artifact

This DBCP introduces procedural authority for a future bc-infra change. The actual change happens in a separate repo, in a separate PR, in a separate session, under operator-attested apply discipline.

## 11. References

- PR-G1.0 implementation DBCP: `docs/implementation/mcf-role-grant-service-implementation-dbcp.md` (merged `ec7053d`, PR #35). R12 (bc-infra IAM dependency) surfaced.
- Platform Role Catalog DBCP: `docs/implementation/platform-role-catalog-dbcp.md` (merged `b2d693d`, PR #36; §5.1 amended `b359d11`, PR #37). §11 R12 carries the dependency.
- Super-Admin Bootstrap DBCP (PR-BS-1): `docs/implementation/super-admin-bootstrap-dbcp.md` (merged `656ac77`, PR #38). §9 clarifies operator vs service identity boundary; §11 R-BS-8 names R12 IAM as PR-G1.5 gate.
- PR-G1.1 (bc-core MCF role-grant service): bc-core merge `f8e8042` (PR #174). `CognitoAdminService` at `src/auth/cognito-admin/cognito-admin.service.ts`; F-D fail-closed via `CognitoServiceFailureError` at SDK boundary.
- PR-CAT-1 (bc-core catalog enforcement): bc-core merge `20a4269` (PR #175). Post-bootstrap JWT carrying `super_admin` passes catalog filter cleanly.
- PR-E1 readiness pack: bc-core merge `3adacbd` (PR #173). JWT decode evidence.
- AWS account / region / profile policy: CLAUDE.md §AWS.
- Cognito user pool ID source: bc-core `src/auth/cognito-admin/cognito-admin.service.spec.ts`.
- M12 three-vendor transcript evidence (referenced cautiously, not relied upon): bc-core `scripts/audit-output/mcf-m12-first-real-run-2026-05-30T08-3*-*Z.evidence.jsonl`.

BuildPlan: docs-only § bc-infra R12 Cognito IAM DBCP authorizing least-privilege policy attach (2 actions, 1 pool ARN, dev environment) to bc-core runtime role; closes R12 governance layer; bc-infra implementation PR ships separately
Finding: PR-G1.0 R12 + Catalog DBCP §11 R12 + PR-BS-1 §9 + §11 R-BS-8 all name bc-infra IAM as a PR-G1.5 gate; live PR-G1.1 CognitoAdminService fails closed without this IAM; this DBCP closes the governance side and unblocks the bc-infra repo PR
Rollback: revert this PR; bc-infra implementation PR has no authority chain to cite; PR-G1.5 remains blocked on the catalog-named gap (no behavioral regression on main; pure procedural removal)
Phase0Impact: none

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
