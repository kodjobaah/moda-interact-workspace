---
id: ARCH-010-ADMIN-003
architecture_id: ARCH-010
title: Lock and settle withdrawn recovery-credit purchases through Shopify Partner Dashboard
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 82
executor: copilot
claimed_at: 2026-09-14T22:04:41Z
attempt: 1
depends_on:
- ARCH-010-ADMIN-002
- ARCH-010-BACKGROUND-022
- ARCH-010-SHARED-008
- ARCH-010-DATABASE-014
- ARCH-010-BACKGROUND-021
enables:
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: 2026-09-14
---

# ARCH-010-ADMIN-003: Lock and settle withdrawn recovery-credit purchases through Shopify Partner Dashboard

## Product correction

The old arbitrary-partial approval/hold workflow is superseded.

The merchant already placed the exact purchase into `WITHDRAWN` through SHOPIFY-025. That transition removed the purchase from future FIFO allocation and placed its currently unreserved credits into aggregate `refundingQuantity`.

ADMIN-003 does **not** choose or hold a partial quantity. It waits for all pre-existing reservations on that purchase to settle, then locks the purchase's **entire remaining `currentAmount`** as the final provider refund quantity.

There is no Shopify refund API call in application code; the human uses Shopify Partner Dashboard/Support and records evidence.

## Authorization

Only active `SUPER_ADMIN` may:

```text
lock provider action
reject before provider action
record provider action
complete refund
move/resolve NEEDS_ATTENTION according to existing Admin conventions
```

Use existing platform-admin authorization/audit infrastructure.

## Irreversible provider-action boundary

Provider action may begin only when a fresh Serializable transaction proves:

```text
refund.status = REQUESTED
purchase.status = WITHDRAWN
purchase.currentAmount > 0
purchase.reservedAmount = 0
refund/purchase belong to same shop
purchase immutable commercial provenance is complete
the aggregate purchased counter exists and is internally consistent
```

If `reservedAmount > 0`, return `WAITING_FOR_RESERVATIONS`; do not create provider instructions and do not guess final quantity.

If `currentAmount = 0`, no money is refundable. Close according to the canonical no-credits terminal path and ensure purchase is `COMPLETED`; do not create a £0 provider action.

## Final credit quantity

At the winning provider-action transaction:

```text
finalCreditQuantity = purchase.currentAmount
```

The merchant/Admin never enters this value.

Persist it in the canonical DATABASE-014 refund field (for example `finalCreditQuantity`) together with the deterministic expected provider amount/currency.

Once refund moves:

```text
REQUESTED -> PROVIDER_ACTION_REQUIRED
```

merchant reactivation is forbidden.

### Race with merchant reactivation

SHOPIFY-025 and ADMIN-003 both CAS the exact refund `status + version`.

If merchant reactivation wins first, Admin retry sees refund `CANCELLED`/purchase ACTIVE and must not begin provider action.

If Admin provider-action lock wins first, merchant retry sees `PROVIDER_ACTION_REQUIRED` and cannot reactivate.

Exactly one wins; no global lock.

## Historical monetary value

Refund money comes only from the exact purchase's immutable provider-confirmed original value.

Let:

```text
G = purchase.creditsGranted
R = finalCreditQuantity
M = purchase.providerPurchaseAmount
```

Require valid purchase amount/currency/provenance and `0 < R <= G`.

Compute the expected provider refund for `R/G` of the original purchase using the deterministic currency-safe precision/rounding rule established by DATABASE-014/provider representation.

Persist:

```text
expectedProviderAmount
expectedProviderCurrency = purchase.providerPurchaseCurrency
```

Never use:

```text
current BillingPlan price
current Shopify plan/tier
current top-up meter rate
another purchase lot
later BillingEconomicsSnapshot
browser/Admin-entered amount as expected truth
```

Because a successful refund makes this purchase terminal REFUNDED, first production has at most one completed refund per purchase; no cumulative multi-partial-refund arithmetic is required.

## Aggregate hold invariant at provider-action boundary

When `reservedAmount = 0`, every remaining current credit on a WITHDRAWN purchase must already be represented in aggregate `refundingQuantity` through SHOPIFY-025/BACKGROUND-022.

Require enough aggregate held quantity for the exact final credit quantity. If parity is inconsistent, do not start provider action; move/report integrity attention rather than repairing by subtraction from another lot.

## Provider settlement instructions

Display exact durable evidence:

```text
shop
purchase/refund IDs
original purchase date
plan/provider subscription/BillingPeriod/meter snapshots
creditsGranted
finalCreditQuantity
original providerPurchaseAmount/providerPurchaseCurrency
expectedProviderAmount/expectedProviderCurrency
```

Human selects actual Shopify action:

```text
REFUND  -> paid charge/invoice can be refunded
CREDIT  -> Shopify requires a credit/adjustment for unpaid charge
```

Do not offer negative/fractional App Events or current-cycle correction events for first-production purchase refunds.

Warn that provider limitations may require Shopify Support/manual escalation. If provider settlement cannot be confirmed, retain purchase WITHDRAWN and aggregate hold.

## Provider evidence

Require:

```text
providerActionKind = REFUND | CREDIT
providerReference bounded string
providerAmount
providerCurrency
explicit confirmation
```

Before local completion require exact match:

```text
providerAmount == expectedProviderAmount
providerCurrency == expectedProviderCurrency
```

If provider evidence differs or action may be ambiguous:

```text
refund -> NEEDS_ATTENTION (or retain equivalent accepted attention state)
purchase stays WITHDRAWN
aggregate hold stays in place
merchant cannot reactivate because provider action may have started
```

Do not silently change expected amount to what the operator typed.

## Completion transaction

After confirmed provider action, one Serializable/CAS transaction re-reads exact refund/purchase/aggregate state and requires:

```text
refund.status = PROVIDER_ACTION_REQUIRED (or retry-safe attention resolution path)
purchase.status = WITHDRAWN
purchase.reservedAmount = 0
purchase.currentAmount = refund.finalCreditQuantity
aggregate.refundingQuantity >= finalCreditQuantity
aggregate.grantedQuantity >= finalCreditQuantity
provider evidence exactly matches expected amount/currency
```

Then atomically:

```text
purchase.currentAmount = 0
purchase.reservedAmount = 0
purchase.status = REFUNDED
purchase.version += 1

aggregate.refundingQuantity -= finalCreditQuantity
aggregate.grantedQuantity   -= finalCreditQuantity
aggregate.version += 1

refund.status = COMPLETED
refund provider evidence fields = confirmed evidence
refund.completedAt = now
refund.version += 1
```

Do not increment a per-purchase `refundedQuantity`; first production has no such lot counter.

Do not modify aggregate committed/reserved quantities during provider completion because `reservedAmount=0` was already required and consumed credits remain committed history.

Write existing `RECOVERY_CREDIT_REFUND` audit evidence and create exactly one merchant `BILLING_REFUND_COMPLETED` message using refund ID identity.

## Reject before provider action

A SUPER_ADMIN may reject only while exact refund is still `REQUESTED` and no provider action may have occurred.

This is concurrency-equivalent to merchant reactivation and must use fresh CAS.

If purchase still has `currentAmount > 0`, atomically:

```text
heldAvailable = currentAmount - reservedAmount
aggregate.refundingQuantity -= heldAvailable
purchase WITHDRAWN -> ACTIVE
refund REQUESTED -> REJECTED
```

Do not change purchase current/reserved quantities.

If currentAmount has reached 0, make/retain purchase COMPLETED and reject/close refund with no provider money movement.

Create exactly one `BILLING_REFUND_REJECTED` merchant message with bounded reason.

Never reject/release hold after provider action may have started. Use NEEDS_ATTENTION instead.

## Multiple purchases

Different purchase lots are independent. Admin may simultaneously have:

```text
Purchase A refund waiting for reservations
Purchase B ready for provider action
Purchase C provider action required
Purchase D completed/refunded
```

No shop-wide refund lock is allowed. Every mutation scopes to exact purchase/refund plus the shared aggregate counter under versioned CAS.

## Required tests

At minimum prove:

1. only SUPER_ADMIN can mutate settlement;
2. reservedAmount>0 blocks provider-action lock;
3. currentAmount=0 cannot create £0 refund;
4. final credit quantity is always exact currentAmount, never operator input;
5. historical purchase amount/currency is sole expected-money authority;
6. current plan/top-up rate changes do not affect expected refund;
7. REQUESTED -> PROVIDER_ACTION_REQUIRED freezes final quantity/amount;
8. merchant-reactivation vs Admin-lock race has exactly one winner;
9. provider-action-required/needs-attention blocks merchant reactivation contractually;
10. aggregate held parity is required;
11. provider amount/currency mismatch cannot complete;
12. successful completion sets purchase REFUNDED/current=0 and removes exact aggregate grant+hold;
13. no per-lot refundedQuantity is written;
14. replay does not double-remove credits or duplicate messages/audit;
15. pre-provider Admin reject reactivates exact purchase and releases only its current unreserved hold;
16. rejection while provider action may have happened never releases hold;
17. other purchase lots remain untouched;
18. no negative App Event/automatic refund API is introduced;
19. focused tests, concurrency tests where applicable, repository build/full suite and `git diff --check` pass.

## Non-goals

Do not create merchant refund requests, implement merchant UI, change FIFO reservation logic, or refund Shopify recurring subscription fees.

## Stop conditions

STOP if a provider refund cannot be tied to exact immutable purchase value, if aggregate hold parity is ambiguous, if exact money cannot be represented safely, or if a completed task must be rewritten.

## Completion Report

### Status
Blocked: the published shared dependency available to Admin does not export the authoritative `BILLING_REFUND_COMPLETED` and `BILLING_REFUND_REJECTED` message contracts required by this task. The newer definitions are present only in the workspace shared source, while Admin resolves the published package and must not create a competing local contract or literal fallback.

### Files Changed
None retained. The initial settlement-domain probe was removed after focused validation proved the shared-contract dependency gap.

### Work Completed
Inspected the complete task definition, current local Admin conventions, Prisma schema, existing refund triage, shared billing source, and database precision/provenance contract. Confirmed the existing schema has the required refund, purchase, aggregate, audit, and provider-evidence fields. No source implementation was retained because the required shared message export is unavailable in the consumed package.

### Validation Results
`npm ci`: passed in the authoritative implementation worktree.
`npm run prisma:generate`: passed.
`npx tsc --noEmit --pretty false`: baseline Admin typechecking progressed after Prisma generation, then failed only in the settlement probe on missing `BILLING_REFUND_COMPLETED` and `BILLING_REFUND_REJECTED` exports from `@modainteract/moda-interact-shared` 0.11.0. The package declaration was inspected and confirms both exports are absent. Required focused tests/build/full suite were not run because implementation is blocked at the shared contract boundary.

### Git / VCS
Launcher claim commit: `1d0d2246b6703c56b14ee802b2d1a5569d0f2bf5`.
Authoritative implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-003`, branch `task/ARCH-010-ADMIN-003`.
Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-003`, branch `task/ARCH-010-ADMIN-003`.
No implementation commit was created because the required shared contract is unavailable. This blocker report is published in commit `a765fc7`.

### Architect Review
Blocked pending `ARCH-010-SHARED-008` publishing the refund message-code contract in the shared package consumed by Admin, or otherwise sequencing a compatible shared dependency release. Do not implement local message-code fallbacks in Admin.
