---
id: ARCH-010-SHOPIFY-004
architecture_id: ARCH-010
title: Present current paid-period entitlement to merchants
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 45
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-010-SHOPIFY-003
- ARCH-010-DATABASE-013
enables:
- ARCH-010-SHOPIFY-007
- ARCH-010-SHOPIFY-009
created: 2026-09-11
updated: 2026-09-14
---

# ARCH-010-SHOPIFY-004: Present current paid-period entitlement to merchants

## Objective

Align merchant-facing paid billing screens with the new period-scoped included-credit state. A merchant who has successfully completed first paid activation must see the exact current Shopify period and Moda's current-period included capacity, while lifetime balances remain separate.

This is merchant UI only. Never expose or route merchants to `moda-interact-admin`.

## Inspect before editing

```text
app/routes/app/billing/route.tsx
app/routes/app/usage/route.jsx
app/routes/app/home/route.jsx
app/components/dashboard/UsageOverview.*
app/components/dashboard/UsageEvents.*
app/i18n/locales/*.json
app/services/billing/billing.service.ts
tests/unit/billing-ui.test.ts
package.json
```

Reuse existing merchant i18n conventions. Do not hard-code English-only merchant strings.

## Billing service read model

For a safe mapped paid subscription, expose from durable current-period state:

```text
current BillingPeriod id/start/end/status
included grantedQuantity
included committedQuantity
included reservedQuantity
included forfeitedQuantity
included remaining = max(granted - committed - reserved - forfeited, 0)
purchased lifetime granted/committed/reserved/refunding/available
shop-lifetime Free granted/committed/reserved/remaining
```

Do not use shop-wide paid UsageEvent aggregate as the authoritative "included remaining" calculation.

If the paid subscription is ACTIVE but period/counter state is missing/inconsistent, surface the existing safe `configuration unavailable` merchant state rather than displaying invented zero/full allowance.

## Merchant `/app/billing`

For paid plan, show at minimum:

```text
Current plan: <mapped plan name>
Status: ACTIVE
Current period: <Shopify start> - <Shopify end>
Included recoveries: <remaining> of <granted> remaining
Purchased recovery credits: <available> ...
Lifetime Free recoveries: <remaining> of <granted> remaining
```

It is acceptable to show committed/reserved details separately if the existing UI style supports them, but do not confuse reserved with already-consumed usage.

Keep the Shopify-hosted plan-change link.

Keep top-up purchase CTA only when the existing ARCH-008 eligibility checks pass:

```text
current plan active
exact local/provider billing cycle matches
pack meter verified
plan pack configuration enabled
```

Do not make the purchase button appear merely because a paid period counter exists.

## `/app` and `/app/usage`

After successful paid onboarding, normal merchant dashboard/detail/usage routes remain available.

Usage period selection must continue to use durable BillingPeriod ids/boundaries. Where current-period summary displays included capacity, use the period counter. Historical usage events remain event history; do not rewrite them into the new counter.

Do not expose current/past data from another tenant.

## Feature availability

UI navigation/actions may be hidden/disabled according to existing `BillingPlanFeature` mappings, but do not add plan-name conditionals such as `if plan === Growth`.

`moda-interact-admin` remains internal only and must not appear in merchant navigation, buttons, redirects or support links.

## Required tests

Prove at least:

1. paid billing screen reads current period counter;
2. remaining calculation accounts for committed + reserved + forfeited;
3. paid screen does not use shop-wide usage aggregate as included remaining;
4. current period dates render from durable Shopify-derived period;
5. purchased credits render separately;
5a. remaining lifetime Free credits render separately while Paid and are not hidden/reset;
6. missing paid period shows safe configuration-unavailable state;
7. missing paid period counter shows safe configuration-unavailable state;
8. top-up CTA still requires exact ARCH-008 purchase eligibility;
9. plan-change link still points to Shopify-hosted selection flow;
10. merchant routes contain no Admin links/redirects;
11. Free billing UI remains correct;
12. merchant-facing new strings use i18n keys across the repository's supported locale contract.

## Validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test -- tests/unit/billing-ui.test.ts
npm run typecheck
npm run build
git diff --check
```

Run the full declared `npm test` if focused validation passes and repository baseline permits it; report known unrelated baseline failures by baseline ID rather than rediscovering them.

## Non-goals

Do not change Background admission, create periods, implement plan changes, cancellation, refund behaviour, Admin UI, or pricing amounts.

## Stop conditions

STOP if the integrated paid period counter/read model differs materially from ARCH-010-DATABASE-002 or if merchant UI would need to query Shopify directly on every screen render.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `app/services/billing/billing.service.ts`
- `app/routes/app/billing/route.tsx`
- `app/i18n/locales/*.json` (all 20 supported merchant locales)
- `tests/unit/billing-ui.test.ts`
- `tests/unit/billing-i18n.test.ts`
- `tests/unit/services/billing.service.test.ts`

### Work Completed
- Updated `getMerchantBillingState` to read the durable current `BillingPeriod` included-credit counter.
- Paid included remaining is calculated as `max(granted - committed - reserved - forfeited, 0)` and is not derived from the shop-wide usage aggregate.
- Added paid-period/counter consistency validation and fail-closed configuration-unavailable projection.
- Kept lifetime Free capacity and purchased credits as separate merchant-facing balances.
- Preserved Shopify-hosted plan selection/change flow and existing exact top-up eligibility gate.
- Added merchant i18n keys for paid-period and lifetime Free presentation across every supported locale.
- Added focused UI, service, and locale contract coverage for the acceptance matrix.

### Validation Results
- `npm run prisma:validate` — passed.
- `npm run prisma:generate` — passed.
- `npm run test -- tests/unit/billing-ui.test.ts tests/unit/billing-i18n.test.ts` — passed, 15 tests.
- Focused final billing validation (`billing.service.test.ts`, `billing-ui.test.ts`, `billing-i18n.test.ts`) — passed, 111 tests.
- `npm test` — passed, 38 test files; 381 passed, 3 skipped.
- `npm run build` — passed.
- `git diff --check` — passed.
- `npm run typecheck` — non-zero under documented `TYPECHECK-001` repository baseline; no new TypeScript errors were reported in the changed billing service or route.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-004`.
- Implementation branch: `task/ARCH-010-SHOPIFY-004`.
- Implementation commit: `03ba8f5c7d0bfe0c051f09e1ddd6639ee3c1c356` (pushed to `origin/task/ARCH-010-SHOPIFY-004`).
- Implementation worktree was clean after commit; the prepared packet's physical worktree and dependency-gate evidence were retained.
- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-004`.
- Parent branch: `task/ARCH-010-SHOPIFY-004`.
- Parent claim commit: `2edf9d7bd57f7c7755d987ab42be660e26fa42d3`.
- Parent submodule pointer was not staged or changed; implementation publication remains on its task branch for architect review.

### Architect Review
Pending.

## Architect Review — Attempt 1

### Status

**Changes Requested**

Attempt 1 correctly moves Paid included-capacity presentation onto the durable current
`BillingPeriodEntitlementCounter`, keeps lifetime Free and purchased balances separate,
preserves the Shopify-hosted plan-change flow, and keeps the existing top-up purchase
eligibility gate.

Two production correctness gaps remain, plus two narrower permanent-evidence gaps.

Do not redesign billing or move work into SHOPIFY-009. The corrections below are the
complete Attempt-2 contract.

### Accepted Attempt-1 work to preserve

Preserve:

- Paid included remaining is not calculated from shop-wide `UsageEvent` totals.
- Included remaining uses:

```text
granted - committed - reserved - forfeited
```

- lifetime Free remains a separate balance under Paid;
- purchased credits remain a separate merchant-facing balance;
- the Shopify-hosted plan-change link remains `/app/billing/select`;
- existing ARCH-008 pack-purchase verification remains authoritative;
- merchant navigation contains no `moda-interact-admin` link/redirect;
- Free billing presentation remains supported;
- new billing copy remains in the merchant i18n catalogue contract.

### Finding 1 — purchased available balance ignores `refundingQuantity`

The task's required read model explicitly says:

```text
purchased lifetime granted/committed/reserved/refunding/available
```

and the canonical ARCH-010 accounting model defines aggregate purchased spendability
as:

```text
available =
  max(
    grantedQuantity
      - committedQuantity
      - reservedQuantity
      - refundingQuantity,
    0
  )
```

`ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS).refundingQuantity` is the
hot-path hold for unreserved credits belonging to `WITHDRAWN` purchases. Those credits
must not be shown as spendable.

Attempt 1 currently returns:

```ts
available: Math.max(
  grantedQuantity - committedQuantity - reservedQuantity,
  0,
)
```

and omits `refundingQuantity` from both the service projection and merchant copy.

This can overstate merchant-available purchased credits during an in-progress refund.

#### Required correction

In:

```text
app/services/billing/billing.service.ts
```

return:

```ts
purchasedRecoveryCredits: {
  grantedQuantity: purchasedCounter?.grantedQuantity ?? 0,
  committedQuantity: purchasedCounter?.committedQuantity ?? 0,
  reservedQuantity: purchasedCounter?.reservedQuantity ?? 0,
  refundingQuantity: purchasedCounter?.refundingQuantity ?? 0,
  available: Math.max(
    (purchasedCounter?.grantedQuantity ?? 0)
      - (purchasedCounter?.committedQuantity ?? 0)
      - (purchasedCounter?.reservedQuantity ?? 0)
      - (purchasedCounter?.refundingQuantity ?? 0),
    0,
  ),
},
```

Do not change purchase/refund lifecycle mutations in this task.

In:

```text
app/routes/app/billing/route.tsx
```

pass the new value to merchant i18n:

```ts
i18n.t("billing.purchasedRecoveryCredits", {
  granted: purchasedRecoveryCredits.grantedQuantity,
  committed: purchasedRecoveryCredits.committedQuantity,
  reserved: purchasedRecoveryCredits.reservedQuantity,
  refunding: purchasedRecoveryCredits.refundingQuantity,
  available: purchasedRecoveryCredits.available,
})
```

Update the existing `billing.purchasedRecoveryCredits` translation in **all supported
merchant locale catalogues** so its placeholder contract is exactly:

```text
{granted}
{committed}
{reserved}
{refunding}
{available}
```

For English use exactly:

```text
Purchased recovery credits: {granted} - {committed} - {reserved} - {refunding} held for refund ({available} available)
```

For the other locale catalogues preserve the existing translated sentence and add an
equivalent localized "held for refund/refunding" phrase around `{refunding}`. Do not
leave the English phrase copied into non-English catalogues.

### Finding 2 — the Paid period safety predicate accepts materially inconsistent period state

The task requires:

```text
If the paid subscription is ACTIVE but period/counter state is
missing/inconsistent, surface configuration unavailable.
```

Attempt 1 validates pointer/boundaries/shop/status/counter grant, but does not prove
that the pointed period is owned by the current Subscription/current mapped Paid plan.

A stale/corrupt period can therefore be presented as current if it has matching
boundaries and a matching counter even when its ownership/plan snapshot belongs to a
different plan projection.

#### Required correction

In:

```text
app/services/billing/billing.service.ts
```

strengthen the Paid read-model validity check.

For `paidIncluded` to be non-null, require all of the following:

```text
Subscription.status = ACTIVE

Subscription.plan exists
Subscription.plan.active = true
Subscription.plan.kind = PAID_METERED
Subscription.observedShopifyPlanHandle =
  Subscription.plan.shopifyPlanHandle

Subscription.billingPeriodId is non-null
BillingPeriod.id = Subscription.billingPeriodId
BillingPeriod.shopId = requested shopId
BillingPeriod.subscriptionId = Subscription.id
BillingPeriod.planId = Subscription.plan.id
BillingPeriod.shopifyPlanHandleSnapshot =
  Subscription.plan.shopifyPlanHandle
BillingPeriod.planKindSnapshot = PAID_METERED
BillingPeriod.status = OPEN

BillingPeriod.periodStart = Subscription.currentPeriodStart
BillingPeriod.periodEnd = Subscription.currentPeriodEnd
BillingPeriod.periodStart < BillingPeriod.periodEnd

BillingPeriod.includedRecoveryCreditsGranted is a non-negative safe integer

exact INCLUDED_RECOVERY_CREDITS counter exists
counter.shopId = requested shopId
counter.billingPeriodId = BillingPeriod.id
counter.grantedQuantity =
  BillingPeriod.includedRecoveryCreditsGranted

counter granted/committed/reserved/forfeited are all
non-negative safe integers

committed + reserved + forfeited <= granted
```

If **any** required condition fails:

```text
paidIncluded = null
paidConfigurationUnavailable = true
```

Do not silently clamp an internally impossible counter such as:

```text
committed + reserved + forfeited > granted
```

to an ordinary `remaining = 0` presentation. That is configuration/integrity
unavailable, not genuine exhaustion.

Do not compare the period grant to the **current mutable BillingPlan allowance**.
The period's snapshotted grant is historical/current-period authority.

Do not require `planNameSnapshot` to equal the current plan name; names may be
presentation metadata while the stable plan/handle/kind ownership is the safety
boundary.

### Finding 3 — missing period and missing counter are not proven at the service boundary

The current UI test supplies:

```text
paidIncluded = null
paidConfigurationUnavailable = true
```

as mocked service output.

That proves the component can render the safe state, but it does not prove
`getMerchantBillingState()` actually derives it when durable period state is missing.

#### Required tests

In:

```text
tests/unit/services/billing.service.test.ts
```

create/reuse a canonical valid Paid merchant-state fixture and add a parameterized test
named:

```text
fails merchant Paid presentation closed for inconsistent current period: %s
```

Required rows:

```text
billingPeriod relation missing
billingPeriodId missing
period status CLOSED
period shopId differs
period subscriptionId differs
period planId differs
period Shopify handle snapshot differs
period plan kind snapshot is FREE
period boundary differs from Subscription
periodStart >= periodEnd
includedRecoveryCreditsGranted is null
includedRecoveryCreditsGranted is negative
included counter missing
counter shopId differs
counter billingPeriodId differs
counter granted differs from period grant
counter committed is negative
counter reserved is negative
counter forfeited is negative
committed + reserved + forfeited exceeds granted
current BillingPlan inactive
observed Shopify handle differs from mapped plan handle
```

For every row assert:

```ts
expect(result.paidIncluded).toBeNull();
expect(result.paidConfigurationUnavailable).toBe(true);
```

For at least the two task-mandated rows:

```text
billingPeriod relation missing
included counter missing
```

also assert `usageQuantity` is not substituted as Paid included remaining.

Keep the existing valid Paid test and strengthen its fixture so it includes the exact
ownership/snapshot fields used by the production predicate:

```text
Subscription.id
Subscription.observedShopifyPlanHandle
BillingPlan.id
BillingPlan.shopifyPlanHandle
BillingPlan.active
BillingPeriod.subscriptionId
BillingPeriod.planId
BillingPeriod.shopifyPlanHandleSnapshot
BillingPeriod.planKindSnapshot
```

### Finding 4 — purchased refund hold and exact durable period dates need explicit merchant evidence

#### Service projection test

Add:

```text
subtracts purchased refund holds from merchant available credits
```

Fixture:

```text
grantedQuantity   = 100
committedQuantity = 20
reservedQuantity  = 5
refundingQuantity = 10
```

Assert exactly:

```ts
expect(result.purchasedRecoveryCredits).toEqual({
  grantedQuantity: 100,
  committedQuantity: 20,
  reservedQuantity: 5,
  refundingQuantity: 10,
  available: 65,
});
```

Also prove `usageEvent.aggregate` has no influence on that purchased balance.

#### Billing route test

In:

```text
tests/unit/billing-ui.test.ts
```

strengthen the valid Paid loader case to assert:

```ts
expect(result.subscription).toMatchObject({
  currentPeriodStart: "2026-09-01T00:00:00.000Z",
  currentPeriodEnd: "2026-10-01T00:00:00.000Z",
});
```

and keep/prove that the route renders those values through:

```text
billing.currentPeriod
i18n.formatDate(...)
```

Update the purchased-balance test fixture to include:

```text
refundingQuantity: 10
available: 65
```

and assert the loader returns both values independently of pack-purchase eligibility.

### i18n regression contract

In:

```text
tests/unit/billing-i18n.test.ts
```

add `refunding` to the runtime interpolation fixture.

For `billing.purchasedRecoveryCredits`, assert its placeholder set is exactly:

```ts
[
  "available",
  "committed",
  "granted",
  "refunding",
  "reserved",
]
```

for every supported catalogue.

Keep the existing all-locale billing-key parity test.

### Required Attempt-2 validation

From `moda-interact`, run:

```bash
npm run prisma:validate
npm run prisma:generate

npm run test -- \
  tests/unit/services/billing.service.test.ts \
  tests/unit/billing-ui.test.ts \
  tests/unit/billing-i18n.test.ts

npm test
npm run typecheck
npm run build
git diff --check

rg -n "moda-interact-admin" app/routes/app/billing app/services/billing
```

Record exact pass/fail/skip counts.

For the known typecheck baseline:

- report the repository-wide result under `TYPECHECK-001`;
- prove no diagnostic originates from an Attempt-2 changed file;
- do not modify unrelated baseline files.

`rg` should produce no merchant/Admin coupling introduced by this task.

### Allowed Attempt-2 scope

Allowed production files:

```text
moda-interact/app/services/billing/billing.service.ts
moda-interact/app/routes/app/billing/route.tsx
moda-interact/app/i18n/locales/*.json
```

Allowed focused test files:

```text
moda-interact/tests/unit/services/billing.service.test.ts
moda-interact/tests/unit/billing-ui.test.ts
moda-interact/tests/unit/billing-i18n.test.ts
```

Normal task/Completion Report updates are allowed through the coordination-document
exception.

Do **not** modify:

```text
Prisma schema/migrations
Background admission/reservations
RecoveryCreditPurchase lifecycle mutations
RecoveryCreditRefund lifecycle mutations
SHOPIFY-009 local recovery-capacity projection
Shopify Partner provider contracts
plan-change/cancellation/rollover logic
Admin
Messaging
Gateway
Shared package/contracts
pricing amounts
```

If the integrated schema lacks any field named in the exact safety predicate above,
STOP and return the schema mismatch to `moda_architect`; do not invent a compatibility
field.

### Completion Report requirements

Attempt 2 must include a concise evidence table:

```text
Requirement | Exact test(s) | Result
```

covering the task's original required tests 1 through 12 plus:

```text
purchased refunding reduces available
paid period ownership/snapshot inconsistencies fail closed
```

Also record immutable workflow evidence:

```text
Attempt-1 implementation full SHA:
03ba8f5c7d0bfe0c051f09e1ddd6639ee3c1c356

Attempt-1 final parent/report full SHA:
resolve the full SHA corresponding to user handoff 70b6d4c

Attempt-2 launcher claim full SHA
Attempt-2 implementation full SHA
Attempt-2 parent/report publication full SHA
database gitlink before/after
parent branch clean/pushed
implementation branch clean/pushed
```

Do not leave publication-SHA placeholders.

### Reclaim / stop condition

Return this SAME task through `/moda-task`.

Preserve:

```text
attempt: 1
```

The next authorized claim must increment to **Attempt 2 exactly once**.

After implementing only the corrections above, running validation, updating the
Completion Report, setting the task back to `status: review`, clearing
`executor`/`claimed_at`, committing/pushing both mirrored task branches and verifying
both are clean, STOP and return to `moda_architect`.

Do not start `ARCH-010-SHOPIFY-007`, `ARCH-010-SHOPIFY-009` or any system-test task.

