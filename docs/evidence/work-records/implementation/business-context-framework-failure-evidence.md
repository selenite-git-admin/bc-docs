---
title: Business Context Framework — Failure-Evidence Map (first pass)
status: draft
date: 2026-05-18
project: bc-core
domain: bcf
focus: governance
session: SES-0e109c
---

# Business Context Framework — Failure-Evidence Map (first pass)

**Purpose.** First-pass evidence inventory of where existing BCF-relevant services, workflows, and operator surfaces did not work as intended. Scope: Business Fields (BF), Business Objects (BO), Canonical Fields (CF), BF↔CF mapping, catalog publication/certification, AI panels (Maker/Checker/Gate), gates, bc-seed substrate, and operator UI surfaces.

**Operator constraints honoured.**

- Treated as **evidence inventory, not a decision record**.
- No final architecture proposed. No requirements rewrite. Code existence is not treated as operational fitness.
- Ambiguous evidence is marked low confidence rather than resolved.
- Pairs with: `business-context-framework-requirements.md` (v0.4) and `business-context-framework-inventory.md` (verdict-pass).

**Method.** Sources read: feedback memory files (11), session notes (3), DevHub decision list (320 records, 121 BCF-relevant by keyword filter), DevHub task list (failed + parked-now), DevHub change records (340 bc-core session records), and four key ADRs (D305 / D408 / D409 / G11 SDA). The D409 BF-first Precision Batch 1 audit summary (2026-05-17) was supplied directly by the operator. Where supplied sources were thin (notably bc-seed Mongo), the evidence is flagged as a gap rather than inferred.

---

## 1. Executive summary

The dominant failure pattern across BCF-relevant artifacts is **`certified` treated as a status-flag mutation rather than an evidenced admission act**, combined with **gates that are advisory in code but load-bearing in operator expectation**. Five specific consequences recur:

1. **Mass placeholder admission.** OAGIS BF import auto-certified rows with synthetic fallback definitions; the calibrated D408 audit found 462 placeholder-defined certified rows and 4,141 anchorless rows in a population of 7,062.
2. **Rules-stage admission diverges from AI-panel admission by an order of magnitude.** D409 Precision Batch 1 (25 rows, 2026-05-17): rules-stage = 25/25 ADMIT_READY; AI panel = 2/25 (8%). The gap is systemic, not row-specific.
3. **No reference-time enforcement of certification.** All 603 CFs sit in `draft`; no service path checks CF certification at MC bind, MC activate, or `cc_field_mapping` insert. The asymmetric BO-cert gate (checks BF, not CF) is the contamination path.
4. **Meaning-once invariant unenforced at write-time.** Funnel-padding attempts (81 CFs → 1 NETWR column; 144 R4 padding candidates) reach review because no write-time semantic-signature check exists.
5. **Helper-script trust and "make it green" pressure produce gate-bypass code paths.** PLN-c028cd bulk-generated 1,389 chain artifacts and produced zero snapshots (9h wasted); a fallback path made 7 MCs appear "producing" while `chain_complete=0`; `MetricWizardService.completeMetric` was silently 500-ing for three weeks.

Forty-seven findings are catalogued across nine areas. Most carry **high** evidence confidence — the major exception is bc-seed Mongo, where supplied sources are thin and the area is flagged as an inventory gap. Inventory-verdict shift candidates are flagged in §5 for operator review; none are decided here.

---

## 2. Findings table

| # | Area | Artifact / Service / Workflow | Source ref | Intended behavior | Observed failure | Failure class | Severity | Confidence | Inventory verdict to consider |
|---|---|---|---|---|---|---|---|---|---|
| F1 | (a) BF | `oagis-onboarding.service.ts` `bulkCertifyFields()` | ADR-1ce490 §Open items #6; D408 audit | Imported BFs admitted via gated review | Importer auto-calls `bulkCertifyFields(...)` immediately after `bulkCreateFields(...)` even when `field.description` is empty → row enters with synthetic fallback definition (`"X from OAGIS undefined"` / `"<field> on <component>"`) at `status=certified` | gate-bypass; fabrication | high | high | deprecate / wrap |
| F2 | (a) BF | `contract.business_field` certification status semantics | ADR-1ce490 §Context, audit-calibrated 2026-05-16 | `certified` = evidenced, reviewed admission | 462 rows `certified` with templated placeholder defs and zero anchor evidence; 7,062 total with 4,141 lacking any anchor (T0+T1_only); 1,400 only OAGIS structural evidence; 779 G1-lexical failures (682 banned templates, 97 too-short) | state-inconsistency; placeholder/padding | high | high | adapt (two-axis state model) |
| F3 | (a) BF | T4 (CC-mapped) BF cohort | ADR-1ce490 §T4 canary | BFs steering canonical pipelines pass hard gates | 15 hard fails in the 316 already-bound cohort (G1=11, G3=4) — steering pipelines with incoherent semantics | state-inconsistency | high | high | adapt (P0/P1 cleanup) |
| F4 | (a) BF | D409 BF precision batch 1 (25 rows, 2026-05-17) | operator-supplied audit summary | Rules-stage admission ≈ AI panel admission | Rules-stage `25/25 ADMIT_READY`; AI panel only `2/25 (8%)` admissible; gap is systemic, not row-specific | gate-bypass; missing-evidence | high | high | gap (rules-only ≠ admission) |
| F5 | (a) BF | Name-splitter / field-code normalization (D409 batch) | operator-supplied audit summary | Preserve identity | 11/25 rows `REJECT_BAD_MODEL` from name-splitter corruption | other (name corruption) | high | med | adapt |
| F6 | (a) BF | Definition generator (D409 batch) | operator-supplied audit summary | Each row a domain-defensible sentence | Template-placeholder defs, rationale-style defs, shared boilerplate observed across the cohort | fabrication; placeholder/padding | high | high | adapt |
| F7 | (a) BF | `standard_ref` / `semantic_family` / `unit_type_code` provenance fields | operator-supplied audit summary; ADR-1ce490 §G3/G5; ADR-a17d0f §C5 | Populated per gate | `standard_ref` universally NULL; `semantic_family`/`unit_type_code` NULL on Quantity/Amount/UOM/date rows; per ADR-a17d0f all 603 CFs also `semantic_family=NULL` | missing-evidence; state-inconsistency | high | high | adapt |
| F8 | (a) BF | BF row `state` pair | operator-supplied audit summary | Lifecycle clear | All 25 rows carry `certified + candidate_import` simultaneously (two-axis state vacuously violated before D408 lands) | state-inconsistency | high | med | adapt |
| F9 | (a) BF | SAP `_hdr` suffix handling | operator-supplied audit summary | Source-system table suffix not leaking to platform identity | `_hdr` suffix leaking into BF identifiers | vocabulary-drift; alias-mismatch | med | med | adapt |
| F10 | (b) BO | `business_object` certification gate | ADR-a17d0f §C6 | "All BFs certified" check at BO approval also enforces CF cert | BO approval checks BF cert only; no enforcement of CF cert at cc_field_mapping create, MC bind, MC activate, CM/OC authoring | gate-bypass | high | high | adapt |
| F11 | (b) BO | BO catalog `naming_policy_violation` enforcement | ADR-1ce490 §2.1 | Names prefixed by `object_class_` or registered abbreviation | 2,688 currently-certified BFs use unregistered abbreviated prefixes; registry doesn't yet exist; rule presently advisory only | vocabulary-drift; gate-bypass | med | high | gap (registry) |
| F12 | (c) CF | `canonical_field` lifecycle | ADR-a17d0f §Context, §C4–C5 | Operational lifecycle | 603/603 CFs in `draft` (no other state ever used); 122 non-snake_case CFs accepted despite SOP mandate | state-inconsistency; gate-bypass | high | high | adapt |
| F13 | (c) CF | CF certification reference gate | ADR-a17d0f §C6 | CF cert checked at MC bind / activate / cc_field_mapping insert | No such check anywhere; `metric-readiness.service.ts::bind`, MC version activate, cc_field_mapping insert all accept `draft` CFs | gate-bypass | high | high | adapt |
| F14 | (c) CF | CF naming rule (P3 snake_case, NOT BO-scoped) | ADR-a17d0f §C4 | Service enforces | Service accepts 122 violations | gate-bypass | med | high | adapt |
| F15 | (c) CF | `semantic_family` closed-enum gate | ADR-a17d0f §C5 | DB CHECK + service path | Enum named only in code comment; no DB CHECK; no service path; all 603 CFs NULL | missing-evidence; state-inconsistency | high | high | gap |
| F16 | (c) CF | Meaning-once invariant on `cc_field_mapping` (Foundation I) | ADR-a17d0f §C5/§4 G10 | Write-time check rejects duplicate semantic signatures | No write-time check exists; audit found 144 R4 funnel-padding candidates and 172 normalized-form stem-clusters (403 CFs) | missing-evidence; padding/placeholder | high | high | gap |
| F17 | (d) BF↔CF mapping | `cc_field_mapping` SUM-vs-name semantic drift | feedback_d335_audit_insufficient_alone.md | Mapping is semantically sound | Canonical example: `total_customer_accounts` (CF) → `receivable_hdr_amount` (BF, currency) with rule `sum`; formula audit passes; result is varying-wrong instead of constant-wrong | alias-mismatch | high | high | adapt |
| F18 | (d) BF↔CF mapping | "Funnel padding" attempt SES-db0a03 | feedback_funnel_padding.md | Per-CF semantic source mapping | Proposal to repoint 81 differently-named CFs at one SAP NETWR column to unblock MCs; user-rejected; now graduated to MLS-14 semantic-class-collapse gate | padding/placeholder; alias-mismatch | high | high | keep-as-substrate (gate) |
| F19 | (d) BF↔CF mapping | `FieldMappingService.suggest()` / `CanonicalWizardService` | ADR-1ce490 §3 (Service-guard implication) | Suggest from certified/admitted BFs | Both services read catalog without state-awareness — contamination vector; uncertified rows surface as bindable in UI | scope-conflation; missing-evidence | high | high | adapt |
| F20 | (d) BF↔CF mapping | "Duplicate primary alias overwrite" in `assembleInputPayloads()` | session_d323_greenfield_oc_enrichment.md §Rejection breakdown | One alias resolves cleanly per variable | 30 of 80 MC rejections traced to alias overwrite bug (combined with missing CC data) | alias-mismatch | high | med | adapt |
| F21 | (d) BF↔CF mapping | OC `field_map` translates source→BF at CO creation | session_d323_greenfield_oc_enrichment.md | Necessary and sufficient for downstream resolution | Enrichment moved 15/93 MCs to producing; remainder blocked on missing CCs/readers + cc_field_mapping gaps + alias bug — i.e. OC map is necessary but not sufficient | scope-conflation | med | high | keep-as-substrate |
| F22 | (e) Catalog cert flow | `status_code='certified'` mutation as certification act | ADR-1ce490 §Decision; ADR-a17d0f §Decision | Cert is an evidenced ledger entry | Cert is treated as a status-flag mutation; no `certification_record` ledger row required; violates Foundation Invariant VI | missing-evidence; state-inconsistency | high | high | adapt |
| F23 | (e) Catalog cert flow | Five competing certification lifecycles | ADR-a17d0f §C1 | One lifecycle | Five different effective lifecycles across 4 governing sources and 3 service implementations (binary / single / three-state CHECK / DEC-5017fe four-state / DEC-d72560 single-state) | vocabulary-drift; state-inconsistency | high | high | adapt |
| F24 | (e) Catalog cert flow | Primitive naming (Business Field vs StandardField*) | ADR-a17d0f §C2 | One name | Docs say "Business Field"; bc-core controller uses `StandardField*` | vocabulary-drift | med | high | adapt |
| F25 | (e) Catalog cert flow | `chain_status` SSOT pre-activation | ADR-bebaec 2026-05-14 erratum | MLS-14 reads `chain_verdict='complete'` on activation | `ChainStatusService.getActiveMcVersions()` filters to active only → new MC pre-activation has NULL row → MLS-14 refuses for wrong reason | silent-drop; gate-bypass (false reject) | high | high | keep-as-substrate (patched) |
| F26 | (e) Catalog cert flow | `IntegrityService` (pre-D305) | ADR-bebaec §Bugs | One stable answer for chain completeness | 5 bugs documented: suffix-matching FP; first-OC-wins (`.slice(0,1)`); two-binding-sources first-wins; coverage-vs-chain inconsistency on Reader; computed BFs bypass mapping. Every session reported different numbers (100% vs 30% vs 86% vs 22/51) | silent-drop; alias-mismatch; scope-conflation | high | high | deprecate (kept as gates-only) |
| F27 | (e) Catalog cert flow | `MetricWizardService.completeMetric` | session_d340_definition_canonical.md §New discoveries | Wizard writes metric_contract via canonical onboarding | Wizard had been silently 500-ing for ~3 weeks (`tier_code` stale since Mar 25; `category_code` read but never SELECTed); also bypassed seed-promotion canonical path → quarantined | silent-drop; gate-bypass | high | high | deprecate |
| F28 | (e) Catalog cert flow | `metric_contract.metric_definition_id` FK | session_d340_definition_canonical.md | NOT NULL FK | 778 rows historically orphan (589 active + 189 archived); created by unidentified bulk script via `createMinimalMetricContract` | state-inconsistency | high | high | adapt (FK enforced) |
| F29 | (f) AI panels | bc-ai as advisory vs gate (D409 batch 1) | operator-supplied audit summary; ADR-a17d0f §5 | AI advisory only; deterministic gates block | Rules stage said admissible (25/25); AI panel disagreed (2/25); divergence shows rules-stage cannot stand alone as admission, AI verdict carries load that ADR-a17d0f says it should not | scope-conflation; gate-bypass | high | high | adapt |
| F30 | (f) AI panels | LLM auto-certification risk | ADR-b8ec00 §Context; §Core rule | Agents recommend only; humans certify | D408/D409 explicitly authored to prevent "LLM auto-certification that fabricates evidence and silently re-decides BF/BO meaning" — i.e. observed shape in prior attempts | fabrication | high | med | gap (Explorer/Skeptic/Moderator split) |
| F31 | (f) AI panels | Mega-onboarding / coverage-as-KPI pressure | ADR-b8ec00 §"The problem with mega-onboarding" | Coverage is output of evidence, not input | Historical: 462 placeholder admits + funnel padding all traced to coverage-as-success-metric | padding/placeholder | high | high | adapt |
| F32 | (f) AI panels | Cross-family bc-ai verification of MC body | feedback_runtime_readiness_gate.md §"Rejection observability"; SES-594568 findings | Operator can see why MC failed | No Inspector field surfaces latest rejection reason; no join from `metric_evaluation` to evidence envelope; persisted in `evidence_object` but not surfaced; earlier diagnosis queried wrong table (`evidence_record`) — internal forensics were wrong-for-a-day | missing-evidence; untrusted-helper | high | high | adapt |
| F33 | (f) AI panels | D335 formula↔rule audit | feedback_d335_audit_insufficient_alone.md | Catches metric correctness issues | Scope is formula↔rule only — does not catch CF→BF semantic mismatch (the binding layer); flipping SUM→COUNT can replace constant-wrong with varying-wrong | scope-conflation; missing-evidence | high | high | keep-as-substrate |
| F34 | (g) bc-seed | (no direct BCF-relevant bc-seed Mongo evidence in supplied sources) | — | — | None of the supplied feedback/session files name bc-seed Mongo behavior. Absence is not evidence — flag as inventory gap, not failure. | — | — | low | gap (need additional sources) |
| F35 | (g) bc-seed | Header `tags`-as-varcodes / formulaic descriptions in mc-onboarding | MEMORY.md SES-594568 entry | Header authoring fidelity | `mc-onboarding.service.ts:442-443` hardcodes header shape; Foundation-strict authoring requires slice-0 overrides; live lifecycle uses only `{draft,active,superseded}`; `KNOWN_CONSTANTS` TS map used as transitional non-SoT runtime; 1,216 non-deprecated seeds carry `draft` | vocabulary-drift; placeholder/padding | med | med | adapt |
| F36 | (h) Operator UI | bc-admin domain split (platform vs tenant) | feedback_platform_vocabulary.md | bc-admin platform-only | bc-admin had previously used tenant-runtime vocabulary (SO/CO/AO) and tenant-scoped endpoint design (incl. "Tenant identification required" 400s) before separation | scope-conflation; vocabulary-drift | med | high | adapt |
| F37 | (h) Operator UI | Catalog page "Object" overload | feedback_platform_vocabulary.md | "Source Table" terminology, distinct from runtime SO | `source_object` 254K-table catalog was conflated with execution-model SO; rename in flight | vocabulary-drift | low | high | adapt |
| F38 | (h) Operator UI | Multiple MC detail pages (pre-D340) | session_d340_definition_canonical.md | One canonical home per metric | Two detail surfaces existed (MetricContractDetailPage + definition page) — accident, not design | scope-conflation | med | high | deprecate (folded) |
| F39 | (h) Operator UI | bc-admin "Contracted" filter / orphan view | session_d340_definition_canonical.md §Outstanding follow-ups #5 | All visible MCs are FK-anchored to a definition | 589 contracts historically lived as orphans (no `metric_definition_id`); cause never traced | state-inconsistency | med | high | adapt |
| F40 | (h) Operator UI | SOPs / spine docs carrying counts | feedback_no_stats_in_sops.md | Process docs reference live queries | contract-chain-assembly.md said "0 BFs, 0 BOs" when reality was 171 BOs / 4,083 BFs — every session was reading stale state from the doc | other (stale doc) | med | high | adapt |
| F41 | (h) Operator UI | "Producing MC" pilot framing | feedback_runtime_readiness_gate.md §Sandbox1 classification | A single honest count of runtime-ready MCs | "14 runtime-ready" misleading: only 1 typed-table-backed, 12 JSONB-only, 1 ledger-orphan, 7 rejected source-data-blocked, 8 upstream-CC-blocked, 1 formula-blocked, 1 warn — must qualify by materialization tier | other (count framing); padding/placeholder | med | high | adapt |
| F42 | (i) Cross-cutting | Helper-script trust | feedback_runtime_readiness_gate.md §Helper-script trust; feedback_session_discipline_d268.md Rule 9 | Script output is verification | `evaluate-ready-mcs.mjs` hardcoded to wrong tenant + pre-DEC-f02230 schema + lacks `--mc`/`--limit`/`--tenant` flags despite being usable-looking. PLN-c028cd: 55 OCs / 1,022 field maps / 48 SCs / 43 ACs / 221 reader bindings bulk-generated to "make chains green" — none produced snapshots; ~9 hours wasted | untrusted-helper; gate-bypass; padding/placeholder | high | high | gap |
| F43 | (i) Cross-cutting | Funnel "fallback that bypassed chain_complete=0" | feedback_no_hacks_no_bypass.md | Strict cumulative subsetting | Code had fallback making 7 MCs appear "producing" while chain_complete=0 — logically impossible; user caught | gate-bypass; padding/placeholder | high | high | adapt |
| F44 | (i) Cross-cutting | Capability claims preceding proof | feedback_zero_claims_policy.md | Only claim what's been first-hand-proven E2E | Standing rule born from prior over-claims (SAP-S/4 claim explicitly named as risk); simulator-only proofs do not count | other (claim discipline) | high | high | keep |
| F45 | (i) Cross-cutting | Placeholder text in formulas/descriptions | feedback_no_placeholders.md | Empty/null when unknown | Generic placeholder values appeared as user-visible formula decomposition ("Numerator Value / Denominator Value × Percentage Multiplier") | placeholder/padding; fabrication | high | high | adapt |
| F46 | (i) Cross-cutting | Forensics-on-wrong-table episode | feedback_runtime_readiness_gate.md §Why | Inspector data discovery is reliable | 2026-04-29 forensics queried `evidence.evidence_record` (link table) instead of `evidence.evidence_object` (envelope) — diagnosis wrong-for-a-day; not a code bug, a discoverability failure | missing-evidence | med | high | adapt |
| F47 | (i) Cross-cutting | Alias enrichment as a chain-completeness lever | session_alias_enrichment_apr11.md | Enriching aliases moves chains forward | Worked (+104 full chains, -22% mapping_binding breaks) but only on subset where source columns were honestly named; chain_complete=0 elsewhere; demonstrates per-CF semantic discipline matters more than alias count | (success caveat) | low | med | keep |

---

## 3. Per-area notes

**(a) BF authoring & admission.** The dominant pattern is that "certified" was a status-flag mutation at import time, not an evidenced admission act. OAGIS onboarding silently auto-certified rows carrying synthetic fallback definitions; the calibrated D408 audit found 462–779 lexically failing rows and 4,141 rows with no anchor at all. The D409 25-row precision batch confirmed the failure is systemic, not residual: rules-stage and AI-panel verdicts diverged 25→2. Identity hygiene failures (name-splitter, `_hdr` leak) compound the definition-quality failures.

**(b) BO authoring & verification.** Only two findings, but both are structural: BO approval enforces BF certification but not CF certification (the asymmetric gate is the contamination path for the entire downstream chain), and 2,688 certified BFs use abbreviation prefixes for which no registered-abbreviation authority yet exists. The second is a "rule pending substrate" gap, not a code failure.

**(c) CF authoring & certification.** Strong, consistent evidence of catastrophic governance gaps: all 603 CFs in `draft`, all 603 with `semantic_family=NULL`, 122 non-snake_case admitted, no `semantic_family` DB CHECK, no Meaning-once write-time check, no reference-time cert check at any binding boundary. Every governance assertion in DEC-d72560 / DEC-69f09e / canonical-field-seeding is unenforced.

**(d) BF↔CF mapping.** The pathology is alias/semantic-mismatch combined with absent Meaning-once enforcement: `total_customer_accounts → receivable_hdr_amount` passed every audit; the 81-CF→NETWR funnel-padding episode would have shipped if not caught manually. The "duplicate primary alias overwrite" in `assembleInputPayloads()` plus 40 MCs with cc_field_mapping CF-gaps quantify the operational cost. OC field-map enrichment is necessary but never sufficient.

**(e) Catalog publication / certification flow.** Five lifecycles, two primitive names, status-flag-as-certification, IntegrityService 5-bug count, MetricWizardService silently 500-ing for three weeks, `chain_status` SSOT pre-activation NULL-row race, 778 historical metric_contract orphans with no traceable creator. The pattern is that no single component owns admission, so every component implements its own version.

**(f) AI panels & verification.** Two adjacent failures: D335 audit catches formula-rule mismatch but not the load-bearing BF↔CF semantic mismatch (scope-conflation that produces "varying-wrong" output); and AI verdicts have been functionally loaded as decision-makers in the rules-only D409 pipeline (8% admit vs 100% admit divergence). Rejection observability is also weak — envelopes persist but no surface reads them; forensics queried the wrong table for a day. Mega-onboarding / coverage-pressure is the named historical anti-pattern D409 was built to refuse.

**(g) bc-seed substrate.** Supplied sources contain little direct bc-seed Mongo evidence; the closest is SES-594568 on mc-onboarding header hardcoding and KNOWN_CONSTANTS being a non-SoT transitional map with 1,216 draft seeds. Flag as inventory gap — pull additional sources before drawing conclusions.

**(h) Operator UI.** Pattern: surfaces that mixed scopes (bc-admin platform vs tenant), surfaces that duplicated entities (MetricContractDetail + Definition pages), surfaces that lied about counts (SOPs with stale "0 BFs"), and surfaces that conflated heterogeneous states ("14 runtime-ready" hiding 7 distinct materialization tiers). Catalog "Object" overload is the smallest example, "pilot count" the most operationally costly.

**(i) Cross-cutting.** Two repeated patterns: helper scripts are routinely trusted as proof (PLN-c028cd burned 9 hours on this; `evaluate-ready-mcs.mjs` is a current ticking version), and "make it green" pressure produces gate-bypass code paths (chain_complete=0 fallback; bulk reader-binding generation; funnel-padding repoints). The zero-claims policy, no-placeholders rule, and D268 discipline ADR all exist as compensating controls because the underlying gates are absent or evadable.

---

## 4. Sessions / records index

| File / record | One-line takeaway |
|---|---|
| feedback_funnel_padding.md | 81-CFs-to-1-NETWR-sum proposed; rejected; now MLS-14 semantic-class-collapse gate. |
| feedback_no_placeholders.md | Generic placeholder text in user-visible fields destroys trust; empty/null preferred. |
| feedback_no_hacks_no_bypass.md | Chain-complete=0 + "producing" simultaneously surfaced a fallback bypassing the cumulative gate. |
| feedback_zero_claims_policy.md | Standing rule: no capability claim without first-hand E2E proof; simulator runs don't count. |
| feedback_session_discipline_d268.md | PLN-c028cd bulk-generated 55 OCs / 1,022 maps / 48 SCs / 43 ACs / 221 bindings; zero snapshots; 9h wasted. |
| feedback_d335_audit_insufficient_alone.md | Formula-rule audit can pass on a CF→BF mapping that is semantically wrong. |
| feedback_runtime_readiness_gate.md | Contract-gate eligibility ≠ runtime-ready; helper-script trust caveat; envelope discoverability gap. |
| feedback_platform_vocabulary.md | bc-admin must speak SC/AC/OC/CC/MC/IC, not SO/CO/AO; catalog "Object" → "Source Table". |
| feedback_no_stats_in_sops.md | contract-chain-assembly.md said "0 BFs, 0 BOs" while reality was 171 / 4,083. |
| canonical_field_hypothesis.md | DEC-d72560 lifecycle = single "draft" state; reference-time cert was always implicit. |
| chain_completeness_ssot_d305.md | IntegrityService had 5 bugs; sessions reported wildly different completeness numbers. |
| session_alias_enrichment_apr11.md | +101 SAP aliases moved 146→250 full-chain MCs; alias-as-lever works only with honest mappings. |
| session_d340_definition_canonical.md | 778 orphan metric_contracts backfilled; MetricWizardService silently 500-ing 3 weeks. |
| session_d323_greenfield_oc_enrichment.md | 15/93 MCs producing after OC field_map enrichment; alias-overwrite + cc_field_mapping gaps remain. |
| ADR-bebaec.md (D305) | Defines L1–L7 / C1–C5 / E1–E3; documents IntegrityService 5 bugs; 2026-05-14 pre-activation race erratum. |
| ADR-1ce490.md (D408) | Calibrated audit: 462 placeholder certs, 4,141 anchorless rows, 779 G1 fails, 15 T4 hard fails. |
| ADR-a17d0f.md (G11 / SDA) | Six conflicts C1–C6: 5 lifecycles, name disagreement, snake_case unenforced, semantic_family NULL, ref-time cert absent. |
| ADR-b8ec00.md (D409) | Multi-agent factory authored explicitly to refuse "mega onboarding" and LLM auto-certification. |
| D409 batch-1 audit summary (operator-supplied) | Rules 25/25 vs AI 2/25; 11 name-splitter corruptions; universal certified+candidate_import state pair. |

---

## 5. Open questions for Codex deep review

1. Who/what process originally created the 589 orphan `metric_contract` rows via `createMinimalMetricContract` without a definition_id? (session_d340 §5 — never traced.)
2. Is the "duplicate primary alias overwrite" bug in `assembleInputPayloads()` (session_d323) still present, and does it interact with the D305 L4 trace?
3. Does any current bc-admin authoring surface (`FieldMappingService.suggest()`, `CanonicalWizardService`) actually filter by `catalog_state_code` yet, or is contamination still live? ADR-1ce490 §3 names this as a required service-side guard "before client-side filtering."
4. Confirm whether the rules-stage admission code path in the D409 batch can actually be reconciled with ADR-a17d0f's deterministic-gates-block + AI-advisory-only design, or whether the divergence indicates the rules stage is implementing a different (looser) gate set.
5. What is the current state of bc-seed Mongo with respect to BCF inventory artifacts? (Supplied sources are thin — request more.)
6. Is the `evaluate-ready-mcs.mjs` helper still in tree with hardcoded `tbc_selenite_dev` / `boundary.canonical_object`? If so, what other helpers in `bc-core/scripts/` share that profile?
7. For the 7 SAP `_hdr`-suffix-leak rows in the D409 batch, did the suffix originate in the source catalog (`source_object` register) or in the BF naming generator?
8. Does the `chain_status` pre-activation erratum (slice 0.8) cover all activation paths, or only `ContractService.transitionState`? Are there alternative activation entry points (e.g. seed promote, wizard) still subject to the NULL-row race?
9. How does `MetricWizardService.completeMetric` quarantine interact with any bc-admin surfaces that previously called it? Are there UI dead ends?
10. "11/25 REJECT_BAD_MODEL from name-splitter corruption" — is this an upstream generator failure, a parser failure inside the AI panel, or a normalization-step failure? Locating the failure layer determines repair location (A vs B vs D).

---

## 6. Inventory verdict shifts to consider (flags, not decisions)

| Artifact | Current likely classification | Suggested re-examination |
|---|---|---|
| `oagis-onboarding.service.ts` auto-certify path | substrate | candidate **deprecate / wrap** — admission rule is explicitly violated (F1) |
| `contract.business_field` table | substrate (catalog) | **adapt** — needs two-axis state + ledger before reuse claim holds (F2/F8/F22) |
| `IntegrityService` | substrate | already **deprecate**-with-narrow-use; verify no new callers added (F26) |
| `MetricWizardService.completeMetric` | service | **deprecate** — already quarantined; finish removal (F27) |
| `FieldMappingService.suggest()` / `CanonicalWizardService` | substrate (authoring) | **adapt** — server-side state-aware filter required before any reuse (F19) |
| `assembleInputPayloads()` alias resolution | substrate (runtime) | **adapt** — duplicate-primary bug needs fix before reuse (F20) |
| D335 formula-audit | substrate | **keep-as-substrate** — necessary but explicitly insufficient; pair with semantic check (F33) |
| `chain_status` SSOT / ChainStatusService | substrate | **keep** — D305 pattern sound; pre-activation race patched in erratum (F25/F26) |
| Rules-stage D409 pipeline (pre-AI) | service | **adapt or gap** — divergence with AI panel says rules-only ≠ admission (F4/F29) |
| AI panel role split (Explorer/Skeptic/Moderator) | new substrate | **keep** — explicitly authored to refuse the failure mode evidenced in F30/F31 |
| Helper scripts in `bc-core/scripts/` (evaluate-ready-mcs, etc.) | tooling | **gap** — need provenance audit; treat all as untrusted by default (F42) |
| SOPs / spine docs carrying live counts | doc-substrate | **adapt** — strip stats, link to queries (F40) |
| Pilot/funnel count surfaces | UI | **adapt** — must qualify by materialization tier (F41) |
| bc-seed substrate (BCF parts) | unknown | **gap** — re-inventory after additional sources read (F34/F35) |
| `business_object` cert gate (BF-only) | service | **adapt** — extend to CF cert check (F10) |
| `metric.metric_contract.metric_definition_id` FK | substrate | **keep** — already enforced post-D340; backfill source still unknown (F28/F39) |
| `MetricContractDetailPage` (bc-admin) | UI | already **deprecate** — folded into definition page tabs (F38) |

---

## 7. Limitations of this pass

- **bc-seed Mongo** is under-evidenced; one finding only (F34/F35). Additional source-pull required.
- **Code re-verification not performed.** Findings are sourced from prior session notes, ADRs, and the operator-supplied audit summary. Whether a referenced bug is still live in the current commit head is not re-tested here. Open questions in §5 carry the re-verification load.
- **Cross-family AI verification of MC body** (F32) is observed indirectly via rejection-observability evidence; the actual cross-family panel behavior on BCF-scope artifacts has not been directly sampled.
- **No quantification of false positives.** The 47 findings include some single-source items (F20, F47) marked at low/medium confidence; they should not drive verdict shifts on their own.
- **No verdict decided.** §5 and §6 are flag-lists for operator review against the BCF inventory; this document does not modify the inventory.
