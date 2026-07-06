---
uid: DEC-c566f3
title: "D223: KPI Catalog AI Assistant — Structured Retrieval + Grounded LLM"
description: "KPI assistant architecture: structured retrieval + grounded Bedrock LLM, no RAG/vector DB"
status: decided
subdomain: metric-catalog
focus: ai-qa-over-kpi
date: 2026-03-29
project: bc-ai
domain: metrics
refs:
  - type: decision
    uid: DEC-e9294b
    label: "D222: bc-ai Platform AI Orchestration Service"
  - type: decision
    uid: DEC-ecec75
    label: "D068: Metric Architecture — one contract per KPI"
  - type: document
    path: "architecture/database/schema-map.md"
    label: "Platform DB schema map"
  - type: plan
    uid: PLN-18cb0b
    label: "bc-ai implementation plan (Phase C0 addition)"
  - type: plan
    uid: PLN-86b3fc
    label: "Metric Catalog enrichment plan (data backbone)"
authority: authoritative
migrated_from: legacy v2 archive
---

# D223: KPI Catalog AI Assistant — Structured Retrieval + Grounded LLM

## Context

BareCount is building a 10K KPI catalog across 5 detailed tables (metric_definition, metric_formula, metric_formula_variable, metric_knowledge, metric_formula_verification) with enriched formulas, variable bindings, knowledge context, stakeholders, thresholds, and search tags. Tenant databases hold computed metric_snapshot rows with actual values, threshold states, and quality signals.

Users need a way to ask business questions in plain language ("How fast are we collecting from customers?") and get deterministic, auditable answers grounded entirely in our data — no internet knowledge, no hallucination.

### Requirements

1. **Natural language input** — business users, not SQL
2. **Deterministic outputs** — every number from a DB column, never generated
3. **Strictly our data** — no LLM training data, no internet, no external sources
4. **Auditable** — every claim traces to a metric ID and snapshot timestamp
5. **Tenant-scoped** — user only sees their contracted metrics
6. **Trust guardrails** — anti-hallucination, anti-misuse, PII protection

## Decision

Use **structured SQL retrieval + grounded LLM synthesis** on Bedrock. The AI is a translator, not a calculator.

### Architecture

```
User question (natural language)
  |
  v
+----------------------------------+
| Step 1: Intent -> KPI Resolution |  Model: Haiku 4.5
| Maps natural language to         |  Latency: ~200ms
| metric_definition_id(s)          |  Cost: ~$0.001/query
| Extracts: function, category,    |
| search terms, comparison intent  |
+----------------------------------+
  |
  v
+----------------------------------+
| Step 2: Catalog Lookup           |  Pure SQL -- no AI
| Platform DB (bc_platform_dev):   |
|   metric_definition              |  name, function, category, tags
|   + metric_formula               |  O1 = (I1/I2) * C1
|   + metric_formula_variable      |  I1=accounts_receivable, etc.
|   + metric_knowledge             |  context, stakeholders, thresholds
| Uses: FTS (search_vector) +      |
|       relational JOINs + filters |
| Returns: top-N KPI records       |
+----------------------------------+
  |
  v
+----------------------------------+
| Step 3: Snapshot Lookup          |  Pure SQL -- no AI
| Tenant DB (tbc_{slug}_dev):      |
|   metric_snapshot                |  metric_value_json (the number)
|   -> threshold_state_json        |  green/amber/red vs target
|   -> quality_signals_json        |  confidence, completeness
|   -> input_references_json       |  lineage to source objects
|   -> evaluated_at                |  when it was computed
| Falls back gracefully if no      |
| snapshot exists yet              |
+----------------------------------+
  |
  v
+----------------------------------+
| Step 4: Grounded Composer        |  Model: Sonnet 4.5
| System prompt enforces:          |  Latency: ~1-2s
|  - ONLY use provided data        |  Cost: ~$0.01/query
|  - Cite MT-{seq} for every claim |
|  - If no data, say "no data"     |
|  - Never advise, only inform     |
| Input: question + KPI records    |
|        + snapshot values          |
| Output: natural language with    |
|         citations                |
+----------------------------------+
  |
  v
+----------------------------------+
| Step 5: Output Validator         |  Code -- deterministic
|  - Every MT-xxx in response      |
|    must exist in retrieved set   |
|  - Every number must trace to    |
|    a field in the input data     |
|  - Strip uncited claims          |
|  - Confidence disclosure if      |
|    <3 KPIs matched               |
+----------------------------------+
```

### Example

**User asks:** "How fast are we collecting from customers?"

**Step 1 resolves:** MT-0042 (Days Sales Outstanding), MT-0039 (Collection Effectiveness Index)

**Step 2 returns:**
- MT-0042: DSO, formula `O1 = (I1 / I2) * C1`, variables: I1=accounts_receivable, I2=net_credit_sales, C1=365, unit=days, stakeholders=[CFO, AR Manager], threshold: good <35, amber 35-60, red >60

**Step 3 returns:**
- MT-0042: value=47, threshold_state=amber, evaluated_at=2026-03-28, quality=high

**Step 4 composes:**

> "Your Days Sales Outstanding is **47 days** (as of Mar 28). This measures how quickly you collect receivables, computed as Accounts Receivable / (Net Credit Sales / 365). Current status: **amber** — target is under 35 days. Your Collection Effectiveness Index (MT-0039) is at 82%, which provides additional context on collection quality. Stakeholders: CFO reviews monthly, AR Manager reviews weekly."

Every number, every metric name, every threshold — from the DB.

### Model Assignment

| Role | Model | Justification |
|---|---|---|
| Intent classifier / KPI resolver | Haiku 4.5 | Fast (~200ms), cheap, structured JSON output |
| Response composer | Sonnet 4.5 | Quality prose, follows grounding constraints reliably |
| Fallback composer | Nova Pro | If Sonnet throttled |
| Input/output guardrails | Bedrock Guardrails | Native integration, no custom code for content filtering |

### Guardrail Architecture (3 layers)

**Layer 1 — Input (Bedrock Guardrails):**
- Topic block: reject questions not about KPIs/metrics/business performance
- PII filter: block personal data in queries
- Injection defense: detect prompt manipulation attempts
- Tenant fence: user can only query their contracted metric scope

**Layer 2 — Retrieval (deterministic code):**
- Hard ceiling: never pass >20 KPI records to the composer
- Tenant scope: SQL WHERE clause enforces tenant's contracted metric set via metric_binding -> contract_binding
- No cross-tenant leakage: query always includes tenant filter before LLM sees anything
- No snapshot without contract: uncontracted metrics return definition only, no values

**Layer 3 — Output (code + Bedrock):**
- Citation validation: every MT-xxx must exist in retrieved set
- Number validation: every number must trace to a field in the input data
- Confidence disclosure: if <3 KPIs matched, state "limited results"
- No-advice guardrail: "I can explain what this KPI measures, but I cannot advise on business decisions"
- Bedrock content filter: block harmful/biased/inappropriate output
- Audit log: every query + response logged with user_id, tenant_id, KPI IDs, model, tokens

## Options Considered

### Option A: RAG with Vector Embeddings (REJECTED)
- Embed metric_knowledge into vector store (pgvector/Pinecone/OpenSearch)
- Semantic search -> retrieve top-K -> LLM synthesizes
- **Rejected because:** Our data is structured and relational, not unstructured documents. SQL with FTS already indexed. Vector DB adds infrastructure (embedding pipeline, sync on every KPI change, re-indexing) for zero value over what PostgreSQL gives us. Also cannot retrieve computed snapshot values — only definitions.

### Option B: Fine-tuned Model (REJECTED)
- Train a model on our 10K KPIs
- **Rejected because:** Fine-tuned models are frozen snapshots — our catalog changes daily during enrichment. Hallucination risk increases (model memorizes patterns, invents plausible KPIs). Expensive to retrain. Impossible to audit which training example produced a response.

### Option C: Hosted External Model — GLM-5 / other (REJECTED)
- Host a separate model (GLM-5, Llama, etc.) on EC2/SageMaker
- **Rejected because:** Adds a vendor, deployment, billing stream, and latency hop. bc-ai already has Bedrock connected with 7 models green. No Bedrock Guardrails integration — would build guardrails from scratch. No advantage for structured data grounding tasks.

### Option D: Structured Retrieval + Grounded LLM on Bedrock (SELECTED)
- As described in Decision section above
- **Selected because:** Zero new infrastructure. Always fresh (live DB queries). Auditable (every claim traces to MT-xxx + snapshot). Cheap (~$0.01/query). Trust by architecture, not by model choice.

## Consequences

### Positive
- Every answer is auditable — traces to specific KPI IDs and snapshot timestamps
- Zero hallucination by design — LLM never sees its own training data about KPIs
- Always current — query hits live DB, no re-indexing on KPI changes
- Cheap — estimated $11/day at 1,000 queries/day
- No new infrastructure — uses existing PostgreSQL + Bedrock
- Becomes foundation for full CXO Assistant (PLN-18cb0b Phase C)

### Negative
- Fuzzy/exploratory queries ("metrics related to sustainability") depend on quality of metric_knowledge.search_tags — catalog enrichment quality matters
- Intent classification can pick the wrong KPI — mitigated by showing matched KPIs for user correction
- Requires metric_snapshot rows to exist for value responses — tenants with no computed snapshots get definition-only answers

### Implementation Path (Phase C0 in PLN-18cb0b)

| Step | Deliverable | Sessions |
|---|---|---|
| C0.1 | KPI resolver endpoint: `POST /api/ai/kpi/resolve` — NL to metric_definition_id(s) | 1 |
| C0.2 | Snapshot retrieval service — metric IDs + tenant -> latest snapshots with full context | 1 |
| C0.3 | Grounded composer + output validator | 1 |
| C0.4 | Bedrock Guardrails configuration | 0.5 |
| C0.5 | bc-portal chat UI — panel with structured responses + citation links | 1-2 |
| **Total** | | **4-5 sessions** |

Runs in parallel with metric catalog enrichment (PLN-86b3fc) — every newly enriched KPI becomes instantly queryable.

### Cost Estimate

| Component | Per-query | At 1,000 queries/day |
|---|---|---|
| Haiku 4.5 (intent) | ~$0.001 | $1/day |
| Sonnet 4.5 (composer) | ~$0.01 | $10/day |
| PostgreSQL queries | negligible | negligible |
| Bedrock Guardrails | included | included |
| **Total** | ~$0.011 | **~$11/day** |

---

## Addendum A: Dual-Provider Pattern (dev/prod)

Grounding is architecture-dependent, not host-dependent. The model receives the same system prompt + retrieved DB rows regardless of transport. For dev/testing, use Anthropic API directly; for production, use Bedrock.

```
LLM_PROVIDER=anthropic     # dev — Anthropic API key
LLM_PROVIDER=bedrock       # prod — IAM role, Bedrock Guardrails
```

Abstract client in `bc-ai/clients/llm.py`:

| Role | Bedrock (prod) | Anthropic API (dev) |
|---|---|---|
| Intent resolver | Haiku 4.5 (inference profile) | claude-haiku-4-5-20251001 |
| Composer | Sonnet 4.5 (inference profile) | claude-sonnet-4-5-20241022 |
| Fallback | Nova Pro | Haiku 4.5 |

What differs by provider:
- Bedrock Guardrails (native) — production only. Dev uses code-based guardrails (output validator).
- IAM auth vs API key — deployment concern, not grounding concern.
- CloudWatch metrics — production only. Dev logs to bc-ai SQLite.

---

## Addendum B: User-Scoped Access Control (4-fence model)

### Problem

Department users must only see KPIs relevant to their function and access level. A Finance accountant cannot see HR KPIs. Within Finance, an accountant may not see executive-level ratios (ROIC, EVA). Access must be enforced BEFORE data reaches the LLM — if the model never sees the KPI, it cannot leak it.

### Design

**Dimension 1: KPI classification (platform DB)**

Add `access_tier_code` to `metric_definition`:
- `operational` — transactional KPIs (AP aging, invoice count, headcount)
- `management` — department-level ratios and trends (DSO, CEI, turnover rate)
- `executive` — strategic/board-level KPIs (EVA, ROIC, shareholder return)

This is intrinsic to the KPI, not tenant-specific.

**Dimension 2: Role-based access policy (tenant DB)**

New table per tenant schema:

```sql
CREATE TABLE {tenant_schema}.metric_access_policy (
  policy_id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  role_code         text NOT NULL,
  function_code     text,           -- NULL = all functions
  subfunction_code  text,           -- NULL = all subfunctions
  max_tier_code     text NOT NULL
                    CHECK (max_tier_code IN ('operational','management','executive')),
  created_at        timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX uq_metric_access_policy__role_fn_sub
  ON {tenant_schema}.metric_access_policy(role_code, function_code, subfunction_code);
```

Example policy for a tenant:

| role_code | function_code | subfunction_code | max_tier_code |
|---|---|---|---|
| accountant | finance | accounts_receivable | operational |
| accountant | finance | accounts_payable | operational |
| ar_manager | finance | accounts_receivable | management |
| finance_director | finance | NULL | management |
| cfo | finance | NULL | executive |
| cfo | NULL | NULL | executive |
| hr_manager | human_resources | NULL | management |
| chro | human_resources | NULL | executive |

No matching policy row = zero results. **Fail closed.**

### 4-Fence Retrieval Model

The SQL query enforces 4 fences before any data reaches the LLM:

```
Fence 1: Tenant contract scope
  WHERE md.metric_definition_id IN (contracted metrics for this tenant)

Fence 2: Function scope
  AND (policy.function_code IS NULL OR policy.function_code = md.function_code)

Fence 3: Subfunction scope
  AND (policy.subfunction_code IS NULL OR policy.subfunction_code = md.subfunction_code)

Fence 4: Access tier
  AND tier_rank(md.access_tier_code) <= tier_rank(policy.max_tier_code)
```

All 4 fences are SQL WHERE clauses — deterministic, auditable, zero LLM involvement.

### Tier classification during enrichment

The 10K KPI catalog needs `access_tier_code` populated. This becomes an additional enrichment pass (alongside formula + knowledge):
- AI classifies each KPI as operational/management/executive based on name, description, stakeholders
- Human reviews executive-tier classifications (highest sensitivity)
- Default: `operational` (fail safe — no one gets accidentally elevated access)

---

## Addendum C: Full Query-to-Answer Flow (with error/rejection/failure routes)

### Flow Diagram

```
USER QUESTION
  |
  v
[G1] INPUT GUARD ──────────────────────────> REJECT: "off-topic"
  |  - Is it about KPIs/metrics?               User sees: "I can only answer
  |  - PII detected?                            questions about your business
  |  - Injection attempt?                       metrics and KPIs."
  |  - Rate limit exceeded?
  |  - Empty/gibberish?
  |
  | PASS
  v
[S1] INTENT RESOLVER (Haiku 4.5) ─────────> ERROR: model timeout/failure
  |  Input: question + user context             |
  |  Output: {                                  v
  |    intent: "find_kpis" | "explain_kpi"    FALLBACK: retry once with
  |            | "compare" | "trend"            fallback model (Haiku again)
  |    filters: { function, category, ...}      |
  |    search_terms: ["collection","AR"]        v
  |    confidence: 0.0-1.0                    FAIL: "I couldn't understand
  |  }                                         your question. Try rephrasing
  |                                             e.g. 'What KPIs measure AR
  | confidence < 0.3 ──────────────────────>    performance?'"
  |   CLARIFY: "Did you mean KPIs about       (logged as resolution_failure)
  |   [finance/collections] or [HR/retention]?"
  |
  | confidence >= 0.3
  v
[S2] CATALOG QUERY (PostgreSQL) ───────────> ERROR: DB connection failure
  |  Platform DB: metric_definition             |
  |    JOIN metric_formula                      v
  |    JOIN metric_formula_variable           FAIL: "Service temporarily
  |    JOIN metric_knowledge                   unavailable. Try again."
  |  WHERE:                                    (logged as db_error, alert)
  |    Fence 1: tenant contract scope
  |    Fence 2: function scope (user role)
  |    Fence 3: subfunction scope (user role)
  |    Fence 4: access tier (user role)
  |    + FTS match (search_vector)
  |    + filter match (function, category)
  |  LIMIT 20
  |
  | 0 results ─────────────────────────────> NO_MATCH: "No KPIs matching
  |                                           your query are available in
  | N results (1-20)                          your current scope. You have
  v                                           access to [Finance/AR] KPIs."
[S3] SNAPSHOT LOOKUP (Tenant DB) ──────────> ERROR: tenant DB unreachable
  |  tbc_{slug}: metric_snapshot                |
  |    WHERE metric_contract_id IN (...)        v
  |    ORDER BY evaluated_at DESC             DEGRADE: continue without
  |    LIMIT 1 per KPI                         snapshots — definition-only
  |                                             response (clearly stated)
  | Has snapshots ──> full response
  | No snapshots ───> definition-only
  |   "MT-0042 (DSO) is defined but has
  |    no computed value yet for your tenant."
  v
[S4] GROUNDED COMPOSER (Sonnet 4.5) ──────> ERROR: model timeout/failure
  |  System prompt:                             |
  |    "ONLY answer from provided data.         v
  |     Cite MT-{seq} for every claim.        FALLBACK: retry with fallback
  |     If no data, say 'no data available'.    model (Haiku 4.5)
  |     Never give business advice.             |
  |     Never invent numbers."                  v
  |  Input:                                   FAIL: return raw structured
  |    question + KPI records + snapshots       data as formatted table
  |  Output:                                    (no prose, but user still
  |    natural language with citations          gets the numbers)
  |                                             (logged as composer_failure)
  v
[G2] OUTPUT VALIDATOR (deterministic code)
  |  Check 1: Every MT-xxx in response
  |           exists in retrieved set?
  |    FAIL ──> strip uncited sentences
  |
  |  Check 2: Every number in response
  |           traces to input data?
  |    FAIL ──> strip sentences with
  |            ungrounded numbers
  |
  |  Check 3: Response contains advice
  |           or predictions?
  |    FAIL ──> append disclaimer:
  |            "This is informational only."
  |
  |  Check 4: Response is empty after
  |           stripping?
  |    FAIL ──> return structured table
  |            fallback (raw data, no prose)
  |
  | PASS (validated response)
  v
[G3] AUDIT LOG (deterministic code)
  |  Write to bc-ai SQLite:
  |    query_id, user_id, tenant_id,
  |    role_code, question_text,
  |    resolved_kpi_ids, snapshot_ids,
  |    model_used, input_tokens,
  |    output_tokens, response_text,
  |    fences_applied, strips_applied,
  |    latency_ms, timestamp
  |
  v
RESPONSE TO USER
  |
  | Structured payload:
  | {
  |   answer: "Your DSO is 47 days...",
  |   citations: [
  |     { id: "MT-0042", name: "DSO",
  |       value: 47, unit: "days",
  |       evaluated_at: "2026-03-28",
  |       threshold_state: "amber",
  |       link: "/metrics/MT-0042" }
  |   ],
  |   confidence: "high" | "medium" | "low",
  |   scope_note: "Showing Finance/AR KPIs",
  |   disclaimer: null | "informational only"
  | }
```

### Error Classification

| Code | Trigger | User Experience | System Action |
|---|---|---|---|
| `rejected_off_topic` | G1 blocks non-KPI question | Friendly redirect message | Log, no LLM cost |
| `rejected_pii` | G1 detects personal data | "Please don't include personal data" | Log, no LLM cost |
| `rejected_injection` | G1 detects prompt attack | Generic refusal | Log + alert |
| `rejected_rate_limit` | G1 rate limit exceeded | "Too many requests, try in 60s" | Log, no LLM cost |
| `resolution_low_conf` | S1 confidence < 0.3 | Clarification prompt | Log, minimal cost |
| `resolution_failure` | S1 model error after retry | "Couldn't understand, rephrase" | Log + alert |
| `no_match` | S2 returns 0 rows | "No KPIs in your scope match" | Log |
| `no_access` | S2 fences filter all results | "No KPIs available in your scope" | Log (indistinguishable from no_match to user) |
| `snapshot_missing` | S3 no snapshots for KPI(s) | Definition-only answer | Log |
| `snapshot_db_error` | S3 tenant DB unreachable | Definition-only (degraded) | Log + alert |
| `composer_failure` | S4 model error after retry | Structured table fallback | Log + alert |
| `validation_stripped` | G2 strips uncited content | Cleaned response (user unaware) | Log |
| `validation_empty` | G2 strips everything | Structured table fallback | Log + alert |
| `success` | Full path completes | Rich answer with citations | Log |

### Key Design Principle: Never Fail Silent, Always Degrade Gracefully

- Model fails → try fallback model → if both fail → return raw data as table
- Tenant DB fails → return definition-only (no values, clearly stated)
- Validation strips everything → return structured table (no prose)
- No match → tell user their scope, suggest refinement
- `no_access` is INDISTINGUISHABLE from `no_match` to the user — never reveal that a KPI exists but is denied (information leak)
