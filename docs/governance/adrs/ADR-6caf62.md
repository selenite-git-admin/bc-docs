---
uid: DEC-6caf62
title: "Calculator-grade release plane — external audit gates active→released via a two-pointer release-admission plane"
description: "External audit gates production consumption at a separate release-admission plane (active→released), not the MCF lifecycle; two current pointers (internally-active vs released-current); interim approved→active freeze stays until consumers are repointed."
status: superseded
superseded_by: DEC-29c80b
date: 2026-07-11T13:46:55.590Z
project: bc-core
domain: metrics
subdomain: metric-lifecycle
focus: governance
---

# Calculator-grade release plane — external audit gates active→released via a two-pointer release-admission plane

## Context

The approved→active freeze halted authoring and left the 338 existing actives as an awkward grandfather. Gating release/consumption instead of activation lets authoring + internal MCF publication continue to active while preserving a hard production boundary, and classifies the existing population honestly (active-unreleased) with no history rewrite. Modelling release as a separate append-only event plane (not a governance_state value) keeps revocation/re-audit from mutating lifecycle backward (Invariant III) and reflects that audit currency is orthogonal to and revocable independently of the authoring lifecycle. The two-pointer separation is required so a prior released version keeps serving while its successor awaits audit. Refines (does not reverse) the D519/DEC-3d6eeb consumption-boundary enforcement intent; supersedes the approved→active enforcement point trialled under MCF-ACT-006/PR#462 (whose gate logic relocates to the active→released transition). The interim freeze must persist through the whole cutover because active still leaks into SDG/binding/runtime/upstream resolution until those are repointed.

## Decision

Operator + external auditor (Codex bc-core-release-audit-gate-requirement-v2) agreed to move the external-audit enforcement point from approved→active to a governed active→released calculator-grade boundary. Semantic split: active = internally complete + current in the MCF authoring/lifecycle plane + eligible for external audit; released = externally audited, admitted under the current gate policy, calculator-grade consumable.

TWO INDEPENDENT PLANES (released is NOT a governance_state_code value):
1. MCF lifecycle (unchanged): draft→review→approved→active→superseded.
2. Release admission: effective status DERIVED from append-only release/revocation/expiry/supersession events. Statuses: AUDIT_PENDING, RELEASED, AUDIT_BLOCKED, RELEASE_STALE, REVOKED. Revocation appends an event; it never deletes the release, changes its historical verdict, or moves MCV lifecycle backward (Invariant III).

TWO CURRENT POINTERS: (a) internally-current-active MCV (MCF is_current); (b) released-current MCV — an explicit governed selection (NOT is_current, version_seq, or wall-clock). A successor may go active + audit-pending while the prior released MCV keeps serving production; the released-current pointer moves atomically only on successful release of the successor (or explicit revocation of the prior release). This prevents the current is_current demotion from causing either a production outage or an unaudited-consumption bypass.

RELEASE EVENT (append-only, cert-bound): exact MCV + package signature + dependency closure root + imported audit artifact + admission UID + all independent audit-axis results + Directory-to-MCF conformance + gate-policy/engine/methodology/signer/canonicalization versions + actor/timestamp + prior released event superseded. Idempotent only for the exact MCV/package/closure/admission/policy tuple.

ATOMIC RELEASE PREDICATE (one tx, stable snapshot): lock MCV+MC+release-selection coordinate; recompute package signature + full closure; resolve exactly one authenticated current admission matching MCV/package/closure/policy/engine/methodology; require every applicable audit axis + semantic-conformance PASS; require trusted non-revoked signer/import/artifact/admission; require no blocking open NC; write release event; atomically move released-current pointer. DB trigger / constrained release writer backstops: no released-current selection without a matching admission-linked release event. No OPERATOR_REVIEW/sub-floor override.

CONSUMPTION RULE: every calculator-grade boundary resolves the released-current MCV, never merely active — SDG admission + synthetic generation, tenant binding, production metric evaluation, externally-presented calculator-grade values, released derived-metric evaluation, action/intervention paths. A derived MCV can be internally active over merely-active upstream, but cannot be RELEASED unless every upstream metric-input resolves to an exact current released MCV in the audited transitive closure. Release currency is rechecked at consumption (dependency/policy/signer/engine/methodology/NC/revocation change can make a prior release stale without rewriting history).

DISTINCT SURFACES PRESERVED: chain-completeness green = structural/source-chain readiness (NOT audit PASS); Directory realized = an MCF realization exists (add a separate released signal); MCF active = internally active (NOT production-released); audit status is never inferred from lifecycle labels. UI may combine lifecycle + release status into one badge but APIs/evidence keep them as separate filterable fields (labels: Active-Audit Pending, Active-Audit Blocked, Released, Active-Release Stale, Release Revoked).

EXISTING 338 ACTIVE MCVs: classified through the release plane (current PASS+admission→releasable; pending→AUDIT_PENDING; failure/blocking-NC→AUDIT_BLOCKED; stale package/closure→RELEASE_STALE; revoked→REVOKED). No indefinite active-equals-released grandfather.

CUTOVER (inseparable): release enforcement + consumption repointing are one cutover. The interim approved→active freeze (BCCORE_MCF_ACTIVATION_AUDIT_SENTINEL) MUST stay armed until every consumer is repointed to released-current — disarming earlier lets active leak into production. Sequence: inventory consumers → build import/admission/release-event/revocation/released-selection substrate → atomic release gate + backstop → repoint every calculator-grade consumer → import/recompute existing population → prove adversarial refusal + old-released/new-active continuity → only then remove the freeze.
