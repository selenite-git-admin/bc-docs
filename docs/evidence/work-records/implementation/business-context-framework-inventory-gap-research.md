---
title: Business Context Framework — Inventory Gap-Research Sweep (first pass)
status: draft
date: 2026-05-18
project: bc-docs
domain: contracts
subdomain: catalog
focus: inventory
session: SES-0e109c
---

# Business Context Framework — Inventory Gap-Research Sweep (first pass)

**Purpose.** Identify gaps in the current BCF inventory (`business-context-framework-inventory.md`) caused by assuming existing services work as intended when prior session evidence shows they did not. Cross-checks the inventory's per-artifact classifications against the failure-evidence map (`business-context-framework-failure-evidence.md`) and the underlying DevHub / ADR / session record.

**Discipline (operator-supplied).**
- Source evidence only. No architecture proposed. No requirements rewrite. **The inventory document is not modified by this sweep.**
- Missing evidence is classified as `evidence gap`, not as a proven defect.
- BCF-direct issues are kept separate from MCF / runtime / UI-adjacent issues.
- Old "engine" / "admission" vocabulary is flagged as historical only; not reintroduced as target architecture.
- Final inventory verdicts are not decided. Only candidate shifts are flagged.
- Where evidence conflicts, both sides are preserved and the finding is marked `needs Codex verification`.

**Method.** Read the inventory section by section; for each classified artifact, ask "does the failure-evidence map (FEM) or any source record contradict, refine, or extend the inventory's classification?" Findings G1–G27 below capture only the gaps, not the agreements.

**Source legend.** `FEM Fxx` = finding in failure-evidence map. `INV §x.y` = section in inventory. `ADR-xxxxxx` = ADR file in `bc-docs-v3/docs/adrs/`. `FEEDBACK-name` = memory file in `~/.claude/projects/.../memory/`. `SES-xxxxxx` = DevHub session. `TSK-xxxxxx` = DevHub task.

---

## 1. Executive summary

1. **The inventory's "adapt" classifications for BF/BO/CF services consistently understate the gap.** Multiple "adapt" rows describe vocabulary harmonization + Framework Approval wrapping; the FEM shows the underlying services bypass their own gates (F1 oagis auto-certify), enforce asymmetric checks (F10 BO cert checks BF not CF), or have no enforcement at any reference boundary (F13 CF cert nowhere checked).
2. **Two BCF-direct services missing from the inventory entirely.** `FieldMappingService.suggest()` and `CanonicalWizardService` (FEM F19) are described in ADR-1ce490 §3 as load-bearing contamination vectors but do not appear in INV §2. Also missing: assembleInputPayloads alias-overwrite bug (FEM F20).
3. **bc-seed verdict (keep-as-substrate + wrap) is unsupported by operational evidence.** INV §6 lists open questions (update cadence, coverage gaps, latency, versioning) that match FEM F34 — flagged there as evidence gap. The inventory's classification is a planning assumption, not a verified one.
4. **D409 rules-stage vs AI-panel divergence (25/25 vs 2/25, FEM F4/F29) is not surfaced in the inventory.** INV §2.1 treats `bf-correction.helper.ts` (D408 validators) as "sound" and "aligning with BCF PE1-PE6"; the FEM shows the AI panel disagrees with the rules stage by an order of magnitude on the same cohort.
5. **`certified` semantics are inventoried as a vocabulary problem; FEM evidence (F1/F2/F22) shows this is not merely a vocabulary problem; it is an evidence-grade publication / approval semantics problem.** INV §1.2 + §7.2 classify `certified_catalog` as a "non-Foundation state name" needing rename; the underlying issue is that the cert-as-flag mutation accepted 462 placeholder-defined rows. Rename without ledger semantics would preserve the defect.
6. **bc-ai provider-diversity gap is correctly inventoried (INV §3.4) but the inventory does not surface the operational consequence.** FEM F30 shows D409 was explicitly authored to prevent LLM auto-certification fabrication, i.e. a prior shape the inventory's "adapt" verdict assumes will not recur post-harmonization.
7. **Helper-script trust failure mode is not inventoried at all.** FEM F42 (PLN-c028cd's 1,389 bulk-generated artifacts, 0 snapshots, ~9h wasted; `evaluate-ready-mcs.mjs` hardcoded to wrong tenant) names a category of tooling the inventory does not survey.
8. **Inventory verdicts on MCF/out-of-scope artifacts may obscure BCF-adjacent contamination.** `MetricWizardService.completeMetric` (F27, silently 500-ing 3 weeks) and the 778 orphan `metric_contract` rows (F28) sit at the BCF boundary; they affect what BCF observes downstream even if they are MCF-authored.

---

## 2. Findings table

| # | Title | Affected artifact / service | Inventory classification (visible) | Evidence source | Excerpt / paraphrase | Failure mode | BCF relevance | Evidence class | Confidence | Suggested inventory impact | Open question for Codex |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G1 | OAGIS auto-certify path not surfaced under `standard-field.service.ts` adapt verdict | `oagis-onboarding.service.ts` `bulkCertifyFields()` invoked immediately after `bulkCreateFields()` | Not directly inventoried; `standard-field.service.ts` classified **adapt** (INV §2.1) with vocabulary-cleanup framing | FEM F1; ADR-1ce490 §Open items #6 | Importer auto-calls `bulkCertifyFields(...)` even when `field.description` empty → row enters at `status=certified` with synthetic fallback def | gate-bypass; fabrication | direct | ADR/design record | high | adapt → consider **deprecate path for the oagis auto-cert call site** (independent of standard-field.service.ts verdict) | Is the auto-certify call still present in current commit? Are there other call sites that bypass certifyField? |
| G2 | INV §1.3 explains `admit_bf_catalog` (1,651 rows) as vocabulary defect only; does not link to the 462 placeholder-defined rows from D408 audit | `contract.certification_record` action codes | INV §1.3 = vocabulary defect; INV §2.8 = **adapt** (extend with NF1 fields) | FEM F2; ADR-1ce490 calibrated 2026-05-16 | 462 rows `certified` with templated placeholder defs and zero anchor evidence; 4,141 anchorless overall | placeholder/padding; state-inconsistency | direct | DB/query-observed + ADR | high | adapt — confirmed; **add evidence-grade column to migration scope** (vocabulary cleanup alone insufficient) | Of the 1,651 `admit_bf_catalog` records, how many overlap the 462 placeholder-defined population? |
| G3 | D409 rules-stage vs AI-panel divergence (25/25 vs 2/25) absent from `bf-correction.helper.ts` adapt verdict | `bf-correction.helper.ts` D408 validators | INV §2.1 = **adapt**; described as "sound and aligning with BCF PE1-PE6" | FEM F4/F29; operator-supplied 2026-05-17 audit summary | Rules-stage classifier said 25/25 ADMIT_READY; AI panel said 2/25 (8%); 11 REJECT_BAD_MODEL, 12 NEEDS_EVIDENCE | gate-bypass; scope-conflation | direct | operator audit | high | adapt remains; **add caveat that rules-stage validators alone are insufficient as gate**; do not let "sound" framing carry forward unchallenged | Are PE1-PE6 in BCF requirements aligned with the AI panel's `REJECT_BAD_MODEL` defect classes, or with the rules-stage classifier's `ADMIT_READY_CANDIDATE` envelope? |
| G4 | Name-splitter corruption (FEM F5) is not inventoried under any BF service | Name-splitter / field-code normalizer (location not yet identified — generator or parser) | Not inventoried | FEM F5; operator audit summary | 11/25 D409 rows REJECT_BAD_MODEL due to multi-word property fragments absorbed into `object_class` | other (name corruption); alias-mismatch | direct | operator audit | medium | **gap** — add row identifying the normalizer and assigning a verdict | Where does the name-splitter live? (BF authoring pipeline upstream vs AC parser vs BF service itself?) |
| G5 | BO cert gate asymmetry — "no CF check anywhere downstream of BO composition" mis-located on approveObject | `business-object.service.ts::approveObject` (BF-composition approval, correctly BF-scoped); **live CF-cert gap is at CC mapping / reference-time surfaces, captured by G6b** | INV §2.2 = **adapt**; notes minimum-composition re-encoding only | FEM F10; ADR-a17d0f §C6; Codex pass §8.1 (business-object.service.ts:611/700) | BO approval is BF-composition approval and does NOT need a CF check; Codex confirms BF-cert + SDA evidence check is present. The actual CF-cert reference-time gap lives at CC mapping writes — see G6b. | gate-bypass (mis-anchored on approveObject) | direct (re-anchored to G6b) | ADR + code | high | **G5 anchor corrected**: do not add CF-cert enforcement to approveObject; the live gap is at CC mapping (G6b). No `business-object.service.ts` adapt-scope change driven by G5. | None remaining for approveObject; live question moved to G6b. |
| G6 | `canonical-field.service.ts` adapt verdict notes dormant lifecycle but not the reference-time enforcement gap | `canonical-field.service.ts`; `metric-readiness.service.ts::bind`; `cc_field_mapping` insert | INV §2.3 = **adapt** ("activate the dormant lifecycle"); INV §2.4 cc-onboarding = **wrap** | FEM F13/F15; ADR-a17d0f §C6 | No service path checks CF cert at MC bind / MC activate / cc_field_mapping insert; 603/603 CFs in `draft`; `semantic_family` enum named only in code comment, no DB CHECK, no service path | gate-bypass; missing-evidence | direct | DB/query-observed + ADR | high | adapt confirmed; **candidate adapt scope should include reference-time enforcement and `semantic_family` substrate** (pending Codex verification of exact bind sites) | Catalog the full set of reference sites where CF cert should be checked but is not. Is there a DB CHECK on `semantic_family` (inventory says no — confirm). |
| G7 | Meaning-once invariant on `cc_field_mapping` not inventoried | `cc-onboarding.service.ts::addFieldSelection` / `addMappings` / `replaceMapping` | INV §2.4 = **wrap** (BCF chapter 14 mapping authoring) | FEM F16; ADR-a17d0f §C5/§4 G10 | No write-time check for duplicate semantic signatures; audit found 144 R4 funnel-padding candidates and 172 normalized-form stem-clusters | missing-evidence; padding/placeholder | direct | DB/query-observed | high | wrap → **wrap-with-gap** (the wrap must add a Meaning-once write-time check; inventory does not state this explicitly) | What is the current write-time validation in addFieldSelection / addMappings? Does any existing audit script implement the stem-clustering check or only post-hoc analysis? |
| G8 | `FieldMappingService.suggest()` not inventoried | `FieldMappingService.suggest()` and `CanonicalWizardService` | Not inventoried | FEM F19; ADR-1ce490 §3 | Both services read catalog without state-awareness — contamination vector; uncertified rows surface as bindable in UI | scope-conflation; missing-evidence | direct | ADR | high | **gap** — inventory should list these and assign verdict (likely adapt) | Do these services exist in current bc-core/src and what catalog-state filtering, if any, do they apply server-side? |
| G9 | "Duplicate primary alias overwrite" in `assembleInputPayloads()` not inventoried | `assembleInputPayloads()` (runtime) | Not inventoried (runtime is outside BCF scope per INV §Method); but it consumes BCF outputs | FEM F20; session_d323_greenfield_oc_enrichment.md §Rejection breakdown | 30 of 80 MC rejections traced to alias overwrite bug combined with missing CC data | alias-mismatch | adjacent (runtime) | DevHub/session | medium | adjacent — flag in INV §2.5 "out of BCF scope" rows that this contaminates downstream MCF; no BCF verdict shift | Is the bug still live? If yes, does it affect BF↔CF mapping resolution outputs that BCF authors? |
| G10 | OC field_map necessary but not sufficient — not surfaced under wrap verdict | `cc-onboarding.service.ts` wrap | INV §2.4 = **wrap** | FEM F21; session_d323 | OC field_map enrichment moved 15/93 MCs to producing; remainder blocked on missing CCs/readers + cc_field_mapping gaps + alias bug | scope-conflation | adjacent | DevHub/session | high | wrap unchanged; add note that wrap success ≠ chain completeness | None |
| G11 | "`certified` = status flag" semantics not surfaced as the core defect (only as vocabulary) | `contract.business_field` certification semantics | INV §1.2 / §7.2 = vocabulary defect; INV §2.8 = **adapt** certification_record | FEM F22; ADR-1ce490; ADR-a17d0f | Cert treated as status-flag mutation; no ledger row required; violates Foundation Invariant VI | missing-evidence; state-inconsistency | direct | ADR | high | adapt confirmed; **inventory framing of "vocabulary defect" understates the issue**; flag for D6 ADR that rename without ledger semantics preserves the defect | Should this be split into two ADR scopes (D3 vocab vs D6 evidence-grade ledger) or handled together? |
| G12 | Five competing certification lifecycles not catalogued at INV §1.2 | `business_field` lifecycle; `business_object`; `canonical_field`; CC; MC | INV §1.2 lists state pairs; INV §7.4 names non-Foundation states; does not enumerate the 5 lifecycles | FEM F23; ADR-a17d0f §C1 | Five effective lifecycles across 4 governing sources and 3 service implementations | vocabulary-drift; state-inconsistency | direct | ADR | high | adapt; **add 5-lifecycle enumeration table to inventory** as input to D3/D6 | Which lifecycle is the live source of truth per service? |
| G13 | `chain_status` SSOT pre-activation race not surfaced as adjacent | `ChainStatusService.getActiveMcVersions()` | INV §2.5 = "out of BCF scope; MCF"; INV §8.4 = `IntegrityService` deprecate | FEM F25; ADR-bebaec 2026-05-14 erratum | Filter to active only → new MC pre-activation has NULL row → MLS-14 refuses for wrong reason | silent-drop; gate-bypass (false reject) | MCF (adjacent) | ADR | high | unchanged; flag that BCF Lifecycle Audit Panel (chapter 7 stage 3) may read this and inherit the race semantics | Does the erratum cover all activation paths or only ContractService.transitionState? |
| G14 | IntegrityService deprecation correct but call sites not re-verified | `integrity.service.ts` | INV §8.4 = **deprecate** | FEM F26; ADR-bebaec | Deprecated per D305; kept for two callers only (per file docstring) | silent-drop; alias-mismatch; scope-conflation | adjacent | ADR | medium | deprecate confirmed; **needs Codex verification that no new callers added since the docstring was written** | Grep all imports of integrity.service across bc-core/bc-admin; produce current caller list. |
| G15 | `MetricWizardService.completeMetric` silently 500-ing 3 weeks — adjacent contamination not flagged | `MetricWizardService.completeMetric` | Not inventoried (out of BCF scope; MCF) | FEM F27; session_d340_definition_canonical.md | Silently 500-ing ~3 weeks; bypassed seed-promotion canonical path; quarantined | silent-drop; gate-bypass | MCF (adjacent) | DevHub/session | high | no BCF verdict; **add adjacent-contamination note**: MCF wizard bypass affected which entries BCF would inherit as referenced | Is the quarantine complete? Any UI dead ends from bc-admin to the quarantined endpoint? |
| G16 | 778 orphan `metric_contract` rows — adjacent to BCF reference impact | `metric.metric_contract.metric_definition_id` historical orphans | Not inventoried (MCF) | FEM F28; session_d340 | 778 orphan (589 active + 189 archived); unidentified bulk script via createMinimalMetricContract | state-inconsistency | MCF (adjacent) | DB/query-observed | high | no BCF verdict; flag that BCF Reference Impact Viewer (INV §4.2 gap) must handle orphans or be specified to ignore them | Who/what created the orphans? Never traced. |
| G17 | bc-ai provider-monoculture risk inventoried but operational consequence not | All Nova-only bc-ai flows (bf_dedup, bf_pii_classify, bo_composer, bo_dedup, field_mapper) | INV §3.1 = **adapt** with provider-diversity gap noted | FEM F30; ADR-b8ec00 §Context | D408/D409 explicitly authored to prevent LLM auto-certification that fabricates evidence | fabrication | direct | ADR | medium | adapt confirmed; **add operator-facing risk note in inventory §3.4** that historical attempts in this shape produced the failures D409 was built to refuse | None |
| G18 | Mega-onboarding / coverage-as-KPI pressure not surfaced as risk in inventory § 9.7's first-shipped-scope hypothesis | Hypothesis: scope 1 (BF/BO) as smallest first-shipped scope | INV §9.7 = hypothesis | FEM F31; ADR-b8ec00 | Historical: 462 placeholder admits + funnel padding all traced to coverage-as-success-metric | padding/placeholder | direct | ADR | high | unchanged; **add explicit anti-coverage-KPI guard rail to §9.7 hypothesis** (currently absent) | None |
| G19 | Rejection observability gap not surfaced under any bc-admin adapt | Inspector / metric_evaluation join to evidence envelope | INV §4 lists ActivityLogPage adapt + RejectionSummaryPage keep (runtime) | FEM F32; FEEDBACK-runtime_readiness_gate; SES-594568 | No Inspector surface reads latest rejection reason; persisted in `evidence_object` but not surfaced; forensics queried wrong table for a day | missing-evidence; untrusted-helper | adjacent | DevHub/session | high | flag as adjacent; consider whether BCF Authoring Panel Rejection Log (INV §4.2 gap) should subsume / share substrate with the runtime rejection surface | Should the runtime rejection envelope and the BCF Authoring Panel rejection log share storage and viewer? |
| G20 | D335 formula↔rule audit insufficiency not surfaced under cc_field_audit verdict | `cc_field_audit` agent (BCF strongest fit) | INV §3.1 = **adapt** ("strongest existing fit") | FEM F33; FEEDBACK-d335_audit_insufficient_alone | Scope is formula↔rule only — does not catch CF→BF semantic mismatch; SUM→COUNT can replace constant-wrong with varying-wrong | scope-conflation; missing-evidence | direct | DevHub/session | high | adapt confirmed; **inventory's "strongest existing fit" framing needs softening** — fit on shape, but the audit's known scope is structurally insufficient for the load BCF places on it | What additional check class would close the semantic-mismatch gap? Defer to bc-ai inventory pass. |
| G21 | bc-seed verdict is a planning assumption, not operationally verified | `oagis-seed.service.ts`, `seed_oagis_components`, `seed_bo_crosswalk`, `seed_metrics` | INV §6 / §2.7 = **keep-as-substrate + wrap**; INV §6 lists open questions but holds verdict | FEM F34/F35 (evidence gap); SES-594568 (header hardcoding only indirectly) | None of the supplied sources name bc-seed Mongo operational behavior at BCF scale | evidence gap | direct | inference | low | **needs Codex verification** — inventory verdict held without operational evidence; downgrade to provisional until coverage/currency verified | Pull bc-seed coverage report: how many OAGIS Nouns/Components/Fields are present vs target? Update cadence? Last sync? |
| G22 | bc-admin platform/tenant scope-conflation history not surfaced | bc-admin pages (system-level finding, not page-level) | INV §4 verdicts per page; no system-level note | FEEDBACK-platform_vocabulary | bc-admin previously used tenant-runtime vocabulary (SO/CO/AO) and tenant-scoped endpoint design before separation | scope-conflation; vocabulary-drift | adjacent | feedback note | medium | flag in §4 preamble that vocabulary discipline is a recurrent issue; D3 cleanup carries this load | None |
| G23 | "Producing MC" pilot framing precedent not surfaced as risk to BCF Calibration Dashboard scoping | BCF Calibration Dashboard (gap) | INV §4.2 = **gap** | FEM F41; FEEDBACK-runtime_readiness_gate | "14 runtime-ready" hid 7 distinct materialization tiers — must qualify by tier | other (count framing); padding/placeholder | direct | DevHub/session | high | gap unchanged; **add design constraint to gap spec**: any BCF dashboard count must qualify by sample/calibration/sampling tier so the runtime-readiness mistake doesn't recur | None |
| G24 | Helper-script trust failure category not inventoried | `bc-core/scripts/` helper category (e.g. `evaluate-ready-mcs.mjs`); PLN-c028cd | Not inventoried | FEM F42; FEEDBACK-runtime_readiness_gate; FEEDBACK-session_discipline_d268 | `evaluate-ready-mcs.mjs` hardcoded to wrong tenant + pre-DEC-f02230 schema; PLN-c028cd bulk-generated 1,389 chain artifacts → 0 snapshots → 9h wasted | untrusted-helper; gate-bypass; padding/placeholder | adjacent | feedback note | high | **gap** — add helper-script tooling category to inventory; default-untrusted classification with provenance audit required before reuse | Full grep of `bc-core/scripts/` against current schema and tenant; identify hardcoded assumptions. |
| G25 | Funnel/UI "make it green" fallback precedent not surfaced as risk to BCF UI gap-specs | All BCF UI gap surfaces (Calibration Dashboard, Rejection Log, etc.) | INV §4.2 lists 8 surfaces as gaps | FEM F43; FEEDBACK-no_hacks_no_bypass | Funnel code had fallback making 7 MCs appear "producing" while chain_complete=0 | gate-bypass; padding/placeholder | direct | feedback note | high | gaps unchanged; **add anti-fallback constraint** to UI gap specs (no surface may compute a state inconsistent with its named gate) | None |
| G26 | SOPs / spine docs carrying live counts not surfaced as inventory hygiene risk | INV §1 itself (which carries live counts) | INV §10 says "re-survey before D6 if more than a week" | FEM F40; FEEDBACK-no_stats_in_sops | contract-chain-assembly.md said "0 BFs, 0 BOs" while reality was 171/4,083 | other (stale doc) | cross-cutting | feedback note | high | unchanged but **process commitment §10 should be strengthened**: inventory counts must be timestamped and re-queryable; consider live-query callouts instead of embedded numbers | None |
| G27 | "Adapt" verdict on cc_field_audit assumes provider-diversity upgrade is incremental; FEM F30 implies it is load-bearing for the BCF promise | `cc_field_audit` agent | INV §3.1 = **adapt** (partial cross-family) | FEM F30; ADR-b8ec00 | "LLM auto-certification" risk explicitly authored against | fabrication | direct | ADR | medium | adapt confirmed; **flag that adapt scope must include the OpenAI Gate role addition before the agent serves Publication Panel load, not after** | When does the OpenAI integration land? Is there a TSK for it? (TSK-9c97de mentioned in audit summary for bc-ai bf_admission_review endpoint.) |

---

## 3. Per-area notes

**(a) BF authoring & admission.** The inventory's "adapt" verdict on `standard-field.service.ts`, `bf-correction.helper.ts`, and `bf-catalog-state.guard.ts` is consistent with the failure evidence only at the vocabulary / Framework-Approval-wrapping level. The deeper failures — auto-certify bypass (G1), placeholder-grade certification (G2), rules-stage vs AI-panel divergence (G3), name-splitter corruption (G4) — are not surfaced in the inventory's per-row notes. None of this requires a verdict change; all of it requires the "adapt" scope to be widened beyond vocabulary.

**(b) BO authoring & verification.** The asymmetric BO cert gate (G5) is the most concrete BCF-direct gap not visible in the inventory's "adapt" verdict on `business-object.service.ts`. The bo-verification.service.ts row correctly flags single-provider Gemini and missing NF1 fields; FEM agrees.

**(c) CF authoring & certification.** Inventory describes CF lifecycle as "dormant" (3 lifetime records) and treats this as a scope to be activated. FEM evidence (G6) shows the lifecycle is not just dormant but unenforced at every reference boundary; activation alone without reference-time checks would not satisfy BCF chapter 14. The semantic_family substrate (DB CHECK + service path + closed enum) is a gap that the inventory describes but does not classify as a build item.

**(d) BF↔CF mapping.** Two BCF-direct services are missing from the inventory entirely (G8: `FieldMappingService.suggest()` and `CanonicalWizardService`). The cc-onboarding wrap verdict needs the explicit Meaning-once write-time check requirement (G7). The runtime-side alias-overwrite bug (G9) is adjacent contamination worth noting in §2.5.

**(e) Catalog publication / certification flow.** The inventory frames the certification problem primarily as vocabulary (INV §7); the FEM frames it primarily as evidence-grade ledger semantics. Both framings are correct but the inventory's framing risks D3 (vocab cleanup) being treated as sufficient when the evidence shows D6 (Framework Approval + authoring records) must land alongside. G11/G12 capture this.

**(f) AI panels & verification.** Inventory correctly identifies provider-monoculture as a gap; does not surface that bc-ai's audit scope (cc_field_audit) is structurally insufficient for the CF→BF semantic-mismatch class (G20). The "strongest existing fit" language for cc_field_audit needs softening.

**(g) bc-seed.** The inventory holds a verdict (keep-as-substrate + wrap) but lists the operational verification questions as open. The FEM lists the area as an evidence gap. Both are right; the inventory verdict should be treated as provisional until operational evidence lands (G21).

**(h) Operator UI.** Inventory's 8-gap list is well-shaped. The cross-cutting risks — pilot-framing precedent (G23), no-fallback constraint (G25), platform/tenant vocabulary discipline (G22) — should be incorporated into the gap specs as design constraints.

**(i) Cross-cutting.** Helper-script tooling (G24) is a category the inventory does not survey; FEM F42 makes it a high-value addition. Inventory hygiene itself (G26) — the inventory carries live counts that will go stale.

---

## 4. Evidence index

| Source | One-line takeaway |
|---|---|
| `business-context-framework-inventory.md` | Subject of this sweep; per-artifact classifications point-in-time 2026-05-18. |
| `business-context-framework-failure-evidence.md` (FEM, 47 findings) | First-pass evidence map; cross-referenced throughout this sweep. |
| ADR-1ce490.md (D408) | Calibrated audit: 462 placeholder certs, 4,141 anchorless, 779 G1 fails, 15 T4 hard fails. |
| ADR-a17d0f.md (G11 / SDA) | Six conflicts C1–C6 on certification semantics. |
| ADR-b8ec00.md (D409) | Multi-agent factory authored explicitly against LLM auto-certification. |
| ADR-bebaec.md (D305) | IntegrityService 5 bugs; chain-status SSOT; pre-activation erratum. |
| operator-supplied 2026-05-17 D409 batch-1 summary | Rules 25/25 vs AI 2/25; 11 name-splitter corruptions. |
| FEEDBACK-funnel_padding | 81 CFs → 1 NETWR; rejected; MLS-14 gate. |
| FEEDBACK-no_placeholders | Empty/null preferred over generic placeholder text. |
| FEEDBACK-no_hacks_no_bypass | chain_complete=0 + "producing" → fallback bypass. |
| FEEDBACK-zero_claims_policy | No capability claim without first-hand E2E proof. |
| FEEDBACK-session_discipline_d268 | PLN-c028cd: 1,389 bulk artifacts, 0 snapshots, 9h wasted. |
| FEEDBACK-d335_audit_insufficient_alone | Formula↔rule audit passes on semantic-mismatch mappings. |
| FEEDBACK-runtime_readiness_gate | Contract-gate eligibility ≠ runtime-ready; helper-script trust; envelope discoverability gap. |
| FEEDBACK-platform_vocabulary | bc-admin must speak SC/AC/OC/CC/MC/IC; catalog "Object" → "Source Table". |
| FEEDBACK-no_stats_in_sops | Spine doc said 0/0 vs real 171/4,083. |
| session_d323_greenfield_oc_enrichment.md | 15/93 MCs producing after OC enrichment; alias-overwrite + cc_field_mapping gaps remain. |
| session_d340_definition_canonical.md | 778 orphan metric_contracts; MetricWizardService silently 500-ing 3 weeks. |
| SES-594568 (MEMORY entry) | mc-onboarding header hardcoding; KNOWN_CONSTANTS non-SoT; 1,216 draft seeds. |

---

## 5. Candidate inventory verdict shifts (flags, not decisions)

Split into three buckets so a subsequent editing pass does not accidentally pull MCF/runtime concerns back into BCF scope.

### 5.1 BCF inventory changes (in scope of BCF inventory edit)

| Inventory row | Current verdict | Candidate shift | Driver |
|---|---|---|---|
| `oagis-onboarding.service.ts` auto-certify call site | not inventoried | add row: candidate **deprecate** the auto-cert call site (independent of `standard-field.service.ts`) | G1 / FEM F1 |
| `standard-field.service.ts` | adapt | keep adapt; **widen scope** beyond vocabulary to include evidence-grade ledger + auto-cert bypass disposition | G1/G2/G3/G11 |
| `bf-correction.helper.ts` "sound and aligning with PE1-PE6" framing | adapt | keep adapt; **soften "sound" framing** pending PE reconciliation against AI-panel defect classes | G3 |
| `business-object.service.ts::approveObject` | adapt | **no scope change driven by G5** — approveObject is BF-composition approval and is correctly BF-scoped; CF-cert gap is at CC mapping (G6b), not here | G5 (anchor corrected) |
| `canonical-field.service.ts` | adapt | keep adapt; **candidate scope additions**: reference-time enforcement + `semantic_family` substrate | G6 |
| `cc-onboarding.service.ts` wrap | wrap | wrap-**with-gap**: Meaning-once write-time check is gap, not assumed | G7 |
| `FieldMappingService.suggest()` / `CanonicalWizardService` | not inventoried | add rows: candidate **keep / adapt** (state filtering present per Codex pass — see §8) | G8 |
| Name-splitter / field-code normalizer | not inventoried | add row: candidate **needs Codex verification** to locate the artifact | G4 |
| `cc_field_audit` agent | adapt ("strongest existing fit") | adapt; **soften framing**; OpenAI Gate role pre-condition for Publication-Panel load-bearing use | G20/G27 |
| All Nova-only bc-ai flows | adapt | adapt; **add operator-facing risk note** on provider-monoculture historical fabrication shape | G17 |
| `oagis-seed.service.ts` + bc-seed collections | keep-as-substrate + wrap | **needs operational verification** — verdict held without operational evidence (Mongo not queried in Codex pass) | G21 |
| `bc-core/scripts/` helper category | not inventoried | **add gap row**: default-untrusted; provenance audit required | G24 |
| Inventory §1 live counts | timestamped 2026-05-18 | **process strengthening**: counts should be live-queryable, not embedded | G26 |
| §9.7 first-shipped-scope hypothesis | hypothesis only | unchanged; **add anti-coverage-KPI guard rail** | G18 |
| BCF Authoring Panel Rejection Log gap | gap | gap; **consider shared substrate with runtime rejection envelope** | G19 |
| BCF Calibration Dashboard gap | gap | gap; **add tier-qualification design constraint** | G23 |
| BCF UI gaps generally | gap | gap; **add anti-fallback constraint** | G25 |
| bc-admin §4 preamble | per-page verdicts | **add system-level note** on vocabulary discipline recurrence | G22 |

### 5.2 BCF-adjacent notes (record adjacency in inventory; do not pull into BCF verdicts)

| Inventory row | Current verdict | Candidate adjacency note | Driver |
|---|---|---|---|
| `IntegrityService` | deprecate | deprecate confirmed; **needs Codex verification** of current call sites | G14 |
| `chain_status` pre-activation race | out-of-BCF-scope (MCF) | unchanged; **flag inheritance risk** for BCF Lifecycle Audit Panel (Codex pass: explicit fix in place — see §8) | G13 |

### 5.3 MCF deferred notes (out of BCF inventory; recorded so they are not lost)

| Inventory row | Current status | Deferred note | Driver |
|---|---|---|---|
| `MetricWizardService.completeMetric` | not inventoried (MCF) | no BCF verdict; **deferred to MCF inventory** — Codex pass confirms quarantine | G15 |
| 778 orphan `metric_contract` rows | not inventoried (MCF) | no BCF verdict; **deferred to MCF inventory**; informs Reference Impact Viewer gap-spec design | G16 |

---

## 6. Open questions for Codex deep verification

1. **OAGIS auto-certify call site (G1).** Is `bulkCertifyFields()` still invoked immediately after `bulkCreateFields()` in the current commit? Are there other call sites that bypass the per-field certify path?
2. **D408 audit overlap (G2).** Of the 1,651 `admit_bf_catalog` certification_record rows, how many correspond to the 462 placeholder-defined BFs from the D408 audit population?
3. **PE-vs-AI-panel reconciliation (G3).** Are BCF PE1-PE6 aligned with the AI panel's `REJECT_BAD_MODEL` defect classes, or with the rules-stage classifier's `ADMIT_READY_CANDIDATE` envelope?
4. **Name-splitter location (G4).** Where does the multi-word-property → object_class corruption originate — BF generator, AC parser, BF service input normalizer, or upstream OAGIS ingest?
5. **BO approve internals (G5).** Where exactly in `approveObject` does the BF cert check live, and what is the precise enforcement vs advisory status?
6. **CF reference-time enforcement sites (G6).** Catalog all reference sites where CF cert should be checked but is not (`metric-readiness.service.ts::bind`, MC version activate, cc_field_mapping insert, CM authoring, OC authoring). Confirm absence of DB CHECK on `semantic_family`.
7. **Meaning-once substrate (G7).** What is the current write-time validation, if any, in `addFieldSelection` / `addMappings`? Does any existing audit script implement the stem-clustering / normalized-form check, or is it post-hoc only?
8. **FieldMappingService state filtering (G8).** Confirm presence of both services in current bc-core/src; document any server-side catalog-state filtering applied today.
9. **assembleInputPayloads alias bug (G9).** Is the duplicate-primary overwrite still present? Does it interact with the D305 L4 trace?
10. **IntegrityService caller list (G14).** Grep all imports of `integrity.service` across bc-core / bc-admin; produce current caller list to confirm only the two documented gates remain.
11. **MetricWizardService quarantine (G15).** Is the quarantine complete? Are there bc-admin surfaces that previously called it now showing dead-end UX?
12. **Orphan metric_contract provenance (G16).** Who/what process originally created the 589 active + 189 archived orphans via `createMinimalMetricContract`? Never traced in session_d340.
13. **chain_status erratum scope (G13).** Does the 2026-05-14 erratum cover all activation paths, or only `ContractService.transitionState`?
14. **bc-seed operational state (G21).** Pull coverage report for `seed_oagis_components`: how many OAGIS Nouns/Components/Fields present vs the BCF-needed set; update cadence; last sync; version-tracking shape.
15. **OpenAI Gate role landing (G27).** Is there an open task for adding OpenAI as the third provider in `cc_field_audit`? (Audit summary references TSK-9c97de for bc-ai `bf_admission_review` endpoint.)
16. **Helper-script audit (G24).** Full grep of `bc-core/scripts/`: identify hardcoded tenant assumptions and pre-DEC-f02230 schema references; produce trust-classification per script.
17. **Five-lifecycle enumeration (G12).** Per-service: which lifecycle is the live source of truth? (BF, BO, CF, CC, MC each implement their own variant per ADR-a17d0f.)
18. **`_hdr` SAP suffix leak (G4 adjacent).** Did the suffix originate in the source catalog register or in the BF naming generator?

---

## 7. Limitations

- **Inventory not re-verified against current commit head.** This sweep cross-checks the inventory text against the FEM and source records only; whether classifications are still accurate against the actual bc-core / bc-ai / bc-admin commit head as of 2026-05-18 is not re-validated.
- **No code reads performed in this sweep.** All findings are document-grounded. Several open questions require Codex code-level verification.
- **Single-source findings preserved.** G9 (alias bug), G15 (wizard quarantine), G19 (rejection observability) are session-note-grounded; rated medium confidence absent code re-verification.
- **bc-seed evidence is thin** in supplied sources — G21 is the explicit evidence-gap finding; additional pull required.
- **No verdicts decided.** §5 candidate shifts are flags for operator review; the inventory document is not modified by this sweep.
- **MCF / runtime adjacency findings (G9, G13, G15, G16) carry no BCF verdict** — they are surfaced to inform Reference Impact Viewer / Lifecycle Audit Panel gap specs and to mark adjacent contamination, not to expand BCF scope.

---

## 8. Codex verification pass (2026-05-18, read-only against current bc-core)

Codex performed a narrow read-only code verification pass against current bc-core. This section records what changed for each affected finding. **Source-of-truth: code line references below.** Where Codex contradicts the document-grounded text in §2, the Codex line references take precedence; the §2 row is preserved for traceability of how the finding evolved.

### 8.1 Confirmed (current, code-grounded)

| Finding | Code evidence | Outcome |
|---|---|---|
| **G1** OAGIS auto-certify path | `bc-core/src/registry/oagis-onboarding.service.ts:283` calls `bulkCreateFields()`; line 300 immediately calls `bulkCertifyFields(..., true)` | **Confirmed live.** Add `oagis-onboarding.service.ts` as its own inventory row — candidate **adapt / deprecate the auto-cert call site**. |
| **G5 (refined)** BO approval cert checks | `bc-core/src/registry/business-object.service.ts:611` checks BF `status='certified'` + SDA evidence via `findSdaCertifiedFieldIds`; certifies at line 700 | BF cert trust is **stronger than this sweep described** — SDA evidence check is present. BO approval is BF-composition approval, so **the absence of a CF cert check on approveObject is correct, not a defect**. The live CF-cert asymmetry persists at CC mapping / reference-time surfaces and is captured by **G6b**, not here. G5 row in §2 re-anchored accordingly. |
| **G7** Meaning-once write-time gap | `bc-core/src/registry/cc-onboarding.service.ts:754` validates shape, BF selection, and BF certification — **no write-time Meaning-once / semantic-signature check before mapping insert** | **Confirmed in sharper form.** Wrap-with-gap stands. |
| **G24** Helper-script trust category | `bc-core/scripts/evaluate-ready-mcs.mjs:14-21`, `:37`, `:80-85` hardcoded to `tbc_selenite_dev`, `demo-selenite`, `boundary.canonical_object`, `localhost`, version `1.0.0`. **138 of 156 script files** hit tenant/env/schema patterns | **Confirmed.** Helper scripts merit a **separate default-untrusted inventory category**. |

### 8.2 Partly reversed (state filtering present in current code)

| Finding | Code evidence | Outcome |
|---|---|---|
| **G8** `FieldMappingService.suggest()` | `bc-core/src/registry/field-mapping.service.ts:115`, `:122` filter BFs to `catalog_state_code='certified_catalog'` | **Partly reversed.** Service is present and state-filtered. Inventory should still **add the row** but the verdict is likely **keep / adapt**, not "state-blind contamination vector." |
| **G8** `CanonicalWizardService` | `bc-core/src/registry/canonical-wizard.service.ts:287`, `:309`, `:485` filter to certified BFs in both write and UI paths | **Partly reversed.** Same disposition as `FieldMappingService`. |

### 8.3 Refined / split

| Finding | Code evidence | Outcome |
|---|---|---|
| **G6** (split into G6a / G6b) | G6a — `bc-core/src/registry/contract.service.ts:70` requires `canonical_field.status_code='certified'` AND `semantic_family IS NOT NULL`, enforced at lines 128-154, **for MC activation**. G6b — `bc-core/src/registry/cc-onboarding.service.ts:770` looks up CF by name and uses `dataType` but does **not** require `cf.statusCode === 'certified'` or `semanticFamily != null` before insert/replace | **Split.** MC activation does enforce CF cert + semantic_family — G6a is closed. **CC mapping writes still do not check CF certification** — G6b remains a live gap. |

### 8.4 Already fixed / quarantined

| Finding | Code evidence | Outcome |
|---|---|---|
| **G15** MetricWizardService quarantine | `bc-core/src/registry/metric-wizard.controller.ts:71` and `metric-wizard.service.ts:220` | **Quarantine confirmed at both controller and service layers.** MCF-deferred note can be marked closed when MCF inventory is written. |
| **G13** chain_status pre-activation race | `bc-core/src/registry/contract.service.ts:578` calls `refreshChainStatusForVersion()` before MLS-14 | **Explicit fix in place.** BCF Lifecycle Audit Panel inheritance risk reduced; flag retained as design note. |

### 8.5 Unchanged (operational verification still pending)

| Finding | Code evidence | Outcome |
|---|---|---|
| **G21** bc-seed operational state | `bc-core/src/registry/oagis-seed.service.ts:89`, `:100`, `:151` — read-only Mongo proxy that returns empty results when Mongo is unavailable. Codex **did not connect to Mongo** | **Unchanged.** G21 remains **needs operational verification**, not proven defect. |

### 8.6 Net effect on the gap-research sweep

- **Strong remaining live gaps** (after Codex pass): G1 (oagis auto-cert), G6b (CF cert at CC mapping writes), G7 (Meaning-once at mapping insert), G24 (helper-script trust category).
- **Partly closed in code, inventory row still useful**: G8 (state filtering present; classify rather than omit).
- **Already closed / quarantined**: G13 (race), G15 (wizard) — record-and-close, no further BCF action.
- **Operational evidence still missing**: G21 (bc-seed) — Mongo pull required before verdict is firm.
- **Findings unchanged by this pass** (no code touched): G2, G3, G4, G9, G10, G11, G12, G14, G16, G17, G18, G19, G20, G22, G23, G25, G26, G27.

### 8.7 Codex-recommended next narrow verification pass (not started)

1. Current code re-check for G1, G5, G6a/b, G7, G8 — **done in this pass** (8.1–8.3).
2. Script/tooling audit for G24 — **partial** (scope of 138/156 confirmed; per-script trust classification still to produce).
3. bc-seed operational pull for G21.
4. Integrity / adjacent caller checks for G14, G15, G16 — only after BCF-direct checks are done.

---

## 9. Scoped inventory-edit drivers (operator-approved scope)

The first inventory-edit pass driven by this sweep is **deliberately narrow**. Five BCF-direct changes; nothing else.

| # | Driver | Action in inventory | Verdict shape | Source findings |
|---|---|---|---|---|
| 1 | **`oagis-onboarding.service.ts`** — G1 auto-cert chain still live (`:283` → `:300`) | Add as its own inventory row under §2.1 (or §2.7 if seed-grouped) | live **adapt / deprecate candidate** for the auto-cert call site | G1 (Codex §8.1) |
| 2 | **`cc-onboarding.service.ts`** — two distinct gap details | Sharpen existing wrap row in §2.4 with explicit gap callouts: (a) missing CF trust check at mapping insert/replace (CF looked up by name at `:770`, no cert/semantic_family check), (b) missing Meaning-once write-time semantic-signature check at `:754` | wrap-**with-gap** (two gap items spelled out) | G6b, G7 (Codex §8.1, §8.3) |
| 3 | **`FieldMappingService.suggest()`** and **`CanonicalWizardService`** — missing inventory rows; state filtering is present | Add two new rows in §2.4 with brief code refs | **keep / adapt**, not defect-first | G8 (Codex §8.2) |
| 4 | **Helper scripts category** (`bc-core/scripts/`) — currently uninventoried | Add new section (e.g. §2.9 or a top-level §6.5) — separate category | **default-untrusted** until provenance + tenant/env/schema assumptions are audited per script | G24 (Codex §8.1) |
| 5 | **bc-seed** — keep operational caveat | Restate §6 verdict with explicit provisional qualifier | **keep-as-substrate + wrap, provisional** — useful candidate source; operational coverage / currency / version-tracking remain unverified | G21 (Codex §8.5) |

### 9.1 Explicit non-inclusions in this inventory-edit pass

| Excluded | Reason |
|---|---|
| G13 chain_status pre-activation race | Codex §8.4: explicit fix already in place (`contract.service.ts:578`). Keep as design note for BCF Lifecycle Audit Panel; do not promote to live BCF gap. |
| G15 MetricWizardService quarantine | Codex §8.4: quarantine confirmed at both controller and service layers. Record-and-close; MCF-deferred. |
| G5 CF-cert at `approveObject` | §2 row re-anchored: BO approval is BF-composition approval and is correctly BF-scoped. The CF-cert gap lives at CC mapping and is fully captured by driver #2 above. **Do not add a CF check to approveObject in any inventory edit.** |
| All other G-findings | Out of scope for first inventory-edit pass. Remain available for subsequent passes once the five above land. |

### 9.2 Discipline for the inventory-edit pass

- The inventory edit applies only to the five drivers in §9. No other rows change.
- Each new or sharpened row must cite the Codex code line reference from §8 (not the FEM excerpt) as the load-bearing evidence.
- Vocabulary discipline holds: do not reintroduce "admit" / "admission" / "engine" language; "publication" + "approval" + "Framework Approval" remain canonical.
- §5 candidate-shifts table remains the broader inventory-research record for future passes; this driver list is a strict subset.
