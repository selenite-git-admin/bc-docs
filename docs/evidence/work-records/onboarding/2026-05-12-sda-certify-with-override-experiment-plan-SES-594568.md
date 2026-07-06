---
title: "SDA certify-with-override experiment — plan only"
session: SES-594568
date: 2026-05-12
status: plan
type: experiment-plan
authority: DEC-a17d0f
related:
  - 2026-05-12-sda-certification-operator-runbook-SES-594568.md
  - 2026-05-12-sda-external-standard-g4-experiment-result-SES-594568.md
---

# Certify-with-override experiment — plan

Per runbook §7 alternative. Exercises SDA-4's override discipline
end-to-end on **one** BF with **exactly one** honest overridable
failure. **Plan only — no PATCH, no submit-for-review, no certify,
no live writes from this MWR.**

## 1. Scope (locked)

- One BF candidate, primary. One backup.
- Read-only planning. No metadata or lifecycle writes.
- No matrix change. No DBCP. No bc-core code change.
- Target failure: **G4 `source_standard_missing`** (overridable,
  data-wrong-not-data-missing). Other gates pass cleanly after the
  approved metadata PATCH.
- The override discipline exercised:
  - `gateCode='G4'`
  - `rationaleText` ≥ 40 chars
  - `followupTaskUid` references a real DevHub task created
    just-in-time at execution (see §8 — not a "new task" filed by
    this plan; structurally required by the override act itself
    per the runbook §5 + DBCP-1c CHECK).

## 2. Why G4 over G3

- **G4 is the cleanest overridable failure.** Leaving
  `definition_standard` NULL (the trigger) doesn't weaken any other
  attribute of the BF. The BF stays a fully-valid, well-defined,
  uniquely-named primitive with a real `semantic_family`. The only
  open question is "which external standard authored this term",
  and that's a documentation gap, not a quality problem.
- G3 alternatives would require deliberately authoring (or
  preserving) a weaker definition — that's manufacturing a failure
  rather than honestly recording one.
- G4 also exercises the **explicit absence** of an external-standard
  citation, which is the inverse of last turn's experiment (which
  exercised a present citation). Symmetric coverage.

## 3. Primary candidate

### 3.1 Identity

| field | value |
|---|---|
| field_id | `019d70bb-f471-7683-b455-cc5600af5840` |
| name | `remittance_advice_hdr_payee_party_identifier` |
| business_function | `finance` |
| object_class | `remittance_advice_hdr_payee_party` |
| property | `identifier` |
| data_type | `string` |
| status_code | `draft` |
| existing `semantic_family` / `definition_standard` / `standard_ref` | all NULL |
| prior `certification_record` rows | 0 |
| parent BO | `remittance_advice_hdr` (`certified`) |
| definition (53 chars) | *"The party receiving the payment should be identified."* |
| G2a / G2b collisions | 0 / 0 (verified) |
| banned-token check | clean |
| mentions external standard in definition? | **no** (clean for "absent-standard" framing) |

### 3.2 Proposed metadata PATCH (one field, NOT two)

```json
{ "semanticFamily": "identifier" }
```

Deliberately omits `definitionStandard` so G4 fails with
`source_standard_missing` after this PATCH. `standard_ref` not
sent either.

This is a **deliberate departure from runbook §3.3's two-field
PATCH**. The execution turn should explicitly note "single-field
PATCH for override experiment" — it is not a slip.

### 3.3 Family choice — `identifier`

`master.semantic_family['identifier'].compatible_data_types =
['string']`, `compatible_unit_types = null`. Matches `data_type=
string`. Matrix-clean. Same family as four of the seven prior
certifications; not a stretch, but the experiment's stretch is G4
override, not family novelty.

### 3.4 Expected G1–G8 verdicts after the §3.2 PATCH

| Gate | Verdict | Overridable | Why |
|---|---|---|---|
| G1 | pass | true | snake_case + name starts with `remittance_advice_hdr_payee_party_` |
| G2a | pass | false | 0 exact-name collisions (verified) |
| G2b | pass | true | 0 normalized-form collisions (verified) |
| G3 | pass | true | 53 chars, no banned tokens, sentence-shaped |
| **G4** | **fail** | **true** | `definition_standard IS NULL` → `failures: ['source_standard_missing']`. **Real data-wrong-but-overridable.** |
| G5 | pass | false | `semantic_family='identifier'` in enum |
| G6 | pass | false | `data_type='string'` ∈ `compatible_data_types`; unit `null` |
| G7 | pass | false | name starts with `BF.object_class + '_'` |
| G8 | pass | false | CF-only; N/A for BF |

Expected summary: `canCertifyWithoutOverride: false`,
`hasBlockingFailures: false`, `hasOverridableFailures: true`,
`unevaluableGates: []`. **Exactly one overridable failure, G4.**

### 3.5 Proposed override body for certify

```json
{
  "gateResults": [<the 9 server-computed gate results from /evaluate-gates,
                    8 pass + 1 fail with G4 detail.failures=['source_standard_missing']>],
  "override": {
    "gateCode": "G4",
    "rationaleText": "Provenance authoring for the remittance_advice_hdr ISO_20022 lineage is deferred to a separate metadata pass; this primitive is being certified ahead of that pass to unblock downstream consumption.",
    "followupTaskUid": "<TSK-uid-created-at-execution-time>"
  }
}
```

`rationaleText` length: 211 chars (well above the 40-char minimum
enforced by the pure builder + DBCP-1c CHECK).

`followupTaskUid` placeholder: **created at execution**, not by
this plan. The follow-up task records the metadata work that will
eventually populate `definition_standard='ISO_20022'` +
`standard_ref` on this BF (probably batched alongside the other
remittance_advice and credit/debit_transfer ISO_20022 candidates
in a future authoring pass). This task is **structurally required
by the SDA-4 override contract** — it's not a "new task" in the
sense your standing rule guards against; it's a load-bearing
artifact for the override act itself.

## 4. Backup candidate

### 4.1 Identity

| field | value |
|---|---|
| field_id | `019d70bb-74ae-7f66-9e91-e52dc69bb951` |
| name | `remittance_advice_hdr_payer_party_identifier` |
| object_class | `remittance_advice_hdr_payer_party` |
| property | `identifier` |
| data_type | `string` |
| status_code | `draft` |
| metadata fields | all NULL |
| prior ledger rows | 0 |
| parent BO | `remittance_advice_hdr` (`certified`) |
| definition (50 chars) | *"The party making the payment should be identified."* |
| G2a/G2b/banned-token | all clean |
| external-standard mention | none |

### 4.2 Proposed metadata PATCH

```json
{ "semanticFamily": "identifier" }
```

Same as primary. Same expected gate shape, same override target,
same rationale shape. Available if the primary preflight fails.

## 5. Preflight (per the runbook §3.1 + this experiment's extras)

```sql
SELECT json_build_object(
  'status_code', status_code, 'semantic_family', semantic_family,
  'definition_standard', definition_standard, 'standard_ref', standard_ref,
  'data_type', data_type, 'name', name, 'object_class', object_class)
FROM contract.business_field WHERE field_id=:fieldId;

SELECT COUNT(*) FROM contract.certification_record WHERE primitive_id=:fieldId;
```

Halt if: `status_code <> 'draft'`, any of the three metadata fields
non-NULL, prior ledger rows exist, or BO not certified.

## 6. Re-evaluate-gates contract (post-PATCH)

`GET /api/sda/primitives/business_field/:fieldId/evaluate-gates`

Required for the experiment:
- `summary.canCertifyWithoutOverride === false`
- `summary.hasBlockingFailures === false`
- `summary.hasOverridableFailures === true`
- `summary.unevaluableGates === []`
- exactly one failing gate, code `G4`, `detail.failures` contains
  `source_standard_missing`

If the post-PATCH state shows anything else (zero failures, or
multiple failures, or any non-overridable failure, or any
unevaluable gate), **stop** — the experiment's premise is broken.

## 7. Postflight (per the runbook §3.8 + this experiment's extras)

```sql
SELECT bf.status_code AS bf_status,
       (SELECT COUNT(*) FROM contract.certification_record
        WHERE primitive_id=bf.field_id) AS ledger_rows
FROM contract.business_field bf WHERE bf.field_id=:fieldId;

SELECT action_code, from_state_code, to_state_code,
       jsonb_array_length(gate_results_json) AS gate_count,
       override_gate_code,
       override_rationale_text,
       override_followup_task_uid,
       char_length(override_rationale_text) AS rationale_len
FROM contract.certification_record
WHERE primitive_id=:fieldId
ORDER BY created_at;
```

Required:
- `bf_status='certified'`, `ledger_rows=2`.
- Row 1: `submit_for_review proposed→reviewing`, gate_count=0,
  all three override columns NULL.
- Row 2: `certify reviewing→certified`, gate_count=9,
  `override_gate_code='G4'`, `override_rationale_text` non-empty
  and ≥40 chars (verify `rationale_len >= 40`),
  `override_followup_task_uid` non-empty matching the just-created
  TSK uid.

## 8. Follow-up task created at execution time

The override act requires a non-empty `followupTaskUid` at the
DBCP-1c CHECK level. The execution turn will create one DevHub
task **just before submit-for-review** with this shape:

- title: "Author ISO_20022 provenance for remittance_advice_hdr_payee_party_identifier (post-override)"
- project: `bc-core`
- status: `planned`
- priority: `later`
- tags: `sda,override-followup,iso20022-authoring`
- details: linkback to this MWR + the override rationale; concrete
  next action ("PATCH definitionStandard='ISO_20022' + standardRef=
  '<ISO20022:camt.029 or similar>' once the message map for
  remittance_advice_hdr is reviewed").

The TSK uid returned by `devhub_task_add` is the value plugged
into the certify body's `override.followupTaskUid`. This is not a
"new task filed by the plan" — the plan declares the slot; the
task is materialized at execution.

If for any reason the task creation fails at execution time, **stop
before submit-for-review** — never submit a primitive whose only
viable certification path requires a `followupTaskUid` that doesn't
yet exist.

## 9. Recovery — if submit-for-review succeeds but certify fails

After `submit-for-review`, the BF is at `status_code='reviewing'`
with one ledger row. If `certify` fails (any HTTP 4xx/5xx), the
recovery is **`return-to-author`**, not `withdraw`:

```http
POST /api/sda/primitives/business_field/:fieldId/return-to-author
```

Expected effect: `status_code: reviewing → proposed`, one new
ledger row (`action_code='return_to_author'`). Total 2 rows after
recovery. The BF is back in an author-editable state without
"withdrawn" terminality. Original submit-for-review row preserved
verbatim (immutable ledger).

Why **not** `withdraw`: `withdrawn` is a terminal state for SDA-4
in this Tranche per runbook §1, and represents "the author has
abandoned this BF". A failed certify call is not abandonment —
it's a transient operational issue, recoverable by
return-to-author.

The recovery path mirrors the rollback contract tested in
`state-transition.spec.ts` (the atomic dual-write guarantees that
a failed certify does not partially flip status; the BF stays at
`reviewing` for `return-to-author` to handle).

## 10. What this experiment proves (when executed)

- **SDA-4 override discipline end-to-end.** The DBCP-1c CHECK on
  certification_record's override-trio (gate_code, rationale,
  followup_task_uid all non-null when an override is recorded)
  becomes live-tested on a real row.
- **Override-permitted certification path works.** A primitive
  with one honest overridable failure can reach `certified` via
  the operator-asserted override, with a complete audit trail
  pointing at the deferred work.
- **G4's overridable=true branch is exercised against a real
  `source_standard_missing` failure**, not a manufactured one.
- **return-to-author recovery is available** if certify fails —
  not exercised in the success path, but documented as the
  honest recovery target.

## 11. What this experiment does NOT prove

- Non-overridable gate override rejection. The state-transition
  service spec already covers it (4 cases). A separate experiment
  could exercise it live if you want a belt-and-suspenders check.
- Multiple-overridable-failure case. SDA-4's current design
  permits exactly one override per certify call; a future ADR
  decision is whether to allow per-gate-failure tuples.
- OAGIS / IFRS / IIA / US_GAAP / COSO branches of G4 — those
  remain unexercised live.
- CF or BO certification — still BF-only.

## 12. Boundaries honoured by this plan

- No PATCH executed. No submit-for-review. No certify.
- No DevHub task created — the slot is reserved, materialized at
  execution.
- No bc-core code change. No DBCP. No master.* edits.
- No new architectural task filed. Three known follow-ups
  (`TSK-c94055`, `TSK-84d81c`, `TSK-000fa7`) remain `planned/later`.
- No other primitive touched.

## 13. Awaiting operator authorization

When approved, execution proceeds in this order:
1. Preflight (§5).
2. Single-field PATCH (§3.2).
3. Re-evaluate gates (§6) — require exactly one G4 failure.
4. Create the follow-up DevHub task (§8); capture its UID.
5. `POST submit-for-review`.
6. Verify intermediate state.
7. `POST certify` with §3.5 body (using the real TSK uid).
8. Postflight (§7).

Stop immediately on any deviation. If §3 primary preflight fails,
fall through to §4 backup as a second-attempt experiment (also
with explicit approval).

---

**End of plan.**
