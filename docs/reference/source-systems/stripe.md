---
uid: SRC-f3c8d1
slug: stripe
title: "Stripe"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: payments
subdomain: stripe
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://docs.stripe.com/api
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/stripe.md
---

# Stripe

This page records BareCount's source-admission posture for Stripe. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no Stripe auth helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidates: `stripe-rest-v1`, `stripe-webhook`, `stripe-cdc-events`.

---

## 3. What BareCount Admits

### 3.1 Metadata

Products (catalog items); Prices (pricing definitions); Coupons; Tax Rates; Plans (legacy, superseded by Prices); Webhook Endpoints.

### 3.2 Business data

Charges (completed payment attempts); PaymentIntents (lifecycle orchestration); Invoices (billing statements); Subscriptions (recurring billing agreements); Customers; Payouts (funds disbursement); Balance Transactions (ledger entries for all fund movements — the canonical financial record); Refunds; Disputes (chargebacks); Credit Notes.

**Balance Transactions** is the most authoritative financial source — it captures every fund movement (charge, refund, payout, fee, dispute) as a single ledger entry.

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

Base URL: `https://api.stripe.com/v1/`. (v2 namespace at `/v2/` for newer endpoints; both in the readiness baseline supported.)

### 6.2 Auth

- **Restricted Keys** (preferred for BareCount): scoped read-only key with explicit resource list.
- **Secret Key** (avoid): full account access; not suitable for read-only integrations.
- **OAuth 2.0** (Connect platforms): for marketplaces.

### 6.3 Pagination and incrementality

`limit` (max 100) + `starting_after` cursor. Incremental admission via `created` filter (`created[gte]=...`). For Balance Transactions, the executor walks `available_on` to align with payout cycles.

### 6.4 Webhooks

`POST /v1/webhook_endpoints` to subscribe. Signature verification via `Stripe-Signature` header (HMAC-SHA256). Events: `charge.succeeded`, `invoice.payment_succeeded`, `customer.subscription.created`, hundreds more.

### 6.5 API version pinning

Set an explicit `Stripe-Version` header on every request, using the version recorded in tenant onboarding evidence. The dashboard records each account's "default version"; the BareCount executor must override per call to ensure consistent behaviour.

### 6.6 Rate limits

100 read req/sec live mode (default); 25 read req/sec test mode. HTTP 429 with `Retry-After`. Live mode limits scale up on request.

---

## 7. Customer-Side Onboarding

1. Customer creates a **Restricted Key** in Dashboard → Developers → API Keys with read-only resource scopes (`charge:read`, `invoice:read`, `subscription:read`, etc.).
2. Customer optionally configures a webhook endpoint pointing to BareCount.
3. Hand BareCount: Restricted Key, account ID, optional webhook signing secret.

---

## 8. BareCount-Side Onboarding

Connection profile: `system_type_code: 'stripe'`; `account_id`; `auth.method: 'stripe_restricted_key' | 'oauth2_stripe_connect'`; `auth.credential_ref`; `api_version` (pinned). Smoke test: `GET /v1/balance` returns the account balance.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Stripe REST executor** with `Stripe-Version` pinning, cursor pagination, and Balance Transaction walk strategy.
2. **Restricted Key + OAuth Connect** auth methods.
3. **Webhook receiver** with HMAC-SHA256 signature verification.
4. **Balance Transaction canonical mapping** — Stripe's most-authoritative financial record; canonical layer should treat it as the source of truth over individual Charge records.
5. **Test-mode vs live-mode** discrimination in admission contract.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Stripe API documentation | https://docs.stripe.com/api |
| API versioning | https://docs.stripe.com/api/versioning |
| Restricted Keys | https://docs.stripe.com/keys |
| Webhooks | https://docs.stripe.com/webhooks |
| Predecessor — legacy v2 archive Stripe reference | legacy-v2/reference/sources/stripe.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
