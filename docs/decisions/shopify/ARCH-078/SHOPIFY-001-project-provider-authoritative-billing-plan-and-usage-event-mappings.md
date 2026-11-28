---
id: ARCH-078-SHOPIFY-001
architecture_id: ARCH-078
title: Project Shopify subscriptions without reporting-handle meter validation
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-078-DATABASE-001]
enables: [ARCH-078-SYSTEM-TEST-001]
created: 2026-11-22
updated: 2026-11-22
---

# ARCH-078-SHOPIFY-001 — Project Shopify subscriptions using provider-authoritative usage-event mapping

## Architecture and dependency

Follow [ARCH-078](../../../architecture/ARCH-078-shopify-provider-authoritative-billing-plan-and-usage-event-mapping.md).

Hard dependency: `ARCH-078-DATABASE-001` must be architect-accepted and the database submodule pin/Prisma client must include `Subscription.unmappedShopifyUsageEventHandles`.

## Objective

Correct the Shopify app's subscription resolution and initial paid activation so the exact Shopify flat-rate plan handle determines subscription identity, while missing `MerchantPricingUsageEvent` mappings are recorded for Admin without invalidating a valid subscription.

## Read before editing

Read these exact files and tests:

```text
app/services/billing/billing-plan-resolution.service.ts
app/services/billing/subscription-sync.service.ts
app/services/billing/subscription-activation.service.ts
app/services/billing/providers/shopify-billing.provider.ts
app/services/billing/shopify-billing-operation.service.ts
app/services/billing/recovery-credit-purchase-request.service.ts
tests/unit/services/billing/billing-plan-resolution.service.test.ts
tests/unit/services/billing/subscription-sync.service.test.ts
tests/unit/services/billing/subscription-activation.service.test.ts
tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts
tests/unit/services/shopify-billing.provider.test.ts
tests/integration/billing-activation.postgres.integration.test.ts
```

Search the full Shopify repository for:

```text
shopifyRecoveryUsageEventHandle
shopifyUsageEventHandle
MISSING_USAGE_METER
UNMAPPED_PLAN_HANDLE
usageEventHandles
unmappedShopifyUsageEventHandles
```

## Required local mapping component

Create one small Shopify-app-local component:

```text
app/services/billing/shopify-usage-event-mapping.ts
```

Do not add this logic to `moda-interact-shared`.

The component must accept the exact provider plan handle and the provider-returned `usageEventHandles`, read the exact matching `MerchantPricingPlan.usageEvents.eventHandle` values through the existing Prisma boundary, and return:

- provider-returned handles with exact catalogue matches;
- provider-returned handles without catalogue matches.

Rules:

- no catalogue plan => all provider-returned handles are unmapped;
- no catalogue usage events => all provider-returned handles are unmapped;
- catalogue-only events absent from Shopify are ignored;
- exact, case-sensitive handle matching; no aliases or inferred handles;
- deduplicate and return deterministic ordering;
- do not create catalogue rows or an operational usage-event table.

Reuse the component from subscription sync and initial paid activation. Do not duplicate mapping logic.

## Plan resolution and reporting-handle correction

In `app/services/billing/billing-plan-resolution.service.ts`:

- Continue to resolve an existing operational `BillingPlan` by exact `shopifyPlanHandle`.
- If missing, resolve the exact `MerchantPricingPlan` and preserve existing genuine plan-kind, required-feature, included-credit and merchant-knowledge validation.
- Remove the `FREE_PLAN_HAS_RECOVERY_USAGE_METER` and `PAID_PLAN_MISSING_RECOVERY_USAGE_METER` validation outcomes. `shopifyRecoveryUsageEventHandle` is not a Shopify billable usage-meter mapping.
- A paid plan with a null or customer-defined `shopifyRecoveryUsageEventHandle` must still materialise when its other required plan fields are valid.
- Copy a configured paid reporting handle to nullable `BillingPlan.shopifyUsageEventHandle` when present; otherwise use `null`. Do not use a non-null assertion.
- Do not compare the reporting handle with `providerSubscription.usageEventHandles`.
- Preserve existing App Events reporting use of `BillingPlan.shopifyUsageEventHandle`.

## Subscription sync and initial activation

In `app/services/billing/subscription-sync.service.ts`:

- Remove `paidMeterIsPresent` as a subscription validity condition.
- Remove `MISSING_USAGE_METER` as a consequence of `plan.shopifyUsageEventHandle` being empty or absent from provider usage handles.
- Keep existing exact flat-rate plan-handle mapping, valid operational plan, included recovery allowance, billing-cycle, pending-plan and billing-period integrity rules.
- Compute the provider usage-event mapping using the new local component.
- In the same transaction/upsert that commits the current provider subscription, set `unmappedShopifyUsageEventHandles` to the complete unmapped provider-returned handle list.
- If no local plan exists for the provider-returned plan handle, keep the existing `UNMAPPED` status and exact `observedShopifyPlanHandle`, but set `lastSyncErrorCode = null` and `lastSyncErrorAt = null`. Do not persist `UNMAPPED_PLAN_HANDLE` as a sync error.
- If the operational plan exists but the catalogue plan is absent, keep the existing operational plan status and record all provider-returned usage-event handles as unmapped.
- If provider usage-event mappings are incomplete, keep provider-derived `ACTIVE`/`TRIALING`, and do not write sync-error metadata or schedule a retry solely for those mappings.
- Clear the array when Shopify confirms there is no active subscription/contract. Do not change it on a provider API failure.

In `app/services/billing/subscription-activation.service.ts`:

- Remove the `usageMeter` presence/membership requirement from `finalizeInitialPaidActivation` and any other initial paid activation validation.
- Keep exact plan identity, active plan, paid plan kind, included allowance, billing-cycle and unsupported-trial rules.
- Compute the unmapped provider usage-event handles using the same local mapping component inside the existing transaction and persist the array with the activation projection.
- An arbitrary or absent `shopifyRecoveryUsageEventHandle` must not produce `MISSING_USAGE_METER` or block activation.

Do not change `app/services/billing/providers/shopify-billing.provider.ts`'s current provider contract: it must continue to require exactly one valid `FlatRatePrice` plan handle and derive `usageEventHandles` only from Shopify `TieredPrice` items.

## Purchase/reporting boundaries

- Preserve the existing purchase rule: a purchase event must be both configured as a `MerchantPricingUsageEvent` and present in the provider-returned usage-event handles.
- A provider-returned but unmapped handle is not offered for purchase until Admin adds the exact matching catalogue event.
- Mapped provider events remain purchasable even if another returned event is unmapped.
- Do not change BillingOperation identity, quotes, confirmation, usage reporting, refund logic, credit balances or App Events reporting.
- Do not change the current App Events reporting handle to a billable usage handle.

## Tests

Update existing tests and add focused coverage for:

1. Paid Starter with arbitrary `shopifyRecoveryUsageEventHandle` absent from `usageEventHandles` activates successfully.
2. Paid Starter with null `shopifyRecoveryUsageEventHandle` activates/materialises if all other required plan configuration is valid.
3. Provider returns `bronze`, `silver`, `gold`; catalogue has `bronze`, `silver`; subscription remains ACTIVE/TRIALING and stores only `gold`.
4. Catalogue has an event absent from provider response; it is ignored and does not fail activation.
5. Unknown local plan handle projects `UNMAPPED`, keeps exact observed handle, and has null sync-error fields.
6. Existing operational plan without a catalogue plan remains usable while all provider-returned usage events are recorded as unmapped.
7. Admin-added matching event is removed from the unmapped array on the next successful sync.
8. Credit-pack purchase requests remain blocked for unmapped provider events and continue to work for mapped provider events.
9. Real provider/Prisma failures still follow existing failure logging and preserve original error details.

## Out of scope

- No Background or Admin source changes.
- No Shared package change.
- No provider GraphQL/parser contract change.
- No new table, enum, queue or scheduler.
- No change to App Events publisher, billing-operation accounting, refunds or WooCommerce.

## Validation

Run:

```bash
npx vitest run \
  tests/unit/services/billing/billing-plan-resolution.service.test.ts \
  tests/unit/services/billing/subscription-sync.service.test.ts \
  tests/unit/services/billing/subscription-activation.service.test.ts \
  tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts \
  tests/unit/services/shopify-billing.provider.test.ts

npx vitest run tests/integration/billing-activation.postgres.integration.test.ts
npx tsc --noEmit
npm run lint
git diff --check
```

Inspect `package.json` for the repository's actual test/build commands. Report exact command results and distinguish existing baseline failures from new failures.

## Stop condition

Submit the Completion Report with exact changed paths, branch SHA, database submodule pin and test evidence. Stop for architect review; do not execute Background, Admin or System Test tasks.
