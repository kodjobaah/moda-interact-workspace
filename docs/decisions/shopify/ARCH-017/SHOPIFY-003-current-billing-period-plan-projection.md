---
id: ARCH-017-SHOPIFY-003
architecture_id: ARCH-017
title: Make Shopify subscription sync self-heal and enforce plan-complete current BillingPeriods
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-017-SHOPIFY-002
enables: []
created: 2026-09-19
updated: 2026-09-19
---

# ARCH-017-SHOPIFY-003

## Objective

Correct the current-cycle projection defect in `moda-interact` so a successful mapped Shopify subscription cannot be committed as `ACTIVE` or `TRIALING` while `Subscription.billingPeriodId` points at an OPEN `BillingPeriod` whose plan identity is missing or conflicts with `Subscription.planId`.

This task is a follow-on correction. Do **not** reopen `ARCH-017-SHOPIFY-001` and do **not** merge this work into `ARCH-017-SHOPIFY-002`.

`ARCH-017-SHOPIFY-002` owns only the Shopify callback onboarding milestone. This task owns only the current BillingPeriod projection invariant inside `BillingService.syncSubscription()`.

ARCH-011 remains out of scope. Do not add prorated plan segments or same-cycle plan changes.

## Current defect in the supplied 2026-09-19 snapshot

File:

```text
app/services/billing/billing.service.ts
```

The generic `syncSubscription()` path currently uses this exact shape:

```ts
const billingPeriod = !initialPaidProjection && providerSubscription.currentPeriodStart && providerSubscription.currentPeriodEnd
  ? await transaction.billingPeriod.upsert({
      where: {
        shopId_periodStart_periodEnd: {
          shopId,
          periodStart: providerSubscription.currentPeriodStart,
          periodEnd: providerSubscription.currentPeriodEnd,
        },
      },
      update: { status: BillingPeriodStatus.OPEN },
      create: {
        shopId,
        subscriptionId,
        planId: planIsUsable ? plan?.id ?? null : null,
        shopifyPlanHandleSnapshot: providerSubscription.planHandle,
        planNameSnapshot: plan?.name ?? null,
        planKindSnapshot: plan?.kind ?? null,
        includedRecoveryCreditsGranted: null,
        periodStart: providerSubscription.currentPeriodStart,
        periodEnd: providerSubscription.currentPeriodEnd,
        status: BillingPeriodStatus.OPEN,
      },
    })
  : null;
```

The `create` branch can contain plan information, but the `update` branch only sets `status=OPEN`. Therefore an exact provider-cycle row first created while unmapped can remain permanently null-mapped after the BillingPlan later resolves, while the Subscription is updated to the resolved plan.

The observed invalid state is:

```text
Subscription.status = ACTIVE
Subscription.planId = <free-plan-id>
Subscription.billingPeriodId = <period-id>

BillingPeriod.id = <period-id>
BillingPeriod.planId = null
BillingPeriod.shopifyPlanHandleSnapshot = null
BillingPeriod.planNameSnapshot = null
BillingPeriod.planKindSnapshot = null
```

This task must make that state impossible after a successful `syncSubscription()` commit.

## Required invariant

After `syncSubscription()` commits `ACTIVE` or `TRIALING` with non-null `planId` and `billingPeriodId`, the referenced OPEN BillingPeriod MUST satisfy all of the following:

```text
BillingPeriod.shopId == Subscription.shopId
BillingPeriod.subscriptionId == Subscription.id
BillingPeriod.planId == Subscription.planId
BillingPeriod.periodStart == Subscription.currentPeriodStart
BillingPeriod.periodEnd == Subscription.currentPeriodEnd
BillingPeriod.shopifyPlanHandleSnapshot == Subscription.observedShopifyPlanHandle
BillingPeriod.planNameSnapshot == current BillingPlan.name
BillingPeriod.planKindSnapshot == current BillingPlan.kind
```

Additional rules:

```text
FREE:
  includedRecoveryCreditsGranted == null
  no INCLUDED_RECOVERY_CREDITS BillingPeriodEntitlementCounter exists

PAID_METERED:
  includedRecoveryCreditsGranted == BillingPlan.includedRecoveryConversationAllowance
  exactly one INCLUDED_RECOVERY_CREDITS BillingPeriodEntitlementCounter exists
  counter.grantedQuantity == includedRecoveryConversationAllowance
```

The exact same OPEN provider cycle may be repaired in place only when its non-null durable fields are compatible with the resolved plan. Conflicting non-null history must never be overwritten.

## Dependency gate

Do not start until `ARCH-017-SHOPIFY-002` is architect-accepted and Complete.

This dependency is intentional because SHOPIFY-002 and this task both modify `app/services/billing/billing.service.ts`. They must execute sequentially so Luna does not implement against a stale sibling branch.

At task start:

```bash
npm run prisma:generate
```

Use the database submodule already present in the prepared task worktree. Do not modify it.

## Read before editing

Read these files completely before changing code:

```text
app/services/billing/billing.service.ts
tests/unit/services/billing.service.test.ts
database/prisma/schema.prisma
docs/architecture/ARCH-017-billing-plan-materialisation-dynamic-features.md
docs/decisions/shopify/ARCH-017/SHOPIFY-002-callback-onboarding-milestone-decoupling.md
```

Specifically inspect the existing strict initial-paid activation block in `syncSubscription()`. Reuse its conflict philosophy; do not weaken it.

## Authorized implementation surface

Production code:

```text
app/services/billing/billing.service.ts
```

Tests:

```text
tests/unit/services/billing.service.test.ts
```

Do not edit callback onboarding code in this task except for imports made unused solely by the BillingService change. Do not edit routes, Admin, Background, Shared, or the database schema.

If the correction cannot be implemented within these two files, stop and return the exact dependency to `moda_architect`.

---

# Part A — add one deterministic current-period projection helper

## A1. Add internal result/reason types

Near the existing `DurableBillingCycle` helper types in `billing.service.ts`, add internal types equivalent to:

```ts
type CurrentBillingPeriodPlan = Pick<
  BillingPlan,
  | "id"
  | "name"
  | "kind"
  | "shopifyPlanHandle"
  | "includedRecoveryConversationAllowance"
>;

type CurrentBillingPeriodProjectionConflictReason =
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

type CurrentBillingPeriodProjectionResult =
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

Do not export these types.

## A2. Add `ensureMappedCurrentBillingPeriodProjection()`

Add one private module helper in `billing.service.ts` with this exact signature:

```ts
async function ensureMappedCurrentBillingPeriodProjection(
  transaction: Prisma.TransactionClient,
  input: {
    shopId: string;
    subscriptionId: string;
    periodStart: Date;
    periodEnd: Date;
    providerPlanHandle: string;
    plan: CurrentBillingPeriodPlan;
  },
): Promise<CurrentBillingPeriodProjectionResult>
```

The helper is ONLY for a resolved plan that is about to be committed as executable `ACTIVE`/`TRIALING`. Do not call it for `UNMAPPED` or `SYNC_ERROR` projections.

Implement the algorithm below exactly.

### A2.1 Validate paid allowance before touching the period

```ts
const expectedGrant = input.plan.kind === BillingPlanKind.PAID_METERED
  ? input.plan.includedRecoveryConversationAllowance
  : null;

if (
  input.plan.kind === BillingPlanKind.PAID_METERED &&
  (
    expectedGrant === null ||
    !Number.isSafeInteger(expectedGrant) ||
    expectedGrant < 0
  )
) {
  return {
    kind: "CONFLICT",
    billingPeriodId: null,
    reason: "INVALID_INCLUDED_ALLOWANCE",
  };
}
```

### A2.2 Read exact provider cycle by existing unique key

```ts
const existingPeriod = await transaction.billingPeriod.findUnique({
  where: {
    shopId_periodStart_periodEnd: {
      shopId: input.shopId,
      periodStart: input.periodStart,
      periodEnd: input.periodEnd,
    },
  },
});
```

### A2.3 If no period exists, create the complete mapped period

Create exactly:

```ts
const createdPeriod = await transaction.billingPeriod.create({
  data: {
    shopId: input.shopId,
    subscriptionId: input.subscriptionId,
    planId: input.plan.id,
    shopifyPlanHandleSnapshot: input.providerPlanHandle,
    planNameSnapshot: input.plan.name,
    planKindSnapshot: input.plan.kind,
    includedRecoveryCreditsGranted: expectedGrant,
    periodStart: input.periodStart,
    periodEnd: input.periodEnd,
    status: BillingPeriodStatus.OPEN,
  },
});
```

If the plan is `PAID_METERED`, immediately create exactly one included-credit counter in the same transaction:

```ts
await transaction.billingPeriodEntitlementCounter.create({
  data: {
    shopId: input.shopId,
    billingPeriodId: createdPeriod.id,
    counter: BillingPeriodEntitlementCounterKind.INCLUDED_RECOVERY_CREDITS,
    grantedQuantity: expectedGrant as number,
    committedQuantity: 0,
    reservedQuantity: 0,
    forfeitedQuantity: 0,
  },
});
```

Return:

```ts
return {
  kind: "READY",
  billingPeriodId: createdPeriod.id,
  repaired: false,
};
```

### A2.4 Existing period must never be reopened or stolen

For an existing row, return `CONFLICT` without writing it when:

```text
existingPeriod.status != OPEN
existingPeriod.subscriptionId != input.subscriptionId
existingPeriod.shopifyPlanHandleSnapshot is non-null and != input.providerPlanHandle
existingPeriod.planId is non-null and != input.plan.id
existingPeriod.planNameSnapshot is non-null and != input.plan.name
existingPeriod.planKindSnapshot is non-null and != input.plan.kind
```

Use the matching stable reason from the type above.

Do not create a replacement overlapping period.

### A2.5 Missing/null projection fields on the same OPEN cycle are repairable

If every existing non-null field is compatible, update the exact existing row in place so it has the complete expected mapping:

```ts
const repairedPeriod = await transaction.billingPeriod.update({
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

This is the required self-heal for the currently observed null-mapped Free period.

### A2.6 FREE counter rule

For `BillingPlanKind.FREE`, query:

```ts
const includedCounter = await transaction.billingPeriodEntitlementCounter.findUnique({
  where: {
    billingPeriodId_counter: {
      billingPeriodId: repairedPeriod.id,
      counter: BillingPeriodEntitlementCounterKind.INCLUDED_RECOVERY_CREDITS,
    },
  },
});
```

If it exists, return `CONFLICT` with `FREE_INCLUDED_COUNTER_PRESENT`.

Do not delete it automatically.

### A2.7 PAID counter rule

For `PAID_METERED`, read the same counter key.

If no counter exists, create it with exactly:

```text
grantedQuantity = expectedGrant
committedQuantity = 0
reservedQuantity = 0
forfeitedQuantity = 0
```

If a counter exists, it is compatible only when:

```text
counter.shopId == input.shopId
counter.grantedQuantity == expectedGrant
all four quantities are safe integers >= 0
committedQuantity + reservedQuantity + forfeitedQuantity <= grantedQuantity
```

If incompatible, return `CONFLICT` with `PAID_COUNTER_MISMATCH` and do not rewrite quantities.

Do not reset committed/reserved/forfeited usage during replay.

### A2.8 Return repair status

Return `repaired=true` when an existing BillingPeriod had any missing expected projection field or the paid included counter had to be created.

Otherwise return `repaired=false` for an already-consistent replay.

---

# Part B — use the helper only for executable mapped generic sync

## B1. Add paid allowance validation to generic status selection

Immediately after current `paidMeterIsPresent`, add:

```ts
const paidAllowanceIsValid = plan?.kind !== BillingPlanKind.PAID_METERED
  || (
    plan.includedRecoveryConversationAllowance !== null &&
    Number.isSafeInteger(plan.includedRecoveryConversationAllowance) &&
    plan.includedRecoveryConversationAllowance >= 0
  );
```

Change status calculation to:

```ts
const status = !planIsUsable
  ? SubscriptionProjectionStatus.UNMAPPED
  : !paidMeterIsPresent || !paidAllowanceIsValid
    ? SubscriptionProjectionStatus.SYNC_ERROR
    : providerSubscription.status === "TRIALING"
      ? SubscriptionProjectionStatus.TRIALING
      : SubscriptionProjectionStatus.ACTIVE;
```

Change `syncErrorCode` to:

```ts
const syncErrorCode = status === SubscriptionProjectionStatus.UNMAPPED
  ? "UNMAPPED_PLAN_HANDLE"
  : status === SubscriptionProjectionStatus.SYNC_ERROR
    ? !paidMeterIsPresent
      ? "MISSING_USAGE_METER"
      : "INVALID_INCLUDED_ALLOWANCE"
    : null;
```

Do not change initial-paid activation semantics; its stricter branch remains authoritative when `initialPaidActivation=true`.

## B2. Extend the locked Subscription read

In the generic transaction, extend `existingSubscription` select to include:

```ts
billingPeriodId: true,
currentPeriodStart: true,
currentPeriodEnd: true,
```

Do not remove the existing selected fields.

## B3. Replace the generic mapped ACTIVE/TRIALING BillingPeriod upsert

Keep the current `initialPaidProjection` exclusion.

When all are true:

```text
!initialPaidProjection
providerSubscription.currentPeriodStart != null
providerSubscription.currentPeriodEnd != null
status is ACTIVE or TRIALING
plan != null
plan.active == true
```

call:

```ts
const projection = await ensureMappedCurrentBillingPeriodProjection(transaction, {
  shopId,
  subscriptionId,
  periodStart: providerSubscription.currentPeriodStart,
  periodEnd: providerSubscription.currentPeriodEnd,
  providerPlanHandle: providerSubscription.planHandle,
  plan,
});
```

If `projection.kind === "READY"`, use `projection.billingPeriodId` when writing the Subscription.

## B4. Conflict handling is fail-closed and must not overwrite history

If `projection.kind === "CONFLICT"`:

1. do not modify the BillingPeriod further;
2. do not create another BillingPeriod for the same dates;
3. do not advance a previously-null Subscription `planId` to the resolved plan;
4. preserve any existing `planId`, `billingPeriodId`, `currentPeriodStart`, and `currentPeriodEnd` from the locked Subscription row;
5. write:

```text
status = SYNC_ERROR
lastSyncErrorCode = BILLING_PERIOD_PLAN_CONFLICT
lastSyncErrorAt = now
lastSyncedAt = now
```

6. preserve the existing pending-intent fields using the same rules already calculated by the method;
7. return the resulting Subscription.

Log only the bounded `projection.reason`; do not persist it into `lastSyncErrorCode`.

## B5. Non-executable projections stay non-entitled

For `UNMAPPED` or `SYNC_ERROR` caused by provider/plan configuration before current-period projection succeeds:

- do not create a paid included-credit counter;
- do not call `ensureMappedCurrentBillingPeriodProjection()`;
- preserve existing generic provider-observation behaviour;
- an unmapped OPEN period may remain plan-null and later be self-healed when the same exact cycle becomes executable.

Do not grant paid entitlement while status is `UNMAPPED` or `SYNC_ERROR`.

## B6. Subscription and mapped BillingPeriod must commit atomically

The helper call and the final Subscription upsert/update MUST remain inside the same existing `database.$transaction()` callback.

A successful `ACTIVE`/`TRIALING` commit must never expose a mapped Subscription with an incomplete current period.

---

# Required focused tests

Add tests to `tests/unit/services/billing.service.test.ts` that prove all of the following.

1. **Observed Free self-heal**: an exact OPEN period exists with the same shop/subscription/cycle and all plan fields null. A successful sync for active Free reuses the same period ID and fills `planId`, handle, name, kind; included grant remains null; Subscription becomes ACTIVE and points to the same period.
2. **Free replay**: already-correct Free period remains unchanged and no included counter is created.
3. **Paid self-heal**: exact OPEN period exists plan-null; successful paid sync fills plan snapshots and included grant and creates one included counter with zero committed/reserved/forfeited quantities.
4. **Paid replay preserves usage**: existing correct paid counter with non-zero committed/reserved/forfeited values is not reset.
5. **Missing paid counter repair**: mapped correct paid period with no included counter gets exactly one counter without replacing the period.
6. **Closed-period conflict**: exact cycle is CLOSED; sync writes Subscription `SYNC_ERROR/BILLING_PERIOD_PLAN_CONFLICT`, does not reopen it and does not create an overlapping period.
7. **Different-plan conflict**: exact OPEN period has another non-null plan; sync fails closed and leaves period history unchanged.
8. **Subscription mismatch conflict**: exact cycle belongs to a different Subscription; sync fails closed and does not steal it.
9. **Invalid paid allowance**: active paid plan with null/negative/non-integer included allowance produces `SYNC_ERROR/INVALID_INCLUDED_ALLOWANCE` and creates no included counter.
10. **UNMAPPED does not grant entitlement**: unknown plan handle does not invoke mapped-period entitlement creation.
11. **Later resolution repairs same row**: first sync leaves an unmapped exact cycle; after a BillingPlan exists, a later sync repairs the same BillingPeriod ID rather than creating another period.
12. **No regression to initial-paid activation**: existing strict initial-paid tests continue to pass.

Do not mock away the period/counter compatibility checks in the new tests.

## Acceptance criteria

- [ ] No successful generic `ACTIVE`/`TRIALING` sync can point to a current OPEN BillingPeriod whose plan identity is null.
- [ ] The exact observed Free null-mapped period is self-healed in place on the next successful same-cycle sync.
- [ ] Paid same-cycle repair creates the included-credit counter exactly once.
- [ ] Existing paid usage quantities are never reset during replay.
- [ ] Conflicting durable period history is never overwritten or replaced by an overlapping row.
- [ ] Conflicts project `SYNC_ERROR/BILLING_PERIOD_PLAN_CONFLICT`.
- [ ] UNMAPPED/SYNC_ERROR paths do not grant paid entitlement.
- [ ] SHOPIFY-002 onboarding behaviour is unchanged.
- [ ] ARCH-011 remains absent.

## Validation

Run exactly the repository-supported commands:

```bash
npm run prisma:generate
npx vitest run tests/unit/services/billing.service.test.ts
npm run typecheck
npm run lint -- --no-cache app/services/billing/billing.service.ts tests/unit/services/billing.service.test.ts
npm run build
git diff --check
```

If the repository lint command does not accept file arguments in this form, use the existing repository-supported changed-file ESLint invocation and record the exact command in the Completion Report. Do not invent a new package script merely for this task.

## Stop condition

After the defined work, focused tests and required validation pass, complete the task Completion Report, set the task to `review`, return control to `moda_architect`, and STOP.

Do not begin any Background or system-test task.
