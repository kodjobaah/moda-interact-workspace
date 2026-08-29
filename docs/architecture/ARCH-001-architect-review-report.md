# ARCH-001 Architect Review Report — 2026-08-29

## Overall outcome

The implementation is moving in the correct architectural direction, but ARCH-001 is **not ready for system testing yet**. One task is accepted; two upstream tasks have Changes Requested; downstream tasks are blocked in dependency order.

## Task outcomes

| Task | Architect outcome | Immediate action |
|---|---|---|
| ARCH-001-SHARED-001 | Accepted / Complete | None |
| ARCH-001-SHOPIFY-001 | Changes Requested / In Progress | Normalize Shopify offset timestamps to canonical UTC and use shared schema-version constant |
| ARCH-001-SHOPIFY-002 | Blocked | Re-review after SHOPIFY-001 correction |
| ARCH-001-BACKGROUND-001 | Changes Requested / In Progress | Use shared queue/job constants and preserve v1 checkout URL locator |
| ARCH-001-BACKGROUND-002 | Blocked | After B001: remove stale old cart alias when candidate refresh changes cart token |
| ARCH-001-BACKGROUND-003 | Blocked | After B001: correct GraphQL 2026-07 count and abandoned-checkout field shapes |
| ARCH-001-BACKGROUND-004 | Blocked | After B002/B003: make partial materialization/messaging retry resumable; do not remove candidate indexes on retryable failure |
| ARCH-001-BACKGROUND-005 | Blocked | After B004: strengthen Redis lock/lease/release and tombstone-before-active-job-cancel race handling |
| ARCH-001-BACKGROUND-006 | Blocked | Re-review after B003 and resolve durable `detectedAt`/checkout-created-time semantics |

## Highest-priority findings

### 1. Real Shopify timestamps can be rejected at ingress

The producer copies webhook `created_at` directly into v2 payloads. The supplied Shopify payload samples use values such as `2021-12-31T19:00:00-05:00`. The shared v2 schema uses `z.iso.datetime()`, whose default contract expects UTC/Z and rejects timezone offsets. The producer must normalize valid Shopify provider timestamps to UTC ISO before parsing the shared event.

### 2. BACKGROUND-003 GraphQL document is not valid for Shopify Admin GraphQL 2026-07

The bounded lookup design is retained, but implementation fields/arguments must be corrected:

- `abandonedCheckoutsCount(limit:, query:)`, not `maximum:`;
- request `count` and `precision`; use a count bound capable of detecting more than the configured maximum;
- `AbandonedCheckout.totalPriceSet`, not `totalPrice` / top-level `currencyCode`;
- `AbandonedCheckoutLineItem.originalUnitPriceSet` and direct `sku`, not the current assumed fields.

### 3. Materialization retries can strand a recovery

If the recovery row is created and subsequent customer/conversation/WhatsApp work fails, retry sees the existing DETECTED recovery and no-ops. The recovery can remain permanently DETECTED/FAILED instead of resuming the message intent. Candidate indexes are also removed in a `finally` block even on retryable failures.

### 4. Candidate/order race lock is not safe enough

The custom Redis lock has a fixed 10-second TTL, no renewal, and non-atomic GET-then-DEL release while the protected path includes external network calls. The order path also tries to remove the BullMQ job before recording the order-completion guard. An active job can make removal fail before the guard exists.

## Validation position

The repository agents recorded substantial targeted validation and successful builds, with one pre-existing background unit-test failure. The architect could not independently rerun all suites from the supplied ZIP because dependencies were not fully runnable in the review environment. Static code review plus current Shopify/Zod API verification was sufficient to identify the correctness issues above.

## Next execution

Two tasks can be worked now, in parallel:

1. `ARCH-001-SHOPIFY-001` -> `moda_app`
2. `ARCH-001-BACKGROUND-001` -> `moda_background`

Do not start the blocked downstream tasks until the architect accepts their dependencies.

After all implementation tasks are Complete, create an `ARCH-001-SYSTEM-TEST-001` task for `moda_system_test`.
