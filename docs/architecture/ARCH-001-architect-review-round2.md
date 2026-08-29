# ARCH-001 Architect Review — Round 2

Date: 2026-08-29

## Overall decision

The two round-1 correction tasks are accepted:

- `ARCH-001-SHOPIFY-001` -> **Complete / Accepted**
- `ARCH-001-BACKGROUND-001` -> **Complete / Accepted**

`SHARED-001` and `SHOPIFY-002` have also been formally architect-reviewed and recorded as Accepted.

The downstream background tasks were not actually architect-reviewed in the submitted workspace. Their task files had been changed to `Complete`, but their Architect Review sections contained no reviewed files, no validation evidence and used `Complete` as a review status (the valid accepted review state is `Accepted`). The code was therefore reviewed from source rather than trusting those metadata edits.

## Current task state

| Task | Decision |
|---|---|
| ARCH-001-SHARED-001 | Complete / Accepted |
| ARCH-001-SHOPIFY-001 | Complete / Accepted |
| ARCH-001-SHOPIFY-002 | Complete / Accepted |
| ARCH-001-BACKGROUND-001 | Complete / Accepted |
| ARCH-001-BACKGROUND-002 | In Progress / Changes Requested |
| ARCH-001-BACKGROUND-003 | In Progress / Changes Requested |
| ARCH-001-BACKGROUND-004 | Blocked |
| ARCH-001-BACKGROUND-005 | Blocked |
| ARCH-001-BACKGROUND-006 | Blocked on BACKGROUND-003 only |
| ARCH-001-GATEWAY-001 | Ready |

## Findings requiring correction

### BACKGROUND-002 — duplicate timing and stale cart alias

`PendingRecoveryCandidateService.scheduleFromCheckoutCreated()` calls `changeDelay()` when the deterministic candidate already exists. Because Shopify webhook processing is at-least-once, a duplicate `checkout.created` delivery can postpone recovery.

The existing candidate's due time must remain anchored to the first accepted checkout-create.

When candidate data changes from one cart token to another, the old cart alias is also left in Redis. That stale alias can later correlate an order to the wrong candidate.

### BACKGROUND-003 — Shopify GraphQL schema mismatch

The bounded lookup design remains valid, but the GraphQL request does not match Admin GraphQL 2026-07.

The implementation currently uses `abandonedCheckoutsCount(maximum:)`; the current API uses `limit`. The current abandoned-checkout object exposes `totalPriceSet` rather than the queried top-level `currencyCode` / `totalPrice`, and line items expose `originalUnitPriceSet` plus direct `sku`.

The unit tests mirror the invalid provider response shape, so they cannot prove live schema compatibility.

The task has been returned for correction with a recommended bounded selector (`MAX + 1`) followed by a full Node fetch for the single exact URL match.

### BACKGROUND-004 — partial failure can strand DETECTED recovery

If the recovery row is created and a later customer/conversation/WhatsApp operation throws, BullMQ retries. The retry sees the existing active recovery and returns `no-op-existing`, so the recovery can remain `DETECTED` without resuming its initial message workflow.

The pending-candidate worker also removes transient candidate indexes from a `finally` block, including retryable failures.

### BACKGROUND-005 — lock/ordering race is not safe

The checkout lock has a fixed 10-second TTL and no lease renewal while the protected path can contain external network work.

Release is non-atomic `GET` then `DEL`, allowing an expired owner to race with a new owner.

Order handling attempts candidate removal before writing the order-completed tombstone. An active BullMQ job can make removal fail before suppression state exists.

The one-hour tombstone is also shorter than Shopify's documented webhook retry horizon and needs an explicit safe lifetime/scheduling strategy.

### BACKGROUND-006 — schema change not required

The implementation can continue using the existing schema once BACKGROUND-003 is corrected.

ARCH-001 now explicitly defines:

- `detectedAt` = original Shopify checkout-created/detection anchor;
- `createdAt` = durable recovery materialization time;
- `messageSentAt` = message lifecycle time.

No database task is needed.

## Shopify producer duplicate-delivery clarification

ARCH-001 does not attempt exactly-once webhook delivery.

The producer's deterministic BullMQ job IDs provide useful duplicate suppression while a job exists, but `removeOnComplete: true` means that identity is not a permanent receipt ledger. This is acceptable because ARCH-001 requires idempotent consumers.

The critical correction is therefore in BACKGROUND-002: a repeated checkout-create event must not reset the candidate delay or create a second business workflow.

## Infrastructure assessment

Under the new `moda_gateway` ownership model, ARCH-001 requires one infrastructure task.

Both `moda-interact` and `moda-interact-background` currently reference the shared package using:

`file:../moda-interact-shared`

while their Dockerfiles install dependencies from the individual service directory. The actual Render source/build context and shared-package resolution must be proven rather than assumed.

`ARCH-001-GATEWAY-001` is therefore Ready and can run in parallel with BACKGROUND-002/003 corrections.

It must not silently publish packages or change application business capabilities. If the current Render topology cannot resolve the shared package, it should return the exact architectural dependency to `moda_architect`.

## Validation position

The architect inspected the submitted source and compared it with the previous workspace snapshot.

Independent full test execution could not be completed from the ZIP because dependency installation was not available reliably in the review environment. Agent-recorded validation was considered for the accepted correction tasks, while the defects above were established directly from static code inspection and current Shopify provider documentation.

## Next parallel work

Two background corrections and one infrastructure task can proceed now:

1. `ARCH-001-BACKGROUND-002` -> `moda_background`
2. `ARCH-001-BACKGROUND-003` -> `moda_background`
3. `ARCH-001-GATEWAY-001` -> `moda_gateway`

BACKGROUND-002 and BACKGROUND-003 are independent and may be implemented in parallel if separate repository worktrees/executors are used safely. If one `moda_background` executor is used, follow repository task priority/claiming rules.

Do not start BACKGROUND-004/005/006 yet.

After all business implementation and gateway tasks are architect-accepted, create `ARCH-001-SYSTEM-TEST-001` for `moda_system_test`.
