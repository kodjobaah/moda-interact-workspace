---
id: ARCH-015-SHOPIFY-003
architecture_id: ARCH-015
title: Enforce current-provider-context refund eligibility and durable refund holds
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-015-SHARED-001
- ARCH-015-SHOPIFY-002
- ARCH-015-BACKGROUND-001
enables:
- ARCH-015-BACKGROUND-003
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-015-SHOPIFY-003

## Objective

Prevent historical purchases from entering the normal monetary refund path while keeping their credits spendable. For eligible current-context purchases, create a durable refund request/entitlement hold only; Background owns provider correction.

## Authorized implementation surface

```text
app/services/billing/recovery-credit-purchase-management.service.ts
app/services/billing/providers/shopify-billing.provider.ts    # read only if required by current service composition
app/routes/app/billing/recovery-credit-purchases/route.tsx
app/components/dashboard/*purchase*manager*.*
tests/unit/services/recovery-credit-purchase-management.service.test.ts
tests/unit/recovery-credit-purchase-manager.test.tsx
# directly affected route tests
```

No App Events submission from this task.

## Fresh provider eligibility

Before changing purchase/refund state:

1. authenticate exact shop;
2. load exact purchase;
3. reject cross-shop/missing;
4. require purchase `ACTIVE`;
5. require provider purchase amount is non-null and strictly > 0 for monetary refund eligibility;
6. require unused current balance > 0;
7. obtain fresh Shopify active subscription;
8. derive current provider context through Shared;
9. require purchase context matches current context;
10. require purchase plan handle equals live provider plan handle;
11. require purchase billingPeriodId equals current local subscription billingPeriodId;
12. require purchase event handle is present in live provider subscription.

Historical/context-mismatched purchase outcome:

```text
REFUND_NOT_CURRENT_PROVIDER_CONTEXT
```

It must remain ACTIVE and no aggregate hold/refund row is created.

Zero-cost purchase outcome:

```text
REFUND_NOT_AVAILABLE
```

Credits remain spendable.

## Hold semantics

For eligible purchase, preserve existing safe reservation behavior:

```text
availableAmount = max(currentAmount - reservedAmount, 0)
```

If availableAmount < 1 => REFUND_NOT_AVAILABLE.

Create one idempotent RecoveryCreditRefund with immutable snapshots.

Transition purchase:

```text
ACTIVE -> WITHDRAWN
```

Increase aggregate `refundingQuantity` by currently available amount only. Existing reserved usage may complete/release under current reservation service rules.

Do not mark refund provider-complete.

Do not set provider evidence fields as if a provider action occurred.

## Durable invocation boundary

Successful request ends after transaction commits.

Do NOT call Background/Redis directly.

The existing billing scheduler discovers:

```text
RecoveryCreditRefund.status = REQUESTED
```

and `ARCH-015-BACKGROUND-003` processes it asynchronously.

## UI

History remains visible.

Historical ACTIVE purchase:
- show remaining credits as usable;
- hide/disable normal refund action with generic explanation that it is no longer refundable under the current subscription;
- do not imply credits expired.

REQUESTED/WITHDRAWN:
- show refund requested/processing state.

## Required tests

- current-context active positive-value purchase -> REQUESTED refund + WITHDRAWN hold;
- historical prior-plan purchase -> REFUND_NOT_CURRENT_PROVIDER_CONTEXT, stays ACTIVE;
- prior billing-cycle purchase -> not current provider context;
- event handle absent from current provider subscription -> not current context;
- null legacy id current native App Pricing context works through Shared identity;
- zero-cost purchase not monetary-refundable;
- reserved credits excluded from initial hold;
- duplicate request is idempotent;
- no Background queue/network App Event invocation;
- merchant UI keeps historical credits visible/spendable.

## Stop conditions

STOP if:

- safe eligibility requires mutating historical purchase provenance;
- task needs a new refund status/field;
- refund request must synchronously wait for Background/provider completion.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
