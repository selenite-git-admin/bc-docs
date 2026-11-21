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

## Amendment 1 (2026-11-21): a second factor is required for platform users

The original text above stays as decided and is not rewritten.

AUTHORITY: recorded operator grant `2026-11-21T16-27-02-562Z-6ba51faa`, text sha256 `6ba51faa0230f663925d34f4d859039f79bba81cddd249be92563f47895a2eb4`, method totp.

A second factor at sign-in is required for platform users. The sentence that makes it optional and an administrator's choice per user no longer holds.
