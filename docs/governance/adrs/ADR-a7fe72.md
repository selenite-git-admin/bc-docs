---
uid: DEC-a7fe72
title: "Finance Package v0 — scope lock, gold-universe planning SSOT, and execution sequence"
description: "Six operator locks defining Finance Package v0: narrow execution scope (AR invoice/billing + collections-flow + one revenue family), gold 1241-row universe re-homed to bc-docs-v3 as planning SSOT, average_days_to_collect grammar specimen, gold_only_unmatched quarantine, AP BCF-first later, D401 as-of early-design/later-build"
status: decided
date: 2026-06-11T06:16:29.441Z
project: bc-core
domain: metrics
subdomain: metric-portfolio
focus: governance
---

# Finance Package v0 — scope lock, gold-universe planning SSOT, and execution sequence

## Context

The ground survey measured the finance candidate space (1241 gold rows across 21 subfunctions; 894 exact-name seed matches carrying formulas) against chain reality (SC 30,368 / AC 30,367 active vs OC 1 / CC 1 — the throat; BCF rich on Customer Invoice / Customer Payment / Customer; only period_aggregate temporal semantics production-proven). A wide execution front would violate the locked concept-thread growth model (metric-demand-driven threads only, no speculative widening) and repeat the funnel-padding failure mode. A narrow front — invoice-grain flow metrics first — converts the existing BCF/OC/CC investment into green metrics fastest while the two structural unlocks (AP entities, as-of grammar) are designed in parallel rather than blocking. Re-homing the gold universe prevents the planning baseline from living solely inside a 772MB SQL dump; keeping it planning-SSOT (not runtime substrate) preserves the SERVICES-ONLY and seed→intake authoring discipline. The 347 unmatched rows are quarantined from authoring because most sample as APQC-style org-benchmark metrics that are not document-computable — executing them would produce placeholder semantics, violating the no-placeholders policy.

## Decision

Operator locks the six open decisions from the Finance Package v0 ground survey (SES-20c056, scripts/audit-output/finance-package-v0-ground-survey-2026-06-11.md), establishing the principle **"roadmap-wide, execution-narrow"**:

**Lock 1 — Gold universe re-homing (survey D1).** The 1241-row classified finance metric master (formerly metric.metric_definition, wiped in the 2026-06-09/10 resets; sole survivor = the COPY block in bc-core/docker/redesign/golden-snapshot-pre-reset-2026-06-09.sql) is re-homed as a governed, lightweight planning artifact: `bc-docs-v3/docs/assets/data/finance-gold-metric-definition-1241-2026-06-09.tsv` (header row prepended; data rows byte-identical to the dump COPY block; headerless-extract sha256 183996bb91ee3cce3457adebee314b33d0500e059d4a3c832c39aeb007776324) plus provenance chapter `docs/implementation/finance-package-v0-gold-universe.md`. This artifact is the **planning SSOT for the finance candidate universe — explicitly NOT runtime substrate**. It does not feed evaluation, binding, or any runtime path; authoring still flows exclusively through mcf.seed_metric → intake → M12 panel → governed gates.

**Lock 2 — Package v0 scope (survey D2): NARROW.** Finance Package v0 execution scope = (a) AR invoice/billing metrics, (b) AR collections-flow metrics where invoice-grain fields suffice, (c) ONE revenue/net-revenue family, (d) cash only if low-friction (Bank Statement / BSL BCF entities already exist). **Accounts payable is excluded from v0 execution** until the vendor-side BCF entity gap (Vendor, Vendor Invoice, Vendor Payment — currently zero entities) is first closed.

**Lock 3 — Grammar specimen (survey D3).** `average_days_to_collect` is the grammar probe for the date-diff / collection-timing family. **Panel + materialization-preflight ONLY** — no M12.5, no MC authoring. If grammar cannot express it, F1 shrinks honestly to the sum/count/ratio subset; no A-layer (SDG) compensation is permitted (Foundation Invariant I).

**Lock 4 — 347 unmatched gold rows (survey D4): triage, don't execute.** Gold rows with no exact-name seed match are catalogued as `gold_only_unmatched` in the planning artifact. They MUST NOT drive authoring until matched to seed/formula/source concepts or deliberately rewritten through the governed seed path.

**Lock 5 — AP timing (survey D5): parallel planning, later execution.** AP enters the roadmap now (planning/design), but execution is BCF-first — entity authoring precedes any OC/CC work — and follows the v0 core, not in parallel with it.

**Lock 6 — As-of packet timing (survey D6): early design, later build.** The D401/as-of grammar packet (open-item canonical + as_of evaluator semantics + BSID-class source) starts design soon because it unlocks the commercially critical DSO/aging family (~60–90 metrics), but it must NOT block F1. F1 harvests only what current grammar (period_aggregate + sum/count_distinct/divide + filters) can express, plus whatever the Lock-3 specimen proves.

**Execution sequence (operator-ordered):** (1) re-home gold artifact → (2) lock v0 scope from the survey matrix → (3) run average_days_to_collect specimen probe → (4) if pass, invoice-slice widening (OC/CC 3.0.0 successors, ~7 CI threads) → (5) payment slice (new OC + Customer Payment-grain CC) → (6) in parallel, design AP BCF/entity packet and D401 as-of packet.
