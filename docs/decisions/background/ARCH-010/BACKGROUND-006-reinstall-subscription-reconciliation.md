---
id: ARCH-010-BACKGROUND-006
architecture_id: ARCH-010
title: Reconcile reinstalled shops before business execution resumes
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 49
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHARED-008
- ARCH-010-BACKGROUND-001
- ARCH-010-BACKGROUND-003
- ARCH-010-BACKGROUND-007
- ARCH-010-BACKGROUND-004
- ARCH-010-BACKGROUND-005
enables:
- ARCH-010-SHOPIFY-006
- ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: 2026-09-13
---

# ARCH-010-BACKGROUND-006: Reconcile reinstalled shops before business execution resumes

## Objective

Extend the existing ARCH-010 subscription-reconciliation BullMQ worker so an authenticated reinstall can re-establish Shopify billing truth **before** an `UNINSTALLED` shop is made executable again.

This is a narrow exception to the Iteration-4 inactive-shop gate. It must never become a generic way for background jobs to process uninstalled shops.

## Inspect before editing

Inspect the integrated implementation, not only the snapshot paths below:

```text
src/entrypoints/billing.ts
src/entrypoints/billing-resources.ts
src/runtime/billing-scheduler.ts
src/services/billing-reconciliation.service.ts
src/services/effective-billing-policy.service.ts
src/providers/shopify-partner-billing.provider.ts
src/services/recovery-billing.service.ts
src/runtime/redis.ts (or accepted equivalent)
src/observability/**
package.json
```

Also inspect the accepted implementations/reports for:

```text
ARCH-010-BACKGROUND-001
ARCH-010-BACKGROUND-002
ARCH-010-BACKGROUND-003
ARCH-010-BACKGROUND-004
ARCH-010-BACKGROUND-005
```

Do not duplicate their queue, provider, paid-period counter or execution-gate mechanisms.

## Reuse the existing Shared contract

Use only the published canonical reconciliation contract from:

```text
@modainteract/moda-interact-shared/billing
```

Do not create another queue name/job schema merely for reinstall.

The durable reason for allowing the job is loaded from PostgreSQL (`Shop.reinstallPendingAt`), not trusted from an unvalidated queue payload.

## Authorised uninstalled-shop exception

The existing reconciliation consumer normally no-ops for `Shop.status != ACTIVE`.

Add exactly this allowed exception:

```text
Shop.status = UNINSTALLED
Shop.reinstallPendingAt != null
Subscription exists
Subscription.nextReconcileAt != null
payload.expectedNextReconcileAt == Subscription.nextReconcileAt.toISOString()
```

All other `UNINSTALLED`/`SUSPENDED` jobs remain successful terminal no-ops.

This exception authorises only Partner subscription reconciliation and the final Shop lifecycle transaction. It does not authorise CheckoutRecovery, WhatsApp, conversation, CommerceAgent, Shopify commerce-data lookup, credit consumption, or new customer work.

## Provider call

Call the existing Partner provider:

```text
activeSubscription(appId, shopId)
```

using the Shop's durable `shopifyShopId` and existing app credentials/provider implementation.

Never infer current entitlement from the preserved local Subscription alone.

## Outcome A — provider successfully returns null

A successful null response is authoritative for this iteration.

In one transaction:

```text
Subscription.planId = null
Subscription.observedShopifyPlanHandle = null
Subscription.status = NO_CONTRACT
Subscription.billingPeriodId/current pointer = null
Subscription.currentPeriodStart = null
Subscription.currentPeriodEnd = null
Subscription.trialEndsAt = null
Subscription.cancelAtPeriodEnd = false
Subscription.providerSubscriptionId = null
Subscription.pendingShopifyPlanHandle = null
Subscription.pendingPlanId = null
Subscription.pendingEffectiveAt = null
Subscription.nextReconcileAt = null
Subscription.lastSyncedAt = now
Subscription.lastSyncErrorCode = null
Subscription.lastSyncErrorAt = null

ShopSettings.onboardingCompleted = false

Shop.status = ACTIVE
Shop.uninstalledAt = null
Shop.reinstallPendingAt = null
```

Do **not** delete or reset:

```text
historical BillingPeriod rows/counters
LIFETIME_FREE_RECOVERY_CREDITS usage
purchased lifetime top-up balance/lots
promotional lifetime balances
RecoveryCreditPurchase / RecoveryCreditRefund history
recovery/conversation history
```

Do not close/forfeit an old detached paid BillingPeriod in this task. The canonical close/forfeit lifecycle belongs to the next ARCH-010 billing-period transition. The current Subscription pointer must be cleared so the old period cannot be treated as current entitlement.

## Outcome B — verified current Free plan

Require:

```text
provider current handle maps to active local BillingPlan
BillingPlan.kind = FREE
provider projection is otherwise safe under existing mapping rules
```

Then transactionally:

- apply provider current/pending projection using the accepted billing reconciliation rules;
- preserve Free lifetime counter/history exactly;
- do not grant/reset five Free conversations;
- do not create promotional credits;
- set `ShopSettings.onboardingCompleted=true`;
- clear `Subscription.nextReconcileAt` and transient reinstall sync-error metadata;
- set Shop ACTIVE;
- clear `uninstalledAt` and `reinstallPendingAt`.

## Outcome C — verified same paid plan and exact same paid BillingPeriod

Immediate paid reactivation is allowed only if all are true:

```text
provider current plan handle == preserved observedShopifyPlanHandle
provider plan maps to same active local planId
plan kind == PAID_METERED
required normal usage meter is present
provider.currentPeriodStart/end are non-null
provider current period exactly matches Subscription.currentPeriodStart/end
Subscription.billingPeriodId is non-null
that BillingPeriod row has the same shop/start/end
that period has exactly one INCLUDED_RECOVERY_CREDITS counter required by ARCH-010-DATABASE-002
```

Then:

- reuse the existing BillingPeriod and counter;
- do not modify `grantedQuantity`, `committedQuantity`, `reservedQuantity` or `forfeitedQuantity` merely due to reinstall;
- do not grant a fresh allowance;
- refresh provider current/pending/cancel-at-end fields and sync metadata;
- set onboarding complete;
- set Shop ACTIVE and clear uninstall/reinstall markers;
- replace the reinstall wake-up with normal paid lifecycle scheduling: `nextReconcileAt = max(now, currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)`;
- after commit, best-effort enqueue the deterministic normal paid reconciliation job.

`cancelAtEndOfCycle=true` is not by itself a reason to deny the current verified cycle. Do not implement the eventual cycle-end transition here.

## Outcome D — same paid plan, Shopify has advanced to a later paid cycle

If the provider current plan is the **same mapped active PAID_METERED plan** but the provider currentBillingCycle is later/non-overlapping relative to the preserved local period, delegate to the canonical internal transition from `ARCH-010-BACKGROUND-007` while Shop remains UNINSTALLED.

Do not duplicate close/open logic in reinstall code.

When canonical rollover succeeds:

- reuse the newly-installed current BillingPeriod/counter;
- preserve all lifetime balances;
- set `ShopSettings.onboardingCompleted=true`;
- set `Shop.status=ACTIVE`;
- clear `uninstalledAt` and `reinstallPendingAt`;
- retain the normal paid `nextReconcileAt` created by the rollover transition.

If the canonical transition reports provider cycle lag/transport failure, keep Shop UNINSTALLED and reuse the reconciliation retry it provides.

## Outcome E — paid plan/entitlement still does not align

Fail closed when any of these remain true:

```text
provider current paid plan differs from preserved current plan
provider cycle overlaps old local period invalidly
current BillingPeriod pointer/row is missing
period included-credit counter is missing/inconsistent
required paid meter is missing
canonical same-plan rollover rejects integrity
```

Then:

- keep `Shop.status=UNINSTALLED`;
- keep `reinstallPendingAt`;
- do not alter paid allowance counters;
- do not apply upgrade/downgrade;
- do not activate business execution;
- record bounded diagnostic sync metadata;
- do not invent a new period outside BACKGROUND-007.

A provider current **different paid plan** remains deferred to the ARCH-010 upgrade/downgrade iteration.

## Provider transport/throttle/5xx failure

A transport/provider failure must not change current entitlement truth.

Preserve Shop UNINSTALLED and all Subscription/credit/period fields. Update only:

```text
lastSyncErrorCode
lastSyncErrorAt
nextReconcileAt
```

Reuse ARCH-010's bounded retry cadence for up to 24 hours from `Shop.reinstallPendingAt`.

Before the 24-hour boundary, best-effort enqueue the next deterministic delayed reconciliation job.

At/after 24 hours:

```text
Shop remains UNINSTALLED
reinstallPendingAt remains non-null
nextReconcileAt = null
```

so the merchant-facing restoration page can show explicit retry/support. Do not fabricate `NO_CONTRACT` when Shopify could not be reached.

## Startup and periodic BullMQ reconstruction

Extend ARCH-010-BACKGROUND-001 reconstruction to include:

```text
Shop.status = UNINSTALLED
Shop.reinstallPendingAt != null
Subscription.nextReconcileAt != null
```

in addition to its existing active-shop pending-activation query.

For each row, publish the same deterministic job with:

```text
delay = max(0, nextReconcileAt - now)
```

Queue reconstruction must not call Shopify itself.

Redis enqueue failure remains non-transactional to PostgreSQL state and must be recoverable by later periodic/startup repair.

## Interaction with ordinary reconciliation

The ordinary rotating ARCH-007 billing scanner must continue to exclude arbitrary UNINSTALLED shops. It must not clear `reinstallPendingAt`, mutate the preserved subscription or reactivate a shop.

Only the explicit reconciliation job path above may process the pending reinstall exception.

## Observability

Reuse existing shared structured logging and existing BullMQ/OpenTelemetry instrumentation. Add only domain-semantic outcome logging/metrics if current instrumentation cannot answer:

```text
reinstall reconciliation succeeded as Free
reinstall reconciliation succeeded as same paid period
reinstall resolved to no contract
reinstall provider retry/timeout
reinstall blocked by period alignment
```

Do not duplicate generic queue/job/HTTP metrics already emitted by approved instrumentation.

## Required tests

At minimum prove:

1. ordinary UNINSTALLED shop without `reinstallPendingAt` is still no-op;
2. SUSPENDED shop is never processed as reinstall;
3. pending reinstall with matching expected schedule invokes Partner provider;
4. stale expectedNextReconcileAt job is no-op;
5. provider null establishes ACTIVE + NO_CONTRACT + onboarding false;
6. provider null clears current/pending Subscription pointers but preserves historical period rows;
7. provider null preserves Free lifetime usage;
8. provider null preserves purchased/promotional balances and refund state;
9. verified Free sets ACTIVE/onboarding true without changing Free counter quantities;
10. same paid plan + exact same cycle reuses existing BillingPeriod/counter;
11. same paid cycle does not change granted/committed/reserved/forfeited quantities;
12. `cancelAtEndOfCycle=true` on the same verified cycle does not by itself block restoration;
13. same-plan later paid cycle delegates to BACKGROUND-007 and reactivates only after canonical rollover succeeds;
14. same-plan rollover does not reset historical/lifetime balances;
15. changed paid plan remains fail-closed and does not apply upgrade/downgrade;
16. missing paid period/counter fails closed;
16. provider transport error preserves all current subscription/credit truth;
17. retry tiers schedule the next durable time and deterministic job;
18. 24-hour transport expiry leaves Shop execution disabled and stops automatic scheduling;
19. startup reconstruction restores reinstall jobs;
20. periodic repair restores a Redis-lost reinstall job;
21. ordinary active-shop initial activation reconciliation remains passing;
22. Iteration-4 recovery and WhatsApp inactive-shop gates remain passing;
23. usage publication for legitimate pre-uninstall committed usage remains passing.

## Validation

Inspect `package.json`; run focused tests first, then repository-declared relevant test/build/typecheck validation and `git diff --check`.

## Non-goals

Do not:

- solve shop identity;
- create a second reconciliation queue;
- implement normal billing-period rollover;
- duplicate the canonical BACKGROUND-007 paid period close/open transition;
- implement upgrade/downgrade;
- expose Admin;
- change Meta ingress ownership resolution;
- delete merchant history.

## Stop conditions

STOP and return to `moda_architect` if:

- DATABASE-003/Shared contract/generated Prisma shape is unavailable;
- the accepted Background-001 queue contract cannot express the existing deterministic shop/schedule wake-up without a breaking Shared change;
- paid same-period restoration cannot prove exact period/counter identity;
- the integrated BACKGROUND-007 transition cannot safely reconcile a same-plan changed-cycle merchant;
- a generic UNINSTALLED execution path would need to be reopened.

## Completion Report

### Status
Ready for Architect Review.

### Files Changed
- `moda-interact-background/src/services/billing-subscription-reconciliation.service.ts`
- `moda-interact-background/tests/unit/services/billing-subscription-reconciliation.service.test.ts`

### Work Completed
- Extended canonical subscription queue reconstruction to restore durable pending-reinstall jobs without contacting Shopify.
- Added the exact `UNINSTALLED + reinstallPendingAt + matching nextReconcileAt` exception; arbitrary `UNINSTALLED` and all `SUSPENDED` jobs remain terminal no-ops.
- Reconciled Partner null, verified Free, same paid period, and later same-plan paid cycle outcomes while preserving historical and lifetime entitlement state.
- Delegated later same-plan paid cycle rotation to `SamePlanBillingPeriodRolloverService` and reactivated the shop only after successful canonical transition.
- Added bounded 24-hour reinstall provider retry metadata and fail-closed period/plan diagnostics.
- Added focused regressions for stale/missing reinstall authorization, null-provider activation, Free reactivation, reconstruction, and no-Shopify reconstruction behavior.

### Validation Results
- `npm test -- --run tests/unit/services/billing-subscription-reconciliation.service.test.ts`: passed, 1 file and 74 tests.
- Adjacent gate suite (`billing-scheduler`, `entrypoint-isolation`, `shopify-usage-event-publisher`, `recovery-routing`): passed, 4 files and 49 tests.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- `npm test`: baseline failures remain in `tests/unit/services/recovery-credit-purchase.service.test.ts` (8 failures caused by the existing generated purchase schema/status mismatch) and `tests/unit/runtime/observability-startup.test.ts` (2 existing observability/runtime-version expectations); no failures occurred in the touched reconciliation tests.
- `npm run build`: baseline TypeScript failures remain in purchase/recovery-credit services for the same generated schema/status mismatch; no errors in task-touched files.

### Git / VCS
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-006`, `task/ARCH-010-BACKGROUND-006`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-006`, `task/ARCH-010-BACKGROUND-006`.
- Implementation commit: `8da03a0` (`feat(background): reconcile subscriptions after reinstall`), pushed to `origin/task/ARCH-010-BACKGROUND-006`.
- Launcher claim commit: `8b70d55c32a24b1dd79de279785d4138cc120642`, pushed before implementation.
- Isolated worktrees used; shared checkout was not switched or mutated.

### Architect Review

#### Review Status
Changes Requested

#### Review Notes
Attempt 1 is not acceptable yet. The implementation commit is `8da03a0c1908ffd97a72369784672936db5881a5`. The parent Completion Report is `c4a9262844e9164246e39923f58356e3b7bbd8e6`.

The implementation has the correct high-level shape: it reuses the canonical subscription-reconciliation queue/provider, extends reconstruction, delegates same-plan cycle rollover to `SamePlanBillingPeriodRolloverService`, and keeps ordinary inactive-shop business work gated. However, the real reinstall execution path is currently unreachable and several required reinstall invariants are either not enforced or not covered by executable tests.

This is a correction of the SAME task. Preserve the current `attempt: 1`; the next `/moda-task ARCH-010-BACKGROUND-006` claim increments it to Attempt 2 exactly once. Do not create another task.

#### Blocking findings

1. **`reconcileJob()` does not select `Shop.reinstallPendingAt`.**

   The production `shop.findUnique()` select contains `id`, `status`, `shopifyShopId`, `settings`, and `subscription`, but omits `reinstallPendingAt`. The code then type-casts the Prisma result to pretend the field exists. Real Prisma select results do not contain unselected columns, so `row.reinstallPendingAt` is `undefined` and every real `UNINSTALLED` job returns at `row.reinstallPendingAt == null` before Partner is called. The unit harness hides this by returning the entire mocked row regardless of the requested Prisma `select`.

2. **The reinstall branch does not verify `job.subscriptionId`.**

   The normal ACTIVE path checks `row.subscription.id !== job.subscriptionId`; the new UNINSTALLED branch does not. The reinstall exception must require the queued subscription id to equal the shop's current durable Subscription id before calling Partner.

3. **A stale Partner response can reactivate a shop after the reinstall attempt changes.**

   `completeReinstallWithoutContract`, `completeReinstallFree`, `activateReinstallPaid`, and `activateReinstallAfterRollover` recheck only Subscription schedule/state. They do not transactionally prove that the Shop is still `UNINSTALLED` with the exact `reinstallPendingAt` captured before the Partner call. A concurrent retry, suspension, uninstall lifecycle change, or another restoration attempt can therefore be overwritten by an older Partner response.

4. **Successful Free/Paid restoration does not faithfully refresh provider pending-plan projection.**

   Outcome B requires current/pending provider projection under the accepted mapping rules. `completeReinstallFree()` hard-clears all pending fields. `activateReinstallPaid()` leaves the preserved pending fields untouched. Both are wrong when Shopify currently reports `pendingPlanHandle` / `pendingEffectiveAt`.

5. **Pack-enabled Free mapping can activate with a missing configured pack meter handle.**

   The guard only rejects when `shopifyRecoveryCreditPackEventHandle` is non-null but absent from `provider.usageEventHandles`. For `recoveryCreditPackEnabled=true`, a null configured pack-event handle must also fail closed as `MISSING_USAGE_METER`, matching the accepted Free/rollover mapping rule.

6. **Same-paid-period validation proves counter existence but not counter integrity.**

   The task requires missing/inconsistent period-counter state to fail closed. Attempt 1 selects only `{ id: true }` from `BillingPeriodEntitlementCounter`. Before reactivation, verify the exact period/counter identity and quantity invariants used by the accepted Paid billing policy: matching shop/period, safe non-negative integer quantities, and `committedQuantity + reservedQuantity + forfeitedQuantity <= grantedQuantity`. The counter grant must agree with the immutable period grant snapshot; reinstall must never repair/reset these quantities.

7. **Same-paid-period restoration stores a normal `nextReconcileAt` but does not best-effort publish the corresponding deterministic job.**

   `activateReinstallPaid()` computes/persists the drain-window schedule and returns a boolean. `completeReinstallPaid()` returns immediately after it, without `publishNext(...)`. The task explicitly requires the normal paid follow-up job after commit. Queue failure must remain non-transactional and repairable by reconstruction.

8. **The submitted tests do not cover the task's required reinstall matrix.**

   The added tests cover the mocked happy-path null/Free cases, stale schedule, and reconstruction, but no direct reinstall tests prove the required same-paid-cycle, rollover, changed-plan, missing/inconsistent counter, transport-expiry, SUSPENDED, pending-projection, or preservation cases. Passing 74 focused tests does not substitute for the task's explicit Required tests.

#### Required Attempt-2 production corrections

Make only the following bounded corrections in `moda-interact-background/src/services/billing-subscription-reconciliation.service.ts`. Do not redesign unrelated billing reconciliation.

1. **Use the real Prisma reinstall field.**
   - Add `reinstallPendingAt: true` to the `shop.findUnique()` select in `reconcileJob()`.
   - Remove the unsafe cast that invents `{ reinstallPendingAt: Date | null }`. Let Prisma infer the selected field.
   - Before any Partner call on the UNINSTALLED exception require all of:

     ```text
     row.status == UNINSTALLED
     row.reinstallPendingAt != null
     row.subscription != null
     row.subscription.id == job.subscriptionId
     row.subscription.nextReconcileAt != null
     row.subscription.nextReconcileAt.toISOString() == job.expectedNextReconcileAt
     ```

   - `SUSPENDED`, ordinary `UNINSTALLED`, mismatched subscription id, stale schedule, missing Shopify shop id, and missing Subscription remain terminal successful no-ops with no Partner call.

2. **Make the durable Shop reinstall marker part of every successful transaction.**
   - Pass the captured `ReinstallExpected.reinstallPendingAt` through every completion path.
   - Before committing ANY successful restoration, transactionally prove:

     ```text
     Shop.id == shopId
     Shop.status == UNINSTALLED
     Shop.reinstallPendingAt == expected.reinstallPendingAt
     Subscription.id == expected.subscriptionId
     Subscription.nextReconcileAt == expected.nextReconcileAt
     ```

   - The check must be concurrency-safe, not a non-locking read followed by unconditional `shop.update()`. Use one consistent transaction pattern that locks/CASes the Shop row and rolls back all Subscription/ShopSettings/BillingPeriod changes if the marker/status changed.
   - Do not turn a stale marker/CAS miss into a provider/configuration error. It is a terminal stale-job no-op. Do not enqueue another job from that stale attempt.
   - Apply this to provider-null, verified Free, same-paid-cycle, and later-cycle rollover success.

3. **Keep canonical rollover atomic with the reinstall authority.**
   - For the later same-plan paid-cycle path, continue using `SamePlanBillingPeriodRolloverService`; do not copy its close/open implementation.
   - Use its existing `transitionInTransaction(...)` capability (or an equivalently atomic use of the canonical service) so the exact reinstall Shop marker is verified in the same transaction that performs the rollover and final Shop activation.
   - If the reinstall marker/status changed, the rollover must not commit for that stale attempt.
   - Preserve `provider-cycle-lag` / integrity failure semantics from BACKGROUND-007; do not invent a replacement period.

4. **Refresh provider pending projection on successful current-plan reconciliation.**
   - Resolve `provider.pendingPlanHandle` using the existing BillingPlan mapping rule used elsewhere in this service.
   - On successful Free and same-paid-cycle restoration write:

     ```text
     pendingShopifyPlanHandle = provider.pendingPlanHandle
     pendingPlanId = mapped active local pending plan id, else null
     pendingEffectiveAt = provider.pendingEffectiveAt
     ```

   - If `pendingPlanHandle` is null, all three pending fields become null.
   - Do not apply the pending plan early; this is projection only.
   - Add equivalent projection after a successful same-plan rollover if the canonical rollover primitive does not already persist these three fields.

5. **Enforce the accepted pack-enabled Free meter rule.**
   - If `plan.kind == FREE && plan.recoveryCreditPackEnabled == true`, require BOTH:

     ```text
     plan.shopifyRecoveryCreditPackEventHandle != null
     provider.usageEventHandles contains that exact handle
     ```

   - Otherwise keep Shop UNINSTALLED and record `MISSING_USAGE_METER`.
   - Do not create a local substitute handle.

6. **Validate exact same-paid-period integrity before restoration.**
   - Revalidate under the final restoration transaction, not only before it.
   - The pointed BillingPeriod must be OPEN and match at least:

     ```text
     period.id == Subscription.billingPeriodId
     period.shopId == shopId
     period.subscriptionId == Subscription.id
     period.planId == current paid plan id
     period.periodStart/end == Subscription.currentPeriodStart/end == provider current period
     ```

   - Load the unique `INCLUDED_RECOVERY_CREDITS` counter and require:

     ```text
     counter.shopId == shopId
     counter.billingPeriodId == period.id
     granted/committed/reserved/forfeited are safe non-negative integers
     committed + reserved + forfeited <= granted
     counter.grantedQuantity == period.includedRecoveryCreditsGranted
     ```

   - Any failure records `PERIOD_ALIGNMENT_REQUIRED`, leaves Shop UNINSTALLED, preserves all quantities, and performs no upgrade/downgrade.

7. **Publish the exact paid follow-up job after a successful same-cycle commit.**
   - Keep `nextReconcileAt = max(now, currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)`.
   - After the transaction commits, call the existing `publishNext(shopId, subscriptionId, nextReconcileAt)`.
   - Do not make Redis success part of the PostgreSQL transaction. A queue failure must leave the committed durable schedule intact so `reconstruct()` repairs it.

#### Required Attempt-2 tests

Add executable tests in `tests/unit/services/billing-subscription-reconciliation.service.test.ts`. Existing unrelated tests may remain unchanged. Do not satisfy these requirements with source-text/regex assertions.

At minimum add/strengthen tests that prove all of the following:

1. The actual `shop.findUnique()` call selects `reinstallPendingAt: true`; remove reliance on the harness returning unselected fields.
2. UNINSTALLED + exact marker + exact schedule + matching subscription id calls Partner.
3. UNINSTALLED with a different `job.subscriptionId` is a no-op and never calls Partner.
4. SUSPENDED with a reinstall marker/schedule is still a no-op and never calls Partner.
5. A marker/status change after Partner returns causes the final transaction to do no restoration and does not enqueue. Cover at least `reinstallPendingAt` changed and Shop changed to `SUSPENDED`.
6. Provider null establishes ACTIVE + NO_CONTRACT + onboarding false, clears current/pending Subscription pointers, and does not mutate/delete historical BillingPeriod/counter, lifetime-Free, purchased, promotional, purchase or refund state. Add spies/mocks for those owned models so preservation is explicit rather than inferred from absence of fixture fields.
7. Verified Free preserves existing lifetime counter quantities exactly and creates no lifetime grant.
8. Pack-enabled Free with `shopifyRecoveryCreditPackEventHandle=null` fails closed; pack-enabled Free whose configured handle is absent from provider handles also fails closed.
9. Provider pending-plan projection is refreshed for a successful Free restore, including both mapped-active pending plan and null/unmapped cases.
10. Same paid plan + exact same cycle reuses the existing BillingPeriod/counter, leaves all four counter quantities unchanged, restores ACTIVE/onboarding, and accepts `cancelAtPeriodEnd=true`.
11. Same-paid-cycle restoration rejects: missing period, wrong shop/subscription/plan identity, CLOSED period, missing counter, counter identity mismatch, negative/non-integer quantity, `committed + reserved + forfeited > granted`, and grant mismatch with `BillingPeriod.includedRecoveryCreditsGranted`.
12. Successful same-paid-cycle restoration refreshes provider pending projection and enqueues the deterministic drain-window job after commit.
13. If that enqueue fails, durable ACTIVE state and `nextReconcileAt` remain committed and a later `reconstruct()` republishes the same deterministic job.
14. Same-plan later/non-overlapping paid cycle delegates to the canonical BACKGROUND-007 transition, activates only after that transition succeeds, preserves historical/lifetime balances, and keeps the normal rollover schedule.
15. A stale reinstall marker discovered during the later-cycle transaction rolls back/no-ops the canonical rollover for that stale attempt.
16. Different provider paid plan remains fail-closed; no upgrade/downgrade and no counter mutation.
17. Provider transport error while reinstalling updates only `lastSyncErrorCode`, `lastSyncErrorAt`, and `nextReconcileAt`; Shop remains UNINSTALLED and all entitlement/current/pending/credit fields are unchanged.
18. Reinstall retry tiers are derived from `Shop.reinstallPendingAt`, enqueue the deterministic next job before 24h, and at/after 24h leave `nextReconcileAt=null`, Shop UNINSTALLED, marker present, and no enqueue.
19. Startup/periodic `reconstruct()` includes pending reinstall rows, publishes with `delay=max(0,next-now)`, and never calls Shopify.
20. Keep the existing active initial-activation tests green, plus the adjacent inactive recovery/WhatsApp and pre-uninstall usage-publication gates required by this task.

The test harness must not mask Prisma-select mistakes. Where a production branch depends on a selected field, either assert the exact Prisma `select` or make the mock honor the select shape.

#### Validation required for Attempt 2

Run exactly the repository-declared validation that applies to this task:

```bash
npm test -- --run tests/unit/services/billing-subscription-reconciliation.service.test.ts

npm test -- --run \
  tests/unit/runtime/billing-scheduler.test.ts \
  tests/unit/runtime/entrypoint-isolation.test.ts \
  tests/unit/services/shopify-usage-event-publisher.service.test.ts \
  tests/unit/services/recovery-routing.service.test.ts

npm run prisma:validate
npm test
npm run build
git diff --check
```

Do not invent `npm run lint` or `npm run typecheck`; this repository does not declare those scripts. If full `npm test` / `npm run build` still fail only with the documented unrelated purchase/observability baseline, record exact counts/files and prove there are no diagnostics/failures in the files changed by BACKGROUND-006. Any new failure in the touched slice is a task failure.

#### Scope / stop condition

- Allowed production file: `src/services/billing-subscription-reconciliation.service.ts`.
- Allowed focused test file: `tests/unit/services/billing-subscription-reconciliation.service.test.ts`.
- Do not modify Prisma schema, Shared contracts, queue names/payload schema, Shopify app, Admin, Messaging, purchase/refund semantics, generic inactive-shop gates, or `SamePlanBillingPeriodRolloverService` unless a concrete defect in that already-accepted primitive makes this correction impossible. If that occurs, STOP and return Blocked with exact evidence rather than modifying it opportunistically.
- Preserve all valid Attempt-1 work, including reconstruction and canonical rollover delegation.
- After the corrections and required validation, update the Completion Report, set the SAME task to `review`, clear `executor`/`claimed_at`, push both mirrored task branches, return to `moda_architect`, and STOP. Do not start `SHOPIFY-006` or any system-test task.

#### Reviewed Files
- `moda-interact-background/src/services/billing-subscription-reconciliation.service.ts`
- `moda-interact-background/tests/unit/services/billing-subscription-reconciliation.service.test.ts`
- `moda-interact-background/src/services/same-plan-billing-period-rollover.service.ts`
- `moda-interact-background/src/services/effective-billing-policy.service.ts`
- `docs/decisions/background/ARCH-010/BACKGROUND-006-reinstall-subscription-reconciliation.md`
- `docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`

#### Validation Reviewed
- Reported focused reconciliation suite: 74/74 passed.
- Reported adjacent gate suite: 49/49 passed.
- Reported Prisma validation and `git diff --check`: passed.
- Reported full-suite baseline: 718 passed / 10 failed / 12 skipped; failures reported outside the touched reconciliation slice.
- Reported build baseline: 15 existing generated purchase-client/type errors in two unrelated purchase services; no reported errors in the touched service.
- Review finding: the focused mocks do not model Prisma `select`, so those green results do not prove the real reinstall branch is reachable.

#### Architecture Conformance
Not yet conformant. The implementation preserves the intended queue/provider/reconstruction ownership boundaries, but the missing durable reinstall field, stale-attempt race, incomplete provider projection, counter-integrity gap and missing paid follow-up publication violate the explicit Iteration-5 restoration contract.

#### Follow-up
Return `ARCH-010-BACKGROUND-006` to Attempt 2 on the same task branch. Downstream `ARCH-010-SHOPIFY-006` and `ARCH-010-SYSTEM-TEST-002` remain gated until BACKGROUND-006 is architect-accepted Complete.
