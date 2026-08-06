---
uid: DEC-e1241a
title: "Source catalog artefacts carry identity; derivability verifies but never substitutes"
description: "A source catalog is admitted as a hash-identified artefact with declared extraction method and module set; re-derivation is a verification check, never a bootstrap authority."
status: proposed
date: 2026-08-06T03:07:04.085Z
project: platform
domain: sources
subdomain: source-catalog
focus: schema
---

# Source catalog artefacts carry identity; derivability verifies but never substitutes

## Context

Measured on 2026-08-06 against bc_platform_dev: all three `source_version` rows carry verification_status='unverified' and there is no artefact identity anywhere — no hash, no extraction record, no module-set declaration. A contract can name a version but nothing ties that version to a verifiable thing.

That gap is survivable while every admission is grandfathered. It stops being survivable the moment a source is admitted deliberately, because a governed admission whose subject has no identity is ceremony rather than governance. Odoo is about to be that first deliberate admission, so the substrate must exist before it rather than be retrofitted after.

The prohibition in point 4 corrects an error made in the design discussion itself. Having established that Odoo's catalog is re-derivable from `ir.model`, the author concluded it therefore need not be preserved and could simply be regenerated at bootstrap. The operator rejected this on the grounds that the platform is contract-based and an accidental version mismatch would be fatal — which is exactly Invariant IV's named failure mode, "implicit resolutions such as head version are not admitted". Re-derivability makes verification cheap; it is not a licence to skip preservation. The confusion is recorded because it is a natural one and will recur.

Point 3 encodes the distinction the operator drew between SAP and Odoo: SAP stayed in Mongo because its authenticity was never established, while Odoo is clean and official and can be onboarded directly. Making that a CHECK constraint rather than a convention means the rule cannot be quietly relaxed by someone who finds it inconvenient — the archived SAP scrape already claims `source: ddic` while admitting `confidence: low`, which is precisely the case where identical content and different provenance must be kept distinguishable.

Point 6 follows from 5 rather than from any judgement about SAP's data quality. There is no official manner in which a scraped catalog can currently re-enter; stamping it as governed would defeat the channel. Sequencing the withdrawal after Odoo contracts exist means the platform is never without an anchor — measured: the live chain is 27 observation contracts over 27 SAP tables, while ~30,350 admission contracts are orphan scaffolding referenced by nothing.

Point 7 follows from measurement, not assertion: `mcf.metric_variable_binding` resolves variables to business concepts and entities, and of 432 metric contract versions none reference a source table. The binding layer is where source-specificity is concentrated, which is what makes withdrawal an exercise of the design rather than damage to it.

Supporting artefacts: DESIGN-source-catalog-identity-and-sap-withdrawal-2026-08-06.md (sha256 7cc6ebe0...) and DBCP-source-catalog-identity-2026-08-06.md (sha256 639ceaac...), both in barecount-devhub artifacts/source-onboarding/. The DBCP is proposed and NOT applied.

## Decision

A source catalog version MUST be bound to a specific, hash-identified artefact before any contract may bind to it.

1. ARTEFACT IDENTITY. `source.source_catalog_artefact` hangs beneath `source.source_version` and carries `artefact_sha256` (unique), `artefact_uri`, `extraction_method_code`, extraction tool and version, `module_set_json`, counts, and extraction/verification timestamps. A version code such as "EHP8 6.0" is a label; the hash is the identity.

2. MODULE SET IS IDENTITY, NOT METADATA. `module_set_json` is NOT NULL. A catalog extracted from an instance with `mrp` installed describes a different system from one without. Without this, "Odoo 17.0" silently means whatever happened to be installed on extraction day.

3. EXTRACTION METHOD IS A FIRST-CLASS, QUERYABLE PROPERTY. `extraction_method_code` is one of `self_describing`, `vendor_supplied`, `scraped`. Two artefacts may hold identical content and still differ in kind, because one can be verified against its origin and the other cannot. A `scraped` artefact can NEVER be marked verified — enforced by CHECK (`extraction_method_code <> 'scraped' OR verified_at IS NULL`), not by documentation.

4. DERIVABILITY BUYS VERIFICATION, NEVER SUBSTITUTION. For a self-describing source, "verified" means re-derived from a live instance of the declared version and matched the recorded hash. Re-deriving the catalog AT BOOTSTRAP is prohibited: it is an implicit reference to head state, which Invariant IV does not admit, and it would let an instance upgrade silently rebind every contract beneath it without any version change or emitted evidence.

5. ADMISSION ROUTE FOLLOWS EXTRACTION METHOD. A self-describing source (Odoo via `ir.model`/`ir.model.fields`; SAP via DDIC read from a real system) is admitted directly into the source catalog. A source whose layout cannot be obtained first-hand is not admitted at all — it does not get a lower-confidence admission, it gets none.

6. SAP ECC AND S/4HANA ARE WITHDRAWN, CATALOG AND CONTRACTS. The present catalog came from a third-party scrape self-labelled `source: ddic, confidence: low`. Its contracts (SC/AC/OC/CC) are source-specific by construction and must be re-authored rather than re-pointed. Re-entry is blocked on first-hand DDIC access, which is an acquisition requirement, not a scheduling one.

7. WHAT SURVIVES A SOURCE CHANGE. BCF concepts and entities, and MC definitions, are source-agnostic and durable. SC/AC/OC/CC are the binding layer and are disposable per source. Concept-to-field knowledge is salvaged as a separate non-FK, hash-bound artefact carrying per-row provenance that distinguishes contract-authored mappings from advisory hints.

## Relationship to existing decisions

This ADR was first recorded without this section, having been written from memory rather than
from a decision search. The search was then run and found four adjacent decisions, none of
which had been cited. Recorded here rather than silently corrected, because the omission is
the kind that produces contradiction without anyone noticing.

**DEC-0b5a4c (D551) — source seed catalog to Postgres.** D551 as originally decided said Odoo
"seeds greenfield from the live pilot instance" through a `source.seed_source_table` seed
store. That store was created by its DBCP-1 and **removed by DBCP-2** following the operator's
design correction to direct admission; `source.*` today holds only the original six tables.
This ADR **refines and does not contradict** D551 as amended: extraction *from* a live instance
is exactly how a self-describing artefact is obtained. What is prohibited is re-deriving at
*bootstrap*, which is a different act — one is a dated extraction that produces a frozen,
hashed artefact, the other is an unversioned head resolution standing in for one.

**DEC-ddc13e (D500) — concept↔source soft-reference layer.** D500 establishes that
`concept_source_reference.source_field_id` FKs the onboarded catalog specifically so that
"FK-to-catalog forbids un-onboarded refs so SDG/SC/AC/OC share one source-of-truth". Point 7's
requirement that concept-to-field salvage live *outside* that table is therefore not a
workaround for an awkward constraint — it is a consequence of a deliberate one. The FK is
working as designed; salvage simply is not a reference and must not pretend to be.

**DEC-f4084d (D511) — `registerSourceStack`.** `POST /api/source-catalog/stacks` already
provides the governed one-call channel: registers the object if absent under the D284 veracity
gate, registers missing fields, authors SC v1 + AC v1, activates both. **Odoo admission uses
this existing channel.** This ADR adds artefact identity beneath it; it does not design a new
admission path, and nothing here justifies bypassing that endpoint or writing to `source.*`
directly.

**DEC-29f134 — runtime drift detection.** The admission-boundary probe diffs observed payload
field-sets against the source catalog and dispatches per the contract's validation policy. It
is therefore a consumer of catalog identity: a catalog that silently changed underneath a
contract would make drift detection compare against a moved reference and report nothing. This
strengthens point 4 rather than qualifying it, and it was missing from the consumer analysis in
the supporting design note.

## Consequences

- 241 green chain statuses go red or unresolvable, 80 active metric contract versions lose their chain, and the readiness dial darkens until Odoo contracts exist. Acceptable pre-production; stated so it is expected rather than discovered.
- The 91 `concept_registry.concept_source_reference` rows (39 ECC, 52 S/4HANA) are casualties of the withdrawal — `source_field_id` foreign-keys the catalog being removed, which is why the salvage in point 7 cannot live in that table.
- 58 `runtime.reader_flavor` rows bind to source versions and their fate is not decided here.
- Withdrawal must treat the JSONB `source_references` inside observation-contract bodies as the primary dependency: `observation_contract.source_contract_id` is NULL on all 27 rows, so the declared foreign key is unused and no constraint protects those references. The database will permit that delete silently where it refuses most others.

## Open items

- Six of the 27 live source contracts do not resolve to a system, probably a null `source_version_id`. Inference, not measurement — establish before withdrawal.
- DEC-… (D525) held that the audit programme stays on SAP ECC. Withdrawal either revisits that or takes an explicit carve-out.
- Scope of metric re-anchoring: one chain proven end to end before many, given 43 active metrics are known to sum across currencies and 343 grandfathered actives remain unresolved.

## Status note

`proposed`, not `decided`. The DBCP it depends on is unapplied and unauthorized, and three open items above are unresolved. It moves to `decided` when those close.
