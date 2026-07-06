---
uid: SRC-f2b836
slug: microsoft-d365-fo
title: "Microsoft Dynamics 365 Finance & Operations"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: enterprise-erp
subdomain: microsoft
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/odata
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/microsoft-d365-fo.md
---

# Microsoft Dynamics 365 Finance & Operations

This page records BareCount's source-admission posture for Microsoft Dynamics 365 Finance & Operations. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for OData V4 against D365 F&O; no Microsoft Entra OAuth helper in `CredentialResolverService`; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `microsoft-d365-fo-odata-v4` — synchronous OData V4 reads against `/data/{CollectionName}` for moderate-volume realtime/delta admission.
- `microsoft-d365-fo-dmf` — DMF (Data Management Framework) asynchronous bulk extract via Azure Blob Storage for initial historical loads.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of accounts (main account structures, account categories); legal entities (company codes, operating unit hierarchy); financial dimensions (custom segmented dimensions); currencies and exchange rate types; fiscal calendars; posting profiles; number sequences.

### 3.2 Business data

| Domain | Records |
|---|---|
| General Ledger | Posted vouchers, journal headers/lines, subledger entries |
| Vendor invoices | PO invoices, pending invoices, vendor invoice journals |
| Customer invoices | Sales order invoices, free text invoices, project invoices |
| Payments | Vendor payment journals, customer payment journals, settlement transactions |
| Fixed Assets | Acquisitions, depreciation transactions, disposals, transfers |
| Budget | Budget register entries, budget plan allocations |
| Bank | Statement imports, reconciliation, cash position |
| Purchase / Sales orders | Headers, lines, confirmations, packing slips |
| Inventory | Goods receipts, issues, transfer journals, counting journals |

### 3.3 Financial dimensions

D365 F&O uses a segmented dimension model where dimension combinations are stored as RecIds. OData entities typically expose dimensions as display strings (e.g. `001-100-CC01`). Parsing dimension segments requires knowledge of the customer's dimension structure.

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

### 6.1 OData V4 REST (primary)

| Aspect | Detail |
|---|---|
| Base URL | `https://{environment}.operations.dynamics.com/data/{CollectionName}` |
| Metadata | `https://{environment}.operations.dynamics.com/data/$metadata` |
| Query options | `$filter`, `$select`, `$expand`, `$orderby`, `$top`, `$skip`, `$count` |
| Cross-company | `?cross-company=true` (required for multi-entity reads) |
| Pagination | Server-driven, **vendor-defined page size** with `@odata.nextLink` |
| Timeout | Vendor-defined per-request timeout |
| Enum namespace | `Microsoft.Dynamics.DataEntities` |
| `$batch` | Supported — bundle multiple operations in one HTTP request |

Complex queries with deep `$expand` can hit the 2-minute timeout — prefer flat entity reads with subsequent lookups over deeply nested expansions.

### 6.2 Data Management Framework (DMF / DIXF)

Package REST API for asynchronous import/export via Azure Blob storage. Key APIs: `ImportFromPackage`, `ExportToPackage`, `GetExecutionSummaryStatus`. Better suited to initial historical loads (millions of records).

### 6.3 Authentication (Microsoft Entra ID)

Service-to-Service flow:

1. Register an application in Microsoft Entra ID (Azure portal → App Registrations).
2. Create a client secret or upload a certificate.
3. Add API permission for **Microsoft Dynamics ERP** (`Microsoft.ERP`).
4. In D365 F&O: **System Administration → Setup → Microsoft Entra applications** — register the app's Client ID and map to a service account user.
5. Obtain bearer token: `POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token`.
6. Use `Authorization: Bearer {token}` on all API requests.

Token lifetime: vendor-defined token window. Reader must implement refresh.

### 6.4 Rate limiting (service protection)

Two layers:

**Resource-based (environment-wide):** triggered when aggregate CPU/memory utilisation on web servers exceeds thresholds. Returns HTTP 429 with `Retry-After`. Priority-based throttling allows administrators to rank integration apps **High / Medium / Low** in **System Administration → Setup → Throttling priority mapping**.

**OData-specific:** vendor-defined page-size and request-time limits, `$batch` subject to same throttling.

BareCount design: exponential backoff respecting `Retry-After`; minimal payloads via `$select`; DMF for bulk; request customer to set BareCount's app to Medium or High priority.

### 6.5 Key data entities

**General Ledger:** `GeneralJournalAccountEntries`, `LedgerJournalHeaders`, `LedgerJournalLines`, `MainAccounts`, `FinancialDimensions`, `LegalEntities`.

**Accounts Payable:** `VendorInvoiceHeaders`, `VendorInvoiceLines`, `VendorsV2`, `VendorGroupEntities`.

**Accounts Receivable:** `SalesInvoiceHeadersV2`, `SalesInvoiceLinesV3`, `FreeTextInvoiceHeadersV2`, `CustomersV3`, `SalesOrderHeadersV2`.

**Fixed Assets:** `FixedAssets`, `FixedAssetBooks`, `FixedAssetGroups`, `FixedAssetTransactions`.

**Budgeting:** `BudgetRegisterEntryHeaders`, `BudgetAccountEntries`, `BudgetModels`.

**Supply Chain:** `PurchaseOrderHeadersV2`, `PurchaseOrderLinesV2`, `ProductsV2`, `InventoryOnhandEntities`.

### 6.6 Entity coverage gaps

Not every underlying table has an OData-enabled entity. Known gaps:
- `VendInvoiceJour` (posted vendor invoices) — no standard entity; needs custom entity or DMF export.
- `SubledgerJournalEntry` — limited entity coverage.
- Some entities exist for DMF but are not marked `IsPublic` for OData.

---

## 7. Customer-Side Onboarding

1. Register a new application in **Microsoft Entra ID** (Azure portal → App Registrations).
2. Create a client secret or upload an X.509 certificate.
3. Grant the application API permission for **Microsoft Dynamics ERP**.
4. In D365 F&O: System Administration → Setup → Microsoft Entra applications → register the app's Client ID and map to a system user with read-only roles for the modules in scope.
5. Set BareCount's app priority to **Medium** or **High** in throttling priority mapping.
6. Hand BareCount: tenant ID, client ID, client secret (or cert), environment URL.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'microsoft_d365_fo'`
- `endpoint_url`
- `auth.method: 'oauth2_entra_client_credentials'`
- `auth.credential_ref`
- `tenant_id`

Smoke test: hit `/data/$metadata`, then read one entity with `$top=1`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Microsoft Entra OAuth helper** in `CredentialResolverService` — needs `oauth2_entra_client_credentials` auth method (similar to OCI IAM but Entra-specific token endpoint and audience).
2. **OData V4 executor** with cross-company query support and `@odata.nextLink` pagination at the 10K-record-per-page cap.
3. **DMF executor** — drives async export jobs and admits the resulting CSV from Azure Blob.
4. **Throttle handling** — Retry-After header + priority-based throttling awareness.
5. **Financial dimension parsing** — display strings to dimension-segment tuples per customer's structure.
6. **Entity coverage gaps** — fallback strategy when a needed table has no OData entity (DMF or custom entity).

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| OData overview | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/odata |
| Data Entities overview | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entities |
| Service Protection API Limits | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/service-protection-api-limits |
| Priority-Based Throttling | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/priority-based-throttling |
| Data Management Package REST API | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-management-api |
| Authentication and Authorization | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/power-platform/authentication-and-authorization |
| Dynamics 365 Licensing Guide | https://www.microsoft.com/licensing/guidance/Dynamics-365 |
| Predecessor — legacy v2 archive D365 F&O reference | legacy-v2/reference/sources/microsoft-d365-fo.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
