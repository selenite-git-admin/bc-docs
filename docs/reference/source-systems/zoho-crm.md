---
uid: SRC-c4e8a2
slug: zoho-crm
title: "Zoho CRM"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: crm
subdomain: zoho
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.zoho.com/crm/developer/docs/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/zoho-crm.md
---

# Zoho CRM

This page records BareCount's source-admission posture for Zoho CRM. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for Zoho CRM REST API; no Zoho OAuth 2.0 helper with multi-region support (shared gap with Zoho Books); no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `zoho-crm-rest-v7` — primary integration surface.
- `zoho-crm-webhook` — push notifications via workflow rules.

---

## 3. What BareCount Admits

### 3.1 Metadata

Module definitions and field metadata via Settings API; custom module and custom field definitions (up to 500 custom fields/module on Ultimate); layout metadata, picklist values, role hierarchy; related lists and lookup field relationships; custom views (saved filters/list views).

### 3.2 Business data

| Domain | Modules |
|---|---|
| Sales | Leads, Contacts, Accounts, Deals |
| Marketing | Campaigns |
| Inventory | Products, Quotes, Sales Orders, Purchase Orders, Invoices, Vendors, Price Books |
| Support | Cases (Solutions) |
| Activities | Tasks, Events (Meetings), Calls |
| Custom | Any custom modules |

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

### 6.1 Region-specific base URLs (same 8 data centres as Zoho Books)

| Region | API base URL |
|---|---|
| US | `https://www.zohoapis.com/crm/v7/` |
| EU | `https://www.zohoapis.eu/crm/v7/` |
| India | `https://www.zohoapis.in/crm/v7/` |
| Australia | `https://www.zohoapis.com.au/crm/v7/` |
| Japan | `https://www.zohoapis.jp/crm/v7/` |
| Canada | `https://www.zohoapis.ca/crm/v7/` |
| Saudi Arabia | `https://www.zohoapis.sa/crm/v7/` |
| China | `https://www.zohoapis.com.cn/crm/v7/` |

OAuth token endpoint is also region-specific (`accounts.zoho.com`, `accounts.zoho.eu`, …).

### 6.2 Authentication

OAuth 2.0 authorization code flow:
1. Customer authorises via region-appropriate Zoho consent.
2. Exchange auth code for access + refresh tokens.
3. Access token: 1 hour; refresh token: until revoked.

### 6.3 Pagination and incrementality

Most list endpoints support `page` + `per_page` (max 200). Modified-since via `If-Modified-Since` header or `modified_time` query parameter.

### 6.4 Bulk Read API

Zoho CRM has a dedicated **Bulk Read API** for large historical loads — submit a job, poll, download CSV result. Useful for initial seeding when the per-call rate would exhaust credits.

### 6.5 Rate limits

| Limit | Value |
|---|---|
| Concurrent | 25 calls per user per organisation |
| Per minute | Plan-based (60–500/min) |
| Daily | API credit window — see §4 |
| Throttle | HTTP 429 |

---

## 7. Customer-Side Onboarding

1. Customer registers a Zoho API Console application (region-appropriate).
2. Configures scopes: `ZohoCRM.modules.ALL`, `ZohoCRM.settings.READ`, `ZohoCRM.bulk.READ`, etc.
3. OAuth consent flow → BareCount receives access + refresh tokens.
4. Discover org via `GET /org`.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'zoho_crm'`
- `region` — one of `us`, `eu`, `in`, `au`, `jp`, `ca`, `sa`, `cn`
- `org_id`
- `auth.method: 'oauth2_zoho_authorization_code'` (shared with Zoho Books)
- `auth.credential_ref`

Smoke test: `GET /org` (region-correct), then `GET /Leads?per_page=1`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Zoho OAuth 2.0 helper** with **per-region token + API endpoints** (shared gap with Zoho Books).
2. **REST executor** with `If-Modified-Since` and region-aware base URL.
3. **Bulk Read API path** for initial historical seeding.
4. **Webhook receiver** with signature verification.
5. **API credit budgeting** — admission contract should declare expected daily credit consumption vs the customer's edition limit.
6. **Custom module discovery** — Settings API auto-discovery per tenant.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Zoho CRM Developer | https://www.zoho.com/crm/developer/docs/ |
| API v7 reference | https://www.zoho.com/crm/developer/docs/api/v7/ |
| OAuth 2.0 | https://www.zoho.com/crm/developer/docs/api/v7/auth-request.html |
| Bulk Read API | https://www.zoho.com/crm/developer/docs/api/v7/bulk-read.html |
| API limits | https://www.zoho.com/crm/developer/docs/api/v7/api-limits.html |
| Predecessor — legacy v2 archive Zoho CRM reference | legacy-v2/reference/sources/zoho-crm.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
