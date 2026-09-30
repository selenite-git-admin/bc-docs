---
uid: retire-rejected-exit-dbcp-2026-09-30
title: "DBCP — governed retire-rejected exit (bc-db migration 0029; TSK-f36519)"
description: "Adds the recorded, governed exit for a metric contract version whose certification decision-stream head is REJECT: a same-state audit_reject_retire certificate, an append-only mcf.rejected_version_retirement record citing the REJECT decision, and an archive class guard, so the parent soft-archive frees the name and identity for a corrected version. Clone-proved; not applied."
status: proposed
date: 2026-09-30
project: bc-core
domain: metrics
subdomain: metric-lifecycle
focus: retire-rejected-exit
supersedes:
superseded_by:
---

# DBCP — governed retire-rejected exit (bc-db migration 0029)

**Design:** memo barecount-devhub `artifacts/coverage-arc/LIFECYCLE-REJECT-EXIT-MEMO.md`, revision 3 (commit 86b1236c). The auditor accepted it with boundary on gen-c49698-03, a third round under operator grant `2026-09-30T05-16-06-877Z-39c87136` (text sha256 `39c87136…8a25`).

**Task:** TSK-f36519. **Author:** SES-7cd112.

**Status: NOT APPLIED.** Applying is a separate act. It needs the operator's explicit DB yes, recorded as a bc-exchange grant.

## 1. Why

- **The shape.** A version whose certification decision-stream head is `REJECT` stays `audit_pending` with `is_current = false`. Live `mcf.fn_mcv_state_transition_check` allows only `→ active` (C8) or `→ audit_blocked` (hard-closed).
- **The name stays held.** `idx_mcf_mc_mc_name_active` and `idx_mcf_mc_identity_active` are both partial on `archived_at IS NULL`, so the name and identity stay held and a corrected version cannot be authored.
- **No existing act fits** (memo §1).
- **Live instances:** four REJECTs from the Kaveri coverage windows of 2026-09-30:

| Metric | Version |
|---|---|
| supplier_billed_amount | 293045c9 |
| payable_control_balance | 0742d6db |
| non_current_asset_balance | 3b227305 |
| total_liability_balance | 5ab06357 |

## 2. What changes

**The migration:** bc-db `migrations/0029_mcf_retire_rejected_exit.sql` (`transactional: true`, `plane: bootstrap`; sha256 `8132c7ae8beb0466a822fe318f46e8a0d65e2b834a84cd8e94a2a6af8e6d2d7e`), on branch `claude/0029-retire-rejected-exit`, commit b205639a, draft PR selenite-git-admin/bc-db#97.

- **Why bc-db.** It was first drafted as bc-core `docker/redesign/64-…`. The bc-core CI freeze guard showed that `docker/redesign` is frozen (DEC-4c1396): the bc-db forward-migration spine is the only platform schema path. bc-core PR #901 is closed and superseded.
- **Why the bootstrap plane.** It changes baseline-owned objects: the certificate CHECKs, and a trigger on `mcf.metric_contract`.
- **Ownership and grants.**
  - The new table and functions are owned by `bc_schema_owner`, and the guard functions are `SECURITY DEFINER` with `search_path pg_catalog` (the `mcf.fn_mc_grain_freeze_guard` pattern).
  - `bc_platform_runtime` holds SELECT and INSERT only on the record, and PUBLIC is revoked.
  - The migration's verification block asserts all of this.
- **The reverse.** bc-db is forward-only, so the reverse is a later forward migration. Its draft is clone-proved and kept with the evidence (`0029-reverse-forward-migration-draft.sql`). It refuses once any record or `audit_reject_retire` certificate exists.

- **`mcf.certification_record` CHECKs.** `certification_record_action_code_check` and `certification_record_action_state_check` are replaced to add one tuple: `audit_reject_retire`, `audit_pending → audit_pending`. It is a same-state record, like the existing `audit_rerequest`.
  - Every existing pair is byte-identical; the clone proof compares the text.
  - The migration refuses if either CHECK differs from the text read live on 2026-09-30.
  - The existing certificate triggers are unaffected by the new code. `trg_audit_cert_finalize` acts only on audit_admit, audit_block and audit_migrate. The C7/C8 backstops act only on their own codes. The legacy-tuple freeze refuses only two direct-to-active tuples.
- **New table `mcf.rejected_version_retirement`**, append-only:

  | Column | Type and constraint |
  |---|---|
  | `rejected_version_retirement_id` | uuid PK |
  | `metric_contract_version_uid` | FK, UNIQUE |
  | `rejected_decision_uid` | FK to `metric_audit.decision` |
  | `certification_record_id` | FK, UNIQUE |
  | `rationale_text` | ≥ 40 characters |
  | `retired_by_name` | |
  | `retired_at` | |

  - 7 columns, no JSONB, ISO 11179 names.
  - Index `idx_rejected_version_retirement_rejected_decision_uid`.
  - The certificate table is not widened: it already has 25 columns against the 20-column rule.
- **New triggers** (3, `trg_rre_*`):
  - `trg_rre_record_immutable`: refuses UPDATE and DELETE on the record.
  - `trg_rre_record_insert_guard`: locks the parent (FOR UPDATE) and every child, then requires:
    - the version is `audit_pending` and not current;
    - the cited decision IS `metric_audit.fn_decision_stream_head(version)` and is a `REJECT` for this version;
    - there is no non-archived `audit_admit`;
    - the certificate is this version's `audit_reject_retire`;
    - there is no `active` or `is_current` child;
    - the parent is unarchived and no directory member is realized to it.
  - `trg_rre_archive_guard`: BEFORE UPDATE OF `archived_at` on `mcf.metric_contract`, when `archived_at` goes NULL → NOT NULL.
    - With **no live child**, every child whose stream head is a non-admitted `REJECT` needs a record whose `rejected_decision_uid` equals the **current** head, and a `REVOKE` head refuses.
    - With a **live child**, it is silent. That is the `retireActiveErroneousMetric` path (branch b′, which the auditor accepted).
- **Rows at apply:** 0 records. The verification block asserts the empty table, the 3 triggers and the new code.

## 3. What does not change

- **No version row, decision row or certificate row is modified**, before or after a retirement (Invariant III). A retirement writes one certificate, one record and the parent's `archived_at`.
- **Sibling acts keep working:**
  - abandon (a draft parent) and retire-active (a sole live version, and a mixed parent) are unaffected;
  - retire-demoted-duplicate is unaffected for twins without a decision;
  - a demoted twin with a REJECT head is refused on that path, by design (memo §3, the auditor's finding 3).
- **No package, digest or evaluation change.**

## 4. Sequencing

- **No deploy coupling at apply.** Today nothing can retire a REJECT version; after the apply nothing still can until the service slice (`retireRejectedMetric` in `mcf-cert-writer.service.ts`, plus its controller and tests) is served.
  - The only behaviour change at apply is that a parent with a REJECT-head child and no live child can no longer be archived without the record. No governed act does that today.
- **The service slice** also updates `src/__architecture__/persisted-codes.snapshot.json` (the persisted certificate codes) and is reviewed separately (engine lane).
- **After the service is served,** each retirement is an operator-granted act per metric (the metric onboarding lane, operator grant ead781aa).

## 5. Clone proof (2026-09-30, bc-db 0029)

- **Source.** Live `bc_platform_dev`, `pg_dump -Fc` read-only. It was restored **with owners and grants**, the roles recreated with their live LOGIN/NOLOGIN attributes, into a throwaway `postgres:17.11-alpine` container on 127.0.0.1 (`retire-rejected-exit/0029-clone-source.txt`: dump sha256 and sysid; the container and dump are deleted).
  - 0 restore errors; 450 versions and 1,381 certificates. `mcf.metric_contract` is owned by `bc_schema_owner`, and the served login's real privileges are present.
  - (A first proof of the bc-core draft ran on an ownerless restore. It is superseded by this one.)
- **Apply, reverse, re-apply** (`0029-apply-reverse-transcript.txt`).
  - Apply 1 is clean: 3 triggers, the record owned by `bc_schema_owner`, and the served login granted exactly INSERT and SELECT.
  - The reverse draft restores both CHECKs **byte-identical**, with no triggers left.
  - Apply 2 is clean, and a third apply is refused (fail-closed).
- **Vectors: 32 of 32 PASS** (`0029-vectors-transcript.txt`, harness `0029-vector-harness.sql`, runner `0029-run-vectors.zsh`).
  - Each vector is its own transaction, rolled back.
  - Fixture shapes not present in live data were built with `session_replication_role = replica`. Every guard under test ran with triggers on.

| Vectors | What they prove |
|---|---|
| V01, V02 × 4 | For each live shape, the name and identity are held before (a probe insert of the same `mc_name` and identity refuses); the act succeeds, and the probe then succeeds |
| V03 | A direct archive without a record is refused |
| V04 | A certificate with the wrong code is refused |
| V05 | A cited decision that is not the head is refused |
| V06 | A record of a now-stale head does not authorize the archive |
| V07 | Recording the new head succeeds |
| V08, V09 | A PASS or REVOKE head is refused at the record |
| V10 | A REVOKE head is refused at the archive |
| V11a, V11b | A fork cannot be constructed: `uq_decision_genesis` and `decision_supersedes_decision_uid_key` refuse it, so the guard's fork branch is defence in depth |
| V12 | A current version is refused |
| V13 | A non-archived admit is refused |
| V14 | A realized member is refused |
| V15, V16 | UPDATE and DELETE on the record are refused |
| **G1** | retire-active archives a MIXED parent (its live target plus the REJECTed sibling), with the sibling's version row and decisions unchanged |
| **G2** | A REJECT record on that mixed parent is refused |
| **G3** | A no-live-child archive without a current-head record is refused |
| S1 | retire-active on a sole live version is unaffected |
| S2 | A demoted twin with no decision is unaffected |
| S3 | abandon of a draft parent is unaffected |
| **L1** | The served login `bc_platform_runtime` performs the whole act (certificate, record, archive) under its real grants |
| **L2** | A direct archive by the served login is refused by the guard |
| **L3** | An edit of the record by the served login is refused ("permission denied") |

- **G4, lock validity through the archive, as the served login** (`0029-lock-proof-transcript.txt`):
  - Session A, as `bc_platform_runtime`, inserted the certificate and the record, held the transaction for 8 s, then archived and committed.
  - Concurrent session B (lock_timeout 3 s) tried to make the version live and to update the parent. **Both were refused with a lock timeout.**
  - A's archive then committed.
- **The reverse after a committed record refuses** ("retirement records exist (immutable)"), with the 3 triggers and 1 record intact.
- **bc-db local checks:** the byte-discipline rule (no CR) passes, and `tools/tests/runner.test.sh` passes. CI runs the full suite on the PR.

## 6. Apply plan (for the operator's DB yes)

1. Check that nothing is live: no `run-live-*` running, and the kit claim is absent or held by this act.
2. Back up to governed custody: a fresh read-only dump, sha256 recorded.
3. Apply through the bc-db runner (the bootstrap plane, as the operating principal). It writes the migration and its ledger event in one transaction. Capture the verbatim transcript (pre-checks, apply, verification blocks, exit code).
4. Post-checks: the 3 `trg_rre_*` triggers present, 0 records, both CHECKs carrying the new tuple, all 1,381 existing certificates still valid (the CHECK validates on add).
5. Commit the applied-byte SQL hash, the transcript and the backup reference to the exchange.
6. **Reverse** (only while no record or `audit_reject_retire` certificate exists): a later forward migration from the proven draft. It refuses afterwards; the reverse is then by governance.
