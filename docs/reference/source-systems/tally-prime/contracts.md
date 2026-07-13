---
uid: SRC-b3e7c2-contracts
slug: tally-prime-contracts
title: "Tally Prime — Contracts"
description: "Contracts authored against Tally Prime (none yet) and candidate OC-pattern questions to resolve before authoring."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Contract Registry, not an authority
domain: accounting
subdomain: tally
focus: contracts
docket_of: tally-prime
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Tally Prime — Contracts

> **Projection, not authority (D526 Amendment 1).** Authority for contract content is the Contract Registry
> (`contract.*`); the exact contract-set participating in a proof is bound by the source-realization package
> (`source_realization_refs[]` in [index.md](index.md)), not by hand-copied UIDs here. This page indexes the
> registry and captures Tally-specific contract *pattern questions* (design guidance, not governed identity).

Contracts realized against Tally Prime. Cover: [index.md](index.md).

## Source Contracts (SC)
| SC | Version | Source objects | Status | Registry ref |
|---|---|---|---|---|
| _none authored_ | | vouchers / ledgers / masters (planned) | — | — |

## Admission Contracts (AC)
| AC | Version | SC bound | Status | Registry ref |
|---|---|---|---|---|
| _none authored_ | | | — | `index.md` `admission_contract_versions: []` |

> Tally Prime is **`designed`** with **no evidence of any kind** — no executor, no simulator profile, no
> instance ever read (see [evidence.md](evidence.md) and [index.md](index.md) `proof_status`). No Source/
> Admission Contracts have been authored. Populate this table and `admission_contract_versions[]` in
> [index.md](index.md) when the first Tally SC/AC lands.

## Observation Contracts (OC)

### Candidate OC-pattern questions (⧗ all unresolved — verify before authoring)

No OC exists and no OC pattern is asserted. The following **must be resolved from version-exact official
documentation and instance verification** before the first Tally OC is authored; nothing here is a claim:

| Question | Why it gates OC authoring | Status |
|---|---|---|
| Debit/credit representation in voucher ledger entries (signed amounts vs a separate direction indicator in the XML `Export` shape) | Determines whether a sign-indicator-style OC pattern (as used for SAP ECC sub-ledger) is needed at the canonical boundary | ⧗ unverified — pin against the official XML schema for the exact release |
| Amount/currency representation (base vs foreign currency, per-entry vs per-voucher) | Determines amount `representation_term` handling and any currency roles | ⧗ unverified |
| Voucher-type extensibility (custom voucher types) | OC field mappings must not assume the standard taxonomy is closed | ⧗ instance-scoped discovery required |
| TDL-customization impact on export shapes | A customized instance can change the observed shape; OC universality is instance-scoped until verified | ⧗ per-instance verification required (see [catalog.md](catalog.md)) |
| Edit Log variant exposure of edit history via integration surfaces | Possible change-detection input; affects observation semantics if usable | ⧗ unverified |

## Canonical Contracts (CC)
| CC | Version | Grain | Business concepts resolved | Status |
|---|---|---|---|---|
| _none authored_ | | | | — |

## Notes
- **Read-only posture.** The official XML interface supports `Import` (write into Tally) as well as `Export`; only `Export`-class reads are in BareCount scope ([index.md](index.md) §4.A.2). No contract may bind a write path.
- **Per-company scoping.** TallyPrime books are per-company data files; SC scope is naturally per company dataset, and contracts must carry that scope explicitly rather than assume a single-company installation.
