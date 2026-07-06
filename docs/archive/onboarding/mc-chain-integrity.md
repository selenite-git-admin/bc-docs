---
id: mc-chain-integrity
order: 61
title: "MC Chain Integrity"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, chain-completeness-and-verdict, metric-contract-creation, canonical-contract-creation, observation-contract-creation, ai-gates, ai-trust-and-verification]
governing_sources:
  - The Contract Grammar
  - Chain Completeness and Verdict
  - Metric Evaluation
governing_adrs:
  - DEC-bebaec (D305 Chain Completeness SSOT)
  - DEC-d72560 (D301 Two-vocabulary model)
  - DEC-9361cd (D302 cc_field_mapping; canonical uniqueness invariant)
  - DEC-c0290f (D315 Metric evaluation engine; finiteness gate; null rejection)
  - DEC-35b34b (D335 Aggregation authority; the diagnostic's anchor)
governing_sops:
  - legacy-v2/docs/sops/mc-chain-integrity-sop.md
errata_referenced: []
v2_sources:
  - sops/mc-chain-integrity-sop.md
diagrams: []
---

# MC Chain Integrity

## Scope

This chapter records the governed sequence by which an existing Metric Contract that has already passed creation gates is walked through an end-to-end integrity check, classified against twelve problem classes, remediated through a governed pathway, and verified for changed output. The chapter names the scope boundary (existing MCs whose values are suspect, not net-new MC creation), the twelve problem classes (D335-R4 sum-on-rule mismatches, CF-to-BF semantic mismatches, dead field references, bare variables, missing BF source, grain CF unmapped, mapping coverage gaps, unit and direction incoherence, AI-caught semantic mismatches, AI-ambiguous verdicts), the toolkit (`mc-diagnose.mjs`, `mc-ai-review.mjs`, `mc-fix.mjs`, `mc-verify.mjs`), the four verdicts (`ready`, `auto-fixable`, `human-required`, `blocked`), the per-MC procedure (load to classify to apply to verify to log), the AI-gated CF-to-BF review with locked prompt template and known-answer evaluation suite, the verifiability pre-check that prevents shipping unverifiable fixes, and the change log that records every refinement of the SOP itself. It records the boundary between MC Chain Integrity and adjacent chapters (MC Creation for net-new, Metric Registration for seed-to-platform, CC Creation and CF Seeding for preceding layers). It records the as-built drift between the procedure and the platform's current chain integrity state.

This chapter does not redefine the chain completeness SSOT (Chain Completeness and Verdict; DEC-bebaec), the metric evaluation engine (Metric Evaluation; DEC-c0290f), or the contract creation chapters that produce the artifacts the diagnostic walks against.

**Governing source.** outline.md §4.6; Chain Completeness and Verdict.

## When the Procedure Runs

The procedure is for existing MCs whose output values are suspect. It is not for net-new MC creation (use Metric Contract Creation), seed-catalog-to-platform registration (use Metric Registration), or CC and CF creation (use Canonical Contract Creation and Canonical Field Seeding). Triggers:

| Trigger | Form |
|---|---|
| Audit flag | The D335 audit (`d335-audit-formula-rule-mismatch.mjs`) reports the MC as suspect |
| Stakeholder report | A user or stakeholder reports a metric value that looks wrong (constant, zero, infinite, nonsensical) |
| CC or OC change | A `cc_field_mapping` or OC `field_mappings[]` entry changed and bound MCs need re-validation |
| Source authority change | An SC or OC change shifted CF-to-BF alignment and later MCs need re-checking |
| Governance review | A locked ADR the MC predates surfaces (e.g., DEC-35b34b for D335 Aggregation Authority) |

The chapter records "one MC at a time" as the rule. Bulk-mode flags are forbidden until the first three to five MCs have been walked individually and the SOP has stabilized.

**Governing source.** Chain Completeness and Verdict.

## What the Procedure Produces

| Artifact | Form |
|---|---|
| Diagnostic JSON verdict | One per MC; emitted by `mc-diagnose.mjs`; saved to the per-MC session log |
| New MC version (when fix applied) | `contract.metric_contract` plus `contract.contract_version` (auto-supersedes prior active version per DEC-bebaec) |
| Verification snapshot diff | Old vs new metric values across grain groups; emitted by `mc-verify.mjs` |
| FUP entry (when blocked or held) | Row in `d335-phase3-followups.md` with preceding-layer gap detail |
| Change record at the DevHub session | `mc-log.md` row plus `runway.md` status (✅ fixed, ⚠ blocked, ✗ aborted) |

The procedure writes through the governed pathway only. `mc-fix.mjs` calls `POST /onboarding/mc/{mcUid}/versions/{newVersion}` (semver minor bump) which routes through `McOnboardingService.createVersion` and runs the MC creation gates. There is no direct SQL write path.

**Governing source.** The Contract Grammar.

## The Twelve Problem Classes

Every walked MC is screened against twelve classes. A new class that surfaces is added here and the diagnostic is extended before the walk continues.

| # | Code | Class |
|---|---|---|
| 1 | D335_SUM_ON_COUNT_WHERE_NOT_NULL | Formula uses SUM on a CF whose `cc_field_mapping` rule is `count_where_not_null` |
| 2 | D335_SUM_ON_COUNT_DISTINCT | Formula uses SUM on a CF with rule `count_distinct` |
| 3 | D335_SUM_ON_LATEST | Formula uses SUM on a CF with rule `latest` |
| 4 | CF_BF_SEMANTIC_MISMATCH | CF name implies one semantic (e.g., count) but BF it resolves to carries another (e.g., currency); name-token heuristic |
| 5 | D315_DEAD_FIELD_REF | Variable's `field_code` is not a registered CF |
| 6 | D315_BARE_VARIABLE | Input variable used in formula without an aggregation function |
| 7 | D302_MISSING_BF_SOURCE | BF that a CF resolves to has no OC field_mapping (unreachable from source) |
| 8 | GRAIN_CF_UNMAPPED | Grain CF declared on the MC but has no `cc_field_mapping` in any bound CC |
| 9 | MAPPING_COVERAGE_GAP | Not every input CF is present in every bound CC's `cc_field_mapping` |
| 10 | UNIT_DIRECTION_INCOHERENT | Declared `unit` and `direction_code` mismatch the formula shape (e.g., percentage metric, direction higher-is-better, formula produces days) |
| 11 | CF_BF_AI_MISMATCH | AI judged CF-to-BF pairing semantically incompatible at confidence at or above 0.8; catches cases the name-token heuristic cannot |
| 12 | CF_BF_AI_AMBIGUOUS | AI verdict ambiguous; low-confidence mismatch (below 0.8); low-confidence aligned (below 0.6); escalates to human-required |

Classes 1 to 3 are the D335-R4 core (formula-rule mismatches). Class 4 is the heuristic that catches token-explicit semantic mismatches. Classes 5 to 10 had partial coverage in the wider codebase; this chapter unifies them into a single per-MC verdict surface. Classes 11 to 12 add AI-gated semantic review (introduced in v0.3 of the SOP).

**Governing source.** Metric Evaluation; The Contract Grammar.

## The Toolkit

Scripts live in `bc-core/scripts/`. Writes route through the governed pathway only.

| Script | Purpose | Writes |
|---|---|---|
| `mc-diagnose.mjs <mcUid>` | Runs all twelve checks; emits JSON verdict plus human-readable summary; includes Step 2.5 AI review (disable via `--no-ai` or `DISABLE_AI=1`) | No |
| `mc-ai-review.mjs <mcUid>` | Invokes bc-ai for the CF-to-BF semantic judgment (classes 11 to 12); locked prompt template; deterministic cache keyed by `(cfId, bfId, rule, promptVersion)` | No |
| `mc-ai-eval.mjs` | Known-answer regression runner; runs every entry in `mc-ai-known-answers.json`; any miss blocks shipping a prompt or model change | No |
| `mc-fix.mjs <mcUid> --apply=<checkCode>` | Applies the prescribed fix for one check via REST; idempotent | Yes (via McOnboardingService) |
| `mc-verify.mjs <mcUid>` | Triggers re-evaluation in the verification tenant and diffs old vs new snapshot values | Yes (evaluation records) |
| `d335-mc-log.md` | Append-only per-MC session log; one row per walk-through with timestamp, verdict, actions, outcomes | No (human-authored markdown) |
| `d335-finance-runway.md` | Scan-sorted sequencing of finance MCs; mark each row ✅, ⚠, or ✗ as walked | No |

**Governing source.** Metric Evaluation; AI Gates.

## Per-MC Procedure

Run these steps in order. A failed step follows its escalation path before the next step runs.

### Step 1: Load Context

```
node scripts/mc-diagnose.mjs <mcUid>
```

The diagnostic emits:

```
{
  "mcUid": "...",
  "mcName": "...",
  "versionCode": "1.1.0",
  "formulaText": "...",
  "bindings": [...],
  "findings": [
    { "checkCode", "severity", "subject", "detail", "fixProcedure", "requiresHuman", "requiresAi" }
  ],
  "verdict": "ready" | "auto-fixable" | "human-required" | "blocked"
}
```

A one-page human summary prints to stdout.

### Step 2: Classify Verdict

`mc-diagnose.mjs` runs the v0.2 name-token heuristic AND invokes `mc-ai-review.mjs` (Step 2.5, blocking) for every (CF, BF, rule) triple the heuristic did not flag. The verdict matrix:

| Verdict | Meaning | Next |
|---|---|---|
| `ready` | No findings of severity `fail` and no AI ambiguous; MC passes integrity | Step 7 (log; mark runway ✅); no fix needed |
| `auto-fixable` | All `fail` findings are in classes 1 to 2; no CF-to-BF mismatches (heuristic or AI) | Step 3 |
| `human-required` | Class 3 (`latest` fix); class 10 (unit coherence); class 12 (AI ambiguous); mapping coverage warnings | Step 4 |
| `blocked` | Any CF-to-BF semantic mismatch (class 4 heuristic or class 11 AI); missing BF source (class 7) | Step 5 |

### Step 3: Auto-Fixable Path

For each finding:

```
node scripts/mc-fix.mjs <mcUid> --apply=<checkCode>
```

The fix calls `POST /onboarding/mc/{mcUid}/versions/{newVersion}` (semver minor bump). The governed version path runs the MC creation gates; the prior active version auto-supersedes per DEC-bebaec.

If `mc-fix.mjs` fails any creation gate, the failure is evidence that another problem class exists that `mc-diagnose.mjs` did not catch. The class is added to the SOP, the diagnostic is extended, and Step 1 restarts.

### Step 4: Human-Required Path

The actor opens the finding in bc-admin catalog view and decides:

| Situation | Action |
|---|---|
| Variant of a known class with a case-by-case answer (e.g., `SUM(latest)` to `MAX` vs `MIN` vs `COUNT_DISTINCT`) | Make the call; record the reasoning in the session log; apply via `mc-fix.mjs` with an explicit `--formula=` override |
| Decision requires stakeholder sign-off | Hold the MC not-approved; open a FUP entry in `d335-phase3-followups.md`; update runway row to ⚠; exit |

### Step 5: Blocked Path

The MC cannot be corrected at the MC layer because an upstream contract (CC, OC, SC, or CF mapping) is wrong.

| Action | Form |
|---|---|
| Open a Class A FUP entry | `d335-phase3-followups.md` with the specific UIDs and the preceding-layer gap |
| Update runway row | ⚠ with FUP reference |
| Hold the MC not-approved | Do not create a new version |
| Exit | The MC re-enters the runway after the preceding-layer fix |

### Step 6: AI Semantic Review (When Prompted)

Step 2.5 invokes `mc-ai-review.mjs` blockingly. The script pairs each (CF name, CF description, CF unit_type, BF name, BF data_type, rule) tuple and asks: "Does the BF credibly carry values representing the CF's declared semantic?"

Verdict codes: `aligned`, `ambiguous`, `mismatch`. Only `mismatch` triggers a Blocked verdict. The AI reasoning is recorded in the session log; a future human review may disagree.

Asymmetric thresholds:

| Verdict | Confidence threshold | Effect |
|---|---|---|
| `mismatch` | At or above 0.8 | Auto-block |
| `aligned` | At or above 0.6 | Silent-pass |
| `ambiguous` (any) | Any | Escalate to human-required |
| `mismatch` below 0.8 | Low confidence | Escalate to human-required |
| `aligned` below 0.6 | Low confidence | Escalate to human-required |

The locked prompt template lives at `bc-core/scripts/mc-ai-review-prompt.md`; the SHA256 of the file is the cache-invalidating prompt-version primitive. The cache directory is `bc-core/scripts/.cache/mc-ai-review/` (gitignored). One JSON file per `(cfId, bfId, rule, promptVersion, model)` hash.

### Step 6.5: Verifiability Pre-Check

Before running verify, the actor confirms the target tenant has COs from every bound CC. If `mc-verify.mjs` reports `0 COs sampled`, the MC is UNTESTABLE in that tenant; the fix cannot be proven.

Action: supersede the new version (an unverified change has shipped); update runway to ⚠ with reason "UNTESTABLE -- no CO data in <tenant>"; open a FUP for the bound CC's reader or OC work that must precede this MC walk.

The pre-check avoids the failure mode of "applied a fix that looked right; no one can prove it either way; sat in production until someone caught it downstream".

### Step 7: Verify (After Step 3 or Step 4 Applied a Fix)

```
node scripts/mc-verify.mjs <mcUid>
```

The verify step triggers re-evaluation in the verification tenant and diffs against the most recent prior snapshot set. Output:

| Section | Content |
|---|---|
| Old version values | min, max, distinct count |
| New version values | min, max, distinct count |
| Sample 5 grain groups | Old vs new pair |
| Assertions | New distinct_count is greater than or equal to old; if old distinct_count was 1 (known-constant tell), new distinct_count is greater than 1; formula evaluates without error across sample COs |

A failed assertion means the fix is not proven. The actor supersedes the new version via the contract service, holds the MC not-approved, and opens a FUP.

### Step 8: Log and Update Runway

The actor appends a row to `scripts/d335-mc-log.md` with the MC name, date, verdict, DevHub session UID, findings list, actions (commands run, versions created), verification (old values, new values, delta), and outcome. The actor updates the runway row in `scripts/d335-finance-runway.md` (✅ fixed with new version code; ⚠ blocked with FUP reference; ✗ aborted with reason). The actor records a DevHub session checkpoint with the summary.

### Step 9: Self-Audit at Session Close

When closing the DevHub session, the actor's self-audit lists which D268 rules applied (`rules_relevant`), which rules tempted a shortcut and were stopped (`rules_tested`, e.g., "Rule 3 -- considered batch-apply after MC #3, held at one-at-a-time"), close calls (`near_misses`), and `rules_obeyed: true` only if no rule was violated.

**Governing source.** The Contract Grammar; Quality Gates and Chain Integrity; Metric Evaluation.

## Verdict Classification Reference

| Verdict | Typical findings | Walk time |
|---|---|---|
| `ready` | None | 2 minutes |
| `auto-fixable` | Classes 1 to 3 only | 10 to 15 minutes |
| `human-required` | Class 3 (latest to MAX/MIN decision) or class 10 (unit coherence) | 20 to 45 minutes |
| `blocked` | Class 4 (CF-to-BF semantic) or class 7 (missing BF source) | 15 minutes (log only) |

**Governing source.** The Contract Grammar.

## SOP Change Log

The SOP itself evolves with each pass. The change log records every refinement.

| Version | Form |
|---|---|
| v0.1 | Initial SOP; ten problem classes identified; toolkit scripts referenced but not yet all built |
| v0.2 | Class 4 (CF-to-BF semantic) heuristic refined; recognizes that `count_where_not_null` and `count_distinct` are the intended bridge between count-semantic CFs and value-semantic BFs; mismatch only fires when the rule preserves the BF's native semantic instead of bridging it |
| v0.3 | AI-gated CF-to-BF review mandatory in `mc-diagnose.mjs` (Step 2.5); asymmetric thresholds (mismatch at 0.8, aligned at 0.6); locked prompt template; known-answer suite at `mc-ai-known-answers.json` re-run via `mc-ai-eval.mjs` before any prompt or model change |
| v0.3.1 | Bug fix in `decideVerdict`: `CF_BF_AI_AMBIGUOUS` warns escalate verdict to `human-required` even when D335 fails are also present |

The chapter is the canonical record of the SOP's evolution; the v2 SOP file is the operational checklist.

**Governing source.** The Contract Grammar.

## Boundary with Other Onboarding Chapters

| Chapter | Relationship |
|---|---|
| Metric Contract Creation | Governs net-new MC creation; this chapter governs walk-through of existing MCs |
| Metric Registration | Governs seed-to-platform metric registration; an MC in this chapter is a registered metric that has been MC-created and is now under integrity review |
| Canonical Contract Creation | When a CF-to-BF mismatch is the root cause, the fix is in CC `cc_field_mapping`, not in the MC; this chapter routes the fix back to CC Creation as a Class A FUP |
| Canonical Field Seeding | When a dead field reference is the root cause, the fix is to register the missing CF; this chapter routes back to CF Seeding |
| Observation Contract Creation | When a missing BF source is the root cause, the fix is in OC `field_mappings[]`; this chapter routes back to OC Creation |
| Chain Completeness and Verdict | The chain status SSOT is the read source for which MCs need walking; this chapter is the procedure that turns the audit signal into governed action |

**Governing source.** Metric Contract Creation; Metric Registration; Canonical Contract Creation; Canonical Field Seeding; Observation Contract Creation; Chain Completeness and Verdict.

## Drift Inventory

| Drift item | Form |
|---|---|
| Bulk-mode flag forbidden until SOP stabilizes | The chapter forbids `--batch` on `mc-fix.mjs` until at least three to five MCs have been walked individually. The forbiddenness is a discipline, not a tooling constraint; the script does not implement bulk mode |
| AI verification surface is required at full sensitivity | The empirical baseline showed the AI gate catches semantic mismatches the name-token heuristic misses. Disabling AI via `DISABLE_AI=1` skips Step 2.5 and produces a less rigorous verdict; the chapter records this as explicit drift the actor accepts when running diagnostics without AI |
| Empirical bottleneck is upstream | The runway analysis showed CF-to-BF mismatches as the dominant bottleneck; the bottleneck is preceding-layer CC mapping hygiene, not formula-fix tooling. The implication is recorded so future SOP refinements focus the right layer |
| Verifiability gap | A non-trivial number of MCs report UNTESTABLE because the bound CC has no CO data in the verification tenant; the FUP path lifts the preceding-layer gap, but the MC walk does not produce a verified fix until the upstream is unblocked |
| Cache invalidation on prompt change | The AI cache invalidates on prompt SHA256 change; an actor who edits the prompt template re-runs the known-answer suite (`mc-ai-eval.mjs`) before any new diagnostic to confirm the new prompt has not regressed |

**Governing source.** Metric Evaluation; AI Trust and Verification; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-bebaec | Establishes the chain completeness SSOT; the diagnostic reads chain status from the SSOT and writes new MC versions through the governed pathway that auto-supersedes per the SSOT version model |
| DEC-d72560 | Establishes the two-vocabulary model; class 4 and class 11 catch CF-to-BF semantic mismatches that the two-vocabulary chain depends on |
| DEC-9361cd | Establishes `cc_field_mapping` rules; classes 1 to 3 catch formula-rule mismatches against those rules |
| DEC-c0290f | Establishes the metric evaluation engine; the verification step (Step 7) re-runs evaluation against the engine and diffs |
| DEC-35b34b | Establishes aggregation authority; the diagnostic anchors against the metric formula as authoritative aggregation |

**Governing source.** Decisions: ADR Registry.

## References

- The Contract Grammar
- Chain Completeness and Verdict
- Metric Evaluation
- Metric Contract Creation
- Metric Registration
- Canonical Contract Creation
- Canonical Field Seeding
- Observation Contract Creation
- AI Gates
- AI Trust and Verification
- Quality Gates and Chain Integrity
- DEC-bebaec: Chain Completeness SSOT
- DEC-d72560: Canonical Field as 3rd contract primitive
- DEC-9361cd: cc_field_mapping (1-to-many with filters)
- DEC-c0290f: Metric evaluation engine
- DEC-35b34b: Aggregation authority
- legacy-v2/docs/sops/mc-chain-integrity-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding


