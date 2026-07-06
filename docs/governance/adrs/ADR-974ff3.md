---
uid: DEC-974ff3
title: "Source-Chain Contract Binding Model & Meta-Schema Correction"
description: "Superseded binding model that linked source-chain contracts via meta-schema. Replaced by per-family binding tables."
status: superseded
date: 2026-03-10
project: bc-core
domain: database
refs:
  - type: decision
    label: "D044"
authority: retired
migrated_from: legacy v2 archive
---


# Source-Chain Contract Binding Model & Meta-Schema Correction

## Context

Superseded by D069 (DEC-36d78f). D055 removed output_fields from Extraction Contract with rationale "data shape is Source Contract responsibility." D069 corrects this: (1) Extraction Contract is retired entirely — Flavor + Observation Schema carry extraction config. (2) Source Contract scope narrowed to projected fields, not full table schema. (3) Field selection is Reader's business awareness via Observation Schema, not a contract-level concern. The removal of output_fields without providing an alternative field selection mechanism was the root cause of the "dumb pipe" problem — D069 fills this gap.

## Contract Binding Model (corrected)

The three source-chain contracts bind as follows:

| Contract | Concern | Lives with | Points to | Relation |
|----------|---------|------------|-----------|----------|
| **Extraction** | How to pull (method, scheduling, incremental) | Reader | Source entity | N per Reader (one per entity it extracts from) |
| **Source** | What shape to expect (versioned schema declaration) | Source Object | — | 1 per source object |
| **Admission** | What fields to admit, identity, rules | Reader | Source entity | N per Reader (one per entity + business purpose) |

### Key Principles

1. **Extraction is a Reader concern**, not an object concern. Each Reader has N extraction contracts — one per source entity it reads from. The extraction contract references `source_entity` (pointer) but is governed as Reader configuration. Multiple extraction contracts per Reader are expected (full load vs CDC, different schedules).

2. **Source Contract is the only object-scoped contract** in the source chain. It freezes a versioned schema declaration for a source object. The Source Catalog provides discovery (what exists now); the Source Contract provides governance (what I expect, with drift detection). One per source object.

3. **Admission is a Reader concern**, bound per Reader + source entity. Declares which fields to admit, identity semantics, admissibility rules, and validation policy. Multiple admission contracts per Reader are expected (one per source object the Reader reads from).

4. **Source Object page shows Source Contract only.** Extraction and Admission authoring happens on the Reader page. Source Object page may show read-only cross-references ("Referenced by N admission contracts").

### Meta-Schema Corrections Required

**extraction-v1.json:**
- **Remove `output_fields`** — declaring the shape of extracted data is the Source Contract's responsibility (`schema` field). Having both is a spec leak and creates redundancy.
- Keep `source_system`, `source_entity` (pointer to what is being extracted)
- Keep `extraction_method`, `endpoint`, `parameters`, `incremental`, `scheduling` (core extraction concerns)

**canonical-v1.json:**
- **Remove `source_dependencies` and `canonical_mapping`** from required fields — D044 moved source-to-canonical wiring into the Canonical Mapping Binding. The canonical contract should only declare `evaluation_tier`, `resolved_schema`, `business_key_fields`, and `semantic_rules`.
- `join_context` also moves to Mapping Binding (it's source-wiring, not canonical form)

**source-v1.json:** No changes needed — clean as-is.

**admission-v1.json:** No changes needed — clean as-is.

### Supersedes / Corrects
- Corrects the implicit 1:1:1 model (one extraction + one source + one admission per object) that was assumed in the Source Catalog UI implementation
- Aligns meta-schemas with D044 (Canonical Mapping Binding split)
- Clarifies Reader operational model (Component Ref 090 §4.2, §7.1) relationship to contract governance

## Consequences

N/A
