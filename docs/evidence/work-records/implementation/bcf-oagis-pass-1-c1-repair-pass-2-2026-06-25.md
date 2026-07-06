---
title: BCF × OAGIS Pass 1 C1 Repair Pass 2 — Contextual Family Grouping (2026-06-25)
description: Held repair-pass-2 report for the 32 unresolved Pass 1 C1 rows after the DPO-r1 transport+confirm batch. Groups the 32 rows into 8 semantic families instead of by raw bf_name. Recommends new dispositions for 5 rows (1 reject, 1 defer, 1 map-to-existing, and reaffirms the rest under a cleaner family-decision framework). Identifies 5 operator-decision family-level questions + 4 isolated row-level questions that, once answered, would unlock subsequent panel-ready packets. Proposes 0 immediate transport rows. Updates the C1 completeness definition.
status: held
authority: dec-f94895 + operator instruction 2026-06-24 (C1 contextual repair pass 2)
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-c1-repair-pass-2
related_docs:
  - bcf-oagis-broad-buildout-blueprint-2026-06-23.md
  - bcf-oagis-retry-ledger-2026-06-24.md
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
  - bcf-oagis-pass-1-c1-closeout-2026-06-24.md
  - bcf-oagis-pass-1-c1-v2-closeout-2026-06-24.md
  - bcf-desktop-prep-handoff-contract-2026-06-25.md
related_adrs:
  - DEC-f94895
related_sessions:
  - SES-dfac49
---

# BCF × OAGIS Pass 1 C1 Repair Pass 2 — Contextual Family Grouping (2026-06-25)

> Held report. Reframes the 32 unresolved Pass 1 C1 rows by semantic family rather than by bf_name. Recommends 4 disposition changes (1 reject, 1 defer, 1 map-to-existing, 1 already-deferred row reaffirmed under cleaner reasoning). Identifies 5 family-level operator decisions + 4 isolated row-level decisions that gate any further panel-ready transport. Proposes **0 immediate transport rows** under v1 policy. Held under the Desktop-prep-handoff contract `bcf-desktop-prep-handoff-contract-2026-06-25.md` §§5, 6, 9: no panels, no confirmations, no substrate mutation.

## 1. Starting state

| Class | Count | Notes |
|---|---:|---|
| Authored draft characteristics in substrate | **5** | seq 2 payment method code, seq 3 transportation method code, seq 5 incoterms code, seq 38 sex code, seq 39 marital status code |
| Map-to-existing (no new characteristic) | **2** | seq 16 destination_country_code → existing `country code` (role: destination); seq 34 origination_country_code → existing `country code` (role: origin) |
| Permanently rejected | **1** | seq 37 `code` (bare representation term) |
| **Unresolved at start of repair pass 2** | **32** | 26 operator_semantic_decision + 6 defer_insufficient_evidence |
| **Total** | **40** | Pass 1 C1 catalogue size |

The 32 unresolved are the subject of this repair pass.

## 2. Family grouping (8 semantic families)

Grouped by substantive concept rather than bf_name surface. Each row appears in exactly one family.

| Family | Rows | Count |
|---|---|---:|
| 2.1 Type / status / source classifiers | seq 1, 18, 26 | 3 |
| 2.2 Unit-of-measure family | seq 7, 8, 23, 24 | 4 |
| 2.3 Freight / logistics service family | seq 9, 15, 17, 28, 32 | 5 |
| 2.4 Location / point family | seq 6, 29, 30, 31 | 4 |
| 2.5 Scheduling / sequence family | seq 19, 33, 36 | 3 |
| 2.6 HR / workforce family | seq 14, 35 | 2 |
| 2.7 Financial / matching / payment-agent family | seq 4, 13, 27 | 3 |
| 2.8 Domain-specific / source-diagnostic leftovers | seq 10, 11, 12, 20, 21, 22, 25, 40 | 8 |
| **Total** | | **32** |

## 3. Family-by-family analysis

### 3.1 Type / status / source classifiers (3 rows)

| seq | bf_name | OAGIS substantive concept |
|---:|---|---|
| 1 | `type_code` | A bare-shape generic "type" classifier with no parent context within the OAGIS field. Appears on `invoice-line`, `match-document-header`, `actual-ledger`, `credit-status`, etc. — always with a parent component supplying the semantic frame. Substrate already holds three role-specific siblings (`document type code`, `account type code`, `adjustment type code`) that name the *what-is-being-typed* explicitly. The bare term carries no substantive value property of its own. |
| 18 | `date_code` | Misnomer. OAGIS gloss: "indicates whether schedule dates are delivery-based or shipment-based; valid values Ship and Deliver." Substantively a *schedule-dating-mode* classifier (which date semantic applies to the schedule), not a coded value naming a date. Narrow to shipment-schedule context. |
| 26 | `source_type_code` | Substantive procurement classifier. OAGIS examples: make, buy, govt furnished, engineering installed. Real make-or-buy item-sourcing-strategy semantics. |

**Recommended dispositions:**

| seq | New disposition | Reason |
|---:|---|---|
| **1** | **`reject_circular_or_generic`** (was `operator_semantic_decision`) | Bare "type code" is representation-term-shaped + source-field-copy + no substantive head noun. Substrate's three role-specific siblings cover the substantive use; the generic form is admission-grammar leakage. Same root cause as seq 37 `code`. Permanent. |
| 18 | `operator_semantic_decision` (unchanged) | Substantive concept exists but the term must be renamed before admission. Operator-recommended new term: `schedule dating mode code` or `date semantic code`. Then either Global (shipment-schedule cross-system applicability) or scheduling-domain. |
| 26 | `operator_semantic_decision` (unchanged) | Could panel-ready as Global `item sourcing strategy code` with the make/buy/govt-furnished/engineering-installed enumeration as evidence. Risk: weak named-standard anchor (no single ISO/UN standard for make-or-buy). Operator decides framing or defers. |

### 3.2 Unit-of-measure family (4 rows)

| seq | bf_name | OAGIS substantive concept |
|---:|---|---|
| 7 | `base_uom_code` | Base unit-of-measure code for an item (the unit in which the item is natively counted). |
| 8 | `storage_uom_code` | Unit-of-measure used when the item is stored. |
| 23 | `shipping_uom_code` | Unit-of-measure used when the item is shipped. |
| 24 | `alternate_uom_code` | Alternate unit-of-measure available for an item. |

All four name placements of the same substantive value property: *the code identifying a unit of measure*. Substrate has no Global parent for unit-of-measure identification. The Global anchor exists: UN/CEFACT Recommendation 20 (and complementarily UCUM) publish a cross-industry unit-of-measure code list.

**Recommended dispositions:** **All four → `operator_semantic_decision` (unchanged), grouped under one family-level decision.**

The operator decision is single, not four:
- **Option A** — Admit a Global `unit of measure code` parent characteristic (UN/CEFACT Rec 20 + UCUM as multi-source anchor). Then the four rows become `map_to_existing_characteristic` with role qualifiers `base`, `storage`, `shipping`, `alternate` at Pass 3 BC binding.
- **Option B** — Defer the parent and admit four role-qualified Global siblings (e.g. `base unit of measure code`). Higher panel-failure risk (M9 source-field-copy on the qualifier).
- **Option C** — Treat unit-of-measure as item-master-domain. Higher operator-policy overhead.

Recommended: Option A (parent admit + role-qualified placements). Aligns with the country-code precedent (seq 16, 34 already map to substrate `country code` with role qualifiers).

### 3.3 Freight / logistics service family (5 rows)

| seq | bf_name | OAGIS substantive concept |
|---:|---|---|
| 9 | `freight_term_code` | Billing terms for freight cost. Named values: Prepaid, Collect, Third Party, Prepaid and Add, Consignee Billed. |
| 15 | `shipment_service_level_code` | Shipper-side service-level for carrier delivery quality. |
| 17 | `freight_classification_code` | NMFC (US trucking) freight class. |
| 28 | `carrier_service_level_code` | Carrier-side service-level marketing term for delivery quality. |
| 32 | `receipt_routing_code` | Material condition / routing on receipt. Named values: Customer consignment, Inspection, Vendor consignment, Blocked, Bonded. OAGIS-listed synonyms: "Material Status", "Material Condition Code". |

**Sub-family observations:**

- seq 15 + seq 28: same substantive concept (delivery service level), shipper-side vs carrier-side phrasing. Should be merged into a single Global characteristic.
- seq 17: NMFC is US-regional, not Global. Cannot panel-ready under v1 policy.
- seq 9: substantive named values; overlaps in scope with active substrate `payment terms`.
- seq 32: actually a *material condition* concept, not a delivery-service concept. OAGIS-listed synonym names the broader concept.

**Recommended dispositions:**

| seq | New disposition | Reason |
|---:|---|---|
| 9 | `operator_semantic_decision` (unchanged) | Operator decides: (a) admit Global `freight billing terms code` separate from `payment terms`; (b) map to existing `payment terms` with role_qualifier=freight; (c) defer. Cross-jurisdiction freight-billing-terms vocabulary is OAGIS-named + carrier-industry-standard, supports admission. |
| **15 + 28** | **MERGE: `operator_semantic_decision` (unchanged), single family decision** | Operator admits one Global `delivery service level code` characteristic. Both seq 15 (shipper-side) and seq 28 (carrier-side) become role-qualified BC bindings of the same Global characteristic at Pass 3. |
| 17 | `operator_semantic_decision` (unchanged) | NMFC is US-regional. Cannot be Global under v1 policy. Operator decides: (a) admit US-domain freight-classification policy + admit as domain-specific; (b) defer pending cross-jurisdiction freight-classification standard. |
| 32 | `operator_semantic_decision` (unchanged) | RENAME to `material condition code` per OAGIS-listed synonym, then panel-ready as Global with the OAGIS named values + manufacturing/inventory cross-system applicability. Medium confidence (no single named standards body, but OAGIS-listed synonyms + cross-domain use). |

### 3.4 Location / point family (4 rows)

| seq | bf_name | OAGIS substantive concept |
|---:|---|---|
| 6 | `distribution_center_code` | DistributionCenter the Seller will ship items from. |
| 29 | `point_of_loading_code` | Location goods are to be loaded. |
| 30 | `point_of_shipment_code` | Location goods are to be shipped. |
| 31 | `point_of_staging_code` | Location goods are placed prior to loading for shipment. |

All four name placements of the same value property: *the code identifying a trading-location*. Substrate has no Global parent for location identification. UN/LOCODE publishes the Global cross-industry location-code enumeration.

**Recommended dispositions:** **All four → `operator_semantic_decision` (unchanged), one family-level decision.**

Mirror of the UOM family pattern:
- **Option A** — Admit Global `location code` parent (UN/LOCODE anchor). Then the four become `map_to_existing_characteristic` with role qualifiers `distribution_center`, `loading`, `shipment`, `staging`.
- **Option B** — Defer parent and admit four role-qualified Global siblings.
- **Option C** — Logistics-domain admission.

Recommended: Option A.

### 3.5 Scheduling / sequence family (3 rows)

| seq | bf_name | OAGIS substantive concept |
|---:|---|---|
| 19 | `schedule_type_code` | OAGIS explicit: "can be used in a variety of contexts" — polysemous. Different meaning per context. |
| 33 | `sequence_code` | Generic ordinal-position-within-operation/step/process. OAGIS gloss thin. |
| 36 | `end_sequence_code` | Ending production-sequence ordinal. Narrow production-domain. |

**Recommended dispositions:**

| seq | New disposition | Reason |
|---:|---|---|
| **19** | **`defer_insufficient_evidence` (unchanged; permanent)** | OAGIS explicitly polysemous. No single business value property authorable. Permanent unless OAGIS is amended. |
| 33 | `operator_semantic_decision` (unchanged) | Substrate has `line number` (ordinal within document). Could admit broader Global `sequence position number` characteristic (shape: count/integer/identifier), but the bare "sequence code" form is rep-term-shaped — must rename. Medium operator confidence. |
| **36** | **`defer_insufficient_evidence` (unchanged; permanent)** | Narrow production-sequence-ending semantics. Rep-term-shaped name. Thin evidence. Permanent unless broader sequence-position framework lands. |

### 3.6 HR / workforce family (2 rows)

| seq | bf_name | OAGIS substantive concept |
|---:|---|---|
| 14 | `job_code` | "Grouping of similar or equivalent job descriptions" — HR job classification. |
| 35 | `wage_type_code` | OAGIS examples: Exempt from Overtime, Non-Exempt from Overtime. US FLSA-style wage classification. |

Both HR-domain. No cross-jurisdiction Global enumeration exists:
- ILO has classifications but no single canonical enumeration for either.
- US BLS publishes SOC (Standard Occupational Classification) — regional.
- ISCO (International Standard Classification of Occupations) — multi-version, jurisdiction-dependent.
- FLSA wage classification is US-only.

**Recommended dispositions:**

| seq | New disposition | Reason |
|---:|---|---|
| 14 | `operator_semantic_decision` (unchanged) | Operator decides whether to open an HR/workforce-domain admission policy and admit as domain characteristic. Or defer pending cross-jurisdiction job-classification standard. |
| 35 | `operator_semantic_decision` (unchanged) | Same as seq 14. Both rows ride together under one HR-domain admission decision. |

### 3.7 Financial / matching / payment-agent family (3 rows)

| seq | bf_name | OAGIS substantive concept |
|---:|---|---|
| 4 | `special_price_authorization_code` | Supplier's code to authorize special pricing as result of an agreement. Inherently bilateral (issued by one supplier, consumed by one buyer). |
| 13 | `first_agent_payment_method_code` | Specifies the transfer method used by the first agent in a multi-agent payment chain. ISO 20022 pacs.008 PaymentInstructionAgentChain semantics. Substantively identical value property to substrate draft `payment method code` (id `61b92f99-…`); the qualifier "first agent" is a placement role in the payment chain. |
| 27 | `financial_match_code` | Invoice-matching types: 2-way (Invoice, PO), 3-way (Invoice, PO, Receipt), 4-way (Invoice, PO, Receipt, Invoice). Cross-system AP standard. |

**Recommended dispositions:**

| seq | New disposition | Reason |
|---:|---|---|
| **4** | **`defer_insufficient_evidence`** (was `operator_semantic_decision`; permanent) | Inherently bilateral. Each supplier issues its own authorization-reference codes; no Global enumeration possible by structure. The "code" here is a per-document identifier scoped to one trading relationship. Permanent defer unless trading-partner-managed code-list management surfaces as a separate platform feature. |
| **13** | **`map_to_existing_characteristic`** (was `operator_semantic_decision`) | Substrate draft `payment method code` (id `61b92f99-5450-41f0-92c0-84fd9b61aa14`) names the substantive value property. The qualifier "first agent" identifies the placement in the payment chain (which agent's payment method is being recorded), not a new value property. Maps cleanly. `role_qualifier: first_agent`. Same disposition pattern as seq 16 / 34 (country code role placements). |
| 27 | `operator_semantic_decision` (unchanged) | Substantive evidence (2-way / 3-way / 4-way matching is cross-industry AP standard). Could panel-ready as Global `invoice match type code`. Risk: no single named standards body publishes the 2/3/4-way enumeration (it's a best-practice term from AP literature). Operator decides whether to attempt panel-ready with the AP-best-practice citation, or treat as procurement-domain. |

### 3.8 Domain-specific / source-diagnostic leftovers (8 rows)

| seq | bf_name | Substantive concept + permanence verdict |
|---:|---|---|
| **10** | `ownership_code` | OAGIS explicit: "user defined based on a specific Customer or Supplier." Partner-negotiated. **PERMANENT DEFER** unless cross-system ownership-status vocabulary surfaces. |
| 11 | `harmonized_tariff_schedule_code` | Real WCO HS standard (Global). Customs-domain by use. Awaiting customs-domain admission policy decision. |
| 12 | `transaction_analysis_code` | OAGIS: "segmenting code used to analyze accounting transactions, commonly used in project accounting applications." Project-accounting-domain. Awaiting domain admission. |
| **20** | `usage_restriction_code` | OAGIS explicit: "implementation is to be agreed upon between trading partners." Partner-negotiated. **PERMANENT DEFER**. |
| 21 | `formulation_code` | OAGIS: "Formulation Code as required by Customs declaration on the Commercial Invoice in numerous countries." Customs-domain. Sibling of seq 11. |
| **22** | `tracking_method_code` | OAGIS: "list of codes associated with the appropriate method of tracking a program." Thin; no examples; no standards anchor. **PERMANENT DEFER** unless substantive cross-system evidence surfaces. |
| 25 | `expiration_control_code` | OAGIS: "type of control used to determine whether or not an item has expired." Inventory/perishable-item-domain. Awaiting inventory-domain admission. |
| **40** | `capa_resource_type_code` | OAGIS: "Code or enumeration for the kind of corrective action resource." Narrow CAPA/quality-domain. Acronym unexpanded in source. Thin. **PERMANENT DEFER**. |

**Recommended dispositions:**

| seq | New disposition |
|---:|---|
| 10, 20, 22, 40 | `defer_insufficient_evidence` (unchanged; **permanent**) |
| 11, 21 | `operator_semantic_decision` (unchanged; awaiting customs-domain admission) |
| 12 | `operator_semantic_decision` (unchanged; awaiting project-accounting-domain admission) |
| 25 | `operator_semantic_decision` (unchanged; awaiting inventory-domain admission) |

## 4. Per-row decision table (all 32 unresolved)

| seq | bf_name | Family | Old disposition | New disposition | Confidence | Next action |
|---:|---|---|---|---|---|---|
| 1 | type_code | 2.1 Type | operator_semantic_decision | **reject_circular_or_generic** | high | Permanent reject. Bare term is admission-grammar leakage. |
| 4 | special_price_authorization_code | 2.7 Finance | operator_semantic_decision | **defer_insufficient_evidence** | high | Permanent defer. Partner-bilateral; no Global enumeration possible. |
| 6 | distribution_center_code | 2.4 Location | operator_semantic_decision | operator_semantic_decision | high | Pending Location-family parent admission. |
| 7 | base_uom_code | 2.2 UOM | operator_semantic_decision | operator_semantic_decision | high | Pending UOM-family parent admission. |
| 8 | storage_uom_code | 2.2 UOM | operator_semantic_decision | operator_semantic_decision | high | Pending UOM-family parent admission. |
| 9 | freight_term_code | 2.3 Freight | operator_semantic_decision | operator_semantic_decision | medium | Operator decides admit vs map-to-payment-terms vs defer. |
| 10 | ownership_code | 2.8 Leftovers | defer_insufficient_evidence | defer_insufficient_evidence | high | **Permanent**. Partner-negotiated semantics. |
| 11 | harmonized_tariff_schedule_code | 2.8 Leftovers | operator_semantic_decision | operator_semantic_decision | high | Pending customs-domain admission. WCO HS standard exists. |
| 12 | transaction_analysis_code | 2.8 Leftovers | operator_semantic_decision | operator_semantic_decision | medium | Pending project-accounting-domain admission. |
| **13** | first_agent_payment_method_code | 2.7 Finance | operator_semantic_decision | **map_to_existing_characteristic** | high | Map to substrate draft `payment method code` (`61b92f99-…`) with `role_qualifier: first_agent`. Same pattern as country-code role placements. |
| 14 | job_code | 2.6 HR | operator_semantic_decision | operator_semantic_decision | medium | Pending HR-domain admission. Family with seq 35. |
| 15 | shipment_service_level_code | 2.3 Freight | operator_semantic_decision | operator_semantic_decision | medium | **MERGE with seq 28**: admit one Global `delivery service level code`; both 15 + 28 become role-qualified BC bindings. |
| 17 | freight_classification_code | 2.3 Freight | operator_semantic_decision | operator_semantic_decision | high | NMFC is US-regional. Pending US-domain or freight-domain admission, or defer. |
| 18 | date_code | 2.1 Type | operator_semantic_decision | operator_semantic_decision | high | **RENAME** to `schedule dating mode code` (or `date semantic code`) before admission. Then operator decides Global vs scheduling-domain. |
| 19 | schedule_type_code | 2.5 Scheduling | defer_insufficient_evidence | defer_insufficient_evidence | high | **Permanent**. OAGIS explicitly polysemous. |
| 20 | usage_restriction_code | 2.8 Leftovers | defer_insufficient_evidence | defer_insufficient_evidence | high | **Permanent**. Partner-negotiated semantics. |
| 21 | formulation_code | 2.8 Leftovers | operator_semantic_decision | operator_semantic_decision | medium | Pending customs-domain admission. Sibling of seq 11. |
| 22 | tracking_method_code | 2.8 Leftovers | defer_insufficient_evidence | defer_insufficient_evidence | high | **Permanent** unless substantive cross-system evidence surfaces. |
| 23 | shipping_uom_code | 2.2 UOM | operator_semantic_decision | operator_semantic_decision | high | Pending UOM-family parent admission. |
| 24 | alternate_uom_code | 2.2 UOM | operator_semantic_decision | operator_semantic_decision | high | Pending UOM-family parent admission. |
| 25 | expiration_control_code | 2.8 Leftovers | operator_semantic_decision | operator_semantic_decision | medium | Pending inventory-domain admission. |
| 26 | source_type_code | 2.1 Type | operator_semantic_decision | operator_semantic_decision | medium | Could panel-ready as Global `item sourcing strategy code` (make/buy/etc.). Weak named-standard anchor. Operator decides. |
| 27 | financial_match_code | 2.7 Finance | operator_semantic_decision | operator_semantic_decision | medium | Could panel-ready as Global `invoice match type code` (2/3/4-way). Weak named-standard anchor. Operator decides. |
| 28 | carrier_service_level_code | 2.3 Freight | operator_semantic_decision | operator_semantic_decision | medium | **MERGE with seq 15**. Same family decision. |
| 29 | point_of_loading_code | 2.4 Location | operator_semantic_decision | operator_semantic_decision | high | Pending Location-family parent admission. |
| 30 | point_of_shipment_code | 2.4 Location | operator_semantic_decision | operator_semantic_decision | high | Pending Location-family parent admission. |
| 31 | point_of_staging_code | 2.4 Location | operator_semantic_decision | operator_semantic_decision | high | Pending Location-family parent admission. |
| 32 | receipt_routing_code | 2.3 Freight | operator_semantic_decision | operator_semantic_decision | medium | **RENAME** to `material condition code` per OAGIS-listed synonym. Then panel-ready as Global with named values + cross-domain applicability. |
| 33 | sequence_code | 2.5 Scheduling | operator_semantic_decision | operator_semantic_decision | medium | **RENAME** to `sequence position number` (not "code"; semantic is ordinal, not code). Operator decides Global ordinal-position or defer. |
| 35 | wage_type_code | 2.6 HR | operator_semantic_decision | operator_semantic_decision | medium | Family with seq 14. Pending HR-domain admission. |
| 36 | end_sequence_code | 2.5 Scheduling | defer_insufficient_evidence | defer_insufficient_evidence | high | **Permanent**. Narrow + thin + rep-term-shaped. |
| 40 | capa_resource_type_code | 2.8 Leftovers | defer_insufficient_evidence | defer_insufficient_evidence | high | **Permanent**. Narrow CAPA-quality-domain + thin. |

### 4.1 Disposition delta

| Disposition | Before repair pass 2 | After repair pass 2 | Δ |
|---|---:|---:|---:|
| `operator_semantic_decision` | 26 | **23** | **−3** |
| `defer_insufficient_evidence` | 6 | **7** | **+1** |
| `map_to_existing_characteristic` | 0 (within these 32) | **1** | **+1** |
| `reject_circular_or_generic` | 0 (within these 32) | **1** | **+1** |
| **Total** | **32** | **32** | 0 |

**3 disposition changes:**
- seq 1 `type_code`: operator_semantic_decision → `reject_circular_or_generic`
- seq 4 `special_price_authorization_code`: operator_semantic_decision → `defer_insufficient_evidence`
- seq 13 `first_agent_payment_method_code`: operator_semantic_decision → `map_to_existing_characteristic`

## 5. Proposed reduced transport set

**0 panel_ready_retry candidates from this repair pass.** Under F4-v2 v1 policy (Global only), no row in the 32 can be panel-ready without operator framing decisions first. The decisions required are family-level, not per-row.

### 5.1 Optional speculative panel_ready_retry candidates (NOT recommended without operator authorization)

If the operator chooses to attempt panel-ready under v1 policy without first opening a domain-admission policy or family-parent admission, four rows have non-zero chance of APPROVE_FOR_DRAFT:

| seq | proposedName (authored) | Standards anchor | Panel-approval risk |
|---:|---|---|---|
| 26 | `item sourcing strategy code` | OAGIS named enumeration (make/buy/govt-furnished/engineering-installed); no single ISO/UN | Medium (no named standards body) |
| 27 | `invoice match type code` | AP industry-standard 2/3/4-way matching; no single named standards body | Medium-low (best-practice citation only) |
| 32 | `material condition code` | OAGIS-listed synonym; cross-domain manufacturing/inventory applicability | Medium-low |
| 33 | `sequence position number` | No standards anchor; generic ordinal-position concept | Low (panel likely M9 fail on bare bf_name shape) |

**Recommendation: do NOT attempt these without operator authorization.** The risk-adjusted yield is low, and a partial-fail batch consumes Pass 1 panel-call budget that would be more productively spent after operator framing decisions unlock cleaner candidates.

### 5.2 Map-to-existing recommendation (1 new row)

**seq 13 `first_agent_payment_method_code`:**

| Field | Value |
|---|---|
| Existing characteristic id | `61b92f99-5450-41f0-92c0-84fd9b61aa14` |
| Existing term | `payment method code` (substrate draft authored 2026-06-24T06:56:27Z via v2 confirm batch) |
| Role qualifier | `first_agent` |
| Target future BC context | ISO 20022 pacs.008 / pain.001 PaymentInstructionAgentChain — a payment-chain-position qualifier of the same substantive value property |
| Confidence | high |

This is a clean role-qualified placement, identical pattern to seq 16/34 destination/origin country codes. No transport call required; the placement materialises at Pass 3 BC binding time when the operator authorizes binding `payment method code` to a payment-chain entity with the `first_agent` role.

## 6. Rows still requiring operator decision after repair

23 rows remain at `operator_semantic_decision`. They factor into **5 family-level decisions** + **4 isolated row-level decisions**:

### 6.1 Family-level decisions (5 questions, 17 rows)

| # | Decision question | Rows affected | Recommended option |
|---:|---|---|---|
| 1 | **UOM-family parent admit** — admit Global `unit of measure code` (UN/CEFACT Rec 20 + UCUM)? | seq 7, 8, 23, 24 (4 rows) | Yes — admit parent; the four become `map_to_existing` at Pass 3 with role qualifiers `base/storage/shipping/alternate`. Pass-1 panel cost: 1 call. |
| 2 | **Location-family parent admit** — admit Global `location code` (UN/LOCODE)? | seq 6, 29, 30, 31 (4 rows) | Yes — admit parent; the four become `map_to_existing` at Pass 3 with role qualifiers `distribution_center/loading/shipment/staging`. Pass-1 panel cost: 1 call. |
| 3 | **Freight/logistics service merge + framing** — merge seq 15 + 28; decide on seq 9, 17, 32 | seq 9, 15, 17, 28, 32 (5 rows) | Merge 15+28 → one Global `delivery service level code`. RENAME seq 32 → `material condition code` (Global candidate). seq 9 → defer (or freight-domain). seq 17 → defer (US-regional). Pass-1 panel cost: 1-2 calls. |
| 4 | **HR-domain admission policy** — open HR/workforce-domain admission? | seq 14, 35 (2 rows) | Recommend defer pending cross-jurisdiction occupational standards adoption. No urgency. Pass-1 panel cost: 0 (deferred). |
| 5 | **Customs / inventory / project-accounting domain admission** — open one or all of customs / inventory / project-accounting domains? | seq 11, 12, 21, 25 (4 rows) | Decide per domain. Customs has WCO HS standard, strongest candidate. Inventory has no standard. Project-accounting has no single standard. Recommend customs-domain admission only. Pass-1 panel cost: 1-2 calls if admitted. |

### 6.2 Isolated row-level decisions (4 questions, 4 rows)

| # | Decision question | Row | Recommended action |
|---:|---|---|---|
| 6 | seq 18 `date_code` — rename and admit, or defer? | 18 | RENAME → `schedule dating mode code` (or `date semantic code`). Then attempt panel-ready with Ship/Deliver enumeration + cross-system shipment-schedule applicability. Risk: weak named-standard anchor (OAGIS-only). Operator decides admit or defer. |
| 7 | seq 26 `source_type_code` — admit make-or-buy classifier as Global? | 26 | Reframe as `item sourcing strategy code`. Operator decides whether procurement best-practice + OAGIS-named enumeration counts as Global anchor. |
| 8 | seq 27 `financial_match_code` — admit invoice-matching classifier as Global? | 27 | Reframe as `invoice match type code`. Operator decides whether AP best-practice + OAGIS-named values count as Global anchor. |
| 9 | seq 33 `sequence_code` — admit broader ordinal-position concept? | 33 | RENAME → `sequence position number` (shape change: count/integer not code). Operator decides whether to admit broader ordinal characteristic or defer pending sequence-vocabulary policy. |

### 6.3 Operator-decision summary

| Decision class | Count |
|---:|---|
| Family-level decisions | 5 |
| Isolated row-level decisions | 4 |
| **Total operator decisions remaining for full C1 closure** | **9** |

These 9 decisions, once made, would reclassify all 23 `operator_semantic_decision` rows into final dispositions. Best-case (all admit-as-Global decisions go through): up to ~7 panel-ready transports across UOM parent + Location parent + delivery-service-level + material-condition + customs-HS + reframed seq 18/26/27/33. Worst-case (all defer): 23 rows become `defer_insufficient_evidence` and Pass 1 C1 closes with 5 authored + 3 map-to-existing + 2 permanently rejected + 30 deferred + 0 outstanding.

## 7. Updated C1 completeness definition

### 7.1 What must be authored now

**5 characteristics** — already authored as drafts in substrate via v2 + DPO-r1 batches. **DONE**.

| seq | term | characteristic_id |
|---:|---|---|
| 2 | payment method code | `61b92f99-5450-41f0-92c0-84fd9b61aa14` |
| 3 | transportation method code | `b5999e2e-5c04-46eb-818d-cd7ab9933131` |
| 5 | incoterms code | `679cda4b-3952-4337-b6d1-8def0b2083ff` |
| 38 | sex code | `a27b9810-3fc8-4a22-9489-fa7cc0008199` |
| 39 | marital status code | `5566c109-71ee-4aa2-b160-13e924a2ab54` |

All at `lifecycle_state='draft'`. Awaiting separate operator publication step to flip draft → active.

### 7.2 What is intentionally map-to-existing (no new characteristic)

**3 rows** — bind to existing substrate at Pass 3 BC binding with role qualifiers:

| seq | bf_name | Maps to | Role qualifier |
|---:|---|---|---|
| 13 | `first_agent_payment_method_code` | substrate draft `payment method code` (`61b92f99-…`) | `first_agent` |
| 16 | `destination_country_code` | substrate `country code` (`ce27c255-…`) | `destination` |
| 34 | `origination_country_code` | substrate `country code` (`ce27c255-…`) | `origin` |

Plus prospective map-to-existing if family-parent decisions go through:
- UOM family (4 rows): maps to a future `unit of measure code` parent if admitted
- Location family (4 rows): maps to a future `location code` parent if admitted

### 7.3 What is permanently rejected

**2 rows** — terms that cannot ever be admitted as characteristics:

| seq | bf_name | Reason |
|---:|---|---|
| 1 | `type_code` | Bare term is representation-term-shaped + source-field-copy; no substantive head noun. Substrate's three role-specific siblings cover the substantive use. |
| 37 | `code` | Bare representation term. OAGIS gloss "Element for the communication of all codes" is meta-description of the field, not a value property. |

### 7.4 What is legitimately parked because no evidence exists

**7 rows** — permanent defers, no path forward unless cross-system evidence surfaces:

| seq | bf_name | Reason | Trigger to reopen |
|---:|---|---|---|
| 4 | special_price_authorization_code | Partner-bilateral (per-document supplier authorization reference) | Trading-partner-managed code-list management surfaces as separate platform feature |
| 10 | ownership_code | OAGIS explicit: "user defined per Customer or Supplier" | Cross-system ownership-status vocabulary surfaces |
| 19 | schedule_type_code | OAGIS explicit: polysemous | OAGIS amends evidence |
| 20 | usage_restriction_code | OAGIS explicit: "agreed upon between trading partners" | Cross-system usage-restriction vocabulary surfaces |
| 22 | tracking_method_code | Thin evidence, no standards anchor | Substantive cross-system evidence surfaces |
| 36 | end_sequence_code | Narrow production-domain + rep-term-shaped + thin | Broader sequence-position framework landed |
| 40 | capa_resource_type_code | Narrow CAPA/quality-domain + unexpanded acronym + thin | Quality-management admission policy + substantive enumeration |

### 7.5 What awaits operator framing decisions

**23 rows** — `operator_semantic_decision`, grouped under 5 family decisions + 4 isolated decisions per §6.

## 8. Cumulative C1 state after repair pass 2

| Final class | Count | % | Notes |
|---|---:|---:|---|
| Authored (draft) | 5 | 12.5% | seq 2, 3, 5, 38, 39 — substrate writes complete; activation pending |
| Map-to-existing | 3 | 7.5% | seq 13 (NEW this pass), 16, 34 — no new characteristics created; binds at Pass 3 |
| Permanently rejected | 2 | 5.0% | seq 1 (NEW this pass), 37 — bare representation-term shapes |
| Permanently deferred | 7 | 17.5% | seq 4 (NEW this pass), 10, 19, 20, 22, 36, 40 |
| **Resolved without further action** | **17** | **42.5%** | — |
| Operator-decision pending | 23 | 57.5% | 5 family decisions + 4 isolated decisions cover all 23 |
| **Total** | **40** | **100%** | Pass 1 C1 catalogue |

## 9. Non-actions

- No panels run. No confirmations run. No substrate mutation.
- No new transport packets emitted to disk. The 32 unresolved row dispositions are recorded in this report; if operator authorizes regenerating the DPO output packet directory with the updated dispositions, that's a separate held step (the DPO-r1 packet JSONs remain unchanged and accurately reflect the dispositions at the moment of the transport+confirm batch).
- No retry-ledger writes. The retry ledger header `execution_start_gate` remains `pass_1_c1_v2_complete_held_pre_c2`.
- No Pass 1 C2 entry.

Held. Awaiting operator decision on the 9 outstanding questions (5 family-level + 4 isolated), at which point repair pass 3 (or direct transport) becomes possible.
