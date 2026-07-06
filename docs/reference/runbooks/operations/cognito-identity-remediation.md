---
id: cognito-identity-remediation
title: "Cognito Identity Remediation (Runbook)"
status: drafting
authority: authoritative
doc_type: runbook
governing_adrs:
  - DEC-f0e78e (Platform/tenant authority boundary — distinct classes; narrow platform-inspection carve-out)
  - DEC-952faa (Metric Inspector — amended by DEC-f0e78e D-4)
governing_sources:
  - Security Operations
  - Tenancy and Binding
  - The Authority Model
depends_on: [security-operations, tenancy-and-binding, the-authority-model]
errata_referenced: []
v2_sources: []
diagrams: []
---

# Cognito Identity Remediation (Runbook)

## Purpose

This runbook is the procedural document the operator follows to bring the Cognito user pool `ap-south-1_bM5xehxIx` into compliance with the authority-class invariant declared in DEC-f0e78e D-1:

> A Cognito identity is platform-admin XOR tenant-member. No JWT carries both `platform_admin` (in `custom:roles`) and `custom:tenant_id`.

This runbook is the document. The execution task is `TSK-e5f943`. This document is referenced by `TSK-385fa0` (write-only) and consumed by `TSK-e5f943` (execution).

## Scope

This runbook covers:

- Pool-wide claim audit query shape (read-only AWS CLI commands)
- Per-user remediation table — the two named identities and a generic per-shape recipe
- Split-account path for humans who legitimately need both authority classes
- Rollout sequence designed to avoid mid-flight JWT mismatches
- Rollback / abort criteria
- bc-portal regression dependency
- Provisioning-side guard reference (out of scope here, flagged)

This runbook does **not** cover:

- Designing the provisioning-side guard (Lambda or attribute-mapping rule). That is part of the `TSK-e5f943` execution scope.
- Inspector route family rework. That is `TSK-da749e`.
- Audit table DDL. That is `TSK-6e8174`.
- Audit retention and rotation. Deferred per DEC-f0e78e.

## Prerequisites

Before any step in this runbook is executed:

- DEC-f0e78e is in `decided` status.
- `TSK-6e8174` (audit table DDL) is applied to `bc_platform_dev` after explicit user approval. The audit table must exist before any platform-admin inspection read can succeed; running this remediation before the audit table lands is correct (this remediation is identity-only), but landing the audit table reduces operator-side work later.
- Operator has AWS CLI configured with `AWS_PROFILE=barecount` (account `546549546538`, region `ap-south-1`).
- Operator has rights on the Cognito user pool `ap-south-1_bM5xehxIx`: `cognito-idp:ListUsers`, `cognito-idp:AdminGetUser`, `cognito-idp:AdminUpdateUserAttributes`, `cognito-idp:AdminUserGlobalSignOut`, `cognito-idp:AdminCreateUser`.
- A pre-remediation snapshot of every user's attributes is captured (see `Step 1 — capture rollback snapshot`).

## Authority Class Invariants (the rule the audit checks)

For every active user in pool `ap-south-1_bM5xehxIx`:

- **Platform identity:**
  - `custom:roles` contains `platform_admin` (and may contain other platform-side roles such as `schema_author`)
  - `custom:roles` does **not** contain any tenant-side role (`operator`, `analyst`, …)
  - `custom:tenant_id` is unset (or empty string)
- **Tenant identity:**
  - `custom:roles` does **not** contain `platform_admin` or `schema_author`
  - `custom:roles` may contain tenant-side roles (`operator`, `analyst`, …)
  - `custom:tenant_id` is set to a real tenant slug (must match a row in `tenant.tenants.slug` on `bc_platform_dev`)

Per DEC-f0e78e D-1: `schema_author` is platform-side. If tenant-local authoring is later needed, a distinct tenant-side role name is created. `schema_author` is not reused across the boundary.

A user that satisfies neither shape is a violator. A user that has `(platform_admin in custom:roles) AND (custom:tenant_id is set and non-empty)` is a violator (dual shape). A user that has neither `platform_admin` nor `custom:tenant_id` is a violator (orphan).

## Step 1 — capture rollback snapshot

Before any mutation, capture the current state. This is the only artifact rollback depends on.

```bash
AWS_PROFILE=barecount aws cognito-idp list-users \
  --user-pool-id ap-south-1_bM5xehxIx \
  --region ap-south-1 \
  --output json \
  > cognito-snapshot-pre-remediation-$(date -u +%Y%m%dT%H%M%SZ).json
```

Verify line count and a spot check:

```bash
jq '.Users | length' cognito-snapshot-pre-remediation-*.json
jq '.Users[] | {username: .Username, sub: (.Attributes[] | select(.Name=="sub").Value), email: (.Attributes[] | select(.Name=="email").Value)}' \
  cognito-snapshot-pre-remediation-*.json | head -20
```

Store the snapshot in **encrypted S3** (suggested bucket: `barecount-ops-snapshots/cognito/`) under **least-privilege access** — only the operator role and the rollback-procedure runner. **Retention: 30 days, then automatic delete via S3 lifecycle policy.** Identity snapshots are not retained indefinitely; if an incident or legal hold requires longer retention, the operator opens an explicit hold record before day 30 and the lifecycle rule honors the hold. The snapshot is the rollback source; do not begin Step 3 without it.

## Step 2 — pool-wide claim audit (read-only)

Project the relevant fields and identify violators.

### 2a — list all active users with the relevant attributes

```bash
AWS_PROFILE=barecount aws cognito-idp list-users \
  --user-pool-id ap-south-1_bM5xehxIx \
  --region ap-south-1 \
  --filter 'status = "CONFIRMED"' \
  --output json \
  | jq -c '.Users[] | {
      sub:        (.Attributes[] | select(.Name=="sub").Value),
      email:      (.Attributes[] | select(.Name=="email").Value),
      enabled:    .Enabled,
      status:     .UserStatus,
      roles:      ((.Attributes[] | select(.Name=="custom:roles").Value) // null),
      tenant_id:  ((.Attributes[] | select(.Name=="custom:tenant_id").Value) // null)
    }' \
  > cognito-pool-projection.jsonl
```

Each line is one user. `roles` is the raw JSON-string-encoded array stored in the custom attribute (e.g. `"[\"platform_admin\",\"operator\"]"`).

### 2b — flag dual-shape violators

```bash
jq -c 'select(
    (.roles | fromjson | index("platform_admin")) != null
    and (.tenant_id != null and .tenant_id != "")
  )' cognito-pool-projection.jsonl
```

Every line printed here is a user who must be remediated. The named remediation candidates for this runbook instance include:

- `anant@selenite.co` (intended platform admin, stale `custom:tenant_id=demo-selenite`)
- `anant+sandbox1@selenite.co` (intended sandbox1 operator, holds `platform_admin`)

### 2c — flag orphan-shape violators

```bash
jq -c 'select(
    (.roles | fromjson | index("platform_admin")) == null
    and (.tenant_id == null or .tenant_id == "")
  )' cognito-pool-projection.jsonl
```

These are users who are neither platform admin nor tenant member — sign-in succeeds but the JWT cannot satisfy any route guard. Either remediate by assigning the correct identity class or disable the user.

### 2d — flag tenant identities pointing at non-existent tenants

The `custom:tenant_id` value must exist as a row in `tenant.tenants.slug` on `bc_platform_dev`. Confirm against the live tenant list (read-only):

```bash
psql "$DATABASE_URL" -t -c "SELECT slug FROM tenant.tenants WHERE status_code = 'active'" \
  > active-tenant-slugs.txt
```

Compare each non-null `tenant_id` from `2a` against the active tenant list. Any non-match is a violator; the named stale-tenant example in this runbook instance is `anant@selenite.co` with stale `demo-selenite`.

## Step 3 — per-user remediation table

Three named cases plus a generic recipe. Two are dual-shape violators. The runbook expects each violator to map to one of these cases.

| User | Current shape | Action | Result |
|------|---------------|--------|--------|
| `anant+sandbox1@selenite.co` | `custom:roles=["platform_admin","schema_author","operator","analyst"]`, `custom:tenant_id=sandbox1` | Strip `platform_admin` and `schema_author` from `custom:roles`. Keep `custom:tenant_id=sandbox1`. Keep tenant-side roles (`operator`, `analyst`). | Tenant identity for sandbox1. |
| `anant@selenite.co` | `custom:roles=["platform_admin","schema_author","operator","analyst"]`, `custom:tenant_id=demo-selenite` (stale) | Strip `operator` and `analyst` from `custom:roles`. Unset `custom:tenant_id` entirely. Keep `platform_admin` and `schema_author`. | Platform identity. |
| Any other dual-shape violator | `(platform_admin in roles) AND (tenant_id set)` | Decide the **intended** authority class for the human. If tenant: strip platform-side roles, keep `tenant_id`. If platform: strip tenant-side roles, unset `tenant_id`. If both are required: open a split-account ticket per Step 4. | Single-shape identity matching intent. |
| Any orphan-shape violator | `NOT platform_admin AND NOT tenant_id` | Decide intent. Either assign roles (and `tenant_id` if tenant) or disable the user. | Single-shape identity or disabled. |

### 3a — apply attribute updates

For a user being moved to **tenant identity**:

```bash
AWS_PROFILE=barecount aws cognito-idp admin-update-user-attributes \
  --user-pool-id ap-south-1_bM5xehxIx \
  --username "anant+sandbox1@selenite.co" \
  --user-attributes Name=custom:roles,Value='["operator","analyst"]'
```

For a user being moved to **platform identity** (note `custom:tenant_id` is set to empty string to unset; CLI does not accept removal directly):

```bash
AWS_PROFILE=barecount aws cognito-idp admin-update-user-attributes \
  --user-pool-id ap-south-1_bM5xehxIx \
  --username "anant@selenite.co" \
  --user-attributes \
      Name=custom:roles,Value='["platform_admin","schema_author"]' \
      Name=custom:tenant_id,Value=''
```

### 3b — invalidate existing JWTs

A JWT issued before the attribute update does not reflect the new attributes. The next sign-in mints a JWT against the new shape; until then, the existing JWT may attempt operations the new contract no longer permits. Force a global sign-out so the next call has to re-authenticate:

```bash
AWS_PROFILE=barecount aws cognito-idp admin-user-global-sign-out \
  --user-pool-id ap-south-1_bM5xehxIx \
  --username "anant+sandbox1@selenite.co"
```

Repeat for each remediated user. Not optional. Skipping this leaves a window in which a JWT and the user's true authority class disagree.

### 3c — verify

Re-run `Step 2b`, `Step 2c`, `Step 2d`. The expected output: empty for `2b` (no dual-shape), empty for `2c` (no orphan-shape unless intended-disabled), empty mismatches for `2d` (no stale tenant slugs).

## Step 4 — split-account path for dual-authority humans

A human who legitimately needs both views (e.g. founder reviewing tenant data while also performing platform-admin work) is **not** a dual-shape JWT. The model is two distinct Cognito identities for the same person.

### 4a — naming convention

The existing alias-plus-tenant pattern (`anant+sandbox1@selenite.co`) is the model. For a person `<base>@<domain>` who needs platform admin + sandbox1 tenant:

- Platform identity: `<base>@<domain>` (e.g. `anant@selenite.co`)
- Tenant identity: `<base>+<tenant-slug>@<domain>` (e.g. `anant+sandbox1@selenite.co`)

For multiple tenant identities (one human, multiple tenants): one alias per tenant.

### 4b — create the second identity

If the person holds a dual-shape identity and needs to retain both authorities:

1. Decide which existing user is recast to which class (typically: existing `<base>@<domain>` becomes the platform identity).
2. Create the new tenant identity:

   ```bash
   AWS_PROFILE=barecount aws cognito-idp admin-create-user \
     --user-pool-id ap-south-1_bM5xehxIx \
     --username "<base>+<tenant-slug>@<domain>" \
     --user-attributes \
         Name=email,Value="<base>+<tenant-slug>@<domain>" \
         Name=email_verified,Value=true \
         Name=custom:tenant_id,Value="<tenant-slug>" \
         Name=custom:roles,Value='["operator","analyst"]' \
         Name=custom:display_name,Value="<display name>" \
     --message-action SUPPRESS
   ```

3. Set a temporary password and require change-on-first-login:

   ```bash
   AWS_PROFILE=barecount aws cognito-idp admin-set-user-password \
     --user-pool-id ap-south-1_bM5xehxIx \
     --username "<base>+<tenant-slug>@<domain>" \
     --password '<temporary password>' \
     --no-permanent
   ```

4. Communicate the new credentials to the human via the agreed secure channel (not in the runbook output, not in chat history).
5. Strip the dual claims from the existing identity per Step 3.
6. The human switches authority by signing in with the appropriate identity, never by re-using one JWT across both.

### 4c — password manager and operator workflow notes

The split is real to the operator: two sets of saved credentials, two sign-in flows, two browser profiles or incognito sessions if simultaneous access is needed. Document this in the operator's day-to-day procedure before announcing the change.

## Step 5 — rollout sequence

The order matters. Out-of-order steps can leave users with JWTs that disagree with their true authority class (transient mismatch).

1. **Build and ship the provisioning-side guard.** Pre-token-generation Lambda or attribute-mapping rule that rejects creation/update of any user whose final shape would violate the invariant. Without this, a remediated user can drift back into dual shape on the next admin write. (Design and execution are part of `TSK-e5f943`; this runbook flags the requirement.)
2. **Run the audit (Step 2).** Produce the violator list.
3. **Open a change-record entry** recording the planned remediation (actor, target users, scope, planned start/end). **Direct-notify every affected human** before any global sign-out or claim mutation: "Your sign-in will need to happen again. After the change, your role set may differ." The runbook does **not** permit silent identity changes — the change-record entry **plus** direct notification is a hard prerequisite for Step 4. For the current pilot (founder operating against the founder's own identities), direct founder/operator notification is sufficient. A formal communication channel for larger pools is an Operations decision and is not gated here.
4. **Per affected user, in sequence:**
   1. Apply Step 3a (attribute update).
   2. Apply Step 3b (global sign-out).
   3. Verify the user signs in cleanly under the new shape.
5. **Run the audit again (Step 2)** — confirm zero dual-shape, zero orphan-shape, zero stale-tenant-id rows.
6. **Trigger the bc-portal regression check** — `TSK-476978`. Do not declare remediation complete until that passes.

In a small-pool scenario like this runbook's named case list, Steps 4 can run interleaved without harm. In a larger pool, batch by authority class — remediate all platform identities first, then all tenant identities — so any temporary 401/403 fall on a known set.

## Step 6 — rollback / abort criteria

Abort the remediation if any of the following occurs:

- A remediated user reports they cannot sign in for any reason other than "I need to use the new password / new flow." (User-facing 401 is acceptable post-`admin-user-global-sign-out`; everything else is an abort signal.)
- A remediated platform identity hits an unexpected 403 against `/api/admin/inspection/*` after re-signin.
- A remediated tenant identity hits an unexpected 401/403 against `/api/t/*` after re-signin.
- The audit table (`TSK-6e8174`) is unavailable (Inspector reads will fail closed; this affects bc-admin smoke but does not change the identity remediation correctness).
- Any user is locked out by a misclick during attribute updates.

### Rollback procedure

For a single user:

```bash
# Read the pre-remediation snapshot, find the user, and replay the original attributes.
jq -c '.Users[] | select(.Username=="<username>") | .Attributes' \
  cognito-snapshot-pre-remediation-*.json
# Use the output as the --user-attributes argument:
AWS_PROFILE=barecount aws cognito-idp admin-update-user-attributes \
  --user-pool-id ap-south-1_bM5xehxIx \
  --username "<username>" \
  --user-attributes <restored-attributes>
AWS_PROFILE=barecount aws cognito-idp admin-user-global-sign-out \
  --user-pool-id ap-south-1_bM5xehxIx \
  --username "<username>"
```

For a pool-wide rollback: same procedure, scripted across the snapshot. Pool-wide rollback is the reason Step 1 is mandatory.

A rollback is not a failure of the model. It is a failure of the rollout. Re-plan, fix the cause, re-apply.

## Step 7 — bc-portal regression dependency

The Cognito remediation strips `platform_admin` from intended-tenant identities. bc-portal reads tenant data via `/api/t/*` routes that depend on tenant-side claims, not on `platform_admin`. The expectation is that bc-portal continues to work unchanged. The regression check (`TSK-476978`) verifies this end-to-end.

If bc-portal regresses post-remediation, it is **not** because `platform_admin` was stripped from the tenant identity. It is because some bc-portal code path implicitly required a platform-side role to run. That is a defect to fix in bc-portal — do not roll back the Cognito remediation to mask it. File a separate bc-portal defect task.

## Provisioning-side guard — layered enforcement (founder ruling Q2)

DEC-f0e78e D-1 requires the invariant to hold not just at one-shot remediation but going forward. The guard is **layered**, not either-or. Both layers ship; the token guard is fail-closed and authoritative.

### Layer 1 — Pre-token-generation Lambda (token invariant guard, fail closed)

Rejects token issuance for any identity whose effective shape would violate `(platform_admin in custom:roles) XOR (custom:tenant_id is set)`. Runs at every sign-in. **This is the load-bearing guard** — even if a bad identity row exists in the pool (admin write, manual edit, restored backup, drift), no JWT minted from it can satisfy the invariant.

A misconfigured user discovers the rejection at sign-in time, not at admin-write time. That is acceptable: the alternative — admitting a violating JWT — is unacceptable.

Implementation: Cognito Pre-Token-Generation Lambda trigger on the `ap-south-1_bM5xehxIx` user pool. The Lambda inspects the user's stored `custom:roles` and `custom:tenant_id`, computes the invariant, and either passes the request through or denies token issuance with an explicit reason code.

### Layer 2 — Provisioning-side validation (bad-state prevention)

Rejects the admin write that would leave a user in violating shape. Runs at provisioning time so bad identity state is not created in the pool to begin with. Catches violations at the source instead of at sign-in.

Implementation options (Operations decision; one of):

- Cognito **Pre-Sign-Up** trigger Lambda for self-signup paths
- A wrapper around `AdminCreateUser` and `AdminUpdateUserAttributes` (in the bc-core admin-API layer or in an ops tool) that enforces the invariant before the AWS SDK call
- Attribute-mapping rule if the pool is wired to a federated identity provider

The provisioning-side guard does **not** replace Layer 1. Layer 1 is the fail-closed line. Layer 2 prevents avoidable bad state.

### Sequencing

If forced to ship one layer first: **Layer 1 first**. A pool with the invariant unenforced at the token boundary is exposed; a pool with the invariant unenforced at the provisioning boundary is merely brittle.

Both are required for `TSK-e5f943` to be considered complete.

## Acceptance

This runbook is acceptably executed when:

1. `Step 2b` returns empty (zero dual-shape rows).
2. `Step 2c` returns empty (zero orphan-shape rows) — or every orphan is intentionally disabled and recorded.
3. `Step 2d` returns no mismatches (zero stale `custom:tenant_id` values).
4. The provisioning-side guard is in place.
5. `TSK-476978` (bc-portal regression) passes.
6. The pre-remediation snapshot from `Step 1` is retained per ops snapshot retention policy.

## Open questions

The original three open questions in this runbook have been resolved by founder ruling:

- **Provisioning-side guard mechanism** — resolved as **layered enforcement**. See "Provisioning-side guard — layered enforcement" section above. Layer 1 (pre-token-generation Lambda) ships first; Layer 2 (provisioning-side validation) ships alongside.
- **Snapshot retention** — resolved as **30 days, encrypted S3, least-privilege access**. Automatic delete after 30 days unless an explicit incident or legal hold is opened. See Step 1.
- **Communication channel** — resolved as **change-record entry plus direct notification** before any global sign-out or claim mutation. The runbook does not permit silent identity changes. See Step 5.3. A formal channel for larger pools is an Operations decision and is not gated here.

No outstanding open questions.

## References

- DEC-f0e78e (D388) — governing decision
- DEC-952faa (D386) — Inspector design, amended by D-4 of DEC-f0e78e
- ADR ADR-f0e78e.md, ADR-952faa.md
- TSK-385fa0 (this runbook, write task)
- TSK-e5f943 (execution task — runs this runbook)
- TSK-476978 (bc-portal regression — Step 7)
- TSK-6e8174 (audit table DDL — prerequisite for the Inspector route surface, not for this runbook's identity-only scope)
- RSK-b240f9 (security risk being mitigated)
