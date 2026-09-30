-- Clone-proof vectors for migration 64 (TSK-f36519). Throwaway clone ONLY (cov-rre-proof).
-- Fixture shapes are built with SET LOCAL session_replication_role = replica (triggers skipped) and every
-- guard under test runs with triggers ON (session_replication_role = origin). Each vector runs in its own
-- transaction and ROLLS BACK, so vectors are independent; results go to proof.result.
\set ON_ERROR_STOP 1
CREATE SCHEMA proof;

-- live shapes (read live 2026-09-30): version, parent, REJECT head
CREATE TABLE proof.shape (name text, mcv uuid, parent uuid, head uuid);
INSERT INTO proof.shape SELECT c.mc_name, v.metric_contract_version_uid, v.metric_contract_uid, metric_audit.fn_decision_stream_head(v.metric_contract_version_uid)
  FROM mcf.metric_contract_version v JOIN mcf.metric_contract c USING (metric_contract_uid)
 WHERE v.metric_contract_version_uid IN ('293045c9-ed1f-48fb-aaaa-39566f91eec1','0742d6db-e112-40c4-b9ca-46dbfea97c84','3b227305-04fd-4289-b430-e7115bf1a62b','5ab06357-0580-41f1-aa81-7e8a4c388adf');

CREATE FUNCTION proof.cert(p_mcv uuid, p_code text, p_from text, p_to text) RETURNS uuid LANGUAGE plpgsql AS $$
DECLARE v uuid; pv text;
BEGIN
  SELECT policy_version INTO pv FROM mcf.certification_record ORDER BY created_at DESC LIMIT 1;
  INSERT INTO mcf.certification_record (primitive_type, primitive_id, action_code, from_state_code, to_state_code,
      certifier_sub, certifier_role_at_action, certifier_email, policy_version, subject_kind)
  VALUES ('metric_contract_version', p_mcv, p_code, p_from, p_to, 'proof-operator', 'operator', 'proof@example.invalid', pv, 'metric_contract_version')
  RETURNING certification_record_id INTO v;
  RETURN v;
END $$;

CREATE FUNCTION proof.retire(p_mcv uuid) RETURNS void LANGUAGE plpgsql AS $$  -- the act's writes, in order
DECLARE c uuid; h uuid; par uuid;
BEGIN
  h := metric_audit.fn_decision_stream_head(p_mcv);
  c := proof.cert(p_mcv, 'audit_reject_retire', 'audit_pending', 'audit_pending');
  INSERT INTO mcf.rejected_version_retirement (metric_contract_version_uid, rejected_decision_uid, certification_record_id, rationale_text, retired_by_name)
  VALUES (p_mcv, h, c, 'clone proof: panel-2 REJECT retired under the governed exit, TSK-f36519', 'proof-operator');
  SELECT metric_contract_uid INTO par FROM mcf.metric_contract_version WHERE metric_contract_version_uid = p_mcv;
  UPDATE mcf.metric_contract SET archived_at = now() WHERE metric_contract_uid = par;
END $$;

-- a superseding decision (fixture): copy the head, change code/uid/digests; REVOKE nulls the report fields
CREATE FUNCTION proof.supersede(p_mcv uuid, p_code text, p_supersede boolean DEFAULT true) RETURNS uuid LANGUAGE plpgsql AS $$
DECLARE d jsonb; nu uuid := gen_random_uuid(); h uuid;
BEGIN
  h := metric_audit.fn_decision_stream_head(p_mcv);
  SELECT to_jsonb(x) INTO d FROM metric_audit.decision x WHERE x.decision_uid = h;
  d := d || jsonb_build_object('decision_uid', nu, 'decision_code', p_code, 'feed_event_uid', gen_random_uuid(),
        'decision_payload_digest', md5(random()::text), 'decision_digest', md5(random()::text),
        'supersedes_decision_uid', CASE WHEN p_supersede THEN h::text ELSE NULL END);
  IF p_code = 'REVOKE' THEN
    d := d || jsonb_build_object('report_uid', null, 'report_digest', null, 'structural_verdict', null, 'foundation_verdict', null,
          'exactness_result', null, 'contextual_definition_score', null, 'contextual_formula_score', null,
          'contextual_input_semantics_score', null, 'contextual_overall_score', null, 'contextual_decision', null,
          'semantic_conformance_verdict', null, 'revocation_json', '{"reason":"proof"}'::jsonb);
  END IF;
  SET LOCAL session_replication_role = replica;
  INSERT INTO metric_audit.decision SELECT * FROM jsonb_populate_record(NULL::metric_audit.decision, d);
  SET LOCAL session_replication_role = origin;
  RETURN nu;
END $$;

-- probe: can an unarchived copy of this parent (same mc_name AND same identity tuple) be inserted? (rolled back)
CREATE FUNCTION proof.name_free(p_parent uuid) RETURNS boolean LANGUAGE plpgsql AS $$
BEGIN
  BEGIN
    SET LOCAL session_replication_role = replica;  -- the probe tests the unique indexes only
    INSERT INTO mcf.metric_contract SELECT * FROM jsonb_populate_record(NULL::mcf.metric_contract,
      (SELECT to_jsonb(c) || jsonb_build_object('metric_contract_uid', gen_random_uuid(), 'archived_at', null) FROM mcf.metric_contract c WHERE c.metric_contract_uid = p_parent));
    SET LOCAL session_replication_role = origin;
    RAISE EXCEPTION 'probe-ok';
  EXCEPTION WHEN unique_violation THEN SET LOCAL session_replication_role = origin; RETURN false;
            WHEN raise_exception THEN SET LOCAL session_replication_role = origin; RETURN SQLERRM = 'probe-ok';
  END;
END $$;

CREATE FUNCTION proof.try(p_sql text) RETURNS text LANGUAGE plpgsql AS $$
DECLARE msg text;
BEGIN
  BEGIN
    EXECUTE p_sql;
    RETURN 'OK';
  EXCEPTION WHEN OTHERS THEN
    GET STACKED DIAGNOSTICS msg = MESSAGE_TEXT;
    RETURN 'REFUSED: ' || left(msg, 170);
  END;
END $$;
