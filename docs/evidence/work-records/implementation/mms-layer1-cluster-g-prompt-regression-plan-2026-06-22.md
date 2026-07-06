---
title: "MMS Layer 1 — Cluster G — bc-ai Prompt Terminology Rename — Regression Plan"
description: "Planning + fixture-inventory document for Cluster G of MMS Layer 1: renaming legacy workflow codes inside bc-ai's 3 registry-authoring prompt files (Maker / Checker / Moderator) under a gated regression discipline. Inventories the prompt surface, audits fixture availability, defines the fresh-fixture construction procedure (necessary because bc-core's ai_telemetry stores hashes only), proposes the regression acceptance gates, and lists what's NOT in scope. No prompt edits, no model calls, no DB writes performed by this document."
date: 2026-06-22
project: bc-docs
domain: governance
subdomain: terminology
focus: cluster-g-prompt-regression-plan
authority: reference
scope_locks: planning-only; no prompt edits; no model calls; no bc-ai code edits; no DB writes; no runtime change; no PR
parent_adr: ../adrs/ADR-54f221.md
predecessor_inventory: ./mms-layer1-interpretation-surfaces-inventory-2026-06-22.md
predecessor_plan: ./mms-layer1-track2-comments-tests-plan-2026-06-22.md
parent_doctrine: ../operating-model/metric-management-system.md
---

# MMS Layer 1 — Cluster G — bc-ai Prompt Terminology Rename — Regression Plan

> Planning document only. **No prompt edits, no model calls, no bc-ai code edits (read-only inspection used to produce this plan), no DB reads/writes against bc-core, no runtime/service restart, no PR.** This plan determines whether Cluster G is ready to open the prompt-rewrite work; the verdict (§9) is one of the operator-decision outputs.

## 1. Why Cluster G is gated

Layer 1 surfaces fall into two execution regimes under DEC-54f221:

| Regime | Surfaces | Risk profile |
|---|---|---|
| Mechanical rewrite (Track 1 + Track 2) | Operator-visible UI, runbook prose, source comments / JSDoc, test descriptions, spec filenames | Renaming text changes what humans read. Substitution is mechanical; verification is `tsc` + `vitest` + grep. Track 1 + Track 2 closed 2026-06-22 with zero TS errors introduced and zero vitest failures introduced across ~821 replacements. |
| **Model-input rewrite (Cluster G)** | **3 bc-ai system prompts** the registry-authoring panel reads at every invocation | Renaming text changes what the **model** reads. Substitution looks mechanical but the model's interpretation may shift in non-mechanical ways. Verification cannot be `tsc` + grep alone; it requires a **before/after panel output comparison** on representative candidates with the rename applied. |

This document plans the regression discipline. It does not authorize any prompt edit.

## 2. Cluster G surface — verified 2026-06-22

bc-ai prompt directory totals: **47 prompt files** under `app/prompts/` and `app/housekeeping/prompts/` (single-format `.md` files; no `.j2` / `.jinja` / `.yaml` prompt templates).

**Files containing legacy workflow codes — exactly 3, all in the registry-authoring v1.0 family:**

| File | Occurrences | Roles |
|---|---:|---|
| `bc-ai/app/prompts/registry-authoring/v1.0/maker.md` | 18 | system prompt for the Maker agent |
| `bc-ai/app/prompts/registry-authoring/v1.0/moderator.md` | 8 | system prompt for the Moderator / Judge agent |
| `bc-ai/app/prompts/registry-authoring/v1.0/checker.md` | 3 | system prompt for the Checker agent |
| **Total** | **29** | |

**Files clean of legacy workflow codes — 44** (bf-dedup, bf-pii-classify, bo-dedup, bo-suggest, cc-field-audit, chain-audit, eval-advise, field-map, kpi-ask, metric-trace, metric-verify, process-audit, source-verify, table-verify, plus 7 housekeeping reasoner prompts). No Cluster G work needed.

**False-positive prompts noted in the Layer 1 inventory §10.3 (NOT in scope for rename):**

- `app/prompts/kpi-ask/v1.0/composer.md` — line 31 cites `C1` only as a literal example of "raw variable codes like I1, I2, C1, O1" (a documentation example of variable-naming convention). Not a workflow code reference.
- `app/housekeeping/prompts/mkdocs-maintainer/v1.0/reasoner.md` — lines 6–7 cite `F01–F06`, `P01–P10`, `C01–C02` as documentation-site navigation section codes. Not workflow codes.

Confirmed by 2026-06-22 grep with the narrower regex `\bM(1[0-9]|[2-9])\b|\bM12\.5\b|PE-MC-[0-9]+|\bB6\b|\bC5\b|\bF3\b|L-V1` — these false positives do not match. Confirms the Layer 1 inventory is still accurate.

## 3. Legacy-code inventory — per-prompt detail

### 3.1 maker.md (18 occurrences)

| Lines | Code | Context |
|---|---|---|
| 4 | `BCF B6` | Panel identity assertion — "You are the Maker on the BareCount Business Concept Registry Authoring Panel (BCF B6, DEC-02f5a9)." |
| 12 | `F3` | Heading — "## F3 operation discriminator (read once, apply always)" |
| 14, 21, 22, 137, 161, 162, 287 | `F3` | "F3 service method name" / "rejected by F3" / "refused by F3" — multiple Maker constraints citing the F3 dispatch boundary |
| 202 | `M1-M10` | Heading — "#### Vocabulary Admission Checklist v1 — answer every MUST (M1-M10)" |
| 208–217 | `M1`, `M2`, …, `M10` | The 10 checklist items themselves — each on its own line: `**M1** Bounded evidence is present…`, `**M2** The candidate evidence is cited verbatim…`, etc. through M10. |
| 295 | `M1-M10` | Output-shape clause — "the `checklist_answers` object (M1-M10, each `{ "answer": "...", "basis": "..." }`)" |

**Critical sub-finding (preserved from Layer 1 inventory §10.4): M1–M10 may function as positional anchors.** The Maker prompt enumerates 10 checklist items as M1 through M10 in order. The ordinal sequence may be a learned positional signal for the model — it's not just a label, it's the structure that organizes the verification ritual. Renaming the ordinal suffix (e.g. `M1` → `M01`) preserves the positional signal; renaming to per-criterion semantic names ("Bounded Evidence Check", "Citation Verbatim Check", etc.) loses the ordinal signal and is a higher-risk transformation.

### 3.2 moderator.md (8 occurrences)

| Lines | Code | Context |
|---|---|---|
| 4 | `BCF B6` | Panel identity assertion |
| 5 | `B6` | "closed B6 verdict and payload" |
| 14, 52 | `M1-M10` | Vocabulary Admission Checklist references |
| 33 | `F3` | "f3_operation MUST be the F3 service method name" |
| 39, 40 | `F3` | Service-method dispatch context |
| 154, 155 | `M1`, `M10` | JSON example showing checklist_answers shape (`"M1": { … }`, `"M10": { … }`) |
| 160 | `M1-M10` | "Every M1-M10 item must be present in checklist_answers" |

### 3.3 checker.md (3 occurrences)

| Lines | Code | Context |
|---|---|---|
| 4 | `BCF B6` | Panel identity assertion |
| 29 | `M1-M10` | "independently attack the Vocabulary Admission Checklist (M1-M10)" |
| 33 | `M9`, `M8` | Adversarial-attack examples — "Is the term a copied source field, not an authored business term (M9)? Is the definition circular (M8)?" |

### 3.4 Code-family summary across the 3 prompts

| Family | Count | Operator-mapped semantic name (per Layer 1 inventory §4) |
|---|---:|---|
| `BCF B6` / `B6` (panel identity) | 5 | "Business Concept Draft Review" panel |
| `F3` (governed-vocabulary write dispatch) | 9 | "Registry Write" / "Registry Transition" service method |
| `M1` – `M10` individually (checklist items) | ~15 | **Operator decision required.** Layer 1 inventory §10.7 recommended preserving the ordinal suffix: `M1` → `VOCAB-CHECK-01` etc. — see §6.2 below. |
| `M1-M10` shorthand (the checklist family) | 5 | "Vocabulary Admission Checklist" (already in prose alongside `M1-M10` shorthand in the existing prompts; effectively a rename of the legacy-code alias, not the family) |

Decision identifiers (`DEC-02f5a9`) in the prompts are preserved verbatim per all prior Track 1/2 batches — never renamed.

`f3_operation` (snake_case field name, lowercase) is a code identifier (Layer 2 territory) — preserved verbatim. The renaming target is the standalone uppercase `F3` workflow-code references only.

## 4. Fixture availability — critical finding

The Layer 1 inventory §10.5 stated: *"bc-ai does not retain fixture copies. All panel evidence lives in bc-core's ledger post-execution."* This planning pass found a deeper limitation:

**bc-core's ai_telemetry tables store SHA-256 hashes only — not raw prompts or raw responses.**

Sources for this finding (read-only inspection of bc-core + bc-ai code):

- `bc-core/src/database/schema/ai-telemetry/ai-call-ledger.ts` header: "Six sha256 content-hash columns: prompt_system_hash, prompt_user_hash (always required), prompt_content_sha256, schema_hash, context_hash, response_hash (optional). **Raw prompts and raw responses are NEVER stored here; they live in caller-owned gitignored artefacts addressed by artifact_uri (held packet §7).**"
- `bc-ai/app/pipeline/bcf_telemetry.py:510–513` redaction list explicitly strips `raw_prompt`, `raw_response`, `raw_prompts`, `raw_responses` before sending to bc-core.
- `bc-ai/app/pipeline/bcf_telemetry.py:394` shows `artifact_uri=None` — bc-ai is not currently populating the artifact_uri pointer, so no caller-owned artifact store is being written.

What IS persisted, by location:

| Store | What it holds | Useful for replay? |
|---|---|---|
| `bc-core ai_telemetry.ai_run_ledger` | One row per panel run: `run_kind`, `run_scope`, `objective` (≤500 chars), `started_at`, `ended_at`, `status`, `tenant_id`, `subject_kind_code`, `subject_uid`, cost aggregates | **No** — metadata only, no inputs/outputs |
| `bc-core ai_telemetry.ai_call_ledger` | One row per LLM call within a run: `provider`, `model`, `role`, `prompt_system_hash`, `prompt_user_hash`, `context_hash`, `response_hash`, `tokens`, `cost_usd`, `cache_status`, `error_code` | **No** — hashes only, no replayable content |
| `bc-ai bc-ai.db` (SQLite, `evidence` table) | Per-run: `entity_id`, `flow_id`, `routing`, `maker_output` (JSON), `checker_output` (JSON), `gate_output` (JSON), confidence scores, model IDs, tokens, cost | **Partial** — outputs available; input context packet NOT stored. Would need to reconstruct the input from the BCF substrate state at run time. |
| Filesystem (gitignored) | No `fixtures/` / `snapshots/` / `panel-runs/` / `replays/` directories present in bc-ai | n/a |

### 4.1 Implication — fixtures must be CONSTRUCTED FRESH

A true before/after regression cannot be performed by importing historical panel runs because:

1. The **input context packets** sent to the models are not stored anywhere — the BCF substrate has moved on since each historical run, so reconstruction is not deterministic.
2. The **system prompts at the time** of each historical run are not stored — only their sha256 hashes. (The current prompts are in git, but if a historical run used an older revision of the prompt, the older revision exists only in git history and we don't know which sha256 matched which revision.)
3. Even the **model responses** from bc-ai.db's `maker_output` / `checker_output` / `gate_output` are JSON OUTPUTS only — not the full request/response that the LLM API received/emitted.

The only viable regression approach is to **construct a fresh fixture set today** by:

1. Selecting a representative candidate set (operator-curated, see §5).
2. Running each candidate through the registry-authoring panel **today** with the CURRENT (legacy-code) prompts and `temperature=0` — this becomes the **baseline (A)**.
3. Persisting the full request/response payloads for each candidate / each role (Maker, Checker, Moderator) under a local fixture directory (e.g. `bc-ai/fixtures/cluster-g/baseline-2026-06-22/<candidate_id>/<role>.json`).
4. Editing the 3 prompts on a feature branch.
5. Re-running the same candidates with the REWRITTEN prompts and `temperature=0` — this becomes the **rewrite (B)**.
6. Comparing A vs B per the acceptance gates (§7).

The baseline-capture step (steps 1–3) is a **prerequisite** to any prompt rewrite and consumes real model budget. The operator must authorize fixture capture before the rewrite work opens.

## 5. Proposed fixture set

Operator-confirmable; this section is the recommendation, not a final decision.

### 5.1 Sizing

Layer 1 inventory §10.6 Phase 1 suggested "30–60 days" of historical panel runs. Since we cannot import historical runs (per §4.1), the question becomes: how many fresh candidates make a statistically defensible regression?

| Tier | N | Coverage rationale |
|---|---:|---|
| Minimum | 30 | Enough to detect a single-digit-percentage shift in verdict distribution. Acceptable for first-pass go/no-go. |
| **Recommended** | **60** | Better resolution on edge cases; lets us cover 3 operations × 3 verdict bands × ~7 candidates each plus some variance. **Use this as the default.** |
| Thorough | 120 | If operator wants minimal residual ambiguity. Double the model cost. |

### 5.2 Candidate composition (target distribution at N=60)

Three operations × three verdict bands:

| Operation | APPROVE | OPERATOR_REVIEW | REJECT | Subtotal |
|---|---:|---:|---:|---:|
| `createEntity` | 8 | 4 | 4 | 16 |
| `createBusinessConcept` | 10 | 6 | 4 | 20 |
| `createCharacteristic` | 12 | 8 | 4 | 24 |
| **Subtotal** | **30** | **18** | **12** | **60** |

Rationale:

- **`createCharacteristic` gets the most weight (24)** because it's the path the M1–M10 Vocabulary Admission Checklist is built for. Renaming M1–M10 has the highest model-behavior risk on this path.
- **APPROVE band gets the most weight (30)** because false-negatives (an old APPROVE becoming a new REJECT or OPERATOR_REVIEW under the rewrite) are the highest-risk regression — they would block operator workflows that previously succeeded.
- **REJECT band gets the lowest weight (12)** because false-positives (an old REJECT becoming a new APPROVE) are still a regression but more visible at the operator-review stage.
- **OPERATOR_REVIEW band (18)** because OPERATOR_REVIEW is the most variance-sensitive verdict and a useful canary for "model is less confident now."

### 5.3 Candidate sourcing

Three viable paths (operator picks one or a blend):

**(a) Real prior panel-run subjects (preferred).** Query bc-core's `ai_run_ledger` for `run_kind='bcf-panel'` runs over the last 60 days, group by terminal verdict, sample 60 distinct `subject_uid` values per the distribution in §5.2. Then **construct the input context packet today** for each subject by replaying the BCF substrate's `getRegistryPacket(subject)` call — this is the canonical bc-ai entrypoint. The candidate set is "real subjects, fresh packets." Accept the substrate drift (some packets will differ from what was used at the original run) — we are testing prompt behavior, not historical replay.

**(b) Operator-curated subjects.** Operator hand-picks 60 subjects spanning the 3×3 grid. Slower to curate but gives the highest confidence in coverage of edge cases (homonyms, near-duplicates, code-valued concepts, status BCs with canonical value sets, etc.).

**(c) Synthetic candidates.** Construct 60 synthetic candidate inputs from scratch. Fastest but lowest fidelity — synthetic packets don't exercise the live substrate state.

**Recommended: (a) augmented with up to 10 (b)-curated edge cases** that the operator wants explicit coverage of (e.g. specific M-criteria failures the operator suspects the model handles fragilely).

### 5.4 Fixture-set on-disk shape

Proposed (operator-final):

```
bc-ai/fixtures/cluster-g/baseline-2026-06-22/
├── manifest.jsonl              ← one row per candidate: subject_uid, operation, expected_verdict
├── candidates/
│   ├── 00001-cand-abc123.json  ← input context packet
│   ├── 00002-cand-def456.json
│   └── …
└── outputs/
    ├── 00001/
    │   ├── maker.json           ← Maker model's full structured output + tokens / cost / duration
    │   ├── checker.json
    │   ├── moderator.json
    │   └── summary.json         ← consensus verdict + emitted f3_input shape
    └── …
```

After the rewrite, parallel directory `rewrite-2026-06-23/` (or whatever date) holds the B-side outputs with the same per-candidate shape.

Both directories are gitignored (large, model-output-heavy) — the manifests + acceptance reports are checked in.

## 6. Proposed semantic renames for Cluster G

Per Layer 1 inventory §4 + §10.7 recommendation:

| Legacy in prompt | Proposed semantic | Notes |
|---|---|---|
| `BCF B6` / `B6` (5 sites) | `BCF Business Concept Draft Review` panel / `Business Concept Draft Review` | Same family-name rename used in Track 2 bc-core comments. Single first-mention alias on each prompt file. |
| `F3` (9 sites — uppercase standalone) | `Registry Transition` service method | Same as Track 2. `f3_operation` (snake_case field name) is **preserved verbatim** as a Layer 2 identifier. |
| `M1`–`M10` (per-criterion, ~15 sites) | **Operator decision — see §6.2** | Critical positional-anchor question. |
| `M1-M10` (family shorthand, 5 sites) | `Vocabulary Admission Checklist` | Family rename only. Prose already uses "Vocabulary Admission Checklist" alongside `M1-M10` in existing prompts; rewrite drops the `M1-M10` shorthand in favor of the family name. |

### 6.1 First-mention alias discipline

Same as Track 2: semantic name primary, `(legacy: B6)` or `; legacy: B6` on first meaningful mention per prompt file, semantic-only on subsequent. The rewrite is *not* operator-visible in the rendered UI — prompts are model input — so the alias serves the human reader of the prompt source, not the model.

### 6.2 M1–M10 — the critical decision

The Layer 1 inventory §10.4 + §10.7 flagged that **M1 through M10 may function as ordinal positional anchors** for the model. The Maker explicitly enumerates M1, M2, …, M10 as a checklist in line order; the Moderator references the same list; the Checker independently attacks the list.

Three rename options, in increasing order of model-behavior risk:

| Option | Pattern | Positional anchor preserved? | Risk profile |
|---|---|---|---|
| **A. Numeric-suffix rename** | `M1` → `VOCAB-CHECK-01`, `M2` → `VOCAB-CHECK-02`, … `M10` → `VOCAB-CHECK-10`. Family-name rewrite: `M1-M10` → `VOCAB-CHECK-01..10`. | ✓ Yes — ordinal-N preserved | Lowest risk. The model sees a different prefix but the sequence is intact. **Default recommendation.** |
| B. Letter-suffix rename | `M1` → `VOCAB-CHECK-A`, … `M10` → `VOCAB-CHECK-J`. Family: `VOCAB-CHECK-A..J`. | ✓ Yes (alphabetic ordinal) | Slightly higher risk — letter ordinals may map differently to model's numeric sense of "ten items." |
| C. Per-criterion semantic rename | `M1` → `Bounded Evidence`, `M2` → `Citation Verbatim`, `M3` → `English Term and Definition`, …, `M10` → `Operator-Initiated Run` | ✗ No — semantic names lose the ordinal sequence | Highest risk. Loses positional anchor. The model has to associate 10 distinct phrases with 10 checklist positions; verdict drift expected. Requires fixture set N≥120 for confidence. |

**Plan recommendation: Option A** for the rewrite branch. The regression discipline (§7) is the same in any case, but Option A is the only one this plan endorses going in. If regression results show option A is safe, we can later evaluate Option C on its own gated branch — but Option C is not a default.

### 6.3 Out-of-scope inside the prompts

Preserved verbatim per all prior Track 1/2 batches:

- Decision identifiers — `DEC-02f5a9` (5 sites in the 3 prompts) — never renamed.
- Code identifiers — `f3_operation` (snake_case field name), `createEntity` / `createBusinessConcept` / `createCharacteristic` (operation discriminators), `registerCharacteristic` (F3 service method name), `proposed_operation`, `verdict_payload_json`, `source_citations`, `canonicalValueSet`, `semanticRole`, `proposedName`, etc. — all preserved.
- Closed-string output values — `APPROVE_FOR_DRAFT`, `REJECT`, `OPERATOR_REVIEW`, `global`, `pass`, `value` / `code` (kind enum), `status` / `dimension` / `diagnostic` / `strategic_filter` (semanticRole enum) — runtime payload values, preserved.
- Model invocation parameters — provider, model, temperature, max_tokens — not touched by this rewrite.

## 7. Regression acceptance gates

Each gate is a **hard requirement** for merging the rewrite branch. All gates must be GREEN.

### 7.1 Verdict-code match — ≥98%

For each candidate, compare the Moderator's `verdict_code` (A side) vs (B side). Verdict-code is one of `APPROVE_FOR_DRAFT`, `REJECT`, `OPERATOR_REVIEW` (and `OPERATOR_REVIEW_LATE` if emitted).

- **Threshold: ≥98% exact match across the fixture set.** At N=60, allows ≤1 mismatch.
- **Hard sub-threshold: 100% on APPROVE_FOR_DRAFT runs.** Any baseline APPROVE that flips to REJECT or OPERATOR_REVIEW under the rewrite is an immediate halt — operator must review before any further rewrite work.
- Direction-of-drift report: if the few mismatches are all in the same direction (e.g. all "APPROVE → OPERATOR_REVIEW"), flag as a confidence-loss signal.

### 7.2 `f3_input` structural equality — byte- or schema-exact

For every APPROVE run on the B side, the emitted `f3_input` JSON shape must match the A side exactly:

- **Field set:** identical keys, no additions, no deletions. Operator-recommended fields: `entity_name`, `characteristic_id`, `representation_term`, `data_type`, `semantic_role`, `canonical_value_set`, `kind`, `definition`, `term`, `proposed_operation.f3_operation`, `source_citations`, `checklist_answers` (the M1–M10 / VOCAB-CHECK-01..10 block), `classification`, `operator_confirm_required`.
- **Value equality:** byte-exact for primitives (string, number, boolean). Order-independent for arrays where the schema is set-valued. For the `checklist_answers` block specifically: if rename Option A is chosen, key names change (M1 → VOCAB-CHECK-01); the **answer values must remain byte-exact** even though keys differ. The mapping `M{i} → VOCAB-CHECK-0{i}` must be honored 1:1.
- **No new schema variants:** the rewrite must not introduce a new `f3_input` field or remove an existing one. The bc-core `recommendation.validator.ts` (cited in `test_registry_authoring_panel.py:345–349` as the canonical contract) defines the valid shape — anything outside that shape is a regression failure.

### 7.3 No new missing structured-output envelopes

bc-ai's `parse_json_output` (Maker), `parse_json_output` (Checker), and the Moderator's emit path can fail to produce a structured envelope if the model returns malformed JSON. The baseline ratio of "missing envelope" cases is known (close to zero at `temperature=0`). The rewrite must not increase this ratio.

- **Threshold: B side parse-failure count ≤ A side parse-failure count + 1.**
- Any new parse-failure case must be reviewed manually before pass.

### 7.4 OPERATOR_REVIEW downgrade ratio

If the rewrite introduces a material increase in OPERATOR_REVIEW downgrades (cases the model was confident about under the baseline but now hedges on), that's a confidence-loss signal that operators will feel as more manual-review queue volume.

- **Threshold: B side OPERATOR_REVIEW count ≤ A side OPERATOR_REVIEW count × 1.20.** (20% increase tolerance.)
- Beyond 20%: halt and review the affected candidates manually.

### 7.5 Reasoning-text coherence (manual spot-check)

For each verdict band (APPROVE, OPERATOR_REVIEW, REJECT), spot-check the **reasoning_trace** text of 3 randomly-selected B-side runs. The reasoning must be coherent prose with the new semantic names — not garbled, not stuck citing the legacy code, not switching mid-sentence.

- **Manual gate:** operator + author both review the 9 spot-checked traces and concur on pass/fail.

### 7.6 Cost / token-count sanity

Token counts and cost are not regression gates per se, but they're a useful sanity check on whether the new prompts caused a material change in model behavior.

- **Soft threshold:** B side total tokens within ±15% of A side total tokens; B side total cost within ±15% of A side total cost.
- Outside this range: investigate before merge.

### 7.7 Stochastic-source handling

All regression runs use `temperature=0`. If any model in the panel exposes non-determinism even at temperature=0 (e.g. tool-routing, sampling, or backend load-balancing producing different responses on identical inputs), document the source and run each candidate **N=3 times** on the B side. Report median verdict and per-candidate variance.

## 8. Execution sequence

Locked sequence; no step may be reordered without a separate operator decision.

| # | Step | Authorization required | Output |
|---|---|---|---|
| 1 | Operator approves this plan | — | Plan ratified; §5.2 fixture distribution + §6.2 Option choice locked |
| 2 | **Construct fixture candidate set** per §5.3 | Operator authorization (involves bc-core SQL reads + BCF substrate `getRegistryPacket` calls — read-only on substrate) | `bc-ai/fixtures/cluster-g/candidates/*.json` + `manifest.jsonl` |
| 3 | **Baseline replay (A)** — run each candidate through current prompts at `temperature=0` | Operator authorization (consumes model budget) | `bc-ai/fixtures/cluster-g/baseline-{date}/outputs/<candidate>/<role>.json` |
| 4 | **Capture baseline metrics** — verdict distribution, parse-failure count, token / cost totals | Automatic at end of step 3 | `bc-ai/fixtures/cluster-g/baseline-{date}/baseline-summary.json` |
| 5 | **Prompt rewrite on feature branch** — apply §6 renames to the 3 files | Operator authorization | Branch with 3 prompt files edited; **NOT MERGED** |
| 6 | **Rewrite replay (B)** — same candidate set, rewritten prompts, `temperature=0` | Operator authorization (consumes model budget again) | `bc-ai/fixtures/cluster-g/rewrite-{date}/outputs/<candidate>/<role>.json` |
| 7 | **Regression diff report** — apply gates §7.1–§7.7 | Automatic | `bc-ai/fixtures/cluster-g/regression-report-{date}.md` — checked into git for review |
| 8 | **Operator review of regression report** | Operator decision | Pass / fail / iterate |
| 9 | **Canary deploy (if pass)** — deploy bc-ai with new prompts to staging, run a fresh wave of BCF authoring on a controlled candidate subset, compare staging telemetry vs feature-branch regression results | Operator authorization | Staging telemetry + comparison |
| 10 | **Production roll-out** — merge feature branch; monitor bc-core's BCF panel telemetry for 7 days post-deploy for verdict-distribution anomalies | Operator authorization | Track 2 closure note updated; ADR DEC-54f221 Layer 1 marked closed |

The fixture capture step (#2 and #3) is the prerequisite. Without it, no rewrite can be safely evaluated.

## 9. Open questions and blockers

### 9.1 Open questions for operator

1. **Sizing — N=30 / 60 / 120?** §5.1 recommends 60. Confirm.
2. **Sourcing — (a) real subjects with fresh packets, (b) operator-curated, (c) synthetic, or a blend?** §5.3 recommends (a) + 10 of (b).
3. **M1–M10 rename — Option A / B / C?** §6.2 recommends A (`VOCAB-CHECK-01..10`).
4. **Verdict-code threshold — 98% / 99% / 100%?** §7.1 recommends 98%.
5. **APPROVE flip tolerance — strictly 0, or allow 1 with manual review?** §7.1 recommends strictly 0.
6. **OPERATOR_REVIEW increase tolerance — 20% / 10% / 0%?** §7.4 recommends 20%.
7. **Are fixture outputs checked into git (large)?** Or stored externally (e.g. `bc-ai/fixtures/` gitignored, with manifests / reports checked in)? Recommendation: gitignored outputs, checked-in manifests + acceptance report only.
8. **Cost budget for the regression runs.** N=60 × 3 roles × 2 replays = 360 model calls per side, 720 total. Order-of-magnitude estimate at current pricing: Claude Opus + GPT-5.5 + DeepSeek-on-Bedrock, ~$50–150 total. Operator confirms budget allocation before step 2 opens.

### 9.2 Blockers

1. **No artifact_uri populated in bc-ai** (per §4). Fixture capture is the only viable path. Not a blocker on Cluster G itself, but a planning constraint that drives steps #2 and #3 above.
2. **Model availability.** Maker (Claude Opus 4.7) + Checker (DeepSeek V3.2 via Bedrock Converse) + Moderator (GPT-5.5-2026-04-23) — all three providers must be reachable and within rate limits during fixture capture + replay. CodeArtifact / Cognito tokens valid throughout.
3. **No bc-ai tests for prompt content currently exist.** The 3 spec files we already covered (test_bcf_telemetry.py, test_registry_authoring_composition.py, test_registry_authoring_panel.py) test the panel orchestration and roster composition, not the prompt content itself. The regression discipline IS the test for prompt content; there is no unit-test alternative.
4. **bc-core's ai-telemetry endpoint must remain available** during fixture capture (each panel run emits telemetry via `POST /api/ai-telemetry/bcf-panel-run/from-summary`). bc-core does not need to be running for the rewrite itself, but it must be reachable during baseline + rewrite replays.

### 9.3 Not blockers but worth flagging

- The `M1–M10` checklist may carry **load-bearing positional semantics** that the model has learned implicitly. Even with Option A (numeric-suffix preserved), the prefix change (`M1` → `VOCAB-CHECK-01`) introduces 6 extra tokens per criterion = 60 extra prompt tokens × 3 panel agents. Token count may shift slightly without behavior shifting.
- The `BCF B6, DEC-02f5a9` parenthetical is the panel's identity anchor. Renaming `B6` to `Business Concept Draft Review` keeps the identity assertion intact but lengthens it. Marginal token cost.
- The `F3` references are all in operator-facing constraint language (e.g. "refused by F3 with bc_kind_role_coupling_violation"). Renaming to "Registry Transition" preserves the meaning but loses the conciseness of a 2-character code. The model may emit slightly longer rationales after the rename.

## 10. Explicit out-of-scope for Cluster G

Per ADR DEC-54f221, Cluster G covers prompt text only. The following are **explicitly NOT in scope** for this batch:

| Surface | Out-of-scope reason |
|---|---|
| **Implementation identifiers** — `MetricAuthoringMaterializationService`, `McfCertWriterService`, `RegistryAuthoringMaker` / `Checker` / `Moderator` class names, `flow_id` constant, `model_id` constants on agent classes (`opus-maker`, `deepseek-checker`, `gpt-55-judge`), Python function / variable / module names | Layer 2 (Implementation Names) — operator-gated; separate from Layer 1. |
| **Telemetry keys** — bc-core ai-telemetry column names, JSON keys in telemetry payload (`runUid`, `panelRunUid`, `verdictCode`, `agentOutputsJson`, etc.), event-emit identifiers | Layer 3 (Compatibility Names) — operator-gated; requires telemetry / log / dashboard pre-inventory before opening. |
| **DB enum values** — `run_kind`, `run_scope`, `status`, `verdict_code` ENUM values inside the bc-core ai_run_ledger / ai_call_ledger / bcf_panel_run tables; closed-string status values like `'PASS'`, `'REJECT'`, `'OPERATOR_REVIEW'`, `'wip'` | Layer 3 — persisted compatibility names. |
| **Runtime payload values** — the output JSON values themselves (verdict_code values, classification values, semantic_role values, kind values, operation discriminator values like `createEntity`, `createBusinessConcept`, `createCharacteristic`) | Run-time semantics — these are governed by bc-core's recommendation validator, not by prompt text. Changing them is a substrate decision, not a rename. |
| **Model / provider swaps** — switching Maker from Claude Opus to a different model; switching Checker from DeepSeek; switching Moderator from GPT-5.5 | A separate operator decision under DEC-09f86b (D-M12 Panel) / equivalent. Cluster G renames text inside prompts that the current 3 models read. Different models would invalidate the regression fixtures and require a fresh discipline. |
| **The 44 prompt files clean of legacy workflow codes** | Not in scope — they have nothing to rename. |
| **bc-core code that produces the BCF authoring packet, processes the panel response, or persists telemetry** | Out of Cluster G scope. Cluster G is bc-ai prompts only. |
| **Documentation references to `B6` / `M12` / `PE-MC-*` etc. in `bc-docs-v3/docs/`** | Already done across Tracks 1+2. Cluster G doesn't reopen documentation. |

## 11. Recommendation on whether Cluster G is ready for fixture import

**Cluster G is NOT ready for prompt rewrite execution today.** It is ready to open the **fixture-capture step (§8 step 2 → step 4)** under operator authorization. Specifically:

- **Ready ✓** — Surface inventory complete (3 files, 29 occurrences, per-file detail in §3).
- **Ready ✓** — Operator-mapped semantic names exist for B6, F3, and M1–M10 (with the Option A recommendation per §6.2).
- **Ready ✓** — Regression-acceptance gates defined (§7).
- **Ready ✓** — Out-of-scope surface explicitly bounded (§10).
- **NOT ready ✗** — No fixture set exists. **bc-core's ai_telemetry tables store hashes only; bc-ai.db stores partial outputs without inputs**; no on-disk artifact store; no historical replay path is available. The §8 step 2–3 fresh-fixture-capture is a **prerequisite**, not a parallel activity.
- **NOT ready ✗** — Operator decisions on §9.1 questions 1–8 are required before fixture capture can be authorized (sizing, sourcing, M1–M10 option, thresholds, cost budget).
- **NOT ready ✗** — Operator-authorized budget for ~720 model calls (≈$50–$150 estimated) is a precondition for fixture capture.

The recommendation to the operator is therefore:

1. **Ratify this plan** (§§ 1–10) with any adjustments to the open questions in §9.1.
2. **Authorize fixture capture** as a single operator-scoped session (§8 steps 2–4): construct the candidate set, run baselines at `temperature=0`, persist outputs.
3. **Pause for review** of the baseline summary (`baseline-summary.json`) before authorizing the rewrite branch.
4. **Authorize prompt rewrite + B-side replay** (§8 steps 5–7) once baseline is committed.
5. **Operator-review the regression report** (§8 step 8) before any merge.

Cluster G is the last Layer 1 surface. Once it closes, Layer 1 under DEC-54f221 is complete and the path to Layer 2 / Layer 3 opens.

## 12. Scope honoured

- Planning / fixture-inventory only.
- No prompt edits.
- No bc-ai code edits (read-only inspection used to produce this plan).
- No model calls.
- No DB writes; no DB reads against bc-core (used only the schema files in `bc-core/src/database/schema/ai-telemetry/*.ts` for shape — these are declarative Drizzle definitions, not live data).
- No runtime / service restart.
- No PR.
- No DevHub decision mutation.
- No business / platform substrate mutation.
- The two stuck Metric Contract Versions on `bc_platform_dev` are untouched.

**Stop after this plan.**
