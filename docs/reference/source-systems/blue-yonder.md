---
uid: SRC-b4e2d8
slug: blue-yonder
title: "Blue Yonder"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: supply-chain
subdomain: blue-yonder
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://success.blueyonder.com
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/blue-yonder.md
---

# Blue Yonder

This page records BareCount's source-admission posture for Blue Yonder. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no Blue Yonder auth helper; no customer engagement; no Success Portal access.

---

## 2. Reader Flavor Binding

Empty list. Candidates: `blue-yonder-rest`, `blue-yonder-streaming`.

---

## 3. What BareCount Admits

### 3.1 Metadata

Item master (SKU definitions, product attributes, hierarchies, categories); location master (DCs, warehouses, stores, plants, supplier locations); network definitions (topology, lanes, routes, source-destination); calendar definitions (planning, fiscal, promotional, seasonal); organisational hierarchies (BUs, divisions, regions, planning groups); UOM definitions and conversions.

### 3.2 Business data — planning

Demand forecasts (statistical baseline, promotional uplift, consensus, accuracy); replenishment plans (orders, safety stock, reorder points, dynamic adjustments); supply plans (production schedules, procurement plans, capacity allocations); inventory positions (on-hand, in-transit, allocated, ATP); promotional plans (event definitions, demand impact, cannibalisation/halo effects).

### 3.3 Business data — execution

Warehouse orders (receipts, shipments, pick/pack/ship, wave plans); transportation plans (load plans, carrier assignments, route optimisation, freight costs); labour plans (workforce schedules, demand forecasts, productivity); order lifecycle (capture, fulfillment promises, orchestration events); returns (reverse logistics, dispositions).

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

| Surface | Use |
|---|---|
| REST APIs | Standard CRUD-style integration on planning + execution entities |
| Streaming APIs (2025+) | Real-time event streams |
| AI agent APIs (2025+) | Agentic invocation of Blue Yonder ML models |

### 6.2 Endpoints

Tenant-specific; provided via Success Portal during onboarding.

### 6.3 Auth

OAuth 2.0 client credentials issued by Blue Yonder during customer onboarding.

### 6.4 Pagination and incrementality

Standard offset/cursor pagination per resource. Incremental admission via `modified_since` filters where exposed; streaming surfaces provide push-based delta.

### 6.5 Rate limits

Not publicly documented. Per-tenant fair-use enforcement.

---

## 7. Customer-Side Onboarding

1. Customer engages Blue Yonder onboarding to grant BareCount access via the Success Portal or sandbox environment.
2. Customer provisions OAuth 2.0 credentials.
3. Customer scopes credentials to read-only modules.
4. Hand BareCount: tenant URL, OAuth credentials, list of modules in scope, Success Portal access (for documentation lookup).

---

## 8. BareCount-Side Onboarding

Connection profile: `system_type_code: 'blue_yonder'`; `tenant_url`; `auth.method: 'oauth2_blue_yonder'`; `auth.credential_ref`. Smoke test: a small list call against a planning entity once credentials are valid.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Blue Yonder REST executor**.
2. **OAuth 2.0 client credentials** auth.
3. **Streaming-API subscriber** for real-time delta.
4. **Success Portal access** — customer must grant this to BareCount; otherwise schema discovery is blocked.
5. **Public schema gap** — admission contract design is per-customer until BareCount has partnership status.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Blue Yonder Success Portal (gated) | https://success.blueyonder.com |
| Blue Yonder product | https://blueyonder.com/ |
| Predecessor — legacy v2 archive Blue Yonder reference | legacy-v2/reference/sources/blue-yonder.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
