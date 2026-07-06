---
title: BCF Characteristic Amendment Doctrine — Reconciling DEC-26b6e2 with the Governed amend-definition Endpoint (2026-06-23)
description: Held doctrine packet drafting a successor-ADR amendment to DEC-26b6e2. Ratifies the in-place governed amend-definition endpoint (PR #343 / TSK-4c6fbd) only under a strict six-condition editorial-amendment test; meaning-bearing scope changes continue to require supersedeCharacteristic. Applies the test retrospectively to four historical amendments (delivery date broaden+narrow, invoice receipt / system entry split, net amount, gross amount) and concludes on remediation. Proposes the SOL × line number parked-panel disposition independently. No authoring, no registration with DevHub.
status: held
authority: implementation-doctrine
date: 2026-06-23
project: bc-docs-v3
domain: contracts
subdomain: semantic-vocabulary
focus: lifecycle
governing_adr_target: DEC-26b6e2
related_docs: [bcf-grounding-recheck-2026-06-23.md, bcf-characteristic-scope-audit-2026-06-23.md, bcf-wave-a-supplier-invoice-header-parity-closeout-2026-06-23.md]
---

# BCF Characteristic Amendment Doctrine — Reconciling DEC-26b6e2 with the Governed `amend-definition` Endpoint (2026-06-23)

## 0. Why this exists

DEC-26b6e2 ("Immutable Characteristic Atoms", decided 2026-05-22) says active characteristic definitions are **"never edited in place and never versioned"** — every correction goes through `supersedeCharacteristic`, minting a new `characteristic_id`. PR #343 / TSK-4c6fbd (shipped sometime between 2026-06-19 and 2026-06-20) added a new endpoint `POST /api/bcf/registry/characteristics/{id}/amend-definition` that **does** edit definitions in place — under a governed cert and an append-only `characteristic_definition_amendment` ledger row — and the service docstring at `registry-authoring.service.ts:1142` explicitly states this is an "ADR refinement (DEC-26b6e2): term frozen at publication; definition editorially amendable only via this method."

The refinement was implemented but never formalized as a successor ADR. The substrate CHECK constraint `characteristic_definition_amendment_correction_class_chk = 'editorial'` already enforces that **only editorial amendments** can pass through this path — meaning-bearing changes are structurally blocked from the amend-definition ledger. But what "editorial" means in operational terms has been left to judgement, and that ambiguity has now produced two outcomes worth examining: the 2026-06-20 `delivery date` broadening (which was substantively meaning-bearing and had to be reversed the next day), and the 2026-06-23 `net amount` + `gross amount` broadenings (this session, currently in the substrate as `correction_class='editorial'`).

This packet ratifies the amend-definition endpoint **only under a strict six-condition editorial-amendment test**, applies the test to the four historical amendments, and surfaces remediation if any fails the test.

## 1. The strict editorial-amendment test (proposed)

An in-place `amend-definition` call is the doctrinally-correct path **if and only if all six conditions below hold**. If any one fails, the change is meaning-bearing and MUST go via `supersedeCharacteristic` (minting a new `characteristic_id`).

| # | Condition | What it tests |
|---|---|---|
| **E1** | The characteristic `term` is unchanged. | DEC-26b6e2 freezes the term at publication. The amend endpoint does not touch `characteristic.term`; this condition is mechanically enforced. |
| **E2** | The characteristic's bound representation_term, data_type, and (D442) semantic_role are unchanged. | These three shape attributes pin the characteristic's substrate identity at the type / role level. Any change here moves the characteristic into a different vocabulary cell. |
| **E3** | No new semantic class is introduced. | The denotation class — what kind of thing the characteristic refers to — is the same before and after. "Invoice net amount" and "document-level net amount" share the same denotation class (pre-tax document monetary total). "Physical delivery" and "document receipt" are DIFFERENT denotation classes; the latter is not a refinement of the former. |
| **E4** | The amendment clarifies / removes accidental wording, OR aligns the definition with already-governed active bindings. | The amendment's editorial purpose is to make the definition true to the substrate that's already in place — not to expand into new substrate. If the change is driven by a pre-existing scope leak (an active binding that the prior definition was inconsistent with), aligning the definition is editorial. |
| **E5** | No existing valid binding becomes invalid. | Existing active BCs were authored and certified against the prior definition. An amendment that would invalidate any of them is meaning-bearing — the affected BCs would need a governed rebind, which is the exact "silent re-pointing of consuming concepts" failure DEC-26b6e2 was written to prevent. |
| **E6** | No future binding becomes valid **solely** by semantic expansion into a new class. | New bindings *may* become valid after the amendment — but only if they belong to a class the substrate already represented (per E4). If a class genuinely new to this characteristic becomes admissible solely as a result of the amendment, that is meaning-bearing. |

**Operational interpretation of "new class" (E3 / E6).** A class is "already represented" iff at least one active BC on the characteristic at amendment time binds to an entity of that class. The class taxonomy referenced here is the same one §11.6 of the Vocabulary Evidence Framework uses operationally — invoice / order / payment / receipt / shipment / etc.

**Default disposition when uncertain.** If any condition is ambiguous, the doctrine default is supersession, not amendment. Editorial is the narrow path; supersession is the safe path. This matches DEC-26b6e2's spirit.

## 2. Proposed successor ADR

**Title.** *Editorial Amendment of Active Characteristic Definitions — Refinement of DEC-26b6e2*

**Status.** `proposed` (would become `decided` on operator approval; this packet does **not** register it with DevHub).

**Filename.** Generated atomically by `devhub_decision_record` at registration time. Path will be `bc-docs-v3/docs/adrs/ADR-{shortuid}.md`. Do not pre-allocate.

**Supersedes / amends.** Refines DEC-26b6e2 without superseding it. DEC-26b6e2's core (active characteristics are immutable semantic atoms; term frozen; supersession is the principal correction path) stands. This refinement narrows the conditions under which the amend-definition endpoint is the doctrinally-correct path.

**Context (proposed text).**
> DEC-26b6e2 froze active characteristic definitions in place and required `supersedeCharacteristic` for all corrections. PR #343 / TSK-4c6fbd (June 2026) added an in-place governed `amend-definition` endpoint to close the IPCT Path P structural-circular gap surfaced by date-semantics work, on the premise that some corrections are non-denotation-changing and the supersession path is operationally heavy for typo / clarity fixes. The implementation enforces `correction_class='editorial'` only via a DB CHECK constraint, but the operational meaning of "editorial" was never formalized as ADR text. The 2026-06-20 `delivery date` broadening showed that an in-place amendment can silently introduce a denotation-changing scope shift if "editorial" is interpreted permissively. A strict structural test is needed.

**Decision (proposed text).**
> Active characteristic definitions remain immutable atoms (DEC-26b6e2). The in-place `amend-definition` endpoint is the doctrinally-correct path if and only if all six conditions E1–E6 of the strict editorial-amendment test hold. If any condition fails, the change is meaning-bearing and MUST go via `supersedeCharacteristic` (a new `characteristic_id`, with `characteristic_supersession.correction_class` carrying the audit classification). The substrate CHECK constraint `characteristic_definition_amendment_correction_class_chk='editorial'` continues to enforce that only editorial amendments enter the amendment ledger. Operator-direct recommendation + cert + amend-definition continues to mint the audit chain at the editorial path; supersession + new characteristic + rebinding continues to mint the audit chain at the meaning-bearing path.

**Consequences (proposed text).**
> - Editorial amendments preserve `characteristic_id` and term and produce one `characteristic_definition_amendment` ledger row per amendment.
> - Meaning-bearing scope changes mint a new `characteristic_id`; existing BCs on the predecessor remain historically correct; new BCs may bind to the successor; concept-level rebind is its own governed act.
> - The six-condition test makes the editorial / meaning-bearing classification deterministic at amendment time — no post-hoc reclassification.
> - DEC-26b6e2's no-silent-rebind guarantee is preserved: in-place amendment is allowed only when no existing binding's meaning is changed by the amendment (E5).

## 3. Retrospective application of the test

### 3.1 `delivery date` — broadening 2026-06-20 (amendment `5948bfe3-…`)

| Condition | Verdict | Reasoning |
|---|---|---|
| E1 term unchanged | ✓ | `delivery date` unchanged. |
| E2 shape unchanged | ✓ | `date` / `date` / `temporal` unchanged. |
| E3 no new semantic class | ✗ | Broadened from "physical delivery" (class 8 fulfillment event) to "deliverables — goods, services, **or documents**". Documents are not physical things; document receipt is a different denotation class (class 9 admission). **A new semantic class was introduced.** |
| E4 clarifies / aligns | ✗ | At amendment time, `delivery date` had **only one active binding**: `Customer Shipment × delivery date`. No invoice-class or document-class binding pre-existed. The amendment was not aligning the definition with already-governed substrate; it was creating new substrate. |
| E5 no existing binding invalidated | ✓ | The pre-existing `Customer Shipment × delivery date` binding remained valid. |
| E6 no new class admitted solely by expansion | ✗ | `Supplier Invoice × delivery date` (the new binding the amendment enabled) was solely admitted by semantic expansion into the document-receipt class. |

**Verdict: FAIL on E3, E4, E6.** This was a meaning-bearing change that took the editorial path. Should have been `supersedeCharacteristic` minting `delivery_date_v2` with the broader definition (or, more correctly, an entirely new characteristic name like `invoice_receipt_date` — which is what eventually happened).

**Current substrate state.** The 2026-06-20 broadening was reversed on 2026-06-21 (narrowing amendment `47896fe4-…`) and `Supplier Invoice × delivery date` was superseded; `invoice receipt date` and `system entry date` were admitted as fresh characteristics. The end state is doctrinally clean — the path to get there was not.

### 3.2 `delivery date` — narrowing 2026-06-21 (amendment `47896fe4-…`)

| Condition | Verdict | Reasoning |
|---|---|---|
| E1 term unchanged | ✓ | |
| E2 shape unchanged | ✓ | |
| E3 no new semantic class | ✓ | Narrowing reduced the class; did not add one. |
| E4 clarifies / aligns | ✓ | Restored the definition to the physical-delivery class, aligned with the original `Customer Shipment × delivery date` binding. |
| E5 no existing binding invalidated | ✗ | **At narrowing time, `Supplier Invoice × delivery date` was still an active binding** (the BC supersession happened separately). The narrowing made that BC's binding invalid relative to the new definition. |
| E6 no new class admitted solely by expansion | ✓ (vacuous — narrowing, not expansion) | |

**Verdict: FAIL on E5.** The narrowing was substrate-correcting (good intent) but should have been ordered differently: first supersede the offending `SI × delivery date` BC (which did happen), then either amend or supersede the characteristic. The amendment-while-an-invalid-binding-still-active sequence is foundationally inconsistent under E5. If the test had been in force, the narrowing would have been rejected at the panel stage and routed to supersession.

**Practical impact.** Low — the SI × delivery date supersession + the narrowing landed close together in time and the resulting state is clean. But the audit trail shows an interval where the definition contradicted an active binding.

### 3.3 `invoice receipt date` / `system entry date` split

Not amendments — these were *new characteristic admissions* via `registry_author_vocabulary`. The editorial test does not apply (no in-place definition change to an existing characteristic). The path was doctrinally correct.

### 3.4 `net amount` amendment 2026-06-23 (amendment `6d93beae-…`)

| Condition | Verdict | Reasoning |
|---|---|---|
| E1 term unchanged | ✓ | `net amount` unchanged. |
| E2 shape unchanged | ✓ | All bindings remain `amount` / `decimal` / `amount`. |
| E3 no new semantic class | ✓ | Denotation class — "pre-tax document monetary total" — is unchanged. The broadening removed the word "Invoice" from a definition that was inconsistent with the substrate (PO already bound it). |
| E4 clarifies / aligns | ✓ | At amendment time, active bindings were Customer Invoice, **Purchase Order**, Supplier Invoice. PO is an order-class document. The prior definition said "Invoice monetary amount …" — a textual misalignment with the substrate. The amendment aligned the definition with the already-governed PO binding. |
| E5 no existing binding invalidated | ✓ | All three pre-existing active BCs remain valid under the broader definition. |
| E6 no new class admitted solely by expansion | ✓ | The order class was already represented (via PO × net amount) before the amendment. Subsequent SO × net amount admission (fresh panel `60669a2e-…`) was admitted into a class already present in the substrate. |

**Verdict: PASS on all six.** Editorial under the strict test. **No remediation required.** Amendment `6d93beae-…` was the doctrinally-correct path.

### 3.5 `gross amount` amendment 2026-06-23 (amendment `bf4880c0-…`)

| Condition | Verdict | Reasoning |
|---|---|---|
| E1 term unchanged | ✓ | |
| E2 shape unchanged | ✓ | All bindings remain `amount` / `decimal` / `amount`. |
| E3 no new semantic class | ✓ | Denotation class — "post-tax document monetary total" — unchanged. |
| E4 clarifies / aligns | ✓ (with caveat) | At amendment time, active bindings were Customer Invoice, **Remittance Advice**, Supplier Invoice. RA is a payment-side document, not an invoice — the prior definition's "Invoice total" was a textual misalignment with the RA binding. The amendment aligned. *Caveat:* RA's status as "non-invoice" is borderline (it's invoice-adjacent / settlement-adjacent), so the alignment argument is weaker than for net amount. |
| E5 no existing binding invalidated | ✓ | All three pre-existing active BCs remain valid. |
| E6 no new class admitted solely by expansion | ✓ (with caveat) | The "payment-adjacent" class was already represented via RA. Subsequent order-class bindings (SO/PO × gross amount) would be admitted into a class beyond RA. Under the operator's wording — *"no future binding becomes valid **solely** by semantic expansion into a new class"* — the "solely" qualifier reads as: if alignment with already-governed substrate is the *primary* driver and new-class admission is *secondary*, the condition passes. The pre-existing RA binding provides the primary driver. |

**Verdict: PASS on all six (with two borderline marks on E4/E6).** Editorial under the strict test. **No remediation required.** Amendment `bf4880c0-…` was the doctrinally-correct path — but it was closer to the editorial / meaning-bearing line than `net amount`. A future amendment of similar shape on a characteristic with **only invoice-class bindings** (no pre-existing scope leak to align against) would FAIL E4 and FAIL E6 — that future amendment would need supersession.

## 4. Conclusion on net / gross amount disposition

**Both amendments are valid editorial amendments under the proposed strict test.** No remediation required. The audit chain stands:
- net amount: amendment `6d93beae-…`, cert `d067ea91-…`, panel_run `61bd664f-…`.
- gross amount: amendment `bf4880c0-…`, cert `76f427b1-…`, panel_run `35d2c6ef-…`.

Both pass E1–E5 cleanly. E6 passes on the operator's "solely" reading, with the gross amount case slightly closer to the line.

**Recommendation for future amendments:** The pattern that worked here (pre-existing scope leak that the amendment aligns to) is the safe editorial shape. The pattern that *failed* on `delivery date` (no pre-existing leak; the amendment is admitting an entirely new class) is the unsafe shape — that pattern MUST go through supersession.

## 5. Parked SOL × line number panel (`0a5d2e5c-…`)

Independent of the amendment doctrine. The grounding-recheck (Q5/Q6) concluded:
- `identifier` is the doctrinally-supported representation_term per ISO 11179-5 + Vocabulary Evidence Framework §5 closed-set.
- Substrate evidence (6 sibling line-number bindings, all `identifier` / `string` / `identity`) is settled, not drift.

This doctrine packet does not change those conclusions. **After operator acceptance of this packet, the SOL × line number parked panel may proceed to operator-confirm** via `POST /api/bcf/registry-shape-certifications/confirm` with rationale stating the doctrine basis. Confirming would consume the parked panel and author the BC under the existing Maker draft. This is independent of the amendment doctrine — no characteristic amendment is involved.

## 6. What this packet deliberately does not do

- Does not register an ADR with DevHub. Title and shape are proposed; the operator decides whether to file via `devhub_decision_record`. CLAUDE.md atomicity rule applies (do not pre-allocate D-code; allocator assigns at registration).
- Does not amend any characteristic.
- Does not supersede any characteristic.
- Does not confirm any parked panel.
- Does not edit code. The service docstring at `registry-authoring.service.ts:1142-1145` already states the refinement; if the operator wants to add a pointer to the new ADR after registration, that's a one-line code edit deferred to a separate authorized turn.
- Does not commit anything in bc-docs-v3. This packet joins the deferred uncommitted batch alongside the audit + grounding-recheck.

## 7. Recommended next action

1. **Operator review of this packet.** Accept / reject / refine the six-condition test.
2. **If accepted, register the ADR** via `devhub_decision_record` (operator runs; do not specify a `decision_code` — the allocator assigns atomically per CLAUDE.md D334 rule). Title: *"Editorial Amendment of Active Characteristic Definitions — Refinement of DEC-26b6e2"*. Domain: `contracts`. Subdomain: `semantic-vocabulary`. Focus: `lifecycle`. Supersedes / amends: refines DEC-26b6e2.
3. **After the ADR lands**, confirm the parked SOL × line number panel `0a5d2e5c-…` independently (§5 above).
4. **Resume Wave B** for the remaining candidates that depend on the safe whitelist (PO × exchange rate already done — was #2; remaining: SOL × tax rate, POL × tax rate, POL × delivered quantity, SI Line × discount). SI Line × ordered quantity continues to be held pending §3.4 wording clarification (independent of this packet).
5. **No retrospective remediation needed.** net amount + gross amount amendments stand as doctrinally-correct editorial under the new test.

## 8. Operational state (unchanged)

- bc-core PID 29912 from `C:\MyProjects\bc-core-runtime` at `c63db8ed`, healthy.
- bc-ai PID 28444, port 4300, healthy.
- Dirty `C:\MyProjects\bc-core` worktree untouched.
- DDL 15 in place. MMS recovery closed. PCIC v2 active.
- Wave A's 4 SI header BCs active. Wave B fresh: 2 authored (SO × net amount, PO × exchange rate); SOL × line number parked at `0a5d2e5c-…`.
- net amount + gross amount editorially broadened (this turn); under the proposed test, both stand as doctrinally-correct.
- This packet untracked in bc-docs-v3 working tree alongside prior held packets; commit batch still deferred.

Held for operator decision on the proposed test + ADR registration.
