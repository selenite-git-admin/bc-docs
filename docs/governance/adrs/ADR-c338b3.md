---
uid: DEC-c338b3
title: "BF/BO versioning model for supersede-active (Model E)"
description: "Adopt a nullable supersedes_id self-FK on business_field/business_object for C7 supersede-active; two-act supersession completed via C5 operatorAdvance."
status: decided
date: 2026-05-20T04:01:06.983Z
project: bc-core
domain: contracts
subdomain: framework-approval
focus: lifecycle
---

# BF/BO versioning model for supersede-active (Model E)

## Context

Requirements require supersede-active to author a new version that, on reaching active, supersedes the prior version with an explicit successor pointer, the prior version remaining addressable. BF/BO have governance_state='superseded' but no version column, no lineage pointer, and no effective dating. A minimal nullable self-FK (supersedes_id) is the smallest substrate that satisfies the explicit-pointer requirement: version_no and family_uid are derivable by walking the chain, effective dating carries no lineage and duplicates the active/superseded signal, and a ledger-only link cannot hold the pending author-time intent between successor creation and activation. No data backfill is required (existing rows = original version).

## Amendment (2026-05-20) — survey correction: name uniqueness

During D413 PR 1 implementation the substrate inventory below was found **wrong on one point**: it states "No DB UNIQUE on business_field.name / business_object.object_name." Uniqueness **did** exist — as full unique **indexes** (`uq_business_field__name`, `uq_business_object__name`). The survey used a `pg_constraint` query, which does not see `CREATE UNIQUE INDEX`.

Consequence: a same-named successor cannot coexist with an active predecessor under a **full** unique index, so replacing it with a **partial** unique is **mandatory substrate**, not the deferred "active-name partial unique" that **lock 7 (below) is therefore superseded by this amendment**. The D413 PR 1 migration drops the two full unique indexes and creates partial ones with predicate `WHERE governance_state = 'active' OR governance_state IS NULL` (operator decision, 2026-05-20): an `active` predecessor and its draft successor may share a name, while NULL-governance (legacy) rows stay strictly unique. The active-name partial unique is **not deferred** — it is part of the D413 PR 1 substrate DBCP. Implemented in bc-core PR #38.

# BF/BO Versioning Model for supersede-active — Model E

## Dependency
This ADR DEPENDS ON DEC-47a4e7 (C5 operator-driven transition expansion / operatorAdvance). The two-act supersession's completion step — successor approved→active plus the paired predecessor active→superseded — IS operatorAdvance's behavior. DEC-47a4e7 must be filed and implemented before the supersede-active code slice. The two ADRs are a pair.

## Authority / requirements basis
DEC-149ab2 (D411); BCF Requirements Ch.5 "Operator override mechanisms" + "Transition rules" (supersede-active = operator authors a new version; when it reaches active the prior version moves to superseded; active→superseded carries an explicit successor pointer; the prior version remains addressable); Foundation Invariant III (active artifacts immutable; supersession is the only change mechanism); N7 (no hard delete); N8 (no in-place mutation of active). Build-plan §3 C7.

## Substrate inventory (verified against bc_platform_dev)
- business_field: 33 columns; field_id PK, name (NOT NULL), definition, status_code (legacy axis), catalog_state_code (D408 axis, default candidate_import), governance_state (nullable, BCF axis), archived_at, certification_record_id (FK), quarantine_marker.
- business_object: 17 columns; object_id PK, object_name (NOT NULL), display_name, definition_text, status_code, governance_state (nullable). No archived_at, no catalog_state_code, no certification_record_id. Composed of BFs via business_object_field; has business_object_relation rows.
- Neither table has a version column, family/lineage uid, effective_from/effective_to, or a successor/predecessor pointer.
- ~~No DB UNIQUE on business_field.name or business_object.object_name — uniqueness is service-layer only (findByName).~~ **CORRECTED — see Amendment above: full unique INDEXES `uq_business_field__name` / `uq_business_object__name` do exist.**
- certification_record already carries supersedes_primitive_id (uuid, nullable) and action_code='supersede' in the CHECK enum, with a buildCertificationRecord supersede-pair invariant. Zero supersede rows have ever been written.
- governance_state distribution: BF active 1651 / draft 262 / NULL 5157; BO active 194 / draft 1 / NULL 8. review, approved, superseded all unused. Supersession has never occurred.

## Accepted decision
1. Adopt Model E: add one nullable self-FK column supersedes_id (uuid) to business_field (REFERENCES business_field(field_id)) and business_object (REFERENCES business_object(object_id)), with a CHECK supersedes_id <> own-PK. The successor row points back to the predecessor it replaces.
2. Two-act supersession. Act (a) author-successor: an operator endpoint creates a NEW row — content cloned from the predecessor with operator overrides, governance_state='draft', supersedes_id = predecessor id; the predecessor is untouched and stays active. Act (b) complete-supersession: when the successor reaches active via C5 operatorAdvance (DEC-47a4e7), the predecessor flips active→superseded atomically in the same transaction.
3. Add one new certification_record action_code: author_successor — the operator's authoring act for act (a), an operator-authored legacy-shape cert row with rationale in gate_results_json. The completed supersession (act b) is recorded with the existing supersede action_code (primitive_id = successor, supersedes_primitive_id = predecessor).
4. No version_no, no family_uid, no effective_from/effective_to in v1. version_no is derivable (supersedes_id chain length); family identity is the chain; effective dating carries no lineage and partially duplicates governance_state. These may be revisited if as-of-time queries are later required.
5. BF-first, BO-second implementation split. BF is a single-row clone. BO is materially heavier: a new object_id has no composition or relations until cloned.
6. The BO successor clones the predecessor's business_object_field composition and business_object_relation rows by default (into the new object_id), in the same transaction as the successor row insert.
7. **[SUPERSEDED by the Amendment above — the active-name partial unique is mandatory D413 PR 1 substrate, not deferred. The original deferred-lock text follows for the record.]** The active-name partial unique constraint (UNIQUE(name) WHERE governance_state='active') is DEFERRED to a separate DBCP, contingent on a pre-check confirming zero existing active-name duplicates among the 1651 active BF / 194 active BO. It is not part of the v1 supersede-active slice. Name reuse by the successor is permitted because the supersede endpoint is a distinct entry point that explicitly sets supersedes_id (it does not pass through the normal create-time findByName block).

## Rejected alternatives
- Model A (version_no + family_uid on every row): forces a data backfill of all ~7000 BF + ~200 BO rows and makes every "id = the member" call site family-aware. version_no and family_uid are derivable from the chain — premature at v1 chain lengths of 1-2.
- Model C (effective_from/effective_to): effective dating answers "what was active at time T" but carries NO lineage; still needs a pointer. Partially duplicates the active/superseded signal already in governance_state. Adds a backfill. A complement, not a substitute — deferred.
- Model D (ledger-only link, zero BF/BO DDL): the cert ledger records completed acts only; it cannot hold the author-time "successor supersedes predecessor" intent that must persist on a member column between successor creation and activation. Insufficient.

## DDL / DBCP implications
- DBCP: ALTER business_field ADD COLUMN supersedes_id uuid + self-FK + CHECK (supersedes_id <> field_id); same for business_object (self-FK to object_id). Partial index ON (supersedes_id) WHERE supersedes_id IS NOT NULL on each (reverse-lineage lookup).
- DBCP: add author_successor to certification_record_action_code_chk. (operator_advance_state and supersede are covered by DEC-47a4e7 and the existing enum respectively.)
- No data backfill — existing rows: supersedes_id = NULL = original version (correct).
- Deferred separate DBCP: active-name partial unique, after duplicate pre-check.

## Implementation sequence
1. DEC-47a4e7 (operatorAdvance) implemented first — prerequisite.
2. DBCP: supersedes_id columns + indexes + author_successor action_code (apply to bc_platform_dev, verify).
3. BF supersede-active: author-successor endpoint + repository clone + author_successor cert row; activation + predecessor flip via operatorAdvance.
4. BO supersede-active: as BF, plus composition/relation cloning into the new object_id.
5. Deferred: active-name partial unique DBCP (after pre-check).

## Test obligations
- author-successor creates a draft row with supersedes_id set, predecessor untouched and still active.
- author_successor cert row: legacy-shape, rationale in gate_results_json, preserved verbatim (N29).
- Successor activation via operatorAdvance flips the predecessor active→superseded atomically; supersede cert row written; both in one transaction (abort if predecessor not active — per DEC-47a4e7).
- supersedes_id <> own-PK CHECK rejects self-supersession.
- Reverse-lineage query (WHERE supersedes_id = X) returns the successor.
- BO: successor clones composition + relations; counts match the predecessor.
- Name reuse by the successor is permitted; the normal create endpoint still blocks duplicate names.
- Predecessor remains addressable after supersession (Invariant III).

## Hard stops carried into implementation
- supersede-active is unbuildable until DEC-47a4e7 (operatorAdvance) ships.
- The active-name partial unique requires a duplicate pre-check before its DBCP.
- BF successor catalog_state_code starting value (the candidate_import default is wrong for a clone of a certified member) is an implementation decision to resolve in the BF slice.
