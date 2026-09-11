---
id: ARCH-010-SHOPIFY-001
architecture_id: ARCH-010
title: Establish fresh-install no-plan state and onboarding-only merchant access
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: copilot
claimed_at: 2026-09-11T22:22:53Z
attempt: 2
depends_on:
  - ARCH-007-SHOPIFY-001
  - ARCH-007-SHOPIFY-002
enables:
  - ARCH-010-SHOPIFY-002
created: 2026-09-11
updated: 2026-09-11T22:11:44Z
---

# ARCH-010-SHOPIFY-001: Establish fresh-install no-plan state and onboarding-only merchant access

## Architecture

Canonical portable architecture definition:

`docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`

This task implements only **Fresh install -> Installed / No plan / Onboarding**.

## Objective

For a genuinely new Shopify merchant, make the first durable Moda state deterministic and make the existing onboarding experience the first merchant screen.

After successful Shopify identity resolution, a new shop must have:

```text
Shop.status                       ACTIVE
ShopSettings.onboardingCompleted  false
Subscription.status               NO_CONTRACT
Subscription.planId               null
Subscription.pendingPlanId        null
no BillingPeriod
no plan entitlement grant
```

The merchant must see the existing `Onboarding` UI at `/app`. Product/usage surfaces must remain unavailable until a mapped Shopify plan is verified active.

## Repository boundary

Repository:

```text
moda-interact/
```

Agent:

```text
moda_app
```

Do not modify:

```text
moda-interact-admin/
moda-interact-background/
moda-interact-database/
moda-interact-shared/
moda-interact-gateway/
moda-interact-messaging/
```

If implementation appears to require a schema, Shared contract, Background worker, Gateway, Admin or Messaging change, STOP and return the gap to `moda_architect`.

## Current implementation to inspect before editing

Read these files first:

```text
app/services/shop/shop.service.ts
app/routes/auth/catchall/route.jsx
app/routes/app/route.jsx
app/routes/app/home/route.jsx
app/routes/app/billing/route.tsx
app/routes/app/billing/select/route.jsx
app/components/onboarding/Onboarding.jsx
app/routes/app/usage/route.jsx
app/routes/app/pending-recoveries/route.jsx
app/services/billing/billing.service.ts
app/services/shop/shop-access-policy.ts
app/routes.ts
```

Also inspect focused tests covering those files before changing source.

## Required behaviour

### 1. Durable fresh-install projection

When `ShopService.resolveShopifyShop()` resolves a shop and no local `Subscription` row exists for that `shopId`, create exactly one projection:

```text
status = NO_CONTRACT
planId = null
observedShopifyPlanHandle = null
billing-period pointer = null
currentPeriodStart = null
currentPeriodEnd = null
trialEndsAt = null
cancelAtPeriodEnd = false
providerSubscriptionId = null
pendingShopifyPlanHandle = null
pendingPlanId = null
pendingEffectiveAt = null
```

Use the exact fields present in the repository's accepted Prisma client at execution time. Do not invent a field from a future ARCH-010 schema revision if it has not yet been integrated.

Creation MUST be idempotent by the existing unique `Subscription.shopId` constraint.

For an existing Subscription row, **do not update it to NO_CONTRACT** from this initialization path. In particular, do not overwrite:

```text
ACTIVE
TRIALING
UNMAPPED
SYNC_ERROR
existing NO_CONTRACT lifecycle timestamps/history
```

Do not use this task to implement reinstall reconciliation; reinstall is a later ARCH-010 iteration.

### 2. Do not grant credits on installation

Fresh installation alone MUST NOT:

- create a BillingPeriod;
- consume/create a Free lifetime entitlement reservation;
- increment `FREE_RECOVERY_LIFETIME`;
- create purchased-credit grants;
- create a recovery-credit purchase;
- report an App Event to Shopify.

The existing Free plan's 5 lifetime recoveries become relevant only after Free plan activation is verified in a later transition.

### 3. Render onboarding at `/app`

Correct the current contradictory route behaviour in `app/routes/app/home/route.jsx`.

Today the loader redirects when `!settings || !settings.onboardingCompleted`, while the component later contains an `Onboarding` branch for that same condition. Remove the redirect-to-billing behaviour and return a **minimal onboarding loader result** instead.

For incomplete onboarding, the loader MUST NOT perform dashboard/recovery/usage work such as:

```text
readPendingRecoveries
checkoutRecovery.findMany
billingPeriod.findMany
usageEvent.findMany/aggregate for dashboard presentation
```

It should return only the data necessary for the existing `Onboarding` component, including merchant locale/time-zone context.

The component must render:

```text
<Onboarding merchantUi={merchantUi} />
```

for the fresh no-plan state.

Do not duplicate the onboarding component in a new route unless the existing route structure makes reuse impossible; if so, STOP and return the conflict to `moda_architect` before redesigning routing.

### 4. Plan-selection navigation remains Shopify-hosted

Preserve the existing onboarding CTA path:

```text
/app -> /app/billing -> /app/billing/select -> Shopify-hosted pricing
```

Do not introduce:

```text
appSubscriptionCreate
billing.request
appPurchaseOneTimeCreate
```

Do not call the Partner API simply to render the first onboarding page.

### 5. Merchant surfaces allowed in NO_CONTRACT/onboarding state

Allowed:

```text
/app
/app/billing
/app/billing/select
/app/merchant-support
/app/billing/callback     transition/resource endpoint only
```

`/app/merchant-support` remains merchant-facing. `moda-interact-admin` is never a merchant surface.

Product/usage data surfaces must not expose functional data for this state.

At minimum make the following deterministic:

```text
/app/usage
/app/pending-recoveries
```

When onboarding is incomplete or local subscription projection is `NO_CONTRACT`, redirect navigational UI routes to `/app`; resource endpoints must use an equivalent fail-closed response/redirect compatible with their existing caller. Do not return a successful merchant product dataset merely because `Shop.status=ACTIVE`.

Do not add Admin access or Admin redirects.

### 6. Background/service entitlement remains fail-closed

Do not modify Background in this task. Existing Background billing admission already treats missing/`NO_CONTRACT` subscription as unavailable.

Add application-side tests only where required to prove the merchant routes introduced/changed here cannot expose product behaviour before plan activation.

### 7. Existing subscription safety

Add regression coverage proving repeated `resolveShopifyShop()` calls for a shop with an existing active subscription do not reset or alter the subscription.

This protects normal requests because `resolveShopifyShop()` is called repeatedly across authenticated merchant routes.

## Explicit non-goals

Do NOT implement in this task:

- Free plan activation;
- paid plan activation;
- Shopify billing callback redesign beyond preserving existing behaviour;
- billing-period creation/rollover;
- pending plan upgrades/downgrades;
- subscription event history;
- uninstall or reinstall changes;
- subscription cancellation;
- top-up purchase redesign;
- top-up refund behaviour;
- BullMQ billing lifecycle scheduling;
- Redis recovery/reconstruction;
- Admin UI;
- system tests.

## Required tests

Add/adjust focused tests that prove at least:

1. a newly resolved shop gets exactly one `NO_CONTRACT` Subscription projection;
2. repeated resolution is idempotent;
3. resolving a shop with an existing ACTIVE subscription does not overwrite it;
4. resolving a shop with an existing TRIALING subscription does not overwrite it;
5. fresh install does not create BillingPeriod or credit/purchase records;
6. `/app` with `onboardingCompleted=false` renders onboarding rather than redirecting to `/app/billing`;
7. the incomplete-onboarding `/app` loader does not query recovery/dashboard/usage datasets;
8. onboarding's plan CTA continues to lead through the existing billing/Shopify-hosted pricing path;
9. `/app/usage` is unavailable and routes back to onboarding for NO_CONTRACT/incomplete onboarding;
10. `/app/pending-recoveries` fails closed for NO_CONTRACT/incomplete onboarding;
11. merchant support remains reachable for an ACTIVE shop in the no-plan state;
12. no merchant route or CTA introduced by this task targets `moda-interact-admin`.

Prefer behavioural tests over source-string assertions when the current test harness allows it.

## Validation

Inspect `package.json` first and use the scripts that actually exist. For the supplied baseline they are:

```bash
npm test
npm run typecheck
npm run build
npm run prisma:validate
git diff --check
```

A documented pre-existing baseline failure may be referenced only if it still exactly matches the workspace baseline and this task introduces no regression. Do not dismiss a changed/new failure as baseline.

## Acceptance criteria

The task is acceptable only if all are true:

- new shops obtain a durable, replay-safe `NO_CONTRACT` projection;
- existing subscription projections are never downgraded/reset by shop resolution;
- `/app` actually renders the existing onboarding UI for incomplete onboarding;
- no-plan onboarding does not execute unnecessary dashboard/recovery/usage queries;
- plan selection continues through Shopify-hosted pricing;
- product/usage data surfaces fail closed before plan activation;
- merchant support remains available;
- no credit grant, BillingPeriod or App Event is created merely because the app was installed;
- no merchant access to `moda-interact-admin` is introduced;
- validation shows no task-introduced regression.

## Stop conditions

STOP and return to `moda_architect` if any of the following is discovered:

- creating the initial projection requires a Prisma schema change not present in the accepted database dependency;
- the only safe implementation would overwrite an existing subscription during ordinary `resolveShopifyShop()` calls;
- Shopify framework routing prevents rendering the existing onboarding component without an architectural route change;
- enforcing no-plan route access requires a new cross-repository contract;
- a required dependency/version is unavailable;
- the task would require implementing Free/Paid activation, billing-period rollover, reinstall or another later ARCH-010 transition.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact/app/services/shop/shop.service.ts`
- `moda-interact/app/routes/app/home/route.jsx`
- `moda-interact/app/routes/app/usage/route.jsx`
- `moda-interact/app/routes/app/pending-recoveries/route.jsx`
- `moda-interact/tests/unit/services/shop.service.test.ts`
- `moda-interact/tests/unit/home-route.test.ts`
- `moda-interact/tests/unit/usage-route.test.ts`
- `moda-interact/tests/unit/pending-recoveries-route.test.ts`

### Work Completed

- Added an idempotent `Subscription` upsert keyed by `shopId` that creates only
  the accepted `NO_CONTRACT` projection and leaves existing subscription rows
  unchanged.
- Preserved the existing active shop and onboarding projection without adding
  billing periods, credit grants, purchases, or Shopify app events.
- Changed `/app` to return the minimal onboarding loader result for incomplete
  onboarding and for missing or non-active subscriptions, without dashboard,
  recovery, billing-period, or usage dataset queries.
- Kept the existing onboarding billing CTA and Shopify-hosted pricing route
  unchanged.
- Redirected `/app/usage` to `/app` unless onboarding is complete and the
  subscription is `ACTIVE` or `TRIALING`.
- Made `/app/pending-recoveries` return an empty unavailable response for
  incomplete onboarding or a non-active subscription.
- Added focused coverage for projection replay, existing `ACTIVE` and
  `TRIALING` preservation, onboarding query avoidance, usage redirects, and
  pending-recoveries fail-closed behavior.

### Validation Results

- Focused tests: passed, 4 files / 20 tests.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- `npm test`: 29 files passed, 1 skipped, 2 files failed with 3 existing
  internationalization catalogue failures for missing
  `billingCommerce.actions.manageCapacity`; no focused task test failed.
- `npm run typecheck`: non-zero with documented baseline `TYPECHECK-001` (48
  pre-existing TypeScript errors); no new task-specific error was introduced.

### Git / VCS

Implementation worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-001`

- Branch: `task/ARCH-010-SHOPIFY-001`
- Commit: `ea15631` (`fix: gate fresh installs until subscription activation`)
- Published to `origin/task/ARCH-010-SHOPIFY-001`.
- Parent task worktree:
  `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-001`
- Parent submodule gitlink was not staged or changed.

### Architect Review

Pending.

#### Attempt 1 — Changes Requested (workflow evidence only)

The implementation and focused acceptance behaviour pass architectural review.
No production or test-code correction is requested.

Architect review verified:

- `ShopService.resolveShopifyShop()` creates the fresh-install Subscription with
  `status = NO_CONTRACT`, null current/pending plan/provider/billing-period fields
  required by the task, and `cancelAtPeriodEnd = false`;
- the Subscription write is an upsert by the unique `shopId` with `update: {}`,
  so repeated merchant-route resolution is replay-safe and existing `ACTIVE`,
  `TRIALING` or other lifecycle projections are not reset by initialization;
- fresh shop resolution does not create a BillingPeriod, entitlement reservation,
  purchased-credit grant/purchase or Shopify App Event;
- the `/app` loader now builds merchant locale/time-zone context and returns the
  onboarding result before subscription/dashboard/recovery/billing-period/usage
  presentation queries when onboarding is incomplete;
- a completed-settings shop without an `ACTIVE`/`TRIALING` local projection also
  receives the existing Onboarding component rather than product/dashboard data;
- the existing Onboarding CTA still targets `/app/billing`, and the existing
  `/app/billing/select` route redirects to Shopify-hosted App Pricing;
- no `appSubscriptionCreate`, `billing.request` or
  `appPurchaseOneTimeCreate` flow was introduced;
- `/app/usage` redirects to `/app` for incomplete onboarding or a missing /
  non-`ACTIVE`/non-`TRIALING` subscription before product usage datasets are read;
- `/app/pending-recoveries` returns the existing fail-closed unavailable resource
  shape for incomplete onboarding / no-contract state without reading pending
  recoveries;
- `/app/merchant-support` remains governed by Shop execution status and does not
  require a commercial Subscription, so an `ACTIVE` no-plan merchant remains able
  to reach support;
- no merchant route or CTA changed by this task targets `moda-interact-admin`;
- focused task tests report 20 passing tests;
- `npm run build`, `npm run prisma:validate` and `git diff --check` passed;
- the three full-suite failures are internationalisation-catalogue assertions
  outside this task's changed files, while the task-focused tests pass;
- the reported TypeScript failures are documented baseline diagnostics and no
  task-focused compile/build failure is present;
- implementation commit `ea15631` is the reviewed Attempt 1 implementation head;
- the submitted handoff identifies parent review-report commit `712c374`.

One mandatory workflow-policy item remains incomplete.

##### Required correction — record full isolation/synchronization evidence

The Completion Report records the canonical implementation and parent worktree
paths, but it does not durably state the required negative-isolation assertions
and all four start-of-attempt synchronization outcomes.

On Attempt 2, using the resolver-selected canonical worktrees, record exactly:

```text
Parent worktree:
Implementation worktree:

Negative isolation assertions:
  parent is not the primary/shared workspace: yes
  implementation is not the shared repository checkout: yes

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Implementation commit:
Parent report commit:
Branches pushed:
Worktrees clean:
```

Also record the exact focused Vitest command(s) that produced the 20 passing task
tests.

This is an evidence/report-only correction.

Do **not** change the accepted SHOPIFY-001 implementation or focused tests merely to
manufacture another implementation commit. If start-of-attempt synchronization
introduces a genuine semantic conflict, stop and return that conflict to
`moda_architect`.

After synchronization, rerun:

```text
the same focused SHOPIFY-001 test command(s)
npm run build
npm run prisma:validate
git diff --check
```

The already-documented unrelated full-suite i18n and baseline TypeScript failures
may remain documented unchanged.

Return the same task to `review`.

