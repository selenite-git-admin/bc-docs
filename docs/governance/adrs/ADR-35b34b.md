---
uid: DEC-35b34b
title: "Aggregation Authority — Metric Formulas Own Aggregation; cc_field_mapping.resolution_rule_code Becomes Documentary"
description: "Resolve the silent-wrong-values problem: metric.service.translatePayload copies BF values without honoring resolution_rule_code (count_distinct/count_where_not_null/latest), producing meaningless metric values for ~55% of currently-producing MCs. Fix: consolidate all aggregation at the metric-engine formula layer. cc_field_mapping rules become documentary; formulas are authoritative."
status: decided
subdomain: aggregation
focus: governance
date: 2026-04-15
project: bc-core
domain: contracts
decision_code: D335
authority: authoritative
refs:
  - type: decision
    uid: DEC-d72560
    label: "D301 — Canonical Field as 3rd Contract Primitive (introduced resolution_rule_code)"
  - type: decision
    uid: DEC-9a5dc0
    label: "D302 — CC Field Mapping: 1-BF-to-Many-CFs + Filter (extended rule semantics)"
  - type: decision
    uid: DEC-637072
    label: "D330 — Derived Canonical Fields (per-row compute primitive)"
  - type: decision
    uid: DEC-c0290f
    label: "D315 — Metric Evaluation Verification Framework"
migrated_from: legacy v2 archive
---

# Aggregation Authority — Metric Formulas Own Aggregation

## Context

### Discovery

During SES-de4e13 (D330 Phase 6 implementation), diagnostic work on `mc__average_days_delinquent` revealed that `metric.service.assembleInputPayloads` — specifically the `translatePayload` closure at line 543 — **does not honor `cc_field_mapping.resolution_rule_code`**. Its logic is:

```typescript
for (const [bfName, cfEntries] of bfToCfMap) {
  const value = payload[bfName];
  if (value === undefined) continue;
  for (const { cfName } of cfEntries) {
    result[cfName] = value;   // pure BF-to-CF rename; rule is ignored
  }
}
```

The rule codes `sum`, `count_distinct`, `count_where_not_null`, `latest`, `assert_equal` that D301 introduced and D302 extended are **dead metadata** at metric evaluation time.

### Scope

Platform `contract.cc_field_mapping` distribution (2026-04-15):

| rule | rows | % |
|---|---|---|
| `sum` | 1,022 | 60.8% |
| `count_distinct` | 297 | 17.7% |
| `latest` | 255 | 15.2% |
| `count_where_not_null` | 65 | 3.9% |
| `assert_equal` | 40 | 2.4% |
| `compute` (D330) | 2 | 0.1% |

**617 rows (36.7%)** declare a rule other than `sum` — the rules that translatePayload ignores. Every MC whose inputs include any of these is at risk of silent-wrong values.

### Concrete evidence — `mc__active_customer_rate`

- Formula: `O1 = (SUM(I1) / SUM(I2)) * C1`
- I1 = `number_of_active_customer_accounts` → mapped to `receivable_hdr_amount` with rule `count_where_not_null`
- I2 = `total_customer_accounts` → mapped to `receivable_hdr_amount` with rule `sum`
- Both CFs point to the SAME BF (`receivable_hdr_amount`)

What happens at runtime:
1. translatePayload copies `receivable_hdr_amount` → both `I1` and `I2` slots (same value)
2. Metric engine: `SUM(I1) = SUM(amounts across grain)`, `SUM(I2) = SUM(amounts across grain)` — identical
3. Result: `(SUM/SUM) × 100 = 1.0 × 100 = 100`

**Every grain group emits `active_customer_rate = 100`** — a constant. This has been shipping as "accepted" data.

Verified in tenant: `evaluation_result_json.grainResults[*].metricValueJson.active_customer_rate === 100` across all 779 grain groups. The rule declared `count_where_not_null` was the authors' intent; the formula uses `SUM`; neither actually produces a count.

### Producing-MC impact

Of 20 currently-producing MCs in demo-selenite:

| Category | Count |
|---|---|
| Only `sum` rules on inputs | 9 (likely trustworthy) |
| At least one `count_where_not_null` input | 8 (suspect — formula vs rule mismatch) |
| At least one `count_distinct` input | 2 (suspect) |
| At least one `latest` input | 3 (suspect) |
| Uses D330 `compute` | 1 (trustworthy — compute is honored) |

Overlap: 11 of 20 producing MCs (55%) have at least one non-`sum` non-`compute` input and are potentially wrong.

### Root cause

Aggregation semantic is **overspecified** — both in `cc_field_mapping.resolution_rule_code` AND in MC formula aggregation functions (SUM/AVG/COUNT/MIN/MAX). These two sources of truth diverge in practice:

- `cc_field_mapping` says: "when translating this BF to this CF, aggregate using rule X"
- MC formula says: "when computing this metric, apply aggregation function Y to the CF values"

Both cannot be authoritative. Today the mapping rule is advisory (ignored at runtime) but declared — creating a false sense that the rule matters.

## Decision

### D335-R1: MC formula is the authoritative aggregation layer

All aggregation (SUM, AVG, COUNT, MIN, MAX, COUNT over filters, etc.) lives in metric-engine formula evaluation. A metric says *"O1 = SUM(I1) / COUNT(I2)"* and that is what executes — no translation-time pre-aggregation.

### D335-R2: `cc_field_mapping.resolution_rule_code` becomes documentary

The column stays for historical/governance purposes but is no longer consulted by any runtime code. Its values (`sum`, `latest`, `count_distinct`, `count_where_not_null`, `assert_equal`, `compute`) continue to describe **authorial intent** — "this CF was intended to be used with a COUNT-style aggregation" — but the runtime does not enforce this.

New CC governance gate (`CR-QG-CC-010`): for a CF declared with rule `count_*`, all referencing MC formulas must wrap the CF in a COUNT-family metric aggregation. This gate checks intent/usage consistency at MC-binding time, not at translation time.

### D335-R3: Extend metric engine with COUNT_DISTINCT

Metric engine currently supports SUM, AVG, COUNT, MIN, MAX. Adding COUNT_DISTINCT is a small extension that lets MC formulas express `count_distinct` intent directly: `COUNT_DISTINCT(field_code)`.

Implementation: add to `resolveAggregation` in metric-evaluation-engine.service.ts:
```typescript
case 'COUNT_DISTINCT': {
  const seen = new Set(payloads.map(p => p[fieldCode]).filter(v => v != null));
  result = seen.size;
  break;
}
```

### D335-R4: MC formulas audited and corrected per authorial intent

Every MC whose inputs declare a `count_*` rule gets its formula audited:

| Current formula pattern | Intent | Corrected formula |
|---|---|---|
| `SUM(I)` where I is `count_where_not_null` | count of rows | `COUNT(I)` |
| `SUM(I)` where I is `count_distinct` | count distinct | `COUNT_DISTINCT(I)` |
| `SUM(I)` where I is `latest` | latest value per grain | `MAX(I)` (for dates) or design decision for non-dates |

Correction is done via `McOnboardingService.createVersion` — the governed path. Each MC gets a new version with the corrected formula; prior version is superseded.

### D335-R5: `assert_equal` semantic is preserved implicitly

Grain fields (company_code, fiscal_period) declared with `assert_equal` continue to work because:
- They are CC grain dimensions; translation copies them into every payload identically
- Metric engine groups BY grain before evaluating formulas
- Grain fields are not aggregated by formula; they're dimension keys

No change needed.

### D335-R6: `latest` semantic requires case-by-case review

`latest` is currently used 255 times. It means "in a grain group, take the one value (or the most-recent one if disambiguation needed)". Most uses are probably on grain-identity fields where all rows in the group share the same value (so MAX/MIN/LATEST are all equal). A few may need genuine temporal-latest semantics.

The audit (D335-R4) will identify which `latest`-tagged MCs need attention. For those:
- If values are identical within grain: formula `SUM(I)` was wrong (inflates by count), should be `MAX(I)` or `MIN(I)`
- If temporal-latest is needed: either compute `MAX(I)` (if a timestamp orders the values) or introduce a new `compute` mapping with a D330 `latest_where` function (future work)

## Options Considered

### Option A: Honor resolution_rule_code in translatePayload (grain-aware) (REJECTED)

Make translatePayload compute grain groupings and apply the rule per-group, emitting one pre-aggregated payload per grain group.

**Why rejected:**
- Requires translatePayload to know about grain (currently grain is metric-engine concern)
- Metric engine already groups by grain; double-grouping is redundant
- Changes semantic of formulas: SUM(CF) across N rows would become SUM across M pre-aggregated values — confusing
- Still leaves us with two aggregation layers (translation + formula) that must agree

### Option B: Make formulas authoritative, migrate mappings (CHOSEN)

Covered above as D335-R1 through R6.

**Why chosen:** One aggregation authority. No runtime changes to translation (already pure rename). Small extension to metric engine (COUNT_DISTINCT). Per-MC formula audit + correction via governed service. Existing cc_field_mapping rows untouched; their `resolution_rule_code` stays as documented intent.

### Option C: Do nothing — accept silent-wrong values (REJECTED)

Document the problem but ship no fix.

**Why rejected:** `mc__active_customer_rate = 100` forever is not a shippable product state. Trust in metric values is foundational to BareCount.

### Option D: Migrate all count_* mappings to D330 compute (REJECTED)

Each count_where_not_null row becomes a `row_count_where` compute mapping. Aggregation semantic stays in the mapping layer, just using the compute primitive.

**Why rejected:** Doubles the mapping complexity without clarifying where aggregation lives. Also fundamentally doesn't change the issue — D330's compute is evaluated per-row (returning 0 or 1), then metric engine SUMs. So it's equivalent to having the formula say COUNT directly. Option B is simpler.

## Consequences

### Positive

- Metric values become trustworthy for all producing + future MCs
- One aggregation authority (metric-engine formula) — simpler mental model
- Runtime code does not change (translation already does the right thing for its role)
- D330 compute fits naturally: it's per-row derivation; aggregation of computed rows still happens in the formula

### Negative

- Audit burden: every MC that binds a `count_*` or `latest` input needs its formula reviewed. Likely ~20-30 MCs across producing + rejected sets
- Some formulas may need significant rework (e.g., `(SUM(I1) / SUM(I2)) * 100` might become `(COUNT_WHERE(I1, filter) / COUNT(I2)) * 100` — requires engine support for conditional count or D330 mapping split)
- `resolution_rule_code` becoming documentary is a conceptual reset — CF-authoring tools and docs need updating to reflect this

### Risks

| Risk | Mitigation |
|---|---|
| Audit misses a wrong formula → silent-wrong persists | Automated check: scan all MCs, flag any input CF whose cc_field_mapping.rule ≠ sum AND whose formula wraps it in SUM(). Output a gap list. |
| Formula corrections break previously-accepted evaluations (values change) | Expected. These MCs were reporting wrong numbers. Re-evaluation post-correction gives honest numbers. Communicate to users: "numbers updated to reflect actual definition." Log each correction in the metric version history. |
| Metric-engine COUNT_DISTINCT differs from DB COUNT(DISTINCT) semantics for null handling | Unit test explicitly covers null handling: skip nulls, not count them. |
| Legacy `latest` mappings that encoded per-group "pick one value" semantic can't be expressed as MAX/MIN | Case-by-case: most will work with MAX/MIN. Those that need true temporal-latest get a D330 `latest_where` extension (separate ADR). |

### Neutral

- No schema changes
- No data changes to existing cc_field_mapping rows (they're now documentary)
- D330 compute primitive remains; complementary to D335
- Chain completeness SSOT (D305) is unchanged — it inspects mapping existence, not rule semantics

## Migration Plan

1. **Phase 1 — Engine extension**
   - Add `COUNT_DISTINCT` to metric engine's `resolveAggregation`
   - Unit tests
2. **Phase 2 — Audit tool**
   - Script: for each MC with variables that reference non-sum cc_field_mappings, output current formula + flag if formula uses SUM/incorrect aggregation
   - Output: CSV/report of suspect MCs, their formulas, and recommended corrections
3. **Phase 3 — Per-MC formula correction (one-then-many)**
   - Pick ONE suspect MC (e.g., `mc__active_customer_rate`)
   - Apply corrected formula via `McOnboardingService.createVersion`
   - Re-evaluate; confirm new value ≠ old constant; confirm semantic correctness
   - Batch-apply remaining corrections, evaluating each
4. **Phase 4 — Documentation update**
   - CC creation SOP: note that `resolution_rule_code` is now documentary; real aggregation lives in MC formula
   - Metric authoring docs: list available aggregations (SUM, COUNT, COUNT_DISTINCT, AVG, MIN, MAX)
5. **Phase 5 — CR-QG-CC-010 gate**
   - On MC binding, check formula aggregations match CC input rule intent; warn on mismatch
6. **Phase 6 — Chain-status refresh + verify**
   - Producing count should be ≥ pre-migration (wrong values were still "accepted")
   - Spot-check 3-5 previously-constant-valued MCs to confirm numbers are now varying by grain group

## Rollback

- Phase 1: revert COUNT_DISTINCT addition (engine returns unknown-aggregation error)
- Phase 3 corrections: each MC's prior version is preserved; supersede the new version to restore prior behavior
- No data mutations outside MC versions

## Out of Scope

- `latest` → true temporal-latest semantic with ORDER BY (needs D330 extension, separate ADR)
- Filtered sums beyond what D330 `sum_where` already provides
- Metric engine extension for per-grain-group windowed functions (rolling averages, etc.)
