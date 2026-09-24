---
uid: DEC-fa9424
title: "Metric authoring is Directory-primary — Member-anchored M12 door in bc-admin; retire the seed-primary Register entry"
description: "The Directory Member becomes the sole UI authoring entry (member-anchored M12 panel door, no-black-box); the seed-primary Register page/nav retires, POST /mcf/intakes/from-seed 410-retires, intake-queue control plane re-homes; Catalog copy corrected (TSK-1a2a15)."
status: implemented
date: 2026-09-20T07:35:44.015Z
project: bc-core
domain: metrics
subdomain: metric-directory/authoring
focus: ui-control-plane
---

# Metric authoring is Directory-primary — Member-anchored M12 door in bc-admin; retire the seed-primary Register entry

> **Provenance and status history (reconciled 2026-09-24, bc-docs#59; TSK-0f1782).** This body is the Codex-reviewed text of DEC-fa9424 exactly as merged in bc-core PR #789 (merge `9b23029933`, `docs/design/adr-fa9424-directory-primary-metric-authoring.md`, blob `83598cde7fde12bfadccd121f6aef1a73988e90b`, unchanged on bc-core `main`). Only the frontmatter status and this note differ. The earlier bc-docs file carried the pre-review registry text at `proposed`.
> - **proposed** — 2026-09-20 07:35 UTC: recorded in DevHub (SES-d418b6).
> - **decided** — 2026-09-20 08:07 UTC: after bc-core #789, the ADR review PR, drew CHANGES_REQUESTED from bc-auditor-app (07:48 UTC), addressed round 1, was APPROVED (08:02 UTC), and merged at 08:02 UTC.
> - **implemented** — 2026-09-20 13:06 UTC: after every delivery slice below had merged:
>   - **S1:** bc-core #792 (11:56 UTC), bc-admin #48 (12:07 UTC), bc-admin #49 (12:39 UTC);
>   - **S3:** bc-core #791 (09:13 UTC);
>   - **S2** (including the D6 Catalog copy fix): bc-admin #50 (13:05 UTC).
>   - The later Member-create door (bc-core #794, bc-admin #51, TSK-4d89d0) builds on this decision; it is not required for its status.

## Context (grounded study, SES-d418b6, 2026-09-20 — read-only)

**Doctrine.** `bc-docs/docs/operating-model/metric-directory.md` (draft-authoritative) §8: *"Seeds are secondary … never the worklist authority. (This inverts the earlier seed-primary model.)"* D506 (DEC-b5c7ff) realized the Directory in bc-core (own-intent / derive-realization; keystone at materialization; Phase 5 retires the seed-primary stores). D507 (DEC-5842d4) Phase 1.6 fixed the intended flow — *"pick a directory member → drive → draft"* — and its deterministic envelope generator is live (`GET /api/metric-directory/members/:memberUid/envelope`, `metric-directory.controller.ts:554`, base members only). DEC-d894de requires every workflow to carry three legs: SOP + programmatic flow + UI control plane.

**Code reality.** The bc-core member-anchored chain is complete end to end:

- `POST /mcf/intakes` accepts `directory_member_uid` and lands it in reservoir provenance (`mcf-intake.controller.ts:59`);
- the M12 panel threads it (`metric-authoring-panel.service.ts:635`);
- M12.5 materialization stamps the provenance keystone into `metric_contract.candidate_source_ref_json` (`metric-authoring-materialization.service.ts:1267`);
- realization authority is the D523 typed append-only ledger (`metric_directory.realization_event` + `realization_operative`), asserted only by the separate governed act `PATCH /metric-directory/members/:uid/realize` (actor + authority_ref + rationale). Materialization does **not** emit a realization event — the keystone JSON is provenance only. The realization guard `verifyRealizableMcv` (`metric-directory.service.ts:1626`) accepts only an MCV in governance state `approved|active`; M12.5 materialization produces a **draft** MCV, so realization is never assertable straight off a materialize.

bc-admin contradicts the doctrine at every front door:

1. The Directory authoring door (`MetricCandidateAuthoringPage`, `/catalog/metrics/directory/author`) is **free-form** — its `toIntake()` never sets `directory_member_uid` although `CreateIntakeInput` supports it.
2. `MemberDetailPage`'s Realization card says *"Realize it on-demand via the metric authoring panel"* — with **no action**. There is no per-Member authoring entry anywhere.
3. The seed-primary entry is alive and promoted: `MetricRegistrationPage` at `/catalog/metrics/register`, listed in the **Onboarding** group of both `TopNavbar.tsx:71` and `LeftSidebar.tsx:84`, backed by `POST /mcf/intakes/from-seed`; `/catalog/metrics/create` and `/seed` redirect into it.
4. `MetricCatalogPage` teaches the inverted model in three places: the header comment (*"authoring now enters via Register → MCF intake"*), the subtitle (*"New metrics enter via Register (seed → MCF intake → M12 panel)"*, line 159) and the empty state (*"register a seed to begin"*, line 171).

**Live substrate (platform DB, 2026-09-20).** 380 active directory members. Of **433** metric contracts: 355 `operator_direct` (238 member-keystoned), 72 legacy `other`, and **6 — ever — from `seed_metrics`** (~1.4%). Intake queue: 481 `operator_direct` rows (269 member-anchored) vs 19 `seed_metrics` rows (12 consumed, 5 pending, 2 rejected). Member-anchored authoring is the de-facto path — but only through the MCP drive. The UI leg is the missing DEC-d894de third leg.

**Trigger.** Operator caught the contradiction in SES-9c706c (bc-admin UI quality pass) when a proposed "Register Metric" button merge into the Catalog would have cemented the to-be-inverted seed-primary UX; the change was reverted and TSK-1a2a15 raised (critical-path).

## Decision

### D1 — The Member is the sole UI authoring entry

A new metric is authored in bc-admin **only from a Directory Member**. Free-form (memberless) candidate authoring retires together with the seed door: an idea that deserves authoring first becomes intent — Family → Group → Member via the existing governed create doors (`FamilyGroupAuthoring`, `POST /metric-directory/members`) — then is authored from that Member. This is metric-directory.md §1/§8 and D506 D2 applied to the UI: the Directory is the worklist authority; the M12 panel is the authoring boundary.

The programmatic leg (`devhub_metric_drive`, operator-direct API) is untouched — this ADR governs the UI control plane.

### D2 — Member-anchored M12 door

`MetricCandidateAuthoringPage` becomes member-anchored:

- **Route:** `/catalog/metrics/directory/members/:memberUid/author`. The old `/catalog/metrics/directory/author` route is removed (not redirected — it had no stable external audience).
- **Entry points:** (a) an **"Author via M12 panel"** action on `MemberDetailPage`'s Realization card, shown only when the member is unrealized and unarchived; (b) a row-level action on the Members tab for unrealized members. The tab-level free-form "Author metric" CTA is removed.
- **Pre-fill, locked identity:** candidate name locked to `member_code`; description pre-filled from `member_knowledge.definition_text`/`rationale_text` (editable — the panel benefits from operator narrative); `grain_hint` derived from the group grain (entity + temporal anchor); `formula_hint` from `formula_intent_text`/`derivation_json`. All derived values are **displayed, not hidden**.
- **Member context stays visible during authoring:** the member's spec (class, group, theme, discriminator) and the concept-coverage card (realizability), so a `bcf_gap` member is authored eyes-open — the UI **warns** on gaps but does not gate; preflight/panel/PE-MC remain the enforcement of record (doctrine §8 "surfaced gap, never a silent skip"; feasibility-server correctness is TSK-209877, orthogonal).
- **Wire-through:** `toIntake()` sets `directory_member_uid`. No bc-core change needed — the chain (context §"Code reality") already carries it to the keystone.
- Both base and derived members may enter the door; the panel adjudicates the candidate either way.

### D3 — The UI leg keeps the M11/M12 intake path

The door continues to run `POST /mcf/intakes` → `POST /mcf/panel-runs` (hint-based intake). The D507 Phase-1.6 envelope generator remains the **drive path's** deterministic leg (it produces a maker envelope for preflight + drive, base members only). Converging the two authoring machineries (envelope-backed UI authoring) is explicitly deferred — a candidate follow-on once this door is proven, not a blocker for it.

### D4 — Realization stays a separate, explicit governed act, gated by MCV governance state *(revised per Codex PR #789 review r1)*

M12.5 materialization stamps provenance only and yields a **draft** MCV. The realization guard (`verifyRealizableMcv`, `metric-directory.service.ts:1626` — the migration-37/P0-2 posture) accepts only an `approved|active` MCV, so realization is **not assertable at materialization time**. The governed sequence is therefore three explicit acts: **materialize (draft, M12.5) → approve/activate (M13/M14, MCF governance) → assert realization (D523 ledger, Directory governance)** — and the UI states it rather than hiding it:

1. **Outcome surface (post-materialize):** does **not** offer realization. Alongside the draft-MCV link it states the prerequisite verbatim: *"Draft created. Realization can be asserted from the member's Realization card once this version is approved (M13)."*
2. **Return path (MemberDetailPage Realization card):** for an unrealized member, the card lists the MCVs carrying this member's provenance keystone, each with its live `governance_state_code`, via a thin read-only surface (the member-detail read extended, or a small `GET /metric-directory/members/:uid/realization-candidates`; no schema). The list is **provenance-labeled display, never realization state** (TSK-d37d1b posture). **"Assert realization"** (`authority_ref` + `rationale` → `PATCH members/:uid/realize`) enables only for an `approved|active` MCV; for a draft it renders disabled with the prerequisite shown.
3. The act is never auto-emitted, and it is **not** coupled to M13 approval either — approval remains an MCF governance act, realization remains a Directory governance act (coupling either pair would be silent chain wiring, DEC-ebf0b4). Non-member-anchored materializations (drive/API) are unaffected.

### D5 — Retire the seed-primary Register entry

1. **Nav:** remove "Register Metric" from `TopNavbar` and `LeftSidebar` (Onboarding group).
2. **Routes:** `/catalog/metrics/register`, `/catalog/metrics/create`, `/catalog/metrics/seed` all redirect to `/catalog/metrics/directory`.
3. **Page:** `MetricRegistrationPage`'s seed-browse/register leg is deleted, with `registerSeedViaMcf` and the seed-browse hooks in `seed-metrics.ts`.
4. **Control plane survives:** the page's "Registration Queue" tab (M11 intake queue + governed Cancel, reject reason ≥ 20 chars) is the only intake-queue UI and must not die with the page. It re-homes as an **"Intake queue"** tab on the Metric Directory page (the authoring worklist context), listing all intakes (operator_direct + residual seed rows) with the existing cancel act.
5. **bc-core:** `POST /mcf/intakes/from-seed` **410-retires** (house pattern, D481/D547), citing this ADR. The `seed_metrics` reservoir rows and the 19 seed intake rows are **retained as evidence** (doctrine §8: seeds are evidence and coverage) — no DB change. The 5 pending seed intakes are dispositioned by the operator through the existing governed cancel, not by code.
6. The DevHub-side `onboarding_candidate` store retirement (D506 Phase 5, devhub repo) is **out of scope** here — tracked separately.

### D6 — Correct the Catalog's stale seed-primary copy

`MetricCatalogPage`: header comment, subtitle (line 159) and empty state (line 171) are rewritten to Directory-primary language (e.g. subtitle: *"New metrics are authored from the Metric Directory (Member → M12 panel)"*; empty state: *"No governed metric contracts yet — author from a Directory member"*).

### D7 — No-black-box visibility contract (unchanged, extended)

The door keeps the BCF/MCF minimal pattern already in `MetricCandidateAuthoringPage`/`McfAuthoringOutcome` (DEC-d894de): three visible phases (form → panel running → outcome); verdict + per-role adjudication (maker/checker/judge, grounding, defect/review reason) shown **verbatim**; rejection is a legitimate outcome that materializes nothing while the intake + panel run remain the audit trail; materialize is a distinct `mcf_publisher` act. D2's member-context panel and D4's explicit realization act extend the same posture: every write in the loop is a visible, attributable act.

### D8 — Sequencing and fences

- bc-admin work lands **after** the held `claude/ui-quality-pass` branch merges (it moves the same nav files); rebase, don't fork the nav.
- **No schema changes.** No panel/verdict logic changes. No changes to `devhub_metric_drive` or the envelope generator.
- **No new dependence on `candidate_source_ref_json`** — realization reads stay on the D523 typed-ledger views; the keystone JSON remains provenance only (aligned with TSK-d37d1b).
- One PR per delivery slice; Codex is reviewer/auditor of record.

## Foundation / invariant check

Repair location **F** (UI control plane / read model) plus one endpoint retirement (D, subtractive). No change to A–E substance.

| # | Invariant | How honored |
|---|---|---|
| I | Meaning evaluated once | The door feeds intent to the M12 boundary; it derives hints from the member spec and never computes realized semantics. |
| III | State immutable | Realization stays on the append-only D523 ledger; rejection leaves the intake + panel run as immutable audit trail. |
| IV | References explicit | `directory_member_uid` threaded intake→panel→keystone; realization by exact MCV uid via the governed act. |
| VI | Evidence emitted, not inferred | Panel provenance shown verbatim; realization asserted with authority + rationale, never inferred from materialization. |

DB rules: no DDL, no new columns, no cached state. The 410 retirement follows the D481/D547 house pattern.

## Alternatives considered

- **Keep Register alongside the member door** — rejected: cements the inverted model the doctrine explicitly kills; live data shows the path produced 6 of 433 MCs.
- **Merge Register into the Catalog as a button** — proposed in SES-9c706c, caught and reverted by operator ruling; rejected here for the record.
- **Auto-emit the realization event at M12.5 materialization** — rejected for v1: silent chain wiring (DEC-ebf0b4), couples the MCF publisher act to directory authority, and changes a governed write path; also structurally impossible as-is — the draft MCV fails the `approved|active` realization guard.
- **Offer "Assert realization" immediately on the post-materialize outcome surface** — the original D4; rejected on Codex PR #789 review r1: materialization yields a draft MCV, the guard requires `approved|active`, so the offered act would fail every time. Replaced by the stated three-act sequence + the Realization-card return path.
- **Relax the realization guard to accept draft MCVs** — rejected: the `approved|active` requirement is the migration-37/P0-2 posture (an unapproved declaration is not a realizable subject); weakening a governance trigger to serve UI convenience inverts the authority relationship.
- **Envelope-generator-backed UI authoring** — deferred (D3): different machinery (preflight/drive), base-only today; unification is a follow-on, not a precondition.
- **Hard-block authoring of `bcf_gap` members in the UI** — rejected: the UI warns and surfaces; preflight/panel are the enforcement of record, and a hard UI gate would duplicate (and drift from) server rules (TSK-209877 territory).

## Delivery slices (each a Codex-reviewed PR)

1. **S1 (bc-admin + one thin bc-core read):** member-anchored door — route, entry points on MemberDetailPage + Members tab, pre-fill/lock, member-context + coverage display, `directory_member_uid` wire-through; post-materialize prerequisite notice (D4.1); MemberDetailPage Realization card gains the provenance-labeled MCV list + governance-state-gated "Assert realization" (D4.2), backed by the thin realization-candidates read (read-only, no schema). After `ui-quality-pass` merges.
2. **S2 (bc-admin):** Register retirement — nav removal, redirects, page deletion, intake-queue re-home to the Directory page, Catalog copy fix (D6).
3. **S3 (bc-core):** `POST /mcf/intakes/from-seed` 410 retirement + tests; no data changes.

## Scope fences

No DB schema changes; no panel prompt/verdict/roster changes; no `devhub_metric_drive` changes; no bulk data acts; no devhub `onboarding_candidate` retirement (separate program); no changes to realization-ledger semantics.

## References

TSK-1a2a15 (this ADR's task) · metric-directory.md §1/§8/§11 · DEC-c3e57f (D422) · DEC-b5c7ff (D506) · DEC-5842d4 (D507, Phase 1.6) · DEC-d894de (three-leg, no black boxes) · DEC-ebf0b4 (no unverified chain wiring) · D523 realization ledger (migration 37) · DEC-67f399 (class doctrine) · TSK-d37d1b (keystone → typed relation; provenance-only JSON) · TSK-209877 (feasibility fix) · SES-9c706c checkpoint #7 (trigger) · SES-d418b6 checkpoint #1 (grounded study).
