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
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHARED-008
- ARCH-010-BACKGROUND-006
enables:
- ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: 2026-09-14
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
Ready for Review.

### Files Changed
- `app/routes.ts`
- `app/routes/auth/catchall/route.jsx`
- `app/routes/app/reinstalling/route.jsx`
- `app/services/billing/billing-reconciliation.service.ts`
- `app/services/shop/shop-access-policy.ts`
- `app/services/shop/shop.service.ts`
- `tests/unit/services/shop.service.test.ts`
- `tests/unit/routes/auth-catchall.test.ts`
- `tests/unit/routes/reinstalling-route.test.ts`

### Work Completed
- APP_UNINSTALLED now transactionally preserves subscription, billing-period, credit, refund, history and onboarding state while setting `UNINSTALLED`, preserving the first uninstall cutoff, and clearing `reinstallPendingAt`.
- Removed direct `markInstalled` reactivation. Active shops remain lifecycle no-ops and suspended shops cannot be silently reactivated.
- Added durable first-attempt and explicit retry reinstall scheduling, preserving existing subscription projection state and returning committed reconciliation inputs.
- Reused the canonical Shared `reconcile-subscription` producer with deterministic `expectedNextReconcileAt` payloads and shared structured logging for best-effort enqueue failures.
- Added `/app/reinstalling` pending/stopped/retry behavior and routed pending product access to it while keeping authenticated merchant support available.
- Added focused lifecycle, auth, access-policy, route and producer tests. No Partner API calls, entitlement mutation, billing-period mutation, Admin UI, or other repository changes were made.

### Validation Results
- Focused tests first: `npm test -- --run tests/unit/services/shop.service.test.ts tests/unit/shop-access-policy.test.ts tests/unit/services/billing-reconciliation.service.test.ts tests/unit/home-route.test.ts tests/unit/routes/auth-catchall.test.ts tests/unit/routes/reinstalling-route.test.ts tests/unit/routes/explicit-route-config.test.ts` -> 7 files passed, 32 tests passed.
- Full tests after `npm run prisma:generate`: `npm test` -> 36 files passed, 2 skipped; 321 tests passed, 3 skipped.
- Production build: `npm run build` -> passed, including Prisma generation and client/server bundles.
- Changed-file lint -> passed. Repository lint -> baseline failure with 11 errors in unrelated onboarding, billing-options/select, merchant-support, privacy, billing-provider and webhook-test files.
- Typecheck -> baseline failure after Prisma generation; remaining diagnostics are existing auth-catchall JSX typing and pre-existing test typing issues, with no diagnostics in the new reinstalling route or newly typed shop-service transactions.
- `git diff --check` -> passed.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-006`
- Implementation branch: `task/ARCH-010-SHOPIFY-006`
- Implementation commit: `6c62577` (`feat(shopify): gate reinstall on subscription restoration`)
- Implementation branch pushed to `origin/task/ARCH-010-SHOPIFY-006`.
- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-006`
- Parent branch/report commit and push: `0e23b44` pushed to `origin/task/ARCH-010-SHOPIFY-006`.

### Architect Review
Pending.

## Architect Review — Attempt 1

### Status

**Changes Requested**

Attempt 1 establishes the correct overall reinstall architecture: direct
`UNINSTALLED -> ACTIVE` reactivation is removed, billing/credit projection is
preserved on uninstall, the canonical Shared reconciliation queue is reused,
`/app/reinstalling` is present, active product routes use the Shop access policy,
and Partner verification remains owned by BACKGROUND-006.

The implementation is not yet safe under duplicate uninstall delivery and concurrent
or repeated reinstall requests. The corrections below are the complete Attempt-2
contract. Preserve the accepted architecture and do not redesign subscription,
billing-period, credit, queue, or shop-identity contracts.

### Finding 1 — a delayed duplicate uninstall can erase a new reinstall attempt

`app/services/shop/shop.service.ts::markUninstalled(...)` currently performs two Shop
writes:

1. a guarded write where `uninstalledAt = null` that records the stable uninstall
   cutoff and clears `reinstallPendingAt`; then
2. an unconditional second `updateMany({ where: { id } ... })` that again sets
   `status = UNINSTALLED` and `reinstallPendingAt = null`.

The first write is the duplicate-safe uninstall boundary. The second write defeats
that boundary. If a duplicate webhook from the original uninstall arrives after the
merchant has reinstalled and `reinstallPendingAt` has been established, the duplicate
can clear the live reinstall marker and invalidate BACKGROUND-006 authority.

#### Required correction

In `app/services/shop/shop.service.ts`:

- remove the unconditional second Shop mutation;
- for a genuine new uninstall, keep one guarded mutation equivalent to:

```ts
where: {
  id: shop.id,
  uninstalledAt: null,
},
data: {
  status: "UNINSTALLED",
  uninstalledAt,
  reinstallPendingAt: null,
}
```

- do not modify Subscription, BillingPeriod, ShopSettings, lifetime/purchased/
  promotional credits, refund state, or history;
- a duplicate delivery when `uninstalledAt` is already non-null must perform no
  second lifecycle mutation and therefore must preserve any `reinstallPendingAt`
  created after the original uninstall;
- do not add event-time heuristics or a second uninstall identity model. A successful
  BACKGROUND-006 restoration already clears `uninstalledAt`, so a genuinely later
  uninstall can again satisfy the guarded `uninstalledAt = null` transition.

### Finding 2 — ordinary auth silently restarts a stopped reinstall attempt

`beginReinstallReconciliation(...)` treats:

```text
reinstallPendingAt != null
Subscription.nextReconcileAt == null
```

as a reason to set `nextReconcileAt = now` again. Therefore a normal OAuth/auth
callback can restart a Background attempt that Background intentionally stopped and
that `/app/reinstalling` is supposed to present as the explicit Retry/support state.

This violates Part E: **only the explicit Retry action may restart a stopped attempt**.

#### Required correction

For `beginReinstallReconciliation(...)`:

- when `Shop.status != UNINSTALLED`, return `null`;
- when `reinstallPendingAt != null` and the existing Subscription has
  `nextReconcileAt != null`, preserve both durable values and return them for the
  deterministic best-effort enqueue;
- when `reinstallPendingAt != null` and Subscription is absent or has
  `nextReconcileAt == null`, do **not** reset either value and return `null`; this is
  the stopped state owned by the restoration screen/explicit Retry action;
- ordinary auth must never reset `reinstallPendingAt` or restart the bounded retry
  window.

Update `app/routes/auth/catchall/route.jsx` so every resolved `UNINSTALLED` Shop is
redirected to `/app/reinstalling` after the begin operation, even when the begin
operation returns `null`. Only call
`enqueueBillingSubscriptionReconcileBestEffort(...)` when a non-null durable
reconciliation payload is returned.

### Finding 3 — first-attempt CAS loss can return a marker that was never persisted

The first-attempt path reads `reinstallPendingAt = null`, calls guarded
`shop.updateMany(...)`, but ignores `updated.count`. Two concurrent authenticated
requests can both classify themselves as `isFirstAttempt`; the loser can then write a
new `Subscription.nextReconcileAt` and return its local `now` as
`reinstallPendingAt` even though another request owns the durable marker.

The task explicitly requires returned values to be the committed durable values used
for deterministic enqueue.

#### Required correction

Keep the existing conditional/CAS approach, but make its result authoritative:

1. if the first-attempt `Shop.updateMany` updates exactly one row, this transaction
   owns the new marker and may set/create the Subscription immediate schedule;
2. if it updates zero rows, do not write a competing schedule from the stale read;
   re-read the durable Shop/Subscription state after the conflicting transaction is
   visible;
3. if the re-read is still `UNINSTALLED`, has a durable `reinstallPendingAt`, and has
   non-null `nextReconcileAt`, return those **actual** values without mutation;
4. if the re-read is stopped (`nextReconcileAt == null`) or lifecycle state changed,
   return `null`;
5. never return the losing request's local timestamp as the durable marker.

Do not introduce a process-local mutex. PostgreSQL durable state/CAS remains the
source of truth.

### Finding 4 — Retry is not restricted to stopped state and is stale-race unsafe

`retryReinstallReconciliation(...)` currently permits any
`UNINSTALLED + reinstallPendingAt != null` row, including a still-pending attempt with
non-null `nextReconcileAt`. A crafted/replayed POST can therefore reset the retry
window while reconciliation is still live.

It also ignores the result of its guarded Shop write. If BACKGROUND-006 activates or
suspends the Shop between the read and update, this method can still overwrite
`Subscription.nextReconcileAt` and publish a stale job after lifecycle authority has
changed.

#### Required correction

The Retry transaction must be all-or-nothing and must require the stopped state:

```text
Shop.status = UNINSTALLED
Shop.reinstallPendingAt = <non-null exact current marker>
Subscription.nextReconcileAt = null
```

An absent Subscription may be treated as stopped and recreated as `NO_CONTRACT`, as
already allowed by this task, but do not alter any existing plan/cycle/credit fields.

Required transaction behaviour:

1. read the exact current Shop marker and Subscription schedule;
2. if an existing Subscription has `nextReconcileAt != null`, return `null` with **no
   Shop or Subscription mutation**;
3. CAS the Shop using `status = UNINSTALLED` **and the exact previously-read
   `reinstallPendingAt`**; set the new marker only if that CAS updates exactly one row;
4. if the Shop CAS updates zero rows, return/abort with no Subscription mutation;
5. only after the Shop CAS succeeds, set/create `Subscription.nextReconcileAt = now`;
6. return the committed new marker/schedule for post-commit deterministic enqueue;
7. if a subsequent guarded Subscription mutation cannot be completed, roll back the
   transaction rather than leaving the Shop marker reset without its matching
   schedule.

The route action may continue redirecting to `/app/reinstalling`; when the service
returns `null`, it must not enqueue anything.

### Finding 5 — required access/restoration evidence is incomplete

The production `assertActiveShop`/`assertSupportShop` shape is directionally correct,
but the focused suite does not prove several explicit SHOPIFY-006 acceptance cases.
For example, `shop-access-policy.test.ts` currently tests only an UNINSTALLED Shop
**without** a reinstall marker, so it never executes the new `/app/reinstalling`
branch.

Attempt 2 must add deterministic executable tests rather than source-only comments.

#### `tests/unit/services/shop.service.test.ts`

Add/strengthen tests proving:

1. delayed duplicate uninstall after a reinstall marker exists performs no
   unconditional marker-clearing mutation;
2. first begin attempt persists marker + immediate schedule;
3. existing pending attempt preserves marker and schedule;
4. existing stopped attempt (`marker != null`, `nextReconcileAt == null`) is **not**
   automatically restarted by begin/auth;
5. simulated first-attempt CAS loss re-reads and returns the competing transaction's
   durable marker/schedule, with no stale schedule overwrite;
6. Retry while `nextReconcileAt != null` is rejected with no marker/schedule mutation;
7. stopped Retry resets the exact old marker and immediate schedule once;
8. stale Retry Shop CAS failure after lifecycle change performs no Subscription
   update/create and returns `null`.

#### `tests/unit/routes/auth-catchall.test.ts`

Prove:

9. ACTIVE is a lifecycle no-op;
10. SUSPENDED never calls begin/enqueue;
11. first/pending UNINSTALLED state redirects `/app/reinstalling` and enqueues only
    when a durable payload exists;
12. stopped UNINSTALLED state still redirects `/app/reinstalling` when begin returns
    `null`, and does not enqueue.

#### `tests/unit/shop-access-policy.test.ts`

Prove separately:

13. `UNINSTALLED + reinstallPendingAt` on an active/product capability redirects
    `/app/reinstalling`;
14. `UNINSTALLED` without a marker retains the existing fallback redirect;
15. `UNINSTALLED + reinstallPendingAt` is allowed through `assertSupportShop`;
16. SUSPENDED support remains allowed.

#### `tests/unit/home-route.test.ts`

Add a pending-reinstall loader test proving the redirect occurs **before** calls to:

```text
shopSettings.findUnique
billingService.getSubscription
readPendingRecoveries
checkoutRecovery.findMany
billingPeriod.findMany
usageEvent.findMany
```

Also retain/prove the existing Background outcomes:

- ACTIVE + onboarding incomplete/NO_CONTRACT reaches onboarding without product data;
- ACTIVE Free/Paid/Trialing can continue through the normal merchant application.

#### `tests/unit/routes/reinstalling-route.test.ts`

Add explicit loader/action cases proving:

17. ACTIVE -> `/app`;
18. SUSPENDED -> `/app/merchant-support`;
19. UNINSTALLED with no marker -> normal auth/install handling (`/auth/login` in the
    current implementation);
20. ordinary pending/stopped loader reads only the Shop + reinstall Subscription
    schedule and does not reset the retry window;
21. Retry action with a null service result does not enqueue.

#### Existing merchant/billing route suites

Add/strengthen behavioural tests proving:

22. `/app/billing/select` for
    `UNINSTALLED + reinstallPendingAt` redirects `/app/reinstalling` before Shopify
    hosted-pricing redirect is invoked;
23. authenticated pending-reinstall merchant support remains reachable and uses only
    the authenticated Shop id;
24. the reinstall page/routes add no `moda-interact-admin` route/link.

Reuse `tests/unit/billing-ui.test.ts` and
`tests/unit/merchant-support-route.test.ts` where practical; do not create duplicate
access-policy implementations inside tests.

### Scope / non-goals for Attempt 2

Allowed production scope:

```text
app/services/shop/shop.service.ts
app/routes/auth/catchall/route.jsx
```

`app/routes/app/reinstalling/route.jsx` may be changed only if necessary to consume the
corrected service result; its product/state design should otherwise remain intact.

Allowed test scope includes the focused files listed above.

Do **not** modify:

- Prisma schema/migrations;
- Shared package/contracts;
- BACKGROUND-006;
- Partner API/provider calls;
- BillingPeriod/credit/refund/promotion business state;
- shop identity resolution;
- Admin, Messaging or Gateway;
- upgrade/downgrade/cancellation/freeze logic.

Do not add a second queue producer or a local subscription-reconciliation contract.

### Required validation for Attempt 2

Run from `moda-interact`:

```bash
npm test -- --run \
  tests/unit/services/shop.service.test.ts \
  tests/unit/shop-access-policy.test.ts \
  tests/unit/services/billing-reconciliation.service.test.ts \
  tests/unit/home-route.test.ts \
  tests/unit/routes/auth-catchall.test.ts \
  tests/unit/routes/reinstalling-route.test.ts \
  tests/unit/billing-ui.test.ts \
  tests/unit/merchant-support-route.test.ts \
  tests/unit/routes/explicit-route-config.test.ts

npm test
npm run build
npm run typecheck
npm run lint
git diff --check
```

Report exact pass/fail/skip counts. Existing unrelated repository lint/typecheck
baselines may be documented, but there must be no diagnostic in an Attempt-2 changed
file.

### Workflow / stop condition

Return this **same task** through the normal `/moda-task` workflow.

Keep:

```text
attempt: 1
```

The next authorized claim increments it to **Attempt 2 exactly once**.

After implementing only these corrections, updating the Completion Report, setting
`status: review`, clearing `executor`/`claimed_at`, committing/pushing both mirrored
task branches, STOP and return to `moda_architect`.

`ARCH-010-SYSTEM-TEST-002` remains Pending/manual-gated and MUST NOT be started.

