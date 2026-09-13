---
id: ARCH-010-ADMIN-002
architecture_id: ARCH-010
title: Review merchant recovery-credit purchase refund requests
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 81
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-014
- ARCH-010-BACKGROUND-022
- ARCH-010-SHOPIFY-025
- ARCH-010-SHARED-008
- ARCH-010-ADMIN-010
enables:
- ARCH-010-ADMIN-003
created: 2026-09-11
updated: '2026-09-13'
---

# ARCH-010-ADMIN-002: Review merchant recovery-credit purchase refund requests

## Product correction

The old definition expected Admin to convert a merchant support message into an arbitrary partial-credit refund quantity. That design is superseded before implementation.

The merchant now creates the durable request directly through SHOPIFY-025 by withdrawing one exact ACTIVE `RecoveryCreditPurchase`. There is no Admin-entered refund quantity.

This task owns the internal review/queue/read experience only. ADMIN-003 owns the irreversible provider-action boundary and settlement.

## Objective

Give authorized internal Admin users a deterministic queue/detail view of merchant-created `RecoveryCreditRefund` requests and their exact purchase-lot state.

Admin must be able to understand:

```text
which shop requested it
which exact RecoveryCreditPurchase was withdrawn
original purchase/subscription/BillingPeriod/plan/meter provenance
original purchase amount/currency
request-time current/reserved/available snapshots
current purchase currentAmount/reservedAmount
whether existing reservations are still draining
whether provider action may begin
refund workflow/history
```

Admin does not choose how many credits to refund.

## Authorization

Use existing internal Admin authorization.

ADMIN and SUPER_ADMIN may view/review if that matches existing support/billing conventions.

Only SUPER_ADMIN may perform ADMIN-003 provider settlement actions.

Merchants never access Admin routes.

## Queue

Add/reuse a bounded paginated queue for refund workflows. Default page 20, max 50 unless repository convention is stricter.

Useful filters:

```text
REQUESTED
READY_FOR_PROVIDER_ACTION (derived: refund REQUESTED + purchase WITHDRAWN + reservedAmount=0 + currentAmount>0)
WAITING_FOR_RESERVATIONS (derived: refund REQUESTED + purchase WITHDRAWN + reservedAmount>0)
PROVIDER_ACTION_REQUIRED
NEEDS_ATTENTION
COMPLETED
REJECTED
CANCELLED
```

`READY_FOR_PROVIDER_ACTION` and `WAITING_FOR_RESERVATIONS` are Admin read-model labels, not new database refund statuses.

Every query must be database-scoped/paginated; do not load all shops then filter.

## Exact request detail

For one request display at minimum:

```text
refund ID/status/createdAt/source
merchant/shop identity allowed by Admin conventions
requestedByShopifyUserId when present

purchase ID/status
purchase created/activated date
creditsGranted
currentAmount
reservedAmount
current unreserved amount = currentAmount - reservedAmount

currentAmountAtRequestSnapshot
reservedAmountAtRequestSnapshot
availableAmountAtRequestSnapshot

billingPeriod/provider-subscription/plan/event snapshots
original providerPurchaseAmount/providerPurchaseCurrency
provider before/after valuation evidence in a bounded operator-safe form

existing exact UsageReservations if current Admin patterns permit bounded drill-down
historical refund attempts for this purchase
```

Do not display current BillingPlan price as refund authority.

## State interpretation

### Purchase WITHDRAWN + reservedAmount > 0

Display clearly:

```text
Waiting for in-flight conversations to settle.
Provider refund action MUST NOT start yet.
```

Existing reservations may commit or release. A release can increase the final refund quantity; a commit can reduce it.

### Purchase WITHDRAWN + reservedAmount = 0 + currentAmount > 0

Display:

```text
Ready for provider action.
Final credit quantity will be locked by ADMIN-003 from currentAmount.
```

Do not let ADMIN-002 persist a quantity.

### Purchase COMPLETED

There is nothing left to refund. The live request should already be terminally closed by BACKGROUND-022/SHOPIFY-025 race handling. If an inconsistent non-terminal refund remains, surface `DATA_INTEGRITY_ATTENTION`; do not repair it in this read task.

### Purchase ACTIVE

A non-terminal refund with ACTIVE purchase is inconsistent unless it is in the middle of an atomic action that cannot be observed after commit. Surface integrity attention; do not invent a hold.

### Purchase REFUNDED

Show terminal historical settlement; no new action.

## No support-message prerequisite

A `MerchantSupportMessage` is no longer required to create the refund request.

If the merchant separately contacted support, Admin may display/link that thread through existing support tooling, but it is contextual only and must not become refund identity/quantity authority.

Do not create a `RecoveryCreditRefund` from NLP, keywords or support triage in this task.

## No quantity controls

The Admin UI must contain **no** control equivalent to:

```text
creditsRequested input
creditsApproved input
partial amount selector
percentage selector
```

The product rule is always: refund every credit that remains unused on the exact withdrawn purchase once its existing reservations have drained.

## Merchant cancellation/reactivation visibility

If the merchant reactivated the purchase before provider action, the refund becomes terminal `CANCELLED` with a bounded reason. Show that history; do not reopen it automatically.

A later refund request against the reactivated ACTIVE purchase creates a new refund row through SHOPIFY-025.

## Required tests

At minimum prove:

1. Admin authorization protects queue/detail;
2. queue pagination/filtering is bounded;
3. merchant-created requests appear without support message;
4. request-time snapshots and current purchase amounts are both shown distinctly;
5. WITHDRAWN + reserved>0 is labelled waiting and cannot start provider action here;
6. WITHDRAWN + reserved=0 + current>0 is labelled ready;
7. no quantity/percentage/money-entry control exists in ADMIN-002;
8. current plan/top-up price is not presented as refund authority;
9. merchant-reactivated terminal refund history is visible;
10. completed/refunded purchases cannot be triaged into another refund here;
11. inconsistent ACTIVE/non-terminal refund fails visibly rather than being auto-repaired;
12. cross-shop data isolation/Admin authorization tests pass;
13. focused tests, repository validation/build and `git diff --check` pass.

## Non-goals

Do not create merchant refund requests, mutate purchase holds, choose provider action, calculate final provider refund amount, confirm provider settlement, or call Shopify.

## Stop conditions

STOP if SHOPIFY-025 does not create durable merchant refund requests, if DATABASE-014 fields are unavailable, or if implementing the queue would require recreating the old arbitrary-partial-refund model.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
