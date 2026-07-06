---
title: "Phase 1 bulk BF semantic remediation — closeout"
task: TSK-9515d5
date: 2026-05-15
status: closed
type: sop-closeout
authority: DEC-a49413
related:
  - DEC-a49413   # §11 BF SDA-trust predicate; §12 BF semantic remediation
  - DEC-a17d0f   # SDA umbrella authority
  - 2026-05-15-phase1-bulk-bf-semantic-remediation-plan-TSK-9515d5.md
---

# Phase 1 Bulk BF Semantic Remediation — Closeout (TSK-9515d5)

**Status:** Phase 1 closed 2026-05-15. SOP §6 final acceptance satisfied.

---

## 1. Authority and scope

| Authority | Reference |
|---|---|
| Decision | **DEC-a49413** §11 (BF SDA-trust read predicate) and §12 (post-certify BF semantic remediation endpoint) |
| Task | **TSK-9515d5** — Operationalise OAGIS provenance lookup and bulk apply |
| Umbrella | DEC-a17d0f (SDA primitive certification) |
| Operating SOP | [`2026-05-15-phase1-bulk-bf-semantic-remediation-plan-TSK-9515d5.md`](../../work-records/onboarding/2026-05-15-phase1-bulk-bf-semantic-remediation-plan-TSK-9515d5.md) (commits `6ee3170` initial, `9160c15` shrinkage amendment) |

Scope was strictly the **single-HIGH OAGIS BFs** with no §11 evidence, after exclusion of:
- multi-HIGH (Phase 2 backlog)
- MEDIUM / LOW (Phase 3 backlog)
- no-candidate (Phase 4 backlog)
- `Amount` / `Quantity` representation terms (Phase 1b backlog)
- `Number` representation term (refused)
- (representation_term, data_type) pairs not in the patched frozen derivation table

No metric promotion, no CF changes, no tenant DB touches. Writes only via `POST /api/business-fields/:fieldId/remediate-semantics`.

---

## 2. Cohort

| Stage | Count |
|---|---:|
| Original OAGIS BFs with `status='certified'` and no §11 evidence (audit `4cdad6a`) | 3,804 |
| Single-HIGH `suggest_standard_ref` candidates | 1,555 |
| After Phase 1 derivation-table filter and projected G1–G8 replay | **1,200** (dry_run_ok) |
| Excluded / deferred buckets (sum to 2,604) | see below |

Excluded / deferred breakdown:

| Bucket | Count | Disposition |
|---|---:|---|
| `suggest_no_candidates` | 1,228 | Phase 4 — seed gap or property-shape mismatch |
| `suggest_only_medium_or_low` | 630 | Phase 3 — MEDIUM-only spot-check protocol |
| `suggest_multi_high` | 391 | Phase 2 — operator disambiguation |
| `deferred_data_shape` | 264 | Phase 4 — Identifier/Code with `data_type='code'` violates G6 |
| `excluded_phase1b_unit_resolution` | 87 | Phase 1b — Amount/Quantity need a unit-resolution playbook |
| `refused_ambiguous` | 4 | Refused — `representation_term='Number'` |
| **Total deferred** | **2,604** | |

---

## 3. Execution

| Step | Cap | Successes | p50 latency | Notes |
|---|---:|---:|---:|---|
| Canary (SES-594568, pre-Phase 1) | 1 | 1 | — | `invoice_hdr_total_amount` → `measure-currency/currency` |
| Run 1 | 25 | **25** | 107 ms | First capped apply; exposed envelope-bug in JSONL fidelity (DB writes correct) |
| Run 2 | 250 | **250** | 115 ms | Drift guard had to be softened to shrinkage-tolerant after run-1 |
| Run 3 | 925 | **925** | 121 ms | Final remainder; clean execution end-to-end |
| **Total bulk** | | **1,200** | | Cumulative wall-clock ≈ 3.5 min for 1,200 POSTs |

Canary BF retained as a known-good baseline throughout. Every apply run pre-flighted the canary via PG SELECT before processing any cohort row; all three runs found it §11-trusted with the expected `(measure-currency, currency, OAGIS, https://www.oagidocs.org/docs/invoice-header#total-amount)` shape.

---

## 4. Verification

| Gate | Result |
|---|---|
| Structural QA on dry-run sample (seed 20260515) | **30 / 30 PASS** |
| Enriched semantic QA against PG + Mongo + raw OAGIS scrape archive | **30 / 30 PASS** |
| Run-1 12-check review | **25 / 25 PASS** |
| Run-2 12-check review | **250 / 250 PASS** |
| Run-3 12-check review | **925 / 925 PASS** |
| Final acceptance sample, seed 20260515, n=50 | **50 / 50 PASS** (threshold ≥49 / 50) |

The final-acceptance packet sampled across all three apply JSONLs with proportional draw (run-1: 1, run-2: 8, run-3: 41), covering the full family/unit distribution of the 1,200 writes including the one row in the highest-watch derivation family (`measure-percent / percentage`).

---

## 5. DB final state

| Metric | Value |
|---|---:|
| `contract.certification_record` rows with `action_code='remediate_bf_semantics'` | **1,201** |
|  — of which canary (pre-Phase 1) | 1 |
|  — of which Phase 1 bulk | 1,200 |
| BFs that gained §11 SDA trust evidence via Phase 1 | **1,200** |
| Live untrusted OAGIS cohort remaining | **2,604** |
| `contract.canonical_field` rows touched in window | 0 |
| `contract.metric_contract` rows touched in window | 0 |
| Tenant DB rows touched | 0 |

Window: `2026-05-15T13:15:44.175Z` → `2026-05-15T~13:55:00Z`. All §11 trust accruals were via `remediate_bf_semantics` action_code with `from_state='certified' AND to_state='certified'`; no state transitions, no override-path use.

---

## 6. Invariants preserved

- ❌ Zero CF row changes across the full Phase 1 window.
- ❌ Zero `metric_contract` row changes.
- ❌ Zero tenant DB connections opened.
- ❌ Zero direct SQL writes — every change flowed through `POST /api/business-fields/:fieldId/remediate-semantics`.
- ❌ Zero override-path uses (the §12 endpoint has no override; any G1–G8 failure refuses).
- ❌ Zero `local_gate_failed`, `endpoint_422`, `endpoint_5xx`, or `already_trusted` results across 1,200 POSTs.
- ✅ All 1,200 cert_records carry full G1, G2a, G2b, G3, G4, G5, G6, G7, G8 verdicts, all `pass`.
- ✅ All 1,200 BFs retain `status_code='certified'`; immutable columns (`representation_term`, `data_type`, `pii_classification`) unchanged.
- ✅ All proposed `standardRef` values match the OAGIS provenance pattern `https://www.oagidocs.org/docs/{componentSlug}#{fieldSlug}` with byte-identical evidence corroboration across PG, Mongo seed, and raw scrape archive.

---

## 7. Known anomaly

**Run-1 JSONL fidelity gap (closed for run-2 / run-3).**

- **Symptom:** Run-1's `phase1-bf-remediation-apply-2026-05-15T13-16-10-070Z.jsonl` captured `certificationRecordId = null` on all 25 success rows.
- **Root cause:** bc-core wraps 2xx responses in `{ data, timestamp }` via `ResponseEnvelopeInterceptor`. The apply script at commit `317c319` read `resp.payload?.record?.certificationRecordId`, one level too shallow. Should have been `resp.payload?.data?.record?.certificationRecordId`.
- **Impact:** Auditing fidelity only. The 25 underlying DB writes were correct and complete (G1–G8 all pass, states certified→certified, action_code correct). PG remains the canonical audit anchor; the run-1 review and final-acceptance packet both source cert_record IDs from PG via `primitive_id + action_code + window` when JSONL has `null`.
- **Fix:** commit `d56fce4` patched the success and error response-extraction paths in `bulk-remediate-bf-semantics.mjs`. Verified in run-2 and run-3: every successful apply row carries a non-null `certificationRecordId` in the JSONL natively.
- **No remediation required.** The DB audit chain is intact end-to-end.

---

## 8. Artifacts

### bc-core commits

| Commit | Subject |
|---|---|
| `c074a2a` | feat: §12 remediation endpoint + service + repo |
| `6a53c5a` | feat: GET suggest-standard-ref + service method |
| `4cdad6a` | chore: read-only OAGIS standard-ref coverage audit script |
| `00a2b59` | feat: Phase 1 BF semantic remediation dry-run script |
| `2a382c7` | chore: deterministic QA sampler |
| `c3d5876` | chore: enriched semantic review packet (generator + packet) |
| `317c319` | feat: implement guarded apply mode for BF remediation |
| `d56fce4` | fix: capture enveloped cert record id in apply audit |
| `b4add0f` | fix: allow staged apply cohort shrinkage |
| `12efe61` | chore: record Phase 1 final acceptance sample |

### bc-docs-v3 commits

| Commit | Subject |
|---|---|
| `b632d72` | docs: SOP for Phase 1 bulk BF semantic remediation |
| `6ee3170` | docs: align Phase 1 BF bulk derivation table with live SDA enum |
| `9160c15` | docs: clarify staged apply drift guard |
| _(this commit)_ | docs: close Phase 1 BF semantic remediation |

### Output artifacts (uncommitted, retained under `bc-core/scripts/audit-output/`)

- Dry-run JSONLs: `phase1-bf-remediation-dry-run-2026-05-15T12-28-16-615Z.jsonl` (initial, 3,804 rows); `phase1-bf-remediation-dry-run-2026-05-15T13-48-13-002Z.jsonl` (refreshed, 3,529 rows).
- Apply JSONLs: `phase1-bf-remediation-apply-2026-05-15T13-16-10-070Z.jsonl` (run-1, 25 rows); `…T13-42-17-090Z.jsonl` (run-2, 250 rows); `…T13-52-58-593Z.jsonl` (run-3, 925 rows).
- Summary CSVs: one per JSONL.
- Enriched semantic-review packet: committed at `c3d5876` (path `scripts/audit-output/phase1-bf-remediation-enriched-semantic-review-seed-20260515.md`).
- Final-acceptance packet: committed at `12efe61` (path `scripts/audit-output/phase1-bf-remediation-final-acceptance-seed-20260515.md`).

### Review helpers (committed)

- `scripts/qa-sample-dry-run-30.mjs` — deterministic dry-run QA sampler (commit `2a382c7`)
- `scripts/review-apply-25.mjs` — apply-window 12-check audit (commit `d56fce4`)
- `scripts/build-phase1-final-acceptance-packet.mjs` — Phase 1 final-acceptance generator (commit `12efe61`)

---

## 9. Backlog (deferred to subsequent phases)

| Phase | Cohort | Approximate count | Gating decision |
|---|---|---:|---|
| **1b** | `Amount` and `Quantity` BFs (`measure-currency` / `measure-count`) | **87** | Requires a unit-resolution playbook: how to pick a currency / count unit per BF without operator-by-operator hand-curation. |
| **2** | Multi-HIGH single-noun ambiguous BFs | **391** | Per-row operator disambiguation; suggest endpoint already returns all candidates with full evidence. |
| **3** | MEDIUM-only candidates (crosswalk + one signal) | **630** | Mandatory spot-rate ≥10%; semantic match weaker; needs hand review. |
| **4** | `suggest_no_candidates` + `deferred_data_shape` + `refused_ambiguous` | **1,492** | Seed enrichment (missing crosswalk rows, nested-complex-type field walks) or operator-authored `standardRef`. |

Combined deferred: **2,600** = 87 + 391 + 630 + 1,492. Add the remaining 4 `refused_ambiguous` (`Number`) and the total reconciles to the live untrusted OAGIS cohort of 2,604.

---

## 10. Recommendation for the next slice

**Recommended next: Phase 2 — multi-HIGH disambiguation (391 BFs).**

Rationale:
- **Highest leverage per row.** Every Phase 2 BF already has a single noun resolved by crosswalk and at least one HIGH-confidence candidate. Operator effort is "pick one of N", not "is this OAGIS noun correct at all".
- **Reuses existing infrastructure.** The `GET /api/business-fields/:fieldId/suggest-standard-ref` endpoint already returns all candidates ranked by confidence. The §12 remediation endpoint is unchanged. The bulk apply script's payload-derivation table is unchanged. The only new artifact is an operator UI or batch CSV that lets a human pick one of the candidates.
- **No SOP rewrite.** The Phase 1 SOP applies almost verbatim. The only substantive change is the cohort filter ("multi-HIGH" instead of "single-HIGH") and the operator-input step before the bulk script runs.
- **No seed work, no enum extension, no playbook authoring.** Phase 1b (`measure-currency` / `measure-count`) requires an entire unit-resolution playbook. Phase 3 (MEDIUM) requires deciding what counts as enough evidence when description-match is absent. Phase 4 requires either seed enrichment (Mongo collection additions) or one-by-one operator authoring. All three are bigger lifts.
- **Closest to "done".** Phase 2's 391 rows are the cheapest path from 1,200 trusted BFs to ~1,591 trusted BFs (33% additional coverage) with minimal new policy.

**Suggested next sub-tasks (do not start yet):**

1. Author Phase 2 SOP as a sibling work-record (`2026-MM-DD-phase2-multi-high-bulk-bf-semantic-remediation-plan-TSK-9515d5.md`). Same shape as Phase 1 SOP; differences:
   - Cohort filter: `suggest_multi_high` instead of `dry_run_ok` from the Phase 1 dry-run output.
   - New required operator-input step: a CSV (or admin-UI flow) that pins one `standardRef` per BF before bulk apply.
   - Same QA ladder (30-row dry-run, 25-row first apply, 250 apply, remainder apply, 50-row final acceptance, ≥49/50 threshold).
2. Decide UI vs CSV authoring. The bc-admin embedded reader is the canonical UI surface (per DEC-b97390 / D372); a "Multi-HIGH disambiguation queue" view would be ergonomic but is a larger build. A CSV round-trip is the cheaper start.
3. Re-use the existing apply script with one new mode (`--from-disambig=<path>`) that reads the operator-chosen `standardRef` per BF instead of deriving from the single HIGH.

**What not to do next.** Phase 4 first (seed enrichment) — it is the biggest lift and would only land 1,492 rows after weeks of seed work; Phase 2's 391 rows can land in a single afternoon once the disambiguation input shape is locked.

---

## 11. Closeout

**Phase 1 SOP §6 final acceptance satisfied (50 / 50, threshold ≥49 / 50).** TSK-9515d5 Phase 1 closed. The remaining 2,604-row OAGIS legacy-cert cohort is the Phase 1b/2/3/4 backlog and is out of scope for this task closure.

---

## Errata / refinement (added 2026-05-15 after Phase 2 packet generation)

**Phase 2 cohort count refined: 391 → 191 under the SOP's frozen-table eligibility filter.**

The bucket figures in §2, §9, and §10 above (`suggest_multi_high: 391`) reflect the raw multi-HIGH bucket from the original coverage audit (bc-core commit `4cdad6a`). When the Phase 2 SOP (`bc-docs-v3/...2026-05-15-phase2-multi-high-bf-semantic-remediation-plan-TSK-9515d5.md`, commit `e809057`) was authored, its §2 rule 5 required Phase 2 candidates to be **frozen-table-eligible** (i.e. their `(representation_term, data_type)` pair must be one of the included rows in the Phase 1 derivation table). That eligibility cut reduces the multi-HIGH bucket from 391 → **191**.

The other ~200 multi-HIGH rows are not lost; they are routed to phases other than Phase 2:

- Multi-HIGH whose `(rt, dt)` pair is `Amount/number` or `Quantity/number` → **Phase 1b** (unit-resolution playbook).
- Multi-HIGH whose `(rt, dt)` pair is `Identifier/code`, `Code/code`, `Indicator/boolean`, `Number/*`, or any other shape outside the frozen table → **Phase 4** (data-shape / seed enrichment / refused-ambiguous).

The Phase 1 facts in §2–§7 of this closeout remain unchanged:
- 1,200 Phase 1 bulk remediations.
- 1,201 `remediate_bf_semantics` rows in DB (1 canary + 1,200 bulk).
- 2,604-row remaining untrusted OAGIS cohort.

Backlog math after this refinement:

| Phase | Cohort (refined) | Approx count |
|---|---|---:|
| Phase 2 (multi-HIGH **and** frozen-table-eligible) | | **191** |
| Phase 1b (Amount/Quantity, unit resolution) | | 87 (+ any multi-HIGH Amount/Quantity rerouted from Phase 2) |
| Phase 3 (MEDIUM-only) | | 630 |
| Phase 4 (no-candidate, data-shape, indicator, refused-ambiguous, plus multi-HIGH frozen-ineligible) | | 1,492 (+ the residual ~200 multi-HIGH frozen-ineligible rows) |
| **Total residual** | | **2,604** (unchanged) |

If Phase 2 closes the full 191-row eligible cohort, cumulative trust is 1,391 of 3,805 OAGIS-cert population; residual backlog becomes **2,413**.

Phase 2 packet generator: bc-core commit `1a2e17d` (`scripts/build-phase2-multi-high-packet.mjs`). Phase 2 packet artifacts: `scripts/audit-output/phase2-multi-high-disambiguation-packet-seed-20260515.md` + `…selection-draft-seed-20260515.jsonl`.

Phase 2 cohort split (run 2026-05-15):
- AI-PICK: **112** (~59%).
- REVIEW (operator must choose): **79** (~41%).
- Validation failures (selectedStandardRef not in candidate set): **0**.
