---
uid: DEC-2cf250
title: "BareCount visual language — bare/confident/light; color as information, not decoration"
description: "bc-portal surface stays light/white with disciplined color. No dark-mode-as-default; no gradient chrome. Color earns its place as information carrier (status, severity, function hue). Dark is a deliberate state, never a default."
status: decided
subdomain: design-system
focus: visual-language-policy
date: 2026-04-19T15:23:59.001Z
project: bc-portal
domain: design-system
amends: DEC-9a3c6a
migrated_from: legacy v2 archive
---

# BareCount visual language — bare/confident/light; color as information, not decoration

## Context

The "BareCount should look dark/bold like other data products" temptation recurred during a gradient experiment on the Beyond LHS panel. Walked through it and concluded it's a false signal from the market, not a real product need.

**Why the market signal is misleading:**

Most TAs say they "like dark data-product UIs" because:
- Existing BI tools are white + cluttered; dark feels premium by contrast (signal is about *contrast*, not *dark*)
- Dark hides UI noise when a product has too much of it
- Dark photographs well in sales decks and demo videos

None of these apply to BareCount. BareCount is explicitly a lean anti-dashboard product — it has less to hide, not more. Adding visual chrome to "feel serious" is the same retrofit failure mode D361 rejects for routes: dressing up the product in other products' conventions instead of letting the thesis drive the shape.

**Why light is the honest choice here:**

1. "Bare" is literally in the name. A dark-navy gradient canvas contradicts the brand word.
2. Claude, Linear, Notion, Stripe Dashboard — the products BareCount actually aspires to match in polish — all chose calm light UIs. Not because they're timid, but because they had confidence in the product and didn't need chrome to signal seriousness.
3. Dark/bold data-product themes correlate with products that have *no differentiated point of view*. BareCount has one (contract chain, leanness, trust). Signaling with chrome would flatten what's actually differentiated about it.
4. Chrome ages fastest. The "2026 dark navy with teal spotlight" look is already a cliché in data-tool marketing pages. In three years it will look like 2020 purple-gradient SaaS looks today.

**Honest counterpoint considered and rejected:** "Dark looks more premium to enterprise buyers." This is only true because most enterprise BI tools have poor information hierarchy and dark compensates. Fix the information hierarchy; the chrome problem dissolves.

**Where this ADR does NOT apply:**
- Platform-internal tools (bc-admin, devhub) can adopt any visual language — they're ops surfaces for the BareCount team, not product surfaces
- A deliberate, gated "focus mode" state inside Beyond (e.g., a boardroom presentation view) can go dark as an explicit treatment
- Brand/marketing site (bc-website) follows brand guidelines separately

## Decision

bc-portal (and by extension all tenant-facing BareCount surfaces) uses a light/white visual language by default. This is a governance decision, not a style preference — it encodes the product thesis into the UI.

**Rules:**

1. **Base surface is light.** White and low-chroma neutrals. The existing shadcn/ui canonical palette (D356) is the reference — do not bolt on darker base themes without another explicit ADR.

2. **Color is information, not decoration.** A color on the page must answer a question: what status? what severity? what function group? what semantic role? If a color exists only to make the UI "look modern" or "feel premium," it is cut.

3. **No gradient chrome as default.** Gradients are permitted only when (a) they carry semantic meaning (e.g., the OKLCH 10-hue function wheel in globals.css), or (b) they are a deliberate, localized treatment with an ADR justifying them. A gradient-filled panel "because dark looks cool" fails this test.

4. **Dark is a state, not a default.** If a surface needs a dark treatment — e.g., an immersive metric-drill "focus mode" or a presentation view — it is entered as an intentional state with a visible affordance, not adopted as the global chrome. A user should never land on a BareCount surface in dark mode without having asked for it.

5. **The "modern" signal comes from content patterns, not chrome.** Trust-chain visualization, the function-hue wheel, typography rhythm, motion on metric reveal, confident whitespace. Do not look modern by borrowing other products' chrome.

**Amends DEC-9a3c6a (D356 — DS governance, banned arbitrary hex).** D356 set the *mechanism* (tokens, no arbitrary hex). This decision sets the *aesthetic intent* those tokens must serve.

**Procedural effect:** any PR introducing a dark base background, default gradient chrome, or color without semantic role should be rejected or require an ADR. This ADR is the tiebreaker when the "should we go darker/bolder" temptation recurs.
