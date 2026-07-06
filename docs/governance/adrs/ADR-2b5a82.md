---
uid: DEC-2b5a82
title: "Readiness assessment rules for master_data and integration"
description: "master_data and integration status are binary (not-started vs done). No partial or wip states allowed"
status: decided
subdomain: readiness-model
focus: status-enum-discipline
date: 2026-02-26
project: bc-core
domain: platform
authority: authoritative
migrated_from: legacy v2 archive
---


# Readiness assessment rules for master_data and integration

## Context

Hardcoded data in the portal is not master data delivery. Readiness must reflect real integration state, not UI completeness alone. Partial/wip creates ambiguity — either the API feeds the screen or it doesn't.

## Decision

master_data_status = not-started when data is hardcoded in portal. Done only when sourced from bc-core API. integration_status = not-started for all screens until actual bc-core integration exists. No partial/wip — binary yes or no.

## Options Considered

N/A

## Consequences

N/A
