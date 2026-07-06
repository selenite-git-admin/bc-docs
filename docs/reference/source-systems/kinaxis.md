---
uid: SRC-a7e3b1
slug: kinaxis
title: "Kinaxis Maestro"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: supply-chain
subdomain: kinaxis
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.kinaxis.com/en/developer-studio
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/kinaxis.md
---

# Kinaxis Maestro

This page records BareCount's source-admission posture for Kinaxis Maestro. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no Kinaxis auth helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate: `kinaxis-maestro-rest` — REST API via Developer Studio.

---

## 3. What BareCount Admits

### 3.1 Metadata

Part Master (item/SKU); BOM (multi-level structures, effectivity dates); resources (machines, work centres, labour); calendars (production, shipping, supplier lead-time); sites/locations; routing; suppliers; customers.

### 3.2 Business data

| Domain | Objects |
|---|---|
| Demand Planning | Demand forecasts, statistical/consensus, accuracy metrics, demand-sensing signals |
| Supply Planning | Supply plans, planned orders, requisitions, work orders, transfers |
| Inventory | On-hand, in-transit, on-order, safety stock, projections, aging |
| Capacity Planning | Capacity plans, resource utilisation, constraint profiles |
| Order Management | Sales orders, ATP/CTP commitments, allocations, fulfillment, OTIF |
| S&OP / IBP | S&OP plans, scenario comparisons, financial reconciliation, KPI snapshots |
| MPS | MPS plans, firm planned orders, schedule adherence |
| Scenarios | What-if scenario snapshots (digital twins) |

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

Tenant-specific: `https://<tenant>.kinaxis.com/api/`. Resource-oriented REST.

### 6.2 Auth

OAuth 2.0 client credentials via Maestro Developer Studio. Bearer JWT.

### 6.3 Pagination and incrementality

Standard offset/limit. Incremental admission via `modified_since` filter where exposed.

### 6.4 Worksheet-driven model

Maestro is built around **worksheets** — saved queries against the in-memory data model. Many integrations admit data via worksheet exports (configurable per customer) rather than direct entity reads.

---

## 7. Customer-Side Onboarding

1. Customer enables Developer Studio access for BareCount.
2. Generates OAuth 2.0 client credentials.
3. Builds worksheets for the data shapes BareCount needs (or identifies existing ones).
4. Hand BareCount: tenant URL, OAuth credentials, worksheet IDs.

---

## 8. BareCount-Side Onboarding

Connection profile: `system_type_code: 'kinaxis_maestro'`; `tenant_url`; `auth.method: 'oauth2_kinaxis'`; `auth.credential_ref`; `worksheet_ids[]`. Smoke test: call a small worksheet.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Kinaxis OAuth 2.0 helper**.
2. **Kinaxis REST executor** with worksheet-driven query model.
3. **Worksheet auto-discovery** — admission contract design depends on which worksheets exist per tenant.
4. **Scenario / what-if data semantics** — digital-twin observations need careful canonical mapping (the same SKU may appear in many scenarios with different projected values).

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Kinaxis Developer Studio | https://www.kinaxis.com/en/developer-studio |
| Kinaxis Maestro product | https://www.kinaxis.com/en/products/maestro |
| Predecessor — legacy v2 archive Kinaxis reference | legacy-v2/reference/sources/kinaxis.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
