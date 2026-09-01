---
uid: DEC-1c5af4
title: "Demo World Foundry is Odoo-scoped; source-generality deferred to rule-of-two"
description: "Demo World Foundry is Odoo-scoped; source-generality deferred to rule-of-two"
status: decided
date: 2026-09-01T06:32:31.011Z
project: bc-synth
domain: demo
subdomain: world-foundry
focus: scope
---

# Demo World Foundry is Odoo-scoped; source-generality deferred to rule-of-two

## Context

No rationale recorded.

## Decision

Context: The Demo World Foundry emerged 2026-09-01 as the build console + foundry engine + run-package chain for the v3 KPC demo world. Its navigation, extraction and executors were built against Odoo 19 Enterprise. The question arose whether it is (or should claim to be) a source-agnostic demo-building framework.

Decision (operator ruling 2026-09-01):
1. The Foundry is DECLARED Odoo-scoped. Its design vocabulary (78 apps, 610 menus, module closures, install/not-required verdicts), its graph extraction, and every build executor are Odoo 19 EE constructs; a Salesforce or Dynamics demo would need new extraction, new executors and a different design vocabulary. The product is named "Odoo Demo World Foundry".
2. The reusable asset is the METHOD, not the software: design sheets -> receipted build (hash-chained, commit-only-on-green) -> gated validation; solve-then-build including the paper cash solve; the three-layer scoping (global machinery / source system / world); the blueprint + coverage rollup; declared-behavior parity checks.
3. Source-generality is deferred to the rule of two: shared machinery is extracted only when a second concrete source system exists in sources/<x>/. Building modular multi-source capability now is judged complex AND premature. A second source system brings its own foundry instance sharing the method.
4. Layering stands: global (foundry docs/engine/console under tooling), source-system (the Odoo estate runbook), world (each package). The queued repo-root move of engine+console proceeds under this Odoo-scoped identity.
