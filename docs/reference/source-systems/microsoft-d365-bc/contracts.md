---
uid: SRC-e4a7b2-contracts
slug: microsoft-d365-bc-contracts
title: "Microsoft Dynamics 365 Business Central — Contracts"
description: "Contracts authored against Business Central (none), and candidate OC design notes: signed amount + dual debit/credit columns, detailed-ledger application state, dimension-set model."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Contract Registry, not an authority
domain: enterprise-erp
subdomain: microsoft
focus: contracts
docket_of: microsoft-d365-bc
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Microsoft Dynamics 365 Business Central — Contracts

> **Projection, not authority (D526 Amendment 1).** Authority for contract content is the Contract Registry
> (`contract.*`); the exact contract-set participating in a proof is bound by the source-realization package
> (`source_realization_refs[]` in [index.md](index.md)), not by hand-copied UIDs here. This page indexes the
> registry and captures Business Central-specific contract *patterns* (which are design guidance, not governed
> identity).

Contracts realized against Microsoft Dynamics 365 Business Central. Cover: [index.md](index.md).

## Source Contracts (SC)
| SC | Version | Source objects | Status | Registry ref |
|---|---|---|---|---|
| _none authored for Business Central_ | | G/L Entry-class, Cust./Vendor Ledger Entry + Detailed entries, sales/purchase documents (planned candidates) | — | — |

## Admission Contracts (AC)
| AC | Version | SC bound | Status | Registry ref |
|---|---|---|---|---|
| _none authored for Business Central_ | | | — | `index.md` `admission_contract_versions: []` |

> Business Central is **`designed`** with **no evidence of any kind** — no executor, no simulator profile, no
> instance ever touched (see [evidence.md](evidence.md) and [index.md](index.md) `proof_status`). No
> Source/Admission Contracts have been authored. Populate this table and `admission_contract_versions[]` in
> [index.md](index.md) when the first Business Central SC/AC lands.

## Observation Contracts (OC)

### Candidate OC design notes (unverified — no OC authored)

These are **design notes from official-documentation research only**; no OC exists. Column-level facts below
were checked against the Microsoft Learn per-table application reference on 2026-07-13 (only the G/L Entry and
Detailed Cust. Ledg. Entry pages individually confirmed); every other column-level assertion is ⧗ pending
verification against the version-exact application reference before any OC is authored.

**1. Signed amount + dual debit/credit columns (contrast SAP `SHKZG`).** The
[G/L Entry table (ID 17)](https://learn.microsoft.com/en-us/dynamics365/business-central/application/base-application/table/microsoft.finance.generalledger.ledger.g-l-entry)
carries a **signed `Amount`** *and* separate **`Debit Amount` / `Credit Amount`** columns, plus
additional-currency variants (`Additional-Currency Amount`, `Add.-Currency Debit/Credit Amount`). This is
neither SAP's unsigned-amount + sign-indicator shape (`role: "sign_indicator"` OC pattern) nor Fusion's pure
dual-column shape: the candidate OC pattern must declare **which representation the metric observes** (signed
`Amount` vs the debit/credit pair) and must not silently mix them — sums over `Amount` and sums over
`Debit Amount − Credit Amount` are equivalent only if that equivalence is verified per version, not assumed.

**2. Detailed ledger entries carry application/remaining state.** AR/AP observation has two layers: the ledger
entry (Cust./Vendor Ledger Entry) and its **detailed ledger entries** (e.g.
[Detailed Cust. Ledg. Entry, ID 379](https://learn.microsoft.com/en-us/dynamics365/business-central/application/base-application/table/microsoft.sales.receivables.detailed-cust.-ledg.-entry):
`Entry Type` enum, `Amount` / `Amount (LCY)`, application and unapplication fields such as
`Applied Cust. Ledger Entry No.`, `Unapplied`, `Unapplied by Entry No.`). Payment application, discounts,
exchange-rate adjustments, and remaining-amount state are **detailed-layer facts**. An OC over ledger entries
and an OC over detailed entries observe **different layers of the same economics**; the contract must name its
layer explicitly so open-item metrics (aging, DSO/DPO-class) never silently mix them. The vendor-side analogue
(Detailed Vendor Ledg. Entry) is ⧗ not individually page-verified.

**3. Dimension-set model.** Ledger entries carry `Global Dimension 1/2 Code`, `Shortcut Dimension 3–8 Code`,
and a `Dimension Set ID` (fields verified on Table 17). Dimension *codes, values, and business meaning* are
per-customer configuration — segment semantics cannot be declared platform-universally; the OC/CC boundary must
bind dimension meaning per realization.

**4. Access-surface vs table shape.** The admissible object on Business Central online is the **API v2.0
entity or OData-exposed page** over the table, not the table itself ([index.md](index.md) §3). API entity
field names differ from table field names (camelCase API properties vs quoted table field captions); the OC
binds the access-surface shape, and the catalog must hold the entity↔table mapping (see
[catalog.md](catalog.md)).

## Canonical Contracts (CC)
| CC | Version | Grain | Business concepts resolved | Status |
|---|---|---|---|---|
| _none authored for Business Central_ | | | | — |

## Notes
- **Currency.** Ledger entries carry local-currency amounts alongside source/additional-currency variants
  (`Amount (LCY)`, `Source Currency Amount`, `Additional-Currency Amount` — G/L Entry and Detailed Cust. Ledg.
  Entry pages). Which variant a metric observes, and how multi-currency aggregation behaves, must be declared
  explicitly at the CC/MC boundary — ⧗ no research beyond the documented existence of the variants.
