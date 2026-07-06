# v4 Migration Plan

Inventory run: `1`
Source documents: `972`
Documents with migration decisions: `972`

This report combines the first-pass control-plane classification and the second-pass undecided review. It does not copy prose from v3. `regenerate_from_source` rows remain intentionally unimported until generators rebuild them from current source.

## Decision Summary

| Decision | Files |
|---|---|
| migrate_governance | 479 |
| migrate_evidence | 281 |
| migrate_current | 92 |
| migrate_reference | 89 |
| regenerate_from_source | 23 |
| archive_only | 7 |
| reject_do_not_migrate | 1 |

## Target Kinds

| Target Kind | Files |
|---|---|
| adr | 471 |
| evidence_work_record | 158 |
| current_chapter | 92 |
| evidence_dbcp | 73 |
| source_system_reference | 61 |
| evidence_closeout | 37 |
| curated_reference | 28 |
| generated_reference | 23 |
| evidence_audit | 10 |
| errata | 8 |
| archive_only | 7 |
| evidence_ledger | 3 |
| retired_not_migrated | 1 |

## Reader Visibility

| Visibility | Files |
|---|---|
| governance | 479 |
| evidence | 281 |
| primary | 92 |
| reference | 89 |
| hidden | 24 |
| archive | 7 |

## Current Truth Flag

| Current Truth | Files |
|---|---|
| 1 | 555 |
| 0 | 417 |

## High-Confidence Current Chapters

| Section | Source | Target |
|---|---|---|
| ai | ai/ai-agents.md | docs/ai/ai-agents.md |
| ai | ai/ai-architecture.md | docs/ai/ai-architecture.md |
| ai | ai/ai-gates.md | docs/ai/ai-gates.md |
| ai | ai/ai-overview.md | docs/ai/ai-overview.md |
| ai | ai/ai-trust-and-verification.md | docs/ai/ai-trust-and-verification.md |
| ai | ai/ai-usage-visibility.md | docs/ai/ai-usage-visibility.md |
| ai | ai/bedrock-and-inference-profiles.md | docs/ai/bedrock-and-inference-profiles.md |
| compliance | compliance/compliance-overview.md | docs/compliance/compliance-overview.md |
| compliance | compliance/infosec-and-access-control.md | docs/compliance/infosec-and-access-control.md |
| compliance | compliance/iso-27001-conformance.md | docs/compliance/iso-27001-conformance.md |
| compliance | compliance/privacy-and-the-immutable-fact.md | docs/compliance/privacy-and-the-immutable-fact.md |
| compliance | compliance/risk-and-vendor-management.md | docs/compliance/risk-and-vendor-management.md |
| compliance | compliance/soc-2-conformance.md | docs/compliance/soc-2-conformance.md |
| development | development/build-and-release.md | docs/development/build-and-release.md |
| development | development/decision-and-change-procedure.md | docs/development/decision-and-change-procedure.md |
| development | development/developer-experience.md | docs/development/developer-experience.md |
| development | development/development-overview.md | docs/development/development-overview.md |
| development | development/devhub.md | docs/development/devhub.md |
| development | development/documentation-system.md | docs/development/documentation-system.md |
| development | development/metric-readiness-toolkit.md | docs/development/metric-readiness-toolkit.md |
| development | development/quality-assurance.md | docs/development/quality-assurance.md |
| foundation | foundation/foundation-overview.md | docs/foundation/foundation-overview.md |
| foundation | foundation/the-authority-model.md | docs/foundation/the-authority-model.md |
| foundation | foundation/the-contract-grammar.md | docs/foundation/the-contract-grammar.md |
| foundation | foundation/the-dual-layer-interaction-model.md | docs/foundation/the-dual-layer-interaction-model.md |
| foundation | foundation/the-evaluation-boundaries.md | docs/foundation/the-evaluation-boundaries.md |
| foundation | foundation/the-governed-selection.md | docs/foundation/the-governed-selection.md |
| foundation | foundation/the-invariants.md | docs/foundation/the-invariants.md |
| foundation | foundation/the-object-model.md | docs/foundation/the-object-model.md |
| foundation | foundation/the-problem.md | docs/foundation/the-problem.md |
| foundation | foundation/the-solution.md | docs/foundation/the-solution.md |
| implementation | implementation/api-surface.md | docs/implementation/api-surface.md |
| implementation | implementation/architecture.md | docs/implementation/architecture.md |
| implementation | implementation/audit-and-activity-logging.md | docs/implementation/audit-and-activity-logging.md |
| implementation | implementation/auxiliary-services.md | docs/implementation/auxiliary-services.md |
| implementation | implementation/backend-services.md | docs/implementation/backend-services.md |
| implementation | implementation/business-concept-registry.md | docs/implementation/business-concept-registry.md |
| implementation | implementation/data-model-and-schema.md | docs/implementation/data-model-and-schema.md |
| implementation | implementation/frontend-experience.md | docs/implementation/frontend-experience.md |
| implementation | implementation/implementation-overview.md | docs/implementation/implementation-overview.md |
| implementation | implementation/infrastructure.md | docs/implementation/infrastructure.md |
| implementation | implementation/internal-modules.md | docs/implementation/internal-modules.md |
| implementation | implementation/notifications-and-webhooks.md | docs/implementation/notifications-and-webhooks.md |
| implementation | implementation/synthetic-data-and-testing.md | docs/implementation/synthetic-data-and-testing.md |
| onboarding | onboarding/business-field-and-business-object-onboarding.md | docs/onboarding/business-field-and-business-object-onboarding.md |
| onboarding | onboarding/canonical-contract-creation.md | docs/onboarding/canonical-contract-creation.md |
| onboarding | onboarding/canonical-field-seeding.md | docs/onboarding/canonical-field-seeding.md |
| onboarding | onboarding/metric-workstream.md | docs/onboarding/metric-workstream.md |
| onboarding | onboarding/multi-standard-onboarding.md | docs/onboarding/multi-standard-onboarding.md |
| onboarding | onboarding/observation-contract-creation.md | docs/onboarding/observation-contract-creation.md |
| onboarding | onboarding/onboarding-overview.md | docs/onboarding/onboarding-overview.md |
| onboarding | onboarding/reader-creation.md | docs/onboarding/reader-creation.md |
| onboarding | onboarding/seed-catalog-management.md | docs/onboarding/seed-catalog-management.md |
| onboarding | onboarding/source-and-admission-contract-creation.md | docs/onboarding/source-and-admission-contract-creation.md |
| onboarding | onboarding/source-registration.md | docs/onboarding/source-registration.md |
| onboarding | onboarding/tenant-metric-binding.md | docs/onboarding/tenant-metric-binding.md |
| onboarding | onboarding/tenant-onboarding.md | docs/onboarding/tenant-onboarding.md |
| operating-model | operating-model/action-evaluation.md | docs/operating-model/action-evaluation.md |
| operating-model | operating-model/admission-and-observation.md | docs/operating-model/admission-and-observation.md |
| operating-model | operating-model/business-vocabulary.md | docs/operating-model/business-vocabulary.md |
| operating-model | operating-model/canonical-evaluation.md | docs/operating-model/canonical-evaluation.md |
| operating-model | operating-model/chain-completeness-and-verdict.md | docs/operating-model/chain-completeness-and-verdict.md |
| operating-model | operating-model/connectors-and-readers.md | docs/operating-model/connectors-and-readers.md |
| operating-model | operating-model/contract-chain-assembly.md | docs/operating-model/contract-chain-assembly.md |
| operating-model | operating-model/evidence-and-lineage.md | docs/operating-model/evidence-and-lineage.md |
| operating-model | operating-model/fiscal-time-and-temporal-gates.md | docs/operating-model/fiscal-time-and-temporal-gates.md |
| operating-model | operating-model/mcf-legacy-bridge.md | docs/operating-model/mcf-legacy-bridge.md |
| operating-model | operating-model/metric-catalog.md | docs/operating-model/metric-catalog.md |
| operating-model | operating-model/metric-evaluation.md | docs/operating-model/metric-evaluation.md |
| operating-model | operating-model/metric-management-system-recovery-track.md | docs/operating-model/metric-management-system-recovery-track.md |
| operating-model | operating-model/metric-management-system.md | docs/operating-model/metric-management-system.md |
| operating-model | operating-model/operating-model-overview.md | docs/operating-model/operating-model-overview.md |
| operating-model | operating-model/quality-gates-and-chain-integrity.md | docs/operating-model/quality-gates-and-chain-integrity.md |
| operating-model | operating-model/source-change-classification.md | docs/operating-model/source-change-classification.md |
| operating-model | operating-model/sources-and-the-catalog.md | docs/operating-model/sources-and-the-catalog.md |
| operating-model | operating-model/tenancy-and-binding.md | docs/operating-model/tenancy-and-binding.md |
| operating-model | operating-model/tenant-entitlement-enforcement.md | docs/operating-model/tenant-entitlement-enforcement.md |
| operating-model | operating-model/tenant-extensions-and-overrides.md | docs/operating-model/tenant-extensions-and-overrides.md |
| operations | operations/demo-operations.md | docs/operations/demo-operations.md |
| operations | operations/deployment-topology.md | docs/operations/deployment-topology.md |
| operations | operations/incident-and-change-management.md | docs/operations/incident-and-change-management.md |
| operations | operations/observability-and-telemetry.md | docs/operations/observability-and-telemetry.md |
| operations | operations/operations-overview.md | docs/operations/operations-overview.md |
| operations | operations/performance-and-scale.md | docs/operations/performance-and-scale.md |
| operations | operations/runtime-operations.md | docs/operations/runtime-operations.md |
| operations | operations/runtime-runbook.md | docs/operations/runtime-runbook.md |
| operations | operations/security-operations.md | docs/operations/security-operations.md |
| operations | operations/support-and-escalation.md | docs/operations/support-and-escalation.md |
| operations | operations/tenant-lifecycle-and-subscription.md | docs/operations/tenant-lifecycle-and-subscription.md |
| operations | operations/upgrade-and-migration.md | docs/operations/upgrade-and-migration.md |
| overview | overview/platform-overview.md | docs/overview/platform-overview.md |
| overview | overview/structural-differentiators.md | docs/overview/structural-differentiators.md |

## Regenerate Instead Of Copy

| Source | Planned Target | Rationale |
|---|---|---|
| api/README.md | docs/reference/api/README.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/README.md | docs/reference/data-dictionary/README.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/admin.md | docs/reference/data-dictionary/admin.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/contract.md | docs/reference/data-dictionary/contract.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/envelope.md | docs/reference/data-dictionary/envelope.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/evidence.md | docs/reference/data-dictionary/evidence.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/execution.md | docs/reference/data-dictionary/execution.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/fact.md | docs/reference/data-dictionary/fact.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/infrastructure.md | docs/reference/data-dictionary/infrastructure.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/master.md | docs/reference/data-dictionary/master.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/metric.md | docs/reference/data-dictionary/metric.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/operations.md | docs/reference/data-dictionary/operations.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/organization.md | docs/reference/data-dictionary/organization.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/pricing.md | docs/reference/data-dictionary/pricing.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/progression.md | docs/reference/data-dictionary/progression.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/runtime.md | docs/reference/data-dictionary/runtime.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/source.md | docs/reference/data-dictionary/source.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/support.md | docs/reference/data-dictionary/support.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/tenant.md | docs/reference/data-dictionary/tenant.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/tenant_dim.md | docs/reference/data-dictionary/tenant_dim.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/test_bench.md | docs/reference/data-dictionary/test_bench.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| data-dictionary/users.md | docs/reference/data-dictionary/users.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |
| schemas/README.md | docs/reference/schemas/README.md | Generated references must be rebuilt from current source, not copied from stale v3 output. |

## Evidence Preserved Outside Reader Flow

| Evidence Kind | Files |
|---|---|
| evidence_work_record | 158 |
| evidence_dbcp | 73 |
| evidence_closeout | 37 |
| evidence_audit | 10 |
| evidence_ledger | 3 |

## Undecided Review Queue

Total undecided: `0`

| Guessed Kind | Source | Reason |
|---|---|---|

## Next Migration Gates

1. Clean link/path findings from `target-audit.md`, starting with missing internal links and legacy doc-root references.
2. Build generators for API, schemas, and data dictionary before importing generated references.
3. Run a correctness pass on primary reader-flow chapters against `bc-core` coverage.
4. Keep source v3 read-only until explicit cutover.
