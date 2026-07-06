---
title: "D429 Step-5 — ARPI MCF Materialization Writer (SERVICES-ONLY) — DBCP (held)"
description: Held Database/Code Change Proposal for the D429 Step-5 writer that synthesizes a legacy runtime contract.metric_contract[_version] row (denormalized contract_json envelope) from the normalized MCF shape, ARPI-only, SERVICES-ONLY. Resolves the five open writer questions (metric_definition_id FK, body.unit, fiscal_period grain, eligibility artifacts, formula AST→text) with file:line-grounded recommendations; isolates the required DDL as a separate sub-DBCP; gates everything behind D428 §9. Design only — no implementation, no DB writes, no materialization.
status: draft
date: 2026-06-09
project: bc-core
domain: contracts
subdomain: metric-store
focus: materialization-boundary
governs: DEC-61f7c8 (D428 §9) · DEC-c3e57f (D422 MCF) · DEC-a6258b (D430) · DEC-4a17e0 (D431) · DEC-1efa47/DEC-d7e7a0/DEC-a8e8fc (D363–D365 fiscal calendar)
depends_on: mcf-arpi-step5-slice0-synthesis-reproof-2026-06-09.md (GO), mcf-arpi-contract-json-synthesis-proof-2026-06-07.md, mcf-materialization-boundary-options-2026-06-07.md
task: TSK-0ba31e
---

# D429 Step-5 — ARPI MCF Materialization Writer (SERVICES-ONLY) — DBCP

> **Held. Design only.** No implementation, no DB write, no materialization, no `synthesizeContractJson` execution. This DBCP **is** the D428 §9 "implementing DBCP" gate for ARPI; it also names a separate isolated DDL sub-DBCP it depends on (§8). Nothing here lifts D428 §9 — it proposes the path to do so under explicit approval. The writer may synthesize and write `contract_json` **only after** all §7 gates pass and §8 is applied.

## 0. D428 §9 guardrail (verbatim — the gate over this work)

> **9. GUARDRAIL: no MCF materialization into contract.* and no legacy wipe until this amendment AND its implementing DBCP(s) are approved.** — `ADR-61f7c8.md:32` (DEC-61f7c8 / D428, decided 2026-06-07).

Materializing ARPI into `contract.metric_contract*` is exactly "MCF materialization into contract.*". This DBCP + its DDL sub-DBCP (§8) are the implementing DBCP(s) §9 requires. No legacy *wipe* is in scope (that is a separate later DBCP per D428 §5).

## 1. GO input (from Slice 0 — `…slice0-synthesis-reproof-2026-06-09.md`)

Active/current MCV **`b1933c30`** · grain entity **`e3963e45`** (Customer Invoice) · active CC-v2 **`cc__customer_invoice_arpi_slice`** · active OC-v2 **`oc__customer_invoice_arpi_slice_type_sd_s_map`**. Resolved (D430 canonical + D431 source):

| Role | Concept | Canonical field | Source field |
|---|---|---|---|
| numerator_source | `1a2ac2f2` | `amount` | NETWR |
| denominator_key | `51482979` | `document_number` | VBELN |
| temporal_anchor | `61e19048` | `document_date` | FKDAT |

The writer locates its source by **UID `b1933c30`** (legacy `contract.metric_contract` has **no** ARPI row — 780 rows / 2 active, none ARPI; the writer **creates** a new legacy row).

## 2. Scope — two bars, hard split

| In scope (writer DOES) | Out of scope (explicitly deferred) |
|---|---|
| Create `contract.metric_contract` (parent) + `contract.metric_contract_version` (active) with the synthesized denormalized `contract_json` | **Bar 2 runtime tenant evaluation** — no `progression.*` / `fact.ms_*` / `metric_snapshot` writes |
| Reach **platform-ready**: active MCV + `ChainStatusService` computes `chain_verdict='complete'` | `tenant.contract_binding` creation (tenant onboarding — later runtime step) |
| ARPI **only**, one metric, located by UID | Generalization to other metrics / a coverage wave |
| SERVICES-ONLY (no raw SQL writes) | Legacy wipe (D428 §5, separate DBCP) |

"Platform-ready" = discoverable (`listActiveMcs`) **and** `chain_verdict='complete'`. Producing tenant facts is a distinct, separately-approved runtime step.

## 3. SERVICES-ONLY writer composition (no new governed service needed)

Per the grounding, the legacy metric write path already exists as services; the writer **composes** them (never raw-INSERTs):

1. **Parent** — `ContractMetricsRepository.createMinimalMetricContract(...)` (`contract-metrics.repository.ts:129-167`). **Minimal extension required**: it currently hard-requires `metricDefinitionId`; under decision Q1(b) it must accept a null/absent definition. This extension is the SERVICES-ONLY-compliant change (extend the service, never bypass it).
2. **Version** — `ContractVersionRepository.createVersion({contractId, version:'1.0.0', contractJson:<synthesized>, governanceState, maintenanceApproval}, 'metric')` (`contract-version.repository.ts:16-50`). Accepts an arbitrary envelope + state; **no new SQL, no new service**.
3. **Activation** — `ContractService.activateVersion` → `transitionState` (`contract.service.ts:489-679`), which **synchronously fires `ChainStatusService.refreshChainStatusForVersion` before the MLS-14 gate** (`:546-555`) and `refreshChainStatus` async post-activation.
4. **D432 guard escape** — both create choke points call `assertLegacyMetricAuthoringAllowed` (`legacy-metric-authoring.guard.ts:47-72`), which requires env `BCCORE_ALLOW_LEGACY_METRIC_AUTHORING=1` **and** a `maintenanceApproval` rationale ≥12 chars (CREATE-only, metric-only). The guard docstring names exactly "the future MCF → contract.metric_contract materialization writer" as the authorized caller. The writer threads a rationale (e.g. `"D428 MCF materialization writer — ARPI b1933c30"`) and the operator sets the env flag at execution.

The writer is therefore a thin orchestrator (a new `Mcf...MaterializationWriterService` composing the above) + one small `createMinimalMetricContract` extension. It reads the MCF normalized shape (`mcf.metric_contract[_version]` + `metric_variable_binding`), the D430/D431 resolvers, synthesizes the envelope (§5), and writes via 1–3 under the §4/§6/§7 gates.

## 4. Resolved writer decisions

### Q1 — `metric_definition_id` NOT NULL FK → **(b) drop FK + make nullable** (isolated DDL sub-DBCP, §8)
`fk_metric_contract__metric_definition` (NOT NULL, FK→`metric.metric_definition`; `11-deferred-fks.sql:20-22`; `02-contract.sql:239`). The runtime **evaluate** path never dereferences it — it is a passthrough projection in `metric-catalog-reader.repository.ts:153` and is **dropped** from `ChainStatusService`'s projection (`chain-status.service.ts:864-871`); `metric-readiness.service.ts:299-319` **already null-guards** (orphan banner, not a crash). Minting a fake `metric.metric_definition` stub is rejected: it would require `discipline_code` (NOT NULL, composite FK to `metric_discipline`) + `function_code` + a unique name tuple, and `MetricDefinitionRepository.create` doesn't even accept `disciplineCode` — i.e. a stub re-entangles legacy *and* needs its own code change (worse than (b)). MCF provenance rides in `contract_json.header` now; promote to a typed `mcf_*` provenance column (option (c)) only if materialization generalizes past ARPI. **Residual:** an MCF MC with NULL definition appears in `getOrphanContracts()` (cosmetic admin banner); the D068 partial unique index `uq_metric_contract__one_active_per_definition (metric_definition_id) WHERE archived_at IS NULL` stays (NULLs are distinct in a unique index), at the cost of the one-active-per-definition guarantee for NULL-definition MCs (acceptable for an ARPI proof).

### Q2 — `body.unit` → **fixed `"currency"`** (display-only; cannot change the computed value)
`unit` is in `metric-v1.schema.json` `body.required` (`:15,:80-84`) so it cannot be omitted, but the engine **never reads it** (0 refs in `metric-evaluation-engine.service.ts` + `normalizeEnvelope`); it is label/display metadata. The rebind refreshed the numerator unit `USD→null`, so it is not derivable from the snapshot. Emit the corpus token **`"currency"`**. **Residual:** only a *future* unit-aware fact projector (flagged-but-unimplemented, `schema-provisioner.repository.ts:375`) could care — use a real corpus token to avoid surprising it. No computation risk.

### Q3 — grain / fiscal_period → **grain `field_code = "fiscal_period"` (NOT `document_date`)**; verify CC stamping
**Correction to the Slice-0 envelope sketch.** The engine GROUP-BYs `payload['fiscal_period']` — a value **stamped at canonical resolution** by `enrichFiscalPeriod` (`canonical-resolution.service.ts:1070-1105`), which reads the **CC's** `body.posting_date_field`, resolves it via `FiscalCalendarService.resolve` (`fiscal-calendar.service.ts:76-98`), and writes `payload.fiscal_period` **before** the CO is persisted. 100% of the live corpus uses `{key:'fiscal_period', source:'business_field', field_code:'fiscal_period'}`. So the writer emits:
```json
"grain": [ { "key": "fiscal_period", "source": "business_field", "field_code": "fiscal_period" } ]
"temporal_gate": { "field_code": "fiscal_period", "required_periods": 1, "completeness_threshold": 80 }
```
`document_date` appears in **neither** — it is the **CC's `posting_date_field`** (upstream). **Never** emit `source:'evaluation_period'` (`MetricService` never sets `envelope.evaluationPeriod`; it fails loudly — `metric.service.ts:126-133`).
**Load-bearing precondition (writer cannot compensate — Foundation A/C):** ARPI's grain only works if **`cc__customer_invoice_arpi_slice` declares `body.posting_date_field` = the document_date business field** AND the target tenant has a seeded `master.fiscal_period` + `organization.fiscal_calendar_config` (D364/D365). If `posting_date_field` is absent, `fiscal_period` is never stamped and the engine silently collapses to one `_null_` group (wrong grain, not a hard error). **This is a §6 verify-precondition, not a writer responsibility.** `completeness_threshold` is `0–100` in the legacy schema (`metric-v1.schema.json:68-79`) — use `80`.

### Q4 — eligibility artifacts → writer reaches `chain_verdict='complete'` via activation; tenant binding deferred
**Discovery** (`listActiveMcs`, `metric-catalog-reader.repository.ts:149-176`) needs only `archived_at IS NULL` + an `active` MCV. **Readiness/evaluable** needs `chain_verdict='complete'` AND `audit_status_code != 'fail'` (`metric-readiness.service.ts:184-186`; `audit_status_code` lives on the parent, default `'pending'` = non-failed — leave default). `chain_status` is **recomputed by `ChainStatusService` (D305 SSOT, sole writer), not hand-writable**, and is **auto-invoked on activation** (`contract.service.ts:546-555`). Therefore: the writer activating via `ContractService.activateVersion` produces `chain_status` for free **iff the synthesized `co_bindings[].canonical_contract` + `fields_used` resolve to active CCs** — else the verdict is `unlinked/partial` and the **MLS-14 gate blocks activation with `chain_not_complete`** (`contract.service.ts:565-580`). This is desirable: the platform's own gate is the correctness backstop, so the writer's envelope is **not cosmetic**. **`tenant.contract_binding`** (active, `contract_family='metric'`) + `fact.ms_*` are the **deferred** Bar-2 step (out of scope).

### Q5 — formula AST→text + var_code mapping → **`O1 = SUM(I1) / COUNT_DISTINCT(I2)`**, deterministic
Engine grammar (`metric-evaluation-engine.service.ts:490-759`): `AGG_FUNCTIONS={SUM,COUNT,COUNT_DISTINCT,AVG,MIN,MAX}`, operators `+ - * /`, output on the LHS of `=`. The real binding is **`variables[].field_code`** (var_code is only the formula-text token). Deterministic mapping rule the writer MUST use: output→`O1`; inputs→`I1..In` assigned in **`variable_role_code ASC`** order (the same sort the MCF canonicalizer uses — `formula-canonicalization.service.ts:714-727`), each `Ik.field_code` = that binding's resolved canonical field. For ARPI:
```json
"formula": { "text": "O1 = SUM(I1) / COUNT_DISTINCT(I2)" },
"variables": [
  { "var_code": "I1", "role": "input",  "field_code": "amount" },
  { "var_code": "I2", "role": "input",  "field_code": "document_number" },
  { "var_code": "O1", "role": "output", "field_code": "arpi" }
]
```
Lossless 1:1; division-by-zero is guarded (honest rejection, not NaN — Invariant VI). **Residual (verification, not defect):** `COUNT_DISTINCT` has **0 rows in the live `contract.*` corpus** — ARPI is the first end-to-end COUNT_DISTINCT evaluation; the code path is unit-tested but never E2E in `contract.*`. The §10 test plan requires a one-MC E2E proof before any generalization. Output `field_code='arpi'` (avoid reusing an input field_code).

## 5. Synthesized `contract_json` (writer target — corrected)

```jsonc
{
  "$contract": "barecount/metric/v1", "version": "1.0.0",
  "header": {
    "kind": "metric", "category": "metric",
    "name": "average_revenue_per_invoice", "display_name": "Average Revenue per Invoice",
    "governance": { "state": "active" }, "tenant_scope": { "scope": "global" },
    "contract_id": "<minted>", "provenance": { "mcf_metric_contract_version_uid": "b1933c30-…", "source": "mcf-step5-writer" }  // Q1: provenance in header until option (c)
  },
  "body": {
    "unit": "currency",                                   // Q2
    "direction_code": "higher_is_better",                 // default
    "formula": { "text": "O1 = SUM(I1) / COUNT_DISTINCT(I2)" },  // Q5
    "variables": [
      { "var_code": "I1", "role": "input",  "field_code": "amount" },
      { "var_code": "I2", "role": "input",  "field_code": "document_number" },
      { "var_code": "O1", "role": "output", "field_code": "arpi" }
    ],
    "grain": [ { "key": "fiscal_period", "source": "business_field", "field_code": "fiscal_period" } ],  // Q3 — NOT document_date
    "co_bindings": [ { "role": "primary", "canonical_contract": "cc__customer_invoice_arpi_slice", "fields_used": ["amount", "document_number"] } ],  // Q4 — must resolve to active CC
    "temporal_gate": { "field_code": "fiscal_period", "required_periods": 1, "completeness_threshold": 80 }  // Q3
  }
}
```
(`fields_used` carries the two formula-operand fields; `document_date` is the CC's posting_date_field, not an MC field.)

## 6. Preconditions to VERIFY before the writer synthesizes (read-only gates)

1. **Slice-0 GO still holds** — re-run `_step5-slice0-arpi-synthesis-reproof.mjs`; all 3 bindings resolve on grain `e3963e45` to the single active `cc__customer_invoice_arpi_slice`; all observable.
2. **CC declares `posting_date_field`** — `cc__customer_invoice_arpi_slice.body.posting_date_field` resolves to the document_date business field (Q3 dependency). If absent → **STOP**; this is a CC authoring gap (separate, upstream).
3. **Fiscal calendar seeded** for the intended evaluation tenant (`master.fiscal_period` + `organization.fiscal_calendar_config`, D364/D365). If absent → grain collapses; **STOP** (verify before any eventual evaluation).
4. **co_bindings resolve to an active CC** (so activation's chain compute reaches `complete`) — confirm `cc__customer_invoice_arpi_slice` active and declares `amount` + `document_number`.
5. **§8 DDL sub-DBCP applied** (metric_definition_id nullable) — else `createMinimalMetricContract` cannot insert without a definition.
6. **No existing active ARPI legacy MC** — idempotency: confirm `contract.metric_contract` has no active ARPI row before create.

## 7. Gate sequence (writer writes `contract_json` only after ALL pass)

`§6 preconditions (1–6)` → `meta-schema validation` (the synthesized envelope validates against `metric-v1.schema.json` via `ContractService.createVersion`) → `D432 escape present` (env flag + ≥12-char rationale) → `create parent (NULL definition)` → `create version (draft)` → `activateVersion` → `ChainStatusService` computes → **`chain_verdict='complete'` AND MLS-14 gate passes** (else activation refuses `chain_not_complete` — fail-safe, no partial state) → platform-ready. Any gate failure halts with an explicit error; no compensation.

## 8. Required isolated DDL sub-DBCP (separate approval — the D428 §9 DDL)

**`d429-step5-metric-definition-id-nullable-dbcp-2026-06-09.md` (authored 2026-06-09, TSK-f06131 — held).** Scope = the only DDL this track needs. **Refined** from the original drop-FK phrasing to the minimal, safer form — **DROP NOT NULL only, KEEP the FK** (PostgreSQL exempts NULL from FK enforcement: legacy metrics retain referential integrity, MCF metrics carry NULL):
```sql
ALTER TABLE contract.metric_contract ALTER COLUMN metric_definition_id DROP NOT NULL;
```
+ Drizzle edit (`src/database/schema/contract/metric-contract.ts:25-27` — remove `.notNull()`, keep `.references()`) + revert script (`SET NOT NULL`; valid only while no NULL rows exist) + **golden snapshot before apply** (Database Change Protocol + D428 §9). Both indexes (incl. the D068 partial unique) are unaffected; 0 NULL rows today / 780 total (confirmed). **Schema-drift note folded into the sub-DBCP:** live `contract.metric_contract.category_code` is NOT NULL default `'metric'` but absent from `02-contract.sql`/Drizzle (default covers omitted inserts). **This sub-DBCP is approved + applied BEFORE the writer code executes.**

## 9. Stop conditions

- CC has no `posting_date_field`, or fiscal calendar not seeded → **STOP** (upstream CC/source gap; do not embed `document_date` in the MC grain as a workaround — that is lower-layer compensation, forbidden).
- `co_bindings` do not resolve to an active CC → activation will (correctly) refuse `chain_not_complete`; **STOP** and fix the binding, do not force-activate.
- §8 DDL not approved/applied → **STOP** (do not mint a fake `metric_definition` stub to satisfy the FK — explicitly rejected, Q1).
- Any attempt to write `fact.ms_*` / `progression.*` / `metric_snapshot` or create a `tenant.contract_binding` → out of scope; **STOP**.
- More than one metric in a run → out of scope (ARPI-only); **STOP**.

## 10. Test plan

- **Unit (writer service):** AST→text translation (exact `O1 = SUM(I1) / COUNT_DISTINCT(I2)`); var_code assignment by `variable_role_code ASC`; envelope assembly matches §5; refuses when a binding is unresolved/superseded; refuses when grain would be `document_date`; passes the D432 rationale through.
- **Unit (createMinimalMetricContract extension):** accepts null `metricDefinitionId`; still enforces the D432 guard.
- **Integration (no commit / tx-rollback or test-env):** synthesized envelope passes `metric-v1` meta-schema validation via `ContractService.createVersion`; activation drives `ChainStatusService` to `chain_verdict='complete'` for ARPI; MLS-14 gate passes. Negative: a deliberately-broken `co_bindings` yields `chain_not_complete` and activation refuses (fail-safe proof).
- **E2E COUNT_DISTINCT proof (first ever in `contract.*`):** with real Customer Invoice COs resolved, evaluate ARPI once and inspect the snapshot — confirm the denominator is a **distinct** invoice count (not row count). Gated behind a separate Bar-2 authorization (not in this writer's scope, but named here as the generalization gate).
- **Idempotency:** re-running the writer for ARPI does not create a second active legacy MC.

## 11. Rollback plan

- **Writer code:** revert the held PR (no runtime effect until executed).
- **Single ARPI write:** the created legacy MC is **archivable** — set `contract.metric_contract.archived_at` (soft delete, D162 rule 8) via the governed path → it leaves `listActiveMcs`; supersede/transition the MCV out of `active`. No hard delete needed; immutable history preserved (Invariant III). No tenant facts were produced (Bar 2 deferred), so there is nothing to unwind downstream.
- **§8 DDL:** revert script re-adds the FK + NOT NULL (valid only while no NULL `metric_definition_id` rows exist — so revert the ARPI write first). Golden snapshot is the backstop.

## 12. Can the ARPI writer be opened as a held PR after this DBCP?

**Yes — held, with a hard dependency.** After this DBCP is approved, a held writer PR (new `Mcf…MaterializationWriterService` + `createMinimalMetricContract` null-definition extension + tests) **can** be opened. It **must not merge or execute** until: (a) the **§8 DDL sub-DBCP** is approved + applied (golden-snapshot-backed); (b) the **§6 preconditions** verify (especially CC `posting_date_field` + fiscal calendar); and (c) D428 §9 is satisfied by (a). The held PR is code-complete-and-reviewable but inert — exactly the established hold pattern. Recommended order: **approve this DBCP → author + approve + apply §8 DDL → open held writer PR → verify §6 → execute once for ARPI under explicit approval.**

## 13. Open items

- **OI-1 (RESOLVED 2026-06-09 — GO):** `cc__customer_invoice_arpi_slice` declares `body.posting_date_field = "document_date"` (verified, read-only probe `_step5-ddl-and-oi1-probe.mjs`). No CC correction required; the writer PR is **not** blocked on this. See `d429-step5-metric-definition-id-nullable-dbcp-2026-06-09.md` §OI-1. *(§6.2)*
- **OI-2:** fiscal calendar seeding for the evaluation tenant (D364/D365) — verify at Bar-2 time, not now.
- **OI-3:** `COUNT_DISTINCT` is unproven E2E in `contract.*` — first-use; §10 E2E proof required before generalization.
- **OI-4:** `category_code` schema drift (DDL/Drizzle vs live) — reconcile in §8.
- **OI-5:** Q1 long-term shape — promote MCF provenance from `header` (now) to a typed `mcf_*` column (option (c)) if/when materialization generalizes past ARPI.

**No implementation performed. No DB write, no DDL, no materialization. D428 §9 intact. bc-core on `main d92dda3`.**
