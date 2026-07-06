---
uid: SRC-b3e7c2
slug: tally-prime
title: "Tally Prime"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: accounting
subdomain: tally
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://help.tallysolutions.com/integration-with-tallyprime/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/tally-prime.md
---

# Tally Prime

This page records BareCount's source-admission posture for Tally Prime. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for ODBC, XML, or JSON Tally APIs; no on-premise agent or VPN bridge architecture; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `tally-prime-xml` — XML API over local TCP.
- `tally-prime-json` — JSON API over local TCP (preferred over XML for new dev).
- `tally-prime-odbc` — ODBC for SQL-style queries (limited syntax).
- `tally-prime-agent` — BareCount-deployed local agent that the customer installs alongside Tally; bridges to the BareCount cloud over an outbound TLS tunnel.

---

## 3. What BareCount Admits

### 3.1 Metadata

Company master definitions (chart of accounts, cost centres, stock groups); voucher type definitions (sales, purchase, journal, payment, receipt); GST configuration (HSN codes, GST rates, GSTIN details); stock item categories and unit definitions.

### 3.2 Business data

Voucher records: sales, purchase, journal, payment, receipt, contra, debit / credit notes; ledger balances and transaction history; stock movement and inventory reports; GST returns data (GSTR-1, GSTR-3B, GSTR-9 fields).

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

### 6.1 Access methods

| Method | Protocol | Notes |
|---|---|---|
| ODBC | SQL over TCP (port 9000) | Read-only via SQL-like queries; limited syntax |
| XML API | HTTP POST to Tally's built-in HTTP server | TDL-based request/response; full access; all operations are POST |
| JSON API | HTTP POST to Tally's built-in HTTP server | Modern alternative to XML; same capabilities; easier parsing |

### 6.2 Network requirement

Tally must be running and reachable on the network. There is **no cloud-hosted API**. For remote access:

- Customer exposes Tally port (default 9000) — security risk; avoid where possible.
- Customer-side VPN.
- BareCount agent on the Tally host with outbound tunnel.

### 6.3 Authentication

Tally itself does not use modern auth. Authentication is **network-layer**:
- IP whitelisting.
- VPN / TLS tunnel termination point.
- Optionally a Tally user with restricted security level for the connection.

The agent / bridge layer carries its own credentials (BareCount-issued service token).

### 6.4 Delta strategy

Voucher records have no built-in `lastModifiedDateTime`. Strategies:
- Full daily snapshot.
- Voucher number high-water mark plus periodic reconciliation.
- TDL-based incremental query (date range on `VOUCHERDATE`).

---

## 7. Customer-Side Onboarding

1. Customer confirms Tally Prime version and edition (Silver / Gold).
2. Choose bridge model:
   - VPN: customer-side VPN to BareCount.
   - Agent: install BareCount's Tally Bridge agent on the Tally host or a peer machine.
   - Middleware: subscribe to a third-party Tally-to-cloud bridge.
3. Customer creates a Tally user with appropriate security level.
4. For agent path: configure outbound network access to BareCount endpoints.
5. Hand BareCount: Tally connection details (host:port) plus chosen bridge credentials.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'tally_prime'`
- `bridge_method: 'vpn' | 'agent' | 'middleware'`
- `tally_host`, `tally_port`
- `auth.method: 'tally_user' | 'agent_token' | 'middleware_credentials'`
- `auth.credential_ref`

Smoke test: simple TDL request fetching `EXPORT REPORT 'List of Companies'`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **TDL-based XML / JSON executor** — no executor for the Tally HTTP server in the readiness baseline.
2. **BareCount Tally Bridge agent** — Windows service architecture, outbound-tunnel design, packaging. Significant build.
3. **Delta strategy without `lastModifiedDateTime`** — voucher-number high-water plus reconciliation.
4. **Bridge security model** — agent credential issuance, rotation, revocation.
5. **TDL knowledge** — Tally's "TDL" templating model is its own language; the executor must serialise / parse correctly.
6. **Voucher type customisation** — customers commonly add custom voucher types; the catalogue must auto-discover.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Tally Prime Help — Integration | https://help.tallysolutions.com/integration-with-tallyprime/ |
| Tally ODBC | https://help.tallysolutions.com/article/Connect/integration/odbc.htm |
| TDL Reference | https://help.tallysolutions.com/article/TDL/Welcome.htm |
| Predecessor — legacy v2 archive Tally Prime reference | legacy-v2/reference/sources/tally-prime.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
