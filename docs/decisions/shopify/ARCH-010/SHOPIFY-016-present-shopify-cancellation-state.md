---
id: ARCH-010-SHOPIFY-016
architecture_id: ARCH-010
title: Present cancellation, NO_CONTRACT and FROZEN merchant restriction states
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
  - ARCH-010-SHOPIFY-018
  - ARCH-010-BACKGROUND-012
  - ARCH-010-BACKGROUND-013
enables:
  - ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: 2026-09-12
---

# ARCH-010-SHOPIFY-016: Present cancellation, NO_CONTRACT and FROZEN merchant restriction states

## Consolidation

This task absorbs `ARCH-010-SHOPIFY-019`. `SHOPIFY-019` is superseded and MUST NOT be implemented separately.

The merge is deliberate: cancellation-scheduled, effective NO_CONTRACT and FROZEN are mutually exclusive merchant restriction states rendered on the same merchant surfaces and guarding the same billing actions. One explicit state matrix prevents conflicting banners/actions.

## Objective

Make `/app` and `/app/billing/options` present the current Shopify lifecycle restriction truth accurately while keeping merchants in the merchant application for read/history/support where allowed.

Shopify remains cancellation/freeze authority. Moda exposes no local subscription cancellation mutation and no Admin access.

## Inspect before editing

```text
app/routes/app/home/route.jsx
app/routes/app/billing/route.tsx
app/routes/app/billing/options/route.tsx
app/routes/app/billing/select/route.jsx
app/routes/app/merchant-support/route.jsx
app/services/billing/billing.service.ts
app/services/shop/shop-access-policy.ts
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/TopUpPurchasePanel.jsx
app/components/dashboard/SubscriptionChangePanel.jsx
app/i18n/locales/*.json
tests/unit/home-route.test.ts
tests/unit/billing-ui.test.ts
tests/unit/services/billing.service.test.ts
tests/unit/billing-i18n.test.ts
```

Consume `SHOPIFY-018` provider lifecycle read state and the durable local Subscription projection. Ordinary dashboard rendering MUST NOT add recurring Partner API polling.

## Binding state precedence

Render/guard in this exact precedence order:

1. `FROZEN` durable/restoration-pending lifecycle;
2. provider pending plan update;
3. scheduled full cancellation (`cancelAtEndOfCycle=true`, no pending update);
4. effective post-onboarding `NO_CONTRACT`;
5. fresh onboarding `NO_CONTRACT` (`onboardingCompleted=false`);
6. ordinary active/trialing state;
7. provider verification unavailable is presentation uncertainty and MUST NOT be converted into cancellation/freeze/current-plan truth from local price mappings.

Pending plan update always renders as plan change, not full cancellation.

## Merchant state matrix

### A. FROZEN

Required behaviour:

- `/app` remains normal landing/dashboard, not first-time onboarding;
- usage/events/recovery/history and historical conversation/recovery detail remain readable under existing access policy;
- show localized `Subscription paused by Shopify`/equivalent message;
- explain Shopify billing must be resolved before Moda resumes;
- do not promise an exact restoration/reactivation time;
- show current/mapped provider identity when available;
- show balances/history as preserved but non-spendable;
- support remains available;
- top-up CTA/action is unavailable;
- plan-change CTA/action is unavailable while local execution remains FROZEN/restoration-pending;
- provider ACTIVE while local FROZEN renders a restoring/verifying state and keeps mutations disabled;
- do not redirect to onboarding;
- do not call FROZEN cancellation or credit exhaustion.

Direct server invocation of top-up or plan-change/select actions while FROZEN MUST fail closed even if a UI control is bypassed.

### B. Pending provider plan update

Render the plan-change state owned by SHOPIFY-015/BACKGROUND-010.

Do not show full-cancellation messaging solely because outgoing provider data also carries cancellation-at-cycle-end semantics.

### C. Scheduled full cancellation

While the current provider contract remains active through exact period end:

- dashboard/history/current conversations/recoveries remain available under normal entitlement;
- show localized scheduled-end warning with exact provider cycle end;
- show existing balances normally;
- disable new top-up purchase/action;
- keep Shopify-hosted Manage/Change plan CTA available so the merchant can use Shopify's own management surface;
- do not offer local `Cancel subscription`/undo mutation;
- do not claim entitlement ended early.

### D. Effective NO_CONTRACT after onboarding

When `onboardingCompleted=true` and Subscription is NO_CONTRACT:

- keep `/app` as merchant landing surface rather than first-time onboarding;
- keep usage/events/recovery history/support/billing navigation readable;
- show localized `subscription ended / choose a plan to resume` message;
- show preserved purchased/lifetime-Free/promotion balances as non-spendable;
- new top-up is unavailable because there is no active provider contract/meter/cycle;
- new recovery/business actions are unavailable through Background gate;
- Shopify-hosted plan-selection/manage CTA remains available;
- present a CONTRACT_REQUIRED/canonical lifecycle restriction, never RECOVERY_CAPACITY_EXHAUSTED;
- do not set onboarding false in this task.

### E. Fresh NO_CONTRACT onboarding

When `onboardingCompleted=false`, preserve the existing first-install onboarding behaviour. Do not route a fresh merchant into post-cancellation dashboard semantics.

### F. Provider verification unavailable

Do not use local BillingPlan price/name/rank as proof of cancellation, freeze or active provider commercial state. Render a bounded verification-unavailable state when an explicit provider verification surface needs it while preserving durable access rules.

## Capacity projection source

Consume the already-defined `SHOPIFY-009` local recovery-capacity projection rather than creating a second lifecycle/capacity vocabulary.

For durable/restoration-pending FROZEN state, the projection must remain the canonical equivalent of:

```text
availability = CONTRACT_FROZEN
canStartRecovery = false
```

Informational Paid-included, promotional, purchased and lifetime-Free balances may remain visible, but they are non-spendable while FROZEN. Do not zero balances and do not report ordinary `EXHAUSTED`.

For effective post-onboarding `NO_CONTRACT`, consume the corresponding `CONTRACT_REQUIRED` projection from SHOPIFY-009 rather than reclassifying preserved balances as available capacity.

## Action guards

Server-side action guards are mandatory; UI disabled state is not security/correctness authority.

| State | New top-up | Shopify-hosted plan select/change |
|---|---|---|
| ACTIVE/TRIALING normal | normal SHOPIFY-014/015 rules | allowed |
| scheduled full cancellation | DENY top-up | allowed |
| FROZEN/restoring | DENY | DENY until restored |
| effective NO_CONTRACT after onboarding | DENY | allowed to establish new provider contract |
| fresh NO_CONTRACT onboarding | DENY | allowed through onboarding selection flow |

Do not add a Moda cancellation/refund mutation as a workaround.

## No Admin boundary

No route, banner, button, support CTA or redirect may expose `moda-interact-admin` to merchants.

## Required tests

1. pending plan update renders as plan change, not cancellation;
2. scheduled full cancellation renders exact provider cycle end;
3. scheduled cancellation leaves dashboard/history accessible;
4. scheduled cancellation disables top-up UI and direct server action;
5. scheduled cancellation keeps Shopify-hosted plan management available;
6. scheduled cancellation preserves visible balances/current entitlement until boundary;
7. effective NO_CONTRACT + onboarding complete lands in merchant dashboard/read-only app, not onboarding;
8. fresh NO_CONTRACT + onboarding incomplete still uses onboarding;
9. effective NO_CONTRACT renders CONTRACT_REQUIRED, not EXHAUSTED;
10. purchased/lifetime-Free/promotion balances remain visible but non-spendable under NO_CONTRACT;
11. FROZEN merchant lands on `/app`, not onboarding;
12. FROZEN dashboard/history/usage remain readable;
13. frozen banner can render from durable local state without Partner call on ordinary dashboard render;
14. billing options renders FROZEN distinctly from cancellation/exhaustion;
15. FROZEN disables top-up UI and direct server action;
16. FROZEN disables plan-change UI and direct `/app/billing/select` invocation;
17. support remains available while FROZEN;
18. provider ACTIVE + local FROZEN renders restoring state and remains mutation-disabled;
19. successful local restoration removes frozen warning on next normal read;
20. provider verification failure does not fabricate cancellation/freeze/active truth from local mapping;
21. no local `appSubscriptionCancel` action exists;
22. no Admin route/link/redirect is exposed;
23. all new visible strings satisfy locale/i18n parity;
24. FROZEN consumes SHOPIFY-009's `CONTRACT_FROZEN`/canonical projection with `canStartRecovery=false` even when balances remain;
25. FROZEN presentation does not zero informational balances or relabel the state as ordinary capacity exhaustion.

## Non-goals

Do not implement Background lifecycle reconciliation/gates, provider subscription mutations, refund settlement, new provider polling loops, credit mutations or shop identity redesign.

## Validation

Inspect `package.json`. Run focused home/billing/action/component/i18n tests, then repository-declared test/typecheck/build commands and `git diff --check`. Do not invent scripts.

## Stop conditions

STOP and return to `moda_architect` if:

1. current merchant routing cannot distinguish fresh NO_CONTRACT from post-onboarding NO_CONTRACT without rewriting unrelated onboarding architecture;
2. direct billing actions cannot consume current lifecycle restriction state without duplicating a second Partner API implementation;
3. the implementation would need Admin exposure or local Shopify cancellation mutation.

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
