---
id: ARCH-010-SHOPIFY-017
architecture_id: ARCH-010
title: Present unused purchased-credit refundability and support CTA
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 78
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-DATABASE-007
  - ARCH-010-SHARED-006
  - ARCH-010-SHOPIFY-012
enables:
  - ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-SHOPIFY-017: Present unused purchased-credit refundability and support CTA

## Objective

Expose the Moda product rule that unused purchased top-up credits may be requested for refund while keeping provider money movement human/support owned.

Merchants never receive access to `moda-interact-admin`.

## Files/surfaces to inspect

Inspect actual integrated equivalents before editing:

```text
/app/billing/options route + BillingPurchaseHub children
/app/merchant-support route/components/actions
billing/capacity read services from SHOPIFY-009/012/014
merchant billing i18n catalogues/tests
```

Do not assume prototype component names survived SHOPIFY-010/011/012.

## Merchant billing-options behaviour

On `/app/billing/options`, display a non-authoritative informational refund section when the shop has at least one provider-confirmed purchased-credit lot.

At minimum show:

```text
Purchased credits currently spendable (aggregate)
Purchased credits currently held for refund (aggregate, if >0)
Refund policy: only unused purchased top-up credits are refundable
Lifetime Free credits are not refundable
```

Do not display a local monetary refund estimate.

Do not claim Shopify refund eligibility merely from local age/state.

Provide CTA:

```text
Request a refund
-> /app/merchant-support?topic=topup-refund
```

or the equivalent existing support prefill mechanism.

If the support route has no query-prefill convention, add the smallest bounded query handling needed to preselect/prefill a translated top-up-refund topic without auto-submitting a request.

## No self-service settlement

The merchant must not:

- select Shopify charge IDs;
- enter provider refund amounts;
- call Shopify refund APIs;
- directly mutate RecoveryCreditRefund;
- directly place a refund hold;
- choose REFUND vs CREDIT provider action;
- access internal Admin screens.

Submitting the ordinary support message is the only merchant action in this task.

Human Admin owns conversion of that support message into a durable refund request.

## Subscription state

Refund information/support remains visible for an installed merchant even when:

```text
Free
Paid
NO_CONTRACT after prior cancellation
```

provided the normal dashboard/billing history is accessible.

Do not enable recovery execution for NO_CONTRACT merely because purchased balances exist.

## Lot information

Do not expose internal purchase IDs unless an existing merchant purchase-history pattern already does so safely.

Merchant UI may show human-friendly purchase date/credits granted/unused amount if SHOPIFY-012 already renders purchase history and DATABASE-007 data is available, but the CTA must remain support-based.

If adding per-lot display would materially expand the current route beyond this task, show only aggregate refund-policy information and STOP rather than redesign the page.

## Merchant messaging

Ensure the merchant support/system message renderer recognizes translated copy for Shared codes:

```text
BILLING_REFUND_REQUEST_RECEIVED
BILLING_REFUND_COMPLETED
BILLING_REFUND_REJECTED
```

Do not create a second message mechanism.

## Required tests

At minimum prove:

1. billing-options remains available and shows refund policy with purchased credits;
2. lifetime Free is explicitly not refundable;
3. no local monetary estimate is shown;
4. refund CTA routes only to merchant support;
5. no refund DB/provider mutation occurs from merchant UI;
6. support topic prefill is bounded and does not auto-submit;
7. Free, Paid and onboarded NO_CONTRACT merchants can reach the support CTA when normal billing/history is allowed;
8. Admin route/access is never linked/exposed;
9. request/completed/rejected system messages render through i18n;
10. existing top-up purchase and plan-change actions remain intact.

Run focused route/component tests, repository unit/type/lint/build commands declared by `package.json`, and `git diff --check`.

## Non-goals

Do not implement Admin triage/approval, provider settlement, lot reservation accounting, subscription refunds or refund eligibility promises beyond local unused-credit policy.


## Final promotional-credit refund exclusion

Promotional credits are excluded from every purchased-credit refundability calculation and quantity limit. They may be displayed separately as non-refundable Moda-provided capacity, but must never be represented as a refundable RecoveryCreditPurchase lot or included in provider refund/credit instructions.

## Stop conditions

STOP if DATABASE-007 purchase-lot/refund fields are unavailable to the merchant read layer, if the only way to satisfy the request is to expose Admin/provider settlement controls to the merchant, or if provider monetary eligibility would have to be guessed from local data.

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
