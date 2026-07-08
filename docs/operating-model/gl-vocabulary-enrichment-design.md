---
id: gl-vocabulary-enrichment-design
order: 10.85
title: "GL Vocabulary Enrichment — design (Metric Directory GL gaps)"
status: drafting
authority: draft-authoritative
depends_on: [business-vocabulary, metric-directory, metric-management-system]
governing_sources:
  - Business Vocabulary (BCF — entity / characteristic / business_concept, semantic roles, canonical_value_set)
  - The Metric Directory (the feasibility gate that surfaced these gaps)
  - Foundation (Invariant I — meaning at its boundary; source-agnosticism / D441)
governing_adrs:
  - DEC-b5c7ff (D506 — Metric Directory; its bcf_gap feasibility flag drives this backlog)
errata_referenced: []
ratification: design surfaced by the Metric Directory feasibility gate 2026-07-08; not yet authored; input to governed BCF authoring
scope_locks: documentation-only; no substrate mutation; no panel run; no PR
related:
  - business-vocabulary.md (BCF authoring authority)
  - metric-directory.md (the value layer that surfaced these gaps)
---

# GL Vocabulary Enrichment — design

## Why this exists

Extending the Metric Directory (DEC-b5c7ff / D506) to General Ledger surfaced a hard finding: **the valuable GL metrics are almost entirely BCF-gated.** The GL BCF vocabulary today offers only four discriminating dimensions — `GL Account.account_class_code`, `Journal Entry.currency_code`, `Journal Entry.status`, `Journal Entry Line.ledger_account_identifier` — while the GL seed reservoir wants metrics keyed on entry-method, line-type, error/rework, intercompany, reconciliation events, and close events, **none of which exist**. So only the basic counts/sums are `bcf_ready`; the journal-quality program is `bcf_gap`.

This is the directory's feasibility gate doing its job: the bottleneck has shifted from metric-authoring to **BCF vocabulary**. This document is the design for closing that gap. It is a **proposal** — authoring runs through the governed BCF panel; nothing here is authored yet.

## The six gaps

### A. Dimensions / status on EXISTING entities (small — add a governed concept + canonical_value_set)

| # | Concept | Entity | Role · representation | Canonical values | Unblocks |
|---|---|---|---|---|---|
| # | Concept | Entity | Role · representation | Canonical values | Status |
| 1 | **entry method** | Journal Entry | dimension · code | `manual`, `automated`, `system_generated`, `partially_system_generated` | ✅ **AUTHORED + ACTIVE** (2026-07-08) — characteristic `9485cffa`, concept `eee06046`. Unblocks % processed manually / automatically / partially. |
| 2 | **line type** | Journal Entry Line | dimension · code | `first_time_originating`, `corrective_adjusting`, `intercompany`, `recurring`, `other` | ✅ **AUTHORED + ACTIVE** (2026-07-08) — characteristic `0bc731b8`, concept `ffaaee59`. Unblocks corrective/adjusting %, first-time %, intercompany-line %, line-type-other %. |
| 3 | ~~**processing quality**~~ | Journal Entry | ~~status · code~~ | ~~`error_free_first_time`, `reworked`, `errored`~~ | ❌ **REJECTED — DO NOT AUTHOR** (M5, 2026-07-08). |
| 4 | ~~**intercompany indicator**~~ | Journal Entry | ~~status · code~~ | ~~`intercompany`, `standalone`~~ | ❌ **DROP** — redundant with #2's line-level `intercompany` (see below). |

**#3 processing quality — rejected by the M5 gate (2026-07-08).** An attempt to author this was withdrawn as an admission error. The BCF panel's M5 (synonym / near-duplicate) check correctly found: (a) it overlaps the governed **`status`** characteristic ("current lifecycle or processing state of a record"); (b) its `reworked` value **duplicates #2 `line type`'s `corrective_adjusting`** (both = "this posting is a correction of a prior entry"); (c) it is a **metric-driven convenience aggregation** (a first-time-right grouping) composed from existing governed facts, not a genuinely new value-property (Invariant I / no fact-shape-tied vocabulary). Therefore `journal_entry_error_rate` and error-free-first-time % **must be composed at the metric layer from `line type` (`corrective_adjusting`) + `status`** — not from a new BCF term.

**#4 intercompany indicator — drop.** The `intercompany` value already exists at line grain in #2. A header-grain "any line is intercompany" metric composes from #2; a separate header characteristic is a duplicate vocabulary path.

### B. New ENTITIES (larger — an event/master + its concepts + reference roles)

| # | New entity | Key concepts | Unblocks |
|---|---|---|---|
| 5 | **GL Account Reconciliation** | reconciliation date (temporal); reconciliation status (`reconciled`/`pending`/`overdue`); reconciled GL account (reference → GL Account); fiscal period (reference) | account_reconciliation_completion, subledger_to_gl_reconciliation_delay, intercompany_reconciliation_rate |
| 6 | **Financial Close** | close start / completion date (temporal); close status; close type (`monthly`/`quarterly`/`annual`); fiscal period (reference); legal entity (reference) | close_cycle_time, monthly-close cycle time, post_close_adjustment_count (adjustments dated after the close-completion date) |

## Discipline

- **Canonical, not source literals.** These are governed dimensions with declared `canonical_value_set`s. The reader/canonical layer (repair-locations A/C) maps source-system codes (SAP `BLART`, entry-type fields, close-task-system statuses) onto these values. Metrics discriminate on the canonical value only (D441 source-agnosticism; Invariant I).
- **A-layer feasibility for #5/#6.** New entities imply **source data** (reconciliation logs, close-task systems) a tenant may or may not emit. Their feasibility is admission-boundary (does the source provide it), not merely BCF — confirm source availability before authoring the entity.
- **Sequencing.** #1 (entry method) and #2 (line type) are AUTHORED + ACTIVE (2026-07-08). #3 and #4 are rejected/dropped (above) — the journal-quality metrics they were meant to unblock compose from #1/#2 + the existing `status` characteristic at the metric layer. #5–#6 are the heavy lift (new entities + source dependency) — later, gated on A-layer source availability.
- **Retry discipline (lesson, 2026-07-08).** BCF panel parks are of two kinds. A **structural** park ("recommendation malformed: checklist_answers must carry {answer,basis} for M1–M10") is maker output-quality noise — a retry is legitimate. A **semantic** park (M5 synonym/near-duplicate collision, or insufficient evidence) is a real objection — **do not retry to get a different maker roll**; that is forcing past the gate. Read `bcf.panel_output_record.verdict_payload_json->>'review_reason'` before any retry, and only retry structural parks. Authoring #3 violated this and had to be withdrawn.

## Authoring path (governed)

Concepts are authored through the **BCF authoring panel** (`POST /api/bcf/registry-authoring-runs` → maker/checker/moderator consensus → C5 certification → F3 write). High-risk vocabulary APPROVEs (`createCharacteristic`) park as `awaiting_operator_confirm` and complete via `POST /api/bcf/registry-shape-certifications/confirm` (`{panelRunUid, subjectKind, actionCode, rationale ≥40 chars}`). Panel runs are in-process in bc-core and **die on bc-core restart** — coordinate with any concurrent BCF session before firing.

Once authored, the Metric Directory's `bcf_gap` GL members flip to `bcf_ready`, and the journal-quality metrics can be authored via the metric drive against the value blueprint.
