# Odoo Target-Company Data-Profile Framework

**Status:** DRAFT for in-depth discussion. **Scope: SOURCE-SIDE ONLY** — the at-home
backbone. This document does NOT cover platform integration (reader → contract chain →
metric → projection); that is the deferred, Track-C-gated
`PKG-odoo-pilot-implementation-design`, which *consumes* this framework.
**Authority context:** D538 (master-data / profile framework) · D539 (no platform FX) ·
D537 (pre-staging) · TSK-43eecb. **Locked principle (2026-07-30):** source-side is
decoupled from metric-side; readers are function-scoped + source-agnostic; build a
max-function-module *coherent* Odoo at home to break the reader/metric catch-22.

---

## 1. Why this exists (the catch-22 it breaks)

The Reader is **function/subfunction-scoped and source-agnostic**: an AR Reader owns the
canonical maps for AR objects across *all* systems (SAP/BC/Odoo/Tally) and acquires
per-source **flavors**. Therefore a function's reader flavor and its metrics **cannot be
developed or validated until a source carrying that function's data exists.**

Without a full-function source at home, every non-finance function is stuck: you can't
build the Payroll reader until payroll data exists, can't build the Inventory reader until
inventory data exists — and that data only arrives when a real client with that module
lands. That is a catch-22: you develop reactively, on the client's clock, against their
live system, with no way to pre-validate.

**This framework is the escape.** A max-function-module, coherent Odoo built at home means
**every function's reader flavor and metric surface can be developed and proven before any
client** — so when a prospect lands, the reader already exists and the metrics are already
validated. Odoo is uniquely suited: it is the one target system we can freely stand up and
script all functions' data for (open, deterministic). SAP/BC/Tally we cannot generate as
freely.

**Two hard rules that keep the decoupling honest:**
- Source completeness is driven by **realism / function coverage**, never by metric demand.
- Source richness **never implies metric realization** — having HR data ≠ having an HR
  metric. Zero-claims and gate-eligible ≠ runtime-ready still hold. The backbone lowers the
  *cost* of realizing a metric, never the *bar*.

---

## 2. Architecture — two layers

### 2.1 Base installation (profile-independent)
The platform-aimed Odoo system itself, shared by all profiles:
- **Runtime:** Odoo 17 + Postgres, on the cost-managed EC2 pattern (start → build → AMI →
  stop). Modules: the full-function set the framework targets (see §4), installed once.
- **Config scaffolding:** `setup_shell.py` (company/entity creation, currency/FY/CoA — ORM,
  not RPC), `setup_config.py` (idempotent audit+repair of identity/bank/tax/supplementary
  accounts), `onboarding_shell.py` (dashboard banner). This layer is *system* setup, not a
  profile — it makes a clean Odoo ready to receive any profile's data.

### 2.2 Profile (what defines a target company)
A **profile** is the complete definition of one synthetic target company. Its parts:

| Part | What it is | Artifact (mfg-in = Profile #1) |
|---|---|---|
| **Archetype** | industry · size · geography · accounting standard · buyer type (B2B/B2C) | B2B precision-components mfr · India · Ind AS · 3 legal entities |
| **Master registry** | the shared cross-system join-key entities (customers, vendors, items, employees, machines…) with `active_from`/churn | `data/profiles/mfg-in/master.json` (IDs = `CUST-`/`VEND-`/`ITEM-`…) |
| **Generators** | the per-function chronological passes that emit the funnel head; Odoo materializes the rest | `seed.py`, `coverage.py`, `scenarios.py`, `bank_recon.py`, `anomalies.py`… |
| **Benchmarks** | the financial-structure envelope (common-size ranges) the world must land inside | `master.json.benchmarks` |
| **Gate battery** | the reusable acceptance test | `verify/{integrity,benchmarks,coa_coverage}.py` + regression guards |
| **Anomaly register** | planted, documented defects = the falsifiable answer key | `data/profiles/mfg-in/anomalies.json` |

**The key idea:** framework *code* is shared; a profile is *config + data*. A second profile
reuses the base install, the generator machinery, and the gate battery — it changes the
archetype, the registry, the benchmark envelope, and the generator parameters.

---

## 3. The chronological build (the profile *builder*)

A profile is built by **one forward simulation loop** (per `PLAN-odoo-pilot-v2` §1), not by
layered passes — this dissolves the inter-pass defect class the dry-run hit
(phantom-remits, REV-chains). It also mirrors the platform's own object progression
(forward-only, no back-reference, no rewrite) — the generator adopting the discipline of
the thing that will read it.

```
simulate_company_creation()          # base install applied, entities incorporated, capital
for month in window:                 # forward only
    master_deltas(month)             #   customers/vendors onboard & churn; machines bought
                                     #   (named-vendor bill) / retired (disposal); price revs
    operations(month)                #   per-function funnel head: O2C, P2P, CRM, production…
    month_close(month)               #   payroll, depreciation-on-assets-that-exist, accruals
    next_month_obligations(month+1)  #   statutory remits, EMIs, settlements, reversals
```

Each **function** is an additive pass in this loop, realism-gated, proven on one month
before the full window (D268 one-then-many). This is exactly how finance came together in
the dry-run; new functions extend the same loop.

**Honest limit (verified):** business dates (posting/document/due/clearing) are fully
backdatable and spread across the window → all business-date metrics are meaningful.
Odoo-owned wall-clock (`create_date`, CRM `date_closed`) is NOT backdatable → audit-log
process-velocity (CRM stage-dwell) is only demonstrable on the living-data window forward,
not on the back-seed. Stated, not hidden.

---

## 4. Function-coverage map (the horizon)

The horizon is **function coverage via one coherent business**. The archetype is the
coherence spine (same customers/products/entities across modules, so cross-function metrics
resolve); it is NOT a bound on modules. Install every Odoo module the coherent manufacturer
runs:

| Odoo module | Function(s) unlocked | Reader/metric surface | mfg-in status |
|---|---|---|---|
| `account` + `l10n_in` | GL, AR, AP, tax, financial-reporting, cash/treasury | 296 finance MCVs | ✅ DONE (dry-run) |
| `sale_management` | sales / O2C, revenue | order-to-cash, sales metrics | ✅ funnel head |
| `purchase` | procurement / P2P | PO→receipt→bill, spend | ✅ (PO flow added) |
| `stock` | inventory, valuation, logistics | inventory metrics, delivered qty | ◐ deliveries yes; **valuation = rebuild-native (storable products)** |
| `crm` | sales pipeline, marketing-adjacent | funnel, velocity, campaign | ◐ pipeline+journeys; velocity living-only |
| `mrp` | manufacturing / MES | production orders, BoM, WIP | ❌ Tier-2 (next) |
| `hr` + `hr_payroll` | HR / payroll headcount | per-employee payroll metrics | ❌ GL payroll yes; per-employee = Tier-2 |
| `hr_timesheet` / `project` | project, utilization | project metrics | ❌ Tier-2 |
| `quality` / `maintenance` | quality, asset maintenance | NC, MTBF, AMC | ❌ Tier-2 (QA rejections exist as financial shadow) |
| `hr_expense` | employee expenses | expense metrics | ❌ Tier-2 |

**One archetype covers most functions, not all.** A manufacturer does not run POS/retail,
ecommerce, subscription-revenue, or field-service. Those function-shapes need a **second
archetype** (a retailer, a services firm) — §5.

**Build sequence (proposed):** finance ✅ → inventory+MRP (unlocks manufacturing +
valuation, the biggest gap) → HR/payroll (per-employee) → quality/maintenance/project.
Each is an additive chronological pass with its own realism gate.

---

## 5. Multi-profile model

`mfg-in` is **Profile #1**. The framework is built to hold N profiles so the function
surface *and* the source-shape variety grow:

- **More function coverage** — a retailer profile brings POS/retail/ecommerce function-shapes
  a manufacturer can't. A services firm brings project/subscription shapes.
- **More source-shape variety** — different accounting standards (US GAAP, IFRS), geographies
  (different tax/localization modules), sizes (single-entity SME vs multi-entity group),
  buyer types (B2B vs B2C). This is what lets a reader flavor be tested against *variety*,
  not one shape.
- **Shared spine, per-profile config** — base install + generator machinery + gate battery
  are shared; archetype + registry + benchmarks + generator parameters are per-profile.

**Profile roadmap (candidate):** P1 mfg-in (B2B mfr / India / Ind AS) ✅ · P2 retailer
(B2C / POS+ecommerce) · P3 services/IT firm (project/subscription) · P4 a US-GAAP or
multi-entity-group variant. Order driven by which function-shapes the platform most needs
to develop readers for — a discussion, not fixed here.

---

## 6. Gate battery (reusable acceptance test)

Every profile passes the same battery before its AMI is baked (all green on mfg-in):
- `verify/integrity.py` — per-company zero-sum ledgers, no orphans/missing company_id, FX
  both-amounts, UI list views load.
- `verify/benchmarks.py` — the profile's declared financial-structure envelope (per FY, per
  entity); fails outside the enforced ranges. This is how a calibration error (e.g. B2C-scale
  ad-spend in a B2B profile) becomes mechanical rather than eyeball-caught.
- `verify/coa_coverage.py` — per-company CoA coverage (mfg-in: 97%).
- Regression guards — no reversal chains, no duplicate obligations.
- Generator rules (paid for): idempotency = ref + `state != cancel`; one rnd stream per
  generator per month; reversal sources exclude their own outputs; registers built by
  discovery not by logging.

---

## 7. Operations

- **Instantiate:** start EC2 → base install → run the profile's chronological build → gate →
  bake AMI (`<profile>-<date>-<horizon>`) → stop instance. Cost: ~$0.67/build-day on
  t3.medium.
- **Living data:** from AMI onward, a catch-up loop posts the missed days on wake so
  freshness is automatic without 24/7 compute — and it is the only way behavioral
  (wall-clock) history accumulates truthfully.
- **Snapshot/resume:** each profile = one AMI; stopped instance resumes in ~2 min.
- **Registry of profiles:** the committed `data/profiles/<name>/` tree is the profile SSOT
  (master.json, anomalies.json, gate results). See §8 for surfacing this.

---

## 8. The bc-admin read surface (repair location F — the framework console)

*(This section is the in-depth discussion topic — operator idea 2026-07-30. Design
questions are flagged for decision, not pre-decided.)*

**What it is:** a read-only surface in **bc-admin** (platform scope) that is the human
window onto the profile framework — the operator/reviewer/demo view of *what target
companies exist in our at-home lab and how healthy each is*.

**Why bc-admin and not Odoo's own UI:** Odoo's web client shows *one profile's raw data*.
The bc-admin surface shows the **framework layer Odoo doesn't know about** — archetype,
function coverage, benchmark health, gate results, the anomaly answer-key — and it is the
**one place to see ALL profiles across ALL source systems** (when BC/Tally profiles arrive,
they aren't in the Odoo UI). It is the cross-source, cross-profile, framework-level console.
This is the read model / diagnostics layer (repair location F) for the backbone.

**Candidate views (read-only):**
1. **Profile catalog** — all profiles: archetype, source system, function coverage,
   last-built date, gate status (green/amber), AMI id.
2. **Profile detail** — the companies/entities, the function-coverage map, benchmark
   dashboard (per-FY common-size vs envelope), CoA coverage, doc counts.
3. **Anomaly register** — the planted-defect answer key (the falsifiable demo surface).
4. **Gate results** — the acceptance-test output, per profile, historized.

**Design questions to resolve (the depth):**
- **Data source / authority.** The committed `data/profiles/<name>/*.json` + gate outputs
  are the SSOT. bc-admin reads bc-core (platform-scoped), not bc-sdg files. So a serving
  layer is needed. Options: (a) a thin bc-core platform endpoint that reads a *profile
  registry* table; (b) devhub serves it (devhub is the coordination hub, already has an API
  + MCP); (c) bc-core reads the artifacts from a synced location. **Where should the profile
  registry live?**
- **What IS a profile, in platform terms?** A profile is closer to a *synthetic tenant*
  (a specific company world) than to a *source system* (Odoo the software). Source Catalog
  (`source.*`) registers the *system*; a profile is an *instance/tenant* of it. Does a
  profile map to a tenant row, a new first-class "profile" entity, or stay file-only with a
  thin registry? (Leaning: a lightweight profile registry keyed to the artifacts, distinct
  from both source-system and tenant, until Track-C onboarding makes it a real tenant.)
- **Live vs snapshot data.** Detail views over *counts/benchmarks/gates* read the committed
  artifacts (cheap, always available). Showing *live Odoo rows* would require the instance
  running + a read path — defer, or link out to the Odoo UI.
- **Scope of read-only v1.** Catalog + detail + benchmarks + anomalies from artifacts is a
  bounded first cut. Later (write): trigger a build/refresh from the UI (much later; it
  drives EC2 + generators).
- **bc-admin constraints.** Platform scope → `@PlatformOnly()`, no x-tenant-id; no hardcoded
  enum arrays (use `useMaster*` hooks); React/Vite; port 3010.

**Sequencing:** the console is a *consumer* of the framework — build it after the profile
artifact schema is stable (mfg-in already gives a concrete schema to design against). It
does not touch Track-C. A natural near-term slice: profile-catalog + mfg-in detail +
benchmark/gate/anomaly panels, served from a thin profile registry.

---

## 9. What this framework does NOT do (boundaries)

- No reader, no contract chain, no metric evaluation, no projection — that is the deferred
  `PKG-odoo-pilot-implementation-design` (Track-C-gated).
- No claim that source richness = metric capability (§1 rule 2).
- No tenant onboarding into the platform (that is Track-C).
- The bc-admin console (§8) reads the framework; it is not a platform-integration surface.
