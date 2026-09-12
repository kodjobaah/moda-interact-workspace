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
status: pending
priority: 49
executor: null
claimed_at: null
attempt: 0
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
updated: '2026-09-12'
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
