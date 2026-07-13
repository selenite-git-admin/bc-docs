---
uid: SRC-b3e7c2-catalog
slug: tally-prime-catalog
title: "Tally Prime — Catalog"
description: "Candidate Tally Prime object footprint (vouchers, ledgers, masters) — nothing registered; no provisional seed loaded; seeding approach undesigned."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Source Catalog, not an authority
domain: accounting
subdomain: tally
focus: catalog
docket_of: tally-prime
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Tally Prime — Catalog

> **Projection, not authority (D526 Amendment 1).** Authority is the Source Catalog (`source.*`) and seed store
> (`bc_seed.*`). This page indexes what is registered and its catalog root. For Tally Prime **nothing is
> registered and no provisional seed has been loaded** — the object list below is a **candidate footprint**
> derived from official integration documentation only, **not verified source truth** and not seed provenance.

Source-registration and seed-catalog footprint for Tally Prime. Procedures:
[source-registration.md](../../../onboarding/source-registration.md),
[seed-catalog-management.md](../../../onboarding/seed-catalog-management.md). Cover: [index.md](index.md).

## Registration status

⚠ **No governed source-registry coordinate exists** — `index.md` carries `source_registry_ref: null` and
`catalog_root: null`. Until those resolve to `source.*`, **no row below may show a "registered" state**: each is
a **pending/unresolved projection**.

| Artifact | Status | Ref / provenance |
|---|---|---|
| source_provider | ⧗ pending governed ref | label "Tally Solutions"; not yet resolvable to `source.*` |
| source_system (`system_type_code`) | ⧗ pending governed ref | label `tally_prime`; authority = `source_registry_ref` (null) |
| source_version | ⧗ pending | release line 4.0–7.1 per official release notes; exact target release(s) TBD |
| source_module | ⧗ pending | accounting / inventory / statutory (planned segmentation; Tally has no formal module registry) |
| source_object | ⧗ pending — **no seed loaded** | candidate footprint below; seeding approach undesigned (index.md §8) |
| source_field | ⧗ pending — **no seed loaded** | would derive from official TDL documentation + instance discovery |
| catalog_verification_log | ⧗ pending | no verification run — nothing to verify yet |

## Candidate objects (footprint — NOT cataloged, NOT seeded)

Derived from the official integration overview and product documentation only
([integration overview](https://help.tallysolutions.com/integration-with-tallyprime/),
[TDL reference](https://help.tallysolutions.com/article/TDL/Welcome.htm)); grain statements are design
expectations, ⧗ unverified against any release's actual export shapes.

| Object (candidate) | Domain | Expected grain | Notes |
|---|---|---|---|
| Company | admin | Company dataset | Per-company data files; scope unit for everything below |
| Ledger | accounting | Ledger master | Chart-of-accounts leaf; rolls up under groups |
| Group | accounting | Ledger group | Hierarchy above ledgers; customer-editable above reserved primaries (⧗ reserved list unverified) |
| Voucher Type | accounting | Voucher-type master | Standard taxonomy (sales/purchase/journal/payment/receipt/contra/debit-credit note) + customer-defined types |
| Voucher | accounting | Voucher (transaction) | The transaction record; ledger-entry substructure ⧗ shape unverified |
| Cost Centre | accounting | Cost-centre master | |
| Stock Group / Stock Item / Unit | inventory | Respective masters | |
| Stock movement | inventory | Movement entry | ⧗ export shape unverified |
| Tax configuration (e.g. GST) | statutory | Config masters | Region-dependent (Indian deployments: GSTIN/HSN/rates); ⧗ unverified |

## Seed-load provenance

**None.** No seed has been loaded for Tally Prime from any source. There is **no community catalogue**
equivalent to the SAP table catalogues (leanx.eu / se80.co.uk) for Tally shapes; the seeding approach —
official TDL documentation plus per-instance discovery of collections/ODBC tables — is itself undesigned
([index.md](index.md) §8). Until a seed exists *and* a `catalog_verification_log` pass runs against an
exact-release instance, no field definition may be treated as verified.

⚠ Universality caveat: TallyPrime instances commonly carry **TDL customizations** and **custom voucher types**
that alter observed shapes. Shape universality is therefore **release- and instance-scoped** — verified per
source realization, never assumed platform-wide.
