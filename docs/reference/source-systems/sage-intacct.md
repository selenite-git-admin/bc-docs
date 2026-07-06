---
uid: SRC-f6d0b4
slug: sage-intacct
title: "Sage Intacct"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: accounting
subdomain: sage
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developer.sage.com/intacct/docs/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/sage-intacct.md
---

# Sage Intacct

This page records BareCount's source-admission posture for Sage Intacct. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for REST or XML Web Services; no OAuth 2.0 (REST) or sender-ID (XML) helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `sage-intacct-rest` — REST API (OAuth 2.0) for the growing set of objects available via REST.
- `sage-intacct-xml` — XML Web Services (sender ID + password) for full object coverage — fallback for objects not in REST.
- `sage-intacct-dds` — Data Delivery Service for scheduled CSV/flat-file batch reads.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of Accounts (`GLACCOUNT`); 10 standard dimensions (`DEPARTMENT`, `LOCATION`, `CLASS`, `TERRITORY`, `EMPLOYEE`, `PROJECT`, `CUSTOMER`, `VENDOR`, `ITEM`, `WAREHOUSE`); user-defined dimensions (custom UDD objects); entities (`LOCATIONENTITY` — multi-entity structures); currencies (`CURRENCY`, `EXCHRATEYPE`); payment terms (`APTERM`); tax (`TAXDETAIL`, `TAXSCHEDULE`); journals (`JOURNAL`); ownership structures (`GCOWNERSHIPSTRUCTURE`, `GCOWNERSHIPENTITY`).

### 3.2 Business data

| Domain | Objects |
|---|---|
| GL Entries | `GLBATCH`, `GLENTRY` |
| AP Bills | `APBILL`, `APBILLITEM` |
| AP Payments | `APPAYMENT` |
| AR Invoices | `ARINVOICE`, `ARINVOICEITEM` |
| AR Payments | `ARPAYMENT` |
| Cash Receipts | `CASHRECEIPT` |
| Bank Accounts | `CHECKINGACCOUNT`, `SAVINGSACCOUNT`, `CREDITCARD` |
| Deposits | `DEPOSIT` |
| Purchase Orders | `PODOCUMENT`, `PODOCUMENTENTRY` |
| Sales Orders | `SODOCUMENT`, `SODOCUMENTENTRY` |
| Inventory | `ICITEM` |
| Fixed Assets | `ASSETS` |
| GL Balances | `GLACCOUNTBALANCE` |
| GL Detail | `GLDETAIL` |

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

### 6.1 Available APIs

| API | Protocol | Coverage | Status |
|---|---|---|---|
| REST API | JSON over HTTPS (OAuth 2.0) | Growing — recommended for new dev | **GA (Feb 2025)** |
| XML Web Services | XML over HTTPS (SOAP-like) | Full | Mature, production-grade |
| Data Delivery Service (DDS) | Scheduled CSV/flat-file | Read-only export of selected objects | Batch-oriented, useful for bulk |

### 6.2 Authentication

**REST API:**
- OAuth 2.0 authorization code flow.
- Access tokens expire in 1 hour; refresh tokens last 6 months.
- No sender ID required.

**XML Web Services:**
- Sender ID + password (developer-level).
- Plus per-customer Web Services user credentials.
- Each request includes session ID obtained from a `getAPISession` call.

### 6.3 Pagination and incrementality

REST: standard cursor-based pagination. XML `readByQuery`: returns `numremaining` and `resultId` for continuation. Incremental admission via `WHENMODIFIED > '...'` query.

### 6.4 Performance tier and transaction counting

Each `read*` operation counts as one transaction. BareCount admission contracts should batch reads (multi-record `readByQuery`) to minimise transaction count.

---

## 7. Customer-Side Onboarding

1. **Enable Web Services subscription** at the company level (Company → Admin → Subscriptions).
2. **Authorise BareCount sender ID** (XML path) for the company.
3. Create a Web Services user with read-only permissions for the modules in scope.
4. Or for REST: customer goes through OAuth 2.0 consent flow.
5. Confirm Performance Tier covers expected BareCount transaction volume.
6. Hand BareCount: company ID, Web Services user credentials (XML path) or OAuth tokens (REST).

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'sage_intacct'`
- `company_id`
- `auth.method: 'oauth2_sage_intacct' | 'sage_intacct_xml_session'`
- `auth.credential_ref`
- `performance_tier` — informational; helps BareCount budget reads

Smoke test: REST — list one entity; XML — `getAPISession` then a small `readByQuery`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **REST OAuth 2.0 helper** — authorization code flow with the 6-month refresh window.
2. **XML Web Services session manager** — `getAPISession` + sender-ID-signed envelopes.
3. **Two executors** that share canonical mapping but differ in protocol — REST executor for available objects, XML executor for fallback.
4. **DDS receiver** — scheduled CSV pickup from configured destination.
5. **REST/XML object-coverage map** — must keep current as REST adds objects; admission contract chooses path per object.
6. **Performance Tier transaction budgeting** — admission contract should declare expected reads; alert if approaching tier limit.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Sage Intacct Developer | https://developer.sage.com/intacct/docs/ |
| REST API reference | https://developer.sage.com/intacct/reference/ |
| XML Web Services API | https://developer.sage.com/intacct/docs/web-services/ |
| Data Delivery Service | https://developer.sage.com/intacct/docs/data-delivery/ |
| Predecessor — legacy v2 archive Sage Intacct reference | legacy-v2/reference/sources/sage-intacct.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
