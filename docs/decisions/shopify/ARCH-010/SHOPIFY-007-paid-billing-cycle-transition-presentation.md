---
id: ARCH-010-SHOPIFY-007
architecture_id: ARCH-010
title: Present App Pricing billing-cycle transition and guard late-cycle top-up purchase
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 48
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-010-BACKGROUND-007
- ARCH-010-DATABASE-013
- ARCH-010-SHARED-008
- ARCH-010-SHOPIFY-003
- ARCH-010-SHOPIFY-004
enables:
- ARCH-010-SHOPIFY-012
- ARCH-010-SHOPIFY-014
created: 2026-09-11
updated: 2026-09-14
---

# ARCH-010-SHOPIFY-007: Present App Pricing billing-cycle transition and guard late-cycle top-up purchase

## Objective

Make merchant billing UI and server-side top-up creation respect the exact Shopify App Pricing billing-cycle phase for **both Free and Paid** subscriptions.

The cycle phase controls actions that create App Events. It does not redefine recovery entitlement:

```text
Paid included recovery -> period-scoped, creates normal recovery App Event
Free lifetime recovery -> lifetime, creates no normal recovery App Event
Top-up purchase (Free or Paid) -> creates recovery-credit-pack App Event
```

Merchants never access `moda-interact-admin`.

## Architect handoff from BACKGROUND-007 Attempt 8

BACKGROUND-007 Attempt 8 verified a current app-side server-guard gap that this task
already owns.

Verified current source:

```text
repository:
  kodjobaah/moda-interact

inspected main/source commit:
  f0309e7e6a722955c890e8e6791f87667afb3eb0

file:
  app/services/billing/billing.service.ts

method:
  BillingService.requestRecoveryCreditPack(...)
```

At that source state, new pack creation verifies the mapped plan, pack meter,
durable local cycle and exact provider/local cycle, but does **not** reject the
request because the cycle has entered DRAINING or RECONCILING.

This is mandatory SHOPIFY-007 implementation scope, not BACKGROUND-007 rework.

Do not add persisted `DRAINING` or `RECONCILING` BillingPeriod statuses. The schema
has only:

```text
OPEN
CLOSED
```

Derive the purchase phase from durable timestamps and the Shared drain-window
constant:

```text
drainStart =
  currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS

ACTIVE:
  now < drainStart

DRAINING:
  drainStart <= now < currentPeriodEnd

RECONCILING:
  now >= currentPeriodEnd
  AND Subscription still points to that old BillingPeriod
```

The **server mutation** must fail closed before creating either
`UsageEvent(RECOVERY_CREDIT_PACK_PURCHASE)` or `RecoveryCreditPurchase`.

Required permanent mutation tests must include at minimum:

```text
1. Paid ACTIVE + exact cycle/meter -> new purchase may proceed.
2. Free ACTIVE + exact cycle/pack meter -> new purchase may proceed without requiring
   the Paid normal recovery meter.
3. Paid DRAINING -> creates no UsageEvent and no RecoveryCreditPurchase.
4. Free DRAINING -> creates no UsageEvent and no RecoveryCreditPurchase.
5. Paid RECONCILING -> creates no UsageEvent and no RecoveryCreditPurchase.
6. Free RECONCILING -> creates no UsageEvent and no RecoveryCreditPurchase.
7. same existing purchaseId replay remains idempotent even if the current wall-clock
   phase has since entered DRAINING/RECONCILING;
8. exact provider/local cycle or pack-meter mismatch continues to fail closed.
```

The loader/UI may mirror the phase for presentation, but UI disablement is not the
security boundary.

## Inspect before editing

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/routes/app/billing/route.tsx
app/routes/app/usage/route.jsx
app/routes/app/home/route.jsx
app/routes/app/pending-recoveries/route.*
app/components/dashboard/**
app/i18n/locales/*.json
tests/unit/services/billing.service.test.ts
tests/unit/routes/**billing**
package.json
```

Read integrated SHOPIFY-003/004, BACKGROUND-007 and published Shared billing exports first.

## Shared constant

Import:

```text
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
```

from `@modainteract/moda-interact-shared/billing`.

Do not copy a literal five-minute duration into app business logic.

## Derived cycle phase

For a mapped Free or Paid subscription with an exact current local BillingPeriod:

```text
ACTIVE
  now < periodEnd - drainWindow

DRAINING
  periodEnd - drainWindow <= now < periodEnd

RECONCILING
  now >= periodEnd and Subscription still points at that expired period
```

This is derived state only. Do not add another persisted Subscription status.

## Presentation rules

### Paid

ACTIVE uses SHOPIFY-004 normal current-period presentation.

DRAINING displays a localized message that new App-Event-backed Paid activity is briefly paused while Shopify's cycle changes.

RECONCILING displays a bounded verification state and must not present expired included allowance as spendable current capacity.

### Free

Always display Free recovery entitlement from the lifetime Free counter, never from BillingPeriod.

A Free BillingPeriod is shown only as Shopify billing/top-up cycle context where useful. It must never be labelled as a monthly Free recovery allowance.

During DRAINING/RECONCILING, explain only that **new top-up purchase** is temporarily unavailable while Shopify's billing cycle is being confirmed. Do not tell the merchant that their remaining lifetime Free recoveries have expired or paused.

## Merchant routes

Keep merchant-owned routes available during DRAINING/RECONCILING:

```text
/app
/app/usage
/app/billing
/app/billing/options
/app/billing/select
/app/merchant-support
```

Read-only pending/recovery/history surfaces remain available according to existing access policy.

No merchant route/link exposes Admin.

## Top-up purchase server guard

`BillingService.requestRecoveryCreditPack(...)` must apply the same new-purchase guard to Free and Paid:

```text
exact current local BillingPeriod exists
provider current plan == mapped current plan
provider current cycle == local exact cycle
configured recovery-credit-pack meter exists in provider active usage items
now < currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
```

If DRAINING/RECONCILING or exact cycle/meter verification fails:

- create no `RecoveryCreditPurchase`;
- create no pack `UsageEvent`;
- perform no App Events request;
- return the canonical merchant-safe unavailable reason;
- preserve replay/idempotency of an already-existing purchase ID.

### Free-specific guard

For Free:

- do not require `BillingPlan.shopifyUsageEventHandle` (Paid normal recovery meter);
- require the configured `shopifyRecoveryCreditPackEventHandle` only;
- require `Subscription.billingPeriodId` to point to the exact OPEN Free provider BillingPeriod;
- do not create/reset any Free included entitlement while validating or creating a pack request.

## Behaviour matrix

| State | Paid new included recovery | Free lifetime recovery | Purchased-credit recovery | New top-up purchase |
|---|---|---|---|---|
| ACTIVE | allowed if capacity | allowed if lifetime capacity | allowed if purchased capacity | allowed if exact meter/cycle |
| DRAINING | blocked | allowed | allowed | blocked |
| RECONCILING | blocked | allowed if verified Free subscription/lifetime state remains current under ARCH-010 policy | allowed if no new billing event is required | blocked |

The Background entitlement layer remains final recovery-admission authority; this task must not add UI-only bypasses.

## No app-side rollover

The app never closes/opens BillingPeriods or grants credits. BACKGROUND-007 owns same-plan cycle rollover.

Do not add browser polling against Partner API. Billing-management loader may perform explicit Shopify verification through SHOPIFY-013/014 where required, but ordinary dashboard rendering must not become a Partner polling loop.

## Required tests

1. Paid ACTIVE derives ACTIVE;
2. Free ACTIVE derives ACTIVE from exact provider/local period;
3. exact drain start derives DRAINING;
4. exact period end derives RECONCILING;
5. Paid DRAINING/RECONCILING hides/disables included-cycle actions truthfully;
6. Free DRAINING/RECONCILING keeps lifetime-Free capacity presentation unchanged;
7. new pack purchase in ACTIVE may proceed only after exact provider/local cycle + exact pack meter verification;
8. new pack purchase in DRAINING creates no purchase/event;
9. new pack purchase in RECONCILING creates no purchase/event;
10. existing purchase replay remains idempotent;
11. Free does not require Paid normal recovery meter for pack purchase;
12. Free missing exact BillingPeriod is pack-ineligible;
13. Free missing pack meter is pack-ineligible;
14. Free DRAINING still allows remaining lifetime-Free recovery admission in the shared policy/Background path;
15. Free RECONCILING does not claim lifetime entitlement reset;
16. successor Free BillingPeriod restores pack purchase eligibility without changing lifetime Free quantities;
17. plan selection/support/navigation remain available;
18. no merchant link exposes Admin;
19. i18n parity for added states/messages.

## Non-goals

Do not implement:

- period close/open transaction;
- BullMQ worker;
- different-plan transition;
- cancellation;
- refund workflow;
- promotional credits;
- Admin UI.

## Validation

Inspect `package.json`; run focused billing service/route/component tests, declared typecheck/build tests and `git diff --check`. Do not invent scripts.

## Stop conditions

STOP if:

- exact local/provider billing-cycle comparison is unavailable;
- new purchase creation cannot be distinguished from replay;
- implementation would require turning Free lifetime entitlement into a monthly period counter;
- task would require recurring Partner polling from ordinary merchant dashboard loaders.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `app/services/billing/billing.service.ts`
- `app/routes/app/billing/route.tsx`
- `app/i18n/locales/*.json` (20 supported catalogues)
- `tests/unit/services/billing.service.test.ts`
- `tests/unit/billing-ui.test.ts`
- `tests/unit/billing-i18n.test.ts`

### Work Completed
- Preserved derived `ACTIVE`, `DRAINING`, and `RECONCILING` phases from exact timestamps and `APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS`; no persisted phase or app-side rollover was added.
- Made merchant top-up eligibility ACTIVE-only and required an exact OPEN local BillingPeriod for both Free and Paid before provider verification and again inside the write transaction.
- Added truthful Paid/Free transition copy in every locale, suppressed expired Paid included allowance during RECONCILING, preserved lifetime-Free presentation, and kept the buy form behind an explicit ACTIVE guard.
- Preserved replay-before-provider verification and Free pack independence from the Paid normal meter; successor Free cycles continue without lifetime counter mutation.

### Correction-to-Test Mapping
| Correction | Exact test evidence | Result |
|---|---|---|
| Loader eligibility requires ACTIVE | `marks pack purchase ineligible during merchant billing phase: Paid DRAINING`, `Paid RECONCILING`, `Free DRAINING`, `Free RECONCILING`; `keeps pack purchase eligible for exact ACTIVE cycle: Paid`, `Free` | Passed |
| Paid/Free transition presentation and no expired Paid allowance | `uses explicit phase copy for each plan and preserves Free lifetime presentation`; `reads paid included capacity from the current period counter` | Passed |
| OPEN local period required for Paid and Free | `rejects new pack request for CLOSED local BillingPeriod: Paid`, `Free` | Passed |
| Exact phase boundaries | `derives ACTIVE`, `DRAINING`, and `RECONCILING` from exact period timestamps | Passed |
| DRAINING/RECONCILING mutation blocks | `blocks new pack request during billing-cycle phase: Paid DRAINING`, `Paid RECONCILING`, `Free DRAINING`, `Free RECONCILING` | Passed; zero UsageEvent, purchase, and counter writes asserted |
| Replay after transition | `replays existing purchase after cycle enters DRAINING`, `RECONCILING` | Passed; provider not called on replay and one event/purchase retained |
| Successor Free cycle | `restores Free pack eligibility on an exact successor BillingPeriod without changing lifetime Free state` | Passed; successor period referenced and no counter update/upsert |

### Requirement Evidence
| Requirement | Exact test(s) | Result |
|---|---|---|
| Paid ACTIVE derives ACTIVE | `keeps pack purchase eligible for exact ACTIVE cycle: Paid` | Passed |
| Free ACTIVE derives ACTIVE | `keeps pack purchase eligible for exact ACTIVE cycle: Free` | Passed |
| Exact drain-start derives DRAINING | `derives DRAINING from exact period timestamps`; phase matrix rows | Passed |
| Exact period-end derives RECONCILING | `derives RECONCILING from exact period timestamps`; phase matrix rows | Passed |
| Paid DRAINING presentation | `uses explicit phase copy for each plan and preserves Free lifetime presentation` | Passed |
| Paid RECONCILING presentation | Same UI test; `billingPeriodPhase !== "RECONCILING"` excludes `paidIncludedAllowance` | Passed |
| Free DRAINING lifetime presentation | `marks pack purchase ineligible during merchant billing phase: Free DRAINING` | Passed; lifetime quantities unchanged |
| Free RECONCILING lifetime presentation | `marks pack purchase ineligible during merchant billing phase: Free RECONCILING` | Passed; lifetime quantities unchanged |
| ACTIVE new purchase | `creates a pending pack request for a mapped FREE plan`, `PAID_METERED` | Passed |
| Paid/Free DRAINING server block | `blocks new pack request during billing-cycle phase: Paid DRAINING`, `Free DRAINING` | Passed |
| Paid/Free RECONCILING server block | `blocks new pack request during billing-cycle phase: Paid RECONCILING`, `Free RECONCILING` | Passed |
| Existing-purchase replay after transition | `replays existing purchase after cycle enters DRAINING`, `RECONCILING` | Passed |
| Free has no Paid normal-meter dependency | `creates a pending pack request for a mapped FREE plan`; Free ACTIVE eligibility row uses `shopifyUsageEventHandle: null` | Passed |
| Free missing exact period | `fails closed when billingPeriodId is null`; initial pack-enabled Free activation coverage | Passed |
| Free missing pack meter | `creates no usage event for missing meter` | Passed |
| Free DRAINING admission remains lifetime-based | Free phase read-model rows preserve lifetime counter; Background-007 dependency remains admission authority | Passed / prerequisite evidence |
| Free RECONCILING does not reset lifetime entitlement | Free RECONCILING read-model row and successor-cycle test assert unchanged lifetime state | Passed |
| Plan selection/support/navigation remain available | Existing billing UI route, selection redirect, and system-message action tests | Passed |
| No merchant Admin link | `keeps merchant billing surfaces out of the Admin application`; required route scan | Passed; 0 matches |
| i18n parity and localized phase messages | `defines every billing key in every locale catalogue`; `preserves ICU placeholders and resolves every task key through the merchant runtime` | Passed; 20 catalogues, zero placeholders on new keys |

### Validation Results
- Focused required routes/services/i18n: 5 files, 158 passed, 0 skipped.
- Final changed-slice rerun: 3 files, 153 passed, 0 skipped.
- Full suite: `npm test` -> 38 files passed, 2 skipped; 423 tests passed, 3 skipped.
- `npm run prisma:validate` -> passed.
- `npm run prisma:generate` -> passed.
- `npm run typecheck` -> existing `TYPECHECK-001` baseline: 155 errors in 24 files. Changed-file diagnostics remain only the pre-existing `app/routes/app/billing/route.tsx:89`, `app/services/billing/billing.service.ts:1053`, and `tests/unit/services/billing.service.test.ts:1291`; no new Attempt-2 diagnostic remains.
- `npm run build` -> passed; existing Zod annotation, Prisma external-resolution, and bundle-size warnings only.
- `git diff --check` -> passed.
- Admin isolation scan across merchant routes -> 0 matches.
- Drain-window literal scan -> 0 matches.

### Git / VCS
- Attempt-1 claim full SHA: `ef68ab10bd9a39ecf485383248c6c91eac3fd780`.
- Attempt-1 implementation full SHA: `58a138cd27174d09843d04683547310a9e36c8b2`.
- Attempt-1 parent/report full SHA: `c522bd727a9c860b7e1689da95b1d06eefe20faa`.
- Attempt-2 launcher claim full SHA: `37be206ceb4228cce37f7449ddd88ff54139cb88`.
- Attempt-2 implementation commit: `140c476f789fe5694b5c2632413caebc7e9c1f06`, pushed to `origin/task/ARCH-010-SHOPIFY-007` in `moda-interact`.
- Dedicated parent/report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-007`, branch `task/ARCH-010-SHOPIFY-007`.
- Dedicated implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-007`, branch `task/ARCH-010-SHOPIFY-007`.
- Launcher evidence: dependency gate passed; recursive submodule sync/update passed; implementation database submodule was `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94` before and after; parent and implementation origins were current with no startup fast-forward required.
- No implementation submodule gitlink was staged or changed.

## Architect Review — Attempt 1

### Status

**Changes Requested**

Attempt 1 correctly introduces the shared-constant phase derivation, preserves
existing purchase-id replay before provider verification, keeps Free pack purchase
independent from the Paid normal recovery meter, and adds the server-side wall-clock
guard before creating a new pack UsageEvent/RecoveryCreditPurchase.

Three production issues remain:

1. the merchant loader can still mark a DRAINING/RECONCILING top-up as eligible;
2. the UI uses unrelated existing copy and continues to present expired Paid included
   capacity during RECONCILING;
3. the server-side mutation requires an OPEN local BillingPeriod only for Free, so a
   stale/corrupt CLOSED Paid period can still pass the new-purchase guard if its
   timestamps are otherwise in ACTIVE phase.

The required Attempt-1 test matrix is also incomplete: the current mutation test
covers DRAINING only, not RECONCILING, and there is no successor-Free restoration
test.

Attempt 2 must make only the bounded corrections below.

### Accepted Attempt-1 behavior to preserve

Preserve:

- `APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS` from
  `@modainteract/moda-interact-shared/billing`;
- derived phases:

```text
ACTIVE
DRAINING
RECONCILING
```

with exact drain-start and exact period-end boundaries;

- no persisted phase/status field;
- no app-side BillingPeriod rollover;
- existing purchase replay before provider/phase verification;
- exact provider/local cycle comparison;
- exact recovery-credit-pack meter verification;
- Free pack purchase does not require `shopifyUsageEventHandle`;
- no lifetime-Free counter mutation during pack purchase;
- no Admin merchant link;
- existing Shopify plan selection/support routes.

### Finding 1 — merchant pack eligibility ignores cycle phase

`getMerchantBillingState(...)` currently derives `billingPeriodPhase`, but
`recoveryCreditPackPurchaseEligible` is calculated only from:

```text
meter verified
exact local/provider cycle
```

It does **not** require:

```text
billingPeriodPhase === ACTIVE
```

Therefore a DRAINING or RECONCILING billing loader can return:

```text
recoveryCreditPackPurchaseEligible = true
```

and `app/routes/app/billing/route.tsx` can still render the Buy form even though the
POST correctly rejects the request.

The UI is not the security boundary, but it must be truthful.

#### Required correction

In:

```text
app/services/billing/billing.service.ts
```

set merchant purchase eligibility true only when all are true:

```text
provider current plan == mapped local current plan
exact provider/local cycle matches
configured pack meter is present in provider usageEventHandles
pointed local BillingPeriod status == OPEN
billingPeriodPhase == ACTIVE
```

Use the existing derived `billingPeriodPhase`; do not add another clock calculation.

The result must be:

```text
ACTIVE       -> eligible only if all existing meter/cycle conditions pass
DRAINING     -> false
RECONCILING  -> false
```

In:

```text
app/routes/app/billing/route.tsx
```

also include an explicit presentation guard:

```text
billingPeriodPhase === "ACTIVE"
```

around the new-top-up purchase form.

Do not rely only on this UI guard; the server mutation remains authoritative.

### Finding 2 — transition copy and Paid RECONCILING presentation are not truthful

Current route behavior uses:

```text
DRAINING:
  billing.recoveryCreditPurchasePending
  -> "Recovery credit purchase is being confirmed by Shopify."

RECONCILING:
  billing.configurationUnavailableDescription
  -> generic mapping/support error copy
```

Neither describes a billing-cycle transition.

Also, during Paid RECONCILING the route still renders:

```text
billing.paidIncludedAllowance
```

from the expired old BillingPeriod before rendering the generic message.

The task explicitly requires that RECONCILING must not present expired included
allowance as spendable current capacity.

#### Required correction

Add these merchant i18n keys to **every supported locale catalogue**:

```text
billing.paidCycleDraining
billing.paidCycleReconciling
billing.freeCycleDraining
billing.freeCycleReconciling
```

Use these exact English values:

```text
billing.paidCycleDraining
  Shopify is changing your billing cycle. New paid recovery activity and top-up purchases are briefly paused.

billing.paidCycleReconciling
  We are confirming your new Shopify billing cycle. Paid included recovery capacity and new top-up purchases are temporarily unavailable.

billing.freeCycleDraining
  Shopify is changing your billing cycle. Your remaining lifetime Free recoveries are unchanged; only new top-up purchases are briefly paused.

billing.freeCycleReconciling
  We are confirming your Shopify billing cycle. Your remaining lifetime Free recoveries are unchanged; new top-up purchases are temporarily unavailable.
```

For every non-English catalogue add a localized equivalent in that catalogue's
existing language. Do not copy the English sentence into non-English catalogues.
These four keys have **no ICU placeholders**.

In:

```text
app/routes/app/billing/route.tsx
```

render phase copy deterministically:

```text
Paid + DRAINING
  -> billing.paidCycleDraining

Paid + RECONCILING
  -> billing.paidCycleReconciling

Free + DRAINING
  -> billing.freeCycleDraining

Free + RECONCILING
  -> billing.freeCycleReconciling
```

For Paid:

```text
ACTIVE
  -> existing SHOPIFY-004 included allowance presentation

DRAINING
  -> existing current-period balance may remain visible,
     but the paid-cycle pause message must be visible and no new App-Event-backed
     purchase form may be shown

RECONCILING
  -> do NOT render billing.paidIncludedAllowance for the expired old period
  -> render billing.paidCycleReconciling
```

For Free:

```text
ACTIVE / DRAINING / RECONCILING
  -> keep billing.lifetimeFreeAllowance derived from the lifetime Free counter
```

Do not hide or zero lifetime Free capacity merely because the Shopify billing cycle
is DRAINING/RECONCILING.

Do not use `billing.configurationUnavailableDescription` as normal
RECONCILING-cycle copy.

Do not use `billing.recoveryCreditPurchasePending` as normal DRAINING-cycle copy;
that key remains reserved for an actual purchase that has already been created and is
waiting for Shopify billing confirmation.

### Finding 3 — new Paid top-up mutation can target a CLOSED BillingPeriod

`requestRecoveryCreditPack(...)` currently enforces:

```text
Free -> local BillingPeriod.status == OPEN
```

but does not enforce the same OPEN condition for Paid.

A stale/corrupt Paid Subscription can therefore point to:

```text
billingPeriod.status = CLOSED
currentPeriodEnd = future
```

and still pass:

```text
hasDurableBillingPeriod(...)
exact provider/local cycle
deriveBillingPeriodPhase(...) == ACTIVE
```

That can create a new pack UsageEvent referencing a CLOSED BillingPeriod.

#### Required correction

For **both Free and Paid**, before the provider call require:

```text
subscription.billingPeriod != null
subscription.billingPeriod.id == subscription.billingPeriodId
subscription.billingPeriod.status == OPEN
```

Preserve all existing exact-boundary checks.

Inside the transaction re-read, require again for **both Free and Paid**:

```text
currentSubscription.billingPeriod?.status == OPEN
```

before creating:

```text
UsageEvent(RECOVERY_CREDIT_PACK_PURCHASE)
RecoveryCreditPurchase
```

If the local period is CLOSED or missing, fail closed using the existing
merchant-safe local/configuration-unavailable error family.

Do not reopen the period and do not change Background-owned period state.

### Required Attempt-2 permanent tests

#### Billing service phase/read-model tests

File:

```text
tests/unit/services/billing.service.test.ts
```

Keep the existing exact boundary test and add:

```text
marks pack purchase ineligible during merchant billing phase: %s
```

Rows:

```text
Paid DRAINING
Paid RECONCILING
Free DRAINING
Free RECONCILING
```

For every row configure:

```text
exact provider/local cycle
verified pack meter
OPEN local period
```

and assert:

```text
billingPeriodPhase == expected phase
recoveryCreditPackMeterVerified == true
recoveryCreditPackPurchaseEligible == false
```

For Free rows also assert the returned lifetime-Free quantities are unchanged.

Add:

```text
keeps pack purchase eligible for exact ACTIVE cycle: %s
```

Rows:

```text
Paid
Free
```

Assert:

```text
billingPeriodPhase == ACTIVE
recoveryCreditPackPurchaseEligible == true
```

Free must use:

```text
shopifyUsageEventHandle = null
```

and still pass.

#### Server mutation phase matrix

Replace/extend the current single transition test with:

```text
blocks new pack request during billing-cycle phase: %s
```

Rows:

```text
Paid DRAINING
Paid RECONCILING
Free DRAINING
Free RECONCILING
```

Freeze system time deterministically with `vi.useFakeTimers()` /
`vi.setSystemTime(...)`; do not derive the fixture from the machine's real current
time.

For every row assert:

```text
rejects with the canonical transition-unavailable message
zero new UsageEvent
zero new RecoveryCreditPurchase
zero shopEntitlementCounter update/upsert
```

Restore real timers after each test.

Add:

```text
rejects new pack request for CLOSED local BillingPeriod: %s
```

Rows:

```text
Paid
Free
```

Use an otherwise exact ACTIVE provider/local cycle.

Assert:

```text
provider need not be called if the local CLOSED period is rejected preflight
zero UsageEvent
zero RecoveryCreditPurchase
```

#### Replay after phase transition

Add:

```text
replays existing purchase after cycle enters %s
```

Rows:

```text
DRAINING
RECONCILING
```

Create/store the purchase once while ACTIVE, move/freeze time into the requested
phase, make the provider unavailable, then replay the **same purchaseId**.

Assert:

```text
same purchase returned
provider not called for replay
still exactly one UsageEvent
still exactly one RecoveryCreditPurchase
```

This proves idempotent replay remains allowed even when new purchases are blocked.

#### Successor Free cycle

Add:

```text
restores Free pack eligibility on an exact successor BillingPeriod without changing lifetime Free state
```

Use Free with:

```text
shopifyUsageEventHandle = null
pack meter configured
old cycle no longer current
Subscription now points to successor OPEN BillingPeriod
provider current cycle exactly equals successor cycle
phase ACTIVE
```

Assert:

```text
new pack request succeeds
UsageEvent.billingPeriodId == successor BillingPeriod id
shopEntitlementCounter.update not called
shopEntitlementCounter.upsert not called
```

Do not create/reset a monthly Free included counter.

### Required billing UI evidence

File:

```text
tests/unit/billing-ui.test.ts
```

Add source/loader assertions proving:

```text
billingPeriodPhase === "ACTIVE"
```

is part of the buy-form condition.

Add exact phase presentation tests/source assertions:

```text
Paid DRAINING references billing.paidCycleDraining
Paid RECONCILING references billing.paidCycleReconciling
Free DRAINING references billing.freeCycleDraining
Free RECONCILING references billing.freeCycleReconciling
```

Also prove the Paid included allowance branch excludes RECONCILING.

For Free DRAINING and Free RECONCILING, the loader/state fixture must preserve the
same:

```text
lifetimeFree.grantedQuantity
lifetimeFree.committedQuantity
lifetimeFree.reservedQuantity
lifetimeFree.remaining
```

and the route must continue to contain/use:

```text
billing.lifetimeFreeAllowance
```

Do not claim Free lifetime recovery is paused.

### Required i18n evidence

File:

```text
tests/unit/billing-i18n.test.ts
```

Add all four phase keys to the task key list.

For each supported locale assert:

```text
key exists
value is non-empty
placeholder set == []
merchant runtime resolves the key
```

Keep billing-key parity across all catalogues.

For every non-English locale also assert its value for each new phase key is not
byte-for-byte equal to the English value. This prevents accidental English fallback
copy in localized catalogues.

### Required Attempt-2 validation

From `moda-interact` run:

```bash
npm run prisma:validate
npm run prisma:generate

npm test -- --run \
  tests/unit/services/billing.service.test.ts \
  tests/unit/billing-ui.test.ts \
  tests/unit/billing-i18n.test.ts \
  tests/unit/usage-route.test.ts \
  tests/unit/home-route.test.ts \
  tests/unit/routes/pending-recoveries-route.test.ts

npm test
npm run typecheck
npm run build
git diff --check

rg -n "moda-interact-admin" \
  app/routes/app/billing \
  app/routes/app/usage \
  app/routes/app/home \
  app/routes/app/pending-recoveries

rg -n "5 \* 60 \* 1000|300000" \
  app/services/billing \
  app/routes/app/billing
```

Expected static results:

```text
merchant/Admin coupling scan -> zero matches
literal drain-window business-logic scan -> zero matches
```

The existing repository `TYPECHECK-001` baseline is non-blocking only if:

- the repository-wide total does not worsen from the Attempt-1 documented baseline;
- no Attempt-2 changed line introduces a new diagnostic.

### Allowed Attempt-2 scope

Production:

```text
app/services/billing/billing.service.ts
app/routes/app/billing/route.tsx
app/i18n/locales/*.json
```

Tests:

```text
tests/unit/services/billing.service.test.ts
tests/unit/billing-ui.test.ts
tests/unit/billing-i18n.test.ts
```

Normal task/Completion Report updates are allowed through the coordination-document
exception.

`app/services/billing/billing.types.ts` should remain unchanged unless TypeScript
requires no more than a direct type correction for the existing
`BillingPeriodPhase`.

Do not modify:

```text
Prisma schema/migrations
Shared package/contracts
BACKGROUND-007
BACKGROUND rollover/admission code
RecoveryCreditPurchase settlement logic
UsageEvent publishing worker
plan-change/cancellation/refund/promotion behavior
Admin
Messaging
Gateway
ordinary merchant route topology
```

If satisfying the correction would require any Background/schema/Shared change, STOP
and return the exact dependency gap to `moda_architect`.

### Completion Report requirements

Attempt 2 must replace the broad correction summary with a truthful evidence table:

```text
Requirement | Exact test(s) | Result
```

covering original task requirements 1 through 19.

At minimum the table must explicitly map:

```text
Paid ACTIVE
Free ACTIVE
exact drain-start
exact period-end
Paid DRAINING presentation
Paid RECONCILING presentation
Free DRAINING lifetime presentation
Free RECONCILING lifetime presentation
ACTIVE new purchase
Paid/Free DRAINING server block
Paid/Free RECONCILING server block
existing-purchase replay after transition
Free no Paid normal-meter dependency
Free missing exact period
Free missing pack meter
successor Free BillingPeriod restoration
route availability
Admin isolation
i18n parity
```

Also record immutable workflow evidence:

```text
Attempt-1 claim full SHA:
ef68ab10bd9a39ecf485383248c6c91eac3fd780

Attempt-1 implementation full SHA corresponding to:
58a138c

Attempt-1 final parent/report full SHA corresponding to:
c522bd7

Attempt-2 launcher claim full SHA
Attempt-2 implementation full SHA
Attempt-2 parent/report publication full SHA
database gitlink before/after
dedicated parent worktree/branch
dedicated implementation worktree/branch
both branches clean and pushed
```

Resolve abbreviated Attempt-1 SHAs to full SHAs from the dedicated task worktrees.
Do not leave publication placeholders.

### Reclaim / stop condition

Return this SAME task through `/moda-task`.

Preserve:

```text
attempt: 1
```

The next authorized claim must increment to **Attempt 2 exactly once**.

After implementing only the corrections above, running validation, completing the
19-item evidence map, updating the Completion Report, setting `status: review`,
clearing `executor`/`claimed_at`, committing/pushing both mirrored task branches and
verifying both are clean, STOP and return to `moda_architect`.

Do not start `ARCH-010-SHOPIFY-012` or `ARCH-010-SHOPIFY-014`.

## Architect Review — Attempt 2

### Status

**Changes Requested**

Attempt 2 correctly closes the three defects from Attempt 1:

- merchant top-up eligibility is ACTIVE-only;
- Paid/Free DRAINING and RECONCILING have dedicated localized presentation;
- Paid RECONCILING no longer renders the old included allowance;
- the Buy form has an explicit ACTIVE presentation guard;
- both Paid and Free new pack creation require the pointed BillingPeriod to be OPEN
  before provider verification and again inside the write transaction;
- Paid/Free DRAINING and RECONCILING server blocks are covered;
- existing-purchase replay remains provider-independent after the wall clock moves
  into DRAINING/RECONCILING;
- successor Free cycle purchase uses the successor BillingPeriod without lifetime
  counter mutation;
- all 20 locale catalogues contain localized phase copy.

One production correctness defect remains: the merchant cycle phase is currently
conditioned on the provider still reporting the same cycle. That reverses the
authority defined by this task.

No purchase-mutation, i18n-copy, route-topology or Background redesign is requested.

### Finding — `billingPeriodPhase` is incorrectly dependent on provider/local cycle equality

The task defines phase from the **durable local current BillingPeriod**:

```text
drainStart =
  Subscription.currentPeriodEnd
    - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS

ACTIVE:
  now < drainStart

DRAINING:
  drainStart <= now < currentPeriodEnd

RECONCILING:
  now >= currentPeriodEnd
  AND Subscription still points to that old BillingPeriod
```

This is intentionally local derived state. Provider verification is an additional
requirement for creating a new App-Event-backed purchase.

Attempt 2 currently does:

```ts
const providerSubscription =
  await this.provider.getActiveSubscription(...);

if (
  providerSubscription
  && hasMatchingBillingCycle(subscription, providerSubscription)
) {
  billingPeriodPhase =
    deriveBillingPeriodPhase(subscription.currentPeriodEnd);
}
```

Therefore phase becomes `null` in exactly the transition states where the provider is
most likely to have advanced first.

Example:

```text
local Subscription:
  billingPeriodId = old-period
  currentPeriodEnd = 2026-10-01T00:00:00Z
  old BillingPeriod still OPEN

now:
  2026-10-01T00:00:00Z

Shopify provider:
  same plan
  successor currentPeriodStart = 2026-10-01T00:00:00Z
  successor currentPeriodEnd   = 2026-10-31T00:00:00Z
```

The correct local phase is:

```text
RECONCILING
```

because Background has not yet replaced the old local BillingPeriod.

The current implementation instead gets:

```text
hasMatchingBillingCycle(...) = false
billingPeriodPhase = null
```

For a Paid merchant, `paidIncluded` may still be a valid projection of that old OPEN
period, so the route condition:

```ts
billingPeriodPhase !== "RECONCILING" && paidIncluded
```

can render the **expired old included balance** as if it were current spendable
capacity.

The same false-null phase occurs when the Partner read temporarily fails. A provider
outage must make a new top-up ineligible, but it must not erase the locally known
DRAINING/RECONCILING phase.

### Required Attempt-3 correction

Modify only:

```text
app/services/billing/billing.service.ts
tests/unit/services/billing.service.test.ts
tests/unit/billing-ui.test.ts
```

plus this task/Completion Report.

Do not modify locale copy unless a test exposes an actual catalogue defect.

#### 1. Derive phase from the exact OPEN durable local cycle before the provider request

In:

```text
BillingService.getMerchantBillingState(...)
```

derive `billingPeriodPhase` from local durable state **before** calling Shopify.

Use one explicit local validity predicate equivalent to:

```ts
const hasExactOpenLocalCycle = Boolean(
  subscription?.plan?.active
    && subscription.status !== SubscriptionProjectionStatus.NO_CONTRACT
    && hasDurableBillingPeriod(subscription)
    && subscription.billingPeriod?.status === BillingPeriodStatus.OPEN
    && subscription.currentPeriodStart
    && subscription.currentPeriodEnd
    && subscription.currentPeriodStart.getTime()
         < subscription.currentPeriodEnd.getTime()
);
```

Then:

```ts
const billingPeriodPhase =
  hasExactOpenLocalCycle
    ? deriveBillingPeriodPhase(subscription!.currentPeriodEnd)
    : null;
```

Equivalent TypeScript narrowing is acceptable.

Do not require the provider current cycle to match before deriving this local phase.

Do not derive a phase for:

```text
missing BillingPeriod
mismatched billingPeriodId/relation
CLOSED BillingPeriod
missing local start/end
local periodStart >= periodEnd
NO_CONTRACT
inactive mapped plan
```

Those are not an exact OPEN local current cycle.

#### 2. Keep provider truth as a separate purchase-verification authority

The provider read still owns:

```text
current provider plan handle
provider current cycle
active usage-event handles
```

Preserve:

```text
recoveryCreditPackMeterVerified
```

as provider meter verification.

Preserve new-purchase eligibility as requiring **all** of:

```text
local billingPeriodPhase == ACTIVE
local pointed BillingPeriod == OPEN
provider plan == mapped local plan
provider/local cycle exact match
provider exposes exact pack meter
```

If provider verification fails or the provider has already advanced to another
cycle:

```text
billingPeriodPhase
  -> remains the locally derived ACTIVE/DRAINING/RECONCILING value

recoveryCreditPackPurchaseEligible
  -> false
```

Do not overwrite the local phase to `null` in the provider `catch`.

#### 3. Keep server mutation authority unchanged

`requestRecoveryCreditPack(...)` already performs the correct stricter mutation
sequence:

```text
existing purchase replay first
exact OPEN local period
provider plan/meter
exact provider/local cycle
provider-derived ACTIVE phase
transactional re-read
create UsageEvent + RecoveryCreditPurchase
```

Do not rewrite this path for Attempt 3 unless an exact focused test fails.

The server may continue deriving the phase from the provider end there because
`hasMatchingBillingCycle(...)` has already proven provider/local start and end are
identical.

### Required Attempt-3 permanent tests

#### A. Provider already advanced but local period is still old

In:

```text
tests/unit/services/billing.service.test.ts
```

add:

```text
derives RECONCILING from the durable local period when Shopify has already advanced to the successor cycle
```

Freeze:

```text
local period:
  start = 2026-09-01T00:00:00.000Z
  end   = 2026-10-01T00:00:00.000Z

now = 2026-10-01T00:00:00.000Z
```

Keep local:

```text
billingPeriodId = period-old
billingPeriod.status = OPEN
Subscription still points to period-old
```

Return provider truth for the **same plan and same pack meter** but successor cycle:

```text
start = 2026-10-01T00:00:00.000Z
end   = 2026-10-31T00:00:00.000Z
```

Assert:

```ts
expect(result.billingPeriodPhase).toBe("RECONCILING");
expect(result.recoveryCreditPackMeterVerified).toBe(true);
expect(result.recoveryCreditPackPurchaseEligible).toBe(false);
```

For Paid also assert the underlying `paidIncluded` projection may still exist; the
route presentation, not the read model, suppresses it while RECONCILING.

#### B. Provider transport failure does not erase local phase

Add a parameterized test:

```text
preserves durable local billing phase when Shopify verification fails: %s
```

Rows:

```text
DRAINING
RECONCILING
```

Use exact OPEN local state and make:

```ts
provider.getActiveSubscription.mockRejectedValue(
  new Error("Shopify unavailable"),
);
```

Assert:

```text
billingPeriodPhase == expected local phase
recoveryCreditPackMeterVerified == false
recoveryCreditPackPurchaseEligible == false
```

For the RECONCILING Paid row, assert `paidIncluded` remains a data projection so the
UI test can prove it is hidden specifically because phase is RECONCILING.

#### C. Malformed local cycle does not become ACTIVE/DRAINING/RECONCILING

Add:

```text
does not derive a merchant billing phase from an invalid local cycle
```

Use:

```text
currentPeriodStart >= currentPeriodEnd
BillingPeriod relation uses the same invalid boundaries
status = OPEN
```

Assert:

```text
billingPeriodPhase = null
recoveryCreditPackPurchaseEligible = false
```

The provider may return matching malformed boundaries; local invalidity must still
prevent phase/purchase eligibility.

#### D. UI proof for provider-moved local RECONCILING

In:

```text
tests/unit/billing-ui.test.ts
```

add a loader/render-source regression named:

```text
uses durable RECONCILING phase to hide expired Paid included capacity
```

Supply loader state with:

```text
planKind = PAID_METERED
billingPeriodPhase = RECONCILING
paidIncluded = {
  grantedQuantity: 100,
  committedQuantity: 20,
  reservedQuantity: 0,
  forfeitedQuantity: 0,
  remaining: 80,
}
recoveryCreditPackPurchaseEligible = false
```

Preserve the current source assertions proving:

```text
billingPeriodPhase !== "RECONCILING"
```

guards `billing.paidIncludedAllowance`, and:

```text
billing.paidCycleReconciling
```

is the merchant phase message.

The important evidence is that Paid included projection may be non-null while the
RECONCILING phase still prevents it being presented as current capacity.

#### E. Make the successor-Free test time-independent

The current test:

```text
restores Free pack eligibility on an exact successor BillingPeriod without changing lifetime Free state
```

uses fixed October 2026 dates without freezing the wall clock.

Wrap it in:

```ts
vi.useFakeTimers();
vi.setSystemTime(new Date("2026-10-02T00:00:00.000Z"));
...
vi.useRealTimers();
```

or another fixed ACTIVE time within the successor cycle.

Do not leave the test dependent on the machine/current calendar date.

### Completion Report correction

Keep the existing 19-requirement evidence table but correct the phase-authority rows
so they refer to executable tests demonstrating that phase is local durable derived
state.

Add a short invariant section:

```text
Cycle phase authority:
  durable local exact OPEN BillingPeriod timestamps

New top-up authority:
  local ACTIVE phase
  + exact provider/local cycle
  + provider plan
  + provider pack meter

Provider failure/moved successor:
  does not erase local phase
  does make new purchase ineligible
```

Do not claim that exact provider/local cycle equality is required merely to determine
DRAINING/RECONCILING presentation.

### Required Attempt-3 validation

From `moda-interact` run:

```bash
npm run prisma:validate
npm run prisma:generate

npm test -- --run \
  tests/unit/services/billing.service.test.ts \
  tests/unit/billing-ui.test.ts \
  tests/unit/billing-i18n.test.ts \
  tests/unit/usage-route.test.ts \
  tests/unit/home-route.test.ts \
  tests/unit/routes/pending-recoveries-route.test.ts

npm test
npm run typecheck
npm run build
git diff --check

rg -n "moda-interact-admin" \
  app/routes/app/billing \
  app/routes/app/usage \
  app/routes/app/home \
  app/routes/app/pending-recoveries

rg -n "5 \* 60 \* 1000|300000" \
  app/services/billing \
  app/routes/app/billing
```

Record exact pass/fail/skip totals.

The existing `TYPECHECK-001` baseline remains non-blocking only if:

- it does not worsen from Attempt 2;
- no Attempt-3 changed line introduces a new diagnostic.

### Attempt-3 allowed scope

Production:

```text
app/services/billing/billing.service.ts
```

Tests:

```text
tests/unit/services/billing.service.test.ts
tests/unit/billing-ui.test.ts
```

Task/Completion Report updates are allowed through the coordination-document
exception.

Do not modify:

```text
app/routes/app/billing/route.tsx
app/i18n/locales/*.json
app/services/billing/billing.types.ts
Prisma schema/migrations
Shared package/contracts
BACKGROUND-007 or any Background service
RecoveryCreditPurchase settlement
UsageEvent publishing
plan-change/cancellation/refund/promotion logic
Admin
Messaging
Gateway
```

If deriving the local phase independently requires any schema/Shared/Background
change, STOP and return the exact incompatibility to `moda_architect`.

### Workflow evidence required

Preserve:

```text
Attempt-1 claim:
ef68ab10bd9a39ecf485383248c6c91eac3fd780

Attempt-1 implementation:
58a138cd27174d09843d04683547310a9e36c8b2

Attempt-1 parent/report:
c522bd727a9c860b7e1689da95b1d06eefe20faa

Attempt-2 launcher claim:
37be206ceb4228cce37f7449ddd88ff54139cb88

Attempt-2 implementation:
140c476f789fe5694b5c2632413caebc7e9c1f06

Attempt-2 final parent/report:
947179a0c96ee91a0b9fdc6ad653009a71681c3a
```

Record additionally:

```text
Attempt-3 launcher claim full SHA
Attempt-3 implementation full SHA
Attempt-3 parent/report publication full SHA
database gitlink before/after
parent task branch clean/pushed
implementation task branch clean/pushed
```

### Reclaim / stop condition

Return this SAME task through `/moda-task`.

Preserve:

```text
attempt: 2
```

The next authorized claim must increment to **Attempt 3 exactly once**.

After implementing only the local-phase-authority correction, adding the focused
regressions above, making the successor-Free test time-independent, running
validation, updating the Completion Report, setting `status: review`, clearing
`executor`/`claimed_at`, committing/pushing both mirrored task branches and verifying
both are clean, STOP and return to `moda_architect`.

Do not start `ARCH-010-SHOPIFY-012` or `ARCH-010-SHOPIFY-014`.

