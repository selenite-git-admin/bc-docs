---
id: platform-refactor-program-the-thread
order: 45.12
title: "The Thread"
status: drafting
authority: reference
depends_on: [devhub, documentation-system, decision-and-change-procedure]
governing_sources:
  - Platform Refactor Program (the thread; the order of work; when the program is finished)
  - Vocabulary (the status words and the definition of done)
governing_adrs:
  - DEC-71f15e (the Platform Refactor Program)
  - DEC-c220e4 (the interim rule on which metrics a tenant sees)
errata_referenced: []
v2_sources: []
diagrams: []
---

# The Thread

This annex is part of the [Platform Refactor Program](../platform-refactor-program.md). The thread is one tenant and one metric, followed from the metric being available to a user of the tenant seeing its value. It is the program's running test that the parts join. This annex names the metric, lists the steps, lists what must be built for it, and proposes the two metric shapes of the finish test. Each is approved by the operator.

It was read at bc-docs `1860bf65`, bc-core `df52506d` and barecount-devhub `b00e9f85`, and the platform database with read-only queries on 2026-11-14. No tenant database was read, so nothing here states a value Kaveri holds as a fact.

## 1. The tenant and the metric

The tenant is Kaveri, the demo tenant.

**The metric proposed is `receivable_control_balance`** (metric contract `48ea2628-e31c-4add-8ee3-cef23b40cfe9`): the balance of the receivables control account, a sum that is cumulative to date. It is chosen from the reference set by five plain tests.

| Test | Why it matters | This metric |
|---|---|---|
| One source table | The fewest parts between the source and the value | Yes: journal entry lines |
| Its chain is judged green today | The thread should not begin on a known break | Reported so by a reader on 2026-11-14; unverified |
| It is enabled for Kaveri today | A value exists to follow to the portal | Reported so by a reader on 2026-11-14 (its provisioning command `provisioned`); unverified |
| An expected value, worked out apart from the platform, is on a main branch | "Done" needs agreement with such a value | Yes: values for four dates in `barecount-devhub:artifacts/metric-audit/foundry-tally/reference-receivables.json` (read at `b00e9f85`) |
| Its canonical contract has two versions in force | The thread then tests which version an act uses (stitch contract 2) | Reported so by a reader on 2026-11-14 (canonical contract `cc-x13pb`, versions 2.0.0 and 3.0.0); unverified |

Three metrics of the reference set pass the first four tests: this one, `receivable_billed_amount` and `receivable_days_sales_outstanding`. The alternate, if the operator prefers a harder case, is `receivable_days_sales_outstanding`: it adds a trailing window and is made of two other metrics, which must be enabled first.

**What is not established about the metric.**
- The file records where its values came from: a recompute on the posting basis, run read-only against the demo source system on 2026-10-02, apart from the platform. That is documented provenance; it has not been checked by an independent read of the source system for this program. Ruling B5 decides what an expected value must be worked out from.
- Whether today's engine reproduces them. The first reference run, in phase 3, answers that.
- **The enabling step cannot be walked afresh on this metric,** because it is already enabled for Kaveri, and nothing disables a metric today. On the thread, that step is shown by the enabling command's own check and verify on the existing state. A fresh enabling is shown by the finish test, which takes a new metric through it.
- Whether a user of Kaveri can sign in and sees the value. No service was started for this annex.

## 2. The steps

"Today" says whether the step can be performed now by a governed act alone. The last column names the stitch contract the step crosses.

| # | Step | Function | The act | Today | Contract |
|---|---|---|---|---|---|
| 1 | Certified | L6 | The request, the panel's decision and the governed admit act | Done for this metric. For a new metric: yes, by separate routes; no single command | 8 |
| 2 | Released | L6, L8, DL | The platform offers a certified metric | No: no act and no record. Every certified metric is treated as released | 4, 8 |
| 3 | In a package | S4 | The metric is named in a package | No: the package table names readers, not metrics | 4, 6 |
| 4 | Subscribed | S4, DL | The tenant is given a package: one Subscription, in force | No: no record. Every active tenant is treated as subscribed to every available metric (decision DEC-c220e4) | 6, 11 |
| 5 | The tenant is active | S3, S2, S1 | Create the tenant and its first admin; the admin verifies; the tenant becomes `active` only with a verified admin **and** its one Subscription (decision DEC-cf6d3b) | In part: the tenant and its admin are created by two acts that nothing links, and `active` is reached without either check. Kaveri is `active` | 11 |
| 6 | Enabled | L10, DL | The onboarding act (`POST /schema-provisioner/onboard-metric`), then the provisioning worker | Yes, by a platform admin's call and a command run at a terminal. The tenant's admin cannot do it | 3, 5, 6 |
| 7 | Admitted | L7, RT | A reader is executed (`POST t/readers/:readerId/execute`) | Yes; the source system must be started first | 1 |
| 8 | Canonical objects resolved | RT, L5 | The resolve command (`POST t/ccv2-resolve`) | Yes, by hand only; it reads the version in force on the platform, not the one the tenant adopted | 1, 2, 3, 10 |
| 9 | Reporting | RT, EV | The governed evaluation (`POST t/metric-evaluation-governed`), which writes its Evidence with the act | Yes; the caller supplies the date | 1, 2 |
| 10 | In agreement with an expected value, written down | PV | Compare the reported value with the expected one and keep the record | Only by a workaround: a script kept outside the engine (`foundry-tally.mjs`). No governed act and no record | 8 |
| 11 | Visible | DL, TS | The tenant's admin shows the metric | No: no record. Every metric is treated as visible | 7 |
| 12 | Seen in the portal | TS, S1 | A user of Kaveri signs in and reads the value | The read exists; it was not run for this annex | 7 |

Of the twelve steps, four can be performed today by a governed act alone (1, 7, 8, 9, with the limits stated), one in part (5), one by a governed act that only a platform admin can start (6), one only by a workaround (10), one was not run (12), and four do not exist (2, 3, 4, 11). Step 4 comes before step 5 because a tenant is not active without its Subscription.

## 3. What the thread needs that does not exist

By ruling T2 this is the whole of what the program builds for subscription and delivery. A new record is a database change and needs the operator's approval when it is made; approving this list does not approve it.

| # | What is needed | Function | A new record? | Contract |
|---|---|---|---|---|
| 1 | A record that Kaveri has the interim package, which says "all" (rulings T6 and T12), and the check of it before a tenant is `active` | S4, S3 | Yes | 6, 11 |
| 2 | The enabling act checks that the metric is offered, is in the tenant's package and has what it requires, and refuses with a reason | L10, DL | No | 4, 5, 6 |
| 3 | What a metric version requires, declared on the version | L6 | Yes | 5 |
| 4 | The record of the version a tenant adopted, for a canonical contract and for a metric, and the resolver and the evaluation reading it | DL, L5, RT | Yes | 2, 3 |
| 5 | The resolve command issued by the scheduled cycle between admissions and evaluations; the period from the fiscal calendar for the tenant's declared legal entities (rulings B6 and B7) | RT | No | 1 |
| 6 | The reason a metric is not reporting, readable by the tenant's list and shown in the portal | RT, TS | No | 7 |
| 7 | A governed act and a record for agreement with an expected value on the tenant's own data | PV | Yes | 8 |
| 8 | The tenant's creation and its first admin joined in one act | S3, S2 | Not established | 11 |

Designed in phase 2 and **not** built in the program, because the thread does not need them: the release record (every certified metric stays treated as released); a package that lists metrics; the visible and hidden switch (every metric stays treated as visible); disabling a metric; billing and the tiers.

## 4. The two metric shapes of the finish test

The finish test takes one metric from a source table not used before to "done" for a tenant, and then a second metric of a different shape. The operator names the two shapes in phase 2.

The shapes among the metric versions in force (a reader's count, 2026-11-14): a total for one period; a balance as of a date; a total cumulative to date; a figure at a point in time; and a figure over a trailing window of periods.

**Proposed, as one fixed pair: a count for one period, and a balance as of a date.** They differ in kind: the first counts rows inside one period; the second is a standing amount at a date, built from everything before it. Both shapes exist among the versions in force.

**The alternative, for the operator to choose in place of the second:** a ratio over a trailing window of periods. It is the harder test, since it spans several periods and is made of other metrics. It is not proposed because it is not established that a metric of that shape can be drawn from a source table not used before, which the finish test requires. The desk request names the pair being approved.

## 5. Not established

- Every value Kaveri holds, and every fact inside a tenant database.
- Whether the demo source system can still be read with the access it has.
- Whether Kaveri has a user who can sign in.
- The size of the reference set: the scouting record's heading says twelve metrics and its table lists thirteen.
