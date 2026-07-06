---
status: complete
session: SES-594568
created_at: 2026-05-13
scope: read-only-classification
repo: bc-docs-v3
---

# Legacy-Certified vs SDA Dictionary-Certified BF Classification

## 0. Trigger

The Binding Evidence Trace for `mc__total_revenue` found that `BF.actual_ledger_amount` has
`status_code='certified'` but zero rows in `contract.certification_record`.

By SDA-4 standards, that is not audit-backed dictionary certification. It is a legacy status value.
This note classifies the `contract.business_field` registry using SDA ledger evidence rather than the
status string alone.

Read-only only. No DB writes, no code changes, no DBCP, and no certification acts were performed.

## 1. Query Basis

Classification used:

- `contract.business_field.status_code`
- `contract.business_field.semantic_family`
- `contract.business_field.definition_standard`
- `contract.certification_record`

An SDA dictionary-certified BF is counted only when:

- `business_field.status_code='certified'`
- there is a `contract.certification_record` row for `primitive_type='business_field'`
- at least one `action_code='certify'` row carries exactly 9 gate results

Clean vs override is determined from the certify row's override fields:

- clean: no override fields populated
- with override: `override_gate_code`, `override_rationale_text`, or `override_followup_task_uid` populated

## 2. Counts

| Question | Count |
|---|---:|
| Total business_fields | 7,062 |
| business_fields with `status_code='certified'` | 6,787 |
| Certified-status BFs with at least one SDA-4 certification_record row | 8 |
| Certified-status BFs with a `certify` action row carrying 9 gate results | 8 |
| Certified-status BFs with override fields populated | 1 |
| Certified-status BFs with `semantic_family IS NULL` | 6,779 |
| Certified-status BFs with `definition_standard IS NULL` | 242 |

## 3. Classification

| Classification | Definition | Count |
|---|---|---:|
| `sda_dictionary_certified_clean` | `status_code='certified'` + SDA certify row with 9 gate results + no override fields | 7 |
| `sda_dictionary_certified_with_override` | `status_code='certified'` + SDA certify row with 9 gate results + override fields populated | 1 |
| `legacy_certified_no_sda_evidence` | `status_code='certified'` without SDA certify evidence carrying 9 gate results | 6,779 |
| `not_certified` | `status_code <> 'certified'` | 275 |

## 4. Interpretation

`status_code='certified'` is unsafe as an operator-facing trust signal. It combines two materially
different populations: 8 audit-backed SDA dictionary-certified BFs and 6,779 legacy-certified BFs with
no SDA ledger evidence. The legacy population may include useful and historically working fields, but
the status string alone does not prove that G1-G8 were evaluated, that semantic_family was populated,
that provenance passed G4, or that an override trail exists. Any Binding Evidence Trace that treats the
status string as dictionary certification will overstate trust.

## 5. Terminology Rule for Future Traces

Future Binding Evidence Trace artifacts must classify the dictionary layer from SDA ledger evidence,
not from `business_field.status_code` alone.

Use these labels:

- `sda_dictionary_certified_clean`
- `sda_dictionary_certified_with_override`
- `legacy_certified_no_sda_evidence`
- `not_certified`
- `not_applicable`

The legacy status can still be reported as an input field, but it must not be collapsed into
dictionary-layer trust.

## 6. Boundary

This note does not propose a DBCP, a migration, or any retroactive certification sweep. It records the
classification gap so operator-facing trust surfaces do not confuse legacy status with SDA evidence.

