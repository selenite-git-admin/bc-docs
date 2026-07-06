---
id: FND-ERR-002
title: "Reader Observation Schema dual-layer"
status: adopted
authority: authoritative
affected: Foundation §3.3 (admission contracts)
temporary_governance:
  - DEC-136a23
target_resolution: Foundation v2 reader-observation semantics
opened: 2026-04-23
---

# FND-ERR-002 — Reader Observation Schema dual-layer

## Contradiction summary

Foundation §3.3 treats field mapping at the admission boundary as a property of the Admission Contract. In the platform implementation, field mapping is split across two layers: a governed layer in the Observation Contract (`observation_field_map`) and a denormalized runtime copy in the Reader Flavor (`config_json.observation_schema`). The denormalized copy is derived from the governed layer at Reader activation; runtime admission reads the flavor copy for performance reasons.

## Implementation behavior

- **Governed layer (authoritative).** `observation_field_map` lives on the Observation Contract. It is versioned, immutable once published, and subject to contract-chain governance.
- **Runtime copy (derived).** `config_json.observation_schema` lives on the Reader Flavor. It is derived from the Observation Contract at Reader activation; runtime admission reads this copy.

The two layers exist for different purposes: the governed layer supports chain audit and version coexistence; the runtime copy supports admission performance and avoids cross-table lookups on every Source Object emission. The runtime copy is never modified independently of the governed layer; the activation process regenerates it.

## Temporary governance

**DEC-136a23** governs the dual-layer model. The ADR names the authoritative layer, requires derivation from it at activation time, and prohibits divergence between the two.

## Resolution state

**Adopted.** The dual-layer pattern is correct and necessary for the platform's admission performance posture. Foundation v2 will describe admission-time field mapping as a two-layer artifact: governed contract + derived runtime schema. This erratum closes when Foundation v2 publishes the revised admission model.

## References

- DEC-136a23 — Reader Observation Schema two-layer model
- FND-ERR-001 — Observation Contract inclusion (related)
- Chapter 8 — Admission and Observation (describes the dual-layer behavior)
- Foundation §3.3 — affected section
- v2 source: `system/foundation/patent/foundation-gaps.md`
