-- 0032 clone proof (ADR DEC-b1e9eb, DBCP vectors 1-13). THROWAWAY CLONE ONLY (container m0032-proof).
-- Each vector either succeeds or must be refused; any deviation raises VECTOR FAILED and stops the run.
\set ON_ERROR_STOP 1
SET client_min_messages = notice;
CREATE SCHEMA proof;

-- expect_refusal(sql, pattern): the statement must raise an error whose message matches pattern.
CREATE FUNCTION proof.expect_refusal(v text, stmt text, pat text) RETURNS void LANGUAGE plpgsql AS $f$
BEGIN
  BEGIN
    SET CONSTRAINTS ALL IMMEDIATE;
    EXECUTE stmt;
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM ~* pat THEN RAISE NOTICE 'PASS % refused: %', v, SQLERRM; RETURN; END IF;
    RAISE EXCEPTION 'VECTOR FAILED % — refused for the wrong reason: %', v, SQLERRM;
  END;
  RAISE EXCEPTION 'VECTOR FAILED % — statement was NOT refused: %', v, stmt;
END
$f$;

CREATE FUNCTION proof.expect_ok(v text, stmt text) RETURNS void LANGUAGE plpgsql AS $f$
BEGIN
  SET CONSTRAINTS ALL IMMEDIATE;
  EXECUTE stmt;
  RAISE NOTICE 'PASS % accepted', v;
END
$f$;

-- A post-cutover member version: a copy of a pre-cutover draft (new uid, test version code, not current).
CREATE FUNCTION proof.new_member(tag text, acc text) RETURNS uuid LANGUAGE plpgsql AS $f$
DECLARE t mcf.metric_contract_version; u uuid := gen_random_uuid();
BEGIN
  SELECT * INTO t FROM mcf.metric_contract_version WHERE governance_state_code = 'draft' ORDER BY metric_contract_version_uid LIMIT 1;
  t.metric_contract_version_uid := u; t.version_code := 'm0032-' || tag; t.is_current := false;
  t.governance_state_code := 'draft'; t.aggregation_currency_code := acc; t.created_at := now(); t.supersedes_version_uid := NULL;
  INSERT INTO mcf.metric_contract_version SELECT t.*;
  RETURN u;
END
$f$;

CREATE TABLE proof.ids (tag text PRIMARY KEY, uid uuid);
INSERT INTO proof.ids VALUES
  ('A', proof.new_member('A', 'not_applicable')),
  ('B', proof.new_member('B', 'local_currency')),
  ('C', proof.new_member('C', 'not_applicable')),
  ('D', proof.new_member('D', 'not_applicable'));
-- two pre-cutover drafts (no membership), different from the template
INSERT INTO proof.ids SELECT 'P1', metric_contract_version_uid FROM mcf.metric_contract_version
  WHERE governance_state_code = 'draft' AND version_code NOT LIKE 'm0032-%' ORDER BY metric_contract_version_uid OFFSET 1 LIMIT 1;
INSERT INTO proof.ids SELECT 'P2', metric_contract_version_uid FROM mcf.metric_contract_version
  WHERE governance_state_code = 'review' AND version_code NOT LIKE 'm0032-%' ORDER BY metric_contract_version_uid LIMIT 1;

DO $$ BEGIN
  IF (SELECT count(*) FROM mcf.metric_output_declaration_required) <> 4 THEN RAISE EXCEPTION 'VECTOR FAILED setup — expected 4 membership rows (one per new version)'; END IF;
  IF EXISTS (SELECT 1 FROM mcf.metric_output_declaration_required r JOIN proof.ids i ON i.uid = r.metric_contract_version_uid WHERE i.tag LIKE 'P%') THEN
    RAISE EXCEPTION 'VECTOR FAILED setup — a pre-cutover version became a member'; END IF;
  RAISE NOTICE 'PASS setup: 4 new versions -> 4 membership rows written by trg_mod_mcv_membership; pre-cutover versions have none';
END $$;

CREATE FUNCTION proof.u(tag text) RETURNS text LANGUAGE sql AS $f$ SELECT quote_literal(uid) FROM proof.ids WHERE ids.tag = $1 $f$;
CREATE FUNCTION proof.decl(tag text, unit text, places text, mode text) RETURNS text LANGUAGE sql AS $f$
  SELECT format('INSERT INTO mcf.metric_output_declaration (metric_contract_version_uid, unit_type_code, decimal_places_count, rounding_mode_code, declared_by_name) VALUES (%s::uuid, %L, %s, %L, %L)',
                proof.u($1), $2, $3, $4, 'm0032-clone-proof') $f$;

-- V1 the DSO-shaped declaration on a post-cutover draft with not_applicable
SELECT proof.expect_ok('V1 days/2/half_up on member A', proof.decl('A', 'days', '2', 'half_up'));
-- V2 money places are derived: currency with places is refused; and an incoherent unit/currency pair is refused
SELECT proof.expect_refusal('V2 currency with places 2', proof.decl('B', 'currency', '2', 'half_up'), 'chk_metric_output_declaration_places_by_unit');
SELECT proof.expect_refusal('V2b days on a local_currency version', proof.decl('B', 'days', '2', 'half_up'), 'incoherent with aggregation_currency_code');
-- V3 a non-money unit without places
SELECT proof.expect_refusal('V3 days with NULL places', proof.decl('C', 'days', 'NULL', 'half_up'), 'chk_metric_output_declaration_places_by_unit');
-- V4 a pre-cutover version can never gain a declaration
SELECT proof.expect_refusal('V4 declaration on pre-cutover P1', proof.decl('P1', 'days', '2', 'half_up'), 'predates the DEC-b1e9eb cutover');

-- V5 frozen member: approve A (which has its declaration) in isolation, then a declaration insert is refused as frozen
ALTER TABLE mcf.metric_contract_version DISABLE TRIGGER trg_mcf_mcv_state_transition;
SELECT proof.expect_ok('V5 setup: A (declared) enters approved — the new gate lets a declared member through',
  format('UPDATE mcf.metric_contract_version SET governance_state_code = %L WHERE metric_contract_version_uid = %s::uuid', 'approved', proof.u('A')));
SELECT proof.expect_refusal('V5 declaration on frozen member A', proof.decl('A', 'ratio', '4', 'half_even'), 'is frozen');
-- V6 a member without a declaration cannot enter a frozen state (isolated: platform state rules disabled on the clone)
SELECT proof.expect_refusal('V6 member C -> approved without declaration',
  format('UPDATE mcf.metric_contract_version SET governance_state_code = %L WHERE metric_contract_version_uid = %s::uuid', 'approved', proof.u('C')), 'without its output declaration');
-- V10 a pre-cutover version is unaffected by the new gate (P2 review -> approved passes the new gate;
--     the unrelated grain-pin rule is also disabled for this isolated step, since no pre-cutover review version has a pin)
ALTER TABLE mcf.metric_contract_version DISABLE TRIGGER trg_mcv_grain_entity_version_guard;
SELECT proof.expect_ok('V10 pre-cutover P2 review -> approved (new gate does not apply)',
  format('UPDATE mcf.metric_contract_version SET governance_state_code = %L WHERE metric_contract_version_uid = %s::uuid', 'approved', proof.u('P2')));
ALTER TABLE mcf.metric_contract_version ENABLE TRIGGER trg_mcv_grain_entity_version_guard;
ALTER TABLE mcf.metric_contract_version ENABLE TRIGGER trg_mcf_mcv_state_transition;
-- V6 realistic: with the platform rules enabled, the same transition is refused too
SELECT proof.expect_refusal('V6r member C draft -> approved (platform rules on)',
  format('UPDATE mcf.metric_contract_version SET governance_state_code = %L WHERE metric_contract_version_uid = %s::uuid', 'approved', proof.u('C')), 'invalid mcf state transition|without its output declaration');

-- V7 package snapshot for a member without a declaration (isolated: the existing snapshot guard disabled)
ALTER TABLE mcf.mcv_package_snapshot DISABLE TRIGGER trg_mcv_package_snapshot_guard;
CREATE TEMP TABLE snap_tpl AS SELECT * FROM mcf.mcv_package_snapshot LIMIT 1;
UPDATE snap_tpl SET mcv_package_snapshot_uid = gen_random_uuid(), metric_contract_version_uid = (SELECT uid FROM proof.ids WHERE tag = 'C');
SELECT proof.expect_refusal('V7 snapshot for undeclared member C', 'INSERT INTO mcf.mcv_package_snapshot SELECT * FROM snap_tpl', 'no output declaration');

-- V8 the parent currency is frozen once declared (D is a declared draft)
SELECT proof.expect_ok('V8 setup: declare D days/0/half_up', proof.decl('D', 'days', '0', 'half_up'));
SELECT proof.expect_refusal('V8 change aggregation_currency_code on declared draft D',
  format('UPDATE mcf.metric_contract_version SET aggregation_currency_code = %L WHERE metric_contract_version_uid = %s::uuid', 'local_currency', proof.u('D')), 'frozen by its output declaration');

-- V9 immutability of declarations and of the policy row
SELECT proof.expect_refusal('V9 UPDATE a declaration', format('UPDATE mcf.metric_output_declaration SET decimal_places_count = 3 WHERE metric_contract_version_uid = %s::uuid', proof.u('D')), 'is immutable');
SELECT proof.expect_refusal('V9 DELETE a declaration', format('DELETE FROM mcf.metric_output_declaration WHERE metric_contract_version_uid = %s::uuid', proof.u('D')), 'is immutable');
SELECT proof.expect_refusal('V9 UPDATE the policy row', 'UPDATE mcf.metric_output_declaration_policy SET recorded_by_name = ''x''', 'is immutable');
SELECT proof.expect_refusal('V9 DELETE the policy row', 'DELETE FROM mcf.metric_output_declaration_policy', 'is immutable');

-- V11 backdating a member's created_at changes nothing: still refused at freeze and at snapshot
UPDATE mcf.metric_contract_version SET created_at = timestamptz '2020-01-01' WHERE metric_contract_version_uid = (SELECT uid FROM proof.ids WHERE tag = 'C');
DO $$ BEGIN IF (SELECT created_at FROM mcf.metric_contract_version WHERE metric_contract_version_uid = (SELECT uid FROM proof.ids WHERE tag = 'C')) <> timestamptz '2020-01-01'
  THEN RAISE EXCEPTION 'VECTOR FAILED V11 setup — backdate did not apply'; END IF; RAISE NOTICE 'PASS V11 setup: member C created_at backdated to 2020-01-01'; END $$;
ALTER TABLE mcf.metric_contract_version DISABLE TRIGGER trg_mcf_mcv_state_transition;
SELECT proof.expect_refusal('V11 backdated member C -> approved without declaration',
  format('UPDATE mcf.metric_contract_version SET governance_state_code = %L WHERE metric_contract_version_uid = %s::uuid', 'approved', proof.u('C')), 'without its output declaration');
ALTER TABLE mcf.metric_contract_version ENABLE TRIGGER trg_mcf_mcv_state_transition;
SELECT proof.expect_refusal('V11 snapshot for backdated member C', 'INSERT INTO mcf.mcv_package_snapshot SELECT * FROM snap_tpl', 'no output declaration');
ALTER TABLE mcf.mcv_package_snapshot ENABLE TRIGGER trg_mcv_package_snapshot_guard;

-- V12 membership is immutable and cannot be written directly
SELECT proof.expect_refusal('V12 UPDATE a membership row', format('UPDATE mcf.metric_output_declaration_required SET recorded_at = now() WHERE metric_contract_version_uid = %s::uuid', proof.u('C')), 'is immutable');
SELECT proof.expect_refusal('V12 DELETE a membership row', format('DELETE FROM mcf.metric_output_declaration_required WHERE metric_contract_version_uid = %s::uuid', proof.u('C')), 'is immutable');
SELECT proof.expect_refusal('V12 direct INSERT of membership for pre-cutover P1', format('INSERT INTO mcf.metric_output_declaration_required (metric_contract_version_uid) VALUES (%s::uuid)', proof.u('P1')), 'direct insert');

-- V13 moving a pre-cutover version's created_at forward does not make it a member
UPDATE mcf.metric_contract_version SET created_at = now() + interval '1 day' WHERE metric_contract_version_uid = (SELECT uid FROM proof.ids WHERE tag = 'P1');
SELECT proof.expect_refusal('V13 declaration on forward-dated pre-cutover P1', proof.decl('P1', 'days', '2', 'half_up'), 'predates the DEC-b1e9eb cutover');

-- L: the served login (bc_platform_runtime) under its real grants: the governed writer path works; the guards bind it
GRANT USAGE ON SCHEMA proof TO bc_platform_runtime;
GRANT SELECT, INSERT ON proof.ids TO bc_platform_runtime;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA proof TO bc_platform_runtime;
SET ROLE bc_platform_runtime;
INSERT INTO proof.ids VALUES ('E', proof.new_member('E', 'not_applicable'));
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM mcf.metric_output_declaration_required r JOIN proof.ids i ON i.uid = r.metric_contract_version_uid WHERE i.tag = 'E') THEN
    RAISE EXCEPTION 'VECTOR FAILED L1 — the served login created version E but no membership row was written'; END IF;
  RAISE NOTICE 'PASS L1 served login creates a version; the SECURITY DEFINER trigger writes its membership';
END $$;
SELECT proof.expect_ok('L2 served login declares E days/2/half_up', proof.decl('E', 'days', '2', 'half_up'));
SELECT proof.expect_refusal('L3 served login UPDATE of a declaration', format('UPDATE mcf.metric_output_declaration SET decimal_places_count = 3 WHERE metric_contract_version_uid = %s::uuid', proof.u('E')), 'permission denied|is immutable');
SELECT proof.expect_refusal('L4 served login direct INSERT of membership', format('INSERT INTO mcf.metric_output_declaration_required (metric_contract_version_uid) VALUES (%s::uuid)', proof.u('P1')), 'permission denied|direct insert');
SELECT proof.expect_refusal('L5 served login declares a pre-cutover version', proof.decl('P1', 'days', '2', 'half_up'), 'predates the DEC-b1e9eb cutover');
SELECT proof.expect_refusal('L6 served login changes the currency of declared E', format('UPDATE mcf.metric_contract_version SET aggregation_currency_code = %L WHERE metric_contract_version_uid = %s::uuid', 'local_currency', proof.u('E')), 'frozen by its output declaration');
SELECT proof.expect_refusal('L7 served login currency declaration with places', proof.decl('B', 'currency', '2', 'half_up'), 'chk_metric_output_declaration_places_by_unit');
RESET ROLE;
DO $$ BEGIN RAISE NOTICE 'ALL VECTORS PASSED: % declarations, % members', (SELECT count(*) FROM mcf.metric_output_declaration), (SELECT count(*) FROM mcf.metric_output_declaration_required); END $$;
