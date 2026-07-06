---
metric: sda-c3-cross-domain-metric-scope
metric_version: n/a
tenant: platform
source_system: n/a
work_type: adr-draft
session_uid: SES-594568
date: 2026-05-12
status: decision-pending
related_commits: []
related_tasks: []
related_adrs:
  - DEC-a17d0f
  - DEC-ecec75
  - DEC-ddbce8
related_mwrs:
  - 2026-05-12-c1-bf-cf-compatibility-amendment-draft-SES-594568.md
  - 2026-05-12-c2-mc-envelope-dedup-draft-SES-594568.md
  - 2026-05-12-pool1-trust-audit-46-producing-SES-594568.md
related_change_records:
  - CHG-28ab0c
repair_location: B
affected_boundary: tenant_binding
foundation_gate: passed
---

# Lane C C3 — Cross-domain metric scope / tenant applicability policy — ADR draft

> **Filed as [DEC-af8247](../../../../../governance/adrs/ADR-af8247.md) (D406) on 2026-05-12.**

> **Draft only. Not filed as ADR yet.** Small, decision-only ADR. Establishes the policy that determines whether an MC is applicable to a tenant based on the tenant's industry, before the binding is allowed. No code, no schema, no DBCP. After operator review, the substance is filed via `devhub_decision_record`. C3 is a sibling decision under MC Envelope Governance (the peer authority established by C2).

## 0. Stance

The Apex Pool 1 trust audit surfaced `mc__goppar` — "Gross Operating Profit Per Available Room", a hospitality-industry metric — bound for Apex, a tenant that is not in the hospitality industry. The cc_field_mapping is technically valid; the metric produces a number; the number is meaningless for Apex's business.

This is **scope drift at the binding layer**. The platform has no concept today of "this metric is applicable to this tenant" beyond the function/subfunction taxonomy (which is too coarse — every finance tenant has the `finance` function, including ones that are not hotels). Industry-specific metrics leak into deployments that don't operate in those industries because nothing prevents the bind.

C3 establishes the policy. **It does not implement.**

## 1. Context

### 1.1 What's there today (DEC-ddbce8 / D135 — Unified Business Domain Taxonomy)

The Business Domain Taxonomy already exists for primitives — BFs and BOs are classified by domain (finance, sales, operations, hr, etc.). This is the **function-level** classification.

What's missing:
- Per-MC **industry applicability** (which industries the metric is meaningful for — hospitality, manufacturing, banking, insurance, etc.).
- Per-tenant **industry declaration** (what industries the tenant operates in).
- A gate that compares the two at tenant binding.

The function/subfunction system in the MC envelope (`functionCode`, `subfunctionCode`) is the right grain for *what kind of metric this is* (a finance/AP metric vs a sales/order-management metric) — but it cannot answer *which industries this metric is meaningful for*. Many finance MCs are cross-industry; some are industry-specific (`mc__goppar` is finance/revenue_accounting but hospitality-specific).

### 1.2 Why this matters now

If C2's deduplication policy ships without C3, the Apex demo could include hospitality, manufacturing, or insurance MCs producing nonsense numbers — visible in dashboards, claimed as "metrics producing", but unrelated to Apex's actual business. The demo narrative degrades from "trustworthy metrics" to "lots of numbers, some meaningless".

The Pool 1 audit revealed at least one explicit cross-domain leak (`mc__goppar`). Others likely exist among the 46 producing MCs (e.g. `mc__gross_written_premium_gwp`, `mc__insurance_revenue_ifrs_17`, `mc__value_of_new_business_vnb` are insurance-specific MCs — Apex is not an insurer). C3 is the gate that prevents these from ever showing up in a tenant binding without explicit operator acknowledgement.

## 2. Decision

### §1 — Authority placement

Cross-domain scope governance lives under **MC Envelope Governance** (the peer authority established by C2), not under SDA. Reason: industry applicability is a property of the MC envelope (the contract), not of the primitives that constitute it. A revenue CF (`recognized_revenue`) is cross-industry; the MC that consumes it (`mc__insurance_revenue_ifrs_17`) is industry-specific. Industry scope is a metric-level concern.

The metric-seed-catalog (existing playbook surface) is where industry metadata is **declared** per MC at seed time. MC Envelope Governance is where the **gate enforces** it at tenant binding.

### §2 — Industry classification on MCs

Each MC envelope declares `applicable_industries TEXT[]` — a set of industry codes from a closed enum where the metric is meaningful.

Values:

- **`cross_industry`** — applicable to any tenant regardless of industry (the default for most finance MCs: revenue, AR balance, cost of goods sold, etc.).
- **Specific industry codes** — `hospitality`, `manufacturing`, `retail`, `banking`, `insurance`, `healthcare`, `energy`, `telecommunications`, `software_saas`, `professional_services`, `real_estate`, `transportation`, `pharmaceuticals`, `media_entertainment`, `agriculture`. (15 top-level industries — closed enum, extension via ADR.)
- **Multiple industries allowed** — e.g. `['hospitality', 'real_estate']` for a property-rental metric that fits both.

**Default for existing MCs (backfill rule):** any MC currently in the catalog without an explicit `applicable_industries` value is treated as **`cross_industry`** until per-MC review reclassifies it. This is the conservative default — it preserves existing bindings — but it also means the policy is **soft until backfill completes**.

The backfill is **out of C3's scope** — it's a metric-seed-catalog playbook task, MWR-driven, run on demand. C3 declares the framework; backfill is downstream work.

### §3 — Industry classification on tenants

Each tenant declares `tenant.industries TEXT[]` — the set of industry codes the tenant operates in. The column is **named here as a future DBCP** (DBCP-1h, not authored in this ADR).

Apex example: `tenant.industries = ['software_saas']` — Apex is a SaaS platform operating in software. Even though it has a finance function (every company does), it is not in hospitality or insurance.

Multi-industry tenants are supported via the array (e.g. a conglomerate with `['manufacturing', 'retail']`).

### §4 — Compatibility rule

A tenant binding of MC `mc_X` to tenant `T` passes the C3 gate if and only if:

```
'cross_industry' ∈ mc_X.applicable_industries
OR
mc_X.applicable_industries ∩ T.industries ≠ ∅
```

In plain English: either the metric is cross-industry, or there is at least one shared industry between the metric's scope and the tenant's industries.

Examples:

| MC | MC.applicable_industries | Tenant | Tenant.industries | Verdict |
|---|---|---|---|---|
| `mc__total_revenue` | `['cross_industry']` | apex | `['software_saas']` | **pass** |
| `mc__goppar` | `['hospitality']` | apex | `['software_saas']` | **reject** |
| `mc__insurance_revenue_ifrs_17` | `['insurance']` | apex | `['software_saas']` | **reject** |
| `mc__gross_written_premium_gwp` | `['insurance']` | apex | `['software_saas']` | **reject** |
| `mc__inventory_turnover` | `['manufacturing', 'retail']` | sandbox_retail | `['retail']` | **pass** (intersection non-empty) |
| `mc__rate_per_kwh` | `['energy']` | apex | `['software_saas']` | **reject** |

### §5 — Where the gate fires

| Gate point | Behaviour |
|---|---|
| **Tenant binding create** (`POST /api/admin/readiness/tenant/:slug/bind` and equivalent MCP `devhub_tenant_bind_metrics`) | Run C3 check for each MC in the binding request. Reject the binding row if §4 fails. **Block.** |
| **Pre-binding read** (`GET /api/admin/readiness/tenant/:slug/binding-candidates`) | Filter out MCs whose `applicable_industries` does not intersect tenant's industries. Operator never sees them as candidates in normal flow. |
| **MC envelope create** | No C3 check (industry is metadata, not a uniqueness/structure concern). |
| **MC version activate** | No C3 check (same reason). |
| **Existing bindings (backward compat)** | Grandfathered — existing bindings are not retroactively rejected. The C3 gate fires only at new binding writes. Read-only projection (next bullet) surfaces the existing scope violations. |
| **Read-only projection** (retroactive surface) | `GET /api/metric-envelope/cross-domain-violations?tenant=:slug` — lists bindings whose MC's `applicable_industries` do not intersect the tenant's industries. Operator-driven case-by-case adjudication. |

### §6 — Override path

Operator may force-bind a cross-domain MC with rationale ≥40 chars + auto-spawned follow-up task tagged `mc-scope-override`. Legitimate cases:

- **Cross-industry comparison.** A SaaS tenant wants to track a manufacturing-style inventory metric for an internal-services product.
- **Multi-industry tenant transition.** A tenant in the process of expanding into a new industry binds metrics in advance.
- **Demo / training tenants.** Non-production tenants used to demonstrate cross-industry metrics.

Override accumulation is visible in the binding-audit projection (sibling to C2's `mc_envelope_audit_record`). The override is recorded against the binding, not against the MC or the tenant — it's a one-binding decision.

### §7 — Compat mode (per-tenant, per-authority)

To support gradual rollout (per DEC-a17d0f §9 Phase 2 pattern), the C3 gate runs in one of two modes per tenant:

- **`shadow`** (default initially): the C3 check runs at binding-create, but failures are logged (visible in projection + override counter) without blocking. Operator can see the cost of moving to block.
- **`block`** (target state): C3 failures are hard rejections requiring override.

The mode is held in a tenant-level column, **independently addressable per authority**. Two columns (or one column with two named modes per the implementation's choice):

- `sda_preflight_mode TEXT` — governs SDA Phase 2 gates (G9 / G10 / G11) at primitive-reference authoring paths.
- `mc_scope_mode TEXT` — governs the C3 cross-domain scope gate at tenant binding.

Each flips independently. The operator UI may surface them together for convenience, but rollout is **not coupled**: a tenant can be in `block` mode for SDA preflight while remaining in `shadow` mode for C3 cross-domain (or vice versa). This avoids the failure mode where C3 readiness blocks SDA enforcement, or where SDA Phase 2 maturity drags C3 into premature block-mode. The two authorities ship and roll out independently.

Implementation detail (e.g. one column with `{sda: 'shadow', mc_scope: 'shadow'}` JSON or two separate `TEXT` columns) is left to the future DBCP. The **policy** decided here is that the two switches are independent.

### §8 — What Phase 1 ships and what is deferred

**Phase 1 C3 scope (minimum):**

- `applicable_industries TEXT[]` column on `metric_definition` and/or `metric_contract_version` (future DBCP-1i; not authored in this ADR).
- `industries TEXT[]` column on `tenant` (future DBCP-1h; not authored in this ADR).
- `master.industry` table seeded with the 15-value closed enum from §2 (future DBCP-1j; not authored in this ADR).
- The tenant-binding gate (§5) wired into the existing binding service.
- The pre-binding-candidates filter (§5).
- The retroactive read-only projection (§5).
- The override mechanic (§6).

**Deferred:**

- Bulk backfill of `applicable_industries` on existing MCs (operator-driven MWR sweep; not auto).
- Bulk backfill of `tenant.industries` (small — Apex + the dev tenants; operator-driven).
- Industry-taxonomy expansion beyond 15 top-level industries (future ADR if/when needed).
- NAICS / GICS alignment (out of scope; bc_industry is its own controlled vocabulary, not aligned to external standards in v1).
- Sub-industry granularity (e.g. "luxury hospitality" vs "budget hospitality"). Closed enum at the top level only; sub-industry is a future extension if evidence demands it.

## 3. Options Considered

**Option A — Continue without scope governance.** Status quo. Rejected per §1.2 — `mc__goppar` and similar industry-specific MCs leak into Apex's producing dial unchecked.

**Option B — Extend function/subfunction to carry industry.** Repurpose `subfunctionCode` to encode industry (e.g. `finance/revenue_accounting/hospitality`). Rejected because (i) subfunction is already an established categorization with its own playbook, (ii) industry is orthogonal to function, (iii) some industries cut across functions (e.g. `hospitality` applies to both finance/revenue_accounting and operations/inventory).

**Option C — Per-tenant whitelist of MC UIDs.** Tenant declares which MC UIDs it wants. Rejected because (i) doesn't scale (376 MCs, each tenant would manage a list), (ii) doesn't surface the *why* of inclusion/exclusion, (iii) can't enforce platform-wide policy (a manufacturing tenant could whitelist hospitality MCs by accident).

**Option D — Industry as a property of the MC + intersection check at bind (chosen).** The metric's industry scope and the tenant's industries are both declared metadata; the gate checks intersection. Clean separation of concerns; metadata travels with the entities; gate is a single intersection check.

**Option E — AI-driven applicability inference.** Use bc-ai to predict whether an MC is meaningful for a tenant. Rejected as deterministic governance — AI is advisory per the SDA principle; cross-domain scope is a deterministic structural rule.

## 4. Consequences

### Positive

1. **Industry-specific MCs cannot leak into non-applicable tenants** — `mc__goppar` could not bind to Apex without an explicit override.
2. **Demo narratives become defensible** — "Apex is producing 46 MCs" filtered to applicable-to-software-saas yields a smaller but cleaner set.
3. **Closed enum keeps the taxonomy disciplined** — 15 top-level industries forces explicit classification rather than free-form drift.
4. **Backward compatible by default** — existing bindings grandfathered; default `cross_industry` on un-backfilled MCs preserves current behaviour during rollout.
5. **Per-tenant compat mode** — operator can opt each tenant into block mode independently, on a schedule.
6. **Backfill is operator-controllable** — not auto-scoped; each industry-specific MC is reclassified one at a time with rationale.

### Negative

1. **15-value closed enum is opinionated.** Industries that don't fit cleanly (e.g. multi-sector conglomerates, gig economy, fintech-at-the-edges) require an ADR amendment to expand. Mitigation: 15 covers the bulk; expansion is cheap (small ADR).
2. **Backfill is real labor.** Per-MC industry classification requires governing-source review for 376 MCs; not all are obviously cross-industry. Acceptable as an open-ended operator task; the C3 gate doesn't require complete backfill to ship — un-backfilled MCs default to `cross_industry`.
3. **Multi-industry tenants are slightly complex.** Tenants spanning multiple industries (conglomerates) have larger `industries` arrays and broader applicability surfaces. Acceptable — the array semantics are clean (any-intersection passes).
4. **Some legitimate cross-industry use will require overrides.** A SaaS company benchmarking against retail metrics. Acceptable; the override path handles it.

### Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Backfill lags and the gate's effective enforcement is weak | High | Medium | Per-tenant compat mode lets operator hold tenants in `shadow` mode until backfill of MCs they'd bind is complete; the gate is useful even partial |
| Operator override becomes the path of least resistance | Medium | Medium | D366-style ≥40-char rationale + auto-spawned follow-up task; aggregate override count visible per-tenant |
| Industry enum becomes too coarse | Medium | Low | Sub-industry extension is a future ADR; v1 ships at 15 |
| Multi-industry tenant's array becomes too permissive | Low | Low | Array intersection is the rule; tenants with many industries have broader applicability — that's correct behaviour, not a bug |
| Closed-enum bikeshedding stalls the ADR | Medium | Low | The 15 values are a starting point grounded in NAICS top-level sectors + observed industry-specific MCs in the existing catalog; debate is bounded |

## 5. Decision boundary

**Decided here:**

- Authority: MC Envelope Governance (peer to SDA, established by C2).
- Per-MC: `applicable_industries TEXT[]` from the 15-value closed enum.
- Per-tenant: `tenant.industries TEXT[]`.
- Compatibility rule: intersection-or-cross_industry passes (§4).
- Gate fires at tenant binding create + pre-binding candidate read (§5).
- Default for un-backfilled MCs: `cross_industry`.
- Override mechanic: D366-style.
- Compat mode: per-tenant shadow/block (shared mechanism with SDA Phase 2).
- Industries are a closed enum, extension via ADR.

**Not decided here:**

- The exact schema and table placement of `applicable_industries` (future DBCP-1i).
- The exact schema for `tenant.industries` (future DBCP-1h).
- The exact schema for `master.industry` (future DBCP-1j).
- Bulk backfill policy and execution (operator-driven MWR sweep).
- Sub-industry granularity (future ADR if evidence demands).
- NAICS / GICS alignment (out of scope v1).
- Whether industry applies to BFs/BOs (no — primitives are cross-industry; industry is a metric-level concern).

## 6. References

- **DEC-a17d0f** (D403) — SDA umbrella ADR. C3 shares the compat-mode mechanism with SDA Phase 2.
- **DEC-ecec75** (D068) — Metric architecture. The MC envelope is where `applicable_industries` lives.
- **DEC-ddbce8** (D135) — Unified Business Domain Taxonomy. C3's industry taxonomy is a *peer* of the existing domain taxonomy (functions); not a replacement.
- **C2 draft** — [MC envelope deduplication](2026-05-12-c2-mc-envelope-dedup-draft-SES-594568.md). The peer authority C3 lives under.
- **Evidence MWRs:**
  - [Pool 1 trust audit](../../../../audits/onboarding/2026-05-12-pool1-trust-audit-46-producing-SES-594568.md) — `mc__goppar`, `mc__gross_written_premium_gwp`, `mc__insurance_revenue_ifrs_17`, `mc__value_of_new_business_vnb` observed in Apex producing surface.
  - [Apex Phase 0 readiness walkthrough](2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md) §A4 — cross-domain CFs flagged as governance scope #3.

## 7. Operator review checklist

- [ ] §1 — authority placement under MC Envelope Governance (C2's peer authority) accepted
- [ ] §2 — `applicable_industries` per-MC, 15-value closed enum accepted
- [ ] §3 — `tenant.industries` per-tenant accepted
- [ ] §4 — intersection-or-cross_industry compatibility rule accepted
- [ ] §5 — gate at tenant binding create + pre-binding candidates filter accepted
- [ ] §5 — existing bindings grandfathered accepted
- [ ] §6 — D366-style override mechanic accepted
- [ ] §7 — per-tenant shadow/block compat mode (shared with SDA Phase 2) accepted
- [ ] §8 — Phase 1 scope (gate wiring + projection + override) accepted; bulk backfill deferred
- [ ] 15-industry top-level closed enum reviewed; expand list if needed before filing
- [ ] Approved for filing as ADR: _yes / no_

## 8. After this draft is approved

If the operator decides to close Lane C and file all three ADRs (C1 amendment, C2, C3) before Phase 1 implementation:

1. File C1 as amendment to DEC-a17d0f via `devhub_decision_record` per the C1 §14 plan.
2. File C2 as new ADR (MC Envelope Governance + dedup policy).
3. File **this ADR** (C3) as the third sibling. Title: "Cross-Domain Metric Scope and Tenant Applicability Policy". Domain: `contracts`. Subdomain: `mc-envelope`. Focus: `tenant-applicability`. `related_adrs:` should include the C1 and C2 UIDs once they're known.

After filing, the three ADRs collectively close the four Lane C governance scope gaps (G11 BF-CF compatibility, MC envelope dedup, cross-domain scope, plus the deferred fourth — engine `compute__derived` governance — named but not addressed in this wave). Phase 1 implementation can then proceed with a stable Lane A + Lane C governance baseline.
