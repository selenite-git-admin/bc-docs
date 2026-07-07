---
id: quality-assurance
order: 41
title: "Quality Assurance"
status: drafting
authority: authoritative
depends_on: [the-authority-model, devhub, build-and-release]
governing_sources:
  - The Authority Model
  - DevHub
  - Build and Release
governing_adrs:
  - DEC-ee6018 (bc-qa standalone repo; QA tooling lives in its own repo, audits all platform repos cross-cutting)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Quality Assurance

## Scope

This chapter records the platform's quality-assurance substrate: the bc-qa standalone repository, the audit harness that scans every platform repo for code-quality non-conformities, the gate-config that encodes per-repo severity, the eslint-config package that every TypeScript repo consumes, the pre-commit hook that runs at developer-machine commit time, the QA NC register that holds non-conformity records to resolution, the DevHub MCP integration that wraps the audit harness from a Claude session, and the as-built gaps in CI integration.

This chapter does not redefine the build and release procedure that consumes the QA tooling (Build and Release), the developer environment that installs the pre-commit hook (Developer Experience), or the change-record substrate that QA findings are linked to (Decision and Change Procedure).

**Governing source.** outline.md §4.5; The Authority Model.

## bc-qa as the QA Authority

Per `DEC-ee6018`, the platform's quality-assurance tooling lives in `bc-qa`, a standalone repository, not in any application repo and not in DevHub. The discipline is "the platform has one QA authority"; every platform repo consumes bc-qa's tooling, and bc-qa audits every platform repo.

| Repo concern | bc-qa structure |
|---|---|
| The audit harness | `bc-qa/audits/` carries the audit-repo.sh runner and a `checks/` subdirectory of modular check scripts |
| The pre-commit hooks | `bc-qa/hooks/` carries the pre-commit hook plus the install-hooks.sh script that copies it into a target repo |
| The gate configuration | `bc-qa/gates/` carries gate-config.json (per-repo severity matrix) and compliance-gate.sh (the CI integration wrapper) |
| The eslint-config package | `bc-qa/eslint/` is the source of `@barecount/eslint-config`, published to CodeArtifact and consumed by every TypeScript repo |
| The non-conformity register | `bc-qa/audits/nc-register.json` carries per-NC entries with lifecycle state (open through resolved) |

The bc-qa repo has no runtime; it is tooling-only. There is no port, no service, no pm2 entry. Per `DEC-ee6018`, bc-qa is tooling only, with no running service, no port, and no pm2 entry.

**Governing source.** DEC-ee6018 (bc-qa standalone repo); CLAUDE.md (QA Tooling section).

## The Audit Harness

The audit harness scans a target repo for code-quality non-conformities. The runner is `bc-qa/audits/audit-repo.sh`; it iterates a set of modular check scripts under `bc-qa/audits/checks/` and produces a verdict.

| Check | What it scans for |
|---|---|
| `check-eslint.sh` | ESLint runs against the repo's source; rule violations are recorded |
| `check-eslint-config.sh` | Confirms `@barecount/eslint-config` is consumed; absence is the violation |
| `check-ts-strict.sh` | Confirms `tsconfig.json` declares `strict: true` |
| `check-ts-ignore.sh` | Confirms no new `@ts-ignore` markers; `@ts-expect-error` with a justification comment is the substitute |
| `check-any-types.sh` | Confirms no new explicit `any` (literal `: any`, `as any`, `<any>`); the any-count baseline is held |
| `check-function-length.sh` | Confirms maximum function length: sixty effective lines repo-wide, forty effective lines in safety-critical directories |
| `check-nesting-depth.sh` | Confirms maximum nesting depth: three repo-wide, two in safety-critical directories |
| `check-no-eval.sh` | Confirms no `eval()`, `new Function()`, `vm.runInContext()`, or `vm.createScript()` anywhere |
| `check-console-log.sh` | Confirms no `console.log`, `console.info`, `console.debug`, `console.trace` in `src/`; `console.warn` and `console.error` permitted |
| `check-forbidden-vocab.sh` | Scans the safety-critical directories (evaluation, readers, canonical, metrics, boundaries, admission, observation) for forbidden roots |
| `check-hardcoded-enums.sh` | Scans frontend repos for `*_OPTIONS`, `*_TYPES`, `*_STATUSES` arrays; the `// qa-approved: static-enum` comment is the explicit escape |
| `check-ruff.sh` | Runs ruff against bc-ai's Python source |
| `check-chain-invariants.sh` | Queries the platform PostgreSQL container for chain invariant violations; runs only when the container is reachable |

The audit runner reads a per-repo gate-config to classify each finding into block, warn, skip, or info. The verdict logic: any blocked finding produces NON-COMPLIANT (exit code 1); any warned or failed finding produces CONDITIONAL (exit code 0); zero of either produces COMPLIANT (exit code 0).

By default the harness is informational: every check runs and findings are reported, but only blocked findings produce a non-zero exit. The `--gate` flag flips the runner into gating mode: the configured severity for each check is honored. The CI integration wrapper at `bc-qa/gates/compliance-gate.sh` runs the audit in gating mode and is the integration point when CI lands.

**Governing source.** `bc-qa/audits/audit-repo.sh`; `bc-qa/audits/checks/`.

## The Gate Configuration

The gate-config at `bc-qa/gates/gate-config.json` records per-repo severity for each check. The per-repo overrides tighten or loosen the default severity according to the repo's role.

| Check | Default | bc-core | bc-admin | bc-portal | bc-ai | DevHub |
|---|---|---|---|---|---|---|
| `no-eval` | block | block | block | block | block | block |
| `eslint-config` | warn | block | block | warn | skip | skip |
| `eslint` | warn | block | block | warn | skip | skip |
| `ts-strict` | warn | block | block | warn | skip | skip |
| `ts-ignore` | warn | block | warn | warn | skip | skip |
| `forbidden-vocab` | warn | block | warn | warn | warn | skip |
| `any-types` | warn | warn | warn | warn | skip | skip |
| `function-length` | warn | warn | warn | warn | skip | warn |
| `console-log` | warn | warn | warn | warn | skip | skip |
| `hardcoded-enums` | warn | skip | warn | warn | skip | skip |
| `ruff` | warn | not applicable | not applicable | not applicable | block | not applicable |

The `no-eval` row is the only universally-blocking check; every repo blocks on the introduction of dynamic code execution. bc-core carries the strictest profile because the contract evaluation acts run there. bc-ai carries the Python-first profile (ruff blocking; TypeScript checks not applicable). DevHub carries the relaxed profile (engineering-coordination tooling, not contract execution).

**Governing source.** `bc-qa/gates/gate-config.json`; CLAUDE.md (Coding Standards section, Severity Quick Reference table).

## The eslint-config Package

The platform's TypeScript rule set is the `@barecount/eslint-config` package, published from `bc-qa/eslint/` to AWS CodeArtifact. The package exports three entry points.

| Module | Scope | Tightening |
|---|---|---|
| `base` | Default for every TypeScript repo | The Power-of-Ten rules adapted for BareCount: max-depth 3 (warn), no-eval (error), no-new-func, max-lines-per-function 60 (warn), prefer-const, no-var, no-empty, max-nested-callbacks 2 (warn), no-nested-ternary, no-console (allowing warn and error), no-debugger |
| `pipeline` | Override for `src/evaluation/`, `src/readers/`, `src/canonical/`, `src/metrics/`, `src/boundaries/`, `src/admission/`, `src/observation/` in bc-core | max-depth 2 (error), max-lines-per-function 40 (error), max-nested-callbacks 1 (error, forces async/await), no-console (error, structured logger only) |
| `scripts` | Override for seed scripts and one-shot tools | Relaxed; some rules are downgraded from warn to off because seed scripts have different cardinality concerns from runtime code |

Every TypeScript repo's `eslint.config.js` extends `@barecount/eslint-config`; the package handles base rule definition, parser configuration, and the per-directory overrides. Platform repos do not redefine rules locally; if a rule needs to change, it changes in bc-qa and propagates through the next install.

**Governing source.** `bc-qa/eslint/index.cjs`, `base.cjs`, `pipeline.cjs`, `scripts.cjs`.

## The Pre-Commit Hook

The pre-commit hook runs at developer commit time. The install-hooks.sh script copies `bc-qa/hooks/pre-commit` into a target repo's `.git/hooks/pre-commit`, backing up any existing hook with a timestamp suffix.

| Check | Severity | Behavior |
|---|---|---|
| ESLint on staged TS or JS files | Block | Hook exits non-zero, commit is rejected |
| `@ts-ignore` introduced | Block | Suggests `@ts-expect-error` with justification |
| `eval()` or `new Function()` introduced | Block | The universally-blocking discipline, applied at commit time |
| `console.log` introduced | Warn | The hook prints a warning but does not reject the commit |
| ruff on staged Python files (bc-ai) | Block | Same exit-on-failure path |
| `eval` or `exec` introduced in Python | Block | The Python equivalent of the no-eval discipline |

The hook does not unstage on failure. Per pattern 86: a hook that exits non-zero leaves staged files in place; the developer fixes the issue and recommits. There is no automatic recovery; the discipline is "the developer reviews the rejected commit and chooses the next action."

The pre-commit hook is the developer-machine enforcement; the bc-qa audit harness is the on-demand or scheduled enforcement. The two surfaces overlap in coverage but run at different times: pre-commit catches violations before they enter the repository; the audit harness catches drift in the repository state.

**Governing source.** `bc-qa/hooks/pre-commit`; `bc-qa/hooks/install-hooks.sh`.

## The QA NC Register

The non-conformity register at `bc-qa/audits/nc-register.json` records every NC raised by the audit harness or by manual entry. The register is the audit trail: an NC is a row that lives until it is resolved, waived, or accepted.

| Field | Form |
|---|---|
| `nc_id` | `NC-YYYYMMDD-NNN`, auto-generated by `nc-manage.sh raise` |
| `raised_at` | ISO 8601 timestamp |
| `repo`, `check`, `severity` | The target, the check, the severity per gate-config |
| `finding`, `file`, `line` | The human-readable finding; optional file path and line number |
| `status` | `open`, `investigating`, `resolved`, `accepted`, or `waived` |
| `assigned_to`, `resolved_at`, `resolution`, `resolution_type` | Lifecycle attributes |
| `waiver_reason` | Mandatory when `status` becomes `waived`; the rationale is preserved |
| `session_ref`, `commit_ref` | Linkage back to the change-record trail |

NCs are created by two paths. The manual path runs `bc-qa/audits/nc-manage.sh raise <repo> <check> <severity> <finding> [file] [line]`. The automated path runs through the DevHub `devhub_qa_audit` MCP tool, which scans audit output for ESLint findings and bulk-inserts NC rows into the DevHub `qa_nc_records` table; the DevHub-side and the bc-qa-side registers are parallel substrates that the operator reconciles at audit-review time.

**Governing source.** `bc-qa/audits/nc-register.json`; `bc-qa/audits/nc-manage.sh`.

## DevHub MCP Integration

`devhub_qa_audit` (the MCP tool) wraps the bc-qa audit harness from a Claude session. The wrapper at `barecount-devhub/src/lib/qa-audit.js` shells out to `bash bc-qa/audits/audit-repo.sh`, parses the output, persists the run, and auto-raises NCs from any ESLint findings.

| Step | Behavior |
|---|---|
| Shell out | `runAuditShell(repoPath)` invokes the bc-qa runner; stdout is captured even on non-zero exit |
| Verdict parse | `parseAuditCounts(output)` extracts PASS, WARN, FAIL, BLOCK, SKIP counts and computes the verdict |
| Report write | `writeAuditReport(repo, verdict, counts, output)` writes a markdown report to `bc-docs/docs/qa-reports/AUDIT-{repo}-{date}.md` with frontmatter |
| ESLint parse | `parseEslintFindings(output)` reads structured `ESLINT_NC` lines (format `ESLINT_NC|file|line|col|ruleId|severity|message`) and returns finding rows |
| NC creation | `createNcsFromFindings(...)` bulk-inserts NC records into the DevHub `qa_nc_records` table; `severity` maps `error` to `block` and `warning` to `warn`; `check_name` is `eslint:{ruleId}`; the audit UID provides linkage |

The DevHub side persists per-run rows in `qa_audit_runs` (with verdict, counts, and report-file path) and per-NC rows in `qa_nc_records` (with the lifecycle fields parallel to the bc-qa-side register). The two substrates are reconciled at review time; see the drift inventory below.

**Governing source.** `barecount-devhub/src/lib/qa-audit.js`; `barecount-devhub/src/db.js` (qa_audit_runs and qa_nc_records).

## Constraints

| Constraint | Form |
|---|---|
| Single QA authority | bc-qa is the only repo that owns quality-assurance tooling; no platform repo defines its own rule set |
| `no-eval` is universally blocking | Every repo blocks on dynamic code execution introduction |
| Safety-critical directories tighten the rule set | bc-core's evaluation, readers, canonical, metrics, boundaries, admission, and observation directories carry stricter limits than the rest of the codebase |
| Pre-commit hook is local-only | The hook is a developer-machine discipline; nothing prevents bypass with `git commit --no-verify` other than the discipline that the bc-qa audit will catch the violation later |
| Audit is post-hoc by default | The harness runs on demand or on a schedule; CI gating is queued |
| ESLint config delivers through CodeArtifact | Per Build and Release, every install resolves `@barecount/eslint-config` through CodeArtifact; the package version evolves in bc-qa and propagates through the next install |
| Two parallel NC registers | The bc-qa-side register is the file-of-record; the DevHub-side register is the queryable substrate; reconciliation is operator-driven |

**Governing source.** DEC-ee6018; CLAUDE.md (Coding Standards section).

## Failure Modes

| Failure | Behavior |
|---|---|
| `audit-repo.sh` cannot read a target repo | The runner exits with the input-validation error; operator confirms the repo path and reruns |
| ESLint version drift between bc-qa and a target repo | Different rule interpretations may produce different findings; operator reconciles by aligning the package versions in the next install |
| `check-chain-invariants.sh` cannot reach the postgres container | The check is skipped with a warning; the audit continues without the chain-invariant signal |
| Pre-commit hook is bypassed via `git commit --no-verify` | The commit lands without enforcement; the next audit run catches the violation; the bypass is a discipline violation |
| `@barecount/eslint-config` install fails (CodeArtifact 401 or 403) | Standard CodeArtifact renewal procedure (Build and Release); audit cannot run until the install completes |
| ESLint config rule rename in bc-qa breaks a target repo's lint | Operator pins the bc-qa version in the target repo's package.json until the rule rename is reconciled; the discipline is "bc-qa is the authority, but rule renames coordinate across consumers" |
| NC registered in bc-qa-side but missing from DevHub-side | Reconciliation procedure runs at audit review; operator either reraises in the missing register or accepts the partial coverage as a known reconciliation gap |
| pre-commit hook not installed in a repo | The repo carries no commit-time enforcement; the audit harness catches violations later; install-hooks.sh restores the hook |

**Governing source.** `bc-qa/audits/audit-repo.sh`; `bc-qa/hooks/`.

## Drift Inventory

| Drift item | Status |
|---|---|
| No CI integration | Recorded; `bc-qa/gates/compliance-gate.sh` exists as the integration point but no GitHub Actions workflow invokes it |
| `check-chain-invariants.sh` is asymmetric | Recorded; the check queries postgres directly rather than scanning source; it is not in `gate-config.json`; runs only when invoked directly or as part of a full audit |
| `check-nesting-depth.sh` is missing from `gate-config.json` | Recorded; when the audit-runner encounters this check it falls through to the warn default; the gate-config entry is queued |
| Two parallel NC registers (bc-qa-side and DevHub-side) | Recorded; the reconciliation procedure is operator-driven; an automated reconciliation pass is queued |
| Pre-commit hook does not unstage on failure | Recorded; the discipline is intentional ("prevent" rather than "recover"); a documented memory note describing the hook as auto-unstaging is incorrect and is being corrected |
| bc-qa repo carries zero unit tests | Recorded; tooling repos validate through their consumers; testing through integration with target repos is the as-built model |
| ESLint version pinning across consumers is informal | Recorded; consumers install the package version resolved at install time; coordinated rule-rename rollouts are operator-driven |

**Governing source.** `bc-qa/gates/gate-config.json`; CLAUDE.md (Coding Standards Severity Quick Reference table).

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| DevHub | The DevHub MCP tool surface and the `qa_audit_runs` and `qa_nc_records` tables | The `devhub_qa_audit` integration and the auto-raise procedure that writes into those tables |
| Build and Release | The CodeArtifact registry through which `@barecount/eslint-config` is installed; the per-repo build commands that consume the config | The QA tooling that the build-side commands invoke |
| Developer Experience | The developer-machine setup, including the install-hooks.sh invocation | The hook definitions and the rule set the hook enforces |
| Decision and Change Procedure | The change-record substrate that NC `session_ref` and `commit_ref` link back to | The QA NC register as a parallel governance trail to the change-record substrate |
| Operating Model | The platform's contract-evaluation runtime; the safety-critical directories whose stricter rule set the QA tooling enforces | The lint and audit checks that enforce the tighter rules in those directories |

**Governing source.** outline.md §4.5; The Authority Model.

## References

- The Authority Model
- DevHub
- Build and Release
- Developer Experience
- Decision and Change Procedure
- DEC-ee6018 (bc-qa standalone repo)
- CLAUDE.md (QA Tooling, Coding Standards, Severity Quick Reference sections)
