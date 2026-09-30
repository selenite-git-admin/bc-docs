-- ============================================================================
-- DRAFT reverse forward migration for bc-db 0029_mcf_retire_rejected_exit (not a bc-db file; clone-proved only) (TSK-f36519).
-- AUTHORED ONLY — a separate operator-authorized act.
--
-- FAIL-CLOSED: refuses once ANY retirement record or audit_reject_retire certificate exists.
-- Both are immutable evidence (Invariant III); after the first one, rollback is by governance
-- (stop retiring), never by DROP. Restores both certificate CHECKs to their exact pre-0029r text.
-- ============================================================================

DO $rev$
BEGIN
  IF to_regclass('mcf.rejected_version_retirement') IS NULL THEN
    RAISE EXCEPTION '0029r rollback: mcf.rejected_version_retirement is absent — nothing to roll back';
  END IF;
  IF EXISTS (SELECT 1 FROM mcf.rejected_version_retirement) THEN
    RAISE EXCEPTION '0029r rollback refused: retirement records exist (immutable) — roll back by governance, not DROP';
  END IF;
  IF EXISTS (SELECT 1 FROM mcf.certification_record WHERE action_code = 'audit_reject_retire') THEN
    RAISE EXCEPTION '0029r rollback refused: audit_reject_retire certificates exist (immutable)';
  END IF;
END
$rev$;

DROP TRIGGER trg_rre_archive_guard ON mcf.metric_contract;
DROP TABLE mcf.rejected_version_retirement;
DROP FUNCTION mcf.fn_rre_archive_guard();
DROP FUNCTION mcf.fn_rre_record_insert_guard();
DROP FUNCTION mcf.fn_rre_refuse_change();

ALTER TABLE mcf.certification_record DROP CONSTRAINT certification_record_action_state_check;
ALTER TABLE mcf.certification_record ADD CONSTRAINT certification_record_action_state_check CHECK (
     ((action_code = 'metric_create'::text) AND (from_state_code IS NULL) AND (to_state_code = 'draft'::text))
  OR ((action_code = 'metric_transition'::text) AND (from_state_code = 'approved'::text) AND (to_state_code = 'active'::text))
  OR ((action_code = 'metric_supersede'::text) AND (from_state_code = 'active'::text) AND (to_state_code = 'superseded'::text))
  OR ((action_code = 'metric_correction'::text) AND (from_state_code = 'superseded'::text) AND (to_state_code = 'active'::text))
  OR ((action_code = 'metric_correction'::text) AND (from_state_code = 'superseded'::text) AND (to_state_code = 'audit_pending'::text))
  OR ((action_code = 'audit_migrate'::text) AND (from_state_code = 'approved'::text) AND (to_state_code = 'audit_pending'::text))
  OR ((action_code = 'audit_migrate'::text) AND (from_state_code = 'active'::text) AND (to_state_code = 'audit_pending'::text))
  OR ((action_code = 'audit_reintake'::text) AND (from_state_code = 'active'::text) AND (to_state_code = 'audit_pending'::text))
  OR ((action_code = 'audit_block'::text) AND (from_state_code = 'active'::text) AND (to_state_code = 'audit_blocked'::text))
  OR ((action_code = 'audit_block'::text) AND (from_state_code = 'audit_pending'::text) AND (to_state_code = 'audit_blocked'::text))
  OR ((action_code = 'audit_remediate'::text) AND (from_state_code = 'audit_blocked'::text) AND (to_state_code = 'audit_pending'::text))
  OR ((action_code = 'audit_admit'::text) AND (from_state_code = 'audit_pending'::text) AND (to_state_code = 'active'::text))
  OR ((action_code = 'metric_approve'::text) AND (from_state_code = 'review'::text) AND (to_state_code = 'approved'::text))
  OR ((action_code = 'audit_rerequest'::text) AND (from_state_code = 'audit_pending'::text) AND (to_state_code = 'audit_pending'::text))
);
ALTER TABLE mcf.certification_record DROP CONSTRAINT certification_record_action_code_check;
ALTER TABLE mcf.certification_record ADD CONSTRAINT certification_record_action_code_check
  CHECK (action_code = ANY (ARRAY['metric_create'::text, 'metric_transition'::text, 'metric_supersede'::text,
    'metric_correction'::text, 'audit_admit'::text, 'audit_block'::text, 'audit_remediate'::text, 'audit_migrate'::text,
    'metric_approve'::text, 'audit_reintake'::text, 'audit_rerequest'::text]));

DO $revv$
BEGIN
  IF to_regclass('mcf.rejected_version_retirement') IS NOT NULL THEN RAISE EXCEPTION '0029r rollback verify: table still present'; END IF;
  IF EXISTS (SELECT 1 FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid JOIN pg_namespace n ON n.oid = c.relnamespace
             WHERE n.nspname = 'mcf' AND t.tgname LIKE 'trg\_rre\_%') THEN
    RAISE EXCEPTION '0029r rollback verify: a trg_rre_* trigger remains';
  END IF;
  IF pg_get_constraintdef((SELECT oid FROM pg_constraint WHERE conname = 'certification_record_action_code_check')) LIKE '%audit_reject_retire%' THEN
    RAISE EXCEPTION '0029r rollback verify: the action code CHECK still carries audit_reject_retire';
  END IF;
END
$revv$;

