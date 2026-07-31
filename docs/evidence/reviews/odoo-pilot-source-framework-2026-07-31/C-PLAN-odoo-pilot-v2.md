# PLAN — Odoo Pilot v2 (the post-dry-run build)

**Status:** SKELETON — being assembled while the dry-run finishes its gate. The dry-run
(2026-07-30, ~17 commits, three remediation waves, ~1,730 cancelled documents) is the
evidence base; every section cites what was paid for. Full text lands after the gate +
AMI close out the dry-run.
**Authority:** D537 (pre-staging) · D538 (master-data framework) · D539 (no platform FX).
**Operator decisions embedded:** benchmarks-in-profile · dry-run framing · **chronological
build (2026-07-30: "company creation is step#1. then monthly records along with new
customers and vendors in flow. new machines or retiring one or two machines in a natural
flow... if we doing it then let us do it perfect")**.

## 1. THE ARCHITECTURE: one chronological simulation loop

The dry-run built in LAYERS (full funnel window → full coverage window → full scenarios
window → retrofits). That layering caused, directly and measurably:
- balance-driven remittances locked in by ref before other passes posted their balances
  (the phantom-remit wave — 363 cancelled);
- reversal generators re-walking history they had already written (REV-chains — 368);
- depreciation running on asset accounts before any machine was "bought";
- loans/CC/payroll retrofitted against a world that already had five years of shape;
- three separate remediation waves to reconcile passes with each other.

v2 builds the way the operator framed it — **the way a company actually happens**:

```
simulate_company_creation()          # step #1: incorporation, capital, config, CoA,
                                     # supplementary accounts, bank accounts, facilities
for month in window:                 # then the world only ever moves FORWARD
    master_deltas(month)             #   new customers/vendors onboard, some churn,
                                     #   machines bought (bill!) or retired (disposal +
                                     #   loss-on-sale), price revisions take effect
    operations(month)                #   CRM pipeline (some win -> SO -> delivery ->
                                     #   invoice; most lose/linger), POs -> receipts ->
                                     #   bills, imports, IC trade
    month_close(month)               #   payroll accrual, depreciation on assets that
                                     #   EXIST, accruals, CC breathing, statement lines
    next_month_obligations(month+1)  #   remits (GST 20th, PF 15th, wages 5th), EMIs,
                                     #   settlements, accrual reversals on the 1st
```

Why this is not cosmetic:
- **Causal coherence becomes structural**: depreciation cannot precede acquisition,
  remittance reads the true prior-month balance by construction, a reversal can only
  reverse what the same loop wrote last month. The entire class of inter-pass defects
  disappears rather than being gated against.
- **It mirrors the platform's own execution model** — forward-only object progression,
  no back-reference, no rewrite. The world engine adopting the same discipline as the
  thing that will read it is the right kind of perfect.
- **Master data lives in the flow**: a customer exists because they were onboarded in
  month 14; a machine depreciates because it was purchased (as a named vendor bill) in
  month 9 and stops when retired (disposal entry + Loss on Sale of Assets — the chart
  ships the account) in month 51.
- Operator is right that BareCount may not read most of this directly — but every
  drill-down an auditor or prospect performs must survive. Causal coherence under
  arbitrary inspection is what makes the demo unassailable.

**Honest limit (logged, not hidden):** chronology inside a single build day makes every
*document date* real, but wall-clock metadata (`create_date`, mail tracking, CRM
`date_closed`) still stamps the build day — Odoo owns those timestamps and refuses
backdating through the ORM (dry-run proof: writes ignored/recomputed; forcing = SQL =
forbidden). Consequence: **historical CRM velocity is structurally undemonstrable for a
back-seeded world.** Only the living-data doctrine fixes it: from go-live, the catch-up
loop creates each month's records near their true dates, and genuine journeys accumulate
forward. v2 therefore treats the back-seed as "books history" and the living window as
"behavioral history", and says so.

## 2. Dry-run learnings ledger (input, to be expanded at close-out)

**Rebuild-native (cannot retrofit):** inventory/stock valuation (product type locks once
moves exist — storable + RM/FG + opening stock from month 1, MES/QA wave); CRM journeys
(above); income-account routing by product category; PO-linked purchase history.

**Generator rules (each paid for):** idempotency = ref + `state != cancel`; one rnd
stream per generator per month (`{seed}-{gen}-{code}-{ym}`), never shared across
generators (rerun divergence planted anomaly doubles); reversal sources must exclude
their own outputs (`not like %-REV`); registers/answer-keys built by DISCOVERY from the
world, never by logging creations; balance-driven generators only inside the
chronological loop.

**Mechanical gates (replace eyeballs):** profile benchmarks (B2B ad-spend error class →
failing script), per-company CoA coverage ≥70%, integrity sweep (per-company zero-sum,
orphans, FX both-amounts), anomaly register reconciliation, §1 metric-demand map refresh.

**Config is a pass, not a side effect:** setup_config.py audits+repairs identity/bank/
tax/supplementary accounts; onboarding banner via odoo shell; `with_company()` does not
filter; res.partner.bank drops company_id on create; Community lacks
account_tax_periodicity; odoo shell needs the real db password from the compose file.

**Ops traps:** ec2-user not ubuntu; pkill/pgrep -f match their own ssh cmdline; Odoo
refuses unlink of ever-posted moves (cancel is the remediation primitive); RPC
AttributeError on onboarding actions (shell works).

## 3. Open shortcomings (candidates for v2 or explicit acceptance)

- a2 duplicate-vendor-bill anomaly generator returns silently — diagnose or replace.
- Statement-line matching (~85% target) unproven at gate time; suspense clears with it.
- Employee master / payroll headcount: GL payroll is real; per-employee substrate waits
  for the HR wave (demand-gated, TSK-2a7357) — registry-first (`EMP-####`) when it comes.
- Multi-currency rate table is the company's own (correct per D539); no group
  consolidation entities yet.
- Machine RETIREMENT flow — operator-added, not yet generated even in the dry-run world;
  v2 chronology includes it natively (disposal + accumulated-depreciation writeback +
  loss/gain on sale).
- Cross-system projection (BC, SFDC) — the registry join keys are in place; projection
  order and per-system chronology replay belong in this plan's §4 (to be written).

## 4. (to be written at close-out) Build sequence · gate battery · living-data wiring ·
cross-system projection order · cost model · AMI/rebuild policy
