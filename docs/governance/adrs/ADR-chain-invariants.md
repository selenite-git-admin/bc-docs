---
uid: DEC-pending
title: "Contract Chain Invariants — Machine-Checkable Integrity Rules"
description: "Defines 14 invariants across 5 contract chain layers (Source, BF/BO, OC, CC, MC) plus 1 cross-layer invariant. Each invariant is a SQL query that returns violating rows."
status: proposed
date: 2026-04-11
project: bc-core
domain: contracts
refs:
  - type: decision
    uid: DEC-d72560
    label: "D301: Canonical Field as 3rd Contract Primitive"
  - type: decision
    uid: DEC-9a5dc0
    label: "D302: CF Boundary — Reporting Standards Promote to CFs"
  - type: decision
    uid: DEC-ebf0b4
    label: "D268: Session Discipline & Data Integrity"
migrated_from: legacy v2 archive
devhub_registration: doc-registry indexed; decision-registry row absent. UID `DEC-pending` is a placeholder — a real UID has never been allocated. Classified UID_PENDING per Decision-Registration Integrity Audit 2026-06-22 §4.2. To formalize, call `devhub_decision_record` with a fresh description (the allocator will assign a UID) and treat this file as superseded by the new ADR; preservation chosen over forced allocation for now.
---

# Contract Chain Invariants — Machine-Checkable Integrity Rules

> **Decision-registration integrity (2026-06-22).** Classified `UID_PENDING` in the [integrity audit](../../evidence/audits/implementation/devhub-decision-registration-integrity-audit-2026-06-22.md) §4.2 and preserved in the [repair closeout](../../evidence/closeouts/implementation/devhub-decision-registration-integrity-repair-closeout-2026-06-22.md). UID `DEC-pending` is a placeholder; a real allocator UID has not been assigned. Inbound cross-references to this file are by filename (`ADR-chain-invariants.md`), not by UID. Operator can promote to a real UID by calling `devhub_decision_record` and marking this file as superseded by the result. Content below is preserved verbatim per Foundation Invariant III.

## Context

The contract chain (MC → CF → cc_field_mapping → BF → OC → source_field) has implicit rules that, when violated, produce phantom coverage or silent data corruption. The D302 audit (Apr 11 2026) proved this: a single predicate error in integrity.service.ts inflated chain coverage from 41.7% to 99.6%.

We need machine-checkable invariants — SQL queries that return violating rows — so that:
1. Integrity is verified by query, not by code logic
2. Regressions are caught automatically
3. Session discipline (D268) has concrete checks to audit against

### Current State (Audited Apr 11 2026)

| Metric | Value |
|---|---|
| Full chain MCs | 344 / 825 (41.7%) |
| Partial chain MCs | 478 |
| Broken chain MCs | 3 |
| MC CF references with OC path | 563 / 1,282 (43.9%) |
| MC CF references with D302 bypass | 64 |
| MC CF references partial (no OC) | 655 |

## Decision

### Invariant Definitions

Each invariant has a severity: **block** (must fix before deploy) or **warn** (track, don't block).

#### BF/BO Layer

| ID | Rule | Severity |
|---|---|---|
| INV-B1 | Every BF name must be unique | block |
| INV-B2 | Every BF alias must be unique per (field_id, system_type_code) | block |

#### OC Layer

| ID | Rule | Severity |
|---|---|---|
| INV-O1 | No OC version may have duplicate business_field_code entries | block |
| INV-O2 | Every OC field_mapping business_field_code must be a registered BF name | block |
| INV-O3 | Every OC field_mapping source_field must be non-empty | warn |

#### CC Layer

| ID | Rule | Severity |
|---|---|---|
| INV-C1 | Every cc_field_mapping must reference a valid canonical_field_id (FK integrity) | block |
| INV-C2 | Every cc_field_mapping must reference a valid business_field_id (FK integrity) | block |
| INV-C3 | No circular resolution: BF name must not also be a CF name on the same CC | block |
| INV-C4 | cc_field_mapping (canonical_contract_id, canonical_field_id) must be unique | block |

#### MC Layer

| ID | Rule | Severity |
|---|---|---|
| INV-M1 | Every MC fields_used CF name must exist in canonical_field table | block |
| INV-M2 | Every MC co_binding canonical_contract must exist in canonical_contract table | warn |

#### Cross-Layer

| ID | Rule | Severity |
|---|---|---|
| INV-X1 | Every MC CF reference must have a cc_field_mapping on the bound CC | warn |
| INV-X2 | Every cc_field_mapping BF must have OC field_mapping coverage | warn |
| INV-X3 | CC schema (contract_json resolved_schema) must not contain fields from other CCs (no cross-contamination) | block |

### Implementation

Invariant checker lives in `bc-qa/audits/checks/check-chain-invariants.sh`. It connects to PostgreSQL via `docker exec` and runs each invariant as a SQL query. Output: pass/fail per invariant + violating entity count.

Integrated into `bc-qa/audits/audit-repo.sh` for bc-core audits and available standalone via `devhub_qa_audit`.

### Severity Rules

- **block**: If ANY violating row exists, the audit fails. Must fix before deployment.
- **warn**: Violations are reported but don't block. Tracked as quality debt.

Block invariants are structural integrity (FK violations, uniqueness, circular refs). Warn invariants are coverage completeness (OC gaps, missing mappings) — these improve over time.

## Consequences

### Positive
- Chain integrity verified by SQL, not by code logic — immune to bypass bugs
- Regressions caught automatically in audit pipeline
- Session discipline (D268) has concrete invariants to verify against
- New sessions can run invariant check before and after changes

### Negative
- Adds ~30s to bc-core audit run time (14 SQL queries)
- Warn-level invariants will report known gaps (655 partial CFs) — noise until resolved

### Risks
- **RSK-1**: Invariant queries may be slow on large datasets. Mitigate: indexes on FK columns (already exist).
- **RSK-2**: New contract types may need new invariants. Mitigate: extensible script structure (one function per invariant).
