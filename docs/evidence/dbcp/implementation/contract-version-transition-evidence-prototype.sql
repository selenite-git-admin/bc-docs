-- DEC-fbc085 / TSK-56c689 — PROTOTYPE of the proposed emitter (successor 2, gen-1afb60 F1/F2/F4/F5).
-- NOT A MIGRATION. Runs ONLY in a throwaway postgres:17.11-alpine container (no published port),
-- never against bc-postgres. Part 1 = the mechanism (the shape the real DDL will take for the
-- canonical + observation families); Part 2 = scaffolding standing in for live objects;
-- Part 3 = the negative/positive corpus. Every expectation is asserted; any failure aborts (ON_ERROR_STOP).
\set ON_ERROR_STOP 1

-- ── Part 2 (scaffolding standing in for live objects) ───────────────────────
CREATE SCHEMA contract;
CREATE SCHEMA infrastructure;
CREATE ROLE bc_schema_owner NOLOGIN;                   -- exists live
CREATE ROLE chain_auditor_readonly NOLOGIN;            -- exists live
CREATE ROLE served_app LOGIN;                          -- stands in for a NON-superuser served login (D575 W6-P)
CREATE FUNCTION infrastructure.fn_reject_mutation() RETURNS trigger LANGUAGE plpgsql
  SECURITY DEFINER SET search_path TO 'pg_catalog' AS $$
BEGIN RAISE EXCEPTION 'governed table %.% is append-only (Invariant III): % rejected', TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP; END $$;
CREATE TABLE contract.canonical_contract_version (
  canonical_contract_id uuid NOT NULL, version_code text NOT NULL, contract_json jsonb NOT NULL,
  governance_state_code text NOT NULL DEFAULT 'draft', PRIMARY KEY (canonical_contract_id, version_code));
CREATE TABLE contract.observation_contract_version (
  observation_contract_id uuid NOT NULL, version_code text NOT NULL, contract_json jsonb NOT NULL,
  governance_state_code text NOT NULL DEFAULT 'draft', PRIMARY KEY (observation_contract_id, version_code));
GRANT USAGE ON SCHEMA contract TO served_app, chain_auditor_readonly, bc_schema_owner;
GRANT SELECT, INSERT, UPDATE ON contract.canonical_contract_version, contract.observation_contract_version TO served_app;
-- pre-state rows (seeded BEFORE the mechanism exists, as live rows pre-date it)
INSERT INTO contract.canonical_contract_version VALUES
  ('00000000-0000-0000-0000-00000000c150','1.5.0','{"b":1}','active'),
  ('00000000-0000-0000-0000-00000000c150','1.6.0','{"b":2}','approved'),
  ('00000000-0000-0000-0000-00000000c150','9.0.0','{"b":9}','draft');
INSERT INTO contract.observation_contract_version VALUES ('00000000-0000-0000-0000-00000000a120','1.2.0','{"o":1}','active'),
  ('00000000-0000-0000-0000-0000000a0001','1.0.0','{}','draft'),('00000000-0000-0000-0000-0000000a0002','1.0.0','{}','draft');
INSERT INTO contract.canonical_contract_version VALUES
  ('00000000-0000-0000-0000-0000000b0001','1.0.0','{}','draft'),('00000000-0000-0000-0000-0000000b0002','1.0.0','{}','draft'),
  ('00000000-0000-0000-0000-0000000b0003','1.0.0','{}','draft'),('00000000-0000-0000-0000-0000000b0004','1.0.0','{}','draft');
-- target W6-P posture: the version tables are owned by the NOLOGIN schema owner, NOT by the served login
-- (a table owner can DISABLE TRIGGER; live they are owned by the superuser login barecount today).
ALTER TABLE contract.canonical_contract_version OWNER TO bc_schema_owner;
ALTER TABLE contract.observation_contract_version OWNER TO bc_schema_owner;

-- ── Part 1 (the mechanism) ──────────────────────────────────────────────────
CREATE ROLE bc_contract_evidence_emitter NOLOGIN;      -- NEW role (DBCP D6): owns the emitter, sole INSERT holder
GRANT USAGE ON SCHEMA contract TO bc_contract_evidence_emitter;
GRANT SELECT ON contract.canonical_contract_version, contract.observation_contract_version TO bc_contract_evidence_emitter; -- the guard's state cross-check

-- One table per family (real composite FK). 15 columns.
CREATE TABLE contract.canonical_contract_version_transition (
  canonical_contract_version_transition_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  transition_seq          bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
  canonical_contract_id   uuid NOT NULL,
  version_code            text NOT NULL,
  from_state_code         text NULL,
  to_state_code           text NOT NULL,
  transition_cause_code   text NOT NULL CHECK (transition_cause_code IN
                            ('governed_request','provisioning_readiness','authoring_chain','bulk_transition','operator_sql')),
  actor_kind_code         text NOT NULL CHECK (actor_kind_code IN ('authenticated_http','service_system','operator_sql')),
  actor_subject           text NOT NULL,
  request_correlation_id  text NULL,
  rationale_text          text NULL,
  contract_json_sha256    text NOT NULL CHECK (contract_json_sha256 ~ '^[0-9a-f]{64}$'),
  db_principal_name       text NOT NULL,
  transaction_id          xid8 NOT NULL,
  recorded_at             timestamptz NOT NULL,
  CONSTRAINT fk_canonical_contract_version_transition_version FOREIGN KEY (canonical_contract_id, version_code)
    REFERENCES contract.canonical_contract_version (canonical_contract_id, version_code) ON DELETE RESTRICT,
  CONSTRAINT canonical_contract_version_transition_actor_check CHECK (
       (actor_kind_code = 'authenticated_http' AND transition_cause_code IN ('governed_request','bulk_transition') AND request_correlation_id IS NOT NULL)
    OR (actor_kind_code = 'service_system'     AND transition_cause_code IN ('provisioning_readiness','authoring_chain'))
    OR (actor_kind_code = 'operator_sql'       AND transition_cause_code = 'operator_sql' AND length(coalesce(rationale_text,'')) >= 40))
);
CREATE TABLE contract.observation_contract_version_transition (LIKE contract.canonical_contract_version_transition INCLUDING DEFAULTS INCLUDING CONSTRAINTS INCLUDING IDENTITY);
ALTER TABLE contract.observation_contract_version_transition RENAME COLUMN canonical_contract_version_transition_id TO observation_contract_version_transition_id;
ALTER TABLE contract.observation_contract_version_transition RENAME COLUMN canonical_contract_id TO observation_contract_id;
ALTER TABLE contract.observation_contract_version_transition ADD PRIMARY KEY (observation_contract_version_transition_id),
  ADD UNIQUE (transition_seq),
  ADD CONSTRAINT fk_observation_contract_version_transition_version FOREIGN KEY (observation_contract_id, version_code)
    REFERENCES contract.observation_contract_version (observation_contract_id, version_code) ON DELETE RESTRICT;
CREATE INDEX idx_canonical_contract_version_transition_version ON contract.canonical_contract_version_transition (canonical_contract_id, version_code, transition_seq);
CREATE INDEX idx_observation_contract_version_transition_version ON contract.observation_contract_version_transition (observation_contract_id, version_code, transition_seq);
ALTER TABLE contract.canonical_contract_version_transition OWNER TO bc_schema_owner;
ALTER TABLE contract.observation_contract_version_transition OWNER TO bc_schema_owner;
REVOKE ALL ON contract.canonical_contract_version_transition, contract.observation_contract_version_transition FROM PUBLIC;
GRANT INSERT ON contract.canonical_contract_version_transition, contract.observation_contract_version_transition TO bc_contract_evidence_emitter;
GRANT SELECT ON contract.canonical_contract_version_transition, contract.observation_contract_version_transition TO served_app, chain_auditor_readonly;


-- (a) The DECLARATION. Called INSIDE the writing statement (an uncorrelated sub-select = one init-plan).
--     It names each EXACT target transition it covers: family + contract id + version + to-state.
--     Every key is ONE-SHOT and carries its own immutable context; a second declaration for the same
--     key in the same statement is refused. The whole map is bound to (statement_timestamp, xid);
--     a map from any other top-level statement is treated as absent. Invoker rights; it grants
--     nothing — it is a writer assertion.
CREATE FUNCTION contract.fn_declare_transition_context(
  p_family text, p_targets jsonb, p_cause text, p_actor_kind text, p_subject text, p_correlation text, p_rationale text)
RETURNS boolean LANGUAGE plpgsql VOLATILE SET search_path = pg_catalog AS $$
DECLARE
  b   text  := statement_timestamp()::text || '|' || pg_current_xact_id()::text;
  cur jsonb := nullif(current_setting('bc.transition_ctx', true), '')::jsonb;
  ctx jsonb := jsonb_build_object('c', p_cause, 'k', p_actor_kind, 's', p_subject, 'r', p_correlation, 'x', p_rationale);
  t   jsonb;
  k   text;
BEGIN
  IF p_family NOT IN ('canonical','observation') THEN RAISE EXCEPTION 'unknown contract family %', p_family; END IF;
  IF jsonb_typeof(p_targets) IS DISTINCT FROM 'array' OR jsonb_array_length(p_targets) = 0 THEN
    RAISE EXCEPTION 'a transition declaration must name at least one exact target';
  END IF;
  IF cur IS NULL OR cur ->> 'b' IS DISTINCT FROM b THEN cur := jsonb_build_object('b', b, 'e', '{}'::jsonb); END IF;
  FOR t IN SELECT value FROM jsonb_array_elements(p_targets) LOOP
    IF t ->> 'id' IS NULL OR t ->> 'version' IS NULL OR t ->> 'to' IS NULL THEN
      RAISE EXCEPTION 'a transition target needs id, version and to';
    END IF;
    k := p_family || '|' || (t ->> 'id')::uuid::text || '|' || (t ->> 'version') || '|' || (t ->> 'to');
    IF (cur -> 'e') ? k THEN
      RAISE EXCEPTION 'conflicting transition declaration: % is already declared in this statement', k;
    END IF;
    cur := jsonb_set(cur, ARRAY['e', k], ctx);
  END LOOP;
  PERFORM set_config('bc.transition_ctx', cur::text, true);
  RETURN true;
END $$;
REVOKE ALL ON FUNCTION contract.fn_declare_transition_context(text,jsonb,text,text,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION contract.fn_declare_transition_context(text,jsonb,text,text,text,text,text) TO served_app;

-- (b) CONSUMPTION: statement-level AFTER trigger removes this family's unused keys once the
--     statement's row triggers have run (also for zero-row statements), so a declared-but-unused key
--     cannot authorise a later statement that shares the statement_timestamp (a DO block / function).
CREATE FUNCTION contract.fn_contract_version_transition_consume() RETURNS trigger LANGUAGE plpgsql
  SET search_path = pg_catalog AS $$
DECLARE cur jsonb := nullif(current_setting('bc.transition_ctx', true), '')::jsonb;
BEGIN
  IF cur IS NOT NULL THEN
    cur := jsonb_set(cur, '{e}', coalesce((SELECT jsonb_object_agg(key, value) FROM jsonb_each(cur -> 'e')
                                          WHERE key NOT LIKE TG_ARGV[0] || '|%'), '{}'::jsonb));
    PERFORM set_config('bc.transition_ctx', cur::text, true);
  END IF;
  RETURN NULL;
END $$;

-- (c) The EMITTER: SECURITY DEFINER owned by the NOLOGIN emitter role (the only INSERT holder).
--     Emits only for a row whose EXACT key was declared in THIS statement, then removes that key.
CREATE FUNCTION contract.fn_contract_version_transition_emit() RETURNS trigger LANGUAGE plpgsql
  SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE
  fam text  := TG_ARGV[0];
  cid text  := to_jsonb(NEW) ->> (fam || '_contract_id');
  k   text  := fam || '|' || cid || '|' || NEW.version_code || '|' || NEW.governance_state_code;
  cur jsonb := nullif(current_setting('bc.transition_ctx', true), '')::jsonb;
  ctx jsonb;
BEGIN
  IF TG_OP = 'UPDATE' AND OLD.governance_state_code IS NOT DISTINCT FROM NEW.governance_state_code THEN RETURN NULL; END IF;
  IF TG_OP = 'INSERT' AND NEW.governance_state_code = 'draft' THEN RETURN NULL; END IF;
  IF cur IS NULL OR cur ->> 'b' IS DISTINCT FROM (statement_timestamp()::text || '|' || pg_current_xact_id()::text)
     OR NOT ((cur -> 'e') ? k) THEN
    RAISE EXCEPTION 'contract-version transition %.%/% % -> % refused: this exact transition was not declared in this statement (DEC-fbc085, Inv VI)',
      TG_TABLE_NAME, cid, NEW.version_code, CASE WHEN TG_OP = 'UPDATE' THEN OLD.governance_state_code END, NEW.governance_state_code
      USING ERRCODE = 'check_violation';
  END IF;
  ctx := cur -> 'e' -> k;
  PERFORM set_config('bc.transition_ctx', (cur #- ARRAY['e', k])::text, true);   -- one-shot
  EXECUTE format('INSERT INTO contract.%I (%I, version_code, from_state_code, to_state_code, transition_cause_code,
      actor_kind_code, actor_subject, request_correlation_id, rationale_text, contract_json_sha256,
      db_principal_name, transaction_id, recorded_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)',
      fam || '_contract_version_transition', fam || '_contract_id')
  USING cid::uuid, NEW.version_code, CASE WHEN TG_OP = 'UPDATE' THEN OLD.governance_state_code END,
        NEW.governance_state_code, ctx ->> 'c', ctx ->> 'k', ctx ->> 's', ctx ->> 'r', ctx ->> 'x',
        encode(sha256(convert_to(NEW.contract_json::text, 'UTF8')), 'hex'),
        session_user, pg_current_xact_id(), clock_timestamp();
  RETURN NULL;
END $$;
ALTER FUNCTION contract.fn_contract_version_transition_emit() OWNER TO bc_contract_evidence_emitter;
REVOKE ALL ON FUNCTION contract.fn_contract_version_transition_emit() FROM PUBLIC;

-- (d) The INSERT GUARD on the evidence tables: only the emitter, only from inside the version-table
--     trigger, only for a version whose CURRENT state equals to_state; metadata is re-derived.
CREATE FUNCTION contract.fn_contract_version_transition_guard() RETURNS trigger LANGUAGE plpgsql
  SET search_path = pg_catalog AS $$
DECLARE fam text := TG_ARGV[0]; cur text;
BEGIN
  IF current_user <> 'bc_contract_evidence_emitter' OR pg_trigger_depth() < 2 THEN
    RAISE EXCEPTION 'direct INSERT into contract.% refused: rows are emitted only by the version-table trigger (DEC-fbc085)', TG_TABLE_NAME;
  END IF;
  EXECUTE format('SELECT governance_state_code FROM contract.%I WHERE %I = $1 AND version_code = $2',
                 fam || '_contract_version', fam || '_contract_id')
    INTO cur USING (to_jsonb(NEW) ->> (fam || '_contract_id'))::uuid, NEW.version_code;
  IF cur IS DISTINCT FROM NEW.to_state_code THEN
    RAISE EXCEPTION 'transition row refused: version state % does not equal to_state %', cur, NEW.to_state_code;
  END IF;
  NEW.db_principal_name := session_user;
  NEW.transaction_id    := pg_current_xact_id();
  NEW.recorded_at       := clock_timestamp();
  RETURN NEW;
END $$;

DO $$ DECLARE fam text; BEGIN
  FOREACH fam IN ARRAY ARRAY['canonical','observation'] LOOP
    EXECUTE format('CREATE TRIGGER trg_%1$s_contract_version_transition_emit AFTER INSERT OR UPDATE OF governance_state_code
      ON contract.%1$s_contract_version FOR EACH ROW EXECUTE FUNCTION contract.fn_contract_version_transition_emit(%1$L)', fam);
    EXECUTE format('CREATE TRIGGER trg_%1$s_contract_version_transition_consume AFTER INSERT OR UPDATE
      ON contract.%1$s_contract_version FOR EACH STATEMENT EXECUTE FUNCTION contract.fn_contract_version_transition_consume(%1$L)', fam);
    EXECUTE format('CREATE TRIGGER trg_%1$s_contract_version_transition_guard BEFORE INSERT
      ON contract.%1$s_contract_version_transition FOR EACH ROW EXECUTE FUNCTION contract.fn_contract_version_transition_guard(%1$L)', fam);
    EXECUTE format('CREATE TRIGGER trg_%1$s_contract_version_transition_append_only BEFORE UPDATE OR DELETE OR TRUNCATE
      ON contract.%1$s_contract_version_transition FOR EACH STATEMENT EXECUTE FUNCTION infrastructure.fn_reject_mutation()', fam);
  END LOOP;
END $$;

-- ── Part 3 (corpus; runs as the NON-superuser served login) ─────────────────
CREATE SCHEMA t;
GRANT USAGE ON SCHEMA t TO PUBLIC;
-- a refusal is expected and must match
CREATE FUNCTION t.expect_error(p_sql text, p_like text) RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  BEGIN EXECUTE p_sql; EXCEPTION WHEN OTHERS THEN
    IF SQLERRM NOT LIKE p_like THEN RAISE EXCEPTION 'wrong error for [%]: %', left(p_sql, 80), SQLERRM; END IF;
    RAISE NOTICE 'PASS refused: % -> %', left(regexp_replace(p_sql, '\s+', ' ', 'g'), 70), left(SQLERRM, 110); RETURN;
  END;
  RAISE EXCEPTION 'EXPECTED REFUSAL did not happen: %', p_sql;
END $$;
-- compound forms: EITHER refused (fail-closed) OR committed with every row correctly attributed; never misattributed.
-- A committed outcome is checked and then rolled back so later tests start from the same state.
CREATE FUNCTION t.correct_or_refused(p_label text, p_sql text, p_check text, p_refuse_like text) RETURNS text LANGUAGE plpgsql AS $$
DECLARE ok boolean;
BEGIN
  BEGIN
    BEGIN EXECUTE p_sql;
    EXCEPTION WHEN OTHERS THEN
      IF SQLERRM LIKE p_refuse_like THEN RAISE NOTICE 'PASS % (refused, fail-closed): %', p_label, left(SQLERRM, 110); RETURN 'refused'; END IF;
      RAISE EXCEPTION '% wrong error: %', p_label, SQLERRM;
    END;
    EXECUTE p_check INTO ok;
    IF ok IS NOT TRUE THEN RAISE EXCEPTION '% MISATTRIBUTED evidence', p_label; END IF;
    RAISE EXCEPTION USING ERRCODE = 'P0099', MESSAGE = 'rollback-probe';
  EXCEPTION WHEN SQLSTATE 'P0099' THEN
    RAISE NOTICE 'PASS % (committed, every row correctly attributed; rolled back)', p_label; RETURN 'correct';
  END;
END $$;
-- the identity sequence advances even for rolled-back inserts: it proves an emission INSERT executed
CREATE FUNCTION t.seq_last(p_table text) RETURNS bigint LANGUAGE sql SECURITY DEFINER AS
  $$ SELECT coalesce(pg_sequence_last_value(pg_get_serial_sequence(p_table, 'transition_seq')::regclass), 0) $$;
-- declaration shorthand for the corpus
CREATE FUNCTION t.d(p_family text, p_id text, p_version text, p_to text, p_cause text, p_kind text, p_subject text, p_corr text, p_rationale text DEFAULT NULL)
RETURNS boolean LANGUAGE sql AS $$
  SELECT contract.fn_declare_transition_context(p_family, jsonb_build_array(jsonb_build_object('id', p_id, 'version', p_version, 'to', p_to)),
                                                p_cause, p_kind, p_subject, p_corr, p_rationale) $$;
\connect - served_app
\set C '''00000000-0000-0000-0000-00000000c150'''
\set O '''00000000-0000-0000-0000-00000000a120'''

\echo T1 undeclared UPDATE refused, state unchanged
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='pending_provisioning' WHERE version_code='1.6.0'$q$, '%was not declared in this statement%');

\echo T2 7c-c sequence: each write declares its exact target; one row per transition (both families)
UPDATE contract.canonical_contract_version SET governance_state_code='pending_provisioning' WHERE canonical_contract_id=:C AND version_code='1.6.0'
  AND (SELECT t.d('canonical', :C, '1.6.0', 'pending_provisioning', 'governed_request','authenticated_http','sub-A','req-1'));
UPDATE contract.canonical_contract_version SET governance_state_code='active' WHERE canonical_contract_id=:C AND version_code='1.6.0'
  AND (SELECT t.d('canonical', :C, '1.6.0', 'active', 'provisioning_readiness','service_system','bc-core:provisioning-readiness',NULL));
UPDATE contract.canonical_contract_version SET governance_state_code='superseded' WHERE canonical_contract_id=:C AND version_code='1.5.0'
  AND (SELECT t.d('canonical', :C, '1.5.0', 'superseded', 'governed_request','authenticated_http','sub-B','req-2'));
UPDATE contract.observation_contract_version SET governance_state_code='superseded' WHERE observation_contract_id=:O AND version_code='1.2.0'
  AND (SELECT t.d('observation', :O, '1.2.0', 'superseded', 'governed_request','authenticated_http','sub-B','req-3'));
DO $$ BEGIN
  IF (SELECT count(*) FROM contract.canonical_contract_version_transition) <> 3 THEN RAISE EXCEPTION 'T2 canonical count'; END IF;
  IF (SELECT count(*) FROM contract.observation_contract_version_transition) <> 1 THEN RAISE EXCEPTION 'T2 observation count'; END IF;
  IF (SELECT string_agg(from_state_code||'>'||to_state_code||':'||actor_subject, ',' ORDER BY transition_seq) FROM contract.canonical_contract_version_transition)
     <> 'approved>pending_provisioning:sub-A,pending_provisioning>active:bc-core:provisioning-readiness,active>superseded:sub-B' THEN RAISE EXCEPTION 'T2 order/attribution'; END IF;
  IF (SELECT contract_json_sha256 FROM contract.canonical_contract_version_transition WHERE version_code='1.5.0')
     <> encode(sha256(convert_to('{"b": 1}', 'UTF8')), 'hex') THEN RAISE EXCEPTION 'T2 sha representation'; END IF;
  RAISE NOTICE 'PASS T2';
END $$;

\echo T3 A declared then B undeclared in ONE transaction -> B refused; same inside ONE DO block
BEGIN;
UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE canonical_contract_id=:C AND version_code='9.0.0'
  AND (SELECT t.d('canonical', :C, '9.0.0', 'review', 'governed_request','authenticated_http','sub-A','req-4'));
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='approved' WHERE version_code='9.0.0'$q$, '%was not declared%');
ROLLBACK;
SELECT t.expect_error($q$DO $d$ BEGIN
  UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0'
    AND (SELECT t.d('canonical','00000000-0000-0000-0000-00000000c150','9.0.0','review','governed_request','authenticated_http','s','r'));
  UPDATE contract.canonical_contract_version SET governance_state_code='approved' WHERE version_code='9.0.0';
END $d$$q$, '%was not declared%');

\echo T4 a declaration made by an EARLIER statement authorises nothing later; savepoint rollback restores nothing usable
BEGIN;
SELECT t.d('canonical', :C, '9.0.0', 'review', 'governed_request','authenticated_http','sub-A','req-5');
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0'$q$, '%was not declared%');
SAVEPOINT s1;
UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE canonical_contract_id=:C AND version_code='9.0.0'
  AND (SELECT t.d('canonical', :C, '9.0.0', 'review', 'governed_request','authenticated_http','sub-A','req-6'));
ROLLBACK TO SAVEPOINT s1;
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0'$q$, '%was not declared%');
ROLLBACK;

\echo T5 rollback leaves zero rows; same-state UPDATE and draft INSERT emit zero (and need no declaration)
BEGIN;
UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE canonical_contract_id=:C AND version_code='9.0.0'
  AND (SELECT t.d('canonical', :C, '9.0.0', 'review', 'governed_request','authenticated_http','s','r'));
ROLLBACK;
UPDATE contract.canonical_contract_version SET governance_state_code='draft' WHERE version_code='9.0.0';
INSERT INTO contract.canonical_contract_version VALUES (:C,'9.1.0','{}','draft');
DO $$ BEGIN IF (SELECT count(*) FROM contract.canonical_contract_version_transition) <> 3 THEN RAISE EXCEPTION 'T5 count'; END IF; RAISE NOTICE 'PASS T5'; END $$;

\echo T6 non-draft INSERT: undeclared refused; declared emits one birth row (from NULL)
SELECT t.expect_error($q$INSERT INTO contract.canonical_contract_version VALUES ('00000000-0000-0000-0000-00000000c150','9.2.0','{}','approved')$q$, '%was not declared%');
INSERT INTO contract.canonical_contract_version SELECT :C,'9.2.0','{}','approved'
  WHERE (SELECT t.d('canonical', :C, '9.2.0', 'approved', 'authoring_chain','service_system','bc-core:author-observation-chain',NULL));
DO $$ BEGIN IF (SELECT count(*) FROM contract.canonical_contract_version_transition WHERE version_code='9.2.0' AND from_state_code IS NULL) <> 1 THEN RAISE EXCEPTION 'T6'; END IF; RAISE NOTICE 'PASS T6'; END $$;

\echo T7 invalid cause / missing request identity / short operator rationale / missing subject refused (state unchanged)
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0' AND (SELECT t.d('canonical','00000000-0000-0000-0000-00000000c150','9.0.0','review','because','authenticated_http','s','r'))$q$, '%check constraint%');
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0' AND (SELECT t.d('canonical','00000000-0000-0000-0000-00000000c150','9.0.0','review','governed_request','authenticated_http','s',NULL))$q$, '%actor_check%');
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0' AND (SELECT t.d('canonical','00000000-0000-0000-0000-00000000c150','9.0.0','review','operator_sql','operator_sql','op','x','too short'))$q$, '%actor_check%');
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0' AND (SELECT t.d('canonical','00000000-0000-0000-0000-00000000c150','9.0.0','review','governed_request','authenticated_http',NULL,'r'))$q$, '%actor_subject%');

\echo T8 bulk: ONE declaration names every exact target; N rows, each keyed
UPDATE contract.canonical_contract_version SET governance_state_code='review'
  WHERE canonical_contract_id IN ('00000000-0000-0000-0000-0000000b0001','00000000-0000-0000-0000-0000000b0002')
    AND (SELECT contract.fn_declare_transition_context('canonical',
          '[{"id":"00000000-0000-0000-0000-0000000b0001","version":"1.0.0","to":"review"},{"id":"00000000-0000-0000-0000-0000000b0002","version":"1.0.0","to":"review"}]',
          'bulk_transition','authenticated_http','sub-C','req-7',NULL));
DO $$ BEGIN IF (SELECT count(*) FROM contract.canonical_contract_version_transition WHERE actor_subject='sub-C') <> 2 THEN RAISE EXCEPTION 'T8 bulk count'; END IF; RAISE NOTICE 'PASS T8 bulk'; END $$;
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='approved'
  WHERE canonical_contract_id IN ('00000000-0000-0000-0000-0000000b0001','00000000-0000-0000-0000-0000000b0002')
    AND (SELECT t.d('canonical','00000000-0000-0000-0000-0000000b0001','1.0.0','approved','bulk_transition','authenticated_http','sub-C','req-8'))$q$,
  '%was not declared%');

\echo T13 compound statements (gen-1afb60-02 F2): never misattributed
SELECT t.correct_or_refused('T13a two declared same-family CTEs',
  $q$WITH a AS (UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE canonical_contract_id='00000000-0000-0000-0000-0000000b0003'
                AND (SELECT t.d('canonical','00000000-0000-0000-0000-0000000b0003','1.0.0','review','governed_request','authenticated_http','cte-A','req-A')) RETURNING 1),
          b AS (UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE canonical_contract_id='00000000-0000-0000-0000-0000000b0004'
                AND (SELECT t.d('canonical','00000000-0000-0000-0000-0000000b0004','1.0.0','review','governed_request','authenticated_http','cte-B','req-B')) RETURNING 1)
     SELECT (SELECT count(*) FROM a) + (SELECT count(*) FROM b)$q$,
  $q$SELECT (SELECT actor_subject||'/'||request_correlation_id FROM contract.canonical_contract_version_transition WHERE canonical_contract_id='00000000-0000-0000-0000-0000000b0003') = 'cte-A/req-A'
        AND (SELECT actor_subject||'/'||request_correlation_id FROM contract.canonical_contract_version_transition WHERE canonical_contract_id='00000000-0000-0000-0000-0000000b0004') = 'cte-B/req-B'$q$,
  '%was not declared%');
SELECT t.expect_error(
  $q$WITH a AS (UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE canonical_contract_id='00000000-0000-0000-0000-0000000b0003'
                AND (SELECT t.d('canonical','00000000-0000-0000-0000-0000000b0003','1.0.0','review','governed_request','authenticated_http','cte-A-only','req-A')) RETURNING 1),
          b AS (UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE canonical_contract_id='00000000-0000-0000-0000-0000000b0004' RETURNING 1)
     SELECT (SELECT count(*) FROM a) + (SELECT count(*) FROM b)$q$, '%0000000b0004%was not declared%');
SELECT t.correct_or_refused('T13c declared cross-family CTEs',
  $q$WITH a AS (UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE canonical_contract_id='00000000-0000-0000-0000-0000000b0003'
                AND (SELECT t.d('canonical','00000000-0000-0000-0000-0000000b0003','1.0.0','review','governed_request','authenticated_http','cte-C','req-C')) RETURNING 1),
          b AS (UPDATE contract.observation_contract_version SET governance_state_code='review' WHERE observation_contract_id='00000000-0000-0000-0000-0000000a0001'
                AND (SELECT t.d('observation','00000000-0000-0000-0000-0000000a0001','1.0.0','review','governed_request','authenticated_http','cte-O','req-O')) RETURNING 1)
     SELECT (SELECT count(*) FROM a) + (SELECT count(*) FROM b)$q$,
  $q$SELECT (SELECT actor_subject FROM contract.canonical_contract_version_transition WHERE canonical_contract_id='00000000-0000-0000-0000-0000000b0003') = 'cte-C'
        AND (SELECT actor_subject FROM contract.observation_contract_version_transition WHERE observation_contract_id='00000000-0000-0000-0000-0000000a0001') = 'cte-O'$q$,
  '%was not declared%');
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE canonical_contract_id='00000000-0000-0000-0000-0000000b0003'
  AND (SELECT t.d('canonical','00000000-0000-0000-0000-0000000b0003','1.0.0','review','governed_request','authenticated_http','x','r1'))
  AND (SELECT t.d('canonical','00000000-0000-0000-0000-0000000b0003','1.0.0','review','governed_request','authenticated_http','y','r2'))$q$,
  '%conflicting transition declaration%');
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE canonical_contract_id='00000000-0000-0000-0000-0000000b0003'
  AND (SELECT t.d('canonical','00000000-0000-0000-0000-0000000b0003','1.0.0','approved','governed_request','authenticated_http','x','r'))$q$,
  '%was not declared%');
SELECT t.expect_error($q$DO $d$ BEGIN
  UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE canonical_contract_id='00000000-0000-0000-0000-0000000b0004'
    AND (SELECT contract.fn_declare_transition_context('canonical',
          '[{"id":"00000000-0000-0000-0000-0000000b0003","version":"1.0.0","to":"review"},{"id":"00000000-0000-0000-0000-0000000b0004","version":"1.0.0","to":"review"}]',
          'governed_request','authenticated_http','left','over',NULL));
  UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE canonical_contract_id='00000000-0000-0000-0000-0000000b0003';
END $d$$q$, '%0000000b0003%was not declared%');

\echo T15 (F5) atomicity after a REAL emission: row 1 emits, row 2 fails at emission; everything rolls back (both families)
DO $$ DECLARE fam text; ids text[]; s0 bigint; s1 bigint; BEGIN
  FOREACH fam IN ARRAY ARRAY['canonical','observation'] LOOP
    ids := CASE fam WHEN 'canonical' THEN ARRAY['00000000-0000-0000-0000-0000000b0003','00000000-0000-0000-0000-0000000b0004']
                    ELSE ARRAY['00000000-0000-0000-0000-0000000a0001','00000000-0000-0000-0000-0000000a0002'] END;
    s0 := t.seq_last('contract.' || fam || '_contract_version_transition');
    BEGIN
      EXECUTE format($f$UPDATE contract.%1$I SET governance_state_code='approved' WHERE %2$I IN (%3$L::uuid, %4$L::uuid)
        AND (SELECT t.d(%5$L, %3$L, '1.0.0', 'approved', 'governed_request', 'authenticated_http', 'ok', 'req-ok'))
        AND (SELECT t.d(%5$L, %4$L, '1.0.0', 'approved', 'governed_request', 'authenticated_http', 'bad', NULL))$f$,
        fam || '_contract_version', fam || '_contract_id', ids[1], ids[2], fam);
      RAISE EXCEPTION 'T15 % expected failure did not happen', fam;
    EXCEPTION WHEN check_violation THEN
      IF SQLERRM NOT LIKE '%actor_check%' THEN RAISE; END IF;
    END;
    s1 := t.seq_last('contract.' || fam || '_contract_version_transition');
    IF s1 - s0 <> 2 THEN RAISE EXCEPTION 'T15 % precondition NOT met: % emission INSERT(s) executed (need 2: one succeeded, then one failed)', fam, s1 - s0; END IF;
    EXECUTE format('SELECT count(*) FROM contract.%I WHERE %I = ANY ($1::uuid[])', fam || '_contract_version_transition', fam || '_contract_id') INTO s1 USING ids;
    IF s1 <> 0 THEN RAISE EXCEPTION 'T15 % evidence residue', fam; END IF;
    EXECUTE format('SELECT count(*) FROM contract.%I WHERE %I = ANY ($1::uuid[]) AND governance_state_code <> ''draft''', fam || '_contract_version', fam || '_contract_id') INTO s1 USING ids;
    IF s1 <> 0 THEN RAISE EXCEPTION 'T15 % state residue', fam; END IF;
    RAISE NOTICE 'PASS T15 %: 1 emission executed before the failure; 0 rows, 0 state changes after rollback', fam;
  END LOOP;
END $$;

\echo T9 F1 forgery by the served login: direct INSERT / UPDATE / DELETE / TRUNCATE / call emitter / assume roles / disable trigger / replica bypass
SELECT t.expect_error($q$INSERT INTO contract.canonical_contract_version_transition (canonical_contract_id, version_code, from_state_code, to_state_code, transition_cause_code, actor_kind_code, actor_subject, request_correlation_id, contract_json_sha256, db_principal_name, transaction_id, recorded_at)
  VALUES ('00000000-0000-0000-0000-00000000c150','1.5.0','active','superseded','governed_request','authenticated_http','forger','r', repeat('a',64), 'someone_else', '1'::xid8, '2020-01-01')$q$, '%permission denied%');
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version_transition SET actor_subject='x'$q$, '%permission denied%');
SELECT t.expect_error($q$DELETE FROM contract.canonical_contract_version_transition$q$, '%permission denied%');
SELECT t.expect_error($q$TRUNCATE contract.canonical_contract_version_transition$q$, '%permission denied%');
SELECT t.expect_error($q$SELECT contract.fn_contract_version_transition_emit()$q$, '%function%');
SELECT t.expect_error($q$SET ROLE bc_contract_evidence_emitter$q$, '%permission denied%');
SELECT t.expect_error($q$SET ROLE bc_schema_owner$q$, '%permission denied%');
SELECT t.expect_error($q$ALTER TABLE contract.canonical_contract_version DISABLE TRIGGER trg_canonical_contract_version_transition_emit$q$, '%must be owner%');
SELECT t.expect_error($q$ALTER TABLE contract.canonical_contract_version_transition DISABLE TRIGGER ALL$q$, '%must be owner%');
SELECT t.expect_error($q$SET session_replication_role = replica$q$, '%permission denied%');

\echo T14 effective privileges of every ordinary principal (catalog, incl. inherited membership)
DO $$ DECLARE r text; tbl text; BEGIN
  FOREACH r IN ARRAY ARRAY['served_app','chain_auditor_readonly'] LOOP
    IF (SELECT rolsuper OR rolbypassrls OR rolreplication FROM pg_roles WHERE rolname = r) THEN RAISE EXCEPTION 'T14 % is privileged', r; END IF;
    IF pg_has_role(r, 'bc_schema_owner', 'MEMBER') OR pg_has_role(r, 'bc_contract_evidence_emitter', 'MEMBER') THEN RAISE EXCEPTION 'T14 % member of owner/emitter', r; END IF;
    FOREACH tbl IN ARRAY ARRAY['contract.canonical_contract_version_transition','contract.observation_contract_version_transition'] LOOP
      IF has_table_privilege(r, tbl, 'INSERT, UPDATE, DELETE, TRUNCATE, TRIGGER, REFERENCES') THEN RAISE EXCEPTION 'T14 % can write %', r, tbl; END IF;
    END LOOP;
    FOREACH tbl IN ARRAY ARRAY['contract.canonical_contract_version','contract.observation_contract_version'] LOOP
      IF pg_has_role(r, (SELECT relowner FROM pg_class WHERE oid = tbl::regclass), 'MEMBER') THEN RAISE EXCEPTION 'T14 % owns %', r, tbl; END IF;
      IF has_table_privilege(r, tbl, 'TRIGGER, TRUNCATE') THEN RAISE EXCEPTION 'T14 % has TRIGGER/TRUNCATE on %', r, tbl; END IF;
    END LOOP;
  END LOOP;
  IF has_function_privilege('served_app', 'contract.fn_contract_version_transition_emit()', 'EXECUTE') THEN RAISE EXCEPTION 'T14 emitter executable'; END IF;
  RAISE NOTICE 'PASS T14';
END $$;

\echo T12 metadata is derived, not supplied: principal = the writing login session
DO $$ BEGIN IF EXISTS (SELECT 1 FROM contract.canonical_contract_version_transition WHERE db_principal_name <> 'served_app')
  OR EXISTS (SELECT 1 FROM contract.observation_contract_version_transition WHERE db_principal_name <> 'served_app') THEN RAISE EXCEPTION 'T12 principal'; END IF;
  RAISE NOTICE 'PASS T12'; END $$;

\connect - postgres
\echo T10 even the INSERT-holding emitter role cannot insert outside the version-table trigger (guard)
SET ROLE bc_contract_evidence_emitter;
SELECT t.expect_error($q$INSERT INTO contract.canonical_contract_version_transition (canonical_contract_id, version_code, from_state_code, to_state_code, transition_cause_code, actor_kind_code, actor_subject, request_correlation_id, contract_json_sha256, db_principal_name, transaction_id, recorded_at)
  VALUES ('00000000-0000-0000-0000-00000000c150','1.5.0','active','superseded','governed_request','authenticated_http','forger','r', repeat('a',64), 'x', '1'::xid8, now())$q$, '%refused: rows are emitted only by the version-table trigger%');
RESET ROLE;
\echo T11 the OWNER keeps table privileges (recovery authority, DDL) but the append-only trigger still refuses UPDATE/DELETE/TRUNCATE
SET ROLE bc_schema_owner;
SELECT t.expect_error($q$DELETE FROM contract.canonical_contract_version_transition$q$, '%append-only%');
SELECT t.expect_error($q$TRUNCATE contract.canonical_contract_version_transition$q$, '%append-only%');
RESET ROLE;
SELECT transition_seq, version_code, from_state_code, to_state_code, transition_cause_code, actor_kind_code, actor_subject, request_correlation_id, db_principal_name
  FROM contract.canonical_contract_version_transition ORDER BY transition_seq;
\echo ALL PASS
