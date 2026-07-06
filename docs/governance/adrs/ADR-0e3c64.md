---
uid: DEC-0e3c64
title: "Contract Chain Clarification — Observation Contract is Canonical-Chain (Mapping Binding), not Source-Chain"
description: "Observation contract + field map belongs to Canonical Chain (meaning resolution), not Source Chain. DB tables stay, conceptual grouping changes."
status: implemented
subdomain: contract-chain
focus: oc-as-canonical-chain
date: 2026-03-24
project: bc-core
domain: database
refs:
  - type: decision
    label: "D044"
  - type: decision
    label: "D054"
  - type: decision
    label: "D200"
authority: authoritative
migrated_from: legacy v2 archive
---


# Contract Chain Clarification — Observation Contract is Canonical-Chain (Mapping Binding), not Source-Chain

## Context

Foundation spec: meaning resolution happens ONLY at the Canonical Evaluation Boundary. The field map (source_field → business_field) IS meaning resolution wiring. Contract Registry spec (D044, D054) defines the Mapping Binding as a first-class Canonical Chain entity. The observation_field_map belongs there, not with the Source Chain. DB tables stay — only UI presentation and conceptual grouping changes.

## The Clarification

The `observation_contract` + `observation_field_map` belongs to the **Canonical Chain**, not the Source Chain. It performs meaning resolution wiring (source_field → business_field), which is the Canonical Evaluation Boundary's concern.

The Contract Registry spec explicitly names a "Mapping Binding" as a first-class entity (D044, D054 Pattern A). Our `observation_contract` + `canonical_mapping` together form this Mapping Binding.

## Chain Assignment

**Source Chain** (source-specific, structural):
- Source Contract — expected schema of projected fields
- Admission Contract — accept/reject rules, structural validation

**Canonical Chain** (meaning resolution):
- Canonical Contract — universal CO form (references BO)
- Mapping Binding = `canonical_mapping` (per-CO resolution rules) + `observation_contract` + `observation_field_map` (per-source field resolution)

**Metric Chain** (measurement):
- Metric Contract, Intervention Contract

## UI Consequence

The sidebar groups contracts by chain. "Observation Contract" label is retired in UI — the content surfaces under "Mapping Bindings" in the Canonical Chain group.

## DB Consequence

No table restructure. Tables remain as-is. The observation_contract is presented as the field-level detail within a Mapping Binding. The canonical_mapping is the container.

## Field Affinity (new concept)

Pre-contract soft suggestion linking `source.source_field` to `contract.business_field`. Not governed, not immutable. Used by D200 AI mapper and Source Catalog UI.

New table: `source.source_field_affinity` (source_field_id, business_field_id, confidence, provenance_code, note_text, created_at). Lives in source schema because it's metadata about source fields.

## Consequences

N/A
