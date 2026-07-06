# Bidirectional bc-core Documentation Audit

Generated: `2026-07-06T13:17:05.530325+00:00`
Audit run: `80`
bc-core commit: `44767f0`

## Code Fact Inventory

| Fact Type | Facts |
|---|---|
| code_path | 1107 |
| controller | 105 |
| endpoint | 489 |
| env_var | 415 |
| guard | 7 |
| interceptor | 4 |
| middleware | 2 |
| module | 59 |
| schema_table | 557 |
| script_command | 34 |
| service | 168 |

## Doc Claim Grounding

| Claim Type | Status | Claims |
|---|---|---|
| class_symbol | grounded | 416 |
| class_symbol | ungrounded | 53 |
| code_path | ambiguous | 108 |
| code_path | grounded | 136 |
| code_path | out_of_scope | 62 |
| code_path | ungrounded | 134 |
| endpoint | grounded | 58 |
| endpoint | out_of_scope | 54 |
| endpoint | ungrounded | 56 |
| endpoint_path | ambiguous | 1 |
| endpoint_path | grounded | 20 |
| endpoint_path | out_of_scope | 25 |
| endpoint_path | ungrounded | 60 |
| env_var | ambiguous | 9 |
| env_var | grounded | 5 |
| env_var | ungrounded | 15 |
| schema_table | ambiguous | 585 |
| schema_table | grounded | 297 |

## Ungrounded Claim Hotspots

| Document | Claim Type | Ungrounded Claims |
|---|---|---|
| docs/implementation/audit-and-activity-logging.md | code_path | 20 |
| docs/implementation/internal-modules.md | class_symbol | 20 |
| docs/implementation/api-surface.md | endpoint_path | 17 |
| docs/development/documentation-system.md | code_path | 15 |
| docs/onboarding/business-field-and-business-object-onboarding.md | endpoint | 11 |
| docs/development/quality-assurance.md | code_path | 10 |
| docs/development/build-and-release.md | code_path | 8 |
| docs/onboarding/source-registration.md | endpoint | 8 |
| docs/development/decision-and-change-procedure.md | code_path | 7 |
| docs/implementation/audit-and-activity-logging.md | endpoint_path | 7 |
| docs/implementation/internal-modules.md | code_path | 7 |
| docs/development/metric-readiness-toolkit.md | endpoint_path | 6 |
| docs/operating-model/metric-management-system.md | class_symbol | 6 |
| docs/development/metric-readiness-toolkit.md | endpoint | 5 |
| docs/implementation/backend-services.md | code_path | 5 |
| docs/implementation/backend-services.md | env_var | 5 |
| docs/implementation/frontend-experience.md | endpoint_path | 5 |
| docs/implementation/synthetic-data-and-testing.md | code_path | 5 |
| docs/onboarding/source-and-admission-contract-creation.md | endpoint | 5 |
| docs/reference/technical-notes/implementation/metric-context-framework-gap-survey.md | class_symbol | 5 |
| docs/compliance/iso-27001-conformance.md | code_path | 4 |
| docs/compliance/risk-and-vendor-management.md | code_path | 4 |
| docs/implementation/internal-modules.md | endpoint_path | 4 |
| docs/implementation/synthetic-data-and-testing.md | endpoint_path | 4 |
| docs/onboarding/multi-standard-onboarding.md | endpoint | 4 |
| docs/operations/upgrade-and-migration.md | code_path | 4 |
| docs/overview/platform-overview.md | code_path | 4 |
| docs/reference/technical-notes/implementation/core-chain-golden-path.md | endpoint_path | 4 |
| docs/implementation/audit-and-activity-logging.md | endpoint | 3 |
| docs/implementation/backend-services.md | endpoint_path | 3 |

## Code-To-Doc Coverage Depth

| Fact Type | Coverage Depth | Facts |
|---|---|---|
| code_path | not_required | 1107 |
| controller | current_grounded | 9 |
| controller | generated_only | 96 |
| endpoint | current_grounded | 40 |
| endpoint | generated_only | 449 |
| env_var | current_claim_unverified | 6 |
| env_var | current_grounded | 4 |
| env_var | generated_only | 403 |
| env_var | uncovered | 2 |
| guard | current_grounded | 3 |
| guard | uncovered | 4 |
| interceptor | current_grounded | 3 |
| interceptor | uncovered | 1 |
| middleware | current_grounded | 2 |
| module | current_grounded | 27 |
| module | generated_only | 32 |
| schema_table | current_claim_unverified | 116 |
| schema_table | current_grounded | 48 |
| schema_table | generated_only | 393 |
| script_command | generated_only | 34 |
| service | current_grounded | 46 |
| service | generated_only | 122 |

## Ungrounded Current Claims

| Document | Line | Claim Type | Claim | Rationale |
|---|---|---|---|---|
| docs/compliance/infosec-and-access-control.md | 108 | endpoint_path | /api/docs/* | No matching bc-core code fact was found. |
| docs/compliance/iso-27001-conformance.md | 87 | code_path | src/db.js | No matching bc-core code fact was found. |
| docs/compliance/iso-27001-conformance.md | 149 | code_path | src/db.js | No matching bc-core code fact was found. |
| docs/compliance/iso-27001-conformance.md | 170 | code_path | scripts/adr-audit.js | No matching bc-core code fact was found. |
| docs/compliance/iso-27001-conformance.md | 203 | code_path | scripts/adr-audit.js | No matching bc-core code fact was found. |
| docs/compliance/risk-and-vendor-management.md | 36 | code_path | src/db.js | No matching bc-core code fact was found. |
| docs/compliance/risk-and-vendor-management.md | 63 | code_path | src/db.js | No matching bc-core code fact was found. |
| docs/compliance/risk-and-vendor-management.md | 63 | code_path | src/routes/risks.js | No matching bc-core code fact was found. |
| docs/compliance/risk-and-vendor-management.md | 136 | code_path | src/routes/risks.js | No matching bc-core code fact was found. |
| docs/development/build-and-release.md | 49 | code_path | scripts/codeartifact-refresh.js | No matching bc-core code fact was found. |
| docs/development/build-and-release.md | 59 | code_path | src/index.js | No matching bc-core code fact was found. |
| docs/development/build-and-release.md | 65 | code_path | scripts/sync-docs.js | No matching bc-core code fact was found. |
| docs/development/build-and-release.md | 111 | code_path | scripts/seed.js | No matching bc-core code fact was found. |
| docs/development/build-and-release.md | 115 | code_path | scripts/seed.js | No matching bc-core code fact was found. |
| docs/development/build-and-release.md | 123 | code_path | scripts/codeartifact-refresh.js | No matching bc-core code fact was found. |
| docs/development/build-and-release.md | 130 | code_path | scripts/codeartifact-refresh.js | No matching bc-core code fact was found. |
| docs/development/build-and-release.md | 203 | code_path | scripts/sync-docs.js | No matching bc-core code fact was found. |
| docs/development/decision-and-change-procedure.md | 77 | code_path | src/lib/decision-code-reconcile.js | No matching bc-core code fact was found. |
| docs/development/decision-and-change-procedure.md | 88 | code_path | scripts/adr-audit.js | No matching bc-core code fact was found. |
| docs/development/decision-and-change-procedure.md | 94 | code_path | scripts/adr-audit.js | No matching bc-core code fact was found. |
| docs/development/decision-and-change-procedure.md | 96 | code_path | scripts/adr-audit.js | No matching bc-core code fact was found. |
| docs/development/decision-and-change-procedure.md | 110 | code_path | src/routes/decisions.js | No matching bc-core code fact was found. |
| docs/development/decision-and-change-procedure.md | 125 | code_path | src/routes/change-records.js | No matching bc-core code fact was found. |
| docs/development/decision-and-change-procedure.md | 203 | code_path | scripts/adr-backfill-implemented.js | No matching bc-core code fact was found. |
| docs/development/devhub.md | 133 | env_var | BC_DOCS_PATH | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 73 | code_path | scripts/sync-docs.js | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 99 | code_path | scripts/sync-docs.js | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 103 | env_var | V3_DOCS_ROOT | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 112 | code_path | scripts/sync-docs.js | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 116 | code_path | scripts/generate-data-dictionary.mjs | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 128 | code_path | scripts/generate-data-dictionary.mjs | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 136 | env_var | BC_DOCS_PATH | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 143 | code_path | src/lib/doc-scanner.js | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 147 | code_path | scripts/adr-audit.js | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 169 | code_path | scripts/diagram-rewrite.mjs | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 173 | code_path | scripts/diagram-rewrite.mjs | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 177 | code_path | scripts/reference/aws-rewrite-checklist.md | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 190 | code_path | scripts/reference/aws-rewrite-checklist.md | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 221 | code_path | scripts/sync-docs.js | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 221 | code_path | src/lib/doc-scanner.js | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 234 | code_path | scripts/adr-audit.js | No matching bc-core code fact was found. |
| docs/development/documentation-system.md | 266 | code_path | scripts/reference/aws-rewrite-checklist.md | No matching bc-core code fact was found. |
| docs/development/metric-readiness-toolkit.md | 42 | endpoint_path | /api/admin/readiness/* | No matching bc-core code fact was found. |
| docs/development/metric-readiness-toolkit.md | 43 | endpoint_path | /api/admin/tenant-metrics/* | No matching bc-core code fact was found. |
| docs/development/metric-readiness-toolkit.md | 44 | endpoint_path | /api/admin/test-bench/* | No matching bc-core code fact was found. |
| docs/development/metric-readiness-toolkit.md | 44 | endpoint_path | /api/t/test-bench/* | No matching bc-core code fact was found. |
| docs/development/metric-readiness-toolkit.md | 45 | endpoint_path | /api/admin/inspection/* | No matching bc-core code fact was found. |
| docs/development/metric-readiness-toolkit.md | 46 | endpoint_path | /api/schema-provisioner/* | No matching bc-core code fact was found. |
| docs/development/metric-readiness-toolkit.md | 176 | endpoint | POST /admin/readiness/tenant/ | No matching bc-core code fact was found. |
| docs/development/metric-readiness-toolkit.md | 179 | endpoint | GET /admin/inspection/header/... | No matching bc-core code fact was found. |
| docs/development/metric-readiness-toolkit.md | 188 | endpoint | GET /admin/readiness/{catalog | No matching bc-core code fact was found. |
| docs/development/metric-readiness-toolkit.md | 190 | endpoint | POST /admin/readiness/tenant/ | No matching bc-core code fact was found. |
| docs/development/metric-readiness-toolkit.md | 196 | endpoint | GET /api/admin/test-bench/survey-mcs | No matching bc-core code fact was found. |
| docs/development/metric-readiness-toolkit.md | 202 | class_symbol | ArSurveyService | No matching bc-core code fact was found. |
| docs/development/quality-assurance.md | 100 | code_path | src/evaluation/ | No matching bc-core code fact was found. |
| docs/development/quality-assurance.md | 100 | code_path | src/readers/ | No matching bc-core code fact was found. |
| docs/development/quality-assurance.md | 100 | code_path | src/canonical/ | No matching bc-core code fact was found. |
| docs/development/quality-assurance.md | 100 | code_path | src/metrics/ | No matching bc-core code fact was found. |
| docs/development/quality-assurance.md | 100 | code_path | src/boundaries/ | No matching bc-core code fact was found. |
| docs/development/quality-assurance.md | 100 | code_path | src/admission/ | No matching bc-core code fact was found. |
| docs/development/quality-assurance.md | 100 | code_path | src/observation/ | No matching bc-core code fact was found. |
| docs/development/quality-assurance.md | 147 | code_path | src/lib/qa-audit.js | No matching bc-core code fact was found. |
| docs/development/quality-assurance.md | 159 | code_path | src/lib/qa-audit.js | No matching bc-core code fact was found. |
| docs/development/quality-assurance.md | 159 | code_path | src/db.js | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 46 | endpoint_path | /api | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 47 | endpoint_path | /api/t | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 49 | endpoint_path | /api/docs | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 51 | endpoint_path | /api/static/* | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 53 | endpoint_path | /api/docs | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 53 | endpoint_path | /api/docs/{subpath} | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 53 | endpoint_path | /api/docs/* | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 64 | endpoint_path | /api/t/admission-runs | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 64 | endpoint_path | /api/contracts/{id}/versions | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 189 | endpoint_path | /api/docs/* | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 203 | endpoint_path | /api/t | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 205 | endpoint_path | /api/t | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 218 | class_symbol | SwaggerModule | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 218 | endpoint_path | /api/docs | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 241 | endpoint_path | /api/docs/* | No matching bc-core code fact was found. |
| docs/implementation/api-surface.md | 253 | endpoint_path | /api/docs/* | No matching bc-core code fact was found. |
