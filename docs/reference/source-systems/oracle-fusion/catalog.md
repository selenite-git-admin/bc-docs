---
uid: SRC-1b8e5a-catalog
slug: oracle-fusion-catalog
title: "Oracle Fusion Cloud ERP — Catalog"
description: "Oracle Fusion Financials catalog footprint and seed provenance (vendor-published Tables-and-Views sourced — provisional until digest-bound)."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Source Catalog, not an authority
domain: enterprise-erp
subdomain: oracle
focus: catalog
docket_of: oracle-fusion
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Oracle Fusion Cloud ERP — Catalog

> **Projection, not authority (D526 Amendment 1).** Authority is the Source Catalog (`source.*`) and seed store
> (`bc_seed.*`). This page indexes what is registered and its catalog root. The Fusion table/resource definitions
> below are **provisional seed provenance**: they are sourced from Oracle's own public
> [Tables and Views for Financials](https://docs.oracle.com/en/cloud/saas/financials/25d/oedmf/index.html)
> reference — vendor-authored, which is stronger provenance than a community catalogue, but **still provisional**
> until version-exact, digest-bound `official_research_refs[]` records exist and a catalog-verification pass is
> run against an exact release edition. No seed load has actually been executed.

Source-registration and seed-catalog footprint for Oracle Fusion Cloud ERP. Procedures:
[source-registration.md](../../../onboarding/source-registration.md),
[seed-catalog-management.md](../../../onboarding/seed-catalog-management.md). Cover: [index.md](index.md).

## Registration status

⚠ **No governed source-registry coordinate exists** — `index.md` carries `source_registry_ref: null` and
`catalog_root: null`. Until those resolve to `source.*`, **no row below may show a "registered" state**: each is
a **pending/unresolved projection**.

| Artifact | Status | Ref / provenance |
|---|---|---|
| source_provider | ⧗ pending governed ref | label "Oracle"; not yet resolvable to `source.*` |
| source_system (`system_type_code`) | ⧗ pending governed ref | label `oracle_fusion`; authority = `source_registry_ref` (null) |
| source_version | ⧗ pending | quarterly release labels (25C/25D/…) — moving baseline, see index.md §4.A.4 |
| source_module | ⧗ pending | GL / AP / AR / FA / CE / PO / PPM (planned) |
| source_object (tables/resources) | ⧗ pending (no seed loaded) | candidate footprint below from public Tables-and-Views + REST reference; no system touched; not governed |
| source_field | ⧗ pending (no seed loaded) | column definitions available in the public Tables-and-Views reference; not yet extracted or digest-bound |
| catalog_verification_log | ⧗ pending | not yet run vs an exact-release Tables-and-Views edition |

## Tables / entities — candidate footprint (⧗ all pending; no registration, no seed load)

Candidate objects named from the flat-page research and the public references; **every row is ⧗ pending** —
per-object documentation-page verification and seed extraction have not been performed (only `GL_JE_LINES` has
had its documentation page individually confirmed to exist, [here](https://docs.oracle.com/en/cloud/saas/financials/24a/oedmf/gljelines-22720.html)).

| Object (candidate) | Domain | Grain (expected) | Status |
|---|---|---|---|
| GL journal batches / headers / lines (`GL_JE_BATCHES`/`GL_JE_HEADERS`/`GL_JE_LINES`-class) | GL | Batch / journal header / journal line | ⧗ pending |
| GL balances | GL | Ledger × account combination × period | ⧗ pending |
| Subledger accounting entries (`XLA_*`-class) | XLA | Subledger journal header / line | ⧗ pending |
| AP invoices / lines / payments | AP | Invoice header / line / payment | ⧗ pending |
| AR transactions / receipts | AR | Transaction header / line / receipt | ⧗ pending |
| Fixed assets (books, transactions, depreciation) | FA | Asset × book | ⧗ pending |
| Cash management (bank statements, lines) | CE | Statement / line | ⧗ pending |
| Procurement (purchase orders, requisitions, receipts) | PO | Document header / line | ⧗ pending |
| Projects (costs, expenditure items, budgets) | PPM | Expenditure item et al. | ⧗ pending |

## Access-surface note

The customer never has direct SQL access on Fusion SaaS: the admissible object is a **REST resource** or a
**BICC data store (view object)** over the documented table, not the table itself (see [index.md](index.md) §3).
Cataloging therefore needs **both** coordinates per object — the documented table shape (Tables-and-Views) and
the access-surface shape (REST `describe` / BICC enabled data store) — and the mapping between them is itself
catalog work, ⧗ not started.

## Seed-load provenance
- **No seed load has been executed.** The candidate footprint above is narrative only.
- When seeded, definitions will come from Oracle's **public, vendor-authored** references (Tables-and-Views per
  release edition; REST API reference; BICC data-store lists) — **no customer system touched**. Vendor-authored
  is stronger provenance than community catalogues, but it remains **provisional seed provenance, not verified
  source truth**, until each citation is pinned as a version-exact, digest-bound `official_research_refs[]`
  record and a `catalog_verification_log` pass is run against that exact release edition.
- ⚠ Release-scoping rule: Fusion's **mandatory quarterly updates** mean any verified catalog state is scoped to
  an exact release label (e.g. 25D); re-verification per release is part of the realization work, not optional.
  Customer flexfield configuration (key/descriptive) is the additive per-customer catalog work — segment and
  attribute semantics are never assumed platform-universal.
