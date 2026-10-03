---
id: ADR-ERR-008
title: "DEC-4c8bee states that no date basis other than the posting date exists; DEC-26f75a's optional period_aggregate anchor_field is one"
status: open
authority: authoritative
affected: DEC-4c8bee (D649) — Decision point 3, the meaning-label table row "definition_contract_fidelity (the date basis)"
resolution: correction recorded here; the hybrid-corpus decision stands; the date-basis label rests on the two-branch rule below
opened: 2026-10-03
---

# ADR-ERR-008 — DEC-4c8bee: the date basis is the posting date by default, or the gate's declared anchor_field

## Contradiction summary

DEC-4c8bee point 3 labels the date-basis meaning class with: "rows are assigned to fiscal periods by the posting date declared by the canonical contract; no other date basis exists" (citing DEC-ea4523 and DEC-83fda0). The last clause is false. DEC-26f75a (implemented) gives the `period_aggregate` gate an **optional** `anchor_field`: a date field of the grain canonical contract whose value must fall within the evaluation period for a row to be a member. Only when no `anchor_field` is declared is membership the stamped posting fiscal period.

## Implementation behavior

- The engine honours a declared `anchor_field` for `period_aggregate`: `metric-evaluation-orchestrator.service.ts:260-299` and `co-candidate-reader.ts:170, 274`, at bc-core `origin/main`.
- With no `anchor_field`, the canonical resolver stamps fiscal fields from the grain contract's declared `posting_date_field` (`ccv2-canonical-resolver.service.ts:971, 1733-1757`).
- Live, on 2026-10-03, no `period_aggregate` metric contract declares `anchor_field`; only `as_of` gates do.
- The panel package projection for `period_aggregate` keeps only `period_type` and drops `anchor_field` (`package-signature.service.ts:88-91`). That is a separate defect, routed to Platform.

## Resolution

The date-basis meaning label in DEC-4c8bee point 3 reads, in place of the false clause:

> A row's period membership is **(a)** the period of the gate's declared `anchor_field` (DEC-26f75a), when the gate declares one; otherwise **(b)** the fiscal period stamped from the posting-date field declared by the grain canonical contract (DEC-ea4523, DEC-83fda0). A definition that names a date basis is faithful only if the named basis is (a), or is (b) when no anchor is declared.

The hybrid-corpus decision stands. The TSK-9ce7f9 verdict also stands, for that package: its gate declared no `anchor_field`, so "by value date" named a basis the contract did not declare. Its stated reason ("the grammar cannot declare an anchor") is corrected by this entry.

## Resolution state

Open until the move-1 `declared_semantics` statement and the clean-directory G2 rule carry the two-branch rule, and the package projection carries `anchor_field`. Recorded by the Architect, SES-180ad4, 2026-10-03.
