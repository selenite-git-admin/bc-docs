---
uid: DEC-4c8bee
title: "The certification panel's calibration corpus is a hybrid: a real LC5-validated positive, oracle-proven value defects, and retained meaning defects"
description: "Amends DEC-05815d's calibration-corpus methodology. The positive is a real certified, LC5-validated metric (DSO d0f73360) instead of a constructed control. Value-moving defect classes become LC5-proven negatives. Meaning-only classes (currency semantics, definition ambiguity, definition-contract fidelity) stay as constructed negatives, decided against cited declared-semantics facts. An oracle proves value fidelity, not meaning fidelity."
status: proposed
date: 2026-10-03T13:13:03.705Z
project: bc-core
domain: metrics
subdomain: metric-certification/panel-calibration
focus: governance
---

# The certification panel's calibration corpus is a hybrid: a real LC5-validated positive, oracle-proven value defects, and retained meaning defects

## Summary

The constructed calibration positive had no declared ground truth: it carried a definition-contract defect, inherited by every negative (TSK-9ce7f9). A committed LC5 oracle gives value labels an emitted ground truth. Meaning-only defects are invisible to an oracle, so they stay as constructed cases decided against cited declared-semantics facts. Location B, a design act; Invariants VI, I (with DEC-3300f3) and IV.

## Status and authority

- **Proposed.** It moves to decided only on the operator's recorded grant at the bc-exchange desk. The operator's approval of the plan reached the authors through the Chief Controller on 2026-10-03 and is not authority by itself.
- **Amends** DEC-05815d's calibration-corpus methodology, which DEC-d3b916 clause 2 names as the methodology authority. **Stands alongside** DEC-b5978c (the fitness standard), unchanged.
- **Retires** the constructed calibration positive set up by the Codex exchange rulings 4e10ff18 and 2aa6cfe7 (M2, narrowed 2026-08-01). Those were exchange rulings, not ADRs, so no ADR status changes.
- **Authors:** Metric Controller (corpus composition) and Architect (Foundation). Task TSK-fa0e4b; decision page barecount-devhub PR 242.

## Context

- The constructed "sound" control was refuted under prompt v11 in 4 of 5 attempts. Architect and Metric ruled the refutation **defensible**, with the Chief concurring (TSK-9ce7f9; ruling at barecount-devhub PR 240, f04e44f8).
  - The control's definition promises aggregation "by value date". Its contract can declare only a fiscal-period gate, which the platform resolves from the posting date (DEC-ea4523, DEC-83fda0).
  - Every planted negative inherited that defect, so the corpus had no clean ground truth.
  - The same wording is a generated template present in real directory members (TSK-41ee58).
- **History reconstruction.** The panel was never grounded in data, and its last "stable" calibration (2026-08-02) partly rested on missing this defect.
- **The operator's principle.** A metric and its deterministic LC5 answer are the agreed ground truth. The panel judges how BareCount expressed it.

## Decision: corpus composition (Metric Controller)

The U5 calibration corpus is composed as a HYBRID:
- the positive is one REAL, certified, LC5-validated metric;
- value-moving defect classes are planted as LC5-proven negatives;
- meaning-only defect classes are retained as constructed or semantic negatives.

The prior constructed "sound positive" (`positive-constructed-control`) is RETIRED in favour of the validated real positive.

1. **The positive is a real validated metric.**
   - The positive case is receivable_days_sales_outstanding MCV d0f73360: active and certified, Legal-Entity grain, not_applicable currency, posting basis.
   - Its governed Kaveri values (48.77/37.03/38.24/41.24/35.98 days, TSK-3ceb0e) match an independent outside-platform LC5 recompute to the cent (mode-b-dso-recompute.sql).
   - A real validated metric answers "can the panel pass a genuinely sound package" without the r22 problem (the pool could not supply a sound constructed shape), because soundness is anchored to an external oracle, not to the fixture author's enumeration of the grammar.
   - **PRECONDITION (hard):** the oracle must be COMMITTED ON MAIN before it labels anything. The DSO recompute is on a branch today (aef885c0). It must land on main as the committed oracle-of-record before the corpus uses DSO as the labelled positive.

2. **Value-moving defects are LC5-proven negatives.**
   - A class is admitted as an LC5-proven negative only if its single-dimension mutation empirically changes the value against the committed oracle, or makes it non-computable.
   - The admitted classes: wrong_grain, missing_or_unsupported_filter, temporal_boundary_error (a real window or shape mutation, e.g. a fixed-day literal vs calendar days), formula_definition_mismatch, misbound_input, dependency_role_closure_omission, and currency (mixing variant).
   - Each carries its oracle evidence: the diverging recompute. Appendix A is the worked mapping.

3. **Meaning-only defects are retained as semantic negatives.** A class whose single-dimension mutation produces NO value divergence cannot be reduced to an oracle, so it stays a constructed or semantic negative:
   - **currency_semantics_contradiction:** same number, wrong declared currency meaning;
   - **definition_ambiguity:** same computation, under-specified definition;
   - **definition_contract_fidelity:** the "by value date" class, where the definition names a basis the contract cannot back and the computed value is unchanged, because the platform bins by posting date regardless.

   The panel decides these against a CITED declared-semantics fact: the move-1 `declared_semantics` exhibit (PR 242: "rows are assigned to fiscal periods by the posting date; no other date basis exists"). D2 (the moderator's cite-to-pass) enforces exactly that.

4. **Why both halves are required.** An oracle proves VALUE fidelity, not MEANING fidelity. The evidence: the definition_contract_fidelity defect adjudicated DEFENSIBLE on TSK-9ce7f9 produces no value divergence. An oracle recompute also uses the posting date, so it gets an identical number, and a pure value-divergence corpus would wrongly VALIDATE that defect. The semantic corpus is therefore irreducible.

## Foundation (Architect)

- **Repair location: B, the calibration contract's definition of a right answer.** This is a design act (DEC-c48b0f item 5). The previous corpus had no declared ground truth: "sound" meant "the fixture author believes it is sound". This decision declares the ground truth (a committed oracle for value, a cited declared-semantics fact for meaning). Tuning prompts or fixture prose instead (location D) would be compensation.
- **Invariant VI (evidence is emitted, not inferred).** Every label is emitted evidence:
  - a value label is a committed oracle artifact, path@commit and sha, together with the governed evaluation it matched;
  - a meaning label is a cited declared-semantics statement whose authority is a decided ADR.

  No label rests on authored belief.
- **Invariant I (meaning is evaluated once), with DEC-3300f3 (customer data stays in the deterministic runtime).**
  - The oracle runs outside the platform and only **labels** calibration cases. It never produces a platform value.
  - The governed evaluator remains the single producer of metric values.
  - The AI panel receives packages and declared semantics, never data.
- **Invariant IV (references are explicit), and DEC-c48b0f item 2.** A meaning-only defect is a definition that names something the contract does not declare: an implicit reference. Only a declared-semantics fact can expose it, and a value oracle cannot see it. This is why the semantic half is irreducible.
- **Source-agnostic certification is unchanged.** Calibration measures the *panel*, not the source. Using the LC5 world to label calibration cases does not make certification "works on Odoo". The certification panel still judges a definition against its declared contract.

## Consequences

1. The oracle-of-record for DSO lands on main (precondition 1).
2. The calibration fixture is rebuilt.
   - The positive is the DSO package exported through the governed export path (`audit-panel-export.service`), frozen with its sha.
   - The value negatives are its single mutations, each with oracle evidence.
   - The meaning negatives stay constructed, built on a clean base; none inherits a defect.
   - The fixture header cites this ADR and retires `CALIBRATION_POSITIVE_PROVENANCE` (the constructed control).
3. Under DEC-b5978c, a new corpus is a new calibration set (D7). The verdict machinery is unchanged: `expected_cases` is still derived from `calibrationCorpus()`. D5 still moves classes to deterministic rules as those rules land.
4. Order, as the operator approved: move 4 (the A/B) and move 1 (exhibits, prompt v12), then this corpus and a new five-attempt set, then D2. The validation step (move 3, DRIVE-2OCT §13a.1) proceeds in parallel.

## Appendix A

DSO mutation→divergence table: barecount-devhub `artifacts/metric-audit/calibration-reframe/DSO-MUTATION-DIVERGENCE-TABLE-2026-10-03.md` @ d842f14e (sha256 a1d6cc44).
