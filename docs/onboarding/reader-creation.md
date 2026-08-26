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

> **Bridging note.** Where this chapter refers to Business Field, Business Object, or Canonical Field, the semantic-identity role those primitives served is superseded by the **Business Concept Framework (BCF)** — the `concept_registry` schema (Entity / Characteristic / Business Concept), authored through governed ceremonies (AI panel + C5 operator-confirm + F3 write). The legacy `contract.business_field` / `contract.business_object` / canonical-field tables remain in use for OC/CC `field_selection` binding, so the mechanics described here stay valid for that purpose; for semantic identity — "what does this field mean?" — consult the BCF registry. Governing ADRs: DEC-02f5a9 (greenfield), DEC-61850f (adoption). See The Contract Grammar and The Object Model for the Registry model.

## Scope

This chapter records the governed sequence by which a **Reader definition** is created. A Reader is the platform's implementation of the UniBAT pattern (Universal Business-Aware Transactions Reader), the governed definition of the only authorized path through which source data enters BareCount. The Reader is a **definition**; the machine that executes it at admission is the **Runner** (DEC-0d5b39). This chapter authors the definition; it does not perform admission.

The chapter names the four-artifact runtime model (`runtime.reader`, `runtime.reader_flavor`, `runtime.reader_binding`, `runtime.reader_observation_binding`), the **Registry-Entity Reader convention** (DEC-0d5b39, which whole-supersedes DEC-129417 and amends the grouping doctrine of DEC-17112b) that anchors one non-archived Reader to one Business Concept Registry Entity (`admitted_entity_id`), with per-source Flavors identified by `(source_system, scenario)` and **per-entity** Observation- and Admission-Contract bindings, the governed authoring sequence over the `/api/reader-authoring/*` routes (the legacy D209 fast-track and D200 wizard are closed / non-operative), the five-reason chain-resolvability gate that governs Flavor activation, and the multi-flavor pattern for adding a second source system to an existing Reader. It records the boundary between Reader creation and the Connection (whose configuration is platform-held and tenant-owned, credentials external) that supplies runtime credentials. It records the as-built drift between the procedure and the platform's current Reader state.

This chapter does not redefine the UniBAT Reader pattern (Connectors and Readers), the admission and observation runtime acts the Runner performs (Admission and Observation), the Observation Contract the Runner applies (Observation Contract Creation), or the Connection that resolves credentials at runtime (Tenancy and Binding). It uses the **Business Concept Registry** vocabulary (a Business Concept and its properties, `entity.property`); the former Business Object / Business Field / Canonical Field identity is superseded (DEC-02f5a9).

**Governing source.** outline.md §4.6; Connectors and Readers; DEC-0d5b39.

## What the Procedure Produces

| Artifact | Persistent store | Created by |
|---|---|---|
| Reader identity (Registry-Entity-anchored: `admitted_entity_id`) | `runtime.reader` | `POST /api/reader-authoring/readers` |
| Reader Flavor (`(source_system, scenario)` specialization) | `runtime.reader_flavor` | `POST /api/reader-authoring/flavors` |
| Reader Binding (per-entity Admission-Contract pin: `(reader, flavor, source_entity, environment)` or the reader-level fallback with null `flavor_id`) | `runtime.reader_binding` | `POST /api/reader-authoring/admission-bindings` (flavor-specific) or `POST /api/readers/:readerId/bindings` (reader-level) |
| Reader Observation Binding (per-entity Observation-Contract pin: `(reader, flavor, source_entity, environment)`) | `runtime.reader_observation_binding` | `POST /api/reader-authoring/observation-bindings` |

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

## Governed Authoring Sequence

Reader authoring is governed. The ungoverned legacy surfaces (`POST /api/readers`, `POST /api/readers/create-from-oc`, `POST /api/readers/:id/flavors`, `PATCH .../flavors/:id`) are **closed** — each throws `ForbiddenException` (G2 / D560 / Unit A; recovery design F6). All creation flows through `POST /api/reader-authoring/*`. The sequence is: create the Reader (create-or-reuse per Entity), add a Flavor, bind the Observation and Admission Contracts per source entity, then activate the Flavor.

### 1. Create the Reader — `POST /api/reader-authoring/readers`

```
POST /api/reader-authoring/readers
{
  "admittedEntityId": "<active concept_registry.entity uuid>",
  "functionCode": "finance",
  "subfunctionCode": "accounts_receivable",
  "sourceCategoryCode": "enterprise",     // optional
  "displayName": "Journal Entry Reader",  // optional; defaults to the Entity canonical name
  "description": "..."                     // optional
}
```

`admittedEntityId` is validated against an active `concept_registry.entity` (violation → `422 R-C2`). The service **creates-or-reuses** per Entity: identity is an opaque `reader_uid`, deduplicated on the one-non-archived-Reader-per-`admitted_entity_id` constraint. `functionCode`/`subfunctionCode` are master-checked classification (snake_case), not identity. The DTO carries **no** `name`/`tags`/operational-config fields.

### 2. Add a Flavor — `POST /api/reader-authoring/flavors`

```
POST /api/reader-authoring/flavors
{
  "readerId": "<reader-uuid>",
  "sourceSystemCode": "odoo",           // snake_case (P-F2)
  "scenarioCode": "default",            // optional; defaults to "default" (P-F3)
  "displayName": "Odoo (production)",   // optional
  "connectionId": "<connection-uuid>",  // optional — the Connection reference
  "connectorId": "<connector-uuid>"     // optional — retained substrate debt (TSK-ccc82c)
}
```

The Flavor is identified by `(source_system, scenario)`; its name is server-derived (P-F7); one active Flavor per `(reader, source_system, scenario)` (violation → `409`). The **Connector is resolved through the Connection** (`connectionId` → `Connection.connector_id`); `connectorId` on the Flavor is retained compatibility substrate (TSK-ccc82c), not the governing authority. Both are optional in the DTO — see the gap note under Quality Gates.

### 3. Bind the Observation Contract per source entity — `POST /api/reader-authoring/observation-bindings`

```
POST /api/reader-authoring/observation-bindings
{ "readerId": "...", "flavorId": "...", "sourceEntity": "account.move",
  "environmentCode": "dev", "observationContractId": "<oc-uuid>", "versionCode": "1.0.0" }
```

Version-safe: at most one active OC pin per `(reader, flavor, source_entity, environment)`.

### 4. Bind the Admission Contract per source entity

Flavor-specific (governed authoring) — `POST /api/reader-authoring/admission-bindings` (**requires** `flavorId`):

```
POST /api/reader-authoring/admission-bindings
{ "readerId": "...", "flavorId": "...", "sourceEntity": "account.move",
  "environmentCode": "dev", "sourceContractId": "<admission-contract-uuid>", "versionCode": "1.0.0" }
```

`sourceContractId` carries the admission-contract id (historical column name). A conflicting occupied coordinate **refuses (`409`)**, never a silent no-op. The **reader-level fallback** (null-Flavor, coordinate `(reader, source_entity, environment)`) is exposed by the separately mounted `POST /api/readers/:readerId/bindings` surface — a distinct route with a distinct DTO from the authoring `admission-bindings` endpoint (which requires a Flavor). Its `CreateReaderBindingDto` uses different field names, and `readerId` is the path parameter:

```
POST /api/readers/<readerId>/bindings          // reader-level fallback: omit flavorId
{ "contractId": "<admission-contract-uuid>", "version": "1.0.0",
  "sourceEntity": "account.move", "environment": "dev" }
```

Omitting `flavorId` selects the reader-level `(reader, source_entity, environment)` scope; supplying it scopes the binding to that Flavor. Note the field names (`contractId`/`version`/`environment`) differ from the authoring endpoint’s (`sourceContractId`/`versionCode`/`environmentCode`).

### 5. Activate the Flavor — `POST /api/reader-authoring/flavors/:flavorId/activate`

```
POST /api/reader-authoring/flavors/<flavorId>/activate
{ "readerId": "<reader-uuid>", "environmentCode": "dev" }   // environmentCode defaults to "dev"
```

Activation is **fail-closed behind the chain-resolvability gate + a determinism gate**. A refusal returns `422` with the exact `breaks`; a determinism conflict returns `409` with the conflicting flavor ids. There is **no Reader-activation endpoint** — a Reader is live when it has at least one activatable/active Flavor (a Reader may be partially live: one Flavor active, another still draft). Flavors and Readers are retired via `POST /api/reader-authoring/flavors/:flavorId/archive` and `.../readers/:readerId/archive` (reversible via `archived_at`).

**Governing source.** Connectors and Readers; Reader Authoring (governed surface).

## Non-Operative Legacy Surfaces (closed)

These surfaces are recorded because prior procedure and UI reference them; they do not create governed state.

| Surface | State |
|---|---|
| `POST /api/readers` | Closed — `ForbiddenException` (G2 / D560 / Unit A). Use `POST /api/reader-authoring/readers` |
| `POST /api/readers/create-from-oc` (D209 fast-track) | Closed — hard-refusing stub (G2 / D560 / Unit A). No operative bulk fast-track exists; a governed bulk path is a tracked gap |
| `POST /api/readers/:id/flavors` | Closed — `ForbiddenException` (recovery design F6). Use `POST /api/reader-authoring/flavors` |
| `PATCH /api/readers/:id/flavors/:id` | Closed — legacy Flavor mutation refused. Use `.../flavors/:id/activate` and `.../archive` |
| D200 seven-step wizard | Not operative — the current bc-admin surface is a three-step OC/config/review UI that calls the closed `create-from-oc`; a governed Registry-Entity wizard is a gap, not a track |

**Governing source.** Reader Authoring; bc-core reader service (closed legacy handlers).

## Adding a Second Flavor (Multi-Source Reader)

When a Registry Entity needs data from multiple source systems, add a Flavor to the existing Reader rather than creating a new Reader:

1. Create the OC for the second source system's source entity (Observation Contract Creation).
2. `POST /api/reader-authoring/flavors` with the new `(sourceSystemCode, scenarioCode)`.
3. Bind the new OC (`observation-bindings`) and AC (`admission-bindings`) per source entity.
4. Activate the new Flavor (`.../activate`) once the chain-resolvability gate passes.

Both Flavors specialize the same Registry Entity for different source systems; the Runner executes the Reader definition for the selected Flavor and context. The Reader's Entity-anchored identity is unchanged; the Flavor count grows.

**Governing source.** Connectors and Readers.

## Quality Gates

The governed activation act enforces one gate set; other checks named in prior procedure are **not** enforced by the current governed surfaces and are recorded as gaps.

### Flavor activation — chain-resolvability gate (five contract-chain reasons)

`POST /api/reader-authoring/flavors/:flavorId/activate` is fail-closed behind the activation resolver. Per admitted source entity it requires all of the following, else the activation is refused (`422`, `breaks`) with the exact reason:

| # | Requirement | Break reason |
|---|---|---|
| 1 | An active `reader_binding` (flavor-specific or reader-level) admits the entity | `no_ac_binding` (see the as-built note) |
| 2 | The AC binding's SC/AC version resolves to an active version | `ac_version_unresolvable` |
| 3 | An active `reader_observation_binding` exists for the entity | `no_oc_binding` |
| 4 | The bound OC + version is active (not draft/superseded/archived) | `oc_inactive` |
| 5 | The OC→CC chain resolves for the bound OC | `oc_cc_chain_unresolvable` |

A determinism gate additionally refuses (`409`) an activation that would create a conflicting active `(reader, source_system, scenario)`.

**Reason #5 is a bounded proxy.** The current `oc_cc_chain_resolves` input checks for a non-empty `field_mappings` set, not full canonical-coverage. Treat it as a presence proxy, not a proof of complete OC→CC resolution.

**As-built gap — `no_ac_binding` is not currently emitted.** The five reasons above are the *pure resolver's* taxonomy. The live `ReaderChainResolutionService.buildFlavorInput` enumerates entities **only** from the flavor's AC bindings and sets `hasAcBinding: true` for each, so an entity with no AC binding (or a Flavor with no AC bindings at all) yields an empty entity set and `resolveFlavor` returns `activatable: false` with `breaks: []` — the mounted endpoint reports the refusal but cannot currently surface the `no_ac_binding` reason. Fixing the service's entity enumeration to also enumerate OC-only entities (so the exact reason is named, per the DEC-17112b fail-closed requirement) is a separately governed platform unit (TSK-5a1e6e), not part of this docs unit.

### Not enforced by the governed surface (gaps)

- **Connection/Connector resolvability** is **not** checked by the activation resolver. A Flavor with no `connectionId` (and thus no resolvable Connector) can pass activation. Establishing and checking the Connection context is a platform gap.
- **Reader-to-active-Registry-Entity integrity at activation** is not re-checked by the resolver (it is enforced once at creation via `R-C2`).
- **Generic Reader `PATCH`** is not chain-gated; there is no governed Reader-activation act.
- **`reader_name` uniqueness** and **operational-config validation** named in prior procedure are retired/absent: identity is the opaque `reader_uid` with per-`admitted_entity_id` dedup, and `CreateReaderDto` carries no operational config.

**Governing source.** Reader Authoring; reader chain-resolution (activation resolver).

## Forbidden Patterns

| Forbidden | Why |
|---|---|
| One Reader per subfunction (grouping many Entities) | A Reader is anchored to one Business Concept Registry Entity (DEC-0d5b39, one non-archived Reader per `admitted_entity_id`); the former subfunction grouping (DEC-129417 whole-superseded; DEC-17112b grouping amended) no longer holds |
| One Reader per source table | Source entities are per-entity bindings, not Readers |
| Create through the closed legacy surfaces | `POST /api/readers`, `create-from-oc`, and `/flavors` are closed (`ForbiddenException`); use the `/api/reader-authoring/*` governed routes |
| Make the Flavor the Connector authority | The Connector resolves through the Connection (`connectionId` → `Connection.connector_id`); the retained `reader_flavor.connector_id` is substrate debt (TSK-ccc82c), never the governing edge |
| Anchor a Reader to an inactive or absent Registry Entity | The governed `createReader` refuses (`422 R-C2`); a Reader must anchor to an active `concept_registry.entity` |

**Governing source.** Connectors and Readers; Reader Authoring.

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
| No governed bulk creation path | The legacy `create-from-oc` fast-track is closed (`ForbiddenException`); a governed bulk creation path over the `/api/reader-authoring/*` routes is a tracked gap. Creation is currently one governed call per artifact |
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

The Registry-Entity Reader convention is decided in DEC-0d5b39, which whole-supersedes DEC-129417 (per-subfunction consolidation) and amends the grouping doctrine of DEC-17112b (retaining its four-layer model, per-entity Observation Contract binding, chain-resolvability activation gate, policies P2-P6, and flavor topology P-F1..P-F8). The Business Concept Registry supersedes the former BO/BF/CF identity (DEC-02f5a9). The operational config presets (D043 fast-track, D200 wizard, D205, D209) are referenced in the v2 SOP; their record lives in `legacy-v2/docs/sops/reader-creation-sop.md`. The operative preset procedure is not part of this chapter (the D209/D200 surfaces that carried it are closed / non-operative; see Non-Operative Legacy Surfaces).

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
