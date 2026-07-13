---
uid: SRC-e4a7b2
slug: microsoft-d365-bc
title: "Microsoft Dynamics 365 Business Central"
description: "Microsoft Dynamics 365 Business Central admission research: candidate access paths (API v2.0 / OData V4, custom APIs, webhooks) under Microsoft's API and licensing terms; permissibility per customer/deployment is a clearance decision against the governed authority objects, not asserted here."
type: source-systems
status: published
domain: enterprise-erp
subdomain: microsoft
focus: governance
authority_role: projection        # D526 Amendment 1 — projection, not an authority
# --- evidence maturity (D385): what evidence exists, at what scope. NOT an audit verdict. Requires governed evidence. ---
proof_status: designed            # NO evidence of any kind exists — no executor, no simulator profile, no customer engagement. Promote only when a governed proof-scope/evidence object is minted.
proof_scope_refs: []              # governed source-proof-scope UID — none
source_realization_refs: []       # governed source-realization-package UID — none
audit_decision_refs: []           # signed audit-decision UID — none (no realization audit run for Business Central)
# --- exact governed reference coordinates — authority is the REFERENCED object, not these strings; ⧗ = capability/registration pending ---
source_registry_ref: null         # SRC registry UID + exact provider/system/version (⧗ pending source-registration)
reader_flavor_versions: []        # exact reader-flavor version UID + digest (⧗ pending; slugs below are labels only)
catalog_root: null                # source-catalog snapshot / mapping-root digest (⧗ pending)
contract_set_ref: null            # SC/AC/OC/CC version-set UID or contract-set digest (⧗ pending)
admission_contract_versions: []   # AC version UIDs realized against Business Central — none authored (see contracts.md)
official_research_refs: []        # structured {source, version, retrieved_at, digest} per official citation (⧗ digest capture pending — 3rd capability gate)
last_verified_at: 2026-07-13
official_docs_url: https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/
system_type_code: microsoft_d365_bc   # label; authority = source_registry_ref
reader_flavors:
  - microsoft-d365-bc-rest-v2     # label (candidate); authority = reader_flavor_versions[]
  - microsoft-d365-bc-custom-api  # label (candidate); authority = reader_flavor_versions[]
  - microsoft-d365-bc-webhook     # label (candidate); authority = reader_flavor_versions[]
catalog_ref: catalog.md           # human link; authority = catalog_root + source catalog (source.*)
docket_files:
  - contracts.md
  - catalog.md
  - onboarding-log.md
  - evidence.md
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendments 1/2/3)
supersedes: docs/reference/source-systems/microsoft-d365-bc.md
---

# Microsoft Dynamics 365 Business Central

> **Docket cover — this is a PROJECTION, not an authority (DEC-8570d4 Amendment 1).**
> This `index.md` indexes and links governed objects; it does not create source registration, contract
> identity, catalog authority, evidence, or audit decisions. Registries own identities; the audit substrate
> owns evidence and PASS/REJECT/OPERATOR_REVIEW decisions (D525). `proof_status` below is **evidence maturity,
> not an audit verdict**. Reference narrative is here; concrete artifacts are referenced via the sibling files
> under [Docket Contents](#docket-contents).

Microsoft Dynamics 365 Business Central is Microsoft's SMB/mid-market ERP, available as a Microsoft-operated
online (SaaS) service and as an on-premises deployment (including containerized developer instances). Data
access on the online service is through Microsoft-published surfaces — the **standard REST API v2.0** (OData V4,
company-scoped resources), **customer-developed custom APIs** (AL API pages), **OData/SOAP web services over
pages and queries**, and **webhook subscriptions** for change notification. The underlying application table
shapes are publicly documented per table in Microsoft Learn's **application reference**, and the base
application's AL source is published under the MIT license in the **microsoft/BCApps** GitHub repository.
Business Central online receives **two major release waves per year plus monthly minor updates** — a continuous,
Microsoft-managed baseline. BareCount researches the API v2.0 surface (with custom APIs and webhooks as
companions) as **candidate access paths**; which path is permissible for a given customer/deployment is a
**clearance decision** made against the governed authority objects (see §4.A), not asserted here.

No Microsoft-specific admission-stance ADR exists yet (the SAP analogue is D384). Until one is decided, this
docket records official research only; no access path is characterized as sanctioned or excluded.

---

## Docket Contents

| File | Holds |
|---|---|
| **index.md** (this file) | Proof status, reader-flavor binding, reference (admits / legal / commercial / technical / gaps), onboarding runbooks, references, changelog |
| [contracts.md](contracts.md) | Contracts authored against Business Central + candidate OC design notes (signed amount + dual debit/credit columns, detailed-ledger application state, dimension set model) |
| [catalog.md](catalog.md) | Business Central table/API-entity catalog footprint (G/L Entry-class tables, API v2.0 entities) |
| [onboarding-log.md](onboarding-log.md) | Dated onboarding-execution log |
| [evidence.md](evidence.md) | Proof entries — none exist; no simulator coverage; first-hand pending |

---

## 1. Proof Status (evidence maturity) & Audit Decisions

Two orthogonal vocabularies — never infer one from the other (D526 Amendment 1).

**Evidence maturity — `designed`** as of 2026-07-13. Evidence maturity requires *governed* evidence; none exists
for Business Central — and, unlike SAP ECC, there is **no ungoverned background either**: no reader executor has
been built for the BC REST v2.0 surface, no bc-sdg simulator profile exists for Business Central, and no
customer or vendor instance has ever been touched. See [evidence.md](evidence.md).

- **Zero validation of any kind.** No API call, no OData read, no Microsoft Entra token exchange has been
  executed by BareCount against any Business Central instance, real or simulated.
- Promotion to `shape_tested` requires a **minted governed proof-scope/evidence object** with
  `proof_scope_refs[]` / `source_realization_refs[]` populated; `first_hand_proven` requires a real-instance
  entity/scope-specific governed evidence entry — **never** a whole-system promotion of "Business Central."
- Zero-claims rule (D385): until a real Business Central instance has produced metric snapshots end-to-end,
  **no external "we work with Business Central" claim may be made.**

**Audit decision — none.** No source-realization audit (D525) has been run for Business Central;
`audit_decision_refs[]` is empty. PASS/REJECT/OPERATOR_REVIEW are decided and stored in the audit substrate
against an exact realization package; this docket would only ever render such a decision as a labelled "derived
projection" with its governed UID/digest, never as its own authority.

---

## 2. Reader Flavor Binding

| Flavor | Target | Executor | AC version |
|---|---|---|---|
| `microsoft-d365-bc-rest-v2` (candidate) | Standard API v2.0 (`https://api.businesscentral.dynamics.com/v2.0/{tenant}/{environment}/api/v2.0/companies({id})/{resource}`) | — (not built) | — |
| `microsoft-d365-bc-custom-api` (candidate) | Customer-developed AL API pages (`/api/{publisher}/{group}/{version}/`) | — (not built) | — |
| `microsoft-d365-bc-webhook` (candidate) | Subscription API push notifications (delta trigger, not a bulk reader) | — (not built) | — |

All flavors are **candidate labels only** — no executor exists for any of them, and `reader_flavor_versions[]`
is empty. The REST v2.0 flavor is the expected first build (row-level reads, delta by `$filter`); the webhook
flavor would only ever be a delta *trigger* companion, never a standalone admission path.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of accounts (G/L Account → API `accounts`); company information; dimensions and dimension values;
currencies; posting-group configuration; payment terms and methods; units of measure; countries/regions. Table
and field shapes come from two vendor-published surfaces requiring no customer system: the per-table
**application reference on Microsoft Learn** (e.g. [Table "G/L Entry" (ID 17)](https://learn.microsoft.com/en-us/dynamics365/business-central/application/base-application/table/microsoft.finance.generalledger.ledger.g-l-entry))
and the MIT-licensed AL source in [microsoft/BCApps](https://github.com/microsoft/BCApps). Stored as Tier 5/6
entries in the Source Catalog — see [catalog.md](catalog.md).

### 3.2 Business data

Posted business records from Business Central ledger and document tables — general ledger entries (G/L Entry
class), customer/vendor ledger entries and their detailed-ledger application entries, item ledger entries, sales
and purchase invoices/credit memos, sales orders, and master data (customers, vendors, items). Admitted via the
standard API v2.0 entities (e.g. `generalLedgerEntries`, `customers`, `vendors`, `items`, `salesInvoices`,
`purchaseInvoices`, `salesOrders`) or, for shapes the standard API does not expose, via customer-developed
custom APIs. Cataloged in [catalog.md](catalog.md).

On Business Central online the customer never has direct SQL access: the "object" BareCount observes is an
**API entity (AL API page) or OData-exposed page/query over** the documented application table, not the table
itself. Canonical resolution does the same job either way; only the binding differs.

---

> **Scope of §4–§6 (D526 Amendment 1).** Official, general research only — Microsoft policy and the requirements
> any customer must satisfy. **No** tenant names, contracts, credentials, endpoints, approvals, or legal
> conclusions: those are governed-substrate objects referenced by pseudonymous UID/digest from
> onboarding-log.md / evidence.md. Retrieval date + digest for each official source are pinned in
> [References](#9-references) (⧗ digest TODO).

## 4. Legal & Licensing

### 4.A Platform Plane — Microsoft legal & licensing (general)

> **Researched conditions — NOT clearance conclusions.** Nothing here is "sanctioned" or "banned" by BareCount
> assertion. Each condition holds only as supported by a **version-exact** official Microsoft source (recorded
> in `official_research_refs[]` with retrieval date + exact version + content digest — ⧗ digest capture pending,
> 3rd capability gate) and, at runtime, by an exact-release **Platform Source Access Policy** plus the customer's
> **Tenant Source Authorization** (deferred governed authority objects). Which path is permissible for a given
> customer/deployment is a **clearance decision** made against those objects — not asserted here. This is
> assurance research, not legal advice.

**4.A.1 API surfaces and terms (researched, pending exact-version verification).** Microsoft publishes the
standard API v2.0, custom APIs, OData/SOAP web services, and webhook subscriptions as documented product
surfaces of Business Central ([API v2.0 reference](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/)).
The API v2.0 documentation directs integrators to the
[Microsoft APIs Terms of Use](https://learn.microsoft.com/en-us/legal/microsoft-apis/terms-of-use). Whether a
given surface, used by a third-party processor on the customer's behalf, is within the customer's subscription
terms (Microsoft online service terms / universal license terms and the customer's licensing agreement) is a
**customer/Microsoft determination** verified per engagement — ⧗ version-exact service-terms review pending.
Paths BareCount does **not** research: direct database access (not offered on BC online), screen-scraping, or
any undocumented interface.

**4.A.2 Documentation and source licensing (researched).** Unusually for an ERP vendor, both the documentation
and the base-application source are published under open licenses:
- The Business Central end-user documentation source repository
  ([MicrosoftDocs/dynamics365smb-docs](https://github.com/MicrosoftDocs/dynamics365smb-docs)) carries
  **CC-BY-4.0** for documentation content plus **MIT** for code samples (LICENSE / LICENSE-CODE, verified
  2026-07-13). ⧗ The developer/IT-pro docs source repository's public license is not yet individually confirmed.
- The Business Central application source ([microsoft/BCApps](https://github.com/microsoft/BCApps)) — System
  Application, Business Foundation, Base Application, and first-party apps in AL — is published under the
  **MIT license** ("The source code in this repository is available to everyone under the standard MIT
  license," verified 2026-07-13).

These licenses govern *research and catalog-seed provenance* only — they say nothing about runtime access to a
customer's Business Central service, which remains a subscription/licensing matter (§4.A.4).

**4.A.3 Read vs write-back.** BareCount reads only today. API v2.0 permits write operations
(POST/PATCH/DELETE); if an Action Engine ever creates Business Central documents, the customer's licensing
terms and Microsoft's API terms for write access must be resolved in the customer contract before activation.

**4.A.4 User/licence types (researched — commercial consequences are a customer/Microsoft determination).**
Microsoft's licensing documentation ([Licensing in Business Central](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/deployment/licensing))
names **Essentials** and **Premium** (full users), **Team Member** (limited use), **Device**, and **External
Accountant** license types, plus read-only access through Microsoft 365 licenses; entitlements are enforced
above assigned permissions. For machine access, Microsoft's web-services authentication comparison states that
OAuth service-to-service integrations require **"No license required for service-to-service integrations"**
([Web services authentication](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/web-services-authentication))
— recorded here as a researched vendor statement, **not** a BareCount licensing conclusion; any commercial-
licence consequence (including multiplexing considerations) is a customer/Microsoft determination against the
current [Dynamics 365 Licensing Guide](https://go.microsoft.com/fwlink/?LinkId=866544) (⧗ exact edition +
retrieval digest pending).

**4.A.5 Update cadence / support horizon (researched).** Business Central online receives **two major update
cycles per year (general availability every April and October)** plus **minor updates every month in between**;
each major update has a five-month update period, then a grace period, then enforced updates
([Update cycles](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/update-rollout-timeline)).
There is no customer option to remain on an old online version long-term; any BareCount realization must be
verified against a moving release baseline. On-premises follows the customer's own upgrade cadence with
cumulative updates. Exact policy version + retrieval date + digest ⧗ pending.

### 4.B Tenant Connection Plane — customer authorization prerequisites (general, not tenant-specific)

What **any** Business Central customer must have/authorize before connection (stated generically — no named
tenant, no actual approval; those live in the governed substrate):
- **Vendor entitlement**: an active Business Central online subscription (Essentials/Premium tier covering the
  modules in scope) or, for on-premises, a valid Business Central licence for the deployed version.
- **Licensing posture**: whether the connector's service-principal (S2S) access or any dedicated integration
  identity carries subscription consequences is a **customer/Microsoft determination**, not a BareCount
  conclusion — verify against the customer's agreement and the current Dynamics 365 Licensing Guide (§4.A.4).
- **Scope authorization**: internal approval to expose the selected modules/data (GL/AR/AP/inventory/sales
  entities and companies) to an external processor.
- **Entra admin consent**: the connector's Microsoft Entra application permissions (`API.ReadWrite.All`,
  application type) require **tenant-admin consent** in the customer's Entra tenant — an explicit customer-side
  administrative act.
- **Contractual/security approvals** that must exist (MSA/DPA/Order-Form/security-review) — referenced
  generically; the actual executed documents are governed-substrate objects, never recorded here.
- **Residency / retention / subprocessor** considerations for the customer's data leaving their Business
  Central environment (service geography, BareCount as processor/subprocessor).
- **Customer-side authorizer roles**: the Microsoft Entra administrator (app registration + admin consent), the
  Business Central administrator (Microsoft Entra Applications page entry + permission sets + environment/company
  scope), and the data/security approver for scope.

---

## 5. Commercial

General access-model and volume guidance (official/planning research; no tenant-specific commercial terms).

### 5.1 Customer access models

| Model | Path | Cost (Microsoft) | Volume suitability |
|---|---|---|---|
| **Business Central online — API v2.0** | Microsoft-operated SaaS, OAuth via Microsoft Entra | Included surface of the subscription; any usage/licensing consequence is a customer/Microsoft determination | Low–medium; row-level reads, delta by `$filter` + webhooks |
| **Business Central online — custom APIs** | Same service; customer-deployed AL API pages | AL development effort is a customer/partner determination | Same as API v2.0; extends entity coverage |
| **Business Central on-premises / container** | Customer-hosted; API surface enabled by the administrator | Licensing/hosting is a customer/Microsoft determination | Deployment-specific; ⧗ unresearched beyond endpoint shape |

Cost/permissibility per path is a **customer/Microsoft determination** verified against the governed authority
objects (§4.A), not a BareCount conclusion.

### 5.2 Volume considerations

| Scenario | Typical volume | Candidate model |
|---|---|---|
| Initial historical load | 1M–100M records | API v2.0 paged reads within the published operational limits (§6.3); pacing plan required |
| Daily delta admission | 1K–100K/day | `$filter` on last-modified timestamps (⧗ per-entity verification) |
| Realtime/near-realtime | 100–10K/hour | Webhook notifications as trigger + API reads |

---

## 6. Technical

### 6.A Platform Plane — Microsoft technical (general)

#### 6.1 Protocol

REST/JSON over **OData V4**. Online base path
`https://api.businesscentral.dynamics.com/v2.0/{tenantId or domain}/{environment}/api/v2.0/`, with business data
company-scoped as `/companies({companyId})/{resource}`
([API endpoints](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/endpoints-apis-for-dynamics)).
On-premises exposes `https://{host}:{port}/{serverInstance}/api/v2.0/` (disabled by default; administrator must
enable). Custom APIs mount at `/api/{publisher}/{group}/{version}/`. Standard OData query options apply
(`$filter`, `$top`, `$skip`, `$select`, `$expand`, `$orderby`, `$count`); `$batch` is supported (max 100
operations, §6.3). The API surface is updated monthly per the endpoints reference. An
[OpenAPI specification](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-open-api)
is published for the v2.0 surface.

#### 6.2 Authentication

**Business Central online: OAuth 2.0 / Microsoft Entra ID only.** Microsoft's documentation states that
**"Starting October, 2022, the use of access keys (Basic Auth) for web service authentication is deprecated and
not supported in Business Central online"**
([Web services authentication](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/web-services-authentication)).

The machine-access path is **service-to-service (S2S) authentication** via the OAuth 2.0 client-credentials
flow ([Using Service to Service Authentication](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/automation-apis-using-s2s-authentication)):
- Register a Microsoft Entra application; create a client secret (or certificate).
- Grant the **Dynamics 365 Business Central** API the **application** permission `API.ReadWrite.All` (APIs and
  web services); `Automation.ReadWrite.All` exists separately for automation APIs. Admin consent required.
- Token endpoint `https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/token`; scope
  `https://api.businesscentral.dynamics.com/.default`.
- In Business Central, the **Microsoft Entra Applications** page maps the app registration to an in-product
  identity with assigned permission sets. Per Microsoft: **"Applications can't be assigned the SUPER permission
  set"** — least-privilege permission sets are mandatory by product design.
- S2S is available online since v17/v18.3 and on-premises since 18.11/19.5 (with Entra OpenID Connect
  configuration and `ValidAudiences` including `https://api.businesscentral.dynamics.com`).

**On-premises differs**: deployments configured with `NavUserPassword` or `AccessControlService` credential
types still support username + web-service access key (Basic-auth-style) on API/OData endpoints — deployment
modes must never be conflated when authoring connection profiles.

Gap: no Microsoft Entra OAuth client-credentials helper exists in `CredentialResolverService` (§8; shared gap
with Dynamics 365 Finance & Operations).

#### 6.3 Throughput / operational limits (Business Central online — researched from the official limits page)

From [Operational limits for Business Central online](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/operational-limits-online)
(retrieved 2026-07-13; limits change — re-verify per realization):

| Limit | Value | Scope / behavior |
|---|---|---|
| Max concurrent OData V4 requests | 5 | Per user; excess queues, times out after 8 min → HTTP 503 |
| Max connections (processed + queued) | 100 | Per user; excess → HTTP 429 |
| Max request queue size | 95 | Per user; excess → HTTP 429 |
| Speed (rate) | 6,000 requests per 5-minute sliding window | Per user; excess → HTTP 429 (strictly enforced) |
| Legacy per-environment rate | Sandbox 300/min, Production 600/min | Superseded by per-user limits (historically advisory) |
| Max page size | 20,000 entities per request | Per environment; excess → HTTP 413 |
| Max `$batch` size | 100 operations | Per environment |
| Operation timeout | 8 minutes | Per request → HTTP 408, session canceled |
| Max request body size | 350 MB | Per environment |
| Max webhook subscriptions | 200 | Per environment |

Microsoft's FAQ on the same page confirms the limits **apply to application users (service principals) exactly
as to interactive users**, and names workload distribution across multiple users/service principals (e.g.
round-robin) as the official throughput strategy. Retry logic with cool-off on HTTP 429 is expected
([Working with API rate limits](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-rate-limits)).

#### 6.4 Delta strategy

- **`$filter` on last-modified timestamps.** API entities are described as carrying `lastModifiedDateTime`
  (prior research); the underlying tables carry `SystemModifiedAt` / "Last Modified DateTime" fields (verified
  on the G/L Entry table page) — ⧗ per-entity availability/filterability verification pending against the
  release-exact v2.0 resource reference.
- **Webhook subscriptions** ([Working with webhooks](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-subscriptions)):
  `POST /api/v2.0/subscriptions` with a mandatory `validationToken` handshake; subscriptions **expire after
  three days** unless renewed by `PATCH` (handshake again); notifications are aggregated with a default
  30-second delay and collapse to a `collection` notification above 1,000 changed records; failed deliveries
  are retried for 36 hours. Webhooks are a **delta trigger**, not a data channel — payloads reference the
  changed resource; the reader still performs the governed read.
- **Monthly API update cycle** (§6.1) means entity coverage/fields can move between minor versions.

#### 6.5 Schema discovery

Three official public surfaces, requiring no customer system: the OData **`$metadata`** document at the API
root (per-environment, per-version); Microsoft Learn's per-table **application reference** (e.g.
[Table "G/L Entry" (ID 17)](https://learn.microsoft.com/en-us/dynamics365/business-central/application/base-application/table/microsoft.finance.generalledger.ledger.g-l-entry),
[Table "Detailed Cust. Ledg. Entry" (ID 379)](https://learn.microsoft.com/en-us/dynamics365/business-central/application/base-application/table/microsoft.sales.receivables.detailed-cust.-ledg.-entry));
and the MIT-licensed AL source in [microsoft/BCApps](https://github.com/microsoft/BCApps). See
[catalog.md](catalog.md) for the seed footprint and its provisional-provenance status.

#### 6.6 Known semantics (design notes — verify per realization)

- **Signed amounts + dual debit/credit columns.** The G/L Entry table carries a signed `Amount` **and**
  separate `Debit Amount` / `Credit Amount` columns (plus additional-currency variants) — verified on the
  [G/L Entry application-reference page](https://learn.microsoft.com/en-us/dynamics365/business-central/application/base-application/table/microsoft.finance.generalledger.ledger.g-l-entry).
  Contrast SAP's unsigned amount + `SHKZG` indicator. See [contracts.md](contracts.md) for the candidate OC
  pattern.
- **Detailed ledger entries carry application state.** Customer/vendor ledger entries are complemented by
  detailed-ledger entries (e.g. [Detailed Cust. Ledg. Entry, Table 379](https://learn.microsoft.com/en-us/dynamics365/business-central/application/base-application/table/microsoft.sales.receivables.detailed-cust.-ledg.-entry):
  `Entry Type`, `Amount (LCY)`, application/unapplication fields) — payment application and remaining-amount
  state live at this layer, not on the header ledger entry. AR/AP metrics must name which layer they observe.
- **Dimensions model.** Global Dimension 1/2 + Shortcut Dimensions 3–8 + `Dimension Set ID` on ledger entries
  (fields verified on Table 17). Dimension *values and meanings* are per-customer configuration — never assumed
  platform-universal.
- **Posting groups.** Gen. Bus./Gen. Prod./VAT posting-group codes on entries steer account derivation;
  per-customer configuration semantics — verify per realization.
- **Document posting via codeunits.** Documents post through application posting routines (not direct table
  writes); ledger entries are the posted, immutable observation surface — ⧗ official-citation pin pending for
  this design note.

### 6.B Tenant Connection Plane — customer technical prerequisites (general)

What **any** Business Central customer must set up before a connection can be tested (general requirements; the
step-by-step execution runbook is §7, and concrete endpoints/accounts/results live only in the governed
substrate):
- **Customer-side setup**: a Microsoft Entra app registration with the `API.ReadWrite.All` application
  permission and **tenant-admin consent**; a corresponding entry on the Business Central **Microsoft Entra
  Applications** page, enabled.
- **Service identity & minimum permissions**: least-privilege, **read-only** permission sets scoped to exactly
  the objects in the agreed scope — applications **cannot** be assigned SUPER (product-enforced); exact minimum
  read-only permission-set composition per module ⧗ research pending.
- **Environment / company selection**: the target environment name (e.g. production vs sandbox) and the
  in-scope company IDs.
- **Endpoint / network**: the online API endpoint is public HTTPS (`api.businesscentral.dynamics.com`);
  customer-side egress/IP considerations per Microsoft's published service IP guidance; on-premises requires
  the administrator to expose the API through the firewall.
- **Connection-test & first-chain proof requirement**: token acquisition + `$metadata` reachability + list
  companies + one entity `$top=1` read must pass before reader activation; a first governed chain run
  (SO→CO→MS) is the acceptance bar.
- **Version/customization verification**: confirm the environment's base-application version (moving baseline,
  §4.A.5) and any per-tenant extensions (PTEs) or AppSource apps that alter or extend standard field semantics
  (see [catalog.md](catalog.md) — universality is version-scoped).

---

## 7. Onboarding Runbooks

Execution history of these runbooks is logged in [onboarding-log.md](onboarding-log.md). **No run has ever been
executed** — these are designed procedures, unvalidated.

### 7.1 Customer-side — API v2.0 (S2S) path

1. **Confirm subscription scope.** Active Business Central online subscription covering the modules/companies
   in scope.
2. **Register a Microsoft Entra application** in the customer tenant; grant the **Dynamics 365 Business
   Central** API the `API.ReadWrite.All` **application** permission; a tenant admin grants **admin consent**.
3. **Map the application in Business Central**: create the entry on the **Microsoft Entra Applications** page,
   set State = Enabled, and assign **least-privilege read-only permission sets** for the agreed scope (SUPER is
   not assignable to applications).
4. **Select environment and companies** in scope.
5. **Provision the credential via the approved secret-ingress mechanism (never person-to-person).** The
   customer submits the Entra client secret (or certificate) through the governed secret store, which returns a
   `credential_ref` + receipt. Hand BareCount only the **Entra tenant ID, application (client) ID, environment
   name, in-scope company IDs, and the `credential_ref`** — **never the raw secret.** No raw secret enters Git,
   a ticket, chat, email, the docket, or an audit artifact.

### 7.2 Customer-side — custom-API extension path (when standard entities do not cover the scope)

1. Develop/deploy the AL API pages (per-tenant extension or AppSource app) exposing the agreed objects.
2. The same S2S application and permission-set mapping covers custom APIs; extend the permission sets to the
   new objects only.
3. Record the custom API `{publisher}/{group}/{version}` coordinates in the connection scope.

### 7.3 BareCount-side

Per-tenant connection profile in `tbc_{slug}_dev`:

- `system_type_code: 'microsoft_d365_bc'`
- `entra_tenant_id`
- `environment` (e.g. `production`)
- `auth.method: 'oauth2_client_credentials_entra'` (⧗ method not yet implemented — §8)
- `auth.credential_ref` — reference to a secret provisioned via the governed secret-ingress mechanism (yielding
  the `credential_ref` + receipt). Raw secrets never enter the DB, Git, tickets, chat, email, the docket, or
  any audit artifact — only the `credential_ref`.
- `companies[]` — company IDs in scope.

Smoke test: acquire token → `GET /companies` → `$metadata` → one entity `$top=1` for one in-scope company —
before activating any reader.

---

## 8. Known Gaps

1. **No executor** for the BC REST v2.0 surface — the company-scoped path shape
   (`/companies({companyId})/{resource}`) differs from a flat OData root.
2. **Microsoft Entra OAuth client-credentials helper** in `CredentialResolverService` — not built (shared gap
   with Dynamics 365 Finance & Operations).
3. **Webhook subscriber** — three-day-expiry renewal loop, handshake, and `collection`-notification handling
   not built.
4. **Multi-principal scaling** — per-user limits (§6.3) mean high-volume tenants need workload distribution
   across multiple service principals; no distributor exists.
5. **Per-entity delta verification** — `lastModifiedDateTime` availability/filterability per v2.0 entity not
   verified against the release-exact resource reference.
6. **Full v2.0 entity inventory** — only the webhook-supported-resources list has been officially re-verified;
   the complete entity list (incl. `customerLedgerEntries`/`vendorLedgerEntries`/`itemLedgerEntries`/
   `trialBalances` from prior research) is ⧗ pending per-entity verification (see [catalog.md](catalog.md)).
7. **Minimum read-only permission set** per module — not yet researched to the object level (SUPER is
   product-blocked for applications; the least-privilege composition is ours to define and verify).
8. **Custom API discovery** — per-tenant AL extensions add API pages; the catalog must discover them per
   tenant.
9. **On-premises / container variant** — endpoint shape researched; auth and enablement runbook ⧗ unresearched
   beyond §6.2 notes.
10. **Monthly-update feature drift** — API surface updates monthly and majors land twice a year; the catalog
    must be re-verified per version (§4.A.5).
11. **No Microsoft admission-stance ADR** (SAP analogue: D384) — needed before any clearance decision can
    exist.

---

## 9. References

Retrieved 2026-07-13 unless noted; content digests ⧗ pending (G3 capability gate).

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../../governance/adrs/ADR-6cb4f3.md) |
| ADR — Source-System Docket structure (D526) | [ADR-8570d4](../../../governance/adrs/ADR-8570d4.md) |
| Predecessor flat page (restructured into this docket) | `microsoft-d365-bc.md` |
| Companion docket — SAP ECC (accepted exemplar) | [sap-ecc/index.md](../sap-ecc/index.md) |
| Companion source page — Dynamics 365 Finance & Operations | [microsoft-d365-fo.md](../microsoft-d365-fo.md) |
| API v2.0 reference (overview) | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/ |
| API endpoints (online + on-premises URL shapes) | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/endpoints-apis-for-dynamics |
| Service-to-service authentication (S2S, Entra Applications page, no-SUPER rule) | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/automation-apis-using-s2s-authentication |
| Web services authentication (online Basic-Auth removal; on-prem credential types) | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/web-services-authentication |
| Operational limits for Business Central online | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/operational-limits-online |
| Working with API rate limits | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-rate-limits |
| Working with webhooks (subscriptions) | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-subscriptions |
| Update cycles (two major waves/year + monthly minors) | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/update-rollout-timeline |
| Licensing in Business Central (license types; Licensing Guide download) | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/deployment/licensing |
| Dynamics 365 Licensing Guide (download link from the licensing page) | https://go.microsoft.com/fwlink/?LinkId=866544 |
| Microsoft APIs Terms of Use | https://learn.microsoft.com/en-us/legal/microsoft-apis/terms-of-use |
| Application reference — Table "G/L Entry" (ID 17) | https://learn.microsoft.com/en-us/dynamics365/business-central/application/base-application/table/microsoft.finance.generalledger.ledger.g-l-entry |
| Application reference — Table "Detailed Cust. Ledg. Entry" (ID 379) | https://learn.microsoft.com/en-us/dynamics365/business-central/application/base-application/table/microsoft.sales.receivables.detailed-cust.-ledg.-entry |
| microsoft/BCApps (MIT-licensed application source) | https://github.com/microsoft/BCApps |
| MicrosoftDocs/dynamics365smb-docs (CC-BY-4.0 + MIT docs source) | https://github.com/MicrosoftDocs/dynamics365smb-docs |
| OpenAPI specification for API v2.0 | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-open-api |

## 10. Changelog

- **2026-07-13** — authored `microsoft-d365-bc/` docket per **DEC-8570d4 (D526)**, restructuring the flat
  `microsoft-d365-bc.md` page into the docket shape (mirroring the accepted `sap-ecc/`
  exemplar). Re-verified core facts against official Microsoft sources (API v2.0 endpoint shapes, S2S
  client-credentials flow + `.default` scope + no-SUPER rule, online Basic-Auth removal since October 2022,
  current operational limits incl. per-user 6,000/5-min rate + 20,000 max page size, webhook 3-day
  expiry/36-hour retry, two release waves per year + monthly minors, BCApps MIT, docs-repo CC-BY-4.0+MIT,
  G/L Entry + Detailed Cust. Ledg. Entry application-reference pages). Facts from prior research lacking a
  version-exact official source (per-entity `lastModifiedDateTime`, full entity inventory, `$filter IN`
  operator, minimum permission sets) downgraded to ⧗ pending. `proof_status: designed`; no evidence of any
  kind exists.
