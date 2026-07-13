---
uid: SRC-000000
slug: source-systems-index
title: "Source Systems"
description: "Per-source authoritative reference for every system BareCount admits data from — protocol, auth, legal posture, reader-flavor binding, and proof status."
type: source-systems-index
status: published
domain: documentation
subdomain: source-systems
focus: governance
last_verified_at: 2026-04-28
governing_adrs:
  - DEC-6cb4f3   # D385 — this framework
  - DEC-d2cdb9   # D384 — SAP API admission stance
---

# Source Systems

Per-source authoritative reference. Each page covers what BareCount admits, the legal/licensing posture, the customer-side and BareCount-side onboarding runbooks, the reader-flavor binding, and — critically — the **proof status** distinguishing "designed" from "shape-tested" from "first-hand-proven."

Framework defined in **ADR DEC-6cb4f3 (D385)**. Read that before authoring or editing a source page.

---

## Reading a source page

Every source page begins with **§1 Proof Status**. Treat it as load-bearing:

| `proof_status` | What it means | What you can claim externally |
|---|---|---|
| `designed` | Architecture and onboarding documented. Nothing has run end-to-end. | Nothing. We have a plan, not a product. |
| `shape_tested` | Protocol path validated against a simulator or sandbox. Not against a real customer instance. | Nothing externally. Useful internally for engineering planning. |
| `first_hand_proven` | At least one real customer instance has produced metric snapshots through the BareCount chain end-to-end. Includes anonymised reference + date in §9. | The specific verified entities and the date. Nothing beyond what §9 lists. |

This operationalises the standing zero-claims policy: **no external claim runs ahead of first-hand proof.**

---

## Migration status from legacy v2 archive

Legacy v2 source pages under `legacy-v2/reference/sources/` have been migrated into `docs/reference/source-systems/` with the source-system reference shape, frontmatter, and explicit `proof_status`. Proof depth is governed per page: some pages are shape-tested against simulators or executor tests; others remain design-only until executor or customer evidence exists. The documentation-control database and per-page frontmatter are the source of truth for page status.

Rewrite discipline applied: every page reconciled against governing ADRs (especially DEC-d2cdb9 / D384 for SAP variants); pre-policy framings dropped (e.g. SAP "OData = gray area" → "Published OData = sanctioned"); wrong-model access patterns dropped (e.g. SAP "Named User Consultant Access"); platform-evolution constraints preserved (v1 sunset deadlines, region-specific endpoints, gated documentation, licence gates, deprecated auth flows).

The 8 SAP deep-dive guides that lived at `legacy-v2/reference/sources/sap/` (CDS Extractors Guide, CDS Finder Excel, Cloudification Repository, Digital Access Guide, Indirect Access Measurement, Indirect Access Rules, RFC Extraction Ban, User Types) have been **consolidated into [sap-licensing-reference.md](sap-licensing-reference.md)** — a single appendix page that supports the SAP source pages with the SAP-side licensing rules and public catalogue sources.

The category groupings below mirror the v2 index for reader continuity.

---

## Enterprise ERP

| Source | v3 page | v2 reference | Proof |
|--------|---------|---------------|-------|
| SAP S/4HANA | [sap-s4hana.md](sap-s4hana.md) | superseded | `shape_tested` |
| SAP ECC | [sap-ecc/](sap-ecc/index.md) 🗂 | superseded | `designed` |
| SAP BW/4HANA | [sap-bw4hana.md](sap-bw4hana.md) | superseded | `designed` |
| SAP SuccessFactors | [sap-successfactors.md](sap-successfactors.md) | superseded | `designed` |
| SAP Digital Manufacturing | [sap-dm.md](sap-dm.md) | superseded | `designed` |
| _SAP Licensing Reference (appendix)_ | [sap-licensing-reference.md](sap-licensing-reference.md) | superseded (8 v2 guides consolidated) | _appendix_ |
| Oracle Fusion Cloud | [oracle-fusion/](oracle-fusion/index.md) 🗂 | superseded | `designed` |
| Oracle E-Business Suite | [oracle-ebs.md](oracle-ebs.md) | superseded | `designed` |
| Oracle NetSuite | [oracle-netsuite.md](oracle-netsuite.md) | superseded | `designed` |
| Microsoft D365 F&O | [microsoft-d365-fo.md](microsoft-d365-fo.md) | superseded | `designed` |
| Microsoft D365 BC | [microsoft-d365-bc/](microsoft-d365-bc/index.md) 🗂 | superseded | `designed` |
| Epicor Kinetic | [epicor-kinetic.md](epicor-kinetic.md) | superseded | `designed` |
| Infor CloudSuite | [infor-cloudsuite.md](infor-cloudsuite.md) | superseded | `designed` |

## Accounting & Invoicing

| Source | v3 page | v2 reference | Proof |
|--------|---------|---------------|-------|
| QuickBooks Online | [quickbooks-online.md](quickbooks-online.md) | superseded | `designed` |
| Xero | [xero.md](xero.md) | superseded | `designed` |
| FreshBooks | [freshbooks.md](freshbooks.md) | superseded | `designed` |
| Sage Intacct | [sage-intacct.md](sage-intacct.md) | superseded | `designed` |
| Zoho Books | [zoho-books.md](zoho-books.md) | superseded | `designed` |
| Tally Prime | [tally-prime/](tally-prime/index.md) 🗂 | superseded | `designed` |
| Busy Accounting | [busy-accounting.md](busy-accounting.md) | superseded | `designed` |
| Odoo ERP | [odoo-erp/](odoo-erp/index.md) 🗂 | superseded | `designed` |

## Payments & Billing

| Source | v3 page | v2 reference | Proof |
|--------|---------|---------------|-------|
| Stripe | [stripe.md](stripe.md) | superseded | `designed` |
| Razorpay | [razorpay.md](razorpay.md) | superseded | `designed` |
| Chargebee | [chargebee.md](chargebee.md) | superseded | `designed` |

## CRM & Sales

| Source | v3 page | v2 reference | Proof |
|--------|---------|---------------|-------|
| Salesforce | [salesforce.md](salesforce.md) | superseded | `shape_tested` |
| HubSpot | [hubspot.md](hubspot.md) | superseded | `designed` |
| Zoho CRM | [zoho-crm.md](zoho-crm.md) | superseded | `designed` |
| Pipedrive | [pipedrive.md](pipedrive.md) | superseded | `designed` |
| FreshSales | [freshsales.md](freshsales.md) | superseded | `designed` |
| Odoo CRM | [odoo-crm.md](odoo-crm.md) | superseded | `designed` |

## HCM & HR

| Source | v3 page | v2 reference | Proof |
|--------|---------|---------------|-------|
| Workday Financials | [workday-financials.md](workday-financials.md) | superseded (v2 stub) | `designed` |
| Workday HCM | [workday-hcm.md](workday-hcm.md) | superseded (v2 stub) | `designed` |
| BambooHR | [bamboohr.md](bamboohr.md) | superseded | `designed` |
| Darwinbox | [darwinbox.md](darwinbox.md) | superseded | `designed` |
| greytHR | [greythr.md](greythr.md) | superseded | `designed` |
| Zoho People | [zoho-people.md](zoho-people.md) | superseded | `designed` |

## ITSM & Service Management

| Source | v3 page | v2 reference | Proof |
|--------|---------|---------------|-------|
| ServiceNow | [servicenow.md](servicenow.md) | superseded | `designed` |
| Atlassian Jira | [atlassian-jira.md](atlassian-jira.md) | superseded | `designed` |
| Jira Service Management | [jira-sm.md](jira-sm.md) | superseded | `designed` |
| FreshService | [freshservice.md](freshservice.md) | superseded | `designed` |
| ManageEngine ServiceDesk | [manageengine.md](manageengine.md) | superseded | `designed` |
| BMC Helix ITSM | [bmc-helix.md](bmc-helix.md) | superseded | `designed` |

## Project Management

| Source | v3 page | v2 reference | Proof |
|--------|---------|---------------|-------|
| Monday.com | [monday.md](monday.md) | superseded | `designed` |
| Asana | [asana.md](asana.md) | superseded | `designed` |

## Procurement

| Source | v3 page | v2 reference | Proof |
|--------|---------|---------------|-------|
| Coupa | [coupa.md](coupa.md) | superseded | `designed` |
| Jaggaer | [jaggaer.md](jaggaer.md) | superseded | `designed` |
| GEP SMART | [gep.md](gep.md) | superseded | `designed` |

## Manufacturing & Supply Chain

| Source | v3 page | v2 reference | Proof |
|--------|---------|---------------|-------|
| Kinaxis Maestro | [kinaxis.md](kinaxis.md) | superseded | `designed` |
| Blue Yonder | [blue-yonder.md](blue-yonder.md) | superseded | `designed` |
| Dassault DELMIA | [dassault-delmia.md](dassault-delmia.md) | superseded | `designed` |
| Rockwell FactoryTalk | [rockwell-factorytalk.md](rockwell-factorytalk.md) | superseded | `designed` |
| Siemens Opcenter | [siemens-opcenter.md](siemens-opcenter.md) | superseded | `designed` |
| AVEVA MES | [aveva-mes.md](aveva-mes.md) | superseded | `designed` |

## Advertising

| Source | v3 page | v2 reference | Proof |
|--------|---------|---------------|-------|
| Google Ads | [google-ads.md](google-ads.md) | superseded | `designed` |
| LinkedIn Ads | [linkedin-ads.md](linkedin-ads.md) | superseded | `designed` |
| Meta Ads | [meta-ads.md](meta-ads.md) | superseded | `designed` |

## Reference Data (Public)

| Source | v3 page | v2 reference | Proof |
|--------|---------|---------------|-------|
| ECB Exchange Rates | [ecb.md](ecb.md) | superseded | `shape_tested` |
| IMF | [imf.md](imf.md) | superseded | `designed` |
| RBI | [rbi.md](rbi.md) | superseded | `designed` |
| World Bank | [world-bank.md](world-bank.md) | superseded | `designed` |

---

## Authoring a new source page

Source systems are **docket folders** (`<slug>/`) per **DEC-8570d4 (D526)**, not flat files. Full convention: [_template/README.md](_template/README.md).

1. Read **DEC-6cb4f3 (D385)** (framework + required sections) and **DEC-8570d4 (D526)** (docket structure).
2. Copy [_template/](_template/) to `source-systems/<slug>/`. Use the migrated [sap-ecc/](sap-ecc/index.md) 🗂 as the exemplar.
3. Fill `index.md` (the docket cover/manifest): allocate a real `SRC-*` uid, set `proof_status` honestly (start `designed`), `system_type_code`, `reader_flavors[]`. If `first_hand_proven`, `evidence.md` must list verified entities with date + anonymised customer reference.
4. As contracts/catalog/evidence accrue, fill the sibling files (`contracts.md`, `catalog.md`, `onboarding-log.md`, `evidence.md`) AND the `index.md` linking hooks (`admission_contract_versions[]`, `catalog_ref`, `evidence_records[]`).
5. Register in the category table above with a link to `<slug>/` (folder), not `<slug>.md`.
6. Run `devhub_doc_scan` then `devhub_doc_validate`.

> **Migration status (D526):** converting the 61 flat pages to docket folders is staged (prove-on-one → rollout). Migrated: 🗂 **SAP ECC**, 🗂 **Microsoft D365 BC**, 🗂 **Odoo ERP**, 🗂 **Oracle Fusion Cloud ERP**, 🗂 **Tally Prime**. The rest remain flat `<slug>.md` until migrated; new systems are born as dockets.

## Changelog

- Initial source-system framework and SAP S/4HANA exemplar imported from v3. ADRs DEC-6cb4f3 (D385, framework) and DEC-d2cdb9 (D384, SAP stance) recorded.
