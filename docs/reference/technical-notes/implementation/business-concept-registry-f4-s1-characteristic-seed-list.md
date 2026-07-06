---
uid: business-concept-registry-f4-s1-characteristic-seed-list
title: Business Concept Registry — F4-S1 v1 characteristic seed list
description: F4-S1 seed-content artifact — the curated v1 governed characteristic seed list, 24 operator-approved Registry-authored property-characteristics. The BareCount Concept Registry is the authority; external standards and the bc_seed Mongo OAGIS catalog are citation evidence; legacy BF/BO/CF are coverage hints only. Accepted 2026-05-21; the 24 terms operator-approved at the content-review lock 2026-05-21.
status: accepted
date: 2026-05-21
project: bc-docs
domain: contracts
subdomain: catalog
focus: governance
---

# Business Concept Registry — F4-S1 v1 characteristic seed list

> **What this is.** The **F4-S1** deliverable of the accepted F4 design note
> (`business-concept-registry-f4-governed-vocabulary-seed-design.md`) — the
> curated **v1 governed characteristic seed list**, the seed-content review
> packet of that note's §3. It is a **data artifact** — curated, not a
> mechanical import (D2), and not executable: F4-S2 builds the seed runner,
> F4-S3 executes. The artifact is `accepted`; following the 2026-05-21
> content-review pass the **24 surviving terms are operator-`approved`** (§9).
> It re-bases the list on the **three-tier authority hierarchy** of §1.

## 1. Method, authority hierarchy, and curation principle

**The authority hierarchy.** F4 does not "seed from OAGIS" or "seed from ISO."
It **authors BareCount characteristic terms**, citing external evidence where
useful. Three tiers, in strict order of authority:

1. **The BareCount Concept Registry is the authority.** F4 authors each
   characteristic term, its definition, and its identity. The Registry owns the
   final term.
2. **External standards and the `bc_seed` Mongo seed catalogs are
   citation/reference evidence** — used in curation, never source authority.
   The **primary** candidate-evidence source is **`bc_seed.seed_oagis_components`**
   — the OAGIS 10.12 catalog, read directly from MongoDB, field-level (`name`,
   `representation_term`, `semantic_role`, `description`, `cardinality`,
   `source_url`). Secondary: **ISO 11179** (the formation discipline / MDR
   pattern — not term authority); **UN/CEFACT CCTS / Core Component Library**
   where available; **ISO 20022** only where a property-level message element
   directly supports a term; **XBRL / IFRS** mostly reporting-concept evidence
   (Phase G metric / canonical), cited only where one directly supports a
   property characteristic.
3. **Legacy `contract.business_field` / `business_object` / `canonical_field`
   are coverage hints only** — see §2.

**What a characteristic is.** A characteristic is "the *what* of a value
property" (F2) — the ISO 11179 **property** component of a data element. It
**excludes** the **representation term** (`business_concept.representation_term`
records that separately — the 15-term set is F2-seeded) and it **excludes** any
**object class / entity reference** (that is the `entity` the concept attaches
to, or a `kind='reference'` target).

**Candidate-evidence finding.** `bc_seed.seed_oagis_components` holds 158 OAGIS
nouns with 888 distinct field names — each field pre-decomposed into `name`,
`representation_term`, `semantic_role`, and a `description`. This is the
correct primary citation source: OAGIS fields sit at property granularity. The
legacy `contract.business_field` table was itself *generated from* this OAGIS
catalog (its rows carry the OAGIS-recorded `bf_name`) — it is the badly-formed
downstream layer, not a source (§2).

**Curation principle.** v1 selects **universal, reusable value-property
characteristics**, named by their semantic noun with the representation-term
suffix excluded. Terms are authored **in normalized form** — lowercase,
single-spaced — so `term` is identical to its normalized form for every entry
(§4). The list is **deliberately bounded** (D8): 24 terms — a clean
synonym-check baseline, not an exhaustive catalogue. The vocabulary is
governed-*open*; the BCF panel grows it after Phase B.

## 2. Legacy catalog posture

The legacy `contract.business_field` (BF), `business_object` (BO), and
`canonical_field` (CF) catalogs are **downstream artifacts of the BF/BO/CF
three-primitive model that DEC-02f5a9 supersedes**. They are **wrongly formed**
for the Registry: BF `property` values are OAGIS-derived but mangled into
representation-term-suffixed compounds (`unit_price_amount`,
`tax_rate_percent`), and the catalog is heavily polluted with entity-reference
and identifier properties.

Their standing in F4 is **coverage hint only**:

- They are **not imported** — not in whole, not in part.
- They are **not trusted for naming, definition, or identity** — none of those
  is taken from a BF/BO/CF row.
- **Frequency in BF/BO/CF is replication evidence, not correctness evidence** —
  a property that recurs across the catalog recurs because an OAGIS-derived
  artifact was copied, not because the concept is well-formed. No term in §3 is
  justified by a BF/BO/CF count.
- The single legitimate use: a BF/BO/CF occurrence may **hint that a concept
  appears in onboarded data** — a coverage signal that the v1 baseline is not
  missing something the platform already meets. Even that is confirmed against
  the OAGIS source, never asserted from the legacy catalog.

## 3. The v1 characteristic seed list

24 approved characteristics, Registry-authored. The content-review pass of
2026-05-21 (decisions 1–7, §9) flipped every surviving term `proposed →
approved`. The citations column records the external evidence consulted in
curation; it is not an authority claim — the authoring authority is the
Registry (§1).

| # | term | definition | normalized form | citations (OAGIS / standards — evidence, not authority) | synonym review | status |
|---|---|---|---|---|---|---|
| 1 | document date | Calendar date on which a business document is issued or formally dated. | `document date` | OAGIS 10.12 field `Document Date Time` (rep-term DateTime, role temporal); rep-term suffix excluded. | Checked against the other temporal characteristics — distinct events. | approved |
| 2 | posting date | Calendar date on which a transaction is recorded in the accounting ledger. | `posting date` | BareCount fiscal-period domain (D363–D365) — primary basis. OAGIS `Transaction Date Time` cited for the temporal pattern. | Distinct from document date — the ledger-recording event, not document issuance. | approved |
| 3 | due date | Calendar date by which an obligation or payment must be settled. | `due date` | OAGIS 10.12 field `Due Date Time` (DateTime, temporal). ISO 20022 payment messages carry due-date elements. | — | approved |
| 4 | effective date | Date from which a record, rate, or agreement becomes valid. | `effective date` | OAGIS components `Effective Time Period` / `Effectivity` — the validity-window start. | Paired with expiry date as a validity window; distinct endpoints. | approved |
| 5 | expiry date | Date after which a record, rate, or agreement ceases to be valid. | `expiry date` | OAGIS components `Effective Time Period` / `Effectivity` — the validity-window end. | Paired with effective date; distinct endpoints. | approved |
| 6 | unit price | Price of a single unit of a product or service. | `unit price` | OAGIS 10.12 field `Unit Price`. | — | approved |
| 7 | tax | Charge levied by a governing authority on a transaction, income, or holding. | `tax` | OAGIS 10.12 component `Tax`. | Kept distinct from tax rate — `tax` is the levied charge, `tax rate` the percentage. | approved |
| 8 | discount | Reduction granted against a price or an amount owed. | `discount` | OAGIS components `Amount Discount` / `Allowance` ("the discount or allowance the customer is to receive"). | — | approved |
| 9 | freight charge | Charge incurred for transporting goods. | `freight charge` | OAGIS 10.12 field `Freight Charge Amount` (Amount, measure); rep-term suffix excluded. | Renamed from `freight` at the 2026-05-21 content-review lock — `freight charge` is unambiguous (the charge, not the cargo). | approved |
| 10 | credit limit | Maximum outstanding amount permitted for a customer or account. | `credit limit` | OAGIS 10.12 field `Total Credit Limit Amount` (Amount, measure); also `Customer Credit`. BareCount credit-management domain. | A master-data credit ceiling — a control parameter, not an owed or computed amount. | approved |
| 11 | exchange rate | Rate at which an amount in one currency is converted into another. | `exchange rate` | OAGIS 10.12 component `Currency Exchange Rate`. BareCount exchange-rate reader architecture (DEC-b10dad). | — | approved |
| 12 | tax rate | Rate at which tax is applied to a taxable base. | `tax rate` | OAGIS 10.12 component `Tax` (carries rate detail). | See tax — distinct concept. | approved |
| 13 | interest rate | Rate charged or earned on a principal amount over a period of time. | `interest rate` | BareCount finance domain — primary basis. OAGIS `Interest Charge` cited as adjacent evidence. | — | approved |
| 14 | ordered quantity | Number of units requested on an order. | `ordered quantity` | OAGIS order-quantity fields (`Open Purchase Order Quantity` and the order-line quantity context). | Kept distinct from delivered quantity — the two differ by delivery variance. | approved |
| 15 | delivered quantity | Number of units actually delivered or received. | `delivered quantity` | OAGIS fields `Shipped Sales Order Quantity` / `Product Quantity Shipment Receipt`. | See ordered quantity. | approved |
| 16 | gross weight | Weight of goods including packaging and container. | `gross weight` | OAGIS 10.12 field `Gross Weight Measure` (Quantity, measure); rep-term suffix excluded. | Kept distinct from net weight — gross includes packaging, net excludes it. | approved |
| 17 | net weight | Weight of goods excluding packaging and container. | `net weight` | OAGIS 10.12 field `Net Weight Measure` (Quantity, measure); rep-term suffix excluded. | See gross weight. | approved |
| 18 | quantity on hand | Number of units of an item currently held in inventory. | `quantity on hand` | OAGIS 10.12 field `Available Inventory Quantity`. BareCount inventory domain (Inventory Position, F1 §1). | Observed point-in-time stock level — not a metric unless computed over time / grain. Distinct from ordered/delivered quantity (an inventory level, not a transaction count). | approved |
| 19 | status | Current lifecycle or processing state of a record. | `status` | OAGIS 10.12 component `Status` ("indicates the status of the associated object"). | Distinct from reason — state vs cause. Broad but role-specific (always a lifecycle/processing state). | approved |
| 20 | reason | Stated cause or justification for an action, state, or adjustment. | `reason` | OAGIS 10.12 field `Reason Code` (Code, dimension); rep-term suffix excluded. | Distinct from status — the cause, not the state. | approved |
| 21 | payment terms | Agreed conditions governing the timing and manner of payment. | `payment terms` | OAGIS 10.12 component `Payment Term`. | — | approved |
| 22 | description | Explanatory prose characterizing an item, document, or record. | `description` | OAGIS 10.12 field `Description` (Text, descriptor). | Kept distinct from note — `description` is the primary descriptive text; `note` is supplementary annotation. | approved |
| 23 | note | Free-form remarks or commentary attached to a record. | `note` | OAGIS 10.12 field `Note` (Text, descriptor). | Kept distinct from description — `note` is supplementary free-form annotation; `description` is the primary descriptive text. | approved |
| 24 | line number | Ordinal position of a line item within a multi-line document. | `line number` | OAGIS 10.12 field `Line Number Identifier` (Identifier, identifier); rep-term suffix excluded. | — | approved |

## 4. Totals and checks

- **Total count:** **24** approved characteristics — the prior draft's 26 less
  `cost` (held back) and `outstanding balance` (deferred at the 2026-05-21
  content-review lock — §6).
- **Normalized-uniqueness check — PASS.** Every term is authored in normalized
  form (`normalizeName` = trim → collapse `[\s_-]+` → lowercase), so the `term`
  and `normalized form` columns are identical for all 24 rows. The 24
  normalized forms are pairwise distinct — verified by inspection, including
  the renamed `freight charge`. The list will pass `seedGovernedVocabulary`'s
  per-term `assertCharacteristicTermAvailable` check against an empty
  `characteristic` table, and the F4-S2 runner's normalized pre-filter has no
  intra-list duplicate to drop.
- **Representation-term overlap check — PASS.** No term — including the renamed
  `freight charge` — equals any of the 15 F2-seeded representation terms
  (`amount, code, count, date, date_time, duration, identifier, indicator,
  measure, name, percentage, quantity, rate, ratio, text`). Characteristics and
  representation terms are kept lexically disjoint.

## 5. Explicit out-of-scope

This artifact is **characteristics only**. Out of scope, by the F4 design note:

- **Representation terms** — F2-seeded (15 rows), FK-enforced. Never F4.
- **Entities** — cert-gated authoring acts via `createEntity` / the BCF panel;
  never seeded (F4 design note §1).
- **Aliases** — out of v1 (D6); adding them requires an explicit F3 design-note
  amendment.
- **Business concepts and lifecycle transitions** — cert-gated; not vocabulary.
- **Execution** — F4-S3, operator-gated, against `bc_platform_dev` only.
- **The seed runner, data file, and `seedGovernedVocabulary` change** — F4-S2.

## 6. Candidate terms rejected, merged, or deferred

The following candidates were **excluded from the v1 approved list** —
rejected, held back, or deferred:

- **Entity-reference fields — rejected by definition.** OAGIS reference/party
  fields — `Party Identifier`, `Source Identifier`, `Document Reference`,
  `Supplier Party`, `Ship To Party`, `Carrier Party`, `Purchase Order
  Reference`, `Sales Order Reference`, `Contract Reference` — are entity
  references; in the Registry they are `kind='reference'` business concepts
  (`reference_role` + `target_entity_id`), not value-property characteristics.
- **Representation terms — rejected as wrong vocabulary.** OAGIS fields that
  *are* representation terms — `Identifier`, `Type Code`, `Action Code`,
  `Amount` (bare), `Name`, `Code` — belong to the F2-seeded `representation_term`
  set (FK-enforced), not the characteristic vocabulary.
- **Reporting concepts — out of F4 scope.** XBRL US-GAAP / GAAP and IFRS
  taxonomy concepts (`ifrs-full:Assets`, `us-gaap:*`) are financial-statement
  line items / reporting concepts — Phase G metric and Canonical-Contract
  evidence, not value-property characteristics.
- **Legacy compounds — not imported.** Legacy `business_field.property` forms
  (`unit_price_amount`, `tax_rate_percent`, `document_date_time`) are the
  badly-formed downstream of the superseded BF/BO/CF model. Not imported;
  coverage hints only (§2).
- **OAGIS structural / technical fields — rejected.** `Extension`,
  `Attachment`, `Metadata Reference`, `Security Classification`, `UUID` — OAGIS
  message-structural or technical fields, not business characteristics.
- **`outstanding balance` — deferred.** Deferred — aggregate/net position, not
  a v1 raw characteristic. A point-in-time net AR/AP position sits at the
  metric / canonical layer; it belongs to Phase G / MCF, or to a carefully
  framed concept authored after the Registry is live. It was a proposed term in
  the prior draft and was removed from the v1 approved list at the 2026-05-21
  content-review lock (decision 1).
- **`cost` — held back.** Too generic ("cost of what?"), and no clean standards
  citation — OAGIS carries only specific charge fields. The panel can author
  specific cost characteristics later (governed-open).
- **`type` / `classification` — deferred.** Too generic to anchor a synonym
  check at v1 (almost every record carries a "type"). `status` and `reason`,
  by contrast, are kept — broad but role-specific (a state, a cause). Deferred
  to panel-grown additions (decision 4).
- **Compound forms not merged.** `tax` and `tax rate` are kept as two distinct
  characteristics — the levy and the percentage are different property-concepts.
  `Document Date Time` → `document date`; v1 is intentionally date-grained
  (decision 7).

## 7. Data-hygiene notes (non-blocking)

Surfaced while inventorying `bc_seed`; neither blocks F4:

1. **Duplicate ISO-20022 collections.** `bc_seed` carries both `seed_iso_20022`
   (6 docs) and `seed_iso20022` (3 docs) — different names *and* different
   document shapes. They should be reconciled into one collection in a later
   cleanup.
2. **Undeclared `bc_seed` Mongo dependency.** bc-core reads the `bc_seed`
   MongoDB (`mongodb://localhost:27017`; env `SEED_MONGO_URI` / `SEED_MONGO_DB`)
   through `oagis-seed.service.ts` and `seed-metrics.service.ts`, but the
   dependency is not declared in `docker-compose*.yml` or `.env`. It should be
   declared so the dependency is discoverable and provisionable.

## 8. Review questions — resolved

The prior draft's open questions were resolved at the 2026-05-21
content-review lock:

1. **Date granularity** — accepted. The five temporal characteristics keep the
   date-grained form for v1; `Document Date Time` cites to `document date`
   (decision 7).
2. **Term casing** — the 24 terms are approved as authored: normalized form
   (lowercase, single-spaced), so `term` == `normalized form`.
3. **v1 size** — locked at 24 (the prior 26 less `cost` and the deferred
   `outstanding balance`).
4. **Generic classifiers** — `status` and `reason` kept for v1 (broad but
   role-specific); `type` / `classification` remain deferred (decision 4; §6).

## 9. Status

`accepted` — the F4-S1 seed-content artifact, accepted 2026-05-21, re-based on
the three-tier authority hierarchy (§1). At the 2026-05-21 content-review lock
(decisions 1–7) the 25 proposed terms were resolved to a **24-term
operator-approved list**: `outstanding balance` was deferred (§6, decision 1)
and `freight` was renamed to `freight charge` (decision 2); the surviving 24
terms are `operator approval status: approved`. This approved 24-term content
is the seed content that gates F4-S3 execution. F4-S2 builds the runtime form
of this list against this approved content.
