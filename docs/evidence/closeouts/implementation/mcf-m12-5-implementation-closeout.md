---
uid: mcf-m12-5-implementation-closeout
title: MCF M12.5 — Implementation Closeout
description: Closeout record for MCF gate M12.5 (Materialization + Legacy Bridge) per ADR DEC-c3e57f / D422 + DBCP `52fb8bc` + PR-2 implementation addendum (DBCP §0). Locks the post-merge state of the three M12.5 PR-2 PRs (bc-core PR #126 → main `49ebd3c`; bc-docs-v3 PR #4 → main `aa12b04`; barecount-devhub PR #4 → main `2ea9efc`) and the verification evidence that supports M12.5's code-live status. Status is **code-live + first-operational-run pending**: the materialization service is shipped and proven via the live integration spec (real M7/M8/M10 chain against `bc_platform_dev` under SAVEPOINT rollback, all HA-1..HA-8 enforced, R-M12.5-1 hinge proven, JSONB object proof, post-rollback substrate identical to baseline), but no real operational first run has been executed because the prerequisite `mcf.metric_authoring_panel_run` row with `consensus_payload_json.verdict_code = 'APPROVE_FOR_DRAFT'` does not exist in `bc_platform_dev`, and creating one requires either real M12 model-API runs (operator-disallowed by current scope discipline) or operator-authorized cached-transcript replay. M13 PE-MC evaluator remains CLOSED gated on M12.5 closeout **AND** the operator-flagged serious architecture audit. M14 publication remains CLOSED gated on M13 closeout. No DDL applied. No BCF writes. No bc-admin or tenant-runtime changes. `bc-postgres` MCP `allow_write=false` throughout.
status: draft
date: 2026-05-28
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m12-5-implementation-closeout
---

# MCF M12.5 — Implementation Closeout

## 1. Authority

- ADR: `bc-docs-v3/docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422)
- DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md` (`52fb8bc` + §0 PR-2 implementation addendum at `aa12b04`)
- Preflight: `bc-docs-v3/docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-preflight.md`
- Bridge doc: `bc-docs-v3/docs/operating-model/mcf-legacy-bridge.md`
- Operator runbook: `bc-docs-v3/docs/onboarding/metric-registration.md` §"MCF M12.5 — new authoring path"

## 2. Status

**M12.5 status: code-live + first-operational-run pending (blocked on prerequisite)**

- **Code-live:** The materialization service `MetricAuthoringMaterializationService` is on `bc-core` main at `49ebd3c`. All three companion PRs merged in operator-specified order on 2026-05-28. Companion docs are on `bc-docs-v3` main at `aa12b04`. Operator-facing CLAUDE.md note is on `barecount-devhub` main at `2ea9efc`.

- **Evidence-complete for substrate proof:** The live integration spec at `bc-core/src/registry/mcf/metric-authoring-materialization.service.integration.spec.ts` exercises the production service end-to-end against `bc_platform_dev` under SAVEPOINT rollback with the **real** M7/M8/M10 chain (no mocks of in-scope collaborators) and passes all HA-1..HA-8 + R-M12.5-1 hinge + JSONB-object proof assertions, with post-rollback substrate confirmed identical to baseline (see §6).

- **First-operational-run pending:** No real operational materialization has executed against `bc_platform_dev`. The prerequisite `mcf.metric_authoring_panel_run` row with `consensus_payload_json.verdict_code = 'APPROVE_FOR_DRAFT'` does not exist; creating one requires either real M12 model-API runs (currently scope-disallowed) or operator-authorized cached-transcript replay. See §8 + §9.

## 3. Repo SHAs (post-merge, locked)

| Repo | main SHA | Merged from | Merge type |
|---|---|---|---|
| `bc-core` | `49ebd3c21337f92134518c0c77375915949e110b` | PR #126 HEAD `09bf36e` | squash, `--match-head-commit`, `--delete-branch` |
| `bc-docs-v3` | `aa12b0449e53c6339cbbceff252684a3e804ab99` | PR #4 HEAD `bb1ff5f` (was `929c695` pre-trailer-fix) | squash, `--match-head-commit`, `--delete-branch` |
| `barecount-devhub` | `2ea9efc53cc9a3b83c9b4bf8e5a3936c54398566` | PR #4 HEAD `e39cfb3` (was `61db457` pre-rebase) | squash, `--match-head-commit`, `--delete-branch` |

Merge order honored: bc-docs-v3 first → barecount-devhub second → bc-core last (operator preference: implementation lands after operator-facing docs are clean).

## 4. DB before/after row deltas

This closeout gate is read-only. **No row deltas occurred** because no operational materialization ran.

### 4.1 Closeout-time live state (== pre-test baseline)

| Object | Pre-merge | Post-all-merges | Closeout gate | Delta |
|---|---|---|---|---|
| `mcf.metric_contract` | 0 | 0 | 0 | 0 |
| `mcf.metric_contract_version` | 0 | 0 | 0 | 0 |
| `mcf.metric_variable_binding` | 0 | 0 | 0 | 0 |
| `mcf.metric_filter_clause` | 0 | 0 | 0 | 0 |
| `mcf.metric_computed_dimension_ref` | 0 | 0 | 0 | 0 |
| `mcf.metric_contract_revision` | 0 | 0 | 0 | 0 |
| `mcf.metric_supersession` | 0 | 0 | 0 | 0 |
| `mcf.certification_record` | 0 | 0 | 0 | 0 |
| `mcf.metric_publication_eligibility_result` | 0 | 0 | 0 | 0 |
| `mcf.metric_cert_writer_idempotency` | 0 | 0 | 0 | 0 |
| `mcf.metric_authoring_panel_run` | 0 | 0 | 0 | 0 |
| `mcf.metric_authoring_panel_transcript` | 0 | 0 | 0 | 0 |
| `mcf.workspace_tool_allowlist` | 0 | 0 | 0 | 0 |
| `mcf.evidence_source_allowlist` | 0 | 0 | 0 | 0 |
| `mcf.metric_self_verification_fixture` | 0 | 0 | 0 | 0 |
| `mcf.metric_self_verification_result` | 0 | 0 | 0 | 0 |
| `mcf.metric_authoring_intake_queue` | 0 | 0 | 0 | 0 |
| `contract.panel_output_record` | 24 | 24 | 24 | 0 |
| `contract.authoring_panel_rejection_log` | 1 | 1 | 1 | 0 |
| `idx_mcf_mc_mc_name_active` exists | yes (PR-1) | yes | yes | unchanged |
| `contract.framework_policy` mcf_v1 active | 1 | 1 | 1 | unchanged |

## 5. UID chain

No operational materialization occurred. The UID chain that the first operational run will populate is:

```
panel_run_uid          → uuid (mcf.metric_authoring_panel_run.panel_run_uid)
  ↓ FK via consensus_payload_json.intake_back_reference.intake_queue_uid
intake_queue_uid       → uuid (mcf.metric_authoring_intake_queue.intake_queue_uid)

After M12.5 materialization writes:
metric_contract_uid          → uuid (mcf.metric_contract.metric_contract_uid)
metric_contract_version_uid  → uuid (mcf.metric_contract_version.metric_contract_version_uid)
certification_record_id      → uuid (mcf.certification_record.certification_record_id)
fixture_uid                  → uuid (mcf.metric_self_verification_fixture.fixture_uid)
verification_result_uid      → uuid (mcf.metric_self_verification_result.verification_result_uid)
```

The first operational run's evidence artifact (when authorized — see §9) will populate this chain.

## 6. Verifier result and JSONB object proof (from integration spec)

The integration spec exercises the production service against `bc_platform_dev` under SAVEPOINT rollback with the real M7/M8/M10 chain. Per the spec assertions that pass:

- `firstResult.verifier_verdict === 'pass'` — real `FormulaExecutionEngine` evaluates the AST against Section A inputs; real `OutputComparator` matches Section B; verdict = pass.
- `stale_fixture_flag === false` — real M10 `MetricSelfVerificationService` STALE CHECK passes.
- `bound_package_signature_hash_at_run === fixture.bound_package_signature_hash` — algorithmic identity: verifier-recomputed hash (real M7+M8 from MCV substrate) equals M12.5-stamped hash (real M7+M8 from same MCV substrate). This is the R-M12.5-1 hinge.
- Both hashes match `^sha256:[0-9a-f]{64}$` — no placeholder fallback.
- `jsonb_typeof = 'object'` on 8 jsonb columns across 4 tables (fixture section A/B/C, verifier_result verdict_payload, mapr consensus_payload + reservoir_provenance, intake reservoir_provenance + normalized_candidate) — no JSONB STRING corruption.
- Post-rollback live readback confirms all 17 `mcf.*` tables identical to baseline; BCF rows preserved exactly (24 + 1).

Last live integration run captured for this closeout gate:

```
Test Files  1 passed (1)
Tests       1 passed (1)
Duration    2.08s (transform 669ms, setup 0ms, import 1.62s, tests 252ms)
EXIT 0
```

Post-test live DB rowcounts identical to pre-test (confirmed via `bc-postgres` MCP with `allow_write=false`).

## 7. HA-1..HA-8 outcome

| HA | Statement | Enforcement | Status |
|---|---|---|---|
| HA-1 | No legacy `metric.*` writes from M12.5 | Service source has zero imports of `MetricDefinitionService` / `MetricDefinitionRepository`; integration spec asserts forbidden tables 0-delta | ✓ enforced |
| HA-2 | M12.5 calls only M4 `createMetricDraft` — no `submitForReview` / `approveForActivation` / `activateMetric` / `supersedeMetric` | Source has zero call sites to these methods; unit test asserts; integration spec asserts MCV `governance_state_code='draft'` | ✓ enforced |
| HA-3 | No INSERT into `mcf.metric_publication_eligibility_result` / `mcf.metric_supersession` / `mcf.metric_contract_revision` | Integration spec asserts 0-delta on these tables inside the rolled-back tx | ✓ enforced |
| HA-4 | No BCF writes from M12.5 (only reads via `cert.panelRunUid` FK to `contract.panel_output_record`) | Integration spec asserts `contract.panel_output_record` + `contract.authoring_panel_rejection_log` row counts preserved exactly across the rolled-back tx | ✓ enforced |
| HA-5 | Exact 6-row write surface per materialization (1 mc + 1 mcv + 1 binding + 1 cert + 1 fixture + 1 verifier_result) | Integration spec asserts exact row deltas on each table inside the rolled-back tx | ✓ enforced |
| HA-6 | MCV stops at `governance_state_code='draft'` (cert `action_code=metric_create`, `fromStateCode=null`, `toStateCode='draft'`) | Unit test asserts at cert composition; integration spec asserts MCV state live | ✓ enforced |
| HA-7 | Single-source `consensus_payload_json` schema literal shared by M12 panel writer + M12.5 reader | Both services import `panel-payload.schema.json` via shared module path; M12.5 service constructor compiles the same schema via AJV at module init | ✓ enforced |
| HA-8 | Idempotent retry — same `panel_run_uid` returns same 5 substrate UIDs + `intake_transitioned=false`; no new writes | Service `findExistingMaterialization()` detects prior cert+fixture+verifier via `cert.panel_run_uid` join; integration spec asserts retry returns identical UIDs + `intake_transitioned=false` | ✓ enforced |

All 8 hard assertions enforced and live-verified via the integration spec running against `bc_platform_dev`.

## 8. First operational materialization run status

**Status: PENDING — blocked on prerequisite.**

Closeout-gate query against `bc_platform_dev` (read-only):

```
mapr_total                            = 0
mapr_approve_for_draft                = 0   ← M12.5 input prerequisite missing
intake_total                          = 0
intake_pending                        = 0
panel_output_record_total             = 24
panel_output_record_authoring_approve = 19  (BCF-side audit ledger; not coupled to MCF mapr)
framework_policy_mcf_v1_active        = 1
```

The 24 `contract.panel_output_record` rows + 19 with verdict `APPROVE_FOR_DRAFT` are from prior M12 integration testing; they were written to BCF without writing the parallel MCF `mcf.metric_authoring_panel_run` substrate (M12 unit/integration tests stopped at BCF), so they are not eligible M12.5 inputs.

**Prerequisite chain for the first operational run:**

1. **M11 intake row** in `pending` state (currently 0) — requires `scripts/mcf-m11-operator-direct-ingest.mjs` invocation (seed-script class per CLAUDE.md scope discipline)
2. **M12 panel run** producing `consensus_payload_json.verdict_code = 'APPROVE_FOR_DRAFT'` (currently 0) — requires real model API calls for the three-model Maker / Checker / Moderator consensus

Both prerequisites fall under the closeout gate's "do not" list (no seed scripts unless authorized; no real model API calls). Neither was attempted.

## 9. Unblocking paths for the first operational run (separate authorization required)

| Path | Description | Trade-off |
|---|---|---|
| **(a) Synthetic first run** | Operator authorizes inserting a hand-crafted `consensus_payload_json` directly into `mcf.metric_authoring_panel_run` + corresponding `mcf.metric_authoring_intake_queue` row in `pending` | Proves M12.5 service path only; does NOT prove M11 → M12 → M12.5 end-to-end |
| **(b) Real M12 panel run** | Operator authorizes M11 intake submission + a real-model M12 panel run; M12.5 then materializes the produced `APPROVE_FOR_DRAFT` panel | Full evidence chain; requires real-model budget + operator-procured model tokens |
| **(c) Cached M12 transcript replay** | Operator supplies a captured `consensus_payload_json` from a prior real M12 run + replays it into substrate without re-invoking model APIs | Middle ground; depends on whether a captured transcript exists from prior M12 runs |

Until one of (a)/(b)/(c) is operator-authorized in a separate gate, M12.5 first operational run remains pending. The substrate-proof evidence from §6 stands as the existing demonstration that the service path is correct.

## 10. M13 gate status

**M13 (PE-MC evaluator) remains CLOSED.**

Two preconditions for opening M13:

1. **M12.5 closeout** — partially satisfied by this document (code-live + substrate-proof complete; first operational run pending — see §8).
2. **Serious architecture audit before M13** (operator-flagged) — NOT yet started. The audit's scope and acceptance criteria are not yet defined. Until this audit completes, M13 design / DBCP / implementation work is gated.

Both conditions must be satisfied before any M13 work begins.

## 11. M14+ gates

- **M14 publication** — remains CLOSED, gated on M13 closeout per D-M12.5-12.
- **M15 supersession** — remains CLOSED.
- **M16 / M17 bc-admin migration** — out of M12.5 scope.
- **M17 HTTP 410 on legacy POST** — out of M12.5 scope (Sunset header is advisory only).
- **M18+ tenant runtime MCF awareness** — out of M12.5 scope.

## 12. Cross-cutting discipline (this gate)

| Constraint | Status this gate |
|---|---|
| `bc-postgres` MCP `allow_write` | unchanged (false) |
| BCF writes | none |
| DDL applied | none |
| Seed scripts run | none |
| Real model API calls | none |
| bc-admin touched | no |
| Tenant runtime touched | no |
| Persistent DB writes | none |
| Additional commits | this closeout doc and the closeout-gate summary artifact are net-new files; not yet committed at the time of writing |

## 13. Evidence artifact

Gate execution summary captured at:

```
bc-core/scripts/audit-output/mcf-m12-5-closeout-gate-2026-05-28T08-34-57-000Z.summary.md
```

The operator's requested filename `mcf-m12-5-first-materialization-<timestamp>.{summary.md,evidence.jsonl}` is deliberately NOT used because no first operational materialization occurred during this gate; using the "first-materialization" filename for a closeout-gate report would corrupt the M-series post-apply evidence convention (every prior such artifact documented actual DB writes). When the first operational run is authorized and executes, that artifact will be written under the original filename convention with real evidence.

## 14. See also

- `bc-docs-v3/docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md` — design specification (with §0 PR-2 addendum)
- `bc-docs-v3/docs/operating-model/mcf-legacy-bridge.md` — read-fallback policy + Sunset semantics
- `bc-docs-v3/docs/onboarding/metric-registration.md` — operator runbook
- `bc-core/src/registry/mcf/metric-authoring-materialization.service.integration.spec.ts` — live substrate-proof integration spec
- `bc-core/scripts/mcf-m12-5-preflight.mjs` — read-only preflight verifier
