---
uid: DEC-3cc8a1
title: "Metis — AI-Driven Function CounterParts at the Intervention Boundary"
description: "Metis: autonomous AI CounterParts per business function. Hierarchy-aware, bidirectional communication, suo moto actions, cross-function intelligence. Owned by bc-ai."
status: reversed
subdomain: intervention-ai
focus: metis-counterpart-agents
date: 2026-04-02
project: bc-ai
domain: execution
refs:
  - type: decision
    label: "D250 — IC Simplification"
  - type: decision
    label: "D068 — Metric Architecture"
  - type: decision
    label: "D085 — Metric as Data Product"
  - type: decision
    label: "D165 — Intervention Contract Family"
authority: authoritative
migrated_from: legacy v2 archive
---

# D251: Metis — AI-Driven Function CounterParts at the Intervention Boundary

## Naming

**Metis** — the Greek titaness of Good Counsel and Cunning Intelligence. She provided the plan that overthrew Cronus. The name maps to every layer of the system: cunning intelligence (causal reasoning through evidence chains), good counsel (suo moto reports and proactive recommendations), the brain behind the king's success (the CFO succeeds because Metis provides the strategy). Phonetically adjacent to "metrics" — natural, not forced.

| Layer | Name | Usage |
|-------|------|-------|
| Identity | **Metis** | Product name, UI, conversations. "Metis flagged AR deterioration" |
| Role | **CounterPart** | Relationship descriptor. "Your Finance CounterPart" |
| Full | **Metis, your Finance CounterPart** | First introduction, marketing |
| Codebase | `metis/` | bc-ai module: `MetisAgent`, `MetisFlow`, `MetisThread` |

**Domain strategy:**
- Now: `metis.barecount.com` (subdomain, zero cost)
- Soon: `barecount.ai` (~$100, covers all AI surfaces — D223, D235, D251)
- Then: `metis.barecount.ai` (dedicated Metis endpoint)

## Context

The BareCount execution model defines a fixed object progression:

```
Source State -> UinBAT Reader -> SO -> Canonical Evaluation -> CO -> Metric Snapshot -> Action Object
```

Everything up to Metric Snapshot is **observation** — the platform measuring the business. The intervention boundary is where BareCount **acts**. Intervention contracts (D250) define the rules: activation mode, trigger conditions, assignee pool, closure window, evaluation model. But no component autonomously evaluates context and executes these contracts.

Today, the last mile requires human monitoring: a tenant watches dashboards, notices a metric breach, manually creates an Action Object. This is the same gap every BI tool has — and the same gap that commodity alerting (static threshold -> notification) only partially fills.

Meanwhile, bc-ai already operates a maker-checker-gate pipeline with 5 registered agent flows, Bedrock inference profiles, evidence storage, and budget management. The infrastructure for autonomous AI agents exists. It just hasn't been pointed at the intervention boundary yet.

## Problem

**Static alerts are context-blind.** They answer THAT something happened, but not WHY, WHAT it means, or WHAT to do. Three specific failures:

### 1. No causal reasoning

Alert: "AR aging breached 45 days." But the metric is stale because a canonical mapping broke 3 days ago — the real AR aging hasn't changed. A static rule fires on the number. It cannot trace the evidence chain (Metric Snapshot -> CO -> SO -> boundary health) to distinguish a real business problem from a data boundary failure.

BareCount preserves evidence and lineage at every boundary. This chain is a knowledge base that AI can reason over — but only if something reads it.

### 2. No cross-metric pattern recognition

A static alert watches ONE metric against ONE threshold. But business problems manifest as **multi-signal patterns**: revenue flat + DSO climbing + customer churn ticking up — individually none breach thresholds, together they signal trouble. The metric DAG (D068: primary metrics from COs, secondary from upstream metric snapshots) encodes these dependencies. No single rule captures cross-metric correlation.

### 3. No intervention composition

A static alert triggers a notification. An intervention contract (D250) defines more: activation mode, assignee pool from which to select an owner, closure window, evaluation model. But someone still has to read the alert, understand the context, pick the right owner, and set a meaningful target. The Action Object (D250: one intervention per metric per cycle with numeric target) needs to be composed with business context, not just triggered.

### 4. No feedback loop

Fire-and-forget is the same as alerts with extra steps. Without bidirectional communication, follow-up tracking, escalation, and outcome learning, the system never improves. The agent must be a **partner**, not a notifier.

## Decision

### Metis: Autonomous Function CounterParts in bc-ai

Each business function gets a **Metis CounterPart** — an autonomous AI agent that monitors, reasons, acts, communicates, follows up, and learns.

### The Metis Capability Stack

```
Level 0: Threshold evaluation          (what alerts do — table stakes)
Level 1: Causal reasoning              (evidence chain tracing)
Level 2: Cross-metric patterns         (function-level constellation analysis)
Level 3: Intervention composition      (rich Action Objects with business context)
Level 4: Bidirectional communication   (conversation threads, not notifications)
Level 5: Hierarchy-aware escalation    (org structure, role-based messaging)
Level 6: Suo moto actions              (proactive reports, coverage gaps, insights)
Level 7: Cross-function intelligence   (CounterParts sharing signals across functions)
Level 8: Outcome learning              (intervention success/failure feeds future reasoning)
```

Levels 0-2 make it not-alerts. Levels 3-8 make it a **partner**.

### Architecture

```
+------------------------------------------------------------------+
|                       bc-ai (port 4300)                           |
|                                                                   |
|  Existing Flows:                                                  |
|    bo-suggest, field-map, metric-trace,                           |
|    eval-advise, chain-audit, kpi-ask                              |
|                                                                   |
|  Metis Engine (new)                                               |
|  +------------------------------------------------------------+  |
|  |                                                             |  |
|  |  +------------------+    +-------------------+              |  |
|  |  | Observation      |    |  Reasoning Engine |              |  |
|  |  | Reader           |--->|  (Bedrock LLM)    |              |  |
|  |  +------------------+    +--------+----------+              |  |
|  |                                   |                         |  |
|  |  Reads from bc-core:              |  AI capabilities:       |  |
|  |  - metric_snapshot                |  1. Causal tracing      |  |
|  |  - boundary_health                |  2. Cross-metric        |  |
|  |  - evidence + lineage             |     pattern matching    |  |
|  |  - intervention_contract          |  3. Intervention        |  |
|  |  - metric DAG                     |     composition         |  |
|  |  - org hierarchy                  |  4. Outcome learning    |  |
|  |                                   |                         |  |
|  |                +------------------v------------------+      |  |
|  |                |         Metis Composer              |      |  |
|  |                |  Action Object + Evidence + Thread  |      |  |
|  |                +------------------+------------------+      |  |
|  |                                   |                         |  |
|  |                +------------------v------------------+      |  |
|  |                |      Communication Router           |      |  |
|  |                |  In-App | WhatsApp | Teams | Email  |      |  |
|  |                +------------------+------------------+      |  |
|  |                                   |                         |  |
|  |                +------------------v------------------+      |  |
|  |                |      Thread Manager                 |      |  |
|  |                |  Bidirectional | Escalation | Followup    |  |
|  |                +------------------+------------------+      |  |
|  |                                   |                         |  |
|  |                +------------------v------------------+      |  |
|  |                |      Suo Moto Engine                |      |  |
|  |                |  Reports | Insights | Coverage Gaps |      |  |
|  |                +-------------------------------------+      |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

## Capability Detail

### Capabilities 1-3: AI Reasoning (from original D251)

#### Causal Reasoning Through Lineage

Metis reads the **full evidence chain** before evaluating an intervention contract:

```
Metric Snapshot (AR aging = 47 days, breached threshold)
  +-- Evidence: computed from CO "ar-open-items" v3
       +-- CO boundary_health: STALE (last evaluation 3 days ago)
            +-- SO boundary_health: HEALTHY (data flowing)
                 +-- Root cause: canonical mapping broke, not business deterioration
```

**Metis decision:** Do not fire the intervention contract. Surface a boundary health alert to operations instead. The metric is stale, not genuinely deteriorating.

#### Cross-Metric Pattern Recognition

Metis watches the entire function's metric constellation:

```
Finance function — 411 KPIs
  AR aging: 43 days (within threshold)
  DSO: 38 days (within threshold)
  Customer churn: 2.1% (within threshold)
  Revenue growth: -0.3% (within threshold)

  Individual: all green
  Pattern: CORRELATED DETERIORATION across AR cluster
    -> 4 metrics moving negative simultaneously
    -> Historical match: Q3 2025 showed same signature before collection crisis
```

**Metis decision:** Fire intervention contract proactively, before any single metric breaches.

#### Intervention Composition

Metis composes **rich Action Objects**:

```json
{
  "action_object": {
    "metric_contract_id": "metric-ar-aging-v1",
    "target_value": 38,
    "owner": "priya@tenant.com (selected: AR domain expertise, availability)",
    "cycle_end": "2026-05-01",
    "rationale": {
      "trigger": "Cross-metric pattern: AR cluster deterioration",
      "root_cause": "3 large invoices from Customer X exceeded payment terms",
      "business_impact": "Projected DSO breach in 2 cycles if uncorrected",
      "historical_context": "Customer X: same pattern Q3 2025, resolved via direct escalation",
      "recommended_action": "Escalate to collections per IC-0042. Contact Customer X AP."
    }
  }
}
```

### Capability 4: Bidirectional Communication

Metis doesn't send notifications — it opens **conversation threads**. Each intervention creates a thread that lives across channels.

**Metis -> Owner:**
```
"I've flagged AR aging deterioration. 3 invoices from Customer X
 are overdue totaling $240K. Based on Q3 2025 precedent, direct
 AP escalation resolved this in 5 days. I've set a target of
 38 days by May 1. [View Evidence] [Acknowledge] [Ask Me Why]"
```

**Owner -> Metis:**
```
"I've contacted Customer X AP. They say payment is processing,
 expect clearance by April 10."
```

**Metis -> Owner:**
```
"Noted. I'll monitor the AR feed for Customer X payment.
 If cleared by April 10, I'll update the Action Object and
 notify Mike (your manager). If not cleared, I'll nudge you
 on April 11. Thread stays open until cycle evaluation."
```

**The thread is the unit of work**, not the notification. Metis remembers context, tracks commitments, and follows up.

### Capability 5: Hierarchy-Aware Escalation

Tenants capture their org structure in bc-portal (new UI). Metis uses it for role-appropriate communication and escalation.

**Org hierarchy example:**
```
CFO (Sarah)
  +-- VP Finance (Mike)
       +-- AR Manager (Priya)     -> owns: AR aging, DSO, overdue ratio
       +-- AP Manager (James)     -> owns: DPO, early payment discount
       +-- Controller (Lin)       -> owns: close cycle time, journal accuracy
  +-- VP Treasury (Raj)
       +-- Cash Manager (Ana)     -> owns: cash conversion, liquidity ratio
```

**Role-based communication:**

| Role | Metis Communicates | Format | Example |
|------|-------------------|--------|---------|
| **Metric Owner** (Priya) | Detailed intervention: root cause, evidence, action items | Conversational thread | "3 invoices from Customer X overdue..." |
| **Manager** (Mike) | Escalation + team digest | Summary + escalation alert | "Priya has 3 open interventions, 1 unacknowledged for 4 days" |
| **Executive** (Sarah) | Function health + cross-function patterns | Executive brief | "Finance: 5 interventions this week, AR cluster trending negative" |
| **Operations** | Boundary health issues (data, not business) | Technical alert | "Canonical mapping for SAP FI broke — 12 metrics stale" |

**Escalation ladder:**
```
Day 0:  Intervention fired -> Owner (Priya) notified
Day 2:  No acknowledgment -> Metis nudges Priya
Day 4:  Still no action -> Metis escalates to Manager (Mike)
        "3 AR interventions unacknowledged by Priya this week.
         Highest risk: Customer X overdue $240K."
Day 7:  Closure window approaching -> Metis escalates to Executive (Sarah)
        "Finance has 5 open interventions, 2 approaching closure
         without owner action."
```

Escalation timing is configurable per tenant. The hierarchy UI captures structure AND escalation policy.

### Capability 6: Suo Moto Actions

Metis doesn't wait for breaches. It **proactively contributes** on its own initiative.

#### Periodic Health Reports (auto-generated)
```
"Metis Weekly Finance Brief — Week 14"
  - 411 KPIs monitored, 3 interventions fired, 2 resolved, 1 open
  - AR cluster trending negative (-2.3% WoW) — no breach yet, watching
  - Best improvement: Journal accuracy +4% after Lin's process change
  - Recommendation: Consider adding IC for vendor payment terms (no coverage)
```

Sent to the executive automatically on schedule. No one asked — Metis produces it on its own.

#### Pattern Insights (unprompted)
```
"I noticed Q1 close cycle time improved 15% after the admission
 contract for SAP FI was tightened in February. The same pattern
 might apply to AP — your AP admission contract has looser
 validation rules. Want me to draft a tighter AC for review?"
```

Metis connects **intervention outcomes to contract improvements** — closing the loop back to the admission boundary.

#### Coverage Gap Analysis
```
"Finance has 411 KPIs. 38 have intervention contracts.
 12 high-priority KPIs (by metric DAG centrality) have no IC.
 Top 3 uncovered: Revenue Recognition Accuracy, Intercompany
 Reconciliation Rate, Tax Provision Variance.
 Want me to draft ICs for these?"
```

### Capability 7: Cross-Function Intelligence

CounterParts across functions share signals:

```
"HR CounterPart detected elevated attrition in the Finance team.
 Finance CounterPart correlating: journal accuracy degraded 3%
 in the same period. Possible cause: team instability affecting
 close quality. Flagging to CFO and CHRO jointly."
```

This is where the constellation of Metis agents becomes more than the sum of parts. Each function's CounterPart is independent, but they read each other's signals through a shared intelligence layer.

### Capability 8: Outcome Learning

The feedback loop that makes Metis smarter over time:

```
Intervention fired (Day 0)
  -> Owner acknowledges (or ignores — Metis escalates)
  -> Owner reports action taken
  -> Cycle ends -> System evaluates: baseline vs actual (D250)
  -> Outcome: improved / deteriorated / no_change
  -> Metis LEARNS:
     "Direct escalation to Customer X AP resolved AR in 5 days"
     "This pattern + this intervention = 80% success rate"
     Future: recommend same intervention type with higher confidence
```

Over time, Metis builds a **function-specific intervention knowledge base**: which actions work for which patterns in this tenant's business. This is not transferable across tenants (tenant data isolation) but accumulates within each tenant.

## Communication Channels

### In-App (bc-portal)
- Richest experience: full evidence chain, metric charts, lineage visualization
- Thread view with conversation history
- Owner can reply, acknowledge, dismiss, ask follow-up questions
- Executive dashboard with all active Metis threads across functions

### WhatsApp Business API
- Mobile-first nudges for metric owners
- Structured messages with action buttons: [View] [Acknowledge] [Dismiss] [Ask Why]
- Owner replies in natural language — Metis understands and updates thread
- Follow-up reminders on schedule

### Microsoft Teams
- Enterprise standard integration
- Adaptive cards with intervention summary
- Channel posts for team-level digests
- Direct messages for individual escalations

### Email
- Executive briefs and weekly digests
- Escalation notifications
- Formal reports (PDF attachment for board-level)

### Channel-Agnostic Thread
The conversation is **ONE thread** regardless of channel. Owner starts in Teams, continues in-app, gets a WhatsApp reminder. Same context, same history. The thread is stored in bc-ai; channels are delivery mechanisms.

## Tenant Configuration (new bc-portal screens)

1. **Org Hierarchy** — reporting lines, role assignments, metric ownership per function
2. **Escalation Policy** — per-function escalation timing, auto-escalation rules
3. **Communication Preferences** — per-user channel preferences (WhatsApp/Teams/email/in-app)
4. **Metis Settings** — per-function: enable/disable, suo moto frequency, report schedule, budget cap
5. **Metis Thread View** — conversation history per intervention, across all channels

## Scoping

- **Per-function:** Each of the 18 business functions gets its own Metis CounterPart instance. No god-agent.
- **Per-tenant:** Scoped to tenant contract bindings. Tenant A's Finance CounterPart only sees Tenant A's data.
- **Contract-bound:** Metis evaluates intervention contracts. No IC = observe only, do not act.
- **Budget-bound:** Per-tenant daily budget caps. Tiered evaluation (Haiku for screening, Sonnet for composition).

## Integration with bc-ai Infrastructure

| Existing bc-ai Feature | Metis Usage |
|------------------------|-------------|
| Maker-checker-gate pipeline | Reasoning (maker) + validation (checker) + quality gate |
| Bedrock inference profiles | Sonnet for composition, Haiku for screening/classification |
| Evidence storage (SQLite) | Intervention reasoning traces + thread history |
| Budget management | Per-tenant daily budget caps on Metis invocations |
| Review queue | Amber-routed interventions require human approval |
| Model registry + fallback | Automatic model fallback if primary unavailable |

## Options Considered

### Option A: Static rule engine (rejected)
Cannot trace evidence chains, recognize patterns, compose business context, learn from outcomes, or communicate bidirectionally. This is what every monitoring tool does. No differentiation.

### Option B: Metis in bc-core (rejected)
bc-core is the execution backbone — no LLM dependencies, no variable-latency agent invocations. Separation of concerns: bc-core preserves data, Metis reasons over it.

### Option C: Metis in bc-ai (selected)
bc-ai has Bedrock integration, maker-checker-gate pipeline, evidence storage, budget management, review queue. Metis becomes a new module (`metis/`) in the existing architecture.

## Consequences

### Positive

1. **Product differentiation** — "BareCount doesn't just measure your business — Metis, your CounterPart, watches it for you." No competitor offers evidence-grounded, hierarchy-aware, bidirectional AI intervention.
2. **Evidence architecture pays off** — lineage built for auditability becomes Metis's reasoning substrate. Every boundary that preserves evidence makes Metis smarter.
3. **Feedback loop drives improvement** — intervention outcomes feed back into Metis's knowledge base AND into contract improvement recommendations. The platform gets better with use.
4. **Premium monetization** — Metis is the premium tier. Basic: dashboards + alerts. Pro: Metis CounterParts with full capability stack.
5. **Cross-function intelligence** — unique value that single-function tools cannot provide. The constellation of CounterParts sees what no individual tool can.

### Risks

1. **LLM cost** — mitigated by budget caps, tiered model usage, smart scheduling
2. **False positives** — mitigated by review queue, IC rules, tenant disable controls
3. **Channel integration complexity** — WhatsApp Business API + Teams + email requires significant integration work. Phase by channel.
4. **Org hierarchy maintenance** — tenants must keep hierarchy current. Stale hierarchy = wrong escalation. Mitigate with periodic "is this still correct?" prompts.
5. **Trust** — tenants must trust Metis enough to act on its recommendations. Build trust gradually: start with suo moto reports (low risk), then threshold interventions, then proactive pattern interventions.

## Implementation Phases

1. **Phase 0: Foundation** — `metis/` module in bc-ai. Single-metric threshold evaluation. In-app notification only. Validates the pipeline.
2. **Phase 1: Reasoning** — Causal tracing through evidence chains. Distinguishes data problems from business problems.
3. **Phase 2: Composition** — Rich Action Objects with business context. Bidirectional in-app threads.
4. **Phase 3: Hierarchy** — Org structure UI in bc-portal. Role-based communication. Escalation ladder.
5. **Phase 4: Channels** — WhatsApp Business API integration. Teams integration. Email digests.
6. **Phase 5: Patterns** — Cross-metric constellation analysis. Proactive pattern detection.
7. **Phase 6: Suo Moto** — Auto-generated reports. Coverage gap analysis. Contract improvement recommendations.
8. **Phase 7: Cross-Function** — CounterParts sharing signals across functions. Joint escalations.
9. **Phase 8: Learning** — Outcome tracking. Intervention knowledge base. Confidence calibration.

## References

- D250 (DEC-bae0ef): IC Simplification — intervention contract body, Action Object model
- D068 (DEC-ecec75): Metric Architecture — one contract per KPI, metric DAG, domain taxonomy
- D085 (DEC-db1c63): Metric as Data Product — AI activation metadata, output schema
- D165: Intervention Contract Family — 6th contract family, intervention evaluation boundary
- D162 (DEC-351108): Execution model — fixed object progression, boundary tables, evidence
- Greek mythology: Metis, titaness of Good Counsel and Cunning Intelligence
