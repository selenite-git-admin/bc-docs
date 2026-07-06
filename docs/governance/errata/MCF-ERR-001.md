---
id: MCF-ERR-001
title: "First-real-M12 authorization DBCP: verdict-to-intake-status mapping is incorrect"
status: adopted
authority: authoritative
affected: docs/implementation/metric-context-framework-m12-first-real-run-authorization-dbcp.md (bc-docs-v3 main `a18d6e3c`) — §4 expected-intake-row-status row, §4 Run Uniqueness Contract paragraph, §8 outcome table (3 verdict rows), §8.3 Re-attempt Path paragraph, §10 R3 + R5 risk-register rows
temporary_governance:
  - docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md (M12 design-blueprint; Step 8 + outcome table)
  - docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md (M12.5 design; markConsumedByPanel ownership)
  - bc-core src/registry/mcf/metric-authoring-panel.service.ts (HA-6 + transitionIntakeToRejected — code is SoT)
  - bc-core src/registry/mcf/metric-authoring-materialization.service.ts (APPROVE_FOR_DRAFT precondition + markConsumedByPanel — code is SoT)
target_resolution: Future amendment to docs/implementation/metric-context-framework-m12-first-real-run-authorization-dbcp.md aligning §4 / §8 / §10 with the verdict-aware mapping below. Until that amendment lands, this erratum governs the corrected reading of the DBCP for any future operator interpretation; PR #168 execution evidence is amended to reference this erratum.
opened: 2026-05-30
---

# MCF-ERR-001 — First-real-M12 authorization DBCP: verdict-to-intake-status mapping is incorrect

## Contradiction summary

The first-real-M12 authorization DBCP (`metric-context-framework-m12-first-real-run-authorization-dbcp.md`, bc-docs-v3 main `a18d6e3c`, PR #29) documents that **every terminal M12 verdict** transitions the intake row from `pending` to `consumed_by_panel`. That mapping appears in five places in the DBCP:

| DBCP location | Wording |
|---|---|
| §4 `expected_intake_row_status_at_run_end` | `consumed_by_panel` (orchestrator HA-6 transition; applies regardless of terminal verdict) |
| §4 Run Uniqueness Contract paragraph | "The intake row transitions from `pending` → `consumed_by_panel` at the start of the run, preventing concurrent or duplicate attempts." |
| §8 outcome table, all three terminal rows (`APPROVE_FOR_DRAFT`, `OPERATOR_REVIEW`, `REJECT_DEFECT`) | "Intake row status after run = `consumed_by_panel`" |
| §8.3 Re-attempt Path | "The original intake row `4d849778-...` stays at `consumed_by_panel` permanently — it represents the historical first-real-M12 run regardless of verdict." |
| §10 R3 + R5 risk-register | "Intake row already at `consumed_by_panel`…" / "intake row may be left at `consumed_by_panel`" |

This is not the M12 contract. The actual contract — locked in the **M12 authoring panel DBCP** (`metric-context-framework-m12-authoring-panel-dbcp.md`, design blueprint), the **M12.5 materialization DBCP** (`metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md`), and the live bc-core code that implements both — is verdict-aware and assigns the `consumed_by_panel` transition to M12.5, not M12.

## Implementation behavior

The M12 panel service (`bc-core/src/registry/mcf/metric-authoring-panel.service.ts`) implements M12-B proposal-only orchestration. Its hard assertion **HA-6** (named in the service header comment) is:

> "HA-6: NEVER call markConsumedByPanel — that's M12.5's job after substrate write succeeds. CI grep + this source file MUST NOT contain that string."

Step 8 of `runPanel()` performs the only intake-status mutation M12 ever performs, and it does so **only on `REJECT_DEFECT`**:

```ts
// Step 8: SHORT TX #C — intake status transition (all-reject ONLY)
if (consensus.verdict_code === 'REJECT_DEFECT') {
  await this.transitionIntakeToRejected(intake.intake_queue_uid, consensusPayload, deps.tx);
}
// NEVER call markConsumedByPanel here — that's M12.5's job (HA-6)
```

`transitionIntakeToRejected` issues a guarded UPDATE that sets `status_code = 'rejected'` (not `consumed_by_panel`):

```ts
await tx.execute(sql`
  UPDATE mcf.metric_authoring_intake_queue
  SET status_code = 'rejected', status_reason_text = ${reason}
  WHERE intake_queue_uid = ${intakeQueueUid} AND status_code = 'pending'
`);
```

The M12 DBCP itself locks the same behavior in its outcome table (§5 of `metric-context-framework-m12-authoring-panel-dbcp.md`):

| Outcome | Intake row status after run |
|---|---|
| Successful all-approve + grounding pass | unchanged — pending (M12.5 will transition) |
| Successful all-reject | rejected (via `markRejected`) |
| Mixed / partial / vendor outage / vendor failure | unchanged — pending |

And `D-M12-8` in the same DBCP records the operator decision: *"`markRejected` only on all-reject; otherwise leave intake at `pending`; `markConsumedByPanel` FORBIDDEN in M12 v1 (M12.5 owns it after substrate write) — ACCEPTED."*

The M12.5 materialization service (`bc-core/src/registry/mcf/metric-authoring-materialization.service.ts`) carries the `markConsumedByPanel` call site, gated on the `APPROVE_FOR_DRAFT` precondition (Step 1 of `runMaterialization()`):

```ts
const verdict = row.consensus_payload_json?.verdict_code;
if (verdict !== 'APPROVE_FOR_DRAFT') {
  throw new MaterializationPreconditionError(
    `mapr verdict_code='${verdict}', expected 'APPROVE_FOR_DRAFT' (M12.5 only materializes approved proposals)`
  );
}
```

And inside its TX C, after the M10 verifier passes:

```ts
// (b) M11 intake transition — only after verifier result INSERT succeeds
await this.reservoir.markConsumedByPanel(intakeQueueUid, { tx });
```

So the live contract — across two DBCPs and two services — is:

| Verdict | Status after M12 run | Who performs the transition | Status after M12.5 run (if invoked + successful) |
|---|---|---|---|
| `APPROVE_FOR_DRAFT` | `pending` (unchanged) | nobody at M12 | `consumed_by_panel` (M12.5 TX C, `markConsumedByPanel`) |
| `OPERATOR_REVIEW` | `pending` (unchanged) | nobody | M12.5 stays gated; no transition |
| `REJECT_DEFECT` | `rejected` | M12, `transitionIntakeToRejected` | M12.5 stays gated; no further transition |

PR #29's "regardless of terminal verdict" wording contradicts all three rows.

## Why the contradiction matters

PR #29 was authored as a single-use authorization for the first real M12 run; it was not intended as an architectural revision of the M12 / M12.5 boundary. The `consumed_by_panel`-everywhere mapping is a documentation error, not a behavior change. The behavior locked by the M12 DBCP, the M12.5 DBCP, and the bc-core code remains the source of truth.

Two operational claims in PR #29 depend on the incorrect mapping and require re-reading under the verdict-aware contract:

1. **§4 "Run Uniqueness Contract".** The PR #29 paragraph attributes uniqueness to a `pending → consumed_by_panel` transition at the start of the run. The actual M12 uniqueness mechanism is the **in-flight guard** (§5.4 of the M12 DBCP): the panel service queries `mcf.metric_authoring_panel_run` for prior rows keyed on `(reservoir_name, reservoir_entry_id)` and refuses to start a second proposal unless `opts.allowRetry === true`. No status-flip is required for uniqueness; the in-flight guard plus M11's status-transition CAS on the `REJECT_DEFECT` path are what prevent duplicate work. The PR #29 mechanism description is wrong; the actual uniqueness guarantee is intact.

2. **§6 single-use authorization.** PR #29's single-use authorization clause (item 6) was layered on top of the assumed `consumed_by_panel`-everywhere substrate behavior. The single-use rule remains a governance rule — the operator's attestation is consumed by exactly one M12 run regardless of verdict — but it is **enforced operator-side**, not by an automatic substrate transition. After an `OPERATOR_REVIEW` or non-terminal-failure outcome, the intake row stays at `pending`; the substrate technically permits a second M12 run against the same intake row, but the operator-side authorization is exhausted. Re-running the panel against the same intake without a fresh authorization DBCP violates the operator-side single-use rule, even though the substrate's `pending` status does not block it.

These two re-readings do not change the M12 contract; they correct the explanation of how M12's existing safeguards work.

## Application to PR #168 (first-real-M12 execution evidence)

PR #168 (`mcf(m12): FIRST REAL M12 PANEL RUN executed — verdict OPERATOR_REVIEW`, bc-core open at `24d596d6`) executed the first real M12 panel run authorized by PR #29 and returned verdict `OPERATOR_REVIEW`. Per this erratum:

- The `OPERATOR_REVIEW` outcome **satisfies PR #29 §8.1 success criterion (A4)** — any terminal verdict via the real trust path with real adapter provenance discharges D8 condition 7.
- The `OPERATOR_REVIEW` outcome **does not unlock M12.5** (per M12.5's `APPROVE_FOR_DRAFT` precondition).
- The intake row staying at `pending` after the run is the **correct M12 contract** under this verdict, not a deviation.
- PR #168 will be amended to (a) reference this erratum, (b) correct its script's verdict-aware expected-status check to the mapping in this erratum, and (c) correct two prose paragraphs in its summary file that misattributed the verdict-aware behavior to "HA-6 firing only on APPROVE_FOR_DRAFT". HA-6 is the rule that M12 NEVER calls `markConsumedByPanel`; it is not the action.

The substrate evidence in PR #168 is unaffected:

- `bcf.panel_output_record` +1
- `mcf.metric_authoring_panel_run` +1 (`panel_run_uid = 9a462e6c-ce41-4ecb-aa51-cbac6c2b3990`)
- `mcf.metric_authoring_panel_transcript` +3
- `mcf.metric_contract` 0, `mcf.metric_contract_version` 0
- intake `4d849778-3989-4caf-8a71-7d44b782d98e` status `pending` (unchanged)

These deltas exactly match the M12 contract under `OPERATOR_REVIEW`.

## What M12 writes vs what M12.5 may write

For clarity going forward, the substrate-write boundary between M12 and M12.5 is:

| Gate | Writes |
|---|---|
| **M12** | `contract.panel_output_record` (+1), `mcf.metric_authoring_panel_run` (+1), `mcf.metric_authoring_panel_transcript` (+3); on `REJECT_DEFECT` only: `mcf.metric_authoring_intake_queue.status_code = 'rejected'` |
| **M12.5** | `mcf.metric_contract` (+1), `mcf.metric_contract_version` (+1), `metric_variable_binding` (+N), `metric_filter_clause` (+N), `metric_computed_dimension_ref` (+N), `certification_record` (+1), `metric_self_verification_fixture` (+1), `metric_self_verification_result` (+1); on success: `mcf.metric_authoring_intake_queue.status_code = 'consumed_by_panel'` via `markConsumedByPanel` |

M12.5 is therefore the first gate that may create `mcf.metric_contract` / `mcf.metric_contract_version`, and only for `APPROVE_FOR_DRAFT`.

## Temporary governance

Until the PR #29 DBCP is amended in a follow-up bc-docs-v3 PR, the governing reading is:

1. The verdict-aware mapping table in §Implementation behavior of this erratum.
2. The M12 authoring panel DBCP (`metric-context-framework-m12-authoring-panel-dbcp.md`) Step 8 + outcome table + D-M12-8.
3. The M12.5 materialization DBCP (`metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md`) APPROVE_FOR_DRAFT precondition + `markConsumedByPanel` ownership.
4. The bc-core code at the lines cited above (SoT for the runtime contract).

PR #29 governs as authorization for the single first-real-M12 run that produced `panel_run_uid = 9a462e6c-ce41-4ecb-aa51-cbac6c2b3990`. Its single-use clause remains in effect — the operator's attestation is exhausted regardless of verdict — but the substrate-transition mechanism described in PR #29 §4 is incorrect and the operator-side rule from §6 is what enforces single-use.

## Resolution state

**Adopted.** The M12 DBCP + M12.5 DBCP + bc-core code reading is the correct behavior. PR #29's documentation was the deviation. The PR #29 DBCP itself will be amended in a follow-up bc-docs-v3 PR that:

- Rewrites §4 `expected_intake_row_status_at_run_end` as the three-row verdict-aware table.
- Rewrites §4 Run Uniqueness Contract paragraph to attribute uniqueness to the in-flight guard (M12 DBCP §5.4) rather than to a `pending → consumed_by_panel` flip.
- Rewrites §8 outcome table's "Intake row status after run" column with the verdict-aware values.
- Rewrites §8.3 Re-attempt Path to reflect that, for `OPERATOR_REVIEW`, the original intake stays at `pending` and the re-attempt path uses a NEW `reservoir_entry_id`; the substrate's `pending` status is not the single-use enforcer (§6 operator rule is).
- Rewrites §10 R3 + R5 to describe what the substrate state actually is under each verdict and what the recovery path is.

This erratum closes when that follow-up amendment lands.

## References

- `docs/implementation/metric-context-framework-m12-first-real-run-authorization-dbcp.md` (PR #29; bc-docs-v3 main `a18d6e3c`) — §4, §6, §8, §8.3, §10 R3 + R5
- `docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` — Step 8, outcome table, D-M12-8, §5.4 in-flight guard
- `docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md` — APPROVE_FOR_DRAFT precondition, TX C `markConsumedByPanel` ownership
- `docs/operating-model/mcf-legacy-bridge.md` — M11 intake → M12 panel → M12.5 materialization lifecycle
- `docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) — MCF bridge ADR
- `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) — operator authorization stance
- bc-core `src/registry/mcf/metric-authoring-panel.service.ts` (bc-core PR #161 merge `a0fee4e9`) — HA-6 header comment, `runPanel()` Step 8, `transitionIntakeToRejected`
- bc-core `src/registry/mcf/metric-authoring-materialization.service.ts` (bc-core PR #126 merge `49ebd3c2`) — APPROVE_FOR_DRAFT precondition (Step 1), TX C `markConsumedByPanel` (line 780)
- bc-core PR #168 (`mcf-m12-first-real-run-execution-evidence`) — execution evidence for `panel_run_uid = 9a462e6c-ce41-4ecb-aa51-cbac6c2b3990`; substrate-readback verified at bc-core main `0e5e501d`
