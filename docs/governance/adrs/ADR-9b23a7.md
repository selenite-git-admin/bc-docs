---
uid: DEC-9b23a7
title: "Remove pm2 — independent service startup"
description: "pm2 removed from BareCount dev workflow. Each service starts independently in its own repo. DevHub starts via npm run dev (Node --watch). Supersedes D056."
status: implemented
date: 2026-04-10
project: barecount-devhub
domain: devops
authority: authoritative
supersedes: DEC-890417
migrated_from: legacy v2 archive
---

# Remove pm2 — independent service startup

## Context

pm2 (DEC-890417 / D056) was adopted to manage all BareCount dev services from a single ecosystem config. On Windows, it has become a net negative:

1. **CMD window flood** — pm2 spawns a visible `cmd.exe` per managed process. With 9 online services, this produces 23+ cmd.exe windows and 36+ node.exe processes.
2. **Broken monitoring** — pm2's memory monitoring reports 0 MB for all processes on Windows.
3. **DevHub MCP fragility** — `npm run dev:restart` (`pm2 restart all`) kills DevHub alongside app services. The DevHub MCP server (stdio transport) depends on the Express API at localhost:4000. When pm2 restarts DevHub, all active Claude Code sessions lose MCP connectivity.
4. **Redundant process management** — Most services have their own watch/HMR: NestJS `--watch` (SWC), Vite HMR, tsx watch. pm2 adds a wrapper around self-managing processes.
5. **All-or-nothing startup** — `npm run dev:up` starts 9 services when most sessions need 1–2.

## Decision

Remove pm2 from the BareCount dev workflow. Each service starts independently in its own repo using its native dev command.

- **DevHub**: `npm run dev` (Node 22 `--watch` flag). Always-on infrastructure — start first, keep running.
- **bc-core**: `npm run start:dev` (NestJS `--watch`).
- **Frontends**: `npm run dev` (Vite HMR) — start only when needed.
- **Cron jobs**: Run manually (`npm run codeartifact:refresh`) when needed. Library scan triggered from bc-core directly.
- **ecosystem.config.cjs**: Retained as deprecated reference for port assignments and config.

## Options Considered

1. **Keep pm2, fix the issues** — Would require Windows-specific workarounds (hidden windows, custom restart logic). pm2's Windows support is fundamentally limited.
2. **Replace pm2 with concurrently/npm-run-all** — Still starts everything at once. Doesn't solve the "start only what you need" problem.
3. **Independent service startup (chosen)** — Each repo owns its own dev command. No central orchestrator. Fewest processes, no cmd.exe flood, DevHub never killed by app restarts.

## Consequences

- DevHub stays running regardless of app service lifecycle — MCP sessions no longer break.
- Process count drops from 36+ node.exe to ~5–10 per session.
- No more cmd.exe window flood.
- Loss of centralized log aggregation (mitigated: each service logs to its own terminal).
- Loss of one-command startup (mitigated: most sessions only need 1–2 services).
- `ecosystem.config.cjs` kept as deprecated reference — can be removed in future cleanup.
