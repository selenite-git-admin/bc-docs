---
uid: SRC-a4c6e9
slug: zoho-books
title: "Zoho Books"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: accounting
subdomain: zoho
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.zoho.com/books/api/v3/introduction/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/zoho-books.md
---

# Zoho Books

This page records BareCount's source-admission posture for Zoho Books. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for Zoho Books REST API v3; no Zoho OAuth 2.0 helper with multi-region support; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `zoho-books-rest-v3` — primary integration surface.
- `zoho-books-webhook` — push notifications on entity changes.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of Accounts (account types, codes, parent accounts); tax configurations (GST rates, TDS/TCS groups, tax authorities, exemptions); currencies and exchange rates; organisation settings (fiscal year, base currency, time zone, industry); user and role definitions; item catalog (products and services, UOM, tax preferences); contact classifications (customer, vendor, individual, business); payment terms and templates.

### 3.2 Business data

Invoices (sales, recurring, retainer); Bills (vendor, recurring); Expenses (direct, recurring, mileage); Journal Entries (manual, opening balances); Payments (customer, vendor, refunds); Credit Notes and Debit Notes; Vendor Credits; Bank Transactions (deposits, transfers, categorised/uncategorised); Purchase Orders; Sales Orders; Estimates (quotes); Projects and Timesheets; Inventory (stock movements, item groups, composite items); GST returns (GSTR-1, GSTR-3B, GSTR-2B reconciliation — India edition).

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

### 6.1 Region-specific base URLs

| Region | Base URL |
|---|---|
| US | `https://www.zohoapis.com/books/v3/` |
| EU | `https://www.zohoapis.eu/books/v3/` |
| India | `https://www.zohoapis.in/books/v3/` |
| Australia | `https://www.zohoapis.com.au/books/v3/` |
| Japan | `https://www.zohoapis.jp/books/v3/` |
| Canada | `https://www.zohoapis.ca/books/v3/` |
| Saudi Arabia | `https://www.zohoapis.sa/books/v3/` |
| China | `https://www.zohoapis.com.cn/books/v3/` |

Every request requires `organization_id` query parameter. Obtain via `GET /organizations`.

### 6.2 Authentication

OAuth 2.0 authorization code flow:
1. Customer authorises via Zoho consent.
2. BareCount receives auth code → exchanges for access + refresh tokens.
3. Access token: 1 hour; refresh token: until revoked.
4. Token endpoint is **also region-specific** (e.g. `https://accounts.zoho.in/oauth/v2/token` for India).

### 6.3 Pagination and incrementality

Most list endpoints support `page` + `per_page` (max 200). Incremental admission via `last_modified_time` filter.

### 6.4 Webhooks

Workflow rules in Zoho Books can post to BareCount endpoints. Verification via signature in payload.

### 6.5 Rate limits

| Limit | Value |
|---|---|
| Daily | vendor-defined daily quota by organisation and plan |
| Per minute | 100 / min per organisation |
| Concurrent | No published limit |
| Throttle | HTTP 429 |

---

## 7. Customer-Side Onboarding

1. Customer clicks "Connect to BareCount" → redirected to Zoho consent (region-appropriate).
2. Customer authorises with required scopes (`ZohoBooks.invoices.READ`, `ZohoBooks.bills.READ`, etc.).
3. BareCount receives access + refresh tokens, calls `/organizations` to discover org IDs and region.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'zoho_books'`
- `region` — one of `us`, `eu`, `in`, `au`, `jp`, `ca`, `sa`, `cn`
- `organization_id`
- `auth.method: 'oauth2_zoho_authorization_code'`
- `auth.credential_ref`

Smoke test: `GET /organizations` (against the correct region), then list invoices for org.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Zoho OAuth 2.0 helper** with **per-region token + API endpoints**. Single most important Zoho-specific complexity.
2. **REST executor** with `organization_id` propagation and region-aware base URL.
3. **Webhook receiver** with signature verification.
4. **Daily-quota-aware admission scheduling** — Free / Standard plans cannot sustain high-frequency polling.
5. **GST returns module** (India) — admission contract for GSTR-1/3B/2B if needed for compliance use cases.
6. **Multi-org tenants** — when a customer has multiple Zoho organisations, the connection profile must enumerate them.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Zoho Books API v3 | https://www.zoho.com/books/api/v3/introduction/ |
| OAuth 2.0 | https://www.zoho.com/books/api/v3/oauth/ |
| Multi-DC | https://www.zoho.com/books/api/v3/multi-dc/ |
| Webhooks | https://www.zoho.com/books/help/webhooks.html |
| Predecessor — legacy v2 archive Zoho Books reference | legacy-v2/reference/sources/zoho-books.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
