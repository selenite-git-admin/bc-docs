---
uid: SRC-8c5d71
slug: oracle-netsuite
title: "Oracle NetSuite"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: enterprise-erp
subdomain: oracle
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/book_1559132836.html
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/oracle-netsuite.md
---

# Oracle NetSuite

This page records BareCount's source-admission posture for Oracle NetSuite. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for SuiteTalk REST or SuiteQL; no TBA / OAuth 2.0 M2M helper in `CredentialResolverService`; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `oracle-netsuite-suiteql` — SuiteQL bulk reads (vendor-defined page size, SQL-like with `BUILTIN.DF()` / `BUILTIN.CF()`).
- `oracle-netsuite-rest-record` — SuiteTalk REST record-level CRUD (vendor-defined page size).
- `oracle-netsuite-restlet` — Custom RESTlet endpoints (customer-deployed SuiteScript).

---

## 3. What BareCount Admits

### 3.1 Metadata

Subsidiaries; chart of accounts; departments; classes (business segments); locations; currencies; accounting periods; payment terms; tax types; **custom segments and custom fields** (`custbody_`, `custcol_`, `custentity_`, `custitem_` prefixes — customer-specific, cannot be pre-seeded); units of measure; price levels.

### 3.2 Business data

**Transactions:** invoices (`invoice`), vendor bills (`vendorbill`), journal entries (`journalentry`), customer payments (`customerpayment`), vendor payments (`vendorpayment`), credit memos (`creditmemo`), sales orders (`salesorder`), purchase orders (`purchaseorder`), fulfillments (`itemfulfillment`), item receipts (`itemreceipt`), inventory adjustments (`inventoryadjustment`), work orders (`workorder`), expense reports (`expensereport`).

**Entities:** customers, vendors, employees, contacts, partners.

**Items:** inventory, non-inventory, service, assemblies/kits.

**Delta detection:** all records expose `lastmodifieddate` — incremental admission via SuiteQL `WHERE lastmodifieddate > ?`.

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

### 6.1 SuiteTalk REST (recommended)

| Aspect | Detail |
|---|---|
| Base URL | `https://<account-id>.suitetalk.api.netsuite.com/services/rest/record/v1/` |
| Auth | TBA (OAuth 1.0) or OAuth 2.0 M2M |
| Pagination | `limit` and `offset` (vendor-defined page-size limit) |
| Metadata | `GET /services/rest/record/v1/metadata-catalog/{recordType}` — OpenAPI 3.0 schema |
| Batch (2026.1) | Multi-record create / update / delete in a single HTTP request |

### 6.2 SuiteQL (primary for bulk reads)

| Aspect | Detail |
|---|---|
| Endpoint | `POST /services/rest/query/v1/suiteql` |
| Language | SQL-like (SELECT, FROM, WHERE, JOIN, GROUP BY, ORDER BY, subqueries) |
| Pagination | `limit`/`offset` in body (vendor-defined page-size limit) |
| Functions | `BUILTIN.DF()` (display value), `BUILTIN.CF()` (composite filter) |

### 6.3 RESTlets

Customer-deployed SuiteScript scripts. Single call can create/update multiple related records and apply custom business rules. 5 concurrent requests per user (within the account-level pool).

### 6.4 SuiteAnalytics Connect (ODBC/JDBC)

Read-only ODBC/JDBC. Host: `<account-id>.connect.api.netsuite.com`, port 1708. Requires SuiteCloud Plus.

### 6.5 Authentication

**Token-Based Authentication (TBA)** — recommended for M2M:
- 5 credentials: Account ID, Consumer Key, Consumer Secret, Token ID, Token Secret.
- Each request signed with HMAC-SHA256 (OAuth 1.0-style).

**OAuth 2.0 Machine-to-Machine** — newer:
- Available for REST + SuiteQL (not SOAP).
- Client credentials with X.509 certificate; standard Bearer tokens. Simpler than TBA.

### 6.6 Concurrency governance

NetSuite enforces concurrency at the account level — REST + SOAP + RESTlet all draw from the same pool.

| Service tier | Base concurrent | With SuiteCloud Plus |
|---|---|---|
| Shared | 5 | +10 per SC+ licence |
| Tier 1–5 | 15–55 | +10 per SC+ licence |

HTTP 429 when exceeded. `Retry-After` header. SuiteQL: vendor-defined page-size limit; REST list: vendor-defined page-size limit.

### 6.7 Unified transaction shape

All transactions share a single `Transaction` table differentiated by `type` (`CustInvc`, `VendBill`, `Journal`, `SalesOrd`, `PurchOrd`, etc.). SuiteQL tables: `Transaction`, `TransactionLine`, `TransactionAccountingLine`, `Customer`, `Vendor`, `Account`, `Item`.

---

## 7. Customer-Side Onboarding

1. Create an **Integration Record** (Setup → Integration → Manage Integrations).
2. Generate an Access Token under that record (TBA) or configure OAuth 2.0 M2M client + cert.
3. Create a custom role with read-only permissions for the modules in scope.
4. Assign the integration token / OAuth client to a service-account user with that role.
5. Confirm SuiteCloud Plus licensing if high concurrency is needed.
6. Hand BareCount: Account ID, the credential set (TBA quintuple or OAuth client credentials).

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'oracle_netsuite'`
- `account_id`
- `auth.method: 'tba_oauth1' | 'oauth2_m2m'`
- `auth.credential_ref`

Smoke test: REST `GET /metadata-catalog/customer`, then SuiteQL `SELECT id FROM customer WHERE ROWNUM = 1`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **TBA OAuth 1.0 signer** — HMAC-SHA256 signing of REST requests; not in `CredentialResolverService` in the readiness baseline.
2. **OAuth 2.0 M2M with X.509** auth method.
3. **SuiteQL executor** — bulk reader with paginated `limit`/`offset` against the `Transaction`/`Customer`/`Vendor` shape.
4. **Custom-field discovery** — `cust*_` prefixed fields are customer-specific; the catalogue must auto-discover from `metadata-catalog` per tenant.
5. **Concurrency-aware throttling** — must respect `Retry-After` and the per-tier concurrent limit.
6. **2026.1 batch support** — exploit when the executor lands.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| SuiteTalk REST | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/book_1559132836.html |
| SuiteQL Reference | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_156257770590.html |
| SuiteTalk SOAP | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/chapter_N3412498.html |
| Token-Based Authentication | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4247312445.html |
| OAuth 2.0 M2M | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_162aborr6166855.html |
| SuiteAnalytics Connect | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/bridgehead_N1949498.html |
| Concurrency Governance | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_156902498694.html |
| Predecessor — legacy v2 archive NetSuite reference | legacy-v2/reference/sources/oracle-netsuite.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
