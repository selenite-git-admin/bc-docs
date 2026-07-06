---
id: business-context-framework-b6-slice-plan
title: "Business Context Framework — B6 Unified Registry Authoring Panel: Build Slice Plan"
description: "Draft build slice plan for B6 — locks the first slice (B6-S1, the low-risk inline-candidate createBusinessConcept path) and the implementation decisions D7–D10."
status: draft
authority: informative
date: 2026-05-22
project: bc-core
domain: business-context-framework
subdomain: registry-authoring-panel
focus: lifecycle
depends_on:
  - business-context-framework-b6-design-survey
  - business-context-framework-build-plan
  - business-context-framework-phase-a-alignment-dbcp-bucket-1
governing_adrs:
  - DEC-02f5a9
governing_sources:
  - B6 design survey (D1–D6 locked)
  - BCF Requirements Ch.5 / Ch.7 (deemed approval, bounded-write discipline)
  - Foundation — The Invariants (Invariant VI)
---

# Business Context Framework — B6 Unified Registry Authoring Panel: Build Slice Plan

## 1. Purpose and status

Draft build slice plan for B6, derived from the locked B6 design survey
(`business-context-framework-b6-design-survey.md`, D1–D6 locked). It locks the
first build slice — **B6-S1** — and the implementation decisions D7–D10 (§12). **Docs-only — no code follows from
this note directly; `status: draft`.** The note is descriptive-layer
(`authority: informative`): it introduces no invariant and overrides no ADR.

**S1 implies no DDL and no DB-execution gate.** Every table B6-S1 touches already exists; the `recommendation` and `deemed_approval` payloads ride in jsonb columns; the proof track (§4) writes nothing durable — it runs inside one rolled-back transaction. This slice plan requires no migration and no operator DB-execution approval.

## 2. Slice list

| Slice | Scope | State |
|---|---|---|
| **B6-S1** | Low-risk inline-candidate authoring path — `createBusinessConcept` (value concept) end to end: panel → B4a → orchestrator → C5 deemed issuance → F3 write + stamp | **LOCKED (this note)** |
| B6-S2 | Extend the low-risk tier — `createEntity` and `addBusinessConceptVersion` as first-class panel-proposed B6 operations (S1 already exercises `createEntity` as a test prerequisite) | proposed |
| B6-S3 | High-risk tier — the C5 Registry deemed-approval / operator-confirm extension (D3) + `registry_author_vocabulary` and `registry_supersede` | proposed |
| B6-S4 | Registry-native intake substrate + rejection-log surface (the Bucket-2 DBCP fork — D1/D2) | proposed |

Publication (B10) and Lifecycle Audit (B11) are separate Phase B panels, outside the B6 slice line.

## 3. B6-S1 — the locked first slice

B6-S1 is the **low-risk inline-candidate authoring path**. Five steps:

1. **Inline candidate** enters the bc-core / bc-ai path — no intake table (D1); the candidate is an orchestrator DTO / fixture (D7).
2. **bc-ai B6 panel** (Maker / Checker / Moderator) judges placement and emits a `panel_output_record` via B4a, carrying `verdict_payload_json.recommendation` (§5).
3. **bc-core B6 orchestrator** reads the emitted record and **validates the recommendation contract**.
4. On `APPROVE_FOR_DRAFT`: **C5 `issueRegistryShapeCertification`** issues a born-null Registry-shape `certification_record`, emitting the **deemed-approval evidence** in `gate_results_json` (§6).
5. **F3 `RegistryAuthoringService.createBusinessConcept`** executes the write and stamps `target_registry_id` on the cert.

**Operation:** `createBusinessConcept` — a **value concept** (`kind='value'`, `identityRole='descriptive'`) on an existing Entity, binding an existing F4 characteristic and an existing representation term. §2.4.6: `action_code = registry_create`, `subject_kind = business_concept`. Low-risk under the locked Model C (D3): it places a concept with already-governed vocabulary — no new vocabulary, no supersession, no lifecycle transition.

B6-S1 is delivered in **two clearly-separated tracks** — see §4.

## 4. The two B6-S1 tracks

B6-S1 is delivered as two clearly-separated tracks. Track 1 is provable now and depends on no bc-ai component; Track 2 is the live path and depends on the bc-ai build.

### Track 1 — bc-core proof track

The bc-core orchestrator + the C5 `deemed_approval` amendment, verified by a gated integration test driven by a **direct `panel_output_record` fixture** (no bc-ai). `bc_platform_dev` holds 0 entities / 0 business_concepts, so the whole proof runs inside **one rolled-back transaction**, mirroring `registry-shape-issuance.integration.spec.ts` (`BCCORE_INTEGRATION_DB=1`):

1. **Policy fixture** — create a minimal registry-scoped `framework_policy` fixture in-transaction: `scope='registry'`, zero operator-confirm rules, a `policy_version` (D9). No durable policy seed.
2. **Prerequisite Entity** — author one Entity through the governed C5 → F3 path: a fixture `panel_output_record` → `issueRegistryShapeCertification` → `RegistryAuthoringService.createEntity`. `createEntity` is itself a low-risk `registry_create` op; the §5 Model A smoke proved it. Not a back-door insert — the governed path.
3. **B6-S1 proper** — insert the B6-S1 `panel_output_record` directly as a fixture (`verdict_code='APPROVE_FOR_DRAFT'` + the §5 recommendation), run the orchestrator (steps 3–5 of §3) → C5 deemed issuance → F3 `createBusinessConcept` + `target_registry_id` stamp.
4. **Non-APPROVE case** — a fixture `panel_output_record` with `verdict_code='REJECT'`: assert the orchestrator parks/reports and writes **no** cert, **no** Registry row, **no** rejection-log row (§10).
5. **Roll back** — independent post-run counts confirm zero durable rows.

**No durable DB writes occur outside this rolled-back transaction.** Track 1 needs no bc-ai component and is provable now.

### Track 2 — live bc-ai path

The genuinely new build: the bc-ai `bcf-authoring-panel` (Maker / Checker / Moderator) producing a real verdict + recommendation; the **B4b** emitter posting the `panel_output_record` to B4a; and **F5 context delivery to bc-ai**.

Per D8, the F5 HTTP read API is **not** built inside S1 unless the bc-ai integration absolutely requires it — "F5 context delivery to bc-ai" is a B6-S1 live-path interface decision, with the preferred later shape being a bounded **authoring-context packet** prepared by bc-core, rather than bc-ai free-querying the Registry.

Track 2 also requires a **durable** registry `framework_policy` row — created as a separate governed config/data step before the orchestrator is enabled for the live path (D9). Track 2 depends on the bc-ai build.

## 5. The `verdict_payload_json.recommendation` contract

bc-ai-authored free jsonb (the B4a DTO does not constrain `verdict_payload_json`). B6 fixes the sub-schema by convention; the bc-core orchestrator validates it on read (step 3).

```
verdict_code = 'APPROVE_FOR_DRAFT'
verdict_payload_json = {
  recommendation: {
    proposed_operation: {
      subject_kind: 'business_concept',
      action_code:  'registry_create',
      f3_operation: 'createBusinessConcept',
      f3_input: {
        entityId:           string,   // the prerequisite Entity
        kind:               'value',
        identityRole:       'descriptive',
        characteristicId:   string,   // an existing F4 characteristic (uuid)
        representationTerm: string,   // an existing representation term (text)
        definition:         string,
        dataType?:          string,
        unit?:              string,
        semanticRole?:      string
      }
    },
    placement_rationale: string,        // why this entity / value-kind / this characteristic
    evidence: {
      source_citations: string[],       // source rows / system / field provenance
      grounding_basis:  string          // the no-fabrication justification
    },
    operator_confirm_required: false,   // S1 low-risk tier — always false; the
                                        // orchestrator rejects true in S1
    candidate_ref: string               // the inline candidate id (D7)
  }
}

verdict_code = 'REJECT'           → verdict_payload_json = { defect_code: <one of the 9> }
verdict_code = 'OPERATOR_REVIEW'  → verdict_payload_json = { review_reason: string }
```

**Orchestrator validation (step 3)** — reject the panel record if: `verdict_code` is not one of the three; on `APPROVE_FOR_DRAFT` the `recommendation` is absent or malformed; `proposed_operation` is not exactly `registry_create` / `business_concept` / `createBusinessConcept` (S1 is single-operation); `f3_input` is not a well-formed value-concept input; or `operator_confirm_required` is `true` (S1 carries no high-risk tier — a `true` routes to operator-review, it does not auto-issue).

## 6. The `gate_results_json.deemed_approval` block

On `APPROVE_FOR_DRAFT`, C5 writes the cert's `gate_results_json` with the five existing panel-evidence flags **plus** the `deemed_approval` block:

```
gate_results_json = {
  panel_record_found:    true,
  stage_authoring:       true,
  grounding_pass:        true,
  verdict_approved:      true,
  policy_version_matched: true,
  deemed_approval: {
    disposition:                     'auto_issued',
    risk_tier:                       'low',
    policy_version:                  string,   // the registry policy version
    governing_policy_uid:            string,   // the registry framework_policy uid
    operator_confirm_rule_disposition: 'no_rule_applied',
    operator_confirm_rules_in_policy:  0
  }
}
```

`operator_confirm_rule_disposition: 'no_rule_applied'` is the BCF Requirements Ch.7 "operator-confirm bypass record" — a **positive** record that no rule applied, not an absence. Emitting this block is mandatory from S1 (D3; Invariant VI — an unrecorded deemed decision is a silent bypass). It rides in the jsonb `gate_results_json` column — **no DDL**. Emitting it is a small S1 amendment to C5 (§8).

## 7. The registry `framework_policy` row (D9)

B6-S1 needs a registry-scoped `framework_policy` carrying: `scope='registry'` (the additive Phase A scope value); **zero operator-confirm rules** — which makes bounded-write condition 7 ("no operator-confirm rule applies") genuinely true, the foundation of the deemed-approval honesty; and a `policy_version` string — carried by the panel (`panel_output_record.policy_version`), asserted on the `issueRegistryShapeCertification` call, string-matched by C5, and recorded in the cert NF1 `policy_version` field and the `deemed_approval` block.

Per **D9 (locked)**: for **Track 1** the policy is a **transaction-scoped fixture** created inside the rolled-back test — **no durable policy seed**. For **Track 2** durable policy creation is a **separate governed config/data step** before the orchestrator is enabled. Either way it is a data/config row — **no schema change** (`framework_policy` already carries `registry` scope). C5's S1 amendment loads this policy and emits the `deemed_approval` evidence (§6, §8).

## 8. bc-core module plan

| Component | Location (proposed) | Role |
|---|---|---|
| `RegistryAuthoringPanelModule` (B6) | `src/registry/registry-authoring-panel/` | New NestJS module. Imports `FrameworkApprovalModule` (→ `FrameworkApprovalService`) and `RegistryAuthoringModule` (→ `RegistryAuthoringService`). |
| `RegistryAuthoringOrchestrator` | same module | The post-panel driver. Reads the `panel_output_record`; validates the `recommendation` (§5); on `APPROVE_FOR_DRAFT` calls `issueRegistryShapeCertification` then `RegistryAuthoringService.createBusinessConcept`; on non-APPROVE parks/reports (§10). Holds subject/action continuity panel → C5 → F3. |
| `RegistryIntakeCandidate` DTO + `RegistryRecommendation` contract type + validator | same module | The inline-candidate carrier (D7) and the §5 contract type, validated on orchestrator read. |
| Orchestrator entry point | same module | A controller endpoint or a B4a-ingest hook — coupled to D7/D8; left open. |
| **C5 amendment** | `src/registry/framework-approval/` (in-boundary) | `issueRegistryShapeCertification` (+ `WriteRegistryShapeRowInput` / `writeRegistryShapeRow`) amended to: load the registry `framework_policy` via the already-injected `FrameworkPolicyRepository`, confirm zero operator-confirm rules, and emit the `deemed_approval` block into `gate_results_json` (§6). jsonb — no DDL. |
| S1 integration test | `src/registry/registry-authoring-panel/*.integration.spec.ts` | The §4 Track 1 gated, rolled-back smoke. |

The orchestrator and its module sit **outside** `framework-approval/`, so the C5 sole-writer grep guard is not engaged — `FrameworkApprovalService` and `RegistryAuthoringService` are the public DI seams. The panel-output read is the orchestrator's own (a `contract` table; reads are not boundary-restricted).

## 9. bc-ai responsibilities

- **`bcf-authoring-panel`** — the Maker (Gemini) / Checker (GPT-5.5) / Moderator (Opus) trio: placement judgment, three-model consensus, and the §5 verdict + recommendation. For S1 the panel only needs to produce a `createBusinessConcept` value-concept recommendation.
- **B2 input-hash** and **B3 no-fabrication grounding check** — computed bc-ai-side; `input_hash` (`sha256:…`) and `grounding_check_result` ride on the emitted record.
- **B4b emitter** — POSTs the `panel_output_record` to B4a (`POST /api/bcf/panel-output-records`). B4b does not exist today.
- Build-plan prerequisites: **B1** (`AgentRole` `GATE` → `MODERATOR`) and **B5** (closed-enum verdict harmonization), bc-ai-side.

## 10. Non-APPROVE handling (S1)

On `REJECT` or `OPERATOR_REVIEW`: the `panel_output_record` is still emitted, carrying the verdict and the `defect_code` / `review_reason`. **That panel record is the evaluation evidence** (Invariant VI — satisfied). The orchestrator **parks** the candidate — no Registry write, no cert — and **reports** the outcome (returns it to the caller / an Activity-Log entry). **No `authoring_panel_rejection_log` write in S1** (D2): the rejection-log operator surface is the Bucket-2 fork. Parking with the panel record emitted is *not* a silent drop.

## 11. Out of scope for B6-S1

Explicitly excluded from this slice:

- **Registry intake table** — S1 uses inline candidates (D1); persistence is the Bucket-2 fork.
- **Rejection-log DBCP** — no `authoring_panel_rejection_log` write; the Registry-native rejection surface is the Bucket-2 fork (D2).
- **Operator-confirm high-risk tier** — the C5 Registry deemed-approval / operator-confirm extension is the S3 design fork (D3).
- **Supersession, lifecycle transition, proposal action/dismiss** — out of v1 (D4).
- **F5 acyclic preview** — deferred; S1 authors a value concept, no identity-bearing reference (D5).
- **HTTP F5 read API** — not built unless D8 requires it for bc-ai.

## 12. Implementation decisions — D7–D10 (locked)

| ID | Decision | Lock |
|---|---|---|
| **D7** *(LOCKED)* | Inline-candidate home for B6-S1 | **Orchestrator DTO / test fixture only.** The inline candidate lives as a `RegistryIntakeCandidate` orchestrator DTO / test fixture — **no table, no durable intake row**. The durable evidence is the `panel_output_record` plus the downstream cert / version rows. Registry-native intake is deferred to B6-S4 / Bucket-2. |
| **D8** *(LOCKED)* | How bc-ai gets F5 placement context | Track 1 (bc-core proof): pre-enrich the test fixture directly from F5 / in-process reads. Track 2 (live): do **not** build the F5 HTTP API inside S1 unless the bc-ai integration absolutely requires it — "F5 context delivery to bc-ai" is a B6-S1 live-path interface decision. Preferred later shape: bc-core prepares a bounded **authoring-context packet** for bc-ai, rather than bc-ai free-querying the Registry. |
| **D9** *(LOCKED)* | The registry `framework_policy` row | Track 1: a minimal registry-scoped policy **fixture** created inside the rolled-back test transaction — **no durable policy seed**. Track 2: durable policy creation is a separate governed config/data step before the orchestrator is enabled. The policy carries **zero operator-confirm rules**; C5 emits `deemed_approval` evidence that policy allowed auto-issuance and no confirm rule was unmet. No schema change. |
| **D10** *(LOCKED)* | First smoke vocabulary | **Characteristic `unit price`, representation term `amount`.** Both are already-live F4 / F2 governed vocabulary, value-concept-friendly: no identity-bearing reference, no acyclic preview, no new vocabulary. |

## 13. Blockers

- **Track 1 (bc-core proof) has no blockers.** It depends on no bc-ai component — the orchestrator, the C5 `deemed_approval` amendment, and the integration test (driven by a direct `panel_output_record` fixture) are buildable now. No DDL, no durable writes, no execution gate.
- **Track 2 (live bc-ai path)** is blocked on the bc-ai build: the B6 `bcf-authoring-panel` and the **B4b** emitter do not exist. "F5 context delivery to bc-ai" is the open live-path interface decision (D8) — to settle when Track 2 is scheduled.
- **D7–D10 — locked** (§12); no longer open.
- **No DDL / no execution-gate blocker** — every S1 table exists; `recommendation` and `deemed_approval` ride in jsonb columns; the proof track writes nothing durable.

## 14. References

- `business-context-framework-b6-design-survey.md` — D1–D6 locked; the analysis this plan builds on
- `business-context-framework-build-plan.md` — §2 (B6, B1–B5 prerequisites), §16
- `business-context-framework-phase-a-alignment-dbcp-bucket-1.md` — §2.4.4 / §2.4.6
- `business-context-framework-requirements.md` — Ch.5 (authority principle), Ch.7 (bounded-write discipline)
- Foundation — `the-invariants.md` (Invariant VI)
- bc-core — `src/registry/framework-approval/` (C5), `src/registry/concept-registry/` (F3, F5), `src/registry/seed/f4-*` (F4), `src/registry/panel-output-record.*` (B4a), `registry-shape-issuance.integration.spec.ts` (the §5 smoke pattern)
- DEC-02f5a9 (D414) — Business Concept Registry
