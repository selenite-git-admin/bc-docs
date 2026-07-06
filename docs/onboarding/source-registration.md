---
id: source-registration
order: 50
title: "Source Registration"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, the-authority-model, sources-and-the-catalog, business-vocabulary, ai-gates, ai-trust-and-verification, api-surface, data-model-and-schema]
governing_sources:
  - Sources and the Catalog
  - AI Gates
  - AI Trust and Verification
governing_adrs:
  - DEC-1918d0 (D162 database rules)
  - DEC-69f09e (D148 ISO 11179 naming)
governing_sops:
  - legacy-v2/docs/sops/source-registration-sop.md
errata_referenced: []
v2_sources:
  - sops/source-registration-sop.md
  - system/platform/P01-source-catalog/
diagrams: []
---

# Source Registration

## Scope

This chapter records the governed sequence by which a source system, its tables, and its fields are admitted to the Source Catalog. It names the prerequisites the procedure assumes, the artifacts the procedure produces in the catalog, the quality gate each artifact passes, the AI verification step each artifact passes, and the persistence rules the catalog enforces. It states the boundary between source registration and the contract artifacts that consume the catalog (Source Contract, Admission Contract, Observation Contract). It records the as-built drift between the procedure and the catalog's current state.

This chapter does not redefine the catalog inventory or the catalog hierarchy (Sources and the Catalog), the AI gate envelope or the maker-checker-gate verdict shape (AI Gates and AI Trust and Verification), the JWT-guarded API surface that mutates the catalog (API Surface), or the DDL that backs the catalog tables (Data Model and Schema).

**Governing source.** outline.md §4.6; Sources and the Catalog.

## What the Procedure Produces

A complete source registration produces seven catalog artifacts plus an AI verification record per artifact. Each artifact is platform-scoped and immutable to tenant code; a tenant may bind a Connection to it but cannot mutate it.

| Artifact | Catalog table | Created by | Consumed by |
|---|---|---|---|
| Source Provider | `source.source_provider` | Step 1 | Source System |
| Source System | `source.source_system` | Step 1 | Source Version, Connectors and Readers |
| Source Version | `source.source_version` | Step 1 | Source Module |
| Source Module | `source.source_module` | Step 1 | Source Table |
| Source Table | `source.source_object` | Step 2 | Source Field, Source Contract, Admission Contract |
| Source Field | `source.source_field` | Step 3 | Observation Contract field mappings |
| Catalog Verification record | `operations.catalog_verification_log` | Steps 1-3 | Catalog Verification audit trail |

Artifact naming follows ISO 11179 per DEC-69f09e. Module codes are real, specific module identifiers (e.g., `fi`, `co`, `mm`) and never sentinel values such as `_unclassified`, `_default`, or `_unknown`. The DTO at the API surface rejects sentinel values before the catalog is touched.

**Governing source.** Sources and the Catalog; DEC-69f09e.

## Prerequisites

The procedure assumes these are true at the moment Step 1 begins. A precondition that fails is not bypassed; the failed precondition is fixed before the procedure resumes.

| Precondition | Why it is required |
|---|---|
| Cognito authenticated session for the actor | Every catalog mutation is `@PlatformOnly()` JWT-guarded at the API surface |
| Provider, system, version, and module identifiers are known | The DTO rejects sentinel module codes; identifier resolution is upstream of the catalog |
| Seed Catalog populated for the system being registered | Steps 2-3 read tables and fields from the Seed Catalog only; no manual table or field entry is admitted (D269 in the v2 SOP shorthand) |
| AI verification surface reachable | Each catalog artifact passes maker-checker-gate before its catalog row is created with `verificationStatus: verified` |

The actor's role is not part of the catalog's governance state. Catalog rows record the actor identity and the AI verification verdict; the actor's permissions are evaluated at the API surface, not in the catalog data.

**Governing source.** Sources and the Catalog; AI Gates; API Surface.

## Step 1: Register Provider, System, Version, and Modules

A six-field DTO declares the identity of the source. The DTO carries category, system type, provider, system, version, and module identifiers. The exact DTO field names remain owned by the source-catalog API surface. The DTO is authored once and submitted to the AI verification endpoint before the catalog is touched.

The AI verification step calls `POST /api/ai/suggest/source-verify` with the DTO. The maker-checker-gate verdict is the gate at which the catalog admits the registration:

| Verdict | Catalog state assigned at creation |
|---|---|
| `green` | Provider, System, Version, and Modules are created with `catalogStatus: approved` and `verificationStatus: verified`. Module display names are taken from the AI suggestion. |
| `amber` | The same artifacts are created with `catalogStatus: registered` and `verificationStatus: unverified`. The AI corrections are recorded for human review; the actor confirms or revises before promoting status. |
| `red` | No catalog rows are created. The actor revises the DTO and re-runs verification. |

A catalog row's `catalogStatus` and `verificationStatus` are set at creation by the verification verdict. The platform does not admit a `PATCH` that promotes `registered` to `approved` or `unverified` to `verified` after the fact; the verdict that produced the row is the verdict the row carries. Re-verification produces a new row, not a status change on the original.

If the verification surface is unreachable, the actor records the outage and creates the artifacts with `verificationStatus: unverified`. The platform does not synthesize a green verdict to bypass the gate. The unverified artifact is a known gap until verification can run.

**Governing source.** AI Gates; AI Trust and Verification; Sources and the Catalog.

## Step 2: Add Source Tables from the Seed Catalog

A Source Module's tables are admitted from the Seed Catalog only. The actor selects a module and an `object_type` (table, view, sobject, endpoint, dataset), searches the Seed Catalog by table name or description, and selects one entry. The selected entry's metadata is the candidate Source Table.

The candidate passes `POST /api/ai/suggest/table-verify` with the Seed Catalog entry plus a sample of fields. The verdict assigns the catalog state at row creation (same matrix as Step 1: green to approved+verified, amber to registered+unverified, red blocks the create). On admission, `source.source_object` is created via `POST /source-catalog/objects`.

The procedure does not admit hand-typed table names. Tables that do not exist in the Seed Catalog are not added to the catalog directly; the missing entry is added to the Seed Catalog first (Seed Catalog Management) and then re-attempted here.

**Governing source.** Sources and the Catalog; AI Gates; Seed Catalog Management.

## Step 3: Add Source Fields from the Seed Catalog

A Source Table's fields are admitted in bulk from the Seed Catalog. The catalog UI fetches the Seed Catalog entry's fields, marks already-registered fields as registered with a non-actionable badge, and presents the remaining fields for selection. The actor selects individually or selects all unregistered.

For each selected field, `POST /api/source-catalog/fields` creates one catalog field row. After the bulk selection completes, the catalog updates the Source Table row with `seedFieldCount` (the count of fields admitted) and `seedImportedAt` (the ISO 8601 timestamp of the bulk operation). These two columns are the catalog's record that a Seed Catalog import occurred against the Source Table.

A field that the Seed Catalog does not declare is not admitted. The Seed Catalog is the only entry path (D269 in the v2 SOP shorthand). A Z-field (an extension field a tenant uses but the Seed Catalog does not declare) is not admitted at registration; the Z-field is admitted at runtime by the Reader and routed through the tenant Z-field admission path defined by Tenancy and Binding. Z-field admission is not a catalog operation.

**Governing source.** Sources and the Catalog; Tenancy and Binding.

## Quality Gates

The catalog enforces three gates at the API surface. The gates are stated as the rule the surface enforces, not as scripts a caller may bypass.

| Gate | Where enforced | What it checks |
|---|---|---|
| AI verification is mandatory at create | DTO at `POST /source-catalog/{providers,systems,versions,modules,objects,fields}` | The DTO carries the verification verdict; missing verdict creates the row with `verificationStatus: unverified` and the catalog flags the artifact for review |
| Status promotion is forbidden at update | `PATCH /source-catalog/*` | An attempt to set `catalogStatus = 'approved'` from `'registered'` or `verificationStatus = 'verified'` from `'unverified'` is rejected |
| Manual data entry is forbidden | `POST /source-catalog/objects`, `POST /source-catalog/fields` | A `source_object` row whose name does not match any Seed Catalog entry, or a `source_field` row whose name does not match any Seed Catalog field for the parent object, is rejected |

A caller that bypasses the surface and writes directly to PostgreSQL is operating outside the platform's governance. The catalog's gates live on the surface; the database itself does not run them. Direct DB writes are a violation of the catalog's authority model and produce rows the catalog reports as ungoverned in catalog audit.

**Governing source.** Sources and the Catalog; API Surface.

## Catalog Verification Record

Each create operation appends one row to `operations.catalog_verification_log` with the artifact identifier, the AI verdict, the model identifiers used by the maker and the checker, the timestamp, and the actor identity. The log is append-only; it is not mutated to change a prior verdict.

The Catalog Verification record is the catalog's evidence that a given artifact passed (or did not pass) AI verification at the moment of creation. It is the source consulted by the catalog audit substrate when the platform questions whether an artifact's `verificationStatus` is supported by a real verification run.

**Governing source.** Sources and the Catalog; Audit and Activity Logging.

## Boundary with Other Onboarding Chapters

Source registration is the first link in the contract chain. The catalog rows it produces are read by every contract family, but the catalog does not author any contract family's body.

| Chapter | What it consumes from the catalog | What it does not consume |
|---|---|---|
| Source and Admission Contract Creation | `source.source_object`, `source.source_field`, `source.source_version` (for `source_object_id`, field declarations, key markers) | The catalog's AI verification verdicts; SC and AC author their own verdicts |
| Observation Contract Creation | `source.source_object` (for `source_references[]`), `source.source_field` (for `field_mappings[].source_field`) | The catalog's `seedFieldCount`; OC reads SC's declared fields |
| Reader Creation | `source.source_system` (via Connector), `source.source_version` (for Reader Flavor) | The catalog's identity beyond the system reference; Reader binds via Connection at runtime |
| Tenancy and Binding | The catalog identity via the tenant `runtime.connection` row | The catalog's `catalogStatus`; Connection cites the catalog row but does not mutate it |

A chapter that asserts a catalog mutation is asserting a Source Registration step. A chapter that asserts contract creation is asserting one of the contract-creation chapters. The two are not interchangeable.

**Governing source.** Source and Admission Contract Creation; Observation Contract Creation; Reader Creation; Tenancy and Binding.

## Drift Inventory

The procedure as written above is the canonical sequence. The catalog's readiness-baseline state contains drift items that are recorded here so the chapter does not present aspirational behavior as realized.

| Drift item | Form |
|---|---|
| Catalog AI verification fail-open | When `bc-ai` is unreachable, the catalog admits artifacts with `verificationStatus: unverified` rather than blocking the create. The unverified artifact remains in the catalog until a re-verification run upgrades it. The catalog does not re-run verification on a schedule in the readiness baseline; the upgrade is actor-triggered. |
| Status promotion via direct SQL | The `PATCH` surface forbids status promotion. Direct SQL `UPDATE` against the catalog tables is not blocked by the database itself. The audit substrate records the row mutation through DevHub if the SQL was issued by a governed actor; an unaudited SQL path leaves no record on the change ledger. |
| Z-field at registration | The readiness-baseline procedure does not admit Z-fields at registration; Z-field admission is a runtime concern owned by the Reader and the tenant binding. The catalog's `seedFieldCount` therefore does not include Z-fields, and a Source Table whose tenant binding admits many Z-fields shows a `seedFieldCount` that under-counts the runtime field set. |
| Bulk system-scale registration | The procedure documents single-system sequence. Bulk system-scale registration (e.g., a scripted load of an entire ERP catalog) runs the same DTOs and surface calls in a loop in the readiness baseline; the rate-limit on the AI verification surface gates throughput. The catalog admits the rows at the rate the AI surface returns verdicts. |
| `_unclassified` rows in legacy data | The DTO rejects `_unclassified` and similar sentinel module codes in the readiness baseline, but the database contains a small set of legacy rows from prior migrations that carry sentinel-like values. These rows are flagged for cleanup and are not admitted into new tenant bindings until they are re-classified. |

Each drift item is a known gap, not a hidden one. The chapter is the catalog's record of where the procedure and the realization meet.

**Governing source.** Sources and the Catalog; Tenancy and Binding; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-1918d0 | Establishes the database normalization rules the catalog tables follow (no JSONB for queryable data, FK constraints mandatory, soft deletes via `archived_at`); the catalog tables are the chapter's concrete instance of these rules |
| DEC-69f09e | Establishes ISO 11179 snake_case naming for the catalog identifiers (`{entity}_id` for primary keys, `{noun}_code` for codes, `{verb}_at` for timestamps); the catalog rows the chapter produces honor this naming |

Additional decisions that govern the catalog's hierarchy and verification surface (the catalog inventory and the AI maker-checker-gate envelope) are owned by Sources and the Catalog and AI Gates respectively; this chapter's body cites them but does not re-record them in this table per pattern 77.

**Governing source.** Decisions: ADR Registry.

## References

- Sources and the Catalog
- Business Vocabulary
- AI Gates
- AI Trust and Verification
- Seed Catalog Management
- Source and Admission Contract Creation
- Observation Contract Creation
- Reader Creation
- Tenancy and Binding
- API Surface
- Data Model and Schema
- Audit and Activity Logging
- DEC-1918d0: Deployment and database architecture
- DEC-69f09e: ISO 11179 naming convention
- legacy-v2/docs/sops/source-registration-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding

