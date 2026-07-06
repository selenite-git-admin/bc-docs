---
uid: DEC-e82f0a
title: "bc-portal AI Assistant — unified drawer replacing help, dual retrieval (catalog + articles) [QUARANTINED DUPLICATE FILE]"
description: "QUARANTINED DUPLICATE — canonical file is ADR-e82f0a.md (same UID DEC-e82f0a, status implemented). This file has a malformed double-prefixed filename and stale status `decided`; preserved for audit trail."
status: superseded
superseded_by: DEC-e82f0a
date: 2026-03-29
project: bc-portal
domain: platform
refs:
  - type: decision
    uid: DEC-e82f0a
    label: "D223 — KPI Assistant pipeline (bc-admin implementation, D223 reference)"
authority: reference
migrated_from: legacy v2 archive
devhub_registration: doc-registry indexed; this is a DUPLICATE_DECISION file (same UID `DEC-e82f0a` shared with canonical `ADR-e82f0a.md`). Decision-registry has ONE row DEC-e82f0a (status implemented) whose file_path points at `ADR-e82f0a.md` (canonical). This file has a malformed double-prefixed filename and is preserved as historical artifact per Foundation Invariant III; not authoritative. See Decision-Registration Integrity Audit 2026-06-22 §3.5.
---

# bc-portal AI Assistant — Unified Drawer, Dual Retrieval [QUARANTINED DUPLICATE FILE]

> **⚠ QUARANTINED DUPLICATE FILE.** The canonical ADR for UID `DEC-e82f0a` is [`ADR-e82f0a.md`](ADR-e82f0a.md) in this same directory — same UID, `status: implemented`, registered in the DevHub decision registry. This file (`ADR-DEC-e82f0a.md`) carries a malformed double-prefixed filename, was authored earlier under `status: decided`, and is preserved as a historical artifact per Foundation Invariant III. Do not read the body below as live authority; read `ADR-e82f0a.md` instead. Filesystem cleanup (rename or removal) is deferred to operator per Decision-Registration Integrity Audit 2026-06-22 §3.5 and the repair closeout's `do-not-delete` hard stop.

## Context

bc-admin already has a working AI assistant drawer (D223) grounded on the metric catalog via bc-ai (port 4300). bc-portal is the customer-facing app used by tenant employees (CFO, analyst, finance team). It currently has a separate RHS help drawer that surfaces static help articles.

Two questions arose when extending AI assistance to bc-portal:

1. **Separation vs sharing** — should bc-portal's AI assistant be a separate implementation or share code with bc-admin?
2. **Help drawer** — should bc-portal merge its existing static help drawer into the AI assistant?

## Decision

### 1. Separate UI implementation, shared backend

bc-portal and bc-admin maintain **separate AI assistant UI implementations**. No shared npm package is created at this stage.

**Rationale:** The two apps serve fundamentally different users and data contexts:

| | bc-admin | bc-portal |
|---|---|---|
| User | Platform operator | Tenant employee (CFO, analyst) |
| Questions | "Explain this metric definition", "how many AR KPIs?" | "Why is my DSO high?", "what's my current AR turnover?" |
| Data | Catalog definitions only | Catalog definitions + live tenant snapshots |
| Scope | Platform-wide | Tenant-scoped |
| Context header | `context: "platform"` | `context: null` (tenant) + `x-tenant-id` |

The **bc-ai backend** (port 4300) is shared — it already handles both contexts. Forced UI abstraction too early would add complexity without benefit. The component pattern is shared (same drawer shape, message bubbles, MarkdownText/KaTeX renderer, disclaimer); the implementations diverge as needed.

### 2. Help drawer replaced by the AI assistant

The existing bc-portal static help drawer is **retired**. The AI assistant drawer takes its place as the single RHS panel.

Help articles are not deleted — they become a **RAG retrieval source** inside bc-ai. The user sees one unified assistant that answers both metric questions and platform/workflow questions.

### 3. Dual retrieval in bc-ai for bc-portal queries

The D223 pipeline gains a second retrieval source for bc-portal requests:

```
G1 (input guard)
→ S1 (Haiku intent — adds query_type: metric_query | help_query | mixed)
→ S2a (catalog_direct — metric definitions + tenant snapshots)   ← existing
→ S2b (help_retriever — RAG over help articles)                  ← new
→ S3 (merge + rank results by source)                            ← new for mixed
→ S4 (Nova Pro composer — unified grounded answer)
→ G3 (audit log)
```

**Intent routing:**
- `metric_query` → S2a only (catalog + snapshot)
- `help_query` → S2b only (help articles)
- `mixed` → both S2a + S2b, composer synthesises from both sources

**bc-admin is unaffected** — it only uses S2a. The `context: "platform"` flag already bypasses snapshots.

### 4. Help article RAG — indexing approach (deferred)

Help articles (markdown files in bc-docs or a CMS) are chunked and embedded into a vector store (pgvector in bc_platform_dev, or a dedicated table). This is a one-time indexing task. Article maintenance stays editorial — update the article, re-index, AI knowledge updates.

The exact chunking strategy, embedding model, and similarity threshold are deferred to the implementation task.

## Options Considered

### Option A — Shared UI component library (rejected)
Extract drawer components into a shared package used by both bc-admin and bc-portal. Rejected: premature abstraction. The two apps are at different stages and the forced interface would slow both down. Revisit when a third consumer exists.

### Option B — Keep help drawer, add separate AI drawer (rejected)
Two competing RHS panels. Confusing UX — user doesn't know which to open. Help and AI answer the same class of questions differently; unifying them is strictly better.

### Option C — AI drawer with help tab (rejected)
Keep help articles as a browsable tab alongside AI chat. Rejected: static browsing is inferior to AI search. If the AI answers "how do I export data?" correctly from article content, the browse tab has no residual value.

## Consequences

- bc-portal static help drawer is retired once AI assistant is live
- bc-ai gains a `help_retriever` module (S2b) — new retrieval path, separate from catalog_direct
- Help articles need a one-time RAG indexing task before S2b is usable
- bc-portal AI drawer UI is built independently from bc-admin — same pattern, separate files
- bc-portal requests to bc-ai must include `tenant_id` and omit `context: "platform"`
- Mixed queries (metric + help) require a merge/rank step (S3) not present in bc-admin pipeline
- The disclaimer "Answers within your enterprise boundary · not saved · not used for training" applies to bc-portal drawer identically

## Implementation Sequence

1. **Phase 1** — Build bc-portal AI drawer UI (no backend wiring). Mirror bc-admin drawer pattern.
2. **Phase 2** — Wire bc-portal drawer → bc-ai with tenant context. Metric queries work immediately (S2a already handles tenant snapshots).
3. **Phase 3** — Help article RAG: index articles, build S2b help_retriever, add `help_query` / `mixed` intent types to Haiku resolver.
4. **Phase 4** — Retire static help drawer.
