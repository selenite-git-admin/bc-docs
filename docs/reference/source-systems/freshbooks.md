---
uid: SRC-e8a3d7
slug: freshbooks
title: "FreshBooks"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: accounting
subdomain: freshbooks
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.freshbooks.com/api/start
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/freshbooks.md
---

# FreshBooks

This page records BareCount's source-admission posture for FreshBooks. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for FreshBooks REST API; no FreshBooks OAuth 2.0 helper with rotation persistence; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `freshbooks-accounting-rest` — Invoices, expenses, payments, clients, taxes, items.
- `freshbooks-projects-rest` — Projects, services, project assignments.
- `freshbooks-time-rest` — Time entries.
- `freshbooks-webhook` — Push notifications on entity changes.

---

## 3. What BareCount Admits

### 3.1 Metadata

Expense Categories; Tax Codes; Currencies (`currency_code` on records); Payment Methods; Items (reusable line items); Services (billable definitions linked to projects); Tasks (invoice-facing service representation); System Info (`account_id`, `business_id`, role memberships).

### 3.2 Business data

Invoices; Expenses; Payments; Clients; Projects; Time Entries; Estimates (quotes/proposals); Credit Notes; Bills (beta); Bill Payments (beta); Journal Entries (manual accounting entries with debit/credit lines).

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

Base URL: `https://api.freshbooks.com`. Endpoints follow `/{resource_group}/{resource}/{account_or_business_id}/{...}` pattern.

### 6.2 Dual identity model

| Identifier | Used by |
|---|---|
| `account_id` | Older "classic" endpoints (e.g. `/accounting/account/{accountId}/...`) |
| `business_id` | Newer endpoints (e.g. `/projects/business/{businessId}/...`, `/timetracking/business/{businessId}/...`) |

Discovery: `GET /auth/api/v1/users/me` returns the user's businesses and accounts.

### 6.3 Authentication

OAuth 2.0 authorization code flow:
1. Customer authorises via FreshBooks consent.
2. Exchange auth code for access + refresh tokens.
3. **Strict rotation**: each refresh issues a new refresh token; previous becomes invalid. **Must persist immediately.**
4. Access token: 12 hours; refresh token: configurable lifetime.

### 6.4 Webhooks

| Aspect | Detail |
|---|---|
| Subscription | `POST /events/business/{businessId}/callbacks` |
| Verification | Verification token in callback payload |
| Events | `invoice.create`, `invoice.update`, `payment.create`, `expense.create`, etc. |

### 6.5 Rate limits

Daily call limits per account; HTTP 429 with `Retry-After`. No published explicit minute-level limits.

---

## 7. Customer-Side Onboarding

1. Customer clicks "Connect to BareCount" → redirected to FreshBooks consent.
2. Customer authorises with required scopes (`user:profile:read`, `user:invoices:read`, etc.).
3. BareCount receives access + refresh tokens, discovers `account_id`/`business_id`.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'freshbooks'`
- `account_id` and `business_id` (both)
- `auth.method: 'oauth2_freshbooks_authorization_code'`
- `auth.credential_ref` — **refresh-token rotation persisted on every exchange**

Smoke test: `GET /auth/api/v1/users/me` then list invoices for the business.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **FreshBooks OAuth 2.0 helper** with **transactional refresh-token rotation persistence** (must persist new token before doing anything else; failure = customer re-authorisation).
2. **REST executor** routing per-resource between `account_id` and `business_id` paths.
3. **Webhook receiver** with verification token check.
4. **Beta-endpoint policy** — admission contracts using Bills / Bill Vendors should be marked provisional and re-verified periodically.
5. **Rate-limit handling** — `Retry-After` honour with backoff.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| FreshBooks Developer | https://www.freshbooks.com/api/start |
| API documentation | https://www.freshbooks.com/api |
| OAuth 2.0 | https://www.freshbooks.com/api/authentication |
| Webhooks | https://www.freshbooks.com/api/events |
| Predecessor — legacy v2 archive FreshBooks reference | legacy-v2/reference/sources/freshbooks.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
