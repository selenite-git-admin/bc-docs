---
uid: DEC-e9294b
title: "bc-ai — Platform AI Orchestration Service (MCP + REST)"
description: "Standalone AI service providing maker-checker intelligence for all BareCount apps — model registry, prompt flows, evidence audit, budget controls"
status: implemented
subdomain: model-orchestration
focus: platform-ai-service
date: 2026-03-27
project: bc-core
domain: platform
supersedes: DEC-d214ed
refs:
  - type: decision
    uid: DEC-d214ed
    label: "BO-CO Enrichment Engine (superseded — narrow scope, now absorbed into bc-ai)"
  - type: decision
    uid: DEC-40b650
    label: "AI-assisted catalog verification (pattern reused)"
  - type: decision
    uid: DEC-d6f6e1
    label: "DevHub as MCP server (architectural precedent)"
  - type: decision
    uid: DEC-e50b83
    label: "Master port reservation (bc-ai gets 4300)"
  - type: decision
    uid: DEC-376c9c
    label: "DevHub as separate repo + EC2 (deployment precedent)"
  - type: decision
    uid: DEC-e29de9
    label: "BareCount is anti-pipeline: contract-first lifecycle system"
  - type: decision
    uid: DEC-ecec75
    label: "One contract per KPI (2,230 KPIs need AI-assisted chain composition)"
  - type: decision
    uid: DEC-90faff
    label: "Canonical-driven reader creation flow"
  - type: document
    path: "foundation/specification/"
    label: "Foundation Specification (LOCKED)"
  - type: document
    path: "component-references/090-uinbat-reader.md"
    label: "UinBAT Reader Component Reference"
authority: evolving
migrated_from: legacy v2 archive
---

# bc-ai — Platform AI Orchestration Service

## Context

### The Trust Problem

BareCount's value proposition is **trust in numbers**. Every metric traces back through an unbroken chain: KPI → Canonical Objects → Source Objects → raw source data. If any link in this chain is constructed incorrectly — wrong field mappings, wrong CO bindings, wrong business keys — the trust guarantee breaks **silently**. The user sees green pills but the numbers are wrong.

### What Happened (PLN-2ef37f Failure)

Manual SQL enrichment produced 4,495 metric bindings where `fields_used` = ALL Business Object fields (12/12, 15/15) instead of the 3-5 fields each KPI formula actually needs. 147 of 158 observation contracts are empty shells with no source wiring. The data looks complete but is semantically wrong.

### Why It Happened

The existing contract constructors (4 wizard APIs in bc-core) are **structurally correct but knowledge-blind**. They accept whatever inputs the caller provides and execute atomically. They don't know:

- What fields an "AR Invoice" Business Object should have
- That SAP field `BELNR` maps to `document_number`
- That "Days Sales Outstanding" uses 4 specific fields from 2 COs, not all 12
- That `company_code + fiscal_year + document_number` are the business keys for a journal entry

This domain knowledge today lives in **human heads** (or Claude sessions that die after use). There is no persistent, auditable, cross-checked intelligence layer.

### Why a Separate Service

DEC-d214ed (BO-CO Enrichment Engine) established the Claude + Gemini maker-checker pattern but embedded it as a one-off enrichment script. This approach has three fatal flaws:

1. **Ephemeral** — knowledge dies with the session, no persistent model registry or prompt versioning
2. **Narrow** — only covers BO enrichment, not field mapping, metric binding, or integrity checking
3. **Unauditable** — no evidence trail, no confidence scoring, no human review workflow

BareCount needs AI assistance across **every constructor** and **both apps** (bc-admin for platform team, bc-portal for customers). This requires a shared service, not scattered inline calls.

## Decision

### Create `bc-ai` — a standalone AI orchestration MCP server

`bc-ai` is a new BareCount service that provides domain-intelligent suggestions for all contract chain construction and validation. It serves as the **knowledge layer** that sits above the existing structural wizards.

### Architecture

```
┌─────────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Claude Code   │  │   bc-admin   │  │  bc-portal   │  │    DevHub    │
│  (dev sessions) │  │  (platform)  │  │  (customer)  │  │  (ops/audit) │
└────────┬────────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                  │                  │                  │
    MCP protocol        REST API           REST API          MCP protocol
         │                  │                  │                  │
┌────────┴──────────────────┴──────────────────┴──────────────────┴────────┐
│                              bc-ai (:4300)                               │
│                                                                          │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────┐ │
│  │    Model Registry    │  │    Prompt Flows     │  │   Evidence Store │ │
│  │                      │  │                      │  │                  │ │
│  │  • Claude (maker)   │  │  • bo-suggest        │  │  • Every call    │ │
│  │  • Gemini (checker) │  │  • field-map         │  │    logged with   │ │
│  │  • Dynamic list     │  │  • metric-trace      │  │    confidence,   │ │
│  │  • Health + fallback│  │  • integrity-check   │  │    cost, model,  │ │
│  │  • Cost tracking    │  │  • chain-validate    │  │    tokens, time  │ │
│  │                      │  │  • Per-service locks │  │  • Immutable     │ │
│  └─────────────────────┘  └─────────────────────┘  └──────────────────┘ │
│                                                                          │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────┐ │
│  │   Budget Controls   │  │   Review Queue      │  │   Drift Monitor  │ │
│  │                      │  │                      │  │                  │ │
│  │  • Per-model limits │  │  • Green: auto-ok    │  │  • Scheduled     │ │
│  │  • Per-service caps │  │  • Amber: human look │  │    re-validation │ │
│  │  • Daily/monthly    │  │  • Red: human must   │  │  • Model version │ │
│  │  • Kill switch      │  │  • UI in bc-admin    │  │    change detect │ │
│  │                      │  │  • API for bc-portal │  │  • Confidence    │ │
│  │                      │  │                      │  │    degradation   │ │
│  └─────────────────────┘  └─────────────────────┘  └──────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

### Core Principles

#### 1. Maker-Checker Pattern (Non-Negotiable)

Every AI suggestion goes through two independent models:

- **Maker** (default: Claude) generates the suggestion with confidence score
- **Checker** (default: Gemini) independently validates and assigns agreement score
- **Combined confidence** determines routing: auto-approve / human-review / human-required

```
maker_confidence × checker_agreement → combined_score

combined_score ≥ 0.90 → GREEN  (auto-approve, human can override)
combined_score ≥ 0.70 → AMBER  (human review recommended)
combined_score < 0.70 → RED    (human decision required)
```

Thresholds are configurable per flow. Conservative by default — trust is earned.

#### 2. Evidence at Every Call (Non-Negotiable)

Every AI interaction produces an immutable evidence record:

```
{
  evidence_id: uuid,
  flow_code: 'bo-suggest' | 'field-map' | 'metric-trace' | ...,
  entity_type: 'business_object' | 'observation_contract' | 'metric_binding' | ...,
  entity_id: uuid,

  maker: {
    model_id: 'claude-sonnet-4-6',
    model_version: '20250514',
    prompt_version: 'bo-suggest-v1.2',
    suggestion_json: { ... },
    confidence: 0.94,
    input_tokens: 1200,
    output_tokens: 800,
    latency_ms: 2300,
    cost_usd: 0.0045
  },

  checker: {
    model_id: 'gemini-2.0-flash',
    model_version: '2025-04',
    prompt_version: 'bo-check-v1.1',
    validation_json: { ... },
    agreement: 0.91,
    disagreements: [ { field: 'clearing_date', reason: '...' } ],
    input_tokens: 900,
    output_tokens: 400,
    latency_ms: 1100,
    cost_usd: 0.0008
  },

  combined_score: 0.855,
  routing: 'amber',

  human_decision: {
    decided_by: 'anant@selenite.co',
    decided_at: '2026-03-27T12:00:00Z',
    action: 'approved_with_changes',
    changes_json: { ... },
    reason: 'Added clearing_date per Gemini suggestion'
  },

  created_at: '2026-03-27T11:58:00Z'
}
```

This is not optional. This is the audit trail that proves BareCount's numbers are trustworthy.

#### 3. Model Registry with Dynamic Health

Models fail. APIs change. Versions get deprecated. The model registry handles this:

```
{
  models: [
    {
      model_id: 'claude-sonnet-4-6',
      provider: 'anthropic',
      role: 'maker',
      endpoint: 'https://api.anthropic.com/v1/messages',
      api_key_env: 'ANTHROPIC_API_KEY',
      status: 'active',           // active | degraded | unavailable | retired
      last_health_check: '...',
      avg_latency_ms: 2100,
      error_rate_7d: 0.002,
      cost_per_1k_input: 0.003,
      cost_per_1k_output: 0.015,
      fallback_model_id: 'claude-haiku-4-5'
    },
    {
      model_id: 'gemini-2.0-flash',
      provider: 'google',
      role: 'checker',
      endpoint: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent',
      api_key_env: 'GOOGLE_AI_API_KEY',
      status: 'active',
      fallback_model_id: 'gemini-2.5-flash'
    }
  ]
}
```

**Health checks run every 5 minutes.** If a model goes down, the service:
1. Marks it `degraded` or `unavailable`
2. Routes to fallback model
3. Logs the switch in evidence
4. Alerts via DevHub activity log

**Model version tracking:** When a provider updates a model (e.g., Anthropic replaces claude-sonnet-4-6), the registry detects the version change and flags all suggestions made with the old version for potential re-validation.

#### 4. Prompt Flows — Per-Service, Versioned, Lockable

Each AI capability is a **flow** — a versioned prompt template with input/output contracts:

```
flows/
  bo-suggest/
    v1.0/
      maker-prompt.md      — Claude prompt template
      checker-prompt.md    — Gemini validation prompt
      input-schema.json    — What the flow accepts
      output-schema.json   — What the flow returns
      config.json          — Thresholds, model preferences, locks
    v1.1/
      ...
  field-map/
    v1.0/
      ...
  metric-trace/
    v1.0/
      ...
```

**Locks:** A flow version can be locked (no modifications, no model changes). Critical for audit — "this suggestion was made with bo-suggest-v1.0 using claude-sonnet-4-6, and the prompt was locked at the time."

**Per-service model preferences:** Some flows may prefer different models. Field mapping might work better with Gemini's grounded search. Metric tracing might need Claude's reasoning depth. The flow config declares preferences; the model registry resolves availability.

#### 5. Budget Controls

```
{
  global: {
    daily_limit_usd: 50.00,
    monthly_limit_usd: 500.00,
    kill_switch: false          // Emergency stop — all AI calls blocked
  },
  per_model: {
    'claude-sonnet-4-6': { daily_limit_usd: 30.00 },
    'gemini-2.0-flash': { daily_limit_usd: 20.00 }
  },
  per_flow: {
    'bo-suggest': { daily_limit_calls: 500 },
    'metric-trace': { daily_limit_calls: 1000 }
  },
  dev_optimization: {
    prefer_claude_cloud_in_dev: true,   // Use Claude Code's built-in model when available
    prefer_cheaper_model_for_bulk: true  // Use Haiku/Flash for batch operations
  }
}
```

When a budget limit is hit, the service returns a clear error and logs it. No silent degradation.

#### 6. Scheduled Drift Reviews

AI suggestions can become stale:
- A model gets updated and behaves differently
- A BO's field composition changes after initial suggestion
- New source objects are discovered that affect mappings

bc-ai runs scheduled reviews:

```
{
  reviews: [
    {
      name: 'bo-field-drift',
      schedule: 'weekly',
      description: 'Re-validate BO field suggestions against current model versions',
      action: 'flag_degraded_confidence'    // Don't auto-change, just flag
    },
    {
      name: 'mapping-consistency',
      schedule: 'daily',
      description: 'Check that field mappings still align with source catalog changes',
      action: 'create_review_item'
    }
  ]
}
```

### AI Capability Flows (Initial Set)

#### Flow 1: `bo-suggest` — Business Object Field Composition

**Input:** BO name, function, subfunction, tier, existing fields
**Output:** Recommended field list with data types, semantic roles, business keys
**Maker knowledge:** Accounting standards (IFRS, GAAP), ISO 20022, ISO 11179, APQC process framework, industry models
**Checker validation:** Cross-reference against standards documentation, verify completeness and naming
**Consumer:** BO Create Wizard (bc-admin), bulk enrichment orchestrator

#### Flow 2: `field-map` — Source-to-Business Field Mapping

**Input:** BO fields, source system, source object, source fields
**Output:** Mapping pairs with confidence per pair, unmapped fields flagged
**Maker knowledge:** SAP table/field semantics (BKPF, BSEG, VBRK, etc.), Salesforce object models, Oracle EBS table structures
**Checker validation:** Verify data type compatibility, semantic alignment, business key preservation
**Consumer:** Observation Contract Wizard (bc-admin), customer onboarding (bc-portal)

#### Flow 3: `metric-trace` — KPI Formula-to-Field Resolution

**Input:** KPI name, formula, formula_explanation, available COs with their fields
**Output:** CO bindings with specific `fields_used` per binding, binding roles
**Maker knowledge:** KPI definitions, accounting formulas, ratio decomposition, temporal requirements
**Checker validation:** Verify formula completeness (all variables mapped), no orphan bindings, correct roles
**Consumer:** Metric Contract Wizard (bc-admin), bulk composition orchestrator

#### Flow 4: `evaluation-rules` — Business Key and Semantic Rule Suggestion

**Input:** BO name, field composition, function context
**Output:** Business key fields, evaluation tier, semantic rules
**Maker knowledge:** Entity identity patterns (what uniquely identifies a journal entry vs an invoice vs a payment)
**Checker validation:** Verify key minimality (no redundant keys), tier correctness
**Consumer:** Canonical Contract Wizard (bc-admin)

#### Flow 5: `chain-validate` — Semantic Integrity Check

**Input:** Full chain for a KPI (metric → CO bindings → OC field maps → source mappings)
**Output:** Per-link semantic validation, overall chain confidence, flagged issues
**Maker knowledge:** Does the chain make domain sense? Does DSO really need `material_group`?
**Checker validation:** Independent chain trace, cross-reference formula against bindings
**Consumer:** Integrity dashboard (bc-admin), onboarding readiness (bc-portal)

#### Flow 6: `chain-visualize` — Interactive Chain Map

**Input:** KPI ID or function scope
**Output:** Hierarchical chain graph with confidence annotations at each node
**Consumer:** bc-admin Integrity page (new visual map screen)

### Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Runtime** | Python 3.12+ | Founder's primary language — bc-ai is the trust layer, the person who cares most about trust must be able to read/debug/modify it directly |
| **Web framework** | FastAPI (async) | Auto-OpenAPI docs, Pydantic validation, async-native |
| **MCP Server** | `mcp` Python SDK | MCP protocol for Claude Code sessions |
| **AI Runtime** | **Amazon Bedrock** (boto3 bedrock-runtime) | Single AWS credential (barecount profile), consolidated billing, ap-south-1 region, same infrastructure as everything else |
| **Maker model** | Bedrock Claude Sonnet 4.6 (`global.anthropic.claude-sonnet-4-6`) | Best suggestion quality for domain-complex tasks. Verified working 2026-03-27. |
| **Checker model** | Bedrock DeepSeek V3.2 (`deepseek.v3.2`) | Different provider = true independence from Claude maker. Strong reasoning. On Bedrock = single credential + billing. |
| **QA Gate model** | Bedrock Claude Haiku 4.5 (`global.anthropic.claude-haiku-4-5-20251001-v1:0`) | Fast, cheap, rule-focused analysis of maker+checker outputs |
| **Fallback model** | Bedrock Amazon Nova Lite (`apac.amazon.nova-lite-v1:0`) | Ultra-cheap ($0.06/1M tokens) backup if primary models unavailable |
| **CXO Guardrails** | Bedrock Guardrails | Content filtering, PII detection, topic blocking — managed, not custom code |
| **CXO Knowledge** | Bedrock Knowledge Bases + S3 | RAG over bc-docs (Foundation spec, component refs, KPI definitions) — managed retrieval |
| **CXO Agent** | Bedrock Agents | Managed agent orchestration with tool use for CXO Assistant |
| **Data validation** | Pydantic v2 | Strict schemas on all AI inputs/outputs, runtime type checking |
| **Database** | SQLite via aiosqlite | Evidence store, config, model registry — same pattern as DevHub |
| **Prompt Templates** | Markdown files with Jinja2 variables | Human-readable, versioned in git, Python-native templating |
| **Config** | YAML files + DB overrides | Git for defaults, DB for runtime config |
| **Process management** | pm2 with Python interpreter | Same operational model as all BareCount services |

**Why Python, not TypeScript:**

bc-ai is architecturally isolated — it communicates with bc-core/bc-admin/bc-portal via JSON over HTTP and MCP protocol. No shared TypeScript imports. No `@barecount/types` dependency. The interface is pure JSON, validated by Pydantic schemas (stricter than TypeScript interfaces). The founder must be able to independently inspect, debug, and modify the trust layer without depending on Claude sessions.

**Why Bedrock-only (no Gemini/Google API):**

1. **Single credential** — `AWS_PROFILE=barecount`, already configured everywhere. No Google API keys to manage.
2. **Consolidated billing** — one AWS invoice. No separate Anthropic or Google bills.
3. **Data residency** — ap-south-1 region, data stays local
4. **Managed guardrails** — Bedrock Guardrails for CXO Assistant content safety (enterprise requirement)
5. **Managed RAG** — Bedrock Knowledge Bases for CXO Assistant grounded answers
6. **Managed agents** — Bedrock Agents for CXO Assistant orchestration
7. **No Claude price markup** — Bedrock charges same per-token price as direct Anthropic API
8. **Model diversity on one platform** — Claude (maker), DeepSeek V3.2 (checker), Nova (fallback) — all on Bedrock, true provider independence without multiple API accounts
9. **Verified working** — Claude Sonnet 4.6 and Nova Lite invoked successfully on 2026-03-27 from barecount account ap-south-1

**Model lineup (all Bedrock, ap-south-1):**

| Role | Model | Profile ID | Cost (per 1M tokens) |
|------|-------|-----------|---------------------|
| Maker | Claude Sonnet 4.6 | `global.anthropic.claude-sonnet-4-6` | $3 in / $15 out |
| Checker | DeepSeek V3.2 | `deepseek.v3.2` | ~$0.14 in / ~$0.56 out |
| QA Gate | Claude Haiku 4.5 | `global.anthropic.claude-haiku-4-5-20251001-v1:0` | $0.80 in / $4 out |
| Fallback | Amazon Nova Lite | `apac.amazon.nova-lite-v1:0` | $0.06 in / $0.24 out |

**What Bedrock manages vs what we build:**

| Component | Bedrock Managed | We Build |
|-----------|----------------|----------|
| Model access + infra | Yes | — |
| Content guardrails (CXO) | Yes | Configuration only |
| Knowledge base / RAG (CXO) | Yes | Index bc-docs in S3 |
| CXO agent orchestration | Yes | Configuration + tool definitions |
| Maker-checker-gate pipeline | No | Custom agent orchestration |
| QA Gate logic | No | Custom agent |
| Evidence store | No | SQLite |
| Budget per-flow tracking | No | Custom (AWS Cost Explorer for totals) |
| Prompt versioning + locks | No | Custom (git + DB) |
| MCP interface | No | Custom MCP server |
| Cache + Pin | No | Custom |
| Model preference registry | No | Custom |

### Port & Service

| Property | Value |
|----------|-------|
| Port | 4300 |
| pm2 name | `bc-ai` |
| Repo | `C:\MyProjects\bc-ai` (new) |
| DevHub slug | `bc-ai` |
| Language | Python 3.12+ |
| AI Runtime | Amazon Bedrock (ap-south-1) |
| AWS Profile | `barecount` (same as all services) |

### Dual Interface

**MCP Protocol** (for Claude Code sessions):
```
ai_suggest          — Run a flow (bo-suggest, field-map, metric-trace, etc.)
ai_validate         — Run checker independently on any suggestion
ai_evidence_list    — Query evidence records
ai_models_status    — Model registry health
ai_budget_status    — Current spend vs limits
ai_review_queue     — Pending human reviews
```

**REST API** (for bc-admin, bc-portal):
```
POST   /api/ai/suggest          — Run a flow
POST   /api/ai/validate         — Run checker
GET    /api/ai/evidence         — Query evidence
GET    /api/ai/models           — Model status
GET    /api/ai/budget           — Budget status
GET    /api/ai/reviews          — Review queue
POST   /api/ai/reviews/:id/decide  — Human decision on review item
GET    /api/ai/health           — Service health
```

### Integration with Existing Wizards

bc-ai does NOT replace the wizard APIs in bc-core. The wizards remain the **structural execution layer**. bc-ai is the **knowledge layer** that generates inputs for the wizards.

```
User clicks "Create Metric Contract" in bc-admin
  → Metric Wizard Step 1: Select KPI
  → bc-admin calls bc-ai: POST /api/ai/suggest { flow: 'metric-trace', input: { kpiId, formula, availableCOs } }
  → bc-ai returns: suggested CO bindings with fields_used + confidence
  → Metric Wizard Step 2: Shows suggestions with green/amber/red indicators
  → User reviews, adjusts if needed
  → Metric Wizard Step 3: Computation rules (also AI-suggested if desired)
  → Wizard completes → bc-core creates contracts atomically
  → bc-ai evidence record links to the created contract
```

The wizard UI in bc-admin gets an "AI Suggest" button on each step. Clicking it calls bc-ai. The suggestion appears inline with confidence indicators. The user can accept, modify, or ignore.

### Agent Architecture (Not Request-Response Services)

bc-ai capabilities are implemented as **agents**, not stateless service endpoints. An agent is autonomous, tool-using, multi-step, and self-correcting.

**Why agents, not endpoints:**

| Aspect | Service Endpoint | Agent |
|--------|-----------------|-------|
| Execution | Single prompt → single response | Multi-step with tool use and reasoning |
| Self-correction | None | Can retry, research deeper, validate own output |
| Context | Stateless per request | Maintains context across steps |
| Tool use | None | Reads DB, calls APIs, fetches docs, checks constraints |
| Composability | Endpoint A calls endpoint B | Agent A spawns Agent B |

**Agent Registry (initial set):**

| Agent | Role | Model | Purpose |
|-------|------|-------|---------|
| BO Composer | Maker | Claude | Generate BO field compositions from domain knowledge |
| Field Mapper | Maker | Claude | Map source fields to BO fields using system knowledge |
| Metric Tracer | Maker | Claude | Decompose KPI formula into CO field requirements |
| Evaluation Advisor | Maker | Claude | Suggest business keys, evaluation rules, semantic rules |
| Checker | Checker | Gemini | Independent validation of any maker output |
| QA Gate | Gate | Claude (different instance) | Analyze maker+checker outputs, gate quality |
| Chain Auditor | Auditor | Claude | Full chain semantic validation with drill-down |
| CXO Assistant | Customer | Claude | Conversational metric intelligence for executives |

Each agent has: system prompt, available tools, model preference, output schema, and evidence contract.

**Tool Registry (shared across agents):**

| Tool | Purpose |
|------|---------|
| `bc-core-api` | Read/write contracts, BOs, fields, mappings via bc-core REST API |
| `source-catalog` | Query source systems, objects, fields, field affinity |
| `standard-fields` | Look up ISO 11179, IFRS, APQC, ISO 20022 references |
| `sap-knowledge` | SAP table/field semantics (26,937 tables, field descriptions) |
| `evidence-store` | Write/read evidence records |
| `metric-knowledge` | KPI formulas, definitions, domain relationships |

### QA Gate — Evidence as Quality Assurance, Not Quality Control

Evidence is not a post-hoc log. It is an **active gate** that prevents bad suggestions from reaching humans.

**Pipeline: Maker → Checker → QA Gate → Human Review**

The QA Gate Agent runs after both maker and checker complete. It is a **third independent opinion** that:

1. **Compares** maker vs checker — identifies specific disagreements
2. **Validates constraints** — do suggested fields actually exist in the BO? Do COs exist?
3. **Detects hallucination patterns** — confidence 0.99 on an obscure field = suspicious
4. **Checks internal consistency** — does the suggestion contradict itself or existing data?
5. **Validates naming** — ISO 11179 compliance, BareCount naming conventions
6. **Makes gate decision:** PASS → enters review queue | FAIL → retry with feedback or escalate

```
QA Gate Output:
{
  gate_decision: 'pass' | 'fail' | 'retry',
  combined_confidence: 0.87,
  routing: 'green' | 'amber' | 'red',

  analysis: {
    maker_checker_agreement: 0.92,
    constraint_violations: [],
    hallucination_flags: [],
    consistency_issues: [],
    naming_violations: [],
  },

  retry_feedback: null,  // If 'retry': specific guidance for maker to re-run

  evidence_record: { ... }  // Immutable, created only after gate passes
}
```

**Evidence records are only created after the QA gate passes.** Failed attempts are logged separately as `draft_evidence` — visible for debugging but not in the production evidence trail.

### Trust Building — Conservative by Default

AI output is not trusted by default. Trust is earned empirically:

```
Phase A:  Everything → human review (agents suggest, humans decide)
Phase B:  Green → auto-approve for PROVEN patterns only (evidence shows >99% accuracy)
Phase C:  Green → auto-approve broadly, amber → human review
```

**Auto-approve thresholds are per-flow, per-pattern, based on historical accuracy.** The evidence store IS the proof. After 500 human-reviewed suggestions where the agent was right 498 times on BO field naming — that's when auto-approve earns its place for that specific flow.

### Idempotency — Cache + Pin Pattern

LLMs are non-deterministic. Same input → different output. Engineering mitigation:

**Deterministic layers (fully idempotent):**
- QA gate logic (rule-based)
- Evidence storage (same evidence_id → same record)
- Wizard execution (same inputs → same DB state)
- Tool calls (read BO, read fields — deterministic)

**Non-deterministic layers (mitigated):**
- Maker/checker outputs — mitigated via Cache + Pin:

```
1. First call: Agent runs → produces suggestion → hash the input
2. Cache: store suggestion keyed by input hash (TTL: configurable, e.g. 24h)
3. Second call with same input: return cached suggestion
4. Pin: once a human approves a suggestion, it becomes a "pinned decision"
   — future calls return the pinned version, agent does not re-run
5. Invalidation: pin expires when underlying data changes (BO modified, source catalog updated)
```

**Pinned decisions are fully idempotent and permanent.** The agent only re-runs when no cached/pinned result exists or when data changes.

### bc-portal Integration — CXO Assistant (Not Construction Aid)

bc-portal AI is fundamentally different from bc-admin AI. It is not about building the chain. It is about **consuming the chain intelligently**.

**Two distinct AI surfaces in BareCount:**

| | bc-admin (Platform) | bc-portal (Customer) |
|---|---|---|
| **User** | Platform architects | CFOs, COOs, CXOs |
| **Purpose** | Build the chain correctly | Consume the chain intelligently |
| **AI Role** | Construction agents (maker-checker-gate) | Conversational assistant |
| **Interaction** | Wizard steps with suggestions | Natural language Q&A |
| **Trust model** | Evidence trail for builders | Lineage drill-down for consumers |
| **Exposure** | Full internal detail | Sanitized, customer-safe |

**The CXO Assistant is an AI contract on top of the metric layer.** Instead of browsing dashboards, executives ask questions:

```
CFO: "Why did our DSO increase last quarter?"

Assistant → queries metric snapshots → traces chain → finds:
  - AR Invoice open_amount increased 23% (CO: co-ar-invoice)
  - Collection cycle lengthened from 34 to 41 days (CO: co-ar-receipt)
  - Top 3 customers account for 68% of overdue balance

CFO: "Show me the data behind that."

Assistant → renders:
  - Metric snapshot with timestamp + version
  - CO drill-down: which source objects contributed
  - Lineage: SAP BKPF/BSEG → SO → CO → Metric
  - Confidence: "This metric was computed from 14,230 source records,
    all traced through verified contracts"

CFO: "What can we do about it?"

Assistant → references intervention contracts:
  - "Intervention IC-001 recommends: escalate collections for invoices >60 days"
  - "3 customers match this threshold — here are the details"
```

**What makes this different from ChatGPT + a database:**

1. **Every answer has lineage.** The assistant doesn't just say "DSO went up." It shows exactly which source records, through which contracts, produced that number. The CXO can click any claim and see the evidence chain.

2. **Contract-bound answers.** The assistant only answers from contracted data. It cannot hallucinate a metric that doesn't have a complete chain. If the chain is broken, it says so explicitly.

3. **Tenant-isolated.** Customer A's assistant sees only Customer A's data. The AI never cross-references tenants.

4. **No BareCount internals exposed.** The customer never sees model names, prompt versions, confidence scores from our QA pipeline, or evidence records from chain construction. They see business answers with data lineage.

**Exposure protection architecture:**

```
bc-portal (customer) → bc-core (sanitization gateway) → bc-ai (internal)

bc-core sanitizes:
  - Strips: model names, prompt versions, token counts, cost, QA reasoning
  - Translates: confidence 0.94 → "High confidence"
  - Enforces: tenant isolation (SQL fence)
  - Adds: customer-friendly attribution ("Based on your SAP S/4HANA data")
  - Blocks: any query that would expose platform-level metadata
```

**bc-portal NEVER calls bc-ai directly.** All requests route through bc-core.

### Security & Guardrails

1. **No customer data values sent to AI models.** bc-ai receives metadata only (field names, types, KPI formulas, aggregated metrics) — never raw transaction data.
2. **API keys stored in environment variables**, never in config files or DB.
3. **Rate limiting** per caller (bc-admin, bc-portal, Claude Code sessions) and per tenant.
4. **Prompt injection defense:** All user-supplied inputs are sanitized before inclusion in prompts. CXO assistant inputs are especially guarded — customer-typed questions go through sanitization.
5. **Model output validation:** JSON schema validation on all AI responses before use.
6. **Kill switch:** Global emergency stop disables all AI calls instantly.
7. **Tenant data fence:** CXO assistant agent receives only the requesting tenant's data. Cross-tenant queries are architecturally impossible (SQL-level isolation).

### Why Not Embed in bc-core?

1. **Different lifecycle** — AI models change weekly, bc-core changes daily. Decoupled deployment.
2. **Different failure mode** — if AI is down, constructors still work manually. No cascading failure.
3. **Different cost profile** — AI calls cost money. Separate budget tracking and monitoring.
4. **Different scaling** — AI calls are I/O-bound (waiting for API responses). bc-core is CPU-bound (DB queries). Different resource profiles.
5. **Reusability** — bc-admin, bc-portal, Claude Code sessions, DevHub all call the same agent platform.

## Options Considered

### Option A: Embed AI in bc-core services (rejected)
Couples AI lifecycle to API lifecycle. Budget tracking scattered. No MCP interface for Claude Code sessions. No agent architecture.

### Option B: Client-side AI calls from bc-admin/bc-portal (rejected)
Exposes API keys to frontend. No server-side evidence logging. No QA gate. No cross-app consistency.

### Option C: Stateless service endpoints (rejected)
Simple request-response lacks self-correction, tool use, and multi-step reasoning. Insufficient for domain-complex tasks like KPI formula decomposition.

### Option D: Standalone bc-ai agent platform with MCP + REST (chosen)
Agent architecture enables multi-step reasoning with tool use. QA gate provides active quality assurance. Maker-checker-gate pipeline ensures trust. Dual interface serves all consumers. Evidence is a gate, not a log.

## Consequences

### Positive
- Every AI suggestion is auditable with confidence scores
- QA gate actively prevents bad suggestions from reaching humans
- Agents can self-correct and research deeper when uncertain
- Human-in-the-loop by default, auto-approve only for empirically proven patterns
- Model failures are handled gracefully with fallbacks
- Budget is visible and controllable
- CXO assistant creates a new product surface with lineage-backed answers
- Same agent platform serves all consumers

### Negative
- New service to deploy and maintain (mitigated: same tech stack as DevHub)
- Additional network hop for AI-assisted wizard steps
- API key management for multiple providers
- Cost of running three AI calls per suggestion (maker + checker + QA gate)
- Agent complexity is higher than simple endpoints

### Risks
- Model provider API changes could break agents (mitigated: health checks + fallbacks + model registry)
- AI suggestions could be wrong even with maker-checker-gate (mitigated: conservative auto-approve thresholds, evidence trail)
- Cost could escalate with bulk operations (mitigated: budget controls, cheaper models for bulk, cache+pin)
- CXO assistant could surface misleading answers (mitigated: contract-bound responses, lineage drill-down, broken chain disclosure)

## Relationship to DEC-d214ed (Superseded)

DEC-d214ed established the 3-stage enrichment pattern (Generate → Verify → Activate) for BO enrichment. This pattern is **preserved, generalized, and strengthened**:

- Stage 1 (Generate) → bc-ai Maker Agent
- Stage 2 (Verify) → bc-ai Checker Agent
- Stage 3 (NEW: Gate) → bc-ai QA Gate Agent
- Stage 4 (Activate) → existing wizard `complete` endpoints in bc-core

The difference: DEC-d214ed was a one-off script with logging. bc-ai is a persistent agent platform with active quality gating, evidence-as-QA, and a customer-facing CXO assistant surface.

The `bo_enrichment_log`, `bo_verification_log`, and `catalog_verification_log` tables referenced in DEC-d214ed and DEC-40b650 become evidence records in bc-ai's unified evidence store.
