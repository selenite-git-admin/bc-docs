---
uid: DEC-1392ee
title: "Demo tier — 2 weeks free on AWS Shared only"
description: "Only AWS Shared tier eligible for demo. 14-day free trial, auto-suspend on Day 14, data retained 30 days. All other tiers require paid subscription."
status: decided
subdomain: demo-tier
focus: trial-policy
date: 2026-03-03
project: bc-infra
domain: tenants
authority: evolving
migrated_from: legacy v2 archive
---


# Demo tier — 2 weeks free on AWS Shared only

## Context

Demos lower the barrier to entry for prospects. Limiting to AWS Shared keeps trial costs minimal (shared infrastructure, auto-provisioned). Dedicated infrastructure (AWS Separate) and customer-hosted options (BYO-DB, BC-Agent) involve real costs and pre-work that don't make sense for a trial period.

## Decision

Only the AWS Shared hosting tier is eligible for demo/trial. Demo tenants get 14 days free with full platform access. Day 12 triggers a reminder notification. Day 14 auto-suspends the tenant (data retained 30 days, then purged). Conversion to a paid plan (Starter or higher) at any point during or after demo activates the subscription. Demo tenants use a lightweight provisioning path — auto-created DB on shared RDS, no onboarding gate. All other tiers (AWS Separate, BYO-DB, BC-Agent) require paid subscription from day 1.

## Options Considered

N/A

## Consequences

N/A
