# D335 Full-Runway Diagnose Findings — 2026-04-15

**Session:** SES-8c652f
**Scope:** all 268 finance MCs on the D335 runway
**Tenant (testability check):** demo-selenite
**Total runtime:** 22 min (cold run) + 31 sec (cache-warm re-run after verdict-logic fix)

## Headline

> **91% of finance MCs (244 / 268) are currently blocked by upstream CF→BF semantic mismatches. 0 MCs pass all v0.3 integrity checks cleanly. 4 MCs are auto-fixable but untestable (no COs in demo-selenite). 20 MCs are human-required; only 4 of those have tenant data for verification.**

The D335 per-MC formula-correction workstream has a very narrow addressable set right now: **at most 4 MCs can be walked to a fully-verified fix today** (`mc__automated_gl_entry_rate`, `mc__cost_per_transaction`, `mc__customer_delinquency_rate`, `mc__equity_turnover_ratio` — all human-required, not auto-fixable). Everything else is either blocked upstream or can't be verified in the demo tenant.

## Distribution

| Bucket | Count | % |
|---|---:|---:|
| walkable (auto-fixable + testable) | 0 | 0.0% |
| untestable (auto-fixable, no tenant COs) | 4 | 1.5% |
| human-required | 20 | 7.5% |
| blocked | 244 | 91.0% |
| ready | 0 | 0.0% |

## Fail-finding class counts

| Check Code | Count | What it means |
|---|---:|---|
| `CF_BF_AI_MISMATCH` | 438 | AI judged CF↔BF pairing semantically incompatible (confidence ≥ 0.8). This is the v0.3 signal — the heuristic saw ~none of these. |
| `D335_SUM_ON_LATEST` | 187 | Formula uses SUM on a CF whose rule is `latest`. Recommend MAX, case-by-case. |
| `D335_SUM_ON_COUNT_DISTINCT` | 163 | Formula uses SUM on a CF whose rule is `count_distinct`. Recommend COUNT_DISTINCT. |
| `D335_SUM_ON_COUNT_WHERE_NOT_NULL` | 54 | Formula uses SUM on a CF whose rule is `count_where_not_null`. Recommend COUNT. |
| `CF_BF_SEMANTIC_MISMATCH` | 31 | v0.2 heuristic CF↔BF mismatch. AI caught 14× more of this class. |
| `GRAIN_CF_UNMAPPED` | 13 | Grain CF not in any bound CC's cc_field_mapping. |

Warn-level findings (reported but not counted as fail): `CF_BF_AI_AMBIGUOUS` and `MAPPING_COVERAGE_GAP` — seen mostly on human-required MCs.

## By subfunction

17 of 18 finance subfunctions have **100% block rate**. All progress is concentrated in 2 subfunctions:

| Subfunction | Total | Addressable (non-blocked) | % addressable |
|---|---:|---:|---:|
| revenue_accounting | 37 | 12 (3 untestable + 9 human-required) | 32% |
| general_finance | 35 | 6 (1 untestable + 5 human-required) | 17% |
| capital_structure_optimization | 6 | 2 (2 human-required) | 33% |
| fpa | 11 | 2 | 18% |
| treasury | 14 | 1 | 7% |
| investor_relations | 1 | 1 | 100% |
| **All others (12 subfunctions, 163 MCs)** | **163** | **0** | **0%** |

**The 100%-blocked subfunctions (accounts_payable, general_ledger, tax, accounts_receivable, payroll, fixed_assets, etc.) all need upstream CC mapping hygiene before any D335 walk is productive.**

## The 4 testable non-blocked MCs (per-MC walk candidates)

| MC | Subfunction | CO Count | Fail Codes | Needs human review because |
|---|---|---:|---|---|
| `mc__automated_gl_entry_rate` | revenue_accounting | 2052 | D335_SUM_ON_COUNT_DISTINCT | AI ambiguous on 1 input pair |
| `mc__cost_per_transaction` | general_finance | 2052 | D335_SUM_ON_COUNT_DISTINCT | AI ambiguous + MAPPING_COVERAGE_GAP |
| `mc__customer_delinquency_rate` | revenue_accounting | 1368 | D335_SUM_ON_COUNT_DISTINCT, D335_SUM_ON_COUNT_WHERE_NOT_NULL | AI ambiguous on 2 input pairs + MAPPING_COVERAGE_GAP |
| `mc__equity_turnover_ratio` | capital_structure_optimization | (testable) | D335_SUM_ON_LATEST | AI ambiguous + MAPPING_COVERAGE_GAP |

Each requires a human judgment on an AI-ambiguous CF↔BF pair before the D335 formula correction can safely be applied. These are the highest-value candidates for the next per-MC walk session.

## Systemic implications

1. **D335 is a downstream concern.** The 438 AI-caught mismatches are D301-era CF↔BF mapping bugs, not D335 formula bugs. D335-R4 corrections applied on top of wrong mappings produce varying-wrong results (MC#2 case from SES-60f784 proved this). The right sequence is: CC mapping hygiene → then D335 formula corrections.

2. **The heuristic alone was under-reporting by ~14×.** v0.2 flagged 31 `CF_BF_SEMANTIC_MISMATCH`; AI flagged 438 `CF_BF_AI_MISMATCH`. This is the quantified value of the v0.3 gate.

3. **demo-selenite has source-data coverage only in revenue_accounting and general_finance subfunctions.** All 24 non-blocked MCs cluster there. Other subfunctions need reader/OC work before any D335 activity can proceed to verification.

4. **Per-MC walkthroughs will produce ≤ 4 fully-verified fixes in the current state.** The D268 one-then-many discipline works against us here — we can't usefully walk 268 MCs one-by-one if 244 are blocked before the first formula fix. The SOP is correct; the runway is just mostly blocked.

## Recommendations for next session

| Priority | Workstream |
|---|---|
| 1 | **Pivot from D335 per-MC walks to CC mapping hygiene.** Pick a subfunction (suggest accounts_receivable, 16 MCs at 100% blocked) and audit its cc_field_mappings for CF↔BF semantic alignment. Fix at the CC layer; MCs will re-enter the runway. |
| 2 | Walk the 4 testable human-required MCs (one per session) to prove the SOP's human-required path and extract 4 clean fixes. Low-volume but high-signal. |
| 3 | Populate demo-selenite source data for accounts_payable / general_ledger / tax readers so currently-untestable MCs become testable. Unblocks Priority 1's verification path. |
| 4 | Extend the known-answer suite with 2-3 AI-ambiguous cases (from the 20 human-required MCs) so future prompt/model changes are regression-tested. |

## Bug fix shipped this session

`decideVerdict` in `mc-diagnose.mjs` had a logic hole: when fails existed, `CF_BF_AI_AMBIGUOUS` warns were not considered — so 3 MCs with D335 fails + AI-ambiguous warns were returning `auto-fixable` instead of `human-required`. First run reported 3 walkable; after fix, 0. Cache-warm re-run took 31s.

## Artifacts

- Full per-MC JSON: `bc-core/scripts/d335-runway-diagnose-2026-04-15.json`
- Human-readable table: `bc-core/scripts/d335-runway-diagnose-2026-04-15.md`
- Cache: `bc-core/scripts/.cache/mc-ai-review/` — ~600+ entries (one per distinct CF/BF/rule triple).

## D268 compliance

- Rule 1: no bulk chain generation. Diagnose is read-only. ✓
- Rule 3: one-then-many. Runway is diagnose-only; no fixes batch-applied. ✓
- Rule 4: independent verification. All findings come from live DB + live bc-ai calls. Cache is hashed to prevent stale reads. ✓
- Rule 6: checkpoints logged to DevHub every 50 MCs during cold run. ✓
- Rule 10: stop-and-flag on verdict-logic bug. Caught by spot-checking the 3 "walkable" results before writing them up; would have shipped wrong headline. ✓
