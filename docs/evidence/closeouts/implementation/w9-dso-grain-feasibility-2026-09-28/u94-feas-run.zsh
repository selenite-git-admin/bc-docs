#!/bin/zsh
# W9 U9.4 pre-authoring probe runner: a copy of the cleared U9.0 part B runner (gen-852f3a) with a new SQL pin (TSK-5dd706).
# One run: start the AWS Odoo box, run the PINNED read-only SQL in odoo-ent-db-1 over SSM, stop the box.
# The Odoo web serve (odoo-v3-lc5) is NOT started: no Odoo login, no licence use, no port forward.
#
# Launch ONLY through the pinned preflight, which binds this runner's own bytes:
#   R=u90-partB-run.zsh; [[ $(shasum -a 256 < $R | cut -c1-64) == <runner sha256> ]] && zsh -l $R u90-partB.sql <out>
#
# F1: the SQL is copied once into a private file; that copy's SHA-256 must equal SQL_PIN before the instance is
#     started AND again immediately before it is encoded; only that copy is sent.
# F2: the stop path retries, requires an observed `stopped` state, and otherwise exits 71 with an ESCALATE line
#     naming the instance, and writes a HALT file that makes every later run of this runner refuse.
set -u -o pipefail
IID=i-0944d13adbafaa542; R=ap-south-1; DB=v3_lc5; PG=odoo-ent-db-1
SQL_PIN=355430d121fdffd0992737b862c3047051be776f7ba013ca070c86bebcd78f51
HALT=$HOME/bc-stack/logs/u94-feas.HALT
SQL=${1:?sql file}; OUT=${2:?out file}
refuse() { print -u2 "refuse: $*"; exit 3; }
[[ ! -e $HALT ]] || refuse "a previous run could not confirm the box stopped: $(cat $HALT)"
[[ ! -e $OUT ]] || refuse "transcript exists: $OUT"
WORK=$(mktemp -d) || refuse "mktemp"; chmod 700 $WORK
cp -- $SQL $WORK/probe.sql || refuse "cannot copy $SQL"
sha() { shasum -a 256 < $1 | cut -c1-64; }
[[ $(sha $WORK/probe.sql) == $SQL_PIN ]] || refuse "SQL sha256 $(sha $WORK/probe.sql) != pinned $SQL_PIN"
[[ -z $(lsof -nP -iTCP:8100 -sTCP:LISTEN 2>/dev/null) ]] || refuse "something serves :8100 (Odoo already up?)"
state() { aws ec2 describe-instances --region $R --instance-ids $IID --query 'Reservations[0].Instances[0].State.Name' --output text 2>/dev/null; }
st0=$(state) || refuse "cannot read instance state"
[[ $st0 == stopped ]] || refuse "instance is $st0, expected stopped"

rc=1; started=0
stop_box() {
  (( started )) || return 0
  local i s=unknown
  for i in 1 2 3; do
    aws ec2 stop-instances --region $R --instance-ids $IID >/dev/null 2>>$OUT
    aws ec2 wait instance-stopped --region $R --instance-ids $IID 2>>$OUT
    s=$(state); [[ $s == stopped ]] && break
    print "stop attempt $i: state $s" >> $OUT; sleep 10
  done
  if [[ $s == stopped ]]; then
    print "box: stopped (observed)" | tee -a $OUT
  else
    print "ESCALATE: instance $IID NOT confirmed stopped (last state $s) after 3 attempts; stop it by hand: ~/bc-stack/odoo.sh down" | tee -a $OUT >&2
    print "$(date -u +%FT%TZ) instance $IID last state $s; transcript $OUT" > $HALT
    rc=71
  fi
}
finish() { stop_box; rm -rf $WORK; print "exit $rc" >> $OUT; exit $rc; }
trap finish EXIT
trap 'exit' INT TERM HUP

print "== W9 path A/B feasibility $(date -u +%FT%TZ) instance $IID sql sha256 $SQL_PIN" > $OUT
started=1
aws ec2 start-instances --region $R --instance-ids $IID >/dev/null && aws ec2 wait instance-running --region $R --instance-ids $IID \
  || { print "start failed" >> $OUT; exit; }
ping=
for i in {1..60}; do
  ping=$(aws ssm describe-instance-information --region $R --filters "Key=InstanceIds,Values=$IID" --query 'InstanceInformationList[0].PingStatus' --output text 2>/dev/null)
  [[ $ping == Online ]] && break; sleep 5
done
[[ $ping == Online ]] || { print "SSM agent not Online (last: $ping)" >> $OUT; exit; }
[[ $(sha $WORK/probe.sql) == $SQL_PIN ]] || { print "SQL changed after start: refusing to send" >> $OUT; exit; }
b64=$(base64 < $WORK/probe.sql | tr -d '\n')
cmd="docker start $PG >/dev/null || exit 2; ok=0; for i in \$(seq 1 30); do docker exec $PG pg_isready -q && { ok=1; break; }; sleep 2; done; [ \$ok = 1 ] || { echo 'db container not ready' >&2; exit 2; }; u=\$(docker exec $PG printenv POSTGRES_USER); echo $b64 | base64 -d | docker exec -i $PG psql -X -U \"\${u:-postgres}\" -d $DB -v ON_ERROR_STOP=1"
cid=$(aws ssm send-command --region $R --instance-ids $IID --document-name AWS-RunShellScript --comment "bc-u94-feas-readonly" \
      --parameters "$(python3 -c 'import json,sys; print(json.dumps({"commands":[sys.argv[1]]}))' "$cmd")" --query Command.CommandId --output text) \
  || { print "send-command failed" >> $OUT; exit; }
s=
for i in {1..100}; do
  s=$(aws ssm get-command-invocation --region $R --command-id $cid --instance-id $IID --query Status --output text 2>/dev/null)
  [[ $s == (Success|Failed|TimedOut|Cancelled) ]] && break; sleep 3
done
aws ssm get-command-invocation --region $R --command-id $cid --instance-id $IID --query StandardOutputContent --output text >> $OUT 2>&1
aws ssm get-command-invocation --region $R --command-id $cid --instance-id $IID --query StandardErrorContent --output text 2>&1 | sed 's/^/stderr: /' >> $OUT
print "ssm command $cid status ${s:-none}" | tee -a $OUT
[[ $s == Success ]] && rc=0
exit
