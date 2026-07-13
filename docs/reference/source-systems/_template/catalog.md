---
uid: SRC-TEMPLATE-catalog
slug: _template-catalog
title: "<System Name> — Catalog"
description: "Seed-catalog and source-registration entries (provider/system/version/module/table/field) for <System Name>."
type: source-systems-docket
status: draft
authority_role: projection      # D526 Amendment 1 — projection of the Source Catalog, not an authority
domain: <domain>
subdomain: <vendor-family>
focus: catalog
docket_of: _template
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# <System Name> — Catalog

> **Projection, not authority (D526 Amendment 1).** Authority is the Source Catalog (`source.*`) and the seed
> store (`bc_seed.*`). This page indexes what is registered and its catalog/mapping root; it does not define
> catalog identity. Seed material from community catalogues is **provisional provenance**, not verified source
> truth, until exact release/DDIC (or vendor-equivalent) verification.

Source-registration and seed-catalog footprint for this system, referenced by catalog/mapping root. Procedures:
[source-registration.md](../../../onboarding/source-registration.md),
[seed-catalog-management.md](../../../onboarding/seed-catalog-management.md).

## Registration status
| Artifact | Registered | Ref / provenance |
|---|---|---|
| source_provider | ☐ | |
| source_system (`system_type_code`) | ☐ | |
| source_version | ☐ | |
| source_module | ☐ | |
| source_object (tables/entities) | ☐ | count / load script |
| source_field | ☐ | count / load script |
| catalog_verification_log | ☐ | |

## Tables / entities cataloged
| Object | Grain | Key fields | Seed source | Notes |
|---|---|---|---|---|
| _none yet_ | | | | |

## Seed-load provenance
<Which script/package loaded these, when, from which primary source (vendor DD / community catalogue), version-exact.>
