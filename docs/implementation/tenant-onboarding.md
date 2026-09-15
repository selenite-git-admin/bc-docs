---
id: tenant-onboarding
order: 62
title: "Tenant Onboarding and Provisioning"
status: drafting
authority: authoritative
depends_on:
  - platform-db-foundation
  - architecture
  - backend-services
governing_sources:
  - "Platform DB Foundation Program — docs/overview/platform-db-foundation.md"
  - "The tenant lifecycle and subscription model"
  - Database Change Protocol
governing_adrs:
  - DEC-7df811 (Tenant onboarding state model and isolation model — the three lifecycles; database-per-tenant)
  - DEC-a67518 (Tenant onboarding gate — checklist readiness for the bring-your-own-database and appliance tiers)
  - DEC-771baf (Tenant database architecture — platform→tenant one-way dependency; platform owns all contracts)
  - DEC-324d9e (Hosting tiers)
  - DEC-b97390 (Tenant identity carried as a Cognito claim)
  - DEC-3ee0f6 (Per-tenant object-lock archive bucket created at onboarding)
  - DEC-66d3ca (Appliance tier deferred)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Tenant Onboarding and Provisioning

## Purpose

This document describes how a customer becomes a running tenant: the operating model, the lifecycles a tenant moves through, the operator flow in bc-admin, the handoff to the tenant-facing application, and the substrate the flow depends on. It is mechanism-independent: it fixes *what* onboarding does and *which decisions govern it*, and defers *how the underlying tables and databases are delivered* to the Platform DB Foundation program, so the flow never hard-wires a schema file or a provisioning script that the program will change.

The first version supports the **BareCount-hosted shared tier only**. The bring-your-own-database, dedicated, and appliance tiers are named and deferred, not built.

## Operating model: provision, then hand off

BareCount **provisions** a tenant container and then **hands off** to the tenant-facing application. The platform side creates identity, database, placement and access; the tenant then self-serves — connecting sources, pairing readers, and running evaluations. The platform does not drive the tenant's own data work. This is a clean two-boundary model: bc-admin owns creation and readiness visibility; bc-portal owns everything the tenant does inside its own container.

## The three lifecycles

A tenant moves through three distinct lifecycles, fixed by DEC-7df811:

- **Onboarding record** — `initiated → in_progress → ready → activated`, or `cancelled` (terminal). The setup-journey checklist. For the shared tier the readiness gate is trivial and `initiated → ready` is immediate; the substantive gate belongs to the deferred bring-your-own-database and appliance tiers (DEC-a67518).
- **Tenant status** — `provisioning → active → suspended → archived`, plus `failed`. The operational state of the container itself, carried on the tenant registry.
- **Subscription** — `active / suspended / terminated`, one active per tenant, termination irreversible. In the first version, with a single flat pricing band and no billing, no subscription record is instantiated; the operational lifecycle is carried by tenant status. The subscription set stands as the authority for when real pricing bands and billing arrive.

Tenant data is isolated **database-per-tenant** (`tbc_<slug>`), one database per customer, with a one-way platform→tenant dependency (DEC-771baf, DEC-7df811).

## The operator flow (shared tier)

The flow maps to the ten-stage onboarding path. The steps in bold are performed in bc-admin; the rest are tenant-side or backend-automatic.

1. **Intake** — the operator enters the container basics: tenant name, slug, tier, region and admin email. The onboarding record moves `initiated → ready` (trivial for the shared tier).
2. **Provision** — a single governed provisioning call creates the tenant identity and its database, records the placement (deployment model, region, bucket) on the tenant infrastructure record, and creates the per-tenant object-lock archive bucket (DEC-3ee0f6). Tenant status moves `provisioning → active`.
3. **Create tenant admin** — a governed identity user is created for the tenant administrator, carrying the tenant identity as a claim (DEC-b97390).
4. **Activate subscription** — the tier is bound. In the first version this is the single flat band; the onboarding record moves `→ activated`.
5. **Handoff** — the operator surfaces the admin invite and a readiness checklist; the tenant now self-serves.
6–10. **Tenant-side** — the tenant connects sources, pairs readers, runs its first evaluations to a metric snapshot, and bc-admin's readiness view reflects progress.

## The handoff contract

The handoff key is the tenant-administrator identity user, carrying the tenant identity as a claim (DEC-b97390) — this is what lets the tenant-facing application scope itself and pass its active-tenant gate. The handoff artifact is an invite for the tenant admin (never handled as a plaintext credential by the interface — an invite/credential-manager flow) plus the tenant's entry URL.

The readiness signal is a named backend requirement: bc-admin must **show** downstream progress (connections, readers, first snapshot) per tenant, but per-tenant reads are tenant-scoped and are not callable from the platform side. A dedicated **platform-scoped tenant-readiness projection** is required; the readiness view must not be faked from the platform layer.

## Readiness surfaces

The tenant detail view surfaces four read-only, platform-scoped facets:

- **Infrastructure** — the placement record (deployment model, region, quota, bucket) and its approval workflow.
- **Configuration** — connections and reader state, via the platform readiness projection.
- **Health** — reader runs, evaluation success, first-snapshot presence.
- **Scoping** — the tenant's active contract bindings.

## Subscription and pricing surfaces

The package and tier catalog already exists as an operator surface. The intake tier-picker offers only active packages. In the first version there is a single flat **`Free`** band, seeded as deterministic master data through the spine (not a direct insert). A per-tenant subscription panel and any billing surface are deferred until real pricing bands exist; billing is always the *cause* of a lifecycle change, never an *act* performed here.

## What the flow needs from the Platform DB Foundation program

Each item below is named and deferred to a reviewed unit under the program; none is compensated for in the interface layer:

| Need | Kind | Where it lands |
|---|---|---|
| Onboarding-record table | New platform table | Platform spine, via the Database Change Protocol, as its own reviewed unit |
| Single `Free` package seed | Master-data seed | Deterministic, digest-bound seed under the spine |
| Populate the tenant infrastructure record at provisioning | Backend wiring (table exists) | Service/endpoint; no schema change |
| Create-tenant-admin identity endpoint | Backend endpoint | Respects the admin/member distinction |
| Platform-scoped tenant-readiness projection | New backend endpoint | Avoids the tenant-scope wall |
| Authoritative provisioning-target preview | New read + write-boundary check | A preview endpoint returns the database name for a slug using the *same* derivation the provisioner uses, and the provisioning call refuses at the write boundary when the expected target does not match — so preview and provisioning cannot silently diverge |
| Per-tenant object-lock archive bucket at provisioning | Backend (currently manual) | Object-lock enabled at creation (DEC-3ee0f6) |

The **tenant database source-of-truth and upgrade path**, and the **column design of the onboarding-record table**, are owned by the program's tenant-database units, not by this document. The onboarding flow must not hard-wire a tenant schema file or a provisioning script.

## Acceptance walk

A concrete end-to-end example: an operator creates a container for a customer whose source system is Odoo. bc-admin provisions the container (identity, database, placement, admin). The customer's source system must first be authored into the platform source catalog (a separate platform act). The tenant admin then signs in to the tenant-facing application, adds an Odoo connection by reference, pairs a reader, runs the chain, and produces a first metric snapshot in the tenant database — with bc-admin's readiness view reflecting each step. Most of this walk exercises the tenant-facing application and the evaluation path; bc-admin's part is creation and readiness.

## Deferred

The bring-your-own-database, dedicated and separate-hosting tiers, the appliance tier (DEC-66d3ca), and every tenant-preference surface the foundation cannot yet honor are held. Preference screens are shown only for what the foundation can honor; the rest wait for their governing decision and their reviewed unit.
