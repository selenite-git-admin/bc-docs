---
id: business-context-framework-b6-design-survey
title: "Business Context Framework — B6 Unified Registry Authoring Panel: Design Survey"
description: "Draft design survey for B6, the unified Registry Authoring Panel — grounded in repo state, Foundation invariants, and BCF requirements; surfaces the decisions to lock before the B6 build."
status: draft
authority: informative
date: 2026-05-22
project: bc-core
domain: business-context-framework
subdomain: registry-authoring-panel
focus: lifecycle
depends_on:
  - business-context-framework-build-plan
  - business-context-framework-requirements
  - business-context-framework-phase-a-alignment-dbcp-bucket-1
governing_adrs:
  - DEC-02f5a9
governing_sources:
  - BCF Requirements Ch.4 (Lifecycle and state — intake queue)
  - BCF Requirements Ch.5 (Division of labor — authority principle)
  - BCF Requirements Ch.7 (Context Panels — Stage 1; bounded-write discipline, line 543)
  - Foundation — The Invariants (Invariants I, III, IV, V, VI)
  - Foundation — The Authority Model
---

# Business Context Framework — B6 Unified Registry Authoring Panel: Design Survey

## 1. Purpose and status

This is a **draft design survey**, not an architecture lock and not a build plan. It maps what B6 — the unified Registry Authoring Panel — must be, grounded in the actual bc-core repo state after the Phase A Bucket-1 §5 chain merged (PRs #62–#67), in the BCF build plan and requirements, and in the Foundation invariants. It exists so the open decisions can be locked before any B6 code is written. No build PR follows from this note directly; the B6 build itself should begin with a design note / output contract, not code.

This document is descriptive-layer (`authority: informative`). It introduces no invariant and overrides no ADR. Where it identifies a needed substrate, it names it as a **DBCP / design fork**, not a settled design.

## 2. Posture

Three posture rules govern how this survey reads the prior work:

1. **Prior effort artifacts are usable evidence, not binding architecture.** Existing A/B/C/F artifacts are reused where they fit B6's purpose and discarded or bypassed where they encode the wrong model. B6 is **not** force-fit around BF/BO/CF-era surfaces merely because they exist.

2. **No patch/stitch architecture.** Where B6 needs a clean Registry-native intake, operator-confirm, or rejection surface, this survey says so and marks it as a DBCP / design fork — it does not propose stitching B6 onto a legacy BF/BO surface to save a seam.

3. **Re-grounded in Foundation and requirements.** Before the dispositions in §10–§11 were written, the Foundation invariants (`the-invariants.md`), the Authority Model (`the-authority-model.md`), and BCF Requirements Ch.3–Ch.7 were re-read. The grounding result is in §9.

A note on framing: the Registry artifacts B6 authors (`entity`, `business_concept`, `characteristic`, `alias`) are **platform vocabulary substrate**, not the four authoritative progression objects (Source Object → Canonical Object → Metric Snapshot → Action Object). The six invariants still bind B6's governance acts by the same discipline — meaning evaluated once, state immutable, references explicit, evaluation non-replayable, evidence emitted — but B6 does not produce progression objects, and this survey does not claim it does.

## 3. Where B6 sits

B6 is the **load-bearing deliverable of Phase B** (build plan §2 mass line; §16.5 critical path). It is the **unified Registry Authoring Panel** — the merge of the old B6 (BF) and B7 (BO) panels into one, because concept placement is a single judgment and a split would recreate the cross-scope coherence problem DEC-02f5a9 eliminates. It is **Stage 1 — Authoring** of the three-stage Context Panel model (Stage 2 = Publication / B10; Stage 3 = Lifecycle Audit / B11).

**B6 does not exist in code today.** The substrate around it does:

| Component | State |
|---|---|
| F3 `RegistryAuthoringService` — the 12 cert-gated Registry write operations | merged, live |
| F4 governed vocabulary — 24 characteristics + closed representation-term set | merged, live |
| F5 `RegistryReadService` — the Registry lookup / placement-support surface | merged, live |
| C5 `issueRegistryShapeCertification` — born-null Registry-shape cert issuance | merged; **no production caller yet** |
| §5 Model A chain — C5 → F3 — proven end to end (PR #67 live smoke) | merged |
| B4a `panel-output-record` ingest (`POST /api/bcf/panel-output-records`) | merged, live, scope-agnostic |
| **B6 panel** (Maker/Checker/Moderator trio) | not built |
| **B6 orchestrator** (bc-core — drives APPROVE → C5 → F3) | not built |
| **B4b** bc-ai panel-output emitter | not built |
| **Registry intake-candidate substrate** | not built — see D1/D2 |

B6 spans two repos: the **panel** (the AI trio) runs in **bc-ai**; a **B6 orchestrator** in **bc-core** drives the post-APPROVE C5 → F3 sequence. This survey treats "B6" as that whole component.

## 4. What B6 is responsible for

| Responsibility | Grounded mechanism |
|---|---|
| Intake candidate | B6 operates on a Registry intake candidate (a raw concept proposal — name, definition, source rows, citations). BCF Requirements Ch.4 mandates an intake queue; **no Registry intake substrate exists** — D1/D2. |
| Placement judgment | The Maker/Checker/Moderator trio judges entity placement, property placement, concept identity (synonym/homonym vs governed terms), definition discipline, provenance — build plan §2 B6; Requirements Ch.7 Stage 1. |
| Proposal of Registry operation | The panel resolves the candidate to exactly one `(subject_kind, action_code, F3 operation, F3 input)` tuple from the DBCP §2.4.6 matrix — see §8. |
| `panel_output_record` emission | bc-ai posts a `CreatePanelOutputRecordDto` to B4a; `panel_run_uid` is minted DB-side; the proposed operation rides in `verdict_payload_json` — see §9. |
| Handoff to C5 issuance | On `APPROVE_FOR_DRAFT`, the B6 orchestrator calls `FrameworkApprovalService.issueRegistryShapeCertification({subjectKind, actionCode, panelRunUid, policyVersion})` → a born-null Registry-shape `certification_record`. |
| Operator / Framework-Approval confirm | B6 **judges whether** an operation needs operator confirm (build plan §2: "whether new governed terms require operator confirm"). Under the locked Model C (D3) the first slice runs with **zero `registry` operator-confirm rules** — nothing to confirm; when the high-risk tier is built the confirmation rides in `gate_results_json`. See §9.4. |
| F3 execution | The orchestrator passes the issued `certificationRecordId` + `panelRunUid` as a `RegistryAuthorization` to the matching `RegistryAuthoringService` method; F3 verifies, writes, and stamps `target_registry_id`. |

## 5. What B6 must not do

| Prohibition | Why it holds |
|---|---|
| No direct `concept_registry` writes | Every write goes through F3 `RegistryAuthoringService`, cert-gated by `CertificationVerifier`; the F2 schema adds append-only triggers on the version tables. B6 has no write repository and must not acquire one. |
| No raw `certification_record` writes | `CertificationRecordWriteRepository` is module-private to `framework-approval/` and grep-guarded. B6 obtains a cert only via `issueRegistryShapeCertification`. |
| No BF/BO/CF compatibility shim | B6 is Registry-native (Model A: `governance_scope='registry'`, `subject_kind`, `target_registry_id`). It must not poly-ref `primitive_type`/`primitive_id` or route through the legacy `decide()` path. |
| No automatic supersession-cascade activation | `supersedeEntity` *raises* one `supersession_proposal` per identity-bearing dependent; actioning/dismissing each is a separate governed operation. B6 must not auto-action — that would make F3 an auto-rewrite engine. |
| No bypass of governed vocabulary selection | Value concepts bind a `characteristic_id` from the F4 set and a `representation_term` from the closed set (enforced by the `business_concept` kind/metadata disjoint CHECK). B6 selects from F5; a genuinely new characteristic is itself a `registry_author_vocabulary` operation. |

## 6. Components B6 builds on

**F5 — `RegistryReadService`** (`concept-registry/registry-read.service.ts`) — B6's lookup / placement surface, active-only by default:
`findByNormalizedName(kind, rawName)` (synonym/homonym check across canonical names and aliases) · `listEntities` / `resolveEntity` · `listConceptsForEntity` / `resolveConcept` / `resolveConceptVersion` · `listCharacteristics` / `getCharacteristic` / `listRepresentationTerms` (the binding selection sets) · `listAliases` and the supersession-list methods.

**F4 — governed vocabulary** — 24 operator-locked characteristics (`f4-characteristics-v1.ts`, `F4_V1_EXPECTED_COUNT=24`) plus a closed representation-term set. B6 presents these as the candidate's binding choices.

**C5 — `issueRegistryShapeCertification`** — input `{subjectKind, actionCode, panelRunUid, policyVersion}`; validates the locked vocabulary and the §2.4.6 pairing; runs five vocabulary-agnostic panel-evidence checks (panel exists · stage `authoring` · grounding not quarantined · verdict `APPROVE_FOR_DRAFT` · policy version match); writes the born-null cert. `subject_kind` / `action_code` are explicit method inputs — C5 does not read them from the panel record; the B6 orchestrator carries them across from `verdict_payload_json`.

**F3 — `RegistryAuthoringService`** — 12 cert-gated operations; `RegistryAuthorization {certificationRecordId, expectedPanelRunUid?, actorSub}`; re-checks the cert's `(action_code, subject_kind)` against the operation; stamps `target_registry_id`. The placement checkers (`NameConflictChecker`: name-conflict, `assertAcyclic`, `assertDependentDistinct`) are module-private to `RegistryAuthoringModule` — B6 cannot call them; it previews via F5 instead (see D5).

**Phase A surfaces** — `framework_policy`, `operator_confirm_rule`, `phase_state` each gained a `registry` scope value (purely additive). `panel_output_record` (A5) carries the NF1 field set; B8 `CalibrationSamplingService` decides `sampling_status` server-side at B4a ingest.

## 7. (reserved)

## 8. The core authoring decisions B6 must make

Each decision maps to a schema fact and resolves to one §2.4.6 operation:

| Decision | How B6 decides | Resolves to |
|---|---|---|
| New entity vs existing | `findByNormalizedName('entity', name)` + definition similarity over `listEntities`. Strong match ⇒ existing. | existing → place a concept on it · new → `registry_create` / `entity` |
| New concept vs version vs alias/synonym | `listConceptsForEntity(entityId)`. The entity already carries a concept for the same `(characteristic_id)` (value) or `(reference_role, target_entity_id)` (reference) — the anti-synonym unique indexes make this structural ⇒ version if the change is descriptive, or the candidate is a synonym ⇒ alias. New meaning ⇒ new concept. | `registry_create` / `business_concept` · `registry_add_version` / `business_concept` · `registry_author_vocabulary` / `alias` |
| Value vs reference concept | The `business_concept` kind/metadata disjoint CHECK: `value` ⇒ `characteristic_id` + `representation_term` (both mandatory); `reference` ⇒ `reference_role` + `target_entity_id`. | sets `kind` in the `createBusinessConcept` F3 input |
| Characteristic / representation-term selection | Select from F5 `listCharacteristics()` / `listRepresentationTerms()`. No fit ⇒ a vocabulary-authoring op. | bind existing → into the value-concept input · new characteristic → `registry_author_vocabulary` / `characteristic` (confirm-sensitive — D3) |
| Identity-bearing reference + acyclic | A `reference` concept with `identity_role='identity_bearing'` adds an `entity → target_entity` edge to the identity DAG. B6 should preview acyclicity; `assertAcyclic` is F3-private (D5). | F3 enforces at write; B6 previews to avoid a late `UnprocessableEntityException` |
| Supersession vs versioning | A descriptive refinement ⇒ `registry_add_version`. A meaning-bearing change ⇒ `registry_supersede`. The panel's hardest judgment. | `registry_add_version` · `registry_supersede` (+ later proposal resolutions) |

**Op-scope (D4).** Stage 1 (B6) owns `registry_create`, `registry_add_version`, `registry_author_vocabulary`, and *raising* `registry_supersede`. `registry_transition` (lifecycle `draft → review → approved → active`) belongs to B10 (Publication Panel). Whether `registry_action_/dismiss_supersession_proposal` is a B6 act or a separate operator / B11 act is open.

## 9. The output contract

### 9.1 Panel output payload

The panel output payload is the existing `CreatePanelOutputRecordDto` (`src/registry/dto/create-panel-output-record.dto.ts`) posted to B4a — **no envelope schema change needed**:

`stage_code='authoring'` · `prompt_version` · `input_hash` (`sha256:…`, B2) · `policy_version` · `model_identity_json` ({maker, checker, moderator}, each {provider, model_version}) · `agent_outputs_json` ({maker, checker, moderator} transcripts) · `grounding_check_result` · `sampling_status` (server-overridden at B4a) · `verdict_code` · `verdict_payload_json`.

### 9.2 Recording the proposed operation

`panel_output_record` has **no dedicated column** for `subject_kind` / `action_code` / F3-operation-input — and it should not get one: the table is scope-agnostic by design, and C5 takes subject/action as explicit inputs. The schema already designates `verdict_payload_json` as carrying the "recommendation on APPROVE". B6 therefore defines a recommendation sub-schema inside `verdict_payload_json`:

```
verdict_code = 'APPROVE_FOR_DRAFT'
verdict_payload_json = {
  recommendation: {
    proposed_operation: {
      subject_kind:  <one of 5>,
      action_code:   <one of 7 registry_*>,
      f3_operation:  'createEntity' | 'createBusinessConcept' | 'registerCharacteristic' | ...,
      f3_input:      { ...operation-specific RegistryAuthoringService input... }
    },
    placement_rationale: '<why this entity / this kind / this characteristic>',
    evidence: {
      source_citations: [ <source rows / system / field provenance> ],
      grounding_basis:  '<the no-fabrication justification>'
    },
    operator_confirm_required: <boolean>,   // B6's JUDGMENT that confirm is needed
    candidate_ref: '<intake candidate id>'
  }
}
verdict_code = 'REJECT'           → verdict_payload_json = { defect_code: <one of 9> }   // DB CHECK
verdict_code = 'OPERATOR_REVIEW'  → verdict_payload_json = { review_reason: '...' }
```

This is the recommended v1 home for the proposed-operation payload unless a deeper Foundation review shows a stronger need for a dedicated surface.

### 9.3 Evidence, rationale, source/citation, provenance preservation

The chain that satisfies Invariant VI (evidence emitted, not inferred):

1. Agent reasoning → `agent_outputs_json` (verbatim Maker/Checker/Moderator transcripts) — immutable in the append-only `panel_output_record`.
2. Model identity + input snapshot → `model_identity_json` + `input_hash` — the same-input-snapshot proof (B2/B9; Requirements Ch.7 consensus rule).
3. Placement rationale + source citations → `verdict_payload_json.recommendation.evidence`.
4. Grounding verdict → `grounding_check_result` / `quarantined` (B3; Requirements Ch.3 no-fabrication rule).
5. C5 carry-forward → `issueRegistryShapeCertification` copies the 7 NF1 fields into the `certification_record`, plus a `gate_results_json` of the five panel-evidence checks.
6. F3 stamp → every `entity_version` / `business_concept_version` row is stamped with `certification_record_id` + `panel_run_uid`.

Net provenance chain, fully explicit and append-only: **Registry version row → `certification_record` → `panel_output_record` → agent transcripts + input hash.** No reconstruction; every link is a stored reference.

### 9.4 REJECT, deemed approval, and operator-confirm

**REJECT.** The REJECT *evaluation* must emit evidence (Invariant VI — a decision with no emitted evidence is treated as not having occurred), and it does: a REJECT panel run still posts an immutable `panel_output_record` to B4a with `verdict_code='REJECT'` and the `defect_code` in `verdict_payload_json`. **That panel record is the REJECT evidence.** The `authoring_panel_rejection_log` (Requirements Ch.6) is a *separate* operator-facing browse/override surface — not the Invariant VI evidence. **D2 — locked:** the BF/BO C8/C9 surfaces (`intake_queue`, `authoring_panel_rejection_log`) are **not reused as-is**; Registry-native intake + rejection surfaces are a Bucket-2 DBCP fork. For the **first slice**, non-APPROVE paths (REJECT, OPERATOR_REVIEW) **park and report only — no rejection-log write**; the emitted `panel_output_record` carries the evidence, and the rejection-log operator surface lands with the Bucket-2 fork.

**Deemed approval and operator-confirm.** The BCF is a **deemed-approval framework by mandate**. Requirements Ch.5 states the authority principle — "AI proposes, prepares, and approves context … Operator overrides as exception" — and Ch.6 explicitly rules out a routine per-member approval queue ("the operator does not approve as default; the framework approves"). The bounded-write discipline (Ch.7 line 543) is itself the deemed-approval contract: it lists seven conditions under which a panel APPROVE writes catalog state, and **none of them is operator approval**. A panel-approved Registry operation may therefore auto-issue its cert when policy permits — *provided the cert honestly emits the evidence that policy allowed it*. Invariant VI is the honesty test: a decision with no emitted evidence is treated as not having occurred, so an unrecorded deemed-approval decision is a silent bypass.

**Deemed-approval provenance — what the cert must carry so it is not a silent bypass:** `policy_version` (NF1 field — already written); `panel_run_uid` (already written); `certifier_sub = 'bcf-framework-approval'` — the sentinel that already declares the cert BCF-issued, *not* operator-certified; and a new **`gate_results_json.deemed_approval` block** recording the disposition (`auto_issued` / `operator_confirmed` / `operator_confirm_waived`), the governing policy's operator-confirm-rule disposition (this is the Ch.7 "operator-confirm bypass record" — a positive "no rule applied" record, not an absence), and the risk tier. `gate_results_json` is jsonb — emitting this block needs **no DDL**. Calibration sampling (B8) is the statistical backstop that keeps deemed approval safe: a non-zero fraction of deemed panels route to operator review.

**Three models.** *Model A — explicit operator confirm for every Registry action* is **rejected**: it contradicts Requirements Ch.5/Ch.6, and at thousands of concepts operator fatigue degrades the very governance quality it intends — mass rubber-stamping is weaker evidence than a panel verdict plus calibration sampling. *Model B — deemed-by-default* is the Ch.5 default. *Model C — risk-tiered hybrid* is Model B with a framework-default high-risk tier: routine low-risk operations auto-issue; high-risk operations (new governed vocabulary, supersession, lifecycle transition, anything policy-flagged) require explicit operator confirm. The build plan already anticipates Model C — B6 "judges … whether new governed terms require operator confirm."

| Dimension | A — confirm every action | B — deemed everywhere | C — risk-tiered hybrid |
|---|---|---|---|
| Throughput at thousands | fails | excellent | excellent (bulk auto; small confirm tier) |
| Auditability | per-item operator certifier, but rubber-stamp noise degrades it | good *iff* deemed provenance emitted | best — cert records tier + disposition |
| Human fatigue | severe — defeats Ch.6 "1 hour/day" | minimal | low — operator sees the high-risk minority + sampled |
| Governance quality | low — fatigued mass-approval is weak evidence | adequate; routine and consequential ops treated alike | highest — human attention concentrated where it matters |
| Rollback / correction | edit-non-active / supersession | + policy pause + sampling backstop | + the confirm tier prevents the worst classes pre-write |
| Invariant VI honesty | honest but per-item | honest *iff* deemed provenance emitted | honest *iff* per-tier disposition emitted |
| Requirements compliance | **contradicts Ch.5/Ch.6** | compliant (the Ch.5 default) | compliant (Ch.5 default + Ch.4/Ch.7 operator-confirm rules) |

**Locked stance — Model C (D3).** For **B6 v1**, the registry `framework_policy` is configured with **zero operator-confirm rules**, which makes bounded-write condition 7 ("no operator-confirm rule applies") genuinely and honestly true — so v1 needs no operator-confirm evaluation engine, and the `deemed_approval` block records `disposition: 'auto_issued', operator_confirm_rules_in_policy: 0`. v1's enabled op-scope is therefore the **low-risk tier only**; `registry_author_vocabulary`, `registry_supersede`, and `registry_transition` are owned by B6 but **not v1-enabled** until the confirm tier exists. The `deemed_approval` block is emitted **from day one** — Invariant VI makes it non-deferrable.

**Design fork.** The high-risk confirm tier — C5 evaluating operator-confirm rules, classifying risk, and recording the confirmation — is the **C5 Registry deemed-approval / operator-confirm extension**. It needs **no Phase A schema amendment** (`gate_results_json` is jsonb; `operator_confirm_rule` and `framework_policy` already carry `registry` scope), but it is a C5 service-architecture change and gets **its own design note** — a fork, not a v1 stitch. When built, the operator-confirm provenance should ride in `gate_results_json` (mirroring the BF/BO C7 precedent), avoiding a dedicated-table DDL fork.

## 10. Foundation and requirements grounding

The re-grounding (posture rule 3) produced these load-bearing constraints on B6:

- **Invariant I (meaning evaluated once).** B6 is the single Registry placement-meaning point. The legacy BF/BO dedup flows (`bf_dedup`, `bo_dedup`, `bf_pii_classify`, `bo_composer`) are narrow sub-checks — they must not become a second meaning-evaluation point. The build plan is explicit: they "may feed [B6] as input signals — they are not the panel."
- **Invariant III (immutable state).** `panel_output_record`, `certification_record`, and the Registry version rows are append-only. B6 emits new records; it never edits.
- **Invariant IV (explicit references).** Every reference B6 produces — `characteristic_id`, `target_entity_id`, `certification_record_id`, `panel_run_uid`, `target_registry_id` — is an explicit stored id. The Invariant IV "governed selection artifact" clause applies to characteristic selection: the F4 characteristic chosen carries a lifecycle and is referenced by id.
- **Invariant V (non-replayable).** Each B6 run is one act producing one `panel_run_uid`; re-running B6 produces a new record, never an identical one.
- **Invariant VI (evidence emitted, not inferred).** Decisive twice: (1) the REJECT evaluation's evidence is the `panel_output_record` itself (`verdict_code='REJECT'` + `defect_code`), which B6 emits on every run — so the first slice may park a REJECT with **no** `authoring_panel_rejection_log` write without violating Invariant VI; the rejection-log is a separate operator surface, deferred to the Bucket-2 fork (D2); (2) every issuance — deemed or operator-confirmed — must emit its approval disposition as evidence the `certification_record` carries; an unrecorded deemed decision is a silent bypass. This is why D3 (locked as Model C) mandates the `gate_results_json.deemed_approval` block, and why the high-risk-tier confirm path is its own design fork.
- **Requirements Ch.5 (authority principle).** "AI proposes, prepares, and approves context … Operator overrides as exception." Framework Approval = three-model consensus + closed-enum verdict + no-fabrication pass + immutable authoring record + calibration sampling + an active operator override. B6 must satisfy all six conditions for its APPROVE to be a valid Framework Approval.
- **Requirements Ch.7 (bounded-write discipline).** The seven-condition rule at line 543 is the contract B6 → C5 → F3 must collectively satisfy. C5's five Registry panel-evidence checks cover policy/consensus-evidence/grounding/sampling; the operator-pause and operator-confirm conditions are the unbuilt remainder (D3).

## 11. Disposition of prior artifacts (D6)

| Artifact | Disposition | Reason |
|---|---|---|
| `panel_output_record` (A5) + B4a ingest | **Reuse as-is** | Scope-agnostic; the §5 smoke proved C5 reads it for the Registry shape. |
| `certification_record` Registry shape (A6 + Phase A) | **Reuse as-is** | Built and live-proven (PR #67). |
| C5 `issueRegistryShapeCertification` | **Reuse; small S1 amendment** | S1 amends it to emit the `deemed_approval` block into `gate_results_json` (jsonb — no DDL). The high-risk operator-confirm *evaluation* (rule loading, risk classification, confirm record) is the later C5 extension fork (D3). |
| F3 `RegistryAuthoringService`, F4, F5 | **Reuse as-is** | The completed Registry substrate B6 is built to drive. |
| `operator_confirm_rule` table (gained `registry` scope) | **Reuse table; Registry evaluation path unbuilt** | The Phase A scope-add was additive; no Registry evaluator exists — D3. |
| `intake_queue` (C8, BF/BO) | **Replace — Bucket-2 Registry-native fork** | BF/BO-shaped (`admit_from_intake` produces BF/BO catalog rows); not reused as-is. The first slice uses inline candidates (D1); a Registry-native intake table is the later Bucket-2 DBCP fork (D2). |
| `authoring_panel_rejection_log` (C9, BF/BO) | **Replace — Bucket-2 Registry-native fork** | BF/BO-shaped; not reused as-is. The first slice writes no rejection-log row — non-APPROVE paths park/report, the `panel_output_record` carries the REJECT evidence. A Registry-native rejection surface is the Bucket-2 fork (D2). |
| BF/BO dedup flows (`bf_dedup`, `bo_dedup`, …) | **Retire as the panel; may survive as input sub-checks** | Per build plan §2 — not the panel; force-fitting B6 around them is prohibited by posture rule 1. |
| C5b seam (`certifyField` / `approveObject` graft) | **Not reused** | A BF/BO legacy-gate + C5 graft; B6 is Registry-native with its own orchestrator. |
| BCF Requirements Ch.4 / Ch.7 (BF/BO/CF-era framing) | **Evidence; amend** | Predate DEC-02f5a9's Registry model. The intake-queue and rejection-log *mandates* carry; their BF/BO-catalog-row *shape* does not. |

## 12. Locked decisions (D1–D6)

| ID | Decision | Lock |
|---|---|---|
| **D1** *(LOCKED)* | Intake substrate for the first slice | **Locked — inline candidates.** The first slice uses inline Registry intake candidates, **not** a Registry intake table. A Registry-native intake substrate remains the Bucket-2 / later DBCP fork (see D2). |
| **D2** *(LOCKED)* | Intake + rejection surfaces | **Locked — Bucket-2 Registry-native fork.** The BF/BO C8/C9 surfaces (`intake_queue`, `authoring_panel_rejection_log`) are **not reused as-is**; Registry-native intake + rejection surfaces are a Bucket-2 DBCP fork. For the first slice, non-APPROVE paths (REJECT, OPERATOR_REVIEW) **park and report only — no rejection-log write**; the emitted `panel_output_record` carries the REJECT evidence (Invariant VI). |
| **D3** *(LOCKED)* | Deemed-approval model + operator-confirm provenance | **Model C — LOCKED.** Deemed approval is the default bounded-write path when policy permits it; explicit operator confirm is required only when the policy / risk tier demands it; **every issuance emits the deemed-approval / confirm disposition in `gate_results_json` — no silent bypass, no missing evidence** (Invariant VI). Model A (confirm every action) is rejected — it contradicts Requirements Ch.5/Ch.6. v1: deemed issuance for the low-risk tier under a registry `framework_policy` with **zero operator-confirm rules**. The high-risk tier is the **C5 Registry deemed-approval / operator-confirm extension** — a design fork with its own note; no Phase A DDL (provenance rides in `gate_results_json`, mirroring C7). See §9.4. |
| **D4** *(LOCKED)* | B6 op scope + v1 first-slice scope | **Locked.** B6 *owns* create / add-version / author-vocabulary / raise-supersede; `registry_transition` stays B10 (Publication); proposal action/dismiss location is open for a later phase. **First-slice scope = low-risk only:** the `createEntity` prerequisite + the `createBusinessConcept` value concept. **No** vocabulary authoring, supersession, lifecycle transition, or proposal action/dismiss in v1 — those high-risk ops stay behind the operator-confirm design fork (D3). |
| **D5** *(LOCKED)* | Does F5 need an acyclic preview before the B6 build | **Locked — deferred.** The first slice authors a **value** concept only (no identity-bearing reference), so no acyclic preview is needed. Add a read-only `previewAcyclic` to F5 only when B6 first authors identity-bearing reference concepts. |
| **D6** *(LOCKED)* | Prior-artifact disposition after Foundation review | **Locked — per §11.** Reuse `panel_output_record` / `certification_record` / F3 / F4 / F5 / B4a where they fit; fork the intake + rejection surfaces as Bucket-2 Registry-native (D1/D2); retire the BF/BO dedup flows as panel authority — at most evidence / input sub-checks, never the panel. |

## 13. Recommended first slice

The first B6 slice is **`createBusinessConcept`** — authoring one **value concept** on an existing Entity, binding an existing F4 governed characteristic and an existing representation term. It is a `registry_create` / `business_concept` operation and unambiguously **low-risk** under the locked Model C (D3): it places a concept using already-governed vocabulary — it introduces no new vocabulary, supersedes nothing, transitions no lifecycle. `registerCharacteristic` is **not** the first slice — authoring new governed vocabulary is high-risk under Model C and stays behind the operator-confirm design fork (D3 / D4).

**Prerequisite — an existing Entity.** `bc_platform_dev` currently holds **0 `concept_registry.entity` rows and 0 `business_concept` rows** (only the F4 seed — 24 characteristics, 15 representation terms). So option (a) "reuse an existing dev entity" is unavailable, and `registry_add_version` is **not** a cleaner path — it would need the deepest prerequisite chain (an entity *and* a concept *and* a first version, none of which exist). The first slice therefore obtains its Entity via **option (b): author one prerequisite Entity through the existing C5 → F3 governed path.** `createEntity` is itself a low-risk `registry_create` operation, and the §5 Model A smoke already proved `createEntity` end to end through that chain. Concretely, the first-slice integration test mints the prerequisite Entity in-transaction via C5 → F3 `createEntity`, then runs the B6 panel → B4a → C5 → F3 `createBusinessConcept` slice, then rolls back — the same one-transaction pattern as `registry-shape-issuance.integration.spec.ts`. No back-door insert: the prerequisite is authored the governed way.

The slice runs **panel-approval-only**: a registry `framework_policy` with **zero operator-confirm rules** (deemed approval, bounded-write-honest — D3), the `gate_results_json.deemed_approval` block emitted on issuance, non-APPROVE paths (REJECT, OPERATOR_REVIEW) parking and reporting the candidate with **no rejection-log write** (D2), driven by inline candidates (D1). It exercises the full B6 panel → B4a → C5 → F3 chain — the C5 → F3 end is already proven by the §5 smoke — and isolates the genuinely new build (the bc-ai panel + the bc-core B6 orchestrator) from the Bucket-2 and high-risk-confirm forks.

The B6 build should begin with a design note / output contract — not code.

## 14. References

- `business-context-framework-build-plan.md` — §2 (B6 definition, Phase B components), §16 (F-components, critical path)
- `business-context-framework-phase-a-alignment-dbcp-bucket-1.md` — §2.4.4 (registry action codes), §2.4.6 (action_code → subject_kind matrix), §2.4.3 (subject kinds)
- `business-context-framework-requirements.md` — Ch.3 (Publication Eligibility / no-fabrication), Ch.4 (intake queue, operator-confirm policy), Ch.5 (division of labor), Ch.7 (Context Panels; bounded-write discipline, line 543)
- Foundation — `the-invariants.md` (Invariants I, III, IV, V, VI), `the-authority-model.md`
- bc-core — `src/registry/concept-registry/` (F3, F5, `certification-verifier.service.ts`), `src/registry/seed/f4-*` (F4), `src/registry/framework-approval/` (C5), `src/registry/panel-output-record.*` (B4a), `src/database/schema/contract/` and `src/database/schema/concept-registry/` (schema)
- DEC-02f5a9 (D414) — Business Concept Registry
