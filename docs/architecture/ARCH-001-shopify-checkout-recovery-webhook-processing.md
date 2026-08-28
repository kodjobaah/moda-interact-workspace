---
id: ARCH-001
title: Shopify checkout recovery webhook processing
status: agreed
coordinator: moda_architect
created: 2026-08-28
updated: 2026-08-28
---

# ARCH-001: Shopify Checkout Recovery Webhook Processing

## Status

**Agreed**

This document defines the high-level architecture for Shopify checkout and order webhooks used by Moda Interact's checkout-recovery workflow.

The architecture has been reviewed and implementation tasks are now defined below.

---

## Problem

Moda Interact receives Shopify checkout and order activity, but it does not need to model normal Shopify commerce.

Moda only cares about a checkout when:

1. it may become an abandoned-checkout recovery;
2. it already has a `CheckoutRecovery`;
3. an order cancels a pending recovery;
4. an order completes an existing recovery.

Normal Shopify checkout/order activity should be discarded.

The architecture therefore needs a small temporary representation of a possible recovery, while keeping durable PostgreSQL state only for actual `CheckoutRecovery` records.

---

## Core Domain Model

Moda has two checkout-recovery states.

```text
PendingRecoveryCandidate
    temporary
    Redis / BullMQ

CheckoutRecovery
    durable
    PostgreSQL
```

There is no general durable Shopify checkout model in ARCH-001.

---

## Core Principle

A pending recovery candidate does **not** contain the checkout basket.

Moda does not need to retain:

```text
customer
line items
totals
currency
addresses
discounts
checkout basket snapshot
```

while waiting to determine whether a checkout becomes abandoned.

When the recovery delay expires, Moda queries Shopify for the current abandoned-checkout information.

Only then is `CheckoutRecovery` populated in PostgreSQL.

```text
checkout created
      |
      v
PendingRecoveryCandidate
      |
      | recovery delay
      v
query Shopify
      |
      +---- not recoverable ----> discard
      |
      v
create CheckoutRecovery
with current Shopify data
```

---

## Goals

ARCH-001 must:

- keep Shopify webhook ingress small and fast;
- avoid PostgreSQL writes for ordinary Shopify commerce activity;
- use Redis/BullMQ for pending recovery candidates;
- retain only the minimum information required to identify/correlate a pending checkout;
- fetch current checkout information from Shopify only when required;
- create `CheckoutRecovery` only when a checkout actually enters recovery;
- cancel pending recovery when the checkout completes normally;
- discard unrelated orders;
- discard checkout updates when no `CheckoutRecovery` exists;
- refresh an existing recovery when the customer changes the recovered checkout;
- complete or attribute an existing recovery when the customer places an order;
- use a single canonical cross-service event contract;
- tolerate duplicate and concurrent asynchronous processing.

---

## Non-Goals

ARCH-001 does not:

- persist every Shopify checkout;
- persist every Shopify order;
- keep pre-recovery basket history;
- keep pre-recovery line-item history;
- create a general `CheckoutState` table;
- retain unrelated completed orders;
- redesign the WhatsApp conversation flow;
- redesign CommerceAgent;
- redesign billing;
- handle repeat abandonment after a customer edits an existing recovered checkout;
- implement checkout deletion handling.

### Checkout deletion

A future Shopify checkout-deletion flow is expected but is intentionally outside ARCH-001.

When implemented, that flow will need to determine whether deletion should:

- cancel a pending recovery candidate;
- close or invalidate an existing `CheckoutRecovery`;
- affect downstream messaging or conversation state.

That behaviour will be designed in a later architecture iteration.

---

# High-Level Architecture

```text
                          SHOPIFY
                             |
                             v
                  +---------------------+
                  | moda-interact       |
                  | webhook ingress     |
                  |---------------------|
                  | authenticate        |
                  | normalize           |
                  | publish immediately |
                  | acknowledge         |
                  +----------+----------+
                             |
                             v
                  +---------------------+
                  | Redis / BullMQ      |
                  | commerce events     |
                  +----------+----------+
                             |
                             v
               +-----------------------------+
               | moda-interact-background    |
               +--------------+--------------+
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
      checkouts/create  checkouts/update   orders/create
             |                |                |
             v                v                v
       create delayed     recovery exists?   pending candidate?
       candidate              |                |
       in background       +--+--+          +--+--+
                            |     |          |     |
                           no    yes        yes    no
                            |     |          |     |
                            v     v          v     v
                         discard refresh   cancel  existing
                                 recovery candidate recovery?
                                                   |
                                                +--+--+
                                                |     |
                                               yes    no
                                                |     |
                                                v     v
                                             complete discard
                                             recovery
```

---

# PendingRecoveryCandidate

A pending recovery candidate is temporary Redis/BullMQ state.

Its purpose is only:

> Remember enough information to identify this checkout when the recovery delay expires, and to correlate an order that may complete it before recovery begins.

Based on the currently available Shopify webhook payloads, the candidate should contain:

```text
PendingRecoveryCandidate

shopId
checkoutToken
cartToken
abandonedCheckoutUrl
checkoutCreatedAt
```

### `shopId`

Identifies the Moda tenant/shop and allows the background service to resolve the Shopify credentials required for later API access.

### `checkoutToken`

Primary checkout correlation identifier.

It is also available on relevant order payloads as `checkout_token`.

### `cartToken`

Secondary correlation identifier.

It is useful because Shopify order payloads also expose `cart_token`.

### `abandonedCheckoutUrl`

The checkout webhook payload exposes an `abandoned_checkout_url`.

This is retained because it is the buyer recovery URL and may also assist with identifying the corresponding abandoned checkout.

### `checkoutCreatedAt`

Provides a narrow time reference that may assist the later Shopify abandoned-checkout lookup.

---

## Data deliberately not stored

The pending candidate must not persist:

```text
customer
email
phone
lineItems
quantity
prices
total
currency
addresses
discounts
basket contents
```

Those values are fetched from Shopify only if the checkout actually becomes a recovery.

---

# `checkouts/create`

A checkout creation establishes or refreshes a pending recovery candidate.

```text
checkouts/create
      |
      v
authenticate / normalize
      |
      v
background processor
      |
      v
create/reset delayed candidate
      |
      v
wait recovery delay
```

The logical candidate identity is:

```text
shopId + checkoutToken
```

Only one pending recovery candidate should exist for a given shop/checkout.

Repeated candidate creation for the same checkout should refresh the one pending recovery decision rather than create multiple recovery timers.

---

# Pending Recovery Execution

When the delayed candidate becomes due:

```text
candidate executes
      |
      v
resolve Shopify shop credentials
      |
      v
query Shopify
for current abandoned checkout
      |
      v
still eligible?
   +--+--+
   |     |
  no    yes
   |     |
   v     v
discard  create CheckoutRecovery
```

The current webhook snapshot is **not** used to populate `CheckoutRecovery`.

Shopify is queried at recovery time so Moda works from the current checkout state.

The Shopify response is used to populate the recovery information required by Moda, including where available:

- customer information;
- line items;
- quantities;
- totals;
- currency;
- recovery URL;
- checkout state required to confirm recoverability.

---

# Shopify Lookup

ARCH-001 requires a Shopify lookup when the pending candidate matures.

The candidate retains:

```text
shopId
checkoutToken
cartToken
abandonedCheckoutUrl
checkoutCreatedAt
```

because those are the relevant identifiers/locators available from the checkout webhook payload.

The exact GraphQL query and deterministic lookup strategy are **not yet fixed by this high-level architecture**.

The implementation design must establish the cheapest reliable way to identify the correct Shopify abandoned checkout from these values.

The architecture must not assume a GraphQL filter exists unless it is verified during implementation.

---

# `orders/create`

Orders are relevant only when they affect recovery.

## Pending candidate exists

```text
orders/create
      |
      v
match by checkoutToken
or cartToken
      |
      v
pending candidate found
      |
      v
cancel/remove candidate
      |
      v
discard order
```

No PostgreSQL order record is created.

No `CheckoutRecovery` is created.

The checkout completed normally before recovery began, so Moda no longer cares about it.

---

## Existing CheckoutRecovery exists

```text
orders/create
      |
      v
matching CheckoutRecovery
      |
      v
complete / attribute recovery
```

This order matters because it relates to a recovery already being managed by Moda.

---

## No recovery relationship

```text
orders/create
      |
      v
no pending candidate
no CheckoutRecovery
      |
      v
discard
```

No durable business record is required.

---

# `checkouts/update`

A checkout update matters only when the checkout already has a `CheckoutRecovery`.

## No CheckoutRecovery

```text
checkouts/update
      |
      v
CheckoutRecovery exists?
      |
      no
      |
      v
discard
```

This includes a checkout that is still only a pending recovery candidate.

The candidate does not need to track basket changes because the current checkout will be fetched from Shopify if the candidate later matures.

---

## Existing CheckoutRecovery

```text
checkouts/update
      |
      v
CheckoutRecovery exists
      |
      v
query Shopify for current checkout
      |
      v
refresh CheckoutRecovery
```

This supports:

```text
recovery message sent
      |
      v
customer returns
      |
      v
basket changes
      |
      v
checkout update webhook
      |
      v
Moda refreshes current recovery basket
```

The refresh may update:

- line items;
- quantities;
- totals;
- currency;
- recovery URL;
- other existing recovery fields required by the application.

---

# Re-Abandonment After Recovery

ARCH-001 stops after refreshing an existing `CheckoutRecovery`.

The scenario:

```text
recovery sent
    ->
customer changes basket
    ->
customer does not purchase
```

will be handled downstream in a later iteration.

ARCH-001 does not decide whether to:

- restart an abandonment timer;
- send another recovery message;
- create another recovery stage;
- reset the recovery workflow.

---

# Repository Responsibilities

## `moda-interact`

Owner:

```text
moda_app
```

Responsibilities:

- Shopify webhook ingress;
- Shopify webhook authentication;
- minimal normalisation;
- extraction of recovery correlation identifiers;
- publication to BullMQ;
- acknowledgement to Shopify.

It must not perform recovery-state decisions.

---

## `moda-interact-shared`

Owner:

```text
moda_shared
```

Responsibilities:

- canonical Shopify checkout/order event contracts;
- schema versions;
- runtime validation;
- queue/job names;
- shared correlation identifiers/helpers.

Package:

```text
@modainteract/moda-interact-shared
```

Producer and consumer must use the same shared contract.

---

## `moda-interact-background`

Owner:

```text
moda_background
```

Responsibilities:

- pending recovery candidate creation;
- pending candidate refresh;
- pending candidate cancellation;
- delayed candidate execution;
- Shopify API/GraphQL retrieval;
- `CheckoutRecovery` creation;
- existing recovery refresh;
- order/recovery correlation;
- irrelevant-event discard;
- retry and concurrency handling.

---

## `moda-interact-database`

Owner:

```text
moda_database
```

PostgreSQL stores actual recovery business state only.

ARCH-001 does not require a general checkout-state table.

A database task should only be introduced if inspection of the existing `CheckoutRecovery` schema shows that it cannot support:

- current basket data;
- recovery URL;
- recovery completion;
- order attribution;
- required uniqueness/indexing.

---

# Cross-Service Contract

The producer and consumer must share one canonical event definition.

Contract owner:

```text
moda-interact-shared
```

Producer:

```text
moda-interact
```

Consumer:

```text
moda-interact-background
```

The current producer/consumer contract mismatch must be removed.

Pre-recovery events should contain only information required for:

- tenant identification;
- checkout correlation;
- order correlation;
- later Shopify lookup;
- tracing/idempotency.

They should not duplicate checkout basket state that will later be retrieved from Shopify.

---

# Correlation

Primary recovery correlation:

```text
shopId + checkoutToken
```

Secondary order correlation where required:

```text
shopId + cartToken
```

Unsafe heuristics such as customer identity alone must not be used to associate an order with a checkout recovery unless separately designed and approved.

---

# Redis / BullMQ

Redis/BullMQ represents pending recovery state and asynchronous transport.

Candidate logical ID:

```text
recovery-candidate:{shopId}:{checkoutToken}
```

The exact BullMQ-safe identifier may use a deterministic shared helper.

The delayed BullMQ schedule represents the recovery timing.

No separate durable `recoveryDueAt` is required unless implementation needs it for another purpose.

---

# Idempotency

Only one pending recovery candidate may exist for:

```text
shopId + checkoutToken
```

Only one `CheckoutRecovery` may exist for:

```text
shopId + checkoutToken
```

Duplicate webhook or queue processing must not:

- create duplicate candidates;
- create duplicate recoveries;
- duplicate recovery completion;
- corrupt existing recovery state.

---

# Ordering and Concurrency

Global Shopify event ordering is not required.

The narrow recovery correlation key is:

```text
shopId + checkoutToken
```

The important concurrency case is:

```text
pending recovery job becomes due
        |
        | concurrently
        |
orders/create arrives
```

The implementation must ensure that a checkout which completes before recovery is committed does not incorrectly enter the recovery workflow.

The exact concurrency mechanism will be defined in the background implementation task.

---

# Failure Handling

If queue publication fails before webhook acceptance, Shopify should receive a retryable failure.

Once the webhook has been acknowledged, background work must use bounded retries.

Transient failures must not silently lose:

- candidate cancellation;
- Shopify checkout lookup;
- recovery creation;
- recovery refresh;
- recovery completion.

Failed jobs must remain operationally visible for diagnosis/recovery.

---

# Scalability

Reference Shopify ingress workload:

```text
approximately 20,000 inbound events per minute
```

This is raw commerce-event volume, not recovery volume.

Most events should terminate cheaply.

Examples:

```text
checkout update
    -> no recovery
    -> discard

order
    -> no candidate/recovery
    -> discard
```

Shopify API/GraphQL calls occur only for the smaller recovery-related subset:

```text
candidate matures
    -> query Shopify

existing recovery updated
    -> query Shopify
```

This separates raw Shopify webhook scale from recovery-processing and Shopify API scale.

---

# Security and Data Minimisation

The architecture preserves:

- authenticated Shopify webhooks;
- tenant isolation;
- server-side Shopify credentials;
- minimal customer-data logging;
- minimal pre-recovery data retention.

Pending candidates deliberately avoid retaining customer/basket data.

Unrelated Shopify activity is not persisted as Moda business state.

---

# Observability

The system should provide enough operational visibility to trace:

```text
webhook
    ->
queue event
    ->
background decision
    ->
candidate create/cancel
    OR
recovery create/update/complete
    OR
discard
```

Relevant identifiers include:

- Shopify delivery/event identifier;
- shop ID;
- checkout token;
- cart token;
- order ID where relevant;
- BullMQ job ID;
- `CheckoutRecovery.id` after recovery creation.

Irrelevant commerce payloads should not be retained simply for logging.

---

# Rollout

High-level implementation order:

1. publish the recovery-focused shared contract;
2. deploy a background consumer capable of validating the shared contract and tolerating legacy queued v1 events during transition;
3. update `moda-interact` to emit the new minimal checkout-create, checkout-update and order events immediately;
4. create pending recovery candidates inside `moda-interact-background`;
5. implement the Shopify abandoned-checkout lookup;
6. materialize matured candidates into `CheckoutRecovery`;
7. implement order cancellation/completion behaviour;
8. implement existing-recovery refresh on checkout updates;
9. verify retry, duplicate, concurrency and rolling-deployment behaviour.

---

# Decisions / Tasks

ARCH-001 is decomposed into the following repository-owned tasks.

| Task | Owner | Status | Depends On |
|------|-------|--------|------------|
| ARCH-001-SHARED-001 | moda_shared | Ready | - |
| ARCH-001-SHOPIFY-001 | moda_app | Pending | ARCH-001-SHARED-001 |
| ARCH-001-SHOPIFY-002 | moda_app | Pending | ARCH-001-SHOPIFY-001 |
| ARCH-001-BACKGROUND-001 | moda_background | Pending | ARCH-001-SHARED-001 |
| ARCH-001-BACKGROUND-002 | moda_background | Pending | ARCH-001-BACKGROUND-001 |
| ARCH-001-BACKGROUND-003 | moda_background | Pending | ARCH-001-BACKGROUND-001 |
| ARCH-001-BACKGROUND-004 | moda_background | Pending | ARCH-001-BACKGROUND-002, ARCH-001-BACKGROUND-003 |
| ARCH-001-BACKGROUND-005 | moda_background | Pending | ARCH-001-BACKGROUND-004 |
| ARCH-001-BACKGROUND-006 | moda_background | Pending | ARCH-001-BACKGROUND-003 |

No database task is currently required. The existing `CheckoutRecovery` model already contains the durable fields required by this architecture. If implementation discovers that a deterministic Shopify lookup or required recovery transition cannot be supported by the existing schema, the affected task must be blocked and returned to `moda_architect` rather than silently expanding database scope.

## Execution Plan

```text
ARCH-001-SHARED-001
        |
        +-------------------------------+
        |                               |
        v                               v
ARCH-001-SHOPIFY-001          ARCH-001-BACKGROUND-001
        |                               |
        v                         +-----+------+
ARCH-001-SHOPIFY-002           |            |
                                v            v
                    ARCH-001-BACKGROUND-002  ARCH-001-BACKGROUND-003
                                |            |
                                +-----+------+
                                      |
                                      v
                           ARCH-001-BACKGROUND-004
                                      |
                                      v
                           ARCH-001-BACKGROUND-005

ARCH-001-BACKGROUND-003
        |
        v
ARCH-001-BACKGROUND-006
```

`SHOPIFY-001/002` and `BACKGROUND-001/002/003` may proceed independently once their declared dependencies are complete. They should not be serialised merely because they belong to the same architecture.

The individual task file is authoritative for task state.

# Open Questions

## 1. Shopify abandoned-checkout lookup

The exact supported Shopify API/GraphQL lookup must be verified by `ARCH-001-BACKGROUND-003`.

The approved candidate identifiers are:

```text
checkoutToken
cartToken
abandonedCheckoutUrl
checkoutCreatedAt
```

If the lookup cannot be implemented deterministically or with a bounded query using these identifiers, the task must be returned **Blocked** to `moda_architect`.

## 2. Cart webhooks

`carts/create` and `carts/update` remain outside the current recovery flow.

Whether they should remain subscribed but ignored or be removed will be decided separately and must not expand ARCH-001 implementation scope.

---

# Deferred Architecture

The following known flows are intentionally deferred:

## Checkout deletion

Future iteration.

## Re-abandonment after recovery checkout modification

Future downstream recovery-workflow iteration.

These must not be silently implemented as part of ARCH-001.

---

# Change History

## 2026-08-28

Initial architecture created.

## 2026-08-28

Removed general durable checkout-state proposal and made `CheckoutRecovery` the only durable checkout recovery entity.

## 2026-08-28

Reduced pending recovery state to recovery-identification/correlation fields.

## 2026-08-28

Added `abandonedCheckoutUrl`, `cartToken` and `checkoutCreatedAt` based on the available Shopify webhook payload structure.

Clarified that Shopify is queried when current recovery basket data is needed.

## 2026-08-28

Explicitly deferred Shopify checkout-deletion handling to a future architecture iteration.
