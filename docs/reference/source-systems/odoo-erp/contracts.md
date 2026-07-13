---
uid: SRC-a8c3e7-contracts
slug: odoo-erp-contracts
title: "Odoo ERP — Contracts"
description: "Contracts authored against Odoo ERP (none yet), and the signed-columns / reconciliation / move_type OC design notes for Odoo journal items."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Contract Registry, not an authority
domain: enterprise-erp
subdomain: odoo
focus: contracts
docket_of: odoo-erp
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Odoo ERP — Contracts

> **Projection, not authority (D526 Amendment 1).** Authority for contract content is the Contract Registry
> (`contract.*`); the exact contract-set participating in a proof is bound by the source-realization package
> (`source_realization_refs[]` in [index.md](index.md)), not by hand-copied UIDs here. This page indexes the
> registry and captures Odoo-specific contract *patterns* (which are design guidance, not governed identity).

Contracts realized against Odoo ERP. Cover: [index.md](index.md).

## Source Contracts (SC)
| SC | Version | Source objects | Status | Registry ref |
|---|---|---|---|---|
| _none authored for Odoo ERP_ | | `account.move` / `account.move.line` (planned) | — | — |

## Admission Contracts (AC)
| AC | Version | SC bound | Status | Registry ref |
|---|---|---|---|---|
| _none authored for Odoo ERP_ | | | — | `index.md` `admission_contract_versions: []` |

> Odoo ERP is **`designed`** with **no evidence of any kind** — no executor, no instance exercised, no
> Source/Admission Contracts authored (see [evidence.md](evidence.md) and [index.md](index.md) `proof_status`).
> Populate this table and `admission_contract_versions[]` in [index.md](index.md) when the first Odoo SC/AC
> lands.

## Observation Contracts (OC)

### Signed-columns amount pattern (Odoo journal items) — design note, ⧗ pending version-exact verification

Odoo journal items model debit/credit direction as **separate columns** on `account.move.line` rather than
SAP's unsigned-amount + sign-indicator (`SHKZG`) pattern. The OC for Odoo amount concepts must therefore
declare **which representation** feeds each amount concept, instead of a `role: "sign_indicator"` mapping:

| Aspect | Odoo shape (design note) | Contract consequence |
|---|---|---|
| Direction | Debit and credit as separate non-negative columns | No sign-indicator role needed; select or derive the signed representation explicitly in the OC/CC |
| Signed value | A signed balance representation (company currency) | Prefer the signed representation for sum-style metrics; never sum a single unsigned column across mixed-direction rows |
| Foreign currency | Separate foreign-currency amount + currency reference alongside company-currency values | Currency handling at the canonical/CC boundary per platform currency doctrine |

⚠ Every row above is read from Odoo's LGPL source code and prior research — **provisional design guidance,
not verified source truth**, until pinned against the exact target Odoo version (field names, nullability, and
semantics shift across yearly majors; see [catalog.md](catalog.md)).

### Reconciliation / open-item pattern — design note, ⧗ pending version-exact verification

Open vs cleared state of receivable/payable journal items is derived through Odoo's **partial reconciliation
model** (reconciliation records linking journal items, supporting partial matching), not a simple per-row
status flag. AR/AP open-item metrics (aging, DSO-class measures) must contract for the reconciliation
relationship explicitly — an OC over `account.move.line` alone cannot express "open amount" without it.

### `move_type` document-class pattern

Invoices, refunds, vendor bills, and plain journal entries are all rows of **one model** (`account.move`)
discriminated by the `move_type` enumeration (`entry`, `out_invoice`, `out_refund`, `in_invoice`, `in_refund`,
…). Document-class discrimination belongs at the **canonical boundary** (classify/derivation over the declared
value set) — **never as literals inside a Metric Contract** (source-agnostic MC rule). This is the Odoo analogue
of the SAP document-type rule.

## Canonical Contracts (CC)
| CC | Version | Grain | Business concepts resolved | Status |
|---|---|---|---|---|
| _none authored for Odoo ERP_ | | | | — |

## Notes
- **Per-instance schema.** Installed community/custom modules add models and fields; the effective schema is
  per-instance (`fields_get()` harvest) — contracts authored against standard models must be verified against
  the instance's actual field set at realization time.
- **Version scoping.** Odoo ships one major per year and supports the three most recent; every pattern above is
  version-scoped and must be re-pinned per target release ([index.md](index.md) §4.A.4, §6.B).
