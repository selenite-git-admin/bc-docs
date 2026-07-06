# Cutover Replacement Queue

Generated: `2026-07-06T13:46:09.237770+00:00`
Rows: `3066`
CSV: `docs-control\reports\cutover-replacement-queue.csv`

## Safety Boundary

- This is a queue only; it does not edit, rename, delete, or repoint anything.
- Do not execute replacements while active Claude sessions still depend on `bc-docs-v3`.
- Do not rename `bc-docs-v4` to `bc-docs` until the cutover window is explicitly approved.
- Historical provenance rows are intentionally separated from replacement candidates.
- Served documentation copies are excluded; when excluded, rebuild served copies from the cutover docs root instead of hand-editing them.

## Action Summary

| Action | Rows |
|---|---|
| preserve_historical_provenance | 2568 |
| manual_review | 317 |
| replace_after_cutover | 145 |
| defer_claude_ecosystem | 36 |

## Scope Summary

| Scope | Action | Rows |
|---|---|---|
| external_repo | defer_claude_ecosystem | 36 |
| external_repo | manual_review | 308 |
| external_repo | preserve_historical_provenance | 1529 |
| external_repo | replace_after_cutover | 13 |
| internal_v4 | manual_review | 9 |
| internal_v4 | preserve_historical_provenance | 1039 |
| internal_v4 | replace_after_cutover | 132 |

## External Repo Summary

| Repo | Action | Rows |
|---|---|---|
| barecount-devhub | defer_claude_ecosystem | 30 |
| barecount-devhub | manual_review | 6 |
| barecount-devhub | replace_after_cutover | 10 |
| bc-admin | manual_review | 7 |
| bc-admin | replace_after_cutover | 3 |
| bc-ai | manual_review | 3 |
| bc-ai | preserve_historical_provenance | 1 |
| bc-core | defer_claude_ecosystem | 3 |
| bc-core | manual_review | 146 |
| bc-core | preserve_historical_provenance | 764 |
| bc-core-runtime | defer_claude_ecosystem | 3 |
| bc-core-runtime | manual_review | 146 |
| bc-core-runtime | preserve_historical_provenance | 763 |
| bc-qa | preserve_historical_provenance | 1 |

## Ready Replace Candidates

These rows are candidates for direct `bc-docs-v3` -> `bc-docs` replacement during the approved cutover window.

| Scope | Repo | Path | Line | Token | Replacement | Reason |
|---|---|---|---|---|---|---|
| external_repo | barecount-devhub | barecount-devhub/scripts/_bcf-coverage-compiler.mjs | 5 | bc-docs-v3 | bc-docs | DevHub operational docs-root reference; repoint during the approved cutover window. |
| external_repo | barecount-devhub | barecount-devhub/scripts/_bcf-coverage-compiler.mjs | 36 | C:/MyProjects/bc-docs-v3 | C:/MyProjects/bc-docs | DevHub operational docs-root reference; repoint during the approved cutover window. |
| external_repo | barecount-devhub | barecount-devhub/scripts/_bcf-coverage-compiler.mjs | 39 | bc-docs-v3 | bc-docs | DevHub operational docs-root reference; repoint during the approved cutover window. |
| external_repo | barecount-devhub | barecount-devhub/scripts/_bcf-coverage-compiler.mjs | 136 | bc-docs-v3 | bc-docs | DevHub operational docs-root reference; repoint during the approved cutover window. |
| external_repo | barecount-devhub | barecount-devhub/src/lib/decision-code-reconcile.js | 16 | bc-docs-v3 | bc-docs | DevHub operational docs-root reference; repoint during the approved cutover window. |
| external_repo | barecount-devhub | barecount-devhub/src/lib/decision-code-reconcile.js | 23 | C:/MyProjects/bc-docs-v3 | C:/MyProjects/bc-docs | DevHub operational docs-root reference; repoint during the approved cutover window. |
| external_repo | barecount-devhub | barecount-devhub/src/lib/doc-scanner.js | 23 | C:/MyProjects/bc-docs-v3 | C:/MyProjects/bc-docs | DevHub operational docs-root reference; repoint during the approved cutover window. |
| external_repo | barecount-devhub | barecount-devhub/src/lib/docs-registry.js | 13 | C:/MyProjects/bc-docs-v3 | C:/MyProjects/bc-docs | DevHub operational docs-root reference; repoint during the approved cutover window. |
| external_repo | barecount-devhub | barecount-devhub/src/lib/qa-audit.js | 63 | C:/MyProjects/bc-docs-v3 | C:/MyProjects/bc-docs | DevHub operational docs-root reference; repoint during the approved cutover window. |
| external_repo | barecount-devhub | barecount-devhub/src/routes/decisions.js | 125 | bc-docs-v3 | bc-docs | DevHub operational docs-root reference; repoint during the approved cutover window. |
| external_repo | bc-admin | bc-admin/README.md | 9 | C:/MyProjects/bc-docs-v3 | C:/MyProjects/bc-docs | Operational docs-root pointer; candidate for direct repoint during cutover. |
| external_repo | bc-admin | bc-admin/scripts/sync-docs.js | 37 | C:/MyProjects/bc-docs-v3 | C:/MyProjects/bc-docs | Operational docs-root pointer; candidate for direct repoint during cutover. |
| external_repo | bc-admin | bc-admin/scripts/sync-docs.js | 338 | bc-docs-v3 | bc-docs | Operational docs-root pointer; candidate for direct repoint during cutover. |
| internal_v4 | bc-docs-v4 | docs/compliance/compliance-overview.md | 198 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/compliance-overview.md | 199 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/infosec-and-access-control.md | 18 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/infosec-and-access-control.md | 126 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/infosec-and-access-control.md | 238 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/iso-27001-conformance.md | 28 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/iso-27001-conformance.md | 74 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/iso-27001-conformance.md | 170 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/iso-27001-conformance.md | 182 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/iso-27001-conformance.md | 203 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/risk-and-vendor-management.md | 17 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/risk-and-vendor-management.md | 183 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/soc-2-conformance.md | 23 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/compliance/soc-2-conformance.md | 233 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/build-and-release.md | 45 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/build-and-release.md | 65 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/build-and-release.md | 80 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/build-and-release.md | 144 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/build-and-release.md | 203 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/decision-and-change-procedure.md | 19 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/decision-and-change-procedure.md | 29 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/decision-and-change-procedure.md | 37 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/decision-and-change-procedure.md | 46 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/decision-and-change-procedure.md | 88 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/decision-and-change-procedure.md | 94 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/decision-and-change-procedure.md | 96 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/decision-and-change-procedure.md | 171 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/decision-and-change-procedure.md | 237 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/developer-experience.md | 18 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/developer-experience.md | 18 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/developer-experience.md | 70 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/developer-experience.md | 210 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/developer-experience.md | 248 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/developer-experience.md | 254 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/developer-experience.md | 264 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/developer-experience.md | 280 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/developer-experience.md | 283 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/development-overview.md | 23 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/development-overview.md | 71 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/development-overview.md | 134 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/development-overview.md | 160 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/development-overview.md | 160 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/development-overview.md | 191 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/development-overview.md | 196 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/development-overview.md | 197 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/devhub.md | 18 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/devhub.md | 18 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/devhub.md | 36 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/devhub.md | 133 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/devhub.md | 138 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/devhub.md | 211 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/devhub.md | 211 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/devhub.md | 229 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 14 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 28 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 34 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 36 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 40 | C:\MyProjects\bc-docs-v3 | C:\MyProjects\bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 50 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 50 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 99 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 103 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 110 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 116 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 128 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 132 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 136 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 147 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 147 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 159 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 163 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 169 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 173 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 177 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 190 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 196 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 198 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 199 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 234 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 236 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 260 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 264 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 265 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/documentation-system.md | 266 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/development/quality-assurance.md | 153 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/auxiliary-services.md | 89 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/backend-services.md | 142 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/backend-services.md | 149 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/backend-services.md | 151 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/backend-services.md | 159 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/backend-services.md | 162 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/backend-services.md | 171 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/backend-services.md | 178 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/backend-services.md | 178 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/backend-services.md | 245 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/backend-services.md | 283 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/backend-services.md | 305 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/implementation/frontend-experience.md | 155 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 9 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 10 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 11 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 16 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 17 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 18 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 33 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 34 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 304 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 356 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 474 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 474 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 490 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 491 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 492 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 493 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 494 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 495 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 496 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 497 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/onboarding/metric-workstream.md | 498 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/operating-model/metric-management-system.md | 528 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/operating-model/operating-model-overview.md | 155 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/operating-model/operating-model-overview.md | 157 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/operations/deployment-topology.md | 67 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/operations/security-operations.md | 102 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/operations/support-and-escalation.md | 199 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/overview/platform-overview.md | 22 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/overview/platform-overview.md | 152 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/overview/platform-overview.md | 152 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/overview/platform-overview.md | 182 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/overview/platform-overview.md | 211 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/overview/platform-overview.md | 215 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |
| internal_v4 | bc-docs-v4 | docs/overview/platform-overview.md | 216 | bc-docs-v3 | bc-docs | Current reader-visible v4 document; repoint when bc-docs-v4 is renamed to bc-docs. |

## Claude Ecosystem Hold

| Repo | Path | Line | Token | Replacement |
|---|---|---|---|---|
| barecount-devhub | barecount-devhub/.claude/desktop-prep-output-c2-2026-06-25/pre-filter-table.md | 154 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 5 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 7 | C:\MyProjects\bc-docs-v3 | C:\MyProjects\bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 9 | C:\MyProjects\bc-docs-v3 | C:\MyProjects\bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 76 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 140 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 141 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 142 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 143 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 144 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 145 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 149 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 149 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 153 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 162 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 248 | C:\MyProjects\bc-docs-v3 | C:\MyProjects\bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 270 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 426 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 426 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 449 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 451 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 453 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 469 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 479 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 479 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 495 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 519 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 519 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 523 | bc-docs-v3 | bc-docs |
| barecount-devhub | barecount-devhub/CLAUDE.md | 527 | bc-docs-v3 | bc-docs |
| bc-core | bc-core/.claude/plans/d369-handoff-2026-04-28.md | 38 | bc-docs-v3 | bc-docs |
| bc-core | bc-core/.claude/plans/d369-handoff-2026-04-28.md | 111 | bc-docs-v3 | bc-docs |
| bc-core | bc-core/.claude/plans/d369-handoff-2026-04-28.md | 190 | bc-docs-v3 | bc-docs |
| bc-core-runtime | bc-core-runtime/.claude/plans/d369-handoff-2026-04-28.md | 38 | bc-docs-v3 | bc-docs |
| bc-core-runtime | bc-core-runtime/.claude/plans/d369-handoff-2026-04-28.md | 111 | bc-docs-v3 | bc-docs |
| bc-core-runtime | bc-core-runtime/.claude/plans/d369-handoff-2026-04-28.md | 190 | bc-docs-v3 | bc-docs |

## Manual Review Samples

| Scope | Repo | Path | Line | Reason | Excerpt |
|---|---|---|---|---|---|
| external_repo | barecount-devhub | barecount-devhub/src/lib/decision-code-reconcile.js | 4 | Code/config comment or reference; review whether it is live guidance or historical provenance. | * Scans bc-docs-v3/docs/adrs/ADR-*.md for decision_code: frontmatter, |
| external_repo | barecount-devhub | barecount-devhub/src/lib/doc-scanner.js | 4 | Code/config comment or reference; review whether it is live guidance or historical provenance. | * Walks bc-docs-v3/docs/, parses frontmatter, derives type+domain from path, |
| external_repo | barecount-devhub | barecount-devhub/src/lib/doc-scanner.js | 7 | Code/config comment or reference; review whether it is live guidance or historical provenance. | * Ground truth: bc-docs-v3 filesystem + frontmatter |
| external_repo | barecount-devhub | barecount-devhub/src/lib/docs-registry.js | 5 | Code/config comment or reference; review whether it is live guidance or historical provenance. | * `bc-docs-v3/docs/adrs/`. The legacy `docs.registry.json` file indirection |
| external_repo | barecount-devhub | barecount-devhub/src/lib/qa-audit.js | 56 | Code/config comment or reference; review whether it is live guidance or historical provenance. | * Write markdown audit report to bc-docs-v3 (DEC-3395bc). |
| external_repo | barecount-devhub | barecount-devhub/src/mcp-server.js | 2491 | Code/config comment or reference; review whether it is live guidance or historical provenance. | // reference is in bc-docs-v3/docs/development/metric-readiness-toolkit.md. |
| external_repo | bc-admin | bc-admin/.gitignore | 9 | Unclassified external reference; review before editing. | # Generated docs (synced from bc-docs-v3 via scripts/sync-docs.js) |
| external_repo | bc-admin | bc-admin/README.md | 8 | Code/config comment or reference; review whether it is live guidance or historical provenance. | - **A local `bc-docs-v3` checkout** — `npm run dev` and `npm run build` run `scripts/sync-docs.js` on `predev` / `prebuild`. It copies `bc-docs-v3` content into `bc-core/private-docs/`, which bc-core serves to the in-... |
| external_repo | bc-admin | bc-admin/README.md | 8 | Code/config comment or reference; review whether it is live guidance or historical provenance. | - **A local `bc-docs-v3` checkout** — `npm run dev` and `npm run build` run `scripts/sync-docs.js` on `predev` / `prebuild`. It copies `bc-docs-v3` content into `bc-core/private-docs/`, which bc-core serves to the in-... |
| external_repo | bc-admin | bc-admin/scripts/sync-docs.js | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | * sync-docs — copy bc-docs-v3 content into bc-core/private-docs/ |
| external_repo | bc-admin | bc-admin/scripts/sync-docs.js | 5 | Code/config comment or reference; review whether it is live guidance or historical provenance. | * Reads markdown files from bc-docs-v3 (outline.md and docs/), copies |
| external_repo | bc-admin | bc-admin/scripts/sync-docs.js | 9 | Code/config comment or reference; review whether it is live guidance or historical provenance. | * Source structure (bc-docs-v3): |
| external_repo | bc-admin | bc-admin/scripts/sync-docs.js | 317 | Code/config comment or reference; review whether it is live guidance or historical provenance. | * Validate the bc-docs-v3 source BEFORE any destructive write to SYNC_TARGET. |
| external_repo | bc-ai | bc-ai/app/agents/registry_authoring.py | 200 | Code/config comment or reference; review whether it is live guidance or historical provenance. | # bc-docs-v3 bcf-oagis-pass-1-c1-closure-checkpoint-2026-06-25.md Part B. |
| external_repo | bc-ai | bc-ai/tests/test_registry_authoring_panel.py | 2213 | Code/config comment or reference; review whether it is live guidance or historical provenance. | would reintroduce the truncation. Diagnostic: bc-docs-v3 |
| external_repo | bc-ai | bc-ai/tests/test_registry_authoring_panel.py | 2277 | Code/config comment or reference; review whether it is live guidance or historical provenance. | (bc-docs-v3 1ca8ead) where the Moderator emitted f3_operation |
| external_repo | bc-core | bc-core/docker/redesign/06-mcf-lifecycle-certification.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 3983530; rewritten post-M3-cert-amendment to target |
| external_repo | bc-core | bc-core/docker/redesign/07-mcf-formula-ast-storage-rollback.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 62ec707 §13.2.1 + §17.1 — L-3 guard clarification) |
| external_repo | bc-core | bc-core/docker/redesign/07-mcf-formula-ast-storage.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 62ec707 — Formula AST + Hash/Signature Authority) |
| external_repo | bc-core | bc-core/docker/redesign/08-mcf-panel-substrate-rollback.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 00435c0 §14.4) |
| external_repo | bc-core | bc-core/docker/redesign/08-mcf-panel-substrate.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 00435c0 — Metric Authoring Panel substrate) |
| external_repo | bc-core | bc-core/docker/redesign/09-mcf-fixture-substrate-rollback.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 620e11d §12.4) |
| external_repo | bc-core | bc-core/docker/redesign/09-mcf-fixture-substrate.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 620e11d — Self-Verification Fixture Substrate) |
| external_repo | bc-core | bc-core/docker/redesign/10-mcf-self-verification-result-rollback.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 ea8b708 §15.4) |
| external_repo | bc-core | bc-core/docker/redesign/10-mcf-self-verification-result.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 ea8b708 — Deterministic Verifier Service + Result Substrate) |
| external_repo | bc-core | bc-core/docker/redesign/11-mcf-reservoir-ingestion-rollback.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 42f702b §14.4) |
| external_repo | bc-core | bc-core/docker/redesign/11-mcf-reservoir-ingestion.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 42f702b — Reservoir Ingestion + Intake Queue Substrate) |
| external_repo | bc-core | bc-core/docker/redesign/14-mcf-role-grant-audit.sql | 9 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- Impl: bc-docs-v3/docs/implementation/mcf-role-grant-service-implementation-dbcp.md |
| external_repo | bc-core | bc-core/docker/redesign/14R-mcf-role-grant-audit-rollback.sql | 7 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- Impl: bc-docs-v3/docs/implementation/mcf-role-grant-service-implementation-dbcp.md (ec7053d) |
| external_repo | bc-core | bc-core/docker/redesign/15-mcf-seed-reservoir-rollback.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 docs/implementation/mcf-gate0-seed-reservoir-dbcp.md §7) |
| external_repo | bc-core | bc-core/docker/redesign/15-mcf-seed-reservoir.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 docs/implementation/mcf-gate0-seed-reservoir-dbcp.md) |
| external_repo | bc-core | bc-core/docker/redesign/15-mcf-seed-reservoir.sql | 7 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- bc-docs-v3/docs/adrs/ADR-3f093f.md (DEC-3f093f / D426) — canonicality boundary |
| external_repo | bc-core | bc-core/docker/redesign/15-mcf-seed-reservoir.sql | 8 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) — foundational MCF |
| external_repo | bc-core | bc-core/docker/redesign/16-mcf-seed-metric-status.sql | 3 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (per DBCP bc-docs-v3 docs/implementation/mcf-gate0-seed-reservoir-dbcp.md |
| external_repo | bc-core | bc-core/docker/redesign/20-mcf-secondary-metric-dag.sql | 27 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- bc-docs-v3/docs/implementation/metric-context-framework-secondary-metric-dag-substrate-dbcp-2026-06-30.md §3.1/§6.1. |
| external_repo | bc-core | bc-core/docker/redesign/21-mcf-pe-mc-13-15-vocabulary.sql | 21 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- bc-docs-v3/docs/implementation/metric-context-framework-secondary-metric-dag-substrate-dbcp-2026-06-30.md §4.6. |
| external_repo | bc-core | bc-core/docker/redesign/22-mcf-selection-rule-prior-period-end.sql | 17 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- bc-docs-v3/docs/implementation/metric-context-framework-secondary-metric-dag-substrate-dbcp-2026-06-30.md §4.2. |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260515-d407-dbcp-1m-canonical-field-provenance.sql | 5 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- Parity: DBCP-1l on business_field (applied 2026-05-12, bc-docs-v3@a41eb26) |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-c-remove-credit-type-code-cc-mappings.sql | 4 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- Plan: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md §11a.1 |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-c-remove-credit-type-code-cc-mappings.sql | 5 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- Verification: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-dbcp-1q-c-credit-type-code-mapping-removal-verification-plan.md |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-d-demote-no-cc-type-incoherence.sql | 5 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- Plan: bc-docs-v3/docs/onboarding/metric-work-records/_cross/ |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-d-demote-no-cc-type-incoherence.sql | 7 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- §11b lock: bc-docs-v3@2d8a544 |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-d-demote-no-cc-type-incoherence.sql | 56 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- bc-docs-v3/docs/onboarding/metric-work-records/_cross/ |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-e-remove-a1-mismatch-cc-mappings.sql | 4 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- Plan: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-e-remove-a1-mismatch-cc-mappings.sql | 5 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- Verification: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-dbcp-1q-e-a1-mismatch-cc-mapping-removal-verification-plan.md |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-g-add-admit-from-correction-required-action.sql | 4 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- Plan: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-g-add-admit-from-correction-required-action.sql | 6 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- Verification: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-dbcp-1q-g-admit-from-correction-required-action-verification-plan.md |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-g-add-admit-from-correction-required-action.sql | 22 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (designed in bc-docs-v3@2c457a8). The endpoint accepts a row in |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d409-dbcp-1q-i-add-admit-from-candidate-import-action.sql | 6 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- Verification: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-dbcp-1q-i-admit-from-candidate-import-action-verification-plan.md |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d409-dbcp-1q-i-add-admit-from-candidate-import-action.sql | 21 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (designed in bc-docs-v3@06aa817). The endpoint accepts a row in |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260521-f2-concept-registry-schema.sql | 6 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (bc-docs-v3 docs/implementation/business-concept-registry-f1-forward-design.md) |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260521-f2-concept-registry-schema.sql | 8 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (bc-docs-v3 docs/implementation/business-concept-registry-f2-schema-dbcp.md, |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260521-f3-supersession-proposal-provenance.sql | 6 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (bc-docs-v3 docs/implementation/business-concept-registry-f3-authoring-service-design.md) |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260521-f3-supersession-proposal-provenance.sql | 8 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (bc-docs-v3 docs/implementation/business-concept-registry-f3-dbcp.md, |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260521-phase-a-bucket-1-governance-scope-alignment.sql | 6 | Code/config comment or reference; review whether it is live guidance or historical provenance. | -- (bc-docs-v3 business-context-framework-phase-a-alignment-dbcp- |
| external_repo | bc-core | bc-core/scripts/audit-bf-admission-d408-calibrated.mjs | 49 | Unclassified external reference; review before editing. | const ADR_PATH = 'bc-docs-v3/docs/adrs/ADR-1ce490.md'; |
| external_repo | bc-core | bc-core/scripts/audit-bf-admission-d408.mjs | 46 | Unclassified external reference; review before editing. | const ADR_PATH = 'bc-docs-v3/docs/adrs/ADR-1ce490.md'; |
| external_repo | bc-core | bc-core/scripts/author-arpi-oc-v2-slice.mjs | 4 | Unclassified external reference; review before editing. | * Locked proposal: bc-docs-v3/docs/implementation/d431-arpi-oc-v2-slice-proposal-2026-06-08.md |
| external_repo | bc-core | bc-core/scripts/build-d408-a1-asset-cf-binding-audit-packet.mjs | 8 | Unclassified external reference; review before editing. | * Plan: bc-docs-v3/.../2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md |
| external_repo | bc-core | bc-core/scripts/build-d408-a1-asset-cf-binding-audit-packet.mjs | 43 | Unclassified external reference; review before editing. | const PLAN_PATH = 'bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md'; |
| external_repo | bc-core | bc-core/scripts/c2a-pe-mc-11-vocabulary.mjs | 6 | Unclassified external reference; review before editing. | * ADR : bc-docs-v3/docs/adrs/ADR-1002c9.md (DEC-1002c9 / D439, decided) |
| external_repo | bc-core | bc-core/scripts/d408-demote-correction-required-no-cc-1q-d.mjs | 7 | Unclassified external reference; review before editing. | * Plan: bc-docs-v3/docs/onboarding/metric-work-records/_cross/ |
| external_repo | bc-core | bc-core/scripts/d408-demote-correction-required-no-cc-1q-d.mjs | 9 | Unclassified external reference; review before editing. | * §11b sub-cohort lock: bc-docs-v3@2d8a544 |
| external_repo | bc-core | bc-core/scripts/d408-remove-a1-mismatch-cc-mappings-1q-e.mjs | 7 | Unclassified external reference; review before editing. | * Plan: bc-docs-v3/.../2026-05-17-d408-correction-required-bf-cleanup-plan-DEC-1ce490.md |
| external_repo | bc-core | bc-core/scripts/d429-step1-seed-v2-meta-schemas.mjs | 5 | Unclassified external reference; review before editing. | * DBCP (locked): bc-docs-v3/docs/implementation/d430-d431-v2-meta-schema-seed-dbcp-2026-06-08.md |
| external_repo | bc-core | bc-core/scripts/d467-pe-mc-13-15-vocabulary.mjs | 6 | Unclassified external reference; review before editing. | * ADR : bc-docs-v3/docs/adrs/ADR-0f3e57.md (DEC-0f3e57 / D467, decided) |
| external_repo | bc-core | bc-core/scripts/d467-secondary-metric-dag-substrate.mjs | 6 | Unclassified external reference; review before editing. | * ADR : bc-docs-v3/docs/adrs/ADR-0f3e57.md (DEC-0f3e57 / D467, decided) |
| external_repo | bc-core | bc-core/scripts/d467-secondary-metric-dag-substrate.mjs | 7 | Unclassified external reference; review before editing. | * DBCP : bc-docs-v3/docs/implementation/metric-context-framework-secondary-metric-dag-substrate-dbcp-2026-06-30.md §3.1/§6.1 |
| external_repo | bc-core | bc-core/scripts/f1-a2-pe-mc-12-vocabulary.mjs | 6 | Unclassified external reference; review before editing. | * ADR : bc-docs-v3/docs/adrs/ADR-6b35e0.md (DEC-6b35e0 / D441, decided) |
| external_repo | bc-core | bc-core/scripts/mcf-m10-dry-run.mjs | 45 | Unclassified external reference; review before editing. | 'bc-docs-v3/docs/implementation/metric-context-framework-m10-self-verification-result-dbcp.md (ea8b708)'; |
| external_repo | bc-core | bc-core/scripts/mcf-m10-post-apply-verification.mjs | 31 | Unclassified external reference; review before editing. | const DBCP_REF = 'bc-docs-v3/docs/implementation/metric-context-framework-m10-self-verification-result-dbcp.md (ea8b708)'; |
| external_repo | bc-core | bc-core/scripts/mcf-m11-dry-run.mjs | 44 | Unclassified external reference; review before editing. | 'bc-docs-v3/docs/implementation/metric-context-framework-m11-reservoir-ingestion-dbcp.md (42f702b)'; |
| external_repo | bc-core | bc-core/scripts/mcf-m11-first-real-intake.mjs | 329 | Unclassified external reference; review before editing. | cond_1_dbcp_merged: 'DONE (bc-docs-v3 55bc4759)', |
| external_repo | bc-core | bc-core/scripts/mcf-m11-post-apply-verification.mjs | 29 | Unclassified external reference; review before editing. | const DBCP_REF = 'bc-docs-v3/docs/implementation/metric-context-framework-m11-reservoir-ingestion-dbcp.md (42f702b)'; |
| external_repo | bc-core | bc-core/scripts/mcf-m12-5-dry-run.mjs | 49 | Unclassified external reference; review before editing. | 'bc-docs-v3/docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md (52fb8bc)'; |
| external_repo | bc-core | bc-core/scripts/mcf-m12-5-dry-run.mjs | 264 | Unclassified external reference; review before editing. | const bcDocsV3Path = path.resolve(REPO_ROOT, '..', 'bc-docs-v3'); |
| external_repo | bc-core | bc-core/scripts/mcf-m12-5-dry-run.mjs | 269 | Unclassified external reference; review before editing. | { note: 'bc-docs-v3 sibling not found at expected path; skipping (advisory only)' }, |
| external_repo | bc-core | bc-core/scripts/mcf-m12-5-post-apply-verification.mjs | 42 | Unclassified external reference; review before editing. | 'bc-docs-v3/docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md (52fb8bc)'; |
| external_repo | bc-core | bc-core/scripts/mcf-m12-5-post-apply-verification.mjs | 440 | Unclassified external reference; review before editing. | const bcDocsV3Path = path.resolve(REPO_ROOT, '..', 'bc-docs-v3'); |
| external_repo | bc-core | bc-core/scripts/mcf-m12-5-post-apply-verification.mjs | 441 | Unclassified external reference; review before editing. | const bcDocsV3Sha = fs.existsSync(bcDocsV3Path) ? captureGitSha(bcDocsV3Path) : { ok: false, error: 'bc-docs-v3 sibling not found' }; |

Manual review table truncated to 80 rows; full queue is in `docs-control\reports\cutover-replacement-queue.csv`.

## Historical Provenance Samples

| Scope | Repo | Path | Line | Reason | Excerpt |
|---|---|---|---|---|---|
| external_repo | bc-ai | bc-ai/ARCHIVED.md | 20 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | - ADR: `bc-docs-v3/docs/adrs/ADR-ffee4e.md` (D483; supersedes DEC-14fb98) |
| external_repo | bc-core | bc-core/docker/redesign/02-platform-tables.sql | 9 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- superseded by bc-docs-v3 per D373; the DBML was not carried over). |
| external_repo | bc-core | bc-core/docker/redesign/04-mcf-substrate.sql | 5 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/04-mcf-substrate.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Design: bc-docs-v3/docs/implementation/metric-context-framework-m2-identity-substrate-dbcp.md |
| external_repo | bc-core | bc-core/docker/redesign/04-mcf-substrate.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Build plan: bc-docs-v3/docs/implementation/metric-context-framework-build-plan.md (40a9adc) |
| external_repo | bc-core | bc-core/docker/redesign/04-mcf-substrate.sql | 8 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Preflight: bc-docs-v3/docs/implementation/metric-context-framework-m2-preflight-decisions.md |
| external_repo | bc-core | bc-core/docker/redesign/04-mcf-substrate.sql | 9 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Revision: bc-docs-v3 commit dda900e — nullable hash columns + DDL COMMENT discipline |
| external_repo | bc-core | bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql | 5 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m3-lifecycle-substrate-dbcp.md |
| external_repo | bc-core | bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql | 8 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Preflight: bc-docs-v3/docs/implementation/metric-context-framework-m3-lifecycle-substrate-preflight.md (9e472cb) |
| external_repo | bc-core | bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql | 9 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Build plan: bc-docs-v3/docs/implementation/metric-context-framework-build-plan.md §4.2 Gate M3 |
| external_repo | bc-core | bc-core/docker/redesign/05a-mcf-cert-amendment-rollback.sql | 4 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Authority: bc-docs-v3/docs/implementation/metric-context-framework-m3-certification-target-amendment-dbcp.md (06d369c) §10 |
| external_repo | bc-core | bc-core/docker/redesign/05a-mcf-cert-amendment.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/05a-mcf-cert-amendment.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Preflight: bc-docs-v3/docs/implementation/metric-context-framework-m3-m4-cert-substrate-correction-preflight.md (637e667) |
| external_repo | bc-core | bc-core/docker/redesign/05a-mcf-cert-amendment.sql | 8 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m3-certification-target-amendment-dbcp.md (06d369c) |
| external_repo | bc-core | bc-core/docker/redesign/06-mcf-lifecycle-certification-rollback.sql | 4 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Authority: bc-docs-v3/docs/implementation/metric-context-framework-m4-lifecycle-certification-dbcp.md (3983530) §12.5 |
| external_repo | bc-core | bc-core/docker/redesign/06-mcf-lifecycle-certification.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/06-mcf-lifecycle-certification.sql | 8 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Preflight: bc-docs-v3/docs/implementation/metric-context-framework-m4-lifecycle-certification-preflight.md (dd54f44) |
| external_repo | bc-core | bc-core/docker/redesign/06-mcf-lifecycle-certification.sql | 9 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m4-lifecycle-certification-dbcp.md (3983530) |
| external_repo | bc-core | bc-core/docker/redesign/06-mcf-lifecycle-certification.sql | 10 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Correction preflight: bc-docs-v3/docs/implementation/metric-context-framework-m3-m4-cert-substrate-correction-preflight.md (637e667) |
| external_repo | bc-core | bc-core/docker/redesign/06-mcf-lifecycle-certification.sql | 11 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- M3 cert-amendment closeout: bc-docs-v3/docs/implementation/mcf-m3-cert-amendment-apply-closeout.md (60efd9d) |
| external_repo | bc-core | bc-core/docker/redesign/07-mcf-formula-ast-storage-rollback.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/07-mcf-formula-ast-storage-rollback.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m7-m8-formula-hash-authority-dbcp.md (62ec707) §17.1 |
| external_repo | bc-core | bc-core/docker/redesign/07-mcf-formula-ast-storage.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/07-mcf-formula-ast-storage.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Preflight: bc-docs-v3/docs/implementation/metric-context-framework-m7-m8-formula-hash-authority-preflight.md (454bfeb) |
| external_repo | bc-core | bc-core/docker/redesign/07-mcf-formula-ast-storage.sql | 8 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m7-m8-formula-hash-authority-dbcp.md (62ec707) |
| external_repo | bc-core | bc-core/docker/redesign/08-mcf-panel-substrate-rollback.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/08-mcf-panel-substrate-rollback.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m5-panel-substrate-dbcp.md (00435c0) §14.4 |
| external_repo | bc-core | bc-core/docker/redesign/08-mcf-panel-substrate.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/08-mcf-panel-substrate.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Preflight: bc-docs-v3/docs/implementation/metric-context-framework-m5-panel-substrate-preflight.md (6e46d77) |
| external_repo | bc-core | bc-core/docker/redesign/08-mcf-panel-substrate.sql | 8 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m5-panel-substrate-dbcp.md (00435c0) |
| external_repo | bc-core | bc-core/docker/redesign/09-mcf-fixture-substrate-rollback.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/09-mcf-fixture-substrate-rollback.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m9-fixture-substrate-dbcp.md (620e11d) §12.4 |
| external_repo | bc-core | bc-core/docker/redesign/09-mcf-fixture-substrate.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/09-mcf-fixture-substrate.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Preflight: bc-docs-v3/docs/implementation/metric-context-framework-m9-fixture-substrate-preflight.md (686afc3) |
| external_repo | bc-core | bc-core/docker/redesign/09-mcf-fixture-substrate.sql | 8 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m9-fixture-substrate-dbcp.md (620e11d) |
| external_repo | bc-core | bc-core/docker/redesign/10-mcf-self-verification-result-rollback.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/10-mcf-self-verification-result-rollback.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m10-self-verification-result-dbcp.md (ea8b708) §15.4 |
| external_repo | bc-core | bc-core/docker/redesign/10-mcf-self-verification-result.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/10-mcf-self-verification-result.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Preflight: bc-docs-v3/docs/implementation/metric-context-framework-m10-self-verification-result-preflight.md (60930fa) |
| external_repo | bc-core | bc-core/docker/redesign/10-mcf-self-verification-result.sql | 8 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m10-self-verification-result-dbcp.md (ea8b708) |
| external_repo | bc-core | bc-core/docker/redesign/11-mcf-reservoir-ingestion-rollback.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/11-mcf-reservoir-ingestion-rollback.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m11-reservoir-ingestion-dbcp.md (42f702b) §14.4 |
| external_repo | bc-core | bc-core/docker/redesign/11-mcf-reservoir-ingestion.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/11-mcf-reservoir-ingestion.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Preflight: bc-docs-v3/docs/implementation/metric-context-framework-m11-reservoir-ingestion-preflight.md (79142b6) |
| external_repo | bc-core | bc-core/docker/redesign/11-mcf-reservoir-ingestion.sql | 8 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m11-reservoir-ingestion-dbcp.md (42f702b) |
| external_repo | bc-core | bc-core/docker/redesign/12-mcf-m12-5-mc-name-unique-index-rollback.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/12-mcf-m12-5-mc-name-unique-index-rollback.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md (52fb8bc) §7.2 |
| external_repo | bc-core | bc-core/docker/redesign/12-mcf-m12-5-mc-name-unique-index.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/12-mcf-m12-5-mc-name-unique-index.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Preflight: bc-docs-v3/docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-preflight.md (57e828b) |
| external_repo | bc-core | bc-core/docker/redesign/12-mcf-m12-5-mc-name-unique-index.sql | 8 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md (52fb8bc) §7 |
| external_repo | bc-core | bc-core/docker/redesign/13-mcf-m13-pe-mc-uniqueness-index.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/13-mcf-m13-pe-mc-uniqueness-index.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m13-pe-mc-evaluator-dbcp.md |
| external_repo | bc-core | bc-core/docker/redesign/13R-mcf-m13-pe-mc-uniqueness-index-rollback.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/13R-mcf-m13-pe-mc-uniqueness-index-rollback.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m13-pe-mc-evaluator-dbcp.md |
| external_repo | bc-core | bc-core/docker/redesign/14-mcf-m13-pe-mc-chain-fingerprint-index.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/14-mcf-m13-pe-mc-chain-fingerprint-index.sql | 8 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/metric-context-framework-m13-pe-mc-evaluator-dbcp.md |
| external_repo | bc-core | bc-core/docker/redesign/14-mcf-role-grant-audit.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-c3e57f.md (DEC-c3e57f / D422) |
| external_repo | bc-core | bc-core/docker/redesign/14-mcf-role-grant-audit.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Design: bc-docs-v3/docs/implementation/mcf-role-grant-service-dbcp.md |
| external_repo | bc-core | bc-core/docker/redesign/14-mcf-role-grant-audit.sql | 8 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- (bc-docs-v3 main d60a742, PR #34 — D-5 audit row shape) |
| external_repo | bc-core | bc-core/docker/redesign/14-mcf-role-grant-audit.sql | 10 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- (bc-docs-v3 main ec7053d, PR #35 — I-1 + §4 DDL + I-2 DB-change protocol) |
| external_repo | bc-core | bc-core/docker/redesign/14R-mcf-role-grant-audit-rollback.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Design: bc-docs-v3/docs/implementation/mcf-role-grant-service-dbcp.md (d60a742) |
| external_repo | bc-core | bc-core/docker/redesign/15-mcf-m13-pe-mc-evidence-fingerprint-index.sql | 5 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Design: bc-docs-v3/docs/implementation/mms-publication-review-evidence-fingerprint-design-2026-06-23.md |
| external_repo | bc-core | bc-core/docker/redesign/15-mcf-m13-pe-mc-evidence-fingerprint-index.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-2411e4.md (DEC-2411e4 / D450) — amendment §4 |
| external_repo | bc-core | bc-core/docker/redesign/15-mcf-seed-reservoir.sql | 6 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-61f7c8.md (DEC-61f7c8 / D428) — store amendment |
| external_repo | bc-core | bc-core/docker/redesign/15-mcf-seed-reservoir.sql | 9 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP: bc-docs-v3/docs/implementation/mcf-gate0-seed-reservoir-dbcp.md §1 |
| external_repo | bc-core | bc-core/docker/redesign/16-mcf-seed-metric-status.sql | 7 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-61f7c8.md (DEC-61f7c8 / D428) |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-a-bf-catalog-admission-state.sql | 3 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Authority: DEC-1ce490 (D408) — bc-docs-v3/docs/adrs/ADR-1ce490.md |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-a-bf-catalog-admission-state.sql | 4 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Design: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-b-bf-catalog-demotions.sql | 4 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-1ce490.md |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260516-d408-dbcp-1q-b-bf-catalog-demotions.sql | 5 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- DBCP design: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-d-demote-no-cc-type-incoherence.sql | 4 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-1ce490.md |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-g-add-admit-from-correction-required-action.sql | 5 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Design: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-admit-from-correction-required-design-DEC-1ce490.md (bc-docs-v3@2c457a8) |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d408-dbcp-1q-g-add-admit-from-correction-required-action.sql | 5 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Design: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d408-admit-from-correction-required-design-DEC-1ce490.md (bc-docs-v3@2c457a8) |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d409-dbcp-1q-i-add-admit-from-candidate-import-action.sql | 4 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Design: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-admit-from-candidate-import-design-DEC-b8ec00.md (bc-docs-v3@06aa817) |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260517-d409-dbcp-1q-i-add-admit-from-candidate-import-action.sql | 4 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Design: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-admit-from-candidate-import-design-DEC-b8ec00.md (bc-docs-v3@06aa817) |
| external_repo | bc-core | bc-core/docker/redesign/migrations/20260624-dec-ec341c-panel-output-record-admission-scope.sql | 5 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-ec341c.md |
| external_repo | bc-core | bc-core/docker/redesign/migrations/dec-17112b-reader-observation-binding.sql | 2 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- Platform DB (bc_platform_dev). Authority: bc-docs-v3/docs/adrs/ADR-17112b.md. |
| external_repo | bc-core | bc-core/docker/redesign/migrations/dec-31c212-mcf-mcv-classification-master-fk.sql | 2 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | -- ADR: bc-docs-v3/docs/adrs/ADR-31c212.md |
| external_repo | bc-core | bc-core/scripts/archive/audit-output-2026-05-06/bcf-authoring-test-row-cleanup-dry-run-2026-05-28T15-10-48-199Z.summary.md | 4 | Historical code/comment provenance; keep unless a maintainer confirms it is an operational pointer. | **Authority:** bc-docs-v3/docs/implementation/bcf-authoring-test-row-cleanup-dbcp.md |

Historical provenance table truncated to 80 rows; full queue is in `docs-control\reports\cutover-replacement-queue.csv`.
