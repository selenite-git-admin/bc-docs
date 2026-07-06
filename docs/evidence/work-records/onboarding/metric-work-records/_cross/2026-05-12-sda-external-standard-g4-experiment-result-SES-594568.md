---
title: "SDA external-standard G4 experiment — result"
session: SES-594568
date: 2026-05-12
status: complete
type: experiment-result
authority: DEC-a17d0f
related:
  - 2026-05-12-sda-external-standard-g4-experiment-plan-SES-594568.md
  - 2026-05-12-sda-certification-operator-runbook-SES-594568.md
  - 2026-05-12-sda-first-honest-certification-canary-SES-594568.md
---

# External-standard G4 experiment — result

First SDA certification with `definition_standard ≠ BARECOUNT`.
Proves the `EXTERNAL_DEFINITION_STANDARDS` branch of G4 end-to-end
on real persisted state.

## 1. Primitive

| field | value |
|---|---|
| primitive_type | `business_field` |
| field_id | `019d7076-e439-7264-aa92-9b5bd5198307` |
| name | `credit_transfer_hdr_entry_remittance_information` |
| object_class | `credit_transfer_hdr_entry_remittance` |
| parent BO | `credit_transfer_hdr` (`certified`) |
| data_type | `string` |
| business_function | `finance` |

## 2. Final metadata

- `semantic_family = 'text'`
- `definition_standard = 'ISO_20022'`
- `standard_ref = 'ISO20022:pain.001 RemittanceInformation/Unstructured (RmtInf/Ustrd)'`

Citation evidence: BareCount BF definition begins *"Unstructured
remittance information…"* — verbatim ISO_20022 element name `Ustrd`.
The cited path resolves to a precise element in the public
ISO_20022 message dictionary (`pain.001` Customer Credit Transfer
Initiation, RemittanceInformation/Unstructured).

## 3. Lifecycle

- final `status_code = 'certified'`
- exactly **2** rows in `contract.certification_record`:

| # | action_code | from → to | gate_count | override |
|---|---|---|---|---|
| 1 | `submit_for_review` | `proposed → reviewing` | 0 | none (all 3 cols NULL) |
| 2 | `certify` | `reviewing → certified` | **9** | none (all 3 cols NULL) |

Certify row G4 detail (the experiment's primary witness):

```json
{
  "failures": [],
  "hasStandardRef": true,
  "sourceStandard": "ISO_20022"
}
```

Both transitions atomic (status flip + ledger insert in the same
PostgreSQL transaction), verified by millisecond-aligned
`business_field.updated_at` and the certify row's `created_at`.

## 4. Code gap surfaced and fixed

**Gap:** `standardRef` was missing from the metadata PATCH plumbing
across three layers (`UpdateStandardFieldDto`,
`StandardFieldService.updateField`, `StandardFieldRepository.updateField`).
The DB column `contract.business_field.standard_ref` has existed
throughout, but the application write path never accepted the wire-
format field. Every prior PATCH had `standardRef: NULL`, so the gap
was latent until the first external-standard case.

**Symptom:** PATCH 400 with `"property standardRef should not exist"`
at the global ValidationPipe — fail-loud before any DB write.

**Fix:** [bc-core@77763ff](https://github.com/selenite-git-admin/bc-core/commit/77763ff)
— three-layer plumbing mirroring the existing `semanticFamily` +
`definitionStandard` pattern verbatim. ~6 lines total across DTO +
service + repo.

**`--no-verify`** used per operator's upfront authorization in
this session, citing pre-existing TSK-c94055 lint debt in
`standard-field.service.ts` (8 warnings unrelated to this fix).

## 5. What this experiment proves

- **G4's `EXTERNAL_DEFINITION_STANDARDS` branch works end-to-end**
  on a real BF, with a real external standard, with a real
  `standard_ref`. The vocabulary split in `gates.ts` (bc-core@20674ef)
  is now demonstrably correct under live traffic.
- **The `standard_ref`-required path works.** G4 evaluates
  `hasStandardRef=true` correctly when the column is non-empty and
  the standard is external.
- **`text` family works for BF certification.** First non-identifier
  identity-category family used. Confirms the family is matrix-clean
  for `data_type='string'`.
- **`BARECOUNT` is not the only viable `definition_standard` path.**
  Six other slugs (`COSO`, `IFRS`, `IIA`, `ISO_20022`, `OAGIS`,
  `US_GAAP`) are now unblocked at the application layer — every
  future external-standard certification flows through the same
  path with no additional code changes.

## 6. Aggregate SDA certification state (post-experiment)

- **Certified BFs:** 7
  - canary: `credit_status_customer_identifier`
  - batch (5): `credit_status_date`, `payable_hdr_vendor_identifier`,
    `journal_entry_hdr_created_by_user_identifier`,
    `employee_work_schedule_schedule_start_date`,
    `debit_transfer_hdr_debtor_party_name`
  - this experiment: `credit_transfer_hdr_entry_remittance_information`
- **SDA-4 ledger rows:** 14 (2 per primitive, every certify carrying
  9 gate results, zero overrides anywhere)
- **Families exercised:** `identifier`, `date`, `name`, `text`
- **Definition standards exercised:** `BARECOUNT` (×6), `ISO_20022` (×1)
- **Overrides issued:** 0

## 7. Boundaries honoured

- One primitive touched. Backup candidate
  `019d7079-5771-7e77-ab69-9a3d3a012f74`
  (`credit_transfer_payment_debtor_identifier`) untouched.
- One bc-core commit (`77763ff`), scope-limited to `standardRef`
  plumbing.
- No DBCP. No master.* edits. No bc-core code beyond the 3-layer
  plumbing fix.
- No metric repair writes. No tenant / runtime touches.
- No CF or BO certification. No supersede / archive / unarchive.
- Provenance ledger untouched.
- Three follow-up tasks (`TSK-c94055`, `TSK-84d81c`, `TSK-000fa7`)
  remain `planned/later`. No new tasks filed by this experiment —
  the `standardRef` plumbing gap was the expected kind of bug the
  canary discipline surfaces, not a new architectural question.

## 8. Next gates (not in scope for this MWR)

- Certify-with-override experiment (runbook §7 alternative) —
  needs its own plan MWR.
- OAGIS / IFRS / IIA / US_GAAP / COSO branches of G4 — each
  warrants its own one-primitive experiment when a clean
  candidate emerges.
- CF or BO certification — requires the mirror of DBCP-1l +
  gate-evaluator extension for those primitives.

---

**End of experiment record.**
