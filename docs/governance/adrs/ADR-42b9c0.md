---
uid: DEC-42b9c0
title: "Admin-provisioned users only (no self-signup)"
description: "No Cognito self-signup. Users created by tenant admin via bc-core API calling AdminCreateUser. Invitation email flow"
status: implemented
subdomain: provisioning
focus: admin-only
date: 2026-02-26
project: bc-core
domain: tenants
authority: authoritative
migrated_from: legacy v2 archive
---


# Admin-provisioned users only (no self-signup)

## Context

BareCount is B2B SaaS — users are provisioned by customer admins, not self-registered. AdminCreateUser sets custom:tenant_id at creation time, ensuring tenant binding from day one. Invitation flow gives admin control over who accesses their tenant.

## Decision

No self-signup in Cognito. Users created by tenant admin via bc-core API calling Cognito AdminCreateUser. Users receive invitation email with temp password. First login triggers FORCE_CHANGE_PASSWORD flow.

## Options Considered

N/A

## Consequences

The negative half of the decision (no Cognito self-signup) is fully enforced — the frontend exposes no signUp path and bc-core has no public registration endpoint.

The positive half (provisioning via bc-core API → `AdminCreateUser` → invitation email) is **partially implemented**:
- `FORCE_CHANGE_PASSWORD` flow on first login is supported (`bc-portal/apps/web/src/.../ProtectedRoute.tsx` handles `newPasswordRequired`).
- The bc-core API endpoint that wraps `AdminCreateUser` does NOT exist as of 2026-04-22. User provisioning currently happens via the AWS Cognito console or IaC.

Status flipped to `implemented` to acknowledge the operational baseline (no self-signup is the security floor and it holds). The missing API path is tracked as a follow-up gap and will land naturally with the Tenant Onboarding Gate work (DEC-a67518), which is the natural carrier for the user-creation flow. Building the API standalone now would ship infrastructure ahead of its consumer.

When the API ships, this section will note the closing commit.
