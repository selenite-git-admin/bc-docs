---
uid: SRC-f8a6b4
slug: aveva-mes
title: "AVEVA MES"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: mes
subdomain: aveva
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://docs.aveva.com/category/manufacturing-execution-system
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/aveva-mes.md
---

# AVEVA MES

This page records BareCount's source-admission posture for AVEVA MES. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no AVEVA auth helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidates:

- `aveva-mes-web-api` — REST Web API (on-prem and cloud).
- `aveva-connect-data-services` — cloud bridge via AVEVA CONNECT.

---

## 3. What BareCount Admits

### 3.1 Metadata

Equipment model (classes, instances, hierarchies — ISA-95 aligned, properties, capabilities); material definitions (classes, definitions, lots, sublots, properties, UOM); personnel model (classes / roles, person instances, qualifications, certifications); process segments (definitions, parameters, dependencies, resource requirements); BOM (product specs, material requirements per process segment).

### 3.2 Business data — production

Work orders / job orders (ID, product, quantity, priority, scheduled / actual dates, status, requirements); production records (who/what/when/where/why/how-much per step); material lot tracking (raw, WIP, finished goods, genealogy); inventory movements (transfers, consumption, output, shipments).

### 3.3 Business data — quality and performance

Quality sample plans and test results (sample measurements, pass/fail, SPC rule violations); SPC data (X-bar/range, individual/moving range, attribute charts P/U/Np/C/DPMO); OEE metrics (availability, performance, quality); downtime events (planned vs unplanned, reason codes, changeover).

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

### 6.1 Web API

| Aspect | Detail |
|---|---|
| Surface | REST endpoints |
| Format | JSON |
| Coverage | Full MES (production, quality, materials, OEE) |
| Quality SPC endpoints | Added in recent releases |

### 6.2 AVEVA CONNECT (cloud)

OAuth 2.0-based access to cloud-published data services. Integration pattern: CONNECT data services egress to BareCount endpoint, or BareCount pulls via REST.

### 6.3 OPC-UA edge

For real-time machine data, AVEVA MES connects to OPC-UA equipment. BareCount admission goes through the Web API, not direct OPC-UA.

### 6.4 Auth

| Deployment | Auth |
|---|---|
| On-prem Web API | Token-based (AVEVA-issued); HTTP Basic with service account |
| AVEVA CONNECT (cloud) | OAuth 2.0 |

### 6.5 Pagination and incrementality

Standard offset / cursor pagination per resource; incremental admission via `modified_since`.

---

## 7. Customer-Side Onboarding

1. Customer determines deployment (on-prem AVEVA MES vs AVEVA CONNECT cloud).
2. Customer provisions credentials per deployment.
3. Customer scopes credentials to read-only.
4. For cloud: register BareCount as an AVEVA CONNECT integration; receive OAuth credentials.
5. Hand BareCount: endpoint URL, credentials, modules in scope.

---

## 8. BareCount-Side Onboarding

Per-deployment connection profile: `system_type_code: 'aveva_mes' | 'aveva_connect'`; `endpoint_url`; `auth.method: 'aveva_basic' | 'oauth2_aveva_connect'`; `auth.credential_ref`. Smoke test: list a small number of equipment definitions.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **AVEVA Web API REST executor** with token-based / Basic auth.
2. **AVEVA CONNECT OAuth 2.0** for cloud customers.
3. **OPC-UA out of scope** — admission is via Web API only.
4. **Hybrid cloud / on-prem connection profile** — model must accommodate both deployments under one customer.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| AVEVA MES documentation | https://docs.aveva.com/category/manufacturing-execution-system |
| AVEVA CONNECT | https://www.aveva.com/en/products/connect/ |
| Predecessor — legacy v2 archive AVEVA MES reference | legacy-v2/reference/sources/aveva-mes.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
