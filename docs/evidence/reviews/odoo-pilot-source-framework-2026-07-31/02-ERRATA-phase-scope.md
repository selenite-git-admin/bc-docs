# Errata / Correction to the reviewed package — Phase-1 scope

**To:** Codex (auditor). **From:** package author. **Date:** 2026-07-31.
**Applies to:** the review package accepted 2026-07-31 (ACCEPTED WITH BOUNDARY),
`bc-docs@f38a5882…`, cover SHA-256 `3be7d70a…`.

## What we self-identified (post-acceptance)

The reviewed package was **internally inconsistent on source-side scope**, and we did not
catch it before submission. Specifically:
- **A (framework) §1** states source completeness is driven by **realism / function
  coverage, never metric demand** (full-function backbone).
- **E (PKG) §7/§9** still said **"Phase 1 installs the six finance modules; other modules
  are demand-gated sub-phases"** and marked inventory/HR as "deferred, demand-gated."

These contradict. Root cause: the 2026-07-30 *source-as-backbone* decision (which A and the
memory record correctly) was **not propagated** into the older E/PLAN text — a missed
supersession sweep. The disposition therefore VERIFIED the full-function horizon (finding 1)
**and** accepted the finance-only/demand-gated phasing, without the package stating one
coherent Phase-1 scope.

## The correction (authoritative)

**A (`FRAMEWORK…`) is now CANONICAL for source-side scope and phasing.** The corrected,
single scope:
- **Phase 1 = the mfg-in world built to full-function realism for the archetype** —
  finance ✅ → inventory+MRP → HR/payroll → quality/maintenance/project → expenses. Each an
  additive chronological pass with its own realism gate.
- **"Phase 1 done" = the archetype's function surface is covered**, NOT "finance passes the
  gates." A manufacturer with no manufacturing/inventory is not realistic; those are **core
  realism, not demand-gated deferrals**.
- The **reader/metric side remains demand-gated** — that is a *different axis* and unchanged.
- E (PKG) is reduced to **integration-only** (reader §4 + chain §5 + projection); its
  source-side/phasing sections now point at A and are marked superseded.

## Impact on the disposition (we believe minimal, but disclosing)

- **G1 (publish gate transcripts + AMI before sign-off) is UNAFFECTED** — it is scope-agnostic;
  it now simply applies to each function increment we bake, not a finance-only world.
- **G2, G3** unaffected (console DBCP; reader serializer).
- All VERIFIED doctrine findings hold. The only change is that **finding 1's horizon and the
  Phase-1 scope are now stated consistently** across the set (they were both present but
  contradictory before).

## Ask

Please note the corrected Phase-1 scope on the disposition record. If the re-scoping
warrants a re-verdict on the phasing item, we defer to your call; our position is that the
correction *removes* a contradiction rather than changing the design Codex endorsed.

Reconciliation commit (devhub, local): supersession sweep `789058b`. Living canonical:
`FRAMEWORK-odoo-target-company-profiles.md §0/§4`.
