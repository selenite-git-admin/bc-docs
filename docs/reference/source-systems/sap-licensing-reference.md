---
uid: SRC-saplic1
slug: sap-licensing-reference
title: "SAP Licensing & Public Catalogue Reference"
description: "SAP source-admission appendix. Vendor legal and catalogue facts must be verified during source onboarding."
type: source-systems
status: verification_required
domain: enterprise-erp
subdomain: sap
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.sap.com/about/agreements/policies/digital-access.html
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-d2cdb9   # D384 — SAP API admission stance
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/sap/
---

# SAP Licensing & Public Catalogue Reference

> Verification note: This appendix is retained for SAP vendor-context orientation. It is not current SAP licensing advice. Verify SAP policy, official catalogue status, and customer contract terms during source onboarding; DEC-d2cdb9 remains BareCount's admission authority.

This page consolidates the SAP-side reference material that informs the SAP source pages — [sap-s4hana](sap-s4hana.md), [sap-ecc](sap-ecc/index.md), [sap-bw4hana](sap-bw4hana.md), [sap-successfactors](sap-successfactors.md), [sap-dm](sap-dm.md). It is **appendix material**: it explains what SAP's own rules say so BareCount's onboarding playbook can reference the correct framing without reproducing it on every source page.

The authoritative position on BareCount's SAP admission stance is **DEC-d2cdb9 (D384)** — read that first if you want the actionable rule. This page provides the supporting context.

---

## 1. SAP API Policy v.4/2026 — short pointer

SAP published API Policy v.4/2026 in April 2026. It restricts SAP system access to **Published APIs only** (those listed on SAP Business Accelerator Hub or in official product documentation) and explicitly prohibits use of internal, private, or non-published APIs. BareCount's stance is recorded in **[DEC-d2cdb9 (D384)](../../governance/adrs/ADR-d2cdb9.md)** — admit only via sanctioned paths (`sap-s4-cloud-odata`, `sap-s4-onprem-cds`, `sap-bdc-connect`). Sources for the policy text itself are linked in §7.

---

## 2. Indirect Access

### 2.1 What it is

Indirect access occurs when users or systems interact with SAP software through a **non-SAP intermediary** rather than directly through SAP's own user interface. This includes:

- Third-party applications reading or writing SAP data.
- Bots, sensors, IoT devices creating SAP documents.
- Middleware / integration platforms connecting to SAP.
- Custom portals or apps built on SAP data.

### 2.2 SAP's "Use" definition

> "Use" means to activate the processing capabilities of the Software, load, execute, access, employ the Software, or display information resulting from such capabilities. Use may occur by way of an interface delivered with or as a part of the Software, a Customer or third-party interface, or another intermediary system.

This broad definition explicitly covers programmatic access by third-party systems like BareCount. It is the legal foundation under which SAP measures indirect access in audits.

### 2.3 Risk categories under SAP's framework

| Risk | Examples |
|---|---|
| **High** | RFC extraction by third-party tools (banned by SAP Note 3255746); unlicensed programmatic access by external systems; Named User sharing/multiplexing; automated document creation without Digital Access licensing |
| **Medium** | OData access by external systems (defensible if read-only, but the broad "Use" definition creates ambiguity unless operating under a sanctioned Communication Arrangement); API-based metadata extraction (gray area absent a sanctioned path) |
| **Low** | Customer-initiated data exports (Indirect Static Read); Integration Suite iFlows running inside the customer's licensed SAP; self-service ABAP reports run by licensed customer users |

Under **D384**, BareCount routes admission only through the High/Medium → Low side of this table — the sanctioned paths in the policy.

### 2.4 Indirect Static Read exemption

SAP exempts read-only data exports as "Indirect Static Read" — but only when:

1. **Initiated by a customer's licensed SAP user** (not by a third-party machine).
2. **No further processing triggered** in SAP.
3. **Data flows one-way OUT** of SAP.

For BareCount this means the customer ABAP-transport path (customer runs `ZBCNT_*` report under their own user, sends JSON to BareCount) is the only model that qualifies. Direct BareCount-to-SAP API calls do not, since BareCount initiates them.

### 2.5 How SAP measures indirect access

The SAP audit process:

1. SAP requests tables from the customer's SAP system.
2. Creates a register of all interfaces connecting to/from the SAP core.
3. Analyzes extracted data + interviews system owners.
4. Identifies whether feeds originate from SAP or non-SAP systems.
5. Determines presence of users not covered by Professional / Limited / equivalent named-user licences.

**SAP Passport Tool** is SAP's official measurement tool — covers SAP ABAP, NetWeaver Java, SAP Cloud Platform (Neo), UI5, HANA. It differentiates SAP-created documents from external documents. Note that SAP Passport serves SAP's interests; independent measurement is recommended for customers preparing for an audit.

---

## 3. Digital Access (document-based licensing)

### 3.1 What it is

SAP introduced Digital Access in 2018 as an alternative to user-based licensing for indirect scenarios. Instead of counting named users, the model charges based on **creation** of nine specific document types triggered by external systems.

### 3.2 The nine charged document types

1. Sales Orders
2. Purchase Orders
3. Financial Documents (Journal Entries)
4. Goods Movements (Material Documents)
5. Service Orders
6. Service Confirmations
7. Manufacturing Orders (Production Orders)
8. Quality Inspection Lots
9. Supplier Invoices

### 3.3 Key exemption — reads, updates, deletes

**READS, UPDATES, and DELETES are NOT charged** under Digital Access. Only CREATION of the nine document types triggers licensing.

This is the foundation of BareCount's commercial position: BareCount **only reads** — admission is a read operation. No Digital Access charges apply to BareCount's observation work.

If BareCount's Action Engine ever creates SAP documents (out of scope today), full Digital Access licensing applies and must be in the customer contract before activation.

### 3.4 Pricing options

| Model | Detail |
|---|---|
| Per-document volume packs | Charged per document created |
| Unlimited flat-fee licences | Fixed fee regardless of volume |
| DAAP (Digital Access Adoption Program) | Up to 90% discount when converting from classic indirect access — incentive to switch licensing models |

### 3.5 What does NOT count as Digital Access

- ABAP extensions made by the customer / partner — internal call, not external.
- Logging into a client app — counts as logging into the digital core with a licensed user.
- Documents created by a licensed SAP user through direct interaction — direct, not indirect.
- Read-only data access (queries, reports, exports) — with caveats noted in §2.3.

---

## 4. SAP Note 3255746 — RFC extraction ban

### 4.1 The note

SAP issued **Note 3255746** on 2 February 2024 explicitly prohibiting the use of RFC (Remote Function Call) modules in the **Operational Data Provisioning (ODP) Data Replication API**. The restriction applies to customer and third-party applications extracting ABAP data from SAP systems — whether on-premise or cloud-based. RFC modules are designated for "SAP-internal applications only" and can be modified without notice.

### 4.2 Key restrictions

- Strict usage prohibitions for external data extraction via RFC.
- SAP reserves the right to implement technical measures restricting unauthorised RFC use.
- SAP reserves the right to conduct audits.
- SAP disclaims responsibility for issues arising from non-compliant usage — problems are "entirely at the risk of the customer."
- Existing integrations relying on RFC are subject to disruption.

### 4.3 Underlying rationale

- Security vulnerabilities from improperly guarded RFC interfaces.
- Regulatory compliance needs (GDPR, HIPAA, SOX).
- Excessive exposure risk from broad system access permissions.
- Shift toward modern APIs (REST, OData).
- System performance concerns from high RFC call volumes.

### 4.4 SAP-certified alternatives

Under D384 BareCount uses the following sanctioned paths instead of RFC-based extraction:

| Path | When |
|---|---|
| **Published OData APIs (Business Accelerator Hub)** | S/4HANA Cloud (Public + Private Edition); preferred for new tenants |
| **CDS-view Published APIs** | S/4HANA on-prem with CDS released views activated |
| **BDC Connect** | Tenants on SAP Business Data Cloud (separate partnership posture) |
| **Customer ABAP Transport (Indirect Static Read)** | ECC and on-prem S/4 — customer runs report under their own user |
| **BTP Integration Suite iFlow** | Customers running BTP alongside ECC or S/4 |

### 4.5 BareCount rule

BareCount **never** uses RFC for data extraction from customer SAP systems. The internal bc-sdg ECC simulator at port 6100 emulates RFC/table-grain shapes for **internal testing only** — it is not a production reader path.

---

## 5. SAP user types

### 5.1 The five user types

| Type | Logon access | Password expiration | Password change | SSO support |
|---|---|---|---|---|
| Dialog | GUI/RFC | Yes | Yes | Yes |
| System | RFC only | No | No | No |
| Service | GUI/RFC | No | No | No |
| Communications | RFC | Yes | Yes | Yes |
| Reference | None | N/A | N/A | N/A |

### 5.2 Key distinctions

- **System** is appropriate for automated machine connections (background jobs, system-to-system) — no GUI, no password expiration. Common for service accounts under sanctioned API paths.
- **Communications** is for an end user (with password change capability) who also connects by RFC. Activating password-expiration policies can break RFC connections unexpectedly.
- **Service** users can work in the GUI without password flow; suitable for emergency admin access. Does not generate SSO logon tickets.
- **Reference** users enable role inheritance via the user profile's Roles tab; can complicate authorisation traceability.
- **Dialog** is for human interactive use; not appropriate for BareCount machine access.

### 5.3 BareCount-side guidance

For customer-granted SAP access under sanctioned paths:

- **Communication User** (the modern S/4HANA Cloud equivalent of "System" or "Communications" — created in the Communication Arrangement onboarding flow) is the right service identity. See [sap-s4hana §7](sap-s4hana.md) for the onboarding sequence.
- **System** user type is the on-prem equivalent for ECC + S/4 on-prem.
- **Never use Dialog or Service** — these are for human interactive use.

Misclassification (e.g. running BareCount admission under a customer's Named User credential) is a customer-side licensing violation. BareCount onboarding must surface this.

---

## 6. Public catalogue sources for SAP metadata

BareCount seeds its SAP source catalogue from **public sources** — no customer system contact required. This is essential for pre-population: a prospect's first interaction with BareCount can show what BareCount knows about S/4HANA before they grant any system access.

### 6.1 SAP ABAP ATC Cloudification Repository (GitHub)

Open-source repository maintained by SAP that lists released and classic APIs for SAP Cloud ERP. Apache 2.0 licence. Updated regularly via GitHub Actions.

| Aspect | Detail |
|---|---|
| Repository | `https://github.com/SAP/abap-atc-cr-cv-s4hc` |
| Files | `objectReleaseInfoLatest.json` (Cloud public), `objectReleaseInfo_PCELatest.json` (Cloud Private), `objectClassifications_SAP.json` (ATC check 3565942) |
| Coverage | 44,541 total entries; 7,927 DDLS (CDS view definitions); 7,626 released CDS views; 6,801 I_ interface views; 242 C_ consumption views |
| Module distribution (I_ views) | FI 1,094; SD 645; MM 629; PP 493; LO 434; PM 293; QM 206 |
| Format | JSON (per-entry: `tadirObject`, `tadirObjName`, `objectType`, `softwareComponent`, `applicationComponent`, `state`, `successorClassification`) |

**Limitation: names + metadata only — NO field definitions.** Must be combined with CDS Finder Excel or `se80.co.uk` for field-level data.

Direct download URLs:
- Public Cloud Latest: `https://raw.githubusercontent.com/SAP/abap-atc-cr-cv-s4hc/main/src/objectReleaseInfoLatest.json`
- Private Cloud Latest: `https://raw.githubusercontent.com/SAP/abap-atc-cr-cv-s4hc/main/src/objectReleaseInfo_PCELatest.json`

### 6.2 CDS Finder Excel

SAP-published Excel sheet that maps **classic SAP tables to released CDS views** at field level.

| Aspect | Detail |
|---|---|
| Source | SAP community blog post (linked in §7) |
| Password | `CDSFinder@2025` |
| Source system | SAP S/4HANA 2023 FPS01 |
| Row count | **106,946 field-level mapping rows** |
| Scope | C1-released CDS views only |
| Coverage | ~2,000 tables, varying mapping quality |
| Default filter | Tables with no release state → only C1-released CDS views |

Mapping methodology: uses class `cl_dd_ddl_field_tracker` to derive base-table relationships for every field of every CDS view. Result is a custom table of all relations between classic tables/fields and existing CDS views.

**Important disclaimer (SAP's):** The mapping is a **starting point, not a guarantee of succession**. CDS views may have fixed WHERE conditions limiting scope, missing columns vs the base table, or specialisation (e.g. customer-only filters). Verify per use case.

Example mapping:

| CDS Entity | CDS Field | Base Table | Base Table Field |
|---|---|---|---|
| `I_STORAGELOCATION` | `DIVISION` | `T001L` | `SPART` |

For T001L, `I_StorageLocation` maps 9 fields and is released for ABAP Cloud usage.

### 6.3 CDS extractor discovery (per-customer)

For customer-side onboarding (not catalogue seed) — discover which CDS extractors are available in the customer's S/4HANA system:

| Step | Action |
|---|---|
| 1 | CDS view `I_DataExtractionEnabledView` (DDIC name `IXTRCTNENBLDVW`) in SE16. Filter for released vs unreleased; CDC-enabled vs full-load only. **Warning:** column 1 (extractor name) is case-sensitive; SE16 may upper-case search patterns and miss valid results. |
| 2 | Find DDIC name — design-time CDS name ≠ runtime DDIC name. Mapping in `RSODPABAPCDSVIEW`. Example: `C_PurchaseOrderItemDEX` → `CMMPOITMDX`. |
| 3 | Analyze in ABAP Dictionary (SE11). Annotation tables: `DDHEADANNO` (header), `DDCDS_ELMNT_ANNO` (element/field). |
| 4 | Fiori View Browser (`/n/UI2/FLP`, role `SAP_BR_Analytics_Specialist`). Filter for extraction-enabled views; download to Excel. |
| 5 | ADT Dependency Analyzer (Eclipse) — disassembles the data model and shows which source SAP tables the extractor reads. |

**CDS extractor growth (per release):**

| Release | Count | Delta-capable |
|---|---|---|
| 2019 | ~500 | ~10% |
| 2020 | ~1,100 | ~10% |
| 2021 | ~1,800 | ~15% |
| 2022 | ~2,400 | ~18% |
| 2023 | ~2,800 | ~20% |
| 2025 | ~4,700 | ~18% |

Only ~18–20% of extractors support CDC (Change Data Capture). Important for incremental data admission planning.

Authorisations: SAP Note 2930269 (CDS extraction authorisations); SAP Note 2855052 (additional CDS extraction authorisations); SAP Note 2433354 (missing Business Content DataSources with ODP framework).

### 6.4 Other public sources

- **`leanx.eu`** — comprehensive SAP table catalogue with field definitions; covers ECC + S/4HANA classic tables.
- **`se80.co.uk`** — SAP table and CDS view definitions with full field details. Cloudflare-protected; may need Playwright for scraping.
- **SAP Business Accelerator Hub** — `https://api.sap.com/` — the canonical catalogue of Published APIs, including OData services per S/4HANA module.

---

## 7. References

| Resource | Link |
|---|---|
| ADR — SAP API admission stance (D384) | [ADR-d2cdb9](../../governance/adrs/ADR-d2cdb9.md) |
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| SAP API Policy v.4/2026 (PDF) | https://www.sap.com/docs/download/2026/04/dce9aee4-497f-0010-bca6-c68f7e60039b.pdf |
| SAP Note 3255746 (ODP RFC ban) | https://me.sap.com/notes/3255746 |
| SAP Digital Access licensing | https://www.sap.com/about/agreements/policies/digital-access.html |
| SAP Note 2930269 — CDS extraction authorisations | https://launchpad.support.sap.com/#/notes/2930269 |
| SAP Note 2855052 — additional CDS extraction authorisations | https://launchpad.support.sap.com/#/notes/2855052 |
| SAP Note 2433354 — missing Business Content DataSources with ODP | https://launchpad.support.sap.com/#/notes/2433354 |
| SAP Cloudification Repository | https://github.com/SAP/abap-atc-cr-cv-s4hc |
| SAP Business Accelerator Hub | https://api.sap.com/ |
| Finding the right CDS extractor (SAP community) | https://community.sap.com/t5/technology-blog-posts-by-sap/finding-the-right-cds-extractor-in-sap-s-4hana/ba-p/13521296 |
| CDS Finder Excel cheat sheet (SAP community) | https://community.sap.com/t5/technology-blog-posts-by-sap/how-to-find-a-cds-view-for-a-classic-table-in-abap-cheat-sheet/ba-p/13901500 |
| `leanx.eu` SAP table reference | https://leanx.eu/en/sap/table/ |
| `se80.co.uk` SAP tables | https://www.se80.co.uk/saptables/ |
| SAP ERP Help Portal | https://help.sap.com/docs/SAP_ERP |
| SAP S/4HANA Help Portal | https://help.sap.com/docs/SAP_S4HANA_CLOUD |

### Predecessor v2 guides (now consolidated here)

| v2 path |
|---|
| `legacy-v2/reference/sources/sap/sap-cds-extractors-guide.md` |
| `legacy-v2/reference/sources/sap/sap-cds-finder-excel.md` |
| `legacy-v2/reference/sources/sap/sap-cloudification-repository.md` |
| `legacy-v2/reference/sources/sap/sap-digital-access-guide.md` |
| `legacy-v2/reference/sources/sap/sap-indirect-access-measurement-2025.md` |
| `legacy-v2/reference/sources/sap/sap-indirect-access-rules.md` |
| `legacy-v2/reference/sources/sap/sap-rfc-extraction-ban.md` |
| `legacy-v2/reference/sources/sap/sap-user-types.md` |

---

## 8. Changelog

- **2026-04-28** — initial v3 page. Consolidates the 8 SAP deep-dive guides at `legacy-v2/reference/sources/sap/`. Drops the v2 "Models 1–4" framing (replaced by D384's sanctioned-path framing). Drops the v2 "Named User Consultant Access" wrong-model option. Reconciles indirect-access guidance against DEC-d2cdb9 (D384). Public catalogue source counts (Cloudification Repository: 44,541 entries / 7,626 released CDS views; CDS Finder Excel: 106,946 mapping rows; CDS extractor count by release: ~4,700 in 2025 with ~18% delta-capable) preserved.
