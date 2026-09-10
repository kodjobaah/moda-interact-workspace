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
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-09-10T10:31:10Z
attempt: 1
depends_on:
  - ARCH-007-SHOPIFY-002
enables: []
created: 2026-09-10
updated: 2026-09-10
---

# ARCH-008-SHOPIFY-003: Add mock UI components for recovery top-ups and plan upgrades

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

## Scope

Modify only the `moda-interact` repository surfaces needed for this prototype:

- `app/components/onboarding/Onboarding.jsx`;
- `app/components/onboarding/Onboarding.css`;
- the existing merchant locale catalogues for new copy;
- focused onboarding component/source tests, if the repository has an applicable
  test surface.

Do not change billing services, routes, database schemas, Shopify provider code,
shared packages, or the package/export architecture.

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
In Progress

### Files Changed
None

### Work Completed
None

### Validation Results
None

### Deviations
None

### Assumptions
None

### Unresolved Issues
None

### Architectural Concerns
None

### Architect Review

#### Review Status
Pending

#### Review Notes
None

#### Reviewed Files
None

#### Validation Reviewed
None

#### Architecture Conformance
Pending

#### Follow-up
None