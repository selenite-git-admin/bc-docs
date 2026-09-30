#!/bin/zsh -l
# 0032 clone proof (bc-db migration 0032, renumbered from 0030 by the Chief's ruling 2026-09-30 16:00Z; ADR DEC-b1e9eb).
# A THROWAWAY clone of a FRESH read-only live dump; never live. usage: 0032-clone-proof.zsh <bcdb-0032-worktree> <N> <out>
#  0 fresh dump (roles --no-role-passwords + platform -Fc) from the live container; READ-ONLY by construction.
#  1 clone: new container of the pinned engine, NO published port, REFUSED if it reports the live system identifier.
#  2 four databases restored owner- and grant-faithfully: proof, prev_bytes (race red check), rb_fresh (rollback B), and
#    the runner tree = bc-db origin/main (e47c1c8 or later: 0029 + 0031 + the excepted-aware runner) + the 0032 files.
#  3 the window's true pre-state on each: 0029, then the 0031 window (0003, 0031, record-exception 0001/0002/0008).
#  4 0032 through the runner (staged dir holding only 0032) -> its in-transaction verification; then vectors 1-13 + L1-L7.
#  5 race vectors (0032-race.zsh): fixed bytes on proof; the PREVIOUS unfixed bytes c7da1454 (bc-db 46453b57, then
#    named 0030) on prev_bytes as the red check.
#  6 rollback A (proof: declarations exist -> refused), B (rb_fresh: apply, rollback, 0 objects, rolled_back, re-apply
#    through the runner, a direct second SQL run refused), C (no ledger variables -> refused). 7 clone + dump removed.
set -u; setopt pipefail
WT=${1:?bc-db worktree holding the 0032 files}; N=${2:?}; OUT=${3:?}; H=${0:A:h}; LIVE=bc-postgres; LIVE_SYSID=7689410286420172840
[[ ! -e $OUT ]] || { print "REFUSED: $OUT exists"; exit 3 }; mkdir -p $OUT/dump; T=$OUT/PROOF.txt
log(){ print -r -- "[$(date -u +%FT%TZ)] $*" | tee -a $T; }; fail(){ log "0032 PROOF RED: $*"; docker rm -f -v ${C:-none} >/dev/null 2>&1; rm -rf $OUT/dump; exit 1; }
M=0032_mcf_metric_output_declaration
# the runner tree: origin/main + the two 0032 files from the PR worktree
BC=$OUT/bcdb; mkdir -p $BC; git -C $WT fetch -q origin main 2>/dev/null; MAIN=$(git -C $WT rev-parse origin/main)
git -C $WT archive $MAIN | tar -x -C $BC || fail "export main"
cp $WT/migrations/$M.sql $BC/migrations/ && cp $WT/rollback/$M.rollback.sql $BC/rollback/ || fail "copy 0032 files"
git -C $WT show 46453b571932ad4ff11324deef0bb86cec396f32:migrations/0030_mcf_metric_output_declaration.sql > $OUT/prev-0030.sql || fail "previous bytes"
SHA=$(shasum -a 256 < $BC/migrations/$M.sql | cut -c1-64); RSHA=$(shasum -a 256 < $BC/rollback/$M.rollback.sql | cut -c1-64)
PSHA=$(shasum -a 256 < $OUT/prev-0030.sql | cut -c1-64); PR_HEAD=$(git -C $WT rev-parse HEAD)
log "runner tree: bc-db main $MAIN + 0032 from PR head $PR_HEAD; migration sha256 $SHA; rollback $RSHA; previous bytes $PSHA"
[[ $PSHA == c7da1454* ]] || fail "previous bytes are not c7da1454"
PIN=$(node -e "process.stdout.write(require('$BC/versions/contract.json').engine.pinned_reference)"); C=m0032c$N
docker inspect $C >/dev/null 2>&1 && fail "container $C exists"

# ---- 0 fresh read-only dump ----
docker exec $LIVE pg_dumpall -U barecount --roles-only --no-role-passwords > $OUT/dump/roles.sql || fail "roles dump"
docker exec $LIVE pg_dump -U barecount -d bc_platform_dev -Fc > $OUT/dump/platform.dump || fail "platform dump"
LV=$(print "BEGIN READ ONLY; SELECT count(*)||'/'||max(event_seq) FROM infrastructure.schema_migration_event; ROLLBACK;" | docker exec -i $LIVE psql -X -qAt -U barecount -d bc_platform_dev | grep '/')
log "fresh dump: platform.dump sha256 $(shasum -a 256 < $OUT/dump/platform.dump | cut -c1-64); live ledger rows/max seq $LV"

# ---- 1 clone ----
docker run -d --name $C -e POSTGRES_USER=barecount -e POSTGRES_PASSWORD=$(openssl rand -hex 12) $PIN >/dev/null || fail "start clone"
for i in {1..90}; do docker exec $C pg_isready -q -U barecount 2>/dev/null && (( $(docker logs $C 2>&1 | grep -c 'ready to accept connections') >= 2 )) && break; sleep 1; done
SYS=$(docker exec $C psql -X -qAt -U barecount -d postgres -c 'select system_identifier from pg_control_system()')
[[ $SYS != $LIVE_SYSID ]] || fail "the clone reports the LIVE system identifier"
log "clone $C up (no published port), sysid $SYS (live is $LIVE_SYSID)"
grep -v -E '^(CREATE|ALTER) ROLE barecount;?' $OUT/dump/roles.sql | docker exec -i $C psql -X -q -U barecount -d postgres > $OUT/roles-restore.log 2>&1
docker cp $OUT/dump/platform.dump $C:/tmp/platform.dump >/dev/null || fail "copy dump"
q(){ docker exec -i $C psql -X -qAt -v ON_ERROR_STOP=1 -U barecount -d $1; }
for db in bc_platform_dev prev_bytes rb_fresh; do
  print "CREATE DATABASE $db" | q postgres >/dev/null || fail "create $db"
  docker exec $C pg_restore -U barecount -d $db --exit-on-error /tmp/platform.dump > $OUT/restore-$db.log 2>&1 || fail "restore $db: $(tail -1 $OUT/restore-$db.log)"
done
log "restored bc_platform_dev, prev_bytes, rb_fresh; ledger $(print "SELECT count(*)||'/'||max(event_seq) FROM infrastructure.schema_migration_event" | q bc_platform_dev); versions $(print "SELECT count(*) FROM mcf.metric_contract_version" | q bc_platform_dev)"

# ---- helpers: the SAME runner command as live (staged dir holding only one migration) ----
DISP="sha256:$(printf 'm0032-clone-proof-placeholder-disposition' | shasum -a 256 | cut -c1-64)"
run(){ local db=$1; shift; node $BC/tools/runner/runner.js "$@" --psql "docker exec -i $C psql -U barecount -X -d $db"; }
stage(){ local d=$(mktemp -d); cp $1 $d/; print $d; }
apply1(){ run $1 apply --migrations $(stage $2) --principal barecount --git-ref $MAIN --review-disposition-sha256 $DISP > $OUT/r-$1-${2:t:r}.json 2> $OUT/r-$1-${2:t:r}.err || fail "$1 apply ${2:t}: $(tail -1 $OUT/r-$1-${2:t:r}.err)"; }
state(){ print "SELECT coalesce(infrastructure.fn_migration_current_state('$2'),'UNRECORDED')" | q $1; }
prewindow(){ local db=$1 m
  apply1 $db $BC/migrations/0029_mcf_retire_rejected_exit.sql
  apply1 $db $BC/migrations/0003_nontxn_ledger.sql
  apply1 $db $BC/migrations/0031_ledger_excepted_kind.sql
  for m in 0001_runner_smoke 0002_spine_roles 0008_content_release_ledger; do
    run $db record-exception --migration $BC/migrations/$m.sql --principal barecount --rationale "clone proof: the approved 0031 window disposition" --git-ref $MAIN --review-disposition-sha256 $DISP > /dev/null 2> $OUT/x-$db-$m.err || fail "$db exception $m: $(tail -1 $OUT/x-$db-$m.err)"
  done
  log "$db pre-state (the 0032 window's): 0029 $(state $db 0029_mcf_retire_rejected_exit), 0003 $(state $db 0003_nontxn_ledger), 0031 $(state $db 0031_ledger_excepted_kind), exceptions $(print "SELECT count(*) FROM infrastructure.schema_migration_event WHERE event_kind='excepted'" | q $db)"
}
for db in bc_platform_dev prev_bytes rb_fresh; do prewindow $db; done

# ---- 4 apply 0032 + vectors ----
apply1 bc_platform_dev $BC/migrations/$M.sql
log "apply 0032 through the runner: $(state bc_platform_dev $M); policy/members/declarations $(print "SELECT (SELECT count(*) FROM mcf.metric_output_declaration_policy)||'/'||(SELECT count(*) FROM mcf.metric_output_declaration_required)||'/'||(SELECT count(*) FROM mcf.metric_output_declaration)" | q bc_platform_dev); trg_mod_* $(print "SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'trg_mod_%'" | q bc_platform_dev)"
docker cp $H/0032-vectors.sql $C:/tmp/v.sql >/dev/null
docker exec $C psql -X -v ON_ERROR_STOP=1 -U barecount -d bc_platform_dev -f /tmp/v.sql > $OUT/0032-vectors-transcript.txt 2>&1 || fail "vectors: $(grep -m1 'VECTOR FAILED\|ERROR' $OUT/0032-vectors-transcript.txt)"
log "vectors: $(grep -c 'PASS ' $OUT/0032-vectors-transcript.txt) PASS lines; $(grep -o 'ALL VECTORS PASSED[^\"]*' $OUT/0032-vectors-transcript.txt | head -1)"

# ---- 5 race vectors: fixed (0032) and previous bytes (red check) ----
docker cp $H/0032-race-setup.sql $C:/tmp/rs.sql >/dev/null
docker exec $C psql -X -q -v ON_ERROR_STOP=1 -U barecount -d bc_platform_dev -f /tmp/rs.sql > /dev/null || fail "race setup (proof)"
zsh $H/0032-race.zsh $C bc_platform_dev "FIXED ${SHA:0:8} (0032)" > $OUT/0032-race-transcript.txt 2>&1
docker cp $OUT/prev-0030.sql $C:/tmp/prev.sql >/dev/null
docker exec $C psql -X -q -v ON_ERROR_STOP=1 -1 -U barecount -d prev_bytes -f /tmp/prev.sql > $OUT/prev-apply.log 2>&1 || fail "previous bytes apply: $(tail -1 $OUT/prev-apply.log)"
docker exec $C psql -X -q -v ON_ERROR_STOP=1 -U barecount -d prev_bytes -f /tmp/rs.sql > /dev/null || fail "race setup (prev)"
zsh $H/0032-race.zsh $C prev_bytes "PREVIOUS ${PSHA:0:8} (red check; then named 0030)" >> $OUT/0032-race-transcript.txt 2>&1
FX=$(grep -A99 'FIXED' $OUT/0032-race-transcript.txt | grep -m1 'incoherent pairs' | grep -oE '[0-9]+$'); PV=$(grep -A99 'PREVIOUS' $OUT/0032-race-transcript.txt | grep -m1 'incoherent pairs' | grep -oE '[0-9]+$')
log "race: fixed bytes incoherent pairs $FX (both orders refused: $(grep -A8 'FIXED' $OUT/0032-race-transcript.txt | grep -c 'ERROR')); previous bytes incoherent pairs $PV (red check)"
[[ $FX == 0 && $(grep -A8 'FIXED' $OUT/0032-race-transcript.txt | grep -c 'ERROR') == 2 && $PV -ge 1 ]] || fail "race vectors"

# ---- 6 rollback A / B / C ----
docker cp $BC/rollback/$M.rollback.sql $C:/tmp/rb.sql >/dev/null
docker cp $BC/migrations/$M.sql $C:/tmp/m.sql >/dev/null
rb(){ docker exec $C psql -X -q -v ON_ERROR_STOP=1 -1 -U barecount -d $1 ${@:2} -f /tmp/rb.sql; }
{ print "== A. rollback on the proof database (declarations exist): must refuse"
  rb bc_platform_dev -v m0032_git_ref=$MAIN -v m0032_disposition=${DISP#sha256:} 2>&1 | grep -o 'ERROR: .*'
  print "== B. rb_fresh: apply (runner) -> rollback -> objects gone + ledger rolled_back -> re-apply (runner) -> direct second run refused"
  apply1 rb_fresh $BC/migrations/$M.sql; print "APPLY: $(state rb_fresh $M)"
  rb rb_fresh -v m0032_git_ref=$MAIN -v m0032_disposition=${DISP#sha256:} > /dev/null 2>&1 && print "ROLLBACK_OK" || print "ROLLBACK_FAILED"
  print "objects remaining: $(print "SELECT count(*) FROM pg_class WHERE relname LIKE 'metric_output_declaration%'" | q rb_fresh) tables, $(print "SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'trg_mod_%'" | q rb_fresh) triggers, $(print "SELECT count(*) FROM pg_proc WHERE proname LIKE 'fn_mod_%'" | q rb_fresh) functions; ledger: $(state rb_fresh $M)"
  apply1 rb_fresh $BC/migrations/$M.sql; print "RE-APPLY: $(state rb_fresh $M)"
  docker exec $C psql -X -q -v ON_ERROR_STOP=1 -1 -U barecount -d rb_fresh -f /tmp/m.sql 2>&1 | grep -o 'ERROR: .*'
  print "== C. rollback without the ledger variables: must refuse"
  rb rb_fresh 2>&1 | grep -o 'ERROR: .*'
} > $OUT/0032-rollback-transcript.txt 2>&1
log "rollback: $(tr '\n' ' ' < $OUT/0032-rollback-transcript.txt | cut -c1-600)"
grep -q 'output declarations exist' $OUT/0032-rollback-transcript.txt && grep -q 'ROLLBACK_OK' $OUT/0032-rollback-transcript.txt \
  && grep -q 'objects remaining: 0 tables, 0 triggers, 0 functions; ledger: rolled_back' $OUT/0032-rollback-transcript.txt \
  && grep -q 'RE-APPLY: applied' $OUT/0032-rollback-transcript.txt && grep -q '0032 refused: the output-declaration objects already' $OUT/0032-rollback-transcript.txt \
  && grep -q 'm0032_git_ref is not set' $OUT/0032-rollback-transcript.txt || fail "rollback A/B/C"

# ---- 7 cleanup ----
docker rm -f -v $C >/dev/null; rm -rf $OUT/dump $OUT/bcdb; log "clone, dump and runner tree removed (hashes recorded above)"
log "0032 PROOF GREEN: fresh read-only live dump restored owner/grant-faithfully; the window's pre-state (0029, 0003, 0031, three exceptions) through the runner; 0032 applied through the runner with its in-transaction verification; vectors 1-13 + L1-L7 passed; race vectors refused in both orders with 0 incoherent pairs (previous bytes c7da1454: >=1, red check); rollback A refused, B round trip exact, C refused; clone removed"
