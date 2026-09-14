---
id: ARCH-011-BACKGROUND-002
architecture_id: ARCH-011
title: Reconcile and apply provider-authoritative same-cycle upgrades
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-DATABASE-001
- ARCH-011-SHARED-002
- ARCH-011-BACKGROUND-001
enables:
- ARCH-011-BACKGROUND-003
- ARCH-011-SHOPIFY-002
created: 2026-09-14
updated: 2026-09-14
---

# ARCH-011-BACKGROUND-002

## Objective
Extend the **existing** billing-subscription reconciliation worker so Shopify's actual current plan is reconciled into ARCH-011 transitions/segments/entitlement. Do not implement recovery admission safety here.

## Authorized implementation surface
```text
src/services/billing-subscription-reconciliation.service.ts
src/services/plan-upgrade-reconciliation.service.ts          # new
src/workers/billing-subscription-reconciliation.worker.ts     # only if dependency wiring requires
src/entrypoints/billing.ts                                    # only if constructor wiring requires
tests/unit/services/billing-subscription-reconciliation.service.test.ts
tests/unit/services/plan-upgrade-reconciliation.service.test.ts # new
tests/integration/plan-upgrade-reconciliation.concurrency.integration.test.ts # new
```
No other billing/reservation service may be edited.

## Exact architecture
Create class `PlanUpgradeReconciliationService` in the new file. `BillingSubscriptionReconciliationService.reconcileJob` remains the sole worker entrypoint and delegates to it after one fresh `getSubscriptionReconciliationSnapshot` call.

Extend `reconstruct()` and job eligibility so a Subscription with an unresolved transition (`REQUESTED|PROVIDER_CONFIRMED|NEEDS_ATTENTION`) and non-null `nextReconcileAt` is reconstructed even when `pendingPlanId` is null.

Use published Shared constants: first merchant observation at 60s; REQUESTED expires at `requestedAt + 30m`; subsequent REQUESTED/NEEDS_ATTENTION retries are exactly 60s capped at that deadline/current cycle boundary, whichever is earlier.

## Binding decision table
Given local plan/cycle and fresh provider snapshot:

```text
provider current == local, no lower pending:
  REQUESTED before deadline -> leave plan/counter/segments unchanged; nextReconcileAt=now+60s
  REQUESTED at/after deadline -> FAILED, failureCode=REQUEST_NOT_CONFIRMED, nextReconcileAt=null
  no unresolved -> existing baseline path

provider current == local, mapped pending lower:
  preserve existing Subscription pendingPlan/pendingEffectiveAt projection
  REQUESTED -> SUPERSEDED, failureCode=PROVIDER_SELECTED_DEFERRED_DOWNGRADE
  no ARCH-011 downgrade transition/segment/grant

provider current is mapped UPGRADE:
  requested target is ignored for authority
  if REQUESTED from same source: preserve requested snapshots and confirm actual provider target
  otherwise create PROVIDER_OBSERVED transition with all requested fields null
  select exact event using BACKGROUND-001 helper
  no exact event -> NEEDS_ATTENTION, nextReconcileAt=now+60s bounded by cycle end
  exact event -> apply below

provider current is mapped DOWNGRADE:
  provider cycle changed -> delegate existing boundary path
  provider cycle same -> NEEDS_ATTENTION/fail closed; no plan/segment/counter mutation

SAME + cycle advanced -> existing same-plan rollover
UNRESOLVED/unmapped -> no grant/application; persist bounded sync error/NEEDS_ATTENTION as applicable
```

## Same-cycle application transaction
Implement in `PlanUpgradeReconciliationService.applySameCycleUpgrade` using one `Prisma.TransactionIsolationLevel.Serializable` transaction and existing `FOR UPDATE` order: ShopSettings (if needed) -> Subscription -> BillingPeriod -> included counter/transition rows. No advisory/process/Redis lock.

Inside transaction exactly:
1. re-read Subscription, open BillingPeriod, transition/version, final segment, INCLUDED counter;
2. verify provider target/cycle/event evidence still matches pre-transaction snapshot;
3. if no segments exist, create opening segment from `BillingPeriod` opening snapshots for `periodStart..periodEnd`; if opening allowance snapshot is null, STOP/NEEDS_ATTENTION (do not guess);
4. require final segment effectiveTo==periodEnd and planId==transition.fromPlanId;
5. update final segment effectiveTo=providerEffectiveAt;
6. create one target segment `providerEffectiveAt..periodEnd` with provider target snapshots and `sourceTransitionId=transition.id`;
7. calculate target from complete candidate segments via Shared;
8. `alreadyGranted = INCLUDED counter.grantedQuantity`; only when opening plan is FREE and no INCLUDED counter exists may alreadyGranted be 0;
9. calculate delta via Shared; target<granted => rollback and NEEDS_ATTENTION/`TARGET_BELOW_GRANTED`;
10. update counter with version CAS: increment granted by delta and version by 1; preserve committed/reserved/forfeited;
11. update Subscription planId/observed handle/current cycle to provider target but keep same BillingPeriod id;
12. write immutable target/alreadyGranted/delta snapshots and mark transition APPLIED with mode SAME_CYCLE_PRORATED/appliedAt;
13. commit once. Retry serialization/CAS using existing repository retry convention; replay must detect APPLIED/sourceTransitionId and return no-op.

New-cycle higher/lower and same-plan cycle rollover MUST call/retain existing ARCH-010 boundary services; do not duplicate full-opening logic in this task.

## Exact tests
Add cases matching the 28 cases from architecture, including requested Scale/provider Growth, provider-observed, lost callback scheduled job, request expiry, pending lower supersession, same-cycle lower fail closed, half-cycle 100/300=>200/delta100, usage independence, direct skip, repeated upgrades, duplicate event, two reconciler race, counter CAS race, missing-event recovery, cycle-close failure, event-at-cycle-start boundary path, null cycle no proration, target<granted.

## Validation
```text
npm run prisma:validate
npm run prisma:generate
npx vitest run tests/unit/services/billing-subscription-reconciliation.service.test.ts tests/unit/services/plan-upgrade-reconciliation.service.test.ts
npx vitest run tests/integration/plan-upgrade-reconciliation.concurrency.integration.test.ts
npm test
npm run build
git diff --check
```

## Stop conditions
STOP rather than redesign if exact event evidence is unavailable, opening allowance cannot be proven, baseline rollover service is absent, lower-paid normally becomes current same-cycle, or a new locking strategy would be required.

## Completion protocol

After all Work Items, Acceptance Criteria and Validation pass: update the Completion Report, set task status to `review`, clear the active claim according to the normal launcher protocol, return control to `moda_architect`, and **STOP**. Do not start an enabled/follow-on task.
