---
uid: SRC-TEMPLATE-contracts
slug: _template-contracts
title: "<System Name> — Contracts"
description: "Source/Admission/Observation/Canonical Contracts authored against <System Name>, with Contract Registry links."
type: source-systems-docket
status: draft
authority_role: projection      # D526 Amendment 1 — projection of the Contract Registry, not an authority
domain: <domain>
subdomain: <vendor-family>
focus: contracts
docket_of: _template            # slug of the owning docket (index.md)
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# <System Name> — Contracts

> **Projection, not authority (D526 Amendment 1).** Authority for contract content is the Contract Registry
> (`contract.*`). This page indexes governed contract versions by exact UID; it does not define contract
> identity. Values must be generated or CI-reconciled from the registry, never hand-asserted.

Contracts realized against this source system, referenced by governed version UID. The exact SC/AC/OC/CC
version set (or contract-set digest) that participates in a proof is bound by the source-realization package
referenced from [index.md](index.md) `source_realization_refs[]` — not by hand-copying UIDs here.

## Source Contracts (SC)
| SC | Version | Source objects (tables/entities) | Status | Registry ref |
|---|---|---|---|---|
| _none yet_ | | | | |

## Admission Contracts (AC)
| AC | Version | SC bound | Status | Registry ref |
|---|---|---|---|---|
| _none yet_ | | | | |

## Observation Contracts (OC)
| OC | Version | Entity | Canonical target | Status |
|---|---|---|---|---|
| _none yet_ | | | | |

## Canonical Contracts (CC)
| CC | Version | Grain | Business concepts resolved | Status |
|---|---|---|---|---|
| _none yet_ | | | | |

## Notes
<Source-specific contract notes: sign/OC patterns, join semantics, coded-value classify inputs, etc.>
