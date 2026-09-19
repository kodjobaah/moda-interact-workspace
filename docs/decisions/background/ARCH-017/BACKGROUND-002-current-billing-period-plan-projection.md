---
id: ARCH-017-BACKGROUND-002
architecture_id: ARCH-017
title: Enforce plan-complete current BillingPeriods across background reconciliation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-017-BACKGROUND-001
enables: []
created: 2026-09-19
updated: 2026-09-19
---

# ARCH-017-BACKGROUND-002


## Objective

Correct Background billing reconciliation so an executable mapped subscription cannot be created, refreshed, reinstalled, cycle-discovered or reconciled while its exact current OPEN `BillingPeriod` remains plan-null or partially projected.

The correction must self-heal the currently observed development state on the next successful same-cycle provider reconciliation without a database backfill or manual SQL.

This task does not reopen `ARCH-017-BACKGROUND-001`; that task remains Complete. This task is a bounded correctness follow-up discovered during manual system testing.

ARCH-011 remains out of scope.

## Current defects in the supplied 2026-09-19 snapshot

### Defect 1 — `billing-reconciliation.service.ts` can create the exact invalid state

Current generic code creates an OPEN period without any plan fields:

```ts
const billingPeriod = provider.currentPeriodStart && provider.currentPeriodEnd
  ? await this.database.billingPeriod.upsert({
      where: {
        shopId_periodStart_periodEnd: {
          shopId,
          periodStart: provider.currentPeriodStart,
          periodEnd: provider.currentPeriodEnd,
        },
      },
      update: { status: BillingPeriodStatus.OPEN },
      create: {
        shopId,
        subscriptionId: (await this.database.subscription.findUniqueOrThrow({
          where: { shopId },
          select: { id: true },
        })).id,
        periodStart: provider.currentPeriodStart,
        periodEnd: provider.currentPeriodEnd,
        status: BillingPeriodStatus.OPEN,
      },
    })
  : null;
```

Immediately afterwards the same path can write:

```ts
planId: planUsable ? plan?.id ?? null : null,
billingPeriodId: billingPeriod?.id ?? null,
status: ACTIVE | TRIALING,
```

That directly permits a mapped ACTIVE Subscription pointing at a plan-null period.

### Defect 2 — `billing-subscription-reconciliation.service.ts` uses `update: {}`

These functions create complete periods but never repair an existing exact-cycle row:

```text
completeReinstallFree()
reconcileFreeCycle()
completeVerifiedFree()
applyOtherCurrentPlan()
```

Each contains an exact-cycle `billingPeriod.upsert()` whose update branch is `{}`. A row created earlier while unmapped therefore remains incomplete forever.

### Defect 3 — same-plan reconciliation reaches rollover logic before repairing the current row

When `existing.planId === plan.id`, `BillingReconciliationService` can enter pending/same-plan rollover logic while `existing.billingPeriodId` references a plan-null current period. The current-period projection must be validated/repaired before the existing same-plan lifecycle service is allowed to continue.

## Required invariant

For every Background path that commits:

```text
Subscription.status = ACTIVE or TRIALING
Subscription.planId != null
Subscription.billingPeriodId != null
```

the referenced BillingPeriod must be the exact provider cycle and must be plan-complete:

```text
BillingPeriod.status = OPEN
BillingPeriod.subscriptionId = Subscription.id
BillingPeriod.planId = Subscription.planId
BillingPeriod.shopifyPlanHandleSnapshot = provider.planHandle
BillingPeriod.planNameSnapshot = BillingPlan.name
BillingPeriod.planKindSnapshot = BillingPlan.kind
```

FREE:

```text
includedRecoveryCreditsGranted = null
no INCLUDED_RECOVERY_CREDITS counter
```

PAID_METERED:

```text
includedRecoveryCreditsGranted = BillingPlan.includedRecoveryConversationAllowance
exactly one INCLUDED_RECOVERY_CREDITS counter
counter.grantedQuantity = included allowance
```

Missing/null compatible fields on the same OPEN cycle are repairable. Conflicting non-null history is not.

## Dependency gate

`ARCH-017-BACKGROUND-001` is Complete and is the required baseline.

Do not modify its accepted dynamic-feature or PlatformBillingPolicy behaviour except where imports/tests need to compile after this task.

At task start:

```bash
npm run prisma:generate
```

## Read before editing

Read these files completely:

```text
src/services/billing-reconciliation.service.ts
src/services/billing-subscription-reconciliation.service.ts
src/services/same-plan-billing-period-rollover.service.ts
src/services/shopify-plan-change-transition.service.ts
tests/unit/services/billing-reconciliation.service.test.ts
tests/unit/services/billing-subscription-reconciliation.service.test.ts
database/prisma/schema.prisma
docs/architecture/ARCH-017-billing-plan-materialisation-dynamic-features.md
```

The two existing transition services are read-only unless compilation proves a minimal import/type change is necessary. Do not move this task's generic repair semantics into them.

## Authorized implementation surface

Production:

```text
src/services/current-billing-period-projection.service.ts    # new
src/services/billing-reconciliation.service.ts
src/services/billing-subscription-reconciliation.service.ts
```

Tests:

```text
tests/unit/services/billing-reconciliation.service.test.ts
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

Do not edit the database submodule, queue contracts, Shared package, Admin, or Shopify application.

---

# Part A — add one reusable projection primitive

## A1. Create `src/services/current-billing-period-projection.service.ts`

Create this file. It must be database-only and must make no Shopify/Partner network call and no queue publication.

Use imports:

```ts
import {
  BillingPeriodEntitlementCounterKind,
  BillingPeriodStatus,
  BillingPlanKind,
  Prisma,
} from "@prisma/client";
```

Export these types:

```ts
export type CurrentBillingPeriodPlanProjection = {
  id: string;
  name: string;
  kind: BillingPlanKind;
  shopifyPlanHandle: string;
  includedRecoveryConversationAllowance: number | null;
};

export type CurrentBillingPeriodProjectionConflictReason =
  | "CLOSED_PERIOD"
  | "SUBSCRIPTION_MISMATCH"
  | "HANDLE_MISMATCH"
  | "PLAN_MISMATCH"
  | "PLAN_NAME_MISMATCH"
  | "PLAN_KIND_MISMATCH"
  | "INCLUDED_GRANT_MISMATCH"
  | "FREE_INCLUDED_COUNTER_PRESENT"
  | "INVALID_INCLUDED_ALLOWANCE"
  | "PAID_COUNTER_MISMATCH";

export type CurrentBillingPeriodProjectionResult =
  | {
      kind: "READY";
      billingPeriodId: string;
      repaired: boolean;
    }
  | {
      kind: "CONFLICT";
      billingPeriodId: string | null;
      reason: CurrentBillingPeriodProjectionConflictReason;
    };
```

Export one function only:

```ts
export async function ensureCurrentBillingPeriodProjection(
  transaction: Prisma.TransactionClient,
  input: {
    shopId: string;
    subscriptionId: string;
    periodStart: Date;
    periodEnd: Date;
    providerPlanHandle: string;
    plan: CurrentBillingPeriodPlanProjection;
  },
): Promise<CurrentBillingPeriodProjectionResult>
```

## A2. Exact helper algorithm

Implement these steps in this order.

### 1. Validate paid allowance

For `PAID_METERED`, `includedRecoveryConversationAllowance` must be a safe integer >= 0. Otherwise return:

```ts
{
  kind: "CONFLICT",
  billingPeriodId: null,
  reason: "INVALID_INCLUDED_ALLOWANCE",
}
```

Do not write database state.

### 2. Read exact period

Use only:

```ts
shopId_periodStart_periodEnd
```

Do not search by `subscriptionId` alone and do not create a second overlapping period.

### 3. Create complete row when absent

When absent, create:

```ts
{
  shopId: input.shopId,
  subscriptionId: input.subscriptionId,
  planId: input.plan.id,
  shopifyPlanHandleSnapshot: input.providerPlanHandle,
  planNameSnapshot: input.plan.name,
  planKindSnapshot: input.plan.kind,
  includedRecoveryCreditsGranted:
    input.plan.kind === BillingPlanKind.PAID_METERED
      ? input.plan.includedRecoveryConversationAllowance
      : null,
  periodStart: input.periodStart,
  periodEnd: input.periodEnd,
  status: BillingPeriodStatus.OPEN,
}
```

For PAID, create the included counter in the same transaction with zero consumed quantities.

For FREE, do not create a period counter.

### 4. Reject incompatible existing history

Return `CONFLICT` without modifying the period when:

```text
status is CLOSED
subscriptionId differs
non-null handle snapshot differs
non-null planId differs
non-null planNameSnapshot differs
non-null planKindSnapshot differs
non-null includedRecoveryCreditsGranted differs from the expected value
```

For a FREE plan, the expected included grant is null.

### 5. Repair compatible missing/null projection fields in place

If every non-null durable field is compatible, update the same existing row to the complete expected mapping:

```ts
await transaction.billingPeriod.update({
  where: { id: existingPeriod.id },
  data: {
    planId: input.plan.id,
    shopifyPlanHandleSnapshot: input.providerPlanHandle,
    planNameSnapshot: input.plan.name,
    planKindSnapshot: input.plan.kind,
    includedRecoveryCreditsGranted: expectedGrant,
    status: BillingPeriodStatus.OPEN,
  },
});
```

This includes the exact manual-test state where every plan field is null.

### 6. FREE counter invariant

Query the unique INCLUDED_RECOVERY_CREDITS counter key.

If FREE and the counter exists, return `CONFLICT/FREE_INCLUDED_COUNTER_PRESENT`. Do not delete it.

### 7. PAID counter invariant

For PAID:

- if no counter exists, create it with the full grant and zero committed/reserved/forfeited values;
- if it exists, require matching `shopId`, matching `grantedQuantity`, all quantities safe integers >= 0, and:

```text
committedQuantity + reservedQuantity + forfeitedQuantity <= grantedQuantity
```

Otherwise return `CONFLICT/PAID_COUNTER_MISMATCH` without resetting quantities.

### 8. Return repair flag

`repaired=true` if the existing period was incomplete or a missing paid counter was created. Otherwise false.

Do not log inside this primitive. Callers own bounded logs and state transitions.

---

# Part B — correct `BillingReconciliationService`

File:

```text
src/services/billing-reconciliation.service.ts
```

Import `ensureCurrentBillingPeriodProjection`.

## B1. Repair current same-plan cycle BEFORE pending/rollover handling

In the branch:

```ts
if (existing?.id && plan?.active && existing.planId === plan.id) {
```

before the existing pending-plan/cancellation branch and before `SamePlanBillingPeriodRolloverService.transition()`, calculate:

```ts
const providerMatchesCurrentCycle = Boolean(
  provider.currentPeriodStart &&
  provider.currentPeriodEnd &&
  existing.currentPeriodStart &&
  existing.currentPeriodEnd &&
  provider.currentPeriodStart.getTime() === existing.currentPeriodStart.getTime() &&
  provider.currentPeriodEnd.getTime() === existing.currentPeriodEnd.getTime()
);
```

When `providerMatchesCurrentCycle` is true, run one database transaction that:

1. locks the Subscription row with `SELECT ... FOR UPDATE`;
2. rereads at minimum `id`, `status`, `planId`, `billingPeriodId`, `currentPeriodStart`, `currentPeriodEnd`, `nextReconcileAt`;
3. returns stale/no-op if those durable facts no longer match the pre-transaction `existing` snapshot;
4. calls `ensureCurrentBillingPeriodProjection()` with the resolved current plan and provider cycle;
5. if READY, updates only these Subscription fields as needed:

```text
billingPeriodId = helper.billingPeriodId
currentPeriodStart = provider.currentPeriodStart
currentPeriodEnd = provider.currentPeriodEnd
lastSyncedAt = now
```

Do not clear pending plan/cancellation fields in this repair step;
6. if CONFLICT, set:

```text
status = SYNC_ERROR
lastSyncErrorCode = BILLING_PERIOD_PLAN_CONFLICT
lastSyncErrorAt = now
lastSyncedAt = now
nextReconcileAt = now + 60 seconds
```

and preserve `planId`, current period pointers and pending intent;
7. after commit, enqueue the existing deterministic subscription-reconcile job when a conflict scheduled `nextReconcileAt`.

If a conflict was recorded, return immediately from `reconcileShop()` and do not invoke SamePlan rollover or plan-change logic in the same pass.

This is the self-heal path for the live Free subscription shown during manual testing.

## B2. Replace the generic bare BillingPeriod creation

Find the generic tail that currently creates a period with only shop/subscription/date/status.

Do not leave that code in place.

For a resolved executable plan (`planUsable === true` and status is ACTIVE/TRIALING), project the BillingPeriod and Subscription in one `$transaction()`:

1. lock/reread Subscription;
2. call `ensureCurrentBillingPeriodProjection()`;
3. if READY, write `planId`, `billingPeriodId`, provider cycle, status and existing provider/pending metadata in the same transaction;
4. if CONFLICT, write `SYNC_ERROR/BILLING_PERIOD_PLAN_CONFLICT`, preserve existing current plan/period pointers and schedule a 60-second bounded retry;
5. do not create an overlapping period.

For UNMAPPED or other existing fail-closed states, do not call the mapped helper and do not create paid entitlement.

Delete the current bare `billingPeriod.upsert()` create branch after the replacement is in place.

---

# Part C — correct `BillingSubscriptionReconciliationService`

File:

```text
src/services/billing-subscription-reconciliation.service.ts
```

Import the helper and replace each exact-cycle `billingPeriod.upsert(... update: {})` in the functions below.

## C1. `completeReinstallFree()`

Replace the upsert with `ensureCurrentBillingPeriodProjection()` using the Free plan.

The function already owns a transaction and locks Shop/ShopSettings/Subscription. Keep those locks.

If helper returns CONFLICT:

```text
Subscription.status = SYNC_ERROR
lastSyncErrorCode = BILLING_PERIOD_PLAN_CONFLICT
lastSyncErrorAt = now
nextReconcileAt = now + 60 seconds
```

Do not reactivate the Shop in the same conflicting transaction. Commit the fail-closed Subscription state, then publish the existing deterministic retry after commit.

If READY, continue the existing reinstall activation and use `helper.billingPeriodId`.

## C2. `reconcileFreeCycle()`

Replace the upsert with the helper.

On CONFLICT, write the same `SYNC_ERROR/BILLING_PERIOD_PLAN_CONFLICT`, schedule a 60-second retry, return a result that causes the caller to publish only that retry, and do not overwrite the period.

On READY, continue using the returned period ID and existing drain schedule.

## C3. `completeVerifiedFree()`

Replace the upsert with the helper.

On CONFLICT, do not commit `ACTIVE/TRIALING`. Commit `SYNC_ERROR/BILLING_PERIOD_PLAN_CONFLICT` and schedule the normal bounded retry.

On READY, preserve all current lifetime-Free grant logic and use the returned period ID.

Do not change the lifetime Free counter value on replay.

## C4. `applyOtherCurrentPlan()`

This path may resolve FREE or PAID.

When `planUsable` and the resulting status would otherwise be ACTIVE/TRIALING, call the helper.

For PAID, pass `includedRecoveryConversationAllowance`; therefore extend this function's plan type/select if it does not currently include that field.

If READY, use the returned period ID.

If CONFLICT, override the result to:

```text
status = SYNC_ERROR
lastSyncErrorCode = BILLING_PERIOD_PLAN_CONFLICT
```

and preserve any existing current period/plan pointer rather than claiming the conflicted row.

If the plan is UNMAPPED or already SYNC_ERROR for missing usage meter, do not create an included counter.

## C5. Do not change strict existing Paid activation/reinstall paths that are already complete

The current strict Paid activation and Paid reinstall implementations already validate exact BillingPeriod snapshots/counters before committing entitlement. Do not rewrite those paths merely for stylistic consistency.

Only modify them if a focused test proves they call one of the defective generic helpers above; otherwise leave them unchanged.

---

# Required focused tests

## `billing-reconciliation.service.test.ts`

Add tests for:

1. **Exact live-state self-heal**: existing ACTIVE Free Subscription has resolved `planId` and `billingPeriodId`, exact provider cycle matches, period plan fields are null. One successful reconciliation repairs the same period ID and remains ACTIVE.
2. **Same-plan Free replay**: already complete period stays unchanged.
3. **Same-plan Paid missing counter repair**: complete mapped paid period missing its counter receives exactly one counter without resetting other durable state.
4. **Conflict does not enter rollover**: conflicting same-cycle period records `SYNC_ERROR/BILLING_PERIOD_PLAN_CONFLICT`, schedules one retry, and `SamePlanBillingPeriodRolloverService.transition()` is not allowed to mutate state in that pass.
5. **Generic new mapped Free projection** creates a complete period, not the old bare row.
6. **Generic new mapped Paid projection** creates complete snapshots and included counter atomically.
7. **UNMAPPED projection** creates no paid included counter.
8. **Subscription/period transaction atomicity**: helper conflict leaves historical period unchanged and does not commit ACTIVE/TRIALING against it.

## `billing-subscription-reconciliation.service.test.ts`

Add/update tests for:

1. `completeReinstallFree()` repairs an exact plan-null OPEN period in place.
2. `reconcileFreeCycle()` repairs an exact incomplete OPEN period in place.
3. `completeVerifiedFree()` repairs an exact incomplete OPEN period in place.
4. `applyOtherCurrentPlan()` repairs a Free incomplete period before ACTIVE commit.
5. `applyOtherCurrentPlan()` repairs a Paid incomplete period and creates one included counter.
6. every function above fails closed on a CLOSED exact period.
7. every function above fails closed on an exact period owned by another Subscription.
8. every function above fails closed on conflicting non-null plan identity.
9. Paid replay preserves non-zero committed/reserved/forfeited quantities.
10. no correction path creates a second BillingPeriod for the same `(shopId, periodStart, periodEnd)`.
11. existing lifetime Free counter tests remain unchanged and pass.
12. existing strict Paid activation/reinstall tests remain unchanged and pass.

## Acceptance criteria

- [ ] The exact manually observed ACTIVE Free + null-mapped period state self-heals on the next successful same-cycle Background reconciliation.
- [ ] `BillingReconciliationService` can no longer create a bare current BillingPeriod while committing a mapped ACTIVE/TRIALING Subscription.
- [ ] All four listed `BillingSubscriptionReconciliationService` Free/generic paths repair compatible existing rows instead of `update: {}` no-op.
- [ ] Paid executable periods always have exactly one matching included-credit counter.
- [ ] Existing paid usage quantities are never reset by reconciliation.
- [ ] Conflicting period history is never overwritten, reopened, stolen or replaced with an overlapping row.
- [ ] Conflicts persist `SYNC_ERROR/BILLING_PERIOD_PLAN_CONFLICT` and schedule a bounded retry.
- [ ] No database migration/backfill is introduced.
- [ ] ARCH-011 remains out of scope.

## Validation

Run:

```bash
npm run prisma:generate
npx vitest run \
  tests/unit/services/billing-reconciliation.service.test.ts \
  tests/unit/services/billing-subscription-reconciliation.service.test.ts
npm run test:unit
npm run build
git diff --check
```

If `npm run test:unit` exposes a documented unrelated baseline failure, record the exact baseline evidence in the Completion Report. Focused tests for this task must pass completely.

## Stop condition

After implementation, focused/full-unit validation and Completion Report are complete, set status to `review`, return control to `moda_architect`, and STOP.

Do not start SHOPIFY-003 or a system-test task.
