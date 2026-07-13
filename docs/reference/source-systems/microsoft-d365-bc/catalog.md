---
uid: SRC-e4a7b2-catalog
slug: microsoft-d365-bc-catalog
title: "Microsoft Dynamics 365 Business Central — Catalog"
description: "Business Central catalog footprint and seed provenance (vendor-published Learn application reference + MIT source — provisional until digest-bound)."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Source Catalog, not an authority
domain: enterprise-erp
subdomain: microsoft
focus: catalog
docket_of: microsoft-d365-bc
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Microsoft Dynamics 365 Business Central — Catalog

> **Projection, not authority (D526 Amendment 1).** Authority is the Source Catalog (`source.*`) and seed store
> (`bc_seed.*`). This page indexes what is registered and its catalog root. The Business Central table/entity
> definitions below are **provisional seed provenance**: they are sourced from Microsoft's own vendor-published
> surfaces — the per-table [application reference on Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/business-central/application/base-application/table/microsoft.finance.generalledger.ledger.g-l-entry)
> and the MIT-licensed AL source in [microsoft/BCApps](https://github.com/microsoft/BCApps) — unusually strong
> candidate provenance for an ERP (vendor-authored documentation *and* readable source), but **still
> provisional** until version-exact, digest-bound `official_research_refs[]` records exist and a
> catalog-verification pass is run against an exact version (G3). No seed load has actually been executed.

Source-registration and seed-catalog footprint for Microsoft Dynamics 365 Business Central. Procedures:
[source-registration.md](../../../onboarding/source-registration.md),
[seed-catalog-management.md](../../../onboarding/seed-catalog-management.md). Cover: [index.md](index.md).

## Registration status

⚠ **No governed source-registry coordinate exists** — `index.md` carries `source_registry_ref: null` and
`catalog_root: null`. Until those resolve to `source.*`, **no row below may show a "registered" state**: each is
a **pending/unresolved projection**.

| Artifact | Status | Ref / provenance |
|---|---|---|
| source_provider | ⧗ pending governed ref | label "Microsoft"; not yet resolvable to `source.*` |
| source_system (`system_type_code`) | ⧗ pending governed ref | label `microsoft_d365_bc`; authority = `source_registry_ref` (null) |
| source_version | ⧗ pending | online = moving baseline (two major waves/year + monthly minors, see index.md §4.A.5); on-prem = customer version |
| source_module | ⧗ pending | GL / AR / AP / Inventory / Sales / Purchasing (planned) |
| source_object (tables/entities) | ⧗ pending (no seed loaded) | candidate footprint below from the Learn application reference + API v2.0 surface; no system touched; not governed |
| source_field | ⧗ pending (no seed loaded) | field definitions available on the Learn per-table pages and in BCApps AL source; not yet extracted or digest-bound |
| catalog_verification_log | ⧗ pending | not yet run vs an exact-version application reference / BCApps tag |

## Tables / entities — candidate footprint (⧗ all pending; no registration, no seed load)

Candidate objects named from the flat-page research and the vendor-published references; **every row is
⧗ pending** — per-object documentation-page verification and seed extraction have not been performed. Only two
table pages have been individually confirmed to exist (2026-07-13):
[G/L Entry (ID 17)](https://learn.microsoft.com/en-us/dynamics365/business-central/application/base-application/table/microsoft.finance.generalledger.ledger.g-l-entry)
and [Detailed Cust. Ledg. Entry (ID 379)](https://learn.microsoft.com/en-us/dynamics365/business-central/application/base-application/table/microsoft.sales.receivables.detailed-cust.-ledg.-entry).

| Object (candidate) | Domain | Grain (expected) | Status |
|---|---|---|---|
| G/L Entry (Table 17) | GL | Posted general-ledger entry line | ⧗ pending (page confirmed) |
| Cust. Ledger Entry / Detailed Cust. Ledg. Entry (Table 379) | AR | Ledger entry / detailed application entry | ⧗ pending (detailed page confirmed) |
| Vendor Ledger Entry / Detailed Vendor Ledg. Entry | AP | Ledger entry / detailed application entry | ⧗ pending |
| Item Ledger Entry / Value Entry | Inventory | Item movement / valuation entry | ⧗ pending |
| Sales Invoice Header / Line (posted) | Sales | Document header / line | ⧗ pending |
| Purch. Invoice Header / Line (posted) | Purchasing | Document header / line | ⧗ pending |
| Sales Header / Line (open orders) | Sales | Document header / line | ⧗ pending |
| G/L Account, Customer, Vendor, Item | Master data | Master record | ⧗ pending |
| Dimension / Dimension Value / Dimension Set Entry | Config | Dimension model | ⧗ pending |
| Posting-group setup tables | Config | Configuration record | ⧗ pending |

## Access-surface note

On Business Central online the customer never has direct SQL access: the admissible object is an **API v2.0
entity (AL API page) or an OData-exposed page/query** over the documented table, not the table itself (see
[index.md](index.md) §3). Cataloging therefore needs **both** coordinates per object — the documented table
shape (Learn application reference / BCApps source) and the access-surface shape (API entity from `$metadata`)
— and the entity↔table mapping is itself catalog work, ⧗ not started. API entities officially re-confirmed to
exist (via the [webhook supported-resources list](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-subscriptions),
2026-07-13) include `accounts`, `companyInformation`, `currencies`, `customers`, `dimensions`,
`generalLedgerEntries`, `items`, `journals`, `paymentMethods`, `paymentTerms`, `purchaseInvoices`,
`salesCreditMemos`, `salesInvoices`, `salesOrders`, `unitsOfMeasure`, `vendors`. Entities from prior research
**not** re-confirmed this pass — `customerLedgerEntries`, `vendorLedgerEntries`, `itemLedgerEntries`,
`trialBalances` — remain ⧗ pending per-entity verification against the v2.0 resource reference.

## Seed-load provenance
- **No seed load has been executed.** The candidate footprint above is narrative only.
- When seeded, definitions will come from Microsoft's **public, vendor-authored** surfaces (per-table Learn
  application reference; BCApps MIT-licensed AL source; API `$metadata` shape) — **no customer system
  touched**. Vendor-authored documentation plus readable MIT source is unusually strong candidate provenance,
  but it remains **provisional seed provenance, not verified source truth**, until each citation is pinned as a
  version-exact, digest-bound `official_research_refs[]` record and a `catalog_verification_log` pass is run
  against that exact version (G3).
- ⚠ Version-scoping rule: Business Central online's **two major waves per year + monthly minor updates** mean
  any verified catalog state is scoped to an exact base-application version; re-verification per version is
  part of the realization work, not optional. Per-tenant extensions (PTEs) and AppSource apps — including
  custom APIs — are the additive per-customer catalog work; extension-added fields and entities are never
  assumed platform-universal.
