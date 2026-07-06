---
uid: DEC-9bffcd
title: "BF-SF aliases as relational table, not JSONB"
description: "BF-SF alias mapping uses contract.business_field_alias table (D162-compliant), deprecating business_field.source_aliases JSONB column"
status: implemented
subdomain: payload-storage
focus: schema
date: 2026-04-09T03:03:37.378Z
project: bc-core
domain: contracts
migrated_from: legacy v2 archive
---

# BF-SF aliases as relational table, not JSONB

## Context

D162 Rule 1: No JSONB for queryable data. Aliases are queried (WHERE, JOIN) by FieldMappingService for AI-assisted mapping suggestions. Relational table enables: DB-enforced uniqueness (CR-AL-003), indexed reverse lookup, provenance tracking, FK validation against source_system. Follows business_object_field junction precedent.

## Decision

Business Field source aliases stored in a proper relational table `contract.business_field_alias`, not as JSONB on `business_field.source_aliases`. The JSONB column is deprecated — source of truth moves to the alias table. Existing OAGIS aliases (3,809 rows) migrated to the new table.
