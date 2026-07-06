---
title: BCF × OAGIS Pass 1 C1 RP-3 Packet Prep — Taxonomy Refresh (2026-06-25)
description: Held packet-prep summary for C1 RP-3, revision r3 — platform-native taxonomy. Scopes are now cross_function / function_scoped / industry_scoped (replacing the prior cross_domain / domain_scoped wording). 15 packets total — 12 panel-ready (immediate transport set), 1 confirmed to substrate (freight terms code), 2 held for operator source-evidence re-check. Token scrub clean. Hash deny-list extended with the prior RP-3 r2 outcomes. Substantive content unchanged except for two non-mechanical re-scopes (process step number cross_domain → function_scoped/operations_planning; product formulation reference domain_scoped → industry_scoped/process_manufacturing). No panel calls, no C5 confirms, no substrate mutations, no retry-ledger writes.
status: held
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-c1-rp3-packet-prep
related_docs:
  - bcf-oagis-pass-1-c1-rp2-parked-row-analysis-2026-06-25.md
  - bcf-oagis-pass-1-c1-operator-decision-packet-2026-06-25.md
---

# BCF × OAGIS Pass 1 C1 RP-3 Packet Prep — Taxonomy Refresh (2026-06-25)

> Held packet-prep summary, revision r3. Platform-native taxonomy applied. **12 panel-ready (held for transport) + 1 confirmed to substrate + 2 held for operator review = 15 packets total.** Substantive content preserved except two non-mechanical re-scopes (§4).

## 1. Taxonomy reconciliation note

The earlier RP-3 prep summary used `cross_domain` and `domain_scoped` scope labels. "Domain" is ambiguous in BareCount — it can refer to source domain, industry domain, bounded context, or business function — so the platform-native axes (business function / subfunction / industry) are used instead.

**Why `domain_scoped` was retired.** It conflated three distinct ideas: a business function (workforce_payroll, accounting), an industry (process manufacturing), and a regulatory regime. Each of those has different evidence requirements and different downstream implications for catalog organisation, ramp gates, and stakeholder mapping. Conflating them into one scope class hid those differences.

**Replacement scopes (all three valid for admission):**

| Scope | Definition |
|---|---|
| `cross_function` | A system-agnostic characteristic valid across multiple business functions. Example: country code (ISO 3166) is used in logistics, customs, HR jurisdiction, treasury, tax. |
| `function_scoped` | A system-agnostic characteristic valid inside a business function or subfunction. **Not** source-system-specific. **Not** vendor-field leakage. Example: wage type code is observed across multiple HR/payroll systems and labour-rights frameworks within the workforce-payroll function. |
| `industry_scoped` | A system-agnostic characteristic valid because a specific industry or regulatory context demands it. Use only when the scope is truly an industry or regulatory regime, not merely a business function. Example: product formulation reference exists because chemical / pharmaceutical / food / cosmetic / beverage industry-regulatory regimes (FDA, EMA, ICH IDMP, ISO 22000) require ingredient-composition traceability that discrete-manufacturing industries do not need. |

**`function_scoped` is not source-system-specific.** A function-scoped characteristic must be evidenced across at least two systems / standards / frameworks within the same business function, with an explicit function name, system-agnostic term, and definition that survives onboarding a second source system. A characteristic that exists only in one ERP module or one source-field is `source_system_specific` (invalid), not `function_scoped`.

**Most BareCount characteristics may be scoped.** Universal / cross-function is not the default requirement. The previous admission policy's implicit assumption that all governed characteristics must be cross-industry global is too strong; the corrected doctrine accepts any of `cross_function`, `function_scoped`, or `industry_scoped` provided the scope is explicit, evidence-backed, and not source / system / local leakage.

**Invalid scope classes (unchanged):** `source_system_specific`, `local_alias`, `implementation_artifact`, `source_field_copy`, `semantic_duplicate`.

## 2. Counts

### 2.1 Disposition counts

| Disposition | Count | Rows |
|---|---:|---|
| `panel_ready_retry` (immediate transport set) | **12** | rows 01, 02, 04, 06, 07, 09–15 (skipping 03 which is confirmed, and 05 + 08 which are held) |
| `confirmed_to_substrate` | **1** | row 03 freight terms code (cert `a1729d06`, characteristic `1e698556`, lifecycle draft, 2026-06-24T12:17:43Z) |
| `held_source_evidence_recheck` | **2** | row 05 (receipt routing code), row 08 (job code) |
| **Total packets in prep state** | **15** | |

### 2.2 Scope distribution (across all 15 packets)

| Scope | Count | Rows |
|---|---:|---|
| `cross_function` | **5** | row 01 (location), row 02 (transport service level), row 03 (freight terms — confirmed), row 06 (item sourcing strategy), row 11 (item ownership type) |
| `function_scoped` | **7** | row 04 (process step number / operations_planning), row 07 (schedule type / operations_planning), row 09 (wage type / workforce_payroll), row 10 (negotiated price authorization reference / pricing_commercial), row 12 (transaction analysis / accounting), row 14 (expiration control / inventory_perishables_management), row 15 (quality action resource category / quality_management) |
| `industry_scoped` | **1** | row 13 (product formulation reference / process_manufacturing) |
| `pending_operator_review` | **2** | row 05 (receipt routing code), row 08 (job code) |
| **Total** | **15** | |

### 2.3 Immediate transport set (12 panel-ready)

Excluding the confirmed-to-substrate row (03) and the two held rows (05, 08):

| Scope | Count | Rows |
|---|---:|---|
| `cross_function` | 4 | location code, transport service level code, item sourcing strategy code, item ownership type code |
| `function_scoped` | 7 | process step number (operations_planning), schedule type code (operations_planning), wage type code (workforce_payroll), negotiated price authorization reference (pricing_commercial), transaction analysis code (accounting), expiration control code (inventory_perishables_management), quality action resource category code (quality_management) |
| `industry_scoped` | 1 | product formulation reference (process_manufacturing) |
| **Total transport-pending** | **12** | |

## 3. Per-row table

| # | candidateRef | proposedName | Old scope (r2) | New scope (r3) | Old fn/domain | New fn / industry | Disposition | panel_packet_hash (head) | Hash changed from r2? |
|---:|---|---|---|---|---|---|---|---|---|
| 01 | pass1-c1-rp3-01-location_code | location code | cross_domain | cross_function | — | — | panel_ready_retry | fcbfd42742d771ec… | yes |
| 02 | pass1-c1-rp3-02-transport_service_level_code | transport service level code | cross_domain | cross_function | — | — | panel_ready_retry | 8dbbb15275442c76… | yes |
| 03 | pass1-c1-rp3-03-freight_terms_code | freight terms code | cross_domain | cross_function | — | — | **confirmed_to_substrate** | 54d7221f97e4f3ad… | yes |
| 04 | pass1-c1-rp3-04-process_step_number | process step number | cross_domain | **function_scoped** | — | operations_planning | panel_ready_retry | a2770b62182b7caf… | yes |
| 05 | pass1-c1-rp3-05-receipt_routing_code_HELD | receipt routing code | pending_operator_review | pending_operator_review | — | — | held_source_evidence_recheck | 0528daf70a84b600… | no (hold-row content unchanged) |
| 06 | pass1-c1-rp3-06-item_sourcing_strategy_code | item sourcing strategy code | cross_domain | cross_function | — | — | panel_ready_retry | bcbd69696c080eba… | yes |
| 07 | pass1-c1-rp3-07-schedule_type_code | schedule type code | domain_scoped | function_scoped | scheduling_operations | operations_planning | panel_ready_retry | 3a26e0d8603f1147… | yes |
| 08 | pass1-c1-rp3-08-job_code_HELD | job code | pending_operator_review | pending_operator_review | — | — | held_source_evidence_recheck | 8e2be34f76433258… | no (hold-row content unchanged) |
| 09 | pass1-c1-rp3-09-wage_type_code | wage type code | domain_scoped | function_scoped | workforce_payroll | workforce_payroll | panel_ready_retry | 52363ecd65c8e932… | yes |
| 10 | pass1-c1-rp3-10-negotiated_price_authorization_reference | negotiated price authorization reference | domain_scoped | function_scoped | pricing_commercial | pricing_commercial | panel_ready_retry | 737378877ed0eb68… | yes |
| 11 | pass1-c1-rp3-11-item_ownership_type_code | item ownership type code | cross_domain | cross_function | — | — | panel_ready_retry | 600904297dbd3b15… | yes |
| 12 | pass1-c1-rp3-12-transaction_analysis_code | transaction analysis code | domain_scoped | function_scoped | accounting | accounting | panel_ready_retry | aeeb4c08f74a88a5… | yes |
| 13 | pass1-c1-rp3-13-product_formulation_reference | product formulation reference | domain_scoped | **industry_scoped** | product_production_quality | process_manufacturing | panel_ready_retry | d95a5a213ad45867… | yes |
| 14 | pass1-c1-rp3-14-expiration_control_code | expiration control code | domain_scoped | function_scoped | inventory_perishables_management | inventory_perishables_management | panel_ready_retry | 313834582cad0c9d… | yes |
| 15 | pass1-c1-rp3-15-quality_action_resource_category_code | quality action resource category code | domain_scoped | function_scoped | quality_management | quality_management | panel_ready_retry | 6c6b26611105b78e… | yes |

## 4. Non-mechanical scope changes

Two rows changed scope in a non-mechanical way (beyond the cross_domain → cross_function and domain_scoped → function_scoped relabel):

### 4.1 Row 04 — process step number: cross_domain → function_scoped / operations_planning

- **Reason for re-scope.** The prior r2 packet claimed `cross_domain` based on a four-context reach (manufacturing-operations, production-sequencing, process-control, logistics). The r2 panel transport rejected the row with the substantive reason "Global classification is not evidence-backed. The cited evidence supports manufacturing / production-operations usage (APICS work-order operation sequence, ISA-95 operations-management, SAP PP routing, Oracle Process Manufacturing) but does not establish cross-industry Global applicability." The panel's reading is correct against the evidence: all the cited anchors are operations / manufacturing systems within the broader operations-planning function. The logistics-manifest reach was thin.
- **r3 scope.** `function_scoped` / `operations_planning`. The value-property is observed across multiple operations-planning systems and standards (APICS, ISA-95, SAP PP, Oracle Process Manufacturing) — solidly multi-system within one business function. Distinct from substrate 'line number' (document-line ordinal) remains the M-distinctness anchor.
- **Effect on transport.** The row stays in the immediate transport set; only the scope and rationale are relabeled.

### 4.2 Row 13 — product formulation reference: domain_scoped → industry_scoped / process_manufacturing

- **Reason for re-scope.** The prior r2 packet claimed `domain_scoped` with domain `product_production_quality`. Reviewing the evidence, the value-property is required specifically because process-manufacturing industries (chemical, pharmaceutical, food, cosmetic, beverage) are regulated by composition-traceability regimes (FDA Substance Registration System, ICH IDMP Pharmaceutical Product Identifier, EMA Annex 16, ISO 22000 food-safety, GS1 GDSN for cross-trading-partner product master) that discrete-manufacturing industries do not have an equivalent need for. The driver is industry-regulatory, not a generic business function.
- **r3 scope.** `industry_scoped` / `process_manufacturing`. The industry context is explicit (the formulated-product manufacturing verticals); the evidence is substantive across both industry-regulatory anchors (ICH IDMP, FDA SRS, ISO 22000, EMA) and the ERP-side anchors that implement those requirements (SAP PP-PI, Oracle OPM, GS1 GDSN).
- **Effect on transport.** The row stays in the immediate transport set; the scope class changes from `function_scoped` to `industry_scoped`. The packet's `industry` field is set to `process_manufacturing`; `business_function` is null.

## 5. Held rows — operator decisions needed

Unchanged from the r2 prep summary; carried forward.

### 5.1 Row 05: receipt routing code (seq 32)

Three coupled operator decisions (term name / value-property scope / distinction from substrate 'status'). Recommended path: keep the OAGIS-canonical name 'receipt routing code', framed as 'receipt routing decision'. See packet `operator_review_summary` for full detail.

### 5.2 Row 08: job code (seq 14)

Four candidate readings (workforce job/work-role classification / project-accounting job-number identification / map-to-existing / propose-different-term). Recommended: confirm workforce job-classification reading. See packet `operator_review_summary` for full detail.

## 6. Verification results

| Check | Result | Notes |
|---|---|---|
| Forbidden-token scan on authored prose fields | **0 hits** | Scrubbed fields: definition, candidateEvidence.citedText, semantic_identity_reason, standards_notes, cross_function_rationale, function_rationale, industry_rationale. Patterns include M-codes, AR-codes, pipeline tokens, ADR identifiers, internal verdict codes, wave codes, doctrine section references. |
| Substrate exact-term collisions | **0 / 15** | Substrate now 76 non-archived terms (62 active + 14 draft; freight terms code is the new draft). The confirmed_to_substrate row (03) is correctly NOT flagged as a collision since it represents the row's graduation, not a duplicate authoring attempt. |
| Hash deny-list collisions | **0 / 15** | Deny-list extended to **79 entries** = 40 v1 + 3 v2_builder + 3 v2_outcomes + 2 dpo_r1 + 22 rp2 + **13 rp3_r2** (new). All 15 r3 hashes are new and distinct from r2 (terminology changes in prose flow into the hash inputs). |
| Token scrub on all authored fields | **clean** | 0 hits across 15 packets × 6 scanned fields. |

## 7. Output artefacts

Generator: `barecount-devhub/scripts/_desktop-prep-output-c1-rp3.mjs` (deterministic; re-running yields identical hashes).

Output directory: `barecount-devhub/.claude/desktop-prep-output-c1-rp3-2026-06-25/`

| Artefact | Purpose |
|---|---|
| `packets/c1-rp3/pass1-c1-rp3-*.json` (15 files) | One JSON per RP-3 row. Panel-ready packets carry definition, citedText, classification, scope, business_function (for function_scoped) / industry (for industry_scoped). Confirmed-to-substrate row carries a `confirmation_record` field. Held packets carry hold_reason + operator_review_summary. |
| `manifest.json` | sha256 per packet file |
| `prep-summary.json` | Disposition counts, scope distribution, deny-list summary, collision-check results, token-scan results |

## 8. Scope locks honored

- 0 panel calls.
- 0 C5 confirms.
- 0 substrate mutations.
- 0 retry-ledger writes.
- 0 C2 entry.
- Files written: 1 generator-script revision + 17 prep-output artefacts (15 packet JSONs + manifest + summary) + 1 prep-summary doc rewrite + 1 analysis-doc §1.5.2 addition.

## 9. Next gate

**Operator decisions required before RP-3 r3 transport:**

1. **Authorize the immediate transport set of 12 panel-ready packets.**
2. **Decide row 05 (receipt routing code)** — three coupled term / scope / distinction questions per §5.1.
3. **Decide row 08 (job code)** — choose between readings (a) / (b) / (c) / (d) per §5.2.

The transport set is **semantically identical apart from taxonomy wording**, with the two non-mechanical re-scopes documented in §4. The cross-source citations, definitions, and distinctness arguments are unchanged across all 12 panel-ready rows.

A separate workstream remains: the durable ADR / runtime-policy fix to allow `function_scoped` and `industry_scoped` admission to APPROVE (rather than being routed to OPERATOR_REVIEW). RP-3 r2 transport showed that the runtime policy still enforces Global-only — re-transporting these 12 rows under the same runtime policy is expected to land most of them at OPERATOR_REVIEW again, but it gives the panel another chance on cross_function rows and serves as an admission-policy regression test once the policy fix lands.

Until decision (1) lands and the runtime policy is updated, RP-3 r3 stays at `held`. No transport initiated.
