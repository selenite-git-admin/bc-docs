---
title: BCF × OAGIS Pass 1 C1 RP-2 Parked-Row Analysis (2026-06-25)
description: Held root-cause analysis of the 15 RP-2 parked OPERATOR_REVIEW rows. Each row is read against its panel verdict_payload, the original packet, the substrate-neighbor list, and the F4-v2 orchestrator's documented confirm semantics. 14 of 15 require packet rewrite + panel rerun; 1 (sequence number) is a separate operator doctrine decision about scope vs substrate line number. 0 rows are admissible via direct C5 confirm of the parked panel (orchestrator returns parked for non-APPROVE verdicts per registry-authoring-orchestrator.service.ts:293). Panel-policy gaps identified: M5 surface-pattern false-positives (most frequent), anti-leakage rule over-application collapsing valid function-scoped or industry-scoped governed characteristics into source/system-specific leakage (3 rows), M9 reading-of-rename-as-copy (2 rows), M6 representation-term-suffix false-positive (1 row). A required doctrine correction (§1.5) is the precondition to RP-3 rerun: BareCount admits system-agnostic, evidence-backed governed characteristics — they may be cross-function, function-scoped, or industry-scoped — and F4-v2 must reject only source-system-specific leakage, local aliases, implementation artifacts, source-field copies, and semantic duplicates. No panels run, no confirmations dispatched, no substrate mutated, no retry-ledger writes, no C2 entry.
status: held
authority: dec-f94895 + bcf-oagis-pass-1-c1-operator-decision-packet-2026-06-25 + required-doctrine-correction-2026-06-25 (admission scope is cross_function, function_scoped, or industry_scoped; anti-leakage rule applies only to source-system-specific leakage, local aliases, implementation artifacts, source-field copies, and semantic duplicates)
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-c1-rp2-parked-row-analysis
related_docs:
  - bcf-oagis-pass-1-c1-operator-decision-packet-2026-06-25.md
  - bcf-oagis-pass-1-c1-repair-pass-2-packet-prep-2026-06-25.md
  - bcf-desktop-prep-handoff-contract-2026-06-25.md
related_adrs:
  - DEC-f94895
related_sessions:
  - SES-dfac49
---

# BCF × OAGIS Pass 1 C1 RP-2 Parked-Row Analysis (2026-06-25)

> Held root-cause analysis of the 15 RP-2 parked OPERATOR_REVIEW rows. **14 / 15 require packet rewrite + panel rerun; 1 (sequence number) requires an operator doctrine decision.** 0 rows are admissible via direct C5 confirm of the parked panel — see §1.1 for the orchestrator-side reason.

## 1. Executive summary

### 1.1 Why "operator-confirm of a parked panel" is not a path

The F4-v2 post-confirm executor refuses to write a characteristic when the panel verdict was anything other than `APPROVE_FOR_DRAFT`. From `registry-authoring-orchestrator.service.ts:293`:

```ts
if (panel.verdictCode !== APPROVED_VERDICT_V1) {
  return {
    kind: 'parked',
    panelRunUid,
    verdictCode: panel.verdictCode,
    detail: `non-APPROVE verdict '${panel.verdictCode}' — no Registry write`,
  };
}
```

This means the C5 confirm endpoint, when invoked against a panelRunUid that landed at OPERATOR_REVIEW, mints the cert at the C5 boundary but the post-confirm executor returns `parked` without invoking F3 `registerCharacteristic`. No substrate row is created. Therefore "operator confirms parked panel" is structurally not available as a closure path under F4-v2 v1.

The realistic closure paths for OPERATOR_REVIEW rows are:
- **Packet rewrite + panel rerun** — sharpen the citedText / definition / classification, re-transport.
- **Map to existing characteristic** — declare the row binds via role qualifier at Pass 3 BC binding (no new substrate row).
- **Reject** — acknowledge the term cannot be admitted at all.
- **Operator doctrine decision** — operator makes a framing call (e.g., admit broader parent that subsumes existing substrate term) before re-prep.

### 1.2 Counts by root cause

| Root cause | Count | Rows |
|---|---:|---|
| `panel_policy_gap` — M5 surface-pattern false-positive (morphological or label adjacency) | **8** | location, freight terms, receipt routing, schedule type, ownership type, transaction analysis, expiration control, (transport service level — partial) |
| `panel_policy_gap` — Anti-leakage rule over-application (valid function-scoped, industry-scoped, or cross-function governed characteristics misclassified as source-system-specific leakage) — see §1.5 doctrine correction | **3** | wage type code, formulation code, corrective action resource type code |
| `panel_policy_gap` — M9 reading-of-authoring-as-source-field-copy (rename mis-read) | **2** | transport service level code, sourcing method code |
| `panel_policy_gap` — M6 representation-term-suffix surface false-positive | **1** | job code |
| `term_name_issue` + `evidence_gap` | **1** | price authorization code |
| `true_duplicate_or_near_duplicate` (generalization-of-existing) | **1** | sequence number |
| **Total root-cause classifications** | **16** | (some rows have two contributing causes; see §3) |

Counted by row (each row has one primary disposition): **14 packet_rewrite_needed + 1 operator_doctrine_decision_needed = 15.**

### 1.3 Counts by recommended action

| Recommended action | Count |
|---|---:|
| Confirmable without rerun | **0** (technically infeasible — see §1.1) |
| Packet rewrite + panel rerun | **14** |
| Map to existing characteristic | **0** |
| Reject | **0** |
| Operator doctrine decision needed | **1** (sequence number) |
| **Total** | **15** |

### 1.4 Panel-policy gaps identified

The 15 parked rows expose **four distinct panel-policy gaps**. Each gap recurs across multiple rows and is likely to recur in future C-waves unless addressed.

| Gap # | Description | Rows affected | Recommendation |
|---:|---|---:|---|
| 1 | **M5 surface-pattern false-positive.** The Checker's no-synonym scan triggers on morphological adjacency (`<noun> code` pattern, `expir-` prefix, `*_type_code` suffix) or on OAGIS-listed synonym labels (e.g. "Material Status") without sufficient weight to the substantive value-property distinction surfaced by the Maker. | 8 | Packet rewrite to add explicit M5 distinctness language in `definition` (and `domain_rationale` where applicable). Longer-term: panel-policy refinement to require substantive value-property analysis, not just surface-token comparison, before raising blocking M5. |
| 2 | **Anti-leakage rule over-application.** The Global-only / Industry-Specific guard was authored to prevent source-system-specific, implementation-specific, local-alias, and legacy field-name leakage from entering the governed vocabulary. The panel is over-applying that guard by collapsing valid scoped, system-agnostic business characteristics into the same leakage bucket and rejecting them. Valid admission scopes are `cross_function`, `function_scoped`, and `industry_scoped`; F4-v2 must reject only `source_system_specific`, `local_alias`, `implementation_artifact`, `source_field_copy`, and `semantic_duplicate`. See §1.5 for the required doctrine correction. | 3 | (a) §1.5 doctrine correction is the precondition. (b) Packet rewrite under the corrected rubric — sharpen business-function (or industry) explicitness, system-agnostic framing, substantive multi-system / multi-standard evidence, no accidental widening. (c) Operator decides per row whether the term lands at `cross_function` (e.g., multi-business-function reach), `function_scoped` (e.g., workforce_payroll, accounting, quality_management), or `industry_scoped` (e.g., process_manufacturing — only when an industry / regulatory context drives the value-property). |
| 3 | **M9 reading-of-rename-as-copy.** When the authored term is a substantive reframing of an OAGIS source-field name (e.g. `source-type-code` → `sourcing method code`, `special-price-authorization-code` → `price authorization code`), the Checker raises M9 source-field-copy concerns despite the substantive authoring change. | 2 | Packet rewrite to use a more clearly distinct term (e.g., `item sourcing strategy code`) AND/OR add cross-system evidence that shows the value-property exists independently of the OAGIS source field. |
| 4 | **M6 representation-term-suffix false-positive.** Terms ending in `code` are flagged as borderline bare-rep-term even when the substantive head noun supplies the value-property scope. Substrate has many such terms (`country code`, `currency code`, `industry code`, `document type code`) that establish the pattern. | 1 | Packet rewrite to provide an explicit substrate-pattern citation in `definition` (e.g., "parallels active substrate `industry code` as a substantive-head-noun + representation-form classifier"). |

### 1.5 Required doctrine correction (precondition to rerun)

> **Status:** required before any RP-3 rerun is authorized. **Scope:** documentation correction; no code, no panel, no substrate impact at the moment of recording. **Effect:** establishes the admission rubric under which the 3 anti-leakage-misapplication rows (wage type, formulation, corrective action resource type) can be rewritten coherently.

**Terminology note (2026-06-25 update).** Earlier drafts of this section used `cross_domain` / `domain_scoped`. The current operating taxonomy is `cross_function` / `function_scoped` / `industry_scoped`, applied below. `classification: domain_specific` may remain in packet JSON only as service / API compatibility residue until the runtime admission policy is updated. The original `cross_domain` / `domain_scoped` wording is preserved in §1.5.1 (acknowledgement event) and §1.5.2 (refinement event) as historical record.

**Problem.** The current F4-v2 v1 admission policy and the corresponding Maker/Checker panel rubric treat `classification` as a binary `global` vs everything-else gate. Non-Global candidates are routed to OPERATOR_REVIEW under an anti-leakage rationale (preventing source-system-specific, implementation-specific, local-alias, or legacy field-name leakage into the governed vocabulary). This is the correct anti-leakage instinct attached to the wrong axis. As a result, the panel is collapsing valid scoped, system-agnostic business characteristics into the same bucket as source-specific leakage and rejecting them. The current parked-row analysis previously characterised this as "Global-only insistence vs operator-authorised non-Global" — that framing read the relaxation as a one-off operator override, which is not what it is. It is a clarification of what the anti-leakage rule was always for.

**Correction.** BareCount admits governed characteristics that are **system-agnostic and evidence-backed**. They may fall into any of three valid admission scopes:

| Scope | Definition | Example |
|---|---|---|
| **`cross_function`** | the value-property is substantively observed across two or more business functions | `country code` (ISO 3166) across logistics, customs, HR jurisdiction, treasury, tax; `currency code` (ISO 4217) across finance, treasury, commerce |
| **`function_scoped`** | the value-property is substantively observed across two or more systems / standards / frameworks within a single business function or subfunction, with the function stated explicitly | `wage type code` across SAP HCM / Workday / Oracle HCM and ILO / FLSA / EU labour frameworks within the workforce_payroll function |
| **`industry_scoped`** | the value-property is required because a specific industry or regulatory context demands it (use only when the scope is truly an industry or regulatory regime, not merely a business function) | `product formulation reference` across chemical / pharmaceutical / food / cosmetic / beverage process-manufacturing industries, driven by FDA SRS, ICH IDMP, EMA, and ISO 22000 composition-traceability regimes |

F4-v2 must reject candidates that fall into any of the following five invalid scopes:

| Scope | What it is |
|---|---|
| **`source_system_specific`** | the value-property exists only in one source system; no cross-system evidence is offered |
| **`local_alias`** | a deployment-specific renaming of an existing governed characteristic |
| **`implementation_artifact`** | a value-property that exists only because of a particular implementation choice (e.g., a status enum forced by a workflow-engine state model) |
| **`source_field_copy`** | a literal or near-literal rename of an OAGIS / SAP / Oracle source-field name without substantive conceptual reframing |
| **`semantic_duplicate`** | a near-duplicate of an existing governed characteristic at the value-property layer |

**Function-scoped admission preconditions (all five required).** A `function_scoped` admission is valid only when:

1. **Business function is explicit** — the packet's `business_function` field is set to a stable BareCount business-function or subfunction code (not free-text).
2. **Term is system-agnostic** — the proposed name and definition do not name a specific source system, product, or implementation.
3. **Definition is not source-narrow** — it describes the value-property at a level that would survive onboarding a second source system in the same function.
4. **Evidence is substantive** — citedText cites at least two systems / standards / frameworks in the same function. One OAGIS reference is not enough on its own to establish function-scoped admission.
5. **The packet does not accidentally widen the term into cross-function by overreaching the citedText** — the citation set and the proposed scope must agree.

**Industry-scoped admission preconditions (all five required).** An `industry_scoped` admission is valid only when:

1. **Industry is explicit** — the packet's `industry` field is set to a stable BareCount industry code (not free-text).
2. **Term is system-agnostic** — the proposed name and definition do not name a specific source system, product, or implementation.
3. **Definition is not source-narrow** — it describes the value-property at a level that would survive onboarding a second source system in the same industry.
4. **Evidence is substantive** — citedText cites at least two systems / standards / frameworks (industry-regulatory anchors and/or ERP-side anchors that implement them) within the same industry.
5. **The packet does not accidentally widen the term into cross-industry or present an industry-driven characteristic as function-scoped** — the citation set and the proposed scope must agree.

**What this is not.** This is not a one-off operator override of a Global-only rule. It is a clarification of what the anti-leakage rule was always for. Recording it explicitly here closes the framing gap so future C-waves are not blocked by the same misapplication.

**Operator action required (precondition to RP-3).**
- (a) Acknowledge the corrected admission rubric — 3 valid scopes (`cross_function`, `function_scoped`, `industry_scoped`) + 5 invalid scopes + 5 function-scoped preconditions + 5 industry-scoped preconditions — as recorded above.
- (b) Confirm whether this is captured as: (i) inline in this analysis document only (current state), (ii) a small amendment note appended to the operator-decision packet, or (iii) a proper ADR (likely successor / amendment of the v1 admission-policy ADR).
- (c) Until (a) is acknowledged, no RP-3 packet rewrites are authorised.

### 1.5.1 Operator acknowledgement (2026-06-25)

> **Historical wording note.** This section records the acknowledgement event at the time it occurred, using the original `cross_domain` / `domain_scoped` taxonomy. The taxonomy was refined to `cross_function` / `function_scoped` / `industry_scoped` on the same day; see §1.5.2 for the refinement event and §1.5 (above) for the current operating statement.

**Acknowledged.** The §1.5 admission-rubric correction is adopted as the operating rubric for C1 RP-3 packet preparation, effective immediately. Capture mode: **(i) inline** — recorded in this analysis document for the duration of C1. A durable ADR (or amendment to the F4-v2 v1 admission-policy ADR) will be filed after C1 closes; until then, this section is the operating authority for RP-3.

Sequence-number doctrine (§3.4): operator selected **Path B** (narrow scope). The candidate term `operation step number` is preferred but is subject to source-evidence verification before lock. If the source evidence does not support operation-step semantics, the narrowest system-agnostic ordinal term that fits the evidence is proposed instead, and the row stops for operator review.

### 1.5.2 Taxonomy refinement to platform-native axes (2026-06-25)

**Refined.** The §1.5 scope labels `cross_domain` and `domain_scoped` are replaced with the platform-native taxonomy: **`cross_function`**, **`function_scoped`**, and **`industry_scoped`**. The motivation is that "domain" is ambiguous in BareCount (it may mean source domain, industry domain, bounded context, or business function); the platform's established axes are business function / subfunction / industry.

**Three valid admission scopes:**

| Scope | Meaning |
|---|---|
| `cross_function` | A system-agnostic characteristic valid across multiple business functions. Example: country code, currency code, location code, unit of measure code. Replaces most uses of `cross_domain`. |
| `function_scoped` | A system-agnostic characteristic valid inside a business function or subfunction. Not source-system-specific; not vendor-field leakage. Examples: wage type code (workforce_payroll), transaction analysis code (accounting), negotiated price authorization reference (pricing_commercial). Replaces `domain_scoped` where the intended scope is a business function or capability area. |
| `industry_scoped` | A system-agnostic characteristic valid because a specific industry or regulatory context demands it. Use only when the scope is truly an industry or regulatory regime, not merely a business function. Examples (with explicit evidence): pharma, healthcare, hazardous materials, regulated trade, process manufacturing. |

**Five invalid scope classes (unchanged):** `source_system_specific`, `local_alias`, `implementation_artifact`, `source_field_copy`, `semantic_duplicate`.

**Core doctrine recap (carries forward from §1.5):**
- BareCount admits governed, system-agnostic characteristics.
- A characteristic does NOT need to be universal to be admitted. Most meaningful enterprise characteristics are scoped.
- The rejection target is source / system / local leakage — not scoped business meaning.
- Scope must be explicit and evidence-backed.
- A function-scoped characteristic must not be accidentally widened into cross-function.
- An industry-scoped characteristic must not be accidentally presented as function-scoped or cross-function.

**Effect on prior §1.5 / §1.5.1 content:** the substance of the doctrine correction is unchanged; only the scope labels and the rationale-field naming change. Mappings: `cross_domain` → `cross_function`; `domain_scoped` → `function_scoped` (or `industry_scoped` where evidence points to an industry/regulatory driver). The five-condition admission preconditions for `function_scoped` carry over with one wording change: "business function is explicit" replaces "domain is explicit". For `industry_scoped`, the parallel preconditions read "industry is explicit", "not accidentally widened into cross-industry", etc.

A durable ADR formalising this taxonomy will be filed as part of the post-C1 admission-policy work, alongside the §1.5 doctrine correction. Until then, this section is the operating authority.

## 2. 15-row decision table

For each row: panel objection summary, root cause, our packet's role, recommended disposition, whether substrate has a real duplicate, and whether the row blocks C1 closure.

| seq | term | panel objection (summary) | root cause | issue with packet? | issue with panel policy? | true semantic risk? | recommended disposition | recommended new term | substrate duplicate? | blocks C1 closure? |
|---:|---|---|---|---|---|---|---|---|---|---|
| 1 | location code | M5 morphological adjacency vs country code | panel_policy_gap (M5 FP) | partial — citedText didn't pre-empt the M5 attack | yes (Gap #1) | low — distinct value property | packet_rewrite_needed | location code (unchanged) | NO — country code names a country (ISO 3166); location code names a place (UN/LOCODE etc.) | yes |
| 2 | transport service level code | M5/M6/M7/M9 disagreement; canonicalized source-field artefact concern | panel_policy_gap (M9 misread of authoring) | partial — citedText could have emphasized the abstraction over role qualifier more | yes (Gap #3) | low — legitimate Parent abstraction over the role-qualified OAGIS sources | packet_rewrite_needed | transport service level code (unchanged) | NO — substrate has no related characteristic | yes |
| 3 | freight terms code | M5 specialization/near-dup vs `payment terms` | panel_policy_gap (M5 surface label match) | partial — citedText distinction wasn't sharp enough | yes (Gap #1) | low — payment terms governs goods-payment timing; freight terms governs freight-cost allocation | packet_rewrite_needed | freight terms code (unchanged) | NO — distinct value property | yes |
| 4 | **sequence number** | **near-duplicate/generalization vs substrate `line number`; Global breadth asserted not established** | **true_duplicate_or_near_duplicate** | yes — definition explicitly included "line within a multi-line document" which IS line number's scope | partial | **yes** — admitting a broader parent characteristic when narrower substrate exists is a real governance question | **operator_doctrine_decision_needed** | (one of three: see §3.4) | **YES (partial)** — line number is the document-line ordinal, which sequence number subsumes | yes |
| 5 | receipt routing code | M5 overlap with substrate `status` via OAGIS-listed synonyms "Material Status / Material Condition Code" | panel_policy_gap (M5 misleading OAGIS-synonym attribution) | partial — citedText included the "Material Status" synonym which became a false-positive trigger | yes (Gap #1) | low — status is record lifecycle; receipt routing is goods-disposition decision | packet_rewrite_needed | material condition code (rename to honor the canonical synonym AND drop the M5 trigger) | NO — distinct value property | yes |
| 6 | sourcing method code | M9 disagreement: term is reworded source-field handle from OAGIS `source-type-code` | panel_policy_gap (M9 misread) + term_name_issue | yes — rename was substantive but visible as a token-level diff | yes (Gap #3) | low — substantive reframing of make-or-buy classification | packet_rewrite_needed | item sourcing strategy code (more distinct) | NO | yes |
| 7 | schedule type code | M5 pattern overlap with substrate `document type code`; Global single-standard | panel_policy_gap (M5 surface pattern + classification_scope) | partial — both M5 and classification can be sharpened | yes (Gap #1 + Gap #2) | low | packet_rewrite_needed | schedule type code (unchanged) | NO — schedule context ≠ document context | yes |
| 8 | job code | M6 No Bare Representation Term (term ends with "code") | panel_policy_gap (M6 FP on suffix) | partial — citedText didn't pre-empt M6 with substrate-pattern evidence | yes (Gap #4) | low — many substrate terms end in "code" with substantive head | packet_rewrite_needed | job code (unchanged) | NO | yes |
| 9 | **wage type code** | classification ambiguity — domain or global; F4-v2 v1 requires explicit `global` | **panel_policy_gap (anti-leakage misapplication — §1.5)** | partial — packet asserted scoped admission without §1.5 framing, so the panel reading defaulted to source-leakage suspicion | yes (Gap #2 — anti-leakage misapplication) | low | packet_rewrite_needed under corrected doctrine (§1.5) — operator selects `cross_function` (multi-business-function reach via labour-rights frameworks) OR `function_scoped`=workforce_payroll | wage type code (unchanged) | NO | yes |
| 10 | price authorization code | Global not evidence-backed (single OAGIS field); M9 near-paraphrase | term_name_issue + evidence_gap | yes — single-source evidence + token-similar to OAGIS field | partial (Gap #3) | low | packet_rewrite_needed | negotiated price authorization reference (more distinct + acknowledges per-agreement nature) | NO | yes |
| 11 | ownership type code | M5 near-dup vs `account type code` (and other `*_type_code`); Global disputed | panel_policy_gap (M5 suffix surface match) | partial — citedText could sharpen M5 distinction from account-type context | yes (Gap #1) | low — account-type is chart-of-accounts; ownership-type is item/asset ownership | packet_rewrite_needed | item ownership type code (extra scope qualifier to differentiate) | NO | yes |
| 12 | transaction analysis code | M5 near-variant within "X code" classifier pattern | panel_policy_gap (M5 pure surface FP) | partial — citedText could explicitly distinguish from `*_type_code` chars | yes (Gap #1) | low | packet_rewrite_needed | transaction analysis code (unchanged) | NO | yes |
| 13 | **formulation code** | Industry-specific not Global; M9 source-field-copy | **panel_policy_gap (anti-leakage misapplication — §1.5) + M9 borderline** | partial — packet asserted scoped admission without §1.5 framing | yes (Gap #2 + partial Gap #3) | low | packet_rewrite_needed under corrected doctrine (§1.5) — operator selects `industry_scoped`=process_manufacturing (recommended; driven by FDA SRS, ICH IDMP, EMA, ISO 22000) OR `function_scoped` if substantively reachable inside one business function; rename to `product formulation reference` to neutralize M9 | product formulation reference | NO | yes |
| 14 | expiration control code | M5 expiration/expiry overlap with substrate `expiry date` | panel_policy_gap (M5 morphological FP) | partial — citedText could pre-empt with explicit policy-vs-date distinction | yes (Gap #1) | low — expiry date is the date; expiration control code is the policy | packet_rewrite_needed | expiration control code (unchanged) | NO | yes |
| 15 | **corrective action resource type code** | Process-domain-specific (quality/CAPA) not Global; M9 cleaned expansion of `capa-resource-type-code` | **panel_policy_gap (anti-leakage misapplication — §1.5) + M9 borderline** | partial — packet asserted scoped admission without §1.5 framing | yes (Gap #2 + partial Gap #3) | low | packet_rewrite_needed under corrected doctrine (§1.5) — operator selects `function_scoped`=quality_management (recommended) OR `cross_function` if substantively reachable across business functions; rename to `quality action resource category code` to neutralize M9 | quality action resource category code | NO | yes |

## 3. Detailed per-row analysis

For brevity, the structural reasoning common to all rows lives in §1. The per-row sections below highlight only what is row-specific.

### 3.1 location code (panel_run_uid `2b2001ee-…`)

- **Panel verdict_payload (excerpt):** *"Material Maker/Checker disagreement on createCharacteristic M5 No-Synonym-Admission: Maker finds 'location code' distinct from active 'country code' and other '<noun> code' characteristics, while Checker raises a blocking near-duplicate / morphological-adjacency concern with governed 'country code'."*
- **Substantive check:** substrate `country code` is the ISO 3166 country identifier. `location code` is the UN/LOCODE-anchored trading-or-operational-place identifier (ports, airports, terminals, distribution centers, manufacturing sites). The Checker's "morphological-adjacency" concern is at the surface pattern `<noun> code`; this pattern is shared by 8+ substrate terms with distinct value properties. The substantive concepts are not duplicate.
- **Recommended rewrite:** add an explicit M5 distinctness paragraph to `global_rationale`: "Distinct from substrate `country code`: country code names a country (a jurisdictional entity); location code names a place within a jurisdiction (port, airport, terminal, manufacturing site, distribution center). The 4 role placements that close via `location code` (seq 6, 29, 30, 31) all reference specific places, not countries. Substrate already governs 8+ `<noun> code` terms with distinct value properties (country code, currency code, industry code, debit credit code, …); pattern alone is not a duplicate signal."

### 3.2 transport service level code (panel_run_uid `ff4959d3-…`)

- **Panel verdict_payload (excerpt):** *"Maker recommends APPROVE with global classification and all M1-M10 passing, but Checker raises blocking concerns that the term may be a canonicalized source-field artefact derived from OAGIS shipment-service-level-code / carrier-service-level-code, may not be an independently authored business term, and may involve rep-term leakage or insufficiently direct grounding."*
- **Substantive check:** the authored term is a Parent abstraction of two role-qualified OAGIS sources (`shipment-service-level-code`, `carrier-service-level-code`). This is exactly the pattern the operator-decision packet authorized — a Global parent term that closes 2+ role-qualified source rows via BC-binding role qualifiers. The successful prior batches included exactly this pattern: `payment method code` (closes the `first agent` role placement of OAGIS first-agent-payment-method-code), `country code` (closes `destination` + `origin` role placements). M9 panel reading treats the abstraction as copy — false-positive.
- **Recommended rewrite:** in `citedText`, explicitly cite the role-qualified OAGIS sources as evidence of the cross-mode Parent abstraction: "OAGIS publishes two role-qualified instances of this value property — shipment-service-level-code (shipper-side) and carrier-service-level-code (carrier-side) — both naming the same underlying service-level classification. The authored Parent characteristic abstracts the role qualifier (placement) into BC-binding metadata, leaving the value-property layer governed once. This is the same Parent pattern previously authored for `payment method code` and `country code`."

### 3.3 freight terms code (panel_run_uid `7dea9967-…`)

- **Panel verdict_payload (excerpt):** *"Maker treats freight-cost billing/allocation as distinct from payment terms, while Checker argues freight payment arrangement may fall within payment terms' scope."*
- **Substantive check:** substrate `payment terms` is "Agreed conditions governing the timing and manner of payment" — that's about WHEN and HOW the buyer pays for the goods. Freight terms is about WHO PAYS for freight cost (Prepaid by shipper / Collect from receiver / Third Party). These are distinct value properties — the Checker's "may fall within" is speculative.
- **Recommended rewrite:** sharpen `definition` distinctness: "Distinct from substrate `payment terms` in value-property scope: `payment terms` governs how and when the buyer pays for the goods themselves (e.g., Net 30, 2/10 Net 30); `freight terms code` governs which party bears freight cost (Prepaid by shipper / Collect from receiver / Third-Party billing / Prepaid and Add / Consignee Billed). The two co-occur on the same documents but govern distinct commercial decisions."

### 3.4 sequence number (panel_run_uid `646a763c-…`)

> **This is a separate modeling decision, independent of §1.5.** The panel concern here is real — the proposed Parent generalizes over substrate `line number`. This is a vocabulary-modeling question (broaden vs narrow vs defer), not an admission-rubric question. It can be resolved before, alongside, or after §1.5. Sequence number is **not** an anti-leakage-misapplication row.

- **Panel verdict_payload (excerpt):** *"proposed term 'sequence number' is a near-duplicate/generalization of active governed characteristic 'line number' (ordinal position of a line item within a multi-line document), creating governed-vocabulary ambiguity for ordinal-position concepts. In addition, the required global classification is not fully evidence-backed: the cited OAGIS evidence substantiates production/order/process sequencing, while broader cross-industry uses such as manifests, logistics, and event sequences are asserted rather than established."*
- **Substantive check:** the panel is correct on the M5 dimension. The packet's own definition explicitly included "line within a multi-line document" — this overlaps `line number`'s scope. Admitting a Parent characteristic that subsumes an existing substrate child is a real governance question. The Global breadth claim was also asserted (manifests, logistics, event sequences) without cross-system citation.
- **Operator doctrine paths:**
  - **Path A (admit broader Parent, deprecate the narrower child).** Author `sequence number` as the Global Parent. Deprecate `line number` (move to superseded). Replace existing BC bindings of `line number` with `sequence number` + role qualifier `document_line`. **Cost:** invasive across substrate; affects existing seeded BCs.
  - **Path B (narrow `sequence number` scope to non-document-line use).** Rewrite the term to explicitly exclude document-line ordinal (which `line number` already covers). E.g., authored as `operation step number` or `process sequence number` with a definition that names operation, process step, manifest, event sequence — but NOT document line. Substrate keeps `line number` for documents. **Cost:** non-invasive; clean closure of seq 33 and seq 36 source rows under a narrower term.
  - **Path C (defer this row).** Mark `sequence number` as `operator_semantic_decision`; close seq 33 + seq 36 source rows under `defer_insufficient_evidence`. **Cost:** 2 source rows left open; no new substrate write.
- **Recommended (operator decides):** **Path B** — minimally invasive, structurally clean, honors the panel's M5 concern, closes the source rows. Rewrite the term as `operation step number` (shape `count|integer|identifier`) with definition that explicitly excludes document-line ordinal. Seq 33 (`sequence-code` on production-order-header) maps cleanly to operation step. Seq 36 (`end-sequence-code` on sequence-schedule-event) maps as role qualifier `end`.

### 3.5 receipt routing code (panel_run_uid `85788430-…`)

- **Panel verdict_payload (excerpt):** *"The candidate evidence lists OAGIS synonyms 'Material Status' and 'Material Condition Code', and the active governed vocabulary already contains 'status' (49e434b6). Although the Maker distinguishes receipt routing code as goods-disposition routing on receipt rather than document lifecycle status, the Checker identifies a plausible synonym/near-duplicate or specialization overlap with the existing governed characteristic 'status'."*
- **Substantive check:** the M5 hit comes from the citedText including the OAGIS-listed synonym "Material Status". Substrate `status` is record-lifecycle state. Receipt routing is goods-disposition decision. The synonym attribution is misleading — "Material Status" is OAGIS's outdated synonym, not the substantive concept.
- **Recommended rewrite:** rename the term to `material condition code` (the cleaner of the two OAGIS-listed synonyms; "Material Status" is the one that triggers the FP). Remove "Material Status" from `citedText` (keep "Material Condition Code"). Sharpen distinction from substrate `status`.

### 3.6 sourcing method code (panel_run_uid `becdc58c-…`)

- **Panel verdict_payload (excerpt):** *"Maker says 'sourcing method code' is an authored canonical business term derived from OAGIS 'source-type-code'; Checker flags it as essentially a reworded source-field handle and therefore a possible M9 violation."*
- **Substantive check:** the rename `source-type-code` → `sourcing method code` is substantive (concept reframed from raw "source type" to "sourcing method") but the Checker reads it as a token-level rewrite. The substrate has no analogous procurement characteristic. Renaming further to `item sourcing strategy code` makes the substantive reframing clearer.
- **Recommended rewrite:** rename to `item sourcing strategy code` (more distinct from the OAGIS source field name). Cite cross-system evidence: SAP Material Master MAKT, Oracle Inventory Source Type, defence-procurement Government-Furnished Property classifications.

### 3.7 schedule type code (panel_run_uid `dc1c7d1f-…`)

- **Panel verdict_payload (excerpt):** *"Maker finds no synonym or near-duplicate, while Checker flags 'schedule type code' as a near-duplicate/pattern overlap with existing governed characteristic 'document type code' and therefore not auto-approvable under No Synonym Admission. Operator review is also warranted because the Global classification is evidence-supported by a single standard only."*
- **Substantive check:** substrate `document type code` classifies documents (invoice / payment / credit memo). Schedule type code classifies schedules (shipment-schedule / delivery-schedule / employee-schedule). Different parent entities, different value spaces. Surface pattern is `*_type_code` (8+ substrate examples with distinct meanings).
- **Recommended rewrite:** sharpen the M5 distinctness ("substrate `document type code` resolves within a document context; `schedule type code` resolves within a schedule-bearing entity context — schedules are not documents in the OAGIS noun taxonomy"). Add cross-entity evidence for Global classification: shipment-schedule, delivery-schedule, production-schedule, employee-schedule.

### 3.8 job code (panel_run_uid `9d766831-…`)

- **Panel verdict_payload (excerpt):** *"Material Maker/Checker disagreement on Vocabulary Admission Checklist M6 (No Bare Representation Term): Maker treats 'job code' as a substantive qualified characteristic because 'job' supplies the work-role classification subject, while Checker flags the term as borderline because it ends with the governed representation term 'code'."*
- **Substantive check:** the M6 representation-term-suffix concern would invalidate `country code`, `currency code`, `industry code`, `document type code`, and ~10 other substrate characteristics. The substantive head noun `job` carries the value-property scope.
- **Recommended rewrite:** in `global_rationale`, cite the substrate pattern: "parallels the substantive-head-noun + representation-form suffix pattern of substrate `country code` (ISO 3166), `currency code` (ISO 4217), `industry code` (NAICS/ISIC/NACE), `document type code`, `account type code`, `adjustment type code`, `debit credit code`, `account class code`. The shared `code` suffix is the representation form; `job` is the substantive head noun supplying value-property scope (job classification grouping per HR / project-accounting / payroll standards)."

### 3.9 wage type code (panel_run_uid `8e19eb3c-…`)

- **Panel verdict_payload (excerpt):** *"Maker classifies 'wage type code' as workforce/payroll-domain and not clearly global, while Checker materially disagrees and finds the OAGIS plus multi-jurisdiction labour-framework evidence could support global classification. F4-v2 v1 APPROVE requires explicit evidence-backed classification = global; ambiguous or non-global classification must be routed to operator review."*
- **Substantive check:** wage type code is a system-agnostic, evidence-backed governed characteristic. It is observed across multiple HR / payroll systems (SAP HCM wage-type infotypes, Workday compensation elements, Oracle HCM element entries) and across multiple labour-rights frameworks (US FLSA, EU Working Time Directive, ILO Convention 1, UK National Minimum Wage Act 1998). The panel's rejection conflates valid `function_scoped` (or `cross_function`) admission with source-system-specific leakage — see §1.5.
- **Recommended rewrite paths (operator selects, post §1.5 acknowledgement):**
  - **(a) `cross_function`** — citedText cites the multi-jurisdiction labour-rights frameworks above plus the multi-system HR/payroll element constructs. The value-property is observable across HR, payroll, treasury (gross-to-net), and labour-law business functions.
  - **(b) `function_scoped`=workforce_payroll** — citedText cites the multi-system HR/payroll element constructs (SAP / Workday / Oracle HCM); business function is explicit; system-agnostic name; substantive cross-system evidence; no accidental cross-function widening.
- **Either path is admissible under corrected doctrine** if the §1.5 preconditions are met. The choice should reflect what the citedText can substantively establish, not what would maximise scope on paper.

### 3.10 price authorization code (panel_run_uid `14a6d91d-…`)

- **Panel verdict_payload (excerpt):** *"Global classification is not explicitly evidence-backed by the supplied candidateEvidence. The evidence is limited to a single OAGIS 10.12 field. There is also M9 source-field-copy risk because the proposed term 'price authorization code' is a near-paraphrase of the cited source field with 'special-' stripped."*
- **Substantive check:** the dropped "special-" prefix is a substantive scope-broadening (price authorization covers more than special-pricing), but the token-similarity is visible. Single-source citedText is the harder gap.
- **Recommended rewrite:** rename to `negotiated price authorization reference` (acknowledges per-agreement nature and is structurally identifier-shape, not code-shape). Add cross-system evidence: SAP VK11/VK12 condition records, Oracle Pricing manager authorization, Salesforce CPQ approval references.

### 3.11 ownership type code (panel_run_uid `c8013739-…`)

- **Panel verdict_payload (excerpt):** *"Checker disputes M5 no-synonym/near-duplicate and the evidence-backed global classification. Specifically, Checker flags possible near-duplicate/domain-variant risk against existing governed type-code characteristics such as 'account type code' and questions whether the cited OAGIS text's 'user defined based on a specific Customer or Supplier' language supports a Global classification."*
- **Substantive check:** substrate `account type code` is the GL-account-type classifier (current asset / long-term liability / etc.). Ownership type code is item/asset ownership category (organization-owned / customer-consigned / supplier-consigned / leased / etc.). Different value spaces.
- **Recommended rewrite:** rename to `item ownership type code` (extra scope qualifier) and sharpen M5 distinctness against `account type code`. Reframe domain_rationale as inventory / asset-management cross-industry vocabulary (acknowledged in operator-decision packet).

### 3.12 transaction analysis code (panel_run_uid `4399814e-…`)

- **Panel verdict_payload (excerpt):** *"Maker concludes 'transaction analysis code' is a genuinely new global characteristic distinct from active terms; Checker raises blocking concern that the term may be a near-variant within the existing 'X code' classifier pattern and requires aggressive operator review."*
- **Substantive check:** pure surface pattern-match. The substantive concept (accounting analytic-segment) doesn't overlap with any substrate term.
- **Recommended rewrite:** in `global_rationale`, explicitly distinguish the value-property from each `*_code` substrate sibling: "distinct from `ledger account identifier` (which names the GL account itself), from `account class code` (which classifies asset/liability/equity/revenue/expense), and from `account type code` (which is the finer-grained type within a class). `transaction analysis code` is an orthogonal analytic-segment dimension used in IFRS 8 / ASC 280 segment reporting and in cost-driver / project-accounting frameworks."

### 3.13 formulation code (panel_run_uid `f0a4a030-…`)

- **Panel verdict_payload (excerpt):** *"The candidate meaning is bounded to formulated-product / process-manufacturing domains such as chemical, pharmaceutical, food, cosmetic, and beverage products. F4-v2 v1 requires global classification for approval. Additional operator concerns: the term appears to be a direct copy of the OAGIS source field 'formulation-code' with only formatting changed."*
- **Substantive check:** product / production formulation is a system-agnostic value-property observed across SAP PP-PI master recipe, Oracle Process Manufacturing formulae, GS1 product master formulation attributes, IDMP-PhPID (pharmaceutical product identifier), and FDA Substance Registration System records. The driver is industry-regulatory (process-manufacturing industries: chemical, pharmaceutical, food, cosmetic, beverage) rather than a generic business function. The panel reading framed this as source-leakage; under §1.5 it is valid `industry_scoped` admission.
- **Recommended rewrite paths (operator selects, post §1.5 acknowledgement):**
  - **(a) `industry_scoped`=process_manufacturing (recommended)** — rename to `product formulation reference` to neutralise the M9 token-level overlap with OAGIS `formulation-code`; citedText cites both industry-regulatory anchors (ICH IDMP, FDA SRS, ISO 22000, EMA) and ERP-side anchors that implement them (SAP PP-PI, Oracle Process Manufacturing, GS1 GDSN); industry is explicit; no accidental cross-industry widening.
  - **(b) `function_scoped`** — only if citedText can substantively scope the term to a single business function (e.g., product-master management) without the industry-regulatory drivers being the actual reason the value-property exists. The evidence does not support this reading; (a) is the honest scope.

### 3.14 expiration control code (panel_run_uid `4ff31973-…`)

- **Panel verdict_payload (excerpt):** *"Maker finds 'expiration control code' substantively distinct from active characteristic 'expiry date' because it is a policy classifier rather than a calendar date; Checker flags 'expiration'/'expiry' overlap as a synonym/near-duplicate risk requiring operator judgment."*
- **Substantive check:** substrate `expiry date` is the date when something expires. `expiration control code` is the POLICY that determines expiration (expiration-date-controlled / best-before-date-controlled / shelf-life-controlled / no-expiration-control). Distinct value-property layer (policy vs value). Morphological match at `expir-` prefix is surface only.
- **Recommended rewrite:** in `definition` and `domain_rationale`, sharpen the policy-vs-value distinction: "Distinct from substrate `expiry date` in the value-property layer it occupies: `expiry date` records the actual calendar date a specific item expires; `expiration control code` classifies the POLICY by which expiration is determined for the item. The two co-occur on perishables (the policy says how to compute the date; the date is the resulting computation)."

### 3.15 corrective action resource type code (panel_run_uid `719e458d-…`)

- **Panel verdict_payload (excerpt):** *"The proposed characteristic appears process-domain-specific to quality-management / CAPA workflows rather than evidence-backed as classification 'global'. F4-v2 v1 requires classification 'global' for approval; non-Global classifications such as industry_specific require operator review. There is also a Maker/Checker blocking concern about whether the proposed term is a cleaned expansion of the source term 'capa-resource-type-code'."*
- **Substantive check:** corrective-action resource categorisation is a system-agnostic value-property observed across ISO 9001 / IATF 16949 / ISO 14001 quality-management standards, FDA 21 CFR 820 corrective action requirements, and quality-management modules of SAP QM / Oracle Quality / Veeva Vault QMS. The business function is quality management. The panel reading framed this as source-leakage; under §1.5 it is valid `function_scoped` admission.
- **Recommended rewrite paths (operator selects, post §1.5 acknowledgement):**
  - **(a) `function_scoped`=quality_management (recommended)** — rename to `quality action resource category code` to neutralise the M9 token-level overlap with the OAGIS / SAP `capa-resource-type-code` token; citedText cites ISO 9001 + IATF 16949 + FDA 21 CFR 820 + SAP QM + Oracle Quality; business function is explicit; no accidental cross-function widening.
  - **(b) `cross_function`** — only if citedText can substantively reach corrective-action resource categorisation outside quality management (e.g., incident-management in IT service management, problem-management in ITIL, root-cause-analysis in safety management). The operator-decision packet did not assert this; (a) is the honest scope.

## 4. Rows safe for operator-confirm without rerun

**0 rows.**

Per §1.1, the F4-v2 post-confirm executor refuses to write a characteristic when the panel verdict was OPERATOR_REVIEW (`registry-authoring-orchestrator.service.ts:293`). Even if the operator believes a panel objection is overreach, the C5 confirm endpoint will mint the cert but the orchestrator will return `parked` without F3-writing the characteristic. The only structural path to admit a parked row is to rewrite the packet and re-run the panel.

## 5. Rows requiring packet rewrite + corrected packet guidance

**14 rows.** Per-row corrected packet guidance is in §3.1–§3.3, §3.5–§3.15. The grouped guidance:

### 5.1 M5 surface-pattern false-positive rewrites (8 rows: location, freight terms, receipt routing, schedule type, ownership type, transaction analysis, expiration control, + transport service level partial)

Common rewrite pattern:
- Add an explicit "M5 distinctness" paragraph in `global_rationale` (or `domain_rationale`) that names the substrate-neighbor term, identifies the value-property layer each occupies, and shows the value spaces are non-overlapping.
- Where the panel triggered on an OAGIS-listed synonym in the citedText (receipt routing case), remove the misleading synonym from the citation; keep only the substantive ones.
- Where the operator-decision packet authorized a rename (receipt routing → material condition code), apply the rename in this rewrite.

### 5.2 Anti-leakage-misapplication rewrites under corrected doctrine (3 rows: wage type code, formulation code, corrective action resource type code)

**Precondition:** §1.5 doctrine correction must be operator-acknowledged before these three rewrites are authored.

Per-row, operator selects between `cross_function`, `function_scoped`, and `industry_scoped`:
- **`cross_function`** — citedText must substantively cross at least two business functions.
- **`function_scoped`** — citedText must cite at least two systems / standards within the single business function, with explicit business-function code, system-agnostic framing, and no accidental cross-function widening (§1.5 function-scoped preconditions 1–5).
- **`industry_scoped`** — citedText must establish that an industry or regulatory context drives the value-property, with explicit industry code, system-agnostic framing, ≥2 systems / standards / regulatory anchors within the same industry, and no accidental cross-industry widening (§1.5 industry-scoped preconditions 1–5).

Either path is admissible under the corrected doctrine. The §3 row sections name candidate citations for each route. The operator's choice should reflect what the citedText can substantively establish, not what would maximise scope on paper. Recommended honest scopes per §3.9 / §3.13 / §3.15:

| Row | Recommended scope | Why |
|---|---|---|
| wage type code | either `cross_function` or `function_scoped`=workforce_payroll (operator's call) | both routes have substantive evidence; labour-rights frameworks support `cross_function`; multi-HR-system evidence alone supports `function_scoped` |
| formulation code | `industry_scoped`=process_manufacturing | the value-property exists because process-manufacturing industries (chemical, pharma, food, cosmetic, beverage) are regulated by composition-traceability regimes (FDA SRS, ICH IDMP, EMA, ISO 22000); function-scoped reach inside a single business function is not what the evidence establishes |
| corrective action resource type code | `function_scoped`=quality_management | cross-function reach into ITSM / safety / problem-management not asserted by current evidence |

In all three cases the rewrite must satisfy the §1.5 preconditions for the chosen scope (explicit business function or industry, system-agnostic name, definition not source-narrow, ≥2 systems / standards in citedText, no accidental widening).

### 5.3 M9 reading-of-rename-as-copy rewrites (2 rows: transport service level code, sourcing method code)

Common rewrite pattern:
- Rename to a term clearly distinct at the token level from the OAGIS source field (e.g., `item sourcing strategy code` instead of `sourcing method code`).
- Add cross-system evidence in citedText (not only OAGIS) to demonstrate the value-property exists independently of the OAGIS source field.

### 5.4 M6 representation-term-suffix rewrite (1 row: job code)

- In `global_rationale`, explicitly cite the substrate pattern of 8+ existing terms ending in `code` with substantive head nouns. The panel concern is structurally unsupportable; sharpening the rationale should resolve it.

## 6. Panel-policy gaps requiring escalation

| Gap # | Description | Rows affected (RP-2 wave) | Escalation recommendation |
|---:|---|---:|---|
| 1 | M5 surface-pattern false-positive | 8 | Tune the Checker's M5 prompt or chain to require substantive value-property analysis (not just surface-token comparison) before raising blocking M5. Documented examples: 8 rows in this wave. |
| 2 | Anti-leakage rule over-application (panel collapses valid scoped, system-agnostic governed characteristics into source/system-specific leakage) | 3 | (a) Adopt the §1.5 doctrine correction: 3 valid scopes (`cross_function`, `function_scoped`, `industry_scoped`) + 5 invalid scopes (`source_system_specific`, `local_alias`, `implementation_artifact`, `source_field_copy`, `semantic_duplicate`) + 5 function-scoped preconditions + 5 industry-scoped preconditions. (b) Update F4-v2 admission policy and the Maker/Checker rubric to honour these. (c) Until (a)+(b) land, all 3 affected rows remain held — no RP-3 rerun is authorised. |
| 3 | M9 reading-of-rename-as-copy | 2 | Tune the Checker's M9 prompt to distinguish substantive reframing (re-scoping, broader head noun, expanded acronym) from pure token-level copying. |
| 4 | M6 representation-term-suffix false-positive | 1 | Tune the Checker's M6 prompt to apply the bare-rep-term test only when no substantive head noun precedes the representation term, not whenever the term ends in `code`. |

Gaps #1 and #4 are immediate panel-prompt refinements; **gap #2 requires the §1.5 doctrine correction to be acknowledged before any RP-3 rewrites are authored**; gap #3 is a prompt-engineering refinement.

## 7. Updated C1 closure path

C1 is **not yet closed.** Pending work:

| Item | Count | Status |
|---|---:|---|
| Substrate draft characteristics authored | **12** | done (5 prior + 7 RP-2 confirms) |
| Map-to-existing source rows declared | 14 | done as packet declarations (Pass 3 BC binding will materialize the bindings) |
| Permanently rejected | 2 | done |
| **RP-2 parked rows pending action** | **15** | held under this analysis document |
| → Packet-rewrite + panel-rerun needed | 14 | held |
| → Operator doctrine decision needed | 1 (sequence number) | held |

### 7.1 Closure paths

**Precondition (gating step, applies to all paths that re-engage the panel):** the §1.5 doctrine correction must be operator-acknowledged before any RP-3 packet rewrite begins. The 3 anti-leakage-misapplication rows (wage type, formulation, corrective action resource type) cannot be rewritten coherently without this acknowledgement. The other 11 RP-3 rows (M5 / M9 / M6 / term-name / sequence-number) do not strictly require §1.5 acknowledgement to be rewritten, but the operator may choose to bundle them under one gate.

**Sequence-number decision is independent** of §1.5. It is a separate modeling choice (paths A/B/C in §3.4) and can be made before, after, or alongside §1.5. The two should not be conflated.

| Path | What it requires | Estimated panel calls |
|---|---|---:|
| **A. Doctrine correction acknowledged → rewrite 14 + decide sequence number** | (1) Operator acknowledges §1.5 (and chooses inline / amendment note / ADR per §1.5 step b). (2) Operator decides §3.4 sequence-number doctrine (paths A/B/C in §3.4). (3) Author RP-3 packets per §5; the 3 anti-leakage-misapplication rows lock `cross_function`, `function_scoped`, or `industry_scoped` per operator selection in §5.2. (4) If sequence-number §3.4 lands on Path B (operation step number), include the narrowed packet; otherwise zero or one as appropriate. (5) Re-transport. | 14–15 |
| B. Subset rewrite | Operator picks which subset of the 14 to rewrite; the rest are declared `operator_semantic_decision` or `defer_insufficient_evidence`. §1.5 acknowledgement is still required for any rewrite of the 3 anti-leakage-misapplication rows. | 1–14 |
| C. Accept current state as C1 close-as-is | 15 RP-2 parked rows + 1 v1 REJECT + 25 prior v1 OPERATOR_REVIEW (now superseded by RP-2 attempts) declared `operator_semantic_decision` or `defer_insufficient_evidence` permanently. C1 closes with 12 substrate writes + 14 map-to-existing + 2 rejects + 12 unresolved. No §1.5 acknowledgement required (no rewrite). | 0 |

**Recommended:** Path A with §3.4 sequence-number Path B (operation step number narrower scope). 14 rewritten packets + 1 narrowed sequence-number packet = 15 panel calls. Pass 1 cap headroom is 215 panel calls; well within budget. Precondition: §1.5 operator acknowledgement.

### 7.2 Effect on cumulative state if Path A succeeds 100%

If all 14 rewrites APPROVE + are confirmed, and sequence number takes Path B and APPROVES + is confirmed:
- Substrate drafts: 12 → **27** (5 prior + 7 RP-2 + up to 15 RP-3)
- Source rows resolved: 40 / 40 (per the operator-decision packet §2.1 partition)
- Pass 1 C1 fully closed.

C2 entry becomes available only when C1 closes — either by Path A succeeding, or by the operator electing Path C and declaring the parked rows permanently deferred.

## 8. Non-actions

This analysis document creation produces:
- 0 panel calls. `bcf.panel_output_record` rows since 2026-06-24T10:33Z (RP-2 confirm batch close): 0.
- 0 C5 confirmations.
- 0 substrate mutation. `concept_registry.entity` (active): 26. `concept_registry.characteristic` (active): 62. `concept_registry.characteristic` (any non-archived): 75. `concept_registry.business_concept` (active value): 194.
- 0 retry-ledger writes. Gate remains `pass_1_c1_v2_complete_held_pre_c2`.
- 0 C2 entry.

Held. Awaiting operator decision on closure path (§7.1) and on the sequence-number doctrine call (§3.4 paths A/B/C).
