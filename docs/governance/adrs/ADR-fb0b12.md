---
uid: DEC-fb0b12
title: "Editorial Amendment of Active Characteristic Definitions — Refinement of DEC-26b6e2"
description: "Refines DEC-26b6e2 by ratifying the governed in-place amend-definition endpoint only under a strict six-condition editorial test (E1-E6); meaning-bearing changes continue to require supersedeCharacteristic; net amount + gross amount 2026-06-23 amendments stand under the test; delivery date 2026-06-20 broadening recorded as historical wrong-path precedent."
status: decided
date: 2026-06-23T11:09:57.648Z
project: bc-docs
domain: contracts
subdomain: semantic-vocabulary
focus: lifecycle
---

# Editorial Amendment of Active Characteristic Definitions — Refinement of DEC-26b6e2

## Context

DEC-26b6e2 froze active characteristic definitions in place and required supersedeCharacteristic for every correction. PR #343 / TSK-4c6fbd subsequently added a governed in-place amend-definition endpoint to close the IPCT Path P structural-circular gap, with the substrate CHECK constraint characteristic_definition_amendment_correction_class_chk enforcing correction_class='editorial' only. The service docstring claimed an "ADR refinement" of DEC-26b6e2 but no successor ADR ever formalized what "editorial" means operationally. The ambiguity produced two observable outcomes: the 2026-06-20 delivery date broadening (a substantively meaning-bearing change that took the editorial path and had to be reversed the next day) and the 2026-06-23 net amount + gross amount broadenings (this session). Operator-held packet bcf-characteristic-amendment-doctrine-2026-06-23.md surfaced the tension and proposed a strict six-condition editorial-amendment test. Operator accepted Option I (ratify amend-definition under the strict test; net/gross stand; default uncertainty to supersession). This ADR formalizes that decision.

## Decision

Active characteristic definitions in the Business Concept Registry remain immutable semantic atoms (DEC-26b6e2 stands). The governed in-place `amend-definition` endpoint (PR #343 / TSK-4c6fbd, `POST /api/bcf/registry/characteristics/{id}/amend-definition`) is the doctrinally-correct path **if and only if all six conditions E1-E6 of the strict editorial-amendment test below hold**. If any one condition fails, the change is meaning-bearing and MUST go via `supersedeCharacteristic` (a new `characteristic_id`).

This ADR **refines DEC-26b6e2 without superseding it**. DEC-26b6e2's core - active characteristics are immutable semantic atoms; term frozen at publication; supersession is the principal correction path - stands. This ADR narrows the conditions under which the amend-definition endpoint is the doctrinally-correct path and formalizes what "editorial" means operationally.

### The strict editorial-amendment test (E1-E6)

An in-place `amend-definition` call is allowed if and only if all six hold:

- **E1 Term unchanged.** The characteristic's `term` is unchanged. (Mechanically enforced - the amend endpoint does not touch `characteristic.term`.)
- **E2 Shape unchanged.** The characteristic's bound `representation_term`, `data_type`, and `semantic_role` (D442) are unchanged across all active BCs. These three shape attributes pin the characteristic's substrate identity at the vocabulary cell.
- **E3 No new semantic class introduced.** The denotation class - what kind of thing the characteristic refers to - is the same before and after. "Invoice net amount" and "document-level net amount" share the same denotation class (pre-tax document monetary total). "Physical delivery" and "document receipt" are different denotation classes; the latter is not a refinement of the former.
- **E4 Clarifies wording or aligns with already-governed bindings.** The amendment removes accidental wording OR aligns the definition with active BC bindings already in place. The editorial purpose is to make the definition true to the substrate that's already in place, not to expand into new substrate.
- **E5 No existing valid binding is invalidated.** Existing active BCs were authored and certified against the prior definition. An amendment that would invalidate any of them is meaning-bearing - the affected BCs would need a governed rebind, which is the exact "silent re-pointing of consuming concepts" failure DEC-26b6e2 was written to prevent.
- **E6 No new class admitted solely by semantic expansion.** New bindings may become valid after the amendment, but only if they belong to a class the substrate already represented (per E4). If a class genuinely new to the characteristic becomes admissible solely as a result of the amendment, that is meaning-bearing.

### Default disposition under uncertainty

If any condition is ambiguous, the doctrine default is **supersession**, not amendment. Editorial is the narrow path; supersession is the safe path. This matches DEC-26b6e2's spirit.

### Substrate enforcement (already in place)

- Substrate CHECK constraint `characteristic_definition_amendment_correction_class_chk` permits `correction_class='editorial'` only on the amendment ledger. Meaning-bearing changes are structurally blocked from the amendment path.
- The amend endpoint preserves `characteristic_id` and `term` (E1 mechanically enforced).
- Cert pairing `(registry_amend_definition, characteristic)` governs the editorial path; cert pairing `(registry_supersede, characteristic)` governs the meaning-bearing path. The two paths emit distinct audit chains.

### Out of scope for amend-definition

The amend-definition endpoint MUST NOT be used to change `representation_term`, `data_type`, or `semantic_role`. Those shape attributes pin the characteristic's substrate identity (E2); any change requires supersession with a new `characteristic_id`. The endpoint is also structurally barred from touching `characteristic.term` (E1).

### Retrospective application

| Amendment | Date | E1 | E2 | E3 | E4 | E5 | E6 | Verdict |
|---|---|---|---|---|---|---|---|---|
| `delivery date` broadening (`5948bfe3-...`) | 2026-06-20 | OK | OK | FAIL (documents are a new class) | FAIL (no pre-existing leak) | OK | FAIL (SI binding admitted solely by expansion) | **Wrong path** - should have been supersession or a new characteristic. End state corrected via subsequent narrowing + BC supersession + admission of `invoice receipt date` / `system entry date` as separate characteristics. Recorded as historical wrong-path precedent. |
| `delivery date` narrowing (`47896fe4-...`) | 2026-06-21 | OK | OK | OK | OK | FAIL (SI x delivery date still active at narrowing time) | OK (narrowing) | **Substrate-correcting intent but non-compliant ordering.** Should have been: supersede the offending BC first, then either amend or supersede the characteristic. Practical impact low - end state is clean. |
| `invoice receipt date` / `system entry date` admissions | 2026-06-21 | N/A - new characteristic admissions, not amendments. Test does not apply. Path was correct (`registry_author_vocabulary`, new `characteristic_id`). | | | | | | **N/A** |
| `net amount` amendment (`6d93beae-...`) | 2026-06-23 | OK | OK | OK | OK (PO x net amount predated, providing alignment target) | OK | OK (order class was already represented via PO) | **PASS** - editorial under the strict test. No remediation. |
| `gross amount` amendment (`bf4880c0-...`) | 2026-06-23 | OK | OK | OK | OK with caveat (RA x gross amount provided alignment target; RA is payment-adjacent, borderline) | OK | OK on the "solely" qualifier | **PASS** - editorial under the strict test. No remediation. Closer to the line than net amount; future amendments of similar shape on a characteristic with only invoice-class bindings (no pre-existing scope leak) would FAIL E4 and E6. |

### Consequences

- Editorial amendments preserve `characteristic_id` and `term` and produce one `characteristic_definition_amendment` ledger row per amendment under the `(registry_amend_definition, characteristic)` cert pairing.
- Meaning-bearing scope changes mint a new `characteristic_id` via `supersedeCharacteristic` under the `(registry_supersede, characteristic)` cert pairing. Existing BCs on the predecessor remain historically correct (DEC-26b6e2); new BCs may bind to the successor; concept-level rebind is its own governed act.
- The six-condition test makes the editorial / meaning-bearing classification deterministic at amendment time - no post-hoc reclassification.
- DEC-26b6e2's no-silent-rebind guarantee is preserved: in-place amendment is allowed only when no existing binding's meaning is changed (E5) and no new class is admitted solely by expansion (E6).
- net amount + gross amount 2026-06-23 amendments stand under the test. No retrospective remediation. The two parked panels (`be8bea24-...` SO x net amount, `0a5d2e5c-...` SOL x line number) are independently dispositioned: the former is functionally obsolete (a successor BC was authored via fresh panel `60669a2e-...`); the latter is resolvable via operator-confirm on representation_term doctrine grounds (`identifier` is correct per ISO 11179-5 + 6 sibling line-number bindings).
- Future amendments that match the unsafe pattern (no pre-existing leak; the amendment is admitting an entirely new class) MUST route via supersession.

### Authority and references

- Refines: DEC-26b6e2 (Immutable Characteristic Atoms, decided 2026-05-22).
- Foundation: Invariant I (meaning is evaluated once), Invariant III (state is immutable).
- Vocabulary Evidence Framework §11.2.3 (no silent broadening); §11.6 (source-attested vs resolver-stamped).
- Business Concept Registry §5 (representation_term closed set); §7 (supersession rule).
- Implementation: PR #343 / TSK-4c6fbd; service at `bc-core/src/registry/concept-registry/registry-authoring.service.ts:1147` (`amendCharacteristicDefinition`); substrate CHECK constraint `characteristic_definition_amendment_correction_class_chk`.
- Held packet: `bc-docs-v3/docs/implementation/bcf-characteristic-amendment-doctrine-2026-06-23.md` (source of the test text and retrospective table).
