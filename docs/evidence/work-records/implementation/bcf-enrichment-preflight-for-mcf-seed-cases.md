---
uid: bcf-enrichment-preflight-for-mcf-seed-cases
title: BCF Enrichment Preflight for MCF Seed Cases — packet-vs-workbench sufficiency, first enrichment slice
description: Preflight report ahead of opening BCF enrichment for MCF first-10-representative-metric authoring. Reads current BCF doctrine + shipped BCF v1 implementation (registry-authoring-context.builder.ts + orchestrator + bc-ai registry_authoring_panel.py + bc-admin business-concepts.ts) and evaluates whether the v1 bounded packet retrieval is sufficient for the enrichment scope MCF Step 4 needs, OR whether the BCF B6-v2 workbench retrofit (per alignment note `da8d9b7`) must open first. Verdict: v1 packet is sufficient for the first-10-metric BCF enrichment slice. Records explicit trigger conditions for B6-v2 retrofit so future operators can recognize the boundary without re-deriving. Recommended first enrichment slice scoped per addendum §2.4 (~30 BCs across ~3-5 Entity families, spanning date / currency / count / duration / negative-test classes). Not a build plan; no code changes; no MCF M3; no MCF M2 DDL apply.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: bcf-enrichment-preflight
---

# BCF Enrichment Preflight for MCF Seed Cases

## 1. Scope, method, and what this is not

### 1.1 Purpose

BCF requirements doctrine is governed workbench (`business-context-framework-requirements.md`, Chapter 7 after commit `1d7d209`). BCF v1 implementation uses a bounded authoring-context packet as retrieval vehicle (`bcf-mcf-panel-workbench-alignment-note.md`, commit `da8d9b7`). MCF M2 substrate has merged (bc-core `92a9056`, PR #101) but is not applied. MCF Step 4 (BCF enrichment for MCF seed cases) is the next operationally-blocking item for MCF first-10-representative-metric authoring.

Before opening enrichment, the open question is: **does the BCF v1 packet support the enrichment scope MCF needs, or must the B6-v2 workbench retrofit open first?**

This preflight answers that by:

1. Reading the shipped BCF v1 implementation (bc-core packet builder + orchestrator; bc-ai panel; bc-admin consumer).
2. Comparing the packet's exposed surfaces against MCF Step 4 requirements (build plan §6 + addendum §2.4).
3. Identifying gaps, if any, that would block first-slice enrichment.
4. Stating the verdict + the trigger conditions for B6-v2 retrofit + the recommended first enrichment slice.

### 1.2 Inputs read

| Class | Source | Role |
|---|---|---|
| BCF doctrine | `bc-docs-v3/docs/implementation/business-context-framework-requirements.md` (post `1d7d209`) | Governed-workbench framing; same-workbench rule; closed read-tool surface |
| BCF inventory + gap | `bc-docs-v3/docs/implementation/business-context-framework-inventory.md` + `*-gap-research.md` + `*-failure-evidence.md` | Architecture-as-built; known scars; helper-script discipline |
| Alignment note | `bc-docs-v3/docs/implementation/bcf-mcf-panel-workbench-alignment-note.md` (`da8d9b7`) | The reconciliation: v1 packet is retrieval vehicle, not governing architecture; B6-v2 trigger conditions |
| MCF build plan §6 / §7 | `bc-docs-v3/docs/implementation/metric-context-framework-build-plan.md` (`40a9adc`) | BCF enrichment interface; 10 representative metric classes |
| MCF addendum §2.4 | `bc-docs-v3/docs/implementation/metric-context-framework-candidate-reservoir-and-authority-classification.md` (`0e3644b`) | ~30 BCs / ~3-5 Entity families / required concept classes |
| BCF v1 packet builder | `bc-core/src/registry/registry-authoring-panel/registry-authoring-context.builder.ts` | Per-operation packet shape (createEntity / createBusinessConcept / createCharacteristic) |
| BCF v1 types | `.../registry-authoring-panel.types.ts` + `.../registry-authoring-run.types.ts` (referenced) | Validated recommendation + outcome union |
| BCF v1 run service | `.../registry-authoring-run.service.ts` | Live path entry point; resolves active framework_policy → builds packet → invokes bc-ai → orchestrator routes outcome |
| BCF v1 orchestrator | `.../registry-authoring-orchestrator.service.ts` | Panel → C5 cert → F3 dispatch; F4-v2 high-risk operator-confirm path |
| BCF v1 bc-ai panel | `bc-ai/app/pipeline/registry_authoring_panel.py` | Maker / Checker / Moderator over the packet; grounding mechanically enforced; closed defect-code list for REJECT |
| BCF v1 bc-admin consumer | `bc-admin/src/api/business-concepts.ts` | Read endpoints (entities / concepts / characteristics) + UI-S4b publication write hooks |

### 1.3 Discipline

- Read-only inspection. No code changes proposed unless this preflight surfaces a hard blocker (it does not).
- No MCF M3 opens.
- No MCF M2 DDL apply.
- Recommendations stop at "open enrichment with this slice"; the enrichment itself is a separate operator-authorized session.

---

## 2. Current shipped BCF architecture

### 2.1 What is built and live

**Substrate** (post-D418, intact per `da8d9b7` §2):
- `concept_registry.entity` + `entity_version` + `entity_supersession`
- `concept_registry.business_concept` + `business_concept_version` + `business_concept_supersession`
- `concept_registry.characteristic` + `characteristic_supersession`
- `concept_registry.representation_term`
- `concept_registry.alias`
- `concept_registry.supersession_proposal` (F3)
- Plus `contract.panel_output_record`, `contract.certification_record`, `contract.framework_policy`, `contract.operator_confirm_rule` (Foundation Governance Substrate per MCF §17.3)

**Services / modules** (bc-core, live):
- `RegistryReadService` (F5) — governed read surface for the Registry.
- `RegistryAuthoringService` (F3) — authoring writes (createEntity / createBusinessConcept / registerCharacteristic) under C5 certification authority.
- `RegistryAuthoringContextBuilder` — assembles the v1 bounded packet from F5 reads only.
- `RegistryAuthoringRunService` — live-path entry: resolves active `framework_policy`, builds packet, invokes bc-ai, returns orchestrator outcome.
- `RegistryAuthoringOrchestrator` — post-panel routing: `APPROVE → C5 issuance → F3 write`; non-APPROVE parked; F4-v2 high-risk path with operator-confirm + Fork-ii idempotent resume.
- `FrameworkApprovalService` (C5) — cert issuance gate + operator-confirm-required fork.
- `panel_output_record` repository — append-only authoring record per Foundation Invariant V.
- `rejection_log` repository — operator-actionable rejection surface (B6 D2: parked candidates write panel_output_record only; non-APPROVE has no rejection-log row).

**Services / modules** (bc-ai, live):
- `registry_authoring_panel.py` — three-agent (Maker / Checker / Moderator) panel entry point. NOT `run_pipeline` (no QA retry, no `evidence_store` write — that surface is for vocabulary-discovery flows, not Registry authoring). Honours bc-core contract: `request = discriminated context packet`, `response = {panelRunUid, verdictCode}`, exactly one `panel_output_record` emitted via B4b.
- Grounding mechanically enforced before APPROVE emission: (a) at least one `evidence.source_citations` entry must deep-equal the candidate's `candidateEvidence`; (b) `createEntity` requires zero `entityNameMatches`; (c) `createBusinessConcept` requires the proposed `characteristicId` / `representationTerm` / `entityId` to each be present in the packet.
- Malformed or ungrounded APPROVE → downgraded to `OPERATOR_REVIEW`.
- Closed v1 REJECT defect-code list (9 codes) enforced by `panel_output_record` CHECK.

**Surfaces** (bc-admin, live):
- Registry browse pages (entities / concepts / characteristics), backed by F5-S2 read endpoints.
- Provenance pages — UI-S2/S3.
- UI-S4b publication confirm flow — single-session request → review → confirm shape (Step A evidence bundle, Step B ≥40-char operator rationale, Step C semantic-finality affirmation where applicable). Mirrors the BCF requirements operator console pattern.

### 2.2 What is NOT built (per BCF requirements doctrine but not shipped)

- **Workbench tool-call interface** — bc-ai does not call read tools mid-panel-run; it reasons over the pre-assembled packet. The doctrinal "broad governed read awareness through closed tool surface" is approximated by "panel sees everything the builder pre-loaded".
- **Per-agent immutable transcript per the workbench framing** — the panel emits one `panel_output_record` per run carrying verdict + recommendation, but per-agent tool-call traces (as MCF requirements §11.3 envisions for MCF panel) are not the v1 audit shape.
- **Workbench fingerprint algorithm** — v1 uses `panel_output_record.policy_version` + input-hash as the consensus-validity surface; the multi-axis workbench fingerprint (tool allowlist version + evidence-source allowlist version + registry snapshot id + policy version + operator-context hash) is not implemented.

These are not bugs; they are the v1-vs-doctrine gap that the alignment note `da8d9b7` formally records. v1 ships with bounded discipline; B6-v2 (when it opens) closes the doctrinal gap.

### 2.3 Live operational characteristics

- **Per-panel-run sequence:** request lands on bc-core run service → policy resolved → packet built → bc-ai invoked synchronously → orchestrator routes outcome (authored / not_issued / parked / awaiting_operator_confirm).
- **Synchronous panel call:** no queue; one HTTP round trip per candidate.
- **F4-v2 high-risk pathway:** registerCharacteristic dispatches operator-confirm via C5; post-confirm executor lands the F3 write through the Fork-ii idempotent-resume pattern.
- **No bc-ai free-query of Registry:** L1-locked. Every Registry observation bc-ai uses is in the packet.

---

## 3. Packet contents and limits

The packet is operation-discriminated. Three operations, three packet shapes.

### 3.1 `createEntity` packet

Fields:
- `operation: 'createEntity'`
- `candidateRef` (operator-supplied identifier)
- `policyVersion` (active registry framework_policy version)
- `candidate` — `{ proposedName, definition, candidateEvidence: { sourceLabel, citedText } }`
- `entityNameMatches` — list of canonical + alias name matches against the proposed name (the duplicate-detection surface)

**What the panel sees:** the candidate + every existing entity-name match (canonical and alias) for the proposed name. Nothing else.

**Sufficiency for entity authoring:** the panel can refuse exact duplicates (`entityNameMatches` non-empty → APPROVE downgraded to OPERATOR_REVIEW; mechanically enforced). The panel can approve fresh names with grounded candidate evidence. The shape is appropriate for the operation.

**Limits:**
- No awareness of related entities (e.g. "Sales Order Line" could overlap with "Order Line Item" — the panel sees neither unless they appear in name matches).
- No source-reality context (the panel does not see which OCs / source systems already emit this concept).
- No platform-wide entity inventory beyond name matches (the full active entity list is not in the packet).

### 3.2 `createBusinessConcept` packet

Fields:
- `operation: 'createBusinessConcept'`
- `candidateRef`, `policyVersion`, `candidate` (as above)
- `selectedEntity` — the target entity resolved via `includeAllStates` (draft target allowed; B10 owns activation)
- `existingConceptsForEntity` — full list of concepts already on the target entity (duplicate-detection surface within the entity)
- `entityPlacementCandidates` — entity name matches for the selected entity's canonical name (placement-disambiguation surface)
- `activeCharacteristics` — full active governed-characteristic list (the panel's vocabulary surface)
- `representationTerms` — closed set of representation terms (the unit / data-type vocabulary)

**What the panel sees:** the candidate + the full target entity context (concepts already on it) + the full active governed vocabulary (characteristics + representation terms).

**Sufficiency for BC authoring:** rich. The panel can refuse duplicates within the target entity, validate that the BC's `characteristicId` / `representationTerm` resolve to known active vocabulary, and ground the BC's definition against the candidate's supplied source evidence.

**Limits:**
- **No cross-entity awareness.** A BC that could plausibly belong on Entity A or Entity B is operator-decided at candidate-submission time (operator chooses `targetEntityId`); panel does not disambiguate.
- **No source-reality awareness.** The panel does not see source contracts that already emit the field this BC represents. Grounding comes entirely from `candidateEvidence`.
- **No MCF-binding-readiness signal.** The packet doesn't know whether this BC will be MCF-bound, used as grain, used as time-anchor, etc. The panel's job is vocabulary authoring; MCF binding is a downstream concern.
- **Full active characteristic list is shipped per packet.** Today's BCF active characteristic count is small (F4-v2 era — single-digit characteristics confirmed per CLAUDE.md D418 Gate 5.3 baseline). At scale this becomes wasteful (KB-sized packets); not a v1 blocker.

### 3.3 `createCharacteristic` packet (F4-v2)

Fields:
- `operation: 'createCharacteristic'`
- `candidateRef`, `policyVersion`, `candidate`
- `activeCharacteristics` — full active list (the no-synonym admission surface)
- `representationTerms` — closed set

**What the panel sees:** the candidate + the full governed vocabulary.

**Sufficiency for characteristic authoring:** v1 vocabulary is small; full active list comparison is the right shape for no-synonym admission. F4-v2 added the Vocabulary Admission Checklist (M1-M10) the panel must answer; an APPROVE recommendation emits a structured answer per checklist item.

**Limits:**
- **Vocabulary scope classification is panel-judged.** F4-v2 admits `global` only at v1; `industry_specific` / `system_specific` / `alias_localization_candidate` / `reject` route to operator-review or refusal. The panel classifies based on the candidate evidence; it does not have cross-industry corpus to compare against.
- High-risk operation → C5 `operator_confirm_required` → F4-v2 S2b post-confirm executor lands the F3 write.

### 3.4 Cross-operation observations

| Property | Status |
|---|---|
| Bounded — single F5-derived assembly | ✓ |
| Builder is pure (no judgement, no vocabulary hardcoded) | ✓ |
| bc-ai cannot free-query the Registry | ✓ (L1 lock) |
| Grounding mechanically enforced before APPROVE | ✓ |
| Closed REJECT defect-code list | ✓ (9 codes, panel_output_record CHECK-enforced) |
| Per-operation discriminated packet shape | ✓ |
| Operator can choose target entity for BC (lifecycle-permissive) | ✓ (`includeAllStates` for `selectedEntity`) |
| Substrate write only via C5 + F3 (panel never writes) | ✓ |

---

## 4. Sufficiency verdict for near-term enrichment

### 4.1 What MCF Step 4 requires (per build plan §6 + addendum §2.4)

To support the 10 representative metric classes in MCF Gate M20:

| MCF mechanic | BCF concept density required |
|---|---|
| `variable_ref` (MCF §7.2) | ≥2 BCs per metric matching representation term + unit |
| Grain entity (MCF §4.3, §6.5) | ≥1 identity-bearing Entity per metric, reachable from bindings |
| Time-anchor variable (MCF §4.4 + §7.2 `time_anchor_resolution`) | ≥1 date-BC per scope |
| Filter input (MCF §4.5) | ≥1 BC per filter clause's referenced field |
| Computed-dimension reference (MCF §9.2) | ≥1 source date-BC for the resolver's input |

**Minimum aggregate:** ~30 BCs spanning ~3-5 Entity families; covering currency / count / duration / date / identifier representation classes; plus ≥1 negative-test case (unreachable BC for grain-reachability test).

### 4.2 Per-need sufficiency analysis

| MCF need | BCF v1 packet sufficiency | Notes |
|---|---|---|
| Adding ~3-5 Entity families | **Sufficient** | `createEntity` packet supports it. Operator-driven concept selection per addendum guardrail #2. |
| Adding ~30 BCs across those entities | **Sufficient** | `createBusinessConcept` packet supports it. Existing-concepts-for-entity check prevents duplicates; active-characteristics + representation-terms validation grounds the BC. |
| Adding new characteristics if needed (e.g. a duration characteristic the platform doesn't have yet) | **Sufficient** (F4-v2 path) | `createCharacteristic` with Vocabulary Admission Checklist. Routes to operator-confirm if high-risk. |
| Grounding BCs in standards (IFRS, GAAP, APQC) | **Sufficient with discipline** | `candidateEvidence.sourceLabel + citedText` carries the citation. Operator (or upstream importer) must supply real standards text. Panel mechanically checks the candidate evidence is cited. |
| Grounding BCs in source-system observations | **Sufficient with discipline** | Same mechanism: candidate evidence carries the source-reality citation. The packet does not auto-surface OC field maps, but the operator can include the relevant OC field reference in `citedText`. |
| Avoiding duplicates within target entity | **Sufficient** | `existingConceptsForEntity` in the packet. |
| Avoiding cross-entity name collisions | **Limited but sufficient for the first slice** | `entityPlacementCandidates` shows name-matches; full cross-entity reasoning is not in v1. For the first 10 metrics (operator-curated 3-5 entities), this is not a load-bearing gap. |
| Authoring BC with MCF-binding-readiness in mind | **Out of BCF scope** | BCF panel authors vocabulary; MCF authoring binds. The separation is correct per the framework boundary. |

### 4.3 Verdict

**BCF v1 packet retrieval is sufficient for the first-10-metric BCF enrichment slice.** No B6-v2 workbench retrofit is required to open MCF Step 4.

Reasoning:
- The 10 representative metrics target operator-selected concepts (per addendum guardrail #2: BCF enrichment is operator + BCF-panel decided, not seed-wording driven). Operator drives concept selection; panel governs the act of authoring each one.
- All three BCF authoring operations (createEntity / createBusinessConcept / createCharacteristic) are supported by v1 packet shape.
- Grounding mechanism (candidate evidence + mechanical panel check) is in place.
- Substrate is correct and the operator console (UI-S4b publication confirm) is shipped.
- The enrichment scope is small (~30 BCs); v1 packet stays well within its sufficiency envelope.

The doctrinal gap (broad governed read awareness vs bounded packet) remains, but it is not load-bearing for the first slice.

---

## 5. Explicit trigger conditions for B6-v2 workbench retrofit

The v1 packet is sufficient for the first-10-metric slice. It will become insufficient under the following conditions. Each is a B6-v2 retrofit trigger.

### 5.1 Hard triggers (B6-v2 must open before further enrichment proceeds)

| # | Trigger | Why it forces B6-v2 |
|---|---|---|
| T-H1 | Cross-entity disambiguation becomes load-bearing for a candidate (e.g. a BC could plausibly belong on Entity A or Entity B, and the choice is non-obvious) | v1 packet shows only the target entity; the panel cannot reason about alternatives. Workbench tool `registry.search_business_concept` lets the panel probe across entities. |
| T-H2 | Source-reality grounding becomes PE-MC-1-mandatory for a class of BCs (e.g. operator decides every quantity-BC must cite the OC that emits it) | Candidate evidence becomes operator-bottlenecked. Workbench tool `source_reality.summarize` lets the panel pull the OC context directly. |
| T-H3 | Active characteristic vocabulary grows beyond a wire-size threshold (~50 chars × full-active-list bundling becomes wasteful per packet, or stale-on-each-write becomes a defect) | The "full active list per packet" pattern doesn't scale. Workbench tool `registry.search_characteristic` lets the panel fetch on-demand. |
| T-H4 | bc-ai panel acquires a free-query tool to the Registry (the L1 lock is broken to handle a new requirement) | L1 lock breakage IS the retrofit. v1's "bc-ai never free-queries" invariant becomes the surface that B6-v2 formalizes through governed tool allowlists. |

### 5.2 Soft triggers (B6-v2 should be planned; enrichment may continue under v1 until decided)

| # | Trigger | Why it suggests B6-v2 |
|---|---|---|
| T-S1 | Per-agent transcripts become an audit requirement (e.g. operator wants to see Maker's tool-call trace separately from Checker's) | v1 emits one consensus `panel_output_record`; per-agent transcripts require the workbench-fingerprint + per-agent-transcript-uid pattern from MCF requirements §11.3. |
| T-S2 | Workbench fingerprint becomes a regulatory or operational requirement | v1's `policy_version + input_hash` is single-axis; the multi-axis workbench fingerprint (tool allowlist + evidence-source allowlist + registry snapshot + policy + operator-context) is the doctrinal form. |
| T-S3 | Operator surfaces start treating the packet as the unit of audit review | v1 already records the packet's effective content in the input hash, but the workbench framing makes the per-tool-call trail the audit unit, not the bundle. |
| T-S4 | MCF Gate M12 (Metric Authoring Panel) starts authoring its own MCF panel; BCF and MCF panel divergence becomes operationally inconvenient | MCF Gate M12 implements the tool-call workbench directly (per MCF M0 §14.9 / DEC-c3e57f Decision 6); a BCF B6-v2 retrofit at the same time would unify the architecture. |

### 5.3 Non-triggers

The following are NOT B6-v2 triggers:
- v1 packet size growing within reasonable bounds (the `createBusinessConcept` packet for a heavily-populated entity stays under ~100 KB at expected scale; not a constraint).
- BCF enrichment volume growing within operator capacity (each panel run is independent; v1 throughput is operator-bound, not architecture-bound).
- MCF M3-M20 implementation work (orthogonal to BCF retrieval architecture).

### 5.4 Practical guidance

If operator observes any T-H trigger during enrichment, **stop enrichment and open the B6-v2 retrofit gate** before the next concept is authored. The retrofit is a separate operator-authorized session; this preflight does not specify its design.

---

## 6. Recommended first enrichment slice for MCF seed cases

### 6.1 Slice scope (per addendum §2.4 + build plan §7)

**Goal:** ~30 BCs across ~3-5 Entity families to support the 10 representative metric classes.

### 6.2 Representation-class coverage requirement

The slice must include at least one BC per representation class needed for the 10 metric classes:

| Representation class | Why MCF needs it | Candidate Entity |
|---|---|---|
| Currency | Ratio metrics, amount aggregations, threshold metrics | Sales Order Line, Customer Invoice, Journal Entry |
| Count | Count metrics, cardinality denominators | Sales Order Line, Shipment, Customer |
| Duration | Lead-time / cycle-time metrics, windowed metrics | Sales Order Line, Workflow Item |
| Date / timestamp | Fiscal-period metrics, temporal anchors, computed-dimension resolvers | Sales Order Line, Customer Invoice, Journal Entry |
| Identifier (reference role) | Grain entities, dimension keys | Sales Order Line, Customer, Product |

### 6.3 Entity-family selection criteria

Operator-decided per addendum guardrail #2. Recommended starting set (operator may revise):

1. **Sales Order Line** — already confirmed active per CLAUDE.md / D418 Gate 5.3 baseline. Anchors ratio / amount / count / duration / date metric classes.
2. **Customer Invoice** — supports DSO-class, fiscal-period, payment-cycle metrics.
3. **Journal Entry** — supports fiscal-period grouping, account-level aggregations.
4. **(Optional) Customer** — supports customer-dimension grouping, CLV-class metrics.
5. **(Optional) Product** — supports product-dimension grouping.

3-5 Entity families is the target; start with 3 and add the 4th/5th if a representative metric class can't be expressed within the first 3.

### 6.4 Per-Entity BC count guidance

Distribute ~30 BCs across the selected entities. Typical pattern for Sales Order Line as the primary entity:

- ~8-10 BCs on Sales Order Line (currency: unit_price, line_amount, discount_amount; count: quantity, line_count; duration: order_to_ship_days, cycle_time; date: order_date, ship_date; identifier: order_line_id)
- ~5-7 BCs on Customer Invoice (currency: invoice_amount, paid_amount, outstanding_amount; date: invoice_date, due_date, paid_date; identifier: invoice_id)
- ~5-7 BCs on Journal Entry (currency: debit_amount, credit_amount; date: posting_date, document_date; identifier: journal_entry_id, account_code; count: line_count)
- ~3-5 BCs on each additional Entity if added

These are illustrative; operator + BCF panel decide actual BCs per business reality, not per this preflight's wording (per addendum guardrail #2 + MCF M1 ADR Decision 10 guardrail 2).

### 6.5 Negative test case

Per build plan §7 selection criteria, the slice must include at least one negative test case: a BC deliberately placed on an Entity unreachable from a representative metric's grain (to confirm MCF Gate M11 / M12 + PE-MC-2 grain-coherence + PE-MC-3 binding-completeness gates refuse). One BC of this kind is enough.

### 6.6 Failure-class coverage requirement

Per build plan §7, the 10 metrics include two deliberate failure cases:

- **Semantic-failure case** (MT-04971-class): two variables bound to BCs that resolve to identical substrate-identity signature; MLS-14 must refuse. The BCF slice needs at least one pair of BCs whose substrate signatures are intentionally identical (e.g. two BCs on different entities but both binding to source field WRBTR on BSID). This is the negative-test artifact for MLS-14.
- **Stale-fixture failure case**: covered by MCF fixture mechanics; no specific BCF BC needed beyond the normal slice.

### 6.7 Authoring sequence guidance

Recommended order (each is its own panel run):

1. **Phase A — Entities first.** Author the 3-5 Entity rows via `createEntity` packet. Each Entity authoring needs operator-supplied candidateEvidence citing a standard (APQC business architecture, IFRS taxonomy, or operator-bounded-domain definition).
2. **Phase B — Characteristics if needed.** If any required representation/characteristic doesn't exist in the active vocabulary, author it via `createCharacteristic` packet (F4-v2 path; operator-confirm-required if Vocabulary Admission Checklist classifies as anything other than `global`).
3. **Phase C — Business Concepts.** For each Entity, author its BCs via `createBusinessConcept` packet. Operator picks `targetEntityId`; the packet shows the entity's existing concepts so duplicates are caught.
4. **Phase D — Acceptance check.** Per build plan §6.2, the slice is accepted when (a) ≥10 candidate seed metrics from the high-confidence + APQC subset have been operator-selected, (b) every BC the selected metrics reference is in `active` state, (c) the BCF panel has reached consensus on every concept (no metric waits on draft/review BC), (d) ≥1 BC per representation class is in active state.

### 6.8 Out of preflight scope

- Specific seed-metric selection from the ~250-300 high-confidence + APQC subset (addendum §3.5). That selection is Step 4's first act, not this preflight's.
- Specific BC naming and definitions. Operator + BCF panel author per business reality.
- Cross-tenant BCF concept density. MCF first-slice is single-tenant scope.

---

## 7. Recommended next actions

### 7.1 Open Step 4 BCF enrichment with v1 packet retrieval

- Authorize BCF Registry read access on bc-postgres MCP allowlist (per gap survey §1.3 / addendum §8.4) so operator can inspect current active-Entity / active-BC / active-Characteristic density before the first authoring run.
- Author the 3-5 Entity rows (Phase A).
- Author any missing Characteristics (Phase B; F4-v2 path).
- Author the ~30 BCs (Phase C).
- Acceptance-check (Phase D).

### 7.2 Do NOT open MCF M3, MCF M2 apply, or B6-v2 retrofit

- **MCF M3** stays closed until M2 substrate is applied and Step 4 BCF enrichment lands.
- **MCF M2 DDL apply** stays closed until operator explicitly approves per CLAUDE.md Database Change Protocol (separate session).
- **BCF B6-v2 retrofit** stays closed until a §5.1 hard trigger surfaces.

### 7.3 Monitor for B6-v2 triggers during Step 4

Operator should watch for the §5.1 hard triggers during enrichment. Specifically:
- T-H1 (cross-entity disambiguation surfacing as a recurring decision)
- T-H2 (operator finding source-reality grounding bottlenecked at candidate-submission time)
- T-H3 (packet sizes growing past comfort threshold)
- T-H4 (any pressure to give bc-ai a free Registry query path)

If any of these surfaces during enrichment, stop and open B6-v2.

### 7.4 What this preflight does NOT recommend

- It does not recommend a code change.
- It does not propose a new BCF gate.
- It does not specify B6-v2 design (that is a separate session, post-trigger).

---

## Document verification

- **All required sections present:** §1 Scope/method, §2 Current shipped BCF architecture, §3 Packet contents and limits, §4 Sufficiency verdict, §5 B6-v2 trigger conditions, §6 Recommended first enrichment slice, §7 Recommended next actions.
- **Read-only inspection only.** No code changes proposed; no source files modified.
- **Verdict explicit:** BCF v1 packet is sufficient for the first-10-metric enrichment slice; B6-v2 retrofit not required before opening Step 4.
- **Trigger conditions enumerated:** 4 hard triggers + 4 soft triggers + non-triggers documented in §5.
- **No MCF M3.** No MCF M2 DDL apply. No B6-v2 open.
