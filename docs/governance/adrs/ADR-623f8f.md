---
uid: DEC-623f8f
title: "ADR Hygiene Policy — closure process for the 351-ADR registry"
description: "8-rule policy for ADR lifecycle: supersession-pair flips, stuck-proposed cleanup, decided→implemented via closes: commit tokens, monthly audit, D-code-as-nickname, orphan tolerance, authoring gates, quarterly sweep."
status: decided
subdomain: adr-governance
focus: lifecycle-policy
date: 2026-04-22T04:13:12.935Z
project: bc-docs
domain: platform
migrated_from: legacy v2 archive
---

# ADR Hygiene Policy — closure process for the 351-ADR registry

## Context

As of 2026-04-22 audit: 253 decided / 41 implemented (6:1 closure debt), 17 supersession pair issues, 7 stuck-proposed > 30 days, 37 D-code collisions. Root cause is absence of a closure process, not bad authoring. Policy formalizes mechanics that automated tools (adr-audit.js, post-merge hooks) can enforce.

## Eight rules

### 1. Supersession pair rule (MANDATORY, enforced)
When a new ADR's frontmatter includes `supersedes: DEC-xxxxxx`:
- Target ADR's status MUST flip to `superseded` in the same commit
- Target ADR SHOULD add `superseded_by: DEC-yyyyyy`
- `scripts/adr-audit.js` fails CI if any `target-not-flipped-to-superseded` issue is present in a PR diff

### 2. Stuck-proposed rule (AUTOMATED, informational)
ADR in `proposed` status > 30 days auto-spawns a DevHub task tagged `adr-stuck-proposed` assigned to the ADR owner. Auto-closes when status flips. No merge enforcement.

### 3. Implementation verification (MANDATORY for new ADRs)
Status transitions:
- `draft` → `proposed`: author submits for review
- `proposed` → `decided`: consensus reached
- `decided` → `implemented`: a commit whose message includes `closes: DEC-xxxxxx` has landed
- `decided` → `superseded`/`reversed`: new ADR takes over

A post-merge hook scans merge-commit messages for `closes:` tokens and updates the ADR's `status` via a PR-bot. No human action needed.

### 4. Monthly audit (AUTOMATED)
`scripts/adr-audit.js` runs monthly via CI/cron. Output compared to previous month; any regression (new supersession issue, new stuck-proposed crossing threshold) opens a governance task. Trend visualization in `docs/governance/adr-audit-history.md` (auto-appended).

### 5. D-code canonical rule (GUIDANCE)
- UIDs (DEC-xxxxxx) are canonical — use in titles, cross-links, new content
- D-codes are nicknames for humans in conversation — kept in DevHub registry but not authoritative
- Existing ADRs are not required to be rewritten; only new content must use UIDs

### 6. Orphan ADRs — no defect classification
An ADR with zero incoming references is NOT automatically stale. Many legitimate decisions stand alone. Orphan count is informational; human review eventually, but orphan does not trigger closure pressure.

### 7. ADR authoring gates
Existing gates kept: frontmatter completeness, required sections, forbidden vocabulary. New gate added: if `supersedes:` field present, target ADR must exist and its status-flip is staged in the same commit.

### 8. Quarterly consolidation sweep
Once per quarter: re-run audit, human review of top 20 orphans for potential archival/merge, human review of retired SOPs + obsolete foundation pages. Owner: platform lead.

## Rollout
1. Register this policy as ADR (this entry, status=decided)
2. Ship `scripts/adr-audit.js` in CI monthly cron (GitHub Actions schedule)
3. Ship post-merge hook scanning `closes: DEC-xxxxxx` and flipping status (GitHub Action)
4. Publicize in project README / CLAUDE.md so future AI sessions enforce from day one

## Out of scope
- Content-level merging of overlapping ADRs
- ADR templates / authoring patterns (already in `docs/authoring/decision.md`)
- Deletion of ADRs (never — superseding preserves history)
- Bulk migration of old ADRs from D-codes to UIDs in cross-references (cosmetic only)
