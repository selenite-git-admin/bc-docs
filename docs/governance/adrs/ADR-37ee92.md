---
uid: DEC-37ee92
title: "D235: Documentation RAG Layer — Vector Retrieval from legacy v2 archive for AI Grounding and Help Assistant"
description: "bc-ai indexes legacy v2 archive corpus into ChromaDB vectors; exposes retrieval endpoints for agent grounding, bc-portal help assistant, bc-admin knowledge queries"
status: reversed
subdomain: rag
focus: doc-vector-retrieval
date: 2026-04-01
project: bc-ai
domain: execution
refs:
  - type: decision
    uid: DEC-c566f3
    label: "D223: KPI Catalog AI Assistant — proven pipeline pattern"
  - type: decision
    uid: DEC-f0eb14
    label: "D229: Documentation Framework — 3-stream, module-component architecture"
  - type: decision
    uid: DEC-2347a3
    label: "D234: Filesystem-Derived Doc Registry"
migrated_from: legacy v2 archive
---

# D235: Documentation RAG Layer — Vector Retrieval from legacy v2 archive for AI Grounding and Help Assistant

## Context

legacy v2 archive is a mature documentation corpus: 1,017 markdown files across 257 ADRs, 10 platform modules (P01–P10), 6 tenant modules (T01–T06), playbooks, dev-guides, and help articles. Total: ~158K lines of structured content with consistent heading hierarchy, frontmatter metadata, and cross-references.

**None of this knowledge is accessible at runtime.** The existing 5 bc-ai agents (BO Suggest, Field Map, Metric Trace, Eval Advise, Chain Audit) run on static prompt templates with no domain context. The KPI Assistant (D223) queries PostgreSQL for metric definitions — it knows nothing about platform architecture, contracts, or domain concepts.

**bc-portal has no help system.** Tenant users have no way to get contextual help about the platform. bc-admin has a HelpDrawer with static markdown articles (D107) and an AI Assistant drawer limited to KPI queries.

The documentation is the knowledge. It needs to be queryable.

## Decision

Add a **vector retrieval layer** to bc-ai that indexes legacy v2 archive and exposes it through API endpoints. Use ChromaDB (local, file-based) for vector storage and Bedrock Titan Embeddings v2 for embedding generation.

### Architecture

```
legacy v2 archive (filesystem, 1,017 .md files)
       │
       ▼
   ┌──────────────────────────┐
   │  Doc Indexer              │  Python script, runs on-demand
   │  ├─ Parse .md files       │  Split by ## heading sections
   │  ├─ Extract frontmatter   │  uid, domain, authority, type, project
   │  ├─ Chunk by heading      │  ~3K chunks estimated
   │  ├─ Embed chunks          │  Bedrock Titan Embeddings v2
   │  └─ Store in ChromaDB     │  Local persistent, file-based
   └──────────┬───────────────┘
              │
              ▼
   ┌──────────────────────────┐
   │  bc-ai (FastAPI :4300)    │
   │                           │
   │  GET  /api/ai/docs/search │  Vector similarity (top-k chunks)
   │  POST /api/ai/docs/ask    │  RAG: retrieve + LLM compose
   │  POST /api/ai/suggest/*   │  Existing agents + doc grounding
   │  POST /api/ai/kpi/ask     │  Existing D223, unchanged
   └──────────────────────────┘
       │                │
       ▼                ▼
   bc-portal         bc-admin
   (help assistant)  (AI drawer expanded)
```

### Chunking Strategy

- **Split by heading** (`## Section`). legacy v2 archive uses consistent heading hierarchy (dossier 9-section format). Each heading section becomes one chunk.
- **Frontmatter metadata** preserved per chunk: `uid`, `domain`, `authority`, `type`, `project`, `source_file`, `heading_path` (e.g., `P01 > Source Catalog > 03 Data Structure`).
- **Max chunk size**: 1,500 tokens. Sections exceeding this split at paragraph boundaries.
- **Estimated corpus**: ~3,000 chunks from 1,017 files.

### Retrieval Strategy

1. **Vector search** with metadata filtering. Query: user question → embed → top-k similar chunks. Filters: `domain`, `type`, `authority`, `project`.
2. **Context scoping**: bc-portal queries filter to T01–T06 tenant modules + help articles + relevant playbooks. bc-admin queries include P01–P10 platform modules + ADRs + dev-guides.
3. **No graph layer in v1**. Frontmatter metadata (`supersedes`, `domain`, `status`) enables structured filtering without a graph database. Graph traversal (impact analysis, decision lineage) deferred to v2 if needed.

### Technology Choices

| Component | Choice | Rationale |
|---|---|---|
| Vector store | ChromaDB (local, file-based) | Zero infrastructure, Python-native, persistent. 3K chunks is trivial. Migrate to pgvector if scale needed. |
| Embeddings | Bedrock Titan Embeddings v2 | Already have Bedrock access (ap-south-1). ~$0.02 to embed entire corpus. 1,024-dim vectors. |
| Chunking | Heading-based + frontmatter | legacy v2 archive has consistent structure — natural chunk boundaries. No token-window sliding needed. |
| LLM for composition | Bedrock Sonnet 4.5 / Haiku 4.5 | Proven in D223 pipeline. Haiku for intent routing, Sonnet for grounded answer composition. |

### Embedding Cost

- Corpus: ~158K lines ≈ 600K tokens
- Titan Embeddings v2: $0.00002/1K tokens
- **Full index: ~$0.012** (one-time, re-run on demand after doc changes)
- Per-query embedding: negligible

### API Endpoints

**`GET /api/ai/docs/search`** — Pure vector retrieval
- Query params: `q` (search text), `domain` (filter), `type` (filter), `top_k` (default 5)
- Returns: ranked chunks with metadata, similarity scores, source file paths

**`POST /api/ai/docs/ask`** — RAG pipeline (retrieve + compose)
- Body: `{ question, context?, scope?, tenant_slug? }`
- `scope`: `"portal"` (tenant docs) | `"admin"` (platform docs) | `"all"`
- Pipeline: G1 (input guard) → embed query → retrieve top-k → S4 (grounded composer) → G3 (audit)
- Returns: `{ answer, citations[], confidence, latency_ms }`
- Reuses D223 patterns: input guard, grounded composition, citation validation

**Existing agent endpoints** — Enhanced with doc grounding
- Before each maker prompt, retrieve 2–3 relevant doc chunks based on entity context
- Inject as `## Platform Knowledge` section in the system prompt
- ~200 extra tokens per agent call, no API change

### Integration Points

**bc-portal Help Assistant** (priority 1):
- New RHS drawer component (same pattern as bc-admin AiAssistantDrawer)
- Calls `POST /api/ai/docs/ask` with `scope: "portal"`, `tenant_slug` from auth context
- Scoped to: T01–T06 tenant modules, help articles, relevant playbooks
- Context-aware: current page route informs the query (e.g., on Connections page → bias toward T03 docs)

**Agent Grounding** (priority 2):
- Modify `pipeline/orchestrator.py` to call `/api/ai/docs/search` before maker prompt
- Entity type + domain → targeted doc retrieval → inject into prompt
- Example: BO Suggest for SAP source → retrieve P01 source catalog dossier + relevant ADRs

**bc-admin AI Drawer Expansion** (priority 3):
- Extend existing AiAssistantDrawer with tab/mode for "Platform Knowledge" queries
- Route to `/api/ai/docs/ask` with `scope: "admin"` instead of `/api/ai/kpi/ask`
- Intent resolver decides: KPI question → existing D223 pipeline, platform question → docs RAG

## Options Considered

### Option A: ChromaDB local vector store (chosen)

Zero infrastructure. File-based persistence in `bc-ai/data/chroma/`. Python-native API. Supports metadata filtering. 3K chunks is well within single-node capacity. Can migrate to pgvector later if needed.

### Option B: pgvector in existing PostgreSQL (rejected for v1)

Would add vector extension to bc_platform_dev. Better for production scale, but adds DB schema dependency, requires Docker rebuild, and mixes AI concerns with platform data. Evaluate for v2 when corpus grows or when multi-service access is needed.

### Option C: Full GraphRAG (Microsoft-style) (rejected for v1)

Entity extraction + community summarization + graph traversal. Powerful for multi-hop queries but: (a) high generation cost for community summaries (~$2–5 per full index with Sonnet), (b) complex infrastructure (graph DB + vector DB + extraction pipeline), (c) overkill for 1K files where frontmatter metadata already provides structured filtering. Park for v2.

### Option D: No RAG — expand static help articles (rejected)

Manually author help articles for bc-portal. Doesn't scale, goes stale, duplicates legacy v2 archive content. The documentation already exists — make it queryable.

## Consequences

### Positive
- bc-portal gets a help assistant immediately, grounded in real documentation
- Existing agents produce better suggestions with domain context
- Single index serves all consumers (portal, admin, agents)
- Minimal infrastructure: one Python dependency (chromadb), one Bedrock embedding model
- Documentation improvements automatically improve AI responses (re-index)

### Negative
- New dependency: chromadb (~200MB installed size)
- Indexing requires legacy v2 archive path accessible from bc-ai (local dev: filesystem, prod: needs deployment strategy)
- Embedding model adds a Bedrock dependency (already have Bedrock, trivial cost)

### Risks
- **Stale index**: Docs change, index doesn't auto-update. Mitigation: re-index script + pm2 cron or DevHub hook after doc changes.
- **Hallucination**: LLM may confabulate beyond retrieved chunks. Mitigation: same grounding discipline as D223 — "ONLY use provided context, cite source for every claim."
- **Scope creep**: Temptation to add graph, fine-tuning, etc. Mitigation: this ADR locks v1 as vector-only. Graph is a separate future decision.

## Phased Rollout

| Phase | Scope | Effort |
|---|---|---|
| A | Indexer script + `/api/ai/docs/search` endpoint + ChromaDB setup | 1–2 sessions |
| B | `/api/ai/docs/ask` RAG endpoint + bc-portal Help Assistant drawer | 2–3 sessions |
| C | Agent grounding (inject doc chunks into existing 5 agent prompts) | 1 session |
| D | bc-admin AI drawer expansion (platform knowledge mode) | 1 session |
