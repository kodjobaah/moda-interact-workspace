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
status: pending
priority: 56
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-SHOPIFY-013
  - ARCH-010-SHARED-008
  - ARCH-010-BACKGROUND-010
  - ARCH-010-SHOPIFY-018
enables:
  - ARCH-010-SHOPIFY-012
created: 2026-09-11
updated: 2026-09-12
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
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
