---
uid: metric-context-framework-m3-lifecycle-substrate-preflight
title: MCF M3 Lifecycle / Immutability Substrate — Preflight
description: Preflight design framing for MCF Gate M3 (lifecycle and immutability substrate). Reads MCF requirements §10 + §17.3, the build plan §4.2 Gate M3 row, the merged M2 DBCP forward references, and the live M2 Drizzle + DDL. Locks the M3 responsibility boundary — `mcf.metric_contract_revision`, `mcf.metric_supersession`, BEFORE-UPDATE immutability triggers across the 5 M2 tables, NOT-NULL transition rules on hash columns when `governance_state_code` reaches `approved`, and cert reuse pattern for MCF `action_code='metric_create'` on `contract.certification_record`. Explicitly excludes M7 (formula AST), M8 (package signature), M9 (fixture / verifier), M11–M12 (authoring), M13 (PE-MC evaluator), and any BCF writes. Recommends docs-only DBCP design as the next gate, mirroring the M2 four-gate pattern (preflight → DBCP → execution PR → DDL apply). Enumerates the 9 operator decisions required before the DBCP design can be authored. No DDL applied; no bc-core schema edited; no MCF metric contracts created.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m3-preflight
---

# MCF M3 — Lifecycle / Immutability Substrate Preflight

## 1. Scope and grounding

### 1.1 Purpose

Frame Gate M3 of the MCF arc (per the build plan §4.2) **before** any DBCP design or bc-core implementation begins. M3 is the lifecycle and immutability substrate — it gives operational force to the lifecycle placeholders M2 shipped (`governance_state_code`, `supersedes_version_uid`, the M3-reserved column COMMENTs) and adds the two new tables MCF §17.1 names (`mcf.metric_contract_revision`, `mcf.metric_supersession`).

This preflight identifies what M3 owns, what it doesn't, what's already decided in MCF M1 (DEC-c3e57f / D422) and the requirements doc, and what operator decisions must be taken before the M3 DBCP design can be authored.

### 1.2 What this preflight is and is not

| | This preflight |
|---|---|
| Is | A docs-only framing of the M3 design boundary, lifecycle + immutability model proposals, table responsibilities, and operator decisions required before DBCP authoring. |
| Is | An explicit recommendation on the M3 path forward (docs-only DBCP → implementation PR → DDL apply). |
| Is not | The M3 DBCP design itself. Column lists, exact constraint shapes, trigger pseudo-code, and migration steps are DBCP scope. |
| Is not | An M3 implementation. No bc-core schema files edited. No DDL written. No Drizzle changes. |
| Is not | An MCF M2 amendment. M2 is live; this preflight reads it but does not modify it. |
| Is not | A revisit of M1. The foundational ADR (DEC-c3e57f / D422) is the authority; this preflight cites it but does not re-decide. |

### 1.3 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core schema edits | ✓ — only read access |
| No DDL applied | ✓ — no apply gate in this preflight |
| No MCF metric contracts created | ✓ — `mcf.metric_contract*` tables remain empty per the M2 apply closeout |
| No M7 / M8 / M9 design | ✓ — M3 scope is structural lifecycle only; M7-M9 are out of scope |
| No BCF writes | ✓ — BCF substrate untouched |
| No Step-4-bis | ✓ — separate workstream; not in this gate |
| `bc-postgres` MCP `allow_write` unchanged | ✓ — preflight is read-only and not even DB-write-needing |

---

## 2. Current live M2 state

Per the M2 apply closeout (`bc-docs-v3 90d6b37`) + post-apply verifier evidence (`bc-core` PR #102 / `2159a0e`):

| Asset | State |
|---|---|
| `mcf` schema | present in `bc_platform_dev` |
| `mcf.metric_contract` | 17 columns, 0 rows |
| `mcf.metric_contract_version` | 15 columns, 0 rows |
| `mcf.metric_variable_binding` | 13 columns, 0 rows |
| `mcf.metric_filter_clause` | 9 columns, 0 rows |
| `mcf.metric_computed_dimension_ref` | 9 columns, 0 rows |
| Hash columns (`formula_intent_hash`, `variable_binding_set_hash`, `filter_set_hash`, `identity_tuple_hash`, `package_signature_hash`, `hash_algorithm_version`) | nullable (per M2 DBCP §11) — M3 must enforce NOT NULL on state transition |
| `governance_state_code` (on `mcf.metric_contract_version`) | placeholder with 5-state CHECK enum (`draft` / `review` / `approved` / `active` / `superseded`); no transition trigger yet |
| `supersedes_version_uid` FK (self-FK on `mcf.metric_contract_version`) | column exists; FK enforced; semantics M3-owned |
| Partial UNIQUE on `identity_tuple_hash` | enforced (only when populated AND not archived) |
| Identity-immutability triggers | **absent** (M3 owns) |
| `mcf.metric_contract_revision` | **does not exist** (M3 creates) |
| `mcf.metric_supersession` | **does not exist** (M3 creates) |
| `contract.certification_record` (Foundation Governance Substrate) | exists (BCF-shared); MCF action_codes not yet seeded |

M2 wrote only structure — no behavioral substrate fired. The writer service (when implemented later in M7+) is currently the only path that would touch `mcf.*`; no service exists yet, so no rows are at risk between now and M3 ship.

---

## 3. M3 responsibility boundary

M3 is the **lifecycle and immutability substrate**. It owns five concerns and nothing else.

### 3.1 What M3 owns

| # | Responsibility | Source |
|---:|---|---|
| 1 | `mcf.metric_contract_revision` — descriptive-only revisions on `active` MCs (display name, threshold, owner, etc.) | MCF §4.6, §17.1, build plan §4.2 Gate M3 |
| 2 | `mcf.metric_supersession` — predecessor → successor edges with correction-class taxonomy | MCF §10.5, §17.1, build plan §4.2 Gate M3 |
| 3 | Immutability triggers — `BEFORE UPDATE` on the 5 M2 tables to reject mutation of identity-bearing columns when the row's lifecycle indicates `active` or `superseded` | MCF §10.4, Foundation Invariant III, M2 DBCP §11.2 |
| 4 | State-transition triggers — `BEFORE UPDATE` on `mcf.metric_contract_version.governance_state_code` to validate forward-only progression through the 5-state graph and enforce hash NOT NULL when transitioning to `approved` | MCF §10.2, M2 DBCP §11.x |
| 5 | Cert reuse pattern — write rows into `contract.certification_record` (Foundation Governance Substrate) with MCF `action_code='metric_create'` when an `intake → draft` write occurs; subsequent transitions (`metric_transition` for approved→active, `metric_supersede` for active→superseded) are M4-owned cert writes that M3's substrate is compatible with | MCF §11.5, §17.3, build plan §4.2 Gate M3 |

### 3.2 What M3 explicitly does NOT own

| # | Out of M3 | Belongs to |
|---:|---|---|
| 1 | Formula AST canonicalization, normalization, identity-hash service | M7 |
| 2 | Package signature hash composition | M8 |
| 3 | Self-verification fixture substrate + structural-check engine | M9 |
| 4 | Deterministic verifier service | M10 |
| 5 | Metric Authoring Panel (M11) + Metric Publication Panel (M12) substrate | M5 + M11/M12 |
| 6 | PE-MC-1..PE-MC-10 evaluator | M13 |
| 7 | Service-level activation preconditions beyond structural NOT-NULL / non-NULL / state-graph (e.g. "PE-MC checks pass" is enforced by M4 service, not by M3 trigger) | M4 service + cert writer |
| 8 | Operator-confirm rule rows for MCF actions | M4 (`contract.operator_confirm_rule` seeding) |
| 9 | `mcf.metric_publication_eligibility_result` substrate | M4 |
| 10 | Any BCF write | BCF arc |
| 11 | Tenant binding lifecycle (MLS 15-25) | M6 + D392 substrate |

### 3.3 Why these boundaries

M3 is the structural-substrate gate. Its triggers enforce **physical contracts** that protect downstream services from violating the lifecycle. The PE-MC checks, fixture verification, and cert content are **service-level contracts** that require additional substrate (M4, M5, M9, M13) before they can fire — they cannot be M3-owned because their inputs don't exist yet at M3-ship time.

The clean separation lets M3 ship and stabilize independently of M7-M13. When M7+ ship later, M3's triggers continue to enforce the structural invariant (no active-row identity mutation) regardless of what M7+ services do.

---

## 4. Proposed lifecycle model

### 4.1 Five-state graph (locked by MCF §10.1)

```
intake → draft → review → approved → active → superseded
```

**`intake` is pre-substrate.** Per §10.1, intake is a Metric Authoring Panel candidate that has not yet been written to `mcf.metric_contract*`. The first substrate write is the `intake → draft` transition (which creates the parent + version rows in a single transaction). M3 does not store `intake` — it only governs the post-intake states (`draft → review → approved → active → superseded`).

### 4.2 Transition actors (per MCF §10.2)

| Transition | Default actor | Substrate enforcement (M3 scope) |
|---|---|---|
| `intake → draft` (first write) | AI by default (panel APPROVE) | M3 trigger validates row creation invariants; no separate state-transition row needed (the first write IS the draft state) |
| `draft → review` | AI by default | M3 trigger: validates current state = 'draft'; new state = 'review'; allow the transition |
| `review → approved` | AI by default | M3 trigger: validates current state = 'review'; new state = 'approved'; **enforces hash columns NOT NULL** on the parent `mcf.metric_contract` (formula_intent_hash, variable_binding_set_hash, filter_set_hash, identity_tuple_hash, package_signature_hash, hash_algorithm_version); rejects if any required hash is NULL |
| `approved → active` | **Operator confirm (always)** | M3 trigger: validates current state = 'approved'; new state = 'active'; verifies cert exists in `contract.certification_record` with `action_code='metric_transition'`, `from_state='approved'`, `to_state='active'`, scoped to this version's UID. Side effect: writes a revision row to `mcf.metric_contract_revision` (if descriptive-only changes accompanied the transition) AND ensures only ONE active version per parent (`is_current = TRUE` discipline) |
| `active → superseded` | **Operator only** | M3 trigger: validates current state = 'active'; new state = 'superseded'; requires a matching `mcf.metric_supersession` row to exist; predecessor.is_current flips from TRUE to FALSE; successor.is_current must become TRUE atomically. Cert: action_code='metric_supersede' |

### 4.3 Reverse / skip transitions

**Forward-only, no skips.** M3 trigger rejects any UPDATE that:
- Moves backward (e.g. `approved → review` or `active → approved`)
- Skips a state (e.g. `draft → approved` without going through `review`)
- Re-enters a non-`draft` state from outside the graph (e.g. INSERT with state='active')

The single exception: a new version row's first state is always `draft` (DEFAULT 'draft' constraint already on M2; M3 trigger reinforces).

### 4.4 Decision retained for DBCP

| # | Decision | Default |
|---:|---|---|
| D-1 | Should `archived_at` be set automatically when state transitions to `superseded`? Or kept separate (an archived row may be in any state)? | Recommendation: keep separate. `archived_at` is the soft-delete column; `superseded` is the lifecycle terminal state. A superseded MC is queryable for historical reference; an archived MC is hidden from default views. |
| D-2 | Should the trigger emit a `panel_output_record` row for AI-default transitions? | Recommendation: no — that's M5's panel run service. M3 just permits/rejects the transition; the panel itself emits its own record. |

---

## 5. Immutability model

### 5.1 Identity-bearing columns (Foundation Invariant III)

Per MCF §4.2 + §10.4, the identity tuple is:

- `grain_entity_id`
- `formula_intent_hash`
- `variable_binding_set_hash` (composed from `mcf.metric_variable_binding` rows)
- `filter_set_hash` (composed from `mcf.metric_filter_clause` rows)
- `temporal_gate_shape_code` + `temporal_gate_params_json` (canonicalized)
- `identity_tuple_hash` (sha256 over the tuple above; UNIQUE basis)
- `package_signature_hash` (composite per §8.7; partition-wise paired with identity_tuple_hash)

M3 trigger: BEFORE UPDATE on `mcf.metric_contract` rejects any change to these columns when the parent has any associated version in state `approved`, `active`, or `superseded`. The trigger looks at the parent → versions relationship and inspects whether at least one version is past-`draft`.

### 5.2 Active-row mutation discipline

On `mcf.metric_contract_version`:
- When `governance_state_code = 'active'`: identity-bearing fields on parent locked; descriptive fields (`description_text`, `function_code`, `subfunction_code`, `owner_json`, `tags`, `threshold_json`, `display_name` on parent) **mutable**, but each mutation must emit a row to `mcf.metric_contract_revision`.
- When `governance_state_code = 'superseded'`: ALL fields locked. Even descriptive updates rejected. (Supersession is the terminal state; correction requires a new version on a new MC.)
- When `governance_state_code = 'approved'`: identity-bearing parent fields locked; descriptive version fields still mutable WITHOUT revision-log requirement (review-state authoring is still active until activation).

On `mcf.metric_variable_binding` / `mcf.metric_filter_clause` / `mcf.metric_computed_dimension_ref`:
- All three are identity-tuple inputs (their content composes into `variable_binding_set_hash` / `filter_set_hash` / etc.).
- M3 trigger: reject UPDATE or DELETE on these rows when their parent `metric_contract_version.governance_state_code` is in (`approved`, `active`, `superseded`).
- INSERT during `draft`/`review`: allowed.

### 5.3 Decision retained for DBCP

| # | Decision | Default |
|---:|---|---|
| D-3 | On parent `mcf.metric_contract`, is `display_name` identity-bearing or descriptive? | Recommendation: descriptive (renaming the MC's user-facing label doesn't change what it computes). |
| D-4 | Is `candidate_source_ref_json` (the non-authoritative orientation field per D422 Decision 3) subject to active-state immutability? | Recommendation: yes — it's a frozen reservoir-provenance reference that shouldn't change post-authoring. But it's already nullable; if NULL at draft, must stay NULL post-active. |
| D-5 | Should M3 ship a "freezer" function (`mcf.freeze_version(version_uid)`) that flips state to `active` in one go, or rely on direct UPDATE? | Recommendation: rely on direct UPDATE through the M3 trigger. The trigger is the gate; a wrapper function is M7+ service concern. |

---

## 6. Revision / audit substrate options

### 6.1 Purpose (per MCF §4.6 + §17.1)

`mcf.metric_contract_revision` records **descriptive-only revisions** on active MCs. Identity-bearing changes are supersession, not revision.

### 6.2 Option A — Single revision table with discriminator

One table `mcf.metric_contract_revision` records every descriptive update with:
- `revision_uid` PK
- `metric_contract_version_uid` FK (the version being revised)
- `revision_seq` (1, 2, 3 within a version)
- `revised_at` timestamp
- `revised_by_name` (Cognito sub / system actor)
- `revision_kind_code` enum: `display_name_change`, `threshold_change`, `owner_change`, `function_code_change`, `description_change`, `tags_change`, `other` (closed set; CHECK constraint)
- `changed_fields_json` — `{ field: { from, to } }` shape
- `rationale_text` (optional; not floor-enforced for descriptive revisions)
- `panel_run_uid` (optional; only set if the revision was AI-proposed)

**Pro**: one table; uniform query surface; easy to audit "what's changed on this MC?"
**Con**: discriminator-driven shape; need CHECK constraints to validate field names; harder to add new revision kinds later (every kind needs schema/CHECK update).

### 6.3 Option B — Snapshot-based revision

`mcf.metric_contract_revision` stores **before/after snapshots**:
- `revision_uid` PK
- `metric_contract_version_uid` FK
- `revision_seq`
- `revised_at`, `revised_by_name`
- `before_snapshot_json` (full version row content before)
- `after_snapshot_json` (full version row content after)
- `rationale_text`, `panel_run_uid`

**Pro**: schema-agnostic; any descriptive field change captured; future-proof.
**Con**: storage bulk; snapshot-driven; harder to query "what was the previous threshold?" without JSON extraction.

### 6.4 Recommendation

**Option A (discriminator-driven).** Reasons:
- The descriptive fields on `mcf.metric_contract_version` are bounded (7 fields: display name, function code, subfunction code, owner json, tags, threshold json, description text). The "other" bucket catches edge cases.
- Discriminator-driven queries are operationally cleaner ("show me all threshold changes in the last 30 days") than snapshot-extraction queries.
- Adding new revision kinds is rare and warrants a deliberate schema change anyway.

### 6.5 Decision retained for DBCP

| # | Decision | Notes |
|---:|---|---|
| D-6 | Confirm the closed revision_kind enum: `display_name_change` / `threshold_change` / `owner_change` / `function_code_change` / `description_change` / `tags_change` / `other` | Operator decides whether `other` belongs in v1 or only via supersession-of-revision-schema later |
| D-7 | Does revision require operator-confirm rationale (≥40 chars) for any kinds? | Recommendation: no — descriptive revisions are low-risk by definition. If a "change" needs operator-confirm, it's misclassified and should be a supersession. |

---

## 7. Supersession substrate options

### 7.1 Required fields (locked by MCF §10.5)

Per §10.5, an `mc_supersession` row must carry:
- `predecessor_mc_id` (= predecessor `metric_contract_uid` OR predecessor `metric_contract_version_uid` — see §7.3 below)
- `successor_mc_id` (same shape)
- `correction_class` enum: `editorial` vs `meaning-bearing` (per DEC-26b6e2 analogue)
- `operator_sub` (Cognito sub from authenticated JWT)
- `rationale_text` (≥40 char floor for high-risk supersession)
- `panel_run_uid` (the panel run that proposed the supersession, if AI-proposed)
- `superseded_at` timestamp

### 7.2 Proposed M3 schema for `mcf.metric_supersession`

| Column | Type | Note |
|---|---|---|
| `supersession_uid` | uuid PK | |
| `predecessor_metric_contract_uid` | uuid NOT NULL FK → `mcf.metric_contract` | The MC being superseded (parent identity) |
| `predecessor_metric_contract_version_uid` | uuid NOT NULL FK → `mcf.metric_contract_version` | The specific version being superseded (the active one at time of supersession) |
| `successor_metric_contract_uid` | uuid NOT NULL FK → `mcf.metric_contract` | The replacing MC (must be different parent — new identity tuple) |
| `successor_metric_contract_version_uid` | uuid NOT NULL FK → `mcf.metric_contract_version` | The replacing version (must be active at time of supersession) |
| `correction_class_code` | text NOT NULL CHECK | `editorial` (no business-meaning change) or `meaning-bearing` (genuine semantic shift); 2-element closed enum |
| `operator_sub` | text NOT NULL | Cognito sub of the operator who confirmed |
| `rationale_text` | text NOT NULL CHECK (LENGTH ≥ 40) | The ≥40-char floor enforced at substrate |
| `panel_run_uid` | uuid (nullable) FK → `mcf.metric_authoring_panel_run` (when M5 ships) | The panel run that proposed; nullable for operator-initiated supersessions |
| `certification_record_id` | uuid NOT NULL FK → `contract.certification_record` | The MCF `action_code='metric_supersede'` cert (M4 substrate writes; M3 references) |
| `superseded_at` | timestamptz NOT NULL DEFAULT now() | |

### 7.3 The "MC vs version" question

§10.5 references `predecessor_mc_id` and `successor_mc_id`. In the substrate, an MC has a parent row + multiple version rows. Supersession can target either:

- **MC-level supersession** (predecessor = parent uid, successor = parent uid): the entire MC is replaced by a new MC. Identity tuple of successor ≠ predecessor by definition (else it would be a revision, not supersession).
- **Version-level supersession** (predecessor = version uid, successor = version uid): a new version supersedes a previous version. This is already captured by `supersedes_version_uid` FK in M2; not the same concept as MCF §10.5 "supersession" which is MC-level.

**Recommendation: §7.2's schema carries BOTH** — the parent UIDs AND the version UIDs. The trigger logic uses the parent UIDs as the canonical predecessor/successor identity; the version UIDs are recorded for audit precision.

The existing `supersedes_version_uid` column on `mcf.metric_contract_version` (from M2) covers a different case: within-MC version succession (e.g. version 2 supersedes version 1 of the same MC during pre-active iterations). That column stays in scope of M3 enforcement (state-transition rules) but doesn't replace the cross-MC `mcf.metric_supersession` table.

### 7.4 Atomicity (per MCF §10.5)

The supersession act must be **atomic**: predecessor.lifecycle_state flips to `superseded` + successor.lifecycle_state must already be `active` + supersession-row insert all in one transaction.

M3 trigger logic: BEFORE UPDATE on `mcf.metric_contract_version` when transitioning to `superseded` — require a matching `mcf.metric_supersession` row to exist AND successor's `lifecycle_state = 'active'` AND successor's `is_current = TRUE`. If any check fails, reject the transition.

The supersession-row insert and the predecessor-flip both happen in the same DB transaction; if either fails, both roll back.

### 7.5 Decision retained for DBCP

| # | Decision | Notes |
|---:|---|---|
| D-8 | Two-element correction_class enum (`editorial` / `meaning-bearing`) — or are there more classes needed? | DEC-26b6e2 (BCF Characteristic supersession) used `correction_class` with similar two-element scope. Recommendation: start with two; add later if a class needs differentiation. |
| D-9 | Should supersession require an active panel run uid (M5-owned), or is operator-initiated (no panel) supersession allowed? | Per §10.5: "panel_run_uid (the panel run that proposed the supersession, if AI-proposed)". So nullable. Operator-initiated supersession is allowed (recommendation: yes; column nullable). |

---

## 8. Activation preconditions and relationship to later gates

### 8.1 The 5 conditions for an "active" MC (per MCF §10.7)

1. `lifecycle_state = 'active'` in `mcf.metric_contract_version`.
2. `archived_at IS NULL` on `mcf.metric_contract` (parent).
3. A `certification_record` row exists with `action_code='metric_transition'`, `from_state='approved'`, `to_state='active'`, linked to the MC's panel run uid.
4. PE-MC-1..PE-MC-10 (per MCF §13) all PASS at certification time (recorded in cert's `gate_results_json`).
5. Identity tuple satisfies the partial-unique constraint (no duplicate active MC with the same tuple).

### 8.2 What M3 enforces vs what later gates enforce

| Condition | M3 enforces? | Notes |
|---|:---:|---|
| #1 lifecycle_state = 'active' | ✓ (trigger validates state graph) | Direct column value |
| #2 archived_at IS NULL when state=active | ✓ (trigger rejects state=active when archived_at set) | Cross-column constraint |
| #3 cert row exists (action_code='metric_transition') | ✓ (trigger references contract.certification_record by version_uid) | M3 trigger READS contract.cert; M4 service WRITES it |
| #4 PE-MC-1..PE-MC-10 all PASS | ✗ M4/M13 enforce | M3 sees the cert row but doesn't validate its `gate_results_json` contents — that's M4 service concern. M3's responsibility ends at "cert exists and is non-revoked." |
| #5 Identity tuple UNIQUE | already enforced by M2 partial-unique index | Existing constraint; M3 does not add to it |

### 8.3 Hash-population gate (M3 ↔ M7 ↔ M8 sequencing)

When state transitions `review → approved`, M3 trigger enforces:
- `formula_intent_hash` IS NOT NULL (M7 writes this)
- `variable_binding_set_hash` IS NOT NULL (M7 writes this from `mcf.metric_variable_binding` rows)
- `filter_set_hash` IS NOT NULL (M7 writes from `mcf.metric_filter_clause`)
- `identity_tuple_hash` IS NOT NULL (M7 writes — the SHA256 over the full identity tuple)
- `package_signature_hash` IS NOT NULL (M8 writes this — composite of formula + bindings + grain + filters + temporal + computed-dim)
- `hash_algorithm_version` IS NOT NULL (one of M7 or M8 writes; first writer wins)

M3 ships **before** M7/M8 services. The triggers won't fire until a service tries to push state to `approved` — and no service will exist to push state until M7+ ship. So the M3 trigger lies dormant for `mcf.*` rows until M7+ become operational. This is safe and correct.

### 8.4 Cert dependency (M3 ↔ M4)

The `approved → active` trigger validates a `contract.certification_record` row exists with the right `action_code`, `from_state`, `to_state`, and version-uid link. The cert row is **written by an M4-owned service** (cert writer for MCF action codes). M4 must ship before MCF can actually push a row past `approved`.

M3 can ship before M4 — the trigger lies dormant for `mcf.*` rows in the same way. When M4 ships, the writer service composes the cert and atomically updates the version state to `active`.

**Sequencing implication:** M3 substrate can land independently. Real MCF authoring (rows pushed to `approved` or beyond) requires M4 + M5 + M7 + M8 + M9 to also be live.

### 8.5 Decision retained for DBCP

| # | Decision | Notes |
|---:|---|---|
| D-10 | Should M3 trigger validate the cert's `is_revoked` / `archived_at` is unset? | Recommendation: yes — an active MC backed by a revoked cert is structurally incoherent. Trigger should require `contract.certification_record.archived_at IS NULL` on the linked cert row. |
| D-11 | Should the `intake → draft` first-write also need a cert? | Per MCF §11.5 the cert is for governed actions. `intake → draft` is AI-default panel APPROVE, low-risk. Build plan §4.2 names `metric_create` as the cert action_code at first write. Recommendation: yes — every MC creation emits a `metric_create` cert (gate row written by M3 supplementary service or by M11 panel run service). |

---

## 9. DDL / Drizzle impact preview

### 9.1 New tables M3 creates

| Table | Approximate column count | Drizzle file |
|---|---:|---|
| `mcf.metric_contract_revision` | ~10 (per §6) | `src/database/schema/mcf/metric-contract-revision.ts` |
| `mcf.metric_supersession` | ~11 (per §7.2) | `src/database/schema/mcf/metric-supersession.ts` |

### 9.2 New triggers M3 creates

Triggers live in DDL only (Drizzle does not model triggers). Approximate list:

| Trigger name | Table | Timing / Event | Body responsibility |
|---|---|---|---|
| `trg_mcv_state_transition` | `mcf.metric_contract_version` | BEFORE UPDATE OF governance_state_code | Validate forward-only state graph; enforce hash NOT-NULL on parent at `→ approved`; verify cert exists at `→ active`; verify supersession row exists at `→ superseded` |
| `trg_mcv_active_immutability` | `mcf.metric_contract_version` | BEFORE UPDATE | Reject identity-bearing field mutation when state in (`approved`, `active`, `superseded`); reject ALL mutation when state = `superseded`; emit revision row on descriptive change when state = `active` |
| `trg_mc_active_immutability` | `mcf.metric_contract` | BEFORE UPDATE | Reject identity-bearing field mutation when any associated version is in (`approved`, `active`, `superseded`) |
| `trg_mvb_active_immutability` | `mcf.metric_variable_binding` | BEFORE UPDATE OR DELETE | Reject when parent version state in (`approved`, `active`, `superseded`) |
| `trg_mfc_active_immutability` | `mcf.metric_filter_clause` | BEFORE UPDATE OR DELETE | Same |
| `trg_mcdr_active_immutability` | `mcf.metric_computed_dimension_ref` | BEFORE UPDATE OR DELETE | Same |

### 9.3 New constraints / indexes

| Constraint / index | Table |
|---|---|
| `mcs_correction_class_chk` CHECK | `mcf.metric_supersession` — enum check on `editorial`/`meaning-bearing` |
| `mcs_rationale_min_length_chk` CHECK | `mcf.metric_supersession` — `LENGTH(rationale_text) >= 40` |
| `mcr_revision_kind_chk` CHECK | `mcf.metric_contract_revision` — closed enum (per §6.4) |
| UNIQUE idx on `(predecessor_metric_contract_uid)` | `mcf.metric_supersession` — at most one active supersession per predecessor MC |
| UNIQUE idx on `(metric_contract_version_uid, revision_seq)` | `mcf.metric_contract_revision` — sequential revisions per version |

### 9.4 No changes to existing M2 columns

M3 does **not**:
- Add NEW columns to the 5 M2 tables (the M2 substrate is sufficient; M3 wires the existing columns via triggers).
- Change M2 column nullability via ALTER COLUMN at apply time. The NOT-NULL discipline is enforced via TRIGGER, not column metadata change. This avoids touching M2 substrate definitionally.
- Modify any M2 CHECK constraint.

### 9.5 No FK additions to existing tables

M3 adds new tables; the new tables FK INTO M2 tables and `contract.certification_record`. No FKs INTO the existing M2 tables are altered.

### 9.6 Cert writer

Per build plan §4.2 Gate M3, M3 also ships the cert-write pattern for `action_code='metric_create'`. This is a **service-layer concern, not DDL**. The DBCP for M3 should specify the service function signature (likely a Node/Drizzle helper in bc-core that the M11 panel run service later calls), even though no MCF panel run service exists yet to call it.

Decision: the cert writer service can be implemented as part of the M3 PR (alongside Drizzle for the two new tables + DDL for the triggers + DDL for the cert writer's expected behavior).

---

## 10. Risks and stop conditions

### 10.1 Risks

| # | Risk | Severity | Mitigation |
|---:|---|---|---|
| R-1 | Trigger logic complexity grows beyond DBCP scope (e.g. cross-table state validation across `metric_contract` + version + bindings) | Medium | Keep triggers focused on single-row constraints. Cross-row coordination happens in service layer, not in trigger. |
| R-2 | Cert reference dependency: M3 trigger references `contract.certification_record` rows that M4 service writes. If M4 ships incomplete, `approved → active` transitions silently fail. | Medium | DBCP should specify exactly what column values and table state the trigger checks. M4 service contract is then explicit. |
| R-3 | Identity-tuple immutability collision with descriptive-revision discipline (e.g. is `temporal_gate_params_json` identity-bearing? canonicalization may treat semantically-identical JSONs as different) | Medium | DBCP must list the exact identity-bearing columns and the canonicalization rules for JSONB fields. M2 DBCP §6.3 + §8.2 specify the canonicalization rules; M3 trigger references them. |
| R-4 | Supersession atomicity bug: if successor not yet `active` when predecessor flipped, the FK to successor.version_uid would still pass at INSERT time, but the supersession-row check at predecessor's UPDATE could pass even if successor wasn't fully transitioned | Medium | Trigger must check successor's lifecycle_state at the moment of predecessor UPDATE. Both transitions wrapped in same DB transaction. |
| R-5 | Revision-table audit fidelity: the revision-table records "what changed" but not "why" without operator-supplied rationale (§6.5). Future operators auditing a revision may not understand intent. | Low | Optional rationale_text on revision; DBCP may make it required for higher-impact revision kinds (threshold_change, owner_change). Operator decision D-7. |
| R-6 | Hash NOT-NULL trigger conflict: if M7 service writes hash columns AFTER state transition to approved (instead of before), the trigger rejects the state transition. | Low | M7 service contract specifies hash write happens before state transition. DBCP names this expectation clearly. |
| R-7 | M3 ships before M4/M5/M7/M8; no actual MCF authoring exercises the triggers. Bugs may surface only at first real metric authoring (M11+). | Medium | DBCP includes positive + negative test suite covering all 5 state transitions, all immutability cases, supersession atomicity. M3 PR delivers these tests pre-apply. |

### 10.2 Stop conditions

DBCP authoring (the next gate) should STOP and re-frame if any of these surface:

- M3 trigger logic exceeds reasonable plpgsql complexity (e.g. requires recursive CTE or stored procedure call) — that signals service-layer drift. Move logic to service.
- Identity-bearing column list is operator-disputed (e.g. operator wants `description_text` to be identity-bearing). The identity tuple definition is in MCF §4.2 + DEC-c3e57f §M2; revisit M1/M2 before M3 if needed.
- Cert-reference dependency cannot be satisfied (e.g. `contract.certification_record` schema doesn't accommodate MCF action codes cleanly). Resolve at Foundation Governance Substrate level (per §17.3 + §19.10 Q26) before M3.

---

## 11. Operator decisions required before M3 execution

These are the named decisions from §3-§9 that the operator must take before the DBCP design can be authored. Numbered for ease of reference.

### 11.1 Lifecycle model decisions

| # | Decision | Recommendation |
|---:|---|---|
| D-1 | `archived_at` set automatically on supersession, or kept separate? | Keep separate (§4.4) |
| D-2 | Trigger emits `panel_output_record` row on AI-default transitions, or leave to M5? | Leave to M5 (§4.4) |

### 11.2 Immutability model decisions

| # | Decision | Recommendation |
|---:|---|---|
| D-3 | `display_name` identity-bearing or descriptive? | Descriptive (§5.3) |
| D-4 | `candidate_source_ref_json` subject to active-state immutability? | Yes — frozen post-authoring (§5.3) |
| D-5 | Ship a `freeze_version()` wrapper function, or rely on direct UPDATE? | Direct UPDATE through trigger (§5.3) |

### 11.3 Revision substrate decisions

| # | Decision | Recommendation |
|---:|---|---|
| D-6 | Closed revision_kind enum (7 elements) | Yes per §6.4 |
| D-7 | Revision requires operator-confirm rationale (≥40 char) for any kinds? | No — descriptive revisions are low-risk (§6.5) |

### 11.4 Supersession decisions

| # | Decision | Recommendation |
|---:|---|---|
| D-8 | Two-element correction_class enum (`editorial` / `meaning-bearing`) | Yes — match DEC-26b6e2 pattern (§7.5) |
| D-9 | Allow operator-initiated supersession (no panel_run_uid)? | Yes — column nullable (§7.5) |

### 11.5 Activation gate decisions

| # | Decision | Recommendation |
|---:|---|---|
| D-10 | M3 trigger checks cert's `is_revoked` / `archived_at` is unset? | Yes (§8.5) |
| D-11 | `intake → draft` (first write) emits `metric_create` cert? | Yes — per build plan §4.2 (§8.5) |

### 11.6 Cross-framework substrate decisions (deferred to operator review)

| # | Decision | Notes |
|---:|---|---|
| D-12 | Cert reuse: confirm MCF reuses `contract.certification_record` rather than getting its own `mcf.certification_record` sibling (§19.10 Q26) | Working position: reuse. DBCP can flag a re-decision opportunity if M4 implementation surfaces a clean break. |
| D-13 | Should M3's DBCP and execution PR be combined, or kept as two separate operator gates (mirroring M2's preflight → DBCP → exec PR → DDL apply pattern)? | Recommendation: keep separate. DBCP design first; implementation second; apply third. (§12) |

---

## 12. Recommended next gate

### 12.1 Recommendation: docs-only DBCP design next

**Next gate: open MCF M3 DBCP design as a docs-only operator-authorized session.** Deliverable: `bc-docs-v3/docs/implementation/metric-context-framework-m3-lifecycle-substrate-dbcp.md`, modeled on the M2 DBCP doc.

DBCP scope (the design doc, not this preflight):
- Exact column lists for `mcf.metric_contract_revision` + `mcf.metric_supersession`
- Exact trigger pseudo-code (plpgsql sketch) for all 6 triggers per §9.2
- Exact CHECK constraint definitions
- Exact index list
- Migration sequencing (ordering of DDL statements; rollback path)
- Service-layer cert writer contract (function signature for the `metric_create` cert write)
- Positive + negative test plan for the DBCP's substrate behavior
- Resolution of all 13 decisions D-1 through D-13 (preflight defaults can carry forward unless operator decides otherwise)

### 12.2 Why this matches M2's pattern

M2 ran as: preflight (`metric-context-framework-m2-preflight-decisions.md`) → DBCP design (`metric-context-framework-m2-identity-substrate-dbcp.md`) → execution PR (bc-core PR #101) → DDL apply (separate Database Change Protocol session). Four discrete operator gates.

M3 is at least as complex (triggers + 2 new tables + cert writer; 13 operator decisions in this preflight). Following the same four-gate pattern preserves the discipline that worked for M2.

### 12.3 What follows DBCP design

When the DBCP design is signed off (all 13 decisions resolved + design accepted):
1. **bc-core implementation PR** — DDL file (`docker/redesign/05-mcf-lifecycle-substrate.sql`), 2 new Drizzle schema files (`mcf/metric-contract-revision.ts` + `mcf/metric-supersession.ts`), cert writer helper, dry-run script, post-apply verifier. PR `NO DB APPLY` discipline matches M2's PR #101. **NOT OPENED in this preflight.**
2. **DDL apply** — separate operator-authorized Database Change Protocol session (matching M2's apply gate). **NOT OPENED in this preflight.**
3. **Post-apply audit artifacts** — committed to bc-core (matching M2 PR #102 pattern). **NOT OPENED in this preflight.**

### 12.4 What stays closed

- **M3 DBCP design** — operator authorizes next; not opened here.
- **M3 implementation PR** — pending DBCP sign-off.
- **M3 DDL apply** — pending implementation PR.
- **M4** (publication eligibility substrate) — depends on M3.
- **M5** (panel substrate), **M6** (tenant binding), **M7-M13** (services) — all sequenced after M3.
- **Step-4-bis** (Metrics 3 + 6 enrichment) — parallel workstream; not in this gate.
- **MCF metric contracts** — none authored; tables stay empty until M11 ships.
- **B6-v2 retrofit** — no trigger fired.
- **bc-postgres MCP write access** — unchanged (`allow_write: false`).
- **`PGMCP_SCHEMAS` `mcf` addition** — deferred until a session actually queries `mcf.*` through bc-postgres MCP (per M2 closeout §4.2).

---

## Document verification

- **All 12 required sections present** (§1 Scope and grounding; §2 Current live M2 state; §3 M3 responsibility boundary; §4 Proposed lifecycle model; §5 Immutability model; §6 Revision / audit substrate options; §7 Supersession substrate options; §8 Activation preconditions and relationship to later gates; §9 DDL / Drizzle impact preview; §10 Risks and stop conditions; §11 Operator decisions required before M3 execution; §12 Recommended next gate).
- **Discipline assertions hold** (§1.3) — zero DDL, zero bc-core schema edits, zero MCF metric contracts, no M7/M8/M9 design, no BCF writes, no Step-4-bis.
- **All 13 operator decisions enumerated** (§11) with recommended defaults — D-1 through D-13.
- **M3 boundary explicit** (§3) — 5 owned responsibilities + 11 explicit non-responsibilities.
- **Recommendation unambiguous** (§12) — docs-only DBCP design next; mirror M2's four-gate pattern.
- **No code changes, no DDL, no DB writes, no schema modifications.** Doc-only commit to bc-docs-v3 main.
