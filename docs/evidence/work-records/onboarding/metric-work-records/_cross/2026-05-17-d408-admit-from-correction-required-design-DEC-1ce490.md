---
title: "D408 admit-from-correction-required endpoint design"
date: 2026-05-17
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
plan: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md
references:
  - bc-core@cea5695 (A2 ISO evidence packet)
  - bc-core@397d9b3 (A2 halted apply — Step 1 422 on §12 status_code precondition)
related_adr: bc-docs-v3/docs/adrs/ADR-a49413.md (§12 remediate-semantics)
session: SES-c5af8c
task: TSK-eae922
type: design-note
status: proposed
---

# D408 `admit-from-correction-required` endpoint — design (not implemented)

Design-only note. **No service code, no SQL, no DB writes, no endpoint calls in this slice.** Authored in response to the §12 precondition gap exposed by `iso20022_camt_xchg_rate` (see `bc-core@397d9b3`).

## 1. Problem statement

The D408 catalog admission state machine (per ADR-1ce490) is orthogonal to the legacy `status_code` lifecycle (`draft` / `proposed` / `certified` / `deprecated` / `superseded` / `withdrawn`). The orthogonality was intentional — `catalog_state_code` records *whether this BF is admissible as catalog vocabulary today*; `status_code` records *whether this BF has been certified through the legacy SDA chain*. A row can legitimately occupy any pair of (status_code, catalog_state_code) values.

D408 currently exposes three governed write endpoints on `business_field`:

| Endpoint | Pre-state required | What it mutates | What it does NOT do |
|---|---|---|---|
| `POST /:id/remediate-semantics` (DEC-a49413 §12) | `status_code='certified'` | `definition_standard`, `standard_ref`, `semantic_family`, `unit_type_code` | Does not flip `catalog_state_code`; does not change `status_code`; refuses `status_code != 'certified'`. |
| `POST /:id/correct-definition` (DEC-1ce490) | `catalog_state_code='correction_required'` | `definition` + the D408 catalog-admission columns (flips `catalog_state_code → certified_catalog`) | Does not change `status_code`; does not touch `semantic_family`/`unit_type_code`/`definition_standard`/`standard_ref`. |
| `POST /:id/correct-type` (DEC-1ce490) | `catalog_state_code='correction_required'` | `representation_term`, `data_type` + the D408 catalog-admission columns (flips `catalog_state_code → certified_catalog`) | Does not change `status_code`; does not touch the four SDA-binding columns. |

These three endpoints assume the path *into* `correction_required` was via either (a) a legacy-certified BF demoted by D408 backfill (DBCP-1q-A) or (b) operator-driven demotion of an already-certified BF. Both paths assume the row arrived with `status_code='certified'`.

The discovery: `iso20022_camt_xchg_rate` arrived in `correction_required` directly from `candidate_import` via DBCP-1q-A backfill without ever being legacy-certified. Its `status_code` is still `'draft'`. Today no endpoint exists that can:

> Take a `status_code='draft'` AND `catalog_state_code='correction_required'` row, apply an operator-approved source-backed full uplift payload (definition + 4 SDA columns + type pair), AND promote it atomically to `status_code='certified'` AND `catalog_state_code='certified_catalog'` after a full projected G1–G8 pass.

The `iso20022_camt_xchg_rate` halt (`bc-core@397d9b3`) made this gap explicit. This endpoint design closes it.

## 2. Why not weaken existing endpoints

- **`/remediate-semantics` (§12) must remain `status_code='certified'`-only.** It was authored under DEC-a49413 specifically to uplift the 1,392 legacy-certified BFs missing SDA evidence — not to elevate draft rows. Accepting `draft` here would re-introduce uncontrolled remediation of non-certified rows, which is exactly what D408 was authored to prevent.
- **`/correct-type` and `/correct-definition` must remain narrow corrections.** Their job is to mutate one dimension (type pair OR definition) of an already-certified BF that D408 flagged for correction. Expanding their scope to also rewrite `definition_standard` + `standard_ref` + `semantic_family` + `unit_type_code` + flip `status_code` would conflate three distinct admission decisions (semantic provenance, type coherence, draft→certified lifecycle promotion) into a single overloaded endpoint.
- **Direct SQL promotion is forbidden** by the Database Change Protocol (CLAUDE.md) and the Foundation Gate (no compensation at the storage layer for an upper-layer governance gap).
- This endpoint is a **new admission boundary** that explicitly accepts the `(draft, correction_required)` state pair as its precondition. It is not a bypass of any existing endpoint; it covers a state pair that has no existing endpoint.

## 3. Proposed endpoint contract

### 3.1 Route + scope

```
POST /api/business-fields/:fieldId/admit-from-correction-required
```

- Platform-scoped (mirrors `/correct-*` and `/remediate-semantics`).
- `@PlatformOnly()` (no tenant header required).
- Requires JWT carrying `platform_admin` role (same as §12 / correct-*).
- `@HttpCode(HttpStatus.OK)` on success.

### 3.2 Request body (`AdmitFromCorrectionRequiredDto`)

```jsonc
{
  "definition": "string (≥20 chars, must pass G1)",
  "definitionStandard": "BARECOUNT | COSO | IFRS | IIA | ISO_20022 | OAGIS | US_GAAP",
  "standardRef": "string | null (required when definitionStandard != BARECOUNT)",
  "semanticFamily": "string (closed enum from profiles.ts SEMANTIC_FAMILY_ENUM)",
  "unitTypeCode": "string | null (null permitted only when G6 matrix says compatible_unit_types=null for the chosen family)",
  "representationTerm": "string (closed enum: Amount, Identifier, Code, Text, DateTime, Quantity, Number, Rate, Date, Name, Percent, Indicator)",
  "dataType": "string (closed enum: number, string, code, timestamp, integer, date, boolean)",
  "rationale": "string (≥40 chars; bounded-domain reason for admission, e.g. 'expected context-engine lookup vocabulary for X')",
  "sourceEvidence": [
    {
      "sourceType": "FASB | SEC | XBRL_US_GAAP | IFRS | OAGIS | ISO_20022 | OTHER",
      "sourceRef": "element id or doc reference",
      "sourceUrl": "URL or doc identifier",
      "citationNote": "operator-authored verbatim/cited quote"
    }
  ],
  "reviewRunUid": "string | null (optional; generated as `d408-admit-<iso-timestamp>` if omitted)"
}
```

Validation rules (executed in `validateAdmitPayload(dto)`, pure, throws 400 on any violation):

- `definition`: ≥ 20 chars, no banned templates, no datatype boilerplate, not a name restatement (delegates to `validateDefinitionG1` from `bf-correction.helper.ts`).
- `definitionStandard`: in the enum above (matches Swagger schema in `/remediate-semantics`).
- `standardRef`: required when `definitionStandard != 'BARECOUNT'` (matches §12 rule).
- `semanticFamily`: must be in `SEMANTIC_FAMILY_ENUM` (closed D366 enum).
- `unitTypeCode`: must match the G6 matrix for the chosen `semanticFamily` (null permitted only when matrix says `compatible_unit_types: null`).
- `representationTerm` + `dataType`: must be in the closed enums; must be G3-coherent (delegates to `validateTypePair` from `bf-correction.helper.ts`).
- `rationale`: ≥ 40 chars (mirrors the override-rationale floor used elsewhere in the SDA framework; prevents one-word admissions).
- `sourceEvidence`: non-empty array; each entry must have non-empty `sourceType`, `sourceRef`, and `citationNote`.

### 3.3 Required preconditions (DB-level, after payload validation)

| Check | Failure response |
|---|---|
| BF row exists | 404 NotFoundException |
| `status_code = 'draft'` (single-axis precondition for this endpoint) | 422 UnprocessableEntity (`status_code_not_draft`) |
| `catalog_state_code = 'correction_required'` | 422 UnprocessableEntity (`catalog_state_not_correction_required`) |
| `archived_at IS NULL` (row is not already archived) | 422 UnprocessableEntity (`row_archived`) |
| No CC data_type conflict on the proposed `dataType` (mirrors `/correct-type`'s pre-write check via `findCcDataTypeConflicts`) | 409 ConflictException with the conflicting CFs in the problem payload |
| Projected post-update row passes the **full SDA G1–G8** evaluation (`evaluateCertificationGates` with `primitiveType='business_field'`) | 422 UnprocessableEntity with `gateResults[]` showing all gates + verdicts |

### 3.4 Atomic transaction (per row, single tx)

On all preconditions pass:

1. INSERT one `contract.certification_record` row:
   - `primitive_type='business_field'`
   - `primitive_id=<fieldId>`
   - `action_code` per §4 decision below
   - `from_state_code='draft'`, `to_state_code='certified'` (status_code axis)
   - `gate_results_json` snapshot containing all G1–G8 verdicts + the rationale + the sourceEvidence array
   - `advisory_verdicts_json=[]`
   - `certifier_sub`, `certifier_role_at_action`, `certifier_email`
   - Returns `certification_record_id`.

2. UPDATE `contract.business_field` SET:
   - `status_code = 'certified'`
   - `definition = <dto.definition>`
   - `definition_standard = <dto.definitionStandard>`
   - `standard_ref = <dto.standardRef>`
   - `semantic_family = <dto.semanticFamily>`
   - `unit_type_code = <dto.unitTypeCode>`
   - `representation_term = <dto.representationTerm>`
   - `data_type = <dto.dataType>`
   - `catalog_state_code = 'certified_catalog'`
   - `catalog_state_reason_code = NULL`
   - `catalog_state_reason_text = <dto.rationale>` (record the bounded-domain reason)
   - `catalog_reviewed_at = now()`
   - `catalog_review_run_uid = <reviewRunUid>`
   - `gate_signals_json = <projected G1–G8 snapshot>`
   - `gate_signals_at = now()`
   - `gate_signals_row_hash = sha256(definition|data_type|representation_term|object_class|semantic_family|unit_type_code)`
   - `admission_rule_version_at_certify = 'v1'` (current D408 admission rule version)
   - `certification_record_id = <new id from step 1>`
   - `archived_at = NULL`
   - WHERE `field_id = <fieldId>` AND `status_code = 'draft'` AND `catalog_state_code = 'correction_required'` (concurrency guard — see §6).

3. If the UPDATE row count is 0, the transaction aborts with 409 `catalog_state_conflict` (another writer changed the row between read and write).

## 4. Ledger / action_code decision

**Recommendation: add a new `action_code` value `admit_bf_from_correction_required`.** Do **not** reuse `admit_bf_catalog`.

### 4.1 Trade-off

| Option | Pros | Cons |
|---|---|---|
| **A. Reuse `admit_bf_catalog`** | No CHECK enum change; matches existing 1,651 `admit_bf_catalog` ledger rows that recorded the DBCP-1q-A grandfather cohort. | Conflates two semantically distinct admission events: "row was already certified-grandfathered by the D408 backfill" vs "row was a draft candidate that an operator admitted via full evidence review". Loses queryability ("show me only operator-admitted-from-correction rows") and erodes the audit-narrative quality of the ledger. |
| **B. New `admit_bf_from_correction_required`** | Distinct, queryable event class. Cleanly records: from_state_code='draft' → to_state_code='certified' WITH catalog axis flip correction_required → certified_catalog. Future reports can count operator-driven admissions vs grandfathered admissions vs recertifications without parsing `gate_results_json`. | Requires a tiny additive DBCP to expand the `certification_record.action_code` CHECK enum (mirrors the DBCP-1q-D pattern that added `type_incoherence_no_active_anchor` to the `catalog_state_reason_code` CHECK). |

The cost of option B is one ALTER CONSTRAINT — already a well-rehearsed pattern in DBCP-1q-D. The benefit is a cleanly separable ledger event class that future audits (and the L-node semantic-verdict gate) can read without ambiguity. **Go with B.**

### 4.2 New action_code DDL (DBCP `1q-G` candidate — author when this design lands)

```sql
ALTER TABLE contract.certification_record
  DROP CONSTRAINT certification_record_action_code_chk;
ALTER TABLE contract.certification_record
  ADD CONSTRAINT certification_record_action_code_chk CHECK (
    action_code = ANY (ARRAY[
      'submit_for_review', 'certify', 'return_to_author', 'deprecate',
      'withdraw', 'supersede', 'archive', 'unarchive',
      'remediate_description', 'remediate_bf_semantics',
      'admit_bf_catalog', 'mark_bf_correction_required',
      'demote_bf_catalog', 'recertify_bf_catalog',
      'admit_bf_from_correction_required'   -- new (DBCP-1q-G)
    ])
  );
```

`CERTIFICATION_ACTION_CODES_SET` in `bc-core/src/registry/semantic-definitions/certification-record.ts` is also extended in the same commit as the endpoint implementation.

`from_state_code='draft'`, `to_state_code='certified'` is recorded explicitly on every row of this action_code; queries that need to count "operator-promoted draft-to-certified admissions" use the action_code alone. The catalog axis transition (`correction_required` → `certified_catalog`) is captured implicitly by reading the BF row's `catalog_state_code` after the update; if a future audit needs it explicitly on the ledger, add a paired column rather than overload the existing from/to_state_code.

## 5. Gate behavior

- **Full final-row G1–G8 projection is required.** No diff-only / "only validate the edited axis" projection. Mirrors `/correct-type` and `/correct-definition`'s posture; Path B (gate narrowing) was explicitly rejected by the operator in §11b of the cleanup plan and stays rejected here.
- **No override path.** Every failure is a hard 422 with the full gate verdict array. Operators may NOT pass an override rationale to bypass any gate.
- **CC data_type conflict returns 409** with a `problem+json` body containing the conflicting `cc_field_mapping` rows (mirror `/correct-type`'s 409 payload).
- **Gate failure response (422)** includes:
  - `type: 'https://barecount.dev/problems/validation-error'`
  - `title: 'Validation Error'`
  - `detail: "Cannot admit BF '<id>': projected SDA gates fail: <codes>. Amend the input and re-run."`
  - `gateResults`: full G1–G8 verdict array (so the operator sees exactly which gate failed and why).

## 6. Idempotency / concurrency

### 6.1 Idempotent re-admit

If a caller re-issues the same payload after a successful admission:

- The row is now `status_code='certified'` AND `catalog_state_code='certified_catalog'`, so the §3.3 precondition `(status_code='draft' AND catalog_state_code='correction_required')` **fails**.
- The endpoint returns **409 `already_admitted`** rather than 200 OK.
- Rationale: 200 OK on the re-call would imply "no-op" which is silently misleading — the caller likely intends a state change they cannot achieve. 409 with a clear `current_state` payload tells the caller "you tried to admit a row that's already admitted; if you need a re-certify, use `/correct-definition` or `/correct-type` or author a new endpoint for that case."

### 6.2 Concurrency guard

- Read the row inside the transaction, NOT before opening it (avoids stale-read race).
- The UPDATE statement carries an explicit `WHERE status_code='draft' AND catalog_state_code='correction_required'` predicate; row-level lock is acquired implicitly by the UPDATE.
- If UPDATE returns 0 rows (another writer changed the row between SELECT and UPDATE inside the same transaction, e.g. via `/correct-type` racing), the transaction aborts with **409 `catalog_state_conflict`**.
- No SELECT FOR UPDATE — the UPDATE-with-predicate guard is sufficient and is the same pattern used by `/correct-type` and `/remediate-semantics`.

### 6.3 Audit-row uniqueness

There is no unique constraint on `(primitive_type, primitive_id, action_code)` in `certification_record`. The same row may legitimately accumulate multiple `admit_bf_from_correction_required` ledger entries over its lifetime (e.g. if it's later demoted and re-admitted). No de-duplication is performed; the audit chain is by design append-only.

## 7. First use case — `iso20022_camt_xchg_rate`

This endpoint is motivated by `iso20022_camt_xchg_rate`. The first apply will be this single row.

### 7.1 Pre-state (verified at design time)

| field | value |
|---|---|
| field_id | `019d773a-0b4e-72ed-bc85-a813e314ad3c` |
| status_code | `draft` |
| catalog_state_code | `correction_required` |
| catalog_state_reason_code | `type_incoherence` |
| representation_term / data_type | `Text` / `number` |
| definition_standard | `ISO_20022` |
| standard_ref / semantic_family / unit_type_code | NULL / NULL / NULL |
| cc_count | 0 |
| existing ledger | exactly 1 row (`mark_bf_correction_required`, draft → draft, DBCP-1q-A) |

### 7.2 Proposed admission payload (from the A2 evidence packet, `bc-core@cea5695`)

```json
{
  "definition": "Foreign exchange rate used to convert an amount between two currencies in an ISO 20022 camt.053 bank-to-customer statement: the multiplier applied to the source-currency amount (SrcCcy) to obtain the target-currency amount (TrgtCcy), expressed as a BaseOneRate decimal per CurrencyExchange (CcyXchg) -> XchgRate.",
  "definitionStandard": "ISO_20022",
  "standardRef": "ISO 20022 camt.053 BankToCustomerStatement: CurrencyExchange (CcyXchg) -> XchgRate, typed BaseOneRate. See https://www.iso20022.org/iso-20022-message-definitions?search=camt.053",
  "semanticFamily": "measure-ratio",
  "unitTypeCode": "ratio",
  "representationTerm": "Rate",
  "dataType": "number",
  "rationale": "ISO 20022 exchange-rate vocabulary is expected context-engine lookup vocabulary for bank statement / FX / cash-management ingestion. Source-backed with verbatim BaseOneRate definition and verbatim CurrencyExchange parent structure (per A2 evidence packet bc-core@cea5695). cc_count=0 today; bounded-domain admission per §11b sub-cohort A2.",
  "sourceEvidence": [
    {
      "sourceType": "ISO_20022",
      "sourceRef": "camt.053 BankToCustomerStatement → CurrencyExchange → XchgRate (BaseOneRate)",
      "sourceUrl": "https://www.iso20022.org/iso-20022-message-definitions?search=camt.053",
      "citationNote": "BaseOneRate verbatim: 'Rate expressed as a decimal, eg, 0.7 is 7/10 and 70%.' CurrencyExchange verbatim: 'Set of elements used to provide details on the currency exchange.' Children: SrcCcy, TrgtCcy, UnitCcy, XchgRate, CtrctId."
    }
  ]
}
```

### 7.3 Expected post-state (after the apply)

- `status_code='certified'`, `catalog_state_code='certified_catalog'`, `catalog_state_reason_code=NULL`
- 4 SDA columns + type pair + definition all set as per payload
- one new `certification_record` row: `action_code='admit_bf_from_correction_required'`, from='draft', to='certified', `gate_results_json` showing G1–G8 all pass
- aggregate deltas: `correction_required` 12 → 11; `certified_catalog` 1,655 → 1,656; `admit_bf_from_correction_required` 0 → 1; all other catalog/lifecycle counts unchanged

### 7.4 Why `iso20022_camt_xchg_rate` is the right first row

- Zero CC bindings: zero downstream blast radius if the apply produces an unexpected state.
- Single-row apply (not a cohort) — minimal probe.
- Operator-approved evidence packet already exists (`bc-core@cea5695`).
- Halted apply audit (`bc-core@397d9b3`) provides the precise endpoint contract that this new endpoint must NOT inherit (the `/remediate-semantics` `status_code='certified'` precondition).

## 8. Foundation invariant analysis

| Invariant | This endpoint's behaviour |
|---|---|
| **I. Meaning is evaluated once** | The full G1–G8 evaluation happens exactly once per call, on the projected post-update row, inside the same transaction as the write. No earlier "meaning evaluation" is replayed. |
| **II. Object ordering is fixed** | The atomic act is `(certification_record INSERT, business_field UPDATE)` paired. Order is fixed: ledger first, then row. (Same as DBCP-1q-D / §12 pattern.) |
| **III. All state is immutable** | The prior `mark_bf_correction_required` ledger row is **not** mutated; it stays on the row as historical evidence. The new admission row is appended. |
| **IV. All references are explicit** | The new ledger row references `primitive_id=<fieldId>`, `from_state_code='draft'`, `to_state_code='certified'`, plus the full `gate_results_json` snapshot. The BF row references `certification_record_id` of the new admission row. |
| **V. Evaluation is non-replayable** | Each call generates a fresh `catalog_review_run_uid` (`d408-admit-<ISO timestamp>`). Re-running the same payload re-evaluates gates from scratch; no cached verdicts. |
| **VI. Evidence is emitted, not inferred** | The `sourceEvidence[]` array, the `rationale`, and the full G1–G8 snapshot are persisted on the ledger row. No downstream consumer needs to *reconstruct* "why was this BF admitted" — the proof is on disk. |

**Repair-location classification (per CLAUDE.md Foundation Gate, A–F shorthand):**

- **B (contract semantics)** — adds a new admission boundary for the `(draft, correction_required)` state pair that the existing contracts do not cover.
- **D (evaluation boundary implementation)** — extends the BF service with a new atomic write path; no metric / canonical engine touched.

**Why not other locations:**

- **A (source reality / admission boundary)** — N/A: this is platform vocabulary admission, not source data admission.
- **C (mapping / binding)** — no `cc_field_mapping` mutation in this endpoint.
- **E (storage / projection)** — no schema change beyond the `action_code` CHECK enum addition (which is additive, forward-only).
- **F (read model / diagnostics)** — no read-model change.

**Hard rules respected:**

- No lower-layer compensation for upper-layer semantic gaps (no SDG / fact / read-filter tweaks).
- No fact-shape-tied formulas (N/A — endpoint mutates BF only).
- No DB row hand-edits (this endpoint replaces hand-edits as the governed path).
- Reads do not trigger evaluation (BF row read inside tx triggers re-evaluation; that's part of the atomic act, not a side-effect read).
- If the projected row would violate Foundation, the endpoint returns 422 with the violation rather than performing the write.

## 9. Rollout sequence

Strictly ordered. Each step ends in a fresh checkpoint and (where applicable) commit.

| # | Step | Output |
|---|---|---|
| 1 | **Design approval** (this artifact). Operator reviews §3–§8; raises objections or approves. | Approval recorded in DevHub session / checkpoint. |
| 2 | **DBCP-1q-G** — additive CHECK enum expansion for `certification_record.action_code` adding `admit_bf_from_correction_required`. Mirrors DBCP-1q-D shape (forward + revert SQL pair, idempotent DROP+ADD CONSTRAINT, no other DDL). | bc-core forward + revert SQL files; bc-docs-v3 verification plan. |
| 3 | **Service implementation** — `AdmitFromCorrectionRequiredDto`, service method `admitFromCorrectionRequired`, repo method `admitBfFromCorrectionRequiredWithAuditTx`, controller `@Post(':fieldId/admit-from-correction-required')`. Extends `bf-correction.helper.ts` only if a new pure helper is needed (e.g. rationale length validator). | bc-core src change + unit tests covering refusal paths (404, 422 status-code, 422 catalog-state, 409 cc-conflict, 422 gate-fail) + 1 happy path. |
| 4 | **Focused tests** — refusal-path coverage exactly matches the §3.3 table; happy path mocked at repo level (mirrors `bf-correction.service.spec.ts`). | bc-core test files added; `npx vitest run` clean. |
| 5 | **Dry-run / probe on the ISO row** — author a probe script (mirrors `apply-d408-iso-xchg-rate-governed-uplift.mjs`) that posts the §7 payload, expects 200, verifies post-state, and writes the audit JSONL. | bc-core probe script + audit. |
| 6 | **Apply ISO row** — execute the probe in live APPLY mode. | DB state: `correction_required` 12 → 11; `certified_catalog` 1,655 → 1,656; new `admit_bf_from_correction_required` ledger row. |
| 7 | **Reconcile** — update plan §11b sub-cohort A2 disposition table to record the admission and close the open item. | bc-docs-v3 plan amendment commit. |

Steps 2 and 3 may be authored in the same bc-core commit (DBCP + service code + tests) since the service code depends on the CHECK enum extension, but the SQL must be applied before the service code is exercised against real data.

## 10. Explicit non-goals

- **NOT** a bulk admission endpoint. Single-row only. No batch payloads, no "admit all matching predicate" mode.
- **NOT** for `candidate_import` rows. The precondition is `catalog_state_code='correction_required'`, full stop. Candidates go through the existing certify chain.
- **NOT** for OAGIS scrape rows without source evidence. The `sourceEvidence[]` array is required and validated for non-empty content; operator review is the human approval gate.
- **NOT** a bypass for §12. `/remediate-semantics` keeps its `status_code='certified'` precondition. This endpoint handles a different state pair, not the same one with a weaker gate.
- **NOT** a return to bulk standards-directory import. Each admission is one row, with one approved evidence payload, with one ledger row, after a full G1–G8 pass.
- **NOT** an override mechanism. No `override_rationale` field in the body. Gates are non-overridable on this endpoint (mirrors `/correct-type` and `/correct-definition` posture).
- **NOT** in scope: changing the `correction_required` → `certified_catalog` transition for rows that are already `status_code='certified'` (those go through `/correct-definition` / `/correct-type`).
- **NOT** in scope: the 11 NEEDS_EVIDENCE definition rows, the 14 demoted rows, the 4 A1 BFs, or any A1 mapping. Those are on their own tracks per the §11b sub-cohort split.

## 11. References

- ADR: `bc-docs-v3/docs/adrs/ADR-1ce490.md` (D408)
- Plan: `bc-docs-v3/.../2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md` (§11b sub-cohort A2)
- Related ADR: `bc-docs-v3/docs/adrs/ADR-a49413.md` (§12 remediate-semantics)
- A2 evidence packet: `bc-core@cea5695`
- A2 halted apply: `bc-core@397d9b3`
- A1 Step C apply: `bc-core@1902d5d` (template for atomic UPDATE+INSERT)
- A1 Step D apply: `bc-core@b23122d` (template for /correct-type sequencing)
- Profiles enum: `bc-core/src/registry/semantic-definitions/profiles.ts`
- Gates matrix: `bc-core/src/registry/semantic-definitions/gates.ts`
- Foundation invariants: `bc-docs-v3/docs/foundation/the-invariants.md`
- Active task: TSK-eae922
