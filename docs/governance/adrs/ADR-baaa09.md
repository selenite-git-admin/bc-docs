---
uid: DEC-baaa09
title: "Source contracts are business-function-agnostic — function_code belongs on canonical/metric layer only"
description: "Source contracts never carry function_code. Business function assignment happens at canonical and metric contract layers only."
status: decided
subdomain: contract-primitive
focus: schema
date: 2026-03-25
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Source contracts are business-function-agnostic — function_code belongs on canonical/metric layer only

## Context

During Finance belt enrichment, we mapped 575 source modules to business functions for catalog browsing. Before propagating these to 14,462 source contracts, we recognized this would conflate source system classification with business binding. Source contracts are runtime/system artifacts — they admit data. The canonical contract is where business meaning is created. Polluting source contracts with business function codes would create false architectural coupling and make it harder to reuse the same source contract across different business contexts.

## Decision

Source contracts and admission contracts are system-level bindings. They bind a source object to the admission boundary. The business function assignment happens at the canonical boundary, not at admission. source_module.business_function is catalog metadata for browsing/discovery only — it must NOT be propagated to source_contract.function_code or admission_contract.function_code. Business meaning is assigned at: (1) canonical_contract.function_code — where SO→CO mapping assigns business context, (2) metric_definition.function_code — where metrics are bound to business functions. The same source contract (e.g., BKPF from S/4) could serve Finance/GL, Finance/AP, or Audit depending on what the canonical layer does with the admitted data.

## Options Considered

N/A

## Consequences

N/A
