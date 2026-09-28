---
id: ARCH-017-BACKGROUND-003
architecture_id: ARCH-017
title: Prioritize operator-requested subscription reconciliation in the global billing scan
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-017-BACKGROUND-002
enables:
  - ARCH-017-ADMIN-002
created: 2026-09-19
updated: 2026-09-19
---

# ARCH-017-BACKGROUND-003

## Objective

Make an operator-requested subscription reconciliation execute on the next global billing-reconciliation cycle by prioritizing ACTIVE shops whose `Subscription.nextReconcileAt <= now`.

This task MUST reuse the existing authoritative provider flow in `BillingReconciliationService`:

```text
getSubscriptionReconciliationSnapshot(...)
    -> applySubscription(...)
```

Do NOT add a second generic provider-reconciliation implementation to `BillingSubscriptionReconciliationService`.
Do NOT add a new queue contract, database field, API endpoint, Redis key or cross-service HTTP call.
Do NOT change subscription state directly merely because an operator requested reconciliation.

`ARCH-017-BACKGROUND-002` is a required prerequisite because manual reconciliation must not re-create or preserve an internally inconsistent current BillingPeriod.

## Current code that motivates this task

`src/services/billing-reconciliation.service.ts` already performs the broad provider reconciliation required by this feature. `reconcileOnce()`:

```text
1. selects ACTIVE Shopify shops;
2. calls getSubscriptionReconciliationSnapshot(partner, shop.shopifyShopId);
3. calls applySubscription(shop.id, snapshot, runtimeConfig);
4. preserves Shopify as the authority for the resulting projection.
```

However, `selectRotatingShopPage()` currently selects only by the in-memory rotating `shop.id` cursor. Setting `Subscription.nextReconcileAt = now` therefore does not guarantee that the requested shop is selected on the next billing cycle.

The targeted `BillingSubscriptionReconciliationService.reconstruct()` also intentionally supports only specialized lifecycle states. Do NOT broaden that worker into a second general reconciliation engine for this task.

## Read before editing

Read these exact files before changing code:

```text
src/services/billing-reconciliation.service.ts
src/services/billing-subscription-reconciliation.service.ts
src/entrypoints/billing.ts
tests/unit/services/billing-reconciliation.service.test.ts
database/prisma/schema.prisma
docs/architecture/ARCH-017-billing-plan-materialisation-dynamic-features.md
docs/decisions/background/ARCH-017/BACKGROUND-002-current-billing-period-plan-projection.md
```

Also inspect `package.json` and use only repository-declared validation scripts.

## Authorized implementation surface

```text
src/services/billing-reconciliation.service.ts
tests/unit/services/billing-reconciliation.service.test.ts
```

`package.json` / lockfile may be changed only if a focused test script is genuinely required. No database submodule edits are authorized.

## Exact behavior

### 1. `Subscription.nextReconcileAt` remains the durable request timestamp

No schema change is required.

Admin will request reconciliation by setting:

```text
Subscription.nextReconcileAt = request timestamp
```

Background MUST treat a subscription whose `nextReconcileAt <= now` as due and prioritize its shop in the next `BillingReconciliationService.reconcileOnce()` scan.

The global scan remains authoritative for the outcome. It may leave the Subscription ACTIVE/TRIALING, move it to NO_CONTRACT/UNMAPPED/SYNC_ERROR/FROZEN, repair it, or schedule a later retry based solely on live Shopify/provider state and the existing projection rules.

### 2. Replace `selectRotatingShopPage()` with due-first + rotation-fill selection

Keep the method private and keep its return shape unchanged.

The method MUST follow this algorithm exactly:

```text
limit = validated caller limit
now = this.now()

A. query due shops first:
   Shop.status = ACTIVE
   Shop.shopifyShopId IS NOT NULL
   Shop.subscription.nextReconcileAt <= now
   order by Shop.id ASC
   take limit

B. if due shops fill the whole batch:
   return due shops
   DO NOT move the ordinary rotation cursor

C. otherwise calculate remaining = limit - dueShops.length

D. fill remaining places from the existing rotating ACTIVE-shop scan,
   excluding every due shop already selected.

E. advance `lastScannedShopId` using only the last shop returned by the
   ordinary rotating portion, never from a due-priority shop.

F. return [...dueShops, ...rotatingShops]
```

The intent is:

- due/manual work is not delayed behind the rotation cursor;
- due shops are not duplicated in the same batch;
- ordinary reconciliation continues to make progress when capacity remains;
- a due-only batch does not make the normal cursor skip shops that were never scanned.

### 3. Use this exact implementation shape

Adapt naming only where TypeScript inference requires it; do not redesign the algorithm.

```ts
private async selectRotatingShopPage(limit: number) {
  const now = this.now();
  const baseWhere = {
    shopifyShopId: { not: null },
    status: "ACTIVE" as const,
  };
  const select = { id: true, shopifyShopId: true } as const;

  const dueShops = await this.database.shop.findMany({
    where: {
      ...baseWhere,
      subscription: {
        is: {
          nextReconcileAt: { lte: now },
        },
      },
    },
    orderBy: { id: "asc" },
    take: limit,
    select,
  });

  if (dueShops.length >= limit) {
    return dueShops;
  }

  const dueIds = dueShops.map((shop) => shop.id);
  const remaining = limit - dueShops.length;
  const exclusion = dueIds.length > 0 ? { notIn: dueIds } : {};

  const afterCursor = this.lastScannedShopId
    ? await this.database.shop.findMany({
        where: {
          ...baseWhere,
          id: {
            gt: this.lastScannedShopId,
            ...exclusion,
          },
        },
        orderBy: { id: "asc" },
        take: remaining,
        select,
      })
    : [];

  const rotatingShops =
    afterCursor.length > 0
      ? afterCursor
      : await this.database.shop.findMany({
          where: {
            ...baseWhere,
            ...(dueIds.length > 0
              ? { id: { notIn: dueIds } }
              : {}),
          },
          orderBy: { id: "asc" },
          take: remaining,
          select,
        });

  const lastRotatingShop = rotatingShops.at(-1);
  if (lastRotatingShop) {
    this.lastScannedShopId = lastRotatingShop.id;
  }

  return [...dueShops, ...rotatingShops];
}
```

If Prisma's generated input type rejects the local `exclusion` spread, write the same two query shapes explicitly. The observable algorithm above is mandatory.

### 4. Do not add status-specific reconciliation code

Do NOT special-case `ACTIVE`, `TRIALING`, `SYNC_ERROR`, `FROZEN`, `NO_CONTRACT` or `UNMAPPED` inside `selectRotatingShopPage()`.

A due timestamp means the shop is selected. `applySubscription()` and the existing lifecycle services decide the result from live provider state.

This also intentionally benefits the existing `UNMAPPED` repair flow, which already sets `nextReconcileAt` after a successful mapping repair.

### 5. Do not clear or rewrite request state in the selector

`selectRotatingShopPage()` MUST NOT mutate:

```text
Subscription.nextReconcileAt
Subscription.status
Subscription.planId
Subscription.billingPeriodId
Subscription.lastSyncErrorCode
Subscription.lastSyncErrorAt
```

The existing reconciliation implementation owns all post-attempt scheduling and projection changes.

## Required tests

Update `tests/unit/services/billing-reconciliation.service.test.ts` with focused tests proving all of the following.

1. A shop with `nextReconcileAt <= now` is selected before a normal shop even when the normal rotation cursor would otherwise select the other shop first.
2. A future `nextReconcileAt` is NOT considered due.
3. Due shops are not duplicated when the rotating fill query runs.
4. If due shops consume the entire batch, `lastScannedShopId` is not advanced from a due shop.
5. If due shops consume only part of the batch, normal rotating shops fill the remaining capacity.
6. The cursor advances from the final rotating shop when a rotating portion exists.
7. With no due shops, behavior remains equivalent to the previous rotating scan.
8. A due UNMAPPED subscription is eligible for global scan selection; the selector does not filter it by subscription status.
9. A due SYNC_ERROR subscription is eligible for global scan selection.
10. A due NO_CONTRACT subscription is eligible for global scan selection.

Use mocked Prisma calls consistent with the existing test style. Do not require a live Shopify call merely to test selection priority.

## Acceptance Criteria

- [ ] No database/schema change was introduced.
- [ ] No new queue/event contract was introduced.
- [ ] Due subscription reconciliation requests are selected on the next global billing scan regardless of rotation cursor position.
- [ ] Normal rotating reconciliation still fills unused batch capacity.
- [ ] A due request does not directly mutate subscription projection state.
- [ ] Existing provider reconciliation remains the sole authority for the resulting Subscription/BillingPeriod state.
- [ ] Existing UNMAPPED repair scheduling benefits from the due-priority path without a separate implementation.
- [ ] Focused tests cover due selection, cursor behavior and status-agnostic eligibility.
- [ ] Required repository validation passes.

## Validation

Run the repository-declared commands after inspecting `package.json`. At minimum:

- [ ] focused `billing-reconciliation.service` unit tests
- [ ] TypeScript/typecheck command declared by the repository, if present
- [ ] lint command declared by the repository, if present
- [ ] production build command declared by the repository, if present/required by current repository validation convention
- [ ] `git diff --check`

Do not invent unavailable scripts.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

1. update this task's Completion Report;
2. set `status: review`;
3. return control to `moda_architect`;
4. STOP.

Do not implement `ARCH-017-ADMIN-002` or any other task.
