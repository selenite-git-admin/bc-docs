---
title: "SDA external-standard G4 experiment — plan only"
session: SES-594568
date: 2026-05-12
status: plan
type: experiment-plan
authority: DEC-a17d0f
related:
  - 2026-05-12-sda-certification-operator-runbook-SES-594568.md
  - 2026-05-12-sda-first-honest-certification-canary-SES-594568.md
---

# External-standard G4 experiment — plan

Per the operator runbook §7, the next live SDA certification should
stretch exactly one previously-untested edge. This plan proposes
**one** BF that legitimately cites an external standard, exercising
the `EXTERNAL_DEFINITION_STANDARDS` branch of G4 with a real
`standard_ref` value. **Plan only — no PATCH, no certify, no live
writes from this MWR.**

## 1. Scope (locked)

- One BF candidate, primary. One backup.
- Read-only planning. No metadata or lifecycle writes.
- No matrix change. No DBCP. No bc-core code change.
- No override. The candidates must pass G4 cleanly on a real ref.

## 2. Recommended standard for this experiment

**ISO_20022.** Reasons:

1. The BareCount registry has 100+ draft BFs in the `credit_transfer_*`,
   `debit_transfer_*`, `remittance_advice_*` namespaces — all of
   which are paradigm ISO_20022 message territory (`pain.001`,
   `pacs.008`, `camt.054`, etc.).
2. ISO_20022 element names are public, stable, and citable to a
   precise message + path — strong evidence for the `standardRef`
   without speculation.
3. OAGIS is the next-strongest candidate but BareCount BF
   definitions don't currently invoke OAGIS terminology verbatim;
   the citation would be conceptual rather than literal. ISO_20022
   has the cleanest evidence trail in the draft pool.

IFRS / US_GAAP / COSO / IIA are deferred — the BFs that would
naturally anchor to them (balance figures, control scores) are
either already-certified, have `data_type='code'` (TSK-84d81c
blocker), or are number-typed without a viable family in today's
matrix.

## 3. Primary candidate

### 3.1 Identity

| field | value |
|---|---|
| field_id | `019d7076-e439-7264-aa92-9b5bd5198307` |
| name | `credit_transfer_hdr_entry_remittance_information` |
| business_function | finance |
| object_class | `credit_transfer_hdr_entry_remittance` |
| property | `information` |
| representation_term | (per row inspection — `Information`) |
| data_type | `string` |
| pii_classification | (per row inspection) |
| status_code | `draft` |
| existing `semantic_family` | NULL |
| existing `definition_standard` | NULL |
| existing `standard_ref` | NULL |
| prior `certification_record` rows | 0 |
| parent BO | `credit_transfer_hdr` (`certified`) |
| definition (71 chars) | *"Unstructured remittance information for the entry, for payment details."* |
| G2a / G2b collisions | 0 / 0 (verified) |
| banned-token check | clean |

### 3.2 Proposed PATCH body

```json
{
  "semanticFamily": "text",
  "definitionStandard": "ISO_20022",
  "standardRef": "ISO20022:pain.001 RemittanceInformation/Unstructured (RmtInf/Ustrd)"
}
```

### 3.3 Evidence — why ISO_20022 is honest here

- **Definition text quotes the standard verbatim.** The BareCount
  definition begins *"Unstructured remittance information…"*.
  `RemittanceInformation` is the literal element name in
  `pain.001` (Customer Credit Transfer Initiation) and
  `pacs.008` (Financial Institution to Financial Institution
  Customer Credit Transfer). Its child `Unstructured` (`Ustrd`)
  carries free-text payment narrative. The BareCount BF's purpose
  and shape is exact one-to-one with the ISO_20022 element.
- **Namespace alignment.** `credit_transfer_*` is the BareCount-side
  name for ISO_20022's credit-transfer family of messages. Every
  other BF under this `object_class` (e.g. `debtor_identifier`,
  `creditor_account_identifier`, `account_identification`) also
  has a direct ISO_20022 analog — confirms the namespace is
  deliberately ISO_20022-aligned, not coincidentally similar.
- **Citation is verifiable.** ISO_20022 publishes the message
  schemas and element dictionaries publicly at iso20022.org
  (Message Definition Reports). The cited path
  `pain.001 RemittanceInformation/Unstructured (RmtInf/Ustrd)`
  is a precise locator within the published schema, not a
  paraphrase.

### 3.4 Family choice — `text`

`master.semantic_family['text']` accepts `compatible_data_types=
['string']`, requires no unit_type — matrix-clean.

Rationale: the BareCount definition emphasizes *unstructured* —
free-form payment narrative, not a coded value, not a person/system
identifier. Of the four identity-category families
(`code`, `name`, `identifier`, `text`), `text` is the one designed
for free-form descriptive content. `identifier` would imply a
closed-set lookup value; `name` would imply a party name. Neither
fits the unstructured-narrative semantics.

### 3.5 Expected G1–G8 verdicts after PATCH

| Gate | Verdict | Reason |
|---|---|---|
| G1 | pass | snake_case + name starts with `credit_transfer_hdr_entry_remittance_` |
| G2a | pass | 0 exact-name collisions (verified) |
| G2b | pass | 0 normalized-form collisions (verified) |
| G3 | pass | 71 chars, no banned tokens, sentence-shaped |
| **G4** | **pass** | `definitionStandard='ISO_20022'` ∈ `EXTERNAL_DEFINITION_STANDARDS`; `standardRef` non-empty → external-standard branch satisfied |
| G5 | pass | `semanticFamily='text'` ∈ `SEMANTIC_FAMILY_ENUM` |
| G6 | pass | `dataType='string'` ∈ `master.semantic_family['text'].compatible_data_types=['string']`; unit `null` |
| G7 | pass | name starts with `BF.object_class + '_'` |
| G8 | pass | CF-only; N/A |

Expected summary: `canCertifyWithoutOverride: true`,
`hasBlockingFailures: false`, `hasOverridableFailures: false`,
`unevaluableGates: []`. **No override required.**

## 4. Backup candidate

### 4.1 Identity

| field | value |
|---|---|
| field_id | `019d7079-5771-7e77-ab69-9a3d3a012f74` |
| name | `credit_transfer_payment_debtor_identifier` |
| object_class | `credit_transfer_payment_debtor` |
| property | `identifier` |
| data_type | `string` |
| status_code | `draft` |
| existing `semantic_family` / `definition_standard` / `standard_ref` | all NULL |
| prior `certification_record` rows | 0 |
| parent BO | `credit_transfer_payment` (`certified`) |
| definition (70 chars) | *"A credit transfer involves a debtor (payer) who initiates the payment."* |
| G2a / G2b collisions | 0 / 0 (verified) |
| banned-token check | clean |

### 4.2 Proposed PATCH body

```json
{
  "semanticFamily": "identifier",
  "definitionStandard": "ISO_20022",
  "standardRef": "ISO20022:pain.001 Debtor (Dbtr)"
}
```

### 4.3 Evidence — why ISO_20022 is honest here

- **Term match.** "Debtor" is the literal ISO_20022 element name
  for the party initiating a credit transfer. `pain.001` uses
  `<Dbtr>` (Debtor) and `<DbtrAcct>` (Debtor Account) as core
  message elements.
- **Definition mirrors the spec.** *"…debtor (payer) who initiates
  the payment"* is essentially a plain-English restatement of
  ISO_20022's Debtor definition.
- **Namespace consistency.** Same `credit_transfer_*` reasoning
  as §3.3.
- **Citation:** `ISO20022:pain.001 Debtor (Dbtr)`. The BF maps to
  the Debtor party concept rather than the inner `<Id>` element;
  the BF's `property='identifier'` reflects BareCount's modeling
  choice of capturing the Debtor through its identifier value.

### 4.4 Family choice — `identifier`

`master.semantic_family['identifier']` accepts
`compatible_data_types=['string']`, requires no unit_type —
matrix-clean. The BF's `property='identifier'` aligns with the
family name.

### 4.5 Expected G1–G8 verdicts after PATCH

Same shape as the primary — all 9 pass, `canCertifyWithoutOverride:
true`, no override required.

## 5. Why pick the primary over the backup

Three reasons to lead with `credit_transfer_hdr_entry_remittance_information`:

1. **Family diversity.** `text` is a family not yet exercised in the
   six certifications so far (which used `identifier` ×4, `date` ×2,
   `name` ×1). The backup uses `identifier`, already over-represented.
2. **Strongest verbatim evidence.** The definition starts with the
   word "Unstructured" — the literal ISO_20022 sub-element name
   `Ustrd`. Citation is unambiguous.
3. **Different gate dynamic.** The primary tests `text` against a
   non-trivial external standard; the backup tests `identifier`
   (already-proven family) against an external standard. The primary
   stretches more of the matrix in a single experiment.

## 6. Boundaries honoured by this plan

- No PATCH executed. No submit-for-review. No certify.
- No live metadata writes against either candidate.
- No DBCP work. No master.* edits. No bc-core code changes.
- No new tasks filed. The 3 known follow-ups (`TSK-c94055`,
  `TSK-84d81c`, `TSK-000fa7`) remain `planned/later`.
- No CF or BO touches.
- Other ISO_20022 candidates (14 sibling BFs) not modified or
  scheduled — this plan covers exactly one experiment.

## 7. What this experiment proves (when executed)

- **G4 external-standard branch** validated end-to-end: a real
  external `definitionStandard` + a real non-empty `standardRef`
  flow through `EXTERNAL_DEFINITION_STANDARDS` cleanly. Today
  every certified BF carries `BARECOUNT`; this is the first
  external case.
- **`text` family** validated as a viable BF family alongside
  `identifier`, `date`, `name`.
- **Cross-vocabulary citation pattern** demonstrated for future
  operators: ISO_20022 element-path style as a canonical
  `standardRef` form. Becomes a reference for OAGIS, IFRS,
  US_GAAP, COSO, IIA citations later.

## 8. What this experiment does NOT prove

- Override discipline (no failing gates → no override exercised).
- OAGIS / IFRS / US_GAAP / COSO / IIA branches of G4 (those need
  their own experiments).
- Bulk-mode behaviour (out of scope — runbook §5 still forbids).
- CF or BO certification (still BF-only).

## 9. Awaiting operator authorization

When you approve the live write, the flow is the operator runbook
§3 verbatim against the primary candidate. If the primary fails
preflight or any unexpected gate result appears, stop per runbook
§3 and fall through to the backup as a second-attempt experiment
(also with explicit approval — not automatic).

---

**End of plan.**
