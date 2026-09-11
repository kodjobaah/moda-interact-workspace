---
id: ARCH-010-BACKGROUND-018
architecture_id: ARCH-010
title: Stop Shopify checkout/cart event processing early for frozen subscriptions
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-BACKGROUND-004
  - ARCH-010-BACKGROUND-016
enables:
  - ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-BACKGROUND-018: Stop Shopify checkout/cart event processing early for frozen subscriptions

## Objective

Make `Subscription.status=FROZEN` an **early Shopify-event processing gate** in `moda-shopify-event-worker` so checkout/cart events accepted before or during a Shopify billing freeze do not create/refresh pending candidates, call Shopify abandoned-checkout APIs, mutate recovery business state, or create downstream customer work.

This task is deliberately separate from `ARCH-010-BACKGROUND-017`:

- `BACKGROUND-017` gates recovery/WhatsApp/CommerceAgent/billable business execution generally;
- `BACKGROUND-018` gates the high-volume `checkout-events` / `order-events` processing boundary itself.

The Shopify HTTP ingress in `moda-interact` MUST remain unchanged. It continues to authenticate, validate, enqueue and acknowledge Shopify quickly. Do **not** add a synchronous billing/subscription database lookup to webhook ingress.

## Architecture invariant

After the canonical Shopify event has been dequeued and its tenant has been resolved to durable Moda shop state:

```text
Shop.status != ACTIVE
    -> existing BACKGROUND-004 behaviour

Shop.status = ACTIVE
AND Subscription.status = FROZEN
    -> checkout/cart business-event processing stops early

Shop.status = ACTIVE
AND Subscription.status is executable
    -> existing event behaviour continues
```

A frozen-state no-op is an expected lifecycle outcome, not a retryable worker failure.

## Inspect before editing

Read the actual repository before changing code, including at least:

```text
src/entrypoints/shopify-event.ts
src/workers/checkout.worker.ts
src/workers/orders.worker.ts
src/events/shopify-contract-adapter.ts
src/services/checkout-recovery.service.ts
src/services/pending-recovery-candidate.service.ts
src/services/abandoned-checkout-lookup.service.ts
src/services/effective-billing-policy.service.ts
src/domain/pending-recovery-candidate.ts

tests covering:
  checkout.worker
  orders.worker
  checkout-recovery.service
  pending-recovery-candidate.service
  BACKGROUND-004 inactive-shop gates
  BACKGROUND-017 frozen execution gates

package.json
```

Read actual package scripts before validation. Do not assume script names.

## Do not change the cross-service event contract

The canonical Shopify recovery event already carries tenant identity:

```text
event.tenant.shopId
event.tenant.shopDomain
```

Use the existing contract. Do not add a new Shared schema field merely for this gate.

If a supplied event path cannot identify its durable shop from the current contract, STOP and return that exact path to `moda_architect`.

## Required hot-path implementation shape

Do not introduce an additional database lookup when an existing first shop lookup can carry the frozen-state selection.

Where a handler already reads `Shop`, extend that same query to select the minimum fields required:

```text
Shop.id
Shop.status
Subscription.status
```

Do not load BillingPlan, counters, BillingPeriod, settings unrelated to the existing handler, or call the Partner API merely to answer this gate.

### checkout.created

The current first durable lookup occurs in `PendingRecoveryCandidateService.scheduleFromCheckoutCreated()`.

Extend that existing lookup. For:

```text
Shop.status = ACTIVE
Subscription.status = FROZEN
```

return a stable typed terminal outcome such as:

```text
discarded-subscription-frozen
```

before any of the following happen:

- BullMQ delayed candidate creation;
- existing candidate refresh/update;
- pending-candidate Redis index creation/update;
- recovery delay scheduling;
- Shopify abandoned-checkout lookup;
- CheckoutRecovery creation/mutation.

Do not throw. Do not retry the Shopify event because the subscription is frozen.

### checkout.updated

`CheckoutRecoveryService.handleCheckoutUpdatedContract()` already resolves `Shop` by `shopDomain` before pending-candidate or recovery work.

Extend that same lookup to include current `Shop.status` and `Subscription.status`.

For FROZEN:

- do not refresh/reschedule a pending candidate;
- do not perform abandoned-checkout provider lookup;
- do not update CheckoutRecovery basket/content fields;
- return a stable ignored/discarded frozen outcome.

### cart.activity

This path receives durable `event.shopId` from the canonical event but currently proceeds directly into pending-candidate Redis state.

Add one minimal durable shop/subscription lookup by `event.shopId` before candidate/index access.

For FROZEN:

- do not resolve/refresh/cancel candidate state from cart activity;
- do not create/update Redis candidate indexes;
- return a stable ignored/discarded frozen outcome.

This single lookup is permitted because the path otherwise has no durable execution-state check. Do not add another lookup later in the same path solely for this gate.

## `order.completed` safety exception

Do **not** treat `order.completed` exactly like checkout/cart activity.

An order completed while Moda is frozen can invalidate a pending or existing abandoned-cart recovery. If the event is dropped completely, the merchant could later unfreeze and Moda could resume a recovery for a checkout that actually became an order during the freeze.

For an ACTIVE shop with FROZEN subscription, `order.completed` may perform only bounded **terminal safety bookkeeping**:

1. resolve existing pending-candidate correlation;
2. cancel/remove the matching pending candidate if one already exists;
3. write the existing order-processed tombstone/correlation required to prevent in-flight materialization;
4. if an existing CheckoutRecovery matches, transition that existing recovery to `COMPLETED` using the current idempotent order-completion path;
5. write the existing status-history entry for that terminal transition.

It MUST NOT:

- create a new pending candidate;
- create a new CheckoutRecovery;
- create a customer;
- create/advance a conversation;
- reserve any credit;
- invoke CommerceAgent;
- send WhatsApp;
- create a new recovery/top-up billing UsageEvent;
- schedule new recovery/business work.

If no existing candidate or recovery can be correlated, discard the order for Moda recovery purposes exactly as the current architecture does. Do not create durable order business state merely because the subscription is frozen.

## Race semantics

Correctness is based on durable subscription state at execution time.

Example:

```text
checkout.created accepted and queued while ACTIVE
        ↓
Shopify freeze reconciled
Subscription.status = FROZEN
        ↓
queued checkout job starts
        ↓
BACKGROUND-018 gate
        ↓
terminal frozen no-op
```

Do not purge every queue and do not require a distributed lock between subscription reconciliation and Shopify event workers.

A job that has already passed the durable gate before the FROZEN transaction commits may finish only according to the existing idempotent/business gates in BACKGROUND-017. Do not invent cross-process global serialization in this task.

## Unfreeze behaviour

Do not replay discarded raw checkout/cart events merely because Shopify later unfreezes.

After BACKGROUND-016 restores an executable subscription:

- new Shopify events process normally;
- already-existing pending/recovery records resume only through their normal ARCH-010 reconciliation/resume paths;
- old discarded checkout/cart webhooks are not reconstructed from Redis.

Before any later customer-facing recovery action, the existing architecture must still revalidate current Shopify checkout/order state. Do not weaken that revalidation.

## Performance requirement

This worker is part of the high-volume Shopify background path.

The task MUST:

- avoid Partner API calls for the gate;
- reuse an existing shop query where one already exists;
- add at most one minimal durable lookup to a path that currently has none (`cart.activity`);
- avoid loading billing counters/period history merely to classify FROZEN;
- return before provider lookups and Redis candidate churn for frozen checkout/cart events.

Do not add a Redis cache of subscription execution state in this task. PostgreSQL remains the correctness source; a cache/invalidation design would be a separate architecture decision.

## Observability

If new logging is required, use the shared structured logger.

A bounded log may include:

```text
reason = subscription_frozen
eventType
shopId or canonical internal shop identifier
```

Do not log Shopify/customer payloads, phone/email data, tokens or secrets.

Do not create duplicate generic BullMQ metrics. Framework/approved worker telemetry remains authoritative for generic queue processing.

## Required tests

At minimum prove:

1. executable checkout.created still schedules/refreshed the normal pending candidate;
2. FROZEN checkout.created creates no BullMQ pending-candidate job;
3. FROZEN checkout.created creates/updates no candidate Redis indexes;
4. FROZEN checkout.updated does not refresh a candidate;
5. FROZEN checkout.updated does not call abandoned-checkout Shopify lookup;
6. FROZEN checkout.updated does not mutate an existing CheckoutRecovery;
7. FROZEN cart.activity performs no candidate/index mutation;
8. frozen checkout/cart outcomes complete the BullMQ job successfully rather than retrying;
9. an event queued before freeze but executed after the FROZEN commit is gated;
10. order.completed for FROZEN cancels an already-existing pending candidate safely;
11. order.completed for FROZEN can mark an already-existing non-terminal recovery COMPLETED;
12. order.completed for FROZEN creates no new recovery/customer/conversation/outbound message/credit reservation/UsageEvent;
13. unrelated order.completed with no candidate/recovery remains discarded and creates no new business record;
14. BACKGROUND-004 UNINSTALLED/SUSPENDED semantics remain unchanged;
15. BACKGROUND-017 recovery/WhatsApp/CommerceAgent frozen gates remain unchanged;
16. after Subscription returns to ACTIVE/TRIALING, new checkout/cart events use the normal path again;
17. no Partner API request is made by the early event gate.

Where dependencies are mocked, explicitly assert forbidden dependencies were not called.

## Non-goals

Do not:

- change Shopify webhook ingress/acknowledgement;
- prevent Shopify from sending webhooks;
- purge all existing BullMQ jobs on freeze;
- redesign shop identification;
- add a new cross-repository event field;
- implement freeze detection/reconciliation (BACKGROUND-015/016);
- implement WhatsApp/CommerceAgent gates (BACKGROUND-017);
- change credit ordering/allowances;
- change cancellation semantics;
- replay raw checkout/cart events on unfreeze;
- modify another repository.

## Validation

Run focused checkout/order worker and service tests, then the actual repository-declared build/typecheck/unit validations required by its `package.json`, plus:

```text
git diff --check
```

Do not invent a validation command that the repository does not provide.

## Stop conditions

STOP and return to `moda_architect` if:

- a relevant Shopify event does not carry enough tenant identity to resolve durable Shop state;
- early gating would require a synchronous Partner API call;
- the only proposed implementation adds multiple new database reads per high-volume event despite an existing shop lookup;
- preserving the order-completion safety exception would require creating new unrelated durable order state;
- an integrated task materially changes the `checkout-events` / `order-events` ownership boundary.

## Completion Report

### Status
Not started.
