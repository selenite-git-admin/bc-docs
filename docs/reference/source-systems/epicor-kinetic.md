---
uid: SRC-e4a71b
slug: epicor-kinetic
title: "Epicor Kinetic"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: enterprise-erp
subdomain: epicor
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.epicor.com/en-us/products/enterprise-resource-planning-erp/kinetic/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/epicor-kinetic.md
---

# Epicor Kinetic

This page records BareCount's source-admission posture for Epicor Kinetic. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for Epicor Kinetic REST or BAQ OData; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `epicor-kinetic-rest-v2` — REST API v2 OData against `Erp.BO.{Service}Svc` business objects.
- `epicor-kinetic-baq` — BAQ OData feed for cross-table customer-defined queries.

(Sub-flavors per domain — financial, order, production, inventory, entity — are runtime configuration of the same executor, not separate reader flavors at the platform layer.)

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of accounts (multi-book, multi-company); company / site / plant codes; currencies and exchange rate types; fiscal periods; UOM, payment terms, posting groups; user-defined (UD) columns and tables (`ShortChar01–10`, `Number01–20`, `Date01–20`, `CheckBox01–20`, `Character01–10`, `UD01–UD40`).

### 3.2 Business data

| Domain | Key business objects |
|---|---|
| Financials | `Erp.BO.GLJrnDtlSvc`, `Erp.BO.APInvoiceSvc`, `Erp.BO.ARInvoiceSvc`, `Erp.BO.PaymentSvc` |
| Orders | `Erp.BO.SalesOrderSvc`, `Erp.BO.POSvc`, `Erp.BO.QuoteSvc` |
| Production | `Erp.BO.JobEntrySvc`, `Erp.BO.MESSvc`, `Erp.BO.LaborSvc` |
| Inventory | `Erp.BO.PartSvc`, `Erp.BO.PartTranSvc`, `Erp.BO.WarehseSvc` |
| Entities | `Erp.BO.CustomerSvc`, `Erp.BO.VendorSvc`, `Erp.BO.EmpBasicSvc` |

`SysRevID` (SQL Server `rowversion`/`timestamp`) auto-increments on any row modification — reliable for delta detection without depending on user-maintained date fields.

---

## 4. Legal & Licensing

Vendor licensing, access-tier, rate-limit, pricing, and contractual terms are not maintained as static facts in v4.

During source onboarding, verify:

- customer entitlement for the selected API or interface
- whether a dedicated service identity requires a paid license
- whether read-only extraction is permitted under the customer contract
- rate-limit, concurrency, and data-egress constraints that affect reader scheduling

Record the verified terms in the onboarding evidence for that tenant and source. This page may name the admission stance, but it must not be treated as vendor-license advice.

---

## 5. Commercial

No static commercial estimate is maintained here.

Capture customer-specific subscription, add-on, service-account, API, connector, egress, partnership, or infrastructure costs during onboarding evidence review.

---

## 6. Technical

### 6.1 REST API v2 (primary)

| Aspect | Detail |
|---|---|
| Protocol | REST over HTTPS (JSON), OData-compliant |
| Base URL | `https://{server}/{instance}/api/v2/odata/{Company}/` |
| API Help | `https://{server}/{instance}/apps/resthelp/` (interactive Swagger explorer) |
| Namespaces | `Erp.BO.*`, `Erp.Lib.*`, `Erp.Proc.*` |
| Methods | OData (GET, POST, PATCH, DELETE) + RPC (custom methods per service) |
| Pagination | OData `$top`, `$skip` |
| Filtering | `$filter`, `$select`, `$expand`, `$orderby` |

API documentation is **deployment-specific** — there is no centralised public reference site. Each Epicor installation hosts its own interactive API Help page.

### 6.2 BAQ (Business Activity Queries)

| Aspect | Detail |
|---|---|
| Endpoint | `/api/v2/odata/{Company}/BaqSvc/{BAQName}` |
| Exposure | BAQs marked "Exposed to OData" in BAQ Designer |
| Updatable | UBAQs allow write-back through the API |
| Best for | Custom cross-table joins, customer-specific data shapes, complex reporting |

### 6.3 Service Connect (middleware)

Visual workflow designer, event-driven orchestration, scheduled jobs. Protocols: REST, SOAP, flat files, DB connectors, EDI. Customers can push data to BareCount via Service Connect workflows. May require separate licence.

### 6.4 BPM Directives (event-driven)

Server-side event hooks on business object methods (pre/post processing, data directives). Custom C# code blocks or Epicor Functions. Could push change events to BareCount webhooks.

### 6.5 Authentication

| Method | Description | BareCount fit |
|---|---|---|
| Basic + API Key | Username/password + API Key header | On-premise primary |
| Token-based (Bearer) | `POST {server}/Token` with `grant_type=password`; token has configurable expiry | Cloud primary (if no Entra) |
| OAuth 2.0 / Microsoft Entra | Kinetic 2022.1+ via Entra app registration; client credentials with secret or certificate | Cloud preferred for enterprise SSO |
| SAML SSO | For interactive users | Not for M2M |

### 6.6 Rate limits

Epicor does not publish specific public rate limit numbers. Limits are deployment-dependent: server-dependent concurrency; HTTP 429 when capacity exceeded; pagination via `$top`/`$skip` (recommend page size 100–500). Long-running queries may timeout — use BAQs for complex joins.

### 6.7 Multi-company / multi-site

Data is scoped to a `Company` identifier. Multi-site uses `Plant` codes within a company. API requests carry the company context in the URL path. BareCount admission contracts must specify company scope.

---

## 7. Customer-Side Onboarding

1. Confirm Kinetic edition (Cloud SaaS / on-premise / hybrid) and version.
2. Create a service account with read-only role for the modules in scope.
3. Generate an API Key (System Management → Security Management → API Keys).
4. Cloud: token endpoint credentials or Microsoft Entra ID app registration.
5. Configure network access (VPN or firewall rules for on-premise; egress IP allowlist for cloud).
6. Optionally create exposed BAQs for cross-table data shapes BareCount needs.
7. Hand BareCount: server URL, instance name, company code(s), service account credentials, API Key, list of exposed BAQs.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'epicor_kinetic'`
- `endpoint_url`
- `instance_name`
- `companies[]`
- `auth.method: 'basic_apikey' | 'bearer_token' | 'oauth2_entra_client_credentials'`
- `auth.credential_ref`

Smoke test: hit OData `$metadata`, then a small read against `Erp.BO.CompanySvc/Companies?$top=1`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Generic OData REST executor with multi-auth support** — Basic+APIKey, Bearer, and Entra OAuth all need to land.
2. **Per-deployment API discovery** — no centralised reference; the executor must walk `$metadata` per customer to learn the surface.
3. **BAQ auto-discovery** — list exposed BAQs and their schemas at admission contract design time.
4. **`SysRevID` delta strategy** vs. date-based delta — pick per entity.
5. **UD columns and UD tables** — customer-specific; the catalogue must auto-discover.
6. **On-premise variants** — older Kinetic deployments may have variant URL paths or auth idiosyncrasies; needs robust executor configuration.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Epicor Kinetic product page | https://www.epicor.com/en-us/products/enterprise-resource-planning-erp/kinetic/ |
| REST API Help | per-deployment at `https://{server}/{instance}/apps/resthelp/` |
| Epicor Cloud SDK | https://www.epicor.com/en-us/products/enterprise-resource-planning-erp/kinetic/cloud-business-platform/ptw-cloud-sdk/ |
| Epicor User Help Forum | https://www.epiusers.help/ |
| Predecessor — legacy v2 archive Epicor Kinetic reference | legacy-v2/reference/sources/epicor-kinetic.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
