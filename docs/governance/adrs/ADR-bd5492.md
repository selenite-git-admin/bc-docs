---
uid: DEC-bd5492
title: "GDPR/DPDP/CCPA Nullification Object — Privacy Erasure for Immutable-Fact Architecture"
description: "Privacy erasure system for immutable-fact platform — sentinel-based PII nullification, evidence chain extension, PII registry, DSAR workflow, retention policies"
status: decided
subdomain: privacy
focus: erasure-architecture
date: 2026-04-05
decision_code: D285
project: bc-core
domain: platform
refs:
  - type: decision
    uid: DEC-8391fd
    label: "D270 Gemini audit that identified this gap"
  - type: task
    uid: TSK-8e7401
    label: "Original task from Gemini audit"
migrated_from: legacy v2 archive
---

# GDPR/DPDP/CCPA Nullification Object — Privacy Erasure for Immutable-Fact Architecture

## Context

BareCount's Foundation Principles create a fundamental conflict with privacy erasure laws:

- **Principle 2** (Facts are immutable) — finalized COs/MOs cannot change
- **Principle 7** (State advances forward only) — no reversals
- **Principle 8** (Absence means non-occurrence) — deleting creates false history

These conflict with **GDPR Article 17** (Right to Erasure), **India DPDP 2023 Section 12** (Right to Erasure), and **CCPA 1798.105** (Right to Delete).

Gemini architecture audit (D270/DEC-8391fd) identified this as a genuine gap — zero ADRs, zero code, zero schema existed for data erasure. BareCount holds PII across three layers:

1. **Platform DB** — operator PII (`createdByName`/`updatedByName` on ~25 tables, `platform_user`, `activity_log`, `ownerJson`)
2. **Tenant DB** — business data PII from source systems in `boundary.*` JSONB envelopes (being dropped per D210), `record.*` typed SQL tables, `evidence.*` hash-chained proof records, `operational.*` users/connections
3. **S3 WORM archives** — raw payloads archived per execution run with Object Lock

## Decision

### Core Concept: Nullification = Overwrite-in-Place + Evidence Extension

Erasure is NOT deletion. PII fields are overwritten with a deterministic sentinel:

```
[NULLIFIED:NUL-a7f3b2]
```

Where `NUL-a7f3b2` is the `request_code` from the nullification request. This resolves the philosophical conflict:

| Principle | Resolution |
|-----------|------------|
| P2: Facts are immutable | PII fields are privacy-protected metadata, not structural facts. The *fact* that "a contract was created on 2024-03-15" is preserved. *Who* created it is erasable. |
| P7: State advances forward | Nullification IS a forward state advance — from `active` to `nullified`. Not a reversal. |
| P8: Absence = non-occurrence | Sentinel explicitly means "was present, legally removed." True NULL still means "never existed." |
| P4: Evidence is recorded | Nullification itself becomes an evidence event. The chain is *extended*, not broken. |

### PII Sensitivity Tiers

| Tier | Name | Examples | Handling |
|------|------|----------|----------|
| T1 | DIRECT_IDENTIFIER | email, firstName, lastName, cognitoSub | Nullify on request |
| T2 | INDIRECT_IDENTIFIER | createdByName, updatedByName, ownerJson names | Nullify on request |
| T3 | BEHAVIORAL | ipAddress, userAgentText, actorId | Nullify on request |
| T4 | SENSITIVE_BUSINESS | authenticationJson, business data in record.* | Nullify on DSAR |
| T5 | STRUCTURAL | tenantId, contractId, timestamps, hashes | NEVER nullify |

### Masking Strategy

| Data Type | Strategy | Result |
|-----------|----------|--------|
| `text` column | Direct overwrite | `'[NULLIFIED:NUL-a7f3b2]'` |
| `jsonb` (ownerJson) | Deep field-level via `nullify_jsonb_paths()` | Role preserved, names masked |
| `jsonb` (authenticationJson) | Full replacement | `'{"status":"nullified","ref":"NUL-a7f3b2"}'` |
| Dynamic `record.*` | Column-level overwrite | Standard sentinel |
| S3 WORM archive | Companion `.nullified` marker object | Original untouched during lock period |
| Evidence `actor_name` | Overwrite + extend chain | New nullification evidence entry preserves original hash |

### Evidence Chain Preservation

1. Record original `content_hash` in `nullification_action.original_value_hash`
2. UPDATE `actor_name` to sentinel — stored hash now mismatches recomputed hash (expected and documented)
3. Append NEW evidence record: `evidenceType: 'nullification'`, documenting affected records and original hashes
4. `verifyChain()` recognizes nullification entries and treats documented mismatches as valid

### New Tables (operations schema)

1. **`pii_field_registry`** — catalogs every PII-bearing column across platform + tenant DBs with sensitivity tier and masking strategy
2. **`nullification_request`** — master DSAR/erasure request record with lifecycle (pending → approved → in_progress → completed)
3. **`nullification_action`** — per-field audit trail (what was masked, SHA-256 of original value, sentinel applied)
4. **`retention_policy`** — auto-nullification schedules per sensitivity tier
5. **`dsar_response`** — DSAR download tracking with time-limited tokens

### S3 WORM Handling

S3 Object Lock prevents deletion during retention period:
1. Place companion `.nullified` marker alongside the original
2. Marker contains nullification request reference and PII JSONB paths
3. All S3 read paths check for markers and strip PII before returning
4. After Object Lock expires, scheduled job replaces original with PII-stripped version

### Implementation Phases

- **Phase 1** (this session): ADR + DDL + Drizzle schemas
- **Phase 2**: NestJS NullificationModule + core services
- **Phase 3**: DSAR + tenant DB cross-database nullification
- **Phase 4**: S3 + retention engine
- **Phase 5**: API endpoints + bc-admin dashboard

## Options Considered

### Option A: Physical deletion (rejected)
DELETE rows containing PII. Rejected — breaks evidence hash chains, violates P2/P7/P8, destroys audit trail.

### Option B: Sentinel-based nullification (chosen)
Overwrite PII fields with traceable sentinel. Chosen — preserves structural integrity, maintains audit trail, complies with GDPR Recital 65 (pseudonymization when full deletion is technically infeasible).

### Option C: Encryption with key destruction (considered for future)
Encrypt PII at rest, destroy key on erasure request. More thorough but requires column-level encryption infrastructure. May be added as enhancement to Phase 2+.

## Consequences

### Positive
- Full GDPR/DPDP/CCPA compliance for both operator and business data PII
- Evidence chain integrity preserved through extension pattern
- PII registry enables automated discovery and audit
- Retention policies enable proactive compliance (not just reactive erasure)
- Sentinel distinguishes "legally removed" from "never existed" (P8 preserved)

### Negative
- Sentinel values visible in queries — frontend must handle display
- JSONB deep masking requires path-by-path registry (maintenance overhead)
- S3 WORM archives cannot be truly erased during lock period — documented exception for regulators

### Risks
- PII missed in JSONB columns → mitigated by periodic audit scan against pii_field_registry
- Dynamic `record.*` tables not discovered → mitigated by information_schema enumeration + contract field cross-reference
- Name matching false positives → mitigated by userId/cognitoSub as primary identifier
