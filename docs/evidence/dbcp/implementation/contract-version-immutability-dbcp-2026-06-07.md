---
title: "Contract-Version Immutability — DBCP (read-only proposal)"
description: Database Change Protocol PROPOSAL to enforce contract-grammar immutability-on-publish at the store — BEFORE UPDATE triggers that freeze active/superseded *_contract_version bodies, an explicit allowed-metadata-only update set, retirement of the d365 active-body mutation script, rollback, and dry-run checks. Step 1 of DEC-7b15c7/D429. Proposal only — no DDL applied, no DB mutated; apply gated on explicit operator approval.
status: draft
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: governance
focus: contract-version-immutability
---

# Contract-Version Immutability — DBCP (read-only proposal)

> **What this is.** A Database Change Protocol **proposal** for step 1 of DEC-7b15c7/D429. It proposes DDL (trigger functions + `BEFORE UPDATE` triggers) and an operational retirement. **Nothing is applied here** — no DDL run, no DB mutated, no script changed. Per the CLAUDE.md Database Change Protocol, **apply requires explicit operator approval**; this doc is the proposal + dry-run plan only.

## Authority
- **ADR:** DEC-7b15c7 / D429 §Gate step 1 (this DBCP enacts it).
- **Audit:** `foundation-contract-governance-audit-2026-06-07.md` finding **X1** (no store enforces contract-version immutability; `scripts/d365-enrich-cc-posting-date.mjs` rewrites ACTIVE canonical bodies in place).
- **Foundation:** `the-contract-grammar.md` §Versioning — "A contract version in `governance.state == 'active'` is immutable. Neither header nor body may be modified in place." (Contracts are **grammar**, not objects; cf. Invariant III for objects.)
- **DB rules:** CLAUDE.md Database Change Protocol; DEC-1918d0/D162 (triggers are guards — no new tables/columns/JSONB/counters); naming DEC-69f09e/D148. DDL SoT = `bc-core/docker/redesign/*.sql` (mirror on apply).
- **Precedent:** `concept_registry.*` already carries an immutability trigger (it blocked an in-place BCF body edit in a prior session). This DBCP extends that established pattern to the contract version tables.

## Objective
Make it **structurally impossible** to modify the **body** (`contract_json`) or version label (`version_code`) of a contract version once it is **published** (`active`) or **retired** (`superseded`). Changes must be expressed as a new version (the grammar's rule). Lifecycle metadata may still be updated.

## Scope
- **IN:** one trigger function per state-column convention + a `BEFORE UPDATE` trigger on each of the 6 `*_contract_version` tables; an explicit allowed-metadata-only column set; retirement/guarding of the `d365`-style active-body UPDATE script; rollback + dry-run plan.
- **OUT (explicit locks):** no Canonical semantic-identity work (that is step 2, a separate ADR); no data backfill or body edits; no MCF materialization; no change to the governance state machine; no new columns/tables.
- **Scope discipline (do not overload this trigger).** This guard enforces **only body/version immutability once published**. It is explicitly **NOT** a lifecycle state-machine validator: it does not decide which `governance_state_code`/`status_code` transitions are legal, does not enforce single-active-version, and **must not be extended to do so**. Lifecycle-transition legality stays in the application/service layer and is a separate concern from this DBCP.

## Verified column reality (live, 2026-06-07)
The version tables are **not uniform** — the trigger must branch on the state column:

| Version table | State column | Body | Identity / version | Lifecycle-metadata cols (mutable) |
|---|---|---|---|---|
| `source_contract_version` | `governance_state_code` | `contract_json` | `source_contract_id`, `version_code` | `success_score`, `last_validated_at`, `supersede_after` |
| `admission_contract_version` | `governance_state_code` | `contract_json` | `admission_contract_id`, `version_code` | `success_score`, `last_validated_at`, `supersede_after` |
| `observation_contract_version` | `governance_state_code` | `contract_json` | `observation_contract_id`, `version_code` | `success_score`, `last_validated_at`, `supersede_after` |
| `canonical_contract_version` | `governance_state_code` | `contract_json` | `canonical_contract_id`, `version_code` | `last_validated_at`, `supersede_after` |
| `metric_contract_version` | `governance_state_code` | `contract_json` | `metric_contract_id`, `version_code` | `success_score`, `last_validated_at`, `supersede_after` |
| `intervention_contract_version` | **`status_code`** | `contract_json` | `intervention_contract_id`, `version_code` | `change_note`, `supersede_after` |

**Inconsistency flagged** (also an audit follow-up): intervention uses `status_code`, the other five `governance_state_code`. Intervention has **0 rows** (unbuilt) — its trigger ships for symmetry but its `status_code` enum values must be confirmed at apply (dry-run DR4).

## Decisions
| # | Decision |
|---|---|
| G1-D1 | **Freeze threshold = `active` + `superseded`.** Bodies are mutable in `draft`/`review`/`approved` (authoring in progress); frozen once published. Matches the grammar's "immutability on publish." *(Option to also freeze `approved` noted in §Open items; default is active+superseded for v1.)* |
| G1-D2 | **Frozen columns:** `contract_json` (body) + `version_code`. Identity FK (`{fam}_contract_id`) is PK-anchored; included in the guard for belt-and-suspenders. |
| G1-D3 | **Allowed metadata-only updates** (NOT blocked, even when active/superseded): the state column itself (`governance_state_code`/`status_code` — forward lifecycle transitions like `active→superseded`), `success_score`, `last_validated_at`, `supersede_after`, `change_note`. These are operational/lifecycle metadata, not the contract body. |
| G1-D4 | **Enforcement is a DB trigger** (not app-only), because the violation today comes from out-of-band scripts that bypass the service layer. App-layer convention is necessary but not sufficient (X1). |
| G1-D5 | **State-machine legality stays the application's job.** The trigger enforces body/identity immutability only; it does not police which state transitions are legal. |

## 1. DDL proposal (NOT applied)
```sql
-- PROPOSAL — apply only after approval; mirror in docker/redesign + Drizzle.

-- Variant A — five families keyed on governance_state_code
CREATE OR REPLACE FUNCTION contract.assert_cv_immutable_gov()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF OLD.governance_state_code IN ('active','superseded') THEN
    IF NEW.contract_json IS DISTINCT FROM OLD.contract_json
       OR NEW.version_code IS DISTINCT FROM OLD.version_code THEN
      RAISE EXCEPTION
        'contract-version immutability (DEC-7b15c7): %.contract_json/version_code is frozen once %=''%''. Author a new version.',
        TG_TABLE_NAME, 'governance_state_code', OLD.governance_state_code
        USING ERRCODE = 'check_violation';
    END IF;
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER trg_cv_immutable BEFORE UPDATE ON contract.source_contract_version
  FOR EACH ROW EXECUTE FUNCTION contract.assert_cv_immutable_gov();
CREATE TRIGGER trg_cv_immutable BEFORE UPDATE ON contract.admission_contract_version
  FOR EACH ROW EXECUTE FUNCTION contract.assert_cv_immutable_gov();
CREATE TRIGGER trg_cv_immutable BEFORE UPDATE ON contract.observation_contract_version
  FOR EACH ROW EXECUTE FUNCTION contract.assert_cv_immutable_gov();
CREATE TRIGGER trg_cv_immutable BEFORE UPDATE ON contract.canonical_contract_version
  FOR EACH ROW EXECUTE FUNCTION contract.assert_cv_immutable_gov();
CREATE TRIGGER trg_cv_immutable BEFORE UPDATE ON contract.metric_contract_version
  FOR EACH ROW EXECUTE FUNCTION contract.assert_cv_immutable_gov();

-- Variant B — intervention keyed on status_code (enum confirmed at DR4)
CREATE OR REPLACE FUNCTION contract.assert_cv_immutable_status()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF OLD.status_code IN ('active','superseded') THEN
    IF NEW.contract_json IS DISTINCT FROM OLD.contract_json
       OR NEW.version_code IS DISTINCT FROM OLD.version_code THEN
      RAISE EXCEPTION
        'contract-version immutability (DEC-7b15c7): intervention_contract_version body/version_code is frozen once status_code=''%''. Author a new version.',
        OLD.status_code USING ERRCODE = 'check_violation';
    END IF;
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER trg_cv_immutable BEFORE UPDATE ON contract.intervention_contract_version
  FOR EACH ROW EXECUTE FUNCTION contract.assert_cv_immutable_status();
```
*Note:* `IS DISTINCT FROM` on `jsonb` compares value-equality, so a no-op rewrite of byte-identical JSON is permitted; only a real body change on a published row is blocked.

## 2. Allowed metadata-only updates (explicit)
On an `active`/`superseded` row, an UPDATE is permitted **iff** it changes only: the state column (forward transition), `success_score`, `last_validated_at`, `supersede_after`, `change_note`. Any change to `contract_json` or `version_code` is rejected. This is what lets D305 supersession (`markForSupersession` stamping `supersede_after` + flipping state) and validation-score updates continue to work untouched.

## 3. Retire/guard the out-of-band `contract_json` mutation script CLASS (d365 is representative, not isolated)
Dry-run DR2 (executed 2026-06-07) found **d365 is not a one-off** — a class of **~9 scripts** rewrites or merges `contract_json` directly on version tables, and **none filters on lifecycle state** (each keys by `contract_id` ± `version_code`). Against the live corpus (source/admission/canonical ~100% active by version state; metric 731/1022 active) every one hits `active`/`superseded` rows and would be **blocked by the trigger**. Pre-apply, **retire or guard the whole class** (move to `scripts/_retired/`, or add a refuse-to-run-on-published guard):

| Script | Target table | State filter? | Class |
|---|---|---|---|
| `scripts/d365-enrich-cc-posting-date.mjs` | canonical | selects active; UPDATE by id+ver | live enrichment (representative) |
| `scripts/enrich-ar-metric-contracts.sql` (×5) | metric | none | live enrichment |
| `scripts/finance-classify-verify.sql` (×2) | metric | `function_code` only, no state | live enrichment (merges body key) |
| `scripts/finance-secondary-bindings.js` | metric | none | live enrichment (merges body patch) |
| `scripts/fix-oc-field-mappings.mjs` | observation | none (all versions of the OC) | live enrichment |
| `scripts/seed-ac-dqc-enrichment.mjs` | admission | id + `version_code` only | live enrichment |
| `scripts/migrate-canonical-contract-json.js` | canonical | none | one-shot migration |
| `scripts/migrate-metric-contract-json.js` | metric | none | one-shot migration |
| `scripts/migrate-formulas-d315.mjs` | metric | none | one-shot migration |

All are **out-of-band** (bypass `ContractService`); **none is a runtime service path** (DR1). Their enrichment/migration intents must instead be expressed as **new versions** (for canonical, that depends on step-2 authoring). Re-running any of them after the trigger lands fails by design — which is the point.

## 4. Rollback plan
Pure-DDL, zero data risk (this DBCP changes **no rows**):
```sql
DROP TRIGGER IF EXISTS trg_cv_immutable ON contract.source_contract_version;
-- … repeat for admission/observation/canonical/metric/intervention …
DROP FUNCTION IF EXISTS contract.assert_cv_immutable_gov();
DROP FUNCTION IF EXISTS contract.assert_cv_immutable_status();
```
Dropping the triggers restores prior behavior exactly. Golden snapshot taken before apply per protocol (defensive only — no data is touched).

## 5. Dry-run checks (read-only, BEFORE apply)
| # | Check | Pass condition |
|---|---|---|
| DR1 | grep bc-core `src/` for any governed write to `contract_json` on a published row (`UPDATE *_contract_version SET contract_json`, Drizzle `.update().set({contractJson})`) | None found (audit: only `updateVersionState` touches state) → trigger blocks **no** live service path |
| DR2 | grep `scripts/` for active-body `contract_json` UPDATEs | Full list classified retire-vs-safe; d365 confirmed as the active offender |
| DR3 | count `active`+`superseded` versions per family (would-be-frozen population) | Recorded as baseline (metric 1022 incl. 778 superseded; canonical 83 archived; etc.) |
| DR4 | enumerate distinct `intervention_contract_version.status_code` values | Confirms the Variant-B `IN ('active','superseded')` condition matches its enum (0 rows today) |
| DR5 | **apply-time, in a rolled-back transaction:** UPDATE one active row's `contract_json` → expect RAISE `check_violation`; then UPDATE its `supersede_after` only → expect success; `ROLLBACK` | Block fires on body; metadata update passes; nothing persisted |
| DR6 | confirm no test/seed mutates an active body (`contract.service.transitionState.spec.ts`, seed loaders) | None — or flagged for adjustment before apply |

## 5a. Dry-run results — executed 2026-06-07 (read-only; DR1–DR4 + DR6; DR5 deferred to apply)

**DR3 — would-be-frozen population (version-level `governance_state_code`/`status_code` ∈ {active, superseded}):**

| Family | active | superseded | **frozen** | draft | review | **mutable** | total |
|---|--:|--:|--:|--:|--:|--:|--:|
| source | 30,368 | 0 | **30,368** | 0 | 0 | 0 | 30,368 |
| admission | 30,367 | 0 | **30,367** | 0 | 0 | 0 | 30,367 |
| observation | 95 | 21 | **116** | 35 | 3 | 38 | 154 |
| canonical | 83 | 0 | **83** | 0 | 0 | 0 | 83 |
| metric | 731 | 2 | **733** | 289 | 0 | 289 | 1,022 |
| intervention | 0 | 0 | **0** | 0 | 0 | 0 | 0 |
| **Total** | | | **≈61,667** | | | **327** | |

**DR4 — `intervention_contract_version.status_code`: 0 rows.** Variant-B trigger ships **dormant**; confirm its enum from the column CHECK/Drizzle before relying on the `('active','superseded')` literal (nothing to freeze today).

**DR1 — live service paths writing `contract_json` after publish: NONE (PASS).** The only `src/` write to `contract_json` is the **INSERT** at version creation (`contract-version.repository.ts:29`). The only `src/` UPDATE to a version table is **state-only** (`src/mls/gate/mls14-reevaluation.service.ts:165` → `governance_state_code='draft'`), which the trigger **allows**. → the trigger blocks **zero governed service paths**.

**DR2 — out-of-band scripts blocked: ~9 (see §3).** d365 is representative, not isolated; none filters on state; all bypass `ContractService`.

**DR6 — tests/seed:** `src/registry/readiness-ledger.service.integration.spec.ts:352` does `UPDATE contract.metric_contract_version SET contract_json=(cycle json)` → **would break under the trigger if its target row is `active`** → pre-apply fix required (§6 step 1). `contract.service.transitionState.spec.ts` uses a **mock** (no DB) → safe. Seed creation (`d225`/`d228`/`finance-co-versions`) **INSERTs** at `draft` → unaffected (BEFORE UPDATE only).

**Net:** safe for the running platform (DR1 clean; the allowed-metadata set covers `mls14` state demotion + D305 supersession `supersede_after` + validation scores). The trigger blocks the out-of-band script class (DR2, intended) and one integration spec (DR6, fix needed).

**Parent/version state desync (follow-up, NOT a blocker — DR3):** version `governance_state_code='active'` (canonical 83, metric 731) diverges from parent-level `archived_at` (canonical 0, metric 2 active). The legacy-corpus archival flipped parent `archived_at` but never flipped the version state to `superseded`. The trigger correctly keys on the **version** state (a published version stays immutable even when its parent is archived). Recorded as an audit follow-up; out of scope for this DBCP.

## 6. Apply checklist (gated — not executed here)
On explicit operator approval only, in order:
0. **Pre-apply cleanup/guard (from DR2):** retire or guard the **entire out-of-band script class** in §3 — d365 is representative, not the only offender. Verify none can run against published rows.
1. **Pre-apply test fix (from DR6):** restructure `readiness-ledger.service.integration.spec.ts` so it does not `UPDATE` an `active` metric body (use a `draft` fixture row or rework the cycle setup); re-run the suite green.
2. **Golden snapshot** (defensive — this DBCP changes no rows).
3. Add the DDL to `docker/redesign` + mirror in Drizzle.
4. Create the trigger functions + the six `BEFORE UPDATE` triggers.
5. **DR5 verification (tx, rolled back):** UPDATE one `active` row's `contract_json` → expect `RAISE check_violation`; then UPDATE only its `supersede_after` → expect success; `ROLLBACK`.
6. Report. Rollback per §4 at any step.

**Not in this checklist (scope discipline):** no lifecycle state-machine validation, no single-active-version enforcement, no fix of the parent/version state desync. Those are separate concerns; this DBCP is body/version immutability only.

## Open items (operator to confirm at approval)
- **Freeze `approved` too?** Default v1 freezes `active`+`superseded` (matches grammar). Extending to `approved` is a stricter option; recommend deferring unless authoring practice wants approved-locked.
- **Intervention `status_code` enum** (DR4) — confirm terminal/published values before relying on Variant B.
- **State-column inconsistency** (`status_code` vs `governance_state_code`) — out of scope to fix here; logged as an audit follow-up.
- **Parent `archived_at` vs version state desync** (DR3) — version `governance_state_code` stayed `active` after parent-contract archival. **Follow-up audit item, not a blocker** for this DBCP; the trigger keys on version state, which is the correct anchor.

## Scope guard
Proposal only. No DDL applied, no DB mutated, no script changed, no PR opened. Enacts DEC-7b15c7/D429 step 1; held for explicit operator approval before any apply.
