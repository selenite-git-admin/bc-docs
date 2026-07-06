---
uid: business-concept-registry-vocabulary-evidence-framework
title: Business Concept Registry — Vocabulary Evidence Framework & Admission Checklist
description: The governed evidence-and-judgment framework for future F4-v2 governed-characteristic expansion. Defines the bounded evidence corpus and its source tiers, the evidence-packet shape, the v1 Vocabulary Admission Checklist (MUST / SHOULD / MAY), the checklist's panel and operator-confirm behaviour, the Global / Industry / System / Alias vocabulary-scope classification, the V8–V10 integration, and the checklist-version provenance. §11 amendment (2026-06-19) ratifies system-agnosticism, characteristic-hygiene, and the canonical-vs-source-diagnostic distinction; §11.6 (2026-06-19) ratifies the source-attested vs resolver-stamped substrate boundary distilled from the held BCF constitutional review on `fiscal period`.
status: accepted — amended 2026-06-19 (see §11 and §11.6)
date: 2026-05-22
amendment_2026-06-19:
  - Added §11 — System-agnosticism, characteristic hygiene, and canonical-vs-source-diagnostic substrate. Ratifies durable doctrine from operator-held BCF packets.
  - Added §11.6 — Source-attested vs resolver-stamped substrate boundary. Distilled from the held BCF constitutional review on `fiscal period` accepted under operator decisions D1–D8. Reserves `posting period code` as the future Layer-B name; forbids bare `fiscal period` as a BCF characteristic name. Governing chapter for fiscal time is the operating-model fiscal-time-and-temporal-gates chapter.
project: bc-docs
domain: contracts
subdomain: catalog
focus: governance
---

# Business Concept Registry — Vocabulary Evidence Framework & Admission Checklist

> **What this is.** The governed **evidence-and-judgment framework** for future
> **F4-v2** governed-characteristic expansion. It defines *how a proposed new
> characteristic is judged* — what evidence may be cited, what the panel and the
> operator must check, and how a candidate is scoped — **before any F4-v2
> implementation begins**. It is a **design note, not an ADR**; it elaborates
> DEC-02f5a9 (D414) and builds on the accepted F4-v2 governed-vocabulary-expansion
> note and the accepted C5 high-risk operator-confirm extension note. It is
> **not a seed list** and **not an implementation plan** — it selects no terms,
> changes no schema, builds no ingestion. Design-only: no code, no branch, no
> DB change, no live runs.

## Scope

Covers: the bounded evidence corpus and its source tiers; the evidence-packet
shape; the v1 Vocabulary Admission Checklist; the checklist's behaviour across
Maker / Checker / Moderator and operator-confirm; the vocabulary-scope
classification (Global / Industry / System / Alias); the V8–V10 integration;
and checklist-version provenance. Out of scope — see §9. This note is the
governing rubric that a later F4-v2 build slice and the
`Vocabulary Evidence Framework` corpus work must honour; it does not perform
either.

## 1. Purpose

F4-v2 makes the governed characteristic vocabulary **panel-grown** (the F4 v1
seed exemption is spent). Growth without a governing rubric degrades fast into
one of four failure modes:

- **model-memory vocabulary** — the panel invents a term from LLM training
  recall, with no citable source;
- **open-internet vocabulary** — a term justified by an unversioned web page,
  blog, or glossary that cannot be re-verified;
- **source-field-copy vocabulary** — a vendor field name or table column
  promoted verbatim into a governed business term;
- **fake-green vocabulary** — a term that passes because the rubric was vague,
  not because the term is sound.

This framework prevents all four. It defines a **bounded evidence corpus**
(§2), a **citation atom** (§3), a **governed Admission Checklist** (§4) that
the panel must answer with cited evidence and the operator confirms against,
and a **scope classification** (§6) that keeps F4-v2 v1 to Global vocabulary
only. It operationalises the F4-v2 note's §5 grammar (V7–V10) into a
panel-facing rubric.

## 2. Source tiers — the bounded evidence corpus

Evidence is **bounded**: a citation is admissible only if it names a source in
one of the tiers below. The corpus is curated, versioned, and closed — it is
not "whatever the model knows".

| Tier | Sources | What it CAN prove | What it CANNOT do |
|---|---|---|---|
| **T1 — Method / grammar authorities** | SBVR / Ronald Ross concept analysis; semantic-modelling governance guidance (e.g. Alexopoulos); data-model pattern sources (e.g. Silverston, Hay) | *How* a term is judged — formation discipline, concept-vs-representation separation, naming pattern | Author or name a term. T1 governs the panel's reasoning; it never supplies a characteristic. |
| **T2 — Cross-enterprise / cross-domain authorities** | ISO 11179; OAGIS; OASIS UBL; UN/CEFACT CCL; GS1 (where product / trade / logistics relevant) | Naming + formation citation evidence for a **cross-industry** business characteristic | Be treated as the authority — the Registry owns the final term; T2 is cited evidence. |
| **T3 — Domain authorities** | ISO 20022 / FIBO (finance, payments); XBRL US-GAAP / IFRS taxonomy (accounting, reporting); other domain corpora **only if bounded and versioned** | Naming + meaning citation evidence **within a named domain** | Justify a *Global* term on domain-only evidence — domain evidence supports an Industry-Specific classification (§6). |
| **T4 — Local / source evidence** | Local SAP S/4 metadata already present in the repo; `bc_seed` / source metadata; operator-provided source evidence | The *source meaning* a candidate carries, and coverage (the concept appears in onboarded data); must be bounded + snapshotted/versioned | Supply the canonical term, definition, or identity — T4 proves source meaning, not Registry naming. |
| **T5 — Coverage hints only** | Legacy BF / BO / CF artifacts; vendor field names; source table / field names | *Where to look* — a hint that a concept may be worth a governed term | Be naming, definition, or identity authority. Frequency in T5 is replication, not correctness. |
| **OUT — Explicitly inadmissible** | Open-internet search; LLM / model memory; random glossaries or blogs; unversioned vendor web pages | Nothing | Be cited at all. A candidate resting on an OUT source fails the checklist. |

The authority hierarchy carries forward from the F4 v1 seed design unchanged:
**the BareCount Concept Registry is the authority**; T2/T3 are citation
evidence; T4 proves source meaning; T5 is a coverage hint only. T1 is the new
explicit tier — the *method* sources that govern judgement.

## 3. Evidence-packet shape

The **citation atom** — the minimum a piece of evidence must carry — is, in v1,
exactly the current `candidateEvidence` shape so no DTO change is forced:

- **`sourceLabel`** — the named source (and, for T2–T4, enough to locate it).
- **`citedText`** — the verbatim text the candidate relies on.

A **richer future shape** is documented here so a later DTO decision is
deliberate, not improvised. Candidate future fields:

- `sourceId` — a stable id into the curated corpus;
- `sourceType` — the tier (T1–T5);
- `sourceVersion` — the version of a versioned standard / taxonomy;
- `citationRef` — a precise locator (clause, element id, table.field);
- `domain` / `industryCode` — the domain / industry the evidence belongs to;
- `retrievedAt` — **for local T4 snapshots only** (a snapshot timestamp;
  never a "fetched from the web" timestamp).

v1 stays at `{ sourceLabel, citedText }`; adopting the richer shape is an open
question (§10) and would be F4-v2 / DTO work, not this note.

## 4. Vocabulary Admission Checklist v1

The checklist a `createCharacteristic` candidate is judged against. Each item
is tagged **[mechanical]** (deterministically enforceable — the F4-v2 §5.1
bc-core floor) or **[judgment]** (panel + operator-confirm). The checklist is
**versioned** — this is **`vocabulary-admission-checklist:v1`** (§8).

### MUST — all must pass for an APPROVE

| # | Requirement | Enforcement |
|---|---|---|
| **M1** | Bounded evidence is present — every citation names a T1–T4 source; no OUT source. | [judgment] |
| **M2** | The candidate evidence is cited mechanically — `evidence.source_citations` includes an entry deep-equal to `candidateEvidence`; the citation is substantive, not decorative. | [mechanical] deep-equal · [judgment] substantive |
| **M3** | The canonical term and definition are English (`en`) — V8. | [mechanical] ASCII floor · [judgment] English |
| **M4** | The mechanical grammar floor passes — F4-v2 §5.1 (word count ≤ 4, `term == normalizeName(term)`, character whitelist, numeric-token floor). | [mechanical] |
| **M5** | Not a normalized duplicate of a governed characteristic. | [mechanical] |
| **M6** | Not a bare representation term. | [mechanical] |
| **M7** | No source-syntax / special-character violation — V10. | [mechanical] |
| **M8** | The definition is non-empty and non-circular — it does not restate the term; it names genus and differentia. | [mechanical] non-empty · [judgment] non-circular |
| **M9** | The term is not merely copied from a source field / table / code — it is an authored business term, not a vendor identifier. | [judgment] |
| **M10** | This is an operator-initiated `createCharacteristic` run — the checklist is evaluated only for deliberate vocabulary authoring. A concept-authoring run may never branch into vocabulary creation (F4-v2 §3). | [structural] |

### SHOULD — expected; a miss requires explicit rationale

| # | Requirement |
|---|---|
| **S1** | The term is 1–3 words. |
| **S2** | The term is singular. |
| **S3** | No entity / object prefix unless it disambiguates an otherwise-meaningless bare head. |
| **S4** | An acronym is spelled out unless the acronym is the dominant business term. |
| **S5** | Numeric tokens are avoided unless the numeral is genuinely semantic. |
| **S6** | The term is useful beyond a single one-field accident — it names a reusable business property. |

### MAY — admitted exceptions, each requiring an explicit stated rationale

| # | Exception |
|---|---|
| **X1** | A 4-word term, with an explicit rationale. |
| **X2** | An irreducible plural (e.g. `payment terms`). |
| **X3** | A numeric business term where the numeral is the established concept (e.g. `1099 indicator`). |
| **X4** | A representation-term word as the genuine semantic *head* of the property (e.g. `due date`, `tax rate`). |
| **X5** | An entity-qualified term where the bare head would be meaningless (e.g. `document date`). |
| **X6** | An acronym retained — only when it is the dominant business term, not a source abbreviation. |

The MUST set is the F4-v2 §5.1 mechanical floor (M3–M8 mechanical parts)
**plus the hard semantic gates** (M1, M2, M9, M10, and the judgment parts of
M3/M8). SHOULD and MAY are the F4-v2 §5.2 judgment surface, made explicit and
answerable.

**M10 is not something the Maker "decides" — it is a system boundary.** The
checklist is evaluated **only** for an operator-initiated `createCharacteristic`
run; the F4-v2 §3 separation structurally bars a concept-authoring run from ever
branching into vocabulary creation. M10 records that boundary; it is not a
per-term judgement.

## 5. Checklist behaviour

- **Maker** answers every checklist item, each MUST/SHOULD answer backed by a
  cited (T1–T4) source; a SHOULD miss or a MAY exception carries an explicit
  stated rationale.
- **Checker** attacks the checklist — it actively tries to break each MUST and
  to expose a weak or decorative citation, an unstated exception, or a
  source-field copy.
- **Moderator** may return `APPROVE` **only if every MUST passes**. Any failed
  MUST → not APPROVE.
- **Operator-confirm** (the C5-HR high-risk gate) sees the *same* checklist and
  the same answers, and confirms or refuses on that basis.
- **Missing evidence, or source ambiguity** → `OPERATOR_REVIEW`, never
  `APPROVE`.
- **A semantic duplicate** (normalized-distinct but synonymous with a governed
  characteristic — the F4-v2 "No Synonym Admission" rule) → `REJECT` or
  `OPERATOR_REVIEW`, never `APPROVE`.
- A candidate **not classified `Global`** — `Industry-Specific`,
  `System-Specific`, or `Alias / Localization Candidate` — **cannot be
  `APPROVE`** for F4-v2 v1; it routes to `OPERATOR_REVIEW` or the defer /
  alias / mapping path (§6). Global classification is explicit and
  evidence-backed, never assumed.
- A SHOULD miss or MAY exception **without** an explicit rationale → treated as
  a fail, routed to `OPERATOR_REVIEW`.

## 6. Vocabulary scope classification

This section locks the design room so F4-v2 v1 cannot over-reach.

**One table.** There is, and will remain, **one `concept_registry.characteristic`
table**. No industry-specific or system-specific characteristic tables are
created. Vocabulary scope is a **future metadata attribute on characteristic
rows** — a flag, decided later (§10) — never a separate table.

**Every `createCharacteristic` candidate is classified into one of five
classes:**

| Class | Definition | F4-v2 v1 disposition |
|---|---|---|
| **Global** | A cross-industry, cross-system business characteristic. | **Admitted** — the only class F4-v2 v1 admits. |
| **Industry-Specific** | Valid within a named industry / domain, not safe as global vocabulary. | **Deferred** — not forced into Global; recorded for a later industry-scoped gate. |
| **System-Specific** | Tied to a named system / application / source context. | **Not Global** — routed to alias, mapping, source evidence, or review; never forced into Global. |
| **Alias / Localization Candidate** | A different wording or language for an *existing* characteristic. | **Not a new characteristic** — deferred to the alias / localization layer. |
| **Reject** | Fails the checklist, or is not a value-property characteristic at all. | **Rejected.** |

**Locks:**

- F4-v2 v1 admits **Global characteristics only**.
- **No global-by-accident.** A candidate classified `Industry-Specific` or
  `System-Specific` **cannot be `APPROVE`** for F4-v2 v1 Global admission — it
  routes to `OPERATOR_REVIEW`, defer, or the alias / mapping path. A Global
  `APPROVE` requires an explicit, evidence-backed Global classification; the
  classification is never assumed.
- Industry-Specific terms are **deferred in v1** — never widened into Global to
  force admission.
- System-Specific terms are **rejected / deferred / aliased / mapped** — never
  forced into Global.
- Legacy / source-specific terms (T5 coverage hints) should usually become
  **aliases or mappings**, not Global characteristics.
- Concept-authoring panels should *eventually* receive a `Global + selected
  industry` vocabulary slice, not all industries at once — how the industry
  context is selected is an open question (§10).

## 7. V8 / V9 / V10 integration

The F4-v2 grammar amendments fold into the checklist, not a parallel rulebook:

- **V8 — Canonical Language.** The canonical term and definition are English
  (`en`) — checklist **M3**. A non-English source term is T2–T4 evidence only;
  a localized label is an Alias / Localization Candidate (§6), not a new
  characteristic.
- **V9 — Numeric Tokens.** Digits are disfavoured, not banned. The mechanical
  trailing-digit-suffix reject is in **M4** (the §5.1 floor); the
  semantic-vs-artifact judgment is **S5**; an admitted numeric business term is
  **X3**.
- **V10 — Character Set.** The canonical term is lowercase ASCII letters and
  single spaces (digits only by the V9 exception) — checklist **M7**; the
  positive whitelist and the rejection of source-syntax / code shapes are the
  §5.1 floor.

## 8. Provenance

The checklist is **versioned**, and versioned-checklist provenance is a
**requirement** — not a best-effort. The version is emitted, not assumed
(Invariant VI). "Recorded somewhere if feasible" is explicitly **not**
acceptable.

- The **panel recommendation must carry `checklist_version`** — the version of
  the Vocabulary Admission Checklist the Maker / Checker / Moderator answered
  (v1 = **`vocabulary-admission-checklist:v1`**).
- The **C5-HR operator-confirm provenance must record the checklist version it
  confirmed** — either copied from the panel recommendation or validated
  against it — so a confirmed cert states *which rubric* the confirm was made
  against.
- Only the **exact field location** remains open (§10) — candidate homes are
  the recommendation `verdict_payload_json` and the C5-HR
  `gate_results_json.operator_confirm` block. The *requirement* is locked; only
  the field is open.
- **No invisible rubric changes.** A change to the checklist is a new version
  (v2, …); every panel run and every confirm is attributable to the checklist
  version in force when it happened.

## 9. Non-goals

This note deliberately does **not**:

- select or author any new characteristic;
- change any schema (the vocabulary-scope flag of §6 is design room, not a
  DDL change — it is a later DBCP);
- design the full operator / authoring UI;
- admit industry-specific vocabulary (deferred — §6);
- solve aliases or localization (their own later layer);
- build evidence-corpus ingestion or tooling;
- start F4-v2 implementation, any bc-ai work, the C5-HR-S3 endpoint, or the
  C5-HR hardening DBCP (TSK-1ba76a).

## 10. Open questions

Captured, not silently resolved:

1. **Checklist-version field location.** Versioned-checklist provenance is a
   *requirement* (§8) — the panel recommendation carries `checklist_version`
   and the operator-confirm provenance records it. The open part is only the
   exact field — the recommendation `verdict_payload_json`, the C5-HR
   `gate_results_json.operator_confirm` block, both, or a dedicated field.
2. **Richer evidence packet.** Whether the §3 richer fields (`sourceType`,
   `sourceVersion`, `citationRef`, …) warrant a `candidateEvidence` DTO /
   schema change later, and when.
3. **Vocabulary-scope representation.** How the Global / Industry / System
   classification (§6) is eventually represented on `characteristic` rows — a
   flag, an enum, a join — and the DBCP that lands it.
4. **Source-corpus admission governance.** How the bounded evidence corpus
   itself is governed — how a source is admitted to a tier, versioned, and
   retired.
5. **Industry-context selection.** How an industry context is selected so a
   future concept-authoring panel receives `Global + selected industry`
   vocabulary rather than all industries.

## 11. System-agnosticism, characteristic hygiene, and substrate role (amendment 2026-06-19)

This section ratifies durable doctrine surfaced by recent BCF breadth work. It
amends — does not replace — §1–§10. Where it overlaps §6 (vocabulary scope
classification), it makes the underlying principle explicit; where it extends,
it adds new rules and a new substrate-role distinction.

### 11.1 System-agnosticism — source carriers are evidence, not scope

The platform vocabulary is **system-agnostic**. A characteristic's scope is
judged in **system-agnostic business terms** — never by which source table or
source field family its current bindings happen to reference.

- Source field names and source table identifiers — e.g. SAP `BLART`,
  `BSAD`/`BSAK`, `EKKO`, `BSART`; Oracle E-Business `DOC_CATEGORY_CODE`;
  NetSuite `tranType`; QuickBooks `DocumentType` — are **evidence of where a
  classifier is physically carried by a source system**. They are **not**
  semantic scope boundaries for platform characteristics.
- A different source field or source table family is **not, by itself**,
  justification for a scoped sibling characteristic.
- A scoped sibling characteristic is justified **only when the business
  meaning differs in system-agnostic terms** — e.g. a genuinely new
  cross-industry/cross-system business meaning that the existing
  characteristic's definition does not cover.

This is the operative form of §6's `System-Specific` reject/defer rule, applied
*inward* — to definition writing and supersession decisions — in addition to
*outward* admission classification.

### 11.2 Characteristic hygiene — generic labels require generic definitions

Three derived rules govern characteristic admission and any subsequent
definition revision:

1. **Generic characteristic labels require generic definitions.** A label like
   `document type code`, `closing balance`, `value date`, `effective date`,
   `reason`, or `status` is generic; its definition must be system-agnostic.
2. **Entity-specific or source-specific examples MAY be cited as provenance**
   inside a generic definition — but they **MUST NOT narrow the definition**
   unless the characteristic label itself is scoped (e.g. a hypothetical
   `bank statement closing balance` would legitimately scope `closing balance`
   to one source-authority surface; `closing balance` alone may not).
3. **No silent characteristic broadening.** If a candidate Business Concept
   depends on broadening the definition of an existing characteristic, the
   panel run must be **parked** for operator decision rather than silently
   broadened. Either the operator authorises broadening (removing provenance
   leakage) via the governed characteristic-supersession path, or the operator
   decides a scoped sibling is genuinely needed because the system-agnostic
   business meaning differs.

These rules apply prospectively at admission (Maker / Checker / Moderator) and
retrospectively when the platform encounters a parked candidate whose objection
is rooted in a leaked source-specific definition.

### 11.3 Canonical metric substrate vs source-diagnostic substrate

The registry's content carries two distinct roles. The distinction is not a new
schema — it is a substrate-role classification used in breadth planning and in
parked-BC triage.

| Role | What it carries | Backbone implication |
|---|---|---|
| **Canonical metric substrate** | Characteristics and BCs that support metric evaluation, joins, filters, comparisons, and analytical explanations. Load-bearing for at least one metric / reconciliation / audit / source-mapping workflow. | **Required** for a backbone to count as complete-enough. |
| **Source-diagnostic substrate** | Characteristics and BCs that preserve source-system classification and debug context. Useful for tracing observations back to source records, but not directly consumed by any metric, join, filter, or comparison the platform exposes. | **Optional**. May remain deferred or parked until a concrete metric / reconciliation / audit / source-mapping workflow concretely requires it. |

**Implication for parked verdicts.** A parked BC whose only function is
source-diagnostic does NOT block backbone completion. The parked verdict is
recorded as an *intentional deferral with documented system-agnostic
rationale*, not as an open coverage gap. Revisitation is triggered by concrete
workflow demand, not by elapsed time.

### 11.4 Worked example — `document type code` (operator decision 2026-06-19)

Operator reclassified `document type code` as **optional source-diagnostic
substrate** on 2026-06-19. The Purchase Order × document type code parked
verdict from the procurement backbone batch is therefore an intentional
deferral, not a backbone-completion blocker. Procurement backbone work is not
gated on resolving it.

When and if a concrete workflow demand surfaces, the documented starting point
is to broaden the existing characteristic's definition (remove source-specific
shorthand from the body; retain SAP/Oracle/NetSuite carriers as cited examples
of source carriers, not as scope qualifiers) via the governed
characteristic-supersession path. A scoped sibling such as
`procurement document type code` is **not** the recommended path: the business
meaning of "code classifying the type of business document" does not differ
between accounting and procurement; only the source enumeration differs, and
§11.1 forbids importing source-enumeration differences into platform
vocabulary structure.

### 11.5 Provenance

The doctrine in §11 was distilled from two held BCF packets (not authoritative
themselves; cited as the working notes whose durable conclusions are ratified
here):

- `barecount-devhub/.claude/bcf-substrate-inventory-and-backbone-audit-held-2026-06-19.md`
  — substrate audit (17 active entities, 53 characteristics, 123 active BCs)
  that identified the provenance-leakage class of risk and the
  canonical/diagnostic distinction.
- `barecount-devhub/.claude/bcf-characteristic-scope-hygiene-decision-held-2026-06-19.md`
  — characteristic scope hygiene decision packet (amended 2026-06-19) that
  applied the doctrine to six suspect characteristics and locked the
  `document type code` deferral.

Companion doctrine on backbone completion and batch execution lives in
`bcf-backbone-breadth-and-batch-doctrine.md`.

### 11.6 Source-attested vs resolver-stamped — the BCF boundary on enrichment outputs (amendment 2026-06-19)

The canonical-vs-source-diagnostic distinction in §11.2 generalises to a
**substrate-boundary rule**: BCF characteristics declare *source-attested* fields
— values that arrive at the Canonical Object via the source mapping path
(Reader, Admission Contract, Observation Contract, Canonical Contract field
selection from source). **Resolver-stamped enrichment outputs** — fields the
canonical resolver computes from canonical context (such as posting date plus
tenant calendar plus legal entity) — live at the Canonical Contract and
canonical-resolution boundary, **not at BCF**.

This rule applies whenever a candidate characteristic touches a concept the
platform already derives at canonical resolution. The fiscal-time chapter
governs the worked example: **canonical reporting period** (resolver-stamped) is
never BCF; **source-attested posting period code** is BCF-admissible only with
strict naming and definition discipline (see *Substrate Boundary — Canonical
Reporting Period vs Source-Attested Posting Period Code* in
`bc-docs-v3/docs/operating-model/fiscal-time-and-temporal-gates.md`). The bare
label `fiscal period` is forbidden as a BCF characteristic name because it
collides with the resolver-derived authority and invites cross-layer drift; the
reserved Layer-B name is `posting period code`.

The pattern is general. Any candidate characteristic that names a concept
BareCount derives at canonical resolution — period, fiscal year, derived
amounts under tenant-context arithmetic, normalised statuses produced by the
resolver — fails the BCF admission test as a category error. If the source
also stamps a distinct, source-attested instance of the same concept and a
metric demands it, the source-attested instance may be admitted as a
diagnostic / control characteristic under §11.2's canonical-vs-source-diagnostic
rule, with a label that explicitly carries the source-attestation marker so it
cannot be confused with the resolver-stamped concept.

The governing chapter for any resolver-derived concept is its own
operating-model chapter (fiscal time for period and fiscal year; future chapters
for other resolver-derived concepts as they are written). Definitions of
BCF characteristics on the source-attested side MUST defer to that chapter for
the canonical concept and MUST NOT describe the resolver's behaviour.

**Provenance.** The doctrine in §11.6 was distilled from the held BCF
constitutional review on `fiscal period`
(`barecount-devhub/.claude/bcf-fiscal-period-constitutional-review-held-2026-06-19.md`)
and accepted by operator decisions D1–D8 on 2026-06-19. The constitutional
review supersedes the earlier audit
(`barecount-devhub/.claude/bcf-fiscal-period-architectural-audit-held-2026-06-19.md`)
for authoritative purposes.

## Status

`accepted — amended 2026-06-19 (§11)` — operator review-back 2026-05-22
accepted the original note with three wording locks: **M10** reworded as a
system boundary (not a Maker decision); **versioned-checklist provenance made a
requirement** — the panel recommendation carries `checklist_version` and the
operator-confirm provenance records it, only the exact field location remains
open; and the explicit **no-global-by-accident** rule — an `Industry-Specific`
/ `System-Specific` classification cannot be `APPROVE` for F4-v2 v1.

The 2026-06-19 amendment (§11) ratifies system-agnosticism applied to
definition writing, characteristic hygiene (generic-label / generic-definition
pairing; no silent broadening), the canonical-vs-source-diagnostic substrate
distinction, and the `document type code` deferral as a worked example. It is
additive — it neither alters §1–§10 nor changes the checklist version.

It remains the governing rubric for future F4-v2 characteristic expansion;
F4-v2 implementation, evidence-corpus work, and any vocabulary selection remain
not started and out of scope.
