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
status: complete
priority: 56
executor: null
claimed_at: null
attempt: 5
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
- Attempt 4 production: `app/routes/app/billing/callback/route.tsx`, `app/services/billing/billing.service.ts`.
- Attempt 4 tests: `tests/unit/routes/billing-callback.test.ts`, `tests/unit/services/billing.service.test.ts`.
- Accepted prior-attempt files remain unchanged: `app/components/dashboard/SubscriptionChangePanel.jsx`, `app/routes/app/billing/options/route.tsx`, and `tests/unit/subscription-change-panel.test.tsx`.

### Work Completed
- Attempt 4 replaces the wall-clock `verificationStartedAt` check with one immutable durable projection fence captured immediately before the single Partner read; the locked projection is compared field-for-field, including exact nullable dates, before any mapping or write.
- Verified CURRENT/PENDING projections now persist provider `currentPeriodStart`, `currentPeriodEnd`, and `trialEndsAt` as exact nullable values, including clearing stale local facts.
- Attempt 4 preserves the accepted active-only pending mapping, lock ordering, callback activation suite, protected-model no-write contract, hosted route composition boundary, provider commercial truth, and callback enqueue restrictions.
- No schema, shared contract, background, provider, Admin, or SHOPIFY-012 implementation was changed.

### Attempt 4 Correction Mapping
- Review Finding 1, durable commit-order fence: `app/services/billing/billing.service.ts` adds `HostedPlanVerificationFence`, the pre-provider reader, complete projection equality, and locked re-read; `app/routes/app/billing/callback/route.tsx` passes the same object to success/failure persistence. Tests in `tests/unit/routes/billing-callback.test.ts`: `captures the durable hosted verification fence before the Partner read`, `passes the same durable hosted verification fence to provider failure recording`, and `does not enqueue a freshness-fenced unverified result`. Service tests in `tests/unit/services/billing.service.test.ts`: `fences a durable commit that is newer than the pre-provider projection even when its updatedAt is earlier than the old wall-clock start`, `fences a changed durable projection even when updatedAt is identical`, and `does not record provider failure when the durable projection changed during verification`.
- Review Finding 2, exact nullable provider projection: `app/services/billing/billing.service.ts` writes provider cycle/trial facts as `Date | null`; `tests/unit/services/billing.service.test.ts` adds `clears stale nullable provider cycle and trial facts from a verified hosted observation`.
- Protected no-write and preservation evidence remains in `tests/unit/services/billing.service.test.ts`: `stores only an active exact pending mapping for %s provider plans`, `locks the accepted settings/subscription pair before rereading the hosted projection`, `schedules current state without changing entitlement ownership`, `does not mutate a mismatch or invent a plan when there is no active subscription`, `updates only retry metadata when provider verification fails`, plus the three durable-fence tests above. The fixture covers BillingPeriod, BillingPeriodEntitlementCounter, ShopEntitlementCounter, RecoveryCreditPurchase, RecoveryCreditRefund, PromotionalCreditGrant, and MerchantPromotionSelection write methods.

### Required Test Mapping
- Callback durable-fence propagation: `captures the durable hosted verification fence before the Partner read`, `passes the same durable hosted verification fence to provider failure recording`, `does not enqueue a freshness-fenced unverified result`, and `distinguishes no active subscription from verification failure` - `tests/unit/routes/billing-callback.test.ts`.
- Hosted-return persistence and protected no-write evidence: `stores only an active exact pending mapping for %s provider plans`, `locks the accepted settings/subscription pair before rereading the hosted projection`, `schedules current state without changing entitlement ownership`, `does not mutate a mismatch or invent a plan when there is no active subscription`, and `updates only retry metadata when provider verification fails` - `tests/unit/services/billing.service.test.ts`.
- Durable-fence tests: `fences a durable commit that is newer than the pre-provider projection even when its updatedAt is earlier than the old wall-clock start`, `fences a changed durable projection even when updatedAt is identical`, and `does not record provider failure when the durable projection changed during verification` - `tests/unit/services/billing.service.test.ts`.
- Nullable projection test: `clears stale nullable provider cycle and trial facts from a verified hosted observation` - `tests/unit/services/billing.service.test.ts`.
- Accepted panel, selection, and i18n coverage remains in `tests/unit/subscription-change-panel.test.tsx`, `tests/unit/billing-ui.test.ts`, `tests/unit/billing-i18n.test.ts`, and `tests/unit/merchant-i18n.test.ts`.

### Validation Results
- Focused command passed: 6 files, 191 tests passed, 0 failed, 0 skipped.
- `npm test` passed: 39 files passed, 2 skipped; 433 tests passed, 3 skipped, 0 failed.
- `npm run prisma:validate` passed; `npm run prisma:generate` passed.
- `npm run typecheck` reproduced baseline `TYPECHECK-001`: 151 errors in 23 files. Existing changed-file baseline diagnostics remain at `app/services/billing/billing.service.ts:1270` and `tests/unit/services/billing.service.test.ts:1290`; no new Attempt 4 diagnostic was introduced.
- `npm run build` passed; only existing Zod/Rollup, unresolved Prisma browser import, empty chunk, chunk-size, and unused React import warnings were emitted.
- `git diff --check` passed.
- Callback skip scan exited 1 with zero matches for `describe.skip`, `it.skip`, `test.skip`.
- Prohibited production scan exited 1 with zero matches for `verificationStartedAt`, local rank/upgrade inference, Billing API mutation, or Admin references.

### Git / VCS
- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-015`, branch `task/ARCH-010-SHOPIFY-015`.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-015`, branch `task/ARCH-010-SHOPIFY-015`.
- Attempt 3 implementation SHA: `69c79a6214dd74521453456724c63092bf369230`.
- Attempt 3 final parent/report SHA: `7bd791e4662c2d554ebbcaf40cbc93dce9a2920e`.
- Attempt 4 launcher claim SHA: `c481e7ad8b83823536b6ef1566259c2250bf6404`.
- Attempt 4 implementation SHA: `aeceed5cb1aa6bd0c9e20bced0130171305a3fa9` (pushed; remote matches).
- Preparation synchronization merge: `1ca0cb0b95e2bbeca37d33d27037521f2eb6b67c`.
- Database submodule before/after: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94` / `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`.
- Parent report publication SHA: `7fa80f3c3428ad36540ee51f2946e67f0c60bbf0` (initial Attempt 4 report publication; this metadata-only SHA update follows it); no implementation submodule gitlink is staged or changed.
- Baseline evidence: implementation worktree is clean and remote-matching before this report edit; parent branch remains the dedicated mirrored task branch.

### Attempt 5 Completion Addendum

#### Status

Ready for Review.

#### Work Completed

- Corrected `getHostedPlanVerificationFence` to return the actual nullable Subscription projection rather than manufacturing an all-null fence object.
- Updated hosted-return success and provider-failure persistence contracts to accept `HostedPlanVerificationFence | null`; unchanged absent rows now classify `NO_ACTIVE_SUBSCRIPTION` as `{ result: "no_active", subscriptionId: null, nextReconcileAt: null }` without mapping lookup or writes, and provider failure returns `null` without manufacturing retry metadata.
- Preserved the present-row field-by-field durable fence comparison and all accepted CURRENT/PENDING/MISMATCH, protected-model no-write, activation, panel, options, provider, and background boundaries.

#### Changed Files

- Implementation: `app/services/billing/billing.service.ts`.
- Tests: `tests/unit/services/billing.service.test.ts`, `tests/unit/routes/billing-callback.test.ts`.
- No other implementation files, schemas, shared contracts, background services, or parent files were changed.

#### Attempt 5 Correction Mapping

- Null fence reader: `returns null hosted verification fence when no durable Subscription exists` in `tests/unit/services/billing.service.test.ts`; asserts the reader returns `null` for an absent row.
- Absent-row NO_ACTIVE: `classifies unchanged absent durable Subscription as no_active` in `tests/unit/services/billing.service.test.ts`; asserts the exact result, no BillingPlan lookup, no Subscription mutation, and no protected-model writes.
- Absent-row provider failure: `does not manufacture retry metadata when durable Subscription is absent` in `tests/unit/services/billing.service.test.ts`; asserts `null` and zero Subscription/protected-model writes.
- Nullable callback propagation: `passes an absent durable verification fence unchanged through hosted NO_ACTIVE verification` and `passes an absent durable verification fence unchanged to failure recording` in `tests/unit/routes/billing-callback.test.ts`; assert ordering, one Partner read, exact `null` propagation, no stale enqueue for NO_ACTIVE, and the merchant-safe redirect/error path.

#### Validation Results

- Focused command passed: 6 files, 196 tests passed, 0 failed, 0 skipped.
- `npm test` passed: 39 files passed, 2 skipped; 438 tests passed, 3 skipped, 0 failed.
- `npm run prisma:validate` passed; `npm run prisma:generate` passed.
- `npm run build` passed; existing Zod/Rollup, unresolved Prisma browser import, empty chunk, chunk-size, and unused React import warnings remain.
- `npm run typecheck` reports 151 errors in 23 files, matching `TYPECHECK-001`; changed-file baseline diagnostics remain at `app/services/billing/billing.service.ts:1253` and `tests/unit/services/billing.service.test.ts:1290`, with no new Attempt 5 diagnostic in the changed callback route or null-fence lines.
- Callback skip scan exited 1 with zero matches for `describe.skip`, `it.skip`, or `test.skip`.
- Prohibited production scan exited 1 with zero matches for `verificationStartedAt`, local rank/upgrade inference, Billing API mutation, or Admin references.
- `git diff --check` passed.

#### Git / VCS

- Implementation commit and remote task branch: `0fad89ce76d59d954a0bd8894d527eaadda478b1` on `task/ARCH-010-SHOPIFY-015`.
- Parent preparation/previous report handoff: `db6574f1afaef0089c99f98f9804bfe6ef66d903`; Attempt 4 final report publication: `4f2abd4d138e1882b9da560e6d27615e9d4c6a50`.
- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-015`; canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-015`; both use `task/ARCH-010-SHOPIFY-015`.
- Launcher claim commit: `bf32268f965829470459d28512222962e3faedb5`; preparation synchronization merge: `1ca0cb0b95e2bbeca37d33d27037521f2eb6b67c`.
- Database submodule before/after: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94` / `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`.
- Implementation branch is pushed and clean; no implementation submodule gitlink was staged or changed. Attempt 5 initial parent/report publication: `693a9817bbc572747e7b04897dc276400790a7d9`; the final parent report publication is this metadata-only follow-up.

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


### Architect Review — Attempt 2

#### Status

**Changes Requested**

Attempt 2 correctly resolves the five defects called out in the Attempt-1 review:

- `app/routes/app/billing/options/route.tsx` is restored to the pre-SHOPIFY-015 parent, preserving SHOPIFY-012 ownership;
- pending provider handles map only to an exact active local `BillingPlan`;
- hosted-return and verification-failure writes use the accepted ShopSettings -> Subscription lock order;
- `SubscriptionChangePanel` no longer invents GBP or a pending interval and renders provider/mapping state separately;
- direct hosted-return and component tests now exist and the reported focused/full/typecheck/build validation is green.

Preserve all of that work. Attempt 3 is narrow. There is one remaining runtime concurrency defect and one synchronization/test-regression that must be corrected before this task can complete.

#### Finding 1 — a pre-lock provider snapshot can overwrite a newer BACKGROUND-010 projection

The callback currently performs this order:

```text
getMerchantShopifySubscriptionState(shopId)   # Partner observation
  -> recordHostedPlanChangeReturn(...)
       -> begin DB transaction
       -> lock ShopSettings + Subscription
       -> write the earlier Partner observation
```

The row lock prevents simultaneous local writes, but it does **not** make the already-acquired provider snapshot fresh.

A concrete failing interleaving is:

```text
T0 callback reads Shopify:
     current = Growth
     pending = Starter
     effectiveAt = boundary

T1 BACKGROUND-010 reaches/proves the boundary, acquires the same Subscription lock,
   commits Starter as the effective current plan, clears the pending transition and
   writes the newer Subscription projection.

T2 callback acquires the lock after BACKGROUND-010 and writes its older T0 snapshot:
     observedShopifyPlanHandle = Growth
     currentPeriodStart/End     = old Growth cycle
     pendingShopifyPlanHandle   = Starter
     pendingPlanId              = Starter
     nextReconcileAt            = old boundary
```

`planId`/`billingPeriodId` remain the newer Background values, so the row becomes internally inconsistent. The immediate queue hint may later repair it, but queue publication is best-effort and the HTTP path must not regress a newer durable projection in the first place.

The same race exists for Partner failure: a callback Partner request may fail, BACKGROUND-010 may successfully synchronize while that request is in flight, and `recordHostedPlanVerificationFailure()` can then overwrite the newer success metadata with `PARTNER_API_ERROR` and a one-minute schedule.

##### Required Attempt-3 correction

Use the existing `Subscription.updatedAt` as the local freshness fence. Do **not** add schema, Shared or Background changes and do **not** hold a database row lock across a Partner network request.

In `app/routes/app/billing/callback/route.tsx`:

1. immediately before starting the hosted-flow Partner read, capture exactly one timestamp, for example:

   ```ts
   const verificationStartedAt = new Date();
   ```

2. call `getMerchantShopifySubscriptionState(shop.id)` exactly once as today;
3. on success, pass that same `verificationStartedAt` into `recordHostedPlanChangeReturn(...)`;
4. on Partner exception, pass that same `verificationStartedAt` into `recordHostedPlanVerificationFailure(...)`;
5. do not re-query Partner and do not move the Partner call inside the DB transaction.

In `BillingService.recordHostedPlanChangeReturn(...)`:

1. keep the accepted ShopSettings -> Subscription lock order;
2. after the lock, re-read the Subscription and include at least:

   ```text
   id
   updatedAt
   status
   observedShopifyPlanHandle
   planId
   billingPeriodId
   pendingShopifyPlanHandle
   pendingPlanId
   pendingEffectiveAt
   nextReconcileAt
   ```

3. before any BillingPlan lookup or Subscription write, compare the locked row with the provider-read fence;
4. if:

   ```text
   current.updatedAt > verificationStartedAt
   ```

   treat the provider snapshot as superseded by newer durable reconciliation state:

   - perform **zero** Subscription writes;
   - perform zero BillingPlan mapping writes/lookups needed only for the stale snapshot;
   - perform zero BillingPeriod/counter/credit/promotion/history writes;
   - return `result: "unverified"` with the existing subscription id and no newly-created schedule;
   - do not rewrite `observedShopifyPlanHandle`, period timestamps, pending fields, error fields or `lastSyncedAt` from the stale snapshot.

5. when the row has not changed since the provider read began, preserve the current Attempt-2 CURRENT/PENDING/MISMATCH/NO_ACTIVE behavior.

Use strict `>` for the timestamp fence. Do not manufacture an ordering from provider timestamps that are not present in the accepted SHOPIFY-013 contract.

In `recordHostedPlanVerificationFailure(...)`:

1. accept the same `verificationStartedAt`;
2. acquire the same accepted locks;
3. re-read `Subscription.updatedAt` before writing failure metadata;
4. if the row is newer than the failed provider-read start, return `null` and write **nothing**;
5. otherwise preserve the current bounded `PARTNER_API_ERROR` + retry scheduling behavior.

In the callback enqueue condition, enqueue the return schedule only for classifications that actually created/reused a reconciliation schedule from this observation (`current`, `pending`, and `no_active`). A freshness-fenced `unverified` result must not publish a stale queue hint.

This is a freshness/CAS guard only. Do not change BACKGROUND-010 transition semantics, plan-change effective-time rules, Shopify authority or the result URLs.

#### Finding 2 — the synchronization merge disabled the accepted SHOPIFY-003 callback regression suite

The synchronized implementation correctly preserves the accepted first-install/first-Paid callback code, but `tests/unit/routes/billing-callback.test.ts` currently contains:

```ts
describe.skip("legacy billing callback activation", ...)
```

Those tests are not legacy. They are the permanent accepted regression evidence from SHOPIFY-003, including first Free activation, first Paid activation, paid provider-null/Partner-failure retry behavior, unsupported Paid trials, fail-closed configuration errors and stale-selection behavior.

The accepted SHOPIFY-003 commit `c84a3612680a048f81f3c042c1aaab8a5ac986be` had this suite enabled as:

```ts
describe("billing callback activation", ...)
```

and its `beforeEach` defaulted `prepareFreeActivation` to the initial Free activation token. The SHOPIFY-015 hosted-flow setup changed that default to `null`, which is why simply removing `.skip` is not sufficient.

##### Required Attempt-3 correction

In `tests/unit/routes/billing-callback.test.ts`:

1. restore the accepted SHOPIFY-003 activation suite to executable `describe(...)`;
2. preserve all accepted SHOPIFY-003 test cases; do not delete or weaken them;
3. restore the activation-suite default setup required by those tests (the accepted default Free activation token/plan behavior);
4. add a nested `beforeEach` inside the hosted-plan-change `describe(...)` that explicitly sets both:

   ```text
   prepareFreeActivation -> null
   preparePaidActivation -> null
   ```

   so hosted-flow tests deterministically enter the SHOPIFY-015 branch;
5. there must be no `describe.skip`/`it.skip`/`test.skip` covering the callback activation or hosted-return contracts;
6. record the new focused/full pass/skip totals. Do not count the 15 disabled SHOPIFY-003 tests as acceptable skipped coverage.

#### Finding 3 — hosted-return preservation evidence is still too indirect

The Attempt-2 Completion Report maps some hosted-return preservation requirements to the older SHOPIFY-003 test `preserves replayed period and lifetime quantities`. That test exercises first-Paid activation, not `recordHostedPlanChangeReturn(...)`.

The hosted-return test fixture also omits the protected model delegates, so it cannot prove the Attempt-1 requirement that CURRENT/PENDING/MISMATCH perform zero writes to:

```text
BillingPeriod
BillingPeriodEntitlementCounter
ShopEntitlementCounter
RecoveryCreditPurchase
PromotionalCreditGrant
MerchantPromotionSelection
```

##### Required Attempt-3 evidence

Extend the **hosted-return** service fixture itself with observable write spies for the protected delegates. At minimum expose/spies for the write methods that production code could call (`create`, `createMany`, `update`, `updateMany`, `upsert`, `delete`, `deleteMany` as applicable to the mock delegate).

Add/strengthen executable tests proving:

1. PENDING preserves existing `status`, `planId`, `billingPeriodId`, current entitlement identity and performs zero protected-model writes;
2. CURRENT preserves `status`, `planId`, `billingPeriodId` and performs zero protected-model writes;
3. MISMATCH performs zero Subscription writes and zero protected-model writes;
4. NO_ACTIVE changes only the accepted reconciliation/error scheduling fields and performs zero protected-model writes;
5. Partner verification failure changes only retry/error metadata when the freshness fence permits it and performs zero protected-model writes;
6. stale **successful** provider observation (`Subscription.updatedAt > verificationStartedAt`) returns `unverified`, performs zero Subscription/protected-model writes and preserves the newer durable current/pending projection;
7. stale **failed** provider observation performs zero Subscription/protected-model writes and returns no new retry schedule;
8. callback success passes the provider-read fence into `recordHostedPlanChangeReturn`;
9. callback failure passes the same provider-read fence into `recordHostedPlanVerificationFailure`;
10. freshness-fenced `unverified` callback result does not enqueue reconciliation.

The Completion Report must map these tests to their exact titles. Do not use unrelated SHOPIFY-003 activation tests as evidence for hosted-return no-write behavior.

#### Accepted Attempt-2 work — do not churn

Unless one of the focused tests exposes a direct defect, do **not** change:

```text
app/routes/app/billing/options/route.tsx
app/components/dashboard/SubscriptionChangePanel.jsx
```

The following Attempt-2 outcomes are accepted and must remain:

```text
billing-options route == exact pre-SHOPIFY-015 parent composition
active-only pending BillingPlan mapping
provider currency is never defaulted to GBP
pending interval is not fabricated
unmapped current contract remains visible
pending mapped Moda name is decoration only
supplied managePlansHref is the only CTA destination
no local rank/price upgrade/downgrade inference
```

#### Attempt-3 allowed scope

Production:

```text
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.service.ts
```

Tests:

```text
tests/unit/routes/billing-callback.test.ts
tests/unit/services/billing.service.test.ts
```

Plus this task file / Completion Report.

Do not modify:

```text
app/routes/app/billing/options/route.tsx
app/components/dashboard/SubscriptionChangePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/billing-purchase.mock.js
app/services/billing/providers/shopify-billing.provider.ts
Prisma schema/migrations
Shared contracts/package version
Background services
Admin, Messaging or Gateway
SHOPIFY-012/014/016 implementation
```

If fixing the freshness race requires a provider-contract/schema/Background change, STOP and return the exact conflict to `moda_architect` rather than expanding scope.

#### Required validation for Attempt 3

From `moda-interact` run:

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

rg -n "describe\\.skip|it\\.skip|test\\.skip" \
  tests/unit/routes/billing-callback.test.ts

rg -n "rank|isUpgrade|isDowngrade|upgradeAction|downgradeAction|appSubscriptionCreate|billing\\.request|moda-interact-admin" \
  app/components/dashboard/SubscriptionChangePanel.jsx \
  app/routes/app/billing/callback/route.tsx \
  app/services/billing/billing.service.ts
```

Expected results:

- callback skip scan exits 1 with zero matches;
- prohibited production scan exits 1 with zero matches;
- focused/full tests record exact pass/fail/skip totals;
- callback activation and hosted-return suites are both executable;
- Prisma validation/generation, typecheck, build and `git diff --check` pass, or any truly unrelated repository baseline is identified with exact changed-file proof.

#### Completion Report required

Record:

- implementation full SHA;
- parent report full SHA;
- preservation of synchronization merge `1ca0cb0b95e2bbeca37d33d27037521f2eb6b67c`;
- canonical parent/implementation worktrees and task branches;
- database submodule SHA before/after;
- exact focused/full test totals and callback skip count;
- exact stale-success/stale-failure freshness-fence test titles;
- exact protected-model no-write test titles;
- Prisma validation/generation, typecheck, build, both static scans and `git diff --check` results;
- clean/pushed branch state.

#### Reclaim / stop condition

Return this **same task** to `/moda-task`.

The current attempt counter remains:

```text
attempt: 2
```

The next authorized claim must increment it to **Attempt 3 exactly once**.

After corrections, set `status: review`, clear `executor`/`claimed_at`, commit and push both task branches, and STOP for architect review. Do not start SHOPIFY-012.

### Architect Review — Attempt 3

#### Status

**Changes Requested**

Attempt 3 correctly implements the previously requested wall-clock freshness check,
restores the accepted SHOPIFY-003 callback suite, and adds direct hosted-return
protected-model evidence. The focused/full/static validation reported by the task is
also consistent with the uploaded snapshot.

Two production correctness defects remain:

1. the wall-clock freshness comparison is not a valid commit-order fence across the
   Shopify app and Background worker;
2. nullable provider cycle/trial facts are persisted as `undefined`, which preserves
   stale local values instead of projecting the exact provider observation.

Attempt 4 must correct those two points and strengthen the hosted-return regression
evidence. Do not churn the accepted panel/options work.

#### Finding 1 — `verificationStartedAt` does not safely order concurrent durable commits

Attempt 3 implements:

```text
callback captures verificationStartedAt = new Date()
  -> Partner read
  -> transaction locks Subscription
  -> if Subscription.updatedAt > verificationStartedAt, reject stale observation
```

This still permits the race that SHOPIFY-015 is intended to prevent.

A concrete interleaving is:

```text
T-1 BACKGROUND-010 acquires/updates the Subscription row inside its transaction.
    The row's new updatedAt is generated now, but the transaction has not committed.

T0  callback captures verificationStartedAt.

T1  callback reads Shopify and receives the pre-transition/current+pending observation.

T2  callback tries to lock Subscription and waits behind BACKGROUND-010.

T3  BACKGROUND-010 commits its newer effective transition.

T4  callback obtains the lock and rereads Subscription.
```

The Background row is newer in **commit order**, but its stored `updatedAt` can be
earlier than `verificationStartedAt` because the Background mutation occurred before
T0. The current strict `updatedAt > verificationStartedAt` test therefore accepts the
older provider observation and can overwrite the newer projection.

Cross-process clock skew between the Shopify app and Background worker is an
additional reason not to compare their wall clocks for optimistic concurrency.

The correct fence is the durable Subscription projection observed **before** the
Partner request, compared for equality after the accepted row lock.

##### Required Attempt-4 correction

In:

```text
app/services/billing/billing.service.ts
```

add a repository-local hosted-verification fence type and reader. It must not require
schema or Shared changes.

Use a shape equivalent to:

```ts
export type HostedPlanVerificationFence = {
  id: string | null;
  updatedAt: Date | null;
  status: SubscriptionProjectionStatus | null;
  observedShopifyPlanHandle: string | null;
  planId: string | null;
  billingPeriodId: string | null;
  currentPeriodStart: Date | null;
  currentPeriodEnd: Date | null;
  trialEndsAt: Date | null;
  cancelAtPeriodEnd: boolean | null;
  pendingShopifyPlanHandle: string | null;
  pendingPlanId: string | null;
  pendingEffectiveAt: Date | null;
  nextReconcileAt: Date | null;
  lastSyncedAt: Date | null;
  lastSyncErrorCode: string | null;
  lastSyncErrorAt: Date | null;
};
```

A null Subscription must return the same shape with null values, or another explicit
`subscription: null` representation that can be compared deterministically.

Add:

```ts
async getHostedPlanVerificationFence(
  shopId: string,
): Promise<HostedPlanVerificationFence>
```

using one ordinary PostgreSQL/Prisma read before the provider request.

Do **not** acquire a row lock and do **not** call Shopify in this method.

Create one local equality helper which compares:

- id;
- `updatedAt`;
- every projection field above;
- nullable Dates by exact `getTime()` equality.

The purpose is not merely to compare timestamps. Even if `updatedAt` collides at the
same millisecond, a changed entitlement/current/pending/error projection must make the
fence unequal.

In:

```text
app/routes/app/billing/callback/route.tsx
```

replace:

```ts
const verificationStartedAt = new Date();
```

with:

```ts
const verificationFence =
  await billingService.getHostedPlanVerificationFence(shop.id);
```

Capture it **immediately before**:

```ts
billingService.getMerchantShopifySubscriptionState(shop.id)
```

and after the initial Free/Paid activation branch has returned no activation.

Call the Partner/read-model method exactly once.

Pass that **same immutable fence value** to:

```text
recordHostedPlanChangeReturn(...)
recordHostedPlanVerificationFailure(...)
```

depending on success/failure.

Do not reread the fence after the Partner request.

In both persistence methods:

1. preserve the accepted ShopSettings -> Subscription lock order;
2. reread the locked Subscription with the complete fence fields;
3. compare the locked projection to the pre-provider `verificationFence`;
4. if unequal:
   - successful observation: return
     `{ result: "unverified", subscriptionId: current?.id ?? null, nextReconcileAt: null }`;
   - failed observation: return `null`;
   - perform zero BillingPlan mapping lookup needed only for that observation;
   - perform zero Subscription mutation;
   - perform zero protected entitlement/history mutation;
5. only an unchanged durable fence may apply CURRENT/PENDING/NO_ACTIVE projection or
   verification-error metadata.

Remove `verificationStartedAt` from the hosted-return/failure method contracts once
the durable fence is in place. Do not keep the wall-clock comparison as a second
authority.

This correction uses the durable row as the optimistic token. It does not change
BACKGROUND-010 or hold a database lock across a network call.

#### Finding 2 — null provider period/trial facts currently preserve stale local values

`recordHostedPlanChangeReturn(...)` currently writes:

```ts
currentPeriodStart:
  provider.currentPeriodStart ? new Date(provider.currentPeriodStart) : undefined,

currentPeriodEnd:
  provider.currentPeriodEnd ? new Date(provider.currentPeriodEnd) : undefined,

trialEndsAt:
  provider.trialEndsAt ? new Date(provider.trialEndsAt) : undefined,
```

For Prisma updates, `undefined` means "do not change this column".

Therefore a verified provider observation such as:

```text
currentPeriodStart = null
currentPeriodEnd   = null
trialEndsAt        = null
```

can leave old non-null local values in place.

That violates this task's `CURRENT`/`PENDING` requirement to persist the exact
provider current projection. It can also leave a stale trial end after Shopify has
already removed the trial.

##### Required correction

For a non-stale verified CURRENT or PENDING provider observation, persist exact
nullable facts:

```ts
currentPeriodStart: provider.currentPeriodStart
  ? new Date(provider.currentPeriodStart)
  : null,

currentPeriodEnd: provider.currentPeriodEnd
  ? new Date(provider.currentPeriodEnd)
  : null,

trialEndsAt: provider.trialEndsAt
  ? new Date(provider.trialEndsAt)
  : null,
```

Do not manufacture a cycle or trial date.

This task still does not open/close BillingPeriod or grant/forfeit entitlement in the
HTTP request.

#### Required Attempt-4 regression evidence

Only the hosted-return/callback tests need additional work.

##### A. Callback durable-fence propagation

In:

```text
tests/unit/routes/billing-callback.test.ts
```

mock:

```text
getHostedPlanVerificationFence
```

with one frozen object.

Add:

```text
captures the durable hosted verification fence before the Partner read
```

Prove invocation order:

```text
getHostedPlanVerificationFence
  before
getMerchantShopifySubscriptionState
```

and prove the exact returned fence object is passed to
`recordHostedPlanChangeReturn(...)`.

Add:

```text
passes the same durable hosted verification fence to provider failure recording
```

Make the Partner read reject and prove the exact same fence object is passed to
`recordHostedPlanVerificationFailure(...)`.

Keep:

```text
does not enqueue a freshness-fenced unverified result
```

and update it to the durable-fence API.

The Partner read must still be called exactly once.

##### B. Commit-order race regression

In:

```text
tests/unit/services/billing.service.test.ts
```

replace the Attempt-3 wall-clock-only stale tests with durable-fence tests.

Add:

```text
fences a durable commit that is newer than the pre-provider projection even when its updatedAt is earlier than the old wall-clock start
```

Use:

```text
pre-provider fence updatedAt = 2026-09-01T10:00:00.000Z
locked/current updatedAt     = 2026-09-01T10:00:00.500Z
hypothetical old wall-clock verification start
                             = 2026-09-01T10:00:01.000Z
```

The important proof is that:

```text
locked.updatedAt < old wall-clock start
locked projection != pre-provider fence
```

and the result is still:

```text
unverified
zero BillingPlan lookup
zero Subscription writes
zero protected-model writes
```

The test must not call or depend on a `verificationStartedAt` production parameter.

Add:

```text
fences a changed durable projection even when updatedAt is identical
```

Keep the same `updatedAt` in the pre-provider fence and locked row, but change at
least one authority field such as:

```text
planId
billingPeriodId
pendingShopifyPlanHandle
```

Assert the provider observation is rejected with zero writes.

This proves the fence is not relying on timestamp uniqueness.

Add the equivalent failed-provider case:

```text
does not record provider failure when the durable projection changed during verification
```

and assert:

```text
recordHostedPlanVerificationFailure -> null
zero Subscription writes
zero protected writes
```

##### C. Exact-null provider projection

Add:

```text
clears stale nullable provider cycle and trial facts from a verified hosted observation
```

Start the local Subscription with non-null:

```text
currentPeriodStart
currentPeriodEnd
trialEndsAt
```

Use a verified provider state with all three values null.

After CURRENT or PENDING persistence assert all three durable fields are exactly null.

Also assert:

```text
status unchanged
planId unchanged
billingPeriodId unchanged
zero BillingPeriod/counter/credit/promotion/refund writes
```

##### D. Complete hosted protected-state spy set

Extend the hosted-return protected-model fixture to include:

```text
recoveryCreditRefund
```

in addition to:

```text
billingPeriod
billingPeriodEntitlementCounter
shopEntitlementCounter
recoveryCreditPurchase
promotionalCreditGrant
merchantPromotionSelection
```

Keep the existing no-write helper over:

```text
create
createMany
update
updateMany
upsert
delete
deleteMany
```

where available.

##### E. Tighten existing CURRENT/PENDING/failure assertions

For PENDING assert explicitly that these remain unchanged:

```text
status
planId
billingPeriodId
```

For CURRENT assert the same.

For provider verification failure, capture the `subscription.updateMany(...)` payload
and assert its business data contains only:

```text
nextReconcileAt
lastSyncErrorCode = PARTNER_API_ERROR
lastSyncErrorAt
```

For NO_ACTIVE, assert the Subscription update changes only:

```text
nextReconcileAt
lastSyncErrorCode = null
lastSyncErrorAt = null
```

plus Prisma-managed `updatedAt` outside the supplied data object.

Do not weaken accepted protected no-write assertions.

#### Accepted Attempt-3 work — do not churn

Keep the restored executable:

```text
describe("billing callback activation", ...)
```

suite and its accepted SHOPIFY-003 defaults.

Keep the hosted-flow nested setup that explicitly sets:

```text
prepareFreeActivation -> null
preparePaidActivation -> null
```

Do not reintroduce callback skips.

Unless a focused test exposes a direct defect, do not change:

```text
app/routes/app/billing/options/route.tsx
app/components/dashboard/SubscriptionChangePanel.jsx
```

The accepted provider-commercial-truth/component behavior remains final for this task.

#### Attempt-4 allowed scope

Production:

```text
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.service.ts
```

Tests:

```text
tests/unit/routes/billing-callback.test.ts
tests/unit/services/billing.service.test.ts
```

Plus this task/Completion Report.

Do not modify:

```text
app/routes/app/billing/options/route.tsx
app/components/dashboard/SubscriptionChangePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/billing-purchase.mock.js
app/services/billing/providers/shopify-billing.provider.ts
Prisma schema/migrations
Shared contracts/package version
Background services
Admin
Messaging
Gateway
SHOPIFY-012/014/016 implementation
```

If a durable pre-provider fence cannot be implemented without a schema/Shared/
Background change, STOP and return the exact limitation to `moda_architect`.

#### Required validation for Attempt 4

From `moda-interact` run:

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

rg -n "describe\\.skip|it\\.skip|test\\.skip" \
  tests/unit/routes/billing-callback.test.ts

rg -n "verificationStartedAt|rank|isUpgrade|isDowngrade|upgradeAction|downgradeAction|appSubscriptionCreate|billing\\.request|moda-interact-admin" \
  app/components/dashboard/SubscriptionChangePanel.jsx \
  app/routes/app/billing/callback/route.tsx \
  app/services/billing/billing.service.ts
```

Expected:

- callback skip scan: zero matches;
- production scan: zero matches for `verificationStartedAt` and all prohibited
  inference/mutation/Admin terms;
- exact focused/full pass/fail/skip totals recorded;
- Prisma validation/generation and build pass;
- `git diff --check` passes;
- typecheck may retain `TYPECHECK-001` only if no Attempt-4 changed line introduces a
  new diagnostic.

#### Completion Report required

Record:

- Attempt-3 implementation full SHA:
  `69c79a6214dd74521453456724c63092bf369230`;
- Attempt-3 final parent/report full SHA corresponding to the developer handoff
  `7bd791e`;
- synchronization merge
  `1ca0cb0b95e2bbeca37d33d27037521f2eb6b67c`;
- Attempt-4 launcher claim full SHA;
- Attempt-4 implementation full SHA;
- Attempt-4 parent/report publication full SHA;
- canonical parent/implementation worktrees and branches;
- database submodule SHA before/after;
- exact durable-fence test titles;
- exact nullable-provider-projection test title;
- exact protected no-write tests;
- focused/full/typecheck/build/static scan results;
- both branches clean and pushed.

Resolve the full Attempt-3 parent SHA with `git rev-parse` from the dedicated parent
task branch. Do not leave `Parent report commit: pending` in the next Completion
Report.

#### Reclaim / stop condition

Return this **same task** through `/moda-task`.

Preserve:

```text
attempt: 3
```

The next authorized claim must increment to **Attempt 4 exactly once**.

After implementing only the corrections above, updating the Completion Report,
running validation, setting `status: review`, clearing `executor`/`claimed_at`,
committing/pushing both mirrored task branches and verifying both are clean, STOP and
return to `moda_architect`.

Do not start `ARCH-010-SHOPIFY-012`.

### Architect Review — Attempt 4

#### Status

**Changes Requested**

Attempt 4 satisfies the substantive durable-fence correction from Attempt 3:

- the callback captures one durable Subscription projection immediately before the
  single Partner read;
- the locked Subscription projection is compared field-for-field after the accepted
  ShopSettings -> Subscription lock;
- changed authority state is fenced even when the old wall-clock ordering would have
  accepted it;
- changed projection is fenced even when `updatedAt` is identical;
- failed Partner verification is also fenced by the same durable projection;
- verified provider `currentPeriodStart`, `currentPeriodEnd` and `trialEndsAt` now
  persist exact null values;
- protected no-write evidence includes `RecoveryCreditRefund`;
- the accepted callback activation, panel/options and provider-commercial-truth work
  remains unchanged.

One narrow production defect remains in the null-Subscription representation. No
other Attempt-4 production correction is requested.

#### Finding — an unchanged absent Subscription always fails the durable fence

`getHostedPlanVerificationFence(...)` currently declares:

```ts
Promise<HostedPlanVerificationFence>
```

and represents no durable Subscription as an object whose every field is null.

The post-lock reread in both hosted persistence methods is:

```ts
const current = await transaction.subscription.findUnique(...);
```

which is actual:

```ts
null
```

when no Subscription exists.

The equality helper begins:

```ts
if (!left || !right) return left === right;
```

Therefore this unchanged durable state:

```text
pre-provider: no Subscription
post-lock:    no Subscription
```

is compared as:

```text
left  = null
right = { id:null, updatedAt:null, ... }
```

and is incorrectly classified as changed/stale.

Consequences:

- a fresh merchant with no durable Subscription and provider
  `NO_ACTIVE_SUBSCRIPTION` cannot reach the task's distinct `no_active`
  classification;
- it is returned as `unverified` even though no concurrent durable change occurred;
- provider failure for an absent durable Subscription also cannot distinguish
  "unchanged but there is no row to update" from a stale fence.

The Attempt-3 Architect Review explicitly required:

```text
A null Subscription must return the same shape with null values,
or another explicit subscription:null representation that can be
compared deterministically.
```

The current implementation creates the first representation before the Partner read
but compares it to the second representation after the lock.

#### Required Attempt-5 correction

Keep the existing field-by-field durable fence exactly as implemented for present
Subscription rows.

Use actual `null` as the canonical absence representation.

In:

```text
app/services/billing/billing.service.ts
```

change:

```ts
async getHostedPlanVerificationFence(
  shopId: string,
): Promise<HostedPlanVerificationFence>
```

to:

```ts
async getHostedPlanVerificationFence(
  shopId: string,
): Promise<HostedPlanVerificationFence | null>
```

and return the Prisma result directly:

```ts
return subscription;
```

Do not manufacture an all-null object.

The existing local type:

```ts
type HostedPlanVerificationFenceSource =
  HostedPlanVerificationFence | null;
```

and:

```ts
sameHostedPlanVerificationFence(...)
```

already support deterministic:

```text
null == null
```

comparison. Preserve their present-field comparison logic unchanged.

Change both persistence method parameters to accept the same nullable fence type:

```ts
recordHostedPlanChangeReturn({
  ...
  verificationFence,
}: {
  ...
  verificationFence: HostedPlanVerificationFence | null;
})
```

and:

```ts
recordHostedPlanVerificationFailure(
  shopId: string,
  verificationFence: HostedPlanVerificationFence | null,
)
```

Do not add a sentinel string, synthetic ID, schema field or Shared contract.

##### Absent Subscription + NO_ACTIVE

After an unchanged:

```text
verificationFence = null
locked current = null
state.status = NO_ACTIVE_SUBSCRIPTION
```

`recordHostedPlanChangeReturn(...)` must return exactly:

```ts
{
  result: "no_active",
  subscriptionId: null,
  nextReconcileAt: null,
}
```

with:

```text
zero BillingPlan lookup
zero Subscription write
zero protected-model write
```

This does not manufacture a Subscription merely to schedule reconciliation.

##### Absent Subscription + Partner failure

After an unchanged:

```text
verificationFence = null
locked current = null
```

`recordHostedPlanVerificationFailure(...)` must return:

```ts
null
```

without issuing a Subscription mutation.

After the fence equality check, add:

```ts
if (!current) return null;
```

before `subscription.updateMany(...)`.

There is no durable Subscription row on which retry/error metadata can be stored.

Do not create one.

#### Required Attempt-5 regression evidence

Allowed tests remain:

```text
tests/unit/routes/billing-callback.test.ts
tests/unit/services/billing.service.test.ts
```

##### Service fence-reader evidence

Add:

```text
returns null hosted verification fence when no durable Subscription exists
```

Mock `database.subscription.findUnique(...)` to return null.

Assert:

```ts
await expect(
  service.getHostedPlanVerificationFence("shop-1"),
).resolves.toBeNull();
```

Also assert the reader performs no write/transaction/provider operation.

##### NO_ACTIVE absent-row evidence

Add:

```text
classifies unchanged absent durable Subscription as no_active
```

Use:

```text
verificationFence = null
transaction subscription findUnique = null
state = {
  status: "NO_ACTIVE_SUBSCRIPTION",
  subscription: null,
}
```

Assert exactly:

```ts
expect(result).toEqual({
  result: "no_active",
  subscriptionId: null,
  nextReconcileAt: null,
});

expect(billingPlan.findUnique).not.toHaveBeenCalled();
expect(subscription.update).not.toHaveBeenCalled();
expect(subscription.updateMany).not.toHaveBeenCalled();
expectNoProtectedWrites(protectedModels);
```

##### Provider-failure absent-row evidence

Add:

```text
does not manufacture retry metadata when durable Subscription is absent
```

Use:

```text
verificationFence = null
locked current = null
```

Assert:

```ts
await expect(
  service.recordHostedPlanVerificationFailure("shop-1", null),
).resolves.toBeNull();

expect(subscription.update).not.toHaveBeenCalled();
expect(subscription.updateMany).not.toHaveBeenCalled();
expectNoProtectedWrites(protectedModels);
```

##### Callback nullable-fence propagation

Add:

```text
passes an absent durable verification fence unchanged through hosted NO_ACTIVE verification
```

Mock:

```text
getHostedPlanVerificationFence -> null
getMerchantShopifySubscriptionState ->
  { status: "NO_ACTIVE_SUBSCRIPTION", subscription: null }
recordHostedPlanChangeReturn ->
  { result: "no_active", subscriptionId: null, nextReconcileAt: null }
```

Prove:

```text
getHostedPlanVerificationFence called before Partner read
Partner read called exactly once
recordHostedPlanChangeReturn receives verificationFence: null
no reconciliation enqueue
redirect = /app/billing/options?plan_change=no_active
```

Add the provider-failure equivalent:

```text
passes an absent durable verification fence unchanged to failure recording
```

and prove:

```text
recordHostedPlanVerificationFailure("shop-1", null)
```

is called.

#### Accepted Attempt-4 work — do not churn

Do not rewrite the accepted durable fence for present rows.

In particular preserve these permanent tests:

```text
captures the durable hosted verification fence before the Partner read
passes the same durable hosted verification fence to provider failure recording
fences a durable commit that is newer than the pre-provider projection even when its updatedAt is earlier than the old wall-clock start
fences a changed durable projection even when updatedAt is identical
does not record provider failure when the durable projection changed during verification
clears stale nullable provider cycle and trial facts from a verified hosted observation
```

Keep the field-by-field fence comparison including exact nullable Date equality.

Keep provider read count exactly one.

Keep the accepted CURRENT/PENDING/NO_ACTIVE business-write restrictions and all
protected no-write assertions.

Do not change:

```text
app/routes/app/billing/options/route.tsx
app/components/dashboard/SubscriptionChangePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx
app/services/billing/providers/shopify-billing.provider.ts
```

#### Attempt-5 allowed scope

Production:

```text
app/services/billing/billing.service.ts
app/routes/app/billing/callback/route.tsx
```

The callback production file should require only TypeScript nullable-fence propagation;
do not change callback behavior unless compilation requires it.

Tests:

```text
tests/unit/services/billing.service.test.ts
tests/unit/routes/billing-callback.test.ts
```

Plus this task/Completion Report.

Do not modify:

```text
Prisma schema/migrations
Shared contracts/package
Background
Admin
Messaging
Gateway
SHOPIFY-012/014/016
panel/options commercial presentation
billing purchase behavior
```

If the null fence cannot be implemented using the existing repository-local type
without schema/Shared changes, STOP and return the exact limitation to
`moda_architect`.

#### Required Attempt-5 validation

From `moda-interact` run:

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

rg -n "describe\\.skip|it\\.skip|test\\.skip" \
  tests/unit/routes/billing-callback.test.ts

rg -n "verificationStartedAt|rank|isUpgrade|isDowngrade|upgradeAction|downgradeAction|appSubscriptionCreate|billing\\.request|moda-interact-admin" \
  app/components/dashboard/SubscriptionChangePanel.jsx \
  app/routes/app/billing/callback/route.tsx \
  app/services/billing/billing.service.ts
```

Expected:

```text
callback skip scan -> zero matches
prohibited production scan -> zero matches
```

Record exact focused/full pass/fail/skip totals.

`TYPECHECK-001` remains non-blocking only if no Attempt-5 changed line introduces a
new diagnostic and the repository baseline does not worsen.

#### Completion Report requirements

Preserve and record:

```text
Attempt-3 implementation:
69c79a6214dd74521453456724c63092bf369230

Attempt-3 parent/report:
7bd791e4662c2d554ebbcaf40cbc93dce9a2920e

Attempt-4 launcher claim:
c481e7ad8b83823536b6ef1566259c2250bf6404

Attempt-4 implementation:
aeceed5cb1aa6bd0c9e20bced0130171305a3fa9

Attempt-4 initial report publication:
7fa80f3c3428ad36540ee51f2946e67f0c60bbf0

Attempt-4 final parent/report:
resolve and record the full SHA corresponding to developer handoff
4f2abd4d138e1882b9da560e6d27615e9d4c6a50

Attempt-5 launcher claim full SHA
Attempt-5 implementation full SHA
Attempt-5 parent/report publication full SHA

database gitlink before/after:
5443afdd8f0c816dc16e1f3e93f9906c5ca31d94
```

Also record the four exact null-fence regression test titles above and both branches
clean/pushed/remote-synchronized.

Do not create an endless report-commit self-reference; record immutable predecessor
publication SHAs plus the final developer handoff SHA in the normal way.

#### Reclaim / stop condition

Return this SAME task through `/moda-task`.

Preserve:

```text
attempt: 4
```

The next authorized claim must increment to **Attempt 5 exactly once**.

After implementing only the null-fence correction, running validation, updating the
Completion Report, setting `status: review`, clearing `executor`/`claimed_at`,
committing/pushing both mirrored branches and verifying them clean, STOP and return to
`moda_architect`.

Do not start `ARCH-010-SHOPIFY-012`.

### Architect Review — Attempt 5

#### Status

**Accepted**

Attempt 5 closes the final null-Subscription durable-fence defect from Attempt 4.

Architect verification against the uploaded Attempt-4 and Attempt-5 snapshots confirms
that the Attempt-5 implementation delta is limited to:

```text
app/services/billing/billing.service.ts
tests/unit/services/billing.service.test.ts
tests/unit/routes/billing-callback.test.ts
```

No schema, Shared, Background, panel/options, provider, Admin, Messaging or Gateway
implementation changed.

Accepted production behavior:

1. `getHostedPlanVerificationFence(...)` returns the actual nullable durable
   Subscription projection:

```text
present Subscription -> full immutable hosted verification fence
absent Subscription  -> null
```

2. The accepted field-by-field equality fence for present rows remains unchanged,
   including exact nullable Date equality and the current/pending/error projection.
3. An unchanged absent Subscription now compares deterministically as `null == null`.
4. `NO_ACTIVE_SUBSCRIPTION` with no durable Subscription returns exactly:

```ts
{
  result: "no_active",
  subscriptionId: null,
  nextReconcileAt: null,
}
```

without BillingPlan lookup, Subscription mutation, reconciliation enqueue, or
protected-model mutation.
5. Provider verification failure with no durable Subscription returns `null` and does
   not manufacture retry/error metadata or a Subscription row.
6. The callback propagates the same nullable fence through both successful
   `NO_ACTIVE` verification and Partner-failure handling.
7. The accepted Attempt-4 commit-order fence, identical-`updatedAt` projection fence,
   exact nullable provider projection, single Partner read, lock order, and protected
   no-write invariants remain intact.

Permanent Attempt-5 regression evidence:

```text
returns null hosted verification fence when no durable Subscription exists

classifies unchanged absent durable Subscription as no_active

does not manufacture retry metadata when durable Subscription is absent

passes an absent durable verification fence unchanged through hosted NO_ACTIVE verification

passes an absent durable verification fence unchanged to failure recording
```

Accepted validation evidence:

```text
Focused:              196 passed, 0 failed, 0 skipped
Full suite:           438 passed, 3 skipped, 0 failed
Prisma validate:      passed
Prisma generate:      passed
Build:                passed
git diff --check:     passed
callback skip scan:   zero matches
prohibited scan:      zero matches
Typecheck baseline:   151 existing TYPECHECK-001 diagnostics; no new Attempt-5 diagnostic
Database gitlink:     5443afdd8f0c816dc16e1f3e93f9906c5ca31d94 unchanged
```

Accepted workflow evidence:

```text
Attempt-4 final parent/report:
4f2abd4d138e1882b9da560e6d27615e9d4c6a50

Attempt-5 launcher claim:
bf32268f965829470459d28512222962e3faedb5

Attempt-5 implementation:
0fad89ce76d59d954a0bd8894d527eaadda478b1

Attempt-5 initial report publication:
693a9817bbc572747e7b04897dc276400790a7d9

Final parent/report handoff reported by developer:
65f7e68923de648e317dee602c78ad3571129f4d
```

The final developer handoff SHA is a later metadata-only parent state than the immutable
initial report-publication commit. No self-referential report-commit cycle is required.

`ARCH-010-SHOPIFY-015` is Complete.

Dependency reconciliation:

- `ARCH-010-SHOPIFY-012` remains Pending because `ARCH-010-SHOPIFY-007`,
  `ARCH-010-SHOPIFY-009`, and `ARCH-010-SHOPIFY-014` are still incomplete.
- No normal implementation task becomes newly Ready solely from this acceptance.

