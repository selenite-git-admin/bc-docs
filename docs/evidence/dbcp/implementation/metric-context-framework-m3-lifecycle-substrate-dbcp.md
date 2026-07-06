---
uid: metric-context-framework-m3-lifecycle-substrate-dbcp
title: MCF M3 — Lifecycle / Immutability Substrate DBCP
description: Database Change Protocol design for MCF Gate M3. Resolves all 13 preflight decisions (D-1 through D-13) and specifies the exact M3 substrate — two new tables (`mcf.metric_contract_revision`, `mcf.metric_supersession`), six BEFORE-/AFTER-UPDATE triggers across the five existing M2 tables (state-transition + immutability + revision-emit), and a cert reuse pattern over `contract.certification_record` for MCF action codes `metric_create`, `metric_transition`, `metric_supersede`. Includes column-level schemas, plpgsql trigger sketches, CHECK constraints, indexes, FK strategy, DDL apply sequence, Drizzle impact (two new schema files, zero modifications to existing M2 schemas), 14-check post-apply verifier specification, rollback story, risk assessment, and the explicit schema-boundary affirmation that `mcf.*` remains greenfield MCF authority substrate and M3 does NOT migrate or reorganize `contract.metric_contract*`, `metric.metric_binding`, or any other legacy MC corpus. Doc-only design; no DDL applied; no bc-core schema edited; no MCF metric contracts created.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m3-dbcp
---

# MCF M3 — Lifecycle / Immutability Substrate DBCP

## 1. Scope and grounding

### 1.1 Purpose

The Database Change Protocol design for MCF Gate M3. This DBCP is the implementation specification that the next gate (M3 execution PR) will realize verbatim. It resolves all 13 decisions left open in the M3 preflight (`bc-docs-v3 9e472cb`), then specifies the exact tables, triggers, constraints, indexes, DDL apply sequence, Drizzle schemas, and post-apply verifier checks.

The DBCP is **docs-only**. No DDL is applied. No bc-core source files are edited. No MCF metric contracts are created. This document is the design that an operator-authorized execution PR will later commit to bc-core, and that a subsequent Database Change Protocol session will later apply to `bc_platform_dev`.

### 1.2 What this DBCP is and is not

| | This DBCP |
|---|---|
| Is | The complete column-level specification for the two new tables + plpgsql sketches for the six triggers + the cert reuse pattern + the verifier check list. |
| Is | The formal resolution of all 13 preflight decisions with rationale. |
| Is | The DDL apply sequence and rollback story. |
| Is not | A bc-core implementation. No source file is edited; no DDL committed. |
| Is not | A DDL apply. The `psql` apply is a separate operator-authorized Database Change Protocol session. |
| Is not | An M4 / M5 / M7 / M8 / M9 design. Those gates are downstream of M3. |
| Is not | A reorganization of legacy `contract.metric_contract*` or `metric.metric_binding`. §16 affirms the schema boundary explicitly. |

### 1.3 Source documents consumed

| Source | Role | Commit / version |
|---|---|---|
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority; locks 5-state lifecycle + identity-tuple model + supersession discipline | `ADR-c3e57f.md` |
| MCF requirements §4.6, §10, §11.5, §17 | Lifecycle states, transition actor matrix, immutable-active discipline, supersession schema, active-MC 5-condition definition, Foundation Governance Substrate, table ownership | `metric-context-framework-requirements.md` |
| MCF build plan §4.2 Gate M3 | Scope: `mcf.metric_contract_revision` + `mcf.metric_supersession` + immutability triggers + cert reuse for `metric_create`; T-shirt M; primary risk supersession edge cases | `metric-context-framework-build-plan.md` |
| M2 DBCP §11 | Forward references to M3 ownership (triggers + revision + supersession + hash NOT-NULL) | `metric-context-framework-m2-identity-substrate-dbcp.md` |
| M3 preflight | 13 decisions D-1..D-13 with recommended defaults; non-responsibility list | `metric-context-framework-m3-lifecycle-substrate-preflight.md` (`9e472cb`) |
| M2 apply closeout | Live M2 state recap | `mcf-m2-ddl-apply-closeout.md` (`90d6b37`) |
| Live `contract.certification_record` schema | Column names confirmed via `pg_describe_table` (read-only this session) | `bc_platform_dev` |
| M2 Drizzle schemas | Confirmed governance_state_code placeholder + supersedes_version_uid FK + 5-state CHECK enum | `bc-core/src/database/schema/mcf/*.ts` |

### 1.4 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core file edits | ✓ — read-only this session |
| No DDL applied | ✓ — this DBCP is design-only |
| No MCF metric contracts created | ✓ — substrate stays empty |
| No legacy MC migration or reorg | ✓ — §16 affirms explicit boundary |
| No M4 / M7 / M8 / M9 design | ✓ — references-only |
| No BCF data touched | ✓ — unchanged |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

---

## 2. M2 live substrate recap

The current state in `bc_platform_dev` (post M2 apply, `2159a0e`):

| Asset | State |
|---|---|
| `mcf` schema | present |
| `mcf.metric_contract` (17 cols, 0 rows) | identity-bearing parent; hash columns nullable |
| `mcf.metric_contract_version` (15 cols, 0 rows) | descriptive body + lifecycle placeholder (`governance_state_code text NOT NULL DEFAULT 'draft'`); 5-state CHECK enum already enforced; `supersedes_version_uid` FK column already present |
| `mcf.metric_variable_binding` (13 cols, 0 rows) | per-variable bindings |
| `mcf.metric_filter_clause` (9 cols, 0 rows) | per-filter clauses |
| `mcf.metric_computed_dimension_ref` (9 cols, 0 rows) | per-computed-dim refs |
| Partial UNIQUE on `mcf.metric_contract.identity_tuple_hash` | enforced (when populated + not archived) |
| `idx_mcf_mcv_current` (UNIQUE WHERE is_current = TRUE) | enforced |
| Identity-immutability triggers | **absent** (M3 introduces) |
| State-transition triggers | **absent** (M3 introduces) |
| `mcf.metric_contract_revision` | **does not exist** (M3 creates) |
| `mcf.metric_supersession` | **does not exist** (M3 creates) |
| Foundation Governance Substrate tables — `contract.certification_record`, `contract.framework_policy`, `contract.operator_confirm_rule` | present (BCF-shared); no MCF action_code rows yet |

M3 builds on this exactly; it adds no columns to the M2 tables. The hash NOT-NULL discipline is enforced via trigger, not via `ALTER COLUMN`.

---

## 3. M3 decision log D-1 through D-13

Each preflight decision is resolved here. The DBCP design (§§4-12) implements these resolutions verbatim.

### 3.1 D-1 — `archived_at` semantics on supersession

**Decision:** KEEP SEPARATE. `archived_at` (on `mcf.metric_contract`) is the soft-delete column; `superseded` is a lifecycle terminal state. A row may be `superseded` + `archived_at IS NULL` (history-queryable) or `superseded` + `archived_at IS NOT NULL` (hidden from default views). M3 trigger does NOT auto-set `archived_at` on `active → superseded`.

**Why:** The two columns mean different things — supersession answers "is this still the current MC?", archival answers "should this row appear in default operator views?". Conflating them loses query flexibility for historical audits. The trigger also rejects `state = 'active'` + `archived_at IS NOT NULL` as an incoherent state (active rows cannot be archived without going through supersession first).

### 3.2 D-2 — Emit `panel_output_record` on AI-default transitions?

**Decision:** NO. M3 triggers permit or reject transitions only; they emit no panel-record audit. The panel itself (M5 substrate) emits its own record when it runs.

**Why:** Separation of concerns. M3 is the lifecycle gate, not the panel surface. If a transition is AI-default, the M5 panel run service writes its own audit row before invoking the state UPDATE. M3 has no business synthesizing a panel record.

### 3.3 D-3 — Is `display_name` identity-bearing or descriptive?

**Decision:** DESCRIPTIVE. The `display_name` column on `mcf.metric_contract` is the operator-facing label, separate from the structural identity tuple.

**Why:** Renaming an MC does not change what it computes. Per MCF §4.7, `display_name` is not in the identity tuple. M3 trigger does not lock `display_name` on active rows; it is updatable via the revision path (with revision-row emission per §6).

### 3.4 D-4 — Is `candidate_source_ref_json` subject to active-state immutability?

**Decision:** YES — frozen post-authoring. Once set at `intake → draft`, the column is locked across all subsequent states.

**Why:** Per DEC-c3e57f Decision 3, this column captures the reservoir provenance trigger for authoring. It is a fixed historical fact. Allowing it to mutate post-authoring would corrupt the audit trail. M3 trigger rejects any UPDATE to `candidate_source_ref_json` on a non-`draft` row.

### 3.5 D-5 — Ship a `freeze_version()` wrapper function?

**Decision:** NO. M3 ships triggers only. Service-level wrappers (e.g. `mcf_freeze_version(version_uid)`) are M7+ service concern.

**Why:** The trigger is the gate. A wrapper function would duplicate enforcement and risk drift between two code paths. Service callers can issue direct UPDATEs through the trigger.

### 3.6 D-6 — Closed `revision_kind_code` enum (7 elements)?

**Decision:** YES. Enum: `display_name_change`, `threshold_change`, `owner_change`, `function_code_change`, `description_change`, `tags_change`, `other`. CHECK constraint at substrate level.

**Why:** The descriptive columns on `mcf.metric_contract_version` are bounded; the kinds cover all current cases. `other` is the safety hatch for edge cases (e.g. multi-field bundled revisions); the DBCP recommends operator-confirm for `other`-classified revisions as a future tightening.

### 3.7 D-7 — Rationale requirement for revisions?

**Decision:** NO substrate-enforced floor on revision rationale. The `rationale_text` column is nullable; no `LENGTH ≥ 40` CHECK.

**Why:** Descriptive revisions (renaming, threshold tweak, tag change) are low-risk; requiring rationale would create friction and operator workarounds. If a specific revision kind warrants required rationale later, the DBCP amendment path adds a per-kind constraint.

### 3.8 D-8 — Two-element `correction_class_code` enum?

**Decision:** YES. Enum: `editorial` (no business-meaning change — e.g. a re-stating of the same formula in canonical form discovered during normalization) and `meaning_bearing` (genuine semantic shift). CHECK constraint at substrate.

**Why:** Mirrors DEC-26b6e2 (BCF `characteristic_supersession.correction_class`). The two-class taxonomy is sufficient for v1; finer differentiation is a future operator decision.

### 3.9 D-9 — Allow operator-initiated supersession (nullable `panel_run_uid`)?

**Decision:** YES. `panel_run_uid` on `mcf.metric_supersession` is nullable.

**Why:** Per MCF §10.5, `panel_run_uid` is "the panel run that proposed the supersession, **if AI-proposed**". Operator-initiated supersession (without a panel proposal) is a legitimate path — e.g. operator discovers a meaning-bearing correction during periodic review and directly authors a successor. The cert (always required) is the operator-confirm authority surface; the panel uid is optional metadata.

### 3.10 D-10 — Trigger checks `cert.is_archived_after IS FALSE` or NULL?

**Decision:** YES. The state-transition trigger checks `contract.certification_record.is_archived_after IS FALSE OR is_archived_after IS NULL` (treating NULL as "not yet archived"). A revoked or archived cert cannot authorize the transition.

**Why:** An active MC backed by a revoked cert is incoherent. The trigger refuses the state UPDATE rather than silently accepting it.

### 3.11 D-11 — `intake → draft` emits `metric_create` cert?

**Decision:** YES. Per build plan §4.2 Gate M3, every MC creation emits a `contract.certification_record` row with `action_code = 'metric_create'`.

**Why:** Foundation Governance Substrate consistency. Every authoring act has a cert. The cert is what later queries cite when asking "who authorized creation of this MC?". Without the cert, the MC has no certified origin.

The cert writer is a service-layer helper (e.g. `mcfCertWriter.writeCreateCert({metricContractUid, panelRunUid, certifierSub})`), shipping in the M3 execution PR alongside the DDL. M3's state-transition trigger does not enforce the `metric_create` cert (that's enforced at row-creation time by the writer service), but the trigger does enforce the `metric_transition` cert at `approved → active`.

### 3.12 D-12 — Cert reuse vs sibling table (§19.10 Q26)?

**Decision:** REUSE. MCF writes rows into `contract.certification_record` scoped by MCF `action_code` values (`metric_create`, `metric_transition`, `metric_supersede`). No `mcf.certification_record` sibling.

**Why:** Foundation Governance Substrate per MCF §17.3 explicitly intends this — neither framework owns; each writes its own scoped rows. The cert table has the shape MCF needs (action_code, from_state_code, to_state_code, primitive_type, primitive_id, panel_run_uid, gate_results_json, certifier_sub all present). If a column-shape gap surfaces at M11+ panel implementation, the operator may revisit per Q26; for now the working assumption holds.

### 3.13 D-13 — Keep DBCP and execution PR as separate gates?

**Decision:** YES. This DBCP is design-only. The implementation PR (DDL + Drizzle schema files + cert writer helper + dry-run script + post-apply verifier) is a separate operator-authorized gate.

**Why:** Pattern matches M2 (preflight → DBCP → execution PR → DDL apply across four discrete gates). Each gate has its own operator-review checkpoint. Combining DBCP + execution PR would lose the design-review checkpoint and shift the operator's veto opportunity to PR review only.

---

## 4. Proposed table: `mcf.metric_contract_revision`

### 4.1 Purpose

Per MCF §4.6 + §17.1, records descriptive-only revisions on `active` MCs. Per the immutability model (§7), revisions are emitted automatically by the AFTER-UPDATE trigger when a descriptive column changes on an active version row.

### 4.2 Column specification

| # | Column | Type | Constraints | Notes |
|---:|---|---|---|---|
| 1 | `revision_uid` | uuid | NOT NULL PRIMARY KEY DEFAULT `gen_random_uuid()` | Stable identifier |
| 2 | `metric_contract_version_uid` | uuid | NOT NULL | The version being revised |
| 3 | `revision_seq` | integer | NOT NULL CHECK (`revision_seq > 0`) | Sequential per version; trigger computes the next value |
| 4 | `revision_kind_code` | text | NOT NULL CHECK (closed enum, §3.6) | One of 7 enum values |
| 5 | `changed_fields_json` | jsonb | NOT NULL | Shape: `{ "field_name": { "from": <old>, "to": <new> } }` |
| 6 | `rationale_text` | text | NULL allowed (D-7) | Operator-supplied or service-supplied note |
| 7 | `panel_run_uid` | uuid | NULL allowed | Optional FK to M5's `mcf.metric_authoring_panel_run` when M5 ships; column already nullable so no FK at M3 |
| 8 | `revised_by_name` | text | NOT NULL | Cognito sub (operator) or service-actor name |
| 9 | `revised_at` | timestamptz | NOT NULL DEFAULT `now()` | |
| 10 | (none) | | | Total: 9 columns |

### 4.3 Constraints

| Name | Definition |
|---|---|
| `mcr_revision_kind_chk` CHECK | `revision_kind_code IN ('display_name_change', 'threshold_change', 'owner_change', 'function_code_change', 'description_change', 'tags_change', 'other')` |
| `mcr_revision_seq_chk` CHECK | `revision_seq > 0` |
| `fk_mcr_mcv` FOREIGN KEY | `(metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |

### 4.4 Indexes

| Name | Type | Definition |
|---|---|---|
| `idx_mcf_mcr_version_seq` | UNIQUE | `(metric_contract_version_uid, revision_seq)` — sequential revisions per version, gap-free at substrate level |
| `idx_mcf_mcr_mcv` | non-unique | `(metric_contract_version_uid)` — query support for "show revisions for this version" |
| `idx_mcf_mcr_revised_at` | non-unique | `(revised_at)` — chronological query support |

### 4.5 No FK to `mcf.metric_authoring_panel_run`

M5 owns that table; M3 ships before M5. The `panel_run_uid` column is structurally a UUID with no FK. When M5 ships and the table exists, a future DBCP amendment can add the FK. For M3 v1, the column is nullable + free-form UUID.

---

## 5. Proposed table: `mcf.metric_supersession`

### 5.1 Purpose

Per MCF §10.5 + §17.1, records the predecessor → successor edge of a supersession act. The supersession is the authority-bearing act that flips a predecessor from `active` to `superseded`; the row in this table is the audit + reference record.

### 5.2 Column specification

| # | Column | Type | Constraints | Notes |
|---:|---|---|---|---|
| 1 | `supersession_uid` | uuid | NOT NULL PRIMARY KEY DEFAULT `gen_random_uuid()` | Stable identifier |
| 2 | `predecessor_metric_contract_uid` | uuid | NOT NULL | The MC being superseded (parent uid) |
| 3 | `predecessor_metric_contract_version_uid` | uuid | NOT NULL | The version being superseded — the active version at supersession time |
| 4 | `successor_metric_contract_uid` | uuid | NOT NULL | The replacing MC (new identity tuple — must be a different MC) |
| 5 | `successor_metric_contract_version_uid` | uuid | NOT NULL | The replacing version |
| 6 | `correction_class_code` | text | NOT NULL CHECK (closed enum, §3.8) | `editorial` or `meaning_bearing` |
| 7 | `operator_sub` | text | NOT NULL | Cognito sub of the confirming operator |
| 8 | `rationale_text` | text | NOT NULL CHECK (`LENGTH(rationale_text) >= 40`) | High-risk supersession floor |
| 9 | `panel_run_uid` | uuid | NULL allowed (D-9) | Nullable for operator-initiated supersessions |
| 10 | `certification_record_id` | uuid | NOT NULL | FK to `contract.certification_record` (action_code='metric_supersede') |
| 11 | `superseded_at` | timestamptz | NOT NULL DEFAULT `now()` | |
| 12 | (none) | | | Total: 11 columns |

### 5.3 Constraints

| Name | Definition |
|---|---|
| `mcs_correction_class_chk` CHECK | `correction_class_code IN ('editorial', 'meaning_bearing')` |
| `mcs_rationale_min_length_chk` CHECK | `LENGTH(rationale_text) >= 40` |
| `mcs_different_mc_chk` CHECK | `predecessor_metric_contract_uid <> successor_metric_contract_uid` — supersession is between two distinct MCs, never to itself |
| `fk_mcs_pred_mc` FOREIGN KEY | `(predecessor_metric_contract_uid) REFERENCES mcf.metric_contract(metric_contract_uid) ON DELETE RESTRICT` |
| `fk_mcs_pred_mcv` FOREIGN KEY | `(predecessor_metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| `fk_mcs_succ_mc` FOREIGN KEY | `(successor_metric_contract_uid) REFERENCES mcf.metric_contract(metric_contract_uid) ON DELETE RESTRICT` |
| `fk_mcs_succ_mcv` FOREIGN KEY | `(successor_metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| `fk_mcs_cert` FOREIGN KEY | `(certification_record_id) REFERENCES contract.certification_record(certification_record_id) ON DELETE RESTRICT` |

### 5.4 Indexes

| Name | Type | Definition |
|---|---|---|
| `idx_mcf_mcs_predecessor_mc` | UNIQUE | `(predecessor_metric_contract_uid)` — at most one supersession per predecessor MC; predecessor cannot be superseded twice |
| `idx_mcf_mcs_successor_mc` | non-unique | `(successor_metric_contract_uid)` — query support: "did this MC supersede anything?" |
| `idx_mcf_mcs_superseded_at` | non-unique | `(superseded_at)` — chronological queries |

### 5.5 Why predecessor + version pair

Per the preflight §7.3, supersession is conceptually MC-level (predecessor MC replaced by successor MC). But the substrate carries both the parent UID AND the version UID for two reasons:

1. **Audit precision** — operators querying "which version was active when superseded?" can answer without inferring from timestamps.
2. **Trigger enforceability** — the state-transition trigger on `mcf.metric_contract_version` needs to look up the supersession row by version UID; carrying the version UID makes that lookup direct.

The UNIQUE index on `(predecessor_metric_contract_uid)` enforces the MC-level uniqueness; the predecessor version UID is informational.

---

## 6. Lifecycle transition model

### 6.1 State graph (locked by MCF §10.1)

```
draft → review → approved → active → superseded
```

Forward-only. No skips. No reverse transitions. `intake` is pre-substrate (no row exists yet; first INSERT creates a `draft` row).

### 6.2 Transition table

| Transition | Default actor | Substrate check (M3) | Side effect |
|---|---|---|---|
| `intake → draft` (INSERT) | AI by default | M3 trigger validates new row has `governance_state_code = 'draft'` | M3 service helper writes a `metric_create` cert (D-11) |
| `draft → review` | AI by default | M3 trigger: `OLD.state = 'draft' AND NEW.state = 'review'` | None |
| `review → approved` | AI by default | M3 trigger: `OLD.state = 'review' AND NEW.state = 'approved'` AND **parent's 6 hash columns NOT NULL** (D-11 service call writes the cert if not yet written; trigger does not write certs) | None directly; PE-MC results go into cert's `gate_results_json` (M4) |
| `approved → active` | **Operator confirm (always)** | M3 trigger: `OLD.state = 'approved' AND NEW.state = 'active'` AND `contract.certification_record` row exists with `action_code = 'metric_transition'`, `from_state_code = 'approved'`, `to_state_code = 'active'`, `primitive_id = NEW.metric_contract_version_uid`, `is_archived_after IS NOT TRUE` | M3 trigger flips `is_current = TRUE` on this row; sets prior `is_current = TRUE` row on the same parent (if any) to FALSE atomically |
| `active → superseded` | **Operator only** | M3 trigger: `OLD.state = 'active' AND NEW.state = 'superseded'` AND a matching `mcf.metric_supersession` row exists with `predecessor_metric_contract_version_uid = OLD.metric_contract_version_uid` AND successor's `lifecycle_state = 'active'` AND `is_current = TRUE` on successor | M3 trigger flips `is_current = FALSE` on this row |

### 6.3 Insert / state-graph trigger sketch

```plpgsql
CREATE OR REPLACE FUNCTION mcf.fn_mcv_state_transition_check()
RETURNS TRIGGER AS $$
DECLARE
  parent_mc record;
  has_active_cert boolean;
  has_supersession boolean;
  successor_state text;
  successor_is_current boolean;
BEGIN
  -- INSERT path: enforce new rows start at 'draft'
  IF TG_OP = 'INSERT' THEN
    IF NEW.governance_state_code <> 'draft' THEN
      RAISE EXCEPTION 'new mcf.metric_contract_version rows must start at draft, got %', NEW.governance_state_code
        USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
  END IF;

  -- UPDATE path: validate forward-only state graph
  IF OLD.governance_state_code = NEW.governance_state_code THEN
    RETURN NEW;  -- no state change; non-state mutations checked by other triggers
  END IF;

  IF NOT (
    (OLD.governance_state_code = 'draft'    AND NEW.governance_state_code = 'review')   OR
    (OLD.governance_state_code = 'review'   AND NEW.governance_state_code = 'approved') OR
    (OLD.governance_state_code = 'approved' AND NEW.governance_state_code = 'active')   OR
    (OLD.governance_state_code = 'active'   AND NEW.governance_state_code = 'superseded')
  ) THEN
    RAISE EXCEPTION 'invalid mcf state transition: % -> %', OLD.governance_state_code, NEW.governance_state_code
      USING ERRCODE = 'check_violation';
  END IF;

  -- review -> approved: parent hash columns NOT NULL
  IF NEW.governance_state_code = 'approved' THEN
    SELECT * INTO parent_mc FROM mcf.metric_contract WHERE metric_contract_uid = OLD.metric_contract_uid;
    IF parent_mc.formula_intent_hash IS NULL OR
       parent_mc.variable_binding_set_hash IS NULL OR
       parent_mc.filter_set_hash IS NULL OR
       parent_mc.identity_tuple_hash IS NULL OR
       parent_mc.package_signature_hash IS NULL OR
       parent_mc.hash_algorithm_version IS NULL THEN
      RAISE EXCEPTION 'mcf state transition to approved requires all 6 hash columns NOT NULL on parent metric_contract %', OLD.metric_contract_uid
        USING ERRCODE = 'check_violation';
    END IF;
  END IF;

  -- approved -> active: matching cert must exist
  IF NEW.governance_state_code = 'active' THEN
    SELECT EXISTS (
      SELECT 1 FROM contract.certification_record cr
      WHERE cr.primitive_type  = 'metric_contract_version'
        AND cr.primitive_id    = NEW.metric_contract_version_uid
        AND cr.action_code     = 'metric_transition'
        AND cr.from_state_code = 'approved'
        AND cr.to_state_code   = 'active'
        AND (cr.is_archived_after IS NOT TRUE)
    ) INTO has_active_cert;

    IF NOT has_active_cert THEN
      RAISE EXCEPTION 'mcf state transition to active requires a metric_transition cert for version %', NEW.metric_contract_version_uid
        USING ERRCODE = 'check_violation';
    END IF;

    -- is_current discipline: only one active version per MC
    UPDATE mcf.metric_contract_version
      SET is_current = FALSE
      WHERE metric_contract_uid = OLD.metric_contract_uid
        AND metric_contract_version_uid <> OLD.metric_contract_version_uid
        AND is_current = TRUE;
    NEW.is_current := TRUE;
  END IF;

  -- active -> superseded: supersession row must exist with active successor
  IF NEW.governance_state_code = 'superseded' THEN
    SELECT successor_v.governance_state_code, successor_v.is_current
      INTO successor_state, successor_is_current
      FROM mcf.metric_supersession s
      JOIN mcf.metric_contract_version successor_v
        ON successor_v.metric_contract_version_uid = s.successor_metric_contract_version_uid
      WHERE s.predecessor_metric_contract_version_uid = OLD.metric_contract_version_uid;

    IF successor_state IS NULL THEN
      RAISE EXCEPTION 'mcf state transition to superseded requires a metric_supersession row for version %', OLD.metric_contract_version_uid
        USING ERRCODE = 'check_violation';
    END IF;
    IF successor_state <> 'active' THEN
      RAISE EXCEPTION 'mcf supersession successor must be active; got state %', successor_state
        USING ERRCODE = 'check_violation';
    END IF;
    IF successor_is_current IS NOT TRUE THEN
      RAISE EXCEPTION 'mcf supersession successor must have is_current = TRUE'
        USING ERRCODE = 'check_violation';
    END IF;
    NEW.is_current := FALSE;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_mcf_mcv_state_transition
  BEFORE INSERT OR UPDATE OF governance_state_code ON mcf.metric_contract_version
  FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcv_state_transition_check();
```

The trigger handles INSERT (force `'draft'` start), UPDATE state-graph validation, plus the three transition-specific preconditions (hash NOT-NULL at `→ approved`, cert at `→ active`, supersession + active successor at `→ superseded`).

### 6.4 Atomicity

The trigger writes to `mcf.metric_contract_version.is_current` (for sibling rows) within the same transaction as the state UPDATE — both succeed or both roll back. The supersession case (predecessor flip + successor `is_current=TRUE` already established) is wrapped by the service layer in a single transaction; trigger checks both rows within that transaction.

---

## 7. Immutability trigger model

### 7.1 Identity-bearing columns (locked by MCF §4.2 + §10.4)

On `mcf.metric_contract` (parent):
- `grain_entity_id`
- `formula_intent_hash`
- `variable_binding_set_hash`
- `filter_set_hash`
- `temporal_gate_shape_code`
- `temporal_gate_params_json`
- `identity_tuple_hash`
- `package_signature_hash`
- `hash_algorithm_version`
- `candidate_source_ref_json` (per D-4)

On `mcf.metric_variable_binding`, `mcf.metric_filter_clause`, `mcf.metric_computed_dimension_ref`: all rows are identity-tuple inputs (their content composes into `variable_binding_set_hash` / `filter_set_hash` / etc.).

### 7.2 Trigger inventory (7 triggers across 4 tables)

| Trigger name | Table | Timing / Event | Body |
|---|---|---|---|
| `trg_mcf_mcv_state_transition` | `mcf.metric_contract_version` | BEFORE INSERT OR UPDATE OF `governance_state_code` | See §6.3. Forward-only state-graph validation + hash NOT-NULL on parent at `→ approved` + cert lookup at `→ active` + supersession-row + active-successor check at `→ superseded`. |
| `trg_mcf_mc_active_immutability` | `mcf.metric_contract` | BEFORE UPDATE | Reject change to any of the 10 identity-bearing columns when ANY associated version has `governance_state_code IN ('approved', 'active', 'superseded')` |
| `trg_mcf_mcv_descriptive_immutability` | `mcf.metric_contract_version` | BEFORE UPDATE | Reject ALL non-state changes when `OLD.governance_state_code IN ('approved', 'superseded')` — Q1 decision: approved is LOCKED; cert binds to the exact content that becomes active, so no cert/content drift. For `OLD.state = 'active'`, permit descriptive column changes only (these emit a revision row via `trg_mcf_mcv_revision_emit` per §7.5); identity-bearing columns live on the parent and are guarded by `trg_mcf_mc_active_immutability` independently. State-column UPDATEs are routed to `trg_mcf_mcv_state_transition` (separate trigger; this trigger ignores them when no other column changed). |
| `trg_mcf_mvb_active_immutability` | `mcf.metric_variable_binding` | BEFORE UPDATE OR DELETE | Reject when parent version `governance_state_code IN ('approved', 'active', 'superseded')` |
| `trg_mcf_mfc_active_immutability` | `mcf.metric_filter_clause` | BEFORE UPDATE OR DELETE | Same |
| `trg_mcf_mcdr_active_immutability` | `mcf.metric_computed_dimension_ref` | BEFORE UPDATE OR DELETE | Same |
| `trg_mcf_mcv_revision_emit` | `mcf.metric_contract_version` | AFTER UPDATE | When state was `active` and descriptive columns changed: INSERT into `mcf.metric_contract_revision` |

#### 7.2.1 Per-state mutation rules (consolidated; Q1 LOCKED resolution)

| State | Identity-bearing parent columns | Descriptive version columns | Child rows (mvb / mfc / mcdr) | Allowed state transition |
|---|---|---|---|---|
| `draft` | Mutable | Mutable | Mutable / deletable / insertable | `→ review` |
| `review` | Mutable | Mutable | Mutable / deletable / insertable | `→ approved` |
| `approved` | **LOCKED** (parent trigger) | **LOCKED** (Q1) | **LOCKED** (child triggers) | `→ active` only |
| `active` | LOCKED | Mutable (emits revision row) | LOCKED | `→ superseded` only |
| `superseded` | LOCKED | LOCKED | LOCKED | none (terminal) |

The approved-state lock (Q1) means: once `governance_state_code = 'approved'`, the only permitted UPDATE on `mcf.metric_contract_version` is the state column itself (to `'active'`). Any other UPDATE — descriptive or otherwise — is rejected by `trg_mcf_mcv_descriptive_immutability`. Child-table mutations and identity-bearing parent column mutations are rejected by their respective triggers. This guarantees the cert that authorizes `approved → active` references the exact row content that becomes active.

### 7.3 Parent immutability trigger sketch

```plpgsql
CREATE OR REPLACE FUNCTION mcf.fn_mc_active_immutability_check()
RETURNS TRIGGER AS $$
DECLARE
  past_draft_count integer;
BEGIN
  SELECT COUNT(*) INTO past_draft_count
    FROM mcf.metric_contract_version
    WHERE metric_contract_uid = OLD.metric_contract_uid
      AND governance_state_code IN ('approved', 'active', 'superseded');

  IF past_draft_count = 0 THEN
    RETURN NEW;  -- all versions still in draft/review; parent identity columns mutable
  END IF;

  -- Reject change to any identity-bearing column
  IF (OLD.grain_entity_id          IS DISTINCT FROM NEW.grain_entity_id)          OR
     (OLD.formula_intent_hash      IS DISTINCT FROM NEW.formula_intent_hash)      OR
     (OLD.variable_binding_set_hash IS DISTINCT FROM NEW.variable_binding_set_hash) OR
     (OLD.filter_set_hash          IS DISTINCT FROM NEW.filter_set_hash)          OR
     (OLD.temporal_gate_shape_code IS DISTINCT FROM NEW.temporal_gate_shape_code) OR
     (OLD.temporal_gate_params_json IS DISTINCT FROM NEW.temporal_gate_params_json) OR
     (OLD.identity_tuple_hash      IS DISTINCT FROM NEW.identity_tuple_hash)      OR
     (OLD.package_signature_hash   IS DISTINCT FROM NEW.package_signature_hash)   OR
     (OLD.hash_algorithm_version   IS DISTINCT FROM NEW.hash_algorithm_version)   OR
     (OLD.candidate_source_ref_json IS DISTINCT FROM NEW.candidate_source_ref_json) THEN
    RAISE EXCEPTION 'mcf.metric_contract.% has at least one version past-draft; identity-bearing columns are immutable', OLD.metric_contract_uid
      USING ERRCODE = 'check_violation';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_mcf_mc_active_immutability
  BEFORE UPDATE ON mcf.metric_contract
  FOR EACH ROW EXECUTE FUNCTION mcf.fn_mc_active_immutability_check();
```

The `display_name` (descriptive per D-3) is NOT in the locked list. The `archived_at`, `updated_at`, `created_at`, `created_by_name` columns are also not in the locked list (operational metadata; `archived_at` is the soft-delete column per D-1).

### 7.4 Child-table immutability triggers (3 mirror-image)

```plpgsql
CREATE OR REPLACE FUNCTION mcf.fn_mvb_active_immutability_check()
RETURNS TRIGGER AS $$
DECLARE
  parent_state text;
BEGIN
  SELECT governance_state_code INTO parent_state
    FROM mcf.metric_contract_version
    WHERE metric_contract_version_uid = COALESCE(OLD.metric_contract_version_uid, NEW.metric_contract_version_uid);

  IF parent_state IN ('approved', 'active', 'superseded') THEN
    RAISE EXCEPTION 'mcf.metric_variable_binding cannot be modified or deleted when parent version is in state %', parent_state
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_mcf_mvb_active_immutability
  BEFORE UPDATE OR DELETE ON mcf.metric_variable_binding
  FOR EACH ROW EXECUTE FUNCTION mcf.fn_mvb_active_immutability_check();
```

Identical pattern for `mcf.metric_filter_clause` and `mcf.metric_computed_dimension_ref` with their own function bodies that read the parent version state.

### 7.5 Revision-emit AFTER-UPDATE trigger

```plpgsql
CREATE OR REPLACE FUNCTION mcf.fn_mcv_revision_emit()
RETURNS TRIGGER AS $$
DECLARE
  next_seq integer;
  changed_fields jsonb := '{}'::jsonb;
  kinds text[] := ARRAY[]::text[];
  revision_kind text;
BEGIN
  -- Only fire on descriptive changes when prior state was active.
  -- (Per Q1, no descriptive changes are permitted at 'approved'; the
  -- descriptive_immutability trigger rejects them BEFORE UPDATE.)
  IF OLD.governance_state_code <> 'active' THEN
    RETURN NEW;
  END IF;

  -- Step 1: collect every changed descriptive field into `changed_fields`,
  -- and accumulate the revision_kind contribution of each into `kinds`.
  -- Each branch is independent; the final revision_kind is derived once
  -- after all contributions are gathered.

  IF OLD.description_text IS DISTINCT FROM NEW.description_text THEN
    changed_fields := changed_fields || jsonb_build_object('description_text',
      jsonb_build_object('from', OLD.description_text, 'to', NEW.description_text));
    kinds := kinds || 'description_change';
  END IF;

  IF OLD.function_code IS DISTINCT FROM NEW.function_code THEN
    changed_fields := changed_fields || jsonb_build_object('function_code',
      jsonb_build_object('from', OLD.function_code, 'to', NEW.function_code));
    kinds := kinds || 'function_code_change';
  END IF;

  IF OLD.subfunction_code IS DISTINCT FROM NEW.subfunction_code THEN
    changed_fields := changed_fields || jsonb_build_object('subfunction_code',
      jsonb_build_object('from', OLD.subfunction_code, 'to', NEW.subfunction_code));
    kinds := kinds || 'function_code_change';  -- subfunction maps to same revision kind
  END IF;

  IF OLD.owner_json IS DISTINCT FROM NEW.owner_json THEN
    changed_fields := changed_fields || jsonb_build_object('owner_json',
      jsonb_build_object('from', OLD.owner_json, 'to', NEW.owner_json));
    kinds := kinds || 'owner_change';
  END IF;

  IF OLD.tags IS DISTINCT FROM NEW.tags THEN
    changed_fields := changed_fields || jsonb_build_object('tags',
      jsonb_build_object('from', to_jsonb(OLD.tags), 'to', to_jsonb(NEW.tags)));
    kinds := kinds || 'tags_change';
  END IF;

  IF OLD.threshold_json IS DISTINCT FROM NEW.threshold_json THEN
    changed_fields := changed_fields || jsonb_build_object('threshold_json',
      jsonb_build_object('from', OLD.threshold_json, 'to', NEW.threshold_json));
    kinds := kinds || 'threshold_change';
  END IF;

  -- display_name lives on the parent mcf.metric_contract, not on the version.
  -- A display_name change goes through a separate UPDATE on the parent (which
  -- the parent immutability trigger permits because display_name is not in
  -- the identity-bearing column list per D-3). That UPDATE does not fire this
  -- trigger; if revision logging is desired for display_name changes, that's
  -- a future amendment.

  -- Step 2: bail out if nothing descriptive changed.
  IF changed_fields = '{}'::jsonb THEN
    RETURN NEW;
  END IF;

  -- Step 3: derive a single revision_kind.
  -- Rule: if all contributors point to the same kind, use that kind;
  -- otherwise this is a multi-kind UPDATE and the kind is 'other'.
  IF (SELECT COUNT(DISTINCT k) FROM unnest(kinds) k) = 1 THEN
    revision_kind := kinds[1];
  ELSE
    revision_kind := 'other';
  END IF;

  -- Step 4: compute next sequence number for this version.
  SELECT COALESCE(MAX(revision_seq), 0) + 1 INTO next_seq
    FROM mcf.metric_contract_revision
    WHERE metric_contract_version_uid = NEW.metric_contract_version_uid;

  -- Step 5: emit the revision row.
  INSERT INTO mcf.metric_contract_revision (
    metric_contract_version_uid, revision_seq, revision_kind_code,
    changed_fields_json, revised_by_name
  )
  VALUES (
    NEW.metric_contract_version_uid, next_seq, revision_kind,
    changed_fields, current_user
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_mcf_mcv_revision_emit
  AFTER UPDATE ON mcf.metric_contract_version
  FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcv_revision_emit();
```

The trigger only fires on `active`-state UPDATEs with descriptive changes. Pre-active iterations (draft / review / approved) do not emit revisions — and per Q1 (the approved-LOCKED decision per §7.2.1), no descriptive changes are even permitted at `approved`, so the trigger does not need to handle that case.

For multi-field updates, `revision_kind = 'other'` when the gathered `kinds` array contains more than one distinct value. A future DBCP amendment may split multi-field UPDATEs into one revision row per field; for v1, a single `'other'` row is acceptable.

The `revised_by_name` uses `current_user` (PostgreSQL session user). For production, the writer service should `SET LOCAL ROLE` to the Cognito sub before the UPDATE so the audit attribution is correct.

---

## 8. Hash / activation gate model

### 8.1 The 6 hash columns

| Column | M3 enforcement at `→ approved` |
|---|---|
| `mcf.metric_contract.formula_intent_hash` | NOT NULL required |
| `mcf.metric_contract.variable_binding_set_hash` | NOT NULL required |
| `mcf.metric_contract.filter_set_hash` | NOT NULL required |
| `mcf.metric_contract.identity_tuple_hash` | NOT NULL required |
| `mcf.metric_contract.package_signature_hash` | NOT NULL required |
| `mcf.metric_contract.hash_algorithm_version` | NOT NULL required |

The check is per §6.3 (state-transition trigger body). Until M7/M8 services exist to populate these, the trigger silently does nothing for `mcf.*` rows (no row reaches `→ approved` because no service exists to push it).

### 8.2 5-condition active definition (per MCF §10.7)

| # | Condition | M3 enforcement |
|---:|---|---|
| 1 | `lifecycle_state = 'active'` | Trigger validates state UPDATE = 'active' |
| 2 | `archived_at IS NULL` (parent) | Trigger checks `mcf.metric_contract.archived_at IS NULL` at `→ active` |
| 3 | Cert row exists with `action_code='metric_transition'`, `from_state_code='approved'`, `to_state_code='active'`, `primitive_id = version_uid`, `is_archived_after IS NOT TRUE` | Trigger checks (§6.3) |
| 4 | PE-MC-1..PE-MC-10 PASS (recorded in cert's `gate_results_json`) | **NOT M3-enforced**. M4 service writes the cert only after PE-MC checks pass; trigger sees the cert exists but does not validate `gate_results_json` content. |
| 5 | Identity tuple satisfies partial-unique constraint | Already enforced by M2 partial-unique index |

M3 covers structural conditions (#1, #2, #3, #5). Conditions #4 (PE-MC content) is service-level, owned by M4 cert writer; M3 trust the cert.

### 8.3 The `metric_create` cert (D-11)

The `intake → draft` transition (INSERT into `mcf.metric_contract` + `mcf.metric_contract_version` + bindings) is accompanied by a `metric_create` cert. The cert is written by an M3-shipped service helper:

```typescript
// bc-core src/registry/mcf/mcf-cert-writer.service.ts (M3 PR ships this)
export class McfCertWriterService {
  async writeMetricCreateCert(input: {
    metricContractVersionUid: string;
    panelRunUid: string | null;
    certifierSub: string;
    certifierRoleAtAction: string;
    gateResultsJson: object;
  }): Promise<{ certificationRecordId: string }> {
    // INSERT INTO contract.certification_record (
    //   primitive_type='metric_contract_version',
    //   primitive_id=input.metricContractVersionUid,
    //   action_code='metric_create',
    //   from_state_code=NULL, to_state_code='draft',
    //   certifier_sub=input.certifierSub,
    //   panel_run_uid=input.panelRunUid,
    //   gate_results_json=input.gateResultsJson,
    //   ...
    // ) RETURNING certification_record_id;
  }
}
```

The cert writer ships alongside the DDL in the M3 implementation PR. It does NOT do the table INSERT itself; that's the eventual M11 panel run service's job. The cert writer is the helper called by whichever service performs the `intake → draft` write.

**`metric_create` cert is service-contract-only at INSERT (not substrate-enforced).** M3 ships NO trigger that enforces the existence of a `metric_create` cert at the `intake → draft` INSERT — for two reasons:

1. The cert references the new version UID, which does not exist before the INSERT. A trigger that checked for a cert at INSERT time would see no row.
2. The writer service must wrap the cert INSERT and the `mcf.metric_contract` + `mcf.metric_contract_version` + child-row INSERTs in a **single DB transaction**. If the transaction commits, the cert exists; if it rolls back, neither the cert nor the MCF rows exist. Atomicity is the discipline; no trigger is needed.

This stands in contrast to the `metric_transition` and `metric_supersede` certs, which are enforced by the state-transition trigger at `→ active` and `→ superseded` respectively (§6.3) — there the cert references an existing version row whose state is about to change, so the trigger can look it up at UPDATE time.

The implication for M3: a buggy writer service that forgets to write the `metric_create` cert produces MCF rows with no audit cert. M3 substrate accepts the INSERT anyway. The only guard is the writer service's own discipline. The M11 panel run service (when it ships) is the only intended writer; its tests must cover the cert-write step.

### 8.4 The `metric_transition` and `metric_supersede` certs

These are written by M4-owned services (M4 ships the cert writers for `metric_transition` at `approved → active` and `metric_supersede` at `active → superseded`). M3 ships ONLY the `metric_create` writer and the state-transition trigger that READS these certs.

---

## 9. Certification reuse model

### 9.1 Foundation Governance Substrate

Per MCF §17.3, `contract.certification_record` is shared between BCF and MCF. BCF writes rows with `action_code` values like `registry_create`, `registry_transition`, `registry_supersede`. MCF writes rows with `action_code` values like `metric_create`, `metric_transition`, `metric_supersede`.

Neither framework reads or mutates the other's rows. The `action_code` namespace separates them; the `primitive_type` column further disambiguates (`'business_concept'` for BCF; `'metric_contract_version'` for MCF).

### 9.2 MCF action codes M3 introduces

| action_code | Purpose | from_state_code | to_state_code | Written by | Substrate enforcement at write time |
|---|---|---|---|---|---|
| `metric_create` | First write of an MC (intake → draft) | NULL | `'draft'` | M3-shipped cert writer helper (called by M11 panel run service later) | **Service-contract only** — no M3 trigger enforces the cert exists at the `mcf.metric_contract` / `mcf.metric_contract_version` INSERT. The writer service must wrap cert-write + row-INSERTs in a single transaction. See §8.3. |
| `metric_transition` | approved → active | `'approved'` | `'active'` | M4-owned cert writer service (M3 trigger reads, does not write) | Substrate-enforced — `trg_mcf_mcv_state_transition` rejects the state UPDATE unless a matching cert row exists with `is_archived_after IS NOT TRUE`. See §6.3. |
| `metric_supersede` | active → superseded | `'active'` | `'superseded'` | M4-owned cert writer service (M3 trigger reads, does not write) | Substrate-enforced — `trg_mcf_mcv_state_transition` rejects unless a matching `mcf.metric_supersession` row exists (which carries an FK to the cert via `certification_record_id`). The cert is referenced indirectly through the supersession row. See §6.3 + §5. |

### 9.3 Substrate impact

The M3 DDL does NOT alter `contract.certification_record`. The existing table accepts MCF rows by virtue of its open `action_code` text column. No new constraints; no new indexes on the cert table.

### 9.4 Open question Q26 (deferred)

Per MCF §19.10 Q26, the operator may decide later to split `contract.certification_record` into `bcf.certification_record` + `mcf.certification_record` siblings if the column shape diverges. The DBCP holds the reuse position; this is reaffirmed in D-12.

---

## 10. Indexes, constraints, and FK strategy

### 10.1 New indexes (per §4.4 + §5.4)

| Table | Index | Type |
|---|---|---|
| `mcf.metric_contract_revision` | `idx_mcf_mcr_version_seq` (UNIQUE) | `(metric_contract_version_uid, revision_seq)` |
| `mcf.metric_contract_revision` | `idx_mcf_mcr_mcv` | `(metric_contract_version_uid)` |
| `mcf.metric_contract_revision` | `idx_mcf_mcr_revised_at` | `(revised_at)` |
| `mcf.metric_supersession` | `idx_mcf_mcs_predecessor_mc` (UNIQUE) | `(predecessor_metric_contract_uid)` |
| `mcf.metric_supersession` | `idx_mcf_mcs_successor_mc` | `(successor_metric_contract_uid)` |
| `mcf.metric_supersession` | `idx_mcf_mcs_superseded_at` | `(superseded_at)` |

### 10.2 New CHECK constraints

| Table | Constraint | Definition |
|---|---|---|
| `mcf.metric_contract_revision` | `mcr_revision_kind_chk` | Closed 7-element enum |
| `mcf.metric_contract_revision` | `mcr_revision_seq_chk` | `revision_seq > 0` |
| `mcf.metric_supersession` | `mcs_correction_class_chk` | Closed 2-element enum |
| `mcf.metric_supersession` | `mcs_rationale_min_length_chk` | `LENGTH(rationale_text) >= 40` |
| `mcf.metric_supersession` | `mcs_different_mc_chk` | `predecessor_metric_contract_uid <> successor_metric_contract_uid` |

### 10.3 New FK constraints

| FK | From → To | ON DELETE |
|---|---|---|
| `fk_mcr_mcv` | `mcf.metric_contract_revision.metric_contract_version_uid` → `mcf.metric_contract_version.metric_contract_version_uid` | RESTRICT |
| `fk_mcs_pred_mc` | `mcf.metric_supersession.predecessor_metric_contract_uid` → `mcf.metric_contract.metric_contract_uid` | RESTRICT |
| `fk_mcs_pred_mcv` | `mcf.metric_supersession.predecessor_metric_contract_version_uid` → `mcf.metric_contract_version.metric_contract_version_uid` | RESTRICT |
| `fk_mcs_succ_mc` | `mcf.metric_supersession.successor_metric_contract_uid` → `mcf.metric_contract.metric_contract_uid` | RESTRICT |
| `fk_mcs_succ_mcv` | `mcf.metric_supersession.successor_metric_contract_version_uid` → `mcf.metric_contract_version.metric_contract_version_uid` | RESTRICT |
| `fk_mcs_cert` | `mcf.metric_supersession.certification_record_id` → `contract.certification_record.certification_record_id` | RESTRICT |

All FKs use ON DELETE RESTRICT to prevent accidental cascade-deletion of MCs into the audit tables (or vice versa).

### 10.4 No changes to existing M2 indexes/constraints

M3 ships exactly the new objects above plus the 6 trigger functions and 6 triggers (§7.2). The M2 partial-UNIQUE on `identity_tuple_hash` and the `idx_mcf_mcv_current` UNIQUE WHERE `is_current = TRUE` are unmodified.

---

## 11. DDL sequence

### 11.1 Apply order (FK-parent-first; trigger functions before triggers)

```sql
-- Step 1: Trigger function definitions (no triggers yet — functions referenced by triggers must exist first)
CREATE OR REPLACE FUNCTION mcf.fn_mcv_state_transition_check() RETURNS TRIGGER AS $$...$$;
CREATE OR REPLACE FUNCTION mcf.fn_mc_active_immutability_check() RETURNS TRIGGER AS $$...$$;
CREATE OR REPLACE FUNCTION mcf.fn_mcv_descriptive_immutability_check() RETURNS TRIGGER AS $$...$$;
CREATE OR REPLACE FUNCTION mcf.fn_mvb_active_immutability_check() RETURNS TRIGGER AS $$...$$;
CREATE OR REPLACE FUNCTION mcf.fn_mfc_active_immutability_check() RETURNS TRIGGER AS $$...$$;
CREATE OR REPLACE FUNCTION mcf.fn_mcdr_active_immutability_check() RETURNS TRIGGER AS $$...$$;
CREATE OR REPLACE FUNCTION mcf.fn_mcv_revision_emit() RETURNS TRIGGER AS $$...$$;

-- Step 2: New tables (mcf.metric_contract_revision must come BEFORE its trigger on mcf.metric_contract_version references it)
CREATE TABLE mcf.metric_contract_revision (...);
CREATE TABLE mcf.metric_supersession (...);

-- Step 3: Indexes on new tables
CREATE UNIQUE INDEX idx_mcf_mcr_version_seq ON mcf.metric_contract_revision (metric_contract_version_uid, revision_seq);
CREATE INDEX idx_mcf_mcr_mcv ON mcf.metric_contract_revision (metric_contract_version_uid);
CREATE INDEX idx_mcf_mcr_revised_at ON mcf.metric_contract_revision (revised_at);
CREATE UNIQUE INDEX idx_mcf_mcs_predecessor_mc ON mcf.metric_supersession (predecessor_metric_contract_uid);
CREATE INDEX idx_mcf_mcs_successor_mc ON mcf.metric_supersession (successor_metric_contract_uid);
CREATE INDEX idx_mcf_mcs_superseded_at ON mcf.metric_supersession (superseded_at);

-- Step 4: Triggers on existing M2 tables
CREATE TRIGGER trg_mcf_mc_active_immutability
  BEFORE UPDATE ON mcf.metric_contract
  FOR EACH ROW EXECUTE FUNCTION mcf.fn_mc_active_immutability_check();

CREATE TRIGGER trg_mcf_mcv_state_transition
  BEFORE INSERT OR UPDATE OF governance_state_code ON mcf.metric_contract_version
  FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcv_state_transition_check();

CREATE TRIGGER trg_mcf_mcv_descriptive_immutability
  BEFORE UPDATE ON mcf.metric_contract_version
  FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcv_descriptive_immutability_check();

CREATE TRIGGER trg_mcf_mcv_revision_emit
  AFTER UPDATE ON mcf.metric_contract_version
  FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcv_revision_emit();

CREATE TRIGGER trg_mcf_mvb_active_immutability
  BEFORE UPDATE OR DELETE ON mcf.metric_variable_binding
  FOR EACH ROW EXECUTE FUNCTION mcf.fn_mvb_active_immutability_check();

CREATE TRIGGER trg_mcf_mfc_active_immutability
  BEFORE UPDATE OR DELETE ON mcf.metric_filter_clause
  FOR EACH ROW EXECUTE FUNCTION mcf.fn_mfc_active_immutability_check();

CREATE TRIGGER trg_mcf_mcdr_active_immutability
  BEFORE UPDATE OR DELETE ON mcf.metric_computed_dimension_ref
  FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcdr_active_immutability_check();

-- Step 5: COMMENT ON TABLE / ON COLUMN annotations for the two new tables
COMMENT ON TABLE mcf.metric_contract_revision IS '...';
COMMENT ON TABLE mcf.metric_supersession IS '...';
-- Plus per-column comments per design discipline (mirroring M2 §11.5 pattern)
```

### 11.2 Single-file DDL

The implementation PR ships this as `bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql` (next file in the redesign sequence after `04-mcf-substrate.sql`). One file, sequenced as above. ON_ERROR_STOP=1 applies.

### 11.3 Idempotency

`CREATE OR REPLACE FUNCTION` is idempotent. `CREATE TABLE` and `CREATE INDEX` are not — a re-apply against an already-applied DB would error on the duplicate object names. This matches M2's discipline (M2 DDL relies on dry-run preconditions confirming the target schema is absent before apply).

The M3 dry-run script (per §13.1) confirms the two new tables and 6 triggers are absent before apply.

---

## 12. Drizzle impact preview

### 12.1 New schema files

| File | Purpose | Lines (approximate) |
|---|---|---:|
| `bc-core/src/database/schema/mcf/metric-contract-revision.ts` | Drizzle pgTable for `mcf.metric_contract_revision` | ~50 |
| `bc-core/src/database/schema/mcf/metric-supersession.ts` | Drizzle pgTable for `mcf.metric_supersession` | ~70 |

Both follow the pattern of the existing M2 Drizzle files (`metric-contract-version.ts` etc.).

### 12.2 Updated files

| File | Change |
|---|---|
| `bc-core/src/database/schema/mcf/index.ts` | Add re-exports for the two new schema modules |

### 12.3 Triggers are NOT in Drizzle

Drizzle does not model triggers, COMMENT ON TABLE, or COMMENT ON COLUMN. These live only in the DDL file. Drizzle's `pgTable` covers columns, CHECK, FK, indexes — the "shape" of the row — but not behavior.

This is the same boundary M2 hit: M2 has DDL COMMENTs that Drizzle doesn't carry, and M2 has the partial-UNIQUE WHERE clause that Drizzle expresses through `.where()` chain.

### 12.4 Cert writer service file

| File | Purpose | Lines (approximate) |
|---|---|---:|
| `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` | Service helper that writes `metric_create` cert rows | ~80 |
| `bc-core/src/registry/mcf/mcf-cert-writer.service.spec.ts` | Unit tests (Vitest) | ~120 |

The service ships alongside the DDL in the M3 implementation PR.

### 12.5 No edits to existing M2 Drizzle

The 5 M2 Drizzle schema files (`metric-contract.ts`, `metric-contract-version.ts`, `metric-variable-binding.ts`, `metric-filter-clause.ts`, `metric-computed-dimension-ref.ts`, `pg-schema.ts`) are not modified by M3. M3 adds new tables; it does not alter M2 tables.

---

## 13. Verification and test plan

### 13.1 Dry-run script (`scripts/mcf-m3-dry-run.mjs`)

Mirrors M2 pattern. 8 preconditions:

| # | Check | Pass criterion |
|---:|---|---|
| 1 | `mcf` schema present (M2 already applied) | YES |
| 2 | 5 M2 mcf tables present | YES |
| 3 | `mcf.metric_contract_revision` ABSENT (clean slate for M3 apply) | YES |
| 4 | `mcf.metric_supersession` ABSENT (clean slate for M3 apply) | YES |
| 5 | M3 trigger functions ABSENT | YES |
| 6 | M3 triggers ABSENT on the 5 M2 tables | YES |
| 7 | `contract.certification_record` schema present (Foundation Governance Substrate) | YES |
| 8 | DDL file parses and hash matches | YES |

Pre-apply DDL hash artifact, ts-stamped per M2's pattern.

### 13.2 Post-apply verifier (`scripts/mcf-m3-post-apply-verification.mjs`)

14 checks:

| # | Check | Pass criterion |
|---:|---|---|
| 1 | `mcf.metric_contract_revision` table present with 9 columns | YES |
| 2 | `mcf.metric_supersession` table present with 11 columns | YES |
| 3 | All 5 CHECK constraints present (`mcr_revision_kind_chk`, `mcr_revision_seq_chk`, `mcs_correction_class_chk`, `mcs_rationale_min_length_chk`, `mcs_different_mc_chk`) | YES |
| 4 | All 6 FK constraints present: 1 on `mcf.metric_contract_revision` (`fk_mcr_mcv`) + 5 on `mcf.metric_supersession` (`fk_mcs_pred_mc`, `fk_mcs_pred_mcv`, `fk_mcs_succ_mc`, `fk_mcs_succ_mcv`, `fk_mcs_cert`). The cert FK is one of the 5 on supersession; not counted separately. | YES |
| 5 | All 6 new indexes present (3 on revision + 3 on supersession) | YES |
| 6 | All 7 trigger functions present in `mcf` schema | YES |
| 7 | All 7 triggers attached to their target tables (1 state-transition on `mcv` + 1 immutability on `mc` + 1 descriptive immutability on `mcv` + 1 revision-emit on `mcv` + 3 child-table immutability on `mvb` / `mfc` / `mcdr`) | YES |
| 8 | Positive trigger test: INSERT into `mcf.metric_contract_version` with `governance_state_code='draft'` succeeds | YES |
| 9 | Negative trigger test: INSERT with `governance_state_code='active'` fails with check_violation | YES |
| 10 | Positive trigger test: UPDATE `governance_state_code` from `'draft'` to `'review'` succeeds | YES |
| 11 | Negative trigger test: UPDATE `governance_state_code` from `'draft'` to `'approved'` (skip review) fails | YES |
| 12 | Negative trigger test: UPDATE `governance_state_code` from `'review'` to `'approved'` when hash column NULL fails | YES |
| 13 | Negative trigger test: DELETE from `mcf.metric_variable_binding` when parent version state is `'approved'` fails | YES |
| 14 | All 5 M2 tables + 2 M3 tables empty after apply (substrate-only apply) | YES |

The trigger tests (8-13) use synthetic test rows in a transaction that's rolled back to keep the substrate empty for the empty-check at #14.

### 13.3 Test data discipline

The post-apply verifier creates ephemeral test rows inside `BEGIN; ... ROLLBACK;` blocks per assertion. No persistent test data is left in the substrate.

### 13.4 Existing M2 verifier should still PASS after M3

The 12 M2 post-apply checks (per `mcf-m2-post-apply-2026-05-26T13-01-55-568Z.summary.md`) must still PASS post-M3. The M3 implementation PR runs both verifiers as part of CI.

---

## 14. Rollback / recovery story

### 14.1 Rollback DDL (`docker/redesign/05-mcf-lifecycle-substrate-rollback.sql`)

```sql
-- Reverse order from §11.1
DROP TRIGGER IF EXISTS trg_mcf_mcdr_active_immutability ON mcf.metric_computed_dimension_ref;
DROP TRIGGER IF EXISTS trg_mcf_mfc_active_immutability ON mcf.metric_filter_clause;
DROP TRIGGER IF EXISTS trg_mcf_mvb_active_immutability ON mcf.metric_variable_binding;
DROP TRIGGER IF EXISTS trg_mcf_mcv_revision_emit ON mcf.metric_contract_version;
DROP TRIGGER IF EXISTS trg_mcf_mcv_descriptive_immutability ON mcf.metric_contract_version;
DROP TRIGGER IF EXISTS trg_mcf_mcv_state_transition ON mcf.metric_contract_version;
DROP TRIGGER IF EXISTS trg_mcf_mc_active_immutability ON mcf.metric_contract;

DROP FUNCTION IF EXISTS mcf.fn_mcv_revision_emit();
DROP FUNCTION IF EXISTS mcf.fn_mcdr_active_immutability_check();
DROP FUNCTION IF EXISTS mcf.fn_mfc_active_immutability_check();
DROP FUNCTION IF EXISTS mcf.fn_mvb_active_immutability_check();
DROP FUNCTION IF EXISTS mcf.fn_mcv_descriptive_immutability_check();
DROP FUNCTION IF EXISTS mcf.fn_mc_active_immutability_check();
DROP FUNCTION IF EXISTS mcf.fn_mcv_state_transition_check();

DROP TABLE IF EXISTS mcf.metric_supersession;
DROP TABLE IF EXISTS mcf.metric_contract_revision;
```

`IF EXISTS` makes the rollback idempotent. Indexes drop with the tables; FKs drop with their owning tables.

### 14.2 Rollback safety

The rollback is safe ONLY if `mcf.metric_contract_revision` and `mcf.metric_supersession` are empty. The post-apply verifier confirms empty state at apply time. If, between apply and a hypothetical rollback, MCF metric authoring has written real rows to these tables, the operator must FIRST archive or migrate those rows before rollback. Per CLAUDE.md Database Change Protocol, rollback is itself a substrate-change session requiring explicit operator approval.

### 14.3 Partial-apply scenario

If the DDL partially applies (e.g. table 1 created, trigger 2 fails mid-flight), the `ON_ERROR_STOP=1` flag aborts the script. The DB ends in a partial state. Recovery: rollback DDL (above) removes any partially-applied objects. Then re-investigate the failure and re-apply once root-caused.

---

## 15. Risks and stop conditions

### 15.1 Design risks (from preflight §10.1, refined)

| # | Risk | Severity | Mitigation in this DBCP |
|---:|---|---|---|
| R-1 | Trigger logic complexity | Medium | All triggers fit in <80 lines of plpgsql each. No recursive CTEs; no inter-table coordination beyond direct FK lookups. |
| R-2 | Cert reference dependency | Medium | The state-transition trigger references `contract.certification_record` columns (`primitive_id`, `action_code`, `from_state_code`, `to_state_code`, `is_archived_after`). These columns exist in the live table (read this session via `pg_describe_table`). M3 can ship before M4; the trigger remains dormant until M4 ships and starts writing certs. |
| R-3 | Identity-tuple immutability with JSONB canonicalization | Medium | M2 DBCP §6.3 + §8.2 specify canonicalization rules. M3 trigger uses `IS DISTINCT FROM` on the JSONB columns, which compares structurally. Equivalent-but-differently-formatted JSON would compare unequal; this is the desired behavior (canonical form is part of identity). |
| R-4 | Supersession atomicity | Medium | The state-transition trigger checks successor `state = 'active'` AND `is_current = TRUE` synchronously. The supersession-row INSERT and predecessor flip happen in the same transaction (service responsibility); trigger sees both within the transaction snapshot. |
| R-5 | Revision-table audit fidelity | Low | The trigger emits multi-field updates as a single `'other'`-kind revision. A future DBCP amendment can split into per-field revisions if needed. |
| R-6 | Hash NOT-NULL trigger conflict with M7/M8 service ordering | Low | The M7/M8 service contract requires hash population before state transition to `approved`. M3 trigger enforces this; the service implements the order. |
| R-7 | First-time exercise | Medium | M3 ships before M11+ services. Triggers don't fire on real rows until authoring begins. The post-apply verifier exercises triggers via ephemeral test transactions (§13.2 checks 8-13), giving high pre-apply confidence. |

### 15.2 New risks surfaced by this DBCP

| # | Risk | Mitigation |
|---|---|---|
| R-8 | `revised_by_name` uses `current_user` which may be a service role, not a Cognito sub | Service must SET LOCAL ROLE before UPDATE on `mcf.metric_contract_version` when active-row descriptive changes are made. This is a service-contract discipline; the trigger trusts `current_user`. |
| R-9 | Multi-field UPDATEs collapse into one `'other'`-kind revision | DBCP design accepts this for v1. If audit granularity is insufficient, future amendment splits into per-field revisions. |
| R-10 | Cert writer service helper requires `certifier_role_at_action` which is contextual | Service caller passes the role; DBCP defines the helper interface but does not specify the role value (caller decides). |
| R-11 | The 4 immutability triggers on child tables (`metric_variable_binding`, `metric_filter_clause`, `metric_computed_dimension_ref`) each do a separate JOIN to fetch parent state. Performance under high-volume authoring | At expected MC creation volume (≤100 / day initially), this is sub-millisecond cost per UPDATE. Index on parent FK makes the lookup index-seek. |

### 15.3 Stop conditions

The M3 implementation PR (next gate) STOPS and re-frames if any of these surface:

- DBCP review reveals a column-shape mismatch with `contract.certification_record` that the M3 design cannot accommodate → re-examine D-12 (cert reuse vs sibling)
- Trigger pseudo-code expands beyond ~150 lines per function → some logic belongs in service layer; re-scope DBCP
- Identity-bearing column list disputed by operator → revisit MCF M1 (DEC-c3e57f) before M3
- Post-apply verifier reveals a check that cannot be satisfied → STOP, document, do not proceed to apply

---

## 16. Schema-boundary note: no metric/contract reorganization

This DBCP is bounded to `mcf.*` substrate additions and the cert reuse pattern on `contract.certification_record`. It explicitly does NOT:

- Migrate `contract.metric_contract` (778/780 archived per M2 DBCP §6.3) into `mcf.metric_contract`. Legacy MC corpus stays historical per D422 Decision 2.
- Migrate `contract.metric_contract_version` (1,022 rows, 729 active on archived parents) into `mcf.metric_contract_version`. Same legacy-only treatment.
- Migrate `metric.metric_binding` (1,133 rows) into `mcf.metric_variable_binding`. The MCF substrate has variable-grain binding semantics (per §6); the legacy `metric_binding` has CC-grain semantics. Conversion would be lossy; not in scope.
- Touch `metric.metric_definition` / `metric.metric_definition_knowledge`. These tables hold KPI catalog intent (~1,819 KPIs per MCF §5.4) as background-reading-only material. They are NOT promoted to `mcf.*` and stay where they are.
- Touch `metric.metric_formula`. This is a legacy formula-shape table; the MCF formula AST (M7) substrate will be `mcf.metric_formula_ast` (a different table per build plan).
- Touch `metric.mls_state`, `metric.metric_evaluation_run`, or any runtime/evaluation table. These are evaluation-boundary substrate, not authoring substrate.
- Add any cross-schema FK from `mcf.*` to `metric.*` (the only cross-schema FK introduced is `mcf.metric_supersession.certification_record_id → contract.certification_record.certification_record_id`, which is to Foundation Governance Substrate, not to legacy MC tables).

The intent is firm: `mcf.*` is greenfield MCF authority substrate. Legacy and runtime tables stay where they are. If a future gate decides to promote a runtime/evaluation table into `mcf.*` (or split existing `metric.*` tables into MCF-authoritative vs evaluation-runtime), that's a separate operator-authorized substrate decision, NOT M3.

---

## 17. Operator approvals required before M3 execution

Before the M3 implementation PR is opened, the operator approves:

| # | Approval item |
|---:|---|
| O-1 | Confirm all 13 decisions D-1 through D-13 (§3) — accept the DBCP recommendations or override |
| O-2 | Confirm the two-table schema (`mcf.metric_contract_revision` + `mcf.metric_supersession`) is appropriate; no third table needed |
| O-3 | Confirm the 6-trigger inventory (§7.2) covers the required immutability + state-transition + revision-emit responsibilities |
| O-4 | Confirm the cert reuse pattern over `contract.certification_record` (no sibling table) — D-12 final |
| O-5 | Confirm `revised_by_name` will use the operator's Cognito sub via service-level SET ROLE; the trigger does not validate the role identity directly |
| O-6 | Confirm the schema-boundary note in §16 — no legacy MC migration in M3 scope |
| O-7 | Approve the next gate: M3 implementation PR (DDL file + 2 Drizzle schema files + cert writer service + dry-run + post-apply verifier; NO DB APPLY) |

The DBCP commit captures the design; the M3 implementation PR is the next operator-authorized session.

---

## 18. Recommended next gate

### 18.1 Recommendation: open M3 implementation PR (NO DB APPLY)

**Next gate: open the M3 implementation PR.** Deliverables (mirroring bc-core PR #101 pattern):

- `bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql` — the DDL file per §11.1
- `bc-core/docker/redesign/05-mcf-lifecycle-substrate-rollback.sql` — rollback DDL per §14.1 (optional companion file)
- `bc-core/src/database/schema/mcf/metric-contract-revision.ts` — Drizzle schema
- `bc-core/src/database/schema/mcf/metric-supersession.ts` — Drizzle schema
- `bc-core/src/database/schema/mcf/index.ts` — re-export additions
- `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` — cert writer helper for `metric_create`
- `bc-core/src/registry/mcf/mcf-cert-writer.service.spec.ts` — Vitest unit tests
- `bc-core/scripts/mcf-m3-dry-run.mjs` — 8-precondition dry-run per §13.1
- `bc-core/scripts/mcf-m3-post-apply-verification.mjs` — 14-check verifier per §13.2

PR title: `feat(mcf): M3 Lifecycle / Immutability Substrate — DDL + Drizzle + verifier (NO DB APPLY)` (mirrors PR #101).

### 18.2 Subsequent gate: M3 DDL apply

After the implementation PR merges, a separate operator-authorized session applies the DDL to `bc_platform_dev` (mirroring the M2 apply gate from earlier this arc). Per CLAUDE.md Database Change Protocol.

### 18.3 What stays closed

| | Status |
|---|---|
| M3 implementation PR | Operator authorizes next; not opened by this DBCP |
| M3 DDL apply | Pending implementation PR |
| M4 (publication eligibility substrate) | Closed; depends on M3 |
| M5 (panel substrate) | Closed |
| M6 (tenant binding) | Closed |
| M7-M13 (services) | Closed |
| MCF metric contracts | None authored; tables stay empty |
| Legacy MC migration | NOT IN M3 SCOPE (§16) |
| Step-4-bis (Metrics 3 + 6) | Parallel workstream; not in this gate |
| B6-v2 retrofit | Closed; no trigger fired |
| `bc-postgres` MCP write access | Unchanged (`allow_write: false`) |
| `PGMCP_SCHEMAS` `mcf` addition | Deferred per M2 closeout |

---

## Document verification

- **All 18 required sections present** (§1 Scope and grounding; §2 M2 live substrate recap; §3 M3 decision log D-1 through D-13; §4 Proposed table `mcf.metric_contract_revision`; §5 Proposed table `mcf.metric_supersession`; §6 Lifecycle transition model; §7 Immutability trigger model; §8 Hash / activation gate model; §9 Certification reuse model; §10 Indexes, constraints, and FK strategy; §11 DDL sequence; §12 Drizzle impact preview; §13 Verification and test plan; §14 Rollback / recovery story; §15 Risks and stop conditions; §16 Schema-boundary note: no metric/contract reorg; §17 Operator approvals required before M3 execution; §18 Recommended next gate).
- **All 13 preflight decisions resolved** in §3 with rationale.
- **Complete column-level specs** for both new tables (§4.2, §5.2).
- **Trigger pseudo-code provided** for the 4 most consequential triggers (§6.3, §7.3, §7.4, §7.5); pattern-equivalent triggers (`mfc`, `mcdr`) follow the mvb sketch.
- **Schema-boundary affirmation** (§16) — explicit list of what M3 does NOT touch.
- **No code changes, no DDL applied, no MCF metric contracts created, no bc-core file edits.** Doc-only commit to bc-docs-v3 main.
