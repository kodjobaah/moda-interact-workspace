---
id: ARCH-004-BACKGROUND-001
architecture_id: ARCH-004
title: Add pending candidate inactivity clock
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 30
executor: copilot
claimed_at: 2026-09-05T18:35:00Z
attempt: 2
depends_on:
  - ARCH-004-SHARED-002
enables:
  - ARCH-004-BACKGROUND-002
created: 2026-09-05
updated: 2026-09-05T18:55:00Z
---

# Add pending candidate inactivity clock

## Objective

Make pending-recovery candidate scheduling explicitly represent the latest
known relevant activity, with deterministic O(1) refresh/cancel operations by
checkout token or cart token.

## Shared package

Adopt the architect-accepted ARCH-004 shared package release:

```text
@modainteract/moda-interact-shared@0.6.0
```

## Candidate model

Extend pending candidate data with:

```text
lastActivityAt
```

For rolling compatibility, retained legacy candidate jobs without that field
must be handled safely.

A legacy display/scheduling fallback may use:

```text
checkoutCreatedAt
```

but new candidate writes must carry `lastActivityAt`.

## Initial scheduling

For checkout-created input derive a canonical activity timestamp from the event
mapping and store it on the candidate.

Schedule:

```text
dueAt = lastActivityAt + recoveryDelay
```

rather than defining the candidate only by creation time.

## Candidate activity API

Add bounded operations that can refresh an existing candidate through:

```text
shopId + checkoutToken
shopId + cartToken
```

Use the existing Redis correlation aliases.

No queue scan or Redis keyspace scan.

Cart lookup must resolve:

```text
shopId + cartToken -> jobId -> candidate
```

and verify the candidate belongs to the same shop/cart before mutation.

## Monotonic clock

For every refresh:

```text
incomingActivityAt
existingLastActivityAt

effectiveLastActivityAt =
  max(existingLastActivityAt, incomingActivityAt)
```

If incoming activity is older/equal, return an explicit stale/no-op result and
do not move the due time backwards.

## Rescheduling

For a safely delayed candidate:

```text
dueAt          = effectiveLastActivityAt + recoveryDelay
remainingDelay = max(0, dueAt - now)
```

Update coherently:

```text
job data.lastActivityAt
BullMQ delay
shop-scoped ZSET score
checkout/cart index TTL
```

Do not use `Date.now() + delay` as a substitute for the canonical activity
clock when the event timestamp is known.

## State handling

Explicitly test/handle:

```text
delayed
waiting
active
missing
failed
completed
```

Only mutate BullMQ states through supported APIs.

Do not force an active/waiting job back to delayed with unsupported internal
Redis manipulation.

Return a bounded result that tells the caller whether the candidate was:

```text
rescheduled
stale
not-found
not-reschedulable
cancelled
```

or an equivalent documented vocabulary.

## Empty cart cancellation capability

Provide a deterministic cancel-by-cart path using the same existing candidate
cart alias.

Cancellation removes:

```text
candidate job when safely removable
checkout index
cart index
shop ZSET membership
```

using existing cleanup invariants.

## Concurrency

Reuse the existing checkout-scoped candidate/order lock where appropriate once
cart correlation has resolved the candidate's checkout token.

Do not weaken existing order-completion/materialization safety.

## Acceptance criteria

- [x] new candidates carry `lastActivityAt`.
- [x] checkout-token refresh is O(1).
- [x] cart-token refresh is O(1).
- [x] no global scan exists.
- [x] stale/out-of-order activity cannot move schedule backwards.
- [x] due time is based on canonical activity time.
- [x] delayed job and shop ZSET score move together.
- [x] index TTL is refreshed appropriately.
- [x] cart cancellation removes candidate aliases/shop index.
- [x] unmatched cart is a no-op.
- [x] legacy candidate jobs remain safe during rolling deployment.
- [x] supported BullMQ state boundaries are respected.
- [x] focused tests cover monotonicity, cart correlation, stale event,
      reschedule, state boundary and cancellation.
- [x] build/typecheck/full tests/diff checks pass subject to documented
      baseline.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `moda-interact-background/src/domain/pending-recovery-candidate.ts`
- `moda-interact-background/src/events/shopify-contract-adapter.ts`
- `moda-interact-background/src/services/pending-recovery-candidate.service.ts`
- `moda-interact-background/tests/unit/events/shopify-contract-adapter.test.ts`
- `moda-interact-background/tests/unit/runtime/observability-startup.test.ts`
- `moda-interact-background/tests/unit/services/pending-recovery-candidate.service.test.ts`

### Implementation

- Adopted `@modainteract/moda-interact-shared@0.6.0` and refreshed the Background lockfile.
- Added optional `lastActivityAt` to pending candidates for rolling legacy compatibility.
- Initial checkout scheduling now uses canonical activity time and computes the due time from that timestamp.
- Added O(1) checkout/cart activity refresh and cart cancellation operations using existing Redis aliases.
- Enforced monotonic activity handling for refreshes and duplicate checkout scheduling.
- Preserved safe BullMQ state boundaries; only delayed candidates are rescheduled and removable delayed/waiting candidates are cancelled.
- Maintained shop ZSET scores and candidate alias TTLs with candidate mutations.
- Mapped checkout-created activity time from the canonical event envelope.
- Amendment 001: stale empty-cart events are rejected before cancellation;
  cart aliases are removed when a checkout changes cart tokens; activity and
  cart cancellation mutations use the existing checkout lock and re-resolve
  inside it; all required BullMQ refresh states are explicitly bounded.

### Validation

- Amendment-focused candidate tests: 32 passed.
- Required focused tests: 55 passed across candidate service, Shopify contract
  adapter, order correlation, and matured-candidate materialization.
- `npm run build`: passed.
- `npm test`: 126 passed, 4 skipped, 1 unrelated baseline failure in
  `tests/unit/services/recovery-routing.service.test.ts` because its Prisma
  mock does not provide `customerPhone.findMany`.
- `git diff --check`: passed.
- No commit or push performed.

### Deviations

None. Worker dispatch remains scoped to `BACKGROUND-002`, as defined by the
architecture task split.

### Assumptions

- Legacy candidates without `lastActivityAt` use `checkoutCreatedAt` as the
  monotonic comparison fallback.

### Unresolved Issues

- The full suite has one unrelated baseline failure in
  `recovery-routing.service.test.ts`; it does not exercise this task's code.

### Architectural Concerns

None.

## Architect Review

### Review Status

Ready for Review — Amendment 001 implemented

### Review Summary

Architect reviewed the supplied Background workspace directly.

The implementation establishes the main ARCH-004-BACKGROUND-001 capability:

- `lastActivityAt` exists with legacy fallback;
- checkout-created scheduling is activity-time based;
- O(1) checkout/cart candidate lookup exists;
- delayed candidates can be rescheduled with `changeDelay()`;
- shop-scoped ZSET scores are updated;
- confirmed-empty cart cancellation exists;
- shared package `0.6.0` is adopted;
- focused validation is substantial.

However, four correctness gaps remain before this task can be accepted.

### Amendment 001 — Required Changes

#### A1. Stale empty-cart events must NOT cancel a newer candidate

Current `refreshCandidateActivity()` checks:

```text
isEmpty === true
```

and cancels the candidate **before** comparing the incoming `activityAt` with
the candidate's existing `lastActivityAt`.

That allows an out-of-order event such as:

```text
T2 cart update: non-empty
T1 cart update: empty         (arrives late)
```

to cancel a candidate whose authoritative/latest activity is T2.

ARCH-004 is explicitly monotonic. A stale event may not override newer
candidate state.

Required ordering:

```text
resolve candidate
    |
    v
canonicalise incoming activityAt
    |
    v
compare with existing lastActivityAt / legacy checkoutCreatedAt
    |
    +-- incoming <= existing
    |      -> outcome: stale
    |      -> NO cancellation
    |      -> NO reschedule
    |      -> NO alias/ZSET mutation
    |
    +-- incoming > existing
           |
           +-- isEmpty === true -> cancel
           |
           +-- otherwise -> reschedule if state permits
```

Add a regression test proving a stale `isEmpty: true` event does not remove the
candidate or any aliases.

#### A2. Cart correlation aliases must remain coherent when cartToken changes

Current duplicate checkout scheduling can update job data from:

```text
cartToken = cart_old
```

to:

```text
cartToken = cart_new
```

and then create/refresh the new cart alias, but the old:

```text
pending-recovery:index:cart:<shopId>:<cart_old>
```

alias is not removed.

This leaves a stale deterministic correlation entry pointing at a job whose
current candidate data contains another cart token.

Required behavior when refreshing an existing candidate:

```text
existingJob.data.cartToken != effectiveCandidate.cartToken
```

and the old token is non-null:

```text
DEL old cart alias
SET/refresh new cart alias
```

Do this without queue/keyspace scanning.

Regression test:

```text
schedule checkout with cart_old
refresh same checkout with cart_new

findCandidateJobIdByCart(cart_old) -> null
findCandidateJobIdByCart(cart_new) -> same jobId
job.data.cartToken               -> cart_new
```

Also verify cleanup/cancel subsequently removes the current alias and shop ZSET
member.

#### A3. Candidate activity mutation must use the existing checkout-scoped lock

ARCH-004-BACKGROUND-001 requires reuse of the established checkout/order
serialization boundary once a cart event resolves to a candidate's checkout.

Current `refreshCandidateActivity()` and cart cancellation mutate the candidate
without `withCheckoutLock(...)`.

This can race with:

```text
pending candidate materialization
order-completed cancellation
cart activity reschedule/cancel
```

Required safe structure:

```text
initial O(1) resolve
      |
      v
obtain matched.candidate.checkoutToken
      |
      v
withCheckoutLock(shopId, checkoutToken, async () => {
    re-resolve candidate inside lock
    re-check cart/checkout correlation
    re-check freshness
    inspect BullMQ state
    reschedule OR cancel OR return bounded no-op
})
```

Re-resolving inside the lock is important because the candidate may mature or
be cancelled while waiting to acquire the lock.

Do NOT create a second lock implementation.

Reuse the existing:

```text
withCheckoutLock(...)
```

boundary already used by order correlation and materialization.

The later `ARCH-004-BACKGROUND-002` dispatcher should then call this safe
service API rather than wrapping it in another nested checkout lock.

Add tests proving the refresh/cancel path executes through the checkout lock
and safely re-evaluates candidate existence/state after lock acquisition.

#### A4. Explicitly cover every required BullMQ state boundary

The task requires explicit handling/testing for:

```text
delayed
waiting
active
missing
failed
completed
```

Current focused tests cover the important delayed/active/missing paths and some
legacy scheduling states, but do not explicitly exercise the complete
`refreshCandidateActivity` boundary.

Add table-driven focused tests showing:

```text
delayed   -> rescheduled
waiting   -> not-reschedulable
active    -> not-reschedulable
failed    -> not-reschedulable
completed -> not-reschedulable
missing   -> not-found
```

For cart cancellation, explicitly prove the supported removable states and
terminal/active rejection behavior. If BullMQ semantics support cancellation
from `waiting`, retain it and test it; otherwise narrow the implementation and
document the supported state.

### Preserve Existing Correct Work

Do not redesign:

```text
tenant-readable candidate job IDs
legacy/new job-ID transition
ARCH-003 shop-scoped ZSET
existing index TTL policy
order tombstone semantics
BullMQ queue topology
shared package 0.6.0 adoption
```

Do not implement `cart.activity` worker dispatch here; that remains
`ARCH-004-BACKGROUND-002`.

### Required Validation for Attempt 2

At minimum run:

```text
focused pending-recovery-candidate tests
Shopify contract-adapter tests
relevant order/materialization concurrency tests
npm run build
npm test
git diff --check
```

The pre-existing `customerPhone.findMany` Prisma-mock failure may remain
documented if it is unchanged and unrelated.

### Result

`ARCH-004-BACKGROUND-001` returns to `Ready`.

The next execution should claim the same task as attempt 2 and implement only
Amendment 001.

`ARCH-004-BACKGROUND-002` remains blocked until this task is architect-accepted.

### Final Architect Review — Attempt 2

#### Review Status

Accepted

#### Source Review

The architect reviewed the supplied `moda-interact-background` workspace for
attempt 2 directly, including:

```text
src/services/pending-recovery-candidate.service.ts
tests/unit/services/pending-recovery-candidate.service.test.ts
src/domain/pending-recovery-candidate.ts
src/events/shopify-contract-adapter.ts
package.json
the task Completion Report
```

The previous Amendment 001 review is intentionally retained above as the
historical record of the first architect review.

#### Amendment 001 Verification

**A1 — stale empty-cart protection: satisfied**

`refreshResolvedCandidateActivity()` now canonicalises and compares the
incoming activity timestamp against:

```text
candidate.lastActivityAt
    ?? candidate.checkoutCreatedAt
```

before inspecting the empty-cart cancellation branch.

Therefore:

```text
incoming <= existing
    -> stale
    -> no cancellation
    -> no reschedule
    -> no alias/ZSET mutation
```

The focused regression test confirms that a stale `isEmpty: true` cart event
leaves the candidate job, cart alias and shop index intact.

**A2 — cart alias replacement: satisfied**

When duplicate checkout scheduling changes:

```text
cart_old -> cart_new
```

the implementation now removes the previous cart alias before updating the
candidate and installing/refreshing the current aliases.

The focused test proves:

```text
cart_old -> null
cart_new -> same candidate job
job.data.cartToken -> cart_new
```

Existing cancellation cleanup continues to remove the current checkout/cart
aliases and shop-index membership.

**A3 — checkout-lock serialization and re-resolution: satisfied**

`refreshCandidateActivity()` now follows the required flow:

```text
O(1) candidate resolve
    |
    v
authoritative checkoutToken
    |
    v
withCheckoutLock(...)
    |
    v
re-resolve candidate inside the lock
    |
    v
re-check correlation/freshness/state
    |
    v
reschedule / cancel / bounded no-op
```

`cancelCandidateByCart()` follows the same checkout-scoped lock and re-resolution
boundary.

This reuses the existing order/materialization mutex rather than creating a
second lock.

The regression test also simulates candidate disappearance while waiting for
the lock and confirms the operation returns `not-found` rather than mutating
stale state.

**A4 — BullMQ state boundary coverage: satisfied**

Focused tests now explicitly cover:

```text
delayed   -> rescheduled
waiting   -> not-reschedulable
active    -> not-reschedulable
failed    -> not-reschedulable
completed -> not-reschedulable
missing   -> not-found
```

Cart cancellation explicitly supports:

```text
delayed
waiting
```

and rejects unsafe active/terminal states through the bounded
`not-reschedulable` result.

#### Preserved Architecture

The accepted implementation preserves:

```text
tenant-readable candidate job IDs
legacy/new candidate-ID transition
ARCH-003 shop-scoped ZSET indexing
bounded candidate-index TTLs
order-completion tombstones
existing BullMQ queue topology
@modainteract/moda-interact-shared@0.6.0
```

Worker dispatch for `cart.activity` remains correctly deferred to
`ARCH-004-BACKGROUND-002`.

#### Validation Reviewed

Attempt 2 reports:

```text
32 amendment-focused candidate tests passed
55 required focused tests passed
npm run build passed
git diff --check passed
npm test:
  126 passed
  4 skipped
  1 unchanged unrelated baseline failure
```

The remaining full-suite failure is the previously documented
`recovery-routing.service.test.ts` Prisma mock deficiency for
`customerPhone.findMany`; it is outside the files and behavior owned by this
task.

No commit or push was performed.

#### Result

`ARCH-004-BACKGROUND-001` is **Complete**.

Its dependency gate is now satisfied, so:

```text
ARCH-004-BACKGROUND-002
```

is promoted to **Ready**.

