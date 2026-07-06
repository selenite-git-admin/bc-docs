---
title: BCF Characteristic Scope Audit (2026-06-23)
description: Held audit packet — definition-vs-binding scope analysis of 26 backbone characteristics + 7 orphans, triggered by Wave B's Sales Order × net amount park. Classifies each characteristic as CLEAN_GENERAL / CLEAN_NARROW / OVER_BROAD / OVER_NARROW / MIXED_BINDINGS / NEEDS_SPLIT / RUNTIME_DERIVED_ONLY / OPERATOR_DECISION_REQUIRED, names the high-risk definitions, proposes amendment/split/supersede paths, and produces the safe-autonomous-reuse whitelist.
status: held
authority: implementation-audit
date: 2026-06-23
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: characteristic-scope-hygiene
related_docs: [bcf-wave-a-supplier-invoice-header-parity-closeout-2026-06-23.md, bcf-backbone-breadth-and-batch-doctrine.md, business-concept-registry-vocabulary-evidence-framework.md]
---

# BCF Characteristic Scope Audit (2026-06-23)

The BCF Fast-Track Wave B halted on candidate #1 — `Sales Order × net amount` — because the panel correctly enforced **no-vocabulary-stretch**: the `net amount` characteristic's governed definition is invoice-scoped, while a Sales Order is an order-class document. This raises the question of whether `net amount` is an isolated mismatch or one of a wider hygiene gap. This audit answers that question across 26 active backbone characteristics + 7 orphans.

## 1. Method

For each characteristic the audit pulled:
- governed `definition` text (the panel's scope gate);
- active BC bindings (what entities currently use it);
- superseded BC bindings (what was retired and why);
- whether each active binding falls inside the definition scope.

Then each characteristic was placed in one of 8 classes:

| Class | Meaning |
|---|---|
| **CLEAN_GENERAL** | Definition supports current bindings AND plausible future cross-entity reuse |
| **CLEAN_NARROW** | Definition is intentionally domain-scoped; current bindings fit; not expected to reuse beyond |
| **OVER_BROAD** | Definition admits more semantic ground than the operator probably wants |
| **OVER_NARROW** | Definition blocks valid reuse; panel will park clean candidates |
| **MIXED_BINDINGS** | Current bindings already exceed the definition's stated scope |
| **NEEDS_SPLIT** | One term carries multiple meanings — should become two characteristics |
| **RUNTIME_DERIVED_ONLY** | Should not be a BCF binding; lives at canonical resolution or metric layer |
| **OPERATOR_DECISION_REQUIRED** | Definition or entity choice is judgment-heavy; not autonomous-safe |

A characteristic can be multi-class (e.g. OVER_NARROW + MIXED_BINDINGS for `net amount`).

## 2. Summary table

| Term | Active bindings (count) | Class | Wave-B-safe? |
|---|---|---|---|
| clearing date | CI, CP, SI, VP (4) | CLEAN_GENERAL | ✓ |
| country code | Bank Account, Customer, PO, Supplier (4) | CLEAN_GENERAL | ✓ |
| currency code | 14 entities | CLEAN_GENERAL | ✓ |
| cycle time | 0 (orphan) | RUNTIME_DERIVED_ONLY | hold |
| delivered quantity | CILI, GR Line, SOL, SI Line (4) | CLEAN_GENERAL | ✓ |
| **delivery date** | Customer Shipment (1) | CLEAN_NARROW (post-Phase-1) | hold (intentionally narrow) |
| discount | CI, CILI, PO Line, SOL, SI (5) | CLEAN_GENERAL | ✓ |
| document date | 11 entities | CLEAN_GENERAL | ✓ |
| document type code | CI, SI (2) | CLEAN_NARROW (accounting-scoped, SAP BLART semantics) | hold |
| due date | CI, SI (2) | CLEAN_GENERAL definition; current bindings invoice-only | ✓ for any obligation-bearing document |
| effective date | Credit Status, Currency Exchange Rate, CI (3) | OPERATOR_DECISION_REQUIRED (status-validity vs rate-effective) | hold |
| exchange rate | Currency Exchange Rate, CI, CP, JE, SO, SI, VP (7) | CLEAN_GENERAL | ✓ |
| expiry date | 0 (orphan) | CLEAN_GENERAL def; entity choice OPERATOR_DECISION_REQUIRED | hold |
| fiscal period | 0 (orphan, **draft**) | RUNTIME_DERIVED_ONLY (per D364 fiscal calendar architecture) | hold permanently |
| **gross amount** | CI, RA, SI (3) | **OVER_NARROW** (invoice-scoped) + MIXED_BINDINGS (RA borderline) | hold |
| interest rate | 0 (orphan) | CLEAN_GENERAL def; entity OPERATOR_DECISION_REQUIRED | hold |
| invoice receipt date | SI (1) | CLEAN_NARROW (AP-only by design) | hold |
| lead time | 0 (orphan) | CLEAN_GENERAL def; entity OPERATOR_DECISION_REQUIRED | hold |
| line number | 6 line entities | CLEAN_GENERAL (line-only by definition; correct) | ✓ |
| **net amount** | CI, PO, SI (3) | **OVER_NARROW** (invoice-scoped) + **MIXED_BINDINGS** (PO already a leak) | hold |
| note | 0 (orphan) | OPERATOR_DECISION_REQUIRED (free-form carrier) | hold |
| ordered quantity | CILI, GR Line, PO Line, SOL (4) | CLEAN_GENERAL definition; mild MIXED_BINDINGS (CILI/GR Line not orders) | borderline — operator decision |
| payment amount | CP, VP (2) | CLEAN_NARROW (payment-specific by design) | hold |
| payment terms | Customer, PO, SO, Supplier (4) | CLEAN_GENERAL | ✓ |
| **posted amount** | Customer Invoice (1) | **MIXED_BINDINGS** (def says "per-line", binding is header) | hold |
| posting date | 11 entities | CLEAN_GENERAL (mild concern on PO commitment posting) | ✓ |
| quantity on hand | 0 (orphan) | CLEAN_NARROW def; no inventory entity admitted | hold permanently until inventory entity admitted |
| sent date | Customer Invoice (1) | CLEAN_GENERAL def; CLEAN_NARROW in current use | ✓ for any document-transmission case |
| status | 22 entities | CLEAN_GENERAL | ✓ |
| system entry date | SI (1) | CLEAN_GENERAL def; CLEAN_NARROW in current use | ✓ for any source-system-stamped doc |
| tax | 8 entities | CLEAN_GENERAL | ✓ |
| tax rate | CILI, GR Line, SI Line (3) | CLEAN_GENERAL def; line-only in practice | ✓ for any line entity |
| value date | BSL, CP, VP (3) | CLEAN_NARROW (banking-specific) | hold |

Phase-1 cleanup outcome holds: `delivery date` is correctly narrowed to physical fulfillment (Customer Shipment), and `invoice receipt date` + `system entry date` are correctly AP-specific.

## 3. High-risk characteristics (deep detail)

### 3.1 `net amount` — OVER_NARROW + MIXED_BINDINGS

**Definition:** *"Invoice monetary amount before tax and gross-up components, after applicable line/price adjustments. Distinct from gross amount, tax amount, posted amount, outstanding amount, and cleared amount."*

**Current active bindings:** Customer Invoice, **Purchase Order** (← scope leak), Supplier Invoice.

**Why this matters:** PO is an order-class document, not an invoice. The PO × net amount binding predates the no-vocabulary-stretch enforcement; it was authored when the definition was either looser or the gate was permissive. The panel now blocks Sales Order × net amount (parked panel run `be8bea24-…`) — but the substrate already carries the inconsistency on PO.

**Two paths to resolve:**

- **Path A — broaden the definition** (single-characteristic continuum). Amend the definition to: *"Document-level monetary amount before tax and gross-up components, after applicable line/price adjustments. Applies to orders (sales/purchase) and invoices (customer/supplier) that carry a pre-tax document total. Distinct from gross amount, tax amount, posted amount, outstanding amount, and cleared amount."* This brings the existing PO binding into scope, unblocks SO × net amount, and is one `amend-definition` call.
- **Path B — split into two characteristics.** Keep `net amount` invoice-scoped; mint a new `order_net_amount` (or `document_net_amount`) characteristic for orders. Higher overhead — every entity needs to pick the right characteristic; sibling entities like Goods Receipt would inherit ambiguity.

**Recommendation:** Path A. The semantic core is "pre-tax document total"; the document class is contextually clear from the entity binding. Cross-document monetary characteristics (compare: `currency code`, `exchange rate`, `tax`) all follow the document-general pattern; `net amount`'s narrow definition is an outlier.

### 3.2 `gross amount` — OVER_NARROW

**Definition:** *"Invoice total monetary amount including applicable tax and gross-up components. Distinct from net amount, tax amount alone, discount amount, posted amount, outstanding amount, and cleared amount."*

**Current active bindings:** Customer Invoice, Remittance Advice, Supplier Invoice.

**Why this matters:** Same shape as `net amount` — narrowly defined as "invoice total" but operator-driven binding to Remittance Advice already stretches the definition (RA references invoices but is a payment-side artifact). Future SO × gross amount, PO × gross amount, GR × gross amount would all park.

**Recommendation:** Broaden in lockstep with `net amount` (Path A symmetry). Suggested text: *"Document total monetary amount including applicable tax and gross-up components. Distinct from net amount (pre-tax), tax amount alone, discount, posted amount, outstanding amount, and cleared amount."*

### 3.3 `posted amount` — MIXED_BINDINGS

**Definition:** *"The **per-line** monetary amount of a financial transaction as recorded in the accounting ledger at posting time, expressed in the document currency. Distinct from net, gross, outstanding, or cleared amounts — it is the raw amount written to the ledger line as the transaction was posted."*

**Current active binding:** Customer Invoice (1, header-level).

**Why this matters:** The definition says **per-line**, but the only binding is to the CI **header**. This is a pre-existing inconsistency surfaced (but not introduced) by Wave A's Tier 2 analysis. Mirroring SI × posted amount under the current state would propagate the mismatch to AP.

**Three paths to resolve:**

- **Path C — supersede CI × posted amount header binding, rebind to CILI.** Most semantically correct: posted amounts ARE per-line in SAP (BSEG-WRBTR / DMBTR). One supersession + one new BC.
- **Path D — broaden definition to "header or line".** *"The monetary amount of a financial transaction as recorded in the accounting ledger at posting time, expressed in the document currency — at either header or line granularity, depending on document conventions."* Lowest churn; accepts header-level use.
- **Path E — split into `posted amount header` + `posted amount line`.** Cleanest but introduces two near-synonyms; the no-synonym-admission rule in the Vocabulary Evidence Framework would need an explicit carve-out.

**Recommendation:** **Path C** (supersede + rebind) is the foundationally-correct fix; Path D is acceptable if operator prioritises lower churn over per-line discipline.

### 3.4 `ordered quantity` — mild MIXED_BINDINGS

**Definition:** *"Number of units requested **on an order**."*

**Current active bindings:** CILI, GR Line, PO Line, SOL.

**Why this matters:** Definition says "on an order"; CILI and GR Line are not orders (invoice line and receipt line, respectively). Convention in SAP/ERP systems is to copy the originally-ordered quantity onto downstream documents (invoice, receipt) for variance tracking. The current bindings reflect this convention — but the definition does not.

**Recommendation:** Soft broadening — *"Number of units **originally requested on the originating order**, carried through to downstream documents (invoice, receipt) for variance tracking against actually-delivered or actually-billed quantity."* No amendment is strictly required (the panel may accept the existing convention if asked) but the definition's word "on" is misleading.

### 3.5 `effective date` — OPERATOR_DECISION_REQUIRED

**Definition:** *"Date from which a record, rate, or agreement becomes valid."*

**Current active bindings:** Credit Status (status validity), Currency Exchange Rate (rate effective), Customer Invoice (status validity, **timestamp granularity** via `date_time` representation_term).

**Why this matters:** Two distinct semantic intents are already living under one characteristic — "this status now applies" (Credit Status, CI) and "this rate now applies" (Currency Exchange Rate). The CI binding is also the only one using `date_time` granularity. Wave A's held Tier 2 question (SI × effective date) is ambiguous against this background.

**Recommendation:** Operator decides — either keep as is and let the entity context disambiguate, or NEEDS_SPLIT into `effective from` (rate/agreement validity) + `status as-of` (status-record validity timestamp).

## 4. RUNTIME_DERIVED_ONLY confirmations

These should **not** be BCF-bound, regardless of how attractive a binding looks:

| Term | Reason |
|---|---|
| `fiscal period` | Per D364 / DEC-d7e7a0 the canonical fiscal period is derived from `posting date` via the tenant fiscal calendar substrate at canonical resolution. It is not a source field. Keep `lifecycle_state='draft'` and do not bind. |
| `cycle time` | A duration metric, computed from start/end timestamps. Lives at the MC layer. |

## 5. Safe-autonomous-reuse whitelist (post-audit)

Characteristics safe for an autonomous Wave-B-style sweep (operator authorises bounded waves; per-candidate eligibility rules still apply):

```
clearing date         (document-general, 4 active bindings)
country code          (general)
currency code         (general, 14 bindings)
delivered quantity    (general; line-only in practice)
discount              (general)
document date         (general)
due date              (general; current binding invoice-only)
exchange rate         (general, 7 bindings)
line number           (line-only, general within line entities)
payment terms         (general)
posting date          (general; mild caveat on PO commitment accounting)
sent date             (general; invoice-only in current use, safe to extend)
status                (maximally general, 22 bindings)
system entry date     (general; AP-only in current use, safe to extend)
tax                   (general, 8 bindings)
tax rate              (general; line-only in practice)
```

## 6. Hold-from-autonomous list (require operator decision first)

```
net amount            (OVER_NARROW — amend before reuse)
gross amount          (OVER_NARROW — amend before reuse)
posted amount         (MIXED_BINDINGS — supersede or amend)
ordered quantity      (soft MIXED_BINDINGS — clarify wording)
effective date        (OPERATOR_DECISION_REQUIRED — split vs keep)
delivery date         (intentionally narrow post-Phase-1; do not autonomously add)
document type code    (accounting-scoped; AR/AP only)
invoice receipt date  (AP-only by design)
system entry date     (currently AP-only; extending requires explicit operator nod)
value date            (banking-specific by design)
payment amount        (payment-specific by design)

# Orphans (entity binding requires operator decision)
expiry date
interest rate
lead time
note

# Runtime-derived (do not bind)
cycle time
fiscal period
quantity on hand      (no inventory entity admitted yet)
```

## 7. Recommended next execution sequence

1. **Decide `net amount` + `gross amount` broadening** (Path A symmetry). Two `POST /api/bcf/registry/characteristics/{id}/amend-definition` calls. Lowest churn; unblocks all order/receipt/payment monetary parity reuse.
2. **Decide `posted amount` resolution** (Path C supersede-and-rebind preferred, Path D broaden acceptable).
3. **(Optional) Decide `ordered quantity` definition rewording.**
4. **Resume Wave B Tier 1 from whitelist.** With `net amount` + `gross amount` broadened, the original Wave B candidate set runs without the SO × net amount park. The 8-candidate list from Wave B Step 1 becomes:
   - SO × net amount (unlocked by §7.1)
   - PO × exchange rate (whitelist-safe)
   - SOL × line number (whitelist-safe)
   - SOL × tax rate (whitelist-safe)
   - POL × tax rate (whitelist-safe)
   - POL × delivered quantity (whitelist-safe)
   - SI Line × discount (whitelist-safe)
   - SI Line × ordered quantity (depends on §7.3 — without amendment, panel may park on the "on an order" wording)
5. **Operator-guided orphan wave.** Per-orphan entity decision: bind `expiry date` / `interest rate` / `lead time` / `note` to operator-selected entities under standard panel runs. Hold `quantity on hand` until an inventory entity is admitted; hold `cycle time` and `fiscal period` permanently (runtime-derived).
6. **Held Tier 2 from Wave A.** After `posted amount` resolution, the SI × posted amount question resolves automatically. The SI × effective date question still needs §3.5 clarification.

## 8. Operational state (carried forward)

- bc-core PID 29912 from runtime worktree `C:\MyProjects\bc-core-runtime` at `c63db8ed`, healthy.
- bc-ai PID 28444, port 4300, healthy.
- Dirty primary worktree `C:\MyProjects\bc-core` untouched.
- DDL 15 in place; MMS recovery closed.
- Wave A's 4 SI header BCs active.
- Parked panel run `be8bea24-…` (Sales Order × net amount) sits in `bcf.panel_output_record` awaiting operator action — either confirm a definition broadening upstream (after §7.1) and re-run, or no-action and leave parked for audit.
- No substrate writes performed by this audit (read-only).

## 9. Non-goals of this audit

- Does **not** amend any characteristic definition (operator authorisation required).
- Does **not** supersede any BC or characteristic.
- Does **not** mint new characteristics.
- Does **not** run any panel.
- Does **not** decide the operator-facing splits (e.g. `effective date` NEEDS_SPLIT) — only surfaces the choice.

Held for operator decision on §7 sequencing.
