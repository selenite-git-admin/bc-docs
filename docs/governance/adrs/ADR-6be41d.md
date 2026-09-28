---
uid: DEC-6be41d
title: "DevHub credential map and credential-rotation helper: credentials stay in AWS Secrets Manager, never in DevHub"
description: "One read-only map of every credential the code and dev setup read, plus an operator-triggered rotation helper that writes straight to Secrets Manager; DevHub stores and shows no credential value."
status: decided
date: 2026-09-28T09:32:48.592Z
project: barecount-devhub
domain: security
subdomain: devhub/credentials
focus: governance
---

# DevHub credential map and credential-rotation helper: credentials stay in AWS Secrets Manager, never in DevHub

## Context

The same credential is supplied in several places (environment, dev secret, per-repo .env, defaults in code, AWS profiles), and a change in one silently breaks the others. On 2026-09-28 a dev password reset left TEST_PASSWORD stale and every DevHub bc-core call failed, including the session-close gate. bc-core also falls back silently to an old user pool when its setting is missing (TSK-b890e2).

A map makes every source visible, and one store removes the copies. Generating the value inside the helper removes the step where a person types a password into two places. Keeping every value out of DevHub, with the helper holding no stored credential and a narrow role, preserves the property that DevHub cannot leak a secret it never has.

## Decision

**Authority.** The operator decided this in chat with Claude (session SES-73d188) on 2026-09-28. The operator's words, in order:
- "There are so many access issues, I am thinking let us create / update tools to manage users and access at one point (platform users and tenant users not part of it -- their respective applications should provide surface for that)."
- "This is beyond read only, but critically required. We can use AWS secrest"
- "third part creds are saved in my google passwords automatically. problem is here in dev env / code"
- To the question of recording the rule change as an ADR, with the helper getting its own tightly limited AWS permissions: "Yes. still the creds are NOT IN devhub"

The auditor takes authority only from the operator directly. The operator confirms this decision to Codex in their own words before this ADR lands.

**Scope.** Only the credentials that the BareCount code and the development setup read while running:
- the dev Cognito accounts;
- the dev secret's keys;
- database role passwords;
- the DevHub write token;
- tokens the dev tooling consumes.

Out of scope: logins to third-party consoles and websites, which the operator keeps in their own password manager, and platform or tenant users, whose applications manage them.

**1. One store.** AWS Secrets Manager (DEC-ecd55c) is the only place a credential value lives. Copies in repo `.env` files and hard-coded fallbacks in code are retired one by one, using the credential map as the checklist. Each credential the helper rotates gets its own secret (one secret, one value), so a write never needs to read or rewrite an unrelated bundle.

**2. Two boundaries.**
- **DevHub** means the web server, the MCP server, the DevHub database, its logs, pages and backups, and the billing job. DevHub never receives, stores, caches, logs, shows or returns credential value bytes. It keeps names, locations, timestamps and fixed outcome categories only.
- **The probe and the helper** are separate local processes outside DevHub (points 3 and 4). They may hold a value in memory only for the one check or rotation they are performing. They return to DevHub only fixed fields: credential name, target, action, outcome category from an allowlist, and timestamp. They never return a value, a fragment of one, or raw error text from a target or AWS.
- **This is a target invariant, not a description of today.** Today the DevHub MCP server's token mint (`src/lib/cognito-credentials.js`) reads password values in-process; that is the existing residual. Moving that mint behind the probe boundary, or retiring it, is part of this decision's migration. Until then, it is listed on the credential map as an open exception.
- **Canary test.** A planted value must never appear in any DevHub API response, page, persisted record, log, error path or backup, including when a target write, a secret write or a check fails.

**3. Credential map (read-only).** DevHub shows every credential name the code reads, across the bc-* repos and DevHub, taken from the code scan. For each name it shows:
- which files read it;
- where it is supplied on this machine (environment, which secret, which `.env`, or a default in code);
- whether it is present;
- the outcome category of a live check (sign-in, database connection, one API read).

It flags duplicates (the same name supplied in more than one place), fallbacks in code, and names that are read but defined nowhere.

Presence is derived without value bytes entering DevHub: secret names come from `ListSecrets` / `DescribeSecret`, and `.env` and code sources from key names. Where only a bundled secret holds a key, its key names come from the probe process, which returns names only. The live checks run in the probe process, never in the DevHub server.

**4. Rotation helper (writes).** A separate local command, never part of the DevHub web or MCP server. The operator runs it in their own Terminal.
- **Operator presence.** Assistants run as the same OS user as the operator, so an OS account cannot tell them apart. Instead, the helper's AWS role can be assumed only with a fresh MFA code from the operator's own device, for a short session. AWS refuses a reused code, which gives fail-closed replay protection, and an assistant cannot produce one. The DevHub write token is never the helper's authorization, so rotating that token does not depend on itself.
- **Allowlist.** Each run names one target and one action from an allowlisted configuration: a pinned dev pool and user, a secret ARN, a database role. Anything else is refused before any write.
- **AWS permissions, target-scoped.**
  - `cognito-idp:AdminSetUserPassword` on the pinned dev pool, for allowlisted users;
  - `secretsmanager:PutSecretValue` on the allowlisted per-credential secret ARNs;
  - nothing else.
  - No `GetSecretValue` on the shared dev secret. Any unavoidable shared-secret case needs its own exact-target design (one ARN, the version workflow, no returned string reaching DevHub, no whole-bundle logs or errors, and an atomicity and recovery plan) and a direct operator grant.
- **Database roles** are changed through a separately constrained database login (its own role, limited to `ALTER ROLE ... PASSWORD` on allowlisted roles). An AWS IAM permission is never used for that. That login's own credential is a per-credential secret the helper may read under the same MFA-bound role.
- **Generate, do not type.** The helper generates the value, applies it to the target, writes it to the target's own secret, and checks it works. No person or assistant types or sees it. On a partial failure, it reports which step failed as a fixed category, and the recovery step, never the value.
- **Record.** After each run, the helper posts fixed metadata to DevHub (who, credential name, target, action, outcome category, time). CloudTrail records the AWS calls.
- **Not an assistant tool.** The helper is not exposed as an MCP tool, and DevHub has no button that runs it. DevHub shows the command to copy, and the result afterwards.

**5. Amendment to ADR DEC-f4a6b9.** Its secret-store rule gains one sentence. The rotation helper and the credential probe are separate processes outside DevHub, which hold a value only transiently. DevHub itself gains no secret access and receives only fixed metadata. The existing billing-job exception stays bounded to its named job and keys.

**6. Order and gates.**
- **First slice:** the read-only credential map (names and presence only), with its canary test. It needs no new privilege.
- **Before any privilege is created:** the helper's IAM role, its database login, and each first use against a new target are cloud or database changes that need the operator's go.
