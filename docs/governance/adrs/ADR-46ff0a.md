---
uid: DEC-46ff0a
title: "D442 Amendment 1 — resolve lineage-vs-version semantic_role collision discovered at Packet 1+2 entry"
description: "Sibling amendment to DEC-61850f (D442). Live `concept_registry.business_concept` already carried an unused `semantic_role text NULL` column at position 9 with different historical intent (rep-term qualifier per DEC-02f5a9/D414's F2 migration). Zero realized data across 109 active BCs. Operator decision 2026-06-13: drop the legacy lineage column entirely; add D442's semantic_role on business_concept_version per D442 D2; amend CHECK constraints to permit semantic_role='reference' on reference-kind BC versions per D442 D1 enum. Preserves D442 D2 (per-version placement) and D5 (read-time resolution at MCV-bound version)."
status: decided
date: 2026-06-13T07:54:38.441Z
project: bc-docs
domain: mcf
subdomain: metric-contract-semantics
focus: schema
---

# D442 Amendment 1 — resolve lineage-vs-version semantic_role collision discovered at Packet 1+2 entry

## Context

See decision text below.

## Context

DEC-61850f (D442) was decided 2026-06-13 with D2 stipulating that `semantic_role` should be stored on `concept_registry.business_concept_version` (per-version, not on the lineage anchor). The rationale was D5 — MCVs bind to a specific BC version, and PE-MC-12 reads role/value-set from that bound version, preserving role-stability across BC supersessions.

When Packet 1+2 entered execution scope under SES-4c82c3 (2026-06-13), read-only schema research discovered a structural collision:

1. `concept_registry.business_concept` ALREADY carries `semantic_role text NULL` at column position 9. The column was added by the F2 migration `docker/redesign/migrations/20260521-f2-concept-registry-schema.sql` under ADR DEC-02f5a9 (D414, May 2026).
2. The legacy column has a different intent. The Supersede DTO comment (`src/registry/concept-registry/registry-authoring.dto.ts:171-172`) describes it as: "used on value concepts only when the rep-term needs further qualification" — a rep-term qualifier role, NOT D442's filter-role classification.
3. The legacy column is part of the immutability trigger set (`tg_business_concept_meaning_immutable`, DEC-02f5a9 §3) — UPDATE raises EXCEPTION.
4. The legacy column is constrained by `business_concept_kind_metadata_chk`: `semantic_role IS NULL` when `kind='reference'`. The CHECK was authored on the assumption the column would only carry rep-term qualifier values for value-kind BCs.
5. Live state: ALL 109 active BCs (109 lineages, 109 versions, 1:1) have `semantic_role=NULL`. Zero realized usage.

This collision was not anticipated in D442. The shape-lock decision was correct in spirit (per-version placement preserves D5) but assumed the column did not already exist on lineage.

## Decision

**Drop the legacy lineage-level `business_concept.semantic_role` column entirely. Add D442's `semantic_role` on `business_concept_version` per D442 D2.**

Three specific sub-decisions:

### A1 — Drop legacy column

`ALTER TABLE concept_registry.business_concept DROP COLUMN semantic_role` is part of the Packet 1+2 DDL transaction.

The column is NOT renamed to `rep_term_qualifier`. The legacy intent ("rep-term qualifier") was never operationally realized — zero BCs carry a value. Preserving a dead column would create confusing dual-meaning naming with the new `business_concept_version.semantic_role` and add ongoing schema noise without any historical-data preservation benefit.

Coordinated changes required by this drop:
- Immutability trigger `tg_business_concept_meaning_immutable`: remove `semantic_role` from its watched-column set on `business_concept`. (The new column on `business_concept_version` is governed by version-immutability — versions are append-only, not UPDATE-protected, per Foundation Invariant III on the version table.)
- CHECK `business_concept_kind_metadata_chk`: remove the `semantic_role IS NULL` clauses tied to kind. The kind/role coupling moves to the version-side constraint below.
- DTO `SupersedeBusinessConceptBodyDto.semanticRole` (registry-authoring.dto.ts:175): remove or migrate to the new field shape. The field was optional and unused.
- DTO `CreateBusinessConceptInput` if it carries semanticRole: same migration.
- Service `RegistryAuthoringService.supersedeBusinessConcept` + sibling create path: remove the legacy field plumbing; add the new field plumbing.
- Drizzle schema `business-concept.ts:82`: drop the `semanticRole` field on the businessConcept table; add it on businessConceptVersion.
- 7 downstream files referencing `semantic_role` (mcf-read.service.ts, mcf-read.service.spec.ts, bcf-correction-recommendation.dto.ts, prompt-loader.spec.ts, oagis-seed.service.ts, oagis-d292.ts, bcf-c1-oagis-cert-disposition.spec.ts): audit individually, repoint reads to the new version-side column where applicable, remove dead references where the legacy intent was the target.

### A2 — Add new column on business_concept_version

`ALTER TABLE concept_registry.business_concept_version ADD COLUMN semantic_role text` (initially NULL during migration window; NOT NULL after backfill).

D442 D1 enum (8 values): `strategic_filter`, `diagnostic`, `identity`, `temporal`, `amount`, `status`, `dimension`, `reference`.

New CHECK on business_concept_version:
- `CHECK (semantic_role IN ('strategic_filter','diagnostic','identity','temporal','amount','status','dimension','reference'))` post-backfill, NOT NULL.

### A3 — Kind/role coupling on version

The legacy CHECK forbade non-NULL semantic_role when kind='reference' (rep-term qualifier had no place on reference-kind BCs). D442 D1 makes `reference` a first-class role value for reference-kind BCs.

New CHECK on business_concept_version enforces kind/role coherence by joining the version row to its lineage `kind` (via concept_id FK):
- `kind='reference'` BC versions MUST carry `semantic_role='reference'`.
- `kind='value'` BC versions MUST carry `semantic_role IN ('strategic_filter','diagnostic','identity','temporal','amount','status','dimension')` — every D1 value EXCEPT `reference`.

This coupling is enforced via a CHECK that references a SQL function reading the lineage `kind` (or equivalently a trigger on INSERT/UPDATE to the version table). The Packet 1+2 DBCP will pick the implementation mechanism after reviewing existing trigger patterns.

### Why amendment-not-supersession

This amendment preserves D442's core architecture (per-version placement + D5 read-time resolution + D6 requirement matrix). It only resolves an unanticipated schema collision discovered at entry. D442 remains decided and is not superseded. Future readers should treat D442 + this amendment together as the operative shape lock.

## Consequences

**Accepted:**
- One-time coordinated DDL transaction touching: business_concept (DROP COLUMN), business_concept_version (ADD COLUMN + CHECK), immutability trigger (column-set amendment), kind-metadata CHECK (DROP semantic_role clauses), kind-role coupling CHECK or trigger (NEW).
- Code changes across ~9 files removing legacy `semantic_role` references and adding D442 semantic_role plumbing.
- DTO change is breaking for any client passing `semanticRole` — but no client uses the field (zero realized data confirms no operational dependency).

**Avoided:**
- Permanent schema noise from a renamed-but-dead `rep_term_qualifier` column.
- D442 D5 stability loss that Path 2 (repurpose in place) would have caused.
- Naming awkwardness of Path 3 (`filter_role`).
- Future readers confused by two columns with overlapping meaning.

**Open follow-up:**
- Packet 1+2 DBCP (forthcoming this session) carries the full DDL + code-change inventory + backfill plan + admission/narrowing validators + tests + rollback.
- TSK-fadcb0 absorbs TSK-7ed42a per operator decision; merge note pending.

## Rejected alternatives

- **Path 2 (repurpose in place):** Keep semantic_role on lineage with new D442 meaning. Rejected — loses D5 per-MCV-binding stability that D442 was specifically careful to preserve. Reclassification of document_type_code from "unclassified" to `diagnostic` (Packet 6a) would be visible immediately to PE-MC-12 against M14-active MCVs, violating Trap A/D mitigation.
- **Path 3 (parallel column with different name):** Add `filter_role` on business_concept_version, leave legacy `semantic_role` alone. Rejected — awkward naming and permanent dead column. Operator §2 rejected.
- **Rename legacy column to rep_term_qualifier:** Preserve possibility of future use. Rejected — zero realized usage, no historical-data preservation benefit, ongoing schema noise.

## References

- Parent ADR: DEC-61850f (D442) — Foundation-shape lock; specifically D2 (per-version placement) and D5 (read-time resolution).
- Antecedent ADR: DEC-02f5a9 (D414) — F2 concept_registry schema (origin of the legacy semantic_role column).
- Live DDL: `bc-core/docker/redesign/migrations/20260521-f2-concept-registry-schema.sql` (legacy column definition).
- Drizzle mirror: `bc-core/src/database/schema/concept-registry/business-concept.ts:82`.
- DTO with stale intent: `bc-core/src/registry/concept-registry/registry-authoring.dto.ts:171-175`.
- Packet 1+2 work session: SES-4c82c3 (checkpoint #1 saved at 'blocked' before this decision; decision unblocks DBCP drafting).
- D441 planning packet: `bc-core/scripts/audit-output/d441-implementation-train-planning-packet-2026-06-13.md`.
