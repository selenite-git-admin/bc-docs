---
title: "SDA certify-with-override experiment — result"
session: SES-594568
date: 2026-05-12
status: complete
type: experiment-result
authority: DEC-a17d0f
related:
  - 2026-05-12-sda-certify-with-override-experiment-plan-SES-594568.md
  - 2026-05-12-sda-certification-operator-runbook-SES-594568.md
  - 2026-05-12-sda-external-standard-g4-experiment-result-SES-594568.md
---

# Certify-with-override experiment — result

First SDA certification with an override. Proves the SDA-4 override
discipline end-to-end on a real BF with one honest overridable
failure, and validates the DBCP-1c override-trio CHECK constraint
live.

## 1. Primitive

| field | value |
|---|---|
| primitive_type | `business_field` |
| field_id | `019d70bb-f471-7683-b455-cc5600af5840` |
| name | `remittance_advice_hdr_payee_party_identifier` |
| object_class | `remittance_advice_hdr_payee_party` |
| parent BO | `remittance_advice_hdr` (`certified`) |
| data_type | `string` |
| business_function | `finance` |

## 2. Final metadata

- `semantic_family = 'identifier'` (set by the single-field PATCH)
- `definition_standard = NULL` (deliberately left unset — the
  override target)
- `standard_ref = NULL`

The `definition_standard` and `standard_ref` columns are
intentionally NULL on the certified row. The certify act is paired
with a recorded override + a live follow-up task that owns the
metadata work needed to populate them later.

## 3. Lifecycle

- final `status_code = 'certified'`
- exactly **2** rows in `contract.certification_record`:

| # | action_code | from → to | gate_count | override_gate_code | override_rationale_len | override_followup_task_uid |
|---|---|---|---|---|---|---|
| 1 | `submit_for_review` | `proposed → reviewing` | 0 | NULL | NULL | NULL |
| 2 | `certify` | `reviewing → certified` | **9** | **`G4`** | **197** (≥40 ✓) | **`TSK-3233f7`** |

Row 1 carries all three override columns NULL (submit-for-review
never records overrides). Row 2 carries the complete override-trio
present — exactly the shape the DBCP-1c `certification_record_override_chk`
CHECK enforces: either all three NULL or all three non-NULL with
rationale length ≥ 40.

Certify row G4 detail:

```json
{
  "failures": ["source_standard_missing"],
  "hasStandardRef": false,
  "sourceStandard": null
}
```

The other 8 gates passed cleanly. G4 verdict `fail`,
`overridable=true` — exactly one overridable failure, exactly one
override.

## 4. Follow-up task

[**TSK-3233f7**](mcp://devhub) — *"Author provenance for
remittance_advice_hdr_payee_party_identifier"*. Status
`planned/later`, tags `sda,override-followup,iso20022-authoring`,
project `bc-core`.

Purpose: track the deferred provenance work that, when completed,
will replace `definition_standard=NULL` with the correct
ISO_20022 lineage (`remittance_advice_hdr` is paradigm ISO_20022
camt.029 / camt.054 territory). The PATCH alone will be sufficient —
the BF is already certified; the metadata correction does not
trigger re-certification.

The task UID is recorded immutably on the certify ledger row's
`override_followup_task_uid` column, so the audit trail leads from
the override act directly to the open work item.

## 5. What this experiment proves

- **SDA-4 override discipline works end-to-end.** A BF with exactly
  one honest overridable failure traversed `submit-for-review` →
  `certify` with the override block populated, and the BF flipped
  to `certified` atomically.
- **The DBCP-1c override-trio CHECK is live-tested.** The constraint
  `certification_record_override_chk` requires either all three
  override columns NULL (`submit_for_review` row) or all three
  non-NULL with `char_length(override_rationale_text) >= 40`
  (`certify` row). Both shapes appear on the same primitive's
  ledger; both passed.
- **G4 `source_standard_missing` can be certified only with a
  complete audit trail.** The override carries the gate code, a
  197-char rationale, and a real TSK uid. There is **no silent
  bypass path** — every requirement of the override discipline
  was satisfied by structure, not convention.
- **Rationale length enforcement is live.** The 40-char floor
  enforced by the pure builder + the DB CHECK held against the
  actual rationale.

## 6. Aggregate SDA certification state (post-experiment)

- **Certified BFs:** 8
  - canary (1): `credit_status_customer_identifier`
  - 5-candidate batch: `credit_status_date`, `payable_hdr_vendor_identifier`,
    `journal_entry_hdr_created_by_user_identifier`,
    `employee_work_schedule_schedule_start_date`,
    `debit_transfer_hdr_debtor_party_name`
  - external-standard G4 experiment (1): `credit_transfer_hdr_entry_remittance_information`
  - certify-with-override experiment (1): `remittance_advice_hdr_payee_party_identifier`
- **SDA-4 ledger rows:** 16 (2 per primitive; every certify
  carrying 9 gate results; one override total — this primitive)
- **Families exercised:** `identifier` (×6), `date` (×2),
  `name` (×1), `text` (×1)
- **Definition standards exercised:** `BARECOUNT` (×6),
  `ISO_20022` (×1), `NULL-with-G4-override` (×1, this primitive)
- **Overrides issued:** 1 (this experiment)

## 7. Boundaries honoured

- One primitive touched. Backup candidate
  `019d70bb-74ae-7f66-9e91-e52dc69bb951`
  (`remittance_advice_hdr_payer_party_identifier`) untouched.
- **One DevHub task created (TSK-3233f7), structurally required by
  the override act.** Not a free-floating new task — the override
  contract requires a non-empty `followup_task_uid` at the DBCP-1c
  CHECK level. Declared as such in the plan MWR §8.
- No DBCP. No master.* edits. No bc-core code change.
- No metric repair writes. No tenant / runtime touches.
- No CF or BO certification. No supersede / archive / unarchive.
- Provenance ledger untouched.
- Three known follow-ups (`TSK-c94055`, `TSK-84d81c`, `TSK-000fa7`)
  remain `planned/later`; this experiment did not change them or
  spawn any new architectural follow-ups beyond the override
  task itself.

## 8. Next gates (not in scope for this MWR)

- Additional override cases targeting different gates (G3 weak
  definition, G2b normalized collision) — each its own plan MWR.
- OAGIS / IFRS / IIA / US_GAAP / COSO branches of G4 — five
  external-standard experiments remaining.
- CF or BO certification — requires the mirror of DBCP-1l + the
  gate-evaluator extension for those primitives.

---

**End of experiment record.**
