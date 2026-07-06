# v4 Cleanup Queue

Generated: `2026-07-06T11:51:33.674370+00:00`
Audit run: `75`
Coverage run: `21`

## Gate Status

- Target documents registered: `977`
- Audit errors/blockers: `0`
- Broken-link findings: `0`
- Warning findings: `33`
- Informational findings: `228`
- Mutable-claim review lines: `0`
- Mutable-claim body lines: `0`
- Generated references still pending regeneration: `0`
- bc-core coverage targets linked: `1107/1107`

## Audit Categories

| Severity | Category | Findings |
|---|---|---|
| warning | stale-doc-root-reference | 33 |
| info | stale-doc-root-reference | 228 |

## Remaining Queues

1. Regenerate source-derived references: `0` generated reference document(s) are missing or stale.
2. Review mutable current/reference claims: `0` warning rows across temporal wording, dates, percentages, large numbers, and unit/count claims.
3. Defer v3 cutover references: `261` remaining legacy-root mentions are warnings/info; after dead-root cleanup these should be v3-only until Claude/v3 cutover.
4. Preserve bc-core coverage: all tracked bc-core targets are linked; keep generated references fresh as code evolves.

## Stale Root Tokens

| Severity | Token | Findings |
|---|---|---|
| info | bc-docs-v3 | 228 |
| warning | C:\MyProjects\bc-docs-v3 | 1 |
| warning | bc-docs-v3 | 32 |

## Migration Decisions

| Decision | Documents |
|---|---|
| archive_only | 7 |
| migrate_current | 92 |
| migrate_evidence | 281 |
| migrate_governance | 479 |
| migrate_reference | 89 |
| regenerate_from_source | 23 |
| reject_do_not_migrate | 1 |

## Generated References Pending

| Source | Planned Target | Rationale |
|---|---|---|

## bc-core Coverage

| Target Type | Targets | With Links | Without Links |
|---|---|---|---|
| config | 7 | 7 | 0 |
| controller | 105 | 105 | 0 |
| module | 59 | 59 | 0 |
| schema | 193 | 193 | 0 |
| script | 573 | 573 | 0 |
| service | 170 | 170 | 0 |

## Top Warning Documents

| Document | Warnings | Categories |
|---|---|---|
| docs/development/documentation-system.md | 2 | stale-doc-root-reference |
| docs/compliance/compliance-overview.md | 1 | stale-doc-root-reference |
| docs/compliance/infosec-and-access-control.md | 1 | stale-doc-root-reference |
| docs/compliance/iso-27001-conformance.md | 1 | stale-doc-root-reference |
| docs/compliance/risk-and-vendor-management.md | 1 | stale-doc-root-reference |
| docs/compliance/soc-2-conformance.md | 1 | stale-doc-root-reference |
| docs/development/build-and-release.md | 1 | stale-doc-root-reference |
| docs/development/decision-and-change-procedure.md | 1 | stale-doc-root-reference |
| docs/development/developer-experience.md | 1 | stale-doc-root-reference |
| docs/development/development-overview.md | 1 | stale-doc-root-reference |
| docs/development/devhub.md | 1 | stale-doc-root-reference |
| docs/development/quality-assurance.md | 1 | stale-doc-root-reference |
| docs/governance/errata/MCF-ERR-001.md | 1 | stale-doc-root-reference |
| docs/implementation/auxiliary-services.md | 1 | stale-doc-root-reference |
| docs/implementation/backend-services.md | 1 | stale-doc-root-reference |
| docs/implementation/frontend-experience.md | 1 | stale-doc-root-reference |
| docs/onboarding/metric-workstream.md | 1 | stale-doc-root-reference |
| docs/operating-model/fiscal-time-and-temporal-gates.md | 1 | stale-doc-root-reference |
| docs/operating-model/mcf-legacy-bridge.md | 1 | stale-doc-root-reference |
| docs/operating-model/metric-management-system.md | 1 | stale-doc-root-reference |
| docs/operating-model/operating-model-overview.md | 1 | stale-doc-root-reference |
| docs/operations/deployment-topology.md | 1 | stale-doc-root-reference |
| docs/operations/security-operations.md | 1 | stale-doc-root-reference |
| docs/operations/support-and-escalation.md | 1 | stale-doc-root-reference |
| docs/overview/platform-overview.md | 1 | stale-doc-root-reference |
| docs/reference/technical-notes/implementation/bcf-mcf-evidence-boundary-operator-decisions-d1-d11.md | 1 | stale-doc-root-reference |
| docs/reference/technical-notes/implementation/bcf-mcf-panel-workbench-alignment-note.md | 1 | stale-doc-root-reference |
| docs/reference/technical-notes/implementation/business-concept-registry-vocabulary-evidence-framework.md | 1 | stale-doc-root-reference |
| docs/reference/technical-notes/implementation/business-context-framework-helper-script-trust-catalog.md | 1 | stale-doc-root-reference |
| docs/reference/technical-notes/implementation/metric-context-framework-candidate-reservoir-and-authority-classification.md | 1 | stale-doc-root-reference |
