---
uid: DBCP-mcf-m12-trust-path-reconciliation
title: MCF M12 trust-path reconciliation DBCP
description: Short decision-focused DBCP. Decides how to reconcile the existing trust-bearing M12 orchestrator (MetricAuthoringPanelService — contract.* writer) with the new post-A5 bcf/mcf persistence writer (M12PanelRunWriterService — bcf.* writer) before any further "first real metric via bcf/mcf" work. Decision-only. No code change. No M12 invocation. No M12.5 invocation. No metric creation. No rollback. No tenant DB.
status: proposed
date: 2026-05-29
project: bc-core
domain: implementation
subdomain: mcf
focus: governance
supersedes: null
superseded_by: null
---

# MCF M12 trust-path reconciliation DBCP

This DBCP answers exactly one question:

> What is the authoritative M12 trust path going forward — the existing orchestrator with its discipline (currently writing to a frozen substrate), the new post-A5 persistence writer (currently with no trust discipline), or a staged migration of the orchestrator's substrate?

Until this is decided, "first real metric via bcf/mcf" has no coherent next PR to write.

---

## 1. Scope / non-scope

### 1.1 In scope

- Naming the architectural fracture between the M12 orchestrator and the post-A5 persistence writer.
- Enumerating three reconciliation options (O1 adapter / O2 retirement / O3 staged migration).
- Recommending a default and stating the trust implication of each option.
- Listing the downstream gates that this decision unblocks.

### 1.2 Non-scope (explicit)

1. **No code change.** This is a governance decision, not a refactor.
2. **No M12 panel invocation.** `MetricAuthoringPanelService.runPanel()` is NOT called.
3. **No M12 writer invocation.** `M12PanelRunWriterService.writePanelRun()` is NOT called.
4. **No M12.5 materialization invocation.** `MetricAuthoringMaterializationService.runMaterialization()` is NOT called.
5. **No metric creation.** No `mcf.metric_contract` / `mcf.metric_contract_version` row authored.
6. **No legacy `metric.metric_definition` write.** The untrusted corpus is left alone.
7. **No rollback executed.** A5 outcome (C) is durable; this DBCP does not address C2.
8. **No tenant DB touch.** Platform DB read-only only.
9. **No DDL/DML.**
10. **No retraction of PR #160's row.** The placeholder row at panelRunUid `48629788-...` stays in substrate; this DBCP only names what it is and isn't.
11. **No re-litigation of A1-A5 substrate work** or the M14 unblock lineage. That work landed.

---

## 2. Authority anchor chain

| Anchor | Reference |
|---|---|
| Stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) |
| M12 implementation closeout | `docs/implementation/mcf-m12-implementation-closeout.md` |
| M12.5 implementation closeout | `docs/implementation/mcf-m12-5-implementation-closeout.md` |
| M13 implementation closeout | `docs/implementation/mcf-m13-implementation-closeout.md` |
| MCF M14/M12 governance DBCP | `docs/implementation/metric-context-framework-m14-m12-governance-dbcp.md` (bc-docs-v3 main `6d20c8d` / PR #23) |
| MCF M14 unblock apply DBCP | `docs/implementation/metric-context-framework-m14-unblock-apply-dbcp.md` (bc-docs-v3 main `2c56151` / PR #24) |
| MCF M12 first real panel-run DBCP | `docs/implementation/metric-context-framework-m12-first-real-run-dbcp.md` (bc-docs-v3 main `ab144f4` / PR #25) |
| MCF M12 first real panel-run closeout | `docs/implementation/metric-context-framework-m12-first-real-run-closeout.md` (PR #26 — pending merge at authoring time of this DBCP) |
| MCF Legacy Bridge | `docs/operating-model/mcf-legacy-bridge.md` |
| bc-docs-v3 anchor (this DBCP base) | `ab144f48634a7772eea029627e78275a7a8c18ac` |
| bc-core anchor | main `64add8594b949321650dd169f24a969f53cf6877` (will advance with PR #160 merge — already merged at `7554f9c8163c9fc332a1e65885083f7353f7a8a4`; this DBCP does not advance bc-core) |

---

## 3. Current standing state (live verified, read-only)

| Substrate | Value | Interpretation |
|---|---|---|
| `bcf.panel_output_record` | 20 | 19 A1 backfill anchors + 1 PR #160 placeholder |
| `contract.panel_output_record` | 19 | Frozen by A4 deny-write triggers |
| `mcf.metric_authoring_panel_run` total | 1 | The PR #160 placeholder row |
| `mcf.metric_authoring_panel_run` with `verdict_code = 'APPROVE_FOR_DRAFT'` | 0 | No M12.5-materializable row exists |
| `mcf.workspace_tool_allowlist` | 0 | M12 allowlists never seeded (per M12 closeout: operator-driven step pending) |
| `mcf.evidence_source_allowlist` | 0 | Same |
| `mcf.metric_authoring_intake_queue` | 0 | No M11 intake row exists |
| `mcf.metric_contract` | 0 | No MCF-authored metric contract exists |
| `mcf.metric_contract_version` | 0 | Same |
| M14 governance gate | OPEN (Option α writer-activation-only; evidence-defined at apply-ts `2026-05-29T16-03-50-994Z`) | Writer DI-resolvable; orchestrator not addressed |
| A5 rollback envelope outcome | **(C)** — durable | Cliff crossed by the PR #160 writer-path proof commit |
| C2 force-rollback / data-loss envelope DBCP | NOT AUTHORED | Out of scope here |

---

## 4. Grounded evidence — the fracture

### 4.1 The trust-bearing orchestrator targets a frozen table

`MetricAuthoringPanelService.runPanel()` in `bc-core/src/registry/mcf/metric-authoring-panel.service.ts` is the canonical M12 trust path. Per the closeout doc (`mcf-m12-implementation-closeout.md` §5) it is "production-ready as substrate-side discipline + orchestration framework." It owns:

- 3-vendor maker / checker / moderator panel deliberation (HA-1..HA-9 enforced)
- AJV runtime schema validation of `consensus_payload_json` (HA-7 — wired at module init; throws `ConsensusPayloadValidationError`)
- Workbench fingerprint discipline (`mcf-workbench-v1`)
- Consensus computation + grounding check
- Defect-code registry pin (`defect_code_registry_version='v1'`)
- 4 reservoir-provenance fields copied from intake to mapr (HA-8)
- Three short transactions: validate / write / conditional reject

**Its write step (Step 7a) executes the SQL `INSERT INTO contract.panel_output_record (...)`** at `metric-authoring-panel.service.ts:608-609`. The table `contract.panel_output_record` is one of the four BCF evidence tables structurally frozen by the Phase A4 deny-write triggers (`trg_contract_panel_output_record_deny_write` and three peers — 4 functions × 4 trigger definitions × 3 events = 12 LIVE event-bindings).

**Consequence.** `runPanel()` cannot complete a write against the live platform substrate today. The trust-bearing path is structurally broken.

### 4.2 The new persistence writer has no trust discipline

`M12PanelRunWriterService.writePanelRun(input)` in `bc-core/src/registry/metric-authoring/m12-panel-run-writer.service.ts:267` is a thin persistence service. It writes one row to `bcf.panel_output_record`, one to `mcf.metric_authoring_panel_run`, and three to `mcf.metric_authoring_panel_transcript` inside a single `db.transaction(...)`. It does NOT:

- run the 3-agent panel
- validate `consensus_payload_json` via AJV
- compute consensus
- compute the workbench fingerprint
- assert HA-1..HA-9
- enforce the defect-code registry pin
- read or transition the intake queue
- check the allowlists

It accepts any caller-provided `M12PanelRunInput` that satisfies the writer's own service-layer regexes (UUID v4 + `sha256:<hex64>` fingerprint + three transcripts) and any caller-provided `panelAnchor` fields that satisfy the bcf substrate-layer CHECK constraints (`stage_code`, `sampling_status`, `grounding_check_result`, `verdict_code`, `model_identity_json.maker.provider` whitelist).

### 4.3 PR #160 demonstrated this, accurately

PR #160 at first-real-run-ts `2026-05-29T17-04-23-850Z`, panelRunUid `48629788-d1a1-419a-8240-013e4e485778`:

- Was a one-shot script that called `M12PanelRunWriterService.writePanelRun()` directly with hand-crafted content.
- Did NOT involve `MetricAuthoringPanelService.runPanel()`.
- Produced a row whose `verdict_code = 'PASS'` and whose `consensus_payload_json` is hand-crafted, not AJV-validated.
- Satisfies the substrate's storage-layer CHECKs but does not satisfy M12.5's read predicate at `bc-core/src/registry/mcf/metric-authoring-materialization.service.ts:365`, which throws `MaterializationPreconditionError` for any `verdict_code !== 'APPROVE_FOR_DRAFT'`.

**The row is correctly described as a writer-path proof commit with placeholder panel content.** It is not a real panel deliberation. It is not a materializable metric proposal. It is not a metric.

### 4.4 The DBCP lineage knew this — but did not resolve it

The M14/M12 governance DBCP (PR #23), M14 unblock apply DBCP (PR #24), and first-real-run DBCP (PR #25) explicitly scoped themselves to `M12PanelRunWriterService` and not to `MetricAuthoringPanelService`. The two-writer split is therefore not accidental. What was deferred is the architectural question of how the orchestrator's trust discipline reaches the post-A5 substrate.

---

## 5. The fracture, stated plainly

| Property | M12 orchestrator (`MetricAuthoringPanelService`) | M12 persistence writer (`M12PanelRunWriterService`) |
|---|---|---|
| Source path | `src/registry/mcf/metric-authoring-panel.service.ts` | `src/registry/metric-authoring/m12-panel-run-writer.service.ts` |
| 3-agent panel deliberation | ✓ | ✗ |
| AJV consensus_payload_json schema validation | ✓ | ✗ |
| Workbench fingerprint discipline | ✓ (`mcf-workbench-v1`) | ✗ (caller supplies any `sha256:<hex64>`) |
| HA-1..HA-9 enforcement | ✓ | ✗ |
| Allowlist + intake queue gating | ✓ | ✗ |
| Defect-code registry pin | ✓ | ✗ |
| Writes to current (post-A5) substrate | ✗ (writes `contract.*`; frozen by A4) | ✓ (writes `bcf.*` + `mcf.*`) |

**Trust discipline lives on one side. Working substrate persistence lives on the other.** Neither side alone is the M12 trust path. The fracture is between them.

---

## 6. Options

### 6.1 O1 — Adapter path (recommended unless infeasible)

Keep `MetricAuthoringPanelService` as the trust-bearing orchestrator. Refactor its Step 7 persistence to call `M12PanelRunWriterService.writePanelRun()` (or an injectable persistence port that the new writer implements) instead of executing raw `INSERT INTO contract.panel_output_record` SQL. After this change, the new writer becomes the orchestrator's bcf/mcf persistence adapter.

**Pros**
- Preserves the full M12 trust discipline that the orchestrator already carries.
- Routes that discipline through the post-A5 substrate without re-implementing it.
- Aligns with established BareCount practice — caller owns discipline, writer is a persistence service.
- Single trust path going forward; no parallel writer paths remaining.
- Does not require new substrate moves.

**Cons**
- Requires a code-change PR in `bc-core`. Not free.
- The orchestrator's existing integration spec (currently SAVEPOINT-rolled-back against `contract.*`) must be ported to assert against `bcf.*` / `mcf.*`.
- The orchestrator's TX layering (TX #A validate / TX #B writes / TX #C reject) must be reconciled with the writer's single-transaction shape, OR the writer must be invocable inside a caller-owned outer transaction (the writer's `writePanelRunInTx(tx, input)` already exists for this).
- Pre-existing operator-deferred prereqs from the M12 closeout (allowlist seed via `mcf-m12-seed-allowlists.mjs`, real vendor adapter wiring, intake row) remain pending and must still land before a real panel run.

### 6.2 O2 — Retirement path

Explicitly retire `MetricAuthoringPanelService` as the trust path. Define where the equivalent trust discipline will live next (likely a new orchestrator built around the writer, or a reorganized authoring service). The bare writer must NOT be allowed to stand alone as the trust path without that re-implementation; absent it, the post-A5 substrate has no trust gate at all.

**Pros**
- Allows a clean architectural restart if the existing orchestrator's design has aged out.
- Opportunity to revisit the 3-vendor / AJV / HA discipline against what the framework now needs.

**Cons**
- Discards working, reviewed, integration-tested code with full discipline and 6+ closeouts' worth of established pattern.
- Replacement orchestrator has to be specced, built, reviewed, and re-tested before any real metric work is possible. Long path.
- During the gap, the bare writer is the only post-A5 persistence path and has no trust discipline — every row it writes is structurally indistinguishable from the PR #160 placeholder. **Any operational use of the bare writer during the gap is a trust hole.**
- Forfeits the M12 closeout's verified discipline guarantees without a like-for-like replacement.

### 6.3 O3 — Staged migration path

Treat the orchestrator's substrate write as an A-series-style migration of its own. Author a governed DBCP that defines the specific code-and-substrate move from `contract.panel_output_record` to `bcf.panel_output_record` (and any necessary collaborator changes), with apply/closeout discipline matching the A1-A5 pattern.

**Pros**
- Matches the governance precedent set by A1-A5 — every substrate move was its own DBCP with apply + closeout evidence.
- Provides operator-authorization points at each step rather than embedding the change inside a code PR.
- Surfaces collaborator impact (FK chains, integration spec migration, lockfile assertions) before code is written.

**Cons**
- Heavier than O1. Multiple PRs, multiple operator authorizations, multiple closeout docs.
- The actual code delta may be small enough that the staged ceremony is disproportionate.
- Still ends at the same destination O1 reaches more directly (orchestrator writes to bcf/mcf via the new writer or an equivalent path).
- Does not by itself produce a metric — the operator-deferred M12 prereqs still apply.

---

## 7. Recommended decision

**O1 — Adapter path.** Unless an evidence-backed reason for infeasibility surfaces during implementation-PR design, refactor `MetricAuthoringPanelService` Step 7a to call `M12PanelRunWriterService.writePanelRunInTx(tx, input)` (the tx-bound variant already exists in the writer for exactly this kind of caller-owned-transaction pattern) instead of executing raw `INSERT INTO contract.panel_output_record` SQL.

**Why not O2.** Retirement is too expensive against the proven discipline already carried by the orchestrator. Retirement also leaves the bare writer as the only post-A5 path during the rebuild gap, which is a trust hole this DBCP is meant to close, not widen.

**Why not O3.** The orchestrator's substrate change is one ALTER-equivalent at the code layer (which table the INSERT targets — already abstracted by the new writer service). A1-A5-style ceremony is right when the substrate itself moves. Here the substrate has already moved (A5 landed); only the orchestrator's call site needs to follow it. A focused implementation PR is the proportionate response.

**If O1 turns out to be infeasible** during implementation design (for example: the orchestrator's TX boundaries cannot be reconciled with the writer's, or HA-1..HA-9 assertions cannot survive the persistence swap), then fall back to O3 — a governed staged migration. Falling back to O2 should require independent operator authorization.

---

## 8. Required downstream gates after this DBCP

Whichever option is selected, the path to "first real metric via bcf/mcf" still requires (in order):

1. **This DBCP merged** — locks the option.
2. **Implementation PR** for the selected option in `bc-core`. Under O1: refactor `MetricAuthoringPanelService` Step 7a to use the new writer. Under O3: substrate-migration DBCP first, then implementation. Under O2: replacement-orchestrator spec first, then implementation.
3. **Implementation evidence PR** — integration spec proves the refactored orchestrator writes to post-A5 substrate under SAVEPOINT-rolled-back conditions, HA-1..HA-9 still enforce, AJV still validates, fingerprint still binds.
4. **Operator-authorized resolution of M12 closeout's deferred prereqs** — allowlist seed via `mcf-m12-seed-allowlists.mjs`; vendor adapter real-API smoke run; first real M11 intake row.
5. **First real M12 panel run** — operator-authorized, through the trust-disciplined orchestrator now writing to bcf/mcf, producing `verdict_code = 'APPROVE_FOR_DRAFT'` on a real authoring-panel deliberation.
6. **First M12.5 materialization** — triggers off the row produced in step 5.
7. **First M13 PE-MC evaluation** — triggers off the row produced in step 6.
8. **First M14 publication** — separate operator-authorized gate.

Steps 4-8 are the "first real metric" lineage. They cannot begin in earnest until step 1 closes.

---

## 9. Explicit affirmations (what this DBCP does NOT do)

1. **Does NOT execute code.** No `bc-core` change in this PR.
2. **Does NOT invoke `MetricAuthoringPanelService.runPanel()`.**
3. **Does NOT invoke `M12PanelRunWriterService.writePanelRun()`.**
4. **Does NOT invoke `MetricAuthoringMaterializationService.runMaterialization()`.**
5. **Does NOT create a metric** (no MCF metric contract; no legacy `metric.metric_definition` write).
6. **Does NOT execute rollback.** A5 outcome (C) remains durable. C2 force-rollback envelope DBCP remains NOT AUTHORED (deferred per locked D4 of PR #25).
7. **Does NOT touch tenant DB.** Platform DB read-only only.
8. **Does NOT apply DDL or DML.**
9. **Does NOT retract PR #160's placeholder row.** The row at `panelRunUid 48629788-...` stays in substrate.
10. **Does NOT pre-authorize the implementation PR.** The implementation PR's authoring is a SEPARATE operator authorization step.

---

## 10. Standing operator constraints

- Operator stance ADR DEC-7f9597 / D423 — operator authorization required on every mutating gate.
- HR1..HR5 — substrate constraints, including HR4 tenant-scope-out-of-scope.
- D1..D8 of the first-real-run DBCP (PR #25) — locked; per-run authorization remains default for any future writer invocation.
- The bare `M12PanelRunWriterService.writePanelRun()` MUST NOT be operationally invoked outside the orchestrator after this DBCP merges. Operationally invoking the bare writer while this reconciliation is pending widens the trust hole rather than closing it.

---

## 11. Out-of-scope re-statement

This DBCP does not:

- Modify `bc-core` source.
- Apply DDL or DML.
- Invoke `MetricAuthoringPanelService.runPanel()` or `M12PanelRunWriterService.writePanelRun()` or `MetricAuthoringMaterializationService.runMaterialization()`.
- Author the implementation PR for the selected option.
- Author the C2 force-rollback envelope DBCP.
- Author the M11 / M9 / M10 / vendor-adapter follow-up DBCPs.
- Author the M14 publication gate DBCP.
- Author the legacy bridge sunset DBCP.
- Re-touch any merged A1-A5 / M14 unblock / first-real-run PR.
- Touch any tenant DB.

It only **decides** which architectural option closes the trust-path fracture, so the next operator-authorized implementation step has a settled premise.
