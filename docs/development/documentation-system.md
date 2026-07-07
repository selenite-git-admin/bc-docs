---
id: documentation-system
order: 42
title: "Documentation System"
status: drafting
authority: authoritative
depends_on: [the-authority-model, devhub, decision-and-change-procedure, audit-and-activity-logging, api-surface, frontend-experience]
governing_sources:
  - The Authority Model
  - DevHub
  - Decision and Change Procedure
  - Audit and Activity Logging
governing_adrs:
  - DEC-3395bc (bc-docs SSOT cutover; flat layout under docs/; ADR files written into docs/adrs/; bc-core JWT-served document endpoints)
  - DEC-b97390 (bc-admin embedded reader is canonical; reader fetches manifest, markdown, and assets from bc-core; URL uglification rejected)
  - DEC-c06f41 (Spine expansion to eight sections plus a home; Implementation reshape; section-overview discipline)
  - DEC-a4e550 (ADR-First Decision Workflow; the ADR file is SSOT)
  - DEC-623f8f (ADR Hygiene Policy; the eight rules that govern the ADR file content lifecycle)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Documentation System

## Scope

This chapter records the platform's documentation system: the bc-docs SSOT repository as the single source of truth, the bc-admin embedded reader as the canonical reader surface, the bc-core JWT-served document endpoints that the reader fetches against, the bc-admin sync-docs script as the manifest builder that bridges the SSOT to the reader, the data-dictionary generator that introspects the live PostgreSQL state, the DevHub document scanner as the derived registry index, the diagram-rewrite script and the section-numbering migration script as authoring aids, and the as-built drift in section coverage and reference-material generation.

This chapter does not redefine the ADR-first procedure (Decision and Change Procedure), the reader-side audit trail (Audit and Activity Logging records the docs JSONL trail and AuditService caller wiring), or the bc-core API surface that hosts the document endpoints (API Surface).

**Governing source.** outline.md §4.5; DEC-3395bc; DEC-b97390.

## bc-docs as the SSOT

Per `DEC-3395bc`, bc-docs is the documentation source of truth. Filesystem layout plus YAML frontmatter authority is the discipline; nothing else is consulted as the authoritative content.

| Property | Form |
|---|---|
| Repository path | `C:\MyProjects\bc-docs` (the platform's developer-machine path; the deployed path is owned by Infrastructure) |
| Layout | Flat under `docs/`: section folders (`foundation`, `operating-model`, `implementation`, `ai`, `development`, `onboarding`, `operations`, `compliance`), top-level governance peers (`adrs`, `errata`), and assets (`data-dictionary`, plus future generated reference materials) |
| Authority axis | Each chapter's frontmatter `authority` field declares whether the chapter is `authoritative`, `reference`, or `evidentiary` |
| Status axis | Each chapter's frontmatter `status` field declares `drafting`, `reviewing`, `locked`, `superseded`, or `retired`; binding force requires `authority: authoritative` plus `status: locked` |
| Naming | Chapter filenames are slugs (no `ch-NN-` prefix); section directories are slugs; ADR filenames are `ADR-{uid}.md`; errata filenames are `FND-ERR-XXX.md` |

The legacy `legacy v2 archive` archive at `legacy-v2-docs-root` is read-only reference. New ADRs land in v3, not v2; new chapters land in v3, not v2. v2 remains as a historical record until the SOPs and reference materials are migrated.

The repository carries an `outline.md` that records the section structure, the chapter list, the voice discipline, and the editorial gates. The outline is authoritative for the framework; the chapter is authoritative for its content.

**Governing source.** DEC-3395bc; bc-docs `outline.md`; bc-docs `HANDOFF.md`.

## The bc-admin Embedded Reader

Per `DEC-b97390`, the bc-admin embedded reader is the canonical reader surface. The reader is mounted in the bc-admin frontend; an operator with platform-scope authentication navigates to the docs route and reads the chapters in the same chrome that hosts the rest of the admin surface.

| Property | Form |
|---|---|
| Mount | The bc-admin React app exposes a docs route; the reader component is hosted under that route |
| Manifest fetch | The reader fetches the document manifest from the bc-core endpoint at app load |
| Chapter fetch | The reader fetches markdown for the selected chapter from a per-file endpoint |
| Asset fetch | The reader fetches diagram SVGs and other assets from a per-asset endpoint |
| Authentication | Every fetch carries the operator's Cognito-issued JWT; the reader does not anonymize requests |
| Hot reload | During development the bc-admin Vite HMR detects markdown changes (after sync-docs.js runs) and hot-reloads the rendered chapter |

The reader is the canonical surface; ad-hoc Markdown viewers in the developer's editor render approximately the same content but are not the reference rendering. Diagram label rewriting, frontmatter-driven section ordering, and chapter cross-link resolution are reader concerns.

URL uglification was rejected at `DEC-3395bc` review as security-through-obscurity; the chapter URLs are predictable. Anti-scraping protection runs on the bc-core side: rate limiting per Cognito subject, structured JSONL audit logging, an invisible Markdown watermark, and a private cache header.

**Governing source.** DEC-b97390 (bc-admin embedded reader); DEC-3395bc (anti-scraping mechanism).

## bc-core JWT-Served Document Endpoints

Per `DEC-3395bc`, bc-core exposes three endpoints that the bc-admin reader consumes. The endpoints are JWT-guarded and rate-limited; they serve content from a `private-docs/` directory that is gitignored and populated by `bc-admin/scripts/sync-docs.js`.

| Endpoint | Purpose |
|---|---|
| `GET /api/docs/manifest` | Returns the manifest of all sections, chapters, collections, and assets |
| `GET /api/docs/file/*splat` | Returns Markdown content for a chapter or governance file |
| `GET /api/docs/asset/*splat` | Returns SVG, PNG, or other asset bytes |

The endpoints are decorated with `@PlatformOnly()` (the JWT guard that requires platform-scope authentication, no tenant header). The `*splat` syntax is NestJS 11 wildcard-route notation; the segment after `file/` or `asset/` is captured and resolved against the `private-docs/` root.

The anti-scraping discipline runs on the controller:

| Mechanism | Form |
|---|---|
| Rate limit | Per Cognito subject; sixty per minute, one thousand per day |
| Audit log | JSONL line per docs response; the JSONL trail is consumed by the operational-log substrate |
| AuditService caller | `DocsController` calls `auditService.append` per Audit and Activity Logging |
| Markdown watermark | An invisible per-request marker is woven into the Markdown response so that scraped content is traceable to the requesting subject |
| Cache header | `Cache-Control: private, max-age=0, no-store` so that cached copies do not leak across users |

The DB-backed access log and the `@nestjs/throttler` package are queued; the current rate-limit and audit substrates are in-memory and JSONL respectively.

**Governing source.** DEC-3395bc (anti-scraping mechanism); `bc-core/src/docs/docs.controller.ts`; Audit and Activity Logging.

## The sync-docs Manifest Builder

`bc-admin/scripts/sync-docs.js` is the build-time bridge between bc-docs and bc-core. The script reads the SSOT, walks every chapter and asset, generates a manifest, and writes the manifest plus the source files into bc-core's `private-docs/` directory.

| Step | Form |
|---|---|
| Source root | Read from environment `BC_DOCS_ROOT` or default to the local bc-docs repo path |
| Sync target | Read from environment `BC_CORE_PRIVATE_DOCS` or default to the bc-core sibling path's `private-docs/` directory |
| Section labels | The script's `SECTION_LABELS` table records the section slug to title mapping; the table enumerates the eight top-level sections and the home overview |
| Collection labels | The `COLLECTION_LABELS` table records the top-level governance and reference collections (ADRs, errata, data-dictionary, glossary, API, schemas, and source systems) |
| Manifest shape | The output manifest carries section list, per-section chapter list, per-chapter frontmatter excerpt, and the asset inventory |
| Output | The manifest writes alongside the copied chapters and assets in `private-docs/` |

The script must be re-run after a chapter is added, removed, or renamed. The bc-admin Vite HMR detects the resulting file change and the reader updates without a full reload. Per pattern 81: the `SECTION_LABELS` table is the source-of-truth for which sections the reader knows about; a section folder created in bc-docs without a corresponding `SECTION_LABELS` entry does not surface in the reader.

**Governing source.** `bc-admin/scripts/sync-docs.js`; DEC-b97390.

## The Data-Dictionary Generator

`bc-docs/scripts/generate-data-dictionary.mjs` produces the data-dictionary reference under `docs/data-dictionary/` by introspecting the live PostgreSQL state. The generator is the authoritative inventory of every table, every column, every index, and every foreign-key constraint as the database actually carries them.

| Property | Form |
|---|---|
| Connection | Two PostgreSQL connection strings: the platform DB and the tenant DB; both default to the local Docker compose substrate; both can be overridden by environment variables |
| Introspection sources | `pg_catalog` and `information_schema` for tables, columns, indexes, FK constraints, types, defaults, and comments |
| Output | One Markdown file per schema under `docs/data-dictionary/`, plus a `README.md` index |
| Rationale | Per pattern 71, the introspection is behavior-grounded: the generator reads what the database contains, not what the DDL files declare; the canonical DDL and the migrations directory may carry drift that the live state resolves |
| Cadence | Operator-run in the readiness baseline; no cron schedule |

The generator is the reference inventory; the chapter (Data Model and Schema) is the authority for the rationale and the design intent. Per pattern 67: chapters describe; references enumerate.

**Governing source.** `bc-docs/scripts/generate-data-dictionary.mjs`; Data Model and Schema.

## DevHub Document Scanner

DevHub maintains a derived `documents` registry by walking bc-docs and reading frontmatter. The scanner is on-demand: `devhub_doc_scan` rebuilds the registry; `devhub_doc_list`, `devhub_doc_get`, `devhub_doc_update`, `devhub_doc_link_ref`, and `devhub_doc_validate` are the subsequent read and mutate tools.

| Aspect | Form |
|---|---|
| Source path | Environment `BC_DOCS_PATH` if set; otherwise the configured bc-docs path |
| Walk | Filesystem recursive walk of `docs/`; every Markdown file is considered |
| Metadata extracted | `id` and `title` from frontmatter; `type` and `domain` derived from the file path; `authority`, `status`, `governing_adrs`, `errata_referenced` from frontmatter |
| Cadence | Operator-run; the boot output's "AUTO-SCAN" line is informational, not a re-scan trigger |

Per pattern 81: the DevHub document registry is a derived index, not the authoritative content. The chapter file is the authority; the registry is the navigation aid. When the registry contradicts the file, the file wins and the registry is rescanned.

**Governing source.** `barecount-devhub/src/lib/doc-scanner.js`; CLAUDE.md (Documentation section).

## ADR Authoring through DevHub

Per `DEC-a4e550` and as recorded in Decision and Change Procedure, the `devhub_decision_record` MCP tool both inserts the registry row and writes the ADR file to `bc-docs/docs/adrs/`. The Documentation System chapter records the file-write side: the ADR file is canonical content, the registry row is metadata, and the ADR audit script `bc-docs/scripts/adr-audit.js` is a pure-diagnostic over the file content.

The ADR file's frontmatter carries `uid`, `title`, `description`, `status`, `date`, `project`, `domain`, plus optional `subdomain`, `focus`, `supersedes`, and `superseded_by`. The body's conventional sections are Context, Decision, and Consequences. Per `DEC-623f8f`, the eight ADR hygiene rules govern the file-content lifecycle (Decision and Change Procedure records the rules; Documentation System records the file shape).

**Governing source.** DEC-a4e550; DEC-3395bc; Decision and Change Procedure.

## Errata Registry

Errata are first-class governance peers under `docs/errata/`. Each erratum has a six-character UID like `FND-ERR-XXX.md` and records a Foundation contradiction or correction. The errata are referenced from chapter frontmatter (`errata_referenced` field) and from body prose with the bare UID.

The errata registry is a small, slow-growing surface. Per `DEC-3395bc`, the errata sit as peers to the section directories; they are not nested under a `reference/` wrapper.

**Governing source.** DEC-3395bc; `bc-docs/docs/errata/`.

## Diagram Substrate

Diagrams live at `bc-docs/docs/assets/diagrams/`. Source format is SVG; filenames follow the `DG-{slug}.svg` convention; chapter body references use absolute paths (`/docs/assets/diagrams/DG-{slug}.svg`).

| Property | Form |
|---|---|
| Active diagrams | The four architectural diagrams (`DG-architecture-conceptual`, `DG-architecture-layers`, `DG-architecture-two-db`, `DG-architecture-composition`) plus four Foundation-and-Operating-Model diagrams (`DG-binding-chain`, `DG-catalog-hierarchy`, `DG-evaluation-boundaries`, `DG-object-model`) |
| Deferred diagrams | A `_deferred/` subdirectory holds diagrams that need a structural redraw before they reach the active set |
| Label rewriting | `bc-docs/scripts/diagram-rewrite.mjs` carries per-diagram label substitution rules; the script is idempotent |
| Bidirectional declaration | Per outline §2.13: every chapter that body-references a diagram declares it in frontmatter `diagrams:`, and every frontmatter-declared diagram is referenced in body |
| Authoring aid | Prose is the spec; the diagram is the navigation aid; when prose and diagram disagree, prose wins and the diagram is redrawn |

**Governing source.** outline.md §2.13; `bc-docs/scripts/diagram-rewrite.mjs`.

## Voice and Editorial Discipline

The documentation's voice is governed by `bc-docs/scripts/reference/aws-rewrite-checklist.md`. The checklist records the AWS-style register, the forbidden vocabulary, the section pattern (six elements for behavior, seven for components), the bidirectional frontmatter discipline, and the per-chapter pattern set that has accumulated through founder cold-reads.

| Discipline | Form |
|---|---|
| Forbidden roots | `pipeline`, `ingest`, `transform`, `materialize`, `flow`, `stage`, `job`, `refresh`, `recompute`, `process`; carve-outs for DAG-direction terms on declared chains and for protocol-vocabulary identifiers |
| Em dashes | Zero in titles, headings, and body prose; commas, colons, periods, semicolons, or parentheses substitute |
| Section numbering | None in chapter titles, headings, or cross-references; chapters are name-keyed; only frontmatter `order` provides sort stability |
| Bidirectional frontmatter | Every `DEC-xxxxxx` and `FND-ERR-xxx` cited in body appears in `governing_adrs` or `errata_referenced`, and vice versa |
| Citation discipline | Each substantive section ends with a `Governing source.` footer; queued chapters are not cited as governing source |
| Pre-commit grep | Operator runs the lint regex before committing a chapter |

The pattern set evolves with each founder cold-read. New patterns are extracted into the checklist; the running count is the live count. The discipline is "patterns are earned, not invented"; a pattern is added when a real cold-read surfaces a real drift that the checklist does not yet catch.

**Governing source.** `bc-docs/scripts/reference/aws-rewrite-checklist.md`; outline.md §2.

## Constraints

| Constraint | Form |
|---|---|
| Single SSOT | bc-docs is the only authoritative content store; legacy v2 archive is read-only archive |
| Canonical reader is bc-admin | The bc-admin embedded reader is the reference rendering; ad-hoc Markdown viewers are not |
| Reader fetches through bc-core | The reader does not read bc-docs directly; it fetches through the JWT-guarded bc-core endpoints |
| sync-docs is the bridge | bc-core does not read bc-docs directly; the sync-docs script populates bc-core's `private-docs/` directory |
| Frontmatter is bidirectional | The bidirectional discipline binds every chapter |
| Voice is grep-checked | The forbidden-roots regex passes before commit |
| Per-section ordering is frontmatter-driven | Section folders carry chapters whose `order` field provides sort stability |
| Naming has no numbers | No `ch-NN-` prefix in filenames; no `Chapter N.` prefix in titles |

**Governing source.** DEC-3395bc; DEC-b97390; outline.md §2.

## Failure Modes

| Failure | Behavior |
|---|---|
| Chapter file frontmatter malformed | DevHub doc scanner skips the file with a warning; the chapter does not surface in the registry until the frontmatter parses |
| sync-docs cannot reach bc-core's `private-docs/` directory | Operator confirms the bc-core sibling path or sets `BC_CORE_PRIVATE_DOCS`; the sync fails until the path resolves |
| bc-core docs endpoint returns 401 | Operator confirms the JWT (Cognito session) is current; the reader prompts for re-authentication |
| Rate limit exceeded | bc-core returns 429; the JSONL trail records the rejection per Audit and Activity Logging |
| ADR file missing for a registry row | Next `devhub_doc_scan` flags the row; operator either rewrites the ADR or removes the registry row through the patch path |
| sync-docs `SECTION_LABELS` does not include a new section | The new section's chapters do not surface in the reader; operator amends the table and re-runs |
| Diagram referenced in body but not declared in frontmatter | The bidirectional check at commit time flags the gap |
| Data-dictionary generator cannot reach the postgres container | Generator exits with an error; operator confirms compose is running and reruns |
| Chapter cites a `DEC-xxxxxx` UID that does not exist in `docs/adrs/` | Pre-commit ADR-existence sweep flags the missing file; operator either writes the ADR or removes the citation |

**Governing source.** `bc-admin/scripts/sync-docs.js`; `bc-core/src/docs/docs.controller.ts`; `barecount-devhub/src/lib/doc-scanner.js`.

## Drift Inventory

| Drift item | Status |
|---|---|
| `private-docs/` rate limit and audit log are in-memory and JSONL respectively | Recorded; DB-backed access log and `@nestjs/throttler` are queued per `DEC-3395bc` deferral |
| Markdown watermark mechanism is per `DEC-3395bc` | Recorded; the invisible-marker scheme is named in the ADR; per-line wiring lives in the docs service module |
| SOPs not yet migrated from legacy v2 archive | Recorded; SOP Index reference material is queued per outline §4.9 |
| Screen Registry generator is queued | Recorded as `TSK-416138`; deferred until both frontends stabilize |
| API Reference generator is queued | Recorded; the DevHub API scanner will produce the inventory; the chapter (API Surface) is the rationale authority |
| Glossary, Diagram Index, Contract Schemas references are queued | Recorded as future top-level peers under `docs/` |
| sync-docs `SECTION_LABELS` table requires manual amendment when a new section folder is added | Recorded; the amendment lands in the same change as the section's first chapter |
| ADR audit script `bc-docs/scripts/adr-audit.js` is operator-run | Recorded; the monthly cron is queued per `DEC-623f8f` rule four |

**Governing source.** outline.md §4.9; bc-docs `HANDOFF.md`.

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| Decision and Change Procedure | The ADR-first procedure, the eight ADR hygiene rules, the change-record substrate | The file-shape and the v3 layout that those decisions land into |
| DevHub | The MCP tool surface and the document registry table | The scanner that builds the registry and the tools that read or mutate it |
| Audit and Activity Logging | The DevHub activity log; the JSONL docs trail; the AuditService caller wiring at `docs.controller.ts` | The docs-side audit emission and the per-Cognito-subject rate-limit substrate |
| API Surface | The bc-core API endpoints and the per-endpoint contract | The three docs-specific endpoints (`/api/docs/manifest`, `/api/docs/file/*splat`, `/api/docs/asset/*splat`) as a documented bc-core surface |
| Data Model and Schema | The platform DB and tenant DB schemas | The data-dictionary generator that introspects those schemas as the inventory reference |
| Frontend Experience | The bc-admin and bc-portal frontends | The bc-admin docs route as one surface within the bc-admin frontend |

**Governing source.** outline.md §4.5; The Authority Model.

## References

- The Authority Model
- DevHub
- Decision and Change Procedure
- Audit and Activity Logging
- API Surface
- Data Model and Schema
- Frontend Experience
- DEC-3395bc (bc-docs SSOT cutover)
- DEC-b97390 (bc-admin embedded reader)
- DEC-c06f41 (Spine expansion to eight sections plus a home)
- DEC-a4e550 (ADR-First Decision Workflow)
- bc-docs outline.md (section structure, voice discipline, editorial gates)
- bc-docs HANDOFF.md (current drafting state and per-chapter workflow)
- `bc-docs/scripts/reference/aws-rewrite-checklist.md` (the voice patterns)

