---
uid: DEC-ecd55c
title: "Connection authority reconciled — config in platform runtime.connection (D168), credentials in AWS Secrets Manager"
description: "Connection config = platform runtime.connection + tenant_id (D168); credentials = AWS Secrets Manager by reference (never any DB). Reconciles the D168/771baf/95687d location tension; amends 95687d §3 cred-in-tenant-DB in-part."
status: decided
date: 2026-07-01T14:17:07.684Z
project: bc-core
domain: connectors
subdomain: connection-authority
focus: credential-isolation
---

# Connection authority reconciled — config in platform runtime.connection (D168), credentials in AWS Secrets Manager

## Context

Three ADRs give apparently conflicting homes for connection storage, and the live pilot exposed the cost of leaving it unreconciled (pilot1 saw apex's connections). D168 (DEC-81cd26, implemented, 2026-03-26) put connection/connection_config/connection_check in the platform DB `runtime` schema with a `tenant_id` ownership column, for FK integrity with connectors (D162 Rule 3), bc-admin cross-tenant visibility without fan-out, and no circular dependency in reader runtime. DEC-771baf (D232, implemented, 2026-03-30) lists `connection*` in the tenant DB `operational` schema (its 4-schema layout predates/ignores the D168 reversal) and states the load-bearing isolation principle: the platform must NEVER read or write a tenant DB. DEC-95687d (proposed, 2026-04-22) §3 step 1 says "the tenant inserts admin.connection + admin.connection_config rows in the tenant DB WITH credentials" — a direct contradiction of D168, and it puts raw credentials in a database. The apparent conflict is really two separate questions conflated into one: (1) where does connection CONFIG live, and (2) where do CREDENTIALS live. Separating them dissolves the tension: config follows the implemented D168 (platform, tenant_id-scoped); credentials go to a managed secret store (AWS Secrets Manager, operator decision 2026-07-01), referenced by connection.authentication_json.credentialRef and resolved via IAM — so the platform reads the secret store, not the tenant DB. This honors 771baf's isolation intent a third way (creds never leak across tenants because they are never in the shared platform DB either), and it makes 95687d's "creds in tenant DB" step unnecessary. The live cross-tenant leak is therefore a filtering/access-control gap on the platform read surface, NOT a storage-location problem — the correct fix is tenant_id scoping, not a tenant-DB move.

The three ADRs, and where they disagree on the surface:

- **DEC-81cd26 (D168, `implemented`, 2026-03-26)** — `connection`, `connection_config`, `connection_check` belong in the **platform DB `runtime` schema**, with a `tenant_id` column for ownership filtering. Connections are infrastructure/config (same category as connectors, readers, contracts), not execution data. This reversed D163's tenant-DB move for FK integrity (D162 Rule 3), bc-admin cross-tenant visibility without fan-out, low volume (5–20/tenant), and to avoid a circular dependency in reader runtime. **The live bc-core code follows this** — `connection.repository.ts` binds `runtime.connection`.
- **DEC-771baf (D232, `implemented`, 2026-03-30)** — its tenant-DB layout lists `connection(_config,_check)` in the tenant `operational` schema (a pre-D168/D163-era listing), and states the load-bearing rule: **the platform must NEVER read or write a tenant DB** (one-way dependency; a tenant's data — including credentials — is the tenant's property).
- **DEC-95687d (`proposed`, 2026-04-22)** — a large typed-first / Schema-Provisioner ADR whose §3 step 1 says, incidentally, *"the tenant inserts `admin.connection` + `admin.connection_config` rows in the tenant DB **with credentials**."* This contradicts D168 and puts raw credentials in a database.

Live symptom (pilot, 2026-07-01): tenant `pilot1` saw tenant `apex`'s connections. The platform `/connections` CRUD controller (`@Controller('connections')`, not under `/t/`) is **not** tenant-scoped, while the `/t/connections` view (`@TenantScoped`) is.

Verified first-hand (`credential-resolver.service.ts`, 2026-07-01): the credential model is already **reference-based** — `ConnectionAuthentication = { method, credentialRef, config? }`, with the file's own contract *"Secrets are NEVER stored in the database — only references to external stores."* **But** only `env:` resolution is implemented; the `ssm:` prefix throws *"SSM credential resolution not yet implemented"*; AWS Secrets Manager is **not wired**.

## Decision

**Split the two questions that were conflated — config location vs credential location — and answer each.**

1. **Connection CONFIG authority = D168 (DEC-81cd26, implemented).** Connection config (endpoint, connector FK, environment, status, health, `authentication_json`) lives in the **platform DB `runtime.connection` (+ `_config`, `_check`) with `tenant_id`** for ownership. No tenant-DB move; no `runtime.connection` retirement. This is affirmed, not changed.

2. **Connection CREDENTIALS authority = AWS Secrets Manager (operator, 2026-07-01).** The actual secret (password, api key, OAuth secret) lives in **AWS Secrets Manager**, never in any database. The DB stores only a **reference**: `connection.authentication_json = { method, credentialRef }`, where `credentialRef` points at the secret. The platform resolves it via IAM at runtime (`CredentialResolverService`), **never** opening a tenant DB.

3. **This reconciles all three ADRs:**
   - **D168 is honored** — config stays in the platform table it already lives in.
   - **DEC-771baf's isolation intent is honored a third way** — the platform reads the *secret store*, not the tenant DB; and because credentials live in *neither* the platform DB nor the tenant DB, one tenant's credentials can never leak to another through a shared DB. "Platform DB vs tenant DB for credentials" was the wrong question. (771baf's `operational`-schema connection listing is a superseded-by-D168 layout artifact, not a live contradiction.)
   - **DEC-95687d is amended IN PART, not superseded.** Its typed-first runtime + Schema-Provisioner core (the substance of the ADR) is untouched and remains `proposed`. Only its §3 step-1 *"tenant inserts admin.connection with credentials in the tenant DB"* is amended: connection config → platform `runtime.connection` per D168; credentials → Secrets Manager reference, not a tenant-DB write. `admin.connection` (tenant DB) is **not** wired for the pilot.

4. **The live cross-tenant leak is an access-control/filtering gap, not a storage problem.** Because config correctly lives in a platform table with `tenant_id`, the fix is to **enforce `tenant_id` scoping on tenant-facing connection reads** and consolidate the two surfaces (one tenant-scoped path `/t/connections` + `/t/connectors-catalog` for the customer; platform `/connections` CRUD restricted to admin scope). No schema change, no tenant-DB move.

## Current state (honest) + follow-up

- **Built + correct today:** the reference-based shape (`{ method, credentialRef }`; secrets never in the DB) and `env:` resolution for the exchange-rate/dev connectors.
- **NOT built today:** the managed-secret-store strategy. `ssm:` throws "not yet implemented"; there is no `secretsmanager:` strategy. Until a store-backed strategy ships, real customer credentials cannot be resolved from Secrets Manager — only `env:` works.
- **Follow-up (scoped task):** add a secret-store resolution strategy to `CredentialResolverService` (a `secretsmanager:<arn|name>` credentialRef prefix, resolved via the `barecount` IAM profile) with SSM Parameter Store as an optional second backend. This is the gate before any real (non-`env:`) customer connection is credentialed. This ADR **decides the target**; it does not claim the wiring exists.

## Consequences

- Slice 1 (the customer connection wizard) builds against the platform `runtime.connection` API under a **tenant-scoped** path; no re-plumbing of the connection service to a tenant DB (the earlier "Option B tenant-side `admin.connection`" direction is retracted).
- Credentials entered in the wizard are written to Secrets Manager and only a `credentialRef` is stored on the connection — once the store-backed resolver strategy ships. Until then the pilot uses `env:`-referenced credentials.
- 771baf's "platform never touches tenant DB" invariant is preserved with zero exceptions.
- ADR-audit `supersessionIssues` stays at 0 — no frontmatter `supersedes` is set (95687d is amended in-part, in-body, not flipped).
