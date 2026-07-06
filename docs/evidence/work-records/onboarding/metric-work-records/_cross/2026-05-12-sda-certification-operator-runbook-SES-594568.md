---
title: "SDA certification — operator runbook (BF only, post-DBCP-1l)"
session: SES-594568
date: 2026-05-12
status: active
type: operator-runbook
authority: DEC-a17d0f
related:
  - DEC-a17d0f # SDA umbrella
  - DBCP-1k    # lifecycle vocabulary (applied)
  - DBCP-1l    # BF.semantic_family support (applied)
  - 2026-05-12-sda-first-honest-certification-canary-SES-594568.md
---

# SDA certification — operator runbook

Repeatable procedure for certifying one `business_field` at a time
through SDA-4 endpoints. Derived from the canary + 5-candidate batch
on 2026-05-12 (6/6 certified, 0 overrides, 0 retries).

## 1. Scope

- **business_field only.** No CF or BO support yet — the gate
  evaluator and PATCH path are wired for BF only.
- **Post-DBCP-1l only.** Requires `contract.business_field.semantic_family`
  column present. Requires bc-core at or beyond `72f22a9`.
- **No bulk mode.** Exactly one primitive at a time, full preflight +
  postflight per candidate.

## 2. Preconditions per candidate

| Check | Source |
|---|---|
| `status_code = 'draft'` | `contract.business_field` |
| Zero prior `certification_record` rows | `contract.certification_record` filtered by `primitive_id` |
| Parent BO is `certified` (via `business_object_field` linkage) | join check |
| Zero G2a/G2b name collisions | exact + normalized scan over `business_field.name` |
| Definition is non-empty, ≥10 chars, no banned tokens (`tbd / todo / placeholder / fixme / xxx`) | scan `definition` |
| `data_type` is compatible with the intended family per `master.semantic_family.compatible_data_types` | static crosswalk |
| Intended family's `compatible_unit_types IS NULL` | BF has no `unit_type_code` column; measure-* and `duration` are not viable today |
| `semanticFamily` value is one of `master.semantic_family.semantic_family_code` | the FK enforces it at write |
| `definitionStandard` value is one of `DEFINITION_STANDARDS` (uppercase master slug) | `gates.ts` enum + DB FK |

**Default `definitionStandard`:** `BARECOUNT` — the only internal
standard, requires no `standard_ref`. Use the other six external
standards (`COSO`, `IFRS`, `IIA`, `ISO_20022`, `OAGIS`, `US_GAAP`)
only when the BF is legitimately anchored to a published external
standard, and supply a non-empty `standardRef` in the same PATCH.

## 3. One-at-a-time execution flow

Steps 4 and 7 are the only state-changing actions. Every other step
is read-only verification.

### 3.1 Preflight — row + ledger

```sql
SELECT json_build_object(
  'status_code', status_code, 'semantic_family', semantic_family,
  'definition_standard', definition_standard, 'data_type', data_type,
  'name', name, 'object_class', object_class
) FROM contract.business_field WHERE field_id=:fieldId;

SELECT COUNT(*) FROM contract.certification_record WHERE primitive_id=:fieldId;
```

Halt if: `status_code <> 'draft'`, prior ledger rows exist, or any
precondition from §2 is violated.

### 3.2 Evaluate gates — baseline

`GET /api/sda/primitives/business_field/:fieldId/evaluate-gates`

Expected baseline before PATCH: G4 fails `source_standard_missing`
(overridable, real data-wrong) and G5/G6 fail unevaluable
(`detail.unevaluable=true`, `missingInputs=['business_field.semantic_family']`).
Other gates pass. Halt if this baseline does not match — investigate
before any write.

### 3.3 PATCH metadata

```http
PATCH /api/business-fields/:fieldId
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "semanticFamily": "<chosen-family>",
  "definitionStandard": "<chosen-standard>"
}
```

Expected: HTTP 200 with the updated row reflecting both fields.
Halt on non-200 or on either field still showing the prior value.

### 3.4 Evaluate gates — post-PATCH

`GET /api/sda/primitives/business_field/:fieldId/evaluate-gates`

Required for unattended certification: all 9 gates `pass`,
`canCertifyWithoutOverride: true`, `hasBlockingFailures: false`,
`hasOverridableFailures: false`, `unevaluableGates: []`.

If any failure remains, stop and decide explicitly: fix the
underlying metadata, use override (with separate approval), or
choose a different candidate.

### 3.5 Submit for review

```http
POST /api/sda/primitives/business_field/:fieldId/submit-for-review
Authorization: Bearer <jwt>
```

(No body.)

Expected: HTTP 200, response carries the new ledger row.

### 3.6 Verify — intermediate

```sql
SELECT status_code FROM contract.business_field WHERE field_id=:fieldId;
SELECT action_code, from_state_code, to_state_code
FROM contract.certification_record
WHERE primitive_id=:fieldId ORDER BY created_at;
```

Expected: `status_code='reviewing'`, exactly 1 ledger row with
`action_code='submit_for_review'`, `from='proposed'`, `to='reviewing'`.

### 3.7 Certify

```http
POST /api/sda/primitives/business_field/:fieldId/certify
Authorization: Bearer <jwt>
Content-Type: application/json

{ "gateResults": [<the exact 9 passing gate results from step 3.4>] }
```

No `override` field if §3.4 reported zero failures. Body shape
preserved verbatim — each gate result carries `gateCode`, `verdict`,
`overridable`, and `detail`.

Expected: HTTP 200 with `actionCode='certify'`,
`fromStateCode='reviewing'`, `toStateCode='certified'`, 9 gate
results in the response, `override: null`.

### 3.8 Postflight

```sql
SELECT bf.status_code AS bf_status,
       (SELECT COUNT(*) FROM contract.certification_record
        WHERE primitive_id=bf.field_id) AS ledger_rows,
       (SELECT COUNT(*) FROM contract.certification_record
        WHERE primitive_id=bf.field_id
          AND override_gate_code IS NOT NULL) AS override_count
FROM contract.business_field bf WHERE bf.field_id=:fieldId;
```

Required: `bf_status='certified'`, `ledger_rows=2`, `override_count=0`
(unless override was pre-approved). The two rows must be
`submit_for_review proposed→reviewing` then
`certify reviewing→certified`.

Stop immediately on any deviation. Do not proceed to the next
candidate.

## 4. Evidence — six certified BFs (2026-05-12)

All six certified through the flow in §3 with zero overrides, zero
retries, two ledger rows each. Same certifier identity
(`anant@selenite.co`, role `platform_admin`).

| # | field_id | name | family | data_type |
|---|---|---|---|---|
| canary | `019d7050-4513-792c-8fb1-c307fbdeaebe` | credit_status_customer_identifier | identifier | string |
| 1 | `019d7051-3245-7f02-bad1-65ca6d07f60f` | credit_status_date | date | date |
| 2 | `019d70a9-5205-732c-916e-0ff909a23844` | payable_hdr_vendor_identifier | identifier | string |
| 3 | `019d709a-455e-71a7-8a2b-e70ccbd46687` | journal_entry_hdr_created_by_user_identifier | identifier | string |
| 4 | `019d70c1-a4dd-78b5-bebf-2a34e4d5599a` | employee_work_schedule_schedule_start_date | date | date |
| 5 | `019d707f-10c4-734e-b5dc-24738e67cf56` | debit_transfer_hdr_debtor_party_name | name | string |

All carry `definition_standard='BARECOUNT'`. 12 net new
`certification_record` rows. Atomic dual-write verified by
millisecond-aligned `business_field.updated_at` and the certify
ledger's `created_at`.

## 5. Boundaries

- **No bulk mode.** Each candidate is its own §3 cycle end-to-end.
- **No metadata edits outside the §3.3 PATCH.** Specifically: no
  `data_type` change, no `definition` rewrite, no `object_class`
  reassignment under cover of a certification.
- **No overrides without separate operator approval.** The certify
  body's `override` field is omitted on this runbook's default path.
  If an overridable gate honestly fails, stop and seek explicit
  approval with a ≥40-char rationale + a followup task UID.
- **No CF or BO certification.** Gate evaluator + PATCH path are
  BF-only. CF and BO support are separate slices (would mirror
  DBCP-1l + the gate-evaluation reader extension).
- **No metric repair writes.** Nothing in `metric.*` / `tenant.*` /
  `runtime.*` is touched by SDA certification.
- **No supersede / archive / unarchive.** Deferred per DBCP-1k §6.4.
- **Provenance ledger untouched.** SDA certification writes to
  `contract.certification_record`, not `contract.primitive_provenance`.

## 6. Known follow-ups (not blockers)

| Task | Title | Status |
|---|---|---|
| [TSK-c94055](mcp://devhub) | Clear pre-existing ESLint debt in `standard-field.service.ts` | `planned/later` |
| [TSK-84d81c](mcp://devhub) | Decide on `data_type='code'` legitimacy (779 BFs affected; not certifiable today against the current matrix) | `planned/later` |
| [TSK-000fa7](mcp://devhub) | Investigate `BF.object_class` vs linked `BO.object_name` mismatch (pattern is registry-wide, not gate-blocking) | `planned/later` |

None of these block the §3 flow for a properly-shaped candidate.

## 7. Next recommended experiment

**Pick ONE of the following** for the next live write — not another
larger `BARECOUNT` batch. The same flow has now been proven 6 times
on the simplest possible shape; the next experiment should stretch
exactly one previously-untested edge:

- **One external-standard G4 case.** Find a draft BF whose
  definition legitimately cites an external standard (e.g. an
  ISO_20022 payment field, an OAGIS taxonomy term). PATCH
  `{"semanticFamily": <suitable>, "definitionStandard": "ISO_20022",
  "standardRef": "<real reference>"}`. Confirm G4 passes through the
  `EXTERNAL_DEFINITION_STANDARDS` branch with a real ref. Proves
  the external-standard half of G4 that this batch did not exercise.
- **One certify-with-override case.** Find a draft BF where one
  overridable gate honestly fails (e.g. G3 with a slightly weak
  definition, or G4 if `definitionStandard` is legitimately
  unknown). PATCH metadata. Run §3.4 to confirm exactly one
  overridable failure. Run submit-for-review. Then certify with
  `{"gateResults":[…], "override":{"gateCode":"G3","rationaleText":
  "<≥40 chars>","followupTaskUid":"<task>"}}`. Confirm certify
  writes the row with override columns populated and the BF flips
  to `certified`. Proves the override discipline end-to-end.

Pick one. File its plan as a separate MWR before the live write.

## 8. Tooling notes

- **JWT:** obtain via `devhub_get_cognito_token` MCP (admin app,
  `platform_admin` role on the demo user). 1-hour TTL.
- **Postflight queries:** the four-field row + ledger join in §3.8
  is the minimum verification. Capture-and-store the response of
  every POST in §3.5 and §3.7 for audit; the `certificationRecordId`
  is the authoritative reference.
- **Failure response:** on any HTTP non-2xx, stop. Do not retry the
  same call without diagnosing. Read the BF row and ledger to
  determine actual state before deciding the next move.

---

**End of runbook.**
