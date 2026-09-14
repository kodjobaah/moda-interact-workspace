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
status: complete
priority: 60
executor: null
claimed_at: null
attempt: 3
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
updated: 2026-09-14
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

### Completion Report

### Status
Ready for Review after corrective attempt 3.

### Files Changed
- Implementation: `app/routes/app/billing/route.tsx` and `tests/unit/billing-ui.test.ts` only.
- Parent repository: this task report only.

### Work Completed
- `/app/billing` now reads the existing local recovery-capacity projection alongside billing state and returns only `lifecycleRestriction: capacity.availability`.
- Scheduled full cancellation uses `cancelAtPeriodEnd === true` with no pending plan to suppress the legacy top-up control while retaining Shopify-hosted plan management.
- `CONTRACT_FROZEN` suppresses both the legacy top-up control and `/app/billing/select` plan-management link; existing server action guards and all unrelated lifecycle behavior remain unchanged.
- Added the two required rendered billing UI regression tests; existing direct-action rejection tests remain intact.

### Validation Results
- Focused validation: `npm test -- --run tests/unit/billing-ui.test.ts` -> 1 file passed, 20 tests passed, 0 failed.
- `git diff --check` passed.
- `npm run typecheck` remains nonzero on existing repository-wide JSX implicit-any and unrelated diagnostics; neither touched file appears in the diagnostics after the local test typing fix.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-016`.
- Implementation branch: `task/ARCH-010-SHOPIFY-016`, commit `3de1f33fd321e72919cb26f7f1dca56c2abdad16`, pushed to `origin/task/ARCH-010-SHOPIFY-016`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-016`.
- Attempt-3 parent claim commit: `e6e282648b16d9bfa76014170e2bb84bcfff228c`.
- No submodule gitlink or unrelated parent files were changed.

### Architect Review
Pending.

## Architect Review — Attempt 2

### Status

**Changes Requested — one merchant-surface functional correction only**

This review intentionally prioritises production functionality over exhaustive test
coverage.

The Attempt-2 lifecycle work is broadly accepted:

```text
/app keeps post-onboarding NO_CONTRACT merchants on the merchant dashboard
fresh NO_CONTRACT onboarding remains on onboarding
FROZEN has dashboard/banner precedence
pending plan change is not mislabelled as full cancellation
scheduled cancellation shows the provider-effective period end
SHOPIFY-009 CONTRACT_REQUIRED / CONTRACT_FROZEN capacity is consumed
billing/options disables top-up under lifecycle restriction
billing/options disables plan management while FROZEN
direct top-up actions fail closed
/app/billing/select fails closed while FROZEN
provider verification failure is not replaced with local commercial guesses
no merchant Admin exposure
no local Shopify cancellation mutation
no recurring Partner polling on the ordinary /app dashboard
```

The translated lifecycle copy is also accepted and does not need further churn.

One existing merchant billing surface still violates the same action matrix.

---

### Finding — `/app/billing` still exposes forbidden UI actions under restricted lifecycle states

File:

```text
app/routes/app/billing/route.tsx
```

The direct server action is correctly guarded, but the rendered page does not apply
the same lifecycle restrictions.

#### A. Scheduled full cancellation can still render the legacy top-up purchase form

The action correctly rejects:

```text
cancelAtPeriodEnd = true
pendingPlan = null
```

However the render condition for the purchase form still depends only on:

```text
billingPeriodPhase === ACTIVE
recoveryCreditPackPurchaseEligible
recoveryCreditPackEnabled
credits/meter verification
```

`getMerchantBillingState()` does not use scheduled full cancellation itself as a
purchase-eligibility veto.

Therefore this valid state is possible:

```text
Subscription ACTIVE
current exact provider cycle still OPEN
pack meter still verified
cancelAtPeriodEnd = true
pendingPlan = null
```

and `/app/billing` can render:

```text
Buy recovery credit pack
```

even though submitting the form is rejected by the action.

That violates the binding state matrix:

```text
scheduled full cancellation
  -> top-up UI unavailable
  -> direct top-up action denied
```

The server guard alone is not sufficient because this task explicitly requires both.

#### B. FROZEN/restoring still renders the legacy plan-change link

At the bottom of `/app/billing`, the route currently renders:

```tsx
<Link to="/app/billing/select">
  ...
</Link>
```

unconditionally.

When durable capacity is:

```text
CONTRACT_FROZEN
```

the `/app/billing/select` server loader correctly returns 403, but the merchant still
sees and can click the plan-change CTA.

That violates:

```text
FROZEN/restoring
  -> plan-change CTA unavailable
  -> direct plan-select invocation denied
```

Again, the server guard is correct; the rendered action is not.

---

### Required correction

Modify only:

```text
app/routes/app/billing/route.tsx
```

Use the durable state already available to this route. Do not introduce a Partner API
call.

#### Loader

Extend the existing loader result with the local recovery-capacity projection:

```ts
const [state, capacity] = await Promise.all([
  billingService.getMerchantBillingState(shop.id),
  billingService.getMerchantRecoveryCapacityState(shop.id),
]);
```

or an equivalent existing-query composition if preferred.

Return only the minimal lifecycle authority needed by the component, for example:

```ts
lifecycleRestriction: capacity.availability
```

Do not create another lifecycle vocabulary.

The accepted meanings are:

```text
CONTRACT_FROZEN   -> frozen/restoring
CONTRACT_REQUIRED -> effective no-contract
other values      -> existing behavior
```

The route already has `subscription.cancelAtPeriodEnd` and pending-plan information.

#### Scheduled cancellation UI

Define scheduled full cancellation using the same rule as the action:

```text
subscription.cancelAtPeriodEnd === true
AND no pending plan
```

Do not hide top-up for a pending plan change solely because the outgoing provider
state also carries cancellation-at-end semantics.

The legacy purchase form must not render when scheduled full cancellation is true.

Do not change the existing server action guard.

#### FROZEN plan-management UI

When:

```text
lifecycleRestriction === CONTRACT_FROZEN
```

do not render the `/app/billing/select` Change/View plans link.

Do not replace it with a local cancellation/reactivation action.

For:

```text
scheduled cancellation
```

the Shopify-hosted plan-management link remains available.

For:

```text
effective NO_CONTRACT / CONTRACT_REQUIRED
```

the Shopify-hosted plan-selection link remains available so the merchant can establish
a new provider contract.

Fresh onboarding behavior remains owned by the existing onboarding flow.

#### Optional presentation consistency

If the route already has an appropriate localized string available, it may display the
existing frozen/contract-required explanatory copy. This is optional for this attempt.

Do not add new translation keys unless genuinely necessary.

---

### Functional regression evidence required

No broad lifecycle matrix is required.

Update:

```text
tests/unit/billing-ui.test.ts
```

with only these two behavior tests.

#### Scheduled cancellation

Render or inspect the actual `BillingRoute` with:

```text
subscription.status = ACTIVE
cancelAtPeriodEnd = true
pendingPlanName = null
billingPeriodPhase = ACTIVE
recoveryCreditPackPurchaseEligible = true
valid pack configuration/meter
```

Require:

```text
Buy recovery credit pack control is absent
Shopify plan-management link remains present
```

The existing direct-action rejection test must continue to pass.

#### FROZEN

Render the route with:

```text
capacity.availability = CONTRACT_FROZEN
```

Require:

```text
/app/billing/select plan-change link is absent
top-up purchase control is absent
```

The existing direct `/app/billing/select` 403 behavior remains unchanged.

No additional locale, provider, home-route, or component test expansion is required.

---

### Accepted Attempt-2 work — do not churn

Do not redesign:

```text
app/routes/app/home/route.jsx
app/components/dashboard/LifecycleRestrictionBanner.jsx
app/routes/app/billing/options/route.tsx
app/routes/app/billing/select/route.jsx
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/TopUpPurchasePanel.jsx
app/components/dashboard/SubscriptionChangePanel.jsx
app/services/billing/billing.service.ts
app/i18n/locales/*.json
```

unless a mechanical import/type adjustment is required by the narrow `/app/billing`
loader change.

Preserve:

```text
FROZEN > pending plan > scheduled cancellation > NO_CONTRACT precedence
post-onboarding NO_CONTRACT dashboard access
fresh-onboarding behavior
preserved informational balances
CONTRACT_FROZEN / CONTRACT_REQUIRED capacity projection
server-side top-up guards
server-side FROZEN plan-select guard
scheduled-cancellation plan-management availability
no local cancellation mutation
no Admin exposure
```

---

### Attempt-3 allowed scope

Production:

```text
app/routes/app/billing/route.tsx
```

Tests:

```text
tests/unit/billing-ui.test.ts
```

plus this task/Completion Report.

If this cannot be corrected without changing provider APIs, schema, Shared contracts,
Background behavior, or merchant routing architecture, STOP and return the exact
limitation to `moda_architect`.

---

### Attempt-3 validation

Prioritise functional behavior:

```bash
npm exec vitest run tests/unit/billing-ui.test.ts
npm run build
git diff --check
```

Run the existing full test suite only for regression awareness.

Typecheck's existing repository-wide implicit-any baseline remains non-blocking if
unchanged.

Do not spend Attempt 3 correcting unrelated typecheck diagnostics.

---

### Workflow / Completion Report

Preserve Attempt-2 publication history:

```text
Attempt-2 launcher claim:
920cdf03038265aa17117ee0491d4128a4965d03

Attempt-2 implementation:
10a6eaf

Attempt-2 parent report:
78e2e69
```

Record full SHAs in the Completion Report when available.

Return this SAME task through `/moda-task`.

Preserve:

```text
attempt: 2
```

The next authorized claim must increment to **Attempt 3 exactly once**.

Attempt 3 may return to review when:

```text
1. scheduled full cancellation cannot render the /app/billing top-up purchase control;
2. FROZEN/restoring cannot render the /app/billing plan-change CTA;
3. scheduled cancellation and effective NO_CONTRACT still retain Shopify-hosted plan
   management/selection as required;
4. existing server guards remain intact;
5. focused functional test and build pass;
6. no new repository regression is introduced;
7. status = review, executor = null, claimed_at = null;
8. both worktrees are clean and pushed.
```

Then STOP and return to `moda_architect`.

`ARCH-010-SYSTEM-TEST-002` remains terminal/manual-gated until this task is
architect-accepted Complete.

## Architect Review — Attempt 3

### Status

**Accepted**

This review intentionally prioritises merchant-facing functionality and server-side
behavior over exhaustive test coverage.

Attempt 3 closes the two remaining functional defects identified in Attempt 2.

### Accepted scheduled-cancellation billing behavior

`/app/billing` now derives scheduled full cancellation using the same binding rule as
the server action:

```text
cancelAtPeriodEnd = true
AND no pending plan
```

When that state is present:

```text
legacy recovery-credit top-up control -> hidden
direct recovery-credit top-up action  -> denied
Shopify-hosted plan management        -> remains available
```

This preserves the important distinction between:

```text
scheduled full cancellation
```

and:

```text
pending plan change
```

A provider pending plan change is therefore not accidentally treated as a full
cancellation merely because the outgoing provider state also carries
`cancelAtPeriodEnd`.

### Accepted FROZEN/restoring billing behavior

`/app/billing` consumes the existing durable recovery-capacity projection and uses:

```text
CONTRACT_FROZEN
```

as the merchant action restriction.

When FROZEN/restoring:

```text
legacy recovery-credit top-up control -> hidden
/app/billing/select plan CTA          -> hidden
direct top-up action                  -> denied
direct billing/select invocation      -> denied
informational billing balances        -> remain readable where already supported
```

No new Partner API call or duplicate lifecycle vocabulary was introduced.

### Accepted effective NO_CONTRACT behavior

Effective post-onboarding `NO_CONTRACT` / `CONTRACT_REQUIRED` remains distinct from
FROZEN.

The merchant can still reach Shopify-hosted plan selection/management in order to
establish a new provider contract, while recovery-credit purchase remains unavailable.

Fresh onboarding behavior remains owned by the existing onboarding flow.

### Accepted lifecycle precedence and presentation

The previously accepted merchant lifecycle precedence remains intact:

```text
1. FROZEN/restoration-pending
2. pending plan change
3. scheduled full cancellation
4. effective post-onboarding NO_CONTRACT
5. fresh onboarding NO_CONTRACT
6. ordinary ACTIVE/TRIALING
7. provider verification uncertainty remains uncertainty
```

The Attempt-3 change does not alter:

```text
/app dashboard lifecycle banner behavior
billing/options purchase hub behavior
Shopify-hosted plan-management flow
translated lifecycle labels
provider lifecycle read model
server-side action guards
```

### Functional acceptance

The UI and action layers now agree on the merchant action matrix:

```text
scheduled full cancellation:
  top-up UI             -> unavailable
  direct top-up         -> denied
  Shopify plan manager  -> available

FROZEN/restoring:
  top-up UI             -> unavailable
  direct top-up         -> denied
  plan-change CTA       -> unavailable
  direct plan select    -> denied

effective NO_CONTRACT:
  top-up                -> unavailable
  Shopify plan select   -> available
```

That is the functional objective of this correction.

### Validation accepted

```text
Focused billing UI:
  20 passed

git diff --check:
  passed

Touched-file diagnostics:
  clear

Typecheck:
  existing repository-wide implicit-any baseline remains
  no Attempt-3 touched-file regression reported
```

Acceptance is based on the runtime behavior above, not on exhaustive lifecycle-test
enumeration.

### Accepted implementation evidence

Developer handoff:

```text
Implementation:
3de1f33fd321e72919cb26f7f1dca56c2abdad16

Parent report:
08587a9
```

Attempt-3 parent claim recorded in the task report:

```text
e6e282648b16d9bfa76014170e2bb84bcfff228c
```

Both implementation and parent branches were reported clean and pushed.

### Dependency reconciliation

`ARCH-010-SHOPIFY-016` is Complete.

`ARCH-010-SYSTEM-TEST-002` now has all implementation prerequisites Complete, but it
remains:

```text
status: pending
completion_mode: manual
```

because ARCH-010 system tests are terminal/manual-gated and are not auto-started.

The individual `ARCH-010-SHOPIFY-012` task in this snapshot is already Complete; the
Shopify `_index.md` still listed it as Ready and is corrected by this acceptance.

The current automatic implementation-ready frontier is:

```text
ARCH-010-SHOPIFY-025
```

No Attempt 4 is required for `ARCH-010-SHOPIFY-016`.

