---
uid: DEC-7df811
title: "Tenant onboarding state model and isolation model"
description: "Fixes the tenant subscription, onboarding-record and status lifecycles and the database-per-tenant isolation model as an exact-head builder-auditor decision; defers the tenant schema count to live measurement."
status: proposed
subdomain: tenant-topology
focus: state-model-and-isolation
date: 2026-09-15
project: platform
domain: tenants
supersedes: DEC-2c79c8
refs:
  - type: decision
    uid: DEC-a67518
    label: "Tenant onboarding gate — origin of the onboarding-record lifecycle set"
  - type: decision
    uid: DEC-771baf
    label: "Tenant database architecture — platform→tenant one-way; database-per-tenant"
  - type: decision
    uid: DEC-f02230
    label: "Tenant DB schema organization (schema count reconciliation deferred)"
  - type: decision
    uid: DEC-faef79
    label: "Customer data isolation — hybrid data plane (mechanism deferred; resolved here)"
  - type: decision
    uid: DEC-09fb2f
    label: "Evidence immutability and non-superuser runtime identity (D575)"
authority: authoritative
---

# Tenant onboarding state model and isolation model

## Context

The tenant-onboarding design and its requirements study surfaced a set of contradictions in the records: three different lifecycle vocabularies, an isolation model that some records still marked as schema-per-tenant while the running system is database-per-tenant, and a disputed tenant schema count. A reconciliation of the lifecycle sets was reported to have been ratified in conversation on 2026-09-09, but that ratification survives only as prose inside an untracked design document; it has no retained, independently verifiable source.

The Platform DB Foundation program runs under an approval-only operating model in which the builder and the independent auditor hold architectural responsibility and resolve decisions as reviewable proposals accepted at an exact commit. Consistent with how the program treats other reported-only records, this decision does **not** assert the 2026-09-09 conversation as immutable evidence. Instead it fixes the state sets and the isolation model afresh, as an explicit builder-auditor decision accepted at an exact immutable head. The 2026-09-09 discussion is recorded as non-authoritative origin only.

## Decision

### 1. Subscription lifecycle

A tenant's commercial subscription uses the closed set **`active` / `suspended` / `terminated`**. Exactly one subscription is active per tenant at a time; termination is irreversible; a succeeding subscription is a new record with the prior one terminated (history preserved). No subscription table is instantiated in the first version — with a single flat pricing band and no billing, the operational lifecycle is carried by the tenant status set (below). The subscription set stands as the authority for when pricing bands and billing are introduced.

### 2. Onboarding-record lifecycle

A tenant's setup journey uses the set **`initiated` / `in_progress` / `ready` / `activated` / `cancelled`**. `cancelled` is terminal and non-reusable. For the BareCount-hosted shared tier the readiness gate is trivial (`initiated → ready` is immediate); the substantive gate applies to the deferred bring-your-own-database and appliance tiers. The origin authority for this set is DEC-a67518.

### 3. Tenant status

A tenant's operational status uses the set **`provisioning` / `active` / `suspended` / `archived` / `failed`**. This set is live-verified: on 2026-09-15 the `status_code` check constraint on `tenant.tenants` in the platform database enumerated exactly these five values. A provisioner code path guards on a value (`retired`) that is not in this set; that is a code-side drift to be corrected in its own change unit, not a change to this set.

### 4. Isolation model

Tenant data is isolated by **database-per-tenant** (`tbc_<slug>`), one database per customer. This resolves the mechanism that DEC-faef79 deliberately left open ("schema-per-tenant vs database-per-tenant vs row-level") and it **supersedes DEC-2c79c8**, which had specified full schema-per-tenant isolation (`t_<slug>`) — a model the running system does not use. The one-way platform→tenant dependency and platform ownership of all contracts (DEC-771baf) are unchanged.

## Not decided here

The **tenant schema count and organization** (recorded variously as four in DEC-771baf, six in DEC-f02230 with renamed schemas, and a different live set) is **not** resolved by this decision. Settling it requires a direct measurement of a live tenant database, which is out of reach of the platform-scoped tooling available to this unit. It is deferred to the tenant-skeleton unit (W2.3), where the live tenant skeleton is measured and its versioned baseline is established. Recording an unverified count here would repeat the very provenance error this decision exists to avoid.

## Citation correction

The legal-entity and evidence-immutability decision is **DEC-09fb2f (D575)**. An earlier reference to `ce4314` for that topic is incorrect — ADR-ce4314 is a distinct decision (onboarding runway lanes) and must not be cited for evidence immutability or legal-entity identity.

## Consequences

1. The onboarding flow can rely on three stable, recorded lifecycle vocabularies without depending on an unretained conversation.
2. The isolation model is unambiguous and the stale schema-per-tenant record is retired, removing a standing contradiction.
3. The tenant schema count remains an open, explicitly-owned item for the tenant-skeleton unit — visible rather than silently assumed.
4. Downstream substrate (the onboarding-record table, any subscription table) lands only through the Database Change Protocol as its own reviewed unit; this decision authorizes no DDL.
