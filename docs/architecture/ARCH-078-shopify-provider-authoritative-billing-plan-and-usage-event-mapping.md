---
id: ARCH-078
title: Shopify provider-authoritative billing plan and usage-event mapping
status: proposed
coordinator: moda_architect
created: 2026-11-22
updated: 2026-11-22
---

# ARCH-078 — Shopify provider-authoritative billing plan and usage-event mapping

## Purpose

Correct Shopify subscription projection so that local catalogue omissions are recoverable Admin configuration work, not false subscription synchronisation failures.

Shopify is authoritative for the flat-rate subscription plan handle and for the billable usage-event handles actually attached to the active subscription. Moda's `MerchantPricingPlan` and its `MerchantPricingUsageEvent` children define how those provider resources are configured and used by Moda.

The current false failure has two causes:

1. `shopifyRecoveryUsageEventHandle` is being compared with Shopify's billable `TieredPrice` usage-event handles, even though it is an App Events reporting handle and may be a customer-configured value.
2. Subscription validation treats incomplete/missing `MerchantPricingUsageEvent` mappings as though the Shopify subscription itself had failed to synchronise.

This architecture separates subscription identity, operational plan materialisation and usage-event catalogue mapping.

## Binding decisions

### 1. Subscription plan identity

- The Shopify subscription's single `FlatRatePrice` item supplies the exact `planHandle`.
- The existing Shopify provider parser's requirement for exactly one valid flat-rate plan handle remains. A malformed provider response with no usable flat-rate handle is still a provider-contract failure; Admin cannot register an exact handle that Shopify did not return.
- For a valid provider handle, resolve the existing operational `BillingPlan` by exact `shopifyPlanHandle`.
- If no operational `BillingPlan` exists, resolve `MerchantPricingPlan` by the same exact handle and materialise the operational plan from an eligible catalogue record using the existing materialisation rules.
- If neither an operational plan nor a catalogue plan exists for the returned handle, project the subscription as the existing `UNMAPPED` status, retain `observedShopifyPlanHandle`, and expose it through the existing Admin Unmapped Subscriptions workflow so an administrator can register the exact plan.
- An unknown local plan mapping is not `SYNC_ERROR`. Do not set `lastSyncErrorCode` or `lastSyncErrorAt` to `UNMAPPED_PLAN_HANDLE`. Do not create a retry loop for this administrative condition.
- If an operational `BillingPlan` already exists but its `MerchantPricingPlan` does not, preserve the existing operational-plan resolution behaviour. The provider usage-event handles are all unmapped until a matching catalogue plan and usage-event configuration are created.
- Existing handling for genuinely inactive or structurally invalid operational/catalogue plans remains unchanged except where this specification explicitly removes the reporting-handle prerequisite.

### 2. `shopifyRecoveryUsageEventHandle` is not a billable-meter mapping

`MerchantPricingPlan.shopifyRecoveryUsageEventHandle` and its operational copy `BillingPlan.shopifyUsageEventHandle` identify the event handle used by Moda's included-recovery App Events reporting.

- Shopify App Events reporting handles are not the `TieredPrice` billable usage-meter catalogue.
- The configured handle may be a customer-defined value. It need not appear in `provider.usageEventHandles`.
- Do not require this field to be non-empty as a prerequisite for subscription activation, plan materialisation, plan changes, billing-period rollover or reinstall reconciliation.
- Do not compare this field with `provider.usageEventHandles`.
- Do not classify its absence or non-membership as `MISSING_USAGE_METER`.
- Retain the database field and its existing use by the included-recovery App Events publisher. This task does not change reporting payloads, reporting idempotency, refund evidence or provider App Events publication semantics.
- Do not reinterpret this field as a `MerchantPricingUsageEvent.eventHandle`.

### 3. One-way usage-event mapping

Shopify's active subscription response supplies `usageEventHandles` from the subscription's `TieredPrice` items. These provider-returned handles are the candidate set. Do not compare the catalogue in both directions.

For the exact provider `planHandle`:

1. Load the matching `MerchantPricingPlan`, if one exists.
2. Load that plan's configured `MerchantPricingUsageEvent.eventHandle` values.
3. Consider only the handles returned by Shopify.
4. A provider-returned handle with an exact matching `MerchantPricingUsageEvent` is mapped and may be used by the existing purchase flow.
5. A provider-returned handle with no exact catalogue match is unmapped and is recorded for Admin attention.
6. A catalogue event not returned by Shopify is ignored. It is not a missing-provider error, is not added to the unmapped list, and is not made available for purchase until Shopify returns it.
7. If no `MerchantPricingPlan` exists, all provider-returned usage-event handles are currently unmapped. This does not change the `UNMAPPED` plan outcome.
8. If a plan exists but has no usage-event children, all provider-returned usage-event handles are unmapped. This does not block subscription activation.

Handle matching is exact and case-sensitive. Do not invent aliases, infer handles from labels, or derive a handle from `shopifyPlanHandle` or `shopifyRecoveryUsageEventHandle`. Deduplicate the persisted unmapped list and use a stable deterministic order.

There is no separate operational `BillingPlanUsageEvent` model in the current schema. Do not invent one. `MerchantPricingUsageEvent` remains the catalogue definition used by existing purchase/configuration code; provider-returned `TieredPrice` items determine which of those definitions are actually available on the subscription.

### 4. Durable Admin attention state

Add exactly one field to the existing `billing.Subscription` model:

```prisma
unmappedShopifyUsageEventHandles String[] @default([])
```

Its meaning is the unique set of usage-event handles returned by Shopify for the currently observed subscription that do not have a matching `MerchantPricingUsageEvent` under the corresponding `MerchantPricingPlan`.

- On every successfully committed current-subscription observation, replace the field with the complete result of the one-way mapping calculation.
- If the operational plan exists but the catalogue plan does not, store all provider-returned usage-event handles.
- If the provider returns no usage events, store `[]`.
- If an administrator adds a matching `MerchantPricingUsageEvent`, the next normal subscription reconciliation recomputes the list and removes the now-mapped handle.
- If Shopify removes a previously returned event, it disappears from the array on the next successful observation; catalogue-only events are not reported.
- When Shopify confirms there is no active subscription/contract, clear the array.
- A provider API failure does not constitute a new observation; preserve the last successfully observed array.
- The array is not an error code, retry marker or subscription lifecycle status.

Do not add a diagnostic table, enum, queue, scheduler, shared-package dependency or additional subscription status.

### 5. Subscription state and error semantics

| Condition | Subscription status | Sync error fields | Admin handling |
|---|---|---|---|
| Shopify plan handle has no local operational or catalogue mapping | `UNMAPPED` | `lastSyncErrorCode = null`, `lastSyncErrorAt = null` | Existing exact-handle plan registration workflow |
| Valid plan, one or more provider usage events lack catalogue entries | Remains provider-derived `ACTIVE` or `TRIALING` | No sync error | Show unmapped handles in existing Admin billing mapping view |
| All provider usage events are mapped | Provider-derived `ACTIVE` or `TRIALING` | No sync error | No mapping warning |
| Catalogue has an event Shopify does not return | Unchanged | No sync error | Ignore |
| Actual Shopify API/provider failure | Existing genuine failure handling | Existing error semantics | Existing Sync Errors workflow |
| Actual database/materialisation/period-integrity failure | Existing genuine failure handling | Existing error semantics | Existing Sync Errors workflow |

A usage-event mapping discrepancy must not:
- change an otherwise valid `ACTIVE`/`TRIALING` subscription to `SYNC_ERROR`;
- populate `lastSyncErrorCode` or `lastSyncErrorAt`;
- prevent a valid plan from being materialised;
- prevent included-plan entitlement/billing-period projection;
- schedule repeated retries solely because an administrator has not configured a usage event.

A missing plan mapping uses the existing `UNMAPPED` state and Admin repair flow, not `SYNC_ERROR`.

### 6. Admin workflow

Reuse the existing `/billing?view=unmapped` Unmapped Subscriptions view.

- Include subscriptions whose status is `UNMAPPED` and subscriptions whose `unmappedShopifyUsageEventHandles` array is non-empty, including otherwise valid `ACTIVE` and `TRIALING` subscriptions.
- Show the subscription status, exact observed Shopify plan handle and each unmapped provider usage-event handle.
- If the exact catalogue plan is missing, link to the existing exact-handle Register Plan workflow.
- If the catalogue plan exists, link to its existing Merchant Pricing Plan editor so the administrator can add the exact missing `MerchantPricingUsageEvent`.
- Do not offer the existing `UNMAPPED` operational-repair action for an `ACTIVE`/`TRIALING` usage-event-only row.
- After the administrator saves the missing usage-event configuration, the next normal reconciliation clears the array. No new Admin action or queue is required.
- The Admin Shopify contract validator must not use `shopifyRecoveryUsageEventHandle` as a subscription validation gate.

### 7. Purchase and accounting boundaries

- Existing credit-pack purchase processing remains strict: a purchase is allowed only for a `MerchantPricingUsageEvent` configured for the plan and a provider usage event actually returned by Shopify.
- An unmapped provider usage event is not offered for purchase until an administrator configures the matching catalogue event.
- Already mapped provider usage events remain available even if another returned event is unmapped.
- Preserve included recovery credit reservation/commit/release, purchased-credit accounting, promotional-credit priority, usage reporting, refund calculations and the 30-day Shopify refund evidence window.
- Preserve the existing App Events reporting path and all actual provider error messages.
- Do not change WooCommerce billing.

## Repository ownership and task order

| Task | Repository | Responsibility | Dependency |
|---|---|---|---|
| `ARCH-078-DATABASE-001` | `moda-interact-database` | Add the durable Subscription array and forward migration | None |
| `ARCH-078-BACKGROUND-001` | `moda-interact-background` | Correct provider-authoritative mapping across Background reconciliation/lifecycle paths | DATABASE-001 |
| `ARCH-078-SHOPIFY-001` | `moda-interact` | Correct Shopify app plan resolution and initial/current subscription projection | DATABASE-001 |
| `ARCH-078-ADMIN-001` | `moda-interact-admin` | Display and resolve plan/usage-event mapping attention in existing billing Admin | DATABASE-001 |
| `ARCH-078-SYSTEM-TEST-001` | `moda-interact-system-test` | Verify the complete cross-repository lifecycle | DATABASE-001, BACKGROUND-001, SHOPIFY-001, ADMIN-001 |

DATABASE-001 is the only prerequisite. BACKGROUND-001, SHOPIFY-001 and ADMIN-001 may proceed in parallel after the accepted database migration and regenerated Prisma client are available. SYSTEM-TEST-001 runs last.

## Non-goals

- No change to Shopify's provider response parser requiring one `FlatRatePrice` item.
- No new plan aliases or per-merchant plan overrides.
- No new `SubscriptionProjectionStatus`.
- No new diagnostic table, queue, scheduler, Admin subsystem or Shared package.
- No `docs/decisions/**/_index.md` edits.
- No deletion or rename of `shopifyRecoveryUsageEventHandle`, `BillingPlan.shopifyUsageEventHandle`, legacy billing fields or App Events publisher.
- No changes to credit consumption, top-up purchase economics, refund policy, App Events payloads, usage-report retries or WooCommerce.

## Acceptance boundary

A subscription is accepted when the exact Shopify flat-rate plan handle resolves to a valid operational plan. Usage-event mapping is a separate, one-way catalogue concern. A missing usage-event catalogue entry is durably visible to Admin but does not invalidate the subscription. A missing local plan mapping is `UNMAPPED`, not a sync error. Actual provider, database and billing-period integrity failures retain their existing error handling.

Implementation agents must stop and report if the current canonical repository/submodule state materially differs from the reviewed snapshots or if a requested behaviour would require a new persistence mechanism beyond the approved Subscription array.
