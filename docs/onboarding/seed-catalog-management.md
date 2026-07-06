---
id: seed-catalog-management
order: 51
title: "Seed Catalog Management"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-authority-model, sources-and-the-catalog, source-registration, data-model-and-schema, infrastructure]
governing_sources:
  - Sources and the Catalog
  - Source Registration
governing_adrs: []
governing_sops:
  - legacy-v2/docs/sops/seed-catalog-sop.md (D269 Seed Catalog as the only entry point for tables and fields)
errata_referenced: []
v2_sources:
  - sops/seed-catalog-sop.md
diagrams: []
---

# Seed Catalog Management

## Scope

This chapter records the governed sequence by which curated reference data about source systems, their tables, and their fields enters the platform's MongoDB Seed Catalog (`bc_seed.seed_tables`). It names the document schema the catalog admits, the constraints the catalog enforces at the schema layer, the script-only authoring path for new systems, the enrichment path for existing tables, and the verification checks the catalog runs after every load. It records the boundary between Seed Catalog Management and Source Registration. It records the as-built drift between the procedure and the catalog contents captured by the readiness baseline.

This chapter does not redefine the Source Catalog itself (Sources and the Catalog) or the registration sequence that consumes the Seed Catalog (Source Registration). The Seed Catalog is the curated reference store that feeds Step 2 and Step 3 of registration; it is not a contract artifact and it is not consumed by any contract family directly.

**Governing source.** outline.md §4.6; Sources and the Catalog.

## What the Procedure Produces

A Seed Catalog load produces or enriches one or more documents in `bc_seed.seed_tables`. Each document represents one source table from one (system, version) pair and carries the table's identifying metadata plus a fields array.

The document schema is fixed:

| Field | Purpose |
|---|---|
| `table_name` | Clean source table name (no prefixes, no `ABAP__TABL__` decoration) |
| `display_name` | Human-readable label shown in registration UI |
| `system` | Lowercase slug identifying the source system (`s4hana`, `ecc`, `netsuite`) |
| `version` | Lowercase slug identifying the version (`on-premise-2023`, `cloud-2023`) |
| `display_system`, `display_version` | Human-readable labels used by the registration UI |
| `module` | Real, specific module code (`fi`, `co`, `mm`, `sd`); sentinel values such as `_unclassified`, `_default`, `_unknown` are rejected |
| `object_type` | One of: `table`, `view`, `sobject`, `endpoint`, `dataset` |
| `description` | Short prose describing the table's role in the source system |
| `field_count` | The count of entries in the `fields` array; the catalog does not reconcile this column itself |
| `fields[]` | Array of field objects with `name`, `type`, `length`, `description`, `isKey`, `position` |
| `source` | Provenance tag identifying where the metadata came from (`ddic`, `api-metadata`, `documentation`) |
| `confidence` | Enrichment-completeness band (`high` for full field metadata, `medium` for partial, `low` for name only) |
| `created_at` | ISO 8601 timestamp of document creation |

The collection carries four indexes that the registration surface and the search surface rely on: `{table_name: 1}`, `{system: 1, module: 1}`, `{system: 1, table_name: 1}`, and `{module: 1}`. These four cover the lookup-by-name, filter-by-system-and-module, system-scoped-lookup, and module-filter paths the registration UI uses.

**Governing source.** Sources and the Catalog; Source Registration.

## Prerequisites

The procedure assumes these are true at the moment a load script begins.

| Precondition | Why it is required |
|---|---|
| MongoDB `bc_seed` database accessible | The catalog lives in MongoDB; the load script writes there directly |
| The bc-core contract surface is reachable with the seed catalog service connected | The platform's read-side caches load on `bc-core` boot; a load that completes without re-connecting `bc-core` is invisible to the registration surface until restart |
| Source data extract is available | The script reads from a CSV, JSON, or DDIC export; the extract is the chapter's input |
| Module classification is known per table | The DTO rejects sentinel module values; classification is resolved before the script runs |
| Provenance is identified | The `source` and `confidence` columns are mandatory and carry meaningful values, not defaults |

The Seed Catalog is platform infrastructure. There is no UI for adding a system; the procedure is script-only. A tenant cannot author into the Seed Catalog; the catalog is platform-scoped and bound by the platform's own authoring discipline.

**Governing source.** Sources and the Catalog; Infrastructure.

## Step 1: Prepare the Source Extract

The script's input is a normalized table-and-fields extract from the system's authoritative source. The authoritative source depends on the system family:

| System family | Authoritative source | Extract format |
|---|---|---|
| SAP ECC, SAP S/4HANA | DDIC (SE11 / SE80 export, sapdatasheet scrape) | CSV or JSON per table |
| Salesforce | Describe API (`/services/data/vXX.0/sobjects/`) | JSON |
| Oracle, NetSuite | SuiteScript Schema Browser | JSON |
| REST APIs | OpenAPI / Swagger specification | JSON |
| Relational databases | `INFORMATION_SCHEMA.COLUMNS` | SQL export |

The extract carries the required columns (`table_name`, `module`, `object_type`) per table. It carries the optional columns (`display_name`, `description`, full `fields[]` array with name, type, length, description, isKey) where the source provides them.

**Governing source.** Source Registration.

## Step 2: Author the Load Script

A new system's load script lives in `bc-core/scripts/` and follows the established greenfield pattern. The script declares the constants the load is keyed against (system slug, version slug, display labels), reads the extract from disk, maps each row into the seed document schema, deduplicates against the existing collection by `table_name`, and supports a `--dry-run` flag.

The script enforces these rules:

| Rule | Form |
|---|---|
| Sentinel modules are rejected | Any input row whose module column resolves to `_unclassified`, `_default`, `_unknown`, `unclassified`, `default`, or `unknown` is rejected at the input-mapping step, not at insert time |
| Confidence is set deterministically | A document with full field metadata is `confidence: 'high'`; partial metadata is `medium`; name-only is `low`. The script does not default to `high` |
| Provenance is tagged | The `source` field is set to identify where the metadata came from; defaults are not used |
| Deduplication is by `(table_name, system)` | An existing document with the same key is enriched (Step 5) rather than duplicated |
| Dry run is mandatory | The first execution against the live catalog uses `--dry-run`; the dry run reports the planned insert count, the module breakdown, and any sentinel rejections |

A script that violates any of these rules is not the catalog's interface; it is a script that does not honor the catalog's discipline, and its output is not admissible until corrected.

**Governing source.** Sources and the Catalog.

## Step 3: Run the Dry Run

The dry run is mandatory before any live load. It produces a report the actor reviews:

| Report item | What is verified |
|---|---|
| Table count | Matches the extract's row count (no silent drops) |
| Module breakdown | All listed modules are real codes; no sentinel values |
| Name hygiene | No prefixed or decorated names (no `ABAP__`, no length-truncated names) |
| Field coverage | The percentage of tables with non-empty `fields[]` matches the extract's field-coverage state |

A dry run that surfaces unexpected counts, sentinel modules, or name-decoration is not promoted to a live run. The discrepancy is investigated and the script revised.

**Governing source.** Sources and the Catalog.

## Step 4: Run Live and Verify

The live run uses the same script without `--dry-run`. After the script completes, the actor verifies the catalog's state via the `bc-core` read surface:

| Verification | Surface |
|---|---|
| Document count is what the dry run predicted | `GET /api/seed-catalog/stats` |
| The new system appears with its module list | `GET /api/seed-catalog/modules?system={system-slug}` |
| Sample table renders fields | `GET /api/seed-catalog/tables/{known-table-name}` |

A `bc-core` restart connects the seed catalog service to the new document set. The service emits a connection log line at boot reporting the document count it found; the actor confirms the count matches the post-load count.

**Governing source.** Sources and the Catalog; API Surface.

## Step 5: Enrich Existing Documents

Field metadata that becomes available after a system is loaded is admitted by an enrichment script. The script reads the new field data and applies a per-document update:

```
db.seed_tables.updateOne(
  { table_name, system },
  { $set: { fields, field_count, confidence: 'high' } }
)
```

The enrichment script does not replace the document. It updates only the columns the enrichment carries. It supports a `--dry-run` flag that reports which documents will be enriched and the existing vs. proposed field counts. The provenance of the enrichment is not recorded as an additional `source` value at the document level; the script records it in its run log, and the catalog's `confidence` upgrade reflects that the enrichment landed.

**Governing source.** Sources and the Catalog.

## Quality Gates

The Seed Catalog enforces five gates. The gates are stated as the rules the script and the read surface honor.

| Gate | Where enforced | What it checks |
|---|---|---|
| Sentinel modules rejected | Load script input-mapping step | Any row whose module is a sentinel value is rejected before insert |
| Naming hygiene | Load script input-mapping step | Table names are clean (no prefixes, no decoration); the catalog does not store decorated names |
| Provenance present | Load script input-mapping step | Every document carries a `source` and a `confidence` value; defaults are not used |
| Deduplication | Load script input-mapping step | The script checks `table_name` against the existing collection before insert |
| No silent backfill | Read surface | The read surface does not synthesize fields from heuristics; a document with empty `fields[]` reports an empty array, and the registration UI surfaces this honestly |

A document that lands in the catalog without passing these gates (e.g., via a direct `db.seed_tables.insertOne` against MongoDB) is in the catalog but is not the catalog's authoritative content. The audit substrate does not see the direct write.

**Governing source.** Sources and the Catalog; Audit and Activity Logging.

## Boundary with Source Registration

The Seed Catalog is the only entry point for Source Tables and Source Fields. The registration sequence consumes the catalog at Step 2 (Add Source Tables) and Step 3 (Add Source Fields). The two boundaries are distinct:

| Concern | Owned by | Persistent store |
|---|---|---|
| Curated reference of what tables and fields the platform knows about | Seed Catalog Management (this chapter) | `bc_seed.seed_tables` (MongoDB) |
| The catalog row that represents a tenant-relevant table or field on the platform | Source Registration | `source.source_object`, `source.source_field` (PostgreSQL) |

A field that exists in `bc_seed.seed_tables` is admissible to a tenant's catalog via Source Registration; it is not automatically present in any tenant's catalog by virtue of being in the Seed Catalog. A field that is not in the Seed Catalog is not admissible at registration; the procedure is to add the field to the Seed Catalog (this chapter, Step 5) first.

**Governing source.** Source Registration; Sources and the Catalog.

## Drift Inventory

| Drift item | Form |
|---|---|
| `bc-core` restart is manual | After a load, the registration surface does not see the new content until `bc-core` reconnects to MongoDB. The readiness-baseline procedure relies on the actor running a manual restart. The catalog does not emit a change notification that triggers reconnection automatically. |
| Field-coverage figures vary by system | The chapter does not assert a coverage percentage. The catalog's coverage reflects what the authoritative source provided at load time; SAP ECC and S/4HANA on-premise have richer field metadata than CDS-only S/4HANA Cloud or REST endpoints, and the read surface reports the actual coverage per system. |
| Enrichment provenance not separately stored | When an enrichment script upgrades a document's `confidence` and replaces the `fields[]` array, the document records the new state but does not preserve the prior provenance as a versioned trail. The script's run log is the audit trail; the catalog itself does not version enrichments. |
| Authoring is script-only | There is no UI for adding a system to the Seed Catalog. The script-only discipline is intentional (the catalog is curated reference data, not user-authored content), but it does mean the Seed Catalog has no governed-via-API entry path; the audit substrate does not capture script invocations the same way it captures API mutations. |
| Re-snapshot policy is informal | A material enrichment of the catalog is followed by a re-snapshot of the bc-core golden state per the project's snapshot discipline. The re-snapshot is not enforced by the catalog itself; it is a project convention recorded in the Operations chapters as they are drafted. |

**Governing source.** Sources and the Catalog; Audit and Activity Logging.

## Governing Decisions

The Seed Catalog discipline (no manual data entry, no in-UI table or field authoring at registration; D269 in the v2 SOP shorthand) is operationalized by this chapter and by `legacy-v2/docs/sops/seed-catalog-sop.md`. No standalone ADR file formalizes the discipline; the SOP plus this chapter are the governing record. The Seed Catalog's storage substrate (MongoDB) is governed by Infrastructure; the document schema is governed by this chapter; the consumption sequence is governed by Source Registration.

**Governing source.** `legacy-v2/docs/sops/seed-catalog-sop.md`; Source Registration.

## References

- Sources and the Catalog
- Source Registration
- Data Model and Schema
- Infrastructure
- API Surface
- Audit and Activity Logging
- legacy-v2/docs/sops/seed-catalog-sop.md (predecessor SOP; D269 Seed Catalog as the only entry point)
- outline.md §4.6: Onboarding

