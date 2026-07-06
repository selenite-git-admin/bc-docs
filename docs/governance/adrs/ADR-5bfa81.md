---
uid: DEC-5bfa81
title: "bc-website Versioning — Branch Model in Single Repo"
description: "Single repo with version branch namespaces (v2/develop, v2/main, v3/develop). Old Web-BareCount repo archived as v1 reference."
status: implemented
subdomain: repo-strategy
focus: branch-versioning-bc-website
date: 2026-03-19
project: bc-website
domain: website
authority: authoritative
migrated_from: legacy v2 archive
---


# bc-website Versioning — Branch Model in Single Repo

## Context

Single repo avoids repo sprawl while preserving full version history. Branch namespaces provide clean isolation between major versions. Web-BareCount remains accessible as v1 reference but is not the active codebase.

## Decision

bc-website uses a single repo with version branches: v2/develop (active development), v2/main (production v2), v3/develop (future). Tags for releases (v2.0.0, v2.1.0). Web-BareCount repo archived as v1 reference — no further development. Each major version gets its own branch namespace (vN/develop, vN/main).

## Options Considered

N/A

## Consequences

N/A
