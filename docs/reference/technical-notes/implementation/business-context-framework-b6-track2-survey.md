---
id: business-context-framework-b6-track2-survey
title: "Business Context Framework — B6 Track 2 (live bc-ai panel): Design Survey"
description: "Draft design survey for B6 Track 2 — the live registry-authoring bc-ai flow, bounded F5 context delivery, and the bc-core run entry point. Locks the Track 2 decisions and names the durable registry framework_policy prerequisite gate."
status: draft
authority: informative
date: 2026-05-22
project: bc-core
domain: business-context-framework
subdomain: registry-authoring-panel
focus: lifecycle
depends_on:
  - business-context-framework-b6-design-survey
  - business-context-framework-b6-slice-plan
  - business-context-framework-build-plan
governing_adrs:
  - DEC-02f5a9
governing_sources:
  - B6 design survey (D1–D6) + B6 slice plan (B6-S1, D7–D10)
  - BCF Requirements Ch.7 (Context Panels; framework policy is a governed authoring act)
  - Foundation — The Invariants (Invariant VI)
---

# Business Context Framework — B6 Track 2 (live bc-ai panel): Design Survey

## 1. Purpose and status

Draft design survey for **B6 Track 2** — the live path of the B6 Unified Registry
Authoring Panel: the bc-ai `registry-authoring` flow, bounded F5 context delivery,
and the bc-core run entry point. It locks the Track 2 decisions and names the one
prerequisite gate (the durable registry `framework_policy` row). **Docs-only — no
code, no branch, no PR follows from this note.** Descriptive-layer
(`authority: informative`): it introduces no invariant and overrides no ADR.

Track 1 (the bc-core proof track — `RegistryAuthoringOrchestrator`, the
recommendation validator, the C5 deemed-approval amendment) is merged on `main`.

## 2. The reframe — four distinct things, kept separate

The B6 slice plan §13 listed **B4b (the bc-ai emitter) as "does not exist"** — that
was inferred from the bc-core side and is **wrong**. The bc-ai repo
(`C:\MyProjects\bc-ai`) already has the AI Panel machinery built and live:

| Component | bc-ai state |
|---|---|
| Maker/Checker/Moderator agent pattern (`BaseAgent`) | built — `app/agents/base.py`; the `run_pipeline` orchestrator drives 12 live `/api/ai/suggest/*` flows |
| B1 — `AgentRole` `MAKER`/`CHECKER`/`MODERATOR` | done (enum-value migration complete) |
| Model roster — Maker=Gemini-2.5-flash · Checker=GPT-5.5 · Moderator=Opus-4.5 | wired to the plan targets — `app/models/registry.py` |
| B2 — input hash (`sha256:`+64 hex) | built — `app/pipeline/input_hash.py` |
| B3 — grounding / no-fabrication | **framework built — nominal** (see §7); `app/pipeline/grounding.py` |
| B4b — panel-output emitter | **built** — `app/pipeline/panel_output_emitter.py`; emits to bc-core B4a at every terminal verdict |
| Cognito service-user auth (bc-ai → bc-core) | built — `app/clients/bc_core_auth.py` |

Track 2 distinguishes **four things** and never conflates them:

1. **The reusable AI Panel substrate** — everything in the table above, reused
   **unchanged**: the `BaseAgent` maker/checker/moderator base class, the model
   roster, the B2 input hash, the B3 grounding helper, the B4b
   `panel_output_record` emitter, the Cognito service-user auth, the prompt
   loader, and the `/api/ai/suggest/*` endpoint conventions. Track 2 builds **no**
   second panel runtime.

2. **The B6-specific panel entry point** — *new* in T2-S2: a Registry-native
   panel function over the substrate (#1), **not** the legacy `run_pipeline`.
   `run_pipeline` collapses every terminal verdict into operational pass/fail
   (`APPROVE_FOR_DRAFT` / `FAIL_QA_GATE` / `FAIL_MAX_RETRIES`), carries a QA
   retry loop, and writes the legacy `evidence_store`. B6 needs none of that — it
   emits **content** verdicts, has **no** retry loop, and writes **no**
   `evidence_store` row (its only write stays the `panel_output_record` via B4b).
   Forcing B6 verdict semantics into `run_pipeline` would be a stitch; the
   B6-specific entry point is the clean alternative (T2-S2 lock — §3 L7).

3. **Registry-native basic support services / checks** — the panel is **not**
   "three agents over raw JSON." Its architecture is **six required B6-S1 evidence
   classes** (§6, L8) that the Maker/Checker/Moderator each reason over. The
   evidence classes are the architecture; packet fields, top-N retrieval, and
   candidate-neighborhood mechanics are **retrieval tactics**, not the
   architecture. The bc-core/F5 bounded context packet is the **v1 retrieval
   vehicle** that supplies material for the evidence classes. If the packet lacks
   enough material for an evidence class, the panel emits `OPERATOR_REVIEW` or the
   PR surfaces a **context-packet gap** — it does **not** fabricate the missing
   context, invent source evidence, reach for another data source, or call a
   BF/BO flow.

4. **The old BF/BO flows — explicitly out of bounds.** `bf_dedup`,
   `bf_pii_classify`, `bo_dedup`, `bo_composer` are narrow legacy use-cases.
   Track 2 does not call them, route through their prompts, or reuse their verdict
   logic. The `registry-authoring` flow is built directly against the Registry
   context packet (#3) and the B6-S1 recommendation contract. Any future salvage
   of their logic is a separate review, as non-authoritative evidence only.

**Track 2's genuinely new work** is therefore: (a) the B6-specific panel entry
point (#2) plus the `registry-authoring` Maker/Checker/Moderator agents and
prompts (#3); (b) bounded F5 context delivery; (c) a bc-core B6-run entry point
that wires candidate → bc-ai → the `RegistryAuthoringOrchestrator`. It is **not**
"build the panel runtime."

## 3. Locked decisions

| ID | Lock |
|---|---|
| **L1 — F5 context delivery** | **Option A, push variant.** bc-core prepares a bounded authoring-context packet **in-process** (F5 `RegistryReadService` reads) and sends it to bc-ai in the flow request body. **No new F5 HTTP read API in Track 2.** bc-ai must not free-query the Registry — it receives a fixed packet and nothing more. |
| **L2 — run endpoint + auth** | One new bc-core **operator/importer-facing platform endpoint** — the B6-run entry point — guarded by **existing platform auth**. The exact guard (decorator, scope) is confirmed against current controller conventions at build/review time, not pre-specified here (`@PlatformOnly()` is the likely guard). bc-core→bc-ai and bc-ai→bc-core auth already exist and are reused unchanged. |
| **L3 — durable registry `framework_policy` row** | A **separate prerequisite gate** (T2-S0, §9). The durable active `registry` policy with zero operator-confirm rules is **authority-bearing governance data** — it must be authored or seeded through a governed step, **not inserted ad hoc**. It is not DDL, but it gets its own small design/gate before live Track 2. |
| **L4 — B3 grounding** | The grounding **framework exists** but is **nominal** — it passes by default because no agent declares `grounded_fields`. The B6 `registry-authoring` flow must **make grounding effective** by declaring grounded fields and citations; otherwise grounding is in name only. |
| **L5 — verdict production** | The bc-ai `registry-authoring` flow must support **all three verdicts** — `APPROVE_FOR_DRAFT`, `REJECT`, `OPERATOR_REVIEW`. Non-APPROVE evidence is the emitted `panel_output_record`; **no C8/C9 rejection-log write in Track 2.** |
| **L6 — boundary** | bc-ai writes only `panel_output_record` (through B4b); the bc-core `RegistryAuthoringOrchestrator` remains the only post-panel executor; no intake table; no rejection-log write; no operator-confirm high-risk tier; no BF/BO legacy-surface stitching. |
| **L7 — B6 panel entry point** | **Option 2 (locked, T2-S2).** Track 2 builds a **B6-specific panel entry point** over the reused substrate (§2 #1) — **not** an extension of `run_pipeline`. The entry point runs the trio in a single pass: **no QA retry loop**, **no legacy `evidence_store` write**; the Moderator emits the closed B6 **content** verdict (`APPROVE_FOR_DRAFT` / `REJECT` / `OPERATOR_REVIEW`) and its `verdict_payload`. `REJECT` and `OPERATOR_REVIEW` are content verdicts, not failed QA attempts. The substrate — `BaseAgent`, model roster, B2 hash, B3 grounding, B4b emitter, prompt loader, endpoint conventions — is reused unchanged. Each role reasons explicitly over the six evidence classes (L8 / §6); insufficient material for a class is surfaced as `OPERATOR_REVIEW` or a context-packet gap, never compensated by a BF/BO flow. |
| **L8 — evidence classes first** | **The architecture is the six B6-S1 evidence classes (§6); retrieval is tactics.** The panel reasoning is defined by six required evidence classes — (1) entity placement judgment; (2) duplicate / synonym / homonym risk; (3) existing concepts / value-concept placement; (4) characteristic + representation-term fit; (5) source / provenance grounding; (6) omissions / truncation / context-gap disclosure. Packet fields, top-N, and candidate-neighborhood mechanics are **retrieval tactics**, not the architecture. The T2-S1 packet is the **v1 retrieval vehicle**; insufficient material for any class → `OPERATOR_REVIEW` or a surfaced context-packet gap. **Provenance split:** candidate source/citation fields (if present) are source evidence for the candidate's business *meaning*; Registry ids/context are *grounding* for placement & vocabulary fit; Registry ids are **not**, by themselves, external source evidence for meaning. |

## 4. B4b emitter

**Already built.** `emit_panel_output_record` (`app/pipeline/panel_output_emitter.py`)
POSTs the camelCase `CreatePanelOutputRecordDto` to bc-core `POST /api/bcf/panel-output-records`
(B4a); auth via the Cognito service-user ID token (`get_bc_core_auth_headers`); the
orchestrator calls it at every terminal verdict and receives the `panel_run_uid`.
The DTO it builds already carries `model_identity_json` (the
{maker,checker,moderator}×{provider,model_version} roster), `agent_outputs_json`
(per-role transcripts), `input_hash`, `policy_version`, `grounding_check_result` /
`quarantined`, `stage_code='authoring'`, `verdict_code`.

The **only emitter-side new work**: the `registry-authoring` flow's
`verdict_payload_json` must carry the B6-S1 `recommendation` object (§6) on
`APPROVE_FOR_DRAFT`, the `defect_code` on `REJECT`, the `review_reason` on
`OPERATOR_REVIEW`. The emitter and the B4a ingest contract are unchanged.

## 5. F5 context delivery (L1 — Option A push)

bc-core's B6-run service builds a **bounded authoring-context packet** in-process
via `RegistryReadService` and pushes it to bc-ai inside the flow request. bc-ai is a
pure `{candidate + context packet} → {verdict + recommendation}` function; its only
outbound call stays the B4b emitter. This keeps **no new bc-core F5 read endpoint
and no bc-ai Registry query surface**.

The packet (fixed shape, for a `createBusinessConcept` candidate): candidate name +
definition; entity-placement options (`findByNormalizedName('entity', …)` +
`listEntities` summaries); existing concepts on the candidate entity
(`listConceptsForEntity`); the F4 governed characteristic vocabulary
(`listCharacteristics`); the representation-term set (`listRepresentationTerms`). A
bounded packet — never a query API. The exact packet contract is T2-S1 work.

## 6. Panel contract

The panel runs through the **B6-specific entry point** (§3 L7) over the reused
substrate — **not** `run_pipeline`. One pass, no retry loop; the only write is the
`panel_output_record` via B4b.

**The six B6-S1 evidence classes — the architecture (L8).** The panel's reasoning
is defined by six required evidence classes. They are the architecture; packet
fields, top-N retrieval, and candidate-neighborhood mechanics are **retrieval
tactics**. Each role reasons over all six:

| # | Evidence class | What the panel must judge | v1 retrieval vehicle (T2-S1 packet) |
|---|---|---|---|
| 1 | Entity placement judgment | is the candidate placed on the right entity (existing vs new)? | `selectedEntity`, `entityPlacementCandidates` |
| 2 | Duplicate / synonym / homonym risk | is the proposed concept a duplicate, or a synonym / homonym collision? | `entityPlacementCandidates`, `existingConceptsForEntity` |
| 3 | Existing concepts / value-concept placement | does the value concept collide with concepts already on the selected entity? | `existingConceptsForEntity` |
| 4 | Characteristic + representation-term fit | does `characteristicId` bind a governed term, and `representationTerm` come from the closed set? | `activeCharacteristics`, `representationTerms` |
| 5 | Source / provenance grounding | candidate source/citation fields (if present) ground the candidate's business *meaning*; Registry ids/context ground *placement & vocabulary fit* — and only that | candidate fields (none in the v1 candidate DTO → `source_citations: []`); packet governed ids = grounding |
| 6 | Omissions / truncation / context-gap disclosure | the panel must disclose what was omitted, truncated, or missing from its context | the panel's own self-assessment over classes 1–5 |

**The packet is the v1 retrieval vehicle, not the architecture.** If it lacks
enough material for an evidence class: a **structurally malformed** packet (a
required field missing / wrong type) is rejected at the endpoint boundary; a
**present-but-insufficient** class yields `OPERATOR_REVIEW` with a `review_reason`
naming the **context-packet gap**. The panel never fabricates the missing context,
**invents source evidence**, reaches for another data source, or calls a BF/BO
flow. A material omission / truncation under class 6 is itself a reason for
`OPERATOR_REVIEW`.

**Roles** (the substrate trio; models per the roster):
- **Maker (Gemini)** — proposes placement (existing-vs-new entity, value concept,
  characteristic + representation-term binding, definition) and **drafts the
  recommendation**, addressing all six evidence classes.
- **Checker (GPT-5.5)** — independently **verifies the draft against all six
  evidence classes**: synonym / homonym risk, definition discipline, the §2.4.6
  `(action_code, subject_kind)` pairing, characteristic + representation-term fit,
  provenance-grounding honesty, no-fabrication, and disclosed omissions.
- **Moderator (Opus)** — consensus over Maker + Checker; **emits the closed B6
  content verdict and `verdict_payload`** (L5), consistent with the six classes.

**Prompt input:** the bounded F5 context packet (§5) — the candidate and the v1
retrieval material for the six evidence classes — plus `policy_version`. T2-S2
carries **no separate seed/provenance bundle**: the packet is the entire input
(L1), and `policy_version` is hashed alongside it by B2 (§7).

**Output — must match the B6-S1 recommendation validator exactly**
(`recommendation.validator.ts`). On `APPROVE_FOR_DRAFT`, `verdict_payload_json`:

```
recommendation: {
  proposed_operation: { subject_kind: 'business_concept', action_code: 'registry_create',
                        f3_operation: 'createBusinessConcept',
                        f3_input: { entityId, kind: 'value', identityRole: 'descriptive',
                                    characteristicId, representationTerm, definition, … } },
  placement_rationale, evidence: { source_citations[], grounding_basis },
  operator_confirm_required: false, candidate_ref
}
```

On **`REJECT`** → `verdict_code='REJECT'`, `verdict_payload_json={ defect_code }`
(one of the nine). On **`OPERATOR_REVIEW`** → `verdict_code='OPERATOR_REVIEW'`,
`verdict_payload_json={ review_reason }`. The current bc-ai pipeline produces only
`APPROVE_FOR_DRAFT` — L5 locks that the new flow must produce all three.

## 7. Provenance

- **Input hash (B2)** — `compute_input_hash(row_payload=context_packet,
  seed_bundle={}, policy_version)` → `sha256:…`. T2-S2 has no separate seed
  bundle; the bounded F5 context packet is the row payload and the active
  `policy_version` is hashed alongside it.
- **Model identity** — the roster; the emitter already builds `model_identity_json`.
- **Source / provenance (evidence class 5).** `recommendation.evidence.source_citations`
  carries **source evidence for the candidate's business meaning**, drawn from the
  candidate's own source/citation fields. The v1 candidate DTO carries none, so v1
  `source_citations` is honestly `[]` — the panel does **not** invent them.
  `recommendation.evidence.grounding_basis` carries the **placement & vocabulary-fit
  grounding** derived from the Registry ids/context in the packet. Registry ids are
  **grounding**, not — by themselves — external source evidence for the candidate's
  meaning; the two are never conflated.
- **Grounding (B3) — nominal until made effective (L4).** The framework exists but
  passes by default; the `registry-authoring` flow's agents must declare
  `grounded_fields` over the recommendation's grounded content (entity id,
  characteristic id, citations) for grounding to verify anything.
- **Non-APPROVE evidence.** A `REJECT` / `OPERATOR_REVIEW` still emits a
  `panel_output_record` (verdict + `defect_code` / `review_reason` + transcripts).
  That record **is** the emitted evidence (Invariant VI); the B6-S1 orchestrator
  parks reading it — no rejection-log row.

## 8. Boundary (L6)

- bc-ai writes only `panel_output_record`, and only through B4b — an
  authoring-record write owned by B4a. It writes no Registry rows and no certs.
- The bc-core `RegistryAuthoringOrchestrator.runS1` remains the **only** post-panel
  executor (C5 issuance → F3 write).
- No C8/C9 rejection-log write — the orchestrator parks non-APPROVE.
- No operator-confirm high-risk tier — the registry `framework_policy` stays
  zero-rule (deemed approval).
- No intake table — the candidate is a request DTO on the B6-run endpoint (D7);
  the Bucket-2 intake substrate stays deferred.
- No BF/BO legacy-surface stitching — `registry-authoring` is a new Registry-native
  flow; the legacy `bf_dedup` / `bo_dedup` flows are untouched.

## 9. Prerequisite gate — the durable registry `framework_policy` row (T2-S0)

**This is the main blocker and gets its own small gate before live Track 2.**

Live Track 2 needs a **durable, active `registry` `framework_policy` row** with
**zero operator-confirm rules**: the live panel stamps its `policy_version` on the
`panel_output_record`, and C5 (`issueRegistryShapeCertification`, inside `runS1`)
resolves the active registry policy and asserts the version matches. Without it,
every live B6 issuance returns `not_issued: registry_policy_not_found`.

It is **not DDL** — the `framework_policy` table exists and already admits
`scope_code='registry'` (Phase A). It is **authority-bearing governance data**:
BCF Requirements Ch.7 states the framework policy is operator-authored and that
policy creation/change is itself a governed authoring act (recorded justification,
Activity-Log event, ADR-style change record, versioned). It must therefore be
created through a governed step — **not an ad-hoc `INSERT`**.

**The open design question for this gate:** how the v1 registry policy row is
authored or seeded. Candidate approaches:
- a small registry-policy **seed** (analogous to the F4 `seed-governed-vocabulary`
  module), with `framework_policy.adr_ref = DEC-02f5a9` and a recorded change
  record binding it to the governing decision;
- a **policy-authoring service** — `FrameworkPolicyRepository` is read-only today;
  a governed write path would be the fuller Requirements-Ch.7 mechanism;
- a one-time governed authoring act.

The row's locked content (whichever path): `scope_code='registry'`,
`operator_confirm_rules_uid_list = {}` (zero rules), a `policy_version` string,
`effective_to = NULL` (active), `adr_ref` bound to DEC-02f5a9. The
`framework_policy_active_per_scope_uniq` index guarantees at most one active
registry policy.

This survey does **not** lock the creation path — it names the gate. The gate
should be opened and decided before T2-S4 (the live smoke), and treated with the
same care as a schema change even though it is data.

## 10. Revised Track 2 slice list

| Slice | Scope | State |
|---|---|---|
| **T2-S0** | Durable registry `framework_policy` prerequisite — the governed config/data creation gate (§9). | **applied** — governed seed migration, `bc_platform_dev` |
| **T2-S1** | The authoring-context-packet contract + the bc-core B6-run service & operator/importer-facing platform endpoint + the bc-core→bc-ai client call. | **merged** — bc-core PR #70 |
| **T2-S2** | The B6-specific panel entry point (L7) over the reused substrate + the `registry-authoring` Maker/Checker/Moderator agents & prompts. | **merged** — bc-ai PR #14 |
| **T2-S3** | Emitter integration — the `panel_output_record` carries `verdict_payload_json.recommendation` in the B6-S1 validator shape; an independent contract mirror guards drift. | **merged** — bc-ai PR #15 |
| **A1** | createEntity extension — the B6 panel authors entities (not only concepts), so the prerequisite Entity is authored honestly through the real panel path; candidate-evidence citation + No Vocabulary Stretching. | **merged** — bc-core PR #71, bc-ai PR #16 |
| **T2-S4** | Live dev-gated smoke — candidate → bc-core B6-run → bc-ai panel → B4b → B4a → orchestrator → C5 → F3. | **proven** — live durable run (see the milestone below) |

The B6 build should continue to begin each slice with a design note / contract,
not code.

### T2-S4 milestone — first live durable B6 authoring

On 2026-05-22 the B6-S1 path was proven live and end to end, twice, producing
the **first durable governed content in the Business Concept Registry** — both
authored only through the real path `POST /api/bcf/registry-authoring-runs` →
bc-ai `registry-authoring` panel (real Maker / Checker / Moderator trio) →
B4b/B4a `panel_output_record` → `RegistryAuthoringOrchestrator.runS1` → C5
`issueRegistryShapeCertification` (Registry-shape deemed cert) → F3 write +
`target_registry_id` stamp. No seed exemption, no raw insert, no fabricated
panel record.

| Subject | Id | State |
|---|---|---|
| Entity `Sales Order Line` | `e974a6cd-8df9-4411-b3e6-ab26cd28fe71` | draft |
| Value concept `Unit Price` on `Sales Order Line` — characteristic `unit price`, representation term `amount` | `f66642ad-92b7-4026-a3f6-8179837bf5c3` | draft |

Both are `draft` — B6 authors drafts; B10 owns publication / activation. The
provenance chain is complete and verified on each: the `entity_version` /
`business_concept_version` row carries `certification_record_id` +
`panel_run_uid`; the Registry-shape `certification_record` carries
`gate_results_json.deemed_approval` and is stamped `target_registry_id` = the
authored id; the `panel_output_record` carries the real model roster, the agent
transcripts, and a `source_citations` entry deep-equal to the candidate's
`candidateEvidence`. All §11 blockers are resolved.

**Stabilization.** The bc-core `HttpRegistryAuthoringPanelClient`
`BC_AI_TIMEOUT_MS` default was raised 10 000 → 180 000 ms — a live panel run is
three sequential cross-family LLM calls and measured 42–67 s; the 10 s default
failed every real run.

**Next recommended design gate — F4-v2 vocabulary expansion.** The live path is
proven; the governing constraint on what it can author is now the breadth of the
F4 governed characteristic vocabulary (24 terms) and the F2 representation-term
set. Expanding the governed vocabulary is the recommended next gate — a design
gate in its own right (No Vocabulary Stretching means the panel emits
`OPERATOR_REVIEW` rather than stretch to a weak fit). It is not part of the
stabilization work.

## 11. Blockers

- **Durable registry `framework_policy` row (T2-S0)** — the main blocker; §9. A
  governed creation path must be designed and the row created before T2-S4. Not
  DDL, but authority-bearing data — no ad-hoc insert.
- **One new bc-core HTTP endpoint** — the B6-run entry point (L2). An
  operator/importer-facing platform endpoint under existing platform auth; the
  exact guard is confirmed at build. bc-ai also gets one new flow endpoint
  (`POST /api/ai/suggest/registry-authoring`), consistent with its 12 existing flows.
- **No new persistent table** — confirmed; the candidate is a request DTO; the
  Bucket-2 intake table stays deferred.
- **REJECT / OPERATOR_REVIEW verdict production** — the bc-ai pipeline produces
  only `APPROVE_FOR_DRAFT` today; the new flow must produce all three (L5; T2-S2).
- **B3 grounding is nominal** — the flow must declare `grounded_fields` for
  grounding to be effective (L4; T2-S2).
- **Candidate source/citation fields — absent in v1 (evidence class 5).** The
  T2-S1 candidate DTO (`candidateRef`, `targetEntityId`, `proposedName`,
  `definition`) carries no source/citation fields, so the candidate-meaning side
  of evidence class 5 rests on the operator-submitted `definition` alone and v1
  `source_citations` is `[]`. Adding candidate source/citation fields is a future
  packet/DTO enhancement, **not** T2-S2 — the panel must not invent citations to
  fill the gap. Surfaced here per L8.
- **`bc-ai/CLAUDE.md` is stale** — do not use it as an architecture reference.

## 12. References

- `business-context-framework-b6-design-survey.md` — D1–D6
- `business-context-framework-b6-slice-plan.md` — B6-S1, D7–D10
- `business-context-framework-build-plan.md` — §2 (B1–B6), §16
- `business-context-framework-requirements.md` — Ch.7 (Context Panels; framework policy as a governed authoring act)
- Foundation — `the-invariants.md` (Invariant VI)
- bc-core — `src/registry/registry-authoring-panel/` (B6-S1, merged), `src/registry/framework-approval/` (C5), `src/registry/concept-registry/` (F3, F5), `src/registry/dto/create-panel-output-record.dto.ts` (B4a contract)
- bc-ai — `app/pipeline/` (orchestrator, `panel_output_emitter`, `input_hash`, `grounding`), `app/agents/` (the trio), `app/models/registry.py` (roster), `app/clients/bc_core_auth.py`
- DEC-02f5a9 (D414) — Business Concept Registry
