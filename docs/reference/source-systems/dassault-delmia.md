---
uid: SRC-c5d1e9
slug: dassault-delmia
title: "Dassault Systèmes DELMIA Apriso"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: mes
subdomain: dassault
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.3ds.com/support/documentation/delmia-apriso-2025-documentation
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/dassault-delmia.md
---

# Dassault Systèmes DELMIA Apriso

This page records BareCount's source-admission posture for Dassault Systèmes DELMIA Apriso. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no DELMIA auth helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate: `dassault-delmia-apriso-rest` — REST against the DELMIA integration framework.

---

## 3. What BareCount Admits

### 3.1 Metadata

Plant hierarchy (Enterprise / site / area / work-centre / work-unit, ISA-95 aligned); work-centre definitions; process plans / routings; manufacturing BOM; equipment master (machines, parameters, maintenance schedules, OPC-UA connection points); personnel master (operators, roles, skills); material definitions.

### 3.2 Business data — production

Production orders (work orders received from ERP, quantities, due dates, priority, specs); execution events (operation start/stop, quantities produced, scrap counts, cycle times, machine utilisation); WIP positions; process parameter records (machine settings, temperature, pressure, speed); product genealogy (full as-built traceability).

### 3.3 Business data — quality

Inspection plans (types, sampling, characteristics, tolerances); test results (measured values, pass/fail, NCRs); SPC (control chart data, capability indices, OOC alerts); Certificate of Analysis (lot-level quality certificates).

### 3.4 Business data — warehouse, maintenance, labour

Inventory positions; maintenance work orders; labour records.

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
| REST APIs | Modern integration; documented in 3DEXPERIENCE Developer documentation |
| SOAP / messaging | Legacy integration patterns; still supported |
| Process Builder | DELMIA-specific orchestration; can call external REST endpoints (push to BareCount) |

### 6.2 Endpoints

Per-tenant 3DEXPERIENCE platform URL.

### 6.3 Auth

3DEXPERIENCE OAuth 2.0 / 3DPassport — Dassault's authentication framework.

### 6.4 Pagination and incrementality

Standard offset/cursor. Incremental via `modified_since` filters per resource.

### 6.5 OPC-UA edge connectivity

For real-time machine data, DELMIA Apriso connects to OPC-UA-compliant equipment. BareCount admission would observe the **already-collected** data via the API surface, not connect to OPC-UA directly.

---

## 7. Customer-Side Onboarding

1. Customer enables 3DEXPERIENCE platform integration access for BareCount.
2. Customer provisions OAuth 2.0 client credentials via 3DPassport.
3. Customer scopes credentials to read-only DELMIA Apriso modules.
4. Customer grants documentation portal access.
5. Hand BareCount: 3DEXPERIENCE tenant URL, OAuth credentials, list of modules in scope.

---

## 8. BareCount-Side Onboarding

Connection profile: `system_type_code: 'dassault_delmia_apriso'`; `tenant_url`; `auth.method: 'oauth2_3dexperience'`; `auth.credential_ref`. Smoke test: a small list call against an enabled module.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **3DEXPERIENCE OAuth 2.0 (3DPassport)** auth method.
2. **DELMIA REST executor** with the platform-specific endpoint patterns.
3. **OPC-UA observability** — out of scope; admission goes through the DELMIA API surface, not direct OPC-UA.
4. **Customer-portal access** for schema discovery.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| DELMIA Apriso 2025 documentation | https://www.3ds.com/support/documentation/delmia-apriso-2025-documentation |
| 3DEXPERIENCE platform | https://www.3ds.com/3dexperience-platform |
| Predecessor — legacy v2 archive DELMIA Apriso reference | legacy-v2/reference/sources/dassault-delmia.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
