---
uid: DEC-29c80b
title: "Single-plane audit lifecycle — audit_pending before active; active means externally audited + calculator-grade"
description: "Insert audit_pending before active in the MCF lifecycle; active = externally audited + admitted + calculator-grade consumable. One-time governed back-entry of existing actives to audit_pending. No consumer repoint. Supersedes the two-plane release model (D522)."
status: decided
date: 2026-07-11T14:00:16.540Z
project: bc-core
domain: metrics
subdomain: metric-lifecycle
focus: governance
supersedes: DEC-6caf62
---

# Single-plane audit lifecycle — audit_pending before active; active means externally audited + calculator-grade

## Context

No production consumers ⇒ D522's release plane + released-current pointer + consumer repoint (bc-core A1-A7, bc-portal, bc-admin, bc-sdg, DevHub) is disproportionate — it solves continuity/backwards-compat problems the platform does not yet have. Calculator-grade reliability does not require two lifecycle planes; it requires that 'active' have one strict, universally-enforced meaning, which inserting audit_pending before active achieves. Materially less work: the entire consumption-repoint program is obviated because consumers already require active. The one real cost — zero active metrics between migration and first audit passes — is honest and acceptable pre-production. If/when production consumption begins and in-flight successor continuity becomes a real need, the two-plane model (D522, preserved in history) is the documented upgrade path. Auditor-side evidence/admission/NC/CR machinery is unchanged, so audit rigor is not reduced — only the platform state model simplifies.

## Decision

PRECONDITION VERIFIED (the fact that makes this safe): BareCount has NO production metric consumption yet — 0 fact.ms_* tables, no progression.metric_snapshot_index, no tenant metric values served, SDG/binding not begun (operator-confirmed 2026-07-11). The two-plane release model's continuity machinery (released-current pointer, prior-released-keeps-serving) solves a problem that does not exist pre-production.

DECISION (operator + Codex): a single lifecycle plane with the audit gate inserted before active:

  draft → review → approved → audit_pending → active (→ superseded)

- audit_pending = internally complete (PE-MC eligible), awaiting external audit. The resting state for newly-authored metrics and the entire back-migrated population.
- active = externally audited, admitted under the current gate policy, and calculator-grade consumable. ONE strict, universally-enforced meaning of 'active'. Existing consumers already require active, so NO consumer repoint is needed (this is the material simplification over D522: no separate release plane, no released-current pointer, no A1-A7 + frontend repoint).

THE GATE relocates from approved→active to audit_pending→active: the atomic admission predicate (resolve exactly one authenticated current external admission matching MCV + package + closure root + policy/engine/methodology; every audit axis + Directory-MCF conformance PASS; trusted non-revoked signer/import/artifact/admission; no blocking open NC) runs in-tx before the audit_pending→active flip. PR#462's assertExternalAuditAdmissionGate logic moves here. DB trigger backstop on audit_pending→active. No OPERATOR_REVIEW/sub-floor override.

FOUR HARD REQUIREMENTS (Codex): (1) a successor stays audit_pending WITHOUT displacing the prior active — is_current does NOT move to the successor until it passes audit; the active/is_current pointer flips atomically only on audit_pending→active. (2) no audit_pending→active without an exact current admission + closed blocking NCs. (3) audit revocation or evidence/closure drift removes production eligibility — via a governed active→audit_blocked transition (append-only cert, not a history rewrite) OR an effective-active currency check (settle in the DBCP). (4) ALL existing actives back-entered to audit_pending — no grandfathering.

MIGRATION: one-time governed back-entry of the 338 active MCVs to audit_pending via append-only governed transition certs (a migration/correction transition, NOT a history rewrite — the MCV identity/package stays immutable; only the lifecycle state transitions, cert-gated like retire/restore). Accepted consequence: after migration there may be ZERO active metrics until audits pass — honest and manageable pre-production.

ENUM: add audit_pending (and audit_blocked if requirement #3 is modelled as a state) to mcv_governance_state_chk. Auditor side UNCHANGED — append-only external_artifact_import, metric_audit_admission, NCs, CRs, signatures, and dependency-closure evidence are all retained; only the bc-core state model simplifies.

INTERIM FREEZE retired: the audit_pending→active gate is inherently fail-closed until admissions exist, so the temporary BCCORE_MCF_ACTIVATION_AUDIT_SENTINEL env flag is no longer needed once the gate lands (metrics simply rest at audit_pending). Chain-green (structural), Directory realized (realization exists), CC/OC active (contract chain), and MLS lifecycle remain distinct and unchanged.

## Amendment (Codex concurrence, 2026-07-11) — audit_blocked state selected; two corrections

The open question (revocation as an `audit_blocked` state vs an effective-active overlay) is resolved: **`audit_blocked` is a governed state.** An effective-active overlay is rejected — it would undermine the whole simplification (consumers could no longer trust `active`; every consumption path would need an extra currency predicate; a miss anywhere recreates the bypass; and "active but blocked" contradicts the strict meaning of active).

Governed transition set:

```
approved       → audit_pending
audit_pending  → active          (audit PASS + current admission + no blocking NC)
audit_pending  → audit_blocked   (audit FAIL or blocking NC)
active         → audit_blocked   (revocation, evidence/closure drift, or blocking NC)
audit_blocked  → audit_pending   (remediation submitted)
active         → superseded      (audited successor activates)
```

Each `→ audit_blocked` transition is an append-only event with a reason code; historical activation and audit evidence are untouched — only the current-state projection changes (Invariant III).

**Correction 1 — atomic invalidation.** Revocation import and the resulting `active → audit_blocked` must be atomic. Dependency drift originating *inside* bc-core (a changed upstream/closure) must trigger the *same* invalidation path, not a separate ad-hoc one.

**Correction 2 — "no consumer repoint" is a verification obligation, not a free lunch.** The claim holds only after proving every calculator-grade consumer fails closed on non-active status. Verification (2026-07-11) FOUND fail-open consumers that resolved by `is_current` without an `active` guard — `composite-metric-evaluation` (spec load + upstream metric_input join) and `beyond-metrics` (`snapshotForMetric`, `metricDetail`). Fixed in PR #463 (`governance_state_code = 'active'` added; no-op today since all `is_current` MCVs are active, forward-closed once `audit_pending` exists). Any future calculator-grade consumer must require `active`, never `is_current` alone.

**Continuity mechanism (requirement #1).** `is_current` MUST remain on the prior `active` MCV until the successor passes audit; the pointer flips atomically only on `audit_pending → active`. Authoring and audit workflows therefore locate the non-current `audit_pending` candidate explicitly (not by `is_current`). This is now the main continuity mechanism and requires a dedicated adversarial test in Track C (a successor audit-pending candidate must never displace the serving prior-active version, and must be findable though non-current).
