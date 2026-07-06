---
uid: DEC-063b5e
title: "Formula Rendering — AST Parser Replaces Regex for LaTeX Generation"
description: "Replace regex formula-to-LaTeX with tokenizer + AST parser for correct rendering of all formula patterns"
status: decided
subdomain: metric-rendering
focus: formula-ast-parser
date: 2026-04-04T15:17:16.124Z
project: bc-admin
domain: metrics
migrated_from: legacy v2 archive
---

# Formula Rendering — AST Parser Replaces Regex for LaTeX Generation

## Context

Regex for math expression parsing is fundamentally fragile. The O1=I1/I2 bug (output name inside fraction numerator) proved it. A proper parser is deterministic, handles all edge cases, and enables formula validation and editing features.

## Decision

Replace the regex-based formula-to-LaTeX converter in bc-admin with a proper tokenizer + AST parser. Current regex approach is fragile — it fails on nested expressions, misplaces the equals sign inside fractions, and cannot handle operator precedence correctly.\n\nThe AST parser will:\n1. Tokenize: split formula text into tokens (var codes, operators, parentheses, equals)\n2. Parse: build an expression tree respecting operator precedence (* / before + -)\n3. Render: walk the tree to emit LaTeX, using \\frac{}{} for division, \\times for multiplication, and proper grouping\n\nVariable code substitution (I1 → display name) happens at render time from the variable bindings, not during parsing. The raw expression (O1 = I1 / I2) is always preserved.\n\nThis also enables future capabilities: formula validation (check all referenced vars have bindings), dependency analysis, and formula editing with live preview.
