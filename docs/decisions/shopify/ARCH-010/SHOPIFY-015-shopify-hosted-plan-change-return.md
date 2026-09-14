---
id: ARCH-010-SHOPIFY-015
architecture_id: ARCH-010
title: Implement Shopify-hosted plan management flow and production panel
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 56
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-010-SHOPIFY-013
  - ARCH-010-SHARED-008
  - ARCH-010-BACKGROUND-010
  - ARCH-010-SHOPIFY-018
enables:
  - ARCH-010-SHOPIFY-012
created: 2026-09-11
updated: 2026-09-14
---

# ARCH-010-SHOPIFY-015: Implement Shopify-hosted plan management flow and production panel

## Consolidation

This task absorbs `ARCH-010-SHOPIFY-011`. `SHOPIFY-011` is superseded and MUST NOT be implemented separately.

The callback/selection flow and `SubscriptionChangePanel` are one merchant plan-management capability. The app owns merchant interaction and synchronous provider verification; `BACKGROUND-010` remains the only owner of effective entitlement transition.

## Objective

Productionise the complete app-owned half of upgrade/downgrade management:

```text
merchant sees current/pending Shopify subscription
  -> Manage / Change plan
  -> /app/billing/select
  -> Shopify-hosted App Pricing
  -> Shopify returns with plan_handle
  -> Moda re-queries Partner activeSubscription
  -> classify CURRENT / PENDING / MISMATCH / NO_ACTIVE / UNVERIFIED
  -> persist/schedule only safe projection state
  -> redirect to /app/billing/options
```

The panel renders Shopify-authoritative current/pending commercial facts. It performs no provider/network mutation itself.

## Inspect before editing

```text
app/routes/app/billing/select/route.jsx
app/routes/app/billing/callback/route.tsx
app/routes/app/billing/options/route.tsx
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/providers/shopify-billing.provider.ts
app/components/dashboard/SubscriptionChangePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/billing-purchase.mock.js
tests/unit/routes/billing-callback.test.ts
tests/unit/services/billing.service.test.ts
tests/unit/services/shopify-billing.provider.test.ts
tests/unit/billing-ui.test.ts
package.json
```

Read `SHOPIFY-013`, `SHOPIFY-018`, `BACKGROUND-010` and the published Shared billing contract before coding.

## Hard authority rules

1. Shopify App Pricing/Partner API is commercial subscription authority.
2. The callback URL `plan_handle` is **selection context only**; it never proves current entitlement.
3. Moda does not enumerate/invent a local commercial catalogue for this panel.
4. Moda does not infer upgrade/downgrade from local price/rank/name.
5. Moda does not call `appSubscriptionCreate`, `billing.request` or local subscription mutation APIs to perform the change.
6. The HTTP callback never opens/closes BillingPeriod and never grants/forfeits recovery capacity.
7. Effective plan transition belongs to `BACKGROUND-010` after provider evidence proves the new plan is current.
8. Purchased, lifetime-Free and promotion history are never reset by the callback.

## Callback classification

After authentication/shop resolution:

### 1. Require requested context

Require `plan_handle`. Unknown local mapping is allowed as provider context but MUST NOT be treated as activated entitlement.

### 2. Query Partner activeSubscription once through the canonical provider/read-model boundary

Do not trust existing local projection as proof when the current callback's provider verification failed.

### 3. Classify in this exact order

#### UNVERIFIED

Partner request throws/times out/throttles/malformed.

- preserve current/pending durable state;
- record/return merchant-safe verification-unavailable state;
- schedule/reuse canonical reconciliation where existing contract permits;
- do not claim plan changed.

#### NO_ACTIVE

Partner returns no live activeSubscription.

- distinguish from transport failure;
- do not manufacture current/pending plan from URL;
- preserve durable history;
- schedule immediate reconciliation if the established lifecycle requires it;
- return merchant to billing options/onboarding according to accepted local access state.

#### CURRENT

Provider current plan handle equals requested `plan_handle`.

- persist exact provider current projection through the canonical read/sync path;
- do not mutate BillingPeriod entitlement in HTTP request;
- schedule immediate deterministic reconciliation so BACKGROUND-010/rollover code owns any required transition;
- redirect `/app/billing/options?plan_change=current` (or existing equivalent explicitly tested).

#### PENDING

Provider pending update handle equals requested `plan_handle` while another current plan remains active.

- preserve current `Subscription.planId` and current BillingPeriod/counters;
- persist `pendingShopifyPlanHandle`;
- map `pendingPlanId` only if an active local BillingPlan mapping exists;
- persist exact provider effective/boundary time using current contract fields;
- set `nextReconcileAt` according to canonical pre-close/boundary schedule;
- enqueue/reuse deterministic `billing-subscription-reconcile` delayed job;
- do not grant new plan features/credits early;
- redirect `/app/billing/options?plan_change=pending` (or existing equivalent).

If the provider pending handle is unmapped locally, preserve the provider handle and fail closed for entitlement mapping. Do not substitute the requested local plan.

#### MISMATCH

Requested handle is neither provider current nor provider pending.

- do not mutate current/pending state from URL;
- do not claim success;
- redirect/render merchant-safe mismatch/verification state.

## SubscriptionChangePanel contract

Refactor the component to accept explicit provider-derived props equivalent to:

```ts
{
  merchantUi,
  current: {
    shopifyPlanHandle,
    mappedModaPlanName,
    price,
    currency,
    interval,
    cancelAtEndOfCycle,
  } | null,
  pending: {
    shopifyPlanHandle,
    mappedModaPlanName,
    price,
    currency,
    effectiveAt,
  } | null,
  providerVerificationState,
  managePlansHref,
  managePlansAvailable,
}
```

Use actual integrated SHOPIFY-013/018 types.

The component MUST:

- render Shopify current handle/commercial price/currency/interval from explicit provider props;
- use mapped Moda plan name only as decoration, never as replacement commercial truth;
- render pending provider plan/effective date distinctly;
- render `cancelAtEndOfCycle` when true without interpreting it as an effective cancellation if a pending plan update exists;
- render unmapped current Shopify plan as existing-but-unmapped;
- render no-active and verification-unavailable distinctly;
- use only supplied `managePlansHref` for the hosted change CTA;
- make no network/database/provider call;
- remove mock/local `plans[]`, price/rank upgrade/downgrade classification, console selection and mock fallback;
- expose no Admin route/link;
- use i18n for all new visible strings.

Do not label a transition "upgrade" or "downgrade" based on local rank. Generic `Change plan` is correct unless Shopify/provider evidence explicitly supplies semantics already accepted by architecture.

## Integration boundary

`SHOPIFY-012` composes this panel into `/app/billing/options`. Do not absorb the full billing-options route/purchase hub composition.

`SHOPIFY-016` later applies FROZEN/cancellation/NO_CONTRACT merchant restriction rules and direct-action guards. Do not duplicate those lifecycle-state screens here.

## Required tests

### Hosted flow/callback

1. `/app/billing/select` redirects to Shopify-hosted pricing;
2. callback requires `plan_handle`;
3. callback re-queries provider and never trusts URL alone;
4. provider failure is UNVERIFIED and preserves local state;
5. provider null is distinct from provider failure;
6. PENDING preserves current plan/period entitlement;
7. mapped pending plan stores pending id/handle/effective boundary and deterministic reconciliation;
8. unmapped pending plan preserves provider handle but maps no entitlement plan;
9. CURRENT schedules reconciliation but opens/closes no BillingPeriod in HTTP request;
10. CURRENT grants/forfeits no credits/features in HTTP request;
11. MISMATCH mutates neither current nor pending state from URL alone;
12. purchased balance/history is unchanged;
13. lifetime-Free quantities/history are unchanged;
14. no local rank/price-based upgrade/downgrade inference exists;
15. no `appSubscriptionCreate`/Billing API plan mutation is introduced;
16. redirect returns only to merchant routes, never Admin.

### Component

17. current provider handle/price/currency/interval render from explicit props;
18. mapped Moda name only decorates provider truth;
19. pending provider handle/effective date render distinctly;
20. `cancelAtEndOfCycle` renders when true;
21. unmapped current plan renders as existing-but-unmapped;
22. no-active state renders distinctly;
23. verification unavailable renders distinctly;
24. no local plans catalogue/price/rank is required;
25. no upgrade/downgrade classification is invented;
26. CTA uses supplied Shopify-hosted href;
27. component makes no local mutation/network call;
28. prototype duplicate/mock blocks/imports are removed;
29. no Admin link exists;
30. i18n catalogue parity is preserved.

## Non-goals

Do not implement effective plan-transition transaction, proration, top-up purchase, cancellation/freeze state presentation, Shopify plan catalogue enumeration, Admin plan creation or pricing management.

## Validation

Inspect `package.json`. Run focused callback/service/provider/component tests, then repository-declared full tests/typecheck/build/Prisma validation applicable to changed files and `git diff --check`. Do not invent scripts.

## Stop conditions

STOP if:

1. BACKGROUND-010 transition contract is unavailable/materially different;
2. SHOPIFY-013/018 cannot expose the provider facts needed without inventing local commercial truth;
3. implementing the flow would require local price/rank inference or a Shopify subscription-creation mutation.

Return the mismatch to `moda_architect` rather than expanding scope.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact/app/components/dashboard/SubscriptionChangePanel.jsx`
- `moda-interact/app/routes/app/billing/options/route.tsx`
- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/tests/unit/services/billing.service.test.ts`
- `moda-interact/tests/unit/subscription-change-panel.test.tsx`

### Work Completed
- Attempt 2 restored `app/routes/app/billing/options/route.tsx` exactly to parent snapshot `d3217c8e6cd49e0974a934353a3f8787e87f89f6`; SHOPIFY-012 remains the owner of that composition.
- Hosted returns now lock the accepted ShopSettings/Subscription pair before rereading, map only an exact active pending BillingPlan, preserve current entitlement/history, and leave effective transitions to BACKGROUND-010.
- The panel renders explicit provider current/pending facts, does not fabricate currency or pending interval, distinguishes unmapped/no-active/unverified state, and uses only the supplied hosted CTA.
- Added direct service and component regression evidence without changing provider, shared, background, schema, or Admin code.

### Attempt 2 Correction Mapping
- Finding 1: implemented by exact route restoration; focused `tests/unit/billing-ui.test.ts` continues to prove hosted selection and Admin exclusion.
- Finding 2: implemented by exact verified pending-handle lookup with `active: true`; `tests/unit/services/billing.service.test.ts` title `stores only an active exact pending mapping for %s provider plans` covers active, inactive, and unmapped cases.
- Finding 3: implemented by `lockInitialFreeActivationState` at transaction start; service test title `locks the accepted settings/subscription pair before rereading the hosted projection` proves lock order.
- Finding 4: implemented in `SubscriptionChangePanel.jsx`; `tests/unit/subscription-change-panel.test.tsx` covers provider facts, pending separation, cancellation, unmapped state, null currency, CTA, and no local mutation patterns.
- Finding 5: implemented with executable callback coverage in `tests/unit/routes/billing-callback.test.ts`, hosted-return service coverage in `tests/unit/services/billing.service.test.ts`, and component coverage in `tests/unit/subscription-change-panel.test.tsx`.

### Required Test Mapping
1. `redirects the selection route to Shopify pricing with a top-level target` - `tests/unit/billing-ui.test.ts`.
2. `requires plan_handle` - `tests/unit/routes/billing-callback.test.ts`.
3. `classifies provider state: %s` plus `getState`/`recordReturn` assertions - `tests/unit/routes/billing-callback.test.ts`.
4. `distinguishes no active subscription from verification failure` - `tests/unit/routes/billing-callback.test.ts`.
5. `distinguishes no active subscription from verification failure` - `tests/unit/routes/billing-callback.test.ts`.
6. `classifies provider state: %s` - `tests/unit/routes/billing-callback.test.ts`.
7. `schedules reconciliation for verified current or pending state` - `tests/unit/routes/billing-callback.test.ts`.
8. `schedules reconciliation for verified current or pending state` - `tests/unit/routes/billing-callback.test.ts`.
9. `schedules current state without changing entitlement ownership` - `tests/unit/services/billing.service.test.ts`.
10. `schedules current state without changing entitlement ownership` - `tests/unit/services/billing.service.test.ts`.
11. `does not mutate a mismatch or invent a plan when there is no active subscription` - `tests/unit/services/billing.service.test.ts`.
12. `preserves replayed period and lifetime quantities` - `tests/unit/services/billing.service.test.ts`.
13. `preserves replayed period and lifetime quantities` - `tests/unit/services/billing.service.test.ts`.
14. `contains no local catalogue, rank inference, or provider mutation` - `tests/unit/subscription-change-panel.test.tsx`.
15. `contains no local catalogue, rank inference, or provider mutation` - `tests/unit/subscription-change-panel.test.tsx`.
16. `keeps merchant billing surfaces out of the Admin application` - `tests/unit/billing-ui.test.ts`.
17. `renders provider current and pending commercial facts separately` - `tests/unit/subscription-change-panel.test.tsx`.
18. `renders provider current and pending commercial facts separately` - `tests/unit/subscription-change-panel.test.tsx`.
19. `renders provider current and pending commercial facts separately` - `tests/unit/subscription-change-panel.test.tsx`.
20. `keeps cancellation distinct from a pending provider update` - `tests/unit/subscription-change-panel.test.tsx`.
21. `renders unmapped current contracts and verification states distinctly` - `tests/unit/subscription-change-panel.test.tsx`.
22. `renders unmapped current contracts and verification states distinctly` - `tests/unit/subscription-change-panel.test.tsx`.
23. `renders unmapped current contracts and verification states distinctly` - `tests/unit/subscription-change-panel.test.tsx`.
24. `contains no local catalogue, rank inference, or provider mutation` - `tests/unit/subscription-change-panel.test.tsx`.
25. `contains no local catalogue, rank inference, or provider mutation` - `tests/unit/subscription-change-panel.test.tsx`.
26. `uses only the supplied hosted plan-management destination` - `tests/unit/subscription-change-panel.test.tsx`.
27. `contains no local catalogue, rank inference, or provider mutation` - `tests/unit/subscription-change-panel.test.tsx`.
28. Exact route restoration and component source assertion - `tests/unit/billing-ui.test.ts`, `tests/unit/subscription-change-panel.test.tsx`.
29. `uses only the supplied hosted plan-management destination` - `tests/unit/subscription-change-panel.test.tsx`.
30. `does not invent a currency when the provider omits it` - `tests/unit/subscription-change-panel.test.tsx`.
31. `defines every billing key in every locale catalogue` - `tests/unit/billing-i18n.test.ts`, `tests/unit/merchant-i18n.test.ts`.

### Validation Results
- Focused validation: 6 files, 142 passed, 15 skipped.
- Full validation: 39 files passed, 2 skipped; 384 passed, 18 skipped.
- `npm run prisma:validate` passed.
- `npm run prisma:generate` passed.
- `npm run typecheck` passed with zero diagnostics.
- `npm run build` passed; only existing bundler warnings were emitted.
- `git diff --check` passed.
- Prohibited static scan returned zero matches for local rank inference, Billing API mutation, and Admin references.

### Git / VCS
- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-015`, branch `task/ARCH-010-SHOPIFY-015`.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-015`, branch `task/ARCH-010-SHOPIFY-015`.
- Preparation synchronization merge preserved: `1ca0cb0b95e2bbeca37d33d27037521f2eb6b67c`.
- Database submodule before/after: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94` / `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`.
- Implementation branch: `task/ARCH-010-SHOPIFY-015`
- Implementation commit: `4858aabbfdbe75f307adfb60dbc52697b43d1570` (pushed to `origin`).
- Parent report commit: pending.
- No implementation submodule gitlink was staged or changed.

### Architect Review — Attempt 1

#### Status

**Changes Requested**

Attempt 1 has the correct high-level direction: the callback re-queries Shopify,
classifies provider current/pending/mismatch/no-active state, removes local rank/price
upgrade/downgrade inference from `SubscriptionChangePanel`, and leaves effective
entitlement transition to BACKGROUND-010.

It is not yet acceptable because the implementation crosses the explicit SHOPIFY-012
integration boundary, persists an inactive pending Moda mapping, presents fabricated
commercial facts in the panel, and does not provide executable service/component
evidence for the task's required invariants. The corrections below are the complete
Attempt-2 contract. Preserve the accepted provider read model from SHOPIFY-013 and the
accepted BACKGROUND-010 transition contract; do not redesign either.

#### Finding 1 — SHOPIFY-015 has absorbed SHOPIFY-012's billing-options composition

`app/routes/app/billing/options/route.tsx` is owned by `ARCH-010-SHOPIFY-012` for the
real purchase-hub/capacity/top-up/plan-management composition. Attempt 1 replaces the
prototype `BillingPurchaseHub` route with only `SubscriptionChangePanel` and removes
the existing top-up/purchase-hub surface.

That is explicitly outside this task's integration boundary and creates ordering risk:
SHOPIFY-012 still needs to compose SHOPIFY-009 capacity, SHOPIFY-014 top-up lifecycle,
SHOPIFY-007 cycle phase, and this task's finished panel.

##### Required correction

Restore:

```text
app/routes/app/billing/options/route.tsx
```

to its exact pre-SHOPIFY-015 content from implementation parent:

```text
d3217c8e6cd49e0974a934353a3f8787e87f89f6
```

Do not productionise `BillingPurchaseHub`, delete `billing-purchase.mock.js`, wire
SHOPIFY-009/014 capacity/top-up state, or otherwise perform SHOPIFY-012 work here.

The callback may continue to redirect to `/app/billing/options?...`; SHOPIFY-012 owns
how that route eventually composes and renders the completed child panel.

#### Finding 2 — pending provider state can persist an inactive Moda plan mapping

`recordHostedPlanChangeReturn(...)` currently writes:

```ts
pendingPlanId: state.pendingModaMapping?.id ?? null
```

The SHOPIFY-013 read model treats an existing `BillingPlan` row as mapping metadata and
does not prove that row is currently active. SHOPIFY-015 is stricter: for a provider
PENDING change, `pendingPlanId` may be persisted only when the exact pending Shopify
handle maps to an **active** local BillingPlan.

##### Required correction

Inside the same database transaction that persists the hosted return:

1. derive `pendingHandle` only from the verified provider snapshot;
2. when `pendingHandle != null`, query the local BillingPlan by exact
   `shopifyPlanHandle = pendingHandle` and require `active = true`;
3. persist that active row's `id` as `pendingPlanId`;
4. if no active mapping exists, persist:

```text
pendingShopifyPlanHandle = exact provider pending handle
pendingPlanId            = null
pendingEffectiveAt       = exact provider effectiveAt or null
```

5. never substitute the requested URL handle or the provider current plan's local id.

Do not change the completed SHOPIFY-013 mapping semantics globally merely to satisfy
this task.

#### Finding 3 — hosted-return persistence must serialize with Background reconciliation

`recordHostedPlanChangeReturn(...)` currently performs a normal `findUnique` followed
by an unconditional `subscription.update({ where: { shopId } })`. BACKGROUND-010 can
mutate the same Subscription projection concurrently. The HTTP callback must not race
an effective Background transition and overwrite its pending/schedule projection.

##### Required correction

At the start of the hosted-return transaction, acquire the existing accepted
Subscription row lock used by Shopify billing state mutations (preserve the repository
lock ordering; do not introduce a process-local mutex). Re-read the Subscription only
after the lock is held, then perform the hosted-return write.

For CURRENT and PENDING callback results the HTTP transaction may update only provider
observation/projection and reconciliation scheduling fields, including as applicable:

```text
observedShopifyPlanHandle
currentPeriodStart
currentPeriodEnd
trialEndsAt
cancelAtPeriodEnd
pendingShopifyPlanHandle
pendingPlanId
pendingEffectiveAt
nextReconcileAt
lastSyncedAt
lastSyncErrorCode / lastSyncErrorAt
```

It MUST NOT write or recreate:

```text
Subscription.status
Subscription.planId
Subscription.billingPeriodId
BillingPeriod
BillingPeriodEntitlementCounter
ShopEntitlementCounter
RecoveryCreditPurchase
PromotionalCreditGrant
MerchantPromotionSelection
```

MISMATCH remains a no-mutation classification. `NO_ACTIVE` must not manufacture or
clear current/pending entitlement from the callback URL. Partner failure must update
only bounded verification-error/retry metadata and preserve all current/pending
entitlement fields.

If the accepted repository lock primitive cannot be reused without changing
BACKGROUND-010 or database schema, STOP and return the exact lock-order conflict to
`moda_architect`.

#### Finding 4 — the panel fabricates provider commercial facts

Attempt 1 contains two provider-truth violations:

1. `SubscriptionChangePanel` formats a null Shopify currency using `"GBP"` as a
   fallback. A missing provider currency must never become GBP merely for display.
2. the attempted `/app/billing/options` integration supplies the **current** billing
   interval as the pending plan's interval. SHOPIFY-013 does not currently expose a
   pending interval through the accepted panel contract, so the panel must not label a
   pending update with the current plan's interval.

The panel also fails to distinguish an existing unmapped Shopify current contract from
an ordinary mapped plan clearly enough, and it does not render the pending mapped Moda
name as decoration when supplied.

##### Required correction

In `SubscriptionChangePanel.jsx`:

- never default provider currency to GBP or any other local currency;
- when provider currency is null, preserve the amount and render a localized
  unavailable/unknown currency indication, or omit currency formatting entirely; do
  not call `formatMoney` with an invented currency;
- current interval may render only from `current.interval` supplied by provider truth;
- remove `pending.interval` as a required prop unless SHOPIFY-013 genuinely supplies a
  pending interval in its accepted contract; do not copy current interval into pending;
- render pending handle/price/effective date distinctly;
- render `pending.mappedModaPlanName` only as optional decoration;
- when the current provider plan exists but `current.mappedModaPlanName == null`, keep
  the provider handle/price visible and render the localized Moda configuration-
  unavailable state rather than treating the Shopify contract as absent;
- keep `cancelAtEndOfCycle` distinct from a pending update;
- keep CTA navigation entirely driven by supplied `managePlansHref`.

Do not add a local plan catalogue, price/rank comparison, or upgrade/downgrade labels.

#### Finding 5 — the required regression contract is largely unimplemented

The report records only two focused files (`79 passed, 9 skipped`). The changed
callback test skips the legacy suite and mocks `recordHostedPlanChangeReturn`, so it
does not prove the new service persistence semantics. There is no executable
`SubscriptionChangePanel` test at all.

Attempt 2 must add permanent tests. Reuse existing tests only when they execute the
exact production method/branch and assert the exact contract.

##### A. Callback / hosted flow tests

In `tests/unit/routes/billing-callback.test.ts` and existing select-route coverage,
prove:

1. `/app/billing/select` redirects to Shopify-hosted pricing with `_top` target;
2. missing `plan_handle` returns 400 before provider verification;
3. callback calls the canonical provider-backed read exactly once and does not use URL
   context as entitlement proof;
4. provider exception calls `recordHostedPlanVerificationFailure`, redirects to
   `plan_change=unverified`, and enqueues only the exact returned durable schedule;
5. provider `null`/NO_ACTIVE is distinct from transport failure and redirects to
   `plan_change=no_active`;
6. CURRENT, PENDING and MISMATCH redirect to their exact merchant result values;
7. CURRENT/PENDING enqueue exactly the `subscriptionId` + persisted
   `expectedNextReconcileAt` returned by the service;
8. MISMATCH performs no enqueue;
9. every redirect remains under `/app/...`; no Admin route/link is introduced.

Do not keep required SHOPIFY-015 evidence only inside `describe.skip(...)`.

##### B. `BillingService.recordHostedPlanChangeReturn` tests

Add executable service tests proving:

10. PENDING preserves existing `status`, `planId`, `billingPeriodId`, current period
    entitlement and all credit/history models;
11. mapped **active** pending handle stores exact handle/id/effective time and the
    deterministic reconciliation schedule;
12. an inactive local BillingPlan for the exact pending handle stores
    `pendingPlanId = null` while preserving provider handle/effective time;
13. an unmapped pending handle behaves the same way (`pendingPlanId = null`);
14. PENDING never uses requested URL handle as the mapping authority;
15. CURRENT schedules immediate reconciliation while opening/closing no BillingPeriod
    and granting/forfeiting no capacity;
16. MISMATCH makes no Subscription mutation;
17. NO_ACTIVE schedules the accepted immediate reconciliation without manufacturing a
    current/pending plan from the URL;
18. provider verification failure preserves current plan/period/pending fields and
    changes only retry/error metadata;
19. hosted-return transaction takes the accepted Subscription lock before reading and
    writing the durable projection;
20. observable mocks prove no writes to BillingPeriod,
    BillingPeriodEntitlementCounter, ShopEntitlementCounter, RecoveryCreditPurchase,
    PromotionalCreditGrant or MerchantPromotionSelection for CURRENT/PENDING/MISMATCH.

##### C. `SubscriptionChangePanel` tests

Create a focused component test (for example
`tests/unit/subscription-change-panel.test.tsx`) using the repository's React/Vitest
stack and prove:

21. current provider handle/amount/currency/interval render from explicit props;
22. mapped current Moda name is decoration only;
23. pending provider handle/price/effective date render separately from current;
24. pending mapped Moda name is optional decoration;
25. current `cancelAtEndOfCycle=true` renders without erasing a pending update;
26. unmapped current provider contract remains visible and shows localized
    configuration-unavailable state;
27. NO_ACTIVE renders distinctly;
28. VERIFICATION_UNAVAILABLE renders distinctly;
29. supplied `managePlansHref` is the only CTA destination;
30. null provider currency does not render/fabricate GBP;
31. component source/runtime contains no local `plans[]`, rank sorting,
    upgrade/downgrade inference, console mutation, provider/network call or Admin link.

##### D. i18n parity

The current referenced static keys already exist in the 20 merchant catalogues. Keep
that parity and execute the existing billing/merchant i18n tests. If Attempt 2 adds any
new static visible string, add the exact key to all 20 catalogues in the same attempt.
Do not leave English-only fallback copy.

#### Attempt-2 allowed scope

Production files:

```text
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.service.ts
app/components/dashboard/SubscriptionChangePanel.jsx
app/routes/app/billing/options/route.tsx   # RESTORE ONLY to d3217c8... parent content
```

Test files:

```text
tests/unit/routes/billing-callback.test.ts
tests/unit/services/billing.service.test.ts
tests/unit/billing-ui.test.ts
tests/unit/billing-i18n.test.ts
tests/unit/merchant-i18n.test.ts
tests/unit/subscription-change-panel.test.tsx   # may be added
```

Do not modify in Attempt 2:

```text
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/billing-purchase.mock.js
app/services/billing/providers/shopify-billing.provider.ts
Prisma schema/migrations
Shared contracts/package version
Background services
SHOPIFY-009/012/014/016 implementation
Admin, Messaging or Gateway
```

`/app/billing/select` should remain unchanged unless a focused test exposes a defect in
its already-hosted redirect behaviour; if so, STOP and report the exact defect before
editing it.

#### Required validation for Attempt 2

From `moda-interact`, run the repository-declared commands:

```bash
npm test -- --run \
  tests/unit/routes/billing-callback.test.ts \
  tests/unit/services/billing.service.test.ts \
  tests/unit/subscription-change-panel.test.tsx \
  tests/unit/billing-ui.test.ts \
  tests/unit/billing-i18n.test.ts \
  tests/unit/merchant-i18n.test.ts

npm test
npm run prisma:validate
npm run prisma:generate
npm run typecheck
npm run build
git diff --check

rg -n "rank|isUpgrade|isDowngrade|upgradeAction|downgradeAction|appSubscriptionCreate|billing\\.request|moda-interact-admin" \
  app/components/dashboard/SubscriptionChangePanel.jsx \
  app/routes/app/billing/callback/route.tsx \
  app/services/billing/billing.service.ts
```

For `rg`, exit 1 because there are zero prohibited matches is the expected clean
result. If repository typecheck still has documented unrelated baseline diagnostics,
record the exact count and prove zero diagnostics in the Attempt-2 changed production
and test files. Report exact test pass/fail/skip totals; do not report only aggregate
"validation passed".

#### Completion Report required

Map every numbered item 1-31 above to an exact test title/file. Record:

- implementation full SHA;
- parent report full SHA;
- canonical parent and implementation worktrees/branches;
- database submodule SHA before/after;
- focused/full test counts;
- Prisma validation/generation, typecheck, build and `git diff --check` outcomes;
- zero prohibited static-scan matches;
- clean/pushed branch state.

#### Reclaim / stop condition

Return this **same task** to `/moda-task`.

The current attempt counter remains:

```text
attempt: 1
```

The next authorized claim must increment it to **Attempt 2 exactly once**.

STOP and return to `moda_architect` rather than expanding scope if any correction
requires:

- changing SHOPIFY-013's provider contract to invent a pending billing interval;
- changing BACKGROUND-010 effective-transition semantics;
- changing Prisma/Shared contracts;
- implementing SHOPIFY-012 billing-options composition or SHOPIFY-014 top-up runtime.

After corrections and validation, set `status: review`, clear claim metadata,
commit/push both task branches, and STOP for architect review.
