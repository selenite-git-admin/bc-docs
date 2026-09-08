---
id: platform-workflow-catalog
title: "Platform-Side Workflow Catalog (Design Plane)"
status: drafting
authority: reference
depends_on: [onboarding-overview, architecture, internal-modules, the-contract-grammar, business-concept-registry]
governing_sources:
  - Onboarding
  - Architecture
  - The Contract Grammar
---

# Platform-Side Workflow Catalog (Design Plane)

> The single index of the platform-side (design-plane) workflows — the governed
> procedures that **author and govern platform artifacts** and **onboard**
> sources, metrics, and tenants. It is the missing "workflow map": which workflows
> exist, how each is governed, whether it has a UI/API/CLI door, and where the
> gaps are. It deliberately excludes the runtime **execution plane** (admission →
> canonical → metric evaluation), which is documented in the Operating Model.

## Two governance tiers

Every platform-side workflow sits in one of two tiers:

| Tier | Planes | How it is governed |
|---|---|---|
| **A — Panel + certification** | BCF concept authoring; MCF metric authoring/audit | AI panels (maker/checker/moderator or maker/checker/judge) → certification record → single-writer execution, with DB-trigger immutability underneath. |
| **B — Code-invariant + role** | Source catalog; contracts (SC/AC/OC/CC); readers; connectors; tenant; packages | Fail-closed resolvers (D430/D431), determinism invariants, role gates (`@PlatformOnly`, `@Roles`, `@RequireOperator`), manifest-SHA interlocks, catalog-status locks. No AI panel. |

Both tiers write through one of two engines: `ContractService.governanceMachine`
(`draft → review → approved → active → superseded`) for SC/AC/OC/CC, and the MCF
cert-writer state machine for metrics. Neither is bypassed by any authoring path.

## Families at a glance

| Family | ~Workflows | Tier | Entry surface | Docs (Onboarding SOP) |
|---|---|---|---|---|
| **Source catalog** (6-tier registration, seed read, discovery, retirement) | ~8 | B | Mostly API; system reg + AI-verify have UI | Source Registration; Seed Catalog Management |
| **Contract authoring** (generic contract + lifecycle; SC/AC; OC/CC chain; mapping-binding; kpi-spec) | ~10 | B | SC/AC have UI; **OC/CC no UI**; lifecycle transitions have UI | SC/AC, OC, CC Creation |
| **BCF concept authoring** (panel → cert → write; publication; adjudication; operator-direct recommendations) | ~13 | A | Browse + publish have UI; **authoring a new concept has no UI** | Business Concept Authoring |
| **MCF metric authoring + audit** (intake → panel → materialize → publication-eligibility → request-audit → admit → supersede/retire/restore/rebind; audit-exchange lane) | ~42 | A | Seed-intake registration + governed detail (view) have UI; **activate/supersede/materialize have no UI** | Metric workstream (five SOPs archived — see gap below) |
| **Readers** (authoring, flavors, bindings, registry, unbind/repoint) | ~6 | B | Reader CRUD has UI; **bindings read-only in UI** | Reader Creation |
| **Connector / onboarding / provisioning** (connector reg, connection, connector-onboard, metric-onboard, drift-check, nightly-reconcile) | ~6 | B | Connector/connection CRUD has UI; onboarding orchestrators API only | Connectors and Readers (descriptive) |
| **Tenant** (management, **governed `POST /tenants`**, tenant-binding, tax-reg, packages) | ~8 | B | Tenant create/edit + **governed provisioning API**; onboarding UI + metric-binding no UI | Tenant Onboarding; Tenant Metric Binding |

## Entry-point map (which one-time acts have a door)

**Have a governed UI door (bc-admin):** Source/Admission contract authoring;
contract lifecycle transitions; source-system registration + AI-verify; metric
registration from seed; reader create/edit/delete; connector + connection CRUD;
tenant create/edit; BCF publication; chain-status/readiness.

**Have NO UI door (operator uses the API):** authoring a **new Business Concept**;
**Observation** and **Canonical** contract authoring; MCF metric
activate/supersede/materialize; seed-catalog enrichment; reader bindings; tenant
metric binding; end-to-end tenant onboarding (four tenant sub-pages are UI stubs).

**Now closed:** tenant DB provisioning — `POST /tenants` is a governed,
fail-closed, DB-per-tenant API (bc-core PR #727). Deployment and live provisioning
remain separately gated.

## Design plane vs execution plane

The platform's *authoring* (this catalog — declarations certified by panels or
code invariants) is distinct from the runtime *execution plane* (the couplings
that carry one boundary's output to the next at runtime). The design plane is
broad and governed; the execution-plane couplings are a separate concern tracked
under the Platform Readiness program. This catalog is the design-plane half.

## Known documentation gaps (as of this writing)

- The five metric-side SOPs (Metric Contract Creation, Metric Registration, MC
  Chain Integrity, Metric Seed Catalog Management, Data Seeding and Build Order)
  are in `docs/archive/onboarding/`; the live metric procedure is the reference
  playbook `onboarding/metric-workstream.md`.
- Several Operating Model chapters still teach the retired BF/BO/CF vocabulary;
  the current model is the Business Concept Framework (see Business Concept
  Registry). Migration is in progress.

## Source of truth

The mechanical facts (route, method, controller, DB tables) are derived from
bc-core by scan; this catalog owns the **governed** facts (governance tier, entry
surface, one-time vs recurring). Where they disagree, the code is authority for
mechanics and this catalog for governance intent.
