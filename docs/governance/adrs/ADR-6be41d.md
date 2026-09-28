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

Operator decision, 2026-09-28 ("Yes. still the creds are NOT IN devhub"), task TSK-84783a.

**Scope.** Only the credentials that the BareCount code and the development setup read while running:
- the dev Cognito accounts;
- the dev secret's keys;
- database role passwords;
- the DevHub write token;
- tokens the dev tooling consumes.

Out of scope: logins to third-party consoles and websites, which the operator keeps in their own password manager, and platform or tenant users, whose applications manage them.

**1. One store.** AWS Secrets Manager (DEC-ecd55c) is the only place a credential value lives. Copies in repo `.env` files and hard-coded fallbacks in code are retired one by one, using the credential map as the checklist.

**2. Credentials are not in DevHub.** No DevHub component (web server, MCP server, database, logs, pages, backups, the billing job or the helper below) stores, caches, logs, displays or returns a credential value. DevHub keeps names, locations, timestamps and check outcomes only.

**3. Credential map (read-only).** DevHub shows every credential name the code reads, across the bc-* repos and DevHub, taken from the code scan. For each name it shows:
- which files read it;
- where its value is supplied on this machine (environment, which secret key, which `.env`, or a default in code);
- whether it resolves;
- the result of a live check (sign-in, database connection, one API read).

It flags duplicates (the same name supplied in more than one place), fallbacks in code, and names that are read but defined nowhere. Resolving a name means checking that it is present, never reading its value into DevHub.

**4. Rotation helper (writes).** A separate local process, not the DevHub web server:
- **Permissions.** It runs under its own least-privilege AWS role: set the password of named users in the dev user pool, `PutSecretValue` on named secret ARNs, and change named database role passwords. It has no `GetSecretValue`, except where the target needs the current value to be replaced, and the value is never returned.
- **Generate, do not type.** It creates the new value itself, applies it to the target, writes it to the secret, and checks that it works, in one step. No person or assistant types or sees the value, which exists only in the helper's memory during that step.
- **Trigger.** Only the operator can trigger it, from DevHub, with a confirmation and the DevHub write token.
- **Not an assistant tool.** It is not exposed as an MCP tool, and an assistant cannot trigger it.
- **Record.** Every action is recorded with who, what, when and the outcome category, in DevHub and in CloudTrail. The value is never recorded.

**5. Amendment to ADR DEC-f4a6b9.** Its secret-store rule ("DevHub never shows values from secret stores ... and reads none, with one exception") gains this helper as a second, bounded exception: it writes values it generated and does not show them.

**6. Cloud changes.** Creating the helper's IAM role, and each first use against a new target, is a cloud change that needs the operator's go.
