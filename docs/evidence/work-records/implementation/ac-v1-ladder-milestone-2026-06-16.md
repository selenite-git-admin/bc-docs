---
title: AC v1 Ladder — Milestone Closeout
description: Record of the seven PRs (#303–#309) that landed the audit-first CEE → Harness governed loop for Admission Contracts, and the first live FSCM AC proof.
authority: implementation-milestone
date: 2026-06-16
status: closed
project: bc-core
domain: chain-enrichment
subdomain: admission-contract-v1
focus: governance-loop
adrs_cited:
  - DEC-739e23
  - DEC-1fa08f
  - DEC-1efa47
---

# AC v1 Ladder — Milestone Closeout

## Summary

The seven PRs landed between 2026-06-16 close the audit-first chain enrichment loop for the Admission Contract family. Before this work the loop had three independent pieces — CAS audited (PR #301/#302), CEE planned only the SC layer, and the harness had governed-apply primitives for SC only. After this work, an operator (and only an operator) can drive the loop end-to-end for AC: CEE detects the gap, emits a v1.1 packet, the harness applies through `ContractService` via a SHA-pinned authorization, and CEE re-checks satisfaction. The loop was proven live against the B-track FSCM specimen on the same day.

This document is the change-record post for the AC v1 ladder. It is closed.

## PRs in this milestone

| PR | Title | Contribution |
|---|---|---|
| **#303** | `feat(harness): PR #1 AC v1 — packet schema + types + loader routing for ac.create_draft` | Grammar surface. Promoted `harness-packet-v1.schema.json` `action` from const `sc.create_draft` to enum `["sc.create_draft", "ac.create_draft"]`. Added the `ApplyPacketV1AcCreateDraft` discriminated-union member and packet-loader routing. AC packets validate against an `allOf/if-then` clause requiring `payload.create_version_envelope.body.source_contract_version_id` (uuid). |
| **#304** | `feat(harness): PR #2 AC v1 — adapter + classifier + apply orchestrator for ac.create_draft` | Executor surface. New sibling files `harness-ac-classifier.ts` and `harness-ac-apply.ts` mirror the SC versions but route writes through an AC-typed `GovernedAcContractCallAdapter`. `buildAcContractServiceAdapter` factory in `contract-service.adapter.ts` wires `ContractService` for AC. Five-state classifier (`READY_TO_APPLY`, `READY_TO_APPLY_PHASE_2`, `IDEMPOTENT_MATCH`, `COLLISION_HASH_MISMATCH`, `ERROR`). Idempotency grounded in deep payload equality, not just hash equality. |
| **#305** | `feat(cee): PR #3 AC v1 — CEE v0.1 admission_contract_gap_plan mode` | Planner surface. Extended `ChainEnrichmentService` with `mode=admission_contract_gap_plan` and `targetKind=admission_contract_gap_plan`. New statuses `ac_gap_satisfied`, `ac_create_proposed`, `blocked_ac_parent_sc_missing`. Probes both `contract.admission_contract` (by AC name) and `contract.source_contract` (by parent SC name). Emitted packet pins `source_contract_version_id` from the detected SC row. `CEE_PLANNER_VERSION` bumped to `cee-v0.1`. |
| **#306** | `feat(harness): PR #4 AC v1 — runtime invocation surface for CEE→Harness AC loop` | Runtime bridge. New `POST /api/harness/apply` controller (`@PlatformOnly` + `@Roles('platform_admin')`). Service `HarnessApplyFromPlanService.runFromPlan(planUid, mode, opts, actorSub)` loads the CEE plan, reconstructs the full `ApplyPacketV1AcCreateDraft` from the slim CEE-emitted packet plus an admission-v1 skeleton body, and invokes `applyAcCreateDraftPacket`. Env-gate `HARNESS_AC_APPLY=ENABLE` enforced on APPLY mode. Closes the structural gap that the orchestrator had no runtime caller. |
| **#307** | `feat(d446): PR #5 AC v1 — DB CHECK constraint alignment` | Storage substrate alignment. DDL widens 3 `mcf.chain_enrichment_plan` CHECK constraints to v0.1 supersets. Apply runner is dry-run-by-default + SHA-pinned env confirm + tenant-DB safe. Rollback SQL refuses if any v0.1 rows exist. Forward-only — new sets are strict supersets. (Companion to #305 which widened the application-layer vocabulary; this aligned the storage substrate.) |
| **#308** | `chore(gitattributes): pin *.sql to text eol=lf — fix Windows CRLF SHA drift` | Cross-platform SHA-pin discipline. After PR #307 merge, Windows `core.autocrlf=true` rewrote the SQL file's working-tree projection to CRLF, breaking the operator's SHA pin. Adds `*.sql text eol=lf` to `.gitattributes` so the file is checked out as LF on every platform. SQL content unchanged. |
| **#309** | `fix(d446): PR #6 AC v1 — CEE v0.1 SQL COMMENT syntax` | Apply-time fix. PR #307's SQL had `COMMENT ON ... IS '...' || '...' || '...'`. Postgres `COMMENT ON ... IS` requires a string literal, not an expression. The trailing COMMENT failed and rolled the whole transaction back. Fix collapses the 3 fragments into one literal. 3 ALTER TABLE statements unchanged. |

### Cumulative shape on `main`

Each PR is squash-merged with SHA-pinned merge gates. As of `main@65b5b5d`:

```
65b5b5d fix(d446):       PR #309 — CEE v0.1 SQL COMMENT syntax (HELD)
57b60c2 chore(gitattributes): pin *.sql to text eol=lf — fix Windows CRLF SHA drift
98003d3 feat(d446):      PR #307 — CEE v0.1 DB CHECK constraint alignment (HELD)
0f9fda3 feat(harness):   PR #306 — runtime invocation surface for CEE→Harness AC loop
cece153 feat(cee):       PR #305 — CEE v0.1 admission_contract_gap_plan mode
bbf0a86 feat(harness):   PR #304 — adapter + classifier + apply orchestrator for ac.create_draft
2ec5856 feat(harness):   PR #303 — packet schema + types + loader routing for ac.create_draft
```

PR #307's DDL was applied separately on 2026-06-16 07:01:46Z via the governed runner with env confirm `BCCORE_CEE_V01_APPLY_CONFIRM=I_HAVE_REVIEWED_DRY_RUN_64beb7ef`. Apply artifact: `bc-core/scripts/audit-output/d446-cee-v01-vocabulary-widen-apply-2026-06-16T07-01-46-585Z.json`. Status `APPLIED`. Three CHECK constraints widened, zero row mutations.

## Live FSCM AC proof (2026-06-16)

The five-step CEE → Harness loop fired end-to-end against the B-track FSCM specimen `sc__sap_fscm_dispute_case` v1.0.0 draft.

| Identifier | Value |
|---|---|
| **Parent SC** | `019ecaad-7d05-72c1-a902-fcaef8705e4f` (`sc__sap_fscm_dispute_case`, v1.0.0 draft, finance / accounts_receivable) |
| **Authored AC** | `019ecf42-d41f-7cb3-91fd-1603c89ce9a1` (`ac__sap_fscm_dispute_case`, finance / accounts_receivable) |
| **AC version** | `1.0.0`, governance_state_code `draft` |
| **AC body `source_contract_version_id` pin** | `019ecaad-7d05-72c1-a902-fcaef8705e4f` (parent SC contract uuid — convention from PR #303/#304/#305) |
| **Proposed CEE plan** | `afd432b4-799c-47de-a9ce-1da97776c11e` (status `ac_create_proposed`, packet kind `ac.create_draft`, hash `sha256:0f00b5fb9f15f9a07415c2722bc86648ccb8234a45f901ae8bab16b35ba9fbe6` — independently recomputed and matched) |
| **Satisfied CEE plan** | `4dccd8c4-58b2-4683-8c38-2ddc5974f3dd` (status `ac_gap_satisfied`, `detected_ac` populated, no packet emitted) |
| **Replay outcome** | `IDEMPOTENT_MATCH` on second dry-run — classifier recognized the existing AC by `(contract_name, version_code)` and skipped the write |

### Substrate delta (allowed and observed)

| Table | Pre-proof | Post-proof | Δ | Source |
|---|---|---|---|---|
| `mcf.chain_enrichment_plan` | 2 | 4 | +2 | Step 1 (ac_create_proposed) + Step 5 (ac_gap_satisfied) |
| `contract.admission_contract` | 30367 | 30368 | +1 | Step 3 `createContract` for `ac__sap_fscm_dispute_case` |
| `contract.admission_contract_version` | 30367 | 30368 | +1 | Step 3 `createVersion` v1.0.0 |

No writes outside these three tables. All AC writes went through `ContractService.createContract` + `createVersion` via the existing AC adapter — no raw DB writes.

## Scope statement — what this rung explicitly did NOT do

- **No CAS work.** CAS v1.1 is the audit family; PR #301/#302 had already closed it. The AC v1 ladder did not extend C2/C3/C4/C5/C11 walkers, did not add a C12 walker for AC presence, and did not extend the snapshot-hash projection to include AC bodies. CAS v1.2 (AC-aware) is a separate follow-up (devhub task TSK-5d27ef remains parked).
- **No M12 / M12.5 / M13 / M14 invocations.** No panel runs, no materialization, no PE-MC evaluator runs, no activations.
- **No OC, CC, or MC authoring for FSCM.** The AC body's `field_rules` carries a placeholder rule (`PL-{ac-slug}-skeleton-placeholder`). Operator-authored DQC rules + OC + CC + MC for the FSCM dispute pipeline are subsequent rungs, not part of this milestone.
- **No tenant activation.** The AC v1.0.0 is in `draft`. Transition to `active` is a separate ContractService call gated by the standard activation discipline.
- **No CAS C12 walker.** Deferred as documented in `.claude/ac-v1-fscm-planning-packet-held-2026-06-16.md` §5 (D4 — DEFER). Tracked as a follow-up.
- **No env-gate window left open.** bc-core was restarted with `HARNESS_AC_APPLY=ENABLE` for the live APPLY call only. After Step 5 the env-gate window was closed by relaunching bc-core without the env var. Verified by inspecting the launch shell env immediately before `exec node`.
- **No CEE-side apply mode.** PR #305 added the planner, PR #306 added the harness runtime bridge. CEE never invokes the harness — the two-person-rule between planner and executor (DEC-739e23) is preserved.
- **No retroactive update of legacy plans.** Existing v0 CEE plan rows (the 2 from before this milestone) remain valid under the widened CHECK constraints (strict superset).

## Authority

- ADR family: DEC-739e23 / D446 (chain enrichment engine), DEC-1fa08f / D445 (chain audit / CAS).
- Planning packet (held during design): `bc-core/.claude/ac-v1-fscm-planning-packet-held-2026-06-16.md` §1–10.
- DBCP for storage substrate widen: `bc-core/docker/redesign/migrations/d446-cee-v0.1-vocabulary-widen.sql` (apply) + `-rollback.sql` (with v0.1-row guard).
- Operator authorization trail: in-conversation per-PR HOLDING approvals and SHA-pin merge gates throughout 2026-06-16.

## Follow-ups (parked, not in scope)

- **TSK-f3104a** — AC v2 grammar rename for `source_contract_version_id` field (the field carries SC contract uuid today; rename or clarify in a future grammar pass).
- **TSK-5d27ef** — CAS v1.2 C12 walker for AC presence + parent-SC coherence; extend snapshot-hash projection to include AC bodies.
- **Operational hardening** — preflight syntax check in the apply runner (e.g. `EXPLAIN` or `PREPARE`-equivalent dry-parse) to catch DDL syntax bugs before live apply. PR #309 surfaced the gap that the dry-run script reads `pg_constraint` for pre-state + SHA over the file, but never attempts the DDL parse.

## Closing

This milestone is closed. The CEE → Harness AC loop is wired, governed, audit-traceable, and proven live on one specimen. The next architectural rung (FSCM Observation Contract / OC v1) is intentionally not started here.
