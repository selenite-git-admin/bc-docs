---
uid: SRC-b4c92d-contracts
slug: sap-ecc-contracts
title: "SAP ECC — Contracts"
description: "Contracts authored against SAP ECC, and the sign-indicator OC pattern for ECC sub-ledger tables."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Contract Registry, not an authority
domain: enterprise-erp
subdomain: sap
focus: contracts
docket_of: sap-ecc
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# SAP ECC — Contracts

> **Projection, not authority (D526 Amendment 1).** Authority for contract content is the Contract Registry
> (`contract.*`); the exact contract-set participating in a proof is bound by the source-realization package
> (`source_realization_refs[]` in [index.md](index.md)), not by hand-copied UIDs here. This page indexes the
> registry and captures ECC-specific contract *patterns* (which are design guidance, not governed identity).

Contracts realized against SAP ECC. Cover: [index.md](index.md).

## Source Contracts (SC)
| SC | Version | Source objects | Status | Registry ref |
|---|---|---|---|---|
| _none authored for real ECC_ | | BKPF/BSEG/BSID/BSAD (planned) | — | — |

## Admission Contracts (AC)
| AC | Version | SC bound | Status | Registry ref |
|---|---|---|---|---|
| _none authored for real ECC_ | | | — | `index.md` `admission_contract_versions: []` |

> ECC remains **`designed`** — the bc-sdg simulator run is ungoverned historical background and does **not**
> establish `shape_tested` (see [evidence.md](evidence.md) and [index.md](index.md) `proof_status`). No
> Source/Admission Contracts have been authored against a real ECC Gateway service yet. Populate this table
> and `admission_contract_versions[]` in [index.md](index.md) when the first real-ECC SC/AC lands.

## Observation Contracts (OC)

### Sign-indicator OC pattern (ECC sub-ledger)

ECC sub-ledger tables store amounts **unsigned**; debit/credit direction is a separate indicator field
(`SHKZG`). The OC declares the sign indicator so the CCv2 resolver applies sign correction at the canonical
boundary. This is the governing contract pattern for every ECC amount metric.

| Table family | Amount semantics | Sign indicator | Credit value |
|---|---|---|---|
| BSID / BSAD (AR open/cleared) | Unsigned (`WRBTR`, `DMBTR`) | `SHKZG` | `H` |
| BSIK / BSAK (AP open/cleared) | Unsigned (`WRBTR`, `DMBTR`) | `SHKZG` | `H` |
| BSEG (document line items) | Unsigned (`WRBTR`, `DMBTR`) | `SHKZG` | `H` |
| ACDOCA (Universal Journal) | **Signed** (`HSL`, `TSL`) | None needed | — |

- **SHKZG values:** `S` = debit (Soll), `H` = credit (Haben). On `SHKZG = H`, amount fields are negated at the canonical boundary so sums compute correctly (credits reduce totals).
- **OC declaration:** a `field_mapping` with `role: "sign_indicator"` and `transform_params: { "credit_value": "H" }`. The CCv2 resolver negates `representation_term: "amount"` fields on credit-side rows. The sign-indicator field is resolver metadata — **not projected to the CO**.
- **Why it matters:** without sign correction, amount metrics summing across debit and credit rows (receivables, payables, revenue) silently overstate — invisible when all rows are debits, breaks the moment credit memos / payments / clearing entries appear.

Governing source for this pattern: [observation-contract-creation.md](../../../onboarding/observation-contract-creation.md) §Sign Handling.

## Canonical Contracts (CC)
| CC | Version | Grain | Business concepts resolved | Status |
|---|---|---|---|---|
| _none authored for real ECC_ | | | | — |

## Notes
- **Currency.** ECC sub-ledger carries document currency (`WRBTR`, `WAERS`) and local currency (`DMBTR`, `HWAER`). When they differ, `DMBTR` is independently rounded per line; the sum of line `DMBTR` may differ from the header-level conversion by ±0.01 per document. Known SAP characteristic — handle at the canonical/CC boundary, not as a defect.
