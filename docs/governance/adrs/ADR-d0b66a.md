---
uid: DEC-d0b66a
title: "The point_in_time metric shape has no gate-level date basis; its period scope is the grain grouping and anchor_role is a row-read variable"
description: "The point_in_time metric shape has no gate-level date basis; its period scope is the grain grouping and anchor_role is a row-read variable"
status: decided
date: 2026-10-05T16:59:59.420Z
project: platform
domain: platform
subdomain: metric-shape-semantics
focus: point_in_time date basis and anchor_role; entry-gate G2/G4 consequence
---

# The point_in_time metric shape has no gate-level date basis; its period scope is the grain grouping and anchor_role is a row-read variable

## Context

See decision text below.

# The point_in_time metric shape has no gate-level date basis; its period scope is the grain grouping and anchor_role is a row-read variable

**Status:** decided. Authority: operator grant `2026-10-05T16-56-07-211Z-419b2e41` (text_sha256 `419b2e41594d401488500165ce4adcec4bc9af485362dae23c055bb5a70b2bf4`; bc-exchange desk #212) — decides the point_in_time semantics as written, and authorizes recording decided + the auditor conducting bounded reviews through acceptance at the then-current head + merge on a green exact head. Author: Architect SES-b9b0ef. Grounded at bc-core `origin/main` cc08875b; formalizes the 0036 design §4 ruling (Platform-concurred, bc-core `4bae7f7`).

## Context

The entry-gate / clean-directory work (DEC-ca8943, DEC-b36e15) left the point_in_time shape's date semantics undeclared: `select-by-gate.ts` notes that a per-shape predicate "is declared in a follow-up" (none existed), so point_in_time resolved to identity with no declared date basis. 18 directory members use point_in_time and were classed NOVEL pending this ruling.

## Decision

1. **point_in_time has NO gate-level date basis.** Its period scope is the GRAIN GROUPING. bc-core `select-by-gate.ts:27-30,497-499` resolve point_in_time (and instantaneous) to IDENTITY — "no row-filtering selection; the grain grouping scopes the period" — and the "per-shape predicate pending declaration" the code flags is hereby declared INTENTIONALLY NONE for point_in_time. So G2 has nothing to refuse for a point_in_time member; any "as of period end" PROSE is a panel advisory only.
2. **anchor_role names a ROW-READ variable**, the row-level `temporal_anchor` (the as-of reporting date stamped per row; `metric-directory.service.ts:292-302`), NOT a date selector. G4 therefore requires its `temporal_anchor` and `measure` concepts to be ordinary contract fields (row-read inputs), with no exemption — the same as any base member.
3. **A metric that needs "the state AT a reporting point P"** (a row predicate selecting the as-of row) is an `as_of` or `cumulative_to_date` metric — a RE-SHAPE, its own design act; it is NOT a point_in_time predicate, and point_in_time is not given one here.
4. **Consequence.** Of the ~18 point_in_time directory members, those that are genuinely point_in_time (identity-scoped; their concepts bind as row-read inputs) are entry-ready / CLEAN on this declaration; any that actually need "state at P" are flagged for re-shape to `as_of` (folding into the clearing_date / as_of ADR). Metric applies the rule per-member.
5. **Foundation.** This records existing behaviour (identity selection + the row-level `temporal_anchor`); repair location B (contract semantics — it declares the point_in_time meaning that was missing, the design act DEC-c48b0f item 4 requires, not a detector). No lower-layer compensation. Invariants preserved: I (meaning evaluated once), II (fixed scope = grain grouping), III/IV/V/VI unaffected.

## References

bc-core `select-by-gate.ts:27-30,497-499` (identity; grain-grouping scope), `metric-directory.service.ts:292-302` (row-level `temporal_anchor`; `anchor_role`); the 0036 design §4 (Platform-concurred at bc-core `4bae7f7`); DEC-ca8943 (entry gate), DEC-b36e15 (pool-readiness); `foundation/the-invariants.md`; `foundation/the-evaluation-boundaries.md`.
