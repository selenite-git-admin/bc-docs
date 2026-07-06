---
title: BCF × OAGIS Pass 1 C1 Repair Pass 2 — Packet Preparation Summary (2026-06-25, corrected)
description: Held summary of the Desktop-style packet preparation phase for the 22 new characteristic terms approved in the C1 operator-decision packet. Corrected to honour the operator's instruction that the F4-v2 v1 Global-only filter does NOT apply — all 22 terms are panel-ready, with classification honest to the term (10 Global + 12 domain-specific). 0 collisions vs 62 active + 6 draft substrate characteristics. Formulation code reclassified from customs to product/production/quality formulation per operator correction. No panels, no confirmations, no substrate writes, no C2 entry.
status: held
authority: bcf-oagis-pass-1-c1-operator-decision-packet-2026-06-25 + DEC-f94895 + operator correction 2026-06-25 (relax Global-only filter)
date: 2026-06-25
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-pass-1-c1-repair-pass-2-packet-prep
related_docs:
  - bcf-oagis-broad-buildout-blueprint-2026-06-23.md
  - bcf-oagis-pass-1-c1-operator-decision-packet-2026-06-25.md
  - bcf-desktop-prep-handoff-contract-2026-06-25.md
  - bcf-oagis-pass-1-c1-v2-closeout-2026-06-24.md
related_adrs:
  - DEC-f94895
related_sessions:
  - SES-dfac49
---

# BCF × OAGIS Pass 1 C1 Repair Pass 2 — Packet Preparation Summary (corrected, 2026-06-25)

> Held packet-preparation summary for Phase 1 of the C1 operator-decision packet (§2.2: 22 new characteristic terms approved). Corrected to honour the operator's instruction that the F4-v2 v1 Global-only admission filter does NOT apply to this packet preparation: all 22 terms are panel-ready, with classification honest to the term (10 carry `classification=global`; 12 carry `classification=domain_specific` with explicit domain scope). No panels run, no confirmations dispatched, no substrate mutated, no C2 entry.

## 1. Identity

| Field | Value |
|---|---|
| Output UID | `DPO-C1-RP2-2026-06-25-r2` (corrected) |
| Desktop prep session | `desktop-prep-2026-06-25-c1-rp2-r1` |
| Built at | `2026-06-25T01:00:00Z` |
| Authority | `bcf-oagis-pass-1-c1-operator-decision-packet-2026-06-25.md` §2.2 + operator correction 2026-06-25 (relax Global-only filter) |
| Output directory | `barecount-devhub/.claude/desktop-prep-output-c1-repair-pass-2-2026-06-25/` |
| Packets emitted | **22** (one per characteristic term) |
| Disposition | **22 / 22 = panel_ready_retry** |
| Schema validation (forbidden tokens, boilerplate, hash format, rationale field presence) | **22/22 PASS** |
| Substrate collisions vs 62 active + 6 draft = 68 terms | **0** |
| Permanent rejects from this set | **0** |
| Operator-review-needed from this set | **0** |

## 2. Counts by disposition + classification

| Disposition | Classification | Count |
|---|---|---:|
| `panel_ready_retry` | `global` | **10** |
| `panel_ready_retry` | `domain_specific` | **12** |
| **Total panel-ready** | | **22** |

## 3. Final panel-ready list — 10 with `classification = global`

| # | term | shape | source rows closed | standards anchor in citedText |
|---:|---|---|---|---|
| 1 | `unit of measure code` | code\|code\|dimension | seq 7, 8, 23, 24 (4 role placements) | UN/CEFACT Rec 20 + UCUM |
| 2 | `location code` | code\|code\|dimension | seq 6, 29, 30, 31 (4 role placements) | UN/LOCODE + broader |
| 3 | `tariff classification code` | code\|code\|dimension | seq 11 (Direct) | WCO HS (jurisdiction-neutral) |
| 4 | `transport service level code` | code\|code\|dimension | seq 15, 28 (2 role placements) | OAGIS cross-mode |
| 5 | `freight terms code` | code\|code\|dimension | seq 9 (Direct) | OAGIS named values |
| 6 | `invoice match type code` | code\|code\|dimension | seq 27 (Direct) | OAGIS 2-/3-/4-way matching |
| 7 | `sequence number` | **count\|integer\|identifier** | seq 33 (Direct) + seq 36 (role: end) | universal ordinal |
| 8 | `receipt routing code` | code\|code\|dimension | seq 32 (Direct) | OAGIS + listed synonyms |
| 9 | `sourcing method code` | code\|code\|dimension | seq 26 (Direct) | OAGIS named values |
| 10 | `schedule date basis code` | code\|code\|dimension | seq 18 (Direct) | OAGIS Ship/Deliver |

## 4. Final panel-ready list — 12 with `classification = domain_specific`

Each packet carries `classification: "domain_specific"`, an explicit `domain` field, and a `domain_rationale` (not `global_rationale`). The packet content cites substantive OAGIS evidence + per-domain published frameworks where they exist.

| # | term | domain | source rows closed |
|---:|---|---|---|
| 11 | `freight classification code` | logistics / freight | seq 17 (Direct) |
| 12 | `schedule type code` | scheduling / operations | seq 19 (Direct) |
| 13 | `job code` | workforce / HR | seq 14 (Direct) |
| 14 | `wage type code` | workforce / payroll | seq 35 (Direct) |
| 15 | `price authorization code` | pricing / commercial | seq 4 (Direct) |
| 16 | `ownership type code` | inventory / asset ownership | seq 10 (Direct) |
| 17 | `transaction analysis code` | accounting | seq 12 (Direct) |
| 18 | `usage restriction code` | commercial / trade compliance | seq 20 (Direct) |
| 19 | `formulation code` | **product / production / quality** *(corrected — NOT customs)* | seq 21 (Direct) |
| 20 | `tracking method code` | inventory / asset tracking | seq 22 (Direct) |
| 21 | `expiration control code` | inventory / perishables management | seq 25 (Direct) |
| 22 | `corrective action resource type code` | quality management / corrective action | seq 40 (Direct) |

### 4.1 `formulation code` reframing (operator correction)

The original packet incorrectly framed this as a customs declaration identifier. Corrected:

- **What the term names:** the recipe, composition, blend, or formulation specification of a product as recorded on the item master.
- **Domain:** product / production / quality management — chemical, pharmaceutical, food, cosmetic, beverage, and analogous formulated-product domains.
- **Use:** drives manufacturing routings, batch quality controls, material requirements, and quality specifications. While customs declarations may reference a formulation, the substantive concept is the formulation itself, not the declaration.
- **OAGIS source field is on `item-master.item-master.formulation-code`** — the item-master surface confirms this is master-data (the formulation IS master data for produced items), not transactional customs documentation.

## 5. Rows still not panel-ready and exact reason

**0 rows.** All 22 approved characteristic terms are panel-ready as of this corrected packet prep. None blocked by:

- exact substrate collision (none found vs 62 active + 6 draft)
- impossible definition (every term has substantive evidence sufficient to author a genus + differentia definition)
- forbidden authored content (no internal-token or XSD-boilerplate hits in any of the 22 packets)
- absent rationale field (10 have `global_rationale`; 12 have `domain_rationale` + `domain`)

## 6. Modeling-rule conformance audit (against operator-decision packet §4 + this turn's instructions)

| Rule | Verdict |
|---|---|
| One packet per characteristic term (NOT per source row) | ✓ 22 packets for 22 terms |
| Authored term, not raw `bf_name` transliteration | ✓ unit of measure code, corrective action resource type code, schedule date basis code, sourcing method code, ownership type code, tariff classification code, freight terms code, invoice match type code, sequence number, price authorization code, transport service level code |
| Standards anchor inline in `citedText` (when standards exist) | ✓ all 10 Global packets carry the standards anchor inline; the 12 domain-specific packets carry substantive OAGIS evidence + per-domain published frameworks where they exist |
| `tariff classification code` jurisdiction-neutral | ✓ definition names HS, HTS, CN, and "analogous national or supranational tariff classifications" |
| `transport service level code` mode-neutral | ✓ definition covers road, rail, air, sea, intermodal |
| `location code` plain | ✓ term is plain `location code` |
| `sequence number` number/ordinal-shaped | ✓ shape `count\|integer\|identifier` |
| Honest classification per term (no Global-only filter) | ✓ 10 Global + 12 domain_specific; each domain explicitly named in the packet |
| **`formulation code` is product/production/quality, NOT customs** | ✓ corrected — citedText and definition rewritten around product master-data formulation; standards_notes explicitly says "NOT a customs declaration identifier" |
| No invented standards anchors | ✓ where no formal standard exists (e.g. ownership type code, tracking method code), the packet cites OAGIS + per-domain published frameworks (e.g. trade-compliance: EAR/ITAR/REACH/GHS; quality: ISO 9001/14001/IATF 16949) without claiming a single combined Global enumeration |
| Forbidden internal tokens (M1..M10, F4-v2, F3, C5, AR-1..AR-5, DEC-*, "Vocabulary Admission Checklist") absent from authored fields | ✓ schema-validator regex pass on all 22 packets |
| XSD primitive-lineage boilerplate absent from `candidateEvidence.citedText` | ✓ schema-validator regex pass on all 22 packets |

## 7. Source-row coverage (unchanged from prior version)

The 22 packets collectively cover:

- **19 Direct source rows** (one packet per source row in the §2.1 `panel_ready_retry` partition of the operator-decision packet)
- **11 Role-qualified source rows** in the `map_to_existing` partition (closed by the Parent packets: 4 UOM, 4 location, 2 transport service level, 1 sequence-end)
- **3 `map_to_existing` source rows already closed by substrate** (seq 13 → existing draft payment method code; seq 16, 34 → existing active country code) — no packet needed
- **5 already-authored draft source rows** (seq 2, 3, 5, 38, 39) — no packet needed
- **2 permanent rejects** (seq 1, 37) — no packet needed

**Total: 19 + 11 + 3 + 5 + 2 = 40 ✓**

## 8. Substrate-write projection

| Phase outcome | Characteristic rows in substrate after closure |
|---|---:|
| Now | 5 (the existing drafts) |
| If all 22 panel-ready packets APPROVE + are confirmed | 5 + 22 = **27** |
| If subset of 22 approve | 5 + (subset count) |

The 27 upper bound matches the substrate-write arithmetic in §6.1 of the operator-decision packet. The 22-vs-40 distinction (characteristic-term count vs source-row count) remains in force per the operator-decision packet §2.3 reading rule.

## 9. Output layout

```
.claude/desktop-prep-output-c1-repair-pass-2-2026-06-25/
├── manifest.json                                       (22 packets + summary)
├── summary.md
└── packets/c1-rp2/
    ├── pass1-c1-rp2-01-unit_of_measure_code.json            (panel_ready_retry / global)
    ├── pass1-c1-rp2-02-location_code.json                   (panel_ready_retry / global)
    ├── pass1-c1-rp2-03-tariff_classification_code.json      (panel_ready_retry / global)
    ├── pass1-c1-rp2-04-transport_service_level_code.json    (panel_ready_retry / global)
    ├── pass1-c1-rp2-05-freight_terms_code.json              (panel_ready_retry / global)
    ├── pass1-c1-rp2-06-invoice_match_type_code.json         (panel_ready_retry / global)
    ├── pass1-c1-rp2-07-sequence_number.json                 (panel_ready_retry / global)
    ├── pass1-c1-rp2-08-receipt_routing_code.json            (panel_ready_retry / global)
    ├── pass1-c1-rp2-09-sourcing_method_code.json            (panel_ready_retry / global)
    ├── pass1-c1-rp2-10-schedule_date_basis_code.json        (panel_ready_retry / global)
    ├── pass1-c1-rp2-11-freight_classification_code.json     (panel_ready_retry / logistics/freight)
    ├── pass1-c1-rp2-12-schedule_type_code.json              (panel_ready_retry / scheduling/operations)
    ├── pass1-c1-rp2-13-job_code.json                        (panel_ready_retry / workforce/HR)
    ├── pass1-c1-rp2-14-wage_type_code.json                  (panel_ready_retry / workforce/payroll)
    ├── pass1-c1-rp2-15-price_authorization_code.json        (panel_ready_retry / pricing/commercial)
    ├── pass1-c1-rp2-16-ownership_type_code.json             (panel_ready_retry / inventory/asset-ownership)
    ├── pass1-c1-rp2-17-transaction_analysis_code.json       (panel_ready_retry / accounting)
    ├── pass1-c1-rp2-18-usage_restriction_code.json          (panel_ready_retry / commercial/trade-compliance)
    ├── pass1-c1-rp2-19-formulation_code.json                (panel_ready_retry / product/production/quality) — CORRECTED
    ├── pass1-c1-rp2-20-tracking_method_code.json            (panel_ready_retry / inventory/asset-tracking)
    ├── pass1-c1-rp2-21-expiration_control_code.json         (panel_ready_retry / inventory/perishables)
    └── pass1-c1-rp2-22-corrective_action_resource_type_code.json (panel_ready_retry / quality)
```

Each packet carries `output_hash` and `panel_packet_hash`.

## 10. Non-actions

- No panel calls. `bcf.panel_output_record` rows since 2026-06-24T08:36Z (DPO-r1 closure): 0.
- No C5 confirmations.
- No substrate mutation. `concept_registry.entity` (active): 26. `concept_registry.characteristic` (active): 62. `concept_registry.characteristic` (any non-archived): 68. `concept_registry.business_concept` (active value): 194.
- No retry-ledger writes. Gate remains `pass_1_c1_v2_complete_held_pre_c2`.
- No C2 entry.
- v1 / v2 / DPO-r1 outcomes JSONLs preserved unmodified.

Held. Awaiting operator authorization for Phase 2 (substrate-collision re-check + hash deny-list re-check + transport authorization for all 22 panel-ready packets per the operator-decision-packet §5 reduced execution plan).
