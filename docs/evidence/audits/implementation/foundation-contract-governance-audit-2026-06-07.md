---
title: "Foundation Contract-Governance Audit — all active contract families (read-only)"
description: Read-only audit of the six contract families (Source, Admission, Observation, Canonical, Metric, Intervention) plus context surfaces (Canonical Mapping, Business Concept Registry, tenant Contract Binding) against the Foundation evaluation-boundary + contract-grammar discipline. Triggered by the legacy Metric Contract hand-typed-field-binding smell. Per family: Foundation role, live schema/lifecycle, authoring paths, validation gates, boundary violations, concrete evidence, classification. Ends in a summary matrix. Authorizes no code, schema, DB write, migration, fix, or panel.
status: draft
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: governance
focus: foundation-audit
---

# Foundation Contract-Governance Audit (read-only)

> **What this is.** A read-only audit of every active contract family against the Foundation (`the-evaluation-boundaries.md`, `the-contract-grammar.md`, `the-object-model.md`) and its governing ADRs (DEC-02f5a9, DEC-29c324, DEC-97bb94, DEC-d72560; D426/D428 where relevant). It was triggered by a confirmed smell: legacy Metric Contracts hand-type physical field bindings. It **authorizes nothing** — no code, schema, DB write, migration, fix, or panel. Findings + a matrix only; everything held.
>
> **Method.** Foundation docs + live `bc_platform_dev` schema/`contract_json` read by the auditor; authoring paths, validation gates, and tests traced by four read-only subagents (file:line evidence retained). Runtime objects (`progression.*`, `fact.*`) live in the tenant DB (`tbc_sandbox1_dev`) and were not queried here.

## The Foundation rubric being audited against

- **Four boundaries, fixed order** (Admission→Canonical→Metric→Action), each applying its governing contract family and producing exactly one progression object (`the-evaluation-boundaries.md` §Boundary inventory; Invariant II).
- **Contracts are grammar, not objects** (`the-object-model.md` §Contracts are grammar). They reference governed artifacts **by identity**.
- **Immutability on publish** — an `active` version is immutable; changes are new versions (`the-contract-grammar.md` §Versioning; Invariant III).
- **Semantic inputs, not column names** — Metric Contracts declare referenced Canonical Contracts/Business Concepts + formula; under **DEC-02f5a9** contract inputs reference **Business Concepts by identity**, not physical fields (`the-contract-grammar.md` §Metric Contract, §Vocabulary).
- **Reads do not trigger evaluation; no boundary-skipping; tenant binding cannot change platform meaning** (three-level governance: Master Shape / Platform Instance / Tenant Override).
- **Repair-location frame (CLAUDE.md):** A source/admission, B contract semantics, C mapping/binding, D evaluation engine, E storage, F read model.

## Headline verdict

The admission-facing families (**Source, Admission, Observation**) are **Foundation-aligned**: they legitimately carry physical source identifiers at the boundary where that is correct. The drift is concentrated **upstream of the metric smell, at the Canonical boundary**, and in two cross-cutting governance gaps:

1. **The Canonical Contract carries no field-level semantic identity** (Invariant I gap) — so meaning is never anchored where the Foundation says it must be. The legacy Metric Contract smell (hand-typed `fields_used`, AP fields bound to an AR invoice CC) is the **downstream symptom** of this, not the root.
2. **No store enforces contract-version immutability** — active contract bodies are mutable, and a shipped script rewrites **active** Canonical Contract bodies in place. The direct violation is of the **contract-grammar immutability-on-publish rule** (`the-contract-grammar.md` §Versioning: an `active` version's header and body may not be modified in place). *Contracts are grammar, not objects* (`the-object-model.md` §Contracts are grammar), so this is a contract-grammar violation — related to, but distinct from, Invariant III (which governs the six authoritative objects).

**Metric (legacy)** is a genuine Foundation violation but is **remediated-by-design** by MCF (which binds to Business Concepts and strips `co_bindings`). **Intervention** is unbuilt and carries a latent misroute bug.

## Cross-cutting findings (span multiple families)

| # | Finding | Evidence | Class | Severity |
|---|---|---|---|---|
| **X1** | **No DB-level immutability on contract version bodies.** No `BEFORE UPDATE`/immutability triggers on `source/admission/observation/canonical_contract_version`; immutability is application convention only (no service exposes a `contract_json` updater). A **shipped script mutates ACTIVE canonical bodies in place**: `scripts/d365-enrich-cc-posting-date.mjs:112,160-161` runs `UPDATE contract.canonical_contract_version SET contract_json=… WHERE governance_state_code='active'`. | DDL `02-contract.sql` (no triggers); script l.112,160-161 | **Foundation violation — contract-grammar immutability-on-publish** (grammar discipline; cf. Inv III for objects) | **High** |
| **X2** | **No field-level semantic identity at the Canonical boundary.** `canonical-v1.schema.json` `field_selection` is a bare string list; `semantic_rules` has no `minItems` (empty is valid); no field declares a Business-Concept binding or representation term. Meaning is name-only. | `meta-schemas/canonical-v1.schema.json:44-90`; `concept_registry` has 0 columns linking CC fields to concepts | **Foundation gap (Inv I) + needs ADR** | **High** |
| **X3** | **Meta-schema runtime authority is the DB row, not the repo file.** Validation loads `contract.contract_meta_schema` (`contract-validation.service.ts:89`); the `.schema.json` files only govern if seeded. File↔DB can drift; only a body-vs-schema checker exists, not file-vs-DB. | `contract-validation.service.ts:30,89-103` | Doc/ADR ambiguity + governance drift | Medium |
| **X4** | **Dead compatibility gate.** `findLatestReleasedVersion` filters `governance_state_code='released'` — a state the machine never sets (`draft/review/approved/active/superseded`). The compatibility + version-increment check never fires for any family. | `contract-version.repository.ts:175`; `contract.service.ts:41-47,349-375` | Live authoring risk (latent) | Medium |
| **X5** | **Degraded activation gate (fail-open).** The canonical/metric activation integrity gate reads physically-dropped tables (`cc_field_mapping`, `canonical_field`, `business_field` — D417/D418) → returns `null` → gate skipped. `IntegrityService` is `@deprecated` but still the live activation check. | `integrity.service.ts:220-261,1005-1009,1289-1311`; `contract.service.ts:464,526-541` | Live runtime risk (publication check that doesn't check) | High |
| **X6** | **Family-dispatch misroute + stale tooling.** `resolveFamily('intervention')→'metric'` (`contract-families.ts:36-38`): an Intervention Contract authored via the generic API is written to `contract.metric_contract`. Plus dead `scripts/create-ocs.mjs` (targets non-existent `/onboarding/oc/*`) and a partly-stale `contract.service.transitionState.spec.ts` exercising the retired CF-trust gate. | `contract-families.ts:36-38,262-286` | Latent correctness bug + historical debt | Medium |

## Per-family audit

### 1. Source Contract — ALIGNED
- **Foundation role.** Structural reference for the Admission boundary; declares one source table/endpoint's fields. Must NOT carry validation rules, runtime config, or lifecycle state (`the-contract-grammar.md` §Source Contract).
- **Live schema.** `contract.source_contract(_version)`; `contract_json` `{$contract,version,header,body}`; **30,368** versions. Lifecycle via governance state machine.
- **Authoring.** LIVE: generic `POST /contracts[/:id/versions]` (`contract.controller.ts:38,205,288` → `contract.service.ts`); bulk `POST /contracts/generate-source-chain` (`contract-generator.service.ts:74`); seed. No AI/panel write path (panel/mcf code has zero `ContractService` refs).
- **Gates.** AJV meta-schema `source-v1.schema.json` (body requires `table_code,label,source_system_version_id,module_code,fields[],primary_key[]`; `additionalProperties:false`). D284 veracity gate at identity creation (`contract.service.ts:86-100`). No SC-specific activation gate.
- **Boundary check.** Physical source field names (`field_code` e.g. `BUKRS`) — **legitimate (repair-location A)**. No cross-boundary leakage. Active-version mutation: not via service, but **no DB trigger** (X1).
- **Evidence.** `sc__ecc__tmw_tdslant` (TMW_TDSLANT, 5 fields); `sc__ecc__tobj_tpt` (TOBJ_TPT, 3 fields).
- **Class.** Clean (role) + cross-cutting X1/X3/X4. **Live risk: Low.**

### 2. Admission Contract — ALIGNED
- **Foundation role.** Governs the Admission boundary: required fields, identity, temporal rules, rejection vs warning. Must NOT declare canonical interpretation.
- **Live schema.** `contract.admission_contract(_version)`; **30,367** versions.
- **Authoring.** Same generic path + the same `generate-source-chain` bulk builder (AC half via `buildAdmissionEnvelope`, `contract-envelope.builder.ts:440-479`, with a hardcoded `GLOBAL_DQC_RULES` set). No AI/panel write.
- **Gates.** `admission-v1.schema.json` (body requires `source_contract_version_id` (uuid → SC), `field_rules[]`, `outcome_thresholds`, `validation_policy`, …; rule `category/severity/action` enums). No AC-specific activation gate.
- **Boundary check.** References `field_code`/`ref_table` (legitimate at admission). Links up to SC by uuid (correct lineage). No metric/canonical leakage. X1 applies.
- **Evidence.** `ac__ecc__rs3rdfldt`, `ac__s4hana__ahs_s_data_xbrl` (both carry GL-001 not_null completeness rule).
- **Class.** Clean (role) + X1/X4. **Live risk: Low.**

### 3. Observation Contract — ALIGNED (the source→business bridge)
- **Foundation role.** Field selection from Source Contract to business vocabulary; defines the Source Object shape. Under DEC-02f5a9 each `observation_field_map` entry binds one source field to **one Business Concept**. Must NOT declare canonical evaluation logic.
- **Live schema.** `contract.observation_contract(_version)` + `observation_field_map`; **154** versions.
- **Authoring.** LIVE: generic `/contracts` with `category:'observation'` (the only live OC write path). `buildObservationEnvelope` exists but is **not wired** to a live service; **no bulk OC generator**. LEGACY/dead: `scripts/create-ocs.mjs` (targets non-existent `/onboarding/oc/{create,preview}`). OAGIS path is read-only.
- **Gates.** `observation-v1.schema.json` (7 required body keys; each `source_reference` must cite both SC + AC version uuids; `field_mappings[]` require `business_field_code` + `source_table` + `source_field` + `transform` enum). **OC-specific activation gate** re-checks the 7 keys (`contract.service.ts:543-558`).
- **Boundary check.** Carries physical source fields **and** `business_field_code` — the SO→business-field translation. Per the Reader-exec-plan model this is the **correct** place for that bridge. Smell: `business_field_code` is a **free string**, not bound to the BCF registry by identity (DEC-02f5a9 intent not yet enforced); provider slug often `unknown`. Two status fields (`status_code` on parent vs version `governance_state_code`) can diverge.
- **Evidence.** `oc__unknown__commercial_invoice_hdr` → `{source_field:KUNRG, source_table:TYPE_SD_S_MAP, business_field_code:commercial_invoice_hdr_bill_to_party_identifier}`; `oc__unknown__currency_exchange_rate` → `{GDATU → currency_exchange_rate_effective_from}`.
- **Class.** Aligned (role) + historical/tooling debt + DEC-02f5a9-pending identity binding. **Live risk: Low–Medium.**

### 4. Canonical Contract — PARTIAL / GAP (root of the metric smell)
- **Foundation role.** Governs the Canonical boundary; references an Entity, declares grain, field selection, resolution rules, resolved schema, **semantic rules**, temporal gate; binds Business Concepts directly (DEC-02f5a9). Carries the business meaning of canonical state (`the-object-model.md` §Canonical Object).
- **Live schema.** `contract.canonical_contract(_version)`; **83** versions, **0 active** (legacy corpus archived Apr–May 2026). `canonical_mapping(_version)` is the superseded binding layer.
- **Authoring.** LIVE: generic `/contracts` (`category:'canonical'`); `canonical_mapping` via `mapping-binding.service.ts` (**no meta-schema validation, no governance state machine** — stores `mapping_json` raw). LEGACY/out-of-band: `scripts/d365-enrich-cc-posting-date.mjs` rewrites active bodies; `migrate-canonical-contract-json.js`, `d225-generate-canonical-chain.js`, 21 seed JSONs. No AI/panel write path (no governed proposal flow for CCs).
- **Gates.** `canonical-v1.schema.json` (8 required body keys; `additionalProperties:false`). Activation integrity gate **degraded/fail-open** (X5). Compatibility gate **dead** (X4). `semantic_rules` enforced only at CO-production time, partially, with a camelCase(engine)/snake_case(schema) mismatch that silently no-ops unknown types (`canonical-evaluation-engine.service.ts:222-237`).
- **Boundary violations.** **(a)** No field-level semantic identity (X2) — `field_selection` is names; `semantic_rules` optional/empty; no concept binding. **(b)** Active versions mutated in place (X1) — DB has no trigger; D365 script does it. **(c)** `canonical_mapping` writes bypass all validation.
- **Evidence.** `cc__invoice_hdr` body: `field_selection` = flat name list incl. `invoice_hdr_total_amount`, `invoice_hdr_extended_amount`, `invoice_hdr_identifier`; `semantic_rules: []`; `resolution_rules` = `sum`/`latest`/`assert_equal` per field (collapse discipline, not meaning). `posting_date_field = invoice_hdr_document_date_time`. Several amount fields, none flagged as "revenue" — ambiguity by construction.
- **Class.** **Foundation gap (Inv I) + Foundation violation (contract-grammar immutability-on-publish, via X1) + requires ADR/DBCP.** **Live risk: High** (this boundary should anchor meaning for the whole metric chain and does not).

### 5. Metric Contract — VIOLATION (legacy) / ALIGNED (MCF)
- **Foundation role.** Governs the Metric boundary; declares referenced Canonical Contracts + formula + grain + temporal gate + thresholds; under DEC-02f5a9 inputs reference **Business Concepts**. Must NOT reference raw Source Objects, produce values by read-time query, or be edited to change historical snapshots.
- **Live schema.** **Legacy** `contract.metric_contract(_version)`: **1022** versions / **780** parents / **2 active** (778 archived); `contract_json.body.co_bindings[{canonical_contract, fields_used[]}]` + `body.formula`. **New** `mcf.metric_contract*` + `mcf.metric_variable_binding` (binds `bound_business_concept_id`).
- **Authoring.** Legacy door **LIVE + validate-only**: generic `POST /contracts/:id/versions` (`contract.service.ts:311-397`) + full-registry seed (`generate-metric-contracts.ts:83-89`). `POST /metric-catalog/definitions` is live but writes `metric.metric_definition`, not the contract. MCF (M12.5) writes `mcf.*` only and **never** `contract.metric_contract` (HA-1).
- **Gates.** `metric-v1.schema.json` keeps inputs at the **canonical** layer (no raw source columns — boundary order OK) **but** `co_bindings[].canonical_contract` and `fields_used` are **free strings with no semantic grounding and no relatedness validation** (`metric-v1.schema.json:55-63`). Activation integrity gate decides on **name-existence + chain completeness only** (`integrity.service.ts:936-992`), never field↔CC meaning; the one trust-adjacent gate is **retired** (D417/D418, `contract.service.ts:68-72`). **No gate rejects an AP field bound to an AR invoice CC.**
- **Boundary violations.** Hand-typed physical canonical field names where **semantic identity is required** ("semantic inputs, not column names"). Does **not** skip the canonical boundary (binds to CC names), so the violation is *semantic grounding*, not boundary order.
- **Evidence (≥3 known-bad, live).** `mc__overdue_payables_pct` → `cc__invoice_hdr` / `[total_overdue_accounts_payable_balance, total_accounts_payable_balance]`; `mc__trade_vs_non_trade_payables_ratio` → `cc__invoice_hdr` / `[total_trade_payables, total_non_trade_payables]`; `mc__ap_turnover_ratio` → `cc__invoice_hdr` / `[total_purchases, average_accounts_payable_balance]`; `mc__vendor_credit_utilization` → `cc__invoice_hdr` / `[current_accounts_payable_balance, total_available_vendor_credit_limit]`. All bind **accounts-payable/vendor** fields to the **AR invoice-header** CC. (Contrast clean MCF: ARPI binds 3 BCF concepts via `mcf.metric_variable_binding`.) Anti-pattern is even baked into `contract.service.transitionState.spec.ts:98-107` as the happy-path fixture.
- **Class.** Legacy: **Foundation violation + live authoring risk (generic door open) + historical debt (existing wrong snapshots in `tbc_sandbox1_dev.fact.*`)**. MCF: **clean/aligned** (forward path), pending the store/visibility decision (separate materialization-boundary memo). **Live risk: High on the legacy door.**

### 6. Intervention Contract — UNBUILT (+ latent misroute bug)
- **Foundation role.** Governs the Action boundary; declares activation mode, trigger conditions against Metric Snapshots, assignee pool, closure window, outcome model. Must NOT define metric logic or permit open-ended non-closure.
- **Live schema.** `contract.intervention_contract(_version)` tables + `intervention-v1.schema.json` exist; **0 rows / 0 versions**.
- **Authoring/gates.** **No** intervention onboarding service/controller. Generic API misroutes `'intervention'→'metric'` (X6) → an IC would be written to `contract.metric_contract`. Activation is an explicit **stub** (`contract-activation.service.ts:221-239`). The seed instance (`exr-intervention.json`) **fails its own meta-schema** (body keys mismatch) → orphaned. The Action-boundary runtime (`action.controller.ts`) exists but is **not contract-governed** (zero IC references).
- **Boundary check.** N/A (no instances). The runtime Action path producing Action Objects without an Intervention Contract is itself a boundary-governance gap to flag.
- **Class.** **Unbuilt + latent correctness bug (misroute).** **Live risk: Low** (nothing uses it); fix the dispatch before any IC authoring.

### Context surfaces
- **Canonical Mapping** (superseded, DEC-02f5a9): live but governance-thin (`mapping-binding.service` does no validation). Historical debt; no new CMs should be authored. **Low.**
- **Business Concept Registry** (`concept_registry.*`, the DEC-02f5a9 replacement): exists and is the **intended semantic-identity authority**, but is **not yet referenced by Canonical or Metric contract authoring** — wiring it is the fix for X2. Aligned-by-design, unwired.
- **Tenant Contract Binding**: three-level governance (tenant cannot change platform meaning). Not deeply audited here; no violation observed; flag for a dedicated pass if tenant overrides grow.

## Summary matrix

| Family | Foundation alignment | Live risk | Worst issue | Recommended next action (no fix authorized) |
|---|---|---|---|---|
| Source | Aligned | Low | No DB immutability on active body (X1) | Include SC version table in an immutability-trigger DBCP |
| Admission | Aligned | Low | X1 + dead compat gate (X4) | Same DBCP; fix `released`-state compat check |
| Observation | Aligned (bridge) | Low–Med | `business_field_code` not registry-bound by identity; dead tooling | Enforce concept-identity when OC adopts DEC-02f5a9; retire `create-ocs.mjs` |
| Canonical | **Partial / gap** | **High** | **No field-level semantic identity (X2) + active-body mutation (X1)** | **ADR: canonical field semantic identity (DEC-02f5a9 concept binding); DBCP: active-version immutability triggers** |
| Metric (legacy) | **Violation** | **High** (legacy door) | Semantically-ungrounded `fields_used` accepted at every gate | ADR to retire/guard the legacy `contract.metric_contract` authoring door; real fix is upstream (X2); MCF is forward path |
| Metric (MCF) | Aligned | n/a (not runtime store) | Not yet wired to runtime | Resolve materialization boundary (separate memo `mcf-materialization-boundary-options-2026-06-07.md`) |
| Intervention | Unbuilt | Low | Family-dispatch misroute → writes to metric table (X6) | Fix `resolveFamily` + `families` table before any IC authoring; document unbuilt status |
| Canonical Mapping | Superseded | Low | No validation on writes | No new CMs; retire post-cutover |
| BCF Registry | Aligned (unwired) | n/a | Not referenced by CC/MC authoring | Wire as the semantic-identity authority (the canonical-binding work) |
| Tenant Binding | Not audited | — | — | Dedicated pass if needed |

## Classification roll-up

- **Foundation violations:** X1 (contract-grammar immutability-on-publish — active contract-body mutation, shipped; grammar-level, cf. Inv III for objects); Metric-legacy semantic-input discipline absent.
- **Foundation gaps requiring ADR:** X2 (Canonical field-level semantic identity).
- **Live runtime risk:** X5 (fail-open activation gate).
- **Live authoring risk:** legacy metric generic door (validate-only); X4 (dead compat).
- **Latent correctness bug:** X6 (intervention misroute).
- **Historical debt only:** archived legacy corpora (canonical, metric), Canonical Mapping, stale tests/tooling.
- **Doc/ADR ambiguity:** X3 (meta-schema file↔DB authority).
- **Clean:** Source, Admission, Observation (roles); MCF metric authoring; BCF registry (design).

## Recommended next actions — operator-locked sequence (2026-06-07; none authorized here)

> **Net operator directive (2026-06-07): PAUSE MCF→`contract.*` materialization (D428) until steps 1–4 land. Do not panic-rewrite; harden contract governance first, then resume.** The contract-governance substrate is not yet strong enough to trust new Metric runtime materialization. The held materialization options memo (`mcf-materialization-boundary-options-2026-06-07.md`) and ARPI synthesis proof (`mcf-arpi-contract-json-synthesis-proof-2026-06-07.md`) remain valid but are **gated** behind this sequence; their canonical-binding finding is an **input to step 2**, not wasted work.

1. **Fix contract-version immutability first** (X1) — DBCP adding `BEFORE UPDATE` immutability guards on active `*_contract_version` bodies; quarantine/retire the `d365-enrich-cc-posting-date`-style in-place active mutation. *Highest — a shipped tool currently violates contract-grammar immutability-on-publish.*
2. **Decide Canonical field-level semantic identity** (X2) — ADR: a Canonical Contract field declares its governed meaning (BCF Business-Concept / characteristic identity); MCF **consumes** this, never invents field mappings. The single upstream fix that makes Canonical correct and Metric resolvable.
3. **Close or guard the legacy Metric Contract authoring path** — until #2 exists, no new legacy-style envelopes carrying free `fields_used` (the generic `POST /contracts` metric door + full-registry seed).
4. **Fix activation/publication gates that fail open** (X5, X4) — especially the integrity gate that reads dropped legacy mapping tables and treats `null` as pass.
5. **Only after 1–4: return to D428 materialization.** Otherwise MCF publishes into `contract.*` before `contract.*` is Foundation-clean.

> **Status update (2026-06-09) — Step 5 ARPI precondition MET.** The editorial-rebind arc is complete: ARPI's active Metric Contract was rebound from its **superseded** BCF concept anchors to their **active** successors (`1a2ac2f2` amount / `51482979` identifier / `61e19048` date) and is now a single clean active MCV **`b1933c30`** (predecessor `8c088f55` superseded). The D430/D431 resolvers it relied on are active. This closes exactly the `UNRESOLVED@C` gap the held ARPI synthesis proof named — so **Step 5 is now unblocked for ARPI specifically** (the first metric it unblocks), **without** lifting the D428 §9 guardrail. The recommended narrow first slice is a **read-only** re-proof of ARPI synthesis against `b1933c30` (go/no-go) before any writer is built. See `mcf-arpi-editorial-rebind-arc-closeout-2026-06-09.md` (change record **CHG-3daea8**); tasks **TSK-a8bedb** (Slice 0, read-only) → **TSK-0ba31e** (ARPI-only writer DBCP, held). *This note records only the ARPI binding-refresh precondition for Step 5; the applied/merged status of steps 1–4 is not re-verified here.*

*Parallel / non-blocking:* fix the Intervention family misroute (X6) before any Action-boundary work (not on the AR critical path).

## Scope guard

Read-only audit. No code, schema, DB write, migration, fix, PR, or panel. Runtime objects in `tbc_sandbox1_dev` not queried. Live row counts/active-body checks for some families noted as not-verified where a DB read was out of scope. This memo recommends; it does not change anything.
