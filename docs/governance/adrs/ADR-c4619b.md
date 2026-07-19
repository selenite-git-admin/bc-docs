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

The prong (a) preflight finding (d9fc0f3f) proved the scaled-decimal EXACT claim unsound for the pinned binary64-v1 engine: live production facts carry drift tails (fact.ms_gross_invoiced_amount 15478987.020000001) while both the canonical inputs (1716/1716 clean 2dp) and the storage columns (Postgres numeric) are exact — the error is manufactured entirely in the JS compute layer summing unit-value doubles. The v1 exactness gate's own text anticipated this fix ("before deterministic decimal execution lands"). Operator selected option 1 over an error-bound admission class (labels the error honestly but keeps producing it) and over holding the 182 blocked members (defeats the directory program). BigInt scaled-integer execution makes the EXACT-class arithmetic exact by construction, is native to the runtime (no dependency), and removes overflow concerns at execution; it additionally makes a single-rounding division claim POSSIBLE — but only via the §7 rational-to-binary64 correctly-rounded primitive, never from BigInt inputs alone — giving both DEC-545a4d prongs a sound re-anchor path under one profile. Storage needs no change, so the unit is compute-layer-only with pinned-version coexistence.

## Decision

Introduce a governed deterministic numeric execution profile (NUMERIC_REPRESENTATION_VERSION 'scaled-decimal-int-v1') under which amount/decimal metric values NEVER pass through JavaScript binary64: values enter from exact stores as decimal strings, are parsed to scale-pinned BigInt scaled integers (scale from the declared domain / ndp policy), all EXACT-class arithmetic (sum, plus, minus, integer multiply, comparisons, case, count) executes in BigInt, and results are emitted as exact decimal strings to Postgres numeric — which is already exact on both ends (empirically verified: canonical values clean 2dp, fact storage numeric; drift enters ONLY in the current JS compute layer). Scope: the M10 fixture verifier (formula-execution engine → v3) and the production metric evaluation engine; storage schemas untouched. Division/avg remain OUTSIDE the exact profile (DEC-545a4d prong (b) may re-anchor on this profile ONLY via the specified rational-to-binary64 correctly-rounded primitive — see §7; BigInt inputs alone do not make a division single-rounding). Existing facts computed under binary64-v1 are immutable and remain labeled by their recorded engine/representation pins — no rewrite, no recompute (Invariants III/V); corrected ongoing series arise only from new evaluations under the new profile. DEC-545a4d prong (a) re-proof evidence (held PR #496) becomes admissible ONLY for evaluation pinned to this profile. Domain-policy magnitude/cardinality bounds are retained solely as prover/domain governance — exactness is preserved only as decimal strings, SQL numeric, or scaled-integer payloads; float-parsed consumption is a presentation approximation outside the EXACT boundary (§5). Values entering from JSON numbers (legacy fixtures) are a distinct labeled entry class that cannot yield profile-pinned EXACT production evidence (§1); new fixtures carry decimal strings. Staged, each unit separately reviewed: (1) this ADR; (2) shared scaled-decimal arithmetic module + verifier v3; (3) production evaluation engine adoption; (4) prong (a) re-anchor + prong (b) package; (5) eligibility manifest v4.

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
   scale: int }`, scale pinned by the declared domain (ndp policy). Two labeled entry classes
   (v2, P1-3 correction): **`exact_string`** — the exact decimal string from the driver/authoring
   (never `Number()`), the only class admissible for profile-pinned EXACT production evidence;
   and **`legacy_json_quantized`** — a JSON number that already passed through binary64 before
   the profile saw it, admitted only through validated quantization to the declared scale
   (round-trip check), which proves scale-compatibility but NOT the original authored decimal.
   Legacy-quantized entry can never yield profile-pinned EXACT production evidence unless the
   package/evidence explicitly labels the quantized legacy source boundary; tests must prove
   this refusal. New fixtures carry decimal strings.
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
5. **Exactness boundary + transport (v2, P0-1 correction):** exactness is preserved ONLY while a
   value remains a decimal string, a SQL `numeric`, or a scaled-integer payload
   `{scaled_value, scale}`. A decimal fraction is generally NOT representable as binary64
   regardless of the scaled integer's magnitude (denominators carry a factor of 5: `0.01`,
   `12.34`, `15478987.02` are all inexact as JS numbers) — so NO downstream-binary64 exactness
   is claimed, bounded or not. Exact external transport is decimal string and/or the
   scaled-integer pair; a consumer that parses a decimal string into a float performs a
   presentation approximation OUTSIDE the EXACT evidence boundary, and profile-governed
   emissions never use JSON numbers for amount values. ndp magnitude/cardinality bounds are
   retained solely as prover/domain-policy governance (declared-domain sanity + the replayable
   cardinality proof basis), not as any downstream representability guarantee.
6. **Admissibility re-anchor:** DEC-545a4d prong (a) re-proof evidence (held PR #496) becomes
   admissible only for evaluation pinned to this profile; the re-proof ledger rows already
   retain prover + policy digests, and the admit-gate resolver must additionally match the
   representation pin.
7. **Division/avg rounding primitive (v2, P0-2 correction):** BigInt-exact inputs do NOT by
   themselves make a division "one correctly-rounded operation" — converting operands to JS
   numbers first rounds them before the divide (operand rounding + arithmetic rounding). Prong
   (b) REPRODUCIBLE may be claimed ONLY over a specified **rational-to-binary64
   correctly-rounded primitive**: from the exact rational
   `(scaled BigInt numerator, BigInt denominator, scale)` directly to the nearest binary64
   value (round-half-even), computed entirely in integer arithmetic (long division with
   guard/round/sticky bits), with NO intermediate binary64 conversion of either operand. The
   naive `Number(scaledValue) / 10^scale / count` is explicitly NOT that primitive and must
   never be labeled REPRODUCIBLE. Unit E3's proof package must carry the per-member operation
   trace showing every non-exact node is exactly one invocation of this primitive over
   exact/reproducible inputs. Prong (b) proceeds as its own reviewed unit only after this
   primitive is implemented and vectored.
8. **Legacy envelope engine (Path B, deprecated):** out of profile scope; it never gains the new
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

## Revision v2 (2026-07-19)

Per review `RESPONSE-Codex-DEC-c4619b-…-2026-07-19.md` (sha256 `e92ed2f2…`, CHANGES REQUIRED —
direction affirmed, two numeric overclaims corrected):

- **P0-1:** removed the false claim that sub-2^53 scaled bounds make decimal values exactly
  representable downstream in binary64; the exactness boundary is now explicit (decimal string /
  SQL numeric / scaled-integer payload only; float parsing = presentation approximation outside
  the EXACT boundary); exact external transport defined as decimal string and/or scaled pair.
- **P0-2:** the prong (b) claim is now conditional on a specified rational-to-binary64
  correctly-rounded primitive (integer long division, guard/round/sticky, round-half-even, no
  intermediate binary64); the naive convert-then-divide is explicitly disqualified; E3 must
  carry per-member operation traces.
- **P1-3:** entry classes split into `exact_string` vs `legacy_json_quantized` with the
  evidence-label refusal rule and required tests.

The v1 body text of §1/§5/§6 was corrected in place (this ADR was `proposed`, never decided;
no accepted text was rewritten). Also corrected the Decision paragraph's transport clause to
match §5.

## Revision v3 (2026-07-19)

Per v2 review (`3e723e97…`, CHANGES REQUIRED, narrow): the Context paragraph still carried the
rejected v1 claim ("turns division into a genuine single-rounding over exact inputs") — now
aligned with §7 (single-rounding possible ONLY via the specified primitive); duplicate spec item
numbering fixed (legacy engine renumbered 7→8).

## Review disposition

v1: CHANGES REQUIRED (`e92ed2f2…`). v2: CHANGES REQUIRED, narrow (`3e723e97…`). v3 pending
re-review; E1 blocked until accepted (operator ratifies).
