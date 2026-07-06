---
id: bedrock-and-inference-profiles
order: 28
title: "Bedrock and Inference Profiles"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-authority-model, operating-model-overview, architecture, infrastructure, auxiliary-services, ai-architecture]
governing_sources:
  - Foundation
  - The Authority Model
  - Architecture
  - Infrastructure
  - Auxiliary Services
  - AI Architecture
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus home; this chapter exists in the AI section)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Bedrock and Inference Profiles

## Scope

This chapter records bc-ai's model substrate in its as-built state at the time of writing: the AWS Bedrock client, the inference profile model that AWS requires for region-bound serving, the model registry that resolves a role identifier to a provider plus a model identifier, the per-provider client classes (Bedrock, Anthropic API direct, Google Gemini), the budget controls that gate every model call, and the per-call cost recording that the budget controls consume.

This chapter sits between AI Architecture and AI Agents. AI Architecture records that bc-ai branches per provider; this chapter records what each branch does and how the model substrate is composed. AI Agents records the agent inventory that consumes the substrate; this chapter is the substrate.

This chapter does not redefine the AWS account, region, profile, or hosting topology (deferred to Infrastructure), the per-agent inventory or the maker-checker-gate triplet pattern (deferred to AI Architecture and AI Agents), the gate verdict authoring contract (deferred to AI Gates), the cross-family verification model (deferred to AI Trust and Verification), or the tenant-facing usage transparency surface (deferred to AI Usage Visibility). Concrete deploy figures (port number, AWS account identifier, region code, profile name) belong to Infrastructure per pattern 85; this chapter names the concepts and routes the figures.

**Governing source.** AI Architecture; Infrastructure; outline.md §4.4.

## Why Inference Profiles

AWS Bedrock requires inference profile identifiers for region-bound serving of model versions. A raw model identifier (the family-and-version string a developer might write into a prompt registry) does not encode the routing logic Bedrock applies under the hood when a model has multiple regional endpoints, capacity pools, or version aliases. The inference profile identifier abstracts the routing and binds the call to a specific regional posture (an Asia Pacific posture or a global posture, in bc-ai's case). The platform's discipline is to use inference profile identifiers, not raw model identifiers, for every Bedrock call.

The discipline lives in the model registry: every Bedrock-served model has a `profile_id` field that is what the Bedrock client passes to `invoke_model`. The bc-ai memory note records this commitment ("Must use inference profile IDs, not raw model IDs"); the registry encodes it.

The two posture prefixes in the readiness baseline are `apac.` (Asia Pacific) and `global.` (multi-region pool). Anthropic models on Bedrock typically come in both postures; Amazon Nova models typically come only in the regional posture. The choice of posture per model is a pricing-and-latency decision recorded in the registry; the chapter records the prefixes and routes the per-model price detail to the registry source file.

**Governing source.** `bc-ai/app/clients/bedrock.py`; `bc-ai/app/models/registry.py`.

## The Bedrock Client

The Bedrock client at `bc-ai/app/clients/bedrock.py` instantiates a boto3 session under the platform's AWS profile and the platform's region (Infrastructure owns both figures). The session creates two boto3 clients: a `bedrock-runtime` client for `invoke_model` calls and a `bedrock` client for service-level operations (used by health checks). All inference goes through `invoke_model`; the alternative `converse` API is not used at the time of writing.

The client branches the request body shape per provider family. Anthropic models on Bedrock require an `anthropic_version` field plus the standard message format the Anthropic SDK uses; Amazon Nova models require a different message wrapping plus an `inferenceConfig` block. The client detects the family from the inference profile identifier (the `_is_anthropic` helper in the same file) and constructs the appropriate body. The response shape also differs per family; the client extracts the text plus token usage in a family-specific extractor.

The client is the single Bedrock entry point for the entire bc-ai service. Every act that targets a Bedrock-served model goes through this client; there is no second Bedrock client.

**Governing source.** `bc-ai/app/clients/bedrock.py`.

## The Model Registry

The model registry at `bc-ai/app/models/registry.py` is an in-memory dictionary keyed by a role identifier (`maker`, `checker`, `gate`, plus role-and-position identifiers like `nova-pro` and `nova-pro-checker`) and resolving to a `ModelEntry` dataclass. Each entry carries:

| Field | Purpose |
|---|---|
| `model_id` | The platform-internal model identifier the registry resolves |
| `profile_id` | The Bedrock inference profile identifier (when the entry is Bedrock-served) or a model-string the SDK accepts (when the entry is direct Anthropic or Gemini) |
| `provider` | One of `google`, `anthropic-api`, or `amazon` (the latter implicit when not set); the agent base class branches on this field |
| `role` | The role this entry serves: maker, checker, or gate |
| `status` | The runtime health status; updated by the model health-check loop |

The registry is initialized at service startup (`model_registry.initialize()` runs in the FastAPI lifespan handler). Initialization registers the per-role entries and the fallback chains. The fallback chains are role-specific: the maker chain is `["nova-pro", "nova-lite"]`; the checker chain is `["nova-pro-checker", "nova-lite"]`; the gate chain is `["nova-lite", "nova-micro"]`. A code comment at the chain declaration ("Nova-only until Anthropic marketplace is resolved") names the current restriction: the fallback chains are Gemini-only because Anthropic-on-Bedrock availability for some model families has not been resolved upstream.

The cross-family pairing that AI Trust and Verification owns is realized in the readiness baseline by the Anthropic SDK direct path (see below). The Bedrock-served Anthropic models exist as registry entries but are not in the maker or checker fallback chains in the readiness baseline.

**Governing source.** `bc-ai/app/models/registry.py`.

## The Anthropic SDK Direct Path

Some bc-ai acts use the Anthropic Python SDK directly rather than calling Anthropic models through Bedrock. The direct client at `bc-ai/app/clients/anthropic_client.py` instantiates `anthropic.Anthropic(api_key=settings.anthropic_api_key)` and calls `messages.create` with the model name as a string (Claude Haiku 4.5, Claude Sonnet 4.5).

Two situations trigger the direct path. First, some checker roles for maker-checker-gate triplets: when a registered checker entry has `provider == 'anthropic-api'`, the agent base class invokes the direct client rather than the Bedrock client. Second, the KPI decomposition act uses Haiku 4.5 as Maker A, Sonnet 4.5 as Maker B, and Haiku 4.5 as moderator; all three calls go through the direct Anthropic client.

The direct path bypasses Bedrock's inference profile abstraction. The model identifier is a Claude marketing name (like `claude-haiku-4-5-20251001`) rather than an inference profile prefix. Pricing and budget tracking are computed against a separate price table because the Anthropic API list price differs from the Bedrock list price. The cost computation lives in the same evidence-store helper that the Bedrock client uses, parametrized by the model identifier.

**Governing source.** `bc-ai/app/clients/anthropic_client.py`; `bc-ai/app/kpi/decompose.py`.

## The Gemini Client

The Gemini client at `bc-ai/app/clients/gemini.py` configures the Google Generative AI SDK at module load time (`genai.configure(api_key=settings.gemini_api_key)`) and creates a `GenerativeModel` instance per call, parametrized by the model identifier. Two model strings are in current use: `gemini-2.5-flash` for the maker, gate, and KPI assistant calls, and `gemini-2.5-pro` for the session governance auditor (registered in `app/auditor/config.py`).

The client returns the generated text plus token usage. There is no streaming support at the time of writing; every call is a synchronous request-response. The current Gemini client does not compute cost, enforce the daily budget cap, or write to `budget_log`; the drift inventory records that gap.

**Governing source.** `bc-ai/app/clients/gemini.py`; `bc-ai/app/auditor/config.py`.

## Budget Controls

bc-ai enforces a daily spend cap for Bedrock and direct Anthropic calls. The cap and the alert threshold are configuration values in `app/config.py`: a daily limit and an alert threshold (the alert threshold sits below the limit so the operator has signal before the cap fires). The budget enforcement is a pre-call check: before every Bedrock or Anthropic-API call, the client queries the budget-log substrate for the day's accumulated cost and raises `BudgetExceededException` if the day's cost has reached the limit. The exception propagates to the FastAPI exception handler and surfaces as an HTTP 429 response. Gemini calls bypass this cap in the readiness baseline because the Gemini client does not call `BudgetStore`.

The budget is a hard block. There is no graceful degradation to a cheaper model when the budget is exceeded; the call fails and the calling service receives the structured failure. The drift inventory below records this as an operational limitation: an organization that wants budget-aware fallback (downgrade to a cheaper model when the daily cap is approached) does not get it from the readiness-baseline implementation.

The alert threshold is a soft signal. When the day's cost crosses the threshold, the budget summary endpoint surfaces an `alert: true` flag; no call is blocked. The alert is consumed by operators who watch the budget endpoint or by housekeeping agents that may be configured to notify on cap proximity (the housekeeping notification surface is queued; AI Usage Visibility records the gap).

**Governing source.** `bc-ai/app/config.py`; `bc-ai/app/clients/bedrock.py`; `bc-ai/app/clients/anthropic_client.py`.

## Per-Call Cost Recording

Every successful Bedrock or direct Anthropic call writes a row to the `budget_log` table in bc-ai's local SQLite. The row carries the model identifier, the act identifier (`flow_id` in the schema), the input and output token counts, the computed cost in USD, and the timestamp. Gemini calls are not represented in `budget_log` in the readiness baseline. The budget cap consults this substrate via `evidence_store.get_daily_spend()`; the budget summary endpoint reads it via `get_budget_summary()` which groups by model and act for operator inspection.

The cost computation is a token-count-times-price computation against static price tables maintained by the Bedrock and Anthropic clients. Provider list pricing does not auto-update, so the recorded cost drifts from the actual invoice when AWS or Anthropic publishes a new price. The drift inventory below records this.

There is no per-tenant cost split at the time of writing. Cost is recorded per call; the call payload may carry a tenant identifier in `structlog` context, but the `budget_log` schema does not have a tenant column. Per-tenant cost aggregation is queued (AI Usage Visibility records the broader visibility gap).

**Governing source.** `bc-ai/app/db/evidence.py`; `bc-ai/app/clients/bedrock.py` (the `MODEL_PRICING` table); `bc-ai/app/db/schema.sql`.

## Failure Modes

| Cause | System response |
|---|---|
| Daily budget cap reached during a request | Bedrock or Anthropic client raises `BudgetExceededException` before the model call; the FastAPI handler returns HTTP 429 with a structured error; the calling service decides whether to retry, fail closed, or proceed unverified |
| Gemini call succeeds outside cost controls | Gemini client returns text and token usage without budget preflight or cost-row persistence; budget reports understate Gemini-backed activity |
| Inference profile identifier not recognized by Bedrock | AWS returns an error from `invoke_model`; the Bedrock client surfaces the error; no row is written to `budget_log`; the act's draft-evidence row records the failure |
| Anthropic API key invalid or rate-limited | The direct client raises; the act records the failure; no `budget_log` row is written |
| Gemini API key invalid or rate-limited | The Gemini client raises; the act records the failure; no `budget_log` row is written |
| Model registry entry's fallback chain exhausted | The orchestrator records a draft-evidence row with `failure_reason='model_unavailable'`; the calling service receives the structured failure |
| Provider price table drifts from list pricing | The recorded cost differs from the actual invoice; the budget cap is computed against the recorded cost, so a drifted-low snapshot lets calls through that should have hit the cap; a drifted-high snapshot blocks calls that should have proceeded; the static price tables need a periodic update |
| Bedrock service-level unavailability (AWS-side outage) | The boto3 client raises; the agent's draft-evidence row records the outage; the orchestrator does not silently substitute a different provider unless the registry's fallback chain authorizes it |

**Governing source.** `bc-ai/app/clients/bedrock.py`; `bc-ai/app/clients/anthropic_client.py`; `bc-ai/app/clients/gemini.py`; `bc-ai/app/pipeline/orchestrator.py`.

## Drift Inventory

Per pattern 69, gaps between the design intent recorded above and the current state are surfaced explicitly.

| Gap | Severity | Detail |
|---|---|---|
| Provider price tables are static code snapshots | Open | Bedrock and Anthropic clients embed provider prices; price changes require code updates |
| No graceful degradation when daily cap fires | Open | The budget cap is a hard block; an organization that wants budget-aware downgrade to a cheaper model does not get it; the operator decides per-call retry policy |
| No per-tenant cost split | Open | `budget_log` has no tenant column; per-tenant cost aggregation is not available; operators see the partial daily total but not the per-tenant breakdown |
| Gemini calls bypass budget and cost recording | Open | `app/clients/gemini.py` logs token usage but does not check the daily cap or write `budget_log` rows |
| Fallback chain names use legacy Nova labels for Gemini bindings | Open | `app/models/registry.py` uses `nova-*` ids while the active profile strings resolve to Gemini; direct Anthropic SDK checkers cover part of the cross-family target in the readiness baseline |
| The `converse` API is not used | Low | All Bedrock calls go through `invoke_model`; the `converse` API is the more recent Bedrock entry point and may be more efficient for multi-turn calls; not yet adopted |
| Streaming is absent across all clients | Low | All three clients (Bedrock, Anthropic SDK direct, Gemini) are synchronous request-response; streaming responses are not exposed to callers |
| Per-call provider override is not exposed | Low | The model registry decides the provider per role at registration; a calling service cannot ask for a specific provider on a specific call; the registry is the single point of routing decision |

**Governing source.** `bc-ai/app/models/registry.py`; `bc-ai/app/clients/`; `bc-ai/app/db/schema.sql`.

## Boundaries with Adjacent Chapters

| Adjacent surface | Where it lives | Why it is not this chapter |
|---|---|---|
| AI Architecture | AI section | Owns the maker-checker-gate triplet pattern, the housekeeping agent pattern, and the auditor pattern. This chapter records the model substrate; AI Architecture records the patterns that consume it |
| AI Agents | AI section | Owns the agent inventory at the cluster level. This chapter records the model registry; AI Agents records the agents that the registry serves |
| AI Trust and Verification | AI section | Owns the cross-family discipline and the trust ladder. This chapter records the registry's current Gemini-only fallback chains; AI Trust and Verification records why cross-family pairing is the design intent |
| AI Usage Visibility | AI section | Owns the tenant-facing transparency surface. This chapter records that `budget_log` has no tenant column; AI Usage Visibility records the broader visibility gap |
| Infrastructure | Implementation section | Owns the AWS account, region, profile, port reservation, and CodeArtifact substrate. This chapter records that the Bedrock client uses the platform's AWS profile; Infrastructure records the figures |
| Auxiliary Services | Implementation section | Owns bc-ai's deployable shape. This chapter records bc-ai's model substrate; Auxiliary Services records bc-ai's deployable posture |

**Governing source.** Operating Model; Implementation; outline.md §4.4.

## Governing Decisions

| Decision | Title | Bedrock and inference-profile impact |
|---|---|---|
| DEC-c06f41 | Spine expansion to eight sections plus home | The Bedrock and Inference Profiles chapter exists in the AI section per DEC-c06f41 |

**Governing source.** The Authority Model.

## References

- AI Architecture
- AI Agents
- AI Gates
- AI Trust and Verification
- AI Usage Visibility
- Architecture
- Infrastructure
- Auxiliary Services
- DEC-c06f41: Spine expansion to eight sections plus home
- outline.md §4.4: AI
- Decisions: ADR Registry

