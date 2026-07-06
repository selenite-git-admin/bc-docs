---
uid: SRC-a9d4e6
slug: razorpay
title: "Razorpay"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: payments
subdomain: razorpay
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://razorpay.com/docs/api/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/razorpay.md
---

# Razorpay

This page records BareCount's source-admission posture for Razorpay. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no Razorpay auth helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidates: `razorpay-rest-v1`, `razorpay-rest-v2-route`, `razorpay-webhook`.

---

## 3. What BareCount Admits

### 3.1 Metadata

Items (products / services configured for invoicing and subscriptions); Plans (subscription billing templates); Addons (one-time charges attached to subscriptions); Webhook event configurations; Virtual Account receiver configurations (bank account, VPA).

### 3.2 Business data

| Domain | Objects |
|---|---|
| Payment Gateway | Payments, Orders, Refunds, Disputes |
| Settlements | Settlements, Instant Settlements, Settlement Recon |
| Subscriptions | Subscriptions, Plans, Addons, Invoices (subscription-generated) |
| Invoicing | Invoices (standalone), Line Items |
| Route / Marketplace | Transfers, Linked Accounts, Reversals |
| RazorpayX (Business Banking) | Payouts, Contacts, Fund Accounts, Transactions, Payout Links |
| Smart Collect | Virtual Accounts, Virtual Account Payments |
| Customers | Customers, Tokens (saved payment methods) |

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

Base URL: `https://api.razorpay.com/v1/`. v2 namespace at `/v2/` (Route only).

### 6.2 Auth

HTTP Basic Authentication: `Authorization: Basic base64(KeyId:KeySecret)`. Test keys (`rzp_test_…`) and live keys (`rzp_live_…`).

### 6.3 Pagination and incrementality

`count` + `skip` (max count 100). Incremental admission via `from` and `to` Unix-timestamp filters on `created_at`.

### 6.4 Webhooks

Configurable per account. Signature verification via `X-Razorpay-Signature` header (HMAC-SHA256 of payload with the webhook secret).

### 6.5 Rate limits

Documented as vendor-defined request quota per account. HTTP 429 with `Retry-After`.

---

## 7. Customer-Side Onboarding

1. Customer creates an API Key in Razorpay Dashboard → Account & Settings → API Keys.
2. Customer assigns the key read-only role (where supported) or scopes via dedicated service-account user.
3. Customer optionally configures a webhook endpoint pointing to BareCount with a shared signing secret.
4. Hand BareCount: Key ID, Key Secret, account mode (test/live), webhook signing secret.

---

## 8. BareCount-Side Onboarding

Connection profile: `system_type_code: 'razorpay'`; `mode: 'test' | 'live'`; `auth.method: 'razorpay_basic'`; `auth.credential_ref`. Smoke test: `GET /v1/payments?count=1`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Razorpay REST executor** with Basic Auth + Unix-timestamp filter handling.
2. **Webhook receiver** with HMAC-SHA256 signature verification.
3. **RazorpayX vs gateway distinction** — RazorpayX (banking) and gateway are different product lines on the same account; canonical mapping must distinguish.
4. **Settlement recon** — admission contract for reconciling payments → settlements → bank deposits, especially across RBI Payment Aggregator settlement timelines.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Razorpay API documentation | https://razorpay.com/docs/api/ |
| Authentication | https://razorpay.com/docs/api/authentication/ |
| Webhooks | https://razorpay.com/docs/webhooks/ |
| Predecessor — legacy v2 archive Razorpay reference | legacy-v2/reference/sources/razorpay.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
