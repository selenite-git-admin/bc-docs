---
uid: business-context-framework-inventory
title: Business Context Framework (BCF) — Implementation Inventory
description: Inventory pass against existing implementation in bc-core, bc-ai, bc-admin, DevHub, bc-seed, and the catalog data state. For each artifact in BCF scope (BF/BO, CF, BF↔CF mapping), classifies it as keep / adapt / wrap / deprecate / gap against the BCF requirements (business-context-framework-requirements.md). Reads-only. Companion to the requirements doc; informs the D6 BCF authority delegation ADR and the gap-pass build plan.
status: draft
date: 2026-05-18
project: bc-docs
domain: contracts
subdomain: catalog
focus: inventory
---

# Business Context Framework (BCF) — Implementation Inventory

## Method

Companion to `business-context-framework-requirements.md` (BCF requirements). For each existing artifact in BCF scope, this inventory classifies as one of:

| Verdict | Meaning |
|---|---|
| **keep** | Matches BCF requirements as-is; no rework needed. Reserved for artifacts that are BCF-compliant without modification. |
| **keep-as-substrate** | Useful read-only foundation (data layer, repository, reference proxy, visualization pattern) that BCF will consume but does not directly implement a BCF requirement. The artifact is preserved as-is for what it does today; BCF builds above it without changing it. |
| **adapt** | Core mechanism salvageable; needs rework to satisfy BCF discipline (vocabulary, authority model, authoring-record emission, three-model consensus, etc.). |
| **wrap** | Keep the underlying mechanism; add a BCF-compliant interface around it (adapter, contract, or facade) without changing the underlying behavior. |
| **deprecate** | Replace entirely; the artifact does not survive in any form under BCF. |
| **gap** | The artifact does not exist; needs to be built from scratch. |

Out of scope: SC, AC, OC, CC composition, CM beyond field-level, IC, all MC concerns (MC contextual attributes, formula, variable binding, chain integrity, runtime-readiness — these are MCF territory per BCF requirements §Scope), AI Contract (provisional), Extraction Contract (retired), all four evaluation boundaries, tenant-facing UI.

### Query basis

All catalog data counts in this inventory are point-in-time as of **2026-05-18** unless noted. Obtained via the `bc-postgres` MCP server connected to `bc_platform_dev` (PostgreSQL 17.8) over the schemas allowlisted for read-only query (`contract`, `master`, `metric`, `runtime`, `source`). Where archive filtering applies, it is noted explicitly on the row (e.g. `archived_at IS NULL`). Counts include only the `contract` schema unless stated otherwise. Queries are `SELECT`-only; no writes. Environment is the local dev DB used by the operator (not a tenant DB).

Source-code surveys in sections 2-6 are from the working tree at **bc-docs-v3@aee8fc1** (commit head at time of inventory drafting). File paths are absolute; classifications reflect the file state at that commit.

### Narrow update — 2026-05-18 (driven by gap-research §9)

Five BCF-direct changes were applied to this inventory in a deliberately narrow pass driven by `business-context-framework-inventory-gap-research.md` §9 and the Codex read-only verification pass §8 (2026-05-18, current bc-core). Changes:

1. **Added** `oagis-onboarding.service.ts` row in §2.1 (auto-cert call site, adapt / deprecate candidate) — G1.
2. **Sharpened** `cc-onboarding.service.ts` row in §2.4 from **wrap** to **wrap-with-gap** with two explicit gap items (G6b CF trust at mapping write; G7 Meaning-once write-time check).
3. **Added** `field-mapping.service.ts` and `canonical-wizard.service.ts` rows in §2.4 as **keep / adapt** (state filtering verified present in code) — G8.
4. **Added** §2.9 helper-scripts category as **default-untrusted** — G24.
5. **Marked bc-seed provisional** (`oagis-seed.service.ts` row in §2.7 and §6 framing) pending operational pull — G21.

Non-changes (explicit guardrails from gap-research §9.1):
- No CF-cert requirement was added to `business-object.service.ts::approveObject`. BO approval is BF-composition approval and is correctly BF-scoped; the live CF-cert gap is at CC mapping (G6b) and is fully captured by change #2 above.
- G13 (chain_status pre-activation race, already fixed at `contract.service.ts:578`) and G15 (`MetricWizardService` quarantine confirmed at controller and service layers) are NOT promoted to live BCF gaps.
- No MCF or runtime-driver inventory changes were applied.

Tone preserved: verdicts, implications, open questions. No architecture proposed.

### Combined narrow update — 2026-05-19 (driven by E1 + E2 evidence)

Documentation merge from two evidence sessions completed under ADR-149ab2 (decided): `business-context-framework-bc-seed-operational-state.md` (E1 / SES-d88ba5) and `business-context-framework-helper-script-trust-catalog.md` (E2 / SES-2cfa45). Four narrow updates:

1. **§2.7 `oagis-seed.service.ts` row** — "provisional" qualifier removed per E1 §6 verdict. Wrapper (E3) scope refined by E1 sub-findings S1/S5/S6 (shared-component lookup path, stale-detection signal, noun-vs-slug lookup-key shape).
2. **§2.9 helper-scripts category** — coarse `default-untrusted` verdict refined to per-script-banded outcome per E2: trusted (38) / diagnostic (67) / unsafe (55) / deprecated (0) across 160 source scripts. **13 active defect surfaces** named as CI's second defect-tag source besides gap-research G-findings. **High-severity substrate note (E2 S1):** zero `.github/workflows/` directories exist in any of the five surveyed repos — the §13 enforcement gate requires a new CI substrate, not only check configuration. The CI harness session is therefore creating CI from scratch, materially widening its scope.
3. **§6 bc-seed framing** — "provisional" qualifier removed; framing updated to reflect E1 operational verification.
4. **This header note** — recording the 2026-05-19 combined update.

Non-changes (explicit guardrails):
- No new evidence beyond what E1 + E2 produced. No re-derivation in this session.
- No edits to §1, §2.1, §2.2, §2.3, §2.4, §2.5, §2.6, §2.8, §3, §4, §5, §7, §8, §9, §10, §11.
- No code changes; no script remediation (the 42 unsafe-but-not-invoked cleanup candidates from E2 §3 remain operator-decision-scope, not BCF execution).
- E2 sub-findings S0 (file-count drift 156→160) and S3 (side-effect false-positive risk for self-classifying audit scripts) preserved as audit-discipline notes inside §2.9; not promoted to inventory-level findings.

Tone preserved. No architecture proposed. Verdicts only.

---

## 1. Catalog data state

### 1.1 Counts

| Item | Count | Notes |
|---|---:|---|
| BFs active (`archived_at IS NULL`) | 6,682 | Includes all catalog states except archived. |
| BFs archived | 388 | `archived_at IS NOT NULL`. |
| BFs cleanly in (`status_code='certified', catalog_state_code='certified_catalog'`) | **1,651** | The only pair that maps cleanly to BCF `active`. |
| BFs cleanly in (`status_code='draft', catalog_state_code='candidate_import'`) | **262** | The only pair that maps cleanly to BCF pre-catalog intake → `draft`. |
| BFs in impossible state combinations | **4,769** | See §1.2. ~71% of active catalog. |
| BFs with definition_standard | 6,433 | 96% — definition_standard is well-populated. |
| BFs with standard_ref | 1,405 | 21% — most BFs lack the citation. |
| BFs with semantic_family | 1,412 | 21% — same. |
| BFs with unit_type_code | **21** | **0.3%** — almost no BFs carry unit anchoring. |
| BFs with at least one alias | 1,956 | 29% — most BFs lack source-system grounding. |
| BFs with BO membership | 5,966 | 89% — most BFs are placed in a BO. |
| BFs orphaned from any BO | 716 | Violates BCF chapter 2 relation rule "A BF MUST belong to exactly one BO". |
| BFs mapped to ≥1 CF (via cc_field_mapping) | **322** | **5%** — only 322 of 6,682 BFs participate in a CF mapping. |
| BFs unmapped to any CF | 6,360 | 95% — the BF↔CF mapping layer is largely unbuilt. |
| Aliases | 1,962 | Roughly one alias per aliased BF. |
| Certification records (BF) | 3,493 | See §1.3. |
| BOs total | 203 |  |
| BOs with zero fields | 9 | Violates minimum-composition. |
| BOs with < 4 fields | 13 | Violates BCF chapter 12 default minimum-composition. |
| BO membership records | 6,352 | One per BF↔BO relation. |
| CFs total | 3,097 | Out of which 1,486 referenced by ≥1 CC. |
| CFs orphan (no CC reference) | **1,611** | 52% — BCF chapter 15 flags these as audit signals. |
| cc_field_mapping rows | 1,616 | BF↔CF mapping instances. |

### 1.2 State-pair distribution (BF)

| status_code | catalog_state_code | count | BCF interpretation |
|---|---|---:|---|
| certified | candidate_import | **4,745** | **Impossible.** Foundation lifecycle has no such pair. Likely produced by past partial migrations or by setting `status_code='certified'` on bulk imports without running the candidate → certified transition. |
| certified | certified_catalog | 1,651 | Cleanly maps to BCF `active`. |
| certified | correction_required | 11 | **Impossible.** Same class of defect. |
| draft | candidate_import | 262 | Cleanly maps to BCF pre-catalog intake → `draft`. |
| draft | certified_catalog | 12 | **Impossible.** A draft cannot already be in certified catalog. |
| draft | correction_required | 1 | Foundation does not have correction_required as a first-class state, but in BCF chapter 4 it's a workflow holding pen. This one row is consistent. |

**Conclusion:** ~71% of the active BF population is in a state pair that cannot be expressed under Foundation Contract Grammar §Lifecycle. The legacy disposition deferral (D1) is sharper than expected: the majority of current BFs cannot move forward under BCF without a state reconciliation step.

### 1.3 Action-code distribution (certification_record, primitive_type='business_field')

| action_code | count | BCF interpretation |
|---|---:|---|
| admit_bf_catalog | 1,651 | **Vocabulary defect** — "admit" is Foundation runtime vocabulary. Should be "publish" or "activate" in catalog scope. |
| remediate_bf_semantics | 1,396 | D408 family. Corresponds to BCF Curation function (now woven into Authoring/Publication panels). |
| demote_bf_catalog | 388 | **Vocabulary defect** — Foundation lifecycle has no "demote"; only "supersede" and "withdraw". |
| mark_bf_correction_required | 30 | Foundation does not have correction_required; BCF treats it as workflow holding pen. |
| admit_bf_from_candidate_import | 8 | **Vocabulary defect** — D409 family. |
| certify | 8 | **Vocabulary defect** — should be "activate" or "publish". |
| submit_for_review | 8 | Reasonable. Matches BCF `draft → review` transition. |
| recertify_bf_catalog | 4 | **Vocabulary defect** — Foundation has no "recertify"; new versions supersede. |

### 1.4 Action-code distribution (certification_record, primitive_type='canonical_field')

| action_code | count |
|---|---:|
| certify | 1 |
| remediate_description | 1 |
| submit_for_review | 1 |

CF certification machinery exists but is essentially unused (3 lifetime records).

### 1.5 Implications for legacy disposition (D1)

The disposition question reframed:

- The 5,007 candidate_import BFs are not the only problem; 4,745 of them are also marked status=`certified` (impossible state).
- Forward-progress requires either (a) state reconciliation (decide each of the 4,769 impossible-state BFs: were they meant to be active, or were they supposed to stay in candidate?), (b) a full reset of the catalog (treat all 4,769 as needing re-publication under BCF), or (c) freeze and parallel — leave the legacy in place with a quarantine flag and have BCF operate only on new content.
- The 21 BFs with unit_type_code, 1,405 with standard_ref, and 1,412 with semantic_family represent the **only BFs that satisfy BCF PE4/PE5 today**. Even among the 1,651 cleanly-active BFs, very few satisfy the BCF publication-eligibility contract.

This is the most consequential inventory finding. D6 or a prerequisite sibling decision must address legacy disposition; the disposition choice directly affects what the framework's first-shipped scope looks like.

---

## 2. bc-core registry services

Scope: services in `bc-core/src/registry/` touching BF, BO, CF, BF↔CF mapping, plus support services (chain status, certification record machinery, seed integration).

### 2.1 BF services

| Artifact | Verdict | Notes |
|---|---|---|
| `standard-field.service.ts` | **adapt** | Core CRUD + lifecycle service for BF (called "StandardField" — vocabulary defect: BCF uses "Business Field"). Public methods: `createField`, `getField`, `listFields`, `updateField`, `deleteField`, `certifyField`, `bulkCreateFields`, `bulkCertifyFields`, `listAliases`, `upsertAlias`, `deleteAlias`, `bulkCreateAliases`, `getAliasStats`, `remediateBfSemantics`, `suggestStandardRef`, `correctBfDefinition`, `correctBfType`, `admitBfFromCorrectionRequired`, `admitBfFromCandidateImport`. Lifecycle state transitions use Foundation-runtime "admit" vocabulary and "certify"/"recertify" non-Foundation states. Authority model is operator-only (no AI panel integration). Authoring records partially emitted via `certification_record` table (already in place) but the table's action_code vocabulary needs cleanup (D3). **Adapt path:** rename to `business-field.service.ts`; rename methods to BCF vocabulary (`activateField`, `proposeField`, etc.); add Framework Approval wrapping; integrate with Context Authoring/Publication Panels. **Caveat (G1):** `bulkCertifyFields` is the underlying mechanism used by the OAGIS auto-cert call site documented as a separate row below (`oagis-onboarding.service.ts`). The adapt scope on `standard-field.service.ts` covers vocabulary + Framework Approval wrapping; disposition of the auto-cert *call site* is handled on its own row, not by widening this row's scope. |
| `standard-field.controller.ts` | **adapt** | Same vocabulary defects; HTTP endpoint surface. Endpoint names like `/admit-from-candidate-import` and `/admit-from-correction-required` need rename to BCF vocabulary (`/publish-from-draft`, `/publish-from-correction-required`). |
| `standard-field.repository.ts` | **keep** with vocabulary cleanup | Repository layer; mostly Foundation-neutral. SQL column references to `catalog_state_code` will need to follow the lifecycle unification if D6 chooses to consolidate `status_code` + `catalog_state_code` into a single `governance.state` column per BCF chapter 4. |
| `bf-correction.helper.ts` | **adapt** | D408 pure validators. Encode admission-gate predicates (G1 definition rules, G3 type-pair coherence, G6 family-unit compatibility). The validators themselves are sound and align with BCF PE1-PE6. Vocabulary defect: file name and references say "correction" which BCF replaces with `correction_required` workflow holding pen. Validators become deterministic publication-gate checks in BCF chapter 7. |
| `bf-catalog-state.guard.ts` | **adapt** | D408 / DEC-1ce490 guard. Refuses cc_field_mapping insert/replace unless BF is in `catalog_state_code='certified_catalog'`. The guard rule is correct in spirit (only active BFs can be referenced in mappings), but it hardcodes the Foundation-defective state name `certified_catalog` and is one of the load-bearing places where lifecycle vocabulary cleanup must happen consistently. |
| `bf-sda-trust.spec.ts` | **keep** | Test file for SDA trust rules; tests are valuable regression coverage. |
| `admit-from-candidate-import.service.spec.ts` | **adapt** | Test file; tests the admission flow. Will need rename and method updates per the parent service adapt. |
| `admit-from-correction-required.service.spec.ts` | **adapt** | Same. |
| `oagis-onboarding.service.ts` | **adapt / deprecate candidate (the auto-cert call site)** | OAGIS BF importer. Verified in gap-research §8.1 (2026-05-18): line 283 calls `bulkCreateFields()`; line 300 immediately calls `bulkCertifyFields(..., true)`. This call-site chain converts import into certification in a single step, even where field descriptions are empty or templated (D408 audit attributed 462 placeholder-defined `certified` rows in part to this path). **Caveat (G1):** the existing adapt verdict on `standard-field.service.ts` does not cover the auto-cert call site; that call site is the live mechanism for the cert-as-flag-mutation problem and is a separate disposition from the per-field `certifyField` method. Adapt path: break the auto-cert chain so import lands rows in a pre-publication state requiring evidenced gating; deprecate the `bulkCertifyFields(..., true)` invocation entirely from this caller. Independent of the broader `standard-field.service.ts` vocabulary adapt. |

### 2.2 BO services

| Artifact | Verdict | Notes |
|---|---|---|
| `business-object.service.ts` | **adapt** | Core BO service. Public methods: `create`, `getById`, `list`, `update`, `delete`, `getFields`, `addField`, `addFields`, `updateField`, `removeField`, `replaceFields`, `getStats`, `getRelations`, `addRelation`, `removeRelation`, `getAuditLog`, `applySuggestions`, `bulkCreate`, `approveObject`. Has `approveObject` method — this is the existing approval path for BO. **Vocabulary alignment needed:** `approveObject` becomes a BCF Framework Approval call in the AI-by-default model; operator-driven approval remains as the override path. The minimum-composition rule (chapter 12) needs to be re-encoded; current DB shows 13 BOs with <4 fields and 9 with zero fields, so the rule is either unenforced or the threshold differs. |
| `business-object.controller.ts` | **adapt** | HTTP surface; same. |
| `business-object.repository.ts` | **keep** | Repository; mostly Foundation-neutral. |
| `business-object.module.ts` | **keep** | NestJS module declaration. |
| `bo-enrichment.repository.ts` | **adapt** | BO enrichment storage. Likely wired to `applySuggestions` in `business-object.service.ts`. Under BCF, BO enrichment becomes a Context Curation function (woven into Authoring/Publication per chapter 7). |
| `bo-verification.service.ts` | **adapt** | D201 orchestrator: loads BO + field composition, runs 3-step Gemini search+verify agent (see §3 bc-ai), persists to `bo_verification_log`. **Critical: this is already a Foundation-Conversation-surface activity that runs and persists results.** Under BCF, this becomes the Context Publication Panel's BO branch — needs to (a) move to three-model consensus (Maker/Checker/Gate present, but uses single Gemini provider, not cross-family), (b) emit immutable panel records with input hash + prompt version + per-agent identity, (c) enroll outputs in calibration sampling. The verification log is the proto-form of the BCF authoring record but lacks several BCF NF1 fields. |
| `bo-verification.repository.ts` | **adapt** | `bo_verification_log` table storage. Adapt to BCF NF1 authoring-record shape. |
| `bo-verification.prompts.ts` | **adapt** | Prompt templates for BO verification. Will need prompt versioning per BCF chapter 7 immutable panel records requirement (`prompt version` is one of the required fields on every panel output). |
| `bo-verification-agent.ts` | **adapt** | D201 agent implementing the 3-step pattern (search → fetch → verify). Cross-family planned but uses Gemini-only currently. |

### 2.3 CF services

| Artifact | Verdict | Notes |
|---|---|---|
| `canonical-field.service.ts` | **adapt** | Core CF service. Public methods: `createField`, `getById`, `findByName`, `listFields`, `batchCreate`, `listMappingsByCC`, `proposeCertification`, `certifyCanonicalField`, `remediateDescription`. CF lifecycle machinery exists but is essentially unused (3 lifetime certification_record entries). Vocabulary defects: "certify"/"certification" instead of BCF "publish"/"Framework Approval". `proposeCertification` is the closest existing surface to a BCF panel-driven submission. **Reference-time enforcement note (G6a/G6b, verified in gap-research §8.3, 2026-05-18):** MC activation (`contract.service.ts:70/128-154`) does enforce CF `status_code='certified'` AND `semantic_family IS NOT NULL` — this enforcement boundary is closed. CC mapping writes (`cc-onboarding.service.ts:770`) do NOT enforce CF certification — see the `cc-onboarding.service.ts` row in §2.4 for the wrap-with-gap disposition. The CF service row itself does not change scope. |
| `canonical-field.controller.ts` | **adapt** | HTTP surface. |
| `canonical-field.repository.ts` | **keep** | Repository. |
| `canonical-field.service.spec.ts` | **keep** | Test file. |

### 2.4 BF↔CF mapping services

| Artifact | Verdict | Notes |
|---|---|---|
| `cc-onboarding.service.ts` | **wrap-with-gap (two gap items)** | CC creation service (auto-derives field_selection from BO field composition). **CC composition itself is out of BCF scope** per requirements §Scope; however, the `addFieldSelection`, `addMappings`, and `replaceMapping` methods touch BF↔CF mapping which IS in BCF scope (chapter 14). Wrap path unchanged: BCF's Context Publication Panel calls these methods to author mappings on draft CM versions; the underlying CC composition decisions remain operator-only. **Gap item 1 (G6b, verified in gap-research §8.3, 2026-05-18, line 770):** CC mapping writes look up CF by name and use `cf.dataType` but do **not** require `cf.statusCode === 'certified'` or `semanticFamily IS NOT NULL` before insert/replace. Reference-time CF trust is enforced at MC activation (`contract.service.ts:70/128-154`) but not here. The wrap must add the CF trust check at the mapping-write boundary. **Gap item 2 (G7, verified at line 754):** existing validation covers shape, BF selection, and BF certification, but there is no write-time Meaning-once / semantic-signature check before mapping insert (Foundation Invariant I, BCF chapter 15). The wrap must add the Meaning-once check. Quality gate CR-QG-CC-001 (11 checks) is referenced separately; alignment with BCF PE1-PE6 + chapter 15 cross-scope coherence still to inventory. |
| `cc-onboarding.controller.ts` | **wrap** | HTTP surface. |
| `cc-onboarding.add-field-selection.service.spec.ts` | **keep** | Test file. |
| `field-mapping.service.ts` (`FieldMappingService.suggest()`) | **keep / adapt** | BF↔CF mapping suggestion service consumed by bc-admin authoring surfaces. Verified in gap-research §8.2 (2026-05-18): lines 115 and 122 filter BFs to `catalog_state_code='certified_catalog'`. State filtering is present today — this row is **added to the inventory** to record the artifact (previously uninventoried) but the verdict is **keep / adapt**, not "state-blind contamination vector" as earlier FEM phrasing implied. Adapt path under BCF: vocabulary alignment with BCF lifecycle state names (`certified_catalog` → BCF `active` per D3 cleanup), surfacing of bc-seed lineage on returned candidates, integration with Framework Approval indicators on the consuming UI. Open question: do current callers in bc-admin compose any client-side filter that loosens the server-side state check? |
| `canonical-wizard.service.ts` (`CanonicalWizardService`) | **keep / adapt** | Wizard service for canonical-field / canonical-contract authoring. Verified in gap-research §8.2: lines 287, 309, 485 filter to certified BFs in both write and UI paths. Same disposition as `FieldMappingService.suggest()` — **added to the inventory** to record the artifact, **keep / adapt** verdict. Adapt path under BCF: same set of items as `FieldMappingService` (vocabulary, bc-seed lineage surfacing, Framework Approval integration). |

### 2.5 Chain / integrity services (mostly out of BCF scope; MCF territory)

| Artifact | Verdict | Notes |
|---|---|---|
| `chain-status.service.ts` (D305) | **out of BCF scope; MCF** | Chain: MC variable → CF → BF → CC schema → OC field_mapping → AC → Reader → Source. The chain touches BCF members (CF, BF) but the chain is downstream of the BCF/MCF split. BCF Lifecycle Audit Panel (chapter 7 stage 3) may read chain status to detect reference impact at supersession; chain authoring is MCF. |
| `integrity.service.ts` | **deprecate** (already marked) | Legacy chain integrity service; deprecated per D305. Kept for two callers (per file docstring): `contract.service.ts` activation gates and `MetricContractDetailPage` per-MC detail view. Both callers are out of BCF scope (MC). Migration to `chain-status.service.ts` is an existing track. |
| `canonical-chain.service.ts` | **out of BCF scope; MCF** | Resolves metric formula fields to Business Objects via D225 BO clustering. Touches BF and BO (BCF members) read-only; called from KPI creation paths. BCF Lifecycle Audit Panel may consume read; no BCF authoring through this path. |
| `mc-integrity.service.ts` / `.controller.ts` / `.repository.ts` | **out of BCF scope; MCF** | MC-specific integrity service. |
| `catalog-verification.service.ts` (D108) | **adapt → MCF or BCF Lifecycle Audit** | AI-assisted catalog verification via Anthropic API; single-flow not three-model. Verifies entity attributes from `SourceCatalogService`; persists to `catalog_verification_log`. Provider singleton (Claude) violates BCF cross-family discipline. Output is verdict + audit trail. Closest BCF fit: Lifecycle Audit Panel periodic checks. Needs migration to three-model + immutable record format. |
| `catalog-verification.controller.ts` | **adapt** | HTTP surface. |
| `catalog-verification.repository.ts` | **adapt** | `catalog_verification_log` table. |
| `catalog-verification.prompts.ts` | **adapt** | Prompt templates; need versioning. |
| `catalog-verification-agent.ts` | **adapt** | 3-step agent (Gemini search → fetch → Claude verify). Cross-provider (Gemini + Claude) but only 2 providers in the path, not 3-role Maker/Checker/Gate. Needs structural alignment with BCF three-model consensus. |

### 2.6 Browse / catalog services

| Artifact | Verdict | Notes |
|---|---|---|
| `business-catalog.service.ts` | **keep** | Read-only catalog browsing service backing `BusinessCatalogPage`. Reads do not trigger evaluation per Foundation §The Evaluation Boundaries; this service is correctly framed as read-only. |
| `business-catalog.controller.ts` | **keep** | HTTP surface. |
| `business-catalog.module.ts` | **keep** | Module. |
| `seed-context-readiness.service.ts` | **wrap** | Read-only diagnostic. Answers "for a draft seed, what context exists, what semantic checks passed/failed/unevaluable, what must be authored or fixed before promotion." Three layers: contextAvailability (inventory), semanticReadiness (authority via CompatibilityFilterService), promotion readiness. The underlying checks are valuable and reusable; the artifact is a **draft-seed promotion-readiness diagnostic**, NOT a BCF deterministic publication gate with Framework Approval policy, operator-confirm rules, panel-output IDs, sampling enrollment, and immutable authoring records. Wrap path: keep the diagnostic; build a BCF publication-gate adapter that consumes the diagnostic's findings AND adds the BCF-required surfaces (policy version, panel output linkage, sampling, immutable record emission). |
| `seed-context-readiness.controller.ts` | **wrap** | HTTP surface for the diagnostic; BCF publication-gate endpoint is a separate adapter that may call this internally. |
| `seed-context-readiness.service.spec.ts` | **keep-as-substrate** | Test file; regression coverage for the underlying diagnostic. |
| `enrichment-processor.ts` | **adapt** | Background worker polling pending metric enrichment jobs and calling bc-ai for KPI decomposition. Out of BCF scope (MC enrichment is MCF); pattern reusable for BCF (e.g. a background worker that polls for queued Context Authoring Panel jobs). |

### 2.7 Seed integration services (bc-seed Mongo proxy)

| Artifact | Verdict | Notes |
|---|---|---|
| `oagis-seed.service.ts` | **keep-as-substrate + wrap** | Read-only Mongo proxy for `bc_seed.seed_oagis_components`. Exposes OAGIS Nouns/Components/Fields for standard-reference proposals. Also exposes a parallel handle on `bc_seed.seed_bo_crosswalk` (TSK-9515d5) for BO provenance lookup. The Mongo proxy itself is keep-as-substrate (data layer is sound), but as a load-bearing BCF dependency it needs a wrapper that adds: (a) lineage metadata (which OAGIS noun/component/field a returned candidate maps to, surfaced on every proposal), (b) coverage tracking (which OAGIS Nouns BCF has consumed vs which are unreferenced), (c) currency/fetchability validation per PE3 (referenced source is valid and admissible — bc-seed lineage means AI didn't invent the reference; the wrapper verifies the reference is still real), (d) version metadata (OAGIS version the seed entry was imported from). Without the wrapper, the read-only proxy alone does not satisfy BCF's no-fabrication promise — it satisfies the "AI didn't invent" half but not the "publication gate verifies" half. **E1 verdict (G21, 2026-05-19, `business-context-framework-bc-seed-operational-state.md`):** E1 downgrades G21 from provisional to usable substrate: bc-seed is reachable, current for OAGIS 10.12, and covers all active OAGIS component slugs referenced by BFs. This does not close the BCF lineage-surfacing requirement: E3 must still wrap candidate returns so each AI-visible candidate carries explicit noun/component/field lineage. E1 evidence is bound to the 2026-04 bc-seed schema shape and should not be reused without re-verifying noun/component/slug structure. E3 wrapper scope is narrowed by E1 sub-findings S1 (shared-component lookup path: 25 of 158 docs have `doc_type='shared_component'` with no `noun` field), S5 (no documented refresh cadence — stale-detection signal becomes Lifecycle Audit Panel input), and S6 (noun-root vs component-slug lookup-key shape: noun root is addressed by `noun` field, components by `slug` inside nested arrays; wrapper must traverse correctly). |
| `seed-catalog.service.ts` | **keep-as-substrate** | Read-only Mongo proxy for `bc_seed.seed_tables` (D269; source-system schemas). Out of BCF direct scope (source layer); its read pattern is the model for `oagis-seed.service.ts`. |
| `seed-metrics.service.ts` | **out of BCF scope; MCF** | Read-only Mongo proxy for `bc_seed.seed_metrics`. Curated metric reference. |
| `seed-catalog.controller.ts` | **keep-as-substrate** | HTTP surface for seed_tables. |
| `oagis-d292.ts` | **keep-as-substrate** | Standalone OAGIS reference data. |

### 2.8 Certification record machinery (BCF authoring-record foundation)

| Artifact | Verdict | Notes |
|---|---|---|
| `contract.certification_record` table (DB) | **adapt** | The existing certification_record table is the closest existing artifact to BCF NF1 authoring records. Columns include `certification_record_id`, `primitive_type`, `primitive_id`, `action_code`, `from_state_code`, `to_state_code`, `is_archived_after`, `gate_results_json`, `advisory_verdicts_json`, `override_gate_code`, `override_rationale_text`, `override_followup_task_uid`, `certifier_sub`, `certifier_role_at_action`, `certifier_email`, `supersedes_primitive_id`, `created_at`. Missing fields for BCF NF1: panel run UID, prompt version, model identity per agent, input hash, sampling status, policy version. Adapt path: extend the table (or add a sibling table) with the BCF authoring-record fields; harmonize `action_code` vocabulary (D3); migrate existing rows to BCF-correct action codes during the legacy disposition (D1). |

### 2.9 Helper scripts category (`bc-core/scripts/`)

| Artifact | Verdict | Notes |
|---|---|---|
| `bc-core/scripts/*` (category) | **per-script-banded with defect-surface verdict** (per E2) | E2 catalog (`business-context-framework-helper-script-trust-catalog.md`, SES-2cfa45, 2026-05-19) audited **160 source scripts** under `bc-core/scripts/` (134 .mjs + 22 .js + 2 .ts + 1 .py + 1 .sh; `.sql` migration bodies excluded). Bands: **trusted (38) / diagnostic (67) / unsafe (55) / deprecated (0)**. Hardcoding rate: 113 of 160 (70.6%) — consistent with Codex §8.1 prior baseline (138/156). Per-script columns recorded in the E2 catalog: path / band / hardcoded tenant / hardcoded schema / hardcoded env / last-modified / author / side-effects / invocation status / call-sites / defect-surface verdict. **Banding rule:** trusted = no hardcoding + read-only; diagnostic = hardcoded + read-only; unsafe = `writes + hardcoding OR stale schema (boundary./canonical_object)`; deprecated = `>6 months old AND not-invoked`. **Defect-surface rule (operative for CI):** `band ∈ {unsafe, deprecated} AND invocation ∈ {invoked-by-ci, invoked-by-package-json, invoked-by-runbook, invoked-by-other-script}` = defect surface. **13 active defect surfaces** as of 2026-05-19: `d369-m1c-sandbox1-probe.mjs`, `d408-backfill-bf-catalog-state-1q-a.mjs`, `d408-demote-bf-catalog-state-1q-b.mjs`, `d408-demote-correction-required-no-cc-1q-d.mjs`, `d408-remove-a1-mismatch-cc-mappings-1q-e.mjs`, **`evaluate-ready-mcs.mjs`** (Codex canonical example), `golden-snapshot.mjs`, `mc-diagnose.mjs`, `mc-verify.mjs`, `oc-sc-pairing-review.mjs`, `seed-fi-readers-week2.mjs`, `seed-reader-bindings.mjs`, `smoke-e2e-pipeline.mjs`. These are CI's **second defect-tag source** besides gap-research G-findings, per build-plan §13.5 / §13.7. Cleanup-candidate count: 42 unsafe-but-not-invoked scripts (not active defect surfaces today; not BCF-execution scope). **High-severity substrate note (E2 sub-finding S1):** **zero `.github/workflows/` directories exist in any of the five surveyed repos (bc-core, bc-admin, bc-ai, bc-portal, bc-docs-v3).** The §13 enforcement gate cannot be wired into existing CI because **CI does not exist as a substrate**. The next session (CI substrate + harness plan) is therefore creating CI from scratch, not configuring it — this materially widens the CI session scope from "add §13 checks" to "build CI substrate, then add §13 checks." Audit-discipline notes preserved: S0 file-count drift 156→160 in one day (re-derive count rather than carrying forward); S3 side-effect false-positive risk for self-classifying audit scripts (audit script that defines pattern literals will grep-match its own literals; manual triage required when band doesn't match expected behaviour). Future re-audit cadence: operator decision; recommend re-run before any major substrate PR lands. |

### Summary table (bc-core registry)

| Verdict | Count of artifacts |
|---|---:|
| keep | 14 |
| adapt | 17 (+1: `canonical-wizard.service.ts`) |
| keep / adapt | 1 (`field-mapping.service.ts`) |
| adapt / deprecate-call-site | 1 (`oagis-onboarding.service.ts`) |
| wrap | 2 (was 3; `cc-onboarding.service.ts` reclassified) |
| wrap-with-gap | 1 (`cc-onboarding.service.ts`) |
| deprecate | 1 |
| per-script-banded (category) | 1 (`bc-core/scripts/*` — per E2 catalog: 160 scripts banded as trusted 38 / diagnostic 67 / unsafe 55 / deprecated 0; 13 active defect surfaces) |
| out-of-scope (MCF) | 6 |

---

## 3. bc-ai agents

Scope: agents in `bc-ai/app/agents/` touching BCF members (BF, BO, CF, BF↔CF mapping).

The bc-ai agent architecture **already implements the three-role pattern** (Maker / Checker / Gate) with cross-family model assignment for some flows. Vocabulary differs from BCF requirements: bc-ai says "Gate"; BCF says "Moderator". Functionally equivalent. The BCF requirements doc should harmonize to "Gate" OR bc-ai vocabulary should harmonize to "Moderator" — D3 vocabulary cleanup applies here too.

The `BaseAgent` class provides the substrate for all three roles. Flows are identified by `flow_id`; each role is a separate class. This structure is **directly reusable for BCF Context Panels** with naming alignment.

### 3.1 Agents in BCF scope

**Column key.** "Role separation" = are the three roles implemented as distinct agents with distinct prompts (Yes/No). "Provider diversity" = are the three roles served by models from genuinely different provider families (e.g. Anthropic + Google + OpenAI), which is what BCF's "cross-family" target means in spirit. Cross-model within the same family (e.g. Nova Pro + Nova Lite) is role separation, not provider diversity.

| Flow | Role separation | Provider diversity | BCF panel mapping | Verdict |
|---|---|---|---|---|
| `bf_dedup` (CR-QG-001 Gate 8) | Yes (Maker / Checker / Gate) | **No** (Nova Pro / Nova Pro / Nova Lite — all AWS Nova family; cross-model within one provider only) | Context Authoring Panel — duplicate detection (chapter 12) | **adapt** — needs vocabulary harmonization (Gate → Moderator OR vice versa), provider-diversity upgrade to satisfy BCF cross-family target, and integration with BCF immutable-record schema. |
| `bf_pii_classify` (CR-QG-001 Gate 7) | Yes | **No** (Nova family only) | Context Authoring Panel — PII classification | **adapt** — same. |
| `bo_composer` ("BOSuggest") | Yes | **No** (Nova family only) | Context Authoring Panel — BO composition coherence + minimum composition gap detection (chapter 12) | **adapt**. |
| `bo_dedup` (CR-QG-002 Gate 4) | Yes | **No** (Nova family only) | Context Authoring Panel — BO duplicate detection; Context Lifecycle Audit Panel — duplicate accretion detection | **adapt** — one agent serves two BCF panel stages. |
| `cc_field_audit` | Yes | **Partial — cross-family** (Gemini 2.5 Flash Maker + Anthropic Haiku Checker + Gemini 2.5 Flash Lite Gate; two providers across three roles) | Context Publication Panel — BF↔CF mapping coherence (chapter 14 + chapter 15 cross-scope coherence). Output recommendations: `map_to_bf`, `leave_unmapped`, `needs_new_bf`, `formula_definitional_error`. | **adapt** — strongest existing fit. Provider-diversity partial (two of three roles share Gemini); meeting BCF's full three-provider target would substitute the Gate role with a third provider (e.g. OpenAI). Closed-enum verdicts already exist; anti-pattern protection in the prompt aligns with BCF no-fabrication rule. |
| `field_mapper` | Yes | **No** (Nova family only) | Context Publication Panel — BF↔CF mapping proposal | **adapt**. |

### 3.2 Agents out of BCF scope

| Flow | Reason out of scope | Note |
|---|---|---|
| `chain_auditor` | MC chain integrity is MCF territory | Reuse pattern for BCF Lifecycle Audit Panel where applicable. |
| `metric_tracer` | MCF | — |
| `metric_verifier` | MCF | — |
| `eval_advisor` | Likely MCF or operations | Check on MCF inventory pass. |
| `source_verifier` | Source-system layer, not catalog | — |
| `table_verifier` | Source-table layer, not catalog | — |

### 3.3 Infrastructure

| Artifact | Verdict | Notes |
|---|---|---|
| `base.py` (BaseAgent, AgentRole enum, Routing, AgentResult, PipelineResult) | **keep** | Solid foundation. AgentRole enum has MAKER, CHECKER, GATE — would extend if BCF naming chooses Moderator instead. |
| `parsers.py` | **keep** | JSON output parsing. |
| Prompt templates (per flow) | **adapt** | Need versioning per BCF NF1 (prompt version on every panel output). Prompt loader exists (`app.prompts.loader.load_prompt`). |

### 3.4 Gaps in bc-ai relative to BCF requirements

| Requirement | Gap |
|---|---|
| Three-model consensus with **same input snapshot** (BCF chapter 7) | bc-ai flows run Maker → Checker → Gate sequentially; verifying that all three saw the same input snapshot is an explicit BCF requirement. Need an input-hash mechanism. |
| Immutable panel output records with BCF NF1 fields (panel run UID, prompt version, model identity per agent, input hash, per-agent transcripts, verdict, grounding check result, policy version) | bc-ai agents emit `AgentResult` and `PipelineResult` but likely do not persist immutable records with all these fields. Need a panel-output-records table. |
| No-fabrication grounding check | Specific to each agent's prompt; not a shared invariant. BCF requires it as a system invariant with quarantine for failures. |
| Calibration sampling enrollment | Not present. BCF NF7 makes this load-bearing. |
| REJECT eligible defect-code closed list (chapter 7 + Deferral D4) | Each agent has its own verdict enums; no central closed list. Need design + operator review. |
| Cross-family provider diversity target | Only `cc_field_audit` is genuinely cross-family (Gemini + Anthropic). Other agents are Nova-family-only (provider-monoculture risk for the high-stakes Publication and Lifecycle Audit panels). |
| Operator-confirm rule engine | Not present in bc-ai (operator-confirm policy is a BCF-side mechanism). |

### Summary table (bc-ai agents)

| Verdict | Count |
|---|---:|
| keep (infrastructure) | 2 |
| adapt (in BCF scope) | 6 |
| out-of-scope (MCF or source) | 6 |
| gap items | 7 |

---

## 4. bc-admin UI surfaces

Scope: pages in `bc-admin/src/pages/` touching BCF members.

### 4.1 Existing BCF-relevant pages

| Page | BCF surface mapping (chapter 6) | Verdict |
|---|---|---|
| `BusinessFieldDetailPage.tsx` | Per-Member Detail View for scope 1 BF | **adapt** — extend with: panel transcript viewer, version history, override action surface, calibration sampling marker, BCF Framework Approval indicators. Existing sections (metadata, description, BO usage list, aliases, certification status) survive. |
| `BusinessObjectsPage.tsx` | Catalog Browser (scope 1 BO list) | **keep** with vocabulary cleanup. |
| `BusinessObjectDetailPage.tsx` | Per-Member Detail View for scope 1 BO | **adapt** — same kind as BF Detail. |
| `CreateBusinessObjectPage.tsx` | Authoring Tool (scope 1 BO) | **adapt** — fits BCF Authoring Tool requirement; needs to produce intake-queue entry that AI then takes over per default. |
| `BusinessCatalogPage.tsx` | Catalog Browser (cross-scope) | **keep** — flat-table-with-filters; URL-synced filter state (per file docstring "URL-synced filters (function, subfunction, businessObjectType, search)"). Direct fit for BCF chapter 6 Catalog Browser. |
| `StandardFieldsPage.tsx` | Catalog Browser (scope 2 CF list) — note the name conflict: "StandardField" is old vocabulary for what BCF calls Canonical Field | **adapt** — rename to `CanonicalFieldsPage` or similar; same UI shape works. |
| `MappingsPage.tsx` | Catalog Browser (scope 3 BF↔CF mapping list) | **adapt**. |
| `MappingBindingsPage.tsx` | Per-Member Detail View for scope 3 | **adapt**. |
| `FieldResolutionPage.tsx` | Mapping impact view (chapter 14 per-scope UI) | **keep** — pattern reusable. |
| `SeedCatalogPage.tsx` | Reference: bc-seed content browser | **keep** — supports operator visibility into bc-seed candidates. |
| `SeedBrowserPage.tsx` | Reference: bc-seed browser | **keep**. |
| `TicketsPage.tsx` + `TicketDetailPage.tsx` | Operator Queue (chapter 6) | **adapt** — needs to consolidate across all three BCF stages; currently scope unclear from name alone. |
| `ActivityLogPage.tsx` | Activity Log (chapter 6, chapter 10 NF1) | **adapt** — extend to filterable by primitive type, panel verdict, action type, policy version, reversal status (BCF chapter 6 Pilot Auto-Action Controls requirements applied to general activity log). |
| `BatchProgressPage.tsx` | Progress UI for bulk operations | **keep**. |
| `IntegrityReportPage.tsx` | Pattern for Calibration Dashboard | **wrap** — reusable visualization patterns (D169/D170 chain validation); not a direct fit for BCF Calibration Dashboard but the dashboard scaffolding is reusable. |
| `MetricFunnelDashboardPage.tsx` | Pattern for Calibration Dashboard | **wrap** — D283 trust chain visualization, maturity funnel, gate pass rates, 5D distribution charts. Out of BCF scope (MCF metric funnel) but the visualization patterns inform BCF Calibration Dashboard. |
| `RejectionSummaryPage.tsx` | NOT the BCF Authoring Panel Rejection Log | **keep** as-is — scoped to runtime admission rejections per D169/D170 reading `execution.rejection_summary`. BCF Authoring Panel Rejection Log is a different surface for catalog intake rejections (gap; see §4.2). |
| `TestBenchPage.tsx` | Pattern for pre-publication testing | **wrap** — pattern reusable for BCF dry-run-style preview before AI executes a transition. |
| Onboard wizards (`OnboardSourceSystemPage.tsx`, `OnboardWizardPage.tsx`, `AutoOnboardPage.tsx`, `CanonicalReaderWizardPage.tsx`, `CreateMetricWizardPage.tsx`, etc.) | Multi-step authoring patterns | **out of BCF scope** (source-system and metric concerns), but pattern reusable. |
| `MetricCatalogPage.tsx`, `MetricContractDetailPage.tsx`, `MetricContractsPage.tsx`, `MetricDefinitionDetailPage.tsx`, `MetricFunnelDashboardPage.tsx`, etc. | MCF territory | **out of BCF scope**. |
| `CanonicalContractsPage.tsx`, `CreateCanonicalContractPage.tsx`, `ContractDetailPage.tsx` | CC composition (out of BCF scope) | **out of BCF scope** — keep referenced read-only from BCF Reference Impact Viewer. |
| Source / admission / observation pages (`SourceContractsPage`, `AdmissionContractsPage`, `ObservationContractsPage`, etc.) | Out of BCF scope | **out of BCF scope**. |

### 4.2 BCF UI surfaces with no existing implementation (gaps)

| BCF surface (chapter 6) | Gap rationale |
|---|---|
| **Panel Transcript Viewer** | No existing UI to read past AI panel outputs (Maker/Checker/Gate transcripts side-by-side). No place today displays the 3-agent output trail. |
| **Calibration Dashboard** | No existing UI for per-stage panel precision over time, classifier-vs-panel-vs-endpoint-vs-operator-override delta tracking, AI-approval-vs-operator-override rate. MetricFunnelDashboardPage is the closest pattern. |
| **Authoring Panel Rejection Log** | RejectionSummaryPage exists but for runtime admission rejections. Authoring Panel rejections (intake → rejection-log path per BCF chapter 4) are a distinct concept with no surface today. |
| **Reference Impact Viewer** | When operator considers superseding a BF/BO/CF/mapping, which downstream artifacts (CCs, MCs, ICs, active Contract Bindings) reference it? No existing UI. Chain-status data exists in DB; visualization gap. |
| **Policy Management surface** | BCF policy configuration (per-scope sampling rates, operator-confirm rules, calibration regression thresholds). No existing UI; BCF requirements expect operator to be able to configure policies and pause/resume. |
| **Activity Dashboard** | Stream of AI activity across all three scopes, filterable. ActivityLogPage is the closest pattern but needs significant extension. |
| **Operator Notifications** | Real-time / digest / threshold-based notification UX. Likely some Tickets infrastructure exists; needs survey. |
| **Operator-confirm UI** | When operator-confirm rules apply, the framework MUST surface pending confirms. No existing UI. |

### Summary table (bc-admin UI)

| Verdict | Count |
|---|---:|
| keep | 6 |
| adapt | 10 |
| wrap | 3 |
| out-of-scope | many |
| gap | 8 surfaces |

---

## 5. DevHub records mapping to BCF discipline

BCF NF1 requires immutable authoring records, ISO 27001 change records auto-wired, reconstructability of any catalog state. DevHub already implements much of this discipline.

| DevHub primitive | Maps to BCF | Verdict |
|---|---|---|
| `devhub_decision_record` (DEC-xxxxxx, ADR files in bc-docs-v3) | BCF chapter 7 framework policy changes are ADR-style change records. The Deferral D6 (BCF authority delegation ADR) uses this primitive. | **keep** — direct fit. |
| `devhub_change_record_save` (plan_json + report_json) | BCF NF1 authoring records for session-scope changes; ISO 27001 change records auto-wire | **keep** — direct fit. |
| `devhub_task_add` | Operator Queue tickets (Lifecycle Audit Panel outputs tickets per chapter 7 stage 3) | **keep** — fit; need to harmonize ticket fields with BCF's per-stage filtering. |
| `devhub_session_open / save_plan / checkpoint / close` | Operator session discipline; not directly BCF but supports the operator workflow | **keep**. |
| `devhub_activity_log` | Activity Log (BCF chapter 6) | **adapt** — DevHub activity log is session-event-flavored; BCF Activity Log needs to surface AI-action events with policy version, panel output IDs, etc. May be a separate stream that joins DevHub session activity. |
| ADR file storage (`bc-docs-v3/docs/adrs/`) | BCF ADR-governed authoring path (chapter 5 + chapter 7 policy changes) | **keep** — direct fit. |

### Summary table (DevHub)

| Verdict | Count |
|---|---:|
| keep | 5 |
| adapt | 1 |

DevHub is the most BCF-ready of all the surveyed surfaces.

---

## 6. bc-seed (MongoDB)

| Collection | Purpose | BCF role |
|---|---|---|
| `bc_seed.seed_tables` | D269 source-system table reference (source-system schemas) | Read by `seed-catalog.service.ts`; supports `SeedCatalogPage`. Out of direct BCF scope (source layer) but bc-seed-as-candidate-source pattern. |
| `bc_seed.seed_oagis_components` | OAGIS Nouns / Components / Fields | Read by `oagis-seed.service.ts`; **direct fit for BCF PE1(c) bc-seed lineage as valid provenance** for BF/CF candidates. The collection structure (noun → components → fields, each with bf_name, semantic_role, cardinality, data_type, description, representation_term) is exactly what BCF Context Authoring Panel needs to propose standard_ref + semantic_family + representation_term for new BFs/CFs. |
| `bc_seed.seed_bo_crosswalk` | TSK-9515d5 BO provenance lookup | Read by `oagis-seed.service.ts` parallel handle; supports BCF BO authoring chapter 12. |
| `bc_seed.seed_metrics` | Curated metric reference | MCF territory. |

bc-seed is **central to BCF's no-fabrication discipline**. The framework's promise that "AI's standard_ref proposals trace to bc-seed lineage; never fabricated" depends on this MongoDB store being current, broad, and accessible.

**E1 operational verdict (G21, 2026-05-19, `business-context-framework-bc-seed-operational-state.md`):** E1 downgrades G21 from provisional to usable substrate: bc-seed is reachable, current for OAGIS 10.12, and covers all active OAGIS component slugs referenced by BFs. This does not close the BCF lineage-surfacing requirement: E3 must still wrap candidate returns so each AI-visible candidate carries explicit noun/component/field lineage. E1 evidence is bound to the 2026-04 bc-seed schema shape and should not be reused without re-verifying noun/component/slug structure.

**Open questions on bc-seed — narrowed by E1:**
- Update cadence — no documented refresh cadence (E1 sub-finding S5; carried to E3 wrapper scope as stale-detection signal).
- Coverage gaps — none for current active OAGIS BF demand: 195 of 195 referenced slugs resolve at component level (E1 §2.3). 120 surfaces remain unreferenced — capacity for the 2,043 active OAGIS BFs missing `standard_ref` (E1 §2.4).
- Read latency at intake-time — empty-on-unavailable contract holds at runtime (E1 §4); intake-time read path is sound. Pre-fetch vs inline-fetch is an E3 design concern.
- Versioning — single version (OAGIS 10.12) across all 158 docs (E1 §3); no multi-version drift. Refresh cadence open per S5.
- Shared-component lookup path (E1 sub-finding S1): 25 of 158 docs have `doc_type='shared_component'` with no `noun` field; current service lookup at `oagis-seed.service.ts:152` uses `{noun: input.noun}` and misses shared components. Carried to E3 wrapper scope.

| Verdict | Count |
|---|---:|
| keep-as-substrate + wrap (3 collections in BCF scope) | 3 |
| out-of-scope (1 collection MCF) | 1 |

---

## 7. Foundation-vocabulary defects across the codebase

BCF requirements §Vocabulary discipline + D3 Deferral identify several vocabulary defects in the existing implementation. This section enumerates concrete locations.

### 7.1 "admit" / "admission" vocabulary used for catalog work

| Location | Defect |
|---|---|
| `bc-core/src/registry/standard-field.service.ts` (1,500+ lines) | Methods `admitBfFromCorrectionRequired`, `admitBfFromCandidateImport`; types `AdmitFromCorrectionRequiredDto`, `AdmitFromCandidateImportDto`, `AdmitFromCorrectionRequiredResult`, `AdmitFromCandidateImportResult`, `AdmitFromCorrectionRequiredEvidence`, `AdmitFromCandidateImportEvidence`. |
| `bc-core/src/registry/standard-field.controller.ts` | Endpoints `POST /api/business-fields/:id/admit-from-correction-required`, `POST /api/business-fields/:id/admit-from-candidate-import`. |
| `bc-core/src/registry/admit-from-candidate-import.service.spec.ts` + `admit-from-correction-required.service.spec.ts` | File names. |
| `contract.certification_record` table | Action codes `admit_bf_catalog` (1,651 rows), `admit_bf_from_candidate_import` (8 rows), `admit_bf_from_correction_required` (0 rows). |
| D408 and D409 ADR titles | Use "admit" framing throughout. |

### 7.2 "certify" / "certified" vocabulary used as Foundation lifecycle state

| Location | Defect |
|---|---|
| `contract.business_field.catalog_state_code` | Value `certified_catalog` should be `active` per Foundation. |
| `contract.certification_record.action_code` | Values `certify`, `recertify_bf_catalog` should be `activate`, plus version supersession instead of recertify. |
| `bc-core/src/registry/standard-field.service.ts` | Methods `certifyField`, `bulkCertifyFields`. |
| `bc-core/src/registry/canonical-field.service.ts` | Methods `proposeCertification`, `certifyCanonicalField`. |
| `bc-core/src/registry/bf-catalog-state.guard.ts` | Guard rule references `certified_catalog` as the only valid state for binding. |
| `bc-admin/src/pages/BusinessFieldDetailPage.tsx` | Page docstring "certification status" — UI vocabulary. |

### 7.3 "approve" on AI/system actions (N26 negative requirement)

| Location | Defect |
|---|---|
| `bc-core/src/registry/business-object.service.ts` | Method `approveObject` is operator-driven today; under BCF this becomes Framework Approval when AI-driven (in BCF scope) or operator approval when out-of-BCF-scope. The method name itself doesn't violate N26 if it's clearly operator-driven, but extending it to AI execution would. |
| Various `*Approval` types in bc-core | Survey needed; may need vocabulary harmonization. |

### 7.4 Non-Foundation lifecycle states

| Location | Defect |
|---|---|
| `contract.business_field.catalog_state_code` | Values `candidate_import`, `certified_catalog`, `correction_required`, `demoted_catalog` are not Foundation lifecycle states. Foundation has `draft → review → approved → active → superseded`. |
| `contract.business_field.status_code` | Two columns encoding lifecycle (Foundation rule: single column). The 4,769 impossible-state-combination rows are the consequence. |

### 7.5 D3 vocabulary cleanup scope summary

The D3 cleanup is substantial:
- ~6 methods to rename in `standard-field.service.ts`
- ~2 endpoints to rename in `standard-field.controller.ts`
- ~2 file renames in registry
- 8 action_code values to remap in `certification_record` (across 3,493 rows)
- 1 lifecycle-state-column consolidation (or 2 columns to keep but with strict invariant enforcement)
- DB column value migration: `certified_catalog` → `active`, `candidate_import` → `draft` (or split between `draft` and `review` based on context), etc.
- Cascading UI label changes in bc-admin

This is the kind of work that should happen in lockstep with D1 (legacy disposition) and D6 (BCF authority ADR). Vocabulary cleanup without lifecycle reconciliation would just move the problem.

---

## 8. Summary tables

### 8.1 Keep (matches BCF requirements as-is)

| Artifact | Category | Why it qualifies |
|---|---|---|
| `business-catalog.service.ts` + controller + module | bc-core | Read-only catalog browsing; Foundation-neutral. |
| `business-object.repository.ts` | bc-core | Foundation-neutral repository. |
| `standard-field.repository.ts` | bc-core | Foundation-neutral repository (modulo column rename). |
| `canonical-field.repository.ts` | bc-core | Same. |
| `seed-context-readiness.service.ts` + controller + spec | bc-core | Direct fit for BCF Publication Panel deterministic gate. |
| `oagis-seed.service.ts` | bc-core | bc-seed PE1(c) provenance source. |
| `seed-catalog.service.ts` + controller | bc-core | Source-system reference; bc-seed pattern. |
| `bf-sda-trust.spec.ts` | bc-core | Regression test. |
| `oagis-d292.ts` | bc-core | Standalone reference data. |
| `base.py` (BaseAgent infrastructure) | bc-ai | Solid foundation; Maker/Checker/Gate roles in place. |
| `parsers.py` | bc-ai | JSON parsing. |
| `BusinessObjectsPage.tsx` (modulo vocabulary) | bc-admin | Catalog Browser pattern. |
| `BusinessCatalogPage.tsx` | bc-admin | Catalog Browser direct fit. |
| `FieldResolutionPage.tsx` | bc-admin | Mapping impact pattern. |
| `SeedCatalogPage.tsx` + `SeedBrowserPage.tsx` | bc-admin | Reference UIs. |
| `BatchProgressPage.tsx` | bc-admin | Progress UI pattern. |
| `RejectionSummaryPage.tsx` | bc-admin | Runtime admission rejections; not BCF but kept distinct. |
| All DevHub primitives (decision_record, change_record_save, task_add, session_*, ADR file storage) | DevHub | Direct fits or near-direct. |
| All bc-seed collections in BCF scope | bc-seed | Central to PE1(c). |

### 8.2 Adapt (core mechanism salvageable; rework needed)

| Artifact | What needs to change |
|---|---|
| `standard-field.service.ts` + controller + spec | Vocabulary (admit → publish; certify → activate; standard-field → business-field); method signatures; Framework Approval integration; AI panel callbacks. |
| `business-object.service.ts` + controller | Vocabulary; minimum-composition rule re-enforcement; Framework Approval integration. |
| `canonical-field.service.ts` + controller + spec | Vocabulary; activate the dormant lifecycle (3 records → real flow); Framework Approval integration. |
| `bo-enrichment.repository.ts` | Wire to BCF Context Curation function (woven into Authoring/Publication). |
| `bo-verification.service.ts` + repository + prompts + agent | Cross-family upgrade (currently Gemini-only); BCF NF1 record format; calibration sampling; prompt versioning. |
| `catalog-verification.service.ts` + controller + repository + prompts + agent | Same; this is a single-Anthropic-call flow that needs to become three-role consensus; logs need BCF NF1 fields. |
| `bf-correction.helper.ts` | Vocabulary (correction → correction_required holding pen); validators become BCF deterministic publication-gate checks. |
| `bf-catalog-state.guard.ts` | State value (certified_catalog → active); guard rule stays. |
| `cc-onboarding.service.ts` `addFieldSelection` / `addMappings` / `replaceMapping` paths | Wrap with BCF chapter 14 mapping authoring on draft CM versions. |
| `enrichment-processor.ts` (pattern) | Reuse pattern for BCF Context Authoring Panel background worker. |
| `contract.certification_record` table | Add BCF NF1 fields (panel run UID, prompt version, model identity, input hash, sampling status, policy version); harmonize action_code vocabulary; migrate existing 3,493 rows. |
| All 6 bc-ai agents in BCF scope (bf_dedup, bf_pii_classify, bo_composer, bo_dedup, cc_field_audit, field_mapper) | Vocabulary harmonization (Gate vs Moderator); cross-family upgrades where currently single-family; input-hash mechanism; immutable record persistence; calibration sampling; grounding check as system invariant. |
| bc-ai prompt templates | Versioning. |
| `BusinessFieldDetailPage.tsx`, `BusinessObjectDetailPage.tsx`, `CreateBusinessObjectPage.tsx` | Panel transcript viewer, version history, override action surfaces, calibration markers, Framework Approval indicators. |
| `StandardFieldsPage.tsx` | Rename to `CanonicalFieldsPage`; same UI shape. |
| `MappingsPage.tsx` + `MappingBindingsPage.tsx` | BCF scope 3 specifics. |
| `TicketsPage.tsx` + `TicketDetailPage.tsx` | Consolidate across all three BCF stages. |
| `ActivityLogPage.tsx` | Filter extensions per BCF chapter 6. |
| DevHub `activity_log` | Extension for AI-action events. |

### 8.3 Wrap (keep underlying mechanism; add BCF interface)

| Artifact | Wrap rationale |
|---|---|
| `cc-onboarding.service.ts` (CC creation parts) | CC composition stays out of BCF scope; mapping-related methods wrapped by BCF chapter 14. |
| `IntegrityReportPage.tsx` | Dashboard scaffolding patterns reusable for BCF Calibration Dashboard. |
| `MetricFunnelDashboardPage.tsx` | Same — visualization patterns. |
| `TestBenchPage.tsx` | Pre-publication preview pattern. |

### 8.4 Deprecate (replace entirely)

| Artifact | Deprecation rationale |
|---|---|
| `integrity.service.ts` | Already marked `@deprecated` per D305. Replaced by `chain-status.service.ts` for MCF; BCF doesn't use either directly. |

### 8.5 Gap (build from scratch)

| Surface / artifact | Where it belongs | Why it's a gap |
|---|---|---|
| BCF Authoring Panel Rejection Log table + UI | bc-core DB + bc-admin | Distinct from runtime admission rejection summary; no existing surface. |
| BCF Panel Transcript Viewer UI | bc-admin | No surface today reads Maker/Checker/Gate output trail side-by-side. |
| BCF Calibration Dashboard | bc-admin + bc-core data layer | Per-stage precision tracking; AI-vs-operator-override delta; quarantine population trend. |
| BCF Reference Impact Viewer | bc-admin | When superseding a member, show downstream impact. Data exists in chain-status; visualization gap. |
| BCF Policy Management UI | bc-admin | Configure per-scope sampling rates, operator-confirm rules, regression thresholds; pause/resume policies. |
| BCF Operator-confirm UI | bc-admin | Surface pending operator-confirm-required actions; capture rationale. |
| BCF Activity Dashboard | bc-admin | Stream of AI activity; primary operator surface. ActivityLogPage close but not equivalent. |
| BCF Operator Notifications UX | bc-admin / integration | Real-time / digest / threshold-based. |
| BCF panel-output-records storage (immutable, replicated) | bc-core DB | The table that holds panel run UID + prompt version + model identity + input hash + per-agent transcripts + verdict + grounding check result + policy version + sampling status. Some shape exists in `bo_verification_log` and `catalog_verification_log` but neither has the full BCF NF1 shape. |
| BCF framework policy table + versioning | bc-core DB | Per-scope policy with declaration template (chapter 7 §Pilot policy declaration template); versioned; ADR-governed change records on each modification. |
| BCF calibration table | bc-core DB | Per-row per-stage: AI verdict, sample status, operator decision, eventual downstream signal. Drives Calibration Dashboard. |
| Provider-diverse Maker/Checker/Gate for high-stakes panels | bc-ai | Currently only `cc_field_audit` is cross-family. Publication Panel and Lifecycle Audit Panel are high-stakes per chapter 7 and target Gemini+OpenAI+Claude. The OpenAI piece is missing from current bc-ai infrastructure. |
| Input-hash mechanism on consensus | bc-ai | Same-input-snapshot rule (BCF chapter 7) requires cryptographic hash comparison; not present. |
| No-fabrication grounding check as system invariant | bc-ai | Currently per-agent prompt concern; needs to be a shared invariant with quarantine. |
| REJECT-eligible defect-code closed list | bc-ai + bc-core | Deferred D4. |
| Operator-confirm rule engine | bc-core | Evaluates rules at panel-execution time; routes matching cases to operator-confirm queue. |
| State reconciliation tooling for 4,769 impossible-state BFs | bc-core | One-shot migration tool; depends on D1 disposition choice. |
| Vocabulary cleanup migration (D3) | DB + bc-core + bc-admin | Coordinated rename across action_codes, state values, method names, endpoint paths, UI labels. |

---

## 9. Inventory-derived hypotheses for the D6 BCF authority delegation ADR (NOT decisions)

> **Discipline note.** This section contains hypotheses derived from the inventory observations above. They are NOT decisions, NOT recommendations the inventory locks in, and NOT scope commitments for D6. They are starting points the gap-pass document and the D6 ADR may consume, modify, or reject. The inventory's authoritative output is the artifact-level classifications in sections 1-8 (data state + per-artifact verdicts). Anything in section 9 that reads like a build-plan or scope recommendation should be treated as inventory-derived hypothesis pending decision elsewhere.

The inventory surfaces several issues that D6 or a prerequisite sibling decision may need to address:

### 9.1 Hypothesis: disposition choice must precede framework activation

The 4,769 impossible-state BFs and 1,611 orphan CFs mean BCF cannot simply "start operating" against the existing catalog. D6 or a prerequisite sibling decision may need to choose one of:

- **(A) Freeze + parallel.** Mark the legacy as quarantined; BCF operates only on new content authored via the framework. Lower migration cost; legacy stays defective; downstream chain quality stays at current level until each legacy artifact is replaced.
- **(B) Reconcile + migrate.** Run a one-shot state reconciliation tool: classify each impossible-state row as (i) was-meant-to-be-active → set both columns to active-equivalent, (ii) was-meant-to-stay-draft → roll back. Then BCF operates against the reconciled catalog. Higher upfront cost; cleaner long-term state.
- **(C) Restart from clean active set.** Take the 1,651 cleanly active BFs as the base; supersede everything else; rebuild from there using BCF discipline. Loses the encoded knowledge in 4,769 rows; cleanest cut.

Each choice has implications for the D3 vocabulary cleanup scope, for the first-shipped BCF scope (which scopes can go live on day 1), and for the operator workload model.

### 9.2 Hypothesis: three-model consensus has partial implementation

bc-ai already has Maker/Checker/Gate role separation. The vocabulary harmonization (Gate vs Moderator) is cosmetic. The harder gaps observed in the inventory are:

- Provider diversity (not just role separation) for high-stakes panels. Only `cc_field_audit` is partially cross-family (Gemini + Anthropic across roles); other flows are Nova-family-only.
- Same-input-snapshot enforcement (input-hash mechanism — gap).
- Immutable panel records with BCF NF1 shape (gap, but bo_verification_log and catalog_verification_log are partial).

A D6 decision authorizing Framework Approval for scopes 1, 2, 3 may need these gaps filled first.

### 9.3 Hypothesis: the certification_record table is the closest existing foundation for BCF authoring records

Reuse > rewrite. Extending `contract.certification_record` to carry BCF NF1 fields appears cheaper than introducing a parallel table. The migration cost would be the 3,493 existing rows being re-shaped + the action_code vocabulary cleanup. D6 or a sibling decision will make the call.

### 9.4 Hypothesis: bc-seed is load-bearing

The BCF promise that "AI's proposals trace to bc-seed lineage; never fabricated" depends on bc-seed being current, comprehensive, and queryable. D6 may want to name bc-seed coverage and currency as a dependency, either by including coverage targets in scope or by explicitly deferring bc-seed expansion to a sibling track.

### 9.5 Observation: operator UI is the longest single gap

8 BCF surfaces are gaps in bc-admin (Panel Transcript Viewer, Calibration Dashboard, Authoring Panel Rejection Log, Reference Impact Viewer, Policy Management, Operator-confirm UI, Activity Dashboard, Operator Notifications). Whatever first-shipped scope D6 selects, it would be unusable without at minimum the UI surfaces the operator interacts with for that scope. The gap-pass document is the right place to translate this observation into a build-order with effort sizing.

### 9.6 Observation: vocabulary cleanup (D3) is bigger than it appears

Beyond the obvious renames, the lifecycle-column situation requires a design decision: keep two columns with a strict invariant, or consolidate to one column with a migration. The 4,769 impossible-state rows are evidence that "keep two columns and trust people to keep them consistent" does not work in practice. D6 or D3 will need to pick.

### 9.7 Hypothesis: smallest credible first-shipped scope

**This is an inventory-derived hypothesis for the gap-pass document and the D6 ADR to consider; it is not a scope decision the inventory locks in.**

A plausible smallest first-shipped BCF scope, derived from what the inventory shows is reusable + what is gap, is:

- **Scope 1 (BF/BO) only**, with the existing standard-field.service + business-object.service adapted, the cc_field_audit and bf_dedup + bo_dedup + bo_composer agents wired to a single panel infrastructure, the certification_record table extended for BCF NF1, the Panel Transcript Viewer + Authoring Panel Rejection Log + Activity Dashboard built, and the legacy disposition resolved.
- Scopes 2 (CF) and 3 (BF↔CF mapping) follow once scope 1 is operating with calibration data accumulating.

The reasoning: scope 1 has the highest concentration of existing reusable artifacts (bf_dedup, bo_composer, bo_dedup are direct fits) and the strongest data motivation (4,769 impossible-state BFs need addressing). Anything larger at first shipping risks the same throughput collapse that prompted BCF in the first place.

D6 may reject this scope, choose a different one, or stage differently. The gap-pass document is where the analysis turns into a build order.

### 9.8 Risks worth surfacing to the D6 ADR

- **Calibration regression on day 1**: AI-by-default with no prior calibration data means the regression threshold (BCF chapter 9 F12) cannot be set from evidence on first activation. D6 will likely need to specify how the threshold is set initially (e.g. conservative bound; auto-pause if any operator override in first N actions).
- **Operator workload paradox**: if BCF Authoring Panel rejects too aggressively, operators get a flood of rejection-log reviews; if it rejects too loosely, garbage enters the catalog. Calibration cycle is the answer but takes time.
- **bc-seed coverage gaps**: if the OAGIS/standards seed is missing entries for some BF/CF categories, AI hits no-fabrication blocks and routes everything to OPERATOR_REVIEW, defeating the framework's throughput purpose.
- **Vocabulary inconsistency mid-migration**: if the D3 cleanup ships incrementally, code paths and UI labels may disagree for a window.

---

## 10. Process commitments

- This inventory is point-in-time (2026-05-18). Data state and source-code state will change; re-survey before D6 if more than a week has passed.
- The per-artifact classifications (sections 1-8) are inventory observations against the BCF requirements. They are inputs to the gap-pass document and the D6 ADR; they are not themselves governance acts.
- Section 9 contains hypotheses and observations derived from the inventory; it is explicitly not a build-plan or scope decision. The gap-pass document is the right place to translate observations into build orders with effort sizing. D6 is the governance act that locks scope and authority.
- The MCF inventory pass (separate document) is independent of this one and proceeds in parallel.

## 11. Open questions surfaced by the inventory

- Disposition choice (§9.1) — operator decision.
- bc-seed update cadence and coverage gaps (§6).
- Vocabulary harmonization direction: bc-ai "Gate" vs BCF "Moderator" — pick one.
- Whether to extend `certification_record` or introduce a parallel `panel_output_record` table.
- Whether to consolidate `status_code` + `catalog_state_code` into a single column or keep two with strict invariant.
- First-shipped scope (§9.7) — operator decision.
- Initial calibration regression thresholds (§9.8) — needs design.
- Operator-confirm rule grammar (BCF chapter 4 open question).
- Closed REJECT-eligible defect-code list (BCF Deferral D4).
- Policy-versioning and policy-history retention strategy.
- Whether BCF Activity Dashboard joins DevHub session events or is a separate stream.
