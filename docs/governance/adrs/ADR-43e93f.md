---
uid: DEC-43e93f
title: "5 schema categories: extractor, source, gdp, kpi, ai"
description: "Schema Registry supports 5 categories mapping to lifecycle: extractor, source, gdp, kpi, ai. Superseded"
status: superseded
date: 2026-02-23
project: bc-core
domain: database
authority: retired
migrated_from: legacy v2 archive
---


# 5 schema categories: extractor, source, gdp, kpi, ai

## Context

Superseded by D089 (DEC-1918d0). The 5 schema categories (extractor, source, gdp, kpi, ai) were replaced by 11 domain-aligned schemas. Terms like 'extractor' and 'gdp' are extinct — replaced by source, canonical, metric.

## Decision

Schema Registry supports 5 categories: extractor (transport envelope, pre-observation), source (observed external data), gdp (canonical/conformed business entities), kpi (finalized metrics/facts), ai (ML/GenAI artifacts). Maps to lifecycle: extractor→pre-observation, source→observation, gdp→admission/evaluation, kpi→evaluation, ai→binds to gdp/kpi.

## Options Considered

N/A

## Consequences

N/A
