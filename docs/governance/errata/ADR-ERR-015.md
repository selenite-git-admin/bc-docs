---
id: ADR-ERR-015
title: "DEC-ffee4e point 3 names the wrong verdict word: the registry panel's rejection value is REJECT; REJECT_DEFECT is the metric panel's word"
status: adopted
authority: authoritative
affected: "docs/governance/adrs/ADR-ffee4e.md (DEC-ffee4e) — Locked point 3, \"Panel semantics unchanged\", the clause \"verdict enum APPROVE_FOR_DRAFT | OPERATOR_REVIEW | REJECT_DEFECT\""
resolution: "correction recorded here; DEC-ffee4e's decision (the panel is ported byte-compatible) is unchanged. The registry authoring panel's verdict values are APPROVE_FOR_DRAFT, OPERATOR_REVIEW and REJECT. REJECT_DEFECT is the word of the metric authoring panel (DEC-09f86b), not of the registry panel."
opened: 2026-11-19
---

# ADR-ERR-015 — DEC-ffee4e point 3: the registry panel's rejection value is REJECT

Found by the design check of AI's Modify step (platform refactor program, phase 4). The decision of DEC-ffee4e is unchanged. One sentence names the wrong word.

## Contradiction summary

DEC-ffee4e, Locked point 3, says:

> "Panel semantics unchanged: A1 grounding checks (...), verdict enum APPROVE_FOR_DRAFT | OPERATOR_REVIEW | REJECT_DEFECT, and the NF1 panel_output_record shape are ported byte-compatible."

The enum in that sentence is the metric authoring panel's. The registry authoring panel, the one DEC-ffee4e ports, writes `REJECT` as its rejection value, and wrote `REJECT` before the port too. So the sentence misdescribes what was ported. The decision to port the panel byte-compatible is not in question.

## Implementation behavior

- bc-core `origin/main` (commit `0001515e`), file `src/registry/bcf/panel/in-process/registry-authoring-verdict.logic.ts`: the constants are `VERDICT_APPROVE = 'APPROVE_FOR_DRAFT'`, `VERDICT_REJECT = 'REJECT'` and `VERDICT_OPERATOR_REVIEW = 'OPERATOR_REVIEW'`. A rejection with a defect code outside the closed list becomes `OPERATOR_REVIEW`.
- `REJECT_DEFECT` is the word of the metric authoring panel: its seats and its consensus (DEC-09f86b; DEC-32a56e uses the same word). Neither of those two ADRs needs a change.
- Ruling B39 of the Platform Refactor Program (`docs/development/platform-refactor-program/rulings.md`; operator's desk grant `2026-11-19T09-33-25-342Z-e02128a0`) makes `REJECT` the one rejection value of the verdict field of `bcf.panel_output_record`. The metric panel keeps `REJECT_DEFECT` for its seats and consensus. Only the record row it writes will store `REJECT`, with the defect code at the top level of the payload.
- Stored rows, as read live by the Chief on 2026-11-19: 12 registry rows hold `REJECT`, and every one has a defect code. 4 metric rows hold `REJECT_DEFECT`. These counts are as of that date.

## Resolution

Read Locked point 3 of DEC-ffee4e as follows. The registry authoring panel's verdict values are `APPROVE_FOR_DRAFT`, `OPERATOR_REVIEW` and `REJECT`. `REJECT_DEFECT` is not one of them. The words "ported byte-compatible" stand, and they now describe the registry panel as it is. The text of DEC-ffee4e is not rewritten.

## Resolution state

`adopted`. The code is the correct behavior and was never different. This correction only makes the ADR text match it.

## References

- `docs/governance/adrs/ADR-ffee4e.md` (DEC-ffee4e), Locked point 3
- DEC-09f86b (the metric panel's `REJECT_DEFECT`), DEC-32a56e
- Ruling B39, `docs/development/platform-refactor-program/rulings.md`
- DEC-149ab2 Amendment 1 (the same change set: the wider defect-code list)
- Errata schema: `docs/governance/errata/README.md` (ADR-ERR family)
