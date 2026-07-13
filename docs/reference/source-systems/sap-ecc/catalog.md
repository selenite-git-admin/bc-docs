---
uid: SRC-b4c92d-catalog
slug: sap-ecc-catalog
title: "SAP ECC — Catalog"
description: "SAP ECC transparent-table catalog footprint and seed provenance (community-catalogue sourced)."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Source Catalog, not an authority
domain: enterprise-erp
subdomain: sap
focus: catalog
docket_of: sap-ecc
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# SAP ECC — Catalog

> **Projection, not authority (D526 Amendment 1).** Authority is the Source Catalog (`source.*`) and seed store
> (`bc_seed.*`). This page indexes what is registered and its catalog root. The ECC table/field definitions below
> are **provisional seed provenance** sourced from community catalogues — **not verified source truth** — until
> verified against an exact ECC release DDIC.

Source-registration and seed-catalog footprint for SAP ECC. Procedures:
[source-registration.md](../../../onboarding/source-registration.md),
[seed-catalog-management.md](../../../onboarding/seed-catalog-management.md). Cover: [index.md](index.md).

## Registration status

⚠ **No governed source-registry coordinate exists yet** — `index.md` carries `source_registry_ref: null` and
`catalog_root: null`. Until those resolve to `source.*`, **no row below may show a "registered" state**: each is
a **pending/unresolved projection** (Codex P1-3 — the docket must be internally honest ahead of the G2 CI check).

| Artifact | Status | Ref / provenance |
|---|---|---|
| source_provider | ⧗ pending governed ref | label "SAP"; not yet resolvable to `source.*` |
| source_system (`system_type_code`) | ⧗ pending governed ref | label `sap_ecc`; authority = `source_registry_ref` (null) |
| source_version | ⧗ pending | ECC EhP levels TBD |
| source_module | ⧗ pending | FI / MM / SD (planned) |
| source_object (tables) | ⧗ pending (provisional seed only) | seeded from public catalogues, no customer system touched; not governed |
| source_field | ⧗ pending (provisional seed only) | classic ABAP DD field defs (leanx.eu / se80.co.uk); not governed |
| catalog_verification_log | ⧗ pending | not yet run vs an exact-release SAP Data Dictionary |

## Tables / entities cataloged
| Object | Domain | Grain | Notes |
|---|---|---|---|
| BKPF | FI | Accounting document header | Document header, posting date `BUDAT`/`CPUDT` |
| BSEG | FI | Accounting document line item | Unsigned amounts + `SHKZG` sign indicator |
| BSID / BSAD | FI-AR | Customer open / cleared items | AR aging, DSO source |
| BSIK / BSAK | FI-AP | Vendor open / cleared items | AP source |
| EKKO / EKPO | MM | Purchase order header / item | |
| MARA / MARC / MARD | MM | Material master (client/plant/storage) | |
| MSEG / MKPF | MM | Goods movement item / header | |
| KNA1 / KNB1 | SD/FI | Customer master (general / company code) | |
| LFA1 / LFB1 | MM/FI | Vendor master (general / company code) | |

> ECC has **no CDS view layer** — the cataloged object is the transparent table (or a SEGW/Gateway view over it),
> not a semantic CDS model. See [index.md](index.md) §3.

## Seed-load provenance
- Table/field definitions seeded from **public catalogues** `leanx.eu` and `se80.co.uk` — **no customer system touched** (per index.md §6.5). This is **provisional seed provenance, not verified source truth**: a `catalog_verification_log` pass against an exact ECC release DDIC is required before any field definition here is treated as verified. Until then, definitions are design-time approximations.
- ⚠ Cross-reference standing rule (**qualified per Codex review**): standard SAP field *semantics* are broadly universal and authored once at platform level, never per-tenant — but this universality is **scoped to an exact release**. Release, support-package level, industry-extension (IS-*), and customer customizing differences remain in scope for a source realization and must be verified per realization, not assumed. Custom `Y*`/`Z*` fields are the additive per-customer catalog work.
