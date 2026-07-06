---
title: "API Reference"
type: generated-reference
status: generated
authority: source-derived
source_repo: bc-core
source_commit: 44767f0
generated_at: 2026-07-06T09:32:32.971208+00:00
generator: generate_source_references.py
---

# API Reference

Generated from NestJS controller files in `bc-core`.

## Controllers

| Controller | Base Path | Tag | Roles | Endpoints | Source |
|---|---|---|---|---|---|
| AdminInspectionController | /admin/inspection/metrics | Admin Inspection |  | 7 | src/admin-inspection/admin-inspection.controller.ts |
| AuthController | /auth | Auth |  | 1 | src/auth/auth.controller.ts |
| UserProvisioningController | /admin/users | User Provisioning | platform_admin | 1 | src/auth/cognito-admin/user-provisioning.controller.ts |
| ActionController | /t/actions | Action — Operations | operator | 12 | src/boundary/action.controller.ts |
| AdmittedRecordController | /t/admitted-records | Admission — Admitted Records | operator | 7 | src/boundary/admission.controller.ts |
| CampaignEvaluationController | /t/metric-evaluation-campaigns |  | operator | 2 | src/boundary/campaign-evaluation.controller.ts |
| CcV2CanonicalResolverController | /t/ccv2-resolve | Canonical Evaluation |  | 1 | src/boundary/ccv2-canonical-resolver.controller.ts |
| EvaluationController | /t/evaluation | Canonical Evaluation — Operations | operator | 10 | src/boundary/evaluation.controller.ts |
| MetricEvaluationOrchestratorController | /t/metric-evaluation-governed |  |  | 1 | src/boundary/metric-evaluation-orchestrator.controller.ts |
| AuditRelationsController |  |  | platform_admin | 4 | src/boundary/metric-value-audit.controller.ts |
| MetricEvaluationController | /t/metric-evaluation | Metric Evaluation — Operations | operator | 12 | src/boundary/metric.controller.ts |
| ObservedRecordController | /t/observed-records | Observation — Observed Records | operator | 3 | src/boundary/observation.controller.ts |
| OrchestratorController | /t/admission-runs | Orchestrator — Admission Runs | operator | 6 | src/boundary/orchestrator.controller.ts |
| PeriodReadinessController | /t/period-readiness |  |  | 1 | src/boundary/period-readiness.controller.ts |
| ReaderExecutionController | /t/readers | Reader Execution | operator | 1 | src/boundary/reader-runtime/reader-execution.controller.ts |
| RuntimeConsoleController | /t/runtime-console |  |  | 5 | src/boundary/runtime-console.controller.ts |
| WebhookEndpointController | /admin/webhook-endpoints | Runtime — Webhook Registry | platform_admin | 3 | src/boundary/webhook-endpoint.controller.ts |
| DocsController | /docs | Documentation |  | 3 | src/docs/docs.controller.ts |
| EvidenceController | /t/evidence | Evidence |  | 13 | src/evidence/evidence.controller.ts |
| FunctionAdminController | /t/admin/functions |  | tenant_admin | 2 | src/function-admin/function-admin.controller.ts |
| HealthController | /health | health |  | 1 | src/health/health.controller.ts |
| MlsBackfillController | /mls |  |  | 7 | src/mls/mls-backfill.controller.ts |
| DsarController | /nullification | Nullification — DSAR |  | 2 | src/nullification/dsar.controller.ts |
| NullificationController | /nullification | Nullification |  | 7 | src/nullification/nullification.controller.ts |
| PiiRegistryController | /nullification/pii-registry | Nullification — PII Registry |  | 3 | src/nullification/pii-registry.controller.ts |
| RetentionController | /nullification/retention-policies | Nullification — Retention |  | 3 | src/nullification/retention.controller.ts |
| LibraryController | /libraries | Libraries |  | 7 | src/platform/library.controller.ts |
| MastersController | /masters | Masters |  | 16 | src/platform/masters/masters.controller.ts |
| VendorCostsController | /vendor-costs | Vendor Costs |  | 1 | src/platform/vendor-costs/vendor-costs.controller.ts |
| ReadinessController | /admin/readiness | Platform Readiness |  | 5 | src/readiness/readiness.controller.ts |
| PanelOperatorAdjudicationController | /bcf | BCF Registry Authoring | platform_admin | 1 | src/registry/bcf/adjudication/panel-operator-adjudication.controller.ts |
| RegistryAuthoringRunController | /bcf/registry-authoring-runs | BCF Registry Authoring |  | 1 | src/registry/bcf/panel/registry-authoring-run.controller.ts |
| RegistryProvenanceController | /bcf/registry/provenance | BCF Registry Provenance |  | 1 | src/registry/bcf/panel/registry-provenance.controller.ts |
| RegistryPublicationController | /bcf/registry-publications | BCF Registry Authoring |  | 2 | src/registry/bcf/panel/registry-publication.controller.ts |
| RegistryShapeCertificationConfirmController | /bcf/registry-shape-certifications | BCF Registry Authoring |  | 1 | src/registry/bcf/panel/registry-shape-certification-confirm.controller.ts |
| BcfPhase3OrphanRepairController | /bcf/registry | BCF Registry Authoring | platform_admin | 1 | src/registry/bcf/phase3-orphan-repair/bcf-phase3-orphan-repair.controller.ts |
| BcfBusinessConceptAuthoringRecommendationController | /bcf/registry | BCF Registry Authoring | platform_admin | 1 | src/registry/bcf/recommendations/business-concept-authoring/bcf-business-concept-authoring-recommendation.controller.ts |
| BcfCharacteristicAdmissionRecommendationController | /bcf/registry | BCF Registry Authoring | platform_admin | 1 | src/registry/bcf/recommendations/characteristic-admission/bcf-characteristic-admission-recommendation.controller.ts |
| BcfCharacteristicCorrectionRecommendationController | /bcf/registry | BCF Registry Authoring | platform_admin | 2 | src/registry/bcf/recommendations/characteristic-correction/bcf-characteristic-correction-recommendation.controller.ts |
| BcfCharacteristicDefinitionAmendmentRecommendationController | /bcf/registry | BCF Registry Authoring | platform_admin | 1 | src/registry/bcf/recommendations/characteristic-definition-amendment/bcf-characteristic-definition-amendment-recommendation.controller.ts |
| BcfCorrectionRecommendationController | /bcf/registry | BCF Registry Authoring | platform_admin | 3 | src/registry/bcf/recommendations/correction/bcf-correction-recommendation.controller.ts |
| BcfEntityCorrectionRecommendationController | /bcf/registry | BCF Registry Authoring | platform_admin | 1 | src/registry/bcf/recommendations/entity-correction/bcf-entity-correction-recommendation.controller.ts |
| BcfEntityVersionAmendmentRecommendationController | /bcf/registry | BCF Registry Authoring | platform_admin | 1 | src/registry/bcf/recommendations/entity-version-amendment/bcf-entity-version-amendment-recommendation.controller.ts |
| BcfTelemetryController | /ai-telemetry | BCF AI Telemetry | platform_admin | 1 | src/registry/bcf/telemetry/bcf-telemetry.controller.ts |
| BusinessCatalogController | /business-catalog | Business Catalog |  | 6 | src/registry/business-catalog.controller.ts |
| RegistryAuthoringController | /bcf/registry | BCF Registry Authoring | platform_admin | 8 | src/registry/concept-registry/registry-authoring.controller.ts |
| RegistryReadController | /bcf/registry | BCF Registry Read |  | 11 | src/registry/concept-registry/registry-read.controller.ts |
| ConnectionController | /connections | Connections |  | 9 | src/registry/connections/connection.controller.ts |
| ConnectorController | /connectors | Connectors |  | 7 | src/registry/connections/connector.controller.ts |
| ContractController | /contracts | Contracts |  | 24 | src/registry/contracts/contract.controller.ts |
| D443Phase2CertSupplyController | /bcf/registry | BCF Registry Authoring | platform_admin | 1 | src/registry/d443-phase2-cert-supply/d443-phase2-cert-supply.controller.ts |
| CoreMapController | /core-map | Core Map |  | 1 | src/registry/execution/core-map/core-map.controller.ts |
| ExecutionController | /execution |  |  | 6 | src/registry/execution/execution.controller.ts |
| PackageController | /packages | Packages |  | 6 | src/registry/execution/package.controller.ts |
| FormulaAuditController | /registry/formula-audit | Formula Audit — D315 | platform_admin | 2 | src/registry/formula-audit.controller.ts |
| RejectionLogController | /framework-approval/rejection-log | BCF — Authoring Panel Rejection Log |  | 1 | src/registry/framework-approval/rejection-log.controller.ts |
| HarnessApplyController | /harness |  | platform_admin | 1 | src/registry/harness-apply/harness-apply.controller.ts |
| IntakeQueueController | /intake-queue |  |  | 5 | src/registry/intake-queue.controller.ts |
| IntegrityController | /registry/integrity | Contract Integrity | operator | 5 | src/registry/integrity.controller.ts |
| KpiSpecController | /metric-definitions | Metric Definitions |  | 6 | src/registry/kpi-spec.controller.ts |
| McIntegrityController | /registry/mc-integrity | MC Integrity — D335 |  | 5 | src/registry/mc-integrity.controller.ts |
| BillingVolumeRetryUnlockController | /mcf/ops | MCF Ops | platform_admin | 1 | src/registry/mcf/billing-volume-retry-unlock/billing-volume-retry-unlock.controller.ts |
| ChainAuditController | /mcf/chain-audit | MCF Chain Audit | platform_admin | 2 | src/registry/mcf/chain-audit/chain-audit.controller.ts |
| ChainEnrichmentController | /mcf/chain-enrichment | MCF Chain Enrichment | platform_admin | 2 | src/registry/mcf/chain-enrichment/chain-enrichment.controller.ts |
| McfArpiMaterializationController | /mcf/arpi-materialization | MCF / D429 Step-5 ARPI Materialization | mcf_publisher | 1 | src/registry/mcf/mcf-arpi-materialization.controller.ts |
| McfIntakeController | /mcf/intakes | MCF / Metric Intake | mcf_author | 6 | src/registry/mcf/mcf-intake.controller.ts |
| McfMaterializationController | /mcf/panel-runs | MCF / Metric Drafting Materialization | mcf_publisher | 1 | src/registry/mcf/mcf-materialization.controller.ts |
| McfMcvAbandonController | /mcf/metric-contract-versions | MCF / MCV Successor Abandon | mcf_publisher | 1 | src/registry/mcf/mcf-mcv-abandon.controller.ts |
| McfMcvFixtureAppendController | /mcf/metric-contract-versions | MCF | platform_admin | 1 | src/registry/mcf/mcf-mcv-fixture-append/mcf-mcv-fixture-append.controller.ts |
| McfMcvRebindController | /mcf/metric-contract-versions |  | mcf_publisher | 1 | src/registry/mcf/mcf-mcv-rebind.controller.ts |
| McfMcvSupersedeController | /mcf/metric-contract-versions | MCF / Metric Supersession | mcf_publisher | 1 | src/registry/mcf/mcf-mcv-supersede.controller.ts |
| McfMetricRenameController | /mcf/metric-contracts | MCF / Metric Display-Name Rename | mcf_publisher | 1 | src/registry/mcf/mcf-metric-rename.controller.ts |
| McfPanelRunController | /mcf/panel-runs | MCF / Metric Draft Review Panel Run | mcf_author | 6 | src/registry/mcf/mcf-panel-run.controller.ts |
| McfPublicationActivationController | /mcf/metric-contract-versions | MCF / Metric Activation | mcf_publisher | 1 | src/registry/mcf/mcf-publication-activation.controller.ts |
| McfPublicationEligibilityController | /mcf/metric-contracts | MCF / Publication Review Eligibility | mcf_author | 5 | src/registry/mcf/mcf-publication-eligibility.controller.ts |
| McfRoleGrantController | /admin/mcf/role-grants | MCF / Role Grants |  | 1 | src/registry/mcf/mcf-role-grant.controller.ts |
| McvChainStatusController | /registry/mcf/chain-status |  | platform_admin | 3 | src/registry/mcf/mcv-chain-status.controller.ts |
| SeedMetricLedgerController | /mcf/seed-ledger | MCF / Seed Ledger | mcf_publisher | 1 | src/registry/mcf/seed-metric-ledger.controller.ts |
| MetaSchemaChangeRequestController | /admin/meta-schema | Meta-Schema Change Request | platform_admin | 8 | src/registry/meta-schemas/meta-schema-change-request.controller.ts |
| MetricBindingController | /metric-bindings | Metric Bindings |  | 4 | src/registry/metric-binding.controller.ts |
| MetricCatalogController | /metric-catalog | Metric Catalog |  | 6 | src/registry/metric-catalog.controller.ts |
| MetricDefinitionController | /metric-catalog/definitions | Metric Definitions |  | 19 | src/registry/metric-definition.controller.ts |
| MetricFunnelController | /admin/registry | Metric Lifecycle Funnel — DEC-a8b33e | platform_admin | 1 | src/registry/metric-funnel.controller.ts |
| MetricReadinessController | /registry/metric-readiness |  | platform_admin | 2 | src/registry/metric-readiness.controller.ts |
| MetricReferenceController | /metric-reference | Metric Reference |  | 7 | src/registry/metric-reference.controller.ts |
| PanelOutputRecordController | /bcf/panel-output-records | BCF Panel Output Records |  | 1 | src/registry/panel-output-record.controller.ts |
| ReaderAuthoringController | /reader-authoring | Reader Authoring |  | 6 | src/registry/readers/reader-authoring.controller.ts |
| ReaderController | /readers | Readers |  | 28 | src/registry/readers/reader.controller.ts |
| DiscoveryController | /discovery | Discovery |  | 11 | src/registry/source-catalog/discovery.controller.ts |
| OagisSeedController | /seed-catalog/oagis | OAGIS Seed Catalog |  | 4 | src/registry/source-catalog/oagis-seed.controller.ts |
| SeedCatalogController | /seed-catalog | Seed Catalog |  | 4 | src/registry/source-catalog/seed-catalog.controller.ts |
| SeedMetricsController | /seed-catalog/metrics | Seed Catalog |  | 4 | src/registry/source-catalog/seed-metrics.controller.ts |
| SourceCatalogStatsController | /source-catalog | Source Catalog |  | 34 | src/registry/source-catalog/source-catalog.controller.ts |
| OnboardingController | /onboarding |  |  | 9 | src/registry/source-catalog/source-reference.controller.ts |
| ConnectorOnboardingController | /schema-provisioner | Schema Provisioner | platform_admin | 3 | src/schema-provisioner/connector-onboarding.controller.ts |
| DriftCheckController | /platform/schema-provisioner | Schema Provisioner | platform_admin | 1 | src/schema-provisioner/drift-check.controller.ts |
| TicketController | /support/tickets | Support Tickets |  | 6 | src/support/support.controller.ts |
| TenantContextController | /t/context | Tenant Context |  | 1 | src/tenancy/tenant-context.controller.ts |
| TenantManagementController | /tenants | Tenant Management |  | 5 | src/tenant-management/tenant-management.controller.ts |
| TenantMetricsController | /admin/tenant-metrics | Tenant Metrics |  | 2 | src/tenant-metrics/tenant-metrics.controller.ts |
| BeyondMetricsController | /t/beyond |  |  | 4 | src/tenant-views/beyond-metrics.controller.ts |
| TenantDiscoveryController | /t/discovery | Tenant — Discovery |  | 30 | src/tenant-views/tenant-views.controller.ts |
| AdminTestBenchController | /admin/test-bench | Admin Test Bench |  | 2 | src/test-bench/admin-test-bench.controller.ts |
| TestBenchExecutionController | /t/test-bench | Test Bench Execution | platform_admin | 4 | src/test-bench/test-bench-execution.controller.ts |
| TestBenchController | /test-bench | Test Bench |  | 12 | src/test-bench/test-bench.controller.ts |

## Endpoints

| Method | Path | Handler | Controller | Summary |
|---|---|---|---|---|
| GET | /admin/inspection/metrics/:uid/header | getHeader | AdminInspectionController | D388 Inspector — Header (platform identity + chain verdict + attestation: proof_status, last_evaluated_at, run_id) |
| GET | /admin/inspection/metrics/:uid/chain | getChainSpine | AdminInspectionController | D388 Inspector — Chain spine (platform L1-L8 counters + attestation: snapshot/CO presence) |
| GET | /admin/inspection/metrics/:uid/monitor | getMonitorPane | AdminInspectionController | D388 Inspector — Monitor pane (platform readiness ledger + attestation: latest evaluation + counts) |
| GET | /admin/inspection/metrics/:uid/semantics | getSemanticChecks | AdminInspectionController | D388 Inspector — Semantic checks (platform-only: kind/code + reason_code) |
| GET | /admin/inspection/metrics/:uid/audit | getAuditLog | AdminInspectionController | D388 Inspector — Audit log (platform-only: contract_release_note for this metric) |
| GET | /admin/inspection/metrics/:uid/tenants | getTenantPivot | AdminInspectionController | D388 Inspector — Tenant pivot (platform-only: which tenants bind this MC + verdict) |
| GET | /admin/inspection/metrics/:uid/cross-pivots | getCrossPivots | AdminInspectionController | D388 Inspector — Cross-pivots (platform-only: other metrics sharing source fields) |
| GET | /auth/me | me | AuthController | Get current user info |
| POST | /admin/users | provision | UserProvisioningController | Provision a Cognito user (DEC-42b9c0 — no self-signup); Cognito emails the invitation |
| POST | /t/actions | createAction | ActionController | Record a declared action at the intervention boundary |
| POST | /t/actions/:actionObjectId/evaluate | evaluateAction | ActionController | Evaluate action outcome at the accountability boundary |
| POST | /t/actions/:actionObjectId/force-close | forceCloseAction | ActionController | Force-close an action without post-boundary comparison |
| POST | /t/actions/validate | dryRunActionEvaluation | ActionController | Dry-run action evaluation without persisting |
| GET | /t/actions/stats | getActionStats | ActionController | Get action statistics |
| GET | /t/actions | listActionObjects | ActionController | List action objects |
| GET | /t/actions/:actionObjectId | getActionObject | ActionController | Get action object by ID |
| GET | /t/actions/:actionObjectId/metric-snapshot | getLinkedMetricSnapshot | ActionController | Get linked metric snapshot for an action object |
| GET | /t/actions/:actionObjectId/evaluation | getLinkedEvaluation | ActionController | Get linked evaluation for an action object |
| GET | /t/actions/:actionObjectId/status | getActionStatus | ActionController | Get current status of an action object |
| GET | /t/actions | listActionEvaluations | ActionController | List action evaluation records |
| GET | /t/actions/:actionEvaluationId | getActionEvaluation | ActionController | Get action evaluation record by ID |
| POST | /t/admitted-records | admitSourceObject | AdmittedRecordController | Admit a source object at the admission boundary |
| GET | /t/admitted-records | listAdmittedRecords | AdmittedRecordController | List admitted records |
| GET | /t/admitted-records/:admittedRecordId | getAdmittedRecord | AdmittedRecordController | Get admitted record by ID |
| GET | /t/admitted-records/:admittedRecordId/source | getLinkedSourceObject | AdmittedRecordController | Get linked source object for an admitted record |
| POST | /t/admitted-records/validate | dryRunValidation | AdmittedRecordController | Dry-run admission validation without creating records |
| GET | /t/admitted-records/rejections | listRejections | AdmittedRecordController | List admission rejection evidence |
| GET | /t/admitted-records/stats | getBoundaryStats | AdmittedRecordController | Get boundary statistics |
| POST | /t/metric-evaluation-campaigns | run | CampaignEvaluationController |  |
| GET | /t/metric-evaluation-campaigns/:campaignId | get | CampaignEvaluationController | Campaign status + per-run outcomes |
| POST | /t/ccv2-resolve | run | CcV2CanonicalResolverController |  |
| POST | /t/evaluation | evaluateAdmittedRecord | EvaluationController | Evaluate an admitted record at the canonical evaluation boundary |
| POST | /t/evaluation/validate | dryRunEvaluation | EvaluationController | Dry-run canonical evaluation without creating records |
| GET | /t/evaluation/rejections | listRejections | EvaluationController | List canonical evaluation rejection evidence |
| GET | /t/evaluation/stats | getEvaluationStats | EvaluationController | Get canonical evaluation statistics |
| GET | /t/evaluation | listEvaluations | EvaluationController | List evaluation records |
| GET | /t/evaluation/:evaluationId | getEvaluation | EvaluationController | Get evaluation record by ID |
| GET | /t/evaluation | listCanonicalObjects | EvaluationController | List canonical objects |
| GET | /t/evaluation/:canonicalObjectId | getCanonicalObject | EvaluationController | Get canonical object by ID |
| GET | /t/evaluation/:canonicalObjectId/admitted | getLinkedAdmittedRecord | EvaluationController | Get linked admitted record for a canonical object |
| GET | /t/evaluation/:canonicalObjectId/evaluation | getLinkedEvaluation | EvaluationController | Get linked evaluation record for a canonical object |
| POST | /t/metric-evaluation-governed | run | MetricEvaluationOrchestratorController |  |
| POST | /registry/mcf/audit-relations | declare | AuditRelationsController | Declare a cross-metric audit relation (D481 §7) |
| GET | /registry/mcf/audit-relations | list | AuditRelationsController | List declared audit relations |
| DELETE | /registry/mcf/audit-relations/:relationUid | archive | AuditRelationsController | Archive an audit relation (soft) |
| POST | /run | run | AuditRelationsController | Run the value audit for one fiscal period (explicit act; reads never trigger this) |
| POST | /t/metric-evaluation | evaluateMetric | MetricEvaluationController | Evaluate canonical objects at the metric evaluation boundary |
| POST | /t/metric-evaluation/validate | dryRunMetricEvaluation | MetricEvaluationController | Dry-run metric evaluation without creating records |
| GET | /t/metric-evaluation/rejections | listRejections | MetricEvaluationController | List metric evaluation rejection evidence |
| GET | /t/metric-evaluation/stats | getMetricStats | MetricEvaluationController | Get metric evaluation statistics |
| GET | /t/metric-evaluation | listMetricEvaluations | MetricEvaluationController | List metric evaluation records |
| GET | /t/metric-evaluation/:metricEvaluationId | getMetricEvaluation | MetricEvaluationController | Get metric evaluation record by ID |
| GET | /t/metric-evaluation | listMetricSnapshots | MetricEvaluationController | List metric snapshots |
| GET | /t/metric-evaluation/latest-per-contract | getLatestPerContract | MetricEvaluationController | Get latest snapshot per metric contract with delta |
| GET | /t/metric-evaluation/timeline | getSnapshotTimeline | MetricEvaluationController | Get chronological snapshot timeline for a metric contract |
| GET | /t/metric-evaluation/:metricSnapshotId | getMetricSnapshot | MetricEvaluationController | Get metric snapshot by ID |
| GET | /t/metric-evaluation/:metricSnapshotId/canonical-objects | getLinkedCanonicalObjects | MetricEvaluationController | Get linked canonical objects for a metric snapshot |
| GET | /t/metric-evaluation/:metricSnapshotId/evaluation | getLinkedEvaluation | MetricEvaluationController | Get linked metric evaluation for a snapshot |
| POST | /t/observed-records | recordObservation | ObservedRecordController | Record a single observation |
| POST | /t/observed-records/batch | recordObservationBatch | ObservedRecordController | Record a batch of observations (max 100) |
| GET | /t/observed-records/:sourceObjectId/admitted | getLinkedAdmittedRecord | ObservedRecordController | Get linked admitted record for a source object |
| POST | /t/admission-runs/:runId/execute | executeFullCycle | OrchestratorController | Execute full observation-to-admission cycle for a run |
| POST | /t/admission-runs/:runId/observe | submitObservations | OrchestratorController | Submit observations for an admission run |
| POST | /t/admission-runs/:runId/admit | admitSourceObjects | OrchestratorController | Admit pending source objects for an admission run |
| POST | /t/admission-runs/:runId/resolve | resolveRun | OrchestratorController | Resolve admitted records into canonical objects via mapping binding |
| GET | /t/admission-runs/:runId/admissions | listRunAdmissions | OrchestratorController | List admissions for an admission run |
| GET | /t/admission-runs/:runId/rejections | listRunRejections | OrchestratorController | List rejections for an admission run |
| GET | /t/period-readiness | list | PeriodReadinessController | Per-period read-readiness (derived on read; never triggers evaluation) |
| POST | /t/readers/:readerId/execute | executeReader | ReaderExecutionController |  |
| GET | /t/runtime-console/campaigns | campaigns | RuntimeConsoleController | Latest evaluation campaigns with run rollups |
| GET | /t/runtime-console/events | events | RuntimeConsoleController | Runtime event outbox (completion-event stream) |
| GET | /t/runtime-console/watermarks | watermarks | RuntimeConsoleController | Reader fetch watermarks (delta discipline state) |
| GET | /t/runtime-console/webhook-deliveries | webhookDeliveries | RuntimeConsoleController | Webhook delivery attempts incl. dead letters |
| GET | /t/runtime-console/audit-verdicts | auditVerdicts | RuntimeConsoleController | Persisted value-audit verdicts (latest per relation/period) |
| POST | /admin/webhook-endpoints | register | WebhookEndpointController | Register an outbound webhook endpoint (D481 §9) |
| GET | /admin/webhook-endpoints | list | WebhookEndpointController | List registered webhook endpoints |
| DELETE | /admin/webhook-endpoints/:endpointId | archive | WebhookEndpointController | Archive a webhook endpoint (soft — archived_at) |
| GET | /docs/manifest | getManifest | DocsController | Get docs manifest (sections + collections) |
| GET | /docs/file/*splat | getFile | DocsController | Get markdown content (watermarked) |
| GET | /docs/asset/*splat | getAsset | DocsController | Get binary asset (diagrams, images) |
| POST | /t/evidence | createEvidence | EvidenceController | Create an evidence record |
| GET | /t/evidence/verify | bulkVerify | EvidenceController | Bulk-verify evidence integrity |
| GET | /t/evidence/export | exportEvidence | EvidenceController | Export evidence records as JSON or CSV |
| GET | /t/evidence | listEvidence | EvidenceController | List evidence records |
| GET | /t/evidence/:evidenceId | getEvidence | EvidenceController | Get evidence by ID |
| GET | /t/evidence/:evidenceId/verify | verifyEvidence | EvidenceController | Verify evidence chain integrity |
| POST | /t/evidence | createEvidenceRecord | EvidenceController | Create an evidence context record |
| GET | /t/evidence | listEvidenceRecords | EvidenceController | List evidence context records |
| GET | /t/evidence/:recordId | getEvidenceRecord | EvidenceController | Get evidence context record by ID |
| POST | /t/evidence | createLineage | EvidenceController | Create a lineage relationship |
| GET | /t/evidence | listLineage | EvidenceController | List lineage relationships |
| GET | /t/evidence/trace/:objectId | traceLineage | EvidenceController | Trace full lineage graph for an object |
| GET | /t/evidence/:lineageId | getLineage | EvidenceController | Get lineage relationship by ID |
| GET | /t/admin/functions/:functionCode/metrics | listMetrics | FunctionAdminController |  |
| PATCH | /t/admin/functions/:functionCode/metrics/:mcUid/binding | setBinding | FunctionAdminController |  |
| GET | /health | check | HealthController | Health check |
| POST | /mls/backfill | runBackfill | MlsBackfillController |  |
| POST | /mls/signature-hash-backfill | runSignatureHashBackfill | MlsBackfillController |  |
| POST | /mls/gate/evaluate | gateEvaluate | MlsBackfillController |  |
| POST | /mls/gate/reevaluate | gateReevaluate | MlsBackfillController |  |
| GET | /mls/activation-violations | listActivationViolations | MlsBackfillController |  |
| GET | /mls/recent-transitions | getRecentTransitions | MlsBackfillController |  |
| GET | /mls/state-buckets | getStateBuckets | MlsBackfillController |  |
| POST | /nullification/requests/:id/dsar | generateDsar | DsarController | Generate DSAR data package for a request |
| GET | /nullification/dsar/:token | downloadDsar | DsarController | Download DSAR data package by token |
| POST | /nullification/requests | create | NullificationController | Submit a nullification/DSAR request |
| GET | /nullification/requests | list | NullificationController | List nullification requests |
| GET | /nullification/requests/:id | get | NullificationController | Get nullification request detail |
| PATCH | /nullification/requests/:id/approve | approve | NullificationController | Approve a pending request |
| PATCH | /nullification/requests/:id/reject | reject | NullificationController | Reject a pending request |
| POST | /nullification/requests/:id/execute | execute | NullificationController | Execute an approved nullification request |
| GET | /nullification/requests/:id/actions | actions | NullificationController | List nullification actions for a request |
| GET | /nullification/pii-registry | list | PiiRegistryController | List PII field registry entries |
| POST | /nullification/pii-registry | create | PiiRegistryController | Register a PII field |
| DELETE | /nullification/pii-registry/:id | remove | PiiRegistryController | Remove a PII field from registry |
| GET | /nullification/retention-policies | list | RetentionController | List retention policies |
| POST | /nullification/retention-policies | create | RetentionController | Create a retention policy |
| POST | /nullification/retention-policies/evaluate | evaluate | RetentionController | Manually trigger retention policy evaluation |
| POST | /libraries | createLibrary | LibraryController | Register a new library (or use POST /libraries/upsert for idempotent create) |
| POST | /libraries/upsert | upsertLibrary | LibraryController | Create or update a library by name+source (idempotent — used by scanner) |
| GET | /libraries/stats | getStats | LibraryController | Library registry summary stats (totals, by status/category/risk, CVE counts) |
| GET | /libraries | listLibraries | LibraryController | List libraries |
| GET | /libraries/:libraryId | getLibrary | LibraryController | Get library by ID |
| PATCH | /libraries/:libraryId | updateLibrary | LibraryController | Update a library |
| DELETE | /libraries/:libraryId | deleteLibrary | LibraryController | Delete a library |
| GET | /masters/industry-categories | listIndustryCategories | MastersController | List all industry categories |
| GET | /masters/industry-categories/:code | getIndustryCategory | MastersController | Get an industry category by code |
| GET | /masters/industries | listIndustries | MastersController | List all industries (optionally filter by category) |
| GET | /masters/industries/:slug | getIndustry | MastersController | Get an industry by slug |
| GET | /masters/functions | listFunctions | MastersController | List all business functions |
| GET | /masters/functions/:slug | getFunction | MastersController | Get a function by slug |
| GET | /masters/currencies | listCurrencies | MastersController | List all currencies (ISO 4217) |
| GET | /masters/currencies/:code | getCurrency | MastersController | Get a currency by ISO 4217 code |
| GET | /masters/countries | listCountries | MastersController | List all countries (ISO 3166-1) |
| GET | /masters/countries/region/:region | listCountriesByRegion | MastersController | List countries by region |
| GET | /masters/countries/:alpha2 | getCountry | MastersController | Get a country by ISO 3166-1 alpha-2 code |
| GET | /masters/statuses | listStatuses | MastersController | List all status definitions |
| GET | /masters/statuses/:context | listStatusesByContext | MastersController | List statuses for a specific context |
| GET | /masters/statuses/:context/:code | getStatus | MastersController | Get a specific status by context and code |
| GET | /masters/subfunctions | listSubfunctions | MastersController | List all business subfunctions |
| GET | /masters/subfunctions/:function/:slug | getSubfunction | MastersController | Get a subfunction by function and slug |
| GET | /vendor-costs | report | VendorCostsController |  |
| GET | /admin/readiness/catalog | getCatalog | ReadinessController |  |
| GET | /admin/readiness/tenant | getTenant | ReadinessController |  |
| GET | /admin/readiness/tenant/:slug/binding-candidates | getBindingCandidates | ReadinessController |  |
| POST | /admin/readiness/tenant/:slug/bind | bind | ReadinessController |  |
| GET | /admin/readiness/tenant/:slug/formula-token-audit | getFormulaTokenAudit | ReadinessController |  |
| POST | /bcf/registry-panel-operator-adjudications | adjudicate | PanelOperatorAdjudicationController |  |
| POST | /bcf/registry-authoring-runs | run | RegistryAuthoringRunController |  |
| GET | /bcf/registry/provenance/publication/:subjectKind/:registryId | inspectPublication | RegistryProvenanceController |  |
| POST | /bcf/registry-publications | request | RegistryPublicationController |  |
| POST | /bcf/registry-publications/confirm | confirm | RegistryPublicationController |  |
| POST | /bcf/registry-shape-certifications/confirm | confirm | RegistryShapeCertificationConfirmController |  |
| POST | /bcf/registry/phase3-orphan-repair | repair | BcfPhase3OrphanRepairController |  |
| POST | /bcf/registry/concepts/authoring-recommendations | submit | BcfBusinessConceptAuthoringRecommendationController |  |
| POST | /bcf/registry/characteristics/admission-recommendations | submit | BcfCharacteristicAdmissionRecommendationController |  |
| POST | /bcf/registry/characteristics/:characteristicId/supersession-recommendations | submitSupersession | BcfCharacteristicCorrectionRecommendationController |  |
| POST | /bcf/registry/characteristics/:characteristicId/withdrawal-recommendations | submitWithdrawal | BcfCharacteristicCorrectionRecommendationController |  |
| POST | /bcf/registry/characteristics/:characteristicId/definition-amendment-recommendations | submit | BcfCharacteristicDefinitionAmendmentRecommendationController |  |
| POST | /bcf/registry/concepts/:conceptId/correction-recommendations | submit | BcfCorrectionRecommendationController |  |
| POST | /bcf/registry/concepts/:conceptId/shape-correction-recommendations | submitShapeCorrection | BcfCorrectionRecommendationController |  |
| POST | /bcf/registry/concepts/:conceptId/reference-correction-recommendations | submitReferenceCorrection | BcfCorrectionRecommendationController |  |
| POST | /bcf/registry/entities/:entityId/correction-recommendations | submit | BcfEntityCorrectionRecommendationController |  |
| POST | /bcf/registry/entities/:entityId/version-amendment-recommendations | submit | BcfEntityVersionAmendmentRecommendationController |  |
| POST | /ai-telemetry/bcf-panel-run/from-summary | ingestBcfPanelRunSummary | BcfTelemetryController | Ingest BCF panel-run telemetry summary |
| GET | /business-catalog/taxonomy | getTaxonomy | BusinessCatalogController | Full domain taxonomy (29 domains, 200+ entities) |
| GET | /business-catalog/objects | getObjectsFlat | BusinessCatalogController | Flat, paginated list of canonical objects with search/filter/sort |
| GET | /business-catalog/domains | getFunctions | BusinessCatalogController | Canonical contracts grouped by function with counts |
| GET | /business-catalog/domains/:function | getFunctionDetail | BusinessCatalogController | Business objects within a function with CO instance counts |
| GET | /business-catalog/mappings | getMappings | BusinessCatalogController | Flat, paginated list of CO↔Metric bindings |
| GET | /business-catalog/stats | getStats | BusinessCatalogController | Dashboard aggregation: domain/object/instance counts |
| POST | /bcf/registry/concepts/:conceptId/supersede | supersedeBusinessConcept | RegistryAuthoringController |  |
| POST | /bcf/registry/entities/:entityId/supersede | supersedeEntity | RegistryAuthoringController |  |
| POST | /bcf/registry/entities/:entityId/versions | addEntityVersion | RegistryAuthoringController |  |
| POST | /bcf/registry/concepts/:conceptId/versions | addBusinessConceptVersion | RegistryAuthoringController |  |
| POST | /bcf/registry/characteristics/:characteristicId/supersede | supersedeCharacteristic | RegistryAuthoringController |  |
| POST | /bcf/registry/characteristics/:characteristicId/amend-definition | amendCharacteristicDefinition | RegistryAuthoringController |  |
| POST | /bcf/registry/characteristics/:characteristicId/withdraw | withdrawCharacteristic | RegistryAuthoringController |  |
| POST | /bcf/registry/concepts/:conceptId/withdraw-draft | withdrawDraftBusinessConcept | RegistryAuthoringController |  |
| GET | /bcf/registry/entities | listEntities | RegistryReadController | List Registry Entities — active-only unless filtered (F5-S2). |
| GET | /bcf/registry/entities/:entityId | resolveEntity | RegistryReadController | Resolve one Registry Entity to its active version (F5-S2). |
| GET | /bcf/registry/entities/:entityId/concepts | listConceptsForEntity | RegistryReadController | List BusinessConcepts owned by one Entity (F5-S2). |
| GET | /bcf/registry/entities/:entityId/supersession | getEntitySupersession | RegistryReadController | Supersession lineage for one Entity — predecessors + successors (F5). |
| GET | /bcf/registry/concepts | listConcepts | RegistryReadController | List BusinessConcepts registry-wide — active-only unless filtered (F5-S2). |
| GET | /bcf/registry/concepts/:conceptId | resolveConcept | RegistryReadController | Resolve one active BusinessConcept by concept id (F5-S2). |
| GET | /bcf/registry/concept-versions/:conceptVersionId | resolveConceptVersion | RegistryReadController |  |
| GET | /bcf/registry/concepts/:conceptId/supersession | getConceptSupersession | RegistryReadController |  |
| GET | /bcf/registry/characteristics | listCharacteristics | RegistryReadController | List governed Characteristics — active-only unless filtered (F5-S2). |
| GET | /bcf/registry/characteristics/:characteristicId | getCharacteristic | RegistryReadController | Resolve one governed Characteristic by id (F5-S2). |
| GET | /bcf/registry/characteristics/:characteristicId/supersession | getCharacteristicSupersession | RegistryReadController |  |
| POST | /connections | createConnection | ConnectionController | Create a new connection |
| GET | /connections | listConnections | ConnectionController | List connections |
| GET | /connections/:connectionId | getConnection | ConnectionController | Get connection by ID |
| PATCH | /connections/:connectionId | updateConnection | ConnectionController | Update a connection |
| DELETE | /connections/:connectionId | deleteConnection | ConnectionController | Delete a connection |
| GET | /connections/:connectionId/flavors | listFlavors | ConnectionController | List reader flavors using this connection |
| POST | /connections/:connectionId/checks | recordCheck | ConnectionController | Record a connection health check |
| GET | /connections/:connectionId/checks | listChecks | ConnectionController | List connection health checks |
| GET | /connections/:connectionId/health | getHealth | ConnectionController | Get connection health summary |
| POST | /connectors | createConnector | ConnectorController | Register a new connector |
| GET | /connectors | listConnectors | ConnectorController | List connectors |
| GET | /connectors/governance | getGovernanceStats | ConnectorController | Connector governance summary (generation method, license, manifest source) |
| GET | /connectors/:connectorId/usage | getConnectorUsage | ConnectorController | D064: Connector usage — connection and flavor counts |
| GET | /connectors/:connectorId | getConnector | ConnectorController | Get connector by ID |
| PATCH | /connectors/:connectorId | updateConnector | ConnectorController | Update a connector |
| DELETE | /connectors/:connectorId | deleteConnector | ConnectorController | Delete a connector |
| POST | /contracts | createContract | ContractController | Create a new contract |
| GET | /contracts | listContracts | ContractController | List contracts |
| GET | /contracts/stats | getContractStats | ContractController | Get contract statistics by category |
| GET | /contracts/drift-summary | getDriftSummary | ContractController | Get drift summary — how many contracts are current/stale/broken |
| GET | /contracts/masters/dqc-rules | getDqcRules | ContractController | DQC rule library — global, platform, tenant rules for admission contracts (D288) |
| POST | /contracts/bulk-transition | bulkTransition | ContractController | Bulk governance state transition for contracts by category |
| POST | /contracts/generate-source-chain | generateSourceChain | ContractController | D289: Bulk-generate SC + AC pairs from eligible source catalog objects (all quality gates) |
| GET | /contracts/:contractId | getContract | ContractController | Get contract by ID |
| GET | /contracts/:contractId/drift | getContractDrift | ContractController | Get drift status — compare contract envelope fields vs current catalog fields |
| PATCH | /contracts/:contractId | updateContract | ContractController | Update a contract |
| DELETE | /contracts/:contractId | deleteContract | ContractController | Delete a contract |
| POST | /contracts/:contractId/archive | archiveContract | ContractController | Archive a contract (soft delete) |
| POST | /contracts/:contractId/unarchive | unarchiveContract | ContractController | Unarchive a contract |
| POST | /contracts/:contractId/versions | createVersion | ContractController | Create a new contract version |
| GET | /contracts/:contractId/versions | listVersions | ContractController | List contract versions |
| GET | /contracts/:contractId/versions/:version | getVersion | ContractController | Get a specific contract version |
| GET | /contracts/:contractId/versions/:version/compatibility | compareVersions | ContractController | Compare contract version compatibility |
| POST | /contracts/:contractId/versions/:version/submit | submitForReview | ContractController | Submit contract version for review |
| POST | /contracts/:contractId/versions/:version/approve | approveVersion | ContractController | Approve a contract version |
| POST | /contracts/:contractId/versions/:version/activate | activateVersion | ContractController | Activate a contract version (make it live) |
| POST | /contracts/:contractId/versions/:version/supersede | supersedeVersion | ContractController | Supersede a contract version (replaced by newer version) |
| POST | /contracts/:contractId/versions/:version/revert | revertToDraft | ContractController | Revert a contract version to draft |
| GET | /contracts/:contractId/versions/:version/approvals | listApprovals | ContractController | List approvals for a contract version |
| POST | /contracts/:contractId/versions/:version/approvals | addApproval | ContractController | Add an approval to a contract version |
| POST | /bcf/registry/d443-phase2-cert-mint | mint | D443Phase2CertSupplyController |  |
| GET | /core-map | getCoreMap | CoreMapController | Get integration readiness map — all resources with status and relationships |
| GET | /execution/overview | getOverview | ExecutionController |  |
| GET | /execution/rollups | listRollups | ExecutionController |  |
| GET | /execution/runs | listRuns | ExecutionController |  |
| GET | /execution/health | listHealth | ExecutionController |  |
| GET | /execution/boundary-progression | listBoundaryProgression | ExecutionController |  |
| GET | /execution/rejections | listRejections | ExecutionController |  |
| POST | /packages | createPackage | PackageController | D086: Create a subscription package |
| GET | /packages | listPackages | PackageController | D086: List subscription packages |
| GET | /packages/:packageId | getPackage | PackageController | D086: Get package by ID |
| PATCH | /packages/:packageId | updatePackage | PackageController | D086: Update a package |
| GET | /packages/:packageId/provision-preview | getProvisioningPreview | PackageController | D086: Preview what readers would be provisioned for this package |
| DELETE | /packages/:packageId | deletePackage | PackageController | D086: Delete a package |
| GET | /registry/formula-audit | runAudit | FormulaAuditController | Run formula audit across all metric contracts (D315 Layer 1) |
| GET | /registry/formula-audit/summary | getSummary | FormulaAuditController | Formula audit summary — reads persisted status from catalog (cheap) |
| POST | /framework-approval/rejection-log/:rejectionLogId/override | overrideRejection | RejectionLogController |  |
| POST | /harness/apply | run | HarnessApplyController |  |
| POST | /intake-queue | enqueue | IntakeQueueController | Enqueue a proposed member into the pre-catalog intake queue |
| GET | /intake-queue | list | IntakeQueueController | List intake-queue entries (cursor-paginated) |
| POST | /intake-queue/age-out | ageOut | IntakeQueueController |  |
| GET | /intake-queue/:id | getById | IntakeQueueController | Get a single intake-queue entry by id |
| POST | /intake-queue/:id/apply-panel-result | applyPanelResult | IntakeQueueController |  |
| GET | /registry/integrity/canonical/:slug/fields | getCanonicalFields | IntegrityController |  |
| GET | /registry/integrity/kpi/:contractId | getKpiIntegrity | IntegrityController |  |
| GET | /registry/integrity/kpi/:contractId/coverage | getKpiCoverage | IntegrityController |  |
| GET | /registry/integrity/report | getIntegrityReport | IntegrityController |  |
| GET | /registry/integrity/canonical/:slug | getCanonicalIntegrity | IntegrityController |  |
| POST | /metric-definitions | create | KpiSpecController | Create a KPI spec for a metric contract |
| GET | /metric-definitions | list | KpiSpecController | List KPI specs with optional filters |
| GET | /metric-definitions/stats | getStats | KpiSpecController | KPI spec statistics |
| GET | /metric-definitions/:contractId | getByContractId | KpiSpecController | Get full KPI spec by contract ID |
| PATCH | /metric-definitions/:contractId | update | KpiSpecController | Update KPI spec fields |
| DELETE | /metric-definitions/:contractId | delete | KpiSpecController | Delete a KPI spec |
| GET | /registry/mc-integrity | list | McIntegrityController | List MC integrity rows with optional filters (findings projected out) |
| GET | /registry/mc-integrity/distribution | distribution | McIntegrityController | Bucket + verdict + subfunction distribution (for dashboard) |
| GET | /registry/mc-integrity/:mcId | getOne | McIntegrityController | Single MC integrity detail (includes findings_json) |
| POST | /registry/mc-integrity/refresh | refreshAll | McIntegrityController | Kick off full-runway re-diagnose (async). Returns 202 + startedAt. |
| POST | /registry/mc-integrity/refresh/:mcId | refreshOne | McIntegrityController | Re-diagnose a single MC synchronously (~3-5s). |
| POST | /mcf/ops/billing-volume-retry-unlock | unlock | BillingVolumeRetryUnlockController |  |
| POST | /mcf/chain-audit/runs | runAudit | ChainAuditController |  |
| GET | /mcf/chain-audit/evidence/:auditEvidenceUid | readEvidence | ChainAuditController |  |
| POST | /mcf/chain-enrichment/plans | createPlan | ChainEnrichmentController |  |
| GET | /mcf/chain-enrichment/plans/:planUid | readPlan | ChainEnrichmentController |  |
| POST | /mcf/arpi-materialization | materialize | McfArpiMaterializationController |  |
| POST | /mcf/intakes | create | McfIntakeController | Create operator-direct Metric Intake entry |
| POST | /mcf/intakes/from-metric-definition | createFromMetricDefinition | McfIntakeController |  |
| POST | /mcf/intakes/from-seed | createFromSeed | McfIntakeController |  |
| GET | /mcf/intakes | list | McfIntakeController | List Metric Intake entries with optional filters |
| GET | /mcf/intakes/:intakeQueueUid | readOne | McfIntakeController | Read one Metric Intake entry by uid |
| PATCH | /mcf/intakes/:intakeQueueUid/reject | reject | McfIntakeController | Operator-driven rejection of a Metric Intake entry (reason ≥20 chars) |
| POST | /mcf/panel-runs/:panelRunUid/materialize | materialize | McfMaterializationController |  |
| POST | /mcf/metric-contract-versions/:metricContractVersionUid/abandon | abandon | McfMcvAbandonController |  |
| POST | /mcf/metric-contract-versions/:mcvUid/append-fixture | appendFixture | McfMcvFixtureAppendController |  |
| POST | /mcf/metric-contract-versions/rebind | rebind | McfMcvRebindController |  |
| POST | /mcf/metric-contract-versions/:metricContractVersionUid/supersede | supersede | McfMcvSupersedeController |  |
| PATCH | /mcf/metric-contracts/:metricContractUid/display-name | renameDisplayName | McfMetricRenameController |  |
| POST | /mcf/panel-runs | runPanel | McfPanelRunController |  |
| POST | /mcf/panel-runs/with-maker | runPanelWithMaker | McfPanelRunController |  |
| GET | /mcf/panel-runs | list | McfPanelRunController | List panel runs with optional filters |
| GET | /mcf/panel-runs/:panelRunUid | readOne | McfPanelRunController | Read one panel run by uid |
| GET | /mcf/panel-runs/:panelRunUid/transcripts | listTranscripts | McfPanelRunController | Read the 3 per-role transcripts for a panel run |
| POST | /mcf/panel-runs/:panelRunUid/materialization-preflight | materializationPreflight | McfPanelRunController | Read-only preflight: is this panel run eligible for Metric Drafting materialization? |
| POST | /mcf/metric-contract-versions/:mcvUid/activate | activate | McfPublicationActivationController |  |
| POST | /mcf/metric-contracts/:metricContractUid/knowledge-from-panel-run/:panelRunUid | persistKnowledge | McfPublicationEligibilityController |  |
| GET | /mcf/metric-contracts | list | McfPublicationEligibilityController |  |
| GET | /mcf/metric-contracts/:metricContractUid | detail | McfPublicationEligibilityController |  |
| GET | /mcf/metric-contracts/:metricContractUid/pe-mc-status | readStatus | McfPublicationEligibilityController | Read Publication Eligibility check results for an MC (persisted pe_check_code values PE-MC-1..12) |
| POST | /mcf/metric-contracts/:metricContractUid/evaluate-pe-mc | evaluate | McfPublicationEligibilityController |  |
| POST | /admin/mcf/role-grants | grantMcfRoles | McfRoleGrantController |  |
| POST | /registry/mcf/chain-status/refresh | refresh | McvChainStatusController | Recompute live chain verdicts for all active MCVs (explicit act — reads never trigger this) |
| GET | /registry/mcf/chain-status/summary | summary | McvChainStatusController | Verdict counts (green/amber/red) |
| GET | /registry/mcf/chain-status | list | McvChainStatusController | Per-MCV verdicts with check details |
| POST | /mcf/seed-ledger/reconcile | reconcile | SeedMetricLedgerController |  |
| POST | /admin/meta-schema/change-request | create | MetaSchemaChangeRequestController |  |
| GET | /admin/meta-schema/change-request | list | MetaSchemaChangeRequestController |  |
| GET | /admin/meta-schema/change-request/:id | getOne | MetaSchemaChangeRequestController | Read one change request including the proposed schema body |
| POST | /admin/meta-schema/change-request/:id/approve | approve | MetaSchemaChangeRequestController |  |
| POST | /admin/meta-schema/change-request/:id/reject | reject | MetaSchemaChangeRequestController |  |
| GET | /admin/meta-schema/drift-report | driftReport | MetaSchemaChangeRequestController |  |
| POST | /admin/meta-schema/drift-report/refresh | driftReportRefresh | MetaSchemaChangeRequestController |  |
| GET | /admin/meta-schema/:category/:version | getActive | MetaSchemaChangeRequestController |  |
| GET | /metric-bindings | list | MetricBindingController | List metric bindings with filters and pagination |
| GET | /metric-bindings/:id | getById | MetricBindingController | Get a single metric binding by ID |
| POST | /metric-bindings | create | MetricBindingController | Create a metric binding (MO → CO) |
| DELETE | /metric-bindings/:id | deleteById | MetricBindingController | Delete a metric binding |
| GET | /metric-catalog/kpis | getKpisFlat | MetricCatalogController | Flat, paginated list of all metric KPIs with search/filter/sort |
| GET | /metric-catalog/taxonomy | getTaxonomy | MetricCatalogController | Full metric module taxonomy (84 modules, 13 CXO packs) |
| GET | /metric-catalog/domains | getFunctions | MetricCatalogController | Metric KPIs grouped by function with counts |
| GET | /metric-catalog/domains/:function | getFunctionDetail | MetricCatalogController | Modules within a function with KPI/snapshot counts |
| GET | /metric-catalog/domains/:function/modules/:subfunction | getModuleDetail | MetricCatalogController | Individual KPI contracts within a module |
| GET | /metric-catalog/stats | getStats | MetricCatalogController | Dashboard aggregation: domain/module/KPI/snapshot counts |
| POST | /metric-catalog/definitions | create | MetricDefinitionController | RETIRED (410 Gone) — legacy single-create write path removed per D481 register item 5; use MCF intake + panel + materialization |
| POST | /metric-catalog/definitions/upload | bulkCreate | MetricDefinitionController | RETIRED (410 Gone) — legacy CSV bulk-create write path removed per D481 register item 5; use MCF intake + panel + materialization |
| GET | /metric-catalog/definitions/check-unique | checkUnique | MetricDefinitionController | Check if a metric definition with this name+function+subfunction already exists |
| POST | /metric-catalog/definitions/suggest | suggest | MetricDefinitionController | AI-suggest characteristics from metric identity + classification (heuristic v1) |
| GET | /metric-catalog/definitions/stats | getStats | MetricDefinitionController | Lifecycle funnel stats — maturity distribution, gate history, 5D breakdowns (D283) |
| GET | /metric-catalog/definitions/masters | getMasters | MetricDefinitionController | All classification master data for form dropdowns |
| GET | /metric-catalog/definitions/batches/:batchId/status | getBatchStatus | MetricDefinitionController | Batch enrichment progress with per-row items |
| POST | /metric-catalog/definitions/batches/:batchId/retry | retryBatch | MetricDefinitionController | Re-queue all failed jobs in a batch |
| GET | /metric-catalog/definitions/batches/:batchId/report | getBatchReport | MetricDefinitionController | Download CSV report for a batch |
| GET | /metric-catalog/definitions/:id | getById | MetricDefinitionController | Get full detail (definition + formula + knowledge + verification + enrichment) |
| PATCH | /metric-catalog/definitions/:id | update | MetricDefinitionController | Update metric definition fields |
| POST | /metric-catalog/definitions/:id/enrich | retriggerEnrichment | MetricDefinitionController | Re-trigger AI enrichment for one definition |
| POST | /metric-catalog/definitions/:id/gate/enrichment | runEnrichmentGate | MetricDefinitionController | Run enrichment gate — checks formula + variables exist (D283) |
| POST | /metric-catalog/definitions/:id/gate/verification | runVerificationGate | MetricDefinitionController | Run verification gate — checks bindings + active mappings for primary metrics (D283) |
| POST | /metric-catalog/definitions/:id/gate/classification | runClassificationGate | MetricDefinitionController | Run classification gate — checks 5D completeness + collision rules (D283) |
| POST | /metric-catalog/definitions/gates/enrichment/bulk | runEnrichmentGateBulk | MetricDefinitionController | Bulk run enrichment gate on all classified metrics (D283) |
| POST | /metric-catalog/definitions/gates/classification/bulk | runClassificationGateBulk | MetricDefinitionController | Bulk run classification gate on all registered metrics (D283) |
| GET | /metric-catalog/definitions/:id/lifecycle | getLifecycleEvents | MetricDefinitionController | Get lifecycle event history for a metric (D283) |
| GET | /metric-catalog/definitions | list | MetricDefinitionController | List metric definitions with filters (offset pagination) |
| GET | /admin/registry/funnel-ladder | getLadder | MetricFunnelController |  |
| GET | /registry/metric-readiness/resolve-definition/:mcId | resolveDefinition | MetricReadinessController | Resolve metric_contract → metric_definition_id via forward FK (used by contract-page redirect) |
| GET | /registry/metric-readiness/chain-detail/:mcId | getChainDetail | MetricReadinessController | Single-MC chain readiness detail — 3-step trace (formula + chain + reader) |
| GET | /metric-reference | list | MetricReferenceController | Paginated list of reference KPIs with search/filter |
| GET | /metric-reference/stats | getStats | MetricReferenceController | Total count + function breakdown for filter pills |
| GET | /metric-reference/filters | getFilters | MetricReferenceController | Filter dropdown options (domains, industries) |
| GET | /metric-reference/:id | getById | MetricReferenceController | Get a single metric reference entry |
| POST | /metric-reference | create | MetricReferenceController | Create a new metric reference entry |
| POST | /metric-reference/bulk | bulkCreate | MetricReferenceController | Bulk create metric reference entries |
| POST | /metric-reference/:id/promote | promote | MetricReferenceController | Promote a reference KPI to the Metric Catalog |
| POST | /bcf/panel-output-records | create | PanelOutputRecordController |  |
| POST | /reader-authoring/flavors | createFlavor | ReaderAuthoringController | Create a draft reader flavor (name derived from source_system/scenario, P-F7) |
| POST | /reader-authoring/flavors/:flavorId/activate | activateFlavor | ReaderAuthoringController | Activate a flavor — fail-closed behind chain-resolvability + determinism gates |
| POST | /reader-authoring/flavors/:flavorId/archive | archiveFlavor | ReaderAuthoringController | Deactivate + archive a flavor (P-F8, reversible via archived_at) |
| POST | /reader-authoring/readers/:readerId/archive | archiveReader | ReaderAuthoringController | Retire (soft-archive) a reader — reversible via archived_at |
| POST | /reader-authoring/observation-bindings | bindObservation | ReaderAuthoringController | Bind (version-safe) an Observation Contract to one source entity of a flavor |
| POST | /reader-authoring/admission-bindings | bindAdmission | ReaderAuthoringController | Bind an Admission Contract (reader_binding) to one source entity of a flavor |
| POST | /readers | createReader | ReaderController | Register a new reader |
| POST | /readers/create-from-oc | createReaderFromOc | ReaderController | D209: Create reader + flavor from an existing observation contract |
| GET | /readers/filters | getReaderFilters | ReaderController | Get distinct filter values for readers (domains, subdomains, statuses) |
| GET | /readers/stats | getReaderStats | ReaderController | Per-reader counts: flavors, bindings (for list enrichment) |
| GET | /readers | listReaders | ReaderController | List readers |
| GET | /readers/:readerId | getReader | ReaderController | Get reader by ID |
| PATCH | /readers/:readerId | updateReader | ReaderController | Update a reader |
| DELETE | /readers/:readerId | deleteReader | ReaderController | Delete a reader |
| POST | /readers/:readerId/flavors | createFlavor | ReaderController | Create a reader flavor |
| GET | /readers/:readerId/flavors | listFlavors | ReaderController | List flavors for a reader |
| GET | /readers/:readerId/flavors/:flavorId | getFlavor | ReaderController | Get a reader flavor by ID |
| PATCH | /readers/:readerId/flavors/:flavorId | updateFlavor | ReaderController | Update a reader flavor |
| DELETE | /readers/:readerId/flavors/:flavorId | deleteFlavor | ReaderController | Delete a reader flavor |
| POST | /readers/:readerId/bindings | bindReader | ReaderController | Bind a reader to a contract version |
| GET | /readers/:readerId/bindings | listReaderBindings | ReaderController | List reader bindings |
| POST | /readers/:readerId/bindings/unbind | unbindReader | ReaderController | Unbind a reader from a contract version |
| POST | /readers/:readerId/runs | createAdmissionRun | ReaderController | Create an admission run for a reader |
| GET | /readers/:readerId/runs | listAdmissionRunsByReader | ReaderController | List admission runs for a reader |
| GET | /readers | listAdmissionRuns | ReaderController | List admission runs |
| GET | /readers/:runId | getAdmissionRun | ReaderController | Get admission run by ID |
| PATCH | /readers/:runId | updateAdmissionRun | ReaderController | Update an admission run |
| GET | /readers/stats | getBoundaryStats | ReaderController | Aggregate boundary stats from admission runs (platform DB) |
| GET | /readers/stats | getEvaluationStats | ReaderController | Evaluation stats placeholder (requires tenant DB) |
| GET | /readers/stats | getMetricEvaluationStats | ReaderController | Metric evaluation stats placeholder (requires tenant DB) |
| GET | /readers/stats | getActionStats | ReaderController | Action stats placeholder (requires tenant DB) |
| POST | /readers | createTenantBinding | ReaderController | Create a tenant binding |
| GET | /readers | listTenantBindings | ReaderController | List tenant bindings |
| POST | /readers/deactivate | deactivateTenantBinding | ReaderController | Deactivate a tenant binding |
| POST | /discovery/scans | createScan | DiscoveryController | Create a discovery scan record |
| GET | /discovery/scans | listScans | DiscoveryController | List discovery scans |
| GET | /discovery/scans/stats | getScanStats | DiscoveryController | Discovery scan aggregation stats |
| GET | /discovery/scans/:scanId | getScan | DiscoveryController | Get a discovery scan by ID |
| POST | /discovery/objects | createObject | DiscoveryController | Create a discovered object |
| GET | /discovery/scans/:scanId/objects | listObjectsByScan | DiscoveryController | List discovered objects in a scan |
| GET | /discovery/objects/:objectId | getObject | DiscoveryController | Get a discovered object by ID |
| POST | /discovery/fields | createField | DiscoveryController | Create a discovered field |
| GET | /discovery/objects/:objectId/fields | listFieldsByObject | DiscoveryController | List discovered fields for an object |
| POST | /discovery/diffs | createDiff | DiscoveryController | Create a discovery diff |
| GET | /discovery/scans/:scanId/diff | getDiffByScanId | DiscoveryController | Get the diff for a scan (against previous scan) |
| GET | /seed-catalog/oagis/stats | getStats | OagisSeedController | OAGIS seed stats — noun counts by domain and subfunction |
| GET | /seed-catalog/oagis/domains | getDomains | OagisSeedController | List distinct OAGIS domains with noun counts |
| GET | /seed-catalog/oagis/nouns | listNouns | OagisSeedController | List OAGIS nouns with filters |
| GET | /seed-catalog/oagis/nouns/:slug | getNoun | OagisSeedController | Get single OAGIS noun with all components and fields |
| GET | /seed-catalog/stats | getStats | SeedCatalogController | Seed catalog stats — table counts by system and module |
| GET | /seed-catalog/modules | getModules | SeedCatalogController | List available modules for a system in the seed catalog |
| GET | /seed-catalog/tables | searchTables | SeedCatalogController | Search seed catalog tables |
| GET | /seed-catalog/tables/:name | getTable | SeedCatalogController | Get a single table with all fields |
| GET | /seed-catalog/metrics/stats | getStats | SeedMetricsController | Seed metric stats — counts by function, confidence, and source |
| GET | /seed-catalog/metrics/functions | getFunctions | SeedMetricsController | List available functions in the metric seed catalog |
| GET | /seed-catalog/metrics | searchMetrics | SeedMetricsController | Search seed catalog metrics |
| GET | /seed-catalog/metrics/:metricName | getMetric | SeedMetricsController | Get a single metric with full detail |
| GET | /source-catalog/stats | catalogStats | SourceCatalogStatsController | Platform-wide catalog statistics — totals, by category, by system type, top systems |
| GET | /source-catalog/masters/source-5d | sourceMasters | SourceCatalogStatsController | Source 5D classification master values — volume, velocity, veracity, pattern, criticality (D284) |
| POST | /source-catalog | create | SourceCatalogStatsController | Register a new source provider |
| GET | /source-catalog | list | SourceCatalogStatsController | List source providers |
| GET | /source-catalog/:providerId/stats | stats | SourceCatalogStatsController | Get aggregated catalog statistics for a provider |
| GET | /source-catalog/:providerId | get | SourceCatalogStatsController | Get provider by ID |
| PATCH | /source-catalog/:providerId | update | SourceCatalogStatsController | Update a provider |
| DELETE | /source-catalog/:providerId | delete | SourceCatalogStatsController | Delete a provider |
| POST | /source-catalog | create | SourceCatalogStatsController | Register a new source system |
| GET | /source-catalog/catalog | catalog | SourceCatalogStatsController | List source systems with provider enrichment — powers Source Catalog page |
| GET | /source-catalog | list | SourceCatalogStatsController | List source systems |
| GET | /source-catalog/:systemId | get | SourceCatalogStatsController | Get system by ID |
| PATCH | /source-catalog/:systemId | update | SourceCatalogStatsController | Update a system |
| DELETE | /source-catalog/:systemId | delete | SourceCatalogStatsController | Delete a system |
| POST | /source-catalog | create | SourceCatalogStatsController | Register a new source version |
| GET | /source-catalog | list | SourceCatalogStatsController | List source versions |
| GET | /source-catalog/:versionId | get | SourceCatalogStatsController | Get version by ID |
| PATCH | /source-catalog/:versionId | update | SourceCatalogStatsController | Update a version |
| DELETE | /source-catalog/:versionId | delete | SourceCatalogStatsController | Delete a version |
| POST | /source-catalog | create | SourceCatalogStatsController | Register a new source module |
| GET | /source-catalog | list | SourceCatalogStatsController | List source modules |
| GET | /source-catalog/:moduleId | get | SourceCatalogStatsController | Get module by ID |
| PATCH | /source-catalog/:moduleId | update | SourceCatalogStatsController | Update a module |
| DELETE | /source-catalog/:moduleId | delete | SourceCatalogStatsController | Delete a module |
| POST | /source-catalog | create | SourceCatalogStatsController | Register a new source object |
| GET | /source-catalog | list | SourceCatalogStatsController | List source objects |
| GET | /source-catalog/:objectId | get | SourceCatalogStatsController | Get object by ID |
| PATCH | /source-catalog/:objectId | update | SourceCatalogStatsController | Update an object |
| DELETE | /source-catalog/:objectId | delete | SourceCatalogStatsController | Delete an object |
| POST | /source-catalog | create | SourceCatalogStatsController | Register a new source field |
| GET | /source-catalog | list | SourceCatalogStatsController | List source fields |
| GET | /source-catalog/:fieldId | get | SourceCatalogStatsController | Get field by ID |
| PATCH | /source-catalog/:fieldId | update | SourceCatalogStatsController | Update a field |
| DELETE | /source-catalog/:fieldId | delete | SourceCatalogStatsController | Delete a field |
| GET | /onboarding/overview | getOverview | OnboardingController |  |
| GET | /onboarding/overview/:providerSlug | getProviderDetail | OnboardingController |  |
| GET | /onboarding/stats | getStats | OnboardingController |  |
| GET | /onboarding | list | OnboardingController |  |
| GET | /onboarding/:tableName | getByName | OnboardingController |  |
| GET | /onboarding/stats | getStats | OnboardingController |  |
| GET | /onboarding | list | OnboardingController |  |
| GET | /onboarding/:objectName | getByName | OnboardingController |  |
| GET | /onboarding | list | OnboardingController |  |
| POST | /schema-provisioner/onboard-connector | onboardConnector | ConnectorOnboardingController |  |
| POST | /schema-provisioner/nightly-reconcile | runNightlyReconcile | ConnectorOnboardingController |  |
| POST | /schema-provisioner/onboard-metric | onboardMetric | ConnectorOnboardingController |  |
| POST | /platform/schema-provisioner/drift-check | driftCheck | DriftCheckController |  |
| POST | /support/tickets | createTicket | TicketController | Create a support ticket |
| GET | /support/tickets/stats | getStats | TicketController | Ticket summary stats (by status, category, severity) |
| GET | /support/tickets | listTickets | TicketController | List tickets with optional filters |
| GET | /support/tickets/:ticketId | getTicket | TicketController | Get a ticket by ID (includes comments) |
| PATCH | /support/tickets/:ticketId | updateTicket | TicketController | Update ticket status, severity, or assignment |
| POST | /support/tickets/:ticketId/comments | addComment | TicketController | Add a comment to a ticket |
| GET | /t/context | getContext | TenantContextController | Resolve + validate the caller |
| POST | /tenants | createTenant | TenantManagementController | Create a new tenant (status: provisioning) |
| GET | /tenants/stats | getStats | TenantManagementController | Tenant registry summary stats |
| GET | /tenants | listTenants | TenantManagementController | List all tenants |
| GET | /tenants/:idOrSlug | getTenant | TenantManagementController | Get tenant by ID or slug |
| PATCH | /tenants/:idOrSlug | updateTenant | TenantManagementController | Update tenant (name, status, config) |
| GET | /admin/tenant-metrics/tenants | listTenants | TenantMetricsController |  |
| GET | /admin/tenant-metrics/snapshot | getSnapshot | TenantMetricsController |  |
| GET | /t/beyond/metric-functions | metricFunctions | BeyondMetricsController | Per-function count rollup for the /beyond LHS (all active MCF metrics, MCF-native) |
| GET | /t/beyond/metrics | metrics | BeyondMetricsController | Active MCF metrics for one function, with producing overlay + latest governed snapshot |
| GET | /t/beyond/metrics/:mcUid/snapshot | snapshot | BeyondMetricsController | Latest governed snapshot (value + fiscal period) for one MCF metric on this tenant |
| GET | /t/beyond/metrics/:mcUid | detail | BeyondMetricsController | MCF metric identity + latest governed snapshot for the /beyond detail view |
| GET | /t/discovery/scans | listScans | TenantDiscoveryController | List discovery scans for this tenant |
| GET | /t/discovery/scans/stats | getScanStats | TenantDiscoveryController | Get discovery scan stats for this tenant |
| GET | /t/discovery/scans/:scanId | getScan | TenantDiscoveryController | Get a specific discovery scan |
| GET | /t/discovery/scans/:scanId/objects | listDiscoveredObjects | TenantDiscoveryController | List discovered objects for a scan |
| GET | /t/discovery | listBindings | TenantDiscoveryController | List mapping bindings for this tenant |
| GET | /t/discovery/:bindingId | getBinding | TenantDiscoveryController | Get a specific mapping binding |
| GET | /t/discovery/:bindingId/versions | listVersions | TenantDiscoveryController | List versions for a mapping binding |
| GET | /t/discovery | listRuns | TenantDiscoveryController | List admission runs for this tenant |
| GET | /t/discovery/:runId | getRun | TenantDiscoveryController | Get an admission run by ID |
| GET | /t/discovery | listContracts | TenantDiscoveryController | List contracts visible to this tenant (via bindings) |
| GET | /t/discovery/:contractId | getContract | TenantDiscoveryController | Get a contract by ID |
| GET | /t/discovery/:contractId/versions | listVersions | TenantDiscoveryController | List contract versions |
| GET | /t/discovery | listReaders | TenantDiscoveryController | List readers available to this tenant |
| GET | /t/discovery/filters | getFilters | TenantDiscoveryController | Get reader filter options |
| GET | /t/discovery/:readerId | getReader | TenantDiscoveryController | Get a reader by ID |
| GET | /t/discovery/:readerId/bindings | listBindings | TenantDiscoveryController | List reader bindings |
| GET | /t/discovery/:readerId/runs | listRuns | TenantDiscoveryController | List admission runs for a reader |
| GET | /t/discovery/:readerId/flavors | listFlavors | TenantDiscoveryController | List reader flavors |
| GET | /t/discovery | listConnectors | TenantDiscoveryController | List connectors available to this tenant |
| GET | /t/discovery/:connectorId | getConnector | TenantDiscoveryController | Get a connector by ID |
| POST | /t/discovery | createConnection | TenantDiscoveryController | Create a connection owned by this tenant |
| GET | /t/discovery | listConnections | TenantDiscoveryController | List connections for this tenant |
| GET | /t/discovery/:connectionId | getConnection | TenantDiscoveryController | Get a connection by ID |
| GET | /t/discovery/:connectionId/checks | listChecks | TenantDiscoveryController | List health checks for a connection |
| POST | /t/discovery/:connectionId/checks | recordCheck | TenantDiscoveryController | Record a connection health check (test) for this tenant |
| GET | /t/discovery | listBindings | TenantDiscoveryController | List reader-tenant bindings for this tenant |
| GET | /t/discovery/catalog/function-counts | functionCounts | TenantDiscoveryController |  |
| GET | /t/discovery/catalog | list | TenantDiscoveryController | Tenant-scoped paginated metric catalog with activation + chain overlay |
| GET | /t/discovery/:metricId | getDetail | TenantDiscoveryController | Tenant-scoped metric detail: definition + formulas + knowledge + chain + activation |
| GET | /t/discovery/:metricId/monitor | getMonitor | TenantDiscoveryController |  |
| POST | /admin/test-bench/evaluate-mc-for-tenant | evaluateMcForTenant | AdminTestBenchController |  |
| POST | /admin/test-bench/dispatch-ready-for-tenant | dispatchReadyForTenant | AdminTestBenchController |  |
| POST | /t/test-bench/execute-reader | executeReader | TestBenchExecutionController | Execute reader: fetch → observe → admit |
| POST | /t/test-bench/resolve-canonical | resolveCanonical | TestBenchExecutionController |  |
| POST | /t/test-bench/evaluate-metric | evaluateMetric | TestBenchExecutionController |  |
| POST | /t/test-bench/execute-chain | executeFullChain | TestBenchExecutionController |  |
| POST | /test-bench/scenarios | createScenario | TestBenchController | Create a test scenario |
| GET | /test-bench/scenarios | listScenarios | TestBenchController | List scenarios |
| GET | /test-bench/scenarios/:id | getScenario | TestBenchController | Get scenario by ID |
| PATCH | /test-bench/scenarios/:id | updateScenario | TestBenchController | Update scenario |
| POST | /test-bench/runs | createRun | TestBenchController | Create and queue a test run |
| GET | /test-bench/runs | listRuns | TestBenchController | List runs |
| GET | /test-bench/runs/:id | getRunDetail | TestBenchController | Get run with steps and metrics |
| PATCH | /test-bench/runs/:id/status | updateRunStatus | TestBenchController | Update run status (running/completed/failed/cancelled) |
| POST | /test-bench/runs/:id/steps | publishRunStep | TestBenchController | Publish a boundary step result |
| POST | /test-bench/runs/:id/metrics | publishRunMetric | TestBenchController | Publish a metric accuracy result |
| GET | /test-bench/preflight/:metricContractId | preflight | TestBenchController |  |
| GET | /test-bench/preflight | preflightBatch | TestBenchController |  |
