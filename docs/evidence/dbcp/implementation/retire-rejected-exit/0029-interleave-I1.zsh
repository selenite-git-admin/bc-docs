#!/bin/zsh
# I1 — the auditor's gen-0ad039-01 interleaving: the version's state changes BEFORE the record-insert guard holds its lock.
# Session B moves the version audit_pending -> audit_blocked in an open transaction (6 s), session A starts the retirement
# 2 s in. Old guard (read, then lock): A validates the stale audit_pending and succeeds. Fixed guard (lock, then read): A
# waits for B, then reads audit_blocked and is refused. A's transaction is rolled back; B's state change is reverted after.
set -u
C=cov-rre-proof; OUT=$1; MCV=293045c9-ed1f-48fb-aaaa-39566f91eec1; PAR=7f1c7ed6-4248-4518-b1e7-58b7d6763dbf
q(){ docker exec -i $C psql -X -qAt -U barecount -d bc_platform_dev; }
( print -r -- "BEGIN; SET LOCAL session_replication_role = replica;
UPDATE mcf.metric_contract_version SET governance_state_code = 'audit_blocked' WHERE metric_contract_version_uid = '$MCV';
SELECT 'B changed to audit_blocked (uncommitted) at ' || clock_timestamp(); SELECT pg_sleep(6); COMMIT;
SELECT 'B committed at ' || clock_timestamp();" | q > $OUT.b 2>&1 ) &
sleep 2
print -r -- "BEGIN;
SELECT 'A starts the retirement at ' || clock_timestamp();
SELECT 'A-RESULT=' || proof.try(\$x\$SELECT proof.retire('$MCV')\$x\$);
SELECT 'A sees version state ' || governance_state_code || ', parent archived=' || (SELECT (archived_at IS NOT NULL)::text FROM mcf.metric_contract WHERE metric_contract_uid = '$PAR') FROM mcf.metric_contract_version WHERE metric_contract_version_uid = '$MCV';
ROLLBACK;" | q > $OUT.a 2>&1
wait
print -r -- "BEGIN; SET LOCAL session_replication_role = replica; UPDATE mcf.metric_contract_version SET governance_state_code = 'audit_pending' WHERE metric_contract_version_uid = '$MCV'; COMMIT;" | q > /dev/null
{ print -- '--- session B'; cat $OUT.b; print -- '--- session A'; cat $OUT.a; } > $OUT; rm -f $OUT.a $OUT.b
