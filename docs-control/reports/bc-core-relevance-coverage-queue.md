# bc-core Relevance And Coverage Queue

Generated: `2026-07-06T13:17:05.607029+00:00`
Audit run: `80`

This queue is a prioritization aid. `generated_only` means the control plane has generated inventory coverage, not necessarily human explanatory coverage.

## Priority Summary

| Priority | Coverage Depth | Fact Type | Facts |
|---|---|---|---|
| high | uncovered | env_var | 2 |
| high | uncovered | guard | 4 |
| high | uncovered | interceptor | 1 |
| medium | current_claim_unverified | env_var | 6 |
| medium | generated_only | controller | 96 |
| medium | generated_only | endpoint | 449 |
| medium | generated_only | env_var | 403 |
| medium | generated_only | module | 7 |
| medium | generated_only | service | 43 |
| low | current_claim_unverified | schema_table | 116 |
| low | generated_only | module | 25 |
| low | generated_only | schema_table | 393 |
| low | generated_only | script_command | 34 |
| low | generated_only | service | 79 |

## Top Code Areas Without Current Grounding

| Code Area | Priority | Coverage Depth | Facts |
|---|---|---|---|
| src/registry | high | uncovered | 3 |
| src/auth | high | uncovered | 2 |
| src/common | high | uncovered | 2 |
| scripts | medium | generated_only | 386 |
| src/boundary | medium | generated_only | 82 |
| src/registry | medium | generated_only | 82 |
| src/registry/source-catalog | medium | generated_only | 62 |
| src/registry/mcf | medium | generated_only | 57 |
| src/registry/bcf | medium | generated_only | 34 |
| src/tenant-views | medium | generated_only | 32 |
| src/registry/readers | medium | generated_only | 31 |
| src/registry/contracts | medium | generated_only | 23 |
| src/registry/concept-registry | medium | generated_only | 21 |
| src/registry/connections | medium | generated_only | 19 |
| src/platform/masters | medium | generated_only | 17 |
| src/test-bench | medium | generated_only | 17 |
| src/registry/execution | medium | generated_only | 16 |
| src/nullification | medium | generated_only | 15 |
| src/evidence | medium | generated_only | 11 |
| src/schema-provisioner | medium | generated_only | 10 |
| src/admin-inspection | medium | generated_only | 9 |
| src/mls | medium | generated_only | 9 |
| src/registry/meta-schemas | medium | generated_only | 9 |
| src/platform | medium | generated_only | 8 |
| src/tenant-management | medium | generated_only | 7 |
| scripts | medium | current_claim_unverified | 6 |
| src/support | medium | generated_only | 6 |
| src/auth | medium | generated_only | 4 |
| src/readiness | medium | generated_only | 4 |
| src/tenant-metrics | medium | generated_only | 4 |
| src/function-admin | medium | generated_only | 3 |
| src/progression | medium | generated_only | 3 |
| src/tenancy | medium | generated_only | 3 |
| src/boundary/reader-runtime | medium | generated_only | 2 |
| src/platform/vendor-costs | medium | generated_only | 2 |
| src/registry/d443-phase2-cert-supply | medium | generated_only | 2 |
| src/registry/framework-approval | medium | generated_only | 2 |
| src/registry/harness-apply | medium | generated_only | 2 |
| src/docs | medium | generated_only | 1 |
| src/health | medium | generated_only | 1 |

## Critical And High Priority Code Fact Samples

| Priority | Fact Type | Symbol | Source Path | Evidence | Generated Claims | Current Claims |
|---|---|---|---|---|---|---|
| high | env_var | NODE_ENV | src/registry/legacy-metric-authoring.guard.ts | process.env reference | 0 | 0 |
| high | env_var | VITEST | src/registry/legacy-metric-authoring.guard.ts | process.env reference | 0 | 0 |
| high | guard | SuperAdminGuard | src/auth/guards/super-admin.guard.ts | guard class | 0 | 0 |
| high | guard | TenantClaimGuard | src/auth/guards/tenant-claim.guard.ts | guard class | 0 | 0 |
| high | guard | IdempotencyGuard | src/common/guards/idempotency.guard.ts | guard class | 0 | 0 |
| high | guard | legacy-metric-authoring.guard | src/registry/legacy-metric-authoring.guard.ts | guard class | 0 | 0 |
| high | interceptor | IdempotencyStoreInterceptor | src/common/interceptors/idempotency-store.interceptor.ts | interceptor class | 0 | 0 |

## Current Documents With Ungrounded Claims

| Document | Ungrounded Claims |
|---|---|
| docs/implementation/internal-modules.md | 31 |
| docs/implementation/audit-and-activity-logging.md | 30 |
| docs/implementation/api-surface.md | 18 |
| docs/development/documentation-system.md | 17 |
| docs/implementation/synthetic-data-and-testing.md | 14 |
| docs/implementation/backend-services.md | 13 |
| docs/development/metric-readiness-toolkit.md | 12 |
| docs/onboarding/business-field-and-business-object-onboarding.md | 12 |
| docs/development/quality-assurance.md | 10 |
| docs/operating-model/metric-management-system.md | 10 |
| docs/development/build-and-release.md | 8 |
| docs/implementation/frontend-experience.md | 8 |
| docs/onboarding/source-registration.md | 8 |
| docs/development/decision-and-change-procedure.md | 7 |
| docs/onboarding/canonical-field-seeding.md | 6 |
| docs/operations/observability-and-telemetry.md | 6 |
| docs/operations/upgrade-and-migration.md | 6 |
| docs/reference/technical-notes/implementation/metric-context-framework-gap-survey.md | 6 |
| docs/onboarding/source-and-admission-contract-creation.md | 5 |
| docs/overview/platform-overview.md | 5 |
| docs/reference/technical-notes/implementation/business-context-framework-b6-track2-survey.md | 5 |
| docs/reference/technical-notes/implementation/core-chain-golden-path.md | 5 |
| docs/compliance/iso-27001-conformance.md | 4 |
| docs/compliance/risk-and-vendor-management.md | 4 |
| docs/onboarding/multi-standard-onboarding.md | 4 |
| docs/operations/runtime-runbook.md | 4 |
| docs/implementation/auxiliary-services.md | 3 |
| docs/implementation/infrastructure.md | 3 |
| docs/operating-model/chain-completeness-and-verdict.md | 3 |
| docs/reference/runbooks/operations/cognito-identity-remediation.md | 3 |
| docs/reference/technical-notes/implementation/business-context-framework-b6-design-survey.md | 3 |
| docs/reference/technical-notes/implementation/metric-context-framework-m12-panel-framework-calibration-followup.md | 3 |
| docs/implementation/data-model-and-schema.md | 2 |
| docs/implementation/notifications-and-webhooks.md | 2 |
| docs/onboarding/metric-workstream.md | 2 |
| docs/onboarding/observation-contract-creation.md | 2 |
| docs/operating-model/mcf-legacy-bridge.md | 2 |
| docs/operating-model/metric-management-system-recovery-track.md | 2 |
| docs/operations/security-operations.md | 2 |
| docs/reference/source-systems/rbi.md | 2 |
| docs/reference/source-systems/sap-dm.md | 2 |
| docs/reference/source-systems/sap-licensing-reference.md | 2 |
| docs/reference/technical-notes/implementation/business-context-framework-helper-script-trust-catalog.md | 2 |
| docs/reference/technical-notes/implementation/finance-package-v0-gold-universe.md | 2 |
| docs/compliance/infosec-and-access-control.md | 1 |
| docs/development/devhub.md | 1 |
| docs/implementation/architecture.md | 1 |
| docs/implementation/implementation-overview.md | 1 |
| docs/onboarding/canonical-contract-creation.md | 1 |
| docs/onboarding/onboarding-overview.md | 1 |
| docs/onboarding/seed-catalog-management.md | 1 |
| docs/operating-model/evidence-and-lineage.md | 1 |
| docs/operations/demo-operations.md | 1 |
| docs/operations/operations-overview.md | 1 |
| docs/reference/source-systems/chargebee.md | 1 |
| docs/reference/source-systems/hubspot.md | 1 |
| docs/reference/source-systems/index.md | 1 |
| docs/reference/source-systems/razorpay.md | 1 |
| docs/reference/source-systems/sap-s4hana.md | 1 |
| docs/reference/technical-notes/implementation/business-concept-registry-f4-governed-vocabulary-seed-design.md | 1 |
| docs/reference/technical-notes/implementation/mcf-re-entry-index.md | 1 |
| docs/reference/technical-notes/implementation/metric-context-framework-m12-first-real-run-disposition.md | 1 |
