---
uid: DEC-c012c0
title: "Metric Contract grammar v1.1 — per-variable temporal input selection"
description: "Adds optional per-variable input_selection grammar (over_period, over_trailing_window) with closed-string anchor expressions and version-gated engine behavior; deliberately excludes at_period_end and balance-metric semantics."
status: superseded
date: 2026-05-11T02:00:03.525Z
project: platform
domain: metric
subdomain: metric-grammar
focus: schema
superseded_by: DEC-83fda0
---

# Metric Contract grammar v1.1 — per-variable temporal input selection

## Rationale

Today's Metric Contract grammar (v1.0) ties every variable's temporal interpretation to the metric's evaluation_period. This is sufficient for per-period flow metrics but cannot express realistic balance metrics like DSO/DPO/DIO whose numerator is open-at-anchor and whose denominator is a trailing window. Attempting to express such metrics under v1.0 forces compensation in lower layers (SDG tuning, fact-side filters, read-model masking) — all Foundation-prohibited. Extending the grammar at Layer B (contract) and Layer D (evaluation boundary) is the only Foundation-compliant fix. However, balance-side honesty also requires Layer A/C work (open-item or bitemporal canonical semantics) that this ADR deliberately defers to a successor ADR. Phase 1 ships the grammar plumbing and a flow-only pilot; DSO v2 waits.

## Context

The Metric Contract (MC) grammar v1.0 declares one temporal frame per metric via `evaluation_period`. Each variable is implicitly evaluated against COs whose grain matches that period. This is correct for *per-period flow* metrics (revenue this period, units sold this period) but is *incorrect* for metrics whose inputs need different temporal frames:

- **Days Sales Outstanding (DSO)** wants an AR balance *as of period end* (an anchor in time) divided by *trailing-90-day credit sales* (a window) × 90.
- **Days Payable Outstanding (DPO)**, **Days Inventory Outstanding (DIO)**, **inventory on hand**, **cash position** — all share this shape: one balance-style numerator, one flow-style denominator over a different window.

Under v1.0 grammar, each variable is forced into the same `evaluation_period` frame. The result for DSO is mathematically capped at `per-row AR/invoice ratio × period_days` — typically 30–38 days regardless of underlying tenant behavior. This is the Apex-shaped grammar that drove this design conversation.

The compensating fixes that were explicitly rejected (Foundation Invariant Check, all anti-Foundation):
- Tuning the SDG to land DSO at a target storyboard value (Invariant I — meaning produced at source layer).
- Adding a read-time filter in `FactReaderService` or an admin endpoint to reshape the value at the surface (Invariant VI — evidence inferred not emitted).
- Hand-editing fact-table rows to back into a target number (Invariant III — state mutated).
- Authoring new temporally-named CFs (`outstanding_receivables_at_period_end`, etc.) to encode time semantics into the registry (CF taxonomy fragmentation; meaning belongs at the variable layer, not the CF layer).

The Foundation-compliant fix is at Layer B + Layer D: the **contract** declares per-variable temporal selection, and the **engine** honors it. That is this ADR.

## Decision

Introduce **Metric Contract grammar v1.1**, an additive, version-gated extension that adds an optional `input_selection` block to each entry of `variables[]`. The v1.0 contracts remain valid and untouched. The new grammar is meta-schema v1.1; a contract declares its grammar version via the `$contract` URI it references.

### Phase-1 grammar additions

A variable may carry an optional `input_selection` block:

```json
{
  "name": "credit_sales",
  "canonical_field": "total_credit_sales",
  "aggregation": "SUM",
  "input_selection": {
    "kind": "over_trailing_window",
    "anchor": "grain.fiscal_period.end",
    "window_days": 90
  }
}
```

Supported `kind` values in phase 1:

1. **`over_period`** — the default v1.0 behavior, made explicit. Selects COs whose grain matches the metric's `evaluation_period`. Equivalent to omitting the block entirely; included as the explicit form for clarity.
2. **`over_trailing_window`** — selects COs whose `posting_date` (or equivalent admission-time anchor declared by the CC) falls in `[anchor − window_days, anchor]`. `window_days` is required and integer-positive. `anchor` is a closed-grammar string (below).

Explicitly **NOT** supported in phase 1 (deferred to the successor ADR):

- **`at_period_end`** — would require selecting only *open* positions (open AR, open AP, on-hand inventory) as of the anchor. Today's canonical contracts (`cc__receivable_hdr`, `cc__payable_hdr`, etc.) are append-only and have no clearing event that produces a separate cleared-item CO. A simple `posting_date ≤ anchor` selector against these CCs produces *cumulative-through-anchor*, not *open-at-anchor* — mathematically distinct. Shipping `at_period_end` against today's CCs would be the "grammar the engine cannot honestly evaluate" anti-pattern. The meta-schema v1.1 enum *omits* `at_period_end`; the engine v1.1 path rejects it deterministically; no contract author can write a v1.1 MC that asks for it.

### Anchor expression grammar

`anchor` is a **string** matching the closed regex grammar:

```
<scope>.<key>.<edge>      where <scope> ∈ {grain, evaluation_period}
                                <key>   = a grain key name (or omitted when scope = evaluation_period)
                                <edge>  ∈ {start, end}
```

Examples: `"grain.fiscal_period.end"`, `"evaluation_period.end"`, `"grain.fiscal_quarter.start"`.

Rationale for string-not-structured-object: terser, validator-friendly via regex, avoids object-shape drift. The engine parser tokenizes the string internally; the wire form stays a single field.

### Engine behavior (version-gated)

The metric evaluation engine reads the bound MC's grammar version (resolved from the `$contract` URI). For v1.0, the engine takes the existing path unchanged. For v1.1, the engine:

1. For each variable, resolves the variable's `input_selection.kind`. Absence is treated as `over_period`.
2. For `over_trailing_window`, resolves the anchor expression to a concrete date via `FiscalCalendarService` (see Layer-D dependency below), then selects COs whose admission-time anchor field (declared by the bound CC) lies in `[anchor − window_days, anchor]`.
3. Records per-variable `selected_co_ids` in `inputReferencesJson` (Invariant IV — references explicit).
4. Emits per-variable `input_selection` evidence in the metric snapshot, including resolved anchor date, window bounds, and selected count. Rejections carry an `input_selection` block in `rejectedGroups`; failure to resolve an anchor produces a named check `anchor_unresolved:<expression>`.
5. Replay against frozen DB state produces a new `metric_evaluation_id` but identical `metricValueJson` (Invariant V — non-replayable, deterministic).

### Layer-D dependency: FiscalCalendarService.resolveByLabel

The engine already receives `envelope.evaluationPeriod` (a string period label) at metric-call time. To resolve `evaluation_period.{start, end}`, the engine needs the period's bounds. Phase 1 adds a small extension to `FiscalCalendarService`:

```
resolveByLabel(period_label: string, legal_entity_code: string)
  → { start_date: ISODate, end_date: ISODate, fiscal_period_code: string }
```

`envelope.evaluationPeriod` continues to be set at metric-call level (today's behavior); promoting it into the MC body is explicitly **not** part of phase 1 — it would entangle the contract with caller-side concerns.

### Multi-legal-entity grain — engine-side resolution

The meta-schema does **not** constrain grain shape for multi-LE cases. When a grain group carries `legal_entity_code`, the engine fetches the per-LE fiscal calendar via tenant `dim_legal_entity → fiscal_calendar_config` (per the D364 fiscal-calendar stack) and applies it to anchor resolution. Groups without `legal_entity_code` fall back to the tenant default. If a grain group folds multiple LEs together (a binding/grain-shape choice), the engine raises a deterministic `anchor_ambiguous_legal_entity` rejection rather than guessing — Foundation-clean failure, not a silent average.

### Tenant opt-out — no new grammar needed

Tenants opt out via the existing `tenant.contract_binding` version-pinning: a tenant that wants v1.0 per-period semantics keeps its binding on the v1.0 MC version; v1.1 is offered alongside as a separate MC version on the same `metric_contract_id`. No new tenant flag, no new contract field. Consistent with Invariant III — new meaning is a new version, never an in-place edit.

### Evidence and observability (additive only)

Phase 1 additions to evidence are strictly **additive**:

- `inputReferencesJson` gains per-variable `selected_co_ids` arrays.
- `metricValueJson.lineage` (or equivalent block) gains per-variable `input_selection` records with `kind`, resolved `anchor_date`, `window_start`, `window_end`, `selected_count`.
- `rejectedGroups[].checks[]` gains `input_selection`-scoped failure names: `anchor_unresolved:<expression>`, `anchor_ambiguous_legal_entity`, `window_days_invalid`, `kind_not_supported_in_version`.

No existing evidence field changes meaning. Replay determinism is preserved (Invariant V).

### Phase-1 pilot — flow-only metric, explicitly NOT DSO

The phase-1 pilot is a **flow-only metric** (e.g., trailing-twelve-month revenue or trailing-90-day credit sales) where `over_trailing_window` adds end-to-end value and neither input requires open-item semantics. **DSO v2.0.0 is not the phase-1 pilot.** Realistic DSO is structurally blocked on upstream Layer A/C work the successor ADR must deliver (open-item canonical semantics). Shipping DSO v2 with the v1.1 grammar but no open-item CC would re-introduce the cumulative-through-anchor anti-pattern at the canonical layer instead of the metric layer.

### Phase 1 is necessary but not sufficient for realistic DSO

This ADR delivers a *necessary* precondition for realistic DSO — the grammar to express "AR balance at period end" / "credit sales over trailing 90 days." It is **not sufficient.** Realistic DSO additionally requires:

- Open-item or bitemporal canonical semantics on `cc__receivable_hdr` (or a sibling open-item CC family) so that `outstanding_receivables_amount` actually means *open* AR at the anchor rather than *cumulative-posted* AR. Without this, the numerator is wrong regardless of grammar.
- The CC mapping audit on `cc__invoice_hdr` to additionally produce `net_credit_sales` (currently only `total_credit_sales` is mapped). The phase-1 grammar can be used with `total_credit_sales` as an explicit approximation.

Both items are Layer A/C audit items, ungated by this ADR, and named for the successor design conversation.

### CF reuse — no new canonical_field entries

The existing CF registry already carries every semantic role realistic DSO will need: `outstanding_receivables_amount`, `customer_outstanding_ar_balance`, `total_credit_sales`, `net_credit_sales`, `days_sales_outstanding`, `days_in_period`, plus others. CFs remain temporally-neutral semantic identifiers; temporal interpretation is decided at the variable layer via `input_selection`. No CF taxonomy fragmentation.

### Successor ADR — required, named, deferred

A successor ADR is **required** before realistic DSO (or any balance metric: DPO, DIO, inventory-on-hand, cash position) can be honestly authored. Working name:

> **Open-item / as-of canonical semantics — temporal projection for balance metrics**

Three candidate mechanisms named for the successor's Foundation Gate (none chosen here):

1. **Separate open-item CC family** — e.g., `cc__receivable_open_item` whose COs *are* open positions; clearing emits a cleared-item CO in a separate family.
2. **Clearing-by-supersession** — clearing is a new CO version on the existing CC whose Lineage references the original; the engine resolves "open at anchor" via the supersession chain.
3. **Bitemporal columns on existing CC** — add `effective_from` / `effective_to`; selection becomes `effective_from ≤ anchor < effective_to`.

Blast radii differ materially. The successor ADR will pick one (or a hybrid) after a separate Foundation Gate. This ADR's phase-1 grammar deliberately omits `at_period_end` so that no consumer can write a contract that depends on the unresolved upstream semantics.

## Scope

### In scope

- Metric meta-schema v1.1 as a *concept* — new schema file authoring is a Stage 2 deliverable, not a sub-decision of this ADR.
- Optional `variables[].input_selection` body-key grammar.
- Phase-1 `kind` enum: `over_period`, `over_trailing_window`.
- Closed-string `anchor` expression grammar (regex-enforceable).
- Engine version-gated behavior driven by the bound MC's `$contract` URI.
- `FiscalCalendarService.resolveByLabel` Layer-D dependency.
- Additive evidence fields for window bounds, resolved anchor, selected CO ids.
- Phase-1 pilot is a flow-only metric.

### Out of scope

- `at_period_end` selector. Excluded from the v1.1 enum; deferred to the successor ADR.
- Realistic DSO. Structurally blocked on successor-ADR open-item CC work.
- Open-item / as-of balance metrics generally (DPO, DIO, inventory-on-hand, cash position).
- DSO v2.0.0 authoring.
- Open-item / clearing / bitemporal canonical-contract work (named as the successor ADR).
- SDG tuning to chase storyboard numbers.
- Fact-side or read-model compensation for grammar gaps.
- Promotion of `envelope.evaluationPeriod` into the MC body.
- Any in-place edit of existing v1.0 MC versions (Invariant III).

## Consequences

**Positive:**
- The grammar can express the *flow* side of balance metrics honestly today (trailing windows), unlocking real flow-only metric work without waiting for the successor ADR.
- The Foundation-compliant repair location (B + D) is enforced by the meta-schema enum — no contract author can write `at_period_end` until the upstream CC work lands.
- Existing v1.0 MCs and bindings continue to evaluate unchanged; no migration, no breaking change.
- Per-variable `selected_co_ids` in lineage strengthens Invariant IV evidence for all v1.1 metrics.

**Negative / accepted costs:**
- Engine path now version-dispatches on grammar version, slightly raising engine complexity. Mitigated by single `evaluateWithGrain` entry with shared aggregation code and shared test suite.
- `inputReferencesJson` grows by per-variable arrays. If size becomes a concern at scale, a hash-and-archive strategy is available; not phase-1 critical.
- DSO storyboard improvement is gated on the successor ADR, not this one. The storyboard's "38 → 47" arc is *not* delivered by phase 1 alone.

**Risks (full table in the draft):**
- Engine path divergence over time (R1) — mitigated by shared aggregation code.
- Anchor resolution failures hiding as silent rejections (R2) — mitigated by named evidence checks.
- `at_period_end` shipping with a dishonest fallback (R3) — mitigated by enum-level exclusion.
- `Date.now()` regression in engine code (R6) — mitigated by a CI grep test.

## Implementation plan (Stage 2 onward — gated on this ADR landing)

1. Author `metric-v1.1.schema.json` adjacent to v1.0; v1.0 remains unchanged.
2. Add `FiscalCalendarService.resolveByLabel` and unit tests.
3. Add version-gated engine path with shared aggregation; per-variable selector logic; deterministic anchor resolution; named rejection checks.
4. Add a CI grep test asserting no `Date.now()` in engine code on the resolve-anchor or select-CO branches.
5. Author the flow-only pilot MC at v1.1 (e.g., trailing-twelve-month revenue). Validate end-to-end against demo-selenite or successor pilot tenant.
6. Update `bc-docs-v3/docs/foundation/the-contract-grammar.md` body-key list for the metric family; update `bc-docs-v3/docs/onboarding/metric-contract-creation.md`.
7. Open the successor ADR conversation: *Open-item / as-of canonical semantics — temporal projection for balance metrics*. DSO v2.0.0 work depends on its outcome.

## References

- Draft: `barecount-devhub/.claude/adr-draft-realistic-dso.md`
- Metric Work Record: `bc-docs-v3/docs/onboarding/metric-work-records/days-sales-outstanding/2026-05-11-grammar-design-SES-b7db1a.md`
- Playbook: `bc-docs-v3/docs/onboarding/metric-workstream.md` (Foundation Gate, Balance vs Flow temporal discipline §8, anti-patterns §10)
- Fiscal calendar stack: D363 / D364 / D365
- Six Foundation Invariants and Repair-location A–F: `CLAUDE.md` Foundation Invariant Check section
- Session: `SES-908735` (this ADR promotion), preceded by `SES-b7db1a` (grammar design study).

