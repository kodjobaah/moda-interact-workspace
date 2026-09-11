---
id: ARCH-010-BACKGROUND-010
architecture_id: ARCH-010
title: Apply Shopify-authoritative plan changes without resetting lifetime credit history
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-DATABASE-004
  - ARCH-010-BACKGROUND-003
  - ARCH-010-BACKGROUND-007
  - ARCH-010-SHARED-002
enables:
  - ARCH-010-BACKGROUND-012
  - ARCH-010-BACKGROUND-016
  - ARCH-010-SHOPIFY-015
  - ARCH-010-SYSTEM-TEST-001
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-BACKGROUND-010: Apply Shopify-authoritative plan changes without resetting lifetime credit history

## Objective

Extend the canonical subscription reconciliation worker so Shopify-hosted plan changes become Moda entitlement transitions exactly once and only when Shopify says the new plan is effective.

This task owns the effective transition. Merchant HTTP callbacks do not grant/forfeit plan entitlement.

## Product invariants

1. Shopify `activeSubscription` is commercial subscription authority.
2. `pendingUpdate` is not current entitlement.
3. Moda never calculates Shopify proration.
4. Purchased recovery credits survive every plan change.
5. Free lifetime usage history survives every plan change and is never reset/re-granted.
6. Paid included credits belong to one paid BillingPeriod and never roll over.
7. Paid plan change at an expected billing-cycle boundary closes the old period and forfeits unused old included credits.
8. New paid allowance is granted exactly once for the new effective paid period.
9. Unknown/unmapped provider plans fail closed; no Free/Paid entitlement is guessed.
10. No merchant is linked to `moda-interact-admin`.

## Inspect before editing

```text
src/services/billing-reconciliation.service.ts
src/providers/shopify-partner-billing.provider.ts
src/services/recovery-billing.service.ts
src/services/paid-recovery-reservation.service.ts
src/workers/billing-worker.ts
existing ARCH-010 subscription reconciliation queue consumer/runtime
relevant unit/integration tests
```

Also read:

```text
docs/decisions/background/ARCH-010/BACKGROUND-003-first-paid-subscription-activation.md
docs/decisions/background/ARCH-010/BACKGROUND-007-canonical-paid-billing-period-rollover.md
docs/decisions/database/ARCH-010/DATABASE-004-billing-period-lifecycle-history.md
```

## Reconciliation input

Every execution must re-query Shopify Partner `activeSubscription`. Do not apply a plan change from only local `pendingPlanId` or a BullMQ payload.

Use the durable Subscription row only as expected/current local state and scheduling metadata.

## State classification

Given local current plan `L`, local pending plan `P`, and provider current/pending state:

### A. Provider still reports current L + pending P

- no entitlement change;
- preserve current BillingPeriod/counter;
- preserve pending fields;
- schedule next reconciliation at `pendingEffectiveAt` / current period boundary;
- return success/no-op.

### B. Provider current == expected pending P at/after expected boundary

Apply the effective transition atomically using the cases below.

### C. Provider current == L and pending disappeared

Treat the pending change as withdrawn/replaced:

- clear only local pending fields that no longer exist in provider state;
- preserve current entitlement;
- reschedule normal renewal reconciliation;
- do not fabricate a plan change event.

### D. Provider current is an unmapped handle

- persist observed Shopify handle according to existing projection conventions;
- set fail-closed `UNMAPPED`/equivalent safe projection;
- do not grant Free or Paid credits;
- preserve historical counters/purchases;
- keep reconciliation recoverable after Admin registers mapping.

### E. Provider query failure

- preserve last known entitlement state;
- record sync failure through existing `lastSyncError*`/telemetry conventions;
- retry through existing schedule;
- provider failure != NO_CONTRACT.

### F. Unexpected immediate current-plan change before expected boundary

ARCH-010's agreed entitlement model assumes plan changes are represented as provider pending updates until their effective boundary. Shopify is still commercial authority, so do not pretend the old provider plan remains current.

However, the current ARCH-010 data model intentionally has one plan/allowance snapshot per BillingPeriod and no mid-cycle plan-entitlement segments.

Therefore if Shopify reports a different current mapped plan while:

```text
now < local currentPeriodEnd
AND
provider currentBillingCycle matches the still-open local cycle
AND
no boundary transition can be proven
```

then:

- do NOT grant a fresh new plan allowance;
- do NOT continue normal paid metered recovery using stale plan-meter assumptions;
- mark a typed fail-closed sync/configuration condition such as `UNEXPECTED_IMMEDIATE_PLAN_CHANGE` using existing projection error fields;
- keep merchant read/history/support surfaces available;
- block new billable recovery/top-up operations until reconciliation is resolved;
- emit structured operational logging;
- do not invent proration or a second overlapping BillingPeriod.

This is a runtime safety branch, not permission to redesign the schema. If this branch occurs as normal production behaviour, return the architecture to `moda_architect` for a separate mid-cycle entitlement design.

## Effective transition cases

All transitions below execute inside one serializable/architecture-approved transaction and must be replay-safe.

### Paid -> Paid at boundary

Preconditions:

- provider current plan maps to active PAID_METERED plan;
- provider current cycle is exact and later/effective relative to old period;
- expected pending/current transition is provable.

Actions:

1. close old OPEN BillingPeriod with `closeReason=PLAN_CHANGED`;
2. release old period outstanding included reservations using accepted period-close rules;
3. set old `forfeitedQuantity = granted - committed` after reservation release, bounded by DB constraints;
4. create/reuse exactly one new BillingPeriod for provider exact current cycle with the new plan snapshots;
5. create/reuse exactly one included-credit counter with `grantedQuantity = newPlan.includedRecoveryConversationAllowance` and zero committed/reserved/forfeited;
6. update Subscription current plan/current period pointer/provider fields;
7. clear pending fields only after provider current state proves the transition;
8. set `nextReconcileAt` to the accepted pre-close boundary for the new period;
9. enqueue/reuse deterministic delayed reconciliation;
10. best-effort capacity-resume hint for recoveries blocked solely by exhausted capacity.

Purchased credits remain unchanged.

### Paid -> Free at boundary

Actions:

1. close old paid period with `PLAN_CHANGED` and forfeit/release using canonical close semantics;
2. set current Subscription plan to mapped FREE plan;
3. require an exact provider Free `currentBillingCycle` when the mapped Free plan enables recovery-credit-pack billing;
4. create/reuse the exact provider Free BillingPeriod with `planKindSnapshot = FREE`, `includedRecoveryCreditsGranted = null`, and no included-credit period counter;
5. point Subscription current period fields/pointer at that Free provider BillingPeriod;
6. do NOT create a monthly Free recovery allowance/counter;
7. do NOT reset Free lifetime usage;
8. purchased credits remain unchanged;
9. clear pending fields after provider confirms Free current;
10. schedule next pre-close reconciliation when Free pack billing is enabled;
11. normal Free admission remains:
   `promotional credits -> purchased credits -> remaining shop-lifetime Free -> BLOCK NEW RECOVERY ADMISSION`.

### Free -> Paid when provider Paid becomes current

Actions:

1. preserve Free lifetime usage exactly as-is;
2. preserve purchased credits;
3. close the current OPEN Free provider BillingPeriod with `PLAN_CHANGED` when one exists and matches the provider-confirmed outgoing cycle; this closes commercial/App-Event scope only and does not alter Free lifetime usage;
4. create the first exact paid BillingPeriod/counter using the same helper/service semantics accepted in BACKGROUND-003;
5. update Subscription to current paid plan/cycle;
6. clear pending fields only after provider confirms current;
7. schedule normal paid pre-close reconciliation;
8. do not reset remaining promotional or lifetime Free credits while merchant is Paid; after paid monthly included and promotional/purchased credits are exhausted, the remaining lifetime Free grant is the final fallback per BACKGROUND-019/BACKGROUND-014/BACKGROUND-011.

### Free -> Free / same-plan observation

No entitlement reset. Preserve Free lifetime usage and purchased credits. If Shopify reports a later exact currentBillingCycle for the same mapped Free plan, delegate to BACKGROUND-007's same-plan Free provider BillingPeriod rollover. Do not independently upsert/open a second Free period.

## No local upgrade/downgrade rank

Do not decide transition direction from a local `tierRank`, price comparison or plan name.

For runtime effects, only the old/current Moda plan kind and new provider-confirmed mapped plan kind matter.

## Billing meter safety

Before opening a new paid period, require the new plan's configured normal recovery meter and pack meter (when enabled) to match active provider subscription items according to accepted provider mapping rules.

Do not send old-plan meter events after provider current plan changed.

## Idempotency

Replaying the same effective provider state must not:

- close the old period twice;
- create a second new period;
- grant included allowance twice;
- reset Free lifetime history;
- increment purchased credits;
- duplicate capacity-resume work beyond deterministic queue semantics.

Use existing unique period/current-period constraints and transaction patterns; do not create an implementation-local mutex as the source of truth.

## Required tests

At minimum prove:

1. current plan + still-pending provider update is a no-op with reschedule;
2. withdrawn provider pending update clears pending fields without entitlement change;
3. paid->paid boundary closes old period with PLAN_CHANGED and opens one new period;
4. paid->paid unused old credits are forfeited, not rolled over;
5. paid->paid new allowance is granted exactly once under replay;
6. paid->paid purchased credits survive unchanged;
7. paid->Free closes paid period, creates/reuses exact Free provider BillingPeriod when required, and creates no monthly Free recovery counter;
8. paid->Free does not reset lifetime Free committed usage;
9. paid->Free purchased credits survive;
9a. paid->Free Free provider period snapshot has includedRecoveryCreditsGranted=null;
10. Free->Paid reuses first-paid activation semantics and preserves Free lifetime history;
11. Free->Paid purchased credits survive;
12. provider unmapped current handle grants no entitlement;
13. provider failure preserves last known entitlement and retries;
14. unexpected immediate same-cycle current-plan change grants no fresh allowance and enters fail-closed sync condition;
15. unexpected immediate branch sends no stale old-plan billing event;
16. old plan meter is never used after a provider-confirmed effective new paid plan;
17. exact provider cycle is required for new paid period;
18. pending fields clear only after provider proves effective current state;
19. deterministic delayed job is scheduled for next period;
20. no local price/rank/proration calculation exists.

## Non-goals

Do not change merchant UI, Shopify callback routes, refund workflows, cancellation flows, promotional credits or Admin plan configuration.

Do not add mid-cycle plan entitlement segments in this task.

## Validation

Run focused reconciliation/transition tests, repository tests declared by the task/package, Prisma/client compatibility checks if touched, typecheck, build and `git diff --check`.

## Stop conditions

STOP if DATABASE-004 does not provide `PLAN_CHANGED` close reason, one-open-period protection and historical plan snapshots.

STOP if implementing the normal supported path requires overlapping BillingPeriods for one Shopify cycle.

STOP and report to `moda_architect` if observed Shopify behaviour makes the `UNEXPECTED_IMMEDIATE_PLAN_CHANGE` branch a normal expected plan-change path rather than an exceptional safety condition.

## Completion Report

### Status
Not started.


## Final promotional preservation contract

Every Shopify plan transition preserves `PROMOTIONAL_RECOVERY_CREDITS` granted/committed/reserved state exactly. Plan change neither grants nor resets promotional capacity. After the effective plan transition, normal recovery admission uses promotional credits in the canonical position ahead of purchased credits.
