---
uid: SRC-b4c92d
slug: sap-ecc
title: "SAP ECC"
description: "Sanctioned-path admission of SAP ECC data via Gateway-published OData or customer ABAP transport, under SAP API Policy v.4/2026. RFC and ODP banned."
type: source-systems
status: published
domain: enterprise-erp
subdomain: sap
focus: governance
proof_status: shape_tested
last_verified_at: 2026-04-28
official_docs_url: https://help.sap.com/docs/SAP_ERP
reader_flavors:
  - sap-ecc-odata-v2
admission_contract_versions: []
governing_adrs:
  - DEC-d2cdb9   # D384 — SAP API admission stance
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2-archive/docs/reference/sources/sap-ecc.md
---

# SAP ECC

SAP ECC (ERP Central Component) is SAP's classic on-premise ERP system. Unlike S/4HANA, ECC predates the CDS-view API layer and historically exposed data through transparent tables, BAPIs, RFCs, and DataSources. Under **SAP API Policy v.4/2026** (DEC-d2cdb9 / D384) the only sanctioned access paths for BareCount are Gateway-published OData services (when available) and customer-initiated ABAP transport runs (Indirect Static Read). RFC and ODP RFC paths are explicitly prohibited.

SAP mainstream maintenance for ECC ends in **2027**; extended maintenance is available through **2030** at additional cost. Customers are expected to migrate to S/4HANA. BareCount supports ECC for the remaining maintenance window and recommends planning the S/4HANA migration path.

This page is governed by **DEC-d2cdb9 (D384)** — the same SAP API admission stance applies to ECC as to S/4HANA.

---

## 1. Proof Status

**`shape_tested`** as of 2026-04-28.

What this means concretely:

- The OData V2 executor (`bc-core/src/boundary/reader-runtime/executors/sap-odata-v2.executor.ts`) has been validated against the BareCount internal SAP ECC simulator at `bc-sdg` port 6100, which mimics ECC table-grain OData V2 protocol shapes (`/Date(epoch)/` timestamps, `__metadata` decoration, `$skiptoken` pagination, CSRF token flow). Memory references 1,368 AR records admitted from the simulator.
- **Zero validation against a real SAP ECC tenant.** No customer Gateway service has been exercised; no customer ABAP transport run has produced admissions through the BareCount chain.
- Until a real ECC instance has produced metric snapshots through the chain end-to-end, **no external "we work with SAP ECC" claim may be made.**

`proof_status` will be promoted to `first_hand_proven` only after §9 Verified Coverage gains an entry with a real (anonymised) customer instance and date.

---

## 2. Reader Flavor Binding

| Flavor | Target | Executor | AC version |
|---|---|---|---|
| `sap-ecc-odata-v2` | SAP ECC with SAP Gateway Foundation activated | `SapOdataV2Executor` | — (not yet built for real ECC) |

The simulator-shaped reader binding used in current testing is the same flavor configured against the bc-sdg simulator endpoint. The first real ECC tenant will require a real Communication Arrangement-equivalent setup on the customer's Gateway.

---

## 3. What BareCount Admits

### 3.1 Metadata

Classic ABAP Dictionary table field definitions: field names, data types (`CHAR`, `CURR`, `DEC`, `DATS`, etc.), key indicators, domain references, foreign-key relationships. Stored as Tier 5/6 entries in the Source Catalog.

### 3.2 Business data

Posted business records from ECC transparent tables — accounting documents (BKPF/BSEG/BSID/BSAD), purchase orders (EKKO/EKPO), material masters (MARA/MARC/MARD), goods movements (MSEG/MKPF), customer and vendor masters (KNA1/KNB1, LFA1/LFB1). Admitted via Gateway-published OData when activated, or as JSON output of a customer-initiated ABAP report run.

ECC differs from S/4HANA in that it has **no CDS view layer**. The "object" we observe is the underlying transparent table (or its view), not a semantic CDS model. Canonical resolution does the same job either way; only the binding differs.

---

## 4. Legal & Licensing

### 4.1 SAP API Policy v.4/2026 (governing)

ECC falls under the same policy as S/4HANA. Specifically:

- **Sanctioned**: Gateway-published OData services exposed by the customer's SAP_GWFND add-on. These are "Published APIs" in the policy sense when listed on SAP Business Accelerator Hub or in the customer's own SEGW service catalogue.
- **Sanctioned**: Customer-initiated ABAP report execution under their own licensed user — the long-standing **Indirect Static Read** exemption.
- **Sanctioned**: BTP Integration Suite iFlow path for customers who run BTP alongside ECC.
- **Banned**: ODP RFC modules — SAP Note 3255746 explicitly prohibits third-party use, and this Note pre-dates Policy v.4/2026.
- **Banned**: undocumented OData services or non-Gateway direct table reads.
- **Banned**: scraping or screen-reading the customer's ECC system.

### 4.2 SAP Digital Access (write-back)

Same nine-document-type framework as S/4HANA. BareCount does not write to ECC today; if/when an Action Engine creates SAP documents, full Digital Access licensing applies and must be in the customer contract before activation.

### 4.3 Named User vs Communication User

ECC has the same Named User vs Communication User distinction. External integrations must run under a Communication User (machine identity), not a Named User (human licence). The classic SAP audit risk applies to misconfigured ECC integrations.

### 4.4 Maintenance timeline

- Mainstream maintenance: ends 2027.
- Extended maintenance: through 2030 (additional cost).
- After 2030: customer is on S/4HANA or unsupported.

This bounds how much engineering BareCount should invest in ECC-specific reader paths. The simulator path covers learning and demos; substantive customer engagements should evaluate the customer's S/4HANA migration plan first.

---

## 5. Commercial

### 5.1 Customer access models (post-Policy v.4/2026)

| Model | Path | Cost (SAP) | Volume suitability |
|---|---|---|---|
| **Gateway-published OData** | ECC + SAP_GWFND add-on | Included if customer has Gateway Foundation; not all ECC systems do | Low–medium realtime |
| **Customer ABAP Transport (Indirect Static Read)** | ECC, no add-on required | Zero — customer runs report under own Named User | High (direct table read) |
| **BTP iFlow** | ECC + BTP subscription | Included in BTP if customer has it | High; OHD/ODQ paths still restricted under SAP Note 3255746 |

The previous v2 framing of "Named User Consultant Access" is dropped — wrong-model under Communication User rules.

### 5.2 Volume considerations

| Scenario | Typical volume | Recommended model |
|---|---|---|
| Initial historical load | 1M–100M records | ABAP Transport (one-shot full export) |
| Daily delta admission | 1K–100K/day | Gateway OData or daily ABAP Transport run |
| Realtime/near-realtime | 100–10K/hour | Gateway OData polling |

---

## 6. Technical

### 6.1 Protocol

OData V2 for Gateway-published services (V4 not generally available on classic ECC). JSON or XML payloads. `$top`/`$skip` pagination, `$inlinecount` for totals, `$filter` for incremental loads, CSRF token flow.

The V2 executor (`SapOdataV2Executor`) handles:

1. CSRF token fetch (`x-csrf-token: Fetch`) and echo on subsequent requests.
2. Paginated query loop with configurable batch size; auto-stops at 100 pages as a safety cap.
3. `$inlinecount=allpages` on the first page for totals.
4. SAP-specific `/Date(epochMs)/` decoding to ISO timestamps; `__metadata` and `__deferred` stripped.
5. SAP-specific headers (`sap-client`, `sap-language`, `Accept: application/json`).

### 6.2 Authentication

Supported today via `CredentialResolverService`:

- **Basic Auth** (technical user + password over TLS) — common for on-prem.
- **Bearer token** (OAuth 2.0) — when an OAuth proxy is configured.

Gap: mTLS / X.509 client cert not yet a first-class method on `ResolvedCredentials`.

### 6.3 Throughput

ECC Gateway services have per-system rate limits configurable by Basis. The executor does not yet implement adaptive backoff. Listed in §10.

### 6.4 Delta strategy

- `$filter` by date field (`BUDAT`, `CPUDT`, `LAEDA`).
- DataSource ODP-based delta is **banned** under SAP Note 3255746 — do not use.
- ABAP Transport export can carry a delta flag if the report logic implements it.

### 6.5 Schema discovery

OData `$metadata` document at the service root yields entity types and key fields. Public catalogues (`leanx.eu`, `se80.co.uk`) cover ECC table definitions for catalogue seed without touching a customer system.

### 6.6 Network plumbing

- Gateway services: HTTPS direct, IP-allowlist as needed.
- ABAP Transport: customer runs `ZBCNT_META_EXPORT` and uploads JSON via the agreed channel — no live BareCount-to-ECC connection required for this path.

---

## 7. Customer-Side Onboarding

### 7.1 Gateway-published OData path

1. **Verify Gateway availability.** SAP Gateway Foundation (`SAP_GWFND`) must be installed; this is **not** universal on ECC. Check with Basis.
2. **Activate the OData service** in `/IWFND/MAINT_SERVICE` for the entity BareCount needs (e.g. a custom CDS-View-equivalent or a SEGW-built service over the relevant tables).
3. **Create a technical (Communication-class) user** with read-only authorisations on the activated services.
4. **Choose network path**: direct VPN/IP allowlist, or BTP Cloud Connector if available.
5. **Hand BareCount**: endpoint URL, credentials, list of activated services.

### 7.2 ABAP Transport path

1. Receive the BareCount-published transport (`ZBCNT_META_EXPORT` or business-data variant).
2. Import via STMS into a development client; promote to production after Basis review.
3. Run the report under a customer-licensed user — Indirect Static Read.
4. Send the JSON output to BareCount via the agreed channel (S3 dropbox, SFTP, signed URL).

---

## 8. BareCount-Side Onboarding

### 8.1 Connection profile

Per-tenant connection profile in `tbc_{slug}_dev`:

- `system_type_code: 'sap_ecc'`
- `endpoint_url`
- `auth.method: 'basic' | 'bearer'`
- `auth.credential_ref` — reference to credential in external store; secrets never in DB.
- `sap_client` (e.g. `100`)
- `sap_language` (default `'EN'`)
- `gateway_services[]` — list of activated services we may call.

### 8.2 Smoke test

Same as S/4HANA: hit `/$metadata` then one entity with `$top=1` before activating the reader.

---

## 9. Verified Coverage

**No SAP ECC entity has been verified first-hand against a real customer instance as of 2026-04-28.**

Internal simulator coverage exists (1,368 AR records via `bc-sdg` port 6100), but the simulator is not a real customer source under D384. This section will list real-tenant verifications when they occur.

---

## 10. Source-System Semantics: Sign Handling

SAP ECC sub-ledger tables store amounts **unsigned**. The debit/credit direction is carried by a separate indicator field. The resolver must apply sign correction at the canonical boundary to produce correctly-signed Canonical Objects.

| Table family | Amount semantics | Sign indicator | Credit value |
|---|---|---|---|
| BSID / BSAD (AR open/cleared) | Unsigned (`WRBTR`, `DMBTR`) | `SHKZG` | `H` |
| BSIK / BSAK (AP open/cleared) | Unsigned (`WRBTR`, `DMBTR`) | `SHKZG` | `H` |
| BSEG (document line items) | Unsigned (`WRBTR`, `DMBTR`) | `SHKZG` | `H` |
| ACDOCA (Universal Journal) | **Signed** (`HSL`, `TSL`) | None needed | — |

**SHKZG values:** `S` = debit (Soll), `H` = credit (Haben). When SHKZG = `H`, amount fields must be negated at the canonical boundary so that sums compute correctly (credits reduce totals).

**OC declaration pattern.** The OC declares the sign indicator via a field_mapping with `role: "sign_indicator"` and `transform_params: { "credit_value": "H" }`. The CCv2 resolver consumes this declaration and negates `representation_term: "amount"` fields on credit-side rows. The sign indicator field is not projected to the CO — it is resolver metadata.

**Impact on metrics.** Without sign correction, all amount metrics that sum across debit and credit rows (receivables, payables, revenue) silently overstate because credit amounts add instead of subtract. This is invisible when all rows are debits (e.g. open invoices only) but breaks as soon as credit memos, payments, or clearing entries appear.

**Currency considerations.** ECC sub-ledger tables carry both document currency (`WRBTR`, `WAERS`) and local currency (`DMBTR`, `HWAER`). When the document currency differs from local currency, `DMBTR` is independently rounded per line — the sum of line-level `DMBTR` values may differ from the header-level conversion of the document total by ±0.01 per document due to rounding. This is a known SAP characteristic, not a BareCount defect.

---

## 11. Known Gaps

1. **Real-tenant Gateway OData** end-to-end — not yet exercised.
2. **mTLS / X.509 client cert** auth — not yet a first-class method on `ResolvedCredentials`.
3. **BTP Cloud Connector** integration for ECC-on-prem.
4. **Adaptive throttle / backoff** for Gateway rate limits.
5. **Delta strategies beyond `$filter` by date** — would require per-entity decision (no OData V4 `$delta` support on classic ECC).
6. **ABAP Transport runbook** — needs documented onboarding playbook (current text is procedural sketch).
7. **Catalogue of which ECC entities have S/4HANA Public OData equivalents** — informs migration conversations with prospective customers.

---

## 12. References

| Resource | Link |
|---|---|
| ADR — SAP API admission stance (D384) | [ADR-d2cdb9](../../governance/adrs/ADR-d2cdb9.md) |
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Companion source page | [SAP S/4HANA](sap-s4hana.md) |
| Companion appendix — SAP licensing & catalogue rules | [sap-licensing-reference.md](sap-licensing-reference.md) |
| SAP API Policy v.4/2026 | https://www.sap.com/docs/download/2026/04/dce9aee4-497f-0010-bca6-c68f7e60039b.pdf |
| SAP Note 3255746 (ODP RFC ban) | https://me.sap.com/notes/3255746 |
| SAP ERP Help Portal | https://help.sap.com/docs/SAP_ERP |
| SAP Gateway Foundation | https://help.sap.com/docs/SAP_NETWEAVER_750/68bf513362174d54b58cddec28794093 |
| leanx.eu SAP table reference | https://leanx.eu/en/sap/table/ |
| Predecessor — legacy v2 SAP ECC reference | legacy-v2-archive/docs/reference/sources/sap-ecc.md |

## 13. Changelog

- **2026-07-07** — added §10 Source-System Semantics: Sign Handling. Documents SHKZG debit/credit indicator on sub-ledger tables (BSID/BSAD/BSIK/BSAK/BSEG), the `role: "sign_indicator"` OC pattern, and currency rounding characteristics. Per TSK-04e6df ERP pitfall remediation.
- **2026-04-28** — initial v3 page. Supersedes `legacy-v2-archive/docs/reference/sources/sap-ecc.md`. Reconciled against **DEC-d2cdb9 (D384)**: previous v2 framing of "OData = gray area" replaced with "Gateway-published OData = sanctioned." Dropped Named User access model. `proof_status: shape_tested` based on bc-sdg V2 simulator coverage. Maintenance-window framing tightened (2027 mainstream, 2030 extended).
