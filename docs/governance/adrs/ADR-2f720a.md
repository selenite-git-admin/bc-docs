---
uid: DEC-2f720a
title: "Metric classification authority: the Metric Directory family governs a directory-linked metric's function/subfunction; the MCV classification is its governed projection"
description: "Directory family = classification authority for directory-linked MCVs; P1-P4 write-gates and net; active-only governed reclassification act; extends DEC-31c212 + DEC-b5c7ff."
status: decided
date: 2026-11-11T04:05:50.413Z
project: bc-core
domain: metrics
subdomain: metric/mcf-classification
focus: governance
related: [DEC-31c212, DEC-b5c7ff, DEC-79b62f, DEC-c48b0f]
---

# Metric classification authority: the Metric Directory family governs a directory-linked metric's function/subfunction; the MCV classification is its governed projection

**Extends** DEC-31c212 (master vocabulary; the panel classifies) and DEC-b5c7ff (the Metric Directory as the value-organizing authority). It supersedes neither. No errata: no existing ADR text is wrong. The gap is a missing precedence rule, which is a decision.

Authored by the Architect (SES-ba2e87) from the Metric-lane design memo (barecount-devhub `artifacts/metric-classification/DESIGN-mcv-subfunction-misclassification-root-fix-2026-11-11.md`, DLV-b779fa) and the Architect co-verdict (`artifacts/metric-classification/ARCHITECT-COVERDICT-mcv-classification-authority-2026-11-11.md`).

**Lane:** a metric-lifecycle act. The verdict belongs to the Chief and the Architect, and never to Codex (grant ead781aa). **Ratified to decided** by the operator under recorded grant `2026-11-11T04-53-39-946Z-49bd39f3` (bc-exchange #407).

## Context

An MCV carries `function_code` / `subfunction_code`: master-valid, with an FK to `master.master_subfunction` (DEC-31c212). When a Metric Directory member realizes the metric, the same placement also lives in the member's family: `metric_directory.family` / `family_version` `(function_slug, subfunction_slug)` (DEC-b5c7ff). That gives two surfaces for one value and no declared precedence, which breaks DB rule 4 (one source of truth per value).

**What it produced** (live read-only, 2026-11-11):
- **11 directory-realized MCVs disagree with their family.** All are `finance/tax` against `finance/accounts_receivable` or `finance/accounts_payable`: 4 `active` and current, 7 `audit_pending`.
- **6 corrective-draft successors copied the same `finance/tax`** (`__tacorr_*`): 1 active and current, 4 `approved`, 1 `audit_pending`. Members still point at the predecessor MC, so these successors are invisible to a directory join.

**Root cause:**
- Hand-authored `operator_direct` intake envelopes arrived pre-filled with `finance/tax`, a template carry-over from `invoiced_tax_amount`.
- The Maker anchored on that value, and the Checker's divergence check is soft.
- Materialization checks only that the pair exists in master.
- Directory realization never compares the family with the MCV.
- Directory-generated intake is correct by construction: `assembleMakerEnvelope` stamps the family slugs.

**Verified at source** (bc-core freeze-1044 @ e8b1a15a; live `bc_platform_dev`):
- **Not sealed.** Classification is outside `identity_tuple_hash`, `package_signature_hash`, the MC-envelope duplicate fingerprint (which excludes it explicitly), the package snapshot, the closure manifest, the demo pin and the chain-status fingerprint.
- **Not frozen.** The C5 freeze trigger does not lock it.
- **Locked only at approved and superseded.** `fn_mcv_descriptive_immutability_check` refuses non-state mutation only at `approved` / `superseded`.
- **The revision row fires only from active.** `fn_mcv_revision_emit` writes a `function_code_change` row only when `OLD.governance_state_code = 'active'`. It stamps `revised_by_name = current_user` and leaves `rationale_text` NULL.
- **Grants exist.** `bc_platform_runtime` holds column UPDATE on both columns and INSERT on `mcf.metric_contract_revision`.

## Decision

### D1. Authority (the declaration)

**For a directory-linked metric, the classification authority is the Metric Directory family placement `(function_slug, subfunction_slug)`.**
- A metric is directory-linked when a non-archived `metric_directory.member` realizes its MC, or realizes the MC its corrective lineage descends from.
- The placement is resolved through the member's current `member_version.family_version_uid` → `family_version`. For a member that has no `member_version` yet, it is resolved from the `family` row.
- The two must agree (on 2026-11-11 they agree for every versioned realized member). A disagreement is a directory defect that P4 surfaces, and it is never resolved by choosing one side.
- **The MCV columns are the governed projection of that placement.** They are stored because un-membered metrics need them and because they are the version-time record. But they are never an independent judgement for a directory-linked metric.

For a metric with **no** directory member, DEC-31c212 §4 stands: the panel classifies into master, with the independence and Checker-echo rules of P1 and P3.

A change of placement for a directory-linked metric is a **directory act**: a member moves between families, or a family is re-placed. It is never an MCV-only override. The MCV projection then follows through D3.

### D2. Classification is mutable descriptive metadata

This confirms and sharpens DEC-31c212 §5:
- `function_code` / `subfunction_code` are not identity, not package-bearing and not sealed.
- Correcting them needs **no successor MCV** and moves no hash, snapshot, pin, certification or chain epoch.
- At `approved` and `superseded` they are locked by the general descriptive-immutability guard. An approved MCV is therefore corrected when it reaches `active`, or (if it is superseded first) its successor is.

### D3. The governed reclassification act (the only correction path)

**`McfMcvReclassificationService.reclassify`** (bc-core, platform-admin), one MCV per call.

**Input:**
- `metricContractVersionUid`, `targetFunctionCode`, `targetSubfunctionCode`
- `rationaleText` (≥ 40 characters)
- `authorityRef`: the recorded operator `grant_id` and the grant's `text_sha256`
- `expectedPackageSignatureHash`
- `dryRun`

**Preconditions** (the act refuses by name and writes nothing):
1. `mcv_not_active`: the MCV must be `active` and `is_current`.
2. `target_not_master_valid`: the target pair must exist and be active in `master.master_subfunction`.
3. `target_disagrees_with_directory_family`: if the metric is directory-linked (D1), the target must equal the resolved family placement.
4. `no_op`: the current pair must differ from the target.
5. `authority_ref_missing`: `authorityRef` must be present.

**Write:**
- `SELECT … FOR UPDATE` on the MCV.
- One `UPDATE` of `function_code` and `subfunction_code` only.

**Post-write re-read** in the same transaction, fail-closed, rolling back on any deviation:
- (i) The parent MC's `package_signature_hash` **and** `identity_tuple_hash` are byte-equal to their pre-write values. The pre-write value of the first must equal `expectedPackageSignatureHash`.
- (ii) **Exactly one** new `mcf.metric_contract_revision` row exists, with `revision_kind_code = 'function_code_change'` and `changed_fields_json` equal to the expected from/to.
- (iii) `governance_state_code` and `is_current` are unchanged.
- (iv) No other MCV column changed.

**Result:** `revision_uid`, the from/to pairs, both hashes and the `authorityRef`. The act record (the DevHub change record bound to the grant) cites the `revision_uid`, so the revision row and its authority are linked by an explicit reference rather than inferred from timestamps (Invariants IV and VI).

**Attribution gap.** The trigger stamps `revised_by_name = bc_platform_runtime` and NULL `rationale_text`; the runtime cannot UPDATE revision rows, and an extra self-inserted row would break (ii). The emitted row therefore carries *what* and *when*; *who* and *why* live in the grant plus the act record cross-referencing `revision_uid`. That is acceptable for the 4 active corrections. Before the worklist batch (D5), a bc-db forward migration should let `fn_mcv_revision_emit` stamp `rationale_text` and `revised_by_name` from transaction-local settings, with the service refusing when they are unset. That migration is DDL, so it needs an operator DB-yes.

**Never:** a hand `UPDATE`, a batch of more than one MCV per call, a certification or state change, or any correction at `audit_pending` / `audit_blocked` (no revision row is emitted there, so the change would be unevidenced).

**Sequence:** one then many. Prove on `customer_invoice_volume` (MCV 7285ce98) and verify independently, then the other 3 active MCVs, each under a recorded grant that names the MCV and the target pair.

### D4. Write-gates (rules before judgement)

Every rule is enforced where the value is written.

- **P1. Every MCV-writing path resolves classification from the directory.** This covers materialization (`resolveClassification`), the MCV rebind, the corrective-draft writers (`__tacorr`, `__ccycorr`, unit corrective) and any future writer, through **one shared resolver**.
  - **Directory-linked (D1):** write the family placement. If the envelope or predecessor carries a pair that disagrees, refuse with `classification_family_mismatch` before any write. Never silently prefer either value.
  - **Un-membered:** keep the master-valid check. If the Checker's independent pair is absent or differs from the Maker's, write `not_defined/not_defined` and add a worklist row, instead of accepting the Maker's anchored pick.
  - **Corrective successors** inherit through lineage (D1). Copying a predecessor's pair is permitted only when it equals the family placement.
- **P2. Directory realization refuses a mismatch.**
  - `assertRealizationInTx` refuses, as `realization_classification_mismatch`, to realize or re-point a member onto an MC whose current MCV pair differs from the family placement.
  - The operator runs D3 first (one act, one effect). Realization never reclassifies as a hidden side effect.
  - The same refusal applies when a member is re-pointed to a corrective successor.
- **P3. Panel prompts** (a logged prompt revision; the roster and models are unchanged, so this is not a calibration change):
  - **The Maker** classifies from grain and measure meaning. Any pre-filled `function_slug` / `subfunction_slug` is a hint to confirm or replace independently, never to echo.
  - **The Checker's** `independent_proposal.function_slug` / `subfunction_slug` echo is **required**. The parser flags its absence, which feeds P1.
  - A divergence stays non-REJECT, because a descriptive field must not block authoring. Its deterministic consequence is P1.
- **P4. Net, not fix.** A read-only diagnostic, `classification_family_aligned`, on the directory lens / readiness projection. It lists:
  - every MCV whose pair differs from its D1 placement;
  - every corrective successor whose lineage member points at a predecessor;
  - every realized member without a `member_version`.

  Reads never trigger evaluation.

### D5. Disposition of the existing extent

- **The 4 active and current MCVs:** corrected through D3, one at a time, under grants.
- **The 7 audit_pending predecessors and the 5 non-active successors** (4 approved, 1 audit_pending): placed on the **governed reclassification worklist**. This is the "governed re-assignment worklist" that DEC-31c212 named as a follow-up and that was never built. Each is corrected through D3 when it becomes active and current. Approved successors are locked until then (D2).
- **The 1 active and current successor** (`invoiced_tax_amount__tacorr_6f5eff75`, MCV cafeb767): **correct first, then re-point.**
  - It is directory-linked *now* under D1, through its corrective lineage: the member realizes the predecessor MC 6f5eff75. So D3 precondition 3 already binds, with its target resolved through that lineage member's family: `finance/accounts_receivable`.
  - **Step 1:** D3 reclassifies cafeb767 to `finance/accounts_receivable` under a recorded grant.
  - **Step 2:** the realization-gap directory act re-points the member onto the successor MC. P2 then accepts it, because the pairs already agree.
  - No step needs a gate bypass or a transiently wrong realization.
  - The general rule for every corrective successor: a lineage-linked successor's classification is corrected through D3 (once it is active) **before** any member is re-pointed onto it. P2 enforces that order.
- **Placement ruling (G6):**
  - `invoiced_tax_amount` stays in `finance/accounts_receivable / ar_sales_adjustments`.
  - `payables_invoiced_tax_amount` stays in `finance/accounts_payable / ap_adjustments`.
  - The principle: **a tax amount measured on a commercial document's grain, as part of that document's gross decomposition (net + tax − discount), belongs to the document's subfunction.** A tax metric belongs in `finance/tax` when it is grained on tax lines, tax codes, jurisdictions or returns and answers liability, recoverability or compliance (the `input_tax_recovery`, `tax_liability_and_flows` and `tax_filing_compliance` families).
  - The directory does not move; the MCVs move.
  - An output-tax-liability metric on the tax-line grain is a separate, future metric for `finance/tax / tax_liability_and_flows`.

## Foundation gate (DEC-79b62f)

- **Location B** (contract semantics: which surface declares a value), enforced at C (binding and realization) and at the write points.
- **Not an upper-layer gap:** master (the vocabulary) and the directory (the placement) are both fully specified.
- **Not lower-layer compensation:** P4 is a net and the fix is the declaration plus write-gates.
- **Design act** (DEC-c48b0f): the precedence is declared, and the reclassification is an execution act under it.
- **Invariant I:** meaning is evaluated once, by the directory, at intent; the MCV projects it and hash byte-equality proves no meaning moved.
- **Invariant III:** no meaning-bearing state changes, and the descriptive change is appended as a revision row.
- **Invariants IV and VI:** the authority is an explicit reference, and the evidence is the trigger-emitted row plus the `revision_uid` ↔ grant cross-reference, never reconstructed.

## Consequences

- No bc-db migration is needed for D3 at `active`: the triggers and grants already exist. The optional attribution migration (D3) is a separate operator-gated DB act.
- A bc-core build delivers D3, P1–P4 and real-DB specs: signature-neutral re-read, the exactly-one revision row, and each named refusal including rollback on an injected second revision row. The build is followed by a governed serve-move.
- The live corrections are single-writer acts under recorded grants that name each MCV UID and target pair verbatim.

**Follow-ups, outside this ADR:**
- Master synonym hygiene: `fpa` / `financial_planning_and_analysis`, `general_ledger` / `general_ledger_accounting`, and `iso_55001` under finance.
- A directory-taxonomy ruling on `maintenance_order_count`.
- The realization gap: members still point at predecessors after a corrective draft.
