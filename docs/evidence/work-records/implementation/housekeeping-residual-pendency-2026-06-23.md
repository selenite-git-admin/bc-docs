---
title: Housekeeping Residual Pendency (2026-06-23)
description: Post-housekeeping manifest after the 5-commit deferred-docs cleanup pass landed all 43 previously-dirty bc-docs-v3 paths. Records what intentionally remains pending in adjacent repos / runtime state (the dirty bc-core Layer 2 worktree, the runtime worktree carrying bc-core PID 29912, and bc-ai PID 28444), why each is held, and the next cleanup track per item.
status: closed
authority: implementation-checkpoint
date: 2026-06-23
project: bc-docs-v3
domain: governance
subdomain: housekeeping
focus: residual-pendency
related_docs: [mms-recovery-closeout-2026-06-23.md, bcf-wave-b-fast-track-parity-closeout-2026-06-23.md, bcf-orphan-characteristic-decision-inventory-2026-06-23.md]
---

# Housekeeping Residual Pendency (2026-06-23)

## Scope

After the 5-commit deferred-docs cleanup pass (commits `bcfba25 d25af42 1976bba bf89706 98d2814` landed all 43 previously-dirty bc-docs-v3 paths), this manifest records what intentionally remains pending in adjacent repos and runtime state. bc-docs-v3 itself is at **zero pendency** post-housekeeping: `git status` clean; this file is the final pending artifact and gets its own commit.

## bc-docs-v3 — zero pendency after this commit

| State | Result |
|---|---|
| `git status` (immediately before this manifest) | clean |
| Housekeeping commits landed | 5 (see §"Commit ledger" below) |
| Files intentionally not committed | none |
| `devhub_doc_scan` post-commit | 890 files scanned, +2 indexed (the two operating-model MMS chapters), 0 updated, 0 retired, 888 unchanged |

### Commit ledger

| SHA | Group | Subject |
|---|---|---|
| `bcfba25` | A | docs(governance): consolidate ADR registry repair artifacts from 2026-06-22 audit pass |
| `d25af42` | B | docs(mms): land semantic-refactor doctrine + MMS chapters + Layer 1/2/3 inventories |
| `1976bba` | C | docs(mms): close PCIC v2 recovery arc — verifier v2 + evidence-fingerprint |
| `bf89706` | D | docs(mcf): file MCF framework audit + briefing + pre-doctrine decisions |
| `98d2814` | E | docs(bcf): DEC-fb0b12 + Wave A/B closeouts + characteristic doctrine arc |

## bc-core primary worktree (`C:\MyProjects\bc-core`)

**Status: dirty. Intentionally untouched per operator standing rule.**

| Metric | Value |
|---|---|
| HEAD | `f83ac2b7` (`[main]`) |
| `git status -s` line count | **511** |
| Content | Layer 2 (Implementation Names) semantic-refactor work-in-progress under DEC-54f221: code identifier renames (M11–M15, PE-MC-*, L-V*, C-FX-*, B6/C5/F3/B10, C1/C2/F1/F2 → semantic names) across bc-core/src/**. Some `git mv` filename renames staged in prior batches. |
| Why held | Operator standing rule for the entire session: **do not touch the dirty `C:\MyProjects\bc-core` worktree** — Layer 2 reconciliation is its own batch, not coupled to runtime/recovery/BCF work. |
| Risk of reconciliation | The Layer 2 hunks overlap with regions of `metric-publication-eligibility-evaluator.service.ts` + `.spec.ts` that bc-core PR #355 + PR #356 modified on `origin/main`. A clean rebase/merge against current main will require resolving conflicts in those files. |
| Next cleanup track | A future operator-authorised "Layer 2 reconciliation" session, run in a dedicated focused batch separate from this housekeeping pass. The MMS recovery and BCF Waves were intentionally driven through a side worktree (`bc-core-runtime`) so this reconciliation could be deferred without blocking other work. |

## bc-core runtime worktree (`C:\MyProjects\bc-core-runtime`)

**Status: clean (only the operator-authorised `node_modules` symlink) — currently serving bc-core PID 29912.**

| Metric | Value |
|---|---|
| HEAD | `c63db8ed` (detached) |
| Created (per operator authorisation) | 2026-06-23 during MMS recovery sequence |
| `git status -s` | `?? node_modules` (symlink to `C:\MyProjects\bc-core\node_modules`, per runtime-worktree recipe) |
| Why held | Currently serving bc-core PID 29912 (see §"Background processes"). Tearing down requires stopping the process; teardown drops the clean runtime checkpoint that includes DEC-fb0b12 / mcf-verifier-v2 / DDL-15 behavior. **No reason to tear down unless ending the session.** |
| Next cleanup track | When the session ends or runtime use ceases: stop bc-core PID 29912 → `git worktree remove C:\MyProjects\bc-core-runtime` → the next dev cycle starts bc-core afresh from the primary worktree (once Layer 2 is reconciled or in a new isolated worktree). |

## Background processes

| Port | PID | Process | Source |
|---|---|---|---|
| 3100 | 29912 | bc-core | `C:\MyProjects\bc-core-runtime\dist\main` (started 2026-06-23 ~07:00 UTC, ~4 hours uptime at this commit) |
| 4300 | 28444 | bc-ai | `C:\MyProjects\bc-ai` (started 2026-06-23 during runtime preflight) |

**Why both stay running:** session-state continuity. No active work is using them at the moment, but next-session restart from clean main + bc-ai venv would take ~1–2 minutes; leaving them up costs nothing. Operator may stop them when ending the session. Per the runtime-worktree recipe in `feedback_runtime_worktree_recipe.md`, `Stop-Process -Id <pid> -Force` is the clean shutdown.

## legacy v2 archive (legacy archive)

Not inspected in this housekeeping pass. Per DEC-3395bc (D373) / DEC-c06f41 (D378), v2 is read-only legacy reference; new authoring lands in v3 only. Out of scope.

## Substrate-side residuals (informational; not housekeeping targets)

These exist in the data substrate and are not files. Listed here only so the next session has full context.

| Item | State | Disposition |
|---|---|---|
| Parked panel `be8bea24-…` (Sales Order × net amount) | Sits in `bcf.panel_output_record` with `verdict_code=OPERATOR_REVIEW`. | **Obsolete** — successor BC was authored via fresh panel `60669a2e-…` after DEC-fb0b12 broadened the `net amount` definition. Left intact as audit history per Foundation Invariant III. Do not confirm. |
| Parked panel `0a5d2e5c-…` (Sales Order Line × line number) | Same substrate state. | **Obsolete** — successor BC was authored via fresh panel `28a5a02e-…` with operator-pinned `identifier/string/identity` shape. Left intact as audit history. Do not confirm. |
| `fiscal period` characteristic (`ef143792-…`) | `lifecycle_state='draft'`, no BC bindings. Forbidden as a BCF characteristic name per Vocabulary Evidence Framework §11.6. | Per orphan-inventory amendment (§8 of `bcf-orphan-characteristic-decision-inventory-2026-06-23.md`): doctrine-driven housekeeping item — leave in draft, archive, or formally renounce. **Not a BC-authoring act.** Deferred operator decision. |
| Stuck MCV (Billing Cycle Time) | Not active post-MMS recovery; sits in non-`active` state on `bc_platform_dev`. | Per `mms-recovery-closeout-2026-06-23.md` and runtime-recovery inventory: deferred to a separate diagnosis cycle. Not BCF-blocking. |

These are not bc-docs-v3 housekeeping concerns. They are noted here purely for cross-session situational awareness.

## Required operator decisions (none for housekeeping; only for future work)

This housekeeping pass surfaced **no** decisions that the operator must make to reach zero docs pendency. The decisions listed below are forward-looking — they govern future work tracks, not the cleanup completed here.

| Future track | Decision the operator will eventually make |
|---|---|
| Layer 2 reconciliation | Whether to commit the 511-line dirty bc-core worktree as one batch or split it into per-cluster commits per ADR DEC-54f221. |
| Cluster G (bc-ai prompts) | Whether to authorise fresh fixture-capture against bc-ai for the regression discipline named in `mms-layer1-cluster-g-prompt-regression-plan-2026-06-22.md`. |
| Layer 3 (Compatibility Names) | Whether to open the additive-only enum-alias work named in `mms-layer3-compatibility-names-inventory-2026-06-23.md`. |
| `fiscal period` housekeeping | Whether to archive the draft row, leave it permanently in draft, or formally renounce per §11.6. |
| Bank Statement Line × line number outlier | Whether to remediate the `count/integer/amount` outlier (supersession to `identifier/string/identity`) or classify it as a banking-domain exception per the Wave B closeout. |
| Billing Cycle Time stuck MCV | Whether to open a separate diagnosis cycle for the R4 Chain Delta / CC-OC Delta classification. |
| SI Line × ordered quantity | Whether to clarify the `ordered quantity` definition (editorial amendment under DEC-fb0b12) before authoring this binding. |

None of these decisions block this commit. They are recorded so a future session does not have to re-discover them.

## Next cleanup track (recommendation)

There is no **next cleanup track**. bc-docs-v3 is at zero pendency. Future work tracks are governed by their own holds (named above), each with its own operator-authorisation gate.

If the operator wants to end the current session cleanly: stop the two background processes, optionally remove the runtime worktree, and the platform returns to a fully quiesced state with all artifacts committed.
