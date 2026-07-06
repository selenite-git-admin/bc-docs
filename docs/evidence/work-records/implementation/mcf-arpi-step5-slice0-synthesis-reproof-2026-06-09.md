---
title: "ARPI Step-5 Slice 0 — contract_json Synthesis Re-Proof (read-only go/no-go)"
description: Read-only re-proof of the ARPI contract_json synthesis against the now-clean active MCV b1933c30, replicating the D430 canonical resolver + D431 O↔C resolver verbatim against live bc_platform_dev. Confirms every UNRESOLVED@C envelope field the 2026-06-07 synthesis proof named is now resolvable, yielding an evaluation-grade envelope. Verdict GO. The go/no-go gate for the Step-5 (D428) materialization writer. No writes, no synthesizeContractJson, no contract.* write, no materialization.
status: complete
date: 2026-06-09
project: bc-core
domain: contracts
subdomain: metric-store
focus: materialization-boundary
governs: DEC-61f7c8 (D428) · DEC-a6258b (D430) · DEC-4a17e0 (D431) · DEC-c3e57f (D422 MCF)
supersedes_finding_in: mcf-arpi-contract-json-synthesis-proof-2026-06-07.md (Bar-2 block — now cleared for ARPI)
task: TSK-a8bedb
---

# ARPI Step-5 Slice 0 — `contract_json` Synthesis Re-Proof (read-only)

> **Verdict: GO.** Every `UNRESOLVED@C` field the 2026-06-07 synthesis proof named is now resolvable for the clean active ARPI MCV `b1933c30`. The Bar-2 (evaluation-readiness) **resolution** block is cleared *for ARPI*. This authorizes nothing: it is the read-only go/no-go gate for the Step-5 materialization writer (TSK-0ba31e). **No writes, no `synthesizeContractJson`, no `contract.*` write, no materialization occurred.**

## Method

Replicated the live resolver logic **verbatim, read-only**, against `bc_platform_dev`:
- **D430** `CanonicalConceptResolverService.resolve(grainEntityId, conceptId)` — active `contract.canonical_contract_version` where `contract_json.$contract='barecount/canonical/v2'`, match `body.field_selection[].business_concept_id`, gated on `concept_registry.business_concept.entity_id == grain`.
- **D431** `ObservationConceptResolverService.isConceptObservableFromSource(conceptId)` — active `contract.observation_contract_version` (`$contract='barecount/observation/v2'`), `body.field_mappings[].business_concept_id` membership.
- Inputs read from `mcf.metric_contract[_version]` + `mcf.metric_variable_binding`. (Script: `bc-core/scripts/_step5-slice0-arpi-synthesis-reproof.mjs`, read-only.)

## Grounding (live, read-only — 2026-06-09)

| # | Check | Result |
|---|---|---|
| 1 | Active/current ARPI MCV | ✅ `b1933c30` `governance_state_code=active`, `is_current=true`, parent `7596213d`, grain `e3963e45` (on `mcf.metric_contract.grain_entity_id`) |
| 2 | Active OC-v2 + CC-v2 | ✅ CC-v2 `cc__customer_invoice_arpi_slice` (`019ea703…`, v1.0.0) active; OC-v2 `oc__customer_invoice_arpi_slice_type_sd_s_map` active |
| 3 | `b1933c30` bindings | ✅ numerator_source→`1a2ac2f2`, denominator_key→`51482979`, temporal_anchor→`61e19048` — all on grain `e3963e45`, all concepts `lifecycle_state=active` |
| 4 | D430 resolve per concept | ✅ all 3 resolve on the grain (see field map) |
| 5 | Previously-`UNRESOLVED@C` envelope fields | ✅ all now derivable (see §Envelope) |
| 6 | `metric_definition_id` NOT NULL | ⚠️ `is_nullable=NO` — **writer-only** blocker (see §Writer questions); does **not** affect this read-only proof |
| 7 | Remaining Bar-2 unresolved mapping | ✅ none — `all_canonical_resolved_on_grain=true`, `single_canonical_contract=true`, `all_observable=true` |

## Exact resolved field map (D430 canonical + D431 observation)

| Metric variable | Bound concept | D430 → CC-v2 field | D431 observable from (OC-v2) |
|---|---|---|---|
| `numerator_source` (amount/decimal) | `1a2ac2f2` | `cc__customer_invoice_arpi_slice` **`.amount`** | `TYPE_SD_S_MAP.NETWR` |
| `denominator_key` (identifier/string) | `51482979` | `cc__customer_invoice_arpi_slice` **`.document_number`** | `TYPE_SD_S_MAP.VBELN` |
| `temporal_anchor` (date/date) | `61e19048` | `cc__customer_invoice_arpi_slice` **`.document_date`** | `TYPE_SD_S_MAP.FKDAT` |

All three resolve to **one** active CC-v2 (`019ea703…`) on the single grain entity `e3963e45` → `co_bindings` is unambiguous. The full **O→C→M** chain holds by concept identity: source field → (OC-v2) concept → (CC-v2) canonical field → (MCV) variable binding.

## Synthesized envelope sketch (read-only — written nowhere)

`UNRESOLVED@C` from the 2026-06-07 proof is replaced by the resolved value **in bold**. This is a sketch; no `contract.*` row was written.

```jsonc
{
  "$contract": "barecount/metric/v1", "version": "1.0.0",
  "header": {
    "kind": "metric", "category": "metric",
    "name": "average_revenue_per_invoice", "display_name": "Average Revenue per Invoice",
    "governance": { "state": "active" },
    "domain": null, "subdomain": null, "owner": null,   // mcf function/subfunction/owner NULL (cosmetic)
    "contract_id": "<minted on write>", "tenant_scope": { "scope": "global" }
  },
  "body": {
    "unit": "<DEFAULT — see writer Q2>",                 // numerator unit refreshed USD→null by rebind
    "direction_code": "higher-is-better",                // seed/default
    "formula": { "text": "O1 = SUM(I1) / COUNT_DISTINCT(I2)" },  // AST→text translate
    "variables": [
      { "role": "output", "var_code": "O1", "field_code": "average_revenue_per_invoice" },
      { "role": "input",  "var_code": "I1", "field_code": "amount" },          // ← RESOLVED
      { "role": "input",  "var_code": "I2", "field_code": "document_number" }  // ← RESOLVED
    ],
    "grain": [
      { "key": "fiscal_period", "source": "business_field", "field_code": "fiscal_period" }  // ← grain field is the STAMPED fiscal_period business_field (D363–D365), NOT document_date; document_date is the CC posting_date_field it derives from (upstream, at canonical resolution). See writer Q3 + Guard B.
    ],
    "co_bindings": [
      { "role": "primary",
        "canonical_contract": "cc__customer_invoice_arpi_slice",               // ← RESOLVED
        "fields_used": ["amount", "document_number"] }                        // ← the two formula operands; document_date is the CC posting_date_field (basis for the stamped fiscal_period), not a formula-used field
    ],
    "temporal_gate": {
      "field_code": "fiscal_period",                     // ← gate operates on the STAMPED fiscal_period business_field, NOT document_date (the temporal_anchor concept resolves to the CC's document_date posting_date_field, from which fiscal_period is stamped at canonical resolution); not a formula variable
      "required_periods": 1, "completeness_threshold": 0.8  // period_aggregate translate
    }
  }
}
```

> **Amendment (2026-06-09, writer PR `b46c657`).** The envelope above is reconciled to the **implemented** Step-5 writer envelope (writer-DBCP §5) per operator ruling: `grain[].field_code` and `temporal_gate.field_code` are **`fiscal_period`** (a stamped `business_field`), **not** `document_date`; `document_date` is the CC `posting_date_field` from which `fiscal_period` is stamped at canonical resolution (D363–D365), and is **not** a formula variable. `co_bindings.fields_used` carries the two formula operands. The earlier draft of this sketch showed `document_date` in the grain / temporal_gate / fields_used — that was the pre-implementation framing and does **not** match the writer. The writer's **Guard B** fail-closes unless the resolved active CC declares `body.posting_date_field='document_date'` AND `document_date ∈ field_selection`.

**Every binding field that was `UNRESOLVED@C` is now resolved.** What remains are *translate/default/mint* concerns (already classified 🟠/🟡 in the 2026-06-07 proof), not resolution blocks.

## Remaining writer-DBCP questions (for TSK-0ba31e — out of scope here)

1. **`metric_definition_id` NOT NULL FK** (`fk_metric_contract__metric_definition`, confirmed `is_nullable=NO`). Per synthesis-proof §5: **(b)** drop/relax the FK as a clean-slate step (preferred for the ARPI proof) vs **(c)** repoint to an MCF provenance column (durable, larger change). A schema change → its own approved DBCP. **Writer-only** — never reached by read-only synthesis.
2. **`body.unit` derivation.** The rebind refreshed the numerator unit `USD → null` (D430 snapshot == live concept). `body.unit` ("currency") is therefore no longer derivable from the unit snapshot; the writer needs a default/convention or a metric-level unit declaration.
3. **Grain/temporal field is `fiscal_period`, not `document_date` (RESOLVED in the writer).** The materialized envelope's `grain[].field_code` and `temporal_gate.field_code` are **`fiscal_period`** (a `business_field`), stamped at canonical resolution from the CC's `posting_date_field` (`document_date`) via the tenant fiscal calendar (D363–D365) BEFORE the engine runs. The engine GROUP-BYs / temporal-gates on the stamped `fiscal_period`, and `document_date` is **not** a formula variable. The writer's Guard B fail-closes unless the resolved active CC declares `body.posting_date_field='document_date'` AND `document_date ∈ field_selection`. (Implemented: writer-DBCP §5; PR head `b46c657`.)
4. **Evaluation-eligibility artifacts** (not part of the envelope, required for the engine to actually evaluate — synthesis-proof §3.7): a `contract.chain_status` row (`chain_verdict='complete'`), `audit_status_code`, and an active `tenant.contract_binding`. The envelope is now synthesizable; these gating artifacts are separate writer/runtime steps.
5. **Formula AST → engine text + var_code mapping** (mechanical translate: `divide/sum/count_distinct` → `/`,`SUM()`,`COUNT_DISTINCT()`; `variable_ref.role` → `var_code`). Lock the translation in the writer; it is deterministic.

None of (1)–(5) is a BCF-concept→canonical-field resolution gap. The single root cause that blocked the 2026-06-07 proof is **closed for ARPI**.

## No-writes attestation

This proof performed **only** `SELECT`/`to_jsonb` reads against `mcf.*`, `contract.*`, `concept_registry.*`, and `information_schema`. **No** `contract.*` write, **no** `synthesizeContractJson` implementation, **no** code change, **no** DB mutation, **no** materialization, **no** tenant runtime evaluation. The D428 §9 guardrail is intact. bc-core remained on `main d92dda3`.
