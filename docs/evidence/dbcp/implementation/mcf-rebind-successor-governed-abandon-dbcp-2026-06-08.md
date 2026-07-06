---
title: Governed abandon of a draft/review MCF rebind successor — mini-DBCP
status: locked
date: 2026-06-08
project: bc-core
domain: implementation
governs: DEC-957fb0 (D434 editorial rebind evidence) · DEC-c3e57f (D422 MCF)
kind: governed-write-path DBCP (lifecycle; DDL-assessment inside)
parent: mcf-editorial-rebind-evidence-handling-dbcp-2026-06-08.md
---

# Governed abandon of a draft/review MCF rebind successor — mini-DBCP

**Locked for implementation (Option 1). No raw `mcf.*` write.** Surfaces a gap discovered while executing the D434 Option-A repair and authorizes the smallest governed mechanism to close it.

## 1. The gap (why the D434 §5 abandon assumption is unmet)
D434 DBCP §5 (Option A) said: *"governed-abandon `9ffed384` via the existing draft/review abandon
(reject) path (sets `archived_at`; no raw DELETE/UPDATE)."* **That path does not exist.** Ground
truth (read-only, 2026-06-08):

- **MCV governance enum has no abandon state.** `mcf.metric_contract_version.governance_state_code`
  CHECK = `('draft','review','approved','active','superseded')` (`docker/redesign/04-mcf-substrate.sql:142`).
  No `rejected`/`abandoned`/`withdrawn`.
- **The MCV table has no `archived_at` column** (verified live). Only the **parent**
  `mcf.metric_contract` has `archived_at` — and the `mc_name` uniqueness index
  `idx_mcf_mc_mc_name_active` keys on `WHERE archived_at IS NULL` (parent-level).
- **The MCF writer (`mcf-cert-writer.service.ts`) is forward-only:** `submitForReview` (draft→review),
  `approveForActivation` (review→approved), `activateMetric` (→active, M14), `supersedeMetric`
  (→superseded, M15). **No abandon/reject/archive of an MCV or its parent MC.**
- The only MC-archive code in the tree is the **billing-volume-retry-unlock one-shot** (hardcoded
  UUIDs, bespoke). The `mcf-intake` `reject` is a **reservoir intake** reject, a different object.
- Substrate comment (L294): lifecycle transitions are M3-owned; *"Until M3, the writer service is the
  only path; service-side discipline holds."* The writer has no abandon.

Per CLAUDE.md (no DB row hand-edits; surface the gap; propose the smallest DBCP; never apply
unilaterally), this halted the Option-A repair until the operator locked Option 1.

## 2. Grounding (live, read-only — 2026-06-08)
- Failed successor `9ffed384-7fa4-4cd0-b75f-19b5974d11f2`: `governance_state_code='review'`,
  `is_current=false`, parent MC `e3c6ef6c-6f29-4251-a7f3-eef96101713f`.
- Predecessor `8c088f55-5cd2-41f0-a1e6-501dce0fe104`: `active`, `is_current=true`.
- `metric_supersession` rows: **0**. Active MCV under `e3c6ef6c`: **0** (no M14).
- Derived `mc_name average_revenue_per_invoice__rebind_8c088f55` is held by **exactly one** parent MC
  `e3c6ef6c` (`archived_at IS NULL`, `display_name='Average Revenue per Invoice'`).

## 3. Proposed mechanism — governed soft-archive of the parent MC (zero DDL)
**Retire the failed successor by soft-archiving its parent MC** (`metric_contract.archived_at = NOW()`
on `e3c6ef6c`) through a governed service method — never a raw UPDATE. This frees the derived `mc_name`
(the unique index is `WHERE archived_at IS NULL`), so a fresh carry-forward-aware rebind can re-mint a
new parent under the freed name. The MCV `9ffed384` row is **not** mutated — it stays `review` under the
archived parent as immutable audit (Invariant III; its cert + PE-MC REJECT rows are preserved).

**Locked implementation shape — Option 1:** add a general `abandonDraftOrReviewSuccessor(mcvUid, rationale)` surface to the MCF writer plus `POST /api/mcf/metric-contract-versions/:mcvUid/abandon`. The rebind capability is now general (not one-shot); its repair counterpart is likewise general so any future failed draft/review rebind successor has a governed cleanup. **Option 2 (bespoke hardcoded UUID one-shot) is rejected.**

**Gates (all-or-none, before the write):**
1. Target MCV exists and `governance_state_code IN ('draft','review')` (refuse `approved`/`active`/`superseded`).
2. Parent MC has **no** `active` MCV (`active_mcv_under_parent = 0`) — never archive a parent with a live version.
3. Parent MC `archived_at IS NULL` (idempotency / not already abandoned).
4. Rationale ≥ 40 chars.

**Write (single tx):** `UPDATE mcf.metric_contract SET archived_at = NOW(), updated_at = NOW() WHERE metric_contract_uid = <parent> AND archived_at IS NULL` (via the service). No MCV mutation; no DELETE; no certification record.

**Endpoint:** `POST /api/mcf/metric-contract-versions/:mcvUid/abandon` (`@Roles('mcf_publisher')`),
body `{ rationale }`.

## 4. Provenance (exact)
| Surface | Field | Value |
|---|---|---|
| parent MC `e3c6ef6c` | `archived_at` | `NOW()` (soft-archive) |
| MCV `9ffed384` | (unchanged) | stays `review`; cert + PE-MC REJECT rows preserved (audit) |

## 5. How it treats `9ffed384`
- `9ffed384` is **not** deleted or re-stated. Its parent MC is archived; the MCV + its immutable
  `metric_create` cert + the M13 PE-MC-1/5/10 REJECT rows remain as the historical record of the
  pre-D434 gap.
- "No longer eligible/current/active": it was never `active`/`is_current`; after parent archive the
  derived `mc_name` is free (rebind gate 8 passes) and read paths that filter `parent.archived_at IS NULL`
  exclude it. (The fresh rebind mints a **new** parent MC, so M13 on the successor never resolves `e3c6ef6c`.)

## 6. Tests (held PR)
- Abandon soft-archives the parent MC + frees the `mc_name`; MCV row unchanged.
- Refuses when MCV is `approved`/`active`/`superseded` (gate 1); refuses when parent has an `active` MCV
  (gate 2); idempotent on already-archived parent (gate 3); refuses short rationale (gate 4).
- Predecessor `8c088f55` untouched; `metric_supersession` unchanged (0); no M14; no MCV enum change.

## 7. Rollback
- Pre-merge: docs-only. Held PR is revertable (zero DDL).
- Post-archive: restoring `archived_at` is outside this DBCP. If an abandon was issued in error, use a separate governed follow-up decision; do not raw-unarchive.

## 8. Explicit exclusions
- No MCV `governance_state_code` enum change (M3 owns lifecycle states). No supersession. No M14
  activation. No mutation of the predecessor or of `9ffed384`'s cert/PE rows. No raw `mcf.*` UPDATE
  outside the governed service. No materialization, no fresh M12 panel.

## 9. Sequence
This mini-DBCP locked → implement as a **held PR** → merge (SHA-pinned) → invoke abandon **once** on
`9ffed384` (frees `e3c6ef6c`'s `mc_name`) → **then** re-run the carry-forward-aware ARPI rebind (D434).
M13/M14/supersession remain separate, gated steps.
