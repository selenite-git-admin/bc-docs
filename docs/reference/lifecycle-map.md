# Lifecycle Map — the admitted authority-creating families

**GENERATED — do not edit.** Regenerate: `node scripts/docs-control/generate_lifecycle_map.mjs`

Generated: 2026-08-03T05:58:41.904Z
Source: bc_platform_dev (live substrate, read-only)

**Authority position (DEC-5a9dee / the Authority Model ladder):** this map is a level-3
GENERATED rendering. Foundation names the families and their states (The Contract Grammar);
this map derives the transition machinery from the substrate. Map/ADR disagreement is a
finding; map/substrate disagreement means the map is stale — regenerate. Verbatim gate and
guard function bodies live in the sibling `enforcement-surface-map.md`; this map indexes
transitions to their enforcers. *Map beats memory, substrate beats map.*

## 1. MCF Metric Contract family (`mcf.metric_contract_version`)

**States (from CHECK `mcv_governance_state_chk`):** `draft` · `review` · `approved` · `active` · `superseded` · `audit_pending` · `audit_blocked`

**Transition matrix (parsed from the live `mcf.fn_mcv_state_transition_check`; the verbatim body follows):**

| # | From | To | Machine note (verbatim comment) | Disposition | Enforcing objects (bodies in the enforcement map) |
|---|---|---|---|---|---|
| 1 | `draft` | `review` | — | open (subject to listed gates) | `mcf.fn_mcv_state_transition_check` |
| 2 | `review` | `approved` | — | open (subject to listed gates) | `mcf.fn_mcv_grain_entity_version_guard`, `mcf.fn_mcv_state_transition_check` |
| 3 | `approved` | `audit_pending` | — | open (subject to listed gates) | `mcf.fn_mcv_state_transition_check` |
| 4 | `audit_pending` | `active` | C8 gate (migration 46) | open (subject to listed gates) | `mcf.fn_mcv_state_transition_check`, `metric_audit.fn_c8_require_admit_evidence` |
| 5 | `audit_pending` | `audit_blocked` | — | open (subject to listed gates) | `mcf.fn_mcv_state_transition_check` |
| 6 | `active` | `audit_blocked` | — | open (subject to listed gates) | `mcf.fn_mcv_state_transition_check` |
| 7 | `active` | `audit_pending` | C7 intake gate (migration 48 below) | open (subject to listed gates) | `mcf.fn_mcv_state_transition_check`, `metric_audit.fn_c7_require_reintake_evidence` |
| 8 | `audit_blocked` | `audit_pending` | re-audit; HARD-CLOSED below | **HARD-CLOSED** (listed, then refused) | `mcf.fn_mcv_state_transition_check` |
| 9 | `superseded` | `audit_pending` | — | open (subject to listed gates) | `mcf.fn_mcv_state_transition_check` |
| 10 | `active` | `superseded` | — | open (subject to listed gates) | `mcf.fn_mcv_state_transition_check` |

**The state machine, verbatim (ground truth for this table):**

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mcv_state_transition_check()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE parent_mc record; successor_state text; successor_is_current boolean; has_cert boolean;
        v_n int; v_approve_cert uuid;
BEGIN
  IF TG_OP = 'INSERT' THEN
    IF NEW.governance_state_code <> 'draft' THEN
      RAISE EXCEPTION 'new mcf.metric_contract_version rows must start at draft, got %', NEW.governance_state_code USING ERRCODE='check_violation'; END IF;
    RETURN NEW;
  END IF;
  IF OLD.governance_state_code = NEW.governance_state_code THEN RETURN NEW; END IF;
  IF NOT (
    (OLD.governance_state_code='draft'         AND NEW.governance_state_code='review')        OR
    (OLD.governance_state_code='review'        AND NEW.governance_state_code='approved')      OR
    (OLD.governance_state_code='approved'      AND NEW.governance_state_code='audit_pending') OR
    (OLD.governance_state_code='audit_pending' AND NEW.governance_state_code='active')        OR  -- C8 gate (migration 46)
    (OLD.governance_state_code='audit_pending' AND NEW.governance_state_code='audit_blocked') OR
    (OLD.governance_state_code='active'        AND NEW.governance_state_code='audit_blocked') OR
    (OLD.governance_state_code='active'        AND NEW.governance_state_code='audit_pending') OR  -- C7 intake gate (migration 48 below)
    (OLD.governance_state_code='audit_blocked' AND NEW.governance_state_code='audit_pending') OR  -- re-audit; HARD-CLOSED below
    (OLD.governance_state_code='superseded'    AND NEW.governance_state_code='audit_pending') OR
    (OLD.governance_state_code='active'        AND NEW.governance_state_code='superseded')
  ) THEN
    RAISE EXCEPTION 'invalid mcf state transition: % -> %', OLD.governance_state_code, NEW.governance_state_code USING ERRCODE='check_violation';
  END IF;
  -- audit_pending -> active (C8 activation gate, migration 46): ready predicate + governed audit_admit cert.
  IF OLD.governance_state_code='audit_pending' AND NEW.governance_state_code='active' THEN
    IF NOT metric_audit.fn_intrinsic_decision_ready(NEW.metric_contract_version_uid) THEN
      RAISE EXCEPTION 'audit_pending->active refused: MCV % not intrinsic-decision-ready (%)',
        NEW.metric_contract_version_uid,
        array_to_string(metric_audit.fn_intrinsic_decision_refusal(NEW.metric_contract_version_uid), ',')
        USING ERRCODE='check_violation'; END IF;
    SELECT count(*) INTO v_n FROM mcf.certification_record cr WHERE cr.primitive_type='metric_contract_version'
      AND cr.primitive_id=NEW.metric_contract_version_uid AND cr.action_code='audit_admit'
      AND cr.from_state_code='audit_pending' AND cr.to_state_code='active' AND cr.is_archived_after IS NOT TRUE;
    IF v_n = 0 THEN RAISE EXCEPTION 'audit_pending->active requires an audit_admit cert for %', NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
    IF v_n > 1 THEN RAISE EXCEPTION 'audit_pending->active: ambiguous (% non-archived audit_admit certs) for %', v_n, NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
    NEW.is_current := TRUE;
  END IF;
  -- active -> audit_pending (C7 re-audit intake gate, migration 48; cohort closure relocated by 53): open-batch ELIGIBLE-cohort
  -- membership + governed audit_reintake cert. transition_evidence is additionally required at COMMIT by
  -- trg_c7_require_reintake_evidence (deferred). is_current is demoted: the MCV leaves the live-current read
  -- surface while pending re-audit. NO request/decision/admission row is written by this edge.
  IF OLD.governance_state_code='active' AND NEW.governance_state_code='audit_pending' THEN
    IF NOT EXISTS (
      SELECT 1 FROM metric_audit.reintake_batch_member m
      JOIN metric_audit.reintake_batch b ON b.reintake_batch_uid = m.reintake_batch_uid
      JOIN metric_audit.reintake_accepted_manifest am ON am.canonical_set_hash = b.manifest_canonical_set_hash
      JOIN metric_audit.reintake_accepted_member amm ON amm.canonical_set_hash = b.manifest_canonical_set_hash
        AND amm.metric_contract_version_uid = m.metric_contract_version_uid
        AND amm.member_uid = m.member_uid AND amm.member_version_uid = m.member_version_uid AND amm.cohort = m.cohort
      WHERE m.metric_contract_version_uid = NEW.metric_contract_version_uid
        AND EXISTS (SELECT 1 FROM metric_audit.reintake_batch_cohort bc
                    WHERE bc.reintake_batch_uid = b.reintake_batch_uid
                      AND bc.cohort = m.cohort AND bc.disposition = 'eligible')
        AND b.status = 'open'
    ) THEN
      RAISE EXCEPTION 'active->audit_pending refused: MCV % is not an accepted-manifest member of an open batch in a cohort AUTHORIZED ELIGIBLE for that batch, bound to the pinned accepted hash', NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
    SELECT count(*) INTO v_n FROM mcf.certification_record cr WHERE cr.primitive_type='metric_contract_version'
      AND cr.primitive_id=NEW.metric_contract_version_uid AND cr.action_code='audit_reintake'
      AND cr.from_state_code='active' AND cr.to_state_code='audit_pending' AND cr.is_archived_after IS NOT TRUE;
    IF v_n = 0 THEN RAISE EXCEPTION 'active->audit_pending requires an audit_reintake cert for %', NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
    IF v_n > 1 THEN RAISE EXCEPTION 'active->audit_pending: ambiguous (% audit_reintake certs) for %', v_n, NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
    NEW.is_current := FALSE;
  END IF;
  -- HARD-CLOSED edge (still owned by a later unit)
  IF OLD.governance_state_code='audit_blocked' AND NEW.governance_state_code='audit_pending' THEN
    RAISE EXCEPTION 'audit_blocked->audit_pending (re-audit) is hard-closed until the governed CR/NC substrate lands (C2.5/C7)' USING ERRCODE='check_violation'; END IF;
  -- review -> approved: parent hash columns NOT NULL (unchanged) + C5 IC-3 metric_approve cert & bound snapshot
  IF NEW.governance_state_code='approved' THEN
    SELECT * INTO parent_mc FROM mcf.metric_contract WHERE metric_contract_uid = OLD.metric_contract_uid;
    IF parent_mc.formula_intent_hash IS NULL OR parent_mc.variable_binding_set_hash IS NULL OR parent_mc.filter_set_hash IS NULL
       OR parent_mc.identity_tuple_hash IS NULL OR parent_mc.package_signature_hash IS NULL OR parent_mc.hash_algorithm_version IS NULL THEN
      RAISE EXCEPTION 'mcf state transition to approved requires all 6 hash columns NOT NULL on parent mcf.metric_contract %', OLD.metric_contract_uid USING ERRCODE='check_violation'; END IF;
    SELECT count(*), (array_agg(cr.certification_record_id))[1] INTO v_n, v_approve_cert
      FROM mcf.certification_record cr
      WHERE cr.primitive_type='metric_contract_version' AND cr.primitive_id=NEW.metric_contract_version_uid
        AND cr.action_code='metric_approve' AND cr.from_state_code='review' AND cr.to_state_code='approved'
        AND cr.is_archived_after IS NOT TRUE;
    IF v_n = 0 THEN
      RAISE EXCEPTION 'review->approved requires a metric_approve cert for %', NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
    IF v_n > 1 THEN
      RAISE EXCEPTION 'review->approved: ambiguous (% metric_approve certs) for %', v_n, NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
    SELECT count(*) INTO v_n FROM mcf.mcv_package_snapshot s
      WHERE s.metric_contract_version_uid = NEW.metric_contract_version_uid
        AND s.approval_certification_id = v_approve_cert AND s.disposition_source='approval';
    IF v_n <> 1 THEN
      RAISE EXCEPTION 'review->approved requires exactly one approval mcv_package_snapshot bound to the metric_approve cert for % (found %)', NEW.metric_contract_version_uid, v_n USING ERRCODE='check_violation'; END IF;
  END IF;
  -- approved -> audit_pending: audit_migrate cert (the C2 request appender wires the outbox row in the same tx)
  IF OLD.governance_state_code='approved' AND NEW.governance_state_code='audit_pending' THEN
    SELECT EXISTS (SELECT 1 FROM mcf.certification_record cr WHERE cr.primitive_type='metric_contract_version'
      AND cr.primitive_id=NEW.metric_contract_version_uid AND cr.action_code='audit_migrate'
      AND cr.from_state_code='approved' AND cr.to_state_code='audit_pending' AND cr.is_archived_after IS NOT TRUE) INTO has_cert;
    IF NOT has_cert THEN RAISE EXCEPTION 'approved->audit_pending requires an audit_migrate cert for %', NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
  END IF;
  -- superseded -> audit_pending: governed recovery, metric_correction cert (C1 cause=metric_correction)
  IF OLD.governance_state_code='superseded' AND NEW.governance_state_code='audit_pending' THEN
    SELECT EXISTS (SELECT 1 FROM mcf.certification_record cr WHERE cr.primitive_type='metric_contract_version'
      AND cr.primitive_id=NEW.metric_contract_version_uid AND cr.action_code='metric_correction'
      AND cr.from_state_code='superseded' AND cr.to_state_code='audit_pending' AND cr.is_archived_after IS NOT TRUE) INTO has_cert;
    IF NOT has_cert THEN RAISE EXCEPTION 'superseded->audit_pending requires a metric_correction cert for %', NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
  END IF;
  -- (active|audit_pending) -> audit_blocked: audit_block cert; active case demotes is_current
  IF NEW.governance_state_code='audit_blocked' THEN
    SELECT EXISTS (SELECT 1 FROM mcf.certification_record cr WHERE cr.primitive_type='metric_contract_version'
      AND cr.primitive_id=NEW.metric_contract_version_uid AND cr.action_code='audit_block'
      AND cr.from_state_code=OLD.governance_state_code AND cr.to_state_code='audit_blocked' AND cr.is_archived_after IS NOT TRUE) INTO has_cert;
    IF NOT has_cert THEN RAISE EXCEPTION '%->audit_blocked requires an audit_block cert for %', OLD.governance_state_code, NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
    IF OLD.governance_state_code='active' THEN NEW.is_current := FALSE; END IF;
  END IF;
  -- active -> superseded: supersession row + active successor required (unchanged)
  IF NEW.governance_state_code='superseded' THEN
    SELECT successor_v.governance_state_code, successor_v.is_current INTO successor_state, successor_is_current
      FROM mcf.metric_supersession s JOIN mcf.metric_contract_version successor_v
        ON successor_v.metric_contract_version_uid = s.successor_metric_contract_version_uid
      WHERE s.predecessor_metric_contract_version_uid = OLD.metric_contract_version_uid;
    IF successor_state IS NULL THEN RAISE EXCEPTION 'mcf state transition to superseded requires a mcf.metric_supersession row for version %', OLD.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
    IF successor_state <> 'active' THEN RAISE EXCEPTION 'mcf supersession successor must be active; got state %', successor_state USING ERRCODE='check_violation'; END IF;
    IF successor_is_current IS NOT TRUE THEN RAISE EXCEPTION 'mcf supersession successor must have is_current = TRUE' USING ERRCODE='check_violation'; END IF;
    NEW.is_current := FALSE;
  END IF;
  RETURN NEW;
END $function$
```

**Certification-action gates on this family** (bodies in `enforcement-surface-map.md`):
the C6 invalidation cascade (`metric_audit.fn_c6_run_cascade` — entry to `audit_blocked`),
the C7 reintake evidence + accepted-manifest/batch gates (`metric_audit.fn_c7_require_reintake_evidence`,
reintake batch/member guards — `active → audit_pending`), and the C8 activation gate
(`metric_audit.fn_c8_require_admit_evidence` + `fn_intrinsic_decision_ready` — `audit_pending → active`).

## 2. Business Concept Registry family (`concept_registry.*`)

### `concept_registry.business_concept`

- CHECK `business_concept_active_version_required_chk`: `CHECK (((lifecycle_state = 'draft'::text) OR (active_version_id IS NOT NULL)))`
- CHECK `business_concept_archived_coherence_chk`: `CHECK (((archived_at IS NULL) OR (lifecycle_state = 'archived'::text)))`
- CHECK `business_concept_lifecycle_chk`: `draft` · `review` · `approved` · `active` · `superseded` · `archived`
- trigger `trg_business_concept_acyclic` → `tg_business_concept_acyclic`
- trigger `trg_business_concept_d443_active_version_role_required` → `tg_business_concept_d443_active_version_role_required`
- trigger `trg_business_concept_meaning_immutable` → `tg_business_concept_meaning_immutable`

### `concept_registry.business_concept_version`

- CHECK `business_concept_version_semantic_role_chk`: `strategic_filter` · `diagnostic` · `identity` · `temporal` · `amount` · `status` · `dimension` · `reference`
- trigger `trg_business_concept_version_d443_role_required` → `tg_business_concept_version_d443_role_required`
- trigger `trg_business_concept_version_d6_1_value_set_required` → `tg_business_concept_version_d6_1_value_set_required`
- trigger `trg_business_concept_version_immutable` → `tg_reject_version_mutation`
- trigger `trg_business_concept_version_kind_role_chk` → `tg_business_concept_version_kind_role_chk`

### `concept_registry.characteristic`

- CHECK `characteristic_archived_coherence_chk`: `CHECK (((archived_at IS NULL) OR (lifecycle_state = 'archived'::text)))`
- CHECK `characteristic_lifecycle_chk`: `draft` · `review` · `approved` · `active` · `superseded` · `archived`

### `concept_registry.characteristic_definition_amendment`

- CHECK `characteristic_definition_amendment_correction_class_chk`: `CHECK ((correction_class = 'editorial'::text))`

### `concept_registry.characteristic_supersession`

- CHECK `characteristic_supersession_correction_class_chk`: `editorial` · `meaning_bearing`

### `concept_registry.entity`

- CHECK `entity_active_version_required_chk`: `CHECK (((lifecycle_state = 'draft'::text) OR (active_version_id IS NOT NULL)))`
- CHECK `entity_lifecycle_chk`: `draft` · `review` · `approved` · `active` · `superseded`

### `concept_registry.entity_version`

- trigger `trg_entity_version_immutable` → `tg_reject_version_mutation`

### `concept_registry.supersession_proposal`

- CHECK `supersession_proposal_outcome_link_chk`: `CHECK ((((proposal_status = 'actioned'::text) AND (resolution_supersession_id IS NOT NULL)) OR ((proposal_status <> 'actioned'::text) AND (resolution_supersessi`
- CHECK `supersession_proposal_resolution_chk`: `actioned` · `dismissed`
- CHECK `supersession_proposal_status_chk`: `open` · `actioned` · `dismissed`

**Honest gap (derived by absence):** the registry substrate above enforces state
VOCABULARY, immutability, and amendment-class rules; no DB-side transition-ORDER guard
exists for concept governance states. Transition order is enforced in the governed services
(FrameworkApprovalService / operatorAdvance per DEC-47a4e7; supersession cascade per
DEC-9d27a9; withdrawal per DEC-1fbaf1). This is a fact of the current substrate, rendered
here so it can never be assumed otherwise.

## 3. Metric Directory Member family (`metric_directory.*`)

### `metric_directory.directory_decision`

- CHECK `chk_dd_kind`: `rationale` · `disposition` · `deferral` · `debate` · `approval` · `rejection`
- trigger `trg_directory_decision_immutable` → `tg_directory_decision_immutable`

### `metric_directory.family`

- trigger `trg_family_frozen` → `fn_family_frozen_guard`

### `metric_directory.family_version`

- trigger `trg_family_version_head` → `fn_family_version_head_guard`
- trigger `trg_family_version_immutable` → `fn_reject_mutation`

### `metric_directory.group`

- CHECK `chk_group_class`: `base` · `derived`
- trigger `trg_group_frozen` → `fn_group_frozen_guard`

### `metric_directory.group_version`

- CHECK `group_version_class_code_check`: `base` · `derived`
- trigger `trg_group_version_head` → `fn_group_version_head_guard`
- trigger `trg_group_version_immutable` → `fn_reject_mutation`

### `metric_directory.member`

- CHECK `chk_member_blocked`: `CHECK (((intent_state_code = 'blocked'::text) = (blocker_code IS NOT NULL)))`
- CHECK `chk_member_class`: `base` · `derived`
- CHECK `chk_member_derivation_class`: `CHECK (((derivation_json IS NULL) OR (class_code = 'derived'::text)))`
- CHECK `chk_member_intent`: `planned` · `blocked`
- trigger `trg_member_frozen` → `fn_member_frozen_guard`
- trigger `trg_member_grain_preserve` → `fn_member_grain_preserve_guard`
- trigger `trg_member_legacy_pointer` → `fn_legacy_pointer_freeze`

### `metric_directory.member_feasibility_result`

- trigger `trg_feasibility_head` → `fn_feasibility_head_guard`
- trigger `trg_member_feasibility_result_immutable` → `fn_reject_mutation`

### `metric_directory.member_knowledge`

- trigger `trg_member_knowledge_frozen` → `fn_member_knowledge_frozen_guard`

### `metric_directory.member_version`

- CHECK `member_version_class_code_check`: `base` · `derived`
- trigger `trg_member_version_finalize` → `fn_member_version_finalize`
- trigger `trg_member_version_head` → `fn_member_version_head_guard`
- trigger `trg_member_version_immutable` → `fn_reject_mutation`

### `metric_directory.member_version_constant`

- trigger `trg_const_finalize` → `fn_child_finalize_guard`
- trigger `trg_constant_value` → `fn_constant_value_guard`
- trigger `trg_member_version_constant_immutable` → `fn_reject_mutation`

### `metric_directory.member_version_dependency`

- trigger `trg_dep_finalize` → `fn_child_finalize_guard`
- trigger `trg_dependency_dag` → `fn_dependency_dag_guard`
- trigger `trg_member_version_dependency_immutable` → `fn_reject_mutation`

### `metric_directory.member_version_direct_input`

- trigger `trg_di_finalize` → `fn_child_finalize_guard`
- trigger `trg_member_version_direct_input_immutable` → `fn_reject_mutation`

### `metric_directory.member_version_discriminator`

- trigger `trg_disc_finalize` → `fn_child_finalize_guard`
- trigger `trg_member_version_discriminator_immutable` → `fn_reject_mutation`

### `metric_directory.migration_batch`

- trigger `trg_batch_close` → `fn_batch_close_guard`
- trigger `trg_batch_nodelete` → `fn_reject_mutation`

### `metric_directory.migration_disposition_event`

- CHECK `disp_shape`: `nc_raised` · `skipped`
- CHECK `migration_disposition_event_disposition_check`: `migrated` · `nc_raised` · `skipped`
- trigger `trg_migration_disposition` → `fn_migration_disposition_guard`
- trigger `trg_migration_disposition_event_immutable` → `fn_reject_mutation`

### `metric_directory.migration_manifest_member`

- trigger `trg_migration_manifest_member_immutable` → `fn_reject_mutation`

### `metric_directory.off_pool_exception_event`

- trigger `trg_off_pool` → `fn_off_pool_guard`
- trigger `trg_off_pool_exception_event_immutable` → `fn_reject_mutation`
- trigger `trg_off_pool_operative` → `fn_off_pool_operative_maint`

### `metric_directory.realization_event`

- trigger `trg_realization_event` → `fn_realization_event_guard`
- trigger `trg_realization_event_immutable` → `fn_reject_mutation`
- trigger `trg_realization_operative` → `fn_realization_operative_maint`

**Family doctrine rendered against substrate (DEC-b5c7ff, admitted per DEC-5a9dee):** a
Member owns INTENT state only; realized state is DERIVED through the realization relation
(`metric_directory.realization_operative` → `mcf.metric_contract_version`), never cached.
Directory identity is load-bearing for MCF lifecycle acts: the C7 accepted-member tuple
requires `member_uid` + `member_version_uid` (operative proof: DEC-21ca17).

## 4. The cross-family lifecycle spine (derived reading order)

Intent is authored in the Directory (member intent states) → meaning is bound in the
Business Concept Registry (concept governance states; contract bodies reference concepts
structurally) → the contract lives in MCF (seven states; certification gates activation at
C8; C6 invalidates; C7 reintakes) → runtime consumers read `active` (selection into
evaluation; readiness projection renders the certified/residue/unattributed split).
Each arrow is a REFERENCE between families, never shared state — the families are decoupled
by design (operator doctrine, 2026-08-03).
