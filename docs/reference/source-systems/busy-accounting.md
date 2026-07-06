---
uid: SRC-7d2c5f
slug: busy-accounting
title: "Busy Accounting"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: accounting
subdomain: busy
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://busy.in/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/busy-accounting.md
---

# Busy Accounting

This page records BareCount's source-admission posture for Busy Accounting. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for any Busy access path; no on-premise agent; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `busy-accounting-mssql` — direct ODBC/JDBC to the MSSQL backend (Enterprise edition only). Preferred path when available.
- `busy-accounting-msaccess` — direct read of `.mdb` files (Basic / Standard editions). Requires file-share access.
- `busy-accounting-export` — scheduled CSV / Excel / XML pickups from a customer-configured drop location.
- `busy-accounting-middleware` — admit via RootFi or similar third-party that already bridges Busy to cloud.
- `busy-accounting-agent` — BareCount-deployed local agent that reads the DB and tunnels to BareCount cloud.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of Accounts (account masters, groups, sub-groups); cost centres and cost categories; stock groups and item masters (item categories, UOM, price lists); voucher type definitions (sales, purchase, journal, payment, receipt, contra, debit/credit notes); GST configuration (GSTIN, HSN/SAC codes, GST rate slabs); godown (warehouse) definitions; employee masters (Enterprise edition payroll); broker/agent masters.

### 3.2 Business data

Vouchers (sales, purchase, sales return, purchase return, payment, receipt, journal, contra, debit note, credit note, stock transfer); ledger entries (transaction-level postings with narrations); inventory movements (stock journal, stock transfer, goods receipt/dispatch); GST returns data (GSTR-1, GSTR-3B, GSTR-2A/2B reconciliation); TDS / TCS records; outstanding reports (receivables / payables aging); production records (BOM-based, job work — Enterprise); payroll records (Enterprise).

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

### 6.1 Storage backends

| Mode | Database | Editions | Notes |
|---|---|---|---|
| File Server | MS Access (`.mdb`) | All | Default. Data files on shared network drive. Concurrency limited. |
| Client-Server | Microsoft SQL Server | Enterprise only | Better concurrency and data integrity. Standard MSSQL ODBC/JDBC works. |

### 6.2 Access patterns

| Pattern | Protocol | Best for |
|---|---|---|
| MSSQL direct | ODBC/JDBC | Reliable bulk + delta for Enterprise customers |
| MS Access direct | ODBC + Jet/ACE driver | Basic/Standard customers; file lock contention with active Busy users |
| Busy export utility | CSV/Excel/XML | Lowest-friction; customer-driven scheduled exports |
| Third-party middleware | Vendor-specific | If customer already uses RootFi etc. |

### 6.3 Authentication

Busy itself does not authenticate API access (because there is no API). Authentication is network/database layer:

- MSSQL: standard SQL Server auth (Windows or SQL credentials).
- MS Access: file-share permissions on the `.mdb`.
- Export pickup: SFTP / S3 / signed URL credentials.
- Agent: BareCount-issued service token over outbound TLS tunnel.

### 6.4 Schema discovery

Busy's database schema is **proprietary and version-dependent**. The data dictionary is not publicly published. BareCount must:

1. Profile the customer's schema (tables, columns) at admission contract design time.
2. Maintain a **Busy schema map** keyed on version (Busy 18, 19, 20, 21).
3. Re-verify when a customer upgrades.

This is a significant catalogue-population cost compared with cloud-API sources.

### 6.5 Delta strategy

Most Busy tables include an `EntryDate` and `LastModified` field. Voucher numbers are monotonic per voucher type. Strategies:
- Date-range queries on `EntryDate` / `LastModified`.
- Voucher number high-water mark plus reconciliation.
- Full daily snapshot if size is small.

---

## 7. Customer-Side Onboarding

1. Confirm Busy edition (Basic / Standard / Enterprise) and version.
2. Confirm storage backend (MS Access vs MSSQL).
3. Choose bridge model:
   - MSSQL direct (Enterprise): customer creates a read-only SQL user, configures network access (VPN or BareCount agent).
   - MS Access (Basic / Standard): customer grants share-level read access to the `.mdb`; BareCount agent or VPN.
   - Export pickup: customer schedules CSV / Excel / XML exports to a configured drop location.
   - Middleware: customer signs up with the chosen middleware vendor.
4. Hand BareCount: connection details, credentials, chosen bridge.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'busy_accounting'`
- `busy_version` (18 / 19 / 20 / 21)
- `bridge_method: 'mssql' | 'msaccess' | 'export' | 'middleware' | 'agent'`
- `auth.method` per bridge
- `auth.credential_ref`
- `schema_map_version` — BareCount-internal: which schema map to apply

Smoke test: per bridge — MSSQL `SELECT 1`; MS Access table-list; export drop reachability; middleware ping.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **MSSQL/MS Access executor** — generic JDBC connector tuned for the read-only-with-bookmarks Busy pattern.
2. **Busy schema map (per version)** — not in any catalogue in the readiness baseline; would be a substantial reverse-engineering effort or partnership with Busy Infotech.
3. **BareCount Tally / Busy Bridge agent** (shared with Tally) — Windows service for outbound-tunnel access.
4. **Export pickup pipeline** — scheduled SFTP/S3 ingest with file-shape validation.
5. **Customer-edition gating** — many MSME prospects will be Basic / Standard with MS Access backend; concurrency constraints on MS Access with active users need careful handling.
6. **GST returns module** — `GSTR-1/3B/2A/2B` schemas evolve with statutory changes.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Busy Infotech | https://busy.in/ |
| Busy product overview | https://busy.in/products/busy-accounting-software |
| Busy GST features | https://busy.in/gst-accounting-software |
| Predecessor — legacy v2 archive Busy Accounting reference | legacy-v2/reference/sources/busy-accounting.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
