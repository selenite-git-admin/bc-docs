---
uid: SRC-a3c7e1-contracts
slug: salesforce-contracts
title: "Salesforce — Contracts"
description: "Contracts authored against Salesforce, and the soft-delete / multi-currency OC patterns for Salesforce sObjects."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Contract Registry, not an authority
domain: crm
subdomain: salesforce
focus: contracts
docket_of: salesforce
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Salesforce — Contracts

> **Projection, not authority (D526 Amendment 1).** Authority for contract content is the Contract Registry
> (`contract.*`); the exact contract-set participating in a proof is bound by the source-realization package
> (`source_realization_refs[]` in [index.md](index.md)), not by hand-copied UIDs here. This page indexes the
> registry and captures Salesforce-specific contract *patterns* (which are design guidance, not governed identity).

Contracts realized against Salesforce. Cover: [index.md](index.md).

## Source Contracts (SC)
| SC | Version | Source objects | Status | Registry ref |
|---|---|---|---|---|
| _none authored for a real Salesforce org_ | | Opportunity / Account / Contact (planned) | — | — |

## Admission Contracts (AC)
| AC | Version | SC bound | Status | Registry ref |
|---|---|---|---|---|
| _none authored for a real Salesforce org_ | | | — | `index.md` `admission_contract_versions: []` |

> Salesforce remains **`designed`** — the bc-sdg simulator run and executor unit tests are ungoverned historical
> background and do **not** establish `shape_tested` (see [evidence.md](evidence.md) and [index.md](index.md)
> `proof_status`). No Source/Admission Contracts have been authored against a real Salesforce org yet. Populate
> this table and `admission_contract_versions[]` in [index.md](index.md) when the first real-org SC/AC lands.

## Observation Contracts (OC)

### Soft-delete visibility pattern (candidate — no OC authored)

Salesforce records deleted or merged are **soft-deleted**: they move to the recycle bin with `IsDeleted = true`.
The standard Query resource excludes them; the
[QueryAll resource](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_queryall.htm)
includes them until recycle-bin purge — after purge they are unrecoverable via the API. An OC over a Salesforce
sObject must therefore **declare its deletion-visibility stance explicitly** rather than inherit whichever
endpoint the reader happened to call:

| Concern | Pattern |
|---|---|
| Deleted-record visibility | Declare Query (live-only) vs QueryAll (including soft-deleted) as an explicit OC-level stance; if soft-deleted rows are admitted, `IsDeleted` must be a declared field, never inferred |
| Merge lineage | Merges soft-delete the losing record and re-parent children; a delta strategy on `SystemModstamp` alone does not surface the loser unless QueryAll semantics are declared |
| Purge horizon | Recycle-bin purge silently removes soft-deleted rows from API visibility — watermark gaps across long outages are a realization-level risk to record |

### Multi-currency pattern (candidate — no OC authored)

In multi-currency orgs, amount fields carry the record's `CurrencyIsoCode`. Cross-currency aggregation is a
**canonical-boundary concern** — never a reader-side conversion, and never a metric-contract literal (metrics
stay source-agnostic). The OC declares the currency-code field alongside each amount field so the canonical
layer can bind currency semantics explicitly. (⧗ exact official multi-currency citation pending in
`official_research_refs[]` — see [index.md](index.md) §6.6.)

These are **candidate design patterns**, not governed contract identity: no OC exists against Salesforce yet.

## Canonical Contracts (CC)
| CC | Version | Grain | Business concepts resolved | Status |
|---|---|---|---|---|
| _none authored for a real Salesforce org_ | | | | — |

## Notes
- **Record types.** One physical sObject (e.g. Opportunity) can carry multiple business record types via
  `RecordTypeId` with distinct picklist and process semantics. Discrimination belongs at the canonical/binding
  layer — a metric contract must not embed record-type literals.
- **Field-level security.** The observable schema is the integration user's schema: Describe results and query
  field access are filtered by profile/permission sets. Contract authoring and catalog verification must run
  under the production integration identity, or the declared shape will not match the realized shape.
