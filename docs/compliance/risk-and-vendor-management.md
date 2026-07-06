---
id: risk-and-vendor-management
order: 46
title: "Risk and Vendor Management"
status: drafting
authority: authoritative
depends_on: [the-authority-model, devhub, infosec-and-access-control, security-operations, support-and-escalation]
governing_sources:
  - The Authority Model
  - DevHub
  - InfoSec and Access Control
governing_adrs:
  - DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact; mitigates RSK-cb8929)
  - DEC-324d9e (Stripe billing integration; subscription and payment management as a vendor surface)
  - DEC-1918d0 (Two-database split; the database substrate that the AWS PostgreSQL vendor relationship hosts)
  - DEC-771baf (Tenant database topology; the per-tenant database the AWS PostgreSQL vendor relationship hosts)
  - DEC-3395bc (bc-docs-v3 SSOT cutover; the documentation surface that the bc-core docs endpoints host)
  - DEC-623f8f (ADR Hygiene Policy; the audit cadence policy that this chapter cites for risk-review scheduling)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Risk and Vendor Management

## Scope

This chapter records the platform's risk register and vendor inventory: the DevHub `risks` table as the platform's risk treatment registry, the `devhub_risk_*` MCP tool family that operators use to record and update rows, the per-row schema (category, likelihood, impact, score, mitigation, owner, status, review date), the externally-cited risks that are documented in ADRs but not yet present in the registry as drift, the eleven external vendors the platform consumes, and the per-vendor failure mode and the platform's response.

This chapter does not redefine the InfoSec controls (InfoSec and Access Control), the operational secrets management (Security Operations), or the support escalation path that consumes vendor-incident triage (Support and Escalation).

**Governing source.** outline.md §4.8; The Authority Model.

## The DevHub Risk Register

The platform's risk treatment registry is the DevHub `risks` table at `barecount-devhub/src/db.js`. Each row carries a unique identifier and a structured assessment.

| Column | Form |
|---|---|
| `uid` | `RSK-xxxxxx` (six hex characters); generated at insert |
| `project_id` | FK to `projects.id`; the project the risk belongs to |
| `title_text`, `description_text` | The risk statement |
| `category_code` | One of `security`, `operational`, `compliance`, `financial`, `technical`, `strategic` |
| `likelihood_code` | One of `very-low`, `low`, `medium`, `high`, `very-high` |
| `impact_code` | One of `very-low`, `low`, `medium`, `high`, `very-high` |
| `risk_score` | Auto-calculated from likelihood plus impact at insert |
| `mitigation_text` | The risk treatment in operational language |
| `owner_name` | The operator responsible for the risk |
| `risk_status` | One of `identified`, `assessed`, `mitigated`, `accepted`, `closed` |
| `review_date`, `created_ts`, `updated_ts` | Lifecycle timestamps |
| `actor_name` | The operator who recorded the row |

The MCP tool family is `devhub_risk_add`, `devhub_risk_list`, `devhub_risk_update`. The signatures map directly to the column set.

| Tool | Effect |
|---|---|
| `devhub_risk_add` | Inserts a new risk row; allocates the `RSK-xxxxxx` UID; auto-calculates the score; logs the activity event |
| `devhub_risk_list` | Returns risks filtered by project, status, or category |
| `devhub_risk_update` | Mutates an existing risk by UID; supports status transition, likelihood or impact revision, mitigation update, owner reassignment, review-date set |

The `risks` table is the authority. The risk treatment record lives in DevHub; ADRs that reference a risk by UID are pointing at the DevHub row.

**Governing source.** `barecount-devhub/src/db.js` (risks schema declaration); `barecount-devhub/src/routes/risks.js`.

## RSK-cb8929 as a Recorded Risk Treatment

`RSK-cb8929` is the platform's known supply-chain risk. The risk is documented in `DEC-441665` (NPM supply chain mitigation via AWS CodeArtifact) and in every committed `.npmrc` file across the five npm-consuming repos. The treatment is the CodeArtifact mirror itself: by routing every install through the cache, the platform ensures that an npmjs.org origin outage does not block the build, and that a yanked or compromised package version does not silently propagate.

The drift: `RSK-cb8929` is absent from the DevHub `risks` table in the readiness baseline. The risk is acknowledged in ADR text and in the `.npmrc` comments, but the registry row that would record the treatment status is missing. Reconciliation lands as a `devhub_risk_add` call with the title "NPM supply-chain compromise" and a `mitigated` status pointing at `DEC-441665` as the treatment ADR.

**Governing source.** DEC-441665; `bc-qa/.npmrc`; CLAUDE.md (NPM Registry section).

## External Vendor Inventory

The platform consumes eleven external vendor surfaces. Each surface has a defined failure mode and a defined platform response. Per pattern 88, the inventory is per-instance enumerated.

| Vendor | Surface consumed | Consumer in the platform | Failure mode |
|---|---|---|---|
| AWS Cognito | JWT issuance, JWKS endpoint, token validation | bc-core JwtAuthGuard plus CognitoJwtStrategy | Authentication unavailable; HTTP 401 across every authenticated route; the platform is unreachable until Cognito recovers |
| AWS CodeArtifact | npm registry mirror per `DEC-441665` | npm install in every npm-consuming repo (barecount-devhub, bc-core, bc-portal, bc-admin, bc-qa) | Token expiry returns HTTP 401 or 403 on install; the operator runs the renewal command per Build and Release |
| AWS Bedrock | Foundation-model invocation surface (Claude, Gemini, Titan) | bc-ai agents per AI Architecture and AI Agents | AI verification unavailable; gates fall back to the per-gate posture defined in AI Gates (advisory or unverified per the gate's own policy) |
| AWS S3 | Object storage for static assets and WORM archives | bc-portal and bc-admin SPA bundles, S3 nullification markers per Privacy and the Immutable Fact | Static assets unreachable; bc-admin or bc-portal cannot load; nullification markers cannot be placed |
| AWS Secrets Manager | API keys, OAuth tokens, Cognito client secrets, third-party credentials | bc-core service startup, runtime secret reads | Secrets unavailable; consumer services cannot authenticate; bc-core fails to start |
| AWS RDS PostgreSQL | Platform DB plus per-tenant DBs per `DEC-1918d0` and `DEC-771baf` | bc-core registry, contract, boundary, audit services | Database unavailable; every API endpoint returns 5xx; the platform is unreachable until PostgreSQL recovers |
| Stripe | Subscription, payment, invoicing surface per `DEC-324d9e` | bc-admin Subscription menu surfaces; bc-core webhook receiver | Billing surface unavailable; tenant subscription transitions stall; the platform's runtime continues serving existing tenants per their current binding |
| npmjs.org | Origin behind the CodeArtifact mirror | Indirect via CodeArtifact only; no direct npmjs.org consumption per `DEC-441665` | npmjs.org unavailable; existing cached versions continue to install; new package versions are blocked until npmjs.org recovers |
| Anthropic Claude API | AI agent reasoning (housekeeping, KPI verification, BO classification) per the AI section | bc-ai agents per AI Architecture | Provider unavailable; the consuming agent's verdict is unavailable; the gate falls back per AI Gates |
| Google Gemini API | Cross-family verification, grounded search, BO field evaluation | bc-ai agents per AI Architecture | Provider unavailable; same fall-back behavior as Claude |
| OpenAI API | Optional AI agent surface; consumption is per-agent-configurable | bc-ai agents where the agent's primary or checker is configured for OpenAI | Provider unavailable; same fall-back behavior |

**Governing source.** Per-vendor consumer chapter (AI Architecture for Bedrock and the AI providers; Operations: Tenant Lifecycle and Subscription for Stripe; Build and Release for CodeArtifact and npmjs.org); CLAUDE.md (AWS section).

## Per-Vendor Risk Profile

Each vendor surface produces a risk profile that the DevHub registry should record. The profile distinguishes the risk class, the likelihood, the impact, and the platform's mitigation.

| Vendor | Risk class | Mitigation |
|---|---|---|
| AWS Cognito | Authentication unavailability | AWS shared-responsibility model; Cognito is a managed service with high availability; no in-platform fallback authenticator |
| AWS CodeArtifact | Token expiry, mirror unavailability | Twelve-hour token TTL with operator-driven renewal; the cache survives npmjs.org outages; recorded as `RSK-cb8929` |
| AWS Bedrock | AI provider unavailability | Cross-family pairing where applicable per AI Trust and Verification; gate-by-gate fallback policy in AI Gates; the platform's contract execution does not depend on Bedrock |
| AWS S3 | Object-store unavailability | AWS shared-responsibility; the runtime contract execution does not depend on S3 reads; Privacy nullification markers can be retried |
| AWS Secrets Manager | Secrets unavailability | Boot-time read with no in-memory cache long-lived; if the read fails, bc-core refuses to start |
| AWS RDS PostgreSQL | Database unavailability or corruption | Local docker compose for development; AWS RDS managed-service guarantees for the staged deployment; backup posture is queued per Operations: Upgrade and Migration |
| Stripe | Billing-surface unavailability or webhook delivery delay | Stripe is the canonical billing substrate per `DEC-324d9e`; the runtime serves existing tenants on their current binding; tier transitions stall but do not break runtime |
| npmjs.org | Origin registry compromise or yanking | CodeArtifact mirror is the immediate dependency source; the cache survives origin incidents; tracked as `RSK-cb8929` |
| Anthropic Claude API | Provider unavailability, model deprecation, pricing change | Per-gate fallback policy in AI Gates; provider price is recorded per AI Usage Visibility but auto-tracking of price drift is queued |
| Google Gemini API | Same as Claude | Same as Claude |
| OpenAI API | Same as Claude | Same as Claude |

**Governing source.** AI Gates; AI Trust and Verification; Operations: Tenant Lifecycle and Subscription; CLAUDE.md.

## Constraints

| Constraint | Form |
|---|---|
| Risk register is canonical | The DevHub `risks` table is the platform's risk treatment authority; ADRs that reference a risk by UID point at the table row |
| Per-vendor inventory is per-instance enumerated | Pattern 88: the chapter does not say "all AWS services"; it enumerates per-vendor surface |
| The runtime contract execution does not depend on AI providers | The chain may proceed under per-gate policy; AI provider unavailability does not block the runtime |
| The runtime contract execution does not depend on Stripe | Tenant subscription transitions stall under Stripe outage; existing bindings continue to serve |
| Authentication is the load-bearing dependency | AWS Cognito unavailability is the universally-blocking failure mode; no in-platform fallback authenticator |
| Database unavailability is the load-bearing dependency | AWS RDS PostgreSQL unavailability blocks every endpoint; the platform is unreachable until recovery |

**Governing source.** AI Gates; CLAUDE.md.

## Failure Modes

| Failure | Behavior |
|---|---|
| `devhub_risk_add` called with missing required field | The route returns 400 with the validation error; the registry row is not created |
| `devhub_risk_update` against a non-existent UID | HTTP 404; operator confirms the UID and retries |
| Risk register reconciliation surfaces an ADR-cited but unregistered risk | Operator runs `devhub_risk_add` to create the registry row; the ADR is updated to reference the row's UID |
| Vendor outage detected | Operator records the incident per Incident and Change Management; the risk register may be updated to reflect the realized impact and the lessons learned |
| Vendor pricing change | Operator records the change in the registry; if material, an ADR records the architectural response |

**Governing source.** `barecount-devhub/src/routes/risks.js`; Incident and Change Management.

## Drift Inventory

| Drift item | Status |
|---|---|
| `RSK-cb8929` is documented in `DEC-441665` and in committed `.npmrc` files but is not present as a row in the DevHub `risks` table | Recorded; reconciliation queued |
| The eleven external vendor surfaces are not all enumerated as `risks` rows | Recorded; the per-vendor risk profile is documented in this chapter; the registry rows are queued |
| Provider price drift is recorded per AI Usage Visibility but auto-tracking is queued | Recorded; the static price snapshots in bc-ai code are operator-updated |
| Quarterly risk review schedule is not yet wired | Recorded; per `DEC-623f8f` the ADR audit script runs ad hoc; the risk-register equivalent cadence is queued |
| AWS service outage detection is operator-driven | Recorded; CloudWatch alarms and AWS service-health subscriptions are queued per Operations: Observability and Telemetry |
| OpenAI API consumption is per-agent-configurable but not centrally tracked | Recorded; the per-agent provider configuration is owned by the agent definition |

**Governing source.** DEC-441665; AI Usage Visibility; Operations: Observability and Telemetry.

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| InfoSec and Access Control | The auth boundary, the scope guard, the docs anti-scraping, the supply-chain control as a technical surface | The supply-chain control as a recorded risk treatment in the registry |
| Security Operations | Operational secrets, key rotation, JIT access, secret-rotation cadence | The operational discipline that consumes the risk register's findings |
| Operations: Tenant Lifecycle and Subscription | The Subscription artifact, the tier model, Stripe as the billing substrate | The Stripe vendor surface and the failure mode at the platform level |
| AI Gates | The per-gate fallback policy under AI provider unavailability | The Bedrock and per-provider vendor surfaces |
| AI Trust and Verification | The cross-family verification posture | The cross-family pairing as a vendor-risk mitigation |
| Operations: Incident and Change Management | The incident triage path | The risk-register update procedure when a recorded risk is realized |
| ISO 27001 Conformance | The conformance posture | The risk register as the platform's risk treatment substrate per ISO 27001 |
| SOC 2 Conformance | The Trust Services Criteria mapping | The CC3 risk-assessment surface |

**Governing source.** outline.md §4.8; The Authority Model.

## References

- The Authority Model
- DevHub
- InfoSec and Access Control
- Security Operations
- Operations: Tenant Lifecycle and Subscription
- Operations: Incident and Change Management
- Operations: Observability and Telemetry
- AI Gates
- AI Trust and Verification
- AI Usage Visibility
- ISO 27001 Conformance
- SOC 2 Conformance
- DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact)
- DEC-324d9e (Stripe billing)
- DEC-1918d0 (Two-database split)
- DEC-3395bc (bc-docs-v3 SSOT cutover)
- CLAUDE.md (NPM Registry section, AWS section)
