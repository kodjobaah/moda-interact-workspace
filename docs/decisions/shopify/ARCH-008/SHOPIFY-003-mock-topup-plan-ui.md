---
id: ARCH-008-SHOPIFY-003
architecture_id: ARCH-008
title: Add mock UI components for recovery top-ups and plan upgrades
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-007-SHOPIFY-002
enables: []
created: 2026-09-10
updated: 2026-09-11
---

# ARCH-008-SHOPIFY-003: Add mock UI components for recovery top-ups and plan upgrades

## Supersession — ARCH-010

Superseded on 2026-09-11 by `ARCH-010-SHOPIFY-008`. The existing `/app/billing/options` screen is retained, but its mock-only implementation direction is replaced by a real server-backed capacity-management implementation. Do not continue this task as a separate prototype. Historical review/completion evidence below is preserved for audit.

## Objective

Add a polished, non-networked merchant UI prototype showing how a merchant can
top up recovery credits and choose a plan upgrade from the existing onboarding
experience. This task is visual and interaction-only: it must not create real
Shopify billing, App Events, database writes, or provider calls.

## Context

ARCH-008 keeps Shopify App Pricing authoritative. The prototype must communicate
that plan changes are completed through Shopify-hosted pricing and that recovery
top-ups are pending Shopify confirmation. Reuse the existing `Onboarding.jsx`,
merchant i18n runtime, and onboarding stylesheet conventions.

The app also resolves the current Shopify shop from authenticated route
loaders. That resolution must not reactivate a merchant suspended for abuse or
another platform-level reason. Lifecycle reactivation is an installation
concern, not a normal page-load side effect.

Access decisions may also depend on the requested route and capability, not
only on the shop lifecycle status. Denied access must provide a useful merchant
flow: operational capability denials redirect to merchant support, while an
uninstalled shop attempting to access support redirects to the login/start
flow. A newly installed shop that has not completed onboarding continues to
start at the billing/onboarding page.

## Scope

Modify only the `moda-interact` repository surfaces needed for this prototype:

- `app/components/onboarding/Onboarding.jsx`;
- `app/components/onboarding/Onboarding.css`;
- the existing merchant locale catalogues for new copy;
- focused onboarding component/source tests, if the repository has an applicable
  test surface.

Do not change billing services, database schemas, Shopify provider code, shared
packages, or the package/export architecture. Route/auth changes are limited
to wiring the explicit installation reactivation operation.

## Shop Lifecycle Safety Requirement

- Normal `resolveShopifyShop()` calls must preserve the existing `Shop.status`
  and `uninstalledAt` values.
- A normal page load must never transition `SUSPENDED` to `ACTIVE`.
- A genuine installation or reinstallation may transition
  `UNINSTALLED -> ACTIVE` through an explicit installation-scoped operation.
- The explicit reactivation operation must not transition `SUSPENDED` to
  `ACTIVE`.
- Tests must cover new-shop creation, repeated resolution, suspended-shop
  preservation, uninstalled-shop reactivation, and duplicate/repeated
  installation handling.

## Contextual Access and Redirect Requirement

- Access-policy checks must receive the originating route and, when relevant,
  the requested capability so future policy rules can distinguish actions such
  as reading usage, managing billing, reading messages, and sending messages.
- Access-policy checks must receive an explicit safe redirect destination.
- A suspended shop denied an operational capability must be redirected to
  `/app/merchant-support`, where it can contact Moda Interact.
- An uninstalled shop denied support access must be redirected to
  `/auth/login` rather than shown a raw forbidden response or sent into a
  redirect loop.
- Incomplete onboarding for a newly installed shop must continue to redirect
  to `/app/billing`.
- The policy must not add message quotas, abuse limits, or other capability
  restrictions unless those are separately specified and implemented as a
  persisted policy requirement.

## Merchant Support Internationalisation Requirement

- The merchant-support page must use the existing merchant ICU/i18n runtime for
  every merchant-visible UI string, including thread headings, empty states,
  pagination, compose controls, validation feedback, action errors, author
  labels, translation states, and original/translated message toggles.
- Reuse the existing `merchantUiContext()` and `createMerchantI18n()` flow; do
  not introduce a second translation mechanism or translate persisted message
  bodies in the route component.
- Add the merchant-support catalogue keys to every locale registered in
  `app/i18n/catalogues.js`, preserving ICU placeholder names such as `{page}`
  and `{totalPages}`.
- Generic action failures must be represented by catalogue keys. Existing
  validation details may remain in the response when they are needed for
  diagnostics, but the rendered merchant-facing fallback must be localized.

## Required UI

Add two clearly distinct mock components to the existing onboarding page:

1. **Recovery top-up mock**
   - show the current purchased-credit balance and a selected pack quantity;
   - provide a bounded pack selector or equivalent mock control;
   - show a translated pending-confirmation state after the mock action;
   - make clear that the pack is billed by Shopify according to the current plan;
   - keep the action local to the component with no network or billing mutation.

2. **Plan-upgrade mock**
   - show the current plan and at least two available higher plans from the
     existing plan catalogue;
   - allow selecting a higher plan in local component state;
   - show a mock CTA that communicates the merchant will continue to Shopify
     hosted pricing;
   - do not imply that the app directly approves, creates, or charges a plan.

Use the existing `plans` and top-up data where practical. Keep the prototype
responsive and accessible: semantic headings, labels, keyboard-operable controls,
visible focus states, and no overlapping or clipped content at mobile widths.

## Internationalisation

Every new merchant-visible string must use the existing merchant ICU/i18n path.
Add each new key to every locale catalogue currently declared by `moda-interact`.
Preserve placeholder names and do not add hard-coded English UI copy in JSX.
Do not create a second translation runtime or locale mechanism.

## Explicit Non-goals

- no real plan upgrade or top-up submission;
- no Shopify API, App Pricing, App Events, or billing provider call;
- no new route or server action;
- no database or shared-contract change;
- no changes to plan economics or displayed monetary source of truth;
- no redesign of unrelated onboarding sections.

## Acceptance Criteria

- [ ] Onboarding renders distinct recovery top-up and plan-upgrade mock sections.
- [ ] Top-up selection and pending confirmation work entirely in local UI state.
- [ ] Plan selection and Shopify-hosted pricing CTA work entirely in local UI state.
- [ ] The UI does not claim that local mock actions completed billing.
- [ ] New copy is catalogued through the existing merchant i18n implementation in
      every declared locale.
- [ ] Controls are keyboard accessible, labelled, and responsive on mobile.
- [ ] Focused tests or source-level tests prove the mock controls and the absence
      of direct billing/provider calls.
- [ ] Shop resolution does not reset an existing shop to `ACTIVE`.
- [ ] Only the explicit installation lifecycle path reactivates an uninstalled
  shop; suspended shops remain suspended.
- [ ] Focused shop lifecycle tests cover the status transitions and preservation
  rules above.
- [ ] Access-policy checks receive route/capability context and an explicit
  redirect destination.
- [ ] Suspended operational denials redirect to merchant support instead of
  returning a raw forbidden response.
- [ ] Uninstalled support denials redirect to the login/start flow.
- [ ] Incomplete first-install onboarding still redirects to `/app/billing`.
- [ ] Merchant-support UI strings are rendered through the merchant i18n
  runtime, with no hard-coded merchant-visible English copy.
- [ ] Merchant-support locale keys exist in every declared locale and preserve
  the required ICU placeholders.
- [ ] Merchant-support i18n tests validate catalogue completeness and the
  localized page/action states.

## Validation

Run the repository commands that exist for the changed surface, at minimum:

```bash
npm test
npm run typecheck
npm run build
git diff --check
```

Record any pre-existing failures separately from task regressions. Do not publish
the package or modify production/shared environments.

## Stop

When the implementation and validation are complete, use
`/moda_developer_update ARCH-008-SHOPIFY-003` for reconciliation and review.

## Completion Report

### Status
Changes Requested — Attempt 1

### Files Changed
- Implementation branch commit `d265060` changes 44 files, including the new dashboard billing components, 20 locale catalogues, billing routes, shop lifecycle/access-policy code, and related tests.
- The implementation worktree also contains uncommitted changes to `app/i18n/locales/zh-Hant.json`, `app/routes/app/merchant-support/route.jsx`, `.vscode/`, and `merge-locales.sh`; these were not modified or discarded during review.

### Work Completed
- The published implementation adds a dashboard billing/options surface and locale keys, plus partial shop lifecycle and access-policy changes.
- It does not yet implement the required onboarding prototype or the complete interaction/access/i18n contract.

### Validation Results
- `npm test`: 216 passed, 1 skipped.
- `npm run build`: passed.
- `git diff --check`: passed.
- `npm run typecheck`: failed with 175 diagnostics, including errors in each new billing prototype component, billing options route, merchant-support route, shop service, and related tests.

### Deviations
- The implementation is materially broader than the declared prototype scope and places the UI in `app/components/dashboard` and `/app/billing/options` while leaving `app/components/onboarding/Onboarding.jsx` unchanged.

### Assumptions
- None accepted for this review; the required onboarding integration and task-surface type safety remain unresolved.

### Unresolved Issues
- See Developer Self-Review - Changes Requested below.

### Architectural Concerns
- The task currently mixes a mock billing surface with production billing-route and merchant-support changes without proving the required no-network/local-state boundary.

### Architect Review

#### Review Status
Changes Requested

#### Review Notes
- See Developer Self-Review - Changes Requested below.

#### Reviewed Files
None

#### Validation Reviewed
- Full tests, build, diff check, and typecheck were run in the canonical implementation worktree.

#### Architecture Conformance
Changes Requested

#### Follow-up
The developer must address the explicit corrections below and re-run the required validation before the next reconciliation.

## Developer Self-Review - Changes Requested

### Blocking Corrections

1. Implement the prototype in the existing onboarding experience required by the task. `app/components/onboarding/Onboarding.jsx` is unchanged, and no onboarding stylesheet or focused onboarding tests were added. The rendered onboarding flow must contain distinct recovery top-up and plan-upgrade sections.
2. Make top-up interaction local and demonstrable: add a bounded pack selector or equivalent selection state, show the selected quantity, and transition to a translated pending-confirmation state after the mock action. Do not rely only on an optional parent callback or console logging.
3. Make plan selection local and Shopify-hosted: expose at least two higher plans, allow selecting a higher plan, and provide a CTA that clearly continues to the existing Shopify-hosted pricing flow. Do not present downgrade actions as part of this upgrade prototype, and do not imply that the app directly approves or charges the plan.
4. Add focused component/source tests proving the two mock controls, local pending/selection state, accessibility labels/focusable controls, absence of network/provider/billing calls, and the hosted-pricing CTA. Existing tests do not exercise the new dashboard components.
5. Resolve all typecheck errors introduced by the task surface. The current run reports 175 diagnostics, including implicit-any/invalid inferred-prop errors in `BillingPurchaseHub.jsx`, `TopUpPurchasePanel.jsx`, `SubscriptionChangePanel.jsx`, `app/routes/app/billing/options/route.tsx`, `app/routes/app/merchant-support/route.jsx`, `shop.service.ts`, and the new policy/service tests. At minimum, the changed files must not add diagnostics relative to a synchronized baseline.
6. Complete the shop lifecycle contract with tests for new-shop creation, repeated resolution, suspended preservation, explicit uninstalled reactivation, and duplicate installation handling. The current `markInstalled` tests only assert the `UNINSTALLED` filter and do not prove the returned/persisted lifecycle state.
7. Make access-policy context meaningful and cover the actual route behavior. Tests must prove route and capability are passed to the policy, suspended operational access redirects to `/app/merchant-support`, uninstalled support access redirects to `/auth/login`, and incomplete first-install onboarding still redirects to `/app/billing`. The app shell currently resolves a shop and reads support data without an access-policy check.
8. Finish merchant-support localization behavior: generic action failures must render catalogue keys rather than raw `fetcher.data.error` text, all declared locales must have the complete key set with placeholder parity, and focused tests must cover localized page/action states. Correct the `session.userId` type error while doing so.

### Required State Transition

This review does not increment the attempt. The task remains Attempt 1 and is returned to `ready` for the developer to continue on the same task branches.