---
uid: SRC-93f4b7
slug: sap-dm
title: "SAP Digital Manufacturing"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: mes
subdomain: sap
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://api.sap.com/package/SAPDigitalManufacturingCloud/rest
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-d2cdb9   # D384 — SAP API admission stance
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/sap-dm.md
---

# SAP Digital Manufacturing

This page records BareCount's source-admission posture for SAP Digital Manufacturing. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

What this means concretely:

- Architecture and onboarding documented.
- No reader executor for SAP DM REST or OData V4 APIs. The existing `SapOdataV4Executor` could likely target DM's OData V4 surfaces with minor work, but DM's primary integration surface is REST (per-domain endpoints under `/order/v1`, `/sfc/v1`, etc.) — no REST executor framework exists in the readiness baseline for this shape.
- No XSUAA-flow integration in `CredentialResolverService` — the OAuth 2.0 Client Credentials path it generally supports needs adaptation for the BTP service-key shape.
- No customer engagement.

Until the REST executor exists and has been shape-tested against an SAP DM trial tenant, **no SAP DM capability claim is permitted externally.**

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `sap-dm-rest-master` — REST APIs for master data (Plant, Material, Routing, Work Center, Resource).
- `sap-dm-rest-execution` — REST APIs for production (Order, SFC, Operation, Activity).
- `sap-dm-rest-quality` — REST APIs for inspection (Nonconformance, Inspection Lot, Visual Inspection).
- `sap-dm-odata-mdo` — OData V4 for Managed Data Objects (analytics).

---

## 3. What BareCount Admits

### 3.1 Metadata

Plant definitions, work-centre definitions, routing definitions (operation sequences, setup/processing/teardown times), material master, resource definitions (machine, tool, labour), bills of materials (BOM), shift and calendar definitions.

### 3.2 Business data — production

Production orders (order ID, material, plant, status, ERP reference); Shop Floor Control (SFC) records (WIP-tracking identifier, status, quantities); operation execution activities; process parameters; material consumption; OEE data (availability, performance, quality).

### 3.3 Business data — quality

Inspection lots; inspection results (measured values, pass/fail); nonconformances (defect codes, severity, disposition); visual inspection results (AI-model predictions, confidence scores).

### 3.4 Business data — logistics

Logistics orders (transport, staging); packing units; material staging requests.

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

### 6.1 Protocol

Two parallel surfaces:

| API | Use |
|---|---|
| REST APIs | Primary integration mechanism for transactional data — Order, SFC, Material, Routing, Nonconformance, Data Collection. JSON over HTTPS. |
| OData V4 APIs | Analytics-oriented; Managed Data Objects (MDOs); reporting. Vendor-defined records-per-response limit with `@odata.nextLink` continuation. |

### 6.2 Endpoint pattern

Base URL is region-specific:

```
https://api.<data-center-ID>.dmc.cloud.sap
```

Where `<data-center-ID>` is e.g. `eu20`, `us10`, `ap10`. Customer provides the exact host.

Per-domain REST APIs:

| API | Base path | Purpose |
|---|---|---|
| Order | `/order/v1` | Production and process order management |
| SFC | `/sfc/v1` | Shop floor control (WIP tracking) |
| Material | `/material/v1` | Material master data |
| Routing | `/routing/v1` | Manufacturing routing definitions |
| Work Center | `/workcenter/v1` | Work centre definitions |
| Resource | `/resource/v1` | Production resources (machines, tools, labour) |
| Nonconformance | `/nonconformance/v1` | Quality deviation records |
| Data Collection | `/datacollection/v1` | Process parameter capture |

### 6.3 Authentication

XSUAA OAuth 2.0 Client Credentials flow:

1. Customer creates a service instance of the SAP DM service in their BTP subaccount.
2. Customer creates a service key — yields `clientid`, `clientsecret`, and token endpoint `url`.
3. Customer hands BareCount the service key.
4. BareCount POSTs `clientid` + `clientsecret` to the token URL, receives a Bearer JWT.
5. JWT is used in `Authorization: Bearer <token>` for subsequent API calls.

| Aspect | Detail |
|---|---|
| Token type | Bearer JWT |
| Token lifetime | Configurable; typically 12 hours |
| Refresh | Re-fetch before expiry; no refresh-token flow |
| Audit | Authentication failures return HTTP 401 |

### 6.4 Rate limiting

| Aspect | Detail |
|---|---|
| Per-tenant rate limits | Enforced by SAP BTP; HTTP 429 on excess |
| Backoff | `Retry-After` header included in 429 responses |
| MDO OData pagination | Vendor-defined records-per-response cap |
| Fair-use policy | Per BTP service description guide |

---

## 7. Customer-Side Onboarding

1. **Confirm SAP DM subscription** is active on a BTP subaccount.
2. **Create a service instance** of the SAP DM service in that subaccount (Cockpit → Service Marketplace → SAP Digital Manufacturing → Create).
3. **Create a service key** for that instance — Cockpit will produce a JSON containing `clientid`, `clientsecret`, `url`, and other metadata.
4. **Confirm regional data centre ID** (e.g. `eu20`).
5. **Confirm functional scope** — which modules BareCount will admit from (Execution, Insights, etc.).
6. **Hand BareCount**: the service key JSON + the regional data centre ID.

---

## 8. BareCount-Side Onboarding

Connection profile shape:

- `system_type_code: 'sap_dm'`
- `endpoint_url` — `https://api.<data-center-ID>.dmc.cloud.sap`
- `auth.method: 'oauth2_xsuaa_client_credentials'` (extension of the existing OAuth method)
- `auth.credential_ref` — reference to the BTP service key JSON in external store
- `module_scopes[]` — modules in scope (`execution`, `insights`, …)

Smoke test: fetch a token, then call `/order/v1/orders?limit=1` to confirm shape and authority.

---

## 9. Verified Coverage

**Nothing.** No SAP DM tenant has been onboarded.

---

## 10. Known Gaps

1. **REST executor** — BareCount has OData V4/V2 executors but no generic REST executor for the per-domain SAP DM API shapes.
2. **XSUAA token-fetch helper** — `CredentialResolverService` needs an XSUAA-aware variant of OAuth 2.0 Client Credentials.
3. **Pagination strategy for MDO OData** — vendor-defined pagination cap requires explicit pagination handling.
4. **Adaptive throttle / backoff** for BTP rate limits.
5. **Edge Computing component** is out of scope for this reference baseline — local edge runtime is a different integration model.
6. **SAP ME / SAP MII customers** — these legacy MES products reach end-of-mainstream Dec 2027; they are not SAP DM and would need separate source pages if BareCount engages a customer still on them.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — SAP API admission stance (D384) | [ADR-d2cdb9](../../governance/adrs/ADR-d2cdb9.md) |
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Companion appendix — SAP licensing & catalogue rules | [sap-licensing-reference.md](sap-licensing-reference.md) |
| SAP DM REST API catalogue | https://api.sap.com/package/SAPDigitalManufacturingCloud/rest |
| SAP DM OData V4 APIs | https://api.sap.com/package/SAPDigitalManufacturingCloud |
| SAP DM Help — APIs | https://help.sap.com/docs/sap-digital-manufacturing/service-catalog/apis |
| SAP DM Integration Guide (PDF) | https://help.sap.com/doc/f6b2ab2222794bebad4c0dcd33138e71/latest/en-US/SAP_DMC_Integration_Guide_enUS.pdf |
| SAP DM Security Guide (PDF) | https://help.sap.com/doc/bbfa1f9524cc4ec3837d8551132f441a/latest/en-US/SAP_DMC_Security_Guide_enUS.pdf |
| S/4HANA integration package | https://api.sap.com/package/DMEInt/overview |
| SAP DM product page | https://www.sap.com/products/scm/digital-manufacturing.html |
| Predecessor — legacy v2 archive SAP DM reference | legacy-v2/reference/sources/sap-dm.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
