---
uid: business-concept-registry-f5-read-surface-slice-plan
title: Business Concept Registry — F5 read-surface slice plan
description: Slice plan for Phase F item F5 — the Registry projection / read surface. Locks a bounded RegistryReadService (read-only, no HTTP in v1), the read-only repositories and RegistryReadModule, the exact v1 read methods, and the explicit exclusions. Accepted 2026-05-21.
status: accepted
date: 2026-05-21
project: bc-docs
domain: contracts
subdomain: catalog
focus: architecture
---

# Business Concept Registry — F5 read-surface slice plan

> **What this is.** The build slice plan for Phase F item **F5** — the
> Registry projection / read surface (build-plan §16.2; DEC-02f5a9 §4). F3 is
> the single *write* path; F5 is the *read* path. This plan translates the
> accepted F5 design survey (operator review-back 2026-05-21, decisions
> D1–D7) into reviewable slices. `status: accepted` — locked on operator
> review-back 2026-05-21; a mechanical consistency check against the locked
> decisions passed.

## 1. Scope and constraints

F5 builds the **read** surface over the `concept_registry` substrate (F2) that
F3 (`RegistryAuthoringService`) writes. The v1 consumers are **in-process**:
the BCF unified Registry Authoring Panel (Phase B) and OC/CC/MC re-authoring
(Phase G — "resolve a Business Concept by identity for the contract chain").

Locked constraints (every slice):

- **F5 is read-only.** `SELECT` only — no `insert` / `update`, no cert gate,
  no lifecycle transitions. The write path stays **exclusively F3** (D1).
- **A bounded read service first; no HTTP API in v1** (D1). The v1 consumers
  inject the service in-process. An HTTP controller is F5-S2, deferred to
  Phase D / operator-UI timing.
- **A separate `RegistryReadModule`** (D2) — F3's `RegistryAuthoringModule`
  stays exactly as-is (exports only `RegistryAuthoringService`, single-writer).
  F5 is a parallel read module with its own read-only repositories; it does
  not import `RegistryAuthoringModule` and does not touch F3's module-private
  write repositories.
- **Reads do not trigger evaluation** (Foundation) — F5 is pure projection.

## 2. Build target and layout

`RegistryReadService` is a NestJS `@Injectable()` read service. F5 code is
co-located with the F3 concept-registry code:

```
src/registry/concept-registry/
  registry-read.module.ts          — RegistryReadModule (exports RegistryReadService)
  registry-read.service.ts         — RegistryReadService (the bounded read surface)
  read-repositories/               — read-only repositories (SELECT only)
    *.read-repository.ts
  *.spec.ts                        — co-located unit specs
```

`RegistryReadModule` registers the read repositories + `RegistryReadService`,
and **exports only `RegistryReadService`**. It has no `imports` — the
`@Global()` `DatabaseModule` provides `CONTROL_PLANE_DB`, which the read
repositories `@Inject`. `RegistryReadModule` is registered into `AppModule`
when its first consumer (the Phase B panel) is built — F5-S1 delivers and
unit-tests the module; the `AppModule` wiring is a Phase-B concern, not an
F5-S1 side effect.

Read-only repositories are organized by read area; reads are join-heavy and
cross-subject (resolving a concept joins `business_concept` +
`business_concept_version` + `entity` + `entity_version` + `characteristic`),
so fewer/larger read repositories are acceptable — the exact split is an
F5-S1 implementation detail.

## 3. The slices

### F5-S1 — read service, read-only repositories, module, unit tests

**Goal.** The bounded read surface: `RegistryReadModule`, the read-only
repositories, `RegistryReadService` with the §4 method set, and unit tests.

- **Files / modules.** `registry-read.module.ts`; `registry-read.service.ts`;
  `read-repositories/*.read-repository.ts`; co-located `*.spec.ts`.
- **Tests.** Stratum-A only — hand-mocked Drizzle builder chains for the
  read repositories (assert SQL shape + filter composition); mocked
  repositories for the `RegistryReadService` specs (assert resolution,
  filtering, active-only defaults, the two resolution modes). **No live DB.**
- **PR.** One normal bc-core PR — read service + read-only repositories +
  module + unit tests. No controller, no execution.

### F5-S1b — gated live-DB read smoke (optional)

**Goal.** A stratum-B smoke that reads the real `concept_registry` (the 24
F4-seeded characteristics are now real data) — only if we decide it adds
value beyond the F5-S1 unit tests.

- **Files.** One `*.integration.spec.ts`, gated by `BCCORE_INTEGRATION_DB`.
- **Status.** **Optional, not default.** Per the operator refinement, F5-S1
  does not bundle a live-DB smoke. F5-S1b is opened only on an explicit
  decision that it is useful.

### F5-S2 — HTTP / API controller (deferred)

**Goal.** An HTTP read API for the out-of-process operator UI (bc-admin).

- **Files.** A `@PlatformOnly()` `@Controller('registry/...')` exposing the
  §4 read methods as `GET` endpoints with `@Query` filters and `cursor` /
  `limit` pagination (matching the existing bc-core read-controller pattern).
- **Status.** **Deferred** — its own gate, Phase D / operator-UI timing. Not
  part of the F5-S1 PR.

## 4. Exact v1 read methods (`RegistryReadService`)

All methods are read-only. List methods default to **active-only**
(`archived_at IS NULL` + active lifecycle); an explicit `includeAllStates`
(or a `lifecycleState` filter) opts into other states (D4). List filters are
pagination-ready (`cursor` / `limit`) even before F5-S2.

**Entities**

- `resolveEntity(entityId)` — the entity anchor resolved to its **current
  active `entity_version`** (canonical name, definition, family code, owner
  domain, provenance ids). Returns `null` if absent.
- `listEntities(filter?)` — filters: `lifecycleState`, `familyCode`,
  `ownerDomain`, `q` (canonical-name search), `includeAllStates`,
  `cursor` / `limit`.

**Characteristics**

- `getCharacteristic(characteristicId)` — a single governed characteristic.
- `listCharacteristics(filter?)` — the governed characteristic vocabulary
  (the F4-seeded set + future); filters: `lifecycleState`, `q`,
  `includeAllStates`, `cursor` / `limit`.

**Representation terms**

- `listRepresentationTerms()` — the closed F2-seeded representation-term set
  (`term`, `definition`).

**Alias / name lookup**

- `listAliases(filter?)` — filters: `targetKind` (`entity` /
  `characteristic`), `targetEntityId`, `targetCharacteristicId`.
- `findByNormalizedName(rawName, nameSpace)` — normalizes `rawName` (the F3
  `normalizeName` rule) and returns matches across canonical names **and**
  aliases within `nameSpace` (`entity` | `characteristic`). This is the
  bounded surface the panel's synonym check reads against.

**Business concepts**

- `listConceptsForEntity(entityId, filter?)` — concepts owned by an entity;
  filters: `kind` (`value` / `reference`), `identityRole`, `lifecycleState`,
  `includeAllStates`.
- `resolveConcept(conceptId)` — **by semantic id → current active version**
  (D3; DEC-02f5a9 §4). Assembles the `entity.property` view: the concept
  anchor's immutable meaning (kind, identity role; for `value` —
  characteristic + representation term + type/unit/semantic; for `reference`
  — reference role + target entity), the **current active**
  `business_concept_version` (definition), the owning entity's id +
  canonical name, the target entity's name where applicable, and the version
  row's provenance ids. Returns `null` if absent.
- `resolveConceptVersion(conceptVersionId)` — **by version id → immutable
  audit-pinned view** (D3; F1 §2). Resolves the exact immutable
  `business_concept_version` row (definition, provenance ids) plus the
  concept anchor's immutable meaning and entity context — it does **not**
  resolve to the active version. This is the surface the contract chain
  reads when it has pinned a `*_version_id`.

**Supersession / proposals** (D5)

- `listEntitySupersessions(filter?)` — entity lineage; filters:
  `predecessorEntityId`, `successorEntityId`.
- `listConceptSupersessions(filter?)` — concept lineage; filters:
  `predecessorConceptId`, `successorConceptId`.
- `listSupersessionProposals(filter?)` — the cascade-workflow state; filters:
  `proposalStatus` (`open` / `actioned` / `dismissed`),
  `entitySupersessionId`, `dependentEntityId`.

Every version-bearing view exposes `certification_record_id` and
`panel_run_uid` as **soft uuid ids** (D7) — F5 performs no join into
`contract.*`; a consumer needing certification detail reads `contract`
itself.

## 5. Explicit exclusions

F5 must not:

- **write** — no `insert` / `update` / lifecycle transitions; writes are
  exclusively F3;
- read or expose **tenant data** — `concept_registry` is platform-only
  (D164); F5 reads the control-plane DB only, never tenant DBs, and uses no
  tenant-request `ClsService` context;
- carry a **legacy BF / BO / CF compatibility shim** — F5 reads the Registry
  only, no bridging to the superseded catalog;
- **join into `contract.*`** — provenance is exposed as soft uuid ids only;
- ship a **controller in F5-S1** — the HTTP surface is F5-S2, deferred.

## 6. Decisions locked (operator review-back, 2026-05-21)

| # | Decision |
|---|---|
| **D1** | Bounded read service first; HTTP API deferred to F5-S2. |
| **D2** | Separate `RegistryReadModule` — not added to `RegistryAuthoringModule`. |
| **D3** | Both resolution modes — by semantic id → current active version; by version id → immutable audit-pinned view. |
| **D4** | Active-only defaults; explicit opt-in for all states. |
| **D5** | Supersession / proposal reads are in v1 scope. |
| **D6** | The service is named `RegistryReadService`. |
| **D7** | Provenance exposed as soft uuid ids only; no `contract.*` joins. |

**Operator refinement.** F5-S1 does not bundle a live-DB integration smoke —
it is one normal bc-core PR (read service, read-only repositories, module,
unit tests). A gated stratum-B smoke is **F5-S1b**, opened only if explicitly
decided useful.

## 7. Status

`accepted` — operator review-back 2026-05-21 locked D1–D7 and the
no-bundled-smoke refinement; a mechanical consistency check against the locked
decisions passed on 2026-05-21 (the explicit `ClsService` exclusion in §5 was
added by that check). F5-S1 is the first build slice (one bc-core PR); F5-S1b
is optional; F5-S2 (the HTTP API) is deferred to Phase D timing.
