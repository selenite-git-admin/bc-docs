---
uid: DEC-615cbd
title: "Operator-backed U7 staging-cloud unit CANCELLATION (revokes RESPONSE-450 staging authority; zero-orphan verified)"
description: "Operator-backed U7 staging-cloud unit CANCELLATION (revokes RESPONSE-450 staging authority; zero-orphan verified)"
status: decided
date: 2026-09-21T04:29:55.305Z
project: bc-core
domain: db-foundation
subdomain: cloud-realization/staging
focus: governance
---

# Operator-backed U7 staging-cloud unit CANCELLATION (revokes RESPONSE-450 staging authority; zero-orphan verified)

## Context

d597 RESPONSE-472 gated terminal exchange closure on the still-open U7 unit, offering two bounded paths: publish the missing completion evidence, or publish a direct operator-backed cancellation that revokes the staging authority, identifies actual cloud state, and proves no orphan. The operator chose cancellation. This DEC is the retained operator-authority record for the U7 disposition that d597 MSG-473 will carry to the auditor, satisfying the "direct operator-backed" provenance requirement (operator issued directly to this session, not a peer relay).

## Decision

The operator directly cancels the U7 staging-cloud completion unit on 2026-09-21 ("cancel U7"), formally revoking the unconsumed bounded staging-DatabaseStack authority granted by d597 RESPONSE-450 and the alert-sink repoint accepted by RESPONSE-453. The staging pilot was deployed and then fully torn down under the operator's earlier "wind down u7" directive; there is no live or billable staging resource to complete, so the unit is cancelled rather than completed. Because "cloud pilot is not here yet," staging realization is folded into the deferred go-live track (W1.6/W4), reopened only on a future deliberate operator decision — not carried as open program debt.

Current AWS state (verified read-only, AWS_PROFILE=default, ap-south-1, 2026-09-21):
- CloudFormation: no bcp-stg-* / DatabaseStack in any live state; the transient REVIEW_IN_PROGRESS changeset shell was removed.
- RDS: no DB instance. NAT: no NAT gateway in "available" state.
- SNS topic: `bcp-stg-aps1-dbs-rotation-alerts` is deleted (list-subscriptions-by-topic → InvalidParameter/NotFound). HOWEVER — corrected from the earlier "zero subscriptions remain" claim — the global `sns list-subscriptions` inventory still returns THREE residual `PendingConfirmation` email subscription records referencing that deleted topic ARN (endpoints: anant@selenite.co ×2, anant.kulk@gmail.com). These are non-deliverable orphan metadata attached to a topic that no longer exists: never confirmed, carrying no SubscriptionArn, and therefore not unsubscribable via API; AWS auto-purges unconfirmed subscriptions ~72h after creation. Non-billable; deliver nothing.
- KMS: exactly one staging key, KeyId `0d5e766c-d710-4b75-93c8-f8df2e67cd58` (ARN `arn:aws:kms:ap-south-1:546549546538:key/0d5e766c-d710-4b75-93c8-f8df2e67cd58`), DescribeKey KeyState=PendingDeletion, DeletionDate=2026-09-28T08:57:55+05:30, tag-bound to this unit (tags: unit=u7, Name=bcp-stg-aps1-dbs-key, Environment=stg, project=bc-db-foundation, track=cloud-realization). Aliases removed with the stack teardown, so tag-identified rather than alias-identified. Non-billable while pending; self-deletes on the scheduled date.
Net: no live or billable staging orphan. The only residues are self-clearing non-billable metadata (3 pending SNS orphans auto-expiring ~72h; 1 KMS key self-deleting 2026-09-28). Production Gate-④, DB/DDL, data-copy and any new cloud mutation remain excluded and untouched by this cancellation.
