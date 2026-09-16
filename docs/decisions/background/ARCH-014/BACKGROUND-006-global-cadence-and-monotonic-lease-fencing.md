---
id: ARCH-014-BACKGROUND-006
architecture_id: ARCH-014
title: Enforce one global cadence window and monotonic lease fencing across replicas
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 68
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-DATABASE-005
- ARCH-014-BACKGROUND-001
- ARCH-014-BACKGROUND-002
- ARCH-014-BACKGROUND-003
enables:
- ARCH-014-BACKGROUND-007
- ARCH-014-SYSTEM-TEST-003
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-014-BACKGROUND-006

## Objective

Correct two horizontal-scaling defects in the accepted runtime-lease foundation:

1. **exclusive execution is not the same as global cadence** — skewed replica timers can acquire the lease one after another and execute two global cycles inside one configured interval;
2. normal release currently `DELETE`s the lease row, so a later acquisition can restart `generation` at `1`, which means fencing generation is not monotonic across ordinary release/reacquire cycles.

After this task, PostgreSQL is authoritative for both current ownership **and** whether a global periodic job is due.

## Binding invariants

For these three leases:

```text
BILLING_RECONCILIATION
RECOVERY_CAPACITY_REPAIR
TRANSLATION_RECONCILIATION
```

all replicas share one cadence history. Local JavaScript timers are wake-up hints only.

For:

```text
QUEUE_CONCURRENCY_RECONCILIATION
```

there is no periodic cadence gate; its due interval is zero. Existing queue-concurrency convergence remains event/config driven.

The database clock (`NOW()`) is authoritative. Do not use `Date.now()` to decide cross-replica lease/cadence eligibility.

## Files in scope

Required production files:

```text
src/runtime/background-runtime-lease.ts
src/runtime/dynamic-leased-scheduler.ts
```

Required tests:

```text
tests/unit/runtime/background-runtime-lease.test.ts
tests/unit/runtime/dynamic-leased-scheduler.test.ts
tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts
scripts/test-integration.mjs
```

Do not redesign billing/recovery/translation business services in this task.

## Required acquisition semantics

Keep the public `tryAcquire(name)` call shape so the queue-concurrency controller does not need an unrelated API redesign.

Change its SQL so a conflicting lease row can be taken only when **both** conditions are true:

```text
leaseUntil <= PostgreSQL NOW()
AND
(lastFinishedAt IS NULL OR lastFinishedAt + authoritative cadence <= PostgreSQL NOW())
```

The authoritative cadence must be read by the acquisition SQL from:

```text
public.BackgroundRuntimeConfig(id = 'default')
```

using this exact mapping:

```text
BILLING_RECONCILIATION
    -> billingReconciliationIntervalSeconds

RECOVERY_CAPACITY_REPAIR
    -> recoveryRepairIntervalSeconds

TRANSLATION_RECONCILIATION
    -> translationReconciliationIntervalSeconds

QUEUE_CONCURRENCY_RECONCILIATION
    -> 0 seconds
```

Do not trust a process-local interval argument for the cross-replica due decision. A stale process must not be able to run early after a newer Admin change increased the interval.

Use fixed SQL/Prisma fragments for this mapping; do not construct a database column name from untrusted/runtime text.

The first acquisition of a name with no lease row remains immediately eligible and inserts generation `1` with `lastFinishedAt = NULL`.

If `BackgroundRuntimeConfig(id='default')` is unexpectedly missing, a scheduled periodic acquisition must not silently invent a cadence. Runtime-config readiness already treats that singleton as mandatory; preserve fail-closed behaviour rather than adding defaults here.

## Required release semantics

`release(handle)` MUST stop deleting the row.

Replace the `DELETE` with one guarded `UPDATE` matching:

```text
name
ownerToken
generation
```

On a successful normal release set, using PostgreSQL time:

```text
leaseUntil     = NOW()
heartbeatAt    = NOW()
lastFinishedAt = NOW()
updatedAt      = NOW()
```

Do not reset `generation`. Do not clear/recycle the owner token in a way that makes an old handle match a future generation.

Because the row remains, every later successful acquisition executes the existing conflict-update path and increments:

```text
generation = previous generation + 1
```

A stale older-generation heartbeat or release must affect zero rows.

A cycle that acquired the lease and then throws is still a completed scheduler attempt for cadence purposes, matching the existing scheduler behaviour that waits before retrying. Therefore `runWithLease` must perform the guarded normal release from its `finally` path when the lease has not already been lost.

If `leaseLost === true`, do not stamp `lastFinishedAt` from the stale owner.

## Dynamic scheduler semantics

Keep recursive non-overlapping `setTimeout`; do not introduce `setInterval`.

`startDynamicLeasedScheduler` must continue to:

1. require the runtime-config service to be started;
2. react to newer interval configuration by rescheduling a waiting local timer;
3. never interrupt an in-flight local run;
4. acquire the distributed lease before business work;
5. fresh-read runtime config after successful acquisition and pass one immutable snapshot to the cycle;
6. schedule another local wake after skip/completion/error.

New binding rule:

> A local timer firing does **not** mean work is due. Only a successful cadence-aware database lease acquisition means the global cycle is due.

Do not add process-local `lastRunAt`, module globals, Redis timestamps or per-replica cadence memory.

## Required integration test

Add:

```text
tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts
```

Use the repository disposable PostgreSQL integration harness. Do not sleep for production intervals.

The test must:

1. capture/restore the current `BackgroundRuntimeConfig` values it changes;
2. set `billingReconciliationIntervalSeconds = 10` (database minimum) using direct test setup;
3. delete only the test lease row for `BILLING_RECONCILIATION` before starting;
4. create two `BackgroundRuntimeLeaseService` instances with distinct explicit owner tokens;
5. race `tryAcquire(BILLING_RECONCILIATION)` and prove exactly one obtains generation `1`;
6. release the winner and prove the row still exists with non-null `lastFinishedAt`;
7. immediately race the two services again and prove **neither** can acquire inside the same cadence window;
8. move only that test row's `lastFinishedAt` far enough into the past using PostgreSQL test setup (for example `NOW() - INTERVAL '11 seconds'`); do not wait 10 seconds;
9. race again and prove exactly one owner acquires generation `2`;
10. prove the old generation-1 handle can neither heartbeat nor release generation 2;
11. clean up the lease row and restore modified runtime configuration in `finally`.

Add this integration test to the `defaultTests` list in `scripts/test-integration.mjs`.

## Required unit regression tests

### Lease tests

Prove SQL/behaviour includes:

```text
lastFinishedAt cadence eligibility
BackgroundRuntimeConfig authoritative cadence mapping
normal release uses UPDATE, not DELETE
normal release stamps lastFinishedAt with NOW()
release -> reacquire generation increases
stale generation cannot heartbeat/release
QUEUE_CONCURRENCY_RECONCILIATION has zero cadence gate
```

### Scheduler skew test

Add a deterministic fake-lease test with two scheduler instances whose local timers are intentionally offset.

Run multiple local wake periods. The fake lease must model shared `lastFinishedAt` cadence, not merely a boolean `acquired` flag.

Required assertion:

```text
within each shared cadence window there is at most one completed global run,
even though both replica timers fire at different times
```

A one-time simultaneous race is insufficient evidence.

## Required validation

Run from `moda-interact-background`:

```bash
npm run test:unit -- tests/unit/runtime/background-runtime-lease.test.ts tests/unit/runtime/dynamic-leased-scheduler.test.ts
npm run test:integration -- tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts
npm run test:unit
npm run build
git diff --check
```

If the disposable integration harness cannot apply the current database migration chain, record the exact migration blocker. Do not replace the required integration test with a mock and do not repair unrelated migration history in this task.

## Non-goals

Do not change:

```text
lease TTL = 120 seconds
heartbeat interval = 30 seconds
runtime-config refresh interval = 5 seconds
BullMQ queue-global-concurrency policy
business reconciliation algorithms
Admin forms
```

## Stop conditions

STOP and return to architect if:

- `DATABASE-005`/`lastFinishedAt` is absent;
- fixing cadence appears to require a second coordination store;
- an implementation would make local clocks authoritative;
- the queue-concurrency reconciler would become cadence-delayed instead of zero-cadence.
