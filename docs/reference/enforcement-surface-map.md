# Enforcement Surface Map

**GENERATED — do not edit.** Regenerate: `node scripts/docs-control/generate_enforcement_surface_map.mjs`

Generated: 2026-07-26T04:23:34.260Z
Sources: bc_platform_dev + bc_audit_dev (live), bc-core@c923f2a, auditor@3230390

**Usage rule (operator, 2026-07-26):** no design, no ADR applied-instance, and no population count
is claimed without citing this map. Counts are computed from the gate predicates below, never from
proxy tables. When the map disagrees with a memory or a memo, the map wins; when the live substrate
disagrees with the map, REGENERATE, then the substrate wins.

## 1. Platform gate + guard functions (`metric_audit.*`) — VERBATIM

### `metric_audit.admission_evidence_digest`

```sql
CREATE OR REPLACE FUNCTION metric_audit.admission_evidence_digest(p_mcv uuid, p_decision uuid, p_request uuid, p_expected text, p_recomputed text, p_closure text, p_supersedes uuid, p_actor text)
 RETURNS text
 LANGUAGE sql
 IMMUTABLE
 SET search_path TO 'pg_catalog'
AS $function$
  SELECT 'sha256:' || encode(sha256(convert_to(jsonb_build_object(
    'schema_version', 'bc-admission-recomputation-evidence-v1',
    'metric_contract_version_uid', p_mcv,
    'effective_decision_uid', p_decision,
    'request_uid', p_request,
    'expected_snapshot_signature_hash', p_expected,
    'recomputed_package_signature_hash', p_recomputed,
    'recomputed_closure_root', p_closure,
    'supersedes_evidence_uid', p_supersedes,
    'actor', p_actor
  )::text, 'UTF8')), 'hex')
$function$
```

### `metric_audit.fn_admission_evidence_guard`

Reads/writes: `metric_audit.admission_recomputation_evidence`, `metric_audit.decision`, `new.effective_decision_uid`, `new.metric_contract_version_uid`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_admission_evidence_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE pred metric_audit.admission_recomputation_evidence%ROWTYPE;
BEGIN
  NEW.recompute_txid := txid_current();  -- DB-owned
  NEW.recomputed_at  := now();           -- DB-owned
  IF NEW.evidence_digest <> metric_audit.admission_evidence_digest(
       NEW.metric_contract_version_uid, NEW.effective_decision_uid, NEW.request_uid,
       NEW.expected_snapshot_signature_hash, NEW.recomputed_package_signature_hash,
       NEW.recomputed_closure_root, NEW.supersedes_evidence_uid, NEW.actor) THEN
    RAISE EXCEPTION 'admission_recomputation_evidence evidence_digest != DB-recomputed semantic identity (forged/tampered column)'
      USING ERRCODE='check_violation'; END IF;
  -- the effective decision must target this MCV (relational closure)
  IF NOT EXISTS (SELECT 1 FROM metric_audit.decision d
                 WHERE d.decision_uid = NEW.effective_decision_uid
                   AND d.metric_contract_version_uid = NEW.metric_contract_version_uid) THEN
    RAISE EXCEPTION 'admission evidence effective_decision % does not target mcv %',
      NEW.effective_decision_uid, NEW.metric_contract_version_uid; END IF;
  -- supersession stays within the SAME (mcv, effective_decision) stream (no cross-stream supersession)
  IF NEW.supersedes_evidence_uid IS NOT NULL THEN
    IF NEW.supersedes_evidence_uid = NEW.evidence_uid THEN
      RAISE EXCEPTION 'admission evidence must not supersede itself'; END IF;
    SELECT * INTO pred FROM metric_audit.admission_recomputation_evidence WHERE evidence_uid = NEW.supersedes_evidence_uid;
    IF pred.evidence_uid IS NULL THEN
      RAISE EXCEPTION 'admission evidence supersedes a non-existent predecessor %', NEW.supersedes_evidence_uid; END IF;
    IF pred.metric_contract_version_uid IS DISTINCT FROM NEW.metric_contract_version_uid
       OR pred.effective_decision_uid IS DISTINCT FROM NEW.effective_decision_uid THEN
      RAISE EXCEPTION 'admission evidence cross-stream supersession refused (predecessor is a different (mcv, decision) stream)'; END IF;
  END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_admission_evidence_head`

Reads/writes: `metric_audit.admission_recomputation_evidence`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_admission_evidence_head(p_mcv uuid, p_decision uuid)
 RETURNS uuid
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE v_n int; v_uid uuid;
BEGIN
  SELECT count(*), (array_agg(e.evidence_uid))[1] INTO v_n, v_uid
    FROM metric_audit.admission_recomputation_evidence e
   WHERE e.metric_contract_version_uid = p_mcv AND e.effective_decision_uid = p_decision
     AND NOT EXISTS (SELECT 1 FROM metric_audit.admission_recomputation_evidence s
                     WHERE s.supersedes_evidence_uid = e.evidence_uid);
  IF v_n > 1 THEN RAISE EXCEPTION 'admission evidence stream fork: % un-superseded heads for (mcv %, decision %)', v_n, p_mcv, p_decision; END IF;
  RETURN v_uid;  -- NULL when none
END $function$
```

### `metric_audit.fn_admission_evidence_immutability`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_admission_evidence_immutability()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN
  RAISE EXCEPTION 'metric_audit.admission_recomputation_evidence is append-only (% refused, Invariant III)', TG_OP USING ERRCODE='check_violation';
END $function$
```

### `metric_audit.fn_artifact_import_guard`

Reads/writes: `new.exception_class`, `new.exception_version_uid`, `new.issued_at`, `new.metric_contract_version_uid`, `new.package_signature_hash`, `new.schema_version`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_artifact_import_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE p jsonb;
BEGIN
  IF NEW.payload_digest <> 'sha256:' || encode(sha256(NEW.payload_bytes),'hex') THEN RAISE EXCEPTION 'payload_digest != sha256(payload_bytes)'; END IF;
  p := convert_from(NEW.payload_bytes,'UTF8')::jsonb;
  IF p->>'schema_version' IS DISTINCT FROM NEW.schema_version OR p->>'exception_version_uid' IS DISTINCT FROM NEW.exception_version_uid
     OR (p->>'metric_contract_version_uid')::uuid IS DISTINCT FROM NEW.metric_contract_version_uid
     OR p->>'package_signature_hash' IS DISTINCT FROM NEW.package_signature_hash
     OR p->>'exception_class' IS DISTINCT FROM NEW.exception_class
     OR (p->>'issued_at')::timestamptz IS DISTINCT FROM NEW.issued_at THEN
    RAISE EXCEPTION 'import columns do not match the signed payload'; END IF;
  IF NOT metric_audit.fn_signer_key_valid_at(NEW.signer_key_id, NEW.issued_at) THEN RAISE EXCEPTION 'signer key % not valid at %', NEW.signer_key_id, NEW.issued_at; END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_authority_pin_supersede`

Reads/writes: `metric_audit.intrinsic_authority_pin`, `metric_audit.intrinsic_authority_pin_event`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_authority_pin_supersede(p_coordinates jsonb, p_expected_successor_digest text, p_methodology_release_ratification_ref text, p_methodology_release_ratification_sha256 text, p_operator_authorization_ref text, p_operator_authorization_sha256 text, p_accepted_review_response_ref text, p_accepted_review_response_sha256 text, p_reason text, p_created_by text)
 RETURNS uuid
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE v_pred uuid; v_canonical text; v_computed text; v_new uuid; v_resolved uuid;
BEGIN
  -- 1. singular current pin, locked
  v_pred := metric_audit.fn_intrinsic_authority_pin_current();
  IF v_pred IS NULL THEN
    RAISE EXCEPTION 'authority-pin supersede refused: no singular current pin' USING ERRCODE='check_violation'; END IF;
  PERFORM 1 FROM metric_audit.intrinsic_authority_pin WHERE pin_uid = v_pred FOR UPDATE;
  -- 1b. HARD-BIND to the exact accepted methodology-v2 move (P0-1 remediation). This is a ONE-SHOT
  --     v1 -> v2 writer, NOT a generic repin: even the owner cannot supersede to arbitrary authority
  --     coordinates. The authority-determining fields are fixed constants (predecessor, successor
  --     coordinates, successor pin digest, accepted M1A methodology-release ratification SHA). It is
  --     inherently one-shot: once v2 is current, v_pred is no longer the v1 pin and this refuses.
  --     (The M4-accepted-response SHA and operator-authorization SHA are M5-time values, required +
  --     format-checked here and bound to their exact accepted values by the M5 apply DBCP.)
  IF v_pred <> 'f14d28fc-3e78-498d-97f2-e4017fd3cc79'::uuid THEN
    RAISE EXCEPTION 'authority-pin supersede refused: predecessor % is not the accepted v1 pin (one-shot v1->v2 only)', v_pred USING ERRCODE='check_violation'; END IF;
  IF p_expected_successor_digest <> 'sha256:3b9278f47d9bd039d74f5f7cb3f01038664b49e395ff2a2aecb51f62bcc989fe' THEN
    RAISE EXCEPTION 'authority-pin supersede refused: only the accepted v2 successor digest is permitted' USING ERRCODE='check_violation'; END IF;
  IF p_coordinates->>'methodology_version'          IS DISTINCT FROM 'bc-metric-intrinsic-audit-methodology-v2'
     OR p_coordinates->>'methodology_digest'        IS DISTINCT FROM 'sha256:1ac88cf1161e5b11df1db301e8a65ffa08ab6a700e3da7faa4d9fd42b3e7cce9'
     OR p_coordinates->>'source_authority_revision' IS DISTINCT FROM 'source-authority-policy-v1.r3'
     OR p_coordinates->>'authority_revision'        IS DISTINCT FROM 'bc-docs@94a0e05751674b380f269453f87b93e62c4aa96f'
     OR p_coordinates->>'source_authority_policy_digest' IS DISTINCT FROM 'sha256:84a09eb4039634f921b45b6f6562b475037cc41c082e2ad72811d1b9f88948d2'
     OR p_coordinates->>'package_hash_algorithm'    IS DISTINCT FROM 'mcf-package-v3'
     OR p_coordinates->>'engine'                    IS DISTINCT FROM 'bc-external-audit'
     OR p_coordinates->>'engine_version'            IS DISTINCT FROM '0.4.0'
     OR p_coordinates->>'gate_policy_version'       IS DISTINCT FROM 'bc-d523-intrinsic-admission-gate-v1' THEN
    RAISE EXCEPTION 'authority-pin supersede refused: coordinates are not the exact accepted v2 successor move' USING ERRCODE='check_violation'; END IF;
  IF p_methodology_release_ratification_sha256 <> 'sha256:b3c87bac35ee6580048890071d862a961cac3955ebd3f50b539cd00ae54a9995' THEN
    RAISE EXCEPTION 'authority-pin supersede refused: methodology-release ratification SHA is not the accepted M1A value' USING ERRCODE='check_violation'; END IF;
  -- 2. digest recompute over the canonical object (defense in depth: computed == expected == 3b9278)
  SELECT '{' || string_agg(to_json(k)::text || ':' || to_json(val)::text, ',' ORDER BY k COLLATE "C") || '}'
    INTO v_canonical
    FROM (VALUES
      ('schema_version',                'c5-intrinsic-authority-pin-v1'),
      ('source_authority_revision',     p_coordinates->>'source_authority_revision'),
      ('authority_revision',            p_coordinates->>'authority_revision'),
      ('source_authority_policy_digest',p_coordinates->>'source_authority_policy_digest'),
      ('package_hash_algorithm',        p_coordinates->>'package_hash_algorithm'),
      ('methodology_version',           p_coordinates->>'methodology_version'),
      ('methodology_digest',            p_coordinates->>'methodology_digest'),
      ('engine',                        p_coordinates->>'engine'),
      ('engine_version',                p_coordinates->>'engine_version'),
      ('gate_policy_version',           p_coordinates->>'gate_policy_version')
    ) AS t(k, val);
  IF (SELECT bool_or(val IS NULL) FROM (VALUES
        (p_coordinates->>'source_authority_revision'),(p_coordinates->>'authority_revision'),
        (p_coordinates->>'source_authority_policy_digest'),(p_coordinates->>'package_hash_algorithm'),
        (p_coordinates->>'methodology_version'),(p_coordinates->>'methodology_digest'),
        (p_coordinates->>'engine'),(p_coordinates->>'engine_version'),
        (p_coordinates->>'gate_policy_version')) AS c(val)) THEN
    RAISE EXCEPTION 'authority-pin supersede refused: incomplete successor coordinates' USING ERRCODE='check_violation'; END IF;
  v_computed := 'sha256:' || encode(sha256(convert_to(v_canonical, 'UTF8')), 'hex');
  IF v_computed <> p_expected_successor_digest THEN
    RAISE EXCEPTION 'authority-pin supersede refused: computed digest % != expected %', v_computed, p_expected_successor_digest USING ERRCODE='check_violation'; END IF;
  -- 3. insert the immutable successor pin (is_current=false: currentness moves to the chain)
  INSERT INTO metric_audit.intrinsic_authority_pin (
    source_authority_revision, authority_revision, source_authority_policy_digest, package_hash_algorithm,
    methodology_version, methodology_digest, engine, engine_version, gate_policy_version, is_current, pinned_by)
  VALUES (
    p_coordinates->>'source_authority_revision', p_coordinates->>'authority_revision',
    p_coordinates->>'source_authority_policy_digest', p_coordinates->>'package_hash_algorithm',
    p_coordinates->>'methodology_version', p_coordinates->>'methodology_digest', p_coordinates->>'engine',
    p_coordinates->>'engine_version', p_coordinates->>'gate_policy_version', false, p_created_by)
  RETURNING pin_uid INTO v_new;
  -- 4. append the supersede event (same tx)
  INSERT INTO metric_audit.intrinsic_authority_pin_event (
    event_kind, predecessor_pin_uid, successor_pin_uid, successor_pin_digest,
    methodology_release_ratification_ref, methodology_release_ratification_sha256,
    operator_authorization_ref, operator_authorization_sha256,
    accepted_review_response_ref, accepted_review_response_sha256, reason, created_by)
  VALUES (
    'supersede_current', v_pred, v_new, p_expected_successor_digest,
    p_methodology_release_ratification_ref, p_methodology_release_ratification_sha256,
    p_operator_authorization_ref, p_operator_authorization_sha256,
    p_accepted_review_response_ref, p_accepted_review_response_sha256, p_reason, p_created_by);
  -- 5. post-check: the resolver must now return exactly the successor
  v_resolved := metric_audit.fn_intrinsic_authority_pin_current();
  IF v_resolved IS DISTINCT FROM v_new THEN
    RAISE EXCEPTION 'authority-pin supersede post-check failed: resolver=% != successor=%', v_resolved, v_new USING ERRCODE='check_violation'; END IF;
  RETURN v_new;
END $function$
```

### `metric_audit.fn_c6_affected_set`

Reads/writes: `mcf.mcv_closure_dependency`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_c6_affected_set(p_root uuid)
 RETURNS uuid[]
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
  WITH RECURSIVE closure(mcv) AS (
    SELECT p_root
    UNION
    SELECT d.dependent_mcv FROM mcf.mcv_closure_dependency d
      JOIN closure c ON d.dependency_uid = c.mcv AND d.dependency_kind='metric_input')
  SELECT array_agg(DISTINCT mcv) FROM closure
$function$
```

### `metric_audit.fn_c6_assert_cascade_complete`

Reads/writes: `mcf.metric_contract_version`, `metric_audit.invalidation`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_c6_assert_cascade_complete(p_root uuid, p_cause_kind text, p_cause_decision uuid, p_cause_nc uuid, p_cause_signer text, p_fingerprint text)
 RETURNS void
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE m uuid; st text;
BEGIN
  FOREACH m IN ARRAY coalesce(metric_audit.fn_c6_affected_set(p_root), ARRAY[]::uuid[]) LOOP
    SELECT governance_state_code INTO st FROM mcf.metric_contract_version WHERE metric_contract_version_uid = m;
    IF st = 'active' THEN
      RAISE EXCEPTION 'C6 stale-active window: MCV % still active under cause %', m, p_fingerprint USING ERRCODE='check_violation'; END IF;
    -- eligibility-bearing MCVs blocked under this cause must carry the exact-cause invalidation. MCVs in
    -- other states (audit_pending/draft/…/superseded) are not blocked-by-cause and require no evidence row.
    IF st = 'audit_blocked' AND NOT EXISTS (
      SELECT 1 FROM metric_audit.invalidation
      WHERE metric_contract_version_uid = m AND cleared_at IS NULL
        AND root_cause_fingerprint = p_fingerprint
        AND cause_kind = p_cause_kind
        AND (p_cause_decision IS NULL OR cause_decision_uid = p_cause_decision)
        AND (p_cause_nc       IS NULL OR cause_nc_uid       = p_cause_nc)
        AND (p_cause_signer   IS NULL OR cause_signer_key_id = p_cause_signer)) THEN
      RAISE EXCEPTION 'C6 cause-evidence missing: MCV % (audit_blocked) has no live invalidation binding cause % (%)', m, p_fingerprint, p_cause_kind USING ERRCODE='check_violation'; END IF;
  END LOOP;
END $function$
```

### `metric_audit.fn_c6_deferred_blocking_nc`

Reads/writes: `metric_audit.decision`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_c6_deferred_blocking_nc()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE v_mcv uuid;
BEGIN
  IF NEW.is_blocking THEN
    SELECT metric_contract_version_uid INTO v_mcv FROM metric_audit.decision WHERE decision_uid = NEW.decision_uid;
    IF v_mcv IS NOT NULL AND metric_audit.fn_effective_decision(v_mcv) = NEW.decision_uid THEN
      PERFORM metric_audit.fn_c6_assert_cascade_complete(v_mcv,
        'blocking_nc', NEW.decision_uid, NEW.nc_uid, NULL, 'blocking_nc:'||NEW.decision_uid::text||':'||NEW.nc_uid::text);
    END IF;
  END IF;
  RETURN NULL;
END $function$
```

### `metric_audit.fn_c6_deferred_revoke`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_c6_deferred_revoke()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  -- a REVOKE makes fn_effective_decision NULL, so key on the STREAM HEAD: this REVOKE is the current head.
  IF NEW.decision_code = 'REVOKE'
     AND metric_audit.fn_decision_stream_head(NEW.metric_contract_version_uid) = NEW.decision_uid THEN
    PERFORM metric_audit.fn_c6_assert_cascade_complete(NEW.metric_contract_version_uid,
      'external_revocation', NEW.decision_uid, NULL, NULL, 'revoke:'||NEW.decision_uid::text);
  END IF;
  RETURN NULL;
END $function$
```

### `metric_audit.fn_c6_deferred_signer_compromise`

Reads/writes: `metric_audit.decision`, `metric_audit.feed_event`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_c6_deferred_signer_compromise()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE d record; fp text;
BEGIN
  IF NEW.event_kind = 'revoke_compromise_retroactive' THEN
    fp := 'signer_compromise:'||NEW.event_uid::text;
    -- affected roots = every effective PASS decision signed by the compromised key.
    FOR d IN
      SELECT dec.metric_contract_version_uid AS mcv
      FROM metric_audit.decision dec
      JOIN metric_audit.feed_event fev ON fev.event_uid = dec.feed_event_uid
      WHERE fev.signer_key_id = NEW.key_id AND dec.decision_code='PASS'
        AND metric_audit.fn_effective_decision(dec.metric_contract_version_uid) = dec.decision_uid
    LOOP
      -- signer compromise binds the compromised KEY (the invariant coordinate across all affected roots);
      -- cause_decision_uid is per-root and a shared dependent records only one root's, so it is not bound here.
      PERFORM metric_audit.fn_c6_assert_cascade_complete(d.mcv, 'external_revocation', NULL, NULL, NEW.key_id, fp);
    END LOOP;
  END IF;
  RETURN NULL;
END $function$
```

### `metric_audit.fn_c6_run_cascade`

Reads/writes: `mcf.certification_record`, `mcf.metric_contract_version`, `metric_audit.decision`, `metric_audit.invalidation`, `metric_audit.transition_evidence`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_c6_run_cascade(p_root uuid, p_cause_kind text, p_cause_decision uuid, p_cause_nc uuid, p_cause_signer text, p_fingerprint text, p_actor text)
 RETURNS integer
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE m uuid; st text; v_inv uuid; v_cert uuid; v_eff uuid; v_head uuid; v_dec uuid; v_reason text; n int := 0;
BEGIN
  FOREACH m IN ARRAY coalesce(metric_audit.fn_c6_affected_set(p_root), ARRAY[]::uuid[]) LOOP
    SELECT governance_state_code INTO st FROM mcf.metric_contract_version WHERE metric_contract_version_uid=m;
    -- (1) cause-exact evidence for every affected ELIGIBILITY-BEARING MCV — 'active' (about to be blocked)
    --     or already 'audit_blocked' (a shared dependent blocked by a prior cause; records THIS cause too).
    --     audit_pending/draft/review/approved/superseded MCVs are not admitted metrics whose eligibility a
    --     cause revokes, so they carry no invalidation (this also keeps genesis REJECT authoring inert).
    IF st IN ('active','audit_blocked') THEN
      INSERT INTO metric_audit.invalidation (metric_contract_version_uid, cause_kind, cause_decision_uid, cause_nc_uid, cause_signer_key_id, root_cause_fingerprint, invalidated_by_name)
      VALUES (m, p_cause_kind, p_cause_decision, p_cause_nc, p_cause_signer, p_fingerprint, p_actor)
      ON CONFLICT (metric_contract_version_uid, root_cause_fingerprint) DO NOTHING
      RETURNING invalidation_uid INTO v_inv;
      IF v_inv IS NULL THEN
        SELECT invalidation_uid INTO v_inv FROM metric_audit.invalidation
          WHERE metric_contract_version_uid=m AND root_cause_fingerprint=p_fingerprint; END IF;
    END IF;
    -- (2) block + cert + citation only for a live active->audit_blocked transition.
    IF st='active' THEN
      INSERT INTO mcf.certification_record (primitive_type, subject_kind, primitive_id, action_code,
        from_state_code, to_state_code, is_archived_after, policy_version, certifier_sub, certifier_role_at_action)
      VALUES ('metric_contract_version','metric_contract_version', m, 'audit_block','active','audit_blocked', false, '1.0.0', p_actor, 'system')
      RETURNING certification_record_id INTO v_cert;
      -- derive the citable terminal decision for THIS MCV (M41 transition_evidence semantics).
      v_eff  := metric_audit.fn_effective_decision(m);
      v_head := metric_audit.fn_decision_stream_head(m);
      v_dec := NULL; v_reason := NULL;
      IF v_eff IS NULL AND v_head IS NOT NULL
         AND (SELECT decision_code FROM metric_audit.decision WHERE decision_uid=v_head) = 'REVOKE' THEN
        v_dec := v_head; v_reason := 'revoked_decision';
      ELSIF v_eff IS NOT NULL
         AND (SELECT decision_code FROM metric_audit.decision WHERE decision_uid=v_eff) = 'REJECT' THEN
        v_dec := v_eff; v_reason := 'rejected_decision';
      END IF;
      IF v_dec IS NOT NULL THEN
        INSERT INTO metric_audit.transition_evidence (certification_record_id, metric_contract_version_uid, action_code,
          from_state_code, to_state_code, decision_uid, block_reason_kind, invalidation_uid)
        VALUES (v_cert, m, 'audit_block','active','audit_blocked', v_dec, v_reason, v_inv);
      END IF;
      UPDATE mcf.metric_contract_version SET governance_state_code='audit_blocked' WHERE metric_contract_version_uid=m;
      n := n + 1;
    END IF;
  END LOOP;
  RETURN n;
END $function$
```

### `metric_audit.fn_c7_require_reintake_evidence`

Reads/writes: `metric_audit.transition_evidence`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_c7_require_reintake_evidence()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN
  IF NEW.primitive_type='metric_contract_version' AND NEW.action_code='audit_reintake'
     AND NEW.from_state_code='active' AND NEW.to_state_code='audit_pending' THEN
    IF NOT EXISTS (SELECT 1 FROM metric_audit.transition_evidence te
                   WHERE te.certification_record_id = NEW.certification_record_id
                     AND te.metric_contract_version_uid = NEW.primitive_id
                     AND te.action_code='audit_reintake') THEN
      RAISE EXCEPTION 'audit_reintake cert % has no matching transition_evidence at commit (C7 backstop)', NEW.certification_record_id USING ERRCODE='check_violation'; END IF;
  END IF;
  RETURN NULL;
END $function$
```

### `metric_audit.fn_c8_require_admit_evidence`

Reads/writes: `metric_audit.transition_evidence`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_c8_require_admit_evidence()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN
  IF NEW.primitive_type='metric_contract_version' AND NEW.action_code='audit_admit'
     AND NEW.from_state_code='audit_pending' AND NEW.to_state_code='active' THEN
    IF NOT EXISTS (SELECT 1 FROM metric_audit.transition_evidence te
                   WHERE te.certification_record_id = NEW.certification_record_id
                     AND te.metric_contract_version_uid = NEW.primitive_id
                     AND te.action_code='audit_admit') THEN
      RAISE EXCEPTION 'audit_admit cert % has no matching transition_evidence at commit (C8 backstop)', NEW.certification_record_id USING ERRCODE='check_violation'; END IF;
  END IF;
  RETURN NULL;
END $function$
```

### `metric_audit.fn_decision_finalize`

Reads/writes: `metric_audit.decision_nc_reference`, `metric_audit.feed_event`, `metric_audit.nc_reference`, `metric_audit.report_raised_nc`, `metric_audit.report_reference`, `rr.closure_root`, `rr.contextual_decision`, `rr.contextual_definition_score`, `rr.contextual_formula_score`, `rr.contextual_input_semantics_score`, `rr.contextual_overall_score`, `rr.exactness_result`, `rr.foundation_verdict`, `rr.metric_contract_version_uid`, `rr.package_snapshot_digest`, `rr.semantic_conformance_verdict`, `rr.structural_verdict`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_decision_finalize()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE ev metric_audit.feed_event%ROWTYPE; p jsonb; rr metric_audit.report_reference%ROWTYPE;
        v_exp_block int; v_exp_nonblock int; v_act int; v_req_code text; v_raised int; v_proj int;
BEGIN
  SELECT * INTO ev FROM metric_audit.feed_event WHERE event_uid = NEW.feed_event_uid;
  p := convert_from(ev.canonical_payload,'UTF8')::jsonb;
  IF NEW.decision_code = 'REVOKE' THEN
    SELECT count(*) INTO v_act FROM metric_audit.decision_nc_reference WHERE decision_uid = NEW.decision_uid;
    IF v_act <> 0 THEN RAISE EXCEPTION 'REVOKE decision % must have an empty NC child set', NEW.decision_uid; END IF;
    RETURN NULL;
  END IF;
  -- PASS/REJECT: report_reference must exist and agree (RDC binding + verdict already bound in the guard)
  SELECT * INTO rr FROM metric_audit.report_reference WHERE report_uid = NEW.report_uid;
  IF rr.report_uid IS NULL THEN RAISE EXCEPTION 'decision % finalize: bound report_reference absent', NEW.decision_uid; END IF;
  IF NEW.metric_contract_version_uid IS DISTINCT FROM rr.metric_contract_version_uid
     OR NEW.package_snapshot_digest IS DISTINCT FROM rr.package_snapshot_digest
     OR NEW.closure_root IS DISTINCT FROM rr.closure_root THEN
    RAISE EXCEPTION 'RDC: decision subject/package/closure != report'; END IF;
  IF NEW.structural_verdict IS DISTINCT FROM rr.structural_verdict
     OR NEW.foundation_verdict IS DISTINCT FROM rr.foundation_verdict
     OR NEW.contextual_definition_score IS DISTINCT FROM rr.contextual_definition_score
     OR NEW.contextual_formula_score IS DISTINCT FROM rr.contextual_formula_score
     OR NEW.contextual_input_semantics_score IS DISTINCT FROM rr.contextual_input_semantics_score
     OR NEW.contextual_overall_score IS DISTINCT FROM rr.contextual_overall_score
     OR NEW.contextual_decision IS DISTINCT FROM rr.contextual_decision
     OR NEW.semantic_conformance_verdict IS DISTINCT FROM rr.semantic_conformance_verdict
     OR NEW.exactness_result IS DISTINCT FROM rr.exactness_result THEN
    RAISE EXCEPTION 'RDC: decision verdict summary != report verdicts'; END IF;
  -- code coherence: PASS->PASS, REJECT->REJECT, OPERATOR_REVIEW->REJECT
  v_req_code := CASE rr.overall_assessment WHEN 'PASS' THEN 'PASS' ELSE 'REJECT' END;
  IF NEW.decision_code IS DISTINCT FROM v_req_code THEN
    RAISE EXCEPTION 'RDC: report overall_assessment % requires decision_code %, got %', rr.overall_assessment, v_req_code, NEW.decision_code; END IF;
  -- review P0-2: BEFORE deriving the expected NC set, prove EXACT closure — every report-raised NC has
  -- exactly one same-report nc_reference. An inner join alone silently drops an unprojected raised NC,
  -- collapsing the expected set to empty and false-passing a childless decision. Assert counts match first.
  SELECT count(*) INTO v_raised FROM metric_audit.report_raised_nc WHERE report_uid = NEW.report_uid;
  SELECT count(*) INTO v_proj
    FROM metric_audit.report_raised_nc rn JOIN metric_audit.nc_reference nr
      ON nr.nc_uid = rn.nc_uid AND nr.report_uid = rn.report_uid
    WHERE rn.report_uid = NEW.report_uid;
  IF v_proj <> v_raised THEN
    RAISE EXCEPTION 'RDC: report % has % raised NCs but only % same-report nc_reference projections — decision cannot finalize',
      NEW.report_uid, v_raised, v_proj; END IF;
  -- exact NC-set equality: expected = every NC raised by the bound report, partitioned by severity.
  SELECT count(*) FILTER (WHERE nr.is_blocking), count(*) FILTER (WHERE NOT nr.is_blocking)
    INTO v_exp_block, v_exp_nonblock
    FROM metric_audit.report_raised_nc rn JOIN metric_audit.nc_reference nr
      ON nr.nc_uid = rn.nc_uid AND nr.report_uid = rn.report_uid
    WHERE rn.report_uid = NEW.report_uid;
  SELECT count(*) INTO v_act FROM metric_audit.decision_nc_reference WHERE decision_uid = NEW.decision_uid;
  IF v_act <> (v_exp_block + v_exp_nonblock) THEN
    RAISE EXCEPTION 'RDC: decision % NC set (%) != report effective NC set (%)', NEW.decision_uid, v_act, v_exp_block + v_exp_nonblock; END IF;
  -- every report-raised NC must be present in the decision child set with matching partition (set equality;
  -- extras already refused by the child membership guard, so count-equality + this presence check = exact)
  IF EXISTS (
    SELECT 1 FROM metric_audit.report_raised_nc rn JOIN metric_audit.nc_reference nr ON nr.nc_uid = rn.nc_uid
     WHERE rn.report_uid = NEW.report_uid
       AND NOT EXISTS (SELECT 1 FROM metric_audit.decision_nc_reference dn
                        WHERE dn.decision_uid = NEW.decision_uid AND dn.nc_uid = rn.nc_uid AND dn.is_blocking = nr.is_blocking)) THEN
    RAISE EXCEPTION 'RDC: decision % omits or mispartitions a report-raised NC', NEW.decision_uid; END IF;
  RETURN NULL;
END $function$
```

### `metric_audit.fn_decision_guard`

Reads/writes: `ev.feed_mode`, `ev.payload_digest`, `metric_audit.decision`, `metric_audit.feed_event`, `metric_audit.report_reference`, `metric_audit.request_publication`, `new.metric_contract_version_uid`, `rr.report_payload_digest`, `rr.request_digest`, `rr.request_uid`, `tgt.decision_digest`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_decision_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE ev metric_audit.feed_event%ROWTYPE; p jsonb; pub metric_audit.request_publication%ROWTYPE; req jsonb;
        v_head uuid; tgt metric_audit.decision%ROWTYPE; rr metric_audit.report_reference%ROWTYPE;
BEGIN
  SELECT * INTO ev FROM metric_audit.feed_event WHERE event_uid = NEW.feed_event_uid;
  IF ev.event_uid IS NULL THEN RAISE EXCEPTION 'decision cites a non-existent feed_event %', NEW.feed_event_uid; END IF;
  IF ev.payload_schema_version IS DISTINCT FROM 'metric-audit-decision-v2' THEN
    RAISE EXCEPTION 'decision feed_event is not a metric-audit-decision-v2 event'; END IF;
  IF NEW.decision_payload_digest IS DISTINCT FROM ev.payload_digest THEN
    RAISE EXCEPTION 'decision decision_payload_digest != feed_event.payload_digest'; END IF;
  p := convert_from(ev.canonical_payload,'UTF8')::jsonb;
  -- core payload binds
  IF NEW.decision_uid IS DISTINCT FROM (p->>'decision_uid')::uuid
     OR NEW.decision_digest IS DISTINCT FROM p->>'decision_digest'
     OR NEW.decision_code IS DISTINCT FROM p->>'decision_code'
     OR NEW.metric_contract_version_uid IS DISTINCT FROM (p#>>'{subject,metric_contract_version_uid}')::uuid
     OR NEW.metric_contract_uid IS DISTINCT FROM (p#>>'{subject,metric_contract_uid}')::uuid
     OR NEW.version_code IS DISTINCT FROM p#>>'{subject,version_code}'
     OR NEW.request_uid IS DISTINCT FROM (p#>>'{request_ref,request_uid}')::uuid
     OR NEW.request_digest IS DISTINCT FROM p#>>'{request_ref,request_digest}'
     OR NEW.package_hash_algorithm IS DISTINCT FROM p#>>'{package,hash_algorithm_version}'
     OR NEW.package_snapshot_digest IS DISTINCT FROM p#>>'{package,package_snapshot_digest}'
     OR NEW.closure_root IS DISTINCT FROM p->>'closure_root'
     OR NEW.supersedes_decision_uid IS DISTINCT FROM (p->>'supersedes_decision_uid')::uuid
     OR NEW.decided_by IS DISTINCT FROM p->>'decided_by'
     OR NEW.decided_at IS DISTINCT FROM (p->>'decided_at')::timestamptz          -- P0-3: bound (feeds stream ordering)
     OR NEW.authority_revision IS DISTINCT FROM p#>>'{authority,authority_revision}'
     OR NEW.methodology_version IS DISTINCT FROM p#>>'{authority,methodology_version}'
     OR NEW.methodology_digest IS DISTINCT FROM p#>>'{authority,methodology_digest}'
     OR NEW.gate_policy_version IS DISTINCT FROM p#>>'{authority,gate_policy_version}'
     OR NEW.engine IS DISTINCT FROM p#>>'{authority,engine}'
     OR NEW.engine_version IS DISTINCT FROM p#>>'{authority,engine_version}'
     OR NEW.source_authority_revision IS DISTINCT FROM p#>>'{authority,source_authority_revision}'
     OR NEW.source_authority_policy_digest IS DISTINCT FROM p#>>'{authority,source_authority_policy_digest}'
     OR NEW.citations_json IS DISTINCT FROM p->'citations'                        -- P0-3: bound
     OR NEW.revocation_json IS DISTINCT FROM NULLIF(p->'revocation','null'::jsonb) THEN  -- P0-3: exact (null-normalized)
    RAISE EXCEPTION 'decision projection is detached from the signed decision payload'; END IF;
  -- feed_mode from the verified event AND agrees with payload.feed.feed_mode
  IF NEW.feed_mode IS DISTINCT FROM ev.feed_mode OR NEW.feed_mode IS DISTINCT FROM p#>>'{feed,feed_mode}' THEN
    RAISE EXCEPTION 'decision feed_mode detached from feed_event/payload'; END IF;
  -- v4 P0-1 + review P0-1: the cited request MUST be a signed publication, AND the decision must agree with
  -- the published request payload (V-D2 in the DB backstop, every decision code). request_digest here is the
  -- request SELF-identity (== published request's own request_digest), NOT the transport payload_digest.
  SELECT * INTO pub FROM metric_audit.request_publication WHERE request_uid = NEW.request_uid;
  IF pub.request_uid IS NULL THEN RAISE EXCEPTION 'decision request % is not a signed publication', NEW.request_uid; END IF;
  req := convert_from(pub.canonical_payload,'UTF8')::jsonb;
  IF NEW.request_digest IS DISTINCT FROM req->>'request_digest'
     OR NEW.metric_contract_version_uid IS DISTINCT FROM (req#>>'{subject,metric_contract_version_uid}')::uuid
     OR NEW.metric_contract_uid IS DISTINCT FROM (req#>>'{subject,metric_contract_uid}')::uuid
     OR NEW.version_code IS DISTINCT FROM req#>>'{subject,version_code}'
     OR NEW.package_snapshot_digest IS DISTINCT FROM req#>>'{package,package_snapshot_digest}'
     OR NEW.closure_root IS DISTINCT FROM req->>'closure_root' THEN
    RAISE EXCEPTION 'decision V-D2: fields disagree with the published request payload'; END IF;
  -- REVOKE identity (V-D7)
  IF NEW.decision_code = 'REVOKE' THEN
    IF NEW.supersedes_decision_uid IS DISTINCT FROM (p#>>'{revocation,revoked_decision_uid}')::uuid THEN
      RAISE EXCEPTION 'REVOKE supersedes_decision_uid != revocation.revoked_decision_uid'; END IF;
    IF NEW.supersedes_decision_uid = NEW.decision_uid THEN RAISE EXCEPTION 'REVOKE must not revoke itself'; END IF;
    SELECT * INTO tgt FROM metric_audit.decision WHERE decision_uid = NEW.supersedes_decision_uid;
    IF tgt.decision_uid IS NULL THEN RAISE EXCEPTION 'REVOKE target % does not exist', NEW.supersedes_decision_uid; END IF;
    IF tgt.metric_contract_version_uid IS DISTINCT FROM NEW.metric_contract_version_uid THEN
      RAISE EXCEPTION 'REVOKE target is a different subject'; END IF;
    IF NEW.revocation_json#>>'{revoked_decision_digest}' IS DISTINCT FROM tgt.decision_digest THEN
      RAISE EXCEPTION 'REVOKE revoked_decision_digest != target decision_digest'; END IF;
  ELSE
    -- PASS/REJECT: verdict block binds; report closure to report_reference
    IF NEW.structural_verdict IS DISTINCT FROM p#>>'{verdict_summary,structural_verdict}'
       OR NEW.foundation_verdict IS DISTINCT FROM p#>>'{verdict_summary,foundation_verdict}'
       OR NEW.contextual_definition_score IS DISTINCT FROM (p#>>'{verdict_summary,contextual,definition,score}')::int
       OR NEW.contextual_formula_score IS DISTINCT FROM (p#>>'{verdict_summary,contextual,formula,score}')::int
       OR NEW.contextual_input_semantics_score IS DISTINCT FROM (p#>>'{verdict_summary,contextual,canonical_input_semantics,score}')::int
       OR NEW.contextual_overall_score IS DISTINCT FROM (p#>>'{verdict_summary,contextual,overall_score}')::int
       OR NEW.contextual_decision IS DISTINCT FROM p#>>'{verdict_summary,contextual,decision}'
       OR NEW.semantic_conformance_verdict IS DISTINCT FROM p#>>'{verdict_summary,semantic_conformance_verdict}'
       OR NEW.exactness_result IS DISTINCT FROM p#>>'{verdict_summary,exactness_result}'
       OR NEW.report_uid IS DISTINCT FROM (p#>>'{report_ref,report_uid}')::uuid
       OR NEW.report_digest IS DISTINCT FROM p#>>'{report_ref,report_digest}' THEN
      RAISE EXCEPTION 'decision verdict/report projection detached from payload'; END IF;
    SELECT * INTO rr FROM metric_audit.report_reference WHERE report_uid = NEW.report_uid;
    IF rr.report_uid IS NULL THEN RAISE EXCEPTION 'decision cites report % with no projection', NEW.report_uid; END IF;
    IF NEW.report_digest IS DISTINCT FROM rr.report_payload_digest THEN
      RAISE EXCEPTION 'decision report_digest != report_reference.report_payload_digest'; END IF;
    -- review P0-1: a PASS/REJECT decision's request must equal the bound report's request (one audit chain)
    IF NEW.request_uid IS DISTINCT FROM rr.request_uid OR NEW.request_digest IS DISTINCT FROM rr.request_digest THEN
      RAISE EXCEPTION 'decision request (uid/digest) != bound report request'; END IF;
  END IF;
  -- chain position via the STRUCTURAL head (includes REVOKE)
  v_head := metric_audit.fn_decision_stream_head(NEW.metric_contract_version_uid);
  IF v_head IS NULL THEN
    IF NEW.supersedes_decision_uid IS NOT NULL THEN RAISE EXCEPTION 'first decision for mcv % must not supersede', NEW.metric_contract_version_uid; END IF;
  ELSE
    IF NEW.supersedes_decision_uid IS DISTINCT FROM v_head THEN
      RAISE EXCEPTION 'decision for mcv % must supersede the current structural head %', NEW.metric_contract_version_uid, v_head; END IF;
    IF (SELECT decided_at FROM metric_audit.decision WHERE decision_uid = v_head) >= NEW.decided_at THEN
      RAISE EXCEPTION 'decision decided_at must be monotonically after the superseded head'; END IF;
  END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_decision_nc_reference_membership`

Reads/writes: `metric_audit.decision`, `metric_audit.feed_event`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_decision_nc_reference_membership()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE ev metric_audit.feed_event%ROWTYPE; p jsonb; n jsonb; found boolean := false; v_expected_blocking boolean;
BEGIN
  SELECT fe.* INTO ev FROM metric_audit.decision d JOIN metric_audit.feed_event fe ON fe.event_uid = d.feed_event_uid
    WHERE d.decision_uid = NEW.decision_uid;
  IF ev.event_uid IS NULL THEN RAISE EXCEPTION 'decision_nc_reference cites a decision with no verified feed_event %', NEW.decision_uid; END IF;
  p := convert_from(ev.canonical_payload,'UTF8')::jsonb;
  -- search blocking set
  FOR n IN SELECT jsonb_array_elements(coalesce(p->'unresolved_blocking_ncs','[]'::jsonb)) LOOP
    IF (n->>'nc_uid')::uuid = NEW.nc_uid THEN v_expected_blocking := true; found := true;
      IF NEW.nc_digest IS DISTINCT FROM n->>'nc_digest' OR NEW.severity IS DISTINCT FROM n->>'severity' THEN
        RAISE EXCEPTION 'decision_nc_reference % typed values diverge from signed blocking NcRef', NEW.nc_uid; END IF;
      EXIT; END IF;
  END LOOP;
  IF NOT found THEN
    FOR n IN SELECT jsonb_array_elements(coalesce(p->'unresolved_nonblocking_ncs','[]'::jsonb)) LOOP
      IF (n->>'nc_uid')::uuid = NEW.nc_uid THEN v_expected_blocking := false; found := true;
        IF NEW.nc_digest IS DISTINCT FROM n->>'nc_digest' OR NEW.severity IS DISTINCT FROM n->>'severity' THEN
          RAISE EXCEPTION 'decision_nc_reference % typed values diverge from signed nonblocking NcRef', NEW.nc_uid; END IF;
        EXIT; END IF;
    END LOOP;
  END IF;
  IF NOT found THEN RAISE EXCEPTION 'decision_nc_reference % is not in the signed decision unresolved-NC set', NEW.nc_uid; END IF;
  IF NEW.is_blocking IS DISTINCT FROM v_expected_blocking THEN
    RAISE EXCEPTION 'decision_nc_reference % partition (is_blocking=%) disagrees with the signed payload', NEW.nc_uid, NEW.is_blocking; END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_decision_stream_head`

Reads/writes: `metric_audit.decision`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_decision_stream_head(p_mcv uuid)
 RETURNS uuid
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE v_n int; v_uid uuid;
BEGIN
  SELECT count(*), (array_agg(d.decision_uid))[1] INTO v_n, v_uid FROM metric_audit.decision d
   WHERE d.metric_contract_version_uid = p_mcv
     AND NOT EXISTS (SELECT 1 FROM metric_audit.decision s WHERE s.supersedes_decision_uid = d.decision_uid);
  IF v_n > 1 THEN RAISE EXCEPTION 'decision stream fork: % un-superseded heads for mcv %', v_n, p_mcv; END IF;
  RETURN v_uid;  -- NULL when none
END $function$
```

### `metric_audit.fn_effective_decision`

Reads/writes: `metric_audit.decision`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_effective_decision(p_mcv uuid)
 RETURNS uuid
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE v_head uuid; v_code text;
BEGIN
  v_head := metric_audit.fn_decision_stream_head(p_mcv);
  IF v_head IS NULL THEN RETURN NULL; END IF;
  SELECT decision_code INTO v_code FROM metric_audit.decision WHERE decision_uid = v_head;
  IF v_code = 'REVOKE' THEN RETURN NULL; END IF;
  RETURN v_head;
END $function$
```

### `metric_audit.fn_effective_feed_registration`

Reads/writes: `metric_audit.feed_registration`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_effective_feed_registration(p_feed text)
 RETURNS uuid
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE v_n int; v_uid uuid;
BEGIN
  -- NB: PostgreSQL has no min(uuid)/max(uuid) aggregate; pick the single head via array_agg (count is the
  -- fail-closed guard, so exactly 0 or 1 element is returned — element [1] is the head or NULL).
  SELECT count(*), (array_agg(r.registration_uid))[1] INTO v_n, v_uid FROM metric_audit.feed_registration r
   WHERE r.feed_name = p_feed
     AND NOT EXISTS (SELECT 1 FROM metric_audit.feed_registration s WHERE s.supersedes_registration_uid = r.registration_uid);
  IF v_n > 1 THEN RAISE EXCEPTION 'feed_registration fork: % un-superseded heads for feed %', v_n, p_feed; END IF;
  RETURN v_uid;  -- NULL when none
END $function$
```

### `metric_audit.fn_feed_checkpoint_guard`

Reads/writes: `metric_audit.feed_event`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_feed_checkpoint_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE v_old bigint;
BEGIN
  -- the claimed position must be an EXACT existing feed_event (name, sequence, envelope_digest)
  IF NOT EXISTS (SELECT 1 FROM metric_audit.feed_event
                 WHERE feed_name = NEW.feed_name AND feed_sequence = NEW.last_verified_sequence
                   AND envelope_digest = NEW.last_event_digest) THEN
    RAISE EXCEPTION 'feed_checkpoint (%, %, %) is not an existing feed_event', NEW.feed_name, NEW.last_verified_sequence, NEW.last_event_digest; END IF;
  IF TG_OP = 'UPDATE' THEN
    v_old := OLD.last_verified_sequence;
    IF NEW.last_verified_sequence < v_old THEN
      RAISE EXCEPTION 'feed_checkpoint regression on %: % < %', NEW.feed_name, NEW.last_verified_sequence, v_old; END IF;
  END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_feed_event_guard`

Reads/writes: `metric_audit.feed_event`, `metric_audit.import_attempt`, `metric_audit.import_attempt_verified`, `new.feed_name`, `new.feed_sequence`, `v.canonical_payload`, `v.envelope_digest`, `v.event_kind`, `v.feed_mode`, `v.feed_sequence`, `v.issued_at`, `v.payload_digest`, `v.payload_schema_version`, `v.prior_event_digest`, `v.signature_algorithm`, `v.signature_b`, `v.signer_key_id`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_feed_event_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE v metric_audit.import_attempt_verified%ROWTYPE; v_prev_digest text; v_prev_max bigint; v_feed text;
BEGIN
  -- the cited attempt MUST be verified (a rejected/unparseable attempt has no _verified child)
  SELECT * INTO v FROM metric_audit.import_attempt_verified WHERE attempt_uid = NEW.import_attempt_uid;
  IF v.attempt_uid IS NULL THEN
    RAISE EXCEPTION 'feed_event cites a non-verified attempt %', NEW.import_attempt_uid; END IF;
  SELECT feed_name INTO v_feed FROM metric_audit.import_attempt WHERE attempt_uid = NEW.import_attempt_uid;
  IF v_feed IS DISTINCT FROM NEW.feed_name THEN
    RAISE EXCEPTION 'feed_event feed % != verified attempt feed %', NEW.feed_name, v_feed; END IF;
  -- every consumed field must equal the verified coordinates (no caller re-assertion)
  IF NEW.feed_sequence IS DISTINCT FROM v.feed_sequence
     OR NEW.feed_mode IS DISTINCT FROM v.feed_mode
     OR NEW.payload_schema_version IS DISTINCT FROM v.payload_schema_version
     OR NEW.event_kind IS DISTINCT FROM v.event_kind
     OR NEW.canonical_payload IS DISTINCT FROM v.canonical_payload
     OR NEW.payload_digest IS DISTINCT FROM v.payload_digest
     OR NEW.envelope_digest IS DISTINCT FROM v.envelope_digest
     OR NEW.signature_b64 IS DISTINCT FROM v.signature_b64
     OR NEW.signature_algorithm IS DISTINCT FROM v.signature_algorithm
     OR NEW.signer_key_id IS DISTINCT FROM v.signer_key_id
     OR NEW.prior_event_digest IS DISTINCT FROM v.prior_event_digest
     OR NEW.issued_at IS DISTINCT FROM v.issued_at THEN
    RAISE EXCEPTION 'feed_event fields diverge from the verified attempt coordinates'; END IF;
  -- payload_digest still self-consistent with bytes; signer still current at issue
  IF NEW.payload_digest <> 'sha256:' || encode(sha256(NEW.canonical_payload),'hex') THEN
    RAISE EXCEPTION 'feed_event payload_digest != sha256(canonical_payload)'; END IF;
  IF NOT metric_audit.fn_signer_key_valid_at(NEW.signer_key_id, NEW.issued_at) THEN
    RAISE EXCEPTION 'feed_event signer % not valid at %', NEW.signer_key_id, NEW.issued_at; END IF;
  -- sequence contiguity + chain
  SELECT max(feed_sequence) INTO v_prev_max FROM metric_audit.feed_event WHERE feed_name = NEW.feed_name;
  IF NEW.feed_sequence = 1 THEN
    IF v_prev_max IS NOT NULL THEN RAISE EXCEPTION 'feed_event % already has events; seq 1 rejected', NEW.feed_name; END IF;
  ELSE
    IF v_prev_max IS DISTINCT FROM NEW.feed_sequence - 1 THEN
      RAISE EXCEPTION 'feed_event gap/fork: % expected %, got %', NEW.feed_name, coalesce(v_prev_max,0)+1, NEW.feed_sequence; END IF;
    SELECT envelope_digest INTO v_prev_digest FROM metric_audit.feed_event
      WHERE feed_name = NEW.feed_name AND feed_sequence = NEW.feed_sequence - 1;
    IF NEW.prior_event_digest IS DISTINCT FROM v_prev_digest THEN
      RAISE EXCEPTION 'feed_event broken chain at % seq %', NEW.feed_name, NEW.feed_sequence; END IF;
  END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_feed_registration_guard`

Reads/writes: `metric_audit.import_attempt_verified`, `v.signer_key_id`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_feed_registration_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE v_head uuid; v metric_audit.import_attempt_verified%ROWTYPE; p jsonb;
BEGIN
  -- C2R4-P0-1: bind EVERY projected column to the exact signed registration payload retained in the
  -- cited verified attempt (C3 consumes this projection as authority; the DB must forbid divergence).
  SELECT * INTO v FROM metric_audit.import_attempt_verified WHERE attempt_uid = NEW.import_attempt_uid;
  IF v.attempt_uid IS NULL THEN RAISE EXCEPTION 'feed_registration cites a non-verified attempt %', NEW.import_attempt_uid; END IF;
  IF v.payload_schema_version IS DISTINCT FROM 'audit-feed-registration-v1' THEN
    RAISE EXCEPTION 'feed_registration attempt is not an audit-feed-registration-v1 event'; END IF;
  p := convert_from(v.canonical_payload,'UTF8')::jsonb;
  IF NEW.registration_uid IS DISTINCT FROM (p->>'registration_uid')::uuid
     OR NEW.feed_name IS DISTINCT FROM p->>'feed_name'
     OR NEW.feed_mode IS DISTINCT FROM p->>'feed_mode'
     OR NEW.direction IS DISTINCT FROM p->>'direction'
     OR NEW.signer_key_id IS DISTINCT FROM p->>'signer_key_id'
     OR NEW.allowed_events IS DISTINCT FROM p->'allowed_events'
     OR NEW.valid_from IS DISTINCT FROM (p->>'valid_from')::timestamptz
     OR NEW.supersedes_registration_uid IS DISTINCT FROM (p->>'supersedes_registration_uid')::uuid
     OR NEW.registration_digest IS DISTINCT FROM p->>'registration_digest' THEN
    RAISE EXCEPTION 'feed_registration projection is detached from the signed registration payload'; END IF;
  -- the registration payload's signer MUST be the key that signed the registration envelope
  -- (no silent delegation of the governed feed to another key without a governed act).
  IF NEW.signer_key_id IS DISTINCT FROM v.signer_key_id THEN
    RAISE EXCEPTION 'feed_registration payload signer % != envelope signer %', NEW.signer_key_id, v.signer_key_id; END IF;
  -- chain position
  v_head := metric_audit.fn_effective_feed_registration(NEW.feed_name);
  IF v_head IS NULL THEN
    IF NEW.supersedes_registration_uid IS NOT NULL THEN RAISE EXCEPTION 'first registration for % must not supersede', NEW.feed_name; END IF;
  ELSE
    IF NEW.supersedes_registration_uid IS DISTINCT FROM v_head THEN
      RAISE EXCEPTION 'registration for % must supersede the current head %', NEW.feed_name, v_head; END IF;
  END IF;
  -- signer current at both the payload issue time (valid_from) and the envelope issue time
  IF NOT metric_audit.fn_signer_key_valid_at(NEW.signer_key_id, NEW.valid_from) THEN
    RAISE EXCEPTION 'feed_registration signer % not valid at %', NEW.signer_key_id, NEW.valid_from; END IF;
  IF NOT metric_audit.fn_signer_key_valid_at(v.signer_key_id, v.issued_at) THEN
    RAISE EXCEPTION 'feed_registration envelope signer % not valid at %', v.signer_key_id, v.issued_at; END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_import_attempt_guard`

Reads/writes: `new.envelope_json`, `new.feed_name`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_import_attempt_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN
  IF NEW.received_digest <> 'sha256:' || encode(sha256(NEW.received_bytes),'hex') THEN
    RAISE EXCEPTION 'import_attempt received_digest != sha256(received_bytes)'; END IF;
  -- C2R2-P0-1: when parsed, envelope_json MUST be the exact parse of the received bytes
  -- (closes the transport-A / parsed-B detachment; the verified child then derives from envelope_json).
  IF NEW.parse_status='parsed' AND convert_from(NEW.received_bytes,'UTF8')::jsonb IS DISTINCT FROM NEW.envelope_json THEN
    RAISE EXCEPTION 'import_attempt envelope_json is not the exact parse of received_bytes'; END IF;
  -- C2R3-P0-1: the feed_name column MUST equal the SIGNED envelope's top-level feed_name (no
  -- caller-supplied feed identity); and when the payload carries payload.feed, it must agree too.
  IF NEW.parse_status='parsed' THEN
    IF NEW.envelope_json->>'feed_name' IS DISTINCT FROM NEW.feed_name THEN
      RAISE EXCEPTION 'import_attempt feed_name % != signed envelope feed_name %', NEW.feed_name, NEW.envelope_json->>'feed_name'; END IF;
    IF NEW.envelope_json #> '{payload,feed}' IS NOT NULL
       AND NEW.envelope_json #>> '{payload,feed,feed_name}' IS DISTINCT FROM NEW.envelope_json->>'feed_name' THEN
      RAISE EXCEPTION 'import_attempt payload.feed.feed_name != signed envelope feed_name'; END IF;
  END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_import_attempt_verified_guard`

Reads/writes: `a.feed_name`, `metric_audit.feed_registration`, `metric_audit.fn_effective_feed_registration`, `metric_audit.import_attempt`, `new.feed_mode`, `payload.feed`, `reg.feed_mode`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_import_attempt_verified_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE a metric_audit.import_attempt%ROWTYPE; e jsonb; reg metric_audit.feed_registration%ROWTYPE;
BEGIN
  SELECT * INTO a FROM metric_audit.import_attempt WHERE attempt_uid = NEW.attempt_uid;
  IF a.verification_result IS DISTINCT FROM 'verified' THEN
    RAISE EXCEPTION 'import_attempt_verified requires a verified parent attempt (got %)', coalesce(a.verification_result,'<none>'); END IF;
  IF a.envelope_json IS NULL THEN RAISE EXCEPTION 'import_attempt_verified: verified parent has no parsed envelope'; END IF;
  e := a.envelope_json;
  -- structural coordinates derived from the parent envelope (feed_mode is NOT taken from the payload
  -- any more — C2R3-P0-2 resolves it from the governed feed registration below).
  IF NEW.feed_sequence IS DISTINCT FROM (e->>'feed_sequence')::bigint
     OR NEW.payload_schema_version IS DISTINCT FROM e->>'payload_schema_version'
     OR NEW.event_kind IS DISTINCT FROM e->>'event_kind'
     OR NEW.payload_digest IS DISTINCT FROM e->>'payload_digest'
     OR NEW.envelope_digest IS DISTINCT FROM e->>'envelope_digest'
     OR NEW.signature_b64 IS DISTINCT FROM e->>'signature_b64'
     OR NEW.signature_algorithm IS DISTINCT FROM e->>'signature_algorithm'
     OR NEW.signer_key_id IS DISTINCT FROM e->>'signer_key_id'
     OR NEW.prior_event_digest IS DISTINCT FROM e->>'prior_envelope_digest'
     OR NEW.issued_at IS DISTINCT FROM (e->>'issued_at')::timestamptz
     OR NEW.subject_ref_json IS DISTINCT FROM e->'subject' THEN
    RAISE EXCEPTION 'import_attempt_verified coordinates are not derived from the parent envelope'; END IF;
  IF NEW.payload_digest <> 'sha256:' || encode(sha256(NEW.canonical_payload),'hex') THEN
    RAISE EXCEPTION 'import_attempt_verified payload_digest != sha256(canonical_payload)'; END IF;
  IF NOT metric_audit.fn_signer_key_valid_at(NEW.signer_key_id, NEW.issued_at) THEN
    RAISE EXCEPTION 'import_attempt_verified signer % not valid at %', NEW.signer_key_id, NEW.issued_at; END IF;
  -- C2R3-P0-2: feed_mode + allowed {schema,event_kind} + direction come from the governed feed
  -- registration, NOT from payload.feed. (The service additionally runs the C1
  -- enforcementAdmissibility check — signature/validity/signer agreement — before promotion.)
  IF NEW.payload_schema_version = 'audit-feed-registration-v1' THEN
    -- a registration event is self-establishing: it consumes no registration and declares its own mode.
    IF NEW.feed_registration_uid IS NOT NULL THEN
      RAISE EXCEPTION 'a registration event must not consume a feed_registration'; END IF;
    IF NEW.feed_mode IS DISTINCT FROM (e#>>'{payload,feed_mode}') THEN
      RAISE EXCEPTION 'registration event feed_mode != declared payload feed_mode'; END IF;
  ELSE
    IF NEW.feed_registration_uid IS NULL THEN
      RAISE EXCEPTION 'inbound event requires the admitting feed_registration_uid'; END IF;
    SELECT * INTO reg FROM metric_audit.feed_registration WHERE registration_uid = NEW.feed_registration_uid;
    IF reg.registration_uid IS NULL THEN RAISE EXCEPTION 'feed_registration_uid % does not resolve', NEW.feed_registration_uid; END IF;
    IF reg.feed_name IS DISTINCT FROM a.feed_name THEN RAISE EXCEPTION 'registration feed % != event feed %', reg.feed_name, a.feed_name; END IF;
    IF NEW.feed_registration_uid IS DISTINCT FROM metric_audit.fn_effective_feed_registration(a.feed_name) THEN
      RAISE EXCEPTION 'feed_registration_uid is not the effective registration for %', a.feed_name; END IF;
    IF reg.direction IS DISTINCT FROM 'auditor_to_platform' THEN
      RAISE EXCEPTION 'inbound event requires an auditor_to_platform registration'; END IF;
    IF NEW.feed_mode IS DISTINCT FROM reg.feed_mode THEN
      RAISE EXCEPTION 'feed_mode % != governed registration mode %', NEW.feed_mode, reg.feed_mode; END IF;
    IF NOT (reg.allowed_events @> jsonb_build_array(jsonb_build_object(
              'payload_schema_version', NEW.payload_schema_version, 'event_kind', NEW.event_kind))) THEN
      RAISE EXCEPTION 'schema/event pair (%/%) not allowed by feed registration', NEW.payload_schema_version, NEW.event_kind; END IF;
    -- if the payload carries payload.feed.feed_mode, it must agree with the governed mode
    IF e #> '{payload,feed}' IS NOT NULL AND e #>> '{payload,feed,feed_mode}' IS DISTINCT FROM NEW.feed_mode THEN
      RAISE EXCEPTION 'payload.feed.feed_mode disagrees with the governed registration mode'; END IF;
  END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_intrinsic_authority_pin_current`

Reads/writes: `metric_audit.intrinsic_authority_pin`, `metric_audit.intrinsic_authority_pin_event`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_intrinsic_authority_pin_current()
 RETURNS uuid
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE v_super int; v_seed_n int; v_seed uuid; v_walk int; v_tail uuid; v_revoked int;
BEGIN
  SELECT count(*) INTO v_super FROM metric_audit.intrinsic_authority_pin_event WHERE event_kind='supersede_current';
  -- seed = the single is_current pin (retained partial-unique index guarantees <= 1)
  SELECT count(*), (array_agg(pin_uid))[1] INTO v_seed_n, v_seed
    FROM metric_audit.intrinsic_authority_pin WHERE is_current;
  IF v_seed_n <> 1 THEN RETURN NULL; END IF;
  -- legacy: no supersession yet -> the seed is current
  IF v_super = 0 THEN RETURN v_seed; END IF;
  -- walk the supersede chain from the seed
  WITH RECURSIVE chain AS (
    SELECT e.successor_pin_uid AS pin, 1 AS depth
      FROM metric_audit.intrinsic_authority_pin_event e
      WHERE e.event_kind='supersede_current' AND e.predecessor_pin_uid = v_seed
    UNION ALL
    SELECT e.successor_pin_uid, c.depth + 1
      FROM chain c
      JOIN metric_audit.intrinsic_authority_pin_event e
        ON e.event_kind='supersede_current' AND e.predecessor_pin_uid = c.pin
  )
  SELECT count(*), (array_agg(pin ORDER BY depth DESC))[1] INTO v_walk, v_tail FROM chain;
  -- broken/orphan chain: the walk from the seed must cover EVERY supersede event
  IF v_walk <> v_super OR v_tail IS NULL THEN RETURN NULL; END IF;
  -- a revoked chain head is not current (fail-closed)
  SELECT count(*) INTO v_revoked FROM metric_audit.intrinsic_authority_pin_event
    WHERE event_kind IN ('revoke_prospective','revoke_compromise_retroactive') AND successor_pin_uid = v_tail;
  IF v_revoked > 0 THEN RETURN NULL; END IF;
  RETURN v_tail;
END $function$
```

### `metric_audit.fn_intrinsic_authority_pin_event_guard`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_intrinsic_authority_pin_event_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN NEW.created_at := now(); RETURN NEW; END $function$
```

### `metric_audit.fn_intrinsic_authority_pin_event_immutable`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_intrinsic_authority_pin_event_immutable()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN
  RAISE EXCEPTION 'metric_audit.intrinsic_authority_pin_event is append-only (% refused, Invariant III)', TG_OP USING ERRCODE='check_violation';
END $function$
```

### `metric_audit.fn_intrinsic_authority_pin_guard`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_intrinsic_authority_pin_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN
  NEW.pinned_at := now();  -- DB-owned event time
  RETURN NEW;
END $function$
```

### `metric_audit.fn_intrinsic_authority_pin_immutability`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_intrinsic_authority_pin_immutability()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN
  RAISE EXCEPTION 'metric_audit.intrinsic_authority_pin is immutable (% refused, Invariant III)', TG_OP USING ERRCODE='check_violation';
END $function$
```

### `metric_audit.fn_intrinsic_decision_ready`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_intrinsic_decision_ready(p_mcv uuid)
 RETURNS boolean
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
  SELECT coalesce(array_length(metric_audit.fn_intrinsic_decision_refusal(p_mcv), 1), 0) = 0
$function$
```

### `metric_audit.fn_intrinsic_decision_refusal`

Refusal codes: `c1_state_not_audit_pending`, `c2_snapshot_not_computed`, `c6_no_effective_pass_decision`, `c3_head_evidence_signature_mismatch`, `c4_closure_root_mismatch`, `c5_no_operative_realization`, `c7_structural_or_foundation_not_pass`, `c8_contextual_below_threshold`, `c9_exactness_disagreement`, `c10_unresolved_blocking_nc`, `c11_feed_not_enforcement`, `c11_enforcement_registration_invalid`, `c11_registration_direction_invalid`, `c11_registration_signer_mismatch`, `c11_registration_signer_invalid`, `c11_feed_checkpoint_regressed`, `c12_effectively_invalidated`

Reads/writes: `dec.closure_root`, `dec.request_uid`, `fev.signer_key_id`, `mcf.exactness_reproof_evidence`, `mcf.mcv_package_snapshot`, `mcf.metric_contract_version`, `metric_audit.admission_recomputation_evidence`, `metric_audit.decision`, `metric_audit.decision_nc_reference`, `metric_audit.feed_checkpoint`, `metric_audit.feed_event`, `metric_audit.feed_registration`, `metric_audit.intrinsic_authority_pin`, `metric_audit.nc_reference`, `pin.authority_revision`, `pin.engine`, `pin.engine_version`, `pin.gate_policy_version`, `pin.methodology_digest`, `pin.methodology_version`, `pin.package_hash_algorithm`, `pin.source_authority_policy_digest`, `pin.source_authority_revision`, `snap.hash_algorithm_version`, `snap.metric_contract_uid`, `snap.metric_contract_version_uid`, `snap.package_signature_hash`, `snap.version_code`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_intrinsic_decision_refusal(p_mcv uuid)
 RETURNS text[]
 LANGUAGE plpgsql
 STABLE
AS $function$
DECLARE
  v_fail text[] := ARRAY[]::text[];
  v_state text;
  snap mcf.mcv_package_snapshot%ROWTYPE;
  v_decision uuid;
  dec metric_audit.decision%ROWTYPE;
  v_head uuid;
  ev metric_audit.admission_recomputation_evidence%ROWTYPE;
  fev metric_audit.feed_event%ROWTYPE;
  v_reg uuid;
  reg metric_audit.feed_registration%ROWTYPE;
  v_pin uuid;
  pin metric_audit.intrinsic_authority_pin%ROWTYPE;
  v_ckpt_seq bigint;
BEGIN
  SELECT governance_state_code INTO v_state FROM mcf.metric_contract_version WHERE metric_contract_version_uid = p_mcv;
  IF v_state IS DISTINCT FROM 'audit_pending' THEN v_fail := array_append(v_fail, 'c1_state_not_audit_pending'); END IF;
  SELECT * INTO snap FROM mcf.mcv_package_snapshot WHERE metric_contract_version_uid = p_mcv;
  IF snap.mcv_package_snapshot_uid IS NULL OR snap.disposition_code IS DISTINCT FROM 'computed' THEN
    v_fail := array_append(v_fail, 'c2_snapshot_not_computed'); END IF;
  v_decision := metric_audit.fn_effective_decision(p_mcv);
  IF v_decision IS NOT NULL THEN SELECT * INTO dec FROM metric_audit.decision WHERE decision_uid = v_decision; END IF;
  IF v_decision IS NULL OR dec.decision_code IS DISTINCT FROM 'PASS' THEN
    v_fail := array_append(v_fail, 'c6_no_effective_pass_decision'); END IF;
  IF v_decision IS NOT NULL THEN
    v_head := metric_audit.fn_admission_evidence_head(p_mcv, v_decision);
    IF v_head IS NOT NULL THEN SELECT * INTO ev FROM metric_audit.admission_recomputation_evidence WHERE evidence_uid = v_head; END IF;
  END IF;
  IF v_head IS NULL OR snap.package_signature_hash IS NULL
     OR ev.expected_snapshot_signature_hash IS DISTINCT FROM snap.package_signature_hash
     OR ev.recomputed_package_signature_hash IS DISTINCT FROM snap.package_signature_hash THEN
    v_fail := array_append(v_fail, 'c3_head_evidence_signature_mismatch'); END IF;
  IF v_decision IS NOT NULL AND snap.mcv_package_snapshot_uid IS NOT NULL THEN
    IF dec.package_snapshot_digest IS DISTINCT FROM snap.package_signature_hash
       OR dec.package_hash_algorithm IS DISTINCT FROM snap.hash_algorithm_version
       OR dec.package_hash_algorithm IS DISTINCT FROM 'mcf-package-v3'
       OR dec.metric_contract_version_uid IS DISTINCT FROM snap.metric_contract_version_uid
       OR dec.metric_contract_uid IS DISTINCT FROM snap.metric_contract_uid
       OR dec.version_code IS DISTINCT FROM snap.version_code THEN
      v_fail := array_append(v_fail, 'package_identity_mismatch'); END IF;
  END IF;
  IF v_head IS NOT NULL AND v_decision IS NOT NULL
     AND ev.request_uid IS DISTINCT FROM dec.request_uid THEN
    v_fail := array_append(v_fail, 'evidence_request_uid_mismatch'); END IF;
  IF v_head IS NULL OR v_decision IS NULL OR ev.recomputed_closure_root IS DISTINCT FROM dec.closure_root THEN
    v_fail := array_append(v_fail, 'c4_closure_root_mismatch'); END IF;
  IF metric_directory.fn_effective_realization_by_mcv(p_mcv) IS NULL THEN
    v_fail := array_append(v_fail, 'c5_no_operative_realization'); END IF;
  v_pin := metric_audit.fn_intrinsic_authority_pin_current();
  IF v_pin IS NULL THEN
    v_fail := array_append(v_fail, 'authority_pin_not_singular');
  ELSIF v_decision IS NOT NULL THEN
    SELECT * INTO pin FROM metric_audit.intrinsic_authority_pin WHERE pin_uid = v_pin;
    IF dec.source_authority_revision      IS DISTINCT FROM pin.source_authority_revision
       OR dec.source_authority_policy_digest IS DISTINCT FROM pin.source_authority_policy_digest
       OR dec.authority_revision          IS DISTINCT FROM pin.authority_revision
       OR dec.gate_policy_version         IS DISTINCT FROM pin.gate_policy_version
       OR dec.methodology_version         IS DISTINCT FROM pin.methodology_version
       OR dec.methodology_digest          IS DISTINCT FROM pin.methodology_digest
       OR dec.engine                      IS DISTINCT FROM pin.engine
       OR dec.engine_version              IS DISTINCT FROM pin.engine_version
       OR dec.package_hash_algorithm      IS DISTINCT FROM pin.package_hash_algorithm THEN
      v_fail := array_append(v_fail, 'authority_pin_mismatch'); END IF;
  END IF;
  IF v_decision IS NULL OR dec.structural_verdict IS DISTINCT FROM 'PASS' OR dec.foundation_verdict IS DISTINCT FROM 'PASS' THEN
    v_fail := array_append(v_fail, 'c7_structural_or_foundation_not_pass'); END IF;
  IF v_decision IS NULL
     OR coalesce(dec.contextual_definition_score, 0)       < 4
     OR coalesce(dec.contextual_formula_score, 0)          < 4
     OR coalesce(dec.contextual_input_semantics_score, 0)  < 4
     OR coalesce(dec.contextual_overall_score, 0)          < 4
     OR dec.contextual_decision IS NULL
     OR dec.contextual_decision NOT IN ('HIGH_CONFIDENCE','VERIFIED') THEN
    v_fail := array_append(v_fail, 'c8_contextual_below_threshold'); END IF;
  -- c9 (UNIT K, dec-414ba2): exactness-basis coherence. Three LABELLED arms; each reads a different
  -- evidence class; no arm substitutes for another (D532 condition 1). Absent decision fails as before.
  IF v_decision IS NULL OR snap.mcv_package_snapshot_uid IS NULL THEN
    v_fail := array_append(v_fail, 'c9_exactness_disagreement');
  ELSIF dec.exactness_basis = 'EXACT_SNAPSHOT' THEN
    -- legacy arm, byte-identical requirements: snapshot proved EXACT at freeze + binary64-eligible.
    IF dec.exactness_result IS DISTINCT FROM 'EXACT'
       OR snap.exactness_result IS DISTINCT FROM 'EXACT'
       OR snap.binary64_activation_eligible IS NOT TRUE THEN
      v_fail := array_append(v_fail, 'c9_exactness_disagreement'); END IF;
  ELSIF dec.exactness_basis = 'EXACT_REPROOF' THEN
    -- prong-(a) re-proof arm: EXACT evidence in the append-only ledger over the SAME frozen package bytes.
    IF dec.exactness_result IS DISTINCT FROM 'EXACT'
       OR NOT EXISTS (
         SELECT 1 FROM mcf.exactness_reproof_evidence e
          WHERE e.metric_contract_version_uid = p_mcv
            AND e.prover_algorithm_version = 'mcf-exactness-v2'
            AND e.verdict_code = 'EXACT'
            AND e.package_signature_hash = snap.package_signature_hash) THEN
      v_fail := array_append(v_fail, 'c9_exactness_disagreement'); END IF;
  ELSIF dec.exactness_basis = 'REPRODUCIBLE' THEN
    -- prong-(b) arm (D532): correctly-rounded REPRODUCIBLE evidence over the same frozen package bytes.
    IF dec.exactness_result IS DISTINCT FROM 'REPRODUCIBLE'
       OR NOT EXISTS (
         SELECT 1 FROM mcf.exactness_reproof_evidence e
          WHERE e.metric_contract_version_uid = p_mcv
            AND e.prover_algorithm_version = 'mcf-reproducibility-v1'
            AND e.verdict_code = 'REPRODUCIBLE'
            AND e.package_signature_hash = snap.package_signature_hash) THEN
      v_fail := array_append(v_fail, 'c9_exactness_disagreement'); END IF;
  ELSE
    v_fail := array_append(v_fail, 'c9_exactness_disagreement');
  END IF;
  IF v_decision IS NOT NULL AND EXISTS (
       SELECT 1 FROM metric_audit.decision_nc_reference dn
         JOIN metric_audit.nc_reference nr ON nr.nc_uid = dn.nc_uid
        WHERE dn.decision_uid = v_decision AND dn.is_blocking AND nr.status = 'OPEN') THEN
    v_fail := array_append(v_fail, 'c10_unresolved_blocking_nc'); END IF;
  IF v_decision IS NULL OR dec.feed_mode IS DISTINCT FROM 'enforcement' THEN
    v_fail := array_append(v_fail, 'c11_feed_not_enforcement');
  ELSE
    SELECT * INTO fev FROM metric_audit.feed_event WHERE event_uid = dec.feed_event_uid;
    IF fev.event_uid IS NOT NULL THEN
      v_reg := metric_audit.fn_effective_feed_registration(fev.feed_name);
      IF v_reg IS NOT NULL THEN SELECT * INTO reg FROM metric_audit.feed_registration WHERE registration_uid = v_reg; END IF;
    END IF;
    IF fev.event_uid IS NULL
       OR fev.feed_mode IS DISTINCT FROM 'enforcement'
       OR v_reg IS NULL
       OR reg.feed_mode IS DISTINCT FROM 'enforcement'
       OR reg.valid_from > fev.issued_at
       OR NOT (reg.allowed_events @> jsonb_build_array(jsonb_build_object(
                 'payload_schema_version', fev.payload_schema_version, 'event_kind', fev.event_kind)))
       OR NOT metric_audit.fn_signer_key_valid_at(fev.signer_key_id, fev.issued_at) THEN
      v_fail := array_append(v_fail, 'c11_enforcement_registration_invalid');
    END IF;
    IF fev.event_uid IS NOT NULL AND v_reg IS NOT NULL THEN
      IF reg.direction IS DISTINCT FROM 'auditor_to_platform' THEN
        v_fail := array_append(v_fail, 'c11_registration_direction_invalid'); END IF;
      IF reg.signer_key_id IS DISTINCT FROM fev.signer_key_id THEN
        v_fail := array_append(v_fail, 'c11_registration_signer_mismatch'); END IF;
      IF NOT metric_audit.fn_signer_key_valid_at(reg.signer_key_id, fev.issued_at) THEN
        v_fail := array_append(v_fail, 'c11_registration_signer_invalid'); END IF;
      SELECT last_verified_sequence INTO v_ckpt_seq FROM metric_audit.feed_checkpoint WHERE feed_name = fev.feed_name;
      IF v_ckpt_seq IS NULL OR v_ckpt_seq < fev.feed_sequence THEN
        v_fail := array_append(v_fail, 'c11_feed_checkpoint_regressed'); END IF;
    END IF;
  END IF;
  IF metric_audit.fn_mcv_effectively_invalidated(p_mcv) THEN
    v_fail := array_append(v_fail, 'c12_effectively_invalidated'); END IF;
  RETURN v_fail;
END
$function$
```

### `metric_audit.fn_invalidation_immutability`

Reads/writes: `new.cause_kind`, `new.invalidated_at`, `new.invalidation_uid`, `new.metric_contract_version_uid`, `new.root_cause_fingerprint`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_invalidation_immutability()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  IF TG_OP='DELETE' THEN RAISE EXCEPTION 'metric_audit.invalidation is append-only (DELETE refused, Invariant III)' USING ERRCODE='check_violation'; END IF;
  IF OLD.invalidation_uid IS DISTINCT FROM NEW.invalidation_uid
     OR OLD.metric_contract_version_uid IS DISTINCT FROM NEW.metric_contract_version_uid
     OR OLD.cause_kind IS DISTINCT FROM NEW.cause_kind
     OR OLD.root_cause_fingerprint IS DISTINCT FROM NEW.root_cause_fingerprint
     OR OLD.invalidated_at IS DISTINCT FROM NEW.invalidated_at THEN
    RAISE EXCEPTION 'metric_audit.invalidation identity is immutable (Invariant III)' USING ERRCODE='check_violation'; END IF;
  IF OLD.cleared_at IS NOT NULL THEN RAISE EXCEPTION 'invalidation already cleared (append-only)' USING ERRCODE='check_violation'; END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_mcv_effectively_invalidated`

Reads/writes: `metric_audit.invalidation`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_mcv_effectively_invalidated(p_mcv uuid)
 RETURNS boolean
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
  SELECT EXISTS (SELECT 1 FROM metric_audit.invalidation
                 WHERE metric_contract_version_uid = p_mcv AND cleared_at IS NULL)
$function$
```

### `metric_audit.fn_nc_reference_guard`

Reads/writes: `ev.payload_digest`, `metric_audit.feed_event`, `metric_audit.report_raised_nc`, `metric_audit.report_reference`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_nc_reference_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE ev metric_audit.feed_event%ROWTYPE; p jsonb;
BEGIN
  SELECT * INTO ev FROM metric_audit.feed_event WHERE event_uid = NEW.feed_event_uid;
  IF ev.event_uid IS NULL THEN RAISE EXCEPTION 'nc_reference cites a non-existent feed_event %', NEW.feed_event_uid; END IF;
  IF ev.payload_schema_version IS DISTINCT FROM 'external-audit-nc-v2' THEN
    RAISE EXCEPTION 'nc_reference feed_event is not an external-audit-nc-v2 event'; END IF;
  IF NEW.nc_payload_digest IS DISTINCT FROM ev.payload_digest THEN
    RAISE EXCEPTION 'nc_reference nc_payload_digest != feed_event.payload_digest'; END IF;
  p := convert_from(ev.canonical_payload,'UTF8')::jsonb;
  IF NEW.nc_uid IS DISTINCT FROM (p->>'nc_uid')::uuid
     OR NEW.report_uid IS DISTINCT FROM (p#>>'{report_ref,report_uid}')::uuid
     OR NEW.finding_uid IS DISTINCT FROM (p#>>'{report_ref,finding_uid}')::uuid
     OR NEW.severity IS DISTINCT FROM p->>'severity'
     OR NEW.scope IS DISTINCT FROM p->>'scope'
     OR NEW.remediation_direction IS DISTINCT FROM p->>'remediation_direction'
     OR NEW.acceptance_criteria_json IS DISTINCT FROM p->'acceptance_criteria'
     OR NEW.requirement_json IS DISTINCT FROM p->'requirement'
     OR NEW.observed_condition IS DISTINCT FROM p->>'observed_condition'
     OR NEW.expected_condition IS DISTINCT FROM p->>'expected_condition'
     OR NEW.impact IS DISTINCT FROM p->>'impact'
     OR NEW.objective_evidence_json IS DISTINCT FROM p->'objective_evidence'
     OR NEW.re_audit_trigger_json IS DISTINCT FROM p->'re_audit_trigger'
     OR NEW.issued_by IS DISTINCT FROM p->>'issued_by'
     OR NEW.issued_at IS DISTINCT FROM (p->>'issued_at')::timestamptz                       -- P0-3: bound
     OR NEW.status IS DISTINCT FROM p->>'status' THEN
    RAISE EXCEPTION 'nc_reference projection is detached from the signed NC payload'; END IF;
  -- acceptance_criteria + remediation must be present (plan test)
  IF jsonb_array_length(coalesce(NEW.acceptance_criteria_json,'[]'::jsonb)) = 0 THEN
    RAISE EXCEPTION 'nc_reference requires non-empty acceptance_criteria'; END IF;
  -- the NC must be a raised NC of its cited report (relational closure)
  IF NOT EXISTS (SELECT 1 FROM metric_audit.report_raised_nc WHERE report_uid = NEW.report_uid AND nc_uid = NEW.nc_uid) THEN
    RAISE EXCEPTION 'nc_reference % is not a raised NC of report %', NEW.nc_uid, NEW.report_uid; END IF;
  -- P0-3: C1 NC->report closure — the signed NC's report_ref.report_digest must equal the bound report's payload digest
  IF (p#>>'{report_ref,report_digest}') IS DISTINCT FROM
       (SELECT report_payload_digest FROM metric_audit.report_reference WHERE report_uid = NEW.report_uid) THEN
    RAISE EXCEPTION 'nc_reference report_ref.report_digest != bound report payload digest'; END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_platform_signer_valid_at`

Reads/writes: `metric_audit.platform_signer`, `metric_audit.platform_signer_event`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_platform_signer_valid_at(p_key text, p_at timestamp with time zone)
 RETURNS boolean
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
  SELECT k.valid_from <= p_at
     AND NOT EXISTS (SELECT 1 FROM metric_audit.platform_signer_event e WHERE e.signer_key_id=p_key AND e.event_kind='revoke_compromise_retroactive')
     AND NOT EXISTS (SELECT 1 FROM metric_audit.platform_signer_event e WHERE e.signer_key_id=p_key AND e.event_kind IN ('expire','rotate','revoke_prospective') AND p_at >= e.effective_at)
  FROM metric_audit.platform_signer k WHERE k.signer_key_id = p_key $function$
```

### `metric_audit.fn_preflight_disposition_guard`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_preflight_disposition_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN
  IF NEW.attempt_digest <> metric_audit.preflight_attempt_digest(
       NEW.metric_contract_version_uid, NEW.cohort_code, NEW.disposition_code, NEW.reason_details_json,
       NEW.authority_revision, NEW.substrate_fingerprint, NEW.attempted_package_snapshot_digest,
       NEW.attempted_closure_root, NEW.actor) THEN
    RAISE EXCEPTION 'preflight_disposition attempt_digest does not match the DB-recomputed semantic identity (forged/tampered column)'
      USING ERRCODE='check_violation';
  END IF;
  -- P1-2: created_at is DB-owned, not caller-forgeable. Force the event time at the boundary,
  -- overwriting any supplied value (a direct-owner insert cannot choose e.g. 1900-01-01).
  NEW.created_at := now();
  RETURN NEW;
END $function$
```

### `metric_audit.fn_preflight_disposition_immutability`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_preflight_disposition_immutability()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN
  RAISE EXCEPTION 'metric_audit.request_preflight_disposition is append-only (% refused)', TG_OP USING ERRCODE='check_violation';
END $function$
```

### `metric_audit.fn_reintake_accepted_immutable`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_reintake_accepted_immutable()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  RAISE EXCEPTION 'metric_audit.% is append-only (accepted-manifest authority is immutable)', TG_TABLE_NAME USING ERRCODE='check_violation';
END $function$
```

### `metric_audit.fn_reintake_batch_immutable`

Reads/writes: `old.authorization_rationale_text`, `old.authorized_at`, `old.authorized_by`, `old.cohort_scope`, `old.created_at`, `old.manifest_canonical_set_hash`, `old.reintake_batch_uid`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_reintake_batch_immutable()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  IF TG_OP='DELETE' THEN
    RAISE EXCEPTION 'metric_audit.reintake_batch is append-only (no delete)' USING ERRCODE='check_violation'; END IF;
  IF NEW.reintake_batch_uid IS DISTINCT FROM OLD.reintake_batch_uid
     OR NEW.manifest_canonical_set_hash IS DISTINCT FROM OLD.manifest_canonical_set_hash
     OR NEW.cohort_scope IS DISTINCT FROM OLD.cohort_scope
     OR NEW.authorized_by IS DISTINCT FROM OLD.authorized_by
     OR NEW.authorization_rationale_text IS DISTINCT FROM OLD.authorization_rationale_text
     OR NEW.authorized_at IS DISTINCT FROM OLD.authorized_at
     OR NEW.created_at IS DISTINCT FROM OLD.created_at THEN
    RAISE EXCEPTION 'metric_audit.reintake_batch: only status may change (open->closed)' USING ERRCODE='check_violation'; END IF;
  IF NOT (OLD.status='open' AND NEW.status='closed') THEN
    RAISE EXCEPTION 'metric_audit.reintake_batch.status may only transition open->closed' USING ERRCODE='check_violation'; END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_reintake_batch_member_cohort_authorized`

Reads/writes: `metric_audit.reintake_batch_cohort`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_reintake_batch_member_cohort_authorized()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM metric_audit.reintake_batch_cohort c
    WHERE c.reintake_batch_uid = NEW.reintake_batch_uid
      AND c.cohort = NEW.cohort
      AND c.disposition = 'eligible'
  ) THEN
    RAISE EXCEPTION 'reintake batch member refused: cohort % is not an ELIGIBLE cohort of batch %',
      NEW.cohort, NEW.reintake_batch_uid USING ERRCODE='check_violation';
  END IF;
  RETURN NEW;
END;
$function$
```

### `metric_audit.fn_reintake_batch_member_immutable`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_reintake_batch_member_immutable()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  RAISE EXCEPTION 'metric_audit.reintake_batch_member is append-only (no update/delete)' USING ERRCODE='check_violation';
END $function$
```

### `metric_audit.fn_reintake_member_accepted_check`

Reads/writes: `metric_audit.reintake_accepted_member`, `metric_audit.reintake_batch`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_reintake_member_accepted_check()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE v_hash text;
BEGIN
  SELECT manifest_canonical_set_hash INTO v_hash FROM metric_audit.reintake_batch WHERE reintake_batch_uid = NEW.reintake_batch_uid;
  IF NOT EXISTS (SELECT 1 FROM metric_audit.reintake_accepted_member am
                 WHERE am.canonical_set_hash = v_hash AND am.member_uid = NEW.member_uid
                   AND am.member_version_uid = NEW.member_version_uid
                   AND am.metric_contract_version_uid = NEW.metric_contract_version_uid
                   AND am.cohort = NEW.cohort) THEN
    RAISE EXCEPTION 'reintake_batch_member tuple not in the accepted manifest % (member_uid=%, member_version_uid=%, mcv=%, cohort=%)',
      v_hash, NEW.member_uid, NEW.member_version_uid, NEW.metric_contract_version_uid, NEW.cohort USING ERRCODE='check_violation'; END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_reject_mutation`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_reject_mutation()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN RAISE EXCEPTION 'governed table %.% is append-only (Invariant III): % rejected', TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP; END $function$
```

### `metric_audit.fn_report_finding_membership`

Reads/writes: `metric_audit.feed_event`, `metric_audit.report_reference`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_report_finding_membership()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE ev metric_audit.feed_event%ROWTYPE; p jsonb; f jsonb; found boolean := false;
BEGIN
  SELECT fe.* INTO ev FROM metric_audit.report_reference r JOIN metric_audit.feed_event fe ON fe.event_uid = r.feed_event_uid
    WHERE r.report_uid = NEW.report_uid;
  IF ev.event_uid IS NULL THEN RAISE EXCEPTION 'report_finding cites a report with no verified feed_event %', NEW.report_uid; END IF;
  p := convert_from(ev.canonical_payload,'UTF8')::jsonb;
  FOR f IN SELECT jsonb_array_elements(p->'findings') LOOP
    IF (f->>'finding_uid')::uuid = NEW.finding_uid THEN
      IF NEW.finding_kind IS DISTINCT FROM f->>'finding_kind'
         OR NEW.severity IS DISTINCT FROM f->>'severity'
         OR NEW.area IS DISTINCT FROM f->>'area'
         OR NEW.description IS DISTINCT FROM f->>'description'
         OR NEW.nc_uid IS DISTINCT FROM (f->>'nc_uid')::uuid
         OR NEW.evidence_citations_json IS DISTINCT FROM f->'evidence_citations' THEN
        RAISE EXCEPTION 'report_finding % typed values diverge from the signed report finding', NEW.finding_uid; END IF;
      found := true; EXIT; END IF;
  END LOOP;
  IF NOT found THEN RAISE EXCEPTION 'report_finding % is not a member of the signed report findings', NEW.finding_uid; END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_report_raised_nc_membership`

Reads/writes: `metric_audit.feed_event`, `metric_audit.report_reference`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_report_raised_nc_membership()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE ev metric_audit.feed_event%ROWTYPE; p jsonb;
BEGIN
  SELECT fe.* INTO ev FROM metric_audit.report_reference r JOIN metric_audit.feed_event fe ON fe.event_uid = r.feed_event_uid
    WHERE r.report_uid = NEW.report_uid;
  IF ev.event_uid IS NULL THEN RAISE EXCEPTION 'report_raised_nc cites a report with no verified feed_event %', NEW.report_uid; END IF;
  p := convert_from(ev.canonical_payload,'UTF8')::jsonb;
  IF NOT (p->'ncs_raised' @> to_jsonb(NEW.nc_uid::text)) THEN
    RAISE EXCEPTION 'report_raised_nc % is not in the signed report ncs_raised set', NEW.nc_uid; END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_report_reference_finalize`

Reads/writes: `metric_audit.feed_event`, `metric_audit.report_finding`, `metric_audit.report_raised_nc`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_report_reference_finalize()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE ev metric_audit.feed_event%ROWTYPE; p jsonb; v_exp_findings int; v_act_findings int; v_exp_ncs int; v_act_ncs int;
BEGIN
  SELECT * INTO ev FROM metric_audit.feed_event WHERE event_uid = NEW.feed_event_uid;
  p := convert_from(ev.canonical_payload,'UTF8')::jsonb;
  v_exp_findings := jsonb_array_length(coalesce(p->'findings','[]'::jsonb));
  SELECT count(*) INTO v_act_findings FROM metric_audit.report_finding WHERE report_uid = NEW.report_uid;
  IF v_act_findings <> v_exp_findings THEN
    RAISE EXCEPTION 'report_reference % finalize: % findings projected, payload declares %', NEW.report_uid, v_act_findings, v_exp_findings; END IF;
  v_exp_ncs := jsonb_array_length(coalesce(p->'ncs_raised','[]'::jsonb));
  SELECT count(*) INTO v_act_ncs FROM metric_audit.report_raised_nc WHERE report_uid = NEW.report_uid;
  IF v_act_ncs <> v_exp_ncs THEN
    RAISE EXCEPTION 'report_reference % finalize: % ncs_raised projected, payload declares %', NEW.report_uid, v_act_ncs, v_exp_ncs; END IF;
  RETURN NULL;
END $function$
```

### `metric_audit.fn_report_reference_guard`

Reads/writes: `ev.payload_digest`, `metric_audit.feed_event`, `metric_audit.request_publication`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_report_reference_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE ev metric_audit.feed_event%ROWTYPE; p jsonb; pub metric_audit.request_publication%ROWTYPE; req jsonb;
BEGIN
  SELECT * INTO ev FROM metric_audit.feed_event WHERE event_uid = NEW.feed_event_uid;
  IF ev.event_uid IS NULL THEN RAISE EXCEPTION 'report_reference cites a non-existent feed_event %', NEW.feed_event_uid; END IF;
  IF ev.payload_schema_version IS DISTINCT FROM 'metric-audit-report-v5' THEN
    RAISE EXCEPTION 'report_reference feed_event is not a metric-audit-report-v5 event'; END IF;
  IF NEW.report_payload_digest IS DISTINCT FROM ev.payload_digest THEN
    RAISE EXCEPTION 'report_reference report_payload_digest != feed_event.payload_digest'; END IF;
  p := convert_from(ev.canonical_payload,'UTF8')::jsonb;
  IF NEW.report_uid IS DISTINCT FROM (p->>'report_uid')::uuid
     OR NEW.request_uid IS DISTINCT FROM (p#>>'{request_ref,request_uid}')::uuid
     OR NEW.request_digest IS DISTINCT FROM p#>>'{request_ref,request_digest}'
     OR NEW.metric_contract_version_uid IS DISTINCT FROM (p#>>'{subject,metric_contract_version_uid}')::uuid
     OR NEW.metric_contract_uid IS DISTINCT FROM (p#>>'{subject,metric_contract_uid}')::uuid
     OR NEW.package_snapshot_digest IS DISTINCT FROM p#>>'{subject,package_snapshot_digest}'
     OR NEW.closure_root IS DISTINCT FROM p#>>'{subject,closure_root}'
     OR NEW.audit_run_uid IS DISTINCT FROM (p->>'audit_run_uid')::uuid
     OR NEW.engine IS DISTINCT FROM p->>'engine' OR NEW.engine_version IS DISTINCT FROM p->>'engine_version'
     OR NEW.methodology_version IS DISTINCT FROM p->>'methodology_version'
     OR NEW.methodology_digest IS DISTINCT FROM p->>'methodology_digest'
     OR NEW.authority_revision IS DISTINCT FROM p->>'authority_revision'
     OR NEW.gate_policy_version IS DISTINCT FROM p->>'gate_policy_version'
     OR NEW.source_authority_revision IS DISTINCT FROM p->>'source_authority_revision'
     OR NEW.overall_assessment IS DISTINCT FROM p->>'overall_assessment'
     OR NEW.structural_verdict IS DISTINCT FROM p#>>'{structural,verdict}'
     OR NEW.foundation_verdict IS DISTINCT FROM p#>>'{foundation,verdict}'
     OR NEW.contextual_definition_score IS DISTINCT FROM (p#>>'{contextual,definition,score}')::int
     OR NEW.contextual_formula_score IS DISTINCT FROM (p#>>'{contextual,formula,score}')::int
     OR NEW.contextual_input_semantics_score IS DISTINCT FROM (p#>>'{contextual,canonical_input_semantics,score}')::int
     OR NEW.contextual_overall_score IS DISTINCT FROM (p#>>'{contextual,overall_score}')::int
     OR NEW.contextual_decision IS DISTINCT FROM p#>>'{contextual,decision}'
     OR NEW.exactness_result IS DISTINCT FROM p->>'exactness_result'
     OR NEW.audited_at IS DISTINCT FROM (p->>'audited_at')::timestamptz THEN                -- P0-3: bound
    RAISE EXCEPTION 'report_reference projection is detached from the signed report payload'; END IF;
  -- semantic_conformance is optional in the payload; NOT_APPLICABLE when absent
  IF NEW.semantic_conformance_verdict IS DISTINCT FROM coalesce(p#>>'{semantic_conformance,verdict}','NOT_APPLICABLE') THEN
    RAISE EXCEPTION 'report_reference semantic_conformance_verdict detached from payload'; END IF;
  -- review P0-1: the cited request MUST be a signed publication, AND the report must agree with the
  -- published request PAYLOAD (self-digest + subject/package/closure). request_ref.request_digest is the
  -- request's canonical SELF-identity (== the published request's own request_digest), NOT the transport
  -- payload_digest — we compare self-to-self here, never to payload_digest.
  SELECT * INTO pub FROM metric_audit.request_publication WHERE request_uid = NEW.request_uid;
  IF pub.request_uid IS NULL THEN RAISE EXCEPTION 'report_reference request % is not a signed publication', NEW.request_uid; END IF;
  req := convert_from(pub.canonical_payload,'UTF8')::jsonb;
  IF NEW.request_digest IS DISTINCT FROM req->>'request_digest'
     OR NEW.metric_contract_version_uid IS DISTINCT FROM (req#>>'{subject,metric_contract_version_uid}')::uuid
     OR NEW.package_snapshot_digest IS DISTINCT FROM req#>>'{package,package_snapshot_digest}'
     OR NEW.closure_root IS DISTINCT FROM req->>'closure_root'
     -- review P0-1: when the report carries the optional MC coordinate it must equal the request's MC
     OR (NEW.metric_contract_uid IS NOT NULL
         AND NEW.metric_contract_uid IS DISTINCT FROM (req#>>'{subject,metric_contract_uid}')::uuid) THEN
    RAISE EXCEPTION 'report_reference disagrees with the published request payload (subject/mc/package/closure/digest)'; END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_request_outbox_guard`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_request_outbox_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE p jsonb;
BEGIN
  IF NEW.request_digest <> 'sha256:' || encode(sha256(NEW.request_canonical_bytes),'hex') THEN
    RAISE EXCEPTION 'request_outbox request_digest != sha256(request_canonical_bytes) [transport digest]'; END IF;
  p := convert_from(NEW.request_canonical_bytes,'UTF8')::jsonb;
  IF p->>'schema_version' IS DISTINCT FROM 'metric-audit-request-v1' THEN
    RAISE EXCEPTION 'request_outbox canonical bytes are not a metric-audit-request-v1 payload'; END IF;
  IF NEW.request_uid IS DISTINCT FROM (p->>'request_uid')::uuid
     OR NEW.metric_contract_version_uid IS DISTINCT FROM (p#>>'{subject,metric_contract_version_uid}')::uuid
     OR NEW.package_snapshot_digest IS DISTINCT FROM p#>>'{package,package_snapshot_digest}'
     OR NEW.closure_root IS DISTINCT FROM p->>'closure_root'
     OR NEW.trigger_kind IS DISTINCT FROM p#>>'{trigger,trigger_kind}'
     OR NEW.cause_kind IS DISTINCT FROM p#>>'{trigger,cause_ref,cause_kind}'
     OR NEW.cause_uid IS DISTINCT FROM p#>>'{trigger,cause_ref,cause_uid}'
     OR NEW.authority_revision IS DISTINCT FROM p->>'authority_revision'
     OR NEW.feed_name IS DISTINCT FROM p#>>'{feed,feed_name}' THEN
    RAISE EXCEPTION 'request_outbox columns are detached from the canonical request payload'; END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_request_publication_guard`

Reads/writes: `metric_audit.platform_signer`, `metric_audit.request_outbox`, `metric_audit.request_publication`, `new.envelope_digest`, `new.feed_name`, `new.feed_sequence`, `new.payload_digest`, `new.platform_signer_fingerprint`, `new.platform_signer_key_id`, `new.signature_algorithm`, `new.signature_b`, `o.feed_name`, `o.request_canonical_bytes`, `o.request_digest`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_request_publication_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE o metric_audit.request_outbox%ROWTYPE; env jsonb; v_prev_digest text; v_prev_max bigint; v_fp text; v_alg text;
BEGIN
  IF NEW.payload_digest <> 'sha256:' || encode(sha256(NEW.canonical_payload),'hex') THEN
    RAISE EXCEPTION 'request_publication payload_digest != sha256(canonical_payload)'; END IF;
  SELECT * INTO o FROM metric_audit.request_outbox WHERE request_uid = NEW.request_uid;
  IF o.request_uid IS NULL THEN RAISE EXCEPTION 'request_publication cites no outbox row %', NEW.request_uid; END IF;
  -- bind publication to the EXACT outbox request (bytes + feed + payload_digest)
  IF NEW.canonical_payload IS DISTINCT FROM o.request_canonical_bytes THEN
    RAISE EXCEPTION 'request_publication canonical_payload != outbox request bytes for %', NEW.request_uid; END IF;
  IF NEW.feed_name IS DISTINCT FROM o.feed_name THEN
    RAISE EXCEPTION 'request_publication feed % != outbox feed % ', NEW.feed_name, o.feed_name; END IF;
  IF NEW.payload_digest IS DISTINCT FROM o.request_digest THEN
    RAISE EXCEPTION 'request_publication payload_digest != outbox request_digest'; END IF;
  -- the duplicated columns must equal the signed envelope contents
  env := NEW.signed_envelope_json;
  IF env->>'payload_digest' IS DISTINCT FROM NEW.payload_digest
     OR env->>'envelope_digest' IS DISTINCT FROM NEW.envelope_digest
     OR env->>'signature_b64' IS DISTINCT FROM NEW.signature_b64
     OR env->>'signature_algorithm' IS DISTINCT FROM NEW.signature_algorithm
     OR env->>'signer_key_id' IS DISTINCT FROM NEW.platform_signer_key_id
     OR env->>'feed_name' IS DISTINCT FROM NEW.feed_name
     OR (env->>'feed_sequence')::bigint IS DISTINCT FROM NEW.feed_sequence THEN
    RAISE EXCEPTION 'request_publication columns diverge from signed_envelope_json'; END IF;
  -- C2R2-P0-2: the signed envelope's OWN payload must be the exact outbox request (the detached-payload
  -- class C1 closed). The envelope carries payload as an object; its digest must equal the outbox
  -- request_digest AND the request bytes must parse to that same payload object.
  IF env->>'payload_digest' IS DISTINCT FROM o.request_digest THEN
    RAISE EXCEPTION 'request_publication envelope payload_digest != outbox request_digest'; END IF;
  IF (env->'payload') IS DISTINCT FROM convert_from(o.request_canonical_bytes,'UTF8')::jsonb THEN
    RAISE EXCEPTION 'request_publication signed envelope payload != outbox request payload'; END IF;
  -- outgoing signer must be CURRENT (lifecycle-aware) in the governed registry + fingerprint/algo match
  IF NOT metric_audit.fn_platform_signer_valid_at(NEW.platform_signer_key_id, NEW.published_at) THEN
    RAISE EXCEPTION 'request_publication signer % not a valid platform signer at % (retired/revoked/absent)', NEW.platform_signer_key_id, NEW.published_at; END IF;
  SELECT fingerprint, algorithm INTO v_fp, v_alg FROM metric_audit.platform_signer WHERE signer_key_id = NEW.platform_signer_key_id;
  IF v_fp IS DISTINCT FROM NEW.platform_signer_fingerprint OR v_alg IS DISTINCT FROM NEW.signature_algorithm THEN
    RAISE EXCEPTION 'request_publication signer fingerprint/algorithm mismatch vs governed platform_signer'; END IF;
  -- sequence contiguity + chain on the outgoing feed
  SELECT max(feed_sequence) INTO v_prev_max FROM metric_audit.request_publication WHERE feed_name = NEW.feed_name;
  IF NEW.feed_sequence = 1 THEN
    IF v_prev_max IS NOT NULL THEN RAISE EXCEPTION 'request_publication % already has events; seq 1 rejected', NEW.feed_name; END IF;
  ELSE
    IF v_prev_max IS DISTINCT FROM NEW.feed_sequence - 1 THEN
      RAISE EXCEPTION 'request_publication gap/fork: % expected %, got %', NEW.feed_name, coalesce(v_prev_max,0)+1, NEW.feed_sequence; END IF;
    SELECT envelope_digest INTO v_prev_digest FROM metric_audit.request_publication
      WHERE feed_name = NEW.feed_name AND feed_sequence = NEW.feed_sequence - 1;
    IF NEW.prior_event_digest IS DISTINCT FROM v_prev_digest THEN
      RAISE EXCEPTION 'request_publication broken chain at % seq %', NEW.feed_name, NEW.feed_sequence; END IF;
  END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.fn_signer_key_valid_at`

Reads/writes: `metric_audit.signer_key`, `metric_audit.signer_key_event`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_signer_key_valid_at(p_key text, p_at timestamp with time zone)
 RETURNS boolean
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
  SELECT k.valid_from <= p_at
     AND NOT EXISTS (SELECT 1 FROM metric_audit.signer_key_event e WHERE e.key_id=p_key AND e.event_kind='revoke_compromise_retroactive')
     AND NOT EXISTS (SELECT 1 FROM metric_audit.signer_key_event e WHERE e.key_id=p_key AND e.event_kind IN ('expire','rotate','revoke_prospective') AND p_at >= e.effective_at)
  FROM metric_audit.signer_key k WHERE k.key_id = p_key $function$
```

### `metric_audit.fn_transition_evidence_guard`

Reads/writes: `cr.action_code`, `cr.from_state_code`, `cr.primitive_id`, `cr.to_state_code`, `mcf.certification_record`, `metric_audit.decision`, `metric_audit.fn_effective_decision`, `metric_audit.request_outbox`, `new.metric_contract_version_uid`

```sql
CREATE OR REPLACE FUNCTION metric_audit.fn_transition_evidence_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE cr mcf.certification_record%ROWTYPE; d metric_audit.decision%ROWTYPE; v_head uuid; ob metric_audit.request_outbox%ROWTYPE;
BEGIN
  SELECT * INTO cr FROM mcf.certification_record WHERE certification_record_id = NEW.certification_record_id;
  IF cr.certification_record_id IS NULL THEN RAISE EXCEPTION 'transition_evidence cites a non-existent cert %', NEW.certification_record_id; END IF;
  IF NEW.action_code IS DISTINCT FROM cr.action_code
     OR NEW.from_state_code IS DISTINCT FROM cr.from_state_code
     OR NEW.to_state_code IS DISTINCT FROM cr.to_state_code
     OR NEW.metric_contract_version_uid IS DISTINCT FROM cr.primitive_id
     OR cr.primitive_type IS DISTINCT FROM 'metric_contract_version' THEN
    RAISE EXCEPTION 'transition_evidence does not match its certification_record (action/from/to/primitive)'; END IF;
  IF NEW.request_uid IS NOT NULL THEN
    SELECT * INTO ob FROM metric_audit.request_outbox WHERE request_uid = NEW.request_uid;
    IF ob.request_uid IS NULL THEN RAISE EXCEPTION 'transition_evidence request % not in outbox', NEW.request_uid; END IF;
    IF ob.metric_contract_version_uid IS DISTINCT FROM NEW.metric_contract_version_uid THEN
      RAISE EXCEPTION 'transition_evidence request targets a different MCV'; END IF;
  END IF;
  IF NEW.action_code = 'audit_block' THEN
    SELECT * INTO d FROM metric_audit.decision WHERE decision_uid = NEW.decision_uid;
    IF d.decision_uid IS NULL THEN RAISE EXCEPTION 'transition_evidence cites a non-existent decision %', NEW.decision_uid; END IF;
    IF d.metric_contract_version_uid IS DISTINCT FROM NEW.metric_contract_version_uid THEN
      RAISE EXCEPTION 'transition_evidence block decision targets a different MCV'; END IF;
    IF NEW.block_reason_kind = 'rejected_decision' THEN
      IF NEW.decision_uid IS DISTINCT FROM metric_audit.fn_effective_decision(NEW.metric_contract_version_uid) OR d.decision_code <> 'REJECT' THEN
        RAISE EXCEPTION 'rejected_decision block must cite the effective REJECT head'; END IF;
    ELSIF NEW.block_reason_kind = 'revoked_decision' THEN
      v_head := metric_audit.fn_decision_stream_head(NEW.metric_contract_version_uid);
      IF NEW.decision_uid IS DISTINCT FROM v_head OR d.decision_code <> 'REVOKE' THEN
        RAISE EXCEPTION 'revoked_decision block must cite the structural REVOKE head'; END IF;
    END IF;
  END IF;
  -- C8: audit_admit activation evidence must cite the effective, non-revoked PASS head for THIS MCV.
  IF NEW.action_code = 'audit_admit' THEN
    SELECT * INTO d FROM metric_audit.decision WHERE decision_uid = NEW.decision_uid;
    IF d.decision_uid IS NULL THEN RAISE EXCEPTION 'transition_evidence cites a non-existent decision %', NEW.decision_uid; END IF;
    IF d.metric_contract_version_uid IS DISTINCT FROM NEW.metric_contract_version_uid THEN
      RAISE EXCEPTION 'audit_admit evidence decision targets a different MCV'; END IF;
    IF NEW.decision_uid IS DISTINCT FROM metric_audit.fn_effective_decision(NEW.metric_contract_version_uid)
       OR d.decision_code <> 'PASS' THEN
      RAISE EXCEPTION 'audit_admit evidence must cite the effective PASS decision'; END IF;
  END IF;
  RETURN NEW;
END $function$
```

### `metric_audit.preflight_attempt_digest`

```sql
CREATE OR REPLACE FUNCTION metric_audit.preflight_attempt_digest(p_mcv uuid, p_cohort text, p_disposition text, p_reasons jsonb, p_authority text, p_fingerprint text, p_pkg text, p_closure text, p_actor text)
 RETURNS text
 LANGUAGE sql
 IMMUTABLE
 SET search_path TO 'pg_catalog'
AS $function$
  SELECT 'sha256:' || encode(sha256(convert_to(jsonb_build_object(
    'schema_version', 'bc-request-preflight-disposition-v2',
    'metric_contract_version_uid', p_mcv,
    'cohort_code', p_cohort,
    'disposition_code', p_disposition,
    'reason_details', p_reasons,
    'authority_revision', p_authority,
    'substrate_fingerprint', p_fingerprint,
    'attempted_package_snapshot_digest', p_pkg,
    'attempted_closure_root', p_closure,
    'actor', p_actor
  )::text, 'UTF8')), 'hex')
$function$
```

## 2. MCF lifecycle guard functions (`mcf.fn_*`) — VERBATIM

### `mcf.fn_audit_cert_finalize`

Reads/writes: `mcf.metric_contract_version`, `new.to_state_code`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_audit_cert_finalize()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE v_state text;
BEGIN
  IF NEW.action_code NOT IN ('audit_admit','audit_block','audit_migrate') OR NEW.to_state_code IS NULL THEN RETURN NULL; END IF;
  IF NEW.primitive_type <> 'metric_contract_version' THEN RETURN NULL; END IF;
  SELECT governance_state_code INTO v_state FROM mcf.metric_contract_version WHERE metric_contract_version_uid = NEW.primitive_id;
  IF v_state IS DISTINCT FROM NEW.to_state_code THEN
    RAISE EXCEPTION 'orphan audit cert: MCV % is in state %, cert % requires to_state % by commit',
      NEW.primitive_id, v_state, NEW.action_code, NEW.to_state_code USING ERRCODE='check_violation'; END IF;
  RETURN NULL;
END $function$
```

### `mcf.fn_binding_entity_version_guard`

Reads/writes: `concept_registry.business_concept_version`, `concept_registry.entity_version`, `new.bound_business_concept_id`, `new.bound_entity_id`, `old.bound_entity_version_id`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_binding_entity_version_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE v_pin_entity uuid; v_bcv_concept uuid; v_bcv_found boolean;
BEGIN
  IF TG_OP='UPDATE' AND OLD.bound_entity_version_id IS NOT NULL
     AND NEW.bound_entity_version_id IS DISTINCT FROM OLD.bound_entity_version_id THEN
    RAISE EXCEPTION 'bound_entity_version_id is immutable once set' USING ERRCODE='check_violation'; END IF;
  -- a Business Concept Version cannot exist without a Business Concept id
  IF NEW.bound_business_concept_version_id IS NOT NULL AND NEW.bound_business_concept_id IS NULL THEN
    RAISE EXCEPTION 'bound_business_concept_version_id requires bound_business_concept_id (incomplete BC target)' USING ERRCODE='check_violation'; END IF;
  IF NEW.bound_business_concept_id IS NOT NULL THEN
    -- Business Concept target: require exact BC version; prohibit an entity-version pin
    IF NEW.bound_business_concept_version_id IS NULL THEN
      RAISE EXCEPTION 'business-concept-target binding requires bound_business_concept_version_id' USING ERRCODE='check_violation'; END IF;
    IF NEW.bound_entity_version_id IS NOT NULL THEN
      RAISE EXCEPTION 'business-concept-target binding must not carry bound_entity_version_id' USING ERRCODE='check_violation'; END IF;
    -- v4: the BC version must EXIST and BELONG to the bound Business Concept (fail-closed null-safe).
    -- The FK (§1) guarantees existence; this resolves lineage. If the row is absent, v_bcv_concept stays
    -- null and the null-safe compare below still refuses.
    SELECT concept_id, true INTO v_bcv_concept, v_bcv_found FROM concept_registry.business_concept_version
      WHERE concept_version_id = NEW.bound_business_concept_version_id;
    IF NOT COALESCE(v_bcv_found, false) THEN
      RAISE EXCEPTION 'bound_business_concept_version_id % does not exist', NEW.bound_business_concept_version_id USING ERRCODE='check_violation'; END IF;
    IF v_bcv_concept IS DISTINCT FROM NEW.bound_business_concept_id THEN
      RAISE EXCEPTION 'bound_business_concept_version_id % belongs to concept %, not bound_business_concept_id %', NEW.bound_business_concept_version_id, v_bcv_concept, NEW.bound_business_concept_id USING ERRCODE='check_violation'; END IF;
  ELSIF NEW.bound_entity_id IS NOT NULL THEN
    -- Entity-only target (no BC id, no BC version): require the matching entity version
    IF NEW.bound_entity_version_id IS NULL THEN
      RAISE EXCEPTION 'entity-target binding requires bound_entity_version_id' USING ERRCODE='check_violation'; END IF;
    SELECT entity_id INTO v_pin_entity FROM concept_registry.entity_version WHERE entity_version_id = NEW.bound_entity_version_id;
    IF v_pin_entity IS DISTINCT FROM NEW.bound_entity_id THEN
      RAISE EXCEPTION 'bound_entity_version_id % belongs to entity %, not bound_entity_id %', NEW.bound_entity_version_id, v_pin_entity, NEW.bound_entity_id USING ERRCODE='check_violation'; END IF;
  ELSE
    -- constant / metric-input (no BC id, no entity id): must not carry an entity-version pin
    IF NEW.bound_entity_version_id IS NOT NULL THEN
      RAISE EXCEPTION 'non-entity-target binding must not carry bound_entity_version_id' USING ERRCODE='check_violation'; END IF;
  END IF;
  RETURN NEW;
END $function$
```

### `mcf.fn_cae_insert_role_check`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_cae_insert_role_check()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  -- Only enforce when the role exists (so dev environments without role isolation
  -- can still insert from the application service role).
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'chain_auditor_readonly') THEN
    IF current_user <> 'chain_auditor_readonly' THEN
      -- Permissive fallback for dev: write a notice instead of raising.
      -- Production deployment should pin connection to chain_auditor_readonly and tighten this.
      RAISE NOTICE 'D445 CAS: chain_audit_evidence written by % (expected chain_auditor_readonly). Production tightening recommended.', current_user;
    END IF;
  END IF;
  RETURN NEW;
END;
$function$
```

### `mcf.fn_cert_legacy_tuple_freeze`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_cert_legacy_tuple_freeze()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN
  IF (NEW.action_code='metric_transition' AND NEW.from_state_code='approved' AND NEW.to_state_code='active')
     OR (NEW.action_code='metric_correction' AND NEW.from_state_code='superseded' AND NEW.to_state_code='active') THEN
    RAISE EXCEPTION 'cert tuple %/%->% is frozen (C4): activation routes through audit_pending; direct-to-active certs are historical only',
      NEW.action_code, NEW.from_state_code, NEW.to_state_code USING ERRCODE='check_violation';
  END IF;
  RETURN NEW;
END $function$
```

### `mcf.fn_exactness_reproof_append_only`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_exactness_reproof_append_only()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  RAISE EXCEPTION 'mcf.exactness_reproof_evidence is append-only (DEC-545a4d boundary 3): % refused', TG_OP;
END;
$function$
```

### `mcf.fn_feb_attestation_exact`

Reads/writes: `mcf.certification_record`, `new.metric_contract_version_uid`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_feb_attestation_exact()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE cr mcf.certification_record%ROWTYPE;
BEGIN
  SELECT * INTO cr FROM mcf.certification_record WHERE certification_record_id = NEW.attestation_cert_id;
  IF cr.certification_record_id IS NULL THEN
    RAISE EXCEPTION 'feb attestation cert % not found', NEW.attestation_cert_id USING ERRCODE='check_violation'; END IF;
  IF cr.primitive_type IS DISTINCT FROM 'metric_contract_version'
     OR cr.primitive_id IS DISTINCT FROM NEW.metric_contract_version_uid THEN
    RAISE EXCEPTION 'feb attestation cert % does not belong to MCV %', NEW.attestation_cert_id, NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
  IF NEW.attestation_kind = 'metric_approve' THEN
    IF cr.action_code IS DISTINCT FROM 'metric_approve' OR cr.from_state_code IS DISTINCT FROM 'review'
       OR cr.to_state_code IS DISTINCT FROM 'approved' THEN
      RAISE EXCEPTION 'feb attestation_kind=metric_approve requires cert tuple metric_approve(review->approved); got %(%->%)', cr.action_code, cr.from_state_code, cr.to_state_code USING ERRCODE='check_violation'; END IF;
  ELSIF NEW.attestation_kind = 'metric_transition_backfill' THEN
    -- unreachable in U1 (chk_feb_origin); tuple enforced now so U2's widening cannot skip it
    IF cr.action_code IS DISTINCT FROM 'metric_transition' OR cr.from_state_code IS DISTINCT FROM 'approved'
       OR cr.to_state_code IS DISTINCT FROM 'active' THEN
      RAISE EXCEPTION 'feb attestation_kind=metric_transition_backfill requires cert tuple metric_transition(approved->active); got %(%->%)', cr.action_code, cr.from_state_code, cr.to_state_code USING ERRCODE='check_violation'; END IF;
  END IF;
  IF cr.is_archived_after IS TRUE THEN
    RAISE EXCEPTION 'feb attestation cert % is archived — a live cert is required at binding creation', NEW.attestation_cert_id USING ERRCODE='check_violation'; END IF;
  RETURN NULL;
END $function$
```

### `mcf.fn_feb_immutable`

Reads/writes: `old.attestation_cert_id`, `old.attestation_kind`, `old.authored_intent_digest`, `old.authored_intent_json`, `old.backfill_run_uid`, `old.binding_digest`, `old.binding_uid`, `old.created_at`, `old.formula_ast_digest`, `old.formula_intent_hash`, `old.latest_revision_uid`, `old.metric_contract_version_uid`, `old.origin_kind`, `old.rendered_explanation_digest`, `old.rendered_explanation_text`, `old.renderer_version`, `old.revision_count_at_binding`, `old.supersedes_binding_uid`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_feb_immutable()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'mcf.formula_explanation_binding is append-only (DELETE rejected)' USING ERRCODE='check_violation'; END IF;
  IF NEW.binding_uid IS DISTINCT FROM OLD.binding_uid
     OR NEW.metric_contract_version_uid IS DISTINCT FROM OLD.metric_contract_version_uid
     OR NEW.formula_intent_hash IS DISTINCT FROM OLD.formula_intent_hash
     OR NEW.formula_ast_digest IS DISTINCT FROM OLD.formula_ast_digest
     OR NEW.authored_intent_json IS DISTINCT FROM OLD.authored_intent_json
     OR NEW.authored_intent_digest IS DISTINCT FROM OLD.authored_intent_digest
     OR NEW.rendered_explanation_text IS DISTINCT FROM OLD.rendered_explanation_text
     OR NEW.rendered_explanation_digest IS DISTINCT FROM OLD.rendered_explanation_digest
     OR NEW.renderer_version IS DISTINCT FROM OLD.renderer_version
     OR NEW.revision_count_at_binding IS DISTINCT FROM OLD.revision_count_at_binding
     OR NEW.latest_revision_uid IS DISTINCT FROM OLD.latest_revision_uid
     OR NEW.attestation_cert_id IS DISTINCT FROM OLD.attestation_cert_id
     OR NEW.attestation_kind IS DISTINCT FROM OLD.attestation_kind
     OR NEW.origin_kind IS DISTINCT FROM OLD.origin_kind
     OR NEW.backfill_run_uid IS DISTINCT FROM OLD.backfill_run_uid
     OR NEW.supersedes_binding_uid IS DISTINCT FROM OLD.supersedes_binding_uid
     OR NEW.binding_digest IS DISTINCT FROM OLD.binding_digest
     OR NEW.created_at IS DISTINCT FROM OLD.created_at THEN
    RAISE EXCEPTION 'mcf.formula_explanation_binding: only the archive flip may change (content is immutable)' USING ERRCODE='check_violation'; END IF;
  IF NOT (OLD.archived_at IS NULL AND NEW.archived_at IS NOT NULL) THEN
    RAISE EXCEPTION 'mcf.formula_explanation_binding.archived_at may only flip NULL -> set (one-way)' USING ERRCODE='check_violation'; END IF;
  NEW.archived_at := now();  -- DB-owned event time; caller-selected timestamps are discarded
  RETURN NEW;
END $function$
```

### `mcf.fn_feb_lineage`

Reads/writes: `mcf.formula_explanation_binding`, `new.metric_contract_version_uid`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_feb_lineage()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE pred mcf.formula_explanation_binding%ROWTYPE; n int;
BEGIN
  IF NEW.supersedes_binding_uid IS NULL THEN
    SELECT count(*) INTO n FROM mcf.formula_explanation_binding
      WHERE metric_contract_version_uid = NEW.metric_contract_version_uid AND binding_uid <> NEW.binding_uid;
    IF n > 0 THEN
      RAISE EXCEPTION 'feb: a successor binding for MCV % must cite supersedes_binding_uid (predecessors exist)', NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
    RETURN NULL;
  END IF;
  SELECT * INTO pred FROM mcf.formula_explanation_binding WHERE binding_uid = NEW.supersedes_binding_uid;
  IF pred.binding_uid IS NULL OR pred.metric_contract_version_uid IS DISTINCT FROM NEW.metric_contract_version_uid THEN
    RAISE EXCEPTION 'feb: supersedes_binding_uid % must cite a binding of the SAME MCV', NEW.supersedes_binding_uid USING ERRCODE='check_violation'; END IF;
  IF pred.archived_at IS NULL THEN
    RAISE EXCEPTION 'feb: cited predecessor % is still live — archive it in the same transaction first', NEW.supersedes_binding_uid USING ERRCODE='check_violation'; END IF;
  -- P1-5 immediate-predecessor identity: the cited row must be the CHAIN TAIL — no other row may already
  -- cite it (uq_feb_one_successor is the hard guarantee at insert; this deferred re-check yields the
  -- explicit refusal message and closes same-tx double-citation).
  SELECT count(*) INTO n FROM mcf.formula_explanation_binding
    WHERE supersedes_binding_uid = NEW.supersedes_binding_uid AND binding_uid <> NEW.binding_uid;
  IF n > 0 THEN
    RAISE EXCEPTION 'feb: predecessor % already has a successor — a successor must cite the IMMEDIATE predecessor (chain tail); skipped ancestors and forks are refused', NEW.supersedes_binding_uid USING ERRCODE='check_violation'; END IF;
  RETURN NULL;
END $function$
```

### `mcf.fn_mapt_immutability_check`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mapt_immutability_check()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  -- Per DBCP M5 §13.2 + D-M5-8 + MCF §11.3 + Invariant V:
  -- per-agent transcripts are immutable authoring records used by audit.
  -- UPDATE and DELETE are rejected unconditionally once the row exists.
  IF TG_OP = 'UPDATE' THEN
    RAISE EXCEPTION 'mcf.metric_authoring_panel_transcript transcript_uid=% is immutable; UPDATE rejected (per DBCP M5 §13 + Invariant V)', OLD.transcript_uid
      USING ERRCODE = 'check_violation';
  END IF;
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'mcf.metric_authoring_panel_transcript transcript_uid=% is immutable; DELETE rejected (per DBCP M5 §13 + Invariant V)', OLD.transcript_uid
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN NULL;
END;
$function$
```

### `mcf.fn_mc_active_immutability_check`

Reads/writes: `mcf.metric_contract_version`, `new.candidate_source_ref_json`, `new.filter_set_hash`, `new.formula_intent_hash`, `new.grain_entity_id`, `new.hash_algorithm_version`, `new.identity_tuple_hash`, `new.package_signature_hash`, `new.temporal_gate_params_json`, `new.temporal_gate_shape_code`, `new.variable_binding_set_hash`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mc_active_immutability_check()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
  frozen_count integer;
BEGIN
  -- frozen if any version is in a frozen state OR has an approval snapshot (bytes frozen).
  SELECT COUNT(*) INTO frozen_count
    FROM mcf.metric_contract_version
    WHERE metric_contract_uid = OLD.metric_contract_uid
      AND (governance_state_code IN ('approved', 'active', 'audit_pending', 'audit_blocked', 'superseded')
           OR mcf.fn_mcv_has_approval_snapshot(metric_contract_version_uid));
  IF frozen_count = 0 THEN RETURN NEW; END IF;
  IF (OLD.grain_entity_id           IS DISTINCT FROM NEW.grain_entity_id)           OR
     (OLD.formula_intent_hash       IS DISTINCT FROM NEW.formula_intent_hash)       OR
     (OLD.variable_binding_set_hash IS DISTINCT FROM NEW.variable_binding_set_hash) OR
     (OLD.filter_set_hash           IS DISTINCT FROM NEW.filter_set_hash)           OR
     (OLD.temporal_gate_shape_code  IS DISTINCT FROM NEW.temporal_gate_shape_code)  OR
     (OLD.temporal_gate_params_json IS DISTINCT FROM NEW.temporal_gate_params_json) OR
     (OLD.identity_tuple_hash       IS DISTINCT FROM NEW.identity_tuple_hash)       OR
     (OLD.package_signature_hash    IS DISTINCT FROM NEW.package_signature_hash)    OR
     (OLD.hash_algorithm_version    IS DISTINCT FROM NEW.hash_algorithm_version)    OR
     (OLD.candidate_source_ref_json IS DISTINCT FROM NEW.candidate_source_ref_json) THEN
    RAISE EXCEPTION 'mcf.metric_contract.% is frozen (past-draft/audit version or approval snapshot); identity-bearing columns are immutable', OLD.metric_contract_uid
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN NEW;
END;
$function$
```

### `mcf.fn_mc_grain_freeze_guard`

Reads/writes: `mcf.metric_contract_version`, `old.grain_entity_id`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mc_grain_freeze_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN
  IF NEW.grain_entity_id IS DISTINCT FROM OLD.grain_entity_id THEN
    PERFORM pg_advisory_xact_lock(1836416052, hashtext(OLD.metric_contract_uid::text));
    IF EXISTS (SELECT 1 FROM mcf.metric_contract_version v
               WHERE v.metric_contract_uid = OLD.metric_contract_uid AND v.grain_entity_version_id IS NOT NULL) THEN
      RAISE EXCEPTION 'metric_contract % grain_entity_id cannot change: a child MCV has a frozen grain_entity_version_id pin', OLD.metric_contract_uid USING ERRCODE='check_violation'; END IF;
  END IF;
  RETURN NEW;
END $function$
```

### `mcf.fn_mcdr_active_immutability_check`

Reads/writes: `mcf.metric_contract_version`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mcdr_active_immutability_check()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE parent_state text; ref_version_uid uuid;
BEGIN
  ref_version_uid := COALESCE(OLD.metric_contract_version_uid, NEW.metric_contract_version_uid);
  SELECT governance_state_code INTO parent_state FROM mcf.metric_contract_version WHERE metric_contract_version_uid = ref_version_uid;
  IF parent_state IN ('approved', 'active', 'audit_pending', 'audit_blocked', 'superseded')
     OR mcf.fn_mcv_has_approval_snapshot(ref_version_uid) THEN
    RAISE EXCEPTION 'mcf.metric_computed_dimension_ref is frozen (parent version % state % or approval snapshot)', ref_version_uid, parent_state
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN COALESCE(NEW, OLD);
END;
$function$
```

### `mcf.fn_mcv_descriptive_immutability_check`

Reads/writes: `new.description_text`, `new.formula_ast_canonical_json`, `new.function_code`, `new.governance_state_code`, `new.metric_contract_uid`, `new.owner_json`, `new.subfunction_code`, `new.supersedes_version_uid`, `new.tags`, `new.threshold_json`, `new.version_code`, `new.version_seq`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mcv_descriptive_immutability_check()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  -- IF #1 — Permit pure state-only UPDATEs.
  -- M7/M8 amendment: formula_ast_canonical_json added to the enumerated set
  -- so changes to it AT THE SAME TIME as a state transition are NOT treated
  -- as "pure state-only" — they get rejected by the third IF below.
  IF OLD.governance_state_code IS DISTINCT FROM NEW.governance_state_code AND
     OLD.metric_contract_uid           IS NOT DISTINCT FROM NEW.metric_contract_uid           AND
     OLD.version_code                  IS NOT DISTINCT FROM NEW.version_code                  AND
     OLD.version_seq                   IS NOT DISTINCT FROM NEW.version_seq                   AND
     OLD.description_text              IS NOT DISTINCT FROM NEW.description_text              AND
     OLD.function_code                 IS NOT DISTINCT FROM NEW.function_code                 AND
     OLD.subfunction_code              IS NOT DISTINCT FROM NEW.subfunction_code              AND
     OLD.owner_json                    IS NOT DISTINCT FROM NEW.owner_json                    AND
     OLD.tags                          IS NOT DISTINCT FROM NEW.tags                          AND
     OLD.threshold_json                IS NOT DISTINCT FROM NEW.threshold_json                AND
     OLD.supersedes_version_uid        IS NOT DISTINCT FROM NEW.supersedes_version_uid        AND
     OLD.formula_ast_canonical_json    IS NOT DISTINCT FROM NEW.formula_ast_canonical_json    THEN
    -- Pure state-only UPDATE — state-transition trigger handles it.
    -- is_current may change too as a side effect; permit it.
    RETURN NEW;
  END IF;
  -- IF #2 — Reject all non-state mutations on approved/superseded rows.
  IF OLD.governance_state_code IN ('approved', 'superseded') THEN
    RAISE EXCEPTION 'mcf.metric_contract_version % is in state % — no non-state mutations permitted (Q1: approved is locked; superseded is terminal; per M3 DBCP + M7/M8 DBCP §13.2.1)', OLD.metric_contract_version_uid, OLD.governance_state_code
      USING ERRCODE = 'check_violation';
  END IF;
  -- IF #3 — Reject identity-bearing AST mutation at review state OR in mixed state+AST UPDATEs.
  -- Per MCF §4.6: identity-bearing changes are supersession territory; they
  -- cannot be mixed with state transitions or applied at review.
  IF (OLD.governance_state_code = 'review' AND
      OLD.formula_ast_canonical_json IS DISTINCT FROM NEW.formula_ast_canonical_json) OR
     (OLD.governance_state_code IS DISTINCT FROM NEW.governance_state_code AND
      OLD.formula_ast_canonical_json IS DISTINCT FROM NEW.formula_ast_canonical_json) THEN
    RAISE EXCEPTION 'mcf.metric_contract_version %: formula_ast_canonical_json is identity-bearing and cannot change at state=% nor in the same UPDATE as a state transition (per MCF §4.6; M7/M8 DBCP §13.2.1). Use supersession.', OLD.metric_contract_version_uid, OLD.governance_state_code
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN NEW;
END;
$function$
```

### `mcf.fn_mcv_grain_entity_version_guard`

Reads/writes: `concept_registry.entity_version`, `mcf.metric_contract`, `new.grain_entity_version_id`, `old.grain_entity_version_id`, `old.metric_contract_uid`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mcv_grain_entity_version_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE v_grain_entity uuid; v_pin_entity uuid; v_setting boolean;
BEGIN
  v_setting := (NEW.grain_entity_version_id IS NOT NULL)
    AND (TG_OP = 'INSERT' OR OLD.grain_entity_version_id IS DISTINCT FROM NEW.grain_entity_version_id);
  IF v_setting THEN PERFORM pg_advisory_xact_lock(1836416052, hashtext(NEW.metric_contract_uid::text)); END IF;
  IF TG_OP = 'UPDATE' AND OLD.grain_entity_version_id IS NOT NULL
     AND NEW.grain_entity_version_id IS DISTINCT FROM OLD.grain_entity_version_id THEN
    RAISE EXCEPTION 'grain_entity_version_id is immutable once set (mcv %)', OLD.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
  -- P0-2 v3: once pinned, the parent coordinate is frozen. Reparenting a pinned MCV is the only path
  -- that changes the (metric_contract_uid, grain_entity_version_id) identity pair without re-entering
  -- the pin-set lock; freezing metric_contract_uid closes it more faithfully than locking the reparent.
  IF TG_OP = 'UPDATE' AND OLD.grain_entity_version_id IS NOT NULL
     AND NEW.metric_contract_uid IS DISTINCT FROM OLD.metric_contract_uid THEN
    RAISE EXCEPTION 'metric_contract_uid is immutable once the MCV grain is pinned (mcv %)', OLD.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
  IF (TG_OP='INSERT' OR OLD.grain_entity_version_id IS NULL) AND NEW.grain_entity_version_id IS NOT NULL
     AND NEW.governance_state_code NOT IN ('draft','review') THEN
    RAISE EXCEPTION 'grain_entity_version_id cannot be set on a %-state MCV; author a successor (mcv %)',
      NEW.governance_state_code, NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
  IF TG_OP='UPDATE' AND OLD.governance_state_code='review' AND NEW.governance_state_code='approved'
     AND NEW.grain_entity_version_id IS NULL THEN
    RAISE EXCEPTION 'review->approved requires a grain_entity_version_id pin (mcv %)', NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
  IF NEW.grain_entity_version_id IS NOT NULL THEN
    SELECT grain_entity_id INTO v_grain_entity FROM mcf.metric_contract WHERE metric_contract_uid = NEW.metric_contract_uid;
    SELECT entity_id INTO v_pin_entity FROM concept_registry.entity_version WHERE entity_version_id = NEW.grain_entity_version_id;
    IF v_pin_entity IS DISTINCT FROM v_grain_entity THEN
      RAISE EXCEPTION 'grain_entity_version_id % belongs to entity %, not the MC grain entity % (mcv %)',
        NEW.grain_entity_version_id, v_pin_entity, v_grain_entity, NEW.metric_contract_version_uid USING ERRCODE='check_violation'; END IF;
  END IF;
  RETURN NEW;
END $function$
```

### `mcf.fn_mcv_has_approval_snapshot`

Reads/writes: `mcf.mcv_package_snapshot`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mcv_has_approval_snapshot(p_mcv uuid)
 RETURNS boolean
 LANGUAGE sql
 STABLE
AS $function$
  SELECT EXISTS (SELECT 1 FROM mcf.mcv_package_snapshot
    WHERE metric_contract_version_uid = p_mcv AND disposition_source = 'approval')
$function$
```

### `mcf.fn_mcv_noncomputable_reasons_ok`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mcv_noncomputable_reasons_ok(p text[])
 RETURNS boolean
 LANGUAGE sql
 IMMUTABLE
 SET search_path TO 'pg_catalog'
AS $function$
  SELECT p IS NOT NULL
     AND array_length(p, 1) >= 1
     AND p <@ ARRAY['binding_missing_bc_version','binding_missing_entity_version','binding_targets_both_bc_and_entity',
                    'filter_bc_version_missing','having_clause_unexecutable','null_grain_entity_version',
                    'temporal_anchor_unreferenced']::text[]
     AND p = (SELECT array_agg(DISTINCT x ORDER BY x) FROM unnest(p) AS x)
$function$
```

### `mcf.fn_mcv_package_identity_immutability_check`

Reads/writes: `new.aggregation_currency_code`, `new.formula_ast_canonical_json`, `new.grain_entity_version_id`, `new.threshold_json`, `new.version_code`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mcv_package_identity_immutability_check()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  IF (OLD.governance_state_code IN ('approved', 'active', 'audit_pending', 'audit_blocked', 'superseded')
      OR NEW.governance_state_code IN ('approved', 'active', 'audit_pending', 'audit_blocked', 'superseded')
      OR mcf.fn_mcv_has_approval_snapshot(OLD.metric_contract_version_uid)) AND (
       (OLD.formula_ast_canonical_json IS DISTINCT FROM NEW.formula_ast_canonical_json) OR
       (OLD.threshold_json             IS DISTINCT FROM NEW.threshold_json)             OR
       (OLD.aggregation_currency_code  IS DISTINCT FROM NEW.aggregation_currency_code)  OR
       (OLD.grain_entity_version_id    IS DISTINCT FROM NEW.grain_entity_version_id)    OR
       (OLD.version_code               IS DISTINCT FROM NEW.version_code)) THEN
    RAISE EXCEPTION 'mcf.metric_contract_version % is frozen (state %/% or approval snapshot) — package-bearing columns are immutable', OLD.metric_contract_version_uid, OLD.governance_state_code, NEW.governance_state_code
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN NEW;
END;
$function$
```

### `mcf.fn_mcv_package_snapshot_guard`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mcv_package_snapshot_guard()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE p jsonb; v_keys text[];
BEGIN
  NEW.computed_at := now();  -- DB-owned event time, not caller-forgeable
  IF NEW.disposition_code = 'computed' THEN
    IF NEW.package_signature_hash <> 'sha256:' || encode(sha256(NEW.canonical_package_bytes), 'hex') THEN
      RAISE EXCEPTION 'mcv_package_snapshot: package_signature_hash != sha256(canonical_package_bytes)'
        USING ERRCODE='check_violation'; END IF;
    p := convert_from(NEW.canonical_package_bytes, 'UTF8')::jsonb;  -- raises on non-JSON bytes
    -- (P1-1a) the payload must be a JSON object with EXACTLY the 23 mcf-package-v3 top-level members
    IF jsonb_typeof(p) IS DISTINCT FROM 'object' THEN
      RAISE EXCEPTION 'mcv_package_snapshot: canonical_package_bytes is not a JSON object'
        USING ERRCODE='check_violation'; END IF;
    v_keys := (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(p) AS k);
    IF v_keys IS DISTINCT FROM ARRAY[
         'aggregation_currency_code','bindings_digest','computed_dimensions_digest','eval_policy_rulebook_digest',
         'eval_policy_rulebook_version','exactness_algorithm_version','exactness_ast_hash','exactness_result',
         'execution_engine_version','filters_digest','formula_ast_hash','grain_entity_id','grain_entity_version_id',
         'hash_algorithm_version','input_domain_digest','metric_contract_uid','metric_contract_version_uid',
         'numeric_representation_version','output_digest','resolved_policy_digest','temporal_gate_digest',
         'thresholds_digest','version_code']::text[] THEN
      RAISE EXCEPTION 'mcv_package_snapshot: canonical_package_bytes top-level keys are not the exact mcf-package-v3 23-member set (extra/missing/noncanonical key)'
        USING ERRCODE='check_violation'; END IF;
    -- (P1-1b) governed algorithm vocabulary
    IF p->>'hash_algorithm_version' IS DISTINCT FROM 'mcf-package-v3' THEN
      RAISE EXCEPTION 'mcv_package_snapshot: hash_algorithm_version must be the governed ''mcf-package-v3'' vocabulary'
        USING ERRCODE='check_violation'; END IF;
    IF NEW.hash_algorithm_version        IS DISTINCT FROM  p->>'hash_algorithm_version'
       OR NEW.metric_contract_version_uid IS DISTINCT FROM (p->>'metric_contract_version_uid')::uuid
       OR NEW.metric_contract_uid         IS DISTINCT FROM (p->>'metric_contract_uid')::uuid
       OR NEW.version_code                IS DISTINCT FROM  p->>'version_code'
       OR NEW.formula_ast_hash            IS DISTINCT FROM  p->>'formula_ast_hash'
       OR NEW.bindings_digest             IS DISTINCT FROM  p->>'bindings_digest'
       OR NEW.filters_digest              IS DISTINCT FROM  p->>'filters_digest'
       OR NEW.computed_dimensions_digest  IS DISTINCT FROM  p->>'computed_dimensions_digest'
       OR NEW.temporal_gate_digest        IS DISTINCT FROM  p->>'temporal_gate_digest'
       OR NEW.grain_entity_id             IS DISTINCT FROM (p->>'grain_entity_id')::uuid
       OR NEW.grain_entity_version_id     IS DISTINCT FROM (p->>'grain_entity_version_id')::uuid
       OR NEW.output_digest               IS DISTINCT FROM  p->>'output_digest'
       OR NEW.aggregation_currency_code   IS DISTINCT FROM  p->>'aggregation_currency_code'
       OR NEW.thresholds_digest           IS DISTINCT FROM  p->>'thresholds_digest'
       OR NEW.input_domain_digest         IS DISTINCT FROM  p->>'input_domain_digest'
       OR NEW.resolved_policy_digest      IS DISTINCT FROM  p->>'resolved_policy_digest'
       OR NEW.eval_policy_rulebook_version IS DISTINCT FROM p->>'eval_policy_rulebook_version'
       OR NEW.eval_policy_rulebook_digest  IS DISTINCT FROM p->>'eval_policy_rulebook_digest'
       OR NEW.execution_engine_version    IS DISTINCT FROM  p->>'execution_engine_version'
       OR NEW.numeric_representation_version IS DISTINCT FROM p->>'numeric_representation_version'
       OR NEW.exactness_result            IS DISTINCT FROM  p->>'exactness_result'
       OR NEW.exactness_algorithm_version IS DISTINCT FROM  p->>'exactness_algorithm_version'
       OR NEW.exactness_ast_hash          IS DISTINCT FROM  p->>'exactness_ast_hash' THEN
      RAISE EXCEPTION 'mcv_package_snapshot: a typed identity column diverges from the canonical package bytes'
        USING ERRCODE='check_violation'; END IF;
    -- binary64 eligibility is derived, never asserted independently
    IF NEW.binary64_activation_eligible IS DISTINCT FROM (NEW.exactness_result = 'EXACT') THEN
      RAISE EXCEPTION 'mcv_package_snapshot: binary64_activation_eligible must equal (exactness_result = ''EXACT'')'
        USING ERRCODE='check_violation'; END IF;
  END IF;
  RETURN NEW;
END $function$
```

### `mcf.fn_mcv_package_snapshot_immutability`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mcv_package_snapshot_immutability()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
BEGIN
  RAISE EXCEPTION 'mcf.mcv_package_snapshot is immutable (% refused, Invariant III)', TG_OP USING ERRCODE='check_violation';
END $function$
```

### `mcf.fn_mcv_revision_emit`

Reads/writes: `mcf.metric_contract_revision`, `new.description_text`, `new.function_code`, `new.owner_json`, `new.subfunction_code`, `new.tags`, `new.threshold_json`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mcv_revision_emit()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
  next_seq integer;
  changed_fields jsonb := '{}'::jsonb;
  kinds text[] := ARRAY[]::text[];
  revision_kind text;
BEGIN
  IF OLD.governance_state_code <> 'active' THEN
    RETURN NEW;
  END IF;
  IF OLD.description_text IS DISTINCT FROM NEW.description_text THEN
    changed_fields := changed_fields || jsonb_build_object('description_text',
      jsonb_build_object('from', OLD.description_text, 'to', NEW.description_text));
    kinds := kinds || 'description_change'::text;
  END IF;
  IF OLD.function_code IS DISTINCT FROM NEW.function_code THEN
    changed_fields := changed_fields || jsonb_build_object('function_code',
      jsonb_build_object('from', OLD.function_code, 'to', NEW.function_code));
    kinds := kinds || 'function_code_change'::text;
  END IF;
  IF OLD.subfunction_code IS DISTINCT FROM NEW.subfunction_code THEN
    changed_fields := changed_fields || jsonb_build_object('subfunction_code',
      jsonb_build_object('from', OLD.subfunction_code, 'to', NEW.subfunction_code));
    kinds := kinds || 'function_code_change'::text;  -- subfunction maps to same revision kind
  END IF;
  IF OLD.owner_json IS DISTINCT FROM NEW.owner_json THEN
    changed_fields := changed_fields || jsonb_build_object('owner_json',
      jsonb_build_object('from', OLD.owner_json, 'to', NEW.owner_json));
    kinds := kinds || 'owner_change'::text;
  END IF;
  IF OLD.tags IS DISTINCT FROM NEW.tags THEN
    changed_fields := changed_fields || jsonb_build_object('tags',
      jsonb_build_object('from', to_jsonb(OLD.tags), 'to', to_jsonb(NEW.tags)));
    kinds := kinds || 'tags_change'::text;
  END IF;
  IF OLD.threshold_json IS DISTINCT FROM NEW.threshold_json THEN
    changed_fields := changed_fields || jsonb_build_object('threshold_json',
      jsonb_build_object('from', OLD.threshold_json, 'to', NEW.threshold_json));
    kinds := kinds || 'threshold_change'::text;
  END IF;
  IF changed_fields = '{}'::jsonb THEN
    RETURN NEW;  -- no descriptive change; no revision row
  END IF;
  IF (SELECT COUNT(DISTINCT k) FROM unnest(kinds) k) = 1 THEN
    revision_kind := kinds[1];
  ELSE
    revision_kind := 'other';
  END IF;
  SELECT COALESCE(MAX(revision_seq), 0) + 1 INTO next_seq
    FROM mcf.metric_contract_revision
    WHERE metric_contract_version_uid = NEW.metric_contract_version_uid;
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
$function$
```

### `mcf.fn_mcv_state_transition_check`

Reads/writes: `mcf.certification_record`, `mcf.mcv_package_snapshot`, `mcf.metric_contract`, `mcf.metric_contract_version`, `mcf.metric_supersession`, `metric_audit.reintake_accepted_manifest`, `metric_audit.reintake_accepted_member`, `metric_audit.reintake_batch`, `metric_audit.reintake_batch_cohort`, `metric_audit.reintake_batch_member`

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

### `mcf.fn_mfc_active_immutability_check`

Reads/writes: `mcf.metric_contract_version`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mfc_active_immutability_check()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE parent_state text; ref_version_uid uuid;
BEGIN
  ref_version_uid := COALESCE(OLD.metric_contract_version_uid, NEW.metric_contract_version_uid);
  SELECT governance_state_code INTO parent_state FROM mcf.metric_contract_version WHERE metric_contract_version_uid = ref_version_uid;
  IF parent_state IN ('approved', 'active', 'audit_pending', 'audit_blocked', 'superseded')
     OR mcf.fn_mcv_has_approval_snapshot(ref_version_uid) THEN
    RAISE EXCEPTION 'mcf.metric_filter_clause is frozen (parent version % state % or approval snapshot)', ref_version_uid, parent_state
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN COALESCE(NEW, OLD);
END;
$function$
```

### `mcf.fn_msvf_immutability_check`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_msvf_immutability_check()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  -- Per DBCP M9 §8 + MCF §12.9 + Invariant III + operator design constraint:
  -- self-verification fixtures are immutable authoring records used by audit
  -- and by the M10 verifier as the operator-asserted source-of-truth for the
  -- expected-output assertion. UPDATE and DELETE are rejected unconditionally
  -- once the row exists.
  IF TG_OP = 'UPDATE' THEN
    RAISE EXCEPTION 'mcf.metric_self_verification_fixture fixture_uid=% is immutable; UPDATE rejected (per DBCP M9 §8 + Invariant III)', OLD.fixture_uid
      USING ERRCODE = 'check_violation';
  END IF;
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'mcf.metric_self_verification_fixture fixture_uid=% is immutable; DELETE rejected (per DBCP M9 §8 + Invariant III)', OLD.fixture_uid
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN NULL;
END;
$function$
```

### `mcf.fn_msvr_immutability_check`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_msvr_immutability_check()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  -- Per DBCP M10 §11 + D-M10-9 + MCF §17.1 + Invariant V:
  -- self-verification result rows are immutable post-INSERT. The append-only
  -- ledger discipline is evidence-grade — UPDATE/DELETE attempts indicate
  -- either a service bug (verifier shouldn't ever rewrite a result) or
  -- malicious tampering with historical verdicts. Both rejected
  -- unconditionally.
  IF TG_OP = 'UPDATE' THEN
    RAISE EXCEPTION 'mcf.metric_self_verification_result verification_result_uid=% is immutable; UPDATE rejected (per DBCP M10 §11 + Invariant V)', OLD.verification_result_uid
      USING ERRCODE = 'check_violation';
  END IF;
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'mcf.metric_self_verification_result verification_result_uid=% is immutable; DELETE rejected (per DBCP M10 §11 + Invariant V)', OLD.verification_result_uid
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN NULL;
END;
$function$
```

### `mcf.fn_mvb_active_immutability_check`

Reads/writes: `mcf.metric_contract_version`

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mvb_active_immutability_check()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE parent_state text; ref_version_uid uuid;
BEGIN
  ref_version_uid := COALESCE(OLD.metric_contract_version_uid, NEW.metric_contract_version_uid);
  SELECT governance_state_code INTO parent_state FROM mcf.metric_contract_version WHERE metric_contract_version_uid = ref_version_uid;
  IF parent_state IN ('approved', 'active', 'audit_pending', 'audit_blocked', 'superseded')
     OR mcf.fn_mcv_has_approval_snapshot(ref_version_uid) THEN
    RAISE EXCEPTION 'mcf.metric_variable_binding is frozen (parent version % state % or approval snapshot)', ref_version_uid, parent_state
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN COALESCE(NEW, OLD);
END;
$function$
```

## 3. Platform substrate constraints — `metric_audit` (every column nullability, FK, CHECK, trigger)

### `metric_audit._m39_role_ledger`

Columns: 3 | **NOT NULL:** `role_name`, `created_by_m39`, `metric_audit_usage_preexisting`

| Kind | Name | Definition |
|---|---|---|
| PK | `_m39_role_ledger_pkey` | `PRIMARY KEY (role_name)` |

### `metric_audit._m40_role_ledger`

Columns: 3 | **NOT NULL:** `role_name`, `created_by_m40`, `metric_audit_usage_preexisting`

| Kind | Name | Definition |
|---|---|---|
| PK | `_m40_role_ledger_pkey` | `PRIMARY KEY (role_name)` |

### `metric_audit.admission_recomputation_evidence`

Columns: 12 | **NOT NULL:** `evidence_uid`, `metric_contract_version_uid`, `effective_decision_uid`, `request_uid`, `expected_snapshot_signature_hash`, `recomputed_package_signature_hash`, `recomputed_closure_root`, `recompute_txid`, `recomputed_at`, `actor`, `evidence_digest`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `admission_recomputation_evid_expected_snapshot_signature__check` | `CHECK ((expected_snapshot_signature_hash ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `admission_recomputation_evid_recomputed_package_signature_check` | `CHECK ((recomputed_package_signature_hash ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `admission_recomputation_evidence_evidence_digest_check` | `CHECK ((evidence_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `admission_recomputation_evidence_recomputed_closure_root_check` | `CHECK ((recomputed_closure_root ~ '^sha256:[a-f0-9]{64}$'::text))` |
| FK | `admission_recomputation_eviden_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| FK | `admission_recomputation_evidence_effective_decision_uid_fkey` | `FOREIGN KEY (effective_decision_uid) REFERENCES metric_audit.decision(decision_uid)` |
| FK | `admission_recomputation_evidence_supersedes_evidence_uid_fkey` | `FOREIGN KEY (supersedes_evidence_uid) REFERENCES metric_audit.admission_recomputation_evidence(evidence_uid)` |
| PK | `admission_recomputation_evidence_pkey` | `PRIMARY KEY (evidence_uid)` |

Triggers:

- `trg_admission_evidence_guard`: `trg_admission_evidence_guard BEFORE INSERT ON metric_audit.admission_recomputation_evidence FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_admission_evidence_guard()`
- `trg_admission_evidence_immutable`: `trg_admission_evidence_immutable BEFORE DELETE OR UPDATE ON metric_audit.admission_recomputation_evidence FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_admission_evidence_immutability()`

### `metric_audit.artifact_import`

Columns: 14 | **NOT NULL:** `import_uid`, `schema_version`, `exception_version_uid`, `metric_contract_version_uid`, `package_signature_hash`, `exception_class`, `issued_at`, `payload_bytes`, `payload_digest`, `signer_key_id`, `signature_b64`, `verified_at`, `verification_detail_json`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `auditor_artifact_import_exception_class_check` | `CHECK ((exception_class = ANY (ARRAY['OFF_POOL'::text, 'LEGACY'::text])))` |
| CHECK | `auditor_artifact_import_package_signature_hash_check` | `CHECK ((package_signature_hash ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `auditor_artifact_import_schema_version_check` | `CHECK ((schema_version = 'bc-off-pool-exception-v1'::text))` |
| FK | `auditor_artifact_import_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| FK | `auditor_artifact_import_signer_key_id_fkey` | `FOREIGN KEY (signer_key_id) REFERENCES metric_audit.signer_key(key_id)` |
| PK | `auditor_artifact_import_pkey` | `PRIMARY KEY (import_uid)` |
| UNIQUE | `uq_import_exception` | `UNIQUE (exception_version_uid)` |

Triggers:

- `trg_artifact_import`: `trg_artifact_import BEFORE INSERT ON metric_audit.artifact_import FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_artifact_import_guard()`
- `trg_auditor_artifact_import_immutable`: `trg_auditor_artifact_import_immutable BEFORE DELETE OR UPDATE ON metric_audit.artifact_import FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.decision`

Columns: 40 | **NOT NULL:** `decision_uid`, `feed_event_uid`, `decision_payload_digest`, `decision_digest`, `metric_contract_version_uid`, `metric_contract_uid`, `version_code`, `decision_code`, `feed_mode`, `request_uid`, `request_digest`, `package_hash_algorithm`, `package_snapshot_digest`, `closure_root`, `authority_revision`, `methodology_version`, `methodology_digest`, `gate_policy_version`, `engine`, `engine_version`, `source_authority_revision`, `source_authority_policy_digest`, `citations_json`, `decided_by`, `decided_at`, `created_at`, `exactness_basis`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_decision_basis_result_coherent` | `CHECK (((exactness_result IS NULL) OR ((exactness_basis = ANY (ARRAY['EXACT_SNAPSHOT'::text, 'EXACT_REPROOF'::text])) AND (exactness_result = ANY (ARRAY['EXACT'::text, 'NOT_PROVEN'::text]))) OR ((exactness_basis = 'REPRODUCIBLE'::text) AND (exactness_result = ANY (ARRAY['REPRODUCIBLE'::text, 'NOT_PROVEN'::text])))))` |
| CHECK | `chk_decision_exactness_basis` | `CHECK ((exactness_basis = ANY (ARRAY['EXACT_SNAPSHOT'::text, 'EXACT_REPROOF'::text, 'REPRODUCIBLE'::text])))` |
| CHECK | `chk_decision_report_by_code` | `CHECK ((((decision_code = 'REVOKE'::text) AND (report_uid IS NULL) AND (report_digest IS NULL) AND (structural_verdict IS NULL) AND (foundation_verdict IS NULL) AND (exactness_result IS NULL) AND (contextual_overall_score IS NULL) AND (contextual_decision IS NULL) AND (semantic_conformance_verdict IS NULL)) OR ((decision_code = ANY (ARRAY['PASS'::text, 'REJECT'::text])) AND (report_uid IS NOT NULL) AND (report_digest IS NOT NULL) AND (structural_verdict IS NOT NULL) AND (foundation_verdict IS NOT NULL) AND (exactness_result IS NOT NULL) AND (contextual_definition_score IS NOT NULL) AND (contextual_formula_score IS NOT NULL) AND (contextual_input_semantics_score IS NOT NULL) AND (contextual_overall_score IS NOT NULL) AND (contextual_decision IS NOT NULL) AND (semantic_conformance_verdict IS NOT NULL))))` |
| CHECK | `chk_decision_revoke_xor` | `CHECK (((decision_code = 'REVOKE'::text) = (revocation_json IS NOT NULL)))` |
| CHECK | `decision_closure_root_check` | `CHECK ((closure_root ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `decision_contextual_decision_check` | `CHECK ((contextual_decision = ANY (ARRAY['VERIFIED'::text, 'HIGH_CONFIDENCE'::text, 'CONDITIONAL'::text, 'REJECT'::text])))` |
| CHECK | `decision_contextual_definition_score_check` | `CHECK (((contextual_definition_score >= 1) AND (contextual_definition_score <= 5)))` |
| CHECK | `decision_contextual_formula_score_check` | `CHECK (((contextual_formula_score >= 1) AND (contextual_formula_score <= 5)))` |
| CHECK | `decision_contextual_input_semantics_score_check` | `CHECK (((contextual_input_semantics_score >= 1) AND (contextual_input_semantics_score <= 5)))` |
| CHECK | `decision_contextual_overall_score_check` | `CHECK (((contextual_overall_score >= 1) AND (contextual_overall_score <= 5)))` |
| CHECK | `decision_decision_code_check` | `CHECK ((decision_code = ANY (ARRAY['PASS'::text, 'REJECT'::text, 'REVOKE'::text])))` |
| CHECK | `decision_decision_digest_check` | `CHECK ((decision_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `decision_decision_payload_digest_check` | `CHECK ((decision_payload_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `decision_exactness_result_check` | `CHECK ((exactness_result = ANY (ARRAY['EXACT'::text, 'NOT_PROVEN'::text, 'REPRODUCIBLE'::text])))` |
| CHECK | `decision_feed_mode_check` | `CHECK ((feed_mode = ANY (ARRAY['shadow'::text, 'enforcement'::text])))` |
| CHECK | `decision_foundation_verdict_check` | `CHECK ((foundation_verdict = ANY (ARRAY['PASS'::text, 'REJECT'::text])))` |
| CHECK | `decision_methodology_digest_check` | `CHECK ((methodology_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `decision_package_hash_algorithm_check` | `CHECK ((package_hash_algorithm = 'mcf-package-v3'::text))` |
| CHECK | `decision_package_snapshot_digest_check` | `CHECK ((package_snapshot_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `decision_report_digest_check` | `CHECK ((report_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `decision_request_digest_check` | `CHECK ((request_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `decision_semantic_conformance_verdict_check` | `CHECK ((semantic_conformance_verdict = ANY (ARRAY['PASS'::text, 'REJECT'::text, 'NOT_APPLICABLE'::text])))` |
| CHECK | `decision_source_authority_policy_digest_check` | `CHECK ((source_authority_policy_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `decision_structural_verdict_check` | `CHECK ((structural_verdict = ANY (ARRAY['PASS'::text, 'REJECT'::text])))` |
| CHECK | `decision_version_code_check` | `CHECK ((version_code ~ '^v[0-9]+$'::text))` |
| FK | `decision_feed_event_uid_fkey` | `FOREIGN KEY (feed_event_uid) REFERENCES metric_audit.feed_event(event_uid)` |
| FK | `decision_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| FK | `decision_report_uid_fkey` | `FOREIGN KEY (report_uid) REFERENCES metric_audit.report_reference(report_uid)` |
| FK | `decision_request_uid_fkey` | `FOREIGN KEY (request_uid) REFERENCES metric_audit.request_publication(request_uid)` |
| FK | `decision_supersedes_decision_uid_fkey` | `FOREIGN KEY (supersedes_decision_uid) REFERENCES metric_audit.decision(decision_uid)` |
| PK | `decision_pkey` | `PRIMARY KEY (decision_uid)` |
| t | `trg_c6_deferred_revoke` | `TRIGGER DEFERRABLE INITIALLY DEFERRED` |
| t | `trg_decision_finalize` | `TRIGGER DEFERRABLE INITIALLY DEFERRED` |
| UNIQUE | `decision_decision_digest_key` | `UNIQUE (decision_digest)` |
| UNIQUE | `decision_feed_event_uid_key` | `UNIQUE (feed_event_uid)` |
| UNIQUE | `decision_supersedes_decision_uid_key` | `UNIQUE (supersedes_decision_uid)` |

Triggers:

- `trg_c6_deferred_revoke`: `CREATE CONSTRAINT TRIGGER trg_c6_deferred_revoke AFTER INSERT ON metric_audit.decision DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_c6_deferred_revoke()`
- `trg_decision_finalize`: `CREATE CONSTRAINT TRIGGER trg_decision_finalize AFTER INSERT ON metric_audit.decision DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_decision_finalize()`
- `trg_decision_guard`: `trg_decision_guard BEFORE INSERT ON metric_audit.decision FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_decision_guard()`
- `trg_decision_immutable`: `trg_decision_immutable BEFORE DELETE OR UPDATE ON metric_audit.decision FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.decision_nc_reference`

Columns: 6 | **NOT NULL:** `decision_uid`, `nc_uid`, `nc_digest`, `severity`, `is_blocking`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_decision_nc_blocking_derivation` | `CHECK ((is_blocking = (severity = ANY (ARRAY['CRITICAL'::text, 'MAJOR'::text]))))` |
| CHECK | `decision_nc_reference_nc_digest_check` | `CHECK ((nc_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `decision_nc_reference_severity_check` | `CHECK ((severity = ANY (ARRAY['CRITICAL'::text, 'MAJOR'::text, 'MINOR'::text])))` |
| FK | `decision_nc_reference_decision_uid_fkey` | `FOREIGN KEY (decision_uid) REFERENCES metric_audit.decision(decision_uid)` |
| FK | `decision_nc_reference_nc_uid_fkey` | `FOREIGN KEY (nc_uid) REFERENCES metric_audit.nc_reference(nc_uid)` |
| PK | `pk_decision_nc_reference` | `PRIMARY KEY (decision_uid, nc_uid)` |
| t | `trg_c6_deferred_blocking_nc` | `TRIGGER DEFERRABLE INITIALLY DEFERRED` |

Triggers:

- `trg_c6_deferred_blocking_nc`: `CREATE CONSTRAINT TRIGGER trg_c6_deferred_blocking_nc AFTER INSERT ON metric_audit.decision_nc_reference DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_c6_deferred_blocking_nc()`
- `trg_decision_nc_reference_immutable`: `trg_decision_nc_reference_immutable BEFORE DELETE OR UPDATE ON metric_audit.decision_nc_reference FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`
- `trg_decision_nc_reference_membership`: `trg_decision_nc_reference_membership BEFORE INSERT ON metric_audit.decision_nc_reference FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_decision_nc_reference_membership()`

### `metric_audit.feed_checkpoint`

Columns: 5 | **NOT NULL:** `feed_name`, `last_verified_sequence`, `last_event_digest`, `heartbeat_at`, `updated_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `feed_checkpoint_last_event_digest_check` | `CHECK ((last_event_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| PK | `feed_checkpoint_pkey` | `PRIMARY KEY (feed_name)` |

Triggers:

- `trg_feed_checkpoint_guard`: `trg_feed_checkpoint_guard BEFORE INSERT OR UPDATE ON metric_audit.feed_checkpoint FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_feed_checkpoint_guard()`

### `metric_audit.feed_event`

Columns: 16 | **NOT NULL:** `event_uid`, `feed_name`, `feed_sequence`, `feed_mode`, `payload_schema_version`, `event_kind`, `canonical_payload`, `payload_digest`, `envelope_digest`, `signature_b64`, `signature_algorithm`, `signer_key_id`, `issued_at`, `import_attempt_uid`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_feed_event_seq_prior` | `CHECK (((feed_sequence = 1) = (prior_event_digest IS NULL)))` |
| CHECK | `feed_event_envelope_digest_check` | `CHECK ((envelope_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `feed_event_event_kind_check` | `CHECK ((event_kind ~ '^[A-Z][A-Z0-9_]{1,63}$'::text))` |
| CHECK | `feed_event_feed_mode_check` | `CHECK ((feed_mode = ANY (ARRAY['shadow'::text, 'enforcement'::text])))` |
| CHECK | `feed_event_payload_digest_check` | `CHECK ((payload_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `feed_event_prior_event_digest_check` | `CHECK ((prior_event_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `feed_event_signature_algorithm_check` | `CHECK ((signature_algorithm = ANY (ARRAY['ed25519'::text, 'rsa-pss-sha256'::text])))` |
| FK | `feed_event_import_attempt_uid_fkey` | `FOREIGN KEY (import_attempt_uid) REFERENCES metric_audit.import_attempt_verified(attempt_uid)` |
| FK | `feed_event_signer_key_id_fkey` | `FOREIGN KEY (signer_key_id) REFERENCES metric_audit.signer_key(key_id)` |
| PK | `feed_event_pkey` | `PRIMARY KEY (event_uid)` |
| UNIQUE | `feed_event_import_attempt_uid_key` | `UNIQUE (import_attempt_uid)` |
| UNIQUE | `uq_feed_event_feed_seq` | `UNIQUE (feed_name, feed_sequence)` |

Triggers:

- `trg_feed_event_guard`: `trg_feed_event_guard BEFORE INSERT ON metric_audit.feed_event FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_feed_event_guard()`
- `trg_feed_event_immutable`: `trg_feed_event_immutable BEFORE DELETE OR UPDATE ON metric_audit.feed_event FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.feed_registration`

Columns: 11 | **NOT NULL:** `registration_uid`, `feed_name`, `feed_mode`, `direction`, `signer_key_id`, `allowed_events`, `valid_from`, `registration_digest`, `import_attempt_uid`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `feed_registration_direction_check` | `CHECK ((direction = ANY (ARRAY['auditor_to_platform'::text, 'platform_to_auditor'::text])))` |
| CHECK | `feed_registration_feed_mode_check` | `CHECK ((feed_mode = ANY (ARRAY['shadow'::text, 'enforcement'::text])))` |
| CHECK | `feed_registration_registration_digest_check` | `CHECK ((registration_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| FK | `feed_registration_import_attempt_uid_fkey` | `FOREIGN KEY (import_attempt_uid) REFERENCES metric_audit.import_attempt_verified(attempt_uid)` |
| FK | `feed_registration_signer_key_id_fkey` | `FOREIGN KEY (signer_key_id) REFERENCES metric_audit.signer_key(key_id)` |
| FK | `feed_registration_supersedes_registration_uid_fkey` | `FOREIGN KEY (supersedes_registration_uid) REFERENCES metric_audit.feed_registration(registration_uid)` |
| PK | `feed_registration_pkey` | `PRIMARY KEY (registration_uid)` |
| UNIQUE | `feed_registration_import_attempt_uid_key` | `UNIQUE (import_attempt_uid)` |
| UNIQUE | `uq_feed_registration_supersedes` | `UNIQUE (supersedes_registration_uid)` |

Triggers:

- `trg_feed_registration_guard`: `trg_feed_registration_guard BEFORE INSERT ON metric_audit.feed_registration FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_feed_registration_guard()`
- `trg_feed_registration_immutable`: `trg_feed_registration_immutable BEFORE DELETE OR UPDATE ON metric_audit.feed_registration FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.import_attempt`

Columns: 12 | **NOT NULL:** `attempt_uid`, `feed_name`, `received_bytes`, `received_digest`, `parse_status`, `verification_result`, `verifier_version`, `imported_at`, `imported_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_import_attempt_parse` | `CHECK (((parse_status = 'unparseable'::text) = (envelope_json IS NULL)))` |
| CHECK | `chk_import_attempt_parse_err` | `CHECK (((parse_status = 'unparseable'::text) = (parse_error IS NOT NULL)))` |
| CHECK | `chk_import_attempt_result` | `CHECK ((((verification_result = 'verified'::text) AND (rejection_reasons_json IS NULL) AND (parse_status = 'parsed'::text)) OR ((verification_result = 'rejected'::text) AND (rejection_reasons_json IS NOT NULL) AND (jsonb_typeof(rejection_reasons_json) = 'array'::text) AND (jsonb_array_length(rejection_reasons_json) >= 1))))` |
| CHECK | `import_attempt_parse_status_check` | `CHECK ((parse_status = ANY (ARRAY['parsed'::text, 'unparseable'::text])))` |
| CHECK | `import_attempt_received_digest_check` | `CHECK ((received_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `import_attempt_verification_result_check` | `CHECK ((verification_result = ANY (ARRAY['verified'::text, 'rejected'::text])))` |
| PK | `import_attempt_pkey` | `PRIMARY KEY (attempt_uid)` |

Triggers:

- `trg_import_attempt_guard`: `trg_import_attempt_guard BEFORE INSERT ON metric_audit.import_attempt FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_import_attempt_guard()`
- `trg_import_attempt_immutable`: `trg_import_attempt_immutable BEFORE DELETE OR UPDATE ON metric_audit.import_attempt FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.import_attempt_verified`

Columns: 15 | **NOT NULL:** `attempt_uid`, `feed_sequence`, `feed_mode`, `payload_schema_version`, `event_kind`, `canonical_payload`, `payload_digest`, `envelope_digest`, `signature_b64`, `signature_algorithm`, `signer_key_id`, `issued_at`, `subject_ref_json`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_verified_seq_prior` | `CHECK (((feed_sequence = 1) = (prior_event_digest IS NULL)))` |
| CHECK | `import_attempt_verified_envelope_digest_check` | `CHECK ((envelope_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `import_attempt_verified_event_kind_check` | `CHECK ((event_kind ~ '^[A-Z][A-Z0-9_]{1,63}$'::text))` |
| CHECK | `import_attempt_verified_feed_mode_check` | `CHECK ((feed_mode = ANY (ARRAY['shadow'::text, 'enforcement'::text])))` |
| CHECK | `import_attempt_verified_payload_digest_check` | `CHECK ((payload_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `import_attempt_verified_prior_event_digest_check` | `CHECK ((prior_event_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `import_attempt_verified_signature_algorithm_check` | `CHECK ((signature_algorithm = ANY (ARRAY['ed25519'::text, 'rsa-pss-sha256'::text])))` |
| FK | `import_attempt_verified_attempt_uid_fkey` | `FOREIGN KEY (attempt_uid) REFERENCES metric_audit.import_attempt(attempt_uid)` |
| FK | `import_attempt_verified_signer_key_id_fkey` | `FOREIGN KEY (signer_key_id) REFERENCES metric_audit.signer_key(key_id)` |
| PK | `import_attempt_verified_pkey` | `PRIMARY KEY (attempt_uid)` |

Triggers:

- `trg_import_attempt_verified_guard`: `trg_import_attempt_verified_guard BEFORE INSERT ON metric_audit.import_attempt_verified FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_import_attempt_verified_guard()`
- `trg_import_attempt_verified_immutable`: `trg_import_attempt_verified_immutable BEFORE DELETE OR UPDATE ON metric_audit.import_attempt_verified FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.intrinsic_authority_pin`

Columns: 13 | **NOT NULL:** `pin_uid`, `source_authority_revision`, `authority_revision`, `source_authority_policy_digest`, `package_hash_algorithm`, `methodology_version`, `methodology_digest`, `engine`, `engine_version`, `gate_policy_version`, `is_current`, `pinned_at`, `pinned_by`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `intrinsic_authority_pin_methodology_digest_check` | `CHECK ((methodology_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `intrinsic_authority_pin_package_hash_algorithm_check` | `CHECK ((package_hash_algorithm = 'mcf-package-v3'::text))` |
| CHECK | `intrinsic_authority_pin_source_authority_policy_digest_check` | `CHECK ((source_authority_policy_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| PK | `intrinsic_authority_pin_pkey` | `PRIMARY KEY (pin_uid)` |

Triggers:

- `trg_intrinsic_authority_pin_guard`: `trg_intrinsic_authority_pin_guard BEFORE INSERT ON metric_audit.intrinsic_authority_pin FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_intrinsic_authority_pin_guard()`
- `trg_intrinsic_authority_pin_immutable`: `trg_intrinsic_authority_pin_immutable BEFORE DELETE OR UPDATE ON metric_audit.intrinsic_authority_pin FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_intrinsic_authority_pin_immutability()`

### `metric_audit.intrinsic_authority_pin_event`

Columns: 15 | **NOT NULL:** `event_uid`, `event_sequence`, `event_kind`, `successor_pin_uid`, `successor_pin_digest`, `methodology_release_ratification_ref`, `methodology_release_ratification_sha256`, `operator_authorization_ref`, `operator_authorization_sha256`, `accepted_review_response_ref`, `accepted_review_response_sha256`, `reason`, `created_at`, `created_by`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_ape_supersede_predecessor` | `CHECK (((event_kind <> 'supersede_current'::text) OR (predecessor_pin_uid IS NOT NULL)))` |
| CHECK | `intrinsic_authority_pin_even_accepted_review_response_sha_check` | `CHECK ((accepted_review_response_sha256 ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `intrinsic_authority_pin_even_methodology_release_ratifica_check` | `CHECK ((methodology_release_ratification_sha256 ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `intrinsic_authority_pin_even_operator_authorization_sha25_check` | `CHECK ((operator_authorization_sha256 ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `intrinsic_authority_pin_event_event_kind_check` | `CHECK ((event_kind = ANY (ARRAY['supersede_current'::text, 'revoke_prospective'::text, 'revoke_compromise_retroactive'::text])))` |
| CHECK | `intrinsic_authority_pin_event_successor_pin_digest_check` | `CHECK ((successor_pin_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| FK | `intrinsic_authority_pin_event_predecessor_pin_uid_fkey` | `FOREIGN KEY (predecessor_pin_uid) REFERENCES metric_audit.intrinsic_authority_pin(pin_uid)` |
| FK | `intrinsic_authority_pin_event_successor_pin_uid_fkey` | `FOREIGN KEY (successor_pin_uid) REFERENCES metric_audit.intrinsic_authority_pin(pin_uid)` |
| PK | `intrinsic_authority_pin_event_pkey` | `PRIMARY KEY (event_uid)` |

Triggers:

- `trg_ape_guard`: `trg_ape_guard BEFORE INSERT ON metric_audit.intrinsic_authority_pin_event FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_intrinsic_authority_pin_event_guard()`
- `trg_ape_immutable`: `trg_ape_immutable BEFORE DELETE OR UPDATE ON metric_audit.intrinsic_authority_pin_event FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_intrinsic_authority_pin_event_immutable()`

### `metric_audit.invalidation`

Columns: 13 | **NOT NULL:** `invalidation_uid`, `metric_contract_version_uid`, `cause_kind`, `root_cause_fingerprint`, `invalidated_at`, `invalidated_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_invalidation_cause_xor` | `CHECK ((((cause_kind = 'external_revocation'::text) AND ((cause_decision_uid IS NOT NULL) OR (cause_signer_key_id IS NOT NULL)) AND (cause_nc_uid IS NULL) AND (closure_root_before IS NULL) AND (closure_root_after IS NULL)) OR ((cause_kind = 'blocking_nc'::text) AND (cause_decision_uid IS NOT NULL) AND (cause_nc_uid IS NOT NULL) AND (cause_signer_key_id IS NULL) AND (closure_root_before IS NULL) AND (closure_root_after IS NULL)) OR ((cause_kind = 'failed_decision'::text) AND (cause_decision_uid IS NOT NULL) AND (cause_nc_uid IS NULL) AND (cause_signer_key_id IS NULL) AND (closure_root_before IS NULL) AND (closure_root_after IS NULL)) OR ((cause_kind = 'internal_closure_drift'::text) AND (closure_root_before IS NOT NULL) AND (closure_root_after IS NOT NULL) AND (cause_decision_uid IS NULL) AND (cause_nc_uid IS NULL) AND (cause_signer_key_id IS NULL))))` |
| CHECK | `invalidation_cause_kind_check` | `CHECK ((cause_kind = ANY (ARRAY['external_revocation'::text, 'blocking_nc'::text, 'internal_closure_drift'::text, 'failed_decision'::text])))` |
| FK | `invalidation_cause_decision_uid_fkey` | `FOREIGN KEY (cause_decision_uid) REFERENCES metric_audit.decision(decision_uid)` |
| FK | `invalidation_cause_signer_key_id_fkey` | `FOREIGN KEY (cause_signer_key_id) REFERENCES metric_audit.signer_key(key_id)` |
| FK | `invalidation_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| PK | `invalidation_pkey` | `PRIMARY KEY (invalidation_uid)` |
| UNIQUE | `uq_invalidation_live` | `UNIQUE (metric_contract_version_uid, root_cause_fingerprint)` |

Triggers:

- `trg_invalidation_immutable`: `trg_invalidation_immutable BEFORE DELETE OR UPDATE ON metric_audit.invalidation FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_invalidation_immutability()`

### `metric_audit.nc_reference`

Columns: 20 | **NOT NULL:** `nc_uid`, `feed_event_uid`, `nc_payload_digest`, `report_uid`, `finding_uid`, `severity`, `scope`, `is_blocking`, `remediation_direction`, `acceptance_criteria_json`, `requirement_json`, `observed_condition`, `expected_condition`, `impact`, `objective_evidence_json`, `re_audit_trigger_json`, `issued_by`, `issued_at`, `status`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_nc_blocking_derivation` | `CHECK ((is_blocking = (severity = ANY (ARRAY['CRITICAL'::text, 'MAJOR'::text]))))` |
| CHECK | `nc_reference_nc_payload_digest_check` | `CHECK ((nc_payload_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `nc_reference_remediation_direction_check` | `CHECK ((length(remediation_direction) > 0))` |
| CHECK | `nc_reference_scope_check` | `CHECK ((scope = ANY (ARRAY['METRIC'::text, 'FAMILY'::text, 'SYSTEMIC'::text])))` |
| CHECK | `nc_reference_severity_check` | `CHECK ((severity = ANY (ARRAY['CRITICAL'::text, 'MAJOR'::text, 'MINOR'::text])))` |
| CHECK | `nc_reference_status_check` | `CHECK ((status = 'OPEN'::text))` |
| FK | `fk_nc_reference_finding` | `FOREIGN KEY (report_uid, finding_uid) REFERENCES metric_audit.report_finding(report_uid, finding_uid)` |
| FK | `nc_reference_feed_event_uid_fkey` | `FOREIGN KEY (feed_event_uid) REFERENCES metric_audit.feed_event(event_uid)` |
| PK | `nc_reference_pkey` | `PRIMARY KEY (nc_uid)` |
| UNIQUE | `nc_reference_feed_event_uid_key` | `UNIQUE (feed_event_uid)` |

Triggers:

- `trg_nc_reference_guard`: `trg_nc_reference_guard BEFORE INSERT ON metric_audit.nc_reference FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_nc_reference_guard()`
- `trg_nc_reference_immutable`: `trg_nc_reference_immutable BEFORE DELETE OR UPDATE ON metric_audit.nc_reference FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.platform_signer`

Columns: 6 | **NOT NULL:** `signer_key_id`, `fingerprint`, `algorithm`, `valid_from`, `created_at`, `created_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `platform_signer_algorithm_check` | `CHECK ((algorithm = ANY (ARRAY['ed25519'::text, 'rsa-pss-sha256'::text])))` |
| CHECK | `platform_signer_fingerprint_check` | `CHECK ((fingerprint ~ '^sha256:[a-f0-9]{64}$'::text))` |
| PK | `platform_signer_pkey` | `PRIMARY KEY (signer_key_id)` |

Triggers:

- `trg_platform_signer_immutable`: `trg_platform_signer_immutable BEFORE DELETE OR UPDATE ON metric_audit.platform_signer FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.platform_signer_event`

Columns: 8 | **NOT NULL:** `event_uid`, `signer_key_id`, `event_kind`, `effective_at`, `authority_ref`, `reason`, `created_at`, `created_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `platform_signer_event_event_kind_check` | `CHECK ((event_kind = ANY (ARRAY['expire'::text, 'rotate'::text, 'revoke_prospective'::text, 'revoke_compromise_retroactive'::text])))` |
| FK | `platform_signer_event_signer_key_id_fkey` | `FOREIGN KEY (signer_key_id) REFERENCES metric_audit.platform_signer(signer_key_id)` |
| PK | `platform_signer_event_pkey` | `PRIMARY KEY (event_uid)` |

Triggers:

- `trg_platform_signer_event_immutable`: `trg_platform_signer_event_immutable BEFORE DELETE OR UPDATE ON metric_audit.platform_signer_event FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.reintake_accepted_manifest`

Columns: 4 | **NOT NULL:** `canonical_set_hash`, `phase`, `accepted_response_ref`, `pinned_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `reintake_accepted_manifest_canonical_set_hash_check` | `CHECK ((canonical_set_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| PK | `reintake_accepted_manifest_pkey` | `PRIMARY KEY (canonical_set_hash)` |

Triggers:

- `trg_reintake_accepted_manifest_immutable`: `trg_reintake_accepted_manifest_immutable BEFORE DELETE OR UPDATE ON metric_audit.reintake_accepted_manifest FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reintake_accepted_immutable()`

### `metric_audit.reintake_accepted_member`

Columns: 6 | **NOT NULL:** `canonical_set_hash`, `member_uid`, `member_version_uid`, `metric_contract_version_uid`, `cohort`, `loaded_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `reintake_accepted_member_cohort_check` | `CHECK ((length(cohort) > 0))` |
| FK | `reintake_accepted_member_canonical_set_hash_fkey` | `FOREIGN KEY (canonical_set_hash) REFERENCES metric_audit.reintake_accepted_manifest(canonical_set_hash)` |
| FK | `reintake_accepted_member_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| PK | `reintake_accepted_member_pkey` | `PRIMARY KEY (canonical_set_hash, metric_contract_version_uid)` |
| UNIQUE | `uq_accepted_member_tuple` | `UNIQUE (canonical_set_hash, member_uid, member_version_uid, metric_contract_version_uid)` |

Triggers:

- `trg_reintake_accepted_member_immutable`: `trg_reintake_accepted_member_immutable BEFORE DELETE OR UPDATE ON metric_audit.reintake_accepted_member FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reintake_accepted_immutable()`

### `metric_audit.reintake_batch`

Columns: 8 | **NOT NULL:** `reintake_batch_uid`, `manifest_canonical_set_hash`, `cohort_scope`, `status`, `authorized_by`, `authorization_rationale_text`, `authorized_at`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `reintake_batch_authorization_rationale_text_check` | `CHECK ((length(authorization_rationale_text) >= 40))` |
| CHECK | `reintake_batch_authorized_by_check` | `CHECK ((length(authorized_by) >= 3))` |
| CHECK | `reintake_batch_cohort_scope_check` | `CHECK ((cohort_scope = ANY (ARRAY['eligible_first_batch'::text, 'eligible_later_batch'::text, 'corrected_successor_eligible'::text, 'corrected_successor_reproof_admissible_eligible'::text, 'reproof_admissible_eligible'::text, 'reproducible_admissible_eligible'::text, 'multi_cohort'::text])))` |
| CHECK | `reintake_batch_status_check` | `CHECK ((status = ANY (ARRAY['open'::text, 'closed'::text])))` |
| FK | `reintake_batch_manifest_canonical_set_hash_fkey` | `FOREIGN KEY (manifest_canonical_set_hash) REFERENCES metric_audit.reintake_accepted_manifest(canonical_set_hash)` |
| PK | `reintake_batch_pkey` | `PRIMARY KEY (reintake_batch_uid)` |

Triggers:

- `trg_reintake_batch_immutable`: `trg_reintake_batch_immutable BEFORE DELETE OR UPDATE ON metric_audit.reintake_batch FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reintake_batch_immutable()`

### `metric_audit.reintake_batch_cohort`

Columns: 5 | **NOT NULL:** `reintake_batch_uid`, `cohort`, `disposition`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `ck_reintake_batch_cohort_disposition` | `CHECK ((disposition = ANY (ARRAY['eligible'::text, 'excluded'::text])))` |
| CHECK | `ck_reintake_batch_cohort_excluded_rationale` | `CHECK (((disposition = 'eligible'::text) OR ((rationale_text IS NOT NULL) AND (length(rationale_text) >= 20))))` |
| CHECK | `ck_reintake_batch_cohort_nonempty` | `CHECK ((length(cohort) > 0))` |
| FK | `reintake_batch_cohort_reintake_batch_uid_fkey` | `FOREIGN KEY (reintake_batch_uid) REFERENCES metric_audit.reintake_batch(reintake_batch_uid)` |
| PK | `pk_reintake_batch_cohort` | `PRIMARY KEY (reintake_batch_uid, cohort)` |

### `metric_audit.reintake_batch_member`

Columns: 7 | **NOT NULL:** `reintake_batch_member_uid`, `reintake_batch_uid`, `metric_contract_version_uid`, `member_uid`, `member_version_uid`, `cohort`, `added_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `reintake_batch_member_cohort_check` | `CHECK ((length(cohort) > 0))` |
| FK | `reintake_batch_member_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| FK | `reintake_batch_member_reintake_batch_uid_fkey` | `FOREIGN KEY (reintake_batch_uid) REFERENCES metric_audit.reintake_batch(reintake_batch_uid)` |
| PK | `reintake_batch_member_pkey` | `PRIMARY KEY (reintake_batch_member_uid)` |
| UNIQUE | `uq_reintake_batch_member` | `UNIQUE (reintake_batch_uid, metric_contract_version_uid)` |

Triggers:

- `trg_reintake_batch_member_cohort_authorized`: `trg_reintake_batch_member_cohort_authorized BEFORE INSERT OR UPDATE ON metric_audit.reintake_batch_member FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reintake_batch_member_cohort_authorized()`
- `trg_reintake_batch_member_immutable`: `trg_reintake_batch_member_immutable BEFORE DELETE OR UPDATE ON metric_audit.reintake_batch_member FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reintake_batch_member_immutable()`
- `trg_reintake_member_accepted`: `trg_reintake_member_accepted BEFORE INSERT ON metric_audit.reintake_batch_member FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reintake_member_accepted_check()`

### `metric_audit.report_finding`

Columns: 9 | **NOT NULL:** `report_uid`, `finding_uid`, `finding_kind`, `severity`, `area`, `description`, `evidence_citations_json`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `report_finding_area_check` | `CHECK ((area ~ '^[a-z][a-z0-9_]{1,63}$'::text))` |
| CHECK | `report_finding_finding_kind_check` | `CHECK ((finding_kind ~ '^[a-z][a-z0-9_]{1,63}$'::text))` |
| CHECK | `report_finding_severity_check` | `CHECK ((severity = ANY (ARRAY['CRITICAL'::text, 'MAJOR'::text, 'MINOR'::text, 'OBSERVATION'::text])))` |
| FK | `report_finding_report_uid_fkey` | `FOREIGN KEY (report_uid) REFERENCES metric_audit.report_reference(report_uid)` |
| PK | `pk_report_finding` | `PRIMARY KEY (report_uid, finding_uid)` |

Triggers:

- `trg_report_finding_immutable`: `trg_report_finding_immutable BEFORE DELETE OR UPDATE ON metric_audit.report_finding FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`
- `trg_report_finding_membership`: `trg_report_finding_membership BEFORE INSERT ON metric_audit.report_finding FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_report_finding_membership()`

### `metric_audit.report_raised_nc`

Columns: 3 | **NOT NULL:** `report_uid`, `nc_uid`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| FK | `report_raised_nc_report_uid_fkey` | `FOREIGN KEY (report_uid) REFERENCES metric_audit.report_reference(report_uid)` |
| PK | `pk_report_raised_nc` | `PRIMARY KEY (report_uid, nc_uid)` |

Triggers:

- `trg_report_raised_nc_immutable`: `trg_report_raised_nc_immutable BEFORE DELETE OR UPDATE ON metric_audit.report_raised_nc FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`
- `trg_report_raised_nc_membership`: `trg_report_raised_nc_membership BEFORE INSERT ON metric_audit.report_raised_nc FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_report_raised_nc_membership()`

### `metric_audit.report_reference`

Columns: 29 | **NOT NULL:** `report_uid`, `feed_event_uid`, `report_payload_digest`, `request_uid`, `request_digest`, `metric_contract_version_uid`, `package_snapshot_digest`, `closure_root`, `audit_run_uid`, `engine`, `engine_version`, `methodology_version`, `methodology_digest`, `authority_revision`, `gate_policy_version`, `source_authority_revision`, `audited_at`, `overall_assessment`, `structural_verdict`, `foundation_verdict`, `contextual_definition_score`, `contextual_formula_score`, `contextual_input_semantics_score`, `contextual_overall_score`, `contextual_decision`, `semantic_conformance_verdict`, `exactness_result`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `report_reference_closure_root_check` | `CHECK ((closure_root ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `report_reference_contextual_decision_check` | `CHECK ((contextual_decision = ANY (ARRAY['VERIFIED'::text, 'HIGH_CONFIDENCE'::text, 'CONDITIONAL'::text, 'REJECT'::text])))` |
| CHECK | `report_reference_contextual_definition_score_check` | `CHECK (((contextual_definition_score >= 1) AND (contextual_definition_score <= 5)))` |
| CHECK | `report_reference_contextual_formula_score_check` | `CHECK (((contextual_formula_score >= 1) AND (contextual_formula_score <= 5)))` |
| CHECK | `report_reference_contextual_input_semantics_score_check` | `CHECK (((contextual_input_semantics_score >= 1) AND (contextual_input_semantics_score <= 5)))` |
| CHECK | `report_reference_contextual_overall_score_check` | `CHECK (((contextual_overall_score >= 1) AND (contextual_overall_score <= 5)))` |
| CHECK | `report_reference_exactness_result_check` | `CHECK ((exactness_result = ANY (ARRAY['EXACT'::text, 'NOT_PROVEN'::text, 'REPRODUCIBLE'::text])))` |
| CHECK | `report_reference_foundation_verdict_check` | `CHECK ((foundation_verdict = ANY (ARRAY['PASS'::text, 'REJECT'::text])))` |
| CHECK | `report_reference_methodology_digest_check` | `CHECK ((methodology_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `report_reference_overall_assessment_check` | `CHECK ((overall_assessment = ANY (ARRAY['PASS'::text, 'REJECT'::text, 'OPERATOR_REVIEW'::text])))` |
| CHECK | `report_reference_package_snapshot_digest_check` | `CHECK ((package_snapshot_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `report_reference_report_payload_digest_check` | `CHECK ((report_payload_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `report_reference_request_digest_check` | `CHECK ((request_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `report_reference_semantic_conformance_verdict_check` | `CHECK ((semantic_conformance_verdict = ANY (ARRAY['PASS'::text, 'REJECT'::text, 'NOT_APPLICABLE'::text])))` |
| CHECK | `report_reference_structural_verdict_check` | `CHECK ((structural_verdict = ANY (ARRAY['PASS'::text, 'REJECT'::text])))` |
| FK | `report_reference_feed_event_uid_fkey` | `FOREIGN KEY (feed_event_uid) REFERENCES metric_audit.feed_event(event_uid)` |
| FK | `report_reference_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| FK | `report_reference_request_uid_fkey` | `FOREIGN KEY (request_uid) REFERENCES metric_audit.request_publication(request_uid)` |
| PK | `report_reference_pkey` | `PRIMARY KEY (report_uid)` |
| t | `trg_report_reference_finalize` | `TRIGGER DEFERRABLE INITIALLY DEFERRED` |
| UNIQUE | `report_reference_feed_event_uid_key` | `UNIQUE (feed_event_uid)` |

Triggers:

- `trg_report_reference_finalize`: `CREATE CONSTRAINT TRIGGER trg_report_reference_finalize AFTER INSERT ON metric_audit.report_reference DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_report_reference_finalize()`
- `trg_report_reference_guard`: `trg_report_reference_guard BEFORE INSERT ON metric_audit.report_reference FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_report_reference_guard()`
- `trg_report_reference_immutable`: `trg_report_reference_immutable BEFORE DELETE OR UPDATE ON metric_audit.report_reference FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.request_outbox`

Columns: 14 | **NOT NULL:** `request_uid`, `metric_contract_version_uid`, `package_snapshot_digest`, `closure_root`, `projection_inputs_digest`, `trigger_kind`, `cause_kind`, `cause_uid`, `authority_revision`, `feed_name`, `request_canonical_bytes`, `request_digest`, `created_at`, `created_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `request_outbox_cause_kind_check` | `CHECK ((cause_kind = ANY (ARRAY['certification_record'::text, 'audit_migration_batch'::text, 'compliance_report'::text, 'invalidation'::text, 'metric_correction'::text])))` |
| CHECK | `request_outbox_closure_root_check` | `CHECK ((closure_root ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `request_outbox_package_snapshot_digest_check` | `CHECK ((package_snapshot_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `request_outbox_projection_inputs_digest_check` | `CHECK ((projection_inputs_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `request_outbox_request_digest_check` | `CHECK ((request_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `request_outbox_trigger_kind_check` | `CHECK ((trigger_kind = ANY (ARRAY['approved_transition'::text, 'migration_batch'::text, 'remediation_re_audit'::text, 'governed_recovery'::text])))` |
| FK | `request_outbox_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| PK | `request_outbox_pkey` | `PRIMARY KEY (request_uid)` |

Triggers:

- `trg_request_outbox_guard`: `trg_request_outbox_guard BEFORE INSERT ON metric_audit.request_outbox FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_request_outbox_guard()`
- `trg_request_outbox_immutable`: `trg_request_outbox_immutable BEFORE DELETE OR UPDATE ON metric_audit.request_outbox FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.request_preflight_disposition`

Columns: 12 | **NOT NULL:** `request_preflight_disposition_uid`, `metric_contract_version_uid`, `disposition_code`, `reason_details_json`, `substrate_fingerprint`, `cohort_code`, `actor`, `authority_revision`, `attempt_digest`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `request_preflight_dispositio_attempted_package_snapshot_d_check` | `CHECK ((attempted_package_snapshot_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `request_preflight_disposition_attempt_digest_check` | `CHECK ((attempt_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `request_preflight_disposition_attempted_closure_root_check` | `CHECK ((attempted_closure_root ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `request_preflight_disposition_disposition_code_check` | `CHECK ((disposition_code = ANY (ARRAY['refused_not_v3_computable'::text, 'refused_no_operative_realization'::text])))` |
| CHECK | `request_preflight_disposition_substrate_fingerprint_check` | `CHECK ((substrate_fingerprint ~ '^sha256:[a-f0-9]{64}$'::text))` |
| FK | `request_preflight_disposition_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| PK | `request_preflight_disposition_pkey` | `PRIMARY KEY (request_preflight_disposition_uid)` |
| UNIQUE | `uq_preflight_disposition_attempt` | `UNIQUE (attempt_digest)` |

Triggers:

- `trg_preflight_disposition_guard`: `trg_preflight_disposition_guard BEFORE INSERT ON metric_audit.request_preflight_disposition FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_preflight_disposition_guard()`
- `trg_preflight_disposition_immutability`: `trg_preflight_disposition_immutability BEFORE DELETE OR UPDATE ON metric_audit.request_preflight_disposition FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_preflight_disposition_immutability()`

### `metric_audit.request_publication`

Columns: 15 | **NOT NULL:** `publication_uid`, `request_uid`, `feed_name`, `feed_sequence`, `signed_envelope_json`, `canonical_payload`, `payload_digest`, `envelope_digest`, `signature_b64`, `signature_algorithm`, `platform_signer_key_id`, `platform_signer_fingerprint`, `published_at`, `published_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_request_publication_seq_prior` | `CHECK (((feed_sequence = 1) = (prior_event_digest IS NULL)))` |
| CHECK | `request_publication_envelope_digest_check` | `CHECK ((envelope_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `request_publication_payload_digest_check` | `CHECK ((payload_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `request_publication_platform_signer_fingerprint_check` | `CHECK ((platform_signer_fingerprint ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `request_publication_prior_event_digest_check` | `CHECK ((prior_event_digest ~ '^sha256:[a-f0-9]{64}$'::text))` |
| CHECK | `request_publication_signature_algorithm_check` | `CHECK ((signature_algorithm = ANY (ARRAY['ed25519'::text, 'rsa-pss-sha256'::text])))` |
| FK | `request_publication_platform_signer_key_id_fkey` | `FOREIGN KEY (platform_signer_key_id) REFERENCES metric_audit.platform_signer(signer_key_id)` |
| FK | `request_publication_request_uid_fkey` | `FOREIGN KEY (request_uid) REFERENCES metric_audit.request_outbox(request_uid)` |
| PK | `request_publication_pkey` | `PRIMARY KEY (publication_uid)` |
| UNIQUE | `request_publication_request_uid_key` | `UNIQUE (request_uid)` |
| UNIQUE | `uq_request_publication_feed_seq` | `UNIQUE (feed_name, feed_sequence)` |

Triggers:

- `trg_request_publication_guard`: `trg_request_publication_guard BEFORE INSERT ON metric_audit.request_publication FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_request_publication_guard()`
- `trg_request_publication_immutable`: `trg_request_publication_immutable BEFORE DELETE OR UPDATE ON metric_audit.request_publication FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.signer_key`

Columns: 6 | **NOT NULL:** `key_id`, `public_key_pem`, `algorithm`, `valid_from`, `created_at`, `created_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `auditor_signer_key_algorithm_check` | `CHECK ((algorithm = ANY (ARRAY['ed25519'::text, 'rsa-pss-sha256'::text])))` |
| PK | `auditor_signer_key_pkey` | `PRIMARY KEY (key_id)` |

Triggers:

- `trg_auditor_signer_key_immutable`: `trg_auditor_signer_key_immutable BEFORE DELETE OR UPDATE ON metric_audit.signer_key FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

### `metric_audit.signer_key_event`

Columns: 8 | **NOT NULL:** `event_uid`, `key_id`, `event_kind`, `effective_at`, `authority_ref`, `reason`, `created_at`, `created_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `auditor_signer_key_event_event_kind_check` | `CHECK ((event_kind = ANY (ARRAY['expire'::text, 'rotate'::text, 'revoke_prospective'::text, 'revoke_compromise_retroactive'::text])))` |
| FK | `auditor_signer_key_event_key_id_fkey` | `FOREIGN KEY (key_id) REFERENCES metric_audit.signer_key(key_id)` |
| PK | `auditor_signer_key_event_pkey` | `PRIMARY KEY (event_uid)` |
| t | `trg_c6_deferred_signer_compromise` | `TRIGGER DEFERRABLE INITIALLY DEFERRED` |

Triggers:

- `trg_auditor_signer_key_event_immutable`: `trg_auditor_signer_key_event_immutable BEFORE DELETE OR UPDATE ON metric_audit.signer_key_event FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`
- `trg_c6_deferred_signer_compromise`: `CREATE CONSTRAINT TRIGGER trg_c6_deferred_signer_compromise AFTER INSERT ON metric_audit.signer_key_event DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_c6_deferred_signer_compromise()`

### `metric_audit.transition_evidence`

Columns: 11 | **NOT NULL:** `transition_evidence_uid`, `certification_record_id`, `metric_contract_version_uid`, `action_code`, `from_state_code`, `to_state_code`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_transition_evidence_shape` | `CHECK ((((action_code = 'audit_migrate'::text) AND (from_state_code = 'approved'::text) AND (to_state_code = 'audit_pending'::text) AND (request_uid IS NOT NULL) AND (decision_uid IS NULL) AND (block_reason_kind IS NULL)) OR ((action_code = 'metric_correction'::text) AND (from_state_code = 'superseded'::text) AND (to_state_code = 'audit_pending'::text) AND (request_uid IS NOT NULL) AND (decision_uid IS NULL) AND (block_reason_kind IS NULL)) OR ((action_code = 'audit_block'::text) AND (to_state_code = 'audit_blocked'::text) AND (from_state_code = ANY (ARRAY['active'::text, 'audit_pending'::text])) AND (decision_uid IS NOT NULL) AND (block_reason_kind IS NOT NULL) AND (request_uid IS NULL)) OR ((action_code = 'audit_admit'::text) AND (from_state_code = 'audit_pending'::text) AND (to_state_code = 'active'::text) AND (decision_uid IS NOT NULL) AND (request_uid IS NULL) AND (block_reason_kind IS NULL)) OR ((action_code = 'audit_reintake'::text) AND (from_state_code = 'active'::text) AND (to_state_code = 'audit_pending'::text) AND (request_uid IS NULL) AND (decision_uid IS NULL) AND (block_reason_kind IS NULL))))` |
| CHECK | `transition_evidence_action_code_check` | `CHECK ((action_code = ANY (ARRAY['audit_migrate'::text, 'audit_block'::text, 'audit_remediate'::text, 'audit_admit'::text, 'metric_correction'::text, 'audit_reintake'::text])))` |
| CHECK | `transition_evidence_block_reason_kind_check` | `CHECK ((block_reason_kind = ANY (ARRAY['rejected_decision'::text, 'revoked_decision'::text])))` |
| FK | `transition_evidence_certification_record_id_fkey` | `FOREIGN KEY (certification_record_id) REFERENCES mcf.certification_record(certification_record_id)` |
| FK | `transition_evidence_decision_uid_fkey` | `FOREIGN KEY (decision_uid) REFERENCES metric_audit.decision(decision_uid)` |
| FK | `transition_evidence_invalidation_uid_fkey` | `FOREIGN KEY (invalidation_uid) REFERENCES metric_audit.invalidation(invalidation_uid)` |
| FK | `transition_evidence_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| FK | `transition_evidence_request_uid_fkey` | `FOREIGN KEY (request_uid) REFERENCES metric_audit.request_outbox(request_uid)` |
| PK | `transition_evidence_pkey` | `PRIMARY KEY (transition_evidence_uid)` |
| UNIQUE | `transition_evidence_certification_record_id_key` | `UNIQUE (certification_record_id)` |
| UNIQUE | `transition_evidence_request_uid_key` | `UNIQUE (request_uid)` |

Triggers:

- `trg_transition_evidence_guard`: `trg_transition_evidence_guard BEFORE INSERT ON metric_audit.transition_evidence FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_transition_evidence_guard()`
- `trg_transition_evidence_immutable`: `trg_transition_evidence_immutable BEFORE DELETE OR UPDATE ON metric_audit.transition_evidence FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_reject_mutation()`

## 4. Platform substrate constraints — `mcf`

### `mcf.certification_record`

Columns: 25 | **NOT NULL:** `certification_record_id`, `primitive_type`, `primitive_id`, `action_code`, `to_state_code`, `gate_results_json`, `advisory_verdicts_json`, `certifier_sub`, `certifier_role_at_action`, `created_at`, `policy_version`, `subject_kind`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `certification_record_action_code_check` | `CHECK ((action_code = ANY (ARRAY['metric_create'::text, 'metric_transition'::text, 'metric_supersede'::text, 'metric_correction'::text, 'audit_admit'::text, 'audit_block'::text, 'audit_remediate'::text, 'audit_migrate'::text, 'metric_approve'::text, 'audit_reintake'::text])))` |
| CHECK | `certification_record_action_state_check` | `CHECK ((((action_code = 'metric_create'::text) AND (from_state_code IS NULL) AND (to_state_code = 'draft'::text)) OR ((action_code = 'metric_transition'::text) AND (from_state_code = 'approved'::text) AND (to_state_code = 'active'::text)) OR ((action_code = 'metric_supersede'::text) AND (from_state_code = 'active'::text) AND (to_state_code = 'superseded'::text)) OR ((action_code = 'metric_correction'::text) AND (from_state_code = 'superseded'::text) AND (to_state_code = 'active'::text)) OR ((action_code = 'metric_correction'::text) AND (from_state_code = 'superseded'::text) AND (to_state_code = 'audit_pending'::text)) OR ((action_code = 'audit_migrate'::text) AND (from_state_code = 'approved'::text) AND (to_state_code = 'audit_pending'::text)) OR ((action_code = 'audit_migrate'::text) AND (from_state_code = 'active'::text) AND (to_state_code = 'audit_pending'::text)) OR ((action_code = 'audit_reintake'::text) AND (from_state_code = 'active'::text) AND (to_state_code = 'audit_pending'::text)) OR ((action_code = 'audit_block'::text) AND (from_state_code = 'active'::text) AND (to_state_code = 'audit_blocked'::text)) OR ((action_code = 'audit_block'::text) AND (from_state_code = 'audit_pending'::text) AND (to_state_code = 'audit_blocked'::text)) OR ((action_code = 'audit_remediate'::text) AND (from_state_code = 'audit_blocked'::text) AND (to_state_code = 'audit_pending'::text)) OR ((action_code = 'audit_admit'::text) AND (from_state_code = 'audit_pending'::text) AND (to_state_code = 'active'::text)) OR ((action_code = 'metric_approve'::text) AND (from_state_code = 'review'::text) AND (to_state_code = 'approved'::text))))` |
| CHECK | `certification_record_supersedes_check` | `CHECK ((((action_code = 'metric_supersede'::text) AND (supersedes_primitive_id IS NOT NULL)) OR ((action_code <> 'metric_supersede'::text) AND (supersedes_primitive_id IS NULL))))` |
| CHECK | `mcf_cert_certifier_role_chk` | `CHECK ((certifier_role_at_action = ANY (ARRAY['panel'::text, 'operator'::text, 'system'::text])))` |
| CHECK | `mcf_cert_grounding_chk` | `CHECK (((grounding_check_result IS NULL) OR (grounding_check_result = ANY (ARRAY['pass'::text, 'quarantined'::text]))))` |
| CHECK | `mcf_cert_nf1_all_or_none_chk` | `CHECK ((((panel_run_uid IS NULL) AND (prompt_version IS NULL) AND (model_identity_json IS NULL) AND (input_hash IS NULL) AND (sampling_status IS NULL) AND (grounding_check_result IS NULL)) OR ((panel_run_uid IS NOT NULL) AND (prompt_version IS NOT NULL) AND (model_identity_json IS NOT NULL) AND (input_hash IS NOT NULL) AND (sampling_status IS NOT NULL) AND (grounding_check_result IS NOT NULL))))` |
| CHECK | `mcf_cert_override_chk` | `CHECK ((((override_gate_code IS NULL) AND (override_rationale_text IS NULL) AND (override_followup_task_uid IS NULL)) OR ((override_gate_code IS NOT NULL) AND (char_length(override_rationale_text) >= 40) AND (override_followup_task_uid IS NOT NULL))))` |
| CHECK | `mcf_cert_primitive_type_chk` | `CHECK ((primitive_type = 'metric_contract_version'::text))` |
| CHECK | `mcf_cert_sampling_chk` | `CHECK (((sampling_status IS NULL) OR (sampling_status = ANY (ARRAY['not_sampled'::text, 'sampled_for_calibration'::text, 'sample_routed_to_operator'::text]))))` |
| CHECK | `mcf_cert_subject_kind_chk` | `CHECK ((subject_kind = ANY (ARRAY['metric_contract_version'::text, 'metric_publication'::text, 'metric_supersession'::text])))` |
| FK | `fk_mcf_cert_panel_run` | `FOREIGN KEY (panel_run_uid) REFERENCES bcf.panel_output_record(panel_run_uid) ON DELETE RESTRICT` |
| PK | `certification_record_pkey` | `PRIMARY KEY (certification_record_id)` |
| t | `trg_audit_cert_finalize` | `TRIGGER DEFERRABLE INITIALLY DEFERRED` |
| t | `trg_c7_require_reintake_evidence` | `TRIGGER DEFERRABLE INITIALLY DEFERRED` |
| t | `trg_c8_require_admit_evidence` | `TRIGGER DEFERRABLE INITIALLY DEFERRED` |

Triggers:

- `trg_audit_cert_finalize`: `CREATE CONSTRAINT TRIGGER trg_audit_cert_finalize AFTER INSERT ON mcf.certification_record DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION mcf.fn_audit_cert_finalize()`
- `trg_c7_require_reintake_evidence`: `CREATE CONSTRAINT TRIGGER trg_c7_require_reintake_evidence AFTER INSERT ON mcf.certification_record DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_c7_require_reintake_evidence()`
- `trg_c8_require_admit_evidence`: `CREATE CONSTRAINT TRIGGER trg_c8_require_admit_evidence AFTER INSERT ON mcf.certification_record DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION metric_audit.fn_c8_require_admit_evidence()`
- `trg_cert_legacy_tuple_freeze`: `trg_cert_legacy_tuple_freeze BEFORE INSERT ON mcf.certification_record FOR EACH ROW EXECUTE FUNCTION mcf.fn_cert_legacy_tuple_freeze()`

### `mcf.chain_audit_evidence`

Columns: 12 | **NOT NULL:** `audit_evidence_uid`, `audit_mode_code`, `target_kind_code`, `target_uid`, `verdict_code`, `findings_json`, `check_results_json`, `input_substrate_snapshot_hash`, `audit_engine_version`, `computed_at`, `computed_by_role`, `computed_by_sub`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chain_audit_evidence_audit_mode_code_check` | `CHECK ((audit_mode_code = ANY (ARRAY['pre_m12_audit'::text, 'pre_m13_audit'::text, 'pre_m14_audit'::text, 'pre_runtime_release_audit'::text, 'regression_audit'::text])))` |
| CHECK | `chain_audit_evidence_input_substrate_snapshot_hash_check` | `CHECK ((input_substrate_snapshot_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `chain_audit_evidence_target_kind_code_check` | `CHECK ((target_kind_code = ANY (ARRAY['mc'::text, 'mcv'::text, 'tenant_binding'::text, 'business_concept'::text, 'entity'::text])))` |
| CHECK | `chain_audit_evidence_verdict_code_check` | `CHECK ((verdict_code = ANY (ARRAY['PASS'::text, 'FAIL'::text, 'OPERATOR_REVIEW'::text, 'NOT_APPLICABLE'::text])))` |
| PK | `chain_audit_evidence_pkey` | `PRIMARY KEY (audit_evidence_uid)` |

Triggers:

- `trg_cae_role_check`: `trg_cae_role_check BEFORE INSERT ON mcf.chain_audit_evidence FOR EACH ROW EXECUTE FUNCTION mcf.fn_cae_insert_role_check()`

### `mcf.chain_enrichment_plan`

Columns: 12 | **NOT NULL:** `plan_uid`, `mode_code`, `target_kind_code`, `target_ref_json`, `status_code`, `plan_json`, `planner_version`, `evidence_json`, `created_by_sub`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chain_enrichment_plan_emitted_packet_hash_check` | `CHECK (((emitted_packet_hash IS NULL) OR (emitted_packet_hash ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| CHECK | `chain_enrichment_plan_mode_code_check` | `CHECK ((mode_code = ANY (ARRAY['source_contract_gap_plan'::text, 'admission_contract_gap_plan'::text, 'observation_contract_gap_plan'::text])))` |
| CHECK | `chain_enrichment_plan_status_code_check` | `CHECK ((status_code = ANY (ARRAY['sc_gap_satisfied'::text, 'sc_create_proposed'::text, 'ac_gap_satisfied'::text, 'ac_create_proposed'::text, 'blocked_ac_parent_sc_missing'::text, 'oc_gap_satisfied'::text, 'oc_create_proposed'::text, 'oc_create_proposed_not_applyable'::text, 'blocked_oc_parent_sc_missing'::text, 'blocked_oc_parent_ac_missing'::text, 'blocked_bcf_prerequisites_missing'::text, 'blocked_out_of_scope'::text, 'blocked_input_invalid'::text])))` |
| CHECK | `chain_enrichment_plan_target_kind_code_check` | `CHECK ((target_kind_code = ANY (ARRAY['source_contract_gap_plan'::text, 'admission_contract_gap_plan'::text, 'observation_contract_gap_plan'::text])))` |
| PK | `chain_enrichment_plan_pkey` | `PRIMARY KEY (plan_uid)` |

### `mcf.evidence_source_allowlist`

Columns: 6 | **NOT NULL:** `evidence_source_uid`, `source_code`, `source_version`, `effective_from`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mesa_effective_to_chk` | `CHECK (((effective_to IS NULL) OR (effective_to > effective_from)))` |
| PK | `evidence_source_allowlist_pkey` | `PRIMARY KEY (evidence_source_uid)` |

### `mcf.exactness_reproof_evidence`

Columns: 15 | **NOT NULL:** `exactness_reproof_uid`, `metric_contract_version_uid`, `package_signature_hash`, `prover_algorithm_version`, `domain_policy_version`, `domain_policy_digest`, `numeric_representation_version`, `verdict_code`, `reasons_json`, `proof_json`, `is_byte_identity_verified`, `executed_by_name`, `executed_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `ck_exactness_reproof_byte_identity` | `CHECK ((is_byte_identity_verified = true))` |
| CHECK | `ck_exactness_reproof_class_prover_pairing` | `CHECK ((((verdict_code = 'EXACT'::text) AND (prover_algorithm_version = 'mcf-exactness-v2'::text)) OR ((verdict_code = 'REPRODUCIBLE'::text) AND (prover_algorithm_version = 'mcf-reproducibility-v1'::text)) OR ((verdict_code = 'NOT_PROVEN'::text) AND (prover_algorithm_version = ANY (ARRAY['mcf-exactness-v2'::text, 'mcf-reproducibility-v1'::text])))))` |
| CHECK | `ck_exactness_reproof_prong_b_payload` | `CHECK ((((verdict_code = 'REPRODUCIBLE'::text) AND (rounding_event_count IS NOT NULL) AND (rounding_event_count >= 0) AND (operation_trace_digest ~ '^sha256:[0-9a-f]{64}$'::text)) OR ((verdict_code <> 'REPRODUCIBLE'::text) AND (rounding_event_count IS NULL) AND (operation_trace_digest IS NULL))))` |
| CHECK | `exactness_reproof_evidence_numeric_representation_version_check` | `CHECK ((numeric_representation_version = 'scaled-decimal-int-v1'::text))` |
| CHECK | `exactness_reproof_evidence_verdict_code_check` | `CHECK ((verdict_code = ANY (ARRAY['EXACT'::text, 'NOT_PROVEN'::text, 'REPRODUCIBLE'::text])))` |
| FK | `fk_exactness_reproof_evidence_mcv` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| PK | `exactness_reproof_evidence_pkey` | `PRIMARY KEY (exactness_reproof_uid)` |
| UNIQUE | `uq_exactness_reproof_identity` | `UNIQUE (package_signature_hash, prover_algorithm_version, domain_policy_digest, numeric_representation_version)` |

Triggers:

- `trg_exactness_reproof_append_only`: `trg_exactness_reproof_append_only BEFORE DELETE OR UPDATE ON mcf.exactness_reproof_evidence FOR EACH ROW EXECUTE FUNCTION mcf.fn_exactness_reproof_append_only()`

### `mcf.formula_explanation_binding`

Columns: 19 | **NOT NULL:** `binding_uid`, `metric_contract_version_uid`, `formula_intent_hash`, `formula_ast_digest`, `authored_intent_json`, `authored_intent_digest`, `rendered_explanation_text`, `rendered_explanation_digest`, `renderer_version`, `revision_count_at_binding`, `attestation_cert_id`, `attestation_kind`, `origin_kind`, `binding_digest`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_feb_origin` | `CHECK (((origin_kind = 'approval'::text) AND (attestation_kind = 'metric_approve'::text) AND (backfill_run_uid IS NULL)))` |
| CHECK | `formula_explanation_binding_attestation_kind_check` | `CHECK ((attestation_kind = ANY (ARRAY['metric_approve'::text, 'metric_transition_backfill'::text])))` |
| CHECK | `formula_explanation_binding_authored_intent_digest_check` | `CHECK ((authored_intent_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `formula_explanation_binding_binding_digest_check` | `CHECK ((binding_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `formula_explanation_binding_formula_ast_digest_check` | `CHECK ((formula_ast_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `formula_explanation_binding_origin_kind_check` | `CHECK ((origin_kind = ANY (ARRAY['approval'::text, 'backfill'::text])))` |
| CHECK | `formula_explanation_binding_rendered_explanation_digest_check` | `CHECK ((rendered_explanation_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `formula_explanation_binding_revision_count_at_binding_check` | `CHECK ((revision_count_at_binding >= 0))` |
| FK | `formula_explanation_binding_attestation_cert_id_fkey` | `FOREIGN KEY (attestation_cert_id) REFERENCES mcf.certification_record(certification_record_id)` |
| FK | `formula_explanation_binding_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| FK | `formula_explanation_binding_supersedes_binding_uid_fkey` | `FOREIGN KEY (supersedes_binding_uid) REFERENCES mcf.formula_explanation_binding(binding_uid)` |
| PK | `formula_explanation_binding_pkey` | `PRIMARY KEY (binding_uid)` |
| t | `trg_feb_attestation_exact` | `TRIGGER DEFERRABLE INITIALLY DEFERRED` |
| t | `trg_feb_lineage` | `TRIGGER DEFERRABLE INITIALLY DEFERRED` |
| UNIQUE | `formula_explanation_binding_binding_digest_key` | `UNIQUE (binding_digest)` |

Triggers:

- `trg_feb_attestation_exact`: `CREATE CONSTRAINT TRIGGER trg_feb_attestation_exact AFTER INSERT ON mcf.formula_explanation_binding DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION mcf.fn_feb_attestation_exact()`
- `trg_feb_immutable`: `trg_feb_immutable BEFORE DELETE OR UPDATE ON mcf.formula_explanation_binding FOR EACH ROW EXECUTE FUNCTION mcf.fn_feb_immutable()`
- `trg_feb_lineage`: `CREATE CONSTRAINT TRIGGER trg_feb_lineage AFTER INSERT ON mcf.formula_explanation_binding DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION mcf.fn_feb_lineage()`

### `mcf.mcv_chain_status`

Columns: 6 | **NOT NULL:** `metric_contract_version_uid`, `mc_name`, `verdict_code`, `checks_json`, `evaluator_version_current`, `computed_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mcv_chain_status_verdict_code_check` | `CHECK ((verdict_code = ANY (ARRAY['green'::text, 'amber'::text, 'red'::text])))` |
| PK | `mcv_chain_status_pkey` | `PRIMARY KEY (metric_contract_version_uid)` |

### `mcf.mcv_closure_dependency`

Columns: 5 | **NOT NULL:** `closure_dependency_uid`, `dependent_mcv`, `dependency_kind`, `dependency_uid`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mcv_closure_dependency_dependency_kind_check` | `CHECK ((dependency_kind = ANY (ARRAY['metric_input'::text, 'business_concept_version'::text, 'entity_version'::text])))` |
| FK | `mcv_closure_dependency_dependent_mcv_fkey` | `FOREIGN KEY (dependent_mcv) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| PK | `mcv_closure_dependency_pkey` | `PRIMARY KEY (closure_dependency_uid)` |
| UNIQUE | `mcv_closure_dependency_dependent_mcv_dependency_kind_depend_key` | `UNIQUE (dependent_mcv, dependency_kind, dependency_uid)` |

### `mcf.mcv_package_snapshot`

Columns: 35 | **NOT NULL:** `mcv_package_snapshot_uid`, `metric_contract_version_uid`, `disposition_code`, `disposition_source`, `computed_at`, `frozen_by`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_mcv_package_snapshot_disposition_xor` | `CHECK ((((disposition_code = 'computed'::text) AND (canonical_package_bytes IS NOT NULL) AND (package_signature_hash IS NOT NULL) AND (hash_algorithm_version IS NOT NULL) AND (metric_contract_uid IS NOT NULL) AND (version_code IS NOT NULL) AND (formula_ast_hash IS NOT NULL) AND (bindings_digest IS NOT NULL) AND (filters_digest IS NOT NULL) AND (computed_dimensions_digest IS NOT NULL) AND (temporal_gate_digest IS NOT NULL) AND (grain_entity_id IS NOT NULL) AND (grain_entity_version_id IS NOT NULL) AND (output_digest IS NOT NULL) AND (aggregation_currency_code IS NOT NULL) AND (thresholds_digest IS NOT NULL) AND (input_domain_digest IS NOT NULL) AND (resolved_policy_digest IS NOT NULL) AND (eval_policy_rulebook_version IS NOT NULL) AND (eval_policy_rulebook_digest IS NOT NULL) AND (execution_engine_version IS NOT NULL) AND (numeric_representation_version IS NOT NULL) AND (exactness_result IS NOT NULL) AND (exactness_algorithm_version IS NOT NULL) AND (exactness_ast_hash IS NOT NULL) AND (exactness_reasons IS NOT NULL) AND (binary64_activation_eligible IS NOT NULL) AND (computable_false_reason_codes IS NULL)) OR ((disposition_code = 'not_computable'::text) AND (computable_false_reason_codes IS NOT NULL) AND mcf.fn_mcv_noncomputable_reasons_ok(computable_false_reason_codes) AND (canonical_package_bytes IS NULL) AND (package_signature_hash IS NULL) AND (hash_algorithm_version IS NULL) AND (metric_contract_uid IS NULL) AND (version_code IS NULL) AND (formula_ast_hash IS NULL) AND (bindings_digest IS NULL) AND (filters_digest IS NULL) AND (computed_dimensions_digest IS NULL) AND (temporal_gate_digest IS NULL) AND (grain_entity_id IS NULL) AND (grain_entity_version_id IS NULL) AND (output_digest IS NULL) AND (aggregation_currency_code IS NULL) AND (thresholds_digest IS NULL) AND (input_domain_digest IS NULL) AND (resolved_policy_digest IS NULL) AND (eval_policy_rulebook_version IS NULL) AND (eval_policy_rulebook_digest IS NULL) AND (execution_engine_version IS NULL) AND (numeric_representation_version IS NULL) AND (exactness_result IS NULL) AND (exactness_algorithm_version IS NULL) AND (exactness_ast_hash IS NULL) AND (exactness_reasons IS NULL) AND (binary64_activation_eligible IS NULL))))` |
| CHECK | `chk_mcv_package_snapshot_source_xor` | `CHECK ((((disposition_source = 'approval'::text) AND (approval_certification_id IS NOT NULL) AND (backfill_manifest_uid IS NULL)) OR ((disposition_source = 'backfill'::text) AND (backfill_manifest_uid IS NOT NULL) AND (approval_certification_id IS NULL))))` |
| CHECK | `mcv_package_snapshot_disposition_code_check` | `CHECK ((disposition_code = ANY (ARRAY['computed'::text, 'not_computable'::text])))` |
| CHECK | `mcv_package_snapshot_disposition_source_check` | `CHECK ((disposition_source = ANY (ARRAY['approval'::text, 'backfill'::text])))` |
| CHECK | `mcv_package_snapshot_package_signature_hash_check` | `CHECK ((package_signature_hash ~ '^sha256:[a-f0-9]{64}$'::text))` |
| FK | `mcv_package_snapshot_approval_certification_id_fkey` | `FOREIGN KEY (approval_certification_id) REFERENCES mcf.certification_record(certification_record_id)` |
| FK | `mcv_package_snapshot_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| PK | `mcv_package_snapshot_pkey` | `PRIMARY KEY (mcv_package_snapshot_uid)` |
| UNIQUE | `mcv_package_snapshot_metric_contract_version_uid_key` | `UNIQUE (metric_contract_version_uid)` |

Triggers:

- `trg_mcv_package_snapshot_guard`: `trg_mcv_package_snapshot_guard BEFORE INSERT ON mcf.mcv_package_snapshot FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcv_package_snapshot_guard()`
- `trg_mcv_package_snapshot_immutable`: `trg_mcv_package_snapshot_immutable BEFORE DELETE OR UPDATE ON mcf.mcv_package_snapshot FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcv_package_snapshot_immutability()`

### `mcf.metric_audit_relation`

Columns: 11 | **NOT NULL:** `relation_uid`, `relation_name`, `relation_kind`, `component_mc_uids`, `tolerance`, `is_active`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `metric_audit_relation_relation_kind_check` | `CHECK ((relation_kind = ANY (ARRAY['sum_equals'::text, 'sum_equals_constant'::text, 'ratio_of'::text])))` |
| PK | `metric_audit_relation_pkey` | `PRIMARY KEY (relation_uid)` |
| UNIQUE | `metric_audit_relation_relation_name_key` | `UNIQUE (relation_name)` |

### `mcf.metric_authoring_intake_queue`

Columns: 14 | **NOT NULL:** `intake_queue_uid`, `reservoir_name`, `reservoir_entry_id`, `reservoir_provenance_source_json`, `reservoir_confidence_band`, `candidate_name`, `candidate_description_text`, `normalized_candidate_json`, `co_bindings_stripped_flag`, `status_code`, `ingested_at`, `ingested_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `maiq_co_bindings_rejection_chk` | `CHECK ((NOT ((normalized_candidate_json)::text ~ '"co_bindings"\s*:'::text)))` |
| CHECK | `maiq_co_bindings_stripped_flag_chk` | `CHECK ((co_bindings_stripped_flag = true))` |
| CHECK | `maiq_confidence_band_chk` | `CHECK ((reservoir_confidence_band = ANY (ARRAY['high'::text, 'medium'::text, 'low'::text])))` |
| CHECK | `maiq_rejected_status_requires_reason_chk` | `CHECK (((status_code <> 'rejected'::text) OR ((status_reason_text IS NOT NULL) AND (char_length(status_reason_text) >= 20))))` |
| CHECK | `maiq_reservoir_name_chk` | `CHECK ((reservoir_name = ANY (ARRAY['seed_metrics'::text, 'metric_definition'::text, 'operator_direct'::text])))` |
| CHECK | `maiq_status_code_chk` | `CHECK ((status_code = ANY (ARRAY['pending'::text, 'consumed_by_panel'::text, 'rejected'::text, 'superseded'::text])))` |
| PK | `metric_authoring_intake_queue_pkey` | `PRIMARY KEY (intake_queue_uid)` |
| UNIQUE | `uq_maiq_reservoir_entry` | `UNIQUE (reservoir_name, reservoir_entry_id)` |

### `mcf.metric_authoring_panel_run`

Columns: 8 | **NOT NULL:** `panel_run_uid`, `workbench_fingerprint_hash`, `consensus_payload_json`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mapr_reservoir_all_or_none_chk` | `CHECK ((((reservoir_name IS NULL) AND (reservoir_entry_id IS NULL) AND (reservoir_provenance_source_json IS NULL) AND (reservoir_confidence_band IS NULL)) OR ((reservoir_name IS NOT NULL) AND (reservoir_entry_id IS NOT NULL) AND (reservoir_provenance_source_json IS NOT NULL) AND (reservoir_confidence_band IS NOT NULL))))` |
| CHECK | `mapr_reservoir_confidence_band_chk` | `CHECK (((reservoir_confidence_band IS NULL) OR (reservoir_confidence_band = ANY (ARRAY['high'::text, 'medium'::text, 'low'::text]))))` |
| CHECK | `mapr_workbench_fp_hash_fmt_chk` | `CHECK ((workbench_fingerprint_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| FK | `fk_mapr_panel_run` | `FOREIGN KEY (panel_run_uid) REFERENCES bcf.panel_output_record(panel_run_uid) ON DELETE RESTRICT` |
| PK | `metric_authoring_panel_run_pkey` | `PRIMARY KEY (panel_run_uid)` |

### `mcf.metric_authoring_panel_transcript`

Columns: 6 | **NOT NULL:** `transcript_uid`, `panel_run_uid`, `model_role_code`, `model_identity_json`, `transcript_payload_json`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mapt_model_role_chk` | `CHECK ((model_role_code = ANY (ARRAY['maker'::text, 'checker'::text, 'moderator'::text])))` |
| FK | `fk_mapt_panel_run` | `FOREIGN KEY (panel_run_uid) REFERENCES mcf.metric_authoring_panel_run(panel_run_uid) ON DELETE RESTRICT` |
| PK | `metric_authoring_panel_transcript_pkey` | `PRIMARY KEY (transcript_uid)` |
| UNIQUE | `uq_mapt_run_role` | `UNIQUE (panel_run_uid, model_role_code)` |

Triggers:

- `trg_mapt_immutability`: `trg_mapt_immutability BEFORE DELETE OR UPDATE ON mcf.metric_authoring_panel_transcript FOR EACH ROW EXECUTE FUNCTION mcf.fn_mapt_immutability_check()`

### `mcf.metric_cert_writer_idempotency`

Columns: 7 | **NOT NULL:** `idempotency_key`, `action_code`, `status`, `created_at`, `updated_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mcwi_status_chk` | `CHECK ((status = ANY (ARRAY['pending'::text, 'committed'::text, 'rolled_back'::text])))` |
| PK | `metric_cert_writer_idempotency_pkey` | `PRIMARY KEY (idempotency_key)` |

### `mcf.metric_computed_dimension_ref`

Columns: 10 | **NOT NULL:** `metric_computed_dimension_ref_uid`, `metric_contract_version_uid`, `dimension_class_code`, `resolver_config_ref_json`, `resolver_params_hash`, `role_in_formula_code`, `structural_sort_key`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mcdr_dimension_class_chk` | `CHECK ((dimension_class_code = ANY (ARRAY['fiscal_period'::text, 'fiscal_year'::text, 'fiscal_quarter'::text, 'calendar_quarter'::text, 'calendar_week_iso'::text, 'derived_grain'::text, 'bucket_label'::text, 'reference_dimension'::text])))` |
| CHECK | `mcdr_role_in_formula_chk` | `CHECK ((role_in_formula_code = ANY (ARRAY['grain'::text, 'filter'::text, 'group_by'::text])))` |
| FK | `fk_mcdr_mcv` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| PK | `metric_computed_dimension_ref_pkey` | `PRIMARY KEY (metric_computed_dimension_ref_uid)` |

Triggers:

- `trg_mcdr_c5_insert_freeze`: `trg_mcdr_c5_insert_freeze BEFORE INSERT ON mcf.metric_computed_dimension_ref FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcdr_active_immutability_check()`
- `trg_mcf_mcdr_active_immutability`: `trg_mcf_mcdr_active_immutability BEFORE DELETE OR UPDATE ON mcf.metric_computed_dimension_ref FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcdr_active_immutability_check()`

### `mcf.metric_contract`

Columns: 17 | **NOT NULL:** `metric_contract_uid`, `mc_name`, `grain_entity_id`, `temporal_gate_shape_code`, `created_at`, `updated_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mc_candidate_source_type_chk` | `CHECK (((candidate_source_ref_json IS NULL) OR ((candidate_source_ref_json ->> 'source_type'::text) = ANY (ARRAY['seed_metrics'::text, 'metric_definition'::text, 'operator_direct'::text, 'legacy_metric_contract'::text, 'other'::text]))))` |
| CHECK | `mc_filter_set_hash_fmt_chk` | `CHECK (((filter_set_hash IS NULL) OR (filter_set_hash ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| CHECK | `mc_formula_intent_hash_fmt_chk` | `CHECK (((formula_intent_hash IS NULL) OR (formula_intent_hash ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| CHECK | `mc_hash_algorithm_version_chk` | `CHECK (((hash_algorithm_version IS NULL) OR (hash_algorithm_version ~ '^mcf-[a-z-]+-v[0-9]+$'::text)))` |
| CHECK | `mc_identity_tuple_hash_fmt_chk` | `CHECK (((identity_tuple_hash IS NULL) OR (identity_tuple_hash ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| CHECK | `mc_package_signature_hash_fmt_chk` | `CHECK (((package_signature_hash IS NULL) OR (package_signature_hash ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| CHECK | `mc_temporal_gate_shape_chk` | `CHECK ((temporal_gate_shape_code = ANY (ARRAY['instantaneous'::text, 'trailing_window'::text, 'period_aggregate'::text, 'point_in_time'::text, 'as_of'::text, 'cumulative_to_date'::text, 'rolling_window'::text])))` |
| CHECK | `mc_variable_binding_set_hash_fmt_chk` | `CHECK (((variable_binding_set_hash IS NULL) OR (variable_binding_set_hash ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| PK | `metric_contract_pkey` | `PRIMARY KEY (metric_contract_uid)` |

Triggers:

- `trg_mc_grain_freeze_guard`: `trg_mc_grain_freeze_guard BEFORE UPDATE ON mcf.metric_contract FOR EACH ROW EXECUTE FUNCTION mcf.fn_mc_grain_freeze_guard()`
- `trg_mcf_mc_active_immutability`: `trg_mcf_mc_active_immutability BEFORE UPDATE ON mcf.metric_contract FOR EACH ROW EXECUTE FUNCTION mcf.fn_mc_active_immutability_check()`

### `mcf.metric_contract_revision`

Columns: 9 | **NOT NULL:** `revision_uid`, `metric_contract_version_uid`, `revision_seq`, `revision_kind_code`, `changed_fields_json`, `revised_by_name`, `revised_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mcr_revision_kind_chk` | `CHECK ((revision_kind_code = ANY (ARRAY['display_name_change'::text, 'threshold_change'::text, 'owner_change'::text, 'function_code_change'::text, 'description_change'::text, 'tags_change'::text, 'other'::text])))` |
| CHECK | `mcr_revision_seq_chk` | `CHECK ((revision_seq > 0))` |
| FK | `fk_mcr_mcv` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| FK | `fk_mcr_panel_run` | `FOREIGN KEY (panel_run_uid) REFERENCES bcf.panel_output_record(panel_run_uid) ON DELETE RESTRICT` |
| PK | `metric_contract_revision_pkey` | `PRIMARY KEY (revision_uid)` |

### `mcf.metric_contract_version`

Columns: 18 | **NOT NULL:** `metric_contract_version_uid`, `metric_contract_uid`, `version_code`, `version_seq`, `is_current`, `function_code`, `subfunction_code`, `governance_state_code`, `created_at`, `formula_ast_canonical_json`, `aggregation_currency_code`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mcv_aggregation_currency_chk` | `CHECK ((aggregation_currency_code = ANY (ARRAY['document_currency'::text, 'single_currency_required'::text, 'local_currency'::text, 'not_applicable'::text])))` |
| CHECK | `mcv_governance_state_chk` | `CHECK ((governance_state_code = ANY (ARRAY['draft'::text, 'review'::text, 'approved'::text, 'active'::text, 'superseded'::text, 'audit_pending'::text, 'audit_blocked'::text])))` |
| CHECK | `mcv_version_seq_chk` | `CHECK ((version_seq > 0))` |
| FK | `fk_mcv_classification_subfunction` | `FOREIGN KEY (function_code, subfunction_code) REFERENCES master.master_subfunction(parent_function, slug) ON DELETE RESTRICT` |
| FK | `fk_mcv_mc` | `FOREIGN KEY (metric_contract_uid) REFERENCES mcf.metric_contract(metric_contract_uid) ON DELETE RESTRICT` |
| FK | `fk_mcv_supersedes_version` | `FOREIGN KEY (supersedes_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| FK | `metric_contract_version_grain_entity_version_id_fkey` | `FOREIGN KEY (grain_entity_version_id) REFERENCES concept_registry.entity_version(entity_version_id)` |
| PK | `metric_contract_version_pkey` | `PRIMARY KEY (metric_contract_version_uid)` |

Triggers:

- `trg_mcf_mcv_descriptive_immutability`: `trg_mcf_mcv_descriptive_immutability BEFORE UPDATE ON mcf.metric_contract_version FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcv_descriptive_immutability_check()`
- `trg_mcf_mcv_revision_emit`: `trg_mcf_mcv_revision_emit AFTER UPDATE ON mcf.metric_contract_version FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcv_revision_emit()`
- `trg_mcf_mcv_state_transition`: `trg_mcf_mcv_state_transition BEFORE INSERT OR UPDATE OF governance_state_code ON mcf.metric_contract_version FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcv_state_transition_check()`
- `trg_mcv_c5_package_identity_freeze`: `trg_mcv_c5_package_identity_freeze BEFORE UPDATE ON mcf.metric_contract_version FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcv_package_identity_immutability_check()`
- `trg_mcv_grain_entity_version_guard`: `trg_mcv_grain_entity_version_guard BEFORE INSERT OR UPDATE ON mcf.metric_contract_version FOR EACH ROW EXECUTE FUNCTION mcf.fn_mcv_grain_entity_version_guard()`

### `mcf.metric_filter_clause`

Columns: 10 | **NOT NULL:** `metric_filter_clause_uid`, `metric_contract_version_uid`, `clause_role_code`, `clause_expression_json`, `operator_code`, `structural_sort_key`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mfc_clause_role_chk` | `CHECK ((clause_role_code = ANY (ARRAY['where'::text, 'having'::text, 'pre_filter'::text])))` |
| CHECK | `mfc_operator_chk` | `CHECK ((operator_code = ANY (ARRAY['eq'::text, 'ne'::text, 'lt'::text, 'lte'::text, 'gt'::text, 'gte'::text, 'in'::text, 'not_in'::text, 'is_null'::text, 'is_not_null'::text, 'between'::text])))` |
| CHECK | `mfc_operator_literal_chk` | `CHECK ((((operator_code = ANY (ARRAY['is_null'::text, 'is_not_null'::text])) AND (literal_value_json IS NULL)) OR ((operator_code <> ALL (ARRAY['is_null'::text, 'is_not_null'::text])) AND (literal_value_json IS NOT NULL))))` |
| FK | `fk_mfc_mcv` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| PK | `metric_filter_clause_pkey` | `PRIMARY KEY (metric_filter_clause_uid)` |

Triggers:

- `trg_mcf_mfc_active_immutability`: `trg_mcf_mfc_active_immutability BEFORE DELETE OR UPDATE ON mcf.metric_filter_clause FOR EACH ROW EXECUTE FUNCTION mcf.fn_mfc_active_immutability_check()`
- `trg_mfc_c5_insert_freeze`: `trg_mfc_c5_insert_freeze BEFORE INSERT ON mcf.metric_filter_clause FOR EACH ROW EXECUTE FUNCTION mcf.fn_mfc_active_immutability_check()`

### `mcf.metric_knowledge_profile`

Columns: 15 | **NOT NULL:** `knowledge_profile_uid`, `metric_contract_uid`, `panel_run_uid`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mkp_acceptance_rationale_len_chk` | `CHECK (((acceptance_rationale_text IS NULL) OR (char_length(acceptance_rationale_text) >= 40)))` |
| FK | `fk_metric_knowledge_profile_mc` | `FOREIGN KEY (metric_contract_uid) REFERENCES mcf.metric_contract(metric_contract_uid)` |
| FK | `fk_metric_knowledge_profile_panel_run` | `FOREIGN KEY (panel_run_uid) REFERENCES mcf.metric_authoring_panel_run(panel_run_uid)` |
| PK | `metric_knowledge_profile_pkey` | `PRIMARY KEY (knowledge_profile_uid)` |
| UNIQUE | `uq_mkp_mc_panel_run` | `UNIQUE (metric_contract_uid, panel_run_uid)` |

### `mcf.metric_publication_eligibility_result`

Columns: 10 | **NOT NULL:** `pe_result_uid`, `metric_contract_version_uid`, `pe_check_code`, `verdict_code`, `evidence_json`, `evaluated_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mper_pe_check_code_chk` | `CHECK ((pe_check_code = ANY (ARRAY['PE-MC-1'::text, 'PE-MC-2'::text, 'PE-MC-3'::text, 'PE-MC-4'::text, 'PE-MC-5'::text, 'PE-MC-6'::text, 'PE-MC-7'::text, 'PE-MC-8'::text, 'PE-MC-9'::text, 'PE-MC-10'::text, 'PE-MC-11'::text, 'PE-MC-12'::text, 'PE-MC-13'::text, 'PE-MC-14'::text, 'PE-MC-15'::text, 'PE-MC-16'::text])))` |
| CHECK | `mper_verdict_code_chk` | `CHECK ((verdict_code = ANY (ARRAY['PASS'::text, 'REJECT'::text, 'OPERATOR_REVIEW'::text])))` |
| FK | `fk_mper_cert` | `FOREIGN KEY (certification_record_id) REFERENCES mcf.certification_record(certification_record_id) ON DELETE RESTRICT` |
| FK | `fk_mper_mcv` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| FK | `fk_mper_panel_run` | `FOREIGN KEY (panel_run_uid) REFERENCES bcf.panel_output_record(panel_run_uid) ON DELETE RESTRICT` |
| FK | `fk_mper_verification_result` | `FOREIGN KEY (satisfying_verification_result_uid) REFERENCES mcf.metric_self_verification_result(verification_result_uid) ON DELETE RESTRICT` |
| PK | `metric_publication_eligibility_result_pkey` | `PRIMARY KEY (pe_result_uid)` |

### `mcf.metric_self_verification_fixture`

Columns: 16 | **NOT NULL:** `fixture_uid`, `metric_contract_uid`, `metric_contract_version_uid`, `section_a_inputs_json`, `section_b_expected_output_json`, `section_c_resolver_config_json`, `formula_intent_hash`, `variable_binding_set_hash`, `grain_filter_temporal_dimension_signature_hash`, `self_verification_fixture_hash`, `bound_package_signature_hash`, `hash_algorithm_version`, `rationale_text`, `authored_by_name`, `panel_run_uid`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `msvf_bound_package_signature_hash_fmt_chk` | `CHECK ((bound_package_signature_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `msvf_formula_intent_hash_fmt_chk` | `CHECK ((formula_intent_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `msvf_grain_filter_temporal_dim_sig_hash_fmt_chk` | `CHECK ((grain_filter_temporal_dimension_signature_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `msvf_hash_algorithm_version_chk` | `CHECK ((hash_algorithm_version ~ '^mcf-[a-z-]+-v[0-9]+$'::text))` |
| CHECK | `msvf_rationale_min_length_chk` | `CHECK ((length(rationale_text) >= 40))` |
| CHECK | `msvf_self_verification_fixture_hash_fmt_chk` | `CHECK ((self_verification_fixture_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `msvf_variable_binding_set_hash_fmt_chk` | `CHECK ((variable_binding_set_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| FK | `fk_msvf_mc` | `FOREIGN KEY (metric_contract_uid) REFERENCES mcf.metric_contract(metric_contract_uid) ON DELETE RESTRICT` |
| FK | `fk_msvf_mcv` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| FK | `fk_msvf_panel_run` | `FOREIGN KEY (panel_run_uid) REFERENCES mcf.metric_authoring_panel_run(panel_run_uid) ON DELETE RESTRICT` |
| PK | `metric_self_verification_fixture_pkey` | `PRIMARY KEY (fixture_uid)` |
| UNIQUE | `uq_msvf_mcv_fixture_hash` | `UNIQUE (metric_contract_version_uid, self_verification_fixture_hash)` |

Triggers:

- `trg_msvf_immutability`: `trg_msvf_immutability BEFORE DELETE OR UPDATE ON mcf.metric_self_verification_fixture FOR EACH ROW EXECUTE FUNCTION mcf.fn_msvf_immutability_check()`

### `mcf.metric_self_verification_result`

Columns: 13 | **NOT NULL:** `verification_result_uid`, `fixture_uid`, `metric_contract_uid`, `metric_contract_version_uid`, `verdict_code`, `verdict_payload_json`, `bound_package_signature_hash_at_run`, `fixture_bound_package_signature_hash`, `stale_fixture_flag`, `verifier_algorithm_version`, `executor_identity_text`, `executed_at`, `execution_duration_ms`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `msvr_algorithm_version_chk` | `CHECK ((verifier_algorithm_version ~ '^mcf-[a-z-]+-v[0-9]+$'::text))` |
| CHECK | `msvr_bound_pkg_hash_at_run_fmt_chk` | `CHECK ((bound_package_signature_hash_at_run ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `msvr_duration_non_negative_chk` | `CHECK ((execution_duration_ms >= 0))` |
| CHECK | `msvr_fixture_bound_pkg_hash_fmt_chk` | `CHECK ((fixture_bound_package_signature_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `msvr_verdict_code_chk` | `CHECK ((verdict_code = ANY (ARRAY['pass'::text, 'fail'::text, 'structural_reject'::text])))` |
| FK | `fk_msvr_fixture` | `FOREIGN KEY (fixture_uid) REFERENCES mcf.metric_self_verification_fixture(fixture_uid) ON DELETE RESTRICT` |
| FK | `fk_msvr_mc` | `FOREIGN KEY (metric_contract_uid) REFERENCES mcf.metric_contract(metric_contract_uid) ON DELETE RESTRICT` |
| FK | `fk_msvr_mcv` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| PK | `metric_self_verification_result_pkey` | `PRIMARY KEY (verification_result_uid)` |
| UNIQUE | `uq_msvr_fixture_version_pkg_hash` | `UNIQUE (fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` |

Triggers:

- `trg_msvr_immutability`: `trg_msvr_immutability BEFORE DELETE OR UPDATE ON mcf.metric_self_verification_result FOR EACH ROW EXECUTE FUNCTION mcf.fn_msvr_immutability_check()`

### `mcf.metric_supersession`

Columns: 11 | **NOT NULL:** `supersession_uid`, `predecessor_metric_contract_uid`, `predecessor_metric_contract_version_uid`, `successor_metric_contract_uid`, `successor_metric_contract_version_uid`, `correction_class_code`, `operator_sub`, `rationale_text`, `certification_record_id`, `superseded_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mcs_correction_class_chk` | `CHECK ((correction_class_code = ANY (ARRAY['editorial'::text, 'meaning_bearing'::text])))` |
| CHECK | `mcs_different_mc_chk` | `CHECK ((predecessor_metric_contract_uid <> successor_metric_contract_uid))` |
| CHECK | `mcs_rationale_min_length_chk` | `CHECK ((length(rationale_text) >= 40))` |
| FK | `fk_mcs_cert` | `FOREIGN KEY (certification_record_id) REFERENCES mcf.certification_record(certification_record_id) ON DELETE RESTRICT` |
| FK | `fk_mcs_panel_run` | `FOREIGN KEY (panel_run_uid) REFERENCES bcf.panel_output_record(panel_run_uid) ON DELETE RESTRICT` |
| FK | `fk_mcs_pred_mc` | `FOREIGN KEY (predecessor_metric_contract_uid) REFERENCES mcf.metric_contract(metric_contract_uid) ON DELETE RESTRICT` |
| FK | `fk_mcs_pred_mcv` | `FOREIGN KEY (predecessor_metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| FK | `fk_mcs_succ_mc` | `FOREIGN KEY (successor_metric_contract_uid) REFERENCES mcf.metric_contract(metric_contract_uid) ON DELETE RESTRICT` |
| FK | `fk_mcs_succ_mcv` | `FOREIGN KEY (successor_metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| PK | `metric_supersession_pkey` | `PRIMARY KEY (supersession_uid)` |

### `mcf.metric_variable_binding`

Columns: 19 | **NOT NULL:** `metric_variable_binding_uid`, `metric_contract_version_uid`, `variable_role_code`, `role_kind_code`, `structural_sort_key`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mvb_role_kind_chk` | `CHECK ((role_kind_code = ANY (ARRAY['input'::text, 'output'::text, 'constant'::text, 'metric_input'::text])))` |
| CHECK | `mvb_role_target_chk` | `CHECK ((((role_kind_code = 'constant'::text) AND (constant_value_json IS NOT NULL) AND (bound_business_concept_id IS NULL) AND (bound_entity_id IS NULL) AND (bound_metric_contract_uid IS NULL)) OR ((role_kind_code = ANY (ARRAY['input'::text, 'output'::text])) AND (constant_value_json IS NULL) AND (bound_metric_contract_uid IS NULL) AND ((bound_business_concept_id IS NOT NULL) OR (bound_entity_id IS NOT NULL))) OR ((role_kind_code = 'metric_input'::text) AND (bound_metric_contract_uid IS NOT NULL) AND (snapshot_selection_rule_code IS NOT NULL) AND (constant_value_json IS NULL) AND (bound_business_concept_id IS NULL) AND (bound_entity_id IS NULL))))` |
| CHECK | `mvb_selection_rule_chk` | `CHECK (((snapshot_selection_rule_code IS NULL) OR (snapshot_selection_rule_code = ANY (ARRAY['as_of_period_end'::text, 'period_matched'::text, 'prior_period_end'::text]))))` |
| FK | `fk_mvb_bound_bc_version` | `FOREIGN KEY (bound_business_concept_version_id) REFERENCES concept_registry.business_concept_version(concept_version_id)` |
| FK | `fk_mvb_mcv` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| FK | `fk_mvb_upstream_mc` | `FOREIGN KEY (bound_metric_contract_uid) REFERENCES mcf.metric_contract(metric_contract_uid) ON DELETE RESTRICT` |
| FK | `metric_variable_binding_bound_entity_version_id_fkey` | `FOREIGN KEY (bound_entity_version_id) REFERENCES concept_registry.entity_version(entity_version_id)` |
| PK | `metric_variable_binding_pkey` | `PRIMARY KEY (metric_variable_binding_uid)` |

Triggers:

- `trg_binding_entity_version_guard`: `trg_binding_entity_version_guard BEFORE INSERT OR UPDATE ON mcf.metric_variable_binding FOR EACH ROW EXECUTE FUNCTION mcf.fn_binding_entity_version_guard()`
- `trg_mcf_mvb_active_immutability`: `trg_mcf_mvb_active_immutability BEFORE DELETE OR UPDATE ON mcf.metric_variable_binding FOR EACH ROW EXECUTE FUNCTION mcf.fn_mvb_active_immutability_check()`
- `trg_mvb_c5_insert_freeze`: `trg_mvb_c5_insert_freeze BEFORE INSERT ON mcf.metric_variable_binding FOR EACH ROW EXECUTE FUNCTION mcf.fn_mvb_active_immutability_check()`

### `mcf.role_grant_audit`

Columns: 13 | **NOT NULL:** `role_grant_uid`, `granted_at`, `granted_by_user_uid`, `granted_by_email_snapshot`, `target_user_uid`, `target_email_snapshot`, `roles_before_json`, `roles_after_json`, `mcf_roles_added_json`, `mcf_roles_removed_json`, `reason_text`, `source_pr_or_dbcp_text`, `cognito_request_id`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_role_grant_audit_diff_not_empty` | `CHECK (((jsonb_array_length(mcf_roles_added_json) + jsonb_array_length(mcf_roles_removed_json)) >= 1))` |
| CHECK | `chk_role_grant_audit_reason_min_length` | `CHECK ((char_length(reason_text) >= 20))` |
| CHECK | `chk_role_grant_audit_source_min_length` | `CHECK ((char_length(source_pr_or_dbcp_text) >= 10))` |
| PK | `role_grant_audit_pkey` | `PRIMARY KEY (role_grant_uid)` |

### `mcf.seed_metric`

Columns: 21 | **NOT NULL:** `seed_metric_id`, `mongo_id`, `metric_name`, `raw_json`, `source_hash`, `source_ref`, `imported_at`, `updated_at`, `status_code`, `status_updated_at`

| Kind | Name | Definition |
|---|---|---|
| PK | `seed_metric_pkey` | `PRIMARY KEY (seed_metric_id)` |
| UNIQUE | `uq_seed_metric_mongo_id` | `UNIQUE (mongo_id)` |

### `mcf.workspace_tool_allowlist`

Columns: 6 | **NOT NULL:** `tool_uid`, `tool_code`, `tool_version`, `effective_from`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `mwta_effective_to_chk` | `CHECK (((effective_to IS NULL) OR (effective_to > effective_from)))` |
| PK | `workspace_tool_allowlist_pkey` | `PRIMARY KEY (tool_uid)` |

## 5. Platform substrate constraints — `metric_directory`

### `metric_directory._m37_grant_ledger`

Columns: 2 | **NOT NULL:** `role_name`, `usage_preexisting`

| Kind | Name | Definition |
|---|---|---|
| PK | `_m37_grant_ledger_pkey` | `PRIMARY KEY (role_name)` |

### `metric_directory.directory_decision`

Columns: 9 | **NOT NULL:** `decision_id`, `decision_kind`, `audience_role`, `author_name`, `body_text`, `references_json`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_dd_audience` | `CHECK ((audience_role = ANY (ARRAY['operator'::text, 'advisor'::text, 'end_user'::text])))` |
| CHECK | `chk_dd_kind` | `CHECK ((decision_kind = ANY (ARRAY['rationale'::text, 'disposition'::text, 'deferral'::text, 'debate'::text, 'approval'::text, 'rejection'::text])))` |
| CHECK | `chk_dd_subject_exactly_one` | `CHECK (((((family_id IS NOT NULL))::integer + ((member_uid IS NOT NULL))::integer) = 1))` |
| FK | `fk_dd_family` | `FOREIGN KEY (family_id) REFERENCES metric_directory.family(family_id) ON DELETE CASCADE` |
| FK | `fk_dd_member` | `FOREIGN KEY (member_uid) REFERENCES metric_directory.member(member_uid) ON DELETE CASCADE` |
| PK | `directory_decision_pkey` | `PRIMARY KEY (decision_id)` |

Triggers:

- `trg_directory_decision_immutable`: `trg_directory_decision_immutable BEFORE DELETE OR UPDATE ON metric_directory.directory_decision FOR EACH ROW EXECUTE FUNCTION metric_directory.tg_directory_decision_immutable()`

### `metric_directory.family`

Columns: 11 | **NOT NULL:** `family_id`, `function_slug`, `subfunction_slug`, `theme_code`, `priority_code`, `created_at`, `updated_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_family_priority` | `CHECK ((priority_code = ANY (ARRAY['now'::text, 'next'::text, 'later'::text])))` |
| FK | `fk_family_subfunction` | `FOREIGN KEY (function_slug, subfunction_slug) REFERENCES master.master_subfunction(parent_function, slug)` |
| PK | `family_pkey` | `PRIMARY KEY (family_id)` |

Triggers:

- `trg_family_frozen`: `trg_family_frozen BEFORE UPDATE ON metric_directory.family FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_family_frozen_guard()`

### `metric_directory.family_industry`

Columns: 2 | **NOT NULL:** `family_id`, `industry_slug`

| Kind | Name | Definition |
|---|---|---|
| FK | `family_industry_family_id_fkey` | `FOREIGN KEY (family_id) REFERENCES metric_directory.family(family_id)` |
| FK | `family_industry_industry_slug_fkey` | `FOREIGN KEY (industry_slug) REFERENCES master.master_industry(slug)` |
| PK | `family_industry_pkey` | `PRIMARY KEY (family_id, industry_slug)` |

### `metric_directory.family_version`

Columns: 13 | **NOT NULL:** `family_version_uid`, `family_id`, `version_coordinate`, `function_slug`, `subfunction_slug`, `theme_code`, `decision_text`, `rationale_text`, `content_hash`, `canonicalization_version`, `created_at`, `created_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `family_version_version_coordinate_check` | `CHECK ((version_coordinate ~ '^v[0-9]+$'::text))` |
| FK | `family_version_family_id_fkey` | `FOREIGN KEY (family_id) REFERENCES metric_directory.family(family_id)` |
| FK | `fk_family_version_supersedes_same_anchor` | `FOREIGN KEY (family_id, supersedes_version_uid) REFERENCES metric_directory.family_version(family_id, family_version_uid)` |
| PK | `family_version_pkey` | `PRIMARY KEY (family_version_uid)` |
| UNIQUE | `uq_family_version_anchor` | `UNIQUE (family_id, family_version_uid)` |
| UNIQUE | `uq_family_version_coord` | `UNIQUE (family_id, version_coordinate)` |
| UNIQUE | `uq_family_version_supersedes` | `UNIQUE (supersedes_version_uid)` |

Triggers:

- `trg_family_version_head`: `trg_family_version_head BEFORE INSERT ON metric_directory.family_version FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_family_version_head_guard()`
- `trg_family_version_immutable`: `trg_family_version_immutable BEFORE DELETE OR UPDATE ON metric_directory.family_version FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`

### `metric_directory.group`

Columns: 11 | **NOT NULL:** `group_id`, `family_id`, `group_code`, `class_code`, `template_json`, `created_at`, `updated_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_group_class` | `CHECK ((class_code = ANY (ARRAY['base'::text, 'derived'::text])))` |
| FK | `group_family_id_fkey` | `FOREIGN KEY (family_id) REFERENCES metric_directory.family(family_id)` |
| FK | `group_grain_entity_id_fkey` | `FOREIGN KEY (grain_entity_id) REFERENCES concept_registry.entity(entity_id)` |
| FK | `group_temporal_anchor_concept_id_fkey` | `FOREIGN KEY (temporal_anchor_concept_id) REFERENCES concept_registry.business_concept(concept_id)` |
| PK | `group_pkey` | `PRIMARY KEY (group_id)` |

Triggers:

- `trg_group_frozen`: `trg_group_frozen BEFORE UPDATE ON metric_directory."group" FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_group_frozen_guard()`

### `metric_directory.group_version`

Columns: 15 | **NOT NULL:** `group_version_uid`, `group_id`, `family_id`, `family_version_uid`, `version_coordinate`, `group_code`, `class_code`, `grain_entity_id`, `content_hash`, `canonicalization_version`, `created_at`, `created_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `group_version_class_code_check` | `CHECK ((class_code = ANY (ARRAY['base'::text, 'derived'::text])))` |
| CHECK | `group_version_version_coordinate_check` | `CHECK ((version_coordinate ~ '^v[0-9]+$'::text))` |
| FK | `fk_group_version_family` | `FOREIGN KEY (family_id, family_version_uid) REFERENCES metric_directory.family_version(family_id, family_version_uid)` |
| FK | `fk_group_version_supersedes_same_anchor` | `FOREIGN KEY (group_id, supersedes_version_uid) REFERENCES metric_directory.group_version(group_id, group_version_uid)` |
| FK | `group_version_group_id_fkey` | `FOREIGN KEY (group_id) REFERENCES metric_directory."group"(group_id)` |
| PK | `group_version_pkey` | `PRIMARY KEY (group_version_uid)` |
| UNIQUE | `uq_group_version_anchor` | `UNIQUE (group_id, group_version_uid)` |
| UNIQUE | `uq_group_version_coord` | `UNIQUE (group_id, version_coordinate)` |
| UNIQUE | `uq_group_version_family_pair` | `UNIQUE (group_version_uid, family_version_uid)` |
| UNIQUE | `uq_group_version_supersedes` | `UNIQUE (supersedes_version_uid)` |

Triggers:

- `trg_group_version_head`: `trg_group_version_head BEFORE INSERT ON metric_directory.group_version FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_group_version_head_guard()`
- `trg_group_version_immutable`: `trg_group_version_immutable BEFORE DELETE OR UPDATE ON metric_directory.group_version FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`

### `metric_directory.member`

Columns: 17 | **NOT NULL:** `member_uid`, `group_id`, `member_code`, `display_name`, `class_code`, `discriminator_json`, `intent_state_code`, `created_at`, `updated_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `chk_member_blocked` | `CHECK (((intent_state_code = 'blocked'::text) = (blocker_code IS NOT NULL)))` |
| CHECK | `chk_member_class` | `CHECK ((class_code = ANY (ARRAY['base'::text, 'derived'::text])))` |
| CHECK | `chk_member_derivation_class` | `CHECK (((derivation_json IS NULL) OR (class_code = 'derived'::text)))` |
| CHECK | `chk_member_intent` | `CHECK ((intent_state_code = ANY (ARRAY['planned'::text, 'blocked'::text])))` |
| FK | `member_group_id_fkey` | `FOREIGN KEY (group_id) REFERENCES metric_directory."group"(group_id)` |
| FK | `member_measure_concept_id_fkey` | `FOREIGN KEY (measure_concept_id) REFERENCES concept_registry.business_concept(concept_id)` |
| FK | `member_realized_metric_contract_uid_fkey` | `FOREIGN KEY (realized_metric_contract_uid) REFERENCES mcf.metric_contract(metric_contract_uid)` |
| PK | `member_pkey` | `PRIMARY KEY (member_uid)` |

Triggers:

- `trg_member_frozen`: `trg_member_frozen BEFORE UPDATE ON metric_directory.member FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_member_frozen_guard()`
- `trg_member_legacy_pointer`: `trg_member_legacy_pointer BEFORE INSERT OR UPDATE ON metric_directory.member FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_legacy_pointer_freeze()`

### `metric_directory.member_feasibility_result`

Columns: 9 | **NOT NULL:** `result_uid`, `member_version_uid`, `dependency_set_hash`, `intent_state_code`, `resolved_bcv_set_json`, `evaluated_at`

| Kind | Name | Definition |
|---|---|---|
| FK | `member_feasibility_result_member_version_uid_fkey` | `FOREIGN KEY (member_version_uid) REFERENCES metric_directory.member_version(member_version_uid)` |
| FK | `member_feasibility_result_supersedes_result_uid_fkey` | `FOREIGN KEY (supersedes_result_uid) REFERENCES metric_directory.member_feasibility_result(result_uid)` |
| PK | `member_feasibility_result_pkey` | `PRIMARY KEY (result_uid)` |
| UNIQUE | `uq_feas_supersedes` | `UNIQUE (supersedes_result_uid)` |

Triggers:

- `trg_feasibility_head`: `trg_feasibility_head BEFORE INSERT ON metric_directory.member_feasibility_result FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_feasibility_head_guard()`
- `trg_member_feasibility_result_immutable`: `trg_member_feasibility_result_immutable BEFORE DELETE OR UPDATE ON metric_directory.member_feasibility_result FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`

### `metric_directory.member_knowledge`

Columns: 6 | **NOT NULL:** `member_uid`, `updated_at`

| Kind | Name | Definition |
|---|---|---|
| FK | `fk_member_knowledge_member` | `FOREIGN KEY (member_uid) REFERENCES metric_directory.member(member_uid) ON DELETE CASCADE` |
| PK | `member_knowledge_pkey` | `PRIMARY KEY (member_uid)` |

Triggers:

- `trg_member_knowledge_frozen`: `trg_member_knowledge_frozen BEFORE INSERT OR UPDATE ON metric_directory.member_knowledge FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_member_knowledge_frozen_guard()`

### `metric_directory.member_version`

Columns: 24 | **NOT NULL:** `member_version_uid`, `member_uid`, `group_id`, `group_version_uid`, `family_version_uid`, `version_coordinate`, `member_code`, `display_name`, `definition_text`, `formula_intent_text`, `class_code`, `grain_entity_id`, `grain_entity_version_id`, `temporal_intent_json`, `output_intent_json`, `decision_evidence_refs`, `content_hash`, `children_set_digest`, `children_set_digest_algorithm`, `canonicalization_version`, `creation_xid8`, `created_at`, `created_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `member_version_class_code_check` | `CHECK ((class_code = ANY (ARRAY['base'::text, 'derived'::text])))` |
| CHECK | `member_version_decision_evidence_refs_check` | `CHECK ((jsonb_array_length(decision_evidence_refs) >= 1))` |
| CHECK | `member_version_version_coordinate_check` | `CHECK ((version_coordinate ~ '^v[0-9]+$'::text))` |
| FK | `fk_member_version_grain_entity_version` | `FOREIGN KEY (grain_entity_id, grain_entity_version_id) REFERENCES concept_registry.entity_version(entity_id, entity_version_id)` |
| FK | `fk_member_version_group` | `FOREIGN KEY (group_id, group_version_uid) REFERENCES metric_directory.group_version(group_id, group_version_uid)` |
| FK | `fk_member_version_group_family_pair` | `FOREIGN KEY (group_version_uid, family_version_uid) REFERENCES metric_directory.group_version(group_version_uid, family_version_uid)` |
| FK | `fk_member_version_supersedes_same_anchor` | `FOREIGN KEY (member_uid, supersedes_version_uid) REFERENCES metric_directory.member_version(member_uid, member_version_uid)` |
| FK | `member_version_member_uid_fkey` | `FOREIGN KEY (member_uid) REFERENCES metric_directory.member(member_uid)` |
| PK | `member_version_pkey` | `PRIMARY KEY (member_version_uid)` |
| t | `trg_member_version_finalize` | `TRIGGER DEFERRABLE INITIALLY DEFERRED` |
| UNIQUE | `uq_member_version_anchor` | `UNIQUE (member_uid, member_version_uid)` |
| UNIQUE | `uq_member_version_coord` | `UNIQUE (member_uid, version_coordinate)` |
| UNIQUE | `uq_member_version_supersedes` | `UNIQUE (supersedes_version_uid)` |

Triggers:

- `trg_member_version_finalize`: `CREATE CONSTRAINT TRIGGER trg_member_version_finalize AFTER INSERT ON metric_directory.member_version DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_member_version_finalize()`
- `trg_member_version_head`: `trg_member_version_head BEFORE INSERT ON metric_directory.member_version FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_member_version_head_guard()`
- `trg_member_version_immutable`: `trg_member_version_immutable BEFORE DELETE OR UPDATE ON metric_directory.member_version FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`

### `metric_directory.member_version_constant`

Columns: 4 | **NOT NULL:** `member_version_uid`, `role_code`, `value_type`, `value_json`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `member_version_constant_value_type_check` | `CHECK ((value_type = ANY (ARRAY['integer'::text, 'decimal_string'::text, 'text'::text, 'boolean'::text, 'date'::text])))` |
| FK | `fk_const_parent` | `FOREIGN KEY (member_version_uid) REFERENCES metric_directory.member_version(member_version_uid) DEFERRABLE INITIALLY DEFERRED` |
| PK | `member_version_constant_pkey` | `PRIMARY KEY (member_version_uid, role_code)` |

Triggers:

- `trg_const_finalize`: `trg_const_finalize BEFORE INSERT ON metric_directory.member_version_constant FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_child_finalize_guard()`
- `trg_constant_value`: `trg_constant_value BEFORE INSERT ON metric_directory.member_version_constant FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_constant_value_guard()`
- `trg_member_version_constant_immutable`: `trg_member_version_constant_immutable BEFORE DELETE OR UPDATE ON metric_directory.member_version_constant FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`

### `metric_directory.member_version_dependency`

Columns: 3 | **NOT NULL:** `member_version_uid`, `role_code`, `upstream_member_version_uid`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `no_self_dependency` | `CHECK ((upstream_member_version_uid <> member_version_uid))` |
| FK | `fk_dep_parent` | `FOREIGN KEY (member_version_uid) REFERENCES metric_directory.member_version(member_version_uid) DEFERRABLE INITIALLY DEFERRED` |
| FK | `member_version_dependency_upstream_member_version_uid_fkey` | `FOREIGN KEY (upstream_member_version_uid) REFERENCES metric_directory.member_version(member_version_uid)` |
| PK | `member_version_dependency_pkey` | `PRIMARY KEY (member_version_uid, role_code)` |
| t | `trg_dependency_dag` | `TRIGGER DEFERRABLE INITIALLY DEFERRED` |

Triggers:

- `trg_dep_finalize`: `trg_dep_finalize BEFORE INSERT ON metric_directory.member_version_dependency FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_child_finalize_guard()`
- `trg_dependency_dag`: `CREATE CONSTRAINT TRIGGER trg_dependency_dag AFTER INSERT ON metric_directory.member_version_dependency DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_dependency_dag_guard()`
- `trg_member_version_dependency_immutable`: `trg_member_version_dependency_immutable BEFORE DELETE OR UPDATE ON metric_directory.member_version_dependency FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`

### `metric_directory.member_version_direct_input`

Columns: 8 | **NOT NULL:** `member_version_uid`, `role_code`, `target_kind`, `representation_code`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `di_target_xor` | `CHECK ((((target_kind = 'business_concept'::text) AND (concept_id IS NOT NULL) AND (concept_version_id IS NOT NULL) AND (entity_id IS NULL) AND (entity_version_id IS NULL)) OR ((target_kind = 'entity'::text) AND (entity_id IS NOT NULL) AND (entity_version_id IS NOT NULL) AND (concept_id IS NULL) AND (concept_version_id IS NULL))))` |
| CHECK | `member_version_direct_input_target_kind_check` | `CHECK ((target_kind = ANY (ARRAY['business_concept'::text, 'entity'::text])))` |
| FK | `fk_di_bcv` | `FOREIGN KEY (concept_id, concept_version_id) REFERENCES concept_registry.business_concept_version(concept_id, concept_version_id)` |
| FK | `fk_di_ev` | `FOREIGN KEY (entity_id, entity_version_id) REFERENCES concept_registry.entity_version(entity_id, entity_version_id)` |
| FK | `fk_di_parent` | `FOREIGN KEY (member_version_uid) REFERENCES metric_directory.member_version(member_version_uid) DEFERRABLE INITIALLY DEFERRED` |
| PK | `member_version_direct_input_pkey` | `PRIMARY KEY (member_version_uid, role_code)` |

Triggers:

- `trg_di_finalize`: `trg_di_finalize BEFORE INSERT ON metric_directory.member_version_direct_input FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_child_finalize_guard()`
- `trg_member_version_direct_input_immutable`: `trg_member_version_direct_input_immutable BEFORE DELETE OR UPDATE ON metric_directory.member_version_direct_input FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`

### `metric_directory.member_version_discriminator`

Columns: 6 | **NOT NULL:** `member_version_uid`, `role_code`, `concept_id`, `concept_version_id`, `operator_code`, `governed_values_json`

| Kind | Name | Definition |
|---|---|---|
| FK | `fk_disc_bcv` | `FOREIGN KEY (concept_id, concept_version_id) REFERENCES concept_registry.business_concept_version(concept_id, concept_version_id)` |
| FK | `fk_disc_parent` | `FOREIGN KEY (member_version_uid) REFERENCES metric_directory.member_version(member_version_uid) DEFERRABLE INITIALLY DEFERRED` |
| PK | `member_version_discriminator_pkey` | `PRIMARY KEY (member_version_uid, role_code)` |

Triggers:

- `trg_disc_finalize`: `trg_disc_finalize BEFORE INSERT ON metric_directory.member_version_discriminator FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_child_finalize_guard()`
- `trg_member_version_discriminator_immutable`: `trg_member_version_discriminator_immutable BEFORE DELETE OR UPDATE ON metric_directory.member_version_discriminator FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`

### `metric_directory.migration_batch`

Columns: 7 | **NOT NULL:** `batch_uid`, `operator_authority_ref`, `d523_authority_ref`, `manifest_hash`, `opened_at`, `system_actor`

| Kind | Name | Definition |
|---|---|---|
| PK | `migration_batch_pkey` | `PRIMARY KEY (batch_uid)` |

Triggers:

- `trg_batch_close`: `trg_batch_close BEFORE UPDATE ON metric_directory.migration_batch FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_batch_close_guard()`
- `trg_batch_nodelete`: `trg_batch_nodelete BEFORE DELETE ON metric_directory.migration_batch FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`

### `metric_directory.migration_disposition_event`

Columns: 10 | **NOT NULL:** `event_uid`, `batch_uid`, `member_uid`, `source_kind`, `disposition`, `disposition_detail`, `created_at`, `created_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `disp_shape` | `CHECK ((((disposition = 'migrated'::text) AND (member_version_uid IS NOT NULL) AND (realization_event_uid IS NOT NULL)) OR ((disposition = ANY (ARRAY['nc_raised'::text, 'skipped'::text])) AND (member_version_uid IS NULL) AND (realization_event_uid IS NULL))))` |
| CHECK | `migration_disposition_event_disposition_check` | `CHECK ((disposition = ANY (ARRAY['migrated'::text, 'nc_raised'::text, 'skipped'::text])))` |
| FK | `fk_disp_manifest` | `FOREIGN KEY (batch_uid, member_uid, source_kind) REFERENCES metric_directory.migration_manifest_member(batch_uid, member_uid, source_kind)` |
| FK | `migration_disposition_event_member_version_uid_fkey` | `FOREIGN KEY (member_version_uid) REFERENCES metric_directory.member_version(member_version_uid)` |
| FK | `migration_disposition_event_realization_event_uid_fkey` | `FOREIGN KEY (realization_event_uid) REFERENCES metric_directory.realization_event(event_uid)` |
| PK | `migration_disposition_event_pkey` | `PRIMARY KEY (event_uid)` |
| UNIQUE | `uq_disp_once` | `UNIQUE (batch_uid, member_uid, source_kind)` |

Triggers:

- `trg_migration_disposition`: `trg_migration_disposition BEFORE INSERT ON metric_directory.migration_disposition_event FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_migration_disposition_guard()`
- `trg_migration_disposition_event_immutable`: `trg_migration_disposition_event_immutable BEFORE DELETE OR UPDATE ON metric_directory.migration_disposition_event FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`

### `metric_directory.migration_manifest_member`

Columns: 4 | **NOT NULL:** `batch_uid`, `member_uid`, `source_kind`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `migration_manifest_member_source_kind_check` | `CHECK ((source_kind = ANY (ARRAY['fk_pointer'::text, 'keystone_stamp'::text])))` |
| FK | `migration_manifest_member_batch_uid_fkey` | `FOREIGN KEY (batch_uid) REFERENCES metric_directory.migration_batch(batch_uid)` |
| PK | `migration_manifest_member_pkey` | `PRIMARY KEY (batch_uid, member_uid, source_kind)` |

Triggers:

- `trg_migration_manifest_member_immutable`: `trg_migration_manifest_member_immutable BEFORE DELETE OR UPDATE ON metric_directory.migration_manifest_member FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`

### `metric_directory.off_pool_exception_event`

Columns: 17 | **NOT NULL:** `event_uid`, `event_kind`, `actor`, `authority_ref`, `issued_at`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `off_pool_exception_event_event_kind_check` | `CHECK ((event_kind = ANY (ARRAY['propose'::text, 'accept'::text, 'revoke'::text])))` |
| CHECK | `off_pool_exception_event_exception_class_check` | `CHECK ((exception_class = ANY (ARRAY['OFF_POOL'::text, 'LEGACY'::text])))` |
| CHECK | `ope_shape` | `CHECK ((((event_kind = 'propose'::text) AND (metric_contract_version_uid IS NOT NULL) AND (package_signature_hash IS NOT NULL) AND (exception_class IS NOT NULL) AND (reason IS NOT NULL) AND (review_trigger_json IS NOT NULL) AND (jsonb_array_length(evidence_refs) >= 1) AND (accepts_event_uid IS NULL) AND (supersedes_event_uid IS NULL) AND (revokes_event_uid IS NULL) AND (import_uid IS NULL)) OR ((event_kind = 'accept'::text) AND (accepts_event_uid IS NOT NULL) AND (import_uid IS NOT NULL) AND (metric_contract_version_uid IS NULL) AND (package_signature_hash IS NULL) AND (exception_class IS NULL) AND (reason IS NULL) AND (review_trigger_json IS NULL) AND (revokes_event_uid IS NULL) AND (evidence_refs IS NULL) AND (supersedes_event_uid IS NULL) AND (expires_at IS NULL)) OR ((event_kind = 'revoke'::text) AND (revokes_event_uid IS NOT NULL) AND (accepts_event_uid IS NULL) AND (supersedes_event_uid IS NULL) AND (import_uid IS NULL) AND (metric_contract_version_uid IS NULL) AND (package_signature_hash IS NULL) AND (exception_class IS NULL) AND (reason IS NULL) AND (review_trigger_json IS NULL) AND (evidence_refs IS NULL) AND (expires_at IS NULL))))` |
| FK | `off_pool_exception_event_accepts_event_uid_fkey` | `FOREIGN KEY (accepts_event_uid) REFERENCES metric_directory.off_pool_exception_event(event_uid)` |
| FK | `off_pool_exception_event_import_uid_fkey` | `FOREIGN KEY (import_uid) REFERENCES metric_audit.artifact_import(import_uid)` |
| FK | `off_pool_exception_event_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| FK | `off_pool_exception_event_revokes_event_uid_fkey` | `FOREIGN KEY (revokes_event_uid) REFERENCES metric_directory.off_pool_exception_event(event_uid)` |
| FK | `off_pool_exception_event_supersedes_event_uid_fkey` | `FOREIGN KEY (supersedes_event_uid) REFERENCES metric_directory.off_pool_exception_event(event_uid)` |
| PK | `off_pool_exception_event_pkey` | `PRIMARY KEY (event_uid)` |
| UNIQUE | `uq_ope_accepts` | `UNIQUE (accepts_event_uid)` |
| UNIQUE | `uq_ope_import` | `UNIQUE (import_uid)` |
| UNIQUE | `uq_ope_revokes` | `UNIQUE (revokes_event_uid)` |
| UNIQUE | `uq_ope_supersedes` | `UNIQUE (supersedes_event_uid)` |

Triggers:

- `trg_off_pool`: `trg_off_pool BEFORE INSERT ON metric_directory.off_pool_exception_event FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_off_pool_guard()`
- `trg_off_pool_exception_event_immutable`: `trg_off_pool_exception_event_immutable BEFORE DELETE OR UPDATE ON metric_directory.off_pool_exception_event FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`
- `trg_off_pool_operative`: `trg_off_pool_operative AFTER INSERT ON metric_directory.off_pool_exception_event FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_off_pool_operative_maint()`

### `metric_directory.off_pool_operative`

Columns: 2 | **NOT NULL:** `metric_contract_version_uid`, `event_uid`

| Kind | Name | Definition |
|---|---|---|
| FK | `off_pool_operative_event_uid_fkey` | `FOREIGN KEY (event_uid) REFERENCES metric_directory.off_pool_exception_event(event_uid)` |
| PK | `off_pool_operative_pkey` | `PRIMARY KEY (metric_contract_version_uid)` |

### `metric_directory.realization_event`

Columns: 12 | **NOT NULL:** `event_uid`, `event_kind`, `authority_ref`, `rationale`, `decided_at`, `created_at`, `created_by_name`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `realization_event_event_kind_check` | `CHECK ((event_kind = ANY (ARRAY['assert'::text, 'revoke'::text])))` |
| CHECK | `reln_shape` | `CHECK ((((event_kind = 'assert'::text) AND (member_version_uid IS NOT NULL) AND (metric_contract_version_uid IS NOT NULL) AND (revokes_event_uid IS NULL)) OR ((event_kind = 'revoke'::text) AND (revokes_event_uid IS NOT NULL) AND (member_version_uid IS NULL) AND (metric_contract_version_uid IS NULL) AND (supersedes_event_uid IS NULL))))` |
| FK | `realization_event_member_version_uid_fkey` | `FOREIGN KEY (member_version_uid) REFERENCES metric_directory.member_version(member_version_uid)` |
| FK | `realization_event_metric_contract_version_uid_fkey` | `FOREIGN KEY (metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid)` |
| FK | `realization_event_revokes_event_uid_fkey` | `FOREIGN KEY (revokes_event_uid) REFERENCES metric_directory.realization_event(event_uid)` |
| FK | `realization_event_supersedes_event_uid_fkey` | `FOREIGN KEY (supersedes_event_uid) REFERENCES metric_directory.realization_event(event_uid)` |
| PK | `realization_event_pkey` | `PRIMARY KEY (event_uid)` |

Triggers:

- `trg_realization_event`: `trg_realization_event BEFORE INSERT ON metric_directory.realization_event FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_realization_event_guard()`
- `trg_realization_event_immutable`: `trg_realization_event_immutable BEFORE DELETE OR UPDATE ON metric_directory.realization_event FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`
- `trg_realization_operative`: `trg_realization_operative AFTER INSERT ON metric_directory.realization_event FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_realization_operative_maint()`

### `metric_directory.realization_operative`

Columns: 4 | **NOT NULL:** `event_uid`, `member_version_uid`, `metric_contract_version_uid`

| Kind | Name | Definition |
|---|---|---|
| FK | `realization_operative_event_uid_fkey` | `FOREIGN KEY (event_uid) REFERENCES metric_directory.realization_event(event_uid)` |
| PK | `realization_operative_pkey` | `PRIMARY KEY (event_uid)` |
| UNIQUE | `uq_operative_mcv` | `UNIQUE (metric_contract_version_uid)` |
| UNIQUE | `uq_operative_member_variant` | `UNIQUE NULLS NOT DISTINCT (member_version_uid, variant_discriminator_json)` |

## 6. Checker-side guard functions (`audit_execution.*`, bc_audit_dev) — VERBATIM

### `audit_execution.append_audit_cohort_member_event`

Reads/writes: `audit_execution.audit_cohort_member`, `audit_execution.audit_cohort_member_event`, `prior.event_hash`

```sql
CREATE OR REPLACE FUNCTION audit_execution.append_audit_cohort_member_event(p_event_uid uuid, p_work_item_uid uuid, p_event_sequence bigint, p_event_kind text, p_details_json text, p_prior_event_hash text, p_event_hash text, p_recorded_at text, p_event_body_json text)
 RETURNS audit_execution.audit_cohort_member_event
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  prior audit_execution.audit_cohort_member_event;
  inserted audit_execution.audit_cohort_member_event;
  expected_body jsonb;
BEGIN
  PERFORM 1 FROM audit_execution.audit_cohort_member WHERE work_item_uid = p_work_item_uid FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'audit cohort member not found' USING ERRCODE = 'P0002'; END IF;
  SELECT * INTO prior FROM audit_execution.audit_cohort_member_event
    WHERE work_item_uid = p_work_item_uid ORDER BY event_sequence DESC LIMIT 1;
  IF p_event_sequence <> COALESCE(prior.event_sequence, 0) + 1
    OR p_prior_event_hash IS DISTINCT FROM prior.event_hash THEN
    RAISE EXCEPTION 'audit cohort member event stream changed' USING ERRCODE = '40001';
  END IF;
  expected_body := jsonb_build_object(
    'event_uid', p_event_uid::text,
    'work_item_uid', p_work_item_uid::text,
    'event_sequence', p_event_sequence,
    'event_kind', p_event_kind,
    'details', p_details_json::jsonb,
    'prior_event_hash', p_prior_event_hash,
    'recorded_at', p_recorded_at
  );
  IF p_event_body_json::jsonb <> expected_body THEN
    RAISE EXCEPTION 'audit cohort member event body fields do not match append coordinates' USING ERRCODE = '22000';
  END IF;
  IF p_event_hash <> 'sha256:' || encode(digest(convert_to(p_event_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'audit cohort member event hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.audit_cohort_member_event (
    event_uid, work_item_uid, event_sequence, event_kind, details_json,
    prior_event_hash, event_hash, recorded_at
  ) VALUES (
    p_event_uid, p_work_item_uid, p_event_sequence, p_event_kind, p_details_json,
    p_prior_event_hash, p_event_hash, p_recorded_at
  ) RETURNING * INTO inserted;
  RETURN inserted;
END;
$function$
```

### `audit_execution.append_audit_run_event`

Reads/writes: `audit_execution.audit_run`, `audit_execution.audit_run_event`, `prior.event_hash`

```sql
CREATE OR REPLACE FUNCTION audit_execution.append_audit_run_event(p_event_uid uuid, p_audit_run_uid uuid, p_event_sequence bigint, p_event_kind text, p_actor text, p_details_json text, p_prior_event_hash text, p_event_hash text, p_recorded_at text, p_event_body_json text)
 RETURNS audit_execution.audit_run_event
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  prior audit_execution.audit_run_event;
  inserted audit_execution.audit_run_event;
  expected_event jsonb;
BEGIN
  PERFORM 1 FROM audit_execution.audit_run WHERE audit_run_uid = p_audit_run_uid FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'audit run not found' USING ERRCODE = 'P0002'; END IF;
  SELECT * INTO prior FROM audit_execution.audit_run_event
    WHERE audit_run_uid = p_audit_run_uid ORDER BY event_sequence DESC LIMIT 1;
  IF p_event_sequence <> COALESCE(prior.event_sequence, 0) + 1
    OR p_prior_event_hash IS DISTINCT FROM prior.event_hash THEN
    RAISE EXCEPTION 'audit-run event stream changed' USING ERRCODE = '40001';
  END IF;
  IF p_event_kind = 'OPENED' THEN
    RAISE EXCEPTION 'OPENED must be created by open_audit_run' USING ERRCODE = '55000';
  END IF;
  expected_event := jsonb_build_object(
    'event_uid', p_event_uid::text,
    'audit_run_uid', p_audit_run_uid::text,
    'event_sequence', p_event_sequence,
    'event_kind', p_event_kind,
    'actor', p_actor,
    'details', p_details_json::jsonb,
    'prior_event_hash', p_prior_event_hash,
    'recorded_at', p_recorded_at
  );
  IF p_event_body_json::jsonb <> expected_event THEN
    RAISE EXCEPTION 'audit-run event body fields do not match append coordinates' USING ERRCODE = '22000';
  END IF;
  IF p_event_hash <> 'sha256:' || encode(digest(convert_to(p_event_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'audit-run event hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.audit_run_event (
    event_uid, audit_run_uid, event_sequence, event_kind, actor, details_json,
    prior_event_hash, event_hash, recorded_at
  ) VALUES (
    p_event_uid, p_audit_run_uid, p_event_sequence, p_event_kind, p_actor, p_details_json,
    p_prior_event_hash, p_event_hash, p_recorded_at
  ) RETURNING * INTO inserted;
  RETURN inserted;
END;
$function$
```

### `audit_execution.append_outbound_feed_publication`

Reads/writes: `audit_execution.outbound_feed_bootstrap`, `audit_execution.outbound_feed_publication`

```sql
CREATE OR REPLACE FUNCTION audit_execution.append_outbound_feed_publication(p_publication_uid uuid, p_audit_run_uid uuid, p_feed_name text, p_report_sequence bigint, p_decision_sequence bigint, p_prior_envelope_digest text, p_report_envelope_digest text, p_decision_envelope_digest text, p_publication_preflight_digest text, p_signer_key_id text, p_signer_fingerprint text, p_transport_receipt_digest text, p_publication_input_digest text, p_published_at text, p_publication_hash text, p_publication_body_json text)
 RETURNS audit_execution.outbound_feed_publication
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  bootstrap audit_execution.outbound_feed_bootstrap;
  existing audit_execution.outbound_feed_publication;
  previous audit_execution.outbound_feed_publication;
  inserted audit_execution.outbound_feed_publication;
  expected_sequence bigint;
  expected_prior text;
  expected_body jsonb;
BEGIN
  PERFORM pg_advisory_xact_lock(hashtextextended(p_feed_name, 0));
  SELECT * INTO existing
  FROM audit_execution.outbound_feed_publication
  WHERE audit_run_uid = p_audit_run_uid;
  IF FOUND THEN
    IF existing.feed_name <> p_feed_name
      OR existing.publication_input_digest <> p_publication_input_digest
      OR existing.report_envelope_digest <> p_report_envelope_digest
      OR existing.decision_envelope_digest <> p_decision_envelope_digest
      OR existing.transport_receipt_digest <> p_transport_receipt_digest
      OR existing.publication_hash <> p_publication_hash THEN
      RAISE EXCEPTION 'outbound publication replay conflict' USING ERRCODE = '23505';
    END IF;
    RETURN existing;
  END IF;
  SELECT * INTO bootstrap
  FROM audit_execution.outbound_feed_bootstrap
  WHERE feed_name = p_feed_name;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'outbound feed bootstrap not registered' USING ERRCODE = '22000';
  END IF;
  IF bootstrap.signer_key_id <> p_signer_key_id
    OR bootstrap.signer_fingerprint <> p_signer_fingerprint THEN
    RAISE EXCEPTION 'outbound signer does not match feed bootstrap' USING ERRCODE = '22000';
  END IF;
  SELECT * INTO previous
  FROM audit_execution.outbound_feed_publication
  WHERE feed_name = p_feed_name
  ORDER BY decision_sequence DESC
  LIMIT 1;
  IF FOUND THEN
    expected_sequence := previous.decision_sequence + 1;
    expected_prior := previous.decision_envelope_digest;
  ELSE
    expected_sequence := bootstrap.next_sequence;
    expected_prior := bootstrap.prior_envelope_digest;
  END IF;
  IF p_report_sequence <> expected_sequence OR p_decision_sequence <> expected_sequence + 1 THEN
    RAISE EXCEPTION 'outbound feed sequence discontinuity' USING ERRCODE = '22000';
  END IF;
  IF p_prior_envelope_digest IS DISTINCT FROM expected_prior THEN
    RAISE EXCEPTION 'outbound feed prior digest discontinuity' USING ERRCODE = '22000';
  END IF;
  expected_body := jsonb_build_object(
    'publication_uid', p_publication_uid::text,
    'audit_run_uid', p_audit_run_uid::text,
    'feed_name', p_feed_name,
    'report_sequence', p_report_sequence,
    'decision_sequence', p_decision_sequence,
    'prior_envelope_digest', p_prior_envelope_digest,
    'report_envelope_digest', p_report_envelope_digest,
    'decision_envelope_digest', p_decision_envelope_digest,
    'publication_preflight_digest', p_publication_preflight_digest,
    'signer_key_id', p_signer_key_id,
    'signer_fingerprint', p_signer_fingerprint,
    'transport_receipt_digest', p_transport_receipt_digest,
    'publication_input_digest', p_publication_input_digest,
    'published_at', p_published_at
  );
  IF p_publication_body_json::jsonb <> expected_body THEN
    RAISE EXCEPTION 'outbound publication body fields do not match coordinates' USING ERRCODE = '22000';
  END IF;
  IF p_publication_hash <> 'sha256:' || encode(digest(convert_to(p_publication_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'outbound publication hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.outbound_feed_publication (
    publication_uid, audit_run_uid, feed_name, report_sequence, decision_sequence,
    prior_envelope_digest, report_envelope_digest, decision_envelope_digest,
    publication_preflight_digest, signer_key_id, signer_fingerprint,
    transport_receipt_digest, publication_input_digest, published_at, publication_hash
  ) VALUES (
    p_publication_uid, p_audit_run_uid, p_feed_name, p_report_sequence, p_decision_sequence,
    p_prior_envelope_digest, p_report_envelope_digest, p_decision_envelope_digest,
    p_publication_preflight_digest, p_signer_key_id, p_signer_fingerprint,
    p_transport_receipt_digest, p_publication_input_digest, p_published_at, p_publication_hash
  ) RETURNING * INTO inserted;
  RETURN inserted;
END;
$function$
```

### `audit_execution.append_verified_context`

Reads/writes: `audit_execution.evidence_object`, `audit_execution.work_context`, `audit_execution.work_item`, `prior.context_package_digest`, `prior.context_uid`

```sql
CREATE OR REPLACE FUNCTION audit_execution.append_verified_context(p_context_uid uuid, p_work_item_uid uuid, p_context_version bigint, p_context_package_json text, p_context_package_digest text, p_context_body_json text, p_previous_context_uid uuid, p_previous_context_digest text, p_grounded_by text, p_created_at text)
 RETURNS audit_execution.work_context
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  prior audit_execution.work_context;
  inserted audit_execution.work_context;
BEGIN
  PERFORM 1 FROM audit_execution.work_item WHERE work_item_uid = p_work_item_uid FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'audit work item not found' USING ERRCODE = 'P0002'; END IF;
  SELECT * INTO prior FROM audit_execution.work_context
    WHERE work_item_uid = p_work_item_uid ORDER BY context_version DESC LIMIT 1;
  IF prior.grounding_status <> 'COORDINATES_ONLY'
    OR p_context_version <> prior.context_version + 1
    OR p_previous_context_uid IS DISTINCT FROM prior.context_uid
    OR p_previous_context_digest IS DISTINCT FROM prior.context_package_digest THEN
    RAISE EXCEPTION 'invalid or stale work-context successor' USING ERRCODE = '40001';
  END IF;
  IF p_context_package_digest <> 'sha256:' || encode(digest(convert_to(p_context_body_json, 'UTF8'), 'sha256'), 'hex')
    OR p_context_package_json::jsonb <> (p_context_body_json::jsonb
      || jsonb_build_object('context_package_digest', p_context_package_digest))
    OR p_context_package_json::jsonb ->> 'grounding_status' <> 'VERIFIED'
    OR p_context_package_json::jsonb ->> 'prior_context_package_digest' <> prior.context_package_digest
    OR jsonb_array_length(p_context_package_json::jsonb -> 'grounded_evidence') = 0 THEN
    RAISE EXCEPTION 'verified context package digest, lineage, or evidence mismatch' USING ERRCODE = '22000';
  END IF;
  IF jsonb_array_length(p_context_package_json::jsonb -> 'grounded_evidence')
      <> (SELECT count(*) FROM audit_execution.evidence_object WHERE work_item_uid = p_work_item_uid)
    OR EXISTS (
      SELECT 1
      FROM jsonb_array_elements(p_context_package_json::jsonb -> 'grounded_evidence') reference
      WHERE NOT EXISTS (
        SELECT 1 FROM audit_execution.evidence_object evidence
        WHERE evidence.work_item_uid = p_work_item_uid
          AND evidence.evidence_uid::text = reference ->> 'evidence_uid'
          AND evidence.content_digest = reference ->> 'content_digest'
          AND evidence.coordinate_digest = reference ->> 'coordinate_digest'
      )
    ) THEN
    RAISE EXCEPTION 'verified context does not bind the exact grounded-evidence set' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.work_context (
    context_uid, work_item_uid, context_version, grounding_status,
    context_package_json, context_package_digest, previous_context_uid,
    previous_context_digest, grounded_by, created_at
  ) VALUES (
    p_context_uid, p_work_item_uid, p_context_version, 'VERIFIED',
    p_context_package_json, p_context_package_digest, p_previous_context_uid,
    p_previous_context_digest, p_grounded_by, p_created_at
  ) RETURNING * INTO inserted;
  RETURN inserted;
END;
$function$
```

### `audit_execution.append_work_item_event`

Reads/writes: `audit_execution.work_item`, `audit_execution.work_item_event`, `prior.claim_token_hash`, `prior.event_hash`, `prior.worker_id`

```sql
CREATE OR REPLACE FUNCTION audit_execution.append_work_item_event(p_event_uid uuid, p_work_item_uid uuid, p_event_sequence bigint, p_event_kind text, p_worker_id text, p_claim_token_hash text, p_lease_expires_at text, p_details_json text, p_prior_event_hash text, p_event_hash text, p_recorded_at text, p_event_body_json text)
 RETURNS audit_execution.work_item_event
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  prior audit_execution.work_item_event;
  inserted audit_execution.work_item_event;
  expected_event jsonb;
BEGIN
  PERFORM 1 FROM audit_execution.work_item WHERE work_item_uid = p_work_item_uid FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'audit work item not found' USING ERRCODE = 'P0002'; END IF;
  SELECT * INTO prior FROM audit_execution.work_item_event
    WHERE work_item_uid = p_work_item_uid ORDER BY event_sequence DESC LIMIT 1;
  IF p_event_sequence <> COALESCE(prior.event_sequence, 0) + 1
    OR p_prior_event_hash IS DISTINCT FROM prior.event_hash THEN
    RAISE EXCEPTION 'work-item event stream changed' USING ERRCODE = '40001';
  END IF;
  IF abs(extract(epoch FROM (p_recorded_at::timestamptz - clock_timestamp()))) > 300
    OR p_recorded_at::timestamptz < prior.recorded_at::timestamptz THEN
    RAISE EXCEPTION 'work-item event timestamp is stale or non-monotonic' USING ERRCODE = '22000';
  END IF;
  IF p_event_kind = 'CLAIMED' THEN
    IF p_worker_id IS NULL OR p_claim_token_hash IS NULL OR p_lease_expires_at IS NULL
      OR p_lease_expires_at::timestamptz <= clock_timestamp()
      OR p_lease_expires_at::timestamptz > clock_timestamp() + interval '1 hour'
      OR NOT (
        prior.event_kind IN ('DISCOVERED', 'RELEASED')
        OR (prior.event_kind IN ('CLAIMED', 'HEARTBEAT') AND prior.lease_expires_at::timestamptz <= clock_timestamp())
      ) THEN
      RAISE EXCEPTION 'invalid work-item claim transition' USING ERRCODE = '55000';
    END IF;
  ELSIF p_event_kind IN ('HEARTBEAT', 'RELEASED', 'SUBMITTED') THEN
    IF prior.event_kind NOT IN ('CLAIMED', 'HEARTBEAT')
      OR prior.lease_expires_at::timestamptz <= clock_timestamp()
      OR p_worker_id IS DISTINCT FROM prior.worker_id
      OR p_claim_token_hash IS DISTINCT FROM prior.claim_token_hash THEN
      RAISE EXCEPTION 'work-item event requires the current live claim' USING ERRCODE = '55000';
    END IF;
    IF p_event_kind = 'HEARTBEAT' AND p_lease_expires_at IS NULL THEN
      RAISE EXCEPTION 'heartbeat requires a lease expiry' USING ERRCODE = '55000';
    END IF;
    IF p_event_kind = 'HEARTBEAT' AND (
      p_lease_expires_at::timestamptz <= clock_timestamp()
      OR p_lease_expires_at::timestamptz > clock_timestamp() + interval '1 hour'
    ) THEN
      RAISE EXCEPTION 'heartbeat lease expiry is outside the allowed window' USING ERRCODE = '55000';
    END IF;
  ELSE
    RAISE EXCEPTION 'event kind cannot be appended through this function' USING ERRCODE = '55000';
  END IF;
  expected_event := jsonb_build_object(
    'event_uid', p_event_uid::text,
    'work_item_uid', p_work_item_uid::text,
    'event_sequence', p_event_sequence,
    'event_kind', p_event_kind,
    'worker_id', p_worker_id,
    'lease_expires_at', p_lease_expires_at,
    'details', p_details_json::jsonb,
    'prior_event_hash', p_prior_event_hash,
    'recorded_at', p_recorded_at
  );
  IF p_event_body_json::jsonb <> expected_event THEN
    RAISE EXCEPTION 'work-item event body fields do not match append coordinates' USING ERRCODE = '22000';
  END IF;
  IF p_event_hash <> 'sha256:' || encode(digest(convert_to(p_event_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'work-item event hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.work_item_event (
    event_uid, work_item_uid, event_sequence, event_kind, worker_id, claim_token_hash,
    lease_expires_at, details_json, prior_event_hash, event_hash, recorded_at
  ) VALUES (
    p_event_uid, p_work_item_uid, p_event_sequence, p_event_kind, p_worker_id, p_claim_token_hash,
    p_lease_expires_at, p_details_json, p_prior_event_hash, p_event_hash, p_recorded_at
  ) RETURNING * INTO inserted;
  RETURN inserted;
END;
$function$
```

### `audit_execution.attach_audit_cohort_member`

Reads/writes: `audit_execution.audit_cohort_member`, `audit_execution.work_item`

```sql
CREATE OR REPLACE FUNCTION audit_execution.attach_audit_cohort_member(p_work_item_uid uuid, p_cohort_uid uuid, p_batch_uid text, p_request_uid uuid, p_subject_uid uuid, p_attached_at text, p_member_hash text, p_member_body_json text)
 RETURNS audit_execution.audit_cohort_member
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  existing audit_execution.audit_cohort_member;
  inserted audit_execution.audit_cohort_member;
  expected_body jsonb;
BEGIN
  SELECT * INTO existing FROM audit_execution.audit_cohort_member WHERE work_item_uid = p_work_item_uid;
  IF FOUND THEN
    IF existing.cohort_uid <> p_cohort_uid OR existing.batch_uid <> p_batch_uid
      OR existing.request_uid <> p_request_uid OR existing.subject_uid <> p_subject_uid
      OR existing.member_hash <> p_member_hash THEN
      RAISE EXCEPTION 'audit cohort member replay conflict' USING ERRCODE = '23505';
    END IF;
    RETURN existing;
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM audit_execution.work_item
    WHERE work_item_uid = p_work_item_uid AND request_uid = p_request_uid AND subject_uid = p_subject_uid
  ) THEN
    RAISE EXCEPTION 'work item coordinates do not match cohort member' USING ERRCODE = '22000';
  END IF;
  expected_body := jsonb_build_object(
    'work_item_uid', p_work_item_uid::text,
    'cohort_uid', p_cohort_uid::text,
    'batch_uid', p_batch_uid,
    'request_uid', p_request_uid::text,
    'subject_uid', p_subject_uid::text,
    'attached_at', p_attached_at
  );
  IF p_member_body_json::jsonb <> expected_body THEN
    RAISE EXCEPTION 'audit cohort member body fields do not match append coordinates' USING ERRCODE = '22000';
  END IF;
  IF p_member_hash <> 'sha256:' || encode(digest(convert_to(p_member_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'audit cohort member hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.audit_cohort_member (
    work_item_uid, cohort_uid, batch_uid, request_uid, subject_uid, attached_at, member_hash
  ) VALUES (
    p_work_item_uid, p_cohort_uid, p_batch_uid, p_request_uid, p_subject_uid, p_attached_at, p_member_hash
  ) RETURNING * INTO inserted;
  RETURN inserted;
END;
$function$
```

### `audit_execution.bind_contextual_release`

Reads/writes: `audit_execution.audit_run`, `audit_execution.audit_run_artifact`, `audit_execution.audit_run_bootstrap_authority_event`, `audit_execution.contextual_release_authority`, `audit_execution.contextual_release_binding`, `audit_execution.outbound_feed_publication`

```sql
CREATE OR REPLACE FUNCTION audit_execution.bind_contextual_release(p_binding_uid uuid, p_audit_run_uid uuid, p_bootstrap_manifest_uid uuid, p_bootstrap_manifest_digest text, p_binding_json text, p_binding_body_json text, p_binding_digest text, p_bound_by text, p_bound_at text, p_artifact_digest text, p_artifact_hash text, p_artifact_body_json text)
 RETURNS audit_execution.contextual_release_binding
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  run_row audit_execution.audit_run;
  authority audit_execution.contextual_release_authority;
  bootstrap audit_execution.audit_run_bootstrap_authority_event;
  existing audit_execution.contextual_release_binding;
  inserted audit_execution.contextual_release_binding;
  body jsonb;
  expected_artifact jsonb;
BEGIN
  SELECT * INTO run_row FROM audit_execution.audit_run WHERE audit_run_uid = p_audit_run_uid FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'audit run not found' USING ERRCODE = 'P0002'; END IF;
  SELECT * INTO existing FROM audit_execution.contextual_release_binding WHERE audit_run_uid = p_audit_run_uid;
  IF FOUND THEN
    IF existing.binding_digest <> p_binding_digest OR existing.binding_json::jsonb <> p_binding_json::jsonb THEN
      RAISE EXCEPTION 'contextual release binding replay conflict' USING ERRCODE = '23505';
    END IF;
    RETURN existing;
  END IF;
  SELECT * INTO authority FROM audit_execution.contextual_release_authority;
  IF NOT FOUND THEN RAISE EXCEPTION 'contextual release authority is not installed' USING ERRCODE = '55000'; END IF;
  SELECT * INTO bootstrap FROM audit_execution.audit_run_bootstrap_authority_event
    ORDER BY event_sequence DESC LIMIT 1;
  IF NOT FOUND OR bootstrap.successor_manifest_uid <> p_bootstrap_manifest_uid
    OR bootstrap.successor_manifest_digest <> p_bootstrap_manifest_digest THEN
    RAISE EXCEPTION 'AuditHub bootstrap successor is not current' USING ERRCODE = '55000';
  END IF;
  body := p_binding_json::jsonb;
  IF body ->> 'schema_version' <> 'contextual-release-binding-v2'
    OR body ->> 'canonicalization_version' <> 'bc-canonical-json-v1'
    OR body ->> 'binding_uid' <> p_binding_uid::text
    OR body ->> 'audit_run_uid' <> p_audit_run_uid::text
    OR body #>> '{request,request_uid}' <> run_row.request_uid::text
    OR body #>> '{request,request_digest}' <> run_row.request_digest
    OR body #>> '{request,request_envelope_digest}' <> run_row.request_envelope_digest
    OR body #>> '{subject,metric_contract_uid}' <> run_row.metric_contract_uid::text
    OR body #>> '{subject,metric_contract_version_uid}' <> run_row.metric_contract_version_uid::text
    OR body #>> '{package,package_snapshot_digest}' <> run_row.package_snapshot_digest
    OR body #>> '{package,closure_root}' <> run_row.closure_root
    OR body #>> '{package,hash_algorithm_version}' <> 'mcf-package-v3'
    OR body #>> '{bootstrap,manifest_uid}' <> p_bootstrap_manifest_uid::text
    OR body #>> '{bootstrap,manifest_digest}' <> p_bootstrap_manifest_digest
    OR body #>> '{contextual_release,accepted_release_uid}' <> authority.contextual_release_uid::text
    OR body #>> '{contextual_release,ratification_digest}' <> authority.contextual_release_ratification_digest
    OR body #>> '{contextual_release,acceptance_manifest_digest}' <> authority.acceptance_manifest_digest
    OR body #> '{contextual_release,component_digests}' <> authority.component_digests_json::jsonb
    OR body #>> '{methodology_release,methodology_release_uid}' <> authority.methodology_release_uid::text
    OR body #>> '{methodology_release,methodology_version}' <> authority.methodology_version
    OR body #>> '{methodology_release,methodology_digest}' <> authority.methodology_digest
    OR body #>> '{methodology_release,ratification_digest}' <> authority.methodology_release_ratification_digest
    OR body #>> '{platform_authority_pin,pin_uid}' <> authority.platform_pin_uid::text
    OR body #>> '{platform_authority_pin,pin_digest}' <> authority.platform_pin_digest
    OR body #>> '{platform_authority_pin,evidence_ref}' <> authority.platform_pin_evidence_ref
    OR body #>> '{platform_authority_pin,evidence_digest}' <> authority.platform_pin_evidence_digest
    OR body #>> '{bound_by,actor}' <> p_bound_by
    OR body #>> '{bound_by,engine}' <> 'bc-external-audit'
    OR body #>> '{bound_by,engine_version}' <> '0.4.0'
    OR body ->> 'bound_at' <> p_bound_at THEN
    RAISE EXCEPTION 'contextual release binding coordinates do not match retained authority' USING ERRCODE = '22000';
  END IF;
  IF p_binding_body_json::jsonb <> body - 'binding_digest'
    OR p_binding_digest <> 'sha256:' || encode(digest(convert_to(
      p_binding_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'contextual release binding digest mismatch' USING ERRCODE = '22000';
  END IF;
  IF EXISTS (
    SELECT 1 FROM audit_execution.audit_run_artifact
    WHERE audit_run_uid = p_audit_run_uid
      AND artifact_kind IN ('REPORT_CANDIDATE','DECISION_CANDIDATE','SIGNING_INTENT','SIGNING_RECEIPT','REPORT_ENVELOPE','DECISION_ENVELOPE')
  ) OR EXISTS (
    SELECT 1 FROM audit_execution.outbound_feed_publication WHERE audit_run_uid = p_audit_run_uid
  ) THEN
    RAISE EXCEPTION 'contextual release cannot be rebound after result or publication artifacts' USING ERRCODE = '55000';
  END IF;
  expected_artifact := jsonb_build_object(
    'artifact_uid', p_binding_uid::text,
    'audit_run_uid', p_audit_run_uid::text,
    'artifact_kind', 'CONTEXTUAL_RELEASE_BINDING',
    'artifact_digest', p_artifact_digest,
    'artifact_json', body,
    'created_by', p_bound_by,
    'created_at', p_bound_at
  );
  IF p_artifact_digest <> 'sha256:' || encode(digest(convert_to(p_binding_json, 'UTF8'), 'sha256'), 'hex')
    OR p_artifact_body_json::jsonb <> expected_artifact
    OR p_artifact_hash <> 'sha256:' || encode(digest(convert_to(p_artifact_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'contextual release binding artifact hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.contextual_release_binding (
    binding_uid, audit_run_uid, bootstrap_manifest_uid, bootstrap_manifest_digest,
    binding_json, binding_digest, bound_by, bound_at
  ) VALUES (
    p_binding_uid, p_audit_run_uid, p_bootstrap_manifest_uid, p_bootstrap_manifest_digest,
    p_binding_json, p_binding_digest, p_bound_by, p_bound_at
  ) RETURNING * INTO inserted;
  INSERT INTO audit_execution.audit_run_artifact (
    artifact_uid, audit_run_uid, artifact_kind, artifact_digest, artifact_json,
    artifact_hash, created_by, created_at
  ) VALUES (
    p_binding_uid, p_audit_run_uid, 'CONTEXTUAL_RELEASE_BINDING', p_artifact_digest,
    p_binding_json, p_artifact_hash, p_bound_by, p_bound_at
  );
  RETURN inserted;
END;
$function$
```

### `audit_execution.discover_work_item`

Reads/writes: `audit_execution.work_context`, `audit_execution.work_item`, `audit_execution.work_item_event`

```sql
CREATE OR REPLACE FUNCTION audit_execution.discover_work_item(p_work_item_uid uuid, p_request_uid uuid, p_request_digest text, p_request_envelope_digest text, p_subject_uid uuid, p_package_snapshot_digest text, p_closure_root text, p_request_payload_json text, p_request_envelope_json text, p_context_uid uuid, p_context_package_json text, p_context_package_digest text, p_context_body_json text, p_created_at text, p_event_uid uuid, p_event_hash text, p_event_body_json text, p_details_json text)
 RETURNS audit_execution.work_item
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  inserted audit_execution.work_item;
  expected_event jsonb;
BEGIN
  IF p_context_package_digest <> 'sha256:' || encode(digest(convert_to(p_context_body_json, 'UTF8'), 'sha256'), 'hex')
    OR p_context_package_json::jsonb <> (p_context_body_json::jsonb
      || jsonb_build_object('context_package_digest', p_context_package_digest))
    OR p_context_package_json::jsonb ->> 'grounding_status' <> 'COORDINATES_ONLY' THEN
    RAISE EXCEPTION 'initial context package digest or shape mismatch' USING ERRCODE = '22000';
  END IF;
  expected_event := jsonb_build_object(
    'event_uid', p_event_uid::text,
    'work_item_uid', p_work_item_uid::text,
    'event_sequence', 1,
    'event_kind', 'DISCOVERED',
    'worker_id', NULL,
    'lease_expires_at', NULL,
    'details', p_details_json::jsonb,
    'prior_event_hash', NULL,
    'recorded_at', p_created_at
  );
  IF p_event_body_json::jsonb <> expected_event THEN
    RAISE EXCEPTION 'discovery event body fields do not match append coordinates' USING ERRCODE = '22000';
  END IF;
  IF p_event_hash <> 'sha256:' || encode(digest(convert_to(p_event_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'discovery event hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.work_item (
    work_item_uid, request_uid, request_digest, request_envelope_digest, subject_uid,
    package_snapshot_digest, closure_root, request_payload_json, request_envelope_json, created_at
  ) VALUES (
    p_work_item_uid, p_request_uid, p_request_digest, p_request_envelope_digest, p_subject_uid,
    p_package_snapshot_digest, p_closure_root, p_request_payload_json, p_request_envelope_json, p_created_at
  ) RETURNING * INTO inserted;
  INSERT INTO audit_execution.work_context (
    context_uid, work_item_uid, context_version, grounding_status,
    context_package_json, context_package_digest, created_at
  ) VALUES (
    p_context_uid, p_work_item_uid, 1, 'COORDINATES_ONLY',
    p_context_package_json, p_context_package_digest, p_created_at
  );
  INSERT INTO audit_execution.work_item_event (
    event_uid, work_item_uid, event_sequence, event_kind, details_json,
    event_hash, recorded_at
  ) VALUES (
    p_event_uid, p_work_item_uid, 1, 'DISCOVERED', p_details_json,
    p_event_hash, p_created_at
  );
  RETURN inserted;
END;
$function$
```

### `audit_execution.open_audit_cohort`

Reads/writes: `audit_execution.audit_cohort`

```sql
CREATE OR REPLACE FUNCTION audit_execution.open_audit_cohort(p_cohort_uid uuid, p_manifest_digest text, p_opened_by text, p_opened_at text, p_cohort_hash text, p_cohort_body_json text)
 RETURNS audit_execution.audit_cohort
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  existing audit_execution.audit_cohort;
  inserted audit_execution.audit_cohort;
  expected_body jsonb;
BEGIN
  SELECT * INTO existing FROM audit_execution.audit_cohort WHERE cohort_uid = p_cohort_uid;
  IF FOUND THEN
    IF existing.manifest_digest <> p_manifest_digest OR existing.cohort_hash <> p_cohort_hash THEN
      RAISE EXCEPTION 'audit cohort replay conflict' USING ERRCODE = '23505';
    END IF;
    RETURN existing;
  END IF;
  expected_body := jsonb_build_object(
    'cohort_uid', p_cohort_uid::text,
    'manifest_digest', p_manifest_digest,
    'opened_by', p_opened_by,
    'opened_at', p_opened_at
  );
  IF p_cohort_body_json::jsonb <> expected_body THEN
    RAISE EXCEPTION 'audit cohort body fields do not match append coordinates' USING ERRCODE = '22000';
  END IF;
  IF p_cohort_hash <> 'sha256:' || encode(digest(convert_to(p_cohort_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'audit cohort hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.audit_cohort (
    cohort_uid, manifest_digest, opened_by, opened_at, cohort_hash
  ) VALUES (
    p_cohort_uid, p_manifest_digest, p_opened_by, p_opened_at, p_cohort_hash
  ) RETURNING * INTO inserted;
  RETURN inserted;
END;
$function$
```

### `audit_execution.open_audit_run`

Reads/writes: `audit_execution.audit_run`, `audit_execution.audit_run_event`

```sql
CREATE OR REPLACE FUNCTION audit_execution.open_audit_run(p_audit_run_uid uuid, p_work_item_uid uuid, p_request_uid uuid, p_request_digest text, p_request_envelope_digest text, p_metric_contract_uid uuid, p_metric_contract_version_uid uuid, p_package_snapshot_digest text, p_closure_root text, p_workflow_pack_digest text, p_instruction_package_digest text, p_methodology_digest text, p_source_authority_policy_digest text, p_opened_by text, p_opened_at text, p_event_uid uuid, p_event_hash text, p_event_body_json text, p_details_json text)
 RETURNS audit_execution.audit_run
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  inserted audit_execution.audit_run;
  expected_event jsonb;
BEGIN
  expected_event := jsonb_build_object(
    'event_uid', p_event_uid::text,
    'audit_run_uid', p_audit_run_uid::text,
    'event_sequence', 1,
    'event_kind', 'OPENED',
    'actor', p_opened_by,
    'details', p_details_json::jsonb,
    'prior_event_hash', NULL,
    'recorded_at', p_opened_at
  );
  IF p_event_body_json::jsonb <> expected_event THEN
    RAISE EXCEPTION 'audit-run open event body fields do not match append coordinates' USING ERRCODE = '22000';
  END IF;
  IF p_event_hash <> 'sha256:' || encode(digest(convert_to(p_event_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'audit-run open event hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.audit_run (
    audit_run_uid, work_item_uid, request_uid, request_digest, request_envelope_digest,
    metric_contract_uid, metric_contract_version_uid, package_snapshot_digest, closure_root,
    workflow_pack_digest, instruction_package_digest, methodology_digest, source_authority_policy_digest,
    opened_by, opened_at
  ) VALUES (
    p_audit_run_uid, p_work_item_uid, p_request_uid, p_request_digest, p_request_envelope_digest,
    p_metric_contract_uid, p_metric_contract_version_uid, p_package_snapshot_digest, p_closure_root,
    p_workflow_pack_digest, p_instruction_package_digest, p_methodology_digest, p_source_authority_policy_digest,
    p_opened_by, p_opened_at
  ) RETURNING * INTO inserted;
  INSERT INTO audit_execution.audit_run_event (
    event_uid, audit_run_uid, event_sequence, event_kind, actor, details_json,
    prior_event_hash, event_hash, recorded_at
  ) VALUES (
    p_event_uid, p_audit_run_uid, 1, 'OPENED', p_opened_by, p_details_json,
    NULL, p_event_hash, p_opened_at
  );
  RETURN inserted;
END;
$function$
```

### `audit_execution.publish_response_packet_outbox`

Reads/writes: `audit_execution.audit_cohort_member`, `audit_execution.audit_run`, `audit_execution.response_packet_outbox`

```sql
CREATE OR REPLACE FUNCTION audit_execution.publish_response_packet_outbox(p_outbox_uid uuid, p_work_item_uid uuid, p_audit_run_uid uuid, p_request_uid uuid, p_subject_uid uuid, p_terminal_status text, p_response_packet_digest text, p_response_packet_json text, p_outbox_hash text, p_ready_at text, p_outbox_body_json text)
 RETURNS audit_execution.response_packet_outbox
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  existing audit_execution.response_packet_outbox;
  inserted audit_execution.response_packet_outbox;
  expected_body jsonb;
BEGIN
  SELECT * INTO existing FROM audit_execution.response_packet_outbox WHERE audit_run_uid = p_audit_run_uid;
  IF FOUND THEN
    IF existing.response_packet_digest <> p_response_packet_digest OR existing.outbox_hash <> p_outbox_hash THEN
      RAISE EXCEPTION 'response packet outbox replay conflict' USING ERRCODE = '23505';
    END IF;
    RETURN existing;
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM audit_execution.audit_cohort_member
    WHERE work_item_uid = p_work_item_uid
      AND request_uid = p_request_uid
      AND subject_uid = p_subject_uid
  ) THEN
    RAISE EXCEPTION 'response packet coordinates do not match cohort member' USING ERRCODE = '22000';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM audit_execution.audit_run
    WHERE audit_run_uid = p_audit_run_uid
      AND work_item_uid = p_work_item_uid
      AND request_uid = p_request_uid
      AND metric_contract_version_uid = p_subject_uid
  ) THEN
    RAISE EXCEPTION 'response packet coordinates do not match retained audit run' USING ERRCODE = '22000';
  END IF;
  IF p_response_packet_digest <> p_response_packet_json::jsonb ->> 'response_packet_digest' THEN
    RAISE EXCEPTION 'response packet digest coordinate mismatch' USING ERRCODE = '22000';
  END IF;
  expected_body := jsonb_build_object(
    'outbox_uid', p_outbox_uid::text,
    'work_item_uid', p_work_item_uid::text,
    'audit_run_uid', p_audit_run_uid::text,
    'request_uid', p_request_uid::text,
    'subject_uid', p_subject_uid::text,
    'terminal_status', p_terminal_status,
    'response_packet_digest', p_response_packet_digest,
    'response_packet', p_response_packet_json::jsonb,
    'ready_at', p_ready_at
  );
  IF p_outbox_body_json::jsonb <> expected_body THEN
    RAISE EXCEPTION 'response packet outbox body fields do not match append coordinates' USING ERRCODE = '22000';
  END IF;
  IF p_outbox_hash <> 'sha256:' || encode(digest(convert_to(p_outbox_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'response packet outbox hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.response_packet_outbox (
    outbox_uid, work_item_uid, audit_run_uid, request_uid, subject_uid, terminal_status,
    response_packet_digest, response_packet_json, outbox_hash, ready_at
  ) VALUES (
    p_outbox_uid, p_work_item_uid, p_audit_run_uid, p_request_uid, p_subject_uid, p_terminal_status,
    p_response_packet_digest, p_response_packet_json, p_outbox_hash, p_ready_at
  ) RETURNING * INTO inserted;
  RETURN inserted;
END;
$function$
```

### `audit_execution.record_audit_run_refusal`

Reads/writes: `audit_execution.audit_run`, `audit_execution.audit_run_refusal`, `audit_execution.audit_run_refusal_code`, `audit_execution.audit_run_side_effect_status`, `prior.refusal_hash`

```sql
CREATE OR REPLACE FUNCTION audit_execution.record_audit_run_refusal(p_refusal_uid uuid, p_audit_run_uid uuid, p_refusal_sequence bigint, p_refusal_receipt_digest text, p_refusal_receipt_json text, p_prior_refusal_hash text, p_refusal_hash text, p_recorded_by text, p_recorded_at text, p_refusal_body_json text)
 RETURNS audit_execution.audit_run_refusal
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  prior audit_execution.audit_run_refusal;
  inserted audit_execution.audit_run_refusal;
BEGIN
  PERFORM 1 FROM audit_execution.audit_run WHERE audit_run_uid = p_audit_run_uid FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'audit run not found' USING ERRCODE = 'P0002'; END IF;
  SELECT * INTO prior FROM audit_execution.audit_run_refusal
    WHERE audit_run_uid = p_audit_run_uid ORDER BY refusal_sequence DESC LIMIT 1;
  IF p_refusal_sequence <> COALESCE(prior.refusal_sequence, 0) + 1
    OR p_prior_refusal_hash IS DISTINCT FROM prior.refusal_hash THEN
    RAISE EXCEPTION 'audit-run refusal stream changed' USING ERRCODE = '40001';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM audit_execution.audit_run_refusal_code
    WHERE code = p_refusal_receipt_json::jsonb ->> 'refusal_code'
  ) THEN
    RAISE EXCEPTION 'unsupported audit-run refusal code' USING ERRCODE = '55000';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM audit_execution.audit_run_side_effect_status
    WHERE code = p_refusal_receipt_json::jsonb ->> 'side_effect_status'
  ) THEN
    RAISE EXCEPTION 'unsupported audit-run side-effect status' USING ERRCODE = '55000';
  END IF;
  IF p_refusal_receipt_digest <> p_refusal_receipt_json::jsonb ->> 'refusal_receipt_digest' THEN
    RAISE EXCEPTION 'audit-run refusal receipt digest coordinate mismatch' USING ERRCODE = '22000';
  END IF;
  IF p_refusal_hash <> 'sha256:' || encode(digest(convert_to(p_refusal_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'audit-run refusal hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.audit_run_refusal (
    refusal_uid, audit_run_uid, refusal_sequence, refusal_receipt_digest, refusal_receipt_json,
    prior_refusal_hash, refusal_hash, recorded_by, recorded_at
  ) VALUES (
    p_refusal_uid, p_audit_run_uid, p_refusal_sequence, p_refusal_receipt_digest, p_refusal_receipt_json,
    p_prior_refusal_hash, p_refusal_hash, p_recorded_by, p_recorded_at
  ) RETURNING * INTO inserted;
  RETURN inserted;
END;
$function$
```

### `audit_execution.record_response_packet_pickup`

Reads/writes: `audit_execution.response_packet_pickup`

```sql
CREATE OR REPLACE FUNCTION audit_execution.record_response_packet_pickup(p_pickup_uid uuid, p_outbox_uid uuid, p_platform_receipt_json text, p_platform_receipt_digest text, p_pickup_hash text, p_picked_up_at text, p_pickup_body_json text)
 RETURNS audit_execution.response_packet_pickup
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  existing audit_execution.response_packet_pickup;
  inserted audit_execution.response_packet_pickup;
  expected_body jsonb;
BEGIN
  SELECT * INTO existing FROM audit_execution.response_packet_pickup WHERE outbox_uid = p_outbox_uid;
  IF FOUND THEN
    IF existing.platform_receipt_digest <> p_platform_receipt_digest OR existing.pickup_hash <> p_pickup_hash THEN
      RAISE EXCEPTION 'response packet pickup replay conflict' USING ERRCODE = '23505';
    END IF;
    RETURN existing;
  END IF;
  IF p_platform_receipt_digest <> 'sha256:' || encode(digest(convert_to(p_platform_receipt_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'platform pickup receipt digest mismatch' USING ERRCODE = '22000';
  END IF;
  expected_body := jsonb_build_object(
    'pickup_uid', p_pickup_uid::text,
    'outbox_uid', p_outbox_uid::text,
    'platform_receipt', p_platform_receipt_json::jsonb,
    'platform_receipt_digest', p_platform_receipt_digest,
    'picked_up_at', p_picked_up_at
  );
  IF p_pickup_body_json::jsonb <> expected_body THEN
    RAISE EXCEPTION 'response packet pickup body fields do not match append coordinates' USING ERRCODE = '22000';
  END IF;
  IF p_pickup_hash <> 'sha256:' || encode(digest(convert_to(p_pickup_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'response packet pickup hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.response_packet_pickup (
    pickup_uid, outbox_uid, platform_receipt_json, platform_receipt_digest, pickup_hash, picked_up_at
  ) VALUES (
    p_pickup_uid, p_outbox_uid, p_platform_receipt_json, p_platform_receipt_digest, p_pickup_hash, p_picked_up_at
  ) RETURNING * INTO inserted;
  RETURN inserted;
END;
$function$
```

### `audit_execution.register_evidence_object`

Reads/writes: `audit_execution.evidence_object`, `audit_execution.work_item`

```sql
CREATE OR REPLACE FUNCTION audit_execution.register_evidence_object(p_evidence_uid uuid, p_work_item_uid uuid, p_coordinate_json text, p_coordinate_digest text, p_content_bytes bytea, p_content_digest text, p_media_type text, p_retrieved_by text, p_retrieved_at text)
 RETURNS audit_execution.evidence_object
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  item audit_execution.work_item;
  inserted audit_execution.evidence_object;
BEGIN
  SELECT * INTO item FROM audit_execution.work_item WHERE work_item_uid = p_work_item_uid FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'audit work item not found' USING ERRCODE = 'P0002'; END IF;
  IF NOT EXISTS (
    SELECT 1 FROM jsonb_array_elements(item.request_payload_json::jsonb -> 'evidence_coordinates') coordinate
    WHERE coordinate = p_coordinate_json::jsonb
  ) THEN
    RAISE EXCEPTION 'evidence coordinate is not governed by the signed request' USING ERRCODE = '22000';
  END IF;
  IF p_coordinate_digest <> 'sha256:' || encode(digest(convert_to(p_coordinate_json, 'UTF8'), 'sha256'), 'hex')
    OR p_content_digest <> 'sha256:' || encode(digest(p_content_bytes, 'sha256'), 'hex')
    OR p_content_digest <> p_coordinate_json::jsonb ->> 'content_digest' THEN
    RAISE EXCEPTION 'evidence coordinate or content digest mismatch' USING ERRCODE = '22000';
  END IF;
  IF abs(extract(epoch FROM (p_retrieved_at::timestamptz - clock_timestamp()))) > 300 THEN
    RAISE EXCEPTION 'evidence retrieval timestamp is stale' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.evidence_object (
    evidence_uid, work_item_uid, coordinate_json, coordinate_digest, content_bytes,
    content_digest, media_type, retrieved_by, retrieved_at
  ) VALUES (
    p_evidence_uid, p_work_item_uid, p_coordinate_json, p_coordinate_digest, p_content_bytes,
    p_content_digest, p_media_type, p_retrieved_by, p_retrieved_at
  ) RETURNING * INTO inserted;
  RETURN inserted;
END;
$function$
```

### `audit_execution.retain_audit_run_artifact`

Reads/writes: `audit_execution.audit_run`, `audit_execution.audit_run_artifact`

```sql
CREATE OR REPLACE FUNCTION audit_execution.retain_audit_run_artifact(p_artifact_uid uuid, p_audit_run_uid uuid, p_artifact_kind text, p_artifact_digest text, p_artifact_json text, p_artifact_hash text, p_created_by text, p_created_at text, p_artifact_body_json text)
 RETURNS audit_execution.audit_run_artifact
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'audit_execution', 'public'
AS $function$
DECLARE
  inserted audit_execution.audit_run_artifact;
BEGIN
  PERFORM 1 FROM audit_execution.audit_run WHERE audit_run_uid = p_audit_run_uid FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'audit run not found' USING ERRCODE = 'P0002'; END IF;
  IF p_artifact_digest <> 'sha256:' || encode(digest(convert_to(p_artifact_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'audit-run artifact digest mismatch' USING ERRCODE = '22000';
  END IF;
  IF p_artifact_hash <> 'sha256:' || encode(digest(convert_to(p_artifact_body_json, 'UTF8'), 'sha256'), 'hex') THEN
    RAISE EXCEPTION 'audit-run artifact hash mismatch' USING ERRCODE = '22000';
  END IF;
  INSERT INTO audit_execution.audit_run_artifact (
    artifact_uid, audit_run_uid, artifact_kind, artifact_digest, artifact_json,
    artifact_hash, created_by, created_at
  ) VALUES (
    p_artifact_uid, p_audit_run_uid, p_artifact_kind, p_artifact_digest, p_artifact_json,
    p_artifact_hash, p_created_by, p_created_at
  ) RETURNING * INTO inserted;
  RETURN inserted;
END;
$function$
```

## 7. Checker-side substrate constraints — `audit_execution`

### `audit_execution.audit_cohort`

Columns: 5 | **NOT NULL:** `cohort_uid`, `manifest_digest`, `opened_by`, `opened_at`, `cohort_hash`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_cohort_cohort_hash_check` | `CHECK ((cohort_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_cohort_manifest_digest_check` | `CHECK ((manifest_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_cohort_opened_by_check` | `CHECK ((length(btrim(opened_by)) > 0))` |
| PK | `audit_cohort_pkey` | `PRIMARY KEY (cohort_uid)` |
| UNIQUE | `audit_cohort_cohort_hash_key` | `UNIQUE (cohort_hash)` |

Triggers:

- `audit_cohort_no_delete`: `audit_cohort_no_delete BEFORE DELETE ON audit_execution.audit_cohort FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_cohort_no_update`: `audit_cohort_no_update BEFORE UPDATE ON audit_execution.audit_cohort FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_cohort_member`

Columns: 7 | **NOT NULL:** `work_item_uid`, `cohort_uid`, `batch_uid`, `request_uid`, `subject_uid`, `attached_at`, `member_hash`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_cohort_member_batch_uid_check` | `CHECK ((length(btrim(batch_uid)) > 0))` |
| CHECK | `audit_cohort_member_member_hash_check` | `CHECK ((member_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| FK | `audit_cohort_member_cohort_uid_fkey` | `FOREIGN KEY (cohort_uid) REFERENCES audit_execution.audit_cohort(cohort_uid) ON DELETE RESTRICT` |
| FK | `audit_cohort_member_work_item_uid_fkey` | `FOREIGN KEY (work_item_uid) REFERENCES audit_execution.work_item(work_item_uid) ON DELETE RESTRICT` |
| PK | `audit_cohort_member_pkey` | `PRIMARY KEY (work_item_uid)` |
| UNIQUE | `audit_cohort_member_cohort_uid_request_uid_key` | `UNIQUE (cohort_uid, request_uid)` |
| UNIQUE | `audit_cohort_member_cohort_uid_subject_uid_key` | `UNIQUE (cohort_uid, subject_uid)` |
| UNIQUE | `audit_cohort_member_member_hash_key` | `UNIQUE (member_hash)` |

Triggers:

- `audit_cohort_member_no_delete`: `audit_cohort_member_no_delete BEFORE DELETE ON audit_execution.audit_cohort_member FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_cohort_member_no_update`: `audit_cohort_member_no_update BEFORE UPDATE ON audit_execution.audit_cohort_member FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_cohort_member_event`

Columns: 8 | **NOT NULL:** `event_uid`, `work_item_uid`, `event_sequence`, `event_kind`, `details_json`, `event_hash`, `recorded_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_cohort_member_event_details_json_check` | `CHECK ((jsonb_typeof((details_json)::jsonb) = 'object'::text))` |
| CHECK | `audit_cohort_member_event_event_hash_check` | `CHECK ((event_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_cohort_member_event_event_kind_check` | `CHECK ((event_kind = ANY (ARRAY['DISCOVERED'::text, 'RUNNING'::text, 'PACKET_READY'::text, 'PLATFORM_PICKED_UP'::text, 'PLATFORM_ADMITTED'::text, 'REFUSED'::text, 'HALTED'::text, 'DEFERRED'::text])))` |
| CHECK | `audit_cohort_member_event_event_sequence_check` | `CHECK ((event_sequence > 0))` |
| CHECK | `audit_cohort_member_event_prior_event_hash_check` | `CHECK (((prior_event_hash IS NULL) OR (prior_event_hash ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| FK | `audit_cohort_member_event_work_item_uid_fkey` | `FOREIGN KEY (work_item_uid) REFERENCES audit_execution.audit_cohort_member(work_item_uid) ON DELETE RESTRICT` |
| PK | `audit_cohort_member_event_pkey` | `PRIMARY KEY (event_uid)` |
| UNIQUE | `audit_cohort_member_event_event_hash_key` | `UNIQUE (event_hash)` |
| UNIQUE | `audit_cohort_member_event_work_item_uid_event_sequence_key` | `UNIQUE (work_item_uid, event_sequence)` |

Triggers:

- `audit_cohort_member_event_no_delete`: `audit_cohort_member_event_no_delete BEFORE DELETE ON audit_execution.audit_cohort_member_event FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_cohort_member_event_no_update`: `audit_cohort_member_event_no_update BEFORE UPDATE ON audit_execution.audit_cohort_member_event FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run`

Columns: 15 | **NOT NULL:** `audit_run_uid`, `request_uid`, `request_digest`, `request_envelope_digest`, `metric_contract_uid`, `metric_contract_version_uid`, `package_snapshot_digest`, `closure_root`, `workflow_pack_digest`, `instruction_package_digest`, `methodology_digest`, `source_authority_policy_digest`, `opened_by`, `opened_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_closure_root_check` | `CHECK ((closure_root ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_instruction_package_digest_check` | `CHECK ((instruction_package_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_methodology_digest_check` | `CHECK ((methodology_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_opened_by_check` | `CHECK ((length(btrim(opened_by)) > 0))` |
| CHECK | `audit_run_package_snapshot_digest_check` | `CHECK ((package_snapshot_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_request_digest_check` | `CHECK ((request_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_request_envelope_digest_check` | `CHECK ((request_envelope_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_source_authority_policy_digest_check` | `CHECK ((source_authority_policy_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_workflow_pack_digest_check` | `CHECK ((workflow_pack_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| FK | `audit_run_work_item_uid_fkey` | `FOREIGN KEY (work_item_uid) REFERENCES audit_execution.work_item(work_item_uid) ON DELETE RESTRICT` |
| PK | `audit_run_pkey` | `PRIMARY KEY (audit_run_uid)` |
| UNIQUE | `audit_run_request_uid_key` | `UNIQUE (request_uid)` |

Triggers:

- `audit_run_no_delete`: `audit_run_no_delete BEFORE DELETE ON audit_execution.audit_run FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_no_update`: `audit_run_no_update BEFORE UPDATE ON audit_execution.audit_run FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_allowed_action`

Columns: 2 | **NOT NULL:** `code`, `sort_order`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_allowed_action_sort_order_check` | `CHECK ((sort_order > 0))` |
| PK | `audit_run_allowed_action_pkey` | `PRIMARY KEY (code)` |
| UNIQUE | `audit_run_allowed_action_sort_order_key` | `UNIQUE (sort_order)` |

Triggers:

- `audit_run_allowed_action_no_delete`: `audit_run_allowed_action_no_delete BEFORE DELETE ON audit_execution.audit_run_allowed_action FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_allowed_action_no_update`: `audit_run_allowed_action_no_update BEFORE UPDATE ON audit_execution.audit_run_allowed_action FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_artifact`

Columns: 8 | **NOT NULL:** `artifact_uid`, `audit_run_uid`, `artifact_kind`, `artifact_digest`, `artifact_json`, `artifact_hash`, `created_by`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_artifact_artifact_digest_check` | `CHECK ((artifact_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_artifact_artifact_hash_check` | `CHECK ((artifact_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_artifact_artifact_json_check` | `CHECK ((jsonb_typeof((artifact_json)::jsonb) = 'object'::text))` |
| CHECK | `audit_run_artifact_created_by_check` | `CHECK ((length(btrim(created_by)) > 0))` |
| FK | `audit_run_artifact_artifact_kind_fkey` | `FOREIGN KEY (artifact_kind) REFERENCES audit_execution.audit_run_artifact_kind(code) ON DELETE RESTRICT` |
| FK | `audit_run_artifact_audit_run_uid_fkey` | `FOREIGN KEY (audit_run_uid) REFERENCES audit_execution.audit_run(audit_run_uid) ON DELETE RESTRICT` |
| PK | `audit_run_artifact_pkey` | `PRIMARY KEY (artifact_uid)` |
| UNIQUE | `audit_run_artifact_artifact_hash_key` | `UNIQUE (artifact_hash)` |

Triggers:

- `audit_run_artifact_no_delete`: `audit_run_artifact_no_delete BEFORE DELETE ON audit_execution.audit_run_artifact FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_artifact_no_update`: `audit_run_artifact_no_update BEFORE UPDATE ON audit_execution.audit_run_artifact FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_artifact_kind`

Columns: 2 | **NOT NULL:** `code`, `sort_order`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_artifact_kind_sort_order_check` | `CHECK ((sort_order > 0))` |
| PK | `audit_run_artifact_kind_pkey` | `PRIMARY KEY (code)` |
| UNIQUE | `audit_run_artifact_kind_sort_order_key` | `UNIQUE (sort_order)` |

Triggers:

- `audit_run_artifact_kind_no_delete`: `audit_run_artifact_kind_no_delete BEFORE DELETE ON audit_execution.audit_run_artifact_kind FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_artifact_kind_no_update`: `audit_run_artifact_kind_no_update BEFORE UPDATE ON audit_execution.audit_run_artifact_kind FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_bootstrap_authority`

Columns: 9 | **NOT NULL:** `manifest_uid`, `target_database`, `connection_role`, `workflow_pack_digest`, `instruction_package_digest`, `engine`, `engine_version`, `expected_vocabulary_digest`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_bootstrap_authority_connection_role_check` | `CHECK ((length(btrim(connection_role)) > 0))` |
| CHECK | `audit_run_bootstrap_authority_engine_check` | `CHECK ((length(btrim(engine)) > 0))` |
| CHECK | `audit_run_bootstrap_authority_engine_version_check` | `CHECK ((length(btrim(engine_version)) > 0))` |
| CHECK | `audit_run_bootstrap_authority_expected_vocabulary_digest_check` | `CHECK ((expected_vocabulary_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_bootstrap_authority_instruction_package_digest_check` | `CHECK ((instruction_package_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_bootstrap_authority_target_database_check` | `CHECK ((length(btrim(target_database)) > 0))` |
| CHECK | `audit_run_bootstrap_authority_workflow_pack_digest_check` | `CHECK ((workflow_pack_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| PK | `audit_run_bootstrap_authority_pkey` | `PRIMARY KEY (manifest_uid)` |

Triggers:

- `audit_run_bootstrap_authority_no_delete`: `audit_run_bootstrap_authority_no_delete BEFORE DELETE ON audit_execution.audit_run_bootstrap_authority FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_bootstrap_authority_no_update`: `audit_run_bootstrap_authority_no_update BEFORE UPDATE ON audit_execution.audit_run_bootstrap_authority FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_bootstrap_authority_event`

Columns: 11 | **NOT NULL:** `event_uid`, `event_sequence`, `predecessor_manifest_uid`, `predecessor_manifest_digest`, `successor_manifest_uid`, `successor_manifest_digest`, `expected_vocabulary_digest`, `authority_ref`, `accepted_by`, `accepted_at`, `event_hash`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_bootstrap_authority_e_successor_manifest_digest_check` | `CHECK ((successor_manifest_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_bootstrap_authority_event_accepted_by_check` | `CHECK ((length(btrim(accepted_by)) > 0))` |
| CHECK | `audit_run_bootstrap_authority_event_authority_ref_check` | `CHECK ((length(btrim(authority_ref)) > 0))` |
| CHECK | `audit_run_bootstrap_authority_event_event_hash_check` | `CHECK ((event_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_bootstrap_authority_event_event_sequence_check` | `CHECK ((event_sequence > 0))` |
| CHECK | `audit_run_bootstrap_authority_expected_vocabulary_digest_check1` | `CHECK ((expected_vocabulary_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_bootstrap_authority_predecessor_manifest_digest_check` | `CHECK ((predecessor_manifest_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| PK | `audit_run_bootstrap_authority_event_pkey` | `PRIMARY KEY (event_uid)` |
| UNIQUE | `audit_run_bootstrap_authority_eve_successor_manifest_digest_key` | `UNIQUE (successor_manifest_digest)` |
| UNIQUE | `audit_run_bootstrap_authority_event_event_hash_key` | `UNIQUE (event_hash)` |
| UNIQUE | `audit_run_bootstrap_authority_event_event_sequence_key` | `UNIQUE (event_sequence)` |
| UNIQUE | `audit_run_bootstrap_authority_event_successor_manifest_uid_key` | `UNIQUE (successor_manifest_uid)` |

Triggers:

- `audit_run_bootstrap_authority_event_no_delete`: `audit_run_bootstrap_authority_event_no_delete BEFORE DELETE ON audit_execution.audit_run_bootstrap_authority_event FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_bootstrap_authority_event_no_update`: `audit_run_bootstrap_authority_event_no_update BEFORE UPDATE ON audit_execution.audit_run_bootstrap_authority_event FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_bootstrap_authority_successor`

Columns: 9 | **NOT NULL:** `successor_uid`, `predecessor_manifest_uid`, `manifest_uid`, `manifest_digest`, `expected_vocabulary_digest`, `authority_ref`, `accepted_by`, `accepted_at`, `successor_hash`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_bootstrap_authority__expected_vocabulary_digest_check` | `CHECK ((expected_vocabulary_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_bootstrap_authority_successor_accepted_by_check` | `CHECK ((length(btrim(accepted_by)) > 0))` |
| CHECK | `audit_run_bootstrap_authority_successor_authority_ref_check` | `CHECK ((length(btrim(authority_ref)) > 0))` |
| CHECK | `audit_run_bootstrap_authority_successor_manifest_digest_check` | `CHECK ((manifest_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_bootstrap_authority_successor_successor_hash_check` | `CHECK ((successor_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| FK | `audit_run_bootstrap_authority_suc_predecessor_manifest_uid_fkey` | `FOREIGN KEY (predecessor_manifest_uid) REFERENCES audit_execution.audit_run_bootstrap_authority(manifest_uid) ON DELETE RESTRICT` |
| PK | `audit_run_bootstrap_authority_successor_pkey` | `PRIMARY KEY (successor_uid)` |
| UNIQUE | `audit_run_bootstrap_authority_successor_manifest_digest_key` | `UNIQUE (manifest_digest)` |
| UNIQUE | `audit_run_bootstrap_authority_successor_manifest_uid_key` | `UNIQUE (manifest_uid)` |
| UNIQUE | `audit_run_bootstrap_authority_successor_successor_hash_key` | `UNIQUE (successor_hash)` |

Triggers:

- `audit_run_bootstrap_authority_successor_no_delete`: `audit_run_bootstrap_authority_successor_no_delete BEFORE DELETE ON audit_execution.audit_run_bootstrap_authority_successor FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_bootstrap_authority_successor_no_update`: `audit_run_bootstrap_authority_successor_no_update BEFORE UPDATE ON audit_execution.audit_run_bootstrap_authority_successor FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_event`

Columns: 9 | **NOT NULL:** `event_uid`, `audit_run_uid`, `event_sequence`, `event_kind`, `actor`, `details_json`, `event_hash`, `recorded_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_event_actor_check` | `CHECK ((length(btrim(actor)) > 0))` |
| CHECK | `audit_run_event_details_json_check` | `CHECK ((jsonb_typeof((details_json)::jsonb) = 'object'::text))` |
| CHECK | `audit_run_event_event_hash_check` | `CHECK ((event_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_event_event_sequence_check` | `CHECK ((event_sequence > 0))` |
| CHECK | `audit_run_event_prior_event_hash_check` | `CHECK (((prior_event_hash IS NULL) OR (prior_event_hash ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| FK | `audit_run_event_audit_run_uid_fkey` | `FOREIGN KEY (audit_run_uid) REFERENCES audit_execution.audit_run(audit_run_uid) ON DELETE RESTRICT` |
| FK | `audit_run_event_event_kind_fkey` | `FOREIGN KEY (event_kind) REFERENCES audit_execution.audit_run_state(code) ON DELETE RESTRICT` |
| PK | `audit_run_event_pkey` | `PRIMARY KEY (event_uid)` |
| UNIQUE | `audit_run_event_audit_run_uid_event_sequence_key` | `UNIQUE (audit_run_uid, event_sequence)` |
| UNIQUE | `audit_run_event_event_hash_key` | `UNIQUE (event_hash)` |

Triggers:

- `audit_run_event_no_delete`: `audit_run_event_no_delete BEFORE DELETE ON audit_execution.audit_run_event FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_event_no_update`: `audit_run_event_no_update BEFORE UPDATE ON audit_execution.audit_run_event FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_refusal`

Columns: 9 | **NOT NULL:** `refusal_uid`, `audit_run_uid`, `refusal_sequence`, `refusal_receipt_digest`, `refusal_receipt_json`, `refusal_hash`, `recorded_by`, `recorded_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_refusal_prior_refusal_hash_check` | `CHECK (((prior_refusal_hash IS NULL) OR (prior_refusal_hash ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| CHECK | `audit_run_refusal_recorded_by_check` | `CHECK ((length(btrim(recorded_by)) > 0))` |
| CHECK | `audit_run_refusal_refusal_hash_check` | `CHECK ((refusal_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_refusal_refusal_receipt_digest_check` | `CHECK ((refusal_receipt_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `audit_run_refusal_refusal_receipt_json_check` | `CHECK ((jsonb_typeof((refusal_receipt_json)::jsonb) = 'object'::text))` |
| CHECK | `audit_run_refusal_refusal_sequence_check` | `CHECK ((refusal_sequence > 0))` |
| FK | `audit_run_refusal_audit_run_uid_fkey` | `FOREIGN KEY (audit_run_uid) REFERENCES audit_execution.audit_run(audit_run_uid) ON DELETE RESTRICT` |
| PK | `audit_run_refusal_pkey` | `PRIMARY KEY (refusal_uid)` |
| UNIQUE | `audit_run_refusal_audit_run_uid_refusal_sequence_key` | `UNIQUE (audit_run_uid, refusal_sequence)` |
| UNIQUE | `audit_run_refusal_refusal_hash_key` | `UNIQUE (refusal_hash)` |

Triggers:

- `audit_run_refusal_no_delete`: `audit_run_refusal_no_delete BEFORE DELETE ON audit_execution.audit_run_refusal FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_refusal_no_update`: `audit_run_refusal_no_update BEFORE UPDATE ON audit_execution.audit_run_refusal FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_refusal_code`

Columns: 2 | **NOT NULL:** `code`, `sort_order`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_refusal_code_sort_order_check` | `CHECK ((sort_order > 0))` |
| PK | `audit_run_refusal_code_pkey` | `PRIMARY KEY (code)` |
| UNIQUE | `audit_run_refusal_code_sort_order_key` | `UNIQUE (sort_order)` |

Triggers:

- `audit_run_refusal_code_no_delete`: `audit_run_refusal_code_no_delete BEFORE DELETE ON audit_execution.audit_run_refusal_code FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_refusal_code_no_update`: `audit_run_refusal_code_no_update BEFORE UPDATE ON audit_execution.audit_run_refusal_code FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_schema_digest`

Columns: 2 | **NOT NULL:** `schema_kind`, `schema_digest`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_schema_digest_schema_digest_check` | `CHECK ((schema_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| PK | `audit_run_schema_digest_pkey` | `PRIMARY KEY (schema_kind)` |

Triggers:

- `audit_run_schema_digest_no_delete`: `audit_run_schema_digest_no_delete BEFORE DELETE ON audit_execution.audit_run_schema_digest FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_schema_digest_no_update`: `audit_run_schema_digest_no_update BEFORE UPDATE ON audit_execution.audit_run_schema_digest FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_side_effect_status`

Columns: 2 | **NOT NULL:** `code`, `sort_order`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_side_effect_status_sort_order_check` | `CHECK ((sort_order > 0))` |
| PK | `audit_run_side_effect_status_pkey` | `PRIMARY KEY (code)` |
| UNIQUE | `audit_run_side_effect_status_sort_order_key` | `UNIQUE (sort_order)` |

Triggers:

- `audit_run_side_effect_status_no_delete`: `audit_run_side_effect_status_no_delete BEFORE DELETE ON audit_execution.audit_run_side_effect_status FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_side_effect_status_no_update`: `audit_run_side_effect_status_no_update BEFORE UPDATE ON audit_execution.audit_run_side_effect_status FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_state`

Columns: 2 | **NOT NULL:** `code`, `sort_order`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_state_sort_order_check` | `CHECK ((sort_order > 0))` |
| PK | `audit_run_state_pkey` | `PRIMARY KEY (code)` |
| UNIQUE | `audit_run_state_sort_order_key` | `UNIQUE (sort_order)` |

Triggers:

- `audit_run_state_no_delete`: `audit_run_state_no_delete BEFORE DELETE ON audit_execution.audit_run_state FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_state_no_update`: `audit_run_state_no_update BEFORE UPDATE ON audit_execution.audit_run_state FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.audit_run_terminal_status`

Columns: 2 | **NOT NULL:** `code`, `sort_order`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `audit_run_terminal_status_sort_order_check` | `CHECK ((sort_order > 0))` |
| PK | `audit_run_terminal_status_pkey` | `PRIMARY KEY (code)` |
| UNIQUE | `audit_run_terminal_status_sort_order_key` | `UNIQUE (sort_order)` |

Triggers:

- `audit_run_terminal_status_no_delete`: `audit_run_terminal_status_no_delete BEFORE DELETE ON audit_execution.audit_run_terminal_status FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `audit_run_terminal_status_no_update`: `audit_run_terminal_status_no_update BEFORE UPDATE ON audit_execution.audit_run_terminal_status FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.contextual_release_authority`

Columns: 15 | **NOT NULL:** `authority_uid`, `contextual_release_uid`, `contextual_release_ratification_digest`, `acceptance_manifest_digest`, `component_digests_json`, `methodology_release_uid`, `methodology_version`, `methodology_digest`, `methodology_release_ratification_digest`, `platform_pin_uid`, `platform_pin_digest`, `platform_pin_evidence_ref`, `platform_pin_evidence_digest`, `authority_ref`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `contextual_release_authority_acceptance_manifest_digest_check` | `CHECK ((acceptance_manifest_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `contextual_release_authority_authority_ref_check` | `CHECK ((length(btrim(authority_ref)) > 0))` |
| CHECK | `contextual_release_authority_component_digests_json_check` | `CHECK ((jsonb_typeof((component_digests_json)::jsonb) = 'object'::text))` |
| CHECK | `contextual_release_authority_contextual_release_ratificat_check` | `CHECK ((contextual_release_ratification_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `contextual_release_authority_methodology_digest_check` | `CHECK ((methodology_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `contextual_release_authority_methodology_release_ratifica_check` | `CHECK ((methodology_release_ratification_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `contextual_release_authority_methodology_version_check` | `CHECK ((length(btrim(methodology_version)) > 0))` |
| CHECK | `contextual_release_authority_platform_pin_digest_check` | `CHECK ((platform_pin_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `contextual_release_authority_platform_pin_evidence_digest_check` | `CHECK ((platform_pin_evidence_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `contextual_release_authority_platform_pin_evidence_ref_check` | `CHECK ((length(btrim(platform_pin_evidence_ref)) > 0))` |
| PK | `contextual_release_authority_pkey` | `PRIMARY KEY (authority_uid)` |

Triggers:

- `contextual_release_authority_no_delete`: `contextual_release_authority_no_delete BEFORE DELETE ON audit_execution.contextual_release_authority FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `contextual_release_authority_no_update`: `contextual_release_authority_no_update BEFORE UPDATE ON audit_execution.contextual_release_authority FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.contextual_release_binding`

Columns: 8 | **NOT NULL:** `binding_uid`, `audit_run_uid`, `bootstrap_manifest_uid`, `bootstrap_manifest_digest`, `binding_json`, `binding_digest`, `bound_by`, `bound_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `contextual_release_binding_binding_digest_check` | `CHECK ((binding_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `contextual_release_binding_binding_json_check` | `CHECK ((jsonb_typeof((binding_json)::jsonb) = 'object'::text))` |
| CHECK | `contextual_release_binding_bootstrap_manifest_digest_check` | `CHECK ((bootstrap_manifest_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `contextual_release_binding_bound_by_check` | `CHECK ((length(btrim(bound_by)) > 0))` |
| FK | `contextual_release_binding_audit_run_uid_fkey` | `FOREIGN KEY (audit_run_uid) REFERENCES audit_execution.audit_run(audit_run_uid) ON DELETE RESTRICT` |
| PK | `contextual_release_binding_pkey` | `PRIMARY KEY (binding_uid)` |
| UNIQUE | `contextual_release_binding_audit_run_uid_key` | `UNIQUE (audit_run_uid)` |
| UNIQUE | `contextual_release_binding_binding_digest_key` | `UNIQUE (binding_digest)` |

Triggers:

- `contextual_release_binding_no_delete`: `contextual_release_binding_no_delete BEFORE DELETE ON audit_execution.contextual_release_binding FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `contextual_release_binding_no_update`: `contextual_release_binding_no_update BEFORE UPDATE ON audit_execution.contextual_release_binding FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.evidence_object`

Columns: 9 | **NOT NULL:** `evidence_uid`, `work_item_uid`, `coordinate_json`, `coordinate_digest`, `content_bytes`, `content_digest`, `media_type`, `retrieved_by`, `retrieved_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `evidence_object_content_digest_check` | `CHECK ((content_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `evidence_object_coordinate_digest_check` | `CHECK ((coordinate_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `evidence_object_coordinate_json_check` | `CHECK ((jsonb_typeof((coordinate_json)::jsonb) = 'object'::text))` |
| CHECK | `evidence_object_media_type_check` | `CHECK ((length(btrim(media_type)) > 0))` |
| CHECK | `evidence_object_retrieved_by_check` | `CHECK ((length(btrim(retrieved_by)) > 0))` |
| FK | `evidence_object_work_item_uid_fkey` | `FOREIGN KEY (work_item_uid) REFERENCES audit_execution.work_item(work_item_uid) ON DELETE RESTRICT` |
| PK | `evidence_object_pkey` | `PRIMARY KEY (evidence_uid)` |
| UNIQUE | `evidence_object_work_item_uid_coordinate_digest_key` | `UNIQUE (work_item_uid, coordinate_digest)` |
| UNIQUE | `evidence_object_work_item_uid_evidence_uid_content_digest_key` | `UNIQUE (work_item_uid, evidence_uid, content_digest)` |

Triggers:

- `evidence_object_no_delete`: `evidence_object_no_delete BEFORE DELETE ON audit_execution.evidence_object FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `evidence_object_no_update`: `evidence_object_no_update BEFORE UPDATE ON audit_execution.evidence_object FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.outbound_feed_bootstrap`

Columns: 8 | **NOT NULL:** `feed_name`, `next_sequence`, `signer_key_id`, `signer_fingerprint`, `authority_ref`, `registered_at`, `bootstrap_hash`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `outbound_feed_bootstrap_authority_ref_check` | `CHECK ((length(btrim(authority_ref)) > 0))` |
| CHECK | `outbound_feed_bootstrap_bootstrap_hash_check` | `CHECK ((bootstrap_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `outbound_feed_bootstrap_feed_name_check` | `CHECK ((length(btrim(feed_name)) > 0))` |
| CHECK | `outbound_feed_bootstrap_next_sequence_check` | `CHECK ((next_sequence > 0))` |
| CHECK | `outbound_feed_bootstrap_prior_envelope_digest_check` | `CHECK (((prior_envelope_digest IS NULL) OR (prior_envelope_digest ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| CHECK | `outbound_feed_bootstrap_signer_fingerprint_check` | `CHECK ((signer_fingerprint ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `outbound_feed_bootstrap_signer_key_id_check` | `CHECK ((length(btrim(signer_key_id)) > 0))` |
| PK | `outbound_feed_bootstrap_pkey` | `PRIMARY KEY (feed_name)` |
| UNIQUE | `outbound_feed_bootstrap_bootstrap_hash_key` | `UNIQUE (bootstrap_hash)` |

Triggers:

- `outbound_feed_bootstrap_no_delete`: `outbound_feed_bootstrap_no_delete BEFORE DELETE ON audit_execution.outbound_feed_bootstrap FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `outbound_feed_bootstrap_no_update`: `outbound_feed_bootstrap_no_update BEFORE UPDATE ON audit_execution.outbound_feed_bootstrap FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.outbound_feed_publication`

Columns: 15 | **NOT NULL:** `publication_uid`, `audit_run_uid`, `feed_name`, `report_sequence`, `decision_sequence`, `report_envelope_digest`, `decision_envelope_digest`, `publication_preflight_digest`, `signer_key_id`, `signer_fingerprint`, `transport_receipt_digest`, `publication_input_digest`, `published_at`, `publication_hash`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `outbound_feed_publication_check` | `CHECK ((decision_sequence = (report_sequence + 1)))` |
| CHECK | `outbound_feed_publication_decision_envelope_digest_check` | `CHECK ((decision_envelope_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `outbound_feed_publication_prior_envelope_digest_check` | `CHECK (((prior_envelope_digest IS NULL) OR (prior_envelope_digest ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| CHECK | `outbound_feed_publication_publication_hash_check` | `CHECK ((publication_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `outbound_feed_publication_publication_input_digest_check` | `CHECK ((publication_input_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `outbound_feed_publication_publication_preflight_digest_check` | `CHECK ((publication_preflight_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `outbound_feed_publication_report_envelope_digest_check` | `CHECK ((report_envelope_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `outbound_feed_publication_report_sequence_check` | `CHECK ((report_sequence > 0))` |
| CHECK | `outbound_feed_publication_signer_fingerprint_check` | `CHECK ((signer_fingerprint ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `outbound_feed_publication_signer_key_id_check` | `CHECK ((length(btrim(signer_key_id)) > 0))` |
| CHECK | `outbound_feed_publication_transport_receipt_digest_check` | `CHECK ((transport_receipt_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| FK | `outbound_feed_publication_audit_run_uid_fkey` | `FOREIGN KEY (audit_run_uid) REFERENCES audit_execution.audit_run(audit_run_uid) ON DELETE RESTRICT` |
| FK | `outbound_feed_publication_feed_name_fkey` | `FOREIGN KEY (feed_name) REFERENCES audit_execution.outbound_feed_bootstrap(feed_name) ON DELETE RESTRICT` |
| PK | `outbound_feed_publication_pkey` | `PRIMARY KEY (publication_uid)` |
| UNIQUE | `outbound_feed_publication_audit_run_uid_key` | `UNIQUE (audit_run_uid)` |
| UNIQUE | `outbound_feed_publication_decision_envelope_digest_key` | `UNIQUE (decision_envelope_digest)` |
| UNIQUE | `outbound_feed_publication_feed_name_decision_sequence_key` | `UNIQUE (feed_name, decision_sequence)` |
| UNIQUE | `outbound_feed_publication_feed_name_report_sequence_key` | `UNIQUE (feed_name, report_sequence)` |
| UNIQUE | `outbound_feed_publication_publication_hash_key` | `UNIQUE (publication_hash)` |
| UNIQUE | `outbound_feed_publication_report_envelope_digest_key` | `UNIQUE (report_envelope_digest)` |
| UNIQUE | `outbound_feed_publication_transport_receipt_digest_key` | `UNIQUE (transport_receipt_digest)` |

Triggers:

- `outbound_feed_publication_no_delete`: `outbound_feed_publication_no_delete BEFORE DELETE ON audit_execution.outbound_feed_publication FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `outbound_feed_publication_no_update`: `outbound_feed_publication_no_update BEFORE UPDATE ON audit_execution.outbound_feed_publication FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.response_packet_outbox`

Columns: 10 | **NOT NULL:** `outbox_uid`, `work_item_uid`, `audit_run_uid`, `request_uid`, `subject_uid`, `terminal_status`, `response_packet_digest`, `response_packet_json`, `outbox_hash`, `ready_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `response_packet_outbox_outbox_hash_check` | `CHECK ((outbox_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `response_packet_outbox_response_packet_digest_check` | `CHECK ((response_packet_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `response_packet_outbox_response_packet_json_check` | `CHECK ((jsonb_typeof((response_packet_json)::jsonb) = 'object'::text))` |
| CHECK | `response_packet_outbox_terminal_status_check` | `CHECK ((length(btrim(terminal_status)) > 0))` |
| FK | `response_packet_outbox_audit_run_uid_fkey` | `FOREIGN KEY (audit_run_uid) REFERENCES audit_execution.audit_run(audit_run_uid) ON DELETE RESTRICT` |
| FK | `response_packet_outbox_work_item_uid_fkey` | `FOREIGN KEY (work_item_uid) REFERENCES audit_execution.audit_cohort_member(work_item_uid) ON DELETE RESTRICT` |
| PK | `response_packet_outbox_pkey` | `PRIMARY KEY (outbox_uid)` |
| UNIQUE | `response_packet_outbox_audit_run_uid_key` | `UNIQUE (audit_run_uid)` |
| UNIQUE | `response_packet_outbox_outbox_hash_key` | `UNIQUE (outbox_hash)` |
| UNIQUE | `response_packet_outbox_response_packet_digest_key` | `UNIQUE (response_packet_digest)` |
| UNIQUE | `response_packet_outbox_work_item_uid_key` | `UNIQUE (work_item_uid)` |

Triggers:

- `response_packet_outbox_no_delete`: `response_packet_outbox_no_delete BEFORE DELETE ON audit_execution.response_packet_outbox FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `response_packet_outbox_no_update`: `response_packet_outbox_no_update BEFORE UPDATE ON audit_execution.response_packet_outbox FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.response_packet_pickup`

Columns: 6 | **NOT NULL:** `pickup_uid`, `outbox_uid`, `platform_receipt_json`, `platform_receipt_digest`, `pickup_hash`, `picked_up_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `response_packet_pickup_pickup_hash_check` | `CHECK ((pickup_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `response_packet_pickup_platform_receipt_digest_check` | `CHECK ((platform_receipt_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `response_packet_pickup_platform_receipt_json_check` | `CHECK ((jsonb_typeof((platform_receipt_json)::jsonb) = 'object'::text))` |
| FK | `response_packet_pickup_outbox_uid_fkey` | `FOREIGN KEY (outbox_uid) REFERENCES audit_execution.response_packet_outbox(outbox_uid) ON DELETE RESTRICT` |
| PK | `response_packet_pickup_pkey` | `PRIMARY KEY (pickup_uid)` |
| UNIQUE | `response_packet_pickup_outbox_uid_key` | `UNIQUE (outbox_uid)` |
| UNIQUE | `response_packet_pickup_pickup_hash_key` | `UNIQUE (pickup_hash)` |
| UNIQUE | `response_packet_pickup_platform_receipt_digest_key` | `UNIQUE (platform_receipt_digest)` |

Triggers:

- `response_packet_pickup_no_delete`: `response_packet_pickup_no_delete BEFORE DELETE ON audit_execution.response_packet_pickup FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `response_packet_pickup_no_update`: `response_packet_pickup_no_update BEFORE UPDATE ON audit_execution.response_packet_pickup FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.work_context`

Columns: 10 | **NOT NULL:** `context_uid`, `work_item_uid`, `context_version`, `grounding_status`, `context_package_json`, `context_package_digest`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `work_context_check` | `CHECK ((((context_version = 1) AND (grounding_status = 'COORDINATES_ONLY'::text) AND (previous_context_uid IS NULL) AND (previous_context_digest IS NULL) AND (grounded_by IS NULL)) OR ((context_version > 1) AND (grounding_status = 'VERIFIED'::text) AND (previous_context_uid IS NOT NULL) AND (previous_context_digest IS NOT NULL) AND (length(btrim(grounded_by)) > 0))))` |
| CHECK | `work_context_context_package_digest_check` | `CHECK ((context_package_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `work_context_context_package_json_check` | `CHECK ((jsonb_typeof((context_package_json)::jsonb) = 'object'::text))` |
| CHECK | `work_context_context_version_check` | `CHECK ((context_version > 0))` |
| CHECK | `work_context_grounding_status_check` | `CHECK ((grounding_status = ANY (ARRAY['COORDINATES_ONLY'::text, 'VERIFIED'::text])))` |
| CHECK | `work_context_previous_context_digest_check` | `CHECK (((previous_context_digest IS NULL) OR (previous_context_digest ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| FK | `work_context_previous_context_uid_fkey` | `FOREIGN KEY (previous_context_uid) REFERENCES audit_execution.work_context(context_uid) ON DELETE RESTRICT` |
| FK | `work_context_work_item_uid_fkey` | `FOREIGN KEY (work_item_uid) REFERENCES audit_execution.work_item(work_item_uid) ON DELETE RESTRICT` |
| PK | `work_context_pkey` | `PRIMARY KEY (context_uid)` |
| UNIQUE | `work_context_context_package_digest_key` | `UNIQUE (context_package_digest)` |
| UNIQUE | `work_context_work_item_uid_context_version_key` | `UNIQUE (work_item_uid, context_version)` |

Triggers:

- `work_context_no_delete`: `work_context_no_delete BEFORE DELETE ON audit_execution.work_context FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `work_context_no_update`: `work_context_no_update BEFORE UPDATE ON audit_execution.work_context FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.work_item`

Columns: 10 | **NOT NULL:** `work_item_uid`, `request_uid`, `request_digest`, `request_envelope_digest`, `subject_uid`, `package_snapshot_digest`, `closure_root`, `request_payload_json`, `request_envelope_json`, `created_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `work_item_closure_root_check` | `CHECK ((closure_root ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `work_item_package_snapshot_digest_check` | `CHECK ((package_snapshot_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `work_item_request_digest_check` | `CHECK ((request_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `work_item_request_envelope_digest_check` | `CHECK ((request_envelope_digest ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `work_item_request_envelope_json_check` | `CHECK ((jsonb_typeof((request_envelope_json)::jsonb) = 'object'::text))` |
| CHECK | `work_item_request_payload_json_check` | `CHECK ((jsonb_typeof((request_payload_json)::jsonb) = 'object'::text))` |
| PK | `work_item_pkey` | `PRIMARY KEY (work_item_uid)` |
| UNIQUE | `work_item_request_envelope_digest_key` | `UNIQUE (request_envelope_digest)` |
| UNIQUE | `work_item_request_uid_key` | `UNIQUE (request_uid)` |

Triggers:

- `work_item_no_delete`: `work_item_no_delete BEFORE DELETE ON audit_execution.work_item FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `work_item_no_update`: `work_item_no_update BEFORE UPDATE ON audit_execution.work_item FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

### `audit_execution.work_item_event`

Columns: 11 | **NOT NULL:** `event_uid`, `work_item_uid`, `event_sequence`, `event_kind`, `details_json`, `event_hash`, `recorded_at`

| Kind | Name | Definition |
|---|---|---|
| CHECK | `work_item_event_claim_token_hash_check` | `CHECK (((claim_token_hash IS NULL) OR (claim_token_hash ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| CHECK | `work_item_event_details_json_check` | `CHECK ((jsonb_typeof((details_json)::jsonb) = 'object'::text))` |
| CHECK | `work_item_event_event_hash_check` | `CHECK ((event_hash ~ '^sha256:[0-9a-f]{64}$'::text))` |
| CHECK | `work_item_event_event_kind_check` | `CHECK ((event_kind = ANY (ARRAY['DISCOVERED'::text, 'CLAIMED'::text, 'HEARTBEAT'::text, 'RELEASED'::text, 'SUBMITTED'::text])))` |
| CHECK | `work_item_event_event_sequence_check` | `CHECK ((event_sequence > 0))` |
| CHECK | `work_item_event_prior_event_hash_check` | `CHECK (((prior_event_hash IS NULL) OR (prior_event_hash ~ '^sha256:[0-9a-f]{64}$'::text)))` |
| FK | `work_item_event_work_item_uid_fkey` | `FOREIGN KEY (work_item_uid) REFERENCES audit_execution.work_item(work_item_uid) ON DELETE RESTRICT` |
| PK | `work_item_event_pkey` | `PRIMARY KEY (event_uid)` |
| UNIQUE | `work_item_event_event_hash_key` | `UNIQUE (event_hash)` |
| UNIQUE | `work_item_event_work_item_uid_event_sequence_key` | `UNIQUE (work_item_uid, event_sequence)` |

Triggers:

- `work_item_event_no_delete`: `work_item_event_no_delete BEFORE DELETE ON audit_execution.work_item_event FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`
- `work_item_event_no_update`: `work_item_event_no_update BEFORE UPDATE ON audit_execution.work_item_event FOR EACH ROW EXECUTE FUNCTION audit_system.reject_mutation()`

## 8. Wire validators (`bc-core src/registry/metric-audit/wire/wire-validate.ts`)

Rule codes with their emitting lines (extracted; the file is the authority):

| Line | Rule text |
|---|---|
| 590 | `if (isDirectory && !nonNull) out.push(`V-R8: projection_inputs.${key} must be non-null for DIRECTORY_ORIGINATED`);` |
| 591 | `if (!isDirectory && nonNull) out.push(`V-R8: projection_inputs.${key} must be null unless DIRECTORY_ORIGINATED`);` |
| 594 | `if (isOffPool && !offPoolNonNull) out.push('V-R8: projection_inputs.off_pool_exception must be non-null for OFF_POOL/LEGACY');` |
| 595 | `if (!isOffPool && offPoolNonNull) out.push('V-R8: projection_inputs.off_pool_exception must be null unless OFF_POOL/LEGACY');` |
| 623 | `if (cause === null) out.push(`V-R4: trigger.cause_ref must not be null for trigger_kind ${kind}`);` |
| 625 | `out.push(`V-R4: trigger_kind ${kind} requires from_state ${rule.from.join('\|')}, got ${fromState}`);` |
| 628 | `out.push(`V-R4: trigger_kind ${kind} requires cause_kind ${rule.causes.join('\|')}, got ${causeKind}`);` |
| 666 | `out.push(`V-R3: evidence_coordinates has duplicate evidence_kind "${kind}"`);` |
| 671 | `if (pkgEntries.length !== 1) out.push('V-R3: evidence_coordinates must contain exactly one package_snapshot entry');` |
| 672 | `if (closureEntries.length !== 1) out.push('V-R3: evidence_coordinates must contain exactly one closure_manifest entry');` |
| 676 | `out.push('V-R3: package_snapshot evidence content_digest must equal package.package_snapshot_digest');` |
| 680 | `out.push('V-R3: closure_manifest evidence content_digest must equal closure_root');` |
| 685 | `if (!byKind.has(kind)) out.push(`V-R3: DIRECTORY_ORIGINATED requires an evidence coordinate of kind "${kind}"`);` |
| 689 | `out.push('V-R3: OFF_POOL/LEGACY requires an evidence coordinate of kind "off_pool_exception"');` |
| 716 | `out.push('V-R6: trigger.occurred_at must be <= created_at');` |
| 719 | `out.push('V-R1: request_digest does not equal the canonical self-digest of the payload without request_digest');` |
| 774 | `checkContextualMath({ min: 'V-D4', table: 'V-D4' }, scores, overall, decision, label, out);` |
| 798 | `out.push('V-D9: exactness_basis REPRODUCIBLE cannot carry exactness_result EXACT — a reproducible basis never asserts exactness');` |
| 800 | `out.push('V-D9: exactness_result REPRODUCIBLE requires exactness_basis REPRODUCIBLE — the basis label is mandatory, never inferred');` |
| 803 | `out.push('V-D9: exactness_result REPRODUCIBLE requires exactness_basis REPRODUCIBLE — the basis label is mandatory, never inferred');` |
| 846 | `out.push('V-D8: authority.source_authority_revision/source_authority_policy_digest do not equal the revision '` |
| 853 | `if (!isRecord(payload.revocation)) out.push('V-D7: decision_code REVOKE requires a non-null revocation object');` |
| 854 | `if (payload.verdict_summary !== null) out.push('V-D7: decision_code REVOKE requires verdict_summary null');` |
| 855 | `if (payload.report_ref !== null) out.push('V-D7: decision_code REVOKE requires report_ref null');` |
| 859 | `out.push(`V-D7: decision_code REVOKE requires ${key} to be empty`);` |
| 865 | `out.push('V-D7: REVOKE requires supersedes_decision_uid equal to revocation.revoked_decision_uid '` |
| 869 | `out.push('V-D7: REVOKE must not revoke itself (revocation.revoked_decision_uid equals decision_uid)');` |
| 894 | `out.push('V-D7: revocation.reason_statement must be at least 40 characters');` |
| 906 | `out.push('V-D3: decision_code PASS requires unresolved_blocking_ncs to be empty');` |
| 910 | `if (summary.structural_verdict !== 'PASS') out.push('V-D3: PASS requires verdict_summary.structural_verdict PASS');` |
| 911 | `if (summary.foundation_verdict !== 'PASS') out.push('V-D3: PASS requires verdict_summary.foundation_verdict PASS');` |
| 913 | `out.push('V-D3: PASS requires semantic_conformance_verdict PASS or NOT_APPLICABLE');` |
| 919 | `out.push('V-D3: PASS requires exactness_result EXACT or (labelled) REPRODUCIBLE');` |
| 926 | `out.push(`V-D3: PASS requires contextual.${axis}.score >= 4`);` |
| 931 | `out.push('V-D3: PASS requires contextual.decision VERIFIED or HIGH_CONFIDENCE');` |
| 956 | `if (view.maxScore !== undefined) checkGradeFloor('V-D8', view.maxScore, citations, 'decision citations vs max axis', out);` |
| 965 | `out.push('V-D1: decision_digest does not equal the canonical self-digest of the payload without decision_digest');` |
| 1000 | `if (value === payload.decision_uid) out.push('V-D6: supersedes_decision_uid must not equal decision_uid');` |
| 1129 | `out.push(`CF-R11: ${entryLabel}.evidence_digest does not reference a citation of this axis`);` |
| 1186 | `out.push(`CF-R4: ${label}.citations must contain at least one closure-bound citation`);` |
| 1210 | `checkContextualMath({ min: 'CF-R1', table: 'CF-R2' }, scores, overall, decision, 'contextual', out);` |
| 1227 | `out.push('CF-R8: semantic_conformance.applicable === false must pair exactly with verdict NOT_APPLICABLE');` |
| 1287 | `if (new Set(raisedUids).size !== raisedUids.length) out.push('CF-R6: ncs_raised contains duplicates');` |
| 1294 | `if (!raisedSet.has(uid)) out.push(`CF-R6: finding nc_uid ${uid} is missing from ncs_raised`);` |
| 1297 | `if (!carriedSet.has(uid)) out.push(`CF-R6: ncs_raised ${uid} has no CRITICAL/MAJOR/MINOR finding carrying it`);` |
| 1360 | `out.push('CF-R9: ncs_raised is non-empty so re_audit.required must be true');` |
| 1363 | `out.push('CF-R9: re_audit.required false requires trigger_kind "none"');` |
| 1366 | `out.push('CF-R9: re_audit.required true requires a non-"none" trigger_kind');` |
| 1391 | `out.push(`CF-R4: contextual.${axis} score ${axisView.score} exceeds the source-authority policy cap ${cap} `` |
| 1449 | `out.push(`CF-R3: overall_assessment must recompute to ${expected} (structural, foundation, contextual, `` |
| 1471 | `out.push(`V-R8: source_authority_revision "${payload.source_authority_revision}" does not equal the policy `` |
| 1798 | `out.push('V-D2: decision.request_ref.request_uid does not equal request.request_uid');` |
| 1801 | `out.push('V-D2: decision.request_ref.request_digest does not equal request.request_digest');` |
| 1806 | `out.push(`V-D2: decision.subject.${key} does not equal request.subject.${key}`);` |
| 1810 | `out.push('V-D2: decision.package.package_snapshot_digest does not equal the request package snapshot digest');` |
| 1813 | `out.push('V-D2: decision.closure_root does not equal request.closure_root');` |
| 1822 | `out.push('CF-R10: envelope.subject.subject_uid does not equal report.subject.metric_contract_version_uid');` |
| 1825 | `out.push('CF-R10: envelope.subject.package_signature_hash does not equal report.subject.package_snapshot_digest');` |
| 1828 | `out.push('CF-R10: envelope.subject.closure_root does not equal report.subject.closure_root');` |
| 1831 | `out.push('CF-R10: envelope.payload_digest does not equal the canonical digest of the report payload');` |
| 1990 | `return ['V-D7: revokeDecisionIdentity requires a REVOKE decision with a revocation object'];` |
| 1993 | `out.push('V-D7: revocation.revoked_decision_uid does not equal the prior decision_uid');` |
| 1996 | `out.push('V-D7: revocation.revoked_decision_digest does not equal the exact prior decision_digest');` |
| 1999 | `out.push('V-D7: REVOKE subject does not equal the revoked decision subject');` |

## 9. Checker rule catalogue (CRV) — `references/contextual-reference-rule-catalog-v1.json`

Status: `PROPOSED_NOT_ACCEPTED_RELEASE` | Governing framework: `[object Object]` | Rules: 22

| Code | Requirement |
|---|---|
| CRV-001 | Basis schema and self-digest are valid. |
| CRV-002 | Request UID and digest match the retained run and published request. |
| CRV-003 | MCV, package digest, hash algorithm, and closure root match. |
| CRV-004 | Full authority coordinates match the run-bound accepted release. |
| CRV-005 | Grain and counted or measured unit are explicit and consistent. |
| CRV-006 | Temporal and aggregation semantics are explicit and consistent. |
| CRV-007 | Declared filters and population boundary are complete enough for the claim. |
| CRV-008 | Formula AST and explanation are bound, or the governed temporary issue path is used. |
| CRV-009 | AST leaf operands resolve through the canonical CF or BCF allowlist. |
| CRV-010 | Source or vendor literals do not leak into source-neutral intrinsic authority. |
| CRV-011 | Reference sufficiency meets the maximum lattice rank from claim type, every burden, and every current upstream dependency. |
| CRV-012 | COMMON_DOMAIN use has a retained rationale digest and permitted scope. |
| CRV-013 | Amount, unit, currency, and sign convention are emitted or produce the catalog-prescribed cap or refusal. |
| CRV-014 | Exactness is treated as runtime evidence, not business-meaning authority. |
| CRV-015 | Source-realization evidence is scoped and cannot universalize the metric. |
| CRV-016 | Regulatory or filing readiness is explicitly excluded. |
| CRV-017 | Database assurance is separate and never averaged into contextual scoring. |
| CRV-018 | Prior audit evidence is current and not the sole current basis. |
| CRV-019 | Upstream dependencies and chain state are current. |
| CRV-020 | Accepted release manifest and every component digest match. |
| CRV-021 | Every material edge behavior has a supported, capped, refused, or justified-not-applicable disposition. |
| CRV-022 | Directory member and version, taxonomy, family, grain, MCF version and inputs, and BCF concepts align semantically with the claim. |

## 10. Canonical population queries (COUNT FROM THE GATE, NOT FROM A TABLE)

The ONLY sanctioned way to claim eligibility counts. These mirror the c9 arms verbatim:

```sql
-- c9 eligibility partition over active current MCVs (arms are mutually exclusive by evidence shape)
WITH act AS (
  SELECT v.metric_contract_version_uid AS mcv, s.exactness_result AS snap_exact,
         s.binary64_activation_eligible AS b64, s.package_signature_hash AS pkg, s.disposition_code AS disp
  FROM mcf.metric_contract_version v
  LEFT JOIN mcf.mcv_package_snapshot s USING (metric_contract_version_uid)
  WHERE v.is_current AND v.governance_state_code='active')
SELECT count(*) AS active_current,
  count(*) FILTER (WHERE snap_exact='EXACT' AND b64 IS TRUE) AS arm_exact_snapshot,
  count(*) FILTER (WHERE EXISTS (SELECT 1 FROM mcf.exactness_reproof_evidence e WHERE e.metric_contract_version_uid=act.mcv
    AND e.prover_algorithm_version='mcf-exactness-v2' AND e.verdict_code='EXACT' AND e.package_signature_hash=act.pkg)) AS arm_exact_reproof,
  count(*) FILTER (WHERE EXISTS (SELECT 1 FROM mcf.exactness_reproof_evidence e WHERE e.metric_contract_version_uid=act.mcv
    AND e.prover_algorithm_version='mcf-reproducibility-v1' AND e.verdict_code='REPRODUCIBLE' AND e.package_signature_hash=act.pkg)) AS arm_reproducible,
  count(*) FILTER (WHERE disp IS DISTINCT FROM 'computed') AS no_computed_snapshot
FROM act;
```

Live at generation time: active=340, arm_exact_snapshot=56, arm_exact_reproof=38, arm_reproducible=70, no_computed_snapshot=167

