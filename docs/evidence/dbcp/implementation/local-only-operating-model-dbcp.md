---
uid: local-only-operating-model-dbcp
title: Local-Only Operating Model DBCP (PR-LO-1) — lock the current local-machine deployment topology; supersede the bc-infra R12 IAM gate on PR-G1.5 for local-dev mode only; preserve PR-R12-1 as dormant forward-looking governance; specify local PR-G1.5 prerequisites + evidence schema; name the future trigger that re-activates R12 IAM
description: Closes the architectural misframing discovered while attempting the bc-infra implementation PR for R12 IAM. bc-core, bc-portal, bc-admin, and bc-ai run LOCALLY on the developer machine today; the only AWS surface is the Cognito user pool `ap-south-1_bM5xehxIx`. There is no bc-core deployed runtime role for the R12 IAM policy to attach to. The R12 gate on PR-G1.5 (named in Catalog DBCP §10 + §11 R12, PR-BS-1 §8 + §11 R-BS-8, PR-R12-1 §6.4) is unsatisfiable in the current operating model and is hereby superseded FOR LOCAL-DEV MODE ONLY. PR-R12-1 stands intact as dormant governance that re-activates the moment a bc-core deployment to AWS lands. This DBCP also locks the local PR-G1.5 evidence schema, the operator-credential boundary, and the trigger condition for re-activating R12. Discovered via TSK-509ef0.
status: proposed
date: 2026-05-31
project: bc-docs
domain: operating-model
subdomain: deployment-topology
focus: local-dev-pr-g1-5
supersedes:
superseded_by:
---

## 1. Authority + scope

### 1.1 Authority chain

| Authority | Where | What it locks today (and what this DBCP changes for local-dev) |
|---|---|---|
| Platform Role Catalog DBCP | `docs/implementation/platform-role-catalog-dbcp.md` (merged `b2d693d`, PR #36; §5.1 amended `b359d11`, PR #37) | §10 sequencing names "bc-core PR-CAT-1 merged" + "bc-infra R12 IAM merged + applied" as PR-G1.5 prerequisites; §11 R12 carries the bc-infra dependency. **This DBCP supersedes the R12 IAM prerequisite for local-dev mode only**; PR-CAT-1 remains a prerequisite (already satisfied). |
| Super-Admin Bootstrap DBCP (PR-BS-1) | `docs/implementation/super-admin-bootstrap-dbcp.md` (merged `656ac77`, PR #38) | §9 distinguishes operator identity vs service identity; §8 sequencing names R12 IAM as a parallel gate; §11 R-BS-8 names R12 IAM as a high-severity risk. **In local-dev mode the two identities are the same (operator IAM = bc-core's runtime AWS identity)**, so §9's distinction has no current load-bearing function and §8's R12 gate is unsatisfiable. PR-BS-1 §5 bootstrap MECHANISM remains fully valid in local-dev mode. |
| bc-infra R12 Cognito IAM DBCP (PR-R12-1) | `docs/implementation/bc-infra-r12-cognito-iam-dbcp.md` (merged `03fa679`, PR #40) | Entire DBCP assumes a deployed bc-core runtime role exists. **PR-R12-1 is preserved INTACT as dormant forward-looking governance.** It is NOT superseded or invalidated; it is marked future-triggered per §6 of this DBCP. The moment a bc-core deployment to AWS lands, PR-R12-1 re-activates as the standing IAM scope lock. |
| PR-G1.1 `CognitoAdminService` | bc-core merge `f8e8042` (PR #174) | The live SDK wrapper. **Works identically in local-dev mode** — calls Cognito via AWS SDK using whatever credentials the process happens to have, which in local-dev is the operator's `barecount` profile. |
| TSK-509ef0 | DevHub task (this session, 2026-05-31) | Captured the misframing during the failed bc-infra implementation PR attempt; this DBCP is the resolution path A from that task's acceptance criteria. |

### 1.2 In scope

- Lock the **current** local-machine deployment topology (operator-side fact, not aspirational)
- Supersede the R12 IAM prerequisite on PR-G1.5 **for local-dev mode only**, leaving PR-R12-1 standing as dormant
- Specify local PR-G1.5 prerequisites (5 items) and evidence schema (7 fields + attestation)
- Lock the operator-credential boundary (operator's AWS profile is the only authorized identity for bc-core → Cognito calls in local-dev mode)
- Name the future trigger condition (bc-core deployment to AWS) that re-activates PR-R12-1 + requires a deployment-topology DBCP

### 1.3 Explicitly out of scope

- **Authorizing AWS deployment of bc-core** — this DBCP says "we are not deployed today and PR-G1.5 works without deployment"; it does NOT authorize a deployment. Deployment requires a separate **bc-core deployment topology DBCP** (not yet authored).
- **Modifying PR-R12-1 content** — PR-R12-1 stands intact; this DBCP supersedes its prerequisite-claim-on-PR-G1.5 for local-dev mode but does not edit a single word of PR-R12-1.
- **Modifying PR-BS-1, Catalog DBCP, or any other merged DBCP** — local-dev mode supersedes specific prerequisite/gate clauses by REFERENCE in this DBCP; no in-place amendments of merged docs.
- **Tenant DB topology** — `tbc_*_dev` schema discussions are out of scope; this DBCP addresses identity/IAM only.
- **bc-portal, bc-admin, bc-ai deployment models** — only mentioned as factual baseline (they also run locally); their individual deployment evolution is out of scope.
- **M11 / M12 / M12.5 / M13 / M14 invocation** — PR-G1.5 unblocks but does not itself authorize metric runtime work.
- **Substrate mutation** — no DDL, no `bc_platform_dev` writes.

## 2. Current operating model (locked)

### 2.1 Local processes

| Component | Runtime | Storage |
|---|---|---|
| bc-core | Node.js (NestJS) on operator machine via `npm run start:dev` | Local Postgres in Docker — `bc_platform_dev` (platform schema; location of `mcf.role_grant_audit`) + per-tenant schemas `tbc_*_dev` (specific tenant schema names + active-tenant configuration are out of scope here; see CLAUDE.md §Database Rules + bc-core `.env`'s `TENANT_DATABASE_URL` for the live value) |
| bc-portal | Vite dev server on operator machine | n/a (calls bc-core) |
| bc-admin | Vite dev server on operator machine | n/a (calls bc-core) |
| bc-ai | Python/FastAPI (uvicorn) on operator machine | n/a |
| Postgres | Local Docker container (`docker compose up -d` in bc-core) | Disk volume on operator machine |
| Redis | Local Docker container (port 6379) | Memory + disk on operator machine |

Per CLAUDE.md §"Dev Service Management" + Port Reservation (D046): bc-core on 3100, bc-portal on 3000, bc-admin on 3010, bc-ai on 4300, DevHub on 4000, Postgres on 5435, Redis on 6379. All localhost.

### 2.2 AWS surface

The **only** BareCount-owned resource in AWS at the time this DBCP is authored:

- **Cognito User Pool**: `ap-south-1_bM5xehxIx`
  - Account: `546549546538` (per CLAUDE.md §AWS — barecount account)
  - Region: `ap-south-1`
  - Stack: bc-infra `AuthStack` (deployed via `platform-infra-stack` CDK, last commit `6b01fab`)

No ECS cluster, no Lambda function, no EC2 instance, no Fargate task, no API Gateway carrying bc-core traffic, no RDS instance hosting bc-core's data. The bc-infra CDK app at `cdk/bin/platform-infra.ts` instantiates exactly one stack: `AuthStack`. Verified via `grep -rln "bc-core|bc_core|BcCore" platform-infra-stack/` → zero matches.

### 2.3 bc-core's runtime AWS identity in local-dev mode

When the local bc-core Node process calls Cognito Admin APIs via `CognitoAdminService` (`bc-core/src/auth/cognito-admin/cognito-admin.service.ts`):

1. The AWS SDK v3 `CognitoIdentityProviderClient` is instantiated with `{ region }` only (no explicit credentials)
2. The SDK resolves credentials via the AWS SDK v3 default provider chain. The canonical order is: (a) environment variables (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN`), then (b) SSO via `~/.aws/sso/cache`, then (c) shared credentials file `~/.aws/credentials` selected by `AWS_PROFILE` / `AWS_DEFAULT_PROFILE`, then (d) ECS task role via container metadata, then (e) EC2 instance metadata service. Steps (d) and (e) are **not applicable to the local operating mode** (no container runtime, no instance metadata). The functional resolution on a standard operator machine reaches step (c) and selects the `barecount` profile.
3. In standard bc-core local setup, the resolved profile is **`barecount`** (per CLAUDE.md §AWS) which corresponds to the **operator's IAM identity**
4. The operator's IAM identity already carries Cognito Admin permissions because the operator administers the AWS account

**Consequence**: bc-core's runtime AWS identity in local-dev mode IS the operator's IAM identity. There is no separate "service IAM" to distinguish from. PR-BS-1 §9's "operator identity vs service identity" distinction has no load-bearing function today — both labels refer to the same IAM principal.

### 2.4 No bc-core deployed runtime role exists

Confirmed by inspection of `C:\MyProjects\platform-infra-stack` at commit `6b01fab` during this session:

- No `aws_iam_role` resource named bc-core, bc-core-runtime, bc-core-task, etc.
- No ECS task definition referencing bc-core
- No Lambda function referencing bc-core
- No EC2 instance profile referencing bc-core
- The legacy `cdk/lib/platform-infra-stack.ts` (with Network + Aurora + DemoLambda + IAM constructs) is **not instantiated by the current CDK entrypoint** (`cdk/bin/platform-infra.ts` instantiates only `AuthStack`). The file exists in the repo but is unreferenced by the active app. If the entrypoint were ever changed to instantiate `PlatformInfraStack`, it would create Lambda + IAM resources that fall under PR-R12-1's scope — i.e., the §6 future trigger would fire.

PR-R12-1 §3.2 listed four candidate role identifiers (ECS task role / EC2 instance profile / Lambda execution role / ECS task execution role marked NOT correct). Zero of the three valid candidates exist today.

## 3. Correction to prior governance (supersession by reference, NOT in-place amendment)

### 3.1 PR-R12-1 — preserved as dormant forward-looking governance

PR-R12-1 (`docs/implementation/bc-infra-r12-cognito-iam-dbcp.md`, merged `03fa679`, PR #40) remains in force as the standing rule for **when bc-core IS deployed to AWS**. Specifically:

- Its IAM action allowlist (`cognito-idp:AdminGetUser` + `cognito-idp:AdminUpdateUserAttributes` only) remains the canonical least-privilege scope for a future deployed runtime role
- Its forbidden-actions list (§4.2) remains the canonical exclusion set
- Its dev pool ARN lock (§3.1) remains correct
- Its hard rules HR-R12-1 through HR-R12-8 remain canonical
- Its risk register R-R12-1 through R-R12-13 remains canonical
- The error-class wiring corrected in amendment v2 (`CognitoAccessDeniedError` vs `CognitoServiceFailureError`) remains factually accurate

**What changes**: PR-R12-1's §6 sequencing claim that PR-G1.5 is gated on "bc-infra R12 IAM applied + smoke-passed" is **superseded for local-dev mode only**. In local-dev mode, bc-core uses operator IAM directly; there is no service role to attach the policy to; the smoke verification has no AWS endpoint to fire against.

**No edit to PR-R12-1.** This DBCP supersedes the prerequisite-claim by reference. PR-R12-1's text is unchanged.

### 3.2 PR-BS-1 §9 — clarified for local-dev mode

PR-BS-1 (`docs/implementation/super-admin-bootstrap-dbcp.md`, merged `656ac77`, PR #38) §9 reads "Operator's own AWS credentials drive this bootstrap (operator identity); bc-core service role is a different IAM principal that requires its own cognito-idp:Admin* permissions for PR-G1.5."

**In local-dev mode** this distinction is meaningless because the two identities are the same. The operator-side bootstrap procedure (§5 Console / CLI under `barecount` profile) remains fully valid and is the only path to grant the first `super_admin`. PR-BS-1 §5 + §6 + §7 + §10 HR-BS-1 through HR-BS-7 are unchanged in interpretation.

**What changes**: PR-BS-1 §8 sequencing diagram's "bc-infra R12 IAM PR" parallel gate is **superseded for local-dev mode** — local PR-G1.5 fires when PR-BS-X is merged; no bc-infra IAM dependency. PR-BS-1 §11 R-BS-8 (bc-infra R12 IAM not landed) becomes inapplicable in local-dev mode.

**No edit to PR-BS-1.** Supersession by reference.

### 3.3 Catalog DBCP §10 item 9 + §11 R12 — clarification (item 9 already carves out local-dev)

Catalog DBCP (`docs/implementation/platform-role-catalog-dbcp.md`, merged `b2d693d` + `b359d11`, PR #36 + #37) §10 line 397 enumerates **nine** PR-G1.5 prerequisites (PR-G1.0 originally named six; PR-G1.0 §R12 added bc-infra IAM as a 7th; this DBCP's parent Catalog DBCP added two more for a total of 9 — Catalog DBCP itself + PR-CAT-1). bc-infra IAM appears as **item 9** in the current text, NOT as a 7th.

**Important**: Catalog DBCP §10 item 9 (line 407) **already contains a local-dev carve-out** in its own text: "Required for AWS-dev PR-G1.5 invocation; local-dev unblocked via developer credentials per CLAUDE.md `barecount` AWS profile." The parent Catalog DBCP author already anticipated the local-dev mode and qualified the prerequisite accordingly.

**What this DBCP changes**:
- §10 item 9 — **not superseded; reinforced and made authoritative**. PR-LO-1 §4 locks the local-dev prerequisite list referenced by §10 item 9's carve-out clause. This DBCP is the authoritative reference the §10 item 9 wording points to.
- §11 R12 risk register row — historically framed as a generic "bc-infra dependency for PR-G1.5"; in local-dev mode that dependency does not apply. PR-LO-1 §4 supersedes the local-dev interpretation of §11 R12 (R12 remains correct for AWS-deployed mode per PR-R12-1 dormancy).

**Net result**: Catalog DBCP §10 + §11 R12 require no in-place amendment. The local-dev carve-out in §10 item 9 is now backed by PR-LO-1 as the authoritative DBCP for the local-dev interpretation. PR-BS-1 §8 + §11 R-BS-8 + PR-R12-1 §6.4 supersessions (§3.1 + §3.2 above) remain valid as written — those documents lack a local-dev carve-out and need the §3 supersession-by-reference treatment.

### 3.4 Why supersession-by-reference and not in-place amendment

In-place amendment of three merged DBCPs would require three separate amendment PRs, each with 3-agent strict review, each editing canonical governance text that's correct for the FUTURE-deployed mode. The misframing isn't that PR-R12-1 / PR-BS-1 §9 / Catalog DBCP §11 R12 are wrong — they're correct for the AWS-deployed scenario. They were premature. This DBCP locks the current scenario without invalidating the standing rule for the future.

When bc-core IS deployed to AWS (per §6 trigger), this DBCP either gets superseded by a "Hybrid mode" DBCP, or PR-R12-1 / PR-BS-1 §9 / Catalog DBCP §11 R12 silently re-activate as written.

## 4. Local PR-G1.5 prerequisites (lock)

In local-dev mode, PR-G1.5 (first service-driven `mcf_author` grant via `POST /api/admin/mcf/role-grants`) requires:

| # | Prerequisite | Status today |
|---|---|---|
| 1 | PR-CAT-1 merged (bc-core `KNOWN_PLATFORM_ROLES` + JWT filter live on bc-core main) | ✓ Merged at bc-core `20a4269` (PR #175) |
| 2 | PR-BS-1 merged (super_admin bootstrap DBCP governance lock) | ✓ Merged at bc-docs-v3 `656ac77` (PR #38) |
| 3 | PR-BS-X evidence merged (operator-executed bootstrap with attested evidence) | ☐ In flight at bc-docs-v3 PR #39 DRAFT — awaits operator execution |
| 4 | Local bc-core running with `barecount` AWS profile credentials available to the process | Operator-side check at PR-G1.5 invocation time |
| 5 | Operator IAM caller identity captured in PR-G1.5 evidence (`aws sts get-caller-identity` from the bc-core process environment) | Operator-side capture at PR-G1.5 invocation time |

**Explicitly NOT a prerequisite in local-dev mode**: bc-infra R12 IAM PR / bc-infra implementation PR / any AWS-deployed bc-core runtime role.

When prerequisites #1-#3 are merged AND #4-#5 are satisfied at invocation time, PR-G1.5 fires.

## 5. PR-G1.5 evidence requirements (local-dev mode)

The PR-G1.5 evidence file MUST be committed to `bc-docs-v3/docs/operations/role-grant-evidence/<YYYY-MM-DD>-pr-g1-5-first-mcf-author-grant.md` (NEW directory — separate from `role-bootstrap-evidence/`).

### 5.1 Required fields

| Field | Format | Source |
|---|---|---|
| `invocation_started_at` | ISO 8601 UTC | operator clock |
| `invocation_completed_at` | ISO 8601 UTC | operator clock |
| `local_bc_core_base_url` | `http://localhost:3100` (or whatever port if overridden) | operator's local config |
| `aws_profile_used` | `barecount` | operator's bc-core `.env` |
| `aws_caller_identity_json` | output of `aws sts get-caller-identity --profile barecount` with `Account` (acceptable to commit; already documented in CLAUDE.md), `UserId`, `Arn` — sensitive segments may be redacted only if they carry session tokens; standard IAM ARN is acceptable | `aws sts get-caller-identity` |
| `target_user_uid` | Cognito sub (UUID) | operator-supplied |
| `target_user_email_snapshot` | email at invocation time | from service response |
| `roles_before_observed` | JSON array — `custom:roles` of target BEFORE the grant | captured via `aws cognito-idp admin-get-user` OR from service `roles_before` response field |
| `desired_mcf_roles` | JSON array — what operator requested | request payload echo |
| `service_response_status` | HTTP 201 (success) or 409 `no_op_grant` or 4xx/5xx | bc-core HTTP response |
| `service_response_body_json` | full `GrantResultDto` shape per PR-G1.0 §I-7 (`role_grant_uid`, `target_*`, `roles_before`, `roles_after`, `mcf_roles_added`, `mcf_roles_removed`, `granted_at`, `granted_by_email_snapshot`, `note`) | bc-core HTTP response |
| `mcf_role_grant_audit_row_uid` | `role_grant_uid` from response | service response field |
| `mcf_role_grant_audit_row_query_output` | row as `SELECT * FROM mcf.role_grant_audit WHERE role_grant_uid = '<uid>'` captured from local Postgres (no sensitive data; the audit row is non-secret) | local Postgres query |
| `cognito_request_id` | from response OR from audit row's `cognito_request_id` column | service / DB |
| `cloudtrail_event_id` | best-effort within ~5-15 min; if not found record `"not_found_within_5_min"` | operator runs CloudTrail query |
| `roles_after_observed` | JSON array — `custom:roles` AFTER grant | from service `roles_after` response OR re-read via `aws cognito-idp admin-get-user` |
| `jwt_refresh_at` | ISO 8601 UTC of operator's sign-out + sign-in | operator clock |
| `refreshed_jwt_decoded_payload_json` | base64-decoded JWT payload segment; **signature redacted to literal `"<redacted>"`** | operator decodes; standard discipline per PR-BS-1 §6.3 |
| `mcf_author_in_refreshed_token` | `true` if `custom:roles` array in decoded payload contains `"mcf_author"`, else `false` | operator verifies |

### 5.2 Operator attestation

Free-text attestation block ≥ 100 chars confirming:

1. "I am `anant@selenite.co`, the invoking operator"
2. "I executed this PR-G1.5 invocation under my own AWS credentials linked to AWS profile `barecount`"
3. "I confirm the local bc-core process at `<local_bc_core_base_url>` used those credentials to call Cognito Admin APIs"
4. "I verified the before-roles and after-roles empirically"
5. "I confirm `mcf_author` was added to the target's `custom:roles`; no other MCF role was added; no non-MCF role was modified"
6. "I understand that any subsequent role grant — including future grants of `mcf_author` or `mcf_publisher` to any identity — MUST go through the same `POST /api/admin/mcf/role-grants` service; no direct AWS-side mutation"

Signature line: `Signed: <operator-email> at <ISO 8601 UTC>`

### 5.3 Redaction discipline

The evidence file MUST NOT contain:

- Raw JWT signature segment (replaced with literal `"<redacted>"`)
- AWS access key / secret key / session token (from environment OR `.aws/credentials`)
- Cognito Console URLs in any capture form (per PR-BS-1 §6.4 broadened wording)
- Local file paths that reveal operator's machine identity beyond what's already public
- **bc-core local DEBUG / verbose log output** — NestJS `start:dev` emits per-request log lines that can include Authorization headers (Bearer tokens), full request bodies (with `desired_mcf_roles` + `reason_text` payload OK, but Authorization header MUST be redacted), or Cognito response bodies (with raw token segments). If captured for evidence, the operator MUST grep and redact `Authorization: Bearer ...` substrings and any `eyJ`-prefixed JWT fragments before commit.
- **bc-core `.env` file contents in any form** — the `.env` carries `DATABASE_URL` + `TENANT_DATABASE_URL` (each with Postgres passwords), `COGNITO_CLIENT_ID` + `COGNITO_ADMIN_CLIENT_ID`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `TEST_PASSWORD`, and may carry SSO session material. None of these belong in evidence. If the operator needs to attest WHICH `.env` values were active at invocation time, the attestation §5.2 carries the operator's word; the file contents do NOT get committed.

The evidence file MAY contain:

- `aws_caller_identity_json` (Account/UserId/Arn — Arn includes the IAM user/role name; this is acceptable for a documented operator)
- Service response body verbatim (no secrets)
- Audit row verbatim (no secrets; all fields are governance metadata)

## 6. Future trigger condition for PR-R12-1 re-activation

PR-R12-1 dormancy ENDS — and PR-R12-1 becomes load-bearing again — when bc-core moves from local-machine execution to AWS-deployed execution.

### 6.1 Trigger events (any one suffices)

- A bc-core deployment artifact lands in any repo: ECS task definition, Lambda function with bc-core code, EC2 instance profile carrying bc-core service, Kubernetes pod with IAM identity, Fargate service definition
- A CI/CD pipeline commits bc-core deployment manifests (Terraform / CloudFormation / CDK / Pulumi resources for bc-core runtime)
- An AWS resource is provisioned that runs bc-core code under any IAM identity OTHER than the operator's local AWS profile

### 6.2 Required precondition before that deployment runs

Before the deployed bc-core runtime invokes any Cognito Admin API in any environment:

1. **bc-core deployment-topology DBCP** authored (separate from this DBCP and from PR-R12-1; locks the deployment shape — ECS Fargate? Lambda? — and the runtime role ARN)
2. **PR-R12-1 implementation PR** opened against bc-infra with the actual runtime role ARN from #1
3. **PR-R12-1 §5.1 apply-side evidence** captured (plan/diff, CloudTrail event ID, `list-attached-role-policies`, `simulate-principal-policy` for the 2 allowed actions + at least one forbidden, SCP verification per R-R12-13)
4. **PR-R12-1 §5.2 smoke verification** executed against the deployed endpoint
5. A **deactivation-of-this-DBCP** action: either supersede this DBCP, or amend its §6 to mark the trigger as satisfied + the deployed environment as the new operating mode

Skipping the precondition list means a deployed bc-core runtime calls Cognito Admin APIs without least-privilege IAM scope — a regression that PR-R12-1 was authored to prevent.

### 6.3 Trigger watcher (operational)

The operator (or a future Claude session) SHOULD set up a low-cost watcher for the trigger condition:

- DevHub task TSK-509ef0 carries the activation trigger description; SHOULD be promoted to `wip` when a bc-core deployment PR lands
- Or: any new DBCP authoring session that adds a bc-core deployment topology MUST cite this DBCP and confirm the §6.2 precondition list before approving the deployment

## 7. Hard rules (HR-LO-1 through HR-LO-5)

### HR-LO-1 — Local-only is the current operating mode; AWS deployment requires explicit re-authorization

bc-core, bc-portal, bc-admin, bc-ai run locally as a matter of explicit policy until a bc-core deployment-topology DBCP is authored and merged. Deploying bc-core to AWS without that DBCP — even temporarily, even in dev — is a violation of this rule.

### HR-LO-2 — Operator AWS credentials are the only authorized identity for bc-core → Cognito calls in local-dev mode

The local bc-core process MUST use the operator's `barecount` AWS profile (or an equivalent profile under the operator's own IAM identity). It MUST NOT use:

- A shared service account
- Hardcoded AWS access keys in `.env` (operator's local credentials live in `~/.aws/credentials`, not in repo)
- A different IAM user that hasn't been assigned Cognito Admin permissions
- Federated credentials assumed via SSO without the operator's explicit configuration

### HR-LO-3 — Evidence MUST redact credentials, tokens, and secrets

Per §5.3 redaction discipline. PR-G1.5 evidence is a public-facing governance artifact; any leak of credentials, raw JWT, session tokens, or AWS access keys is a HR-LO-3 violation.

### HR-LO-4 — This DBCP does NOT authorize AWS deployment of bc-core

A future session that uses this DBCP as authority to deploy bc-core would be misreading it. This DBCP locks the *current* state; it does not authorize any state change. Deployment requires a separate DBCP per §6.2.

### HR-LO-5 — No bypass-by-AI

Claude (this assistant) MUST NOT:

- Invoke `POST /api/admin/mcf/role-grants` (PR-G1.5)
- Run any `aws cognito-idp admin-update-user-attributes` outside the PR-BS-1-authorized bootstrap path
- Modify the operator's `.aws/credentials` or `~/.aws/config`
- Capture or commit operator credentials in any form

Claude MAY:

- Author this DBCP and the §5 PR-G1.5 evidence scaffold
- Help draft the curl invocation pattern for the operator
- Review post-execution evidence for structural completeness against §5

## 8. Risk register (R-LO-1 through R-LO-6)

| ID | Risk | Likelihood | Severity | Mitigation |
|---|---|---|---|---|
| R-LO-1 | Operator credentials leak in PR-G1.5 evidence file | Medium | High | §5.3 explicit redaction discipline + HR-LO-3 + reviewer grep before commit (`Bearer`, `eyJ`, `AKIA`, `aws_session_token`) |
| R-LO-2 | Future Claude session re-reads PR-BS-1 §8 + R12 gate and re-flags R12 IAM as blocking PR-G1.5 (false positive) | Medium | Low (recoverable) | This DBCP's existence is the resolution; future session reads §3 supersession-by-reference table and moves on. TSK-509ef0 also captures the gap. |
| R-LO-3 | Operator forgets to deactivate local-only mode when bc-core deployment to AWS lands; deployed runtime calls Cognito Admin APIs without least-privilege IAM | Medium | High | §6.2 mandates the precondition list; HR-LO-4 explicit no-authorization-for-deployment; TSK-509ef0 carries the trigger description |
| R-LO-4 | Wrong AWS profile resolved at bc-core process start (e.g., default profile instead of `barecount`) → call against wrong account | Low | High | §5.1 requires `aws_caller_identity_json` capture confirming Account `546549546538` before claiming success; bc-core `.env` standard sets `AWS_PROFILE=barecount` per CLAUDE.md §AWS |
| R-LO-5 | Operator runs PR-G1.5 against wrong target user UID | Low | Medium | PR-G1.5 service performs pre-read via `AdminGetUser`; operator captures `target_user_email_snapshot` in evidence and re-reads JWT after grant; mistakes surface in §5.2 attestation reconciliation step |
| R-LO-6 | CloudTrail event delivery lag exceeds 5 min; operator records `"not_found_within_5_min"` and proceeds without correlation | Low | Low | Documented fallback per §5.1; AWS RequestId remains as primary forensic key; CloudTrail event can be back-filled in a follow-up evidence amendment |

## 9. Open questions (deferred)

### OQ-LO-1 — Should staging or prod ever run bc-core locally?

No. Local-dev mode is dev-environment-only. Staging and prod, when provisioned, MUST run deployed bc-core with their own R12 IAM PR (one per environment per HR-R12-3). Recording this here so a future session doesn't ambiguously extend local-dev mode beyond dev.

### OQ-LO-2 — What's the operator's procedure to deactivate local-dev mode when AWS deployment lands?

Not yet specified. Likely shape: a separate "Local-dev mode deactivation DBCP" OR an amendment to this DBCP's §6 noting the trigger has fired + the activation date + the bc-core deployment-topology DBCP UID. Defer until the trigger is closer.

### OQ-LO-3 — Should this DBCP supersede TSK-509ef0?

When this DBCP merges, TSK-509ef0's acceptance criterion "Cleanup DBCP authored + merged + linked from R12 IAM + PR-BS-1 + Catalog DBCP" is partially satisfied. TSK-509ef0 should be updated to reference this DBCP's merge SHA + marked `completed` UNLESS the operator wants TSK-509ef0 to remain `planned` as a watcher for the §6 future trigger. Recommend marking `completed` at this DBCP's merge; create a NEW task for the §6 trigger watcher if desired.

## 10. Hard boundaries (non-execution of this PR)

This PR is **docs-only**.

- ✓ No AWS calls
- ✓ No IAM apply / Cognito modification
- ✓ No role grants (including no PR-G1.5 invocation)
- ✓ No M11 / M12 / M12.5 / M13 / M14 invocation
- ✓ No metric-contract action
- ✓ No DDL applied / no substrate mutation / no tenant DB touch
- ✓ No bc-core / bc-admin / bc-portal / bc-infra / bc-ai code change
- ✓ No in-place amendment of PR-R12-1, PR-BS-1, or Catalog DBCP (supersession is by REFERENCE — this DBCP's §3 stands on its own as the authoritative pointer for local-dev mode)
- ✓ No new npm or pip dependency
- ✓ This DBCP does NOT supersede any prior DBCP whole; it supersedes specific prerequisite-claim clauses for local-dev mode only, by reference

## 11. References

- Platform Role Catalog DBCP: `docs/implementation/platform-role-catalog-dbcp.md` (merged `b2d693d`, PR #36; §5.1 amended `b359d11`, PR #37). §10 sequencing + §11 R12 superseded for local-dev mode per §3.3 above.
- Super-Admin Bootstrap DBCP / PR-BS-1: `docs/implementation/super-admin-bootstrap-dbcp.md` (merged `656ac77`, PR #38). §5 mechanism + §6 evidence schema remain valid in local-dev mode; §9 service-identity distinction + §11 R-BS-8 superseded for local-dev mode per §3.2 above.
- bc-infra R12 Cognito IAM DBCP / PR-R12-1: `docs/implementation/bc-infra-r12-cognito-iam-dbcp.md` (merged `03fa679`, PR #40). PRESERVED INTACT as dormant forward-looking governance per §3.1 above.
- PR-G1.0 implementation DBCP: `docs/implementation/mcf-role-grant-service-implementation-dbcp.md` (merged `ec7053d`, PR #35). §I-7 evidence schema referenced in §5.1 above.
- PR-G1.1 (bc-core MCF role-grant service): bc-core merge `f8e8042` (PR #174). `CognitoAdminService` works the same in local-dev as in deployed mode.
- PR-CAT-1 (bc-core catalog enforcement): bc-core merge `20a4269` (PR #175). Runtime-agnostic.
- PR-BS-X evidence scaffold: bc-docs-v3 PR #39 (DRAFT). Awaiting operator bootstrap execution.
- DevHub task TSK-509ef0: discovery + resolution-path source for this DBCP.
- AWS account / region / profile policy: CLAUDE.md §AWS.
- Port reservations + local-dev service management: CLAUDE.md §"Dev Service Management" + §"Port Reservation (DEC-e50b83 / D046)".
- bc-infra repo state at session time: `C:\MyProjects\platform-infra-stack` HEAD `6b01fab` — confirmed no bc-core runtime role exists.

BuildPlan: docs-only § PR-LO-1 local-only operating model DBCP — lock current local-machine topology; supersede R12 IAM gate on PR-G1.5 for local-dev mode only; preserve PR-R12-1 as dormant; specify local PR-G1.5 prereqs + evidence; name future trigger
Finding: R12 IAM gate on PR-G1.5 (named in Catalog DBCP §10 + §11 R12, PR-BS-1 §8 + §11 R-BS-8, PR-R12-1 §6.4) is unsatisfiable in current operating model — bc-infra has no bc-core runtime role to attach policy to because bc-core runs locally; only Cognito is in AWS; bc-core uses operator IAM at runtime
Rollback: revert this PR; R12 IAM gate re-asserts on PR-G1.5 as written in the three merged DBCPs; future Claude session re-discovers the unsatisfiable gate; PR-G1.5 blocks unnecessarily for local-dev mode (no behavioral regression on main; pure procedural removal of the supersession)
Phase0Impact: none

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
