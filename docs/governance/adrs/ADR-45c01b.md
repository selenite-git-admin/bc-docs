---
uid: DEC-45c01b
title: "BCF characteristic admission — reduce ceremony: panel M5/M6/M9 calibration (v1.1) + fast-lane APPROVE to draft"
description: ""
status: decided
date: 2026-06-25
project: bc-core
domain: contracts
decision_code: D454
subdomain: semantic-vocabulary
focus: governance
---

# BCF characteristic admission — reduce ceremony: panel M5/M6/M9 calibration (v1.1) + fast-lane APPROVE to draft

> **Provenance.** Re-materialized on 2026-08-22 (SES-c2bd78) from the DevHub decision registry (`decision_text`, row created 2026-06-25); the ADR file had never been written to bc-docs (registry `file_path` pointed at the pre-D373 `docs/adrs/` location). Content below is the registry text verbatim. Frontmatter per D373/D334.

## Decision

Two coordinated changes reduce ceremonial friction in BCF characteristic (vocabulary) admission without weakening Foundation guarantees.

(1) Panel prompt calibration — registry-authoring/v1.1 (bc-ai). The Maker/Checker/Moderator prompts are recalibrated so the surface-pattern admission checks discriminate by meaning, not lexical shape. M5 (No-Synonym) flags only a TRUE same-value-property duplicate, not a shared suffix/prefix — the substrate legitimately governs many same-pattern terms (country code, currency code, industry code, document type code, account type code). M9 (source-field copy) flags only a verbatim/near-verbatim lift (re-cased or hyphen-swapped), not a substantive reframing that differs by >=1 meaning-bearing token AND cites >=1 system/standard beyond the originating field. M6 (bare representation term) is enforced mechanically upstream by the term-grammar floor and is no longer re-raised as panel judgment. Mechanical floors (M3/M4/M6/M7), bounded-evidence (M1/M2 verbatim citation), and the DEC-ec341c admission_scope axis are unchanged. The calibration is applied symmetrically to all three agents (Maker can pre-null, Checker can block, Moderator can downgrade). Prompt version bumped v1.0 -> v1.1; checklist_version token unchanged (M1-M10 definitions unchanged).

(2) Fast-lane APPROVE to draft (bc-core). On a clean panel APPROVE_FOR_DRAFT, createCharacteristic (registry_author_vocabulary) now auto-confirms the admission cert under the operator-authorized batch policy and writes the characteristic at lifecycle_state='draft' — parity with the existing low-risk createEntity/createBusinessConcept auto-author paths. The per-row operator-confirm step is removed; the panel M1-M10 checklist already gated the APPROVE. Activation (draft -> active, the DEC-26b6e2 immutable-atom freeze) is NOT auto-run — it remains the operator-gated publication step. Every other high-risk op (supersedeBusinessConcept) still requires an explicit operator confirm; the fast-lane is scoped to the vocabulary-admission action only.

## Rationale

The Pass-1 C1 enrichment drive showed an ~80% panel park rate (2026-06-24: 66 park / 16 approve) driven by surface-pattern M5/M6/M9 false-positives plus a redundant operator-confirm gate, at high panel cost and operator time. A grounded study (Foundation invariants, Vocabulary Evidence Framework, the bc-ai panel code, bc-core orchestrator/validator, DB panel records) confirmed: (a) these rules are characteristic-only — entity and BC admission already run lean; (b) the ceremony, not the Foundation invariants, was the cost driver. Foundation-clean on both changes: draft is not the commitment — DEC-26b6e2 freezes (term, definition) at activation, which stays governed; the admission cert is still emitted (auto-issued under a named batch policy, Invariant VI); admission rigor (bounded evidence, mechanical floors, scope axis, no-synonym for genuine synonyms) is preserved. Amends the C5 high-risk operator-confirm extension design (business-context-framework-c5-high-risk-operator-confirm-extension-design.md) for the vocabulary-admission action only. Verification: v1.1 live-probed on bc-ai (4 historical RP3 parks re-run — 2 clean park->APPROVE flips, 2 retained parks on substantive grounds, 0 ceremonial parks, 0 false-approvals, all stamped registry-authoring/v1.1); bc-core 311 registry-authoring-panel tests green (orchestrator 51/51, incl. new fast-lane + supersede-still-awaits coverage).
