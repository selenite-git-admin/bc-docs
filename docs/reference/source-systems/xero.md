---
uid: SRC-d2b9c5
slug: xero
title: "Xero"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: accounting
subdomain: xero
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developer.xero.com/documentation/api/accounting/overview
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/xero.md
---

# Xero

This page records BareCount's source-admission posture for Xero. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for the Xero Accounting API; no Xero OAuth 2.0 helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `xero-accounting-api` — Accounting API endpoints (Invoices, BankTransactions, ManualJournals, Payments, etc.).
- `xero-journals-api` — Journals endpoint (Advanced developer tier; pre-aggregated GL postings).
- `xero-webhook` — Push notifications on entity changes.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of Accounts (codes, types, classes, tax types, bank account details); Tracking Categories (cost centres, departments — Xero's dimensional tagging); Tax Rates; Currencies; Organisation settings; Branding Themes; Contact Groups; Items.

### 3.2 Business data

Invoices (`ACCREC` sales invoices, `ACCPAY` bills, line items, taxes, payments applied); Bank Transactions (spend/receive money — coded bank lines); Manual Journals (GL with debit/credit lines); Payments (invoice, bill, batch); Credit Notes (customer + supplier, allocations); Bank Transfers; Overpayments and Prepayments; Purchase Orders; Quotes; Repeating Invoices; Journals (system-generated GL postings — read-only, Advanced tier); Contacts (customers, suppliers, addresses, tax numbers); Fixed Assets; Payroll (region-specific); Reports (Trial Balance, P&L, Balance Sheet, Aged Receivables/Payables, BAS/GST).

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

### 6.1 OAuth 2.0

Authorization code flow:
1. Customer redirected to Xero consent UI.
2. BareCount receives auth code → exchanges for access + refresh tokens.
3. Token windows and refresh-token rotation are vendor-defined and must be verified during onboarding.
4. Tokens scoped to one or more Xero **tenants** (organisations).

### 6.2 Endpoints

| API | Base URL |
|---|---|
| Accounting | `https://api.xero.com/api.xro/2.0/` |
| Assets | `https://api.xero.com/assets.xro/1.0/` |
| Payroll AU | `https://api.xero.com/payroll.xro/1.0/` |
| Projects | `https://api.xero.com/projects.xro/2.0/` |
| Files | `https://api.xero.com/files.xro/1.0/` |

All requests include `Xero-Tenant-Id` header.

### 6.3 Pagination and incrementality

Most endpoints support `If-Modified-Since` header for incremental admission. Pagination via `page` parameter (vendor-defined page size).

### 6.4 Rate limits

| Limit | Value |
|---|---|
| Daily | vendor-defined call limit per tenant |
| Per minute | 60 calls per tenant |
| Concurrent | 5 calls per app |
| Throttle response | HTTP 429 with `Retry-After` header |

---

## 7. Customer-Side Onboarding

1. Customer clicks "Connect to BareCount" → redirected to Xero consent.
2. Customer authorises BareCount with required scopes (`accounting.transactions.read`, `accounting.contacts.read`, etc.).
3. BareCount receives access + refresh tokens scoped to selected tenant(s).

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'xero'`
- `tenant_id` (one or more)
- `auth.method: 'oauth2_xero_authorization_code'`
- `auth.credential_ref` — refresh token in external store; **must rotate** on every refresh

Smoke test: `GET /api.xro/2.0/Organisation` to confirm tenant access.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Xero OAuth 2.0 helper** — authorization-code with single-use refresh-token rotation.
2. **REST executor with `If-Modified-Since` and `Xero-Tenant-Id`**.
3. **Webhook receiver**.
4. **Developer Platform tier strategy** — monitor connection count + data egress; plan tier upgrades.
5. **Accounting Activities API decommission (Apr 6 2026)** — verify no executor code references this; use Accounting endpoints + Journals (Advanced tier) instead.
6. **AI/ML use prohibition** — admission contract template should reference this explicitly.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Xero Developer | https://developer.xero.com/ |
| Accounting API overview | https://developer.xero.com/documentation/api/accounting/overview |
| Journals endpoint | https://developer.xero.com/documentation/api/accounting/journals |
| OAuth 2.0 | https://developer.xero.com/documentation/guides/oauth2/overview/ |
| Rate limits | https://developer.xero.com/documentation/guides/oauth2/limits/ |
| Predecessor — legacy v2 archive Xero reference | legacy-v2/reference/sources/xero.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
