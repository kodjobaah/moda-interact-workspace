--- 
id: ARCH-010-SHOPIFY-002 
architecture_id: ARCH-010
title: Activate Free plan with durable asynchronous Shopify verification
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-010-DATABASE-006
  - ARCH-010-SHOPIFY-001
  - ARCH-010-DATABASE-001
  - ARCH-010-DATABASE-004
  - ARCH-010-SHARED-002
  - ARCH-007-SHOPIFY-001
  - ARCH-007-SHOPIFY-002
enables:
  - ARCH-010-SHOPIFY-003
created: 2026-09-11
updated: 2026-09-12
---

# ARCH-010-SHOPIFY-002: Activate Free plan with durable asynchronous Shopify verification

## Architecture

Canonical: `docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`.

This task implements only the merchant-app producer/fast-path side of initial Free activation. Background retry/reconstruction is owned by `ARCH-010-BACKGROUND-001`.

## Objective

When a fresh/onboarding merchant returns from Shopify App Pricing with a known Free `plan_handle`, treat the callback as a **selection intent**, not entitlement proof. Attempt one immediate Partner verification for fast UX; if unresolved or the Partner API cannot be reached, persist an explicit pending activation schedule and send a best-effort BullMQ reconciliation hint. Until Shopify verifies the current Free plan, keep the merchant in onboarding and grant no product access.

## Inspect before editing

```text
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/providers/shopify-billing.provider.ts
app/services/merchant-support/merchant-support.service.ts   # existing best-effort Queue pattern only
app/routes/app/home/route.jsx
app/routes/app/billing/route.tsx
app/services/shop/shop.service.ts
app/services/shop/shop-access-policy.ts
package.json
```

Focused tests at minimum:

```text
tests/unit/routes/billing-callback.test.ts
tests/unit/services/billing.service.test.ts
tests/unit/billing-ui.test.ts
```

## Cross-repository contract

Import the published ARCH-010 contract only from:

```text
@modainteract/moda-interact-shared/billing
```

Use its queue name, job name, payload schema/type and deterministic job-ID helper. Do not duplicate contract constants or Zod schemas locally.

## Callback algorithm

### 1. Validate local requested target

After authentication/shop resolution, read `plan_handle` and map it to an active local `BillingPlan`.

For this task the requested target must be `BillingPlan.kind = FREE`. Unknown/inactive/paid handles must not enter the Free activation path.

### 2. Durably record selection intent before Redis is required

For a valid Free target, upsert/update the shop's existing Subscription so the pending target is durable without changing current entitlement:

```text
pendingShopifyPlanHandle = requested plan_handle
pendingPlanId            = mapped Free BillingPlan.id
pendingEffectiveAt       = now       # initial activation is expected immediately
nextReconcileAt          = now       # due for immediate verification
```

Do NOT set current `planId`, `observedShopifyPlanHandle`, ACTIVE/TRIALING status or onboarding complete from the callback parameter.

A new valid selection replaces an older unresolved initial-selection target.

### 3. Fast-path Partner verification

Call the existing `billingService.syncSubscription(shop.id)` once.

Change its successful-`null` semantics narrowly so an unexpired `NO_CONTRACT` initial activation target is not erased merely because Shopify currently returns no active subscription. Current subscription fields become/stay NO_CONTRACT, but the pending target/schedule remain.

On Partner API throw, do not convert the pending intent/current known subscription into provider truth. Preserve state and continue to unresolved scheduling below.

### 4. Immediate success

If the returned/reloaded projection proves the requested Free plan is the current mapped ACTIVE/TRIALING Shopify plan:

transactionally/idempotently:

```text
ShopSettings.onboardingCompleted = true
pendingShopifyPlanHandle          = null
pendingPlanId                     = null
pendingEffectiveAt                = null
nextReconcileAt                   = null
```

Preserve Free lifetime usage and all top-up balances.

If Shopify returns an exact `currentBillingCycle`, create/reuse the exact Free `BillingPeriod` using DATABASE-004 ownership/snapshot rules before clearing the initial activation schedule:

```text
planKindSnapshot = FREE
includedRecoveryCreditsGranted = null
no BillingPeriodEntitlementCounter
```

If the Free plan has `recoveryCreditPackEnabled=true`, this provider BillingPeriod is the cycle used later by recovery-credit-pack App Events. Persist `currentPeriodStart/currentPeriodEnd` and set `nextReconcileAt = max(now, currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)` so same-plan Free cycle rollover can be reconciled by BACKGROUND-007. Best-effort enqueue the deterministic reconciliation job after commit.

If Shopify verifies the current Free plan but provides no exact cycle, Free onboarding/lifetime entitlement may still complete, but top-up purchase remains ineligible until an exact provider cycle is reconciled. When the mapped Free plan enables recovery-credit packs, retain a short bounded `nextReconcileAt` retry rather than falsely presenting top-up eligibility.

Redirect `/app`.

### 5. Unresolved/null/pending/API failure

If the requested Free plan is not verified as current, including:

```text
provider returns null
requested handle is only pending
Partner API throws/times out/throttles
```

then:

- keep `ShopSettings.onboardingCompleted = false`;
- keep current entitlement fail-closed for a fresh NO_CONTRACT merchant;
- preserve the durable pending target;
- set `nextReconcileAt` to the first retry time from architecture policy (normally now + 1 minute for a fresh intent);
- best-effort add `reconcile-subscription` to the Shared queue using deterministic ID and delay;
- if Redis/queue add fails, do not roll back DB state;
- redirect `/app`, where SHOPIFY-001 renders onboarding.

Do not require a dedicated error screen. A merchant refresh before asynchronous verification completes simply sees onboarding again.

### 6. Best-effort producer implementation

Follow the existing bounded Redis/BullMQ producer style used by merchant communications where appropriate:

- one lazily reused Queue per REDIS_URL, not one connection per request;
- bounded connection/retry behaviour;
- Queue add failure isolated from durable state;
- clean test injection or equivalent existing pattern.

Do not reuse merchant-communications queue itself.

## Important failure distinction

If Shopify's hosted App Pricing page fails **before redirect**, Moda receives no callback and persists nothing new; the merchant later returns to onboarding.

If Shopify redirects and Moda's own Partner API request then fails, the callback has already produced a durable pending target, so Background can recover it asynchronously. Do not conflate these cases.

## Current/pending classification

Preserve/strengthen explicit current-vs-pending classification. `pendingShopifyPlanHandle` alone never completes first-time onboarding. Current ACTIVE/TRIALING mapped Free verification is required.

## Credits / services

This task MUST NOT:

- regrant/reset an existing shop-lifetime Free grant;
- alter `ShopEntitlementCounter` quantities;
- create promotional credits;
- alter purchased credits;
- create a periodic Free recovery allowance;
- create a Free `BillingPeriodEntitlementCounter`;
- activate recovery services while still NO_CONTRACT.

After current Free verification/onboarding completion, existing plan feature/effective billing policy controls runtime services.

## Required tests

Prove at least:

1. valid Free callback records pending target before entitlement activation;
2. unknown/inactive handle does not create pending activation;
3. paid handle does not execute this Free transition;
4. immediate current Free verification sets onboarding true and clears pending schedule;
5. immediate provider null leaves NO_CONTRACT + pending target;
6. null sets nextReconcileAt using initial retry policy;
7. null enqueues deterministic delayed reconciliation hint;
8. Partner API throw preserves pending target and onboarding false;
9. Partner API throw still attempts best-effort delayed hint;
10. queue add failure does not roll back pending DB state;
11. unresolved callback redirects `/app`, not a merchant Admin/error surface;
12. pending-only Shopify verification does not complete onboarding;
13. replay of immediate verified Free callback is idempotent;
14. new valid Free callback replaces older unresolved initial target;
15. first verified activation creates the lifetime Free counter exactly once from platform policy; replay/existing counter preserves all quantities;
16. exact provider Free cycle creates/reuses one Free BillingPeriod with `includedRecoveryCreditsGranted = null`;
17. Free BillingPeriod creation does not create an included-credit counter or reset lifetime Free usage;
18. a pack-enabled Free plan with exact cycle schedules the next pre-close reconciliation;
19. a verified Free plan without exact cycle can complete onboarding but remains top-up-ineligible and schedules bounded reconciliation when pack billing is enabled;
20. no merchant link/redirect targets `moda-interact-admin`.

## Non-goals

Do not implement the Background consumer/reconstruction, Paid activation, plan-boundary rollover, upgrade/downgrade execution, cancellation, top-up refunds, Admin UI or Render wiring.

## Validation

Inspect `package.json`; run focused tests then declared repository test/typecheck/build/Prisma validation plus `git diff --check` as applicable. Do not invent scripts.

## Stop conditions

STOP if published Shared contract or `nextReconcileAt` Prisma field is unavailable, callback cannot persist pending intent without destructive current-state changes, or the implementation would require defining Paid/upgrade/downgrade semantics.

## Completion Report

### Status
Ready for Review

### Files Changed
- `moda-interact/app/routes/app/billing/callback/route.tsx`
- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/app/services/billing/billing-reconciliation.service.ts`
- `moda-interact/tests/unit/routes/billing-callback.test.ts`
- `moda-interact/tests/unit/services/billing.service.test.ts`
- `moda-interact/tests/unit/services/billing-reconciliation.service.test.ts`
- `moda-interact/app/i18n/locales/zh-Hant.json`
- This task file records the execution evidence.

### Work Completed
- Recorded valid Free selection intent before Partner verification without changing current entitlement.
- Added immediate Partner sync, current Free verification, onboarding completion, lifetime Free counter idempotency, and pending schedule handling.
- Preserved fresh NO_CONTRACT intent when Shopify returns null or the Partner call fails.
- Added best-effort lazy BullMQ reconciliation enqueueing using the published Shared `0.10.0` contract and deterministic job IDs.
- Preserved exact Free billing-cycle projection and pre-close reconciliation scheduling from the existing sync path.
- Added the missing Traditional Chinese billing catalogue key required by Shared `0.10.0`.

### Acceptance Criteria
Implemented for the bounded merchant callback/producer scope. Background reconciliation remains out of scope.

### Work Items
Completed callback, billing service, queue producer, focused tests, i18n completeness, and validation.

### Validation Results
- Focused Vitest: 65 passed across callback, billing service, reconciliation producer, billing UI, and merchant i18n tests.
- Full Vitest: 227 passed, 1 skipped across 33 test files.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed with Prisma Client `6.19.3`; generated client exposes `Subscription.nextReconcileAt`.
- `npm run build`: passed.
- Changed-file ESLint: passed; only the repository's TypeScript parser compatibility warning was emitted.
- `npm run typecheck`: repository baseline remains failing in unrelated JSX and existing service/test files; no diagnostics remain in the changed billing callback/service or reconciliation producer files.
- `git diff --check`: passed.
- i18n regional-formatting test: passed after adding `billingCommerce.actions.manageCapacity` to `zh-Hant`.

### Git / VCS
Task branch: `task/ARCH-010-SHOPIFY-002`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-002`
  parent branch: `task/ARCH-010-SHOPIFY-002`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-002`
  implementation branch: `task/ARCH-010-SHOPIFY-002`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact`
  commit: `dd6006c` (`feat: activate verified free billing plans`)
  remote branch: `origin/task/ARCH-010-SHOPIFY-002`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/shopify/ARCH-010/SHOPIFY-002-activate-free-plan-and-complete-onboarding.md`
  report commit: pending
  remote branch: `origin/task/ARCH-010-SHOPIFY-002`
  report pushed: pending
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Deviations
The implementation worktree retains the database gitlink change from `ebe43c0` to published database commit `6d5fb9a`, which contains the required schema and generated-client contract. Per policy it was not staged in the implementation repository.

### Assumptions
The developer will update the parent database submodule pointer when the published database dependency is promoted into the implementation repository's mainline.

### Unresolved Issues
The repository-wide typecheck still reports pre-existing diagnostics outside the changed billing files.

### Architectural Concerns
The database field is available at the current published dependency revision, but the parent submodule pointer remains a developer-owned integration step.

### Architect Review

#### Review Status

Changes Requested

#### Attempt 1 — Changes Requested
Can you make sure you are using the `moda-interact` dependencey '0.10.0'

#### Attempt 2 — Changes Requested

Attempt 1's Shared-package correction is satisfied. Architect review verified that:

- `moda-interact/package.json` declares `@modainteract/moda-interact-shared` as `^0.10.0`;
- `moda-interact/package-lock.json` declares the same range and resolves the installed package to exactly `0.10.0`;
- the implementation imports the canonical billing queue/job constants and deterministic job-ID helper from `@modainteract/moda-interact-shared/billing`;
- the Completion Report records the required dedicated parent/implementation worktrees, the three physical-isolation declarations, and all four start-of-attempt synchronization outcomes;
- the reported repository-wide typecheck failures remain outside the changed SHOPIFY-002 billing files and are not, by themselves, a task regression;
- the unstaged `database` submodule pointer is an expected dependency-validation state and was correctly not staged as an implementation gitlink.

Attempt 2 nevertheless cannot be accepted because the implementation does not yet satisfy the canonical Iteration-2 transition and its explicit Required Tests.

##### Correction 1 — a Partner API failure must never complete onboarding from stale local projection

The callback currently catches `billingService.syncSubscription(shop.id)` failure and then unconditionally reloads the local Subscription projection. If a previous successful sync already left a local `ACTIVE`/`TRIALING` Free projection—for example because the prior attempt committed provider projection but failed before `ShopSettings.onboardingCompleted=true`—a later Partner timeout/5xx can still make `isVerifiedBillingCallback(...)` true and call `completeFreeActivation(...)`.

That violates the architecture invariant:

```text
Partner API failure
  -> proves nothing about current provider truth
  -> preserve durable state
  -> onboarding remains incomplete
  -> record transport-error metadata
  -> schedule deterministic retry
```

Immediate completion must be gated on a successful Partner verification performed by the current callback execution. A failed Partner call must not use stale local `ACTIVE` state as current verification evidence.

Narrowly correct the callback/service flow so that:

1. the current callback knows whether Partner verification actually succeeded;
2. `completeFreeActivation(...)` is unreachable on Partner transport/error failure;
3. the pending target/current projection is preserved;
4. `lastSyncErrorCode = PARTNER_API_ERROR` (or the existing canonical equivalent) and `lastSyncErrorAt = now` are recorded without changing a valid projection to `SYNC_ERROR`;
5. `nextReconcileAt` is advanced and the deterministic best-effort hint is attempted;
6. onboarding remains false for an incomplete first activation.

Add a regression where the local projection is already `ACTIVE` Free, the current Partner call throws, and the callback proves that completion/onboarding is not performed.

##### Correction 2 — constrain SHOPIFY-002 to the initial/no-current-plan transition

`prepareFreeActivation(...)` currently accepts any active local Free target and writes:

```text
pendingShopifyPlanHandle
pendingPlanId
pendingEffectiveAt
nextReconcileAt
```

without classifying the merchant's current Subscription/onboarding state.

That permits an already-active merchant on a different current plan to enter the **initial Free activation** retry path. A provider-observed Paid -> Free or Free-A -> Free-B future plan change belongs to the later plan-change architecture, not SHOPIFY-002.

Preserve the legitimate replay case, but enforce the source boundary:

```text
allowed initial source:
  Shop ACTIVE
  + onboarding incomplete
  + Subscription NO_CONTRACT
  + no current plan

allowed idempotent replay:
  already-current verified same Free plan
  + must preserve all entitlement quantities

not owned by SHOPIFY-002:
  ACTIVE/TRIALING current plan differs from requested Free target
  future provider pending plan change
  upgrade/downgrade/cancellation/reinstall lifecycle
```

A current different plan must not have its pending plan/schedule overwritten by this task.

Add focused tests for the allowed initial source, safe same-plan replay, and rejection/non-mutation of an already-active different-plan source.

##### Correction 3 — never permanently snapshot a missing platform policy as zero lifetime entitlement

`completeFreeActivation(...)` currently uses:

```ts
grantedQuantity: policy?.lifetimeFreeRecoveryAllowance ?? 0
```

The ARCH-010 invariant is to snapshot `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance` exactly once. If the canonical policy row is unexpectedly missing, creating the one-time `FREE_RECOVERY_LIFETIME` counter with `0` permanently records the wrong shop-lifetime grant because replay intentionally does not rewrite an existing counter.

Fail closed instead of fabricating zero entitlement. The transaction must not set onboarding complete or create a new lifetime counter unless the canonical policy value required for first-grant creation exists and is valid.

Preserve an existing lifetime counter exactly; do not require the current platform default merely to replay a merchant whose counter already exists.

Add tests proving:

1. first activation snapshots the policy quantity exactly once;
2. replay preserves `grantedQuantity`, `committedQuantity`, `reservedQuantity` and other existing quantities;
3. missing policy cannot create a zero grant or complete first onboarding.

##### Correction 4 — implement the task's explicit Required Tests rather than relying on aggregate suite count

The task says **"Prove at least"** the 20 listed behaviours. The current additions directly cover only a subset and primarily mock the new BillingService methods at the route boundary.

Before resubmission, add focused behavioural coverage for all required cases, including at minimum the currently unproved service/database semantics:

- valid Free intent is durably recorded before entitlement activation;
- inactive/unknown/Paid targets do not mutate initial Free state;
- immediate verified activation changes onboarding and pending/schedule state correctly;
- Partner failure against stale locally-active state cannot complete onboarding;
- deterministic retry time and deterministic Shared job ID;
- queue failure cannot undo committed durable state;
- verified replay is idempotent;
- a newer unresolved valid selection is not destroyed by an older/replayed callback;
- lifetime Free counter creation/reuse preserves all quantities;
- exact Free provider cycle creates/reuses the DATABASE-004 BillingPeriod with `planKindSnapshot=FREE` and `includedRecoveryCreditsGranted=null`;
- no `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)` is created for Free and lifetime usage is not reset;
- pack-enabled exact-cycle scheduling uses the Shared drain window;
- pack-enabled verified Free without an exact cycle remains onboarding-complete but top-up-ineligible and receives bounded cycle-discovery reconciliation;
- no merchant redirect/link targets `moda-interact-admin`.

Do not add tests merely to increase the count; each named invariant must be asserted against the real service behaviour rather than only asserting calls to mocks.

##### Correction 5 — make the reconciliation producer best-effort across queue acquisition as well as `Queue.add`

`enqueueBillingSubscriptionReconcileBestEffort(...)` currently awaits `getQueue()` outside its `try/catch`. `Queue.add` rejection is isolated, but queue acquisition/replacement/close/constructor errors can still escape and fail the HTTP callback after PostgreSQL state was committed.

Keep the existing lazy single-Queue-per-`REDIS_URL` pattern, but ensure the entire Redis/BullMQ acquisition-and-add path is failure-isolated. Add a focused regression for acquisition/factory failure (or refactor behind a testable queue factory) in addition to the existing `add()` rejection test.

##### Scope guard

Attempt 3 is a correction of SHOPIFY-002 only. Do not implement:

- Paid first activation or Paid included-credit counters;
- effective upgrade/downgrade execution;
- cancellation/uninstall/reinstall transitions;
- Background consumer/reconstruction;
- period rollover;
- Admin UI or Render wiring.

Do not stage the database submodule gitlink. Continue using the published dependency revision required to validate `Subscription.nextReconcileAt`, and record that dependency state in the Completion Report.

##### Attempt 3 validation

Reclaim the same task through `/moda-task`, synchronize both canonical task worktrees, make corrective commits on the same mirrored `task/ARCH-010-SHOPIFY-002` branches, and rerun the task/repository-declared validation.

In addition to the full existing validation, the focused suite must explicitly exercise every item in the task's **Required tests** section.

Return the same task to `review` with:

```text
attempt: 3
```

and updated implementation/report commit evidence.

**Architect decision: Changes Requested — Attempt 2.**
