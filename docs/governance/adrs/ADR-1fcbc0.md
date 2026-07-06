---
uid: DEC-1fcbc0
title: "AWS Cognito for authentication"
description: "Cognito user pools with JWT for all BareCount auth. Tenant ID embedded in JWT claims. Supports MFA, SAML/OIDC federation."
status: implemented
subdomain: cognito-pool
focus: infrastructure
date: 2026-02-22
project: bc-infra
domain: tenants
authority: authoritative
migrated_from: legacy v2 archive
---


# AWS Cognito for authentication

## Context

Managed auth with MFA, federated identity, SAML/OIDC.

## Decision

Cognito user pools with JWT. Tenant ID in claims.

## Options Considered

N/A

## Consequences

N/A
