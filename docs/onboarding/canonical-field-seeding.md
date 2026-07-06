---
id: canonical-field-seeding
order: 54
title: "Canonical Field Seeding"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, the-authority-model, business-vocabulary, metric-catalog, business-field-and-business-object-onboarding, data-model-and-schema]
governing_sources:
  - The Contract Grammar
  - Business Vocabulary
  - Metric Catalog
governing_adrs:
  - DEC-d72560 (D301 Canonical Field as 3rd contract primitive)
  - DEC-9d1f4b (D327 Shared dimension normalization)
  - DEC-69f09e (ISO 11179 naming discipline)
  - DEC-a17d0f (Semantic Definitions Authority — governing authority for CF/BF/BO certification)
  - DEC-b7affa (D404 G11 BF↔CF semantic-family compatibility gate)
  - DEC-a49413 (D407 SDA Phase 1 implementation profile — CF semantic_family advisory panel)
governing_sops:
  - legacy-v2/docs/sops/cf-seeding-sop.md
errata_referenced: []
v2_sources:
  - sops/cf-seeding-sop.md
diagrams: []
---

# Canonical Field Seeding

## Scope

This chapter records the governed sequence by which Canonical Fields (CFs) are admitted to the platform vocabulary. It names the demand signal that drives CF creation (metric formula variables), the naming rules that distinguish CFs from BFs, the role of the five shared dimensions in CF naming, the registration procedure (single and bulk), and the verification gate that confirms every metric formula variable has a corresponding registered CF. It records the boundary between Canonical Field Seeding and the contract families that consume CFs (Canonical Contract Creation, Metric Contract Creation). It records the as-built drift between the procedure and the platform's current CF state.

This chapter does not redefine the contract grammar that introduces CF as the third contract primitive (The Contract Grammar; DEC-d72560), the metric catalog that owns metric definitions and their formula variables (Metric Catalog), or the BF and BO vocabulary that CFs are explicitly distinct from (Business Vocabulary; Business Field and Business Object Onboarding).

**Governing source.** outline.md §4.6; The Contract Grammar.

## What a Canonical Field Is

A Canonical Field is a named, function-scoped field in the platform's metric vocabulary. The persistent store is `contract.canonical_field`. Each row carries an identifier (`canonical_field_id`), a globally unique `field_name` (snake_case), a `display_name`, a `function_code` (and optional `subfunction_code`), a `unit_type_code`, a `data_type`, a `role` (`input` or `output`), and a `description_text`.

CFs are the contractual binding between two vocabularies that the contract chain keeps separate. The source-side vocabulary (BF names) lives in source structure; the metric-side vocabulary (CF names) lives in metric formulas. The Canonical Contract `cc_field_mapping` translates between them. Without the CF as a third primitive, the chain has no place to record the translation; it has either source vocabulary or metric vocabulary, but not both.

A CF is not a BF. BFs are source-scoped (composed into BOs). CFs are metric-scoped (referenced by metric formula variables). They share no namespace. A CF named `accounts_receivable_balance` is metric vocabulary; a BF named `receivable_hdr_amount` is source vocabulary. The Canonical Contract translates between them via `cc_field_mapping`.

**Governing source.** The Contract Grammar.

## What the Procedure Produces

A Canonical Field seeding session produces:

| Artifact | Persistent store | Created by |
|---|---|---|
| Canonical Field rows for all formula variables | `contract.canonical_field` | Steps 4 or 5 |
| Updated coverage state | (derived from gap query) | Step 6 verification |

The procedure does not produce `cc_field_mapping` entries; those are created at Canonical Contract Creation. CF Seeding produces the CF rows that future CC creation will reference.

**Governing source.** The Contract Grammar.

## When the Procedure Runs

The procedure runs in three situations:

| Situation | Trigger |
|---|---|
| Before Canonical Contract Creation | CC Creation prerequisite check requires every CF the CC's `cc_field_mapping` will reference to exist |
| After Metric Registration | A newly registered metric carries formula variables whose names are the demand signal for CFs |
| After chain gap analysis | A chain status check (Chain Completeness and Verdict) reports L4 (CC mapping) gaps that trace to missing CFs |

The procedure does not run speculatively. Every CF is traceable to a metric formula variable or to a grain reference. The chapter does not admit CFs that have no demand signal.

**Governing source.** The Contract Grammar; Metric Catalog; Chain Completeness and Verdict.

## Prerequisites

| Precondition | Why it is required |
|---|---|
| Cognito authenticated session for a platform actor | CF mutations are `@PlatformOnly()` JWT-guarded |
| The bc-core canonical-field surface is reachable | The procedure writes via `POST /api/canonical-fields` and reads via `GET /api/canonical-fields` |
| Metric definitions are registered with formula variables | The demand signal is `metric.metric_formula_variable.field_name`; without metric definitions there is nothing to seed |

A precondition that fails is not bypassed. The procedure does not seed CFs from a speculative list; the demand signal is mandatory.

**Governing source.** The Contract Grammar; Metric Catalog.

## Step 1: Extract the Demand Signal

The actor extracts the set of unique variable field names from current metric formulas:

```
SELECT DISTINCT mfv.field_name
FROM metric.metric_formula_variable mfv
JOIN metric.metric_formula mf
  ON mf.metric_formula_id = mfv.metric_formula_id
WHERE mfv.role IN ('input', 'output')
  AND mf.is_current = true
ORDER BY mfv.field_name;
```

The query returns the set of names that the platform's current metric formulas depend on. Every name in this set must eventually be a registered CF; the chapter calls this the demand signal.

**Governing source.** Metric Catalog.

## Step 2: Read Existing CFs

```
GET /api/canonical-fields?limit=<page-size>
```

The actor collects the registered set of `field_name` values.

**Governing source.** The Contract Grammar.

## Step 3: Identify Gaps

The actor compares the demand signal (Step 1) against the registered set (Step 2). Names in the demand signal but not in the registered set are gaps. The chapter recommends the gap query in SQL form because the result is the work list the seeding session operates on:

```
SELECT mfv.field_name, COUNT(*) AS formula_count
FROM metric.metric_formula_variable mfv
JOIN metric.metric_formula mf
  ON mf.metric_formula_id = mfv.metric_formula_id
LEFT JOIN contract.canonical_field cf
  ON cf.field_name = mfv.field_name
WHERE cf.canonical_field_id IS NULL
  AND mfv.role IN ('input', 'output')
  AND mf.is_current = true
GROUP BY mfv.field_name
ORDER BY formula_count DESC;
```

`formula_count` ranks the gaps by how many metric formulas reference each missing CF; the highest-impact gaps land first in the seeding session.

**Governing source.** Metric Catalog; The Contract Grammar.

## Step 4: Register CFs Individually

For each gap, the actor calls:

```
POST /api/canonical-fields
{
  "fieldName": "accounts_receivable_balance",
  "displayName": "Accounts Receivable Balance",
  "functionCode": "finance",
  "subfunctionCode": "accounts_receivable",
  "unitTypeCode": "currency",
  "dataType": "decimal",
  "role": "input",
  "descriptionText": "Total outstanding accounts receivable at period end"
}
```

The required fields are `fieldName`, `functionCode`, `dataType`, and `role`. The optional fields populate the CF's metadata; a CF that is registered with only the required fields is still admissible, but later chapters (Metric Contract Creation, Chain Completeness and Verdict) treat the metadata gaps as drift.

**Governing source.** The Contract Grammar.

## Step 5: Bulk Register

For large gap sets, the bulk endpoint admits an array of CFs in a single call:

```
POST /api/canonical-fields/batch
{
  "fields": [
    {
      "fieldName": "accounts_receivable_balance",
      "functionCode": "finance",
      "subfunctionCode": "accounts_receivable",
      "unitTypeCode": "currency",
      "dataType": "decimal",
      "role": "input",
      "descriptionText": "Total outstanding accounts receivable at period end"
    }
  ]
}
```

The bulk endpoint enforces the same per-row validation as the single endpoint; an invalid row in the batch causes the row to be rejected with the rest of the batch admitted. The endpoint is convenience, not a discipline change.

**Governing source.** The Contract Grammar.

## Step 6: Verify Zero Gaps

After registration, the actor re-runs the gap query (Step 3) and confirms the result is empty:

```
SELECT mfv.field_name, cf.canonical_field_id
FROM metric.metric_formula_variable mfv
LEFT JOIN contract.canonical_field cf
  ON cf.field_name = mfv.field_name
WHERE cf.canonical_field_id IS NULL
  AND mfv.role IN ('input', 'output');
```

Zero rows confirm that every formula variable has a corresponding CF. Any remaining row identifies an incomplete seeding session and is fixed before the actor proceeds to Canonical Contract Creation.

**Governing source.** The Contract Grammar; Chain Completeness and Verdict.

## CF Certification

CF seeding (Steps 1-6) admits CFs in pre-SDA `draft` state. Admission proves the CF is named correctly and traceable to a demand signal. Admission does **not** prove the CF can participate in a metric chain. Certification — under the Semantic Definitions Authority (SDA, DEC-a17d0f) — does, by carrying the CF through the unified six-state lifecycle to `certified` with an explicit `semantic_family` classification under SDA gates G1–G8 and the related authoring-time gates G9–G11.

A CF that is not `certified` (or whose `semantic_family` is null) may not serve as an input to a metric contract that is activating. The activation gate (Step 0, separate slice) refuses MC activation on any input CF whose state is not `(status_code='certified', semantic_family IS NOT NULL)`. Already-active MCs are unaffected by retroactive enforcement; only new activations consult the gate.

**Governing authority for the certification step.** DEC-a17d0f (Semantic Definitions Authority). SDA owns the lifecycle (six states: `proposed → reviewing → certified → deprecated → superseded` plus terminal `withdrawn`; `is_archived` as an independent visibility flag), the deterministic gates G1–G8 at certification time and G9–G11 at authoring time, the override matrix (overridable G1 / G2b / G3 / G4 with rationale ≥ 40 chars + auto-spawned follow-up TSK; non-overridable G2a / G5 / G6 / G7 / G8 / G10 Class-A), and the evidence ledger `contract.certification_record` (DBCP-1c).

**Supporting amendments.** DEC-b7affa (D404 — G11 BF↔CF semantic-family compatibility, mostly non-overridable, fires at `cc_field_mapping` authoring time). DEC-a49413 (D407 — implementation profile naming the multi-vendor advisory panel for CF `semantic_family` classification + `cf_dedup` advisory).

**AI posture.** Per DEC-a17d0f §5, bc-ai is admitted as **advisory evidence requiring human acknowledgement, never autonomous authority**. AI verdicts never transition state, never block, never certify. Deterministic gates are the only blocking authority.

**Governing source.** DEC-a17d0f; DEC-b7affa; DEC-a49413.

## Step 7: Submit for Review with proposed semantic_family

The actor submits a draft CF to SDA review with a proposed `semantic_family`:

```
POST /api/semantic-definitions/cf/:id/submit-for-review
{ "semanticFamily": "measure-currency" }
```

The `semantic_family` value is chosen from the closed enum sourced from `bc-core/src/registry/semantic/compatibility-filter.service.ts:36-59` (24 values; per DEC-a17d0f §7, normalised by DBCP-1a into `master.semantic_family`):

| Group | Values |
|---|---|
| Identifier / code | `identifier`, `code` |
| Descriptor | `name`, `text` |
| Measure | `measure-currency`, `measure-count`, `measure-ratio`, `measure-percent`, `measure-score` |
| Temporal | `date`, `period`, `datetime`, `duration` |
| Conformed dimension | `dim-calendar-date`, `dim-fiscal-period`, `dim-currency`, `dim-country`, `dim-legal-entity`, `dim-gl-account`, `dim-cost-center`, `dim-customer`, `dim-vendor`, `dim-product` |

The actor may consult the SDA's advisory suggest endpoint before submitting, for a recommendation only:

```
POST /api/semantic-definitions/cf/:id/classify/suggest
```

This invokes the multi-vendor advisory panel (Gemini Maker / OpenAI Checker / Claude Moderator per DEC-a49413) in advisory mode without state change. Response carries a recommended family + rationale. **The recommendation is advisory; the operator's submitted value is what the SDA gates evaluate.**

**Governing source.** DEC-a17d0f §6 (service surface); DEC-a49413 (panel composition); DEC-804874 (semantic_family column).

## Step 8: Preview SDA gates

Before committing the certify transition, the actor previews the gate run:

```
POST /api/semantic-definitions/cf/:id/certify/preview
```

The response reports per-gate verdicts from SDA's `gates.ts` evaluator. For CF certification at the `reviewing → certified` transition, gates G1–G8 are evaluated (per DEC-a17d0f §4):

| Gate | Concern | Overridable? |
|---|---|---|
| G1 | Naming profile (P3 — CF) compliance | Yes (rationale + follow-up TSK) |
| G2a | Exact-identity uniqueness | No |
| G2b | Normalized-form collision | Yes |
| G3 | Definition presence and quality | Yes |
| G4 | Provenance presence | Yes |
| **G5** | **`semantic_family` populated and in master enum (CF-binding)** | **No** |
| **G6** | **Data type / unit compatibility per `semantic_family` compatibility matrix** | **No** |
| G8 | Anti-BO-prefix on CF naming | No |

Gates G9 (reference admissibility at authoring time), G10 (Meaning-once on `cc_field_mapping`), and G11 (BF↔CF compatibility — DEC-b7affa) fire downstream when this CF is referenced by a CC or MC; they do not run at CF certification time.

The advisory panel (Gemini / OpenAI / Claude per DEC-a49413) runs alongside the gate evaluation and writes evidence to `advisory_verdicts[]`. The panel does not produce a gate verdict; its combined acknowledgement state maps to SDA §5's `green / amber / red / unverified` vocabulary.

**Governing source.** DEC-a17d0f §4; DEC-a49413 §2.

## Step 9: Certify

```
POST /api/semantic-definitions/cf/:id/certify
{
  "semanticFamily": "measure-currency",
  "overrides": [
    { "gateCode": "G3", "rationale": "..." }     // only when an overridable gate failed
  ],
  "acknowledgements": [
    { "surface": "advisory_panel", "verdict": "amber", "rationale": "..." }   // only when AI verdict requires
  ]
}
```

Per SDA's contract:

- **Hard refusal** on any non-overridable gate (G2a / G5 / G6 / G7-BF / G8-CF / G10 Class-A) — the CF stays at its current state; SDA writes a `return_to_author` row to `contract.certification_record` with `gate_results_json` carrying the failed gate evidence.
- **Overridable gate failure** — operator may proceed by supplying `overrides[]` entries with rationale ≥ 40 chars; SDA auto-spawns a follow-up TSK tagged `sda-override`, records its UID in `override_followup_task_uid`, and proceeds.
- **AI advisory amber / red / unverified** — operator must supply matching `acknowledgements[]` rationale ≥ 40 chars per DEC-a17d0f §5; same auto-spawned follow-up mechanic. If a deterministic gate fails, AI acknowledgement does not bypass.

On success the CF transitions `reviewing → certified` with `semantic_family` recorded. The transition is terminal for the certified value; re-classification requires `deprecated → superseded` with a successor CF carrying the corrected family (per SDA §2).

`contract.certification_record` is written per DEC-a17d0f §7. All columns populated to SDA's contract: `primitive_type='canonical_field'`, `primitive_id`, `action_code`, `from_state_code` / `to_state_code` per the six-state lifecycle, `gate_results_json` as a `GateResult[]` array per `bc-core/src/registry/semantic-definitions/gates.ts`, `advisory_verdicts_json` carrying entries `{surface, verdict, confidence, rationale, model_id, prompt_hash, timestamp, acknowledgement}` per DEC-a17d0f §5 (one entry per panel participant + one for `cf_dedup`), and `override_*` fields populated when the override / acknowledgement path is used.

`contract.l_node_semantic_trace` is **not** used for CF certification evidence — that table is MC × variable × L-node chain-trace evidence (D366).

On a successful `reviewing → certified` transition, SDA fires the D366 refresh hook for every CC that maps this CF, so L-node verdicts re-roll for affected metric contracts: `LNodeSemanticService.refreshAffectedMetrics(ccId)` is called per CC fanned out from `cc_field_mapping WHERE canonical_field_id = :cfId` (per DEC-a49413 §6).

**Governing source.** DEC-a17d0f §§4–7; DEC-a49413 §§5–6; DEC-804874 (D366).

## Step 10: Bulk Certification

The SDA's certify path admits bulk operations for the one-time backfill of pre-SDA CFs in `draft` with `semantic_family IS NULL`:

```
POST /api/semantic-definitions/cf/batch-certify
{
  "certifications": [
    { "cfId": "...", "semanticFamily": "measure-currency", "overrides": [], "acknowledgements": [] },
    { "cfId": "...", "semanticFamily": "period",           "overrides": [], "acknowledgements": [] }
  ]
}
```

Per-CF discipline follows SDA's contract:

| Rule | Form |
|---|---|
| Per-CF gates run independently | One CF's gate failures do not affect other CFs in the batch |
| Per-CF advisory panels run concurrently across CFs (N ≤ 5 default), sequentially within a CF | Maker → Checker → Moderator within a CF; up to N CFs in flight |
| Per-CF overrides + acknowledgements | Each requires per-CF rationale ≥ 40 chars + per-CF auto-spawned follow-up TSK. No batch-level override |
| Atomic per CF | One `certification_record` row per CF per attempt; failures leave the CF at its current SDA state |

The pre-SDA CF backfill is coordinated with SDA Phase 1 DBCP-1d (bulk `draft → proposed` migration).

**Governing source.** DEC-a17d0f §§4, 9; DEC-a49413 §7.

## Step 11: Verify Certification Coverage

After certification (single or bulk), the actor verifies zero uncertified CFs in the demand signal:

```sql
SELECT mfv.field_name, cf.status_code, cf.semantic_family
FROM metric.metric_formula_variable mfv
JOIN metric.metric_formula mf
  ON mf.metric_formula_id = mfv.metric_formula_id
LEFT JOIN contract.canonical_field cf
  ON cf.field_name = mfv.field_name
WHERE mfv.role IN ('input', 'output')
  AND mf.is_current = true
  AND (cf.status_code IS DISTINCT FROM 'certified' OR cf.semantic_family IS NULL);
```

Zero rows confirm every metric formula variable resolves to a `certified` CF with a populated `semantic_family`. Any remaining row blocks MC activation for the metric(s) that reference it (Step 0 gate, separate slice).

**Governing source.** DEC-a17d0f; Chain Completeness and Verdict.

## Naming Rules

The chapter codifies four CF naming rules. They are stated as the platform's discipline, not as recommendations.

| Rule | Form | Reason |
|---|---|---|
| CF names equal metric formula variable names | The demand signal is the source of truth for CF names | Top-down from demand, not bottom-up from source structure |
| Snake_case, globally unique | ISO 11179 naming per DEC-69f09e | The CF is a registry primary key and a JSON property name |
| Function-scoped | A CF lives in a business function (finance, supply chain, etc.); it does not live in a BO | CFs are metric vocabulary, not source vocabulary |
| Output CFs follow `{metric_short_name}_{property}` | The output CF for the DSO metric is `dso_days` | Establishes the link from the output to the metric that produced it |

A CF that is named with a BO prefix (e.g., `receivable_hdr_amount`) is a BF name, not a CF name. The chapter does not admit BO-prefixed names into the CF registry; the registration endpoint rejects them at the validation layer.

**Governing source.** The Contract Grammar; Business Vocabulary.

## Shared Dimension CFs

The five shared dimensions (`company_code`, `currency_code`, `language_code`, `country_code`, `unit_of_measure`; D294 in the v2 SOP shorthand) may be registered as CFs when metric formulas reference them in formulas or grain definitions. The CF name is the shared name verbatim, not a BO-scoped variant:

| Field | Value |
|---|---|
| `fieldName` | `company_code` (not `ar_company_code`) |
| `role` | `input` |
| `unitTypeCode` | `text` |
| `dataType` | `text` |
| `functionCode` | The function where the shared dimension is first needed, or a shared / common function code |

The shared dimension CFs unify multi-CC metrics. A metric that binds both `cc__receivable_hdr` and `cc__invoice_hdr` needs one grain key (`company_code`) that matches across both. The CC onboarding service normalizes shared dimensions in its `field_selection` per DEC-9d1f4b; this chapter governs the CF naming that the normalization expects.

**Governing source.** The Contract Grammar; Business Vocabulary.

## Quality Checks

The procedure enforces four checks the actor runs after every seeding session:

| Check | SQL form | Pass condition |
|---|---|---|
| No duplicate `field_name` | `SELECT field_name, COUNT(*) FROM contract.canonical_field GROUP BY field_name HAVING COUNT(*) > 1` | Zero rows |
| Every CF carries `function_code` | `SELECT * FROM contract.canonical_field WHERE function_code IS NULL` | Zero rows |
| Every `cc_field_mapping.cf_name` resolves to a CF row | `SELECT ccfm.cf_name FROM contract.cc_field_mapping ccfm LEFT JOIN contract.canonical_field cf ON cf.field_name = ccfm.cf_name WHERE cf.canonical_field_id IS NULL` | Zero rows |
| Every metric formula variable has a CF | The Step 6 verification query | Zero rows |

A check that returns rows identifies a violation; the violation is fixed before the chapter declares the session complete.

**Governing source.** The Contract Grammar.

## Boundary with Other Onboarding Chapters

| Chapter | Relationship |
|---|---|
| Business Field and Business Object Onboarding | BFs are source vocabulary; CFs are metric vocabulary. The two registries do not share names. The Canonical Contract translates between them via `cc_field_mapping`. |
| Source and Admission Contract Creation | No direct relationship; SC and AC operate on the source catalog, not on the CF registry |
| Observation Contract Creation | No direct relationship; OC operates on BF names (source vocabulary), not on CF names |
| Canonical Contract Creation | CC creation references CF names in `cc_field_mapping`; every referenced CF must exist before CC creation runs. CF Seeding is the prerequisite for CC creation |
| Metric Contract Creation | MC variables bind to CF names via `field_code`. Every input variable's `field_code` must be a registered CF |
| Metric Registration | The metric registration sequence registers `metric_definition` and `metric_formula` rows; the formula variable names are the demand signal CF Seeding extracts at Step 1 |

**Governing source.** Canonical Contract Creation; Metric Contract Creation; Metric Registration.

## Forbidden Patterns

The chapter records four forbidden patterns. They are forbidden because each one breaks the contract chain at a specific layer.

| Forbidden | Why |
|---|---|
| Auto-create CFs during CC creation | CFs are a contract primitive (DEC-d72560); they are explicitly registered through this chapter, not synthesized as a side effect of CC creation |
| Use BO-scoped names for CFs | CFs use metric vocabulary; the CC `cc_field_mapping` translates BF (BO-scoped) to CF (metric-scoped). A BO-prefixed CF collapses the distinction |
| Skip the verification step (Step 6) | Unverified CF seeding propagates gaps into CC creation (missing `cc_field_mapping` targets) and MC creation (unbound variables); the verification is the chapter's confirmation that the demand signal is satisfied |
| Seed CFs without a demand signal | Every CF is traceable to a metric formula variable or to a grain reference; speculative CFs accumulate as registry noise that later chapters cannot clean up |
| Backfill `semantic_family` directly via SQL | Bypasses the SDA gates and the evidence trail in `contract.certification_record`. All transitions go through the SDA state-transition endpoints (DEC-a17d0f §6) |
| Treat a non-overridable SDA gate (G2a, G5, G6, G7-BF, G8-CF, G10 Class-A) as overridable | The SDA's non-overridable gates have no override path. Operator remediation is to fix the inputs and re-submit (DEC-a17d0f §4) |
| Use AI panel consensus as an autonomous certifier | bc-ai is advisory evidence only per DEC-a17d0f §5. Human certifier acknowledgement is the lock; AI verdicts never transition state, never block, never certify |

**Governing source.** The Contract Grammar; Chain Completeness and Verdict; DEC-a17d0f; DEC-a49413.

## Drift Inventory

| Drift item | Form |
|---|---|
| Pre-D301 CFs | The platform contains CFs registered before DEC-d72560 formalized CF as the third primitive. Some pre-D301 entries carry incomplete metadata (`unit_type_code` missing, `subfunction_code` missing); they are valid for chain integrity but flagged for backfill |
| Output CFs lag behind output BFs | Output CFs (`{metric_short_name}_{property}`) are registered alongside output BF registration in Metric Contract Creation. Some early MCs registered output BFs without registering output CFs; the catch-up registration is queued |
| Constants are CF-shaped but not registered as CFs | A formula constant (e.g., `constant_percentage_multiplier`) is referenced in `metric_formula_variable` with `role: constant`. Constants are metric-local and do not require CF registration; the verification query at Step 6 excludes them by filtering `role IN ('input', 'output')` |
| Coverage drift between metric_formula_variable and canonical_field | The chapter's verification query is the authoritative coverage check. A coverage report that disagrees with the query result is using stale data |
| Existing pre-SDA CFs are uncertified | The pre-SDA CF corpus carries `status_code='draft'` and `semantic_family IS NULL`. Until SDA Phase 1 lands (DBCPs 1a–1f + bulk `draft → proposed` migration per DBCP-1d) and the bulk backfill (Step 10) is run, every new MC activation is refused by the Step 0 gate. The catalog cleanup is the unblocking item for resuming metric promotion (DEC-a17d0f §9) |
| D366 trace rows are all `not_applicable` | Cause is the same as above (no classified CFs → `CompatibilityFilterService` cannot fire any rule). Will self-clear as SDA certification fills `semantic_family` |

**Governing source.** The Contract Grammar; Audit and Activity Logging; DEC-a17d0f; DEC-a49413.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-a17d0f | **Governing authority** — Semantic Definitions Authority for BF / BO / CF / semantic_family identity, certification, provenance, supersession, aliases, Meaning-once. Defines the six-state lifecycle, gates G1–G10, override matrix, AI-as-advisory posture, and evidence schema |
| DEC-b7affa | Sibling amendment to SDA — adds gate G11 (BF↔CF semantic-family compatibility) at `cc_field_mapping` authoring time |
| DEC-d72560 | Establishes Canonical Field as the third contract primitive. **Superseded by DEC-a17d0f** on lifecycle / certification topics; kept here as historical context for the two-vocabulary model |
| DEC-9d1f4b | Establishes the shared dimension normalization rule that the CC onboarding service consumes; this chapter governs the CF naming the normalization expects |
| DEC-69f09e | Establishes the naming discipline this chapter applies to CF registration |
| DEC-a49413 | SDA Phase 1 implementation profile — specifies the multi-vendor advisory panel (Gemini Maker / OpenAI Checker / Claude Moderator) for CF `semantic_family` classification and the `cf_dedup` advisory for G2b. Sources advisory evidence under SDA §5; does not introduce new gates or alter the SDA lifecycle |

**Governing source.** Decisions: ADR Registry.

## References

- The Contract Grammar
- Business Vocabulary
- Metric Catalog
- Business Field and Business Object Onboarding
- Canonical Contract Creation
- Metric Contract Creation
- Metric Registration
- Chain Completeness and Verdict
- Data Model and Schema
- DEC-d72560: Canonical Field as 3rd contract primitive
- DEC-9d1f4b: Shared dimension normalization
- legacy-v2/docs/sops/cf-seeding-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding


