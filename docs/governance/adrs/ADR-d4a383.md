---
uid: DEC-d4a383
title: "Infrastructure lives in dedicated infra repo"
description: "All infrastructure (Docker, Terraform, init scripts) must be in the dedicated infra repo, not embedded in service repos like bc-core."
status: implemented
subdomain: project-organization
focus: infra-repo-separation
date: 2026-02-23
project: bc-infra
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Infrastructure lives in dedicated infra repo

## Context

User directive: "any infra across platform can/must be provided through infra repo". Keeps infrastructure centralized, avoids drift between repos, and separates concerns between application code and deployment infrastructure.

## Decision

All infrastructure (Docker Compose, init scripts, Terraform, etc.) across the platform must be provided through a dedicated infra repo — not embedded in individual service repos like bc-core. A dev-only docker-compose.yml may remain in bc-core for local convenience but the canonical infra definitions belong in the infra repo.

## Options Considered

N/A

## Consequences

N/A
