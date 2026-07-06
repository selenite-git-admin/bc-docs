---
id: demo-plan-cfo-pack
order: 30
title: "CFO Pack Demo Plan"
status: locked
authority: authoritative
depends_on: [tenancy-and-binding, metric-catalog, metric-evaluation, quality-gates-and-chain-integrity]
governing_sources:
  - DataJetty Platform pitch deck (December 2026 skeleton)
  - bc-portal Beyond UX v1 spec
  - Metric Readiness Toolkit (development/)
governing_adrs:
  - DEC-076521 (D396 — Apex Tenant Binds to SAP S/4HANA Reader Chain; bc-sdg as Profile-Parameterised SDG-SAP Service)
  - DEC-049cb1 (D395 — superseded by DEC-076521; retained for traceability)
  - DEC-28b176 (D394 — Metric Readiness Model)
  - DEC-d2cdb9 (D384 — SAP API admission stance; Published OData / CDS Published Views only)
  - DEC-6cb4f3 (D385 — Source Systems framework)
  - DEC-bebaec (D305 — Chain Completeness SSOT)
  - DEC-6cdceb (D361 — bc-portal three-surface split; Beyond / Metrics / Data / Settings)
  - DEC-2cf250 (D362 — BareCount visual language)
  - DEC-771baf (Tenant database architecture; platform-tenant one-way dependency — the structural barrier behind the permanent demo invariant)
  - DEC-1918d0 (Database Rules; per-tenant SQL isolation enforced at the connection layer)
errata_referenced: []
v2_sources: []
diagrams: []
---

# CFO Pack Demo Plan

The DataJetty CFO Pack ("Money Metrics") is the anchor demo: a Finance Control Tower with ~30–40 hero KPIs across 10 KPI groups, surfaced through the Beyond conversational canvas with Rooth-grounded answers and one-click drilldown into the Trust Chain. This document is the framework that ties the product narrative to the implementation phases. The phase-0 storyboard is its first deliverable, not its content.

## Positioning

From the DataJetty deck:

- **Tagline**: *"Zero-Engineering Data Action Platform — For Trusted, Business-Aware Intelligence"*
- **Anchor pack**: CFO ("Money Metrics") — Finance Control Tower
- **Why it wins**: Zero IT lift, ERP/CRM-agnostic, CFO-grade definitions, governed KPI dictionary, MVP in 4–6 weeks, foundation scales to CMO/CGO/COO packs
- **Differentiator surfaced in Beyond**: *"Ask the CFO AI"* (Rooth) — conversational over governed metrics with provenance one click away

The demo must demonstrate both differentiators in the same flow: a CFO asks Rooth a business question, Rooth answers using metrics that tie out, and a click takes them to the Trust Chain to see the source provenance. *"Beyond Dashboards"* is not a phrase; it's a navigation pattern.

## Permanent demo invariant — client data access is denied by design

The demo is not a one-time artefact for a specific event; it is the **permanent sales surface** for BareCount. After the platform has paying clients, marketing demos still use the synthetic Apex Motors tenant. Live client data is never used as marketing material. This is a foundational decision worth stating explicitly because the architecture enforces it.

### The architectural barrier

Quoting [`compliance/infosec-and-access-control.md`](../../../compliance/infosec-and-access-control.md):

> *"The connection isolation is structural: the platform connection cannot read tenant data because the connection string points at a different database; the tenant connection cannot read platform-scope tables because the search path scopes the resolution to the tenant schemas. A misrouted query returns 'relation does not exist' rather than leaking data across the boundary."*

Three architectural levels enforce this:

| Level | Mechanism | Effect |
|---|---|---|
| Database | Platform DB and each tenant DB are separate database instances with separate connection strings | A platform-side service literally cannot resolve tenant tables |
| Schema | Within a tenant connection, the search path scopes to that tenant's schemas (`progression`, `fact`, `evidence`, `admin`, `organization`, `tenant_dim`) | Misrouted queries within a tenant return "relation does not exist", not data |
| Direction-of-dependency | Code paths flow platform → tenant only; tenant services never read platform-scope rows directly (DEC-771baf) | The dependency direction is the access-control discipline; enforced in `bc-core/src/database/tenant-connection.service.ts` |

The implication: a BareCount engineer cannot pull client data into a marketing demo by accident, by oversight, or by team-pressure. They would have to engineer a deliberate exception — a new connection string, a bypass of tenant routing, a rewrite of the search-path scoping. Such a violation leaves traces and would surface in any standard SOC 2 / ISO 27001 review.

### What this means for the marketing pitch

Most companies tell prospects *"we promise not to use your data for marketing."* That's a contractual claim. BareCount's claim is a system-property claim:

> *"We can't use your data. The architecture is designed so that the team building the demo and the team running your tenant cannot share data. A query that crossed the boundary would return 'relation does not exist'. The implementation lives in `tenant-connection.service.ts`; the design is locked by DEC-771baf and DEC-1918d0."*

That's a stronger statement, and it's a sales differentiator with risk-averse Indian large-cap CFOs who name data exposure as a primary objection. It moves *"no client data in marketing"* from being a limitation we tolerate to being a property we claim.

### The marketing playbook post-clients

| Allowed (with explicit per-use consent) | Forbidden (always) |
|---|---|
| Written case studies — describe outcomes, not show data | Live client-data demos to other prospects |
| Screenshots with redaction or mock numbers, used in pitch decks | Real client screenshots without redaction |
| Quotes / testimonials | Pulling client KPIs into BareCount marketing dashboards |
| Aggregate "across our customer base, DSO improves X% on average" | Individual client identification in any marketing surface |
| Customer logos on website (with consent) | "Customer X uses BareCount and they have ₹Y working capital" — even with consent |

Each allowed pattern requires explicit consent for the *specific* use. Consent doesn't transfer between formats — a logo permission is not a screenshot permission, a screenshot permission is not a numbers permission.

Live demos always use SDG. This is a permanent operational rule.

### The structural extension to demo operations

Because the demo is permanent, bc-sdg is permanent. Phase 1 (next section) is reshaped accordingly: bc-sdg is not a one-shot emitter; it is a continuous service that:

- Emits postings on a schedule (rolling forward; old periods age out gracefully)
- Maintains story-event *patterns* rather than fixed events (the named entities and amounts in the storyboard are templates the patterns instantiate quarterly)
- Pushes through bc-core's standard reader API — the same path a real customer's data would take. The Trust Chain in the demo shows real run IDs, real timestamps, real evidence rows. Provenance is fully authentic regardless of data origin.

Operational consequences of the always-on architecture (cost budget, monitoring, period rollover) live in `docs/operations/demo-operations.md` (separate chapter, written when Phase 1 architecture lands).

## The reality gap

As of 2026-05-08, sandbox1 (the demo tenant) has:

| Layer | Count | Meaning |
|---|---:|---|
| Finance MDs in seed catalog | 1,241 | The aspirational set |
| MCs with active versions | 376 | What's authored |
| MCs bound to sandbox1 | 30 | Pilot scope |
| MCs producing in sandbox1 | 14 | Today's reality |
| Audit-clean unbound (would produce) | 7 | Strict candidates left |

Across 6 sessions of fixing onboarding issues (SES-61f2f6 → SES-d88852), sandbox1 went from 2 producing to 14. Each remaining gap is well-categorized by the [Metric Readiness Toolkit](../../../development/metric-readiness-toolkit.md):

- **652 MDs without an MC**: catalog authoring backlog
- **96% of active MCs not producing in sandbox1**: ~75% of broken tokens are `null_in_tenant` (upstream source-data emission gap), ~25% are `type_mismatch` (authoring-shape repointable)

For a CFO demo that demonstrates 30–40 hero metrics tying out coherently, the dominant constraint is **source-data emission**, not chain authoring. bc-sdg must produce a coherent business story, not random data.

## The four-phase plan

| Phase | Weeks | Owner | What unlocks |
|---|---:|---|---|
| 0 — Storyboard lock | 0.5 | founder + Claude | Contract for everything downstream |
| 1 — bc-sdg coherent ledger as continuous service | **4–5** | bc-sdg sessions | Apex tenant emits postings on a schedule; story-event patterns refresh quarterly; coherence monitored hourly |
| 2 — Catalog activation in apex tenant | 1–2 | bc-core sessions | 36 hero KPIs producing in apex; sandbox1 stays as dev tenant |
| 3 — Beyond rewire with role-aware Rooth | 1–2 | bc-portal session | 5 users each see their own LHS + Rooth narration; type-first + drag-first both wired |
| 4 — Demo Operations | 1–2 | shared | Coherence monitor + rollover + health dashboard + cost monitoring; demo runs autonomously |

**Total: ~8–10 weeks** to a permanent, self-running, prospect-pokeable CFO Pack demo. Tier 1 only (no SFDC bridge yet); the deck's *"MVP in 4–6 weeks"* claim is met by Phases 0–2 (storyboard + coherent emission + catalog activation), with Phases 3–4 making the demo operational rather than just buildable.

### Phase 0 — Storyboard lock (~0.5 week, COMPLETE)

**Owner**: founder + Claude session  
**Deliverable**: [`docs/operating-model/demo-plan-cfo-pack-storyboard.md`](demo-plan-cfo-pack-storyboard.md) — locked.

The storyboard is the contract for everything downstream. It locks:

1. **The 30–40 hero KPIs** — selected from the deck's 10 KPI groups (Revenue & Profitability, Liquidity & Working Capital, AR Performance, AP Performance, Budgeting & Forecast Accuracy, Cost Accounting, Tax & Compliance, ERP Practices & Control, Anomaly & Alerts, Finance Ops Readiness)
2. **The narrative arc** — what the CFO discovers during the walkthrough (e.g. *"Q3 closed with revenue up 8% but cash down — DSO crept 38 → 47, top customer missed two cycles, dispute cycle stretched"*)
3. **10–15 Rooth Q&A pairs** — what the CFO asks, what Rooth answers, which metrics back the answer, which click opens the Trust Chain
4. **Coherence assertions** — the equations that must tie out (revenue − COGS = gross profit, DSO + DIO − DPO = CCC, current ratio = current assets / current liabilities, etc.)
5. **The synthetic-business shape** — industry (mid-market manufacturing), 3 company codes, ~5K customers, ~500 vendors, 12–24 months of postings, embedded story events (one delinquent customer, one cost overrun, one anomaly worth surfacing)

**Exit criteria**: founder approves the storyboard. Phase 1 cannot begin without it.

### Phase 1 — bc-sdg coherent ledger as a continuous service (4–5 weeks)

**Owner**: bc-sdg session(s)  
**Deliverable**: a bookkeeping-correct emitter that runs as a continuous, autonomous service against the apex tenant, with story-event patterns that refresh quarterly.

**Architecture lock**: [DEC-076521 (D396) — Apex Tenant Binds to SAP S/4HANA Reader Chain; bc-sdg as Profile-Parameterised SDG-SAP Service](../../../governance/adrs/ADR-076521.md). Read this before starting any Phase 1 implementation work. (The earlier [DEC-049cb1 (D395)](../../../governance/adrs/ADR-049cb1.md) is superseded — its custom `apex-emitter` source_system + push framing diverged from the canonical pattern in [`source-systems/sap-s4hana.md`](../../../reference/source-systems/sap-s4hana.md).)

Apex tenant uses the **canonical SAP S/4HANA reader chain** — the same chain that will serve a real S/4HANA customer. The single architectural difference is `runtime.connection.endpoint_uri`: apex points at bc-sdg's existing 4200 OData server (S/4HANA Cloud landscape route); a real customer points at their SAP server. Identical Trust Chain, identical executor (`SapOdataV4Executor`), identical contracts.

bc-sdg's existing 4200 OData server is the **SDG-SAP service** — a profile-parameterised synthetic-data emitter. It already supports six stochastic profiles (`auto-parts`, `chem-co`, `fmcg`, `mfg-co`, `pharma-co`, `real-estate-co`). Phase 1 adds a 7th profile, `apex-motors` (auto-OEM industry, the demo storyboard's narrative), with story-event patterns layered on top. Future tenants on pharma / FMCG / etc. instantiate parallel profiles; SDG-SAP is permanent infrastructure, not apex-specific.

**Five components (per DEC-076521)**:

| # | Component | Where it lives | One-line role |
|---|---|---|---|
| A | World-state persistence | Postgres schema `sdg_world` (renamed from `apex_world`) in `bc_sdg` cluster, partitioned by `profile_code` | Ground truth for entities, prices, FX, period state, pattern arcs, balances |
| B | Story-event pattern engine | `bc-sdg/src/sdg/engine/` (generic) + `bc-sdg/src/sdg/profiles/apex-motors/patterns.ts` (per-profile) | Code-defined state machines (cannot be silenced) that rotate named entities quarterly |
| C | Bookkeeping-correct posting generator | `bc-sdg/src/sdg/profiles/apex-motors/posting/` | Reuses `core/document-balancer.ts`; produces BSEG/BKPF rows in `sdg_world` ready for OData projection |
| D | Tenant binding to SAP reader chain | platform DB (2 rows) | Insert `runtime.connection` for apex (endpoint = bc-sdg 4200 /s4cloud with profile selector) + `runtime.reader_binding` linking the existing SAP S/4HANA Cloud reader to apex tenant. NO custom executor; NO /snapshot push. |
| E | Lambda decomposition + EventBridge | AWS infra | 5 Lambdas (`sdg-apex-emit`, `sdg-apex-close`, `sdg-apex-pattern-refresh`, `sdg-coherence`, `sdg-period-rollover`); cost ~$10–15/mo |

**Architectural choices (locked, per DEC-076521)**:

| Choice | Decision |
|---|---|
| Source identity | `source.source_system.system_name='s4hana'` — the existing platform row. The Trust Chain reports SAP S/4HANA Cloud, not a synthetic source. |
| Reader chain | Existing `sap-s4-cloud-odata` flavor on `SapOdataV4Executor`. No new reader, no new executor. |
| Data path | bc-core's SAP reader **pulls** from bc-sdg's 4200 OData server (S/4HANA Cloud landscape). Identical mechanism a real S/4HANA customer's chain uses. The single difference is `runtime.connection.endpoint_uri` — apex points at bc-sdg, a real customer points at their SAP server. |
| Deployment | AWS Lambda + EventBridge scheduled rules. Cheapest reliable always-on; ~$10–30/month. The "emit" Lambda regenerates `sdg_world` data; bc-core's SAP reader pulls via OData on its own schedule. |
| Tenant | New tenant with slug `apex` (separate from `sandbox1` dev tenant). Demo URL: `apex.barecount.app/beyond`. |
| Profile | `apex-motors` profile in bc-sdg's 4200 server profile system. Auto-OEM industry. First storyboard-driven profile. Future pharma / FMCG / etc. follow the same pattern. |
| Period rollover | "Demo current date" is a moving variable (`today() − 30 days`). Latest visible period is always last completed month. Old periods archived to S3 after 24 months. |
| World-state continuity | Named entities (customers, vendors, materials, prices, FX) persist across cycles in `sdg_world` partitioned by `profile_code`. Story events evolve on top of stable world-state. |

**Tables to emit (priority by leverage)**:

1. `BKPF/BSEG` (universal posting headers + lines) — covers ~60% of finance KPIs
2. `T001/KNA1/LFA1/T030` (master data + chart of accounts) — segmentation, top-N customers/vendors
3. `BSID/BSAD/BSIK/BSAK` (AR + AP open + cleared items)
4. `VBRK/VBRP` (billing headers + lines) — revenue, gross margin
5. `MSEG/MBEW` (inventory movements + valuation) — COGS, DIO
6. `CSKS/COEP` (cost centers + CO line items) — cost accounting KPIs
7. `BSET` (tax line items) — tax/compliance KPIs
8. `GLT0/FAGLFLEXT` (GL totals + budget) — period roll-ups, budget variance
9. `BNKA/FEBRE` (banks + statements) — cash position, liquidity ratios
10. `USR02` + audit fields (after-hours, custom Z usage) — ERP Practices, Anomaly

**Story-event patterns (not fixed events)**: the storyboard's 7 events are *templates* that fire on schedules. Examples:

| Pattern | Cadence | Variation |
|---|---|---|
| Delinquent fleet customer | every 2–3 months | rotating named customer, ₹8–20 Cr range, 4–8 week arc |
| Cost-center overrun | every ~3 months | rotating cost-center, 10–20% variance, 1–2 month duration |
| Same-party AR/AP flag | persistent (structural) | xPress Logistics relationship; magnitude varies quarterly |
| After-hours JE | 1–2 per quarter | rotating user, varying account, ₹1–5 Cr range |
| Group consolidation delay | once per quarter close | varying BU, varying intercompany amount |
| MSME 45-day exposure | persistent baseline | magnitude varies; 1–2 actual breaches per quarter |
| Quarterly results variance | every quarter close | ±2–6% vs synthetic analyst consensus |

The named entities and amounts in the storyboard ("MetroLink State Transport Ltd, ₹15 Cr") are the **template** Rooth uses. The actual entity at any moment is whichever the pattern selected for the current window.

**Coherence requirements** (continuously enforced, not just at acceptance):

- Every posted invoice hits revenue + AR + tax (3 BSEG lines, same BKPF header)
- Every payment receipt clears an AR open item AND increments cash
- Cost of every shipped good hits COGS + decrements inventory at moving-average cost
- Period totals (GLT0) = sum of detail postings (BSEG) within the period
- DSO + DIO − DPO ties to CCC computed independently from base postings
- A coherence-monitor daemon runs hourly, re-evaluates the 8 storyboard assertions, alerts loudly on drift

**Exit criteria**: the apex tenant has 24 months of generated postings; the chain produces COs across all bound CCs; the 36 hero KPIs all produce; the 8 coherence assertions all tie out; the coherence monitor runs hourly with no failures over 7 consecutive days. Verified end-to-end via `devhub_readiness_dial tenant=apex` showing `producing: 36 / wouldProduceIfBound: 0`.

### Phase 2 — Catalog activation in apex tenant (1–2 weeks)

**Owner**: bc-core sessions  
**Deliverable**: the 36 hero KPIs from the storyboard all produce in the new `apex` tenant, with realistic numbers that tie out.

Steps:

1. Provision new tenant `apex` (slug = company slug; demo URL `apex.barecount.app/beyond`). Sandbox1 stays as the dev tenant.
2. Provision the 5 Cognito users on `@apex.in` with first-name logins and functional-role claims (meera/anil/suresh/pradeep/rajesh).
3. Identify which storyboard KPIs already have authored MCs and which need MC authoring (~30–60 missing MCs from the 652 MD-without-MC backlog, scoped to demo only).
4. Author missing MCs via the existing onboarding flow (SOPs in [Onboarding](../onboarding/)).
5. Bind via curated `POST /api/admin/readiness/tenant/apex/bind`.
6. Reconcile via `POST /api/schema-provisioner/nightly-reconcile`.
7. Re-evaluate via `evaluate-mc-for-tenant` per MC; capture rejection reasons for misses.
8. Iterate authoring fixes until every demo KPI is `producing` AND audits clean for the apex tenant.

**Exit criteria**: `devhub_readiness_dial tenant=apex` shows the 36 demo MCs in `producing` and `wouldProduceIfBound: 0`. The 8 storyboard coherence assertions tie out within rounding. Sandbox1 remains untouched as the dev tenant.

### Phase 3 — Beyond rewire with role-aware Rooth (1–2 weeks)

**Owner**: bc-portal session  
**Deliverable**: Beyond LHS pulls real activated metrics from apex; Rooth answers are grounded in live data and tuned to the logged-in user's functional role.

Today the Beyond LHS accordion is mock-fed. Phase 3 wires it to real bc-core endpoints AND adds role-aware Rooth behavior:

1. **LHS shape API** → `GET /api/t/metrics/catalog` (already shipped per HANDOFF-BEYOND-LOCK.md). Filter the LHS by the logged-in user's functional role (CFO sees all groups; AR Manager sees only AR + related; etc.)
2. **Per-metric monitor data** → `GET /api/t/metrics/:id/monitor` (pending — "highest-leverage unblock" in the bc-portal handoff)
3. **Type-first Rooth grounding** — typed questions get LLM-grounded answers, with the metric catalog and provenance as retrieval context, plus a role-specific system prompt
4. **Drag-first Rooth narration** — when a metric is dragged into focus, Rooth proactively narrates a per-metric briefing pack (top contributors, change drivers, related anomalies). This is precomputed or computed-on-focus per the storyboard's drag-first specification — separate engineering from type-first
5. **Role-aware vocabulary + filters** — Rooth's tone, the entities it names, and the LHS filter all derive from the user's functional-role claim in their Cognito profile

**Exit criteria**: the storyboard's 30-min role tour works end-to-end with all five users. Each user sees their own LHS view; each Rooth answer is grounded in apex's live data with click-through to the Trust Chain.

### Phase 4 — Demo Operations (1–2 weeks)

**Owner**: shared (bc-sdg + bc-core + bc-admin)  
**Deliverable**: monitoring, rollover, and cost management for the always-on demo.

Because the demo is permanent, Phase 4 builds the operational scaffolding that keeps it relevant without manual intervention:

1. **Coherence monitor daemon** — runs hourly, re-evaluates the 8 storyboard assertions, alerts to Slack/email on drift
2. **Period rollover automation** — monthly job advances "demo current date", archives the oldest period to S3, ensures the demo always shows the last 24 months
3. **Demo health dashboard** (bc-admin internal surface) — shows apex readiness dial (must always be 36/36/0), coherence assertions (all green), last-successful generation cycle, story-event recency per pattern
4. **Cost monitoring** — Lambda invocation count, EventBridge event count, apex tenant DB size; budget alarms at 80% / 100% of monthly cap

**Exit criteria**: 30 consecutive days of apex tenant in green state — readiness dial 36/36/0, coherence assertions all passing, no operator intervention required, costs within budget. After this, the demo is autonomous.

This phase replaces the previously-considered SFDC sales bridge (which is deferred to a later T2 phase, not blocking the CFO Pack demo).

## Coherence model — what the demo MUST get right

The "business ready / zero engineering" tagline argues for option (b): coherent rolled-up numbers, not just plausible-looking ones. A sharp customer audits the demo and finds inconsistencies if the numbers don't tie out.

The non-negotiable coherence assertions:

| Equation | Inputs | Frequency |
|---|---|---|
| Gross Profit = Revenue − COGS | Revenue (VBRK + GL), COGS (MSEG + GL) | M |
| Gross Profit Margin = Gross Profit / Revenue | computed | M |
| EBITDA = Operating Profit + Depreciation + Amortization | GL postings | M, Q |
| Working Capital = Current Assets − Current Liabilities | balance-sheet roll-up | W, M |
| CCC = DSO + DIO − DPO | three independent metrics, must agree | W, M |
| Current Ratio = Current Assets / Current Liabilities | balance-sheet roll-up | M |
| Quick Ratio = (Current Assets − Inventory) / Current Liabilities | balance-sheet roll-up | M |
| AR Aging buckets sum to Total Outstanding AR | per-customer aging | W |
| AP Aging buckets sum to Total Outstanding AP | per-vendor aging | W |
| Period total (GLT0) = sum of detail postings (BSEG) | per period, per account | M |

Each row above is a test bc-sdg must satisfy by construction, not by accident.

## Risks and open items

| Risk | Mitigation |
|---|---|
| bc-sdg coherent ledger is multi-week and unowned today | Phase 1 is the first explicit owner; storyboard lock (Phase 0) front-loads the design risk |
| 652 MD-without-MC authoring backlog | Scope Phase 2 to demo-relevant MCs only; treat the wider authoring backlog as separate |
| Rooth grounding (real LLM vs canned answers) | Start with canned answers tied to storyboard Q&A; LLM grounding is post-demo work |
| Type-mismatch tokens (~136 catalog-wide) | Pattern A retype already done. Patterns B/C (per-CF judgment) are only relevant for tenants with the affected source data; defer until a tenant needs those metrics |
| Demo coherence drift across iterations | Maintain a coherence-assertion test suite; run after every bc-sdg or catalog change |

Open follow-up tasks tracked in DevHub with tag `cfo-pack-demo` (to be linked once Phase 0 is filed).

## Operating cadence during phases

- **Per session**: open session → check the relevant dial (`devhub_readiness_dial`) → diagnose via `devhub_formula_token_audit` if numbers are wrong → fix → re-check → close
- **Per phase exit**: full audit re-run; coherence-assertion verification; demo walkthrough rehearsal
- **Weekly during build**: drift watch (audit reason categories shouldn't shift unexpectedly)
- **Per change**: don't trust engine "evaluation accepted" alone — the engine accepts numerically-coerced strings (e.g. `Number("2025") = 2025`) which the audit correctly flags as `type_mismatch`

## Cross-references

- ADR: [DEC-28b176 (D394) — Metric Readiness Model](../../../governance/adrs/ADR-28b176.md)
- ADR: [DEC-6cdceb (D361) — bc-portal three-surface split (Beyond)](../../../governance/adrs/ADR-6cdceb.md)
- Toolkit reference: [Metric Readiness Toolkit](../../../development/metric-readiness-toolkit.md)
- bc-portal handoff: `bc-portal/HANDOFF-BEYOND-LOCK.md`
- DataJetty deck: `OneDrive/BareCount/Business Presentations/DataJetty Platform.pptx`
