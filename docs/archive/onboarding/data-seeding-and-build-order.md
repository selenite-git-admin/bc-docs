---
id: data-seeding-and-build-order
order: 62
title: "Data Seeding and Build Order"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, contract-chain-assembly, source-registration, seed-catalog-management, business-field-and-business-object-onboarding, canonical-field-seeding, source-and-admission-contract-creation, observation-contract-creation, canonical-contract-creation, metric-contract-creation, reader-creation]
governing_sources:
  - The Contract Grammar
  - Contract Chain Assembly
governing_adrs:
  - DEC-da4c51 (D068 Contract trust chain; lifecycle stages with upward trust propagation)
governing_sops:
  - legacy-v2/docs/sops/data-seeding-sop.md
errata_referenced: []
v2_sources:
  - sops/data-seeding-sop.md
diagrams: []
---

# Data Seeding and Build Order

## Scope

This chapter records the governed sequence by which the contract chain is built end-to-end for the first time, after a clean-slate revert, when onboarding a new source system, or when adding a new business function's contracts. It names the eleven build levels (master data and meta-schemas at level 0; through Connectors at level 10), the dependency graph that orders them (every level depends on the levels before it), the verification gates run between levels (D268 Rule 8: independent query after every mutation), the one-then-many discipline (prove one complete chain end-to-end before scaling), and the rollback procedures per layer plus full session. It records the boundary between Data Seeding and Build Order and the per-artifact creation chapters that produce each layer's individual artifacts. It records the as-built drift between the procedure and the platform's current build sequence.

This chapter does not redefine the per-artifact creation chapters (Source Registration; Seed Catalog Management; Business Field and Business Object Onboarding; Canonical Field Seeding; Source and Admission Contract Creation; Observation Contract Creation; Canonical Contract Creation; Metric Contract Creation; Reader Creation; Metric Registration; MC Chain Integrity). This chapter sequences them.

**Governing source.** outline.md §4.6; Contract Chain Assembly.

## What the Procedure Produces

| Artifact | Form |
|---|---|
| One end-to-end chain that demonstrates the build sequence | A chosen Business Object whose contract chain is operational from source table to metric snapshot |
| Per-level baseline counts | Recorded at session start and at each build level; the chapter calls this the chain's stocktake |
| Verification queries per level | The SQL the actor runs after each mutation to confirm the row landed; recorded in the session log |
| DevHub session checkpoints per BO | One checkpoint after each BO's chain reaches the final layer |

The procedure produces a chain, not a contract artifact directly. The artifacts at each layer are produced by the chapters that govern them; this chapter sequences those chapters.

**Governing source.** Contract Chain Assembly.

## Governing Discipline (D268)

Every step in this chapter operates under D268 (Session Discipline). Five rules apply at every level:

| Rule | Form |
|---|---|
| Rule 1: No bulk generation | Each OC and field map is built individually with verified mappings; no scripts that generate many at once without per-item verification |
| Rule 4: One-then-many | Prove one complete chain works end-to-end before scaling to a second chain |
| Rule 6: Checkpoint per mutation | Save a DevHub checkpoint after each data change |
| Rule 8: Proof before proceeding | Independent query after every INSERT (the script's success log is not proof; an independent SELECT is) |
| Rule 9: Script output is not verification | Trust a separate SELECT, not the script's stdout |

The chapter records these as the procedure's running constraint. A step that violates them produces output the chapter does not admit.

**Governing source.** The Contract Grammar.

## The Eleven Build Levels

The build sequence is a strict dependency graph. Each level depends on every level before it; no skipping.

| Level | Layer | Per-artifact chapter |
|---|---|---|
| 0 | Master data plus meta-schemas (independent) | (Platform infrastructure; not chapter-governed) |
| 1 | Source Systems plus Metric Definitions | Source Registration; Metric Registration |
| 2 | Source Versions plus Business Objects | Source Registration; Business Field and Business Object Onboarding |
| 3 | Source Modules plus Business Fields plus Canonical Fields | Source Registration; Business Field and Business Object Onboarding; Canonical Field Seeding |
| 4 | Canonical Contracts plus `cc_field_mapping` (BF to CF) | Canonical Contract Creation |
| 5 | Source Objects plus Canonical Mappings plus Metric Bindings | Source Registration; Canonical Contract Creation; Metric Contract Creation |
| 6 | Source Fields plus Source Contracts plus Admission Contracts | Source Registration; Source and Admission Contract Creation |
| 7 | Observation Contracts plus Field Maps (the bridge layer) | Observation Contract Creation |
| 8 | Readers plus Flavors plus Bindings (runtime infrastructure) | Reader Creation |
| 9 | Intervention Contracts (action layer) | (Per-artifact chapter not in this section) |
| 10 | Connectors (connection infrastructure) | (Per-artifact chapter not in this section) |

The dependency note: levels 0 to 6 define structure. Level 7 creates the semantic bridge between source data and business meaning; without level 7 the chain has no place where source vocabulary becomes business vocabulary. Level 8 wires the runtime that executes the chain. Levels below 7 are mechanical; level 7 requires domain knowledge.

**Governing source.** Contract Chain Assembly; The Contract Grammar.

## Step SOP-1: Verify Baseline (Always Run First)

Every seeding session starts with a baseline count. The actor runs:

```
SELECT 'source_contract' as family, count(*) FROM contract.source_contract
UNION ALL SELECT 'admission_contract',     count(*) FROM contract.admission_contract
UNION ALL SELECT 'observation_contract',   count(*) FROM contract.observation_contract
UNION ALL SELECT 'canonical_contract',     count(*) FROM contract.canonical_contract
UNION ALL SELECT 'metric_contract',        count(*) FROM contract.metric_contract
UNION ALL SELECT 'intervention_contract',  count(*) FROM contract.intervention_contract
ORDER BY family;

SELECT 'business_object' as entity,        count(*) FROM contract.business_object
UNION ALL SELECT 'business_field',         count(*) FROM contract.business_field
UNION ALL SELECT 'observation_field_map',  count(*) FROM contract.observation_field_map
UNION ALL SELECT 'reader',                 count(*) FROM runtime.reader
UNION ALL SELECT 'reader_binding',         count(*) FROM runtime.reader_binding
UNION ALL SELECT 'reader_flavor',          count(*) FROM runtime.reader_flavor
UNION ALL SELECT 'metric_binding',         count(*) FROM metric.metric_binding
ORDER BY entity;
```

Counts are saved in the session plan. Any deviation from a prior session's expected baseline is investigated before proceeding. The chapter does not hardcode count expectations; counts change every session, and the chapter's discipline is to read the live state, not to assume one.

**Governing source.** The Contract Grammar.

## Step SOP-2: Pick One Business Object to Wire End-to-End

The actor selects one BO that has a Canonical Contract, certified Business Fields, at least one Metric Contract bound to it via `metric_binding`, and Source Contracts covering source objects with relevant fields. The chapter recommends the discovery query:

```
SELECT bo.business_object_id, bo.business_object_name, bo.function_code,
       (SELECT count(*) FROM contract.business_object_field bof
        WHERE bof.business_object_id = bo.business_object_id) as bf_count,
       (SELECT count(*) FROM contract.canonical_contract cc
        WHERE cc.object_id = bo.business_object_id) as cc_count,
       (SELECT count(*) FROM metric.metric_binding mb
        JOIN contract.canonical_contract cc ON cc.canonical_contract_id = mb.canonical_contract_id
        WHERE cc.object_id = bo.business_object_id) as mc_bound
FROM contract.business_object bo
WHERE bo.archived_at IS NULL
ORDER BY bf_count DESC
LIMIT 10;
```

The actor records the choice in the session plan: BO name, function, why selected, expected chain. D268 Rule 4 (one-then-many) requires this step; a complete chain for one BO proves the pattern before scaling.

**Governing source.** The Contract Grammar.

## Step SOP-3: Map Source Fields to Business Fields (Design Step; No DB Writes)

This is the step that fails most often when skipped. Field mapping requires domain knowledge. The chapter records the design step explicitly so it happens before any DB writes.

The actor lists the BO's BFs (`SELECT ... FROM contract.business_object_field`), finds the source objects that feed the BO (`SELECT ... FROM contract.source_contract WHERE function_code = ...`), lists each source object's fields, and writes the mapping table:

| Business Field | Source Object | Source Field | Mapping Type | Notes |
|---|---|---|---|---|
| `bf_posting_date` | BSEG | BUDAT | direct | |
| `bf_amount_local` | BSEG | DMBTR | direct | |
| `bf_currency_code` | BSEG | WAERS | direct | |
| `bf_company_code` | BKPF | BUKRS | join(BELNR) | |

The actor reviews the mapping with the user and gets explicit approval before any DB writes. A mapping that has not been reviewed is a mapping the chapter does not admit.

**Governing source.** Observation Contract Creation.

## Step SOP-4 to SOP-5: Create OC and Field Maps (One at a Time)

The actor creates the Observation Contract per Observation Contract Creation. Each `observation_field_map` row is created individually; the chapter does not admit a script that bulk-inserts all field maps without per-row verification.

After each insert, the actor runs the verification SELECT and confirms the row landed. After all field maps for the OC are inserted, the actor runs the completeness check (count mapped vs total BFs for the BO) and confirms the count matches the design table.

**Governing source.** Observation Contract Creation.

## Step SOP-6: Wire Reader Infrastructure

The actor creates the Reader Flavor and Binding per Reader Creation. Each artifact is verified after creation. The actor runs the chain trace SQL that joins `runtime.reader_binding` to `runtime.reader_flavor` to `runtime.reader` to `contract.observation_contract` to `contract.source_contract` and confirms every column has a value.

**Governing source.** Reader Creation.

## Step SOP-7: Validate the Complete Chain (End-to-End Proof)

The actor runs the full chain trace for the chosen BO:

```
WITH chain AS (
  SELECT
    bo.business_object_name,
    cc.canonical_contract_name,
    mc.metric_contract_name,
    md.metric_definition_name,
    oc.observation_contract_name,
    sc.source_contract_name,
    ac.admission_contract_name,
    r.reader_name,
    rf.flavor_name,
    (SELECT count(*) FROM contract.observation_field_map ofm
     WHERE ofm.observation_contract_id = oc.observation_contract_id) as field_maps
  FROM contract.business_object bo
  JOIN contract.canonical_contract cc ON cc.object_id = bo.business_object_id
  JOIN metric.metric_binding mb ON mb.canonical_contract_id = cc.canonical_contract_id
  JOIN contract.metric_contract mc ON mc.metric_contract_id = mb.metric_contract_id
  JOIN metric.metric_definition md ON md.metric_definition_id = mc.metric_definition_id
  LEFT JOIN contract.observation_contract oc ON oc.function_code = bo.function_code
  LEFT JOIN contract.source_contract sc ON sc.source_contract_id = oc.source_contract_id
  LEFT JOIN contract.admission_contract ac ON ac.source_object_id = sc.source_object_id
  LEFT JOIN runtime.reader_binding rb ON rb.observation_contract_id = oc.observation_contract_id
  LEFT JOIN runtime.reader_flavor rf ON rf.reader_flavor_id = rb.reader_flavor_id
  LEFT JOIN runtime.reader r ON r.reader_id = rf.reader_id
  WHERE bo.business_object_id = '<bo_id>'
)
SELECT * FROM chain LIMIT 20;
```

Success criterion: every column has a value (no NULLs in the OC, SC, AC, or Reader columns); the field_maps count matches the design table. Any NULL identifies an incomplete chain; the actor returns to the appropriate step before proceeding.

**Governing source.** Chain Completeness and Verdict.

## Step SOP-8: Scale to the Next BO

After SOP-7 proves one complete chain, the actor repeats SOP-2 through SOP-7 for the next BO. The chapter forbids batch mode: each BO's chain is built individually with the verification gates run per BO.

After every five BOs, the actor runs a summary check:

```
SELECT
  count(DISTINCT oc.observation_contract_id) as ocs,
  count(DISTINCT ofm.observation_field_map_id) as field_maps,
  count(DISTINCT rb.reader_binding_id) as reader_bindings
FROM contract.observation_contract oc
LEFT JOIN contract.observation_field_map ofm ON ofm.observation_contract_id = oc.observation_contract_id
LEFT JOIN runtime.reader_binding rb ON rb.observation_contract_id = oc.observation_contract_id;
```

A DevHub checkpoint is saved after each BO's chain completes.

**Governing source.** The Contract Grammar.

## Rollback

The chapter records two rollback procedures.

**Per-OC rollback (one OC is wrong).** The actor deletes field maps first (FK dependency), then reader bindings, then the OC itself:

```
DELETE FROM contract.observation_field_map WHERE observation_contract_id = '<oc_id>';
DELETE FROM runtime.reader_binding         WHERE observation_contract_id = '<oc_id>';
DELETE FROM contract.observation_contract  WHERE observation_contract_id = '<oc_id>';
```

**Full-session rollback (the entire session's work is wrong).** The actor counts what the session added by `created_at` range and deletes in dependency order:

```
SELECT count(*) FROM contract.observation_contract  WHERE created_at > '<session_start>';
SELECT count(*) FROM contract.observation_field_map WHERE created_at > '<session_start>';
SELECT count(*) FROM runtime.reader_binding         WHERE created_at > '<session_start>';
SELECT count(*) FROM runtime.reader_flavor          WHERE created_at > '<session_start>';

DELETE FROM runtime.reader_binding         WHERE created_at > '<session_start>';
DELETE FROM runtime.reader_flavor          WHERE created_at > '<session_start>';
DELETE FROM contract.observation_field_map WHERE created_at > '<session_start>';
DELETE FROM contract.observation_contract  WHERE created_at > '<session_start>';
```

A rollback at the chain level is destructive. The chapter requires the actor to confirm the session's start timestamp and the affected count before each delete.

**Governing source.** Audit and Activity Logging.

## Anti-Patterns (D268 Violations)

The chapter records five anti-patterns. Each is a violation of D268 the procedure does not admit.

| Anti-pattern | Why it fails |
|---|---|
| Bulk-generating OCs from a script | Each OC needs verified field mappings; bulk generation produces unverified mappings that propagate as L4 chain gaps |
| Creating field maps without knowing the source fields | "Derive later" produces fake-green chain status that conceals real gaps |
| Skipping SOP-3 (the design step) | Going straight from BO selection to INSERT skips the field-mapping design that requires domain knowledge |
| Running SOP-8 before SOP-7 succeeds | Scaling an unproven pattern propagates the unverified chain pattern across many BOs |
| Trusting AI-generated field mappings without review | AI suggests; the human approves; the AI's confidence is not the chain's authority |

**Governing source.** The Contract Grammar.

## Boundary with Other Onboarding Chapters

| Chapter | Relationship |
|---|---|
| Source Registration | Provides the catalog rows the build sequence consumes at level 1 |
| Seed Catalog Management | Provides the curated reference data Source Registration consumes |
| Business Field and Business Object Onboarding | Produces the BFs and BOs the build sequence consumes at levels 2 and 3 |
| Canonical Field Seeding | Produces the CFs the build sequence consumes at level 3 |
| Source and Admission Contract Creation | Produces the SC and AC pairs the build sequence consumes at level 6 |
| Observation Contract Creation | Produces the OCs and field maps the build sequence consumes at level 7 |
| Canonical Contract Creation | Produces the CCs and Canonical Mappings the build sequence consumes at levels 4 and 5 |
| Metric Contract Creation | Produces the MCs the build sequence consumes at level 5 |
| Reader Creation | Produces the Readers, Flavors, and Bindings the build sequence consumes at level 8 |
| Metric Registration | Produces the metric definitions Metric Contract Creation consumes |
| MC Chain Integrity | Operates on the chain after the build sequence completes; the diagnostic at Step SOP-7 anticipates the same checks at a chain-status level |

**Governing source.** The per-artifact onboarding chapters.

## Drift Inventory

| Drift item | Form |
|---|---|
| Greenfield re-seeds happen periodically | When a major architectural change lands (new contract primitive, new gate), the chain is sometimes greenfield-rebuilt; this chapter is the procedure for the rebuild, not for routine ongoing seeding |
| Chain status is the runtime view, not the seeding view | The chain status SSOT (Chain Completeness and Verdict) reads the current state; this chapter writes the state via the per-artifact creation chapters. The seeding view is a build sequence; the chain status view is a reflection |
| Anti-patterns are tempting at scale | The chapter forbids batch generation; under deadline pressure, the temptation to script bulk creates real gaps. The chapter records the temptation explicitly so future actors stop at the temptation rather than at the consequence |
| Per-level dependency completeness | A real seeding session may discover that a level-3 CF is missing during level-4 CC creation; the procedure routes back to Canonical Field Seeding, then resumes at level 4. The dependency graph is strict but the per-level walkback is part of the procedure |

**Governing source.** Chain Completeness and Verdict; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-da4c51 | Establishes the contract trust chain with lifecycle stages and upward trust propagation; the build sequence is the operational form of trust propagation upward through the levels |

The session-discipline rules (D268) referenced throughout this chapter live in `legacy-v2/docs/decisions/ADR-ebf0b4.md`; new ADR files for the seeding-specific anti-patterns may be filed if the policies are restated outside the v2 SOP location.

**Governing source.** Decisions: ADR Registry.

## References

- The Contract Grammar
- Contract Chain Assembly
- Chain Completeness and Verdict
- Source Registration
- Seed Catalog Management
- Business Field and Business Object Onboarding
- Canonical Field Seeding
- Source and Admission Contract Creation
- Observation Contract Creation
- Canonical Contract Creation
- Metric Contract Creation
- Reader Creation
- Metric Registration
- MC Chain Integrity
- Audit and Activity Logging
- DEC-da4c51: Contract trust chain
- legacy-v2/docs/sops/data-seeding-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding


