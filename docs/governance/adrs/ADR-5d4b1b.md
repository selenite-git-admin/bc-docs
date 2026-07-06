---
uid: DEC-5d4b1b
title: "bc-website v2 tech stack — Astro + React islands + Tailwind"
description: "Astro 5 + React 19 islands + Tailwind 4 + MDX. Pure static build to S3+CloudFront. Content via Astro Content Collections."
status: implemented
subdomain: tech-stack
focus: bc-website-v2-astro
date: 2026-03-19
project: bc-website
domain: auth
authority: authoritative
migrated_from: legacy v2 archive
---


# bc-website v2 tech stack — Astro + React islands + Tailwind

## Context

Marketing site is 90% static content — shipping zero JS by default is correct. Astro's island architecture lets us use React where needed without penalizing the whole site. Static output fits the existing AWS S3+CloudFront infra pattern. Tailwind keeps styling consistent with bc-portal and bc-admin. MDX enables content updates without touching components. Next.js rejected: ships full React runtime, SSR features unnecessary for static marketing site, export mode loses framework advantages. v1 was Figma Maker auto-generated SPA (client-rendered, no SEO) — v2 fixes this fundamentally.

## Decision

bc-website v2 uses Astro 5 + React 19 (islands) + Tailwind 4 + MDX + TypeScript. Build output is pure static HTML/CSS/JS, deployed to S3+CloudFront. React components used only for interactive islands (pricing, forms, animations). Content pages authored in MDX via Astro Content Collections. Figma MCP generates React components which are used as Astro islands directly.

## Options Considered

N/A

## Consequences

N/A
