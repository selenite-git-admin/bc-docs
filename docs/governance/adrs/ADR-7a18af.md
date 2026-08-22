---
uid: DEC-7a18af
title: "Source field capability is empirically probed and stored in a source_field_capability satellite — never derived from type"
description: "Field access capability (searchable/aggregatable/stored/etc.) is an empirical, probe-sourced observation stored in a new 1:1 source.source_field_capability satellite with provenance — not inferred from data type."
status: proposed
date: 2026-08-10T12:14:06.310Z
project: bc-core
domain: sources
subdomain: source-catalog/field-capability
focus: schema
---

# Source field capability is empirically probed and stored in a source_field_capability satellite — never derived from type

## Context

Foundation Invariant VI (evidence is emitted, not inferred) is the load-bearing constraint: capability MUST be probe-sourced with provenance (probed_at, probe_method_text), never inferred from type. This is the empirical mandate of KR-G G-6 ('searchability/computability of a field is empirical, not derivable — 13 false positives from derivation in v1') and its Odoo-19 witnesses S-2 (stock.quant.value readable but not searchable/aggregatable — read_group returns no key; value:sum works while bare value is silently dropped) and S-9 (res.partner.property_product_pricelist store=false). A catalog that carries type but not capability looks complete and gets a reader killed at runtime when it filters or aggregates on an incapable field.

Repair location A→E, DESIGN act (D541): capability is an admission-boundary (A) observation of the source's field access surface, materialized in catalog storage (E) as a source_field satellite. It is NOT compensation at a lower layer — there is no capability storage today to bypass. The downstream enforcement (reader/AC/OC authoring rejecting a domain filter or read_group on an incapable field) is execution OVER this design; building only a runtime 'reader died' detector would be a net, not a fix. B (contract grammar 'requires capability' declaration) is the NEXT step and cannot reference a capability the catalog does not yet hold — so B is not underspecified for this step; this catalog fact is its prerequisite.

Invariant III (immutability): capability is version-scoped (a field is under a specific source_version); a re-probe of the same field/version that disagrees with a stored verdict surfaces a contradiction (via probed_at + probe_run_ref history), it is not silently overwritten. Invariant I (meaning evaluated once): capability is observed once at scan and referenced thereafter, never re-derived per read.

Transport for the probe is settled independently: JSON-RPC (S-40 — Odoo-19 XML-RPC marshaller faults on None), live-proven client at bc-demo/simulator/adapters/odoo19ee/client.py. This ADR is the Scanner's schema prerequisite so Connector and Scanner can then proceed in parallel without the Scanner having to run twice. Alternative considered and rejected: extend source_field_typing with capability columns — rejected because it mixes structural and behavioral concerns and entangles two independent probe-provenance trails under one coherence trigger.

## Decision

A field's access capability against its live source system — whether it is readable, searchable (usable in a domain/WHERE filter without fault), aggregatable (usable as a read_group measure/groupby), stored, and sortable — is recorded in the source catalog as an EMPIRICALLY PROBED observation, stored in a NEW 1:1 satellite table `source.source_field_capability` keyed on `field_id` (FK → source.source_field, ON DELETE CASCADE), mirroring the existing `source.source_field_typing` satellite.

Columns (proposed): `field_id` uuid PK/FK; `is_readable` boolean; `is_searchable` boolean; `is_aggregatable` boolean; `is_stored` boolean; `is_sortable` boolean; `probe_method_text` text (how observed, e.g. 'jsonrpc:search1+read_group'); `probed_at` timestamptz; `probe_run_ref` text (scanner run / evidence pointer, nullable); `created_at`/`updated_at`. Row-present ⇒ probed; row-absent ⇒ unprobed (tri-state: no row = unknown, row+false = probed-negative, row+true = probed-positive). All booleans NOT NULL within a present row.

WHY A SATELLITE, NOT COLUMNS ON source_field: source_field is already at the D162 20-column cap; capability is a distinct concern from structural typing (behavioral access vs shape), so it earns its own satellite rather than bloating source_field_typing (whose coherence CHECK + trigger stay clean). WHY REAL COLUMNS, NOT JSONB: is_searchable/is_aggregatable are queried directly by the Scanner and by reader-authoring ('give me the searchable fields') ⇒ D162 Rule 1 forbids JSONB for queryable data.

The Scanner populates this satellite by probing the live system (attempt a bounded search domain and a read_group per candidate field); it never derives capability from the ORM ttype or the stored/computed flag alone.
