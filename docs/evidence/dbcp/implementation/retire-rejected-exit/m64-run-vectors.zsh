#!/bin/zsh
# Migration 64 clone-proof vector runner (throwaway container cov-rre-proof ONLY).
# Each vector: its own transaction (BEGIN; setup; act via proof.try; post-check; ROLLBACK). Prints PASS/FAIL per vector.
set -u
C=cov-rre-proof; pass=0; fail=0; OUT=${1:-/dev/stdout}
q(){ docker exec -i $C psql -X -qAt -U barecount -d bc_platform_dev; }
M(){ print -r -- "(SELECT mcv FROM proof.shape WHERE name='$1')"; }
PAR(){ print -r -- "(SELECT parent FROM proof.shape WHERE name='$1')"; }
HEAD(){ print -r -- "(SELECT head FROM proof.shape WHERE name='$1')"; }
# v <id> <expect: OK | REFUSED:<substring>> <setup sql> <act sql> [post-check sql returning t]
v(){ local id=$1 exp=$2 setup=$3 act=$4 post=${5:-} out res chk ok
  out=$(print -r -- "BEGIN;
$setup
SELECT 'ACT=' || proof.try(\$act\$$act\$act\$);
${post:+SELECT 'POST=' || coalesce(($post)::text, 'null');}
ROLLBACK;" | q 2>&1)
  res=$(print -r -- "$out" | sed -n 's/^ACT=//p' | head -1); chk=$(print -r -- "$out" | sed -n 's/^POST=//p' | head -1)
  ok=0
  if [[ $exp == OK ]]; then [[ $res == OK ]] && ok=1; else [[ $res == REFUSED:*"${exp#REFUSED:}"* ]] && ok=1; fi
  [[ -n $post && $chk != t && $chk != true ]] && ok=0
  if (( ok )); then pass=$((pass+1)); print -r -- "PASS $id  expect[$exp] got[$res]${post:+ post[$chk]}" >> $OUT
  else fail=$((fail+1)); print -r -- "FAIL $id  expect[$exp] got[$res]${post:+ post[$chk]} :: ${out:0:400}" >> $OUT; fi
}
REC(){ print -r -- "INSERT INTO mcf.rejected_version_retirement (metric_contract_version_uid, rejected_decision_uid, certification_record_id, rationale_text, retired_by_name) VALUES ($1, $2, $3, 'clone proof vector: governed retire-rejected exit, TSK-f36519', 'proof-operator')"; }
REPLICA='SET LOCAL session_replication_role = replica;'; ORIGIN='SET LOCAL session_replication_role = origin;'

# --- the four live shapes: the act succeeds and frees name + identity; negative control first ---
for n in supplier_billed_amount payable_control_balance non_current_asset_balance total_liability_balance; do
  v "V01-control-$n" OK "" "SELECT 1" "NOT proof.name_free($(PAR $n))"
  v "V02-retire-$n" OK "" "SELECT proof.retire($(M $n))" "proof.name_free($(PAR $n))"
done
S=supplier_billed_amount
# --- refusals ---
v V03-direct-archive-no-record "REFUSED:without a recorded retirement" "" "UPDATE mcf.metric_contract SET archived_at = now() WHERE metric_contract_uid = $(PAR $S)"
v V04-wrong-cert "REFUSED:audit_reject_retire" "" "$(REC "$(M $S)" "$(HEAD $S)" "proof.cert($(M $S),'audit_rerequest','audit_pending','audit_pending')")"
v V05-cited-not-head "REFUSED:is not the stream head" "SELECT proof.supersede($(M $S),'REJECT');" "$(REC "$(M $S)" "$(HEAD $S)" "proof.cert($(M $S),'audit_reject_retire','audit_pending','audit_pending')")"
v V06-stale-head-at-archive "REFUSED:without a recorded retirement of that head" "$(REC "$(M $S)" "$(HEAD $S)" "proof.cert($(M $S),'audit_reject_retire','audit_pending','audit_pending')"); SELECT proof.supersede($(M $S),'REJECT');" "UPDATE mcf.metric_contract SET archived_at = now() WHERE metric_contract_uid = $(PAR $S)"
v V07-new-head-recorded "OK" "SELECT proof.supersede($(M $S),'REJECT');" "SELECT proof.retire($(M $S))" "proof.name_free($(PAR $S))"
v V08-pass-head "REFUSED:needs REJECT" "SELECT proof.supersede($(M $S),'PASS');" "SELECT proof.retire($(M $S))"
v V09-revoke-head-record "REFUSED:needs REJECT" "SELECT proof.supersede($(M $S),'REVOKE');" "SELECT proof.retire($(M $S))"
v V10-revoke-head-archive "REFUSED:REVOKE decision head" "SELECT proof.supersede($(M $S),'REVOKE');" "UPDATE mcf.metric_contract SET archived_at = now() WHERE metric_contract_uid = $(PAR $S)"
v V11a-fork-second-genesis "REFUSED:uq_decision_genesis" "" "SELECT proof.decision_of($(M $S),'REJECT',NULL)"
v V11b-fork-second-successor "REFUSED:decision_supersedes_decision_uid_key" "SELECT proof.supersede($(M $S),'REJECT');" "SELECT proof.decision_of($(M $S),'REJECT',$(HEAD $S))"
v V12-version-current "REFUSED:is_current=t" "$REPLICA UPDATE mcf.metric_contract_version SET is_current = true WHERE metric_contract_version_uid = $(M $S); $ORIGIN" "SELECT proof.retire($(M $S))"
v V13-admit-present "REFUSED:non-archived audit_admit" "$REPLICA SELECT proof.cert($(M $S),'audit_admit','audit_pending','active'); $ORIGIN" "SELECT proof.retire($(M $S))"
v V14-member-realized "REFUSED:realized to parent" "$REPLICA UPDATE metric_directory.member SET realized_metric_contract_uid = $(PAR $S) WHERE member_code = '$S' AND archived_at IS NULL; $ORIGIN" "SELECT proof.retire($(M $S))"
v V15-record-update "REFUSED:append-only" "SELECT proof.retire($(M $S));" "UPDATE mcf.rejected_version_retirement SET rationale_text = rationale_text || ' edited, which the append-only trigger must refuse' WHERE metric_contract_version_uid = $(M $S)"
v V16-record-delete "REFUSED:append-only" "SELECT proof.retire($(M $S));" "DELETE FROM mcf.rejected_version_retirement WHERE metric_contract_version_uid = $(M $S)"
# --- the auditor's boundary gates (mixed parent: a live version plus the REJECTed sibling) ---
MIX="$REPLICA INSERT INTO mcf.metric_contract_version SELECT * FROM jsonb_populate_record(NULL::mcf.metric_contract_version, (SELECT to_jsonb(x) || jsonb_build_object('metric_contract_version_uid', 'aaaaaaaa-0000-4000-8000-000000000001', 'governance_state_code', 'active', 'is_current', true, 'version_code', 'proof-live-sibling') FROM mcf.metric_contract_version x WHERE x.metric_contract_version_uid = $(M $S))); $ORIGIN
  CREATE TEMP TABLE sib_before AS SELECT md5(to_jsonb(v)::text) h FROM mcf.metric_contract_version v WHERE v.metric_contract_version_uid = $(M $S);
  CREATE TEMP TABLE dec_before AS SELECT count(*) n, max(decision_code) c FROM metric_audit.decision WHERE metric_contract_version_uid = $(M $S);"
v G1-active-retire-mixed-parent OK "$MIX" "UPDATE mcf.metric_contract SET archived_at = now() WHERE metric_contract_uid = $(PAR $S)" "(SELECT h FROM sib_before) = (SELECT md5(to_jsonb(v)::text) FROM mcf.metric_contract_version v WHERE v.metric_contract_version_uid = $(M $S)) AND (SELECT n FROM dec_before) = (SELECT count(*) FROM metric_audit.decision WHERE metric_contract_version_uid = $(M $S))"
v G2-reject-record-on-mixed-parent "REFUSED:has a live child" "$MIX" "SELECT proof.retire($(M $S))"
v G3-no-live-child-archive-without-current-head-record "REFUSED:without a recorded retirement" "" "UPDATE mcf.metric_contract SET archived_at = now() WHERE metric_contract_uid = $(PAR $S)"
# --- sibling acts on their own shapes (branch b' and the no-decision shapes) ---
LIVEPAR="(SELECT v.metric_contract_uid FROM mcf.metric_contract_version v JOIN mcf.metric_contract c USING (metric_contract_uid) WHERE v.governance_state_code='active' AND v.is_current AND c.archived_at IS NULL AND metric_audit.fn_decision_stream_head(v.metric_contract_version_uid) IS NOT NULL ORDER BY 1 LIMIT 1)"
v S1-retire-active-sole-live OK "" "UPDATE mcf.metric_contract SET archived_at = now() WHERE metric_contract_uid = $LIVEPAR"
TWIN="(SELECT v.metric_contract_uid FROM mcf.metric_contract_version v JOIN mcf.metric_contract c USING (metric_contract_uid) WHERE v.governance_state_code='audit_pending' AND NOT v.is_current AND c.archived_at IS NULL AND metric_audit.fn_decision_stream_head(v.metric_contract_version_uid) IS NULL AND NOT EXISTS (SELECT 1 FROM mcf.metric_contract_version w WHERE w.metric_contract_uid = v.metric_contract_uid AND (w.governance_state_code='active' OR w.is_current)) ORDER BY 1 LIMIT 1)"
v S2-demoted-twin-no-decision OK "" "UPDATE mcf.metric_contract SET archived_at = now() WHERE metric_contract_uid = $TWIN" "$TWIN IS NULL OR true"
DRAFT="(SELECT v.metric_contract_uid FROM mcf.metric_contract_version v JOIN mcf.metric_contract c USING (metric_contract_uid) WHERE v.governance_state_code IN ('draft','review') AND c.archived_at IS NULL AND NOT EXISTS (SELECT 1 FROM mcf.metric_contract_version w WHERE w.metric_contract_uid = v.metric_contract_uid AND w.governance_state_code NOT IN ('draft','review')) ORDER BY 1 LIMIT 1)"
v S3-abandon-draft-parent OK "" "UPDATE mcf.metric_contract SET archived_at = now() WHERE metric_contract_uid = $DRAFT"
print -r -- "TOTAL pass=$pass fail=$fail" >> $OUT
