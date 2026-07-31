# Runbook — mfg-in world engine on Odoo (D537/D538)

**Purpose:** repeatable procedure + data-pointer map for the pilot source world engine. Expect several
iterations: each metric wave reveals data pointers the world doesn't yet emit, and we come back here.
**Authority:** DEC-731c15 (D537 pre-staging) · DEC-def930 (D538 master-data framework + Amendment 1 base engine).
**Code (bc-sdg, COMMITTED @060fbf4):** `tools/mfg-in-odoo/` — see its **README.md** for the file map, run
order and doctrine constraints. Scripts: `master_gen.py`, `setup_shell.py` (ORM via `odoo shell`), `seed.py`,
`coverage.py`, `verify/{verify_world,coa_coverage,verify_lines,rpc_read_proof}.py`, `infra/ec2-userdata.sh` ·
registry `data/profiles/mfg-in/master.json`.

> **✅ DRY-RUN COMPLETE (2026-07-30) — full 5-FY world built, all gates green, AMI baked.**
> The dry-run's real deliverable is `.claude/PLAN-odoo-pilot-v2-2026-07-30.md` (chronological rebuild).
> **World state:** 3 companies (BPI/SEW/KTL, MH/TN/KA ⇒ real intra-state CGST/SGST + inter-state IGST + import
> IGST). Full realism landed via probe→fix loop: statutory remittance (GSTR-3B rhythm), intercompany trade,
> advances, late fees, import SWIFT/FX charges, term loans + directors' loan + **cash credit** (112240) with
> seasonal utilization, capex as named-vendor bills, spares (SKF/Schaeffler) + quarterly AMC, **monthly payroll**
> (Indian statutory: gross + employer PF/ESI, TDS→20th, PF/ESI→15th via 112460, net→5th, Diwali bonus),
> volume rebates + rate-diff CNs + QA rejections + scrap sales, CRM pipeline (lost + open + journeys), purchase
> orders (PO→receipt→bill), and **15 planted anomalies** (`data/profiles/mfg-in/anomalies.json` = answer key).
> **AMI:** `ami-0de1ac3735186651f` (mfg-in-odoo-2026-07-30-5fy-dryrun). Supplementary accounts 211900/212000/
> 112240/112460 added via `setup_config.py`.
>
> **KNOWN SCAR TISSUE (why the pilot uses a CLEAN rebuild, not this AMI):** ~1,730 documents cancelled across
> three remediation waves (B2C ad-spend miscalibration, REV-chain bug, wrong-shaped wage accruals); CRM
> back-catalog timestamps compressed to build-day (Odoo owns create_date/date_closed — see PLAN §1). Good for
> reader-testing + demo; the pilot world is a one-command chronological rebuild from PLAN-v2.
>
> **§2 run order below is SUPERSEDED** — the actual pass sequence is: `setup_shell` → `setup_config` +
> `onboarding_shell` → `master_gen` → `seed` (funnel + PO) → `coverage` → `scenarios` → `ap_parity --only bank`
> → `bank_recon` → `anomalies` → gates (`verify/integrity` + `verify/benchmarks` + `verify/coa_coverage`).
> Module list: `account,l10n_in,crm,sale_management,stock,purchase`.
>
> **§4b coverage: 97% per company (85/87)** — far past the 70% target. Demand side unchanged (296 active
> finance MCVs, re-measured 2026-07-30); supply side now covers the high-demand core + most of the tail.

## 1. What core finance metrics actually need (measured 2026-07-29 from live `bc_platform_dev`)

Active MCVs by subfunction: general_ledger 61 · financial_reporting 57 · **accounts_receivable 41** ·
accounts_payable 28 · tax 21 · fixed_assets 21 · credit_and_collections 15 · fpa 12 · cash_flow_management 12 ·
treasury 11 · revenue_accounting 9 · billing 6. (Other functions are seed-stage — finance is the live corpus.)

**Entities bound (what the source must expose as objects):**

| Entity | MCVs | Odoo model | Status in world engine |
|---|---|---|---|
| GL Account | 46 | `account.account` | ✅ 83 accounts (l10n_in Indian CoA) |
| Customer Invoice | 41 | `account.move` (out_invoice) | ✅ seeded + posted |
| Supplier Invoice | 17 | `account.move` (in_invoice) | ✅ seeded + posted |
| Journal Entry / Line | 9 / 8 | `account.move` / `account.move.line` | ✅ materialized by Odoo posting |
| Tax Line | 5 | `account.move.line` (tax) | ✅ real GST (IGST/CGST/SGST) |
| Bank Account | 4 | `account.journal` (bank) + `account.bank.statement.line` | ⚠ statements seeded, **unreconciled** |
| Customer Invoice Line Item | 4 | `account.move.line` (product) | ✅ |
| Revenue Recognition Line | 4 | — | ❌ **gap** (needs deferred-revenue schedules) |
| Customer / Vendor Payment | 2 / 1 | `account.payment` | ✅ + invoice reconciliation |

**Characteristics bound (the field-level data pointers), by demand:**

| Data pointer | MCVs | Odoo source | Status |
|---|---|---|---|
| posting date | 65 | `account.move.date` | ✅ |
| balance date (as-of) | 50 | derived at read (open items) | ✅ real open items exist |
| closing balance | 28 | GL balance at date | ✅ derivable from move lines |
| gross amount | 26 | `amount_total` | ✅ |
| net movement | 16 | debit−credit | ✅ |
| clearing date | 9 | payment reconciliation date | ✅ |
| net payment term days | 6 | `invoice_payment_term_id` | ⚠ **registry has terms_days but partner terms not yet set in Odoo** |
| document number / type code | 6 / 6 | `name` / `move_type` | ✅ |
| due date | 6 | `invoice_date_due` | ✅ (from terms) |
| tax | 6 | tax lines | ✅ GST |
| document date | 4 | `invoice_date` | ✅ |
| payment / net / credit / debit amount | 3/3/2/2 | payment + line amounts | ✅ |
| discount | 2 | line discount | ❌ **gap** (no discounts generated) |
| revenue amount | 2 | sales account lines | ✅ |
| status | 2 | `state` / `payment_state` | ✅ |
| value date | 2 | statement line date | ✅ |
| credit limit | 1 | partner credit limit | ❌ **gap** |
| invoice receipt date | 1 | vendor bill receipt | ❌ **gap** |
| ordered / delivered quantity | 1 / 1 | `sale.order.line` qty | ⚠ ordered ✅, delivered ❌ (no stock moves) |
| clearance time | 1 | derived (clearing − posting) | ✅ |
| line number | 1 | line sequence | ✅ |

**Verdict:** the world engine already covers the **high-demand core** (dates, amounts, balances, clearing,
document identity, tax, status) — i.e. AR/AP/GL/financial-reporting are feedable today. Known gaps are all
**low-demand tail** and each is a small additive unit: partner payment terms (⚠ easy, do next), discounts,
credit limits, vendor invoice-receipt date, delivered quantity (needs `stock`), revenue-recognition schedules,
bank-rec matching.

## 2. Build procedure (ORDER IS LOAD-BEARING)

1. **Instance**: `aws ec2 start-instances --instance-ids <id>` (containers auto-start; re-read public IP — it changes).
2. **DB rebuild** (clean slate; deterministic so always safe):
   `docker stop odoo-odoo-1` → `docker exec odoo-db-1 psql -U odoo -d postgres -c 'DROP DATABASE IF EXISTS pilot;'`
   → `docker start` → `docker exec odoo-odoo-1 odoo -d pilot -i account,l10n_in,crm,sale_management --without-demo=all --db_host=db --db_user=odoo --db_password=<pw> --stop-after-init` → `docker restart`.
3. **`setup_shell.py`** (via `odoo shell`, NOT RPC — `res.company` cannot be created over RPC) — MUST run
   before any posting: 3 Indian entities (MH/TN/KA) / INR / FY-31-Mar / full GST addresses / per-company CoA / admin
   accounting groups. **Odoo cannot change company currency once journal entries exist.**
4. **`master_gen.py`** → registry (deterministic; validate GSTIN format locally before shipping).
5. **`seed.py --from-month 2021-04`** — funnel head only; Odoo materializes the rest. Run **on the instance**
   (localhost RPC ≈ 60 s/month vs ~10× slower cross-region). `nohup … &` + `seed.log`.
6. **Verify** (see §4), then **bake AMI** → **stop/terminate** (hibernate).

## 3. Traps already paid for (do not rediscover)

- **Odoo 17 RPC:** `create` returns a **list**; private `_create_invoices`/`_reverse_moves` are RPC-blocked (use
  the `sale.advance.payment.inv` wizard / direct `out_refund`); **XML-RPC cannot marshal `None`** in wizard
  responses → use **JSON-RPC**; `write` needs **two** positional args; nested `[[id]]` must be flattened but
  **never** flatten field lists.
- **l10n_in fidelity checks:** refuses to post without a **complete company address incl. State**
  (GST place-of-supply); **validates GSTIN** (15 chars `SS+PAN+entity+Z+check`).
- **Admin needs** `account.group_account_user` + `group_account_manager` for bank-statement work.
- **Partners can't be deleted** once referenced in accounting → rebuild the DB instead of cleaning up.
- **msys/AWS CLI:** `MSYS_NO_PATHCONV=1` (else `/dev/xvda` is mangled); `file://C:/…` for user-data.
- Changing the random stream can expose latent generator bugs (an empty `randint` range surfaced this way) —
  re-validate the registry after any generator edit.

## 4. Verification set (run after every seed)

Company currency/country/FY · invoice currency = INR · a sampled invoice's journal items **balance**
(dr = cr) and include a **GST tax line** · `payment_state` distribution ≈ dials (65% paid / 8% partial /
3% credit-memo / 2% disputed) · AR lines with `full_reconcile_id` > 0 · `account.bank.statement.line` count
> 0 · registry counts exactly **200 / 100 / 50**.

## 4b. CoA COVERAGE as the completeness test (iteration 2, operator-driven 2026-07-29)

**Principle:** completeness is measured against the **chart of accounts**, not against whatever the O2C flow
happens to touch. Measure with `verify/coa_coverage.py` (`account.move.line` read_group by `account_id` ÷ `account.account`).

| State | Coverage | Touched families |
|---|---|---|
| funnel-head seed only | **16%** (14/83) | AR/AP, sales, purchase, GST, bank/outstanding |
| + `coverage.py` (1 month) | **55%** (46/83) | + 26 expense, fixed assets + depreciation, prepaid/advances + amortisation, statutory liabilities, petty cash |

`coverage.py` is **CoA-driven**: reads the live chart, groups by `account_type`, posts plausible operational +
period-end journal activity per family (rotating the whole expense family, quarterly capex, monthly straight-line
depreciation, month-end accruals, prepaid amortisation, other income, petty-cash cycle). Additive, idempotent by
`COV-*` ref, balanced-by-assertion, posts through Odoo. It also provisions the **company bank account**
(`res.partner.bank`, HDFC + IFSC-style BIC) and links it to the bank journal — previously absent.

Why it matters for metrics: fixed_assets (21 MCVs), tax (21), cash_flow_management (12), treasury (11) and much
of financial_reporting (57) bind accounts the AR/AP flow never touches.

**Remaining untouched (~45%)** and their likely homes: 12 current liabilities + 9 current assets (more statutory /
deposit / advance variety), 7 income (product/service/export revenue split — needs more sale-line variety),
2 other income, 1 receivable (employee/other debtors), 1 cash, 1 equity (opening balance / retained earnings —
best done as an FY-open entry). Raise coverage by extending `coverage.py`'s per-family generators, not by
touching the O2C driver.

## 5. Iteration loop (the repeat process)

**The demand test comes first — do not build a world no metric asks for.** Before adding a module or a
master family, count the *live* demand. Measured 2026-07-30: **296 of 296 active MCVs are `finance`**;
BCF defines `Employee` and `Timesheet` but **both have 0 metric bindings**. On that evidence the `hr`
(HRMS) world was **considered and deferred** on 2026-07-30, same as `mrp` (MES) and OCA helpdesk (ITSM) —
see `TSK-2a7357`. Note finance does *not* need employees: finance metrics bind **GL accounts**, so
`coverage.py`'s salary/statutory accruals are legitimate GL-level facts with no employee dimension.
Trigger for any Tier-2 world = the first metric in that function reaching `active`. When one is built,
its master entities go into the **shared registry first** (`EMP-####` in `master.json`), never
Odoo-native — that is the D538 cross-system join key, and retrofitting it later breaks projection.

When a metric wave needs a pointer the world lacks: (a) add it to §1's table with its MCV demand count;
(b) decide the layer — registry (master attribute), driver (new funnel-head act), or a new Odoo module
(Tier-2 per D538 §3c); (c) extend + **prove on one month**; (d) re-seed forward (idempotent by `MFG-*` refs, so
catch-up is safe) or rebuild if the change is structural (e.g. new module altering the CoA); (e) re-run §4.

## 6. Claim boundary (standing)

Infra/data green ≠ pilot green. No SC/AC/OC/CC or metric work here (Track-C-gated, D524 hold). Registry IDs are
cross-system **join keys**, never platform identity. Vendor posting engine is the coherence gate — **no raw SQL**.
