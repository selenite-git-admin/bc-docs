---
title: BCF × OAGIS Pass 1 C1 Operator Decision Packet (2026-06-25)
description: Formal C1 operator-decision packet ratifying the disposition of all 40 Pass 1 C1 candidates. Source-row closure (sums to 40): 5 already-authored draft source rows + 19 source rows needing new characteristic packet preparation + 14 source rows resolving as role-qualified mappings + 2 permanent rejects. Characteristic-term accounting (separate): 22 new characteristic terms approved for packet preparation, of which 19 are derived directly from panel_ready_retry source rows and 3 are new parent characteristics (unit of measure code, location code, transport service level code) that have no direct C1 source row but enable 10 of the 14 role-qualified mappings. Counts by source row and counts by characteristic term answer different questions and must not be added together. Provides definitions + evidence cautions for each of the 22 new terms, a complete 40-row closure table, and a reduced execution plan for packet preparation, transport, and confirmation. Held; no panels, no substrate mutation, no ledger rewrite.
status: held
authority: dec-f94895 + operator decision packet ratified 2026-06-25
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-c1-operator-decision-packet
related_docs:
  - bcf-oagis-broad-buildout-blueprint-2026-06-23.md
  - bcf-oagis-retry-ledger-2026-06-24.md
  - bcf-oagis-a0.5-template-catalogue-2026-06-24.md
  - bcf-oagis-pass-1-c1-closeout-2026-06-24.md
  - bcf-oagis-pass-1-c1-v2-closeout-2026-06-24.md
  - bcf-desktop-prep-handoff-contract-2026-06-25.md
  - bcf-oagis-pass-1-c1-repair-pass-2-2026-06-25.md
related_adrs:
  - DEC-f94895
related_sessions:
  - SES-dfac49
---

# BCF × OAGIS Pass 1 C1 Operator Decision Packet (2026-06-25)

> **Held packet.** Ratifies the full disposition of all 40 Pass 1 C1 candidates per the operator decisions of 2026-06-25. The 40 catalogue source rows are accounted for in §2.1 (source-row closure accounting, sums to 40). The 22 new characteristic terms approved for panel packet preparation are accounted for separately in §2.2 (characteristic-term accounting). **Counts by source row and counts by characteristic term answer different questions and must not be added together.** No panels run, no confirmations dispatched, no substrate mutated, no retry ledger rewritten by this document.

## 1. C1 current substrate state

> **Reading guide.** The subsections below describe the substrate / disposition landscape from multiple complementary views. They are **NOT mutually exclusive partitions of the 40 source rows** — for example, §1.2 (2 country-code mappings) is a subset of §1.5 (14 role-qualified mappings), and §1.4 (22 new characteristic terms) is a term count not a source-row count. The exhaustive, mutually-exclusive source-row partition is in §2.1. The exhaustive characteristic-term count is in §2.2. **Counts by source row and counts by characteristic term answer different questions and must not be added together.**

### 1.1 5 draft-authored characteristics

Already in substrate at `lifecycle_state='draft'`; substrate writes complete; activation (draft → active) deferred to a separate publication step that this packet does NOT request.

| seq | bf_name | term | characteristic_id | created_at | source path |
|---:|---|---|---|---|---|
| 2 | `payment_method_code` | **payment method code** | `61b92f99-5450-41f0-92c0-84fd9b61aa14` | 2026-06-24T06:56:27Z | v1 OPERATOR_REVIEW → v2 panel APPROVE → v2 C5 confirm |
| 3 | `transportation_method_code` | **transportation method code** | `b5999e2e-5c04-46eb-818d-cd7ab9933131` | 2026-06-24T06:53:36Z | v1 panel APPROVE → v2 C5 confirm |
| 5 | `incoterms_code` | **incoterms code** | `679cda4b-3952-4337-b6d1-8def0b2083ff` | 2026-06-24T06:54:23Z | v1 panel APPROVE → v2 C5 confirm |
| 38 | `gender_code` | **sex code** | `a27b9810-3fc8-4a22-9489-fa7cc0008199` | 2026-06-24T08:35:52Z | DPO-r1 panel APPROVE → DPO-r1 C5 confirm |
| 39 | `marital_status_code` | **marital status code** | `5566c109-71ee-4aa2-b160-13e924a2ab54` | 2026-06-24T08:36:05Z | DPO-r1 panel APPROVE → DPO-r1 C5 confirm |

### 1.2 2 existing country-code mappings

No new characteristic. Each binds at Pass 3 BC binding time with a placement-role qualifier.

| seq | bf_name | Maps to | Role qualifier |
|---:|---|---|---|
| 16 | `destination_country_code` | active `country code` (`ce27c255-e720-40dc-9d62-54c5516d28c4`) | `destination` |
| 34 | `origination_country_code` | active `country code` (`ce27c255-e720-40dc-9d62-54c5516d28c4`) | `origin` |

### 1.3 2 permanent rejects

| seq | bf_name | Reason |
|---:|---|---|
| 1 | `type_code` | Bare term "type code" is a generic family root with no substantive head noun; substrate already governs three role-specific siblings (`document type code`, `account type code`, `adjustment type code`) that name the *what-is-being-typed* explicitly. Generic admission would be admission-grammar leakage. Per operator decision 2026-06-25 letter B. Permanent. |
| 37 | `code` | Bare representation-term leakage. OAGIS gloss "Element for the communication of all codes" is meta-description, not a value property. Permanent. |

### 1.4 22 new characteristics now approved for packet preparation

This is a **characteristic-term count**, not a source-row count. 19 of the 22 terms map one-to-one with a `panel_ready_retry` source row in §2.1. The remaining 3 terms (`unit of measure code`, `location code`, `transport service level code`) are parent characteristics with no direct C1 source row; they enable 10 of the 14 role-qualified mappings in §1.5 (`unit of measure code` × 4 + `location code` × 4 + `transport service level code` × 2). The 11th map-to-newly-approved-parent (seq 36 `end_sequence_code`) binds to `sequence number`, which is itself one of the 19 Direct terms (deriving from seq 33). The remaining 3 of the 14 mappings (seq 13, 16, 34) bind to characteristics that already exist in substrate. See §2.1a and §2.2 for the normative partition.

Authored term, definition, evidence anchor, and shape spec for each are in §3.

| # | term | Resolves source row(s) | Shape |
|---:|---|---|---|
| 1 | **unit of measure code** | seq 7, 8, 23, 24 (4 role placements) | code \| code \| dimension |
| 2 | **location code** | seq 6, 29, 30, 31 (4 role placements) | code \| code \| dimension |
| 3 | **transport service level code** | seq 15, 28 (2 role placements) | code \| code \| dimension |
| 4 | **freight terms code** | seq 9 | code \| code \| dimension |
| 5 | **freight classification code** | seq 17 | code \| code \| dimension |
| 6 | **receipt routing code** | seq 32 | code \| code \| dimension |
| 7 | **schedule date basis code** | seq 18 | code \| code \| dimension |
| 8 | **sourcing method code** | seq 26 | code \| code \| dimension |
| 9 | **schedule type code** | seq 19 | code \| code \| dimension |
| 10 | **sequence number** | seq 33 + seq 36 (role placement) | count \| integer \| identifier |
| 11 | **job code** | seq 14 | code \| code \| dimension |
| 12 | **wage type code** | seq 35 | code \| code \| dimension |
| 13 | **price authorization code** | seq 4 | code \| code \| dimension |
| 14 | **invoice match type code** | seq 27 | code \| code \| dimension |
| 15 | **ownership type code** | seq 10 | code \| code \| dimension |
| 16 | **tariff classification code** | seq 11 | code \| code \| dimension |
| 17 | **transaction analysis code** | seq 12 | code \| code \| dimension |
| 18 | **usage restriction code** | seq 20 | code \| code \| dimension |
| 19 | **formulation code** | seq 21 | code \| code \| dimension |
| 20 | **tracking method code** | seq 22 | code \| code \| dimension |
| 21 | **expiration control code** | seq 25 | code \| code \| dimension |
| 22 | **corrective action resource type code** | seq 40 | code \| code \| dimension |

### 1.5 Role-qualified mapping table (final)

14 rows bind to an existing or newly approved characteristic via role qualifier; no separate characteristic is created.

| seq | bf_name | Binds to | Role qualifier | Parent status |
|---:|---|---|---|---|
| 6 | `distribution_center_code` | `location code` | `distribution_center` | new (parent in §1.4) |
| 7 | `base_uom_code` | `unit of measure code` | `base` | new (parent in §1.4) |
| 8 | `storage_uom_code` | `unit of measure code` | `storage` | new (parent in §1.4) |
| 13 | `first_agent_payment_method_code` | `payment method code` | `first_agent` | existing draft (`61b92f99-…`) |
| 15 | `shipment_service_level_code` | `transport service level code` | `shipment` | new (parent in §1.4) |
| 16 | `destination_country_code` | `country code` | `destination` | existing active (`ce27c255-…`) |
| 23 | `shipping_uom_code` | `unit of measure code` | `shipping` | new (parent in §1.4) |
| 24 | `alternate_uom_code` | `unit of measure code` | `alternate` | new (parent in §1.4) |
| 28 | `carrier_service_level_code` | `transport service level code` | `carrier` | new (parent in §1.4) |
| 29 | `point_of_loading_code` | `location code` | `loading` | new (parent in §1.4) |
| 30 | `point_of_shipment_code` | `location code` | `shipment` | new (parent in §1.4) |
| 31 | `point_of_staging_code` | `location code` | `staging` | new (parent in §1.4) |
| 34 | `origination_country_code` | `country code` | `origin` | existing active (`ce27c255-…`) |
| 36 | `end_sequence_code` | `sequence number` | `end` | new (parent in §1.4) |

## 2. Complete 40-row closure table

| seq | bf_name | Final disposition | Final term | Role qualifier | Panel needed? | Substrate write done? |
|---:|---|---|---|---|:-:|:-:|
| 1 | `type_code` | reject_circular_or_generic | — | — | no | no |
| 2 | `payment_method_code` | authored_draft | payment method code | — | done | **YES** |
| 3 | `transportation_method_code` | authored_draft | transportation method code | — | done | **YES** |
| 4 | `special_price_authorization_code` | panel_ready_retry | price authorization code | — | **yes** | no |
| 5 | `incoterms_code` | authored_draft | incoterms code | — | done | **YES** |
| 6 | `distribution_center_code` | map_to_existing | location code | distribution_center | yes (parent only) | no |
| 7 | `base_uom_code` | map_to_existing | unit of measure code | base | yes (parent only) | no |
| 8 | `storage_uom_code` | map_to_existing | unit of measure code | storage | yes (parent only) | no |
| 9 | `freight_term_code` | panel_ready_retry | freight terms code | — | **yes** | no |
| 10 | `ownership_code` | panel_ready_retry | ownership type code | — | **yes** | no |
| 11 | `harmonized_tariff_schedule_code` | panel_ready_retry | tariff classification code | — | **yes** | no |
| 12 | `transaction_analysis_code` | panel_ready_retry | transaction analysis code | — | **yes** | no |
| 13 | `first_agent_payment_method_code` | map_to_existing | payment method code | first_agent | no (parent already draft) | no |
| 14 | `job_code` | panel_ready_retry | job code | — | **yes** | no |
| 15 | `shipment_service_level_code` | map_to_existing | transport service level code | shipment | yes (parent only) | no |
| 16 | `destination_country_code` | map_to_existing | country code | destination | no (parent already active) | no |
| 17 | `freight_classification_code` | panel_ready_retry | freight classification code | — | **yes** | no |
| 18 | `date_code` | panel_ready_retry | schedule date basis code | — | **yes** | no |
| 19 | `schedule_type_code` | panel_ready_retry | schedule type code | — | **yes** | no |
| 20 | `usage_restriction_code` | panel_ready_retry | usage restriction code | — | **yes** | no |
| 21 | `formulation_code` | panel_ready_retry | formulation code | — | **yes** | no |
| 22 | `tracking_method_code` | panel_ready_retry | tracking method code | — | **yes** | no |
| 23 | `shipping_uom_code` | map_to_existing | unit of measure code | shipping | yes (parent only) | no |
| 24 | `alternate_uom_code` | map_to_existing | unit of measure code | alternate | yes (parent only) | no |
| 25 | `expiration_control_code` | panel_ready_retry | expiration control code | — | **yes** | no |
| 26 | `source_type_code` | panel_ready_retry | sourcing method code | — | **yes** | no |
| 27 | `financial_match_code` | panel_ready_retry | invoice match type code | — | **yes** | no |
| 28 | `carrier_service_level_code` | map_to_existing | transport service level code | carrier | yes (parent only) | no |
| 29 | `point_of_loading_code` | map_to_existing | location code | loading | yes (parent only) | no |
| 30 | `point_of_shipment_code` | map_to_existing | location code | shipment | yes (parent only) | no |
| 31 | `point_of_staging_code` | map_to_existing | location code | staging | yes (parent only) | no |
| 32 | `receipt_routing_code` | panel_ready_retry | receipt routing code | — | **yes** | no |
| 33 | `sequence_code` | panel_ready_retry | sequence number | — | **yes** | no |
| 34 | `origination_country_code` | map_to_existing | country code | origin | no (parent already active) | no |
| 35 | `wage_type_code` | panel_ready_retry | wage type code | — | **yes** | no |
| 36 | `end_sequence_code` | map_to_existing | sequence number | end | yes (parent only) | no |
| 37 | `code` | reject_circular_or_generic | — | — | no | no |
| 38 | `gender_code` | authored_draft | sex code | — | done | **YES** |
| 39 | `marital_status_code` | authored_draft | marital status code | — | done | **YES** |
| 40 | `capa_resource_type_code` | panel_ready_retry | corrective action resource type code | — | **yes** | no |

### 2.1 Source-row closure accounting (sums to 40)

This view counts catalogue source rows. Each of the 40 Pass 1 C1 source rows appears in exactly one bucket. **This accounting answers: "how is each C1 catalogue row resolved?"**

| Source-row disposition | Count | Source rows |
|---|---:|---|
| `authored_draft` — substrate write already done at draft | **5** | seq 2, 3, 5, 38, 39 |
| `panel_ready_retry` — source row needs a new characteristic packet to be prepared (one new term per source row) | **19** | seq 4, 9, 10, 11, 12, 14, 17, 18, 19, 20, 21, 22, 25, 26, 27, 32, 33, 35, 40 |
| `map_to_existing` — source row binds via role qualifier to a parent characteristic at Pass 3 BC binding; no new characteristic created from this row | **14** | seq 6, 7, 8, 13, 15, 16, 23, 24, 28, 29, 30, 31, 34, 36 |
| `reject_circular_or_generic` — source row permanently rejected | **2** | seq 1, 37 |
| **Total source rows** | **40** | |

### 2.1a `map_to_existing` sub-classification (14 rows broken out)

The 14 map_to_existing rows split by parent-availability:

| Parent-availability sub-class | Count | Source rows | Parent characteristic |
|---|---:|---|---|
| Maps to a **newly approved** parent characteristic (parent is one of the 22 new terms in §2.2) | **11** | seq 6, 7, 8, 15, 23, 24, 28, 29, 30, 31, 36 | unit of measure code (×4), location code (×4), transport service level code (×2), sequence number (×1) |
| Maps to an **already-authored** parent characteristic (parent already exists in substrate) | **3** | seq 13, 16, 34 | payment method code (existing draft, ×1), country code (existing active, ×2) |
| **Total `map_to_existing`** | **14** | | |

### 2.2 Characteristic-term accounting — 22 new terms approved for packet preparation

This view counts characteristic terms to be added to substrate. **This accounting answers: "how many new vocabulary entries are being authored?"**

> **Important:** This count is independent of the §2.1 source-row count. Some new terms close exactly one source row; some new terms close multiple source rows via role qualifier; and some new terms are parents that close source rows without themselves being a source row. **Do not add these 22 to the 40 source rows or to any subset of §2.1.**

| Characteristic-term origin | Count | Notes |
|---|---:|---|
| **Direct** — one new term per `panel_ready_retry` source row (one-to-one with §2.1 row 2) | **19** | terms defined in §3.4–§3.22; each derived from the named source row in §2 closure table |
| **Parent** — new term not corresponding to any single C1 source row; authored solely to enable role-qualified bindings of 10 `map_to_existing` source rows | **3** | `unit of measure code` (§3.1; closes seq 7, 8, 23, 24), `location code` (§3.2; closes seq 6, 29, 30, 31), `transport service level code` (§3.3; closes seq 15, 28) |
| **Total new characteristic terms approved for packet preparation** | **22** | |

**Note on the dual-role characteristic `sequence number`:** This term is **one of the 19 Direct terms** (it derives from source row seq 33 `sequence_code`, defined in §3.10). It **also serves as the parent** for the role-qualified binding of map_to_existing source row seq 36 `end_sequence_code` (`role: end`). It is therefore counted **once** in the 22 new terms but closes **two** source rows (one as Direct from seq 33, one as parent for seq 36). The 11-row `map_to_existing`-to-newly-approved-parent sub-class in §2.1a includes seq 36's binding to `sequence number`.

### 2.3 Reading rule

> **Counts by source row and counts by characteristic term answer different questions and must not be added together.** Specifically:
>
> - "5 done + 19 need packets + 14 map + 2 reject = 40" is **source-row arithmetic** — each C1 row counted once. Valid.
> - "5 done + 22 new terms = 27 total substrate writes when complete" is **substrate-write arithmetic** — count of characteristic rows in `concept_registry.characteristic` after C1 closure. Valid.
> - "5 done + 22 new + 14 map + 2 reject = 43" is **invalid** — it mixes source-row counts (5 + 14 + 2) with characteristic-term counts (22). The 22 is not a source-row count.

## 3. Definitions for the 22 newly approved characteristic terms

Each definition follows the genus + differentia rule. Each carries an evidence / standards caution where relevant. The shape spec lives next to the term.

### 3.1 `unit of measure code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying the unit in which a physical quantity is expressed — covering mass, volume, length, count, time, and composite units. Distinct from the quantity value itself (which carries a numeric magnitude) and from currency code (which identifies a monetary denomination, not a physical quantity).
- **Standards anchor:** UN/CEFACT Recommendation 20 publishes a cross-industry unit-of-measure code list; UCUM (Regenstrief Institute) provides a complementary scientific/technical anchor.
- **Cautions:** The authored term is **not** "UOM code" — the acronym is unexpanded and a non-standard authored form. Distinct from any per-source unit-of-measure mapping policy.

### 3.2 `location code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying a trading or operational location — port, airport, freight terminal, distribution center, manufacturing site, inland clearance depot, or other named place — drawn from a governed enumeration of cross-industry location identifiers. Distinct from country code (which identifies a country) and from any address element or postal-code identifier (which identifies a postal delivery point).
- **Standards anchor:** UN/LOCODE (United Nations Code for Trade and Transport Locations) publishes the cross-industry Global enumeration.
- **Cautions:** Term is kept plain — **not** "operational location code" or "trading location code". The placement role (distribution center, loading, shipment, staging) is recorded at BC binding via role qualifier, not in the characteristic term.

### 3.3 `transport service level code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value naming the class or quality of transport service to be provided for a movement of goods, covering service classes such as express, standard, economy, deferred, and analogous categories used across road, rail, air, sea, and intermodal transport. Distinct from carrier identifier (which names the transport provider), freight terms (which govern who pays for transport), and freight classification (which classifies the goods themselves).
- **Standards anchor:** OAGIS publishes a cross-industry service-level code list; carrier-specific service-level vocabularies (FedEx, UPS, DHL, etc.) map into this characteristic via role-specific BC bindings.
- **Cautions:** Term covers all transport modes — **not** narrowed to last-mile delivery or to a single mode. Carrier-side vs shipper-side role distinction is recorded at BC binding (seq 15 `shipment` role; seq 28 `carrier` role).

### 3.4 `freight terms code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value naming the agreed terms governing how freight cost is billed and allocated between trading parties — covering values such as prepaid, collect, third-party billing, prepaid and add, and consignee-billed. Distinct from payment terms (which govern timing of payment for the goods), Incoterms (which govern transfer of risk and responsibility), and freight classification (which classifies the goods).
- **Standards anchor:** OAGIS publishes the named-value enumeration; cross-industry freight-billing-terms vocabulary is widely used in shipping and logistics documents.
- **Cautions:** Not a synonym of substrate `payment terms` (substrate `payment terms` governs payment for the goods; this governs freight cost). M5 no-synonym risk addressed by the explicit distinction in the definition.

### 3.5 `freight classification code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying the published freight class assigned to goods for the purpose of computing freight rates, covering classifications such as NMFC (National Motor Freight Classification, US road), analogous published classifications in other jurisdictions, and mode-specific freight classifications. Distinct from tariff classification (which governs customs duty) and from product / commodity code (which identifies the product itself).
- **Standards anchor:** Primary US road anchor is NMFC. Other jurisdictions publish analogous enumerations for road, rail, sea, and air; the characteristic accepts the per-jurisdiction enumeration as carried by the source.
- **Cautions:** Not a single Global enumeration; the characteristic is a cross-jurisdiction concept whose specific code list is recorded as evidence at binding time. The authored term is mode-neutral.

### 3.6 `receipt routing code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value naming the disposition or condition assigned to received goods on arrival at a buyer or downstream facility, covering values such as accepted into inventory, sent to inspection, placed on customer consignment, placed on vendor consignment, blocked from use, and held in bonded warehouse. Distinct from purchase-order or receipt lifecycle status (which records document state) and from quality-inspection outcome (which records inspection result).
- **Standards anchor:** OAGIS publishes the named-value enumeration; OAGIS-listed synonyms include "Material Status" and "Material Condition Code". Cross-industry inventory and receiving-process vocabulary.
- **Cautions:** Authored term reflects the OAGIS-canonical name "receipt routing code"; the OAGIS-listed synonyms are recorded in evidence for panel M5 no-synonym scan.

### 3.7 `schedule date basis code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value indicating which date semantic applies to the dates carried on a schedule — for example, whether the dates name shipment events or delivery events. Distinct from any specific date value (which carries a calendar date) and from delivery date / ship date characteristics (which carry resolved event-anchored dates).
- **Standards anchor:** OAGIS publishes the Ship / Deliver enumeration on shipment-schedule headers; the concept generalises across schedule-bearing entities in supply-chain and logistics documents.
- **Cautions:** Term is renamed from the OAGIS source `date code` to a substantive authored form. OAGIS evidence treats the field as polysemous at the schedule-context level; the authored characteristic clarifies the semantic as date-basis selection.

### 3.8 `sourcing method code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value naming the way an item is acquired by the procuring organisation — covering values such as manufactured in-house (make), purchased from supplier (buy), government-furnished, engineering-installed, and analogous acquisition modes. Distinct from supplier identifier (which names the trading partner) and from item-master classification codes (which classify the product itself).
- **Standards anchor:** OAGIS-named enumeration anchored in procurement-industry best practice (make-or-buy decision vocabulary); used cross-industry in item-master and procurement records.
- **Cautions:** Authored term is reframed from the OAGIS source `source_type_code` to a substantive procurement-domain authored form. M9 source-field-copy risk is addressed by the term reframing.

### 3.9 `schedule type code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying the type of schedule a record represents — for example, work schedule, shipment schedule, delivery schedule, payment schedule, production schedule — drawn from a governed enumeration of schedule-type categories.
- **Standards anchor:** OAGIS publishes the schedule-type code list; the enumeration resolves per schedule-bearing entity context.
- **Cautions:** OAGIS evidence is explicitly polysemous per OAGIS gloss ("can be used in a variety of contexts"). Panel may park as `operator_semantic_decision` at packet review and require the context-dependent meaning be recorded at BC binding rather than in the characteristic. Risk: medium-low panel approval probability without an additional cross-system grounding citation.

### 3.10 `sequence number`

- **Shape:** `count | integer | identifier`
- **Definition:** A whole number identifying the ordinal position of an item within an ordered set — operation step within a process, line within a multi-line document, event within a sequence, item within a manifest, production-sequence position. Distinct from line number (which is the ordinal-position within a multi-line document specifically) and from identifier (which is an opaque handle, not a position).
- **Standards anchor:** Industry-standard ordinal-position concept; no single named standards body; used cross-industry.
- **Cautions:** **Shape is `count | integer | identifier`, NOT `code | code | dimension`.** The OAGIS source field suffix `_code` (in `sequence_code`, `end_sequence_code`) is misleading — the authored characteristic is number-shaped, not code-shaped. Distinct from substrate `line number` (which is document-line-ordinal); the new characteristic generalises beyond multi-line documents.

### 3.11 `job code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying the job or work-role classification assigned to a position, employee, or contractor, drawn from a governed enumeration of job-classification categories. Distinct from employee identifier (which names the person), job title (free-form name), wage type code (which classifies pay treatment), and pay grade (which sets compensation band).
- **Standards anchor:** No single Global enumeration; regional anchors include US BLS SOC (Standard Occupational Classification), ISCO (ILO), and per-jurisdiction job-classification standards. The authored characteristic accepts the per-jurisdiction code list as carried by the source.
- **Cautions:** Domain-specific (HR / workforce). Panel may require domain-admission policy adoption before approval; if no admission policy is opened, panel may park as `operator_semantic_decision`.

### 3.12 `wage type code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value classifying how an employee's or worker's wage is treated under labour rules — for example, whether the wage is exempt or non-exempt from overtime under applicable labour law — covering categories used cross-jurisdiction for wage and hour administration. Distinct from job code (which classifies the work role), pay grade (compensation band), and payroll element identifier.
- **Standards anchor:** OAGIS-named enumeration anchored in cross-industry wage-and-hour administration practice; no single Global standards body, multiple per-jurisdiction frameworks (US FLSA, EU Working Time Directive analogues, ILO conventions).
- **Cautions:** Family with seq 14 `job code` under HR domain. Same panel-admission risk; may require domain-admission policy.

### 3.13 `price authorization code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying a special-pricing authorization granted under a specific commercial agreement between trading parties. Names the authorization itself — not the pricing it authorizes, not the agreement under which it was granted, and not the parties involved.
- **Standards anchor:** OAGIS publishes the field on three-way-match documents. The value space is per-agreement and per-supplier; no single Global enumeration.
- **Cautions:** Inherently bilateral per OAGIS evidence ("supplier's code to authorize special pricing as a result of an agreement"). Panel may push back on Global classification or push toward identifier-shape rather than code-shape. Medium panel-approval risk.

### 3.14 `invoice match type code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value naming the matching mode applied when reconciling an invoice against supporting documents — for example, two-way matching (invoice + purchase order), three-way matching (invoice + purchase order + goods receipt), four-way matching (invoice + purchase order + goods receipt + inspection), and analogous accounts-payable matching policies. Distinct from match outcome (which records pass/fail) and from any document identifier.
- **Standards anchor:** Accounts-payable industry-standard 2-/3-/4-way matching vocabulary; widely used cross-system; no single named standards body but cross-industry.
- **Cautions:** Anchor is industry-standard best practice rather than a single named standards body. Medium panel-approval risk; if panel parks, operator may accept domain-specific admission under a procurement / AP-domain policy.

### 3.15 `ownership type code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying the ownership category of an item or asset — for example, organisation-owned, customer-consigned, supplier-consigned, third-party-managed, and leased. Distinct from any owner identifier (which names the owning party) and from custody / location indicators (which record where the item is, not who owns it).
- **Standards anchor:** No single named standards body; cross-industry inventory and asset-management vocabulary.
- **Cautions:** OAGIS evidence is partner-negotiated ("user defined per Customer or Supplier"). Panel may park as `operator_semantic_decision` or push toward per-agreement identifier modeling. The authored characteristic frames the concept as a Global ownership-category enumeration rather than a per-agreement identifier; if panel parks, operator decides whether to defer or accept domain-specific framing.

### 3.16 `tariff classification code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying the classification of an item under a published customs tariff schedule, covering the Harmonized System (HS) maintained by the World Customs Organization, the Harmonized Tariff Schedule of the United States (HTS), the EU Combined Nomenclature (CN), and analogous national or supranational tariff classifications. Identifies the tariff-classification line that determines customs duty treatment.
- **Standards anchor:** WCO Harmonized System (HS) is the Global anchor; HTS, CN, and other national/supranational classifications are jurisdiction-specific extensions of the HS or analogous frameworks.
- **Cautions:** The authored term is **jurisdiction-neutral** — explicitly **not** "US HTS code", "WCO HS code", or any single jurisdiction's name. The specific tariff version (HS, HTS, CN, etc.) is recorded as evidence at the binding context, not in the characteristic term. Authored term covers customs-tariff classification broadly.

### 3.17 `transaction analysis code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying an analytic segment used to dimension general-ledger or project-accounting transactions — for example, project code, cost-driver, profit-center, segment, business-unit-internal-code, or analogous accounting-segmentation categories. Distinct from ledger-account identifier (which names the GL account itself) and from cost-center code (which is one specific segmentation dimension).
- **Standards anchor:** No single Global enumeration; cross-system accounting-segmentation vocabulary used in project accounting (PSA, EPM) and segment reporting. Industry-standard practice across ERP vendors.
- **Cautions:** OAGIS evidence anchors specifically to project-accounting context. The authored characteristic generalises the concept beyond project accounting to GL-segmentation broadly. Medium panel-approval risk; panel may push toward project-accounting-domain admission rather than Global.

### 3.18 `usage restriction code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying restrictions placed on the use of an item in commerce — for example, restricted to certain customer classes, restricted from certain geographies, restricted from certain end-uses, hazardous-material restricted, and dual-use export-controlled. Distinct from regulatory status (which records compliance outcome) and from any pricing-tier code.
- **Standards anchor:** No single Global enumeration; cross-industry trade-compliance vocabulary used in export controls, hazardous-material classification, and end-use restrictions.
- **Cautions:** OAGIS evidence is partner-negotiated ("implementation of this is to be agreed upon between trading partners"). Panel may park as `operator_semantic_decision` or push the characteristic toward per-agreement identifier modeling rather than Global enumeration. High panel-park risk.

### 3.19 `formulation code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying the formulation of a chemical, pharmaceutical, food, or analogous regulated product, drawn from a governed enumeration or issuing-authority reference used in customs declarations, regulatory filings, and supply-chain documentation. Distinct from product identifier (which names the marketed product) and from batch / lot identifier.
- **Standards anchor:** OAGIS anchors to customs declaration on commercial invoices. Domain-specific (chemical / pharmaceutical / food / regulated trade); per-jurisdiction enumerations published by FDA, EMA, EPA, REACH, and analogous regulators.
- **Cautions:** Domain-specific. Panel may push toward domain-admission policy rather than Global. Multiple per-jurisdiction enumerations carried as evidence at binding time.

### 3.20 `tracking method code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying the method by which an item or work program is tracked through its lifecycle — for example, serial-number-tracked, lot-tracked, batch-tracked, license-plate-tracked, and untracked. Distinct from tracking identifier (which carries the actual reference number) and from serial-number / lot-number characteristics.
- **Standards anchor:** Cross-industry inventory-tracking and asset-management vocabulary; no single named standards body.
- **Cautions:** OAGIS evidence is thin ("list of codes associated with the appropriate method of tracking a program") — no examples, no standards anchor. High panel-park risk; if panel parks, operator may accept domain-specific admission under an inventory / asset-management domain policy.

### 3.21 `expiration control code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying the policy used to determine when an item is considered expired — for example, expiration-date controlled, best-before-date controlled, shelf-life-controlled, and no-expiration-control. Distinct from expiration date (which carries the actual calendar date) and from product / batch identifier.
- **Standards anchor:** Cross-industry inventory and perishables-management vocabulary; no single named standards body.
- **Cautions:** Domain-specific (inventory / perishables). Panel may push toward domain-admission policy; if no policy, may park.

### 3.22 `corrective action resource type code`

- **Shape:** `code | code | dimension`
- **Definition:** A coded value identifying the category of resource assigned to a corrective or preventive action — for example, person, equipment, material, document, training, and system. Distinct from resource identifier (which names the specific assigned resource) and from corrective-action workflow status (which records lifecycle state).
- **Standards anchor:** Cross-industry quality-management and corrective/preventive-action (CAPA) vocabulary; ISO 9001, ISO 14001, IATF 16949, and analogous quality-management standards reference but do not publish a single enumeration.
- **Cautions:** Authored term **expands the unexpanded acronym "capa"** from the OAGIS source `capa_resource_type_code` to "corrective action resource". Domain-specific (quality management / CAPA). Panel may push toward domain-admission; high panel-park risk for Global classification.

## 4. Modeling rules honored by this packet

| Rule | How this packet honors it |
|---|---|
| Do not create separate characteristics for role-qualified variants when a parent exists | UOM family (4 rows) bind to one parent `unit of measure code`; Location family (4 rows) bind to one `location code`; Transport service-level (2 rows) bind to one `transport service level code`; payment-method-first-agent (1 row) binds to existing draft `payment method code`; country-code (2 rows) bind to existing active `country code`; sequence-end (1 row) binds to new `sequence number`. **14 role placements; 0 sibling-style new characteristics.** |
| Do not use raw source abbreviations like UOM or CAPA in authored terms | `unit of measure code` (not "uom code"); `corrective action resource type code` (not "capa resource type code"). Both acronyms expanded. |
| For `tariff classification code`, avoid claiming it is only US HTS | Authored term is jurisdiction-neutral; definition explicitly names HS, HTS, CN, and "analogous national or supranational tariff classifications". |
| For `transport service level code`, do not over-narrow to last-mile delivery | Definition explicitly covers "road, rail, air, sea, and intermodal transport"; not narrowed to delivery service alone. |
| For `location code`, keep the term plain; do not use "operational location code" | Authored term is plain `location code`. Placement roles recorded as role qualifiers at BC binding. |
| For `sequence number`, acknowledge it is not a code-shape characteristic even if the source field says `sequence_code` | Shape is **`count \| integer \| identifier`**; definition explicitly disclaims the OAGIS field-name suffix `_code` as misleading. |

## 5. Reduced execution plan

### 5.1 Phase 1 — Packet preparation (no transport)

Prepare 22 Desktop-style semantic packets, one per new characteristic in §1.4 / §3. The 14 role-qualified mappings in §1.5 do **not** require their own packets — they bind at Pass 3 BC binding time, after their parent characteristics are admitted.

Per-packet required content (per `bcf-desktop-prep-handoff-contract-2026-06-25.md` §7 hardened schema):
- authored `proposedName` (per §3)
- genus + differentia `definition` (per §3)
- `candidateEvidence.sourceLabel` (per-row OAGIS provenance)
- `candidateEvidence.citedText` carrying the standards anchor inline (no XSD boilerplate; no internal-token leakage)
- `classification` = `global` or `domain_specific` per the operator's choice for each row
- `global_rationale` (per §3 standards anchor + cross-entity reuse pattern + sibling-substrate pattern)
- `semantic_identity_confidence`, `semantic_identity_reason`
- `definition_quality = pass`
- `evidence_quality ∈ {substantive, standard_backed}`
- `shape_tuple` per §3 (note: `sequence number` is `count | integer | identifier`)
- `panel_packet_hash` (per the hardened-schema formula)
- `output_hash` (per the hardened-schema formula)

### 5.2 Phase 2 — Dedupe + collision check before transport

Before any panel call:
- **Term-dedupe within the packet set.** 22 distinct proposed terms must be unique; reject the packet set if any two propose the same term.
- **Substrate-collision check.** Query `concept_registry.characteristic WHERE LOWER(term) IN (<22 proposed terms>) AND archived_at IS NULL` and confirm **zero** matches against the 62 active + 6 draft rows in substrate (62 active + the 4 drafts already in §1.1 + the 2 pre-existing drafts: `fiscal period`, and the v2-batch-confirmed 3). Total active + draft cohort = 68; the substrate-of-record SQL is `(active) ∪ (draft) WHERE archived_at IS NULL`.
- **Packet_hash deny-list check.** Each `panel_packet_hash` must NOT appear in the v1 / v2 / DPO-r1 deny list (cumulative 42 v1+v2 hashes + 2 DPO-r1 hashes = **44 distinct deny-list entries**). The new packets are over different inputs and will not collide; the check is the existing transport-script discipline.

### 5.3 Phase 3 — Transport authorization

- Operator authorizes transport per packet (or per group). The transport script posts each authorized packet to `POST /api/bcf/registry-authoring-runs` with bounded concurrency = 2 and per-row timeout = 180s. Pass 1 cap headroom: 237 / 270 panel calls; ~$76 / $80 spend. The 22 calls would consume ~$8 estimated; well within the cap.
- For each non-APPROVE outcome, the row is recorded with the panel's substantive review_reason and the packet is NOT retried under the same hash. Operator decides re-prep or accept the verdict.

### 5.4 Phase 4 — Confirmation (writer concurrency = 1)

- For each APPROVE_FOR_DRAFT row, operator authorizes the C5 confirm. The confirm script posts to `POST /api/bcf/registry-shape-certifications/confirm` sequentially (one at a time). Each successful confirm produces:
  - 1 new row in `concept_registry.characteristic` at `lifecycle_state='draft'`
  - 1 `(registry_create, characteristic)` cert in `bcf.certification_record`
  - The new term holds the substrate `uq_characteristic_term_live` unique-on-`term` lock
- Pre-write substrate-collision check at confirm time (defense in depth): re-query for any active or draft row with the term, halt if found.

### 5.5 Phase 5 — Pass 1 C1 closure

Once each of the 22 new characteristic terms is either authored as a draft or has a recorded non-APPROVE final disposition (operator_semantic_decision / defer_insufficient_evidence) — and all 40 source rows therefore carry a recorded final disposition per the §2.1 source-row accounting — Pass 1 C1 is **complete**. The closure state is defined in §6. Note: the "22" here is the characteristic-term count (§2.2), not a source-row count; not all 22 terms map one-to-one to source rows.

## 6. Updated C1 completeness definition

### 6.1 What "complete" means after this decision packet

Pass 1 C1 is **complete** when each of the **40 source rows** reaches a terminal disposition. The §2.1 source-row accounting and the §2.2 characteristic-term accounting are presented separately below.

#### Source-row terminal states (sums to 40, per §2.1)

| Source-row terminal state | Count | Source rows |
|---|---:|---|
| `authored_draft` — substrate write done | 5 (done) | seq 2, 3, 5, 38, 39 |
| `panel_ready_retry` — packet preparation → panel → confirm → substrate draft | up to 19 (pending) | seq 4, 9, 10, 11, 12, 14, 17, 18, 19, 20, 21, 22, 25, 26, 27, 32, 33, 35, 40 |
| `map_to_existing` — role-qualified binding declared (no substrate write from this row; binding materialises at Pass 3) | 14 | seq 6, 7, 8, 13, 15, 16, 23, 24, 28, 29, 30, 31, 34, 36 |
| `reject_circular_or_generic` — permanent reject | 2 | seq 1, 37 |
| **Total** | **40** | |

#### Characteristic-term writes projected at closure (independent of source-row count)

| Characteristic-term origin | Count | Notes |
|---|---:|---|
| Already-authored draft characteristics | 5 | substrate write done |
| New characteristic terms pending packet preparation + panel approval + C5 confirm | up to 22 | 19 Direct + 3 Parent terms per §2.2; one substrate row per term once confirmed |
| **Total characteristic rows in `concept_registry.characteristic` after C1 closure** | **up to 27** | 5 + 22 if every panel approves |

> **Reading rule.** The "up to 27" total is **substrate-write arithmetic** (count of characteristic rows in substrate after closure). It is NOT 27 source rows. It is the sum of 5 already-authored drafts + the 22 new terms projected by §2.2. The 14 `map_to_existing` source rows and the 2 permanent rejects do not contribute substrate writes from this packet.

A row in `panel_ready_retry` that the panel parks does NOT block C1 completion — the row simply moves to `operator_semantic_decision` or `defer_insufficient_evidence` and is recorded as such in the next closeout. C1 completion does not require every packet to APPROVE; it requires every source row to have a recorded final disposition.

### 6.2 Why C2 remains blocked until these 22 candidate packets are handled

Pass 1 C2 (date / timestamp temporal characteristics — 46 candidates per the A0.5 catalogue) **CANNOT** begin while C1 packet preparation, transport, and confirmation are in progress. The reasons:

1. **Substrate cohort consistency.** C2 packet preparation must read a stable substrate cohort to perform M5 no-synonym checks against. While C1 transport / confirm is in flight, the substrate is in motion (rows being added at draft). A C2 packet preparation against a moving substrate risks claiming uniqueness against a substrate state that is no longer true at the time C2 packets transport. The transport-time substrate state must match the packet-prep-time substrate state, modulo recorded C1 deltas.

2. **Pass 1 panel-call budget.** Pass 1 carries one shared call cap (270 calls) and one shared spend cap ($80). Beginning C2 in parallel risks blowing the cap before C1 is closed; ordering matters under shared budget.

3. **C5 single-writer discipline.** Confirmations through C5 are sequential (writer concurrency = 1). Multiple parallel pass-level confirm batches would violate the single-writer guarantee at the operator-decision-coordination layer (even though bc-core orchestrator-side serializes at the DB layer). C2 confirms must wait until C1 confirms are settled.

4. **Operator review bandwidth.** Each panel verdict triggers an operator decision (approve to confirm, accept park, re-prep, etc.). Running C1 + C2 in parallel exceeds the operator's review queue capacity at this batch size.

5. **Retry-ledger gate authority.** The retry ledger `execution_start_gate` is `pass_1_c1_v2_complete_held_pre_c2`. Flipping to `pass_1_c2_authorized` requires explicit operator instruction after C1 closure is recorded.

When C1 closure is recorded (per §6.1), C2 entry becomes available. The decision packet for C2 will be a separate document, modeled on this one.

## 7. Non-actions

This document creation produces:
- No panel calls (`bcf.panel_output_record` rows since v2-batch close still 0)
- No C5 confirmations
- No substrate mutation
  - `concept_registry.entity` (active): 26 (unchanged)
  - `concept_registry.characteristic` (active): 62 (unchanged)
  - `concept_registry.characteristic` (any non-archived): 68 (unchanged after the 5 DPO-confirmed drafts)
  - `concept_registry.business_concept` (active value): 194 (unchanged)
- No retry-ledger writes (gate remains `pass_1_c1_v2_complete_held_pre_c2`)
- No transport packet emission (Desktop output directory `desktop-prep-output-c1-clean-2026-06-25/` unchanged; this packet is held planning for a future packet directory)
- No C2 entry

Held. Awaiting operator authorization to begin Phase 1 (packet preparation for the **22 new characteristic terms** per §3 / §2.2 — derived from **19 `panel_ready_retry` source rows** plus 3 new parent terms with no direct C1 source row) per the reduced execution plan in §5.

Reminder: counts by source row (40 total, partitioned as 5 + 19 + 14 + 2 per §2.1) and counts by characteristic term (22 new terms per §2.2) answer different questions and must not be added together.
