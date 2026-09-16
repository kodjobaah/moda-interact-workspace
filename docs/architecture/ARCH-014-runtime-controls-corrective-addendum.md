# ARCH-014 corrective runtime-control gap addendum

Date: 2026-09-16

This addendum records the post-implementation audit findings from the supplied `moda-interact-workspace(20260916-094937).zip` snapshot. It supersedes the narrower assumption that a non-overlapping process-local scheduler plus an exclusive lease is sufficient for horizontally scaled global cadence.

## Binding distinction: ownership vs cadence

A distributed lease answers:

```text
Who may execute now?
```

It does **not**, by itself, answer:

```text
Is the next global cycle due yet?
```

For `BILLING_RECONCILIATION`, `RECOVERY_CAPACITY_REPAIR` and `TRANSLATION_RECONCILIATION`, PostgreSQL must persist both facts.

`BackgroundRuntimeLease.lastFinishedAt` is therefore the global cadence history. A periodic lease can be acquired only when:

```text
leaseUntil <= PostgreSQL NOW()
AND
(lastFinishedAt IS NULL OR lastFinishedAt + latest configured interval <= PostgreSQL NOW())
```

The interval comes from the current `BackgroundRuntimeConfig(id='default')` row inside the acquisition decision. A stale replica cannot make itself eligible using an older process-local interval.

`QUEUE_CONCURRENCY_RECONCILIATION` uses a zero-second cadence gate because it is convergence/event driven rather than one of the three global periodic loops.

## Retained lease rows and fencing

Normal release no longer deletes a lease row. It atomically expires the current owner and records `lastFinishedAt = NOW()` under `name + ownerToken + generation` fencing.

Because the row survives, every successful reacquisition increments the existing generation:

```text
1 -> 2 -> 3 -> ...
```

An old handle can never become equivalent to a later handle owned by the same long-lived process token.

## Local timers are wake-up hints

Every replica may keep a recursive local `setTimeout`, and config updates may reschedule that local timer. The local timer does not authorize work. The cadence-aware database acquisition does.

This prevents skewed replicas from producing sequential duplicate global cycles such as:

```text
replica B run at 60.0s
replica A run at 61.0s
```

inside one 60-second global cadence window.

## Runtime-policy authority

Production business services do not fall back to compiled test defaults when `BackgroundRuntimeConfigService` has not started. Startup wiring errors must surface.

After successful startup:

```text
valid newer row     -> adopt
invalid newer row   -> retain last-known-good, log, do not notify
read outage         -> retain last-known-good
```

Background validates the same min/max and cross-field contract enforced by DATABASE-004 before adopting a snapshot.

## Billing periodic retry authority

The periodic billing scan's no-provider and scanner-error retry paths use the cycle snapshot:

```text
billingProviderRetrySeconds
billingFrozenRecheckSeconds
```

Literal 5-minute / 60-minute retry values are not separate production authorities.

The existing billing lifecycle retry-tier structure remains intentionally system-managed.

## Current corrective execution graph

```text
ARCH-014-DATABASE-005 COMPLETE
        |
        v
ARCH-014-BACKGROUND-006 READY
        |
        v
ARCH-014-BACKGROUND-007 PENDING
        |
        +--------------------------+
                                   |
ARCH-014-ADMIN-010 READY ----------+----> ARCH-014-SYSTEM-TEST-003 PENDING
        |
        +------------------------------> ARCH-014-SYSTEM-TEST-002 PENDING
```

`DATABASE-005` is architect-accepted Complete. `BACKGROUND-006` is now Ready. `ADMIN-010` remains independently Ready and can run in parallel with `BACKGROUND-006`.
