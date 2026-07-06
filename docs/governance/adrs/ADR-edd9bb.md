---
uid: DEC-edd9bb
title: "BC-Agent On-Premises Appliance — premium tier with branded hardware"
description: "Premium on-prem tier: customer buys hardware per spec, BareCount provides pre-configured Data Plane runtime with secure remote management channel."
status: decided
subdomain: deployment-tier
focus: enterprise-onprem-appliance
date: 2026-03-03
project: platform
domain: readers
authority: evolving
migrated_from: legacy v2 archive
---


# BC-Agent On-Premises Appliance — premium tier with branded hardware

## Context

Financial institutions, government agencies, and healthcare organizations often mandate that sensitive data never leaves their physical premises. A branded appliance program turns this constraint into a premium revenue stream. Customer buys the hardware (no CAPEX for BareCount), BareCount provides the intelligence layer. This also strengthens the patent filing — a physical deployment model with secure remote management, tenant-local processing, and Control Plane / Data Plane separation is a distinct and defensible architectural claim beyond the provisional patent's current scope.

## Decision

BareCount offers a premium on-premises tier: the BC-Agent Appliance. Customer purchases hardware from a BareCount-recommended specification list (not BareCount's duty to procure). BareCount provides: (1) BC-Agent software package — pre-configured Data Plane runtime with all dependencies (reader engine, evaluation engines, tenant DB, monitoring agent). (2) Installation and commissioning service. (3) Remote access channel for management, updates, and monitoring (secure tunnel with customer-controlled firewall rules). (4) Ongoing update delivery — Control Plane pushes configuration, agent auto-updates via secure channel. Customer provides: hardware per spec, network access to their data sources, firewall allowlist for Control Plane communication. The appliance is fully self-contained — processes data locally, stores boundary objects and evidence locally, only sends operational telemetry to BareCount Control Plane.

## Options Considered

N/A

## Consequences

N/A
