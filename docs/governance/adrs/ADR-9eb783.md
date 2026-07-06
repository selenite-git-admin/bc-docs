---
uid: DEC-9eb783
title: "Pin all dependency versions exactly — no caret/tilde ranges"
description: "All npm dependencies pinned to exact versions. No caret or tilde ranges. Prevents surprise breakage from transitive updates."
status: decided
subdomain: dependency-management
focus: version-pinning-discipline
date: 2026-02-23
project: bc-core
domain: subscription
authority: authoritative
migrated_from: legacy v2 archive
---


# Pin all dependency versions exactly — no caret/tilde ranges

## Context

User requirement for stability and security. Prevents accidental breaking changes from minor/patch bumps. All dependencies audited for vulnerabilities before adoption. Exact pins ensure reproducible builds across dev machines and CI. Combined with lockfile, guarantees identical node_modules everywhere.

## Decision

All npm dependencies in bc-core will use exact version pinning (e.g., "11.1.14" not "^11.0.0"). package-lock.json must always be committed. No accidental upgrades. Use npm ci in CI/CD, not npm install. Dependency upgrades are deliberate, audited, and version-bumped explicitly.

## Options Considered

N/A

## Consequences

N/A
