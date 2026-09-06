# ARCH-004: Correlated cart activity recovery rescheduling

## Purpose

ARCH-004 changes pending recovery from a checkout-creation timer into a true
**inactivity timer**.

A shopper who is still changing the cart or checkout has not abandoned it.

The governing rule becomes:

```text
scheduledFor = lastActivityAt + recoveryDelay
```

## Activity that can move the clock

For an existing pending candidate:

```text
checkout.created
checkout.updated
cart.create
cart.update
```

may contribute to the latest relevant activity time.

A cart event does not create a recovery candidate by itself.

## Deterministic equivalent-checkout rule

A cart may affect a pending checkout only when it can be correlated through the
existing tenant-scoped candidate cart index:

```text
shopId + cartToken
        |
        v
pending candidate
        |
        v
authoritative checkoutToken
```

ARCH-004 explicitly does **not** correlate using:

```text
email
phone
customer name
URL inference
queue scans
Redis keyspace scans
cross-tenant guessing
```

## Monotonic activity clock

Out-of-order or duplicate Shopify events must not move recovery backwards.

Conceptually:

```text
effectiveLastActivityAt =
  max(existingLastActivityAt, incomingActivityAt)
```

Then:

```text
dueAt = effectiveLastActivityAt + recoveryDelay
```

## Rescheduling contract

For a safely delayed candidate, the same logical candidate is updated:

```text
candidate.lastActivityAt
BullMQ delayed schedule
shop-scoped ZSET score
candidate correlation TTLs
```

A cart/checkout activity event should not create duplicate pending candidates.

## Empty cart

Canonical cart activity carries a tri-state emptiness decision:

```text
true   -> confirmed empty: cancel pending candidate
false  -> active cart: reschedule
null   -> unknown: treat as activity, do not guess cancellation
```

## Queue topology

No new cart queue is introduced.

Cart recovery activity uses:

```text
queue:   checkout-events
jobName: cart-activity
```

This preserves the existing queue topology and ARCH-003 observability model.

## Checkout update compatibility

Before ARCH-004, a checkout update could be ignored before
`CheckoutRecovery` materialisation.

After ARCH-004:

```text
checkout.updated
   |
   +-- matching pending candidate
   |      -> advance inactivity clock / reschedule
   |
   +-- no candidate but existing CheckoutRecovery
   |      -> preserve existing refresh behaviour
   |
   +-- neither
          -> discard
```

Existing order-completion cancellation remains unchanged.

## Merchant UI effect

Because schedule can move after checkout creation, the operational timestamp is
no longer accurately described by:

```text
CHECKOUT CREATED
```

The pending-recovery UI should use:

```text
LAST ACTIVITY
```

with:

```text
lastActivityAt
scheduledFor
status
```

while preserving sensitive-field redaction.

## Shared contract

ARCH-004 adds canonical:

```text
cart.activity
```

with a minimal payload:

```text
cartToken
isEmpty
```

The shared contract continues to carry tenant identity and canonical event
timestamps in the envelope.

## Task ownership

Implementation is distributed under:

```text
docs/decisions/shared/ARCH-004/
docs/decisions/shopify/ARCH-004/
docs/decisions/background/ARCH-004/
docs/decisions/system-test/ARCH-004/
```

The task files remain authoritative for current execution/review state.
