---
uid: business-concept-registry-f3-service-slice-plan
title: Business Concept Registry — F3 service-build slice plan
description: Slice plan for building the RegistryAuthoringService from the accepted F3 authoring-service design note — six reviewable slices (F3-private repositories, authorization-verification core, create/version/lifecycle operations, supersession cascade, name-conflict pre-checks, end-to-end smoke). Accepted on operator review-back 2026-05-21.
status: accepted
date: 2026-05-21
project: bc-docs
domain: contracts
subdomain: catalog
focus: architecture
---

# Business Concept Registry — F3 service-build slice plan

> **What this is.** The build slice plan for `RegistryAuthoringService` — the
> F3 service half of the BCF Phase F item F3. It translates the accepted F3
> authoring-service design note and the approved F3 DBCP packet (rev 2) into six
> reviewable slices. Each slice ships as its own small PR carrying the
> build-plan §13 trailers; all are additive substrate (build-plan §13.1 —
> exempt from consumer-map / characterization).
>
> **Accepted (2026-05-21).** Operator review-back accepted the six-slice shape,
> resolved the three §5 questions, and added a slice-1 write-access-boundary
> test. `status: accepted` — the F3 service build proceeds slice by slice,
> slice 1 first, each its own reviewed PR.

## 1. Scope and hard constraints

This plan covers the F3 **service** build only. The F3 substrate (the
`concept_registry` schema, F2 + F3 migrations) is applied and verified; this
plan builds the governed write path on top of it.

The four hard constraints govern every slice:

- **F3 is the only writer to `concept_registry`.** The repository layer (slice
  1) is module-private — not exported from `RegistryAuthoringModule`. No other
  module can inject it; no raw `INSERT` / `UPDATE` against `concept_registry.*`
  exists anywhere else. Slice 1 adds a write-access-boundary test that holds
  this true (§3, §5).
- **Every state-changing operation requires a verified `certification_record_id`**
  — except the one closed F4 governed-vocabulary-seed exemption (F3 design note
  §1). The exemption is a single named method, not a flag, role, or parameter.
- **No direct raw lifecycle writes outside F3.** `lifecycle_state` transitions
  go only through `RegistryAuthoringService` — the F2 meaning-immutability
  trigger deliberately permits `lifecycle_state` updates, so only this
  discipline stops a stray write.
- **No service code precedes an accepted slice plan.** This plan is `accepted`
  (§5); the build proceeds slice by slice, in order.

## 2. Build target and layout

`RegistryAuthoringService` is a NestJS `@Injectable()` service. All F3 service
code lives in a new directory, grouped like the existing `src/registry/semantic-definitions/`:

```
src/registry/concept-registry/
  registry-authoring.module.ts            — the NestJS module (only RegistryAuthoringService is exported)
  registry-authoring.service.ts           — the single governed write path (façade over the slices)
  certification-verifier.service.ts       — authorization-verification core (slice 2)
  name-conflict.checker.ts                — name-conflict + acyclic + distinctness pre-checks (slices 3 + 5)
  registry-authorization.exception.ts     — F3 domain exceptions (extends NestJS HTTP exceptions)
  repositories/
    entity.repository.ts                  — entity / entity_version / entity_supersession
    business-concept.repository.ts        — business_concept / *_version / *_supersession
    vocabulary.repository.ts              — characteristic / representation_term / alias
    supersession-proposal.repository.ts   — supersession_proposal
  *.spec.ts                               — co-located unit specs
  registry-authoring.integration.spec.ts  — end-to-end smoke (slice 6)
```

Confirmed bc-core conventions this build follows (from a codebase survey):
the service owns the transaction boundary (`this.db.transaction(async (tx) => …)`)
and threads `tx` into repository methods; repositories are `@Injectable()`,
inject the `CONTROL_PLANE_DB` token, and take an optional `tx?: DbOrTx`;
`Logger` is per-class (`new Logger(Name.name)`); domain errors are NestJS HTTP
exception subclasses surfaced by the global `ProblemDetailFilter`; PKs are
DB-generated `uuid`s (`.returning()` the generated id — no `IdService`).

**Prerequisite — control-plane wiring.** `concept_registry` is exported in the
Drizzle barrel but is **not** registered in `src/database/control-plane.provider.ts`
(neither the `ControlPlaneSchema` type, the provider `schema` spread, nor the
connection `search_path`). Until it is, no repository can query
`concept_registry`. This wiring is the first task of slice 1. It is **not** a
DDL change and **not** a new DBCP (the schema and tables already exist) — but it
edits a shared, sensitive provider file, so it is **flagged for explicit review
inside the slice-1 PR**.

## 3. The six slices

### Slice 1 — F3-private repository layer

**Goal.** The data-access floor: typed Drizzle repositories over the 10
`concept_registry` tables, module-private, transaction-aware.

- **Files / modules.** `repositories/{entity,business-concept,vocabulary,supersession-proposal}.repository.ts`; `registry-authoring.module.ts` (skeleton — registers the four repositories, exports nothing yet); `src/database/control-plane.provider.ts` (**flagged** — add `concept_registry` to the schema map + `search_path`); co-located `*.repository.spec.ts`.
- **Public service methods.** None — no service yet. Repositories expose typed data-access methods that each accept an optional `tx?: DbOrTx`: e.g. `EntityRepository.insertAnchor` / `.insertVersion` / `.updateLifecyclePointers` / `.findById` / `.insertSupersession`; analogous on the other three. They carry no business logic and no authorization.
- **Transaction boundaries.** None opened here — repositories never own a transaction; they run on `(tx ?? this.db)`.
- **Invariants enforced.** Establishes the structural precondition for the **single-writer** constraint (repositories module-private, unexported). No runtime Foundation invariant yet; the F2/F3 DB triggers and constraints remain the structural floor beneath this layer.
- **Tests.** Per-repository unit specs (hand-mocked Drizzle builder chain — bc-core stratum A) asserting correct table/column SQL shape; one `Test.createTestingModule` wiring smoke spec asserting DI resolves; and a **write-access-boundary test** (operator review-back addition) — asserts `RegistryAuthoringModule` exports only `RegistryAuthoringService` and that the four repositories are absent from its `exports`, so no other module can inject a raw `concept_registry` writer. A structural guard against future bypasses.
- **PR.** **Own PR.** Additive new files + the one flagged provider edit.

### Slice 2 — Authorization-verification core

**Goal.** The component that proves a write is governed: resolve and verify a
`certification_record_id` before any state change.

- **Files / modules.** `certification-verifier.service.ts`; `registry-authorization.exception.ts` (e.g. `UnverifiedCertificationException extends UnprocessableEntityException`); module registers the verifier; co-located spec.
- **Public service methods.** `CertificationVerifier.verify(certificationRecordId: string, panelRunUid: string | undefined, tx): Promise<VerifiedCertification>` — runs the v1 predicate locked in §5.1: the cert row **exists**; it was **BCF-issued** (`certifier_sub = 'bcf-framework-approval'` together with an approval action/verdict lineage — *not* a bare `action_code` value, which carries legacy meanings); it **has panel evidence** (`panel_run_uid` present); and when the operation supplies a `panelRunUid`, the cert's `panel_run_uid` **matches** it. It throws a clean domain exception on any failure. v1 does **not** match the cert against legacy BF/BO primitive ids — Registry primitives are new; F3 stamps the verified provenance onto the registry version instead. **The F4-seed exemption is not a parameter here** — it is realised as a single named method on `RegistryAuthoringService` (`seedGovernedVocabulary`, slice 3) that is the *only* path which does not call `verify()`. `CertificationVerifier` itself has no bypass.
- **Transaction boundaries.** None of its own — `verify()` runs its `SELECT` on the caller's `tx`, inside the same transaction as the write it authorizes.
- **Invariants enforced.** The F3 design note §1 external-authorization model; **Invariant VI** groundwork (a write cannot proceed without resolvable approval evidence — and that evidence must carry panel lineage). Reads cross-schema into `contract` — permitted (only a cross-schema *FK* is forbidden; a read is not).
- **Tests.** Unit specs — a BCF-issued cert with panel evidence passes; a missing id throws; a cert not issued by `bcf-framework-approval` throws; a cert without `panel_run_uid` throws; a supplied panel lineage that does not match the cert throws. The exemption path is documented and asserted to be the sole non-verifying entry.
- **PR.** **Own PR.** Small and security-critical — isolated review is worth it. The v1 verification predicate is locked in §5.1.

### Slice 3 — Create / bootstrap + add-version + lifecycle operations

**Goal.** The core operation set (design note §2): bring entities, concepts, and
vocabulary into being and move their lifecycle — every write cert-gated,
provenance-stamped, and name-conflict-checked.

- **Files / modules.** `registry-authoring.service.ts` (its first real methods); `name-conflict.checker.ts` — the §4 cross-namespace name-conflict check, folded in here per §5.2; `dto/` input types; module now **exports `RegistryAuthoringService`**; co-located specs.
- **Public service methods.** `createEntity`, `createBusinessConcept` (bootstrap); `addEntityVersion`, `addBusinessConceptVersion`; `transitionEntityLifecycle`, `transitionBusinessConceptLifecycle`; `registerCharacteristic`, `registerRepresentationTerm`, `registerAlias`; and `seedGovernedVocabulary` — the **one** F4 exemption method (no `verify()` call). Every other method takes and verifies a `certification_record_id`. The §4 name-conflict check is an internal pre-check (`assertNoNameConflict`), not new public API.
- **Transaction boundaries.** **Bootstrap** = one `db.transaction`: `verify()` → name-conflict pre-check → insert anchor (`draft`, `active_version_id` NULL) → insert first version (provenance-stamped) → update the anchor's `active_version_id` + lifecycle. Callers never observe the null-pointer state. **Add-version** = one transaction (verify → insert stamped version → re-point `active_version_id`). **Lifecycle transition** = one transaction (verify → update `lifecycle_state`). All pre-check reads run inside the write transaction.
- **Invariants enforced.** **I** (meaning produced once, at the F3 boundary); **III** (versions append-only, anchor meaning write-once — F3 respects, DB enforces); **IV** (explicit references); **VI** (provenance — `certification_record_id` + `panel_run_uid` stamped onto every version row, §5); the §1 cert-gate on every operation; bootstrap atomicity (§2); the §4 two-name-space separation (entity names and characteristic terms do not cross — no database floor exists for this, so it is enforced here).
- **Tests.** Per-operation unit specs (mocked repositories + mocked verifier): bootstrap creates anchor+version and activates atomically; add-version stamps provenance; lifecycle transition is cert-gated; a missing/invalid cert throws and writes nothing. Name-conflict specs: a collision within a name-space is rejected; an entity name and a characteristic term sharing a word do **not** collide.
- **PR.** **Own PR** — the largest. May be sub-split (create+version / lifecycle+vocabulary) if review prefers; planned as one. Carries the §4 name-conflict check (§5.2 resolved).

### Slice 4 — Supersession + cascade proposal workflow

**Goal.** Meaning-bearing change: supersede an entity/concept and run the
governed cascade through `supersession_proposal` (design note §3).

- **Files / modules.** `registry-authoring.service.ts` (extended); a `cascade-planner` helper computing the affected-dependent set; `supersession-proposal.repository.ts` (built in slice 1); specs.
- **Public service methods.** `supersedeEntity`, `supersedeBusinessConcept` (mint a new id, write the typed `*_supersession` row, flip the predecessor to `superseded`, raise one `supersession_proposal` per dependent); `actionSupersessionProposal` (a governed re-author of the dependent — itself a supersession — that sets the proposal `actioned` + `resolution_supersession_id`); `dismissSupersessionProposal` (closes the proposal `dismissed`).
- **Transaction boundaries.** `supersedeEntity` = one transaction covering verify → new anchor+version → `entity_supersession` → predecessor lifecycle flip → dependent-set computation → N `supersession_proposal` inserts. `actionSupersessionProposal` = one transaction (verify → re-author the dependent → set the proposal `actioned` + link). `dismissSupersessionProposal` = one transaction (verify → set `dismissed` + `resolved_*`).
- **Invariants enforced.** **III** (supersession = new anchor + lineage row, never a rewrite); **IV** (the cascade is explicit `supersession_proposal` rows; the resolution link is explicit); **VI** (the re-author's cert stamped on the new version; the cascade outcome emitted via `resolution_supersession_id`); the §3 "governed proposals, never auto-rewrite" rule.
- **Tests.** Unit specs — supersede mints a new id + lineage + one proposal per dependent; action re-points and sets `resolution_supersession_id`; dismiss closes without re-point; the `supersession_proposal_outcome_link_chk` is respected.
- **PR.** **Own PR.** `dismiss` is cert-verified but not cert-stamped — see §5.3.

### Slice 5 — Acyclic + dependent-distinctness pre-checks

**Goal.** The remaining clean-error guards (design note §1; DBCP packet §8.3) —
the §4 name-conflict check moved to slice 3 (§5.2).

- **Files / modules.** `name-conflict.checker.ts` (extended — the acyclic and distinctness checks join the §4 check already added in slice 3); `registry-authoring.service.ts` wires the pre-checks into the slice-3/4 operations; specs.
- **Public service methods.** None new — internal pre-checks: `assertAcyclic(entityId, targetEntityId, tx)` and `assertDependentDistinct(...)`.
- **Two checks.** (a) **Acyclic identity-graph pre-check** — *clean-error only*: the F2 `trg_business_concept_acyclic` trigger is the structural floor; this pre-check raises the good explained error first. (b) **Dependent-distinctness** — *genuinely new* (DBCP packet §8.3): the database cannot CHECK `dependent_entity_id` against the superseded / successor entities; F3 must (`dependent ≠ superseded`, `dependent ≠ successor`).
- **Transaction boundaries.** None of its own — pre-check reads run inside the write transaction, before the write, on a consistent snapshot.
- **Invariants enforced.** §1 "F3 adds what the database cannot express." For (a) the guarantee already exists at the DB floor — this slice is error-surface quality; for (b) this slice *is* the only enforcement.
- **Tests.** Unit specs — the acyclic pre-check rejects a cycle with a clean message; dependent-distinctness rejects `dependent = superseded` and `dependent = successor`.
- **PR.** **Own PR.** Safe as a later slice: (a) has a DB floor; (b) is only reachable once slice 4's supersession exists.

### Slice 6 — End-to-end smoke path

**Goal.** Prove the whole governed path on a live database.

- **Files / modules.** `registry-authoring.integration.spec.ts` (bc-core stratum B — `*.integration.spec.ts`, gated by `BCCORE_INTEGRATION_DB=1`, manual ID-tracked `afterAll` cleanup); optionally a smoke script.
- **Public service methods.** None new.
- **Transaction boundaries.** Exercises the service's own transactions end to end; the test owns no transaction beyond tracking inserted ids for teardown.
- **Invariants enforced.** Observes the full chain in one run — bootstrap atomicity, the cert-gate, provenance stamping, and cascade emission — against a real `bc_platform_dev`-shaped database.
- **Tests.** This slice *is* a test: bootstrap an entity → bootstrap a value concept → add a version → supersede the entity → observe a `supersession_proposal` raised → action it → observe `resolution_supersession_id` set. Per-slice unit tests already travel with slices 1–5; slice 6 is strictly the cross-slice smoke.
- **PR.** **Own PR** — small.

## 4. Sequencing and PR plan

Six slices, six small PRs, built in order:

```
Slice 1  repositories + module skeleton + control-plane wiring
   └─> Slice 2  certification verifier
          └─> Slice 3  create / version / lifecycle / vocabulary  [+ §4 name-conflict]
                 ├─> Slice 4  supersession + cascade
                 └─> Slice 5  acyclic + dependent-distinctness pre-checks
                        └─> Slice 6  end-to-end smoke
```

Dependencies: 2 needs 1; 3 needs 1–2; 4 needs 1–3; 5 needs 3 (and 4 for the
distinctness check); 6 needs all. Each PR is additive substrate under
build-plan §13.1 (exempt from consumer-map / characterization) and carries the
§13 trailers (`BuildPlan: F3`, `ADR: DEC-02f5a9`, `Finding`, `Phase0Impact`,
`Rollback`). No F3 migration or DDL is touched by any slice — the substrate is
already applied.

## 5. Review resolution (2026-05-21)

Operator review-back accepted the six-slice shape and resolved the questions:

**5.1 — The v1 certification-verification predicate (slice 2) — locked.**
`contract.certification_record` is an append-only ledger; a bare
`action_code = 'certify'` is **not** the test (that column carries legacy
meanings). The v1 predicate is: the cert row **exists**; it was **BCF-issued**
(`certifier_sub = 'bcf-framework-approval'` together with an approval
action/verdict lineage); it **has panel evidence** (`panel_run_uid` present);
and when the operation supplies a panel lineage, the cert's `panel_run_uid`
**matches** it. v1 does **not** match the cert against legacy BF/BO primitive
ids — Registry primitives are new; F3 stamps the verified provenance onto the
registry version instead. Reflected in slice 2.

**5.2 — The §4 name-conflict check folds into slice 3 — locked.** A create
path without conflict checks would be unsafe even temporarily, and the §4 check
has no database floor. Slice 3 now carries it; slice 5 is reduced to the
acyclic and dependent-distinctness pre-checks.

**5.3 — `dismissSupersessionProposal` is verified-not-stamped for v1 — locked.**
Dismiss is gated on a verified cert (the hard constraint) but stamps nothing —
the proposal row's `resolved_by` / `resolved_at` are the durable record. If cert
provenance on dismiss is later needed, it is added deliberately as a follow-on
DBCP column, not retrofitted.

**5.4 — HTTP surface — unchanged.** Not raised in review; these six slices
deliver the injectable service only. An HTTP controller, if wanted, is a
separate slice — flag if needed.

**Review-back addition — slice-1 write-access-boundary test.** Slice 1 adds a
small test (or lint guard) asserting `RegistryAuthoringModule` exports only
`RegistryAuthoringService` and keeps the four repositories module-private — a
structural guard against future raw-write bypasses. Reflected in slice 1.

## 6. Testing posture

Per-slice unit tests travel **with** each slice's PR (the bc-core stratum-A
mocked-Drizzle pattern) — testing is never deferred. Slice 6 is strictly the
cross-slice **end-to-end smoke** (stratum B, live-DB, `BCCORE_INTEGRATION_DB`
gated), which can only be written once slices 1–5 exist. Mock-heavy tests beyond
the thin Drizzle-builder mock are out of scope (D082 test discipline).

## 7. Status

`accepted` — operator review-back applied 2026-05-21 (§5). The F3 service build
proceeds slice by slice, **slice 1 first**, each as its own reviewed PR. Slice 1
delivers the F3-private repository layer, the `control-plane.provider` wiring
(flagged for explicit review in that PR), and the write-access-boundary test.
