---
uid: DEC-422db8
title: "Multi-source connector generation — not Airbyte-only, intermediate spec, risk mitigations"
description: "Multiple input parsers (Airbyte/Singer/Meltano/raw API) feed one BC-owned intermediate spec and one code generator"
status: implemented
subdomain: connectors
focus: connector-generation-strategy
date: 2026-03-05
project: bc-infra
domain: database
refs:
  - type: decision
    label: "D038"
  - type: decision
    label: "D039"
authority: authoritative
migrated_from: legacy v2 archive
---


# Multi-source connector generation — not Airbyte-only, intermediate spec, risk mitigations

## Context

Single-source dependency on Airbyte carries 7 identified risks (license rug-pull, schema breaks, quality variance, coverage gaps, company viability, schema mismatches, IP perception). The multi-source intermediate-spec architecture mitigates all 7 by decoupling input parsing from code generation. The BareCount Connector Spec acts as the firewall — upstream changes affect parsers only, never the generator or generated executors. Fork/snapshot of MIT manifests provides legal insurance against future license changes (Airbyte already moved core MIT→ELv2 in 2021).

## Decision

Connector auto-generation MUST NOT depend solely on Airbyte. Architecture uses a multi-source input strategy with a BareCount-owned intermediate format:

```
Airbyte YAML manifests ──┐
Singer Tap specs ─────────┤──→ BareCount Connector Spec (BC-owned schema) ──→ ReaderExecutor Generator
Meltano configs ──────────┤
Raw API documentation ────┘
```

Multiple input parsers, one intermediate BareCount Connector Spec, one TypeScript code generator. If any upstream source changes license or dies, we swap the parser — not the generator or generated code.

**Airbyte exploitation rules:**
1. Only use MIT-licensed manifests and CDK schema. Check each connector's metadata.yaml before use.
2. Fork/snapshot all target MIT manifests into a BareCount-controlled repo as dated archive. This is the license-change hedge.
3. Pin to a specific Airbyte manifest schema version. Abstract with adapter layer for schema upgrades.
4. Auto-generated connectors start in "draft" status. Promoted to "available" only after passing BareCount validation suite (evidence chain, admission contract compliance, pagination correctness).
5. Generated code is original TypeScript with MIT attribution header. No Airbyte runtime dependency.
6. The BareCount Connector Spec is our IP — not derived from Airbyte's schema, but informed by multiple sources.

**Connector tiers (from D038, refined):**
- Top 10 strategic connectors → hand-built (Strategy C), full BareCount integration, proprietary
- Connectors 11–50 → auto-generated via manifest factory (Strategy A), validated, MIT (@barecount/connectors)
- Connectors 50+ → community contributions using the same factory + validation gate

**Extends D038.** D038 established ReaderExecutor as containment boundary and flagged Airbyte exploration. D039 locks the multi-source architecture and risk mitigations.

## Options Considered

N/A

## Consequences

N/A
