# D335 MC Chain Integrity — Per-MC Walkthrough Log

Append-only record of each MC walked through [mc-chain-integrity-sop.md](../../../../archive/onboarding/mc-chain-integrity.md).

Format: one section per walkthrough. Newest at bottom.

---

## mc__active_customer_rate — 2026-04-15 — BLOCKED

- **DevHub session:** SES-60f784
- **MC UID:** `019d7838-9dc1-71a7-85af-1fc0d3bbede6`
- **Subfunction:** finance / revenue_accounting
- **Version at walk time:** 1.1.0 (active)
- **Formula:** `O1 = (SUM(I1) / SUM(I2)) * C1`
- **Existing snapshots:** 779 snapshots, all value = `100` (one distinct payload — the constant-100 signal)
- **Runway bucket:** B5 (BLOCKED)

### Diagnose output (v0.2 heuristic — final)

Two fail findings after SOP heuristic refinement:

1. `D335_SUM_ON_COUNT_WHERE_NOT_NULL` — I1 wraps in SUM but rule is count_where_not_null. Recommend COUNT.
2. `CF_BF_SEMANTIC_MISMATCH` — I2: CF `total_customer_accounts` (count-name) → BF `receivable_hdr_amount` (currency-name) with rule=`sum`. Rule doesn't bridge count↔value; SUM of currency ≠ count of accounts.

Verdict: **BLOCKED** (CF↔BF semantic mismatch sends to blocked path).

**Initial v0.1 heuristic run (SUPERSEDED — false positive).** v0.1 flagged both I1 AND I2 as CF↔BF mismatches. I1's CF is also count-named over a currency BF, but rule=`count_where_not_null` is precisely the intended bridge (COUNT of the amount column = count of rows with amount). v0.1 missed this. v0.2 recognizes bridging rules; I1 now correctly passes. Lesson logged to SOP Change Log.

### Actions taken (SOP Step 5 — Blocked path)

- v0.2 diagnose confirms I2 is the real blocker. I1 is aligned under the bridging rule.
- FUP-1 in `scripts/d335-phase3-followups.md` is correctly scoped to I2 only (already).
- Runway row updated to ⚠ (blocked, see FUP-1).
- **No new version created.** MC remains at 1.1.0.

### Verification

Not applicable — blocked path exits before fix or verify.

### Outcome

`blocked` — MC held at v1.1.0 until upstream cc_field_mapping review (D301-era) re-examines whether `receivable_hdr_amount` is the right BF target for I2 (`total_customer_accounts`). Re-enters runway after FUP-1 resolves.

### Learnings for the SOP

- **Heuristic v0.1 → v0.2 update forced mid-walk.** Good example of "let the SOP evolve from the walks, not designed in vacuum." Had we proceeded with v0.1, we'd have blocked ~80% of top-5 runway candidates with false-positive CF↔BF mismatches, wasting judgment time and potentially opening FUPs that didn't belong.
- Diagnose's handling of the blocked path is correct — emits all fail findings, does not stop at first. This is important because a single walk can surface multiple problem classes.
- The v0.2 heuristic rule-of-thumb: *a name gap is only a gap if the rule doesn't close it.* This is the crux of D335's "rule is documentary" position — the rule tells you what SHOULD be happening; the formula tells you what IS happening; the mismatch is between those two. CF/BF names are the third dimension.

---

## mc__average_invoice_value — 2026-04-15 — UNTESTABLE (rolled back)

- **DevHub session:** SES-951037
- **MC UID:** `019d7838-31f8-7e12-8129-c4cc051bd131`
- **Subfunction:** finance / general_finance
- **Formula (pre-fix):** `O1 = SUM(I1) / SUM(I2)` (unit: currency)
- **Existing snapshots:** 0 in demo-selenite
- **Runway bucket:** B0

### Diagnose output (v0.3 — heuristic + AI)

- 1 fail finding: `D335_SUM_ON_COUNT_WHERE_NOT_NULL` (I2 `total_number_of_invoices`)
- AI review: 2 pairs, both aligned at sufficient confidence — no AI findings
- **Verdict: AUTO-FIXABLE**

### Actions taken

1. `mc-fix.mjs --apply=D335_SUM_ON_COUNT_WHERE_NOT_NULL` → Status 201, v1.1.0 active, v1.0.0 superseded.
2. `mc-verify.mjs --version=1.1.0 --tenant=demo-selenite` → **0 COs sampled from bound CC**. Cannot trigger evaluation. Verify exits with error, not FAIL.
3. Per new SOP Step 6.5 (UNTESTABLE): supersede v1.1.0 → v1.0.0 auto-reactivated.

### Outcome

`untestable` — FUP-3 needed: the bound CC for this MC has no canonical objects in demo-selenite, so no fix applied to this MC can be proved. MC held at v1.0.0 pending reader/OC work that populates COs for the bound CC.

### Learnings for the SOP

- **New verdict path needed: UNTESTABLE.** SOP v0.3 had only ready/auto-fixable/human-required/blocked. When bound CC has 0 COs in the verification tenant, neither A0 nor A1 can be asserted. Added Step 6.5 pre-check.
- **Empirical:** across 7 B0 candidates screened this session, 6 came back blocked/human-required under v0.3 AI review, and the one auto-fixable happened to be UNTESTABLE. The happy path is rarer than the bucket distribution suggested. This is a product-state problem (bindings outpace source coverage), not a SOP bug.
- **Governed rollback for UNTESTABLE is identical to verify-FAIL rollback:** supersede new version, prior auto-reactivates. Clean.

---

## mc__revenue_recognition_lag — 2026-04-15 — FAIL (rolled back)

- **DevHub session:** SES-60f784
- **MC UID:** `019d760b-0bf1-76cc-88ee-e67d23d7cc02`
- **Subfunction:** finance / accounts_receivable
- **Version at walk time:** 1.0.0 (active)
- **Formula (pre-fix):** `O1 = SUM(I1) / SUM(I2)` (unit: days)
- **Existing snapshots:** 779 snapshots, 779 distinct values, range [0.002, 0.143]
- **Runway bucket:** B0

### Diagnose output (v0.2 heuristic)

Single fail finding:
1. `D335_SUM_ON_COUNT_WHERE_NOT_NULL` — I2 (`number_of_revenue_transactions`) wraps in SUM but rule is `count_where_not_null`. Recommend COUNT.

No CF↔BF semantic mismatch detected (v0.2 heuristic passed — both I1 `total_days_between_invoice_and_recognition` and I2 have neutral name tokens).

Verdict: **AUTO-FIXABLE**.

### Actions taken (SOP Step 3 — Auto-fixable path)

1. `mc-fix.mjs --apply=D335_SUM_ON_COUNT_WHERE_NOT_NULL` dry-run confirmed:
   - `O1 = SUM(I1) / SUM(I2)` → `O1 = SUM(I1) / COUNT(I2)`
   - Only I2 matches count_where_not_null rule; I1 stays SUM.
2. Real fix: POST `/api/onboarding/mc/:id/versions/1.1.0` — Status 201 CREATED. v1.0.0 auto-superseded per D305.

### Verification (SOP Step 7)

`mc-verify.mjs --version=1.1.0 --tenant=demo-selenite`:

- Pre-fix (v1.0.0): n=779, distinct=779, range=[0.002, 0.143]
- Triggered eval on 200 sampled COs from bound CC
- Post-fix (v1.1.0): n=115, distinct=1, all values = `2026`

Assertions:
- A0 (new snapshots created): PASS (115)
- A1 (new.distinct ≥ old.distinct): **FAIL** (old=779, new=1)
- A3 (eval no errors): PASS

Verdict: **FAIL**.

### Root cause (discovered post-verify)

I1 CF `total_days_between_invoice_and_recognition` is mapped to BF `receivable_hdr_fiscal_year` with rule `sum`. Per-row, fiscal_year = 2026; SUM across N rows in a grain = 2026N; divided by COUNT(I2) = N gives constant 2026. Arithmetic is now correct; the BF is nonsense for the CF.

This is **NOT** something D335-R4 can fix. It is a CF→BF mapping error that the v0.2 heuristic couldn't detect (both name tokens are neutral: "days" ∉ VALUE_TOKENS and "fiscal_year" ∉ COUNT_TOKENS).

### Rollback

`POST /api/contracts/:id/versions/1.1.0/supersede` → Status 200. v1.0.0 auto-returned to active. v1.1.0 preserved as `superseded` for audit.

115 wrong snapshots remain tagged with `metric_version='1.1.0'` (superseded); consumers querying for active version will not see them.

### Outcome

`blocked (verify-fail)` — FUP-2 opened in `d335-phase3-followups.md`. MC held at v1.0.0.

### Learnings for the SOP

- **The heuristic cannot catch all semantic mismatches.** Even with v0.2's rule-bridging awareness, a mapping like `days → fiscal_year` slips through because both tokens are neutral. The SOP's Step 7 verify is not belt-and-suspenders; it is the **primary** defense against this class. Do not skip verify even when diagnose says auto-fixable.
- **The heuristic need: v0.3 would add DURATION_TOKENS (days, hours, minutes) and DATE_TOKENS (year, date, period) and flag duration ↔ date pairings as mismatches regardless of rule.** But even this would miss many cases (e.g., CF `customer_churn_rate` ↔ BF `delinquent_balance` — both value-ish but semantically unrelated). Open question: is there a tractable heuristic, or does every MC need an AI review pass?
- **The governed rollback path works.** Supersede-new → prior-auto-activates is clean. v1.1.0 is preserved for audit. No manual DB surgery needed.
- **Verify's assertion A1 (new.distinct ≥ old.distinct) was the catcher.** If we'd only assertion'd A0 (new snapshots created) we'd have shipped this. Keep A1.
- **Next walkthrough (MC #3) should pick an auto-fixable candidate whose CF and BF names are *both* clearly aligned** (ideally CF and BF share a common root token), to establish a PASS case for the SOP. The current 2-for-2 fail rate isn't representative; we need a confirmed happy path.

---
