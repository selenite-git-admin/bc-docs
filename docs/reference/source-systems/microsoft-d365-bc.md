---
uid: SRC-e4a7b2
slug: microsoft-d365-bc
title: "Microsoft Dynamics 365 Business Central"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: enterprise-erp
subdomain: microsoft
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/microsoft-d365-bc.md
---

# Microsoft Dynamics 365 Business Central

This page records BareCount's source-admission posture for Microsoft Dynamics 365 Business Central. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for the BC REST v2.0 surface; no Microsoft Entra OAuth helper in `CredentialResolverService` (shared gap with D365 F&O); no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `microsoft-d365-bc-rest-v2` — Standard REST API v2.0 against `/v2.0/{tenantId}/{environment}/api/v2.0/`.
- `microsoft-d365-bc-custom-api` — Customer-developed API pages in AL (Application Language) for extension-specific entities or fields.
- `microsoft-d365-bc-webhook` — Push notifications via Subscription API for near-realtime delta detection.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of Accounts (Table 15 → API `accounts`); company information (`companyInformation`); dimensions (Table 348/349); currencies (Table 4/330 → `currencies`); posting groups (Tables 92–95, 252, 325); units of measure; payment terms; payment methods; countries / regions.

### 3.2 Business data

| Resource | Description |
|---|---|
| `generalLedgerEntries` | Primary financial observation — every posted transaction |
| `customerLedgerEntries` | AR aging, payment application, open receivables |
| `vendorLedgerEntries` | AP aging, payment application, open payables |
| `itemLedgerEntries` | Inventory movement, cost of goods, stock valuation |
| `salesInvoices` / `salesCreditMemos` | Revenue recognition, customer billing, returns |
| `purchaseInvoices` | Cost recognition, vendor billing |
| `salesOrders` | Open order book, demand observation |
| `trialBalances` / `incomeStatements` / `cashFlowStatement` | Period-end financial position |
| `customers` / `vendors` / `items` | Master data |

All entities expose `lastModifiedDateTime` for delta detection.

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

### 6.1 Standard REST API v2.0 (primary)

| Aspect | Detail |
|---|---|
| Endpoint pattern | `https://api.businesscentral.dynamics.com/v2.0/{tenantId}/{environment}/api/v2.0/companies({companyId})/{resource}` |
| Auth | OAuth 2.0 Client Credentials via Microsoft Entra ID |
| Pagination | OData `$top`, `$skip` |
| Filtering | `$filter` (with `IN` operator), `$expand`, `$select`, `$orderby`, `$count` |
| Batch | `$batch` supported (max 100 operations per batch) |

API v2.0 is current; Microsoft continues adding entities and fields. The `IN` operator supports multi-value filter (e.g. `$filter=status in ('Open','Released')`).

### 6.2 Custom APIs (AL)

Customer-developed API pages in AL. Endpoint: `/api/v2.0/.../api/{publisher}/{group}/{version}/`. Use to expose customer-specific extensions or extended fields.

### 6.3 Webhooks

Subscription API: `POST /api/v2.0/subscriptions`. 36-hour retry window. Subscription expires after **3 days** if not renewed. Push notifications on entity changes.

### 6.4 Authentication

OAuth 2.0 Client Credentials via Microsoft Entra ID:

1. Register app in Microsoft Entra ID.
2. Grant `API.ReadWrite.All` permission (or a narrower custom scope).
3. In Business Central → **Microsoft Entra Applications** page → create entry for the registered app.
4. Assign a permission set (e.g. `D365 AUTOMATION`, `D365 FULL ACCESS`, or a custom read-only set).
5. Provide BareCount: Tenant ID, Client ID, Client Secret, Environment name.

Basic Authentication is **deprecated** and disabled by default in new environments. Do not use.

### 6.5 Rate limits

| Limit | Value | Scope |
|---|---|---|
| Concurrent requests | 5 | Per user / per app |
| Max simultaneous connections | 100 | Per user / per app |
| Rate limit | vendor-defined sliding-window quota | Per user / per app |
| Production env rate | ~600 req/min | Per environment |
| Sandbox env rate | ~300 req/min | Per environment |
| Request timeout | vendor-defined request timeout | Per request |
| Max response size | vendor-defined OData page-size limit | Per request |
| Webhook subscription lifetime | 3 days (renewable) | Per subscription |
| Throttle response | HTTP 429 | — |

Scaling strategy: distribute admission workloads across multiple Microsoft Entra application registrations. Each app registration carries its own vendor-defined quota.

### 6.6 Key entities (BareCount priority)

`generalLedgerEntries`, `customers`, `vendors`, `items`, `salesInvoices`, `purchaseInvoices`, `accounts`, `trialBalances`, `salesOrders`, `itemLedgerEntries`. Detail in the `v2 reference page` §5 (full field-level schema).

---

## 7. Customer-Side Onboarding

1. Register a new application in Microsoft Entra ID (Azure portal).
2. Grant `API.ReadWrite.All` (or narrower custom scope).
3. In Business Central, navigate to **Microsoft Entra Applications** and create an entry for the registered app.
4. Assign a permission set scoped to read-only across the modules in scope.
5. Hand BareCount: Tenant ID, Client ID, Client Secret, Environment name (e.g. `production`), company GUIDs.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'microsoft_d365_bc'`
- `tenant_id`
- `environment` (e.g. `production`)
- `auth.method: 'oauth2_entra_client_credentials'` (shared with D365 F&O)
- `auth.credential_ref`
- `companies[]` — company GUIDs in scope

Smoke test: list companies (`/api/v2.0/companies`), then list one resource for one company (`/companies({id})/accounts?$top=1`).

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Microsoft Entra OAuth helper** — same gap as D365 F&O.
2. **REST executor with BC's company-scoped path shape** — `/companies({companyId})/{resource}` differs from a flat OData root.
3. **Webhook subscriber** — Subscription renewal logic for the 3-day expiry.
4. **Multi-app scaling** — for high-volume tenants, the integration may need multiple Entra app registrations and a request distributor.
5. **Custom API discovery** — AL extensions add API pages; the catalogue must auto-discover per tenant.
6. **Multiplexing licence advisory** — needs documented checklist for customers reading the Microsoft licensing rule.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| API v2.0 Reference | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/ |
| API Endpoints | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/endpoints-apis-for-dynamics |
| API Rate Limits | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-current-limits |
| Operational Limits | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/operational-limits-online |
| OData Web Services | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/odata-web-services |
| Webhooks | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-subscriptions |
| Licensing Guide | https://www.microsoft.com/content/dam/microsoft/final/en-us/microsoft-brand/documents/Dynamics-365-Licensing-Guide-January-2025.pdf |
| Predecessor — legacy v2 archive D365 BC reference | legacy-v2/reference/sources/microsoft-d365-bc.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
