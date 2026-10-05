---
id: ADR-ERR-010
title: "DEC-b5978c D5 keeps 'filter semantics' in the panel; the filter class splits, and its structural (unsupported) sub-mode is a deterministic leaver"
status: open
authority: authoritative
affected: DEC-b5978c (D648) — Decision D5, the "rules before judgement" deterministic-leaver set and the "panel keeps ... filter semantics" clause
resolution: correction recorded here; the D5 decision and its "keeps filter semantics" clause stand; "filter semantics" denotes the semantic sub-mode only, and the filter class's structural sub-mode is a deterministic leaver
opened: 2026-10-05
---

# ADR-ERR-010 — DEC-b5978c D5: the filter class splits; its structural sub-mode is a deterministic leaver

## Contradiction summary

DEC-b5978c D5 ("Rules before judgement") lists the defect classes that leave the panel corpus as deterministic checks land — "wrong grain, then temporal boundary, then closure omission and misbound input" — and then says "The panel keeps definition↔formula fidelity, ambiguity and filter semantics." Read against the corpus, the single class `missing_or_unsupported_filter` (DEC-4c8bee point 2) has **two** distinct failure modes, only one of which is the "filter semantics" D5 keeps:

- **Structural (unsupported):** a filter whose bound concept or field is **not declared in the grain canonical contract's resolved schema**. This is decidable from declarations alone — it is a bindability defect, not a judgement.
- **Semantic (wrong population):** a filter that is well-formed and supported, but expresses the **wrong population** for the metric's intended meaning. This is a meaning judgement that no deterministic rule can settle.

D5 names neither sub-mode explicitly for the filter class: it lists the structural classes (grain/temporal/closure/misbound) as leavers and keeps "filter semantics." It does not state where the filter class's **structural** sub-mode belongs. Left unsplit, the class appears both as a panel-kept class (via "filter semantics") and as a value-moving class whose structural half is mechanically decidable — the gap this entry closes.

## Implementation behavior

Read at bc-core `origin/main` and the DEC-ca8943 entry-gate design:

- The structural sub-mode is already the entry gate's deterministic check: DEC-ca8943 G4 refuses a discriminator (filter) concept that is **not** declared in the grain canonical contract's resolved schema (clean-directory design `DESIGN-entry-gate-evaluator-and-0036.md` §4, G4). Its live runtime/PE-MC counterpart is TSK-93f0d0.
- The semantic sub-mode is not deterministically decidable from declarations: whether a supported filter yields the intended population is exactly a panel meaning judgement (DEC-c48b0f item 4 leaves meaning to the panel; the mechanical part becomes a rule).

## Resolution

DEC-b5978c D5's decision and its "the panel keeps ... filter semantics" clause **stand**. This entry records how the filter class maps onto them:

1. **The filter class splits into a structural and a semantic sub-mode** (definitions above).
2. **The structural (unsupported) sub-mode is a deterministic leaver.** When its deterministic check lands (DEC-ca8943 G4 / TSK-93f0d0), it joins the substrate-proven classes and leaves the panel corpus, under the **same** "rules before judgement" rule D5 applies to wrong grain, temporal boundary, closure omission and misbound input. D5's ordered leaver list is read to admit this sub-mode as it lands, not to exclude it.
3. **The semantic (wrong-population) sub-mode is the "filter semantics" D5 keeps.** It stays in the reduced panel corpus. So the filter class does **not** leave the panel wholesale (unlike wrong grain): the corpus retains a **semantic** filter negative so that filter-semantics fitness stays measured.
4. **"Filter semantics" in D5 denotes the semantic sub-mode only** — not the structural sub-mode, which was never a judgement.

This changes no decision: the deterministic-vs-judgement division is DEC-c48b0f item 4, which D5 already invokes; this entry applies it to the two halves of one class whose name conflated them.

## Resolution state

Open until the deterministic structural-filter check lands (DEC-ca8943 G4 in migration 0036, and its live counterpart TSK-93f0d0) and the calibration corpus re-pins to carry a **semantic** filter negative (the wrong-population case) while the structural sub-mode is dropped to the substrate — the same migrate-then-re-pin pattern as wrong grain. Recorded by the Architect, SES-b9b0ef, 2026-10-05.
