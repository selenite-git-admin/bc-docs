---
uid: SRC-4d6a2e
slug: oracle-ebs
title: "Oracle E-Business Suite"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: enterprise-erp
subdomain: oracle
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://docs.oracle.com/cd/E26401_01/doc.122/e20927/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/oracle-ebs.md
---

# Oracle E-Business Suite

This page records BareCount's source-admission posture for Oracle E-Business Suite. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for ISG REST or JDBC; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `oracle-ebs-isg-rest` — REST against ISG-deployed PL/SQL APIs and Concurrent Programs (R12.2.3+).
- `oracle-ebs-jdbc` — direct JDBC reads against `APPS` synonyms (read-only); preferred for bulk historical loads when the customer permits.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of Accounts (`GL_CODE_COMBINATIONS`, `FND_ID_FLEX_SEGMENTS`); organisation hierarchies (`HR_ALL_ORGANIZATION_UNITS`); accounting calendar (`GL_PERIODS`); lookup values (`FND_LOOKUP_VALUES`); application dictionary (`FND_TABLES`, `FND_COLUMNS`); flexfield definitions; currency and rates (`FND_CURRENCIES`, `GL_DAILY_RATES`); item categories; payment terms.

### 3.2 Business data

| Domain | Key tables |
|---|---|
| General Ledger | `GL_JE_HEADERS/LINES`, `GL_BALANCES` |
| Accounts Payable | `AP_INVOICES_ALL`, `AP_CHECKS_ALL`, `AP_INVOICE_LINES_ALL`, `AP_INVOICE_DISTRIBUTIONS_ALL` |
| Accounts Receivable | `RA_CUSTOMER_TRX_ALL`, `RA_CUSTOMER_TRX_LINES_ALL`, `AR_CASH_RECEIPTS_ALL`, `AR_PAYMENT_SCHEDULES_ALL`, `HZ_PARTIES`, `HZ_CUST_ACCOUNTS` |
| Fixed Assets | `FA_ADDITIONS_B`, `FA_BOOKS`, `FA_DEPRN_SUMMARY` |
| Cash Management | `CE_BANK_ACCOUNTS`, `CE_STATEMENT_HEADERS/LINES` |
| Purchasing | `PO_HEADERS_ALL`, `PO_LINES_ALL` |
| Order Management | `OE_ORDER_HEADERS_ALL`, `OE_ORDER_LINES_ALL` |
| Inventory | `MTL_SYSTEM_ITEMS_B`, `MTL_MATERIAL_TRANSACTIONS` |
| Subledger Accounting (R12+) | `XLA_AE_HEADERS`, `XLA_AE_LINES` |

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

| Method | Protocol | Coverage | Notes |
|---|---|---|---|
| ISG REST | REST/JSON | PL/SQL APIs, Concurrent Programs | R12.2.3+; deployed via Integration Repository |
| ISG SOAP | SOAP 1.1/1.2 | Same | Some features need Oracle SOA Suite |
| JDBC direct | SQL over JDBC | Full DB | Read-only recommended; query via `APPS` schema |
| Oracle Integration Cloud | REST | EBS Adapter catalogue | Requires OIC licence + on-prem connectivity agent |
| BI Publisher | Scheduled XML/CSV | Report-defined scope | Periodic file extract |

### 6.2 Authentication for ISG REST

| Method | Description |
|---|---|
| HTTP Basic | EBS username + password, Base64 |
| Token-Based | Call Login Service to obtain EBS Token; pass on subsequent calls |
| SAML Token | PKI-trusted entity sends signed SAML assertion with valid EBS username |

For JDBC: standard Oracle DB authentication. Multi-org security via `MO_GLOBAL.INIT('M')` and `MO_GLOBAL.SET_POLICY_CONTEXT('S', <org_id>)`. Always query through `APPS` synonyms.

### 6.3 Rate limiting

EBS ISG has **no** native REST rate limiting. Throughput is bounded by WebLogic thread pool, DB connection pool, and Concurrent Manager limits. BareCount must implement client-side rate limiting (target 10–50 req/s) and respect WebLogic connection pool sizing.

---

## 7. Customer-Side Onboarding

1. Confirm R12.2 + ISG enabled (deploy via Integration Repository if not).
2. Create a service account with read-only access to required modules.
3. Choose auth path: Basic / Token / SAML for REST, or DB user for JDBC.
4. Confirm with Oracle licensing advisor that the read-only service account is covered under the customer's licence.
5. Configure network access (VPN or firewall rules) from BareCount to the EBS WebLogic / DB tier.
6. Hand BareCount: WebLogic URL, service account credentials, JDBC connection string (if used), confirmation of multi-org context.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'oracle_ebs'`
- `endpoint_url` (WebLogic URL) and/or `jdbc_url`
- `auth.method: 'basic' | 'ebs_token' | 'saml' | 'jdbc'`
- `org_id` / `ledger_id` / multi-org context

Smoke test: ISG path — call a benign GET; JDBC path — `SELECT 1 FROM DUAL` and a single-row read against `GL_PERIODS`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **ISG REST executor.**
2. **JDBC reader.** Generic JDBC connector with multi-org context handling (`MO_GLOBAL.SET_POLICY_CONTEXT`).
3. **Token-based auth helper** for ISG Login Service.
4. **Indirect-access advisory checklist** — needs a documented one-pager that customers can take to their Oracle licensing advisor.
5. **No OIC dependency** — BareCount cannot require OIC; the integration must work without it.
6. **R12.2 maintenance commitment** is through 2036 — sustained, not transitional. Investment in ECC executor is justified for a long maintenance window.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Oracle E-Business Suite R12.2 documentation | https://docs.oracle.com/cd/E26401_01/doc.122/e20927/ |
| ISG REST Services Guide | https://docs.oracle.com/cd/E26401_01/doc.122/e20927/T511175T673702.htm |
| EBS Integration Repository | https://docs.oracle.com/cd/E26401_01/doc.122/e20927/T511175T673698.htm |
| Oracle EBS Lifetime Support Policy | https://www.oracle.com/us/support/library/lifetime-support-applications-702468.pdf |
| Oracle Licensing Guide | https://www.oracle.com/assets/technology-price-list-070617.pdf |
| Predecessor — legacy v2 archive Oracle EBS reference | legacy-v2/reference/sources/oracle-ebs.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
