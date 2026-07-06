---
id: metric-seed-catalog-management
order: 52
title: "Metric Seed Catalog Management"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-authority-model, metric-catalog, metric-evaluation, business-vocabulary, data-model-and-schema, infrastructure]
governing_sources:
  - Metric Catalog
  - Business Vocabulary
governing_adrs:
  - DEC-ecec75 (D068 one metric per KPI; metric architecture)
governing_sops:
  - legacy-v2/docs/sops/metric-seed-catalog-sop.md
errata_referenced: []
v2_sources:
  - sops/metric-seed-catalog-sop.md
diagrams: []
---

# Metric Seed Catalog Management

## Scope

This chapter records the governed sequence by which curated metric reference data enters the platform's MongoDB Metric Seed Catalog (`bc_seed.seed_metrics`). It names the document schema the catalog admits, the constraints the catalog enforces, the script-only authoring path for new metrics, the enrichment path for existing metrics, the dedup-aware merge path for external metric collections, and the verification checks the catalog runs after every load. It records the boundary between the Metric Seed Catalog and Metric Registration. It records the as-built drift between the procedure and the catalog's current contents.

This chapter does not redefine the metric catalog runtime tables (`metric.metric_definition`, `metric.metric_definition_knowledge`) governed by Metric Catalog, the metric evaluation runtime governed by Metric Evaluation, or the registration sequence that promotes seed entries into the platform governed by Metric Registration.

The Metric Seed Catalog is a dumb store of curated metric reference data. All quality gates (classification, dedup, validation) live at the Metric Registration boundary, not in the catalog itself.

**Governing source.** outline.md §4.6; Metric Catalog.

## What the Procedure Produces

A Metric Seed Catalog load produces or enriches one or more documents in `bc_seed.seed_metrics`. Each document represents one metric definition keyed by `metric_name` (snake_case, globally unique within the collection) and carries the metric's identifying metadata plus optional thresholds, formula reference, and binding hints.

The document schema is fixed:

| Field | Purpose |
|---|---|
| `metric_name` | snake_case identifier, unique across the collection (slugified from `display_name` if not provided) |
| `display_name` | Human-readable label |
| `description` | Required prose; the dedup gate at registration relies on this being substantive |
| `function_code` | Lowercase slug; sentinel values (`_unclassified`, `_default`, `_unknown`) are rejected |
| `subfunction_code` | Optional but recommended lowercase slug |
| `industry_category_code`, `industry_code` | `universal` for cross-industry; sector slugs otherwise |
| `tier_code` | `standard`, `operational`, or `predictive` |
| `direction` | `lower-is-better`, `higher-is-better`, or `target-is-optimal` |
| `bsc_perspective` | Balanced Scorecard lens or `null` |
| `reference_formula` | Prose formula reference (not the parseable runtime formula) |
| `measurement_approach` | Prose describing how the metric is computed in practice |
| `thresholds` | Optional four-band structure (excellent / good / warning / critical) with `min`/`max` |
| `co_bindings[]` | Optional canonical contract slugs the metric depends on |
| `related_metrics[]` | Optional sibling metric slugs |
| `search_tags[]` | Optional synonyms and abbreviations for discoverability |
| `sources[]` | Provenance tags (`apqc`, `cfo-pack`, `internet`, `industry-reference`, `manual`) |
| `confidence` | `high`, `medium`, `low`, or `deprecated` |
| `created_at`, `updated_at` | ISO 8601 timestamps |

The collection carries five indexes the registration surface and the search surface rely on: `{metric_name: 1}` (unique), `{function_code: 1, subfunction_code: 1}`, `{industry_category_code: 1, industry_code: 1}`, `{sources: 1}`, and `{confidence: 1}`.

**Governing source.** Metric Catalog; Business Vocabulary.

## Prerequisites

| Precondition | Why it is required |
|---|---|
| MongoDB `bc_seed` database accessible | The catalog lives in MongoDB; the load script writes there directly |
| The bc-core contract surface is reachable with the metric seed surface connected | The platform's read-side surface is on `bc-core`; visibility requires reconnection |
| Source data extract is available | A CSV, JSON, or SQLite export from the authoritative external source |
| Function classification is known per metric | The DTO rejects sentinel function codes; classification is resolved before the script runs |
| Provenance is identified | The `sources[]` array carries the originating tag, not a default |

The Metric Seed Catalog has no UI for adding a metric. The procedure is script-only.

**Governing source.** Metric Catalog; Infrastructure.

## Step 1: Prepare the Source Extract

The script's input depends on the external source:

| Source family | Description | Format |
|---|---|---|
| APQC PCF | APQC's KPI decomposition reference (the PCF) | CSV or Excel |
| CXO Packs | Curated KPIs per executive function (CFO, COO, etc.) | TypeScript or JSON |
| Internet reference | Enterprise and industry KPI databases | CSV or JSON |
| Industry standards | Sector-specific metric frameworks | CSV or JSON |
| Manual | Hand-curated metrics for custom domains | JSON |

Per metric, the extract carries `metric_name` or `display_name`, `description`, and `function_code` as required columns, and any of the optional columns where the source provides them.

**Governing source.** Metric Catalog.

## Step 2: Author the Load Script

A new external source's load script lives in `bc-core/scripts/` and follows the established pattern. The script reads the extract, maps each row into the seed document schema, deduplicates against the existing collection by `metric_name`, and supports a `--dry-run` flag.

The script enforces these rules:

| Rule | Form |
|---|---|
| Sentinel function codes are rejected | Any input row whose `function_code` resolves to a sentinel is rejected at the input-mapping step |
| Slugification is deterministic | When the extract carries `display_name` only, the script applies a single canonical `slugify` (lowercase, non-alphanumeric to underscore, trim leading/trailing underscores) |
| Confidence is set deterministically | A document with thresholds plus reference formula plus knowledge is `high`; partial is `medium`; name-and-description-only is `low` |
| Provenance is tagged | The `sources[]` array is set to identify where the metric came from; the script never defaults |
| Deduplication is by `metric_name` | An existing document with the same `metric_name` is enriched (Step 5) rather than duplicated |
| Empty descriptions are rejected | A document with a missing or empty `description` is rejected at the input-mapping step; the dedup gate at registration consumes the description |
| Dry run is mandatory | The first execution against the live catalog uses `--dry-run`; the dry run reports the planned insert count, the function breakdown, and the confidence distribution |

A script that violates these rules produces output the catalog's discipline does not admit, regardless of whether the mongo write succeeds.

**Governing source.** Metric Catalog.

## Step 3: Run the Dry Run

The dry run produces a report the actor reviews:

| Report item | What is verified |
|---|---|
| Metric count matches expectations | The extract row count and the planned insert count agree |
| Function breakdown | All listed functions are real codes; no sentinels |
| Duplicate `metric_name` | No duplicates within the batch |
| Confidence distribution | Reported (high / medium / low); matches the extract's metadata completeness |
| No empty descriptions | Zero rows would be inserted with an empty or missing description |

A dry run that surfaces unexpected counts, sentinel functions, or empty descriptions is not promoted to a live run.

**Governing source.** Metric Catalog.

## Step 4: Run Live and Verify

The live run uses the same script without `--dry-run`. The actor verifies the catalog's state via the `bc-core` read surface:

| Verification | Surface |
|---|---|
| Document count | `GET /api/seed-catalog/metrics/stats` |
| Function list with counts | `GET /api/seed-catalog/metrics/functions` |
| Sample metric round-trip | `GET /api/seed-catalog/metrics/{known-metric-name}` |
| Function filter | `GET /api/seed-catalog/metrics?function=finance&limit=5` |

A `bc-core` restart connects the surface to the new document set; the boot log reports the connected count.

**Governing source.** Metric Catalog.

## Step 5: Enrich Existing Metrics

When new metadata becomes available for metrics already in the catalog (thresholds from CXO packs, formulas from enrichment, CO bindings from contract analysis), an enrichment script applies a per-document update:

```
db.seed_metrics.updateOne(
  { metric_name },
  {
    $set: { thresholds, direction, co_bindings, confidence: 'high', updated_at: new Date() },
    $addToSet: { sources: enrichmentSource }
  }
)
```

The script does not replace the document. It updates only the fields the enrichment carries. It uses `$addToSet` for `sources` to preserve the prior provenance trail. It supports `--dry-run` and reports per-document the field changes.

**Governing source.** Metric Catalog.

## Step 6: Merge from External Source with Dedup

When merging a large external dataset that may overlap with existing seed metrics, the script runs in three passes:

**Pass 1: Export existing metric names.** The script exports the set of `metric_name` values currently in the collection.

**Pass 2: Classify each incoming metric.** For each incoming metric, the script checks against the exported set:

| Match type | Action |
|---|---|
| Exact name match | Enrich the existing document (Step 5) |
| No match | Insert as a new document |
| Ambiguous (similar name, same function) | Set aside for AI-assisted dedup |

**Pass 3: AI-assisted dedup for the ambiguous set.** The script batches ambiguous pairs by function, calls the AI dedup surface with name plus description pairs, and asks the maker-checker-gate envelope to classify each pair as `same` (merge), `related` (link via `related_metrics`), or `distinct` (insert both). A human reviews the AI verdict before applying.

The merge does not auto-apply AI verdicts. The verdict is a recommendation; the apply step is human-confirmed.

**Governing source.** Metric Catalog; AI Gates; AI Trust and Verification.

## Quality Gates

The Metric Seed Catalog enforces six gates at the script layer.

| Gate | Where enforced | What it checks |
|---|---|---|
| Sentinel function codes rejected | Load script input-mapping step | Any row whose `function_code` is a sentinel is rejected |
| Slugification deterministic | Load script input-mapping step | `metric_name` derives from `display_name` via the canonical `slugify` only |
| Empty descriptions rejected | Load script input-mapping step | A row with missing or empty `description` is rejected |
| Provenance present | Load script input-mapping step | Every document carries a non-empty `sources[]` array |
| Deduplication by `metric_name` | Load script input-mapping step | The script checks `metric_name` against the existing collection before insert |
| Quality gates do not run in the catalog | Read surface | The catalog is a dumb store; classification, dedup, and validation run at Metric Registration, not here |

The last gate is structural: the catalog itself does not classify or validate. A document in the catalog has not passed the platform's metric gates; it is a candidate for registration. Metric Registration is the chapter that runs the AI verification verdict and admits the metric to `metric.metric_definition`.

**Governing source.** Metric Catalog; Metric Registration.

## Boundary with Metric Registration

The Metric Seed Catalog is the input. Metric Registration is the gate. The two boundaries are distinct:

| Concern | Owned by | Persistent store |
|---|---|---|
| Curated metric reference data (definitions, descriptions, candidate thresholds) | Metric Seed Catalog Management (this chapter) | `bc_seed.seed_metrics` (MongoDB) |
| The platform metric definition row that an enrichment procedure can build on | Metric Registration | `metric.metric_definition` (PostgreSQL) |

A metric that exists in `seed_metrics` is a candidate. A metric in `metric.metric_definition` has passed the four registration gates (classification, dedup, function validation, name canonicalization). The `seedRef` column on `metric.metric_definition` is the back-pointer from the platform definition to its seed candidate.

**Governing source.** Metric Registration; Metric Catalog.

## Drift Inventory

| Drift item | Form |
|---|---|
| `bc-core` restart is manual | After a load or enrichment, the registration surface does not see the new content until `bc-core` reconnects to MongoDB |
| Confidence distribution varies by source | The chapter does not assert a target confidence mix. The read surface reports the confidence distribution from the loaded source documents; source-specific confidence belongs in generated or operational reports |
| Initial population has multiple scripted loads | The catalog has multiple loader families. A system audit reports the current per-source counts without this chapter recording a time-bound phase inventory |
| Constants are not yet seeded | Some metric formulas reference numeric constants (days-in-period multipliers, percentage scaling). The catalog does not yet carry a `formula.constants` map per document; constant values are sourced from a curated map in `bc-core/src/registry/seed/d329-constants.ts` at registration time. Extending the seed schema to carry constants is a queued enhancement |
| Authoring is script-only | The catalog has no governed-via-API entry path; the audit substrate does not capture script invocations the same way it captures API mutations |

**Governing source.** Metric Catalog; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-ecec75 | Establishes one metric per KPI as the metric architecture; the seed catalog's `metric_name` uniqueness, the dedup discipline, and the registration boundary all derive from this principle |

**Governing source.** Decisions: ADR Registry.

## References

- Metric Catalog
- Business Vocabulary
- Metric Registration
- Metric Evaluation
- Data Model and Schema
- Infrastructure
- AI Gates
- AI Trust and Verification
- DEC-ecec75: One metric per KPI; metric architecture
- legacy-v2/docs/sops/metric-seed-catalog-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding


