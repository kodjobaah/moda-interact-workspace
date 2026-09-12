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
status: in_progress
priority: 40
executor: copilot
claimed_at: 2026-09-12T00:00:00Z
attempt: 6
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

Ready for Review.

Attempt 6 correction checklist:

- Added ordered `ShopSettings` then `Subscription` row locks to prepare, sync,
  and completion transactions without holding locks across Partner I/O.
- Preserved the exact unresolved onboarding selection through provider-null and
  provider-active syncs; only a successful completion may consume it.
- Required completion to match the current requested Free plan and exact pending
  target while onboarding is incomplete, preventing an older callback from
  completing over newer Free-B intent.
- Added direct service and callback regressions for the older-callback loser,
  stale provider pending data, lock transaction doubles, and no periodic Free
  entitlement counter creation.

### Status
Ready for Review

### Files Changed
- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/app/routes/app/billing/callback/route.tsx`
- `moda-interact/tests/unit/services/billing.service.test.ts`
- `moda-interact/tests/unit/routes/billing-callback.test.ts`
- This task file records the Attempt 6 execution evidence.

### Work Completed
- Retained all prior Attempt 1 through Attempt 5 corrections, including Shared
  billing contract `@modainteract/moda-interact-shared@0.10.0`, Partner-success
  gating, canonical transport errors, durable retries, best-effort queue
  acquisition/add, source-state classification, atomic lifetime-counter
  creation, exact Free-period snapshots, and merchant `/app` redirects.
- Serialized initial Free state classification with the required database lock
  order and made pending-token consumption authoritative inside completion.
- Kept lifetime and purchased quantities unchanged and avoided any periodic Free
  entitlement counter.

### Acceptance Criteria
Implemented for the bounded merchant callback/producer scope. Background
reconciliation, Paid plans, plan changes, Admin, and infrastructure remain out of scope.

### Work Items
Completed callback, billing service, queue producer, focused tests, i18n completeness, and validation.

### Validation Results
- Focused Vitest: 71 passed across BillingService, billing callback,
  reconciliation producer, and billing UI suites.
- Full Vitest: 245 passed, 1 skipped across 33 test files.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed with Prisma Client `6.19.3`; generated client exposes `Subscription.nextReconcileAt`.
- `npm run build`: passed.
- Changed-file ESLint: passed; only the repository TypeScript parser compatibility warning was emitted.
- `npm run typecheck`: repository baseline remains failing in unrelated existing
  files; no diagnostics were reported in the changed billing production/test files.
- `git diff --check`: passed.
- Focused coverage includes the explicit no-`moda-interact-admin` redirect/link assertion.

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
  correction commit: `e8eb64e` (`fix: serialize free activation completion`)
  prior task commits retained: `dd6006c`, `695439d`, `99f7925`, `d3bad71`
  remote branch: `origin/task/ARCH-010-SHOPIFY-002`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/shopify/ARCH-010/SHOPIFY-002-activate-free-plan-and-complete-onboarding.md`
  claim commit: `ab220d4`
  report commit: this parent task-branch publication commit
  remote branch: `origin/task/ARCH-010-SHOPIFY-002`
  report pushed: pending publication
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Deviations
The implementation worktree retains the pre-existing database gitlink change from
`ebe43c0` to published database commit `6d5fb9adf2e5c1fb28333b330dd183c9cda41550`,
which provides the required schema and generated-client contract. Per policy it
was not staged in the implementation repository.

### Assumptions
The developer will update the parent database submodule pointer when the published database dependency is promoted into the implementation repository's mainline.

### Unresolved Issues
The repository-wide typecheck remains a documented pre-existing baseline failure
in unrelated files; changed billing files have no reported diagnostics.

### Architectural Concerns
The database field is available at the published dependency revision, while the
parent submodule pointer remains a developer-owned integration step.

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

#### Attempt 3 — Changes Requested

Attempt 3 correctly addresses several Attempt-2 defects:

- completion is now gated on successful Partner verification from the current callback execution;
- Partner transport failure records `PARTNER_API_ERROR` and cannot complete onboarding from a stale local ACTIVE/TRIALING projection;
- missing/invalid `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance` no longer fabricates a zero lifetime grant;
- BullMQ queue acquisition/construction and `Queue.add` failures are contained inside the best-effort producer boundary;
- Shared billing contract usage remains on `@modainteract/moda-interact-shared@0.10.0`;
- worktree-isolation and start-of-attempt synchronization evidence is present.

The task is still not acceptable because the explicit Required Tests / idempotency correction from Attempt 2 was not completed, and static review of the untested service methods exposes three correctness gaps.

##### Correction 1 — enforce the Iteration-2 source state even when the Subscription row is absent

`prepareFreeActivation(...)` currently treats:

```ts
!currentSubscription
```

as sufficient for initial activation, without also requiring:

```text
ShopSettings.onboardingCompleted = false
```

The binding Iteration-2 source state requires onboarding to be incomplete. A shop with `onboardingCompleted=true` and an unexpectedly absent Subscription must not silently re-enter the first-activation transition.

Narrow the source classification so initial activation requires onboarding incomplete whether the Subscription is absent or is an explicit `NO_CONTRACT + no current plan` row.

Keep same-plan verified replay allowed.

Add direct service tests proving:

1. fresh/no-subscription + onboarding incomplete is accepted;
2. fresh `NO_CONTRACT + no current plan` + onboarding incomplete is accepted;
3. no-subscription + onboarding already complete is rejected without mutation;
4. ACTIVE/TRIALING different-plan state is rejected without mutation;
5. verified same-Free replay remains allowed.

##### Correction 2 — make first lifetime-grant creation concurrency-idempotent

`completeFreeActivation(...)` now performs:

```text
findUnique(FREE_RECOVERY_LIFETIME)
  -> if missing, read policy
  -> create counter
```

Sequential replay is safe, but concurrent verified callbacks can both observe the counter as missing and race on the database unique constraint `(shopId, counter)`. One request can therefore fail instead of behaving idempotently.

The architecture requires the first verified activation to `create/reuse` the shop-lifetime counter transactionally and idempotently.

Use a race-safe create/reuse mechanism that:

- preserves an existing counter and all of its quantities unchanged;
- snapshots the platform policy only when a counter genuinely needs to be created;
- does not require the policy merely to replay a shop that already has a counter;
- tolerates concurrent first-activation attempts without producing a user-visible uniqueness failure;
- sets onboarding complete only after the counter exists/reuses successfully.

Add direct service coverage for first creation, existing-counter replay with non-zero committed/reserved/refunding/version state, missing-policy fail-closed behaviour, and a concurrent/create-race equivalent.

##### Correction 3 — an older in-flight callback must not erase a newer unresolved local selection

Attempt 2 explicitly required:

```text
a newer unresolved valid selection is not destroyed by an older/replayed callback
```

The current generic `syncSubscription(...)` can still overwrite the locally durable pending target from provider data without considering whether the local pending selection was written by a newer callback.

Example:

```text
callback A records pending Free-A
callback B records newer pending Free-B
callback A continues and provider still reports Free-A/current with no pending update
syncSubscription writes provider pending=null
=> newer durable Free-B selection can be cleared
```

The durable local selection exists specifically to survive provider propagation lag, so an older callback must not destroy a newer local intent merely because the Partner response does not yet expose it.

Preserve the newest unresolved local initial-selection target unless the provider response actually verifies that target as current or provides authoritative pending state that supersedes it. Use the narrowest mechanism appropriate to the existing service; do not design later upgrade/downgrade execution in this task.

Add a focused race/replay test proving that a newer Free selection survives completion of an older callback/sync attempt.

##### Correction 4 — finish the task's explicit Required Tests against real service behaviour

The task says **"Prove at least"** 20 named behaviours. Attempt 3 added regressions for stale Partner projection and queue acquisition, but there is still no direct test invocation of either:

```text
BillingService.prepareFreeActivation(...)
BillingService.completeFreeActivation(...)
```

Consequently the current focused suite still does not prove several mandatory semantics, including:

- durable pending intent before entitlement activation;
- inactive/unknown/Paid target non-mutation at the service/database boundary;
- exact source-state classification;
- same-plan replay;
- replacement/preservation of unresolved selection intent;
- one-time lifetime counter snapshot and quantity preservation;
- missing-policy fail-closed behaviour;
- exact Free BillingPeriod snapshots (`planKindSnapshot=FREE`, `includedRecoveryCreditsGranted=null`);
- absence of a Free `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)`;
- preservation of lifetime usage across Free cycle projection;
- exact-cycle pre-close scheduling using the Shared drain-window constant;
- verified pack-enabled Free without a cycle completing onboarding while remaining top-up-ineligible and retaining bounded reconciliation.

Add focused behavioural tests for every item in the canonical `Required tests` section. Route tests may mock orchestration boundaries, but the service/database invariants must be asserted against the actual BillingService methods rather than inferred from aggregate suite counts.

##### Validation / workflow

This remains the same task. Do not create a new correction task and do not stage the database submodule gitlink.

Reclaim with `/moda-task`; the next valid claim is:

```text
attempt: 4
```

Run the task-declared focused/full validation and return the same mirrored branches to `review` with updated implementation/report evidence.

Repository-wide pre-existing typecheck/lint diagnostics outside the changed task files remain non-blocking if they are unchanged and correctly documented.

**Architect decision: Changes Requested — Attempt 3.**

#### Attempt 4 — Changes Requested

Attempt 4 adds useful direct `BillingService` coverage and keeps the previously
accepted Partner-failure, platform-policy and best-effort Queue corrections. It also
adds assertions for Free BillingPeriod snapshot fields and pack-enabled scheduling.

Attempt 4 cannot be accepted because the three correctness defects identified in the
Attempt-3 architect decision remain in the production implementation.

##### Correction 1 — absent Subscription must still require onboarding incomplete

`prepareFreeActivation(...)` still classifies:

```ts
const isInitialActivation = !currentSubscription ||
  (
    currentSubscription.status === SubscriptionProjectionStatus.NO_CONTRACT &&
    currentSubscription.planId === null &&
    !currentSubscription.observedShopifyPlanHandle &&
    settings?.onboardingCompleted !== true
  );
```

The `!currentSubscription` branch bypasses `ShopSettings.onboardingCompleted`.

Therefore:

```text
Subscription row absent
+ onboardingCompleted = true
```

can still re-enter first Free activation and create a new pending initial-selection
schedule.

The Iteration-2 source boundary requires onboarding incomplete for the fresh/no-current
source regardless of whether the Subscription row is absent or an explicit
`NO_CONTRACT` row.

Correct the predicate and add the exact regression required by Attempt 3:

```text
no Subscription
+ onboardingCompleted = true
=> prepareFreeActivation returns null
=> no Subscription upsert/mutation
```

Keep:

- fresh/no-subscription + onboarding incomplete allowed;
- NO_CONTRACT/no-current-plan + onboarding incomplete allowed;
- verified same-Free replay allowed;
- ACTIVE/TRIALING different-plan rejected.

##### Correction 2 — first lifetime grant is still not concurrency-idempotent

`completeFreeActivation(...)` still performs:

```text
findUnique(FREE_RECOVERY_LIFETIME)
-> policy lookup
-> create
```

with no race-safe create/reuse handling.

Two concurrent verified callbacks can both observe no counter and both attempt
`create`; one can fail on the unique `(shopId, counter)` invariant rather than replay
idempotently.

Replace this with an atomic/race-safe create-or-reuse design that:

- snapshots `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance` only when a counter
  genuinely needs first creation;
- preserves every existing counter quantity/state on replay;
- does not require current policy merely to reuse an existing counter;
- tolerates concurrent first activation without surfacing a uniqueness failure;
- completes onboarding only after a valid counter exists/reuses successfully.

Add a focused race/concurrent-create regression. Sequential
`findUnique -> create` test coverage is not sufficient.

##### Correction 3 — generic sync still destroys newer unresolved local selection intent

The current provider-active branch of `syncSubscription(...)` still writes:

```ts
pendingShopifyPlanHandle: providerSubscription.pendingPlanHandle,
pendingPlanId: pendingPlan?.active ? pendingPlan.id : null,
pendingEffectiveAt: providerSubscription.pendingPlanHandle
  ? providerSubscription.currentPeriodEnd
  : null,
```

without protecting a newer durable initial-selection target.

The Attempt-3 race therefore still exists:

```text
callback A records Free-A
callback B records newer Free-B
callback A's Partner read returns current Free-A / provider pending null
syncSubscription from A writes pending null
=> newer Free-B intent is erased
```

Preserve the newest unresolved local initial-selection intent unless current provider
truth actually verifies that target or authoritative provider pending state supersedes
it. Keep this correction bounded to the first-activation intent owned by SHOPIFY-002;
do not implement general upgrade/downgrade execution.

Add the exact older-callback/newer-selection race regression.

##### Correction 4 — complete the canonical Required Tests, not only the direct-method subset

Attempt 4 improves coverage but the canonical task still requires all 20 named
behaviours to be proved.

At minimum the next attempt must explicitly cover the still-unproved/partially-proved
items:

- no-Subscription + onboarding-complete source rejection;
- concurrent first lifetime-counter creation/reuse;
- newer unresolved Free selection surviving an older callback/sync;
- a new valid Free callback replacing an older unresolved initial target;
- exact Free BillingPeriod creation/reuse without creating
  `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)`;
- lifetime usage remaining unchanged while the Free BillingPeriod is created/reused;
- verified pack-enabled Free with no exact cycle:
  onboarding completes, lifetime entitlement is preserved/created once,
  top-up eligibility remains false because no exact period exists,
  and bounded reconciliation remains scheduled;
- explicit proof that no merchant redirect/link introduced by this task targets
  `moda-interact-admin`.

Tests must assert the actual service/database behaviour where the invariant belongs.
Do not satisfy these with route mocks alone.

##### Completion Report / validation evidence

The task frontmatter correctly records `attempt: 4`, but the Completion Report still
labels its checklist as "Attempt 3" and describes earlier validation/report state.

For Attempt 5, refresh the Completion Report so it clearly identifies the actual
Attempt-5 corrections, current implementation commit(s), current parent report commit,
and current focused/full validation outcomes. Preserve historical Architect Review
sections unchanged.

The reported repository-wide pre-existing typecheck issues remain non-blocking if
unchanged and outside the corrected task files.

##### Workflow / scope

This remains the same SHOPIFY-002 task and the same mirrored task branches.

Do not:

- stage the database gitlink;
- implement Background consumer/reconstruction;
- implement Paid first activation;
- implement upgrade/downgrade/cancellation/reinstall execution;
- add Admin or infrastructure work.

Reclaim through `/moda-task`. The next valid claim is:

```text
attempt: 5
```

**Architect decision: Changes Requested — Attempt 4.**

#### Attempt 5 — Changes Requested

Attempt 5 correctly satisfies three substantial parts of the Attempt-4 correction:

- `prepareFreeActivation(...)` now requires `ShopSettings.onboardingCompleted != true`
  for the absent-Subscription initial source as well as the explicit
  `NO_CONTRACT + no current plan` source;
- first `FREE_RECOVERY_LIFETIME` creation is now race-safe at the database boundary
  through `INSERT ... SELECT PlatformBillingPolicy.lifetimeFreeRecoveryAllowance ...
  ON CONFLICT ("shopId","counter") DO NOTHING`, followed by an exact counter re-read;
  an existing counter is not rewritten and missing policy remains fail-closed;
- `syncSubscription(...)` now preserves a newer local Free-B intent in the tested
  case where an older Free-A Partner response reports current Free-A and no provider
  pending handle;
- the new direct service tests cover absent-Subscription/onboarding-complete rejection,
  replacement of an older local initial target, concurrent lifetime-counter creation,
  and the Free-A/current + Free-B/local-pending case;
- build, Prisma generate/validate, changed-file ESLint and `git diff --check` are
  reported passing; the repository-wide 163 typecheck diagnostics remain outside the
  changed files and are not the reason for this decision;
- the database gitlink remains unstaged.

Attempt 5 still cannot be accepted because the newer-selection ordering invariant is
not protected **end-to-end** across `prepareFreeActivation -> syncSubscription ->
completeFreeActivation`. The new test stops after `syncSubscription`, before the code
that currently destroys the preserved newer intent.

##### Correction 1 — keep one durable initial-selection token until successful completion

Files:

```text
app/services/billing/billing.service.ts
app/routes/app/billing/callback/route.tsx
tests/unit/services/billing.service.test.ts
tests/unit/routes/billing-callback.test.ts
```

For an onboarding-incomplete merchant, the pending fields are the durable identity of
the latest initial selection:

```text
pendingShopifyPlanHandle
pendingPlanId
pendingEffectiveAt
nextReconcileAt
```

Do not clear or replace that local token merely because an older Partner request
returns current/pending provider data.

Implement the following exact rule inside `syncSubscription(...)`:

```text
hasUnresolvedInitialSelection =
  ShopSettings.onboardingCompleted = false
  AND pendingShopifyPlanHandle != null
  AND pendingPlanId != null
```

When `hasUnresolvedInitialSelection` is true:

```text
provider current handle == local pending handle
    -> project provider current plan/status/cycle truth
    -> KEEP the exact local pendingShopifyPlanHandle
    -> KEEP the exact local pendingPlanId
    -> KEEP the exact local pendingEffectiveAt
    -> KEEP the exact local nextReconcileAt
       until completeFreeActivation consumes the token

provider current handle != local pending handle
    -> project provider current truth as appropriate
    -> KEEP the exact local pending target/schedule

provider pending handle is null
    -> KEEP local pending target/schedule

provider pending handle is some other handle
    -> KEEP local pending target/schedule
       (Partner pending data has no ordering/version metadata proving that an older
        response supersedes the newer callback selection)
```

Only when there is **no** unresolved onboarding selection may the generic provider
pending projection replace the local pending fields.

Apply the same preservation rule to the provider-null branch. A transient/provider-null
read must not erase an onboarding-incomplete pending target merely because a previous
sync partially projected `ACTIVE`/`TRIALING`.

This is intentionally limited to the initial/onboarding state. Do not implement
general upgrade/downgrade ordering here.

##### Correction 2 — serialize prepare/sync/complete state classification

The remaining race cannot be fixed by an extra JavaScript `if` alone.

Example still possible in Attempt 5:

```text
A prepare Free-A
A Partner request starts
B prepare Free-B and becomes the newer local selection
A Partner returns current Free-A
A sync preserves Free-B
A route reloads ACTIVE Free-A + pending Free-B
A isVerifiedBillingCallback returns true
A completeFreeActivation("Free-A") clears all pending fields
=> Free-B is lost and onboarding completes under the older selection
```

There is also a smaller read/write window where `prepareFreeActivation` can classify
`NO_CONTRACT`, another transaction completes onboarding, and the stale prepare then
writes a pending target onto the now-completed Subscription.

Use PostgreSQL row locking in the existing Prisma transactions. Do not add a schema
field or a new database task.

Add one small helper in `billing.service.ts` (name may differ, behaviour may not):

```ts
async function lockInitialFreeActivationState(
  transaction: Prisma.TransactionClient,
  shopId: string,
) {
  await transaction.$queryRaw(Prisma.sql`
    SELECT "shopId"
    FROM "shopify"."ShopSettings"
    WHERE "shopId" = ${shopId}
    FOR UPDATE
  `);

  await transaction.$queryRaw(Prisma.sql`
    SELECT "id"
    FROM "billing"."Subscription"
    WHERE "shopId" = ${shopId}
    FOR UPDATE
  `);
}
```

Required lock order is always:

```text
1. ShopSettings
2. Subscription
```

Use that order in `prepareFreeActivation(...)` and `completeFreeActivation(...)`
before classifying source/onboarding/pending state.

In the provider-null and provider-active `syncSubscription(...)` write transactions,
lock the existing Subscription row with `FOR UPDATE` **before** reading the existing
Subscription used to decide pending preservation.

Do not hold these locks across the Partner network call. The Partner request remains
outside the DB transaction.

##### Correction 3 — completion must consume only the exact current initial selection

After `syncSubscription(...)`, immediate completion is permitted only when:

```text
provider verification from this callback succeeded
current Subscription status IN (ACTIVE, TRIALING)
current plan is the requested active Free plan
observedShopifyPlanHandle == requestedPlanHandle
```

and, for `ShopSettings.onboardingCompleted = false`:

```text
pendingShopifyPlanHandle == requestedPlanHandle
pendingPlanId == current planId
pendingEffectiveAt != null
```

If onboarding is already complete and the same Free plan is current, the existing
same-plan replay remains allowed even when the pending fields are null.

Inside `completeFreeActivation(...)`, after acquiring the locks from Correction 2:

1. load `ShopSettings` and Subscription+plan;
2. if onboarding is incomplete and the exact pending target is not the requested
   current Free plan, return `false` **without**:
   - creating/reusing the lifetime counter,
   - changing ShopSettings,
   - clearing pending fields;
3. if the exact target is valid, perform the existing race-safe lifetime counter
   ensure;
4. set `onboardingCompleted = true`;
5. clear the consumed pending target;
6. preserve the already-computed `nextReconcileAt` for a pack-enabled Free plan,
   otherwise clear it.

Also strengthen `isVerifiedBillingCallback(...)` so an onboarding-incomplete callback
is not considered immediately completable when the reloaded projection visibly
contains a different pending target. The service-level locked check remains the
authoritative protection; the route check is only an early guard.

##### Correction 4 — add the two missing newer-selection race regressions

The current Attempt-5 regression proves only:

```text
local Free-B
provider current Free-A
provider pending null
syncSubscription
=> Free-B survives
```

Add these exact tests.

**Test A — old callback cannot complete over newer target**

Arrange:

```text
ShopSettings.onboardingCompleted = false
Subscription after older Partner sync:
  status = ACTIVE
  planId = Free-A
  observedShopifyPlanHandle = Free-A
  pendingShopifyPlanHandle = Free-B
  pendingPlanId = Free-B
```

Call:

```text
completeFreeActivation(shopId, Free-A)
```

Assert:

```text
result = false
onboardingCompleted remains false
Free-B pending fields remain unchanged
FREE_RECOVERY_LIFETIME is not created by the losing callback
```

**Test B — stale provider pending does not overwrite newer local target**

Arrange:

```text
local pending = Free-B
ShopSettings.onboardingCompleted = false
older Partner response:
  current = Free-A
  pending = Free-A (or another non-B handle)
```

Call `syncSubscription(...)`.

Assert:

```text
pendingShopifyPlanHandle remains Free-B
pendingPlanId remains Free-B id
pendingEffectiveAt unchanged
nextReconcileAt unchanged
```

Do not weaken the existing provider-pending projection tests for normal already
onboarded subscriptions.

##### Correction 5 — explicitly prove Required Tests 17, 19 and 20

The task says `Prove at least` the 20 named behaviours. The source behaviour is mostly
present, but Attempt 5 still does not directly assert these three acceptance points.

Add deterministic focused tests:

**Required Test 17 — no periodic Free counter and no lifetime reset**

For an exact provider Free cycle:

```text
existing FREE_RECOVERY_LIFETIME:
  grantedQuantity = 5
  committedQuantity = 3
  reservedQuantity = 1
  refundingQuantity = 1
  version = N
```

After `syncSubscription(...)` and replay of the exact period, assert:

```text
BillingPeriod create snapshot:
  planKindSnapshot = FREE
  includedRecoveryCreditsGranted = null

no BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS) create/upsert occurs

FREE_RECOVERY_LIFETIME values remain exactly:
  5 / 3 / 1 / 1 / N
```

If the unit-test database mock does not currently expose
`billingPeriodEntitlementCounter`, add a spy-only mock member and assert it is not
called. Do not add production writes merely to make the test observable.

**Required Test 19 — verified pack-enabled Free with no exact cycle**

Prove one coherent flow, not separate unrelated assertions:

```text
provider verifies current Free
currentPeriodStart = null
currentPeriodEnd = null
recoveryCreditPackEnabled = true
```

After sync + completion assert:

```text
ShopSettings.onboardingCompleted = true
lifetime counter exists exactly once
Subscription.billingPeriodId = null
Subscription.nextReconcileAt is bounded/non-null
recovery-credit-pack purchase remains ineligible because no exact BillingPeriod exists
```

**Required Test 20 — no merchant route/link targets Moda Admin**

Add a focused static/source or route-output assertion covering the merchant billing
callback/selection surfaces changed by this task:

```text
must not contain or redirect to "moda-interact-admin"
```

`admin.shopify.com/.../pricing_plans` is Shopify hosted pricing and remains valid.

##### Correction 6 — normalize the Attempt-6 Completion Report

The current Attempt-5 Completion Report is much improved, but its parent report field
still says:

```text
report commit: this parent task-branch publication commit
```

For Attempt 6, record exact immutable evidence:

```text
implementation commit: <new commit>
parent claim commit: <existing/new exact hash>
parent report/review commit: <exact hash>
database dependency revision: 6d5fb9a...
submodule gitlink staged: no
```

Keep the three physical-isolation declarations and all four synchronization outcomes.

Preserve every historical `#### Attempt N — ...` Architect Review section unchanged.

##### Attempt-6 validation

Before returning to `review`, run the repository/task-declared validation and record
the exact results:

```text
focused BillingService tests
billing callback tests
billing reconciliation producer tests
billing UI tests
full Vitest suite
npm run prisma:validate
npm run prisma:generate
npm run build
changed-file ESLint
npm run typecheck
git diff --check
```

The known repository-wide typecheck baseline may remain documented if the changed
SHOPIFY-002 files introduce no diagnostic.

##### Scope guard

Attempt 6 remains `ARCH-010-SHOPIFY-002` only.

Do not:

- add a database column/version field;
- stage or commit the database gitlink;
- implement the Background consumer/reconstruction;
- implement Paid first activation;
- implement upgrade/downgrade/cancellation/reinstall;
- implement period rollover;
- add Admin or Render/infrastructure work.

Stop and return to `moda_architect` if preserving the exact latest initial selection
would require a schema change.

Reclaim through `/moda-task`. The next valid claim is:

```text
attempt: 6
```

**Architect decision: Changes Requested — Attempt 5.**
