---
uid: DEC-414ba2
title: "Correctly-rounded reproducibility is a distinct, labelled basis for metric audit eligibility"
description: "Ratio metrics (divide/avg) can never be EXACT; recognise DEC-545a4d prong (b) REPRODUCIBLE as a sufficient but distinctly labelled eligibility basis, under three conditions."
status: implemented
date: 2026-07-24T13:49:33.156Z
project: bc-core
domain: metrics
subdomain: metric-audit/numeric-admission
focus: governance
---

# Correctly-rounded reproducibility is a distinct, labelled basis for metric audit eligibility

## Context

**The measured problem.** Division and averaging cannot be proven exact — the quotient does not
terminate, so a value must be discarded. Under the exactness-only eligibility rule the entire ratio family
(DSO, turnover, margin %, concentration, on-time rate, average days to collect, per-unit) is
**permanently** ineligible for audit, regardless of correctness.

**Evidence (live, 2026-07-24; the split independently verified twice by AuditHub):**

- 182 `computed`/`NOT_PROVEN` package snapshots; 96 carry re-proof evidence; the remaining **86 split
  exactly 79 `divide` + 7 `avg`**.
- The 7 `avg` members were **executed** through the merged `ExactnessReproofService` on a faithful
  throwaway clone: **7/7 NOT_PROVEN, 0 EXACT, 0 refused**, identical reason
  `aggregate 'avg' over data values is not proven exact`. Averaging is summation plus division and fails
  structurally like divide. Clone dropped; production ledger re-verified unchanged at 96 rows / 94 EXACT.
- **Therefore the winnable prong-(a) backlog is zero.** Running all 86 through exactness would write 86
  evidence rows and move **not one** member into an eligible cohort.
- `mcf.exactness_reproof_evidence` holds 94 EXACT + 2 NOT_PROVEN, **all `mcf-exactness-v2`**. Zero
  `mcf-reproducibility-v1` rows have ever been written.
- `manifest-v4-derive.mjs` instantiates `ExactnessAdmissibilityResolver` only and re-cohorts solely on
  `aPinned.admissible`; **no reproducibility consumer exists in the derivation**.

**Why this finishes a decision rather than reversing one.** DEC-545a4d deliberately created **both**
prongs, and prong (b) is fully implemented and merged — prover, service, resolver, specs. What was never
decided is whether prong (b) counts toward *eligibility*. No prior ADR ruled that it does not; it was
simply never wired to a consumer. **This is a gap, not a rule being relaxed.**

**Why not "allow rounding".** That loose framing would admit arbitrary rounding and implementation drift,
and would be a genuine quality regression. Correctly-rounded reproducibility is a rigorous guarantee:
every rounding is the nearest representable value under a defined rule, so any conforming implementation
reproduces bit-for-bit identical results. It is the standard prevailing in the wider industry; requiring
"never rounds" is stricter than that norm and, as measured, unsatisfiable for most of a finance metric set.

**Consequence if declined.** BareCount could certify only counts and sums (AR balance, invoice count,
total invoiced) and never the ratios that constitute the actual analytical product. That is a
product-viability question, not merely a governance one.

## Decision

Where prong-(a) EXACT admission is mathematically unavailable, a metric MAY be audit-eligible on the basis
of DEC-545a4d prong (b) **CORRECTLY-ROUNDED REPRODUCIBILITY** (`mcf-reproducibility-v1`), subject to three
binding conditions:

1. **DISTINCT LABEL, NEVER SUBSTITUTION.** Every audit decision MUST record which basis it rests on
   (EXACT or REPRODUCIBLE). A consumer MUST always be able to distinguish "this computation never rounds"
   from "this computation rounds predictably". The existing three-way separation in code — structural via
   `prover_algorithm_version`, nominal via `reproducibleAdmissible` vs `admissible`, explicit via by-name
   refusal — is **preserved, not weakened**; eligibility gains a second accepted basis, it does not merge
   the two.

2. **THE ERROR BOUND TRAVELS WITH THE CLAIM.** The published operation count `k` / error bound MUST be
   part of the evidence a decision cites. REPRODUCIBLE must never degrade into an unbounded assurance.

3. **EXACTNESS STILL WINS WHERE AVAILABLE.** Metrics whose arithmetic permits prong (a) remain
   EXACT-basis. Nothing already proven EXACT is downgraded, relabelled, or re-derived. Prong (b) is
   admissible **only** where prong (a) is mathematically unattainable.

## Scope and boundaries

**This decision governs AUDIT ELIGIBILITY only. It does NOT decide runtime ACTIVATION.** The
`binary64_activation_eligible` flag and the non-collapse assertion in the manifest derivation
("reproof-sourced admissibility never implies b64") are explicitly **out of scope** and remain as they
are. Whether a REPRODUCIBLE-basis metric may be activated for runtime is a separate, undecided question.

**Known unverified at ratification** — recorded so the decision is made with its limits visible:

- Ratio exposure among the **68 `not_computable`** snapshots and the **120 MCVs with no snapshot at all**
  is NOT measured. Real exposure is likely **larger** than 86, not smaller.
- The interaction with `binary64_activation_eligible` is NOT verified (deliberately out of scope above).
- No consumer change is designed or authorised by this ADR.

## Ratification

Ratified by the **operator**, consistent with the D519/D523 external-audit gate under which the
code-review engagement concluded on 2026-07-19 with the operator as **sole ratifier**. AuditHub
verification is cited as **input, not as the ruling**:

- `QUESTION-Claude-reproducible-not-exact-ratio-eligibility-2026-07-24.md`, sha256
  `2a970062717e6e3d8d993eb448abe8af097abc07fe17c86e7e96a031b79ba2ad` — ACCEPTED WITH BOUNDARY, framing
  confirmed, derivation and live table state independently verified, **no doctrine answer given**.
- `AMENDMENT-Claude-ratio-eligibility-all-86-measured-2026-07-24.md`, sha256
  `7d7a2760389880584daaa02744418df4dcc90692c320549596da64442baef851` — ACCEPTED WITH BOUNDARY, durable
  production state and the 79/7 split re-verified, clone-drop boundary confirmed, **no doctrine answer
  given**.

## Consequences

- **88 metrics** that are today permanently ineligible gain a path to audit eligibility.
- Every future ratio metric has a path rather than a dead end.
- Audit decisions gain a mandatory **basis label**.
- Implementation is expected to be small: the eligibility derivation must accept a prong-(b) record and
  carry its label and bound. That work is **not** authorised by this ADR and takes the normal review flow.
- **Principal residual risk:** a downstream consumer that reads "audited" without checking the basis could
  treat a REPRODUCIBLE metric as EXACT. Condition 1 exists to prevent exactly this, and the label must be
  mandatory rather than advisory in any implementation.
