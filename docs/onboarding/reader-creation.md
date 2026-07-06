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

This chapter records the governed sequence by which a Reader is created. The Reader is the platform's implementation of the UniBAT pattern (Universal Business-Aware Transactions Reader), the only authorized path through which source data enters BareCount. The chapter names the three-table model (`runtime.reader`, `runtime.reader_flavor`, `runtime.reader_binding`), the subfunction-scoped Reader convention (D312 in the v2 SOP shorthand) that groups all BOs in a subfunction under one Reader with one Flavor per (source system, BO) pair, the three creation tracks (D209 fast-track from OC, manual via API, the seven-step wizard at D200), the seven chain integrity checks (CR-QG-RDR-003) that determine whether a Reader is operational, and the multi-flavor pattern for adding a second source system to an existing Reader. It records the boundary between Reader creation and the Tenant Connection that supplies runtime credentials. It records the as-built drift between the procedure and the platform's current Reader state.

This chapter does not redefine the UniBAT Reader pattern (Connectors and Readers), the admission and observation runtime acts (Admission and Observation), the OC the Reader executes (Observation Contract Creation), or the Tenant Connection that supplies credentials at runtime (Tenancy and Binding).

**Governing source.** outline.md §4.6; Connectors and Readers.

## What the Procedure Produces

| Artifact | Persistent store | Created by |
|---|---|---|
| Reader identity (subfunction-scoped) | `runtime.reader` | Step 1 (or D209 fast-track) |
| Reader Flavor (per source system, per BO) | `runtime.reader_flavor` | Step 2 (or D209 fast-track) |
| Reader Binding (concrete source entity, environment) | `runtime.reader_binding` | Step 4 (or auto via D209) |
| OC back-reference | `contract.observation_contract.reader_id` | D209 fast-track only |

Per the subfunction-scoped convention, one Reader covers all BOs in a subfunction. Each (source system, BO) pair is a Flavor under that Reader. Adding a second source system for a BO adds a Flavor; it does not add a new Reader.

**Governing source.** Connectors and Readers.

## Three-Table Model

The Reader is decomposed across three tables, each with a distinct concern.

| Table | Concern |
|---|---|
| `runtime.reader` | Identity: function code, subfunction code, operational config (schedule, retry policy, circuit breaker, alerts) |
| `runtime.reader_flavor` | Source adapter: source system reference, BO reference, Connector reference, OC reference, observation schema |
| `runtime.reader_binding` | Concrete source entity: SC reference, version code, source entity (table or endpoint), environment code |

The relationships:

```
Reader (1 per subfunction)
  function_code + subfunction_code -> domain scope
  Flavor: ecc-receivable-hdr (SAP ECC, BO: receivable_hdr)
    observation_contract_id -> OC (field mappings for this BO)
    connector_id -> extraction protocol (e.g., OData V2)
    Binding -> Source Contract + BSID + environment
  Flavor: ecc-receivable-line (SAP ECC, BO: receivable_line)
    observation_contract_id -> different OC, same subfunction
    Binding -> Source Contract + BSID line items + environment
  Flavor: tally-receivable-hdr (Tally, BO: receivable_hdr)
    observation_contract_id -> Tally OC for same BO
    connector_id -> different connector (Tally API)
    Binding -> Tally voucher table + environment
```

**Governing source.** Connectors and Readers.

## Prerequisites

| Precondition | Why it is required |
|---|---|
| Cognito authenticated session for a platform actor | Reader mutations are `@PlatformOnly()` JWT-guarded |
| Active OC for the target BO | The Reader Flavor binds an OC; without an OC the Reader cannot execute |
| Approved BO with certified BFs | The OC the Reader executes references the BO; the BO must be approved |
| Active Connector | The Reader Flavor binds a Connector (e.g., `odata-v2`); the Connector is the protocol adapter |
| OC has field mappings | The OC body's `field_mappings[]` is the Reader's instruction set; an OC with no mappings cannot drive observation |

If any prerequisite is missing, the prerequisite procedure runs first (Business Field and Business Object Onboarding for missing BOs; Source and Admission Contract Creation for missing SCs; Observation Contract Creation for missing OCs).

**Governing source.** Connectors and Readers; Observation Contract Creation.

## Track A: D209 Fast-Track (Recommended When OC Exists)

The fast-track surface at `POST /api/readers/create-from-oc` is the primary path for bulk reader creation when OCs are already created. It runs four sub-steps in one call.

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

Default recommendation for enterprise readers: `daily-business` schedule, `conservative` retry, `standard` circuit breaker. The defaults match typical ERP source cadence.

The service creates one `runtime.reader` row (draft), one `runtime.reader_flavor` row (draft) bound to the OC and Connector with the field map in `config_json`, and updates the OC with the `reader_id` back-reference.

**Governing source.** Connectors and Readers.

## Track B: Manual via API

For one-off reader creation or fine-grained control, the actor calls the per-table endpoints directly:

```
POST /api/readers
{
  "name": "<bo-slug>-reader",
  "displayName": "<BO Display Name> Reader",
  "sourceCategory": "enterprise",
  "function": "<function_code>",
  "subfunction": "<subfunction_code>",
  "sourceSystem": "<source_system_name>",
  "description": "Reader for <BO name>",
  "tags": ["<system>", "<bo>"]
}
```

Then add a Flavor:

```
POST /api/readers/<readerId>/flavors
{
  "name": "<system>-<bo>-<protocol>",
  "displayName": "<BO Name> -- <System Name>",
  "sourceSystem": "<source_system>",
  "connectorId": "<connector-uuid>",
  "observationSchema": {
    "observedFields": ["BUKRS", "BELNR"],
    "standardFields": ["company_code", "document_number"],
    "fieldMap": { "BUKRS": "company_code", "BELNR": "document_number" }
  },
  "status": "draft"
}
```

Bind the OC:

```
PATCH /api/readers/<readerId>/flavors/<flavorId>
{ "observationContractId": "<oc-uuid>" }
```

Optionally add a Binding for SC linkage:

```
POST /api/readers/bindings
{
  "readerId": "<reader-uuid>",
  "flavorId": "<flavor-uuid>",
  "sourceContractId": "<sc-uuid>",
  "versionCode": "1.0.0",
  "sourceEntity": "BSID",
  "environmentCode": "dev"
}
```

**Governing source.** Connectors and Readers.

## Track C: Reader Constructor Wizard (D200)

The seven-step wizard orchestrates the full chain from BO selection through reader activation:

| Step | Action |
|---|---|
| 1 | Select Business Object |
| 2 | Select Canonical Contract |
| 3 | Select or create Observation Contract |
| 4 | Select Connector |
| 5 | Select Source Version |
| 6 | Create Reader plus Flavor (calls D209 fast-track internally) |
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

Activation requires CR-QG-RDR-003 (the seven chain integrity checks below) to pass. A draft Flavor or a Flavor with missing OC binding cannot be activated.

**Governing source.** Connectors and Readers.

## Adding a Second Flavor (Multi-Source Reader)

When a BO needs data from multiple source systems, the actor adds a Flavor to the existing Reader rather than creating a new Reader. The procedure:

1. Create the OC for the second source system (Observation Contract Creation).
2. Add a Flavor to the existing Reader pointing at the new system's Connector.
3. Bind the new OC to the new Flavor via PATCH.
4. Activate the new Flavor when readiness checks pass.

Both Flavors emit the same business fields (same BO) but read from different source systems. The Reader's subfunction-scoped identity remains; the Flavor count grows.

**Governing source.** Connectors and Readers.

## Quality Gates

The Reader creation enforces three classes of gate.

### CR-QG-RDR-001: Reader Creation Gate

| # | Check |
|---|---|
| 1 | BO linked: `business_object_id` references an existing BO |
| 2 | Name unique: no existing Reader with the same `reader_name` |
| 3 | Function valid: `function_code` matches a registered business function |
| 4 | Operational config valid: schedule cron is parseable; retry config has valid values |

### CR-QG-RDR-002: Flavor Readiness Gate

| # | Check |
|---|---|
| 1 | OC bound: `observation_contract_id` is non-null and references an active OC |
| 2 | Connector bound: `connector_id` is non-null and references an active Connector |
| 3 | Config present: `config_json` carries the field map |
| 4 | Status active: Flavor `status_code` is `active` (after the activation step) |

### CR-QG-RDR-003: Reader Chain Integrity (Seven Checks)

A Reader is chain-complete when all seven checks pass:

| # | Check |
|---|---|
| 1 | BO linked: `reader.business_object_id` is non-null |
| 2 | BO approved: the referenced BO has `approved` status |
| 3 | Has active flavor: at least one `reader_flavor` with `status: active` |
| 4 | Flavor has OC: the active flavor has non-null `observation_contract_id` |
| 5 | Flavor has Connector: the active flavor has non-null `connector_id` referencing an active Connector |
| 6 | Has binding: the active flavor has at least one `reader_binding` row |
| 7 | SC active: every binding references an active Source Contract |

Only chain-complete Readers can execute Admission Runs. The checks are run on demand via the integrity surface and on every Reader status change.

**Governing source.** Connectors and Readers; Quality Gates and Chain Integrity.

## Forbidden Patterns

The chapter records five forbidden patterns. Each one breaks the platform's UniBAT discipline at a specific layer.

| Forbidden | Why |
|---|---|
| One Reader per BO | Readers are subfunction-scoped (D312 in the v2 SOP shorthand); multiple BOs in the same subfunction share one Reader with one Flavor per (source system, BO) pair |
| One Reader per source table | Source tables are Bindings, not Readers |
| Skip OC binding | A Reader without an OC-bound Flavor cannot execute Admission Runs; the Flavor is the contract-bearing layer |
| Hardcode credentials in Reader config | Credentials live in `runtime.connection` (tenant-scoped), not in the Reader |
| Create Readers for BOs that lack OCs | The Reader executes the OC; without an OC there is nothing to execute |

**Governing source.** Connectors and Readers; Tenancy and Binding.

## Boundary with Other Onboarding Chapters

| Chapter | Relationship |
|---|---|
| Source and Admission Contract Creation | Provides the SC the `reader_binding` references |
| Business Field and Business Object Onboarding | Provides the BO the Reader is linked to |
| Observation Contract Creation | Provides the OC the Reader Flavor binds |
| Canonical Contract Creation | Independent; the Reader does not bind a CC; the CC consumes SOs the Reader produces |
| Metric Contract Creation | Independent; the MC consumes COs that later evaluation produces from SOs |
| Tenant Onboarding | The Tenant Connection (per-tenant credentials) is paired with the Reader Flavor at runtime; the Reader is platform-scoped, the Connection is tenant-scoped |

**Governing source.** Source and Admission Contract Creation; Observation Contract Creation; Tenant Onboarding.

## Drift Inventory

| Drift item | Form |
|---|---|
| `create-from-oc` derives Reader name from OC display name | The fast-track surface produces Reader names that may include the source-table component instead of the BO. The actor renames via PATCH if subfunction discipline requires; the chapter records this as a known cosmetic drift |
| Connector inventory is small | The readiness-baseline platform Connector list is short (the OData V2 connector covers SAP ECC and S/4HANA). Other source families (Salesforce, Oracle, Tally, REST APIs) are connector gaps recorded in Connectors and Readers |
| Bulk reader creation throughput is OC-driven | When OCs land in batches (multi-domain onboarding), the create-from-oc surface admits them in sequence; the platform does not parallelize across OCs to avoid AI verification rate limits at the preceding OC creation layer |
| Activation gate failures surface late | A Flavor with missing OC binding can be created in `draft`; the failure surfaces at the activation step, not at create. The actor reads the chain integrity report to identify the missing binding |
| qa-bench Reader provisioning is aspirational | Test Bench Module writes evidence into the addressed tenant in the readiness baseline rather than a dedicated qa-bench tenant; the qa-bench Reader provisioning is a queued surface in Synthetic Data and Testing |

**Governing source.** Connectors and Readers; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-b228ec | Establishes Source Catalog and Integration as separate trees; the Reader bridges them via Flavor (Connector reference plus OC reference) |
| DEC-90faff | Establishes the canonical-driven reader creation sequence (top-down assembly) |
| DEC-36d78f | Establishes the Reader observation schema with selective observation and standard field naming |

The subfunction-scoped Reader convention (D312 in the v2 SOP shorthand) and the operational config presets (D043 fast-track, D200 wizard, D205, D209) are referenced in the v2 SOP without standalone ADR files in the reviewed source set; their record lives in `legacy-v2/docs/sops/reader-creation-sop.md` and in this chapter.

**Governing source.** Decisions: ADR Registry.

## References

- Connectors and Readers
- Admission and Observation
- Sources and the Catalog
- Source Registration
- Business Field and Business Object Onboarding
- Source and Admission Contract Creation
- Observation Contract Creation
- Tenant Onboarding
- Tenancy and Binding
- Quality Gates and Chain Integrity
- Data Model and Schema
- API Surface
- DEC-b228ec: Source Catalog and Integration as separate trees
- DEC-90faff: Canonical-driven reader creation sequence
- DEC-36d78f: Reader observation schema
- legacy-v2/docs/sops/reader-creation-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding


