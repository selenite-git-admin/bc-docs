---
id: metric-registration
order: 60
title: "Metric Registration"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, metric-catalog, metric-seed-catalog-management, ai-gates, ai-trust-and-verification, business-vocabulary, data-model-and-schema]
governing_sources:
  - Metric Catalog
  - AI Gates
  - AI Trust and Verification
governing_adrs:
  - DEC-ecec75 (D068 One MC per KPI; metric architecture)
governing_sops:
  - legacy-v2/docs/sops/metric-registration-sop.md
errata_referenced: []
v2_sources:
  - sops/metric-registration-sop.md
diagrams: []
---

# Metric Registration

## Scope

This chapter records the governed sequence by which metrics from the Metric Seed Catalog (`bc_seed.seed_metrics`) are admitted to the platform metric catalog (`metric.metric_definition`). The chapter names the four AI verification gates the procedure runs at registration time (metric classification, semantic dedup, function validation, name canonicalization), the verdict-routing rule (all green to auto-register; any amber with no red to register with corrections; any red blocks), the seed-to-platform field mapping, the registration result `seedRef` back-pointer, and the boundary between Metric Registration and the post-registration enrichment procedure that builds `metric_formula` and `metric_definition_knowledge` rows. It records the boundary between Metric Registration and Metric Contract Creation. It records the as-built drift between the procedure and the platform's current metric registration state.

This chapter does not redefine the Metric Seed Catalog (Metric Seed Catalog Management), the metric catalog runtime tables (Metric Catalog), the AI maker-checker-gate envelope (AI Gates), or the metric contract creation that consumes registered definitions (Metric Contract Creation).

All quality gates (classification, dedup, function validation, name canonicalization) live at the Metric Registration boundary, not in the seed catalog. The seed catalog is a dumb store; this chapter is the first gate.

**Governing source.** outline.md §4.6; Metric Catalog.

## What the Procedure Produces

| Artifact | Persistent store | Created by |
|---|---|---|
| Platform metric definition (status `active`, maturity `registered`) | `metric.metric_definition` | Step 4 |
| Related-metric link (when amber dedup verdict identified a sibling) | `metric.metric_definition_knowledge.related_metrics[]` | Step 4 |
| AI verification trail | `bc-ai` evidence table (`maker_checker_gate` runs) | Steps 3 |
| `seedRef` back-pointer | `metric.metric_definition.seedRef` | Step 4 |

The platform definition row carries the metric's identity (name, display name, description, function code, subfunction code, industry codes, tier code) plus its registration trail (`maturityCode: registered`, `seedRef` pointing back to the seed catalog `metric_name`). The `metric_formula` and `metric_definition_knowledge` rows are produced by the post-registration enrichment procedure, not by this chapter.

**Governing source.** Metric Catalog.

## Prerequisites

| Precondition | Why it is required |
|---|---|
| Cognito authenticated session for a platform actor | Metric mutations are `@PlatformOnly()` JWT-guarded |
| Seed Metric Catalog populated (`bc_seed.seed_metrics`) | The procedure operates on candidates from the seed catalog; no seed entries means no candidates |
| The bc-core contract surface is reachable | The procedure writes via `POST /api/metric-definitions` and reads via `GET /api/metric-definitions` |
| The bc-ai metric-verification surface is reachable | The four registration gates run via `POST /api/ai/suggest/metric-verify`; absence of the surface defers registration rather than allowing it without verification |

A precondition that fails is not bypassed. AI absence does not unlock manual override; the procedure defers and records the outage.

**Governing source.** Metric Catalog; AI Gates.

## The Four Registration Gates

Every candidate metric passes through four gates at registration. The gates are run by the AI verification endpoint as a maker-checker-gate envelope; the verdict per gate routes the candidate.

| # | Gate | Question | Verdicts |
|---|---|---|---|
| 1 | Metric Classification | Is this a measurable KPI with formula, direction, threshold, or is it a data point, operational descriptor, or runtime observation? | `red` blocks; `green` confirms; `amber` requires human review |
| 2 | Semantic Dedup | Does this metric already exist under a different name? Checks by intent, not by slug ("Days Sales Outstanding" and "Days in Accounts Receivable" are the same metric) | `red` blocks (returns existing metric ID); `amber` registers and links related; `green` no match |
| 3 | Function Validation | Is `function_code` and `subfunction_code` correct for the metric? | `green` confirmed; `amber` AI suggests correction (e.g., "this is supply_chain, not operations") |
| 4 | Name Canonicalization | Is the display name clear, canonical, and professional? | `green` good; `amber` AI suggests better name (e.g., "Asset maintenance cost as a percentage of revenue" to "Asset Maintenance Cost Ratio") |

Verdict combination:

| Combined verdict | Action |
|---|---|
| All green | Auto-register |
| Any amber, no red | Register with AI corrections applied; human can override per-correction |
| Any red | Blocked; cannot register |

A red verdict is a hard block. Bypassing a red verdict requires escalation through bc-admin with explicit justification and re-verification with additional context; programmatic override is forbidden.

**Governing source.** AI Gates; AI Trust and Verification.

## Track A: Manual plus AI (UI-Driven)

The bc-admin UI at `/metrics/register` presents the seed catalog. The actor browses by function, searches by name or description, filters by `confidence` and `source`, and selects one or more metrics to register.

The UI calls `POST /api/ai/suggest/metric-verify` per selection with the seed metadata plus the existing platform metrics for the function (the dedup context). The maker-checker-gate envelope returns the four verdicts. The UI renders results per metric:

| Row state | Display |
|---|---|
| Green | Ready to register; no issues |
| Amber | Corrections suggested; the actor accepts or overrides each |
| Red | Blocked; the row shows the reason (not a metric, or duplicate of `<metric_name>`) |

The actor reviews amber items, accepts or overrides corrections, and clicks Register N Metrics. Only green and accepted-amber rows are admitted; red rows stay in the seed catalog without a platform definition.

**Governing source.** Metric Catalog; AI Gates.

## Track B: Programmatic

The same endpoints serve agent-driven registration. The actor reads the seed metrics for a function, fetches the existing platform metrics for the same function as dedup context, calls `POST /api/ai/suggest/metric-verify` per seed metric, and registers the non-red candidates via `POST /api/metric-definitions`:

```
POST /api/metric-definitions
{
  "metricName": "asset_maintenance_cost_ratio",
  "displayName": "Asset Maintenance Cost Ratio",
  "descriptionText": "Maintenance cost as a percentage of total revenue.",
  "functionCode": "asset_management",
  "subfunctionCode": null,
  "industryCategoryCode": "universal",
  "industryCode": "universal",
  "tierCode": "standard",
  "statusCode": "active",
  "maturityCode": "registered",
  "seedRef": "asset_maintenance_cost_as_a_percentage_of_revenue"
}
```

For bulk registration, the verification surface admits a batch endpoint: `POST /api/ai/suggest/metric-verify-batch` accepts an array of candidates and returns an array of verdicts; same gates, parallel model calls, single round trip. The chapter records that provider-throttle protection is required; the active cap belongs to the implementation configuration, not chapter prose.

The two tracks call the same gates. There are no programmatic shortcuts.

**Governing source.** AI Gates.

## Field Mapping (Seed to Platform)

The procedure maps seed catalog columns to platform definition columns:

| Seed catalog field | Platform definition field |
|---|---|
| `metric_name` (corrected by AI canonicalization if amber) | `metricName` |
| `display_name` | `displayName` |
| `description` | `descriptionText` |
| `function_code` (corrected by AI function validation if amber) | `functionCode` |
| `subfunction_code` | `subfunctionCode` |
| `industry_category_code` | `industryCategoryCode` |
| `industry_code` | `industryCode` |
| `tier_code` (default `standard`) | `tierCode` |
| n/a (set by registration) | `statusCode: active` |
| n/a (set by registration) | `maturityCode: registered` |
| Seed catalog `metric_name` (original, before any AI canonicalization) | `seedRef` |

The `seedRef` preserves the back-pointer to the seed candidate even when AI corrections changed the platform `metricName`. The seed catalog itself is not mutated by registration; the seed remains as raw reference data.

**Governing source.** Metric Catalog; Metric Seed Catalog Management.

## Related Metric Linking

When the dedup gate returns `amber` with a related metric identified, the procedure creates a bidirectional link:

```
metric_a.related_metrics += metric_b
metric_b.related_metrics += metric_a
```

The link is informational; it does not affect computation. It surfaces in the metric catalog UI as the "Related" set so an actor exploring one metric can navigate to its siblings.

**Governing source.** Metric Catalog.

## The Boundary with Enrichment

Registration produces the metric definition shell. Enrichment fills it. The post-registration procedure is governed elsewhere (the Metric Catalog enrichment surface is not in scope for this chapter), but the chapter records the four enrichment phases for orientation:

| Phase | Input | Output |
|---|---|---|
| Formula enrichment | Registered `metric_definition` | `metric_formula` row with parseable expression and `metric_formula_variable` rows |
| Knowledge enrichment | `metric_definition` plus `metric_formula` | `metric_definition_knowledge` row with context, stakeholders, drivers, thresholds |
| Verification | `metric_formula` | `metric_formula_verification` row from cross-family AI verification |
| Maturity promotion | All enrichment complete | `maturityCode` advances `registered` to `verified` (auto) to `locked` (manual) |

Enrichment is a separate procedure; this chapter ends at the `registered` state.

**Governing source.** Metric Catalog.

## Forbidden Patterns

The chapter records seven forbidden patterns. Each one violates the platform's metric registration discipline.

| Forbidden | Why |
|---|---|
| Quality gates in the seed catalog | The seed catalog is a dumb store; classification, dedup, validation belong here at registration |
| Direct DB writes | All registrations route through the REST API; no `INSERT INTO metric.metric_definition` from psql or scripts |
| Skip AI verification | Every candidate runs through `metric-verify`; if `bc-ai` is unreachable, the actor records the outage and defers registration |
| Bulk maturity promotion | Each metric earns its maturity through the enrichment procedure; no `UPDATE metric.metric_definition SET maturity_code = 'verified'` across all rows |
| Modify seed catalog based on registration results | Registration results are not written back to seed; the seed catalog stays as raw reference data |
| Register blocked metrics | A red verdict blocks registration; programmatic override is forbidden, escalation is the only path |
| Register without dedup context | The `existing_metrics[]` list is mandatory in the verification call; without it, the dedup gate cannot function |

**Governing source.** Metric Catalog; AI Gates.

## Boundary with Other Onboarding Chapters

| Chapter | Relationship |
|---|---|
| Metric Seed Catalog Management | Provides the candidate seed entries this chapter promotes |
| Canonical Field Seeding | Independent at registration time; CFs are seeded from the metric formula variables that emerge during enrichment, not at registration |
| Canonical Contract Creation | Independent at registration time; CCs are created against BOs, not against metric definitions |
| Metric Contract Creation | The MC binds a registered metric definition; without registration there is no definition for the MC to bind |
| MC Chain Integrity | Operates on existing MCs; the registration step is a precondition for MC creation |

**Governing source.** Metric Seed Catalog Management; Metric Contract Creation.

## Drift Inventory

| Drift item | Form |
|---|---|
| Maker model selection | The maker model for `metric-verify` is currently a Gemini family model; the checker is a direct-Anthropic family model. Cross-family discipline applies (the AI Trust and Verification chapter governs the matrix); the chapter records that the registration gate runs through the same cross-family envelope as other gates |
| Dedup gate dependence on existing metric set | The dedup gate's `existing_metrics[]` payload is the function-scoped existing list at the moment of verification. A concurrent registration in the same function may produce a duplicate that the dedup gate did not see; the chapter records this race-condition gap |
| Function validation accuracy varies | The function validation gate is calibrated against the master taxonomy; metrics in domain niches (industrial-specific KPIs, finance-specific accounting concepts) may receive amber verdicts more often than core KPIs |
| Bulk registration throughput is rate-limited | Provider-throttle protection constrains bulk operations; the implementation configuration owns the active cap |
| Enrichment procedure is partial | Some registered metrics never reach `verified` because the enrichment procedure has not run end-to-end against them. The catalog reports per-maturity counts; the registration step itself is healthy even when enrichment lags |

**Governing source.** AI Gates; AI Trust and Verification; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-ecec75 | Establishes one MC per KPI; the dedup discipline at registration is the operational form of "one metric per KPI" at the definition layer |

**Governing source.** Decisions: ADR Registry.

## References

- Metric Catalog
- Metric Seed Catalog Management
- Metric Contract Creation
- Canonical Field Seeding
- AI Gates
- AI Trust and Verification
- Business Vocabulary
- Data Model and Schema
- DEC-ecec75: One MC per KPI; metric architecture
- legacy-v2/docs/sops/metric-registration-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding



## MCF Metric Drafting — new authoring path (operator runbook addition)

**Added per Metric Drafting (legacy: M12.5) PR-2 (DBCP §12.3 operator runbook update).**

Effective from MCF Metric Drafting closeout, new metric authoring follows the MCF intake → panel → materialization sequence:

1. **Metric Intake (legacy: M11)** — operator submits the candidate metric via `ReservoirIngestionService.ingestOperatorDirectSubmission(...)` (CLI), OR candidates flow in automatically from the `seed_metrics` / `metric_definition` adapter sources.
2. **Metric Draft Review panel (legacy: M12)** — three-model panel (Maker / Checker / Moderator) produces a consensus proposal in `mcf.metric_authoring_panel_run.consensus_payload_json`. Operator reviews the proposal via the M16 audit UI (when shipped).
3. **Metric Drafting materialization** — `MetricAuthoringMaterializationService.runMaterialization(panelRunUid, opts)` materializes an `APPROVE_FOR_DRAFT` panel proposal into MCF substrate. The service:
   - Reads the mapr + linked intake row
   - Validates Materialization Preconditions (legacy: L-V1 / L-V2 / L-V3)
   - Performs the runtime `framework_policy` lookup (deterministic latest-wins; throws on >1 active row)
   - Detects existing materialization for HA-8 idempotent retry (returns prior UIDs without re-writing)
   - Calls `McfCertWriterService.createMetricDraft` (with real canonical AST per D-M12.5-AST AST-A)
   - Inserts one `mcf.metric_self_verification_fixture` with the 6 hash columns computed from MCV substrate
   - Runs the M10 verifier on the fixture
   - Transitions the Metric Intake row from `pending` → `consumed_by_panel`
   - Returns a `MaterializationResult` with the 5 new substrate UIDs + `intake_transitioned` flag

   **Operator workflow (Metric Drafting PR-2 ship):**
   - Preflight (read-only): `node bc-core/scripts/mcf-m12-5-preflight.mjs --panel-run-uid <uuid>` runs 5 substrate probes (mapr APPROVE_FOR_DRAFT, framework_policy exact-1-active, PR-1 partial-unique index present, M11 intake state, HA-8 retry detection) without writing. Exit 0 = safe to proceed.
   - Service invocation: wire `MetricAuthoringMaterializationService` through NestJS DI (registered in the MCF module alongside its 6 collaborators) or invoke via the integration spec wiring pattern (see `bc-core/src/registry/mcf/metric-authoring-materialization.service.integration.spec.ts`). A NestJS-bootstrap CLI for direct one-shot invocation is deferred to a follow-up PR.

The materialized MCV stops at `governance_state_code='draft'`. Publication Review (legacy: M13) runs the Publication Eligibility checks (legacy: PE-MC). Publication (`approved → active`) is Metric Activation (legacy: M14).

### Legacy `POST /api/metric-catalog/definitions` during the transition window

The legacy `POST /api/metric-catalog/definitions` endpoint remains LIVE during the Sunset window (per `BCCORE_MCF_LEGACY_SUNSET_DATE`) for backward compatibility. It carries a `Sunset` HTTP header signaling the deprecation date. **New authoring should NOT use the legacy endpoint.**

See `docs/operating-model/mcf-legacy-bridge.md` for the canonical read-fallback policy + Sunset semantics.

### Tenant runtime — unchanged during Metric Drafting

Tenant runtime evaluation (`boundary/metric.service.ts`, `ReadinessLedgerService`, `chain-status.service.ts`) continues to read against the legacy `metric.metric_definition` corpus during Metric Drafting. Tenant runtime MCF awareness ships in M18+. Until then, materialized MCs in `mcf.metric_contract` are visible to operator inspection only — they do NOT influence tenant evaluation.
