---
uid: SRC-a8c3e7-catalog
slug: odoo-erp-catalog
title: "Odoo ERP — Catalog"
description: "Odoo ERP model catalog footprint and seed provenance (LGPL source-code sourced, provisional)."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Source Catalog, not an authority
domain: enterprise-erp
subdomain: odoo
focus: catalog
docket_of: odoo-erp
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Odoo ERP — Catalog

> **Projection, not authority (D526 Amendment 1).** Authority is the Source Catalog (`source.*`) and seed store
> (`bc_seed.*`). This page indexes what is registered and its catalog root. The Odoo model/field definitions
> below are **provisional seed provenance** sourced from Odoo's published LGPL source code — **not verified
> source truth** — until verified against an exact Odoo release and the target instance's installed-module set.

Source-registration and seed-catalog footprint for Odoo ERP. Procedures:
[source-registration.md](../../../onboarding/source-registration.md),
[seed-catalog-management.md](../../../onboarding/seed-catalog-management.md). Cover: [index.md](index.md).

## Registration status

⚠ **No governed source-registry coordinate exists yet** — `index.md` carries `source_registry_ref: null` and
`catalog_root: null`. Until those resolve to `source.*`, **no row below may show a "registered" state**: each is
a **pending/unresolved projection** (the docket must be internally honest ahead of the G2 CI check).

| Artifact | Status | Ref / provenance |
|---|---|---|
| source_provider | ⧗ pending governed ref | label "Odoo S.A."; not yet resolvable to `source.*` |
| source_system (`system_type_code`) | ⧗ pending governed ref | label `odoo_erp`; authority = `source_registry_ref` (null) |
| source_version | ⧗ pending | yearly majors; three most recent supported (v-exact TBD at registration) |
| source_module | ⧗ pending | `account` / `sale` / `purchase` / `stock` / `mrp` (planned) |
| source_object (models) | ⧗ pending (provisional seed only) | seeded from Odoo LGPL source code, no customer system touched; not governed |
| source_field | ⧗ pending (provisional seed only) | per-model field defs from `github.com/odoo/odoo` `addons/*/models/`; not governed |
| catalog_verification_log | ⧗ pending | not yet run vs an exact-release Odoo codebase or a live `fields_get()` harvest |

## Models / entities cataloged

| Object (model) | Domain | Grain | Notes |
|---|---|---|---|
| `account.move` | FI | Journal entry / document header | `move_type` discriminates entry / invoice / refund / bill |
| `account.move.line` | FI | Journal item (document line) | Debit/credit as separate columns; signed balance (design note — [contracts.md](contracts.md)) |
| `account.account`, `account.group` | FI | Chart of accounts | |
| `account.payment` | FI | Payment | |
| `account.bank.statement` / `.line` | FI | Bank statement header / line | |
| `res.company`, `res.currency` | Core | Company / currency master | Exchange rates via currency model family |
| `res.partner` | Core | Partner (customer / vendor / contact) | Single partner model across roles |
| `sale.order` / `sale.order.line` | SD | Sales order header / line | |
| `purchase.order` / `purchase.order.line` | MM | Purchase order header / line | |
| `stock.picking` / `stock.move` | MM | Transfer / stock move | |
| `mrp.production`, `mrp.bom`, `mrp.workorder` | PP | Manufacturing order / BoM / work order | |

> The cataloged object in Odoo is an **ORM model**, not a SQL table — the external API exposes model-level
> `search_read` / `fields_get`, and per-instance modules extend models with additional fields. See
> [index.md](index.md) §3 and §6.5.

## Seed-load provenance

- Model/field definitions are seeded from **Odoo's published LGPL source code**
  (`github.com/odoo/odoo`, e.g. [`addons/account/models/`](https://github.com/odoo/odoo/tree/18.0/addons/account/models)
  — `account_move.py`, `account_move_line.py`, `account_payment.py`, `account_account.py` confirmed present on
  the 18.0 branch) — **no customer system touched**. Odoo's schema authority *is* that source code (the models
  define the schema), but as catalog provenance this remains **provisional until version-exact verification**: a
  `catalog_verification_log` pass against the exact target release (and, per instance, a live `fields_get()`
  harvest) is required before any field definition here is treated as verified. Until then, definitions are
  design-time approximations.
- ⚠ Universality is **narrower than SAP's**: standard-model semantics are authored once at platform level, but
  they are scoped to an **exact yearly major** (schema shifts across majors) **and** to the instance's
  **installed-module inventory** — community/custom modules add models and fields that can only be discovered
  per instance via `fields_get()` / `ir.model.fields`. Per-instance additive catalog work is expected for any
  non-standard module.
