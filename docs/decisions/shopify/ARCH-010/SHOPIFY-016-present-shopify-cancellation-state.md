---
id: ARCH-010-SHOPIFY-016
architecture_id: ARCH-010
title: Present Shopify cancellation state without local cancellation authority
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-SHOPIFY-009
- ARCH-010-SHOPIFY-012
- ARCH-010-SHOPIFY-013
- ARCH-010-BACKGROUND-012
- ARCH-010-BACKGROUND-013
enables:
- ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-SHOPIFY-016: Present Shopify cancellation state without local cancellation authority

## Objective

Make merchant-facing Moda surfaces accurately present scheduled/effective Shopify subscription cancellation while keeping Shopify as the only cancellation authority.

Moda must not expose a local `Cancel subscription` action that calls Billing API.

## Inspect before editing

```text
app/routes/app/route.tsx
app/routes/app/billing/options/route.tsx
app/components/billing/SubscriptionChangePanel.*
app/components/billing/BillingPurchaseHub.*
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/providers/shopify-billing.provider.ts
SHOPIFY-009 capacity projection implementation
SHOPIFY-012 billing-options integration
SHOPIFY-013 authoritative commercial read model
relevant i18n catalogs/tests
```

## Authority

Use SHOPIFY-013 commercial state for:

```text
current provider plan
current provider billing cycle
cancelAtEndOfCycle
pendingUpdate
```

Use Moda local durable projection/counters for:

```text
current executable contract projection
lifetime Free balance
purchased balance
paid included balance/history
```

Never infer cancellation from a local `BillingPlan` row.

## Cancellation classification for UI

Classify in this order.

### 1. Pending plan change exists

If Shopify has `pendingUpdate`, present the plan-change state owned by `ARCH-010-SHOPIFY-015` / `ARCH-010-BACKGROUND-010`.

Do not label it full cancellation merely because the outgoing provider subscription also has `cancelAtEndOfCycle=true`.

### 2. Full cancellation scheduled

```text
activeSubscription != null
cancelAtEndOfCycle = true
pendingUpdate = null
```

Present:

- current plan remains active until the exact current cycle end;
- recoveries/current conversations remain available under normal entitlement until then;
- new top-up purchase is disabled;
- purchased and lifetime Free balances are not deleted;
- a localized warning/banner on `/app` and `/app/billing/options`;
- a Shopify-managed subscription link/CTA using the existing hosted plan-management route, without promising that Moda itself can undo cancellation.

Do not redirect the merchant away from the dashboard.

### 3. Effective no contract for an existing onboarded merchant

When local Subscription is NO_CONTRACT after the merchant previously completed onboarding:

- keep `/app` as the normal merchant landing surface;
- keep usage/events/recovery history/support/billing navigation readable;
- show a localized `subscription ended / choose a plan to resume` banner;
- show purchased and lifetime Free balances as **preserved but currently non-spendable**;
- top-up purchase unavailable because there is no active Shopify plan/meter/cycle;
- plan-selection/manage CTA remains available through Shopify-hosted pricing;
- do not set `onboardingCompleted=false` in this task;
- do not send the merchant to `moda-interact-admin`.

### 4. Fresh never-activated NO_CONTRACT merchant

Preserve the fresh-install/onboarding behavior from `ARCH-010-SHOPIFY-001`:

```text
onboardingCompleted=false
-> onboarding / plan-selection flow
```

Do not use the post-cancellation dashboard state for a never-activated merchant.

## Capacity read model amendment

Consume SHOPIFY-009's explicit `CONTRACT_REQUIRED`/equivalent state for an onboarded NO_CONTRACT merchant.

Do not display this as `EXHAUSTED` even when local lifetime balances are zero.

Required distinction:

```text
EXHAUSTED
  active executable Shopify contract exists
  but all usable recovery-credit sources are exhausted

CONTRACT_REQUIRED
  no executable Shopify contract exists
  balances may still be preserved
```

## Top-up behavior

Disable the Buy top-up CTA when either:

```text
full cancellation scheduled
OR
NO_CONTRACT
```

Do not call `requestRecoveryCreditPack()` in either state.

The UI must explain that preserved purchased/lifetime credits remain on the merchant account but require an active Shopify plan before recovery execution resumes.

## Existing conversations/history

After effective cancellation, merchant UI may still show historical conversations/messages/recoveries. Do not imply those conversations are actively serviced.

Background execution behavior is owned by BACKGROUND-013.

## Required tests

At minimum prove:

1. pending plan change is shown as plan change, not full cancellation;
2. scheduled full cancellation displays exact provider cycle end;
3. scheduled cancellation leaves dashboard/history accessible;
4. scheduled cancellation disables top-up CTA/action;
5. scheduled cancellation does not hide current balances;
6. effective NO_CONTRACT + onboardingCompleted=true lands on dashboard/read-only merchant app rather than onboarding;
7. fresh NO_CONTRACT + onboardingCompleted=false still uses onboarding;
8. effective cancellation shows CONTRACT_REQUIRED rather than EXHAUSTED;
9. preserved purchased credits display but are not spendable while NO_CONTRACT;
10. preserved lifetime Free credits display but are not spendable while NO_CONTRACT;
11. plan-selection/manage CTA routes through Shopify-hosted pricing;
12. no local `appSubscriptionCancel` action exists;
13. no Admin route/link is exposed;
14. Shopify verification failure is presented as verification unavailable, not cancellation;
15. local BillingPlan data is never used to claim cancellation/commercial truth;
16. i18n covers scheduled/end/no-contract messaging.

## Non-goals

Do not implement cancellation mutation, Admin approval, top-up refund, resubscription entitlement activation, freeze handling or deterministic shop identity redesign.

## Stop conditions

Stop and return to `moda_architect` if the existing merchant route architecture cannot distinguish `onboardingCompleted=false` fresh NO_CONTRACT from `onboardingCompleted=true` post-cancellation NO_CONTRACT without rewriting unrelated onboarding flows.


## Final frozen-versus-canceled distinction

Cancellation presentation MUST consume SHOPIFY-018 lifecycle state. Provider `activeSubscription=null` with latest FROZEN must show the frozen/paused state, not subscription-ended/NO_CONTRACT messaging. Effective cancellation presentation requires provider CANCELED evidence plus the reconciled local NO_CONTRACT transition.

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
