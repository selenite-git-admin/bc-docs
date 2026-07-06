---
uid: SRC-b4c92d
slug: sap-ecc
title: "SAP ECC"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
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
supersedes: legacy-v2/reference/sources/sap-ecc.md
---

# SAP ECC

This page records BareCount's source-admission posture for SAP ECC. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `shape_tested`.

What this means concretely:

- The OData V2 executor (`bc-core/src/boundary/reader-runtime/executors/sap-odata-v2.executor.ts`) has been validated against the BareCount internal SAP ECC simulator at `bc-sdg` port 6100, which mimics ECC table-grain OData V2 protocol shapes (`/Date(epoch)/` timestamps, `__metadata` decoration, `$skiptoken` pagination, CSRF token flow). Memory references internal simulator AR-record coverage admitted from the simulator.
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

OData V2 for Gateway-published services (V4 not generally available on classic ECC). JSON or XML payloads. `$top`/`$skip` pagination, `$inlinecount` for totals, `$filter` for incremental loads, CSRF token flow.

The V2 executor (`SapOdataV2Executor`) handles:

1. CSRF token fetch (`x-csrf-token: Fetch`) and echo on subsequent requests.
2. Paginated query loop with configurable batch size; auto-stops at 100 pages as a safety cap.
3. `$inlinecount=allpages` on the first page for totals.
4. SAP-specific `/Date(epochMs)/` decoding to ISO timestamps; `__metadata` and `__deferred` stripped.
5. SAP-specific headers (`sap-client`, `sap-language`, `Accept: application/json`).

### 6.2 Authentication

Supported in the readiness baseline via `CredentialResolverService`:

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

**No SAP ECC entity has been verified first-hand against a real customer instance in the reference baseline.**

Internal simulator coverage exists (internal simulator AR-record coverage via `bc-sdg`), but the simulator is not a real customer source under D384. This section will list real-tenant verifications when they occur.

---

## 10. Known Gaps

1. **Real-tenant Gateway OData** end-to-end — not yet exercised.
2. **mTLS / X.509 client cert** auth — not yet a first-class method on `ResolvedCredentials`.
3. **BTP Cloud Connector** integration for ECC-on-prem.
4. **Adaptive throttle / backoff** for Gateway rate limits.
5. **Delta strategies beyond `$filter` by date** — would require per-entity decision (no OData V4 `$delta` support on classic ECC).
6. **ABAP Transport runbook** — needs documented onboarding playbook (current text is procedural sketch).
7. **Catalogue of which ECC entities have S/4HANA Public OData equivalents** — informs migration conversations with prospective customers.

---

## 11. References

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
| Predecessor — legacy v2 archive SAP ECC reference | legacy-v2/reference/sources/sap-ecc.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
