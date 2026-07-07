---
id: build-and-release
order: 40
title: "Build and Release"
status: drafting
authority: authoritative
depends_on: [the-authority-model, devhub, infrastructure, deployment-topology]
governing_sources:
  - The Authority Model
  - Infrastructure
  - Deployment Topology
governing_adrs:
  - DEC-890417 (pm2 service supervisor; superseded; the as-built model starts each service independently in its own repo)
  - DEC-1918d0 (Two-database split; the platform plus tenant DB topology that bc-core seeds)
  - DEC-e50b83 (Port reservation; build outputs run against reserved ports)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Build and Release

## Scope

This chapter records the build-and-release substrate for the BareCount platform: how each repo installs dependencies, how each service starts in development, what each repo builds when a release-candidate artifact is required, and what the readiness-baseline release path is. It records the CodeArtifact npm registry as the dependency-resolution surface, the per-repo development-server commands, the per-repo build outputs, the renewal procedure for the CodeArtifact authentication token, the docker compose substrate that bc-core consumes locally, the canonical DDL and the migrations directory, the seed scripts that initialize the registry, and the as-built gaps in continuous integration and formal release tooling.

This chapter does not name specific port numbers, AWS account identifiers, AWS region codes, AWS profile names, or IAM role ARNs. Those deploy coordinates are owned by Infrastructure (the as-deployed surface) and Deployment Topology (the operational topology). Per pattern 85, this chapter records the procedure shape and routes the deploy-coordinate detail to those owning chapters.

This chapter also does not redefine the engineering session protocol (Decision and Change Procedure) or the QA gate substrate (Quality Assurance).

**Governing source.** outline.md §4.5; The Authority Model.

## CodeArtifact as the npm Registry

Every BareCount repo that consumes npm dependencies routes installs through AWS CodeArtifact. The CodeArtifact mirror caches every package the platform has ever installed; npmjs.org sits behind the mirror, but the mirror is the immediate dependency source. Per the platform's risk register, this is a supply-chain control: every install is recorded in CodeArtifact, every dependency is reproducible from the mirror.

| Repo | `.npmrc` | Notes |
|---|---|---|
| `barecount-devhub` | Yes | Routes installs through CodeArtifact |
| `bc-core` | Yes | Routes installs through CodeArtifact |
| `bc-portal` | Yes | Routes installs through CodeArtifact (npm workspaces; the workspace `.npmrc` covers the apps under it) |
| `bc-admin` | Yes | Routes installs through CodeArtifact |
| `bc-qa` | Yes | Routes installs through CodeArtifact (publishes the `@barecount/eslint-config` package back to CodeArtifact) |
| `bc-ai` | Not applicable | Python service; pip-based dependency resolution; not part of npm registry routing |
| `bc-docs` | Not applicable | Markdown-only; no runtime dependencies |

The `.npmrc` files are committed; the registry URL embeds an AWS account identifier and a region code that are deploy coordinates owned by Infrastructure. The per-repo file points at the same domain and repository so that every repo resolves against the same cached package set.

The authentication token has a twelve-hour TTL. After the TTL elapses, `npm install` returns 401 or 403 against the registry. The renewal command runs through the AWS CLI; the wrapper script lives at `barecount-devhub/scripts/codeartifact-refresh.js` and is exposed as `npm run codeartifact:refresh`. The renewal command's domain, repository, region, and AWS profile are deploy coordinates owned by Infrastructure; the procedure is operator-driven (the wrapper is invoked manually when an install fails).

**Governing source.** Infrastructure (CodeArtifact deploy coordinates); CLAUDE.md (NPM Registry section).

## Per-Repo Development Server

Per `DEC-890417` superseded, the platform does not orchestrate services through a supervisor. Each service starts independently in its own repo with its own development command. The platform-wide rule is "start only what the session needs."

| Repo | Command | Watch substrate |
|---|---|---|
| `barecount-devhub` | `npm run dev` (`node --watch src/index.js`) | Node `--watch` for HMR |
| `bc-core` | `npm run start:dev` (`nest start --watch`) | NestJS `--watch` via SWC |
| `bc-portal` | `npm run dev` (delegates to the workspace's web app `vite`) | Vite HMR |
| `bc-admin` | `npm run dev` (`vite`) | Vite HMR |
| `bc-ai` | `python -m uvicorn main:app` (the Python service has no npm dev script) | Uvicorn auto-reload |
| `bc-qa` | None (no runtime; tooling-only repo) | Not applicable |
| `bc-docs` | None (markdown-only); the bc-admin reader renders chapters via Vite HMR after `bc-admin/scripts/sync-docs.js` runs | Indirect (through bc-admin's HMR) |

The deprecated `ecosystem.config.cjs` files for pm2 are still committed in `barecount-devhub` and `bc-ai` as historical reference per pattern 71. They are marked deprecated in their own headers and are not consumed by the as-built path.

**Governing source.** CLAUDE.md (Dev Service Management section); per-repo `package.json`.

## Build Outputs

Three repos build runtime artifacts. The remaining repos either ship source (markdown, shell scripts, eslint configs) or run as Python (no npm build path).

| Repo | Build command | Output |
|---|---|---|
| `bc-core` | `npm run build` (`nest build`) | `dist/` (NestJS standard) |
| `bc-portal` | `npm run build` (delegates to the workspace web app's `vite build`) | `apps/web/dist/` (Vite standard) |
| `bc-admin` | `npm run build` (`vite build`) | `dist/` (Vite standard) |
| `barecount-devhub`, `bc-qa`, `bc-docs` | Not defined | Source-shipped repos |

Type-check and lint commands are repo-local. `bc-core` exposes both `npm run typecheck` (`tsc --noEmit`) and `npm run lint` (`eslint .` plus a column-name lint). `bc-admin` exposes `npm run typecheck`. `bc-portal` and `barecount-devhub` rely on the pre-commit hook for lint enforcement; per-repo CLI lint commands are not standardized.

**Governing source.** Per-repo `package.json`; Quality Assurance (lint surface).

## Docker Compose for bc-core

bc-core consumes a docker compose substrate for the local PostgreSQL and Redis services. The compose file declares two services and three init scripts.

| Substrate | Container image (family) | Init payload |
|---|---|---|
| PostgreSQL | postgres 17.x alpine | `01-platform-schemas.sql`, `02-platform-tables.sql`, `03-tenant-db.sql` (the canonical DDL) |
| Redis | redis 7.x alpine | None (cache; no init payload) |

The container image versions, the host-port mappings, and the data-volume layout are deploy coordinates owned by Infrastructure. This chapter records that compose is the local-development substrate and that the canonical DDL is the init payload; the operational topology is owned by Deployment Topology.

The canonical DDL lives at `bc-core/docker/redesign/`. Per `DEC-1918d0`, the platform-DB DDL is split across seventeen files under `02-platform-tables/` (one per concern: master, source, contract, metric, runtime, tenant, users, operations, execution, pricing, infrastructure, support, deferred-fks, test-bench, date-dim, fiscal-calendar, plus an aggregator); the tenant-DB DDL is `03-tenant-db.sql`; an aggregator `02-platform-tables.sql` references the seventeen-file set. The migrations directory `bc-core/docker/redesign/migrations/` carries forty-two evolution files in `YYYYMMdd-descriptor.sql` plus paired `.revert.sql` form. Per CLAUDE.md, the migrations directory contains thirty-six tables that have not yet been folded back into the canonical files; the fold-back is `TSK-cc631d` in DevHub.

**Governing source.** `bc-core/docker/redesign/`; DEC-1918d0; Infrastructure.

## Drizzle and the Schema Surface

bc-core's Drizzle schema mirrors the canonical DDL. The Drizzle config at `bc-core/drizzle.config.ts` declares the schema directory, the dialect, and the migration output directory. The Drizzle migrations are not the canonical DDL; the canonical DDL is the docker-init payload. Drizzle is the type surface that the application uses to query the database; the canonical DDL is what the database actually contains.

When the canonical DDL evolves, the Drizzle schema is updated in the same change. When the two diverge, the canonical DDL wins and the Drizzle schema is corrected to match.

**Governing source.** `bc-core/drizzle.config.ts`; CLAUDE.md (Database Change Protocol section).

## Seed Scripts

`barecount-devhub` exposes `npm run seed` which invokes `scripts/seed.js`. The seed script populates the DevHub SQLite registry with the project list, the seeded ADR registry, and the initial document index after a clean checkout.

`bc-core` does not expose `npm run seed`. The bc-core registry is initialized through the docker compose init payload (the canonical DDL is sufficient to bring the schema online); business catalog seeding (the source catalog, business field catalog, metric seed catalog) is owned by the governed onboarding sequences in Onboarding, not by a `seed` script.

**Governing source.** `barecount-devhub/scripts/seed.js`; Onboarding section (governed catalog procedures).

## CodeArtifact Token Renewal

The CodeArtifact token expires every twelve hours. After expiry, every `npm install` call returns 401 or 403 against the registry. The renewal command is operator-driven.

| Aspect | Form |
|---|---|
| Renewal command | `npm run codeartifact:refresh` from `barecount-devhub` (the wrapper at `scripts/codeartifact-refresh.js`) |
| Underlying invocation | `aws codeartifact login --tool npm --domain {domain} --repository {repo} --region {region}` (the domain, repository, region, and AWS profile are deploy coordinates owned by Infrastructure) |
| Trigger | Manual; the operator runs renewal when an install fails with 401 or 403 |
| Discipline | Per CLAUDE.md, the registry routing is mandatory; never override `.npmrc` to point at npmjs.org |

The token TTL is a known operational constraint; per the drift inventory below, an automated renewal cron is queued.

**Governing source.** `barecount-devhub/scripts/codeartifact-refresh.js`; Infrastructure.

## Continuous Integration and Release Tooling

The platform does not run continuous-integration automation in the readiness baseline. The verified repos sampled for this chapter do not carry `.github/workflows/` content.

| Repo | `.github/workflows/` | Status |
|---|---|---|
| `barecount-devhub` | Not present | No CI |
| `bc-core` | Not present | No CI |
| `bc-portal` | Not present | No CI |
| `bc-admin` | Not present | No CI |
| `bc-ai` | Not present | No CI |
| `bc-qa` | Not present | No CI; the audit harness is intended for CI integration but is not yet wired |
| `bc-docs` | Not present | No CI; the ADR audit script is operator-run |

The QA hooks (Quality Assurance) run pre-commit at the developer machine; the bc-qa audit harness runs on demand via the `devhub_qa_audit` MCP tool or the `bash bc-qa/audits/audit-repo.sh` CLI. The transition from local-only enforcement to CI-integrated enforcement is queued as drift; the gate-bash wrapper `bc-qa/gates/compliance-gate.sh` exists as the integration point but is not invoked from a CI workflow in the readiness baseline.

The platform also does not use a formal release tool in the readiness baseline. No semantic-release configuration, no changesets manifest, no release manifest live in any repo. Per-repo `package.json` carries a static `version` field that is set by hand. The readiness-baseline release path is "the artifact runs locally; a deploy is recorded in Infrastructure when it happens."

**Governing source.** `bc-qa/gates/compliance-gate.sh` (the gate wrapper that exists for CI integration); CLAUDE.md (QA Tooling section).

## Constraints

| Constraint | Form |
|---|---|
| CodeArtifact mandatory | Every install routes through CodeArtifact; `.npmrc` overrides to npmjs.org are disallowed per CLAUDE.md |
| Per-repo independence | Each service starts in its own repo; no platform-wide supervisor |
| Canonical DDL is authority | The bc-core canonical DDL under `docker/redesign/` is the schema authority; Drizzle schemas track the canonical DDL; migrations drift back into the canonical DDL on the fold-back schedule |
| Database changes are gated | Per CLAUDE.md, every database change requires explicit user approval; this constraint binds Build and Release because schema-evolution releases run through the same governance |
| Token renewal is operator-driven | The CodeArtifact token window is renewed manually; no automated renewal cron is wired |
| No CI in the readiness baseline | Quality enforcement runs at developer pre-commit and at on-demand audit; no GitHub Actions workflows |
| Static `version` fields | Per-repo `package.json` carries a hand-set `version` field; no formal release tool |

**Governing source.** CLAUDE.md (NPM Registry, Database Change Protocol, Don't sections); per-repo `package.json` and `.npmrc`.

## Failure Modes

| Failure | Behavior |
|---|---|
| `npm install` returns 401 or 403 | Token expired; operator runs `npm run codeartifact:refresh` and retries |
| `npm install` cannot reach CodeArtifact | Operator inspects network; the registry is not optional, so falling back to npmjs.org is not authorized; the operator surfaces the outage to Infrastructure |
| `nest build` or `vite build` fails | Operator inspects the type or lint error; the failure is local; no CI to surface it broadly |
| Docker compose cannot start the postgres or redis containers | Operator inspects the compose log; the schema-init payload may be at fault; the operator either fixes the SQL or reverts to the prior commit |
| Schema migration breaks the canonical DDL state | Per CLAUDE.md the database change protocol blocks unapproved DB changes; an unapproved migration that lands is treated as a discipline violation; the rollback path is the prior canonical state |
| Drizzle schema diverges from canonical DDL | The data-dictionary generator (Documentation System) reads the live database and surfaces the divergence as a drift item |
| `npm run seed` writes against a stale schema | Operator drops the SQLite file and reruns from a clean checkout; the seed script tolerates a fresh-from-empty initialization |
| Twelve-hour TTL elapses mid-deploy | The deploy that consumes the registry fails; operator renews and retries; deploys plan around the TTL by renewing as part of the operator's start-of-session procedure |

**Governing source.** CLAUDE.md (Database Change Protocol, Don't sections); Infrastructure (deploy coordinates).

## Drift Inventory

| Drift item | Status |
|---|---|
| No CI test workflows in any repo | Recorded; the gate-bash wrapper at `bc-qa/gates/compliance-gate.sh` is the integration point when CI lands |
| No formal release tool | Recorded; per-repo `version` fields are hand-set; semantic-release, changesets, or a release manifest are queued |
| `bc-core` has no `npm run seed` script | Recorded; the docker init payload is the canonical seeding path; business catalog seeding is owned by the governed onboarding sequences |
| `bc-core` migrations directory carries thirty-six tables not folded back into canonical DDL | Recorded as `TSK-cc631d` in DevHub |
| Deprecated pm2 `ecosystem.config.cjs` files still committed | Recorded; the files are marked deprecated in their own headers and are not consumed; they remain as historical reference per pattern 71 |
| CodeArtifact token renewal is manual | Recorded; an automated renewal cron is queued |
| `npm run lint` and `npm run typecheck` are not standardized across repos | Recorded; bc-core and bc-admin carry lint commands; bc-portal and barecount-devhub rely on the pre-commit hook |
| The `bc-qa/gates/compliance-gate.sh` wrapper exists but is not invoked from any CI | Recorded; ready for adoption when CI lands |

**Governing source.** CLAUDE.md (QA Tooling, Don't sections); per-repo `package.json`.

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| Infrastructure | The as-deployed AWS substrate, including CodeArtifact deploy coordinates (account, region, profile, domain, repository), reserved ports, and IAM | The build-side procedure that consumes those coordinates |
| Operations: Deployment Topology | The operational topology of the deployed platform; the per-environment substrate; the deploy procedure as run by Operations | The build-side artifact that Operations deploys |
| Quality Assurance | The bc-qa repository, the audit harness, the gate-config, and the eslint-config package | The build-side commands that consume the QA tooling |
| Documentation System | The bc-docs SSOT and the bc-admin reader build path through `bc-admin/scripts/sync-docs.js` | The sync-docs script as a build-time procedure that produces the manifest the bc-core docs endpoints serve |
| Decision and Change Procedure | The session protocol and the change-record substrate that govern release-bearing changes | The build-side commands that release-bearing changes invoke |

**Governing source.** outline.md §4.5; The Authority Model.

## References

- The Authority Model
- Infrastructure
- Operations: Deployment Topology
- Quality Assurance
- Documentation System
- Decision and Change Procedure
- DEC-890417 (pm2 service supervisor; superseded)
- DEC-1918d0 (Two-database split)
- DEC-e50b83 (Port reservation)
- CLAUDE.md (NPM Registry, Dev Service Management, Database Change Protocol, Don't sections)
