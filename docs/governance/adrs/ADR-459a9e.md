---
uid: DEC-459a9e
title: "Zod v4 syntax rule for MCP tool schemas + tools/list regression guard"
description: "Any single-arg z.record() in an MCP tool shape will make tools/list throw on v4 zod, hiding all 53 devhub tools. Must use z.record(keyType, valueType)."
status: implemented
subdomain: mcp-platform
focus: schema-contract-guard
date: 2026-04-19T12:38:47.915Z
project: barecount-devhub
domain: platform
migrated_from: legacy v2 archive
---

# Zod v4 syntax rule for MCP tool schemas + tools/list regression guard

## Context

Zod v4 changed z.record() signature from single-arg (value schema) to two-arg (key schema, value schema). A silent regression — no deprecation warning — because v4 parses the single arg as the key schema and leaves the value undefined. Failure only surfaces at JSON-schema serialization time, inside the MCP SDK tools/list handler.

## Decision

All MCP tool input shapes in `src/mcp-server.js` MUST use Zod v4 syntax.
Specifically: `z.record(keyType, valueType)` with two arguments. Single-arg
`z.record(valueType)` is a v3 pattern and silently breaks tools/list on v4.

## Why this matters

One broken tool schema poisons the entire tools/list response. Claude Code
registers the devhub MCP server but surfaces ZERO tools. The session protocol
(`devhub_session_boot`, `devhub_task_*`, `devhub_decision_record`, etc.)
becomes unavailable — silently, because the MCP client only logs the -32603
error internally.

## Regression guard

- A self-test at `scripts/check-mcp-tools-list.js` spawns mcp-server.js and
  calls tools/list via stdio JSON-RPC. Fails (exit 1) if any error is returned
  or tool count < expected threshold.
- Run manually before any mcp-server.js edit; add to CI.
- The shim (`src/mcp-shim.js`) is kept minimal: exec the server immediately,
  no wait-for-health wrapper (which blocked MCP handshake for up to 60s and
  racing with the MCP client timeout). Tool calls handle DevHub-down gracefully
  via the existing `api()` helper — same lazy pattern as bc-postgres.

## Detection history

Bug introduced when package.json was pinned to `zod: ^4.3.6`. Undetected for
~6 sessions because the symptom ("devhub_* not in tool list") looked like
an MCP registration / server-down issue, not a server-internal error.
Traced via Protocol.setRequestHandler instrumentation to
`z.record(z.any()).optional()` on devhub_process_audit_run (lines 1938-1939).
