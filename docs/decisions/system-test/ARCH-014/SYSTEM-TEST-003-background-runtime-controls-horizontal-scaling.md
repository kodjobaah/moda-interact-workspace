---
id: ARCH-014-SYSTEM-TEST-003
architecture_id: ARCH-014
title: Validate runtime controls, global cadence and horizontal-scaling convergence end to end
task_kind: validation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: developer
completion_mode: manual
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-DATABASE-004
- ARCH-014-DATABASE-005
- ARCH-014-BACKGROUND-001
- ARCH-014-BACKGROUND-002
- ARCH-014-BACKGROUND-003
- ARCH-014-BACKGROUND-004
- ARCH-014-BACKGROUND-005
- ARCH-014-BACKGROUND-006
- ARCH-014-ADMIN-009
- ARCH-014-ADMIN-010
enables: []
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-014-SYSTEM-TEST-003

## Terminal/manual gate

Do not auto-start. Developer invokes this only after every dependency above is architect-accepted/integrated. Do not modify production code from this task.

## Objective

Prove that Admin runtime-control changes are durable, audited and safe under horizontal scaling, including the corrective distinction between **exclusive lease ownership** and **one shared global cadence window**.

A test that proves only "two replicas cannot hold the lease simultaneously" is insufficient.

## Environment

Use one PostgreSQL database and one Redis instance shared by all test processes.

Run at least two independently constructed Background process/service instances for concurrency scenarios. Use separate Node processes for terminal multi-replica scheduler/queue scenarios where the harness supports it.

Do not fake horizontal scaling by invoking one singleton twice in one call stack for the terminal global-cadence or BullMQ global-concurrency scenarios.

## Scenario A — optimistic Admin mutation

Start with config version `N`.

Issue two concurrent mutations carrying `expectedVersion = N` from independent request contexts.

Required:

```text
exactly one succeeds
resulting version = N + 1
exactly one BackgroundRuntimeConfigAuditEvent is created
loser returns the exact concurrency conflict
winner values remain authoritative
```

Repeat using two different tabs to prove there is still no silent field merge.

## Scenario B — retained lease row and monotonic fencing

For a controlled lease name:

1. remove only the test lease row;
2. race two distinct owners; exactly one obtains generation 1;
3. complete/release that cycle;
4. prove the row still exists and `lastFinishedAt` is non-null;
5. after making the cadence due in controlled test setup, reacquire;
6. prove generation is now 2, not reset to 1;
7. prove the generation-1 handle fails heartbeat and release against generation 2.

Evidence must include the persisted row after normal release.

## Scenario C — skewed multi-replica global cadence

This scenario is mandatory and is the regression test for the audit finding.

Run at least two scheduler replicas for `BILLING_RECONCILIATION` with intentionally skewed local wake times. Business work should be deliberately short so the lease is released well before the configured interval.

Observe multiple cadence windows, not a one-time start race.

Required:

```text
at most one completed BILLING_RECONCILIATION cycle in each shared cadence window
```

Specifically prove the old failure pattern cannot occur:

```text
replica B completes at ~T
replica A's independently skewed timer fires shortly afterward
replica A must NOT execute another cycle before T + configured interval
```

Repeat equivalent controlled evidence for recovery-capacity repair and translation reconciliation, using test-friendly setup rather than waiting production durations.

The assertion must be based on shared PostgreSQL cadence state (`lastFinishedAt` / DB time), not a process-local counter.

## Scenario D — live interval changes across replicas

Start with a known interval, complete one global cycle, then Admin-save a shorter interval without redeploying workers.

Required:

- config version propagates;
- waiting local schedulers may reschedule;
- database cadence uses the latest committed interval;
- at most one replica executes when the new cadence becomes due;
- an in-flight cycle is not interrupted.

Repeat with an **increased** interval and prove a stale replica that has not yet refreshed cannot run early using the old shorter process-local interval. The cadence-aware acquisition must follow current PostgreSQL configuration.

## Scenario E — runtime-config validation / last-known-good

After valid initialization, inject or simulate a newer invalid persisted row in a controlled test transaction (or use a repository-supported fixture that bypasses DB CHECK only for the service boundary test).

Required:

```text
invalid newer snapshot is rejected
current in-memory version/value remains the previous valid snapshot
listeners are not notified
refresh failure is logged
subsequent valid higher version is adopted
```

Initial startup with missing/unreadable/invalid singleton must fail readiness.

## Scenario F — no production fallback authority

Prove that translation batching, conversation settling and abuse-admission code do not fall back to compiled defaults when runtime config is not started.

In production-style wiring the not-started error must surface. In isolated tests, explicit injected readers remain supported.

## Scenario G — billing retry controls reach all periodic scanner paths

Configure non-default values for:

```text
billingProviderRetrySeconds
billingFrozenRecheckSeconds
```

Prove the periodic scanner uses them for:

```text
ordinary provider/API sync-error retry
frozen subscription retry
existing subscription with no current provider contract
```

The queued `nextReconcileAt`/delay must reflect the same immutable cycle snapshot.

Do not confuse this with the intentionally fixed billing lifecycle retry-tier structure.

## Scenario H — batch/throughput controls

Change and prove:

```text
billing shops per cycle
Shopify usage publish batch
recovery shops per repair
recoveries per resume job
translation reconciliation page size
translations per provider batch
```

The exact committed bound must reach the service query/processing boundary.

## Scenario I — translation retry separation

Set:

```text
translationPollIntervalSeconds = 120
translationResultRetrySeconds = 30
```

Prove provider polling uses 120 and failed result application uses 30.

No migrated translation tuning environment variable may override DB state.

## Scenario J — messaging settle controls

With two messaging replicas:

1. commit quiet window 3000 / max settle 10000;
2. save quiet window 1000;
3. wait for normal config convergence;
4. send a subsequent turn.

Prove later turns use 1000 without restart. Existing in-flight/finished work is not retroactively mutated.

## Scenario K — abuse protection

Lower one sender limit using Admin.

After config convergence, prove requests through more than one messaging replica share Redis counters and enforce the committed limit. Redis outage remains fail-closed.

Prove fixed one-minute/ten-minute windows did not become editable/change.

## Scenario L — fleet-wide BullMQ concurrency

For a controlled queue, run at least two Worker instances sharing Redis.

Configure global concurrency `4`; queue enough blocking jobs to exceed four.

Required:

```text
aggregate active jobs across all replicas <= 4
```

Admin-save `2`; allow already-active work to finish; prove subsequent aggregate active work converges to <=2 without worker restart.

Admin-save `6`; prove aggregate may rise to <=6.

A stale config replica must not revert Redis to an older cap after the newer DB version exists.

## Scenario M — Admin UI usability/hardening

Verify Admin Controls contains:

```text
Operational
Advanced
Abuse Protection
```

and grouped Setting / Value / Purpose-Guidance tables.

Verify:

- fleet-wide wording is scoped to Worker throughput;
- every row shows default/range;
- millisecond-backed invalid inputs report human seconds (`0.25..10`, `1..30`), not stored milliseconds;
- system-managed settings are not editable;
- merchant recovery delay is not duplicated as a global control;
- raw technical env names are not primary labels;
- stale save displays exact concurrency message.

## Evidence required

Completion evidence must include:

```text
migration/config version evidence
retained lease row with lastFinishedAt
monotonic generation evidence
skewed multi-replica cadence evidence across multiple periods
Admin concurrent-save evidence
runtime last-known-good validation evidence
billing retry-path evidence
multi-process BullMQ global-concurrency evidence
Admin DOM/screenshots for each tab
commands/tests executed
any environment limitations
```

## Pass condition

All scenarios A-M pass.

Any of the following is a failure:

```text
lost Admin update
duplicate global periodic cycle inside one cadence window
generation reset after normal release/reacquire
stale owner can heartbeat/release newer generation
invalid runtime snapshot replaces last-known-good
production fallback to compiled runtime defaults
periodic billing retry ignores committed runtime values
stale global-concurrency reversion
Admin-editable system-managed invariant
```
