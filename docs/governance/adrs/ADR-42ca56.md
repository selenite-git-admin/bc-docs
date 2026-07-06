---
uid: DEC-42ca56
title: "MCP Tool Registry — scanner-derived catalog of DevHub MCP tools with side-effect metadata"
description: "Scanner-derived MCP tool registry (48 DevHub tools, v1). Follows api_registry pattern. Source annotations classify side_effect + domain. v1 = docs only; v1.1 adds D268 self-audit gate. External MCP servers deferred to v2."
status: implemented
date: 2026-04-15T02:57:36.043Z
project: barecount-devhub
domain: governance
migrated_from: legacy v2 archive
---

# MCP Tool Registry — scanner-derived catalog of DevHub MCP tools with side-effect metadata

## Context

**Why now.** DevHub has 48 MCP tools in a single file with no structured metadata. MCP's native tools/list returns free-form descriptions — you cannot programmatically filter "every tool that mutates contracts." As the MCP surface grows (external servers bring hundreds more tools), discoverability and write-safety become harder to reason about.

**Why this shape.** The api_registry precedent is exact (47 rows, scanner src/lib/api-scanner.js, MCP tools devhub_api_{scan,list,blast}, scope + auth + roles columns). Extending it to MCP tools is pattern consistency, not invention. Same "walk → parse → upsert → stats" loop as doc-scanner and api-scanner. Minimal cognitive cost for the team.

**Why source annotations.** Name-pattern classification (list/get→read, save/update/add→write) fails on edge cases like devhub_qa_audit (reads but may trigger writes) or devhub_session_get_context (reads but is stateful). 48 tools is a small one-time cost for permanent disambiguation. Scanner warns on missing annotations, forcing discipline on future additions.

**Why v1 is DevHub-only.** External MCP servers have three complications: (a) auth-gated tool listings (Gmail, Box, Slack), (b) stdio servers only listable when running, (c) ownership — who updates the registry when the external server changes? Proving the schema on 48 tools you fully control first lets v2 attack external servers with real constraints observed.

**Why metadata-first, gate-later.** Building a write-safety gate without a concrete consumer produces dead metadata. D268 session self-audit is the obvious v1.1 consumer — destructive tool calls during a session should surface in close-time audit. But commit to the registry first, then wire the gate once v1 is stable and consumers can be validated.

**Alignment with existing architecture.**
- D221 (ADR-first): this ADR auto-generates the canonical file in legacy v2 archive
- D229 (documentation framework): scanner-derived pattern matches doc-scanner
- D268 (session discipline): side_effect metadata is the hook for future self-audit
- D305 (chain_status SSOT): registry-is-authority pattern, not ad-hoc recompute

**Non-goals.** Not a replacement for MCP tools/list (complementary). Not a service orchestrator (P09 Service Catalog is business services, a different concept). Not a permissions system (permission mode stays orthogonal).

## Decision

DevHub will gain a scanner-derived MCP tool registry following the existing api_registry pattern exactly.

**v1 scope**
- DevHub's own 48 MCP tools parsed from src/mcp-server.js
- New table mcp_tool_registry with columns: tool_name, server_slug, description, input_schema_json, side_effect (read|write|destructive), domain, source_file, source_line, requires_auth, requires_devhub_api, scan_ts, created_ts, updated_ts
- New scanner src/lib/mcp-tool-scanner.js — parses server.tool(...) blocks and reads inline annotations // @side-effect: and // @domain:
- New MCP tools: devhub_mcp_scan, devhub_mcp_list, devhub_mcp_get (mirror devhub_api_* naming)
- New route src/routes/mcp-registry.js exposing GET /api/mcp-registry, GET /api/mcp-registry/:tool_name, POST /api/mcp-registry/scan
- Auto-scan on DevHub boot (consistent with doc-scanner and api-scanner)
- Annotate all 48 existing server.tool(...) blocks with classification markers; scanner warns on missing annotations

**Classification strategy**
Source annotations over name-pattern inference. One-time 48-line edit eliminates ambiguity forever. Pattern matching would miss edge cases (e.g. devhub_qa_audit reads but can trigger remediation writes).

**Deferred to v2**
- External MCP servers: bc-postgres, Claude_Preview, AWS_API_MCP_Server, Playwright, Gmail, Scheduled-Tasks, MCP_DOCKER, plugin:legal:*, mcp-registry. The v1 server_slug column designs forward-compat, but v2 will need scanner extensions (walk .claude/settings.json, enumerate live tools/list, handle auth-gated servers).
- Active write-safety enforcement. In v1 side_effect is documentation. In v1.1 it becomes the hook for D268 session self-audit — flag destructive tool usage without approval.

**Explicitly out of scope**
- npm scripts / CLI commands — MCP tools only
- Competing with or replacing Claude Code's native ToolSearch — DevHub registry is independent, project-side discovery
- MCP server lifecycle management (start/stop/health)
