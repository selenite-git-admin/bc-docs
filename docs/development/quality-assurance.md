---
id: quality-assurance
order: 41
title: "Quality Assurance"
status: drafting
authority: authoritative
depends_on: [the-authority-model, devhub, build-and-release, continuous-integration, decision-and-change-procedure]
governing_sources:
  - The Authority Model
  - DevHub
  - Build and Release
  - Continuous Integration
  - Decision and Change Procedure
governing_adrs:
  - DEC-5b760c (QA enforcement consolidates into per-repo CI; DevHub is the sole NC authority; bc-qa retires and archives)
  - DEC-ee6018 (Power of Ten, adapted coding rules; the rule set that CI enforces through @barecount/eslint-config)
  - DEC-f0c0f7 (No hardcoded enums; a convention with no enforcer, recorded here as such)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Quality Assurance

## Scope

This chapter records where the platform's engineering quality is enforced and what that enforcement is. Since `DEC-5b760c` (decided 2026-08-24) each repository's own continuous-integration workflow is the only place quality rules are enforced, the DevHub `qa_nc_records` table is the only non-conformance register, and the bc-qa repository that once held a cross-repository audit is archived. The chapter states the coding rules (`DEC-ee6018`) as the executable configuration defines them, the enforcement each repository actually applies on every push (with the file and line that applies it), the architecture gates that bc-core runs as tests, the non-conformance register and what does and does not write to it, and the gaps between the written standard and the enforced one.

This chapter does not redefine the build and release procedure and the CI workflows themselves (Build and Release; Continuous Integration), the DevHub tables and tools (DevHub), or the change-record trail that a non-conformance links to (Decision and Change Procedure).

The chapter's rule is the Compliance section's rule: a control is described only where it exists, at the level at which it binds. A rule set to `warn` binds only in a repository whose CI fails on warnings. Everything in the enforcement table below was read from the named files on 2026-09-30; the drift inventory records where the standard and the enforcement differ.

**Governing source.** DEC-5b760c; DEC-ee6018; The Authority Model.

## Where Quality Is Enforced

`DEC-5b760c` moved enforcement to where code changes: each repository's CI, on every push and pull request. The decision was taken after the cross-repository audit mechanism ran once in five months and returned a verdict dominated by defects in the gate itself (a vacuous forbidden-vocabulary scan, two false-positive blocks, a summary-only report, a file register never written by tooling). The principle it recorded: a gate that runs on every push beats an audit that runs never.

| Disposition (DEC-5b760c) | State on 2026-09-30 |
|---|---|
| Each repository's CI is its QA enforcement authority; severity lives in each repository's own lint and test configuration | In force; see the enforcement table |
| The DevHub database is the single non-conformance authority; the bc-qa file register is retired | In force; the file register had zero entries for its whole life (NC-04b0bb) |
| `@barecount/eslint-config` is sourced from `bc-core/tools/eslint-config` and published to CodeArtifact under the unchanged name | In force; version 1.0.0; four consumers pin `^1.0.0` |
| The two unique checks (frozen imports, forbidden vocabulary) become bc-core vitest architecture tests | In force; `src/__architecture__/frozen-imports.spec.ts` and `forbidden-vocab.spec.ts` with `frozen-registry.json` and `forbidden-vocab.baseline.json`, run in the sharded vitest job |
| The shell audit layer, compliance gate, reports directory, `nc-manage.sh` and hook templates retire with the repository | Retired; no repository carries the bc-qa hook (no `.husky`, no `lint-staged`, no `.pre-commit-config.yaml` anywhere) |
| `check-chain-invariants.sh` is preserved by the archive for the chain-invariants track | Archived; not running anywhere |
| bc-qa is archived (GitHub archive flag; local copy under `_archived-repos`) | Done 2026-08-24 |

Nothing runs across repositories any more. The DevHub Guards page keeps a read-only rule scan of every repository's `main` (Hotspots; ten rules) as a mirror, not a gate: it fails nothing and writes no register.

**Governing source.** DEC-5b760c; `bc-core/src/__architecture__/`; barecount-devhub `src/lib/rule-audits.js`.

## The Coding Rules as the Executable Configuration Defines Them

`DEC-ee6018` adapted the Power of Ten rules for BareCount. The executable form is the `@barecount/eslint-config` package (`bc-core/tools/eslint-config/eslint/`, version 1.0.0). It exports three configurations; a consumer spreads the ones it wants into its own `eslint.config`. The levels below are the package's, read on 2026-09-30. The project instructions' prose summary of the rules is not the authority; these files are.

| Rule | `base.cjs` (all `src/**`) | `pipeline.cjs` (the safety-critical directories) | `scripts.cjs` (seeds, scripts, tools, drizzle) |
|---|---|---|---|
| `no-eval`, `no-new-func`, `no-implied-eval` | error | error | error |
| `prefer-const`, `no-var` | error | error | error |
| `no-empty` (empty catch not allowed) | error | error | error |
| `no-with`, `no-debugger` | error | error | error |
| `max-depth` | warn, 3 | error, 2 | warn, 3 |
| `max-lines-per-function` | warn, 60 (blank lines and comments skipped) | error, 40 | off |
| `max-nested-callbacks` | warn, 2 | error, 1 | warn, 2 |
| `no-nested-ternary` | warn | warn | warn |
| `no-console` | warn, allowing `warn` and `error` | error | off |
| `no-restricted-syntax`: dynamic `require`, module-level `let`, `new Proxy` | warn | warn | off |

Two rules the project instructions list are not in the shared package. `@typescript-eslint/no-explicit-any` is set to `warn` in the bc-core, bc-admin and bc-portal repository configurations and is not set in barecount-devhub (plain JavaScript). The ban on `@ts-ignore` comes from typescript-eslint's recommended set, which the three TypeScript repositories extend.

The `pipeline.cjs` file globs name `src/evaluation/`, `src/readers/`, `src/canonical/`, `src/metrics/`, `src/boundaries/`, `src/admission/` and `src/observation/`. None of those directories exists in bc-core, whose evaluation code lives under `src/boundary/` (singular). bc-core's own `eslint.config.mjs` therefore restates the four pipeline rules at `error` for `src/boundary/**` (lines 78 to 85). In every other consumer the pipeline configuration matches no file.

**Governing source.** `bc-core/tools/eslint-config/eslint/base.cjs`, `pipeline.cjs`, `scripts.cjs`, `index.cjs`; `bc-core/eslint.config.mjs`; DEC-ee6018.

## Enforcement per Repository

What each repository's CI runs on every push and pull request, and whether the `warn`-level rules bind there. A `warn` rule binds only where ESLint runs with `--max-warnings 0`. Branch protection on `main` was read from the GitHub API on the same day.

| Repository | Lint in CI | Warn-level rules bind? | Other gates in CI | Branch protection on `main` |
|---|---|---|---|---|
| bc-core | `npx eslint . --max-warnings 0` (`.github/workflows/ci.yml:76`) | Yes | `npm run lint:columns` (ISO 11179 column names, `ci.yml:84`); `npm run typecheck` (three tsconfigs, `ci.yml:86`); vitest in three shards including the architecture tests (`ci.yml:155`); a database integration job | One approval, `quality-gate` check, enforced for administrators |
| bc-portal | `npm run lint --workspace=apps/web` (`ci.yml:44`), which is `eslint src/ --max-warnings 0` (`apps/web/package.json:10`) | Yes | typecheck, build, vitest | One approval, `quality-gate`, enforced for administrators |
| barecount-devhub | `npx eslint src/` (`ci.yml:105`; the step is named "errors fail; warnings backlog tracked separately") | No: errors only | hook-mode check, MCP tools-list check, exchange publisher tests, `npm test` (node test runner) | One approval, `quality-gate` and `unit-tests (macos-latest)`, enforced for administrators |
| bc-admin | None: no ESLint step in `ci.yml` and no `lint` script in `package.json` | No: nothing lints | `npm run typecheck` (`ci.yml:63`; a hard gate since 2026-09-30, TSK-6d58ee), `npm run test` (`ci.yml:70`), `npx vite build` (`ci.yml:73`) | One approval, `build`, enforced for administrators |
| bc-db | None (SQL and shell; no JavaScript source) | Not applicable | Five rehearsal shards of shell and node tests, aggregated by `quality-gate` | One approval, `quality-gate`, enforced for administrators |
| bc-demo | None (Python) | Not applicable | pytest, build gates, `compileall` | One approval, `test` and `build-gates`, enforced for administrators |
| bc-infra | None | Not applicable | `npm test`, `cdk synth`, `cdk diff --fail` with a replacement guard (`ci-validate.yml`) | One approval, `validate`, enforced for administrators |
| bc-docs | None | Not applicable | `python scripts/docs-control/audit_adrs.py` (`adr-hygiene.yml:25`; merge-blocking on supersession issues only) | One approval, `adr-hygiene`, enforced for administrators |
| bc-exchange | None (`node --check` syntax checks only, `ci.yml:18`) | Not applicable | `npm test` | One approval, `test`; not enforced for administrators |
| bc-external-audit | No CI workflow at all | Not applicable | None | No branch protection; the operator merges by hand after the auditor's review (see ISO 27001 Conformance, A.8.32) |

So the Power of Ten `warn` rules (function length, nesting depth, callback depth, nested ternaries, console use, module-level `let`) bind in bc-core and bc-portal only. In barecount-devhub they are advisory; in bc-admin nothing lints at all. The `error` rules (`no-eval`, `prefer-const`, `no-var`, `no-empty`) bind wherever ESLint runs: bc-core, bc-portal and barecount-devhub.

There is no developer-machine hook anywhere except barecount-devhub's own scoped pre-commit hook (`scripts/hooks/pre-commit`, installed through `core.hooksPath`), which guards the MCP tools list and runbook paths and runs no lint. The bc-qa hook that earlier versions of this chapter and of InfoSec and Access Control described is gone.

**Governing source.** Each repository's `.github/workflows/*.yml` and `package.json`; the GitHub branch-protection API, read 2026-09-30.

## Architecture Gates in bc-core

bc-core carries gates that no lint rule can express, as vitest specifications under `src/__architecture__/`, run in the sharded vitest job of its CI. They are shrink-only registers: a new violation fails the build, and a baseline entry that no longer matches fails too until the baseline is lowered.

| Gate | What it holds |
|---|---|
| `frozen-imports.spec.ts` with `frozen-registry.json` | The modules whose import surface is frozen (the DEC-5b760c port of the bc-qa check, with import-specifier parsing and a refusal-test exemption) |
| `forbidden-vocab.spec.ts` with `forbidden-vocab.baseline.json` | The forbidden vocabulary in the evaluation code, failing closed when zero files are scanned |
| `boundary-quality.spec.ts` with `boundary-quality.baseline.json` | Per-file counts for the evaluation code (calculator rules, security, length, lint suppression, smell, tests, docs, duplication), frozen at a dated `main` |
| The other specifications in the same directory | Plane discipline (D575), controller injection and request validation, route scope and roles, persisted codes, fetch depth and further structural rules; the directory listing on `main` is the inventory |

These gates are the only place where quality rules bind at the level of the evaluation code's structure rather than its syntax. The review rule that accompanies them: a pull request that raises a baseline count or adds a baseline key is refused, since the test cannot block that by itself.

**Governing source.** `bc-core/src/__architecture__/`; DEC-5b760c dispositions 4 and 5.

## Rule 14: No Hardcoded Enum Arrays (a Convention)

`DEC-f0c0f7` requires that front-end dropdowns are API-driven and forbids hardcoded `{value, label}` arrays outside a short list of exceptions, with `// qa-approved: static-enum` as the escape hatch. Its enforcement table names `check-hardcoded-enums.sh` in bc-qa and a planned ESLint rule. Neither exists: the script exists in no live or archived repository, and no consumer's ESLint configuration and no shared configuration carries such a rule. The ADR's `implemented` status is therefore wider than its enforcement, and the marker is used in bc-admin only (eleven occurrences) while bc-portal carries hundreds of unmarked `value`/`label` lines.

Until an enforcer exists, rule 14 is a code-review convention, not a gate. This chapter records it as such; the decision on building the rule or amending the ADR by erratum is queued (see the drift inventory).

**Governing source.** DEC-f0c0f7; the consumer `eslint.config` files.

## The Non-Conformance Register

The register is the DevHub `qa_nc_records` table, the single non-conformance authority since `DEC-5b760c`. It is queryable through `GET /api/qa/nc` and `GET /api/qa/nc/stats`, written through `POST /api/qa/nc` and `PATCH /api/qa/nc/:uid`, and wrapped by the MCP tools `devhub_qa_nc_raise`, `devhub_qa_nc_update`, `devhub_qa_nc_list` and `devhub_qa_nc_stats`.

| Field | Form |
|---|---|
| `uid` | `NC-xxxxxx`, allocated by DevHub |
| `repo_slug`, `check_name`, `severity` | The repository, the check (for ESLint findings, `eslint:<ruleId>`), `block` or `warn` |
| `finding`, `file_path`, `line_number` | The finding and its location |
| `nc_status` | `open`, `investigating`, `resolved`, `accepted` or `waived`; `resolved_at` is set when the status moves to `resolved`, `waived` or `accepted` |
| `resolution`, `resolution_type`, `waiver_reason`, `assigned_to` | Lifecycle attributes; a waiver carries its reason |
| `commit_ref`, `session_ref`, `audit_uid`, `actor_name` | Links to the change-record trail and to the run that raised the row |

The register has no idempotency key: two raises of the same finding produce two rows. Any automated writer must supply one.

Its consumers are the DevHub ISO readiness page (counts by status and open rows by repository) and the daily NC-aging housekeeping digest, which reports counts, aging buckets and rows from retired tooling.

**What writes it today: nothing.** The register's rows were raised by the retired bc-qa audit through DevHub's `devhub_qa_audit` wrapper, which `DEC-5b760c` retired with the mechanism. CI fails a build when a gate goes red but writes no row. As read on 2026-09-30 the register holds 1,581 rows, 1,566 of them open, all raised on or before 2026-08-24, and no row has been raised or resolved since. The aging digest therefore reports a frozen register, and the register is not evidence of any current non-conformance process. The Compliance & Quality controller has put two decisions to the operator (barecount-devhub task TSK-1c4ae3): a writer inside DevHub that reconciles the register from its own per-repository rule scan of `main`, restricted to the rules CI actually fails on and keyed for idempotency; and one bulk ruling on the 1,565 bc-qa-era rows, waiving them as superseded by per-repository CI while keeping the one real finding (NC-e886b3) open. Until a writer exists and is proven by one row raised and one resolved through it, this chapter claims none.

**Governing source.** barecount-devhub `src/db.js` (the `qa_nc_records` schema), `src/routes/qa.js`, `src/mcp-server.js`; the NC-aging digest (TSK-b0685b); DEC-5b760c disposition 2.

## Constraints

| Constraint | Form |
|---|---|
| Per-repository CI is the only enforcement home | No cross-repository audit runs; severity is each repository's own configuration (DEC-5b760c) |
| The DevHub table is the only register | No file register; `bc-qa/audits/nc-register.json` is retired and must not be cited |
| The executable configuration is the authority for rule levels | Prose summaries (including the project instructions) restate; the `.cjs` files and each repository's `eslint.config` decide |
| A `warn` rule binds only under `--max-warnings 0` | Today: bc-core and bc-portal |
| The safety-critical directories are `src/boundary/**` in bc-core | The shared `pipeline.cjs` globs match nothing; bc-core restates the rules for the real directory |
| The shared package is delivered through CodeArtifact | Every install resolves `@barecount/eslint-config` through the `barecount` domain (Build and Release) |
| No claim without an enforcer | Rule 14 is a convention; the register has no writer; both are recorded as such |

**Governing source.** DEC-5b760c; DEC-ee6018; Build and Release.

## Failure Modes

| Failure | Behavior |
|---|---|
| A lint error or a failing test on a pull request | The repository's CI check fails; branch protection refuses the merge until the head is green |
| A warning in bc-core or bc-portal | Fails the build (`--max-warnings 0`); the change is fixed or the rule is deliberately disabled inline with a reason, which review sees |
| A warning in barecount-devhub | Passes CI; it joins the warnings backlog and nothing tracks it except the Guards page rule scan |
| A lint violation in bc-admin | Nothing catches it in CI; typecheck, tests and build are the only gates |
| A new architecture-gate violation in bc-core | The shrink-only spec fails; the baseline may not be raised in the same pull request |
| A CodeArtifact token expiry (401 or 403 on install) | The standard renewal (Build and Release) |
| A finding that should be a non-conformance | Nothing files it automatically; a person raises it with `devhub_qa_nc_raise`, or it stays outside the register |
| A rule-14 violation | Only code review can catch it; there is no gate |

**Governing source.** Each repository's CI workflow; `bc-core/src/__architecture__/`.

## Drift Inventory

| Drift item | Status |
|---|---|
| Enforcement is uneven: `warn`-level Power of Ten rules bind only in bc-core and bc-portal; barecount-devhub passes warnings; bc-admin has no lint step | Recorded 2026-09-30; adding ESLint with `--max-warnings 0` to bc-admin and barecount-devhub CI is queued with the Admin Portal and DevHub controllers |
| The shared `pipeline.cjs` globs match no directory in any consumer | Recorded; bc-core restates the rules for `src/boundary/**`; renaming the globs in the package is queued |
| Rule 14 has no enforcer while `DEC-f0c0f7` reads `implemented` | Recorded; build `@barecount/no-hardcoded-selects` in the shared package, or amend the ADR by erratum |
| The non-conformance register has no writer and has been frozen since 2026-08-24 | Recorded; the writer and the bulk ruling on the old rows are with the operator (TSK-1c4ae3) |
| The register has no idempotency key | Recorded; required before any automated writer runs |
| bc-external-audit has no CI and no branch protection | Recorded; review there is by practice on the exchange (ISO 27001 Conformance, A.8.32) |
| The project instructions describe the rules at their intended levels and say they are "enforced in each repo's CI" | Recorded; true only as this chapter's table qualifies it |
| Other chapters still describe bc-qa as live (Build and Release, Developer Experience, DevHub, Decision and Change Procedure, the Development and Compliance overviews, SOC 2 Conformance, Security Operations, and others) | Recorded 2026-09-30 as a docs gap for their owning controllers; this chapter and ISO 27001 Conformance are corrected in this unit |

**Governing source.** This chapter's enforcement table; DEC-5b760c; DEC-f0c0f7.

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| DevHub | The `qa_nc_records` table, the `/api/qa/nc` routes and the `devhub_qa_nc_*` tools; the Guards page rule scan | The register's role as the single non-conformance authority and its current state |
| Build and Release; Continuous Integration | The CI workflows as build procedure; the CodeArtifact registry through which the shared configuration installs | The quality gates those workflows enforce and at what level |
| Decision and Change Procedure | The change-record trail that `session_ref` and `commit_ref` link to | The non-conformance register as a parallel trail |
| ISO 27001 Conformance | The conformance mapping (A.8.8 technical vulnerabilities, A.8.25 secure development, A.8.28 secure coding, A.8.32 change management) | The enforcement those clauses cite |
| InfoSec and Access Control | The access-control surfaces | Nothing at commit time: the developer-machine hook it once cited is gone |
| Operating Model | The evaluation runtime whose code lives under `src/boundary` | The stricter rules and the architecture gates that bind there |

**Governing source.** The Authority Model.

## References

- The Authority Model
- DevHub
- Build and Release
- Continuous Integration
- Decision and Change Procedure
- ISO 27001 Conformance
- InfoSec and Access Control
- DEC-5b760c (QA enforcement consolidates into per-repo CI; DevHub is the sole NC authority; bc-qa retires)
- DEC-ee6018 (Power of Ten, adapted coding rules)
- DEC-f0c0f7 (No hardcoded enums)
- `bc-core/tools/eslint-config/eslint/` (the executable rule set)
- `bc-core/src/__architecture__/` (the architecture gates)
