---
uid: dir004-feasibility-history-dbcp-2026-10-01
title: "DBCP — Metric Directory feasibility-result history + BCV change re-eval (bc-db migration 0033; TSK-209877)"
description: "Adds the deferred DIR-004 Phase B storage: an append-only feasibility-result history, a normalised record of the active-BCV references each result relied on, an append-only change-detected re-evaluation queue, a current-view, and one SECURITY DEFINER trigger that queues a member for re-evaluation when a referenced concept's active version changes. First guards-drops the empty legacy pre-spine feasibility table and its two dependent functions (docker/redesign/37), replacing them with the governed normalised shape. Clone-proved; not applied."
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

**0. Guarded disposal of the legacy pre-spine feasibility objects.** (Section 0 takes an ACCESS EXCLUSIVE lock on the legacy table BEFORE testing emptiness, in the same transaction, so no concurrent writer can insert between the count and the DROP and be lost — Codex gen-9bab57-01 #1.) An older `metric_directory.member_feasibility_result` exists on live from `docker/redesign/37-metric-directory-versioning.sql` (db3bb9b5, 2026-07-12, audit-accepted) and the bc-db baseline candidate (`0000_baseline.rds.sql`) — legacy schema predating DEC-4c1396 (not out-of-band), EMPTY, and a non-compliant JSONB shape (`resolved_bcv_set_json`, against D162 rule 1). Section 0 of the migration drops it **and** its two dependent legacy functions `fn_effective_feasibility(uuid)` and `fn_feasibility_head_guard()` (its own triggers `trg_feasibility_head` + `trg_member_feasibility_result_immutable` and its grants drop with the table). **Guarded:** the drop fires only if the table exists and is EMPTY — a non-empty table raises and the whole (transactional) migration aborts, so a real table can never be dropped. No other live object references the two functions (grep: only file 37 + the baseline). Shared functions (`fn_reject_mutation`, `fn_stream_lock`, `fn_require_read_committed`) and `member_version` are untouched. Operator direction to drop in 0033: 2026-10-01 (via the Chief).

Then the new objects, in schema `metric_directory`:

1. **`member_feasibility_result`** — append-only, one row per evaluation: `feasibility_result_id` (PK), `member_uid` → `metric_directory.member`, `intent_state_code` (planned|blocked), `blocker_code` (bcf_gap|bcf_value_gap|null), `blocker_reason_text`, `trigger_reason_code` (initial|bcf_active_version_change|manual), `evaluated_at`, `evaluated_by_name`. CHECKs mirror the member's intent/blocker invariant. Current state is **derived on read** (the directory's `v_member_realized` / derive-not-cache doctrine), never an in-place update.
2. **`member_feasibility_reference`** — the resolved BCV references per result, **normalised, not JSONB**, so a BCV change finds affected members by query (DB rule 1): `feasibility_reference_id` (PK), `feasibility_result_id` → result, `concept_id` → `concept_registry.business_concept`, `resolved_version_id`, `reference_role` (measure|discriminator). A **composite FK** `(concept_id, resolved_version_id)` → `concept_registry.business_concept_version (concept_id, concept_version_id)` binds the version to its concept, so a row can never pair concept A with concept B's version (Codex gen-9bab57-01 #2); MATCH SIMPLE leaves a NULL `resolved_version_id` (a gap) unchecked while `concept_id` keeps its own `business_concept` FK. This needs one **additive UNIQUE** on `business_concept_version (concept_id, concept_version_id)` as the FK target — the only change to an existing table, and unviolatable since `concept_version_id` is the PK.
3. **`member_feasibility_reeval_request`** — append-only, change-detected queue: `reeval_request_id` (PK), `member_uid` → member, `concept_id` → concept, `reason_code` (bcf_active_version_change), `detected_at`. "Pending" is derived (a request with no later result for that member), so the queue is never mutated.
4. **`v_member_feasibility_current`** — the latest result per `member_uid` (DISTINCT ON).
5. **`fn_member_feasibility_bcf_reeval()` + `trg_business_concept_feasibility_reeval`** — SECURITY DEFINER, owned by `bc_schema_owner`, `search_path pg_catalog` (the `mcf.fn_mc_grain_freeze_guard` pattern). AFTER UPDATE OF `active_version_id` ON `concept_registry.business_concept`: for the changed concept, it queues every member whose **current** feasibility referenced that concept at a different (or null) version. A `canonical_value_set` change arrives as a NEW active version (`business_concept_version` rows are immutable, Invariant III), so this one trigger covers both "active BCV changed" and "value set changed".

Grants (least-privilege): owned by `bc_schema_owner`; the served login `bc_platform_runtime` may INSERT + SELECT the result and reference tables (the app appends results) and SELECT the queue + view (it drains by reading); the definer trigger writes the queue, so the served login needs no write there; `chain_auditor_readonly` may SELECT all. No UPDATE/DELETE for the served login (append-only).

## 3. What does not change

Apart from the guarded disposal of the empty legacy feasibility objects in §2.0 and one additive UNIQUE on `concept_registry.business_concept_version (concept_id, concept_version_id)` (the FK target in §2.2; unviolatable, no data change), no existing table, column, row, grant, routine, or trigger is modified. `business_concept` is read only (the trigger reads `active_version_id`; it does not alter the BCF). `member_version` and the shared functions are untouched. No data is written by the migration. The re-evaluation **itself** — re-running `checkMemberFeasibility` and appending a new result — is bc-core application logic that drains the queue (a follow-up PR, no DDL); a read never evaluates (the Evaluation Boundary).

## 4. Sequencing

Independent of the 0028/0029 (applied) and 0031/0032 (queued) migrations — it touches disjoint objects. It applies in number order after 0032 per the live-order rule (DEC-bd6894); if the operator wants it before 0032, it carries a recorded disposition. No bc-core serve depends on it until the drainer PR lands (which merges only after 0033 is live — no code ahead of its DDL).

## 5. Clone proof

**Round 2 is GREEN on `ea9ce08`** (migration sha `21e41da7`), with both Codex gen-9bab57-01 fixes demonstrated. DB Controller, owner/grant-faithful clone-apply on a throwaway clone of dump `20261001T075638Z` (carries the legacy table; sysid ≠ live). Evidence: barecount-devhub `artifacts/db-manager/0033-proof-2026-10-01/` @ `276d0352` (`0033-green-PROOF.txt`, `0033-lock-vector.txt`, `0033-safety-planted-row-runner.err`, driver, README, MANIFEST):

- **#1 lock race (fixed):** the lock vector mirrors section 0 — T1 holds ACCESS EXCLUSIVE, counts 0, drops, commits; a concurrent T2 insert (+1s) is BLOCKED ~3s then FAILS "relation does not exist" — no row landed between the count and the drop; the table is gone after.
- **#2 composite FK (fixed):** b1 accept (a reference with a version OF its concept); b2 REFUSE (a concept paired with ANOTHER concept's version — foreign-key violation); b3 accept (a NULL-version gap, MATCH SIMPLE).
- **Apply (GREEN):** the empty legacy table + BOTH dependent functions dropped → gone; new objects 3/1/1/1 (bc_schema_owner); grants `bc_platform_runtime` INSERT+SELECT result&reference, SELECT-only queue&view; served-login vectors V1–V4 (queue writes refused); a concept `active_version_id` change queues exactly one reeval.
- **Safety:** with a planted row, 0033 refuses (runner exit 1, "exists and is NOT empty", no ledger row, table + both functions intact; transactional rollback).

The live window runs the gated driver `window-0033.sh` re-pinned to `ea9ce08` + migration `21e41da7` (runner `e35fcc2d` unchanged): barecount-devhub `claude/0028-kit-successor` @ `6b279274`, driver sha `f54911522e…`. Its empty pre-check is **advisory**; section 0's in-transaction ACCESS EXCLUSIVE re-count is authoritative (written into the driver + README).

Round-1 evidence (on `6f8a7c4`, migration `883ed0ad`, @ `e0ba3471`) is retained for history. Both phases below:

1. **Pre-state:** the three legacy objects present (table + `fn_effective_feasibility` + `fn_feasibility_head_guard`, true/true/true).
2. **Section 0:** dropped the empty legacy table **and both** dependent functions → all gone after.
3. **Create:** 3 tables / 1 view / 1 trigger fn / 1 trigger, all owned by `bc_schema_owner`; postconditions pass.
4. **Grants:** `bc_platform_runtime` INSERT+SELECT on result & reference, SELECT-only on queue & view (queue writes refused); auditor SELECT.
5. **Served-login vectors** as `bc_platform_runtime`: V1/V2 INSERT a result + references ok; V3 SELECT ok; V4 INSERT/UPDATE/DELETE on the reeval queue all **refused**.
6. **Trigger:** a concept `active_version_id` change queued exactly one reeval (before 0 → after 1).
7. **Safety:** with a planted row (valid FK), 0033 **refuses** (runner exit 1, "exists and is NOT empty", no 0033 ledger row, table + both functions intact) — the guard never drops a non-empty table; the transactional migration rolled back.

The live window will run the gated driver `window-0033.sh` (barecount-devhub `claude/0028-kit-successor` @ `877fe282`, driver sha `128f0275…`), which pins commit `6f8a7c4` + runner `e35fcc2d` + migration `883ed0ad`, refuses unless the legacy table is present and empty before any mutation, and asserts the post-state (both legacy fns gone, 3/1/1/1 objects, exact grants).

## 6. Apply plan (for the operator's DB yes)

The DB Controller runs the gated driver `window-0033.sh` (above) for the live apply; Platform schedules the window apart from any arc act and verifies read-only. Needs the operator's explicit DB yes (a bc-exchange grant) — the drop of the legacy objects makes the grant text name the drop as well as the create.

1. Check that nothing is live: no `run-live-*` running; the kit claim absent or held by this act.
2. Back up to governed custody: a fresh read-only dump, sha256 recorded.
3. Run `window-0033.sh` live (re-pinned to `ea9ce08` / runner `e35fcc2d` / migration `21e41da7`): its advisory pre-check confirms the legacy table is present and EMPTY, then the migration applies through the bc-db runner (bootstrap plane) where section 0's in-transaction ACCESS EXCLUSIVE re-count is authoritative; captures the verbatim transcript.
4. Post-checks (the driver asserts): both legacy functions gone and the legacy table gone; the five new objects present (3/1/1/1); grants as §2; 0 rows in all three new tables; the trigger present on `business_concept`.
5. Commit the applied-byte SQL hash, the transcript and the backup reference to the exchange.
6. **Reverse** (only while no `member_feasibility_result` row exists): a later forward migration from the proven draft. Once any result row exists it is refused — results are immutable evidence. (The legacy drop is not reversed by this migration; the legacy objects were empty and audit-accepted-as-superseded.)
