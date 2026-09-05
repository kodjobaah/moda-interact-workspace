---
id: ARCH-004
title: Correlated cart activity recovery rescheduling
status: in_progress
coordinator: moda_architect
created: 2026-09-05
updated: 2026-09-05
---

# ARCH-004: Correlated cart activity recovery rescheduling

## Status

In Progress.

Immediate executable task:

```text
ARCH-004-SHARED-001
```

## Problem

The current recovery candidate lifecycle is primarily checkout-driven.

The Shopify application is already subscribed to:

```text
carts/create
carts/update
checkouts/create
checkouts/update
orders/create
```

but the current Shopify ingress deliberately ignores cart topics.

The Background candidate implementation already maintains deterministic O(1)
correlation aliases for:

```text
shopId + checkoutToken
shopId + cartToken
```

and an active pending-recovery candidate can already be rescheduled with
BullMQ `changeDelay()` while it remains delayed.

The current historical ARCH-001 rule for `checkout.updated` says:

```text
No CheckoutRecovery means the update is irrelevant before recovery exists.
```

That rule no longer expresses the desired product behaviour.

A customer who is still changing the basket has not abandoned it.

The recovery timer should therefore represent:

```text
time since last relevant correlated cart / checkout activity
```

rather than:

```text
time since checkout creation only
```

## Architecture decision

ARCH-004 introduces a unified pending-recovery inactivity clock.

```text
checkout.created
      |
      v
create candidate
lastActivityAt = activity timestamp
scheduledFor   = lastActivityAt + recoveryDelay

checkout.updated ----------------------+
                                       |
cart.create / cart.update              |
      |                                |
      v                                v
deterministic candidate correlation
      |
      +---- no candidate ----> no-op
      |
      +---- matching candidate
                |
                +---- non-empty activity
                |       |
                |       v
                |   advance lastActivityAt
                |   reschedule candidate
                |
                +---- confirmed empty cart
                        |
                        v
                    cancel candidate
```

Order completion continues to cancel/suppress recovery through the existing
order-correlation path.

## Core invariant

A recovery may become eligible only after the configured recovery delay has
elapsed since the latest relevant activity known for that pending candidate.

Conceptually:

```text
scheduledFor = lastActivityAt + recoveryDelay
```

The timer is an inactivity timer.

## What counts as relevant activity

For a pending candidate:

```text
checkout.created
checkout.updated
cart.create
cart.update
```

can advance the activity clock.

Cart activity is relevant only if its cart token deterministically resolves to
an existing pending candidate for the same internal shop.

A cart event MUST NOT create a recovery candidate by itself.

## Deterministic "equivalent checkout" rule

The equivalent checkout for a cart is resolved only through the existing
candidate cart index:

```text
pending-recovery:index:cart:<shopId>:<cartToken>
```

That index points to the pending candidate job, whose candidate data carries
the authoritative checkout token.

Allowed:

```text
shopId + cartToken -> candidate job -> checkoutToken
```

Not allowed:

```text
email matching
phone matching
customer-name matching
customer-id guessing unless explicitly present in a future canonical contract
queue scans
Redis keyspace scans
URL inference
cross-tenant inference
```

If no indexed candidate exists, the cart event is a no-op for pending recovery.

## Event time

The canonical activity timestamp is derived from the canonical Shopify event
envelope.

For checkout/cart activity:

```text
activityAt = occurredAt ?? receivedAt
```

For checkout creation, provider checkout creation time may be retained for
display/audit, but the pending recovery inactivity clock uses the canonical
activity timestamp.

The implementation MUST be monotonic:

```text
effectiveLastActivityAt =
  max(existingLastActivityAt, incomingActivityAt)
```

An older or duplicate event must never move the recovery schedule backwards.

## Scheduling semantics

For a safely reschedulable delayed candidate:

```text
dueAt          = effectiveLastActivityAt + recoveryDelay
remainingDelay = max(0, dueAt - now)
```

Update:

```text
candidate.lastActivityAt
BullMQ job data
BullMQ delayed schedule
pending-recovery:index:shop:<shopId> ZSET score
candidate correlation TTLs
```

as one coherent logical operation.

Do not blindly schedule `now + recoveryDelay` when the event carries an earlier
authoritative activity timestamp.

## Candidate state boundary

Normal ARCH-004 rescheduling applies while a candidate remains safely
reschedulable in BullMQ's delayed state.

The implementation must explicitly define and test behaviour when the candidate
has already transitioned to:

```text
waiting
active
missing
completed
failed
```

Do not force unsupported BullMQ state mutation.

Where the existing checkout-scoped candidate/order lock can safely serialize
candidate mutation with materialization, reuse it.

A late event must produce an explicit bounded outcome such as:

```text
rescheduled
stale
not-found
not-reschedulable
cancelled
```

rather than silently guessing.

## Empty cart policy

A cart webhook may only cancel a candidate when the Shopify payload provides
enough information to establish that the cart is empty.

Canonical cart activity therefore carries:

```text
isEmpty: true | false | null
```

Semantics:

```text
true  -> cancel the matched pending candidate
false -> activity; reschedule
null  -> emptiness unknown; treat as activity, do not infer cancellation
```

Do not publish line-item/customer PII merely to support this decision.

## Queue decision

ARCH-004 does NOT add a fifth BullMQ queue.

Cart activity belongs to the existing recovery-relevant Shopify event lane:

```text
queue:   checkout-events
jobName: cart-activity
```

This avoids unnecessary queue topology, Admin UI, telemetry and deployment
changes while keeping cart/checkout recovery activity in the same worker
process.

The existing operational queue set remains:

```text
checkout-events
order-events
pending-recovery-candidates
whatsapp-events
```

## Shared contract decision

The canonical v2 Shopify recovery-event contract is extended additively with:

```text
eventType: cart.activity
payload:
  cartToken: string
  isEmpty: boolean | null
```

The envelope continues to provide:

```text
tenant.shopId
tenant.shopDomain
providerTopic
occurredAt
receivedAt
deliveryId
eventId
traceId
orderingKey
```

No cart contents, email, phone number or customer identity are required.

The queue contract is extended with:

```text
CART_ACTIVITY_EVENTS:
  queueName: checkout-events
  jobName: cart-activity
```

Because existing older consumers reject unknown discriminated-union event
types, the producer MUST NOT begin publishing `cart.activity` until the shared
contract release has been adopted by the Background consumer.

## Checkout update compatibility

ARCH-004 supersedes one narrow ARCH-001 rule.

Before ARCH-004:

```text
checkout.updated + no CheckoutRecovery -> discard
```

After ARCH-004:

```text
checkout.updated
    |
    +-- matching pending candidate -> advance inactivity clock / reschedule
    |
    +-- no pending candidate
           |
           +-- existing CheckoutRecovery -> preserve ARCH-001 refresh behaviour
           |
           +-- neither -> discard
```

The existing post-materialization recovery refresh behaviour is preserved.

## Merchant UI

The pending-recovery panel currently labels its first timestamp:

```text
CHECKOUT CREATED
```

That becomes inaccurate once checkout/cart activity can move the recovery
schedule.

The approved label is:

```text
LAST ACTIVITY
```

The merchant-safe DTO should expose:

```text
lastActivityAt
scheduledFor
status
```

Legacy pending jobs that predate `lastActivityAt` may fall back to
`checkoutCreatedAt` for display only during rolling deployment.

The UI must continue to hide:

```text
checkoutToken
cartToken
abandonedCheckoutUrl
Redis keys
raw BullMQ data
```

## Non-goals

ARCH-004 does not:

- create recovery candidates from cart events alone;
- add a new BullMQ queue;
- change the configured recovery delay model;
- infer candidate identity from PII;
- persist every cart mutation in PostgreSQL;
- reopen terminal `CheckoutRecovery` records;
- send a second recovery message;
- redesign the merchant Usage page;
- alter order-completion cancellation semantics;
- expose raw cart contents in the merchant UI.

## Data/storage impact

No PostgreSQL migration is expected.

Ephemeral candidate data gains:

```text
lastActivityAt
```

The existing:

```text
pending-recovery:index:checkout:...
pending-recovery:index:cart:...
pending-recovery:index:shop:...
```

structures remain authoritative for pending-candidate correlation/listing.

## Task graph

```text
ARCH-004-SHARED-001
        |
        v
ARCH-004-SHARED-002
      /            \
     v              v
SHOPIFY-001     BACKGROUND-001
                     |
                     v
                BACKGROUND-002
                     |
                     v
                SHOPIFY-002
                     |
                     v
              SYSTEM-TEST-001
```

`SHOPIFY-001` and `BACKGROUND-001` may execute in parallel after the shared
package release.

`SYSTEM-TEST-001` also depends on the Shopify producer path, even though the
diagram emphasises the candidate/UI chain.

## Tasks

```text
ARCH-004-SHARED-001
  Extend canonical v2 contract with cart.activity

ARCH-004-SHARED-002
  Publish the shared cart-activity contract release

ARCH-004-SHOPIFY-001
  Publish carts/create and carts/update as canonical cart.activity events

ARCH-004-BACKGROUND-001
  Add monotonic pending-candidate activity clock and cart correlation mutation

ARCH-004-BACKGROUND-002
  Reschedule pending recovery from checkout/cart activity

ARCH-004-SHOPIFY-002
  Show Last Activity in merchant Pending recoveries

ARCH-004-SYSTEM-TEST-001
  Verify correlated cart activity resets the recovery inactivity clock
```

## Architecture acceptance

ARCH-004 is Complete only when:

- canonical cart activity is published and consumed;
- a deterministically matched cart event advances the pending candidate clock;
- an out-of-order older event cannot move the schedule backwards;
- an unmatched cart event does not touch another checkout;
- confirmed empty cart cancels the candidate;
- checkout.updated reschedules a pending candidate while preserving existing
  post-materialization refresh behaviour;
- merchant UI shows `LAST ACTIVITY`;
- the pending candidate's shop-scoped index score tracks the new due time;
- no new BullMQ queue is introduced;
- end-to-end evidence proves the behaviour.
