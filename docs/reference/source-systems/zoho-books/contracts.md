---
uid: SRC-a4c6e9-contracts
slug: zoho-books-contracts
title: "Zoho Books — Contracts"
description: "Contracts authored against Zoho Books (none yet), and candidate contract-pattern notes for entity-typed credit documents and organization scoping."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Contract Registry, not an authority
domain: accounting
subdomain: zoho
focus: contracts
docket_of: zoho-books
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Zoho Books — Contracts

> **Projection, not authority (D526 Amendment 1).** Authority for contract content is the Contract Registry
> (`contract.*`); the exact contract-set participating in a proof is bound by the source-realization package
> (`source_realization_refs[]` in [index.md](index.md)), not by hand-copied UIDs here. This page indexes the
> registry and captures Zoho-Books-specific contract *patterns* (which are design guidance, not governed
> identity).

Contracts realized against Zoho Books. Cover: [index.md](index.md).

## Source Contracts (SC)
| SC | Version | Source objects | Status | Registry ref |
|---|---|---|---|---|
| _none authored_ | | invoices / bills / journals / chartofaccounts / contacts (planned) | — | — |

## Admission Contracts (AC)
| AC | Version | SC bound | Status | Registry ref |
|---|---|---|---|---|
| _none authored_ | | | — | `index.md` `admission_contract_versions: []` |

> Zoho Books is **`designed`** with **no evidence of any kind** — no simulator profile exists and no real
> organization has been touched (see [evidence.md](evidence.md) and [index.md](index.md) `proof_status`).
> No Source/Admission Contracts have been authored. Populate this table and
> `admission_contract_versions[]` in [index.md](index.md) when the first Zoho Books SC/AC lands.

## Observation Contracts (OC)

No OC has been authored against Zoho Books. The notes below are **candidate design patterns**
(⧗ unverified against contract authoring) recorded so the first authoring session does not rediscover them.

### Candidate pattern — entity-typed credit documents (no sign indicator)

Zoho Books does not use an in-row debit/credit sign-indicator field (contrast SAP `SHKZG` — see the
[sap-ecc docket](../sap-ecc/contracts.md)). Direction is carried by the **entity type**: credit notes and
vendor credits are separate API modules from invoices and bills. Any amount metric summing across document
families must resolve directional semantics at the **canonical boundary** (per-module OC → CC resolution),
never by admission-time mutation of amounts. Whether journal-entry lines carry an explicit debit/credit
attribute in the API shape is ⧗ pending verification against the official journals module reference during
OC authoring.

### Candidate pattern — organization scoping in the connection coordinate

Every Zoho Books read is scoped by `organization_id`. The SC/AC connection scope must pin the exact
organization(s); an OC over a module is meaningful only within one organization's data. Multi-org customers
mean multiple connection coordinates, not one merged stream.

## Canonical Contracts (CC)
| CC | Version | Grain | Business concepts resolved | Status |
|---|---|---|---|---|
| _none authored_ | | | | — |

## Notes
- **Currency.** Zoho Books organizations have a base currency; multi-currency documents carry a
  transaction currency and exchange-rate information. Exact field names, rounding behavior, and
  base-vs-transaction amount availability per module are ⧗ pending verification against the official
  per-module API reference — do not assume SAP-style dual-amount columns.
- **Report basis (accrual vs cash)** is a read-time projection in Zoho Books reporting, not a property of
  the transactional documents BareCount would admit — basis semantics belong at the canonical/metric
  boundary. See [index.md](index.md) §6.7.
