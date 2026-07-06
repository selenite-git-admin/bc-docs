---
title: "Pass 1 calibration — Q1 through Q4 outcomes"
session: SES-594568
date: 2026-05-14
status: complete
type: calibration
authority: DEC-a17d0f
related:
  - 2026-05-12-pass1-grammar-artifact-register-SES-594568.md
  - DEC-01df6b  # contract_json authoritative
  - DEC-01419c  # MC body purity (9 keys)
  - DEC-a17d0f  # SDA umbrella
  - D232        # JSON-first principle
  - D233        # Three-level governance
  - D164        # Contracts platform-governed
---

# Pass 1 calibration — Q1 through Q4 outcomes

Short calibration MWR closing the six open questions raised in
`2026-05-12-pass1-grammar-artifact-register-SES-594568.md` (§4).
Q5 (output shape) and Q6 (AI Contract activation) are intentionally
**not** answered as separate questions — Q6 folds into the
certification step of Q4; Q5 was a documentation-shape question
that does not require its own decision now.

The audit plan's Pass 2–5 framing is **dropped** in favour of
picking concrete slices of work and shipping them one at a time
(SDA-4 pattern). The grammar artifact register (Pass 1) plus the
calibrations below are sufficient input.

## Q1 — Metric Contract body extensibility / master-shape update

**Outcome: Path A.** Any extension to the Metric Contract body
(currently 9 keys per DEC-01419c) requires an ADR plus a master-
shape update. Path B (in-place hygiene — extending the body
without governance) is rejected.

Rationale: the master shape governs validation across all
`contract_json` instances in the family. Silent extension would
let two MCs with the same `$contract` version disagree on body
shape, breaking the "shape is platform-locked" guarantee in
D233. Path A keeps every body-shape change auditable.

Practical effect on slice (1): the slice does **not** propose a
body extension. The 9-key body is sufficient for the promotion
gate Q4 specifies (formula, test data, certification verdict
live in their own places — body purity preserved).

## Q2 — Primitive lifecycle vocabulary

**Outcome: L1 three-state lifecycle.** Primitives (BO, BF, CF)
use `pending` → `active` → `retired`. Existing intermediate
ledger states (`draft`, `reviewing`, `proposed`, `certified`,
`deprecated`, `withdrawn`) collapse to one of the three under a
mapping recorded in the Q2 ADR. The 16 existing
`certification_record` rows are preserved under Invariant III
(immutability) — the mapping is declared, not retroactively
applied.

Driver: AI-readability. AI callers cannot reliably reason about
six near-synonymous states; three load-bearing states match how
the lifecycle is actually monitored (rarely, at transitions only).

The Q2 ADR is a prerequisite to any work that transitions
primitive state, and is therefore a near-term enabler — but
slice (1) below does not transition primitives; it operates on
the Metric Contract layer only.

## Q3 — `metric_formula` / `metric_formula_variable` / `metric_binding` as authority

**Outcome: not a design question.** DEC-01df6b (D248) already locks
the answer: **`contract_json` is authored, catalog tables are
derived.** The Metric Evaluator reads `contract_json` only. The
catalog tables are projections. If they disagree, `contract_json`
wins. No direct writes to `metric_formula`, `metric_formula_variable`,
or `metric_binding` from authoring flows.

What remains is a conformance check (was Pass 2 in the original
plan): does the current implementation respect this? That check
becomes part of slice (1) below — when we wire the promotion gate
end-to-end, we verify the writes go through `contract_json` only.

## Q4 — Promotion gate (seed → catalog)

**Outcome: gate requires three things, all self-contained.**

1. **Formula** — well-formed expression over declared variables
   (`I1`, `I2`, …). Variables are abstract; they do not reference
   real CFs at definition time.
2. **Test data** — synthetic inputs + expected output. Formula
   runs against the test data and produces the expected number.
3. **Certification** — bc-ai maker-checker (cross-family) runs
   once, verdict recorded in `metric_formula_verification` as the
   evidence ledger for the formation act. If verdict is `fail` or
   `not_run`, promotion is blocked.

If all three pass, the seed becomes a defined Metric Contract.
The contract is then honored — no re-verification on read, no
aging, no separate verification lifecycle to babysit.

### Bridges are platform-authored, not part of MC definition

A defined MC uses **abstract variables**. Whether any CF, BF, or
SF exists to feed those variables is a **separate, downstream
question** (chain readiness, per-source bridge inventory). MC
definition does not block on chain availability.

### Universal-bridge thesis (recovered)

The platform's value proposition: **metric grammar is universal,
and bridges (SF → CF → MC variable) are also universal for
standard source-product installs.** SAP FAGLPOSE.WRBTR carries
the same meaning on every standard SAP install. NetSuite revenue
carries the same meaning on every standard NetSuite install. The
platform authors bridges once, AI + HITL, and they apply to every
tenant on that source.

Per-tenant context-assertion at the bridge level is not the model.

### Custom-field edge — Foundation-resolved

Already locked by Foundation:

- Source Contract `fields[]` carries `z_extension` per field
  (`the-contract-grammar.md` §Source Contract).
- D233 three-level governance: tenant customization lives **only**
  in Contract Binding (Tenant Override level). Contracts themselves
  are platform-governed artifacts (D164). Contract Bindings cannot
  remove platform-declared fields or modify platform-declared rules.

Custom fields are isolated by construction. They never enter the
universal contracts and therefore never compromise the universal
bridge claim.

### Q6 (AI Contract activation) folds into Q4

The dual-AI maker-checker call in Q4's certification step is the
operational substrate the AI Contract family would govern, if/when
that provisional family activates. No separate decision required
now; activation can be revisited when there are enough verification
acts to justify governing them as a family.

## Pass 2–5 dropped — work proceeds as slices

The five-pass audit-plan framing is **withdrawn**. It was producing
documents about documents. The grammar register (Pass 1) plus this
calibration is enough to start real work.

Each future slice gets its own plan-and-result MWR pair, SDA-4
pattern. Three candidates, ordered by platform value:

1. **Wire the seed → catalog promotion gate end-to-end on one
   metric.** Real code, real DB writes, real `metric_formula_verification`
   row written by the act. After this slice: the gate is real.
2. **Author universal bridges for SAP standard finance fields and
   pilot-confirm one metric on real install data.** After this
   slice: the universal-bridge thesis is proven once end-to-end.
3. **Ship the `z_extension` rejection path at admission so custom
   fields are isolated into Contract Binding scope.** After this
   slice: the universal/custom separation is enforced, not just
   declared.

Next slice selection is the next operator decision.

## Findings carried forward from Pass 1

The six findings (§3.3.1 – §3.3.6) of the Pass 1 register remain
open. They are not re-litigated here. Each lands inside whichever
slice closes it:

- §3.3.1 (MC body shape risk) → closed by Q1 (Path A governance
  rule; slice (1) honours it by not extending the body).
- §3.3.2 (primitive lifecycle multiplicity) → closed by Q2 L1.
- §3.3.3 (`metric_formula_verification` underpopulation) → closed
  by slice (1).
- §3.3.4 (726 / 729 MCs lacking verification) → grandfathered;
  cleared one at a time on next author-edit, by slice (1)'s gate.
- §3.3.5 (catalog–contract_json divergence) → conformance check
  inside slice (1).
- §3.3.6 (count divergence across MLS / dial / inspector /
  chain_status / version table) → tracked by TSK-9702ac, blocked
  on arch completion (post-slices).

## Boundaries honoured

- No code change in this MWR.
- No DB write, no DBCP.
- No new gate proposed beyond what Foundation, DEC-01df6b,
  DEC-01419c, and D232/D233/D164 already specify.
- No new task filed beyond TSK-9702ac (pre-existing).
- The decision to drop Pass 2–5 is procedural, not architectural —
  it does not modify any Foundation or ADR commitment; it only
  withdraws an audit-plan structure proposed mid-session.

---

**End of calibration.**
