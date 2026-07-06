---
uid: DEC-a537bf
title: "Cognito JWT end-to-end token strategy"
description: "JWT tokens from Cognito flow end-to-end: frontend gets token, passes as Bearer header, bc-core validates via JWKS."
status: implemented
subdomain: token-strategy
focus: jwks-validation
date: 2026-02-26
project: bc-core
domain: auth
authority: authoritative
migrated_from: legacy v2 archive
---


# Cognito JWT end-to-end token strategy

## Context

Eliminates custom token issuance. Cognito manages full token lifecycle (access, refresh, expiry, revocation). No shared JWT secret needed. Standard OIDC pattern — more secure (RS256 asymmetric), no secret rotation burden.

## Decision

Portal authenticates directly with Cognito, sends Cognito JWT to bc-core, bc-core validates via JWKS. No custom token issuance by bc-core.

## Options Considered

N/A

## Consequences

N/A
