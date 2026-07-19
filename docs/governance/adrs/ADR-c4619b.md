---
uid: DEC-c4619b
title: "Deterministic numeric execution profile: scaled-integer exact arithmetic for metric evaluation"
description: "Amounts never touch binary64: BigInt scaled-integer execution between exact decimal stores; verifier v3 + production engine; binary64-v1 facts immutable+labeled; re-anchors DEC-545a4d prongs a+b."
status: proposed
date: 2026-07-19T09:12:34.043Z
project: bc-core
domain: metrics
subdomain: metric-runtime
focus: numeric-execution
---

# Deterministic numeric execution profile: scaled-integer exact arithmetic for metric evaluation

## Context

The prong (a) preflight finding (d9fc0f3f) proved the scaled-decimal EXACT claim unsound for the pinned binary64-v1 engine: live production facts carry drift tails (fact.ms_gross_invoiced_amount 15478987.020000001) while both the canonical inputs (1716/1716 clean 2dp) and the storage columns (Postgres numeric) are exact — the error is manufactured entirely in the JS compute layer summing unit-value doubles. The v1 exactness gate's own text anticipated this fix ("before deterministic decimal execution lands"). Operator selected option 1 over an error-bound admission class (labels the error honestly but keeps producing it) and over holding the 182 blocked members (defeats the directory program). BigInt scaled-integer execution makes the arithmetic exact by construction, is native to the runtime (no dependency), removes overflow concerns at execution, and turns division into a genuine single-rounding over exact inputs — rescuing both DEC-545a4d prongs with one profile. Storage needs no change, so the unit is compute-layer-only with pinned-version coexistence.

## Decision

Introduce a governed deterministic numeric execution profile (NUMERIC_REPRESENTATION_VERSION 'scaled-decimal-int-v1') under which amount/decimal metric values NEVER pass through JavaScript binary64: values enter from exact stores as decimal strings, are parsed to scale-pinned BigInt scaled integers (scale from the declared domain / ndp policy), all EXACT-class arithmetic (sum, plus, minus, integer multiply, comparisons, case, count) executes in BigInt, and results are emitted as exact decimal strings to Postgres numeric — which is already exact on both ends (empirically verified: canonical values clean 2dp, fact storage numeric; drift enters ONLY in the current JS compute layer). Scope: the M10 fixture verifier (formula-execution engine → v3) and the production metric evaluation engine; storage schemas untouched. Division/avg remain OUTSIDE the exact profile (they become provable as single-correctly-rounded REPRODUCIBLE ops over exact inputs — DEC-545a4d prong (b) re-anchors on this profile). Existing facts computed under binary64-v1 are immutable and remain labeled by their recorded engine/representation pins — no rewrite, no recompute (Invariants III/V); corrected ongoing series arise only from new evaluations under the new profile. DEC-545a4d prong (a) re-proof evidence (held PR #496) becomes admissible ONLY for evaluation pinned to this profile. Domain-policy magnitude/cardinality bounds are retained even though BigInt cannot overflow — they guarantee downstream binary64 consumers (JSON, dashboards) can represent results exactly. Values entering from JSON numbers (legacy fixtures) require validated quantization to the declared scale; new fixtures carry decimal strings. Staged, each unit separately reviewed: (1) this ADR; (2) shared scaled-decimal arithmetic module + verifier v3; (3) production evaluation engine adoption; (4) prong (a) re-anchor + prong (b) package; (5) eligibility manifest v4.

## Measured drift surface (reconnaissance annex, 2026-07-19)

Empirical anchors: canonical inputs clean (1716/1716 at exactly 2dp on
`co_customer_invoice_arpi_slice_v9_7_0.gross_amount`); storage exact (`numeric` on both canonical
and `fact.ms_*.metric_value`); exact SQL sum returns clean decimals; stored facts carry binary64
tails (`ms_gross_invoiced_amount` P01 `15478987.020000001`, P02 `…860000003`, P03 `…55000001`).
The full code-path map identifies every site (governed runtime path: `formula-execution.engine.ts`
`applyAggregate`/`applyArithmetic` shared with the M10 verifier; persistence bind
`governed-metric-persistence.adapter.ts`; re-hydration `fact-reader.service.ts` `coerceValue`
`Number(raw)`; composite path `Number()` cast; legacy envelope engine `runNumericAggregate`).
The postgres.js driver already returns `numeric` columns as exact strings (no custom parsers) —
the profile intercepts before any `Number()` conversion. No decimal/BigInt library is in use and
none is added: the profile uses native `BigInt`.

## Profile specification (decision detail)

1. **Representation:** an amount/decimal value under the profile is `{ scaledValue: BigInt,
   scale: int }`, scale pinned by the declared domain (ndp policy). Entry points parse the exact
   decimal STRING from the driver (never `Number()`); JSON-number entry (legacy fixtures) is
   admitted only through validated quantization to the declared scale (round-trip check), new
   fixtures carry decimal strings.
2. **Arithmetic (EXACT class):** sum/plus/minus over equal scales; multiply where ≤1 operand is
   scaled (scale preserved) — this also resolves the 11 scaled-multiply rehearsal residuals;
   comparisons over equal scales; case/count unchanged. All in BigInt — overflow impossible at
   execution. `divide`/`avg`/`median`/`percentile`/`moving_avg` are NOT in the exact profile
   (prong (b) re-anchors them as single-correctly-rounded over exact inputs).
3. **Emission:** results serialize to exact decimal strings for SQL binds (never JS-number
   binds on profile-governed values). The verifier's OutputComparator compares exact-class
   values by exact scaled equality — no epsilon.
4. **Pins:** `NUMERIC_REPRESENTATION_VERSION = 'scaled-decimal-int-v1'`; verifier engine bump
   (`mcf-verifier-v3`); the governed production engine records the same pins in evaluation
   evidence. Packages/snapshots frozen under `binary64-v1` are immutable and stay labeled;
   coexistence is by pin, never by rewrite (Invariant III), and nothing recomputes old facts
   (Invariant V).
5. **Bounds retained:** ndp magnitude/cardinality bounds stay governed even though BigInt cannot
   overflow — they guarantee any downstream binary64 consumer (JSON payloads, dashboards) can
   represent emitted values exactly, and they remain the prover's replayable proof basis.
6. **Admissibility re-anchor:** DEC-545a4d prong (a) re-proof evidence (held PR #496) becomes
   admissible only for evaluation pinned to this profile; the re-proof ledger rows already
   retain prover + policy digests, and the admit-gate resolver must additionally match the
   representation pin. Prong (b) REPRODUCIBLE becomes provable (exact inputs + one IEEE-754
   correctly-rounded division) and proceeds as its own reviewed unit after this profile ships.
7. **Legacy envelope engine (Path B, deprecated):** out of profile scope; it never gains the new
   pin, and metrics evaluated through it remain non-admissible under the exactness gate exactly
   as today. The composite path adopts the profile with the governed engine.

## Staging (each unit separately reviewed)

1. This ADR → decided.
2. Unit E1: shared scaled-decimal arithmetic module + `mcf-verifier-v3` (fixture playback +
   OutputComparator exact equality) + profile-pinned entry parsing; full vector suite.
3. Unit E2: governed production engine + persistence adapter + fact-reader adoption (string-path
   end-to-end); composite path; evaluation-evidence pins; scratch rehearsal proving byte-exact
   SQL-vs-engine agreement on live-shaped data.
4. Unit E3: DEC-545a4d prong (a) re-anchor (ledger DBCP + re-proof admissibility w/ pin match),
   then prong (b) package.
5. Eligibility manifest v4 re-derivation.

## Review disposition

Pending review (relayed to the auditor channel per the DEC-545a4d pattern; operator ratifies).
