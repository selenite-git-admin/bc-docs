---
title: "Schema Reference"
type: generated-reference
status: generated
authority: source-derived
source_repo: bc-core
source_commit: 44767f0
generated_at: 2026-07-06T09:32:32.971208+00:00
generator: generate_source_references.py
---

# Schema Reference

Generated from Drizzle schema files in `bc-core`.

## Domains

| Domain | Files | Tables |
|---|---|---|
| ai-telemetry | 4 | 2 |
| bcf | 7 | 5 |
| concept-registry | 6 | 12 |
| contract | 27 | 42 |
| envelope | 1 | 6 |
| evidence | 1 | 3 |
| execution | 4 | 5 |
| index | 1 | 0 |
| infrastructure | 6 | 4 |
| master | 35 | 34 |
| mcf | 24 | 22 |
| metric | 14 | 15 |
| operations | 14 | 15 |
| platform | 6 | 4 |
| pricing | 3 | 1 |
| progression | 1 | 14 |
| public | 1 | 0 |
| registry | 1 | 0 |
| runtime | 6 | 12 |
| source | 4 | 9 |
| support | 3 | 2 |
| tenant | 7 | 4 |
| tenant-db | 7 | 3 |
| tenant-user | 1 | 0 |
| test-bench | 6 | 4 |
| users | 3 | 1 |

## Files

| Domain | Source | Tables | Exports |
|---|---|---|---|
| ai-telemetry | src/database/schema/ai-telemetry/ai-call-ledger.ts | ai_call_ledger | aiCallLedger |
| ai-telemetry | src/database/schema/ai-telemetry/ai-run-ledger.ts | ai_run_ledger | aiRunLedger |
| ai-telemetry | src/database/schema/ai-telemetry/index.ts | none detected |  |
| ai-telemetry | src/database/schema/ai-telemetry/pg-schema.ts | none detected | aiTelemetrySchema |
| bcf | src/database/schema/bcf/authoring-panel-rejection-log.ts | authoring_panel_rejection_log | authoringPanelRejectionLog |
| bcf | src/database/schema/bcf/calibration-event.ts | calibration_event | calibrationEvent |
| bcf | src/database/schema/bcf/certification-record.ts | certification_record | certificationRecord |
| bcf | src/database/schema/bcf/index.ts | none detected |  |
| bcf | src/database/schema/bcf/oagis-seed.ts | oagis_seed | oagisSeed |
| bcf | src/database/schema/bcf/panel-output-record.ts | panel_output_record | panelOutputRecord |
| bcf | src/database/schema/bcf/pg-schema.ts | none detected | bcfSchema |
| concept-registry | src/database/schema/concept-registry/business-concept.ts | business_concept, business_concept_supersession, business_concept_version | businessConcept, businessConceptSupersession, businessConceptVersion |
| concept-registry | src/database/schema/concept-registry/entity.ts | entity, entity_supersession, entity_version | entity, entitySupersession, entityVersion |
| concept-registry | src/database/schema/concept-registry/index.ts | none detected |  |
| concept-registry | src/database/schema/concept-registry/pg-schema.ts | none detected | conceptRegistrySchema |
| concept-registry | src/database/schema/concept-registry/supersession-proposal.ts | supersession_proposal | supersessionProposal |
| concept-registry | src/database/schema/concept-registry/vocabulary.ts | alias, characteristic, characteristic_definition_amendment, characteristic_supersession, representation_term | alias, characteristic, characteristicDefinitionAmendment, characteristicSupersession, representationTerm |
| contract | src/database/schema/contract/admission-contract.ts | admission_contract, admission_contract_approval, admission_contract_version | admissionContract, admissionContractApproval, admissionContractVersion |
| contract | src/database/schema/contract/ai-contract.ts | ai_contract, ai_contract_approval, ai_contract_version | aiContract, aiContractApproval, aiContractVersion |
| contract | src/database/schema/contract/authoring-panel-rejection-log.ts | authoring_panel_rejection_log | authoringPanelRejectionLog |
| contract | src/database/schema/contract/calibration-event.ts | calibration_event | calibrationEvent |
| contract | src/database/schema/contract/canonical-contract.ts | canonical_contract, canonical_contract_approval, canonical_contract_version | canonicalContract, canonicalContractApproval, canonicalContractVersion |
| contract | src/database/schema/contract/canonical-mapping.ts | canonical_mapping, canonical_mapping_version | canonicalMapping, canonicalMappingVersion |
| contract | src/database/schema/contract/certification-record.ts | certification_record | certificationRecord |
| contract | src/database/schema/contract/chain-status.ts | chain_status, chain_trace | chainStatus, chainTrace |
| contract | src/database/schema/contract/cohort-signal.ts | cohort_signal | cohortSignal |
| contract | src/database/schema/contract/contract-lineage.ts | contract_lineage | contractLineage |
| contract | src/database/schema/contract/contract-meta-schema.ts | contract_meta_schema | contractMetaSchema |
| contract | src/database/schema/contract/framework-policy.ts | framework_policy | frameworkPolicy |
| contract | src/database/schema/contract/index.ts | none detected |  |
| contract | src/database/schema/contract/intake-queue.ts | intake_queue | intakeQueue |
| contract | src/database/schema/contract/intervention-contract.ts | intervention_contract, intervention_contract_approval, intervention_contract_version | interventionContract, interventionContractApproval, interventionContractVersion |
| contract | src/database/schema/contract/l-node-semantic-trace.ts | l_node_semantic_trace | lNodeSemanticTrace |
| contract | src/database/schema/contract/l-node-semantic-verdict.ts | l_node_semantic_verdict | lNodeSemanticVerdict |
| contract | src/database/schema/contract/mc-envelope-audit-record.ts | mc_envelope_audit_record | mcEnvelopeAuditRecord |
| contract | src/database/schema/contract/mc-integrity-state.ts | mc_integrity_state | mcIntegrityState |
| contract | src/database/schema/contract/metric-contract.ts | metric_contract, metric_contract_approval, metric_contract_version | metricContract, metricContractApproval, metricContractVersion |
| contract | src/database/schema/contract/observation-contract.ts | observation_contract, observation_contract_approval, observation_contract_version, observation_field_map | observationContract, observationContractApproval, observationContractVersion, observationFieldMap |
| contract | src/database/schema/contract/operator-confirm-rule.ts | operator_confirm_rule | operatorConfirmRule |
| contract | src/database/schema/contract/panel-output-record.ts | panel_output_record | panelOutputRecord |
| contract | src/database/schema/contract/pg-schema.ts | none detected | contractSchema |
| contract | src/database/schema/contract/phase-state.ts | phase_state | phaseState |
| contract | src/database/schema/contract/primitive-provenance.ts | primitive_provenance | primitiveProvenance |
| contract | src/database/schema/contract/source-contract.ts | source_contract, source_contract_approval, source_contract_version | sourceContract, sourceContractApproval, sourceContractVersion |
| envelope | src/database/schema/envelope.ts | action_evaluation, action_object, metric_evaluation, metric_snapshot, observed_record, source_object | actionEvaluation, actionObject, envelopeSchema, metricEvaluation, metricSnapshot, observedRecord, sourceObject |
| evidence | src/database/schema/evidence.ts | evidence_object, evidence_record, lineage_object | evidenceObject, evidenceRecord, evidenceSchema, lineageObject |
| execution | src/database/schema/execution/boundary-rollup.ts | boundary_rollup | boundaryRollup |
| execution | src/database/schema/execution/index.ts | none detected |  |
| execution | src/database/schema/execution/pg-schema.ts | none detected | executionSchema |
| execution | src/database/schema/execution/run-summary.ts | boundary_health, boundary_progression, rejection_summary, run_summary | boundaryHealth, boundaryProgression, rejectionSummary, runSummary |
| index | src/database/schema/index.ts | none detected |  |
| infrastructure | src/database/schema/infrastructure/email-template.ts | email_template | emailTemplate |
| infrastructure | src/database/schema/infrastructure/feature-flag.ts | feature_flag | featureFlag |
| infrastructure | src/database/schema/infrastructure/idempotency-keys.ts | idempotency_keys | idempotencyKeys |
| infrastructure | src/database/schema/infrastructure/index.ts | none detected |  |
| infrastructure | src/database/schema/infrastructure/notification-log.ts | notification_log | notificationLog |
| infrastructure | src/database/schema/infrastructure/pg-schema.ts | none detected | infrastructureSchema |
| master | src/database/schema/master/dim-country.ts | dim_country | dimCountry |
| master | src/database/schema/master/dim-currency.ts | dim_currency | dimCurrency |
| master | src/database/schema/master/dim-date.ts | dim_date | dimDate |
| master | src/database/schema/master/dim-fiscal-calendar.ts | dim_fiscal_calendar | dimFiscalCalendar |
| master | src/database/schema/master/dim-fiscal-period.ts | dim_fiscal_period | dimFiscalPeriod |
| master | src/database/schema/master/index.ts | none detected |  |
| master | src/database/schema/master/library.ts | library | library |
| master | src/database/schema/master/mapping-binding.ts | mapping_binding, mapping_binding_version | mappingBinding, mappingBindingVersion |
| master | src/database/schema/master/master-definition-standard.ts | master_definition_standard | masterDefinitionStandard |
| master | src/database/schema/master/master-domain.ts | master_function | masterFunction |
| master | src/database/schema/master/master-dqc-rule.ts | master_dqc_rule | masterDqcRule |
| master | src/database/schema/master/master-industry-category.ts | master_industry_category | masterIndustryCategory |
| master | src/database/schema/master/master-industry.ts | master_industry | masterIndustry |
| master | src/database/schema/master/master-metric-category.ts | master_metric_category | masterMetricCategory |
| master | src/database/schema/master/master-metric-composition.ts | master_metric_composition | masterMetricComposition |
| master | src/database/schema/master/master-metric-direction.ts | master_metric_direction | masterMetricDirection |
| master | src/database/schema/master/master-metric-impact.ts | master_metric_impact | masterMetricImpact |
| master | src/database/schema/master/master-metric-precision.ts | master_metric_precision | masterMetricPrecision |
| master | src/database/schema/master/master-metric-purpose.ts | master_metric_purpose | masterMetricPurpose |
| master | src/database/schema/master/master-metric-shape.ts | master_metric_shape | masterMetricShape |
| master | src/database/schema/master/master-metric-temporality.ts | master_metric_temporality | masterMetricTemporality |
| master | src/database/schema/master/master-metric-type.ts | master_metric_type | masterMetricType |
| master | src/database/schema/master/master-semantic-family.ts | semantic_family | masterSemanticFamily |
| master | src/database/schema/master/master-source-criticality.ts | master_source_criticality | masterSourceCriticality |
| master | src/database/schema/master/master-source-pattern.ts | master_source_pattern | masterSourcePattern |
| master | src/database/schema/master/master-source-velocity.ts | master_source_velocity | masterSourceVelocity |
| master | src/database/schema/master/master-source-veracity.ts | master_source_veracity | masterSourceVeracity |
| master | src/database/schema/master/master-source-volume.ts | master_source_volume | masterSourceVolume |
| master | src/database/schema/master/master-status.ts | master_status | masterStatus |
| master | src/database/schema/master/master-subdomain.ts | master_subfunction | masterSubfunction |
| master | src/database/schema/master/master-system-type.ts | master_system_type | masterSystemType |
| master | src/database/schema/master/master-unit-type.ts | master_unit_type | masterUnitType |
| master | src/database/schema/master/pg-schema.ts | none detected | masterSchema |
| master | src/database/schema/master/standard-field.ts | standard_field | standardField |
| master | src/database/schema/master/tenant-applicability-industry.ts | industry | tenantApplicabilityIndustry |
| mcf | src/database/schema/mcf/certification-record.ts | certification_record | certificationRecord |
| mcf | src/database/schema/mcf/chain-audit-evidence.ts | chain_audit_evidence | chainAuditEvidence, mcfSchema |
| mcf | src/database/schema/mcf/chain-enrichment-plan.ts | chain_enrichment_plan | chainEnrichmentPlan, mcfSchema |
| mcf | src/database/schema/mcf/evidence-source-allowlist.ts | evidence_source_allowlist | evidenceSourceAllowlist |
| mcf | src/database/schema/mcf/index.ts | none detected |  |
| mcf | src/database/schema/mcf/metric-authoring-intake-queue.ts | metric_authoring_intake_queue | metricAuthoringIntakeQueue |
| mcf | src/database/schema/mcf/metric-authoring-panel-run.ts | metric_authoring_panel_run | metricAuthoringPanelRun |
| mcf | src/database/schema/mcf/metric-authoring-panel-transcript.ts | metric_authoring_panel_transcript | metricAuthoringPanelTranscript |
| mcf | src/database/schema/mcf/metric-cert-writer-idempotency.ts | metric_cert_writer_idempotency | metricCertWriterIdempotency |
| mcf | src/database/schema/mcf/metric-computed-dimension-ref.ts | metric_computed_dimension_ref | metricComputedDimensionRef |
| mcf | src/database/schema/mcf/metric-contract-revision.ts | metric_contract_revision | metricContractRevision |
| mcf | src/database/schema/mcf/metric-contract-version.ts | metric_contract_version | metricContractVersion |
| mcf | src/database/schema/mcf/metric-contract.ts | metric_contract | metricContract |
| mcf | src/database/schema/mcf/metric-filter-clause.ts | metric_filter_clause | metricFilterClause |
| mcf | src/database/schema/mcf/metric-knowledge-profile.ts | metric_knowledge_profile | metricKnowledgeProfile |
| mcf | src/database/schema/mcf/metric-publication-eligibility-result.ts | metric_publication_eligibility_result | metricPublicationEligibilityResult |
| mcf | src/database/schema/mcf/metric-self-verification-fixture.ts | metric_self_verification_fixture | metricSelfVerificationFixture |
| mcf | src/database/schema/mcf/metric-self-verification-result.ts | metric_self_verification_result | metricSelfVerificationResult |
| mcf | src/database/schema/mcf/metric-supersession.ts | metric_supersession | metricSupersession |
| mcf | src/database/schema/mcf/metric-variable-binding.ts | metric_variable_binding | metricVariableBinding |
| mcf | src/database/schema/mcf/pg-schema.ts | none detected | mcfSchema |
| mcf | src/database/schema/mcf/role-grant-audit.ts | role_grant_audit | roleGrantAudit |
| mcf | src/database/schema/mcf/seed-metric.ts | seed_metric | seedMetric |
| mcf | src/database/schema/mcf/workspace-tool-allowlist.ts | workspace_tool_allowlist | workspaceToolAllowlist |
| metric | src/database/schema/metric/enrichment-job.ts | metric_enrichment_job | metricEnrichmentJob |
| metric | src/database/schema/metric/index.ts | none detected |  |
| metric | src/database/schema/metric/intentional-reuse-pattern.ts | intentional_reuse_pattern | intentionalReusePattern |
| metric | src/database/schema/metric/lifecycle-event-log.ts | lifecycle_event_log | lifecycleEventLog |
| metric | src/database/schema/metric/mc-dependency.ts | mc_dependency | mcDependency |
| metric | src/database/schema/metric/metric-binding.ts | metric_binding | metricBinding |
| metric | src/database/schema/metric/metric-contract-version-activation-log.ts | metric_contract_version_activation_log | metricContractVersionActivationLog |
| metric | src/database/schema/metric/metric-definition.ts | metric_definition, metric_knowledge | metricDefinition, metricKnowledge |
| metric | src/database/schema/metric/metric-formula.ts | metric_formula, metric_formula_variable, metric_formula_verification | metricFormula, metricFormulaVariable, metricFormulaVerification |
| metric | src/database/schema/metric/mls-state-event.ts | mls_state_event | mlsStateEvent |
| metric | src/database/schema/metric/mls-state.ts | mls_state | mlsState |
| metric | src/database/schema/metric/mls-trigger-binding.ts | mls_trigger_binding | mlsTriggerBinding |
| metric | src/database/schema/metric/pg-schema.ts | none detected | metricSchema |
| metric | src/database/schema/metric/readiness-ledger.ts | readiness_ledger | readinessLedger |
| operations | src/database/schema/operations/activity-log.ts | activity_log | activityLog |
| operations | src/database/schema/operations/audit-log.ts | audit_log | auditLog |
| operations | src/database/schema/operations/bo-enrichment-log.ts | bo_enrichment_log | boEnrichmentLog |
| operations | src/database/schema/operations/bo-verification-log.ts | bo_verification_log | boVerificationLog |
| operations | src/database/schema/operations/catalog-verification-log.ts | catalog_verification_log | catalogVerificationLog |
| operations | src/database/schema/operations/discovery.ts | discovered_field, discovered_object, discovery_diff, discovery_scan | discoveredField, discoveredObject, discoveryDiff, discoveryScan |
| operations | src/database/schema/operations/dsar-response.ts | dsar_response | dsarResponse |
| operations | src/database/schema/operations/index.ts | none detected |  |
| operations | src/database/schema/operations/nullification-action.ts | nullification_action | nullificationAction |
| operations | src/database/schema/operations/nullification-request.ts | nullification_request | nullificationRequest |
| operations | src/database/schema/operations/pg-schema.ts | none detected | operationsSchema |
| operations | src/database/schema/operations/pii-field-registry.ts | pii_field_registry | piiFieldRegistry |
| operations | src/database/schema/operations/platform-inspection-audit-log.ts | platform_inspection_audit_log | platformInspectionAuditLog |
| operations | src/database/schema/operations/retention-policy.ts | retention_policy | retentionPolicy |
| platform | src/database/schema/platform/index.ts | none detected |  |
| platform | src/database/schema/platform/library.ts | library | library |
| platform | src/database/schema/platform/master-domain.ts | master_function | masterFunction |
| platform | src/database/schema/platform/master-status.ts | master_status | masterStatus |
| platform | src/database/schema/platform/master-subdomain.ts | master_subfunction | masterSubfunction |
| platform | src/database/schema/platform/pg-schema.ts | none detected | platformSchema |
| pricing | src/database/schema/pricing/index.ts | none detected |  |
| pricing | src/database/schema/pricing/package.ts | package | subscriptionPackage |
| pricing | src/database/schema/pricing/pg-schema.ts | none detected | pricingSchema |
| progression | src/database/schema/progression.ts | admission, admission_run, canonical_evaluation, canonical_run, evaluation_campaign, evaluation_campaign_run, intervention_evaluation, intervention_run, metric_evaluation, metric_run, metric_snapshot_index, reader_watermark, runtime_event, webhook_delivery | admission, admissionRun, canonicalEvaluation, canonicalRun, evaluationCampaign, evaluationCampaignRun, interventionEvaluation, interventionRun, metricEvaluation, metricRun, metricSnapshotIndex, progressionSchema ... |
| public | src/database/schema/public.ts | none detected |  |
| registry | src/database/schema/registry/index.ts | none detected |  |
| runtime | src/database/schema/runtime/connection.ts | connection, connection_check, connection_config | connection, connectionCheck, connectionConfig |
| runtime | src/database/schema/runtime/connector.ts | connector, connector_protocol, connector_provenance | connector, connectorProtocol, connectorProvenance |
| runtime | src/database/schema/runtime/index.ts | none detected |  |
| runtime | src/database/schema/runtime/pg-schema.ts | none detected | runtimeSchema |
| runtime | src/database/schema/runtime/reader.ts | admission_run, reader, reader_binding, reader_flavor, reader_observation_binding | admissionRun, reader, readerBinding, readerFlavor, readerObservationBinding |
| runtime | src/database/schema/runtime/webhook-endpoint.ts | webhook_endpoint | webhookEndpoint |
| source | src/database/schema/source/index.ts | none detected |  |
| source | src/database/schema/source/pg-schema.ts | none detected | sourceSchema |
| source | src/database/schema/source/source-catalog.ts | source_field, source_module, source_object, source_provider, source_system, source_version | sourceField, sourceModule, sourceObject, sourceProvider, sourceSystem, sourceVersion |
| source | src/database/schema/source/source-reference.ts | sap_cds_field_mapping, sap_cds_reference, sap_table_reference | sapCdsFieldMapping, sapCdsReference, sapTableReference |
| support | src/database/schema/support/index.ts | none detected |  |
| support | src/database/schema/support/pg-schema.ts | none detected | supportSchema |
| support | src/database/schema/support/ticket.ts | ticket, ticket_comment | ticket, ticketComment |
| tenant-db | src/database/schema/tenant-db/organization/fiscal-calendar-config.ts | fiscal_calendar_config | fiscalCalendarConfig |
| tenant-db | src/database/schema/tenant-db/organization/index.ts | none detected |  |
| tenant-db | src/database/schema/tenant-db/organization/org-profile.ts | org_profile | orgProfile |
| tenant-db | src/database/schema/tenant-db/organization/pg-schema.ts | none detected | organizationSchema |
| tenant-db | src/database/schema/tenant-db/tenant_dim/dim-legal-entity.ts | dim_legal_entity | dimLegalEntity |
| tenant-db | src/database/schema/tenant-db/tenant_dim/index.ts | none detected |  |
| tenant-db | src/database/schema/tenant-db/tenant_dim/pg-schema.ts | none detected | tenantDimSchema |
| tenant-user | src/database/schema/tenant-user.ts | none detected | users |
| tenant | src/database/schema/tenant.ts | none detected | users |
| tenant | src/database/schema/tenant/contract-binding.ts | contract_binding | contractBinding |
| tenant | src/database/schema/tenant/index.ts | none detected |  |
| tenant | src/database/schema/tenant/pg-schema.ts | none detected | tenantSchema |
| tenant | src/database/schema/tenant/tenant-binding.ts | tenant_binding | tenantBinding |
| tenant | src/database/schema/tenant/tenant-infrastructure.ts | tenant_infrastructure | tenantInfrastructure |
| tenant | src/database/schema/tenant/tenants.ts | tenants | tenants |
| test-bench | src/database/schema/test-bench/index.ts | none detected |  |
| test-bench | src/database/schema/test-bench/pg-schema.ts | none detected | testBenchSchema |
| test-bench | src/database/schema/test-bench/run-metric.ts | run_metric | runMetric |
| test-bench | src/database/schema/test-bench/run-step.ts | run_step | runStep |
| test-bench | src/database/schema/test-bench/run.ts | run | run |
| test-bench | src/database/schema/test-bench/scenario.ts | scenario | scenario |
| users | src/database/schema/users/index.ts | none detected |  |
| users | src/database/schema/users/pg-schema.ts | none detected | usersSchema |
| users | src/database/schema/users/platform-user.ts | platform_user | platformUser |
