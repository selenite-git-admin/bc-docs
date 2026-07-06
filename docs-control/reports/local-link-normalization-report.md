# Local Link Normalization Report

Generated: `2026-07-06T08:47:36.353738+00:00`
Dry run: `False`
Replacements: `33`
Files touched: `8`
Missing registered files skipped: `0`

## Reasons

| Reason | Replacements |
|---|---|
| absolute-local-link | 14 |
| link-escapes-docs-root | 19 |

## Files

| File | Replacements |
|---|---|
| docs/operating-model/metric-management-system.md | 13 |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md | 9 |
| docs/evidence/closeouts/onboarding/2026-05-17-d409-asset-queue-closeout-DEC-b8ec00.md | 4 |
| docs/evidence/work-records/implementation/bcf-characteristic-amendment-doctrine-2026-06-23.md | 2 |
| docs/governance/adrs/ADR-1efa47.md | 2 |
| docs/evidence/work-records/implementation/housekeeping-residual-pendency-2026-06-23.md | 1 |
| docs/operating-model/metric-management-system-recovery-track.md | 1 |
| docs/reference/source-systems/microsoft-d365-bc.md | 1 |

## Sample Replacements

| File | Label | Old Target | Replacement | Reason |
|---|---|---|---|---|
| docs/evidence/closeouts/onboarding/2026-05-17-d409-asset-queue-closeout-DEC-b8ec00.md | Asset Batch 1 classification packet | ../../../../bc-core/scripts/audit-output/d409-asset-orphan-cf-batch1-packet-2026-05-17.md | `Asset Batch 1 classification packet` | link-escapes-docs-root |
| docs/evidence/closeouts/onboarding/2026-05-17-d409-asset-queue-closeout-DEC-b8ec00.md | Mega Drive 1 source-family packet | ../../../../bc-core/scripts/audit-output/d409-asset-batch2-source-family-packet-2026-05-17.md | `Mega Drive 1 source-family packet` | link-escapes-docs-root |
| docs/evidence/closeouts/onboarding/2026-05-17-d409-asset-queue-closeout-DEC-b8ec00.md | Mega Drive 1 apply artifacts | ../../../../bc-core/scripts/audit-output/d409-asset-batch2-us-gaap-ready-apply-2026-05-17.summary.md | `Mega Drive 1 apply artifacts` | link-escapes-docs-root |
| docs/evidence/closeouts/onboarding/2026-05-17-d409-asset-queue-closeout-DEC-b8ec00.md | Asset Batch 3 sublane triage packet | ../../../../bc-core/scripts/audit-output/d409-asset-model-conflict-sublane-packet-2026-05-17.md | `Asset Batch 3 sublane triage packet` | link-escapes-docs-root |
| docs/evidence/work-records/implementation/bcf-characteristic-amendment-doctrine-2026-06-23.md | registry-authoring.service.ts:1142 | C:/MyProjects/bc-core-runtime/src/registry/concept-registry/registry-authoring.service.ts:1142 | `registry-authoring.service.ts:1142` | absolute-local-link |
| docs/evidence/work-records/implementation/bcf-characteristic-amendment-doctrine-2026-06-23.md | registry-authoring.service.ts:1142-1145 | C:/MyProjects/bc-core-runtime/src/registry/concept-registry/registry-authoring.service.ts:1142 | `registry-authoring.service.ts:1142-1145` | absolute-local-link |
| docs/evidence/work-records/implementation/housekeeping-residual-pendency-2026-06-23.md | feedback_runtime_worktree_recipe.md | C:/Users/anant/.claude/projects/C--MyProjects-barecount-devhub/memory/feedback_runtime_worktree_recipe.md | `feedback_runtime_worktree_recipe.md` | absolute-local-link |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md | metric-readiness.controller.ts:17 | C:\MyProjects\bc-core\src\registry\metric-readiness.controller.ts | `metric-readiness.controller.ts:17` | absolute-local-link |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md | tenant-metrics.controller.ts:18 | C:\MyProjects\bc-core\src\tenant-metrics\tenant-metrics.controller.ts | `tenant-metrics.controller.ts:18` | absolute-local-link |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md | scope.guard.ts:43-47 | C:\MyProjects\bc-core\src\auth\guards\scope.guard.ts | `scope.guard.ts:43-47` | absolute-local-link |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md | roles.guard.ts:32 | C:\MyProjects\bc-core\src\auth\guards\roles.guard.ts | `roles.guard.ts:32` | absolute-local-link |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md | cognito-jwt.strategy.ts:54 | C:\MyProjects\bc-core\src\auth\strategies\cognito-jwt.strategy.ts | `cognito-jwt.strategy.ts:54` | absolute-local-link |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md | scope.guard.ts | C:\MyProjects\bc-core\src\auth\guards\scope.guard.ts | `scope.guard.ts` | absolute-local-link |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md | roles.guard.ts | C:\MyProjects\bc-core\src\auth\guards\roles.guard.ts | `roles.guard.ts` | absolute-local-link |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md | jwt-auth.guard.ts | C:\MyProjects\bc-core\src\auth\guards\jwt-auth.guard.ts | `jwt-auth.guard.ts` | absolute-local-link |
| docs/evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md | cognito-jwt.strategy.ts | C:\MyProjects\bc-core\src\auth\strategies\cognito-jwt.strategy.ts | `cognito-jwt.strategy.ts` | absolute-local-link |
| docs/governance/adrs/ADR-1efa47.md | metric-evaluation-engine.service.ts:879 | C:/MyProjects/bc-core/src/boundary/metric-evaluation-engine.service.ts | `metric-evaluation-engine.service.ts:879` | absolute-local-link |
| docs/governance/adrs/ADR-1efa47.md | chain-status.service.ts:681 | C:/MyProjects/bc-core/src/registry/chain-status.service.ts:681 | `chain-status.service.ts:681` | absolute-local-link |
| docs/operating-model/metric-management-system-recovery-track.md | `bc-core/src/database/schema/mcf/` | ../../../bc-core/src/database/schema/mcf/ | `bc-core/src/database/schema/mcf/` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `bc-core/src/database/schema/mcf/metric-contract.ts` | ../../../bc-core/src/database/schema/mcf/metric-contract.ts | `bc-core/src/database/schema/mcf/metric-contract.ts` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `metric-contract.ts` | ../../../bc-core/src/database/schema/mcf/metric-contract.ts | `metric-contract.ts` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `metric-contract-version.ts` | ../../../bc-core/src/database/schema/mcf/metric-contract-version.ts | `metric-contract-version.ts` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `04-mcf-substrate.sql` | ../../../bc-core/docker/redesign/04-mcf-substrate.sql | `04-mcf-substrate.sql` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `07-mcf-formula-ast-storage.sql` | ../../../bc-core/docker/redesign/07-mcf-formula-ast-storage.sql | `07-mcf-formula-ast-storage.sql` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `05-mcf-lifecycle-substrate.sql` | ../../../bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql | `05-mcf-lifecycle-substrate.sql` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `07-mcf-formula-ast-storage.sql` | ../../../bc-core/docker/redesign/07-mcf-formula-ast-storage.sql | `07-mcf-formula-ast-storage.sql` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `mcf-mcv-abandon.controller.ts` | ../../../bc-core/src/registry/mcf/mcf-mcv-abandon.controller.ts | `mcf-mcv-abandon.controller.ts` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `10-mcf-self-verification-result.sql` | ../../../bc-core/docker/redesign/10-mcf-self-verification-result.sql | `10-mcf-self-verification-result.sql` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `05-mcf-lifecycle-substrate.sql` | ../../../bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql | `05-mcf-lifecycle-substrate.sql` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `bc-core/src/database/schema/mcf/metric-contract.ts` | ../../../bc-core/src/database/schema/mcf/metric-contract.ts | `bc-core/src/database/schema/mcf/metric-contract.ts` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `bc-core/src/database/schema/mcf/` | ../../../bc-core/src/database/schema/mcf/ | `bc-core/src/database/schema/mcf/` | link-escapes-docs-root |
| docs/operating-model/metric-management-system.md | `bc-core/docker/redesign/04..19-mcf-*.sql` | ../../../bc-core/docker/redesign/ | `bc-core/docker/redesign/04..19-mcf-*.sql` | link-escapes-docs-root |
| docs/reference/source-systems/microsoft-d365-bc.md | v2 reference page | ../../../bc-docs-v2/docs/reference/sources/microsoft-d365-bc.md | `v2 reference page` | link-escapes-docs-root |
