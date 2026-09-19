---
id: ARCH-017-SHOPIFY-002
architecture_id: ARCH-017
title: Decouple Shopify callback onboarding milestone from Moda billing reconciliation
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-017-SHOPIFY-001
enables:
- ARCH-017-SHOPIFY-003
created: 2026-09-19
updated: 2026-09-19
---

# ARCH-017-SHOPIFY-002

## Objective

Make `ShopSettings.onboardingCompleted` a one-way Shopify callback milestone that is owned exclusively by the authenticated billing callback route and is completely independent of Moda billing resolution, provider verification, mapping, materialisation, activation, reconciliation and retry outcomes.

This is a new follow-on task. Do **not** reopen or rewrite the accepted implementation history of `ARCH-017-SHOPIFY-001`.

The required invariant is:

```text
successful Shopify admin authentication
  -> resolve the authenticated shop
  -> assert the shop is ACTIVE
  -> persist ShopSettings.onboardingCompleted=true
  -> only then validate callback parameters and perform Moda billing/provider work
```

Once the callback milestone is persisted, every later Moda outcome leaves it `true`, including:

```text
missing/invalid callback parameter
provider/API failure
provider returns no active subscription
provider/current-plan mismatch
unknown catalogue plan -> UNMAPPED
invalid local catalogue/operational plan -> SYNC_ERROR
BillingPlan materialisation failure
Subscription/BillingPeriod projection failure
bounded retry scheduling
later cancellation / NO_CONTRACT / reinstall / plan change
```

`BillingService` must not read, write or branch on `onboardingCompleted` after this task.

## Dependency gate

`ARCH-017-SHOPIFY-001` is complete and is the behavioural baseline for this task.

Do not change its accepted BillingPlan resolver/materialiser, feature-preference implementation, provider mapping/error semantics, stale-token fencing model, or ARCH-010 non-prorated billing semantics except for the onboarding coupling explicitly identified below.

Before editing, ensure the implementation worktree contains the accepted database revision used by the current Shopify repository and run the repository-declared Prisma generation command.

## Read before editing

Read these files completely before making changes:

```text
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.service.ts
tests/unit/routes/billing-callback.test.ts
tests/unit/services/billing.service.test.ts
app/services/billing/billing-reconciliation.service.ts
app/services/billing/billing.types.ts
database/prisma/schema.prisma
docs/architecture/ARCH-017-billing-plan-materialisation-dynamic-features.md
docs/decisions/shopify/ARCH-017/SHOPIFY-001-lazy-billing-plan-materialisation-and-feature-preferences.md
```

The Background reconciliation service is read-only context for this task. Do not edit it.

## Authorized implementation surface

Modify production code only in:

```text
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.service.ts
```

Modify focused tests only in:

```text
tests/unit/routes/billing-callback.test.ts
tests/unit/services/billing.service.test.ts
```

The parent task Completion Report may be updated by the normal task workflow.

Do **not** modify any other application file, repository, Prisma schema/migration, package manifest, generated client, architecture document or task definition during implementation.

If the required behaviour cannot be implemented within the four files above, stop and return the concrete dependency to `moda_architect`. Do not broaden scope.

---

# Part A — callback owns the onboarding milestone

## A1. Reorder the callback entry sequence exactly

File:

```text
app/routes/app/billing/callback/route.tsx
```

The current route reads and validates `plan_handle` before resolving the shop and persists onboarding only after later provider/billing checks. Replace that ownership model.

The top of `loader()` must follow this order exactly:

```ts
export async function loader({ request }: LoaderFunctionArgs) {
  const {
    admin,
    redirect,
    session,
  } = await authenticate.admin(request);

  const shop = await shopService.resolveShopifyShop({
    admin,
    domain: session.shop,
  });
  assertActiveShop(shop, {
    route: "/app/billing/callback",
    capability: "sync-billing",
    redirectTo: "/app/merchant-support",
  });

  await persistOnboardingMilestone(shop.id);

  const url = new URL(request.url);
  const requestedPlanHandle = url.searchParams.get("plan_handle");

  if (!requestedPlanHandle) {
    throw new Response("Missing plan_handle", { status: 400 });
  }

  // Existing billing callback flow continues here.
```

Do not move `persistOnboardingMilestone()` below:

```text
plan_handle validation
prepareFreeActivation
preparePaidActivation
syncSubscription
getMerchantShopifySubscriptionState
recordHostedPlanChangeReturn
recordHostedPlanVerificationFailure
any BillingPlan resolution/materialisation
any Subscription/BillingPeriod mutation
```

Authentication, authenticated-shop resolution and the ACTIVE-shop assertion remain prerequisites. An unauthenticated request or a request for a non-active shop must not set onboarding.

## A2. Make milestone persistence idempotent and result-independent

Change:

```ts
async function persistOnboardingMilestone(shopId: string): Promise<boolean>
```

to:

```ts
async function persistOnboardingMilestone(shopId: string): Promise<void>
```

The body must remain an idempotent monotonic update:

```ts
async function persistOnboardingMilestone(shopId: string): Promise<void> {
  await db.shopSettings.updateMany({
    where: {
      shopId,
      onboardingCompleted: false,
    },
    data: {
      onboardingCompleted: true,
    },
  });
}
```

Do not inspect `updated.count` and do not use update count as a first-onboarding discriminator.

A repeated callback where onboarding is already `true` is still a valid callback and must continue through the billing flow.

## A3. Remove provider-verification ownership of onboarding

Delete the callback helper:

```ts
isManagedPricingSelectionObserved(...)
```

and remove its now-unused:

```ts
MerchantShopifySubscriptionState
```

import if no other callback code needs it.

In the activation branch, delete the entire conditional onboarding block currently equivalent to:

```ts
if (
  partnerVerificationSucceeded &&
  syncedSubscription?.providerSubscriptionId &&
  syncedSubscription.observedShopifyPlanHandle === requestedPlanHandle
) {
  await persistOnboardingMilestone(shop.id);
}
```

There must be no later callback write to `onboardingCompleted` because it has already been persisted at callback entry.

Provider verification still controls billing projection/activation. It no longer controls onboarding.

## A4. Provider failure must not affect onboarding

Keep the existing provider failure behaviour:

```text
syncSubscription throws
  -> schedule the existing bounded retry where applicable
  -> redirect using the existing flow
```

and:

```text
getMerchantShopifySubscriptionState throws
  -> recordHostedPlanVerificationFailure
  -> enqueue existing retry when returned
  -> redirect to plan_change=unverified
```

Do not convert provider failures into onboarding failures.

Because onboarding was already persisted before these calls, no catch block may revert it or write `false`.

## A5. Hosted return redirect must not depend on whether the milestone changed on this request

Delete:

```ts
const onboardingCompletedNow = ...
```

and replace the final success redirect predicate:

```ts
if (
  onboardingCompletedNow &&
  (result.result === "current" || result.result === "pending")
) {
  return redirect("/app");
}
```

with exactly:

```ts
if (result.result === "current" || result.result === "pending") {
  return redirect("/app");
}
```

Do not change the existing redirect behaviour for:

```text
mismatch
unverified
no_active
```

except that onboarding remains `true` because the authenticated callback already occurred.

---

# Part B — remove onboarding from BillingService lifecycle decisions

File:

```text
app/services/billing/billing.service.ts
```

After implementation this command must return no matches:

```bash
rg -n "onboardingCompleted" app/services/billing/billing.service.ts
```

Do not satisfy this by renaming the field or hiding it behind another helper. `BillingService` must genuinely stop reading and writing this milestone.

## B1. Token matcher

Replace the current matcher signature:

```ts
function matchesInitialFreeActivationToken(
  settings: { onboardingCompleted: boolean } | null,
  subscription: ...,
  expected: InitialFreeActivationToken,
): boolean
```

with:

```ts
function matchesInitialFreeActivationToken(
  subscription: {
    id: string;
    pendingPlanId: string | null;
    pendingShopifyPlanHandle: string | null;
    pendingEffectiveAt: Date | null;
    nextReconcileAt: Date | null;
  } | null,
  expected: InitialFreeActivationToken,
): boolean {
  return subscription?.id === expected.subscriptionId &&
    subscription.pendingPlanId === expected.pendingPlanId &&
    subscription.pendingShopifyPlanHandle === expected.pendingShopifyPlanHandle &&
    subscription.pendingEffectiveAt?.getTime() === expected.pendingEffectiveAt.getTime() &&
    subscription.nextReconcileAt?.getTime() === expected.nextReconcileAt.getTime();
}
```

Do not weaken any of the five durable token comparisons.

Update every caller to pass only `subscription` and `expected`.

## B2. `prepareFreeActivation()`

Inside the existing transaction, delete the `shopSettings.findUnique()` read used only for onboarding.

Replace:

```ts
const isInitialActivation = settings?.onboardingCompleted !== true &&
  (!currentSubscription ||
    (currentSubscription.status === SubscriptionProjectionStatus.NO_CONTRACT &&
      currentSubscription.planId === null &&
      !currentSubscription.observedShopifyPlanHandle));
```

with exactly:

```ts
const isInitialActivation = !currentSubscription ||
  (currentSubscription.status === SubscriptionProjectionStatus.NO_CONTRACT &&
    currentSubscription.planId === null &&
    !currentSubscription.observedShopifyPlanHandle);
```

Preserve `isVerifiedReplay` exactly.

Do not change the pending-token fields written by this method.

## B3. `preparePaidActivation()`

Delete the `shopSettings.findUnique()` onboarding read.

Replace the initial-activation predicate with exactly:

```ts
const isInitialActivation = !currentSubscription ||
  (currentSubscription.status === SubscriptionProjectionStatus.NO_CONTRACT &&
    currentSubscription.planId === null &&
    !currentSubscription.observedShopifyPlanHandle);
```

Do not add verified-replay behaviour to Paid as part of this task.

Do not change the pending-token fields.

## B4. `scheduleInitialFreeReconciliationIfCurrent()`

Delete the `shopSettings.findUnique()` onboarding read.

Retain the Subscription read and change:

```ts
matchesInitialFreeActivationToken(settings, subscription, expected)
```

to:

```ts
matchesInitialFreeActivationToken(subscription, expected)
```

The stale-token behaviour remains exactly the same except that changing onboarding state no longer invalidates a token.

## B5. `completeFreeActivation()`

Delete the `shopSettings.findUnique()` onboarding read.

Delete this write entirely:

```ts
await transaction.shopSettings.update({
  where: { shopId },
  data: { onboardingCompleted: true },
});
```

Replace the current onboarding-dependent pending-selection guard with:

```ts
const hasPendingSelection =
  subscription.pendingShopifyPlanHandle !== null ||
  subscription.pendingPlanId !== null ||
  subscription.pendingEffectiveAt !== null;

if (
  hasPendingSelection &&
  (
    subscription.pendingShopifyPlanHandle !== requestedPlanHandle ||
    subscription.pendingPlanId !== subscription.planId ||
    !subscription.pendingEffectiveAt
  )
) {
  return null;
}
```

This means:

```text
verified replay with no pending selection -> allowed
current initial Free selection still pending exactly -> allowed
newer/different pending selection -> rejected
```

Do not change the existing plan/status/provider verification guard above this block.

Do not change the existing completion scheduling logic below this block.

## B6. `syncSubscription()` — provider-null branch

In the provider-null transaction:

1. delete the `shopSettings.findUnique()` onboarding read;
2. add `planId: true` to the existing Subscription `select` if it is not already selected;
3. update the token call to:

```ts
matchesInitialFreeActivationToken(current, expectedInitialSelection)
```

4. replace the onboarding-dependent `preserveInitialIntent` with exactly:

```ts
const preserveInitialIntent = Boolean(
  current &&
  current.status === SubscriptionProjectionStatus.NO_CONTRACT &&
  current.planId === null &&
  !current.observedShopifyPlanHandle &&
  current.pendingShopifyPlanHandle &&
  current.pendingPlanId &&
  current.pendingEffectiveAt &&
  current.nextReconcileAt
);
```

Preserve the existing NO_CONTRACT projection and all existing active-subscription cancellation/lifecycle behaviour.

Do not clear the initial pending token merely because onboarding is true.

## B7. `syncSubscription()` — provider-active branch

Inside the provider-active transaction:

1. delete the `shopSettings.findUnique()` onboarding read;
2. update the stale-token check to:

```ts
if (
  expectedInitialSelection &&
  !matchesInitialFreeActivationToken(existingSubscription, expectedInitialSelection)
) {
  return null;
}
```

3. replace `initialPaidActivation` with exactly:

```ts
const initialPaidActivation = Boolean(
  expectedInitialSelection &&
  existingSubscription?.planId === null &&
  !existingSubscription.observedShopifyPlanHandle &&
  expectedInitialSelection.planKind === BillingPlanKind.PAID_METERED &&
  providerSubscription.planHandle === expectedInitialSelection.pendingShopifyPlanHandle
);
```

4. inside the successful initial Paid activation branch, delete:

```ts
await transaction.shopSettings.update({
  where: { shopId },
  data: { onboardingCompleted: true },
});
```

5. replace the later onboarding-dependent `preserveInitialIntent` with exactly:

```ts
const preserveInitialIntent = Boolean(
  existingSubscription &&
  existingSubscription.status === SubscriptionProjectionStatus.NO_CONTRACT &&
  existingSubscription.planId === null &&
  !existingSubscription.observedShopifyPlanHandle &&
  existingSubscription.pendingShopifyPlanHandle &&
  existingSubscription.pendingPlanId &&
  existingSubscription.pendingEffectiveAt &&
  existingSubscription.nextReconcileAt
);
```

Do not otherwise change:

```text
initial Paid exact-plan validation
usage-meter validation
BillingPeriod creation
included allowance/counter creation
UNMAPPED/SYNC_ERROR projection
pending provider update projection
nextReconcileAt calculation
established plan-change behaviour
```

---

# Part C — focused deterministic regression tests

## C1. Callback tests

File:

```text
tests/unit/routes/billing-callback.test.ts
```

Update existing tests rather than adding a parallel callback test harness.

### Test 1 — milestone precedes initial Free billing work

Replace the meaning of the existing test named approximately:

```text
completes onboarding only after current Free verification
```

with:

```text
persists onboarding before initial Free billing work
```

Required assertions:

```ts
expect(mocks.updateShopSettings).toHaveBeenCalledWith({
  where: { shopId: "shop-1", onboardingCompleted: false },
  data: { onboardingCompleted: true },
});
expect(mocks.updateShopSettings).toHaveBeenCalledBefore(mocks.prepareFreeActivation);
expect(mocks.updateShopSettings).toHaveBeenCalledBefore(mocks.syncSubscription);
```

Keep the successful Free activation assertions.

### Test 2 — initial Paid Partner failure still has onboarding complete

Use the existing `keeps a Paid Partner failure on the existing bounded retry path` case.

Add assertions that:

```text
updateShopSettings was called exactly once
updateShopSettings occurred before preparePaidActivation/syncSubscription
retry scheduling still occurs
```

Do not require provider success.

### Test 3 — hosted provider verification failure still has onboarding complete

Use the existing hosted callback failure test where `getMerchantShopifySubscriptionState` rejects.

Assert:

```text
onboarding update was called before getMerchantShopifySubscriptionState
recordHostedPlanVerificationFailure still runs
existing retry enqueue behaviour is preserved
redirect remains plan_change=unverified
```

### Test 4 — provider mismatch no longer suppresses onboarding

The current test named approximately:

```text
does not persist onboarding from a mismatched provider selection
```

must be inverted.

Rename it to express the new invariant, for example:

```text
keeps onboarding complete when provider selection mismatches the requested handle
```

Assert onboarding update occurred, while preserving the existing mismatch billing result/redirect assertions.

### Test 5 — missing `plan_handle`

The existing missing-plan-handle test must now prove:

```text
authentication succeeds
shop resolves and is ACTIVE
onboarding update occurs
then loader throws 400 Missing plan_handle
prepareFreeActivation is not called
preparePaidActivation is not called
provider verification is not called
```

This is intentional. Missing Moda callback metadata does not undo the Shopify onboarding milestone.

### Test 6 — repeated callback

Set the mocked onboarding update result to `{ count: 0 }` to represent an already-completed milestone.

For a hosted result of `current` or `pending`, assert the callback still redirects to:

```text
/app
```

Do not use update count to choose the redirect.

## C2. BillingService tests

File:

```text
tests/unit/services/billing.service.test.ts
```

Use the existing database fixtures. Do not create a second fake BillingService implementation.

Add/update focused cases proving:

### Test 1 — Free preparation ignores onboarding milestone

For otherwise identical fresh/NO_CONTRACT state, run with:

```text
onboardingCompleted=false
onboardingCompleted=true
```

and assert `prepareFreeActivation()` returns the same INITIAL activation/token shape in both cases.

### Test 2 — Paid preparation ignores onboarding milestone

Do the same for `preparePaidActivation()`.

### Test 3 — onboarding transition does not stale an initial token

Create an initial token, change only fixture `onboardingCompleted` from false to true, leave all Subscription token fields unchanged, then call a token-guarded path such as:

```text
scheduleInitialFreeReconciliationIfCurrent
```

Assert the current token remains valid and the update occurs.

### Test 4 — durable token change still stales the token

Retain the existing stale-token tests where one of these changes:

```text
subscription id
pendingPlanId
pendingShopifyPlanHandle
pendingEffectiveAt
nextReconcileAt
```

They must still reject/no-op.

### Test 5 — Free completion protects newer pending selection independent of onboarding

For a verified current Free projection with a newer/different pending selection, assert `completeFreeActivation()` returns `null` for both onboarding values.

For a verified replay with all pending fields null, assert completion remains allowed.

### Test 6 — provider-null preserves initial intent when onboarding=true

With a valid initial pending token and `onboardingCompleted=true`, make the provider return null and assert the pending plan identity/effective/reconcile token is preserved in the NO_CONTRACT projection.

### Test 7 — initial Paid activation works when onboarding=true

With a current valid initial Paid token, matching provider plan, valid usage meter and `onboardingCompleted=true`, assert the canonical initial Paid activation still creates/projects the same plan/period/allowance state as the existing false-onboarding case.

## C3. Source-level invariant

Run:

```bash
rg -n "onboardingCompleted" app/services/billing/billing.service.ts
```

Expected result:

```text
no output
exit status 1 from rg because there are no matches
```

Record this explicitly in the Completion Report as a PASS condition. Do not treat `rg` exit status 1 as a command failure for this specific assertion.

---

# Validation

Run from the `moda-interact` implementation worktree.

Before the first Node command, follow the workspace Node bootstrap policy.

Run exactly:

```bash
npm run prisma:generate
npm run prisma:validate

npx vitest run \
  tests/unit/routes/billing-callback.test.ts \
  tests/unit/services/billing.service.test.ts

npm run typecheck
npm run build

npx eslint \
  app/routes/app/billing/callback/route.tsx \
  app/services/billing/billing.service.ts \
  tests/unit/routes/billing-callback.test.ts \
  tests/unit/services/billing.service.test.ts

npm test

git diff --check
```

Then run the source invariant separately:

```bash
if rg -n "onboardingCompleted" app/services/billing/billing.service.ts; then
  echo "FAIL: BillingService still depends on onboardingCompleted" >&2
  exit 1
else
  echo "PASS: BillingService has no onboardingCompleted dependency"
fi
```

Do not repair unrelated repository baseline failures. If an unchanged documented baseline failure occurs, identify the baseline ID and prove the changed files introduced no new failure.

Any failure originating in one of the four authorized files is blocking.

---

# Acceptance criteria

All of the following must be true:

1. Successful Shopify admin authentication + authenticated ACTIVE-shop resolution reaches `persistOnboardingMilestone(shop.id)` before callback parameter validation or billing/provider work.
2. Missing `plan_handle` after that point returns 400 but leaves onboarding complete.
3. Provider/API verification failure cannot prevent or revert onboarding completion.
4. Provider mismatch cannot prevent or revert onboarding completion.
5. `persistOnboardingMilestone()` is idempotent and its update count does not control redirect behaviour.
6. Repeated callbacks with onboarding already true still process normally.
7. `BillingService` contains no `onboardingCompleted` read, write or branch.
8. Free/Paid initial activation eligibility is derived from durable Subscription state only.
9. Initial activation tokens remain fenced by exact durable Subscription token fields.
10. Changing only onboarding from false to true cannot make a valid current initial token stale.
11. Changing any durable token field still makes the token stale.
12. Initial provider-null projection preserves valid pending intent independent of onboarding.
13. Matching initial Paid activation still uses the existing canonical initial Paid path.
14. Newer/different pending Free selection remains protected from stale completion.
15. No ARCH-011 proration or same-cycle segmentation is introduced.
16. No changes are made outside the authorized four implementation/test files.

The final behavioural invariant is:

```text
Holding authenticated shop identity, Subscription state and provider truth constant,
changing ShopSettings.onboardingCompleted from false to true must not change any
BillingService decision or billing lifecycle result.
```

and:

```text
Once the authenticated ACTIVE-shop billing callback is entered,
subsequent Moda billing/provider failures must not change onboardingCompleted back
to false or prevent the callback milestone from being persisted.
```

---

# Non-goals

Do not:

```text
reopen ARCH-017-SHOPIFY-001
change BillingPlan resolver/materialiser behaviour
change MerchantPricingPlan/BillingPlan identity rules
change feature preferences or /app/features
change Admin functionality
change Background reconciliation
change Prisma schema or migrations
change Shopify managed-pricing configuration
add proration or ARCH-011 behaviour
change usage-meter semantics
redesign hosted plan-change state machinery
introduce a new callback state/correlation mechanism
change route authentication
```

If a future requirement needs cryptographic proof that Shopify, rather than an authenticated merchant manually entering the route URL, initiated the callback, that is a separate architecture task. This task intentionally defines the authenticated ACTIVE-shop callback entry as the onboarding milestone.

---

# Stop conditions

Stop and return to `moda_architect` without speculative changes if any of these occurs:

1. callback milestone persistence cannot occur before billing/provider work without changing authentication or shop-resolution contracts;
2. removing onboarding from `BillingService` requires a database schema change;
3. stale-token safety cannot be preserved using the existing durable Subscription token fields;
4. initial Paid activation would require changing BillingPeriod/proration semantics;
5. a required fix needs a production-file edit outside the two authorized production files;
6. the current implementation differs materially from the code shapes named in this task because another merged task changed the same lifecycle.

Do not broaden the task to solve those conditions.

---

# Completion Report

Repository agent MUST append a Completion Report containing at minimum:

```text
Attempt: <N>
Implementation commit: <sha>
Database revision: <sha>
Focused callback/billing tests: <result>
Full test suite: <result>
Prisma generate: PASS/FAIL
Prisma validate: PASS/FAIL
Typecheck: PASS/FAIL
Build: PASS/FAIL
Changed-file lint: PASS/FAIL
git diff --check: PASS/FAIL
BillingService onboarding source invariant: PASS/FAIL
```

The report MUST also state explicitly:

```text
Callback milestone is persisted before plan_handle validation.
Callback milestone is persisted before any provider/billing operation.
Provider failure does not affect onboarding completion.
Provider mismatch does not affect onboarding completion.
BillingService contains zero onboardingCompleted references.
Token freshness is determined only by durable Subscription token fields.
```

Include launcher-prepared parent/implementation worktree isolation and synchronization evidence required by the repository workflow.

Set task status to `review`; do not self-accept.

# Architect Review

Pending `moda_architect` review.
