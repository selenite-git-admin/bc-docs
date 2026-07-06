---
title: BCF Orphan Characteristic Decision Inventory (2026-06-23)
description: Read-only inventory of active characteristics with zero active BC bindings. Classifies each under DEC-fb0b12 + Vocabulary Evidence Framework §11 doctrine. 6 active orphans + 1 draft orphan. **Amended 2026-06-23 (§8):** §5's three-candidate recommendation is withdrawn under operator's orphan-as-vocabulary-capacity rule — orphans activate only when pulled by concrete metric / source-chain / entity-backbone / workflow demand, not when pushed at by a sweep. Only `fiscal period` is doctrine-driven housekeeping (§11.6-forbidden BCF name; stays in draft permanently or is archived); the remaining 6 stay orphan as vocabulary reserve until concrete demand surfaces.
status: held
authority: implementation-inventory
date: 2026-06-23
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-orphan-inventory
related_docs: [bcf-characteristic-scope-audit-2026-06-23.md, bcf-characteristic-amendment-doctrine-2026-06-23.md, bcf-wave-b-fast-track-parity-closeout-2026-06-23.md, ADR-fb0b12.md, business-concept-registry-vocabulary-evidence-framework.md]
---

# BCF Orphan Characteristic Decision Inventory (2026-06-23)

After Wave A + Wave B closed (11 BCs authored this session; 194 total active BCs), the substrate carries 7 active characteristics with **zero active BC bindings**: 6 with `lifecycle_state='active'` and 1 with `lifecycle_state='draft'`. This packet inventories them, classifies each under DEC-fb0b12 + Vocabulary Evidence Framework §11 doctrine, and proposes — or explicitly does not propose — a next targeted operator-decision path. No mutations. **Do not author yet.**

## 1. Live orphan inventory

Query: `concept_registry.characteristic` where `lifecycle_state IN ('active','draft')`, `archived_at IS NULL`, and no row in `concept_registry.business_concept` with `lifecycle_state='active'` references the characteristic.

| Term | char_uid | lifecycle | Definition (verbatim, governed) |
|---|---|---|---|
| `cycle time` | `7042ca4f-…` | active | "The elapsed time required to complete one full iteration of a repeatable business activity, measured from the start of one cycle to the start of the next." |
| `expiry date` | `209b3118-…` | active | "Date after which a record, rate, or agreement ceases to be valid." |
| `fiscal period` | `ef143792-…` | **draft** | "The fiscal-period identifier the Journal Entry posts into … Derived from the posting date through the tenant's fiscal calendar substrate (date_dim + tenant.fiscal_calendar_config per D364 / DEC-d7e7a0) … A canonical platform code; source-system fiscal-period codes … are normalised to this canonical code at the reader boundary. Expected platform shape: code / string / dimension." |
| `interest rate` | `7fe93afb-…` | active | "Rate charged or earned on a principal amount over a period of time." |
| `lead time` | `407a6582-…` | active | "The elapsed time between initiating a business activity and the expected completion or receipt of its result." |
| `note` | `d2c79a0a-…` | active | "Free-form remarks or commentary attached to a record." |
| `quantity on hand` | `e33aa290-…` | active | "Number of units of an item currently held in inventory." |

Totals: 62 active characteristics, **6 active orphans (10% of active vocabulary)**, 1 draft orphan. The active vocabulary's orphan rate is non-trivial; this is largely a substrate-history artifact (characteristics admitted before their target entity was admitted, or admitted speculatively).

## 2. Classification table

| Term | Classification | Likely semantic class | Likely shape | Plausible target entity / entities |
|---|---|---|---|---|
| `cycle time` | **METRIC_DERIVED_ONLY** | Duration measure | n/a (not BCF) | None — belongs at MCF |
| `expiry date` | **OPERATOR_DECISION_REQUIRED** | Temporal (valid-to anchor) | `date` / `date` / `temporal` | Currency Exchange Rate (strongest); Credit Application; Credit Status; Bank Account |
| `fiscal period` | **RUNTIME_DERIVED_ONLY** | Resolver-stamped period code | n/a (forbidden as BCF term per §11.6) | None — keep draft, do not activate |
| `interest rate` | **OPERATOR_DECISION_REQUIRED** | Rate | `rate` / `decimal` / `amount` | Credit Application (strongest); Bank Account; Customer |
| `lead time` | **OPERATOR_DECISION_REQUIRED** | Duration (planning) | `quantity` or `count` / `decimal` or `integer` / `amount` | Supplier (strongest, planning lead time on master); Purchase Order Line (per-line planned delivery time) |
| `note` | **HOLD_AMBIGUOUS** | Free-form text carrier | `text` / `string` / (no metric role) | Any — but no current entity *needs* it |
| `quantity on hand` | **OPERATOR_DECISION_REQUIRED** | Inventory measure | `quantity` / `decimal` / `amount` | Blocked — no inventory entity admitted (would need `Material` / `Inventory Position` / `Stock Item` admission first) |

**None are SAFE_BCF_CANDIDATE on the unattended-autonomous level.** Every active-state orphan needs an operator entity decision before a panel can author it without packet-blindness drift.

## 3. Per-orphan doctrine analysis

### 3.1 `cycle time` — METRIC_DERIVED_ONLY

A cycle time is a *computed* duration over start/end timestamps captured on a sequence of source events — exactly the role of an MCF Metric Contract, not a BCF characteristic. The platform already produces `invoice_processing_cycle_time` and similar via MCF (the active MC `0511925f-…`). Binding `cycle time` to a BCF entity would create a substrate-level synonym for what's already computed by MCF.

Doctrine: Vocabulary Evidence Framework §11.6 source-attested-vs-resolver-stamped distinction; cycle time is the same category as `fiscal period` — derived from upstream observations, not directly attested on a source row. (One narrow exception: SAP supplier master sometimes carries a *planning* cycle time, but that's already covered semantically by `lead time` — see §3.4.)

**Disposition: leave orphan. Do not author. Do not amend.**

### 3.2 `expiry date` — OPERATOR_DECISION_REQUIRED

Mirror of `effective date` (already active on Credit Status, Currency Exchange Rate, Customer Invoice). The strongest single binding target is **Currency Exchange Rate × expiry date** — every governed rate has an effective period (effective-from + effective-to), and the existing Currency Exchange Rate × effective date BC implies an unstated effective-to that this characteristic would explicitly bind.

Secondary candidates:
- Credit Application × expiry date (application validity window)
- Credit Status × expiry date (status validity window — but Credit Status is currently as-of-stamped, not validity-windowed; needs operator clarification)
- Bank Account × expiry date (e.g., debit-card expiry on the account; but Bank Account already might use other temporal anchors)

**Disposition: operator decides target entity. Strongest single-candidate target: Currency Exchange Rate × expiry date. Symmetric with the existing effective date binding; doctrinally clean.**

### 3.3 `fiscal period` — RUNTIME_DERIVED_ONLY (also forbidden as BCF term)

Vocabulary Evidence Framework §11.6 explicitly forbids `fiscal period` as a BCF characteristic name: *"The bare label `fiscal period` is forbidden as a BCF characteristic name because it collides with the resolver-derived authority and invites cross-layer drift; the reserved Layer-B name is `posting period code`."* The current orphan row is in `lifecycle_state='draft'` and the definition itself flags it as "Derived from the posting date through the tenant's fiscal calendar substrate".

**Disposition: leave draft. Do not activate. Do not bind.** If the operator decides a source-attested period-code characteristic is needed in future, the path is to author a *new* characteristic under the §11.6-reserved name `posting period code` (a new `characteristic_id`, distinct from this orphan draft row) on entities where the source system actually emits a discrete period code that isn't synonymous with the resolver-derived canonical period.

The existing draft row could be archived or superseded as housekeeping — but per the read-only scope of this packet, that is also a deferred operator decision, not a recommendation here.

### 3.4 `interest rate` — OPERATOR_DECISION_REQUIRED

Genuinely source-attested in multiple ERP contexts. Strongest single binding target is **Credit Application × interest rate** — the credit terms on the application are the canonical operator-facing carrier (SAP credit-management master holds interest rate per customer; on a credit-application surface this is the per-application offer).

Secondary candidates:
- Bank Account × interest rate (account-level savings/checking interest rate; valid if `Bank Account` is in scope for that semantic)
- Customer × interest rate (collection penalty rate — operator-decided, less canonical)

The semantic span of "interest rate" is wider than the definition prose admits — applied to credit, to bank accounts, to debts, to investments. Per Vocabulary Evidence Framework §11.2.1 (system-agnosticism), different source carriers are not by themselves justification for scoped siblings. **One characteristic; operator decides which entity(ies) bind it.** Multi-entity binding is fine if each binding is semantically valid under the definition.

**Disposition: operator decides target. Strongest single-candidate target: Credit Application × interest rate.** Multi-entity binding (Credit Application + Bank Account) is also doctrinally clean if both are in scope.

### 3.5 `lead time` — OPERATOR_DECISION_REQUIRED

The definition is general ("elapsed time between initiating a business activity and the expected completion") and applies to multiple contexts. Two operationally distinct flavors:

- **Planning lead time** (source-attested) — a value the source system carries on a master record: supplier delivery lead time (SAP LFB1-related fields), planned delivery time per PO line (EKPO-PLIFZ). This IS a real source field, not derived.
- **Actual lead time** (metric-derived) — computed as `goods_receipt_date − po_creation_date` (or similar). This is MCF.

The source-attested flavor is the BCF-admissible interpretation. **Strongest single binding target: Supplier × lead time** (the supplier-master planning lead time the buyer uses for MRP / supply planning).

Secondary candidate: Purchase Order Line × lead time (per-line planned delivery time from EKPO-PLIFZ). Slightly weaker — the per-PO-line override is less reused than the supplier master.

Shape question: the definition reads as a duration ("elapsed time"). The closed representation_term set offers `quantity` (e.g., "5 days" expressed as a count with a unit) or `count` (a non-monetary integer tally). Either could fit; the data_type would be `decimal` (allowing fractional days) or `integer`. The substrate has no sibling precedent — first such characteristic. Operator should pin shape ahead of the panel, mirroring the Wave B SOL × line number pattern.

**Disposition: operator decides target + shape. Strongest single-candidate target: Supplier × lead time. Shape proposal: `quantity / decimal / amount`** (days with fractional precision; semantic_role=amount mirrors how `delivered quantity` / `ordered quantity` are encoded across the line backbone).

### 3.6 `note` — HOLD_AMBIGUOUS

A free-form text carrier whose definition is intentionally maximally broad. *Any* entity could carry a note, but `note` doesn't drive any metric, join, or filter. Per BCF backbone breadth doctrine §11.3, this is the prototypical *source-diagnostic substrate*: useful for tracing observations to source rows but not load-bearing for analytical workflows.

The §11.3 disposition for source-diagnostic substrate is: **deferred until concrete workflow demand surfaces**. No metric currently demands `note` on any entity.

**Disposition: stay orphan. If a specific workflow demand surfaces (e.g., dispute-handling on Customer Invoice needs a per-invoice note), author at that point on the specific demanding entity. Until then, do not author speculatively.**

### 3.7 `quantity on hand` — OPERATOR_DECISION_REQUIRED (gated on entity admission)

Inventory-specific by definition. The substrate has no inventory entity admitted: no `Material`, no `Inventory Position`, no `Stock Item`, no `Warehouse Location`. The characteristic exists but has no target.

This is gated on a prior decision: **admit an inventory entity**. Until then, `quantity on hand` cannot be bound without inventing the target entity at panel time, which would be operator-decision-required and would likely park.

**Disposition: stay orphan. Entity admission is the prerequisite, not a wave action.** If the operator wants to open the inventory backbone, that's a separate operator-authored entity-admission decision (a `createEntity` panel run, not a BC-binding wave). Once `Inventory Position` (or equivalent) is admitted, `quantity on hand` becomes a SAFE_BCF_CANDIDATE on that entity.

## 4. Risks if an orphan wave is run autonomously

Same class of failure as Wave B's initial parks:

- **Maker packet-blindness on shape.** For `lead time` (first such characteristic, no substrate sibling), the Maker would have to invent a shape — same risk that produced `identifier/integer/identity` in the SOL × line number prior parked panel.
- **Maker entity-selection guessing.** For `interest rate`, multiple entity candidates exist; an autonomous panel without entity pin would either pick one and bind it (silently locking the substrate to that choice) or park.
- **No-vocabulary-stretch parks.** Even where the entity choice is reasonable, the Maker may park if the entity's prior bindings don't align with the orphan characteristic's definition.
- **Doctrine-forbidden mints.** Without explicit operator caveat, an autonomous wave attempting to bind `fiscal period` would violate §11.6 — the panel might catch it (good) or might mint a binding (catastrophic for substrate hygiene).

## 5. Recommended next action

**Do not run an orphan wave yet.**

Instead, recommend **three single-candidate operator-decision-then-targeted-bind cycles**, each independently authorized:

| # | Candidate | Target entity | Shape (proposed) | Doctrinal status |
|---|---|---|---|---|
| 1 | `interest rate` × Credit Application | Credit Application (`720f3c23-…`) | rate / decimal / amount | Clean. Source-attested. Doctrinally clear. |
| 2 | `lead time` × Supplier | Supplier (`2374fee4-…`) | quantity / decimal / amount | First-of-kind for `lead time`. Operator should pin shape in candidate evidence ahead of panel. |
| 3 | `expiry date` × Currency Exchange Rate | Currency Exchange Rate (`70a282ab-…`) | date / date / temporal | Symmetric with existing `effective date` binding on the same entity. Doctrinally clean. |

Each is a single-BC bounded operator-confirmation-then-fresh-panel cycle, not an autonomous sweep. Each follows the post-Wave-B doctrine (pin shape in candidate evidence; halt on park).

**The remaining 4 orphans stay orphan:**
- `cycle time` — METRIC_DERIVED_ONLY (belongs at MCF)
- `fiscal period` — RUNTIME_DERIVED_ONLY (§11.6 forbidden; stay draft)
- `note` — HOLD_AMBIGUOUS (source-diagnostic, no demand)
- `quantity on hand` — gated on inventory-entity admission (a separate decision)

## 6. Explicit non-actions in this packet

- No BCF panel calls.
- No characteristic amendments.
- No characteristic supersessions.
- No BC authoring.
- No MCF / CC / OC work.
- No code edits.
- No PR.
- No direct SQL writes.
- **Do not author yet.** The packet's explicit recommendation is to authorize one targeted single-candidate cycle at a time, not an orphan wave.

## 7. Operational state (unchanged)

- bc-core PID 29912 from `C:\MyProjects\bc-core-runtime` at `c63db8ed`, healthy.
- bc-ai PID 28444, port 4300, healthy.
- Dirty `C:\MyProjects\bc-core` worktree untouched.
- Wave A + Wave B closed. 194 active BCs across 26 active entities. 62 active characteristics. 4 amendment ledger rows. 7 active-orphan + 1 draft-orphan characteristics.
- Two parked panels (`be8bea24-…`, `0a5d2e5c-…`) untouched as audit history.
- DEC-fb0b12 ADR filed (editorial-amendment refinement of DEC-26b6e2).
- This packet joins the deferred uncommitted bc-docs-v3 batch.

Held for operator decision on the three recommended single-candidate cycles (or for explicit deferral if the operator prefers to address a different track — e.g., SI Line × ordered quantity wording clarification, posted amount disposition, or the BSL × line number outlier audit — before any orphan work).

## 8. Amendment 2026-06-23 — orphans are vocabulary capacity, not a triable backlog

**Operator correction to §5.** "Has no active binding" is not, by itself, justification for a proactive operator decision. Orphan characteristics are **vocabulary capacity** held in reserve; they activate only when one of four concrete pulls surfaces:

1. A concrete **metric** requires a specific (entity, characteristic) binding,
2. A **source-chain** (SC → AC → OC → CC) enrichment requires it,
3. A specific **entity-backbone-completion** need requires it (a metric or workflow already depends on a slice the binding would close), or
4. An **operator workflow / use case** explicitly requires the binding.

Otherwise the orphan stays orphan. This is not backlog; it is reserve. The framing matches BCF backbone breadth-and-batch doctrine §2.3 (source-diagnostic deferral pattern) and Vocabulary Evidence Framework §11.3 (canonical-vs-source-diagnostic substrate distinction).

**Doctrine-driven exception — `fiscal period` only.** The orphan itself violates doctrine (Vocabulary Evidence Framework §11.6: the bare label is forbidden as a BCF characteristic name; the row sits in `draft` lifecycle and should not activate as-is). The actionable handling is **housekeeping** — leave-draft-permanently, archive, or formally renounce as a deferred decision. **Not authoring.** Whichever path the operator takes, it is not a BC-binding act.

**Reclassification of the remaining 6 orphans** under the pull-driven rule:

| Term | Revised disposition under pull-driven rule |
|---|---|
| `cycle time` | Stays orphan **permanently in BCF** — metric-derived, belongs at MCF. Never pulled into BCF. |
| `expiry date` | Vocabulary capacity. Awaits a concrete metric / source-chain / workflow demand for an entity-level expiry binding. No current pull. |
| `interest rate` | Vocabulary capacity. Awaits a concrete credit / banking metric / workflow demand. No current pull. |
| `lead time` | Vocabulary capacity. Awaits a concrete three-way-match / supply-planning metric or supplier-master-completion workflow demand. No current pull. |
| `note` | Vocabulary capacity. Awaits a concrete operator-workflow demand (e.g., dispute-handling on Customer Invoice). No current pull. |
| `quantity on hand` | Vocabulary capacity, gated on inventory-entity admission. Awaits a concrete inventory-track demand AND a separate entity-admission decision. No current pull on either gate. |

**§5's three-candidate recommendation is withdrawn.** The proposed cycles for `interest rate × Credit Application`, `lead time × Supplier`, and `expiry date × Currency Exchange Rate` were push-driven ("we have orphans, let's pull them into bindings"). They are not authorized for autonomous follow-up. They become candidates only if and when a concrete metric / source-chain / entity-backbone-completion / workflow demand surfaces that requires the binding. The Wave-B-style risk analysis in §4 still applies for any future pulled binding (shape pinning ahead of panel; halt on park).

**No additional orphan inventory pass scheduled.** Orphan revisitation is triggered by concrete workflow demand, not by elapsed time or substrate-completeness audits. If the operator notices an orphan that arrived after this packet was held, the same pull-driven rule applies.

**Net effect on session-held state.** The operational state in §7 is unchanged; no mutations follow from this amendment. The packet's primary contribution post-amendment is the rule itself + the doctrine-driven `fiscal period` housekeeping flag, not a wave proposal.
