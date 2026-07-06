---
uid: SRC-c7f1a3
slug: quickbooks-online
title: "QuickBooks Online"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: accounting
subdomain: intuit
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developer.intuit.com/app/developer/qbo/docs/get-started
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/quickbooks-online.md
---

# QuickBooks Online

This page records BareCount's source-admission posture for QuickBooks Online. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for QBO REST API; no Intuit OAuth 2.0 helper in `CredentialResolverService`; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `quickbooks-online-rest-v3` — Accounting API v3 against `/v3/company/{realmId}/`.
- `quickbooks-online-cdc` — Change Data Capture batch delta fetch since timestamp.
- `quickbooks-online-webhook` — Push notifications on entity changes.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of Accounts (Account); Classes (profit centre / cost centre); Departments / Locations; Tax Codes and Tax Rates; Payment Methods; Terms; Currencies (multi-currency); Preferences (accounting method, fiscal year); CompanyInfo.

### 3.2 Business data

| Domain | Entities |
|---|---|
| Sales transactions | Invoice, SalesReceipt, Estimate, CreditMemo, RefundReceipt, Payment |
| Expense transactions | Bill, BillPayment, Purchase, PurchaseOrder, VendorCredit |
| Banking | Deposit, Transfer |
| Journals | JournalEntry (manual GL adjustments) |
| Master | Customer, Vendor, Employee, Item (products/services) |
| Attachments | Attachable |
| Budget | Budget (Plus and Advanced tiers only) |
| Multi-currency | ExchangeRate |

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

### 6.1 Available APIs

| API | Purpose | Auth |
|---|---|---|
| Accounting API v3 | Core CRUD + query | OAuth 2.0 |
| Payments API | CC / ACH processing | OAuth 2.0 |
| Payroll API | Employee, pay run, compensation | OAuth 2.0 |
| Reports API | P&L, Balance Sheet | OAuth 2.0 |
| Webhooks | Push on entity changes | HMAC verification |
| Change Data Capture (CDC) | Batch delta since timestamp | OAuth 2.0 |

### 6.2 Endpoints

- Production: `https://quickbooks.api.intuit.com/v3/company/{realmId}/`
- Sandbox: `https://sandbox-quickbooks.api.intuit.com/v3/company/{realmId}/`

### 6.3 Authentication

OAuth 2.0 authorization code flow:
1. Customer authorises via Intuit's consent UI.
2. BareCount receives authorization code, exchanges for access + refresh tokens.
3. Access token: ~1 hour. Refresh token: 100 days.
4. Tokens scoped to `realmId` (the customer's QBO company).

### 6.4 Query language

QBO uses a subset of SQL-like syntax in URL-encoded `query` parameter:
```
GET /v3/company/{realmId}/query?query=SELECT * FROM Invoice WHERE TxnDate >= '2025-01-01' MAXRESULTS 100&minorversion=70
```

---

## 7. Customer-Side Onboarding

1. Customer clicks "Connect to BareCount" in BareCount UI → redirected to Intuit consent.
2. Customer authorises BareCount with required scopes.
3. BareCount stores the access + refresh tokens for the customer's `realmId`.
4. (Customer may need to upgrade to Plus or Advanced for classes/locations support.)

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'quickbooks_online'`
- `realm_id`
- `auth.method: 'oauth2_intuit_authorization_code'`
- `auth.credential_ref` — refresh token in external store

Smoke test: `GET /v3/company/{realmId}/companyinfo/{realmId}`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Intuit OAuth 2.0 helper** — authorization-code flow with redirect handling and refresh-token rotation.
2. **REST executor with QBO query syntax** — supports `WHERE`, `MAXRESULTS`, `STARTPOSITION` for pagination.
3. **CDC implementation** — alternative bulk-delta path independent of polling.
4. **Webhook receiver** with HMAC verification.
5. **App Partner Program tier strategy** — must monitor cumulative call volume across customers and plan tier upgrades before quota exhaustion.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Intuit Developer Portal | https://developer.intuit.com/app/developer/qbo/docs/get-started |
| Accounting API v3 reference | https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account |
| Intuit App Partner Program | https://developer.intuit.com/app/developer/qbo/docs/develop/intuit-app-partner-program |
| OAuth 2.0 setup | https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0 |
| Webhooks | https://developer.intuit.com/app/developer/qbo/docs/develop/webhooks |
| Predecessor — legacy v2 archive QBO reference | legacy-v2/reference/sources/quickbooks-online.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
