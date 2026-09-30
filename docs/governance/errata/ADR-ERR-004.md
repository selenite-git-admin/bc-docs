---
id: ADR-ERR-004
title: "DEC-41e4bc roster: twelve controllers amended to thirteen (UI split into Customer Portal and Admin Portal; Metrics & Onboarding renamed Metric)"
status: adopted
authority: authoritative
affected: DEC-41e4bc (D637) — decision point 1, the roster
resolution: operator direction 2026-09-30, recorded in the design document (barecount-devhub PR 148, artifacts/controllers/DESIGN-session-protocol-controllers-2026-09-30.md, "Amendment" paragraph) and in docs/development/the-controller-operating-model.md
opened: 2026-09-30
---

# ADR-ERR-004 — DEC-41e4bc roster: twelve controllers amended to thirteen

## Contradiction summary

ADR DEC-41e4bc (decided 2026-09-30) names twelve controllers in decision point 1: Chief, Architect, Platform, Metrics & Onboarding, DB, DevHub, UI, Infra & CI, Audit, Docs, Demo, Compliance & Quality. On the same day, after the record was written, the operator directed two changes: the UI controller is split into a **Customer Portal** controller (bc-portal, the shared front-end conventions, bc-website-v2) and an **Admin Portal** controller (bc-admin), because the two surfaces serve different audiences under different scope rules; and "Metrics & Onboarding" is renamed **Metric** with its scope unchanged. The fleet is therefore thirteen controllers. The ADR text was not changed, so the record and the operating fleet disagreed.

## Amendment

Decision point 1 of DEC-41e4bc reads, as amended: thirteen controllers as DevHub data: Chief, Architect, Platform, Metric, DB, DevHub, Customer Portal, Admin Portal, Infra & CI, Audit, Docs, Demo, Compliance & Quality. Every other decision point of DEC-41e4bc is unchanged. The responsibility map splits the former UI rows into a bc-portal row (Customer Portal) and a bc-admin row (Admin Portal), with the shared front-end conventions owned by Customer Portal and reviewed by Admin Portal.

## Why an erratum, not a successor ADR

The change amends one point of a two-day-old record. A successor ADR would, under the ADR Hygiene Policy's supersession pair rule (DEC-623f8f rule 1), mark the whole of DEC-41e4bc superseded, which is false: its other nine points stand. An erratum keeps the record and states the amendment beside it.

## Sources

- Operator direction in chat with the Chief Controller, 2026-09-30 (recorded in the design document's amendment paragraph and in the Chief Controller's DevHub session SES-a1366c).
- Research report "Controller charters from documentation" (2026-09-30), Part A.1 and Part D decision 2, approved by the operator on 2026-09-30.
