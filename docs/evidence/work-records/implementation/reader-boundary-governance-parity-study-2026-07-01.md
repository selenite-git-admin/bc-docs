---
uid: STUDY-reader-boundary-2026-07-01
title: "UniBAT Reader Boundary — Governance-Parity Study & Plan"
description: "Grounded audit + plan to bring the admission-entry boundary (Source State → UniBAT Reader → Source Object) to BCF/MCF/metric-engine-grade governance, on two axes. Part 1 — RUNTIME: what is governed (admission contract gate + validation), what is not (admission-run resumability/idempotency, flavor governance, executor version-gating, reader-level evidence). Part 2 — AUTHORING: the governed reader onboarding surface — the subfunction grouping doctrine, the four-layer model (Reader → Flavor → per-entity Admission + Observation Contract binding), the design policies, and the authoring-service target the Reader lacks (creation is thin CRUD + seed). AR-first, so the first pilot E2E stands on a verified, correctly-wired Reader. Companion to the metric-evaluation-boundary study."
status: drafting
authority: study
date: 2026-07-01
project: bc-core
domain: readers
subdomain: reader-runtime
governing_sources:
  - The Invariants — II (ordering begins at the SO), III (immutable), V (non-replayable), VI (evidence emitted)
  - The Evaluation Boundaries — the admission boundary (repair location A)
  - The Contract Grammar — Source / Admission / Observation Contracts
  - Metric Evaluation Boundary Governance-Parity Study (2026-07-01) — the companion + the pattern to port
---

# UniBAT Reader Boundary — Governance-Parity Study & Plan

*Grounding tags: **[F]** Foundation invariant · **[Cv]** code fact verified first-hand (this study) · **[Cm]** code fact from the 2026-07-01 read-only audit map (spot-verify before an ADR builds on it) · **[T]** target — proposed · **[X]** external influence.*

## 0. Why this document exists

BCF governed the concepts, MCF governed the metrics, and the Metric Evaluation Boundary study (2026-07-01) governed the *evaluation* runtime (`CO → Metric Snapshot`). The **UniBAT Reader** — the *entry* boundary, `Source State → Reader → Source Object` — is the last major organically-evolved runtime, and it is the one place where "garbage in" is literal: the Source Object is the **first authoritative object**, where Invariant II's ordering *begins*. An ungoverned Reader poisons the whole chain and no downstream governance recovers it.

This matters acutely for the **first pilot E2E** (fine-tuned SDG → `pilot1` → all active AR metrics). That run is `SDG → Reader → SO → CO → MS`. If the Reader is ad-hoc, every Source Object is suspect and the E2E validates a governed metric engine on an ungoverned foundation — which proves nothing. So governing the Reader is a *precondition* for the E2E to mean anything, not scope creep.

**Headline (grounded, not assumed):** the Reader boundary is **more built than the metric engine was** — it is production-wired end-to-end, and the *admission contract gate is genuinely governed* (strict validation + an enforced reader binding). The gap is specifically the **Reader runtime layer**: ungoverned flavors, hand-wired un-version-gated executors, **no admission-run resumability/idempotency (per-batch independent writes)**, implicit reader-level evidence, and a **rotted baseline test**. The diagnosis "governed contracts over an organically-evolved runtime" holds — but the fix is targeted, not a rewrite.

## 1. Governing principle: the Reader IS the SDG-blindness boundary

The Metric study §1 established that the runtime is **SDG-blind** — SDG is a source system *behind the Reader*. **The indistinguishability that matters is achieved** (precise version, per the Codex audit §11): **[Cm]** `SdgOdataExecutor` (`sdg-odata.executor.ts:82`) emits ordinary `RunObservationItem`s — no synthetic flag in the payload/admission shape, so **downstream never branches on the source**; the orchestrator/admission treat SDG records identically to a real SAP read. It DOES honestly stamp `provenanceJson.source = 'bc-sdg'` (`:88`) — but that is *correct Invariant-VI provenance* (real SAP would stamp `'sap'`), not a blindness leak: blindness means no downstream *special-casing*, which holds. **[Cv]** the Reader runtime is executor-agnostic — it never knows the source protocol (`reader-runtime.service.ts:124-132`, executor resolved by `connector.executorClass ?? flavor.name`).

Consequence: **the SDG-on-pilot1 E2E is only meaningful because the Reader is SDG-blind**, and it *is*. This is the good news — the pilot's core assumption is sound. It also binds the plan: nothing in the Reader may become SDG-aware; SDG conforms to the Source/Admission Contracts, never the reverse.

## 2. What the Reader boundary is

Foundation **repair location A** (source reality / admission boundary): the Reader, the Admission Contract, the Observation Contract, the Source Contract. It produces the **Source Object** — Invariant II's ordering starts here. The moving parts (all **[Cv/Cm]**):
- **Reader + Reader Flavor** — a read configuration (`runtime.reader_flavor`): which connector/connection/entities/config. **[Cm]** unversioned; `status_code` defaults `'draft'`; `config_json` is open JSONB; the `observation_contract_id` is optional/soft.
- **Executor (protocol reader)** — the source-specific fetch (SAP OData v2/v4, Salesforce, ECB SDMX, OER, **SDG OData**). **[Cv]** hand-registered in a `Map` at module init (`ExecutorRegistryService`); resolved by key at runtime (`reader-runtime.service.ts:126-127`).
- **Reader Binding** — `runtime.reader_binding` binds (reader, source entity, environment) → an **admission contract version**. **[Cv]** ENFORCED: the runtime throws if no active binding exists (`reader-runtime.service.ts:144-148`). This is the entry governance gate.
- **Admission Run** — `runtime.admission_run`, one per execution cycle. **[Cv]** created `status='running'` (`:156-165`), closed `'completed'`/`'failed'` (`:247-250`, `:312-317`). Mirrors `metric_run`.
- **The downstream boundaries** — Observation (synthesize SO + emit evidence/lineage), Admission (validate against the AC, accept/reject + evidence), Canonical, Metric.

## 3. As-built coherence map

### 3.1 The Reader runtime (thin orchestration)
**[Cv]** `ReaderRuntimeService.executeReader()` (`reader-runtime.service.ts:80-326`, flagged `// eslint-disable max-lines-per-function` — a long, organically-grown method): resolve reader → flavor → connection endpoint → executor (by key) → active admission bindings (throw if none) → create `admission_run` → run the executor → **feed observations to the orchestrator in batches of 100** → close the run → best-effort readiness + auto-canonical-resolution + metric-eval triggers.

The runtime is **executor-agnostic and validation-free**: it does not validate observations — that is the Admission boundary's job.

### 3.2 The governed layer (the parts that ARE mature)
- **[Cv]** Reader binding is enforced (`:144-148`) — no read runs without an admission-contract binding.
- **[Cm]** Admission validation is strict: `ContractValidationService.validateAgainstContract()` runs structural (AJV JSON-Schema 2020), identity, temporal, and admissibility stages (`admission.service.ts`, `contract-validation.service.ts`), rejecting non-conforming records.
- **[Cm]** Observation + Admission boundaries emit evidence + lineage (Inv VI) — `observation_recorded` / `observed_as`, admission accept/reject evidence.
- **[Cv]** The admission run lifecycle exists (created `running`, closed `completed`/`failed`).

### 3.3 The store
**[Cm]** `admission.admitted_record` (accepted SOs) + rejection evidence + `runtime.admission_run` (run telemetry). Per D369 the typed `fact.so_*` store is the target SO home (companion to `fact.co_/ms_`). The admission run carries record counts + duration + error ref.

## 4. Five-dimension governance audit (verdicts)

| # | Dimension | Verdict | Grounding |
|---|---|---|---|
| a | Wired to production | **HIGH** — unlike the metric engine (unwired), the Reader is fully production-wired: `POST /t/readers/:id/execute` → full pipeline **[Cm]** | better than the metric engine's start point |
| b | Governed enough | **SPLIT** — the admission *contract gate* is strict **[Cm]**; the *runtime layer* is loose: flavors unversioned/`draft`-default, executors hand-wired, **no version-gating** of flavor/executor/AC-at-flavor **[Cv/Cm]** |
| c | Error / failure | **MEDIUM** — executor failure is caught, run marked `failed`, operator ticket raised **[Cv:309-325]**; but downstream (readiness, canonical resolution, metric eval) is best-effort `.catch()` **[Cv:256-286]** → a run can report `completed` while COs/metrics silently didn't surface. No circuit breaker |
| d | Evidence / lineage (Inv VI) | **PARTIAL — but present, not absent (corrected per §11).** observation/admission emit evidence downstream **[Cm]**; reader-run evidence DOES exist — terminal (`reader.service.ts:546`) + per-batch (`orchestrator.service.ts:126`) — but is **under-contextualized**: it carries reader/contract/version only, not flavor, connection, executor key/version, source-entity set, or fetch provenance. The gap is *completeness*, not existence |
| e | When/how SOs written (Inv III) | **LOW — the serious gap.** **[Cv:233-243]** observations are admitted in independent 100-record batches (a separate `executeFullCycle` per batch); a mid-run failure leaves batches `1..N-1` committed while the run is marked `failed`. **No atomicity, no resumability, no idempotent re-admission** (a re-run re-observes/re-admits). This is the same class of gap `metric_run` + deterministic-id + `ON CONFLICT` solved for the metric boundary |

Secondary findings: **[Cv]** the baseline test `reader-runtime.service.spec.ts` is **broken** — it constructs the service with 6 args against a 10-arg constructor (`:64-75`), so 11/13 tests fail (`executorRegistry` lands in the `canonicalResolution` slot). **[Cv]** stale defaults: `tenantId ?? 'demo-selenite'` (`:159`) and `?? 'unknown'` (`:258, :281, :320`) — `demo-selenite` is not the live tenant (`pilot1` is).

## 5. The closure rule, applied to admission

> No admitted-object shape is admissible until the Admission Contract can declare it, admission validation can gate it, the Reader runtime can produce it **resumably and idempotently**, and the store can persist it immutably — all four expressing the same thing.

Today: the AC declares + admission validates (governed), but the runtime produces it **non-resumably / non-idempotently** and writes per-batch. That is the vertical layer-drift the closure rule forbids — the same drift the metric study found one boundary downstream.

## 6. Gaps & discussion

1. **Admission-run resumability/idempotency (the serious one).** Per-batch independent writes + a non-resumed failed run + no idempotent re-admission = partial data on failure and duplicates on retry. **Discussion:** the fix is a *port*, not an invention — the metric boundary already solved this (a run object as the idempotency boundary + deterministic identity + `ON CONFLICT DO NOTHING`). Admission needs a deterministic admitted-record identity (source natural key + admission-run scope) so re-admission is idempotent and a failed run is resumable.
2. **Reader Flavor governance.** A flavor is an ungoverned JSONB config (`draft`-default, unversioned). **Discussion:** should a flavor be a governed, versioned entity (like an SC/AC version) with an activation gate, or does the *reader binding* (already enforced, version-pinned to an AC) carry enough governance and the flavor stay operational config? Likely the binding is the governance anchor; the flavor needs *versioning + an active-state gate*, not full contract status.
3. **Executor version-gating.** Executors are hand-wired with no version tracking. **Discussion:** stamp an executor/protocol version on the admission run (evidence context, Inv VI) so a Source Object records *which reader produced it* — parity with the metric engine's `engine_version` target.
4. **Reader-level evidence.** Reader execution isn't traced to the evidence chain (only implicit via `admission_run`). **Discussion:** emit an explicit reader-run evidence record (Inv VI) so "which read produced this SO, from which flavor/executor/source, when" is preserved, not inferred.
5. **Best-effort downstream.** Canonical resolution + metric-eval triggers are non-fatal `.catch()`. **Discussion:** acceptable as *triggers* (the orchestrator §13 will own re-triggering), but the run's `completed` status should distinguish "admitted + surfaced" from "admitted, downstream deferred" so it isn't read as fully done.
6. **Rotted test + stale defaults.** The broken baseline test and `demo-selenite`/`unknown` defaults are hygiene debt that erodes trust in the boundary.

## 7. Target: the governed Reader boundary (all SDG-blind)

1. **Resumable, idempotent admission run** — port the metric-boundary pattern: a deterministic admitted-record identity (source natural key + run scope) + `ON CONFLICT DO NOTHING`; a failed run is resumable, a redelivery supersedes-or-skips, never duplicates. **The one that should land before the pilot ships.**
2. **Flavor versioning + active-state gate** — a flavor carries a version + an activation gate; the reader binding stays the AC-version anchor.
3. **Executor/reader version stamped on the run** (Inv VI evaluation context) — a Source Object records which reader produced it.
4. **Explicit reader-run evidence** on the authoritative evidence chain (Inv VI).
5. **Honest run status** — distinguish admitted vs downstream-surfaced.
6. **Fix the baseline test + stale defaults** — restore the trustable baseline.

## 8. Non-goals

Not a rewrite — the pipeline is wired and admission validation is strict; the work is the runtime *governance layer*, not the fetch/validate logic. Not new executors. **Not SDG work** — SDG-blindness is confirmed and must be preserved (SDG conforms to the SC/AC). Not an Admission-Contract-grammar change (that grammar is governed; this is the runtime that serves it).

## 9. Build sequence

**The pre-pilot gate is TWO items** (revised per the Codex audit §11): (1) admission-run resumability/idempotency, and (2) active/explicit flavor gating for the AR path — because the runtime picks `flavors[0]` (`reader-runtime.service.ts:97`) and the flavor list is not filtered to `status=active` (`reader.repository.ts:393`), while `reader_flavor` defaults to `draft`, so a pilot could silently read via a draft/inactive flavor unless the caller passes the exact AR `flavorId`.

**Slice 0 — AR-first hardening (the E2E precondition):**
- Fix the `reader-runtime.service.spec` baseline (the 10-arg DI) — restore the green baseline.
- **Flavor gating (pre-pilot):** require an explicit `flavorId` OR filter flavor selection to `status=active` (+ exclude archived) — so the AR pilot cannot read through a draft flavor.
- Trace + verify the **AR admission path** on constructed/SDG data: `SDG → SdgOdataExecutor → observation → admission validation against the AR Admission Contract → Source Object`. Confirm the AR reader binding + flavor + AC are sound and produce valid SOs. Read-only against live substrate where possible; constructed data otherwise (STOP AT CHAIN INTEGRITY).

**ADR sequence (the parallel program, AR as first slice):**
1. **ADR — Admission run resumability & idempotency** (port the metric pattern; the serious one; **pre-pilot**). Independently confirmed (Codex §11): no hidden dedupe — observation/admission mint fresh IDs per record (`observation.service.ts:55`, `admission.service.ts:164`) and `progression.*` has no uniqueness over (source natural key, run), so a re-run re-admits as new.
2. **ADR — Reader Flavor versioning & active-state gate** (**now pre-pilot for selection** per §11; full versioning can follow).
3. **ADR — Reader evidence: COMPLETE it, don't add it.** Terminal + per-batch admission-run evidence already exist (`reader.service.ts:546`, `orchestrator.service.ts:126`) but carry only reader/contract/version — extend to flavor, connection, executor key/version, source-entity set, and fetch provenance (Inv VI completeness).
4. **ADR — Run-status honesty + failure taxonomy** — distinguish *admitted/completed* from *downstream-surfaced*. Scope note (§11): this gates a pilot claim of "E2E surfaced metrics"; a narrower "SO admission integrity" claim does not require it.

Each closes under the closure rule (§5) and is validated SDG-blind (§1). Same rhythm that worked for the metric engine: prove AR-first, then generalize.

## 10. Evidence & verification

**First-hand verified this study [Cv]:** the 10-arg constructor vs the spec's 6 (`reader-runtime.service.ts:64-75` vs `reader-runtime.service.spec.ts:139`); the per-batch admission with no atomicity (`:233-243`); best-effort downstream (`:256-286`); failed-run-not-resumed (`:309-325`); enforced reader binding (`:144-148`); the run lifecycle (`:156-165`, `:247-250`); stale tenant defaults (`:159, :258, :281, :320`).

**From the 2026-07-01 read-only audit map [Cm] — spot-verify before the ADRs build on them:** SDG-blind executor (no synthetic flag); strict admission validation (AJV + identity + temporal + admissibility); observation/admission evidence emission; flavor `draft`-default + open JSONB + optional OC; the executor registry contents. The map is thorough and internally consistent, but these were not re-read first-hand for this study.

## 11. Independent audit refinements (Codex, 2026-07-01) — accepted

An independent audit confirmed the load-bearing claims and sharpened five points; the study above is revised to match.

1. **Admission idempotency/resumability — confirmed, no hidden dedupe (the pre-pilot claim).** Independently traced: observation/admission mint fresh IDs per record (`observation.service.ts:55`, `admission.service.ts:164`), `progression.*` carries indexes but no uniqueness over (source natural key, run) (`progression.ts:43`), and the only duplicate check is by the freshly-generated source-object id (`admission.service.ts:55`) — so a re-run re-admits as new data. "Same class as the metric-run gap; port the pattern" is correct.
2. **Flavor governance upgraded to pre-pilot.** The runtime selects `flavors[0]` when no `flavorId` is passed (`reader-runtime.service.ts:97`) and the flavor list is not filtered to `status=active` / non-archived (`reader.repository.ts:393`), while `reader_flavor` defaults to `draft`. A pilot could silently read via a draft/inactive flavor. → the pre-pilot gate is now TWO items (§9).
3. **SDG "identical observations" overstated → corrected (§1).** Observations are identical in payload/admission shape (no downstream branching), but the executor honestly stamps `provenanceJson.source='bc-sdg'` (`sdg-odata.executor.ts:88`). That is correct Inv-VI provenance, not a blindness leak.
4. **Reader-run evidence: "add from zero" → "complete it" (§4d, §9-ADR-3).** Terminal + per-batch admission-run evidence already exist (`reader.service.ts:546`, `orchestrator.service.ts:126`); they are under-contextualized (reader/contract/version only), not absent.
5. **Downstream best-effort — scope by the pilot's claim (§9-ADR-4).** Status-honesty (admitted vs downstream-surfaced) gates a pilot claim of "E2E surfaced metrics"; a narrower "SO admission integrity" claim does not require it.

Confirmed first-hand by the audit: the rotted baseline test (11 failed / 2 passed; `executorRegistry.get` undefined at `:127`), the enforced reader binding (`:144`), and strict validation with rejection-before-persistence (`contract-validation.service.ts:60`, `admission.service.ts:71`). Diagnosis "governed contracts over an organically-evolved runtime" assessed as fair. (Live SQL spot-check was skipped — `psql` not on the auditor's PATH; the code-level audit stands.)

---

# Part 2 — the Reader onboarding / authoring governed surface

*Part 1 (above) audits the Reader **runtime** (resumability, evidence, status). Part 2 is the deeper axis surfaced while grounding the pilot AR path: **how readers are created, grouped, and wired** — the governed authoring surface BCF and MCF have but the Reader lacks. This is where the grouping doctrine, the per-entity OC wiring, and the activation gate live; it is what makes a *trustworthy* reader (correct flavor, wired observation contracts, resolvable chain) rather than a hand-patched one. Grounding here is first-hand `[Cv]` (live `bc_platform_dev` queries + the creation service, 2026-07-01).*

## 12. Grounded reality of Reader authoring

- **[Cv] Grouping is already subfunction-scoped.** 24 readers, each exactly one `(source_category, function, subfunction)` — the full enterprise subfunction taxonomy (`accounts-receivable-reader` = `enterprise/finance/accounts_receivable`; also AP, GL, treasury, cost_accounting, cash_flow, fixed_assets, inventory, logistics, order_management, production, workforce, …). `reader_version` is NULL (unversioned); `status_code='active'`.
- **[Cv] Creation is thin CRUD + seed.** `ReaderService.createReader` is a name-uniqueness check under a `// Reader CRUD` header (`reader.service.ts:93-100`); the 24 readers were bulk-seeded (`registry/seed/seed-registry-full.ts`). No validation, no lifecycle gate, no policy — unlike `bcf-registry-authoring` / the metric-authoring panel.
- **[Cv] Flavors are ungoverned in cardinality.** 65 total / 13 active; AR alone has 5 active (`apex-actual-ledger`, `apex-journal-entry-hdr`, `apex-receivable-hdr`, `ecc-bc-ar-operations`, `ecc-credit`) → `flavors[0]` (`reader-runtime.service.ts:97`) is nondeterministic.
- **[Cv] Binding is per-entity → Admission Contract** (`reader_binding`: reader/flavor, `source_entity`, admission-contract version) — correctly granular.
- **[Cv] The semantic layer is barely built vs the admission layer.** `source_contract` = 30,370, `admission_contract` = 30,369 (bulk, ~1 AC per source entity), but `observation_contract` = **6** (5 AR-related + active: `oc__receivable_posting_bsad`, `oc__receivable_clearing_bsad`, `oc__customer_invoice_arpi_slice_type_sd_s_map`, `oc__customer_invoice_cleared_item_bsad`, `oc__customer_master_payer_kurgv`).
- **[Cv] The OC is under-modeled + unwired.** `reader_flavor.observation_contract_id` is a *single* field, and **0 flavors are linked to any OC** — so `SO → CO` resolution (D336, gated on `flavor.observationContractId`, `reader-runtime.service.ts:270`) never fires, even though the AR OCs exist. A flavor MUST be able to observe many entities — the AR-family chain requires one flavor over `BSAD` + `KURGV` + `TYPE_SD_S_MAP` — yet a single-OC field can express at most one entity's OC. (Capability requirement, not current state: live flavors each bind ≤1 active entity today, so the single-OC field is not yet *visibly* broken; it becomes impossible the moment a flavor must observe the ≥2 entities every real metric chain needs — Part 2 §19 / ADR #R1 F4.)

## 13. The grouping doctrine: subfunction as the owning container (refined per §19 audit)

One reader per `(source_category, function, subfunction)` — the subfunction is the **owning container** for a coherent set of source entities and the metrics over them; it is the axis MCF also classifies metrics on (`function_code`/`subfunction_code`). Alternatives are worse: by *source-system* fragments one subfunction across SAP/Salesforce; by *entity* explodes into thousands of micro-readers; by *function* is too coarse (finance has ~10 subfunctions).

**Nuance (corrected — the earlier `reader.subfunction == metric.subfunction` was overstated):** the mapping is NOT strictly 1:1. **[Cv]** active AR metrics span *three* metric subfunctions — `accounts_receivable`, `billing`, `credit_and_collections` — but only `accounts-receivable-reader` exists (no `billing-reader`, no `credit-and-collections-reader`). So the reader taxonomy is currently **coarser and incomplete** relative to the metric taxonomy. The doctrine is therefore: subfunction is the grouping container, with **scenario / source-system / entity completeness beneath it**, and a standing question — *does every metric subfunction have (or map to) a reader that admits its entities?* For "AR" the answer today is "one reader nominally, but the billing + credit_and_collections metric families have no dedicated reader," which is part of the pilot alignment work (§17–§18-pre).

## 14. The four-layer model

```
Reader     = the subfunction's admission boundary        (one per source_category/function/subfunction)
  └ Flavor = a (source_system, scenario) way to read it   (e.g. SAP-ECC-AR)
      └ Binding (per source entity):
            → Admission Contract   (admissibility of the source shape)
            → Observation Contract (SO → CO: observed field → business concept → canonical field)
```

The key correction the grounding forces: **the Observation Contract must be bound per source entity, exactly like the Admission Contract** — not one `observation_contract_id` per flavor. That single-field model is why the `SO → CO` wiring is absent; a `(flavor, source_entity) → OC` binding (mirroring `reader_binding`'s `(flavor, source_entity) → AC`) is the fix.

## 15. Design policies (the governance CRUD lacks)

1. **Subfunction uniqueness** — at most one active reader per `(source_category, function, subfunction)`.
2. **Active-flavor determinism** — at most one active flavor per `(reader, source_system, scenario, environment)`, with runtime selection matching the admission run's connection → `(source_system, scenario)` rather than `flavors[0]`. **Keyed on the system axis, NOT collapsing it** — the Reader is system-agnostic, so one AR reader legitimately has a SAP flavor + an Oracle flavor + a Tally flavor all active (that is multi-system support); the defect is ungoverned *selection*, not flavor count. Kills the AR-5-flavors `flavors[0]` ambiguity.
3. **Per-entity contract completeness** — every bound source entity must resolve `SC → AC → OC → CC`; a reader cannot activate with a bound entity that has no OC. The `SO → CO` gap becomes a *gate*, not a silent stop.
4. **Chain-resolvability activation gate** — the closure rule applied to the reader: a reader activates only when its whole admission chain is resolvable (the same shape as MCF's `PE-MC-11` / the G3 source-chain gate).
5. **Versioning + lifecycle** — readers/flavors carry a version and a `draft → active` lifecycle with the gates above (`reader_version` is NULL today).
6. **Environment / flavor binding consistency** (added per §19 audit) — bindings within a reader must be environment-coherent. Today AR mixes `development` and `apex` bindings, has a duplicated `CustomerOpenItemSet`, null `flavor_id` (reader-level) bindings alongside flavor-scoped ones, and draft+active flavors under one reader. Per-entity completeness (policy 3) catches some of this, but environment-scoped determinism — one coherent binding set per `(reader, environment)` — deserves its own check.

## 16. The governed authoring surface (target)

A **Reader-authoring service**, parallel to `bcf-registry-authoring` / the metric-authoring panel: it validates the four-layer model against the §15 policies, drives a `draft → active` lifecycle with the completeness + resolvability gates, and emits evidence — replacing the CRUD + seed path. The live AR gaps (5 active flavors, unwired OCs, no `pilot1` binding) are precisely the *symptoms* of this surface not existing; the policies would have made them impossible.

## 17. Coverage quantification — binding ↔ OC misalignment (the real SO→CO gap)

**[Cv]** Traced the AR reader's bound source entities against the OCs' declared `source_references.source_table` (live, 2026-07-01). The AR reader binds 8 distinct entities; **only 1 has a matching OC:**

| AR reader binds | OC coverage |
|---|---|
| `TYPE_SD_S_MAP` (ARPI slice) | ✅ `oc__customer_invoice_arpi_slice_type_sd_s_map` |
| `BSID` (open items — `ar_balance`) · `BKPF` · `FAGLPOSE` · `I_BillingDocument` · `CustomerOpenItemSet` · `RVKRED_TS_POST_FLE` · `SGLPOS_C_CT` | ❌ none |

The OCs that DO exist target `BSAD` (cleared items — 3 OCs), `KURGV` (customer master), `RBKP` (AP) — **entities the AR reader does not bind**. So it is not "OCs exist, just wire them" (Part 2 §12's first read was too optimistic): the reader admits entities with no OC while the OCs describe entities that are not admitted. **The only coherent AR chain today is ARPI** (`TYPE_SD_S_MAP`, bound AND OC'd — consistent with ARPI being the one proven AR metric). The rest of the AR suite is blocked by a **binding ↔ OC misalignment**, not a wiring toggle.

This is the sharpest evidence for Part 2's thesis: the AR reader is `active` with **7 of 8 bound entities having no `SO → CO` path** — precisely what policy 3 (per-entity completeness) + policy 4 (chain-resolvability activation gate) would have refused.

## 18-pre. Pilot implication — align AR *through* the surface, not by hand

The pilot AR path is fixed by the authoring surface, not hand-patching, and the work is bigger than wiring:
- **Align bindings ↔ OCs per entity** (policy 3): for each entity the AR metrics need, ensure a bound entity WITH an OC → CC path. Concretely: author the missing OCs for the admitted entities (`BSID` for `ar_balance`, etc.), and/or bind the entities the existing OCs already cover (`BSAD` for cleared/clearing metrics, `KURGV` for customer-axis) — driven by what the active AR metrics actually consume.
- **Pin the AR flavor** (policy 2) and **create the `pilot1` binding** (Part 1 Slice-0 gap 3).
- **Pass the resolvability gate** (policy 4) before the reader is considered pilot-ready — so the pilot's `SO → CO → MS` chain is trustworthy per entity, not coherent for ARPI alone.

The pilot's honest scope today is **ARPI end-to-end**; "all active AR metrics" requires closing the binding↔OC alignment first — which is exactly the authoring-surface work.

### 17.1 True target set — AR-family metric → required entity analysis (quantified 2026-07-01)

**[Cv]** Traced all active metrics → bound business concepts → active-OC coverage → required source entities. Findings:
- **All 51 active metrics are AR-family**: 35 `accounts_receivable` + 3 `billing` + 13 `credit_and_collections`. So `accounts-receivable-reader` is the natural **AR-family container** for all three (they share source entities) — resolving the §13 subfunction question in the container direction.
- **Concept coverage is complete**: the AR metrics bind **10 distinct concepts, all 10 covered by active OCs.** At the concept-observability layer: **31 RESOLVABLE, 1 BLOCKED** (`average_clearance_time` — 1 concept with no OC), **19 NO-CONCEPT** (composites — 0 bound concepts; they consume upstream metrics, ADR #3, and resolve after their base metrics).
- **The gap is a reader-admission misalignment, and it is small.** The 10 needed concepts come from **`BSAD` (7 concepts), `TYPE_SD_S_MAP` (3), `KURGV` (1)`**. The AR reader binds `TYPE_SD_S_MAP` ✅ but **NOT `BSAD` or `KURGV`**, and instead binds 7 entities (`BSID`, `BKPF`, `FAGLPOSE`, `I_BillingDocument`, `CustomerOpenItemSet`, `RVKRED_TS_POST_FLE`, `SGLPOS_C_CT`) that provide **zero** needed concepts. The reader was configured (`apex` vintage) to admit the wrong entities.

**Corrected pilot target (supersedes the "only ARPI" framing):** the fix is **bind `BSAD` + `KURGV`** (8 of 10 concepts) + wire their per-entity OCs → **31 base AR metrics become resolvable**; the 19 composites follow (ADR #3); only `average_clearance_time` stays blocked (needs 1 OC). This is a 2-entity admission alignment, not an 8-OC authoring effort.

**Caveat — RESOLVED (P0, 2026-07-01, verdict PASSED).** The open-vs-cleared check is done: the as-of family (`ar_balance`, `ar_aging_*`, open-count) computes open-at-P *from* `BSAD` via `closing_field=clearing_date` (an item now cleared was open at any P before its clearing date — the SAP bitemporal pattern), so `BSAD`-sourcing is semantically correct, not a mismatch; `BSID` is the vestigial binding. The due-date family (`overdue_*`) depends on the DERIVED `due_date = date_add(posting_date, net_payment_term_days)` (active `cc__customer_invoice_arpi_slice` v8), with `BSAD` supplying the inputs (`BUDAT`, `ZBD1T`) — not the raw `ZFBDT` (a baseline-vs-due mislabel in `oc__receivable_posting_bsad` to reconcile). Residual scope: `BSAD` = cleared history, complete for a **closed historical pilot period**; a current-period pilot would need a `BSID` OC for still-open items. The 31-base-metric target holds. Full note in `pilot-e2e-readiness-consolidated-plan-2026-07-01.md` §3 P0.

## 18. Two axes, one program

The Reader program now has two axes: **Part 1 — runtime** (resumability/idempotency, evidence completeness, status honesty) and **Part 2 — authoring** (subfunction doctrine, four-layer model with per-entity OC, the five policies, the authoring service). Both feed the ADR sequence (§9), which grows to include: **Reader authoring surface & the four-layer model** (per-entity OC binding + the activation/completeness gates) — arguably the *most foundational* ADR, because it is where reader correctness enters the system. AR is the first slice of both axes.

## 19. Part 2 independent audit refinements (Codex, 2026-07-01) — accepted

Confirmed the load-bearing Part-2 claims and corrected four; the study above is revised to match.

1. **Per-entity OC binding — confirmed.** The only runtime OC pointer is `reader_flavor.observation_contract_id` (`schema/runtime/reader.ts:67`), 0 populated live; no `(flavor_id, source_entity) → OC` table exists. (`observation_field_map.source_entity` in `schema/contract/observation-contract.ts:96` is per-field-map metadata *inside* an OC — not a runtime binding keyed to reader bindings.)
2. **AR coverage / only-ARPI-coherent — confirmed** (8 bound entities, only `TYPE_SD_S_MAP` OC'd; OCs target `TYPE_SD_S_MAP`/`BSAD`/`KURGV`/`RBKP`).
3. **Activation/completeness gates absent — confirmed + located:** `createFlavor` accepts a flavor with a null OC (`reader.service.ts:221`; persisted `observationContractId: null` at `reader.repository.ts:365`); `bindReader` (`reader.service.ts:353`) checks only duplicate active AC binding, not OC coverage or SO→CO resolvability. This is exactly how an `active` reader admits 7/8 entities with no OC path.
4. **"Creation is CRUD" — nuance.** Beyond thin `createReader`, there is `createReaderFromOc` (`reader.service.ts:623`) — an OC-driven path that creates *draft* readers/flavors, still one-OC-per-flavor. It is more than CRUD but is not the governed per-entity authoring surface Part 2 targets.
5. **Subfunction doctrine overstated → corrected (§13).** `reader.subfunction == metric.subfunction` is not exact: active AR metrics span `accounts_receivable` + `billing` + `credit_and_collections`, but only `accounts-receivable-reader` exists. Subfunction is the owning container; the reader taxonomy is coarser/incomplete vs the metric taxonomy.
6. **Seed provenance — corrected.** The checked-in `seed-registry-full.ts:449` still names readers `ar-invoice-reader` etc., while live is `accounts-receivable-reader` — so the current seed file does not explain live state; DB facts are authoritative, the seed file is not cited as provenance.
7. **Added policy 6** (§15): environment/flavor binding consistency (AR mixes `development`/`apex`, dup `CustomerOpenItemSet`, null `flavor_id`, draft+active flavors).

Verified counts (live `bc_platform_dev`): SC 30,370 (30,369 active + 1 draft); AC 30,369 (30,368 active + 1 draft); OC 6 (6 active + 6 superseded); `runtime.reader` 24; flavors with an OC = 0. SC/AC bulk is auto-generated (`sc__ecc__a151`, `ac__ecc__a151`, …). Per-entity OC binding assessed as the right fix: current live flavors each bind ≤1 active entity (so one-flavor-one-entity holds *today*), but the AR-family metric chain requires one flavor to observe ≥2 entities (`BSAD` + `KURGV` + `TYPE_SD_S_MAP`), which the single-OC-per-flavor model cannot express — a capability requirement, not a current-state count (aligned with ADR #R1 F4).
