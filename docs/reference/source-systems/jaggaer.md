---
uid: SRC-e1f5a7
slug: jaggaer
title: "Jaggaer"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: procurement
subdomain: jaggaer
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.jaggaer.com/solutions/integrations
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/jaggaer.md
---

# Jaggaer

This page records BareCount's source-admission posture for Jaggaer. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no Jaggaer auth helper; no customer engagement; no Jaggaer Professional Services partnership.

---

## 2. Reader Flavor Binding

Empty list. Candidates: `jaggaer-one-rest`, `jaggaer-aso-rest`.

---

## 3. What BareCount Admits

### 3.1 Metadata

Supplier master records, commodity / category taxonomy; contract templates and clause libraries; approval workflow definitions, catalog structures; organisation units and cost centres.

### 3.2 Business data

| Domain | Key objects |
|---|---|
| Requisitions | Purchase requisitions, line items, approvals |
| Purchase Orders | PO headers, line items, delivery schedules |
| Invoices | Headers, line items, 3-way match status |
| Sourcing Events | RFx, auctions, bid responses, award decisions |
| Contracts | Contract records, milestones, obligations |
| Supplier Assessments | Performance scorecards, risk ratings, qualification status |
| Spend Analytics | Classified spend records, category breakdowns |
| Inventory | Stock levels, reorder points, consumption history |

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

### 6.1 API surfaces

| Surface | Coverage |
|---|---|
| Jaggaer One REST | Core S2P entities (requisitions, POs, invoices, contracts, suppliers) |
| ASO REST | Advanced Sourcing Optimizer (sourcing events, bid analytics) |

### 6.2 Endpoints

Per-tenant URL: `https://<tenant>.app.jaggaer.com/api/`. ASO: `https://<tenant>.asoptimizer.com/api/` or per-customer subdomain.

### 6.3 Auth

OAuth 2.0 client credentials issued by Jaggaer during activation. Specifics documented in customer-portal docs once access is granted.

### 6.4 Pagination and incrementality

Standard offset-based pagination. Incremental admission via `modified_after` filter where exposed.

### 6.5 Rate limits

Not publicly published. Per-tenant fair-use; HTTP 429 expected.

---

## 7. Customer-Side Onboarding

1. Customer engages **Jaggaer Professional Services** to activate API access for their tenant. **This is a paid engagement** — not self-service.
2. Jaggaer issues OAuth 2.0 credentials.
3. Customer scopes credentials to read-only modules.
4. Hand BareCount: tenant URL, OAuth credentials, list of activated modules.

---

## 8. BareCount-Side Onboarding

Connection profile: `system_type_code: 'jaggaer'`; `tenant_url`; `auth.method: 'oauth2_jaggaer_client_credentials'`; `auth.credential_ref`. Smoke test: a small list call against the activated module.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Jaggaer REST executor** (Jaggaer One + ASO).
2. **OAuth 2.0 client credentials** auth.
3. **Customer-activation gate** — onboarding flow must surface the Professional Services engagement requirement.
4. **Public documentation gaps** — schemas only available after customer activation; admission contract design is per-customer until BareCount has partnership status.
5. **Jaggaer technology partnership** — pursue when customer count justifies; would streamline activation.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Jaggaer integrations overview | https://www.jaggaer.com/solutions/integrations |
| ASO API docs | https://asodocs.jaggaer.com/ |
| Predecessor — legacy v2 archive Jaggaer reference | legacy-v2/reference/sources/jaggaer.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
