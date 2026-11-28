---
id: ARCH-078-BACKGROUND-001
architecture_id: ARCH-078
title: Project Shopify subscriptions independently of usage-event catalogue mappings
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-078-DATABASE-001]
enables: [ARCH-078-SYSTEM-TEST-001]
created: 2026-11-22
updated: 2026-11-22
---

# ARCH-078-BACKGROUND-001 — Project provider-authoritative billing mappings

## Architecture and dependency

Follow [ARCH-078](../../../architecture/ARCH-078-shopify-provider-authoritative-billing-plan-and-usage-event-mapping.md).

Hard dependency: `ARCH-078-DATABASE-001` must be architect-accepted and the corresponding database submodule pin and generated Prisma client must be present before implementation.

## Objective

Remove the false subscription validation that treats `BillingPlan.shopifyUsageEventHandle` as a Shopify billable usage meter. Use Shopify's exact plan handle to resolve/materialise the operational plan, and use only Shopify-returned usage-event handles as candidates for matching against `MerchantPricingPlan.usageEvents`.

Persist returned-but-unmapped event handles to `Subscription.unmappedShopifyUsageEventHandles`. Missing event catalogue mappings must not block an otherwise valid subscription or produce `SYNC_ERROR`.

## Read before editing

Read these exact current files and their focused tests:

```text
src/services/billing-plan-materialization.service.ts
src/services/billing-reconciliation.service.ts
src/services/billing-reconciliation/established-plan-observation.service.ts
src/services/billing-reconciliation/observed-plan-projection.ts
src/services/billing-reconciliation/plan-change-target-prerequisites.ts
src/services/billing-reconciliation/shopify-event-handle-validation.ts
src/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.ts
src/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.ts
src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts
src/services/same-plan-billing-period-rollover.service.ts
src/services/shopify-plan-change-transition.service.ts
src/services/shopify-subscription-lifecycle-reconciliation.service.ts
src/providers/shopify-partner-billing.provider.ts
tests/unit/services/billing-plan-materialization.service.test.ts
tests/unit/services/billing-reconciliation.service.test.ts
tests/unit/services/billing-reconciliation/established-plan-observation.service.test.ts
tests/unit/services/billing-reconciliation/generic-subscription-projection.service.test.ts
tests/unit/services/billing-reconciliation/shopify-event-handle-validation.test.ts
tests/unit/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.test.ts
tests/unit/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.test.ts
tests/unit/services/billing-subscription-reconciliation/reinstall-reconciliation.service.test.ts
tests/unit/services/same-plan-billing-period-rollover.service.test.ts
tests/unit/services/shopify-plan-change-transition.service.test.ts
tests/unit/services/shopify-subscription-lifecycle-reconciliation.service.test.ts
```

Search the complete repository for every use of:

```text
hasValidRecoveryReportingHandle
shopifyUsageEventHandle
shopifyRecoveryUsageEventHandle
MISSING_USAGE_METER
UNMAPPED_PLAN_HANDLE
unmappedShopifyUsageEventHandles
```

Do not assume the listed files are the only consumers.

## Required local mapping component

Create one small Background-local component:

```text
src/services/billing-reconciliation/shopify-usage-event-mapping.ts
```

It must be reusable by the Background reconciliation/lifecycle call sites and must not be added to `moda-interact-shared`.

Contract:

- Accept the exact provider `planHandle` and `PartnerSubscription.usageEventHandles`.
- Read `MerchantPricingPlan.usageEvents.eventHandle` for that exact plan handle through the injected Prisma client/transaction boundary.
- Return the exact provider handles that have matching catalogue event handles and the exact provider handles that do not.
- If the catalogue plan does not exist, return all provider-returned handles as unmapped.
- If the catalogue exists but has no usage events, return all provider-returned handles as unmapped.
- If Shopify returns no usage-event handles, return an empty unmapped list.
- Ignore catalogue-only handles that Shopify did not return.
- Match exact handles; do not lowercase, alias, derive or match by admin label.
- Deduplicate provider handles and return a deterministic stable ordering.
- Do not create or mutate `MerchantPricingUsageEvent` rows. Admin owns catalogue authoring.
- The helper must not read or write `Subscription`; callers write the returned array inside their existing projection transaction.

Use this one component at every Background provider-subscription observation path. Do not duplicate the set-comparison logic in each service.

## Plan materialisation and reporting-handle correction

In `src/services/billing-plan-materialization.service.ts`:

- Continue to resolve an existing operational `BillingPlan` by exact `shopifyPlanHandle`.
- If absent, resolve the exact `MerchantPricingPlan` and retain existing `isActive`, `publicationStatus`, included-credit, required-feature and other genuine catalogue checks.
- Remove `shopifyRecoveryUsageEventHandle`/its operational copy from materialisation prerequisites. A missing or customer-defined reporting handle must not return `INVALID_CATALOGUE_PLAN`.
- Do not reject a Free plan solely because that optional App Events reporting field is populated.
- When materialising a paid `BillingPlan`, copy the configured reporting handle to nullable `BillingPlan.shopifyUsageEventHandle` if present; otherwise store `null`. Do not assert non-null.
- Preserve the current included-recovery allowance, feature materialisation, transaction isolation and concurrent-winner handling.
- Preserve the existing reporting publisher's use of `BillingPlan.shopifyUsageEventHandle`; do not change App Events payloads or refund evidence.

In every reconciliation/transition path, remove `hasValidRecoveryReportingHandle` as a subscription or plan-transition prerequisite. It must no longer compare `shopifyUsageEventHandle` with `provider.usageEventHandles`, require a non-empty handle, return `MISSING_USAGE_METER`, or prevent plan materialisation/activation/rollover/reinstall.

Keep the separate legacy `recoveryCreditPackEnabled` / `shopifyRecoveryCreditPackEventHandle` behaviour unchanged in this task. Newly materialised MerchantPricing plans continue to use the current `recoveryCreditPackEnabled: false` behaviour. Do not conflate that legacy single-pack field with the `MerchantPricingUsageEvent` catalogue.

## Subscription projection rules

### A. Unknown local plan mapping

When Shopify returns a valid flat-rate `planHandle`, but neither an existing operational `BillingPlan` nor an eligible `MerchantPricingPlan` can resolve it:

- Set the existing `Subscription.status` to `UNMAPPED`.
- Persist the exact `observedShopifyPlanHandle`.
- Preserve the existing unmapped billing-period snapshot/history behaviour.
- Set `lastSyncErrorCode = null` and `lastSyncErrorAt = null`; do not store `UNMAPPED_PLAN_HANDLE` in sync-error fields.
- Do not set `SYNC_ERROR`.
- Do not publish a repeated retry solely for the missing catalogue/operational mapping. The existing Admin exact-handle repair workflow owns the correction and requests/reaches normal reconciliation.
- Compute `unmappedShopifyUsageEventHandles` against the absent catalogue as all usage-event handles returned by Shopify.

Do not change the provider parser's malformed-response behaviour when Shopify returns no usable flat-rate handle at all.

### B. Existing operational plan but no MerchantPricingPlan

Preserve the existing active operational-plan resolution. Do not mark a valid active subscription `UNMAPPED` solely because the catalogue record is missing. Since there is no MerchantPricingUsageEvent catalogue to match against, store all provider-returned usage-event handles in `unmappedShopifyUsageEventHandles` for Admin to register the exact catalogue plan and its events.

### C. Valid plan with incomplete usage-event mappings

- Resolve/materialise the plan normally.
- Keep `Subscription.status` equal to provider-derived `ACTIVE` or `TRIALING`.
- Write only the unmapped provider-returned handles to `unmappedShopifyUsageEventHandles`.
- Keep `lastSyncErrorCode` and `lastSyncErrorAt` clear for this mapping-only condition.
- Do not return `MISSING_USAGE_METER`, schedule a retry, reject a plan transition, skip a billing-period rollover or block reinstall solely because a MerchantPricingUsageEvent catalogue mapping is missing.
- Existing mapped usage events remain usable. An unmapped event remains unavailable to purchase until Admin creates its matching catalogue event.

### D. Fully mapped or removed provider events

- When all provider-returned usage-event handles have exact catalogue matches, write `[]`.
- When Shopify no longer returns a previously unmapped handle, remove it on the next successful observation.
- Catalogue-only usage events are ignored and never added to the array.
- When Shopify confirms there is no active subscription/contract, clear the array.
- When the Shopify API call fails, preserve the last successfully observed array; provider failure handling and original error logging remain unchanged.

### E. Transaction and concurrency rules

- Write the complete array in the same existing transaction that commits the subscription projection.
- Use the existing subscription lifecycle lock, expected-state fence, provider lifecycle ordering and stale-job checks at each call site.
- Do not implement read-modify-write array appends. Recompute and replace the array from the provider snapshot and exact catalogue state.
- Do not overwrite unrelated Subscription fields or weaken existing billing-period/entitlement transaction guards.

## Exact Background call sites to audit

At minimum update and test the existing validation/projection paths in:

```text
src/services/billing-reconciliation/observed-plan-projection.ts
src/services/billing-reconciliation/established-plan-observation.service.ts
src/services/billing-reconciliation/plan-change-target-prerequisites.ts
src/services/billing-reconciliation.service.ts
src/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.ts
src/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.ts
src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts
src/services/same-plan-billing-period-rollover.service.ts
src/services/shopify-plan-change-transition.service.ts
src/services/shopify-subscription-lifecycle-reconciliation.service.ts
```

Also inspect every caller discovered by the required repository-wide search. Do not leave a secondary lifecycle, reinstall, plan-change or rollover path capable of writing `SYNC_ERROR` from `shopifyRecoveryUsageEventHandle` membership.

## Tests

Add focused tests for the new mapping component and update existing focused tests.

Required cases:

1. Exact provider event handles with exact catalogue matches return mapped and no unmapped handles.
2. Provider returns `bronze`, `silver`, `gold`; catalogue contains only `bronze`, `silver`; unmapped result is exactly `gold`.
3. Catalogue contains `bronze`, `silver`, `gold`; provider returns only `bronze`; result is empty. Missing provider-side `silver`/`gold` is not an error.
4. No catalogue plan or no usage-event children means every provider-returned handle is unmapped.
5. Empty provider usage-event list produces `[]`.
6. Duplicate provider handles are deduplicated deterministically.
7. Arbitrary, empty or provider-absent `shopifyRecoveryUsageEventHandle` does not invalidate paid materialisation or activation.
8. Existing plan identity, included allowance, billing-cycle, concurrency, stale-job and period-integrity guards remain enforced.
9. Unknown local plan maps to `UNMAPPED`, preserves exact observed handle, has null sync-error fields and does not publish a repeated retry solely for configuration.
10. Active and trialing subscriptions with unmapped event handles remain ACTIVE/TRIALING and persist the array without sync-error metadata.
11. Admin correction followed by next reconciliation clears the resolved handle.
12. Provider API/database errors still follow existing genuine error handling and preserve original provider error message/details.
13. Existing legacy credit-pack path remains unchanged and is not confused with MerchantPricingUsageEvent mapping.

Add one disposable-PostgreSQL integration test under:

```text
tests/integration/shopify-usage-event-mapping.integration.test.ts
```

It must prove the Subscription array is committed atomically with status/plan/billing-period projection and is cleared on a later successful observation.

## Out of scope

- No changes to credit reservation/commit/release, purchased-credit balances, promotion priority, BillingOperation quote/confirm/refund logic or Shopify refund calculations.
- No change to App Events reporting handle payload or the 30-day refund evidence policy.
- No Shared package change.
- No Admin implementation in this task.
- No WooCommerce code change.
- No new table, queue, scheduler or Subscription status.

## Validation

Run the focused Vitest suites listed above plus the new mapping tests and integration test, then:

```bash
npx tsc --noEmit
npm run lint
git diff --check
```

Run the repository's existing focused integration command (`node scripts/test-integration.mjs tests/integration/shopify-usage-event-mapping.integration.test.ts`) and report the actual disposable PostgreSQL/Redis environment and cleanup evidence. Inspect `package.json` before selecting any additional project scripts.

## Stop condition

Submit a Completion Report with exact changed paths, tests, worktree/branch SHA, database submodule pin and cleanup evidence. Stop for architect review. Do not execute Shopify, Admin or System Test tasks.
