---
uid: SRC-a4c6e9-catalog
slug: zoho-books-catalog
title: "Zoho Books — Catalog"
description: "Zoho Books API-module catalog footprint and seed provenance (official API documentation sourced; nothing registered)."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Source Catalog, not an authority
domain: accounting
subdomain: zoho
focus: catalog
docket_of: zoho-books
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Zoho Books — Catalog

> **Projection, not authority (D526 Amendment 1).** Authority is the Source Catalog (`source.*`) and seed
> store (`bc_seed.*`). This page indexes what is registered and its catalog root. The Zoho Books module
> definitions below are **provisional seed provenance** sourced from the official API documentation — **not
> verified source truth** — until verified against a live organization's actual module shapes (edition- and
> customization-scoped).

Source-registration and seed-catalog footprint for Zoho Books. Procedures:
[source-registration.md](../../../onboarding/source-registration.md),
[seed-catalog-management.md](../../../onboarding/seed-catalog-management.md). Cover: [index.md](index.md).

## Registration status

⚠ **No governed source-registry coordinate exists** — `index.md` carries `source_registry_ref: null` and
`catalog_root: null`. Until those resolve to `source.*`, **no row below may show a "registered" state**: each
is a **pending/unresolved projection**.

| Artifact | Status | Ref / provenance |
|---|---|---|
| source_provider | ⧗ pending governed ref | label "Zoho"; not yet resolvable to `source.*` |
| source_system (`system_type_code`) | ⧗ pending governed ref | label `zoho_books`; authority = `source_registry_ref` (null) |
| source_version | ⧗ pending | REST API v3; product plan/edition per tenant TBD |
| source_module | ⧗ pending | Sales / Purchases / Accountant / Banking (planned) |
| source_object (API modules) | ⧗ pending (provisional seed only) | from official API v3 documentation; no customer organization touched; not governed |
| source_field | ⧗ pending (provisional seed only) | per-module JSON shapes from the official API reference + OpenAPI files; not governed; not yet seeded |
| catalog_verification_log | ⧗ pending | not yet run vs a live organization's module shapes |

## API modules / entities cataloged (candidate footprint — all ⧗ pending registration)

Core set per the official [API v3 documentation](https://www.zoho.com/books/api/v3/introduction/):

| Module | Domain | Grain | Notes |
|---|---|---|---|
| Organizations | Settings | Organization | Connection coordinate; every request scoped by `organization_id` |
| Chart of Accounts | Accountant | Account | Account types, codes, hierarchy |
| Journals | Accountant | Manual journal entry | Line-level debit/credit shape ⧗ pending verification |
| Invoices | Sales | Sales invoice | AR source |
| Credit Notes | Sales | Credit note | Entity-typed credit document (see [contracts.md](contracts.md)) |
| Customer Payments | Sales | Payment | |
| Estimates | Sales | Estimate/quote | |
| Sales Orders | Sales | Sales order | |
| Contacts | Sales/Purchases | Customer/vendor master | Classification: customer vs vendor |
| Bills | Purchases | Vendor bill | AP source |
| Vendor Credits | Purchases | Vendor credit | Entity-typed credit document |
| Purchase Orders | Purchases | Purchase order | |
| Expenses | Purchases | Expense | |
| Bank Accounts / Bank Transactions | Banking | Account / transaction | |
| Users | Settings | User | |

> Regional-edition modules (e.g. India-edition GST returns) and per-tenant custom fields extend this
> surface and are **not** cataloged until verified against official edition documentation and the actual
> organization (⧗ — [index.md](index.md) §8 gap 7).

## Seed-load provenance

- Module/field definitions are to be seeded from the **official Zoho Books API v3 documentation**
  (per-module reference pages and downloadable OpenAPI documents) — **no customer organization touched**.
  This is **provisional seed provenance, not verified source truth**: a `catalog_verification_log` pass
  against a live organization's actual responses is required before any field definition here is treated
  as verified. Until then, definitions are design-time approximations. **No seed load has been executed
  yet** — the table above is a candidate footprint only.
- ⚠ Cross-reference standing rule (qualified): the published API module shape is broadly universal and
  authored once at platform level, never per-tenant — but this universality is **scoped to the API version
  (v3), the product edition (regional editions differ, e.g. India GST), and the plan**. Custom fields are
  the additive per-customer catalog work; edition/plan differences must be verified per realization, not
  assumed.
