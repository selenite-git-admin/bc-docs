---
uid: NOTE-connection-slice-platform-2026-07-01
title: "Connection Slice — Platform Design Note (schema deltas + API contract + the connection-authority decision)"
description: "The platform contract for Slice 1 (customer connection flow). Grounds what already exists (full catalog/connector/connection APIs), surfaces the one real decision — connection authority: platform runtime.connection (current, unfiltered, credentials in the shared DB) vs tenant-side admin.connection (ADR-771baf) — with its attached tenancy/credential-isolation leak, options, and the minimal schema deltas + DB-approval asks. Platform-first, before any bc-portal code."
status: draft
authority: note
date: 2026-07-01
project: bc-core
domain: readers
---

# Connection Slice — Platform Design Note

## 0. Purpose

The platform contract for **Slice 1** (the customer connection flow, per the Connection Onboarding model note). Platform-first: bc-core schema + API settled and DB-approved **before** any bc-portal page. bc-portal will only consume the API defined here.

## 0a. Decisions locked (operator, 2026-07-01) — CORRECTED

> **Correction (2026-07-01):** an earlier draft of this note chose "Option B — tenant-side `admin.connection`." That was **wrong** — it contradicted the *implemented* decision **D168** and jumped to the *proposed, unbuilt* DEC-95687d. Caught by operator research (the discipline of checking decisions before deciding). The corrected, grounded decision is below.

- **Connection authority = D168 (implemented) — platform `runtime.connection` + `tenant_id`.** Connections are **infrastructure/config, not tenant execution data** (D168, `ADR-81cd26`/`bc7281`, which superseded D163's tenant-DB move for FK integrity, admin visibility, and no-circular-dependency — the "logistics" reasons). No tenant-DB move; no `runtime.connection` retirement.
- **Credentials = AWS Secrets Manager (operator, 2026-07-01).** The DB (platform *or* tenant) stores only a **reference** (`connection.authentication_json.credentialRef`); the actual secret lives in AWS Secrets Manager. The platform resolves it via IAM (`CredentialResolverService` — already built), **never** reading the tenant DB. This **satisfies ADR-771baf a third way** (platform reads the secret store, not the tenant DB) and **dissolves the D168 ↔ DEC-95687d tension** — credentials live in *neither* DB, so "platform vs tenant DB for creds" was the wrong question. DEC-95687d's "insert creds into `admin.connection`" is amended-in-part by the secret-store model. → **Reconciling ADR filed: `DEC-ecd55c` (D474)** — affirms D168, amends DEC-95687d §3 in-part (not a wholesale supersession — 95687d's typed-first core stands), honors 771baf a third way. Records the honest current-state: `CredentialResolverService` has the correct `{method, credentialRef}` shape + `env:` resolution only; the `secretsmanager:` strategy is unbuilt (follow-up TSK-3da1f0).
- **`admin.connection` (tenant DB) is NOT wired** for the pilot — it is the DEC-95687d proposal (unbuilt, 0 rows); credentials go to Secrets Manager instead.
- **Platform surface = seed + API first**; bc-admin management UI is a follow-on.

**Grounded delta (D168) — NO schema change, so NO DBCP:**
1. **Fix the cross-tenant leak by scoping, not moving.** The leak (pilot1 saw apex's connections) is a *filtering* gap, not a storage-location problem: the platform `/connections` CRUD controller is **not** tenant-scoped, while the `/t/connections` view (`@TenantScoped`) is. Enforce `tenant_id` scoping on tenant-facing connection reads.
2. **Consolidate the two surfaces** (no-coexistence, per operator): one authoritative tenant path (`/t/connections` + `/t/connectors-catalog`, tenant-scoped) for the customer; the platform `/connections` CRUD is admin-only (or restricted). Delete/retire whichever duplicate is redundant — on the *platform* table, no tenant-DB move.
3. **Verify** `CredentialResolverService` resolves `credentialRef` from AWS Secrets Manager (wire the backend if it currently uses a placeholder/env).
4. **Seed** the SAP ECC / S/4HANA connectors the pilot needs (2 live).

**STATUS (SES-f4abf7, 2026-07-01) — leak FIXED + proven live.** Items 1–3 done: the cross-tenant leak was in `TenantConnectionController` (`/t/connections`, `@TenantScoped`) — its `listConnections`/`getConnection`/`listChecks` handlers never injected `@CurrentTenant()` nor passed `tenantId`, so a tenant-scoped call returned *all* tenants' connections. Fix (code only, no schema — the `tenant_id` column already exists per D168): repo now projects + filters `tenant_id`; `ConnectionService.getConnection(id, tenantId?)`/`listChecks(...,tenantId?)` enforce ownership (404, not 403, so existence isn't revealed); the controller passes `tenant.tenantId`. The platform `/connections` CRUD is already `@PlatformOnly()` (admin, sees all — unchanged). Verified: `/t/connections` as pilot1 → 0 (was 3); platform `/connections` → all 3; pilot1 GET apex's connection by id → 404. Item 3: resolver is `env:`-only, Secrets Manager unbuilt → TSK-3da1f0. Item 4 (ECC connector) deferred into the Slice-1 build → TSK-452201. Consolidation: no duplicate to delete — platform CRUD = admin authoring, `/t/connections` = customer reads; they are scope-split, not redundant.

**Naming resolution — Connector lifecycle (operator-locked 2026-07-01; see model note §0b).** "Connection" retired as a customer-facing concept; the single concept is the **Connector** with lifecycle `Available → Configured → Active → Connected ⇄ Disconnected`. Data impact:
- The *Configured/Active Connector instance* lives in **`runtime.connection`** (platform, D168) — the conventional connector-type + connection-instance split; `runtime.connector` stays the *Available* driver.
- **Status vocabulary:** `runtime.connection.connection_status` holds the **lifecycle** (`configured` / `active` / `suspended` / `archived`), separate from **health** (`connected` / `disconnected`, derived from the latest `connection_check`). (Note: `connection_status` here diverges from the `status_code` convention used by reader/connector/flavor — a possible small cleanup, non-blocking.)
- The API/UI present Connector states; the `connection` table is never customer-facing.

## 1. What already exists (the platform is ~90% built)

Grounded in bc-core controllers (2026-07-01):

| Capability | API (bc-core, under `/api`) | Backing |
|---|---|---|
| **Catalog** Provider→System→Version (+ modules/objects/fields) | `/source-catalog/providers`, `/systems`, `/versions`, `/modules`, `/objects`, `/fields` — list + `:id` + `catalog`/`stats` | `source.*` (platform) |
| **Connectors** | `/connectors` — POST, GET list, GET `:id`, `governance`, `:id/usage`, PATCH `:id` | `runtime.connector` (platform) |
| **Connections** | `/connections` — POST, GET list, GET `:id`, PATCH, DELETE, GET `:id/flavors`, POST/GET `:id/checks`, GET `:id/health` | `runtime.connection` (platform) |

So Slice 1's platform work is mostly **verify + one decision + fill gaps** — not net-new schema. The catalog drill-down, connector list, connection create/test(`/checks`)/health the wizard needs are all present.

## 2. The one real decision — Connection authority (the corner-piece)

**Two connection homes exist; the API uses the wrong one for tenancy.**

- `connection.repository` reads/writes **`runtime.connection` (platform DB)**, and `/connections` is a **platform route** (`@Controller('connections')`, NOT under `/t/`) — so it is **not tenant-scoped**. Live proof: `pilot1` sees `apex`'s connections (the list isn't filtered by tenant). Every tenant's endpoint + credential reference sits in the **shared platform DB**, visible across tenants.
- The tenant DB (`tbc_pilot1_dev`) already has **`admin.connection` / `admin.connection_check` / `admin.connection_config`** — the tenant-side home per **ADR-771baf** (connections are tenant-owned; credentials are tenant property; platform never leaks one tenant's creds to another). Currently **unused by the API**.

This is the multi-tenancy corner-piece (PoV §2/§8 Q1) made concrete: **where do connections live?**

**Option A — Platform `runtime.connection` + tenant scoping.** Keep the current table; add `tenant_id` filtering to `/connections` (or move it under `/t/` so the middleware scopes it). Smallest change; API mostly works. **But credentials stay in the shared platform DB** — contradicts ADR-771baf's isolation; a weaker security posture as tenants scale.
- *Risk:* one DB compromise exposes all tenants' connection config; the isolation ADR-771baf mandates is not realized.

**Option B — Tenant-side `admin.connection` (ADR-771baf-correct).** Connections live in each tenant's DB (`admin.connection`). Platform provisions the tenant-side tables; the API reads/writes the tenant DB via the tenant connection (under `/t/` so it's tenant-scoped). Credentials never sit in the shared DB. **More work** (repoint the connection service/repo to the tenant DB; cross-DB; connection create becomes a tenant-DB write). Architecturally correct + fixes the leak by construction.

**Recommendation (for the operator):** **Option B is the right end-state** — it's what ADR-771baf already decided, it fixes the live cross-tenant leak, and connection is the tenant's anchor (P-F6). For the **single-tenant pilot**, Option A is *tolerable short-term* to unblock, but since we're being deliberate about the corner-piece, resolving to **B now** avoids re-plumbing the connection service twice. **This is the decision to lock before Slice 1 code.**

## 3. Schema deltas (DB Change Protocol — approval-gated)

Driven by the §2 decision:

- **If Option B (recommended):** no *new* tables — `admin.connection(_config,_check)` already exist in the tenant DB. The delta is (a) confirm those tenant-side tables match `runtime.connection`'s shape (they appear to); (b) **code**: repoint `ConnectionRepository`/`ConnectionService` to the tenant DB (via `TenantConnectionService.forTenantData`) and move `/connections` under `/t/`; (c) **retire/repurpose** `runtime.connection` (platform) — migrate its 3 rows or mark deprecated. Minimal *schema* change; mostly a routing/ownership move.
- **If Option A:** add `tenant_id` filtering to the connection reads + a NOT-NULL/index on `runtime.connection.tenant_id`; keep the table. Smaller now, but leaves the ADR-771baf debt.
- **Catalog / connector:** no deltas — the tables + APIs exist. (Connector catalog is sparse — 2 rows — but that's *seed data*, not schema.)

No schema is touched until you pick A or B and approve the specific DDL/routing change.

## 4. API contract for bc-portal (Slice 1)

The v3 `ConnectionsPage` wizard consumes (all existing, modulo the §2 routing move):

```
Catalog drill-down:
  GET /source-catalog/providers                      → vendors (SAP…)
  GET /source-catalog/systems?providerId=…           → systems (ECC, S/4HANA)
  GET /source-catalog/versions?systemId=…            → versions (EHP8, Public/Private Cloud)
Connectors:
  GET /connectors?system=…&version=…                 → protocol options for (system, version)
Connection wizard:
  POST /connections            {connectorId, endpoint, environment, auth, scope?}   → create (draft)
  POST /connections/:id/checks {type: ping|auth_test}                               → test (connection_check)
  GET  /connections/:id/health                                                      → health chip
  GET  /connections                                                                 → tenant's connection list
```
*(Under Option B these move under `/api/t/…` and are tenant-scoped; under Option A `/connections` gains a tenant filter.)* The exact query-param shapes are verified against the controllers during platform build; any gap (e.g. connector filter by system+version) is a small additive endpoint, not schema.

## 5. bc-admin scope

Platform authoring surfaces (manage catalog + connectors + reader templates) live in bc-admin. **For the pilot: not required up front** — the catalog + connectors can be **seeded** (they largely exist), and bc-portal builds against the API. bc-admin management UI is a **follow-on** (add when humans need to curate the catalog/connectors without seeds). *Operator confirm: seed-first, bc-admin UI later — or build bc-admin catalog/connector management now?*

## 6. Decisions to lock (operator) + DB asks

1. **Connection authority — A or B** (§2). *Recommendation: B.* Gates Slice 1 code + the schema delta.
2. **bc-admin scope now vs later** (§5). *Recommendation: seed + API first.*
3. **DB approval:** the specific delta from decision 1 (Option B: routing/ownership move + retire `runtime.connection`; Option A: `tenant_id` filter/index). No DDL until approved.

## 7. Slice 1 sequence (once locked)

```
1. Lock §2 + §5, approve §6 DB delta.
2. Platform: apply the connection-authority change (bc-core) + verify the catalog/connector/connection
   APIs return what §4 needs + seed the connector catalog for SAP ECC/S4HANA.
3. bc-portal: build the v3 ConnectionsPage wizard on the frozen API (pure UI).
```

Legacy `/data-sources` (`ConnectedDataSourceDetailPage`, `ConnectionStatus`, `ActiveReaders`) = reference for the screens; retired once v3 covers the flow.
