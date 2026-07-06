---
uid: DEC-d6f6e1
title: "DevHub as MCP server"
description: "Added MCP protocol layer (stdio transport) on top of existing Express API. Eliminates shell escaping issues and works from any MCP-compatible client."
status: implemented
subdomain: mcp-architecture
focus: dev-coordination-protocol
date: 2026-02-22
project: barecount-devhub
domain: connectors
authority: authoritative
migrated_from: legacy v2 archive
---


# DevHub as MCP server

## Context

Native MCP tools eliminate shell escaping issues, are faster than CLI scripts, and make DevHub accessible from any MCP-compatible client (Claude Code, Cursor, etc.).

## Decision

Added MCP protocol layer (stdio transport) on top of existing Express API. 14 tools covering sessions, TODOs, parking, decisions, projects, and activity.

## Options Considered

N/A

## Consequences

N/A
