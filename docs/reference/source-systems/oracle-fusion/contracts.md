---
uid: SRC-1b8e5a-contracts
slug: oracle-fusion-contracts
title: "Oracle Fusion Cloud ERP — Contracts"
description: "Contracts authored against Oracle Fusion (none), and candidate OC design notes: signed dual-column amounts and the XLA subledger→GL layering."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Contract Registry, not an authority
domain: enterprise-erp
subdomain: oracle
focus: contracts
docket_of: oracle-fusion
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Oracle Fusion Cloud ERP — Contracts

> **Projection, not authority (D526 Amendment 1).** Authority for contract content is the Contract Registry
> (`contract.*`); the exact contract-set participating in a proof is bound by the source-realization package
> (`source_realization_refs[]` in [index.md](index.md)), not by hand-copied UIDs here. This page indexes the
> registry and captures Fusion-specific contract *patterns* (which are design guidance, not governed identity).

Contracts realized against Oracle Fusion Cloud ERP. Cover: [index.md](index.md).

## Source Contracts (SC)
| SC | Version | Source objects | Status | Registry ref |
|---|---|---|---|---|
| _none authored for Fusion_ | | GL_JE_HEADERS/GL_JE_LINES-class, XLA_*, AP/AR (planned candidates) | — | — |

## Admission Contracts (AC)
| AC | Version | SC bound | Status | Registry ref |
|---|---|---|---|---|
| _none authored for Fusion_ | | | — | `index.md` `admission_contract_versions: []` |

> Oracle Fusion is **`designed`** with **no evidence of any kind** — no executor, no simulator profile, no
> instance ever touched (see [evidence.md](evidence.md) and [index.md](index.md) `proof_status`). No
> Source/Admission Contracts have been authored. Populate this table and `admission_contract_versions[]` in
> [index.md](index.md) when the first Fusion SC/AC lands.

## Observation Contracts (OC)

### Candidate OC design notes (unverified — no OC authored)

These are **design notes from official-documentation research only**; no OC exists, and every column-level
assertion is ⧗ pending verification against the release-exact
[Tables and Views for Financials](https://docs.oracle.com/en/cloud/saas/financials/25d/oedmf/index.html) pages
before any OC is authored.

**1. Signed dual-column amounts (contrast SAP `SHKZG`).** Fusion GL journal lines carry **separate debit and
credit amount columns** (entered- and accounted-currency variants) rather than a single unsigned amount plus a
sign-indicator field. The candidate OC pattern is therefore a **dual-column declaration** (debit column + credit
column, each with entered/accounted currency variants), not the SAP `role: "sign_indicator"` pattern. How
netting/direction is expressed at the canonical boundary is an authoring decision to be made when the first
Fusion amount OC is written — column names and semantics ⧗ verify per release.

**2. XLA subledger→GL layering.** Subledger transactions are accounted by **Create Accounting** into subledger
journal entries (XLA) and then transferred/posted to General Ledger
([Using Subledger Accounting, 25D](https://docs.oracle.com/en/cloud/saas/financials/25d/fausl/using-subledger-accounting.pdf)).
An OC over GL-layer objects and an OC over subledger-layer objects observe **different layers of the same
economics**; the contract must name its layer explicitly so metrics never silently mix them.

**3. Chart-of-accounts flexfield.** GL code combinations are key-flexfield segments whose meaning is
per-customer configuration. Segment semantics cannot be declared platform-universally; the OC/CC boundary must
bind segment meaning per realization.

## Canonical Contracts (CC)
| CC | Version | Grain | Business concepts resolved | Status |
|---|---|---|---|---|
| _none authored for Fusion_ | | | | — |

## Notes
- **Currency.** Fusion carries entered-currency and ledger(accounted)-currency amount variants on accounting
  lines. Which variant a metric observes, and how multi-ledger/multi-currency aggregation behaves, must be
  declared explicitly at the CC/MC boundary — ⧗ no research beyond the documented existence of both variants.
