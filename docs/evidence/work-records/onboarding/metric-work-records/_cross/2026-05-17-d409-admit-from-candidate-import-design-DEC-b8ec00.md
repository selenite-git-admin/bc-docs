---
title: "D409 — `admit-from-candidate-import` endpoint design"
date: 2026-05-17
authority: DEC-b8ec00 (D409 — BF-BO Catalog Expansion Factory)
adr: bc-docs-v3/docs/adrs/ADR-b8ec00.md
sop: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md
modeling_policy: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-credit-facility-modeling-policy.md
predecessor_decision: DEC-1ce490 (D408 — contract.business_field is the certified BF-BO catalog)
gap_report: bc-core/scripts/audit-output/d409-cc-credit-execute-slice-1-governed-path-gap-2026-05-17.md
session: SES-2be973
type: endpoint-design
status: proposed
version: 0.1
governing_invariants:
  - I (Meaning is evaluated once)
  - IV (All references are explicit)
  - VI (Evidence is emitted, not inferred)
---

# D409 — `POST /api/business-fields/:id/admit-from-candidate-import`

A standing D409 admission endpoint that closes the `candidate_import → certified_catalog` edge for a brand-new SDA-backed business field. Without this endpoint, every D409 admission must either bypass governance (forbidden) or author a one-shot DBCP (does not scale).

This note is design only. It does not author code, SQL, or DBCP-1q-I (the CHECK-enum extension below). Implementation is a separate session after operator approval.

---

## 1. Problem statement

D409 Pilot 1 Slice 1 (`gap report`, bc-core@15000ef) confirmed that the factory can produce defensible `ADMIT_READY` recommendations but cannot execute any of them through existing governed paths:

| Operation | Path | Status |
|---|---|---|
| A — create BF | `POST /business-fields` → `createField` | ✔ governed (lands in `status_code='draft'`, `catalog_state_code='candidate_import'` per schema default) |
| B — certify status | `POST /business-fields/:id/certify` → `certifyField` (CR-QG-001) | ✔ governed (flips `status_code` only; **does not touch** `catalog_state_code`) |
| **C — promote `candidate_import` → `certified_catalog`** | — | **✘ NOT GOVERNED** |
| D — add cc_field_mapping | `POST /onboarding/cc/:contractId/field-mappings` | ✔ governed (`filterJson` supported), but D408 GS-3 guard at `cc-onboarding.service.ts:648-649` refuses non-`certified_catalog` BFs — unreachable until C exists |

The 1,651 rows currently in `certified_catalog` were promoted by a one-time D408 migration, not by a standing endpoint. Every future D409 admission (asset depreciation, ISO 20022 modeling, tax, treasury, payroll, derivatives) hits the same wall. The factory recommendation path produces packets, the modeling-policy decision is settled, but the apply edge is missing.

The legacy `POST /business-fields/:id/certify` is insufficient for three reasons:

1. It flips only `status_code`, leaving `catalog_state_code='candidate_import'`. GS-3 then blocks every binding.
2. It carries no D408 ledger semantics — no `certification_record` row with `action_code='admit_bf_catalog'` (or equivalent), so the D408 catalog admission audit trail is empty for the row.
3. It does not require the SDA evidence body (`semanticFamily`, `unitTypeCode`, `definitionStandard`, `standardRef`) that the D409 modeling discipline mandates for a defensible admission.

GS-3 is correct — it must not be relaxed. The fix is to define the missing admission edge.

---

## 2. Relationship to existing `/admit-from-correction-required`

`POST /business-fields/:id/admit-from-correction-required` (D408 §12, 1q-G) and the proposed `POST /business-fields/:id/admit-from-candidate-import` are siblings, not duplicates. The differences are load-bearing for the audit trail.

| Aspect | `/admit-from-correction-required` (D408) | `/admit-from-candidate-import` (D409, proposed) |
|---|---|---|
| Source state | `status_code='draft'` AND `catalog_state_code='correction_required'` | `status_code='draft'` AND `catalog_state_code='candidate_import'` |
| Target state | `status_code='certified'` AND `catalog_state_code='certified_catalog'` | `status_code='certified'` AND `catalog_state_code='certified_catalog'` |
| Used for | Repair: a row was previously flagged `correction_required` (e.g. weak definition, type-incoherence, ISO 20022 shape question); the operator has authored a correction and now re-admits | Admission: a brand-new BF was created via `POST /business-fields`, has full SDA evidence, has never been admitted before |
| Evidence focus | Correction evidence — what changed, why the prior reason_code no longer applies | Source evidence — standards-tier citations (US-GAAP XBRL / IFRS / XBRL / OAGIS / ISO 20022) on first-time admission |
| Anchor evidence requirement | BO membership OR alias OR `cc_field_mapping` reference *likely* exists (the row was previously certified or has prior context) | Brand-new BF — anchor evidence may not exist yet; the standards-tier citation is the anchor |
| Action code (ledger) | `admit_bf_from_correction_required` (D408) | `admit_bf_from_candidate_import` (NEW, this design) |
| `from_state_code` in `certification_record` | `'correction_required'` | `'candidate_import'` |
| Risk profile | Lower: row already passed an earlier admission cycle | Higher: first admission; SDA gates are the only filter |
| Caller | D408 cleanup workflows (cc_field_mapping issues, ISO 20022 modeling fixes) | D409 factory workflows (new BFs from cc__credit, asset, ISO 20022 modeling, etc.) |

**Why separate, not one overloaded endpoint:**

1. **Audit clarity (Invariant VI — evidence emitted, not inferred).** Querying "how many BFs were admitted from a correction history vs admitted fresh from D409 discovery?" must be answerable from the ledger alone, not by joining against prior rows. Separate action codes make this a one-table query.
2. **Operator intent.** The two endpoints correspond to different operator intentions — one says "I am repairing a row I previously flagged," the other says "I am admitting new vocabulary." Conflating them obscures intent in incident reviews.
3. **Gate emphasis.** `/admit-from-correction-required` may relax certain duplicate checks (the row already existed in some form). `/admit-from-candidate-import` cannot — it is the first-admission moment and must run the full duplicate / collision gate.
4. **Future divergence.** If D409 grows additional first-admission semantics (e.g. requiring a parent BO membership decision before admit), those constraints belong on the candidate-import path, not bolted onto the correction path.

A single overloaded endpoint would either gradually drift (the gates branch on source state) or become a misnomer that does not reflect the operator's act. Two endpoints with one action code each is the cheaper long-term shape.

---

## 3. Proposed endpoint contract

### 3.1 Route

```
POST /api/business-fields/:id/admit-from-candidate-import
```

`@PlatformOnly()`. Requires platform-admin JWT (same authorisation as the rest of the `business-fields` controller).

### 3.2 Path parameter

- `:id` — `business_field.field_id`, UUID. Parsed via `ParseUUIDPipe`. Returns `400` if not a UUID.

### 3.3 Request body

```ts
{
  // Definition and standard provenance (D408 SDA G1-G8)
  definition: string;                  // ≥ 20 chars; non-templated
  definitionStandard: 'BARECOUNT' | 'COSO' | 'IFRS' | 'IIA' | 'ISO_20022' | 'OAGIS' | 'US_GAAP' | 'US_GAAP_XBRL';
  standardRef?: string | null;         // Required when definitionStandard is external (not BARECOUNT)

  // SDA semantic columns (D366 enums)
  semanticFamily: string;              // D366 enum value (e.g. 'measure-currency', 'identifier', 'temporal-date')
  unitTypeCode?: string | null;        // Required when family.compatible_unit_types != null (D366 matrix)
  representationTerm?: string | null;  // ISO 11179 representation term

  // Type metadata (used to validate against existing structural columns; row's own data_type is immutable post-create)
  dataType: 'string' | 'number' | 'integer' | 'date' | 'timestamp' | 'boolean' | 'code';

  // Audit
  rationale: string;                   // ≥ 40 chars, free text
  sourceEvidence: Array<{
    type: 'xbrl-us-gaap' | 'ifrs' | 'oagis' | 'iso20022' | 'us-gaap-sda' | 'internal-bo-membership' | 'internal-cc-reference' | 'internal-sda-projection' | 'internal-alias';
    citation: string;                  // Element name / paragraph / xpath / etc.
    location?: string;                 // Where in the source the citation was found
    scope?: string;                    // One-line scope statement
  }>;
}
```

Notes:

- `name`, `function`, `objectClass`, `property`, `dataType`, `piiClassification` are **immutable** after `POST /business-fields`. This endpoint refuses (422) if the request body's `dataType` does not match the row's existing `dataType`. This makes the endpoint idempotent under retry and prevents accidental type changes at admission.
- `representationTerm` is allowed to be supplied here because the legacy `createField` does not have a strong representation-term gate; this endpoint fills it in atomically with admission. Once admitted, representation_term is immutable per the existing certified-field rules.
- `sourceEvidence` is at minimum one item. A `BARECOUNT`-only admission with no external citation is allowed but is **never** sufficient on its own for a brand-new BF — the gate matrix (§5) will refuse if `definitionStandard='BARECOUNT'` AND no internal-tier anchor evidence is present.

### 3.4 Preconditions (atomic — checked inside the same transaction as the update)

1. JWT carries `platform_admin` (matches `@PlatformOnly()` semantics on the controller).
2. Row exists (404 if not).
3. `status_code = 'draft'` (422 if not).
4. `catalog_state_code = 'candidate_import'` (409 `catalog_state_conflict` if not; in particular, 409 if already `certified_catalog`).
5. `archived_at IS NULL` (422 if not).
6. `sourceEvidence.length >= 1` (400 if not).
7. `rationale.length >= 40` (400 if not).
8. All enum values (`definitionStandard`, `semanticFamily`, `unitTypeCode`, `representationTerm` against ISO 11179 enum, `dataType`) in their respective allowed sets (400 if not).
9. `dataType` in body matches `business_field.data_type` in the row (422 if mismatch — see §3.3 note).
10. No duplicate BF name and no normalised-collision (D408 dedup semantics; 409 if a `certified_catalog` BF with the same `name` exists).
11. No `cc_field_mapping` row already binds this `field_id` (sanity — should be impossible at `candidate_import`, but defensive: 409 if any).
12. Full projected G1–G8 SDA gate pass (§5).

### 3.5 Atomic effect (single transaction)

```sql
-- Pseudo-SQL; real implementation in Drizzle / TS service
UPDATE contract.business_field
SET
  status_code = 'certified',
  catalog_state_code = 'certified_catalog',
  catalog_state_reason_code = NULL,
  catalog_state_reason_text = :rationale,
  catalog_reviewed_at = NOW(),
  catalog_review_run_uid = :session_uid,
  definition = :definition,
  definition_standard = :definitionStandard,
  standard_ref = :standardRef,
  semantic_family = :semanticFamily,
  unit_type_code = :unitTypeCode,
  representation_term = COALESCE(:representationTerm, representation_term),
  gate_signals_json = :gate_signals,           -- G1–G8 verdicts
  gate_signals_at = NOW(),
  gate_signals_row_hash = :row_hash,
  admission_rule_version_at_certify = :rule_version,
  certification_record_id = :new_cr_id,
  archived_at = NULL,
  updated_by_name = :operator_name,
  updated_at = NOW()
WHERE field_id = :id
  AND status_code = 'draft'
  AND catalog_state_code = 'candidate_import';

-- If the UPDATE returns zero rows, raise 409 catalog_state_conflict.

INSERT INTO contract.certification_record (
  certification_record_id, primitive_type, primitive_id,
  action_code, from_state_code, to_state_code,
  rationale_text, evidence_json, certifier_name, created_at
) VALUES (
  :new_cr_id, 'business_field', :id,
  'admit_bf_from_candidate_import',          -- §4 below
  'candidate_import', 'certified_catalog',
  :rationale, :evidence_json, :operator_name, NOW()
);
```

`status_code` and `catalog_state_code` flip in the same UPDATE — no half-state is ever visible. The `certification_record` row is the audit ledger for the admission and references `:new_cr_id` already written into `business_field.certification_record_id`.

### 3.6 Response

```ts
// 200 OK
{
  fieldId: string;
  name: string;
  statusCode: 'certified';
  catalogStateCode: 'certified_catalog';
  certificationRecordId: string;
  gateResults: Array<{ gate: 'G1' | 'G2' | ... | 'G8'; passed: true; detail: string; }>;
  admittedAt: string;     // ISO 8601 timestamp
}
```

### 3.7 HTTP status taxonomy

| Status | When |
|---|---|
| `200 OK` | Admission succeeded |
| `400 Bad Request` | Body malformed; enum violation; rationale too short; `sourceEvidence` empty |
| `401 Unauthorized` | JWT missing/invalid |
| `403 Forbidden` | JWT not platform-admin |
| `404 Not Found` | `:id` does not exist |
| `409 Conflict` | `catalog_state_code != 'candidate_import'` (covers "already admitted" — never silent success); name collision; row currently has cc_field_mapping |
| `422 Unprocessable Entity` | `status_code != 'draft'`; `archived_at IS NOT NULL`; `dataType` mismatch with row; any G1–G8 gate failure (gate verdicts in body) |
| `500 Internal Server Error` | DB / transaction / bc-ai error not classifiable above |

---

## 4. Ledger / action_code decision

Recommend a **new** action_code: `admit_bf_from_candidate_import`.

Why not reuse:

| Existing action_code | Why not for this endpoint |
|---|---|
| `admit_bf_catalog` | Historical / backfill admission. The 1,651 existing rows under this code came from a one-time D408 migration. Reusing it would muddle "migration-era admissions" with "factory-era admissions" in every audit, and would prevent a clean count of factory throughput. |
| `admit_bf_from_correction_required` | Different `from_state_code` (`correction_required` vs `candidate_import`). The CHECK constraint on `certification_record` (per D408) couples `action_code` to a particular `(from_state, to_state)` transition. Mis-pairing breaks the constraint. Also conflates correction history with first admission (§2). |
| `certify` | Pre-D408 legacy action; carried only the `status_code` transition. Reusing it inside a `catalog_state_code` admission ledgers a misleading audit row. |
| `recertify_bf_catalog` | Reserved for moving an already-`certified_catalog` row back through certify (e.g. SDA uplift). Wrong source state. |

**DBCP-1q-I — CHECK enum extension (prerequisite, not authored here).** The `certification_record.action_code` CHECK constraint must be extended to allow `'admit_bf_from_candidate_import'`. The DBCP pattern matches DBCP-1q-G (which added `admit_bf_from_correction_required`):

- Authored as a `*.sql` forward + `*.sql` reverse + a verification-plan markdown under `bc-docs-v3/docs/onboarding/metric-work-records/_cross/`.
- Additive only — does not remove any existing enum value.
- Requires explicit user approval per CLAUDE.md DB Change Protocol.

The endpoint code must not ship until DBCP-1q-I is applied, otherwise every admission will fail at the `INSERT certification_record` step.

---

## 5. Gate behavior (G1–G8)

The endpoint runs the **full** projected G1–G8 SDA gate matrix on the post-update row state. No diff-only optimisations; no overrides; no skip-on-AI-unavailable shortcuts at admission (legacy bulk-certify allowed this for backfill, but first admission is not backfill).

| Gate | Concern | Source of truth |
|---|---|---|
| G1 | Definition non-trivial (≥ 20 chars, non-templated, not the OAGIS placeholder `"<x> from OAGIS undefined"`) | D408 §SDA G1 |
| G2 | ISO 11179 naming (snake_case, valid `object_class` + `property` pair) | D408 §SDA G2 |
| G3 | Type / representation-term coherence | D366 matrix |
| G4 | Semantic family / unit_type_code matrix (`family.compatible_unit_types`) | D366 |
| G5 | External-standard ref required when `definition_standard ≠ 'BARECOUNT'` | D408 §SDA G5 |
| G6 | PII classification AI cross-check (call `bc-ai` `/api/bf-pii-classify`); fail-closed on disagreement | D288 / D408 |
| G7 | Semantic dedup AI check (call `bc-ai` `/api/bf-dedup`); fail-closed on `red`; allow with warning on `amber`; pass on `green` or `unverified` | D408 G7 |
| G8 | Anchor evidence: at least one item in `sourceEvidence[]` is **standards-tier** (`xbrl-us-gaap | ifrs | oagis | iso20022 | us-gaap-sda`) when `definitionStandard ≠ 'BARECOUNT'`. For `BARECOUNT`-only rows, at least one internal-tier anchor (BO membership planned, alias, SDA projection) is named in the rationale | D409 SOP §4.3 |

`gate_signals_json` records each gate's verdict + detail and is persisted on the row. On any blocker, the endpoint returns `422` with the failed gate(s) in the response body and **does not write**.

**No override path.** D366 / DEC-804874 §4-style overrides are not allowed at admission. If a row cannot satisfy G1–G8, the operator must revise the request body or accept that the row stays `candidate_import` until evidence is sourced — the same discipline D409 SOP §9 already mandates.

---

## 6. Idempotency / concurrency

- **Predicate guard.** The `UPDATE` includes `AND status_code='draft' AND catalog_state_code='candidate_import'` in the `WHERE`. If a concurrent caller has already admitted the row, the `UPDATE` matches zero rows.
- **Zero-row update → 409.** The service maps a zero-row result to `409 catalog_state_conflict`. **Never** silent success. The caller learns explicitly that someone else (or a prior retry) already moved the row.
- **No "already admitted, return 200" shortcut.** The legacy bulk-certify path allowed this for backfill; the D409 admission moment is a discrete operator act, and treating a second call as a no-op invites accidental double-attribution in audit. The operator must explicitly read the new row state (via `GET /business-fields/:id`) if curious — that is a separate, idempotent call.
- **No request idempotency key required.** The catalog-state predicate guard provides the same protection in fewer moving parts.

---

## 7. First D409 use case — cc__credit slice

Once this endpoint ships, the two BFs proposed in the D409 admission+rebind packet (`bc-core@b628d9c`) are the first apply targets:

| Order | BF | source evidence |
|---|---|---|
| 1 | `credit_facility_amount_outstanding` | `us-gaap:LineOfCreditFacilityAmountOutstanding` (ASC 470-10-50) |
| 2 | `credit_facility_maximum_borrowing_capacity` | `us-gaap:LineOfCreditFacilityMaximumBorrowingCapacity` (ASC 470-10-50); axis `us-gaap:LineOfCreditFacilityAxis` / member `us-gaap:RevolvingCreditFacilityMember` is carried at the `cc_field_mapping.filter_json` level per the modeling policy |

Each BF apply is a three-call ceremony (operator-driven):

1. `POST /business-fields` — create the BF (lands in `candidate_import`).
2. `POST /business-fields/:id/admit-from-candidate-import` — **this new endpoint** — admits to `certified_catalog` with full SDA evidence.
3. `POST /onboarding/cc/:contractId/field-mappings` — add the paired CF rebinds (GS-3 now passes).

After both BFs are admitted, the four cc_field_mapping rebinds run through `addMappings`:

| CF | target BF | `filterJson` |
|---|---|---|
| `drawn_credit_facility_amount` | `credit_facility_amount_outstanding` | `null` (aggregate) |
| `revolving_credit_drawn` | `credit_facility_amount_outstanding` | `{ "facility_type": "revolving" }` |
| `total_credit_facility_limit` | `credit_facility_maximum_borrowing_capacity` | `null` (aggregate) |
| `revolving_credit_limit` | `credit_facility_maximum_borrowing_capacity` | `{ "facility_type": "revolving" }` |

### 7.1 Packet correction — `resolutionRuleCode`

The prior admission+rebind packet (`bc-core@b628d9c`) listed `resolutionRuleCode='identity'`. `'identity'` is not in the `CcFieldMappingDto` enum, which is:

```
sum | latest | assert_equal | count_distinct | count_where_not_null | compute
```

For the four credit-facility amount mappings, the correct rule is **`'sum'`** — the source may emit multiple facility rows per reporting boundary, and the canonical value is the sum across the filter (or across all facility types when no filter applies). This correction does not require re-running the modeling-policy decision; it is a mechanical DTO conformance fix. The next admission+rebind packet (authored after this design is approved) should reflect `'sum'`.

If the operator later determines that a different aggregation is correct for a specific source system (e.g. the source emits already-aggregated balances and `latest` is correct, or `assert_equal` should refuse multi-row inputs), that is a per-tenant binding decision and lives on the `cc_field_mapping` row, not on the BF.

---

## 8. Foundation invariant analysis

**Repair-location classification (CLAUDE.md §Foundation Invariant Check).** B + D.

- **B (contract grammar).** The endpoint is a new admission boundary — a B-layer primitive that declares what it means for a brand-new BF to acquire `certified_catalog` status under D408's catalog vocabulary.
- **D (evaluation boundary implementation).** The endpoint itself is the implementation of that boundary — the runtime that enforces the gate matrix and writes the atomic transition.
- **Not C** (mapping). The C-layer rebinds remain on the existing `addMappings` endpoint; the design does not touch them.
- **Not E** (storage). The schema columns already exist; no new columns are proposed.
- **Not F** (read model). No diagnostic surfaces are added.

**Invariant alignment:**

| Invariant | How the endpoint honours it |
|---|---|
| I — Meaning is evaluated once | Admission is the single moment at which a new BF's meaning enters the certified catalog. The endpoint enforces full G1–G8; it does not allow meaning to be partially set and then patched in by subsequent calls. The legacy `certify` + `remediate-semantics` two-step lacked this property — meaning could be set after certification — and the new endpoint closes that drift |
| IV — All references are explicit | Every `sourceEvidence` item carries `type` and `citation` (and optionally `location` and `scope`). Free-form claims are not evidence. The ledger row records the evidence_json verbatim |
| VI — Evidence is emitted, not inferred | The certification_record row with `action_code='admit_bf_from_candidate_import'` is the emitted evidence of the admission event. Future audits do not need to reconstruct "did this row ever pass G1–G8?" — the gate_signals_json + evidence_json on the row + the ledger row are the proof |

**Anti-patterns the design refuses (D409 SOP §9 / modeling policy §7 / discipline rules):**

- **No standards-directory bulk import.** The endpoint admits one BF at a time. Bulk admission is explicitly out of scope (§10).
- **Agents recommend; endpoint admits.** The endpoint is the only place catalog_state_code flips to `certified_catalog` for first-admission rows.
- **No direct SQL promotion.** Even with this endpoint in place, the `UPDATE contract.business_field SET catalog_state_code='certified_catalog' WHERE field_id=$1` pattern remains forbidden — the endpoint runs the gates, writes the ledger, and is the *only* admission surface.
- **No LLM auto-certification.** Even when the D409 LLM trio (TSK-926c77) ships, it produces *recommendations*; the operator (or the operator-controlled apply script) invokes the endpoint.

---

## 9. Rollout sequence

Strict order. Each step is a separate operator session.

1. **Design approval.** Operator approves this note (or amends and re-approves).
2. **DBCP-1q-I — `action_code` CHECK enum extension.** Authored as forward `*.sql` + reverse `*.sql` + verification-plan markdown under `bc-docs-v3/docs/onboarding/metric-work-records/_cross/`. Adds `'admit_bf_from_candidate_import'` to the enum. Additive only. Requires explicit user approval before apply per CLAUDE.md DB Change Protocol.
3. **Implement endpoint in bc-core.**
   - New service method `StandardFieldService.admitFromCandidateImport(fieldId, body, certifier)`.
   - New repository method `StandardFieldRepository.admitFromCandidateImport(input)` with the predicate-guarded atomic UPDATE + ledger INSERT.
   - New DTO `AdmitFromCandidateImportDto` reusing `RemediateBfSemanticsDto` shape where applicable + adding `definition`, `representationTerm`, `dataType`, `rationale`, `sourceEvidence`.
   - New controller route `@Post(':fieldId/admit-from-candidate-import')` on `StandardFieldController`.
   - Reuse `runStructuralGates`, `callBfPiiClassify`, `callBfDedup` from the existing certify path.
   - Reuse the `certification_record` insert helper.
4. **Tests.**
   - Unit: gate matrix per gate (G1–G8 each with one passing + one failing case).
   - Unit: predicate-guard 409 path (concurrent admission).
   - Unit: enum / rationale / sourceEvidence body validation.
   - Integration: full create → admit-from-candidate-import → addMappings ceremony on a test BF.
   - Idempotency: second call returns 409 (not 200).
5. **First apply — cc__credit slice.** Use the endpoint for `credit_facility_amount_outstanding`, then for `credit_facility_maximum_borrowing_capacity`. Verify 14 D408 invariants after each step.
6. **Mapping rebind packet update.** Author the corrected admission+rebind packet using `resolutionRuleCode='sum'` (§7.1) for the four cc_field_mapping inserts. Apply via the existing governed mapping endpoint.
7. **Re-evaluate the 7 downstream MCs** that reference the four rebound CFs via `contract.chain_status` SSOT.

Each step is gated on the prior step's success and operator approval. Steps 5–7 happen one cc_field_mapping at a time per SOP §3.

---

## 10. Non-goals

The proposed endpoint **does not**:

- Provide a bulk `candidate_import → certified_catalog` promotion API. There is no batch shape; one-BF-per-call is the contract. Bulk admission would re-introduce the coverage-shaped failure mode D408 and D409 were built to eliminate.
- Bypass the D409 evidence packet. The endpoint runs after a packet has emitted `ADMIT_READY` and the operator has approved the apply. The endpoint itself does not consume the packet — it consumes the body the operator constructs from the packet.
- Replace the legacy `POST /business-fields/:id/certify` endpoint. That endpoint remains as the `status_code='draft' → 'certified'` lifecycle move and may be invoked separately on rows that never need catalog admission (a rare case but reserved).
- Admit non-source-backed rows. Without standards-tier or named internal-tier anchor evidence in `sourceEvidence[]`, G8 fails and the endpoint returns 422.
- Admit rows with bad names or invalid `object_class` / `property`. Those checks run at `POST /business-fields` (createField) time; the endpoint refuses to admit a row that would not have passed create if re-validated.

---

## 11. References

- `Gap report (bc-core@15000ef)`
- [D409 SOP v0.1](2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md)
- [D409 agent prompt scaffold v0.1](2026-05-17-d409-agent-prompt-scaffold.md)
- [D409 credit-facility modeling policy v0.1](2026-05-17-d409-credit-facility-modeling-policy.md)
- `D409 cc__credit admission+rebind packet`
- [ADR-b8ec00](../../../../../governance/adrs/ADR-b8ec00.md) — D409
- [ADR-1ce490](../../../../../governance/adrs/ADR-1ce490.md) — D408
- [D408 admit-from-correction-required design](2026-05-17-d408-admit-from-correction-required-design-DEC-1ce490.md) — sibling endpoint
- CLAUDE.md §Foundation Invariant Check, §Database Change Protocol
- [the-invariants.md](../../../../../foundation/the-invariants.md)

### Changelog

| Version | Date | Note |
|---|---|---|
| 0.1 | 2026-05-17 | Initial design (SES-2be973). Proposed; not implemented. Awaits operator approval + DBCP-1q-I. |
