---
uid: DEC-5dfee7
title: "Public data sources auto-connect without credentials; per-connector legal file"
description: "ECB, World Bank, FRED etc. connect without credentials. Each connector maintains a legal/licensing file with disclaimers and restrictions."
status: implemented
subdomain: connectors
focus: auth-policy
date: 2026-02-27
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Public data sources auto-connect without credentials; per-connector legal file

## Context

Public datasets have open APIs — no auth needed. Legal clarity per connector prevents compliance issues. SAP SDK example shows that some connectors need client-provided components (exact version match), which is a tactical requirement that must be surfaced early in the registration flow.

## Decision

Public data sources (ECB, World Bank, FRED, etc.) can be connected without credentials or method configuration — the platform handles admission directly. Each connector must maintain a legal/licensing file documenting: what is allowed, what is restricted, SDK requirements (e.g., SAP SDK must be uploaded by client with exact version match). Disclaimer text should appear on the connector card. Development can proceed in advance; tactical needs (like client-uploaded SDKs) are flagged at registration time.

## Options Considered

N/A

## Consequences

N/A
