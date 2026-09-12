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
claimed_at: 2026-09-12T00:30:00Z
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
In Progress.

### Files Changed
- No implementation files changed.
- This task file records the blocker and execution evidence.

### Work Completed
- Established and synchronized the resolver-authoritative parent and implementation worktrees.
- Verified `status: ready`, `assigned_agent: moda_app`, `execution_mode: agent`, and all seven explicit dependencies as `complete` before claiming.
- Claimed the task with normalized executor `copilot` and published the parent claim commit.
- Inspected the existing callback and billing service only far enough to confirm the requested Free intent would require the missing Shared contract.

### Validation Results
- Resolver: passed; task was materialized, ready, agent-executed, and routed to `moda_app`.
- Dependency gate: passed for `ARCH-010-DATABASE-006`, `ARCH-010-SHOPIFY-001`, `ARCH-010-DATABASE-001`, `ARCH-010-DATABASE-004`, `ARCH-010-SHARED-002`, `ARCH-007-SHOPIFY-001`, and `ARCH-007-SHOPIFY-002`; all were `complete`.
- Worktree synchronization: passed for both canonical task worktrees; both were clean and current with `origin/main`.
- Shared contract inspection: blocked. Installed `@modainteract/moda-interact-shared@0.7.4` exposes only the ARCH-007 billing symbols from `dist/billing.d.ts`; it does not export the ARCH-010 reconciliation queue name, job name, payload schema/type, or deterministic job-ID helper required by this task.
- No focused application tests were run because the task stop condition forbids implementing a competing local contract.
- Claim-only `git diff --check`: passed.

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
  implementation source changes: none
  remote branch: `origin/task/ARCH-010-SHOPIFY-002`
  branch pushed: yes; no implementation commit was created because execution is blocked before implementation

Parent workspace:
  task file: `docs/decisions/shopify/ARCH-010/SHOPIFY-002-activate-free-plan-and-complete-onboarding.md`
  claim commit: `a57f99e`
  remote branch: `origin/task/ARCH-010-SHOPIFY-002`
  claim pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Architectural Concerns
`ARCH-010-SHARED-002` is marked complete, but the current `moda-interact` dependency resolves to Shared `0.7.4`, whose published `billing` entrypoint lacks the ARCH-010 subscription-reconciliation contract. The missing contract must be published and consumed from `@modainteract/moda-interact-shared/billing` before this task can safely implement queue publication. This agent did not create a local replacement.

### Architect Review
Pending.

#### Attempt 1 — Changes Requested
Can you make sure you are using the `moda-interact` dependencey '0.10.0'
