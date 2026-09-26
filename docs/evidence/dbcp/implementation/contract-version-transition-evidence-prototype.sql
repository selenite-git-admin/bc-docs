-- DEC-fbc085 / TSK-56c689 — PROTOTYPE of the proposed emitter (successor 1, gen-1afb60 F1/F2).
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
INSERT INTO contract.observation_contract_version VALUES ('00000000-0000-0000-0000-00000000a120','1.2.0','{"o":1}','active');

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

-- (a) The DECLARATION: called INSIDE the writing statement (an uncorrelated sub-select = one init-plan).
--     Sets EVERY field explicitly (no inheritance of an older subject/rationale) and binds the context
--     to THIS statement + transaction. Invoker rights; it grants nothing — it is a writer assertion.
CREATE FUNCTION contract.fn_declare_transition_context(
  p_cause text, p_actor_kind text, p_subject text, p_correlation text, p_rationale text)
RETURNS boolean LANGUAGE plpgsql VOLATILE SET search_path = pg_catalog AS $$
BEGIN
  PERFORM set_config('bc.transition_cause',       coalesce(p_cause, ''),       true);
  PERFORM set_config('bc.transition_actor_kind',  coalesce(p_actor_kind, ''),  true);
  PERFORM set_config('bc.transition_subject',     coalesce(p_subject, ''),     true);
  PERFORM set_config('bc.transition_correlation', coalesce(p_correlation, ''), true);
  PERFORM set_config('bc.transition_rationale',   coalesce(p_rationale, ''),   true);
  PERFORM set_config('bc.transition_binding',     statement_timestamp()::text || '|' || pg_current_xact_id()::text, true);
  RETURN true;
END $$;
REVOKE ALL ON FUNCTION contract.fn_declare_transition_context(text,text,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION contract.fn_declare_transition_context(text,text,text,text,text) TO served_app;

-- (b) RESET + CONSUMPTION: the same function runs as a BEFORE-STATEMENT trigger (wipes any context
--     declared by an EARLIER statement, before this statement's init-plan declares its own) and as an
--     AFTER-STATEMENT trigger (clears it once this statement's row triggers ran, also for zero rows).
--     A context therefore never outlives, and never pre-dates, the one writing statement.
CREATE FUNCTION contract.fn_contract_version_transition_consume() RETURNS trigger LANGUAGE plpgsql
  SET search_path = pg_catalog AS $$
BEGIN
  PERFORM set_config(k, '', true) FROM unnest(ARRAY['bc.transition_cause','bc.transition_actor_kind',
    'bc.transition_subject','bc.transition_correlation','bc.transition_rationale','bc.transition_binding']) k;
  RETURN NULL;
END $$;

-- (c) The EMITTER: SECURITY DEFINER owned by the NOLOGIN emitter role (the only INSERT holder).
CREATE FUNCTION contract.fn_contract_version_transition_emit() RETURNS trigger LANGUAGE plpgsql
  SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE
  fam   text := TG_ARGV[0];
  cause text := nullif(current_setting('bc.transition_cause', true), '');
  bind  text := nullif(current_setting('bc.transition_binding', true), '');
BEGIN
  IF TG_OP = 'UPDATE' AND OLD.governance_state_code IS NOT DISTINCT FROM NEW.governance_state_code THEN RETURN NULL; END IF;
  IF TG_OP = 'INSERT' AND NEW.governance_state_code = 'draft' THEN RETURN NULL; END IF;
  IF cause IS NULL OR bind IS DISTINCT FROM (statement_timestamp()::text || '|' || pg_current_xact_id()::text) THEN
    RAISE EXCEPTION 'contract-version transition %.% % -> % refused: no transition context declared in this statement (DEC-fbc085, Inv VI)',
      TG_TABLE_NAME, NEW.version_code, CASE WHEN TG_OP = 'UPDATE' THEN OLD.governance_state_code END, NEW.governance_state_code
      USING ERRCODE = 'check_violation';
  END IF;
  EXECUTE format('INSERT INTO contract.%I (%I, version_code, from_state_code, to_state_code, transition_cause_code,
      actor_kind_code, actor_subject, request_correlation_id, rationale_text, contract_json_sha256,
      db_principal_name, transaction_id, recorded_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)',
      fam || '_contract_version_transition', fam || '_contract_id')
  USING (to_jsonb(NEW) ->> (fam || '_contract_id'))::uuid, NEW.version_code,
        CASE WHEN TG_OP = 'UPDATE' THEN OLD.governance_state_code END, NEW.governance_state_code, cause,
        nullif(current_setting('bc.transition_actor_kind', true), ''),
        nullif(current_setting('bc.transition_subject', true), ''),
        nullif(current_setting('bc.transition_correlation', true), ''),
        nullif(current_setting('bc.transition_rationale', true), ''),
        encode(sha256(convert_to(NEW.contract_json::text, 'UTF8')), 'hex'),
        session_user, pg_current_xact_id(), clock_timestamp();
  RETURN NULL;
END $$;
ALTER FUNCTION contract.fn_contract_version_transition_emit() OWNER TO bc_contract_evidence_emitter;
REVOKE ALL ON FUNCTION contract.fn_contract_version_transition_emit() FROM PUBLIC;

-- (d) The INSERT GUARD on the evidence tables: only the emitter, only from inside the version-table
--     trigger, only for a version whose CURRENT state equals to_state; metadata is re-derived, never
--     taken from the inserter.
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
    EXECUTE format('CREATE TRIGGER trg_%1$s_contract_version_transition_reset BEFORE INSERT OR UPDATE
      ON contract.%1$s_contract_version FOR EACH STATEMENT EXECUTE FUNCTION contract.fn_contract_version_transition_consume()', fam);
    EXECUTE format('CREATE TRIGGER trg_%1$s_contract_version_transition_consume AFTER INSERT OR UPDATE
      ON contract.%1$s_contract_version FOR EACH STATEMENT EXECUTE FUNCTION contract.fn_contract_version_transition_consume()', fam);
    EXECUTE format('CREATE TRIGGER trg_%1$s_contract_version_transition_guard BEFORE INSERT
      ON contract.%1$s_contract_version_transition FOR EACH ROW EXECUTE FUNCTION contract.fn_contract_version_transition_guard(%1$L)', fam);
    EXECUTE format('CREATE TRIGGER trg_%1$s_contract_version_transition_append_only BEFORE UPDATE OR DELETE OR TRUNCATE
      ON contract.%1$s_contract_version_transition FOR EACH STATEMENT EXECUTE FUNCTION infrastructure.fn_reject_mutation()', fam);
  END LOOP;
END $$;

-- ── Part 3 (corpus; runs as the NON-superuser served role) ──────────────────
CREATE SCHEMA t;
GRANT USAGE ON SCHEMA t TO PUBLIC;
CREATE FUNCTION t.expect_error(p_sql text, p_like text) RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  BEGIN EXECUTE p_sql; EXCEPTION WHEN OTHERS THEN
    IF SQLERRM NOT LIKE p_like THEN RAISE EXCEPTION 'wrong error for [%]: %', p_sql, SQLERRM; END IF;
    RAISE NOTICE 'PASS refused: % -> %', left(p_sql, 60), left(SQLERRM, 90); RETURN;
  END;
  RAISE EXCEPTION 'EXPECTED REFUSAL did not happen: %', p_sql;
END $$;
\connect - served_app

\echo T1 undeclared UPDATE refused, state unchanged
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='pending_provisioning' WHERE version_code='1.6.0'$q$, '%no transition context declared%');

\echo T2 7c-c sequence: declared in-statement, one row per transition (both families)
UPDATE contract.canonical_contract_version SET governance_state_code='pending_provisioning'
  WHERE version_code='1.6.0' AND (SELECT contract.fn_declare_transition_context('governed_request','authenticated_http','sub-A','req-1',NULL));
UPDATE contract.canonical_contract_version SET governance_state_code='active'
  WHERE version_code='1.6.0' AND (SELECT contract.fn_declare_transition_context('provisioning_readiness','service_system','bc-core:provisioning-readiness',NULL,NULL));
UPDATE contract.canonical_contract_version SET governance_state_code='superseded'
  WHERE version_code='1.5.0' AND (SELECT contract.fn_declare_transition_context('governed_request','authenticated_http','sub-B','req-2',NULL));
UPDATE contract.observation_contract_version SET governance_state_code='superseded'
  WHERE version_code='1.2.0' AND (SELECT contract.fn_declare_transition_context('governed_request','authenticated_http','sub-B','req-3',NULL));
DO $$ BEGIN
  IF (SELECT count(*) FROM contract.canonical_contract_version_transition) <> 3 THEN RAISE EXCEPTION 'T2 canonical count'; END IF;
  IF (SELECT count(*) FROM contract.observation_contract_version_transition) <> 1 THEN RAISE EXCEPTION 'T2 observation count'; END IF;
  IF EXISTS (SELECT 1 FROM contract.canonical_contract_version_transition WHERE version_code='1.5.0' AND actor_subject <> 'sub-B') THEN RAISE EXCEPTION 'T2 actor leak'; END IF;
  IF (SELECT string_agg(from_state_code||'>'||to_state_code, ',' ORDER BY transition_seq) FROM contract.canonical_contract_version_transition WHERE version_code='1.6.0')
     <> 'approved>pending_provisioning,pending_provisioning>active' THEN RAISE EXCEPTION 'T2 order'; END IF;
  IF (SELECT contract_json_sha256 FROM contract.canonical_contract_version_transition WHERE version_code='1.5.0')
     <> encode(sha256(convert_to('{"b": 1}', 'UTF8')), 'hex') THEN RAISE EXCEPTION 'T2 sha representation'; END IF;
  RAISE NOTICE 'PASS T2';
END $$;

\echo T3 context is statement-scoped: A declared then B undeclared in ONE transaction -> B refused (also inside a DO block)
BEGIN;
UPDATE contract.canonical_contract_version SET governance_state_code='review'
  WHERE version_code='9.0.0' AND (SELECT contract.fn_declare_transition_context('governed_request','authenticated_http','sub-A','req-4',NULL));
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='approved' WHERE version_code='9.0.0'$q$, '%no transition context declared%');
ROLLBACK;
SELECT t.expect_error($q$DO $d$ BEGIN
  UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0'
    AND (SELECT contract.fn_declare_transition_context('governed_request','authenticated_http','s','r',NULL));
  UPDATE contract.canonical_contract_version SET governance_state_code='approved' WHERE version_code='9.0.0';
END $d$$q$, '%no transition context declared%');

\echo T4 a context declared in an EARLIER statement does not authorise a later one; savepoint rollback restores nothing usable
BEGIN;
SELECT contract.fn_declare_transition_context('governed_request','authenticated_http','sub-A','req-5',NULL);
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0'$q$, '%no transition context declared%');
SAVEPOINT s1;
UPDATE contract.canonical_contract_version SET governance_state_code='review'
  WHERE version_code='9.0.0' AND (SELECT contract.fn_declare_transition_context('governed_request','authenticated_http','sub-A','req-6',NULL));
ROLLBACK TO SAVEPOINT s1;
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0'$q$, '%no transition context declared%');
ROLLBACK;

\echo T5 rollback after a declared transition leaves zero rows; same-state UPDATE and draft INSERT emit zero
BEGIN;
UPDATE contract.canonical_contract_version SET governance_state_code='review'
  WHERE version_code='9.0.0' AND (SELECT contract.fn_declare_transition_context('governed_request','authenticated_http','s','r',NULL));
ROLLBACK;
UPDATE contract.canonical_contract_version SET governance_state_code='draft' WHERE version_code='9.0.0';
INSERT INTO contract.canonical_contract_version VALUES ('00000000-0000-0000-0000-00000000c150','9.1.0','{}','draft');
DO $$ BEGIN IF (SELECT count(*) FROM contract.canonical_contract_version_transition) <> 3 THEN RAISE EXCEPTION 'T5 count'; END IF; RAISE NOTICE 'PASS T5'; END $$;

\echo T6 non-draft INSERT: undeclared refused; declared emits one birth row (from NULL)
SELECT t.expect_error($q$INSERT INTO contract.canonical_contract_version VALUES ('00000000-0000-0000-0000-00000000c150','9.2.0','{}','approved')$q$, '%no transition context declared%');
INSERT INTO contract.canonical_contract_version SELECT '00000000-0000-0000-0000-00000000c150','9.2.0','{}','approved'
  WHERE (SELECT contract.fn_declare_transition_context('authoring_chain','service_system','bc-core:author-observation-chain',NULL,NULL));
DO $$ BEGIN IF (SELECT count(*) FROM contract.canonical_contract_version_transition WHERE version_code='9.2.0' AND from_state_code IS NULL) <> 1 THEN RAISE EXCEPTION 'T6'; END IF; RAISE NOTICE 'PASS T6'; END $$;

\echo T7 invalid cause / missing request identity / short operator rationale refused (state unchanged)
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0' AND (SELECT contract.fn_declare_transition_context('because','authenticated_http','s','r',NULL))$q$, '%check constraint%');
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0' AND (SELECT contract.fn_declare_transition_context('governed_request','authenticated_http','s',NULL,NULL))$q$, '%actor_check%');
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0' AND (SELECT contract.fn_declare_transition_context('operator_sql','operator_sql','op','x','too short'))$q$, '%actor_check%');
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version SET governance_state_code='review' WHERE version_code='9.0.0' AND (SELECT contract.fn_declare_transition_context('governed_request','authenticated_http',NULL,'r',NULL))$q$, '%actor_subject%');

\echo T8 bulk: one declaration covers exactly one statement; mixed failure is atomic
INSERT INTO contract.canonical_contract_version VALUES
  ('00000000-0000-0000-0000-0000000b0001','1.0.0','{}','draft'),('00000000-0000-0000-0000-0000000b0002','1.0.0','{}','draft');
UPDATE contract.canonical_contract_version SET governance_state_code='review'
  WHERE canonical_contract_id IN ('00000000-0000-0000-0000-0000000b0001','00000000-0000-0000-0000-0000000b0002')
    AND (SELECT contract.fn_declare_transition_context('bulk_transition','authenticated_http','sub-C','req-7',NULL));
DO $$ BEGIN IF (SELECT count(*) FROM contract.canonical_contract_version_transition WHERE actor_subject='sub-C') <> 2 THEN RAISE EXCEPTION 'T8 bulk count'; END IF; RAISE NOTICE 'PASS T8 bulk'; END $$;
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version
  SET governance_state_code = CASE WHEN canonical_contract_id='00000000-0000-0000-0000-0000000b0002' THEN (1/0)::text ELSE 'approved' END
  WHERE canonical_contract_id IN ('00000000-0000-0000-0000-0000000b0001','00000000-0000-0000-0000-0000000b0002')
    AND (SELECT contract.fn_declare_transition_context('bulk_transition','authenticated_http','sub-D','req-8',NULL))$q$, '%division by zero%');
DO $$ BEGIN IF EXISTS (SELECT 1 FROM contract.canonical_contract_version_transition WHERE actor_subject='sub-D')
  OR EXISTS (SELECT 1 FROM contract.canonical_contract_version WHERE governance_state_code='approved' AND canonical_contract_id='00000000-0000-0000-0000-0000000b0001')
  THEN RAISE EXCEPTION 'T8 atomicity'; END IF; RAISE NOTICE 'PASS T8 atomic'; END $$;

\echo T9 F1 forgery: direct INSERT / metadata override / UPDATE / DELETE / TRUNCATE refused for the served role
SELECT t.expect_error($q$INSERT INTO contract.canonical_contract_version_transition (canonical_contract_id, version_code, from_state_code, to_state_code, transition_cause_code, actor_kind_code, actor_subject, request_correlation_id, contract_json_sha256, db_principal_name, transaction_id, recorded_at)
  VALUES ('00000000-0000-0000-0000-00000000c150','1.5.0','active','superseded','governed_request','authenticated_http','forger','r', repeat('a',64), 'someone_else', '1'::xid8, '2020-01-01')$q$, '%permission denied%');
SELECT t.expect_error($q$UPDATE contract.canonical_contract_version_transition SET actor_subject='x'$q$, '%permission denied%');
SELECT t.expect_error($q$DELETE FROM contract.canonical_contract_version_transition$q$, '%permission denied%');
SELECT t.expect_error($q$TRUNCATE contract.canonical_contract_version_transition$q$, '%permission denied%');
SELECT t.expect_error($q$SELECT contract.fn_contract_version_transition_emit()$q$, '%function%');
SELECT t.expect_error($q$SET ROLE bc_contract_evidence_emitter$q$, '%permission denied%');
\connect - postgres
\echo T10 even WITH the INSERT privilege (emitter role, as superuser SET ROLE), a direct insert outside the trigger is refused by the guard
SET ROLE bc_contract_evidence_emitter;
SELECT t.expect_error($q$INSERT INTO contract.canonical_contract_version_transition (canonical_contract_id, version_code, from_state_code, to_state_code, transition_cause_code, actor_kind_code, actor_subject, request_correlation_id, contract_json_sha256, db_principal_name, transaction_id, recorded_at)
  VALUES ('00000000-0000-0000-0000-00000000c150','1.5.0','active','superseded','governed_request','authenticated_http','forger','r', repeat('a',64), 'x', '1'::xid8, now())$q$, '%refused: rows are emitted only by the version-table trigger%');
RESET ROLE;
\echo T11 owner/superuser authority (the recovery boundary) is NOT constrained by this design: append-only trigger still refuses UPDATE/DELETE/TRUNCATE for the owner
SET ROLE bc_schema_owner;
SELECT t.expect_error($q$DELETE FROM contract.canonical_contract_version_transition$q$, '%append-only%');
SELECT t.expect_error($q$TRUNCATE contract.canonical_contract_version_transition$q$, '%append-only%');
RESET ROLE;

\echo T12 metadata is derived, not supplied: principal = the writing login session (served_app)
DO $$ BEGIN IF EXISTS (SELECT 1 FROM contract.canonical_contract_version_transition WHERE db_principal_name <> 'served_app') THEN RAISE EXCEPTION 'T12 principal'; END IF; RAISE NOTICE 'PASS T12'; END $$;
SELECT transition_seq, version_code, from_state_code, to_state_code, transition_cause_code, actor_kind_code, actor_subject, db_principal_name FROM contract.canonical_contract_version_transition ORDER BY transition_seq;
\echo ALL PASS
