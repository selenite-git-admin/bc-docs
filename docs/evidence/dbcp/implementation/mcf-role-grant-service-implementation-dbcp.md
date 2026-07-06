---
uid: mcf-role-grant-service-implementation-dbcp
title: MCF — Role-Grant Service Implementation DBCP (PR-G1.0; resolve 7 OPEN-Q + R11 + IAM + DB-change protocol shape; lock implementation details before PR-G1.1 code)
description: Implementation-detail DBCP authored after PR-G1 design DBCP (bc-docs-v3 main `d60a742`, PR #34) locked 6 architectural decisions D-1..D-6 and named 7 OPEN-Q items + R11 (concurrent-grant race) deferred to "PR-G1 implementation DBCP" — this document. PR-E1 readiness evidence (bc-core main `3adacbd`, PR #173) confirmed the substrate and service-side readiness ahead of PR-G2 and named the auth gap whose resolution path now flows through this DBCP. Operator selected all 7 implementation picks via pre-DBCP option matrix; operator explicitly upgraded concurrency mitigation from R11's v2-deferred default (operator-side discipline) to v1 advisory lock (`pg_advisory_xact_lock(hashtext(target_user_uid))`) per the direction "avoid designing a role-grant service with a known race on day one." Locks the audit-table placement (`mcf.role_grant_audit`), the audit-table DDL shape (13 columns, 3 indexes, no FKs, no soft-delete, immutable), the database-change protocol shape (additive Drizzle schema + minimal migration DBCP; DDL marked PENDING explicit operator approval before PR-G1.1 ships), the layered `SuperAdminGuard` + `@RequireSuperAdmin()` decorator pattern (no global RolesGuard modification; admin-bypass explicitly rejected for this endpoint only), the IAM policy snippet (pool-resource-scoped to `arn:aws:cognito-idp:ap-south-1:546549546538:userpool/ap-south-1_bM5xehxIx` + `cognito-idp:AdminUpdateUserAttributes` + `cognito-idp:AdminGetUser` actions; bc-infra cross-repo dependency named as new R12), the advisory-lock concurrency mechanism with its interaction with the no-op-check race window, the 409 `no_op_grant` semantics confirmation (no AWS call, no audit row, current state in response body), and the response `note` field carrying token re-issuance guidance. Defines PR-G1.1's implementation scope, 2 new test obligations beyond design DBCP §7 (concurrency serialization + note-field assertion bringing total to 17), and the sequencing within PR-G1.1 (Drizzle schema first → migration approval gate → DDL apply → service+guard+controller code → tests). Subordinate to PR-G1 design DBCP; does NOT supersede it. Marks audit-table DDL as PENDING explicit operator approval per CLAUDE.md Database Change Protocol — PR-G1.1 cannot MERGE (squash to bc-core main) until that approval lands and commit (b) post-apply evidence is captured per §11.2 step 3 (PR-G1.1 may OPEN with commit (a) before the approval; the approval gate is mid-PR, not pre-PR). NOT EXECUTED — docs-only implementation lock. No bc-core code change. No AWS calls. No Cognito modification. No role grants. No M12 / M12.5 / M13 / M14 invocation. No provider calls. No substrate mutation. No DDL applied. No tenant DB touch. No metric contract authored. No supersession of PR-S1, PR-C4, PR-G1 design DBCP, MCF-ERR-001, DEC-7f9597/D423, or DEC-ebf0b4/D268.
status: proposed
date: 2026-05-31
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-role-grant-service
supersedes:
superseded_by:
---

# MCF — Role-Grant Service Implementation DBCP (PR-G1.0)

> Subordinate to **PR-G1 design DBCP** (`docs/implementation/mcf-role-grant-service-dbcp.md`, merged at bc-docs-v3 main `d60a742`, PR #34). Does NOT supersede it. PR-G1.0 resolves the 7 OPEN-Q items + R11 mitigation + IAM + DB-change protocol shape that the design DBCP §12 deferred to "PR-G1 implementation DBCP."
>
> Sibling of **PR-E1 readiness evidence** (`bc-core/scripts/audit-output/pr-e1-readiness-2026-05-31T02-11-30Z.summary.md`, merged at bc-core main `3adacbd`, PR #173).
>
> Authorizes the shape of **PR-G1.1** (next bc-core implementation PR) but does NOT authorize the audit-table DDL apply — that requires a separate explicit operator approval per CLAUDE.md Database Change Protocol.

## 1. Scope

### 1.1 Question this DBCP answers

> The PR-G1 design DBCP locked D-1..D-6 (build the endpoint, operate on custom:roles directly, allowlist `{mcf_author, mcf_publisher}`, preservation formula, audit row shape, bootstrap is separate). It also named 7 OPEN-Q items (audit table placement; `@RequireSuperAdmin()` mechanism; bootstrap DBCP; no-op semantics; `mcf_reader` deferred; integration tests; token re-issuance UX) and R11 (concurrent-grant race) explicitly deferred to "PR-G1 implementation DBCP." PR-E1 evidence confirmed substrate readiness. **What are the locked implementation details that close those OPEN-Q + R11 so PR-G1.1 can ship against a fully specified contract?**

### 1.2 In scope

- Mapping of the design DBCP's 7 OPEN-Q items + R11 to this DBCP's I-1..I-7 picks
- Audit table DDL proposal — table, columns, indexes, FK posture, soft-delete posture (PENDING DB-change approval per CLAUDE.md)
- Drizzle schema location + shape
- `SuperAdminGuard` + `@RequireSuperAdmin()` decorator architecture
- IAM policy snippet (pool-resource-scoped) + bc-infra cross-repo dependency
- Concurrency mechanism (`pg_advisory_xact_lock` + interaction with no-op check)
- Response shape update (`note` field for token re-issuance guidance)
- 3 additional vitest cases (advisory-lock serialization + note-field assertion on both 201/409 + SDK requestId null rejection); total = 18 (added case 18 in amendment v2 to tighten F-D enforcement)
- PR-G1.1 implementation scope + intra-PR sequencing (schema → migration approval gate → DDL apply → code → tests)
- R12 (bc-infra cross-repo timing) added to the risk register

### 1.3 Explicitly out of scope

- Any bc-core code change (docs only)
- Any DDL apply (PENDING explicit operator approval per CLAUDE.md)
- Any AWS call; any Cognito modification; any role grant
- Cognito Groups → MCF role projection (`mcf-auth.config.ts`) — separate follow-up
- bc-admin UI for role grants
- `mcf_reader` role
- First-`super_admin` bootstrap DBCP
- PR-G2 authorization DBCP
- M12 / M12.5 / M13 / M14 invocation
- Substrate mutation; tenant DB touch
- bc-infra IAM policy attachment PR (sibling repo; separate session)

## 2. Mapping — design DBCP OPEN-Q → PR-G1.0 picks

| Design DBCP item | PR-G1.0 pick | Disposition |
|---|---|---|
| OPEN-Q-1 — audit table placement | **I-1** | RESOLVED — `mcf.role_grant_audit` |
| (R11) — concurrent-grant race mitigation | **I-5** | RESOLVED — advisory lock at v1 |
| OPEN-Q-2 — `@RequireSuperAdmin()` design | **I-3** | RESOLVED — layered `SuperAdminGuard` + decorator bundle |
| OPEN-Q-3 — first-super_admin bootstrap DBCP | (n/a) | UNCHANGED — separate scope; not in PR-G1.0 |
| OPEN-Q-4 — no-op semantics | **I-6** | CONFIRMED — already locked in design DBCP D-5; PR-G1.0 reaffirms binding (advisory lock makes the check race-free) |
| OPEN-Q-5 — `mcf_reader` allowlist addition | (n/a) | UNCHANGED — out of scope; deferred until UserRole literal exists AND a new DBCP authorizes allowlist expansion (design DBCP D-3 names the DBCP gate explicitly) |
| OPEN-Q-6 — integration tests vs sandboxed Cognito | (n/a) | UNCHANGED — deferred follow-up; not in PR-G1.1 v1 |
| OPEN-Q-7 — token re-issuance UX | **I-7** | RESOLVED — response `note` field with guidance text |
| Design DBCP §6.1 step IAM | **I-4** | RESOLVED — pool-resource-scoped policy; bc-infra cross-repo dependency |
| Design DBCP §6.1 audit table DDL | **I-2** | RESOLVED — additive Drizzle schema; DDL PENDING explicit DB-change approval |

OPEN-Q-3, OPEN-Q-5, OPEN-Q-6 remain unresolved by design and are NOT in this DBCP's scope.

## 3. Locked picks (I-1 through I-7)

### I-1: Audit table at `mcf.role_grant_audit`

Colocated with the existing MCF substrate (`mcf.metric_authoring_intake_queue`, `mcf.metric_authoring_panel_run`, `mcf.metric_authoring_panel_transcript`, etc.). Matches the established "MCF is its own domain" pattern in `bc_platform_dev`. Lowest scope: no need to extend a platform-wide audit table that does not currently exist, and no need to fit the 13 audit fields into a generic append-only ledger schema.

If a unified platform audit emerges later, migration from `mcf.role_grant_audit` to a unified table is a follow-up DBCP, not a blocker on PR-G1.1.

### I-2: Additive Drizzle schema + minimal migration DBCP; DDL PENDING DB-change approval

The audit table is brand new with no existing data dependencies. The DDL is additive only. Rollback = `DROP TABLE` (idempotent). Drizzle schema lives at `bc-core/src/database/schema/mcf-role-grant-audit.ts` per bc-core's existing `src/database/schema/` convention.

**Migration DBCP shape (minimal):** PR-G1.1's commit message includes the DDL statements (or a pointer to `bc-core/docker/redesign/*.sql` if that pattern is preferred). Dry-run → operator approval → apply → evidence row in `scripts/audit-output/`. No staging migration needed because the table is empty at apply time.

**CLAUDE.md Database Change Protocol gate:** The audit-table DDL is a database change. Per CLAUDE.md, **no DDL may be applied without explicit operator approval**. PR-G1.1 includes the proposed DDL in the PR description (so the operator can review the exact shape), but the DDL execution is gated behind:

1. Operator's explicit "approve the audit-table DDL" message in the PR-G1.1 conversation, AND
2. An evidence-pack commit in `bc-core/scripts/audit-output/mcf-role-grant-audit-apply-<ts>.summary.md` proving the apply ran cleanly and the post-apply table shape matches the proposal byte-for-byte.

### I-3: Layered `SuperAdminGuard` + `@RequireSuperAdmin()` decorator bundle

A new standalone guard at `bc-core/src/auth/guards/super-admin.guard.ts`:

- Implements `CanActivate`
- Reads `request.user as AuthUser`
- Returns true iff `user.roles.includes('super_admin')` (literal match; NO `admin` bypass)
- Returns false otherwise; the upstream `RolesGuard` chain produces a 403

A new decorator at `bc-core/src/common/decorators/require-super-admin.decorator.ts`:

```ts
import { applyDecorators, UseGuards } from '@nestjs/common';
import { SuperAdminGuard } from '../../auth/guards/super-admin.guard';

export const RequireSuperAdmin = () => applyDecorators(UseGuards(SuperAdminGuard));
```

Endpoint usage in `McfRoleGrantController`:

```ts
@Post()
@RequireSuperAdmin()
async grantMcfRoles(@Body() dto: GrantMcfRolesDto, @CurrentUser() user: AuthUser) { ... }
```

**No modification to the global `RolesGuard`.** Blast radius confined to the new endpoint. The `admin` bypass continues to apply on every OTHER `@Roles()`-decorated endpoint exactly as today.

**Why a decorator bundle even though `@UseGuards(SuperAdminGuard)` would suffice:** clean endpoint reading + single concept to remember + grep-ability (a future audit can find `@RequireSuperAdmin()` everywhere it's used).

### I-4: IAM policy — pool-resource-scoped

Exact policy snippet (to be applied to bc-core's deployed task/Lambda role; **NOT** in PR-G1.1 because the role lives in bc-infra):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "McfRoleGrantServiceCognitoAdminAccess",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:AdminUpdateUserAttributes",
        "cognito-idp:AdminGetUser"
      ],
      "Resource": "arn:aws:cognito-idp:ap-south-1:546549546538:userpool/ap-south-1_bM5xehxIx"
    }
  ]
}
```

- `cognito-idp:AdminUpdateUserAttributes` — the actual write call from `CognitoAdminService.updateCustomRoles`
- `cognito-idp:AdminGetUser` — the pre-update read in `getUserAttributes` to populate `roles_before_json` and verify the target user exists in the configured pool
- Resource scoped to one specific user pool (the BareCount admin pool from PR-E1 §2.1 JWT decode: `ap-south-1_bM5xehxIx`)
- Account: `546549546538` (per CLAUDE.md AWS profile)
- Region: `ap-south-1`

**Cross-repo dependency (NEW R12):** The IAM policy attachment lives in **bc-infra** (`C:\MyProjects\platform-infra-stack`), not in bc-core. PR-G1.1 in bc-core CANNOT successfully call the endpoint against any deployed environment until a separate bc-infra PR attaches this policy to bc-core's task role. PR-G1.5 (operator-attested first invocation) is timing-coupled to the bc-infra PR landing.

**Local dev mitigation:** developer AWS credentials (the `barecount` profile) presumably carry `cognito-idp:AdminUpdateUserAttributes` already; PR-G1.1 testing in local dev is unblocked. The bc-infra PR is blocking for AWS dev and any higher environment.

### I-5: Concurrency — `pg_advisory_xact_lock(hashtext(target_user_uid))` at v1

The advisory lock is acquired at the very start of `McfRoleGrantService.grantMcfRoles`'s outer transaction, BEFORE the read-diff-write-audit sequence begins:

```ts
async grantMcfRoles(input: GrantInput): Promise<GrantResult> {
  return this.db.transaction(async (tx) => {
    // I-5: serialize concurrent grants against the same target user
    await tx.execute(sql`SELECT pg_advisory_xact_lock(hashtext(${input.target_user_uid}))`);

    // I-6: no-op check happens AFTER the lock acquires, so the read is race-free
    const current = await this.cognitoAdmin.getUserAttributes(input.target_user_uid);
    const desiredFinal = computeDesiredFinal(current.customRoles, input.desired_mcf_roles);
    if (arraysEqualAsSet(current.customRoles, desiredFinal)) {
      throw new NoOpGrantError(current);  // controller → 409 with current state
    }

    // ... AWS call → audit INSERT → return GrantResult
  });
}
```

**Why `pg_advisory_xact_lock` and not `pg_advisory_lock`:** the `_xact_` variant is auto-released at transaction commit/rollback. No explicit `pg_advisory_unlock` call needed. Cleaner contract; impossible to leak the lock if the service throws between acquire and commit.

**Why `hashtext` of the UUID string and not the raw UUID:** `pg_advisory_xact_lock` takes one `bigint`. `hashtext` produces a 32-bit signed int from a text input; PostgreSQL widens it to int8. Hash collisions across different target_user_uid values are possible in theory but harmless — they would only cause two unrelated grants to serialize unnecessarily, never produce incorrect behavior.

**Concurrency interaction with no-op (I-6):** before I-5, the no-op check at PR-G1's controller layer could race against a concurrent grant: two operators read identical `custom:roles`, both compute the same diff, both decide it's NOT a no-op, both call AdminUpdateUserAttributes. With I-5, the second operator's transaction blocks at `pg_advisory_xact_lock` until the first commits; when the second proceeds it re-reads `custom:roles` and now sees the post-grant state — which may have become a no-op, correctly producing a 409.

**Concurrency interaction with audit row (HR3 from design DBCP):** the audit INSERT is the LAST DML in the transaction, before commit. The advisory lock guarantees no other transaction has overlapping read-write semantics on the same target. Two audits for the same target with overlapping `granted_at` cannot both reflect the SAME `roles_before_json` — by construction.

### I-6: No-op semantics confirmation

Already locked in design DBCP D-5 / §4.3 / §7 case 8. PR-G1.0 reaffirms binding:

- **HTTP 409** `no_op_grant`
- **NO AWS call** (`CognitoAdminService.updateCustomRoles` not invoked)
- **NO audit row** (insert skipped)
- **Response body includes current state** so client can confirm no diff exists

The advisory lock from I-5 closes the race window the design DBCP amendment v2 noted: the no-op check now happens AFTER the lock acquires, so concurrent grants serialize cleanly. Within the lock, the read-diff-decision sequence is consistent with what the eventual write (or no-op) reflects.

### I-7: Token re-issuance UX — response `note` field

Add a `note` field (string, REQUIRED) to BOTH the 201 success response AND the 409 `no_op_grant` response. Operator/UI clients can surface it verbatim regardless of HTTP status. Locked here, not deferred to PR-G1.1.

**201 response shape:**

```ts
{
  role_grant_uid: string;
  target_user_uid: string;
  target_email_snapshot: string;
  roles_before: string[];
  roles_after: string[];
  mcf_roles_added: string[];
  mcf_roles_removed: string[];
  granted_at: string;   // ISO timestamp
  granted_by_email_snapshot: string;
  note: string;         // I-7: token re-issuance guidance
}
```

**Verbatim `note` text on the 201 success path (locked):**

> "Re-fetch your Cognito ID token (via `devhub_get_cognito_token` or by signing out and back in) to obtain a new token carrying the granted role. Cached tokens issued before this grant will continue to lack the role until they expire (Cognito default: 1 hour). The grant has been applied to Cognito and recorded in the audit row above; the only remaining client-side action is the token refresh."

**409 `no_op_grant` response shape:**

```ts
{
  code: 'no_op_grant';
  message: string;                  // e.g., 'Desired MCF roles already match current state; no change applied.'
  current_state: {
    target_user_uid: string;
    target_email_snapshot: string;
    custom_roles: string[];         // current Cognito custom:roles for target
    current_mcf_roles: string[];    // MCF-allowlist intersection
  };
  note: string;                     // I-7: locked verbatim text below
}
```

**Verbatim `note` text on the 409 no-op path (locked):**

> "No changes applied — the desired MCF role set already matches the current Cognito state. No token refresh is required for the target user. If you reached this response unexpectedly, verify the `desired_mcf_roles` payload reflects the change you intended."

OpenAPI description for `note` (same on both paths):

> "Human-readable guidance to be displayed verbatim to the operator. On 201 it carries the token re-issuance instruction; on 409 it confirms no client-side action is needed. Always present; never null."

## 4. Audit table DDL proposal — `mcf.role_grant_audit`

> ⚠ **PENDING explicit operator approval per CLAUDE.md Database Change Protocol.** This DDL is **NOT** applied by merging this DBCP. PR-G1.1 includes the DDL in its PR description for review; operator must explicitly approve before the DDL runs.

### 4.1 Table shape (13 columns)

```sql
-- ============================================================================
-- mcf.role_grant_audit — immutable audit ledger for MCF role grants
-- Authority: PR-G1 design DBCP D-5 + PR-G1.0 implementation DBCP I-1
-- Cardinality: one row per successful POST /api/admin/mcf/role-grants invocation
-- Mutation: INSERT only (audit is immutable; no UPDATE, no DELETE, no soft-delete)
-- ============================================================================
CREATE TABLE mcf.role_grant_audit (
  role_grant_uid             uuid           PRIMARY KEY,
  granted_at                 timestamptz    NOT NULL DEFAULT now(),
  granted_by_user_uid        uuid           NOT NULL,
  granted_by_email_snapshot  text           NOT NULL,
  target_user_uid            uuid           NOT NULL,
  target_email_snapshot      text           NOT NULL,
  roles_before_json          jsonb          NOT NULL,
  roles_after_json           jsonb          NOT NULL,
  mcf_roles_added_json       jsonb          NOT NULL DEFAULT '[]'::jsonb,
  mcf_roles_removed_json     jsonb          NOT NULL DEFAULT '[]'::jsonb,
  reason_text                text           NOT NULL,
  source_pr_or_dbcp_text     text           NOT NULL,
  cognito_request_id         text           NOT NULL,
  CONSTRAINT chk_role_grant_audit_reason_min_length
    CHECK (char_length(reason_text) >= 20),
  CONSTRAINT chk_role_grant_audit_source_min_length
    CHECK (char_length(source_pr_or_dbcp_text) >= 10),
  CONSTRAINT chk_role_grant_audit_diff_not_empty
    CHECK (jsonb_array_length(mcf_roles_added_json) + jsonb_array_length(mcf_roles_removed_json) >= 1)
);

CREATE INDEX idx_role_grant_audit_target_user_uid
  ON mcf.role_grant_audit (target_user_uid);

CREATE INDEX idx_role_grant_audit_granted_at
  ON mcf.role_grant_audit (granted_at DESC);

CREATE INDEX idx_role_grant_audit_target_recent
  ON mcf.role_grant_audit (target_user_uid, granted_at DESC);

COMMENT ON TABLE  mcf.role_grant_audit IS 'Immutable audit ledger for MCF role grants per PR-G1 design DBCP D-5 + PR-G1.0 I-1. INSERT only; no UPDATE; no DELETE.';
COMMENT ON COLUMN mcf.role_grant_audit.granted_by_email_snapshot IS 'Operator email at grant time; intentional snapshot (not denormalization) to preserve audit immutability if the Cognito user is later renamed/deleted.';
COMMENT ON COLUMN mcf.role_grant_audit.target_email_snapshot     IS 'Target email at grant time; same immutability rationale.';
COMMENT ON COLUMN mcf.role_grant_audit.roles_before_json         IS 'Full custom:roles array as observed before the grant (operator-side reasoning record).';
COMMENT ON COLUMN mcf.role_grant_audit.roles_after_json          IS 'Full custom:roles array as observed AFTER the grant via a subsequent getUserAttributes call (post-write reflection).';
COMMENT ON COLUMN mcf.role_grant_audit.mcf_roles_added_json      IS 'Derived diff: MCF-allowlist subset added (declarative summary of the change).';
COMMENT ON COLUMN mcf.role_grant_audit.mcf_roles_removed_json    IS 'Derived diff: MCF-allowlist subset removed.';
COMMENT ON COLUMN mcf.role_grant_audit.cognito_request_id        IS 'AWS RequestId from AdminUpdateUserAttributes response $metadata for CloudTrail cross-correlation. NOT NULL enforced at the SERVICE layer (not relied on at the DB layer): the @smithy/types ResponseMetadata interface declares requestId as string | undefined, so CognitoAdminService.updateCustomRoles MUST throw CognitoServiceFailureError(`AWS response missing requestId`) when result.$metadata.requestId is undefined or empty. The service-layer guard fires BEFORE the audit INSERT, so the DB CHECK never observes a NULL — HR3 returns 500 cleanly and no audit row is emitted. Defense-in-depth: the NOT NULL DB constraint would catch any future regression where the guard is removed.';
```

### 4.2 D162 compliance notes

| Rule | Status |
|---|---|
| 1. No JSONB for queryable data | ✓ All 4 JSONB columns are opaque snapshots / declarative diffs; not filtered/joined/sorted on |
| 2. No denormalized counters | ✓ None |
| 3. FK constraints mandatory | n/a — `granted_by_user_uid` and `target_user_uid` reference external Cognito user pool sub values; no bc-core users table exists to FK against. Documented as intentional external-reference. |
| 4. One source of truth per value | `*_email_snapshot` columns are explicitly snapshots, not denormalization; rationale documented in COMMENT |
| 5. Shared patterns use shared tables | n/a — first audit table of this shape; future unification with platform-wide audit is a separate DBCP |
| 6. Max 20 columns per table | ✓ 13 columns |
| 7. Indexes follow query patterns | ✓ 3 indexes named per expected query patterns (per-target, time-windowed, per-target-recent) |
| 8. Soft deletes: `archived_at` | n/a — audit is immutable; soft-delete inapplicable; documented in COMMENT |
| 9. Temporal: `effective_from / effective_to` | n/a — audit is point-in-time; temporal range inapplicable |
| 10. New table checklist | ✓ All applicable rules satisfied; checklist embedded in PR-G1.1 DDL apply DBCP |

### 4.3 Migration script shape (proposed for PR-G1.1)

PR-G1.1 includes:
- `bc-core/docker/redesign/<NN>-mcf-role-grant-audit.sql` (forward) — exact DDL above
- `bc-core/scripts/mcf-role-grant-audit-apply.mjs` — apply script with env-gate, dry-run, post-apply verification (table exists, indexes exist, constraints exist, row count = 0)
- `bc-core/scripts/mcf-role-grant-audit-rollback.mjs` — rollback (`DROP TABLE IF EXISTS mcf.role_grant_audit`); idempotent

Sequencing per PR-G1.1 §11.2 below.

## 5. Drizzle schema location + shape

File: `bc-core/src/database/schema/mcf-role-grant-audit.ts`

```ts
import { pgSchema, uuid, timestamp, text, jsonb, index, check } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';
import { mcfSchema } from './pg-schema';  // existing mcf schema definition (export of pgSchema('mcf'))

export const roleGrantAudit = mcfSchema.table('role_grant_audit', {
  roleGrantUid: uuid('role_grant_uid').primaryKey(),
  grantedAt: timestamp('granted_at', { withTimezone: true }).notNull().defaultNow(),
  grantedByUserUid: uuid('granted_by_user_uid').notNull(),
  grantedByEmailSnapshot: text('granted_by_email_snapshot').notNull(),
  targetUserUid: uuid('target_user_uid').notNull(),
  targetEmailSnapshot: text('target_email_snapshot').notNull(),
  rolesBeforeJson: jsonb('roles_before_json').notNull(),
  rolesAfterJson: jsonb('roles_after_json').notNull(),
  mcfRolesAddedJson: jsonb('mcf_roles_added_json').notNull().default(sql`'[]'::jsonb`),
  mcfRolesRemovedJson: jsonb('mcf_roles_removed_json').notNull().default(sql`'[]'::jsonb`),
  reasonText: text('reason_text').notNull(),
  sourcePrOrDbcpText: text('source_pr_or_dbcp_text').notNull(),
  cognitoRequestId: text('cognito_request_id').notNull(),
}, (t) => [
  // Array form per drizzle-orm 0.45.1 (the object form is @deprecated; every
  // existing MCF schema file under bc-core/src/database/schema/mcf/ uses array form).
  check('chk_role_grant_audit_reason_min_length',
    sql`char_length(${t.reasonText}) >= 20`),
  check('chk_role_grant_audit_source_min_length',
    sql`char_length(${t.sourcePrOrDbcpText}) >= 10`),
  check('chk_role_grant_audit_diff_not_empty',
    sql`jsonb_array_length(${t.mcfRolesAddedJson}) + jsonb_array_length(${t.mcfRolesRemovedJson}) >= 1`),
  index('idx_role_grant_audit_target_user_uid').on(t.targetUserUid),
  // `.desc()` on granted_at to match the DDL's `(granted_at DESC)` index spec.
  index('idx_role_grant_audit_granted_at').on(t.grantedAt.desc()),
  index('idx_role_grant_audit_target_recent').on(t.targetUserUid, t.grantedAt.desc()),
]);
```

Naming convention: `{noun}_uid` PK column → `role_grant_uid`. This refines design DBCP D-5's column name `grant_uid` for consistency with bc-core's `{noun}_uid` pattern (e.g., `intake_queue_uid`, `panel_run_uid`, `transcript_uid`). No semantic change; purely a naming refinement noted explicitly.

## 6. Service + guard architecture

```
McfRoleGrantController                                  bc-core/src/registry/mcf/
├── @PlatformOnly()
├── @RequireSuperAdmin()       (NEW — bundles @UseGuards(SuperAdminGuard))
└── @Post()
    grantMcfRoles(@Body() dto, @CurrentUser() user)
        ↓
McfRoleGrantService                                     bc-core/src/registry/mcf/
├── grantMcfRoles(input): Promise<GrantResult>
│   1. db.transaction
│   2. pg_advisory_xact_lock(hashtext(target_user_uid))   [I-5]
│   3. cognitoAdmin.getUserAttributes(target_user_uid)    [pre-update read]
│   4. compute final = (current ∖ MCF_ALLOWLIST) ∪ (desired ∩ MCF_ALLOWLIST)   [D-4]
│   5. if (final == current MCF subset) throw NoOpGrantError(current)          [I-6]
│   6. cognitoAdmin.updateCustomRoles(target_user_uid, final)
│       → returns { requestId }                                                [F2 amendment v2]
│   7. cognitoAdmin.getUserAttributes(target_user_uid)    [post-update reflection for roles_after_json]
│   8. INSERT INTO mcf.role_grant_audit (...)             [HR3 — before commit]
│   9. COMMIT → advisory lock auto-released               [I-5]
│  10. return GrantResult with note field                 [I-7]
        ↓
CognitoAdminService                                     bc-core/src/auth/cognito-admin/
├── constructor(@Inject(CONFIG) config)
│   → reads cognito.userPoolId and aws.region from ConfigService
├── getUserAttributes(targetUserUid): Promise<{ email, customRoles }>
├── updateCustomRoles(targetUserUid, newRoles): Promise<{ requestId }>
│   → returns result.$metadata.requestId                  [F2 amendment v2]
│   → throws CognitoServiceFailureError if result.$metadata.requestId is
│     undefined or empty (the SDK types it as `string | undefined`; we
│     enforce non-null at the service boundary, not at the DB)
│                                                          [F-D amendment v2]
└── Maps AWS exceptions:
    UserNotFoundException → TargetUserNotFoundError
    AccessDeniedException → CognitoAccessDeniedError
    others → CognitoServiceFailureError
```

Auth chain:

```
Request → CognitoJwtStrategy → ScopeGuard (PlatformOnly) → SuperAdminGuard → Controller method
                                  ↓ scope==platform           ↓ roles.includes('super_admin')
                                  403 if no                   403 if no (NO admin bypass)
```

SuperAdminGuard pseudocode:

```ts
@Injectable()
export class SuperAdminGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const user = request.user as AuthUser | undefined;
    if (!user) return false;
    return user.roles.includes('super_admin');   // NO admin bypass for this guard
  }
}
```

## 7. Concurrency mechanism — explicit interaction matrix

| Scenario | Behavior |
|---|---|
| Single operator, single user | Normal path; lock acquires instantly; grant + audit succeed |
| Two operators, same target user | Second operator's `pg_advisory_xact_lock` blocks until first commits; second then re-reads `custom:roles` (post-first-grant state); may turn into a no-op → 409, OR may apply a DIFFERENT grant (e.g., add `mcf_publisher` while first added `mcf_author`) |
| Two operators, different target users | No blocking; `hashtext` collision possible but harmless (just serializes unrelated grants briefly); independent transactions commit independently |
| Operator's transaction errors after lock acquire | Lock auto-released on ROLLBACK (the `_xact_` variant guarantees this); next operator unblocks |
| Operator's transaction errors mid-AWS-call | Lock still released on tx rollback; HOWEVER the AWS call may have succeeded — operator's idempotent retry path is the no-op 409 detection on the next attempt |
| AWS succeeded, audit INSERT failed | HR3 mandates 500 response; lock auto-released; operator retries — the next attempt detects the new state (Cognito reflects the change) and either no-ops (if the desired set already equals new state) or applies a different diff |
| AWS succeeded, audit INSERT succeeded, transaction ROLLBACK before COMMIT (subsequent statement or COMMIT itself fails) | Same observable consequence as the preceding row: the audit row never persists (rolled back), Cognito reflects the change. Mechanism differs (audit INSERT did complete before the rollback) but recovery path is identical: lock auto-released; operator retries; next attempt detects the new state and either no-ops or applies a different diff. The advisory lock + outer-tx pattern makes this scenario observationally equivalent to the audit-INSERT-failed case at the operator's interface. |

This is the same contract the design DBCP §HR3 named, now made race-free by I-5.

## 8. IAM policy + bc-infra cross-repo dependency

IAM policy as in §I-4 above. Application:

- **Repo:** bc-infra (`C:\MyProjects\platform-infra-stack`)
- **Likely path:** Terraform / CloudFormation / CDK module owning bc-core's task role definition
- **Author timing:** before PR-G1.5 first invocation in AWS dev; after PR-G1.1 ships in bc-core
- **Verification:** bc-infra PR commits an evidence file demonstrating the policy is attached to bc-core's role ARN (output of `aws iam list-attached-role-policies --role-name <bc-core-task-role>`)

**Local dev mitigation:** developer's AWS credentials (the `barecount` profile per CLAUDE.md) already carry broad permissions; PR-G1.1 vitest and local-dev manual testing work without the bc-infra PR. The bc-infra PR is strictly required for AWS dev and beyond.

**R12 (NEW):** bc-infra PR timing. See §13.

## 9. Updated test obligations (17 total = design DBCP's 15 + 2 new)

Carrying forward design DBCP §7 cases 1-15. Adding:

**16. concurrent grant serialization** — open two concurrent simulated transactions against the same `target_user_uid`; assert that the second transaction waits at `pg_advisory_xact_lock` until the first commits; assert that the second reads the post-first-commit `custom:roles` state. Implementation uses test-only `tx1.begin → lock → ... → tx2.begin → blocked → tx1.commit → tx2.unblocks`. Either real Postgres in an integration test OR a unit test with a `tx`-spy that captures the lock-acquire order.

**17. response `note` field carries the canonical guidance text on BOTH 201 and 409 paths** — for the 201 happy-path test (case 9), additionally assert `response.note` byte-equals the §I-7 locked 201 text. For the no-op 409 test (case 8), additionally assert `response.note` byte-equals the §I-7 locked 409 text. The `note` field is REQUIRED on both paths; an absent or null `note` fails the test.

**18. SDK requestId null is rejected at service layer (F-D enforcement)** — mocked `CognitoAdminService.updateCustomRoles` returns `{ requestId: undefined }`; assert `McfRoleGrantService.grantMcfRoles` throws `CognitoServiceFailureError`; assert controller returns 500 via ProblemDetailFilter; assert audit row is NOT emitted (no INSERT call observed on the tx spy — the service-layer guard fires BEFORE the audit INSERT, so the DB CHECK never runs). Repeats with `{ requestId: '' }` (empty string) and `{}` (missing `requestId` entirely).

### 9.1 Notes on case 16

Concurrent serialization is hard to test cleanly in unit tests without a real DB. Two practical options for PR-G1.1:

- **(a) Pure unit test with mocked tx:** spy on the SQL passed to `tx.execute`; assert `pg_advisory_xact_lock(hashtext(...))` is the FIRST statement of the transaction; assert it's called exactly once per grant call. This proves the LOCK is invoked but not that it actually serializes.
- **(b) Integration test against a local Postgres:** assert two parallel `grantMcfRoles` calls against the same target produce sequential audit rows; assert against different targets they produce concurrent audit rows. Reuses the bc-core integration-test pattern already established for M12.5.

Recommendation: do (a) in PR-G1.1 v1 (cheap and proves the SQL is there); track (b) as a SEPARATE integration-test follow-up — **PR-G1.1-Q-3** (NEW; see §13) — distinct from design DBCP OPEN-Q-6 because (b) tests Postgres advisory-lock serialization (not Cognito SDK sandboxing). Conflating these in a single follow-up risks losing one when the other ships.

## 10. Risk register update — R1 through R12

R1-R11 carry forward from design DBCP §10 with one update:

**R11 (REVISED):** concurrent-grant race — design DBCP defaulted PR-G1 v1 to operator-side discipline + v2 advisory-lock follow-up. **PR-G1.0 revises upward to v1 advisory lock per operator direction.** Mitigation is now `pg_advisory_xact_lock(hashtext(target_user_uid))` at the start of the grantMcfRoles transaction; the v2 follow-up is no longer needed.

**R12 (NEW):** bc-infra IAM policy attachment timing. PR-G1.1 in bc-core can ship with green tests against mocked `CognitoAdminService` but cannot successfully call the endpoint in AWS dev until a separate bc-infra PR attaches the I-4 policy to bc-core's deployed role. PR-G1.5 (operator-attested first invocation) is timing-coupled to the bc-infra PR landing.
- **Mitigation:** PR-G1.5 prerequisites (named in design DBCP §9 and PR-E1 §8) gain a new step: "bc-infra PR attaching I-4 IAM policy to bc-core task role has merged AND evidence committed."
- **Local-dev mitigation:** developer credentials cover the call; PR-G1.1 testing and PR-G1.5 dry-runs in local dev are unblocked.
- **Recommended action:** open the bc-infra PR DURING PR-G1.1 review window (in parallel) so PR-G1.5 is not blocked on a serial cross-repo dependency.

## 11. PR-G1.1 implementation scope + intra-PR sequencing

### 11.1 In scope (single bc-core PR)

1. **Drizzle schema** at `src/database/schema/mcf-role-grant-audit.ts` (per §5)
2. **DDL migration script** at `docker/redesign/<NN>-mcf-role-grant-audit.sql` (per §4.1)
3. **Apply + rollback scripts** at `scripts/mcf-role-grant-audit-apply.mjs` and `scripts/mcf-role-grant-audit-rollback.mjs` (per §4.3)
4. **`CognitoAdminService`** at `src/auth/cognito-admin/cognito-admin.service.ts` + module wiring
5. **`McfRoleGrantService`** at `src/registry/mcf/mcf-role-grant.service.ts`
6. **`SuperAdminGuard`** at `src/auth/guards/super-admin.guard.ts`
7. **`@RequireSuperAdmin()`** decorator at `src/common/decorators/require-super-admin.decorator.ts` + barrel export in `decorators/index.ts`
8. **`McfRoleGrantController`** at `src/registry/mcf/mcf-role-grant.controller.ts`
9. **AppModule registration** + module integration into existing McfModule OR new RoleGrantModule (PR-G1.1 picks)
10. **OpenAPI schemas** for `GrantMcfRolesDto`, `GrantResult` (with `note` field per I-7), and the 4 error envelope shapes
11. **17 vitest cases** per §9 above
12. (REMOVED in amendment v2) — the stale `bc-core/src/app.module.ts:188-191` comment fix is moved to a separate one-commit cleanup PR; bundling a doc-only comment cleanup with substantive service code complicates the 3-agent review at §11.2 step 5. See §11.3.

### 11.2 Intra-PR sequencing (gated)

1. **Commit (a):** Drizzle schema + DDL + apply/rollback scripts. PR opens. Operator reviews the proposed DDL.
2. **Operator approval gate:** explicit message in PR conversation: "approve audit-table DDL apply."
3. **Commit (b):** apply DDL against `bc_platform_dev` via the apply script with env-gate; capture evidence at `scripts/audit-output/mcf-role-grant-audit-apply-<ts>.summary.md`. **Failure recovery (F-F):** if the apply fails (schema collision, env-gate mismatch, DB connectivity, or constraint validation), run `scripts/mcf-role-grant-audit-rollback.mjs` to restore clean state (`DROP TABLE IF EXISTS mcf.role_grant_audit` is idempotent — safe to run even if the table never got created). Diagnose the root cause; fix; re-run apply; re-capture evidence. Do NOT push commit (c) until commit (b) post-apply verification passes (table exists, all 3 indexes exist, all 3 CHECK constraints exist, row count = 0). The PR may sit in commit (a) + failed-apply state during the diagnose-and-fix window; that is recoverable. The PR may NOT progress to commit (c) without clean commit (b) evidence.
4. **Commit (c):** service + guard + controller + tests. Vitest green; lockfile green; tsc green; ESLint green.
5. **Review:** 3-agent parallel strict review (factual + boundary discipline + tests) — matches the established pattern.
6. **Amendments** if review finds issues.
7. **Squash-merge** with full-SHA pin + branch delete.

### 11.3 Out of scope for PR-G1.1

- bc-infra IAM PR (separate repo; separate session)
- PR-G1.5 (operator-attested first invocation; separate action)
- Cognito Groups → role projection (`mcf-auth.config.ts`)
- `mcf_reader` role
- Integration tests against localstack/sandboxed Cognito (deferred follow-up)
- Cross-tenant role grants
- Bulk role grants
- Removing the global admin-bypass from `RolesGuard` (scope-limited to the new endpoint via SuperAdminGuard)
- Stale `bc-core/src/app.module.ts:188-191` comment fix (post-PR-C4 wording cleanup) — moved to a separate one-commit cleanup PR (amendment v2 hygiene): bundling a doc-only comment cleanup with substantive service code would complicate the 3-agent review

## 12. Standing gate state

### Pre-DBCP (bc-docs-v3 main `d60a742`, bc-core main `3adacbd`)

- PR-G1 design DBCP merged ✓
- PR-E1 readiness evidence merged ✓
- 7 OPEN-Q + R11 deferred to PR-G1 implementation DBCP — UNRESOLVED
- Audit table placement undecided
- DB-change protocol shape undecided
- IAM policy snippet undecided
- Concurrency mechanism = operator-discipline default (R11 v1)

### Post-DBCP (this PR merged)

- I-1..I-7 locked
- Audit table DDL proposed and PENDING explicit DB-change approval (CLAUDE.md gate)
- Concurrency upgraded to v1 advisory lock (R11 revised)
- bc-infra cross-repo dependency named as R12
- PR-G1.1 implementation scope fully specified
- Test obligations updated to 17 cases

### Post-PR-G1.1 (next bc-core PR merged, AFTER operator-approved DDL apply)

- `POST /api/admin/mcf/role-grants` live in bc-core
- `mcf.role_grant_audit` table exists in `bc_platform_dev`
- All MCF role grants flow through the service
- Local-dev invocation works; AWS-dev invocation requires bc-infra PR (R12)

### Post-PR-G1.5 (operator-attested first invocation)

- For AWS-dev or beyond: bc-infra IAM policy PR merged (R12 mitigated; bc-core task role carries `cognito-idp:AdminUpdateUserAttributes` + `cognito-idp:AdminGetUser` scoped to `ap-south-1_bM5xehxIx`). For local-dev PR-G1.5 invocation: not required (developer credentials cover it per the `barecount` AWS profile in CLAUDE.md).
- `mcf_author` granted to operator via the service
- Audit row exists; fresh token carries `mcf_author`
- PR-G2 cleared to proceed

## 13. Remaining open questions

Items still genuinely open after this DBCP:

- **OPEN-Q-3 (design DBCP)** — first-`super_admin` bootstrap DBCP. Not addressed here; remains separate scope.
- **OPEN-Q-5 (design DBCP)** — `mcf_reader` allowlist addition. Out of scope.
- **OPEN-Q-6 (design DBCP)** — integration tests against localstack/sandboxed Cognito. Deferred; named in §9.1 as follow-up after PR-G1.1.
- **PR-G1.1-Q-1 (NEW)** — module ownership: does `McfRoleGrantController` register in the existing `McfModule` (alongside intake/panel-run/materialization/PE-MC) OR in a new `McfAdminModule`? Recommend the existing `McfModule` for v1 (one MCF service surface); resolve at PR-G1.1 review time if disagreement.
- **PR-G1.1-Q-2 (NEW)** — should case 16 (concurrent serialization) be a unit test (cheap, no real DB) OR an integration test (real DB, real serialization observable)? §9.1 recommends (a) at v1; PR-G1.1 implementer confirms.
- **PR-G1.1-Q-3 (NEW in amendment v2)** — advisory-lock integration test against real Postgres as a follow-up to case 16 unit test. Distinct from design DBCP OPEN-Q-6 (Cognito sandbox tests) because (Q-3) exercises Postgres `pg_advisory_xact_lock` serialization, not Cognito SDK behavior. Track separately so neither follow-up is lost.

## 14. Non-goals

- No bc-core code change in this DBCP (docs only)
- No DDL applied (PENDING explicit DB-change approval per CLAUDE.md)
- No AWS calls
- No Cognito modification; no role grants
- No M12 / M12.5 / M13 / M14 invocation
- No substrate mutation; no tenant DB touch
- No metric contract authored
- No supersession of PR-S1, PR-C4, PR-G1 design DBCP, MCF-ERR-001, DEC-7f9597/D423, or DEC-ebf0b4/D268
- No update to `mcf-auth.config.ts` (Cognito Groups projection deferred)
- No bc-infra PR opened in this session (separate scope; named only)
- No bc-admin UI design

## 15. References

- PR-G1 design DBCP (parent): `docs/implementation/mcf-role-grant-service-dbcp.md` (merged at `d60a742`, PR #34)
- PR-E1 readiness evidence (sibling): `bc-core/scripts/audit-output/pr-e1-readiness-2026-05-31T02-11-30Z.summary.md` (merged at bc-core `3adacbd`, PR #173)
- PR-S1 (parent of design DBCP): `docs/implementation/metric-context-framework-service-ification-dbcp.md` (merged at `fa1b719`, PR #33)
- PR-C4 (bc-core service surface): bc-core merge `2a7a1e5` (PR #172)
- Auth chain: `bc-core/src/auth/strategies/cognito-jwt.strategy.ts`, `roles.guard.ts:35`, `scope.guard.ts:43-49`
- MCF roles: `bc-core/src/types/enums.ts:20-21`
- Database Rules (D162): CLAUDE.md §Database Rules (10 rules)
- Database Change Protocol: CLAUDE.md §Database Change Protocol (MANDATORY)
- Operator stance ADR: DEC-7f9597 / D423
- Session discipline ADR: DEC-ebf0b4 / D268
- MCF-ERR-001 (intake verdict-aware mutation): `docs/errata/MCF-ERR-001.md`
- Cognito user pool: `ap-south-1_bM5xehxIx` (AWS account `546549546538`, region `ap-south-1`, profile `barecount`)
