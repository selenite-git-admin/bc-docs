---
metric: apex-platform-wide-readiness-walkthrough
metric_version: n/a
tenant: apex
source_system: n/a
work_type: read-only-diagnostic
session_uid: SES-594568
date: 2026-05-12
status: decision-pending
related_commits: []
related_tasks: []
related_adrs:
  - DEC-a17d0f
  - DEC-5017fe
  - DEC-d72560
  - DEC-69f09e
  - DEC-804874
  - DEC-ebf0b4
related_mwrs:
  - 2026-05-12-semantic-base-audit-SES-a223ea.md
  - 2026-05-12-semantic-definitions-authority-design-SES-a223ea.md
  - 2026-05-12-tier1-cf-certification-design-SES-a223ea.md
related_change_records:
  - CHG-28ab0c
repair_location: D
affected_boundary: metric_evaluation
foundation_gate: passed
---

# Apex Phase 0 readiness walkthrough — classification of bound-not-producing MCs

> **Read-only diagnostic.** No writes, no certification acts, no scripts authored. All data fetched via implemented service surfaces. The MWR proposes a recommendation; no implementation action is taken. Stops at the decision-pending line.

## 0. Purpose and stance

Apex is the demo tenant. The goal is **maximum genuinely working Apex metrics without shortcuts**. This walkthrough classifies the bound-not-producing Apex metric population through the SDA Phase 0 projections (shipped on bc-core@cb4b972 under the umbrella ADR DEC-a17d0f / D403) and the existing readiness/inspection services, so the operator can decide whether a tactical write slice is safe today or whether the next investment must be SDA Phase 1.

The walkthrough is **read-only by construction** — service-layer reads only, no `metric.snapshot` access, no direct DB, no scripts, no writer endpoints, no Phase 1, no DBCPs.

## 1. Current Apex readiness dial

Source: `devhub_readiness_dial(tenant='apex')` — computed 2026-05-12T05:55:38.353Z.

| Surface | Number |
|---|---|
| Catalog total MCs | 376 |
| Catalog chain-complete | 185 |
| Catalog formula-supported | 360 |
| Catalog ready (chain ∧ formula) | 175 |
| **Apex bound** | **160** |
| **Apex producing** | **46** |
| **Apex wouldProduceIfBound (strict per-formula-token, audit-clean unbound)** | **0** |

**Headline:** Apex has **114 bound-not-producing MCs** (160 − 46). There are **zero easy unbound wins** (wouldProduceIfBound = 0).

The 46 producing MCs are the current demo surface. Every additional MC beyond 46 requires touching the bound-not-producing population, all of which has ≥1 broken formula token.

### Chain status (D305 SSOT)

Source: `devhub_chain_status` — computed 2026-05-11.

| Pipeline level | MCs (of 376) | Vars (of 800) |
|---|---|---|
| L1 CF Registered | 376 (100.0%) | 800 (100.0%) |
| L2 CF→BF Mapped | 376 (100.0%) | 800 (100.0%) |
| L3 BF in Schema | 376 (100.0%) | 800 (100.0%) |
| L4 Source Mapped | 376 (100.0%) | 800 (100.0%) |
| L5 AC Covers | 375 (99.8%) | 798 (99.8%) |
| L6 Reader Bound | 375 (99.8%) | 798 (99.8%) |
| L7 In Catalog | 375 (99.8%) | 798 (99.8%) |

540 (MC × version) rows in `contract.chain_status`. 247 complete, 293 partial, 0 broken, 0 unlinked. All in `finance` function.

**L1–L7 looks "almost complete" by chain-status terms.** This is the gap to the L-node semantic verdict and the SDA Phase 0 verdicts — chain-status counts *whether the link exists*, not whether the link's *semantic content* is sound.

### L-node semantic verdicts

Source: `devhub_l_node_audit(verdict='red,yellow')` — returned **0 rows**.

Either no L-node verdicts have been computed recently, or no red/yellow verdicts exist. Phase 0 projections (below) confirm the semantic problems are widespread, so the empty L-node table is interpreted as **"verdicts not run recently"** rather than "no problems". The L-node gate is therefore **not informative** for this walkthrough.

## 2. Bound-not-producing classification

Per-MC enumeration of the 114 bound-not-producing Apex MCs requires `/api/admin/tenant-metrics/snapshot?tenant=apex` and `/api/registry/metric-readiness/mc-list?tenantId=apex`. Both returned **401 Unauthorized** under the platform_admin Cognito JWT used for this session, despite the same token successfully calling `/api/admin/readiness/tenant/apex/binding-candidates` and the entire `/api/semantic-definitions/projections/*` surface.

**Probable cause:** the `@Roles('platform_admin')` decorator on `MetricReadinessController` and the `@PlatformOnly()` guard on `TenantMetricsController` interact with the token's role-claim shape differently from the SDA controller (which is `@PlatformOnly()` only). The token carries `custom:roles` as a JSON-string array `["platform_admin","schema_author","operator","analyst"]` — the roles guard may parse this differently from the scope guard. Out of scope for this walkthrough.

**Data substitute used:** `devhub_formula_token_audit(tenant='apex')` returns per-token classification across all 376 MCs and the same numbers can be aggregated by reason — this is the authoritative source the dial itself derives from.

### Formula-token audit — platform-wide, with subfunction breakdown

Source: `devhub_formula_token_audit(tenant='apex', top_n_broken_cfs=30)` — computed 2026-05-12T05:56:06.402Z.

**Totals:** 376 MCs · clean=38 · broken=338 · skipped=0.

The 38 clean MCs are platform-wide; the 46 producing Apex MCs include those 38 plus 8 more that produce despite formula-token issues (likely output-only or computed-from-snapshot patterns).

**Broken-token reason breakdown (532 total broken tokens across 338 MCs):**

| Reason | Tokens | Category |
|---|---|---|
| `null_in_tenant` (upstream source-data emission gap) | 396 | **reader-coverage candidate** |
| `type_mismatch` (cc_field_mapping points at wrong-type BF) | 134 | **mapping-source gap** |
| `no_mapping` (CF unmapped on any bound CC) | 2 | **clean service-repairable** |

**By subfunction (top 10 by broken-MC count):**

| Subfunction | Total | Clean | Broken |
|---|---|---|---|
| finance/accounts_payable | 76 | 2 | 74 |
| finance/general_finance | 58 | 7 | 51 |
| finance/revenue_accounting | 43 | 12 | 31 |
| finance/general_ledger | 36 | 2 | 34 |
| finance/treasury | 30 | 2 | 28 |
| finance/tax | 23 | 0 | 23 |
| finance/accounts_receivable | 22 | 3 | 19 |
| finance/fpa | 16 | 2 | 14 |
| finance/capital_structure_optimization | 14 | 1 | 13 |
| finance/fixed_assets | 11 | 2 | 9 |

`revenue_accounting` is the only subfunction with >10 clean MCs. `accounts_receivable` (the recurring pilot surface, per memory's "sandbox1 AR pilot ceiling locked at 14/31") has 3 clean of 22.

## 3. SDA Phase 0 projection findings (the semantic floor)

All counts platform-wide, not Apex-filtered (Apex shares the platform contract layer).

### Certification state

Source: `GET /api/semantic-definitions/projections/certification-state` — 10,361 primitive rows.

| Primitive | Total | Projected state | Provenance | semantic_family (CF only) |
|---|---|---|---|---|
| canonical_field | 3,097 | 100% `proposed` | 0 have provenance | 0 have semantic_family |
| business_field | 7,062 | 100% `proposed` | 0 have provenance | — |
| business_object | 202 | 100% `proposed` | 0 have provenance | — |

- 1,527 CFs (49%) are referenced by ≥1 `cc_field_mapping` row.
- 196 CFs (6.3%) fail P3 profile compliance.

**Every primitive is in `proposed` (the projected name for the historical `draft` status).** No certification has occurred via the SDA path (Phase 1 not shipped). G4 (provenance) and G5 (semantic_family) are universally failing.

### Profile violations (G1)

Source: `GET /api/semantic-definitions/projections/profile-violations` — 6,007 violation rows.

| Profile | Violation rows | Notable failures |
|---|---|---|
| **P2** (BF — BO-scoped snake_case) | 2,714 | `not_bo_scoped: 2685`; `uses_bo_prefix:asset/credit/invoice_line/personnel: 76` |
| **P3** (CF — non-BO-scoped snake_case) | 196 | `not_snake_case: 69`; `exceeds_max_length_64: 995` (note: length failures are counted as P3 here) |
| **P5** (semantic_family enum) | 3,097 | `null_semantic_family: 3097` (every CF) |

- 69 CFs with non-snake_case names (e.g. `Employee Training in New Tech`, `On-time Payment Rate`).
- 995 CFs over the 64-char length cap.
- 2,685 BFs not BO-scoped (D292 violation).

### Meaning-once collisions (G10) — the smoking gun

Source: `GET /api/semantic-definitions/projections/meaning-once-candidates` — **144 collision groups**.

Top collision groups (each row = one signature with N distinct CFs all resolving through it):

| # | Canonical signature | Colliding CF count |
|---|---|---|
| 1 | `cc__actual_ledger.actual_ledger_amount` (sum) | **281** |
| 2 | `cc__invoice_hdr.invoice_hdr_total_amount` (sum) | 78 |
| 3 | `cc__bc_financial_risk_management_operations.bc_financial_risk_management_ops_total_auditable_operations_scope` (sum) | 53 |
| 4 | `cc__receivable_hdr.receivable_hdr_amount` (sum) | 49 |
| 5 | `cc__commercial_invoice_hdr.commercial_invoice_hdr_total_tax_amount` (sum) | 44 |
| 6 | `cc__project_accounting.project_accounting_project_actual_cost_amount` (sum) | 39 |
| 7 | `cc__bc_gl_operations.bc_gl_ops_number_of_standard_accounts` (count_distinct) | 37 |
| 8 | `cc__actual_ledger.actual_ledger_amount` (latest) | 37 |
| 9 | `cc__invoice_hdr.invoice_hdr_extended_amount` (sum) | 30 |
| 10 | `cc__gaap_income_statement.gaap_income_gross_profit` (sum) | 26 |

**281 distinct CFs — including `net_income`, `recognized_revenue`, `billed_revenue`, `accounts_payable_balance`, `cost_of_goods_sold` — all resolve through the same `cc__actual_ledger.actual_ledger_amount sum` signature.** Under SDA G10 Class-A (non-overridable, Sev-1), once any one of these CFs is certified, the remaining 280 cannot be certified through the same signature without (a) distinguishing filter_json / compute_json, (b) targeting the existing CF and deprecating the candidate, or (c) deprecating the existing and superseding.

This is **the funnel-padding pattern named in memory `feedback_funnel_padding.md` made concrete in data**. It is the structural form of "81 CFs = 1 NETWR sum is semantic noise, not progress" from sandbox1.

### Stale cc_field_mapping references

Source: `GET /api/semantic-definitions/projections/stale-cc-field-mapping-references` — **1,659 stale rows**, all with reason `target_cf_not_certified_or_deprecated` (since 0 CFs are certified, every mapping row is stale by this projection).

Top CCs by stale-ref count: `cc__actual_ledger` (385), `cc__bc_financial_risk_management_operations` (176), `cc__bc_ap_operations` (156), `cc__invoice_hdr` (152), `cc__receivable_hdr` (118), `cc__bc_gl_operations` (113), `cc__asset` (101), `cc__bc_internal_audit_operations` (63), `cc__commercial_invoice_hdr` (56), `cc__journal_entry_hdr` (44).

These are the same CCs that dominate the G10 collision list — the funnel-padding and the staleness are the same phenomenon viewed from two projections.

### Duplicate name clusters (G2b)

Source: `GET /api/semantic-definitions/projections/duplicate-name-clusters` — **4 clusters**, all `normalized_form`, 0 `exact_identity` (consistent with the live unique-index diagnostic). Examples: `on_time_payment_rate` / `On-time Payment Rate`; `total_number_of_tax_processes` / `Total Number of Tax Processes`; `early_payment_discount_capture_rate` / a Title-Case sibling.

Only 4 clusters surface here because Phase 0's G2b is conservative (exact normalized match). The real Title-Case violation count is 69 (per profile-violations P3 / `not_snake_case`).

### Unique-index diagnostic

Source: `GET /api/semantic-definitions/diagnostics/unique-index-state` — **clean.** Live DB enforces strict single-column uniqueness on `contract.canonical_field(field_name)` via `canonical_field_field_name_key`. 0 exact-byte duplicates. Drizzle-declared name `uq_canonical_field__name` is index-name drift only, not a missing constraint. SDA ADR §C3 verification confirmed.

## 4. Cross-reference: top broken Apex CFs vs G10 collision groups

For each of the top 20 broken Apex CFs (by `null_in_tenant + type_mismatch` count), the collision-group membership in G10:

| Broken Apex CF | Broken-token count | G10 collision-group membership |
|---|---|---|
| `operating_cash_flow` | 11 | in group of **19** via `cc__gaap_cash_flow.gaap_cashflow_operating_net (sum)` |
| `total_payments_count` | 7 | in group of **78** via `cc__invoice_hdr.invoice_hdr_total_amount (sum)`; also group of 3 |
| `total_invoice_line_items_count` | 6 | in groups of 9 and 7 |
| `total_invoices_processed_count` | 5 | in group of **78** + group of 6 |
| `total_journal_entry_line_items` | 5 | in group of 2 |
| `total_debt` | 5 | in group of **53** + group of **44** |
| `total_invoice_line_items` | 4 | in group of 4 |
| `average_total_assets` | 4 | in group of 15 via `cc__actual_ledger.actual_ledger_fiscal_year (latest)` |
| `total_finance_function_it_costs` | 4 | in group of **21** |
| `total_company_revenue` | 4 | in group of **78** via `cc__invoice_hdr.invoice_hdr_total_amount (sum)` |
| `total_current_liabilities` | 4 | in group of **53** + group of **44** + group of 19 |
| `total_invoices_processed` | 3 | in group of **78** + group of 6 |
| `reporting_period_in_months` | 3 | in group of 17 + group of 3 |
| `total_supplier_invoices_received` | 3 | in group of **78** + group of 4 |
| `total_variable_costs` | 3 | in group of **39** |
| `average_inventory_value` | 3 | **NOT in any collision group** |
| `total_current_assets` | 3 | in group of **53** + group of **44** |
| `pre_tax_income` | 3 | in group of 17 |
| `total_number_of_tax_processes` | 3 | in group of 8 |
| `current_liabilities` | 3 | **NOT in any collision group** |

**18 of 20 top broken Apex CFs sit inside a G10 collision group.** The two exceptions (`average_inventory_value`, `current_liabilities`) are pure `null_in_tenant` cases — upstream emission gap, not semantic collision.

The top three biggest collision groups (281, 78, 53 colliders) account for the bulk of Apex's broken token surface. Each represents a *single source-field semantic* (e.g. `invoice_hdr_total_amount sum`) being declared as the resolution of many distinct business CFs — e.g. `total_company_revenue`, `total_payments_count`, `total_invoices_processed`, `total_invoices_processed_count`, `total_supplier_invoices_received` are five *materially different* Apex business concepts all resolving through the same source aggregation.

This is not a "tenant data is missing" problem. It is a **contract semantics** problem.

## 5. Per-MC classification (114 bound-not-producing Apex MCs)

Without the per-MC name list (blocked by §2 401), classification is by *token-reason × collision-group* and is necessarily approximate. The reasons-to-categories mapping uses the seven categories the operator named.

| Category | Token volume | Estimated MC share | Notes |
|---|---|---|---|
| **A. Clean service-repairable** | 2 `no_mapping` tokens | ≤2 MCs | Truly trivial: CF exists, just unmapped to any bound CC. Service-call to add a mapping. **Risk: which CC the new mapping should target is a G10 question** — if the target signature is already shared by ≥1 other CF, the "fix" reproduces the funnel-padding pattern. Safe only when target signature is unique. |
| **B. Reader-coverage candidate** | ~150 `null_in_tenant` tokens **NOT in any G10 collision group** (estimated as the share where collision-group membership is empty or count = 1) | ~30–40 MCs | Upstream source-data emission gap; the AC/SC/reader doesn't emit this BF for Apex's bound CCs. Phase 0 cannot distinguish reader-coverage gaps from CC field_selection misses cleanly — needs per-MC chain-detail inspection (§2 blocker). |
| **C. Mapping-source gap** | ~134 `type_mismatch` tokens | ~50–60 MCs | `cc_field_mapping` points at wrong-type BF. But: when ≥5 CFs already collide on a signature (G10), "wrong type" is symptomatic of funnel-padding (multiple semantics squeezed onto one BF). True type-mismatch fixes are only safe in clusters where collision count = 1. |
| **D. MC envelope / role issue** | Subset of `type_mismatch` where role-shape mismatch (input vs derived) | Unknown without per-MC inspection | The 8-MC gap between formula-clean (38) and Apex producing (46) suggests some MCs produce despite formula-token issues — derived/output-only roles work around the gates. Conversely, role-misdeclarations can cause clean tokens to not produce. |
| **E. Shell-CC / ADR-grade cluster** | The 281-CF, 78-CF, 53-CF, 49-CF, 44-CF collision groups | **Most of the broken population** | The four largest G10 collision groups touch ~505 CFs across ~144 MCs platform-wide. Any Apex MC whose variables include even one CF in these groups is semantically blocked until either (i) the SDA G10 Class-A path resolves the collision via distinguishing filter/compute or supersession, or (ii) the cluster is declared ADR-grade and a per-cluster decision splits the survivors. **This is the dominant category.** |
| **F. Grammar / balance-flow deferred** | Some `null_in_tenant` cases where the CF semantic requires a temporal pattern the MC engine doesn't yet express (e.g. as-of balance, trailing window — the D210 / SES-f10b35 pattern from memory) | Unknown without per-MC inspection | Deferred until MC grammar extends; not a Phase-0-fixable category. |
| **G. Blocked by SDA semantic-risk finding** | All MCs whose CF semantic is null (every CF has `null_semantic_family`) | All 376 MCs technically | G5 is hard-law non-overridable. **No MC can reach genuine SDA `certified` state without semantic_family populated** (SDA G5). Today this is invisible because no MC is certified-or-not — they all sit in `proposed`. Once Phase 1 ships and the certification gate runs, this becomes a structural blocker for every MC that touches an uncertified CF (which is all of them). |

**The 7-category sum is not a clean partition.** Most bound-not-producing Apex MCs sit in **multiple categories simultaneously** — e.g. an AP MC whose `total_invoices_processed` variable is in the 78-CF collision group AND is null_in_tenant AND would fail G5 once certification gate runs. Tactical repair of any one dimension does not unblock the MC if other dimensions remain.

## 6. Top 5 candidate ranking — by category, not by MC

Without per-MC names, ranking individual MCs is not possible from this walkthrough. The honest ranking is **by category** with explicit risk per candidate:

| # | Candidate slice | Demo value | Semantic cleanliness | Repair surface | Expected uplift | Risk | Recommendation |
|---|---|---|---|---|---|---|---|
| 1 | **The 2 `no_mapping` MCs, where target CC signature has collision count = 1** | Low (2 MCs) | High (signature unique) | Single `cc_field_mapping` insert per MC | +0 to +2 producing Apex MCs | **Low-Medium** — needs verification the target signature is unique-among-`certified`-intent; if any colliding CF is in the target signature, the "fix" is funnel-padding | **Inspect first.** Cannot recommend without identifying the 2 MCs and their target signatures. |
| 2 | **Reader-coverage candidates where the CF is NOT in any G10 group** (e.g. `average_inventory_value`, `current_liabilities`) | Low-Medium (covers a handful of MCs each) | High (no collision) | Reader / AC / OC field_selection extension — requires SC mapping if the source field isn't admitted | +1 to +5 producing Apex MCs per CF unblocked | **Medium** — depends on whether the source emits the field; if not, escalates to SC/AC contract work | **Inspect first.** Defensible if reader gap is genuinely coverage, not semantic ambiguity. |
| 3 | **Revenue-accounting subfunction MCs in the 78-CF `cc__invoice_hdr.invoice_hdr_total_amount sum` collision group** — pick one survivor (e.g. `total_company_revenue`), supersede the others off this signature | Medium-High (revenue is a demo headline) | Requires SDA Phase 1+ supersession; today none of the candidates are certified, so it's pre-certification cleanup | One signature, ~78 CFs to triage per per-cluster review | +0 producing today (cannot enforce); foundation for ≥5 demo-grade AR/RA metrics later | **High** — risks repeating the funnel-padding pattern if survivor selection lacks a governing-source review per cluster | **Defer.** Requires SDA Phase 1 (G10 enforcement) + per-cluster ADR-grade decision. |
| 4 | **AP subfunction collision group: `cc__bc_ap_operations.*`** (multiple groups of 6, 9, 3 colliders) | Medium (AP is a recurring demo subfunction) | Requires per-cluster review; smaller groups are more tractable than the 78/53/49 monsters | Multiple small clusters; each needs governing-source review | Unknown without enumeration; potentially 5-10 MCs | **Medium-High** — same risk as #3, smaller blast radius | **Defer.** Same as #3. |
| 5 | **The 8-MC gap between formula-clean platform (38) and Apex producing (46)** — understand why these 8 produce despite formula-token issues; this reveals which derived/output-only patterns are safely Apex-bound today | Medium (audit/proof artifact) | Read-only inspection | Per-MC inspection on 8 MCs | +0 (already producing); evidence for future tactical work | **Low** | **Inspect when per-MC list becomes accessible.** Free intelligence about the engine's tolerance for incomplete chains. |

**No candidate above is a "ship today" candidate.** The two low-risk slices (#1, #2) require per-MC identification that this walkthrough could not obtain (auth-guard blocker). The three medium-to-high-risk slices (#3, #4) are explicitly SDA Phase 1+ territory.

## 7. Stop conditions encountered

Per the operator's stop conditions (CLAUDE.md Foundation Invariant Check + D268 Rule 7):

| Stop condition | Triggered | Action taken |
|---|---|---|
| **Doc / data conflicts** | C3 verification: the SDA design's earlier concern about CF unique-index drift is **resolved** — Phase 0 diagnostic confirms strict single-column uniqueness via `canonical_field_field_name_key`, 0 exact duplicates. Drizzle name drift is cosmetic only. No new conflict surfaced. | Noted; no action required. |
| **Implementation drift found** | Two diagnostic surfaces (`/api/admin/tenant-metrics/snapshot`, `/api/registry/metric-readiness/*`) returned 401 under a JWT that successfully authorised every other admin surface called in this session, including SDA projections and readiness/binding-candidates. Likely a `@Roles('platform_admin')` vs `@PlatformOnly()` guard interaction with the role-claim shape. | **Flagged as a gap.** Out of scope for this walkthrough; should be diagnosed separately (TSK candidate: `qa-shift-left` / auth-guard consistency). The walkthrough proceeded using formula-token-audit + SDA projections as the data substitute. |
| **DB write or tenant action required** | None. All operations were service-layer reads. No DBCP needed. No tenant/runtime touch. | None. |
| **Funnel-padding temptation** | The 281-CF / 78-CF / 53-CF G10 collision groups are textbook funnel-padding. Any path that "fixes" Apex demo MCs by repointing CFs at shared source signatures would compound the pattern. | **Refused at the design layer.** No candidate recommendation in §6 takes this shortcut. |
| **Semantic collapse** | Top broken Apex CFs (revenue, payments, debt, liabilities, assets — all materially distinct concepts) are already collapsed onto the same source signatures in the platform contract layer. This is **pre-existing semantic collapse**, not a current-session-introduced one. | **Flagged.** No action this slice — Phase 1+ SDA G10 enforcement is the structural response per DEC-a17d0f §4. |
| **Shortcut greenification** | The temptation to bind more catalog-clean MCs to Apex is structurally pre-empted: `wouldProduceIfBound = 0`. There are no audit-clean unbound MCs whose CCs have COs in Apex. | None — the data prevents the shortcut. |
| **Foundation invariant violation** | None proposed. Diagnostic only. | None. |

## 8. Recommendation — one next governed write slice, or no safe slice

### Verdict

**No write slice is safe today.** The data does not support a defensible "ship N more Apex MCs without SDA Phase 1" tactical path. Specifically:

1. **`wouldProduceIfBound = 0`** — there are zero audit-clean unbound MCs to bind. The 46 producing MCs are already producing; the 114 bound-not-producing are blocked by upstream issues.
2. **18 of the top 20 broken Apex CFs sit inside G10 collision groups** of 4 to 78 colliders. Any "tactical fix" that repoints a colliding CF, or adds a new mapping into a shared signature, **is funnel-padding by definition**.
3. **All 3,097 CFs are missing `semantic_family` (G5 hard-law) and provenance (G4)**. Even the trivial `no_mapping` (n=2) and "not-in-any-collision-group" reader-coverage candidates (e.g. `average_inventory_value`, `current_liabilities`) cannot pass SDA G5 until semantic_family is populated. Today this is invisible because Phase 1 enforcement isn't running — but writing today bakes in primitives that will fail enforcement tomorrow.
4. **Two of the three lowest-risk candidate slices** (the 2 `no_mapping` MCs; the 2 not-in-collision-group reader candidates) **cannot be identified without resolving the 401 auth-guard issue** on the readiness/tenant-metrics surfaces. Without per-MC identification, recommending a write is shooting in the dark.

### What the next session should do instead

Three options, in order of preference:

| Option | Scope | Effort | Risk | When |
|---|---|---|---|---|
| **A. Resolve the readiness/tenant-metrics 401 + re-run §6 with per-MC names** | Diagnose the `@Roles('platform_admin')` guard auth-shape; re-fetch bound-not-producing list with named MCs; recompute §6 candidates with collision-group membership per MC variable | 1 short session, read-only | Low | Recommended next |
| **B. Per-cluster governing-source review of the top G10 collision groups** | Take the 281-CF / 78-CF / 53-CF / 49-CF / 44-CF groups; for each, governing-source review (which Apex business concepts are genuinely distinct vs aliases vs duplicates); produce a per-cluster ADR-grade MWR | 1 session per cluster, paper-only | Medium (requires SDA Phase 1 to act on findings) | After A, in parallel with C |
| **C. SDA Phase 1 DBCP-1a only — author the `master.semantic_family` master table DBCP** | Smallest Phase 1 DBCP; additive new table; doesn't touch any existing primitive; unlocks G5 evaluation in subsequent Phase 1 DBCPs | 1 session, DBCP draft only (no execution) | Low (additive) | After A, when operator approves entering Phase 1 |

**Recommendation:** start with **Option A** — diagnose the 401 and re-run §6 with named MCs. The per-MC data is the difference between speculation and a defensible candidate ledger.

If Option A confirms <3 truly-safe candidates (i.e. CFs not in any collision group, with reader-coverage gap as the only blocker, AND target signature is unique), then **the structurally correct next investment is SDA Phase 1**, starting with DBCP-1a (Option C).

If Option A surfaces ≥5 truly-safe candidates, a small per-cluster repair MWR (with explicit one-then-many discipline per D268) becomes safe.

### What this walkthrough explicitly does not do

- No certification acts.
- No `cc_field_mapping` writes.
- No reader / AC / SC changes.
- No tenant binding changes.
- No DBCP authored.
- No SDA Phase 1 work begun.
- No ADR authored.
- No script committed.
- No tenant/runtime touch.

The MWR's job is to put real data in front of the operator. The decision on which option to pursue next is the operator's.

## 9. Evidence (sources used)

| Source | Used for | Computed |
|---|---|---|
| `devhub_readiness_dial(tenant='apex')` | §1 dial: 160 bound / 46 producing / 0 wouldProduceIfBound | 2026-05-12T05:55:38.353Z |
| `devhub_chain_status` | §1 pipeline L1-L7 | 2026-05-11 05:31:17 |
| `devhub_formula_token_audit(tenant='apex', top_n_broken_cfs=30)` | §2 token-reason breakdown, top 30 broken CFs, subfunction yield | 2026-05-12T05:56:06.402Z |
| `devhub_l_node_audit(verdict='red,yellow')` | §1 L-node verdicts (returned 0 rows) | 2026-05-12 |
| `GET /api/semantic-definitions/projections/certification-state` | §3 primitive counts; provenance / semantic_family coverage | 2026-05-12 |
| `GET /api/semantic-definitions/projections/meaning-once-candidates` | §3 144 collision groups; top-10 worst by colliding-count; cross-ref to top broken Apex CFs (§4) | 2026-05-12 |
| `GET /api/semantic-definitions/projections/duplicate-name-clusters` | §3 G2b 4-cluster set | 2026-05-12 |
| `GET /api/semantic-definitions/projections/profile-violations` | §3 P2/P3/P5 violation totals | 2026-05-12 |
| `GET /api/semantic-definitions/projections/stale-cc-field-mapping-references` | §3 1,659 stale rows; top-10 CCs by stale-ref count | 2026-05-12 |
| `GET /api/semantic-definitions/diagnostics/unique-index-state` | §3 unique-index live state (resolves SDA ADR §C3) | 2026-05-12T05:59:54.915Z |
| `GET /api/admin/readiness/tenant/apex/binding-candidates` | Cross-check (returned count=0 — consistent with dial wouldProduceIfBound=0) | 2026-05-12T05:57:14.446Z |
| (Blocked) `GET /api/admin/tenant-metrics/snapshot?tenant=apex` | Would have provided per-MC named list with named blockers; **returned 401** | n/a |
| (Blocked) `GET /api/registry/metric-readiness/mc-list?tenantId=apex` | Would have provided per-(tenant × MC) gate-list; **returned 401** | n/a |

## 10. State of play

- **DEC-a17d0f / D403 (SDA umbrella ADR) is filed and pushed.** Phase 0 read-only projections are live on bc-core@cb4b972 and demonstrably useful as the diagnostic surface used in this walkthrough.
- **Apex's 46/160 producing ratio is constrained by platform-layer semantic collapse**, not by Apex tenant data alone. The 281/78/53/49/44 G10 collision groups are pre-existing and structural.
- **The cheapest next move** is resolving the readiness/tenant-metrics 401 to get the per-MC list (Option A above). That single step converts the §6 ranking from category-level to MC-level and enables defensible per-MC decisions.
- **No write is recommended this session.** The walkthrough stops here.

## 11. Closing note

The SDA Phase 0 projections are doing exactly what they were designed to do — make the semantic floor visible without writing anything. The picture they paint is sobering: there is no shortcut path to "Apex producing more demo metrics" that doesn't go through either (a) SDA Phase 1 enforcement against the G10 collision groups, or (b) explicit per-cluster ADR-grade decisions on which survivors keep which signatures. The 46/160 dial is not a tactical gap; it is a structural artifact of pre-SDA contract authoring.

The operator's instinct to ask for "data before more paper" was correct. The data now answers the question the strategic plan could only speculate about.

---

# Addendum (Option A — named candidate ledger) — 2026-05-12 PM

> **Update to §2, §5, §6, §8.** Per operator counter-proposal: diagnose the 401 on the readiness / tenant-metrics surfaces, then re-run the Apex classification with named MCs. All scanning remains read-only, service-layer. Per operator interpretation: missing `semantic_family` / provenance is treated as SDA semantic-risk evidence, not as a runtime hard blocker. Runtime hard blockers in this addendum are **G10 collision membership, fiscal-year / non-sense source mappings, D335-R4 SUM-on-latest, and missing CF→BF mappings**.

## A1. Auth diagnosis — the 401 was transient

The 401 documented in §2 and §7 of the original walkthrough is **resolved without code change**. Re-probing the same endpoints with the same platform_admin Cognito JWT now returns 200:

| Endpoint | Previous | Now |
|---|---|---|
| `GET /api/admin/tenant-metrics/tenants` | 401 | 200 |
| `GET /api/admin/tenant-metrics/snapshot?tenant=apex` | 401 | 200 |
| `GET /api/registry/metric-readiness/funnel?tenantId=apex` | 401 | 200 |
| `GET /api/registry/metric-readiness/orphan-contracts` | 401 | 200 |
| `GET /api/registry/metric-readiness/chain-detail/:mcId` | (not tried) | 200 |

**Root-cause attribution.** Source inspection confirmed:

- `MetricReadinessController` is decorated `@Roles('platform_admin')` (`metric-readiness.controller.ts:17`).
- `TenantMetricsController` is decorated `@PlatformOnly()` (`tenant-metrics.controller.ts:18`).
- `ScopeGuard` throws `ForbiddenException` (403), not 401, on scope mismatch (`scope.guard.ts:43-47`).
- `RolesGuard` returns `false` on no-user, NestJS converts to 403 — also not 401 (`roles.guard.ts:32`).
- A 401 from these routes therefore originates at the upstream `JwtAuthGuard` (Passport `cognito-jwt`), not at the role/scope layer.

The same JWT validates fine now. Likely causes for the earlier transient rejection: (a) NestJS hot-reload from the prior session's edits caused a brief window where the Passport strategy reloaded with stale JWKS cache and rejected mid-window tokens; (b) JWKS rate-limit hit (`jwksRequestsPerMinute: 5` per `cognito-jwt.strategy.ts:54`) during rapid probing; (c) a token clock-skew edge case at first-mint.

**No code change recommended.** Smallest safe fix if recurrence becomes a pattern: bump `jwksRequestsPerMinute` from 5 to 10, or pre-warm the JWKS cache on app boot. Both are 1-line changes in `cognito-jwt.strategy.ts`. Filing this as a known transient is sufficient unless operator deems otherwise.

## A2. Corrected Apex totals (from `/api/admin/tenant-metrics/snapshot?tenant=apex`)

```
totals: {
  tenantsCount:           1,
  boundMcsCount:          296,    // raw (tenant × MC × version) rows
  activeBindingsRawCount: 296,
  tenantReadyCount:       160,    // platform-ready MCs bound to Apex
  tenantEvaluatedCount:   53,
  liveCount:              46,
  producingMcsCount:      46,
  staleBindingsCount:     136     // binding present but MC not platform-ready
}
```

**Corrected classification of the 250 bound-not-producing rows (296 − 46):**

| Stage | Last evaluation status | Count | Meaning |
|---|---|---|---|
| `stale_binding` | `rejected` | 82 | MC not platform-ready; dispatcher already rejected. **Not Apex-tactical.** |
| `stale_binding` | `never` | 54 | MC not platform-ready; never invoked. **Not Apex-tactical.** |
| `tenant_ready` | `rejected` | 71 | MC platform-ready, evaluation invoked and rejected. **Dispatch_gap candidates.** |
| `tenant_ready` | `never` | 36 | MC platform-ready, never invoked. **Dispatch_gap candidates.** |
| `tenant_evaluated` | `accepted` | 7 | Evaluation succeeded, but no `metric_snapshot_index` linkage. **Closest to producing.** |

**The Apex-tactical surface is 114 MCs** (107 `tenant_ready/dispatch_gap` + 7 `tenant_evaluated/accepted`). The 136 `stale_binding` rows are upstream-MC-broken; their repair is platform contract work, not Apex tactical.

## A3. The 7 closest-to-producing MCs — named, with chain detail

All seven have `chainVerdict: complete`, evaluation accepted, but no snapshot index linkage (blocker: "data freshness gap"). Per-MC chain-detail (variables, traces, audit findings, source field):

| # | MC | Subfunction | Formula | Audit | Findings | Inputs → source |
|---|---|---|---|---|---|---|
| 1 | `mc__days_sales_outstanding` | accounts_receivable | `O1 = (SUM(I1) / SUM(I2)) * I3` | warn | none | `accounts_receivable_balance` → BSID.WRBTR (49-collision); `total_credit_sales` → TYPE_SD_S_MAP.NETWR (30-collision) |
| 2 | `mc__roa_return_on_assets` | capital_structure_optimization | `O1 = (SUM(I1) / SUM(I2)) * C1` | warn | **D335_SUM_ON_LATEST** on I2 | `net_income` → cc__actual_ledger (281-collision); `average_total_assets` → **BKPF.GJAHR** (fiscal year — nonsense) |
| 3 | `mc__return_on_assets_roa` | fixed_assets | same as #2 | warn | **D335_SUM_ON_LATEST** on I2 | duplicate of #2 (different MC, same semantics) |
| 4 | `mc__accounts_payable_turnover_ratio` | general_ledger | `O1 = SUM(I1) / SUM(I2)` | pass | **D335_SUM_ON_LATEST** on I2 | `cost_of_goods_sold` → cc__actual_ledger (281-collision); `average_accounts_payable` → **FAGLPOSE.GJAHR** (fiscal year — nonsense) |
| 5 | `mc__complete_the_monthly_consolidated_financial_statements` | general_ledger | `O1 = SUM(I1)` | pass | **D335_SUM_ON_LATEST** on I1 | `days_to_consolidated_statements` → **BKPF.GJAHR** (fiscal year — nonsense for a "days to complete" metric) |
| 6 | `mc__net_working_capital_ratio` | treasury | `O1 = (SUM(I1) / SUM(I2)) * C1` | warn | none | `net_working_capital` → actual_ledger_amount **computed** source; `annual_revenue` → FAGLPOSE.WRBTR (281-collision) |
| 7 | `mc__working_capital_as_of_revenue` | treasury | same as #6 | warn | none | duplicate of #6 (different MC, same semantics) |

**Findings:**

- **All 7 land at least one input on the 281-CF (`cc__actual_ledger.actual_ledger_amount sum`), 49-CF (`cc__receivable_hdr.receivable_hdr_amount sum`), 30-CF (`cc__invoice_hdr.invoice_hdr_extended_amount sum`), or fiscal-year-as-source.** None has a clean signature.
- **4 of 7 carry an explicit D335-R4 finding** — formula uses `SUM()` but `cc_field_mapping.resolution_rule_code = 'latest'`. The evaluation succeeded because the engine took the "latest" value, but the metric semantic is wrong — averaging or summing a fiscal-year code is not a real number.
- **MCs #2/#3 and #6/#7 are duplicate pairs** — same formula and same input CFs, registered as separate MCs in different subfunctions. This is its own funnel-padding pattern (same metric registered twice).
- **MC #5 maps "days to complete consolidated statements" to GJAHR (a fiscal year code).** That cannot produce a defensible business value. It would produce numbers, but the numbers would be unrelated to the metric's stated meaning.

**None of the 7 is a safe write candidate.** Removing the snapshot-index linkage blocker would make them produce *wrong numbers*, not *demo-grade results*. The data-freshness gap is a benevolent firewall against the broken upstream mappings.

## A4. Full scan of the 114 non-stale candidates

Method: `GET /api/registry/metric-readiness/chain-detail/:mcId` for every one of the 114; cross-reference each input CF's name against the G10 meaning-once-candidates projection to compute `maxCollisionSize` (largest collision group the CF participates in). All 114 were successfully scanned.

### Aggregate cleanliness counts

| Cleanliness criterion | Count of 114 |
|---|---|
| Formula `auditStatus == 'pass'` AND `findings == []` | **31** |
| No input mapped to a fiscal-year source field (GJAHR or `*fiscal_year` BF) | **100** |
| At least one input has worst-collision-group size ≤ 1 (truly unique signature) | **1** |
| All inputs have worst-collision-group size ≤ 5 | **8** |
| **All of: audit pass + no findings + no fiscal_year source + all inputs collision ≤ 5** | **0** |
| **Strict clean (above + all inputs collision ≤ 1)** | **0** |

**Zero candidates pass the strict cleanliness gate. Zero pass even the looser ≤5-collision gate when audit and source-sanity are added.**

### Top-15 cleanest-first ranking (sorted: findings → fiscal_year_source → worstCollision → audit-warn-after-pass)

| Rank | MC | Subfunction | Formula | Audit | Findings | Worst input collision | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `mc__finance_function_it_costs_allocated_to_controls_and_risk_management` | GL | 4-var ratio | warn | 0 | **21** | `total_finance_function_it_costs` → BKPF.KURSF (exchange rate — nonsense for "IT costs") |
| 2 | `mc__overhead_rate` | GL | 4-var ratio | warn | 0 | **21** | `total_indirect_costs` → BKPF.KURSF (exchange rate) |
| 3 | `mc__maintenance_cost_pct_of_asset_value` | fixed_assets | 4-var ratio | warn | 0 | **25** | `total_asset_value` → BKPF.KURSF (exchange rate) |
| 4 | `mc__asset_maintenance_cost_ratio` | iso_55001 | 4-var ratio | warn | 0 | **25** | similar nonsense mappings |
| 5 | `mc__spend_by_vendor_category` | AP | filtered sum | **pass** | 0 | **30** | `transaction_amount` → TYPE_SD_S_MAP.NETWR (invoice line net — defensible semantically but 30-CF collision) |
| 6 | `mc__cash_flow_to_revenue_ratio` | cash_flow | 4-var ratio | warn | 0 | **30** | `operating_cash_flow` has no L2 BF (input missing) |
| 7 | `mc__depreciation_amortization_as_of_revenue` | fixed_assets | 4-var ratio | warn | 0 | **30** | mixed ANLC + TYPE_SD_S_MAP |
| 8 | `mc__ebitda_margin` | GL | 4-var ratio | warn | 0 | **30** | EBITDA CF has no L2 BF (input missing) |
| 9 | `mc__sg_a_as_of_revenue` | GL | 4-var ratio | warn | 0 | **30** | SG&A CF has no L2 BF (input missing) |
| 10 | `mc__bad_debt_ratio` | revenue_accounting | 4-var ratio | warn | 0 | **30** | total_revenue → NETWR (30-CF) |
| 11 | `mc__goppar` | AR | 2-var ratio | **pass** | 0 | **49** | Hotel-industry "Gross Operating Profit Per Available Room" mapped to BSID.WRBTR — **definitionally wrong** (this is not a hotel-domain platform yet) |
| 12 | `mc__high_risk_ar_exposure` | AR | filtered sum | **pass** | 0 | **49** | `accounts_receivable_balance` semantically OK (BSID.WRBTR=AR amount); `customer_credit_risk_rating` → credit_type_code (different concept) |
| 13 | `mc__days_sales_outstanding` | AR | 4-var ratio | warn | 0 | **49** | (one of the 7 accepted; see A3) |
| 14 | `mc__debt_yield` | general_finance | 4-var ratio | warn | 0 | **49** | `total_loan_amount` → BSID.WRBTR (49-CF) |
| 15 | `mc__contribution_margin` | general_finance | difference | **pass** | 0 | **53** | `total_sales_revenue` → BSID.WRBTR (53-CF); `total_variable_costs` → COSP.WTG001 (39-CF) |

### Per-category classification (named ledger replaces §5 category estimates)

| Category | Count | Examples |
|---|---|---|
| **A. Clean service-repairable** (no broken token, only dispatch-plumbing gap) | **0** | none |
| **B. Reader-coverage candidate** (one or more inputs have no L2 BF mapping in chain trace — i.e. CF→BF unmapped) | ~9 | `mc__cash_flow_to_revenue_ratio` (operating_cash_flow no BF), `mc__ebitda_margin` (EBITDA no BF), `mc__sg_a_as_of_revenue` (SG&A no BF), `mc__debt_yield` (net_operating_income no BF), `mc__bad_debt_ratio` (total_uncollectable_balances no BF), `mc__goppar` (gross_operating_profit no BF), `mc__contribution_margin_per_product` (similar), several others. **In every observed case, the "missing BF" CF is a derived/output-only concept that has no source-side analog — adding a mapping would be funnel-padding by construction.** |
| **C. Mapping-source gap** (D335-R4 SUM-on-latest or fiscal-year-as-source) | ~14 | All four of the 7-accepted-list's D335-flagged MCs (#2-#5), plus dispatch-gap MCs with the same shape |
| **D. MC envelope / role issue** (duplicate MCs, e.g. mc__roa_return_on_assets vs mc__return_on_assets_roa; mc__net_working_capital_ratio vs mc__working_capital_as_of_revenue) | ~6 (3 pairs) | mc__roa_return_on_assets / mc__return_on_assets_roa; mc__net_working_capital_ratio / mc__working_capital_as_of_revenue; possibly mc__fixed_asset_turnover (fpa) / mc__fixed_asset_turnover_ratio (GL) |
| **E. Shell-CC / ADR-grade cluster** (all inputs in collision groups of ≥10) | **≥85** | The dominant category. Every input above worst-collision=10 is in a funnel-padded cluster |
| **F. Grammar / balance-flow deferred** (computed-source CFs, temporal patterns) | ~6 | `mc__net_working_capital_ratio` (`net_working_capital` → computed source); `mc__working_capital_as_of_revenue` (same); the `average_*` CFs that map to GJAHR are arguably also in this bucket — they're temporal balance metrics that the current grammar can't express |
| **G. Blocked by SDA semantic-risk finding** (per operator interpretation: this is risk evidence, not a hard blocker today) | 114 of 114 | All 114 have inputs whose CFs lack `semantic_family` and provenance. Recorded as risk, not a runtime hard blocker per the addendum's interpretation guidance. |

Bucket sums exceed 114 because most MCs sit in multiple buckets simultaneously. The bucket assigned in the column above is the most-restrictive applicable category per MC (E if it's in a heavily collided cluster, regardless of other issues).

## A5. Top 5 named candidate ranking with evidence

Per the operator's request — top 5 ranked by demo value × semantic cleanliness × repair surface × expected uplift × risk:

| # | MC (named) | Demo value | Semantic cleanliness | Repair surface | Expected uplift | Risk | Verdict |
|---|---|---|---|---|---|---|---|
| **1** | **`mc__high_risk_ar_exposure`** (AR, filtered sum) | High — AR is the demo pilot | `accounts_receivable_balance` mapping to BSID.WRBTR is semantically correct; the wider 49-CF collision group is a *platform-layer* problem, this MC's specific use is defensible | The "filter" semantics (credit_risk_rating = 'HIGH') is the only authoring step that would need to be confirmed; no D335 finding | +1 Apex MC | **Medium-High** — the `customer_credit_risk_rating` input maps to a `credit_type_code` BF, which is not a credit risk rating. This is a real semantic mismatch hiding inside an otherwise clean MC. Until `customer_credit_risk_rating` has its own source mapping (or the formula is rewritten), this is funnel-padding through the back door. | **Defer** — closest plausible candidate, but the credit-risk-rating mapping is the unresolved issue |
| **2** | `mc__spend_by_vendor_category` (AP, filtered sum) | Medium-High — AP demo value | `transaction_amount` → NETWR is semantically defensible (vendor spend = invoice net); the filter `vendor_category` would need verification | Filter authoring + verify vendor_category mapping | +1 Apex MC | **Medium-High** — 30-CF collision on NETWR means once any of those 30 CFs is SDA-certified, this MC's mapping becomes G10 Class-A blocking | **Defer** — same shape as #1 |
| **3** | `mc__contribution_margin` (general_finance, difference) | Medium | `total_sales_revenue` → BSID.WRBTR (53-collision); `total_variable_costs` → COSP.WTG001 (39-collision); both highly collided | Both inputs in heavy collision groups — funnel-padded | +1 Apex MC | **High** — touching either input mapping reproduces funnel-padding | **Defer** |
| **4** | None of the 7-accepted are viable | — | All 7 have either D335-R4, fiscal-year-as-source, or 281-collision membership | — | — | High | **All 7 deferred** |
| **5** | None of the duplicate-pair MCs are viable | — | The duplicates compound the funnel-padding pattern (same metric registered twice, each colliding with the other plus the rest of the cluster) | — | — | High | **All 6 deferred** |

**Verdict: no candidate in the top-15 cleanest list passes the operator's stated hard-blocker bar** ("unresolved semantic collision / shell / grammar / balance-flow risk"). The cleanest #1 candidate (`mc__high_risk_ar_exposure`) has a real semantic mismatch on its filter variable that this walkthrough caught — exactly the kind of hidden funnel-padding the SDA was filed to prevent.

## A6. Stop conditions encountered (named-ledger phase)

| Stop condition | Triggered | Action |
|---|---|---|
| **401 auth-guard issue** | Diagnosed as transient (likely JWKS cache or hot-reload). Source inspection confirms `JwtAuthGuard` is the only path that returns 401 from these endpoints; ScopeGuard and RolesGuard return 403. | Reported. No code patch applied. Smallest-safe-fix candidate (raise `jwksRequestsPerMinute`) documented; not applied. |
| **Funnel-padding temptation** at the "top 5 candidates" surface | Multiple top-ranked candidates land their inputs on collision-group source signatures. `mc__high_risk_ar_exposure` looked clean until the `customer_credit_risk_rating` input was traced to a `credit_type_code` BF — a real semantic mismatch. | Refused. No candidate recommended for action. |
| **Duplicate MC registration** (3 named pairs, possibly more) | mc__roa_return_on_assets / mc__return_on_assets_roa; mc__net_working_capital_ratio / mc__working_capital_as_of_revenue; possibly mc__fixed_asset_turnover / mc__fixed_asset_turnover_ratio | Flagged as Category D. Not addressed in this walkthrough. Belongs to MC envelope governance, not Apex tactical. |
| **Hotel-industry CF in finance domain** | `mc__goppar` (Gross Operating Profit Per Available Room) mapped to BSID.WRBTR (general AR receivable amount) | Flagged as nonsensical mapping. No action. |
| **D335-R4 SUM-on-latest** | 4 of the 7 evaluated/accepted candidates have this real bug. The fix procedure named in chain-detail (`mc-fix.mjs --apply=D335_SUM_ON_LATEST`) was NOT invoked. | Not invoked. Out of scope. |

## A7. Recommendation (revised) — no safe write candidate yet

**Definitive answer: no Apex MC in the bound-not-producing population is safe to ship today** without either:

1. **Reader-coverage work + SC/AC contract authoring** to add genuinely missing source-side mappings for the ~9 Category B candidates whose CFs have no L2 BF (operating_cash_flow, ebitda, sg_a, net_operating_income, total_uncollectable_balances, gross_operating_profit, etc.). These would require adding mappings to source fields that almost certainly don't exist as discrete columns in the source system — most of these are derived business concepts. Adding a mapping is funnel-padding by construction.
2. **G10 cluster cleanup with explicit survivor selection** per the design's per-cluster ADR pattern (out of scope per operator boundary).
3. **D335-R4 fixes** for the 14 SUM-on-latest cases — but every one of those MCs has a more fundamental issue (mapping to fiscal year, etc.).
4. **MC envelope deduplication** for the 3 (probably more) duplicate-pair MCs — but neither survivor in any pair has a clean mapping today.

**The cleanest plausible candidate (`mc__high_risk_ar_exposure`) failed under inspection** because its `customer_credit_risk_rating` input maps to a `credit_type_code` BF — a different business concept. This is the exact failure mode the SDA G10 + Meaning-once invariant is designed to catch at write time. The walkthrough caught it at read time before any write attempt.

### What changes from §8 of the original walkthrough

The original recommendation was "no write slice safe yet, run Option A". Option A is complete; the recommendation **stands and is now confirmed by data**.

### Recommended next move

Two options, in order of preference:

| Option | Scope | Effort | Risk |
|---|---|---|---|
| **B (from §8)** Per-cluster governing-source review of the top G10 collision groups — start with the 281-CF `cc__actual_ledger.actual_ledger_amount sum` group | Pick 5-10 CFs from the 281 that are demo-relevant for Apex (e.g. net_income, recognized_revenue, billed_revenue, accounts_payable_balance, cost_of_goods_sold, all already in this group); for each, governing-source review per the SDA's per-cluster pattern; produce a per-cluster ADR-grade decision MWR proposing survivors and supersession plan. Still paper-only. | 1 session per cluster, paper | Medium — the decisions made here will eventually drive SDA Phase 1 implementation; survivor selection is irreversible once acted on |
| **C (from §8)** Draft DBCP-1a (`master.semantic_family` master table only) | Smallest Phase 1 step; additive new table; doesn't touch any existing primitive | 1 session, DBCP draft only — no execution | Low — operator-approval gate on execution |

**Recommendation: Option B with a 281-cluster cut first.** That cluster touches every demo-headline finance metric (revenue, payables, net income, COGS) and is the lever for ~30% of the bound-not-producing surface. A per-cluster MWR there is the highest-information next paper-only artifact.

If the operator prefers to move forward with structural Phase 1 instead, **Option C is also legitimate** — DBCP-1a is the minimum-risk Phase 1 step and unlocks G5 evaluation downstream.

**Not recommended: any write action on the 114 named candidates.** The data does not support it.

## A8. Evidence sources added (this addendum)

| Source | Used for | Computed |
|---|---|---|
| `GET /api/admin/tenant-metrics/snapshot?tenant=apex` (296 rows × 12 cols) | A2 corrected totals, A3 named accepted list, A4 candidate enumeration | 2026-05-12T06:15:46 |
| `GET /api/registry/metric-readiness/chain-detail/:mcId` × 114 | A3 per-MC trace for accepted; A4 full scan of dispatch_gap | 2026-05-12 PM |
| `GET /api/semantic-definitions/projections/meaning-once-candidates` (re-fetch) | CF → maxCollisionSize map for the full 1,280-CF collision-membership set | 2026-05-12 PM |
| Source inspection: `scope.guard.ts`, `roles.guard.ts`, `jwt-auth.guard.ts`, `cognito-jwt.strategy.ts` | A1 auth diagnosis (401 attribution) | n/a |

## A9. State of play (after addendum)

- Named ledger of 114 non-stale bound-not-producing Apex MCs is complete.
- 7 closest-to-producing MCs are named and chain-detailed; **none is a safe write candidate**.
- Full scan of 114 confirms **zero strict-clean MCs and zero loose-clean MCs**.
- Auth-guard 401 was transient; no fix required.
- Recommendation: defer all Apex writes. Move next to either Option B (per-cluster governing-source review of the 281-CF group) or Option C (DBCP-1a only).

The Phase 0 walkthrough is now operator-actionable. The decision on the next path is the operator's.
