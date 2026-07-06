# Initial v3 Inventory

Run: `1`
Completed: `2026-07-06 07:33:02`

This report is generated from the v4 SQLite control database. It inventories `bc-docs-v3` as read-only source material; it does not migrate or edit source content.

## By Top-Level Directory

| Directory | Files |
|---|---:|
| `adrs` | 471 |
| `ai` | 7 |
| `api` | 1 |
| `assets` | 1 |
| `compliance` | 6 |
| `data-dictionary` | 21 |
| `development` | 9 |
| `errata` | 8 |
| `foundation` | 10 |
| `glossary` | 1 |
| `implementation` | 234 |
| `onboarding` | 90 |
| `operating-model` | 23 |
| `operations` | 26 |
| `overview` | 2 |
| `schemas` | 1 |
| `source-systems` | 61 |

## By Guessed Kind

| Kind | Files |
|---|---:|
| `adr` | 471 |
| `current_chapter_candidate` | 222 |
| `evidence_dbcp` | 72 |
| `evidence_work_record` | 64 |
| `source_system_reference` | 61 |
| `evidence_closeout` | 36 |
| `generated_or_curated_reference` | 24 |
| `evidence_audit` | 10 |
| `errata` | 8 |
| `evidence_ledger` | 3 |
| `archive_candidate` | 1 |

## Frontmatter Coverage

| Has Frontmatter | Files |
|---|---:|
| yes | 963 |
| no | 9 |

## Link Risk Snapshot

| Scope | Links | Missing/Flagged |
|---|---:|---:|
| `internal` | 1407 | 125 |
| `external_url` | 25 | 0 |
| `mcp` | 14 | 0 |
| `absolute_local` | 14 | 14 |

## Next Decisions

- Tune classification rules before copying any prose.
- Mark current chapters versus evidence/archive candidates.
- Regenerate API, schema, and data-dictionary references from source code instead of migrating stale generated pages.
- Keep `bc-docs-v3` untouched until final cutover.
