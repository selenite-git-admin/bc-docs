---
uid: DEC-e8bea2
title: "Metric Directory onboarding integrity gates (the directory-entry integrity bar)"
description: "Metric Directory onboarding integrity gates (the directory-entry integrity bar)"
status: proposed
date: 2026-10-09T01:32:07.051Z
project: bc-core
domain: platform
subdomain: metric-directory
focus: onboarding-integrity-gates
---

# Metric Directory onboarding integrity gates (the directory-entry integrity bar)

## Context

Phase A is dispositioning 398 directory members that carry gaps: measureless base members, null-composition derived members, version-less group/family references, non-canonical temporal anchors, `derivation_json` drift, duplicate-active identities, and catalog orphans. Those are **symptoms**. The disease is that the directory onboarding/authoring surfaces **admit or finalize** these states, so cleaning without hardening the entry re-accumulates them on the next drive.

This ADR proposes the entry-time + finalize-time gates that make each bad-state class **unrepresentable or rejected at the source**. It is the directory analog of the catalog integrity bar (DEC-92f709) and the mechanical-integrity layer of the green-field program (DEC-ab630a). Repair location **A (source/admission) + B (contract semantics)**; no lower-layer compensation (DEC-c48b0f).

**Grounded this pass (read the bodies, not the comments):** bc-core `origin/main @d4abcba0` — `fn_member_version_finalize` (bc-db baseline L11412-11439), `checkMemberFeasibility`, `createMember` (L1039), `createMemberFromDirectorySpec` (L935; delegates to `createMember` at L1038), `buildVariableBindings` (L214), `setMemberDerivation` (L1700) + `validateDerivation` (L2074) + `assertNoGovernedVersion` (L1623), `createGroup`/`createFamily`, and the `fn_group/family_version_head_guard` + `fn_group/family_frozen_guard` family (bc-db baseline).

## Decision

Adopt **eight** directory-entry integrity gates. Each is enforced at **two layers**:

1. **Finalize-time class-guard** — a `SECURITY DEFINER` trigger (the `fn_member_version_finalize` / `fn_*_version_head_guard` family) that makes the bad state **unrepresentable on any write path** (governed route, `from-spec`, migration backfill, future route, or raw SQL by the schema owner). "Guard the class, not the instance."
2. **Admission-time source-fix** — the service refuses the bad shape early with a clean error AND, where a service **emits** a bad shape, the **emitter is fixed** (never a downstream scrubber).

Admission alone is insufficient (alternate write paths bypass it — exactly how the 398 arrived). Finalize alone is unergonomic (late, opaque) and blind to member-row-only state (`member.measure_concept_id`, which no member_version trigger sees). Both layers together are the bar. This mirrors the **already-live** `fn_group_version_head_guard`/`fn_family_version_head_guard` pattern (verified: they refuse a `supersedes`-NULL insert when a head exists, and `fn_stream_lock` serializes the race — an ABSENT-v1-only guarantee by construction).

No DDL for gates 1/2/3/5/6 (trigger + service strengthening). Gate 4's member-row class-guard and gate 8's terminal-reject leg are DB gates. Enablers being built now (Track-A version authoring, the F2 fix, the set-measure route, `rejectMember`) **must embed their gate on landing**. Gate 7 (one-active-per-identity) is **referenced** to the catalog/realization bar, not absorbed. Status `proposed` → normal review flow to `accepted` (operator / Codex).

## Rationale

**Grounded root cause (Gate 1).** `fn_member_version_finalize` checks, for `class_code='base'`, only `v_direct >= 1 AND v_dep = 0` — it does **not** require a direct input with `role_code='measure'`. So a base version whose only direct input is a `temporal_anchor` finalizes with **no measure**. The emitter is `buildVariableBindings` + `createMemberFromDirectorySpec`, which materialize a `temporal_anchor` direct input (`role_kind='input'`) and emit the measure only when `op='sum' && measureConceptId`. **Gate 1 (measureless base) and Gate 5 (non-canonical temporal anchor) are the same canonical-shape violation** (the F2 defect, TSK-ef89d8). The canonical base shape (the TSK-24cc24 ruling + C-FX-8 + package-v3 role-closure) is **measure-only** direct inputs; the temporal anchor is declared **once at the group** (`group.temporal_anchor_concept_id`) and carried by C-FX-8 row-stamping — never a member-version direct input.

**Foundation self-check.** (1) *Why A/B + finalize?* The states are admitted/finalized at the source; the fix is the missing declaration plus the finalize class-guard. (2) *Why not an upper layer?* The directory **is** the admission boundary for metric intent; the gates **are** the missing upper-layer declaration. (3) *Why not a lower layer?* A lower-layer scrubber is Phase-A cleanup, not prevention — the lower-layer compensation DEC-c48b0f forbids; we fix the emitter and the finalize contract. (4) *Design or execution act?* Gates 1/5 encode a **design act** (the canonical measure-only + group-declared-anchor shape, TSK-24cc24/C-FX-8); the finalize/admission changes **execute** it. Gates 2/3/6 execute already-declared contracts; Gate 8 executes DEC-85fd8d; Gate 7 references the catalog bar.

## Gate matrix

WHERE legend — **A** admission (service), **F** finalize (DB trigger), **R** member-row guard, **P** plane-boundary act.

**Gate 1 — measureless base version.** Forbid: a `class=base` member_version with no `role_code='measure'` direct input. WHERE/service: **F** — strengthen `fn_member_version_finalize` (base requires a measure-role direct input; measure-only) + **A** — `createMember` / `createMemberVersionForExistingMember` / `createMemberFromDirectorySpec` refuse a base version without a measure. Invariant: IV + VI. DDL: no. *FLAG-2 first requirement: enumerate the 95/110 (fold Platform's per-member report); mechanism grounded = the `v_direct>=1`-not-measure-role hole.*

**Gate 2 — null-composition derived.** Forbid: a `class=derived` member with no declared composition. WHERE/service: **F** already enforces, for derived, `v_dep>=1 AND v_direct=0` at the version level (keep) + **A/R** — a derived member must have a current version (deps enforced by finalize) or be honestly dispositioned, never a silent null. Invariant: IV + VI. DDL: no.

**Gate 3 — version-less group/family reference.** Forbid: a member bound to a group/family with no current version. WHERE/service: **A** — `createMember` already refuses (L1053-55), and `createMemberFromDirectorySpec` inherits it by delegating to `createMember` (L1038 — confirmed parity); `createGroup`/`createFamily` always mint v1; the Track-A route asserts-no-existing-version + appends. **F** — `fn_member_version_finalize` matches class/grain against the group_version, which must exist. Invariant: IV + III. DDL: no. Empty (0-member) version-less groups → archive, never version.

**Gate 4 — base member measure NULL (member row; the 153).** Forbid: a `class=base` member row with `measure_concept_id` NULL in use. WHERE/service: **A** — `createMember` requires a measure for base (currently nullable, L1065) + the set-measure route (§3a gap; the only governed bind) + member/version measure consistency. Prefer **no DDL** via the Gate-1 finalize guarantee + consistency; a member-row CHECK (`class_code <> 'base' OR measure_concept_id IS NOT NULL`) is an **optional later DB gate** that must follow the Phase-A cleanup of the 153. Invariant: IV.

**Gate 5 — non-canonical temporal anchor (F2, TSK-ef89d8).** Forbid: a member_version with a `temporal_anchor` direct input. WHERE/service: **A (fix the emitter)** — `buildVariableBindings` + `createMemberFromDirectorySpec` stop emitting the anchor direct input (measure-only per TSK-24cc24/C-FX-8) + **F** — finalize rejects a base version carrying a `temporal_anchor` direct input. Invariant: II + IV. DDL: no. Directory-plane only. *Separate (referenced, not absorbed):* the evaluation/mvb-plane anchor representation (`metric-directory.service.ts:294` — `time_anchor` is not a valid `mvb_role_kind`, so the maker envelope uses `role_kind='input'` + C-FX-8 row-stamp) is an **evaluation-plane** reconcile, distinct from the directory member_version direct-input rule here.

**Gate 6 — `derivation_json` drift from `member_version_dependency`.** Forbid: `member.derivation_json` that is not a faithful projection of the current version's `member_version_dependency`. WHERE/service: **A** — `validateDerivation` (L2074) currently checks only ref-existence + acyclicity, **not** consistency with `member_version_dependency`; add the projection-consistency check. Invariant: IV + one-source-of-truth (DB rule 4). DDL: no. *Concrete finding:* `setMemberDerivation` calls `assertNoGovernedVersion` (L1623), which refuses a member that has a current version; so for a **versioned** member the composition lives only in `member_version_dependency`, and `derivation_json` (hence `v_member_depends_on`) is empty and cannot be set post-hoc. Design: `member_version_dependency` is the single source; `derivation_json` must be a **projection** (computed / a view, or populated at version-mint), never an independent post-hoc `setMemberDerivation` on a versioned member. (This also blocks the morning F3 plan's "`setMemberDerivation` on the 14 versioned members" — flagged to Chief/Metric separately.)

**Gate 7 — duplicate-active catalog contract per identity.** Forbid: more than one active `mcf.metric_contract` bound to one directory-member identity. WHERE/service: **P** — the realization/catalog plane (`realizeMember` + MCF admission refuse a second active per identity); the directory contributes identity-minted-once. Invariant: IV. Ownership: belongs to the catalog bar (DEC-92f709) — **referenced, not absorbed**.

**Gate 8 — orphan: catalog contract with no directory member.** Forbid: a catalog contract with no member, silently. WHERE/service: **P/A** — adopt (keyed on **identity** = measure + grain + discriminator, not name) OR honest reject-with-reason. Invariant: VI + DEC-85fd8d. DDL: **yes** for the reject leg (bc-db 0035 applied + the `rejectMember` act; grant `0a35dc47`).

## Enabling dependencies (the §3a gaps — prerequisites)

- `rejectMember` act + bc-db 0035 → Gates 2, 8.
- the set-measure route → Gate 4.
- adopt / identity-reconcile → Gate 8.
- the Track-A group/family version route → Gate 3 (Foundation-checked PASS @`cad6fbd5`).

Each enabler **must embed its gate on landing**; the Architect reviews each at its head.

## Authority

DEC-c48b0f (design act / no lower-layer compensation), DEC-92f709 (catalog deterministic-gate bar), DEC-ab630a (green-field three integrity layers), DEC-85fd8d (directory entry rejection terminal state), the TSK-24cc24 ruling + C-FX-8 (canonical measure-only + group-declared anchor), the metric-directory charter §5/§6/§8, DB rule 4 (one source of truth per value).

## Sequencing

Parallel to / follow-on from Phase-A execution; do **not** block the prepped cleanup. Enablers embed their gates immediately. The FLAG-2 finalize-hole (Gate 1) + the F2 emitter fix (Gate 5) are the first build piece (same canonical-shape enforcement). Then Platform builds each gate through the review flow (no-DDL where possible; any schema change = DB gate).
