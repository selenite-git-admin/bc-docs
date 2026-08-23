---
uid: DEC-cbc07b
title: "Type Conformance Enforcement — Source Object through Metric Snapshot"
description: "Every field flowing through the chain (SO → AR → CO → MS) must conform to its Business Field's declared data_type; normalization happens at admission, not at metric evaluation"
status: proposed
date: 2026-04-15
project: bc-core
domain: contracts
decision_code: D331
authority: authoritative
refs:
  - type: decision
    uid: DEC-f66378
    label: "D292 — BO-Scoped BF Composition"
  - type: decision
    uid: DEC-d72560
    label: "D301 — Canonical Field as 3rd Contract Primitive"
  - type: decision
    uid: DEC-c0290f
    label: "D315 — Metric Evaluation Engine (late coercion, to be superseded)"
  - type: decision
    uid: DEC-4a8abb
    label: "D329 — MC Constant Value Propagation (related gap — data types carry end-to-end)"
  - type: document
    path: "docs/architecture/contract-chain-assembly.md"
    label: "Contract Chain Assembly (SO → AR → CO → MS flow)"
migrated_from: legacy v2 archive
devhub_registration: doc-registry indexed; decision-registry row absent (FILE_ONLY_UNEXPLAINED per Decision-Registration Integrity Audit 2026-06-22). Note PATH_MISMATCH context — the DevHub decision row DEC-4a8abb has title "Type Conformance Enforcement" with file_path docs/adrs/ADR-cbc07b.md, i.e. the registry tracks this decision under DEC-4a8abb but its own file_path correctly points here. File-side UID DEC-cbc07b is the authority used by inbound cross-references; preservation over re-mint per operator doctrine.
---

# Type Conformance Enforcement — Source Object through Metric Snapshot

> **Decision-registration integrity (2026-06-22).** Classified `FILE_ONLY_UNEXPLAINED` + part of the PATH_MISMATCH cluster in the [integrity audit](../../evidence/audits/implementation/devhub-decision-registration-integrity-audit-2026-06-22.md) §3.1–§3.2 and recorded in the [repair closeout](../../evidence/closeouts/implementation/devhub-decision-registration-integrity-repair-closeout-2026-06-22.md). The DevHub decision-registry row that carries this doctrine is UID `DEC-4a8abb` (title "Type Conformance Enforcement…"); its `file_path` correctly points here. Inbound cross-references use file-side UID `DEC-cbc07b` (D331); the registry's title/file_path correction cannot be performed via `devhub_decision_update` (no title or file_path field), and a direct DB write is out of scope. Content below is preserved verbatim per Foundation Invariant III.

## Context

The BareCount contract chain carries field values through six governed stages: Source Object (SO) → Admitted Record (AR) → Canonical Object (CO) → Metric Snapshot (MS). Each stage has contracts (SC, AC, OC, CC, MC) that govern structure, mapping, and evaluation. The `business_field.data_type` column declares the data type of every BF (number, date, timestamp, boolean, code, string).

**Today, BF.data_type is advisory, not enforced.** A field traverses the chain as the raw text it arrived as. Type coercion happens late (at metric evaluation, L7) via defensive `Number()` calls and D315 guardrails that reject non-numeric values in SUM/AVG aggregations.

### Observed failures caused by late coercion

During demo-selenite execution (proven 2026-04-15), the D315 metric engine rejected 8 MCs with this class of error:

```
Non-numeric values for 'sum_of_days_past_due_for_overdue_invoices' in SUM()
Non-numeric values for 'total_processing_time_for_invoices' in SUM()
```

Investigation revealed:
- SAP BSID (CustomerOpenItemSet) emits `DMBTR` as `"145272.42"` (string) — should be `number` per BF.data_type
- OC transform `direct` passes it through as text
- Admitted Record stores text
- Canonical Object stores text
- Metric engine coerces `"145272.42"` → `145272.42` (works)
- BUT for time-duration CFs mapped to timestamp BFs, the value `"2026-04-09"` flows as text; `Number("2026-04-09")` is `NaN`; SUM fails

The engine's rejection is **correct** but the diagnosis is at the wrong layer. Type errors should surface at L5 (admission), where they are data-quality signals, not at L7 where they look like formula bugs.

### Cross-source inconsistency

When multiple source systems map to the same BF, each may emit different shapes:

| BF | Source | Raw value | Current payload |
|---|---|---|---|
| `receivable_hdr_amount` | SAP DMBTR | `"145272.42"` | string |
| `receivable_hdr_amount` | Oracle INV_AMT | `145272.42` | number |
| `receivable_hdr_amount` | SFDC Amount__c | `"145272.42"` | string |

Downstream consumers (CC resolution rules, metric engine) must handle three shapes for the same BF. This is a leaky abstraction — the BF contract declares `data_type: number`, but the platform doesn't enforce it.

## Decision

### D331-R1: BF.data_type is the type authority

Every BF's `data_type` is authoritative and closed. Valid values: `number`, `integer`, `string`, `date`, `timestamp`, `boolean`, `code` (string with controlled vocabulary), `text` (unconstrained string). Every downstream stage (OC, AC, CC, MC) MUST conform to this type.

### D331-R2: OC transforms are typed

`observation_contract.field_mappings[].transform` is extended from free-form strings to a named function library with declared input/output types:

```yaml
# Current
transform: "direct"       # no type semantics
transform: "date_iso8601" # implied timestamp

# Target (D331)
transform:
  function: "to_number"        # fn name from transform library
  input_type: "string"         # what the source emits
  output_type: "number"        # MUST match target BF.data_type
  params: { decimal_sep: "." }  # optional
```

Transform library (initial set):
- `identity` — passthrough when source type already matches BF type
- `to_number` — coerce string → number (with locale-aware decimal separator)
- `to_integer` — string → integer (rejects fractional)
- `to_date_iso8601` — various date formats → ISO 8601 date string
- `to_timestamp_iso8601` — timestamp normalization
- `to_boolean` — string/code → boolean (with declared true/false set)
- `to_code` — trim + case-normalize + validate against master code table
- `to_text` — trim whitespace, preserve as string

### D331-R3: Admission validates + stores normalized values

`AdmissionContract.field_rules[]` gets a new rule type: `type_conformance`. For every field in OC field_mappings:

1. Apply the declared OC transform to the raw source value
2. Validate the transformed value matches target BF.data_type
3. On success: store the **normalized** (typed) value in `admitted_record.payload_json`
4. On failure: reject the record (existing rejection path), with reason `TYPE_COERCION_FAILED`

After admission, `admitted_record.payload_json` stores **typed JSON values** — numbers as numbers, dates as ISO strings, booleans as booleans. Raw source text is preserved only in `observed_record.raw_payload_json` for audit.

### D331-R4: Canonical resolution operates on typed values

`CanonicalEvaluationEngine` no longer coerces. Resolution rules act on typed values:
- `sum` requires type `number` or `integer` — type mismatch is a rejection, not a silent `Number()` attempt
- `latest` / `earliest` require `date` or `timestamp`
- `assert_equal` compares typed values (no string comparison for numbers)

### D331-R5: Metric engine defensive guardrails become no-ops

D315 guardrails (non-numeric value rejection, null/undefined rejection, finiteness check) stay in place as belt-and-suspenders but should **never trigger** in a type-conformant chain. Triggering them becomes a data-quality alert: the chain leaked a typed invariant.

### D331-R6: Chain integrity strengthens

The L5 check in ChainStatusService (`l5_ac_exists`) is extended to `l5_ac_enforces_types` — AC must declare `type_conformance` rules for every field in its source_references, matching the target BFs' data_types.

### D331-R7: Migration strategy — phased, not flag-day

1. **Phase 1:** Add transform library + DTO/schema changes, default transforms to `identity` for backward compatibility
2. **Phase 2:** Admission starts storing typed values where the transform is declared; untyped mappings still pass through as text
3. **Phase 3:** Run a one-time audit: for each active OC, propose a typed transform per field based on source SC type + target BF data_type. Human-review, apply via new OC versions.
4. **Phase 4:** AC versioning — each AC gets a new version with `type_conformance` rules for its source_references
5. **Phase 5:** Once all active OCs+ACs are typed, flip a flag to reject untyped admission (no more identity fallback)

This avoids a big-bang break.

## Options Considered

### Option A: Keep late coercion, patch engine case-by-case (REJECTED)

Add special handling in the metric engine for every new type edge case. Already doing this with D315 guardrails. Technical debt grows.

### Option B: Type enforcement at CC level only (REJECTED)

Canonical resolution coerces to types before producing CO. Moves the problem one stage up but still leaves admission producing mixed-type records. Cross-source inconsistency persists through AR.

### Option C: Type enforcement at admission (CHOSEN)

Earliest stage where per-source transforms are already governed (OC field_mappings.transform). Extending transform to be type-aware is a natural evolution. Admitted records become source-agnostic in shape. Downstream stages simplify.

## Consequences

### Positive

- Type errors surface at L5 (admission) — clear diagnosis, data-quality signal
- Admitted records are source-agnostic — CC and MC logic simplifies
- D315 engine guardrails become defensive no-ops (still present, never fire)
- Cross-source consistency guaranteed — `receivable_hdr_amount` is always a number regardless of source
- BF.data_type becomes authoritative, closing a long-standing leaky abstraction
- Unlocks D330 (derived CFs) — duration fields become typed transforms from two dates to day count

### Negative

- Schema changes: `observation_contract.field_mappings[].transform` moves from string to structured object
- AC contract body gets a new rule type (`type_conformance`)
- Backward compatibility via phased migration requires 5 phases — not a quick win
- Every active OC needs a new version with typed transforms (~60 OCs currently)
- Every active AC needs a new version with type_conformance rules (~30,000 ACs if SC/AC auto-generation remains 1:1 with source objects — may need a bulk migration script)

### Risks

| Risk | Mitigation |
|---|---|
| Source systems emit values that don't cleanly coerce (e.g., SAP "00145272.42" with leading zeros) | Transform library handles common patterns; unknown patterns route to rejection with clear error |
| Timestamps with timezone ambiguity | Normalize to UTC with source tz as metadata in admitted_record |
| Code fields (e.g., company_code) with leading spaces or case variations | `to_code` trims + optionally case-normalizes per declared convention |
| Existing demo data (string-typed COs) breaks after phase-5 flip | Greenfield tenant re-execution after migration — existing test data is disposable |

### Neutral

- No impact to BF/BO onboarding (D292 — names and roles unchanged)
- No impact to D301 (canonical field naming + cc_field_mapping still valid)
- No impact to D327 (shared dimension normalization is orthogonal)
- Strengthens D329 — constants become typed (`value: number` is already typed; aligns naturally)

## Out of Scope

- Derived field computation (covered by D330 — derived CFs benefit from D331's transform library but are a separate concern)
- Type system for CO/MS outputs (covered implicitly by propagation — if admitted record is typed, downstream is typed by construction)
- Unit-of-measure normalization (separate concern — e.g., USD vs EUR vs INR — requires a conversion service, not just type coercion)

## Implementation Phasing

**Not part of this ADR commitment — to be scoped in a separate plan.** D329 implementation proceeds first; D331 follows in its own session.
