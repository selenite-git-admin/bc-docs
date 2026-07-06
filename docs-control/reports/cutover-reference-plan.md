# Cutover Reference Plan

Generated: `2026-07-06T11:53:59.205760+00:00`
Audit run: `75`
Deferred references: `261`

## Safety Boundary

- Do not repoint these references while active Claude sessions still rely on `bc-docs-v3`.
- Do not rename `bc-docs-v4` to `bc-docs` until the user explicitly approves the cutover window.
- Treat evidence and archive references as historical provenance unless the cutover report marks them as operational links.

## Summary By Severity

| Severity | References |
|---|---|
| info | 228 |
| warning | 33 |

## Summary By Token

| Severity | Token | References |
|---|---|---|
| info | bc-docs-v3 | 228 |
| warning | C:\MyProjects\bc-docs-v3 | 1 |
| warning | bc-docs-v3 | 32 |

## Summary By Document Kind

| Severity | Document Kind | Visibility | References |
|---|---|---|---|
| info | adr | governance | 46 |
| info | evidence_audit | evidence | 5 |
| info | evidence_closeout | evidence | 35 |
| info | evidence_dbcp | evidence | 49 |
| info | evidence_ledger | evidence | 3 |
| info | evidence_work_record | evidence | 90 |
| warning | curated_reference | reference | 7 |
| warning | current_chapter | primary | 25 |
| warning | errata | governance | 1 |

## Warning References

These are current or reader-visible references to review first during cutover.

| Path | Document Kind | Visibility | Current Truth | Token |
|---|---|---|---|---|
| docs/compliance/compliance-overview.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/compliance/infosec-and-access-control.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/compliance/iso-27001-conformance.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/compliance/risk-and-vendor-management.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/compliance/soc-2-conformance.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/development/build-and-release.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/development/decision-and-change-procedure.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/development/developer-experience.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/development/development-overview.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/development/devhub.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/development/documentation-system.md | current_chapter | primary | 1 | C:\MyProjects\bc-docs-v3 |
| docs/development/documentation-system.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/development/quality-assurance.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/governance/errata/MCF-ERR-001.md | errata | governance | 1 | bc-docs-v3 |
| docs/implementation/auxiliary-services.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/implementation/backend-services.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/implementation/frontend-experience.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/onboarding/metric-workstream.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/operating-model/fiscal-time-and-temporal-gates.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/operating-model/mcf-legacy-bridge.md | current_chapter | primary | 0 | bc-docs-v3 |
| docs/operating-model/metric-management-system.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/operating-model/operating-model-overview.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/operations/deployment-topology.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/operations/security-operations.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/operations/support-and-escalation.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/overview/platform-overview.md | current_chapter | primary | 1 | bc-docs-v3 |
| docs/reference/technical-notes/implementation/bcf-mcf-evidence-boundary-operator-decisions-d1-d11.md | curated_reference | reference | 0 | bc-docs-v3 |
| docs/reference/technical-notes/implementation/bcf-mcf-panel-workbench-alignment-note.md | curated_reference | reference | 0 | bc-docs-v3 |
| docs/reference/technical-notes/implementation/business-concept-registry-vocabulary-evidence-framework.md | curated_reference | reference | 0 | bc-docs-v3 |
| docs/reference/technical-notes/implementation/business-context-framework-helper-script-trust-catalog.md | curated_reference | reference | 0 | bc-docs-v3 |
| docs/reference/technical-notes/implementation/metric-context-framework-candidate-reservoir-and-authority-classification.md | curated_reference | reference | 0 | bc-docs-v3 |
| docs/reference/technical-notes/implementation/metric-context-framework-m12-first-real-run-disposition.md | curated_reference | reference | 0 | bc-docs-v3 |
| docs/reference/technical-notes/implementation/metric-context-framework-m12-panel-framework-calibration-followup.md | curated_reference | reference | 0 | bc-docs-v3 |

## Informational References

These are evidence, archive, or hidden references. Preserve them when they are historical provenance; repoint only if they are operational links.

| Path | Document Kind | Visibility | Current Truth | Token |
|---|---|---|---|---|
| docs/evidence/audits/implementation/bcf-characteristic-scope-audit-2026-06-23.md | evidence_audit | evidence | 0 | bc-docs-v3 |
| docs/evidence/audits/implementation/devhub-decision-registration-integrity-audit-2026-06-22.md | evidence_audit | evidence | 0 | bc-docs-v3 |
| docs/evidence/audits/implementation/mcf-framework-audit-2026-06-22.md | evidence_audit | evidence | 0 | bc-docs-v3 |
| docs/evidence/audits/implementation/mcf-framework-audit-brief-2026-06-22.md | evidence_audit | evidence | 0 | bc-docs-v3 |
| docs/evidence/audits/implementation/mcf-post-bcf-metric-workflow-wiring-impact.md | evidence_audit | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/bcf-customer-invoice-id-resolution-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/bcf-enrichment-execution-closeout-for-mcf-step-4.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/bcf-evidence-schema-phase-a3-step-20-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/bcf-evidence-schema-phase-a4-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/bcf-evidence-schema-phase-a5-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/bcf-oagis-pass-1-c1-closeout-2026-06-24.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/bcf-oagis-pass-1-c1-v2-closeout-2026-06-24.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/bcf-oagis-pass-1-retrofit-batch-1-failure-closeout-2026-06-25.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/bcf-posted-amount-operator-resolution-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/bcf-step-4-publication-confirm-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/bcf-wave-a-supplier-invoice-header-parity-closeout-2026-06-23.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/bcf-wave-b-fast-track-parity-closeout-2026-06-23.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/business-concept-registry-backend-mvp-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/business-concept-registry-ui-mvp-shipped.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/devhub-decision-registration-integrity-repair-closeout-2026-06-22.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mcf-m10-apply-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mcf-m11-apply-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mcf-m12-5-implementation-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mcf-m12-implementation-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mcf-m13-implementation-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mcf-m2-ddl-apply-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mcf-m3-cert-amendment-apply-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mcf-m3-ddl-apply-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mcf-m4-ddl-apply-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mcf-m5-apply-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mcf-m7-m8-apply-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mcf-m9-apply-closeout.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/implementation/mms-recovery-closeout-2026-06-23.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/onboarding/2026-05-15-phase1-bulk-bf-semantic-remediation-closeout-TSK-9515d5.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/onboarding/2026-05-15-phase2-multi-high-bf-semantic-remediation-closeout-TSK-9515d5.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/onboarding/2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/onboarding/2026-05-16-d408-service-guard-closeout-DEC-1ce490.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/onboarding/2026-05-17-d408-correction-cleanup-closeout-DEC-1ce490.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/onboarding/2026-05-17-d409-asset-queue-closeout-DEC-b8ec00.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/closeouts/onboarding/2026-05-17-d409-pilot-1-cc-credit-closeout-DEC-b8ec00.md | evidence_closeout | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/bc-infra-r12-cognito-iam-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/bcf-authoring-test-row-cleanup-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/bcf-evidence-schema-phase-a1-apply-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/bcf-evidence-schema-phase-a1-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/bcf-evidence-schema-phase-a2-migration-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/bcf-evidence-schema-phase-a3-step-20-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/bcf-evidence-schema-phase-a3-writer-reader-cutover-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/bcf-evidence-schema-phase-a4-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/bcf-evidence-schema-phase-a5-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/d418-gate-5-physical-disposition-dbcp-design.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/d445-cas-v0-evidence-substrate-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/d461-canonical-reduction-derived-field-dbcp-2026-06-27.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/local-only-operating-model-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/mcf-role-grant-service-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/mcf-role-grant-service-implementation-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-duplicate-alias-handling-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m10-self-verification-result-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m11-reservoir-ingestion-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m12-authoring-panel-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m12-deferred-prereqs-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m12-first-real-run-authorization-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m12-first-real-run-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m12-panel-framework-calibration-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m12-trust-path-reconciliation-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m13-pe-mc-evaluator-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m14-invocation-surface-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m14-m12-governance-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m14-unblock-apply-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m3-certification-target-amendment-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m3-lifecycle-substrate-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m4-lifecycle-certification-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m5-panel-substrate-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m7-m8-formula-hash-authority-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-m9-fixture-substrate-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/metric-context-framework-service-ification-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/platform-role-catalog-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/pr-g2-first-service-surface-m12-authz.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/implementation/super-admin-bootstrap-dbcp.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/onboarding/2026-05-12-phase2-dbcp-1l-bf-semantic-family-draft-SES-594568.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/onboarding/2026-05-14-dbcp-verdict-code-extension-SES-594568.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/onboarding/2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/onboarding/2026-05-16-d408-dbcp-1q-a-verification-plan.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/onboarding/2026-05-16-d408-dbcp-1q-b-verification-plan.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/onboarding/2026-05-17-d408-dbcp-1q-c-credit-type-code-mapping-removal-verification-plan.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/onboarding/2026-05-17-d408-dbcp-1q-d-no-cc-type-incoherence-demotion-verification-plan.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/onboarding/2026-05-17-d408-dbcp-1q-e-a1-mismatch-cc-mapping-removal-verification-plan.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/dbcp/onboarding/2026-05-17-d408-dbcp-1q-g-admit-from-correction-required-action-verification-plan.md | evidence_dbcp | evidence | 0 | bc-docs-v3 |
| docs/evidence/ledgers/implementation/bcf-bc-coverage-ledger-view-2026-06-25.md | evidence_ledger | evidence | 0 | bc-docs-v3 |
| docs/evidence/ledgers/implementation/bcf-oagis-pass-1-retrofit-scoping-ledger-2026-06-25.md | evidence_ledger | evidence | 0 | bc-docs-v3 |
| docs/evidence/ledgers/implementation/bcf-oagis-retry-ledger-2026-06-24.md | evidence_ledger | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-c3-c6-projection-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-characteristic-amendment-doctrine-2026-06-23.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-coverage-compiler-validation-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-desktop-prep-handoff-contract-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-enrichment-preflight-for-mcf-seed-cases.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-grounding-recheck-2026-06-23.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-a0.5-template-catalogue-2026-06-24.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-broad-buildout-blueprint-2026-06-23.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-compile-report-2026-06-24.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-closure-checkpoint-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-operator-decision-packet-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-packet-builder-v2-design-2026-06-24.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-repair-pass-2-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-repair-pass-2-packet-prep-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-rp2-parked-row-analysis-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-rp3-packet-prep-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-1-c2-closure-checkpoint-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-1-c5-closure-checkpoint-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-1-retrofit-batch-1-v2-pilot-activation-checkpoint-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-1-retrofit-batch-1-v2-pilot-closure-checkpoint-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-1-retrofit-checker-first-preflight-v2-doctrine-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-2-e1-item-closure-checkpoint-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-2-e2-asset-maintenance-closure-checkpoint-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-2-e2-equipment-operator-decision-packet-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-2-entry-note-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-oagis-pass-3-item-shelf-life-bc-binding-closure-checkpoint-2026-06-25.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-orphan-characteristic-decision-inventory-2026-06-23.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/bcf-to-mcf-step-4-readiness-handoff.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/business-concept-registry-greenfield-enrichment-plan-sketch.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/business-context-framework-ci-harness-plan.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/business-context-framework-inventory-gap-research.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/business-context-framework-inventory.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/chain-engines-design-packet-2026-06-15.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/housekeeping-residual-pendency-2026-06-23.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mcf-final-operating-flow-pre-doctrine-decisions-2026-06-22.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-build-plan.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-inventory.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-m0-pre-m1-decision-packet.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-m10-self-verification-result-preflight.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-m11-reservoir-ingestion-preflight.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-preflight.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-m12-authoring-panel-preflight.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-m2-preflight-decisions.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-m3-lifecycle-substrate-preflight.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-m3-m4-cert-substrate-correction-preflight.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-m4-lifecycle-certification-preflight.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-m5-panel-substrate-preflight.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-m7-m8-formula-hash-authority-preflight.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/metric-context-framework-m9-fixture-substrate-preflight.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mms-layer1-cluster-g-prompt-regression-plan-2026-06-22.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mms-layer1-consolidation-checkpoint-2026-06-22.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mms-layer1-interpretation-surfaces-inventory-2026-06-22.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mms-layer1-track2-comments-tests-plan-2026-06-22.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mms-layer2-implementation-names-inventory-2026-06-22.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mms-layer2-route-alias-inventory-2026-06-23.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mms-layer3-compatibility-names-inventory-2026-06-23.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mms-publication-review-evidence-fingerprint-design-2026-06-23.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mms-r3-filter-clause-verifier-repair-design-2026-06-23.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mms-r3-filter-clause-verifier-v2-plan-2026-06-23.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mms-runtime-recovery-inventory-2026-06-23.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/implementation/mms-step2-operator-facing-docs-ui-labels-inventory-2026-06-22.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/2026-05-12-phase1-tranche1-final-execution-packet-SES-594568.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/2026-05-14-slice1-promotion-gate-plan-SES-594568.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/2026-05-15-phase1-bulk-bf-semantic-remediation-plan-TSK-9515d5.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/2026-05-15-phase2-multi-high-bf-semantic-remediation-plan-TSK-9515d5.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/2026-05-15-phase3-medium-bf-semantic-remediation-plan-TSK-9515d5.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/2026-05-15-phase3-oagis-description-root-cause-study-TSK-9515d5.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/2026-05-16-d408-service-guards-plan-DEC-1ce490.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/README.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-11-total-revenue-production-gap-SES-1c080e.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-semantic-definitions-authority-design-SES-a223ea.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-13-legacy-vs-sda-dictionary-certified-bf-classification-SES-594568.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-14-session-findings-SES-594568.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-14-slice0.5-execution-result-SES-594568.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-14-slice0.8-execution-result-SES-594568.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-14-slice1-execution-result-SES-594568.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-15-slice2-execution-result-SES-594568.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-17-d408-admit-from-correction-required-design-DEC-1ce490.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-admit-from-candidate-import-design-DEC-b8ec00.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-agent-prompt-scaffold.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-credit-facility-modeling-policy.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-intangible-asset-PARKED.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-17-d409-intangible-asset-cc-scope-decision-DEC-b8ec00.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/onboarding/metric-work-records/days-sales-outstanding/2026-05-11-grammar-design-SES-b7db1a.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/operations/mcf-panel-run-evidence/2026-05-31-pr-e2-first-service-surface-m12.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/operations/mms-terminology-transition-note-2026-06-22.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/operations/role-bootstrap-evidence/2026-05-31-super-admin-bootstrap.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/evidence/work-records/operations/role-grant-evidence/2026-05-31-pr-g1-5-first-mcf-author-grant.md | evidence_work_record | evidence | 0 | bc-docs-v3 |
| docs/governance/adrs/ADR-049cb1.md | adr | governance | 0 | bc-docs-v3 |
| docs/governance/adrs/ADR-076521.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-0cdfed.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-1db1c7.md | adr | governance | 0 | bc-docs-v3 |
| docs/governance/adrs/ADR-1fa08f.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-2411e4.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-2c2849.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-2f0967.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-327d4e.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-3395bc.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-354552.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-376587.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-3ee0f6.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-3f093f.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-54f221.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-5cb154.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-5ea578.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-61850f.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-61f7c8.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-65dc86.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-6b35e0.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-6cb4f3.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-72d723.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-739e23.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-7a1c98.md | adr | governance | 0 | bc-docs-v3 |
| docs/governance/adrs/ADR-7f9597.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-889238.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-952faa.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-9c0da7.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-a7fe72.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-af8247.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-b0839a.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-b7affa.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-b8ec00.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-b97390.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-c012c0.md | adr | governance | 0 | bc-docs-v3 |
| docs/governance/adrs/ADR-c06f41.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-ce6e2b.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-cff0cf.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-e01fcf.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-ebb3cd.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-ec341c.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-f8f925.md | adr | governance | 0 | bc-docs-v3 |
| docs/governance/adrs/ADR-f94895.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/ADR-fb0b12.md | adr | governance | 1 | bc-docs-v3 |
| docs/governance/adrs/README.md | adr | governance | 1 | bc-docs-v3 |
