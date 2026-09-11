---
id: ARCH-010-ADMIN-002
architecture_id: ARCH-010
title: Triage merchant support into exact partial top-up refund requests
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 79
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-DATABASE-007
  - ARCH-010-SHARED-006
enables:
  - ARCH-010-ADMIN-003
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-ADMIN-002: Triage merchant support into exact partial top-up refund requests

## Objective

Let an internal human Admin convert an explicit merchant support message into one deterministic `RecoveryCreditRefund` request for one historical purchased-credit lot and one positive whole-credit quantity.

This task does not approve, hold or settle the refund.

## Authorization

Use existing internal Admin authorization.

ADMIN and SUPER_ADMIN may triage if that matches the existing support-triage convention.

Merchants never access this UI.

## Source request

Triage starts from an exact `MerchantSupportMessage` selected by the human Admin.

Do not use NLP/LLM/keyword auto-classification to create refund records.

The human explicitly selects action:

```text
RECOVERY_CREDIT_REFUND
```

## Refundable purchase-lot context

Server-side query only same-shop provider-confirmed purchased-credit lots.

Show for each lot at minimum:

```text
purchase date / activation date
creditsGranted
committedQuantity
reservedQuantity
refundingQuantity
refundedQuantity
refundableQuantity derived exactly
plan handle snapshot
event handle snapshot
billing period/source usage identity
existing refund requests
```

Recommended display ordering is newest purchase first for operator convenience, but eligibility calculations must use durable lot fields and must not mutate FIFO consumption policy.

Do not show lifetime Free credits as refundable.

## Request quantity

Admin selects exactly one purchase lot and enters one positive integer `creditsRequested`.

Require at request creation time:

```text
purchase belongs to shop
purchase is provider-confirmed historical top-up
creditsRequested >= 1
creditsRequested <= current lot refundableQuantity
```

Request creation does **not** hold credits. Display a clear internal warning that the merchant can continue spending until SUPER_ADMIN approval and the quantity will be revalidated then.

## Durable request

Create one `RecoveryCreditRefund` with at least:

```text
shopId
purchaseId
source = MERCHANT_SUPPORT
sourceMessageId
requestedByShopifyUserId when available from source context
purchaseCreditsGrantedSnapshot
originalUsageEventIdSnapshot
billingPeriodIdSnapshot
planHandleSnapshot
eventHandleSnapshot
creditsRequested
status = REQUESTED
requestKey
```

Do not choose provider action, provider amount, settlement mode, hold fields or approval actor here.

### Request idempotency

One support-message triage replay for the same selected purchase/quantity must return the existing request rather than create a duplicate.

The request key must support multiple historical refunds per purchase. Do **not** use `recovery-credit-refund:<purchaseId>` as the sole identity.

Use a deterministic identity including source message and purchase/request dimension, for example equivalent to:

```text
recovery-credit-refund:<sourceMessageId>:<purchaseId>:<creditsRequested>
```

bounded according to existing DB conventions.

If a different quantity is selected later, treat it as a new human decision/request only when the previous request is terminal or the operator explicitly abandons it according to existing support workflow.

## Merchant acknowledgement

Create the merchant system message exactly once using Shared:

```text
BILLING_REFUND_REQUEST_RECEIVED
```

with refund ID as event identity.

Do not promise completion or monetary amount.

## Pagination/isolation

Purchase and refund queries must be scoped by `shopId` in the database query, not filtered after loading.

Use existing Admin pagination conventions; page size default 20, max 50 unless the integrated app has a stricter standard.

Reject cross-shop IDs server-side.

## Tests

At minimum:

1. authorized Admin can triage;
2. merchant/non-admin denied;
3. no automatic NLP classification;
4. only same-shop provider-confirmed purchases selectable;
5. lifetime Free absent from refund candidates;
6. derived refundable formula exact;
7. request quantity 1..refundable accepted;
8. zero/negative/over-refundable rejected;
9. request creation does not change aggregate/purchase refunding quantity;
10. request snapshots exact purchase/provider identity;
11. same triage replay idempotent;
12. different support message can create later partial request for same purchase;
13. cross-shop purchase rejected;
14. acknowledgement message once with canonical Shared code;
15. no provider network call;
16. i18n/pagination validation.

Run actual Admin tests/type/lint/build/Prisma validation declared by repository plus `git diff --check`.

## Non-goals

Do not approve/hold, issue Shopify refund/credit, finalize local credits, call App Events, change subscription state or grant merchant Admin access.

## Stop conditions

STOP and return to `moda_architect` if DATABASE-007 lot/refund fields are unavailable or materially renamed, if same-shop purchase ownership cannot be proven server-side, or if triage would need to perform the provider settlement/credit hold owned by ADMIN-003.

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
