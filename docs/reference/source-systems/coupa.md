---
uid: SRC-d9e4f2
slug: coupa
title: "Coupa"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: procurement
subdomain: coupa
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://compass.coupa.com/en-us/products/product-documentation/integration-technical-documentation/the-coupa-core-api
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/coupa.md
---

# Coupa

This page records BareCount's source-admission posture for Coupa. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no Coupa OAuth/OIDC helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidates: `coupa-core-rest`, `coupa-sftp-flat-file`.

---

## 3. What BareCount Admits

### 3.1 Metadata

Suppliers, Chart of Accounts, Departments, Content Groups; lookup values, commodities, items, currencies, exchange rates; payment terms, users, addresses, units of measure.

### 3.2 Business data

Requisitions, Purchase Orders, Invoices, Receipts, Contracts, Expense Reports, Payments (Coupa Pay), Approvals, Sourcing Events.

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

### 6.1 Endpoint

Base URL: `https://<tenant>.coupahost.com/api/`.

### 6.2 Auth

OIDC OAuth 2.0 with client credentials. Token endpoint: `<tenant>.coupahost.com/oauth2/token`. Bearer JWT in `Authorization` header.

### 6.3 Pagination and incrementality

Offset-based: `offset` + `limit` (max 50/page). Incremental admission via `updated-at[gt]` filter on supported resources.

### 6.4 sFTP flat files

For very large historical loads, Coupa supports CSV exports to sFTP — useful for initial seeding when the 25 req/sec rate would cap throughput.

---

## 7. Customer-Side Onboarding

1. Customer registers an OAuth 2.0 client in Coupa Admin → Integrations → OAuth 2.0 / OIDC Clients.
2. Configures scopes (read-only across the modules in scope).
3. Creates a service-account user (BareCount integrator).
4. Hand BareCount: tenant URL, client ID, client secret, scopes.

---

## 8. BareCount-Side Onboarding

Connection profile: `system_type_code: 'coupa'`; `tenant_url`; `auth.method: 'oauth2_coupa_oidc'`; `auth.credential_ref`. Smoke test: `GET /api/users/current`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Coupa OIDC OAuth 2.0 helper**.
2. **Coupa REST executor** with offset pagination (50/page) and rate-limit awareness.
3. **sFTP flat-file ingest** for bulk historical loads.
4. **Legacy API key migration** — confirm no executor code references API key path.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Coupa Core API documentation | https://compass.coupa.com/en-us/products/product-documentation/integration-technical-documentation/the-coupa-core-api |
| Coupa OAuth 2.0 / OIDC | https://compass.coupa.com/en-us/products/product-documentation/integration-technical-documentation/oauth |
| Predecessor — legacy v2 archive Coupa reference | legacy-v2/reference/sources/coupa.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
