---
uid: DEC-d0b66a
title: "point_in_time has no gate-level date basis and no runtime period selection; its temporal predicate is pending declaration, anchor_role is a row-read variable, and aggregating members carry a wrong-data risk until re-shaped or the predicate is built"
description: "point_in_time resolves to identity with no period/snapshot selection; the directory generator over-claims an as-of runtime semantic the evaluator does not implement, so point_in_time members are not auto-clean"
status: decided
date: 2026-10-05T16:59:59.420Z
project: platform
domain: platform
subdomain: metric-shape-semantics
focus: point_in_time date basis, runtime selection gap, anchor_role, and the entry-gate G2/G4 + directory-clean consequence
---

# point_in_time: no gate-level date basis, no runtime period selection, predicate pending declaration

**Status:** decided. Authority: operator grant `2026-10-05T16-56-07-211Z-419b2e41` (text_sha256 `419b2e41594d401488500165ce4adcec4bc9af485362dae23c055bb5a70b2bf4`; bc-exchange desk #212) — decides the point_in_time semantics and authorizes recording decided + the auditor conducting bounded reviews through acceptance at the then-current head + merge on a green exact head. Author: Architect SES-b9b0ef. Grounded at bc-core `origin/main` cc08875b. Round-1 auditor review (gen-57f13d-01) corrected an earlier draft that wrongly claimed grain grouping scopes the period and that genuine members are clean; this version records the accurate runtime boundary.

## Context

The entry-gate / clean-directory work (DEC-ca8943, DEC-b36e15) left the point_in_time shape's runtime date semantics undeclared. `select-by-gate.ts` flags its per-shape predicate as "pending declaration" and resolves point_in_time to identity; 18 directory members use point_in_time and were classed NOVEL pending this ruling. Grounding the runtime path (not only the gate module) shows the predicate is not merely undeclared — it is declared-but-unbuilt, and the directory generator asserts a runtime semantic the evaluator does not deliver.

## Decision

1. **point_in_time resolves to IDENTITY — no gate date predicate AND no runtime period/snapshot selection.** At cc08875b, `select-by-gate.ts:26-27` resolves the degenerate point shapes (`point_in_time`, `instantaneous`) to IDENTITY, and `:142-144` records the result as "identity selection (every candidate retained) for a shape whose per-shape predicate is **pending declaration**; the resolved set equals the candidate set." Only `period_aggregate` is period-scoped, and that scope is applied **by the caller**, not the gate: `metric-evaluation-orchestrator.service.ts:41-42` (`PERIOD_AGGREGATE_SHAPE` — "its candidates MUST be period-scoped by the caller") and `co-candidate-reader.ts:130-138` (`scopeCandidatesToPeriod` filters **only** `period_aggregate`; `as_of` passes `scope=false`). The grain grouping decides **which grain's** candidates enumerate; it is **not** a period scope. There is therefore no gate-level date basis for G2 to refuse — but neither is there any runtime period selection for point_in_time.

2. **The predicate is PENDING DECLARATION, not intentionally none.** `co-candidate-reader.ts:20-26` states the scope holds "**Until ADR #2 adds the per-input period predicate**." point_in_time's temporal selection is a design+implementation act still owed, not a solved identity reshaper.

3. **anchor_role names a ROW-READ variable** — the row-level `temporal_anchor` (the as-of reporting date stamped per row; `metric-directory.service.ts:289-302`, C-FX-8 "since no time_anchor binding, we stamp it on the rows"), NOT a date selector. G4 requires its `temporal_anchor` and `measure` concepts to be ordinary contract fields (row-read inputs), with no exemption.

4. **Declared-but-unbuilt runtime semantic (the wrong-data risk).** The directory generator `buildGateArtifacts` (`metric-directory.service.ts:289-305`) generates point_in_time members as "an as-of snapshot of a stock ... NOT re-summed/re-counted across periods" and asserts "the point_in_time GATE SHAPE alone carries the as-of semantics at runtime." The evaluator does not implement that selection (Decision 1). So where a point_in_time member's candidate set spans multiple reporting dates and its formula aggregates (SUM binds measure + temporal_anchor and Σ's the measure; COUNT row-counts), the evaluator **re-sums across periods** — exactly what the generator forbids — and yields a wrong scalar. The generator's runtime claim is inaccurate at cc08875b.

5. **Directory consequence — point_in_time members are NOT auto-clean.** A point_in_time member is entry-ready only when the unscoped candidate set **equals** its intended snapshot — a current-state read whose grain yields a single reporting-date candidate set, so identity selection already is the intended value. Any member whose candidate set spans multiple reporting dates and whose formula aggregates is **HELD (not clean)**: it is re-shaped to `as_of`/`cumulative_to_date` (which perform real row selection — `select-by-gate.ts:186-214`), or it awaits the per-input period predicate (the ADR #2 implementation act). Metric classifies per-member on candidate-date-span + formula; the directory must NOT clean members on "point_in_time = identity."

6. **A metric that needs "the state AT a reporting point P"** (a row predicate selecting the as-of row) is an `as_of` or `cumulative_to_date` metric — a RE-SHAPE and its own design act. point_in_time is not given such a predicate here.

7. **Foundation.** This ADR records an upper-layer semantic predicate that is declared (the gate shape promises as-of semantics) but unbuilt (the evaluator does not select). Cleaning members on the basis that "identity selection is correct" would be lower-layer compensation for that gap — forbidden (DEC-c48b0f; the-invariants.md). The faithful repair is at the declaration/evaluation layer (repair location B/D): either build the per-input period predicate (ADR #2) or re-shape the member to `as_of`. This ADR states the boundary accurately and defers the predicate; it does not build it, and it does not pretend the gap is closed (Invariant I — meaning is evaluated once, not asserted by a gate shape the evaluator ignores).

## References

bc-core cc08875b: `select-by-gate.ts:26-27,142-144,186-214`; `co-candidate-reader.ts:20-26,130-138`; `metric-evaluation-orchestrator.service.ts:41-42`; `metric-directory.service.ts:289-305`. The 0036 design §4 (Platform-concurred at bc-core `4bae7f7`); DEC-ca8943 (entry gate), DEC-b36e15 (pool-readiness); `foundation/the-invariants.md`; `foundation/the-evaluation-boundaries.md`. Follow-up: the per-input period predicate ("ADR #2") and the point_in_time runtime-gap risk.
