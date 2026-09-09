---
uid: DEC-66d3ca
title: "BC-Agent on-premises appliance tier deferred from the Platform DB Foundation Program and tenant onboarding"
description: "D6: BC-Agent appliance tier deferred from the DB foundation program and onboarding v1; DEC-edd9bb unchanged; appliance-vs-hosted-DB conflict parked; reinstatement needs its own record"
status: decided
date: 2026-09-09T09:33:35.218Z
project: bc-db
domain: tenants
subdomain: tenants/hosting-tiers
focus: bc-agent-deferral
---

# BC-Agent on-premises appliance tier deferred from the Platform DB Foundation Program and tenant onboarding

## Context

Ratified by the operator on 2026-09-09 ("ratify D1 D6 D8"; earlier direction the same day: "This was just a concept — not seriously explored. Can be dropped/deferred if becomes complex."). The tier was never designed beyond the appliance ADR; there is no revenue dependency on it; its two records contradict each other on where the tenant's data lives; and carrying it in the foundation matrix would force the content-promotion wave to solve appliance distribution before the hosted platform is even reproducible. Deferring it removes a column from the program's scope without changing any decided record.

## Decision

The BC-Agent on-premises appliance tier (DEC-edd9bb, status decided/evolving) is deferred: it is excluded from the Platform DB Foundation Program's scope matrix (Tenant DB hosting classes are BareCount-hosted — AWS Shared / AWS Separate — and BYO-DB only) and from the first version of tenant onboarding. The conflict between DEC-edd9bb (appliance holds a local tenant database; data never leaves the premises; the control plane pushes configuration) and the operating chapter tenant-onboarding.md (no tenant DB provisioned for the agent; the agent writes to BareCount's hosted tenant DB) is parked, not resolved; DEC-edd9bb's own status is unchanged by this record. Reinstating the tier requires its own decision record, which must settle that conflict and, if the appliance-local model holds, make curated-content distribution to appliances (W3 content promotion) a hard tier requirement.
