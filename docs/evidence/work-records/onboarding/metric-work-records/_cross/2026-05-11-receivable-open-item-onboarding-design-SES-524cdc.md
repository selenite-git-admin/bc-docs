---
metric: cc__receivable_open_item (architectural enabler for DSO v2 / DPO v2 / DIO v2)
metric_version: n/a
tenant: apex
source_system: sap_ecc
work_type: tenant-onboarding
session_uid: SES-524cdc
date: 2026-05-11
status: decision-pending
related_commits:
  - 276ff15  # docs(adr): promote open-item canonical semantics ADR
  - 9f0ce57  # docs(metric): scope DSO open-item architecture
related_tasks: []
related_adrs:
  - DEC-1db1c7  # D401 — Open-item / as-of canonical semantics (proposed) — authority for this onboarding
  - DEC-c012c0  # D400 — Metric Contract grammar v1.1 (proposed) — layered pair
related_change_records:
  - CHG-9b61c9                  # SES-524cdc plan-side
repair_location: A+C
affected_boundary: canonical_evaluation
foundation_gate: passed
---

# Receivable open-item onboarding — design discovery — 2026-05-11

> **This record is orientation memory, not contract authority.** Canonical sources (DEC-1db1c7 / ADR-1db1c7.md, contract.* tables, evidence rows) win on conflict.

## Summary

DSO Phase-2 Slice 1 was scoped as "author + provision `cc__receivable_open_item` for apex" — the smallest provable step of DEC-1db1c7 (D401) Mechanism A. Discovery in this session shows the slice is materially larger than a single-turn operation: it spans 5+ governed-service calls in sequence (OC/CC/canonical_mapping/cc_field_mapping/tenant_binding/fact-table-provisioning/reader-execution/verification), and **multiple substantive design decisions remain unresolved** before any contract authoring should proceed.

This record captures the Foundation Gate, the service-path inventory, the prerequisite-artifact survey, and the 5 outstanding design decisions. **No contracts, mappings, bindings, or schemas were authored this session.** Operator direction is required on each design decision before sub-slicing the implementation work.

## Foundation Gate Result

- **Repair location:** A + C. Source already emits `AUGDT` / `AUGBL` (verified on `bc-sdg` CustomerOpenItemSet, probed during Slice 1f and re-probed here). Layer C is the work: new CC + canonical_mapping + cc_field_mapping + tenant binding.
- **Affected boundary:** `canonical_evaluation`.
- **Six-invariant pre-check:**
  - I (meaning produced once) — open/cleared distinction comes from source; no SDG tuning, no engine inference, no read-side projection. ✓
  - II (object ordering) — Source → Reader → SO → Admission → Canonical → CO. Unchanged. ✓
  - III (state immutable) — new COs in a new CC family; legacy `cc__receivable_hdr` untouched. ✓
  - IV (references explicit) — open-AR CO ids will surface in `inputReferencesJson` at DSO v2 evaluation time (Slice 2 work; not in Slice 1's scope). ✓
  - V (non-replayable) — each evaluation produces a new `metric_evaluation_id`. ✓ structurally.
  - VI (evidence emitted) — admission/canonical/resolution ledger rows. ✓
- **No SDG tuning, no read-model compensation, no DSO v2 authoring this slice.** ✓
- **Override?** none.

## Service-path inventory

| Function | Service path | Confirmed |
|---|---|---|
| OC preview / create | `POST /api/onboarding/oc/preview`, `POST /api/onboarding/oc/create` (bc-core `oc-onboarding.controller.ts`; DTO `CreateOcDto` requires `businessObjectCode`, `sourceVersionId`, `sourceTables`, `joinSemantics`, `fieldMappings`, `identitySemantics`) | ✓ |
| CC preview / create | `POST /api/onboarding/cc/preview`, `POST /api/onboarding/cc/create` (bc-core `cc-onboarding.controller.ts`) | ✓ |
| CC field-mapping add | `POST /api/onboarding/cc/{contractId}/field-mappings` (atomic add) | ✓ |
| CC field-mapping replace (D330-R5) | `POST /api/onboarding/cc/{contractId}/field-mappings/{mappingId}/replace` (used in Slice 1 of total_revenue arc) | ✓ |
| canonical_mapping (mapping body) | Authored as part of CC onboarding flow OR via the canonical-wizard sessions endpoint `POST /api/canonical-wizard/sessions` + `complete` | ✓ partially — needs further trace |
| Tenant binding for a CC | `tenant.contract_binding` rows written via schema-provisioner onboard-connector OR directly via `devhub_tenant_bind_metrics` (MC-only — needs separate path for CC) | **⚠ GAP** — see Decision D5 below |
| Fact-table provisioning | `POST /api/schema-provisioner/onboard-connector` (full chain walk) OR `POST /api/schema-provisioner/nightly-reconcile` | ✓ |
| Reader execution | `POST /api/t/test-bench/execute-reader` (used in Slice 1b, 1g) | ✓ |
| Verification — tenant DB read-only | `postgres` client → `tbc_apex_dev` SELECT (used in Slice 1f, 1g, 1h) | ✓ |

## Prerequisite-artifact survey

### Business Objects

Existing BOs in the AR domain:

- `receivable_hdr` (Receivable Header, approved, subfunction `accounts_receivable`, basic tier)
- `receivable_line` (Receivable Line, approved)
- `gaap_receivables` (GAAP Receivables, approved)

**No** `receivable_open_item` BO exists. **Design Decision D1** — see below.

### Business Fields under `receivable_hdr`

25 BFs already certified (OAGIS standard), including:

- `receivable_hdr_amount` (number) — could serve as the open-item amount
- `receivable_hdr_functional_amount` (number) — functional-currency variant
- `receivable_hdr_party_identifier`, `receivable_hdr_bill_to_party_identifier`, `receivable_hdr_customer_identifier` (string) — customer identity
- `receivable_hdr_document_date_time` (timestamp) — posting date
- `receivable_hdr_status_code` (code) — currently stamps cleared/open via AUGBL value
- `receivable_hdr_payment_terms_code`, `receivable_hdr_tax_code` (code)
- `receivable_hdr_uuid`, `receivable_hdr_identifier`, `receivable_hdr_source_identifier` (string) — IDs

**No** `receivable_open_item_*` BFs exist. **Design Decision D2** — reuse `receivable_hdr_*` BFs or author new ones?

### Existing OCs that touch CustomerOpenItemSet

```
oc__s4hana__bsid__receivable_hdr v1.0.0 — handles BOTH BSID + CustomerOpenItemSet
  Source: BSID (15 BF mappings)
  Source: CustomerOpenItemSet (3 BF mappings — GJAHR → receivable_hdr_fiscal_year, MADAT → ..._last_modification_date_time, ZFBDT → receivable_hdr_due_date)
```

**The existing OC already partially handles CustomerOpenItemSet.** No additional fields are mapped from CustomerOpenItemSet today; the OC reads BSID for the bulk of receivable header data and only 3 supplementary fields from CustomerOpenItemSet.

**Crucial subtlety:** `AUGBL` from BSID maps to `receivable_hdr_status_code`. Per the existing OC, an open vs cleared state is partially derivable from this BF — but the legacy CC `cc__receivable_hdr` does NOT filter on it; it admits all postings. Hence the append-only behavior the DSO MWR flagged.

**Design Decision D3** — three sub-options for the new CC's source path:

- **D3a** Reuse existing OC `oc__s4hana__bsid__receivable_hdr`; place the AUGBL-IS-NULL filter at the **canonical_mapping** layer (via `filter_json` on cc_field_mapping or via a CC-level filter clause if supported).
- **D3b** Author new OC `oc__s4hana__customer_open_items__receivable_open_item` that reads CustomerOpenItemSet directly with a reader-level `$filter=AUGBL eq null`. Requires verifying the V2 executor supports OData `eq null` syntax (sap-odata-v2.executor.ts `buildDateFilter` only does date ranges today — extending to NULL-equality is engine code work).
- **D3c** Reuse the existing OC at admission/observation layer; perform open/cleared partitioning at canonical_resolution layer (engine code work).

D3a is the lowest-risk option but depends on canonical_mapping's `filter_json` semantics supporting null-equality. D3b is a one-shot reader change. D3c is a substantive engine change.

### Source contracts touching CustomerOpenItemSet

Six `sc__*__bsid*` source contracts active (`sc__ecc__bsid`, `sc__s4hana__bsid`, plus `_bck`, `_rec`, `_pso_bck`, `_oilbsid_bck` variants). **No source_contract explicitly named for CustomerOpenItemSet** — the existing OC reads it through one of the BSID source contracts, suggesting CustomerOpenItemSet is treated as a secondary table within an existing source contract's tableset.

**Design Decision D4** — does the new CC's OC bind to an existing BSID source_contract, or does a new `sc__s4hana__customer_open_items` source_contract need authoring? Slice 1b's invoice readers used `sc__s4hana__i_billingdocument` (S/4HANA V4); BSID is V2/ECC. The CustomerOpenItemSet endpoint is V2 (per Slice 1g simulator probe).

### Tenant binding semantics (CC-level)

`tenant.contract_binding` schema (already inspected in Slice 1c): `contract_family text`, `contract_id uuid`, `version_code text`. So CC bindings ARE supported in the schema. But the runtime API for writing them:

- `devhub_tenant_bind_metrics` MCP wraps **MC** bindings only (D394).
- `POST /api/schema-provisioner/onboard-connector` writes CC + reader bindings as part of a tenant onboarding walk.
- A dedicated "bind one CC to one tenant" endpoint was not found in this discovery.

**Design Decision D5** — for a single-CC binding to apex without re-onboarding the entire connector, what's the governed path? Options:
- D5a Use `onboard-connector` and accept it walks every reachable CC (over-broad).
- D5b Check whether `schema-provisioner/nightly-reconcile` provisions a single CC's fact table once its binding row exists.
- D5c If neither is single-CC-scoped, this is a **service gap**. Surface it; either author a small admin endpoint or proceed under DBCP for the one tenant_binding row insert.

## Source-feasibility (re-probed in Slice 1f; re-confirmed here)

bc-sdg `CustomerOpenItemSet` V2 endpoint `http://localhost:6200/sdg/apex-motors/CustomerOpenItemSet`:

- Total rows for apex: 8 (historical) + 73 (per probe of full sample; this number from earlier slices). Actual count may vary.
- Field columns include: `BUKRS, BELNR, GJAHR, BUZEI, KUNNR, DMBTR, WRBTR, SHKZG, WAERS, BUDAT, BLDAT, BSCHL, KOART, HKONT, SGTXT, BLART, USNAM, ZFBDT, MADAT, MWSKZ, WMWST, XBLNR, PRCTR, GSBER, ZUONR, RSTGR, AUGDT, AUGBL, ZTERM, MAHNS`.
- `AUGDT` and `AUGBL` populated on cleared items, `null` on open items.
- Sample open row: `BUKRS=1100, KUNNR=FLT-MTRLNK, DMBTR=248320000.00, WRBTR=248320000.00, BUDAT=2024-08-15, AUGBL=null, AUGDT=null` — confirms semantic.

All fields needed for the new CC are present at the source. Source feasibility is not the blocker.

## Outstanding design decisions (5)

Each decision is small but consequential. None can be inferred from current evidence without operator input.

| # | Decision | Options | Recommended default |
|---|---|---|---|
| **D1** | New BO `receivable_open_item` or reuse `receivable_hdr` BO? | (a) author new BO; (b) reuse `receivable_hdr` BO (the new CC simply lives under the same BO with a different scope) | **(b) reuse**. The new CC is semantically a *subset* of the existing receivable_hdr BO's instances (only open ones). Authoring a parallel BO duplicates the schema for no semantic gain. |
| **D2** | New BFs `receivable_open_item_*` or reuse `receivable_hdr_*` BFs? | (a) author new BF family; (b) reuse existing `receivable_hdr_*` BFs | **(b) reuse**. Same rationale as D1; CFs (which mappings ultimately resolve to) remain the semantic carrier. |
| **D3** | Where to place the AUGBL-IS-NULL filter? | (a) canonical_mapping-level filter_json (lowest-risk if supported); (b) new OC with reader-level $filter (medium; tests V2 executor's null-handling); (c) canonical_resolution code change | **(a)** — pending verification that `cc_field_mapping.filter_json` or `canonical_mapping_version.mapping_json` supports null-equality predicates. |
| **D4** | New source_contract for CustomerOpenItemSet, or piggy-back on existing BSID source_contract? | (a) author `sc__s4hana__customer_open_items` v1.0.0; (b) extend an existing BSID source_contract's tableset; (c) reuse without change (existing OC already touches CustomerOpenItemSet) | **(c) reuse without change**. The existing OC mapping already enumerates CustomerOpenItemSet fields; the source_contract chain is intact. |
| **D5** | Governed CC-level tenant binding path for a single CC | (a) `schema-provisioner/onboard-connector` (over-broad); (b) `nightly-reconcile` after manual `tenant.contract_binding` insert; (c) raw DBCP for one row | **(b)** if `nightly-reconcile` provisions the fact table from an existing binding; **(c)** under DB Change Protocol if no service path exists; **(a)** rejected as too broad. |

## Gated Fast-Track Run — Slice 1.1 (2026-05-11)

Operator approved a fast-track attempt: complete realistic DSO end-to-end if all gates pass, halt immediately on any gate failure. **Result: 2 of 2 examined gates FAILED. Run halted before any authoring.** No contracts, mappings, bindings, or schemas touched.

### Gate 1a — `filter_json` null-equality support (canonical_mapping-level filter)

**Status: FAIL.**

- 6 `cc_field_mapping` rows currently use `filter_json`. All 6 are **semantic annotations**, not runtime predicates:
  - `cc__receivable_hdr`: `{"semantic_target": "billed_revenue"}` × 2
  - `cc__xbrl_gaap_equity`: `{"note": "Revenue - COGS - OpEx", "account_group": "ebit_components"}` × 2 (EBIT / EBITDA), plus 2 more market-data annotations
- bc-core code scan: `cc-onboarding.service.ts` writes `filterJson` (lines 487, 501, 636, 650, 716) and rejects it on compute mappings (line 744). **`canonical-resolution.service.ts` does not read `filterJson` anywhere.** `metric.service.ts` does not read it either.
- Conclusion: `filter_json` cannot filter "open-only" records at canonical-resolution runtime today. Design Decision D3a is invalidated.

### Gate 1b — CustomerOpenItemSet source-chain governance

**Status: SKIPPED** (downstream of Gate 1a failure; would not unblock the slice on its own).

### Gate 1c — narrow apex CC binding/provisioning path

**Status: SKIPPED** (downstream of Gate 1a failure).

### Gate 1d — metric grammar / engine support for DSO v2 requirements

**Status: FAIL.**

- DSO v2.0.0 would need `input_selection` declarations (per DEC-c012c0 grammar v1.1: `over_period`, `over_trailing_window`, and re-admitted `at_period_end` once DEC-1db1c7 lands).
- bc-core engine code scan (`metric-evaluation-engine.service.ts` + recursive search across `src/`): **zero occurrences of `at_period_end`, `over_trailing_window`, `over_period`, or `input_selection` strings in the runtime engine.** Only hit is in `admin-inspection/temporality-compatibility.ts` for an unrelated temporality-kind code (`stock_at_period_end`).
- Conclusion: **ADR-c012c0's Stage 2 implementation (meta-schema v1.1 file + engine version-gated path) has NOT landed in bc-core.** The grammar is on paper; the engine still operates under v1.0 semantics.

### Cascade implication — DEC-c012c0 is a runtime prerequisite, not just paper

Even if Gate 1a passed and we landed `cc__receivable_open_item` for apex, DSO v2.0.0 could not be authored against it. Authoring would require:

- Meta-schema v1.1 file at `bc-core/src/registry/meta-schemas/metric-v1.1.schema.json` (or equivalent) so MC version writes accept the new body keys.
- Engine code path (`metric.service.ts` + `metric-evaluation-engine.service.ts`) that reads `input_selection`, resolves anchors via `FiscalCalendarService.resolveByLabel` (per ADR-c012c0 §Layer-D dependency), filters per-variable CO sets, and emits the additive evidence shape.
- The author flow (`POST /api/onboarding/mc/...`) needs to validate against the new schema.

None of this code exists in `bc-core` today.

### Honest assessment

**Two independent architectural gates fail.** The fast-track approved scope (Slice 1 + DSO v2 authoring + eval) was based on a paper plan that assumed ADR-c012c0 + DEC-1db1c7 had landed end-to-end. They are both `proposed` ADRs that scope decisions; **neither has been implemented in bc-core**. The total_revenue arc (Slices 1–1h) realized through existing engine paths because total_revenue is a flow metric operating on grammar v1.0 — it never exercised the v1.1 grammar or the open-item semantics.

This is the architectural debt the planning document called out: realistic DSO requires **both** the grammar v1.1 engine implementation (ADR-c012c0 Stage 2) **AND** the open-item CC family (DEC-1db1c7 implementation slices). Both are docs-only today.

### What WOULD complete the arc (out of scope for this run)

| Prerequisite | Authority | Implementation gate |
|---|---|---|
| Grammar v1.1 meta-schema file | DEC-c012c0 §Stage-2 deliverables | `bc-core/src/registry/meta-schemas/metric-v1.1.schema.json` |
| Engine support for `input_selection.kind` | DEC-c012c0 | `metric-evaluation-engine.service.ts` extension |
| `FiscalCalendarService.resolveByLabel` | DEC-c012c0 Layer-D dependency | bc-core service extension |
| Open-item CC family pattern | DEC-1db1c7 (D401) | Slices 1.x of this MWR (with Gate 1a resolved — either canonical_mapping filter support OR new OC with reader-level filter OR engine-level partitioning) |
| DSO v2.0.0 MC authoring | post both above | New MC version under playbook §3 + §5 |

### Stop-condition acknowledgements per operator instruction

- ✗ `filter_json` cannot express open-only safely → **TRIGGERED Gate 1a stop.**
- — narrow binding/provisioning path → not checked (downstream of stop).
- — CustomerOpenItemSet data availability → 73 rows confirmed in Slice 1f probe; **NOT the blocker**.
- ✗ grammar/engine support for DSO v2 not implemented → **TRIGGERED Gate 1d stop.**
- — any SDG tuning / read-side compensation / fact-side computation / in-place MC mutation → none attempted.

### Recommendation

**Pause Slice 1 implementation. Author the cc__receivable_open_item architecturally as a SUBSET-CC-OF-existing-receivable_hdr-BO with canonical_mapping-level filter.** Sub-slice the work as follows:

- **Slice 1.0 (this session)** — design discovery + MWR (this record). DONE.
- **Slice 1.1 (next)** — verify canonical_mapping-level filter_json semantics. Read-only inspection of one existing cc_field_mapping that uses filter_json (we saw `filter_json` is a column on `cc_field_mapping`; need to find a row that uses it, confirm shape, confirm null-handling). If filter_json supports `{"AUGBL": {"is_null": true}}`-style predicates, D3a is approved. If not, fall back to D3b (new OC).
- **Slice 1.2** — preview-create the OC (`POST /api/onboarding/oc/preview`) to confirm DTO acceptance and Foundation Gate at the OC layer. No writes yet.
- **Slice 1.3** — preview-create the CC (`POST /api/onboarding/cc/preview`). Verify CC envelope shape matches the existing `cc__receivable_hdr` template.
- **Slice 1.4** — execute the OC create + CC create + canonical_mapping authoring in sequence. Single operator approval point.
- **Slice 1.5** — author cc_field_mapping rows (CFs that should resolve to the new CC). Includes `outstanding_receivables_amount` → `receivable_hdr_amount` (or `_functional_amount`) with filter for AUGBL IS NULL.
- **Slice 1.6** — bind to apex via D5's chosen path. DBCP gate if path (c) is needed.
- **Slice 1.7** — schema-provisioner reconcile to materialize `fact.co_receivable_open_item_v1_0_0`.
- **Slice 1.8** — execute reader; verify open-AR COs land; tenant-DB grain-overlap recheck.

Each sub-slice has its own approval gate and stop conditions. The cumulative arc completes DEC-1db1c7 Mechanism A for AR. DSO Phase-2 Slice 2 (DSO v2.0.0 authoring) follows after that.

## Non-decisions

- Did NOT author any OC, CC, canonical_mapping, cc_field_mapping, or tenant_binding.
- Did NOT execute any reader.
- Did NOT touch demo-selenite or sandbox1.
- Did NOT modify ADR-c012c0 or ADR-1db1c7.
- Did NOT write to any DB.
- Did NOT commit any file in any repo this session.
- Did NOT propose changes to the engine, SDG, or any code.

## Follow-ups

- **OPERATOR DECISION** on each of D1–D5 above. The recommended defaults are listed; operator approval (or override) is required before Slice 1.1 begins.
- **Read-only verification of `filter_json` semantics** — one query against `contract.cc_field_mapping WHERE filter_json IS NOT NULL` to confirm shape and supported predicates. Belongs in Slice 1.1.
- **Source-contract chain verification** — confirm which `sc__*__bsid*` variant the existing OC `oc__s4hana__bsid__receivable_hdr` binds to, to validate D4(c) "reuse without change". Belongs in Slice 1.1.
- **Tenant-binding path test** — try `nightly-reconcile` against a known existing CC binding to see whether it idempotently re-provisions, validating D5(b). Belongs in Slice 1.6 precheck.

(No `TSK-` UIDs filed this session; operator has visibility on each open decision.)
