---
id: ARCH-015-SHOPIFY-002
architecture_id: ARCH-015
title: Recovery-credit purchase admission, provenance and single-flight creation
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-015-SHARED-001
- ARCH-015-DATABASE-001
- ARCH-015-SHOPIFY-001
enables:
- ARCH-015-BACKGROUND-001
- ARCH-015-SHOPIFY-003
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-015-SHOPIFY-002

## Objective

Make a merchant-selected resolved offer create exactly one durable REQUESTED purchase with immutable provider-before evidence, while preserving asynchronous App Event publication.

Do NOT call the Shopify App Events HTTP endpoint directly from the web request. Continue creating a PENDING `UsageEvent`; the existing Background publisher owns submission.

## Authorized implementation surface

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/routes/app/billing/options/route.tsx
app/components/dashboard/TopUpPurchasePanel.jsx
# ARCH-015/ARCH-014 offer resolver files from SHOPIFY-001
tests/unit/services/billing.service.test.ts
tests/unit/billing-ui.test.ts
tests/unit/*topup*.test.*
```

No database schema edits.

## Request contract

Merchant form/action may submit only:

```text
intent = BUY_RECOVERY_CREDIT_PACK
purchaseId = valid UUID
eventHandle = selected offer handle
```

Do not trust browser values for:

```text
creditsGranted
price
currency
planId
provider quantity/cost
provider context
billing period
```

## Exact server sequence

For a new purchase:

1. validate intent/UUID/eventHandle;
2. authenticate/resolve exact shop;
3. replay same `purchaseId` if already present for same shop;
4. obtain a fresh Shopify active subscription;
5. require ACTIVE/TRIALING executable contract under current existing rules;
6. resolve current provider plan handle;
7. verify selected `eventHandle` is present in live provider usage items;
8. resolve ARCH-014 plan by current provider plan handle;
9. resolve selected ARCH-014 usage event under that plan;
10. set `creditsGranted = creditsGrantedPerUnit`;
11. capture provider usage quantity/cost/currency BEFORE;
12. derive provider context identity through published Shared helper;
13. verify exact current local open BillingPeriod/cycle;
14. start Serializable transaction;
15. lock the current Subscription row `FOR UPDATE` using existing safe pattern;
16. re-read/revalidate current subscription/plan/billing period;
17. replay same purchase id if transaction sees it;
18. find unresolved purchase using EXACT scope:

```text
shopId
status = REQUESTED
shopifyEventHandleSnapshot = selected eventHandle
```

Do NOT include billingPeriodId/providerSubscriptionId/planId in the single-flight lookup.

19. if unresolved row exists, reject with the existing bounded awaiting-confirmation merchant outcome;
20. create one `UsageEvent`:
   - metric `RECOVERY_CREDIT_PACK_PURCHASE`
   - quantity Decimal `1`
   - selected event handle
   - current billingPeriodId
   - PENDING report state
   - deterministic idempotency from shop + purchase identity
21. create `RecoveryCreditPurchase` with:
   - operational current planId for provenance relation only;
   - current billingPeriodId;
   - provider plan handle snapshot;
   - selected event handle snapshot;
   - derived provider context identity in existing `providerSubscriptionIdSnapshot`;
   - Decimal quantity-before;
   - provider cost/currency-before;
   - provider live price snapshot;
   - ARCH-014 `creditsGrantedPerUnit`;
   - currentAmount=0/status REQUESTED;
22. commit;
23. return pending purchase state.

## Revalidation rule

The provider/ARCH-014 configuration must be rechecked immediately before transaction write. If provider plan/meter/credits mapping changed from the pre-transaction evidence, abort and create nothing.

Do not read singular BillingPlan pack configuration for validation.

## Native App Pricing

A null Shopify `legacySubscriptionId` is valid when Shared can derive provider context from plan + exact cycle.

Do not reject merely because providerSubscriptionId is null.

Do not write fabricated derived identity into `Subscription.providerSubscriptionId`; use it only in purchase provenance.

## Concurrency requirements

- same shop + same eventHandle genuine simultaneous new purchases => only one new REQUESTED row;
- same purchaseId replay => return same row;
- same shop + different event handles may create independent REQUESTED rows;
- unique/idempotency races must replay safely, not duplicate.

## Required tests

Include exact tests for:

- Bronze/Silver/Gold selection passes selected handle;
- browser-supplied fake credits/price are ignored/not accepted;
- credits come from ARCH-014 exact plan+event;
- live provider meter required;
- null legacy id succeeds via Shared fallback identity;
- fractional provider-before quantity can be persisted;
- same purchaseId replay;
- concurrent same handle single-flight;
- existing REQUESTED from previous billing period still blocks same handle;
- existing REQUESTED from previous provider id still blocks same handle;
- different handle not blocked;
- no App Events HTTP call from web task;
- one PENDING UsageEvent + one REQUESTED purchase created atomically;
- no use of singular BillingPlan top-up fields.

## Stop conditions

STOP if:

- implementing exact single-flight requires a new lock table/unique index rather than existing row lock + durable REQUESTED row;
- exact provider before quantity cannot be stored after DATABASE-001;
- ARCH-014 returns ambiguous duplicate event handles for the resolved plan;
- purchase creation requires direct App Events network submission.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

### Status

Implementation complete for attempt 2. Return to `moda_architect` for review.

### Physical Worktree Isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-SHOPIFY-002` on `task/ARCH-015-SHOPIFY-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-SHOPIFY-002` on `task/ARCH-015-SHOPIFY-002`.
- Shared/default checkout switched or mutated: no.
- Another task worktree reused: no.

### Physical Worktree Isolation

- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-SHOPIFY-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-SHOPIFY-002`.
- Implementation branch: `task/ARCH-015-SHOPIFY-002`.
- Shared/default checkout switched or mutated: no.

### Attempt 2 Evidence

- Launcher claim commit: `f6484b0`.
- Database submodule: `f202931c58dba7f9fcc53c74333736e978e8b6de`.
- Shared package: `@modainteract/moda-interact-shared` `^0.11.2`, lockfile `0.11.2`.
- Implementation commit: `91717c0`.
- Implementation pushed to `origin/task/ARCH-015-SHOPIFY-002`.

### Implementation Summary

- Accepts only the selected `eventHandle` from the merchant form and resolves credits from the current ARCH-014 MerchantPricing plan/event.
- Verifies the selected live Shopify usage meter, provider cycle, and provider-before quantity/cost/currency.
- Uses the Shared provider context identity helper, including the valid null legacy subscription fallback.
- Revalidates provider and MerchantPricing configuration before the serializable transaction write.
- Uses exact shop/status/event-handle single-flight scope and preserves atomic PENDING UsageEvent plus REQUESTED purchase creation.
- Adds per-offer POST forms and focused service/UI coverage; no direct App Events HTTP call was added.

### Validation Evidence

- `npm test -- --run tests/unit/billing-purchase-hub.test.tsx tests/unit/billing-ui.test.ts tests/unit/services/billing.service.test.ts`: passed, 3 files / 210 tests.
- `npm run build`: passed, including Prisma client generation and client/SSR bundles.
- `git diff --check`: passed.
- `npm run lint`: not clean because of 16 pre-existing errors in unrelated dashboard/routes/provider/test files; the touched test file has only existing duplicate-import warnings.
- `npm run typecheck`: not clean because of existing broad JavaScript implicit-any and unrelated route errors; no task-specific validation was isolated by the repository command.

### Completion Report Status

Review requested; claim cleared. Return to `moda_architect` and stop. No merge to `main` was performed.
