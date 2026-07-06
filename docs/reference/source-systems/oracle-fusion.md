---
uid: SRC-1b8e5a
slug: oracle-fusion
title: "Oracle Fusion Cloud ERP"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: enterprise-erp
subdomain: oracle
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://docs.oracle.com/en/cloud/saas/financials/25d/farfa/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/oracle-fusion.md
---

# Oracle Fusion Cloud ERP

This page records BareCount's source-admission posture for Oracle Fusion Cloud ERP. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor; no OAuth-via-OCI-IAM helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `oracle-fusion-rest-v1` — REST API V1 against `/fscmRestApi/resources/11.13.18.05/{resource}`.
- `oracle-fusion-bicc` — BICC pre-defined data store (PVO) bulk extract for historical / large-volume loads, output to OCI Object Storage as CSV with manifest.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of accounts (segments, value sets, hierarchies); business units; ledgers and ledger sets; currencies and exchange rates; lookup values; suppliers and customers; tax configuration; items and categories; organisations; project structures.

### 3.2 Business data

| Domain | Business objects |
|---|---|
| General Ledger | Journal batches/headers/lines, account balances (PTD/QTD/YTD), subledger accounting entries |
| Accounts Payable | Supplier invoices, lines, distributions, payment batches, payments, holds, prepayments |
| Accounts Receivable | Customer invoices, credit memos, receipts, receipt applications, adjustments |
| Fixed Assets | Asset books, additions, depreciation schedules, retirements, revaluations |
| Cash Management | Bank statements, lines, reconciliation, internal transfers, cash positions |
| Procurement | Purchase orders, requisitions, agreements, receipts, sourcing awards |
| Project Management | Project costs, expenditure items, budgets, revenue, billing events |

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

### 6.1 REST API V1 (primary)

| Aspect | Detail |
|---|---|
| Base path | `https://<HOST>/fscmRestApi/resources/11.13.18.05/<resource>` |
| Pagination | `offset` and `limit` (default page size typically 25) |
| Filtering | `q` parameter with field-level filters (e.g. `?q=InvoiceDate>2025-01-01`) |
| Field selection | `fields` |
| Expand | `expand` |
| POST limit | Vendor-defined POST batch-size limit |
| Quarterly versioning | Feature releases 25A–26D; resource version `11.13.18.05` stable |

V2 APIs are being introduced for specific resources with enhanced filtering and performance — not generally available across the surface yet.

### 6.2 BICC bulk extract

Optimized pre-defined data stores (PVOs) per module. Full and incremental modes. Output: CSV with `MANIFEST.MF` and MD5 checksums. Default extract timeout: 10 hours per view object. Suited to initial historical loads (millions of records).

### 6.3 ERP Business Events

Event-driven push for real-time notification of transaction changes (journal posted, invoice validated, payment created). Useful for triggering near-realtime delta admission.

### 6.4 Authentication

OCI IAM (Identity and Access Management) for OAuth 2.0 — **not** the older standalone IDCS. Steps:

1. Configure a **Confidential Application** in the OCI IAM Identity Domain linked to the Fusion instance.
2. Define access **scope** (e.g. `urn:opc:resource:fa:adf.fscm.read`).
3. Use **Client Credentials** grant for server-to-server.
4. Exchange `client_id` + `client_secret` at `/oauth2/v1/token` for an access token.
5. Pass token as `Authorization: Bearer <token>`.

### 6.5 Rate limits

Oracle does not publish explicit per-minute REST rate limits. Constraints: pod capacity, fair-use, BICC 10-hour timeout per PVO, max 30 identity trust objects per instance.

### 6.6 Key REST resources

**Financials:** `invoices`, `receivablesInvoices`, `journalBatches`, `ledgerBalances`, `payablesPayments`, `cashBankAccounts`, `bankStatements`, `expenseReports`, `currencyRates`.

**Procurement:** `purchaseOrders`, `purchaseRequisitions`, `purchaseAgreements`, `suppliers`, `supplierNegotiations`.

**Projects:** `projects`, `projectCosts`, `projectExpenditureItems`, `projectBudgets`, `awards`.

**Supply chain:** `inventoryTransactions`, `receivingTransactions`, `inboundShipments`.

**Platform:** `erpintegrations`, `erpBusinessEvents`, `commonLookups`.

---

## 7. Customer-Side Onboarding

1. Confirm active Fusion subscription and the modules in scope.
2. In OCI IAM (Identity Domain linked to the Fusion instance), create a **Confidential Application** for BareCount with the appropriate scope.
3. Generate `client_id` and `client_secret` (or upload a certificate).
4. In Fusion, create an integration user (or designate one) with the job roles needed for the modules in scope; map to the OCI IAM application.
5. Hand BareCount: tenant base URL, `client_id`, `client_secret` (or cert), integration user identity, scope.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'oracle_fusion'`
- `endpoint_url`
- `auth.method: 'oauth2_client_credentials_oci'` (extension of existing OAuth method)
- `auth.credential_ref` — to credential in external store
- `module_scopes[]`

Smoke test: hit `/fscmRestApi/resources/11.13.18.05` root, then list one resource (`invoices?limit=1`).

---

## 9. Verified Coverage

**Nothing.** No reader, no admission.

---

## 10. Known Gaps

1. **REST executor** with Fusion's V1 path conventions and `q`-parameter filter dialect.
2. **OCI IAM OAuth client_credentials** helper in `CredentialResolverService`.
3. **BICC integration** — separate executor that drives the PVO extract job and admits the CSV output from OCI Object Storage.
4. **ERP Business Events** subscriber for near-realtime triggers.
5. **Quarterly-release feature drift** — new entities and new V2 endpoints land each quarter; the catalogue must refresh accordingly.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| REST API for Financials (Release 25D) | https://docs.oracle.com/en/cloud/saas/financials/25d/farfa/ |
| REST API for Procurement | https://docs.oracle.com/en/cloud/saas/procurement/26a/fapra/rest-endpoints.html |
| REST API for Projects | https://docs.oracle.com/en/cloud/saas/project-management/25d/fapap/rest-endpoints.html |
| Configure OAuth using OCI IAM | https://docs.oracle.com/en/cloud/saas/applications-common/25b/oaext/configure-oauth.html |
| Data extraction guidelines (A-Team) | https://www.ateam-oracle.com/data-extraction-options-and-guidelines-for-oracle-fusion-applications-suite |
| Oracle Fusion Cloud Service Descriptions | https://www.oracle.com/contracts/docs/oracle-fusion-cloud-service-desc-1843611.pdf |
| Predecessor — legacy v2 archive Oracle Fusion reference | legacy-v2/reference/sources/oracle-fusion.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
