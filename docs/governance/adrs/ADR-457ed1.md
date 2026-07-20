---
uid: DEC-457ed1
title: "Prong (b) licensed rounding operations: any single correctly-rounded arithmetic operation"
description: "Amends DEC-545a4d prong (b): the licensed rounding set becomes divide, avg, multiply, plus, minus (one correctly-rounded op per node) over EXACT/REPRODUCIBLE operands; unblocks the 48 percentage-idiom members."
status: proposed
date: 2026-07-20T06:22:03.893Z
project: bc-core
domain: metrics
subdomain: metric-runtime
focus: numeric-admission
---

# Prong (b) licensed rounding operations: any single correctly-rounded arithmetic operation

## Context

MEASURED PROBLEM. Unit B2 implemented the stated grammar literally and ran a read-only analysis over the 86 still-blocked directory members (package prongb-b2-reproducible-package-v2-2026-07-20.md, sha c935a6cf...; transcript 91545dc9..., independently reproduced by the auditor). Result, bucketed on structured refusal codes: 30 REPRODUCIBLE, 48 refused with `unlicensed_rounding_node`, 5 with `divide_operand_not_proven`, 3 with `avg_operand_not_exact`. Every one of the 48 is the percentage idiom multiply(divide(a,b), 100) or multiply(avg(...), 100): a ratio scaled to a percentage. They are blocked solely because `multiply` is not on the licensed list — not by any soundness concern.

WHY THE WIDENING IS SOUND. IEEE-754 multiplication, addition, and subtraction are correctly rounded: the standard requires the nearest representable result, so every conforming platform yields the identical bit pattern. Chaining them preserves the only property REPRODUCIBLE claims — bit-identical replay. Refusing them protects nothing; it merely privileges two operations over three others that carry exactly the same determinism guarantee. The original parenthetical is better read as naming the operations the authors had in view than as a considered exclusion of the rest.

ALTERNATIVES CONSIDERED.
(a) Narrow amendment licensing `multiply` by an exactly-representable literal only. Covers the same 48 with a smaller surface, but special-cases an idiom and would need widening again at the first metric that divides by a constant or sums two ratios.
(b) Reshape the 48 metrics to divide(multiply(a,100), b), scaling inside the exact layer so only one rounding occurs. This needs no grammar change and is measurably MORE ACCURATE: a 40,000-case sweep found the two forms differ in the last unit in the last place for 26.31% of cases (e.g. (100/30000)*100 = 0.33333333333333337 versus (100*100)/30000 = 0.3333333333333333). It was rejected on cost, not correctness — it rewrites 48 formula ASTs, and a formula change is a metric-identity change requiring 48 governed contract versions and supersessions to buy one ulp, far below any financial materiality threshold. The accuracy advantage is recorded here so the trade-off is on the record rather than discovered later.
(c) Decline and leave the 48 permanently NOT_PROVEN. Rejected: it strands a third of the remaining directory population over a specification ambiguity rather than a numeric risk.

FOUNDATION INVARIANT TEST. Repair location B (contract semantics — the admission grammar), which is where a grammar question belongs; no compensation at C-F. I (meaning evaluated once): the amendment changes what the prover may certify, not what any metric means. III (immutability): no frozen snapshot or existing evidence row is altered; reclassification is additive re-proof evidence exactly as prong (a) established. V (non-replayable evaluation): admission continues to read recorded evidence; nothing re-evaluates on read. VI (evidence emitted): the operation trace is emitted by a real prover run and now publishes the rounding count, strengthening rather than weakening the emitted evidence.

EXPECTED EFFECT, NOT YET CLAIMED. Implementation is expected to reclassify the 48 members whose sole refusal code is `unlicensed_rounding_node`, taking prong (b) coverage from 30 to 78 of 86. This is a prediction to be PROVEN by re-running the B2 analysis under the amended grammar in a successor unit; it is not asserted as fact here. The remaining 8 (5 unprovable operands, 3 avg over non-exact operands) are unaffected by this amendment and need separate work.

STAGING. This ADR decides the grammar only. It authorizes no code, no ledger migration, no REPRODUCIBLE persistence, no resolver or eligibility change, and no re-proof. Each remains its own reviewed unit: B2.1 (prover widening + re-run of the analysis), B3 (verdict_code migration under its own DBCP, class label, separate eligibility surface), B4 (engine adoption, production re-proof, manifest).

## Decision

AMENDS TWO ADRs — it supersedes neither.

(1) DEC-545a4d prong (b): the licensed rounding set (below). Prong (a), the EXACT class, the additive re-proof ledger, and the deterministic prover-policy-bound resolver are untouched and remain in force.

(2) DEC-c4619b §7: the operation-trace contract (see AMENDED TRACE CONTRACT below). Revision v2 of this ADR corrects an earlier draft that claimed DEC-c4619b was unaffected — that was wrong. §7 currently requires the trace to show "every non-exact node is exactly one invocation of this primitive", and licensing `multiply`/`plus`/`minus` over already-rounded operands introduces non-exact nodes that are NOT primitive invocations. The trace contract must therefore be amended explicitly rather than stretched silently. The rest of DEC-c4619b — the deterministic numeric execution profile, the scaled-decimal EXACT boundary, the §7 primitive itself and the disqualification of naive convert-then-divide — is unaffected and remains in force.

AMENDED CLAUSE. DEC-545a4d states: "REPRODUCIBLE iff the formula AST proves: every node is (i) EXACT under prong-(a) rules, or (ii) one IEEE-754 binary64 correctly-rounded operation (`divide`; `avg` as exact-sum / exact-count) whose operands are EXACT or REPRODUCIBLE." The parenthetical enumerates two operations and has been implemented as exhaustive (unit B2).

It is replaced by: every node is (i) EXACT under prong-(a) rules, or (ii) EXACTLY ONE IEEE-754 binary64 correctly-rounded arithmetic operation — `divide`, `avg` (as exact-sum / exact-count), `multiply`, `plus`, or `minus` — whose operands are EXACT or REPRODUCIBLE.

WHAT REMAINS REFUSED (unchanged, and explicitly not widened):
1. Aggregates other than `avg` over non-EXACT operands. `sum`, `min`, `max`, `median`, `percentile` over REPRODUCIBLE values are n-1 or more rounding events, not one operation, and stay NOT_PROVEN. `avg` still requires an EXACT operand for the same reason.
2. `mod` is NOT licensed. No live member needs it and its rounding semantics differ; licensing it would require its own decision.
3. Non-numeric operands. A node that is EXACT only in the sense of introducing no rounding (text, date, boolean) is not a valid operand of an arithmetic operation; the numeric regime is required (the guard added in B2).
4. Silent promotion. EXACT and REPRODUCIBLE remain distinct classes. `binary64_activation_eligible` stays EXACT-only. A REPRODUCIBLE member requires its own eligibility surface and must carry its class label on every decision, report, and closure surface.

OPERAND RULE (closes an overflow hole, and is the precise statement of "one operation"). A rounding node is licensed ONLY in these two situations:

(a) At least one operand is REPRODUCIBLE. The node is then exactly one hardware IEEE-754 binary64 operation over values that are already binary64. Licensed for `divide`, `multiply`, `plus`, `minus`.

(b) All operands are EXACT and the node is `divide` or `avg`. The node is then the exact-to-binary64 boundary crossing and MUST use the DEC-c4619b §7 rational-to-binary64 primitive over ONE exact rational.

Consequently, `multiply`/`plus`/`minus` over operands that are ALL EXACT is NOT a licensed rounding node. If prong (a) proves such a node exact, it needs no rounding; if prong (a) REFUSES it (for example an exact product whose interval exceeds the safe range), it stays NOT_PROVEN. It must never be rescued by converting exact operands to binary64 and operating on them — that is two operand roundings plus an arithmetic rounding, not one operation, and it is precisely the convert-then-divide anti-pattern DEC-c4619b §7 disqualifies.

AMENDED TRACE CONTRACT (amends DEC-c4619b §7). §7 requires the per-member operation trace to show that every non-exact node is exactly one invocation of the rational-to-binary64 primitive. That is replaced by: every non-exact node is exactly ONE correctly-rounded operation, which is EITHER one invocation of the §7 primitive (case (b) above) OR one hardware IEEE-754 binary64 operation over already-rounded operands (case (a)). The §7 primitive requirement is PRESERVED UNWEAKENED wherever the exact-to-binary64 boundary is crossed, and naive convert-then-divide remains disqualified.

The trace MUST record, per rounding node: node path, operation, operand classes, rounding provenance, and a per-member total count. Multi-event traces are explicitly authorized — a percentage legitimately carries two — and the trace must state the count rather than implying a single crossing.

PROVENANCE VOCABULARY (extends DEC-c4619b §7). Exactly one label per rounding node:

- `primitive_rational_to_binary64` — the boundary crossing via the §7 primitive (case (b)).
- `ieee_binary64_divide` — `divide` over an already-rounded operand.
- `ieee_binary64_multiply` — `multiply` over an already-rounded operand.
- `ieee_binary64_plus` — `plus` over an already-rounded operand.
- `ieee_binary64_minus` — `minus` over an already-rounded operand.

Labels are AST-op-aligned deliberately, so a trace reader can map every entry back to a node without inference. Any future licensed operation requires its own label and its own amendment.

SCOPE OF THE CLAIM. REPRODUCIBLE asserts replay determinism and nothing else: every licensed operation is correctly rounded, so a conforming platform reproduces the identical bit pattern on any replay. It does NOT assert accuracy. Chaining k correctly-rounded operations accumulates bounded, deterministic error; the class is honest about this precisely because the trace publishes k.

## Revision v2 (2026-07-20)

Per review `RESPONSE-Codex-...-D529-...-2026-07-20.md` (sha256
`f39bc015f59bcdc40000625a24058e2e4b81afd976110c5eb59c36b03140d38a`, CHANGES REQUIRED —
policy direction plausible, authority boundary wrong):

- **Corrected the authority claim.** v1 asserted "DEC-c4619b is likewise unaffected" while
  simultaneously expanding the trace and provenance contract that DEC-c4619b §7 governs. That
  was internally contradictory. This ADR now amends **two** ADRs explicitly — DEC-545a4d
  prong (b) for the licensed rounding set, and DEC-c4619b §7 for the trace contract — and
  states precisely what in DEC-c4619b is left untouched.
- **Added the AMENDED TRACE CONTRACT clause**, giving B2.1 an explicit authority for
  multi-event traces: every non-exact node is exactly one correctly-rounded operation, being
  either a §7 primitive invocation at the exact-to-binary64 boundary or one hardware IEEE-754
  operation over already-rounded operands. The §7 primitive requirement is preserved
  unweakened at the boundary, and naive convert-then-divide remains disqualified.
- **Added the PROVENANCE VOCABULARY clause**, defining the labels for `multiply`, `plus` and
  `minus` over already-rounded operands, which v1 required implicitly but never named.
- **Added the OPERAND RULE**, which closes a hole v1 left open: `multiply`/`plus`/`minus` over
  operands that are all EXACT is not a licensed rounding node, so a node prong (a) refuses
  (e.g. an exact product exceeding the safe range) can never be rescued by converting exact
  operands to binary64 — that would be operand roundings plus an arithmetic rounding, not one
  operation.

This ADR is `proposed`; no accepted text has been rewritten (the DEC-c4619b v2 precedent).
