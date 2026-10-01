---
uid: dir004-feasibility-history-dbcp-2026-10-01
title: "DBCP — Metric Directory feasibility-result history + BCV change re-eval (bc-db migration 0033; TSK-209877)"
description: "Adds the deferred DIR-004 Phase B storage: an append-only feasibility-result history, a normalised record of the active-BCV references each result relied on, an append-only change-detected re-evaluation queue, a current-view, and one SECURITY DEFINER trigger that queues a member for re-evaluation when a referenced concept's active version changes. New objects only; no existing object changed; no data written. Not applied."
status: proposed
date: 2026-10-01
project: bc-core
domain: metrics
subdomain: metric-directory
focus: dir004-feasibility-history
supersedes:
superseded_by:
---

# DBCP — Metric Directory feasibility-result history (bc-db migration 0033)

**Design:** this DBCP and the migration `bc-db/migrations/0033_metric_directory_feasibility_history.sql` (branch `claude/0033-feasibility-history`, commit `765ea4c`, draft PR bc-db #101). The DIR-004 core fix landed in bc-core #460 (checkMemberFeasibility resolves the ACTIVE BCV and validates discriminator values against its `canonical_value_set`); Phase B — recording the resolved BCV set and re-evaluating on a BCV change — was explicitly deferred to this DBCP.

**Task:** TSK-209877. **Author:** SES-3e2822 (Platform Controller).

**Status: NOT APPLIED.** Applying is a separate act. It needs the operator's explicit DB yes, recorded as a bc-exchange grant.

## 1. Why

`checkMemberFeasibility` (bc-core `src/registry/metric-directory/metric-directory.service.ts:1055`) judges a directory member against the live BCF: each referenced concept must be an ACTIVE business concept, and each discriminator value must belong to the active version's `canonical_value_set`. Today that verdict is computed and returned, but nothing records **which active BCV versions the verdict relied on**, and nothing re-judges a member when a referenced BCV later changes its active version (or its value set). So a member marked `planned` can silently become stale when the governed vocabulary it depends on moves.

Phase B makes the verdict **evidence** (Invariant VI — emitted, not inferred) and **immutable history** (Invariant III — a new verdict is appended, the prior one preserved), and makes a BCV change **detectable** so the member is re-judged.

## 2. What changes

All objects are new, in schema `metric_directory`:

1. **`member_feasibility_result`** — append-only, one row per evaluation: `feasibility_result_id` (PK), `member_uid` → `metric_directory.member`, `intent_state_code` (planned|blocked), `blocker_code` (bcf_gap|bcf_value_gap|null), `blocker_reason_text`, `trigger_reason_code` (initial|bcf_active_version_change|manual), `evaluated_at`, `evaluated_by_name`. CHECKs mirror the member's intent/blocker invariant. Current state is **derived on read** (the directory's `v_member_realized` / derive-not-cache doctrine), never an in-place update.
2. **`member_feasibility_reference`** — the resolved BCV references per result, **normalised, not JSONB**, so a BCV change finds affected members by query (DB rule 1): `feasibility_reference_id` (PK), `feasibility_result_id` → result, `concept_id` → `concept_registry.business_concept`, `resolved_version_id` → `concept_registry.business_concept_version` (NULL = the concept was absent/not active at eval time, i.e. the gap), `reference_role` (measure|discriminator).
3. **`member_feasibility_reeval_request`** — append-only, change-detected queue: `reeval_request_id` (PK), `member_uid` → member, `concept_id` → concept, `reason_code` (bcf_active_version_change), `detected_at`. "Pending" is derived (a request with no later result for that member), so the queue is never mutated.
4. **`v_member_feasibility_current`** — the latest result per `member_uid` (DISTINCT ON).
5. **`fn_member_feasibility_bcf_reeval()` + `trg_business_concept_feasibility_reeval`** — SECURITY DEFINER, owned by `bc_schema_owner`, `search_path pg_catalog` (the `mcf.fn_mc_grain_freeze_guard` pattern). AFTER UPDATE OF `active_version_id` ON `concept_registry.business_concept`: for the changed concept, it queues every member whose **current** feasibility referenced that concept at a different (or null) version. A `canonical_value_set` change arrives as a NEW active version (`business_concept_version` rows are immutable, Invariant III), so this one trigger covers both "active BCV changed" and "value set changed".

Grants (least-privilege): owned by `bc_schema_owner`; the served login `bc_platform_runtime` may INSERT + SELECT the result and reference tables (the app appends results) and SELECT the queue + view (it drains by reading); the definer trigger writes the queue, so the served login needs no write there; `chain_auditor_readonly` may SELECT all. No UPDATE/DELETE for the served login (append-only).

## 3. What does not change

No existing table, column, row, grant, routine, or trigger is modified. `business_concept` / `business_concept_version` are read only (the trigger reads `active_version_id`; it does not alter the BCF). No data is written by the migration. The re-evaluation **itself** — re-running `checkMemberFeasibility` and appending a new result — is bc-core application logic that drains the queue (a follow-up PR, no DDL); a read never evaluates (the Evaluation Boundary).

## 4. Sequencing

Independent of the 0028/0029 (applied) and 0031/0032 (queued) migrations — it touches disjoint objects. It applies in number order after 0032 per the live-order rule (DEC-bd6894); if the operator wants it before 0032, it carries a recorded disposition. No bc-core serve depends on it until the drainer PR lands (which merges only after 0033 is live — no code ahead of its DDL).

## 5. Clone proof

**PENDING — the DB Controller runs the owner- and grant-faithful clone-apply proof on commit `765ea4c`, reusing the fresh read-only dump `20261001T064658Z`, and the evidence is inserted here before Codex review.** The proof must show, on a clone with `bc_schema_owner` / `bc_platform_runtime` / `chain_auditor_readonly` present:

1. Pre-state: the five objects absent; preconditions pass.
2. Apply through the bc-db runner (bootstrap plane): the five objects created; postconditions pass; exit 0.
3. Grants exactly as §2 (the served login has INSERT+SELECT on result/reference, SELECT on queue+view, and **no** write on the queue).
4. Served-login vectors as `bc_platform_runtime`: can INSERT a result + its references and SELECT the view; **cannot** INSERT/UPDATE/DELETE the reeval queue (permission denied).
5. The trigger: as `bc_platform_runtime`, update a test concept's `active_version_id` (on the clone) for a concept referenced by a seeded current result at the old version → exactly one reeval request appears for that member; a change to an unreferenced concept → none.
6. Idempotency/refusal: re-applying refuses (the pre-state guard on `member_feasibility_result` existing).

## 6. Apply plan (for the operator's DB yes)

1. Check that nothing is live: no `run-live-*` running; the kit claim absent or held by this act.
2. Back up to governed custody: a fresh read-only dump, sha256 recorded.
3. Apply through the bc-db runner (bootstrap plane), capturing the verbatim transcript (pre-checks, apply, postconditions, exit code).
4. Post-checks: the five objects present; grants as §2; 0 rows in all three tables; the trigger present on `business_concept`.
5. Commit the applied-byte SQL hash, the transcript and the backup reference to the exchange.
6. **Reverse** (only while no `member_feasibility_result` row exists): a later forward migration from the proven draft. Once any result row exists it is refused — results are immutable evidence.
