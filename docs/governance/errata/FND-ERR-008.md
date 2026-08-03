---
id: FND-ERR-008
title: "Legacy five-state lifecycle stated linear/no-rollback; the implementing machine was looser"
status: adopted
authority: authoritative
affected: The Contract Grammar §Lifecycle and deprecation policy (legacy contract-family envelope)
temporary_governance:
  - DEC-5a9dee
target_resolution: historical note on a frozen family — no text rewrite
opened: 2026-08-03
---

# FND-ERR-008 — Legacy five-state lifecycle stated linear/no-rollback; the implementing machine was looser

## Contradiction summary

Foundation's lifecycle section stated the legacy contract-family `governance.state` lifecycle as
*"a five-state linear lifecycle. Rollback does not occur within a version."* The implementing
state machine (`bc-core` `contract.service.ts`, `governanceMachine`) additionally allowed
`review → draft` (the `revertToDraft` operation) and a direct `draft → active` shortcut — a
backward arc and a skip the "linear, no rollback" sentence excluded. The looseness predates the
MCF era and was observed by the lifecycle authority study (register F-032 sharpening; also
DEC-29b518's X4 finding that `'released'` was a ghost state in the same vocabulary).

## Implementation behavior

The legacy machine operated with the looser transition set for the whole life of the legacy
family. No incident is attributed to the divergence; the family's corpus is empty since the M17
transition and its activation path is retired with a governed refusal (DEC-d9fa49).

## Resolution state

**Adopted as a historical note; deliberately NOT rewritten.** The family is frozen — rewriting
its grammar now would revise history rather than govern behavior (Invariant III discipline
applied to documentation). The lifecycle section carries a one-line pointer to this erratum. The
live families' lifecycles are stated per family with transition detail delegated to the generated
enforcement-surface map (DEC-5a9dee), which is the structural prevention of this erratum's class:
Foundation names states; enforcement detail lives where it is generated from fact.

## References

- DEC-5a9dee — family-scoped lifecycle + states-plus-delegation
- DEC-d9fa49 — legacy activation retirement (D547)
- Lifecycle authority study register F-032 + amendment ledger E-8
