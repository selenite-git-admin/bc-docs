---
uid: business-context-framework-phase-a-governance-scope-alignment-design
title: Business Context Framework — Phase A governance scope-alignment design note
description: Design note for the Phase A governance substrate under DEC-02f5a9. Phase A (A5–A14) is already built; the gap is the pre-DEC-02f5a9 BF/BO/CF scope vocabulary carried in DB CHECK constraints. Inventories every stale scope surface, classifies it into three buckets, locks one governance scope `registry`, locks the transitional scope-value disposition, and frames the open certification-record identity question. Accepted 2026-05-21.
status: accepted
date: 2026-05-21
project: bc-docs
domain: contracts
subdomain: governance
focus: architecture
---

# Business Context Framework — Phase A governance scope-alignment design note

> **What this is.** The design step that precedes any Phase A Database Change
> Protocol. The BCF governance substrate (build-plan §1, items A5–A14) is
> **already built** — but it was built before DEC-02f5a9 and carries the
> superseded BF/BO/CF scope vocabulary in DB `CHECK` constraints. This note
> inventories every stale scope surface, classifies each into one of three
> buckets, locks the governance scope model, and frames the one genuine open
> design question — what a BCF certification row identifies for a Registry
> authoring operation. It is **not** a DBCP and **not** a build plan.
> `status: accepted` — locked on operator review-back 2026-05-21.

## 1. Scope and constraints

- **Design note only.** No DDL, no code, no branch, no PR. The DBCP that
  re-scopes the `CHECK` constraints is a **later, separate, operator-approved**
  step — it does not begin until this note is accepted and its open question
  (§6) is locked.
- **Authority.** DEC-02f5a9 (D414) Business Concept Registry; the BCF build
  plan (`business-context-framework-build-plan.md` §1, §16); DEC-149ab2 (D411)
  — the ADR the existing A-substrate cites.
- **This note classifies and locks direction.** It does not author the new
  constraints; it decides *which* surfaces change, *into what scope model*,
  and *what stays parked*.

## 2. Background — Phase A is built; the gap is scope vocabulary

Phase A is not a greenfield build. The pre-DEC-02f5a9 BCF effort already landed
the whole governance substrate — eleven A-item commits (`A5`–`A14`, plus the
interim `A4`), with services and tests under `src/registry/framework-approval/`
and `src/registry/framework-calibration/` and nine `contract.*` schema tables.
`A7` is closed (a no-backfill disposition — the all-7-NULL `legacy_pre_bcf`
shape is the disposition). `A12` is folded into `A5` as the REJECT defect-code
`CHECK`.

The gap DEC-02f5a9 opens is narrower than "build Phase A": the substrate speaks
the **pre-DEC-02f5a9 three-scope vocabulary** (`bf_bo` / `cf` / `mapping`, and
the `business_field` / `business_object` / `canonical_field` primitive types),
hardcoded in DB `CHECK` constraints. DEC-02f5a9 §16.1 collapsed Scope 1/2/3
into **one** Business Concept Registry of Entities and Business Concepts. The
build plan §16.4's claim that the surviving A-substrate "carries forward
unchanged" is half right: `A5` / `A10` / `A12` / `A13` are genuinely
vocabulary-agnostic; `A8` / `A9` / `A14` (and the `A6` cert ledger, and the
`C8` / `C9` queue surfaces) are not.

## 3. Stale-surface inventory

Every governance surface carrying the BF/BO/CF scope vocabulary:

| # | Surface | Stale column(s) | Current `CHECK` / shape | Build item |
|---|---|---|---|---|
| 1 | `contract.framework_policy` | `scope_code` | `IN ('bf_bo','cf','mapping','all')` | A8 |
| 2 | `contract.operator_confirm_rule` | `scope` | `IN ('bf','bo','cf','mapping','any')` | A9 |
| 3 | `contract.phase_state` | `scope_code` | `IN ('bf_bo','cf','mapping','all')`; PK `(scope_code, stage_code)` | A14 |
| 4 | `contract.certification_record` | `primitive_type`, `primitive_id` | `primitive_type IN ('canonical_field','business_field','business_object')`; `primitive_id` `NOT NULL` poly-ref to an existing row | A6 |
| 5 | `contract.authoring_panel_rejection_log` | `scope_code`, `primitive_type`, `primitive_id` | `scope_code IN ('bf_bo','cf','mapping')`; `primitive_type IN ('business_field','business_object','canonical_field')`; `primitive_id` `NOT NULL` | C9 |
| 6 | `contract.intake_queue` | `scope_code`, `primitive_type` | `scope_code IN ('bf_bo','cf','mapping')`; `primitive_type IN ('business_field','business_object','canonical_field')`; `outcome_primitive_id` already **nullable** | C8 |
| 7 | `contract.primitive_provenance` | `primitive_type`, `primitive_id` | `primitive_type IN ('canonical_field','business_field','business_object')` | legacy SDA ledger (DEC-a17d0f) |

`A5` `panel_output_record` (`stage_code`, no scope/primitive column), `A10`
predicate parser, `A12` defect codes, `A13` `calibration_event` (keyed by
`panel_run_uid`, no scope column) carry **no** stale scope surface — confirmed
vocabulary-agnostic, no alignment work.

## 4. Classification

### 4.1 Bucket 1 — critical path for B6 governance

**`framework_policy`, `operator_confirm_rule`, `phase_state`,
`certification_record`.**

B6 (the unified Registry Authoring Panel) emits `panel_output_record` rows
(`A5`, clean), but its runs are *governed* by `framework_policy`, *phase-tracked*
by `phase_state`, *operator-confirm-gated* by `operator_confirm_rule`, and
*authorized into F3* through a `certification_record` (F3's `CertificationVerifier`
reads exactly this table). While `scope_code` can only be `bf_bo` / `cf` /
`mapping`, a Registry-authoring governance policy cannot be expressed without
abusing `all` — compensation, not a fix. **These four block a properly-governed
B6** and are the substantive content of the Phase A alignment.

### 4.2 Bucket 2 — conditional / reuse decision for B6

**`authoring_panel_rejection_log` (C9), `intake_queue` (C8).**

These are not on the critical path by themselves — they depend on a prior
decision: **does B6's Registry authoring reuse the C8 intake queue and the C9
rejection log (re-scoped to `registry`), or does Registry intake/rejection get
its own surfaces?** Until the B6 design settles that, these two are conditional.
If reused, they re-scope exactly like Bucket 1; if not, they stay on the BF/BO
path and join Bucket 3. The Phase A alignment should **not** pre-empt the B6
design — it records the dependency and defers these two.

### 4.3 Bucket 3 — parked legacy / Phase G

**`primitive_provenance`, and the old BF/BO/CF service paths.**

`primitive_provenance` is the legacy semantic-definitions provenance ledger
(DEC-a17d0f). Under DEC-02f5a9, F3 writes its own provenance into
`concept_registry` (`provenance_json`, `certification_record_id`,
`panel_run_uid` on the version rows). The legacy ledger, the A1–A4
`governance.state` columns, and the C1–C4 BF/BO/CF service paths are retired or
compatibility-wrapped at the **Phase G** cutover (build-plan §16.3; physical-table
disposition is the `G6` DBCP). **No alignment investment** — touching them now
is interim work on tables the cutover discards.

## 5. Scope-model lock — one governance scope `registry`

**Locked recommendation:** `framework_policy`, `phase_state`, and
`operator_confirm_rule` adopt a single governance scope value — `registry`.

- `framework_policy.scope_code` → `registry`. The "one active policy per scope"
  unique index then means **one active governance policy for Registry
  authoring**.
- `phase_state.scope_code` → `registry`. With one scope and three stages the
  table is ≤3 rows (was ~12).
- `operator_confirm_rule.scope` → `registry`, retaining a wildcard
  (`any`-equivalent) for cross-transition rules.

**Do not split the governance scope into `entity` and `business_concept`.**
Those are Registry **subject kinds**, not governance scopes. Governance
discipline — the sampling rate, the Phase 0/1/2 calibration ladder, the
operator-confirm rules — is calibrated to *AI authoring against the Registry*
as one activity. B6 is one unified panel that judges entity placement and
concept placement together (build-plan §16.4); forking the scope by subject
kind would fork the calibration ladder and re-introduce the cross-scope
coherence problem DEC-02f5a9 eliminated. Subject kind is still recorded — as a
per-operation attribute on the cert row / intake entry (§6), never as a
governance scope.

**Transitional scope-value disposition (locked — L4).** The DBCP **adds**
`registry` and **keeps** the existing `bf_bo` / `cf` / `mapping` scope values
and the `business_field` / `business_object` / `canonical_field` primitive-type
values in place. They are dropped only at the Phase G cutover, when the
parked-but-live legacy paths that depend on them are themselves retired
(build-plan §16.3). Dropping them before Phase G would break those legacy paths
while they are still running.

## 6. The open design point — what a BCF cert row identifies for a Registry operation

This is the one genuine open design question in Phase A. It is **not** decided
by this note.

### 6.1 F3 cert-gated operations

F3 (`RegistryAuthoringService`) is the single write path to `concept_registry`;
every state-changing operation is certification-gated — the sole exemption is
the closed F4 `seedGovernedVocabulary` path. The cert-gated operations, by
subject kind:

| Subject kind | F3 cert-gated operations |
|---|---|
| `entity` | create entity; add entity version; lifecycle transition; supersede |
| `business_concept` | create concept; add concept version; lifecycle transition; supersede |
| `characteristic` | author a governed characteristic (operator path; F4 seed is the exemption) |
| `representation_term` | add to the closed representation-term set (a governance act) |
| `alias` | author an alias |
| `supersession_proposal` | action a proposal; dismiss a proposal |

*(The exact F3 method surface is confirmed against `registry-authoring.service.ts`
at build time; the subject-kind categories above are the design unit.)*

### 6.2 The problem — the target id does not exist at authorization time

A BCF `certification_record` row is the **authorization token**: C5 (Framework
Approval) writes it from a B6 panel APPROVE, and F3 then consumes it to
authorize the write. The current cert ledger models identity as
`primitive_type` + a `NOT NULL` `primitive_id` **poly-ref to an already-existing
row** — correct for BF/BO/CF state transitions on rows that exist.

It breaks for the Registry. For a **create** (entity, concept, characteristic,
…) the target id is generated by F3's `INSERT` (`gen_random_uuid()`); for a
**version-add** the version id is born by F3; for a **proposal action** the
outcome (a new supersession + a re-authored successor concept) is born by F3.
**When C5 writes the cert row, the final Registry target id does not yet
exist.** So `certification_record.primitive_id NOT NULL` cannot hold it.

**This blocks at cert issuance, not at F3 verification.** The stale
`primitive_type CHECK ('canonical_field','business_field','business_object')`
means C5 / B6 cannot write a well-formed Registry authorization row at all — the
`CHECK` rejects an `entity` / `business_concept` / `characteristic` subject, and
`primitive_id NOT NULL` has nothing to reference. F3's `CertificationVerifier`
is **not** the constraint: it matches on `action_code`, `panel_run_uid`, panel
lineage, and the BCF-issued check — it does not match a BF/BO/CF `primitive_id`.
The Phase A problem is therefore the **cert-issuance shape** — what C5 / B6 must
be able to write — not F3's verification logic, which does not change here.

### 6.3 Candidate models

Two facts bound the design space:

- The cert row **already carries `panel_run_uid`** (the A6 NF1 field) — the
  panel-run spine exists.
- F3's `entity_version` and `business_concept_version` rows **already carry
  `certification_record_id` + `panel_run_uid`** (the F3 DBCP added them) — a
  reverse link *target → cert* already exists, **but only for entity and
  business_concept**; `characteristic` / `representation_term` / `alias` /
  supersession rows do not carry it.
- `intake_queue.outcome_primitive_id` is an in-substrate precedent for a
  **born-null target id stamped post-execution** (set when the entry reaches
  `advanced`).

**Model A — operation-identified, with a born-null target id stamped on
completion.** The cert row identifies the registry authoring operation, the
subject kind, and `panel_run_uid`; a nullable `target_registry_id` is set by F3
after the authorized write succeeds. *Pro:* self-contained in the cert ledger,
uniform across every subject kind, no F3 schema change. *Con — and this is not
free:* `certification_record` is an **append-only audit ledger by convention**.
A post-execution stamp is a deliberate exception to that convention — **not** a
mere reuse of the `intake_queue` precedent (`intake_queue` is an explicitly
mutable queue table; the cert ledger is not). Choosing Model A means committing
to an explicit **one-time completion-stamp invariant**, enforced in the F3 write
path and — ideally — at the storage layer:

- F3 may set `target_registry_id` **exactly once**, in the same transaction as
  the authorized write;
- the only permitted transition is **`NULL` → non-`NULL`** — never
  non-`NULL` → any other value;
- F3 may stamp **only the `certification_record` row it verified** for that
  operation;
- the value is **never updated** afterward — there is no correction path.

Model A is viable only if that invariant is accepted as a deliberate, bounded
audit-ledger exception.

**Model B — operation-identified, no forward target id.** The cert row never
points at the target; the *target → cert* reverse link carries the join. *Pro:*
the cert ledger stays purely append-only. *Con:* the reverse link exists today
only for `entity` / `business_concept` — `characteristic` / `representation_term`
/ `alias` / supersession rows would need new `certification_record_id` columns,
which is **F3 schema work**, arguably outside Phase A scope.

### 6.4 What must be locked

The decision the operator must lock on review-back, before the DBCP:

1. **What a BCF cert row for a Registry operation identifies** — the registry
   authoring operation, the subject kind, `panel_run_uid`, and whether a
   forward `target_registry_id` (born-null write-back, Model A) or no forward
   id (Model B).
2. **The consequent cert-record shape** — `primitive_id` made nullable /
   repurposed; `primitive_type` reworked into a `subject_kind` enum over the six
   kinds in §6.1; whether the operation is a new `registry_authoring_operation`
   column or an extension of the `action_code` enum that F3's
   `CertificationVerifier` already matches on.

This note frames the question and **does not decide it**. Both models carry a
real cost — Model A a deliberate exception to the append-only audit ledger
(§6.3), Model B new F3-side reverse-link columns on the four subject tables
that lack them. **O1 is the main review-back decision** and stays open.

## 7. Out of scope / follow-ups

- **The DBCP itself** — a later, separate, operator-approved step, opened only
  after this note is accepted and §6 is locked.
- **A11 cohort-signal content review** — any registered cohort signal naming a
  BF/BO cohort is a follow-up, **not blocking** this alignment note.
- **Phase C / Phase D BF/BO retargets** — the C/D rows that still name BF/BO/CF
  are Phase C/D maintenance (build-plan §16.4), not Phase A.
- **Bucket 3** — `primitive_provenance` and the legacy service paths are Phase G.

## 8. Decisions — locked and open

**Locked (operator review-back, 2026-05-21):**

| # | Decision |
|---|---|
| **L1** | Phase A is built; the Phase A gate is a DEC-02f5a9 scope-alignment, not a build. |
| **L2** | One governance scope — `registry` — for `framework_policy` / `phase_state` / `operator_confirm_rule`. Not split by subject kind. |
| **L3** | The three-bucket classification: Bucket 1 critical-path (4 surfaces), Bucket 2 conditional on B6 (2 surfaces), Bucket 3 parked / Phase G. |
| **L4** | The DBCP **adds** `registry` and **keeps** the old `bf_bo` / `cf` / `mapping` scope values and the BF/BO/CF primitive-type values until the Phase G cutover — dropping them earlier would break parked-but-live legacy paths. |
| **L5** | O1 resolved as **Model A** (operator lock, 2026-05-21): a Registry certification row identifies the *authorized Registry authoring operation* — `governance_scope = registry`, `subject_kind`, an operation code, `panel_run_uid` as the authorization spine, and a nullable `target_registry_id` stamped by F3 exactly once (`NULL` → non-`NULL`, in the authorized write's transaction, never changed). Operationalized in the Phase A alignment DBCP packet (Bucket 1). |

**Open — for operator lock:**

| # | Question |
|---|---|
| **O2** | Bucket 2 — whether B6 reuses the C8 intake queue and C9 rejection log (re-scoped) or gets its own Registry surfaces. Conditional on the B6 design. |

## 9. Status

`accepted` — operator review-back 2026-05-21 locked L1–L5. O1 is resolved as
Model A (L5); the Phase A alignment DBCP packet for the four Bucket-1 surfaces
is **approved** (rev 2 — `business-context-framework-phase-a-alignment-dbcp-bucket-1.md`).
O2 remains open — Bucket 2 follows the B6 design; Bucket 3 is Phase G.
