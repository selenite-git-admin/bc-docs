---
id: reader-creation
order: 59
title: "Reader Creation"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-evaluation-boundaries, connectors-and-readers, admission-and-observation, observation-contract-creation, source-and-admission-contract-creation, business-field-and-business-object-onboarding, tenancy-and-binding, data-model-and-schema, api-surface]
governing_sources:
  - Connectors and Readers
  - Admission and Observation
  - Observation Contract Creation
governing_adrs:
  - DEC-b228ec (D018 Source Catalog and Integration as separate trees)
  - DEC-90faff (D069 Canonical-driven reader creation sequence; top-down assembly)
  - DEC-36d78f (D069 Reader observation schema; selective observation with standard field naming)
  - DEC-0d5b39 (Reader anchored to one Registry Entity; source-agnostic; Flavor=(source_system,scenario); Connector via Connection.connector_id; Reader-definition / Runner-machine split; supersedes DEC-129417; amends DEC-17112b)
  - DEC-02f5a9 (Business Concept Registry supersedes Business Object / Business Field / Canonical Field identity)
governing_sops:
  - legacy-v2/docs/sops/reader-creation-sop.md
errata_referenced: []
v2_sources:
  - sops/reader-creation-sop.md
  - system/platform/P05-runtime-definitions/reader/
diagrams: []
---

# Reader Creation

## Scope

This chapter records the governed sequence by which a **Reader definition** is created. A Reader is the platform's implementation of the UniBAT pattern (Universal Business-Aware Transactions Reader), the governed definition of the only authorized path through which source data enters BareCount. The Reader is a **definition**; the machine that executes it at admission is the **Runner** (DEC-0d5b39). This chapter authors the definition; it does not perform admission.

The chapter names the four-artifact runtime model (`runtime.reader`, `runtime.reader_flavor`, `runtime.reader_binding`, `runtime.reader_observation_binding`), the **Registry-Entity Reader convention** (DEC-0d5b39, which whole-supersedes DEC-129417 and amends the grouping doctrine of DEC-17112b) that anchors one non-archived Reader to one Business Concept Registry Entity (`admitted_entity_id`), with per-source Flavors identified by `(source_system, scenario)` and **per-entity** Observation- and Admission-Contract bindings, the three creation tracks (D209 fast-track from OC, manual via API, the seven-step wizard at D200), the seven chain integrity checks (CR-QG-RDR-003) that determine whether a Reader is operational, and the multi-flavor pattern for adding a second source system to an existing Reader. It records the boundary between Reader creation and the Connection (whose configuration is platform-held and tenant-owned, credentials external) that supplies runtime credentials. It records the as-built drift between the procedure and the platform's current Reader state.

This chapter does not redefine the UniBAT Reader pattern (Connectors and Readers), the admission and observation runtime acts the Runner performs (Admission and Observation), the Observation Contract the Runner applies (Observation Contract Creation), or the Connection that resolves credentials at runtime (Tenancy and Binding). It uses the **Business Concept Registry** vocabulary (a Business Concept and its properties, `entity.property`); the former Business Object / Business Field / Canonical Field identity is superseded (DEC-02f5a9).

**Governing source.** outline.md §4.6; Connectors and Readers; DEC-0d5b39.

## What the Procedure Produces

| Artifact | Persistent store | Created by |
|---|---|---|
| Reader identity (Registry-Entity-anchored: `admitted_entity_id`) | `runtime.reader` | Step 1 (or D209 fast-track) |
| Reader Flavor (`(source_system, scenario)` specialization) | `runtime.reader_flavor` | Step 2 (or D209 fast-track) |
| Reader Binding (per-entity Admission-Contract pin: `(reader, flavor, source_entity, environment)` or the reader-level fallback with null `flavor_id`) | `runtime.reader_binding` | Step 4 (or auto via D209) |
| Reader Observation Binding (per-entity Observation-Contract pin: `(reader, flavor, source_entity, environment)`) | `runtime.reader_observation_binding` | D209 fast-track / bind step |

Per the Registry-Entity convention (DEC-0d5b39), one non-archived Reader is anchored to one Business Concept Registry Entity (`admitted_entity_id`; the authoring service validates it against an active `concept_registry.entity`, error `R-C2`). Each source system is a Flavor `(source_system, scenario)` under that Reader; a Flavor observes **many** source entities, each pinned to its own Observation Contract through `reader_observation_binding`. Adding a second source system adds a Flavor; it does not add a new Reader.

**Governing source.** Connectors and Readers.

## The Four-Artifact Runtime Model

A Reader definition is decomposed across four runtime tables, each with a distinct concern.

| Table | Concern |
|---|---|
| `runtime.reader` | Identity: `admitted_entity_id` (the Business Concept Registry Entity; one non-archived Reader per Entity, across draft and active). `function_code`/`subfunction_code` are non-identity classification. Operational config (schedule, retry policy, circuit breaker, alerts) |
| `runtime.reader_flavor` | Source specialization: `(source_system, scenario)` — one active Flavor per `(reader, source_system, scenario)`. The Connector is resolved through the Connection (`connector_id`); the retained `reader_flavor.connector_id`/`connection_id` columns are current compatibility substrate pending retirement (DEC-0d5b39 D3; TSK-ccc82c). The deprecated `reader_flavor.observation_contract_id` is retired (0 rows) — OC pins live in `reader_observation_binding` |
| `runtime.reader_binding` | Per-entity Admission-Contract pin: `source_contract_id` (carries an admission-contract id, historical column name), `version_code`, `source_entity`, `environment_code`. Two active levels: flavor-specific `(reader, flavor, source_entity, environment)` and reader-level fallback `(reader, source_entity, environment)` with null `flavor_id` |
| `runtime.reader_observation_binding` | Per-entity Observation-Contract pin: `(reader, flavor, source_entity, environment)` → `(observation_contract_id, version_code)` |

The relationships:

```
Reader (1 per Registry Entity: admitted_entity_id -> concept_registry.entity)
  function_code + subfunction_code -> non-identity classification
  Flavor: odoo-default (source_system=odoo, scenario=default)
    Connector + credentials -> resolved through the Connection (connector_id)
    reader_observation_binding[account.move]  -> OC (field mappings for that entity)
    reader_observation_binding[account.move.line] -> different OC, same Flavor
    reader_binding[account.move] -> Admission Contract version + environment
  Flavor: sap-default (source_system=sap, scenario=default)
    reader_observation_binding[bkpf] -> SAP OC for the same Registry Entity
    reader_binding[bkpf] -> Admission Contract version + environment
```

A Flavor observes many source entities; each source entity has its own per-entity OC and AC bindings. No single Observation Contract is identified on the Flavor.

**Governing source.** Connectors and Readers.

## Prerequisites

| Precondition | Why it is required |
|---|---|
| Cognito authenticated session for a platform actor | Reader mutations are `@PlatformOnly()` JWT-guarded |
| Active Business Concept Registry Entity | The Reader anchors to `admitted_entity_id`; the authoring service refuses (`R-C2`) an entity that is not an active `concept_registry.entity` |
| Active OC per target source entity | Each `reader_observation_binding` pins an active OC for one source entity; without an OC the Runner cannot observe that entity |
| Active Connector reachable through a Connection | The Runner resolves the Connector via `Connection.connector_id`; the Connector is the protocol adapter |
| OC has field mappings | The OC body's `field_mappings[]` (each `source_field → business_concept_id`) is the observation instruction set; D431 CS-2 enforces field→concept integrity at OC authoring, so an OC that maps to a concept must have the concept declared observable |

If any prerequisite is missing, the prerequisite procedure runs first (Business Concept authoring for missing Registry Entities; Source and Admission Contract Creation for missing SCs/ACs; Observation Contract Creation for missing OCs).

**Governing source.** Connectors and Readers; Observation Contract Creation.

## Track A: D209 Fast-Track (Recommended When OC Exists)

The fast-track surface at `POST /api/readers/create-from-oc` is the primary path for bulk reader creation when OCs are already created. It runs the sub-steps in one call.

```
POST /api/readers/create-from-oc
{
  "observationContractId": "<oc-uuid>",
  "connectorId": "<connector-uuid>",
  "executionMode": "full",
  "backfillMode": "none",
  "schedulePreset": "daily-business",
  "retryStrategy": "conservative",
  "circuitBreaker": "standard",
  "alertPreset": "default"
}
```

The schedule presets:

| Preset | Cron | Cadence |
|---|---|---|
| `realtime` | `* * * * *` | Every minute |
| `hourly` | `0 * * * *` | Top of every hour |
| `daily-business` | `0 6 * * 1-5` | Weekdays 06:00 UTC |
| `daily-offpeak` | `0 2 * * *` | Daily 02:00 UTC |
| `weekly` | `0 6 * * 1` | Mondays 06:00 UTC |
| `monthly` | `0 6 1 * *` | First of month 06:00 UTC |

> Note: schedule presets are stored operational config. Under the accepted orchestration doctrine (DEC-01bd6b) admission runs on governed, version-pinned commands on the source axis, not as cron-as-trigger; the preset is the current mechanism pending that orchestration build.

The retry strategies:

| Strategy | Backoff posture | Use |
|---|---|---|
| `conservative` | Bounded exponential retry profile | Default for enterprise readers |
| `aggressive` | Higher-attempt linear retry profile | Fast retry when source throttling risk is low |
| `none` | No retry | Use only when retries would be unsafe |

The circuit breaker presets:

| Preset | Open threshold | Cooldown posture |
|---|---|---|
| `sensitive` | Low failure threshold | Short cooldown |
| `standard` | Balanced failure threshold | Standard cooldown |
| `relaxed` | Higher failure threshold | Longer cooldown |

Default recommendation for enterprise readers: `daily-business` schedule, `conservative` retry, `standard` circuit breaker.

The service creates one `runtime.reader` row (draft, anchored to the OC's Registry Entity), one `runtime.reader_flavor` row (draft) for the source `(source_system, scenario)`, and the per-entity `reader_observation_binding` pinning the OC for the source entity.

**Governing source.** Connectors and Readers.

## Track B: Manual via API

For one-off reader creation or fine-grained control, the actor calls the per-artifact endpoints directly:

```
POST /api/readers
{
  "name": "<entity-slug>-reader",
  "displayName": "<Registry Entity Display Name> Reader",
  "admittedEntityId": "<concept_registry.entity uuid>",
  "sourceCategory": "enterprise",
  "function": "<function_code>",
  "subfunction": "<subfunction_code>",
  "description": "Reader for <Registry Entity name>",
  "tags": ["<entity>"]
}
```

`function`/`subfunction` are non-identity classification; the identity is `admittedEntityId`.

Then add a Flavor for a source `(source_system, scenario)`:

```
POST /api/readers/<readerId>/flavors
{
  "name": "<source_system>-<scenario>",
  "displayName": "<Registry Entity> -- <System Name>",
  "sourceSystem": "<source_system>",
  "scenario": "default",
  "status": "draft"
}
```

Pin the Observation Contract for a source entity (per-entity binding):

```
POST /api/readers/<readerId>/bindings   (observation binding, per source entity)
{
  "flavorId": "<flavor-uuid>",
  "sourceEntity": "account.move",
  "environmentCode": "dev",
  "observationContractId": "<oc-uuid>",
  "versionCode": "1.0.0"
}
```

Pin the Admission Contract for the same source entity (flavor-specific, or reader-level with `flavorId: null`):

```
POST /api/readers/<readerId>/bindings   (admission binding, per source entity)
{
  "flavorId": "<flavor-uuid | null for reader-level fallback>",
  "sourceContractId": "<admission-contract-uuid>",
  "versionCode": "1.0.0",
  "sourceEntity": "account.move",
  "environmentCode": "dev"
}
```

The Connector and credentials are supplied through the Connection at runtime; they are not on the Reader or Flavor.

**Governing source.** Connectors and Readers.

## Track C: Reader Constructor Wizard (D200)

The seven-step wizard orchestrates the full chain from Registry Entity selection through reader activation:

| Step | Action |
|---|---|
| 1 | Select Business Concept Registry Entity |
| 2 | Select Canonical Contract |
| 3 | Select or create Observation Contract (per source entity) |
| 4 | Select Connector (resolved through the Connection) |
| 5 | Select Source Version |
| 6 | Create Reader plus Flavor and per-entity bindings (calls D209 fast-track internally) |
| 7 | Review and Activate |

The wizard is the appropriate path when OCs do not yet exist and guided creation is preferred. For bulk operations where OCs exist, Track A is faster.

**Governing source.** Connectors and Readers.

## Activation

Readers are created as `draft`. The actor activates the Flavor first (after CR-QG-RDR-002 readiness checks pass) and then the Reader (once the Reader has at least one active Flavor):

```
PATCH /api/readers/<readerId>/flavors/<flavorId>
{ "status": "active" }

PATCH /api/readers/<readerId>
{ "status": "active" }
```

Activation requires CR-QG-RDR-003 (the seven chain integrity checks below) to pass. A draft Flavor or a Flavor with no active per-entity OC binding cannot be activated.

**Governing source.** Connectors and Readers.

## Adding a Second Flavor (Multi-Source Reader)

When a Registry Entity needs data from multiple source systems, the actor adds a Flavor to the existing Reader rather than creating a new Reader. The procedure:

1. Create the OC for the second source system's source entity (Observation Contract Creation).
2. Add a Flavor `(source_system, scenario)` to the existing Reader.
3. Pin the new OC to the new Flavor per source entity via `reader_observation_binding`, and pin the Admission Contract via `reader_binding`.
4. Activate the new Flavor when readiness checks pass.

Both Flavors admit the same Registry Entity (same Business Concept properties) but read from different source systems. The Reader's Entity-anchored identity remains; the Flavor count grows.

**Governing source.** Connectors and Readers.

## Quality Gates

The Reader creation enforces three classes of gate.

### CR-QG-RDR-001: Reader Creation Gate

| # | Check |
|---|---|
| 1 | Entity anchored: `admitted_entity_id` references an active Business Concept Registry Entity (`R-C2`) |
| 2 | Name unique: no existing Reader with the same `reader_name` |
| 3 | Function valid: `function_code` matches a registered business function (classification only) |
| 4 | Operational config valid: schedule cron is parseable; retry config has valid values |

### CR-QG-RDR-002: Flavor Readiness Gate

| # | Check |
|---|---|
| 1 | OC pinned: at least one active `reader_observation_binding` pins an active OC for a source entity |
| 2 | Connector resolvable: the Connection resolves an active Connector (`connector_id`) |
| 3 | AC pinned: an active `reader_binding` (flavor-specific or reader-level fallback) pins an active Admission Contract for the source entity |
| 4 | Status active: Flavor `status_code` is `active` (after the activation step) |

### CR-QG-RDR-003: Reader Chain Integrity (Seven Checks)

A Reader is chain-complete when all seven checks pass (mirroring the runtime resolver's break-reason taxonomy):

| # | Check |
|---|---|
| 1 | Entity anchored: `reader.admitted_entity_id` is non-null and references an active Registry Entity |
| 2 | Registry Entity active: the anchored `concept_registry.entity` is active (not archived) |
| 3 | Has active flavor: at least one `reader_flavor` with `status: active` |
| 4 | Flavor has OC binding: an active `reader_observation_binding` exists for the entity (else resolver `no_oc_binding`) and the OC/version is active (else `oc_inactive`) |
| 5 | Connector resolvable: the Connection resolves an active Connector |
| 6 | Has AC binding: an active `reader_binding` exists for the entity (else `no_ac_binding`) and its AC/SC version resolves active (else `ac_version_unresolvable`) |
| 7 | OC→CC chain resolves: the bound OC's canonical chain resolves (else `oc_cc_chain_unresolvable`) |

Only chain-complete Readers can execute Admission Runs; every break is a named, fail-closed resolver reason, not a silent miss. The checks are run on demand via the integrity surface and on every Reader status change.

**Governing source.** Connectors and Readers; Quality Gates and Chain Integrity.

## Forbidden Patterns

The chapter records five forbidden patterns. Each one breaks the platform's UniBAT discipline at a specific layer.

| Forbidden | Why |
|---|---|
| One Reader per subfunction (grouping many Entities) | A Reader is anchored to one Business Concept Registry Entity (DEC-0d5b39, one non-archived Reader per `admitted_entity_id`); the former subfunction grouping (DEC-129417 whole-superseded; DEC-17112b grouping amended) no longer holds |
| One Reader per source table | Source entities are per-entity bindings, not Readers |
| Skip OC binding | A Reader with no active `reader_observation_binding` for an entity cannot admit it (resolver `no_oc_binding`); the per-entity OC binding is the contract-bearing layer |
| Hardcode credentials in Reader or Flavor config | Connector and credentials are resolved through the Connection (configuration platform-held, tenant-owned, credentials external); they are not on the Reader or Flavor |
| Anchor a Reader to an inactive or absent Registry Entity | The authoring service refuses (`R-C2`); a Reader must anchor to an active `concept_registry.entity` |

**Governing source.** Connectors and Readers; Tenancy and Binding.

## Boundary with Other Onboarding Chapters

| Chapter | Relationship |
|---|---|
| Source and Admission Contract Creation | Provides the SC/AC the `reader_binding` references |
| Business Concept authoring | Provides the Registry Entity the Reader anchors to (`admitted_entity_id`) |
| Observation Contract Creation | Provides the OC the `reader_observation_binding` pins per source entity |
| Canonical Contract Creation | Independent; the Reader does not bind a CC; the CC consumes SOs the Runner produces (D431 O↔C ties CC concepts back to active OC observability) |
| Metric Contract Creation | Independent; the MC consumes COs that later evaluation produces from SOs |
| Tenant Onboarding | The Connection (platform-held config, tenant-owned, external credentials) is resolved for the Reader Flavor at runtime; the Reader definition is platform-scoped |

**Governing source.** Source and Admission Contract Creation; Observation Contract Creation; Tenant Onboarding.

## Drift Inventory

| Drift item | Form |
|---|---|
| `create-from-oc` derives Reader name from OC display name | The fast-track surface produces Reader names that may include the source-entity component. The actor renames via PATCH if entity-anchoring discipline requires; recorded as a known cosmetic drift |
| Flavor Connector/Connection columns retained | `reader_flavor.connector_id`/`connection_id` remain live columns (compatibility substrate) even though `Connection.connector_id` is the decided sole authority; retirement tracked under TSK-ccc82c |
| Connector inventory is small | The readiness-baseline platform Connector list is short. Other source families are connector gaps recorded in Connectors and Readers |
| Activation gate failures surface at bind/activation | A Flavor with no active per-entity OC binding can be created in `draft`; the break surfaces at activation as a named resolver reason (`no_oc_binding`), not at create. The actor reads the chain integrity report to identify the missing binding |
| qa-bench Reader provisioning is aspirational | Test Bench Module writes evidence into the addressed tenant in the readiness baseline rather than a dedicated qa-bench tenant; the qa-bench Reader provisioning is a queued surface in Synthetic Data and Testing |

**Governing source.** Connectors and Readers; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-b228ec | Establishes Source Catalog and Integration as separate trees; the Reader bridges them via Flavor + per-entity bindings |
| DEC-90faff | Establishes the canonical-driven reader creation sequence (top-down assembly) |
| DEC-36d78f | Establishes the Reader observation schema with selective observation and standard field naming |

The Registry-Entity Reader convention is decided in DEC-0d5b39, which whole-supersedes DEC-129417 (per-subfunction consolidation) and amends the grouping doctrine of DEC-17112b (retaining its four-layer model, per-entity Observation Contract binding, chain-resolvability activation gate, policies P2-P6, and flavor topology P-F1..P-F8). The Business Concept Registry supersedes the former BO/BF/CF identity (DEC-02f5a9). The operational config presets (D043 fast-track, D200 wizard, D205, D209) are referenced in the v2 SOP; their record lives in `legacy-v2/docs/sops/reader-creation-sop.md` and in this chapter.

**Governing source.** Decisions: ADR Registry.

## References

- Connectors and Readers
- Admission and Observation
- Sources and the Catalog
- Source Registration
- Observation Contract Creation
- Source and Admission Contract Creation
- Tenant Onboarding
- Tenancy and Binding
- Quality Gates and Chain Integrity
- Data Model and Schema
- API Surface
- DEC-b228ec: Source Catalog and Integration as separate trees
- DEC-90faff: Canonical-driven reader creation sequence
- DEC-36d78f: Reader observation schema
- DEC-0d5b39: The Reader Model and the Runtime Ecosystem
- DEC-02f5a9: Business Concept Registry
- legacy-v2/docs/sops/reader-creation-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding
