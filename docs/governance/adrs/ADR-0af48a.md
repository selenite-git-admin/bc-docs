---
uid: DEC-0af48a
title: "The exactness invariant governs all amount-producing operations — extend DEC-c4619b scope to the resolution layer"
description: "Extends the scaled-decimal-int-v1 exactness profile (DEC-c4619b) from the evaluation engine to every amount-producing operation — resolution-layer reducers now, source-admission numeric parse later — through the one existing ScaledDecimal module under one prover boundary; no second engine."
status: proposed
date: 2026-11-01T10:09:33.260Z
project: platform
domain: metrics
subdomain: metrics/numeric-execution
focus: exactness-invariant-jurisdiction
---

# The exactness invariant governs all amount-producing operations — extend DEC-c4619b scope to the resolution layer

## Context

GROUNDING (bc-core origin/main @ 259ae6c4; ruling artifact RULING-resolveSum-binary64-vs-scaled-decimal-R2-2026-11-01.md @9c0d1a54):

1. The rule-system ALREADY EXISTS as one engine, one grammar, one obedience gate (the legacy `runNumericAggregate` compute path named in DEC-c4619b's annex has ZERO hits on origin/main — consolidation already happened; this ADR protects it, it does not create it). So the answer to the operator's general-form question ("shall we create a global metrics formula rule engine every formula obeys?") is NOT "build an engine" — that duplicates `FormulaExecutionEngine` + the exactness prover + `scaled-decimal.ts` and re-creates the very second compute path the consolidation removed (the rework trap) — but "extend the ONE existing rule's JURISDICTION."

2. `resolveSum` is a real binary64 amount-producing reduction OUTSIDE the DEC-c4619b declared scope: `const v = Number(raw); sum += v`, accumulator a JS literal `0`. Its output is AUTHORITATIVE — written once onto the primary/CO row by `copyMergedColumns` (:1571) and read by the evaluation engine as an already-collapsed single column; the engine never sees the addends and cannot re-prove the aggregation. Storage gives no rounding net: `ddl-generator.service.ts:106-107` types contract decimal/number -> Postgres bare `numeric` (no scale), so a binary64 tail persists verbatim (the exact drift DEC-c4619b documents). The downstream profile is fail-closed, not silent (`parseDecimalString` refuses nonzero digits beyond scale) — so a drift tail yields a hard eval stop or a non-EXACT label, never a silent cent miss.

3. It is a DOCUMENTED BOUNDARY, not a missed sweep: DEC-c4619b deliberately scoped to the evaluation engine ("storage schemas untouched"); the resolver `Number()` is in the resolution path that Decision left untouched. This is why it is the operator's doctrine call, not a mechanical bug fix: it asks whether "amounts never touch binary64" should hold at EVERY amount-producing boundary or only inside the evaluation engine as written.

4. Exactness bound worked for LC5 AR (DEC-545a4d prong a): a sum over n inputs scaled_decimal(scale=s,|x|<=B) is EXACT iff n*B*10^s < 2^53, provided each input is parsed to a scaled integer first. Policy `NUMERIC_DOMAIN_POLICY_V1` for (amount,decimal) = scale 2, |x| <= 10^8; B*10^s = 10^10; with a generous n = 10^5 lines/key, n*B*10^s = 10^15 < 2^53 (~9x margin). So `sumSameScale` over scale-2 BigInt cents is provably EXACT for LC5 AR — the gap is the REPRESENTATION (`Number()`+`+=` on decimal binary64), never the magnitude.

5. U4 (R2 AR) vs R4-scale: for AR Balance the `ci_doc_residual` sum collapses `asset_receivable` lines per (move_name, company_id). Single-contributor groups (one receivable line per invoice, the normal case) are provably exact -> match the LC5 oracle to the cent; drift needs >=2 contributing lines (multi-installment terms). So U4 is NOT a blocker, conditional on the multi-line-group count (the one open datum, read against `tbc_kaveri_dev`, folded into the U4 pre-emit gate), with fail-closed as the net. R4-scale is the real exposure: across the corpus multi-line sum groups are routine, so an unprofiled binary64 reduce becomes a broad recurring fail-closed blocker AND a standing dent in the DEC-346ae7 claim-3 mechanism story.

FOUNDATION (DEC-79b62f): this is a DESIGN/DECLARATION act (DEC-c48b0f), not a detector — the fix is declaring the invariant's jurisdiction; a detector at `resolveSum` would be the net, not the fix. Repair location B (the rule's scope/semantics), realized at D (resolution reducers) and later A (source-admission parse). Invariant at stake: VI (evidence emitted, not inferred) + the DEC-346ae7 claim-3 mechanism guarantee — an amount the mechanism PRODUCES must be produced under the exactness discipline the mechanism CLAIMS. No lower-layer compensation (DB hand-edit, NULL-store rounding) is acceptable; the fix belongs at the reduce itself.

RELATIONSHIP (amends, not supersedes — Architect call): DEC-c4619b is decided AND implemented; its mechanism is correct and in production. Superseding it would re-open a live, working ADR and (per hygiene rule 1) flip it to superseded, falsely signalling its mechanism is retired. The correct relationship is an amendment that widens only its declared scope. Therefore no `supersedes_ref` is set and DEC-c4619b stays decided.

## Decision

The deterministic numeric-execution invariant `scaled-decimal-int-v1` (declared by DEC-c4619b) SHALL govern EVERY amount-producing operation in the platform — formula kernels AND the canonical resolution layer's amount-producing reducers — through the ONE existing `scaled-decimal.ts` module under the ONE existing prover boundary. This EXTENDS (amends), it does NOT supersede, DEC-c4619b: that ADR remains decided+implemented and its mechanism (BigInt scale-pinned arithmetic, EXACT|REPRODUCIBLE|NOT_PROVEN verdict grammar, C9 admit gate) is unchanged and correct. Only its DECLARED SCOPE is widened.

SCOPE TODAY (DEC-c4619b): "the M10 fixture verifier (formula-execution engine -> v3) and the production metric evaluation engine; storage schemas untouched." The invariant's reach is thereby confined to operations INSIDE the formula AST. The canonical resolution layer produces canonical AMOUNTS before evaluation and is outside that reach by construction.

SCOPE AFTER THIS ADR: + the canonical resolution layer's amount-producing reducers. The governed class is named explicitly (not a single site): in `bc-core/src/boundary/ccv2-canonical-resolver.service.ts` — `resolveSum` (~:1657), `latestByValue`/`resolveLatestBy` (~:1693), the D514 n-ary row-local sum (~:2348), and `sumDeclaredColumns` (~:2391). A SECOND amount-producing class — source-admission numeric parse in the reader executors (`parseFloat` at `ecb-sdmx.executor.ts:162`, `fred-api.executor.ts:139`; repair location A) — is NAMED here and STAGED LATER, not folded into the first pass. (The `Number(...)` sites in `resolved-admission-context.ts` are row-count/cardinality guards, NOT amounts, and are out of scope.)

REALIZATION PRINCIPLE (no rework, no second engine): route the named reducers through the SAME `scaled-decimal.ts` module the engine already uses — replace `Number()`/`+=` with `parseDecimalString` (EXACT entry; the resolver holds the raw SQL numeric string, never a JS number) + `sumSameScale`, scale taken from the eval engine's `numeric-domain-policy`. Scale is already SELECTed at `resolvePinnedOcLeg:829` and discarded, so it is recoverable with no new query. Extend the prover/obedience gate to ASSERT the resolution reducers are profile-pinned, so rule-obedience is checked over both layers under one boundary. No new module, no new grammar, no new engine; `FormulaExecutionEngineV3` remains the single exact-profile subclass of the single `FormulaExecutionEngine`.

STAGING (one stage per PR, Platform lane, resolveSum first): Stage 1 = `resolveSum` routed through `scaled-decimal.ts` + prover extended to check obedience there; real-DB tests; carry the LC5-AR bound + the multi-line-group count as the U4 gate datum. Stage 2 = the three sibling reducers (`latestByValue`, the n-ary sum, `sumDeclaredColumns`). Stage 3 = the source-admission `parseFloat` class (FX/macro). Each stage is a named, labeled instance under this one declaration.

STATUS = proposed. The decided-status flip and every merge remain operator-gated. Until this ADR is decided and Stage 1 lands, the resolver reduce is recorded as an explicitly labeled EXEMPTION to the DEC-c4619b profile (so it is never mistaken for proven-exact), guarded by the R2 U4 pre-emit gate (the multi-line-group count read against `tbc_kaveri_dev`). The exemption does NOT extend to R4-scale.
