---
uid: DEC-6ee36c
decision_code: D345
title: "Metric discipline taxonomy — function sub-grouping on metric_definition"
description: "Introduce `discipline` as a mandatory sub-grouping layer on metric_definition; Finance disciplines = Working Capital, P&L, Close & Control, Planning, Others; MCs inherit from parent definition."
status: implemented
subdomain: metric-architecture
focus: discipline-taxonomy
date: 2026-04-17
project: bc-core
domain: metrics
refs:
  - type: decision
    uid: DEC-e8a4d2
    label: "D344 — Definition is the canonical parent of MC"
  - type: decision
    uid: DEC-ecec75
    label: "D068 — One contract per KPI (metric architecture)"
  - type: decision
    uid: DEC-bebaec
    label: "D305 — Chain completeness SSOT"
migrated_from: legacy v2 archive
---

# Metric discipline taxonomy — function sub-grouping on metric_definition

## Context

BareCount metrics are organized by `function_code` (finance, hr, ops, sales, …) and `subfunction_code` (20+ per function, e.g. finance has `accounts_payable`, `general_ledger`, `fpa`, `treasury`, …). This taxonomy is *operational* — it mirrors how platform contracts are authored — but it is too granular for the product UX.

Two concrete pain points drove this ADR:

1. **No admin surface for decentralized governance.** Function heads (CFO, CHRO, COO) need a single console to govern their metrics — readiness, freshness, quality, access — without drowning in 20 subfunctions. A CFO does not think in "accounts_payable vs credit_and_collections"; they think in "Working Capital" and "P&L".
2. **No grouping layer exists.** Grouping 20 subfunctions into 4 disciplines has no home in the data model. Hardcoding the map in the frontend violates the "no hardcoded enum arrays" rule (CLAUDE.md QA shift-left) and scatters business taxonomy across repos.

Related facts from the current system:
- 828 metric contracts across 20 finance subfunctions today; 1,241 metric definitions across 21 finance subfunctions (the definition table has broader coverage than the contract table; `internal_audit` has 48 definitions but no MCs yet — surfaced during backfill).
- `general_finance` is the largest bucket at 90 MCs / 204 definitions. Inspection shows it is **not** sloppy classification — it is a genuine cross-cutting bucket containing industry-specific (Insurance IFRS17, Banking CASA, Healthcare Payer Mix) and company-wide ratios (EVA, Cash Ratio, Debt-to-Equity).
- D344 locks "Metric Definition is the canonical parent of MC" — MCs fold under definitions. Any new taxonomy attribute belongs on the parent.
- Future new subfunctions need explicit mapping in this ADR (or a superseding one) before `discipline_code` can be made NOT NULL for their rows.

## Decision

### 1. Introduce `discipline` as a new taxonomy layer

Add a **mandatory, function-scoped** taxonomy layer between `function` and `subfunction` called **discipline**.

- Every `metric_definition` must have a `(function_code, discipline_code)` pair.
- The `discipline_code` is unique *within a function*, not globally. `planning` means something different in finance vs hr.
- MCs **inherit** discipline from their parent `metric_definition` (D344). No discipline column on `metric_contract`.

### 2. Naming: `discipline`

Chosen over `stream`, `pillar`, `practice`, `capability_area`. Rationale: function heads talk in disciplines ("the Working Capital discipline", "the FP&A discipline"). It is the most business-native term, and the term a CFO would use when demoing the product.

**Collision note:** D333 uses "discipline" in the phrase "session discipline audit" for a different concept (session self-audit). The two terms do not collide operationally, but if ambiguity arises in future docs, D333's wording can be renamed to "session self-audit" (its actual meaning) without loss.

### 3. Schema

New master table in platform DB:

```
metric.metric_discipline
  function_code       VARCHAR  FK → master.function.function_code  NOT NULL
  discipline_code     VARCHAR  NOT NULL                            -- e.g. 'working_capital'
  display_name        VARCHAR  NOT NULL                            -- 'Working Capital'
  description_text    TEXT
  sort_order          INT      NOT NULL DEFAULT 0
  archived_at         TIMESTAMPTZ
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
  PRIMARY KEY (function_code, discipline_code)
```

New column on `metric.metric_definition`:

```
discipline_code     VARCHAR  NOT NULL
-- Composite FK: (function_code, discipline_code) → metric.metric_discipline
```

Notes per D162 database rules:
- No JSONB for queryable data — discipline is a column, not a JSON tag (Rule 1).
- Composite FK enforces that a discipline is valid for the stated function (Rule 3).
- No denormalized counters (Rule 2) — counts like "how many MCs in WC" come from a view, not a stored column.
- Naming: `snake_case`, `{noun}_code` for the code column (D148).

### 4. Finance disciplines — the 5 locked values

| `discipline_code` | `display_name` | Scope |
|---|---|---|
| `working_capital` | Working Capital | Liquidity, AR/AP, cash conversion, credit & collections, billing |
| `profit_and_loss` | P&L | Revenue, cost, margin, profitability ratios |
| `close_and_control` | Close & Control | Period close, GL, audit, tax compliance, financial reporting, shared-services cost |
| `planning` | Planning | FP&A, capital structure, investor relations, forward-looking valuation |
| `others` | Others | Industry-specific (Insurance IFRS17, Banking CASA, Healthcare Payer Mix, Hotel F&B) and cross-cutting metrics that do not fit the primary four. Triage bucket for metrics awaiting future classification or separate industry disciplines. |

**Why `others` is a real discipline, not a deferral:** as new tenants onboard across industries, metrics land here without blocking the admin console. Over time, if a coherent cluster emerges (e.g. 40+ Insurance metrics), a dedicated `insurance` discipline is added and those rows are re-homed via UPDATE. `others` keeps the system shippable today without forcing wrong classifications.

### 5. Subfunction → discipline mapping (finance)

| Subfunction | Discipline |
|---|---|
| `accounts_receivable` | working_capital |
| `accounts_payable` | working_capital |
| `credit_and_collections` | working_capital |
| `cash_flow_management` | working_capital |
| `treasury` | working_capital |
| `billing` | working_capital |
| `revenue_accounting` | profit_and_loss |
| `cost_accounting` | profit_and_loss |
| `payroll` | profit_and_loss |
| `general_ledger` | close_and_control |
| `financial_reporting` | close_and_control |
| `financial_systems` | close_and_control |
| `fixed_assets` | close_and_control |
| `financial_risk_management` | close_and_control |
| `iso_55001` | close_and_control |
| `internal_audit` | close_and_control |
| `tax` | close_and_control |
| `fpa` | planning |
| `capital_structure_optimization` | planning |
| `investor_relations` | planning |
| `general_finance` | **(classified per-metric into WC/P&L/Close/Planning/Others, see §6)** |

**Tax placement rationale:** OAGIS does not classify tax as a process discipline — it models tax as a data primitive (Tax Noun component embedded in Invoice/JournalEntry BODs). The relevant industry standard for process grouping is APQC PCF 8.0, which places "Manage taxes" (8.9) alongside GL/reporting/internal-controls, not under planning. Our 31 tax MCs are predominantly compliance/operations metrics (automation rate, jurisdictions managed, penalty & interest), consistent with `close_and_control` framing. Tax *strategy* metrics (e.g. "Tax Savings from Planning") may be re-homed to `planning` during triage if the judgment call favors that.

**Subfunction is retained** as a secondary grouping inside a discipline. Subfunctions are referenced by contracts, readers, SOPs, and existing chain metadata — deprecating subfunction is a larger migration than this ADR scopes. The admin UX groups by discipline; power users can drill down to subfunction within a discipline.

### 6. `general_finance` triage rule

The 90 `general_finance` MCs do not map cleanly to one discipline because the subfunction itself is cross-cutting. Classification happens **per `metric_definition`**, using a rule-based first pass with human review of edges:

**Rule-based first pass (applied by migration script, not ADR):**

- Industry-specific keywords `/IFRS\s?17|GWP|CSM|embedded value|VNB|loss development|combined ratio|CASA|yield on advances|spread \(yield|credit-deposit|payer mix|outpatient|tuition|F&B|AISC|AIC|farm/i` → `others`
- Metric name matches `/cash|liquidity|invoice|payment|credit|deposit|undrawn|runway|burn/i` → `working_capital`
- Metric name matches `/margin|cost|revenue|profit|yield|spread|price|pricing|return on sales/i` → `profit_and_loss`
- Metric name matches `/tax|audit|deferred|compliance|control|shared services|legal entity|IT costs/i` → `close_and_control`
- Metric name matches `/debt|equity|dividend|capital|valuation|book value|refinancing/i` → `planning`
- No match → `others`

**Human review required** for metrics matching ≥2 rules. Examples:
- `Return on Idle Cash` — matches cash (WC) and return (P&L). Likely `working_capital` (it is a cash-efficiency metric).
- `Tax Savings from Planning` — matches tax (Close) and planning. Likely `planning` (the act of planning, not tax operations).
- `Cash Cost per Unit` — matches cash (WC) and cost (P&L). Likely `profit_and_loss` (unit economics).

Outcome documented in a follow-up task, not in this ADR. This ADR locks the *taxonomy*, not every individual classification.

**Industry-specific metrics go to `others` by default** (§4). If a later industry-specific discipline is added (e.g. `insurance`), those rows are re-homed via UPDATE. `others` is explicitly not a dumping ground — it is a staging discipline with a known exit path.

### 7. Migration strategy

1. Create `metric.metric_discipline` table.
2. Seed the 5 finance disciplines (working_capital, profit_and_loss, close_and_control, planning, others).
3. Add `discipline_code` as **nullable** on `metric_definition`.
4. Run classification script (rule-based pass + manual review file for edges).
5. Backfill all metric definitions (714 + any new ones).
6. Alter `discipline_code` to **NOT NULL** once backfill complete.
7. Enforce composite FK.

Migration gates:
- Zero NULL `discipline_code` before NOT NULL alter.
- Zero rows violating composite FK before FK alter.
- Regression check: chain_status counts unchanged (discipline is UX metadata, not chain logic).

## Options Considered

### Option A: Discipline as schema column on `metric_definition` (chosen)

Pros: data-driven, extensible to hr/ops/sales, honors "no hardcoded enums in frontend" rule (CLAUDE.md), composable with RBAC and dashboards, survives ownership changes.
Cons: schema change, migration cost, requires triage of 90 `general_finance` MCs.

### Option B: Hardcode the subfunction → discipline map in bc-portal (rejected)

Pros: ships faster, no migration.
Cons: violates QA shift-left rule, duplicates business taxonomy if hr/ops want the same pattern, breaks when subfunctions are added/renamed, cannot support future per-tenant overrides.

### Option C: Use `tags` JSONB on `metric_definition` (rejected)

Pros: no schema change.
Cons: violates D162 Rule 1 (no JSONB for queryable data — UI filters, admin pages, RBAC all query this). Breaks referential integrity.

### Option D: New taxonomy at `subfunction` level only (rejected)

Pros: no new layer.
Cons: we already have 20 subfunctions; the problem is they are too granular for admin UX. Adding a new term at the same level solves nothing.

## Consequences

### Positive
- Single source of truth for business-facing grouping. Admin UX, dashboards, RBAC, and docs read from one column.
- Extensible — hr can have its own disciplines (e.g. Talent, Comp & Benefits, Workforce Analytics) without ADR revision.
- Enables the Function Admin Console (ADR-B, pending) to group metrics coherently.
- Aligns metric taxonomy with how function heads actually speak about their domain.

### Negative
- Schema migration with a not-null column requires backfill discipline.
- `general_finance` triage is real work — 90 MCs need classification with human judgment on edges.
- Two grouping layers (discipline + subfunction) increase cognitive load for contract authors. Mitigated by authoring UI showing discipline as a derived label from subfunction where the map is unambiguous.

### Risks
- **Misclassification during triage** — wrong discipline puts a metric in the wrong admin's console. Mitigation: classification is reversible (UPDATE one column), and the triage file is reviewed before bulk apply.
- **Function-specific disciplines may diverge over time** — finance may refine its disciplines later (e.g. split WC into AR/AP/Cash). Mitigation: disciplines are data rows, not enums — renaming or adding is a data change, not a code change.
- **`others` becomes a dumping ground** — without discipline, classifiers default to `others` to avoid decisions. Mitigation: the rule-based triage script in §6 does not default to `others` for well-matched metrics; `others` is reserved for industry-specific and genuinely unclassifiable. A periodic review (quarterly) inspects `others` volume and splits out new disciplines when a coherent cluster of ≥15 metrics forms.

## Follow-ups (not blocking this ADR)

- **ADR-B** — Function Admin Console + decentralized RBAC (`function_admin` role scoped by `function_code`, route `/admin/functions/{function_code}`).
- **Task** — classify all 90 `general_finance` MCs via the §6 rule-based pass + human review.
- **Task** — seed disciplines for hr, ops, sales, marketing once finance is proven.
- **Task** — update metric authoring UI (bc-admin) to show discipline alongside function/subfunction.

## Out of scope

- Freshness SLA, quality thresholds, and access control models — covered by ADR-B and its sub-ADRs.
- Tenant-level discipline overrides — no evidence of need; defer.
- Cross-function disciplines — explicitly rejected (§1). A "compliance" discipline spanning finance + legal + hr is not supported in v1.
