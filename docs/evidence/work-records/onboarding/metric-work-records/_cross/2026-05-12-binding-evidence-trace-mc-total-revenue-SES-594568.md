---
title: "Binding Evidence Trace — mc__total_revenue (Apex)"
session: SES-594568
date: 2026-05-12
status: complete
type: binding-evidence-trace
authority: DEC-a17d0f
related:
  - 2026-05-12-sda-phase1-proof-summary-SES-594568.md
---

# Binding Evidence Trace — `mc__total_revenue`

Read-only trace. No writes, no certifications, no proposed gates.

## Chosen metric

| field | value |
|---|---|
| metric_contract_id | `019d7838-50c5-7d96-a3ec-cfef9432d451` |
| metric_contract_name | `mc__total_revenue` |
| display_name | `Mc — Total Revenue` |
| version_code | `1.0.0` |
| function / subfunction | `finance` / `general_finance` |
| formula | `O1 = SUM(I1)` |
| variables | `I1` (input, `currency`, `field_name='sales_revenue_item'`) + `O1` (output) |
| chain_status.chain_verdict | `complete` |
| chain_status.grain_complete | `true` |
| chain_status.has_live_source | `true` |
| canonical_contract binding | `cc__actual_ledger` (`019d762a-17b6-71d1-8cdf-7b899eb28247`), role `primary` |

Chain reads (input direction):

```
S/4HANA FAGLPOSE.WRBTR
    │  (observation_field_map, OC: oc__s4hana__faglpose__actual_ledger v1.0.0)
    ▼
BF.actual_ledger_amount     id 019d6db8-8eb0-7d65-bc62-9dcacdc74261
                             status_code='certified', semantic_family=NULL,
                             definition_standard='OAGIS', data_type='number',
                             certification_record rows: 0  ←── legacy-certified
    │  (cc_field_mapping in CC cc__actual_ledger)
    ▼
CF.sales_revenue_item       id 72ae5625-1144-4550-942d-dc6b68e1209c
                             status_code='draft', semantic_family=NULL,
                             data_type='number'
    │  (CC field referenced by MC variable I1.field_name)
    ▼
MC variable I1 (currency, input)
    │  (formula: O1 = SUM(I1))
    ▼
mc__total_revenue snapshot
    │  (snapshot table in tbc_apex_dev — not directly observable
    │   from the bc_platform_dev connection; chain_status reports
    │   has_live_source=true)
```

## Binding Evidence Trace — flat table

| metric_id | edge_type | from_node | to_node | dictionary_layer_status | compatibility_gate_status | consumption_evidence | evidence_detail | observed_gap |
|---|---|---|---|---|---|---|---|---|
| `019d7838-…cad98` | source_column_to_BF | `s4hana.FAGLPOSE.WRBTR` | `BF.actual_ledger_amount` | not_applicable | no_gate_today | compatible_no_evidence | OC `oc__s4hana__faglpose__actual_ledger` v1.0.0 declares the mapping (`observation_field_map.source_field_name='WRBTR'`, `source_entity='FAGLPOSE'`). chain_status reports `has_live_source=true`, so admitted rows are flowing somewhere, but no per-edge admission-time evidence ledger exists. | No SC/AC/OC dictionary-certification mechanism. No mechanism to verify that the WRBTR column actually carries "actual ledger amount" semantics on the Apex source. The "mapping was authored by a human" is the only assertion. |
| `019d7838-…cad98` | BF_to_CF | `BF.actual_ledger_amount` | `CF.sales_revenue_item` | **not_dictionary_certified** | no_gate_today | compatible_no_evidence | `cc_field_mapping` row `056a3e05-098b-41ba-b4e6-7eb25a909031` in CC `cc__actual_ledger` pairs the two. **BF's `status_code='certified'` is legacy-asserted, not SDA-4 audited** — zero rows in `contract.certification_record` for this BF. CF is in `draft` and has no CF-side certification mechanism today. | (a) BF certification predates SDA-4 — column value says "certified" but no audit trail exists; would not pass G5/G6 today because `semantic_family=NULL`. (b) CF certification is unimplemented Phase 1-side. (c) G11 BF-CF compatibility gate is declared (DEC-b7affa) but not live, so the pairing has no mechanical compatibility check. |
| `019d7838-…cad98` | CF_to_MC_variable | `CF.sales_revenue_item` | `MC.I1 (currency, input)` | not_applicable | passes_known_gate | compatible_no_evidence | `metric_binding.fields_used = ['sales_revenue_item']` for binding `db8cb957-…` (role=`primary`); `metric_formula_variable.field_name='sales_revenue_item'` for `I1`. Name match holds; `metric_formula_verification` exists for formula syntactic checks (`O1 = SUM(I1)` is well-formed); the variable's `unit_type_code='currency'` is recorded. | No semantic check between the CF's declared meaning and the variable's intent. "sales_revenue_item" appearing in both `fields_used` and `metric_formula_variable.field_name` is string-equality, not semantic-equivalence. |
| `019d7838-…cad98` | MC_to_snapshot | `mc__total_revenue` | `snapshot rows (tbc_apex_dev)` | not_applicable | passes_known_gate | not_observable_today | `chain_status.chain_verdict='complete'`, `grain_complete=true`, `has_live_source=true`, `variables_complete=1/1`. Snapshots cannot be inspected from this connection (snapshot tables live in `tbc_apex_dev`; bc-postgres MCP is bound to `bc_platform_dev`). | No platform-side per-snapshot consumption telemetry. No operator-reaction signal (dispute / acknowledge / quarantine flags) recorded anywhere reachable from this view. Whether the produced values "look right to an Apex operator" is silent in the platform DB. |

## Layer-by-layer status

**Layer 1 — Dictionary certification:** 1 of 2 dictionary primitives in the chain (the BF, the CF) is non-trivially classified. The BF carries `status_code='certified'` but **no SDA-4 audit row** — this is the legacy-certification pattern that pre-dates the work documented in `2026-05-12-sda-phase1-proof-summary-SES-594568.md`. By the SDA-4 standard, this BF would re-fail G5 today (`semantic_family=NULL`) and would need an override or metadata PATCH before SDA-4 would re-issue a certified row. The CF is `draft`; no CF certification mechanism exists.

**Layer 2 — Compatibility gates:** Three of four edges have `no_gate_today` or only string-equality / formula-syntax mechanical checks. Only `MC_to_snapshot` passes a non-trivial mechanical gate (`chain_status.chain_verdict='complete'` is the rolled-up "the chain assembles and a snapshot can be produced" signal — itself a composite, not a single gate).

**Layer 3 — Consumption evidence:** Universally **silent** on a per-edge basis. Every edge except `MC_to_snapshot` is `compatible_no_evidence` — the chain is producing snapshots, but no record exists at any per-edge granularity that says "this specific edge has been observed to produce sane values". `MC_to_snapshot` is `not_observable_today` because the snapshot rows live in the tenant DB and are not reachable through this connection.

**Layer 4 — Metric Trust Evidence:** see next section.

## Metric Trust Evidence

**Verdict for `mc__total_revenue` on Apex: `mechanically_producing_only`.**

What this means:
- The chain assembles. The formula is well-formed. A snapshot is produced (per `chain_status.has_live_source=true` + `chain_verdict='complete'`).
- One dictionary primitive in the chain (BF `actual_ledger_amount`) carries `status_code='certified'`, but the assertion has no SDA-4 audit trail behind it — it is legacy-certified. By our current SDA standard, this BF is not dictionary-certified.
- The other dictionary primitive in the chain (CF `sales_revenue_item`) is in `draft`. No CF certification mechanism exists today.
- No per-edge consumption evidence is recorded anywhere reachable from the platform DB. The "metric is producing" signal is the only positive evidence; it is mechanical, not contextual.

Which edges carry evidence:
- `MC_to_snapshot`: weak-positive evidence via `chain_status.has_live_source=true`. This says "something is being produced", not "what is produced is right".
- All other edges: silent (`compatible_no_evidence` / `not_observable_today`).

Why this is **not** `evidence_supported`:
- "Producing snapshots" is not the same as "producing right snapshots". An operator confirmation, a downstream consumer's silence-after-consumption, or a known-good reconciliation against an external source would be evidence. None of those is observable in this trace.

Why this is **not** `evidence_contradicted`:
- No negative signal is observable either. Nothing in the chain shows a dispute, a quarantine, a snapshot rejected for being out-of-range, or a re-computation that produced a different answer. Silence in both directions.

Why this is **not** `not_assessable`:
- The chain mechanically assembles end-to-end with one composite gate (`chain_status`) passing. The verdict is `mechanically_producing_only` rather than `not_assessable` because mechanical production *is* observable; it is just not sufficient.

Why this is **not** `hard_blocked`:
- No edge fails a gate it could have passed. No structural breakage. The chain mechanically functions.

## Note (operator-facing)

> Dictionary certification is necessary but not sufficient. Compatibility gates rule out obvious nonsense. Consumption evidence is what can rule in trust.

For `mc__total_revenue` on Apex today: dictionary certification is *partially* present and *partially* legacy. Compatibility gates are *mostly* absent at the per-edge granularity. Consumption evidence is *universally silent*. The metric is producing snapshots; whether those snapshots are trustworthy is, at this moment, **not a question this trace can answer**.

## What this trace exposes about the larger system

- **The single most surprising finding:** the one "certified" BF in this chain was certified by a pre-SDA path. Anyone trusting `status_code='certified'` as evidence of SDA-4 audit would be misled here. This pattern likely repeats across most of the 6,779 historically-certified BFs in the registry.
- The structural gap (no per-edge consumption ledger anywhere) means that even when SDA-4 certifications accumulate, they will not by themselves answer "is this metric trustworthy" — they will only answer "is this primitive dictionary-coherent". The two questions are different and the trace makes the difference visible per edge.
- `MC_to_snapshot` evidence is hidden in the tenant DB and is unreachable from a platform-side trace. Any future Metric Trust Evidence surface will need either tenant-DB query access, or a platform-side echo of snapshot consumption telemetry, to bring this layer into view.

## Boundaries honoured

- Read-only. No PATCH, no certify, no DBCP, no master.* edits.
- No new gates proposed. No new tasks filed. No trust score computed.
- No write to any DevHub, ledger, or schema artifact beyond this MWR.
- One metric traced. No other metrics inspected.

---

**End of Binding Evidence Trace.**
