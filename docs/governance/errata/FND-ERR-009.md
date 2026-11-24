---
id: FND-ERR-009
title: "The engine falls short of the amended metric life cycle: it activates a version that is not Demoed, refuses a second version of one metric contract, moves no tenant and sends no notice"
status: rejected
authority: authoritative
affected: The Contract Grammar §Lifecycle and deprecation policy, MCF Metric Contract family, and §Versioning and immutability on publish (as amended)
temporary_governance:
  - The Contract Grammar, MCF Metric Contract family and Versioning and immutability on publish (as amended); DEC-(platform-version record)
target_resolution: the engine is changed to match the amended Foundation (TSK-663b6b, TSK-d382f3, TSK-e2cf8b)
opened: 2026-11-22
---

# FND-ERR-009 — The engine falls short of the amended metric life cycle

## Contradiction summary

The Contract Grammar, as amended, says: a version of an MCF Metric Contract reaches `active` only
when it is Demoed, and each version is Demoed on its own; a change to a metric is a new version
of the same metric contract, and the prior version moves to `superseded`; a metric is its Metric
Directory Member, and its formula, grain and bindings may change from one version to the next;
when a new version enters `active`, the platform moves each tenant using the contract to it by a
recorded act at the moment of the notice, and each evaluation names the version it applies; a
change of meaning sends a critical notice, any other change that alters values sends a plain
notice, and a wording-only change sends none.

The engine does not do these things. The engine is wrong and is being changed to match. The
Foundation text stays as amended.

## Implementation behavior

- **Demoed is not required for `active`.** A version reaches `active` when its chain check
  passes; the chain check's self-verification is met by test cases the authoring panel wrote. No
  check that the version is Demoed stands between `audit_pending` and `active`.
- **One version per metric contract.** Every metric contract has exactly one version. A second
  version of the same contract is refused by the drafting code, the one-current-version rule, the
  supersession rules and a database check that a successor is a different contract. The identity
  hashes on a contract are frozen past draft, so its formula, grain and bindings cannot change by
  version. A replacement is made between two different contracts, and a contract can be replaced
  once.
- **No tenant is moved.** A tenant asks for a metric by its metric contract. After a
  replacement, the old contract answers `unsupported`, and nothing moves the tenant to the
  successor. Each value carries its contract and version, but the version is the contract's
  current active version at the moment of evaluation, not one named by a recorded move.
- **No notice is sent.** The engine records two classes of change, `editorial` and
  `meaning_bearing`, not the three kinds the Foundation names. No service sends a notice to a
  tenant.
- **Contextual scores still gate a decision fed by the signed exchange.** The activation
  predicate `metric_audit.fn_intrinsic_decision_refusal` refuses a version whose decision arrived
  on the signed exchange feed (`feed_event_uid` present) when any contextual score is below 4 or
  the contextual decision is not `HIGH_CONFIDENCE` or `VERIFIED` (bc-db
  `migrations/0063_c8_rebase_intrinsic_decision_refusal.sql`, lines 127-136; applied to the live
  database on 2026-11-09). A decision of the certification panel running inside the platform gates nothing there
  (the same file, lines 123-126). No task carries this respect yet.

## Temporary governance

The amended Foundation text governs. Nothing in this entry permits the behaviour described
above: an act that relies on it does not meet the Foundation, and the engine's present behaviour
is not accepted in the meantime.

## Resolution state

Rejected: the engine is changed to match the Foundation. Each task comes back to the owner as a
design first, and no engine change is made without his go:

- TSK-663b6b — becoming `active` requires the version to be Demoed, each version on its own.
- TSK-d382f3 — a metric takes new versions in place: a new version of the same metric contract,
  the prior version superseded, each tenant moved by a recorded act, each evaluation naming its
  version.
- TSK-e2cf8b — the notice to each tenant by the kind of change, for contracts and metrics alike.

The entry is closed when the three are built, the respect that no task carries yet is resolved, and the engine's behaviour matches the text.

## References

- DEC-(platform-version record) — the platform-version record of this amendment (The Authority
  Model, "A new platform version declared through ADR"); its uid is inserted when it is created
- The Contract Grammar — MCF Metric Contract family; Metric Directory Member family; Versioning
  and immutability on publish
- The Invariants — Invariant III (versions coexist; supersession changes future use) and
  Invariant IV (explicit references)
- DEC-c48b0f, DEC-025bfc, DEC-d5fb43 (as amended 2026-11-22)
