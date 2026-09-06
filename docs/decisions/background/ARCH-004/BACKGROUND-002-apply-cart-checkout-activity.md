---
id: ARCH-004-BACKGROUND-002
architecture_id: ARCH-004
title: Apply checkout and cart activity to pending recovery
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 40
executor: copilot
claimed_at: 2026-09-05T19:00:00Z
attempt: 1
depends_on:
  - ARCH-004-BACKGROUND-001
enables:
  - ARCH-004-SHOPIFY-002
  - ARCH-004-SYSTEM-TEST-001
created: 2026-09-05
updated: 2026-09-05T19:15:00Z
---

# Apply checkout and cart activity to pending recovery

## Objective

Consume canonical checkout/cart activity and reset the pending-recovery
inactivity clock when a deterministic candidate exists.

## Checkout update behaviour

This task intentionally supersedes the pre-recovery portion of
`ARCH-001-BACKGROUND-006`.

New flow:

```text
checkout.updated
    |
    v
resolve shop
    |
    v
matching pending candidate by checkoutToken?
    |
   yes -----------------> refresh candidate activity / reschedule
    |
    no
    |
    v
existing CheckoutRecovery?
    |
   yes -----------------> preserve existing ARCH-001 current-Shopify refresh
    |
    no -----------------> discard
```

Do not remove the existing post-materialization recovery refresh path.

## Cart activity behaviour

Add the `cart-activity` job to the existing checkout worker.

Flow:

```text
cart.activity
    |
    v
shopId + cartToken candidate lookup
    |
    +-- none -> no-op
    |
    +-- matched
           |
           +-- isEmpty === true
           |       -> cancel pending candidate
           |
           +-- isEmpty === false/null
                   -> advance activity clock / reschedule
```

A cart event never creates a candidate.

## Activity timestamp

Map canonical event envelope time to the service input:

```text
activityAt = event.occurredAt ?? event.receivedAt
```

Do not derive activity time from worker processing time unless the canonical
event itself lacks both fields, which should be rejected by the shared schema.

## Correlation

Cart activity uses only:

```text
event.tenant.shopId
event.payload.cartToken
```

plus the existing candidate cart index.

No PII correlation.

## Worker topology

Use the existing:

```text
checkout-events
```

worker.

Add:

```text
cart-activity
```

to its accepted job names/dispatch.

No fifth queue or worker process.

Queue-performance telemetry from ARCH-003-BACKGROUND-003 should automatically
continue to report this work under the existing queue, with the bounded
`bullmq.job.name` value for cart activity.

## Empty cart

Only:

```text
isEmpty === true
```

cancels.

`null` must not be interpreted as empty.

## Existing order behaviour

Do not change order cancellation/tombstone/checkout lock behaviour.

## Acceptance criteria

- [x] checkout.updated reschedules a matching pending candidate.
- [x] checkout.updated with no pending candidate still refreshes an existing
      active CheckoutRecovery exactly as before.
- [x] checkout.updated with neither candidate nor recovery is discarded.
- [x] cart.activity with matched candidate reschedules it.
- [x] unmatched cart activity is a bounded no-op.
- [x] confirmed empty matched cart cancels candidate.
- [x] unknown emptiness does not cancel.
- [x] older activity does not move schedule backwards.
- [x] no new BullMQ queue exists.
- [x] no Shopify API lookup is made merely to process a pending cart activity.
- [x] post-materialization recovery refresh tests remain green.
- [x] order-correlation tests remain green.
- [x] focused/full tests, build/typecheck/diff checks pass subject to documented
      baseline.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-background/src/events/shopify-contract-adapter.ts`
- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/src/services/pending-recovery-candidate.service.ts`
- `moda-interact-background/src/workers/checkout.worker.ts`
- `moda-interact-background/tests/unit/events/shopify-contract-adapter.test.ts`
- `moda-interact-background/tests/unit/observability/worker-metrics.test.ts`
- `moda-interact-background/tests/unit/services/checkout-refresh.test.ts`

### Work Completed

- Added canonical `activityAt` mapping for `checkout.updated` and `cart.activity`.
- Added cart activity contract mapping using only `tenant.shopId`, cart token,
    emptiness, and canonical envelope time.
- Added `cart-activity` to the existing `checkout-events` worker dispatch and
    bounded worker telemetry job names.
- Made checkout updates refresh a matching pending candidate before falling
    back to the existing durable `CheckoutRecovery` refresh path.
- Added cart activity handling that delegates to O(1) candidate correlation and
    never performs a Shopify lookup or creates a candidate.

### Validation Results

- Focused integration and regression tests: 72 passed.
- `npm run build`: passed.
- `npm test`: 129 passed, 4 skipped, 1 unrelated baseline failure in
    `tests/unit/services/recovery-routing.service.test.ts` because its Prisma
    mock does not provide `customerPhone.findMany`.
- `git diff --check`: passed.
- No commit or push performed.

### Deviations

None. Pending-candidate mutation remains owned by `BACKGROUND-001`; this task
only dispatches and consumes its service API.

### Assumptions

- A checkout update that resolves to a pending candidate returns a bounded
    pending outcome and does not also refresh a durable recovery.

### Unresolved Issues

- The full suite retains the unrelated `customerPhone.findMany` Prisma-mock
    failure documented above.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Source Review

The architect reviewed the supplied `moda-interact-background` workspace
directly, including:

```text
src/events/shopify-contract-adapter.ts
src/services/checkout-recovery.service.ts
src/services/pending-recovery-candidate.service.ts
src/workers/checkout.worker.ts
tests/unit/events/shopify-contract-adapter.test.ts
tests/unit/services/checkout-refresh.test.ts
tests/unit/services/pending-recovery-candidate.service.test.ts
tests/unit/observability/worker-metrics.test.ts
package.json
```

### Architecture Verification

**Canonical timestamps — accepted**

The contract adapter maps activity time as:

```text
activityAt = event.occurredAt ?? event.receivedAt
```

for both `checkout.updated` and `cart.activity`.

The Background service does not substitute worker-processing time for a valid
canonical event timestamp.

**Checkout update precedence — accepted**

`handleCheckoutUpdatedContract()` now follows:

```text
resolve Shop
    |
    v
refreshCandidateActivity(shopId + checkoutToken)
    |
    +-- matching pending candidate
    |      -> return bounded pending outcome
    |      -> no Shopify lookup
    |
    +-- not-found
           -> preserve existing CheckoutRecovery refresh flow
```

This preserves the post-materialization ARCH-001 behavior while allowing a
pre-materialization checkout update to reset the candidate inactivity clock.

A pending-candidate result such as `stale` or `not-reschedulable` does not fall
through into durable recovery refresh, preserving pending-candidate precedence.

**Cart activity — accepted**

`handleCartActivityContract()` delegates only:

```text
shopId
cartToken
activityAt
isEmpty
```

to the accepted BACKGROUND-001 candidate API.

It does not:

```text
perform Shopify lookup
create CheckoutRecovery
create a pending candidate
infer by email/phone/customer data
scan BullMQ
scan Redis keyspace
```

Candidate correlation therefore remains deterministic and tenant-scoped.

**Empty / unknown / stale semantics — accepted**

The accepted BACKGROUND-001 service provides:

```text
isEmpty === true   -> cancel only when the activity is newer and state is safe
isEmpty === false  -> reschedule when delayed
isEmpty === null   -> activity only; never inferred as empty
older activity     -> stale; no backwards schedule mutation
```

BACKGROUND-002 correctly routes canonical inputs into those semantics.

**Worker topology — accepted**

The existing `checkout-events` worker now accepts:

```text
checkout-created
checkout-updated
cart-activity
```

using canonical shared queue contracts.

No new `cart-events` queue or fifth Shopify worker is introduced.

`cart-activity` is also included in the bounded worker metric job-name set, so
ARCH-003 operational telemetry remains on the existing checkout queue.

**Shared dependency — accepted**

The Background repository consumes:

```text
@modainteract/moda-interact-shared@0.6.0
```

which contains the accepted ARCH-004 cart activity contract.

### Validation Reviewed

The implementation report records:

```text
72 focused tests passed
npm run build passed
git diff --check passed

full suite:
129 passed
4 skipped
1 unchanged unrelated baseline failure
```

The remaining full-suite failure is the previously documented
`recovery-routing.service.test.ts` Prisma mock deficiency for
`customerPhone.findMany`; it is outside this task's changed behavior.

No commit or push was performed.

### Result

`ARCH-004-BACKGROUND-002` is **Complete**.

Its completion satisfies the sole dependency for:

```text
ARCH-004-SHOPIFY-002
```

so `ARCH-004-SHOPIFY-002` is promoted to **Ready**.

`ARCH-004-SYSTEM-TEST-001` remains **Pending** until
`ARCH-004-SHOPIFY-002` is architect-accepted.
