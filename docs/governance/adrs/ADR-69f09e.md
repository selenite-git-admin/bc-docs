---
uid: DEC-69f09e
title: "ISO 11179 Technical Naming Standard — all internal technical names"
description: "All BareCount technical names follow ISO 11179-5 naming grammar with mandatory representation terms (_id, _code, _text, _ts, etc.) and per-surface case conventions"
status: implemented
subdomain: naming-standards
focus: iso-11179-technical-naming
date: 2026-03-15
project: platform
domain: governance
refs:
  - type: document
    path: "foundation/governance/technical-naming-standard.md"
    label: "Authoritative naming standard document"
  - type: document
    path: "foundation/governance/d078-rename-manifest.md"
    label: "D078 rename manifest for retrofit"
  - type: decision
    uid: DEC-5017fe
    label: "D139: Standard Field Registry — extends naming to observation vocabulary"
  - type: decision
    uid: DEC-ddbce8
    label: "D135: Unified Business Domain Taxonomy"
authority: authoritative
migrated_from: legacy v2 archive
---

# ISO 11179 Technical Naming Standard

## Context

BareCount enforces contracts on customer data — admission contracts, canonical schemas, metric contracts. The platform's own technical surface (database columns, API fields, route segments) was using ad-hoc naming with no consistency across repos. Field names like `status`, `source`, `created`, `active` appeared everywhere with ambiguous semantics.

The foundation language system already governs business vocabulary (forbidden terms like "pipeline", required terms like "observe"). But the technical surface — database columns, JSON fields, API routes — had no governance layer.

We are in dev/wiring phase, pre-launch. Post-launch, renaming becomes exponentially harder due to API versioning and client compatibility. This is the last practical window for a complete retrofit.

## Decision

All BareCount internal technical names follow a naming standard derived from **ISO 11179-5** (Naming and Identification Principles).

### Naming Grammar

Every technical name: `[Qualifier] ObjectClass · [Qualifier] Property · RepresentationTerm`

### Mandatory Representation Terms

No naked field names. Every column/field must end with a representation term:

| Term | Semantics | Example |
|------|-----------|---------|
| `_id` | Surrogate identifier | `contract_id` |
| `_uid` | Human-readable short UID | `session_uid` |
| `_code` | Business code | `currency_code` |
| `_name` | Human label | `reader_name` |
| `_text` | Free-form content | `description_text` |
| `_ts` | Timestamp (ISO 8601) | `admitted_ts` |
| `_date` | Calendar date | `fiscal_date` |
| `_count` | Whole number | `record_count` |
| `_amount` | Monetary/decimal | `invoice_amount` |
| `_rate` | Ratio/percentage | `exchange_rate` |
| `_flag` | Boolean | `active_flag` |
| `_status` | Lifecycle state | `task_status` |
| `_json` | Serialized JSON | `config_json` |
| `_seq` | Sequence/ordinal | `version_seq` |
| `_ref` | Foreign reference | `parent_ref` |

(Full list: 21 terms covering all data types)

### Case Conventions

| Surface | Convention | Example |
|---------|-----------|---------|
| DB columns | `snake_case` | `contract_uid` |
| API routes | `kebab-case` | `/admission-contracts` |
| JSON fields | `snake_case` | `source_type` |
| JS/TS variables | `camelCase` | `contractUid` |
| Types/Classes | `PascalCase` | `AdmissionContract` |
| Env vars | `SCREAMING_SNAKE` | `COGNITO_USER_POOL_ID` |
| File names | `kebab-case` | `admission-contract.service.ts` |

### Scope

**In:** All code, schemas, APIs, databases across all BareCount repos.
**Out:** External system identifiers (SAP BKPF, Salesforce Account__c), UI display labels, foundation business vocabulary.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **ISO 11179-5 naming standard (chosen)** | Proven grammar, used by national metadata registries. Extends existing governance. Removes ambiguity. | Requires full retrofit of existing code. |
| Forward-only convention (new code only) | No retrofit cost. | Permanent inconsistency between old and new code. Grows worse over time. |
| No naming standard | Zero effort. | Ad-hoc naming contradicts platform's contract-discipline thesis. |

## Consequences

1. **Full retrofit required** — all existing columns, fields, routes must be renamed. Rename order: DB → API → frontend (bottom-up).
2. **Every CLAUDE.md references the standard** — enforcement happens per-session.
3. **Developer cognitive load reduced** — `_ts` always means timestamp, `_flag` always means boolean.
4. **Authoritative document maintained** at `foundation/governance/technical-naming-standard.md`.
5. **D078 rename manifest** tracks the actual field-by-field rename mapping.
