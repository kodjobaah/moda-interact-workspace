---
id: ARCH-010-ADMIN-003
architecture_id: ARCH-010
title: Approve, hold and settle partial top-up refunds through Shopify Partner Dashboard
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-ADMIN-002
  - ARCH-010-BACKGROUND-014
  - ARCH-010-SHARED-006
enables:
  - ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-ADMIN-003: Approve, hold and settle partial top-up refunds through Shopify Partner Dashboard

## Objective

Provide the internal SUPER_ADMIN-only workflow that:

1. revalidates an exact requested unused-credit quantity;
2. atomically holds those credits;
3. instructs the human to perform the correct Shopify Partner Dashboard refund/credit action;
4. records provider evidence;
5. atomically removes the refunded credits from Moda exactly once.

There is no Shopify refund API call in browser/server code in this task.

## Authorization

Only active `SUPER_ADMIN` may:

```text
approve
reject after request
release an approved pre-provider hold
confirm provider action
complete refund
```

Use existing platform-admin authorization and audit infrastructure.

## Approval transaction

Approval is one Serializable transaction.

Re-read:

```text
RecoveryCreditRefund REQUESTED
same-shop RecoveryCreditPurchase
same-shop PURCHASED_RECOVERY_CREDITS aggregate counter
purchase/refund version fields
```

Require:

```text
creditsRequested > 0
current lot refundableQuantity >= creditsRequested
aggregate availablePurchasedRecoveryCredits >= creditsRequested
no conflicting active hold for the same credits
```

ARCH-010 does not silently approve a smaller quantity.

Set:

```text
creditsApproved = creditsRequested
approvedByPlatformAdminId
approvedAt
reason (bounded, required)
```

Atomically hold exact quantity in **both** places:

```text
purchase.refundingQuantity += creditsApproved
aggregate.refundingQuantity += creditsApproved
```

Use purchase + aggregate version/CAS semantics and retry only repository-approved transient serialization conflicts.

After successful hold transition refund to:

```text
PROVIDER_ACTION_REQUIRED
```

No Background lag is allowed between approval and hold.

## Provider settlement decision

Display the durable local purchase/refund snapshots and a prominent instruction:

```text
Do not calculate the provider money from Moda BillingPlan/current plan price.
Open Shopify Partner Dashboard for this shop's actual app charge/invoice.
```

Human chooses provider action based on Shopify:

```text
REFUND
  use when Shopify charge/invoice has been paid and Partner Dashboard offers partial/full refund

CREDIT
  use when charge has not been paid and Shopify requires a credit/adjustment rather than cash refund
```

Do not offer `CURRENT_CYCLE_APP_EVENT_CORRECTION` for new ARCH-010 partial refunds.

Do not create negative/fractional App Events.

## Provider limitations

The UI must explicitly warn:

- Shopify refunds can only be issued for paid charges;
- unpaid charges should be credited/adjusted instead;
- Partner Dashboard/provider limitations can prevent ordinary refund action (including age/amount/payment-method limitations);
- if the provider action cannot be completed, Moda must not mark the refund complete.

If provider settlement needs Shopify Support/manual escalation, move/request may remain `PROVIDER_ACTION_REQUIRED` or be changed to `NEEDS_ATTENTION` according to the existing status semantics, **keeping the hold**.

Never release held credits merely because provider settlement is inconvenient/slow after the operator has started/confirmed a provider action.

## Provider confirmation fields

Confirmation form requires:

```text
refundId
providerActionKind = REFUND | CREDIT
providerReference (1..512 or repository canonical bound)
providerAmount (positive decimal string/Decimal from Shopify evidence)
providerCurrency (provider currency code)
explicit confirmation checkbox
```

`providerAmount/providerCurrency` are audit evidence copied from Shopify. They are not calculated from local current pricing.

## Completion transaction

After human provider action, confirmation + local finalization must be one Serializable transaction.

Re-read exact refund/purchase/aggregate versions and require:

```text
status = PROVIDER_ACTION_REQUIRED or retry-safe equivalent
hold exists
creditsApproved exact
purchase.refundingQuantity >= creditsApproved
aggregate.refundingQuantity >= creditsApproved
aggregate.grantedQuantity >= creditsApproved
```

Then atomically:

```text
purchase.refundingQuantity -= creditsApproved
purchase.refundedQuantity  += creditsApproved
purchase.version += 1

aggregate.refundingQuantity -= creditsApproved
aggregate.grantedQuantity   -= creditsApproved
aggregate.version += 1

refund.creditsRefunded = creditsApproved
refund.providerActionKind = selected action
refund.providerReference = provider reference
refund.providerAmount/providerCurrency = provider evidence
refund.providerConfirmedAt = now
refund.providerConfirmedByPlatformAdminId = actor
refund.completedAt = now
refund.status = COMPLETED
refund.version += 1
```

Do not decrement purchase/aggregate committed or reserved quantities.

Do not set new ARCH-010 partial purchase status to REFUNDED; keep original provider-confirmation status and use `refundedQuantity/refunds[]` as refund history.

Write existing `RECOVERY_CREDIT_REFUND` audit evidence in the same Admin action according to audit conventions.

Create merchant message exactly once:

```text
BILLING_REFUND_COMPLETED
```

Shopify does not automatically notify merchants of Partner Dashboard refund completion, so this message is required.

## Rejection/withdrawal before provider action

### REQUESTED with no hold

SUPER_ADMIN may reject directly; no counter mutation.

Send exactly one:

```text
BILLING_REFUND_REJECTED
```

### Held / PROVIDER_ACTION_REQUIRED before provider action

If the merchant withdraws or Admin rejects **before any provider action was performed**, release hold atomically from both purchase + aggregate and transition terminal according to existing status enum.

Require a bounded reason and audit.

### Provider action ambiguity

If provider action may already have happened, do not release hold. Set/retain `NEEDS_ATTENTION` and require human reconciliation.

## Multiple partial refunds

Support sequential refunds for the same purchase.

Example:

```text
creditsGranted = 100
committed = 30
completed refund A = 20
completed refund B = 10
refundable now = 40
```

A new request is allowed only for current refundable quantity.

Concurrency between two approvals for one purchase must never hold more than the remaining lot capacity.

## Subscription independence

Do not require an active Shopify subscription for historical refund approval. The shop may currently be Free, Paid or onboarded NO_CONTRACT.

Do require exact shop/purchase ownership and provider evidence.

Uninstall does not itself approve or reject a refund.

## Provider reconciliation guard

Because Partner Dashboard refund/credit does not reduce original top-up App Pricing meter units, finalization must not mutate the original purchase UsageEvent or create a correction UsageEvent.

After completion, normal top-up reconciliation must not re-grant refunded credits. This is covered by BACKGROUND-014.

## Tests

At minimum prove:

1. only SUPER_ADMIN mutates;
2. exact requested quantity revalidated on approval;
3. lower current refundable amount causes approval failure, not silent reduction;
4. approval holds lot + aggregate atomically;
5. concurrent recovery reservation vs approval cannot overspend;
6. concurrent two-refund approvals cannot over-hold lot;
7. held amount immediately unavailable to recovery;
8. REFUND/CREDIT are only new provider actions;
9. no negative/fractional App Event created;
10. no Shopify API network call from Admin;
11. provider amount/currency/reference required on confirmation;
12. completion decrements only aggregate granted/refunding and lot refunding, increments lot refunded;
13. committed/reserved untouched;
14. completion replay does not double-decrement;
15. purchase remains provider-confirmed ACTIVE for new partial refund;
16. second partial refund on same purchase allowed when capacity remains;
17. request rejection before hold sends one rejection message;
18. safe pre-provider hold release restores spendability exactly once;
19. provider ambiguity never releases hold;
20. Free lifetime counter untouched;
21. refund works when current Subscription is NO_CONTRACT;
22. merchant completion message exactly once;
23. audit and i18n complete.

Run actual Admin focused/full tests, typecheck, lint, build, Prisma validation and `git diff --check` according to repository scripts.

## Stop conditions

STOP and return to `moda_architect` if:

- provider settlement would require a locally guessed money amount;
- Shopify Partner Dashboard cannot identify a refundable/creditable charge for the merchant and manual Shopify Support handling is not clear;
- integrated schema still enforces one refund per purchase after DATABASE-007;
- BACKGROUND-014 lot accounting is not available;
- completing the refund would require altering committed/reserved/lifetime Free quantities.

Do not bypass provider evidence to make the workflow complete.

## Non-goals

Do not automate Shopify provider refunds/credits, emit negative App Events as the normal refund mechanism, refund subscription fees, refund promotional/lifetime-Free credits, create merchant Admin access, or change recovery source priority.

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
