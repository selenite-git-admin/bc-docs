---
id: FND-ERR-007
title: "Live authority-creating families outside the grammar taxonomy"
status: adopted
authority: authoritative
affected: The Contract Grammar §Artifact classification; The Authority Model §Foundation authority (artifact count)
temporary_governance:
  - DEC-c3e57f
  - DEC-c48b0f
  - DEC-02f5a9
  - DEC-149ab2
  - DEC-b5c7ff
target_resolution: DEC-5a9dee taxonomy extension (this erratum's own adopting act)
opened: 2026-08-03
---

# FND-ERR-007 — Live authority-creating families outside the grammar taxonomy

## Contradiction summary

Foundation's grammar taxonomy enumerated twelve artifacts and contained no entry for three
families that create authority in the live platform: the **MCF Metric Contract** family
(`mcf.metric_contract_version`, the platform's central artifact since DEC-c3e57f, 2026-05), the
**Business Concept Registry** family (the vocabulary authority since DEC-02f5a9, 2026-05, present
in the chapter only as the primitives' successor callout), and the **Metric Directory Member**
family (governed intent identity since DEC-b5c7ff, 2026-07). The taxonomy's "Metric Contract" row
named the legacy family (DEC-29c324) — frozen at authoring (DEC-7bdd03), retired at activation
(DEC-d9fa49), corpus empty since the M17 transition. Every certification-lifecycle act since
DEC-c3e57f was formally outside Foundation's grammar — not forbidden by it, unknown to it.

## Implementation behavior

The live platform authored, certified, activated, withdrew, and demoted metric contracts under
the MCF seven-state machine; bound contract bodies to Business Concepts structurally
(DEC-a6258b, DEC-4a17e0); and required Metric Directory identity for governed lifecycle acts
(the C7 reintake gate's accepted-member tuple — operatively proven by DEC-21ca17, where 31
metrics could not complete a governed demotion without directory identity). The platform's
behavior was correct and ADR-governed throughout; the gap was in the Foundation text.

## Temporary governance

During the window (2026-05 through 2026-08) the families were governed by their own ADRs:
DEC-c3e57f + DEC-c48b0f (MCF lifecycle and certification), DEC-02f5a9 + DEC-149ab2 (Business
Concept Registry and its delegation), DEC-b5c7ff (Metric Directory). The lifecycle authority
study (Phase 1 register F-032, ratified with its amendment ledger) recorded the gap.

## Resolution state

**Adopted and resolved by DEC-5a9dee.** The taxonomy extends to fifteen artifacts under the
authority-creation admission test (a family enters iff it creates authority — DEC-c3e57f
Decision 3); the three families enter with identical shape (row, governing records, state names,
delegation of transition detail to the generated enforcement-surface map); the legacy Metric
Contract row flips to Superseded/Frozen. Recorded exclusions: the seed reservoir (informs, never
creates authority) and Reader flavors (deferred; Operating-Model runtime configuration). This
erratum closes with the publication of the revised taxonomy — it remains as the record of the
window and of the one-family-at-a-time admission pattern that produced it (see FND-ERR-001 for
the prior instance of the class).

## References

- DEC-5a9dee — the taxonomy extension (F-032 disposition)
- Lifecycle authority study: `barecount-devhub/artifacts/lifecycle-study/PHASE1-findings-register.md` (F-032) + `PHASE1-AMENDMENT-LEDGER.md`
- Design memo: `barecount-devhub/artifacts/lifecycle-study/DESIGN-MEMO-foundation-grammar-F032.md`
