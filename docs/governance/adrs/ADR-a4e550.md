---
uid: DEC-a4e550
title: "Documentation Registry in DevHub + Standard ADR File Format"
description: "DevHub tracks all bc-docs files with type/domain/freshness. ADR files in bc-docs are source of truth for decisions. DevHub is metadata registry only."
status: implemented
subdomain: doc-framework
focus: adr-file-format
date: 2026-03-26
project: bc-docs
domain: platform
refs:
  - type: document
    path: "architecture/database/schema-map.md"
    label: "Example document tracked by registry"
authority: authoritative
migrated_from: legacy v2 archive
---


# Documentation Registry in DevHub + Standard ADR File Format

## Context

docs.registry.json was a static file that drifted (~70% coverage after 3 weeks). DevHub already tracks decisions, tasks, sessions — adding documents completes the picture. Decisions stored as freeform text blobs lack context/options/consequences that the standard ADR format captures. UID-based filenames fix the D-number collision problem (15 duplicate codes). Cross-reference registry enables freshness tracking: if a decision is newer than a document's last_validated_date, the document is flagged possibly_stale. Same pattern applied to decisions themselves — if a decision supersedes another, the old one's status updates automatically.

## Decision

### 1. Document Registry in DevHub
Add a `document` table to DevHub that registers every file in bc-docs. DevHub becomes the metadata authority (what exists, type, applicability, freshness). bc-docs remains the content store (markdown files on disk). No more static docs.registry.json as source of truth.

### 2. Standard ADR File Format
All decisions are stored as markdown files in `bc-docs/architecture/decisions/DEC-xxxxxx.md` using standard ADR format: Context, Decision, Options Considered, Consequences, References. DevHub's decisions table keeps registry metadata + file_path pointer. Heavy text (decision_text, rationale_text) stops being written to DevHub — the file IS the content.

### 3. UID-Based Decision Filenames
Decision files use `DEC-xxxxxx.md` (UID), not `D001.md` (sequential code). D-number codes are optional labels, not identifiers. Eliminates the duplicate D-number collision problem (15 codes with duplicates in current system).

### 4. Document Types (engineering artifact taxonomy)
Documents classified by type: specification, component-ref, architecture, database, api, screen, decision, playbook, qa, reference, security, user-story, patent.

### 5. Applicability (project + domain)
Each document tagged with primary project (bc-core, bc-admin, bc-portal, platform) and primary domain (contracts, metrics, sources, readers, connectors, tenants, evidence, canonical, governance, subscription, admission, execution, auth, deployment).

### 6. Freshness Tracking
Each document has created_date, last_validated_date, validated_by_ref (SES-xxxxxx). Status lifecycle: unvalidated → fresh → possibly_stale → stale → retired. Auto-suggest staleness when linked decisions are newer than last_validated_date. Validation = compared to codebase and confirmed accuracy.

### 7. Cross-Reference Registry
Universal ref system: any document or decision can declare refs to other decisions, documents, tasks, or plans. Stored in document_ref junction table. Queryable both directions. Same refs[] format in ADR frontmatter and document registry.

### 8. ADR Frontmatter Standard
Every ADR file includes: uid, title, description (one-liner for session scanning), status, date, project, domain, supersedes, refs[]. Description enables fast relevance matching without reading full content.


## Options Considered

N/A

## Schema

document table: document_id, document_uid (DOC-xxxxxx), file_path, title_text, description_text, document_type_code, authority_code, project_code, domain_code, created_date, last_validated_date, validated_by_ref, status_code.

document_decision junction: document_id → decision_uid.

document_ref table: source_uid, target_type (decision|document|task|plan), target_uid, target_path, label_text.

decisions table additions: file_path, description_text, domain_code, supersedes_ref, superseded_by_ref.

## Migration
- Existing 231 decisions: keep decision_text/rationale_text for backward compat, stop writing new content there
- ADR files written on-demand: when a session touches a decision, it writes the ADR file
- New decisions always get an ADR file
- Document registry seeded from git log for created_date, all start as unvalidated

## Consequences

N/A
