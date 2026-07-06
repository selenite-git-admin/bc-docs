---
uid: business-context-framework-ci-harness-plan
title: Business Context Framework (BCF) — CI Substrate + §13 Harness Plan
description: Two load-bearing decisions for the CI substrate + §13 enforcement harness. Driven by E2 sub-finding S1 (no .github/workflows/ exists in the surveyed BareCount repos). Most CI decisions are obvious and deferred to the implementation PR; this document captures only the two that need pre-implementation thinking.
status: draft
date: 2026-05-19
project: bc-docs
domain: contracts
subdomain: catalog
focus: governance
session: SES-23fc7e
revised_in: SES-48710f
---

# Business Context Framework (BCF) — CI Substrate + §13 Harness Plan

## Why this document is short

An earlier 274-line version of this plan locked 8 decisions. Self-review concluded that 6 of them were obvious — a competent engineer surveying the repos and reading build-plan §13 makes the same calls in a 30-minute design pass at the top of the implementation PR. Pre-litigating obvious decisions in a separate session was governance-of-governance, not load-bearing planning.

This trimmed version preserves **two genuinely consequential decisions** (workflow location and recursive bootstrap) and defers the rest to the implementation session.

The full prior version is recoverable from git history (commit `f2519cf`) if context is needed.

## Inputs

- `business-context-framework-build-plan.md` §13 (spec source)
- `business-context-framework-inventory.md` §2.9 (defect-surface verdicts)
- `business-context-framework-inventory-gap-research.md` §2 (G-findings)
- `business-context-framework-helper-script-trust-catalog.md` §6 S1 (no CI substrate exists)

## Decision 1 — Workflow file location

**Options:**
- (a) **Per-repo `.github/workflows/`** — each repo carries its own copy of the §13 check workflows
- (b) **Central reusable workflow in bc-docs-v3** — one definition; thin per-repo workflows reference it via `uses: selenite-git-admin/bc-docs-v3/.github/workflows/bcf-13-gate.yml@main`

**Decided: (b) Central reusable workflow in bc-docs-v3.**

**Rationale:** Spec lives in bc-docs-v3 (build-plan §13, inventory §2.9, gap-research §2). Co-locating enforcement with spec keeps source-of-truth unitary. Per-repo (option a) duplicates the workflow definition and drift becomes inevitable — E2 already proved the cost of unaudited per-source divergence (138/156 hardcoded scripts).

**Cost of being wrong: medium.** If reusable workflow proves too rigid (some repo needs a check the others don't), splitting later is N×1 PR. Same cost for the reverse. Edge to central because the §13 spec is unitary by design (§13.8 anti-pattern explicitly forbids divergence).

**Implementation note:** the reusable workflow couples bc-docs-v3 availability to all consuming repos' CI. If bc-docs-v3 has an access issue, CI in all consuming repos fails simultaneously. Worth verifying during implementation that the cross-repo `uses:` syntax works with the existing repo access model.

## Decision 2 — Recursive bootstrap (CI's own §13 compliance)

**Problem.** Per §13.1 no behavior-changing PR merges without §13 trailers. The first CI PR creates the gate. If the gate must be running for the PR to pass, the first PR can't pass.

### Bootstrap exception (operator-locked form, SES-fb016a)

> Until CI exists, the CI-substrate PR may use ad-hoc BuildPlan IDs (`CI-S1`, `CI-S2`, …) and manual reviewer verification against §13. This exception applies only to PRs whose primary purpose is creating or enabling the CI harness. Once the first enforcing workflow lands, subsequent PRs must use normal BuildPlan IDs unless explicitly grandfathered in the CI PR body.

**Two tightenings vs an unbounded exception:**

1. **Scoped by PR purpose.** The exception applies only to PRs whose primary purpose is creating or enabling the CI harness. An adjacent unrelated PR cannot piggyback on the bootstrap to skip trailer enforcement.
2. **Explicit grandfathering.** Once the first enforcing workflow lands, any continued use of `CI-S<n>` IDs (or any other variance from normal BuildPlan IDs) requires explicit listing in the CI PR's body under a `## Grandfathered IDs` heading. Silent persistence of the bootstrap shape is not permitted.

### Operational shape

- **First CI PR:** carries §13 trailers in commit message; uses `CI-S<n>` IDs; reviewer manually verifies trailers per §13.7 reviewer-layer enforcement; PR body contains a `## Bootstrap exception` heading citing this section by URL/anchor.
- **BuildPlan-ID validator (implemented in that first PR):** accepts `^CI-S\d+$` in addition to `^[ABCDE]\d+$` so the bootstrap commits remain valid after CI starts enforcing.
- **Follow-up build-plan amendment** (optional; implementation session's call): if the CI substrate grows beyond ~3 PRs and `CI-S<n>` proliferates, a follow-up driver session may prepend Phase 0 (CI substrate) and re-label CI-S<n> as P0-<n>. If it amendments, the CI PR that lands the rename must explicitly list the grandfathered IDs in its `## Grandfathered IDs` section so subsequent PRs cannot silently extend the exception.

**Cost of being wrong: low.** The exception is bounded by PR purpose (limits blast radius) and explicit grandfathering (prevents silent persistence). Both are the operator-named tightenings vs the looser prior form.

## Deferred to implementation PR (decide in the PR design notes, not here)

These are obvious enough that a planning document doesn't add value over a competent engineer's design pass at the top of the PR:

- **CI platform.** GitHub Actions (repos are on GitHub).
- **Trailer-presence check shape.** Squash-merge target commit. Check all 7 §13.2 trailers present; fail if any missing.
- **BuildPlan-ID validator source-of-truth.** Parse build-plan §1–§5 at CI runtime; promote to a `_machine/` manifest if markdown-format friction proves high.
- **Defect-tag-grep source list.** Parse gap-research §2 G-findings + inventory §2.9 13 defect surfaces at CI runtime; same v1/v2 escape hatch as above.
- **Phase0Impact validator.** Closed-enum string match on `{none, increases, decreases}`. If `increases`, PR body must contain a substantive `## Phase 0 workload impact` subsection (reviewer-checked, not CI-checked).
- **Rollout sequence.** bc-docs-v3 first (dogfood the reusable workflow), then bc-core (where Phase A substrate lands), then bc-admin / bc-ai / bc-portal. Dry-run for a small batch of PRs before flipping to enforcing — the implementation session picks the batch size based on observed false-positive rate.
- **Specific regex bodies, YAML body design, negative-test fixtures** — all implementation concerns.

The implementation session writes its own design notes for these at the top of its PR. Reviewers check the design notes against §13.7 (CI-vs-reviewer split) at PR review.

## Entry criteria for the implementation session

The implementation session can open when:

1. This plan is committed (decisions 1 and 2 locked).
2. Operator confirms the bootstrap exception form (manual reviewer-verification of first CI PR's trailers).

The implementation session opens its own session UID. Expected first deliverable: a single dogfooding PR in bc-docs-v3 landing the reusable workflow + bc-docs-v3 thin local workflow + bc-docs-v3 enters dry-run mode.

## Cross-reference

| Document | Why referenced |
|---|---|
| `business-context-framework-build-plan.md` §13 | The spec this plan implements enforcement for |
| `business-context-framework-inventory.md` §2.9 | Defect-surface source #2 |
| `business-context-framework-inventory-gap-research.md` §2 | Defect-surface source #1 (G-findings) |
| `business-context-framework-helper-script-trust-catalog.md` §6 S1 | The finding that drove this plan into existence |
| `docs/adrs/ADR-149ab2.md` (DEC-149ab2 / D411) | Authority context |
