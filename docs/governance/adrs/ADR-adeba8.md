---
uid: DEC-adeba8
title: "Connector category: external_source for non-operational reference data sources"
description: "New connector category external_source for reference data (exchange rates, indices). Distinct from operational enterprise sources."
status: implemented
subdomain: connectors
focus: external-source-category
date: 2026-02-27
project: bc-core
domain: connectors
authority: authoritative
migrated_from: legacy v2 archive
---


# Connector category: external_source for non-operational reference data sources

## Context

ECB SDMX REST API doesn't fit operational_system (not a business system) or data_store (not a database/warehouse) or file_storage (not S3/GCS). A distinct category clarifies the nature of the data source and enables appropriate UI treatment.

## Decision

Added external_source as a fourth connector category alongside operational_system, data_store, and file_storage. Used for reference data APIs like ECB, FRED, OER that are neither operational systems nor data stores.

## Options Considered

N/A

## Consequences

N/A
