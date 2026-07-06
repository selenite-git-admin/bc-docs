---
uid: business-concept-registry-f3-authoring-service-design
title: Business Concept Registry — F3 authoring-service design note
description: Design note for the Registry authoring service (Phase F item F3) — the single governed write path for concept_registry state. Locks the external-authorization model, the supersession cascade, the name-conflict checks, and provenance stamping; states plainly the small additive DBCP F3 carries.
status: accepted
date: 2026-05-21
project: bc-docs
domain: contracts
subdomain: catalog
focus: architecture
---

# Business Concept Registry — F3 authoring-service design note

> **What this is.** Phase F item **F3** of the BCF build plan — the design for
> the Registry authoring service, the single governed write path for
> `concept_registry` state. This note locks the F3 design surveyed and reviewed
> 2026-05-21: the external-authorization model (§1), the supersession cascade
> (§3), the name-conflict checks (§4), and provenance stamping (§5). It is a
> **design note, not an ADR** — it elaborates DEC-02f5a9 and builds on the
> accepted F1 forward-design note and the approved F2 schema DBCP packet.
> **F3 carries a small additive DBCP** (§6) — it is not service code alone.
> `status: accepted` — locked on operator review-back 2026-05-21. The F3 build
> begins after PR #50 (the F2 migration) is reviewed.

## Scope

This note covers the F3 service boundary and its four locked design points. It
does not author the F3 service code or the F3 DBCP migration — those are F3
build-time work, sequenced after PR #50. It states the design they implement.

## 1. Boundary and the authorization model

**F3 is the single governed write path for `concept_registry` state.** Every
write — entity and concept anchors, versions, lifecycle transitions, and the
vocabulary tables — goes through F3. The registry repository layer is
F3-private; no raw `INSERT` / `UPDATE` against `concept_registry.*` is issued
from anywhere else. This is a service-architecture rule, and it must be: the F2
meaning-immutability trigger deliberately permits `lifecycle_state` updates, so
nothing at the database layer stops a stray raw lifecycle write — only the
sole-write-path discipline does.

**Authorization stays external and explicit.** The BCF Authoring Panel judges
placement; Framework Approval is the governed approval act. F3 does no AI and
makes no placement judgment — **F3 executes.** F3 does not trust a caller's
assertion that a write was approved: **every state-changing F3 operation
requires an authorization reference — a `certification_record_id`, the durable
governed-approval artifact — and F3 verifies that the reference resolves to a
valid, approved `certification_record` for this write before it writes.** F3
cannot write un-authorized Registry state.

**The mandate is operational; the exemption register is named and tiny.** At
the database layer the provenance column is a nullable `uuid` (§5 — the F2
coexistence rule forbids a cross-schema FK into `contract`). Database-nullable
is a schema-isolation fact, **not** a statement that the value is optional: F3
rejects any state-changing operation that arrives without a verifiable
`certification_record_id`. Exactly one F3 path is exempt — **the F4
governed-vocabulary seed**, the one-time initial population of the seed
`characteristic` rows, which necessarily runs before the panel /
Framework-Approval path is in service for vocabulary. (The closed
`representation_term` set is seeded directly in the F2 migration SQL and never
passes through F3 at all.) That is the **entire** exemption register: a
build-time seed, not a runtime escape hatch. It admits no caller, no
environment flag, and no `admin` role at runtime; adding an entry is itself a
governance act — a design-note amendment — so the list stays named, never
implied.

The authoring sequence:

```
intake candidate
  -> Panel judges placement
  -> Framework Approval records a certification_record
  -> F3 executes the write, given (and verifying) the certification_record_id
```

The F2 database triggers and constraints are the structural floor. F3 adds what
the database cannot express: bootstrap ordering, transaction boundaries,
clean-error pre-checks (the acyclic identity-graph pre-check, and the
name-conflict checks of §4), and the supersession workflow of §3.

## 2. Operation set

| Subject | Operations |
|---|---|
| Entity | create (bootstrap), add descriptive version, supersede, lifecycle transition |
| Business Concept | create (bootstrap), add descriptive version, supersede, lifecycle transition |
| Vocabulary | register characteristic, register representation term, register alias |

Every state-changing operation takes the §1 authorization reference, subject
only to the §1 exemption register. **Create
(bootstrap)** is a single transaction: insert the anchor (`draft`,
`active_version_id` NULL) → insert the first version → update the anchor's
`active_version_id`. Callers never observe the null-pointer state.

## 3. Supersession cascade — D1

A meaning-bearing change to an entity (a change to its identity-bearing property
set) mints a new `entity_id` and an `entity_supersession` row (F1.2). Every
entity whose identity-bearing reference points at the superseded entity must
re-point — and F1.2 locked that this is **governed proposals, never
auto-rewrite**.

**Locked:** F3 writes one row to a new **`concept_registry.supersession_proposal`**
table per affected (dependent) entity. F3 never auto-rewrites a dependent. An
operator actions a proposal through F3 — itself a governed re-author of the
affected entity, and so itself requiring an authorization reference (§1). The
proposal table makes the cascade auditable and operator-paced.
`supersession_proposal` is part of the F3 DBCP (§6).

## 4. Name-conflict checks — D2

The F2 database constraint `uq_alias_kind_normalized` blocks a duplicate
normalized alias within a target kind. F3 adds the cross-table normalized-name
check the database cannot express — **split into two name-spaces by kind**:

- **Entity name-space** — an entity `canonical_name` and entity-targeted
  aliases conflict with each other.
- **Characteristic name-space** — a characteristic `term` and
  characteristic-targeted aliases conflict with each other.
- **The two name-spaces do not cross.** An entity name and a characteristic
  term may legitimately share a word — concept identity is `entity.property`,
  two levels; the entity space and the property-characteristic space are
  distinct.

On registering a `canonical_name`, a characteristic `term`, or an alias, F3
pre-checks the normalized form against the other members of its name-space and
rejects a collision with a clean, explained error. The database constraint is
the base layer; F3 is the cross-namespace guard, per name-space.

## 5. Provenance stamping — D3

Every F3-written version row records its authorizing provenance, with the
**durable approval artifact as primary**:

- **`certification_record_id`** — primary, and **operationally mandatory** per
  §1. `contract.certification_record` is the durable proof of the governed
  approval event. It is the same reference F3 required and verified at the
  write (§1): the required input and the stamped provenance are one and the
  same. The column is database-nullable (see the cross-schema note), but F3
  writes no version row without it — outside the §1 exemption register.
- **`panel_run_uid`** — optional. `contract.panel_output_record` proves the
  AI-panel evidence behind the decision — supplementary, not authoritative.

Panel proves evidence; the certification record proves the governed approval.
Stamping the certification reference makes registry provenance explicit, not
inferred (Invariant VI).

**Cross-schema note.** `certification_record` and `panel_output_record` live in
the `contract` schema. To preserve the F2 coexistence rule — no FK crosses
between `concept_registry` and `contract` — these provenance columns are **plain
`uuid` soft references, not database FKs.** "Soft" names only the absence of a
database FK constraint; it does not weaken the obligation —
`certification_record_id` is operationally mandatory under §1 regardless. F3
verifies the `certification_record` at the service layer (§1); it does not rely
on a cross-schema FK. This keeps
`concept_registry` FK-isolated until the Phase G cutover.

## 6. The F3 DBCP

**F3 is not service code alone — it carries a small additive DBCP.** The DBCP
adds, additively, within the `concept_registry` schema:

- **`supersession_proposal`** — the table behind §3: the superseded entity, the
  affected dependent entity, the proposed re-point, proposal status, and
  created / actioned metadata. FK-internal to `concept_registry.entity`.
- **Provenance columns** on `entity_version` and `business_concept_version` —
  `certification_record_id` (uuid; nullable column, no cross-schema FK, but
  **operationally mandatory** per §1) and `panel_run_uid` (uuid; nullable, and
  **genuinely optional**), per §5.

The DBCP is additive — a new table plus new nullable columns; no existing
`concept_registry` table is restructured, and no FK crosses to `contract.*`. It
is authored and reviewed exactly as the F2 DBCP was: a packet, then a
forward / revert migration, then the Drizzle-mirror update — operator-approved
before any execution. It sequences after the F2 migration (it is additive on
F2's schema).

## 7. What the F3 build delivers, and when

F3 build has two parts:

1. **The F3 DBCP** — the `supersession_proposal` table and the provenance
   columns (§6), authored as a packet + forward/revert migration + Drizzle
   mirror update.
2. **The `RegistryAuthoringService`** — the single governed write path: the
   operation set (§2), the required-authorization-reference rule and its
   verification (§1), the bootstrap orchestration, the clean-error pre-checks
   (acyclic, name-conflict §4), and the supersession-cascade workflow (§3).

**Sequencing.** F3 build begins after PR #50 (the F2 migration) is reviewed —
F3 builds against F2's `concept_registry` schema, and the F3 DBCP is additive on
top of it. The F3 design changes no DEC-02f5a9 / F1 / F2 decision; it elaborates
them.

## Status

`accepted` — locked on operator review-back 2026-05-21. F3 build (the DBCP,
then the service) proceeds on the operator's go, after PR #50 (the F2
migration) is reviewed.
