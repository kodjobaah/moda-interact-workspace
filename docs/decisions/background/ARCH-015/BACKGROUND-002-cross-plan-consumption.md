---
id: ARCH-015-BACKGROUND-002
architecture_id: ARCH-015
title: Consume historical purchased-credit lots before current refundable lots
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 50
executor: copilot
claimed_at: 2026-09-16T00:00:23Z
attempt: 1
depends_on:
- ARCH-015-SHARED-001
- ARCH-015-BACKGROUND-001
enables:
- ARCH-015-SYSTEM-TEST-001
created: 2026-09-15
updated: 2026-09-16
---

# ARCH-015-BACKGROUND-002

## Objective

Preserve all active purchased credits across plan/cycle changes while changing reservation selection to consume historical/non-current-provider-context lots before current-context lots.

## Authorized implementation surface

```text
src/services/purchased-recovery-reservation.service.ts
src/services/recovery-billing.service.ts                 # only if orchestration needs classification input
tests/unit/services/purchased-recovery-reservation.service.test.ts
tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts
```

No Shopify network call in the reservation path.

## Current-context classification

Use current local Subscription projection only as a consumption-order hint.

Derive current provider context through Shared from:

```text
Subscription.providerSubscriptionId
Subscription.observedShopifyPlanHandle
Subscription.currentPeriodStart
Subscription.currentPeriodEnd
Subscription.billingPeriodId
```

A lot is "current-context" only when:

```text
status == ACTIVE
purchase.providerSubscriptionIdSnapshot == current derived context
purchase.shopifyPlanHandleSnapshot == current observed plan handle
purchase.billingPeriodId == current billingPeriodId
```

If subscription projection is missing/ambiguous/unmapped/frozen, classify all lots as historical for ordering. This does not make them unspendable.

## Selection order

For spendable ACTIVE lots:

```text
1. historical/non-current lots
   order activatedAt ASC NULLS LAST, createdAt ASC, id ASC

2. current-context lots
   same oldest-first order
```

Retain all existing atomic reservation/CAS/refund-hold rules.

Do not filter by current `planId`, current billingPeriodId, or current meter to determine spendability.

## Replay behavior

If an existing released reservation can reuse its original lot and that lot is still ACTIVE/spendable, preserve replay affinity even if classification changed. If original lot cannot be reused, apply the new ordered selector.

## Shopify billing rule

Commit of purchased credits continues to create local `RECOVERY_CONVERSATION` usage evidence with `ShopifyReportState.NOT_APPLICABLE`.

Never emit the purchase meter's event handle when consuming credits.

## Tests

- old Starter lot remains spendable after Growth transition;
- historical Starter lots selected before current Growth lot even when Growth lot is older by id;
- within historical group oldest first;
- within current group oldest first;
- ambiguous local subscription => all lots still spendable, oldest ordering;
- no current plan/billingPeriod filter removes historical credits;
- replay original lot semantics preserved;
- refund-held WITHDRAWN lots remain non-selectable;
- purchased-credit commit remains NOT_APPLICABLE to Shopify;
- concurrency/CAS tests remain green.

## Stop conditions

STOP if implementing order requires Shopify network I/O in recovery admission/reservation.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
