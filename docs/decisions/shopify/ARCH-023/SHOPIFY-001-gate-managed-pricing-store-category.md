---
id: ARCH-023-SHOPIFY-001
architecture_id: ARCH-023
title: Gate Managed Pricing with Store Category selection
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-002
  - ARCH-023-SHARED-004
enables:
  - ARCH-023-SHOPIFY-002
  - ARCH-023-SYSTEM-TEST-001
created: 2026-09-27
updated: 2026-09-27
---

# Gate Managed Pricing with Store Category selection

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Insert the Store Category confirmation step before the first Shopify Managed Pricing redirect, preselecting from Shopify taxonomy evidence and persisting only pending Commerce profile state.

## Context

`/app/billing/select` currently redirects directly to Shopify Managed Pricing. The merchant must preview/confirm the category default Shop Instructions before leaving Moda, but nothing becomes active until subscription projection is `ACTIVE` or `TRIALING`.

## Scope

- Load enabled/ready Store Categories and localized default-template previews for the shop default language with English fallback.
- Read bounded Shopify product-taxonomy evidence available through the app and deterministically preselect the mapped category or configured fallback category.
- Allow merchant override before continue.
- Persist pending category, exact template id/edit version, resolved language and selection timestamp in `CommerceShopProfile`.
- Redirect to existing Shopify Managed Pricing only after pending persistence succeeds.
- Restore a previously pending choice when the merchant returns without activating a plan.

## Out of Scope

- Activating the category/prompt.
- Changing Shopify billing callback/subscription semantics.
- Later post-onboarding category changes.

## Requirements

- Suggestion is advisory; merchant can always choose another enabled/ready category.
- The exact template edit version/language previewed is pinned before redirect.
- No active category or Shop prompt is created by this route.
- `onboardingCompleted` is not treated as activation authority.
- If shop locale is missing/unsupported, use English.

## Work Items

- [ ] Add category-gate route/component and server loader/action.
- [ ] Add taxonomy mapping/suggestion adapter.
- [ ] Replace direct first-time Managed Pricing redirect with category gate while preserving existing billing route/auth.
- [ ] Add abandon/return/pending-state tests.

## Interfaces / Contracts

Consumes ARCH-023-DATABASE-002 and Shared locale/profile contracts. Background activation is owned by ARCH-023-BACKGROUND-002.

## Dependencies

- ARCH-023-DATABASE-002
- ARCH-023-SHARED-004

## Enables

- ARCH-023-SHOPIFY-002
- ARCH-023-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Shopify-derived category is preselected but editable.
- [ ] Pending state survives leaving/returning from Shopify Managed Pricing without activating.
- [ ] No category/prompt becomes active before durable subscription projection.

## Validation

- [ ] Focused route/service/component tests.
- [ ] Existing billing-selection/callback regression tests.
- [ ] Lint/typecheck/build as declared.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

None

## Completion Report

### Status

Not Started

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

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None
