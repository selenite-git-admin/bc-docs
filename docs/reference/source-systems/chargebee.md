---
uid: SRC-b5e2f8
slug: chargebee
title: "Chargebee"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: payments
subdomain: chargebee
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://apidocs.chargebee.com/docs/api/getting-started
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/chargebee.md
---

# Chargebee

This page records BareCount's source-admission posture for Chargebee. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no Chargebee auth helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidates: `chargebee-rest-v2`, `chargebee-webhook`.

---

## 3. What BareCount Admits

### 3.1 Metadata (product catalog)

Items (plan-items, addon-items, charge-items); Item Prices (pricing variants per item); Item Families (product line groupings); Attached Items (addon/charge-to-plan attachment rules); Coupons; Coupon Codes; Features (feature flags / entitlements attached to plans); Configurations (site-level: currencies, tax, dunning); Business Entities (legal entities for multi-entity billing).

### 3.2 Business data

Subscriptions (state, trial, billing cycles, items, tiers, scheduled changes, advance invoicing); Invoices (line items, taxes, discounts, linked payments, dunning status, amounts due/paid/credited); Credit Notes; Transactions (payment + refund events, gateway references, linked invoices/credit notes); Customers (profiles, addresses, payment sources, auto-collection settings, promotional credits, tax exemptions); Orders (fulfillment records); Quotes; Events (audit trail).

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

### 6.1 Endpoints

Site-specific base URL: `https://<your-site>.chargebee.com/api/v2/`. Each Chargebee customer has a unique site domain.

### 6.2 Auth

HTTP Basic Authentication: `Authorization: Basic base64(api_key:)` (note the empty password — colon required). OAuth 2.0 for marketplace apps. Test sites and live sites have different keys.

### 6.3 TLS trust store

Verify the BareCount executor's HTTP client includes the DigiCert Global Root G2 certificate. Modern Node.js / OpenSSL trust stores include this by default (post-2020); if the executor uses an old or pinned trust store, update it.

### 6.4 Pagination and incrementality

`limit` (max 100) + `offset` cursor. Incremental admission via `updated_at[after]` filter (Unix timestamp).

### 6.5 Webhooks

Configurable per site. POST to BareCount endpoint with payload + Basic Auth header (using a webhook secret).

### 6.6 Rate limits

Documented as ~150 req/min default. HTTP 429 with `Retry-After`.

---

## 7. Customer-Side Onboarding

1. Customer creates a read-only API key in Chargebee Dashboard → Settings → API Keys.
2. Customer optionally configures a webhook endpoint with a Basic Auth secret pointing to BareCount.
3. Hand BareCount: site domain, API key, mode (test/live), webhook secret.

---

## 8. BareCount-Side Onboarding

Connection profile: `system_type_code: 'chargebee'`; `site_domain`; `mode: 'test' | 'live'`; `auth.method: 'chargebee_basic_apikey'`; `auth.credential_ref`. Smoke test: `GET /api/v2/customers?limit=1`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Chargebee REST executor** with site-specific base URL handling.
2. **DigiCert Global Root G2 trust store** — confirm BareCount's TLS configuration includes it.
3. **Webhook receiver** with Basic Auth verification.
4. **Subscription-to-revenue canonical mapping** — Chargebee Subscription, Invoice, Transaction, Credit Note must reconcile to BareCount canonical revenue/recognition objects.
5. **Multi-entity billing** — Chargebee Business Entities map to BareCount tenant or legal-entity dimension.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Chargebee API documentation | https://apidocs.chargebee.com/docs/api/getting-started |
| Authentication | https://apidocs.chargebee.com/docs/api/authentication |
| Webhooks | https://apidocs.chargebee.com/docs/api/events |
| TLS certificate change announcement | https://www.chargebee.com/docs/2.0/digicert-update.html |
| Predecessor — legacy v2 archive Chargebee reference | legacy-v2/reference/sources/chargebee.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
