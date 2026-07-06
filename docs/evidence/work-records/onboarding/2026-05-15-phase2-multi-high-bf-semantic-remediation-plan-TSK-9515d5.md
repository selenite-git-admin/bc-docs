---
title: "Phase 2 multi-HIGH BF semantic remediation — operational SOP"
task: TSK-9515d5
date: 2026-05-15
status: plan
type: sop-plan
authority: DEC-a49413
related:
  - DEC-a49413   # §11 BF SDA-trust predicate; §12 BF semantic remediation
  - DEC-a17d0f   # SDA umbrella authority
  - 2026-05-15-phase1-bulk-bf-semantic-remediation-plan-TSK-9515d5.md
  - 2026-05-15-phase1-bulk-bf-semantic-remediation-closeout-TSK-9515d5.md
---

# Phase 2 Multi-HIGH BF Semantic Remediation — Operational SOP

**Status:** plan, awaiting operator approval.
**Scope:** one-off operational procedure for the multi-HIGH OAGIS legacy BFs that are also frozen-table-eligible (see §2 rule 5). Originally framed as "391 multi-HIGH rows" sourced from the raw audit bucket (commit `4cdad6a`); under §2 the operationally-eligible Phase 2 cohort is **191** rows. The other ~200 multi-HIGH rows are routed to Phase 1b or Phase 4 — see §10 backlog and the errata note in the Phase 1 closeout. Not a contract change. The §12 contract (DEC-a49413 v5) is unchanged. The §12 endpoint, the @PlatformOnly() gate, G1–G8 evaluation, atomic UPDATE+INSERT transaction, and refuse-on-any-failure rule all stay exactly as Phase 1 used them.
**What is different from Phase 1:** the operator (or an AI assist) must **choose exactly one** of multiple HIGH-confidence candidates per BF before any bulk apply. Phase 1 didn't need a chooser because every cohort row had exactly one HIGH candidate.

---

## 1. Authority and scope

| Authority | Reference |
|---|---|
| Decision | **DEC-a49413** §11 (read predicate) and §12 (remediation endpoint) — unchanged |
| Task | **TSK-9515d5** — Phase 2 slice |
| Phase 1 SOP | [2026-05-15-phase1-bulk-bf-semantic-remediation-plan-TSK-9515d5.md](2026-05-15-phase1-bulk-bf-semantic-remediation-plan-TSK-9515d5.md) |
| Phase 1 closeout | [2026-05-15-phase1-bulk-bf-semantic-remediation-closeout-TSK-9515d5.md](../../closeouts/onboarding/2026-05-15-phase1-bulk-bf-semantic-remediation-closeout-TSK-9515d5.md) |

**Operational artifacts reused unchanged from Phase 1:**
- `bc-core/scripts/audit-suggest-standard-ref-coverage.mjs` (commit `4cdad6a`) — defines the cohort funnel and produces the multi-HIGH bucket count.
- `bc-core/src/registry/standard-field.service.ts::suggestStandardRef` (commit `6a53c5a`) — the read-only suggestion path; in Phase 2 we use it to surface **all** HIGH candidates per BF, not just the unique one.
- `bc-core/scripts/bulk-remediate-bf-semantics.mjs` (commits `00a2b59` → `d56fce4` → `b4add0f`) — the §12 caller. Phase 2 reuses every guard (canary assertion, drift guard, per-row §11 recheck, halt criteria, scary banner, JSONL/CSV emit). The only addition is a new flag `--from-selection=<path>` (see §4 below).

**Canary baseline (unchanged):** `invoice_hdr_total_amount` remains §11-trusted with `(measure-currency, currency, OAGIS, https://www.oagidocs.org/docs/invoice-header#total-amount)`. Every Phase 2 run asserts this at start; any drift on the canary aborts before any iteration.

---

## 2. Cohort definition

A BF is in the Phase 2 cohort iff **all** of the following hold:

1. `business_field.status_code = 'certified'`
2. `business_field.definition_standard = 'OAGIS'`
3. No row in `contract.certification_record` with `primitive_type='business_field'`, `primitive_id=field_id`, and `action_code IN ('certify','remediate_bf_semantics')` (no §11 evidence).
4. `suggestStandardRef(fieldId)` returns **two or more** candidates of confidence `high`.
5. The BF's `(representation_term, data_type)` maps to a row in the Phase 1 frozen derivation table (commit `6ee3170`) **other than** the excluded rows (`Amount`, `Quantity`, `Number`). The same Phase 1 family/unit mapping applies; we do not change the derivation table for Phase 2.
6. The projected G1–G8 replay passes with that derivation under at least one of the HIGH candidates' `standardRef`.

**Indicative size.**
- Raw multi-HIGH bucket from the Phase 1 audit on 2026-05-15 (commit `4cdad6a`): 391 rows.
- After applying rule 5 (frozen-table-eligibility), the **operationally-eligible Phase 2 cohort is 191 rows** (run of bc-core commit `1a2e17d` on 2026-05-15).
- AI-PICK rows: 112 (~59%). REVIEW rows: 79 (~41%). Validation failures: 0.
- The ~200 multi-HIGH rows excluded by rule 5 are routed to Phase 1b (Amount/Quantity unit resolution) or Phase 4 (data-shape, Indicator, Number, other excluded patterns) — see §10.

**Explicit exclusions (will NOT enter Phase 2):**
- MEDIUM-only candidates → Phase 3.
- No-candidate rows → Phase 4.
- `deferred_data_shape` (Identifier/Code with `data_type='code'`) → Phase 4.
- `Amount` / `Quantity` (`measure-currency`, `measure-count`) → Phase 1b.
- `Number` representation term → refused.
- Any BF that gained §11 evidence between cohort audit and apply (handled by per-row §11 recheck).

---

## 3. Disambiguation source

Each Phase 2 BF has **>1 HIGH-confidence candidate** from `suggestStandardRef`. A HIGH candidate is `crosswalk + descriptionMatch + (propertyMatch OR derivedBfNameMatch)`. Multi-HIGH means the same `bf_name` / `property` / `description` byte-identically matches a field in more than one OAGIS component under the same noun — most commonly header vs line variants (`invoice-header` + `invoice-line`), or related sub-component pairs.

**Hard rule.** The operator (or AI assist) picks **exactly one** of the row's HIGH candidates. The selected `standardRef` is the one written by the §12 endpoint. **No fabricated refs.** The selection script must refuse any `standardRef` that is not byte-identical to one of the row's HIGH candidates as enumerated by the suggestion service at packet-generation time.

**AI-assist heuristic (binding for "AI-selected" rows in the review packet):**

| Signal | AI recommendation |
|---|---|
| Exactly one HIGH candidate has `descriptionMatch=true` **and** the others have `descriptionMatch=false` | **PICK** that candidate |
| Exactly one HIGH candidate has both `propertyMatch=true` and `derivedBfNameMatch=true` while others have only one | **PICK** that candidate |
| Header-vs-line ambiguity and the BF name carries `_hdr_` / `_line_` / `_dtl_` infix that disambiguates by convention | **PICK** the candidate whose `componentSlug` matches the infix |
| Multiple HIGH candidates with identical evidence signatures across all flags | **REVIEW** — operator must choose; no AI default |
| Any candidate's standardRef base does not match its component `source_url` in the local OAGIS scrape archive (`barecount-devhub/data/oagis-finance-extract.json`) | **REVIEW** — flag for source corroboration |

Multi-attempt heuristics are conjunctive: the script applies them in order and emits `ai_recommendation = "pick:{idx}"` or `ai_recommendation = "review"`. The packet records all signals so the operator can override any AI pick.

**No live oagidocs.org dependency.** Like Phase 1, every "evidence" check uses local sources: PG `business_field`, Mongo `bc_seed.seed_oagis_components` + `seed_bo_crosswalk`, and the raw scrape archive in `barecount-devhub/data/`.

---

## 4. Review packet and selection file

### Review packet (operator artifact)

One Markdown block per BF, generated by a new read-only helper `bc-core/scripts/build-phase2-disambiguation-packet.mjs` (to be authored next). Each block contains:

- **BF block.** `fieldId`, `name`, `objectClass`, `property`, `representationTerm`, `dataType`, `definition` (from PG `business_field`).
- **Derived payload.** `proposed.semanticFamily`, `proposed.unitTypeCode`, `proposed.definitionStandard='OAGIS'` — these are constant across all HIGH candidates of the same BF; only `standardRef` varies.
- **Candidates table.** One row per HIGH candidate with: `idx`, `noun`, `componentSlug`, `fieldSlug`, `componentSourceUrl`, `sourceVersion`, `standardRef`, `descriptionMatch`, `propertyMatch`, `derivedBfNameMatch`, `crosswalkMatch`.
- **AI recommendation.** Either `pick:{idx}` with a one-sentence rationale or `review` with the conflict description.
- **Operator selection line.** A `selection: pick:{idx}` field the operator fills in by editing the packet (or the operator drops the row to skip).

The packet is produced once and archived under `bc-core/scripts/audit-output/`. The same deterministic seed (Phase 1 default `20260515`) governs any sample reviews.

### Selection file (script input)

The bulk script accepts a new flag: `--from-selection=<path>` (replaces `--from-dryrun=<path>` for Phase 2 invocations; both are mutually exclusive within a single run).

**Shape: JSONL, one row per BF to apply.**

```json
{
  "fieldId": "019d6dcc-...",
  "name": "invoice_hdr_total_amount_basis_amount",
  "selectedStandardRef": "https://www.oagidocs.org/docs/invoice-header#total-amount-basis-amount",
  "selectedCandidate": {
    "idx": 1,
    "componentSlug": "invoice-header",
    "fieldSlug": "total-amount-basis-amount"
  },
  "selector": "ai" | "operator",
  "selectorNote": "<optional rationale>"
}
```

**Validation rules enforced by the script (refuse before any POST):**
1. Selection file must exist and be valid JSONL with all required fields.
2. Every `fieldId` must be in the current live Phase 2 cohort (status='certified' + OAGIS + no §11 + multi-HIGH + frozen-table-eligible).
3. The script re-runs `suggestStandardRef` for each `fieldId` and asserts the selected `standardRef` is byte-identical to one of the HIGH candidates returned. If it doesn't match → refuse with `result='selection_not_in_candidates'`, halt the row, continue accumulating violations and refuse the run.
4. The selected `componentSlug` and `fieldSlug` must match the chosen `standardRef` (`https://www.oagidocs.org/docs/{componentSlug}#{fieldSlug}`).
5. No fabricated refs: if `selectedStandardRef` is null, empty, or not on `oagidocs.org`, the row is rejected.
6. Duplicate `fieldId` entries → reject the file.

**The selection file is forensic evidence.** It is retained for 90 days under `bc-core/scripts/audit-output/phase2-selections/` alongside JSONL/CSV outputs from the runs that consumed it.

---

## 5. Dry-run mode (read-only)

`node scripts/bulk-remediate-bf-semantics.mjs --mode=dry-run --from-selection=<path>`

For each BF in the selection file:
1. Load BF from PG (full row).
2. Confirm BF is still in the live Phase 2 cohort (cohort criteria as in §2).
3. Re-run `suggestStandardRef` and validate the selected `standardRef` is among the HIGH candidates (validation rules §4).
4. Derive payload: `semanticFamily` + `unitTypeCode` from the Phase 1 frozen table; `definitionStandard='OAGIS'`; `standardRef` from the selection.
5. Replay projected G1–G8 locally with the proposed payload.
6. Emit one JSONL row per BF: `before`, `proposed`, `provenance` (the chosen candidate's evidence), `dryRunGates`, `mode='dry-run'`, `result ∈ {dry_run_ok, selection_not_in_candidates, cohort_drift, projected_gate_failed, no_derivation_rule, …}`.
7. Summary CSV at end with per-result counts.

No POSTs. No writes. Output to `scripts/audit-output/phase2-bf-remediation-dry-run-{ts}.jsonl` and matching `.summary.csv`.

---

## 6. Apply mode

`node scripts/bulk-remediate-bf-semantics.mjs --mode=apply --from-selection=<path>`

**Required env (refuse before any POST if missing — same gates as Phase 1):**
- `PHASE2_MAX_APPLY` — positive integer (replaces `PHASE1_MAX_APPLY`; the script accepts both, the active one is picked by mode).
- `BC_CORE_BEARER_TOKEN` — Cognito platform-admin JWT.

**Required argument:**
- `--from-selection=<path>` to a fresh dry-run-validated selection file (same JSONL the dry-run consumed).

**Drift guard (shrinkage-tolerant, same semantics as Phase 1 commit `b4add0f`):**
- Compare live Phase 2 cohort fieldIds against the selection-file fieldIds.
- **Block on EXPANSION** — any live cohort fieldId not in the selection file is an unreviewed candidate; refuse. (Operator must regenerate the selection packet to include or explicitly exclude the new candidates.)
- **Allow SHRINKAGE** — selection-file fieldIds missing from the live cohort are tolerated (they may have gained §11 trust via an independent path, or status changed).

**Per-row apply flow:**
1. Re-check §11 evidence; if trusted, skip with `result='already_trusted'`.
2. Re-derive payload from selection + frozen table.
3. Local G1–G8 replay; halt on disagreement (`result='local_gate_failed'`).
4. POST `${BC_CORE_BASE_URL}/api/business-fields/:fieldId/remediate-semantics`. No service shortcut.
5. Record JSONL line with the resolved `certificationRecordId` from the response envelope (fix `d56fce4`).

**Concurrency:** 1 (sequential).
**Halt criteria (SOP §7 carried forward):** 3 consecutive 5xx; 5 consecutive identical 422; p50 latency > 2 s over 50-row rolling window.
**Stop criterion:** `PHASE2_MAX_APPLY` successful applies. Cap counts successes only, matching Phase 1 rule 12.

---

## 7. QA / acceptance ladder

### Pre-apply (mandatory)

- **AI-selected rows.** Operator reviews **30 random AI-selected** rows from the disambiguation packet. Each pick is justified by the AI heuristic stated above; operator confirms semantic fit by opening the chosen `standardRef` (or its local scrape evidence) and rejecting any mismatch. Threshold: **30/30**.
- **REVIEW rows (no AI default).** Operator reviews **100%** of REVIEW-marked rows — no AI shortcut. Operator picks one HIGH candidate per row and writes it into the selection file.
- Dry-run must produce all selected rows as `result='dry_run_ok'` (no `selection_not_in_candidates`, no `projected_gate_failed`). Any other result halts before apply.

### Run cadence (cap 25 → 100 → remainder)

Phase 2 cohort is smaller than Phase 1 (191 eligible vs 1,200); the cadence adjusts:

| Step | `PHASE2_MAX_APPLY` | Operator action between steps |
|---|---:|---|
| Apply 25 | 25 | Review **100% of JSONL output** (25 rows); confirm `certificationRecordId` non-null on every line; PG spot-read 2 cert_records |
| Apply 100 | 100 | Sample 30 random successes; semantic spot-check; **acceptance ≥ 29/30** |
| Apply remainder | unbounded | Final remainder (~66 rows expected at 191-row eligibility; exact number depends on shrinkage between runs) |
| Final acceptance | n=50 (deterministic seed) | **≥ 49/50** PASS required (same threshold as Phase 1) |

The 50-row final acceptance follows the Phase 1 packet shape (`scripts/build-phase1-final-acceptance-packet.mjs` adapted for Phase 2 JSONLs). The same twelve checks per row apply, plus:
- **C13 selection-fidelity.** Sampled row's PG `standard_ref` matches the selection-file `selectedStandardRef` byte-identically. Confirms the operator's chosen candidate was the one written.

### Canary assertion

Every Phase 2 run asserts the canary baseline on the SAME `invoice_hdr_total_amount` row (still §11-trusted, still expected family/unit/ref). Any drift aborts before iteration.

---

## 8. Rollback / correction

**Forward-only correction.** Same posture as Phase 1.

- A wrong row stays as a recorded `remediate_bf_semantics` ledger entry. The §11 trust predicate is satisfied by ANY matching ledger row.
- Correction = a **second** `remediate_bf_semantics` call against the same BF with a corrected `standardRef`. Overwrites the four columns; appends a new cert_record. Audit trail gains a second row.
- **No `withdraw_bf_semantics` action in Phase 2.** The `certification_record.action_code` CHECK constraint stays unchanged. A withdraw action would be a future DBCP under its own ADR; do not pre-build.

**Snapshot strategy.** Operator takes `pg_dump --schema=contract --table=business_field --table=certification_record` immediately before each apply run (3 snapshots: pre-25, pre-100, pre-remainder). Retain 90 days. Restore is break-glass DBCP only.

**Halt criteria.** Same as Phase 1; consecutive-5xx, consecutive-identical-422, p50-latency thresholds. Plus a new Phase-2-specific halt:
- **3 consecutive `selection_not_in_candidates` rows** (suggests a stale selection file vs current live cohort + suggestions) → halt and ask operator to regenerate the disambiguation packet.

---

## 9. Hard boundaries (restated)

- ❌ **No metric promotion** in this phase.
- ❌ **No CF row changes.**
- ❌ **No direct SQL writes.** Every column change goes through the §12 endpoint.
- ❌ **No MEDIUM, LOW, no-candidate rows** in the cohort.
- ❌ **No `measure-currency` / `measure-count` / `Number`** rows.
- ❌ **No fabricated standardRefs.** Every selected ref must be byte-identical to one of the row's HIGH candidates as returned by `suggestStandardRef`.
- ❌ **No override path.** Any single G1–G8 failure refuses the row.
- ❌ **No tenant DB touches.**
- ❌ **No live oagidocs.org dependency.** All evidence local (PG + Mongo seed + raw scrape archive).
- ❌ **No service shortcut.** All writes route through `POST /api/business-fields/:fieldId/remediate-semantics` and inherit @PlatformOnly auth, atomic UPDATE+INSERT, and inline G1–G8.

---

## 10. Backlog after Phase 2

| Phase | Cohort | Approx count | Notes |
|---|---|---:|---|
| **1b** | `Amount` / `Quantity` BFs (`measure-currency` / `measure-count`) | 87 | Requires unit-resolution playbook; deferred. |
| **3** | MEDIUM-only candidates | 630 | Mandatory spot-rate ≥10%; weaker semantic match. |
| **4** | `suggest_no_candidates` + `deferred_data_shape` + `refused_ambiguous` | 1,492 | Seed enrichment or operator-authored refs. |

Phase 2 alone closes **191 / 2,604** of the residual untrusted OAGIS cohort (~7.3%). Cumulative Phase 1 + Phase 2 trusted BFs would be **1,391** out of an original 3,805 (canary + audit population), leaving **2,413** in Phase 1b/3/4 backlog. The ~200 multi-HIGH rows that did not qualify under §2 rule 5 remain in the Phase 1b / Phase 4 backlogs and are accounted for in those phases.

---

## 11. Next artifact

Implementation slices, deferred until this SOP is approved:

1. **Disambiguation packet generator** — `bc-core/scripts/build-phase2-disambiguation-packet.mjs` (read-only). Loads cohort, runs `suggestStandardRef` per BF, builds the per-BF block with AI recommendation, writes Markdown packet under `scripts/audit-output/`.
2. **Apply script extension** — single new flag `--from-selection=<path>` in `bulk-remediate-bf-semantics.mjs`; minimal addition to drift guard, dry-run path, and apply path that handles selection-file validation + selection-vs-candidate verification. No new endpoints; reuses `POST /api/business-fields/:fieldId/remediate-semantics`.
3. **Final-acceptance generator** — `bc-core/scripts/build-phase2-final-acceptance-packet.mjs` adapted from the Phase 1 helper. Adds C13 selection-fidelity check.

Authoring deferred until operator approval of this SOP.

---

## 12. Cross-references

- `bc-docs-v3/docs/adrs/ADR-a49413.md` §11, §12 (unchanged)
- `bc-docs-v3/docs/adrs/ADR-a17d0f.md` (SDA umbrella)
- `bc-core/scripts/bulk-remediate-bf-semantics.mjs` (commits `00a2b59` → `b4add0f`)
- `bc-core/scripts/audit-suggest-standard-ref-coverage.mjs` (commit `4cdad6a`)
- `bc-core/src/registry/standard-field.service.ts::suggestStandardRef` (commit `6a53c5a`)
- Phase 1 SOP: `2026-05-15-phase1-bulk-bf-semantic-remediation-plan-TSK-9515d5.md`
- Phase 1 closeout: `2026-05-15-phase1-bulk-bf-semantic-remediation-closeout-TSK-9515d5.md`
- Canary record: SES-594568, BF `invoice_hdr_total_amount`
- Phase 2 packet generator + draft selection: bc-core commit `1a2e17d` (`scripts/build-phase2-multi-high-packet.mjs` + `scripts/audit-output/phase2-multi-high-disambiguation-packet-seed-20260515.md` + `…selection-draft-seed-20260515.jsonl`)

---

## Errata / refinement (added 2026-05-15 after packet generation)

The phrase "391 multi-HIGH" used in this SOP's earlier wording (now patched) referred to the raw multi-HIGH bucket from the original coverage audit (bc-core commit `4cdad6a`). When the eligibility predicate in §2 rule 5 (frozen-table-eligible (`representation_term`, `data_type`) pair) is applied, the operational Phase 2 cohort is **191 rows**, not 391. The packet generator (`1a2e17d`) reports the funnel:

```
live OAGIS no-§11 cohort:               2,604
frozen-table-ineligible (filtered out): 1,128
non-multi-HIGH (filtered out):          1,285
Phase 2 multi-HIGH cohort:                191
  AI PICK:                                112
  REVIEW (operator must choose):           79
```

The ~200 multi-HIGH rows excluded by §2 rule 5 are not lost; they're routed to the appropriate downstream phase:

- Multi-HIGH whose `(rt, dt)` is `Amount/number` or `Quantity/number` → **Phase 1b** (unit-resolution playbook).
- Multi-HIGH whose `(rt, dt)` is `Identifier/code`, `Code/code`, `Indicator/boolean`, `Number/*`, or any other shape outside the frozen table → **Phase 4** (data-shape / seed enrichment / refused-ambiguous).

Backlog math (refined):
- Phase 2 closes 191 / 2,604 = ~7.3% of the residual OAGIS untrusted cohort.
- Cumulative Phase 1 + Phase 2 trusted (on full Phase 2 completion) = **1,391** of 3,805.
- Residual after Phase 2 = **2,413** in Phase 1b/3/4 backlogs.

Run cadence unchanged in shape; the "remainder" step lands ~66 rows instead of the earlier estimate of ~266.
