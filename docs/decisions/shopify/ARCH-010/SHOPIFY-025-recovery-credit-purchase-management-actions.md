---
id: ARCH-010-SHOPIFY-025
architecture_id: ARCH-010
title: Add merchant recovery-credit purchase history read model and refund lifecycle actions
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 79
executor: copilot
claimed_at: 2026-09-14T18:07:40Z
attempt: 1
depends_on:
- ARCH-010-DATABASE-014
- ARCH-010-BACKGROUND-021
- ARCH-010-BACKGROUND-022
- ARCH-010-SHOPIFY-014
- ARCH-010-SHARED-008
enables:
- ARCH-010-SHOPIFY-026
- ARCH-010-ADMIN-002
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-13
updated: 2026-09-14
---

# ARCH-010-SHOPIFY-025: Add merchant recovery-credit purchase history read model and refund lifecycle actions

## Objective

Provide one server-side merchant capability for:

1. listing the shop's own `RecoveryCreditPurchase` history across all canonical states;
2. requesting refund withdrawal for **one or more ACTIVE purchases**;
3. cancelling/reactivating one WITHDRAWN purchase while provider refund action has not begun;
4. returning deterministic per-purchase results under races with Background conversation reservations.

This task owns server read/action behaviour only. `SHOPIFY-026` owns the dedicated merchant page/components.

There is **no merchant-selected credit quantity** and no automatic Shopify money movement.

## Inspect before editing

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/repositories/**
app/routes/app/billing/**
server Prisma/database access conventions
authenticated Shopify user/shop resolution
merchant i18n/error/action conventions
tests/unit/services/**
```

Read implemented `DATABASE-014`, `BACKGROUND-021`, `BACKGROUND-022`, and `SHOPIFY-014` first.

Prefer a focused server service such as:

```text
app/services/billing/recovery-credit-purchase-management.service.ts
```

Use repository naming conventions if an equivalent service already exists. Do not put concurrency/business logic in React components.

## Merchant purchase-history read model

Expose a shop-scoped paginated read model. Query by `shopId` in the database; never fetch cross-shop rows then filter in memory.

Default page size 20, hard max 50 unless the repository already uses a stricter standard.

At minimum return for each purchase:

```text
id
status: REQUESTED | ACTIVE | COMPLETED | WITHDRAWN | REFUNDED
createdAt
activatedAt
creditsGranted
currentAmount
reservedAmount
availableAmount = max(currentAmount - reservedAmount, 0)
planName/planHandle snapshot safe for merchant display
original provider purchase amount/currency when confirmed
latest/live refund summary if any
completed refund summary if any
```

The server may return `availableAmount` as a computed read-model field; it is never persisted.

For merchant semantics:

```text
ACTIVE     -> availableAmount can be selected for withdrawal only if > 0
WITHDRAWN  -> zero spendable capacity; show current/reserved and refund workflow
COMPLETED  -> all credits consumed
REFUNDED   -> remaining unused credits were refunded
REQUESTED  -> purchase still awaiting provider confirmation; non-spendable/non-refundable
```

Do not expose internal provider credentials, raw GraphQL responses, Admin IDs or secrets.

## Request refund for one purchase — canonical transaction

A refund request means:

> Withdraw this entire purchase from new allocation and refund every credit that ultimately remains unused after existing reservations settle.

The merchant does **not** supply quantity, price, currency, provider charge ID or provider action kind.

Use one Serializable transaction with bounded retry/CAS for each selected purchase.

### Transaction steps

Freshly read:

```text
RecoveryCreditPurchase
ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS)
any non-terminal RecoveryCreditRefund for this purchase
```

Require:

```text
purchase.shopId = authenticated shop
purchase.status = ACTIVE
no non-terminal refund already exists
```

Compute from the winning database state:

```text
availableAmount = purchase.currentAmount - purchase.reservedAmount
```

If:

```text
availableAmount < 1
```

return per-item result:

```text
REFUND_NOT_AVAILABLE
```

with no mutation. The purchase stays ACTIVE.

Otherwise create one `RecoveryCreditRefund` with:

```text
source = MERCHANT_UI
purchase/shop identity
authenticated Shopify user identity when available
immutable commercial snapshots from purchase
currentAmountAtRequestSnapshot = purchase.currentAmount
reservedAmountAtRequestSnapshot = purchase.reservedAmount
availableAmountAtRequestSnapshot = availableAmount
status = REQUESTED
bounded deterministic requestKey/idempotency identity
```

Then atomically CAS both purchase and aggregate counter in the same transaction:

```text
purchase:
  WHERE id + status=ACTIVE + version=expected
  SET status=WITHDRAWN, version += 1

aggregate purchased counter:
  refundingQuantity += availableAmount
  version += 1 via expected-version CAS
```

`availableAmount` is the unreserved part of this purchase that becomes held immediately. Existing reservations remain represented in aggregate `reservedQuantity` and are not double-counted in `refundingQuantity`.

If either CAS fails, roll back the **whole transaction** and retry from fresh state. Do not reuse a stale browser quantity.

## Reservation/refund race — required observable results

The browser-displayed value is advisory only. Server state at the winning CAS decides.

### Displayed 1, conversation wins it

If the merchant saw:

```text
available = 1
```

but a conversation reserves that credit first, refund retry sees:

```text
available = 0
```

Return:

```text
REFUND_NOT_AVAILABLE
```

Do not set WITHDRAWN.

### Displayed 2, conversation reserves 1 first

Fresh retry sees:

```text
currentAmount = 2
reservedAmount = 1
availableAmount = 1
```

Request succeeds:

```text
ACTIVE -> WITHDRAWN
availableAmountAtRequestSnapshot = 1
```

Return enough state for UI copy equivalent to:

```text
Refund requested. 1 credit is currently refundable and 1 credit is still in progress.
The final refund will cover every credit that remains after in-flight conversations settle.
```

Do not promise that the final refund quantity is permanently 1. If the in-flight conversation later releases, BACKGROUND-022 moves that credit into the withdrawal hold and the final refund can become 2.

### Refund wins first

If ACTIVE -> WITHDRAWN wins first, a competing Background reservation must lose/retry and skip this lot. SHOPIFY-025 must not create a shop-global lock.

## Batch refund request: one or more purchases

Accept a bounded unique list of purchase IDs, recommended max 20 per action.

Security:

```text
all IDs are resolved under authenticated shopId
unknown/cross-shop IDs return a bounded per-item denial/not-found result
client cannot submit quantities or money
```

**Do not wrap the whole batch in one database transaction.**

Process each selected purchase independently through the canonical single-purchase transaction above. This is deliberate because different lots may race independently with conversations.

Return ordered per-purchase outcomes such as:

```text
REQUESTED
REFUND_NOT_AVAILABLE
NOT_ACTIVE
ALREADY_WITHDRAWN
ALREADY_REFUNDED
COMPLETED
NOT_FOUND
```

A failure on Purchase B must not roll back a successful withdrawal of Purchase A.

Use one client request identity for transport replay plus purchase ID in each per-lot request key, or another deterministic equivalent that permits:

- safe HTTP retry of the same batch;
- later new refund request after a prior refund request was withdrawn/reactivated;
- no duplicate live refund row for one purchase.

## Reactivate/cancel refund request

A merchant may change their mind only while the purchase is WITHDRAWN and the exact live refund is still strictly pre-provider-action:

```text
purchase.status = WITHDRAWN
refund.status = REQUESTED
no provider action/reference/confirmation exists
```

Use one Serializable transaction and CAS both refund and purchase/aggregate state.

Freshly compute:

```text
heldAvailable = purchase.currentAmount - purchase.reservedAmount
```

### If currentAmount > 0

Atomically:

```text
aggregate.refundingQuantity -= heldAvailable
purchase.status = ACTIVE
purchase.version += 1
refund.status = CANCELLED
refund.reason = MERCHANT_REACTIVATED (bounded canonical equivalent)
refund.version += 1
```

Do not change `currentAmount` or `reservedAmount`.

Existing reservations continue. The reactivated purchase returns to its original FIFO position because `activatedAt/createdAt/id` are unchanged.

### If currentAmount = 0

Do not reactivate. Atomically ensure:

```text
purchase.status = COMPLETED
refund.status = CANCELLED
reason = NO_CREDITS_REMAINING
```

and return a completed/no-credits result.

### Race with Admin provider-action lock

ADMIN-003 moves refund `REQUESTED -> PROVIDER_ACTION_REQUIRED` using refund version/CAS.

Merchant reactivation and Admin provider-action lock therefore compete on the same refund version. Exactly one wins.

If Admin wins first, merchant retry sees `PROVIDER_ACTION_REQUIRED` and must return:

```text
REACTIVATION_NOT_AVAILABLE
```

Never restore credits after provider settlement may have started.

## Aggregate-counter correctness

Request/re-activate paths must maintain the same aggregate conventions BACKGROUND-022 uses:

```text
request withdrawal:
  refundingQuantity += currentAmount - reservedAmount

reactivate:
  refundingQuantity -= currentAmount - reservedAmount
```

All counter updates require versioned CAS in the same transaction as purchase/refund lifecycle mutation.

Do not derive a shop-global purchase state from the aggregate counter.

## Merchant system messages

Use existing published Shared codes where product messaging already expects them:

```text
BILLING_REFUND_REQUEST_RECEIVED
BILLING_REFUND_COMPLETED
BILLING_REFUND_REJECTED
```

The request-received message may be created exactly once on successful per-purchase request using refund ID as identity.

Do not create new Shared codes merely for immediate UI confirmation/reactivation unless implementation proves the existing merchant history cannot communicate the state. If a new cross-service code is genuinely required, STOP and return to `moda_architect` rather than inventing one in this repo.

## Capacity resume after reactivation

Reactivation can restore spendable purchased capacity. Do not add a cross-repository Redis/BullMQ dependency to the Shopify app solely for this action.

BACKGROUND-009's durable periodic capacity-repair scan remains sufficient first-production recovery if no existing safe post-commit hook is available. If an accepted local integration already exposes a best-effort resume hint without coupling the app to Background internals, it may be used post-commit only.

## Required tests

At minimum prove:

1. list query is shop-scoped and paginated;
2. all five purchase states map correctly;
3. ACTIVE available is `currentAmount-reservedAmount`;
4. quantity/money supplied by client is ignored/rejected;
5. request with available 0 performs no mutation;
6. request with available >0 creates one refund + ACTIVE->WITHDRAWN + aggregate hold atomically;
7. same request replay is idempotent;
8. one-live-refund DB conflict is handled deterministically;
9. displayed-1 / reservation-wins returns REFUND_NOT_AVAILABLE;
10. displayed-2 / one reservation wins can withdraw fresh available 1;
11. refund-wins causes stale reservation CAS to lose (service contract/integration fixture);
12. batch processes lots independently and reports partial success;
13. cross-shop purchase ID cannot be read/mutated;
14. reactivation REQUESTED refund restores ACTIVE and aggregate hold exactly;
15. reactivation does not alter current/reserved values;
16. provider-action-required refund cannot be reactivated;
17. reactivation/Admin-lock race has exactly one winner;
18. currentAmount 0 cannot reactivate and yields COMPLETED;
19. no provider refund API/negative App Event is called;
20. focused service tests, repository typecheck/build/full relevant tests and `git diff --check` pass.

## Non-goals

Do not implement React/page UI, provider settlement, Admin approval, Background reservation code or database schema.

## Stop conditions

STOP if DATABASE-014/BACKGROUND-022 are not integrated, if authenticated shop scoping cannot be proven, or if the only implementation would require a shop-global lock or client-trusted quantity.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact/app/services/billing/recovery-credit-purchase-management.service.ts`
- `moda-interact/tests/unit/services/recovery-credit-purchase-management.service.test.ts`

### Work Completed
- Added a shop-scoped, paginated purchase-history read model with default page size 20, hard maximum 50, all five canonical purchase statuses, computed non-negative availability, safe plan and original-provider-purchase summaries, and safe live/completed refund summaries.
- Added Serializable bounded-retry refund withdrawal for one purchase and bounded batches of up to 20 unique purchase IDs. Each transaction fresh-reads the purchase, live refund state, and purchased-credit aggregate, ignores client quantity/money fields, creates immutable `MERCHANT_UI` refund snapshots, and CAS-updates `ACTIVE -> WITHDRAWN` plus aggregate `refundingQuantity`.
- Added deterministic request keys, idempotent live-refund replay, independent batch outcomes, authenticated shop scoping, cross-shop not-found behavior, and no provider refund API or negative App Event path.
- Added Serializable/CAS reactivation for strictly pre-provider-action `REQUESTED` refunds, including aggregate hold release, unchanged current/reserved balances, provider-action rejection, and `currentAmount = 0` completion with `NO_CREDITS_REMAINING` cancellation.
- Added focused coverage for pagination/scoping, every status, fresh availability and client-input rejection, zero-availability no-op, atomic hold, replay/conflict retry, reservation-race outcomes through the service contract, partial batch success, reactivation preservation, provider-action locking, and empty-purchase completion.

### Validation Results
- `npm test -- --run tests/unit/services/recovery-credit-purchase-management.service.test.ts`: passed, 10/10.
- Relevant billing suites (`billing.service`, `billing-reconciliation.service`, and the new management service): passed, 3 files and 197 tests.
- `npm test`: passed, 42 files and 514 tests; 2 files and 3 tests skipped.
- `npm run prisma:generate`: passed.
- `npm run prisma:validate`: passed.
- `npm run build`: passed.
- Touched-file ESLint: passed; only the repository's TypeScript-version support warning was emitted.
- `git diff --check`: passed.
- `npm run typecheck`: existing baseline failure with 141 diagnostics across the repository; no diagnostic referenced either changed file. The observed baseline includes existing untyped JSX route/component diagnostics, missing `d3` declarations, an existing nullable `subscription.plan` diagnostic in `billing.service.ts`, and the existing Redis `zrange` type mismatch.

### Git / VCS
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-025`.
- Implementation branch: `task/ARCH-010-SHOPIFY-025`.
- Implementation commit: `7ac42c4f24ada3321f1aff9ec6e8cf32697ef982` (`feat(shopify): manage recovery credit purchase refunds`).
- Implementation branch pushed successfully to `origin/task/ARCH-010-SHOPIFY-025`.
- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-025`.
- No schema, Shared, Background, Admin, provider, route, or UI files were changed.

### Architect Review
Pending.
