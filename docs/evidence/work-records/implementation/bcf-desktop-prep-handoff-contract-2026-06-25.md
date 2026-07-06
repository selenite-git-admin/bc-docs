---
title: BCF Desktop Semantic Packet-Prep Handoff Contract (2026-06-25)
description: Held contract that establishes the post-C1 architecture for BCF × OAGIS broad foundation buildout. Defines the role split between A0 deterministic compile (candidate skeletons), Claude Code Desktop (semantic packet preparation), transport script (schema + hash validation + API transport), bc-core/bc-ai F4-v2 (governed panel review), and C5 / single writer (governed write). Closes the old C1 v1/v2 attempt as diagnostic-only audit history. Specifies the clean C1 restart procedure, the Desktop input bundle, the Desktop output JSON schema, the transport script boundary (may / must not), the governance boundary, and the next safe action.
status: held
authority: dec-f94895 + operator architecture revision 2026-06-24
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-desktop-prep-handoff-contract
related_docs:
  - bcf-oagis-broad-buildout-blueprint-2026-06-23.md
  - bcf-oagis-compile-report-2026-06-24.md
  - bcf-oagis-retry-ledger-2026-06-24.md
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
  - bcf-oagis-pass-1-c1-closeout-2026-06-24.md
  - bcf-oagis-pass-1-c1-packet-builder-v2-design-2026-06-24.md
  - bcf-oagis-pass-1-c1-v2-closeout-2026-06-24.md
related_adrs:
  - DEC-f94895
related_sessions:
  - SES-dfac49
---

# BCF Desktop Semantic Packet-Prep Handoff Contract (2026-06-25)

> **Held design.** Defines the BCF × OAGIS broad-buildout architecture from the v2 closeout boundary forward. No runtime action authorized by this contract on its own. The next safe action after this contract is to generate a Desktop input bundle for a clean C1 restart; transport waits on operator approval after Desktop returns the packet set.

## 1. Core architecture

The broad-foundation-buildout program now operates as a five-stage pipeline. Each stage has a strict role; no stage carries the authority of another.

```
┌──────────────────────────────┐
│ A0 deterministic compile     │ — produces candidate skeletons (provenance, OAGIS evidence,
│ (script + retry ledger)      │   used_by_bc, shape tuple). No semantic interpretation.
└──────────────┬───────────────┘
               │ candidate skeletons + context bundle
               ▼
┌──────────────────────────────┐
│ Claude Code Desktop          │ — performs semantic packet preparation. Contextual
│ (offline, semantic prep)     │   interpretation. Reads substrate, panel-feedback corpus,
│                              │   standards reference, sibling patterns. Emits per-row
│                              │   packets with disposition, definition, evidence, hash.
└──────────────┬───────────────┘
               │ Desktop-output packet set (JSON files, hash-signed)
               ▼
┌──────────────────────────────┐
│ Transport script             │ — validates JSON schema, recomputes packet_hash, checks
│ (no semantic authority)      │   source_status consistency, posts to F4-v2 / C5 per
│                              │   disposition, records outcomes. Never rewrites packets.
└──────────────┬───────────────┘
               │ POST /api/bcf/registry-authoring-runs
               │ POST /api/bcf/registry-shape-certifications/confirm
               ▼
┌──────────────────────────────┐
│ bc-core / bc-ai F4-v2 panel  │ — governed maker / checker / judge review against
│                              │   Vocabulary Admission Checklist (M1–M10). Stamps
│                              │   panel_output_record. Returns verdict.
└──────────────┬───────────────┘
               │ verdict
               ▼
┌──────────────────────────────┐
│ C5 / single writer           │ — operator-confirm path for governed-vocabulary
│                              │   expansion. Mints certification_record. F3
│                              │   registerCharacteristic creates the substrate row.
│                              │   Single-writer concurrency.
└──────────────────────────────┘
```

### Important authority statements (non-negotiable in this contract)

- **Desktop prepares semantic proposals.** Desktop is not registry authority.
- **Scripts are not semantic authority.** They validate, hash, transport, ledger; they do not interpret.
- **bc-core / bc-ai F4-v2 panel is the only governed semantic-review surface.**
- **C5 / single writer is the only substrate write path.**
- **All writes go through the single writer.** No parallel-writer, no direct-DB substrate change.
- **Desktop output does not create substrate.** Substrate is created only by F4-v2 outcome → cert → F3 — never by Desktop, never by a transport script.

## 2. Why this contract exists

Pass 1 C1 produced the empirical evidence that motivates this contract.

- **A0 / A0.5 demonstrated they can identify candidate skeletons.** The OAGIS extract was parsed, the 595 raw C1 occurrences were deduped to 40 distinct bf_names, the substrate was correctly excluded, and the per-row provenance (noun.component.field) + shape tuple was clean. Skeleton production was fully deterministic and correct.
- **The v1 (script-built) packet builder produced 89% non-APPROVE.** 28 panel calls returned 25 OPERATOR_REVIEW + 1 REJECT + 2 APPROVE_FOR_DRAFT. Substantive panel feedback consistently flagged M2 (thin / boilerplate evidence), M8 (circular definition), M9 (source-field copy), and non-Global classification. Root cause: the script used a template definition (`"A coded value identifying the X of the associated entity. Code-typed dimension sourced from the OAGIS 10.12 vocabulary."`), a transliterated proposedName (`bf.replace(/_/g,' ')`), an unfiltered citedText (sometimes XSD primitive boilerplate), and no Global rationale — all by construction, not by row.
- **The v2 (refined script) packet builder improved discipline but did not solve the substantive problem.** v2 added pre-panel filtering, true packet_hash, per-row bucket assignment, and substantive citedText for 3 rows. Results: 1 APPROVE_FOR_DRAFT (`payment_method_code`), 2 OPERATOR_REVIEW (`gender_code`, `marital_status_code`). The 2 v2 parks were diagnosed: the F4-v2 DTO carries only `(sourceLabel, citedText)`, so a Global anchor (ISO/IEC 5218, UN/CEFACT TDED) placed in the v2 `definition` did not reach the panel's M2 check, which only inspects citedText. Even at the v2 level, deciding *whether the OAGIS gloss substantively establishes Global meaning* is a contextual semantic judgment a script cannot make from regex / heuristics alone.
- **Therefore the old C1 attempt is closed as diagnostic, not repaired row by row.** Re-targeting the 25 OPERATOR_REVIEW rows or the 2 v2 OPERATOR_REVIEW rows with yet-another-script (v2.1 / v3) would compound script-side semantic authorship, which the v1/v2 evidence now disqualifies. The right architectural move is to relocate semantic packet preparation to Claude Code Desktop, which can perform contextual interpretation at lower marginal cost under the Max plan and can read the substrate, panel-feedback corpus, standards reference, and sibling-pattern examples *in context* per row, producing a per-row authored packet rather than a templated one.

## 3. Current C1 freeze record

State of Pass 1 C1 at the moment this contract is filed. These numbers are the freeze baseline for the clean restart.

| Surface | Value |
|---|---|
| C1 queue size (unique proposed characteristics) | **40** |
| v1 panels run | **28** |
| v2 panels run | **3** |
| Confirmations run (C5) | **3** |
| Active entities | **26** |
| Active characteristics | **62** |
| Active business concepts (kind=value) | **194** |
| Total non-archived characteristics (any lifecycle) | **66** |
| New draft characteristics in substrate (this batch) | **3** |
| C2 status | **not started** |
| BC bindings created for the 3 drafts | **0** |
| Pass 1 caps consumed | 31 / 270 panel calls; <$3 / $80 spend |
| Wall-time consumed | ~80 min total (services + 2 batches) |
| Fatal stops fired | 0 |
| Retry ledger gate | `pass_1_c1_v2_complete_held_pre_c2` |

### The 3 new draft characteristics in substrate

| seq | term | characteristic_id | cert_id | source path |
|---:|---|---|---|---|
| 3 | transportation method code | `b5999e2e-5c04-46eb-818d-cd7ab9933131` | `c8a2aaa1-d7b6-4e26-aa95-f7fe762164eb` | v1 APPROVE_FOR_DRAFT → v2 C5 confirm |
| 5 | incoterms code | `679cda4b-3952-4337-b6d1-8def0b2083ff` | `eb41c81a-e35b-4224-8191-6d1b5cd45790` | v1 APPROVE_FOR_DRAFT → v2 C5 confirm |
| 2 | payment method code | `61b92f99-5450-41f0-92c0-84fd9b61aa14` | `a763af37-4a43-4afd-807c-a140ecb9e781` | v2 panel APPROVE_FOR_DRAFT → v2 C5 confirm |

All 3 at `lifecycle_state='draft'`. Each holds the term in `uq_characteristic_term_live` (the unique-on-`term` index for non-superseded rows), so subsequent waves cannot claim the same term without first superseding these.

**C1 execution is held.** No further C1 panel call, C5 confirm, or substrate mutation is authorized by this contract.

## 4. C1 legacy attempt disposition

### 4.1 The old C1 v1/v2 attempt is diagnostic-only.

The old attempt is preserved as **audit history and feedback corpus**. It is NOT an execution precedent and NOT a row-by-row repair target. Specifically:

- **Old v1/v2 packet hashes are superseded.** A future clean C1 restart computes fresh packet_hashes from Desktop-prepared content; the v1 evidenceHash (sha256 of citedText + AR) and the v2 packet_hash (sha256 of proposedName + def + sourceLabel + citedText + classification + global_rationale + shape) are no longer authoritative for any future row. A row with the same bf_name in the clean restart is treated as a fresh candidate, not a retry.
- **Old row classifications are not authoritative for future execution.** The v2 5+2 bucketing (panel_ready_retry / confirm_existing_approval_later / defer_insufficient_evidence / map_to_existing_characteristic / operator_semantic_decision / reject_*) was script-side reasoning. Desktop produces fresh dispositions per row; old dispositions are *evidence*, not the queue.
- **Old panel outcomes remain as feedback corpus only.** The 28 v1 + 3 v2 `bcf.panel_output_record.verdict_payload_json` review_reasons are a high-value Desktop input: they tell Desktop *exactly* what the F4-v2 panel will reject and why. Desktop reads them, learns the substantive failure modes, and prepares packets that would clear those failure modes.
- **Do not create a "repair the 28" workstream.** No script will be authored to re-issue the 28 v1 parks with tweaked packets. No script will retry the 2 v2 OPERATOR_REVIEW rows under a v2.1 packet. The semantic prep responsibility is now Desktop's.
- **Do not retry any old packet.** Any panel call posted with a packet_hash that matches a v1 or v2 hash is a violation of this contract.
- **The 3 draft-authored characteristics remain in substrate as draft state.** They must be accounted for in the next clean compile as `already_draft_authored` rows. They are not duplicated, not re-proposed, not superseded.
- **The 28 v1 + 3 v2 panel outcomes must be preserved as evidence for packet-prep improvement.** They live in `bcf.panel_output_record` (Postgres) and in the JSONL artifacts `pass1-c1-outcomes-2026-06-24.jsonl` + `pass1-c1-v2-panel-outcomes-2026-06-24.jsonl` + `pass1-c1-v2-confirm-outcomes-2026-06-24.jsonl`. These are immutable audit history; the clean restart bundle includes them as Desktop input but does not overwrite them.

### 4.2 Classification of the 40 old C1 rows

| Bucket | Count | Definition | Future action |
|---|---:|---|---|
| **A. Draft-authored rows, retained as current substrate** | **3** | Rows already authored at `lifecycle_state='draft'` and holding their term in substrate. | Excluded from future C1 panel re-prep. Marked `already_draft_authored` in any future skeleton bundle. May be promoted draft→active via a separate publication step if and when the operator authorizes; that decision is independent of the broad-foundation-buildout pipeline. |
| **B. Old v1 hard reject, feedback only** | **1** | seq 18 `date_code` — verdict_code `REJECT`, defect_code `PROV_FABRICATED` (proposed definition not grounded in cited evidence). | Not individually remediated now. Desktop reads the REJECT payload as a calibration data point for the "PROV_FABRICATED" failure mode. The clean C1 restart may or may not include `date_code` as a candidate; Desktop decides based on whether a substantive Global meaning is available. |
| **C. Old v1 OPERATOR_REVIEW parks, feedback only** | **25** | seq 1, 4, 6–9, 12–17, 19–28 — script-built v1 packets failed M2/M8/M9/Global checks. | Not individually remediated now. The 25 substantive review_reason payloads form the bulk of the Desktop calibration corpus. The clean C1 restart may include some of these candidates with Desktop-authored packets; others may be reclassified as map_to_existing / defer / operator_semantic_decision / reject. Old dispositions are evidence, not the queue. |
| **D. Old v2 parked rows, feedback only** | **2** | seq 38 `gender_code` / proposed `sex code`, seq 39 `marital_status_code` — script-built v2 packets failed because the Global standards anchor (ISO/IEC 5218, UN/CEFACT TDED) was in `definition` not `citedText`. | Not individually remediated now. Desktop reads the v2 review_reason as evidence that the Global anchor MUST live in the citation, not the proposed definition. |
| **E. Never-run old C1 rows** | **12** | seq 29–37, 40 — the executor halted at 28/40 in the v1 batch and the v2 batch ran only 3 (seq 2, 38, 39), so 12 rows were never panel-attempted. | Not promoted to "panel-ready" by being unrun. They re-enter the clean restart on the same footing as every other row: Desktop reads provenance, OAGIS evidence, substrate context, standards reference, and produces a fresh per-row disposition + packet. |

### 4.3 Overlap clarification

- **Historical panel outcome buckets are audit history.** Buckets A–D describe what the panel said about the 31 rows that were attempted. Bucket E describes what was never attempted.
- **The future execution queue is regenerated cleanly.** It is not a transformation of A–D. It is a fresh disposition assignment produced by Desktop per row, after Desktop reads the skeleton + context bundle (which includes A–D as input, not as queue).
- **Old row status alone is not the future queue.** A row in old bucket C ("v1 OPERATOR_REVIEW") may end up in the clean restart as `panel_ready_retry` (Desktop authored a substantively different packet), `map_to_existing_characteristic` (Desktop saw it should reuse a substrate row), `defer_insufficient_evidence` (Desktop sees no path to Global classification), `operator_semantic_decision` (Desktop flags the framing ambiguity), `reject_source_field_copy` (Desktop sees the OAGIS source-field is the whole proposed name), `reject_circular_or_generic` (Desktop sees the term is a representation-term-shape), or `already_draft_authored` (only the 3 in bucket A).

## 5. Clean C1 restart under Desktop-prep method

When operator authorizes the clean C1 restart, the procedure is:

### 5.1 Regenerate C1 candidate skeletons from primary sources

Skeleton input is deterministic. It must combine:
- current substrate (active + draft, including the 3 C1 drafts);
- the A0 / A0.5 catalogue rows (the 40 C1 entries; the broader 217 for later waves);
- the OAGIS extract raw field records (`data/oagis-finance-extract-enriched-2026-05-15.json`);
- existing panel feedback corpus (28 v1 + 3 v2 `bcf.panel_output_record` payloads).

The skeleton output is a per-row JSON record with provenance, OAGIS field record, shape tuple, used_by_bc target count, and all available evidence — but no proposedName, definition, classification, or disposition.

### 5.2 Account for the 3 draft-authored characteristics

Each clean-restart skeleton row must check whether the bf_name resolves to an existing draft. Specifically:
- seq 2 `payment_method_code` resolves to `61b92f99-…` (draft) — skeleton marked `already_draft_authored` and **excluded** from the Desktop-prep set.
- seq 3 `transportation_method_code` resolves to `b5999e2e-…` (draft) — same.
- seq 5 `incoterms_code` resolves to `679cda4b-…` (draft) — same.

These 3 are NOT duplicated, NOT re-proposed, NOT re-prepared by Desktop. They simply hold their terms; future BC bindings will reference them by characteristic_id.

The remaining 37 rows enter the Desktop-prep set.

### 5.3 Desktop prepares fresh semantic packets

For each of the 37 rows, Desktop produces a per-row packet (schema in §7). Desktop performs:
- contextual interpretation of the OAGIS evidence (is it substantive? is it boilerplate? is it partner-negotiated? does it carry a standards anchor?);
- substrate sibling-pattern lookup (is there an active characteristic that this row should reuse with a role qualifier? is there a substrate pattern that suggests admission as a sibling?);
- standards-reference matching (is the value property published in ISO 20022 / ISO/IEC / UN/CEFACT / ICC / NMFC / WCO / UCUM / UN Rec 20 / etc.?);
- authored proposedName (not transliterated from OAGIS field);
- genus-and-differentia definition (not restating the term, not embedding source attribution as meaning);
- substantive citedText (multi-source where the Global anchor lives outside the OAGIS field; XSD boilerplate auto-rejected);
- Global/domain rationale (cross-entity reuse count / standards-backed / sibling-pattern citation);
- map-to-existing decision (if a substrate row already governs this concept);
- defer / operator-semantic-decision / reject disposition (per §7).

### 5.4 Transport only `panel_ready_retry` rows that the operator approves for transport

After Desktop returns the packet set:
- the transport script validates each packet against the JSON schema (§7) and recomputes packet_hash;
- the operator reviews the packet set and approves a subset for transport;
- the transport script posts only the approved `panel_ready_retry` rows to F4-v2;
- the transport script posts no other disposition without explicit per-row operator authorization;
- the C5 confirm path is invoked only when an F4-v2 outcome is `awaiting_operator_confirm` AND the operator authorizes the confirm.

### 5.5 No C2 until clean C1 restart is closed or explicitly abandoned

Pass 1 C2 (date / timestamp characteristics — 46 proposed) does NOT begin while clean C1 is in progress. If the operator chooses to abandon the clean C1 restart, C2 entry requires an explicit instruction. The retry ledger gate remains `pass_1_c1_v2_complete_held_pre_c2` until the operator flips it.

## 6. Desktop input bundle

The Desktop input bundle is a single deterministic export produced by a (future) bundler script. It contains everything Desktop needs to prepare semantic packets *offline*, in one read. It does NOT include credentials or any live-API surface.

Bundle contents:

| Item | Source | Format | Notes |
|---|---|---|---|
| A0 retry ledger rows for C1 and later waves | `bcf-oagis-retry-ledger-2026-06-24.md` + future ledger revisions | YAML/JSON extract | per-row provenance + admission_rationales + used_by_bc + packet_hash (old, marked deprecated) |
| A0.5 catalogue rows | `bcf-oagis-a0.5-template-catalogue-2026-06-24.md` | per-cluster matrix | 217 candidate chars across C1–C6 + 13 entity slices + RED packets |
| OAGIS raw field records | `data/oagis-finance-extract-enriched-2026-05-15.json` | JSON | 133 nouns / 2,868 scalar fields with description, oagis_data_type, representation_term, data_type, semantic_role, bf_name, description_source |
| Current substrate — active entities | `concept_registry.entity WHERE lifecycle_state='active' AND archived_at IS NULL` | JSON snapshot | 26 rows + version + slice metadata |
| Current substrate — active characteristics | `concept_registry.characteristic WHERE lifecycle_state='active' AND archived_at IS NULL` | JSON snapshot | 62 rows with `term`, `definition`, shape tuple (from version table) |
| Current substrate — active BCs | `concept_registry.business_concept WHERE lifecycle_state='active' AND kind='value' AND archived_at IS NULL` | JSON snapshot | 194 rows with entity placement + characteristic binding |
| Current draft characteristics | `concept_registry.characteristic WHERE lifecycle_state='draft' AND archived_at IS NULL` | JSON snapshot | includes the 3 C1 drafts (`b5999e2e`, `679cda4b`, `61b92f99`) + `fiscal period` |
| Existing characteristic definitions and shape tuples | join characteristic + characteristic_version | JSON snapshot | the substrate vocabulary against which Desktop checks no-synonym admission |
| Sibling BC examples | join business_concept + entity + characteristic | JSON snapshot | shows existing role-placement patterns (e.g. how `country code` is used by multiple BCs with role qualifiers) |
| 28 v1 panel verdict_payload_json rows | `bcf.panel_output_record WHERE panel_run_uid IN (28 v1 uids)` | JSON | substantive review_reason / details — the M2/M8/M9/Global failure-mode corpus |
| 3 v2 panel verdict_payload_json rows | `bcf.panel_output_record WHERE panel_run_uid IN (3 v2 uids)` | JSON | substantive review_reason / approve_for_draft recommendation for `payment_method_code` |
| Known standards reference index | curated list, to be authored | JSON | ISO 20022, ISO/IEC 5218, ICC Incoterms, UN/CEFACT TDED, NMFC, UN Rec 20, UCUM, WCO HS, NACE, ICD, etc. — each with the value-property domain it governs |
| DEC-f94895 / A1–A5 rules | `bc-docs-v3/docs/adrs/ADR-f94895.md` | markdown | program-execution authority + concurrency / cap / pin posture |
| DEC-fb0b12 amendment doctrine | `bc-docs-v3/docs/adrs/ADR-fb0b12.md` | markdown | editorial amendment E1–E6 test for held packets |
| BCF registry doctrine | `bc-docs-v3/docs/foundation/the-contract-grammar.md` + `the-invariants.md` + `the-evaluation-boundaries.md` | markdown | the six invariants + boundary inventory + twelve-artifact contract grammar |
| F4-v2 Vocabulary Admission Checklist | from `bcf.panel_output_record` checklist_answers schema (M1–M10) | extracted spec | what the panel actually tests; Desktop targets every MUST item explicitly |

Bundle file layout (suggested):
```
desktop-prep-bundle/<bundle-uid>/
  meta.json                            (bundle-uid, built-at, source-commit-shas, contract-version)
  skeletons/c1/                        (37 row JSONs for clean C1; future waves add c2/, c3/, …)
    pass1-c1-clean-XX-<bf>.json
  substrate/
    entity.json
    characteristic.json
    characteristic_version.json
    business_concept.json
    business_concept_version.json
  oagis/
    extract.json                       (full enriched extract, frozen at bundle build)
  feedback-corpus/
    v1-panel-outcomes.json             (28 rows)
    v2-panel-outcomes.json             (3 rows)
  standards/
    standards-reference-index.json     (curated, to be authored)
  doctrine/
    dec-f94895.md
    dec-fb0b12.md
    foundation-chapters/
      the-contract-grammar.md
      the-invariants.md
      the-evaluation-boundaries.md
    vocabulary-admission-checklist-v1.md
```

The bundler is a future deterministic script (suggested name `_desktop-prep-bundle.mjs`); writing it is *not* part of this contract. This contract specifies the bundle shape; the bundler implementation is the next-session deliverable.

## 7. Desktop output JSON schema

For each candidate, Desktop outputs one JSON file with the following fields. All fields except where noted are required.

### 7.1 Identity + lineage

- `candidateRef` — string, unique within the clean restart. Suggested format: `pass1-c1-clean-XX-<bf_name>`.
- `source_status` — enum:
  - `never_run` — bucket E from §4.2 (12 rows)
  - `v1_park` — bucket C (25 rows)
  - `v1_reject` — bucket B (1 row, seq 18)
  - `v2_park` — bucket D (2 rows)
  - `draft_authored` — bucket A (3 rows, but these are EXCLUDED from Desktop-prep; `source_status` is only emitted if Desktop is asked to acknowledge them as substrate, not propose them)
  - `clean_restart` — the catch-all when the clean restart introduces a row not in the old 40 (e.g., from a future wave; not expected in clean C1)

### 7.2 Disposition

- `disposition` — enum:
  - `panel_ready_retry` — Desktop has authored a clean packet that should clear M1–M10 + Global; eligible for F4-v2 transport.
  - `already_draft_authored` — substrate already holds this concept at draft state; no panel call, no proposal.
  - `map_to_existing_characteristic` — substrate already holds the Global parent; this row is a role-placement at BC binding, not a new char. Carries `mapTo` field with the target term + characteristic_id.
  - `defer_insufficient_evidence` — OAGIS evidence is XSD boilerplate / partner-negotiated / polysemous / thin / standards-anchor not available. No panel call.
  - `operator_semantic_decision` — substantive but Global scope is ambiguous; operator must decide admit-vs-broaden-vs-scope (UOM family parent, location family parent, HR/logistics/customs/inventory/procurement domain admission, root-vs-leaf, etc.).
  - `reject_source_field_copy` — proposed concept is structurally a transliteration of the OAGIS field; no authored business term available.
  - `reject_circular_or_generic` — proposed term is a bare representation term (`code`, `identifier`), or the only available semantics is "X code" for any X — generic placeholder.

### 7.3 Authored packet (only required when `disposition='panel_ready_retry'`)

- `proposedName` — string, authored (not bf_name transliteration).
- `definition` — string, genus + differentia. Must not restate `proposedName`. Must not embed source attribution as meaning.
- `candidateEvidence.sourceLabel` — string, e.g. `"OAGIS Standard 10.12 — <noun>.<component>.<field_path>"`. May include cross-source citation when the Global anchor lives outside OAGIS.
- `candidateEvidence.citedText` — string, ≤ 500 chars (cap raised from A0.5 Cat-3's 200 to accommodate multi-source citation when the Global anchor is a separate standard). Must carry the substantive business meaning AND the Global anchor when applicable. XSD primitive boilerplate is disallowed.
- `classification` — enum: `global` | `domain_specific` | `not_global_defer`.
- `global_rationale` — string, present when `classification='global'`. Cites: standards-backed (named standard publishing the Global enumeration), cross-entity reuse (≥ 3 named entities), sibling-substrate pattern (named existing Global char with the same standards-backed enumerated shape) — at least one of these must be a real, verifiable citation.

### 7.4 Quality signals

- `semantic_identity_confidence` — enum: `high` | `medium` | `low`. Desktop's self-assessment of how confidently the proposed identity is distinguishable from existing substrate and from other proposed candidates.
- `semantic_identity_reason` — string, ≥ 80 chars. Names the deciding factor: existing-substrate near-duplicate analysis, sibling-pattern comparison, standards-backed disambiguation, OAGIS gloss substantiveness, etc.
- `definition_quality` — enum: `pass` | `fail` | `needs_operator`. Desktop's self-check of the definition against §3.2 of the v2 design (genus + differentia, non-circular, no source attribution as meaning, distinguishes Global from entity placement role).
- `evidence_quality` — enum: `substantive` | `boilerplate` | `thin` | `standard_backed` | `partner_defined`. Desktop's classification of the citedText quality.

### 7.5 Provenance + context

- `shape_tuple` — string, e.g. `"code|code|dimension"` (representation_term | data_type | semantic_role).
- `used_by_bc_target_count` — integer, from A0.5 catalogue.
- `target_entities` — array of strings; entity slices this characteristic is expected to bind into at Pass 3.
- `admission_rationales` — array; subset of `[AR-1, AR-2, AR-3, AR-4, AR-5]` per DEC-f94895.
- `prior_panel_feedback_summary` — object or null; carries summarized review_reason from the old v1/v2 panel attempt if `source_status` was `v1_park` / `v1_reject` / `v2_park`. Format: `{ panel_run_uid, verdict_code, summarized_review_reason, addressed_by_this_packet: true|false|partial }`.

### 7.6 Fingerprint + audit

- `packet_hash` — sha256 over the deterministic concatenation `(proposedName ‖ definition ‖ sourceLabel ‖ citedText ‖ classification ‖ global_rationale ‖ shape_tuple)`. The transport script recomputes and verifies before posting.
- `desktop_prep_session` — string identifier of the Desktop session (e.g. claude-code session-uid).
- `desktop_prep_timestamp` — ISO-8601 UTC timestamp.

A schema validator is the responsibility of the transport script (§8). A reference JSON Schema document will be authored alongside the bundler in the next-session deliverable set.

## 8. Transport script boundary

The transport script has **no semantic authority**. It is a thin layer that converts validated Desktop packets into governed F4-v2 / C5 API calls and records outcomes.

### 8.1 The transport script MAY:

- read Desktop output packets from a known directory;
- validate each packet against the JSON Schema (§7);
- recompute `packet_hash` over the deterministic content and verify it equals the packet's `packet_hash` field — REFUSE the packet if mismatched;
- verify `candidateRef` exists in the current clean ledger and has not already been transported;
- verify `source_status` is consistent with the clean ledger row (e.g., a row marked `already_draft_authored` in the ledger cannot be transported as `panel_ready_retry`);
- POST `panel_ready_retry` packets to `POST /api/bcf/registry-authoring-runs` with operator-approved concurrency (≤ 2) and 180s per-row timeout, recording outcomes to a JSONL trace + summary JSON;
- POST C5 confirms to `POST /api/bcf/registry-shape-certifications/confirm` ONLY for rows the operator explicitly approves for confirmation, sequentially, with writer concurrency = 1;
- record every outcome to the ledger trace + a per-run summary file;
- enforce DEC-f94895 caps (program spend, panel-call count, per-row latency, wall-time, concurrency).

### 8.2 The transport script MUST NOT:

- rewrite `proposedName` (even for whitespace / case normalization);
- rewrite `definition`;
- rewrite `citedText` or `sourceLabel`;
- choose `disposition` or change `mapTo` targets;
- infer semantics from regex / heuristics / term matching;
- retry old v1 or v2 packet hashes (the script maintains an old-hash deny list, populated from the v1 outcomes JSONL + the v2 outcomes JSONL);
- post any disposition other than `panel_ready_retry` to F4-v2;
- post any C5 confirm without explicit per-row operator authorization;
- write directly to substrate (no `concept_registry.*` INSERT/UPDATE/DELETE from the script);
- enrich, mutate, or substitute Desktop output; refusal is the only response to a malformed packet.

A future implementation file `_pkt-validate-and-transport.mjs` (or similar — name TBD) realizes this surface. Its creation is not part of this contract; this contract specifies the boundary.

## 9. Governance boundary

| Surface | Authority | Allowed action |
|---|---|---|
| **A0 deterministic compile** | none semantic | extracts candidates; does not interpret |
| **Claude Code Desktop** | proposes | prepares per-row packets; does not write |
| **Transport script** | none semantic | validates, hashes, posts, ledgers; does not interpret, does not rewrite, does not bypass |
| **bc-core / bc-ai F4-v2 panel** | governed review | runs Vocabulary Admission Checklist; decides verdict_code; does not write substrate directly |
| **C5 / single writer** | governed write | mints cert, runs F3 registerCharacteristic, creates substrate row at draft; single-writer concurrency |
| **Operator** | final authority | approves each step; resolves operator_semantic_decision rows; approves transport per row; approves C5 confirms |

Five non-negotiable rules:
1. **Desktop prepares semantic proposals.** Desktop is not registry authority.
2. **bc-core / bc-ai F4-v2 remains the only governed semantic review surface.**
3. **C5 / single writer remains the only substrate write path.**
4. **Desktop output does not create substrate.**
5. **All panel and writer outcomes must be ledgered** — to the retry ledger and to the per-batch JSONL traces. Audit history is immutable; no row's prior outcome is rewritten by a future attempt.

The old C1 attempt remains diagnostic history under all five rules. No future workstream supersedes that designation.

## 10. Next safe action after this contract

The next safe step after this contract is:

> **Generate a Desktop input bundle for a clean C1 restart** (§6).

Specifically: file a held design + start a next session to author the bundler script `_desktop-prep-bundle.mjs`, the standards reference index, and the JSON Schema for the Desktop output packet. Run the bundler once for the 37 clean-C1-restart skeletons + context. Hand the bundle to Claude Code Desktop. Desktop returns the packet set. Operator reviews. Operator approves a transport subset. Transport script validates + transports the approved subset. Outcomes are ledgered. Substrate writes (if any) land via the single writer.

**Do not execute transport until**:
- Desktop returns the packet set,
- the packet set is schema-validated and hash-verified by the transport script,
- the operator explicitly approves the transport subset and the per-row C5 confirms.

No panels. No confirmations. No substrate mutation. No C2. No further C1 execution. No retry from old packet hashes.

Held.
