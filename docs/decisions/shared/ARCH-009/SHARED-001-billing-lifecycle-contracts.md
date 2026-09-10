---
id: ARCH-009-SHARED-001
architecture_id: ARCH-009
title: Publish lifecycle messages, cancellation mapping and purchased-credit availability
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-009-DATABASE-001
enables:
  - ARCH-009-SHOPIFY-001
  - ARCH-009-BACKGROUND-001
  - ARCH-009-BACKGROUND-002
  - ARCH-009-ADMIN-001
created: 2026-09-09
updated: 2026-09-10
---

# ARCH-009-SHARED-001

## Baseline

Expected package baseline exactly 0.8.0.

If different, STOP and report drift.

Target:

```text
0.9.0
```

## SYSTEM message additions

Append exactly:

```ts
PLAN_CHANGE_ACTION_REQUIRED: "BILLING_PLAN_CHANGE_ACTION_REQUIRED",
CANCELLATION_REQUEST_RECEIVED: "BILLING_CANCELLATION_REQUEST_RECEIVED",
CANCELLATION_COMPLETED: "BILLING_CANCELLATION_COMPLETED",
CANCELLATION_REJECTED: "BILLING_CANCELLATION_REJECTED",
REFUND_REQUEST_RECEIVED: "BILLING_REFUND_REQUEST_RECEIVED",
REFUND_COMPLETED: "BILLING_REFUND_COMPLETED",
REFUND_REJECTED: "BILLING_REFUND_REJECTED",
```

Add exact values to billing system-code Zod tuple.

## Cancellation modes

```ts
export const SUBSCRIPTION_CANCELLATION_MODES = [
  "END_OF_CYCLE",
  "IMMEDIATE_NO_PRORATION",
  "IMMEDIATE_PRORATED",
  "IMMEDIATE_SKIP_FINAL_USAGE",
] as const;

export const SubscriptionCancellationModeSchema =
  z.enum(SUBSCRIPTION_CANCELLATION_MODES);

export type SubscriptionCancellationMode =
  z.infer<typeof SubscriptionCancellationModeSchema>;
```

## Exact provider mapping

```ts
export type ShopifySubscriptionCancellationArgs = Readonly<{
  deferCancellation: boolean;
  prorate: boolean;
  skipFinalUsageCharge: boolean;
}>;

export const SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS = {
  END_OF_CYCLE: {
    deferCancellation: true,
    prorate: false,
    skipFinalUsageCharge: false,
  },
  IMMEDIATE_NO_PRORATION: {
    deferCancellation: false,
    prorate: false,
    skipFinalUsageCharge: false,
  },
  IMMEDIATE_PRORATED: {
    deferCancellation: false,
    prorate: true,
    skipFinalUsageCharge: false,
  },
  IMMEDIATE_SKIP_FINAL_USAGE: {
    deferCancellation: false,
    prorate: false,
    skipFinalUsageCharge: true,
  },
} as const satisfies Readonly<
  Record<SubscriptionCancellationMode, ShopifySubscriptionCancellationArgs>
>;
```

No consumer duplicates this mapping.

## Availability helper

```ts
export type PurchasedRecoveryCreditCounterSnapshot = Readonly<{
  grantedQuantity: number;
  committedQuantity: number;
  reservedQuantity: number;
  refundingQuantity: number;
}>;

export function availablePurchasedRecoveryCredits(
  counter: PurchasedRecoveryCreditCounterSnapshot,
): number {
  for (const [name, value] of Object.entries(counter)) {
    if (!Number.isInteger(value) || value < 0) {
      throw new Error(`${name} must be a non-negative integer`);
    }
  }

  return Math.max(
    counter.grantedQuantity
      - counter.committedQuantity
      - counter.reservedQuantity
      - counter.refundingQuantity,
    0,
  );
}
```

## Tests

Prove:

- old codes unchanged;
- seven new codes exact;
- mode tuple exact;
- mapping exact;
- no prorate+skip-final combination;
- 100/20/10/0 -> 70;
- 100/20/10/30 -> 40;
- negative result -> 0;
- negative/non-integer input throws.

## Package

Set version 0.9.0.

Do not alter exports map.

If publishing is allowed, publish and verify:

```bash
npm view @modainteract/moda-interact-shared@0.9.0 version dist.shasum
```

Otherwise report not published.

## Validation

```bash
npm test
npm run typecheck
npm run build
git diff --check
```

## Stop

Return review and STOP.

## Completion Report

### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
None
### Deviations
None
### Assumptions
None
### Unresolved Issues
None
### Architectural Concerns
None

## Architect Review

### Review Status
Pending
### Review Notes
None
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending
### Follow-up
None
