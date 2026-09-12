---
id: ARCH-010
title: Merchant lifecycle state transitions and behavioural access
status: agreed
coordinator: moda_architect
created: 2026-09-11
updated: 2026-09-12
---

# ARCH-010: Merchant lifecycle state transitions and behavioural access

## Status

**Agreed.** The ARCH-010 behavioural architecture is complete and consolidated. Fresh/returning activation, Free/Paid entitlement, recovery-capacity priority, App Pricing billing-period rollover, plan changes, uninstall/reinstall, cancellation, freeze/unfreeze, purchased-credit refunds and promotional credits are all defined. Repository implementation tasks plus terminal/manual-gated system tests are materialised below.

> **Final-state reading rule:** This file retains numbered iteration headings as design provenance, but those headings are **not independent current contracts**. Implementers must use the consolidated invariants near the top of this document plus the exact current `ARCH-010-*` task. Earlier iteration-scoped phrases such as “later iteration”, “not in this iteration” or pre-promotion/pre-freeze capacity examples describe the design sequence only and must not override the final ARCH-010 state. For a non-iterative readable model, use [`../product/pricing-and-billing-model.md`](../product/pricing-and-billing-model.md). For explicit old→new rules, use [`ARCH-010-supersession-map.md`](ARCH-010-supersession-map.md).


> **Promotional-campaign amendment (2026-09-12):** The final first-release promo model is optional merchant opt-in campaigns, not direct non-expiring Admin grants. See [`ARCH-010-promotional-campaigns.md`](ARCH-010-promotional-campaigns.md). A selected usable promotion is the **highest-priority** recovery source. Older Iteration-12 text describing lifetime/unselected direct grants is design provenance only.

> **First-production baseline amendment (2026-09-12):** ARCH-010 is now the clean first-production database/runtime baseline. [`ARCH-010-first-production-baseline.md`](ARCH-010-first-production-baseline.md) is binding over any older compatibility/backfill wording retained below as design provenance. First production has no `BillingPlan.freeLifetimeConversationAllowance`, `BillingAllowanceAdjustment`, old `FREE_RECOVERY_LIFETIME`, aggregate `PROMOTIONAL_RECOVERY_CREDITS`, local cancellation state machine, `MIGRATION_RECONCILED`, purchase `REFUNDED` state, negative-App-Event refund correction model, or campaign-less promotional grant fallback. Implementers MUST NOT preserve those removed concepts merely because an earlier iteration mentions them.

> **Task-consolidation amendment (2026-09-12):** For active implementation ownership, `BACKGROUND-016` is superseded by `BACKGROUND-012`; `BACKGROUND-017` by `BACKGROUND-013`; `SHOPIFY-010` by `SHOPIFY-014`; `SHOPIFY-011` by `SHOPIFY-015`; and `SHOPIFY-019` by `SHOPIFY-016`. Any older iteration text below assigning work to those superseded IDs is design provenance only. Repository agents MUST implement the surviving task file and MUST NOT claim the superseded task. `BACKGROUND-018` remains deliberately separate because it owns the high-volume queued Shopify-event hot path.

## Problem

Moda Interact has durable billing, subscription, entitlement and uninstall primitives from ARCH-007/008/009, but merchant-facing behaviour is not yet defined consistently as a state machine. ARCH-010 defines transitions between merchant lifecycle states and, for each resulting state, the screens, actions and runtime services that are available.

ARCH-009 is frozen while ARCH-010 resolves the lifecycle model. ARCH-010 may later supersede, reopen or narrow affected ARCH-009 tasks. Do not preserve an ARCH-009 behaviour merely because an older task is Complete when it conflicts with the agreed ARCH-010 lifecycle.

## Global invariants agreed before ARCH-010

- Merchants never access `moda-interact-admin`; it is an internal platform/support console only.
- Shopify App Pricing is the subscription authority.
- One durable local `Subscription` projection exists per installed shop once the merchant has been resolved locally.
- `Subscription` represents current/pending local projection truth. ARCH-010 does not add a second append-only local subscription-history table: exact provider BillingPeriod history is local, latest provider lifecycle evidence is persisted for reconciliation, and the Shopify Partner Historical Events API remains authoritative for the full provider lifecycle timeline.
- Every merchant/shop receives one shop-lifetime Free recovery grant at first verified subscription activation, regardless of whether the first Shopify plan is Free or Paid. The current grant is 5 recovery conversations.
- Paid plans have period-scoped included recovery credits.
- Paid-plan included credits do not roll over.
- A paid-plan upgrade/downgrade becomes effective at the next Shopify billing-cycle boundary; no Moda proration is performed.
- Promotional credits are optional campaign-linked merchant allocations. Campaigns target GLOBAL, PLAN or SHOP, expire, are merchant-selected, are non-refundable, and preserve durable history after expiry/close.
- Purchased lifetime top-up credits survive plan changes/uninstall/reinstall; their unused portion may be refunded through the Moda top-up refund workflow.
- Recovery-capacity priority is deliberate: a usable merchant-selected promotion comes **first**. Paid then falls back to current-period included credits, purchased lifetime top-ups and shop-lifetime Free; Free falls back to purchased then lifetime Free; then **BLOCK NEW RECOVERY ADMISSION**.
- In ARCH-010, `BLOCK NEW RECOVERY ADMISSION` is a capacity outcome, not a global execution state: existing admitted conversations continue and merchant dashboard/history/billing/support access remains available. Broader execution stops are represented separately by `FROZEN`, `NO_CONTRACT` and inactive/uninstalled states.
- Shopify owns subscription cancellation and subscription-fee refund behaviour. Moda's refund workflow is only for purchased top-up credits.
- PostgreSQL is durable lifecycle truth. Redis/BullMQ is scheduling/delivery infrastructure, never the sole source of billing state.

## Canonical shop-lifetime Free grant and capacity priority

`LIFETIME_FREE_RECOVERY_CREDITS` is the canonical **shop-lifetime introductory entitlement**, not a Free-plan-owned allowance.

Binding rules:

```text
first verified Shopify subscription activation (Free OR Paid)
  -> snapshot PlatformBillingPolicy.lifetimeFreeRecoveryAllowance
  -> create/reuse ShopEntitlementCounter(LIFETIME_FREE_RECOVERY_CREDITS)
  -> grantedQuantity is written once
  -> later plan changes/reinstall/renewal NEVER reset or regrant it
```

The current product grant is 5 recoveries. Future changes to the platform default affect only merchants whose lifetime grant has not yet been created; they do not mutate existing shops. There is no signed allowance-adjustment compatibility in the first-production model. Campaign/testing/goodwill/support promotional capacity is created only through campaign-linked `PromotionalCreditGrant` lots.

Canonical recovery-capacity order:

```text
FREE subscription
  selected usable campaign PromotionalCreditGrant
  -> PURCHASED_RECOVERY_CREDITS
  -> LIFETIME_FREE_RECOVERY_CREDITS
  -> EXHAUSTED

PAID subscription
  selected usable campaign PromotionalCreditGrant
  -> current-period INCLUDED_RECOVERY_CREDITS
  -> PURCHASED_RECOVERY_CREDITS
  -> LIFETIME_FREE_RECOVERY_CREDITS
  -> EXHAUSTED
```

Promotional credits are intentionally consumed before merchant-funded refundable purchased credits. For Paid, promotion is also intentionally consumed before period included capacity. Purchased credits remain consumed before lifetime Free credits. The exact selected campaign grant lot is promotion authority; there is no aggregate promotional entitlement counter.

`BillingPlan` does not contain or own a lifetime-Free allowance in the first-production baseline. The canonical default is `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance`, while each shop's actual grant is the snapshotted `ShopEntitlementCounter.grantedQuantity` for `LIFETIME_FREE_RECOVERY_CREDITS`.

# Iteration 1 — Fresh install -> Installed / No plan / Onboarding

## Source state

The Shopify shop has completed app installation/authentication but Moda has no existing durable Shop for that Shopify identity.

## Trigger

Successful authenticated Shopify app entry for a previously unseen Shopify shop.

## Target durable state

```text
Shop.status                  = ACTIVE
Shop.uninstalledAt           = null
ShopSettings exists
ShopSettings.onboardingCompleted = false
Subscription exists
Subscription.status          = NO_CONTRACT
Subscription.planId          = null
Subscription.pendingPlanId   = null
Subscription.billingPeriodId/currentBillingPeriodId = null
BillingPeriod                = none
plan included credits        = none
lifetime Free grant             = not created before first verified activation
promotional balance             = optional pre-grant, preserved but non-spendable until executable contract
purchased top-up credits     = none for a genuinely new shop
```

No Shopify subscription query is required merely to render the first onboarding screen. Shopify is queried when the merchant returns from/enters billing verification or when another explicit reconciliation trigger requires it.

## Merchant UI after transition

Allowed merchant surfaces:

- `/app` — render the existing `Onboarding` experience.
- `/app/billing` — no-contract billing state / plan-selection entry.
- `/app/billing/select` — redirect to Shopify-hosted App Pricing.
- `/app/merchant-support` — merchant support/messages remain available.
- `/app/billing/callback` — transition/resource endpoint only; not a navigational screen.

Unavailable until a mapped plan becomes active:

- recovery/dashboard detail and recovery data views;
- usage/billable-event history;
- pending-recovery resource data;
- recovery automation;
- WhatsApp recovery sending;
- AI/CommerceAgent recovery execution;
- recovery top-up purchase action.

A direct request to a product/usage surface while `onboardingCompleted=false` or the subscription is `NO_CONTRACT` must return/redirect the merchant to `/app` onboarding rather than expose an empty or partially functional product page.

## Current implementation facts driving this change

- `ShopService.resolveShopifyShop()` already upserts `Shop` and `ShopSettings`.
- It does not create the initial `Subscription` projection.
- `/app` currently redirects incomplete onboarding to `/app/billing`, so the existing `Onboarding` component in the same route is not reached through the normal incomplete-onboarding path.
- `Onboarding` already contains Shopify-plan CTAs.
- `/app/billing/select` already redirects to Shopify-hosted pricing.
- Background's effective billing policy already fails closed for missing/`NO_CONTRACT` subscriptions, so a duplicate Background implementation is not required for this iteration.

## Transaction and idempotency requirements

Fresh-install initialization must be replay-safe. Repeated route/auth resolution for the same shop must not:

- create multiple Subscription rows;
- reset an active/trialing/current subscription to `NO_CONTRACT`;
- reset `onboardingCompleted`;
- grant promotional/free allowance repeatedly;
- create a BillingPeriod before plan activation.

The existing unique `Subscription.shopId` invariant is the durable one-projection guard. Creation should use an idempotent create-if-absent/upsert-with-no-destructive-update pattern.

## Failure behaviour

- If Shopify authentication/identity resolution fails: do not create a partial merchant state and fail the request through existing Shopify auth/error handling.
- If durable Shop/Settings/Subscription initialization fails: do not report onboarding success; surface an application error rather than treating the merchant as subscribed.
- Redis/BullMQ is not required for this transition. Fresh no-plan install creates no billing-cycle delayed job.

## No task required in this iteration

- `moda_background`: current billing policy already denies `NO_CONTRACT`/missing subscription.
- `moda_database`: the current schema can represent one `Subscription` per shop with `NO_CONTRACT`; broader ARCH-010 schema evolution will be handled in the later data-model transition iteration.
- `moda_shared`: no new cross-service contract is required.
- `moda_admin`: merchants never use Admin and no internal operational workflow is introduced here.
- `moda_gateway`: no topology/deployment change.
- `moda_system_test`: terminal integrated system-test tasks will be defined only after the complete ARCH-010 implementation graph is known.

## Next iteration

Plan activation from Installed / No Plan, reviewed separately for Free and Paid because their entitlement/billing-period semantics differ.

# Iteration 2 — Installed / No plan -> Free plan active

## Source state

```text
Shop.status                         = ACTIVE
ShopSettings.onboardingCompleted    = false
Subscription.status                 = NO_CONTRACT
Subscription.planId                 = null
current BillingPeriod               = none
Free lifetime usage                 = preserved historical value (normally 0 on first install)
purchased top-up balance            = preserved historical value (normally 0 on first install)
```

For a genuine first install, historical balances are zero. This transition must also remain safe if the same verified Free activation is replayed.

## Trigger

The merchant selects the Free plan on Shopify's hosted App Pricing page and Shopify redirects to Moda's configured billing callback with `plan_handle`.

The callback parameter is not entitlement proof. Moda must call the Partner API `activeSubscription(appId:, shopId:)` through the existing billing provider and accept Free activation only when the returned **current active** flat-rate plan handle maps to an active local `BillingPlan` whose `kind = FREE`.

A Shopify `pendingUpdate` is not sufficient to complete first-time onboarding. Pending plans are future state and do not replace the current entitlement.

## Target durable state

```text
Shop.status                         = ACTIVE
ShopSettings.onboardingCompleted    = true
Subscription.status                 = ACTIVE or TRIALING as reported/projected
Subscription.planId                 = mapped Free BillingPlan
Subscription.observedShopifyPlanHandle = verified current Free handle
Free lifetime grant                 = one-time ShopEntitlementCounter.grantedQuantity snapshot
Free committed/reserved usage       = existing durable ShopEntitlementCounter usage
purchased top-up balance            = unchanged
```

The canonical product is **one shop-lifetime Free grant** (currently 5 recovery conversations). The grant is created once at the merchant's first verified subscription activation whether that first plan is Free or Paid. It does not reset on billing cycle, reinstall, upgrade or downgrade. No signed Free-allowance adjustment compatibility is part of first production. Promotional/testing/support capacity is campaign-linked promotional grant state only.

Do not model the five Free recoveries as promotional credits. Campaign-linked `PromotionalCreditGrant` lots are separate from the five-credit shop-lifetime grant and the two are never converted into each other.

## Billing-period behaviour for Free

A Moda Free plan can still participate in Shopify App Pricing usage billing. When Free merchants may buy recovery top-ups, the Shopify Free plan is configured as a zero-recurring/usage-enabled plan with the recovery-credit-pack usage meter. Shopify remains commercial authority for that meter and its monthly billing cycle.

Moda therefore persists/reconciles the exact Shopify `currentBillingCycle` as a normal Subscription-owned `BillingPeriod` for Free as well as Paid. The purpose of the Free BillingPeriod is **commercial/App-Event cycle scope**, not recovery entitlement replenishment.

Binding distinction:

```text
Free Shopify BillingPeriod
  = monthly App Pricing / App Event billing scope

LIFETIME_FREE_RECOVERY_CREDITS
  = lifetime Moda recovery entitlement
```

Therefore:

- Free entitlement is **not period-scoped**;
- a Free BillingPeriod has `planKindSnapshot = FREE` and `includedRecoveryCreditsGranted = null`;
- no `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)` is created/granted for Free;
- Free lifetime usage is not reset when a Shopify cycle rolls;
- a Free billing-cycle boundary does not replenish the five lifetime conversations;
- a recovery-credit-pack purchase from Free must verify the exact current provider/local Free BillingPeriod and exact configured pack meter before creating its App Event.

## Merchant UI after transition

Normal merchant application access becomes available after onboarding is complete and the subscription projection is a mapped ACTIVE/TRIALING Free plan.

Available merchant surfaces include:

- `/app` — normal merchant Home/Usage Overview instead of Onboarding;
- `/app?view=detail` — merchant recovery/dashboard detail;
- `/app/usage` — merchant-scoped usage history;
- `/app/billing` — current Free plan, remaining lifetime allowance, purchased-credit balance and plan-selection/change entry;
- `/app/billing/select` — Shopify-hosted App Pricing for a future plan change;
- `/app/merchant-support` — merchant messages/support;
- `/app/pending-recoveries` — merchant-scoped resource endpoint where otherwise permitted by the existing product flow.

`moda-interact-admin` is never a merchant surface.

`/app/billing/options` in the supplied snapshot remains prototype/mock-driven and MUST NOT become an entitlement authority as part of this transition. Its production reconciliation belongs to the later capacity/plan-change UI iteration.

## Runtime services after transition

The Free merchant becomes eligible for capabilities enabled by the mapped `BillingPlanFeature` rows. Do not hardcode plan capabilities in route code.

Current ARCH-007 Free admission remains:

```text
mapped ACTIVE/TRIALING Free plan
        -> resolve effective billing policy
        -> reserve from lifetime Free allowance
        -> successful provider initiation commits one lifetime Free unit
        -> use purchased lifetime credits first when available
        -> when purchased credits are exhausted, use remaining shop-lifetime Free credits
        -> otherwise block the new recovery and surface the capacity-exhausted merchant message
```

Free activation creates no promotional credits automatically. If promotional credits were granted separately, they participate in the canonical Free capacity order `promotional -> purchased -> lifetime Free -> BLOCK NEW RECOVERY ADMISSION` without changing Free activation semantics.

## Onboarding completion invariant

`ShopSettings.onboardingCompleted` means the merchant has successfully activated a verified current plan at least once; it is not itself proof that the merchant currently has entitlement forever.

For this transition it may move:

```text
false -> true
```

only after the callback has re-synchronised Shopify and verified that the callback `plan_handle` is the **current** mapped Free plan.

Do not set it true for:

- `NO_CONTRACT`;
- `UNMAPPED`;
- `SYNC_ERROR`;
- callback handle mismatch;
- a pending-only plan match;
- Partner API failure.

Once true, later cancellation/uninstall behaviour is handled by their own lifecycle transitions rather than resetting onboarding here.

## Idempotency and historical Free usage

Free activation/re-activation MUST NOT:

- reset `ShopEntitlementCounter`;
- decrement `committedQuantity`;
- clear `reservedQuantity`;
- grant five new units by incrementing a counter;
- create duplicate allowance records;
- erase purchased top-up balances.

The shop-lifetime Free allowance is derived only from the canonical shop counter snapshot and durable usage. First production has no signed Free-allowance adjustment compatibility. The current Shopify plan does not own or reset the lifetime grant; all discretionary capacity uses campaign-linked promotional grants.

Example:

```text
merchant previously used 3 of 5 Free recoveries
merchant later returns to Free
remaining Free allowance = 2, not 5
```

## Shopify interactions

Required at activation callback:

```text
Shopify redirect includes plan_handle
        -> authenticate merchant request
        -> resolve durable Shop
        -> Partner API activeSubscription(appId, shopId)
        -> require exactly one active FlatRatePrice current plan handle
        -> map exact handle to active BillingPlan
        -> verify callback plan_handle == current mapped Free handle
        -> persist subscription projection
        -> set onboardingCompleted = true
        -> redirect /app
```

No Billing API `appSubscriptionCreate` or internal Free subscription is introduced.

## BullMQ behaviour

No new BullMQ contract/job is required solely to activate Free.

The existing async recovery pipeline consumes Free entitlement after activation. Billing-cycle delayed reconciliation introduced later for paid-period rollover is not required to replenish Free because Free allowance is lifetime.

## Failure behaviour

- Partner API transport/provider failure: do not change onboarding completion or entitlement; propagate/surface existing safe billing failure behaviour.
- Unknown/inactive local plan mapping: persist/retain fail-closed projection; do not complete onboarding.
- Pending-only callback plan: do not complete onboarding as though the future plan were active.
- Shop becomes unavailable/uninstalled during callback: existing shop access policy applies; do not activate merchant services.
- Failure while setting `onboardingCompleted=true` after subscription projection succeeds: do not fabricate success. Retrying the callback/sync must be safe and eventually complete onboarding without resetting credits.

## Tasks created by this iteration

- `ARCH-010-SHOPIFY-002` — complete onboarding only after verified current Free activation and expose normal merchant behaviour without resetting lifetime Free usage.

No new Database, Shared, Background, Gateway, Admin or System-Test task is required solely for this transition. Broader ARCH-010 data-model and paid billing-period lifecycle work is owned by the separate tasks/sections later in this architecture.

## Next iteration

Initial Paid-plan activation from Installed / No Plan. This is separate because it creates period-scoped included entitlement and establishes the first paid billing-period lifecycle.

## Iteration 2 refinement — durable asynchronous subscription activation verification

### Why this refinement exists

A Shopify App Pricing redirect with `plan_handle` records what the merchant selected, but the callback parameter is not durable entitlement proof. A fresh merchant may return before `activeSubscription` reflects the selected plan, or Moda's own Partner API verification request may fail transiently. ARCH-010 therefore separates **selection intent** from **verified current subscription state**.

### Durable state combinations

Do not introduce a new projection status only for this waiting condition. Use the existing fields plus one durable scheduling field:

```text
NO_CONTRACT + pendingPlanId = null
    -> installed merchant has not selected a verifiable plan

NO_CONTRACT + pendingPlanId != null
    -> initial plan selection has been recorded locally but Shopify has not yet
       verified that plan as the current active subscription

ACTIVE/TRIALING + pendingPlanId != null
    -> a current subscription exists and Shopify/local projection contains a
       future plan change; later ARCH-010 iterations define its boundary behaviour
```

For an initial selection waiting on verification:

```text
pendingShopifyPlanHandle = callback plan_handle after local BillingPlan mapping
pendingPlanId            = mapped active BillingPlan.id
pendingEffectiveAt       = time the immediate activation was requested/recorded
nextReconcileAt          = next durable time Moda should ask Shopify again
```

`pendingEffectiveAt` means the expected provider effective time. For first activation the expectation is immediate, so recording `now` is valid. For later plan changes it remains the future Shopify billing-cycle boundary.

### Callback behaviour

For a locally recognised active Free plan handle:

1. authenticate and resolve the Shop;
2. record the pending selection intent durably before relying on Redis;
3. attempt the existing Partner `activeSubscription` sync once for the fast path;
4. if Shopify verifies the requested handle as the **current** mapped Free plan, complete Iteration 2 immediately and clear the pending activation schedule;
5. if Shopify returns no current subscription, or the requested handle is not current yet, keep onboarding incomplete, retain the pending selection, set `nextReconcileAt`, and publish a best-effort BullMQ reconciliation hint;
6. if the Partner API call itself fails, preserve the durable selection/current state, record sync-error metadata, set `nextReconcileAt`, publish the same best-effort hint, and return the merchant to `/app` onboarding rather than converting the failure into `NO_CONTRACT` entitlement truth.

There are two materially different provider-failure locations:

```text
Shopify-hosted pricing fails before redirect
    -> Moda receives no callback and has nothing new to persist;
       merchant later re-enters `/app` onboarding.

Shopify redirects successfully, then Moda's Partner API verification fails
    -> callback intent already exists locally;
       preserve it and let Background reconcile asynchronously.
```

### Merchant behaviour while initial activation is pending

Until Shopify verifies a current mapped subscription:

```text
ShopSettings.onboardingCompleted = false
Subscription.status              = NO_CONTRACT
pendingPlanId                    = selected plan
```

The merchant remains on the normal `/app` onboarding experience. No recovery/product entitlement is granted. A refresh may simply show onboarding again; a special blocking error page is not required.

The UI may show non-authoritative wording such as "Confirming your plan" when a pending target exists, but this is not required for correctness and must not grant access.

### BullMQ subscription reconciliation contract

Cross-repository contract owner: `moda-interact-shared`.

Canonical queue/job target for this architecture:

```text
queue: billing-subscription-reconcile
job:   reconcile-subscription
```

Payload v1 contains only durable lookup/staleness data:

```text
schemaVersion
shopId
subscriptionId
expectedNextReconcileAt  // ISO-8601 timestamp
```

The payload MUST NOT contain authoritative plan/credit state. The consumer reloads PostgreSQL and Shopify.

A deterministic job ID is derived from `subscriptionId + expectedNextReconcileAt`. This allows application publication and restart/repair reconstruction to converge on the same queued work.

### Background consumer behaviour

`moda-billing-worker` owns the BullMQ consumer. On a reconciliation job it must:

1. validate the Shared payload;
2. reload Shop + Subscription + pending plan from PostgreSQL;
3. no-op if Shop is not ACTIVE, pending state disappeared, or `nextReconcileAt` no longer equals `expectedNextReconcileAt` (stale job);
4. call the existing Shopify Partner `activeSubscription` provider;
5. if the pending target is now the verified current mapped Free plan, transactionally update the subscription projection, clear pending activation fields/`nextReconcileAt`, and set `ShopSettings.onboardingCompleted = true`;
6. if Shopify successfully reports no current subscription yet, preserve `NO_CONTRACT + pendingPlanId`, advance `nextReconcileAt`, and enqueue the next delayed reconciliation;
7. if the Partner API call fails, preserve the last-known projection/status, update `lastSyncErrorCode/lastSyncErrorAt`, advance `nextReconcileAt`, and enqueue the next delayed reconciliation;
8. never grant Free lifetime usage, create a paid period allowance, or perform future upgrade/downgrade logic in this iteration.

A transport/provider failure MUST NOT change an otherwise known ACTIVE/TRIALING subscription to `SYNC_ERROR` merely because Shopify could not be reached. `SYNC_ERROR` remains appropriate for a verified incompatible projection such as a required usage meter being absent; transport failure is recorded in sync-error metadata while preserving last-known entitlement state.

### Retry timing

For Iteration 2 use one explicit bounded initial-activation retry policy, computed from `pendingEffectiveAt` so no additional attempt counter is required:

```text
pending age < 10 minutes   -> retry in 1 minute
pending age < 1 hour       -> retry in 5 minutes
pending age < 24 hours     -> retry in 30 minutes
pending age >= 24 hours    -> stop automatic retries, clear pending activation
                               scheduling/target, remain NO_CONTRACT/onboarding
```

A new plan selection replaces the previous pending target and starts a new pending-effective timestamp. Uninstall clears/suppresses scheduling through the uninstall lifecycle.

### Redis/BullMQ outage recovery

PostgreSQL is the source from which queue work can be rebuilt.

The billing worker must run a queue-repair pass:

- once during billing-worker startup; and
- periodically while the worker remains alive, so a Redis flush/replacement is recovered without requiring a process restart.

The repair query selects only actionable durable rows, not every `NO_CONTRACT` shop:

```text
Shop.status = ACTIVE
Subscription.pendingPlanId IS NOT NULL
Subscription.nextReconcileAt IS NOT NULL
```

For each row, add the deterministic job using:

```text
delay = max(0, nextReconcileAt - now)
```

Duplicate-add because the same deterministic job already exists is benign. Queue publication/repair failure must not roll back durable subscription state.

### Existing billing-worker interaction

The existing ARCH-007 billing worker also performs usage publication and rotating subscription/usage reconciliation. ARCH-010 does not duplicate that deployable service. It adds a dedicated BullMQ subscription-reconciliation consumer to the existing billing-worker runtime.

The existing periodic reconciliation path must be made compatible with pending activation:

- successful provider `null` must not accidentally erase a locally durable initial activation target before its retry window expires;
- Partner transport failure must not overwrite last-known entitlement status with `SYNC_ERROR`;
- existing usage publication/reconciliation duties remain in place unless a later ARCH-010 iteration deliberately changes them.

### Infrastructure implication

In the inspected workspace, `moda-billing-worker-production` and `moda-billing-worker-test` do not currently import their Redis environment groups. The new BullMQ consumer therefore requires a bounded `moda_gateway` change adding the existing environment-specific Redis group to those two billing-worker service declarations. No new Render service is required.

### Task decomposition for this refinement

- `ARCH-010-DATABASE-001` — add durable subscription reconciliation scheduling.
- `ARCH-010-SHARED-001` — define canonical subscription-reconciliation BullMQ contract.
- `ARCH-010-SHARED-002` — publish the accepted Shared contract.
- `ARCH-010-BACKGROUND-001` — consume/retry/rebuild pending subscription reconciliation using Shopify verification.
- `ARCH-010-GATEWAY-001` — give the existing billing worker `REDIS_URL` through the canonical Render Redis env groups.
- `ARCH-010-SHOPIFY-002` — revised to persist pending Free selection and publish a best-effort reconciliation hint when immediate verification is unresolved.



# Iteration 3 — Installed / No plan -> Paid plan active / first billing period

## Scope

This iteration defines **first activation of a paid Shopify App Pricing plan** for a merchant who does not yet have a current Moda plan. It does not define an upgrade/downgrade from an already-active plan and does not yet define end-of-cycle renewal/rollover.

The transition is materially different from Free activation because a paid merchant cannot become fully operational until Moda has an exact Shopify `currentBillingCycle` and has created the local period-scoped included-credit entitlement for that cycle.

## Source state

Normal first-install source:

```text
Shop.status                      = ACTIVE
ShopSettings.onboardingCompleted = false
Subscription.status              = NO_CONTRACT
Subscription.planId              = null
Subscription.current billing period = null
pending paid selection           = null or a locally recorded callback intent
Free lifetime usage              = preserved durable value, normally 0
purchased top-up balance         = preserved durable value, normally 0
promotional credit balance       = preserved durable value, normally 0
```

`LIFETIME_FREE_RECOVERY_CREDITS` is the canonical shop-lifetime counter and remains distinct from campaign-linked `PromotionalCreditGrant` lots. Both may be available under Free or Paid when the subscription is executable, but a usable selected promotion is consumed first and promotional capacity is created only through the campaign model.

## Trigger

The merchant selects a locally recognised paid plan on Shopify's hosted App Pricing page and Shopify redirects to the billing callback with `plan_handle`, or a previously recorded pending paid selection is later reconciled by the billing worker.

The callback `plan_handle` is selection intent only. Entitlement requires Partner API `activeSubscription(appId, shopId)` verification.

## Required Shopify verification

A first paid activation is valid only when all of the following are true at the same observation:

```text
activeSubscription != null
current FlatRatePrice plan handle == requested/pending plan handle
local BillingPlan exists and active
BillingPlan.kind == PAID_METERED
required normal recovery usage meter is configured locally
provider active subscription contains that exact usage meter handle
currentBillingCycle.startTime != null
currentBillingCycle.endTime != null
startTime < endTime
BillingPlan.includedRecoveryConversationAllowance is a non-negative safe integer
```

Do not infer a billing period from local time, calendar month, installation time, callback time, or `trialEndsAt`.

### Paid trials

Shopify currently documents that `currentBillingCycle` is `null` while a subscription is in trial and is populated after the trial ends. ARCH-010 does not invent a synthetic billing period for such a trial.

For the current product, paid trials are **unsupported**. Paid Shopify App Pricing plans should be configured without a trial. If a paid subscription is observed as `TRIALING` with no `currentBillingCycle`, Moda must fail closed for paid recovery entitlement and must not complete first-paid onboarding from that state. This is a provider-plan configuration incompatibility to surface operationally; trial-specific entitlement design is a future architecture if the product later wants trials.

## Target durable state

After successful current paid verification and first-period creation:

```text
Shop.status                         = ACTIVE
ShopSettings.onboardingCompleted    = true
Subscription.status                 = ACTIVE
Subscription.planId                 = verified paid BillingPlan.id
Subscription.observedShopifyPlanHandle = verified current handle
Subscription.currentPeriodStart     = Shopify currentBillingCycle.startTime
Subscription.currentPeriodEnd       = Shopify currentBillingCycle.endTime
Subscription current billing-period pointer = first paid BillingPeriod
Subscription pending initial-selection fields = cleared

BillingPeriod
  shopId       = shop
  periodStart  = exact Shopify startTime
  periodEnd    = exact Shopify endTime
  status       = OPEN

BillingPeriodEntitlementCounter
  billingPeriodId   = first paid period
  counter           = INCLUDED_RECOVERY_CREDITS
  grantedQuantity   = BillingPlan.includedRecoveryConversationAllowance
  committedQuantity = 0
  reservedQuantity  = 0
  forfeitedQuantity = 0

Free lifetime counter        = unchanged
Purchased top-up balance     = unchanged
Promotional lifetime balance = unchanged
```

Creating/replaying this transition must not reset an already-existing first-period counter. If the exact period already exists and its included counter already contains committed/reserved usage, replay reuses it.

If an exact existing period counter's `grantedQuantity` conflicts with the allowance that was snapshotted/expected for that same period, fail closed and surface a billing projection incompatibility; do not rewrite historical entitlement underneath existing usage.

## First paid period creation transaction

The current paid projection, period and included-credit counter must become usable atomically. The transaction must:

1. re-read the Shop, Subscription and target BillingPlan;
2. verify the source remains an initial/no-current-plan activation rather than an upgrade/downgrade;
3. verify the provider observation being applied still corresponds to the expected paid plan and exact cycle;
4. upsert/reuse the exact `BillingPeriod(shopId, periodStart, periodEnd)`;
5. create/reuse the unique period included-credit counter;
6. never reset an existing counter on replay;
7. update Subscription current plan/status/cycle/current period pointer;
8. clear initial pending target/scheduling fields that existed only to obtain activation;
9. set `ShopSettings.onboardingCompleted = true` only after the paid period/counter are valid;
10. commit as one database transaction.

A merchant must never reach `onboardingCompleted=true + paid active` while the current paid period or its included-credit counter is missing.

## Paid included-credit admission after activation

The existing ARCH-007 paid path decides whether included allowance remains by aggregating normal paid `UsageEvent` quantity. That check is not a concurrency-safe reservation boundary.

ARCH-010 changes paid admission to:

```text
new recovery
   |
   v
resolve ACTIVE mapped PAID_METERED policy
   |
   v
require exact OPEN current BillingPeriod
   |
   v
reserve 1 from that period's INCLUDED_RECOVERY_CREDITS counter
   |
   +-- reserved --> initiate provider send
   |                  |
   |                  +-- success --> commit period reservation
   |                  |              + create normal paid Shopify-meter UsageEvent +1
   |                  |
   |                  +-- definitive failure --> release reservation
   |                  +-- ambiguous failure  --> mark reservation ambiguous
   |
   +-- included exhausted --> promotional credits
                               |
                               +-- available --> reserve/consume promotional credit
                               |                (no normal paid recovery meter event)
                               |
                               +-- unavailable --> purchased lifetime credits
                                                   |
                                                   +-- available --> reserve/consume purchased credit
                                                   |                (no normal paid recovery meter event)
                                                   |
                                                   +-- unavailable --> shop-lifetime Free
                                                                       |
                                                                       +-- available --> reserve/consume lifetime Free
                                                                       |                (no normal paid recovery meter event)
                                                                       |
                                                                       +-- unavailable --> BLOCK NEW RECOVERY ADMISSION
                                                                                          (no provider send; no recovery UsageEvent)
```

The normal Shopify recovery meter receives +1 only for Paid recoveries funded by the current period's included allowance. Promotional-, purchased- and shop-lifetime-Free-funded recoveries remain excluded from the normal recovery meter. ARCH-010 does **not** permit automatic paid overage: Paid recovery is blocked only when included, promotional, purchased and lifetime Free sources are all exhausted.

The period counter therefore controls Moda routing; Shopify remains commercial billing authority for reportable included-plan usage.

## Merchant screens after successful paid activation

The merchant leaves onboarding and may access the normal merchant application, subject to the mapped plan features and platform/shop safety policy:

```text
/app
/app?view=detail
/app/usage
/app/billing
/app/billing/select
/app/merchant-support
/app/pending-recoveries
```

`moda-interact-admin` is never a merchant surface.

The billing screen must present at least:

- current paid plan name/status;
- exact current Shopify billing-period start/end;
- included recovery allowance granted for this period;
- included committed/reserved/remaining capacity;
- purchased top-up balance separately;
- pending plan change separately when Shopify reports one;
- plan-change link to Shopify-hosted pricing.

A merchant may purchase a new recovery-credit pack only when the existing ARCH-008 exact-current-cycle and meter verification rules pass. First paid activation does not weaken those checks.

## Service availability after successful paid activation

Availability is not hard-coded from the plan name. The existing `BillingPlanFeature` mappings remain authoritative for merchant/business capabilities.

A successfully activated paid merchant may use `CHECKOUT_RECOVERY`, `AI_CONVERSATIONS`, `PRODUCT_SEARCH`, `ORDER_SUPPORT`, and other mapped capabilities only when their respective plan feature is enabled and existing platform/shop safety controls allow them.

Background entitlement must fail closed if any paid-period invariant is missing even when `Subscription.status = ACTIVE`:

```text
current BillingPeriod missing
current period not OPEN
period boundaries do not match Subscription projection
period included-credit counter missing
period counter invalid/inconsistent
paid normal usage meter mapping missing
```

## Async activation recovery

Iteration 2's existing `billing-subscription-reconcile / reconcile-subscription` contract is reused; do not create another queue.

For `NO_CONTRACT + pending paid target`, the billing worker verifies Shopify just as for Free. When the requested paid plan is now current and all paid-cycle invariants pass, Background may perform the same first-period activation transaction and set onboarding complete.

If Shopify still returns null or the Partner request fails, use the already-agreed bounded initial-activation retry policy.

If Shopify returns the paid plan as current but the cycle/meter/allowance configuration is invalid, do **not** treat that as transient `null` activation and do not grant access. Record/surface a verified projection/configuration error. In particular, an unsupported paid trial must not cause a 1-minute retry loop intended for provider propagation.

## Billing-period scheduling boundary

On first paid activation, persist the authoritative `currentPeriodEnd`. The complete **end-of-period close/open transition and its BullMQ scheduling/reconstruction behaviour will be defined in the normal-renewal iteration**.

Do not implement an incomplete period-end job in this iteration. ARCH-010 will only enable production period-boundary scheduling once the rollover transition is fully specified and task dependencies are reconciled.

## Failure behaviour

- Callback `plan_handle` alone: persist/retain intent only; do not activate.
- Partner API returns null: remain onboarding/NO_CONTRACT and use Iteration 2 async retry policy.
- Partner API transport failure: preserve local known state; use Iteration 2 retry policy.
- Unknown/inactive local paid plan: fail closed as UNMAPPED/configuration state.
- Required paid usage meter absent from provider subscription: fail closed as verified synchronization/configuration error.
- Current billing cycle absent: do not create a paid BillingPeriod. Trial-specific case follows the unsupported-trial rule above.
- Database transaction failure: onboarding remains incomplete; replay must be safe.
- Redis unavailable: durable pending activation remains in PostgreSQL and Iteration 2 queue repair reconstructs verification work.

## Current implementation facts requiring change

The supplied workspace currently:

- creates/reuses `BillingPeriod` directly from `currentBillingCycle` in both application and Background reconciliation;
- stores only one current `Subscription.billingPeriodId` pointer;
- has no period-scoped included-credit reservation counter;
- treats PAID_METERED admission as immediately admitted unless purchased credits are selected, with no included-capacity reservation;
- decides the included -> purchased boundary by aggregating normal paid `UsageEvent` quantity;
- can therefore make the boundary decision concurrently without a period reservation;
- currently allows a paid policy to resolve with no billing period;
- already verifies exact current cycles for **new top-up purchases** under ARCH-008; that protection must remain.

## Tasks created by this iteration

- `ARCH-010-DATABASE-002` — add the period-scoped included-credit counter and reservation linkage required for concurrency-safe paid allowance consumption.
- `ARCH-010-BACKGROUND-011` — make the lifetime Free grant plan-independent and provide the final lifetime-Free fallback after purchased capacity.
- `ARCH-010-BACKGROUND-002` — implement the concurrency-safe Paid included-credit reservation primitive; `BACKGROUND-019` later composes promo-first cross-bucket routing.
- `ARCH-010-BACKGROUND-003` — extend the existing ARCH-010 subscription reconciliation consumer/service to complete first paid activation and create the first paid period/counter asynchronously.
- `ARCH-010-SHOPIFY-003` — implement first paid callback fast-path activation, transactional first-period/counter creation and onboarding completion.
- `ARCH-010-SHOPIFY-004` — present the period-scoped paid allowance and keep merchant route/service exposure aligned with the activated paid state.

No new Shared queue contract, Gateway service, Admin merchant UI or System-Test task is required in this iteration. Iteration 2's queue contract/Redis wiring are reused. Integrated system-test tasks remain terminal and will be defined after the complete ARCH-010 implementation graph is known.

## Next iteration

Uninstall and reinstall behaviour, including preservation of Free lifetime usage, purchased/promotional lifetime balances, subscription reconciliation on reinstall, and suppression/reconstruction of lifecycle jobs.

---

# Iteration 4 — Uninstall as an execution gate

## Agreed product rule

Uninstall is **not** a billing-state reset and is **not** a credit reset.

The uninstall webhook means only:

```text
Shop.status = UNINSTALLED
uninstalledAt = Shopify webhook event time
```

From that point Moda must not start or continue new shop-owned customer/business work for the shop.

Do **not** mutate merely because of uninstall:

```text
Subscription current plan/status/history
Subscription current BillingPeriod pointer
Subscription pending plan-change state
BillingPeriod history
period included-credit counters
LIFETIME_FREE_RECOVERY_CREDITS usage/counter state
purchased top-up lots/balance
promotional recovery-credit balance
refund state
ShopSettings.onboardingCompleted
```

The existing Shopify session deletion remains appropriate.

## Why Subscription must not be changed to NO_CONTRACT on uninstall

The supplied implementation currently sets `Subscription.status = NO_CONTRACT` from `ShopService.markUninstalled()`.

ARCH-010 removes that coupling. `Shop.status` is the execution gate. The subscription projection remains the last durable Shopify billing observation until reinstall/reconciliation explicitly establishes newer Shopify truth.

This separation is required so uninstall does not masquerade as a billing transition or destroy the state needed to reason about reinstall, lifetime balances, refunds, historical usage, or the previous paid period.

## Runtime execution invariant

For shop-owned customer/business processing:

```text
Shop.status == ACTIVE
```

is mandatory.

If the shop is `UNINSTALLED` or `SUSPENDED`, a queued job that can identify that shop must become an idempotent terminal no-op before it:

- creates or mutates CheckoutRecovery business state;
- refreshes recovery state from Shopify;
- schedules a new recovery candidate;
- performs a Shopify business-data lookup for recovery execution;
- creates or appends customer conversation state;
- invokes CommerceAgent / an LLM;
- reserves or commits recovery entitlement;
- sends a WhatsApp message;
- creates new business usage caused by post-uninstall work;
- enqueues a follow-up conversation/recovery action.

The worker must not throw a retryable error merely because the shop is uninstalled. Uninstall is a terminal eligibility decision for that job execution.

## Existing queued Shopify work

Shopify normally stops delivering app webhooks after uninstall, but jobs accepted before the uninstall webhook can still be in Redis/BullMQ.

Therefore absence of future Shopify webhook delivery is **not** sufficient protection.

The Background runtime must gate at durable execution boundaries using current `Shop.status`.

At minimum the supplied implementation requires inactive-shop guards around:

- checkout-created candidate scheduling;
- checkout-update handling;
- cart-activity handling;
- order-completion handling where further recovery work would be performed;
- matured pending-recovery candidate materialisation;
- any provider lookup or recovery mutation reached from those jobs.

Pending candidate indexes/jobs may be cleaned up as required to make the inactive job terminal. Cleanup is not merchant business execution.

## WhatsApp ingress and the known tenant-identification limitation

The Meta/WhatsApp ingress service deliberately normalises and enqueues events without a deterministic `shopId` in the event contract. ARCH-010 does **not** redesign that identity model.

Therefore `moda-interact-messaging` may still:

```text
receive authenticated Meta webhook
-> validate/normalise
-> enqueue whatsapp-events
```

when the ingress layer cannot yet identify the owning shop.

The earliest reliable execution gate is in `moda-interact-background` after durable routing/ownership resolution identifies a shop.

Once an inbound WhatsApp message resolves to an inactive shop, Background must stop before conversation mutation, CommerceAgent invocation, outbound admission or follow-up job creation.

When ownership cannot be determined deterministically, preserve the existing unresolved/ambiguous behaviour. Do not invent a new shop-identification heuristic for ARCH-010.

This known limitation is explicitly accepted for this architecture iteration.

## WhatsApp provider-status bookkeeping

Provider delivery/read/failure statuses for an outbound message that was legitimately sent before uninstall are historical completion/bookkeeping, not new customer/business execution.

ARCH-010 may continue to apply idempotent provider-status updates to those already-existing outbound messages. It must not use such a status event to initiate new customer work for an uninstalled shop.

## Pre-uninstall usage/accounting finalisation

Already-committed accounting for work performed before `uninstalledAt` may finish after uninstall when required for durable correctness.

The supplied `ShopifyUsageEventPublisherService` already distinguishes the uninstall cutoff and permits pre-uninstall usage events while rejecting post-uninstall work. Preserve that behaviour.

Do not create a rule that strands or silently deletes valid pre-uninstall committed usage merely because publication happens after the uninstall webhook.

## Billing reconciliation while uninstalled

The supplied billing reconciliation scanner already selects only `Shop.status = ACTIVE`. Preserve that gate.

ARCH-010 subscription delayed-reconciliation/startup-repair work must also exclude an uninstalled shop from ordinary activation/plan-change processing unless a later reinstall transition explicitly authorises reconciliation for that shop.

Uninstall must not cause a BullMQ plan-reconciliation job to reactivate the shop.

## Merchant screens after uninstall

The app session is removed. The merchant therefore has no merchant application surface while uninstalled.

`moda-interact-admin` remains internal-only and is unaffected by this merchant lifecycle state.

No special merchant uninstall screen is required by this iteration.

## Reinstall coupling — intentionally deferred

The supplied implementation currently calls `markInstalled()` during authenticated Shopify app access and changes an `UNINSTALLED` shop directly back to `ACTIVE`.

After this iteration preserves Subscription billing state on uninstall, blindly reusing that current reinstall behaviour could temporarily reactivate stale entitlement before Shopify truth has been reconciled.

Therefore the Shopify uninstall task defined by this iteration is **pending and must not be executed until the reinstall transition is agreed in the next ARCH-010 iteration**.

The Background inactive-shop guards are independently safe and may be implemented first.

## Explicit non-goals

This iteration does not:

- make shop/tenant identification deterministic;
- add `shopId` to the normalized WhatsApp ingress contract;
- redesign phone-number ownership/routing;
- change the Meta webhook ingress topology;
- purge all Redis jobs on uninstall;
- delete merchant data;
- cancel/refund subscriptions;
- refund purchased top-ups;
- alter lifetime-credit balances;
- define reinstall entitlement reconciliation;
- define billing-period rollover.

## Tasks created by this iteration

- `ARCH-010-BACKGROUND-004` — add the inactive-shop execution gate to queued Shopify/recovery work and preserve only required pre-uninstall accounting finalisation.
- `ARCH-010-BACKGROUND-005` — gate inbound WhatsApp/conversation execution after shop ownership is resolved, while preserving historical provider-status bookkeeping and the existing ambiguous-tenant model.
- `ARCH-010-SHOPIFY-005` — change uninstall persistence to `Shop.status/uninstalledAt` plus session deletion only; preserve subscription/billing/credit state. This task remains pending until reinstall semantics are agreed because current `markInstalled()` would otherwise reopen stale entitlement.

No Database, Shared, Messaging, Gateway, Admin or System-Test implementation task is required for this iteration.

## Next iteration

Reinstall: authenticated return of an existing `UNINSTALLED` Shop, fail-closed Shopify subscription reconciliation before business execution resumes, and reuse of preserved lifetime balances without solving the accepted shop-identification limitation.

---

# Iteration 5 — Reinstall with fail-closed Shopify reconciliation

## Scope and source state

This iteration begins only when the current shop-identification mechanism resolves an authenticated Shopify installation to an existing durable Shop whose state is:

```text
Shop.status = UNINSTALLED
```

The imperfect/non-deterministic shop-identification problem accepted in Iteration 4 remains explicitly out of scope. ARCH-010 does not introduce a second identity heuristic merely to improve reinstall matching.

Uninstall has preserved the last known Subscription projection, BillingPeriod/history, Free lifetime usage, purchased lifetime top-ups, promotional recovery credits, refund state, and `ShopSettings.onboardingCompleted`. Those values are historical/local state only until Shopify is reconciled.

## Architectural principle

A successful Shopify OAuth/authenticated return proves only:

```text
the app is installed again
```

It does **not** prove:

```text
the old subscription is still current
```

Therefore reinstall is a two-stage transition:

```text
UNINSTALLED
   -> REINSTALL RECONCILIATION PENDING (execution still disabled)
   -> Shopify Partner activeSubscription reconciled
   -> ACTIVE with verified entitlement, or ACTIVE/NO_CONTRACT onboarding
```

ARCH-010 does not add a new `ShopStatus`. While reconciliation is pending the Shop remains `UNINSTALLED`, which continues to provide the already-agreed hard execution gate. A separate nullable durable marker records that an authenticated reinstall has occurred and authorises the billing worker to make the otherwise-forbidden reconciliation call for this uninstalled shop.

## Durable reinstall marker

Add to `Shop`:

```text
reinstallPendingAt DateTime?
```

Meaning:

```text
NULL
  -> no authenticated reinstall is awaiting reconciliation

non-NULL + Shop.status=UNINSTALLED
  -> Shopify has authenticated the app again, but Moda has not yet
     established safe current billing truth; customer/business execution
     remains disabled
```

The marker is scheduling/execution metadata, not subscription truth.

`Subscription.nextReconcileAt` remains the durable wake-up schedule. Redis/BullMQ remains disposable.

## Reinstall trigger

Current `app/routes/auth/catchall/route.jsx` resolves the authenticated shop and calls `markInstalled()`, which immediately changes `UNINSTALLED -> ACTIVE`.

That direct transition is no longer allowed.

For an existing `UNINSTALLED` shop, authenticated re-entry must instead atomically/best-effort establish:

```text
Shop.status              = UNINSTALLED     // deliberately unchanged
Shop.reinstallPendingAt  = existing value or now
Shop.uninstalledAt       = preserved until reconciliation completes
Subscription.nextReconcileAt = now
```

If a Subscription projection is unexpectedly absent for a resolved historical Shop, create the normal `NO_CONTRACT` projection rather than activating from stale assumptions.

Then best-effort enqueue the canonical ARCH-010 subscription-reconciliation BullMQ job using the Shared deterministic contract. Queue publication failure must not undo the PostgreSQL marker/schedule; startup/periodic reconstruction must recover it.

Repeated authenticated requests while the same reconciliation attempt is pending must **not** reset `reinstallPendingAt`, because that timestamp bounds retry age. An explicit merchant `Retry restoration` action after automatic retries stop may start a new attempt and reset the marker/schedule.

## Merchant UI while reconciliation is pending

The merchant must not enter the normal product, recovery, usage or billing-purchase surfaces while:

```text
Shop.status = UNINSTALLED
Shop.reinstallPendingAt != null
```

Allowed authenticated merchant surfaces are limited to:

```text
/app/reinstalling
/app/merchant-support   // pending-reinstall-safe support access only
```

`/app/reinstalling` is a merchant-facing Shopify app route owned by `moda_app`. It must not read recovery/customer/conversation data. It presents bounded states such as:

```text
Restoring your Moda Interact account…

or, after automatic retry exhaustion:
We couldn't verify your Shopify subscription automatically.
[Try again] [Contact support]
```

The route may read the local reinstall marker/schedule/status. It must not itself become a second polling loop against Shopify.

All normal merchant routes continue to fail closed until the worker completes reconciliation.

`moda-interact-admin` remains internal-only and is never part of this merchant flow.

## Background reconciliation exception for an uninstalled Shop

Iteration 4 established that ordinary billing/background work ignores an `UNINSTALLED` Shop.

Iteration 5 introduces exactly one narrow exception:

```text
Shop.status = UNINSTALLED
AND Shop.reinstallPendingAt != null
AND Subscription.nextReconcileAt matches the queued expected time
```

may execute the subscription-reconciliation job.

No recovery, WhatsApp, CommerceAgent, entitlement consumption or other customer/business work is authorised by that exception.

The worker calls the existing Shopify Partner API `activeSubscription(appId, shopId)` provider and uses the returned provider state as subscription authority.

## Provider result A — successful null

A successful Partner response with:

```text
activeSubscription = null
```

means Moda has no verified current Shopify App Pricing contract to grant.

Transactionally establish:

```text
Subscription.status = NO_CONTRACT
Subscription.planId = null
Subscription.observedShopifyPlanHandle = null
Subscription.billingPeriod/current pointer = null
Subscription current provider-cycle fields = null
Subscription pending plan fields = null
Subscription.nextReconcileAt = null
Subscription.lastSyncedAt = now
Subscription.lastSyncErrorCode/At = null

ShopSettings.onboardingCompleted = false

Shop.status = ACTIVE
Shop.uninstalledAt = null
Shop.reinstallPendingAt = null
```

Do not delete historical BillingPeriod rows or counters in this iteration. A detached historical OPEN period is not spendable because the Subscription no longer points to it and Background admission sees `NO_CONTRACT`. Canonical period close/forfeit reconciliation is owned by the next billing-period transition iteration rather than being reimplemented inside reinstall.

Preserve:

```text
LIFETIME_FREE_RECOVERY_CREDITS committed/reserved history
purchased lifetime top-up balance/lots
promotional recovery-credit balance
purchase/refund history
merchant/recovery/conversation history
```

The merchant is now an installed/no-plan merchant and returns to the normal onboarding/plan-selection behaviour defined by Iteration 1.

## Provider result B — verified current Free plan

If Shopify returns a current plan handle that maps exactly to an active local `BillingPlan.kind = FREE`:

- project current provider truth using the existing billing mapping rules;
- preserve all Free lifetime usage; do not grant/reset the five lifetime conversations;
- do not grant promotional credits;
- clear stale reinstall scheduling/error state;
- set `ShopSettings.onboardingCompleted = true`;
- set `Shop.status = ACTIVE`;
- clear `Shop.uninstalledAt` and `Shop.reinstallPendingAt`.

The merchant resumes the normal Free product surfaces/services. Purchased/promotional lifetime balances remain unchanged.

## Provider result C — verified same paid plan and same exact cycle

A paid reinstall may resume immediately only when all of the following are true:

```text
provider current plan maps to the same active local paid plan
provider has an exact currentBillingCycle
provider current period start/end exactly equal the preserved Subscription period
preserved Subscription.billingPeriodId identifies that same period
required INCLUDED_RECOVERY_CREDITS period counter exists
required paid usage meter mapping is valid
```

Then:

- reuse the existing BillingPeriod;
- reuse its included-credit counter **without changing granted, committed, reserved or forfeited quantities**;
- do not grant a fresh paid allowance;
- update current provider projection fields, `cancelAtEndOfCycle`, pending update projection and sync metadata;
- set onboarding complete;
- set Shop ACTIVE and clear uninstall/reinstall markers.

If `cancelAtEndOfCycle = true` but Shopify still returns the contract as current with the same current cycle, Moda may restore access for that verified current cycle. The later billing-boundary transition owns what happens at its end.

## Provider result D — paid cycle or paid plan no longer aligns

Reinstall must **not** invent upgrade/downgrade or renewal semantics.

If Shopify returns a paid contract but either:

```text
current plan != preserved current plan
OR
current billing cycle != preserved current BillingPeriod
OR
required period counter is missing/inconsistent
```

then keep customer/business execution disabled and record an explicit reconciliation/configuration reason. Do not regrant included credits, do not silently create a replacement period, and do not change plan rank/allowance.

This path is intentionally fail-closed until the next ARCH-010 iteration defines the canonical BillingPeriod close/open transition. That canonical transition will then be reused by both normal renewal and reinstall-after-cycle-advance.

## Provider transport/throttle/5xx failure

A Partner API failure proves nothing about subscription state.

Preserve:

```text
Shop.status = UNINSTALLED
Shop.reinstallPendingAt
all Subscription entitlement/projection fields
all credit state
```

Update only retry/error metadata and `Subscription.nextReconcileAt`, then best-effort enqueue the next deterministic delayed job.

Reuse the bounded activation retry cadence already defined by ARCH-010:

```text
initial short retry -> 5 minute tier -> 30 minute tier
```

for up to 24 hours from `Shop.reinstallPendingAt`.

After 24 hours of transport failure:

```text
Shop remains UNINSTALLED
reinstallPendingAt remains present
nextReconcileAt = null
```

and the restoration screen exposes explicit `Retry restoration` and merchant support. Do not fabricate `NO_CONTRACT`, do not reactivate, and do not clear preserved credits.

An explicit Retry action starts a new bounded attempt by setting `reinstallPendingAt = now`, `nextReconcileAt = now` and best-effort republishing the deterministic job.

## Redis/BullMQ loss and reconstruction

Extend Iteration 2's startup/periodic queue reconstruction to include both classes:

```text
A. ordinary active-shop pending activation
   Shop.status = ACTIVE
   pendingPlanId != null
   nextReconcileAt != null

B. authenticated reinstall reconciliation
   Shop.status = UNINSTALLED
   reinstallPendingAt != null
   nextReconcileAt != null
```

The reconstruction scan only restores BullMQ jobs. It does not call Shopify for every future row.

If Redis is flushed while the process is running, the periodic repair pass recreates missing jobs from PostgreSQL. If the worker restarts, startup reconstruction does the same.

## Screens/services after the transition

### Reconciliation pending / failed temporarily

Available:

```text
/app/reinstalling
merchant support
explicit Retry restoration after bounded retry exhaustion
```

Unavailable:

```text
recoveries
pending recoveries
usage/dashboard
billing top-up purchase
CommerceAgent/customer conversation processing
WhatsApp outbound work
Shopify recovery/customer business processing
entitlement consumption
```

### Shopify confirms no current contract

Result:

```text
Shop ACTIVE
Subscription NO_CONTRACT
onboardingCompleted = false
```

Available: onboarding, Shopify plan selection, support.

Unavailable: recovery/product execution until a plan is subsequently verified.

### Shopify confirms current Free

Normal Free merchant surfaces/services resume using remaining lifetime Free entitlement plus existing fallback rules.

### Shopify confirms same current Paid plan + exact same cycle

Normal Paid merchant surfaces/services resume using the exact existing period counter; there is no allowance reset.

## Task impact from Iteration 4

`ARCH-010-SHOPIFY-005` is superseded before implementation.

Reason: implementing uninstall preservation separately from safe reinstall would create an unsafe intermediate state in which the old `markInstalled()` could expose preserved stale entitlement. `ARCH-010-SHOPIFY-006` therefore owns the app-side uninstall-preservation **and** fail-closed reinstall entry as one coherent repository change.

`ARCH-010-BACKGROUND-004` and `ARCH-010-BACKGROUND-005` remain valid and independently implementable.

## Tasks created by this iteration

- `ARCH-010-DATABASE-003` — add nullable `Shop.reinstallPendingAt` and reconstruction index.
- `ARCH-010-BACKGROUND-006` — extend the canonical subscription-reconciliation queue/worker with the narrow authenticated-reinstall exception, retry/rebuild behaviour, and safe Free/null/same-paid-period outcomes.
- `ARCH-010-SHOPIFY-006` — replace the unsafe direct `markInstalled()` reactivation with durable reinstall scheduling/restoration UI, and absorb the superseded SHOPIFY-005 uninstall-preservation change.
- `ARCH-010-SHOPIFY-005` — superseded, not to be implemented.

No new Shared, Messaging, Gateway or Admin task is required. The existing ARCH-010 Shared reconciliation contract and billing-worker Redis wiring are reused.

## Next iteration

Canonical billing-period transition/renewal: verify Shopify current subscription/cycle and atomically rotate the exact provider BillingPeriod. For Paid, close/forfeit the old monthly included allowance and grant the successor allowance exactly once. For Free, rotate only commercial/App-Event cycle scope and never reset lifetime Free entitlement. The transition is reusable by normal renewal and reinstall.



# Iteration 6 — Canonical Shopify App Pricing BillingPeriod transition / same-plan renewal

## Scope

This iteration defines the one canonical transition used when a currently verified Free or Paid merchant reaches the end of an exact Shopify App Pricing billing cycle and Shopify confirms another current cycle for the **same mapped plan**. Paid periods also replenish the monthly included allowance; Free periods only rotate commercial/App-Event billing scope.

It also provides the transition primitive that a reinstall can reuse when the merchant was uninstalled across one or more billing boundaries but Shopify still reports the same paid plan.

This iteration deliberately does **not** decide provider-observed outcomes where the next current plan is Free, a different Paid plan, or no contract. Those are cancellation/upgrade/downgrade iterations. Until those later transitions are defined, such outcomes fail closed and must not fabricate a period or entitlement.

## Why rollover cannot be a simple job at `periodEnd`

Shopify App Events billing events are scoped to the merchant's current billing cycle. A billing event whose event timestamp falls outside the current cycle can be rejected once the period closes. The existing billing worker publishes due events on its reconciliation loop rather than synchronously in the recovery request path.

Therefore ARCH-010 introduces a short App Pricing billing-period drain window before the boundary for actions that create App Events.

Canonical constant:

```text
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS = 300000  // 5 minutes
```

The drain window is a cross-repository billing policy constant and is exported from `@modainteract/moda-interact-shared/billing`.

## App Pricing period phases

The phases are derived from durable period timestamps; no new persisted merchant subscription status is required.

```text
ACTIVE
  now < periodEnd - 5 minutes

DRAINING
  periodEnd - 5 minutes <= now < periodEnd

EXPIRED / RECONCILING
  now >= periodEnd and Subscription still points at that old period
```

`BillingPeriod.status` remains `OPEN` during ACTIVE and DRAINING. It becomes `CLOSED` only when Shopify has been queried successfully and Moda can atomically install the verified successor period.

## Behaviour during ACTIVE

Normal paid behaviour continues:

```text
included period credits
  -> purchased lifetime credits
  -> recovery blocked
```

Only included-credit-funded paid recoveries create the normal paid Shopify recovery-meter event. Purchased-credit recoveries do not create that meter event. When neither source has capacity, Moda performs no provider send and creates no recovery usage event.

## Behaviour during DRAINING

The merchant remains subscribed and normal read-only merchant screens remain available.

Allowed:

- existing conversation/customer-response processing that does not create a new normal recovery-meter event;
- recovery work funded by an already-active purchased lifetime credit;
- usage/dashboard/billing/support reads;
- Shopify plan-selection navigation.

Temporarily unavailable:

- a new recovery that would consume current-period included allowance;
- purchase of a new recovery-credit pack, because that purchase itself creates a Shopify billing App Event;
- any other new action that requires creating a billing App Event scoped to the closing period.

The merchant UI may describe this as a brief billing-cycle update. It must not expose Admin.

## Free behaviour during DRAINING / RECONCILING

For Free, cycle transition does **not** pause ordinary lifetime-Free or already-purchased-credit recovery admission because those paths do not create a new Shopify billing App Event. It does pause:

- creation of a new recovery-credit-pack purchase;
- any other action that creates an App Event tied to the closing/expired cycle.

When the same mapped Free plan advances to a later exact provider cycle, close the old Free BillingPeriod and create/reuse the successor with `includedRecoveryCreditsGranted = null`; create no included-credit counter and do not reset `LIFETIME_FREE_RECOVERY_CREDITS`.

## Pre-close BullMQ job

After first paid activation or successful rollover, persist:

```text
nextReconcileAt = max(now, currentPeriodEnd - 5 minutes)
```

and best-effort enqueue the existing deterministic `billing-subscription-reconcile/reconcile-subscription` job.

When that job runs before `periodEnd` and the exact expected timestamp still matches durable state:

1. verify the Subscription still identifies the same exact current period;
2. trigger a focused flush of reportable `UsageEvent` rows for that BillingPeriod;
3. do not close the period;
4. set `nextReconcileAt = periodEnd`;
5. commit DB state;
6. best-effort enqueue the exact-boundary reconciliation job.

Redis remains disposable. Startup/periodic reconstruction rebuilds either the pre-close or boundary job from `nextReconcileAt`.

## Boundary reconciliation source state

The normal same-plan renewal transition requires:

```text
Shop.status = ACTIVE
Subscription.status = ACTIVE
Subscription.plan.kind = PAID_METERED
Subscription.billingPeriodId = old BillingPeriod.id
old BillingPeriod.status = OPEN
old period start/end == Subscription currentPeriodStart/currentPeriodEnd
now >= old periodEnd
expectedNextReconcileAt == durable Subscription.nextReconcileAt
```

A safe reinstall may invoke the same period-transition primitive while `Shop.status = UNINSTALLED` only through the explicit authenticated-reinstall reconciliation path defined in Iteration 5. Generic queued business processing never gains that exception.

## Shopify call at the boundary

Call Partner `activeSubscription(appId, shopId)` outside the database transaction.

For this iteration, successful rollover requires:

```text
provider current plan == same mapped active local PAID_METERED plan
provider currentBillingCycle.startTime != null
provider currentBillingCycle.endTime != null
start < end
```

### Provider still reports the old exact cycle

This can occur because a delayed job runs at the precise boundary before Shopify's projection advances.

Do not close/open anything. Preserve the old period and schedule a short retry. Because local `periodEnd` is already reached, new subscription-dependent business execution remains fail-closed until a new cycle is verified.

### Provider reports a later non-overlapping cycle for the same plan

A current cycle is acceptable when:

```text
providerStart >= oldPeriodEnd
providerEnd > providerStart
```

The normal case is exact continuity (`providerStart == oldPeriodEnd`). A later start is also accepted after worker/Redis downtime; Moda creates only the current Shopify cycle and does **not** fabricate skipped periods.

An overlapping but non-identical cycle is invalid and fails closed.

## Atomic close/open transaction

Do not hold a database transaction open while calling Shopify.

After provider verification, use one DB transaction and lock the durable Subscription row before rereading state.

Revalidate the old current period and plan. If another worker already completed the transition, return an idempotent success/no-op.

### 1. Finalize old period reservations

Because DRAINING prevents new normal metered recovery initiation and outbound provider sends are required to have a bounded timeout shorter than the drain window, there should be no legitimate old-period business action still waiting to start at the boundary.

For the old period counter:

- transition remaining `RESERVED` or `AMBIGUOUS` period reservations to `RELEASED` with `releaseReason = PERIOD_CLOSED`;
- decrement `reservedQuantity` by the released quantity;
- no such reservation may later commit against the closed period;
- compute all remaining unconsumed included capacity as forfeited.

Final invariant:

```text
reservedQuantity = 0
committedQuantity + forfeitedQuantity = grantedQuantity
```

Committed reservations remain committed and remain attached to the old period.

### 2. Handle old-period billing events that missed the cycle

Before/while closing, old-period PENDING/RETRYABLE billing App Events receive a final best-effort flush during the drain window.

Once Shopify has definitively advanced to a later cycle, unresolved old-period billing events can no longer be treated as ordinary retryable current-cycle work. Mark them `NEEDS_ATTENTION` with a bounded canonical reason such as `PERIOD_CLOSED_BEFORE_REPORT` and emit a structured domain warning.

If such a row is a recovery-credit-pack purchase billing event, the purchase must not be silently activated; leave/move it to its existing `NEEDS_ATTENTION` workflow.

Do not block opening the verified next period forever because an old event is no longer reportable through the normal current-cycle API path.

### 3. Close the old BillingPeriod

Set:

```text
status      = CLOSED
closedAt    = old.periodEnd
closeReason = RENEWED_SAME_PLAN
```

Unused included credits never roll over.

### 4. Create/reuse the verified successor BillingPeriod

The target period belongs to the same durable Subscription and snapshots the plan that actually governs it.

For a new row persist:

```text
subscriptionId
shopId
planId
shopifyPlanHandleSnapshot
planNameSnapshot
planKindSnapshot = PAID_METERED
includedRecoveryCreditsGranted
periodStart = provider currentBillingCycle.startTime
periodEnd   = provider currentBillingCycle.endTime
status      = OPEN
```

Create/reuse exactly one `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)` with:

```text
grantedQuantity   = snapshotted included allowance
committedQuantity = 0
reservedQuantity  = 0
forfeitedQuantity = 0
```

Replay must never reset an existing target counter. A conflicting target row/counter fails closed.

### 5. Advance Subscription

Update the current projection to the verified successor period:

```text
billingPeriodId   = new period id
currentPeriodStart = provider start
currentPeriodEnd   = provider end
planId             = same verified paid plan
status             = ACTIVE
lastSyncedAt       = now
lastSyncErrorCode  = null
lastSyncErrorAt    = null
nextReconcileAt    = max(now, new periodEnd - 5 minutes)
```

Continue projecting Shopify `cancelAtEndOfCycle` and `pendingUpdate` truth using the existing provider mapping; this iteration does not execute the future plan-change/cancellation outcome.

After commit, best-effort enqueue the new deterministic delayed reconciliation job.

## Concurrency and idempotency

The transition must be safe when:

- the BullMQ job is duplicated;
- the 60-second reconciliation scan observes the same cycle advance;
- Redis is restored and reconstructs an overdue job;
- a reinstall reconciliation and normal boundary reconciliation race;
- two billing-worker instances run concurrently.

The transaction row-lock + unique period identity + one-OPEN-period database invariant are the correctness mechanism. Queue de-duplication alone is not sufficient.

The existing rotating reconciliation path must no longer blindly `upsert(... status: OPEN)` a newly observed period without closing the predecessor.

## BillingPeriod durable-history changes

Iteration 6 strengthens the period model:

- every BillingPeriod belongs to the durable Subscription;
- `Subscription.billingPeriodId` remains the current-period pointer for compatibility;
- one Subscription may own many historical BillingPeriods;
- at most one owned period may be OPEN;
- new periods snapshot the governing plan/allowance;
- closed periods retain close metadata.

Legacy closed periods are not assigned fabricated historical plans. Nullable snapshot fields are allowed for legacy rows whose historical plan cannot be proven.

## Development migration normalization — superseded for first production

Earlier ARCH-010 development migrations considered normalising multiple historical OPEN BillingPeriods with a migration-only close reason. That approach is **not** part of the first-production baseline.

DATABASE-013 regenerates the schema from an empty database. `MIGRATION_RECONCILED` does not exist in first production and no development BillingPeriod rows are backfilled into the baseline migration.

## Screens/services while boundary reconciliation is overdue

If `now >= currentPeriodEnd` and the Subscription still points to that expired period:

Available:

- `/app` read-only dashboard/history presentation;
- `/app/usage` historical/current-period read presentation;
- `/app/billing` status/plan presentation;
- Shopify plan-selection navigation;
- merchant support.

Unavailable until Shopify confirms the successor state:

- new recovery initiation;
- new purchased-credit consumption through recovery execution;
- new top-up purchase;
- CommerceAgent/customer-response business actions that require a current subscription entitlement;
- any new Shopify billing App Event for that expired period.

The UI displays a bounded billing-cycle reconciliation state rather than pretending the expired period is current.

## Shopify/Partner API failure at boundary

A timeout/throttle/5xx proves nothing about the subscription.

Preserve current plan/period projection and period history. Record sync-error metadata and reschedule the same reconciliation job using bounded backoff. Do not set a last-known valid subscription to `SYNC_ERROR` solely because of transport failure.

Unlike first-time activation, an existing paid merchant does not receive a 24-hour expiry that clears their known subscription. Retry can continue while the merchant remains fail-closed for new business actions whose current-cycle correctness cannot be proven.

## Task changes caused by this iteration

- `ARCH-010-SHARED-001` is amended to export the canonical five-minute App Pricing billing-period drain constant.
- `ARCH-010-BACKGROUND-002` is amended so paid included reservation source identity includes `billingPeriodId` and can be safely re-admitted in a later period.
- `ARCH-010-BACKGROUND-003` and `ARCH-010-SHOPIFY-003` are amended so the first paid period writes the new period ownership/snapshot fields and schedules the pre-close job rather than clearing reconciliation scheduling permanently.
- `ARCH-010-BACKGROUND-006` is amended so same-plan reinstall with a later Shopify cycle delegates to the canonical rollover service instead of duplicating Free/Paid period rotation.

## Tasks created by this iteration

- `ARCH-010-DATABASE-004` — strengthen BillingPeriod ownership/history, close metadata, release reason and one-open-period integrity.
- `ARCH-010-BACKGROUND-007` — implement canonical same-plan Free/Paid provider period drain/close/open/retry/reconstruction transition; only Paid creates/refills an included-credit counter.
- `ARCH-010-BACKGROUND-008` — make paid recovery initiation boundary-safe with drain-window revalidation and bounded WhatsApp send duration.
- `ARCH-010-SHOPIFY-007` — expose merchant billing-cycle reconciliation presentation and server-side drain/expired guards for top-up purchase on both Free and Paid; Free recovery entitlement itself remains lifetime.

No new queue, Render service, Admin task or Messaging-ingress task is required.

## Explicit non-goals for Iteration 6

This rollover iteration does not itself implement:

- paid -> Free or paid -> different Paid effective transitions (owned by BACKGROUND-010 / Shopify plan-change tasks);
- verified cancellation/no-contract outcome (owned by BACKGROUND-012/013 and SHOPIFY-016);
- merchant-facing plan-management UX (owned by SHOPIFY-011/012/015);
- partial purchased-credit refunds (owned by DATABASE-007/BACKGROUND-014/ADMIN-002/003/SHOPIFY-017);
- promotional credits (owned by DATABASE-009/BACKGROUND-019/ADMIN-004/005/SHOPIFY-020);
- promotional-credit expiration/revocation or deterministic shop re-identification redesign (explicit future scope outside ARCH-010).

## Iteration 7 — Recovery-capacity exhaustion and restoration

### Scope

This iteration defines the behavioural state reached when a merchant still has a valid Shopify subscription but has no capacity to start another abandoned-checkout recovery conversation.

Exhaustion is **not** a subscription transition. The subscription remains the same mapped current Shopify plan.

```text
Free ACTIVE + no spendable recovery capacity
    -> Free ACTIVE / RECOVERY_CAPACITY_EXHAUSTED

Paid ACTIVE + no spendable recovery capacity
    -> Paid ACTIVE / RECOVERY_CAPACITY_EXHAUSTED
```

The merchant remains an active Moda tenant. Only **new checkout-recovery initiation** is denied by this capacity state.

### Current implementation facts

The inspected baseline already has these useful behaviours:

- Final Free recovery admission is promotional credits -> purchased credits -> shop-lifetime Free credits -> BLOCK NEW RECOVERY ADMISSION.
- Final Paid recovery admission is selected promotional -> current-period included credits -> purchased -> shop-lifetime Free -> BLOCK NEW RECOVERY ADMISSION.
- an exhausted Free admission currently creates an idempotent `BILLING_FREE_ALLOWANCE_EXHAUSTED` merchant-support SYSTEM message;
- paid capacity exhaustion has no equivalent generic merchant notification yet;
- `CheckoutRecoveryService.handleCheckoutCreated()` creates/retains the durable `CheckoutRecovery` before billing admission and simply returns when billing is blocked;
- that leaves the recovery in `DETECTED` with no durable reason explaining why initiation stopped;
- there is no automatic retry of that DETECTED recovery after a top-up or new paid billing period restores capacity;
- `/app/billing/options` is currently an ARCH-008 mock/prototype surface with hard-coded plans, usage and top-up offers and must not become the production capacity source of truth.

### Canonical capacity-source order

The final ARCH-010 recovery-capacity order is:

```text
FREE
  selected usable campaign PromotionalCreditGrant
  -> PURCHASED_RECOVERY_CREDITS
  -> LIFETIME_FREE_RECOVERY_CREDITS
  -> EXHAUSTED

PAID
  selected usable campaign PromotionalCreditGrant
  -> current BillingPeriod INCLUDED_RECOVERY_CREDITS
  -> PURCHASED_RECOVERY_CREDITS
  -> LIFETIME_FREE_RECOVERY_CREDITS
  -> EXHAUSTED
```

There is no automatic Paid overage. Promotional capacity is an exact campaign-linked grant lot and must never be aliased to the five lifetime Free credits.

### Authority split for Iteration 7

Shopify and Moda own different truths. Do not collapse them into one database catalogue.

```text
Shopify Partner activeSubscription
  -> commercial contract existence
  -> current/pending Shopify plan
  -> flat-rate price/currency
  -> billing interval/current cycle
  -> cancellation-at-cycle-end state

Moda PostgreSQL
  -> mapping from Shopify plan handle to Moda entitlements/features
  -> Free lifetime allowance accounting
  -> Paid current-period included-credit accounting
  -> purchased-credit accounting
  -> recovery-admission availability
```

`billing.BillingPlan` is therefore a **Moda entitlement/configuration mapping keyed by Shopify plan handle**. Creating a `BillingPlan` row does not create or prove the existence of a Shopify plan. Shopify-hosted App Pricing remains the plan catalogue/selection authority.

The durable `Subscription` row is a reconciled operational projection used for fast runtime decisions. It does not replace live Shopify commercial truth on billing-management screens.

### Derived recovery-capacity state

Do not add another Subscription status. Merchant/runtime capacity is derived from the reconciled local plan mapping plus durable counters:

```text
PAID_INCLUDED
  Paid plan and current OPEN-period included remaining > 0

PURCHASED
  purchased available > 0 after any Paid current-period included allowance is exhausted

FREE_LIFETIME
  shop-lifetime Free remaining > 0 after higher-priority sources are exhausted; this source is available under Free OR Paid

EXHAUSTED
  every currently supported recovery-capacity source is unavailable
```

The merchant read model should expose at least:

```text
newRecoveryAllowed: boolean
capacitySource: PAID_INCLUDED | PURCHASED | FREE_LIFETIME | EXHAUSTED
freeLifetimeRemaining: number | null
paidIncludedRemaining: number | null
purchasedAvailable: number
```

This is a projection, not new authoritative persisted state.

### Behaviour matrix

| Subscription/capacity | New checkout recovery | Existing admitted recovery conversation | Shopify event correlation | Merchant UI/history | Top-up purchase | Plan selection |
|---|---|---|---|---|---|---|
| Free + promotional available | allowed from promotional first | continues | continues | available; show promotional/purchased/lifetime balances separately | only when server eligibility permits | available |
| Free + promotional exhausted + purchased available | allowed from purchased | continues | continues | available | only when server eligibility permits | available |
| Free + promotional/purchased exhausted + lifetime Free available | allowed from lifetime Free | continues | continues | available | only when server eligibility permits | available |
| Free + all three lifetime sources exhausted | **blocked** | continues | continues | available; show capacity-exhausted state | only when server eligibility permits | available |
| Paid + selected usable promo | allowed from selected promotion first | continues | continues | available; show selected promo/expiry/fallback | only when server eligibility permits and not draining/reconciling | available |
| Paid + no usable selected promo + included available | allowed from current-period included counter | continues | continues | available | only when server eligibility permits and not draining/reconciling | available |
| Paid + no usable promo + included exhausted + purchased available | allowed from purchased | continues | continues | available | same existing eligibility | available |
| Paid + no usable promo + included/purchased exhausted + lifetime Free available | allowed from lifetime Free | continues | continues | available; show lifetime Free fallback | same existing eligibility | available |
| Paid all sources exhausted | **blocked** until capacity is restored | continues | continues | available; show capacity-exhausted state | same existing eligibility | available |

Recovery-capacity exhaustion does not disable `AI_CONVERSATIONS`, `PRODUCT_SEARCH` or `ORDER_SUPPORT` merely because checkout-recovery capacity is empty. Their existing plan feature mappings and safety policy remain authoritative.

### Exhausted recovery persistence

When a new checkout recovery reaches billing admission and every supported capacity source is exhausted:

1. do not call Meta/WhatsApp;
2. do not create a normal recovery UsageEvent;
3. keep `CheckoutRecovery.status = DETECTED`;
4. durably annotate that DETECTED recovery with `RECOVERY_CAPACITY_EXHAUSTED` and the first block timestamp;
5. create one idempotent merchant-support SYSTEM notification for the current capacity-exhaustion lifecycle;
6. return successful terminal processing for the current queue attempt rather than retry-looping while capacity is known to be absent.

Do not add `CAPACITY_BLOCKED` to `CheckoutRecoveryStatus`; the recovery has not entered a new customer-facing lifecycle stage and must remain eligible to start later if capacity returns while the checkout is still recoverable.

### Exhaustion SYSTEM message lifecycle

Add a generic Shared billing system code:

```text
BILLING_RECOVERY_CAPACITY_EXHAUSTED
```

Use it for Free and Paid full-capacity exhaustion. `BILLING_FREE_ALLOWANCE_EXHAUSTED` is development-era compatibility and is removed from the first-production Shared contract by SHARED-007; no first-production producer or renderer preserves it.

The exhaustion message must be idempotent per capacity epoch rather than per blocked checkout. Its source identity should change only when new capacity has genuinely become available, for example:

```text
Free epoch:
  subscriptionId
  + selected promotional grant identity + granted/committed/reserved quantities
  + purchased granted/committed/reserved/refunding quantities
  + lifetime Free granted/committed/reserved quantities

Paid epoch:
  current BillingPeriod id
  + selected promotional grant identity + granted/committed/reserved quantities
  + period included granted/committed/reserved/forfeited quantities
  + purchased granted/committed/reserved/refunding quantities
  + lifetime Free granted/committed/reserved quantities
```

This prevents one support message per abandoned checkout while allowing a later top-up or later Paid period to create a new message if that newly restored capacity is subsequently exhausted again.

The merchant action for the generic exhaustion message is `/app/billing/options`. The route is retained and productionised in Iteration 7; it is no longer permitted to use mock billing authority. It never links to Admin.

### Existing conversations remain live

Recovery credits pay/admit the **recovery conversation**, not every subsequent customer/agent turn.

Therefore exhausting recovery capacity:

- blocks only a new checkout recovery that has not yet been admitted;
- does not terminate a `MESSAGE_SENT` or `ENGAGED` recovery;
- does not block inbound replies for an already-admitted recovery;
- does not block CommerceAgent continuation for that existing conversation solely because capacity later reaches zero;
- remains subject to all existing outbound safety, abuse and plan-feature controls.

### Capacity restoration and blocked recovery resumption

Capacity may be restored by:

```text
purchased top-up becomes ACTIVE
new Paid BillingPeriod opens with fresh included allowance
new promotional-credit grant becomes available
verified plan transition restores executable capacity
```

A blocked DETECTED recovery must not remain stranded forever merely because the original queue attempt finished while capacity was exhausted.

Background owns a durable-reconstructable **capacity-resume** workflow:

```text
capacity restored
   -> best-effort enqueue shop capacity-resume job
   -> worker loads oldest DETECTED recoveries marked RECOVERY_CAPACITY_EXHAUSTED
   -> revalidate current checkout/recoverability
   -> retry normal recovery initiation
   -> process sequentially until:
        no blocked recovery remains
        OR capacity is exhausted again
        OR a retryable provider error requires BullMQ retry
```

Use the existing per-checkout lock and outbound idempotency key so capacity restoration cannot duplicate an initial WhatsApp recovery message.

Do not blindly send an old stored checkout snapshot. Re-fetch/validate the current abandoned checkout before the resumed initiation. If the checkout is definitively no longer recoverable, use the existing recovery lifecycle/history conventions to make it terminal rather than sending a stale recovery message. Ambiguous/transient provider results remain retryable/fail-closed.

### Redis loss / worker restart

The block is durable in PostgreSQL; the resume job is not authoritative.

The recovery runtime must perform a bounded startup and periodic repair scan for:

```text
CheckoutRecovery.status = DETECTED
admissionBlockReason = RECOVERY_CAPACITY_EXHAUSTED
Shop.status = ACTIVE
```

It may enqueue one deterministic shop-scoped resume job. The job itself re-runs current admission; if capacity remains exhausted it stops without sending and leaves the durable block in place.

This reconstructs lost Redis queue work and also catches capacity restoration mechanisms that do not directly publish a resume hint.

### Merchant screens after exhaustion

The merchant remains on the normal `/app` dashboard. Exhaustion must not redirect the merchant away from dashboard, usage, history or event views.

When every currently supported recovery-capacity source is exhausted, `/app` shows a localized warning explaining that only **new abandoned-checkout recovery initiation** is paused and provides a clear CTA to `/app/billing/options`.

The existing `/app/billing/options` route is retained as the canonical recovery-capacity management screen. Its ARCH-008 mock data/console-only actions are replaced by real durable billing state and existing server billing actions. Hard-coded mock plan prices, usage quantities, purchased balances and `£5/£10/£20` offers must never become production authority. `/app/billing` remains a valid billing summary/status screen and may link to `/app/billing/options`.

#### Billing-options implementation decomposition

A deeper inspection of the ARCH-008 prototype found that productionising this route is not one UI edit. The current `BillingPurchaseHub` imports mock defaults and silently falls back to the first plan; `TopUpPurchasePanel` assumes multiple locally priced offers and computes unit prices in the browser; `SubscriptionChangePanel` assumes locally authoritative plan price/rank data and contains prototype-only duplicate content; and the route itself ignores its loader billing object in favour of `mockBillingState` plus console-only actions.

ARCH-010 therefore decomposes this work:

```text
SHOPIFY-009  local recovery-capacity projection
      |
      +--> SHOPIFY-010  real top-up component
      |
SHOPIFY-013  Shopify commercial subscription projection
      |             |
      +----------> SHOPIFY-011  real Shopify plan-management component
                    \ /
                 SHOPIFY-012
        real billing/options route + hub
      (Shopify commercial + Moda capacity)
                    |
                 SHOPIFY-008
        dashboard exhaustion presentation
```

The current `BillingPlan` model owns the **Moda mapping/configuration** for a Shopify plan handle: kind, allowances, feature mappings and pack quantity/handles. It is not the Shopify commercial plan catalogue and must not be used to prove plan existence, current subscription, price or billing interval. The production UI must therefore not preserve the mock plan-price or multi-priced-pack assumptions merely to retain the prototype card layout.

For merchant billing-management UI, ARCH-010 adds a separate provider-backed commercial read model (`SHOPIFY-013`) using Partner `activeSubscription`. `SHOPIFY-009` remains intentionally local-only because it answers a different question: whether another recovery can be admitted from Moda's durable counters. `/app/billing/options` composes both read models.

#### Free — Free allowance exhausted, purchased credits available

Show:

```text
Free lifetime allowance: 0 remaining
Purchased recovery credits: N available
New recoveries are using purchased credits
```

Normal dashboard/history/support remain available.

#### Free — all current recovery capacity exhausted

Show a localized state equivalent to:

```text
New abandoned-checkout recoveries are paused because no recovery capacity remains.
Existing conversations continue.
Add a recovery top-up if one is available for your plan, or choose another plan.
```

#### Paid — monthly included exhausted, purchased credits available

Show:

```text
This month's included recoveries: 0 remaining
Purchased recovery credits: N available
New recoveries are using purchased credits until the next monthly allowance begins.
```

#### Paid — monthly included and purchased exhausted

Show a localized state equivalent to:

```text
New abandoned-checkout recoveries are paused for the current allowance state.
Add a recovery top-up, or wait for the next monthly billing period to receive the plan's fresh included allowance.
```

Do not describe this as cancellation, subscription expiry, or a failed Shopify contract. The Paid subscription remains ACTIVE.

### Merchant actions while exhausted

Available:

- `/app` dashboard/history/events;
- `/app/usage`;
- `/app/billing`;
- `/app/billing/options` real recovery-capacity management;
- Shopify-hosted plan-selection/change flow;
- `/app/merchant-support`;
- read-only recovery/pending-recovery surfaces;
- top-up purchase only when the real server-side pack/meter/cycle eligibility checks pass.

Unavailable solely because of capacity exhaustion:

- initiation of a new abandoned-checkout recovery conversation.

No merchant surface links to `moda-interact-admin`.

### Top-up purchase note

This iteration does not invent monetary pack configuration or make the mock ARCH-008 top-up catalogue real. `/app/billing` may offer the existing real configured pack only when the server says `recoveryCreditPackPurchaseEligible=true` and all ARCH-008/ARCH-010 billing-cycle guards pass.

`/app/billing/options`, once integrated by SHOPIFY-012, combines Shopify-authoritative current/pending commercial subscription state with Moda-authoritative recovery-capacity accounting, then reuses the existing real server-side top-up eligibility and purchase service. If Shopify verification is temporarily unavailable, the page must not fall back to local `BillingPlan` data as commercial truth; it shows verification unavailable and disables billing mutations. If the current provider/cycle safety rules say a pack cannot be purchased for a given state, the UI must show it as unavailable rather than manufacturing a mock purchase path. Do not create fake Free entitlement resets or local monetary prices.

### Tasks created/amended by Iteration 7

New tasks:

- `ARCH-010-DATABASE-005` — persist a narrow recovery-admission capacity block on DETECTED recoveries.
- `ARCH-010-SHARED-003` — add the generic recovery-capacity-exhausted merchant billing system code.
- `ARCH-010-SHARED-004` — publish the accepted Shared system-code addition.
- `ARCH-010-BACKGROUND-009` — persist exhaustion, notify once per capacity epoch, resume blocked recoveries after capacity restoration, and rebuild lost resume work from PostgreSQL.
- `ARCH-010-SHOPIFY-008` — keep exhausted merchants on the normal dashboard/history with a warning/CTA to the real capacity-management route.
- `ARCH-010-SHOPIFY-009` — provide the PostgreSQL-only merchant recovery-capacity projection used for dashboard/runtime admission presentation; it is not Shopify commercial-plan authority.
- `ARCH-010-SHOPIFY-010` — productionise the top-up child component around the real single configured pack, without local monetary-price authority.
- `ARCH-010-SHOPIFY-011` — productionise the plan-management child component around Shopify-authoritative current/pending subscription facts plus Shopify-hosted plan selection.
- `ARCH-010-SHOPIFY-013` — extend the provider/service contract so billing-management UI can read Shopify-authoritative current/pending plan handle, price, billing interval and cycle without using `BillingPlan` as the commercial catalogue.
- `ARCH-010-SHOPIFY-012` — integrate `/app/billing/options` and `BillingPurchaseHub` by composing SHOPIFY-013 commercial truth with SHOPIFY-009 local recovery-capacity accounting and real actions.

Amended tasks:

- `ARCH-010-BACKGROUND-007` schedules a best-effort capacity-resume hint after a new Paid BillingPeriod is committed.
- `ARCH-008-SHOPIFY-003` is superseded by `ARCH-010-SHOPIFY-008`; its existing screen/component work may be reused, but its mock-only data/action requirements must not continue as a separate production task.

No new Gateway, Messaging-ingress or Admin implementation task is required.

## Explicit non-goals for Iteration 7

This exhaustion iteration does not itself implement:

- promotional-credit grant/reservation mechanics (owned by Iteration 12 tasks);
- partial purchased-credit refunds (owned by the refund tasks);
- paid -> Free / paid -> different Paid effective plan transitions (owned by BACKGROUND-010 and Shopify plan-management tasks);
- Shopify cancellation/no-contract transitions (owned by BACKGROUND-012/013 and SHOPIFY-016);
- promotional-credit expiration/revocation or deterministic shop re-identification redesign (explicit future scope outside ARCH-010).

## Next iteration

Review the **purchased top-up transition** end to end: merchant request -> Shopify App Event -> asynchronous provider confirmation -> purchased-credit activation, how a newly activated pack restores/replays blocked recoveries.



## Iteration 8 — Merchant billing actions: top-up purchase and Shopify-hosted plan changes

### Scope

Iteration 8 makes `/app/billing/options` a real **action surface**, not only a capacity/reporting screen.

It owns two independent merchant actions:

```text
A. Buy recovery top-up
B. Manage/change Shopify plan
```

They share one page but have different authorities and lifecycle mechanics. They MUST remain separate service/component/task boundaries.

### 8A — Recovery top-up purchase

#### Commercial mechanism

The merchant experiences a top-up as a one-off purchase of a lifetime recovery-credit pack.

Moda is on Shopify App Pricing, therefore the Shopify billing implementation remains:

```text
configured recovery-credit-pack usage meter
+ one RECOVERY_CREDIT_PACK_PURCHASE App Event with value=1
```

Do not use Manual Pricing/Billing API `appPurchaseOneTimeCreate`.

Shopify App Pricing does not support native one-time purchases; Shopify's migration guidance for apps with recurring + one-time charges is to represent each repeated one-time charge as an App Event on a usage meter.

#### Free-plan top-up commercial model

Free merchants use the same App Events top-up lifecycle. The Shopify Free plan is configured with a £0 recurring charge (or equivalent no-charge recurring plan representation) plus the `recovery-credit-pack` usage meter. The Free plan therefore still has a Shopify monthly billing cycle for usage billing.

Before a Free top-up request Moda must verify:

```text
provider current plan = mapped Free plan
configured pack meter is an active provider usage item
provider currentBillingCycle is exact
local Subscription/BillingPeriod matches that exact provider cycle
phase is ACTIVE, not DRAINING/RECONCILING
```

The Free BillingPeriod never grants or resets the five lifetime Free recoveries. It exists so App Event purchases are tied to the correct Shopify usage-billing cycle.

#### Top-up transition

```text
READY
  merchant selects Buy pack
      ↓
Moda verifies current Shopify contract, exact pack meter and billing cycle
      ↓
transaction creates:
  RecoveryCreditPurchase(PENDING_BILLING)
  UsageEvent(RECOVERY_CREDIT_PACK_PURCHASE +1, PENDING)
      ↓
merchant sees "being confirmed by Shopify"
      ↓
Background App Events publisher submits event
      ↓
HTTP 202 only means Shopify received the event
      ↓
Background Partner reconciliation checks provider pack-meter usage
      │
      ├── provider confirms next unit
      │       ↓
      │   purchase ACTIVE exactly once
      │   purchased lifetime grantedQuantity += creditsPerPack
      │   blocked recoveries may be resumed by BACKGROUND-009
      │
      ├── publisher definitive failure
      │       ↓
      │   purchase/usage NEEDS_ATTENTION
      │   grant 0
      │
      └── provider not yet confirmed
              ↓
          remain PENDING_BILLING
          grant 0
```

A `202 Accepted` App Events response is never sufficient to activate credits because Shopify validates billing asynchronously.

#### Top-up screen behaviour

`TopUpPurchasePanel` shows:

- current purchased credits available;
- local `creditsPerPack` (what one provider meter unit grants inside Moda);
- current provider pack-meter commercial/pricing representation when safely available;
- pending/active/attention state of the latest durable request;
- one Buy CTA only when current provider/local eligibility is safe.

It never fabricates local £/$ pricing.

The UI may describe this as a one-off recovery top-up, but must not imply Shopify creates a separate Billing API one-time purchase/approval page for each pack.

### 8B — Shopify-hosted upgrade/downgrade initiation

The plan-management panel does not submit a local plan ID.

```text
/app/billing/options
      ↓ Manage/change plan
/app/billing/select
      ↓
Shopify-hosted App Pricing
      ↓
Shopify redirect with plan_handle
      ↓
Moda queries Partner activeSubscription
```

`plan_handle` is context only.

#### Callback classification

```text
CURRENT_MATCH
  requested handle == provider current handle

PENDING_MATCH
  requested handle == provider pendingUpdate handle

NO_ACTIVE_SUBSCRIPTION
  provider returns null

MISMATCH
  provider exists but requested handle is neither current nor pending

VERIFICATION_FAILED
  Partner API could not be queried safely
```

`PENDING_MATCH` preserves current entitlement and schedules the existing deterministic subscription reconciliation job for the provider effective boundary.

`CURRENT_MATCH` never opens/closes BillingPeriods or grants credits in the HTTP callback. It schedules immediate Background reconciliation.

### Effective plan change — Background authority

BACKGROUND-010 applies provider-confirmed plan changes.

Expected supported transitions at a proven effective boundary:

```text
PAID A -> PAID B
  close old paid period PLAN_CHANGED
  forfeit unused old included credits
  open exact provider paid period for B
  grant B included allowance once
  preserve Free lifetime history
  preserve purchased lifetime credits

PAID -> FREE
  close old paid period PLAN_CHANGED
  create/reuse exact provider Free BillingPeriod with no included-credit counter
  no new monthly Free recovery allowance
  restore existing Free lifetime remaining state
  preserve purchased lifetime credits

FREE -> PAID
  preserve Free lifetime history
  close outgoing Free provider BillingPeriod when exact
  create first exact paid period/counter
  preserve purchased lifetime credits
```

No local plan rank or local price is used to classify the commercial change.

### Shopify timing guardrail

ARCH-010's agreed entitlement model assumes a plan change remains provider-pending until its effective boundary. Shopify is commercial authority, and current official App Pricing APIs expose `pendingUpdate` for changes applied at the next billing cycle.

The current ARCH-010 database deliberately models one plan/allowance snapshot per BillingPeriod and does not support a normal mid-cycle plan-entitlement segment.

Therefore, if Partner `activeSubscription` unexpectedly reports a different **current** mapped plan inside the still-open same local Shopify cycle before a boundary transition can be proven:

```text
UNEXPECTED_IMMEDIATE_PLAN_CHANGE
  -> do not grant a fresh allowance
  -> do not use stale old-plan meter assumptions
  -> fail closed for new billable recovery/top-up operations
  -> preserve read/history/support access
  -> retry/reconcile and surface operationally
```

If this occurs as ordinary production Shopify behaviour rather than an exceptional condition, ARCH-010 must return to architecture review and add an explicit mid-cycle entitlement model; an implementation agent must not invent proration/overlapping periods.

### Tasks created/amended by Iteration 8

New:

- `ARCH-010-SHOPIFY-014` — server-side top-up purchase lifecycle/read/action adapter using the existing App Events mechanism.
- `ARCH-010-BACKGROUND-010` — apply provider-confirmed paid/free plan changes and preserve lifetime balances.
- `ARCH-010-SHOPIFY-015` — Shopify-hosted plan-change return/classification and reconciliation handoff.

Amended:

- `ARCH-010-SHOPIFY-013` additionally exposes active provider usage-item price/usage data for exact pack-meter matching.
- `ARCH-010-SHOPIFY-010` consumes SHOPIFY-014 lifecycle state and renders pending/active/attention top-up states.
- `ARCH-010-SHOPIFY-011` consumes SHOPIFY-015 plan-management semantics and performs no local mutation.
- `ARCH-010-SHOPIFY-012` composes the real top-up and hosted-plan-change actions in `/app/billing/options`.

No new Database, Shared, Gateway, Messaging or Admin task ID is required for Iteration 8; this correction amends DATABASE-004, SHARED-001 and the existing rollover tasks so Free provider billing cycles are first-class without changing Free lifetime entitlement semantics.

### Explicit non-goals for Iteration 8

- partial purchased-credit refunds;
- subscription cancellation/refund handling;
- promotional credit grants (owned by Iteration 12);
- deterministic shop re-identification;
- local Shopify plan catalogue creation;
- local proration calculation;
- mid-cycle plan entitlement segmentation.

## Iteration 9 — Shopify subscription cancellation

### Scope

Iteration 9 handles **full Shopify subscription cancellation** while the app remains installed.

This is distinct from:

```text
Paid -> Free
Free -> Paid
Paid A -> Paid B
```

which remain Iteration 8 Shopify-hosted plan changes.

ARCH-010 cancellation authority is Shopify App Pricing. Moda does not call `appSubscriptionCancel`, does not create a human-approved cancellation workflow, and does not treat uninstall as cancellation.

### Provider authority and classification

Every lifecycle decision comes from Partner `activeSubscription` plus the durable local projection.

Classify in this order:

```text
activeSubscription + pendingUpdate
  -> plan-change lifecycle (BACKGROUND-010)

activeSubscription
+ cancelAtEndOfCycle = true
+ pendingUpdate = null
  -> full cancellation scheduled

activeSubscription
+ cancelAtEndOfCycle = false
  -> normal current contract / cancellation not scheduled

activeSubscription = null
  -> no current Shopify App Pricing contract
```

A Partner API transport/throttle/5xx failure is not `null` and must not be converted to NO_CONTRACT.

### Scheduled full cancellation

While Shopify still reports the current subscription:

```text
Subscription current plan    = unchanged
BillingPeriod                 = current/open
cancelAtPeriodEnd             = true
current entitlement           = remains usable
```

The merchant continues using the current plan until the provider contract actually ends.

Capacity order remains unchanged:

```text
Paid:
  selected promotional -> monthly included -> purchased -> lifetime Free -> BLOCK NEW RECOVERY ADMISSION

Free:
  promotional -> purchased -> lifetime Free -> BLOCK NEW RECOVERY ADMISSION
```

However, once **full cancellation** is scheduled, new recovery-credit top-up purchases are disabled. Existing promotional, purchased and lifetime Free credits remain usable until effective contract end.

The normal App Pricing pre-close/drain rules still apply to the final provider cycle.

### Cancellation schedule withdrawn/reversed

If a later Partner query reports the same current contract with:

```text
cancelAtEndOfCycle = false
```

clear the local scheduled-cancellation flag and resume ordinary rollover scheduling. Do not grant/reset any entitlement.

### Effective full cancellation

When Partner successfully returns `null` for a merchant that had a current contract:

```text
close final provider BillingPeriod
  closeReason = CONTRACT_ENDED

Paid final period:
  release outstanding included reservations
  forfeit remaining unused monthly included credits

Free final provider period:
  close commercial/App-Event scope only
  do not alter lifetime Free grant

Subscription:
  status = NO_CONTRACT
  current plan/provider/period pointers = null
  pending plan fields = null
  cancelAtPeriodEnd = false
  nextReconcileAt = null

Shop:
  status remains ACTIVE
```

No successor BillingPeriod is created.

### Lifetime state after cancellation

Full cancellation never deletes or refunds:

```text
shop-lifetime Free remaining balance
purchased lifetime recovery credits
purchase/refund history
historical BillingPeriods
recovery/conversation history
```

Those balances are **preserved but non-spendable** while Subscription is NO_CONTRACT. A later verified Shopify contract is required before recovery execution can resume.

### Merchant application after effective cancellation

A merchant who previously completed onboarding remains an onboarded merchant:

```text
ShopSettings.onboardingCompleted = true
Subscription.status = NO_CONTRACT
```

They continue to land on `/app`, not first-install onboarding.

Available merchant surfaces:

```text
dashboard/read-only status
usage and event history
recovery/conversation history
/app/billing
/app/billing/options
/app/merchant-support
Shopify-hosted plan selection/manage CTA
```

Unavailable business actions:

```text
new recovery initiation
existing conversation agent execution
new outbound WhatsApp business sends
new top-up purchase
spending purchased credits
spending lifetime Free credits
```

The dashboard/billing UI must distinguish:

```text
EXHAUSTED
  active contract exists but all spendable recovery capacity is exhausted

CONTRACT_REQUIRED
  no executable Shopify contract exists; balances may still be preserved
```

### Fresh NO_CONTRACT versus post-cancellation NO_CONTRACT

```text
fresh install / never activated:
  onboardingCompleted = false
  -> onboarding / choose plan

previously activated then cancelled:
  onboardingCompleted = true
  -> dashboard/history + choose plan to resume
```

Do not reset `onboardingCompleted` merely because the contract ends.

### Background execution gate

Effective cancellation is stronger than capacity exhaustion.

After shop ownership is known, Background requires both:

```text
Shop.status = ACTIVE
AND
current executable Subscription state
```

NO_CONTRACT causes new shop-owned business work to become terminal no-op:

- no new pending recovery candidate;
- no new CheckoutRecovery/conversation/send;
- no inbound WhatsApp conversation mutation;
- no queued conversation-turn CommerceAgent execution;
- no new credit reservation/usage.

Historical bookkeeping for irreversible pre-cancellation work may finish when it creates no new customer-facing side effect, including provider delivery statuses and safe terminal history updates.

### BullMQ / recovery

No dedicated cancellation queue is created.

Use the existing deterministic `billing-subscription-reconcile` queue and durable `Subscription.nextReconcileAt`.

While cancellation is scheduled, PostgreSQL contains sufficient state to rebuild a lost delayed job:

```text
cancelAtPeriodEnd = true
currentPeriodEnd = provider cycle end
nextReconcileAt = pre-close/boundary schedule
```

After effective cancellation:

```text
nextReconcileAt = null
```

There is nothing to reconstruct until the merchant initiates a new Shopify plan activation.

### ARCH-009 supersession note

The frozen ARCH-009 design that lets Moda/Admin approve and execute `appSubscriptionCancel` is not part of ARCH-010 and must not be integrated as cancellation authority. ARCH-010 observes Shopify App Pricing cancellation state instead.

### Tasks created/amended by Iteration 9

New:

- `ARCH-010-BACKGROUND-012` — reconcile scheduled/effective Shopify cancellation and close the final provider BillingPeriod.
- `ARCH-010-BACKGROUND-013` — enforce NO_CONTRACT as a shop business-execution gate across queued recovery and WhatsApp/conversation work.
- `ARCH-010-SHOPIFY-016` — present scheduled/effective cancellation on merchant surfaces without local cancellation authority.

Amended:

- `ARCH-010-BACKGROUND-007` delegates provider-null/no-contract boundary outcomes to BACKGROUND-012.
- `ARCH-010-SHOPIFY-009` adds `CONTRACT_REQUIRED` so post-cancellation no-contract state is never mislabelled as credit exhaustion.

No new Database, Shared, Gateway, Messaging or Admin task is required for Iteration 9.

### Explicit non-goals for Iteration 9

- top-up refunds;
- subscription resubscription/reactivation implementation after full cancellation;
- Shopify freeze/payment-interruption semantics;
- deterministic shop re-identification;
- local cancellation mutation/approval;
- merchant access to `moda-interact-admin`.

## Iteration 10 — Partial refund of unused purchased top-up credits

### Scope

Iteration 10 covers only Moda's purchased recovery-credit top-ups.

It does **not** refund Shopify recurring subscription fees. Shopify remains authority for recurring subscription cancellation/refund handling.

The one-time shop-lifetime Free recovery grant is never refundable.

### Product rule

A provider-confirmed top-up purchase creates a durable purchased-credit lot.

For one historical top-up:

```text
creditsGranted = 100
committed       = 30
reserved        = 0
refunding       = 0
refunded        = 0

refundable now = 70
```

A merchant may request any positive whole-credit quantity up to the currently unused portion of one purchase lot.

Multiple partial refunds of the same purchase are allowed as long as unused refundable credits remain.

The canonical per-purchase refundable quantity is:

```text
refundable = max(
  creditsGranted
  - committedQuantity
  - reservedQuantity
  - refundingQuantity
  - refundedQuantity,
  0
)
```

`AMBIGUOUS` purchased reservations remain unavailable and therefore count with reserved quantity until explicitly resolved.

### Purchased-credit lot consumption

Purchased credits remain higher priority than lifetime Free credits.

Within the purchased bucket, recovery reservations consume the oldest provider-confirmed purchase lot first:

```text
activatedAt ASC
createdAt   ASC
id          ASC
```

This FIFO rule is durable policy, not a query convenience. It is required so Moda can determine which historical purchase still owns unused refundable credits.

A recovery reservation must be associated with the exact purchase lot that funded it. Commit/release/ambiguous transitions must update both:

```text
ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS)
AND
RecoveryCreditPurchase lot quantities
```

inside one Serializable transaction.

### Refund request surface

Refunds are not self-service money movement.

`/app/billing/options` may explain that unused purchased top-up credits can be requested for refund and provide a CTA to `/app/merchant-support`.

The merchant does not choose a Shopify charge ID, provider refund amount, refund/credit provider action or settlement mechanism.

A human Admin maps the support request to one purchase lot and one requested whole-credit quantity.

### Request and approval

Admin triage creates one `RecoveryCreditRefund` for one purchase lot.

The request does not hold capacity. A merchant may continue using purchased credits before a SUPER_ADMIN approves the request.

Approval therefore re-reads the exact lot and aggregate counter in a Serializable transaction and requires the exact requested quantity still to be refundable.

ARCH-010 does **not** silently approve a lower quantity. If the requested quantity is no longer refundable, approval fails and the merchant must agree/request a new quantity.

Successful approval atomically holds the exact quantity:

```text
purchase.refundingQuantity += approvedQuantity
aggregate.refundingQuantity += approvedQuantity
```

Held credits are immediately unavailable to recovery admission.

### Shopify provider settlement

ARCH-010 partial refunds use a human Shopify Partner Dashboard settlement path.

Do not create a new negative/fractional App Event for an ARCH-010 partial refund.

Reasons:

1. Shopify App Events are aggregate meter adjustments, not a per-purchase refund primitive.
2. Shopify does not expose an event-level billing result that can be deterministically correlated to Moda's App Event idempotency key after asynchronous billing validation.
3. Partial negative usage can change aggregate meter quantity/pricing semantics and would complicate the existing provider-confirmed top-up reconciliation.
4. Shopify's Partner Dashboard already supports full/partial app-charge refunds and multiple partial refunds while refundable balance remains.

Provider action is selected from the actual Shopify charge/invoice state:

```text
paid charge/invoice
    -> PARTNER_DASHBOARD_REFUND

not-yet-paid charge
    -> PARTNER_DASHBOARD_CREDIT
```

Admin must use Shopify's charge/invoice monetary source. Moda does not infer refund money from the current BillingPlan, current meter rate or current subscription price.

Provider refund eligibility remains subject to Shopify limitations. If the Partner Dashboard cannot settle the charge automatically (including age/provider limitations), Admin must not fabricate success; retain the credit hold and move the request to `NEEDS_ATTENTION` for Shopify Support/manual resolution.

### Provider confirmation and local finalization

After the SUPER_ADMIN performs the Shopify provider action, they record the provider reference plus the actual provider amount/currency and confirm the action.

The same Admin confirmation operation finalizes local capacity atomically:

```text
purchase.refundingQuantity -= quantity
purchase.refundedQuantity  += quantity

aggregate.refundingQuantity -= quantity
aggregate.grantedQuantity   -= quantity

refund.status = COMPLETED
```

Do not change purchase `committedQuantity` or `reservedQuantity` during refund finalization.

New ARCH-010 refunds keep the `RecoveryCreditPurchase` provider-confirmation status `ACTIVE`; refund state is represented by lot quantities and `RecoveryCreditRefund[]`. Do not set `RecoveryCreditPurchase.status=REFUNDED` for a new partial refund. The removed `REFUNDED` enum value is development provenance only and is not present in the first-production schema.

This is deliberate: a Partner Dashboard refund/credit does not remove the original +1 App Pricing usage event from the provider meter, and provider purchase reconciliation must not mistake a refunded historical provider unit for an unactivated new purchase.

### Multiple refunds and idempotency

`RecoveryCreditRefund.purchaseId` is no longer unique.

One purchase may have:

```text
refund A: 20 credits COMPLETED
refund B: 30 credits COMPLETED
refund C: 10 credits REQUESTED
```

provided each request passes the current per-lot refundable check.

Every request has its own durable `requestKey` and version/CAS lifecycle.

Approval, hold, rejection/withdrawal hold release, provider confirmation and completion are replay-safe and exactly-once.

### Hold release

Before any provider action is confirmed, SUPER_ADMIN may reject/withdraw an approved refund and atomically release the hold:

```text
purchase.refundingQuantity -= quantity
aggregate.refundingQuantity -= quantity
```

Once a provider action has been performed or confirmation evidence exists, never auto-release the hold. Provider/local ambiguity is `NEEDS_ATTENTION` until reconciled by a human.

### Subscription independence

Purchased-credit refund eligibility is independent of the current Shopify plan.

A historical unused purchased lot may be refunded while the shop is currently:

```text
Free
Paid
NO_CONTRACT after cancellation
```

provided Admin can identify the shop/purchase and Shopify can settle the historical charge.

Uninstall does not itself create/refund anything. If the merchant cannot use in-app support after uninstall, operational support may still identify the durable shop/purchase outside the merchant UI. Deterministic shop re-identification remains out of scope for ARCH-010.

### Provider reconciliation compatibility

The top-up activation reconciler must distinguish:

```text
provider-confirmed original purchase units
from
local spendable purchased-credit balance
```

Manual Partner Dashboard refunds/credits do not reduce the App Pricing usage-meter quantity. Therefore a completed partial refund must never cause the original provider-confirmed purchase to be treated as a new unmatched unit or re-grant credits.

Development-era `REFUNDED` purchase state and negative correction events are not part of the first-production baseline and are not migrated. Provider reconciliation must instead treat the canonical ACTIVE purchase lot plus local refunded quantities as the durable explanation of the original provider top-up unit.

### Merchant messaging

Use shared billing system message codes for:

```text
refund request received
refund completed
refund rejected
```

Messages are idempotent by refund identity. Shopify does not automatically notify the merchant of Partner Dashboard refund completion, so Moda must provide the merchant-facing completion/rejection message.

### ARCH-009 supersession

The frozen ARCH-009 full-pack-only refund design is superseded for new refund work.

In particular ARCH-010 does not preserve these ARCH-009 assumptions:

```text
purchaseId unique on RecoveryCreditRefund
creditsSnapshot always equals full pack
one refund per purchase
purchase status becomes REFUNDED on completion
CURRENT_CYCLE_APP_EVENT_CORRECTION as the normal refund path
```

Accepted ARCH-009 branch work may be inspected/reused where compatible, but ARCH-010 tasks must implement the rules above and must not depend on the frozen ARCH-009 execution graph.

### Tasks created by Iteration 10

- `ARCH-010-DATABASE-007` — add deterministic purchased-credit lot accounting and multi-partial-refund schema/migration/backfill.
- `ARCH-010-BACKGROUND-014` — make purchased recovery reservations FIFO lot-aware, remove the development automatic negative-App-Event refund path, and keep provider activation reconciliation consistent with local partial refunds.
- `ARCH-010-SHARED-005` — define refund merchant-message codes/contracts.
- `ARCH-010-SHARED-006` — publish the accepted Shared refund contract.
- `ARCH-010-SHOPIFY-017` — expose refundability information/support CTA on merchant billing surfaces without self-service provider money movement.
- `ARCH-010-ADMIN-002` — triage merchant support refund requests into exact purchase-lot/credit-quantity requests.
- `ARCH-010-ADMIN-003` — approve/hold, guide Shopify Partner Dashboard refund/credit settlement, confirm provider evidence and finalize local credit removal exactly once.

No new BullMQ queue, Gateway, Messaging or subscription-cancellation task is required for Iteration 10.



## Iteration 11 — Shopify subscription freeze / unfreeze

### Provider fact and authority

Shopify App Pricing can freeze a subscription because of a store billing issue/non-payment and later unfreeze it when payments resume. A freeze is temporary and is not equivalent to cancellation.

ARCH-010 MUST distinguish the live contract query from subscription lifecycle history:

```text
Partner activeSubscription
    = live current commercial contract/cycle when available

Partner Historical Events
    = lifecycle evidence, including
      SUBSCRIPTION_FROZEN
      SUBSCRIPTION_UNFROZEN
      SUBSCRIPTION_CANCELED
      SUBSCRIPTION_CANCELLATION_SCHEDULED
      SUBSCRIPTION_CREATED
      SUBSCRIPTION_UPDATED
```

`activeSubscription = null` alone is therefore not sufficient evidence for `NO_CONTRACT` when Moda previously had a verified contract. The latest provider lifecycle evidence must be considered before cancellation is finalized.

Do not confuse a merchant subscription freeze with the App Events error `ACCOUNT_FROZEN`; Shopify documents `ACCOUNT_FROZEN` as a **partner account** billing-event error, not this merchant subscription lifecycle state.

### Durable frozen state

Add `FROZEN` to the local Subscription projection vocabulary.

When Shopify's latest effective lifecycle state is `FROZEN`:

```text
Shop.status                    = ACTIVE
Subscription.status            = FROZEN
Subscription.planId            = preserve last verified mapping
observedShopifyPlanHandle      = preserve
current BillingPeriod pointer  = preserve
monthly included counters      = preserve
purchased lifetime credits     = preserve
shop-lifetime Free credits     = preserve
pending plan state             = preserve
cancelAtPeriodEnd              = preserve last provider truth
nextReconcileAt                = now + 1 hour
```

The freeze transition MUST NOT:

- close a BillingPeriod;
- forfeit paid monthly included capacity;
- grant a new allowance;
- reset lifetime Free usage;
- consume/refund purchased credits;
- convert the merchant to `NO_CONTRACT`;
- change `Shop.status` to `UNINSTALLED` or `SUSPENDED`.

### Merchant access while frozen

A frozen merchant remains onboarded and may access read/management surfaces:

```text
/app
/app?view=detail
/app/usage
/app/billing
/app/billing/options   read-only billing state
/app/merchant-support
historical recovery/event/conversation views
```

The merchant MUST see a clear message that Shopify has paused the app subscription because of a store billing issue and that billing must be resolved in Shopify before Moda can resume.

While frozen, the merchant MUST NOT be able to initiate:

- a new recovery;
- a new outbound WhatsApp/business message;
- a CommerceAgent turn;
- a new top-up purchase;
- a plan-change action;
- any new credit reservation or billable App Event.

Existing historical data remains visible. Bounded provider-status/accounting finalization for work committed before the freeze may continue, but it must not create new customer-facing business actions.

### Background execution gate

`Subscription.status = FROZEN` is a first-class execution gate stronger than ordinary credit exhaustion.

All shop-owned business processing must stop after ownership resolves to the frozen shop. The gate is enforced in Background, not merely by hiding merchant UI controls.

Queued jobs that become runnable after the freeze must terminate safely/no-op once they establish the shop is frozen. Do not purge Redis as the correctness mechanism.

### App Event / usage publication while frozen

No new billable event may be created for business work after freeze is known.

A UsageEvent already committed before the freeze may remain durable, but provider publication must not retimestamp it or move it into a later Shopify cycle. If Shopify resumes within the same cycle, normal publication may continue. If the provider cycle advanced and the old event can no longer be billed, preserve the original event/evidence and use the existing attention/error path; do not silently bill it in the new cycle.

A top-up purchase that was already `PENDING_BILLING` before freeze remains pending. It does not grant credits merely because the shop later freezes. Provider confirmation can resume after unfreeze.

### Detecting freeze and cancellation safely

For established merchants, canonical reconciliation uses one provider reconciliation snapshot containing:

```text
activeSubscription
latest relevant subscription lifecycle event
```

Classification rules:

1. latest effective provider lifecycle event `FROZEN` -> local `FROZEN`, regardless of whether a live subscription object is temporarily still returned;
2. `activeSubscription = null` + latest lifecycle event `CANCELED` -> effective cancellation path (BACKGROUND-012);
3. `activeSubscription = null` + latest lifecycle event `FROZEN` -> frozen path, never cancellation;
4. `activeSubscription = null` + lifecycle evidence `UNFROZEN`, `CREATED`, `UPDATED`, `CANCELLATION_SCHEDULED`, or no usable event while a previous contract exists -> provider state is unresolved; fail closed and retry rather than inventing cancellation;
5. Partner transport/history failure is not cancellation and must never restore access.

Lifecycle evidence must never regress to an older provider event than the event already persisted locally.

### Frozen reconciliation and BullMQ recovery

Reuse the existing `billing-subscription-reconcile` queue. No new queue is introduced.

While frozen:

```text
nextReconcileAt = now + 1 hour
```

The billing worker's startup/repair pass must reconstruct missing delayed jobs from:

```text
Subscription.status = FROZEN
AND nextReconcileAt IS NOT NULL
```

Redis remains a disposable wake-up mechanism. PostgreSQL is the durable schedule/state source.

If Shopify remains frozen, persist the newer lifecycle evidence if any, advance `nextReconcileAt` by one hour, and enqueue the next deterministic delayed job.

### Unfreeze

Moda does not restore execution solely because a `SUBSCRIPTION_UNFROZEN` historical event appears. It must also obtain a usable live `activeSubscription` snapshot.

If Shopify is live again:

```text
same plan + same exact provider cycle
    -> restore ACTIVE/TRIALING
    -> reuse same BillingPeriod and counters

same plan + later provider cycle
    -> canonical BACKGROUND-007 rollover directly to Shopify's current cycle
    -> no synthetic intermediate periods
    -> grant only the current paid cycle allowance once
    -> Free plan rotates provider billing scope only

different effective plan
    -> delegate to BACKGROUND-010 plan-change transition
    -> preserve purchased + lifetime Free balances
```

If historical state says `UNFROZEN` but `activeSubscription` is still null, remain fail-closed and retry. Do not restore execution early.

After successful unfreeze, normal `nextReconcileAt` scheduling is restored. Existing capacity-blocked recoveries may receive the normal capacity-resume hint only after the subscription projection is executable again.


### Frozen Shopify-event processing boundary

Shopify webhook ingress remains intentionally lightweight and unchanged during a subscription freeze:

```text
Shopify webhook
  -> authenticate / validate / normalise
  -> durable BullMQ acceptance
  -> acknowledge Shopify
```

Moda does **not** add a synchronous subscription/billing database lookup to the Shopify HTTP request path.

The early freeze stop occurs after dequeue in `moda-shopify-event-worker`, where canonical tenant identity is already available. `ARCH-010-BACKGROUND-018` applies this rule:

```text
ACTIVE shop + FROZEN subscription

checkout.created
checkout.updated
cart.activity
    -> terminal expected no-op before candidate/recovery/provider work

order.completed
    -> bounded terminal safety bookkeeping only
       (cancel existing candidate / mark existing recovery completed)
    -> no new recovery/customer/conversation/billing/outbound work
```

The order exception is required so Moda does not later resume an abandoned-cart recovery for a checkout that converted to an order during the freeze. It is safety bookkeeping, not continued business execution.

Do not purge queues as correctness and do not replay discarded raw checkout/cart events on unfreeze. New events process normally only after BACKGROUND-012 restores an executable subscription.

### Frozen vs cancellation

Freeze and cancellation are distinct:

```text
FROZEN
  temporary Shopify billing hold
  preserve contract projection/counters/period
  all business execution paused
  retry automatically
  may return to ACTIVE

NO_CONTRACT after CANCELED
  Shopify contract ended
  final provider period closed
  paid monthly remainder forfeited
  lifetime balances preserved but non-spendable
  requires a new verified subscription
```

BACKGROUND-012 must therefore no longer interpret `activeSubscription = null` by itself as proof of cancellation.

### Tasks created by Iteration 11

- `ARCH-010-DATABASE-008` — persist `FROZEN` and latest Shopify subscription-lifecycle evidence.
- `ARCH-010-BACKGROUND-015` — add canonical Partner active+historical subscription reconciliation snapshot.
- `ARCH-010-BACKGROUND-012` — reconcile cancellation plus FROZEN/UNFROZEN in the single canonical subscription lifecycle state machine, including delayed retry/rebuild and safe cycle catch-up.
- `ARCH-010-BACKGROUND-013` — enforce distinct NO_CONTRACT and FROZEN business-execution/App-Event gates through one reusable policy boundary.
- `ARCH-010-BACKGROUND-018` — early-stop Shopify checkout/cart event processing for FROZEN shops while retaining order-completion terminal safety bookkeeping.
- `ARCH-010-SHOPIFY-018` — expose provider-authoritative merchant subscription lifecycle state including freeze/unfreeze.
- `ARCH-010-SHOPIFY-016` — present scheduled cancellation, effective NO_CONTRACT and FROZEN restriction states with explicit merchant action guards.

Existing cancellation, rollover, capacity and billing-action tasks are amended to consume this provider-state distinction rather than treating provider null as cancellation.


# Iteration 12 — Optional promotional recovery campaigns

Iteration 12 is amended for first release: promotions are **offers**, not automatic Admin grants. Multiple GLOBAL/PLAN/SHOP campaigns may run at once. Merchants see currently-running campaigns for which they are eligible and opt into one. A Shop may have at most one still-usable selected promotion for new recovery admission.

The selected eligible campaign grant has highest recovery-capacity priority:

```text
PAID
  selected promotion
  -> current-period included
  -> purchased lifetime
  -> lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION

FREE
  selected promotion
  -> purchased lifetime
  -> lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION
```

Campaigns have fixed target/quantity, start/expiry and durable audit history. Admin may close/reopen the same campaign by changing expiry/status only. Reopen never grants a second allocation to a merchant who already claimed it.

Exact campaign targeting, merchant selection, expiry/reservation semantics and history are canonical in [`ARCH-010-promotional-campaigns.md`](ARCH-010-promotional-campaigns.md).

## Iteration 12 task amendment

- `DATABASE-009` remains the completed promotional bucket/provenance foundation.
- `DATABASE-010` owns campaign catalogue/target/lifecycle audit.
- `DATABASE-011` owns campaign+shop allocation, one current selection and exact reservation ownership.
- `ADMIN-004` creates/activates GLOBAL/PLAN/SHOP campaigns; it no longer grants credits directly.
- `ADMIN-005` owns catalogue/close/reopen-by-expiry.
- `ADMIN-006` owns internal campaign merchant usage reporting.
- `SHOPIFY-021` owns eligible offer discovery and merchant opt-in.
- `SHOPIFY-020` owns selected-promo capacity presentation.
- `SHOPIFY-022` owns merchant promo history.
- `BACKGROUND-019` owns selected-promo-first reservation/commit/release.
- `SYSTEM-TEST-003` validates targeting, opt-in, exclusivity, expiry/reopen/history and promo-first consumption.


# Final consolidation and implementation acceptance boundary

ARCH-010 is architecture-complete as of 2026-09-11. The final task graph is intentionally granular and repository-owned. Historical iteration notes in this document explain how the design evolved, but the **canonical rules above and each task's final contract** control implementation.

## Provider assumptions re-verified at consolidation

The consolidation pass re-verified the current Shopify App Pricing documentation on 2026-09-11:

- Shopify App Pricing uses Partner `activeSubscription` plus Historical Events for current/pending/lifecycle truth;
- App Events are the App Pricing mechanism for usage-meter billing, including migrations from repeated one-time charges;
- Shopify App Pricing does not provide native one-time app purchases; Manual Pricing/Billing API remains the legacy/outlier route for those;
- usage-only / zero-recurring plans can carry usage meters;
- app-charge refunds/credits are handled through Shopify provider billing workflows, including partial refunds for paid charges and credits for unpaid charges.

ARCH-010 therefore does not introduce `appSubscriptionCreate`, `appSubscriptionCancel`, `appPurchaseOneTimeCreate` or `APP_SUBSCRIPTIONS_UPDATE` as App Pricing authority.

## Final implementation graph

Before implementation starts, task frontmatter is authoritative for eligibility. `depends_on` is the execution gate; `enables` is maintained as its reverse-index convenience only.

Current pre-implementation counts after consolidation:

```text
ARCH-010 tasks total:            79
implementation/publication:      74 (2 superseded, 72 active)
terminal system-test tasks:       5 manual-gated
complete implementation tasks:   23
review implementation tasks:      1
ready implementation tasks:       4
pending implementation tasks:    44
superseded tasks:                  2
pending manual system tests:       5
```

No implementation/publication/infrastructure task depends on an ARCH-010 system-test task.

## Terminal/manual test gate

The terminal validation chain is:

```text
ARCH-010-SYSTEM-TEST-001  core subscription/capacity/App Pricing lifecycle
ARCH-010-SYSTEM-TEST-002  uninstall/reinstall/cancel/freeze execution gates
ARCH-010-SYSTEM-TEST-003  purchased-credit refunds + promotional operations
             \               |               /
              -> ARCH-010-SYSTEM-TEST-004 final cross-scenario acceptance
```

These tasks are dependency-ready only when their implementation prerequisites are Complete; they still require explicit developer invocation.

## Deliberate future scope, not ARCH-010 gaps

The following are intentionally deferred and must not be improvised by implementation agents:

- expiring or automatically revocable promotional credits;
- automatic promotional campaign scheduling/marketing delivery;
- self-service merchant refund settlement or automatic negative-App-Event refund settlement;
- Moda-owned subscription-fee refunds/cancellation mutations;
- automatic Paid overage;
- a local append-only duplicate of Shopify's full provider subscription history;
- mid-cycle plan-entitlement segmentation/proration if Shopify unexpectedly makes immediate same-cycle plan changes normal;
- deterministic Shopify shop re-identification redesign beyond the current accepted identity mechanism.

If any deferred condition becomes required by real provider behaviour, return to `moda_architect` rather than extending an existing task silently.



## Admin commercial guardrail — upgrade economics

ARCH-010 protects the structural relationship between each lower plan, its recovery-credit-pack economics and the explicitly configured next paid tier. This is an **internal Admin guardrail**, not merchant runtime billing logic.

Default policy:

```text
lower recurring price + cheapest top-up cost needed to reach next-plan MONTHLY capacity
>= next recurring price * 1.20
```

The threshold is durable platform policy in basis points. Upgrade order is represented by explicit BillingPlan-ID edges; no plan name/price/rank inference is allowed. Shopify App Pricing remains monetary authority. Admin stores append-only verified economics snapshots only as audit evidence for the guardrail.

The guardrail excludes lifetime-Free credits, promotional credits, purchased-credit balances and current merchant usage. For this calculation Free monthly included capacity is `0`.

`PASS` is required for economics-affecting activation/mutation. `FAIL` and `UNVERIFIED` both block server-side. The pure evaluator and exhaustive scenario matrix are frozen in `docs/contracts/ARCH-010-upgrade-economics-guardrail.reference.ts` and `docs/contracts/ARCH-010-upgrade-economics-guardrail-test-matrix.md`.
