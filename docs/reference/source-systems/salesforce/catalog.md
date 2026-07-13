---
uid: SRC-a3c7e1-catalog
slug: salesforce-catalog
title: "Salesforce — Catalog"
description: "Salesforce sObject catalog footprint and seed provenance (official Object Reference sourced; per-org Describe verification pending)."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — projection of the Source Catalog, not an authority
domain: crm
subdomain: salesforce
focus: catalog
docket_of: salesforce
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Salesforce — Catalog

> **Projection, not authority (D526 Amendment 1).** Authority is the Source Catalog (`source.*`) and seed store
> (`bc_seed.*`). This page indexes what is registered and its catalog root. The sObject/field definitions below
> are **provisional seed provenance** sourced from the official Salesforce Object Reference — **not verified
> source truth** — until verified against a specific org's Describe output at a pinned API version.

Source-registration and seed-catalog footprint for Salesforce. Procedures:
[source-registration.md](../../../onboarding/source-registration.md),
[seed-catalog-management.md](../../../onboarding/seed-catalog-management.md). Cover: [index.md](index.md).

## Registration status

⚠ **No governed source-registry coordinate exists yet** — `index.md` carries `source_registry_ref: null` and
`catalog_root: null`. Until those resolve to `source.*`, **no row below may show a "registered" state**: each is
a **pending/unresolved projection** (the docket must be internally honest ahead of the G2 CI check).

| Artifact | Status | Ref / provenance |
|---|---|---|
| source_provider | ⧗ pending governed ref | label "Salesforce"; not yet resolvable to `source.*` |
| source_system (`system_type_code`) | ⧗ pending governed ref | label `salesforce`; authority = `source_registry_ref` (null) |
| source_version | ⧗ pending | API version pin TBD (label `v66.0`; current GA v67.0 Summer '26) |
| source_module | ⧗ pending | Sales / Service / Marketing / Commerce (planned) |
| source_object (sObjects) | ⧗ pending (provisional seed only) | seeded from the official [Object Reference](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/); no customer org touched; not governed |
| source_field | ⧗ pending (provisional seed only) | standard-object field definitions from the Object Reference; not governed |
| catalog_verification_log | ⧗ pending | not yet run vs a real org's Describe output at a pinned API version |

## Objects / entities cataloged
| Object | Domain | Grain | Notes |
|---|---|---|---|
| Account | Sales | Company/organization | Party master |
| Contact | Sales | Person at an account | |
| Lead | Sales | Unqualified prospect | Converts to Account/Contact/Opportunity |
| Opportunity | Sales | Deal | `StageName`, `CloseDate`, `Amount`; record types common |
| OpportunityLineItem | Sales | Deal line | Links to PricebookEntry |
| Product2 / PricebookEntry | Sales | Product / priced product | |
| Quote / QuoteLineItem | Sales | Quote header / line | |
| Case / CaseComment | Service | Service case / comment | Service Cloud |
| Entitlement / ServiceContract / WorkOrder | Service | Support entitlements / contracts / work | Service Cloud |
| Campaign / CampaignMember | Marketing | Campaign / membership | Attribution |
| Order / OrderItem | Commerce | Order header / line | |
| User / Profile / PermissionSet / RecordType | Platform | Identity & access context | |
| Task / Event | Activities | Engagement history | |
| Custom objects (`__c`) | Custom | Per-org | Discovered via Describe Global — per-realization catalog work |

> The cataloged object is the **sObject** — the vendor's own API-level semantic object, per-org extensible
> (custom fields on standard objects, custom objects, record types). See [index.md](index.md) §3.

## Seed-load provenance
- Standard sObject/field definitions seeded from the **official Salesforce
  [Object Reference](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/)** —
  **no customer org touched**. This is **provisional seed provenance, not verified source truth**: a
  `catalog_verification_log` pass against a real org's [Describe](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm)
  output at a pinned API version is required before any field definition here is treated as verified. Until
  then, definitions are design-time approximations.
- ⚠ Cross-reference standing rule (qualified): standard sObject *semantics* are broadly universal and authored
  once at platform level, never per-tenant — but this universality is **scoped to an exact API version and
  narrowed by each org's configuration**: custom fields, record types, managed packages, and field-level
  security all alter the realized shape and must be verified per realization, not assumed. Custom `__c`
  objects/fields are the additive per-customer catalog work.
