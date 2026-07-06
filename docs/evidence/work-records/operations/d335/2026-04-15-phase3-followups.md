# D335 Phase 3 — Follow-ups & Blocked MCs

**ADR:** `legacy-v2/docs/decisions/ADR-35b34b.md` (DEC-35b34b)
**Owner:** bc-core / Metric Governance
**Opened:** 2026-04-15

This file tracks D335 Phase 3 blockers that must be resolved before individual MCs
can be approved with corrected formulas. Each entry represents a finding that is
out-of-scope for D335 itself (which is formula↔rule alignment only) but that prevents
us from shipping a semantically-correct metric even after applying the D335-R4 fix.

---

## Class A — CF↔BF mapping-semantic errors (D301-era review needed)

### FUP-3 — `mc__average_invoice_value` bound CC has no COs in demo-selenite (UNTESTABLE)

**Status:** OPEN — MC held at v1.0.0 pending reader/OC work.

**Finding.** The bound CC for this MC has zero canonical objects in the demo-selenite tenant. Verify step cannot trigger evaluation. Fix looked structurally correct (v0.3 diagnose verdict: AUTO-FIXABLE, AI reviews aligned) and was applied cleanly via McOnboardingService, but no snapshot verification is possible. Per SOP v0.3 Step 6.5, superseded v1.1.0 and reverted to v1.0.0.

**Evidence.**
- MC UID: `019d7838-31f8-7e12-8129-c4cc051bd131`
- Subfunction: finance / general_finance
- `mc-verify.mjs` reported `0 COs sampled from bound CC(s)`

**Recommended action.** Identify the bound CC, trace upstream to find which reader/OC should populate it, and admit sample data for demo-selenite so this MC re-enters the runway as walkable.

---

### FUP-2 — `mc__revenue_recognition_lag` I1 CF→BF mapping is semantically wrong (discovered via verify-fail)

**Status:** BLOCKED — MC rolled back to v1.0.0 after D335-R4 fix produced constant value `2026`.

**Finding.** CF `total_days_between_invoice_and_recognition` is mapped to BF `receivable_hdr_fiscal_year` with rule `sum`. The CF name implies "days" (a duration); the BF is a fiscal year. SUM(fiscal_year) across rows in a grain group → `2026 * N`. When I2's COUNT returns N (the row count), the ratio collapses to the constant `2026` — the fiscal year literal.

**Why the D335 audit did NOT catch this.** Name tokens on both sides are neutral to the v0.2 CF↔BF heuristic (COUNT_TOKENS: number_of/count/qty; VALUE_TOKENS: amount/balance/revenue/etc.). "days" and "fiscal_year" don't match either bucket, so the heuristic passed the pairing. Only the Step 7 verify step caught it — post-fix the metric collapsed to a single value across 115 grain groups.

**Evidence.**
- MC UID: `019d760b-0bf1-76cc-88ee-e67d23d7cc02`
- CC: `cc__receivable_hdr` (`019d762a-13e9-789e-86ad-02afdad6eb24`)
- I1 CF: `total_days_between_invoice_and_recognition` → BF `receivable_hdr_fiscal_year` (rule sum)
- I2 CF: `number_of_revenue_transactions` → BF `receivable_hdr_amount` (rule count_where_not_null)
- Pre-fix v1.0.0: 779 snapshots, 779 distinct values, range [0.002, 0.143] — varying nicely, but on a mathematically wrong formula (SUM of years / SUM of currency)
- Post-fix v1.1.0: 115 snapshots, 1 distinct value = 2026 — the formula is now arithmetically correct but the inputs are nonsense

**Recommended action.**
1. The I1 CF must bind to a BF that actually carries day-count or date-difference semantics. Either: (a) the source receivable table has an `invoice_date` and `recognition_date` and we compute the diff via a D330 compute CF, or (b) the metric is implementable only after such source data is admitted.
2. Until the I1 mapping is corrected, `mc__revenue_recognition_lag` cannot be given a trustworthy formula regardless of D335-R4.

**Decision today.** v1.1.0 superseded, v1.0.0 restored to active. MC remains not-approved (v1.0.0's values are also wrong, just not obviously-constant-wrong).

---

### FUP-1 — `mc__active_customer_rate` I2 mapping is semantically wrong

**Status:** BLOCKED — MC must not be approved with any formula until mapping is reviewed.

**Finding.** The input variable `I2 = total_customer_accounts` is mapped via
`cc_field_mapping` to BF `receivable_hdr_amount` (a currency amount) with rule `sum`.
The CF name implies a count of customer accounts; the BF it resolves to is a dollar
figure. Even after D335-R4 flips I1 from `SUM`→`COUNT`, the metric reduces to
`count_of_active_rows / sum_of_receivable_dollars × 100` — unit-incompatible, still wrong.

**Why D335 alone can't fix this.** D335 audits formula aggregation vs. the declared
resolution_rule_code. It does NOT audit whether the BF that a CF resolves to is
semantically the right source for that CF. The rule says `sum` and the formula says
`SUM` — aligned — so the audit gives it a pass on I2 even though the mapping choice
is wrong at a deeper layer.

**Evidence.**
- MC UID: `019d7838-9dc1-71a7-85af-1fc0d3bbede6`
- CC: `cc__receivable_hdr` (`019d762a-13e9-789e-86ad-02afdad6eb24`)
- CF: `total_customer_accounts` → BF `receivable_hdr_amount` (rule `sum`)
- CC: same → CF: `number_of_active_customer_accounts` → BF `receivable_hdr_amount` (rule `count_where_not_null`)
- Both CFs resolve to the same BF; only one can represent truth.
- 779 existing snapshots in demo-selenite all show value = 100 (the SUM/SUM = 1 × 100 artifact the ADR describes).

**Recommended action.**
1. A `cc__receivable_hdr` → `customer_account` BF or equivalent count-carrying BF
   needs to exist in the source contract chain. Today `receivable_hdr` likely has one
   row per invoice/receivable, not one row per customer account — so even a COUNT
   over this CC counts receivables, not accounts.
2. Either: (a) rebind I2's CF mapping to a proper customer-account source, or
   (b) re-scope this metric to `active_receivable_rate` against the actual
   receivables grain, or (c) mark the MC as not implementable against current source
   contracts.
3. Only after mapping review is the D335-R4 formula correction safe to apply.

**Decision today.** v1.2.0 with `O1 = (COUNT(I1) / SUM(I2)) * C1` is NOT created.
The MC remains at v1.1.0 with its known-wrong constant-100 output, documented as such.

---

## Class B — Scope-wide follow-up

### FUP-SW-1 — Audit tool extension: CF↔BF semantic-alignment check

**Status:** open, not scheduled.

**Finding.** The D335 Phase 2 audit (`d335-audit-formula-rule-mismatch.mjs`) is
necessary but not sufficient. It catches only formula↔rule mismatches. A second
audit dimension is needed: CF↔BF semantic alignment (does the BF a CF resolves
to actually carry values that match the CF's name/intent?).

**Recommended action.** Before batch Phase 3 corrections go out, either:
1. Add a Phase 2b audit step that pairs CF name + BF name + rule + sampled values
   and flags semantic mismatches (likely AI-verified, since naming similarity ≠ semantic alignment).
2. Require manual domain review on each MC before its Phase 3 correction is approved.

**Risk if skipped.** Applying D335-R4 formula corrections wholesale would replace
known-wrong-constant values with known-wrong-varying values — no net gain in trust,
and harder to detect the remaining error because the output is no longer the obvious
constant 100 signal.

---

## How to add new entries

New items: append under the appropriate class. Each entry must include:
- Status (BLOCKED / open / resolved)
- Specific MC / CC / CF UIDs
- Why the D335 audit alone won't catch it
- Recommended action with owner (if known)
- Decision today (whether to proceed, park, or block)
