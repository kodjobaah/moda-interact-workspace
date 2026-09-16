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
status: ready
priority: 50
executor: null
claimed_at: null
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

## Completion Report

Status: Ready for Review

Implementation commit: `6050a33` (`Consume historical purchased recovery credits first`), pushed to `task/ARCH-015-BACKGROUND-002`.

### Implementation Summary

- Updated `src/services/purchased-recovery-reservation.service.ts` to read the local Subscription projection and use Shared `isSameShopifyPurchaseProviderContext` for current-context classification.
- ACTIVE spendable lots remain eligible regardless of plan, billing-period, or meter; historical/non-current lots are selected before current-context lots, with existing activatedAt/createdAt/id FIFO ordering within each group.
- Missing, incomplete, unmapped, frozen, or otherwise non-current subscription projections classify lots as historical for ordering without making them unspendable.
- Existing released-reservation replay affinity, refund-held WITHDRAWN exclusion, atomic CAS updates, and local `RECOVERY_CONVERSATION` / `NOT_APPLICABLE` usage evidence remain intact. No Shopify I/O was added.

### Acceptance Mapping

- Cross-plan preservation and no current plan/period filtering: satisfied by retaining all ACTIVE lots in the selector and using context only for ordering.
- Historical-before-current and within-group FIFO: covered by focused unit tests for current-context partitioning and group ordering.
- Ambiguous subscription projection: covered by focused unit test; all lots remain spendable and are ordered historically.
- Replay affinity, WITHDRAWN refund holds, NOT_APPLICABLE evidence, and CAS/concurrency behavior: existing focused unit coverage remains green.

### Tests and Validation

- `npm run test -- tests/unit/services/purchased-recovery-reservation.service.test.ts`: passed, 17/17.
- `npm run test -- tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts`: skipped, 7 tests, because `TEST_DATABASE_URL` and `MODA_DISPOSABLE_INTEGRATION=1` were not enabled in the environment.
- `npm run build`: passed, including Prisma client generation and TypeScript compilation.
- `npm run test:unit`: 925/927 passed; 2 failures are existing unrelated observability-startup baseline expectations for worker close-resource source text and Shared version `0.9.0` versus the repository package version `0.11.2`.
- `git diff --check`: passed.

### Worktree and Dependency Evidence

- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-BACKGROUND-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-BACKGROUND-002`.
- Implementation base: `4dd3782e40892ce0f860a7ea727674cdc62017af`.
- Database submodule observed at: `d44b621cdcc3635127b91601be648b61c0eff1e2`.

### Limitations

- Disposable PostgreSQL concurrency tests were not executable without the required integration environment gate; no source or schema workaround was applied.
- Broader unit-test failures were not modified because they are outside this task's authorized implementation surface.
