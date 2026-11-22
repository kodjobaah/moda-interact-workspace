---
id: ARCH-078-ADMIN-001
architecture_id: ARCH-078
title: Display unmapped Shopify usage-event handles in existing billing Admin
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-078-DATABASE-001]
enables: [ARCH-078-SYSTEM-TEST-001]
created: 2026-11-22
updated: 2026-11-22
---

# ARCH-078-ADMIN-001 — Display unmapped Shopify usage-event handles in existing billing Admin

## Architecture and dependency

Follow [ARCH-078](../../../architecture/ARCH-078-shopify-provider-authoritative-billing-plan-and-usage-event-mapping.md).

Hard dependency: `ARCH-078-DATABASE-001` must be architect-accepted and the Admin Prisma client must expose `Subscription.unmappedShopifyUsageEventHandles`.

## Objective

Reuse the existing `/billing?view=unmapped` Admin surface to display both:
- subscriptions with status `UNMAPPED` whose exact Shopify plan handle needs a catalogue/operational plan mapping;
- otherwise valid `ACTIVE`/`TRIALING` subscriptions with one or more provider-returned usage-event handles that lack `MerchantPricingUsageEvent` catalogue entries.

Do not put usage-event mapping discrepancies in the Sync Errors view.

## Read before editing

Read these exact files:

```text
src/lib/admin/unmapped-subscriptions.ts
src/components/admin/billing-unmapped-subscriptions.tsx
src/lib/admin/shopify-subscription-contract.ts
src/app/actions/billing-unmapped-subscriptions.ts
src/app/(protected)/billing/page.tsx
src/lib/admin/merchant/pricing-plan.ts
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/billing-drawers.tsx
tests/security/admin-merchant-pricing-plan.test.mjs
tests/security/admin-billing-sync-errors.test.mjs
```

Inspect current plan-builder routes and actions before adding links. Reuse existing `/billing?view=plans&planId=...` and `drawer=register-plan` navigation.

## Data/query contract

In `src/lib/admin/unmapped-subscriptions.ts`:

- Add `status` and `unmappedShopifyUsageEventHandles` to the subscription list/detail projection types and Prisma selects.
- Change the list and detail filters from `status = UNMAPPED` to the logical union:
  - `status = UNMAPPED`, OR
  - `unmappedShopifyUsageEventHandles` is not empty.
- Preserve pagination, tenant/shop identity, ordering and existing exact-handle plan resolution.
- `ACTIVE`/`TRIALING` rows with non-empty arrays must be returned without changing their database status.
- A row with no catalogue plan and non-empty array must still be returned so Admin can register the exact plan handle.
- The detail query must allow a subscription through when it is `UNMAPPED` or its unmapped array is non-empty. Do not make the existing `resolveUnmappedSubscriptionAction` accept ACTIVE/TRIALING subscriptions.

## Shopify contract validator

In `src/lib/admin/shopify-subscription-contract.ts`:

- Remove `shopifyRecoveryUsageEventHandle` from the contract-validation input contract and remove the check that it is present in, or absent from, provider usage-event items.
- It must not block Admin plan repair or subscription mapping.
- Continue to verify the exact flat-rate plan handle, expected plan item type, billing period, recurring amount and currency using the existing `VERIFIED` / `MONETARY_MISMATCH` / `MISMATCH` / `UNAVAILABLE` outcomes.
- Do not add symmetric validation requiring every catalogue `MerchantPricingUsageEvent` to appear in Shopify. Shopify-returned provider usage events are handled by the durable unmapped array.
- Keep `providerItems` in the detail evidence so the administrator can inspect the actual Shopify response.

## Admin UI behaviour

In `src/components/admin/billing-unmapped-subscriptions.tsx`:

1. Keep the existing `/billing?view=unmapped` route and existing exact-handle plan registration/operational repair flow.
2. Show the Subscription status in the list.
3. Add a column/section for `unmappedShopifyUsageEventHandles`, showing the exact provider-returned handles. Do not substitute event labels or infer names.
4. For `CATALOGUE_MISSING`, retain the existing **Register exact plan handle** action.
5. For a row with a catalogue plan and non-empty unmapped usage-event handles, add a **Configure usage events** link to the existing Merchant Pricing Plan editor for that exact `cataloguePlan.id`.
6. Do not show the `resolveUnmappedSubscriptionAction` operational-repair form for an `ACTIVE`/`TRIALING` row whose only issue is usage-event mapping. The action remains limited to the existing `UNMAPPED` plan-resolution workflow.
7. In the detail drawer, show the outstanding handles and the configured `MerchantPricingUsageEvent` handles so the operator can see which exact events need adding.
8. If a catalogue plan is missing, show the provider plan handle and outstanding provider usage-event handles alongside the Register Plan action.
9. Once the array is empty, the row must disappear unless the subscription remains `UNMAPPED` for a separate plan-mapping reason.
10. Rename any misleading UI label that presents `shopifyRecoveryUsageEventHandle` as a billable usage meter. If displayed for diagnostics, label it **Included-recovery App Event reporting handle** and explicitly state it is not a Shopify billable usage-meter mapping.

The existing Merchant Pricing Plan builder already owns adding/editing `MerchantPricingUsageEvent` records. Do not create another event editor or a new Admin action.

## Tests

Add a focused Admin test, for example:

```text
tests/security/admin-unmapped-shopify-usage-event-mappings.test.mjs
```

Cover:
- list query includes `UNMAPPED` rows and ACTIVE/TRIALING rows with a non-empty array;
- ACTIVE/TRIALING status is displayed and is not rewritten;
- exact unmapped provider handles are rendered;
- missing catalogue plan links to Register Plan;
- existing catalogue plan links to its editor;
- ACTIVE/TRIALING usage-event-only rows do not render/submit the UNMAPPED repair action;
- clearing the array removes the usage-event-only row from the Admin attention view;
- Admin contract validation does not inspect `shopifyRecoveryUsageEventHandle`;
- catalogue-only events absent from provider response are not represented as unmapped.

Update existing contract and unmapped-subscription tests as needed. Keep authorization and existing SUPER_ADMIN mutation checks unchanged.

## Out of scope

- No database schema or migration in this task.
- No new diagnostics table, service, queue or dashboard.
- No changes to plan economics, credit-pack purchase pricing, billing operations, refunds or App Events reporting.
- No changes to Shared, Background or Shopify application code.
- No `_index.md` edits.

## Validation

Run:

```bash
node --test tests/security/admin-unmapped-shopify-usage-event-mappings.test.mjs
node --test tests/security/admin-merchant-pricing-plan.test.mjs
node --test tests/security/admin-billing-sync-errors.test.mjs
npm run test:unit
npm run lint
npm run build
git diff --check
```

Inspect `package.json` and existing test scripts before running. Report exact results and distinguish baseline failures.

## Stop condition

Submit a Completion Report with exact changed paths, test output and branch SHA. Stop for architect review. Do not execute System Test.
