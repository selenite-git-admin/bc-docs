---
uid: SRC-e7f5a3
slug: siemens-opcenter
title: "Siemens Opcenter"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: mes
subdomain: siemens
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://plm.sw.siemens.com/en-US/opcenter/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/siemens-opcenter.md
---

# Siemens Opcenter

This page records BareCount's source-admission posture for Siemens Opcenter. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no Siemens auth helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Per-sub-product candidates:

- `siemens-opcenter-execution-rest`
- `siemens-opcenter-aps-rest`
- `siemens-opcenter-quality-rest`

Different sub-products have different schemas; per-product flavors are likely.

---

## 3. What BareCount Admits

### 3.1 Metadata

Product definitions (masters, versions, families, attributes); BOMs (engineering, manufacturing, revisions); BOPs (routings, operation sequences, standard times); work centres / equipment (model, types, groups, capacity); quality specifications (inspection plans, sampling plans, control limits).

### 3.2 Business data — production execution

Production orders (ID, product, quantities planned/completed/scrapped, status, dates, priority); operation tracking (status, actual vs planned duration, operator assignment, parameters); material consumption (lots consumed, quantities issued, traceability); genealogy (forward / backward, serial tracking, process parameter history).

### 3.3 Business data — quality and performance

Quality inspections (results, SPC data, NCRs, eBR pharma, eDHR medical devices); OEE metrics (availability, performance, quality per equipment / line / plant); downtime events (reason codes, duration, planned vs unplanned); throughput metrics (units per shift, FTR rates, yield, scrap).

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

REST + OData APIs per sub-product. Pharma sub-product has additional pharmaceutical-specific endpoints (batch records, eBR upload).

### 6.2 Auth

OAuth 2.0 issued via Siemens Xcelerator platform. Tenant-specific.

### 6.3 Pagination and incrementality

Standard offset / cursor with `modified_since` filters where exposed.

---

## 7. Customer-Side Onboarding

1. Customer enables API access in their Xcelerator tenant for BareCount.
2. Customer provisions OAuth 2.0 credentials.
3. Customer scopes credentials to read-only modules.
4. Hand BareCount: tenant URL, OAuth credentials, sub-products + modules in scope.

---

## 8. BareCount-Side Onboarding

Per-sub-product connection profile: `system_type_code: 'siemens_opcenter_execution' | 'siemens_opcenter_aps' | …`; `tenant_url`; `auth.method: 'oauth2_xcelerator'`; `auth.credential_ref`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Siemens Xcelerator OAuth 2.0** auth helper.
2. **Per-sub-product REST executors** — schemas differ.
3. **Pharma-specific endpoints** (eBR upload, Annexes) for life-sciences customers.
4. **Multi-sub-product admission** within a single Siemens customer.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Siemens Opcenter | https://plm.sw.siemens.com/en-US/opcenter/ |
| Siemens Xcelerator | https://www.sw.siemens.com/en-US/products/xcelerator/ |
| Predecessor — legacy v2 archive Siemens Opcenter reference | legacy-v2/reference/sources/siemens-opcenter.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
