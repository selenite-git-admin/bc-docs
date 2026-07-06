---
uid: SRC-f7b2d6
slug: freshsales
title: "Freshsales"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: crm
subdomain: freshworks
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developers.freshworks.com/crm/api/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/freshsales.md
---

# Freshsales

This page records BareCount's source-admission posture for Freshsales. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for Freshsales REST; no Freshworks OAuth 2.0 helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavor when scoped:

- `freshsales-rest` — REST API against either base URL pattern.
- `freshsales-webhook` — push notifications via workflow rules.

---

## 3. What BareCount Admits

### 3.1 Metadata

Contact, Account, Deal, and custom module field definitions via Settings APIs; picklist/dropdown option values; deal pipeline and stage configurations; territory definitions; sales activity type definitions; custom field schemas per entity.

### 3.2 Business data

| Domain | Entities |
|---|---|
| CRM core | Contacts, Accounts (Sales Accounts), Deals |
| CPQ | Products, Product Pricings, CPQ Documents (Quotes / Invoices) |
| Activities | Tasks, Appointments (Meetings), Notes, Sales Activities |
| Communication | Emails, Phone Calls (built-in phone) |
| Scoring | Freddy AI lead scores, deal insights (if enabled) |

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

### 6.1 Dual base URL pattern

| Account vintage | Base URL |
|---|---|
| New (Freshworks-unified) | `https://{bundle-alias}.myfreshworks.com/crm/sales/api/` |
| Legacy | `https://{domain}.freshsales.io/api/` |

The executor must take the base URL as connection-profile config and not hardcode either.

### 6.2 Auth

- **API key** (single-tenant): generated in Personal Settings → API Settings.
- **OAuth 2.0** (multi-tenant marketplace): authorization code flow.

### 6.3 Pagination and incrementality

List endpoints support `page` + `per_page` (max 100). Modified-since via `updated_at` filter parameter on search endpoints.

### 6.4 Webhooks

Configured via Workflow Automations. POST to BareCount endpoint; verification via shared secret in payload.

### 6.5 Rate limits

| Limit | Value |
|---|---|
| Paid editions | 400 req/min |
| Free | restricted (~50 req/min) |
| Throttle | HTTP 429 |

---

## 7. Customer-Side Onboarding

1. Customer determines account vintage (myfreshworks vs freshsales.io).
2. Customer creates API key (Personal Settings → API Settings) or authorises via OAuth marketplace flow.
3. Hand BareCount: base URL pattern, API key (or OAuth tokens).

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'freshsales'`
- `base_url` — explicitly captured (do not derive)
- `auth.method: 'api_key' | 'oauth2_freshworks'`
- `auth.credential_ref`

Smoke test: `GET /selector/owners` (returns the user list) confirms auth + base URL.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Freshsales REST executor** with explicit `base_url` config (no auto-detection).
2. **Auth method support** — both API key (header) and OAuth 2.0 bearer.
3. **Webhook receiver**.
4. **400 req/min throttle handling** with backoff.
5. **CPQ module discovery** — newer entity; admission contract may need to bind CPQ Documents conditionally.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Freshworks Developers | https://developers.freshworks.com/crm/api/ |
| API endpoints | https://developers.freshworks.com/crm/api/#endpoints |
| OAuth 2.0 | https://developers.freshworks.com/freshsales-suite/api/#oauth |
| Webhooks | https://crmsupport.freshworks.com/support/solutions/articles/50000003089 |
| Predecessor — legacy v2 archive Freshsales reference | legacy-v2/reference/sources/freshsales.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
