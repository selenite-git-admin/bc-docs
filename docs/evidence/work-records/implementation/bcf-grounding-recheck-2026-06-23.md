---
title: BCF Grounding Recheck — Phase 1 (Foundation + BCF Doctrine) (2026-06-23)
description: Held re-grounding packet triggered by two BCF panel parks in one session (SO × net amount on invoice-scope leak, SOL × line number on identifier-vs-count). Phase-1 read-only review of Foundation invariants, contract grammar, evaluation boundaries, Business Concept Registry model, Vocabulary Evidence Framework (incl. §11 amendment + no-silent-broadening rule), characteristic immutability ADR DEC-26b6e2, and backbone breadth/batch doctrine. Answers eight grounding questions, surfaces a doctrine-vs-implementation tension between DEC-26b6e2 and the amend-definition endpoint (TSK-4c6fbd), and recommends next action.
status: held
authority: implementation-recheck
date: 2026-06-23
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: doctrine-grounding
related_docs: [bcf-characteristic-scope-audit-2026-06-23.md, bcf-wave-a-supplier-invoice-header-parity-closeout-2026-06-23.md]
---

# BCF Grounding Recheck — Phase 1 (2026-06-23)

Two BCF panel parks in one session — Sales Order × net amount (invoice-scope leak in `net amount` definition) and Sales Order Line × line number (representation_term identifier-vs-count disagreement) — signaled that doctrine itself may be unsettled in places, and that fast-track autonomy was extending past where doctrine actually grants it. This packet re-reads Foundation + BCF authority and surfaces what doctrine actually says, where it's silent, and one operative tension that should be resolved before any further autonomous BCF work.

Read-only. No panel calls, DB writes, amendments, code edits, or PR. The two parked panels (`be8bea24-…` and `0a5d2e5c-…`) remain untouched. The net amount + gross amount amendments earlier this turn (cert `d067ea91-…` / `76f427b1-…`, amendments `6d93beae-…` / `bf4880c0-…`) are surfaced for operator review here — they may or may not need re-classification under the doctrine reading below.

## 1. Doctrine summary

### Foundation (Tier 1 — re-read 2026-06-23)
- **Invariant I (meaning is evaluated once).** One Business Concept = one meaning. Synonyms and homonyms are structurally forbidden, not just detected. A characteristic carrying two distinct business meanings at the same time is an Invariant-I violation regardless of intent.
- **Invariant III (state is immutable).** Active artifacts are never altered in place; corrections are new versions. The five-state lifecycle (`draft → review → approved → active → superseded`) governs every active contract-family instance.
- **Invariant V (evaluation is non-replayable) and VI (evidence is emitted not inferred).** Audit reads preserved state; it does not re-derive. Each amendment / supersession act emits its own cert + ledger row.
- **Contract Grammar.** Business Concept Registry (DEC-02f5a9) supersedes the BF/BO/CF primitives. Concept identity is exactly `entity.property` — two levels, `UNIQUE(entity_id, property_id)`. Family / owner-domain / tags are classification, never identity. Standards (ISO 11179, OAGIS, XBRL, …) are evidence and candidate source — **never identity authority**.

### Business Concept Registry (Tier 2 — `business-concept-registry.md`)
- A property decomposes into a **characteristic** (`credit limit`, `balance`, `status`) and a **representation term** (`amount`, `date`, `code`, `quantity`, `count`, `indicator`, `identifier`, `text`).
- Representation terms are "a **small closed set** — the one place a standard contributes genuine content: the set is seeded from ISO 11179's, then owned" (§5).
- **Supersession rule (§7).** "Changing an entity's identity-bearing property set is supersession — a new entity. Adding a descriptive property to any entity is additive — non-superseding."
- **AI panel role (§10).** "The Context Authoring Panel is **not a duplicate checker.** It is a **concept-placement assistant.** … The irreversible-uniqueness guarantee comes from the registry's structure — not from embeddings, not from name matching, not from a standard."

### Vocabulary Evidence Framework (Tier 2 — `business-concept-registry-vocabulary-evidence-framework.md`)
- **§11.1 — System-agnosticism.** Source field names (BSEG-WRBTR, VBAP-NETWR, etc.) are evidence of where a classifier is physically carried — "**they are not semantic scope boundaries for platform characteristics**". A different source field family is **not** by itself justification for a scoped sibling characteristic.
- **§11.2 — Characteristic hygiene, three rules:**
  1. Generic characteristic labels require generic definitions.
  2. Entity-specific or source-specific examples MAY be cited as provenance inside a generic definition, but MUST NOT narrow the definition unless the label itself is scoped.
  3. **No silent characteristic broadening.** "If a candidate Business Concept depends on broadening the definition of an existing characteristic, the panel run must be **parked** for operator decision rather than silently broadened. Either the operator authorises broadening (removing provenance leakage) via the **governed characteristic-supersession path**, or the operator decides a scoped sibling is genuinely needed."
- **§11.3 — Canonical metric substrate vs source-diagnostic substrate.** Source-diagnostic BCs are optional; parked source-diagnostic BCs are *intentional deferrals*, not coverage gaps.
- **§11.6 — Source-attested vs resolver-stamped.** BCF characteristics declare *source-attested* fields. Resolver-stamped concepts (fiscal period, derived amounts) live at the Canonical Contract / canonical-resolution boundary — never at BCF.

### ADR DEC-26b6e2 — Immutable Characteristic Atoms (Tier 2 — direct quote)
> "Active Characteristics in the Business Concept Registry are **immutable semantic atoms.** Publication — the governed draft → active transition — freezes a characteristic's (term, definition) as its authoritative meaning. An active characteristic's term and definition are **never edited in place and never versioned**: there is no `concept_registry.characteristic_version` table and the characteristic row stays flat."
> "A published characteristic that needs correction is **superseded by a new Characteristic — a new characteristic_id** carrying the corrected (term, definition), authored through the normal governed F4-v2 / F3 path."
> "Existing BusinessConcepts remain bound to the predecessor characteristic — that binding is historically correct, the meaning they were authored and certified against. A concept adopts the successor only through a governed new business_concept_version that re-binds it, so a characteristic meaning change always re-enters concept-level governance."

The ADR explicitly distinguishes `correction_class = editorial` (typo / clarity, denotation unchanged) from `correction_class = meaning_bearing` (denotation changed), but **both** correction classes are recorded "**on a single authority**" (`characteristic_supersession`). The ADR's intent is that **any correction — editorial or meaning-bearing — produces a new characteristic_id via the supersession path**. Edits in place are not part of the model.

### BCF backbone breadth + batch doctrine (Tier 2 — `bcf-backbone-breadth-and-batch-doctrine.md`)
- **§2.3.** Optional diagnostic classifiers can remain deferred. Parked source-diagnostic BCs are intentional deferrals.
- **§3.1.** Run a full backbone slice in one session.
- **§3.4 — Continue-to-exhaustion rule.** "A batch runs to exhaustion. **Per-item failures do not halt the batch.** Panel `OPERATOR_REVIEW` verdict → log, park, continue." Fatal stops are reserved for bc-core/bc-ai unhealth, silent telemetry failure, direct-write/governance-bypass, schema mismatch, cross-registry mutation, prompt/cache drift.

## 2. Answers to the eight grounding questions

### Q1. What is the doctrinal rule for reusing a characteristic across entity classes?
**Reuse is the default; a characteristic is intended to be reusable across multiple entities.** `business-concept-registry.md` §5 names this directly: "A property *belongs to* exactly one entity. An entity may collect properties contributed by many business functions". The characteristic itself — the disambiguating semantic atom — is independent of the entity that binds it. Vocabulary Evidence Framework §11.1 reinforces: source-system carriers (BSEG, VBAP, EKKO) are evidence, not scope. A different source field family is not, by itself, justification for a scoped sibling.

**The constraint on reuse is semantic, not structural.** The same characteristic may bind to multiple entities iff its governed definition validly covers each binding. If the binding entity's business meaning is outside the definition's scope, the panel parks the binding.

### Q2. When is broadening editorial vs meaning-bearing?
**Doctrine + implementation are in apparent tension here. This is the operative tension worth resolving before any further amend-definition work.**

- **DEC-26b6e2 (decided, status unchanged on the ADR file as of 2026-06-23):** treats every correction — editorial OR meaning-bearing — as routing through the supersession path (a new `characteristic_id`). The two `correction_class` values are *audit metadata on one supersession authority*, not two different code paths.
- **PR #343 / TSK-4c6fbd (shipped):** introduced `POST /api/bcf/registry/characteristics/{id}/amend-definition` that *preserves* `characteristic_id` and term, and writes `characteristic_definition_amendment` ledger rows alongside the in-place definition update. The endpoint description claims it "refined" DEC-26b6e2 to *"term frozen; definition editorially amendable under (registry_amend_definition, characteristic) cert governance"*. But **the ADR file itself was not amended** — no amendment paragraph, no follow-up ADR superseding DEC-26b6e2's "never edited in place" clause.
- **Vocabulary Evidence Framework §11.2.3 (amended 2026-06-19):** the default for any broadening (especially one that "removes provenance leakage") is **supersession**, not in-place editorial amendment. The §11.2.3 wording — "via the governed characteristic-supersession path" — explicitly names the supersession path as the authorised path.

**Implication.** The amend-definition endpoint is doctrinally narrow: it's intended for genuine typo / clarity fixes that don't change denotation (DEC-26b6e2's "editorial" `correction_class`). Anything that broadens scope — even if the semantic core feels preserved — should arguably go through supersession per §11.2.3.

### Q3. Does "document-level net amount" legitimately remain the *same* characteristic as invoice-scoped net amount, or should it have been a supersession/split?
**Probably should have been supersession.** The broadening earlier this turn (amendments `6d93beae-…` / `bf4880c0-…`) used the amend-definition path. The reasoning at the time was that the *semantic core* (pre-tax document monetary total) is preserved across invoices, orders, RAs — only the *scope* widens.

Under the strict reading of DEC-26b6e2 + §11.2.3, this should have gone via `supersedeCharacteristic` minting a new characteristic_id. The argument *for* the in-place amend was Path A in the audit packet — "lowest churn; brings existing PO binding into definitional scope". The argument *against* (now surfaced by this recheck): the existing 3 active BC bindings on net amount (CI, PO, SI) were authored / certified against the **invoice-scoped** definition. Under the immutable-atoms ADR, those active BCs were correctly bound to the prior meaning at certification time. An in-place definition update silently re-points 3 active BCs to a broader meaning **without re-entering concept-level governance** — which is the "no-cascade rebind" failure mode DEC-26b6e2 explicitly calls out (§Context, ¶3): *"advancing active_version_id silently re-binds every consuming concept to a new meaning with no concept-level re-authoring or re-certification — meaning drift under a stable reference, failing Invariant I"*.

**The amend-definition path appears to reproduce exactly the failure mode DEC-26b6e2 was written to prevent.** Either:
- (a) PR #343's "refinement" is real and the ADR file is overdue for an amendment paragraph that makes the refinement official; OR
- (b) PR #343 is implementation drift from the ADR, the amend-definition endpoint should not have been used for scope-broadening, and the net/gross amount amendments should be remediated via the supersession path (mint new characteristic_ids with the document-general definition; let existing 3+3 BCs continue to bind the predecessor characteristic; let future SO/PO/GR/etc. BCs bind the successor).

This is a load-bearing operator decision. The held packet does **not** resolve it — it surfaces the tension.

### Q4. What does doctrine say about `representation_term`?
- **`business-concept-registry.md` §5:** *"Representation terms are a **small closed set** — the one place a standard contributes genuine content: the set is seeded from ISO 11179's, then owned."* Substrate enforces this through the CHECK constraint on `concept_registry.business_concept.representation_term`.
- **Vocabulary Evidence Framework M6 ("Not a bare representation term"):** representation_terms are vocabulary primitives, not characteristic names.
- **Vocabulary Evidence Framework X4 ("A representation-term word as the genuine semantic *head* of the property"):** allowed exception — e.g. `due date`, `tax rate`. The representation_term word may appear in a characteristic name when it IS the property's semantic head.
- ISO 11179-5 representation classes (the underlying corpus from which the BareCount closed set was seeded):
  - **Amount** — a monetary value;
  - **Code** — a value from a code list;
  - **Count** — a non-monetary numeric value obtained by counting (integer; "how many instances");
  - **Date** — a calendar date;
  - **Identifier** — a character string used to establish identity of an instance within an identification scheme;
  - **Indicator** — a yes/no-class signal;
  - **Quantity** — a numeric measurable value with a unit;
  - **Text** — free-form language content.

The closed-set discipline is doctrinally clear: panels MUST choose from this set; new representation_terms are not minted as part of business-concept authoring.

### Q5. Is `line number` as `identifier` doctrinally supported, or is `count` plausible?
**`identifier` is the doctrinally supported choice and the Maker was correct.** Under ISO 11179-5 (the seed corpus the closed set draws from):
- `Count` is a non-monetary numeric value obtained by counting — type integer; meaning is "how many instances". Operationally arithmetic ("there are 17 line items on this order" = `count`).
- `Identifier` is a character string establishing identity within a scheme. The line number on a PO/SO/Invoice line is *exactly* this: a value used to disambiguate one line from another within its parent document and to serve as the join key for downstream documents (delivery / billing) that reference lines individually.

The Checker's `count` argument confused the *cardinal* sense (how many lines exist) with the *ordinal* sense (which line is this within the document). Only the cardinal sense is genuinely a count; the ordinal sense is an identifier. Substrate evidence confirms: all 6 existing line-number BCs across distinct line entities (Bank Statement Line, Customer Invoice Line Item, Goods Receipt Line, Journal Entry Line, Purchase Order Line, Supplier Invoice Line) use `identifier` / `string` / `identity`. Substrate is internally consistent and aligned with ISO 11179. The Checker's objection is a representation_term-discipline misreading.

### Q6. Are existing line-number BCs evidence of a settled pattern or historical drift?
**Settled pattern.** Six independent BCs across six distinct line entities all chose `identifier` / `string` / `identity` over a year of BCF authoring. The substrate is internally consistent and consistent with ISO 11179. There is no superseded predecessor binding to a different representation_term. This is settled vocabulary, not historical drift.

The parked SOL × line number panel `0a5d2e5c-…` should be resolvable on the operator's affirmative judgement (`identifier` is correct per substrate + ISO 11179). The Maker draft is doctrinally sound and structurally consistent with the six existing siblings.

### Q7. What are the safe-autonomy rules for future BCF waves?
Synthesising across the read:

**The panel — not autonomous code — is the operative authority for what is safe.** §11.2.3 "no silent broadening" is the operative rule. Anything autonomous Wave-B-style work attempts must satisfy:
- the candidate's binding is *fully covered* by the existing characteristic's definition (no broadening required); AND
- the representation_term and data_type match an existing sibling pattern; AND
- the entity is active and the (entity, characteristic) pair has zero existing rows at any lifecycle.

If any of those fails, the panel parks. The §3.4 backbone batch doctrine says **continue-to-exhaustion through individual parks** (log + park + continue). That contradicts the session-level "halt on any park" rule the operator gave for Wave B / Wave B fresh. The operator's stricter rule is admissible (operator can be stricter than doctrine) but worth noting — the doctrine default is *not* halt-on-park.

**Pragmatic autonomy boundary.** Until the DEC-26b6e2 vs amend-definition tension (Q2/Q3) is resolved, autonomous waves should not propose any candidate that depends on broadening an existing characteristic's definition. The audit packet's safe-autonomous-reuse whitelist (16 characteristics) needs a per-characteristic definition-scope re-read against the actual binding the candidate proposes — name and shape match are not sufficient.

### Q8. What should happen to parked panels `be8bea24-…` and `0a5d2e5c-…`?

**`be8bea24-ca59-4d9c-a519-f32fc199cf71` (Sales Order × net amount):**
- Park reason: net amount was invoice-scoped at panel-run time.
- Current state: net amount has been editorially broadened to document-general (amendment `6d93beae-…`, 2026-06-23 09:28 UTC). The blocker is removed.
- A successor BC was already authored via a fresh panel run `60669a2e-…` (BC `0b5613d0-…`) on the now-broadened characteristic.
- **Disposition:** functionally obsolete — there is an active BC for SO × net amount via the fresh run. The parked panel record stays in `bcf.panel_output_record` as audit history. **Do not confirm** — it would attempt to write a second BC and collide with `uq_business_concept_value_identity`. Leave it parked as the historical record of the earlier panel run that correctly enforced no-vocabulary-stretch at that point in time.

**`0a5d2e5c-4a84-46b2-ab54-9653cc05256b` (Sales Order Line × line number):**
- Park reason: identifier vs count representation_term disagreement.
- Doctrine reading: `identifier` is correct (Q5).
- Substrate reading: 6 existing siblings all use `identifier`/`string`/`identity`.
- **Disposition options:**
  - **Confirm-the-parked** via `POST /api/bcf/registry-shape-certifications/confirm` with operator rationale stating: "`identifier` is the doctrinally-supported representation_term per ISO 11179-5 + Vocabulary Evidence Framework §5 closed-set + 6 sibling line-number bindings." This consumes the parked panel's recommendation directly.
  - **Re-run fresh panel** with the same candidate. With the substrate evidence still consistent, the panel may still park (the Checker's challenge isn't substrate-resolvable — it's a representation_term ontology disagreement). A fresh run does not change the underlying disagreement.
  - **Recommended:** Confirm-the-parked. Re-run would burn the same panel cost without changing the substrate signal.

## 3. Where doctrine is clear

- **Concept identity is `entity.property`** with structural uniqueness. (DEC-02f5a9 + §2-3 BC Registry)
- **Standards are evidence, never identity authority.** (DEC-02f5a9 §9, Vocabulary Evidence Framework §11.1)
- **Representation_term is a closed set** seeded from ISO 11179. (BC Registry §5, Vocabulary Evidence Framework §5)
- **No silent broadening** — broadening goes via supersession or scoped sibling, parked for operator decision. (Vocabulary Evidence Framework §11.2.3)
- **Reuse across entities** is the default; source-carrier differences are evidence, not scope. (Vocabulary Evidence Framework §11.1)
- **System-agnostic generic definitions** for generic labels; source-system examples may be cited as provenance but must not narrow the definition. (§11.2.1 + §11.2.2)
- **Resolver-stamped vs source-attested** boundary: resolver-stamped concepts (fiscal period, derived amounts) are NOT BCF — they live at canonical resolution. (§11.6)
- **Per-item parks don't halt a batch** (continue-to-exhaustion). (Backbone batch doctrine §3.4)

## 4. Where doctrine is silent or ambiguous

- **DEC-26b6e2 vs amend-definition endpoint (Q2/Q3).** This is the operative tension. The ADR's "never edited in place" stance has not been formally amended; the implementation has shipped a path that edits in place under the "editorial" cover. There is no successor ADR refining DEC-26b6e2.
- **What "editorial" means in practice.** DEC-26b6e2 distinguishes editorial (denotation unchanged) from meaning-bearing (denotation changed) but the implementation collapses both under `correction_class = editorial` on the amendment ledger. The boundary is judgment, not a structural test.
- **Backbone halt policy at the session level.** Doctrine §3.4 says continue-to-exhaustion; operator session-level rules have repeatedly said halt-on-park. The operator-stricter override is admissible but the doctrine default isn't called out in operator instructions, which can leave the autonomous agent in ambiguity.
- **Whether the panel should see sibling representation_term bindings** in the packet. The SOL × line number park's stated reason was "*The packet does not show sibling line-number bindings on the referenced line backbone to confirm alignment.*" If the packet builder (`registry-authoring-context.builder.ts:145`) did pass `existingConcepts` and `activeCharacteristics`, the Checker either didn't see them or didn't use them. This is a Tier-3 question (code/prompt inspection) the operator has held this packet from.

## 5. Whether Tier-3 code/prompt inspection is needed

**Yes — for two specific reasons:**

1. **Resolve the DEC-26b6e2 vs amend-definition tension.** Read the bc-core service code for `RegistryAuthoringService.amendCharacteristicDefinition` and the F1/F3 design docs (`business-concept-registry-f1-forward-design.md`, `business-concept-registry-f3-authoring-service-design.md`) to find whether there's a documented refinement of DEC-26b6e2 that hasn't surfaced as a follow-up ADR, OR whether PR #343 / TSK-4c6fbd was an implementation-side gap.

2. **Resolve the packet-visibility question on representation_term.** Read the panel packet builder + the Maker/Checker prompts (likely in `bc-ai/prompts/` or similar) to confirm whether sibling line-number bindings + governed representation_term set are actually shown to the Checker. If not, the SOL × line number park is a packet-visibility defect, not a substantive doctrine disagreement.

Phase 1 doctrine reading alone cannot resolve either. Phase 2 (Tier-3) is the next read.

## 6. Recommended next action

**Hold all BCF authoring + amendment work pending operator decision on the DEC-26b6e2 tension (Q2/Q3 above).** The decision is binary:

- **Option I — Ratify the amend-definition endpoint.** Author a successor ADR formally amending DEC-26b6e2 to read "*term frozen; definition editorially amendable in place for non-denotation-changing corrections; supersession required for any denotation change*". Define the test for "non-denotation-changing" (one possibility: any change that does not alter the set of valid bindings is editorial; any change that admits a previously-invalid binding is denotation-changing → supersession). Under this option, the net/gross amount amendments earlier this turn need re-classification: they admitted previously-invalid bindings (PO × net amount predated and was structurally a leak; SO × net amount became newly valid) → arguably denotation-changing → should have been supersessions despite using the amend-definition path. Remediation: supersede `net amount` and `gross amount` with successor characteristics carrying the document-general definitions; existing BCs continue to bind predecessors; the parked panels and the fresh SO × net amount BC need rebinding.

- **Option II — Reaffirm DEC-26b6e2's strict reading.** Author a follow-up ADR pinning that **all** characteristic definition corrections — editorial or meaning-bearing — go through `supersedeCharacteristic` minting a new `characteristic_id`. The amend-definition endpoint is deprecated or restricted to a much narrower band (e.g., typo / formatting only, with a structural test like Levenshtein distance ≤ N). The net/gross amount amendments are remediated by superseding the predecessor characteristics.

A third option exists but is not recommended: leave the doctrine vs implementation tension unresolved and continue work. That recreates the conditions for the next park to be doctrinally unresolvable.

Whichever option the operator picks, the SOL × line number park (`0a5d2e5c-…`) is independently resolvable per Q5/Q6 — confirm-the-parked with operator rationale on representation_term doctrine.

## 7. Operational state (carried forward unchanged)

- bc-core PID 29912 from `C:\MyProjects\bc-core-runtime` at `c63db8ed`, healthy.
- bc-ai PID 28444, port 4300, healthy.
- Dirty `C:\MyProjects\bc-core` worktree untouched.
- DDL 15 in place; MMS recovery closed; PCIC v2 active.
- Wave A's 4 SI header BCs active.
- Wave B fresh: 2 authored (SO × net amount `0b5613d0-…`, PO × exchange rate `ccf73fae-…`); 5 not attempted; SOL × line number parked at `0a5d2e5c-…`.
- net amount + gross amount editorially broadened earlier this turn (amendments `6d93beae-…` / `bf4880c0-…`) — pending Q2/Q3 disposition.
- This packet is untracked in `bc-docs-v3` working tree alongside prior held packets; commit batch still deferred.

Phase 1 read-only doctrine grounding complete. Holding for operator decision before any next action.
