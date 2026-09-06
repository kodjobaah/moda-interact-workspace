---
id: ARCH-004-SYSTEM-TEST-001
architecture_id: ARCH-004
title: Verify cart activity resets recovery inactivity clock
task_kind: verification
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: ready
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-004-SHARED-002
  - ARCH-004-SHOPIFY-001
  - ARCH-004-BACKGROUND-002
  - ARCH-004-SHOPIFY-002
enables: []
created: 2026-09-05
updated: 2026-09-05T19:30:00Z
---

# Verify cart activity resets recovery inactivity clock

## Objective

Prove the integrated ARCH-004 flow from Shopify cart webhook through BullMQ,
Background pending-candidate rescheduling, Redis shop index and merchant UI.

## Core live scenario

Use one test shop and one checkout/cart pair.

Capture:

```text
T0 checkout.created
candidate.lastActivityAt = T0
candidate scheduledFor   = T0 + recoveryDelay
```

Then perform a real cart change that produces a correlated cart webhook.

Capture:

```text
T1 cart.activity
T1 > T0

same pending candidate identity
candidate.lastActivityAt = T1
scheduledFor             = T1 + recoveryDelay
shop ZSET score          = scheduledFor
```

The merchant panel after manual Refresh must show:

```text
LAST ACTIVITY      -> T1
RECOVERY SCHEDULED -> shifted later
STATUS             -> Scheduled
```

## Required verification scenarios

### 1. Matching cart activity

A cart event carrying the candidate's indexed cart token reschedules the same
candidate.

No duplicate candidate is created.

### 2. Unmatched cart

A different/unindexed cart token does not modify the candidate.

No cross-tenant/cross-checkout match is permitted.

### 3. Monotonic/out-of-order event

A controlled older activity event must not move:

```text
lastActivityAt
scheduledFor
shop ZSET score
```

backwards.

This may be demonstrated with deterministic integration evidence rather than a
live Shopify-delivery replay if Shopify cannot emit an older webhook safely.

### 4. Confirmed empty cart

A matched:

```text
isEmpty = true
```

event removes the pending candidate and its:

```text
checkout alias
cart alias
shop ZSET member
```

The merchant panel no longer lists it after Refresh.

### 5. Unknown emptiness

`isEmpty = null` must not cancel a matched candidate.

### 6. Checkout update

A checkout update before materialization resets the candidate timer.

A checkout update after materialization must preserve the existing
CheckoutRecovery refresh behaviour from ARCH-001.

### 7. Queue topology

Prove cart activity is processed under:

```text
checkout-events
```

with:

```text
jobName = cart-activity
```

and that no `cart-events` queue was introduced.

## Evidence

Evidence must be PII-safe.

Do not store:

```text
customer email
phone number
raw cart contents
checkout URL/token in browser-facing evidence
Redis credentials
```

Developer-only correlation evidence may contain opaque cart/checkout tokens
where required to prove deterministic linkage, but they must not be represented
as merchant browser data.

## Acceptance criteria

- [ ] matched cart activity moves due time forward.
- [ ] same candidate is refreshed rather than duplicated.
- [ ] shop ZSET score matches the new due time.
- [ ] merchant UI shows `LAST ACTIVITY`.
- [ ] manual Refresh reflects reschedule.
- [ ] stale event cannot move clock backwards.
- [ ] unmatched cart cannot mutate candidate.
- [ ] confirmed empty cart cancels.
- [ ] unknown emptiness does not cancel.
- [ ] checkout update pending-candidate behaviour passes.
- [ ] post-materialization checkout refresh regression passes.
- [ ] cart work uses existing checkout-events queue.
- [ ] evidence contains no merchant-facing sensitive leakage.


## Developer manual-validation checkpoint

All implementation dependencies are now Complete and architect-accepted.

This task is therefore `Ready`, but it is intentionally a terminal validation
task.

The expected execution order is:

```text
implementation complete
        |
        v
developer manually exercises ARCH-004
        |
        v
/moda-task ARCH-004-SYSTEM-TEST-001
```

Do not treat this Ready state as a requirement to execute immediately.

Manual developer validation is not a task dependency and does not alter the
system-test acceptance criteria.

## Completion Report

### Status

Not started.

## Architect Review

### Review Status

Pending
