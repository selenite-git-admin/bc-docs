---
uid: DEC-1fbaf1
title: "BCF admission-error withdrawal — archival of vocabulary admitted in error, distinct from supersession"
description: "BCF admission-error withdrawal — archival of vocabulary admitted in error, distinct from supersession"
status: decided
date: 2026-06-26T10:06:55.345Z
project: bc-core
domain: platform
---

# BCF admission-error withdrawal — archival of vocabulary admitted in error, distinct from supersession

## Context

See decision text below.

## Context

The BCF vocabulary is immutable-atom (DEC-26b6e2). Post-activation, a characteristic's only change paths are `amendCharacteristicDefinition` (editorial, same meaning) and `supersedeCharacteristic` (meaning-bearing correction, which REQUIRES an active successor — one predecessor -> one successor). Both model a vocabulary that is correct-at-admission. Neither can RETRACT a row admitted in error.

The 2026-06-26 P1 defect audit (146 characteristics, 6 adversarial auditors against the Vocabulary Admission Checklist v1 + Vocabulary Evidence Framework §11) surfaced two wrong-layer rows: `fiscal period` and `normal balance side` — both RESOLVER-DERIVED (fiscal period from posting date via the tenant fiscal calendar, D364; normal balance side mechanically from account class code), i.e. canonical-resolution outputs wrongly admitted as source-attested BCF characteristics (§11.6 violation). `normal balance side` carries an active dependent Business Concept (`GL Account.normal balance side`). These have NO valid successor — they should not exist — so supersession does not apply, and there is no withdrawal path. Defective vocabulary cannot be removed, blocking a defect-free registry.

## Decision

Add `withdrawCharacteristic` (with a dependent-BC cascade), an ADMISSION-ERROR WITHDRAWAL operation distinct from supersession:

1. **Archival, not deletion.** Sets `archived_at = now()` on the characteristic and cascades to its dependent active Business Concepts. The row is PRESERVED — admission and withdrawal both remain in the record (Invariant III: state is immutable/historical; never hard-delete). `archived_at IS NOT NULL` already removes the row from the `uq_*_live` active set. No DDL — `archived_at` exists on characteristic, business_concept, entity.

2. **No successor.** Withdrawal RETRACTS a meaning admitted in error; supersession REPLACES a meaning with a corrected one. Distinct terminals: withdraw = active/draft -> archived (no successor); supersede = active -> superseded (with successor).

3. **Reference-safe cascade, HARD-REJECT (Invariant IV).** One transaction archives the characteristic + its dependent active BCs. The operation HARD-REJECTS (400, no write) if any dependent BC is bound into an active Metric Contract or Canonical Contract — the operator retires that contract usage first. Withdrawal never silently breaks the contract chain and never leaves a dangling reference.

4. **Evidenced (Invariant VI).** Emits a withdrawal certification (`action_code='registry_withdraw'`, subject_kind, rationale >=40 chars, operator sub) — proven, not inferred.

5. **Authorization.** High-risk (`registry_author_vocabulary` op family / new `withdrawCharacteristic` op), operator-confirmed.

## Foundation gate

Repair location B (the lifecycle grammar gains a terminal) + D (registry service). Invariants honored: III (soft-delete preserves history), IV (cascade + active-contract hard-reject), VI (withdrawal cert), I (no re-evaluation). No invariant violated.

## Scope

BCF `concept_registry` characteristic + business_concept. `withdrawEntity` is a symmetric future addition (same pattern). Code-only: service method + repo archive methods + controller endpoint + cert + the active-contract-reference guard + unit tests. The 22 definition-fixes from the audit use the existing `amendCharacteristicDefinition`; the 9 relabels use `supersedeCharacteristic`; only the 2 wrong-layer rows use `withdrawCharacteristic`.

## Distinct from supersession

supersede = active -> superseded WITH successor (correction); withdraw = active/draft -> archived WITHOUT successor (admission error). Editorial amendment (`amendCharacteristicDefinition`) = same id+term, definition updated in place (same meaning).</decision_text>
<status>decided</status>
<domain_text>concept-registry</domain_text>
<subdomain_text>vocabulary-lifecycle</subdomain_text>
<focus_text>lifecycle</focus_text>
</invoke>
<invoke name="Read">
<parameter name="file_path">C:\MyProjects\bc-core\src\registry\concept-registry\registry-authoring.service.ts
