---
uid: DEC-4bff1c
title: "Reader \"flavors\" are \"Target Sources\""
description: "Internal concept flavor exposed in UI as Target Source. Each represents a specific source system the reader can read from"
status: decided
subdomain: taxonomy
focus: ui-vocabulary-flavor-target-source
date: 2026-03-13
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Reader "flavors" are "Target Sources"

## Context

"Flavor" is an implementation term, not a business concept. "Target Source" communicates clearly what it represents — which source system this reader points to.

## Decision

The internal concept of "flavor" (source-specific implementation of a reader) is exposed in the UI as "Target Source". Each target source represents a specific source system the reader can read from (e.g., ECB, OER, FRED for exchange rate reader). Target Sources table columns: Target Source | Connector | Contracts | Last Validated | Health.

## Options Considered

N/A

## Consequences

N/A
