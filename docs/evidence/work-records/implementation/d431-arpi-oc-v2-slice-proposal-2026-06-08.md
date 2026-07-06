---
title: "D431 ARPI observation-v2 OC slice — read-only proposal (mini-DBCP)"
description: "Read-only proposal for the greenfield ARPI Customer Invoice observation-v2 OC slice (NETWR/VBELN/FKDAT → active BCF concepts). Step 2 of the D429 apply/proof sequence. Authors nothing; applies nothing."
status: locked
date: 2026-06-08
project: bc-core
domain: contracts
subdomain: observation-identity
focus: lifecycle
---

# D431 ARPI observation-v2 OC slice — proposal (read-only)

**Status: LOCKED (open choices O-a / O-b / O-c resolved by operator 2026-06-08) — held; authors nothing, activates nothing, writes nothing.**
**Step 2** of the D429 apply/proof sequence (seed v2 grammars ✅ → **OC-v2 slice (this)** → CC-v2 slice → O→C→M proof → MCF).
**Authorities:** DEC-4a17e0 / D431 (DBCP `d431-observation-field-identity-dbcp-2026-06-08.md`, §6 ARPI slice, §11 guardrails) · DEC-a6258b / D430 (paired CC slice).

---

## 0. Live grounding (read-only, 2026-06-08 — `bc_platform_dev`)

| Surface | Fact |
|---|---|
| `observation/2` meta-schema | **active** (seeded `a2d59b0` chain; 8 rows total) — v2 bodies now validate |
| `canonical/2` meta-schema | **active** (paired CC slice can validate once authored) |
| D431 resolver | `ObservationConceptResolverService` present on `main` (merged #239 `495c45a`) |
| `upsertMetaSchema` | jsonb-serialize fix on `main` (#241) — the seed path that proved this |
| Grain entity `e3963e45` | **"Customer Invoice"** — `lifecycle_state=active` (active version `9d01f949`, cert `dcb3d205`) |
| Anchor — amount `1a2ac2f2` | **active**, entity `e3963e45`, `representation_term=amount`, `unit=null`, `data_type=decimal` |
| Anchor — identifier `51482979` | **active**, entity `e3963e45`, `representation_term=identifier`, `unit=null`, `data_type=string` |
| Anchor — date `61e19048` | **active**, entity `e3963e45`, `representation_term=date`, `unit=null`, `data_type=date` |
| Clean source OC (ground) | `commercial_invoice_hdr` `019d77f1-26b5-72d9-9767-af551640c58c` **v1.0.0 active** maps all three from source_table `TYPE_SD_S_MAP`, transform `direct`: `NETWR→net_amount`, `VBELN→identifier`, `FKDAT→document_date_time` |
| Source lineage (from that OC) | `source_version_id=019d56d1-b378-79c6-9e99-ed267b63a686`; `source_references[0] = {role:header, cardinality:one, source_table:TYPE_SD_S_MAP, sc_version_id:019d6243-e480-776e-b9de-a08855cec44b, ac_version_id:019d6243-e4aa-7662-ba16-cca79b6ac428}` |

All three anchors are **active**, **same grain entity** (`e3963e45` = Customer Invoice), and each maps from **one** source field — so the minimal 3-entry slice has **no `role` requirement** (§11.6 only bites when one source field carries >1 concept in the same OC).

---

## 1. Target OC-v2 purpose
A **source-specific, greenfield** Customer Invoice Observation Contract (observation-v2 grammar) that maps three SAP SD-billing source fields to their **source-agnostic** active BCF concepts. It is the **admission boundary** that makes the three Customer-Invoice concepts *observable from a source* — the precondition the D431 O↔C gate checks before the paired canonical-v2 CC slice can be authored/activated. **Greenfield** (new OC header + v2 version), not a migration of the legacy `commercial_invoice_hdr` v1 (O-D: legacy OCs are not migrated).

## 2. Exact `field_mappings` candidates (3 entries — snapshot copied from the BCF concept, never the source field type)

| `source_field` | `business_concept_id` | `representation_term` | `unit` | `data_type` | `transform` | `source_table` | `role` |
|---|---|---|---|---|---|---|---|
| `NETWR` | `1a2ac2f2-a502-41c1-ad14-d08d2b976e83` | `amount` | `null` | `decimal` | `direct` | `TYPE_SD_S_MAP` | — (not needed) |
| `VBELN` | `51482979-9715-429f-949c-8961f82f436f` | `identifier` | `null` | `string` | `direct` | `TYPE_SD_S_MAP` | — (not needed) |
| `FKDAT` | `61e19048-d1c8-477b-a321-88fad1c28542` | `date` | `null` | `date` | `direct` | `TYPE_SD_S_MAP` | — (not needed) |

The three snapshot columns (`representation_term`/`unit`/`data_type`) are **copied verbatim from the live BCF concept** (§11.5), so they will pass `assertSnapshotMatches`. `business_field_code` is **optional** (O-E) — may be omitted, or set to a back-compat label (e.g. `customer_invoice_net_amount`) for display only; it carries no semantic authority.

## 3. Source table / field / transform (grounded)
- **source_table `TYPE_SD_S_MAP`**, **transform `direct`** for all three — exactly as the active `commercial_invoice_hdr` v1.0.0 OC binds them (same SDG source type-map). NETWR/VBELN/FKDAT are the SAP SD billing-header fields (net value / billing document number / billing date).
- Source lineage is **reused** from the grounding OC: `source_version_id=019d56d1…`, one header `source_references` entry with `sc_version_id=019d6243-e480…` + `ac_version_id=019d6243-e4aa…`, `source_table=TYPE_SD_S_MAP`. No new SC/AC authored.

## 4. Required OC-v2 envelope shape (candidate body)
```jsonc
{
  "$contract": "barecount/observation/v2",
  "version": "1.0.0",
  "header": { /* contract_id, name:"oc__customer_invoice_arpi_slice_type_sd_s_map", display_name:"Customer Invoice — ARPI slice (TYPE_SD_S_MAP source)", category:"observation",
                 kind:"observation", domain:"finance", subdomain:"ar", tenant_scope:{scope:"global"},
                 governance:{state:"draft"}, compatibility_policy:"strict_backward", owner, tags:[], description */ },
  "body": {
    "source_version_id": "019d56d1-b378-79c6-9e99-ed267b63a686",
    "business_object_code": "customer_invoice",            // grain BO = Customer Invoice e3963e45 (the OC *name* carries the ARPI/source slice identity)
    "source_references": [
      { "role": "header", "cardinality": "one", "source_table": "TYPE_SD_S_MAP",
        "sc_version_id": "019d6243-e480-776e-b9de-a08855cec44b",
        "ac_version_id": "019d6243-e4aa-7662-ba16-cca79b6ac428" }
    ],
    "join_semantics": [],
    "field_mappings": [ /* the 3 entries from §2 */ ],
    "identity_semantics": {
      "scope": "per_table", "deduplication": "latest_by_timestamp",
      "identity_fields": ["VBELN"]                          // LOCKED (O-a): per-invoice identity; legacy ["KUNRG"] rejected as drift
    },
    "so_schema": { /* LOCKED (O-b): minimal — declares ONLY the 3 outputs (NETWR/VBELN/FKDAT). NOT a copy of the legacy so_schema; unrelated fields / legacy identity assumptions excluded. Semantic authority stays field_mappings.business_concept_id */ }
  }
}
```

### Locked choices (operator 2026-06-08)
- **O-a — `identity_semantics.identity_fields` = `["VBELN"]` (LOCKED).** The billing document number is the per-invoice identity, consistent with the `VBELN→identifier` concept. The legacy `commercial_invoice_hdr` v1.0.0 `["KUNRG"]` (payer) is **explicitly rejected** — payer is not invoice-header identity and reads as legacy/simulator drift; do not copy it.
- **O-b — `so_schema` = minimal 3-field (LOCKED).** Declare **only** the NETWR/VBELN/FKDAT outputs. **Do not** copy the legacy `so_schema` if it carries unrelated fields or wrong identity assumptions. Semantic authority remains `field_mappings.business_concept_id` (the `so_schema` is shape, not authority).
- **O-c — OC name = `oc__customer_invoice_arpi_slice_type_sd_s_map` (LOCKED); display_name "Customer Invoice — ARPI slice (TYPE_SD_S_MAP source)".** Source-specific slice name, not generic customer invoice. The S/4-confirmed variant (`…_sap_s4`) is **not** used: SAP S/4 is not first-hand proven via a real Published-OData reader chain (Zero-Claims Policy / D384), and the bound source is the SDG `TYPE_SD_S_MAP` corpus — so the `type_sd_s_map` fallback is the accurate, claim-safe name. It can be renamed to the `_sap_s4` form **only** once a real S/4 OData reader chain produces real snapshots.

## 5. Integrity expectations (what `assertObservationFieldIntegrity` will check)
- **Concepts active** — all three are `active` ✓.
- **One grain entity** — all three resolve to entity `e3963e45` (Customer Invoice) ✓ → derived grain entity is unambiguous.
- **Concept-unique within the OC** — three distinct concepts, no duplication ✓.
- **Snapshot equals live BCF triple** — snapshots copied from the concept (amount/null/decimal · identifier/null/string · date/null/date) ✓ → no drift refusal.
- **Source-field / role distinction (§11.6)** — each source field (NETWR, VBELN, FKDAT) appears **once**; no source field maps to >1 concept → **no `role` required**, no refusal ✓.

## 6. Activation expectations
- **`observation/2` meta-schema row exists and is active** ✓ (seeded, confirmed).
- **D431 resolver present** ✓ (`ObservationConceptResolverService` on `main`).
- Authoring (`createVersion`) and activation (`transitionState → active`) both run `assertObservationFieldIntegrity` and **fail closed** if the resolver is absent. With §5 satisfied, **authoring + activation should pass.** The OC then has a single **active** observation-v2 version declaring the three concepts as observable from a source.

## 7. What this unlocks
Once this OC-v2 slice is **active**, the D431 O↔C gate (`assertConceptsObservableFromSource`) can see all three Customer-Invoice concepts declared observable from a source. That is the precondition for the **paired canonical-v2 CC slice** (D430) — which would otherwise **fail closed** at CC authoring/activation. This is concept-identity only (not OC identity, not source coupling — §11.3/§11.4); runtime source selection is unchanged. It sets up the **first full O→C→M concept-identity proof** for ARPI (after the CC slice + the governed ARPI MC rebind).

## 8. Explicit exclusions
- ❌ No canonical-v2 CC authoring yet (next step, after this OC is active).
- ❌ No ARPI MC rebind (separate governed new-MC-version track, D430 O2).
- ❌ No MCF materialization.
- ❌ No direct DB writes / no DDL / no seeding. **This document authors nothing.**
- ❌ No force activation — activation only via the normal `transitionState` gate (fail-closed integrity check).
- ❌ No legacy OC migration; the `commercial_invoice_hdr` v1 OC is read-only ground truth, untouched.

## 9. Stop conditions — checked against live state
| Stop condition | Status |
|---|---|
| any anchor missing / inactive / superseded | **CLEAR** — all three `1a2ac2f2`/`51482979`/`61e19048` are `active`, none superseded |
| source lineage ambiguous | **RESOLVED** — `commercial_invoice_hdr` is the clean SD-billing source (all three present, one `source_table=TYPE_SD_S_MAP`, one SC/AC). `identity_fields` now **locked to `["VBELN"]`** (legacy `["KUNRG"]` rejected). |
| snapshot differs from live BCF concept | **CLEAR** — snapshots are copied from the concept, not the source field type (§11.5) |
| existing OC/source contracts don't support NETWR/VBELN/FKDAT cleanly | **CLEAR for the slice** — each maps once to one concept in the grounding OC. (Note: the legacy corpus doubles NETWR/VBELN onto secondary business fields; the **3-entry v2 slice does not**, so no §11.6 role is needed) |

**No hard stop tripped, and all three open choices are now LOCKED (§4).** The slice is fully specified and ready to author when authorized.

## 10. Foundation gate
- **Repair location B** (observation contract semantics) — the OC field-map declares its concept by identity; `source_field`/`source_table`/`transform` stay legitimately physical (**A**). The slice is authored via the SERVICES-ONLY path (no DB row hand-edit). Invariant I (meaning anchored once at the admission boundary), IV (explicit concept references replace the free string). No lower-layer compensation; reads don't trigger evaluation.

## 11. If approved — execution shape (separate, gated; NOT done here)
Author the greenfield OC-v2 via the SERVICES-ONLY contract path (`ContractService.createVersion` → `transitionState` activate), confirm the integrity gate passes, then verify one active observation-v2 version exists for entity `e3963e45` declaring the three concepts. **Open choices locked; held — awaiting your explicit authorization to author + activate the OC-v2 slice. The OC is NOT authored by this doc.**
