---
id: FND-ERR-001
title: "Observation Contract outside six-family Foundation list"
status: adopted
authority: authoritative
affected: Foundation §2.2 (contract families)
temporary_governance:
  - DEC-0e3c64
  - DEC-136a23
  - DEC-1edaaa
target_resolution: Foundation v2 contract-families list
opened: 2026-04-23
---

# FND-ERR-001 — Observation Contract outside six-family Foundation list

## Contradiction summary

Foundation §2.2 enumerates six contract families — Source, Admission, Canonical, Metric, Action Definition, and (historically) Extraction. The platform implementation additionally defines an **Observation Contract**, which directs a Reader to select Source Contract fields, bind them to business vocabulary, and define the resulting Source Object shape. The Observation Contract is a first-class contract in the runtime, governed, versioned, and immutable — but it does not appear in Foundation's list.

## Implementation behavior

Every Reader operates under two contracts: an Admission Contract (ingress-side gating) and an Observation Contract (field selection, business-vocabulary binding, SO shape). The Observation Contract is emitted and enforced at the admission boundary. Its absence in Foundation is a gap in the Foundation text, not a gap in the platform.

## Temporary governance

The Observation Contract is governed by:

- **DEC-0e3c64** — introduced the Observation Contract as a directive to the Reader
- **DEC-136a23** — defined the Observation Contract's relationship to Canonical Mapping and the Reader flavor's `config_json.observation_schema`
- **DEC-1edaaa** — codified the Observation Contract as a first-class contract family for runtime purposes

Until Foundation v2 formally lists the Observation Contract, these three ADRs govern its place in the contract grammar. Chapter 4 of v3 describes the Observation Contract as an active contract family and labels the Foundation omission explicitly.

## Resolution state

**Adopted.** The platform's behavior is correct; the Observation Contract is a necessary part of the contract grammar. Foundation v2 will list the seven active families (Source, Admission, Observation, Canonical, Metric, Intervention, plus the one supporting schema Canonical Mapping) explicitly. This erratum closes when Foundation v2 publishes the revised contract-families list.

## References

- DEC-0e3c64 — Observation Contract introduction
- DEC-136a23 — Reader Observation Schema two-layer (see also FND-ERR-002)
- DEC-1edaaa — Observation Contract as first-class family
- Chapter 4 — The Contract Grammar (lists the 12-artifact taxonomy)
- Appendix A — Contract Schemas (observation-v1 body page)
- Foundation §2.2 — affected section
- v2 source: `system/foundation/patent/foundation-gaps.md`
