---
title: "Phase 3 MEDIUM-only BF semantic remediation — operational SOP"
task: TSK-9515d5
date: 2026-05-15
status: plan
type: sop-plan
authority: DEC-a49413
related:
  - DEC-a49413   # §11 BF SDA-trust predicate; §12 BF semantic remediation
  - DEC-a17d0f   # SDA umbrella authority
  - 2026-05-15-phase1-bulk-bf-semantic-remediation-plan-TSK-9515d5.md
  - 2026-05-15-phase2-multi-high-bf-semantic-remediation-plan-TSK-9515d5.md
  - 2026-05-15-phase2-multi-high-bf-semantic-remediation-closeout-TSK-9515d5.md
---

# Phase 3 MEDIUM-only BF Semantic Remediation — Operational SOP

**Status:** plan, awaiting operator approval and a fresh read-only cohort count before any implementation.

**Scope:** one-off operational procedure for OAGIS legacy-certified BFs whose `suggestStandardRef` returns one or more MEDIUM-confidence candidates **and no HIGH candidate**. Not a contract change. The §12 contract (DEC-a49413 v5) is unchanged. The §12 endpoint, atomic UPDATE+INSERT transaction, G1–G8 evaluation, and refuse-on-any-failure rule all stay exactly as Phase 1 and Phase 2 used them.

**Substantive design difference vs Phase 2.** Phase 2 disambiguated between *multiple HIGH* candidates whose evidence agreed across description + property + derivedBfName. Phase 3 deals with the *weaker* evidence band: a MEDIUM candidate has either (a) description byte-identical but no name signals (`MEDIUM-D`) or (b) property/derivedBfName matches but no byte-identical description (`MEDIUM-NS`). Both sub-flavours need explicit operator/AI review before the selection enters apply; the AI cannot auto-PICK on a single signal.

---

## 1. Authority and scope

| Authority | Reference |
|---|---|
| Decision | **DEC-a49413** §11 (read predicate) and §12 (remediation endpoint) — unchanged |
| Task | **TSK-9515d5** — Phase 3 slice |
| Phase 1 SOP / closeout | filed 2026-05-15, frozen derivation table reused verbatim |
| Phase 2 SOP / closeout | filed 2026-05-15 (commits `e809057` / `19705e2` / `3e5d507`); operator-disambiguation pipeline reused with minor changes |

**Operational artifacts reused unchanged from Phase 1 / Phase 2:**
- `bc-core/scripts/audit-suggest-standard-ref-coverage.mjs` (commit `4cdad6a`) — produces the MEDIUM bucket count.
- `bc-core/src/registry/standard-field.service.ts::suggestStandardRef` (commit `6a53c5a`) — read-only; returns all confidence bands.
- `bc-core/scripts/bulk-remediate-bf-semantics.mjs` (chain ending at `b2f8bfd`) — the §12 caller. Phase 3 reuses every guard (canary assertion, drift guard, per-row §11 recheck, halt criteria, scary banner, JSONL/CSV emit) and the `--from-selection` flow. **The script's selection validator does NOT gate on `confidence='high'`** (verified in code at apply time); a selection-file entry only needs to be byte-identical to one of the row's *current candidates* as returned by `suggestStandardRef` regardless of band. The script's current behaviour is the design intent for Phase 3.

**Canary baseline (unchanged):** `invoice_hdr_total_amount` remains §11-trusted with `(measure-currency, currency, OAGIS, https://www.oagidocs.org/docs/invoice-header#total-amount)`. Every Phase 3 run asserts this at start.

---

## 2. Cohort definition

A BF is in the Phase 3 cohort iff **all** of the following hold:

1. `business_field.status_code = 'certified'`
2. `business_field.definition_standard = 'OAGIS'`
3. No row in `contract.certification_record` with `primitive_type='business_field'`, `primitive_id=field_id`, and `action_code IN ('certify','remediate_bf_semantics')` (no §11 evidence).
4. `suggestStandardRef(fieldId)` returns **zero HIGH** candidates **and at least one MEDIUM** candidate.
5. The BF's `(representation_term, data_type)` pair is in the Phase 1 frozen derivation table (commits `6ee3170` for the SOP, `12efe61` for the implementation pass).
6. The projected G1–G8 replay passes with the operator-selected MEDIUM candidate's `standardRef`.

**Indicative size.** From the original Phase 1 audit (commit `4cdad6a`): 630 rows in the `suggest_only_medium_or_low` bucket. Phase 1 and Phase 2 did not touch any of these rows. After applying rule 5 (frozen-table-eligibility), the operationally-eligible Phase 3 cohort will be ≤ 630; the implementation script must produce a fresh count before any apply. **Authoring assumes "approximately 600" as a planning placeholder; the actual number is recomputed at runtime.**

**Explicit exclusions (will NOT enter Phase 3):**
- Rows that gained §11 evidence (Phase 1, Phase 2, or independent certification path) → handled by rule 3 + per-row §11 recheck.
- HIGH-candidate rows — those belonged to Phase 1 (single-HIGH) or Phase 2 (multi-HIGH).
- LOW-only rows (description-only without crosswalk, or noun-level only) → Phase 4.
- `deferred_data_shape` (Identifier/Code with `data_type='code'`) → Phase 4.
- `Amount` / `Quantity` (`measure-currency`, `measure-count`) → Phase 1b.
- `Indicator/boolean`, `Number/*` → Phase 4.
- Any BF whose locally-replayed G1–G8 predicts a failure.

---

## 3. Evidence model

A MEDIUM candidate satisfies one of two sub-shapes; the SOP treats them as separate review buckets because their operator-review burden differs.

| Sub-shape | crosswalk | descriptionMatch | propertyMatch / derivedBfNameMatch | Operator review burden |
|---|:---:|:---:|:---:|---|
| **MEDIUM-D** (description-only) | ✓ | ✓ | ✗ on both | Lower — BF definition is byte-identical to OAGIS field description, but the OAGIS bf_name doesn't match the BF property or derivedBfName. Likely a rename/translation on one side. Operator confirms semantic alignment by reading the definition. |
| **MEDIUM-NS** (name-signal-only) | ✓ | ✗ | ✓ on at least one | Higher — the BF property or derived BF name matches an OAGIS bf_name, but the descriptions are NOT byte-identical. Could be a true semantic match with reworded definitions, OR an overloaded name that means something else in OAGIS. Operator reads both definitions and judges. |

Every Phase 3 candidate row must carry these explicit evidence fields in the disambiguation packet and selection file:

- `evidence.crosswalkMatch` (always `true` by cohort definition).
- `evidence.descriptionMatch` (boolean — sub-shape selector).
- `evidence.propertyMatch` (boolean).
- `evidence.derivedBfNameMatch` (boolean).
- `evidence.subShape ∈ {MEDIUM-D, MEDIUM-NS}` — derived from the three booleans above; emitted explicitly for fast operator triage.
- `evidence.scrapeCorroboration` — `{noun: bool, component: bool, field: bool, source_url_match: bool}` against the local OAGIS scrape archive.
- For MEDIUM-NS rows: `evidence.descriptionsDiffer` — first 240 chars of BF definition + first 240 chars of OAGIS field description, side by side, in the packet (markdown table cells; no live fetch).

**No fabricated refs.** Every selected `standardRef` must be byte-identical to a `standardRef` returned by `suggestStandardRef` at packet-generation time AND at apply time.

**No live oagidocs.org dependency.** Like Phase 1 / Phase 2, all evidence is local: PG `business_field`, Mongo `bc_seed.seed_oagis_components` + `seed_bo_crosswalk`, raw scrape archive `barecount-devhub/data/oagis-finance-extract.json`.

---

## 4. Selection and review

### Workflow

1. **Cohort + packet generation** — `bc-core/scripts/build-phase3-medium-packet.mjs` (to be authored). Loads cohort per §2, runs `suggestStandardRef`, filters to rows with zero HIGH + ≥1 MEDIUM, classifies each candidate as MEDIUM-D or MEDIUM-NS, emits Markdown packet + AI-draft JSONL.

2. **AI proposal — restricted vs Phase 2.** The AI may propose a candidate only when **all four** of the following hold:
   - Exactly one MEDIUM candidate exists for the BF (single-MEDIUM); **or** multi-MEDIUM with operator-resolvable disambiguation per the rules below.
   - The candidate is scrape-corroborated (noun + component + field + source_url all present in the local archive).
   - Sub-shape is MEDIUM-D (description-match alone) **or** sub-shape is MEDIUM-NS with the BF property string appearing verbatim in the OAGIS field description (substring check), which is a weaker but non-trivial semantic alignment signal.
   - Frozen-table derivation produces a valid (family, unit) pair.

   Any other case → REVIEW (operator chooses). **There is no auto-PICK based on a single signal alone.**

3. **Multi-MEDIUM disambiguation (when 2 or more MEDIUM candidates per BF).** Apply Phase 2 secondary heuristics:
   - R1 — objectClass suffix `_hdr` / `_line` / `_dtl` / `_item` / `_party` → component token.
   - R3 — component root equals objectClass kebab.
   - R4/R5 — component root prefix-of / inside BF name kebab.
   - First decisive rule wins. Ties → REVIEW.

4. **Operator review** — operator opens the packet, reads each REVIEW row's BF definition + OAGIS field description (when MEDIUM-NS) or the renamed-property context (when MEDIUM-D), and either fills in a `selection: pick:{idx}` line per BF or drops the row (defers to Phase 4 with reason `phase3_review_declined`).

### Selection file shape (`--from-selection=<path>`)

Same envelope as Phase 2 with one new field:

```json
{
  "fieldId": "019d6dcc-...",
  "name": "<bf name>",
  "selectedStandardRef": "https://www.oagidocs.org/docs/<comp>#<field>",
  "selectedCandidate": {
    "idx": 0,
    "componentSlug": "...",
    "fieldSlug": "...",
    "subShape": "MEDIUM-D" | "MEDIUM-NS"
  },
  "selector": "ai_review_medium" | "operator_review",
  "selectorNote": "<rationale string>",
  "semanticFamily": "...",
  "unitTypeCode": "..." | null
}
```

**Script validation rules (refuse before any POST):**
1. Every `fieldId` is in the current live Phase 3 cohort (cohort criteria as in §2).
2. The selected `standardRef` is byte-identical to a `standardRef` returned by `suggestStandardRef` at apply time. (The script does not require the candidate's confidence band to be HIGH; MEDIUM is accepted by design.)
3. The `selectedCandidate.subShape` must match the candidate's actual evidence at apply time (re-derived from `descriptionMatch` / `propertyMatch` / `derivedBfNameMatch`); if it drifted, refuse with `selection_subshape_drift`.
4. The frozen-table derivation at apply time matches the selection's `semanticFamily` and `unitTypeCode`; else refuse with `selection_stale_derivation`.
5. `selector` must be one of `ai_review_medium` or `operator_review`; no other value accepted.
6. No fabricated refs: the selected ref must point at `oagidocs.org` and follow `https://www.oagidocs.org/docs/{componentSlug}#{fieldSlug}`.
7. Duplicate `fieldId` entries → reject the file.

---

## 5. Dry-run mode (read-only)

`node scripts/bulk-remediate-bf-semantics.mjs --mode=dry-run --from-selection=<path>`

For each selected BF:
1. Confirm still in the live Phase 3 cohort.
2. Re-run `suggestStandardRef`; validate selected ref is byte-identical to one current candidate. Validate sub-shape matches.
3. Derive (family, unit) from frozen table; compare to selection.
4. Replay G1–G8 locally.
5. Emit one JSONL row: `before`, `proposed`, `provenance` (MEDIUM sub-shape evidence), `dryRunGates`, `result ∈ {dry_run_ok, selection_not_in_candidates, selection_subshape_drift, selection_stale_derivation, no_longer_live, projected_gate_failed, no_derivation_rule}`, `phase='phase3'`.

No POSTs. No writes. Output to `scripts/audit-output/phase3-bf-remediation-dry-run-{ts}.jsonl` and matching `.summary.csv`.

---

## 6. Apply cadence

**Concurrency:** 1 (sequential).
**Env:** `PHASE3_MAX_APPLY` (positive integer) — distinct from `PHASE1_MAX_APPLY` and `PHASE2_MAX_APPLY` (one MAX env per phase, no reuse). The bulk script will pick the right env based on the presence of `--from-selection` + the dry-run JSONL's `phase` field; **the script needs one tiny change to read `PHASE3_MAX_APPLY` when the dry-run JSONL declares `phase='phase3'`** (Phase 2 currently hardcodes `PHASE2_MAX_APPLY`).
**Required:** `--from-selection=<path>` AND `--from-dryrun=<phase3 dry-run JSONL>`. Selection-only invocation refuses, same as Phase 2.

### Run cadence

Phase 1/2 saw zero apply failures across 1,391 rows. Phase 3's evidence band is weaker but the apply path is the same governed §12 endpoint; the latency profile and error envelope should match. The SOP allows **larger batches** than Phase 2's `25 → 100 → remainder` cadence:

| Step | `PHASE3_MAX_APPLY` | Operator action between steps |
|---|---:|---|
| Dry-run (full pool) | (n/a) | 30-row sample review pre-apply; 30/30 required to proceed |
| Apply 100 (run 1) | 100 | Review **30 random successes** + every non-success line; **acceptance ≥ 29/30** plus all non-success lines explained |
| Apply remainder (run 2) | unbounded (or explicit cap) | Final 50-row acceptance sample, threshold ≥49/50 |

If run-1 surfaces any unexpected `endpoint_422`, `endpoint_5xx`, `selection_not_in_candidates`, `selection_subshape_drift`, or `local_gate_failed`, **revert to the Phase 2 cadence** for the remainder (250 cap with intermediate review). The cadence relaxation is contingent on Phase 1/2's zero-failure posture continuing into Phase 3; the operator may demand a stricter cadence at any time without SOP amendment.

### Drift guard (shrinkage-tolerant — unchanged from Phase 2)

Reports six counts before any POST: selections / dry-run rows / dry_run_ok in dry-run / live selected / shrunk (no longer live, allowed) / unexpected additions (block) / non-dry_run_ok in dry-run (block). Block on EXPANSION or any selected row whose dry-run result wasn't `dry_run_ok`. Allow SHRINKAGE.

### Halt criteria

Same as Phase 1/2 plus the Phase-2-specific consecutive-selection halt:
- 3 consecutive 5xx
- 5 consecutive identical 422
- p50 latency > 2s over 50-row rolling window
- 3 consecutive `selection_not_in_candidates`
- **New for Phase 3:** 3 consecutive `selection_subshape_drift` (selection file is stale on sub-shape labelling).

---

## 7. QA / acceptance

### Pre-apply (mandatory)

- Operator reviews **100% of the AI-proposed selection file** (PICK rows only). Phase 3 is the first slice where AI proposals are not strictly "single decisive signal" — every AI-PICK requires an explicit operator confirmation pass.
- Operator reviews **100% of REVIEW-flagged rows** (no AI default) and writes selections manually or defers.
- Dry-run must produce all selected rows as `result='dry_run_ok'`. Any other result halts before apply.
- **30-row pre-apply spot-check from the AI-PICK pool: 30 / 30 required** (matches Phase 1/2 pre-apply threshold).

### Run cadence

| Step | Cap | Operator action |
|---|---:|---|
| Apply 100 (run 1) | 100 | Review 30 random successes; every non-success line explained; **acceptance ≥ 29/30** of the 30-sample |
| Apply remainder (run 2) | unbounded | Final 50-row sample, threshold **≥ 49/50** |

### Final acceptance sample

50-row deterministic sample (seed `20260515`) across both Phase 3 apply JSONLs, with the same 13 checks as Phase 1 + Phase 2's C13 selection-fidelity, plus a 14th Phase 3-specific check:

- **C14 — sub-shape fidelity.** The cert_record's `gate_results_json` evidence stamp (if present) matches the sub-shape recorded in the selection. If not present (e.g. the endpoint doesn't emit sub-shape), this check is informational only and does not count toward pass/fail.

Acceptance threshold: ≥ 49/50 PASS. Below threshold → halt and file defect; do not proceed.

### Canary assertion

Every Phase 3 run asserts `invoice_hdr_total_amount`'s §11 trust at start. Any drift aborts before iteration.

---

## 8. Hard boundaries (restated)

- ❌ **No metric promotion** in this phase.
- ❌ **No CF row changes.**
- ❌ **No direct SQL writes.** Every column change goes through the §12 endpoint.
- ❌ **No live oagidocs.org dependency.** All evidence local.
- ❌ **No override path.** Any single G1–G8 failure refuses the row.
- ❌ **No HIGH-candidate rows** in the Phase 3 cohort (Phase 1/2 territory).
- ❌ **No LOW-only / no-candidate / data-shape / Amount/Quantity / Indicator / Number rows.**
- ❌ **No tenant DB touches.**
- ❌ **No fabricated standardRefs.** Every selection must be byte-identical to a `suggestStandardRef` candidate at packet generation AND at apply time.
- ❌ **No service shortcut.** All writes route through `POST /api/business-fields/:fieldId/remediate-semantics` and inherit @PlatformOnly auth, atomic UPDATE+INSERT, and inline G1–G8.

---

## 9. Rollback / correction

**Forward-only correction.** Same posture as Phase 1 and Phase 2.

- A wrong row stays as a recorded `remediate_bf_semantics` ledger entry. The §11 trust predicate is satisfied by ANY matching ledger row.
- Correction = a **second** `remediate_bf_semantics` call with a corrected `standardRef`. Overwrites the four columns; appends a new cert_record. Audit trail gains a second row.
- **No `withdraw_bf_semantics` action in Phase 3.** The `certification_record.action_code` CHECK constraint stays unchanged.

**Snapshot strategy.** Operator takes `pg_dump --schema=contract --table=business_field --table=certification_record` immediately before each apply run (2 snapshots: pre-100, pre-remainder). Retain 90 days. Restore is break-glass DBCP only.

---

## 10. Residual backlog after Phase 3

(Implementation-time recompute required; planning placeholders here.)

| Phase | Cohort | Approx count after Phase 3 closes |
|---|---|---:|
| Phase 1b | Amount / Quantity (unit-resolution playbook required) | 87 |
| Phase 4 | no-candidate + data-shape + Indicator/boolean + Number + multi-HIGH frozen-ineligible | 1,696 (or ~ that after Phase 3 closes its share of the original 630) |
| **Total residual** | | **≈ 1,783** |

If Phase 3 closes its full eligible cohort (planning placeholder ≈ 600), cumulative trust would be **≈ 1,992 of 3,805 (~52%)**. Final residual would then sit at ~1,813 across Phase 1b and Phase 4 (the difference is the ~13 multi-MEDIUM-but-frozen-ineligible rows the Phase 3 cohort filter excludes; they land in Phase 4 like the multi-HIGH frozen-ineligibles did in Phase 2).

The implementation script must recompute these numbers and emit a refreshed funnel in the Phase 3 packet output, mirroring the funnel block at the top of the Phase 2 disambiguation packet.

---

## 11. Next artifact

Implementation slices, deferred until this SOP is approved:

1. **Phase 3 packet generator** — `bc-core/scripts/build-phase3-medium-packet.mjs` (read-only). Loads cohort, classifies each MEDIUM candidate as MEDIUM-D / MEDIUM-NS, generates the side-by-side definition view for MEDIUM-NS rows, applies the restricted AI heuristic, writes Markdown packet + JSONL selection draft.
2. **Selection finalizer (if MEDIUM cohort needs operator-resolved REVIEW)** — `bc-core/scripts/finalize-phase3-selections.mjs` (parallel to `finalize-phase2-selections.mjs`, commit `124eda8`).
3. **Apply script extension** — one-line update in `bulk-remediate-bf-semantics.mjs` to read `PHASE3_MAX_APPLY` env when the supplied dry-run JSONL has `phase='phase3'`. The drift guard, per-row preflight, halt criteria, and POST loop need NO changes from Phase 2 — the selection validator already accepts any current candidate band, not just HIGH.
4. **Phase 3 final-acceptance generator** — `bc-core/scripts/build-phase3-final-acceptance-packet.mjs` adapted from the Phase 2 helper. Adds C14 sub-shape fidelity check (informational).

Authoring deferred until operator approval of this SOP.

---

## 12. Cross-references

- `bc-docs-v3/docs/adrs/ADR-a49413.md` §11, §12 (unchanged)
- `bc-docs-v3/docs/adrs/ADR-a17d0f.md` (SDA umbrella)
- `bc-core/scripts/bulk-remediate-bf-semantics.mjs` (commits `00a2b59` → `b2f8bfd`)
- `bc-core/scripts/audit-suggest-standard-ref-coverage.mjs` (commit `4cdad6a`)
- `bc-core/scripts/build-phase2-multi-high-packet.mjs` (commit `1a2e17d`) — template for the Phase 3 packet generator
- `bc-core/scripts/finalize-phase2-selections.mjs` (commit `124eda8`) — template for the Phase 3 selection finalizer
- Phase 2 closeout: `2026-05-15-phase2-multi-high-bf-semantic-remediation-closeout-TSK-9515d5.md` (commit `3e5d507`)
- Canary record: SES-594568, BF `invoice_hdr_total_amount`
