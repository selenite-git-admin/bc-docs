---
title: "D408 BF catalog admission cleanup — DBCP design"
date: 2026-05-16
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
session: SES-8714df
type: dbcp-design
status: proposed
---

# D408 BF catalog admission cleanup — DBCP design

**This document is the DBCP DESIGN ONLY. It is not a migration. No SQL file is authored, no data is mutated, no service code changes. The DBCP requires explicit operator approval before SQL is written.**

## 1. Authority and scope

- **ADR:** [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md) — *contract.business_field is the certified BF-BO catalog* (status: decided, commit `bc-docs-v3@4d8fb89`).
- **Calibrated audit:** `bc-core/scripts/audit-output/d408-bf-admission-audit-calibrated-2026-05-16T04-50-46-684Z.{md,json,per-bf.jsonl}`.
- **Audit script:** `bc-core/scripts/audit-bf-admission-d408-calibrated.mjs` (read-only, invariant-verified).
- **Scope of this DBCP:** schema additions on `contract.business_field`, sibling whitelist table, ledger action_code expansion on `contract.certification_record`, and backfill of `catalog_state_code` from audit evidence. Execution remains gated on operator approval.
- **Not in scope here:** any data mutation, any service-code change, any UI work, any tenant-DB change, any change to `contract.canonical_field` / `metric_contract` / tenant projection tables.

## 2. Foundation invariant check

Per ADR-1ce490 §"Foundation gate" and `bc-docs-v3/docs/foundation/the-invariants.md`:

- **Primary repair location: B (contract semantics)** — the BF catalog is itself a contract; its admission rule was previously undefined, and `status_code='certified'` was being inferred from import metadata rather than emitted as evidenced state (Invariant VI violation).
- **Secondary repair location: A (admission boundary)** — this DBCP introduces the explicit admission-boundary state (`catalog_state_code`) and the ledgered emission of admission events.
- **Tertiary, deferred: D (evaluation boundary / service consumers)** — service guards in `FieldMappingService`, `CanonicalWizardService`, CC onboarding, SDA projections must eventually read state-aware. **Out of scope for this DBCP**; tracked as follow-on slice in §7.

**Why this DBCP is needed.** Legacy `status_code='certified'` does not distinguish curated catalog membership from imported inventory. Without a separate `catalog_state_code`, the calibrated audit findings (T4 hard-fail 15, 4 broken-fallback ∩ CC, 259 clean demotion, 370 broader demotion) cannot be acted on without rewriting `status_code`, which would lose lifecycle semantics other services depend on.

## 3. Proposed schema changes

### 3.1 `contract.business_field` — additive columns (nullable except `catalog_state_code`)

| Column | Type | Nullable | Default | Purpose |
|---|---|---|---|---|
| `catalog_state_code` | text | NO | `'candidate_import'` | D408 admission-pipeline state (see §3.2 enum). |
| `catalog_state_reason_code` | text | YES | NULL | Structured reason for current state (see §3.3 enum). |
| `catalog_state_reason_text` | text | YES | NULL | Free-form reviewer rationale (≥40 chars when reason is an override). |
| `catalog_reviewed_at` | timestamptz | YES | NULL | When the current state was last set by a human. |
| `catalog_review_run_uid` | text | YES | NULL | UID of the audit/review run that produced the current state (e.g. `audit-2026-05-16T04-50-46-684Z` for the initial backfill). |

**`review_due_at` deliberately omitted.** Per ADR §5 and operator decision §10.5, D408 uses event-triggered re-review only. Re-review is represented by `certification_record.action_code='mark_recertify_pending'` writing `catalog_state_code='recertify_pending'` when explicitly invoked. No calendar column is added. If a future ADR genuinely requires calendar review, the column is trivially additive at that time.
| `gate_signals_json` | jsonb | YES | NULL | Snapshot of last G1–G5 machine-gate run. |
| `gate_signals_at` | timestamptz | YES | NULL | When `gate_signals_json` was last computed. |
| `gate_signals_row_hash` | text | YES | NULL | Hash of certification-relevant cols at gate-run time; mismatch on read flips state to `recertify_pending`. |
| `admission_rule_version_at_certify` | text | YES | NULL | Rule pack version under which the BF was last certified (powers ADR §5 version-bump re-review). |
| `certification_record_id` | uuid | YES | NULL | FK to `contract.certification_record.certification_record_id` for the row that produced the current state. |
| `source_origin_code` | text | YES | NULL | `oagis_import` / `sda_discovery` / `manual` / `seed` / `external_standard`. |
| `source_origin_ref` | text | YES | NULL | Artifact path or external standard id. |
| `archived_at` | timestamptz | YES | NULL | Soft delete per D162 rule 8. **Confirmed absent today.** |

### 3.2 `catalog_state_code` enum (CHECK constraint)

CHECK values:

| Value | Meaning |
|---|---|
| `candidate_import` | Imported but not yet evaluated against gates (or has not yet been graded). Default for new rows from import paths. |
| `certified_catalog` | Passed all hard gates AND received human G6 approval (or grandfathered from SDA evidence per backfill rules, §5). |
| `correction_required` | Hard-gate failure that is fixable in place (G1 too-short definition, G3 type incoherence). Not demoted — flagged for inline correction. |
| `demoted_catalog` | Explicit demotion via ledgered action; row preserved (`archived_at` set per D162 §8); excluded from certified reads. |
| `recertify_pending` | Hash mismatch or rule-version bump invalidated prior certification; usable at runtime with UI warning per ADR §5. |

`status_code` (existing column) continues to carry platform-wide lifecycle states (`draft`/`active`/`superseded`). The two axes are independent: a BF is operationally usable when `status_code='active'` AND `catalog_state_code IN ('certified_catalog','recertify_pending')`.

### 3.3 `catalog_state_reason_code` enum (CHECK constraint, nullable)

Free-form text is preserved in `catalog_state_reason_text`; the code is the structured tag. Initial enum:

| Reason code | Applicable states |
|---|---|
| `broken_fallback_definition` | `correction_required` / `demoted_catalog`. Covers BOTH the legacy `"... from OAGIS undefined"` literal AND the broader class of synthetic/template fallback definitions (per ADR §2.2). A row matching either pattern cannot be admitted to `certified_catalog` and must be corrected or demoted. |
| `definition_too_short` | `correction_required` |
| `type_incoherence` | `correction_required` |
| `insufficient_anchor` | `demoted_catalog` / `candidate_import` |
| `naming_policy_advisory` | annotation only — never a state on its own (ADR §2.1 advisory) |
| `manual_review_required` | `candidate_import` |
| `legacy_sda_certified` | `certified_catalog` (grandfathered backfill, §5) |
| `cc_mapping_active` | `certified_catalog` (grandfathered backfill, §5) |
| `foundational_whitelist` | `certified_catalog` (whitelist entry per §4 / ADR §7) |

`naming_policy_advisory` is a signal annotation, not a state. It is stored in `gate_signals_json.g2_advisories` rather than `catalog_state_reason_code`. Listed here for clarity.

### 3.4 New sibling table `contract.business_field_foundational_whitelist`

Per ADR §7. Six columns:

| Column | Type | Notes |
|---|---|---|
| `whitelist_id` | uuid PK | Default `gen_random_uuid()`; surrogate identity for the whitelist row itself |
| `field_name` | text NOT NULL UNIQUE | The BF concept name (e.g. `currency_code`); not a FK to `business_field.field_id` — see rationale below |
| `owner_sub` | text NOT NULL | Cognito sub of the named owner |
| `owner_email` | text NOT NULL | Human-readable owner identifier paired with `owner_sub` |
| `rationale_text` | text NOT NULL | Why this concept is admitted without source evidence; CHECK ≥ 40 chars |
| `created_at` | timestamptz NOT NULL | Default `now()` |

**Why `field_name` (string) and not `field_id` (FK).** Foundational whitelist entries are *concept-name based*, not tied to a particular existing `business_field` row. The whitelist satisfies the *relevance-anchor* requirement (G4) and *real-world-referent* requirement (G5) for shared dimensions; it is not a row-identity assertion. Consequences:

- A whitelist row may exist *before* the corresponding `business_field` row is admitted to the catalog. Membership advertises the intent ("this concept is foundational"); admission of a `business_field` row carrying that `name` then inherits the anchor.
- If a `business_field` row using a whitelisted concept name is later renamed or demoted, the whitelist row is unaffected; a future BF admitted under the same name is still anchored.
- The `field_name UNIQUE` constraint prevents duplicate whitelist entries for the same concept across the lifetime of the catalog. Re-promotion is by row update or by superseding the existing row.

This shape was authored in the SQL forward migration at `bc-core@513404d` (`docker/redesign/migrations/20260516-d408-dbcp-1q-a-bf-catalog-admission-state.sql`) and is reflected in this §3.4 by a deliberate update from the original DBCP design (which used `field_id PK FK`). The change was made because the original FK shape would have required a whitelist row to be deleted when its target BF was demoted — losing the concept-level intent the whitelist exists to preserve.

**Seed rows (locked per §10.2):**

| `field_name` | `owner_sub` | `owner_email` |
|---|---|---|
| `currency_code` | `8bdb9bd0-8827-4cc8-b640-2087658f1eb6` | `anant@selenite.co` |
| `language_code` | `8bdb9bd0-8827-4cc8-b640-2087658f1eb6` | `anant@selenite.co` |
| `country_code` | `8bdb9bd0-8827-4cc8-b640-2087658f1eb6` | `anant@selenite.co` |

Ownership is transferable later via row update or by superseding the existing row.

### 3.5 No destructive operations

- No `DROP COLUMN`, no `DELETE`, no `TRUNCATE`.
- Existing `status_code` values untouched.
- Existing `definition_standard` values untouched.
- Existing FK relationships untouched.

## 4. Certification ledger — reuse `contract.certification_record`

Per ADR §4, no new ledger table. The existing polymorphic ledger is reused with `primitive_type='business_field'`.

### 4.1 Action-code CHECK expansion

Current CHECK (verified 2026-05-16):
```
action_code IN ('submit_for_review','certify','return_to_author','deprecate','withdraw',
                'supersede','archive','unarchive','remediate_description','remediate_bf_semantics')
```

Proposed additions for BF catalog admission:

| New action_code | Purpose |
|---|---|
| `admit_bf_catalog` | G6 mints `certified_catalog` from `candidate_import` or `gates_passed`. |
| `demote_bf_catalog` | Human moves row to `demoted_catalog`; row preserved, `archived_at` set. |
| `mark_bf_correction_required` | Move to `correction_required`; reason in `gate_results_json`. |
| `recertify_bf_catalog` | Move from `recertify_pending` or `correction_required` back to `certified_catalog`. |
| `mark_recertify_pending` | Event-triggered (row edit, rule-version bump) move to `recertify_pending`. |

CHECK expansion is the substance of this DBCP's most invasive change. Filed as **DBCP-1q** within this design; alternatively, if operator prefers to defer, the CHECK can be dropped temporarily and re-added after the data load. **Recommendation:** expand in place — one DDL change is cleaner than drop/reload.

### 4.2 `gate_results_json` shape for BF actions

Every BF-catalog ledger row carries a snapshot in `gate_results_json`:

```json
{
  "audit_run_uid": "audit-2026-05-16T04-50-46-684Z",
  "rule_version": "v1",
  "gate_signals_row_hash": "...",
  "gates": {
    "g1": { "pass": true, "reasons": [] },
    "g2_advisories": ["naming_policy_violation"],
    "g3": { "pass": true, "reasons": [] },
    "g4": { "pass": true, "tier": "T4" },
    "g5": { "pass": true, "evidence": ["sda_certification","cc_mapping"] }
  },
  "context": {
    "alias_count": 0, "sda_evidence_count": 1, "cc_mapping_count": 3,
    "bo_required_or_bk": 1
  }
}
```

Schema is open per `jsonb`; the structure above is a convention, not a CHECK.

## 5. Initial backfill strategy

The calibrated audit's `per-bf.jsonl` is the source of truth for backfill — every BF row is already classified with tier, gate verdicts, and context counts. **The actual SQL must be generated from the JSONL by a small read-only script, not hand-written from this table.** This DBCP commits only to the mapping rules below.

### 5.1 Mapping rules (`catalog_state_code` initial value)

Read each row's gate verdicts (G1/G3/G4/G5 hard; G2 advisory) and tier from the JSONL.

| Cohort (audit-defined) | Approx count | Initial `catalog_state_code` | Initial `catalog_state_reason_code` |
|---|---:|---|---|
| **P0: broken_fallback ∩ CC mapping** | 4 | `correction_required` | `broken_fallback_definition` |
| **P1: T4 hard fails (excluding P0)** | ~11 | `correction_required` | `definition_too_short` or `type_incoherence` (per audit gate) |
| **P2: G3 type-incoherence rows (excluding P0/P1 overlap)** | up to 19 | `correction_required` | `type_incoherence` |
| **P3: T1_only ∩ G1 fail ∩ G5 structural** | 259 | `demoted_catalog` | `broken_fallback_definition` + `insufficient_anchor` |
| **P4: broken-fallback ∩ no-anchor (excluding P3)** | up to 370 | `demoted_catalog` | `broken_fallback_definition` |
| **T1_only ∩ G5 structural-only** (broader, excluding P3/P4) | 946 minus overlap | `candidate_import` | `manual_review_required` |
| **T4 hard-pass (excluding P0/P1)** | ~301 | `certified_catalog` | `cc_mapping_active` |
| **T3 hard-pass (Phase 1/2 clean)** | 1,387 | `certified_catalog` | `legacy_sda_certified` |
| **T2 hard-pass** | ~1,200 | `certified_catalog` | `legacy_sda_certified` *(if also SDA-evidenced)* or `manual_review_required` *(if only alias-anchored)* |
| **T1_req_or_bk hard-pass** | 31 | `certified_catalog` | `cc_mapping_active` (proxy — BO key/required is anchor) |
| **T0_only** | 605 | `candidate_import` | `manual_review_required` |
| **Whitelist members (post-§3.4 seed)** | 3 | `certified_catalog` | `foundational_whitelist` |
| **Everything else not classified above** | residual | `candidate_import` | `manual_review_required` |

Overlap resolution: P0 > P1 > P2 > P3 > P4 > broader buckets. Each BF receives one initial state.

### 5.2 Grandfathering policy (rationale)

T3 and T4 rows that pass all hard gates are *grandfathered* into `certified_catalog` with `reason_code='legacy_sda_certified'` or `'cc_mapping_active'`. They are not re-reviewed by a human at backfill time. This is a pragmatic concession: 1,387 + ~301 + 31 ≈ 1,719 grandfathered rows is too many to put through G6 manually before the platform can use the new state model. The audit-cycle re-review evidence (Phase 1/2 hard-fail = 13) supports the position that grandfathering is low-risk for hard-pass rows.

If operator prefers stricter "no grandfathering" semantics, the alternative is to start every row at `candidate_import` and require explicit G6 admission for every BF. Estimated review burden: 1,719 rows × ≤60 seconds = ~28 hours of human time. **Operator decision (2026-05-16): grandfather accepted — see §10.1.** Grandfathered rows remain subject to event-triggered re-review per ADR §5; this is not permanent immunity.

### 5.3 Ledger row per initial state

Each backfilled state writes one `certification_record` row with appropriate action_code. The backfill script emits these as part of the transaction so the state and its evidence land atomically.

## 6. Cleanup priority

Reproduced from ADR §8, with row counts from the calibrated audit:

| Priority | Cohort | Size | Action |
|---|---|---:|---|
| **P0** | broken-fallback definitions ∩ CC mapping | **4** | `correction_required` then case-by-case fix or demote |
| **P1** | T4 hard failures | **15** | `correction_required` (mostly G1 too-short fixes) + 4 G3 corrections |
| **P2** | G3 type-incoherence rows | **19** | `correction_required`; fix `(representation_term, data_type)` pair per ADR §2 coherence matrix |
| **P3** | Clean demotion cohort | **259** | `demoted_catalog` |
| **P4** | Broader broken-fallback ∩ no-anchor | **370** (≤) | `demoted_catalog` (or `manual_review_required` for overlap with non-P3 cases) |

**Tranche 1 → DBCP-1q-A.** P0 + P1 + P2 = ~38 row touches (exact count must be computed from `per-bf.jsonl` because cohorts overlap — e.g. some P1 rows are also P2 rows). Ships in DBCP-1q-A together with the schema additions, CHECK expansion, whitelist seed, and initial `catalog_state_code` backfill. Highest severity per row.

**Tranche 2 → DBCP-1q-B.** P3 + P4 = ~629 row touches (exact count from JSONL; P3 ⊂ P4 cohort overlap must be resolved with P3 winning per ADR §8 priority). Ships only after DBCP-1q-A is verified in production. Lower severity per row but higher volume.

The exact row sets for both DBCPs are *computed* from the calibrated audit's `per-bf.jsonl`, not hand-listed in either DBCP. The DBCPs reference the audit artifact UID and the computation logic; the row counts above are best-effort upper bounds for sizing only.

## 7. Service-guard follow-on slices (out of scope here)

Tracked as separate decisions/slices to be authored after this DBCP lands:

| Slice | Service | Change |
|---|---|---|
| GS-1 | `FieldMappingService.suggest()` | Default to `catalog_state_code='certified_catalog'`; `include_uncertified=true` opt-in with UI warning. |
| GS-2 | `CanonicalWizardService` candidate endpoint | Same default + opt-in. |
| GS-3 | CC onboarding (`cc_field_mapping` insert) | Refuse non-`certified_catalog`/`recertify_pending` BFs unless explicit operator override ledgered in `certification_record`. |
| GS-4 | SDA projections | Continue reading legacy `status_code` for backwards compat but join `catalog_state_code` for UI surfacing. |
| GS-5 | bc-admin UI | Per ADR §UI surface: `<BFStateChip />`, review-queue page, admission drawer. |

`include_uncertified=true` is platform-admin-only and warning-labeled. No tenant-side surface ever sees uncertified BFs without an explicit platform action.

## 8. Rollback and reversibility

Per ADR §6 (Invariant III compliance):

- **Forward-only correction preferred.** If P2 corrections turn out wrong, fix forward with a new `mark_bf_correction_required` ledger row, then `recertify_bf_catalog`.
- **Demotion is reversible** by a new ledgered action (re-admit), not by `DELETE` / `RESTORE`. Demoted rows remain physically present with `archived_at` set; FK references continue to resolve.
- **No silent deletes** anywhere in this DBCP or its follow-on slices.
- **No FK breakage at demotion** because rows are not removed.
- **CHECK rollback path:** if the action_code CHECK expansion (§4.1) causes problems, the DBCP can be reverted by dropping the CHECK, re-adding the original set, and the new ledger rows (with new action_codes) become unreadable — but they remain physically present in case the CHECK is re-expanded later. Backfill ledger rows would need to be re-emitted with mapped legacy codes if the new codes are permanently abandoned.

## 9. Verification plan

### 9.1 Pre-flight (read-only)

- `contract.certification_record action_code='remediate_bf_semantics'` count = **1,392** (D408 invariant).
- Total `contract.business_field` row count snapshot.
- `contract.cc_field_mapping` row count snapshot.
- `contract.business_object_field` row count snapshot.
- `contract.canonical_field` row count snapshot.
- All `metric_contract*` table counts snapshot.

### 9.2 Mid-flight (after schema changes, before backfill)

- New columns present on `business_field`; `catalog_state_code` defaults to `'candidate_import'` for any future insert.
- New table `contract.business_field_foundational_whitelist` exists with 3 seed rows.
- `certification_record_action_code_chk` expanded; existing rows still satisfy CHECK.

### 9.3 Post-backfill

- Invariant `action_code='remediate_bf_semantics'` count still = **1,392** (backfill does not modify these rows).
- Row count by `catalog_state_code`:
  - `certified_catalog`: ~1,719 (grandfathered) + 3 (whitelist) = ~1,722.
  - `correction_required`: ~38 (Tranche 1 cohort).
  - `demoted_catalog`: ~629 (Tranche 2 cohort).
  - `candidate_import`: ~605 (T0_only) + ~946 (T1_only structural-only minus overlap) + residual.
  - `recertify_pending`: 0 at backfill time.
- T4 cohort breakdown: 316 total → ~301 `certified_catalog`, ~15 `correction_required`.
- Every changed BF row has a paired `certification_record` row with appropriate action_code and `gate_results_json` snapshot.
- No row in `contract.canonical_field`, `contract.metric_contract`, or any tenant DB changed.
- bc-admin BF detail page still renders for sampled certified, demoted, and correction_required rows (UI not yet state-aware, but should not crash).

### 9.4 Out-of-bounds checks

- No tenant DB touched.
- No tenant-projection table touched (`progression.*`, `fact.*`, snapshot index).
- No metric snapshot row created or modified.
- No bc-core code change shipped in same DBCP (service guards are GS-1 through GS-5, separate slices).

## 10. Operator decisions locked (2026-05-16)

The eight open questions in the original DBCP design (filed as `bc-docs-v3@deeefac`) were resolved by the operator on 2026-05-16. This section records the locked decisions; §11 lists the remaining items that move to successor ADRs.

### 10.1. Grandfathering policy — ACCEPTED

Existing hard-pass legacy BFs become `catalog_state_code = 'certified_catalog'` during DBCP-1q-A backfill, with structured `catalog_state_reason_code` of `legacy_sda_certified` or `cc_mapping_active` (per §5.1 mapping table). Approximate cohort: 1,719 rows.

**Rationale (operator):** the calibrated predicate has already separated hard failures from hard passes; requiring manual G6 review of every hard-pass row would add ~28 hours of operator burden without improving the first cleanup tranche. **Important nuance: this is not permanent immunity.** Grandfathered rows remain subject to event-triggered re-review (row edit invalidates hash; admission-rule version bump; explicit `mark_recertify_pending`) per ADR §5.

### 10.2. Whitelist owner — LOCKED

For the three seed rows (`currency_code`, `language_code`, `country_code`):
- `owner_sub = 8bdb9bd0-8827-4cc8-b640-2087658f1eb6`
- `email = anant@selenite.co` (platform admin / current operator)

Ownership is transferable later via row update or supersession. Recorded in §3.4.

### 10.3. `certification_record.action_code` CHECK expansion — IN-PLACE

Use in-place CHECK replacement, same pattern as prior DBCP-1p. Add five action codes (per §4.1): `admit_bf_catalog`, `demote_bf_catalog`, `mark_bf_correction_required`, `recertify_bf_catalog`, `mark_recertify_pending`. **No drop/reload table rebuild.** Single DDL statement: `ALTER TABLE … DROP CONSTRAINT certification_record_action_code_chk, ADD CONSTRAINT certification_record_action_code_chk CHECK (...)`.

### 10.4. Tranche split — TWO DBCPs

| DBCP | Scope |
|---|---|
| **DBCP-1q-A** | Schema additions on `contract.business_field` (§3.1) + `catalog_state_code` CHECK (§3.2) + `catalog_state_reason_code` CHECK (§3.3) + new sibling whitelist table + 3 seed rows (§3.4) + `certification_record.action_code` CHECK expansion (§4.1, §10.3) + initial `catalog_state_code` backfill from `per-bf.jsonl` (§5) + **Tranche 1 correction cohort** application (P0 + P1 + P2 per §6). |
| **DBCP-1q-B** | Demotion cohorts only — **Tranche 2** (P3 + P4 per §6). Ships only after DBCP-1q-A is verified in production. No schema changes; only data state transitions with paired `certification_record` rows. |

Each DBCP carries its own verification per §9 and writes its own pre/post invariant snapshots.

### 10.5. Defaults for other open questions — LOCKED

- **`status_code` vs `catalog_state_code`** — `status_code` remains the platform-wide lifecycle column (`draft`/`active`/`superseded`). `catalog_state_code` is the new context-engine admission state. The two columns are independent axes and both are read by service consumers post-rollout.
- **`archived_at`** — applies to catalog demotion only for this DBCP. No row deletes anywhere. `archived_at` is set on the BF row when it transitions to `demoted_catalog` (and via D162 rule 8 semantics). No platform-wide D162 sweep in this DBCP; if desired, a separate decision can scope it.
- **`review_due_at`** — **column dropped from the schema** per ADR §5. D408 uses event-triggered re-review only. Re-review is represented by `certification_record.action_code='mark_recertify_pending'` writing `catalog_state_code='recertify_pending'` when explicitly invoked. Recorded in §3.1.
- **Successor ADRs** — listed in §11; remain out of DBCP-1q-A/B scope.

### 10.6. Fallback definitions cannot admit BFs — LOCKED (2026-05-16, post-1q-A)

**Rule:** No fallback / synthetic / template definition may pass G1 for `certified_catalog`. See ADR §2.2 for the normative text and the inadmissible-source list.

**Operational consequences:**

- **Backfill (DBCP-1q-A).** The grandfather cohort (1,651 rows → `certified_catalog`) was filtered through the calibrated audit's G1 regex set, which catches the literal `"... from OAGIS undefined"` template and the existing CCTS boilerplate patterns. **The current G1 regex does NOT yet catch the newer synthetic template `"<field> on <component> (OAGIS <noun>)"`** (introduced by a pending OAGIS onboarding patch — see ADR Open item §6). Any BF carrying that template would have passed the 2026-05-16 audit's G1 and may therefore appear in the grandfathered cohort. **This is a known coverage gap; it is not retroactively re-classified by DBCP-1q-A.** A future audit cycle with extended G1 patterns (per ADR §2.2) will surface these rows for `recertify_pending` → human review.
- **DBCP-1q-B.** Tranche 2 demotion design must use a G1 regex set that covers ADR §2.2's full synthetic-template family before authoring SQL, so the demotion cohort isn't blind to the broader pattern.
- **Importer slices.** Service-guard slice GS-3 (CC onboarding refusal of non-certified BFs) is necessary but not sufficient. A separate **importer-compliance** slice must ensure that the OAGIS onboarding service, SDA discovery, and any future standards importer do not insert rows with synthetic definitions as `status_code='certified'`. The currently-uncommitted patch at `bc-core/src/registry/oagis-onboarding.service.ts` does not yet satisfy this — it cleans the broken legacy literal but still emits a synthetic template that the auto-certify step then promotes. The fix is to skip the row, or to insert as `status_code='draft'` + `catalog_state_code='candidate_import'` + `catalog_state_reason_code='manual_review_required'`.

This decision does **not** mutate any existing data. It is the rule under which future audits, demotions, and importer fixes operate.

## 11. Successor ADRs (outside this DBCP)

All eight original open questions are resolved in §10. The items below are **non-blocking** for DBCP-1q-A and DBCP-1q-B execution — each is a successor ADR that may be filed independently. None of these gates DBCP-1q SQL authoring.

1. **Registered-abbreviation registry** — ADR §2.1 future enforcement. Until filed, `naming_policy_violation` remains advisory only. No DBCP-1q dependency.
2. **G3 domain-sanity LLM stack** — ADR §2 future gate. Adds LLM-assisted plausibility checking on `(domain, subdomain)` assignment. No DBCP-1q dependency.
3. **G4 duplicate-embedding stack** — ADR §2 future gate. Adds embedding-based semantic-overlap detection. No DBCP-1q dependency.
4. **Admission-rule versioning scheme** — ADR §5 version-bump trigger. Decides semver / monotonic int / dated tags for the `admission_rule_version_at_certify` column. The column ships in DBCP-1q-A with literal value `'v1'`; the scheme is finalised in a later ADR.

## 12. Next actions

Operator decisions locked per §10 on 2026-05-16. Sequence from here:

1. **Author DBCP-1q-A SQL** — forward migration: schema additions on `contract.business_field` per §3.1 (minus `review_due_at`), `catalog_state_code` CHECK per §3.2, `catalog_state_reason_code` CHECK per §3.3, new sibling whitelist table per §3.4 with 3 seed rows owned by `owner_sub = 8bdb9bd0-8827-4cc8-b640-2087658f1eb6`, `certification_record.action_code` CHECK expansion per §4.1. Reverse migration is column drops + CHECK restoration (rows preserved).
2. **Author DBCP-1q-A backfill script** — read-only on `per-bf.jsonl` → idempotent INSERT into the new whitelist table + UPDATE of `catalog_state_code`/`catalog_state_reason_code`/`gate_signals_json`/`certification_record_id` on `business_field` + paired `certification_record` rows per §5.3. Tranche 1 cohorts (P0+P1+P2) applied in same script via `mark_bf_correction_required` action_code per §10.4.
3. **Author DBCP-1q-A verification plan** — pre/mid/post checks per §9 with concrete SQL queries.
4. **Execute DBCP-1q-A** — dev → verify §9 → operator sign-off → staging → verify → prod.
5. **Author DBCP-1q-B SQL + backfill** after DBCP-1q-A is verified in prod. Tranche 2 cohorts (P3+P4) only, no schema changes.
6. **Execute DBCP-1q-B** — same path.
7. **After both DBCPs succeed:** file follow-on service-guard slices GS-1 through GS-5 as separate decisions (§7).
8. **Close TSK-9515d5 Phase 3** with reference to DEC-1ce490, this DBCP design, and the two DBCP execution records.

**This DBCP design is filed as `proposed`. Operator decisions §10 are locked. Authorisation to begin step 1 (DBCP-1q-A SQL authoring) is the next required operator action — no SQL is authored in advance of that go.**

---

## Appendix A — Verification commands (read-only, runnable today)

```sh
# Pre-flight: invariant
psql "$DATABASE_URL" -c "SELECT count(*) FROM contract.certification_record WHERE action_code='remediate_bf_semantics';"
# Expected: 1392

# Re-confirm calibrated audit unchanged
node bc-core/scripts/audit-bf-admission-d408-calibrated.mjs
# Expect new dated artifact; tier_venn and hard_gate_failure_counts unchanged from 2026-05-16T04:50:46.480Z baseline
```

## Appendix B — References

- ADR: [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md) — DEC-1ce490 / D408
- Audit artifact (md): `bc-core/scripts/audit-output/d408-bf-admission-audit-calibrated-2026-05-16T04-50-46-684Z.md`
- Audit artifact (json): sibling `.json`
- Audit artifact (per-bf): sibling `.per-bf.jsonl`
- Audit script: `bc-core/scripts/audit-bf-admission-d408-calibrated.mjs`
- Baseline (pre-calibration) audit: `bc-core/scripts/audit-output/d408-bf-admission-audit-2026-05-16T04-00-14-480Z.md`
- Baseline script: `bc-core/scripts/audit-bf-admission-d408.mjs`
- D162 (database rules): `bc-docs-v3/docs/adrs/ADR-1918d0.md`
- D268 (session discipline): `bc-docs-v3/docs/adrs/ADR-ebf0b4.md`
- Foundation invariants: `bc-docs-v3/docs/foundation/the-invariants.md`
