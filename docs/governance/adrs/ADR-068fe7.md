---
uid: DEC-068fe7
title: "Mock/Real dual-path via env.useMock"
description: "Every frontend service checks env.useMock flag to return mock data or call real apiClient. One flag switches the entire app."
status: implemented
subdomain: frontend-data-source
focus: mock-real-switching
date: 2026-02-22
project: bc-core
domain: sdg
authority: authoritative
migrated_from: legacy v2 archive
---


# Mock/Real dual-path via env.useMock

## Context

Frontend dev and demos work without backend. One flag to switch.

## Decision

Every service checks env.useMock — returns mock data or calls apiClient

## Options Considered

N/A

## Consequences

N/A
