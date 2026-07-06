---
metric: mc__days_sales_outstanding
metric_version: n/a
tenant: platform
source_system: n/a
work_type: grammar-extension
session_uid: SES-b7db1a
date: 2026-05-11
status: decided
related_commits:
  - 4b52785  # docs: add foundation invariant check to CLAUDE guidance
  - f7faf98  # docs: add metric workstream playbook
related_tasks: []
related_adrs:
  - DEC-c012c0                  # D400 — Metric Contract grammar v1.1 (proposed) — layered pair, not superseded
  - DEC-1db1c7                  # D401 — Open-item / as-of canonical semantics (proposed) — successor; provides upstream open-item CC family
related_change_records:
  - CHG-2c2734                  # SES-b7db1a plan-side (bc-core) — initial DSO grammar design
  - CHG-29c9bb                  # SES-bedcef plan-side (bc-core) — Stage 1 revision under playbook
repair_location: B+D
affected_boundary: metric_evaluation
foundation_gate: passed
---

# Days Sales Outstanding — grammar-extension design — 2026-05-11

> **This record is orientation memory, not contract authority.** It links back to canonical artifacts (DevHub session change records, ADRs once promoted, commits, evidence rows, and contract versions). If this record conflicts with any of those, the canonical source wins and this record is corrected to match. See `metric-work-records/README.md` for the directory's authority framing.

## Summary

Designed (not implemented) a Metric Contract grammar v1.1 extension that adds optional per-variable temporal selection (`input_selection`) to admit `over_trailing_window` for flow measures. Reviewed against the playbook's balance-vs-flow rule (§8) and concluded the design must explicitly exclude `at_period_end` from the phase-1 enum: today's append-only Canonical Contracts have no clearing semantics, so the naive `posting_date ≤ anchor` selector would produce cumulative-through-anchor — mathematically distinct from open-balance-at-anchor — under a misleading kind name. Phase 1 ships flow-only temporal selection; the realistic-DSO numerator side is gated on a successor ADR that delivers open-item / clearing / bitemporal semantics on the upstream CC. The ADR draft lives at `barecount-devhub/.claude/adr-draft-realistic-dso.md`; this record orientates a future operator to that draft and the review that revised it.

## Foundation Gate Result

- **Repair location:** B+D (Metric Contract grammar + Metric Evaluation engine).
- **Affected boundary:** metric_evaluation.
- **Six-invariant pre-check:** pass on all six. Invariant IV (explicit references) is load-bearing — every anchor is contract-declared (`grain.<key>.{start,end}` or `evaluation_period.{start,end}`); no `Date.now()`, no implicit "latest." Invariant V (non-replay) is structurally satisfied — new evaluations produce new snapshots; selection is deterministic from contract + grain group + preserved CO state.
- **Why not other layers:**
  - A (source / SDG): SDG is honest; tuning it to alter the metric number would produce meaning at the source layer (Invariant I). Rejected.
  - B-only: grammar alone is unreachable without engine evaluation; the work is B+D, not pure B.
  - C (mapping / binding): `cc_field_mapping` and `metric_binding` are sound; the gap is in semantic vocabulary the MC can express, not in the routing.
  - D-only: engine alone is invisible without grammar to invoke it; B+D, not pure D.
  - E (storage / projection): fact tables faithfully store what the engine produced; no projection trick fixes a grammar gap.
  - F (read model / diagnostics): a read-side rewrite would infer meaning at the surface, violating Invariant I.
- **Override?** none. Phase-1 stays within Foundation by deferring `at_period_end` until the CC layer can honestly carry open-item semantics.

## Metric Logic Studied

- **Formula / intended calculation:** for realistic DSO — `DSO = (open_AR_balance_as_of_period_end / credit_sales_over_trailing_window) × window_days`. For phase-1 (no `at_period_end`) — only the denominator can be windowed; numerator stays per-period-cumulative, which yields a *grammar-extended but still not realistic* DSO. That partial form is intentionally not DSO v2.
- **Numerator:** semantically *open accounts receivable balance at a point in time* (period_end). Today's `mc__days_sales_outstanding` v1.2.0 numerator is per-period cumulative AR sum, which is mathematically distinct.
- **Denominator:** semantically *credit sales over a defined window* (trailing 90 days for the classic CFO definition, or "the current fiscal_period" for a monthly form). Today's v1.2.0 denominator is per-period credit sales sum, an implicit special case of "window = current fiscal_period."
- **Grain:** `[company_code (business_field), fiscal_period (business_field)]`. Phase-1 grammar adds the option to declare temporal-window inputs *within* this grain — the grain itself does not change.
- **Temporal semantics:** mixed-input metric. Numerator is *balance* (point-in-time anchor). Denominator is *flow* (window). The two have different temporal types — exactly the case the new grammar exists to express.
- **Unit semantics:** days. `window_days` integer on the denominator selector replaces the role today's I3 constant plays in v1.2.0's formula.
- **Threshold semantics:** four bands (excellent ≤ 30, good ≤ 45, warning ≤ 60, critical > 60), `direction_code: lower-is-better`. Carry over to v2.0.0 when authored.
- **Balance vs flow classification:**
  - I1 (open AR): **balance** — requires upstream open-item / as-of semantics; not phase-1 expressible.
  - I2 (credit sales): **flow** — phase-1 expressible via `over_trailing_window`.
- **Required upstream CCs:** `cc__receivable_hdr` for the AR balance side; `cc__invoice_hdr` for the credit sales side. Both versions 1.1.0 active.
- **Required CFs:** `outstanding_receivables_amount` (semantic open AR; production gap — see Assumptions), `total_credit_sales` (phase-1 approximation) or `net_credit_sales` (successor-quality), `days_sales_outstanding` (output), `days_in_period` (constant, possibly migrated to `window_days` on the variable).
- **Required source-state assumptions:** the source system must emit AR-debit postings with reliable `posting_date`. For realistic DSO, the source must also emit clearing events (or the CC must compose open-vs-cleared via supersession or bitemporal columns). The SDG emits posting dates honestly; clearing events are not modeled today, which is the precise gap that blocks the numerator.

## Assumptions

- **Business assumptions:** classic DSO is "how many days of credit sales equivalent are tied up in open AR". Both monthly (window = period_end → period_end, 30 days) and trailing-90 (window = period_end − 90 → period_end, 90 days) are valid; the storyboard's "DSO 47 days" implies the trailing form.
- **Source-system assumptions:** today's `sap_ecc` reader emits invoice + AR-debit postings from BSID. It does **not** emit clearing rows. Real SAP carries clearing in BSAD; today's reader chain does not consume BSAD or any equivalent for `cc__receivable_hdr`. This is the assumption the grammar gap rests on.
- **Contract/mapping assumptions:** `cc__receivable_hdr`'s `receivable_hdr_amount → outstanding_receivables_amount` mapping (rule `sum`) claims to produce open balance, but on an append-only CC with no clearing, it actually produces cumulative-through-anchor. The CF name is right; the CC's current production does not yet match it.
- **Tenant/onboarding assumptions:** any tenant binding the eventual DSO v2 must have an active FiscalCalendarService configuration that resolves period_end deterministically. Apex has this for company_code 1100.
- **Engine/runtime assumptions:** `MetricEvaluationEngine.evaluateWithGrain` accepts version-gating via `envelope.$contract`. v1.0 contracts must continue to run bit-identical; v1.1+ engages the new selector path. `FiscalCalendarService.resolve(date)` is deterministic for any tenant + calendar + date triple.

## Rejected Interpretations

- **`posting_date ≤ anchor` as open-AR semantics.** Rejected because `cc__receivable_hdr` is append-only; a paid invoice's AR-debit CO is not removed or netted. The selector returns cumulative-through-anchor, not open-at-anchor. (Playbook §8 balance-vs-flow rule; Foundation Invariant I — meaning produced at the canonical boundary, not at metric read time.)
- **Tuning SDG arrears decay or interest accrual to make DSO land at a storyboard number.** Rejected per the Foundation hard rule: producing meaning at the source layer to satisfy a metric violates Invariant I. The metric's correctness must come from the contract + engine, not from data shape.
- **Adding a read-time filter on `FactReaderService` to exclude paid invoices from the DSO numerator.** Rejected because reads do not produce meaning (playbook §6; Foundation §boundary-independent rules). Read-side semantics would shift meaning to the wrong boundary.
- **Authoring a new CF named `period_end_open_ar_balance` to carry the as-of semantic in the CF name.** Rejected because the gap is in CC production, not in CF naming. A new CF doesn't fix the open-vs-cleared question; the CC still has to actually produce open positions.
- **Shipping `at_period_end` in phase-1 with the simple `posting_date ≤ anchor` selector, documenting the limitation in Evidence.** Rejected because the kind name implies a semantic the engine does not deliver. Evidence-side disclosure is a weaker corrective than honest grammar; the kind name itself misleads downstream readers (dashboards, alerts, audits) before they reach the evidence row. Playbook §10 anti-pattern: adding grammar the engine cannot honestly evaluate.
- **Changing the metric grain to as-of-date (single global value per as-of, not per-fiscal-period).** Considered but deferred. The platform's grain vocabulary is currently per-period; a global-as-of grain is a larger grammar move with its own ADR. Not blocking the trailing-window phase-1 work.

## Drift / Damage Risks

- **Future remap of `receivable_hdr_amount` to a different CF.** Any change that re-maps the underlying BF in `cc__receivable_hdr` would silently shift what `outstanding_receivables_amount` carries. Layer C audit gate before any such remap.
- **Activating a new `cc__receivable_hdr` version with a different `cc_field_mapping` semantic for `outstanding_receivables_amount`.** The CF name does not change, but the produced value's meaning would. Must be caught by the L-Node semantic gate (D366) and by the playbook's Live MC Safety Workflow if downstream MCs are live.
- **Mass-binding DSO v2.0.0 to all tenants before the successor open-item CC work lands.** The metric would compute under the phase-1 partial grammar, produce a number that looks like DSO, and entrench a misleading interpretation. Stage activation in the ADR explicitly defers DSO v2 to after the successor work for exactly this reason.
- **Future grammar PR that re-admits `at_period_end` without the prerequisite CC work.** Caught by the meta-schema validation test in §7 that asserts v1.1 rejects `at_period_end`. The test is the structural firewall.
- **Engine drift toward wall-clock evaluation.** Caught by the Foundation Gate validation grep test that fails if `metric-evaluation-engine.service.ts` introduces `Date.now()` on the resolve-anchor or select-CO branches.
- **Tuning SDG-side `lifecycle_state` to inflate or deflate the open-AR sum.** Caught by Foundation Gate at the SDG work-type session — SDG calibration to satisfy a metric is the named anti-pattern.
- **Adding read filters in `FactReaderService` or admin dashboards that change apparent DSO values.** Playbook §10 anti-pattern; must be refused at code review.
- **Authoring DSO v3 in place by editing v2.0.0's contract_json.** Invariant III violation; Live MC Safety Workflow forbids in-place semantic mutation.
- **Changing the denominator from `total_credit_sales` to `net_credit_sales` without bumping the MC version.** Semantic mutation of a live MC — playbook §5 hard rule. New meaning, new version.

## Guardrails For Future Work

- Read this record's `Metric Logic Studied`, `Assumptions`, and `Rejected Interpretations` before proposing any DSO change. The earlier rejected interpretations exist precisely to prevent re-running them.
- Run the playbook's Metric Work Sequence (§3) end-to-end before authoring DSO v2 — especially step 3 (impact analysis across all bindings, snapshots, dashboards, storyboards, ADRs) and step 5 (confirm the upstream CC actually produces the declared semantic, not just the CF name).
- For DSO v2 authoring, apply the Live MC Safety Workflow (playbook §5): v1.2.0 stays in place; v2.0.0 is a new contract version; D305 deferred-supersession handles rollover; per-tenant rollover proceeds one tenant at a time.
- If the successor open-item ADR lands a new CC family (e.g., `cc__receivable_open_item`), the grammar's `at_period_end` re-admission proceeds in a coordinated grammar revision — not as a separate engine change.
- Any session touching `outstanding_receivables_amount` (CF), the `receivable_hdr_amount → outstanding_receivables_amount` mapping (cc_field_mapping), or `cc__receivable_hdr`'s active version must check this record's drift list before acting.
- Cross-system portability is the test of correctness for the eventual DSO v2: the same MC must produce equivalent values on a non-SAP CC bound via `tenant.contract_binding`. If the metric only computes correctly against Apex/SAP shape, the contract is too narrow.

## Findings

1. The current `mc__days_sales_outstanding` v1.2.0 computes per-period cumulative AR / per-period credit sales, structurally capped at ~38 days regardless of arrears distribution. Verified in prior session SES-b7db1a (DSO sanity probe).
2. The metric meta-schema v1 has `additionalProperties: false` and no temporal-window vocabulary; `temporal_gate.lookback_window` exists in engine code (`metric.service.ts:259`) but is unreachable via governed authoring because the schema rejects it. The grammar gap is real and specific. (Verified by reading `metric-v1.schema.json` and engine source.)
3. The CF registry already carries the semantic identifiers needed (13+ relevant CFs across AR balance and credit sales families). No new CFs are required for the grammar work. (Verified via `contract.canonical_field` queries.)
4. `cc_field_mapping` routes the right CFs to the right CCs; the gap is at the CC production layer, not at the binding. (Verified via `contract.cc_field_mapping` queries.)
5. `FiscalCalendarService.resolve / currentPeriod / listPeriods` exists with `periodStart` / `periodEnd` resolution — the temporal plumbing is present below the grammar with no grammar surface to invoke it today. (Verified by reading `fiscal-calendar.service.ts`.)
6. The phase-1 grammar can honestly express `over_trailing_window` for flow measures; it cannot honestly express `at_period_end` for balance measures while CCs are append-only. (Logical derivation from balance-vs-flow rule + CC inspection.)
7. A pilot consumer of phase-1 grammar should be a flow-only metric (e.g., trailing-twelve-month revenue), not DSO. DSO waits for the successor open-item / clearing / bitemporal ADR work on `cc__receivable_hdr` (or a successor CC). (Architectural decision from the review.)

## Decision / Recommendation

Approve the revised ADR draft (`barecount-devhub/.claude/adr-draft-realistic-dso.md`) for promotion to a formal ADR in `bc-docs-v3/docs/adrs/` via `devhub_decision_record`. Phase-1 grammar scope is `over_period` (explicit default) + `over_trailing_window` only; `at_period_end` is deferred. DSO v2.0.0 is NOT the phase-1 pilot — a flow-only metric is. Realistic-DSO authoring is gated on a successor open-item / as-of ADR scoping the CC-side semantics. No code is written until the ADR lands; no DSO v2 is authored until both this ADR and the successor are in.

### Promotion outcome — DEC-c012c0 / D400 (2026-05-11)

The draft was promoted to `bc-docs-v3/docs/adrs/ADR-c012c0.md` with status `proposed`, domain `metric`, subdomain `metric-grammar`, focus `schema`. Five questions previously open in the draft were resolved in-document before promotion and are mirrored in the ADR body:

1. **Anchor expression** — closed-string grammar `<scope>.<key>.<edge>` (scope ∈ {grain, evaluation_period}, edge ∈ {start, end}), regex-enforced by the meta-schema. Structured-object form rejected.
2. **`evaluation_period.{start, end}` admitted in phase 1** — engine resolves via a new `FiscalCalendarService.resolveByLabel(period_label, legal_entity_code)` returning `{start_date, end_date}`. `envelope.evaluationPeriod` stays caller-set; not promoted into MC body in phase 1.
3. **Multi-legal-entity ambiguity** — engine resolves per-LE fiscal calendars from tenant `dim_legal_entity` (D364 stack). Grain groups that fold multiple LEs raise a deterministic `anchor_ambiguous_legal_entity` rejection — no silent averaging, no grammar restriction.
4. **No opt-out grammar needed** — existing `tenant.contract_binding` version-pinning is sufficient. Consistent with Invariant III (new meaning = new MC version).
5. **Successor ADR deferred and required for realistic DSO** — working name *Open-item / as-of canonical semantics — temporal projection for balance metrics*. Three candidate mechanisms named (open-item CC family / clearing-by-supersession / bitemporal effective-from-to); none chosen here. This ADR's deliberate omission of `at_period_end` is the engine-side firewall pairing the upstream CC-side gap.

This record's status is now `decided`. Implementation (meta-schema v1.1 file, engine version-gated path, `FiscalCalendarService.resolveByLabel`, flow-only pilot MC) is Stage 2 work gated on this ADR landing as `decided` (a separate operator decision) and is not part of the record's authoring session.

## Demo Positioning (Apex CFO Pack — 2026-05-11)

This section addresses how `mc__days_sales_outstanding` v1.2.0 may be shown in the Apex CFO Pack demo while the realistic-DSO arc is gated on the successor open-item / as-of ADR. The metric continues to compute and store its current output unchanged; only the *presentation* (label, claims, position on the demo canvas) is constrained.

### What v1.2.0 actually computes (recap)

`(Σ same-period AR-debit postings) / (Σ same-period gross credit sales) × 30` — a same-period receivables-to-sales coverage ratio scaled to days-equivalent. Structurally ceiling-bound at ~30–38 days; not open-AR-at-anchor, not trailing-window.

### Demo-safe label

- **Tile label:** **"Collection Pressure"**
- **Technical sub-label (info-pane / tooltip):** **"Receivables Coverage (period view)"**
- The word "DSO" does not appear on the visible tile or in tooltips.

### Allowed claim

- Directional same-period receivables-to-sales coverage indicator. Useful as a supporting signal alongside AR Aging and Top 10 Overdue. Period-internal directional reads only.

### Forbidden claims

The following claims are unsupported by v1.2.0 semantics and must not be made in the demo (script, narration, voice-over, screen labels, or info panes):

- **Textbook / canonical DSO** — i.e., presenting the value as "Days Sales Outstanding" in its standard finance meaning.
- **Open AR as-of period end** — the numerator is cumulative same-period postings, not open positions at an anchor date.
- **Trailing-90 DSO** — grammar v1.0 has no trailing-window selector; the denominator is same-period gross credit sales.
- **DSO trend up/down as a collection-cycle change** — period-over-period deltas reflect within-period AR/sales-ratio drift, not the collection-cycle change a CFO reads "DSO trending" to mean. The structural ceiling compresses dynamic range and disqualifies trend storytelling.
- **CCC identity tie-out** — `DSO + DIO − DPO = CCC` requires three metric families with consistent open-item / trailing-window semantics. None of the three have that today; the identity will not tie out from current engine output.

### Storyboard implication (CFO Pack §7.1 M3 and the AR / liquidity tile set)

- **M3 drag-first headline must lead with AR Aging Weighted Average, not DSO.** The collection-cycle drift narrative (state-transport + corporate-fleet customers driving the increase) is honest from AR Aging weighted-average source data, which is the same operational signal the M3 moment is meant to deliver.
- **"47 days, up from 38 in Q2" may be used only for AR Aging Weighted Average,** and only if the aging-weighted-average source data supports it for the demo tenant. Do not bind the same numbers to a "DSO" label.
- **Collection Pressure may appear as a secondary support tile** alongside AR Aging, Overdue %, and Top 10 Overdue. It is not the M3 headline and is not the drag-first metric.
- **CCC is deferred from this demo cycle.** The CCC coherence demonstration re-enters the storyboard once the successor open-item ADR + DSO/DPO/DIO v2 metrics land with consistent semantics across all three.

### Follow-up

Realistic DSO and CCC tie-out are both gated on:

1. The successor ADR (working name: *Open-item / as-of canonical semantics — temporal projection for balance metrics*) selecting one of the three named mechanisms (open-item CC family / clearing-by-supersession / bitemporal columns) and landing the upstream CC-side semantics.
2. Authoring `mc__days_sales_outstanding` **v2.0.0** under grammar v1.1 (ADR-c012c0) once the successor's CC work is in place.
3. Authoring v2.0.0 of DPO and DIO under the same successor framework before any CCC tile or identity claim is re-enabled.

ADR-c012c0 phase-1 grammar is **necessary but not sufficient** for this storyboard arc. The Apex CFO Pack demo proceeds with the renamed tile and the AR-Aging-led M3 in the meantime.

## Evidence

Canonical artifacts (do not paste contents — link/name only):

- DevHub change records:
  - `CHG-2c2734` — SES-b7db1a (bc-core) plan-side, initial DSO grammar design.
  - `CHG-29c9bb` — SES-bedcef (bc-core) plan-side, Stage 1 revision under playbook discipline (this record's authoring session).
- ADR (promoted from draft):
  - `bc-docs-v3/docs/adrs/ADR-c012c0.md` — `DEC-c012c0` (D400), status `proposed`, promoted 2026-05-11.
  - `barecount-devhub/.claude/adr-draft-realistic-dso.md` — pre-promotion draft (kept as orientation artifact; not authoritative).
- Commits (orientation context, not changes from this session):
  - `4b52785` — `docs: add foundation invariant check to CLAUDE guidance` (CLAUDE.md gate that this work runs under).
  - `f7faf98` — `docs: add metric workstream playbook` (the playbook framing this work).
- Foundation and onboarding sources consulted:
  - `bc-docs-v3/docs/foundation/the-invariants.md`
  - `bc-docs-v3/docs/foundation/the-evaluation-boundaries.md`
  - `bc-docs-v3/docs/foundation/the-contract-grammar.md`
  - `bc-docs-v3/docs/onboarding/metric-contract-creation.md`
  - `bc-docs-v3/docs/onboarding/metric-workstream.md` (§3, §5, §8, §10)
- Registry verification (read-only DB queries via `bc-postgres`):
  - `contract.canonical_field` — 13+ AR/sales/DSO CFs already registered.
  - `contract.cc_field_mapping` — `cc__receivable_hdr` and `cc__invoice_hdr` produce the candidate CFs.
  - `contract.metric_contract_version` — current `mc__days_sales_outstanding` v1.2.0 envelope inspected.

## Non-decisions

- Did NOT promote the ADR draft to `bc-docs-v3/docs/adrs/`. Awaits user approval for `devhub_decision_record` promotion.
- Did NOT author or commit `metric-v1.1.schema.json`.
- Did NOT modify `MetricEvaluationEngine` source or any other bc-core code.
- Did NOT author DSO v2.0.0 against any grammar.
- Did NOT change SDG generator behavior.
- Did NOT register new canonical_field or business_field rows.
- Did NOT add new `cc_field_mapping` rows.
- Did NOT touch `outstanding_receivables_amount`'s mapping rule on `cc__receivable_hdr`.
- Did NOT delete the `MetricService.applyLookbackWindow` dead path — flagged for a separate cleanup ADR.
- Did NOT propose a new CF (the registry already carries the needed semantics).
- Did NOT commit any file in any repo this session.

## Phase 2 Architecture Scoping (2026-05-11)

The successor open-item/as-of ADR — named in `Follow-ups` below and in `ADR-c012c0` §Successor — is now scoped via a separate draft at `barecount-devhub/.claude/adr-draft-open-item-as-of-canonical-semantics.md` (not yet promoted).

### Source-feasibility check

bc-sdg's apex `CustomerOpenItemSet` V2 endpoint (probed 2026-05-11) emits SAP-native open/cleared signal:

- `AUGDT` (clearing date) — `null` on open items
- `AUGBL` (clearing document) — `null` on open items
- `BUDAT`, `BLDAT`, `KUNNR`, `DMBTR`, `WRBTR`, `BSCHL`, `KOART`, `BLART`, `ZFBDT`, `ZTERM` all populated

**All three candidate mechanisms are source-feasible.** No SDG signal additions required.

### Three mechanisms analyzed

| Mechanism | Verdict |
|---|---|
| **A — Separate open-item CC family** (`cc__receivable_open_item` + `cc__receivable_cleared_item` siblings to the legacy `cc__receivable_hdr`) | **RECOMMENDED PRIMARY.** Cleanest semantic separation. Foundation Invariant III preserved trivially (open and cleared events are independent COs in independent CCs; no state mutation, no supersession chain). Engine-code change is minimal — existing CO selection mechanics handle it. Largest contract surface (2 new CCs + 2 OCs + mapping versions), but every artifact is conventional onboarding. Generalizes naturally to AP and inventory. |
| **B — Clearing-by-supersession** (existing CC retains identity; clearing emits a new CO version on the same business_key with lineage reference; engine traverses supersession chain) | **REJECTED for primary; kept as future option.** Invariant III preserved via versioning. Adds non-trivial engine complexity (supersession-chain traversal in CanonicalResolutionService + MetricEvaluationEngine). Tenant migration heavier (per-tenant re-onboarding). Single-CC identity is appealing but doesn't outweigh engine-side cost. |
| **C — Bitemporal `effective_from` / `effective_to` columns** (selection rule `effective_from ≤ anchor < effective_to`) | **REJECTED.** Bitemporal as classically defined requires **mutating** `effective_to` when a later clearing event arrives → violates Foundation Invariant III (state immutable). Workaround (emit new CO version) collapses into Mechanism B with worse ergonomics. |

### Recommendation — Mechanism A

The first implementation slice is the **smallest provable step**: author and onboard `cc__receivable_open_item` (the open-AR-only CC) for apex, verify open-AR COs land, then in a separate later slice author DSO v2.0.0. Mechanism A is also the only Mechanism that does not require an engine-code change.

### Implementation arc (planned, post-ADR promotion)

| Slice | Goal |
|---|---|
| 0 (scoping) | This draft + DSO MWR update (done) |
| 1 | Author + provision `cc__receivable_open_item` + OC + canonical_mapping for apex; verify open-AR COs land |
| 2 | Author DSO v2.0.0 binding `cc__receivable_open_item` (numerator) + `cc__invoice_hdr` trailing-90 (denominator) |
| 3 | Optional: author `cc__receivable_cleared_item` for clearing-event analytics |
| 4 | DPO v2.0.0 + AP open-item CC (mirror of slices 1–2) |
| 5 | DIO v2.0.0 + inventory open-item CC |
| 6 | Re-enable CCC tile + storyboard §9 assertion #2 |
| 7 | Apex demo-readiness triage refresh — flip Tier-A DSO/DPO/CCC from RED to GREEN; M3 narration restored |

### Relationship to ADR-c012c0

The successor ADR **layers on top** of DEC-c012c0 (D400). DEC-c012c0's grammar v1.1 declared `at_period_end` as deferred-not-shipped; the successor re-admits it (as a future grammar v1.2 if needed; or as a runtime-engine extension that consumes existing v1.1 grammar shape against the new CC family) once Mechanism A's CCs are in place. ADR-c012c0 itself is not modified; per DEC-623f8f (D370) supersession-pair rule, the successor may eventually flip ADR-c012c0 to `superseded` if the new grammar version fully replaces it — or both stand as a layered pair (c012c0 = grammar firewall for balance metrics; successor = upstream open-item semantics that re-open the firewall).

### Draft location

`barecount-devhub/.claude/adr-draft-open-item-as-of-canonical-semantics.md` — full mechanism analysis, comparison table, source-feasibility evidence, and 5-answer scoping checklist. Awaits operator approval for promotion via `devhub_decision_record`.

### Records convention

This MWR's `status` stays `decided` — the original Phase-1 grammar decision is unchanged. The Phase-2 architecture is captured here as a scoping update; a separate per-MC MWR will be filed when DSO v2.0.0 is authored (per playbook §11 MC-version-bump trigger).

### ADR Promotion Outcome — DEC-1db1c7 / D401 (2026-05-11)

The Phase-2 scoping draft (`barecount-devhub/.claude/adr-draft-open-item-as-of-canonical-semantics.md`) was promoted via `devhub_decision_record` to a formal ADR:

- **UID:** `DEC-1db1c7`
- **D-code:** `D401`
- **Path:** `bc-docs-v3/docs/adrs/ADR-1db1c7.md`
- **Title:** *Open-item / as-of canonical semantics — temporal projection for balance metrics*
- **Status:** `proposed`
- **Domain / subdomain / focus:** `metric` / `canonical-semantics` / `balance-metrics`

**Decision recorded:** adopt **Mechanism A — separate open-item canonical contract family** as the primary path for realistic DSO and analogous balance metrics. Mechanism B (clearing-by-supersession) deferred; Mechanism C (bitemporal in-place mutation) rejected on Foundation Invariant III.

**Relationship to ADR-c012c0:** **layered pair, not superseded.** ADR-c012c0 owns flow-side temporal input-selection grammar (`over_period`, `over_trailing_window`); DEC-1db1c7 owns upstream open-item canonical semantics. Neither replaces the other. The supersession-pair rule (DEC-623f8f / D370) does not require flipping ADR-c012c0's status. The `related_adrs` frontmatter has been updated to list both.

**Realistic DSO status:** **NOT complete.** This ADR is the architectural enabler. DSO v2.0.0 still requires:
1. `cc__receivable_open_item` authored, provisioned, and bound to apex (DSO Phase-2 Slice 1).
2. DSO v2.0.0 MC authored binding `cc__receivable_open_item` (numerator) + `cc__invoice_hdr` trailing-90 (denominator) (DSO Phase-2 Slice 2).
3. Per-tenant migration via `tenant.contract_binding` version pinning.

**Implementation begins with DSO Phase-2 Slice 1: author + provision `cc__receivable_open_item` for apex.** Smallest provable step. No DSO v2 authoring in Slice 1; that's Slice 2.

**Foundation firewalls preserved:** no SDG tuning, no read-model compensation, no fact-side computation, no in-place live-MC semantic mutation. ADR-c012c0's grammar v1.1 firewall (excluding `at_period_end` against legacy CCs) is preserved; the new CC family is the principled re-admission path at the MC-authoring layer.

## Follow-ups

- **Promote ADR draft to formal ADR.** ✓ Done 2026-05-11 — `DEC-c012c0` (D400), status `proposed`. Approval to flip to `decided` is a separate operator step.
- **Scope successor ADR for open-item / as-of CC semantics.** Three candidate paths (separate open-item CC family / clearing-by-supersession / bitemporal effective-from-to). Architectural conversation, not a single-session task.
- **Identify a phase-1 pilot flow metric.** Candidate: trailing-twelve-month revenue or a similar pure-flow KPI. The pilot proves the grammar end-to-end without depending on balance semantics.
- **Cleanup ADR for `MetricService.applyLookbackWindow` dead path.** Wall-clock semantics in the engine are a Foundation risk; remove the unreachable code before it gets resurrected.
- **CC mapping audit for `outstanding_receivables_amount`.** Confirm the gap is widely understood before any DSO-shaped MC consumes the CF assuming open semantics.

(No `TSK-` UIDs filed in this session; the user has visibility on each open item and can file via `devhub_task_add` at their preferred granularity.)
