---
title: "D409 Credit Facility Modeling Policy — revolving in object_class vs axis dimension"
date: 2026-05-17
authority: DEC-b8ec00 (D409 — BF-BO Catalog Expansion Factory)
adr: bc-docs-v3/docs/adrs/ADR-b8ec00.md
sop: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md
scaffold: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-agent-prompt-scaffold.md
predecessor: DEC-1ce490 (D408)
session: SES-a51816
type: modeling-policy
status: draft
version: 0.1
scope: cc__credit (generalisable; not yet generalised)
governs:
  - 2026-05-17-d409-cc-credit-orphan-cf-packet (Pilot 1)
  - 2026-05-17-d409-cc-credit-revolving-credit-limit-evidence-packet (Pilot 1A)
  - 2026-05-17-d409-cc-credit-remaining-orphan-cf-batch-packet (Pilot 1B)
governing_invariants:
  - I (Meaning is evaluated once)
  - IV (All references are explicit)
  - VI (Evidence is emitted, not inferred)
---

# D409 — Credit Facility Modeling Policy

A B-layer policy decision: **how do we model the "revolving" vs "non-revolving" distinction on credit-facility business fields?** The cc__credit pilot exposed the question; this note answers it before any C-layer admission writes occur. This note governs the four in-flight facility rows surfaced by Pilot 1A/1B and supplies a rule for the rest.

---

## 1. Problem statement

The D409 cc__credit pilot is complete on the recommendation side (all 11 orphan CFs have at least one factory pass). Of those:

- **3 `ADMIT_READY`** — each proposes a *new* business field with `revolving` placed in `object_class`:
  - `revolving_credit_limit` → proposed BF `revolving_credit_facility_maximum_borrowing_capacity` (Pilot 1A).
  - `drawn_credit_facility_amount` → proposed BF `credit_facility_amount_outstanding` (Pilot 1B, lane 3).
  - `revolving_credit_drawn` → proposed BF `revolving_credit_facility_amount_outstanding` (Pilot 1B, lane 3).
- **1 `DUPLICATE_OR_MERGE`** — `total_credit_facility_limit` overlaps Pilot 1A's proposed revolving-specific BF; admitting both as-proposed would create parallel concepts (general limit vs revolving limit) without an explicit governance reason.
- **6 `NEEDS_EVIDENCE`** and **1 `HOLD`** are orthogonal to this policy (operational dates, decision counts, unit/name conflict, bank-vs-customer perspective, empty definition).

The blocker for the three ADMIT_READY rows is not evidence — US-GAAP XBRL coverage is in hand. The blocker is **modeling policy**. Admitting the three rows as-proposed creates a catalog where `revolving` is encoded in `object_class` rather than carried as a tenant/contract dimension. That choice has long-term consequences (catalog complexity, mapping ergonomics, future cross-domain extensibility) and must be settled at B (contract grammar) before any C (mapping) writes occur. If we admit first and decide later, we will be cleaning up duplicates through DBCP later — exactly the funnel-padding pattern SOP §9 forbids.

---

## 2. Evidence basis

### 2.1 Pilot artifacts (all in bc-core/scripts/audit-output)

- **Pilot 1** (bc-core@49eec7c, SES-abd596): `d409-cc-credit-orphan-cf-packet-2026-05-17.{md,jsonl}`. Eleven orphan CFs verified, 10 NEEDS_EVIDENCE + 1 HOLD from deterministic scaffold.
- **Pilot 1A** (bc-core@4a446a9, SES-9346a2): `d409-cc-credit-revolving-credit-limit-evidence-packet-2026-05-17.{md,jsonl}`. Single-CF deep-dive for `revolving_credit_limit`. Pre-sourced US-GAAP XBRL evidence. Verdict ADMIT_READY new BF.
- **Pilot 1B** (bc-core@76dda90, SES-1c3ba4): `d409-cc-credit-remaining-orphan-cf-batch-packet-2026-05-17.{md,jsonl}`. Batch triage of the 10 remaining orphans; lane-level discipline; 2 ADMIT_READY + 1 DUPLICATE_OR_MERGE in the facility-amount lane.

### 2.2 US-GAAP XBRL element families cited by the pilot

Factual citations only; no quoted proprietary or paywalled ASC prose.

- `us-gaap:LineOfCreditFacilityMaximumBorrowingCapacity` — `monetaryItemType`, period type `instant`, balance `credit`. The reporting concept for the *maximum authorised* borrowing limit. Cited by Pilot 1A.
- `us-gaap:LineOfCreditFacilityAmountOutstanding` — `monetaryItemType`, period type `instant`, balance `credit`. The reporting concept for the *outstanding/drawn* balance. Cited by Pilot 1B for `drawn_credit_facility_amount` and `revolving_credit_drawn`.
- `us-gaap:LineOfCreditFacilityAxis` — the dimension over `LineOfCreditFacility*` facts.
- `us-gaap:RevolvingCreditFacilityMember` — a member on the `LineOfCreditFacilityAxis` that specialises a fact to the revolving case.
- FASB ASC 470-10-50 is the disclosure reference for debt/credit facility line items. Operator must independently verify each element/axis/member against the current published us-gaap taxonomy release before any apply.

### 2.3 The key design observation in XBRL

In US-GAAP XBRL, the element itself is **generic** (`LineOfCreditFacility...`). "Revolving" is expressed by **dimensioning** the fact with `RevolvingCreditFacilityMember` on `LineOfCreditFacilityAxis` — not by inventing a separate element. The taxonomy explicitly models the revolving/non-revolving distinction as an axis member, not as a renamed concept. This is the load-bearing piece of evidence for the policy choice below.

---

## 3. Modeling options

### Option A — Revolving in `object_class`

One BF per (facility-type, property) pair. Proposed examples:

| BF name | object_class | property |
|---|---|---|
| `revolving_credit_facility_maximum_borrowing_capacity` | `revolving_credit_facility` | `maximum_borrowing_capacity` |
| `revolving_credit_facility_amount_outstanding` | `revolving_credit_facility` | `amount_outstanding` |
| (sibling) `term_loan_facility_maximum_borrowing_capacity` | `term_loan_facility` | `maximum_borrowing_capacity` |
| (sibling) `term_loan_facility_amount_outstanding` | `term_loan_facility` | `amount_outstanding` |

This is the shape the Pilot 1A/1B scripts proposed by default. It is the BareCount-native pattern (`credit_status_*`, `credit_transfer_hdr_*`, etc.).

### Option B — Revolving as axis / dimension over a generic BF

One BF per property; the facility-type lives as a dimension carried by the CF, the cc_field_mapping, or the metric variable binding.

| BF name | object_class | property | dimension(s) carried by mapping/metric |
|---|---|---|---|
| `credit_facility_maximum_borrowing_capacity` | `credit_facility` | `maximum_borrowing_capacity` | `facility_type ∈ {revolving, term, …}` |
| `credit_facility_amount_outstanding` | `credit_facility` | `amount_outstanding` | `facility_type ∈ {revolving, term, …}` |

This is the XBRL-native pattern (§2.3): one element, dimensioned by an axis member at the fact level.

### Option C — Hybrid (generic-first, subtype-specific only when forced)

Default to generic BFs (Option B shape). Admit a subtype-specific BF (Option A shape) **only when**:

1. The source standard defines a distinct named line item (not just an axis member), **or**
2. The business meaning materially differs from the generic concept in a way that cannot be expressed as a dimension (e.g. a subtype has a different unit type, period type, balance type, or required-vs-optional cardinality), **or**
3. The contract/metric layer cannot carry the facility_type dimension at all (no place for it on the CF/mapping/metric variable) and admitting a generic BF would silently lose that specialisation.

Otherwise the generic BF is the canonical concept and "revolving" is carried as context, not as a renamed BF.

---

## 4. Evaluation criteria

Score each option on the eight criteria from the task brief. Scores: 🟢 best / 🟡 neutral / 🔴 worst (within this comparison; not absolute).

| Criterion | A (object_class) | B (axis/dim) | C (hybrid generic-first) |
|---|:---:|:---:|:---:|
| Semantic uniqueness — one concept ↔ one BF | 🔴 splits one XBRL concept into many BFs | 🟢 mirrors XBRL's one-element-per-concept | 🟢 generic is the canonical concept |
| BF catalog simplicity | 🔴 grows with facility-type cardinality (revolving, term, swingline, letter-of-credit, …) | 🟢 small, stable set | 🟢 small, stable + occasional subtype |
| CF mapping ergonomics | 🟡 mapping is direct but multiple CFs route to multiple parallel BFs | 🟡 mapping must carry the dimension explicitly (more discipline at mapping authoring) | 🟡 same as B for the generic case |
| Metric evaluation compatibility | 🟡 metric variable picks the right specialised BF | 🟢 metric variable picks the generic BF + filters on dimension (more reusable formulas) | 🟢 generic case identical to B |
| Duplicate risk | 🔴 high — already manifested in Pilot 1B (`total_credit_facility_limit` overlaps `revolving_credit_facility_maximum_borrowing_capacity`) | 🟢 low — one concept, one BF | 🟢 low when discipline is held; subtype admission requires §3-style justification |
| Future source-system mapping | 🟡 each new system maps its drawn/limit columns into N×M parallel BFs by facility-type | 🟢 each new system maps into a small fixed set + the dimension | 🟢 same as B |
| D409 admission discipline | 🔴 catalog grows without standards-tier forcing function (admission becomes coverage-shaped) | 🟢 admission gates each new BF on a standards-tier distinction | 🟢 same as B + §3-clause hard rule |
| Alignment with XBRL axis/member design | 🔴 conflicts: invents elements XBRL already covers with axis members | 🟢 mirrors XBRL exactly | 🟢 mirrors XBRL except when a standard defines a distinct concept |

**Summary.** Option A loses on six of eight criteria; its only neutral position is mapping ergonomics. Option B wins on seven of eight and is neutral on one. Option C is identical to B in the common case and adds a controlled escape hatch for the rare cases where a subtype concept truly diverges. Option C is the policy.

---

## 5. Recommended decision

**Option C — Hybrid, generic-first.**

### 5.1 The rule

1. Admit a **generic** `credit_facility_*` BF when the concept is a facility-wide monetary/temporal/identifier attribute. The CF, `cc_field_mapping`, or metric variable carries `facility_type ∈ {revolving, term, swingline, letter_of_credit, …}` as a dimension/filter.
2. Admit a **subtype-specific** BF (e.g. `revolving_credit_facility_*`) **only when** at least one of the §3-C escape conditions holds. Record the reason in the BF's `description_text` and `standard_ref` (the source-standard line-item name) — this is the §3-C audit trail.
3. **Forbidden:** admitting both a generic BF and a parallel subtype-specific BF for the same property unless §3-C condition (1) or (2) is materially satisfied. "Operator preference" or "shorter name" is not a satisfying condition.

### 5.2 Per-CF implications for the current pilot

For each of the four in-flight facility rows, the policy resolves the Pilot 1A/1B verdict as follows:

#### 5.2.1 `revolving_credit_limit`

- **Pilot 1A verdict:** ADMIT_READY new BF `revolving_credit_facility_maximum_borrowing_capacity`.
- **Policy resolution:** *re-route to generic*. The XBRL concept `LineOfCreditFacilityMaximumBorrowingCapacity` is element-level generic; the revolving specialisation is an axis member. None of the §3-C escape conditions hold (no distinct named line item, no unit/period/balance divergence, and the cc__credit contract can carry a `facility_type` dimension via CF or mapping).
- **Admit target:** generic BF `credit_facility_maximum_borrowing_capacity` (object_class=`credit_facility`, property=`maximum_borrowing_capacity`, data_type=number, unit_type_code=currency, definition_standard=US_GAAP_XBRL, standard_ref=`us-gaap:LineOfCreditFacilityMaximumBorrowingCapacity` + ASC 470-10-50).
- **Dimension carriage:** the CF retains its name `revolving_credit_limit`; the `cc_field_mapping` row (when authored) declares `facility_type = revolving` via `filter_json` or `compute_json` (matching the existing `cc_field_mapping.filter_json` shape).

#### 5.2.2 `drawn_credit_facility_amount`

- **Pilot 1B verdict:** ADMIT_READY new BF `credit_facility_amount_outstanding`.
- **Policy resolution:** **stands** (already generic). This row is the simplest case — no facility-type specialisation at the source.
- **Admit target:** as proposed in Pilot 1B (`credit_facility_amount_outstanding`).

#### 5.2.3 `revolving_credit_drawn`

- **Pilot 1B verdict:** ADMIT_READY new BF `revolving_credit_facility_amount_outstanding`.
- **Policy resolution:** *re-route to generic*. Same reasoning as 5.2.1 — the XBRL concept is generic; revolving is an axis member.
- **Admit target:** the **same** generic BF as 5.2.2 (`credit_facility_amount_outstanding`). The CF retains its name `revolving_credit_drawn`; the mapping carries `facility_type = revolving`.
- **Consequence:** Pilot 1B's two ADMIT_READY rows collapse from *two new BFs* to *one new BF with two CF mappings*. This is the duplicate-elimination point the DUPLICATE_OR_MERGE row was warning about.

#### 5.2.4 `total_credit_facility_limit`

- **Pilot 1B verdict:** DUPLICATE_OR_MERGE — pending naming-policy decision.
- **Policy resolution:** the policy answers the underlying question. With the generic BF `credit_facility_maximum_borrowing_capacity` admitted (from 5.2.1), this CF rebinds to the **same** generic BF. The CF's mapping does not need a `facility_type` filter — it is the aggregate/total over all facility types.
- **Reclassified verdict:** **`REBIND_RECOMMENDED`** (against the newly admitted generic BF, once it exists). Until the generic BF is admitted, the row stays open against the policy, not against evidence.

### 5.3 Net change to admission queue

Before the policy:

| Row | Verdict | Proposed new BF |
|---|---|---|
| `revolving_credit_limit` | ADMIT_READY | `revolving_credit_facility_maximum_borrowing_capacity` |
| `drawn_credit_facility_amount` | ADMIT_READY | `credit_facility_amount_outstanding` |
| `revolving_credit_drawn` | ADMIT_READY | `revolving_credit_facility_amount_outstanding` |
| `total_credit_facility_limit` | DUPLICATE_OR_MERGE | — |

After the policy:

| Row | Verdict | Admit target |
|---|---|---|
| `revolving_credit_limit` | ADMIT_READY | generic `credit_facility_maximum_borrowing_capacity` (CF mapping carries `facility_type=revolving`) |
| `drawn_credit_facility_amount` | ADMIT_READY | generic `credit_facility_amount_outstanding` |
| `revolving_credit_drawn` | ADMIT_READY | **same** generic `credit_facility_amount_outstanding` (CF mapping carries `facility_type=revolving`) |
| `total_credit_facility_limit` | REBIND_RECOMMENDED | generic `credit_facility_maximum_borrowing_capacity` (aggregate; no filter) |

**Two** new BFs to admit (not three or four). **Four** CF rebinds to author once those BFs are certified.

The six NEEDS_EVIDENCE rows and the HOLD row are untouched by this policy — they are evidence/definition issues, not modeling issues.

---

## 6. Immediate impact on D409 pilot

### 6.1 Verdict reclassification (governing override)

This note is the **governing override** on the Pilot 1A/1B JSONL/MD artifacts. The artifacts themselves are **not** rewritten — they remain the verifiable record of what the deterministic scaffold produced. The reclassification table in §5.3 is the operator's authoritative view going forward. A future packet (whether human-driven or LLM-driven) that re-runs the same rows should reproduce the §5.3 verdicts; if it reproduces the original Pilot 1A/1B verdicts instead, the LLM trio is failing to apply the policy and the operator should re-instruct.

### 6.2 BFs to admit

Two:

1. `credit_facility_maximum_borrowing_capacity` (generic). Standards-tier evidence: `us-gaap:LineOfCreditFacilityMaximumBorrowingCapacity` + ASC 470-10-50.
2. `credit_facility_amount_outstanding` (generic). Standards-tier evidence: `us-gaap:LineOfCreditFacilityAmountOutstanding` + ASC 470-10-50.

Neither admitted in this session — this note is the policy decision, not the admission packet.

### 6.3 Rows still NEEDS_EVIDENCE / HOLD (unchanged)

- `credit_application_submission_date`, `credit_approval_completion_date` — operator sources OAGIS credit-application BOD or domain SDA.
- `automated_credit_decisions_count`, `total_credit_decisions_count` — operator decides whether these belong in cc__credit at all; no standard reporting concept exists for operational decision-throughput.
- `available_credit_lines` — operator disambiguates name vs unit (`plural lines` ≠ `currency`).
- `total_credit_deployed` — operator clarifies bank-perspective vs customer-perspective.
- `customer_credit_risk_rating` — operator runs `/correct-definition` first (empty `description_text`).

---

## 7. Guardrails

1. **No parallel generic + subtype BFs for the same meaning.** Subtype admission is gated on §3-C condition (1) or (2). The §3-C audit trail (named line item or material divergence) must be recorded in the BF's `description_text` and `standard_ref`.
2. **BF name does not encode every possible dimension.** `facility_type`, `currency`, `tenor_bucket`, `subordination_rank`, etc. live on the CF, mapping, or metric variable — not in the BF name. If a future request proposes a BF name that bakes in two or more dimensions, treat the request as a halt under SOP §9.
3. **No subtype admission to chase coverage.** A subtype BF that exists only because a metric author wanted a shorter name, or because a single source system happens to expose only the revolving column, is a coverage-shaped admission and is forbidden.
4. **Preserve the D409 core rule.** Agents recommend; governed endpoints/scripts mutate. This note does not authorise any admission — only the operator, through the D408 governed path, may admit the two generic BFs.
5. **Policy is cc__credit-scoped, generalisable, not yet generalised.** Other domains (e.g. derivatives, deposits, lease facilities) may surface similar axis-vs-element decisions. Each should be settled with its own modeling-policy note before admission; do not assume this note transitively decides them.

---

## 8. Next implementation step

After this note is approved by the operator, the next D409 session authors a **read-only admission packet** for the two generic BFs and the four CF rebinds. The packet:

- Re-verifies the 14 D408 invariants pre and post.
- Re-verifies all four facility-row CFs are still orphan.
- Lays out the multi-step governed path per BF: `POST /api/business-fields` → governed promotion to `certified_catalog` → `cc_field_mapping` insert(s) with `facility_type` dimension carried as needed.
- Emits a DBCP draft (or per-step plan) for operator review. Does **not** apply.

No admission, no DBCP apply, no rebind in that next session either — the apply is a separate operator-driven session.

In this current session: **policy authored, committed, halted.**

---

## 9. References

- [ADR-b8ec00](../../../../../governance/adrs/ADR-b8ec00.md) — DEC-b8ec00 (D409) governing decision.
- [D409 SOP v0.1](2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md) — operational source of truth.
- [D409 Agent Prompt Scaffold v0.1](2026-05-17-d409-agent-prompt-scaffold.md) — role contracts.
- [D408 correction_required closeout](../../../../closeouts/onboarding/2026-05-17-d408-correction-cleanup-closeout-DEC-1ce490.md) — parent decision artifacts.
- [the-invariants.md](../../../../../foundation/the-invariants.md) — Foundation invariants (I, IV, VI invoked here).

### Changelog

| Version | Date | Note |
|---|---|---|
| 0.1 | 2026-05-17 | Initial policy (SES-a51816). Hybrid generic-first; scoped to cc__credit; collapses four in-flight pilot rows from 3 ADMIT_READY + 1 DUPLICATE_OR_MERGE to 2 new generic BFs + 4 CF rebinds. |
