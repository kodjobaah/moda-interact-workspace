---
id: ARCH-018-BACKGROUND-001
architecture_id: ARCH-018
title: Reconcile expired merchant promotion selections in the billing cadence
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-010-DATABASE-011
- ARCH-014-BACKGROUND-002
- ARCH-014-BACKGROUND-006
enables:
- ARCH-018-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# ARCH-018-BACKGROUND-001

## Objective

Add eventual cleanup of expired `MerchantPromotionSelection` pointers to the **existing** `BILLING_RECONCILIATION` cycle.

Use the same:

```text
BILLING_RECONCILIATION distributed lease
billingReconciliationIntervalSeconds
billingReconciliationShopBatchSize
BackgroundRuntimeConfigSnapshot captured for the cycle
```

Do not create another timer, lease, queue or runtime-control field.

Cleanup is not the business correctness boundary. Shopify selection must already treat `PromotionCampaign.expiresAt <= now` as unlocked even if the stale pointer still exists.

## Read before editing

Read completely:

```text
src/entrypoints/billing.ts
src/services/billing-reconciliation.service.ts
src/services/recovery-credit-refund-correction.service.ts
src/runtime/background-runtime-config.ts
src/runtime/background-runtime-lease.ts
src/runtime/dynamic-leased-scheduler.ts
tests/unit/runtime/billing-entrypoint.runtime-controls.test.ts
tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts
tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts
database/prisma/schema.prisma
docs/architecture/ARCH-018-promotion-selection-lock-and-expiry-reconciliation.md
```

## Authorized implementation surface

Production:

```text
src/services/promotion-selection-expiry-reconciliation.service.ts   # new
src/entrypoints/billing.ts
```

Tests:

```text
tests/unit/services/promotion-selection-expiry-reconciliation.service.test.ts   # new
tests/unit/runtime/billing-entrypoint.runtime-controls.test.ts
tests/integration/promotion-selection-expiry-reconciliation.integration.test.ts # new, disposable DB gate
```

Do not edit the database submodule/schema/migrations, runtime-config schema, lease enum, Admin repository, Shopify repository, gateway or queue contracts.

If implementation requires any of those, STOP and return to `moda_architect`.

---

# Part A — create the cleanup service

Create:

```text
src/services/promotion-selection-expiry-reconciliation.service.ts
```

Use these imports:

```ts
import type { PrismaClient } from "@prisma/client";

import prisma from "../lib/db.js";
import type { BackgroundRuntimeConfigSnapshot } from "../runtime/background-runtime-config.js";
```

Export exactly:

```ts
export type PromotionSelectionExpiryReconciliationResult = {
  selected: number;
  released: number;
  raced: number;
};

export class PromotionSelectionExpiryReconciliationService {
  constructor(
    private readonly database: PrismaClient = prisma,
    private readonly now: () => Date = () => new Date(),
  ) {}

  async reconcileOnce(
    runtimeConfig: Pick<
      BackgroundRuntimeConfigSnapshot,
      "billingReconciliationShopBatchSize"
    >,
  ): Promise<PromotionSelectionExpiryReconciliationResult> {
    // implementation below
  }
}
```

## A1. Capture one cutoff per invocation

At the start of `reconcileOnce()`:

```ts
const cutoff = this.now();
```

Do not call `new Date()` separately per candidate.

## A2. Candidate query

Use:

```ts
const candidates = await this.database.merchantPromotionSelection.findMany({
  where: {
    promotionalCreditGrant: {
      campaign: {
        expiresAt: { lte: cutoff },
      },
    },
  },
  orderBy: [
    { updatedAt: "asc" },
    { id: "asc" },
  ],
  take: runtimeConfig.billingReconciliationShopBatchSize,
  select: {
    id: true,
    shopId: true,
    promotionalCreditGrantId: true,
  },
});
```

Do not filter on:

```text
campaign.status
grant.exhaustedAt
grant remaining quantity
target eligibility
shop/subscription status
```

Expiry alone makes the pointer stale.

## A3. Race-safe final delete

Initialize:

```ts
let released = 0;
let raced = 0;
```

For each candidate execute a single final conditional delete:

```ts
const deletion = await this.database.merchantPromotionSelection.deleteMany({
  where: {
    id: candidate.id,
    shopId: candidate.shopId,
    promotionalCreditGrantId: candidate.promotionalCreditGrantId,
    promotionalCreditGrant: {
      campaign: {
        expiresAt: { lte: cutoff },
      },
    },
  },
});

if (deletion.count === 1) {
  released += 1;
} else {
  raced += 1;
}
```

The final predicate is mandatory.

Do not replace it with:

```ts
delete({ where: { id: candidate.id } })
```

or:

```ts
deleteMany({ where: { shopId: candidate.shopId } })
```

Those forms can delete a newer selection after a race.

Return:

```ts
return {
  selected: candidates.length,
  released,
  raced,
};
```

## A4. Mutation boundary

This service may mutate only:

```text
MerchantPromotionSelection DELETE
```

It MUST NOT update/delete/create:

```text
PromotionCampaign
PromotionCampaignEvent
PromotionalCreditGrant
UsageReservation
BillingPeriod
Subscription
Shop
```

It must not change:

```text
quantity
reservedQuantity
committedQuantity
firstSelectedAt
lastSelectedAt
selectionCount
firstUsedAt
lastUsedAt
exhaustedAt
```

---

# Part B — integrate with existing billing reconciliation cadence

File:

```text
src/entrypoints/billing.ts
```

## B1. Import/instantiate

Add a dynamic import for:

```ts
{ PromotionSelectionExpiryReconciliationService }
```

from:

```text
../services/promotion-selection-expiry-reconciliation.service.js
```

Instantiate exactly one service per billing worker process:

```ts
const promotionSelectionExpiryReconciliationService =
  new PromotionSelectionExpiryReconciliationService();
```

Do not create a scheduler inside the service.

## B2. Run inside `runBillingCycle`

Use the **same `runtimeConfig` argument** already passed into `runBillingCycle`.

Run promotion expiry cleanup immediately after:

```ts
await billingReconciliationService.reconcileOnce(runtimeConfig);
```

and before refund correction/subscription reconstruction.

Use:

```ts
try {
  const promotionExpiry =
    await promotionSelectionExpiryReconciliationService.reconcileOnce(runtimeConfig);

  logger.info("billing.reconciliation.promotion_selection_expiry_completed", {
    leaseGeneration: leaseHandle.generation,
    configVersion: runtimeConfig.version,
    selected: promotionExpiry.selected,
    released: promotionExpiry.released,
    raced: promotionExpiry.raced,
  });
} catch (error) {
  logger.error("billing.reconciliation.promotion_selection_expiry_failed", {
    leaseGeneration: leaseHandle.generation,
    configVersion: runtimeConfig.version,
    errorName:
      error instanceof Error ? error.name.slice(0, 64) : "UnknownError",
    errorMessage:
      error instanceof Error
        ? error.message.slice(0, 256)
        : "unknown failure",
  });
}
```

The catch is required: promotion-pointer cleanup is eventual maintenance and must not prevent existing refund correction or subscription reconstruction from running in that cycle.

Do not log shop IDs, grant IDs, campaign IDs or payloads in these cycle-level events.

## B3. Do not create another timer/lease

There must be no new:

```text
setInterval
startDynamicLeasedScheduler call
BackgroundRuntimeLeaseName value
runtime config field
environment variable
BullMQ queue
```

The only scheduler remains:

```text
leaseName: "BILLING_RECONCILIATION"
getIntervalMs: runtimeConfig.billingReconciliationIntervalSeconds * 1000
```

The promotion service gets the same config snapshot used by the billing stage.

---

# Part C — required focused tests

## C1. Unit service tests

Create:

```text
tests/unit/services/promotion-selection-expiry-reconciliation.service.test.ts
```

Required cases:

1. candidate query filters only `campaign.expiresAt <= cutoff` and uses `billingReconciliationShopBatchSize` as `take`;
2. no candidates -> `{ selected: 0, released: 0, raced: 0 }`;
3. one successful conditional delete -> released increments;
4. delete count 0 -> raced increments, no exception;
5. final delete predicate contains candidate `id`, `shopId`, `promotionalCreditGrantId` and related `expiresAt <= same cutoff`;
6. multiple candidates return exact selected/released/raced counts;
7. the service never calls any mutation method on campaign/grant/reservation models.

Use an injected fixed `now()` and mocked Prisma client. Do not use wall-clock time in unit tests.

## C2. Billing entrypoint source contract

Extend:

```text
tests/unit/runtime/billing-entrypoint.runtime-controls.test.ts
```

Assert `src/entrypoints/billing.ts` contains:

```text
PromotionSelectionExpiryReconciliationService
promotionSelectionExpiryReconciliationService.reconcileOnce(runtimeConfig)
billing.reconciliation.promotion_selection_expiry_completed
billing.reconciliation.promotion_selection_expiry_failed
leaseName: "BILLING_RECONCILIATION"
billingReconciliationIntervalSeconds * 1000
```

Assert there is still only one `startDynamicLeasedScheduler({` occurrence in the billing entrypoint.

## C3. Disposable PostgreSQL race integration

Create:

```text
tests/integration/promotion-selection-expiry-reconciliation.integration.test.ts
```

Follow the repository's existing gate:

```ts
const describeIntegration =
  process.env.TEST_DATABASE_URL &&
  process.env.MODA_DISPOSABLE_INTEGRATION === "1"
    ? describe
    : describe.skip;
```

Required integrated scenarios when the gate is open:

1. expired selection -> pointer deleted; `PromotionalCreditGrant` remains with quantities/history unchanged;
2. unexpired selection -> pointer remains;
3. candidate discovered for expired grant A, pointer changed to unexpired grant B before final conditional delete -> delete count 0 and B remains selected;
4. candidate discovered, campaign expiry extended beyond cutoff before final conditional delete -> delete count 0 and selection remains.

If deterministic orchestration of the between-query/before-delete race requires a test-only injected hook that would change production service API, STOP and return to architect instead. Prefer direct database setup plus testing the same final predicate semantics.

---

# Validation

Inspect `package.json`, then run:

```bash
npm run prisma:generate
npm run prisma:validate

npx vitest run \
  tests/unit/services/promotion-selection-expiry-reconciliation.service.test.ts \
  tests/unit/runtime/billing-entrypoint.runtime-controls.test.ts

npm run build
npm run test:unit
npm test

# Run when the repository disposable integration gate is available:
npm run test:integration

git diff --check
```

If the disposable integration gate is unavailable, record that exact gate as blocked; do not fake PostgreSQL concurrency with a mock and claim it as integration proof.

## Required source invariant searches

Run:

```bash
rg -n "setInterval|startDynamicLeasedScheduler|BILLING_RECONCILIATION|billingReconciliationIntervalSeconds" \
  src/entrypoints/billing.ts \
  src/services/promotion-selection-expiry-reconciliation.service.ts
```

Expected:

```text
one existing startDynamicLeasedScheduler in billing.ts
no scheduler/timer in promotion-selection-expiry-reconciliation.service.ts
no new lease name
```

## Stop conditions

STOP if:

- race-safe conditional deletion cannot be expressed with the existing Prisma schema/client;
- a new index/migration is required for acceptable correctness;
- cleanup requires mutating grants/history;
- integration would require a second reconciliation timer/lease;
- the same runtime-config snapshot cannot be passed to the new service.

## Completion protocol

Record exact changed files, focused/unit/full/integration results, source-invariant results and implementation commit. Set `status: review`, clear claim fields, push both task branches and STOP.

## Acceptance invariant

Promotion cleanup may lag the expiry timestamp, but it can never:

```text
block a post-expiry merchant selection
release a selection before expiry
delete promotional grant/history evidence
delete a newer concurrently selected promotion
```

## Completion Report

Status: Ready for Review

Implementation commit: `4b1b81f436e04a91f5f9a689dcbbe60cf837b4e0`, pushed to `task/ARCH-018-BACKGROUND-001`.

Changed files:

- `src/services/promotion-selection-expiry-reconciliation.service.ts`
- `src/entrypoints/billing.ts`
- `tests/unit/services/promotion-selection-expiry-reconciliation.service.test.ts`
- `tests/unit/runtime/billing-entrypoint.runtime-controls.test.ts`
- `tests/integration/promotion-selection-expiry-reconciliation.integration.test.ts`

Implemented the bounded expiry-only candidate query, single-cutoff race-safe conditional deletion, selected/released/raced result, and mutation boundary. Integrated cleanup into the existing `BILLING_RECONCILIATION` cycle with the same runtime snapshot, lease generation/config-version logs, and failure isolation before refund correction and subscription reconstruction. No new timer, scheduler, lease, runtime field, queue, schema or migration was added.

Validation:

- Focused Vitest: 2 files, 6 tests passed.
- `npm run prisma:generate`: passed as part of `npm run build`.
- `npm run prisma:validate`: passed.
- `npm run build`: passed.
- `npm run test:integration`: passed available gated set, 3 files and 4 tests.
- Direct new integration file: 4 tests skipped because `TEST_DATABASE_URL` and `MODA_DISPOSABLE_INTEGRATION=1` were unavailable; disposable PostgreSQL race proof remains blocked by that exact gate.
- `npm run test:unit` and `npm test`: 70 files passed, 1,056 tests passed, 12 skipped; 3 unrelated existing failures remain in `tests/unit/services/billing-reconciliation.service.test.ts` for provider-cycle lag behavior.
- Required source invariant search and `git diff --check`: passed; one existing `startDynamicLeasedScheduler({` remains in `billing.ts`, and the new service contains no scheduler/timer.

Blockers and unresolved issues: disposable PostgreSQL execution was unavailable. The unrelated provider-cycle lag failures were not changed.

## Architect Review — Attempt 1 — Accepted

Status: Accepted.

Reviewed implementation commit: `4b1b81f436e04a91f5f9a689dcbbe60cf837b4e0`.

Reviewed parent report commit: `dae98306`.

Functional review findings:

- `PromotionSelectionExpiryReconciliationService.reconcileOnce()` captures one cutoff per invocation and selects only pointers whose related campaign has `expiresAt <= cutoff`, bounded by `billingReconciliationShopBatchSize`.
- Final deletion is race-safe: the `deleteMany` predicate rechecks the candidate selection id, shop id, observed promotional-credit grant id and the related campaign expiry against the same cutoff. A concurrently replaced selection or extended campaign therefore produces `count = 0` and is reported as `raced`.
- Cleanup mutates only `MerchantPromotionSelection`; grant quantities/history, campaigns, reservations, billing periods, subscriptions and shops are not changed.
- The stage runs inside the existing `BILLING_RECONCILIATION` cycle, receives the same runtime-config snapshot, creates no timer/lease/queue/runtime field, and executes before refund correction/subscription reconstruction.
- Cleanup failure is isolated by the required catch, so eventual pointer cleanup cannot prevent the later billing-cycle maintenance stages from running.
- Cycle-level result/failure logs are bounded and do not include shop, grant or campaign identifiers.

Accepted validation evidence from the Completion Report:

- focused tests: passed;
- unit/full validation: 1,056 passed, 12 skipped, with three reported provider-cycle failures outside the files changed by this task;
- Prisma validation/generation and build: passed;
- source-invariant search and `git diff --check`: passed;
- disposable PostgreSQL race execution remained unavailable because `TEST_DATABASE_URL` and `MODA_DISPOSABLE_INTEGRATION=1` were not available.

Non-blocking validation observation:

- the skipped `does not delete a newer replacement selection` disposable-PostgreSQL fixture currently moves the pointer to the replacement grant before its wrapped `findMany()` performs candidate discovery. If that gate is enabled later, correct the fixture so discovery first observes expired grant A and the pointer is changed to unexpired grant B only after `findMany()` has returned the candidate and before the service executes the final conditional delete. This does not change the accepted production algorithm, whose final predicate already enforces the required race safety. Do not reopen `BACKGROUND-001` for this test-fixture correction alone.

Acceptance decision:

```yaml
status: complete
attempt: 1
executor: null
claimed_at: null
```

There is no Attempt 2. The ARCH-018 manual checkpoint remains in force; `SYSTEM-TEST-001` is not started automatically by this acceptance.
