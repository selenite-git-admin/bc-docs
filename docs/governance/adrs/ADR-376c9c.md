---
uid: DEC-376c9c
title: "DevHub as separate repo + EC2"
description: "DevHub runs as standalone Express+SQLite app on shared EC2, not inside bc-core or bc-admin"
status: implemented
subdomain: devhub-deployment
focus: standalone-runtime
date: 2026-02-22
project: barecount-devhub
domain: platform
authority: authoritative
migrated_from: legacy v2 archive
---


# DevHub as separate repo + EC2

## Context

Claude sessions need persistent coordination. EC2 doubles as dev environment.

## Decision

Standalone Express+SQLite app on shared EC2 (t3.large)

## Options Considered

N/A

## Consequences

N/A
