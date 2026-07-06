---
uid: SRC-c4d9e6
slug: sap-bw4hana
title: "SAP BW/4HANA"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: draft
domain: enterprise-erp
subdomain: sap
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://help.sap.com/docs/SAP_BW4HANA
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-d2cdb9   # D384 — SAP API admission stance
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/sap-bw4hana.md
---

# SAP BW/4HANA

This page records BareCount's source-admission posture for SAP BW/4HANA. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

What this means concretely:

- Architecture and access models documented; no code path built.
- No simulator coverage for BW objects (`bc-sdg` mimics ECC table-grain shapes, not BW ADSO shapes).
- No reader executor for BW protocols (OHD, BW OData, HANA SQL, InA).
- No customer engagement on BW.

Until at least one BW path is shape-tested or a real customer engagement begins, **no claim about BW/4HANA capability is permitted externally.**

---

## 2. Reader Flavor Binding

Empty list. No flavor exists in the readiness baseline. Candidate flavors when scoped:

- `sap-bw-ohd-export` — admit from OHD flat-file or database-table output.
- `sap-bw-odata` — admit via BW Analysis Service OData V4.
- `sap-bw-hana-sql` — direct SQL against ADSO active table or Calculation View (subject to HANA licence — see §4).
- `sap-bw-abap-transport` — customer-initiated report under Indirect Static Read.

---

## 3. What BareCount Would Admit

### 3.1 Metadata

InfoObject definitions (characteristics, key figures), InfoProvider field structures (ADSO inbound/active/change-log shapes, CompositeProvider constituent references), HANA Calculation View columns, BW Query metadata (optional).

### 3.2 Business data

ADSO active-table records (the materialised, deduplicated data — the primary read target), CompositeProvider query results, HANA Calculation View results, OHD exports.

**Key difference from S/4HANA:** BW data is post-transformation. BareCount admits BW data for **analytical observation**, not raw transaction admission. The data has already passed customer transformation rules and may consolidate multiple source systems. Canonical resolution must account for this — a BW-admitted observation is downstream of the customer's own analytical model.

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

### 6.1 Public catalogue (limited)

Unlike S/4HANA (Cloudification Repository, CDS Finder, se80.co.uk), no equivalent public sources exist for BW objects:

- No Cloudification Repository equivalent for BW objects.
- `leanx.eu` covers SAP tables but not BW InfoProvider structures.
- `se80.co.uk` has some BW-related tables but not InfoProvider definitions.
- SAP's API documentation for BW/4HANA is gated behind support credentials.

### 6.2 Customer-specific metadata

BW/4HANA metadata extraction would require reading:

| Table / Object | Content |
|---|---|
| `RSDCUBE`, `RSDODSO` | InfoProvider definitions (cubes and ADSOs) |
| `RSDCHA`, `RSDKYF` | InfoObject characteristics and key figures |
| `RSDIOBJ` | InfoObject catalog with attributes and properties |
| `RSBSPOKE`, `RSBSPOKEFLD` | Open Hub Destination definitions and field mappings |
| `INFORMATION_SCHEMA` (HANA) | Calculation View metadata (columns, parameters, hierarchies) |
| `RSCRM_DATAMOD` | Data model definitions for mixed scenarios |

### 6.3 Business data admission mechanisms

| Mechanism | Description | Volume |
|---|---|---|
| **Open Hub Destination (OHD)** | Customer configures OHD to export to file or DB table; BareCount admits the output. | High (designed for bulk) |
| **ABAP Report** | Same transport approach; report reads ADSO active table and exports JSON. | High (direct table read) |
| **BW Analysis Service OData V4** | InfoProviders exposed as OData via BW Gateway. | Medium (filtered, moderate volume) |
| **HANA SQL** | Direct SQL to Calculation Views or ADSO active tables. | High (subject to HANA licensing) |
| **InA Protocol** | Information Access protocol used by SAC. | Medium (analytics-oriented) |

### 6.4 ADSO architecture (for context)

The Advanced DataStore Object (ADSO) is the primary storage object in BW/4HANA. Each ADSO has three internal tables:

- **Inbound** — staging area before activation.
- **Active** — current deduplicated data; primary read target.
- **Change log** — delta records for downstream consumption.

BareCount would primarily read from active for full loads and change log for delta scenarios.

---

## 7. Customer-Side Onboarding

### 7.1 OHD path (recommended)

1. Customer Basis configures an Open Hub Destination targeting the InfoProvider/ADSO BareCount needs.
2. OHD exports to a destination flat file or database table on a schedule.
3. BareCount picks up the output via SFTP/S3/agreed channel.
4. No live BareCount-to-BW connection required.

### 7.2 BW Analysis Service OData path

1. Customer activates the BW OData service for the InfoProvider.
2. Customer creates a Communication-class user with read-only authorisation.
3. BareCount calls the service via the V4 executor (when the executor is built — in the readiness baseline only V2 exists).

### 7.3 ABAP Transport path

Same pattern as ECC: import transport, run report under licensed user, send JSON.

---

## 8. BareCount-Side Onboarding

Connection profile shape: same as ECC with `system_type_code: 'sap_bw4hana'`. Reader flavor selection deferred until at least one path is built.

Smoke test pattern: same as S/4HANA — hit `$metadata` (or OHD output health), then a single record fetch.

---

## 9. Verified Coverage

**Nothing.** No BW/4HANA path has been built or validated.

---

## 10. Known Gaps

1. **No reader executor** for any BW path. V4 OData executor exists for S/4HANA shape but BW Analysis Service OData has its own peculiarities (InfoProvider-specific dimensions, hierarchy traversal) that need testing.
2. **No simulator** for BW objects.
3. **No HANA SQL connector** in BareCount.
4. **No InA Protocol implementation**.
5. **No public catalogue source** for BW objects — catalogue seed for a customer requires their own ABAP transport run.
6. **HANA licence implications** for direct SQL access not yet legally reviewed across customer scenarios.
7. **TSK-3c6964** investigation is the parent task — pull and revisit when first BW prospect signs.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — SAP API admission stance (D384) | [ADR-d2cdb9](../../governance/adrs/ADR-d2cdb9.md) |
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Companion appendix — SAP licensing & catalogue rules | [sap-licensing-reference.md](sap-licensing-reference.md) |
| SAP BW/4HANA Help Portal | https://help.sap.com/docs/SAP_BW4HANA |
| SAP BW/4HANA product page | https://www.sap.com/products/technology-platform/bw4hana.html |
| ADSO documentation | https://help.sap.com/docs/SAP_BW4HANA/107a6e8a38b74ede94c833ca3c6b7957 |
| SAP Note 3255746 (ODP RFC ban) | https://me.sap.com/notes/3255746 |
| Predecessor — legacy v2 archive SAP BW/4HANA reference | legacy-v2/reference/sources/sap-bw4hana.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
