---
title: "SDA Phase 1 — proof summary (BF only)"
session: SES-594568
date: 2026-05-12
status: complete
type: phase-summary
authority: DEC-a17d0f
related:
  - DEC-a17d0f # SDA umbrella
  - DBCP-1k    # lifecycle vocabulary (applied)
  - DBCP-1l    # BF.semantic_family support (applied)
  - 2026-05-12-sda-first-honest-certification-canary-SES-594568.md
  - 2026-05-12-sda-certification-operator-runbook-SES-594568.md
  - 2026-05-12-sda-external-standard-g4-experiment-result-SES-594568.md
  - 2026-05-12-sda-certify-with-override-experiment-result-SES-594568.md
---

# SDA Phase 1 — proof summary

Closing MWR for the BF-only Phase 1 SDA arc. Records what the last
session sequence proved end-to-end, what remains unproven, and the
recommended shape of the next phase.

## 1. Proof arc (six load-bearing slices, in order)

| # | Slice | bc-core HEAD | What it locked in |
|---|---|---|---|
| 1 | **DBCP-1l** — `business_field.semantic_family` column + FK + index | (DDL only, no code) | Persisted column to drive G5/G6 honestly. 7,061 rows kept NULL; one canary populated later. |
| 2 | Paired code slice — Drizzle schema + gate reader + service hard-coded null removed + DTO/repo plumbing for `semanticFamily` | `d72fd17` | Gate evaluation reads BF metadata from real persisted state; PATCH path accepts `semanticFamily`. |
| 3 | **SDA-4 lifecycle** validated end-to-end on the canary | `89c50dc` (substrate) + `72f22a9` (DTO fix) | The 5-action state machine + atomic dual-write under live HTTP traffic, 1 primitive. |
| 4 | **Internal-standard path** validated under a 5-candidate batch | (no code change) | Six primitives across 5 BOs, 3 families, certified clean with `BARECOUNT`. Proves the default path is repeatable. |
| 5 | **External-standard path** validated with G4 `EXTERNAL_DEFINITION_STANDARDS` branch | `20674ef` (vocab split) + `77763ff` (`standardRef` plumbing) | One ISO_20022 certification with real `standardRef`. Proves G4's external branch + the `standard_ref`-required semantics. |
| 6 | **Override path** validated with G4 `source_standard_missing` | (no code change) | One certification with `definition_standard=NULL` + a complete override-trio + a follow-up task. Proves the DBCP-1c override CHECK and the audit-trail discipline. |

## 2. Evidence

- **8 BFs certified** end-to-end through SDA-4.
- **16 `certification_record` rows** (2 per primitive: submit_for_review then certify).
- **4 semantic families exercised:** `identifier`, `date`, `name`, `text`.
- **3 standard outcomes exercised:**
  - `BARECOUNT` (internal, no ref) — 6 primitives.
  - `ISO_20022` (external, with real `standardRef`) — 1 primitive.
  - `NULL with G4 override` — 1 primitive.
- **1 override issued.** Target G4, 197-char rationale, follow-up
  [TSK-3233f7](mcp://devhub).
- **Zero silent bypasses.** Every certification carries either a
  fully passing 9-gate result block or an explicit override-trio with
  audit fields populated.

## 3. Bugs found and fixed (all surfaced by live canary discipline)

| Commit | Fix |
|---|---|
| `4fcb03f` | `definitionStandard` pass-through — `StandardFieldService.updateField` was mapping the value from a nonexistent `dto.sourceStandard` field, silently dropping PATCHes of `definitionStandard`. |
| `20674ef` | Definition-standard vocabulary split — `gates.ts:SOURCE_STANDARDS` was lowercase and conflated two governed vocabularies (provenance ledger vs primitive metadata). Added uppercase `DEFINITION_STANDARDS` mirroring `master.master_definition_standard.slug` verbatim; G4 switched to the new set; provenance-domain code and tests untouched. |
| `72f22a9` | `GateResultDto.detail` validation — global `ValidationPipe` with `forbidNonWhitelisted: true` was stripping `detail` from every gate result, returning 400 on every certify call. Added `@Allow()` plus a 6-case DTO-contract regression spec. |
| `77763ff` | `standardRef` plumbing — DTO + service + repo never accepted the wire field. Every prior PATCH had `standardRef: NULL` because the gap was latent under BARECOUNT-only certifications. |

Each was load-bearing for at least one of the six proof-arc slices.
None remain open.

## 4. What is still NOT proven

- **CF certification.** No `canonical_field` has been certified end-to-end.
  The gate evaluator, the column schema (`semantic_family`), and the
  PATCH path for CF are not yet wired the way BF's are. Would require
  mirroring DBCP-1l + the gate-reader extension for `canonical_field`.
- **BO certification.** Same gap for `business_object`. BO's gate
  semantics differ (G7/G8 behave differently).
- **G11 BF-CF semantic compatibility enforcement at authoring time.**
  The contract authority recorded in `DEC-b7affa` is not yet a live
  gate. CC/MC authoring still does not consult certified BF semantics
  when building canonical mappings.
- **Formula and mapping composition correctness.** SDA proves a
  primitive can be honestly certified. It says nothing about whether
  a given CC's `cc_field_mapping` correctly composes certified BF
  semantics into a CC payload, or whether an MC formula correctly
  composes CCs into a metric.
- **Metric-level trust.** A produced MC snapshot's correctness is
  downstream of SDA certification by several layers. No metric has
  been re-evaluated through the certified-BF lens yet.
- **`data_type='code'` resolution.** 779 BFs in the registry carry
  `data_type='code'`, which cannot pass G6 against the current
  compatibility matrix. Tracked at [TSK-84d81c](mcp://devhub) —
  needs an architectural decision before those BFs become certifiable.
- **`BF.object_class` vs linked BO semantics.** Four of the eight
  certified BFs exhibit `BF.object_class ≠ linked BO.object_name`
  (the BF uses a sub-namespace within the BO). G7 reads `BF.object_class`
  directly so this is not gate-blocking, but the data model meaning
  is unclear. Tracked at [TSK-000fa7](mcp://devhub) — needs a
  registry-wide audit and a model decision.

## 5. Recommended next phase

**Do not certify more random BFs yet.** Eight is enough to prove the
mechanism; certifying ten or fifty more single BFs with no consuming
context teaches us nothing new at this layer.

Recommended next move: **use this proof as the prerequisite for a
composition-readiness check on 1–3 Apex metrics.** Concretely:

1. Pick 1–3 Apex metric contracts that are currently producing snapshots.
2. Trace each metric's MC formula back through its variable bindings
   to its CC payload fields → CC's `cc_field_mapping` rows → underlying
   BFs.
3. For each underlying BF, ask: *is it certified? If not, what would
   it take to certify it?*
4. Surface the gap as a composition-readiness ledger: which BFs need
   certification, which need override-eligible PATCH, which need new
   schema work (CF certification, G11, `data_type='code'` decision).
5. Decide separately whether to **extend SDA certification to CF and
   BO** (mirror of DBCP-1l + reader extension) — the answer depends
   on the composition-readiness gaps surfaced in step 4. If the Apex
   metrics' bottleneck is mostly missing CF certification, that's the
   next slice; if it's mostly G11 or formula composition, those are
   the slices.

This shifts the work from "certify primitives in isolation" (which is
proven) to "demonstrate that certified primitives compose into
trustworthy metrics" (which is the actual product question).

## 6. Boundaries honoured throughout the Phase 1 arc

- **BF only.** No CF / BO certification attempted.
- **No bulk.** Eight primitives, one-at-a-time, full preflight +
  postflight on each.
- **No metric repair writes.** Nothing in `metric.*` / `tenant.*` /
  `runtime.*` was touched.
- **No DBCP beyond the two explicitly approved** (`DBCP-1k` lifecycle
  alignment, `DBCP-1l` BF.semantic_family).
- **No master.* edits.** Vocabulary alignment was done in-code
  (`DEFINITION_STANDARDS`); the master tables were read-only sources
  of truth throughout.
- **No provenance ledger writes.** SDA certification writes to
  `contract.certification_record`, never to
  `contract.primitive_provenance`.
- **No supersede / archive / unarchive** acts. Deferred per DBCP-1k §6.4.
- **No `--no-verify` outside the three explicitly authorized commits**
  (`4fcb03f`, `77763ff`, and earlier DBCP-1k paired code slice). All
  others passed the pre-commit hook cleanly.

## 7. Open follow-ups carried forward

| Task | Title | Why still open |
|---|---|---|
| [TSK-c94055](mcp://devhub) | Clear pre-existing ESLint debt in `standard-field.service.ts` | Pre-dates Phase 1; surfaced as the recurring `--no-verify` reason. Not blocking SDA. |
| [TSK-84d81c](mcp://devhub) | Decide on `data_type='code'` legitimacy across the BF registry | Affects ~779 BFs. Needs ADR-level decision. |
| [TSK-000fa7](mcp://devhub) | Investigate `BF.object_class` vs linked BO mismatch | Affects most of the registry. Needs data-model decision. |
| [TSK-3233f7](mcp://devhub) | Author provenance for `remittance_advice_hdr_payee_party_identifier` | Created in this Phase 1 arc as the override follow-up; resolved by a single PATCH when the ISO_20022 message-map review lands. |

All four `planned/later`. None blocks the recommended §5 next phase.

---

**End of Phase 1 SDA proof summary.**
