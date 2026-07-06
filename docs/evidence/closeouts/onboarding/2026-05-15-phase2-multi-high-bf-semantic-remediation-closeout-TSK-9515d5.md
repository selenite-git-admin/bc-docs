---
title: "Phase 2 multi-HIGH BF semantic remediation — closeout"
task: TSK-9515d5
date: 2026-05-15
status: closed
type: sop-closeout
authority: DEC-a49413
related:
  - DEC-a49413   # §11 BF SDA-trust predicate; §12 BF semantic remediation
  - DEC-a17d0f   # SDA umbrella authority
  - 2026-05-15-phase2-multi-high-bf-semantic-remediation-plan-TSK-9515d5.md
  - 2026-05-15-phase1-bulk-bf-semantic-remediation-closeout-TSK-9515d5.md
  - 2026-05-15-phase1-bulk-bf-semantic-remediation-plan-TSK-9515d5.md
---

# Phase 2 Multi-HIGH BF Semantic Remediation — Closeout (TSK-9515d5)

**Status:** Phase 2 closed 2026-05-15. SOP §7 final acceptance satisfied. 191 of 191 SOP-eligible multi-HIGH OAGIS BFs remediated.

---

## 1. Authority and scope

| Authority | Reference |
|---|---|
| Decision | **DEC-a49413** §11 (BF SDA-trust read predicate) and §12 (post-certify BF semantic remediation endpoint) — unchanged |
| Task | **TSK-9515d5** — Phase 2 slice |
| Phase 2 SOP | [2026-05-15-phase2-multi-high-bf-semantic-remediation-plan-TSK-9515d5.md](../../work-records/onboarding/2026-05-15-phase2-multi-high-bf-semantic-remediation-plan-TSK-9515d5.md), filed commit `e809057`; cohort-count errata + shrinkage clarification commit `19705e2` |
| Phase 1 SOP | [2026-05-15-phase1-bulk-bf-semantic-remediation-plan-TSK-9515d5.md](../../work-records/onboarding/2026-05-15-phase1-bulk-bf-semantic-remediation-plan-TSK-9515d5.md) (frozen derivation table reused verbatim) |
| Phase 1 closeout | [2026-05-15-phase1-bulk-bf-semantic-remediation-closeout-TSK-9515d5.md](2026-05-15-phase1-bulk-bf-semantic-remediation-closeout-TSK-9515d5.md) |

Scope was strictly the **multi-HIGH OAGIS BFs that are also frozen-table-eligible** under the Phase 1 derivation table. The §12 endpoint, atomic UPDATE+INSERT transaction, G1–G8 evaluation, and refuse-on-any-failure rule are unchanged from Phase 1.

The substantive design difference from Phase 1 was the introduction of an operator-disambiguation step: every Phase 2 BF has >1 HIGH-confidence `standardRef` candidate, so a chooser (operator or AI assist) selects exactly one before any bulk apply. No live oagidocs.org dependency at any point; all evidence sourced from local PG + Mongo seed + raw scrape archive.

---

## 2. Cohort

| Stage | Count |
|---|---:|
| Live OAGIS no-§11 cohort after Phase 1 | 2,604 |
| Raw multi-HIGH bucket (audit `4cdad6a`) | 391 |
| Frozen-table-ineligible filtered out | 1,128 |
| Non-multi-HIGH (0 or 1 HIGH candidate) filtered out | 1,285 |
| **SOP-eligible Phase 2 cohort** | **191** |
| ↳ AI-PICK (primary heuristic singletons) | 112 |
| ↳ REVIEW resolved by secondary heuristic | 79 |
| ↳ Unresolved (operator_required) | **0** |

The ~200 multi-HIGH rows that did not qualify under SOP §2 rule 5 are not lost; they are routed to Phase 1b (Amount/Quantity → unit-resolution) or Phase 4 (Identifier+code, Code+code, Indicator/boolean, Number/*, etc.). See §9 residual backlog.

Disambiguation rule frequency (from finalize-phase2-selections.mjs run, commit `124eda8`):

| Rule | Count | Pass type |
|---|---:|---|
| `primary:bf_name_infix_header` | 80 | AI-PICK |
| `primary:bf_name_infix_line` | 28 | AI-PICK |
| `primary:bf_name_infix_detail` | 4 | AI-PICK |
| `secondary:R3_component_root_eq_objectClass` | 62 | REVIEW resolved |
| `secondary:R1_objectClass_suffix_item` | 17 | REVIEW resolved |

Total: 80 + 28 + 4 + 62 + 17 = **191** ✓

---

## 3. Artifacts

### bc-core commits (in chronological order)

| Commit | Subject |
|---|---|
| `1a2e17d` | chore: Phase 2 multi-HIGH disambiguation packet (generator + packet + 112-row AI-PICK draft) |
| `124eda8` | chore: finalize Phase 2 multi-HIGH selections (final 191-row selection JSONL + review report) |
| `4adc2c6` | feat: Phase 2 selection-driven dry-run support (`--from-selection`) |
| `d8d49a7` | feat: Phase 2 apply mode (drift guard + per-row validation + halt criteria) |
| `b2f8bfd` | fix: unwrap `suggestForBf` in Phase 2 apply path (one-line crash fix) |
| `390a697` | chore: Phase 2 run-1 review packet (25/25 PASS, 13-check audit) |

### bc-docs-v3 commits

| Commit | Subject |
|---|---|
| `e809057` | docs: Phase 2 SOP (DEC-a49413 §12 operational procedure for the 391 → 191 multi-HIGH cohort) |
| `19705e2` | docs: cohort-count errata (391 raw → 191 SOP-eligible) and shrinkage clarification |
| _(this commit)_ | docs: Phase 2 closeout |

### Output artifacts (uncommitted, retained under `bc-core/scripts/audit-output/`)

- **Disambiguation packet:** `phase2-multi-high-disambiguation-packet-seed-20260515.md` (191 review blocks)
- **AI-PICK draft:** `phase2-multi-high-selection-draft-seed-20260515.jsonl` (112 rows)
- **Finalized selection:** `phase2-multi-high-selection-final-seed-20260515.jsonl` (191 rows)
- **Selection review report:** `phase2-multi-high-selection-review-seed-20260515.md`
- **Phase 2 dry-run:** `phase2-bf-remediation-dry-run-2026-05-15T15-19-10-127Z.jsonl` + `.summary.csv` (191/191 dry_run_ok)
- **Phase 2 apply JSONLs:**
  - run 1: `phase2-bf-remediation-apply-2026-05-15T15-38-23-048Z.jsonl` (25 success)
  - run 2: `phase2-bf-remediation-apply-2026-05-15T15-48-52-901Z.jsonl` (100 success)
  - run 3: `phase2-bf-remediation-apply-2026-05-15T15-53-53-414Z.jsonl` (66 success)
- **Phase 2 run-1 review packet:** `phase2-run1-review-25-seed-20260515.md` (committed at `390a697`)

### Review helpers (committed)

- `scripts/build-phase2-multi-high-packet.mjs` (commit `1a2e17d`)
- `scripts/finalize-phase2-selections.mjs` (commit `124eda8`)
- `scripts/build-phase2-run1-review-packet.mjs` (commit `390a697`)
- `scripts/bulk-remediate-bf-semantics.mjs` (Phase 2 extensions at `4adc2c6` → `d8d49a7` → `b2f8bfd`)

---

## 4. Execution

| Step | Cap | Successes | p50 latency | Notes |
|---|---:|---:|---:|---|
| Phase 2 dry-run (no-write) | (full pool) | 191 / 191 `dry_run_ok` | — | Validation: every selectedStandardRef byte-identical to a current HIGH candidate; derivation matches; gates pass |
| Apply run 1 (after `b2f8bfd` fix) | 25 | **25** | **106 ms** | First successful Phase 2 apply (initial attempt at `d8d49a7` crashed before POST; see §8) |
| Apply run 2 | 100 | **100** | **150 ms** | Drift guard: live=166 / shrunk=25 (allowed) / unexpected=0 |
| Apply run 3 (final remainder) | 66 | **66** | **121 ms** | Drift guard: live=66 / shrunk=125 / unexpected=0 |
| **Total Phase 2 bulk** | | **191** | | All in 191/191 = 100% success |

Wall-clock for the full Phase 2 apply chain: ≈ 6 minutes across the three capped runs and the operator review between them.

Canary `invoice_hdr_total_amount` asserted §11-trusted with the expected `(measure-currency, currency, OAGIS, https://www.oagidocs.org/docs/invoice-header#total-amount)` shape at the start of every run.

---

## 5. Verification

| Gate | Result |
|---|---|
| Disambiguation packet — every PICK selectedStandardRef byte-identical to a HIGH candidate | **0 validation failures across 112 + 79** |
| Phase 2 dry-run (all 191 rows) | **191 / 191 `dry_run_ok`** |
| Run-1 13-check review (apply commit `390a697`) | **25 / 25 PASS** |
| Run-2 30-row sample review (deterministic seed `20260515`) | **30 / 30 PASS** |
| Final acceptance 50-row sample across all three apply JSONLs (proportional draw: run1=4, run2=31, run3=15) | **50 / 50 PASS** (threshold ≥49/50) |

Every check includes the Phase 2 **selection-fidelity** test: PG `standard_ref` byte-identical to the JSONL's `selection.selectedStandardRef`. Zero rows in any review packet had `result != 'success'`, zero `certificationRecordId` were null (the envelope fix from Phase 1, commit `d56fce4`, holds), and every cert_record carries all 9 gates (G1, G2a, G2b, G3, G4, G5, G6, G7, G8) with `pass` verdicts.

Family / unit distribution in the final 50-row sample:

| family / unit | n |
|---|---:|
| `identifier / null` | 34 |
| `datetime / null` | 11 |
| `date / null` | 3 |
| `text / null` | 2 |

---

## 6. DB final state

| Metric | Value |
|---|---:|
| `contract.certification_record` rows with `action_code='remediate_bf_semantics'` | **1,392** |
|  — canary (pre-Phase 1) | 1 |
|  — Phase 1 bulk | 1,200 |
|  — Phase 2 bulk | 191 |
| Cumulative trusted OAGIS BFs (canary + bulk) | **1,392** |
| Live untrusted OAGIS cohort remaining | **2,413** |
| `contract.canonical_field` rows touched in Phase 2 window | 0 |
| `contract.metric_contract` rows touched in Phase 2 window | 0 |
| Tenant DB rows touched | 0 |

Window: `2026-05-15T15:37:56.431Z` (pre-Phase 2 run 1) → `~2026-05-15T15:54:30Z` (Phase 2 run 3 completion). Reconciles: `1 + 1,200 + 191 = 1,392 = rbs_total`. Original OAGIS-cert population: `1,392 + 2,413 = 3,805` ✓.

---

## 7. Invariants preserved

- ❌ Zero CF row changes across the full Phase 2 window.
- ❌ Zero `metric_contract` row changes.
- ❌ Zero tenant DB connections opened.
- ❌ Zero direct SQL writes — every change flowed through `POST /api/business-fields/:fieldId/remediate-semantics`.
- ❌ Zero override-path uses (the §12 endpoint has no override; any G1–G8 failure refuses the row).
- ❌ Zero `local_gate_failed`, `selection_not_in_candidates`, `endpoint_422`, `endpoint_5xx`, or `already_trusted` rows across 191 POSTs.
- ❌ Zero halt-criterion trips (consecutive 5xx, consecutive identical 422, p50 > 2s, consecutive `selection_not_in_candidates`).
- ✅ All 191 cert_records carry full G1–G8 verdicts, all `pass`.
- ✅ All 191 BFs retain `status_code='certified'`; immutable columns (`representation_term`, `data_type`, `pii_classification`) unchanged.
- ✅ All 191 PG `standard_ref` values byte-identical to the operator-finalized selection's `selectedStandardRef` (C13 selection-fidelity 50/50 PASS in final acceptance).
- ✅ No fabricated standardRefs. Every selected ref traces to a `(noun, componentSlug, fieldSlug)` tuple present in the local OAGIS scrape archive.
- ✅ No live oagidocs.org dependency throughout the phase.

---

## 8. Known anomaly

**First Phase 2 apply attempt crashed before POST (closed by `b2f8bfd`).**

- **Symptom:** Apply commit `d8d49a7` invoked at `2026-05-15T15:31:04.158Z` crashed with `TypeError: candidates.filter is not a function` inside the per-row suggest re-check, before any HTTP request was issued.
- **Root cause:** The shared helper `suggestForBf(...)` returns `{ candidates: [...] }`. The Phase 2 dry-run branch (commit `4adc2c6`) correctly unwraps it; the Phase 2 apply branch (commit `d8d49a7`) lost the unwrap on the copy and treated the return value as an array directly.
- **Impact:** **Zero.** No POST requests were issued. DB state at the moment of the crash: `rbs_total=1201` (1 canary + 1,200 Phase 1); both `rbs_added_in_window` and `bf_updated_in_window` were 0. The DB was bit-for-bit identical to its pre-attempt state.
- **Fix:** One-line patch at commit `b2f8bfd` — `const suggest = suggestForBf(...); const highs = suggest.candidates.filter(...);` matching the dry-run branch. Apply retry at `2026-05-15T15:37:56.431Z` succeeded with 25/25 (run 1).
- **No remediation required.** The DB audit chain is intact; the crash was caught before any side effect.

---

## 9. Residual backlog (after Phase 2)

| Phase | Cohort definition | Approx count | Notes |
|---|---|---:|---|
| **1b** | `Amount` / `Quantity` BFs (`measure-currency` / `measure-count`) | **87** | Requires unit-resolution playbook (which currency / count unit per BF); blocked on that authoring. Plus any multi-HIGH Amount/Quantity rerouted from Phase 2. |
| **3** | MEDIUM-only candidates (crosswalk + one signal, not byte-identical description) | **630** | Mandatory spot-rate ≥10%; weaker semantic match; needs hand review. |
| **4** | `suggest_no_candidates` + `deferred_data_shape` + `refused_ambiguous` + multi-HIGH-but-frozen-ineligible | **1,696** | Seed enrichment (missing crosswalk rows; nested complex-type field walks) or operator-authored refs. |
| **Total residual** | | **2,413** | |

87 + 630 + 1,696 = 2,413 = live untrusted OAGIS cohort ✓ (reconciles).

---

## 10. Recommendation for next slice

**Recommended next: Phase 3 — MEDIUM-only candidates (630 BFs).**

Rationale:

- **Larger reach per slice.** 630 vs Phase 1b's 87. Closing Phase 3 moves cumulative coverage from 1,392 → ~2,022 of 3,805 (53%), versus Phase 1b → 1,479 (39%). The marginal trust gain per operator-hour is higher on Phase 3.
- **Reuses Phase 2 infrastructure as-is.** Phase 2 already proved the disambiguation + selection-file + selection-driven apply pipeline works end-to-end. Phase 3 is the same pipeline with a relaxed candidate filter (MEDIUM instead of HIGH). The SOP would change one rule, not the whole shape; the apply script likely needs zero changes (the `--from-selection` flow already validates byte-identity to the selected ref regardless of confidence band).
- **Phase 1b is gated on an external decision.** Phase 1b cannot start until someone authors the unit-resolution playbook (how to choose between `USD`, `EUR`, `INR`, ... per Amount BF, or `EA`, `KG`, ... per Quantity BF). That's a separate research and authoring task; without it, Phase 1b is stuck. Phase 3 has no such external blocker.
- **AI-assist heuristic translates directly.** Phase 2's three-tier heuristic (description-match singleton → property+derivedBfName singleton → infix convention; otherwise REVIEW) ports to Phase 3 with one adjustment: MEDIUM rows by definition lack description-match singletons, so the first rule never fires. The second and third still resolve a usable fraction; the rest go to REVIEW. Operator burden will be higher than Phase 2 (estimate ~30–40% REVIEW vs Phase 2's 41% pre-resolution), but the workflow is identical.
- **Phase 4 should remain last.** 1,696 rows but every row needs seed enrichment, complex-type walks, or hand-authored refs. It is multiple weeks of work and produces the lowest semantic confidence per row.

**Suggested next sub-tasks (do not start yet):**

1. Author the Phase 3 SOP as a sibling work-record. Same shape as Phase 2 SOP; differences:
   - Cohort filter: confidence='medium' rows from `suggestStandardRef` (replaces multi-HIGH).
   - Mandatory spot-rate raised to ≥10% in §7 (vs Phase 2's structural review of 100% AI-PICK packet).
   - Acceptance threshold tightened? Operator's call — could be 49/50 (Phase 1/2 default) or 50/50 for the weaker-evidence band.
2. Verify the suggestion service treats MEDIUM rows correctly. The current `suggestStandardRef` ranks by HIGH/MEDIUM/LOW and returns all candidates with confidence labels; no service-side change needed.
3. Confirm the apply script's selection validation does not gate on `confidence='high'` (audit the validator before running Phase 3 dry-run).

**What not to do next.** Skipping Phase 3 to do Phase 4 first would be a process inversion — Phase 4 has weaker per-row signals and higher operator-authoring burden, and would produce more residual debt than progress.

---

## 11. Closeout

**Phase 2 SOP §7 final acceptance satisfied (50 / 50, threshold ≥49 / 50).** TSK-9515d5 Phase 2 closed. The remaining 2,413-row OAGIS legacy-cert cohort is the Phase 1b / 3 / 4 backlog and is out of scope for this closure.

**Cumulative TSK-9515d5 status: 1,392 trusted of 3,805 OAGIS-cert population (~36.6%) via 1 canary + 1,200 Phase 1 + 191 Phase 2 bulk remediations. Zero CF, metric, tenant, or override-path side effects across both phases.**
