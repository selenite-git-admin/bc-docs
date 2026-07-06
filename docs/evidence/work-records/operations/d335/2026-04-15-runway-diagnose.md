# D335 Runway Diagnose — 2026-04-15

**Session:**   
**Tenant (for testability check):** demo-selenite  
**Total MCs diagnosed:** 1  
**Elapsed:** 0s  
**AI enabled:** true

## Distribution

| Bucket | Count | % |
|---|---:|---:|
| human-required | 1 | 100.0% |

**Definitions:**
- `walkable` — verdict=auto-fixable AND bound CC has COs in the target tenant. Safe to walk end-to-end.
- `untestable` — verdict=auto-fixable BUT zero COs in tenant; fix can't be verified. Apply after reader/OC work.
- `human-required` — needs human judgment (AI ambiguous, class 3 latest, mapping coverage, unit coherence).
- `blocked` — CF↔BF semantic mismatch (heuristic or AI) OR missing BF source. Upstream CC fix required.
- `ready` — no fail findings; MC is healthy. Shouldn't be here if it's on the runway — surface for review.

## By subfunction

| Subfunction | Total | Walkable | Untestable | Human | Blocked | Ready |
|---|---:|---:|---:|---:|---:|---:|
| capital_structure_optimization | 1 | 0 | 0 | 1 | 0 | 0 |

## Fail-finding class counts

| Check Code | Count |
|---|---:|
| `D335_SUM_ON_LATEST` | 1 |

## Walkable MCs (verdict=auto-fixable AND testable)

_None._ Every runway MC is either blocked, human-required, or untestable.

## Per-MC results (first 50)

| # | MC | Subfunction | Verdict | Bucket | Testable | COs | Findings |
|---|---|---|---|---|---|---:|---|
| 1 | `mc__equity_turnover_ratio` | capital_structure_optimization | human-required | human-required | ✓ | 1368 | D335_SUM_ON_LATEST, CF_BF_AI_AMBIGUOUS, MAPPING_COVERAGE_GAP |
