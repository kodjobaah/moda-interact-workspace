---
id: ARCH-010-SHOPIFY-006
architecture_id: ARCH-010
title: Gate reinstall until Background restores Shopify subscription truth
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHARED-008
- ARCH-010-BACKGROUND-006
enables:
- ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-SHOPIFY-006: Gate reinstall until Background restores Shopify subscription truth

## Objective

Replace the unsafe direct `UNINSTALLED -> ACTIVE` reinstall behaviour with a durable fail-closed restoration flow, and absorb the uninstall-persistence work formerly defined by superseded `ARCH-010-SHOPIFY-005`.

This task owns both sides in `moda-interact` so there is no deployable intermediate state where uninstall preserves stale billing state but `markInstalled()` immediately exposes it on reinstall.

## Inspect before editing

Inspect at minimum:

```text
app/routes/auth/catchall/route.jsx
app/routes/webhooks/app/uninstalled/route.jsx
app/services/shop/shop.service.ts
app/services/shop/shop-access-policy.ts
app/services/billing/billing.service.ts
app/routes/app/home/route.jsx
app/routes/app/billing/route.tsx
app/routes/app/billing/select/route.jsx
app/routes/app/merchant-support/route.jsx
app/routes.ts
app/db.server.*
app/components/onboarding/**
tests/unit/services/shop.service.test.ts
tests/unit/shop-access-policy.test.ts
tests/unit/routes/**
package.json
```

Inspect the published Shared reconciliation contract before creating queue producer code. Reuse repository Redis/BullMQ producer conventions if already integrated by SHOPIFY-002; do not create a second queue helper.

## Part A — uninstall persistence (supersedes SHOPIFY-005)

Keep the Iteration-4 rule:

On APP_UNINSTALLED, transactionally persist only installation availability:

```text
Shop.status = UNINSTALLED
Shop.uninstalledAt = stable uninstall event time
Shop.reinstallPendingAt = null
```

Preserve Subscription, BillingPeriod, Free/purchased/promotional credits, refunds, history and `ShopSettings.onboardingCompleted`.

Do not set `Subscription.status=NO_CONTRACT` merely due to uninstall.

Keep existing session deletion and duplicate-safe uninstall cutoff behaviour.

Do not publish a BullMQ reinstall job from uninstall.

## Part B — remove direct markInstalled reactivation

The supplied auth catchall currently calls:

```text
shopService.markInstalled(session.shop)
```

which changes `UNINSTALLED -> ACTIVE` immediately.

That operation is forbidden for an existing uninstalled Shop under ARCH-010.

Normal authenticated access for an already ACTIVE shop must remain a no-op with respect to lifecycle status. A SUSPENDED shop must never be silently reactivated.

## Part C — begin durable reinstall reconciliation

After `resolveShopifyShop({admin, domain})` returns an existing Shop with:

```text
status = UNINSTALLED
```

run a transaction/service operation equivalent to:

1. conditionally set `Shop.reinstallPendingAt = now` only when currently null;
2. keep `Shop.status=UNINSTALLED`;
3. preserve `Shop.uninstalledAt`;
4. ensure a Subscription projection exists; if absent, create `NO_CONTRACT` without inventing plan truth;
5. set `Subscription.nextReconcileAt = now`;
6. preserve current/pending plan/credit/period state until Background verifies Shopify;
7. return the durable `reinstallPendingAt` and `nextReconcileAt` values needed for deterministic enqueue.

Repeated authenticated requests during the same attempt must not reset `reinstallPendingAt`.

After the DB transaction commits, best-effort enqueue the canonical Shared `reconcile-subscription` job using `expectedNextReconcileAt` from the committed row.

Queue-add failure:

- must not roll back the DB state;
- must be logged using shared structured logging;
- must still redirect the merchant to the restoration screen;
- will be repaired by Background startup/periodic reconstruction.

Do not call Partner `activeSubscription` from this auth path. Reinstall verification is owned by BACKGROUND-006.

## Part D — restoration route/screen

Add an explicit merchant-facing route such as:

```text
/app/reinstalling
```

Use the repository's route conventions; exact filename may follow current React Router layout.

The loader must authenticate through Shopify and resolve the same Shop using the accepted current identity mechanism.

Behaviour:

```text
Shop ACTIVE
  -> redirect /app

Shop UNINSTALLED + reinstallPendingAt != null + nextReconcileAt != null
  -> render "Restoring your Moda Interact account"

Shop UNINSTALLED + reinstallPendingAt != null + nextReconcileAt == null
  -> render automatic-restoration-failed state with Retry + Contact support

Shop UNINSTALLED + reinstallPendingAt == null
  -> do not invent a reinstall; route back through normal auth/install handling

Shop SUSPENDED
  -> preserve existing suspended/support policy; never reactivate
```

The restoration loader must not fetch recoveries, conversations, customer data, usage detail or pending recovery lists.

## Part E — Retry restoration action

Provide an explicit authenticated action/button only for a timed-out/stopped reinstall attempt.

In a transaction:

```text
require Shop.status = UNINSTALLED
require Shop.reinstallPendingAt != null
set Shop.reinstallPendingAt = now
set Subscription.nextReconcileAt = now
preserve all billing/credit state
```

Then best-effort publish the deterministic reconciliation job and remain on `/app/reinstalling`.

Do not let ordinary page refresh reset the retry window.

## Part F — access-policy routing while pending

Update merchant route/access handling so a pending reinstall does not bounce into ordinary product screens or an authentication loop.

At minimum:

- `/app` should redirect an authenticated `UNINSTALLED + reinstallPendingAt` shop to `/app/reinstalling` before product queries;
- `/app/billing`, `/app/billing/select`, `/app/usage`, `/app/pending-recoveries`, recovery detail and other product surfaces remain unavailable while pending;
- merchant support is available to the authenticated pending-reinstall merchant;
- no admin screen/link is exposed.

Once BACKGROUND-006 changes Shop to ACTIVE:

- verified Free/Paid with onboarding complete returns to normal `/app`;
- provider-confirmed null sets onboarding false and `/app` renders/routes to the normal onboarding/plan-selection flow defined by `ARCH-010-SHOPIFY-001` / `ARCH-010-SHOPIFY-002`.

## No local entitlement mutation

This Shopify task must not:

- activate a Subscription;
- clear preserved plan state based on the reinstall callback alone;
- create/close BillingPeriod rows;
- grant/reset Free or paid credits;
- consume top-ups;
- apply pending upgrades/downgrades.

Only BACKGROUND-006 may finalize the reinstall after Partner reconciliation.

## Shop identity non-goal

Use the existing `resolveShopifyShop` behaviour. ARCH-010 accepts its current limitations for this initiative.

Do not add:

- new domain/shop heuristics;
- Meta phone mapping changes;
- cross-tenant search;
- alternate shop ownership inference.

## Required tests

At minimum prove:

1. APP_UNINSTALLED marks Shop UNINSTALLED and preserves Subscription status/plan;
2. uninstall clears no lifetime or paid entitlement data;
3. uninstall sets/keeps `reinstallPendingAt=null`;
4. normal auth for ACTIVE shop remains lifecycle no-op;
5. SUSPENDED shop is never reactivated;
6. auth for UNINSTALLED shop leaves status UNINSTALLED;
7. first reinstall attempt sets `reinstallPendingAt` and `nextReconcileAt`;
8. repeated auth does not reset `reinstallPendingAt`;
9. queue publication happens only after durable state commit;
10. queue publication failure does not undo pending reinstall state;
11. deterministic job payload uses committed expectedNextReconcileAt;
12. pending reinstall `/app` redirects before recovery/usage/product queries;
13. restoration route renders pending state without product data reads;
14. ACTIVE shop hitting restoration route redirects `/app`;
15. stopped/expired attempt shows Retry/support;
16. Retry explicitly resets the bounded attempt and schedules immediate reconciliation;
17. normal refresh does not reset the retry window;
18. billing plan selection is unavailable while reconciliation is pending;
19. provider-confirmed NO_CONTRACT state produced by Background reaches onboarding on next merchant request;
20. normal Free/Paid ACTIVE state produced by Background reaches normal merchant app;
21. merchant-support remains reachable during authenticated pending reinstall;
22. no merchant Admin route/link is added;
23. existing install/fresh-onboarding/billing callback tests remain passing.

## Validation

Inspect `package.json`; run focused shop/auth/access route tests first, then repository-declared relevant tests/typecheck/lint/build and `git diff --check`.

## Non-goals

Do not implement:

- Partner API reconciliation in moda-interact;
- billing-period rollover;
- upgrade/downgrade;
- shop identity redesign;
- Background business gates;
- Messaging changes;
- Admin UI;
- top-up refund changes.

## Stop conditions

STOP and return to `moda_architect` if:

- DATABASE-003 or the published Shared queue contract is unavailable;
- BACKGROUND-006 is not accepted/deployable before this task would expose the pending-reinstall producer;
- auth routing cannot distinguish an existing UNINSTALLED Shop without changing the accepted identity model;
- a normal merchant product route would need to allow UNINSTALLED execution to make the restoration page work;
- implementing this task would require direct Partner billing verification in the web request.

## Deployment sequencing

Deploy/integrate in this order:

1. DATABASE-003;
2. BACKGROUND-006 (plus its already-required queue/Redis dependencies);
3. SHOPIFY-006.

Do not deploy SHOPIFY-006 producer behaviour before the Background consumer/reconstruction path is available.

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
