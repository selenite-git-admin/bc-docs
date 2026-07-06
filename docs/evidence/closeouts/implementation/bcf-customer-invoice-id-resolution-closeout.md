---
uid: bcf-customer-invoice-id-resolution-closeout
title: BCF Customer Invoice · invoice id Operator-Resolution Closeout
description: Focused operator-resolution for the parked Customer Invoice · invoice id BC carried forward from publication-confirm closeout 2d9710e + posted-amount-resolution closeout 1ca8ead. Read panel_output_record for prior parked panelRunUid 5555752f; finding was substantive (NOT a Moderator schema bug) — all three agents agreed no active characteristic substantively fit the meaning of 'unique document identifier'; closest active characteristic (`line number`) is per-line position, semantically wrong. Decision Option A — author new `document number` characteristic (generic across invoice / purchase order / shipment / material doc / accounting doc), then author `Customer Invoice · document number` BC against it. Executed: F4-v2 createCharacteristic (clean awaiting_operator_confirm — bc-ai prompt fix from PR #18 7ff8446 working); F4-v2 shape-cert confirm; B10b publish with semanticFinalityAffirmed=true; createBusinessConcept (panel APPROVED autonomously — document number now in active vocabulary); B10 publish. Final substrate state — 2 active entities + 10 active BCs + 29 active characteristics + 0 draft + 0 supersessions + 0 aliases + 0 supersession_proposals. Metric unblock — 8 of 10 (Option B target met); Metrics 3 + 6 remain Step-4-bis. No direct SQL writes; allow_write false confirmed; no MCF gates touched; no B6-v2 retrofit. NOT retry-coaxing — vocabulary gap addressed by the substantive path the panel itself recommended.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: customer-invoice-id-resolution
---

# BCF `Customer Invoice · invoice id` Operator-Resolution Closeout

## 1. Scope and grounding

### 1.1 Purpose

Focused operator-resolution for the parked `Customer Invoice · invoice id` BC (panelRunUid `5555752f-5209-4d81-986d-89f06808563e`) — the last remaining blocker preventing Metric 4 (Aged dispute count) from being authorable into MCF. Per the operator's handoff, decide Option A (author identifier characteristic + re-submit BC) / B (rename to e.g. `invoice number`) / C (reject/defer) by reading the actual panel evidence, and execute the chosen path through existing BCF application paths.

### 1.2 Discipline assertions (all hold)

| Assertion | Status |
|---|---|
| No direct SQL writes to `concept_registry.*` | ✓ — every act through bc-core BCF endpoints. |
| No widening of bc-postgres `allow_write` | ✓ — `pg_server_info` end-of-session confirms `allow_write: false`. |
| No bypass of operator-confirm discipline | ✓ — F4-v2 shape-cert confirm + B10b publication-confirm + B10 BC publication-confirm all carried ≥40-char operator rationale. |
| **No retry-coaxing** | ✓ — read panel_output_record first; finding was a substantive vocabulary gap, not stochastic Moderator noise; corrective action is to AUTHOR THE MISSING CHARACTERISTIC the panel explicitly recommended, not to re-submit the parked BC unchanged. See §3 + §4. |
| Did not revisit Step-4-bis metrics (3 + 6) | ✓ — out of handoff scope. |
| No MCF gates touched | ✓ — M2 DDL not applied, M3 not opened, no MCs created. |
| No B6-v2 retrofit opened | ✓ — no hard trigger fired (§9). |

### 1.3 Endpoints exercised

| Endpoint | Calls |
|---|---:|
| `POST /api/bcf/registry-authoring-runs` (createCharacteristic) | 1 — `document number` |
| `POST /api/bcf/registry-shape-certifications/confirm` (F4-v2) | 1 |
| `POST /api/bcf/registry-publications` (B10 phase 1) | 2 — characteristic + BC |
| `POST /api/bcf/registry-publications/confirm` (B10 phase 2) | 2 — characteristic (`semanticFinalityAffirmed: true`) + BC |
| `POST /api/bcf/registry-authoring-runs` (createBusinessConcept) | 1 — CI · document number |
| Read-only `bc-postgres pg_query` (panel evidence + verification) | ~5 |

Total: **7 endpoint calls**.

### 1.4 Stack state when execution opened

- bc-core (3100) + bc-ai (4300) + bc-admin (3010) all `200`-healthy.
- bc-ai running with PR #18 prompt fix loaded (PID 36588, restarted post-merge of 7ff8446).
- bc-postgres MCP `allow_write: false`; `concept_registry` in `schema_allowlist`.
- Live registry pre-session: 2 active entities + 9 active BCs + 28 active characteristics + 0 draft + 0 supersessions.

---

## 2. Prior parked-item evidence

Read directly via `pg_query` against `contract.panel_output_record WHERE panel_run_uid = '5555752f-5209-4d81-986d-89f06808563e'`.

### 2.1 Orchestrator-level summary

| Field | Value |
|---|---|
| `panel_run_uid` | `5555752f-5209-4d81-986d-89f06808563e` |
| `verdict_code` | `OPERATOR_REVIEW` |
| `grounding_check_result` | `pass` |
| `quarantined` | `false` |
| `sampling_status` | `sampled_for_calibration` |
| `policy_version` | `v1` |
| `prompt_version` | `registry-authoring/v1.0` |
| Models | Maker gemini-2.5-flash · Checker gpt-5.5 · Moderator claude-opus-4-5 (same as posted amount run) |

### 2.2 Moderator's review_reason — substantive vocabulary gap

```text
No governed characteristic in activeCharacteristics substantively fits the meaning of
'invoice id' (a unique document identifier). Available characteristics such as
'line number', 'description', 'status', 'document date', and 'posting date' are weak
or incorrect fits. The representation term 'identifier' is available and appropriate
for the value form, but createBusinessConcept requires both a fitting characteristicId
AND representationTerm. Approving with an approximate characteristic would constitute
vocabulary stretching, which policy prohibits. Operator review is required to
determine whether to expand the governed characteristic vocabulary (e.g., add an
'identifier' or 'document number' characteristic) or to provide alternative guidance
for this candidate.
```

### 2.3 Three-agent substantive agreement — the panel did its job

**Maker (gemini-2.5-flash):** definition clear + evidence strong; entity placement (Customer Invoice) sound; no existing-concept conflict; **set `draft_recommendation: null` and raised flag `no_governed_characteristic_fits`** per the "No vocabulary stretching" discipline.

**Checker (gpt-5.5):** independently verified all checks; agreed no active characteristic substantively represents a general document identifier; concluded "Using a nearby term such as line number, description, status, or document date would be an impermissible stretch."

**Moderator (claude-opus-4-5):** explicit `verdict_code: OPERATOR_REVIEW`. Recommended *"expand the governed characteristic vocabulary (e.g., add an 'identifier' or 'document number' characteristic)"*.

### 2.4 Reading: this is the discipline working as designed

Unlike the `posted amount` parked run (where the panel substantively APPROVED but a Moderator output-schema bug caused parking), this CI · invoice id parking is a **legitimate, substantive non-APPROVE**: the panel correctly refused to bind the BC to a weakly-fitting characteristic.

The corrective action the panel itself prescribed — author the missing characteristic first — is the path that respects the BCF panel's authority over the vocabulary surface. It is NOT retry-coaxing.

---

## 3. Semantic decision — Option A (author new `document number` characteristic)

### 3.1 Decision

**Option A: author a new `document number` characteristic, then author `Customer Invoice · document number` BC against it.**

### 3.2 Why `document number` and not the alternatives

The panel suggested two candidates: `identifier` or `document number`. Considered the operator's three named alternatives + the panel's two suggestions:

| Candidate | Verdict | Reason |
|---|---|---|
| `identifier` (panel-suggested) | **Rejected** | `identifier` is already a representation_term. F4-v2 Vocabulary Admission Checklist M6 ("not a bare representation term") forbids authoring a characteristic that equals a rep term. |
| `document number` (panel-suggested) | **Chosen** | Genuinely global: applies to invoice / purchase order / shipment / journal entry / material doc / accounting doc. Reusable across industries + systems. M4-clean (2 words, lowercase). Distinct from existing `line number` (different scope: document-level vs line-position). |
| `invoice number` | Rejected | Too narrow — Customer-Invoice-specific. Violates the SHOULD ("reusable beyond one field") on Vocabulary Admission Checklist; would create a precedent of entity-specific characteristics. |
| `customer invoice number` | Rejected | Conflates entity name into characteristic. Even narrower. |
| `invoice identifier` | Rejected | Contains representation-term word; M6 would flag rep-term leakage. Also narrow (invoice-specific). |

`document number` is the cleanest expansion: panel-suggested, genuinely global, distinct from existing vocabulary, and reusable.

### 3.3 Why not Option B (rename / refine the BC's proposedName instead)

Option B (rename) would mean re-submitting the BC with a different `proposedName` against the existing weak-fit characteristics. But:
- No existing characteristic substantively fits the document-level identifier meaning. The panel correctly refused vocabulary stretching.
- Renaming the BC without expanding vocabulary just changes the cosmetic label; the semantic gap remains.
- A name like `invoice number` as a BC proposedName would still need a characteristic to bind to; `line number` is wrong; no other fits.

Option B does not resolve the underlying gap.

### 3.4 Why not Option C (reject / defer)

Option C would block Metric 4 (Aged dispute count) indefinitely without addressing the genuine vocabulary need. Document-level identifiers are foundational AR vocabulary — deferring would leak across many future metrics that need entity-id semantics. The panel did not flag this as a "registry should not model this yet" case — quite the opposite: it explicitly recommended expansion.

---

## 4. Characteristic action — `document number` authored + published

### 4.1 createCharacteristic — clean APPROVE on first try (bc-ai prompt fix working)

| Endpoint | `POST /api/bcf/registry-authoring-runs` |
|---|---|
| Payload | `{ operation: 'createCharacteristic', candidateRef: 'cand-2026-05-26-char-document-number', proposedName: 'document number', definition: 'The unique business identifier of a business document, assigned by the issuing system at document creation, used to reference the whole document across systems, transactions, and lifecycle events. Distinct from line number, which identifies the position of a line item within a document — document number identifies the whole document.', candidateEvidence: { OAGIS DocumentID + SAP S/4HANA VBELN/EBELN/MBLNR/BELNR per document type + ISO 11179 } }` |
| Outcome `kind` | `awaiting_operator_confirm` |
| panelRunUid | `68751109-25ef-4698-bd12-e82d5f056d27` |
| governingPolicyUid | `bcf-registry-scope1` |

Notable: this is the **first F4-v2 createCharacteristic run after the bc-ai prompt fix (PR #18 merged as `7ff8446`) was live**. The Moderator emitted the correct `f3_operation: "registerCharacteristic"` (no schema-mismatch parking), confirming the prompt fix worked. The candidate also passed all 10 vocabulary-admission-checklist items at the panel level.

### 4.2 F4-v2 shape-cert confirm

| Endpoint | `POST /api/bcf/registry-shape-certifications/confirm` |
|---|---|
| panelRunUid | `68751109-25ef-4698-bd12-e82d5f056d27` |
| subjectKind | `characteristic` |
| actionCode | `registry_author_vocabulary` |
| rationale (≥40 chars) | Cited the prior parked CI · invoice id run + the panel's recommendation to expand vocabulary; affirmed authorisation under F4-v2 high-risk path. |
| Outcome `kind` | `authored` (authoredSubject: characteristic) |
| certificationRecordId | `3d8a3d68-0b0c-4af2-83f5-143be1d4495e` |
| **characteristicId** | **`40433e4f-568f-489a-ae85-63754ca8ebe9`** |
| Lifecycle landed at | `draft` (per the documented BCF authoring contract) |

### 4.3 B10b publish `document number` characteristic

| Phase | Endpoint | Outcome | Detail |
|---|---|---|---|
| 1 | `POST /api/bcf/registry-publications` | `awaiting_operator_confirm` | subjectKind: characteristic; actionCode: registry_transition |
| 2 | `POST /api/bcf/registry-publications/confirm` (`semanticFinalityAffirmed: true`) | `published` | certificationRecordId `539f0c69-0ddd-40b1-8f0d-ec85600f6461`; lifecycleState `active` |

`semanticFinalityAffirmed: true` per ADR DEC-26b6e2 — the `(term: 'document number', definition)` tuple is now the immutable atom; any correction would require F3 supersession (out of scope).

---

## 5. Customer Invoice identifier BC action — authored + published

### 5.1 createBusinessConcept `Customer Invoice · document number`

| Endpoint | `POST /api/bcf/registry-authoring-runs` |
|---|---|
| Payload | `{ operation: 'createBusinessConcept', candidateRef: 'cand-2026-05-26-ci-document-number', targetEntityId: 'e3963e45-…6446', proposedName: 'document number', definition: 'The unique business identifier of the customer-invoice document … The operator-facing "invoice id" — the value referenced for payment, collection, dispute, and reporting on this specific invoice.', candidateEvidence: { SAP VBRK.VBELN on Customer Invoice + OAGIS Customer Invoice BOD DocumentID } }` |
| Outcome `kind` | `authored` (authoredSubject: business_concept) — panel APPROVED autonomously |
| panelRunUid | `17bcb0bf-072b-4eda-96ac-a0f782944c96` |
| certificationRecordId | `cfcae7b1-16f5-4c69-bc9e-8e68bfbb8073` |
| **conceptId** | **`095afe86-e520-4aab-a28c-b0e6a0cb6bc4`** |
| conceptVersionId | `9f608b77-d0d9-4f93-9729-24c71d840057` |

Panel resolution:
- Characteristic: `document number` (the newly-active one)
- Representation term: **`identifier`** (the panel-judged correct rep term — matches the BC's identifier-role semantics; confirms the Step 4 §5 Metric 4 row's expected rep term)

This is the same autonomous-APPROVE pattern observed for CI · clearing date BC and CI · posted amount BC — when the dependent characteristic is in active vocabulary, the BC panel resolves cleanly.

### 5.2 BC naming convention note

The BC is named `Customer Invoice · document number` (proposedName: `document number`), matching the BCF convention that BC names reflect the characteristic name. Semantically, the invoice's `document number` IS the operator-facing "invoice id" — the value users reference for payment, collection, dispute tracking, and reporting. Step 4 Metric 4 referred to this binding as "CI · invoice id (count target — identifier)"; the authored BC fulfills that role under the canonical BCF naming convention.

### 5.3 B10 publish CI · document number BC

| Phase | Endpoint | Outcome | Detail |
|---|---|---|---|
| 1 | `POST /api/bcf/registry-publications` | `awaiting_operator_confirm` | subjectKind: business_concept |
| 2 | `POST /api/bcf/registry-publications/confirm` | `published` | certificationRecordId `8d06c7b7-66ce-4743-87c4-bd5afdb61488`; lifecycleState `active` |

---

## 6. Live post-action registry verification (read-only)

All counts from live `pg_query` immediately after the 7 endpoint calls. `allow_write: false` re-verified at session end.

### 6.1 Aggregate counts

| metric | session open | session end | delta |
|---|---:|---:|---:|
| entities active | 2 | 2 | 0 |
| business_concepts active | 9 | **10** | +1 (CI · document number) |
| characteristics active | 28 | **29** | +1 (document number) |
| entities draft | 0 | 0 | 0 |
| business_concepts draft | 0 | 0 | 0 |
| characteristics draft | 0 | 0 | 0 |
| representation_terms | 15 | 15 | 0 |
| aliases | 0 | 0 | 0 |
| entity_supersession | 0 | 0 | 0 |
| business_concept_supersession | 0 | 0 | 0 |
| characteristic_supersession | 0 | 0 | 0 |
| supersession_proposal | 0 | 0 | 0 |

Zero draft rows. Zero supersession activity. Zero aliases. Zero supersession_proposals.

### 6.2 Full 10-BC active set

| concept_id | entity | characteristic | rep term |
|---|---|---|---|
| `f66642ad-…f5c3` | Sales Order Line | unit price | amount |
| `f8a30b35-…ac45` | Customer Invoice | due date | date |
| `d05f24b3-…1575` | Customer Invoice | posting date | date |
| `92a5eea0-…0073` | Customer Invoice | status | code |
| `e5774d89-…2eda` | Customer Invoice | effective date | date_time |
| `ea91771f-…1b7e` | Sales Order Line | discount | amount |
| `1bb02176-…1bd4` | Sales Order Line | ordered quantity | quantity |
| `5e0958b5-…b34e` | Customer Invoice | clearing date | date |
| `a42d3fc0-…d734` | Customer Invoice | posted amount | amount |
| `095afe86-…6bc4` | Customer Invoice | **document number** | **identifier** |

The new BC carries representation term `identifier` — the same rep term Step 4 §5 Metric 4 listed as the expected identifier-role rep term.

### 6.3 New characteristic — `document number` active

| characteristic_id | term | lifecycle_state | created_at |
|---|---|---|---|
| `40433e4f-…ebe9` | document number | **active** | 2026-05-26T12:40:26Z |

### 6.4 Sales Order Line / Unit Price unchanged

Sales Order Line entity + Unit Price BC retain their 2026-05-22 timestamps. No supersession references them. The pre-existing BCF baseline is unmoved.

### 6.5 Write discipline

`pg_server_info`: `allow_write: false`; `schema_allowlist: [contract, source, metric, platform, runtime, master, concept_registry]`. Unchanged from session open. Every write through bc-core endpoints.

---

## 7. Metric unblock arithmetic

### 7.1 Per-metric resolution at end of session

| # | Metric | Required BCs / chars | All required `active`? | Status |
|---:|---|---|---|---|
| 1 | Total open receivables | CI · posted amount + CI · clearing date | both active ✓ | UNBLOCKED |
| 2 | Overdue AR % | CI · posted amount + CI · due date | both active ✓ | UNBLOCKED |
| 3 | Unbilled revenue | CI · recognized amount + CI · billed amount | chars absent | Step-4-bis deferred |
| 4 | Aged dispute count | CI · document number (identifier-role BC) + CI · status + CI · effective date | **all three active** ✓ | **UNBLOCKED (new)** |
| 5 | Avg days late, 30d | CI · posting date + CI · due date | both active ✓ | UNBLOCKED |
| 6 | Recognized revenue per fiscal_period | CI · invoice amount + D365 prereq | char absent + D365 prereq | Step-4-bis deferred |
| 7 | AR aging buckets | CI · posted amount + CI · due date | both active ✓ | UNBLOCKED |
| 8 | Discount-to-line-amount | SOL · discount + ordered quantity + unit price | all active ✓ | UNBLOCKED |
| 9 | MLS-14 self-collapse | CI · posted amount | active ✓ | UNBLOCKED |
| 10 | Stale fixture | inherits Metric 2 | Metric 2 unblocked ✓ | UNBLOCKED |

### 7.2 Summary — Option B 8-of-10 target met

| State | Count | Metrics |
|---|---:|---|
| **UNBLOCKED (MCF-bindable today)** | **8** | **Metrics 1, 2, 4, 5, 7, 8, 9, 10** |
| Step-4-bis deferred | 2 | Metric 3, Metric 6 |
| **Total** | **10** | |

**Option B target (8 of 10) MET.** This closes the Step 4 BCF enrichment slice as fully as Option B promised. Metrics 3 + 6 remain Step-4-bis only — separate enrichment session.

### 7.3 Cascade of two operator decisions

Looking back across the four resolution sessions (pre-execution / execution / publication-confirm / posted amount / invoice id):

| Operator decision | Metrics unblocked by that decision alone |
|---|---|
| Author the entities + slice BCs (execution + publication-confirm) | 2 (Metrics 5 + 8) |
| Author + publish `posted amount` characteristic + CI · posted amount BC | +5 (Metrics 1, 2, 7, 9, 10) |
| Author + publish `document number` characteristic + CI · document number BC | +1 (Metric 4) |

Plus the upstream bc-ai prompt fix (PR #18) unblocked stochastic Moderator parking for F4-v2 createCharacteristic generally.

---

## 8. Remaining blockers

### 8.1 Step-4-bis only (out of scope this gate + future enrichment session)

| Metric | Why deferred |
|---|---|
| Metric 3 — Unbilled revenue | Needs `recognized amount` + `billed amount` characteristics (F4-S1 §6 deferred originals); Option B did not author these |
| Metric 6 — Recognized revenue per fiscal_period | Needs `invoice amount` characteristic (F4-S1 §6 deferred original) + D365 `posting_date_field` runtime prerequisite on `contract.canonical_contract` |

Step-4-bis enrichment is the right venue. Operator decides whether to revisit the F4-S1 §6 deferrals (Option A), compose from rawer primitives (Option B-extended), or defer further.

### 8.2 No other parked items

No parked OPERATOR_REVIEW items remain on the Step 4 slice. No deferred BCs. Substrate is in the cleanest state since enrichment began.

### 8.3 Follow-up on bc-ai prompt fix

The bc-ai prompt fix (PR #18 / `7ff8446`) is working as expected — this session's createCharacteristic run produced a clean `awaiting_operator_confirm` on the first attempt with no Moderator schema-bug parking. Continued monitoring recommended for the next few F4-v2 panel runs.

---

## 9. BCF v1 packet sufficiency observations

| Hard trigger | Status this session |
|---|---|
| T-H1 — cross-entity disambiguation load-bearing | NOT TRIGGERED. CI · document number BC's target entity was operator-supplied (Customer Invoice). |
| T-H2 — source-reality grounding PE-MC-1-mandatory | NOT TRIGGERED. Candidate evidence operator-supplied per request body. |
| T-H3 — active characteristic vocabulary wire-size threshold | NOT TRIGGERED. Vocabulary grew 28 → 29 active — well under threshold. |
| T-H4 — bc-ai acquires free Registry query path | NOT TRIGGERED. L1 lock preserved. |

**Verdict: BCF v1 packet remains sufficient. No B6-v2 retrofit opens.**

Soft observation: the panel's parked OPERATOR_REVIEW with explicit vocabulary-expansion recommendation is the v1 design working at full strength. The operator reads the panel evidence (`panel_output_record`), takes the recommended action, and the substrate evolves cleanly. No B6-v2 workbench would have produced a different outcome — the panel correctly identified what was missing and the operator authored it.

---

## 10. Recommended next step

### 10.1 Step 4 BCF enrichment slice — CLOSED for the 8-of-10 Option B target

The Step 4 BCF enrichment slice has reached its Option B acceptance state. All BCs the 8 unblockable metrics need are `active`; the slice's BCF authoring side is complete. From the BCF perspective, the operator may now:

1. **Open MCF M2 DDL apply** (separate operator-authorized session under Database Change Protocol) so the MCF substrate can be provisioned. This is the next operationally-blocking gate per the MCF arc.
2. **Open MCF M3 onwards** once M2 is applied — leading eventually to MCF Gate M20 (first representative metric authoring program) which will MCF-author the 8 unblocked metrics.

### 10.2 Step-4-bis — separate enrichment session

For Metrics 3 + 6, open Step-4-bis when ready:
- Read pre-execution plan §5.5 + execution closeout §8 for the option set (F4-S1 §6 deferral-reversal vs compose-from-rawer-primitives vs defer-further).
- Recommendation in the pre-execution plan: revisit operator decision on `recognized amount` / `billed amount` / `invoice amount` characteristics; D365 `posting_date_field` prereq is independent and tracked separately.

### 10.3 What stays closed

- **MCF M3** — closed.
- **MCF M2 DDL apply** — closed (separate Database Change Protocol session).
- **B6-v2 retrofit** — closed (no trigger fired).
- **MC creation** — closed.
- **bc-postgres write access** — closed (`allow_write: false`).

### 10.4 The seven sessions of Step 4 BCF enrichment

For audit: this resolution closeout caps a seven-session arc that ran today (2026-05-26):

1. SES-0e8cac (10:04-15:44): Pre-execution plan — bc-docs-v3 `248b004`
2. SES-26e8f3 (10:24-16:19): Execution closeout — bc-docs-v3 `3b4c71b`
3. SES-3d0812 (11:44-17:23): Publication-confirm closeout — bc-docs-v3 `2d9710e`
4. SES-bde518 (11:56-17:37): Posted-amount resolution closeout — bc-docs-v3 `1ca8ead`
5. SES-9f0aa5 (12:10-17:46): bc-ai prompt bugfix PR — merged as bc-ai `7ff8446` (PR #18)
6. (bc-ai restart, no DevHub session)
7. SES-afd4d9 (12:34-current): this resolution closeout

Final state across all sessions: 2 active entities + 10 active BCs + 29 active characteristics; 8 of 10 representative metrics MCF-bindable; 0 supersessions / aliases / proposals across the entire arc; zero direct SQL writes; zero MCF gate openings.

---

## Document verification

- **All 10 required sections present** (§1 Scope and grounding; §2 Prior parked-item evidence; §3 Semantic decision; §4 Characteristic action; §5 Customer Invoice identifier BC action; §6 Live post-action verification; §7 Metric unblock arithmetic; §8 Remaining blockers; §9 BCF v1 packet sufficiency; §10 Recommended next step).
- **Parked-item evidence read directly** (§2) — verdict_code, review_reason, all three agent assessments + Moderator's explicit recommendation to add `document number`.
- **Semantic decision justified against three options** (§3) — Option A chosen with explicit rejection of B + C and the operator's three named alternatives.
- **No retry-coaxing** — the parking was substantive (vocabulary gap); the resolution was to author the missing characteristic the panel itself recommended (§3.4 + §4).
- **Discipline assertions hold** (§1.2) — no direct SQL writes, allow_write unchanged, operator-confirm not bypassed, Step-4-bis metrics not touched, MCF gates closed, no B6-v2 opened.
- **Substrate state quantified** (§6) — 2 active entities + 10 active BCs + 29 active characteristics + 0 draft + 0 supersessions + 0 aliases + 0 supersession_proposals.
- **Metric arithmetic explicit** (§7) — 8 unblocked + 2 Step-4-bis deferred = 10. Option B target met.
- **No code changes, no DDL, no DB writes outside the BCF endpoint path.** Doc-only commit.
