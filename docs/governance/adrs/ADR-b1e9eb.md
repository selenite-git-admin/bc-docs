---
uid: DEC-b1e9eb
title: "Metric output declaration: unit of measure, decimal places and rounding, with currency only for monetary output"
description: "Every new metric contract version declares its output unit (master.master_unit_type), decimals (money: derived from master.dim_currency.decimal_places) and rounding (half_up default); evaluation keeps inputs and intermediates exact and rounds once, on the final value; realises the grammar's 'result shape and units' and ADR-da4c51 check 5; amends DEC-c4619b."
status: proposed
date: 2026-09-30T04:09:24.622Z
project: bc-core
domain: metrics
subdomain: metric-contract
focus: output-declaration
---

# Metric output declaration: unit of measure, decimal places and rounding, with currency only for monetary output

## Context

The contract grammar says a Metric Contract declares "unit semantics" and its body declares "result shape and units" (docs/foundation/the-contract-grammar.md:208,210). The Metric Evaluation chapter says the result "type and unit conform to the Contract's declared result shape and units". Two earlier ADRs name the pieces: ADR-8f09d9 lists a fixed body key `unit`, "Output unit (days, %, $, count, ratio)", and ADR-da4c51 requires validation check 5, "Output unit matches".

The MCF substrate never realised this.
- mcf.metric_contract and mcf.metric_contract_version have no unit, decimals or rounding column (bc-core docker/redesign/04-mcf-substrate.sql:62-104; 18 live columns on the version).
- Their only output-side declaration is aggregation_currency_code (24-mcf-aggregation-currency.sql:5-6; 36-...:7-18).
- The package output_digest reads unit and type from a role_kind_code='output' binding (mcf-package-input.build.ts:105-108; mcf-realization-projection.service.ts:219-224). There are none live (input 418, metric_input 332), so every package hashes unit and type as null.
- A ratified unit vocabulary exists but is unused: master.master_unit_type, 11 codes (15-genesis-vocab-seed.sql:131-136).
- Metric values are never rounded (governed-metric-persistence.adapter.ts:122-124), and fact.ms_*.metric_value is unconstrained numeric.

As a result, aggregation_currency_code was standing in for the output unit. That breaks for days, ratios, percentages and counts: the U9.6 DSO certification rejection, and 18 contradictory composites (DEC-fa7c63 Amendment 5, bc-docs#105).

## Decision

1. **Each new version declares one output specification.** Every NEW metric contract version declares exactly one:
   - (a) the unit of measure, from master.master_unit_type;
   - (b) decimal places, 0 to 6, for every non-money unit. For unit `currency` the places are DERIVED, never declared, from master.dim_currency.decimal_places of the resolved currency:
     - local_currency: the evaluated legal entity's tenant_dim.dim_legal_entity.currency_code;
     - single_currency_required and document_currency: only the one currency the evaluation establishes for its rows.
     - An unknown, missing or mixed currency refuses. The column default is never a fallback.
   - (c) the rounding mode: half_up, the platform default, meaning round half away from zero (Excel ROUND parity); or half_even, declared explicitly.
2. **Currency must be coherent with the unit.** aggregation_currency_code stays on the version: unit `currency` requires document_currency, single_currency_required or local_currency, and every other unit requires not_applicable. This is D520 made structural.
3. **Precision and rounding rule:**
   - (i) Inputs keep full source precision; sums and all intermediate arithmetic are exact, with no per-line rounding.
   - (ii) Rounding happens ONCE, on the final metric value, to the declared (or derived) decimals, half-up by default. The largest rounding effect is therefore half of the last shown digit, however many lines are summed.
   - (iii) Divided results (averages, ratios, DSO) are computed as exact fractions and rounded once at the end. This is the new labelled numeric class DECLARED_DECIMAL: exact inputs, rational arithmetic, one declared decimal rounding, and no binary64. It amends DEC-c4619b.
   - (iv) Amounts arrive as the source system recorded them. A foreign-currency line's company-currency amount is converted and rounded by the source at posting, and BareCount takes it as recorded, never re-rounding it.
   - Formulas the rational evaluator cannot express (median, percentile, moving_avg, mod) keep the labelled or refused paths of gen-398517-02.
4. **Evidence records the output and its rounding.** It holds the declaration plus the exact value, the decimals and their source (declared, or the derivation path and value), the mode, and the rounded decimal string, identical in all three evidence copies.
5. **Package identity:** output_digest covers the declaration for new packages, through a versioned v4 package identity. Existing v3 packages and digests are untouched. The v4 landing updates the platform package builders and the independent auditor validator together, and proves the two agree before any declared package is admitted.
6. **The authoring check:** PE-MC enforces ADR-da4c51 check 5 ("output unit matches") with a unit algebra annexed to this ADR. For example: currency divided by currency gives ratio; count divided by count gives ratio; ratio times days(window) gives days; ratio times literal 100 gives percentage; currency times currency is refused.
7. **No backfill.** Existing versions behave exactly as today, with no declaration, and gain one only as a new version (Invariants III and V).
8. **Storage and version boundary:** a new 1:1 immutable table, mcf.metric_output_declaration. Its DBCP needs the operator's explicit DB yes.
   - A one-row policy table records the cutover time, when the migration applies. A version created at or after the cutover is post-cutover.
   - A declaration is refused on any pre-cutover version, and on any frozen version: the platform's existing freeze predicate, meaning an approval, active or audit state, or an approval snapshot.
   - A post-cutover version cannot enter a frozen state, or receive a package snapshot, without its one declaration.
   - Once a declaration exists, the version's aggregation_currency_code can no longer change, so the coherence of rule 2 cannot be broken by a later parent update.

## Order

This comes before S2 of gen-398517. S2's binary64 dispatch then covers only undeclared, legacy metrics.

## Foundation gate

- **Location:** B, a missing declaration, so this is a design act.
- **Not upper:** the grammar already requires it.
- **Not lower:** rounding in persistence, or inferring a unit at read time, would be compensation.

## Operator decisions

Given in chat on 2026-09-30 and relayed by SES-bc9863: half_up is the default; percentage is stored 0-100; this comes before S2; money decimals are derived from the currency's minor unit with no override; and rounding happens once, on the final value.

**These are not yet authority for review or execution.** The operator's direct grant is requested in bc-exchange as request 2026-09-30T04-13-10-016Z-dac91602 on thread gen-fe8f9d. This ADR cites the recorded grant id and its text hash once the grant is recorded.

**The DSO successor (W9 U9.6)** is proposed to declare days, two places and half_even, explicitly. That matches the acceptance rule in DEC-fa7c63 Amendment 4 (f), "both rounded half-even at 2 decimal places", which stays unchanged. This is pending the operator's direct grant, request 2026-09-30T04-13-10-037Z-bed807b6.

## Rationale

It realises a declaration the grammar already requires, removes the misuse of aggregation_currency_code as a unit, and makes the DSO's value equal to the exact quotient at its declared decimals by construction. It is grounded in a reading study (TSK-af9706; Codex design review gen-fe8f9d-01, pending).

## Annex A: unit algebra for the "output unit matches" check

An input's unit comes from its binding. A monetary amount (DEC-14f5b6 rule 2) counts as `currency`, a count as `count`, and a fixed-unit measure as its declared unit. The rules:

| Operation | Result |
|---|---|
| `currency ± currency` | `currency` (one aggregation basis, D520 and DEC-fa7c63 Amendment 5 (a)) |
| `currency ÷ currency` | `ratio` |
| `count ÷ count` | `ratio` |
| `ratio × days(window)` | `days` |
| `ratio × 100` | `percentage` (literal 100 only; the literal carries its unit) |
| `currency × currency` | refused (`MC_DEFECT_UNIT_PROMOTION`, MCF requirements) |

A formula whose derived unit differs from the declared unit is refused. Distinct rules for `rate` and `score` are not settled by this ADR; a metric using them refuses at the check until an amendment defines them.

## Annex B: grounding for rule 3 (iv)

The Kaveri legal entity's recorded journal-line amounts arrive at no more than two decimals. The canonical objects `fact.co_cc_x13pb_v2_0_0` (debit, credit and posted amounts, 28,928 rows) hold no value with more than 2 decimal places (read-only query on tbc_kaveri_dev, 2026-09-29, SES-a5e264). BareCount admits and resolves these recorded amounts as they are; the canonical derivation arithmetic that could alter them is unused by any active canonical contract.

## Review

Proposed. Codex design review round 1 on gen-fe8f9d-01 returned CHANGES REQUIRED: version boundary, parent-update coherence, v4 agreement across both engines, and the DSO rounding reconciliation. This revision answers it, and round 2 follows once the operator's grants are recorded. The design and the DBCP for `mcf.metric_output_declaration` then goes to the operator for the DB yes. Implementation follows in separately reviewed slices: the DBCP apply, the authoring and PE-MC check, the evaluator's DECLARED_DECIMAL path with its evidence, and the package-format step.
