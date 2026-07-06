---
title: "MCF-Materialized Metrics — D305 chain_status / MLS-14 Visibility Study (D429 Step-5 check-5)"
status: study
date: 2026-06-09
project: bc-core
domain: mcf
subdomain: metric-runtime
focus: governance
related:
  - D429 (MCF→legacy materialization)
  - D305 (chain_status SSOT, ADR-bebaec)
  - D391 / DEC-b8b825 (MLS-14 activation gate)
  - D366 / DEC-804874 (L-node semantic verdict)
  - DEC-61f7c8 / D428 §9 (materialization guardrail)
  - HA-1 / D426 (MCF zero-legacy-reads)
  - metric-context-framework-build-plan.md (L5 lock, R-05)
artifact_kind: read-only-architecture-study
---

# MCF-Materialized Metrics vs D305 chain_status & MLS-14 — Read-Only Architecture Study

**Scope:** read-only. No code, DB, schema, tenant-runtime, or materialization changes were made
in producing this study. Grounded against live `bc_platform_dev` and bc-core `main @ ed6c6f0`.

## Recorded decision (operator-locked, 2026-06-09)

- The D429 Step-5 ARPI materialization write **succeeded** (legacy MC `98ae46ed-3c3f-4a31-8cee-4adb762717ab`,
  active version `1.0.0`, `metric_definition_id IS NULL`, `header.lineage` from MCV `b1933c30`).
- Legacy `contract.chain_status` / MLS-14 (`l_node_semantic_verdict`) evidence was **not emitted**.
- This is an **evidence-emission / readiness-visibility gap — NOT proof that ARPI is ungated.**
- **MCF M13/M14 evidence is the authoritative governance evidence** for MCF-materialized metrics.
- **Interim model: D** — mark the metric as MCF-governed / legacy-readiness N/A.
- **Target model: B** — a read-only MCF readiness evidence bridge.
- **Reject A** — do not synthesize a legacy D305 `chain_status` row from the old L1–L8 walk for
  v2-concept-bound metrics (it would render a false RED — see S1).
- **Defer C** — no new MCF-specific projection table yet.
- The writer's hardcoded `chainVerdict:"complete"` **must be corrected** — it should return
  `mcf-governed` or an evidence-backed status (Foundation Invariant VI: evidence emitted, not inferred).

## 0. Grounded state (live)

| Fact | Value |
|---|---|
| Legacy MC | `98ae46ed-3c3f-4a31-8cee-4adb762717ab` (`average_revenue_per_invoice`) |
| Version | `1.0.0`, `governance_state_code='active'`, `version_count=1` |
| `metric_definition_id` | **NULL** |
| `contract.chain_status` row for MC | **none** (table total 540, none in 20 min) |
| `l_node_semantic_verdict` row for MC | **none** (table total 202, latest `2026-05-17`) |
| Source MCV `b1933c30` | active / `is_current=true` |
| MCF upstream evidence | complete — 20 PE-MC rows (9 PASS + PE-MC-8 OPERATOR_REVIEW ×2 phases), 1 passing non-stale M10 verifier result (`metric_self_verification_result`), 1 `metric_transition` activation cert, 6 stamped hash columns |

## 1. Corrected root cause

The first-pass check-5 note attributed the missing row to "the D305 funnel is `metric_definition`-variable-centric,
so a NULL-definition metric enumerates no variables." **That mechanism is incorrect.** Evidence:

- `ChainStatusService.processOneMcVersion` enumerates variables from
  **`mcv.contractJson.body.co_bindings`** (`bc-core/src/registry/chain-status.service.ts:579-580`),
  **not** from `metric_definition`. ARPI *has* co_bindings.
- It calls `upsertChainStatus` **unconditionally** (`chain-status.service.ts:275`) — no early return.
  So **if it had run, a row would exist.**
- The env-on activation log contains **zero** "Pre-activation chain status…" lines
  (the success log at `chain-status.service.ts:915-917`).

**Actual mechanism.** `ContractService.activateVersion` (`contract.service.ts:489`) →
`transitionState` (`:516`). The metric-gate block (`:530`, entered because `detectCategory` keys on
*table membership* — `contract.repository.ts:27-37` — so `category='metric'` regardless of NULL
definition) invokes the chain refresh and MLS-14 gate only behind two `@Optional()` guards:

- `if (this.chainStatusService)` (`contract.service.ts:546`) — **false at runtime** (no refresh log, no row).
- `if (this.mls14Gate)` (`contract.service.ts:565`) — **false at runtime** (no `l_node` verdict; not wired — see S2).

⇒ **Both the D305 pre-activation refresh and the D391/D366 MLS-14 gate were silently no-op'd.** The metric
activated through the bare state transition. This is **not MCF-specific** — it is the activation path's
optional gates resolving to null.

## 2. Q1 — D305 enumeration & why no funnel row

- Per-version: `refreshChainStatusForVersion` (`chain-status.service.ts:894`) → `processOneMcVersion`
  (`:227`) → `traceMcVersion` (L1–L8 per co_binding) → `upsertChainStatus` (`:275`, INSERT…ON CONFLICT `:826`).
- Bulk: `refreshChainStatus` (`:135`) → `getActiveMcVersions` (`:859`) → `catalog.listActiveMcs(...)`.
- Funnel **list** read (`:534-561`): `FROM contract.metric_contract mc LEFT JOIN contract.chain_status cs …
  WHERE mc.archived_at IS NULL` — **no `metric_definition_id` filter**. ⇒ ARPI **already appears** in the
  funnel list as a zero/empty row; it is "uncomputed," not "invisible."
- Why no row now: the synchronous per-version refresh never fired (§1). The next bulk refresh **would**
  enumerate it (see S1) — but with a misleading verdict (see S1 caveat).

## 3. Q2 — MLS-14 PASS/BLOCK on absent chain_status

- Design (`contract.service.ts:537-578`): the sync refresh exists so MLS-14's LEFT JOIN on `chain_status`
  finds a row; otherwise MLS-14 would refuse `chain_not_complete` (BLOCKER). Refuses only on BLOCKER codes
  (`semantic_class_collapse`, `chain_not_complete`).
- What happened: MLS-14 **did not evaluate** — `this.mls14Gate` null (`:565` false). Neither passed nor
  blocked; **skipped**. No `l_node_semantic_verdict` emitted. The gate implementation lives at
  `bc-core/src/mls/gate/mls14-activation-gate.service.ts` (MlsModule), not wired into ContractModule.

## 4. Q4 — Is `chainVerdict:"complete"` honest?

**No.** `mcf-arpi-materialization-writer.service.ts` returns `chainVerdict:'complete'` as a **hardcoded
constant** after `activateVersion` doesn't throw — not read from any persisted verdict. Given §1–§3
(no refresh, no gate) it asserts a completeness never computed. **Violates Foundation Invariant VI**
(evidence emitted, not inferred).

## 5. Q5 — Should activation have refused?

**No.** The legacy `contract.metric_contract` row is a **projection of an already-governed MCF MCV**, not a
net-new governed artifact. ARPI's authoritative chain-integrity gate ran upstream in MCF: M13 PE-MC
(10 checks) + M14 publication (`metric_transition` cert), and **M14 reads only `mcf.*` — zero legacy
reads/writes (HA-1/D426)**. The writer's **Guard B + D430** already enforced the upstream-supply-chain leg
at write time (single active CC-v2 + `posting_date_field='document_date'`). So the metric is **not ungated** —
the gate was applied; only its **evidence was not emitted** into the legacy tables. Refusing would have been
wrong; **emitting the verdict honestly** is what's missing.

Caveat: the build-plan **L5 lock** (`metric-context-framework-build-plan.md:55`) holds MLS-14 and PE-MC as
"layered both-must-pass gates [that] do not subsume" each other, and `:437/:527` name "MLS-14 + PE-MC-10 +
`chain_status` carry the gating load." For an MCF-materialized metric, the `chain_status` co-gate's *intent*
is satisfied by D430/Guard B, but its *artifact* is absent — a gap between intent and recorded evidence.

## 6. Q3 — Options A/B/C/D

| Opt | Description | Assessment |
|---|---|---|
| **A** | Synthesize legacy `chain_status` from contract_json/co_bindings | **Reject.** `traceMcVersion` walks the legacy CF/BF/`canonical_mapping` L1–L8 registry (`chain-status.service.ts` `loadCfRegistry:978`, L8 `:1138`), not the v2 concept chain (D430/D431). A v2-concept-bound MCF metric would likely score `unlinked`/`broken` → **false RED** (confirmed plausible by S1). |
| **B** | Bypass legacy D305; rely on MCF M13/M14 + read-only readiness evidence bridge | **Recommended target.** Aligns with HA-1/D426 + event-sourced MCF evidence. Bridge surfaces PE/verifier/cert evidence where the readiness UI looks, keyed by lineage/provenance. |
| **C** | New MCF-specific chain_status/readiness projection table | **Defer.** MCF readiness is already event-sourced; a projection is convenience, not necessity. |
| **D** | Keep active; mark "not legacy-readiness-visible" until Bar-2 | **Recommended interim.** Honest, zero-risk. |

## 7. S1/S2 probe results (2026-06-09)

### S1 — does `catalog.listActiveMcs({mode:'all-active-versions'})` include NULL-definition metrics?
**Yes.** `MetricCatalogReader.listActiveMcs` (`metric-catalog-reader.repository.ts:137-175`):
`FROM contract.metric_contract mc JOIN contract.metric_contract_version mcv … AND mcv.governance_state_code='active'
LEFT JOIN contract.chain_status cs … WHERE mc.archived_at IS NULL ${mcFilter}`. `metric_definition_id` is
selected (`:153`) but **never filtered**. ⇒ The bulk chain-status refresh enumerator **includes**
NULL-definition metrics; the gap is **transient at the enumeration level**.

**Caveat (reinforces Reject-A):** a refresh-produced row would carry the legacy L1–L8 verdict, which does
not understand the v2 concept chain → likely a **false RED**. "Transient" means a row would appear, **not**
that a green row would appear.

### S2 — why does ContractService see `chainStatusService` / `mls14Gate` as null?
- **`mls14Gate` = CONFIRMED missing module import.** `ContractModule` (`contract.module.ts`) imports only
  `EvidenceModule`, `SchemaProvisionerModule` (`:51`); it does **not** import `MlsModule` nor provide
  `Mls14ActivationGate` (it provides `Mls14PredicateService`, a different class). `ContractService` ctor
  `@Optional() mls14Gate` (`contract.service.ts:68`) → null.
- **`chainStatusService` = NOT a missing import.** ContractModule provides+exports `ChainStatusService`
  (`:70/:104`); only one `ContractService` instance exists (providers list it only in `contract.module.ts`;
  `mcf.module.ts:123` is a comment); `ChainStatusService` ctor (`chain-status.service.ts:124-128`) does not
  back-inject `ContractService` (no direct cycle). Static wiring is **correct**, so the runtime null is
  **not statically explained** — most likely a **DI instantiation-order / circular-dependency artifact** in
  ContractService's broader optional-dep graph (several `@Optional()` deps: `evidenceService`,
  `chainStatusService`, `contractActivationService`, `mls14Gate`, `canonicalResolver`, …). **Definitive
  confirmation requires a runtime DI probe** (e.g. log `!!this.chainStatusService` at activation, or inspect
  Nest's dependency graph) — out of scope for this read-only static study; it is Track-2's first step.

## 8. Recommended architecture decision (matches locked decision)

**D now → B target; reject A; defer C; plus two honesty fixes.**
1. **Interim (D):** record provenance — MCF-governed; legacy `chain_status`/MLS-14 not authoritative —
   in `header.lineage`/provenance + docs, so the empty funnel row reads "MCF-governed, N/A," not "broken."
2. **Target (B):** read-only MCF→readiness evidence bridge surfacing M13 PE + M10 verifier + M14 cert as the
   readiness verdict for MCF-provenance metrics (instead of the legacy L1–L8 walk).
3. **Honesty fix #1:** writer stops returning hardcoded `chainVerdict:'complete'`; return `mcf-governed`
   or read MCF evidence.
4. **Latent-defect flag (separate track):** ContractService.activateVersion's sync chain refresh **and**
   MLS-14 gate are inert (null `@Optional()` deps) for **all** legacy metric activations on that path —
   not just MCF. Highest-value finding; its own investigation.

## 9. Follow-up tracks (drafts, not changes)

### Track 1 — MCF-readiness bridge + writer-verdict honesty (DBCP outline)
- **Scope:** (a) writer `chainVerdict` honesty (1-line return change + spec); (b) read-only MCF-readiness
  bridge service/endpoint surfacing PE/verifier/cert evidence for MCF-provenance metrics; (c) a provenance
  marker / read-model label ("MCF-governed; legacy-readiness N/A").
- **No schema change** (lineage/provenance exist; bridge is read-only).
- **Tests:** writer spec asserts non-hardcoded verdict; bridge unit tests over ARPI's existing MCF rows;
  regression test that legacy `metric_definition` metrics still receive their `chain_status` row.
- **Rollback:** additive/behavioral — revert commit.

### Track 2 — Inert legacy activation gates investigation (separate from ARPI)
- **Step 1 (runtime probe, separately approved):** confirm at runtime whether
  `ContractService.chainStatusService` / `mls14Gate` are null on the activation path (debug log or Nest
  dependency-graph dump).
- **Step 2:** root-cause — (i) wire `MlsModule`/`Mls14ActivationGate` into ContractModule
  (confirmed missing for mls14Gate); (ii) resolve the chainStatusService DI artifact (forwardRef / module
  re-org); or (iii) ratify the sync hook as intended dead code (the bulk refresh + D316 readiness scheduler
  being the real gates) and remove the misleading hook.
- **Blast radius:** affects all legacy metric activations through `ContractService.activateVersion`, not
  just MCF — gate this as a platform-integrity DBCP with its own approval.

## 10. Stop conditions

- **S3 (governance call):** are MCF-materialized metrics gating-governed **solely** by MCF M13/M14
  (this study's recommendation) or must they **also** carry a legacy `chain_status` co-gate (strict reading
  of build-plan L5/R-05)? Operator decision, not a code change.
- **Hard stop:** no code/schema/DB writes until Track-1/Track-2 DBCPs are individually approved.

## 11. Foundation note

The metric's upstream gate **was applied** (Guard B / D430) but its **PASS was not emitted** into the legacy
evidence tables, leaving correctness to be *inferred* from the absence of a refusal. **Foundation Invariant VI
(evidence is emitted, not inferred)** is the governing lens: the fix is to *emit* the verdict (honest writer
status + MCF readiness bridge), not to refuse activation and not to manufacture a legacy L1–L8 row.
