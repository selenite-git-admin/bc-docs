---
uid: DEC-6f7d38
title: "Fresh bc-admin repo — Datajettyadminportal stays as Figma reference"
description: "New bc-admin repo from scratch using bc-portal design system (Radix + Tailwind). Old Datajettyadminportal kept as Figma design reference only."
status: implemented
subdomain: bc-admin
focus: repo-genesis
date: 2026-02-28
project: bc-admin
domain: platform
authority: authoritative
migrated_from: legacy v2 archive
---


# Fresh bc-admin repo — Datajettyadminportal stays as Figma reference

## Context

Datajettyadminportal is tightly coupled to Figma Maker auto-generation. Modifying it fights the generation workflow. Starting fresh with bc-portal's mature design system ensures consistency across customer and admin portals, real API integration from day one, and clean architecture aligned with BareCount execution model (no pipeline terminology).

## Decision

Create new bc-admin repo from scratch. Datajettyadminportal remains as Figma Maker-controlled design reference (never runs in production). bc-admin copies bc-portal's design system (Radix UI + TailwindCSS v4) for consistency. All old Datajettyadminportal phase tasks aborted.

## Options Considered

N/A

## Consequences

N/A
