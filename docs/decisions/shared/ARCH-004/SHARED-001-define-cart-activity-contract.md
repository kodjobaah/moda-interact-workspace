---
id: ARCH-004-SHARED-001
architecture_id: ARCH-004
title: Define canonical cart activity recovery event
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 10
executor: copilot
claimed_at: 2026-09-05T13:56:08Z
attempt: 1
depends_on: []
enables:
  - ARCH-004-SHARED-002
created: 2026-09-05
updated: 2026-09-05
---

# Define canonical cart activity recovery event

## Objective

Extend the canonical Shopify v2 recovery-event contract with a minimal,
PII-safe cart activity event that can correlate a Shopify cart to an existing
pending recovery candidate.

## Architecture

```text
docs/architecture/ARCH-004-cart-activity-recovery-rescheduling.md
```

## Current contract

The v2 discriminated union currently contains:

```text
checkout.created
checkout.updated
order.completed
```

ARCH-004 adds:

```text
cart.activity
```

without creating a new queue.

## Required contract

Add:

```ts
SHOPIFY_RECOVERY_EVENT_TYPES_V2.CART_ACTIVITY = "cart.activity"
```

Add a strict payload equivalent to:

```ts
{
  cartToken: string;
  isEmpty: boolean | null;
}
```

`isEmpty` semantics:

```text
true  = provider payload proves the cart contains no items
false = provider payload proves it contains items
null  = provider payload does not safely establish emptiness
```

Add:

```text
ShopifyCartActivityEventV2Schema
ShopifyCartActivityEventV2
isCartActivityEventV2(...)
```

and include it in:

```text
ShopifyRecoveryEventV2Schema
ShopifyRecoveryEventV2
```

## Queue contract

Extend:

```text
SHOPIFY_WEBHOOK_QUEUE_CONTRACTS
```

with:

```text
CART_ACTIVITY_EVENTS
  queueName: "checkout-events"
  jobName:   "cart-activity"
```

Do not create `cart-events`.

## Ordering key

Add a deterministic cart activity ordering/correlation helper using:

```text
shopId + cartToken
```

The representation must be unambiguous and tested.

It must not include customer PII.

## Compatibility

This is an additive v2 union extension.

Older shared-package consumers will reject `cart.activity`, so publication must
remain gated until the new shared package release is adopted by Background.

Do not silently loosen `.strict()` schema behaviour.

## Out of scope

- Shopify raw webhook normalization;
- Redis candidate lookup;
- recovery scheduling;
- UI changes;
- package publication.

## Acceptance criteria

 [x] `cart.activity` exists in canonical v2 event types.
 [x] strict payload validates `cartToken`.
 [x] `isEmpty` supports true/false/null only.
 [x] event participates in the canonical discriminated union.
 [x] type guard exists.
 [x] existing v2 checkout/order events remain valid.
 [x] queue contract uses existing `checkout-events`.
 [x] deterministic cart ordering key is tested.
 [x] no PII/cart contents are added to the contract.
 [x] unit tests/typecheck/build pass.
 [x] `git diff --check` passes.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-shared/src/shopify/constants.ts`
- `moda-interact-shared/src/shopify/queue-contracts.ts`
- `moda-interact-shared/src/shopify/index.ts`
- `moda-interact-shared/src/shopify/v2/cart-activity.schema.ts`
- `moda-interact-shared/src/shopify/v2/recovery-event.schema.ts`
- `moda-interact-shared/src/shopify/v2/recovery-event.test.ts`

### Work Completed

- Added the strict PII-safe `cart.activity` payload with `cartToken` and
  nullable boolean `isEmpty` semantics.
- Added the cart activity event schema/type, discriminated-union membership,
  and `isCartActivityEventV2` type guard.
- Added `CART_ACTIVITY_EVENTS` on the existing `checkout-events` queue with
  job name `cart-activity`; no new queue was introduced.
- Added a deterministic length-prefixed cart ordering key using `shopId` and
  `cartToken`, including delimiter-collision coverage.
- Preserved strict schemas and existing checkout/order v2 compatibility.

### Validation Results

- Focused v2 recovery-event tests: 14 passed.
- Full shared-package tests: 66 passed, 1 skipped because `TEST_REDIS_URL` is
  not configured for the live BullMQ propagation test.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `git diff --check`: passed.
- Changed-file editor diagnostics: no errors.

### Deviations

None.

### Assumptions

The length-prefixed ordering key is used as the canonical event ordering key;
the existing Background Redis index key format remains owned by Background.

### Unresolved Issues

None.

### Architectural Concerns

None.

### Git / VCS

Implementation ready for developer commit/push. Repository agent did not commit
or push.

## Architect Review

### Review Status

Accepted

### Review Notes

Architect reviewed the supplied implementation archive directly.

Accepted contract:

```text
eventType: cart.activity

payload:
  cartToken: string
  isEmpty: boolean | null
```

The event participates in the strict v2 Shopify recovery-event discriminated
union and exposes:

```text
ShopifyCartActivityEventV2Schema
ShopifyCartActivityEventV2
isCartActivityEventV2(...)
```

The queue contract correctly reuses:

```text
queueName: checkout-events
jobName:   cart-activity
```

No fifth BullMQ queue is introduced.

The cart activity ordering key is deterministic, tenant-scoped and
length-prefixed:

```text
cart:<shopIdLength>:<shopId>:<cartTokenLength>:<cartToken>
```

so delimiter-containing identifiers cannot collide through simple
concatenation.

The payload remains strict and PII-minimal. Cart contents and customer identity
are not added.

Existing checkout/order v2 schemas and the v1 transition parser remain covered
by tests.

### Validation Reviewed

Implementing-agent evidence:

- focused v2 recovery-event tests: 14 passed;
- full shared-package tests: 66 passed;
- 1 Redis-dependent integration test skipped because `TEST_REDIS_URL` is not
  configured;
- typecheck: passed;
- build: passed;
- `git diff --check`: passed.

### Architecture Conformance

Conforms.

### Result

`ARCH-004-SHARED-001` is Complete.

`ARCH-004-SHARED-002` may advance to Ready for publication of the accepted
shared contract.

