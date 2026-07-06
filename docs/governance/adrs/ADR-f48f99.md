---
uid: DEC-f48f99
title: "D418 Historical FK Sink Classification"
description: "Classify operations.bo_enrichment_log and operations.bo_verification_log as historical FK sinks; out of scope for D418 §2 archival; surfaces a Gate 5 dependency for physical disposition of contract.business_object."
status: decided
date: 2026-05-25T05:18:55.419Z
project: bc-core
domain: contracts
subdomain: quarantine-and-retirement
focus: governance
---

# D418 Historical FK Sink Classification

## Context

D418 Gate 1.3 (DB verification) ran an FK-graph sweep across `information_schema` to find all foreign-key constraints whose target is one of the D417/D418 quarantined surfaces. The sweep flagged 14 FK constraints. 12 classified cleanly as `internal_to_quarantine` (FKs between quarantined tables themselves) or `covered_by_apply_predicate` (FKs whose sources are archived via D418 §2).

The remaining 2 FK constraints — `operations.bo_enrichment_log.object_id → contract.business_object` (4,135 rows) and `operations.bo_verification_log.object_id → contract.business_object` (401 rows) — were classified `HIDDEN_ACTIVE_REFERENCE` (i.e. "active rows in a non-quarantined table reference quarantined BOs"). The Gate 1.3 failure verdict was driven primarily by these 2 entries (4,536 of 4,536 hidden references).

Inspection of the source code confirms:

- Both tables are append-only D201 audit trails. DDL comments are explicit: "Business Object enrichment audit trail" and "Business Object verification audit trail (Gemini search + Claude verify)".
- Neither has an `archived_at` column — they follow the append-only audit log pattern, not the lifecycle-managed entity pattern.
- All caller-side READS of these tables in `bc-core/src` are admin/diagnostic views: `findByObjectId(objectId)` returns enrichment/verification history for one BO; `findByVerificationId` is a single-row lookup; daily token aggregation is an admin diagnostic. **No reads of these tables occur in evaluation, admission, canonical resolution, metric computation, boundary execution, readiness, or publication paths.**
- All caller-side WRITES are append-only inserts from the BO enrichment/verification flows (Claude/Gemini-driven).
- The FK constraints exist to preserve referential integrity of audit records — so that an audit row always points to a real BO row that existed at the time of the audited action.

These are, by every operational test, historical audit records rather than active runtime references. The Gate 1.3 `HIDDEN_ACTIVE_REFERENCE` classification is technically correct (active rows + FK to quarantined target) but semantically wrong (the rows are audit history, not runtime references that drive evaluation). A formal decision is needed before Gate 1.3 can re-run with the correct classification.

## Decision

`operations.bo_enrichment_log` and `operations.bo_verification_log` are classified as **historical FK sinks** for the purposes of D417/D418 governance. Their FK references to `contract.business_object` are append-only audit history records, **not active runtime references**. They are explicitly **out of scope** for D418 §2 archival.

### Structural classification criteria

This classification applies structurally — any future table satisfying all five criteria below is automatically classified as a historical FK sink under this ADR without requiring a new ADR:

1. **Schema**: `operations.*`
2. **Table name suffix**: `_log`
3. **Append-only structure**: has `created_at`; has no `archived_at`
4. **No active-runtime reader consumes the table for evaluation, admission, canonicalization, metric computation, boundary execution, readiness, or publication decisions.** Reads are limited to admin diagnostics, audit inspection, or aggregate audit summaries.
5. **FK target** is one of the D417 §2 quarantined surfaces

**Supporting evidence for criterion 4 (not the criterion itself)**: in the current bc-core layout, active-runtime code lives in `bc-core/src/{evaluation,admission,canonical,metrics,boundary,readiness}/` and the corresponding boundary execution paths. Both `operations.bo_enrichment_log` and `operations.bo_verification_log` were verified to have zero readers in these paths at the time of this ADR (see References). The structural rule itself is behavioral — a reader anywhere that consumes the table for a runtime decision (evaluation, admission, canonicalization, metric computation, boundary execution, readiness, or publication) disqualifies the table from this classification, regardless of which folder the reader lives in.

## Consequence — Gate 1.3 audit script (future Gate 1.3.3)

The Gate 1.3 audit script (`scripts/d418-gate-1-3-verification.mjs`) will be tightened to introduce a `historical_fk_sink` classification bucket. Rows matching the five structural criteria above go in this bucket and are excluded from the `HIDDEN_ACTIVE_REFERENCE` count. With that change applied, Gate 1.3 re-run produces 0 `HIDDEN_ACTIVE_REFERENCE` rows and passes cleanly.

**This ADR does not modify the script** — that is a separate gate (call it Gate 1.3.3). Until Gate 1.3.3 lands, the Gate 1.3 audit will continue to flag these as `HIDDEN_ACTIVE_REFERENCE`; that's an accepted reporting noise, not a governance violation.

## Consequence — Gate 5 (physical-disposition DBCP)

Physical disposition (`DROP TABLE contract.business_object`) under a future Gate 5 will require addressing these FKs explicitly. Three feasible paths, to be decided at Gate 5 time:

- **A**. Drop the FK constraints (`bo_enrichment_log_object_id_fkey` + `bo_verification_log_object_id_fkey`) before DROP. Preserves audit data, loses referential integrity of historical records (FK column becomes a dangling UUID).
- **B**. Cascade-delete audit history. Destructive; violates the audit retention principle. Not recommended.
- **C**. Migrate audit data to denormalized form before DROP (snapshot `object_name`, `function_code`, etc. into the audit row, then drop the FK). Preserves both audit data and queryability without referential integrity to a no-longer-existing target.

**This ADR does not select among A/B/C** — it makes the dependency explicit for Gate 5 planning.

## Out of scope

- The Gate 1.3 audit script itself (Gate 1.3.3).
- Gate 5 physical-disposition DBCP path selection (Gate 5 decision at that time).
- BO-side D417/D418 work — Business Object is one of the 8 D417 §2 quarantined surfaces; its retirement is the broader D417/D418 program, not this ADR.
- Other `*_log` tables outside `operations.*` (none currently exist; the structural criteria above only apply to `operations.*`).

## References

- D418 Gate 1.3 FK-sweep output: `bc-core/scripts/audit-output/d418-gate-1-3-fk-sweep-2026-05-25T03-02-28-388Z.jsonl`
- D418 Gate 1.3 summary: `bc-core/scripts/audit-output/d418-gate-1-3-verification-2026-05-25T03-02-28-388Z.summary.md`
- D418 Gate 1.3.1 triage: `bc-core/scripts/audit-output/d418-gate-1-3-1-triage-2026-05-25T03-40-01-853Z.md`
- ADR DEC-a19428 (D418 — Pre-production Legacy Active-Runtime Retirement)
- ADR DEC-6c57e2 (D417 — Legacy Vocabulary Stack Quarantine)
- DDL: `bc-core/docker/redesign/02-platform-tables/07-operations.sql:71-121`
- Caller sites: `bc-core/src/registry/bo-enrichment.repository.ts`, `bc-core/src/registry/bo-verification.repository.ts`
