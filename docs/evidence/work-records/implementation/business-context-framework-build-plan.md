---
uid: business-context-framework-build-plan
title: Business Context Framework (BCF) — Gap-Pass Build Plan
description: Mechanics document translating BCF inventory verdicts (2026-05-18) and ADR-149ab2 (DEC-149ab2 / D411, decided) positions into a build order with T-shirt effort sizing. Scope-1-only first delegation per ADR Q1. DEC-02f5a9 (Business Concept Registry, D414) re-scopes this plan — see §16. Not an authority document — every work item cross-references the ADR position or inventory row that authorizes it.
status: draft
date: 2026-05-19
project: bc-docs
domain: contracts
subdomain: catalog
focus: implementation
---

# Business Context Framework (BCF) — Gap-Pass Build Plan

## What this is

The mechanics document that translates **inventory verdicts** (`business-context-framework-inventory.md` with 2026-05-18 narrow update) and **ADR-149ab2** decisions (DEC-149ab2 / D411, status `decided`) into a build order with T-shirt effort sizing.

## What this is not

- **Not an authority document.** Authority landed in ADR-149ab2. Every work item below cross-references the ADR position (Q1–Q9) or inventory row that authorized it. No build item creates new authority.
- **Not a code-level estimate.** T-shirt sizes only. Hour/day estimates are premature precision at this stage and will mislead.
- **Not a re-scoping of the ADR.** If a later ADR amendment changes any Q1–Q9 position, this plan must be re-scoped. This plan is **tracking ADR-149ab2 at status `decided`**.
- **Scope 2 (CF) and Scope 3 (BF↔CF mapping) no longer exist.** DEC-02f5a9 (§16) collapses Canonical Field into the one Business Concept and eliminates the BF↔CF mapping — they are not deferred scopes, they are retired by the Registry model. §6 F1–F4 are mooted.
- **Not in scope for legacy BF reconciliation.** The 4,769 non-clean-state BFs are subsumed by the greenfield rebuild (DEC-02f5a9 §16.1) — they are not re-authored against the Registry, so there is nothing to reconcile. The earlier sibling-ADR-after-90-days plan (§6 F5) is mooted.
- **Not in scope for MCF.** Sibling document; separate build-plan.

## Effort sizing convention

| Size | Meaning |
|---|---|
| **XS** | Obvious change, isolated to one file/table, no design pass needed |
| **S** | Clear path, single concern, single owner, no cross-service coordination |
| **M** | Multi-concern, needs a short design pass, single owner, no cross-service coordination |
| **L** | Multi-owner or cross-service coordination required; needs a design pass that touches more than one repo |
| **XL** | Requires ADR amendment, Foundation validation, or spans data + service + UI + bc-ai |

Sizes are perceived complexity / scope, not hours. Two L items in sequence ≠ one XL item.

## Phase model

The plan groups work into seven phases by dependency order. Phases can overlap where the dependency graph permits (§7 dependency graph). **Build order is the dependency graph, not the phase letter** — DEC-02f5a9 (§16) inverts the order: the Registry substrate (Phase F) is built first, the greenfield cutover (Phase G) last.

| Build order | Phase | Theme | Why this order |
|---|---|---|---|
| 1 | **Phase F — Registry substrate** | Entity / Property / Business Concept store, identity constraints, authoring service (§16.2) | The Registry is the thing being governed; nothing downstream can author against it until it exists |
| 2 | **Phase A — Governance substrate** | `panel_output_record`, `framework_policy`, `operator_confirm_rule`, `calibration_event`, phase tracker (A5/A8/A9/A10/A13/A14) | The governance machinery; governs whatever the vocabulary is. A1–A4 are interim — see §1 |
| 3 | **Phase B — Panels** | Unified Registry Authoring Panel; Publication Panel; Lifecycle Audit Panel — built against the Registry | A panel cannot author Registry concepts before Phase F exists |
| 4 | **Phase C — bc-core orchestration** | Framework Approval, intake routing, operator override | Bridge between substrate and runtime authoring |
| 5 | **Phase D — Operator UI** | Activity / Calibration dashboards, detail views, override, rejection log | Phase 0 routes 100% to operator review → operator needs usable surfaces |
| parallel | **Phase E — Parallel tracks** | candidate-source pull, helper-script audit | Independent; can run alongside any phase |
| last | **Phase G — Greenfield cutover** | Re-author OC / CC / MC against the Registry; coordinated discard (§16.2) | Runs only after Phase F and the re-authored contracts are ready |

The five Scope-1 build-plan prerequisites named in the ADR-149ab2 Consequences map to Phases A, C, and D. Under DEC-02f5a9 (§16) "Scope 1" is no longer a separate scope — it is the one Registry — but the prerequisite items themselves still hold.

---

## 1. Phase A — Governance substrate

> **DEC-02f5a9 split.** Phase A splits under the Business Concept Registry (§16). **A5, A8, A9, A10, A13, A14** are surviving governance substrate — they govern whatever the vocabulary is and carry forward unchanged. **A1–A4** (the `governance.state` / `quarantine_marker` columns on `business_field` / `business_object`) are **completed interim / physically transitional / retired by Phase G** — no further strategic investment. The 4,769-quarantined-BF reconciliation is subsumed by the greenfield rebuild (§16.1); §6 F5 is mooted. In the dependency graph Phase A is built after Phase F (Registry substrate).

| ID | Item | ADR / inventory citation | T-shirt | Depends on |
|---|---|---|---|---|
| **A1** | Add `governance.state` column to `contract.business_field` and `contract.business_object`; populate from existing `status_code` + `catalog_state_code` pair via the Foundation lifecycle mapping (draft, review, approved, active, superseded) | ADR Q3 | M | — |
| **A2** | Add `quarantine_marker` column to `contract.business_field` (and `business_object` where applicable); populate for the 4,769 non-clean-state BFs per inventory §1.2 breakdown (4,745 + 11 + 12 + 1) | ADR Q2 | S | A1 |
| **A3** | Add deterministic-mapping function from existing dual columns to `governance.state`; document the 4 non-clean pairs that map to quarantine rather than to a Foundation state | ADR Q2, Q3 | S | A1, A2 |
| **A4** | Deprecate dual-column read paths in bc-core registry services (`standard-field.repository.ts`, `business-object.repository.ts`, etc.); add deprecation warning; do not drop columns yet | ADR Q3 | M | A1 |
| **A5** | Create `panel_output_record` table — append-only; columns include `panel_run_uid` (PK), `stage_code`, `prompt_version`, `model_identity_json` (per-agent provider+version+role), `input_hash`, `verdict_code`, `verdict_payload_json`, `grounding_check_result`, `quarantined` (bool), `sampling_status`, `policy_version`, `created_at`. Replicated per NF1. | ADR Q4 | M | — |
| **A6** | Extend `contract.certification_record` with the BCF NF1 fields: `panel_run_uid` (FK → panel_output_record), `prompt_version`, `model_identity_json`, `input_hash`, `policy_version`, `sampling_status`, `grounding_check_result` | ADR Q4 | S | A5 |
| **A7** | Backfill plan for existing 3,493 certification_record rows: cited as `legacy_pre_bcf` in panel_run_uid (nullable FK); inventory §2.8 already classifies the table as adapt | ADR Q4; inventory §2.8 | S | A6 |
| **A8** | Create `framework_policy` table — versioned; columns include `policy_uid`, `policy_version`, `scope_code`, `eligible_operations_json`, `consensus_requirement_json`, `sampling_rate`, `operator_confirm_rules_uid_list`, `notification_policy_json`, `calibration_regression_thresholds_json`, `effective_from`, `effective_to` (nullable), `adr_ref` | Requirements Chapter 7; ADR Q5 (Phase 0/1/2 ladder configured here) | M | — |
| **A9** | Create `operator_confirm_rule` table — columns per ADR Q8 grammar: `rule_uid`, `scope`, `transition`, `predicate_ast_json`, `action_code`, `rationale_required` | ADR Q8 | M | A8 |
| **A10** | Implement predicate AST parser + evaluator for the v1 closed-form grammar (attribute equality / null-check, set membership, registered built-in cohort signals, panel-output signals, composition signals, numeric comparison, AND/OR/NOT); enforce the v1 disallows (no subqueries, joins, UDFs, write actions) at parse time | ADR Q8 | L | A9 |
| **A11** | Register the v1 built-in cohort signals (e.g. `cohort:importers_with_recent_high_reject_rate`); each signal is versioned and registered alongside the policy | ADR Q8 | S | A10 |
| **A12** | Create REJECT defect-code closed enum + DB CHECK on `panel_output_record.verdict_payload_json` → `defect_code` field when verdict is `REJECT`; v1 codes per ADR Q7 (9 codes: DEF_PLACEHOLDER, DEF_RATIONALE, DEF_BOILERPLATE, IDENT_NAME_SPLITTER, IDENT_SOURCE_SUFFIX_LEAK, IDENT_TAUTOLOGICAL, PROV_FABRICATED, STRUCT_TYPE_INCOHERENT, STRUCT_FAMILY_UNIT_MISSING) | ADR Q7 | S | A5 |
| **A13** | Create `calibration_event` table — per panel output: AI verdict, sample-routed-to-operator (bool), operator decision when sampled, eventual downstream signal (e.g. supersession). NF7 load-bearing. | Requirements NF7; ADR Q5 | M | A5 |
| **A14** | Implement Q5 phase-state tracker: per scope per stage, count executions, compute Phase 0/1/2 thresholds, auto-pause on threshold breach (quarantine >5% per 100-rolling, override >0 in Phase 1, override >10% w-o-w in Phase 2). **Also monitors sample-review-age (F5) — an SLA breach feeds the F12 auto-pause path** (folded in 2026-05-20, §15). | ADR Q5; Requirements F5 | L | A8, A13 |

**Phase A total mass:** 5×S + 6×M + 3×L. Heavier on schema and rules infrastructure than on individual services.

---

## 2. Phase B — Panels (against the Registry)

> **DEC-02f5a9.** Phase B is built against the Registry (Phase F) — the panels author Registry concepts (Entities, Business Concepts), not BF/BO. The bc-ai support items (B1–B5, B8, B9) are vocabulary-agnostic and carry forward; B6/B7 are merged into one unified panel (see B6 below).

| ID | Item | ADR / inventory citation | T-shirt | Depends on |
|---|---|---|---|---|
| **B1** | Rename `AgentRole` enum: `GATE` → `MODERATOR` across `bc-ai/app/agents/base.py` and all call sites | ADR Q6 | S | — |
| **B2** | Implement input-hash mechanism: cryptographic hash of the row payload + seed/provenance bundle + policy version; passed to all three agents; recorded on `panel_output_record.input_hash`; consensus validator refuses outputs from agents whose computed input-hash differs | Requirements Chapter 7 "Same input snapshot"; inventory §3.4 | M | A5 |
| **B3** | Promote no-fabrication grounding check from per-agent prompt concern to shared system invariant; outputs failing the check are marked `quarantined: true` in `panel_output_record` and excluded from approval action | Requirements Chapter 7; inventory §3.4 | M | A5 |
| **B4** | Implement panel-output emitter from bc-ai → bc-core: writes `panel_output_record` row with the full NF1 field set on every panel run | ADR Q4; Requirements NF1 | M | A5, B2 |
| **B5** | Closed-enum verdict harmonization: bc-ai agents emit verdict codes from the BCF closed lists (REJECT defect codes per A12; APPROVE codes per stage to be defined in a separate ADR amendment); shared library between agents | ADR Q7 | S | A12 |
| **B6** | **Unified Registry Authoring Panel** (DEC-02f5a9; replaces the separate BF/BO Authoring Panels — old B6 + B7). A purpose-built `bcf-authoring-panel` Maker/Checker/Moderator trio over a Registry intake candidate. **Subject:** Registry intake candidates. **Judges:** entity placement, property placement, concept identity (synonym / homonym against governed terms), definition discipline, provenance, and whether new governed terms require operator confirm. **Outcomes:** `APPROVE_FOR_DRAFT` / `REJECT` + `defect_code` / `OPERATOR_REVIEW`. One panel, not separate Entity and Concept panels — concept placement is a single judgment; a split would recreate the cross-scope coherence problem DEC-02f5a9 eliminates. The legacy `bf_dedup` / `bf_pii_classify` / `bo_dedup` / `bo_composer` flows are narrow sub-checks that may feed it as input signals — they are not the panel. | DEC-02f5a9 §3, §10; Requirements Ch 7 (Stage 1) | L | F1–F5, B1–B5, B9 |
| **B8** | Calibration sampling enrollment in bc-ai: every panel run consults the Phase tracker (A14), records `sampling_status` on the panel output, routes to operator review if sampled | ADR Q5; Requirements NF7 | M | A13, A14, B4 |
| **B9** | Same-input-snapshot input-divergence detection: if any agent's recorded input-hash differs from the others, output is not consensus; routes to OPERATOR_REVIEW with `input_divergence` flag | Requirements F13 | S | B2, B4 |
| **B10** | **Context Publication Panel — Stage 2** (DEC-02f5a9 retarget). Runs the in-catalog lifecycle path `draft → review → approved → active` under Framework Approval for Registry concepts and entities — a distinct subject from the Authoring Panel (existing Registry rows, not the intake queue), judged against the deterministic publication eligibility gates and Registry coherence. Needs the per-stage APPROVE verdict vocabulary pending the ADR amendment named in B5. | Requirements Ch 7 (Stage 2) | L | B6 |
| **B11** | **Context Lifecycle Audit Panel — Stage 3** (DEC-02f5a9 retarget). Periodic panel over `active` Registry concepts and entities detecting duplicate accretion, drift, stale provenance, and synonym / homonym regression; emits tickets / reports / supersession proposals for operator approval — it cannot mutate active artifacts. May be deferred behind Phase 0 go-live but must be tracked. | Requirements Ch 7 (Stage 3) | M | B6 |

**Phase B total mass:** 3×S + 5×M + 2×L (B6 + B7 merged into one unified panel). The **unified Registry Authoring Panel (B6) is the load-bearing deliverable** — the rename, emitter, and hash items exist to support it; it depends on Phase F.

> **B8 implementation note (2026-05-20, B8 PR 2).** The B8 row reads "Calibration sampling enrollment **in bc-ai**". As built, the sampling-policy decision is enforced in **bc-core, at B4a panel-output ingest** (`CalibrationSamplingService`), not in bc-ai. bc-core owns the three inputs the decision needs — A13 `calibration_event`, A14 `phase_state`, and the A8 `framework_policy` sampling rate — so having bc-ai query bc-core for the phase and echo `sampling_status` back would be unnecessary coupling. The draw, the A14 execution count, the Phase 0→1 advance, the `panel_output_record` insert and the `calibration_event` insert are one atomic bc-core transaction. bc-ai still emits the panel run; the `samplingStatus` field on the B4a DTO is accepted for wire compatibility but ignored server-side (deprecation is a B8 follow-up). This is a build-plan re-version, not an ADR change — ADR-149ab2 Q5 fixes the calibration ladder, not the host. B8 PR 2 also lands the A14 tracker's execution-counting + Phase 0→1 advance (build-plan A14); auto-pause and the Phase 1→2 advance — whose ADR Q5 entry gate needs the operator-override signal — remain later slices.

---

## 3. Phase C — bc-core orchestration

> **DEC-02f5a9.** C5–C13 are vocabulary-agnostic governance orchestration and carry forward. **C1–C4** (`oagis-onboarding` disposition, `standard-field` → `business-field` rename, `business-object` adapt, `canonical-field` adapt) are BF/BO/CF-service work superseded by the Registry authoring service (Phase F, item F3) — **interim, retired by Phase G; no further strategic investment** (cf. the §1 Phase A split).

| ID | Item | ADR / inventory citation | T-shirt | Depends on |
|---|---|---|---|---|
| **C1** | OAGIS auto-cert call-site disposition (G1): break the `bulkCertifyFields(..., true)` invocation in `oagis-onboarding.service.ts:300`. Import lands rows at `governance.state='draft'` (per A1) requiring evidenced gating; **never** at `certified`. Inventory verdict: adapt / deprecate the call site (independent of `standard-field.service.ts`) | Inventory §2.1 oagis-onboarding row; FEM F1 | M | A1, A3 |
| **C2** | `standard-field.service.ts` vocabulary rename to `business-field.service.ts`: method renames (`admitBfFromCorrectionRequired` → `publishBfFromCorrectionRequired`, etc.), endpoint renames in `standard-field.controller.ts`, type renames | Inventory §2.1 standard-field row; ADR D3 cleanup | L | A4 |
| **C3** | `business-object.service.ts::approveObject` adapt: **BF-composition approval remains BF-scoped per ADR guardrail; no CF check added here.** Scope of adapt is vocabulary + Framework Approval integration only; minimum-composition rule re-enforcement (4 BF default per Requirements Chapter 12 SHOULD list) | Inventory §2.2; ADR guardrail confirmed in gap-research §9.1 | M | A8, A9 |
| **C4** | `canonical-field.service.ts` adapt for Scope 1 boundary: vocabulary rename only in this phase (Scope 2 lifecycle activation is deferred per ADR Q1). Reference-time enforcement at MC activation is already in place (G6a closed); no change to `contract.service.ts:70/128-154` | Inventory §2.3; gap-research §8.3 G6a closed | XS | — |
| **C5** | Framework Approval orchestration in standard-field / business-object services: when Phase 0 conditions met (consensus + grounding + sampling + authoring record), service writes the approval action; when conditions fail, routes to OPERATOR_REVIEW table. **Bounded-write conditions also include (folded in 2026-05-20, §15): N23 — route to OPERATOR_REVIEW when the operator override mechanism is paused / broken / unavailable; N15 — validate every framework write against Foundation Contract Grammar schemas before commit.** | ADR Authority; Requirements Chapter 7 "Bounded-write discipline", N15, N23 | L | A5, A6, A8, A14, B4 |
| **C6** | Operator-confirm gate wiring: before any AI-driven transition, service evaluates matching `operator_confirm_rule` rows via the parser (A10); matching rules route to confirm-required queue rather than executing | ADR Q8 | M | A9, A10, C5 |
| **C7** | Operator override action endpoints (one per scope): edit-non-active and supersede-active; both require operator rationale text per N29 | Requirements Chapter 6; N29 | M | A6, C5 |
| **C8** | Intake queue table + service: pre-catalog state; aging timer; routes to REJECT / OPERATOR_REVIEW / APPROVE_FOR_DRAFT per Requirements Chapter 4 | Requirements Chapter 4 | M | A5 |
| **C9** | Authoring Panel Rejection Log table + service: REJECT-eligible rejections per A12; operator override path to advance entry from rejection log to `draft` with `manual_override_after_reject` provenance | Requirements Chapter 4, 6, 7 | S | A12, C8 |
| **C10** | N30 anti-coverage-KPI enforcement substrate: shared library that any approval-volume API response must consult and pair with calibration metrics from `calibration_event`; refusing-to-serve is the failure mode | ADR Q9 | M | A13 |
| **C11** | **PE1–PE6 deterministic publication gate** (added 2026-05-20, §15) — bc-core, refuse-only. Deterministic verification of provenance / anchoring / fetchable `standard_ref` / semantic family / type-unit coherence / definition discipline before `review → approved`. Distinct from the Publication Panel (B10, the AI judgment) and from C5 (orchestration): Ch 4 makes it a separate condition — "Publication Panel APPROVE consensus **+** PE1-PE6 deterministic publication gate pass". | Requirements Chapter 3 (PE1–PE6), Chapter 4 | M | A8, B10 |
| **C12** | **Framework-policy validator** (added 2026-05-20, §15) — bc-core, config-time. Rejects at save any `framework_policy` that grants authority outside the three scopes or violates Rules 1/2/3; hard-reject with the cited rule. | Requirements Chapter 9 F15 | S | A8, A10 |
| **C13** | **Failure-mode monitors** (added 2026-05-20, §15) — bc-core scheduled jobs: F1 source-drift detection (source-schema scanner diffs → tickets), F2 provenance-decay link-check on active members, F14 panel-output integrity check + the NF1 cross-storage replication guarantee. | Requirements Chapter 9 F1/F2/F14; NF1 | M | A5 |

**Phase C total mass:** 1×XS + 2×S + 8×M + 2×L. bc-core is the largest mass.

---

## 4. Phase D — Operator UI (bc-admin)

All Phase D items honour the N30 anti-coverage-KPI rule (C10) — every approval-volume display pairs with calibration metrics on the same surface.

> **DEC-02f5a9.** Phase D surfaces retarget to Registry concepts and entities — the BF / BO detail pages (D2, D3) become Registry-concept and Entity detail pages; D12 (`CanonicalFieldsPage`) is mooted (no separate Canonical Field). The surfaces themselves are vocabulary-agnostic; the per-item retarget is ordinary maintenance (§16.4).

| ID | Item | ADR / inventory citation | T-shirt | Depends on |
|---|---|---|---|---|
| **D1** | Activity Dashboard (gap): stream of AI activity, filterable by scope, member, action, lifecycle transition, panel verdict, sampling status, policy version | Inventory §4.2; Requirements Chapter 6 | L | A5, A13, C5, C10 |
| **D2** | Per-Member Detail View for BF — extend `BusinessFieldDetailPage.tsx` (adapt): panel transcript viewer, version history, override action surface, calibration sampling marker, Framework Approval indicators | Inventory §4.1; Requirements Chapter 6 | L | A5, A6, C7 |
| **D3** | Per-Member Detail View for BO — extend `BusinessObjectDetailPage.tsx`: same shape as D2 | Inventory §4.1 | M | A5, A6, C7 |
| **D4** | Panel Transcript Viewer (gap): Maker / Checker / Moderator transcripts side-by-side for any panel run UID; reads stored `panel_output_record` per Foundation Invariant V (audit MUST NOT re-invoke panels) | Inventory §4.2; Requirements Chapter 7, NF8 | M | A5, B4 |
| **D5** | Override Action surface (gap): one-action edit (non-active) or supersede (active) flow; emits authoring record with operator rationale text per N29 | Requirements Chapter 6 | M | C7 |
| **D6** | Authoring Panel Rejection Log UI (gap): browse intake-queue REJECT entries, operator override to advance to draft | Inventory §4.2; Requirements Chapter 4, 6 | M | C9 |
| **D7** | Operator-confirm UI (gap): pending operator-confirm queue, present AI verdict + provenance, operator yes/no + rationale | Inventory §4.2; Requirements Chapter 6 | M | C6 |
| **D8** | Calibration Dashboard (gap): per-scope per-stage precision over time, AI-approval-vs-operator-override rate per member, sampling outcomes, calibration regression alerts. **N30 hard requirement**: every approval-volume number paired with calibration. **Also surfaces the NF5 cost dashboard — per-member / per-stage / per-policy AI cost breakdown** (folded in 2026-05-20, §15). | Inventory §4.2; Requirements NF5, NF7; ADR Q9 | L | A13, A14, C10 |
| **D9** | Policy Management UI: configure per-scope policy (sampling rate, operator-confirm rules, notification rules); pause/resume; modify-and-version per Requirements Chapter 7. **Also implements the Chapter 7 sunset cadence — quarterly review and auto-disable of a policy not re-affirmed within its window** (folded in 2026-05-20, §15). | Inventory §4.2; Requirements Chapter 6, 7 | L | A8 |
| **D10** | Reference Impact Viewer (gap): when operator considers superseding, show downstream impact (CCs, MCs in MCF scope, ICs, Contract Bindings). Chain-status data exists per D305; visualization gap | Inventory §4.2 | M | — (uses existing chain-status) |
| **D11** | Operator Notifications (gap): configurable real-time / digest / threshold-based; per-policy and per-member rules | Inventory §4.2; Requirements Chapter 6 | M | A8, D9 |
| **D12** | `StandardFieldsPage.tsx` rename to `CanonicalFieldsPage` and vocabulary alignment — **NOT activated for Scope 1**; deferred to Scope 2 amendment per ADR Q1 | Inventory §4.1; ADR Q1 sub-deferral | — | (deferred, listed for traceability) |
| **D13** | Phase 0 operator-load support: D1, D2, D3, D5, D6 are the **minimum surfaces required** for Phase 0's 100%-sample workload per ADR Consequences §What changes line 1(d) | ADR Consequences | — | (no item; flag on D1, D2, D3, D5, D6) |
| **D14** | **Activity Log surface** (added 2026-05-20, §15) — bc-admin. Full immutable history: panel calls, gate results, AI actions, operator actions, policy changes, calibration events (Chapter 6 surface; NF6 unified event log). D1 covers only the AI-activity stream; the substrate is A5 + A6 + A13 **plus** operator-action (C7) and policy-change (D9) events, which those items must emit. | Requirements Chapter 6, NF6 | M | A5, A6, A13, C7 |
| **D15** | **Operator Authoring Tool** (added 2026-05-20, §15) — bc-admin. Operator-initiated authoring surface that produces an intake-queue entry; AI then takes over per default (Chapter 6). | Requirements Chapter 6 | M | C8 |

**Phase D total mass:** 4×L + 9×M. UI is large because most surfaces are gaps. (D12/D13 carry no size — deferred / flag-only.)

---

## 5. Phase E — Parallel tracks

These items are independent of Phases A–D and can start at any time.

| ID | Item | ADR / inventory citation | T-shirt | Depends on |
|---|---|---|---|---|
| **E1** | bc-seed operational pull (G21): coverage report on `seed_oagis_components` vs BCF-needed OAGIS Nouns; update cadence audit; version-tracking shape; produce operational-state document so the inventory's "keep-as-substrate + wrap, provisional" can drop the "provisional" qualifier | Inventory §6, §2.7; gap-research G21 | M | — |
| **E2** | Per-script trust audit of `bc-core/scripts/*` (G24): produce per-file classification beyond the 138/156 scope number; each script gets `trusted` / `untrusted` / `quarantined` verdict + rationale; default remains untrusted | Inventory §2.9; gap-research G24 | L | — |
| **E3** | bc-seed wrapper service (per inventory §2.7 wrap path): lineage metadata on every returned candidate, coverage tracking, currency/fetchability validation per PE3, version metadata | Inventory §2.7 oagis-seed row | L | E1 (informs scope) |

**Phase E total mass:** 1×M + 2×L. E1 + E2 can start day 1; E3 follows E1.

---

## 6. Deferred work (out of scope for Scope 1 first delegation)

Listed for traceability so the gap-pass document is complete, not because these are next.

> **DEC-02f5a9.** F1–F5 are **mooted** — Scope 2/3 (the CF and BF↔CF-mapping work F1–F4 deferred) no longer exist under the Registry, and the quarantined-BF reconciliation (F5) is subsumed by the greenfield rebuild (§16.1). F8 (Foundation amendment proposals — BF/CF collapse, BO necessity) is **resolved** by DEC-02f5a9. The table is retained as the dated record.

| ID | Item | Why deferred | Activation gate |
|---|---|---|---|
| **F1** | `cc-onboarding.service.ts` CF trust check at mapping write (G6b live gap) | Scope 3 (BF↔CF mapping) deferred per ADR Q1 | ADR amendment to activate Scope 3 |
| **F2** | `cc-onboarding.service.ts` Meaning-once write-time check (G7 live gap) | Same | Same |
| **F3** | `canonical-field.service.ts` lifecycle activation (operationally non-dormant) | Scope 2 (CF) deferred per ADR Q1 | ADR amendment to activate Scope 2 |
| **F4** | `field-mapping.service.ts` and `canonical-wizard.service.ts` adapt | Inventory says keep/adapt; Scope 2/3 deferred | ADR amendment |
| **F5** | Legacy reconciliation of the 4,769 quarantined BFs (Option A locked freeze; downstream choice between supersede/reconcile/restart) | Sibling ADR after 90 days of BCF calibration data | 90-day calibration data accumulated |
| **F6** | Cross-family provider-diversity for high-stakes panels | **Largely delivered 2026-05-20** — bc-ai PR #12 locked the cross-family roster (Maker=Gemini, Checker=OpenAI GPT-5.5, Moderator=Claude Opus 4.5). The `bf_admission_review` endpoint formerly tracked here is **not** a separate deferred item — it is the real Authoring Panel, now correctly scoped as B6/B7 (see §14). | (roster done; panel = B6/B7) |
| **F7** | MCF (Metric Context Framework) sibling document and build-plan | Out of BCF scope per Requirements; D7 deferral | MCF requirements draft |
| **F8** | Foundation amendment proposals (D2 — BF/CF collapse, BO necessity, etc.; D5 — direct CO→IC triggers) | Carried forward unchanged per ADR non-decision #8 | Operator decision |

---

## 7. Dependency graph (read-order)

> **SUPERSEDED — the graph and critical path in this §7 are NOT current.**
>
> They are the pre-DEC-02f5a9 build order, retained only as the prior record (cf. the §14 correction pattern). **The authoritative dependency graph and critical path are §16.5** — build order Phase F → A → B → C → D, E parallel, G last. Do not plan against the graph below.

```
Phase A — Substrate
  A1 (governance.state) ──┬──> A2 (quarantine_marker) ──> A3 (mapping fn) ──> A4 (deprecate dual-column reads)
                          │
  A5 (panel_output_record) ──┬──> A6 (certification_record extension) ──> A7 (backfill plan)
                              │                                              
                              ├──> A12 (REJECT defect-code enum + CHECK)    
                              └──> A13 (calibration_event)                  
                                                                            
  A8 (framework_policy) ──┬──> A9 (operator_confirm_rule) ──> A10 (predicate parser) ──> A11 (built-in cohort signals)
                          └──> A14 (phase-state tracker) ←── A13            

Phase B — bc-ai (starts after A5, A12, A13 available)
  B1 (Gate → Moderator) ── independent ──
  B2 (input-hash) ──> B3 (grounding check) ──> B4 (panel-output emitter) ──> B5 (closed-enum verdict)
  B4 + B2 ──> B9 (input divergence)
  A14 + B4 ──> B8 (calibration sampling enrollment)
  B1..B5 + B9 ──> B6 (BF Authoring Panel)   ← the BCF product; on the go-live critical path
                  B7 (BO Authoring Panel)
  B6 + B7 ──> B10 (Publication Panel, Stage 2)
              B11 (Lifecycle Audit Panel, Stage 3)

Phase C — bc-core (starts after A-substrate + B-emitter)
  A1 + A3 ──> C1 (oagis auto-cert disposition)
  A4 ──> C2 (BF service rename)
  A8 + A9 ──> C3 (BO adapt)
  C4 (CF vocab) — XS, independent
  A5 + A6 + A8 + A14 + B4 ──> C5 (Framework Approval orchestration)
  A9 + A10 + C5 ──> C6 (operator-confirm gate wiring)
  A6 + C5 ──> C7 (override action endpoints)
  A5 ──> C8 (intake queue) ──> C9 (rejection log)
  A13 ──> C10 (N30 enforcement substrate)
  A8 + B10 ──> C11 (PE1–PE6 deterministic publication gate)
  A8 + A10 ──> C12 (framework-policy validator)
  A5 ──> C13 (failure-mode monitors)

Phase D — Operator UI (starts after A + B + C have produced data sources)
  A5 + A13 + C5 + C10 ──> D1 (Activity Dashboard)
  A5 + A6 + C7 ──> D2 (BF detail) + D3 (BO detail)
  A5 + B4 ──> D4 (Panel Transcript Viewer)
  C7 ──> D5 (Override Action)
  C9 ──> D6 (Rejection Log)
  C6 ──> D7 (Operator-confirm UI)
  A13 + A14 + C10 ──> D8 (Calibration Dashboard)
  A8 ──> D9 (Policy Management)
  D9 + A8 ──> D11 (Notifications)
  D10 (Reference Impact) — independent (uses existing chain-status)
  A5 + A6 + A13 + C7 ──> D14 (Activity Log surface)
  C8 ──> D15 (Operator Authoring Tool)

Phase E — parallel tracks (no dependencies on A–D)
  E1 (bc-seed pull) — independent
  E2 (script audit) — independent
  E1 ──> E3 (bc-seed wrapper service)
```

**Critical path.** Superseded by DEC-02f5a9 — the authoritative critical path is **§16.5**. The pre-DEC-02f5a9 path (`A5 → B2 → B3 → B4 → B6 → C5 → C8 → D6 → Phase 0`) routed Phase 0 over BF/BO authoring; under the Registry the path is headed by Phase F (Registry substrate), then the unified Registry Authoring Panel. The §14 lesson holds — the product's core deliverable (the unified panel, B6) stays on the stated path, and a consumer is never marked complete before its producer (now Phase F).

---

## 8. Sequencing rationale

> **DEC-02f5a9.** The rationale below predates the re-scope. Build order is now Phase F (Registry substrate) first — see §16 and §16.5. The Phase A / Phase B / operator-UI rationale still holds *within* the re-sequenced order; "Phase A first" now reads "Phase F first, then the Phase A governance substrate."

**Why Phase A first.** Schemas and rule infrastructure cannot lag service work. The 462 placeholder certifications (FEM F2) and the 4,769 non-clean-state legacy pairs (inventory §1.2) are evidence that landing services on top of an unfixed substrate produces the same defect. Foundation Invariant VI (evidence emitted, not inferred) is unsatisfiable until `panel_output_record` exists.

**Why Phase B before C5.** `C5` (Framework Approval orchestration) is the bridge service that writes approvals only when the bounded-write discipline (Requirements Chapter 7) holds. That discipline requires the input-hash mechanism (B2), grounding check (B3), and panel-output emitter (B4) to be in place. Without them, C5 cannot reliably refuse to execute when the discipline fails — which is the entire purpose of the discipline.

**Why operator UI minimum (D13) is part of Phase 0 prereqs.** ADR Q5 Phase 0 routes 100% of AI actions to operator review. Without D1 (Activity Dashboard), D2/D3 (Per-Member Detail), D5 (Override Action), and D6 (Rejection Log), the operator cannot do that work. Phase 0 cannot start until D13's five surfaces are usable.

**Why E1/E2 are parallel.** They are independent prerequisites for downgrading the inventory's `provisional` qualifier (E1) and lifting the `default-untrusted` classification on helper scripts (E2). Neither blocks Phase A–D. Starting them on day 1 means evidence is accumulating while substrate work proceeds.

**Why Scope 2/3 work is deferred not pre-staged.** ADR Q1 makes Scope 2/3 conditional on G6b + G7 substrate gaps. Pre-staging F1–F4 work would (a) consume effort before the activation ADR amendment has been filed and (b) risk re-scoping if the amendment shifts position. Phase E is for unconditional parallel work; F-items are conditional.

**Why no schedule, just dependency order.** Effort sizing is judgement-bound; calendar conversion is premature precision. The plan above is a graph, not a Gantt. Operator decides which nodes to staff first within the graph's constraints.

---

## 9. Tooling/script verification work required per prereq

Per G24 (helper-script default-untrusted), any script used in delivering an A/B/C/D/E item must pass a per-script audit before its output is treated as verification. Specific tooling touch points:

| Build item touching scripts | Required per-script audit |
|---|---|
| A1, A2, A3 — migration scripts populating `governance.state` and `quarantine_marker` | Schema-version and tenant assumptions; idempotency under retry; dry-run mode mandatory |
| A7 — certification_record backfill | Same; plus row-count invariants pre/post |
| E1 — bc-seed pull script | New script; no existing artefact to audit; must follow N30 (volume of OAGIS Nouns must be paired with coverage-gap metric) |
| E2 — the audit itself produces the script trust catalog | Bootstrap concern: the audit script auditing scripts must itself be approved |

---

## 10. Tracking against ADR-149ab2

This plan tracks ADR-149ab2 at status `decided` (DEC-149ab2 / D411). If a later ADR amendment changes any Q1–Q9 position, the affected build items must be re-scoped:

| ADR position change | Affected build items |
|---|---|
| Q1 changes (Scope 1 not first, or Scope 2/3 added) | C2, C3, C4 scope changes; D12 activates; F1–F4 promote out of deferred |
| Q2 changes (legacy reconciliation method) | A2, A3 rework; F5 promotes out of deferred |
| Q3 changes (keep two columns with invariant) | A1, A4 cancel; new invariant-enforcement work added |
| Q4 changes (no panel_output_record; single-table extension) | A5, A6 collapse into single item |
| Q5 changes (different phase model) | A14, B8, D8 rework |
| Q6 changes (keep "Gate") | B1 cancel; vocabulary rework in this document and Requirements |
| Q7 changes (different defect codes) | A12, B5 rework |
| Q8 changes (different grammar) | A9, A10, A11 rework |
| Q9 changes (N30 dropped or reshaped) | C10, D1, D8 rework |

The build-plan is re-versionable; the ADR is the authority.

---

## 11. Out of scope (this build plan)

- **Hour or day estimates.** T-shirt only. Calendar conversion is the operator's call after staffing decisions.
- **Resource assignment.** No named owners. The plan is graph + sizes; staffing is operator scope.
- **Risk register beyond build-item callouts.** General BCF risks are in FEM and gap-research; per-item risks are in the table notes only.
- **Anything beyond Scope 1.** F-items are listed for traceability only.
- **MCF.** Sibling document.

## 12. Process commitments

- This plan is point-in-time (2026-05-19). If a later ADR amendment flips any position in DEC-149ab2, this plan is re-scoped (per §10 table) and re-versioned.
- The plan does not lock owners or calendars. It locks dependency order and relative scope.
- T-shirt sizes are intentionally coarse. Anyone re-estimating before staffing should produce a separate sizing document and not edit this one.
- Phase E items can and should start in parallel with Phases A–D; the plan does not require waiting.
- Every work item carries an ADR or inventory citation. If a citation cannot be produced, the item does not belong here — escalate to ADR amendment instead.

---

## 13. Execution discipline

The build-plan graph is necessary but not sufficient. The FEM is a catalogue of services that broke silently because consumer expectations weren't mapped, behavior wasn't characterized, defects shipped because nobody owned cleanup, and helper scripts were trusted as proof. This section codifies the execution harness that prevents the same failure modes during BCF build-out.

The harness has five parts: an execution rule, PR trailers (machine-checkable), two flavors of flag discipline, consumer-map shape with implicit assumptions, defect-characterization tagging, and a 9-question merge gate. **CI is the enforcement mechanism.** This document is the specification, not the gate.

### 13.1 Execution rule

**No behavior-changing PR merges unless it has:**

1. Required PR trailers (§13.2)
2. Consumer map with implicit assumptions captured (§13.4)
3. Characterization tests, tagged if they document defective behavior (§13.5)
4. Rollback path
5. Phase 0 workload impact assessment (§13.6 merge gate Q9)

Read/additive substrate PRs (e.g. Phase A1–A3, A5/A6, A8/A9, A12) are not "behavior-changing" in this sense — they add columns, tables, enums without modifying existing service behavior. They still carry trailers and Phase 0 impact but are exempt from consumer maps and characterization tests because there is no current behavior to map or characterize. A4 (deprecate dual-column read paths) **is** behavior-changing — adding a deprecation warning is a consumer signal — and the full rule applies.

### 13.2 PR trailers

Use git trailers, not a separate ledger document. A separate ledger becomes its own stale-doc problem (FEM F40 / FEEDBACK-no_stats_in_sops: `contract-chain-assembly.md` said "0 BFs, 0 BOs" while reality was 171/4,083). Trailers live with the commit, are machine-checkable, and cannot be skipped silently.

Two trailer tiers: **required** (CI-enforced; PR cannot merge without them) and **contextual** (operator-supplied when meaningful; reviewer-enforced per §13.7; not required by CI).

**Required trailers on every PR (CI-enforced):**

```
BuildPlan: <item ID, e.g. A1, A5, C1>
Finding: <inventory or FEM citation, e.g. G1, F25, none>
Rollback: <one-line path>
Phase0Impact: <none | increases | decreases>
```

**Contextual trailers (reviewer-enforced when relevant):**

```
ADR: <decision UID + position, e.g. DEC-149ab2 Q3>     # when the PR cites a specific ADR position
Consumers: <count mapped, see PR body §Consumer impact># when the PR modifies a service with consumers
Characterization: <test path>                          # when the PR is behavior-changing (per §13.1)
```

CI rejects PRs missing any of the 4 required trailers. CI does not enforce contextual trailers — reviewers do, per §13.7. Reviewers expect `Consumers:` + `Characterization:` on behavior-changing PRs (§13.1); reviewers expect `ADR:` when the PR cites a specific decision position.

`Finding: none` is valid when the item is a pure ADR/build-plan execution with no FEM/inventory finding attached (rare — usually substrate PRs). It is not a license to skip the trailer.

The trim from 7-required to 4-required-plus-3-contextual was locked 2026-05-19 (this commit). Prior 7-required form is recoverable from git history; PRs in flight at the trim time pass under either rule.

### 13.3 Flag discipline — two flavors

Conflating these is the canonical way feature flags become permanent and cleanup never happens.

**(a) Policy-gated capability.** Default **OFF** until policy version P-N is in effect and calibration data permits. Example: Framework Approval executes the `approved → active` transition for Scope 1 BFs under policy P1. Flag survives in code; activation is via `framework_policy` (A8) row, not by removing the flag.

**(b) Defect disposition.** Default **OFF immediately** in PR N (the call site is no longer invoked, or the chained call is broken). Code path **removed entirely** in PR (N+1) after consumer confirmation that nothing else depends on the defective behavior. Flag does not survive past PR (N+1). Example: `oagis-onboarding.service.ts:300` `bulkCertifyFields(..., true)` chain disposition per build-plan C1 and finding G1.

**Why this matters.** Putting (b) under (a)'s pattern means the defect ships in every release until someone explicitly flips the flag — which never happens (FEM F43 funnel-fallback survival pattern is the proof). The two flavors have opposite default semantics and opposite end states; they do not share a code pattern.

### 13.4 Consumer map shape

Call-site enumeration alone is insufficient. FEM F25 (chain_status pre-activation race) is the proof: the caller wasn't relying on a behavior it knew about; it was relying on an *implicit filter assumption* nobody had documented (`getActiveMcVersions` filters to active only). A call-site map would not have caught it. The MLS-14 gate refused for the wrong reason because the consumer's implicit assumption was invisible.

**Required shape per consumer:**

| Field | Meaning |
|---|---|
| **Consumer** | Owning service / page / job / script |
| **Call site** | File + line; what is invoked |
| **Assumption** | What the consumer assumes about the callee's return shape, side effects, state, or filtering. *This is the load-bearing column.* |
| **Failure mode if callee changes** | How the consumer breaks if the assumption no longer holds |
| **Test/verification** | Characterization test path or manual verification step |

The Assumption column is the part the FEM evidence demands. Without it, consumer maps catalogue what is visible and miss what is implicit — which is exactly where the historical breakage lives.

### 13.5 Defect-characterization tagging

When the current behavior of a service being modified is itself wrong (e.g. oagis auto-cert producing placeholder certifications per G1), the characterization test documents the *defective* current behavior. Without an explicit tag, the test becomes a regression baseline against the defect we want to fix — the next person reading the test preserves the defect because "there's a test." Same dynamic that produced FEM F43.

**Required tag:**

```ts
// characterization: documents CURRENT DEFECTIVE behavior per FEM F1 / G1.
// remove when closing build-plan C1. Do not preserve as desired behavior.
describe('oagis-onboarding.bulkCertifyFields auto-cert chain (current defect)', ...)
```

Tag conventions:
- Cite the FEM finding or gap-research G-number that classifies the behavior as defective.
- Cite the build-plan item that will close the defect.
- Use the explicit phrase "CURRENT DEFECTIVE behavior" so grep/CI can detect untagged characterization tests of known-defective services.
- The test is **removed** (not just updated) when the closing build-plan item lands. Updated characterization-of-correct-behavior tests are new tests, not renamed defect tests.

### 13.6 Merge gate (9 questions)

Every behavior-changing PR's body must explicitly answer:

1. **Plan item?** Build-plan §1–§5 ID, e.g. C1.
2. **ADR authority?** DEC-149ab2 Q-position, or sibling ADR.
3. **Finding/inventory source?** FEM Fxx or gap-research Gxx or inventory §x.y.
4. **Consumers checked?** Count and link to PR body's consumer map.
5. **Implicit assumptions captured?** Per §13.4 — assumption column populated for every consumer.
6. **Current behavior characterized?** Test path; tagged per §13.5 if defective.
7. **New behavior tested?** Test path for the intended post-PR behavior.
8. **Rollback path?** One-line; matches `Rollback:` trailer.
9. **Phase 0 sampling/workload impact?** None / increases / decreases. If "increases," explain by how much and whether it threatens Phase 0 throughput (Q5 Phase 0 is operator-workload bound; the critical path identifies UI surface availability as the binding constraint).

Q5 is the part new contributors most often skip. Q9 is the part most likely to be unintentionally violated by Phase A migrations. CI checks trailer presence; reviewers check that the PR body's answers are substantive, not just present.

### 13.7 What CI enforces vs what reviewers enforce

| Layer | Enforces |
|---|---|
| **CI** | Trailer presence; trailer values match known build-plan IDs; trailer values match known ADR UIDs; characterization-test files tagged when modifying services on the known-defective list (G1, G6b, G7 substrate); PR body contains "## Consumer impact" + "## Merge gate" sections |
| **Reviewers** | Trailer values are substantively correct (the cited consumer map is real, the assumption column is populated, the rollback works); Phase 0 impact assessment is honest |

CI cannot judge whether an Assumption column is meaningful; reviewers can. CI can judge whether the column exists; reviewers can't reliably remember to check. Split the labor accordingly.

### 13.8 Discipline-vs-doc anti-pattern

This section is the specification. It is not the gate. If §13 becomes "the doc reviewers check" rather than "the spec CI enforces and reviewers cross-check," it has failed. Tracked failure modes:

- §13 cited verbally but not enforced in CI → FEM F40 stale-doc shape.
- §13 enforced for some repos but not others → FEM F26 IntegrityService-5-bugs cross-consumer-divergence shape.
- §13 carried forward into MCF build-plan and customized differently per sibling framework → divergence; preempt by referencing §13 from MCF rather than re-stating it.

### 13.9 First-batch application

The first execution batch (per §1 + §3 + §5 first-batch list) is mostly additive substrate; full §13 discipline applies to behavior-changing PRs within the batch (notably A4 and the oagis consumer map PR before C1). Additive substrate PRs still carry trailers and Q9 Phase 0 impact but are exempt from §13.4–§13.5 because there is no current behavior to characterize.

---

## 14. Build-sequencing correction & retrospective (2026-05-20)

This section records a build-sequencing failure caught on 2026-05-20, why it
happened, and the corrections applied to this plan. It is on the record so the
process gap is not repeated.

### What happened

BCF Phase A (substrate), the bc-ai emit/calibration items (B1–B5, B8), and the
entire bc-core consumption / governance / calibration layer (C1–C10) were built
and smoke-tested — but **B6/B7, the Context Authoring Panel itself, were never
built.** The Authoring Panel is the BCF product; every other build item exists
to govern, sample, route, or display what the panel produces. The framework's
consumers were built before its producer.

It surfaced during a first-principles survey of the authoring-panel flow: no
`bcf-authoring-panel` flow exists in bc-ai. Every "panel" smoke had used the
legacy `bf-dedup` flow as a **stand-in evidence producer** — `bf-dedup` is a
business-field deduplication flow, not the Framework Approval Authoring Panel.

### Why it happened — five structural causes

1. **The §7 critical path omitted the panel.** The previously stated path to
   "Phase 0 go-live" (`A1 → A3 → A4 → C2 → C5 → C7 → D2/D5`) routed around
   B6/B7. The plan declared go-live reachable without the panel — which is
   false: Phase 0 is "100% of AI actions to operator review", and there is no
   AI action without the panel.
2. **B6/B7 were dependency-graph leaves.** Nothing depends on them. C5, C8, C9,
   C10, and B8 all consume `panel_output_record` generically, so nothing
   downstream ever forced the panel to exist — and nothing failed loudly when
   it didn't.
3. **The plan under-specified the panel and split it in two.** B6/B7 read
   "wire existing `bf_dedup` / `bf_pii_classify` agents" — trivial glue. The
   real thing (a `bf_admission_review` endpoint) was buried in §6 Deferred work
   as F6, attached to a provider-diversity upgrade. The panel was described in
   two inconsistent places and the real one was deferred.
4. **A legacy flow masked the absence.** `bf-dedup` already had a
   maker/checker/moderator trio and emitted `panel_output_record`. Every smoke
   used it; the consumers ate its evidence and everything looked green. Loose
   wording ("BCF panel smoke" for what was a `bf-dedup` roster smoke) hid the
   gap until it was explicitly challenged.
5. **Phase-by-phase top-to-bottom execution stranded B6/B7.** Being last in
   Phase B and leaf nodes, they were skipped; Phase C looked "ready", so work
   moved on.

### The structural pattern

The ADR's six mandatory Framework-Approval conditions split exactly along the
build line: the substrate/governance conditions were built; the panel-core
conditions were not.

| Mandatory condition | Built? |
|---|---|
| (4) immutable NF1 authoring record | yes — A5/A6/B4 |
| (5) calibration sampling enrollment | yes — B8 |
| (6) operator override mechanism | yes — C7 |
| (1) three-model consensus + closed-enum verdict | **no** — panel unbuilt; B5 locked operational codes, not BCF verdicts |
| (2) same-input-snapshot (divergence detection) | **no** — B9 unbuilt; `seed_bundle` stubbed `{}` in B2 |
| (3) no-fabrication grounding check | **no** — B3 helper exists but no agent declares `grounded_fields`, so it always passes |

### Full gap list at 2026-05-20

| Item | Stated status | Actual |
|---|---|---|
| B6 / B7 — Authoring Panels | planned | **unbuilt** — the core miss |
| B9 — input-divergence detection | planned | **unbuilt** |
| B3 — no-fabrication grounding | "built" | **vacuous** — no `grounded_fields` declared |
| B5 — closed-enum verdicts | "built" | **wrong codes** — emits `FAIL_QA_GATE` / `FAIL_MAX_RETRIES`, never `REJECT` + A12 `defect_code` |
| B2 — `seed_bundle` in input-hash | "built" | **stubbed `{}`** |
| A14 — auto-pause / Phase 1→2 advance | partial | deferred (known) |
| B10 — Publication Panel (Stage 2) | (no BF item existed) | **unbuilt** |
| B11 — Lifecycle Audit Panel (Stage 3) | (no item, no deferral) | **unbuilt — plan omission** |
| Phase D — operator UI | planned | **0%** — D1/D2/D3/D5/D6 are the Phase-0 minimum surfaces |
| Phase E — E1/E2/E3 | planned | **0%** |

### Corrections applied to this plan (2026-05-20)

- **B6/B7 re-scoped** — from "wire existing agents" to a dedicated
  `bcf-authoring-panel` flow that renders the real admission decision and emits
  BCF closed-enum verdicts. The legacy `bf_dedup` / `bf_pii_classify` /
  `bo_composer` / `bo_dedup` flows are narrow sub-checks, not the panel.
- **B10 added** — Context Publication Panel (Stage 2), covering BF *and* BO
  (previously inline-for-BO-only, no BF item).
- **B11 added** — Context Lifecycle Audit Panel (Stage 3), previously absent
  from both the plan and the §6 deferral list.
- **§7 dependency graph + critical path corrected** — B6 is now on the stated
  critical path to Phase 0 go-live.
- **§6 F6 reconciled** — the stranded `bf_admission_review` reference is folded
  into B6/B7; the cross-family roster it also tracked was delivered (bc-ai PR #12).

### Re-sequencing rule

Build the Authoring Panel (B6/B7) **before** any further BCF work, then
**re-validate B8, C5, C8, C9, C10 against real panel evidence** — those
consumers were only ever exercised against `bf-dedup` output and controlled
synthetic rows, never a real Authoring Panel verdict.

### Process lessons

1. A build plan must keep the product's core deliverable **on** the stated
   critical path — not as a leaf the graph routes around.
2. A consumer of an artifact must not be marked complete before the artifact's
   **producer** exists; "the consumers are green" is not "the system works".
3. Stand-in test fixtures (here, `bf-dedup`) must be **labelled as stand-ins**
   in every report, so they cannot mask the absence of the real component.

---

## 15. Requirements-coverage matrix (added 2026-05-20)

> **Historical — pre-Registry coverage matrix.** This matrix predates DEC-02f5a9 and maps requirements to the pre-Registry BF/BO/CF build items. It awaits a reflow against the Registry (§16.4). Until that lands, **§16 is authoritative** wherever this matrix and the Registry frame disagree.

The build plan's work items each cite the ADR position or inventory row that
*authorized* them — an item → authority trace. There was **no reverse trace**
(requirement → build item), so a requirement with no item was structurally
invisible. That is the same root cause as the §14 panel miss. This section adds
the missing reverse trace: every BCF requirement family mapped to its build
item(s), with a disposition for each gap.

Scope note: the plan is Scope-1-only (ADR Q1). Scope 2 (CF, Ch 13) and Scope 3
(BF↔CF mapping, Ch 14, and the BF↔CF half of Ch 15) are deferred by design via
§6 F1–F4 — they are marked ⏸ below and are not gaps.

### 15.1 Coverage matrix

Status key: ✅ covered · ◑ partial (see §14 or a disposition below) · ✚ was a coverage gap at 2026-05-20 — now a named item in the §2–§4 tables (or a §15.2 fold), unbuilt · ⏸ deferred by design.

(The `✚` rows record the original gap for the audit trail; the gap itself is closed — each `✚` requirement now traces to a real build item per §15.2 / §15.3.)

| Requirement (source) | Build item(s) | Status |
|---|---|---|
| PE1–PE6 publication eligibility (Ch 3) | **C11 (new)** | ✚ |
| No-fabrication rule (Ch 3, N1) | B3 | ◑ — B3 vacuous (§14) |
| Inconsistency intolerance (Ch 3) | A1, A12 + DB CHECKs | ✅ |
| Intake queue (Ch 4) | C8 | ✅ |
| Five-state lifecycle / `governance.state` (Ch 4) | A1, A3 | ✅ |
| Transition gates intake→…→active (Ch 4) | C5 (draft→review v1); B10 + C11 (review→approved→active) | ◑ |
| Operator override — edit non-active / supersede (Ch 4, 5) | C7 | ✅ |
| Operator-confirm policy (Ch 4, 7) | A9, A10, C6 | ✅ |
| Rule 1 — Framework Approval discipline (Ch 5) | C5 | ◑ — depends on panels (§14) |
| Rule 2 — override always available (Ch 5, N3, N23) | C7; **N23 → C5** | ◑ — N23 check missing |
| Rule 3 — authoring-record trail (Ch 5) | A5, A6 | ✅ |
| Activity Dashboard / Notifications / Detail / Override / Rejection Log / Reference Impact / Transcript Viewer (Ch 6) | D1, D11, D2/D3, D5, D6, D10, D4 | ✅ (planned; Phase D 0%) |
| Policy Management + sunset cadence/auto-disable (Ch 6, 7) | D9 (+ sunset **fold**) | ◑ |
| Calibration Dashboard + NF5 cost dashboard (Ch 6, 10) | D8 (+ cost **fold**) | ◑ |
| Activity Log — full immutable history (Ch 6, NF6) | **D14 (new)** | ✚ |
| Operator Authoring Tool (Ch 6) | **D15 (new)** | ✚ |
| Stage 1 / 2 / 3 Context Panels (Ch 7) | B6, B7 / B10 / B11 | ◑ — unbuilt (§14) |
| Three-model consensus / same-input snapshot (Ch 7, F13) | B2, B9 | ◑ — B9 unbuilt, seed_bundle stub (§14) |
| Immutable panel records (Ch 7, NF1) | A5, B4 | ✅ |
| Framework policy + bounded-write discipline (Ch 7) | A8, C5 | ✅ |
| Closed-enum verdicts (Ch 7, A12) | A12, B5 | ◑ — B5 wrong codes (§14) |
| F1 source drift · F2 provenance decay · F14 panel-output integrity (Ch 9) | **C13 (new)** | ✚ |
| F3 duplicate accretion · F4 panel disagreement (Ch 9) | B11 / B6/B7/B10 | ◑ — unbuilt |
| F5 operator absence (Ch 9) | A14 (**fold** — sample-review-age monitor) | ◑ |
| F6 state inconsistency (Ch 9) | A1 + CHECKs | ✅ |
| F9 AI outage (Ch 9) | operational (see §15.2) | ◑ |
| F12 calibration regression auto-pause (Ch 9) | A14 | ◑ — auto-pause deferred (§14) |
| F15 policy misconfiguration (Ch 9) | **C12 (new)** | ✚ |
| Calibration as first-class (Ch 10 NF7) | A13, A14, C10, D8 | ✅ |
| Foundation-compatibility validation of writes (N15) | **N15 → C5** | ✚ |
| N1–N30 negative requirements (Ch 11) | mostly covered; N30 → C10; **N15, N23 → C5** | ◑ |
| BF↔BO membership coherence (Ch 15, Scope 1) | **fold → B6/B7/B10** panel judgment | ◑ |
| Scope 2 (CF, Ch 13) · Scope 3 (BF↔CF, Ch 14, Ch 15 BF↔CF) | §6 F1–F4 | ⏸ deferred |

### 15.2 Gap dispositions

**New items** (merged into the §3/§4 phase tables 2026-05-20 — see §15.3):

| ID | Item | Why it is distinct |
|---|---|---|
| **C11** | **PE1–PE6 deterministic publication gate** (bc-core, refuse-only). Deterministic verification of provenance / anchoring / fetchable reference / semantic family / type-unit coherence / definition discipline before `review → approved`. | Ch 4 makes it a separate condition from the panel: "Publication Panel APPROVE consensus **+** PE1-PE6 deterministic publication gate pass." It is neither the AI panel (B10) nor the orchestration (C5). T-shirt M; deps A8, B10. |
| **C12** | **Framework-policy validator** (bc-core, config-time). Rejects at save any `framework_policy` that grants authority outside the three scopes or violates Rules 1/2/3. | F15 — "policy validator on every save runs against framework rules at config-time." T-shirt S; deps A8, A10. |
| **C13** | **Failure-mode monitors** (bc-core scheduled jobs): F1 source-drift detection (scanner diffs → tickets), F2 provenance-decay link-check on active members, F14 panel-output integrity check + the NF1 cross-storage replication guarantee. | F1/F2/F14 each specify a detector; none had an item. T-shirt M; deps A5. |
| **D14** | **Activity Log surface** (bc-admin). Full immutable history — panel calls, gate results, AI actions, operator actions, policy changes, calibration events. | Ch 6 lists it as a distinct surface; NF6 requires the unified event log. D1 covers only the *AI-activity* stream. The substrate is A5 + A6 + A13 **plus** operator-action and policy-change events — which C7 and D9 must emit. T-shirt M. |
| **D15** | **Operator Authoring Tool** (bc-admin). Operator-initiated intake-queue entry surface. | Ch 6 required surface; no Phase D item. T-shirt M; deps C8. |

**Fold dispositions** (applied inline to the named item's scope 2026-05-20 — see §15.3):

| Gap | Folds into | Amended scope |
|---|---|---|
| N23 — override-availability | **C5** | `decide()` routes to OPERATOR_REVIEW when the operator override mechanism is paused / broken / unavailable — add to the bounded-write conditions. |
| N15 — Foundation-compat validation | **C5** | Every framework write validated against Foundation Contract Grammar schemas before commit. |
| F5 — sample-review-age monitor | **A14** | A14 also monitors sample-review-age; an SLA breach feeds the F12 auto-pause path. |
| NF5 — cost dashboard | **D8** | D8 also surfaces per-member / per-stage / per-policy AI cost breakdown. |
| Ch 7 — policy sunset cadence | **D9** | D9 also implements the quarterly-review cadence and auto-disable of a policy not re-affirmed within its window. |
| Ch 15 — BF↔BO membership coherence | **B6 / B7 / B10** | The panels' judgment scope explicitly includes BF↔BO membership coherence (Scope 1). |
| F9 — AI-outage heartbeat | operational | Tracked as operational monitoring alongside D11 notifications — not a distinct build item. |

### 15.3 Re-version status

**Merged 2026-05-20 (same day).** C11–C13 are in the §3 Phase C table and
D14–D15 in the §4 Phase D table; the §7 dependency graph carries their edges;
the seven fold amendments are applied inline to A14, C5, D8, D9, B6, B7, and
B10; the Phase C and Phase D mass lines are updated. The §2–§4 tables and the
§15.1 matrix are therefore a single source of truth — no drift.

§15 is retained as the dated audit record of how the coverage gap was found
and closed. The standing rule holds: no build item may be marked complete on
the strength of "the requirement is implied" — every requirement traces to a
named item or an explicit deferral.

---

## 16. DEC-02f5a9 impact — Registry substrate, scope collapse, and cutover (2026-05-21)

DEC-02f5a9 (Business Concept Registry; D414, decided 2026-05-21) supersedes
DEC-a17d0f and the Business Object / Business Field / Canonical Field vocabulary
model. It changes the foundation this plan was built on. This section records
the impact and the re-scoping it requires; it follows the §14 / §15 precedent —
a dated impact section, not a silent rewrite of the phase tables.

### 16.1 Scope collapse

This plan is framed around three scopes (ADR-149ab2 Q1): Scope 1 (Business
Field, with Business Object), Scope 2 (Canonical Field), Scope 3 (BF↔CF
mapping). DEC-02f5a9 collapses that frame:

| Old scope | Under DEC-02f5a9 |
|---|---|
| Scope 1 — Business Field | Business Concept (one registry concept) |
| Scope 2 — Canonical Field | Collapsed into Business Concept — there is no separate canonical-side vocabulary |
| Scope 3 — BF↔CF mapping | **Eliminated** — with one Business Concept there is no BF↔CF identity to map |
| Business Object (within Scope 1) | Entity |

The three scopes become **one governed Business Concept Registry** of Entities
and Business Concepts. The "Scope 1 first, Scope 2/3 deferred" sequencing
(ADR-149ab2 Q1) is retired: there is no Scope 2 or Scope 3 to defer. §6 deferred
items F1–F4 (Scope 2/3 activation) are mooted; §6 F8 (Foundation amendment
proposals — "BF/CF collapse, BO necessity") is **resolved** — DEC-02f5a9 is that
amendment.

### 16.2 New phases — Phase F and Phase G

DEC-02f5a9 authorizes two phases this plan carries. The 2026-05-21 deep
re-scope (§16.4) sizes their build items below. Item IDs and T-shirt sizes are
a first-pass proposal, subject to the same review discipline as the rest of the
plan.

**Phase F — Registry substrate.** Build the Business Concept Registry: the
Entity / Property / Business Concept storage, identity constraints
(`UNIQUE(entity_id, property_id)`; globally unique entity IDs), and the
authoring service. Built alongside the running existing chain (DEC-02f5a9 §6) —
it does not disturb the demo tenant. Phase F is first in the build order;
everything that authors Registry concepts depends on it.

| ID | Item | Citation | T-shirt | Depends on |
|---|---|---|---|---|
| **F1** | Resolve the three forward-design items DEC-02f5a9 left open — composite-entity identity representation, the versioning unit (entity-level vs concept-level lifecycle), and the initial governed content of the entity / property-characteristic / representation-term vocabularies. Design pass; output is a design note the F2 DBCP and F3 service implement. | DEC-02f5a9 Decision boundary; business-concept-registry.md §13 | L | — |
| **F2** | Registry schema DBCP — `entity`, `property`, `business_concept` tables; `UNIQUE(entity_id, property_id)`; globally unique entity IDs; reference-property `(role, target_entity)`; `identity_role`; acyclic identity-reference-graph constraint. Operator-approved DBCP per the Database Change Protocol. | DEC-02f5a9 §1, §3; Decision boundary | L | F1 |
| **F3** | Registry authoring service (bc-core) — create / version Entity, Property, Business Concept; enforce the structural identity constraints at write time (synonyms and homonyms structurally impossible, DEC-02f5a9 §3); five-state lifecycle and the supersession rule (identity-bearing change = supersession). | DEC-02f5a9 §1, §3 | L | F2 |
| **F4** | Governed-vocabulary seed — the closed representation-term set (seeded from ISO 11179, then owned) and the property-characteristic vocabulary; the bounded term set the panel's synonym check tests against. | DEC-02f5a9 §1; business-concept-registry.md §5 | M | F2 |
| **F5** | Registry projection / read surface — resolve a Business Concept by identity for the contract chain and the panels; the ID-only reference surface DEC-02f5a9 §4 requires. | DEC-02f5a9 §4 | M | F3 |

**Phase G — Greenfield cutover.** Per DEC-02f5a9 §5–§6: re-author the existing
Observation Contract versions, discard-and-re-author the Canonical and Metric
Contracts against the Registry, discard the Canonical Mapping layer, then — as
the final coordinated step — retire the old vocabulary-referencing chain and its
runtime evidence and regenerate from source / SDG. Source and Admission
Contracts and the seed catalogs survive (DEC-02f5a9 §5 cleavage plane). Phase G
is last — it runs only after Phase F and the re-authored contracts are ready.

| ID | Item | Citation | T-shirt | Depends on |
|---|---|---|---|---|
| **G1** | Re-author the existing Observation Contract versions against Registry Business Concepts — `observation_field_map` retargets from Business Field to Business Concept; the OC family and the source→concept binding act are unchanged. | DEC-02f5a9 §5 (OC explicit) | L | F5; Registry concepts authored |
| **G2** | Discard and re-author the Canonical Contracts against the Registry — `field_selection` references Business Concepts directly; grain is a typed Entity reference. | DEC-02f5a9 §5 | L | G1 |
| **G3** | Discard and re-author the Metric Contracts against the Registry — `metric_binding` and inputs reference Business Concepts. | DEC-02f5a9 §5 | L | G2 |
| **G4** | Discard the Canonical Mapping / `cc_field_mapping` / metric-binding identity layer. | DEC-02f5a9 §2, §5 | M | G2, G3 |
| **G5** | Coordinated discard of runtime evidence evaluated under discarded or re-authored contract versions; regenerate from source / SDG. Whether raw admitted Source Objects are discarded or retained as pre-cutover audit artifacts is settled in the G7 runbook. | DEC-02f5a9 §6 | L | G1, G2, G3 |
| **G6** | Physical-table disposition DBCP — retire or compatibility-wrap `business_object` / `business_field` / `canonical_field` and the A1–A4 / C1–C4 interim work. Operator-approved DBCP. | DEC-02f5a9 §6 | M | G4 |
| **G7** | Cutover runbook and the coordinated switch — the single act that retires the old chain and brings the Registry-based chain to `active`; golden-snapshot rollback. | DEC-02f5a9 §6 | L | G1–G6 |

### 16.3 Phase A is now interim

Phase A adds `governance.state` and `quarantine_marker` columns to
`contract.business_field` and `contract.business_object` (A1, A2). Under
DEC-02f5a9 those tables are the superseded primitive identity surfaces — retired
or compatibility-wrapped at the Phase G cutover (DEC-02f5a9 §6; physical-table
disposition is a later DBCP). Phase A work remains valid for the pre-cutover
platform but is **interim**: it operates on tables the cutover retires. A deeper
re-scoping of Phase A against the Registry — which Phase A items survive, which
are absorbed into Phase F — is the named follow-up in §16.4.

### 16.4 Re-scoping — landed 2026-05-21

The deep re-scope this section named has landed. Operator locks (2026-05-21):
sequencing inversion (Phase F first); Phase A split (A5/A8/A9/A10/A13/A14
survive, A1–A4 interim); Phase 0 is a post-Phase-F milestone; one unified
Registry Authoring Panel (not separate Entity / Concept panels). Applied:

- Phase model table re-ordered to build order (F → A → B → C → D, E parallel,
  G last).
- §1 Phase A split note added; §3 Phase C and §4 Phase D carry their interim /
  retarget notes; §2 Phase B retitled and built against the Registry; B6 + B7
  merged into the unified Registry Authoring Panel; B10 / B11 retargeted.
- §16.2 sizes the Phase F (F1–F5) and Phase G (G1–G7) build items.
- §16.5 is the re-scoped dependency graph and critical path; the §7 graph is
  bannered as the pre-DEC-02f5a9 record.
- §6 F1–F5 mooted, F8 resolved; §8 sequencing rationale carries the re-scope
  note.

Still open as ordinary plan maintenance — not a frame question, and not a
blocker on build order: a full reflow of the §15 coverage matrix against the
Registry, and the per-item retargeting of the Phase C / Phase D rows that still
name BF / BO / CF (C1–C4 and the detail pages are already flagged interim). The
build order and the four locks are settled by this §16.

### 16.5 Re-scoped dependency graph and critical path

The build order, superseding the §7 graph:

```
Phase F — Registry substrate (FIRST)
  F1 (forward-design lock) -> F2 (schema DBCP) -> F3 (authoring service) -> F5 (projection)
  F2 -> F4 (governed-vocab seed)

Phase A — Governance substrate (after F; A1-A4 parked, see §1)
  A5 -> A6 -> A7;  A5 -> A12;  A5 -> A13
  A8 -> A9 -> A10 -> A11;  A8 -> A14 <- A13

Phase B — Panels against the Registry (after F + A-substrate)
  B1 independent;  B2 -> B3 -> B4 -> B5;  B2 + B4 -> B9;  A14 + B4 -> B8
  F1-F5 + B1-B5 + B9 -> B6 (Unified Registry Authoring Panel)  <- BCF product, critical path
  B6 -> B10 (Publication);  B6 -> B11 (Lifecycle Audit)

Phase C — bc-core orchestration (after A-substrate + B-emitter + B6)
  A5 + A6 + A8 + A14 + B4 + B6 -> C5;  A9 + A10 + C5 -> C6;  A6 + C5 -> C7
  A5 -> C8 -> C9;  A13 -> C10;  A8 + B10 -> C11;  A8 + A10 -> C12;  A5 -> C13
  C1-C4 interim — retired by Phase G; no new investment

Phase D — Operator UI (after A + B + C)
  D1-D11, D14, D15 retargeted to Registry concepts / entities; D12 / D13 flag-only

Phase E — Parallel tracks (independent)
  E1, E2 independent;  E1 -> E3

Phase G — Greenfield cutover (LAST)
  Registry concepts authored via B6 -> G1 (OC) -> G2 (CC) -> G3 (MC)
  G2 + G3 -> G4 (discard mapping layer);  G1-G3 -> G5 (evidence discard + regenerate)
  G4 -> G6 (physical-table DBCP);  G1-G6 -> G7 (cutover runbook + switch)
```

**Critical path** (DEC-02f5a9 frame):

```
Phase F Registry substrate
-> surviving governance substrate (A5 / A8 / A13 / A14)
-> unified Registry Authoring Panel (B6)
-> Framework Approval / intake routing (C5, C8)
-> Phase 0 Registry-authoring go-live
-> Publication / Audit surfaces (B10, B11; Phase D)
-> Phase G greenfield cutover
```

Phase F is the head of the path: no Registry concept can be authored, governed,
sampled, or published before the Registry exists. The §14 lesson holds — the
product's core deliverable (the unified panel, B6) stays on the stated path, and
a consumer is never marked complete before its producer (now Phase F).
