---
uid: DEC-b5c7ff
title: "Metric Directory — realized value-organizing subsystem (bc-core)"
description: "Realize the Metric Directory (value-organizing metric dictionary) as a bc-core schema; intent-owned + derive-realized; keystone proven."
status: decided
date: 2026-07-08T05:26:47.520Z
project: bc-core
domain: metrics
subdomain: metrics/directory
focus: schema
supersedes: DEC-f90ba3
---

# Metric Directory — realized value-organizing subsystem (bc-core)

## Context

Metric onboarding capability was scattered across two repos (files, libs, a drifting devhub store, a cookbook), and each session patched a different part — the true source of session drift. The fix is a single governed dictionary that homes the missing "select" (value) layer and unifies coverage, modelled on BCF which succeeded by being a clean governed registry. Red-team review established the hard constraints now encoded here: it must live in bc-core (D501), must derive realized state rather than duplicate it (or it becomes onboarding_candidate v2 — D505), and must stamp the Member→MC link at authoring (the keystone, since 0/112 active MCs traced to any origin under the old reconcile-by-inference). Keystone-first proved the riskiest unknown before any schema. Seed labels were verified too noisy to bootstrap the taxonomy, so the value spine is operator-curated with APQC as a hint — keeping value judgment with the operator and mechanics with the engine.

## Decision

Realize the **Metric Directory** — the conceptual dictionary in `bc-docs/docs/operating-model/metric-directory.md` (draft-authoritative) — as a governed bc-core subsystem. The directory is the value-organizing peer of BCF: `Function → Subfunction → Family(theme) → Group → Member`, strict single-parent tree; it answers "what metrics should exist, organized by value" and feeds MMS Creation-Track Stage 1. This ADR fixes the IMPLEMENTATION decisions; the conceptual model is locked in the chapter and not restated here.

**D1 — Home.** New `metric_directory` schema in the bc-core platform DB, services-only (no raw INSERT). Consistent with D501 (metric-authoring domain = bc-core; devhub is a thin read console).

**D2 — State model: own-intent, derive-realization.** A Member owns ONLY its intent state (`planned` | `blocked` + reason) and its spec. Realized state (`draft`/`chain_ready`/`published`), `depends_on`, and coverage are VIEWS over `mcf.metric_contract(_version)` — never cached columns or counters (DB Rules #2/#4). This is the anti-drift discipline that killed the 3-way drift of `onboarding_candidate` (D505).

**D3 — Keystone (DONE, commit 7b8e696).** The Member→MC realization link is an EXPLICIT emitted reference: `directory_member_uid` stamped into `metric_contract.candidate_source_ref_json` at materialization (zero schema — `mc_candidate_source_type_chk` only constrains `source_type`). Realized state derives by `candidate_source_ref_json->>'directory_member_uid'` join, NOT by the reconcile-by-inference that gave 0/112. Proven: 2 unit tests + 112/112 live MCs already round-trip the JSONB.

**D4 — Taxonomy spine.** Operator-curated. APQC PCF (`metric_authoring_intake_queue.apqc_subset_classification_text`) is a hint; scraped seed `function_code`/`subfunction_code` labels are NOT auto-trusted (verified poisoned: `general_ledger` bucket held ROE/ESG/audit metrics; `iso_55001` was asset-mgmt mislabeled as finance).

**D5 — Build fresh; retire onboarding_candidate at Phase 5.** No import from the seed-primary devhub `onboarding_candidate` store; the directory is stood up clean and that store + onboarding-sync are retired once the directory is proven. This ADR supersedes DEC-f90ba3 (the onboarding_candidate orchestration schema) in design authority; the physical store lingers only through the migration window.

**D6 — Naming.** Keep the Family/Group conceptual names; disambiguate in code by (a) namespacing all tables under the `metric_directory` schema and (b) renaming the generator's `family-spec` → `group-spec` (it maps to a directory Group, not a Family). The only residual is a harmless word-overlap with `master.semantic_family` (different schema, different meaning).

**D7 — depends_on is a view.** Derived from the Group's `template.inputs` (declared once in the derivation template), never a second hand-kept dependency table.

**D8 — Reconcile retired taxonomy ADRs.** ADR-7bbdba (Industry→Function→Subfunction), ADR-37967b (APQC PCF alignment), ADR-9dce29 (5-D classification) — retired/never-validated prior art; their intent is folded into this ADR + the chapter, superseded-in-spirit.

**Schema sketch (Phase 3; DB Protocol approval required before DDL):**
`metric_directory.function`(function_code,label); `.subfunction`(→function,subfunction_code,label); `.family`(→subfunction,theme_code,decision,rationale,priority,applicable_industries text[] — empty=global); `.group`(→family,class_code base|derived,grain_entity_id,temporal_anchor_concept_id,template_json — discriminated aggregation|derivation); `.member`(member_uid MDM-*,→group,measure_concept_id,representation_code,discriminator_json,class_code,intent_state_code,blocker_code/_reason,applicable_industries_override) — NO realized-state column. Realized state / depends_on / coverage = views.

**Foundation gate:** repair-location F (read-model/diagnostics over the authoring domain) with a touch of C (intent binding); pre-authoring, outside the runtime A–F boundaries. The one real invariant risk — becoming a shadow semantic authority — is mitigated by D2 (derive, never restate) and D3 (reference the MC, never infer). Invariants IV+VI satisfied by the explicit emitted link.

**Phasing:** 1 = this ADR. 2 = keystone (DONE). 3 = `metric_directory` schema (intent-owned fields only; DB Protocol). 4 = derive-realization views (no cached counters). 5 = retire onboarding_candidate + onboarding-sync; rename generator family-spec→group-spec.
