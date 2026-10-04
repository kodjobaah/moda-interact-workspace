---
id: ARCH-027-SHOPIFY-001
architecture_id: ARCH-027
title: Preserve Shopify billing compatibility across provider-aware persistence
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 105
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-SHOPIFY-002
  - ARCH-027-DATABASE-001
enables: []
created: 2026-10-04
updated: 2026-10-04
---

# Preserve Shopify billing compatibility across provider-aware persistence

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Adapt the existing Shopify merchant application to the bounded ARCH-027 provider-aware database schema **without changing Shopify billing product behavior**.

The required result is:

```text
existing Shopify hosted pricing
existing Shopify subscription reconciliation
existing Shopify BillingPlan materialisation
existing Shopify included-credit periods
existing Shopify App Event reporting
existing Shopify top-up purchase flow
existing Shopify purchase history/refund/reactivation
        |
        v
same merchant behavior as before ARCH-027
```

while every Shopify-owned purchase/refund/usage row is now explicit and valid under the ARCH-027 provider-conditional persistence contract:

```text
RecoveryCreditPurchase.provider = SHOPIFY
RecoveryCreditRefund.provider   = SHOPIFY
UsageEvent.provider             = SHOPIFY
```

and Shopify code never accidentally reads or mutates Woo provider rows merely because the generic tables now support both providers.

This is a **compatibility task**, not a multi-provider refactor of `moda-interact`.

The existing Shopify provider types remain Shopify-specific:

```text
BillingProvider
ProviderSubscription.provider = "SHOPIFY"
shopifyShopId
shopifyPlanHandle
Shopify Partner/App Pricing APIs
```

Do not genericize them merely because Woo now exists in other repositories.

## Context

ARCH-027 intentionally preserves the existing Shopify billing architecture and introduces Woo as a bounded adapter around the shared Moda business state.

DATABASE-001 changes the physical purchase/refund schema in ways that affect TypeScript/Prisma consumers even though Shopify runtime behavior must remain unchanged:

### `RecoveryCreditPurchase`

Adds:

```text
provider          default SHOPIFY
providerReference nullable
```

and makes these fields nullable at schema level so Woo can avoid fabricating Shopify evidence:

```text
billingPeriodId
shopifyPlanHandleSnapshot
shopifyEventHandleSnapshot
providerSubscriptionIdSnapshot
providerUsageQuantityBeforeSnapshot
providerUsageCostBeforeSnapshot
providerUsageCostCurrencyBeforeSnapshot
usageEventId
```

The database still requires those fields to be present for:

```text
provider = SHOPIFY
```

### `RecoveryCreditRefund`

Adds:

```text
provider default SHOPIFY
```

and makes Shopify-context snapshots nullable at the physical schema level:

```text
billingPeriodIdSnapshot
providerSubscriptionIdSnapshot
planHandleSnapshot
eventHandleSnapshot
```

The database still requires them for:

```text
provider = SHOPIFY
```

### `BillingPeriodEntitlementCounter`

Adds:

```text
currentAllowanceQuantity Int?
```

Existing Shopify rows migrate with:

```text
currentAllowanceQuantity = NULL
```

ARCH-027 does not change Shopify plan-switch allowance semantics.

### Current source assumptions that need explicit compatibility hardening

The supplied current source shows:

- `RecoveryCreditPurchaseRequestService` relies on DB defaults for `UsageEvent.provider` and the new purchase provider discriminator does not yet exist in source;
- `RecoveryCreditPurchaseManagementService` queries purchase history/refunds only by `shopId`, assumes Shopify snapshot fields are statically non-null and does not yet filter by provider;
- `MerchantBillingReadService` reads REQUESTED/latest purchases for a Shop and assumes Shopify event-handle/usage evidence;
- Shopify refund creation snapshots `billingPeriodId`, provider subscription identity and Shopify handles and must continue requiring all of them;
- Shopify BillingPeriod writers create included counters without the new current-allowance field;
- `BillingPlanResolutionService` is deliberately Shopify-specific and keyed by `shopifyPlanHandle`.

The compatibility change must make the provider boundary explicit while preserving the existing merchant-facing Shopify contracts.

## Scope

Modify only `moda-interact` implementation/tests plus its nested accepted `database/` gitlink.

Expected primary production areas:

```text
app/services/billing/
  billing-plan-resolution.service.ts
  billing-period-projection.ts
  subscription-activation.service.ts
  merchant-billing-read.service.ts
  merchant-recovery-capacity-read.service.ts
  recovery-credit-purchase-request.service.ts
  recovery-credit-purchase-management.service.ts

tests/unit/services/billing/
tests/unit/services/
tests/unit/
```

Additional directly related route/UI types may change only where Prisma nullability requires safe narrowing.

Do not modify `moda-interact-database` schema/migrations in this task.

## Out of Scope

- Woo API/client/webhook behavior.
- Woo plugin/UI.
- Woo Background reconciliation.
- Woo Admin support.
- Genericizing `BillingProvider`.
- Renaming Shopify fields.
- Removing `shopifyPlanHandle`.
- Replacing hosted Shopify pricing.
- Changing ARCH-011 Shopify plan-change semantics.
- Changing Shopify top-up catalogue/pricing semantics.
- Enforcing `maximumUnitsPerBillingPeriod`.
- Adding Woo rows to Shopify UI.
- New database migrations.
- Gateway/system-test work.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Consume the accepted ARCH-027 database contract

Update the `moda-interact/database` nested gitlink to the newest compatible architect-accepted `moda-interact-database` main commit containing `ARCH-027-DATABASE-001`.

Regenerate Prisma before editing source assumptions.

Do not copy/edit Prisma schema locally in `moda-interact`.

### R2 — Shopify purchase creation is explicitly provider-scoped

`RecoveryCreditPurchaseRequestService` must create Shopify purchases with:

```text
provider = SHOPIFY
```

explicitly.

Do not depend only on the database default.

The created purchase must still provide every Shopify-required acquisition field:

```text
billingPeriodId non-null
shopifyPlanHandleSnapshot non-null/non-blank
shopifyEventHandleSnapshot non-null/non-blank
providerSubscriptionIdSnapshot non-null/non-blank
providerUsageQuantityBeforeSnapshot non-null
providerUsageCostBeforeSnapshot non-null
providerUsageCostCurrencyBeforeSnapshot non-null
usageEventId non-null
```

All existing Shopify provider-before evidence/revalidation remains unchanged.

### R3 — Shopify top-up UsageEvent creation is explicit

The purchase-acquisition `UsageEvent` created by the Shopify top-up path must explicitly write:

```text
provider = SHOPIFY
shopifyReportState = PENDING
shopifyEventHandle = selected Shopify event handle
shopifyIdempotencyKey = existing deterministic Shopify key
```

Do not rely on the `UsageEvent.provider` database default.

Do not change quantity, event-handle, billing-period or reporting semantics.

### R4 — Shopify purchase history is provider-isolated

Every Shopify merchant purchase-history query must include:

```text
shopId = authenticated Shopify Shop
provider = SHOPIFY
```

Woo `RecoveryCreditPurchase` rows must never appear in the Shopify application purchase manager even if inconsistent/future data places both provider rows under one Shop.

Status/page/order semantics remain exactly the existing Shopify implementation.

### R5 — Shopify billing-summary top-up reads are provider-isolated

Every `MerchantBillingReadService` query that interprets:

```text
REQUESTED purchases
latest purchase
purchase event handle
purchase UsageEvent Shopify report state
```

must include:

```text
provider = SHOPIFY
```

Do not interpret a Woo purchase with null Shopify snapshots as a Shopify top-up.

### R6 — Physical nullability does not weaken Shopify runtime invariants

Generated Prisma types may now expose nullable fields.

For a row with:

```text
provider = SHOPIFY
```

Shopify services must fail closed if required Shopify evidence is unexpectedly null.

Required evidence includes, according to the owning path:

```text
billingPeriodId
shopifyPlanHandleSnapshot
shopifyEventHandleSnapshot
providerSubscriptionIdSnapshot
usageEventId / usageEvent
Shopify provider-before evidence
```

Do not substitute:

```text
"unknown"
empty string
current plan handle
current event handle
current billing period
```

for missing historical evidence.

### R7 — Shopify purchase-history output contract stays non-null

The current Shopify merchant purchase-history API/UI contract continues to expose:

```text
planName
planHandle
eventHandle
```

as non-null Shopify values.

Narrow/validate the provider-specific nullable database row before constructing that response.

Do not change the Shopify UI contract merely because Woo rows use null Shopify fields.

### R8 — Shopify refund requests are explicitly provider-scoped

`RecoveryCreditPurchaseManagementService.requestRefund*()` must load/mutate only:

```text
purchase.provider = SHOPIFY
```

for the Shopify merchant flow.

A cross-provider row must behave like an unavailable/not-found purchase under the existing tenant-safe contract; it must not enter Shopify provider-context verification.

### R9 — Shopify refund creation writes provider explicitly

Every Shopify-created `RecoveryCreditRefund` must write:

```text
provider = SHOPIFY
```

explicitly.

It must continue to snapshot non-null:

```text
billingPeriodIdSnapshot
providerSubscriptionIdSnapshot
planHandleSnapshot
eventHandleSnapshot
```

plus the existing Shopify Partner development/economic evidence.

No Shopify refund may be persisted with null Shopify provenance merely because the shared schema now permits Woo nulls.

### R10 — Shopify reactivation is provider-isolated

`reactivateRefund()` must only reactivate:

```text
purchase.provider = SHOPIFY
refund.provider = SHOPIFY
```

under the existing Shopify pre-provider-action rules.

Woo refund rows must not be mutated by Shopify merchant routes.

### R11 — Unique-conflict recovery is tenant + provider scoped

When Shopify refund creation handles:

```text
P2002
```

for request-key/live-refund races, every authoritative re-read must prove:

```text
purchase.shopId = authenticated Shop
purchase.provider = SHOPIFY
refund.provider = SHOPIFY
```

before returning an existing outcome.

Do not return a cross-provider refund merely because an ID/request key collides.

### R12 — Current Shopify provider-context refund rule remains unchanged

Keep the current Shopify rule:

```text
active purchase refund requires current Shopify provider/meter context
```

including:

```text
shopifyShopId
current active/trial Shopify subscription
providerSubscriptionIdSnapshot identity
shopifyPlanHandleSnapshot
billingPeriodId/current provider cycle
shopifyEventHandleSnapshot in provider usage handles
```

Do not adopt API-006's Woo purchase-local refund rule into Shopify.

### R13 — Shopify development zero-value purchase/refund behavior remains unchanged

Preserve the accepted existing behavior where Shopify Partner development context may have:

```text
providerPurchaseAmount = 0
```

and remain eligible according to the current development-mode rules.

Woo's strict positive provider amount must not leak into Shopify logic.

### R14 — Shopify included-period writers keep current allowance unset

Every Shopify-owned included-period counter creation/repair path must leave:

```text
currentAllowanceQuantity = NULL
```

explicitly or through an asserted database default.

This includes current source paths such as:

```text
BillingPeriodProjection
SubscriptionActivationService
```

Do not set:

```text
currentAllowanceQuantity = grantedQuantity
```

for Shopify merely because the field exists.

ARCH-027 current-allowance mutation belongs to Woo Background plan switching.

### R15 — Shopify capacity reads preserve exact legacy semantics

For valid Shopify rows where:

```text
currentAllowanceQuantity = NULL
```

existing outputs remain byte-for-behavior equivalent:

```text
paid included granted/remaining
free lifetime
promotional
purchased
top-up eligibility
capacity source
```

Do not apply Woo downgrade/current-allowance semantics to Shopify merchant presentation.

If source code must read `currentAllowanceQuantity` to validate the generated Prisma shape, valid null must behave exactly as before.

### R16 — Unexpected Shopify non-null current allowance fails closed

Because ARCH-027 does not change Shopify plan-switch semantics, a Shopify current paid counter with:

```text
currentAllowanceQuantity != NULL
```

is not a valid state produced by `moda-interact`.

Shopify merchant read/capacity code must not silently reinterpret the Shopify allowance using Woo semantics.

Fail closed through the service's existing configuration-unavailable/integrity path rather than changing merchant capacity.

This catches accidental provider-semantic leakage.

### R17 — BillingPlanResolutionService remains Shopify-specific

Do not weaken the existing Shopify catalogue validation:

```text
FREE:
    no Shopify recovery usage meter

PAID_METERED:
    non-blank Shopify recovery usage meter
```

Do not remove:

```text
shopifyPlanHandle
```

or change the public method contract from:

```text
resolveOrMaterializeBillingPlan(planHandle)
```

to a generic provider API.

ARCH-027 API owns its own bounded Woo-side use of the same operational materialisation semantics.

### R18 — Pre-existing materialised plan is reused deterministically

Add regression proof that when the operational `BillingPlan` for a Shopify `shopifyPlanHandle` already exists — including the case where another accepted runtime may have materialised it first — Shopify:

```text
reuses the same BillingPlan row
does not create a duplicate
does not change its provider-independent plan identity
marks MerchantPricingPlan.materializedAt when still null
```

Existing unique-race behavior remains green.

### R19 — Shopify subscription projection remains Shopify-owned

Preserve existing behavior around:

```text
observedShopifyPlanHandle
pendingShopifyPlanHandle
Shopify currentPeriodStart/currentPeriodEnd
providerSubscriptionId
Shopify lifecycle event reconciliation
```

Do not start reading Woo operations/webhook receipts in `moda-interact`.

### R20 — Shopify App Event publication remains unchanged

Shopify reportable UsageEvents remain:

```text
provider = SHOPIFY
shopifyReportState IN (PENDING, RETRYABLE, IN_FLIGHT, REPORTED, NEEDS_ATTENTION)
```

according to existing lifecycle.

Woo:

```text
provider = WOOCOMMERCE
shopifyReportState = NOT_APPLICABLE
```

is Background-owned and must not be selected/mutated by Shopify merchant code.

Do not add Woo handling to Shopify App Event publisher/provider code.

### R21 — Shopify merchant routes remain provider-specific

Existing Shopify routes/actions continue to pass:

```text
shopifyShopId
Shopify user/session context
Shopify Partner development context
Shopify provider state
```

to the Shopify services exactly as required today.

Do not add:

```text
billingProvider
platform
Woo contract ID
```

inputs to Shopify merchant forms/actions.

### R22 — No merchant-visible UX redesign

Current Shopify:

```text
BillingPurchaseHub
TopUpPurchasePanel
SubscriptionChangePanel
RecoveryCreditPurchaseManager
hosted pricing route/callback
```

remain product-compatible.

Only source changes required by provider-aware persistence/nullability/provider isolation are permitted.

Do not redesign copy/layout/navigation in this task.

## Work Items

- [ ] Update nested database gitlink to accepted ARCH-027-DATABASE-001 and regenerate Prisma.
- [ ] Fix provider-aware Prisma nullability compile errors without weakening Shopify invariants.
- [ ] Explicitly write `RecoveryCreditPurchase.provider=SHOPIFY`.
- [ ] Explicitly write Shopify top-up `UsageEvent.provider=SHOPIFY`.
- [ ] Scope Shopify purchase-history/billing-summary purchase reads to `provider=SHOPIFY`.
- [ ] Add fail-closed narrowing for nullable Shopify purchase evidence.
- [ ] Keep Shopify purchase-history output plan/event handles non-null.
- [ ] Scope refund request/reactivation/live-refund race reads to Shopify provider.
- [ ] Explicitly write `RecoveryCreditRefund.provider=SHOPIFY`.
- [ ] Preserve current Shopify provider-context refund eligibility.
- [ ] Preserve Shopify Partner development zero-value semantics.
- [ ] Ensure Shopify included-counter creation leaves `currentAllowanceQuantity=NULL`.
- [ ] Fail closed if a Shopify current included counter unexpectedly has non-null current allowance.
- [ ] Preserve BillingPlanResolutionService Shopify validation/public contract.
- [ ] Add pre-existing externally-materialised BillingPlan reuse regression.
- [ ] Preserve Shopify subscription/reconciliation/App Event behavior.
- [ ] Add focused database/provider-isolation/regression tests.

## Interfaces / Contracts

### Provider discriminator

Database owner:

`ARCH-027-DATABASE-001`

Shopify application writes/reads:

```text
RecoveryCreditPurchase.provider = SHOPIFY
RecoveryCreditRefund.provider   = SHOPIFY
UsageEvent.provider             = SHOPIFY
```

### Shopify purchase evidence

Despite physical nullability, valid Shopify rows retain:

```text
billingPeriodId
shopifyPlanHandleSnapshot
shopifyEventHandleSnapshot
providerSubscriptionIdSnapshot
usageEventId
```

as non-null provider evidence.

### Shopify current allowance

Valid ARCH-027 Shopify periods:

```text
currentAllowanceQuantity = NULL
```

Existing `grantedQuantity` behavior remains authoritative for Shopify.

### Operational plan identity

Existing bridge remains:

```text
MerchantPricingPlan.shopifyPlanHandle
    -> BillingPlan.shopifyPlanHandle
```

No second Shopify/Woo BillingPlan is introduced.

## Dependencies

- `ARCH-026-SHOPIFY-002`
- `ARCH-027-DATABASE-001`

ARCH-026-SHOPIFY-002 is the previous accepted same-repository Shopify architecture task and prevents implementation against an older `moda-interact` baseline.

ARCH-027-DATABASE-001 supplies the provider-aware Prisma contract that this task must consume.

This task intentionally does not depend on Woo API/UI/Gateway implementation; its purpose is to preserve the existing Shopify edge under the shared schema delta.

## Enables

None yet.

The terminal ARCH-027 integrated validation task should depend on this task so Shopify regression is proven together with the completed Woo path.

## Acceptance Criteria

- [ ] `moda-interact` consumes the accepted ARCH-027 database gitlink without local schema edits.
- [ ] Shopify purchase creation explicitly writes provider SHOPIFY.
- [ ] Shopify top-up UsageEvent explicitly writes provider SHOPIFY and remains PENDING/reportable.
- [ ] Every Shopify purchase-history/top-up read is provider=SHOPIFY scoped.
- [ ] Woo purchase rows cannot appear in Shopify merchant purchase history or latest/pending top-up summary.
- [ ] Nullable database Shopify evidence is narrowed/validated before use; no placeholder historical evidence is fabricated.
- [ ] Shopify merchant purchase-history output remains non-null for planHandle/eventHandle.
- [ ] Shopify refund request only operates on SHOPIFY purchase rows.
- [ ] Shopify refund creation explicitly writes provider SHOPIFY and all required Shopify provenance snapshots remain non-null.
- [ ] Shopify refund reactivation only operates on SHOPIFY purchase/refund rows.
- [ ] P2002/idempotency/live-refund recovery cannot return/mutate a Woo refund row.
- [ ] Current Shopify provider-context refund rule is unchanged.
- [ ] Shopify Partner-development zero-value provider purchase behavior is unchanged.
- [ ] New/repair Shopify paid included counters have currentAllowanceQuantity null.
- [ ] Valid null current allowance produces exact existing Shopify capacity behavior.
- [ ] Unexpected non-null current allowance for Shopify fails closed rather than adopting Woo semantics.
- [ ] BillingPlanResolutionService still requires Shopify meter semantics for paid Shopify catalogue plans.
- [ ] A pre-existing operational BillingPlan with the same handle is reused with no duplicate materialisation.
- [ ] Existing Shopify hosted pricing/callback/subscription projection remains unchanged.
- [ ] Shopify App Event reporting behavior remains unchanged.
- [ ] No Woo operations/receipts/provider contracts are read by Shopify merchant code.
- [ ] No merchant-visible Shopify UX redesign is introduced.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect the accepted `moda-interact/package.json` and repository task instructions before selecting exact commands.

The supplied source baseline declares:

```text
npm test
npm run typecheck
npm run lint
npm run build
npm run prisma:validate
npm run prisma:generate
```

Use the actual accepted repository state rather than assuming scripts remain identical.

Required validation categories:

- [ ] Prisma generate/validate against accepted ARCH-027 database gitlink;
- [ ] project typecheck;
- [ ] targeted changed-file lint;
- [ ] production build;
- [ ] `billing-plan-resolution.service` focused suite;
- [ ] existing-plan/external-materialisation reuse test;
- [ ] unique materialisation race regression test;
- [ ] `recovery-credit-purchase-request.service` focused suite;
- [ ] explicit Shopify purchase/UsageEvent provider assertion;
- [ ] Shopify purchase rejects/fails closed if required generated nullable evidence cannot be established;
- [ ] `recovery-credit-purchase-management.service` focused suite;
- [ ] provider=SHOPIFY history filter test with synthetic Woo row excluded;
- [ ] provider=SHOPIFY refund request exclusion test for synthetic Woo purchase;
- [ ] provider=SHOPIFY reactivation exclusion test for synthetic Woo refund;
- [ ] Shopify refund created with non-null billingPeriod/provider/plan/event snapshots;
- [ ] Shopify Partner development zero-value refund regression;
- [ ] refund P2002/requestKey/live-refund provider-isolation concurrency test;
- [ ] `merchant-billing-read.service` synthetic Woo pending/latest purchase exclusion tests;
- [ ] `merchant-recovery-capacity-read.service` currentAllowance null regression test;
- [ ] unexpected Shopify non-null currentAllowance fail-closed tests in both merchant billing/capacity reads where applicable;
- [ ] `billing-period-projection` new/repaired Shopify counter currentAllowance null tests;
- [ ] `subscription-activation.service` Shopify counter currentAllowance null regression;
- [ ] hosted plan-change/subscription-read/reconciliation focused suites;
- [ ] Shopify billing callback route focused tests;
- [ ] billing purchase hub / top-up / subscription-change / purchase-manager UI regression tests;
- [ ] full repository test suite, with unrelated existing failures documented if any;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization, nested database gitlink and pushed task-branch evidence.

No Woo provider/network/sandbox call is required for this Shopify compatibility task.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin system/sandbox validation.

## Implementation Notes

Keep this task intentionally conservative.

Preferred shape:

```text
ARCH-027 makes generic persistence fields provider-aware
        |
        v
Shopify explicitly scopes itself to SHOPIFY
        |
        v
existing Shopify business/provider behavior unchanged
```

Do not turn the mature Shopify application into a generic provider host.

The Woo application/API/Background own Woo provider mechanics.

`moda-interact` should simply remain a correct Shopify edge over the now provider-aware shared database schema.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- ARCH-027-DATABASE-001 preserves existing Shopify database evidence constraints conditionally under `provider=SHOPIFY`.
- BACKGROUND-001 does not set `currentAllowanceQuantity` for Shopify periods.
- API-side Woo operational BillingPlan materialisation uses the same catalogue projection semantics/unique handle so Shopify can safely reuse an existing operational row.
- Shopify billing remains the reference existing product behavior; ARCH-027 does not intentionally change it.

### Unresolved Issues

None within the Shopify application compatibility boundary.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
