#!/bin/zsh
# Two-session race vectors for migration 0032 (gen-fe8f9d-05 finding). Throwaway container ONLY.
# usage: 0032-race.zsh <container> <db> <label>
set -u
C=$1; DB=$2; L=$3
q(){ docker exec -i $C psql -X -qAt -v ON_ERROR_STOP=1 -U barecount -d $DB; }
X=$(print -r -- "SELECT uid FROM race.ids WHERE tag='X'" | q); Y=$(print -r -- "SELECT uid FROM race.ids WHERE tag='Y'" | q)
DECL(){ print -r -- "INSERT INTO mcf.metric_output_declaration (metric_contract_version_uid, unit_type_code, decimal_places_count, rounding_mode_code, declared_by_name) VALUES ('$1', 'days', 2, 'half_up', 'race-proof')"; }
print -r -- "== [$L] R1 update-first: T2 changes X to local_currency and holds it 4s uncommitted; T1 declares X days at +1s"
( print -r -- "BEGIN; UPDATE mcf.metric_contract_version SET aggregation_currency_code = 'local_currency' WHERE metric_contract_version_uid = '$X'; SELECT pg_sleep(4); COMMIT;" | q >/dev/null 2>&1; print -r -- "   T2 finished at $(date +%T)" ) &
sleep 1
T1S=$(date +%T); T1=$(print -r -- "BEGIN; $(DECL $X); COMMIT;" | q 2>&1 | grep -E 'ERROR' | head -1); T1E=$(date +%T)
wait
print -r -- "   T1 started $T1S ended $T1E: ${T1:-COMMITTED}"
print -r -- "   R1 final: $(print -r -- "SELECT coalesce((SELECT unit_type_code FROM mcf.metric_output_declaration WHERE metric_contract_version_uid = '$X'), '(no declaration)') || ' / ' || (SELECT aggregation_currency_code FROM mcf.metric_contract_version WHERE metric_contract_version_uid = '$X')" | q)"
print -r -- "== [$L] R2 declaration-first: T1 declares Y days and holds it 4s uncommitted; T2 changes Y to local_currency at +1s"
( print -r -- "BEGIN; $(DECL $Y); SELECT pg_sleep(4); COMMIT;" | q >/dev/null 2>&1; print -r -- "   T1 finished at $(date +%T)" ) &
sleep 1
T2S=$(date +%T); T2=$(print -r -- "UPDATE mcf.metric_contract_version SET aggregation_currency_code = 'local_currency' WHERE metric_contract_version_uid = '$Y';" | q 2>&1 | grep -E 'ERROR' | head -1); T2E=$(date +%T)
wait
print -r -- "   T2 started $T2S ended $T2E: ${T2:-COMMITTED}"
print -r -- "   R2 final: $(print -r -- "SELECT coalesce((SELECT unit_type_code FROM mcf.metric_output_declaration WHERE metric_contract_version_uid = '$Y'), '(no declaration)') || ' / ' || (SELECT aggregation_currency_code FROM mcf.metric_contract_version WHERE metric_contract_version_uid = '$Y')" | q)"
print -r -- "   incoherent pairs in the database: $(print -r -- "SELECT count(*) FROM mcf.metric_output_declaration d JOIN mcf.metric_contract_version v USING (metric_contract_version_uid) WHERE (d.unit_type_code = 'currency') <> (v.aggregation_currency_code IN ('document_currency','single_currency_required','local_currency'))" | q)"
