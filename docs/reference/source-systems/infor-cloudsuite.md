---
uid: SRC-b3f892
slug: infor-cloudsuite
title: "Infor CloudSuite"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: enterprise-erp
subdomain: infor
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developer.infor.com/hub/apis
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/infor-cloudsuite.md
---

# Infor CloudSuite

This page records BareCount's source-admission posture for Infor CloudSuite. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for ION BOD subscription or ION API Gateway REST; no Infor OAuth Resource Owner helper in `CredentialResolverService`; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `infor-ion-bod-subscriber` — IMS Connector receiving event-driven BODs (XML, OAGIS standard) for transaction observation.
- `infor-ion-api-gateway-rest` — REST against ION API Gateway for targeted reads, metadata discovery, moderate-volume integration.
- `infor-data-lake-compass` — Compass SQL queries against the Infor Data Lake for bulk historical extracts and analytics-driven access.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of accounts structure and account segments; legal entities and accounting entities; business units / companies / sites; currency definitions and exchange rate types; fiscal calendar and period definitions; supplier and customer master records; item master and product classifications; warehouse and location hierarchies; user-defined fields and code definitions.

### 3.2 Business data — by domain

| Domain | Objects |
|---|---|
| Financials | GL journals, account balances, trial balance, AP invoices/payments, AR invoices/receipts, cash management, bank statements, fixed asset transactions |
| Procurement | Purchase orders, requisitions, goods receipts, supplier invoices, blanket agreements |
| Sales | Sales orders, quotations, invoices, credit memos, returns |
| Inventory | Inventory transactions, stock levels, lot/serial tracking, cycle counts, valuation |
| Manufacturing | Production orders, work orders, BOM explosions, shop floor transactions, quality results |
| Supply Chain | Demand planning outputs, MRP results, shipment records, ASNs |

### 3.3 CloudSuite editions (vertical scope)

| Edition | Base ERP | Industry |
|---|---|---|
| Industrial (CSI) | SyteLine | Discrete / engineer-to-order manufacturing |
| Financials | Infor FSM | Healthcare, public sector, higher education |
| Distribution | Infor M3 / SX.e | Wholesale distribution |
| Food and Beverage | Infor M3 | F&B process manufacturing |
| Fashion | Infor M3 | Apparel, footwear, textiles |
| Chemicals | Infor M3 | Chemical process manufacturing |
| Automotive | Infor LN | Automotive OEM and tier suppliers |
| Aerospace and Defense | Infor LN | Aerospace, defense, complex manufacturing |
| Healthcare | Infor FSM + Cloverleaf | Hospitals, health systems |
| HCM | Infor Global HR | Cross-industry HCM |

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

### 6.1 Infor ION (primary — event-driven)

ION (Intelligent Open Network) is the integration middleware. Asynchronous, event-driven messaging using **Business Object Documents (BODs)**.

| Aspect | Detail |
|---|---|
| Pattern | Asynchronous, event-driven via BODs |
| Transport | BODs flow through ION message queues; applications connect via ION connectors |
| Connector types | Application Connector (Infor apps), **IMS Connector** (REST/JSON for external apps), File Connector (CSV/XML) |
| Workflow | Visual designer for orchestrating multi-step processes; monitors for alerting on BOD events |
| SOR (System of Record) | Each BOD has a designated owner — outbound BODs come from the SOR, inbound go to the SOR |

BareCount integrates as an external application via the **IMS Connector** — receives BOD events at a registered HTTPS endpoint.

### 6.2 BOD structure (OAGIS standard)

```
BOD
+-- ApplicationArea (sender metadata, timestamps, tenant ID, logical ID, BOD ID)
+-- DataArea
    +-- Verb (Sync, Process, Acknowledge, Get, Show, Cancel, Load, Post)
    +-- Noun (PurchaseOrder, AccountingJournal, etc.)
```

Common BOD nouns: `AccountingJournal` (GL), `PayableTransaction` (AP invoice), `ReceivableTransaction` (AR), `PurchaseOrder`, `SalesOrder`, `ItemMaster`, `SupplierPartyMaster`, `CustomerPartyMaster`, `ProductionOrder`, `BillOfMaterials`, `Person` (HR), `Payroll`.

### 6.3 ION API Gateway (REST)

NodeJS-based reverse proxy brokering all REST API requests to CloudSuite applications.

| Aspect | Detail |
|---|---|
| Base path | `https://<tenant>.inforcloudsuite.com/<application>/api/v2/<resource>` |
| Auth | OAuth 2.0 (mandatory) |
| Methods | GET, POST, PUT, PATCH, DELETE |
| Documentation | Swagger 2.0 / OpenAPI 3.0 per application; available via `developer.infor.com/hub/apicatalog` |
| Rate limits | Governed by Infor OS tier (Essentials vs. Professional) — increased on Professional |

### 6.4 Authentication — OAuth 2.0 via Infor OS

| Grant type | Use |
|---|---|
| Resource Owner | **Server-to-server (recommended for BareCount)** |
| Authorization Code | Native mobile/desktop, web apps |
| Implicit | SPAs (legacy) |
| SAML Bearer | Apps integrated with Infor Ming.le SSO |

Setup:

1. Customer registers a BareCount application in their ION API Gateway → generates `client_id` + `client_secret`.
2. Service account created in Infor Federation Services (IFS) with read-only roles.
3. BareCount uses Resource Owner grant for automated token acquisition and refresh.
4. Token lifetime: 2 hours by default (configurable per application).

### 6.5 Infor Data Lake and Birst

Centralised data store within Infor OS aggregating data from connected CloudSuite applications. Queryable via Compass SQL, Compass JDBC driver, and Data Lake APIs. Birst is the embedded BI platform. Useful for bulk historical extracts and cross-application reporting.

---

## 7. Customer-Side Onboarding

1. Confirm Infor OS tier (Essentials or Professional) covers ION API Gateway access.
2. Confirm with Infor account team that BareCount's read-only ION integration does not trigger automation licensing under the customer's contract.
3. Register a BareCount application in the ION API Gateway (Infor OS portal) — receive `client_id` + `client_secret`.
4. Create a service account in Infor Federation Services (IFS) with read-only roles scoped to the modules in scope.
5. Configure ION subscriptions to relevant BOD events (e.g. `SyncAccountingJournal`, `SyncPayableTransaction`, `SyncPurchaseOrder`).
6. Configure delivery to BareCount's registered HTTPS endpoint (IMS Connector).
7. Hand BareCount: tenant URL, `client_id`, `client_secret`, service account identity, list of subscribed BODs, application names in scope.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'infor_cloudsuite'`
- `tenant_url`
- `auth.method: 'oauth2_resource_owner'` (Infor OS variant)
- `auth.credential_ref`
- `applications[]` — CloudSuite applications in scope (e.g. `SyteLine`, `M3`, `LN`, `FSM`)
- `bod_subscriptions[]` — list of BOD nouns BareCount expects to receive

Smoke test: OAuth token fetch, then a single REST GET against the API Catalogue's discovery endpoint.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **OAuth Resource Owner grant** — `CredentialResolverService` does not yet support this Infor-specific OAuth flow.
2. **BOD subscriber** — IMS Connector endpoint that receives, validates, and parses OAGIS-XML BODs into `RunObservationItem`s.
3. **REST executor with Infor's gateway path shape** — `<tenant>.inforcloudsuite.com/<application>/api/v2/...`.
4. **Compass SQL connector** for Data Lake bulk extraction.
5. **Per-edition entity mapping** — SyteLine, M3, LN, FSM each have different underlying schemas; the canonical mapping must adapt per customer's edition.
6. **OAGIS BOD schema library** — keep up with versioned BOD schemas at `schema.infor.com/InforOAGIS/Nouns/`.
7. **Indirect-access advisory checklist** — document the licensing conversation customers must have with their Infor account team before BareCount admission begins.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Infor Developer Portal — API Catalogue | https://developer.infor.com/hub/apicatalog |
| Infor Developer Portal — API Gateway Tutorials | https://developer.infor.com/tutorials/api-gateway |
| ION API Administration Guide | https://docs.infor.com/ionapi/2021-x/en-us/ionapiag_cloud/default.html |
| Infor OS Service Limits | https://docs.infor.com/inforos/12.0.x/en-us/usagelimits_1_0_1/ksp1587771642875.html |
| Infor OAGIS BOD Noun Schema Registry | https://schema.infor.com/InforOAGIS/Nouns/ |
| BOD Message Structure | https://docs.infor.com/depm/2022.x/en-us/depmolh/configuring_ion/exl1510174563113.html |
| ION API SDK (GitHub) | https://github.com/infor-cloud/ion-api-sdk |
| Predecessor — legacy v2 archive Infor CloudSuite reference | legacy-v2/reference/sources/infor-cloudsuite.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
