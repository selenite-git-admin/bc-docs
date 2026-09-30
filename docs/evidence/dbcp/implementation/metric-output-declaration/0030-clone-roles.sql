-- clone roles with the live attributes (read 2026-09-30 from bc_platform_dev pg_roles); passwords are clone-only
CREATE ROLE bc_audit_feed LOGIN INHERIT PASSWORD 'clone';
CREATE ROLE bc_audit_migrator LOGIN INHERIT PASSWORD 'clone';
CREATE ROLE bc_audit_owner NOLOGIN INHERIT;
CREATE ROLE bc_audit_runtime LOGIN INHERIT PASSWORD 'clone';
CREATE ROLE bc_capture_ro LOGIN INHERIT PASSWORD 'clone';
CREATE ROLE bc_contract_evidence_emitter NOLOGIN NOINHERIT;
CREATE ROLE bc_directory_writer NOLOGIN INHERIT;
CREATE ROLE bc_metric_admission_writer NOLOGIN INHERIT;
CREATE ROLE bc_offpool_importer NOLOGIN INHERIT;
CREATE ROLE bc_platform_runtime LOGIN NOINHERIT PASSWORD 'clone';
CREATE ROLE bc_schema_owner NOLOGIN INHERIT;
CREATE ROLE bc_tenant_owner LOGIN NOINHERIT PASSWORD 'clone';
CREATE ROLE bc_tenant_runtime LOGIN NOINHERIT PASSWORD 'clone';
CREATE ROLE chain_auditor_readonly NOLOGIN NOINHERIT;
GRANT bc_audit_owner TO bc_audit_migrator;
GRANT pg_read_all_data TO bc_capture_ro;
