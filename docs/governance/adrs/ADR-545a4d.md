---
uid: DEC-545a4d
title: "Numeric admission classes v2: scaled-decimal exactness + correctly-rounded reproducibility"
description: "Unblocks 182 NOT_PROVEN members: scaled-decimal sums become provably EXACT (~96); division shapes admit under a bit-reproducible correctly-rounded class (~86); additive re-proof evidence, no snapshot mutation."
status: decided
date: 2026-07-19T08:33:36.573Z
project: bc-core
domain: metrics
subdomain: metric-runtime
focus: numeric-admission
---

# Numeric admission classes v2: scaled-decimal exactness + correctly-rounded reproducibility

## Context

Eligibility manifest v3 showed the ready pool is 59/241; all 182 blocked members fail the exactness prover for exactly two reason families. Family 1 (sums over decimal amounts, ~96) is mathematically exact in binary64 when amounts are scaled integers within bound — the prover lacks only a declared bounded domain; refusing these is prover incompleteness, not numeric risk. Family 2 (division, ~86) is genuinely not binary64-exact, but IEEE-754 division is correctly rounded and deterministic — bit-identical replay preserves what the exactness gate actually protects (reproducible, replay-verifiable evidence; Invariants V/VI), so a distinct honestly-labeled admission class is principled where a false EXACT claim would not be. Additive re-proof evidence respects Invariant III (frozen snapshots immutable) and Invariant VI (evidence emitted by running prover v2 over the same bytes, never inferred). Alternatives rejected: portfolio-wide metric reshape (heavy authoring, changes metric identity for 182 members); admitting NOT_PROVEN wholesale (abandons the gate); leaving 182 members permanently inadmissible (defeats the directory program).

## Decision

Two-pronged extension of the metric numeric admission model to unblock the 182 NOT_PROVEN directory members (manifest v3 canonical 786b0cff): (a) bounded scaled-decimal input domains — amount-typed inputs declare scale + magnitude bound; the exactness prover treats sum/add/subtract over scaled-bounded decimals as EXACT while the accumulated scaled magnitude is provably < 2^53 (reclaims ~96 members to full EXACT, no policy compromise); (b) a new REPRODUCIBLE admission class between EXACT and NOT_PROVEN — every operation either exact or a single IEEE-754 correctly-rounded operation (divide/avg) over exact or reproducible inputs, yielding bit-identical replay on any conforming platform (covers ~86 division-shape members under an explicit, honestly-labeled policy). The C9 admit gate accepts EXACT and REPRODUCIBLE; NOT_PROVEN remains refused. Frozen snapshots are NEVER mutated: re-classification of already-frozen packages is emitted as ADDITIVE re-proof evidence (prover v2 over the identical canonical package bytes, keyed by package_signature_hash, own DBCP-gated ledger), which the admit gate consults alongside the snapshot verdict. Implementation is gated: prong (a) first (prover + domain vocabulary), prong (b) second behind its own review; the re-proof ledger DDL requires explicit operator DBCP approval.

## Specification detail (for review)

**Measured blocker families (live, 2026-07-19, over the 182 = 117 operator_review actives + 65
corrected successors):**

| Family | exactness_reasons | n | Lever |
|---|---|---|---|
| 1a | `aggregate 'sum' over data values is not proven exact (unbounded accumulation or fractional)` | 84 | prong (a) |
| 1b | `variable_ref '…' numeric domain (rep=amount, dtype=decimal) is not a bounded integer` | 12 | prong (a) |
| 2a | `'divide' is not integer-exact` | 79 | prong (b) |
| 2b | `aggregate 'avg' … not proven exact` | 7 | prong (b) (avg = exact sum ÷ exact count, one rounding) |

The four families partition the 182 exactly; no member fails for any other reason.

**Prong (a) — prover rule.** An input whose declared domain is `scaled_decimal(scale=s,
|x| ≤ B)` is treated as the integer `x·10^s` with bound `B·10^s`. `sum`/`add`/`subtract` over
n such inputs is EXACT iff `n·B·10^s < 2^53` (n from the gate/window cardinality bound, declared
or derived). No change to admit-gate semantics — this widens what the existing EXACT verdict can
prove. Domain declarations live in the package (input_domain digest already exists in the
snapshot tuple); absent a declaration, behavior is unchanged (NOT_PROVEN).

**Prong (b) — REPRODUCIBLE class.** Verdict grammar becomes `EXACT | REPRODUCIBLE | NOT_PROVEN`.
REPRODUCIBLE iff the formula AST proves: every node is (i) EXACT under prong-(a) rules, or
(ii) one IEEE-754 binary64 correctly-rounded operation (`divide`; `avg` as exact-sum ÷
exact-count) whose operands are EXACT or REPRODUCIBLE. Such results are deterministic and
bit-identical on any IEEE-conforming platform — replay verification remains byte-exact. The admit
gate records which class admitted the member; downstream surfaces MUST carry the class label
(no silent promotion to "exact").

**Additive re-proof evidence (no snapshot mutation).** Frozen `mcv_package_snapshot` rows are
immutable (Invariant III). A re-proof runs prover v2 over the SAME `canonical_package_bytes`
(identity checked by `package_signature_hash`) and emits a new evidence row
{package_signature_hash, prover_algorithm_version, verdict, reasons, proved_at} in a dedicated
ledger (DDL via explicit operator DBCP; append-only; no FK mutation of the snapshot). The C9
admit gate reads: snapshot verdict OR latest re-proof verdict for the identical package hash —
never re-computing at read time (reads do not trigger evaluation).

## Foundation invariant test

- I (meaning once): the prover judges the frozen package bytes; metric meaning is untouched.
- III (immutability): snapshots never mutated; re-proof is additive evidence.
- V (non-replayable evaluation): admission reads recorded evidence; nothing re-evaluates on read.
- VI (evidence emitted): every verdict row is emitted by an actual prover run over identified
  bytes, never inferred from the old verdict.
- Repair location: (a) = D (prover) + B (domain vocabulary); (b) = B (admission semantics);
  ledger = E (additive, DBCP-gated).

## Staging

1. ADR review → decided.
2. Prong (a): prover v2 + domain vocabulary + re-proof ledger DBCP → re-prove the ~96 → verify
   reclassification on scratch first, one-then-many.
3. Prong (b): gate extension behind its own review → re-prove the ~86.
4. Eligibility manifest v4 re-derivation (same drift-refusing method) → pool restated.

## Review disposition (2026-07-19)

**ACCEPTED WITH BOUNDARY** — auditor response
`RESPONSE-Codex-DEC-545a4d-numeric-admission-classes-v2-review-2026-07-19.md`
(sha256 `b526b10f51825a565c88d4196eefbe3e00cad005b18ffb37d4094c2fa199e631`), operator-ratified.
Direction accepted; NO implementation, DDL, ledger write, manifest v4, or admission action
authorized — each unit separately governed. Binding boundaries: (a) is an EXACT proof extension
only, fail-closed to NOT_PROVEN on missing/stale/ambiguous/exceeded bounds; (b) is a distinct
class, never conflated with EXACT (`binary64_activation_eligible` stays EXACT-only; explicit
class field), surfaced in every decision/report/closure; re-proof ledger append-only + DBCP,
consulted via a deterministic prover-policy-bound resolver (not timestamp-latest); bit-replay
claims proven against pinned engine/rulebook; audit schemas must expose class + ledger row. The
response also answers the three open questions below and prescribes the per-prong proof packages.

## Open questions for review (answered by the disposition)

1. Cardinality bound source for prong (a): declared per-gate `n` vs derived from window/grain —
   which is authoritative, and what happens when the live population exceeds the declared bound
   (refusal at evaluation is the proposed answer)?
2. Should REPRODUCIBLE members carry a distinct activation-eligibility flag
   (`binary64_activation_eligible` stays EXACT-only; add `reproducible_activation_eligible`)?
3. Does the audit workflow's report/decision schema need the admission class surfaced
   (auditor-visible label), and does the re-proof ledger need to be part of the audit evidence
   closure for re-proved members?
