---
uid: DEC-912f4f
title: "Cognito-managed TOTP MFA (optional, admin-enforceable)"
description: "MFA uses Cognito-native TOTP. Optional per user, enforceable by admin policy. No custom MFA infra."
status: implemented
subdomain: mfa
focus: totp
date: 2026-02-26
project: platform
domain: auth
authority: authoritative
migrated_from: legacy v2 archive
---


# Cognito-managed TOTP MFA (optional, admin-enforceable)

## Context

TOTP is more secure than SMS (no SIM-swapping risk). Cognito manages TOTP secrets and verification natively. No SNS costs for SMS delivery. Admin-enforceable allows gradual rollout. Existing 6-digit OTP UI is already built.

## Decision

Software token MFA via Cognito (TOTP). No SMS MFA. Optional by default, admin can enforce per-user via AdminSetUserMFAPreference. Existing MfaVerificationPage reused.

## Options Considered

N/A

## Consequences

N/A
