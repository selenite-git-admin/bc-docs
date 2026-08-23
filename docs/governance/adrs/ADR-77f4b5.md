---
uid: DEC-77f4b5
title: "Demo-to-Contract Strategy — Synthetic Data Hook + SAP Licensing Gate"
description: "Demos use synthetic data (no system access). Production onboarding requires Schedule B for SAP licensing obligations as a contractual gate."
status: implemented
subdomain: go-to-market
focus: demo-strategy
date: 2026-03-07
project: bc-sdg
domain: contracts
refs:
  - type: decision
    label: "D187"
authority: authoritative
migrated_from: legacy v2 archive
---


# Demo-to-Contract Strategy — Synthetic Data Hook + SAP Licensing Gate

## Context

Connecting to customer SAP systems without formal agreements exposes customers to SAP audit risk (indirect access, undocumented third-party connections). By gating production access behind Schedule B — which documents the customer's SAP licensing responsibilities — BareCount converts a potential weakness (SAP licensing complexity) into a competitive advantage. SDG synthetic data removes the 'I need to see it working' objection without requiring free pilots.

## Decision

Customer demos use D187-generated synthetic data (no system access needed). Production onboarding requires formal Schedule B agreement because SAP licensing obligations (access model selection, Digital Access awareness, RFC ban compliance) fall on the customer. BareCount surfaces these obligations as a natural contractual gate — not an artificial barrier. This avoids the free-pilot trap while positioning BareCount as a knowledgeable licensing partner.

## Options Considered

N/A

## Consequences

N/A
