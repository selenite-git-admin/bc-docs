---
title: BCF × OAGIS Pass 1 C1 Packet-Builder v2 Design (2026-06-24)
description: Held design for the corrected Pass 1 C1 candidate-packet builder under DEC-f94895. Diagnoses the v1 (executor) packet-construction defects responsible for the 25 OPERATOR_REVIEW + 1 REJECT outcomes against substantive evidence, classifies the defect as packet-construction (not panel/system failure and not substrate failure), specifies the corrected packet-construction discipline, and reclassifies the 40 C1 rows into five disposition buckets with a projected NEW panel-call count of 3 (plus 2 C5 confirms held over from the prior run). No panels, no confirmations, no F3/F4 writes, no substrate mutation.
status: held
authority: dec-f94895 + operator-stated v2 packet discipline 2026-06-24
date: 2026-06-24
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-c1-packet-discipline
related_docs:
  - bcf-oagis-broad-buildout-blueprint-2026-06-23.md
  - bcf-oagis-compile-report-2026-06-24.md
  - bcf-oagis-retry-ledger-2026-06-24.md
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
  - bcf-oagis-pass-1-c1-closeout-2026-06-24.md
related_adrs:
  - DEC-f94895
related_sessions:
  - SES-dfac49
---

# BCF × OAGIS Pass 1 C1 Packet-Builder v2 Design (2026-06-24)

> **Status of Pass 1 C1.** Halted by operator at 28/40 outcomes (2 APPROVE_FOR_DRAFT, 25 OPERATOR_REVIEW, 1 REJECT; 0 cert minted; substrate unchanged at 26 / 62 / 194). Operator classification accepted: the failure mode is **C1 candidate-packet-construction defect**, not panel-tooling failure, not substrate failure, not §8.4 systemic stop. Remaining seq 29–40 held. The 2 APPROVE_FOR_DRAFT held over for C5 confirm. No panels until corrected v2 packet discipline is in force.

## 1. Defect diagnosis — v1 executor `_pass1-c1-execute.mjs`

| Construct | v1 source line | Construction | M-checklist failure observed in panel feedback |
|---|---|---|---|
| `proposedName` | `_pass1-c1-execute.mjs:121` → calls `'toSpacedLowercase()' at :85` | `bfName.replace(/_/g, ' ').toLowerCase()` — mechanical lift of OAGIS field-path slug | **M9 source-field-copy** ("term appears copied from the OAGIS source field name", "near-verbatim from source element name") — observed ~18 of 26 non-APPROVE rows |
| `definition` | `_pass1-c1-execute.mjs:122` → `'buildProposedDefinition()' at :88-92` | Template `"A coded value identifying the ${term} of the associated entity. Code-typed dimension sourced from the OAGIS 10.12 vocabulary."` — restates the term ("circular by construction") and embeds source attribution as part of meaning | **M8 circular definition** ("definition restates the term", "definition is circular/tautological") — observed ~20 of 26 non-APPROVE rows |
| `citedText` | `_pass1-c1-execute.mjs:124` | `oagis.description.slice(0, 200)` — uses whatever the enrichment pass landed; for 2 of 28 rows (`type_code`, `harmonized_tariff_schedule_code`) this is OAGIS standalone-page XSD primitive-lineage boilerplate ("Data Type Description … data type primitives …") rather than business meaning; for many others it is a thin field gloss | **M2 thin / boilerplate citation** ("candidateEvidence describes only technical XSD primitive lineage, not a substantive business meaning", "thin field gloss") — observed in 5+ rows explicitly + drives most "not evidence-backed Global" parks |
| `classification` (Global rationale) | (absent) — DTO has no `classification` field and v1 supplies no Global rationale | The F4-v2 panel must infer Global from the single OAGIS citation alone; with single-field citations from role-specific OAGIS leaves, the panel correctly refuses to certify Global | **Non-Global classification** ("classification is not explicit and evidence-backed Global", "single OAGIS leaf-citation does not establish cross-system or cross-industry governed characteristic status") — observed ~24 of 26 non-APPROVE rows |
| `evidenceHash` | `_pass1-c1-execute.mjs:126` | `sha256(citedText + '|AR-3+AR-4')` — fingerprint over a single field | Causes one false collision (`type_code` ↔ `harmonized_tariff_schedule_code` both XSD-boilerplate citedText) and does not protect retry from re-issuing the same panel input; the hash is not a panel-input fingerprint, just a citedText fingerprint |

### Why these defects produced 89% non-APPROVE

The F4-v2 v1 Vocabulary Admission Checklist gates createCharacteristic on:
- **M2** — candidateEvidence substantively establishes meaning (not boilerplate, not source-field tautology)
- **M5** — term is not a synonym/near-duplicate of existing substrate
- **M6** — term is not a bare representation term
- **M8** — definition is non-circular genus + differentia (does not restate term, does not embed source attribution)
- **M9** — term is an authored business characteristic, not a direct lift of source field name
- **classification=global** with **explicit evidence-backed Global rationale** (single role-specific OAGIS leaf is insufficient)

The v1 packet structurally cannot pass **M8** (template hardcodes circular def), structurally cannot pass **M9** (proposedName is the bf_name lift), and cannot supply **classification=global** rationale. M2 is variable — passes when OAGIS gloss is substantive, fails when OAGIS gloss is XSD boilerplate. So every v1 candidate enters with three structural failures already baked in.

The 2 APPROVE_FOR_DRAFT exceptions (`transportation_method_code`, `incoterms_code`) cleared M8 and M9 only because the underlying business meaning is genuine (substantive OAGIS glosses, standards-backed: ICC Incoterms; generally-recognised carrier transportation classification) — the panel rescued them despite the v1 packet. The 25 OPERATOR_REVIEW + 1 REJECT did not have a strong enough underlying meaning to overcome the v1 packet's structural M8/M9/Global failures.

## 2. Panel-infrastructure non-failure confirmation

| Check | Result | Source |
|---|---|---|
| All 28 calls returned HTTP 200 | ✓ | `pass1-c1-outcomes-2026-06-24.jsonl` |
| 28 distinct panelRunUids minted by bc-core | ✓ | `bcf.panel_output_record` |
| `grounding_check_result = pass` on all 28 | ✓ | `bcf.panel_output_record` |
| `quarantined = false` on all 28 | ✓ | `bcf.panel_output_record` |
| 0 service errors, 0 panel_not_found, 0 auth errors | ✓ | outcomes JSONL |
| 27 of 28 produced a substantive maker payload (1 row had Maker null-draft — seq 23 `shipping_uom_code`; Checker still carried substantive concerns — defect-isolated, not systemic) | ✓ | `bcf.panel_output_record.verdict_payload_json` |
| Verdict distribution: 2 APPROVE_FOR_DRAFT, 25 OPERATOR_REVIEW, 1 REJECT (PROV_FABRICATED) — three distinct verdicts demonstrate panel is differentiating substantively, not defaulting | ✓ | per-row review_reason payloads each substantively distinct |

**§8.4 systemic halt is NOT triggered.** Panel infrastructure is healthy; the 89% non-APPROVE rate is a candidate-packet quality signal.

## 3. Corrected packet-construction discipline (v2)

A v2 packet for any Pass 1 C1 row must satisfy every rule below. Rows that cannot satisfy them are pre-panel-filtered into one of the four non-panel buckets (§4).

### 3.1 `proposedName`

- **Authored, not transliterated.** Must NOT be `bfName.replace(/_/g, ' ').toLowerCase()`.
- **Reject source-field-copy** where the OAGIS field is role-specific. If the proposed name is structurally a kebab-to-space transliteration of the OAGIS field slug (e.g. `distribution-center-code` → "distribution center code"), the row is held into `operator_semantic_decision` unless the OAGIS gloss establishes the term as the substantive head noun (e.g. `transportation-method-code` → "transportation method code" survived only because "transportation method" is the substantive head, "code" the representation form).
- **Collapse role-qualified fields to existing broader substrate characteristic** when a substrate match exists. Specifically:
  - `destination_country_code`, `origination_country_code` → role placement on existing `country code` (substrate id `ce27c255-…`), not a new char.
  - Future C-waves: any OAGIS `<role>_currency_code` field → existing `currency code` / `source currency code` / `target currency code` substrate row; do not author duplicate.
- **Acronym expansion.** "uom" / "capa" / "rfq" / "po" / "sla" expanded ("unit of measure" / "corrective action preventive action" / …) before the term enters a v2 packet.
- **Reject bare representation terms.** "code" / "identifier" / "indicator" / "amount" / "quantity" / "date" alone are not characteristics (M6 rep-term leakage). Auto-routed to `defer_insufficient_evidence`.

### 3.2 `definition`

- **Genus + differentia.** Format: "A {representation form} naming the {differentia} — drawn from {governance scope}. Distinct from {nearby characteristic 1}, {nearby characteristic 2}." The genus carries the representation form (a coded value, an identifier, an amount, …); the differentia carries the substantive business meaning (the *what*, not the *that-it-is-a-code*).
- **Must NOT restate the term.** Templates of the form "A coded value identifying the X" where X is the proposed name are forbidden — that is M8 circular by construction.
- **Must NOT embed source attribution as meaning.** "sourced from OAGIS" / "as defined in SAP" do not belong inside the definition. Source attribution lives in `candidateEvidence.sourceLabel`, never in the definition body.
- **Must distinguish Global from entity placement role.** When a characteristic is role-qualified at use site (e.g. destination country, source currency), the definition must name the substantive value property, not the placement role.

### 3.3 `citedText`

- **Use substantive OAGIS business gloss.** Pull the per-noun field description from the noun page, not the standalone-page primitive-lineage description, when both are available.
- **Reject XSD primitive-lineage boilerplate.** Markers: `"Data Type Description"`, `"data type primitives"`, `"Schema expressions and implementation refinements"`. Rows whose only available OAGIS text matches these markers are pre-filtered to `defer_insufficient_evidence` and **do not enter a panel**.
- **Reject explicitly partner-negotiated semantics.** Markers: `"agreed upon between trading partners"`, `"user defined"`, `"can be used in a variety of contexts"`. Pre-filter to `defer_insufficient_evidence`.
- **Reject context-dependent / polysemous citations** where the OAGIS gloss explicitly says the value differs by context.
- **Length cap 200 chars** preserved.

### 3.4 Global classification rationale

The v2 packet must include an explicit `global_rationale` field documenting **at least one** of:
- **Standards-backed**: cite the Global standard (ISO 20022, ISO/IEC 5218, UN/CEFACT TDED, OAGIS code list, ICC Incoterms, NACE, etc.). One named standard that publishes the Global enumeration is the strongest signal.
- **Cross-entity reuse**: name three or more business concepts (existing substrate or planned C/E waves) that share this characteristic in the same semantic role.
- **Sibling substrate pattern**: cite an existing substrate Global characteristic with the same standards-backed enumerated shape (e.g. `currency code`, `country code`, `industry code`) and demonstrate that the candidate follows the same pattern.

If none of those three can be supplied with a real citation (not template text), the row is pre-filtered to `defer_insufficient_evidence` or `operator_semantic_decision`. F4-v2 v1 admits only Global; non-Global candidates do not go to panel.

> **DTO note.** The current F4-v2 DTO does NOT carry a `classification` or `global_rationale` field — `candidateEvidence` is a 2-tuple (`sourceLabel`, `citedText`). The v2 packet records the rationale as an *operator-side audit artifact* in the packet JSON, and the corrected `citedText` is constructed to include the standard-name citation inline when needed. A future F4-v2 DTO extension to admit a structured `classification` block is a separate work item; v2 lives within the current DTO.

### 3.5 Pre-panel filter (mandatory)

Before any panel call, every row passes through a deterministic filter:

```
INPUT  : row + OAGIS field record + substrate snapshot
OUTPUT : disposition ∈ {
           panel_ready_retry,
           confirm_existing_approval_later,
           defer_insufficient_evidence,
           map_to_existing_characteristic,
           operator_semantic_decision
         }

if substrate has an active characteristic whose term is a stem-match
    or known-synonym of the proposedName:
        disposition = map_to_existing_characteristic
elif row has a prior_verdict == 'APPROVE_FOR_DRAFT' on its prior_panel:
        disposition = confirm_existing_approval_later
elif OAGIS gloss matches XSD_BOILERPLATE
     or matches PARTNER_NEGOTIATED
     or matches POLYSEMOUS_CONTEXT
     or proposedName is a bare representation term:
        disposition = defer_insufficient_evidence
elif Global rationale cannot be established
     (no standard, no cross-entity reuse ≥ 3, no sibling pattern):
        disposition = operator_semantic_decision
else:
        disposition = panel_ready_retry
```

Implementation: `barecount-devhub/scripts/_pass1-c1-packet-builder-v2.mjs` — deterministic, no LLM, no panel calls, no writes. Outputs `barecount-devhub/.claude/pass1-c1-packet-builder-v2-2026-06-24.json`.

### 3.6 Retry handling and packet-hash

- The 26 rows that parked or rejected in the first run **must not** be retried under their original packet. Each retry under v2 carries a NEW `packetHash` because the v2 fingerprint is `sha256(proposedName ‖ definition ‖ sourceLabel ‖ citedText ‖ classification ‖ global_rationale ‖ shape_tuple)` — NOT the v1 `sha256(citedText ‖ AR-digest)` flaw. Any of these inputs changing produces a distinct hash, so a v2 retry packet shares no input with the v1 attempt and the panel sees a genuinely new candidate.
- candidateRef under v2 is `pass1-c1-v2-XX-<bf>` to distinguish from the v1 `pass1-c1-XX-<bf>` ledger trail.
- The 28 original outcomes stay preserved in `pass1-c1-outcomes-2026-06-24.jsonl` and in `bcf.panel_output_record` as audit history. The v2 retry does not delete or rewrite that history; it stamps new panel_run_uids alongside.

## 4. Reclassified C1 queue — 40 rows into 5 buckets

Authority: per-row OAGIS gloss + per-row panel review_reason payload from `bcf.panel_output_record` for the 28 already-attempted rows. Inferred for 12 unstarted rows (seq 29–40) from OAGIS gloss + substrate vocabulary check.

### 4.1 `panel_ready_retry` — 3 rows

These rows can be issued v2-packet panels because each has substantive OAGIS evidence, a clear standards-backed Global rationale, and a non-circular authored definition.

| seq | bf_name | v2 proposedName | Global rationale (summary) | prior verdict |
|---:|---|---|---|---|
| 2 | `payment_method_code` | payment method code | Standards-backed ISO 20022 ExternalPaymentMethod1Code + OAGIS PaymentMethod code list; cross-entity reuse across customer payment / vendor payment / remittance / three-way-match; sibling pattern with `currency code`. | OPERATOR_REVIEW |
| 38 | `gender_code` | **sex code** (corrected to ISO/IEC 5218 canonical) | Standards-backed ISO/IEC 5218 publishes Global enumeration (0/1/2/9); cross-entity reuse on any person-related entity; sibling pattern with `country code`, `industry code`. | (no prior — unstarted) |
| 39 | `marital_status_code` | marital status code | Standards-backed UN/CEFACT TDED + national stat agencies publish Global enumeration; cross-entity reuse on any person-related entity; sibling pattern with `country code`. | (no prior — unstarted) |

### 4.2 `confirm_existing_approval_later` — 2 rows

These rows already received `APPROVE_FOR_DRAFT` under v1. Panel passed M1–M10 because the underlying business meaning was strong enough to rescue the v1 packet. Held for C5 operator confirm; do not re-panel.

| seq | bf_name | proposedName (held from v1) | C5 endpoint | prior verdict |
|---:|---|---|---|---|
| 3 | `transportation_method_code` | transportation method code | `POST /api/bcf/registry-shape-certifications/confirm` `{panelRunUid: c67cd794-…, subjectKind:"characteristic", actionCode:"registry_author_vocabulary", rationale}` | APPROVE_FOR_DRAFT |
| 5 | `incoterms_code` | incoterms code | same endpoint, `panelRunUid: 4b47792c-…` | APPROVE_FOR_DRAFT |

### 4.3 `defer_insufficient_evidence` — 8 rows

OAGIS gloss is XSD boilerplate, partner-negotiated, polysemous, or thin; the row cannot be made panel-ready under current evidence.

| seq | bf_name | Reason |
|---:|---|---|
| 10 | `ownership_code` | OAGIS explicit: "content … user defined based on a specific Customer or Supplier" — partner-negotiated, no Global meaning |
| 11 | `harmonized_tariff_schedule_code` | OAGIS standalone-page returns XSD primitive-lineage boilerplate; HTS is customs/import-export-specific (WCO standard) not Global cross-industry |
| 19 | `schedule_type_code` | OAGIS explicit: "can be used in a variety of contexts" — polysemous |
| 20 | `usage_restriction_code` | OAGIS explicit: "implementation is to be agreed upon between trading partners" |
| 22 | `tracking_method_code` | OAGIS: "list of codes associated with the appropriate method of tracking a program" — thin, no substantive examples or standards-backing |
| 36 | `end_sequence_code` | Narrow production-domain; ambiguous; rep-term-shaped |
| 37 | `code` | Bare "code" — pure rep-term leakage (M6); OAGIS gloss "Element for the communication of all codes" |
| 40 | `capa_resource_type_code` | Narrow CAPA/quality domain; "capa" acronym unexpanded; thin |

### 4.4 `map_to_existing_characteristic` — 2 rows

Substrate already holds the Global parent; the OAGIS field encodes a role placement, not a new characteristic.

| seq | bf_name | Map to | Substrate id |
|---:|---|---|---|
| 16 | `destination_country_code` | `country code` | `ce27c255-e720-40dc-9d62-54c5516d28c4` |
| 34 | `origination_country_code` | `country code` | `ce27c255-e720-40dc-9d62-54c5516d28c4` |

Disposition: at Pass 3 BC binding, both bind to the existing `country code` characteristic with a placement-role qualifier (`destination` / `origin`) on the BC binding metadata, not a new substrate row.

### 4.5 `operator_semantic_decision` — 25 rows

These rows have substantive OAGIS evidence and are admissible, but Global scope is ambiguous and an operator framing decision is required before any v2 packet can be authored. Decisions typically fall into:
- **Admit a broader Global parent first, then qualify at BC binding** (UOM family seq 7/8/23/24; location family seq 6/29/30/31).
- **Decide between Global admit vs domain-specific char admit** under a new domain-admission policy (procurement, logistics, HR, customs, project-accounting, inventory).
- **Decide between admit vs map_to_existing** (seq 9 `freight_term_code` vs substrate `payment terms`).
- **Rename and re-evaluate** (seq 18 `date_code` → `schedule dating mode code` per OAGIS evidence).
- **Decide root-vs-leaf admission** (seq 1 `type_code` — admit Global parent or require all uses to bind to existing role-specific *_type_code chars).

| seq | bf_name | Operator decision required |
|---:|---|---|
| 1 | `type_code` | Generic vs role-specific; substrate already holds `document type code`, `account type code`, `adjustment type code`; decide Global parent admit or require role-specific bindings |
| 4 | `special_price_authorization_code` | Supplier-internal authorization reference; non-Global vs domain admit |
| 6 | `distribution_center_code` | Location-family parent admit (`location code` / `facility code`) first or logistics-domain admit |
| 7 | `base_uom_code` | UOM-family parent admit (`unit of measure code`, UN/CEFACT Rec 20 / UCUM) first |
| 8 | `storage_uom_code` | UOM-family — same |
| 9 | `freight_term_code` | Admit as Global `freight payment terms` or map to substrate `payment terms` |
| 12 | `transaction_analysis_code` | Project-accounting domain admit vs Global `ledger analysis code` |
| 13 | `first_agent_payment_method_code` | Admit as Global payment-chain qualifier or treat as specialization of seq 2 `payment method code` |
| 14 | `job_code` | HR/workforce domain admit |
| 15 | `shipment_service_level_code` | Logistics-domain admit; see also seq 28 |
| 17 | `freight_classification_code` | Logistics-domain admit (NMFC class code) |
| 18 | `date_code` | Rename to substantive (`schedule dating mode code`) and re-evaluate; bare "date code" is misleading per OAGIS (Ship/Deliver enum) |
| 21 | `formulation_code` | Customs/trade-compliance domain admit |
| 23 | `shipping_uom_code` | UOM-family — same parent decision |
| 24 | `alternate_uom_code` | UOM-family — same |
| 25 | `expiration_control_code` | Inventory-domain admit |
| 26 | `source_type_code` | Procurement-domain admit (make-or-buy) |
| 27 | `financial_match_code` | Could be Global as `invoice match type code`; operator framing decision |
| 28 | `carrier_service_level_code` | Logistics-domain; admit alongside seq 15 or merge |
| 29 | `point_of_loading_code` | Location-family — same parent decision |
| 30 | `point_of_shipment_code` | Location-family — same |
| 31 | `point_of_staging_code` | Location-family — same |
| 32 | `receipt_routing_code` | Admit as Global `material condition code` (OAGIS-listed synonym) or receipt-domain admit |
| 33 | `sequence_code` | Bare "sequence code" rep-term-shaped; admit broader `sequence position` / `ordinal position` or defer |
| 35 | `wage_type_code` | HR/payroll domain admit |

## 5. Expected new panel-call count after pre-panel filtering

| Surface | Count |
|---:|---|
| `panel_ready_retry` rows | **3** |
| Expected NEW panel calls in next run | **3** |
| Expected C5 confirms (held over) | 2 (no new panels for these) |
| Expected substrate writes if all 3 panel + 2 confirms succeed (no further parks) | at most 5 new characteristics |
| Rows held without panel | 35 (8 defer + 2 map + 25 operator decision) |

Reduction vs v1 attempted total: from 40 planned → 3 actually panel-eligible under corrected discipline (92.5% reduction in panel volume by pre-filtering). Of the 3, all are standards-backed Global (ISO 20022 / ISO/IEC 5218 / UN/CEFACT TDED), so the v2 packets clear M2/M8/M9 and Global rationale by construction.

## 6. Validity of the 2 APPROVE_FOR_DRAFT rows under corrected discipline

**Preserved.** Both rows remain valid:

- **seq 3 `transportation_method_code`** — panel's APPROVE rested on the substantive OAGIS gloss ("Identifies the general type of carrier transportation used to deliver goods") + the head noun "transportation method" carrying business meaning while "code" is representation form, plus a passing Global classification grounded in "logistics/shipping value property and its reuse across entities that record shipment, delivery, or freight movement". Under v2 packet construction (substantive citedText preserved, non-circular def, explicit Global rationale: cross-entity reuse + sibling code-typed pattern), the same panel result is expected. The v2 packet is *strictly stronger*, not weaker, than what the panel already approved.
- **seq 5 `incoterms_code`** — same logic; ICC Incoterms is a published Global standard, substantive OAGIS gloss is preserved. v2 packet strictly stronger.

Both can be confirmed via C5 immediately when the operator authorizes — no re-panel needed under v2 discipline. If operator preference is to re-issue them under v2 for hash/audit parity with the other panel_ready_retry rows, that is also allowed (the v2 packet would be a fresh panelRunUid; the v1 panelRunUid remains valid for C5 confirm in parallel). Default recommendation: confirm the existing v1 APPROVE_FOR_DRAFTs as-is and reserve panel calls for the 3 panel_ready_retry rows.

## 7. Implementation pointer

`barecount-devhub/scripts/_pass1-c1-packet-builder-v2.mjs` — deterministic builder, encodes per-row disposition and v2 packet content; runs read-only; produces `barecount-devhub/.claude/pass1-c1-packet-builder-v2-2026-06-24.json`.

Output verified: 3 distinct packetHashes for the 3 panel_ready_retry rows (no collisions); v2 hashes differ from v1 hashes by construction (different inputs).

## 8. Non-actions

- No panel calls.
- No C5 confirms.
- No F3 / F4 writes.
- No substrate mutation. `concept_registry.*` row counts unchanged at 26 / 62 / 194.
- No new `bcf.panel_output_record` rows since 2026-06-24T06:00:15Z (last v1 row).
- v1 executor `_pass1-c1-execute.mjs` is preserved as audit history; the v2 builder is a separate file.
- Retry ledger `execution_start_gate` remains `running_pass_1_c1` pending operator decision on the v2 retry queue.

Held. Awaiting operator decision on whether to (a) authorize the 3 v2 panel calls + 2 C5 confirms, (b) defer all C1 work pending the 25 `operator_semantic_decision` rows being resolved upstream, or (c) other direction.
