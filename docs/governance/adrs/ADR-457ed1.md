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

AMENDS DEC-545a4d prong (b) — it does NOT supersede it. Prong (a), the EXACT class, the additive re-proof ledger, and the deterministic prover-policy-bound resolver are all untouched and remain in force. DEC-c4619b (deterministic numeric execution profile) is likewise unaffected.

AMENDED CLAUSE. DEC-545a4d states: "REPRODUCIBLE iff the formula AST proves: every node is (i) EXACT under prong-(a) rules, or (ii) one IEEE-754 binary64 correctly-rounded operation (`divide`; `avg` as exact-sum / exact-count) whose operands are EXACT or REPRODUCIBLE." The parenthetical enumerates two operations and has been implemented as exhaustive (unit B2).

It is replaced by: every node is (i) EXACT under prong-(a) rules, or (ii) EXACTLY ONE IEEE-754 binary64 correctly-rounded arithmetic operation — `divide`, `avg` (as exact-sum / exact-count), `multiply`, `plus`, or `minus` — whose operands are EXACT or REPRODUCIBLE.

WHAT REMAINS REFUSED (unchanged, and explicitly not widened):
1. Aggregates other than `avg` over non-EXACT operands. `sum`, `min`, `max`, `median`, `percentile` over REPRODUCIBLE values are n-1 or more rounding events, not one operation, and stay NOT_PROVEN. `avg` still requires an EXACT operand for the same reason.
2. `mod` is NOT licensed. No live member needs it and its rounding semantics differ; licensing it would require its own decision.
3. Non-numeric operands. A node that is EXACT only in the sense of introducing no rounding (text, date, boolean) is not a valid operand of an arithmetic operation; the numeric regime is required (the guard added in B2).
4. Silent promotion. EXACT and REPRODUCIBLE remain distinct classes. `binary64_activation_eligible` stays EXACT-only. A REPRODUCIBLE member requires its own eligibility surface and must carry its class label on every decision, report, and closure surface.

MANDATORY EVIDENCE. The per-member operation trace required by DEC-c4619b §7 must record EVERY rounding event with its node path, operation, operand classes, and rounding provenance, plus the per-member total. Under this amendment a member may legitimately carry more than one rounding event — a percentage carries two — and the trace must state the count rather than implying a single crossing. The distinction between `primitive_rational_to_binary64` (the exact-to-binary64 boundary crossing, which must use the DEC-c4619b §7 primitive) and `ieee_binary64_divide` (an operation over already-rounded operands) is retained.

SCOPE OF THE CLAIM. REPRODUCIBLE asserts replay determinism and nothing else: every licensed operation is correctly rounded, so a conforming platform reproduces the identical bit pattern on any replay. It does NOT assert accuracy. Chaining k correctly-rounded operations accumulates bounded, deterministic error; the class is honest about this precisely because the trace publishes k.
