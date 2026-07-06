---
uid: business-concept-registry-f4-v2-vocabulary-expansion-design
title: Business Concept Registry — F4-v2 governed vocabulary expansion design note
description: Design note for F4-v2 — the cert-gated successor to the one-time F4 v1 governed-vocabulary seed. F4-v2 adds the B6 createCharacteristic operation so a new governed characteristic is authored through the real panel + C5 high-risk operator-confirm + F3 path. Locks the candidate evidence bar, the V7–V10 characteristic term grammar (doctrine plus the mechanical/judgment split), the strict separation from concept authoring, the draft lifecycle, and a slice plan. Depends on the C5 high-risk operator-confirm extension. Specification only — design-only, no code.
status: accepted
date: 2026-05-22
project: bc-docs
domain: contracts
subdomain: catalog
focus: governance
---

# Business Concept Registry — F4-v2 governed vocabulary expansion design note

> **What this is.** A design note for **F4-v2** — the cert-gated successor to
> the one-time F4 v1 governed-vocabulary seed. F4 v1 seeded the initial 24
> property-characteristics through the single F3 certification *exemption*
> (`seedGovernedVocabulary`), because the panel was not yet in service. The B6
> Track 2 live proof (T2-S4) put the panel in service. F4-v2 is how the
> vocabulary **grows from now on**: a new governed characteristic is authored
> through the real B6 panel → C5 → F3 path, with no exemption. It is a **design
> note, not an ADR** — it elaborates DEC-02f5a9 (D414) and builds on the
> accepted F1/F2/F3/F4 notes. It **depends on** the C5 high-risk operator-confirm
> extension note: `registerCharacteristic` is the first high-risk Registry
> operation and cannot be issued until that fork exists. Design-only: no code,
> no branch, no DDL.

## Scope

F4-v2 covers the B6 `createCharacteristic` operation, the candidate evidence
bar, the V7 characteristic term grammar, the strict separation from concept
authoring, the draft lifecycle, and the recommendation-validator and
orchestrator changes that consume the C5 high-risk fork. It does **not** cover
the C5 operator-confirm fork itself (its own note), F3 (ready — see §2),
representation-term expansion (deferred — §8 V3), or activation (B10). F4-v2
v1 is **characteristics only**.

## 1. What F4-v2 is — the exemption is spent

F4 v1 ran **once**, in the greenfield window, through `seedGovernedVocabulary`
— the single named exemption from F3's certification requirement. The F4 v1
note is explicit: that exemption exists *only because the panel was not yet in
service*, F4 v1 "seeds the floor, not the ceiling", and "the panel grows it
thereafter (governed-open)". The panel is now in service. The exemption is
**spent**: F4-v2 introduces no new exemption and no second write path. Every
new characteristic travels the full panel → C5 → F3 path, exactly like an
entity or a concept (V6).

## 2. The `createCharacteristic` operation

F4-v2 adds a third B6 operation, discriminated the same way the A1 extension
added `createEntity` — but the certification/F3 layer name is the **existing**
governed name, not a new one:

| Layer | Name |
|---|---|
| B6 candidate / packet operation discriminator | `createCharacteristic` |
| Recommendation `f3_operation` | `registerCharacteristic` |
| `action_code` | `registry_author_vocabulary` |
| `subject_kind` | `characteristic` |
| F3 method | `RegistryAuthoringService.registerCharacteristic` — **already exists** |

**F3 needs no new method.** `RegistryAuthoringService.registerCharacteristic(
{ term, definition }, auth)` exists today — cert-gated, runs
`NameConflictChecker.assertCharacteristicTermAvailable`, stamps
`target_registry_id`. `REGISTRY_OP.registerCharacteristic` is already mapped to
`{ registry_author_vocabulary, characteristic }`. F4-v2 reaches an F3 surface
that is already built; the work is in B6 and C5.

`registry_author_vocabulary` is **high-risk** by `classifyRegistryRiskTier`
(only `registry_create` / `registry_add_version` are low-risk). So
`createCharacteristic` always routes through the C5 high-risk operator-confirm
fork — the panel proposes, an operator confirms, then F3 writes.

## 3. The boundary — strict separation from concept authoring

The governing requirement: **expand the vocabulary without weakening "No
Vocabulary Stretching", and without letting the panel invent terms during
concept authoring.** Three structural locks make that true, not aspirational:

1. **The concept panel never branches into vocabulary creation.**
   `createBusinessConcept` is unchanged. A weak or missing characteristic fit
   still yields `OPERATOR_REVIEW` — full stop. No code path leads from concept
   authoring to characteristic authoring; the concept panel cannot emit "…and
   here is a new term I made up".
2. **`createCharacteristic` is operator-initiated only.** The panel never
   self-initiates one. A human reads the `OPERATOR_REVIEW`, and *if* they judge
   a genuine vocabulary gap, *they* submit a `createCharacteristic` candidate.
   Two human-gated steps, two separate panel runs, two separate certs. The
   operator-review queue is the only bridge between the two operations.
3. **A mirror anti-abuse rule for the new operation — No Synonym Admission.**
   "No Vocabulary Stretching" stays verbatim for concept authoring.
   `createCharacteristic` carries its own rule: a proposed term that is a
   synonym or near-duplicate of a governed characteristic → `REJECT` /
   `OPERATOR_REVIEW`, never `APPROVE`. The structural check
   (`assertCharacteristicTermAvailable`) blocks only *normalized* duplicates;
   the panel adds the *semantic* judgment — two terms can be normalized-distinct
   yet synonymous.

## 4. Candidate evidence bar

A `createCharacteristic` candidate carries a `candidateEvidence`
`{ sourceLabel, citedText }` — the same structured evidence rule as the entity
and concept candidates. On `APPROVE`, the recommendation's
`evidence.source_citations` must include an entry deep-equal to
`candidateEvidence`. A term proposed with no substantive business-meaning
evidence — for example, justified only by "it is the SAP source field name" —
fails this bar. Prose-only justification never carries an `APPROVE`.

## 5. The characteristic term grammar (V7–V10)

V7 is sound as a curation **doctrine** but must not be cast as a single
mechanical validator spec — of its clauses, only about five are mechanically
enforceable. Measured against the 24 live characteristics, a literal mechanical
reading would reject roughly half of the *already-approved* vocabulary
(eleven of 24 terms carry a representation-term word as their semantic head:
five `… date`, three `… rate`, three `quantity …`). F4-v2 therefore splits the
grammar into a **mechanical floor** and a **judgment surface**. The 2026-05-22
amendment adds V8 (canonical language), V9 (numeric tokens), and V10 (character
set) into that same two-layer split; all three are satisfied by every one of
the 24 live characteristics (all English, all-ASCII-lowercase, zero digits).

### 5.1 Mechanical floor — bc-core validator / F3

Deterministic, cheap, no semantics:

- **character set (V10)** — the canonical `term` is **lowercase ASCII letters
  and single spaces only**; digits are admitted only under V9. A positive
  whitelist: every other character is rejected — punctuation and separators
  (`/`, `\`, `|`, `&`, `+`, `,`, `.`, `:`, `;`, `_`, `-`, parentheses,
  brackets, quotes, apostrophes), diacritics, and any non-ASCII character. This
  whitelist subsumes the former standalone `/` and `&` rejects;
- `term == normalizeName(term)` — trim → collapse `[\s_-]+` → lowercase; the
  stored term already is its normalized form. With the whitelist this rejects
  mixed-case and underscored / hyphenated source-field and code shapes
  (`salesOrderLinePrice`, `unit_price`, `SCREAMING_SNAKE`, `VBAP-NETPR`,
  `sales_order.unit_price`) before any judgment runs;
- **numeric tokens (V9)** — digits are not banned, but a term whose final
  space-separated token is a bare one- or two-digit numeral (` 1`, ` 2`, ` 01`,
  ` 02`) is rejected as a source-disambiguation artifact (`amount 1`,
  `price 2`). A slash / range bundle (`30/60/90 status`) is already rejected by
  the character whitelist. Every other numeral-bearing term routes to
  panel/operator judgment (§5.2) — it is never mechanically admitted;
- word count ≤ 4 (hard ceiling);
- reject the word-compound ` and ` — an alphabetic compound the character
  whitelist cannot catch;
- reject a term equal to a bare representation term;
- normalized-uniqueness — already enforced by `NameConflictChecker`.

### 5.2 Judgment surface — AI panel, then operator-confirm

Not mechanical; the panel holds the governed characteristics, entities, and
representation terms in its context packet and is the only place that can judge
fit; the operator-confirm gate (§7) is the final per-term accept:

- noun phrase, not a sentence; 1–3 words preferred, 4 only with a stated
  rationale;
- representation-term word as the genuine semantic *head* of the property
  (`due date`, `tax rate`) is admitted; merely appending the OAGIS
  representation suffix (`Amount`, `Measure`, `Code`, `Identifier`, `DateTime`)
  is leakage and is stripped;
- singular by default; a genuine irreducible plural (`payment terms`) is
  admitted on judgment;
- no entity/object prefix unless it disambiguates a meaningless bare head
  (`document date` vs bare `date`);
- one characteristic = one semantic property (semantic, beyond the literal
  compound guard);
- prefer the spelled-out business term; an acronym only when it *is* the
  dominant business term, not the source-field abbreviation;
- a non-circular genus-differentia definition that does not restate the term;
- **numeral (V9)** — admit a numeral only when it is part of an established
  business term or standard concept (`1099 indicator`, `w2 withholding`,
  `3pl status`), never a source-field artifact; an admitted numeric term
  carries an explicit stated rationale;
- **special character (V10)** — where a genuine business term truly carries a
  special character, the operator decides: rewrite it as a plain noun phrase,
  defer it, or leave the typography to a later alias / localization layer. A
  canonical term never preserves source-system or standards typography — cite
  source field `NETPR` as evidence, canonicalize to `unit price`;
- **language (V8)** — the canonical term and definition are English; a
  non-English source term is evidence only, never the canonical term;
- No Synonym Admission — semantic, beyond normalized-equality (§3.3).

### 5.3 Doctrine — docs / panel prompt

The F4 v1 authority hierarchy carries forward unchanged: the BareCount Concept
Registry is the authority; external standards and the `bc_seed` OAGIS catalog
are citation evidence; legacy BF/BO/CF are coverage hints only. The vocabulary
is governed-*open* and deliberately grown one substantive term at a time, not
bulk-imported. v1 canonical terms and definitions are authored in English
(`en`) (V8); a non-English source term may be cited as evidence, and a
localized label or synonym is out of F4-v2 — it belongs to a later alias /
localization layer, never a separate characteristic. These instruct the panel
prompt and the operator; they are not mechanically enforced.

> **Accepted.** §5 records V7 as revised by this note's review and accepted at
> the 2026-05-22 operator review-back: the V7 clauses moved to judgment
> (rep-term head, singular, entity prefix) and the three added rules (definition
> grammar, `term == normalizeName`, acronym policy) are locked.

> **Amendment 2026-05-22.** §5 was amended to add **V8** (canonical language —
> English), **V9** (numeric tokens), and **V10** (character set). V9 and V10
> extend the §5.1 mechanical floor; V8 is doctrine plus a judgment-surface
> rule. The amendment reconciled §5.1 into a single positive character
> whitelist that subsumes the former standalone `/` and `&` rejects. No V1–V7
> decision changed; all 24 live characteristics already satisfy V8–V10.

## 6. Lifecycle — a new characteristic is born `draft`

`registerCharacteristic` passes no `lifecycleState`, so a panel-authored
characteristic takes the `characteristic.lifecycle_state` default — `draft`.
(Contrast `seedGovernedVocabulary`, which hardcodes `active` — seed-only, and
spent.) The schema FK would *allow* a concept to bind a `draft` characteristic,
but B6 concept authoring exposes **only `active` governed characteristics**
through the F5 read surface. Therefore a newly authored characteristic is **not
bindable by normal concept authoring until B10 activates it**. F4-v2 authors
the term; B10 owns publication/activation — the same draft-then-activate
discipline B6 already applies to entities and concepts.

## 7. The B6 changes — validator and orchestrator

**Recommendation validator.** `recommendation.validator.ts` currently bakes in
the low-risk assumption: it rejects `operator_confirm_required !== false` ("no
high-risk tier"), and `validateProposedOperation` asserts `action_code ===
'registry_create'` *before* discriminating, knowing only `createEntity` /
`createBusinessConcept`. F4-v2:

- moves the `action_code` check **into each branch** — `registry_create` for
  the two existing ops, `registry_author_vocabulary` for `registerCharacteristic`;
- adds a `registerCharacteristic` branch validating the `{ term, definition }`
  `f3_input` against the §5.1 mechanical floor;
- permits `operator_confirm_required: true` for the vocabulary operation (and
  only it) — the high-risk discriminator.

**Orchestrator.** `RegistryAuthoringOrchestrator.runS1` is today a single
synchronous pass: panel → C5 `issued` → F3 `authored`. A high-risk operation
makes it **two-phase**: panel → C5 returns `operator_confirm_required` → the
run stops, no Registry write; a second entry point, entered after the operator
confirms through the C5 seam, resumes → C5 issues → F3 `registerCharacteristic`
→ `authored`. The first-phase outcome gains a new `kind` —
`awaiting_operator_confirm` — alongside the existing `authored` / `parked` /
`not_issued` / `panel_not_found`.

## 8. Decisions to lock

| # | Decision | Proposed lock |
|---|---|---|
| **V1** | New B6 operation | B6 `createCharacteristic` → `f3_operation: registerCharacteristic`, `registry_author_vocabulary` / `characteristic`. F3 method already exists; no new F3 method. |
| **V2** | Risk tier | High-risk. Routes through the C5 high-risk operator-confirm fork. F4-v2 **depends on** the C5 high-risk extension note. |
| **V3** | Representation terms | Out of scope. F4-v2 v1 is characteristics only; representation-term expansion stays deferred (closed F2-seeded set). |
| **V4** | Lifecycle | Born `draft`. Not bindable by concept authoring until B10 activates; F5 exposes only `active` characteristics to the concept panel. |
| **V5** | Candidate evidence | Required structured `candidateEvidence`; `APPROVE` cites it deep-equal; no prose-only proof. |
| **V6** | F4 seed exemption | Spent / dormant. No F4-v2 seed exemption, no second write path; `seedGovernedVocabulary` retained only as historical bootstrap machinery. |
| **V7** | Term grammar | Locked as doctrine; split into the §5.1 mechanical floor and the §5.2 judgment surface; three rules added (definition grammar, `term == normalizeName`, acronym policy). Accepted at the 2026-05-22 review-back. |
| **V8** | Canonical language | English (`en`) for the v1 canonical term and definition. A non-English source term is evidence only; localized labels / synonyms are deferred to a later alias / localization layer, never separate characteristics. Amendment 2026-05-22. |
| **V9** | Numeric tokens | Digits disfavoured, not banned. Mechanical floor rejects a trailing bare one- or two-digit source-disambiguation suffix; every other numeral-bearing term routes to panel/operator judgment and needs an explicit rationale to be admitted. Amendment 2026-05-22. |
| **V10** | Character set | The canonical `term` is lowercase ASCII letters + single spaces (digits only under V9); all punctuation, separators, diacritics, apostrophes, and mixed-case / underscored / hyphenated source-field shapes are rejected by a positive whitelist. Amendment 2026-05-22. |

## 9. Slice plan

F4-v2 is T-shirt **M**, sequenced **after** the C5 high-risk extension. Each
slice its own gate. **The bc-core contract leads the bc-ai prompts** — the
prompts are written against a locked contract, never ahead of it.

- **F4-v2-S1 — this design note.** Gate: operator review-back accepts V1…V7
  and the §5 grammar split.
- **F4-v2-S2 — the bc-core path (one bc-core PR).** The candidate DTO + the
  §5.1 mechanical floor; the recommendation-validator extension (§7); the
  orchestrator two-phase change consuming the C5 `operator_confirm_required`
  outcome. This slice **locks the `createCharacteristic` contract** — the
  candidate shape, the recommendation shape, and the `f3_input` shape. Gate: PR
  review (tsc, eslint, vitest).
- **F4-v2-S3 — the bc-ai panel (one bc-ai PR).** Extend the `registry-authoring`
  flow to the `createCharacteristic` operation: the candidate shape, the
  context packet (governed characteristics + entities + representation terms for
  the No Synonym Admission judgment), and the three prompts encoding the §5.2
  judgment surface + No Synonym Admission. **Proceeds only after F4-v2-S2 has
  locked the contract** — the prompts are written against the locked shapes,
  not ahead of them. Gate: PR review (ruff, mypy, tests).
- **F4-v2-S4 — live proof. ✓ Complete 2026-05-22 — see §11.** One real
  `createCharacteristic` run end-to-end: candidate → panel → C5 confirm-required
  → operator confirm → C5 issue → F3 `registerCharacteristic` → a `draft`
  characteristic with a complete provenance chain. Gate: the operator opens the
  run gate.

## 10. Boundaries / non-scope

- **No C5 fork design here** — the C5 high-risk operator-confirm extension is
  its own note; F4-v2 consumes its contract.
- **No concept-authoring change** — `createBusinessConcept` is byte-identical;
  the only bridge from concept authoring to vocabulary expansion is the
  operator reading an `OPERATOR_REVIEW` (§3).
- **No representation-term expansion** (V3). **No alias work** (F4 v1 D6 still
  holds). **No bulk authoring** — the vocabulary grows one substantive,
  operator-confirmed term at a time.
- **No activation** — B10 owns `draft → active` (V4).
- **No DDL** — F3 and the `characteristic` table are built; the C5 note owns
  the operator-confirm provenance question.

## 11. F4-v2-S4 — live high-risk proof result (2026-05-22)

F4-v2-S4 ran on 2026-05-22 — the first live high-risk governed-vocabulary
authoring, end-to-end. All four F4-v2 slices and the C5 high-risk
operator-confirm extension are now built, merged, and live-proven.

**Candidate.** `createCharacteristic` · `proposedName: lead time` ·
`definition: "The elapsed time between initiating a business activity and the
expected completion or receipt of its result."` · `candidateEvidence`:
`SAP S/4HANA — MARC (plant-material master)` / `MARC-PLIFZ "Planned delivery
time in days" — the number of calendar days needed to obtain the material if it
is procured externally.` `lead time` was chosen as a low-ambiguity first
candidate — a genuine gap in the 24-term vocabulary, no synonym overlap (no
duration characteristic existed), and unambiguously global (the SAP field is
evidence, not a scope tie).

**Step 1 — `POST /api/bcf/registry-authoring-runs`.** The live Maker / Checker /
Moderator panel (Gemini 2.5 Flash · GPT-5.5 · Claude Opus 4.5) returned
`awaiting_operator_confirm` — `panelRunUid 00e7517a-0e4c-419b-9372-b73544545ab0`.
The emitted `panel_output_record`: `verdict_code APPROVE_FOR_DRAFT`,
`classification global`, `checklist_version vocabulary-admission-checklist:v1`,
all ten checklist answers M1–M10 `pass`, `grounding_check_result pass`,
`quarantined false`, no downgrade. C5 returned `operator_confirm_required` —
**no cert and no characteristic row were written**, confirming the high-risk
fork holds.

**Step 2 — `POST /api/bcf/registry-shape-certifications/confirm`.** On operator
confirm the path completed: `kind authored` / `authoredSubject characteristic`.

| Result | Value |
|---|---|
| `certificationRecordId` | `404ac530-5e33-44f7-9dc3-9d810cb3d4d3` |
| `characteristicId` | `407a6582-08a9-4c7a-ace1-1faa215d770a` |
| characteristic row | `term lead time`, `lifecycle_state draft`, `created_by bcf-registry-authoring-panel` |
| active vocabulary | 24 → 25 |
| cert `target_registry_id` | `= characteristicId` (stamped by F3) |
| `gate_results_json.deemed_approval.disposition` | `operator_confirmed` |
| `gate_results_json.operator_confirm.basis` | `registry_high_risk_action_code` (`rule_uid null` — v1) |
| operator rationale | stored verbatim in `gate_results_json.operator_confirm.rationale_text` |
| duplicate cert / second panel run | none — one cert, one panel record |

The proof confirms F4-v2's core claim (§1) is live-true: the panel emits a
checklist-backed `global` APPROVE; C5 withholds the cert pending confirm; the
operator confirm issues the cert with `operator_confirmed` /
`registry_high_risk_action_code` provenance; F3 writes the `draft`
characteristic; the cert's `target_registry_id` links it. No exemption, no
second write path.

One run-service defect was found and fixed mid-proof: `RegistryAuthoringRunService.
toCandidate` had not been extended for `createCharacteristic` in F4-v2-S2 (it was
still two-operation, so a characteristic request was wrongly rejected as a
`createBusinessConcept` missing `targetEntityId`). Fixed in a scoped one-PR
change with the previously-missing run-service test coverage, then the proof
resumed.

## 12. Resolved design question — characteristic versioning / publication lifecycle

F4-v2-S4 verification surfaced a structural asymmetry worth recording for a
later gate. `concept_registry` versions `entity` (`entity_version`) and
`business_concept` (`business_concept_version`), and carries a `*_supersession`
table for each. **It does not version characteristics** — `characteristic` is a
flat `(characteristic_id, term, definition, lifecycle_state, …)` row; there is
no `characteristic_version` and no `characteristic_supersession`. The
`RegistryAuthoringOutcome` `authored/characteristic` shape reflects this: it
carries `characteristicId` only, with no `characteristicVersionId` (unlike the
entity and concept outcomes).

This is **correct for F4-v2** — F4-v2 authors a term and stops; §6 and V4 defer
publication / activation to B10. Characteristic provenance is intact without a
version row: the audit chain is

> `panel_output_record` → `certification_record` (`panel_run_uid` +
> `target_registry_id`) → `concept_registry.characteristic`

— the `certification_record` is the join carrying both the panel run and the
authored characteristic id.

**Resolved (2026-05-22) — ADR DEC-26b6e2 (D415), *Immutable Characteristic
Atoms*.** The question — "should a characteristic be versioned and supersedable
like an entity / business concept, or does the flat model remain correct because
a characteristic is a vocabulary atom rather than a structured object?" — is
resolved **in favour of the atom**. A Characteristic **remains a flat semantic
atom**: there is **no `characteristic_version`**, and an active characteristic's
`definition` is **not versioned and not edited in place**. Once published
(`draft → active`) a characteristic's `(term, definition)` is its immutable,
authoritative meaning. A correction is made by **supersession / deprecation** —
a new Characteristic carrying the corrected `(term, definition)`, with
predecessor → successor lineage in a `concept_registry.characteristic_supersession`
record (the supersession carrying a `correction_class` of `editorial` or
`meaning_bearing`) — **not** by versioning.

The reasoning: a Characteristic has no structural identity (unlike an Entity or
a BusinessConcept), so its `definition` is meaning-bearing, not mere prose;
versioning would permit silent meaning drift under a stable `characteristic_id`.
The flat-model observation recorded above therefore stands as the **permanent
design** — the `RegistryAuthoringOutcome` `authored/characteristic` shape
correctly carries `characteristicId` only, with no `characteristicVersionId`.
See ADR DEC-26b6e2 and B10 implementation design §D5 (amended 2026-05-22). The
B10 originally-accepted recommendation to add `characteristic_version` was
reversed on review; characteristic publication is delivered by B10b on the
immutable-atom model.

## Status

`accepted` — operator review-back 2026-05-22 accepted V1…V7 including the §5 V7
mechanical/judgment split, and the §9 slice order in which the bc-core contract
(F4-v2-S2) leads the bc-ai prompts (F4-v2-S3). Depends on the C5 high-risk
operator-confirm extension note. **All four slices F4-v2-S1…S4 are shipped and
live-proven (2026-05-22) — see §11.** The recommended next gate is **B10
(Registry Publication / Lifecycle Design)** — see §12.

> **Amendment — 2026-05-22.** §12's deferred open question (characteristic
> versioning vs flat atom) is **resolved** — see §12 — by ADR DEC-26b6e2 (D415),
> *Immutable Characteristic Atoms*: a Characteristic remains a flat semantic
> atom; no `characteristic_version`; corrections after publication use
> supersession, not versioning. The note stays `status: accepted` (erratum to
> an accepted design).
