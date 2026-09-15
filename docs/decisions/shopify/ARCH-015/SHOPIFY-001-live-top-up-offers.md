---
id: ARCH-015-SHOPIFY-001
architecture_id: ARCH-015
title: Resolve live recovery-credit top-up offers from Shopify and ARCH-014
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-014-SHOPIFY-001
enables:
- ARCH-015-SHOPIFY-002
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-015-SHOPIFY-001

## Objective

Replace the singular operational BillingPlan top-up read model with a live multi-offer resolver that correlates the merchant's current Shopify App Pricing subscription with ARCH-014 `MerchantPricingPlan`/`MerchantPricingUsageEvent` entitlement semantics.

This task is read/UI only. Do not create purchases.

## Authorized implementation surface

```text
app/services/billing/providers/shopify-billing.provider.ts
app/services/billing/billing.types.ts
app/services/billing/billing.service.ts                 # read/commercial projection only
app/services/merchant-pricing/*                         # reuse/extend ARCH-014 server-only capability
app/routes/app/billing/options/route.tsx
app/components/dashboard/TopUpPurchasePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx         # only if prop shape requires
app/i18n/locales/*.json                                 # generic empty/verification labels only
tests/unit/services/billing*.test.*
tests/unit/billing-ui.test.ts
tests/unit/billing-purchase-hub.test.tsx
tests/unit/*topup*.test.*
```

Do not modify purchase mutation semantics in this task.

## Provider parser correction

In `ShopifyBillingProvider`, do not exclude a returned live subscription item solely because `item.price.active === false`.

Keep type/handle validation, but subscription membership comes from `activeSubscription.items`.

Apply the same principle to parsing helpers in this repository.

## Canonical offer resolver

Create/reuse a server-only function equivalent to:

```text
resolveCurrentRecoveryCreditOffers({
  providerSubscription,
  merchantPricingPlan
})
```

Resolution sequence:

1. require live provider subscription;
2. use provider `planHandle`;
3. load exactly one `MerchantPricingPlan` where `shopifyPlanHandle == provider.planHandle`;
4. DO NOT require `MerchantPricingPlan.isActive == true` for an already-contracted merchant;
5. load usage events ordered `position ASC`;
6. for each ARCH-014 usage event, find exact provider usage item where `handle == eventHandle`;
7. only matched events become offers;
8. `creditsGranted` comes from `creditsGrantedPerUnit`;
9. provider price/usage/currency comes from provider usage item, not ARCH-014 monetary fields;
10. unknown provider meters are ignored for purchasing but recorded in bounded diagnostics;
11. ARCH-014 events absent from provider subscription are not purchasable.

Never globally resolve `eventHandle` without the current provider `planHandle`.

## Offer DTO

Return equivalent objects:

```text
{
  eventHandle,
  cataloguePosition,
  creditsGranted,
  providerPrice,
  providerUsage
}
```

Do not expose `adminLabel`.

## Empty-state behavior

Always render the top-up section.

When offer list is empty because no valid intersection exists, render exactly the merchant meaning:

```text
No top ups are currently available for this subscription.
```

Use a translated generic key across all supported locales.

Do not hide the panel.

Provider/API verification failure is separate:

```text
We couldn't verify top-up availability right now. Please try again later.
```

Purchasing remains unavailable in that state.

## Legacy singular fields

This task must stop using these as the operative top-up source:

```text
BillingPlan.recoveryCreditsPerPack
BillingPlan.shopifyRecoveryCreditPackEventHandle
```

Do not delete schema fields in this task; simply remove them from this top-up read/UI flow.

## Required tests

- current Shopify plan resolves matching ARCH-014 plan;
- `isActive=false` catalogue plan can still resolve for an existing live Shopify contract;
- multiple ARCH-014 usage events resolve in `position` order;
- provider meter absent => ARCH-014 event omitted;
- provider-only unknown meter => no fabricated credits;
- same event handle on another plan is never used;
- credits come from `creditsGrantedPerUnit`;
- provider price comes from live provider item;
- `price.active=false` item remains eligible if returned in live subscription;
- zero ARCH-014 events -> empty-state panel shown;
- zero provider matches -> empty-state panel shown;
- provider failure -> verification-unavailable state, not empty-state;
- singular BillingPlan pack fields are not read for offers.

## Stop conditions

STOP if:

- ARCH-014 merchant app implementation is not available/compatible;
- ARCH-014 usage-event rows cannot be distinguished as the intended recovery-credit top-up offers under the accepted ARCH-014 contract;
- resolving an existing subscription requires `MerchantPricingPlan.isActive=true`;
- implementation requires reading ARCH-014 stored price as proof of Shopify's live charge.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

Status: Ready for Review

Implementation summary:

- Added the server-only ARCH-014 to Shopify live subscription intersection resolver, scoped by the current Shopify `planHandle`, ordered by usage-event position, bounded unknown-meter diagnostics, and live provider price/usage data.
- Preserved contracted access to inactive ARCH-014 catalogue plans and retained Shopify subscription items whose returned price has `active: false`.
- Updated the billing read projection and route/UI state to distinguish verified empty offers from verification-unavailable states, always render the top-up panel, and derive configuration from live offers rather than singular `BillingPlan` pack fields.
- Preserved purchase mutation semantics and Shopify-hosted subscription management.

Changed files:

- `app/components/dashboard/BillingPurchaseHub.jsx`
- `app/components/dashboard/TopUpPurchasePanel.jsx`
- `app/i18n/locales/en.json`
- `app/routes/app/billing/options/route.tsx`
- `app/services/billing/billing.service.ts`
- `app/services/billing/billing.types.ts`
- `app/services/billing/providers/shopify-billing.provider.ts`
- `app/services/merchant-pricing/merchant-pricing.server.js`
- `tests/unit/billing-purchase-hub.test.tsx`
- `tests/unit/merchant-pricing-reader.test.js`
- `tests/unit/services/shopify-billing.provider.test.ts`

Validation:

- Focused provider, resolver, and UI suite: 3 files passed, 40 tests passed.
- Expanded focused suite: 4 files passed; two existing exact-active-cycle billing service tests still fail because their fixtures provide only retired singular `BillingPlan` pack metadata and no ARCH-014 `MerchantPricingPlan`.
- `npm run prisma:generate`: passed.
- Focused ESLint for the final corrected service and panel files: passed, with the repository TypeScript-version compatibility warning.
- `npm run typecheck`: repository baseline remains failing in unrelated dashboard/Polaris JavaScript files; no remaining diagnostics were reported for the touched billing service, provider, resolver, route, or top-up panel files.
- Both generic top-up empty/verification keys are present in all 20 supported locale files; English text matches the task contract exactly.
- `git diff --check`: passed.

Baseline limitations:

- The two existing exact-active-cycle billing service tests still encode the retired singular `BillingPlan` top-up contract and fail until their fixtures are migrated to ARCH-014 usage events. No legacy fallback was added because that would violate this task's source-of-truth requirement.
- Full repository typecheck/lint remains affected by pre-existing unrelated diagnostics; the touched-slice checks above are clean.

Launcher and isolation evidence:

- Continued the prepared attempt in `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-SHOPIFY-001` and parent report worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-SHOPIFY-001`.
- Preserved parent claim commit `68b0ccd8e6e776790920056a12836cbb21ec8638` and did not rerun the launcher or create another claim.
- Implementation worktree contained only the 11 authorized ARCH-015 files; the database submodule was not changed.

Commits:

- Implementation: `374f16f` (`feat(billing): resolve live recovery credit top-up offers`)
- Parent report: pending publication on the mirrored `task/ARCH-015-SHOPIFY-001` branch.

## Architect Review — Attempt 1 (revised after ARCH-014 extension)

### Status

**Changes Requested — preserve the extended ARCH-014 reader and remove the unsafe interim purchase action**

Implementation commit `374f16f` is accepted for the core live-offer resolution behavior. The resolver correctly scopes by the current Shopify plan handle, intersects live provider usage items with ARCH-014 usage events, retains returned provider items whose price is inactive, separates verified-empty from verification-unavailable states, and removes the retired singular BillingPlan fields from the operative offer-read path.

Two corrections are required before architect acceptance:

1. the multi-offer cards must remain display-only until `ARCH-015-SHOPIFY-002` owns selected-`eventHandle` purchase admission; and
2. Attempt 2 must integrate on top of the latest accepted ARCH-014 merchant-pricing reader, preserving its highlight/exact-locale behavior rather than restoring the older pre-extension reader from `374f16f`.

The two stale billing-service tests that still use singular BillingPlan top-up fixtures may be migrated to the ARCH-014 fixture contract. Do not restore a production fallback to retired singular fields.

The deterministic Attempt-2 contract follows.

# ARCH-015-SHOPIFY-001 — Attempt 2 correction contract

## Title

Reconcile live recovery-credit offer presentation with the extended ARCH-014 merchant-pricing reader and remove unsafe interim purchase actions

## Workflow identity

This is **not a new task ID**. It is the deterministic correction contract for the existing task:

```text
ARCH-015-SHOPIFY-001
```

Before reclaim, preserve:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

The launcher must increment the same task to **Attempt 2** exactly once.

Do not create `ARCH-015-SHOPIFY-004` or another correction task for this work.

## Additional prerequisite gate introduced by the ARCH-014 extension

The original task depends on `ARCH-014-SHOPIFY-001`. The latest architecture extends the same merchant-pricing reader through `ARCH-014-SHOPIFY-002`.

For Attempt 2, do not edit `app/services/merchant-pricing/merchant-pricing.server.js` until the accepted/integrated implementation of:

```text
ARCH-014-SHOPIFY-002
```

is present in the `moda-interact` baseline used by this task.

The authoritative baseline is the latest canonical implementation containing all accepted ARCH-014 merchant-pricing reader behavior. Do not use the older `374f16f` copy of `merchant-pricing.server.js` as the merge base if it would remove newer ARCH-014 behavior.

STOP and return to `moda_architect` if `ARCH-014-SHOPIFY-002` is not yet accepted/integrated or if its accepted reader contract cannot be identified unambiguously.

## Objective

Preserve all accepted Attempt-1 live recovery-credit offer resolution behavior while correcting two integration/safety issues:

1. preserve the extended ARCH-014 merchant-pricing catalogue reader without regression; and
2. prevent the new multi-offer UI from invoking the legacy singular recovery-pack purchase mutation before `ARCH-015-SHOPIFY-002` implements selected-`eventHandle` purchase admission.

This task remains **read/UI only**.

Do not implement purchase admission in this task.

## Accepted Attempt-1 behavior — preserve exactly

Keep all of the following behavior from implementation commit `374f16f` unless a mechanical merge is required:

```text
current Shopify active/trialing subscription is provider authority
current provider planHandle scopes the ARCH-014 plan lookup
MerchantPricingPlan.isActive is NOT required for an already-contracted merchant
usage events are resolved in position ASC order
provider item handle must exactly equal ARCH-014 eventHandle
only intersecting provider meters + ARCH-014 usage events become offers
creditsGranted comes from MerchantPricingUsageEvent.creditsGrantedPerUnit
provider price/currency/usage comes from the live Shopify provider item
provider item price.active=false does not invalidate returned live subscription membership
provider-only unknown meters do not create offers and produce bounded diagnostics
ARCH-014 events missing from the live subscription are not offers
zero valid intersections is a verified empty state
provider/API verification failure is a distinct verification-unavailable state
BillingPlan.recoveryCreditsPerPack is not an operative offer source
BillingPlan.shopifyRecoveryCreditPackEventHandle is not an operative offer source
```

Preserve the exact merchant empty-state meaning:

```text
No top ups are currently available for this subscription.
```

Preserve the verification-failure meaning:

```text
We couldn't verify top-up availability right now. Please try again later.
```

## ARCH-014 extension integration contract

The latest accepted ARCH-014 reader remains authoritative for general merchant-pricing catalogue presentation.

### `readActiveMerchantPricingCatalogue(...)`

Preserve the complete accepted ARCH-014 behavior, including at minimum:

```text
active catalogue plan filtering
cataloguePosition ordering
exact requested/canonical locale selection
exact-locale plan description validation
ordered usageEvents
ordered MerchantPricingPlan.highlights
exact-locale highlight translations
highlight contentKey / position / title / description merchant DTO
missing or duplicate required exact-locale content fails closed
no English fallback where ARCH-014 forbids it
no adminLabel leakage
no highlight database-id leakage
```

Do not remove, simplify or rewrite this function merely to implement ARCH-015 provider lookup.

### `readMerchantPricingPlanForProvider(...)`

Preserve/add the ARCH-015 provider-specific reader as a separate server-side capability.

Required behavior:

```text
input: current live provider planHandle
trim/non-empty validate planHandle
lookup exactly by MerchantPricingPlan.shopifyPlanHandle
DO NOT filter by MerchantPricingPlan.isActive
return null when no exact plan exists
load usageEvents in position ASC order
load the usage-event fields required by recovery-credit offer resolution
```

This provider-specific reader does **not** need plan highlights. Do not make top-up offer resolution depend on highlight translations or merchant presentation copy.

Do not mutate `readActiveMerchantPricingCatalogue(...)` into the provider lookup.

### `resolveCurrentRecoveryCreditOffers(...)`

Preserve the Attempt-1 resolver contract:

```text
require live ACTIVE/TRIALING provider subscription
require merchantPricingPlan.shopifyPlanHandle === providerSubscription.planHandle
exactly match usage event eventHandle to returned provider usage item handle
sort ARCH-014 usage events by position
creditsGranted <- creditsGrantedPerUnit
providerPrice <- provider item price
providerUsage <- provider item usage
retain returned provider items even when providerItem.price.active === false
unknown provider meters -> bounded diagnostic only
unmatched ARCH-014 event -> omitted offer
```

Return offer DTOs equivalent to:

```text
{
  eventHandle,
  cataloguePosition,
  creditsGranted,
  providerPrice,
  providerUsage
}
```

Do not include ARCH-014 highlight data in this DTO.

## Functional correction — offer cards must not invoke the legacy purchase path

Attempt 1 renders one card per resolved offer but gives every card the same purchase callback. The current legacy route/action does not submit the selected offer `eventHandle`, so the UI cannot prove which displayed offer the merchant chose.

`ARCH-015-SHOPIFY-002` owns the later request contract:

```text
intent = BUY_RECOVERY_CREDIT_PACK
purchaseId = valid UUID
eventHandle = selected offer handle
```

Do **not** implement that request contract here.

For this Attempt 2, make resolved offer cards **display-only**.

Required UI behavior:

```text
resolved offers remain visible
credits remain visible
live provider price remains visible when renderable
catalogue order remains visible
verified empty state remains visible
verification-unavailable state remains visible
NO enabled purchase action is rendered for an offer
NO offer click invokes fetcher.submit
NO eventHandle is submitted by this task
```

Preferred implementation:

- do not render the Buy button in `TopUpPurchasePanel` for ARCH-015-SHOPIFY-001;
- remove the now-unused purchase callback prop from the top-up panel/hub path if it can be done without widening scope;
- if the route retains its existing action for compatibility, do not modify its mutation semantics in this task and do not create a new UI path to it.

Do not add a temporary fallback purchase implementation.

Do not infer a default offer.

Do not automatically choose the first offer.

Do not map Bronze/Silver/Gold by array index.

Do not use `cataloguePosition` as purchase identity.

## Authorized correction surface

Primary files:

```text
app/services/merchant-pricing/merchant-pricing.server.js
app/components/dashboard/TopUpPurchasePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx          # only if callback prop cleanup requires
app/routes/app/billing/options/route.tsx                # only if callback wiring cleanup requires
app/services/billing/billing.service.ts                 # read projection only; no purchase mutation changes
app/services/billing/billing.types.ts                   # only if read DTO shape requires
app/services/billing/providers/shopify-billing.provider.ts  # preserve Attempt-1 parser correction only
```

Tests:

```text
tests/unit/merchant-pricing-reader.test.js
tests/unit/billing-purchase-hub.test.tsx
tests/unit/billing-ui.test.ts                           # if present in the accepted baseline
tests/unit/services/shopify-billing.provider.test.ts
tests/unit/services/billing.service.test.ts             # fixture correction only where required
other existing focused top-up tests directly affected by the change
```

Do not edit database schema/migrations.

Do not edit Shared.

Do not edit Background.

Do not edit Admin.

## Legacy tests

The two previously reported billing-service tests use retired singular `BillingPlan` top-up fixtures.

Do not restore singular production fallback behavior to make those tests pass.

If those tests are in the accepted Attempt-2 baseline and are within the authorized test surface, migrate only their fixtures/assertions so they provide the required ARCH-014 `MerchantPricingPlan` + usage-event evidence expected by the new read model.

Do not change their unrelated billing-cycle assertions.

The goal is:

```text
production contract remains ARCH-014 + live Shopify
stale tests are updated to the production contract
no legacy fallback is reintroduced
```

## Required tests

### Preserve ARCH-015 offer resolution

Prove:

```text
current Shopify plan resolves exact ARCH-014 plan
isActive=false ARCH-014 plan resolves for an existing live provider contract
multiple ARCH-014 usage events resolve in position order
provider meter missing -> event omitted
provider-only meter -> no fabricated credits
same eventHandle on another plan is not used
creditsGranted comes from creditsGrantedPerUnit
price/currency come from live provider item
returned provider price.active=false item remains eligible
zero intersections -> verified empty state
provider failure -> verification-unavailable state
singular BillingPlan pack fields are not read for offers
```

### Preserve extended ARCH-014 reader

Run/add regression assertions proving `readActiveMerchantPricingCatalogue(...)` still:

```text
returns ordered highlights
uses exact locale highlight translations
preserves contentKey/position/title/description
fails closed when required exact-locale plan/highlight content is absent or duplicated
preserves usageEvents alongside highlights
```

Do not weaken the accepted ARCH-014 tests.

### Purchase-action safety gate

Add focused UI evidence proving:

```text
one resolved offer -> offer renders, no enabled Buy action
multiple resolved offers -> all render in order, none exposes an enabled Buy action
verification-unavailable -> no Buy action
verified empty -> no Buy action
rendering an offer does not invoke or require onPurchaseTopUp
```

If source-level route tests exist, prove the top-up card path does not submit a selected offer in SHOPIFY-001.

Do not add SHOPIFY-002 purchase-admission tests here.

## Validation

From `moda-interact`:

```bash
npm run prisma:generate

npx vitest run \
  tests/unit/merchant-pricing-reader.test.js \
  tests/unit/billing-purchase-hub.test.tsx \
  tests/unit/services/shopify-billing.provider.test.ts
```

Also run every directly affected existing top-up/billing UI test discovered in the repository.

If `tests/unit/billing-ui.test.ts` exists in the accepted baseline, include it.

If the two legacy billing-service fixtures are migrated, run the exact affected tests in:

```text
tests/unit/services/billing.service.test.ts
```

Then run:

```bash
npm run typecheck
npm run build
git diff --check
```

For repository-wide baseline failures unrelated to touched files, record exact unchanged diagnostics in the Completion Report. Do not modify unrelated code merely to make a global command green.

## Exact searches before completion

Search the operative offer-read path and confirm there is no use of:

```text
recoveryCreditsPerPack
shopifyRecoveryCreditPackEventHandle
```

as recovery-credit offer authority.

Search the resolved-offer UI path and confirm there is no enabled purchase action wired to an offer before SHOPIFY-002.

Search `merchant-pricing.server.js` and confirm the accepted ARCH-014 highlight reader symbols/fields remain present after the merge.

## Non-goals

Do not implement any of the following in this task:

```text
selected eventHandle purchase submission
strict purchase FormData schema
purchase UUID changes
purchase single-flight
new RecoveryCreditPurchase rows
new UsageEvent creation
provider-before evidence capture
provider-context identity write
refund eligibility
refund holds
Background App Event submission
new queueing
new Prisma models/columns
ARCH-014 Admin editing
highlight use in top-up offer economics
legacy singular BillingPlan fallback
```

These remain owned by later tasks, especially `ARCH-015-SHOPIFY-002`.

## Stop conditions

STOP and return to `moda_architect` without inventing behavior if:

- accepted/integrated `ARCH-014-SHOPIFY-002` is not available;
- merging ARCH-015 provider lookup would require removing or weakening accepted ARCH-014 highlight/exact-locale behavior;
- the latest ARCH-014 reader changed the meaning/schema of `MerchantPricingUsageEvent` so the accepted ARCH-015 resolver contract is no longer valid;
- making the offer UI safe would require implementing selected-offer purchase admission early;
- a new database/schema change appears necessary;
- another task has concurrently modified the same reader in a way that makes the authoritative baseline ambiguous.

## Completion Report requirements

Return the same task to `review` with `attempt: 2` and claim cleared.

Record:

```text
latest accepted ARCH-014 baseline/commit integrated
Attempt-2 implementation commit
files changed
proof that ARCH-014 highlight/exact-locale reader behavior was preserved
proof that ARCH-015 offer resolver behavior was preserved
proof that offer cards are display-only until SHOPIFY-002
legacy singular-field search results
focused test counts
legacy fixture migrations, if any
prisma generation result
typecheck/build result or exact unchanged baseline blockers
git diff --check
implementation and parent worktrees clean
```

Do not mark `ARCH-015-SHOPIFY-002` Ready yourself. Return to `moda_architect`; dependency promotion belongs to architect acceptance.
