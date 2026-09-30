---
id: ARCH-023-SHOPIFY-003
architecture_id: ARCH-023
title: Activate initial pending Store Category after authoritative subscription activation
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 51
executor: copilot
claimed_at: 2026-09-30T19:07:21Z
attempt: 1
depends_on:
  - ARCH-023-SHOPIFY-001
  - ARCH-023-SHOPIFY-002
enables: []
created: 2026-09-29
updated: 2026-09-30
---

# Activate initial pending Store Category after authoritative subscription activation

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Activate the initial pending Store Category only after Moda has durably established that the shop's **current** Subscription is `ACTIVE` or `TRIALING` with a current `planId`.

The plan-selection return/configure signal is not itself activation authority. If the synchronous Shopify-side path observes and commits an active/trialing subscription, it may invoke the activation immediately. If subscription activation is established later by the existing Background billing reconciler, that Background path must invoke the same idempotent activation contract in a separate bounded task.

This task has **no Merchant Knowledge activation behaviour**. Subscription activation only makes plan-backed Merchant Knowledge configuration available; explicit merchant opt-in is owned by SHOPIFY-004/ADMIN-004 and later Background/Commerce follow-ups.

## Context

A `CommerceShopProfile` with:

```text
activeCategoryId = null
pendingCategoryId != null
pendingPromptRevisionId != null
```

represents initial onboarding category state.

Receiving a plan handle, welcome/configure return, or marking onboarding complete does not prove the subscription is active. The only activation gate is the durable current Subscription projection.

After initial activation, any later pending category is a post-onboarding change and must wait for Admin publication.

## Scope

Primary authorized implementation surface:

```text
app/services/store-profile/commerce-environment.server.ts
app/services/store-profile/store-category-activation.server.ts

app/routes/app/billing/callback/route.tsx   # only where this existing path actually commits ACTIVE/TRIALING

existing subscription-sync integration point in moda-interact, if required

tests/unit/store-category-activation.test.ts
tests/unit/routes/billing-callback.test.ts
tests/integration/store-category-activation.integration.test.ts
```

Do not create a new subscription webhook or a second subscription reconciler.

## Out of Scope

- Background subscription-reconciliation fallback implementation.
- later category-change Admin publication.
- Store Category selection.
- plan materialisation logic except consuming the existing durable projection.
- Merchant Knowledge activation, source processing or queue publication.
- Commerce runtime prompt composition.

## Requirements

### R1 — exact environment mapping

Create `resolveShopifyCommerceEnvironment(): CommerceEnvironment` using existing `resolveDeploymentEnvironmentName()` and map exactly:

```text
local -> LOCAL
test -> TEST
development -> DEVELOPMENT
staging -> STAGING
production -> PRODUCTION
```

Unknown values throw `Commerce environment is unavailable.`

### R2 — idempotent activation entrypoint

Create:

```ts
activateInitialPendingStoreCategoryIfEligible({
  shopId,
  expectedPendingSelectionGeneration?,
}): Promise<
  | { kind: "ACTIVATED"; categoryId: string; promptRevisionId: string }
  | { kind: "ALREADY_ACTIVE" }
  | { kind: "NO_PENDING" }
  | { kind: "SUBSCRIPTION_NOT_ACTIVE" }
>
```

### R3 — exact transaction eligibility

In one transaction:

1. lock Shop/CommerceShopProfile scope for `shopId`;
2. load the current Subscription;
3. require `status IN (ACTIVE, TRIALING)` and `planId != null`;
4. no profile -> `NO_PENDING`;
5. `activeCategoryId != null` -> `ALREADY_ACTIVE`;
6. require `pendingCategoryId`, `pendingPromptRevisionId`, `pendingSelectedAt`;
7. if expected generation is supplied, require exact equality;
8. load the pending category and exact pending revision;
9. require DRAFT, SHOP scope, same shop, non-null template provenance;
10. require the revision's `sourceTemplateId` matches the selected category's pinned default-template identity;
11. never re-read current template text.

Structural inconsistency throws bounded `STORE_CATEGORY_PENDING_STATE_CONFLICT` and rolls back.

### R4 — publish the exact pending DRAFT

Use one transaction timestamp and lowercase SHA-256 of exact UTF-8 `promptText`. Require non-empty trimmed text. Publish the existing revision only; do not create a replacement.

### R5 — set current Shop prompt atomically

Resolve current Commerce environment, find/create the one SHOP `CommerceAgentConfiguration`, set `activePromptRevisionId`, increment `promptEditVersion`, and preserve existing `modelId` / `modelEditVersion`.

### R6 — promote profile atomically

In the same transaction:

```text
activeCategoryId          = pendingCategoryId
activeCategoryActivatedAt = now
pendingCategoryId         = null
pendingPromptRevisionId   = null
pendingSelectedAt         = null
```

Preserve `pendingSelectionGeneration`.

### R7 — later changes never auto-activate

If `activeCategoryId != null`, return `ALREADY_ACTIVE` even when another pending category exists.

### R8 — integrate only after durable subscription activation

The Shopify-side integration may call R2 only **after** the existing billing/subscription synchronization path has committed:

```text
Subscription.status IN (ACTIVE, TRIALING)
Subscription.planId != null
```

Do not call merely because a plan handle/configure/welcome return was received. If that return records onboarding/plan intent but the durable subscription is not yet active, leave Store Category pending and let the existing Background billing reconciliation path establish subscription state later.

Category activation failure must not roll back an already-committed billing projection.

### R9 — onboarding milestone is separate

Preserve existing `ShopSettings.onboardingCompleted` semantics. It is neither proof of subscription activation nor the category activation gate.

### R10 — idempotency

Repeated invocation after successful activation returns `ALREADY_ACTIVE`, does not republish, does not increment versions again, and never clears a later post-onboarding pending category.

### R11 — audit

Use existing authorised Commerce audit helpers if available. Do not invent a PlatformAdmin/system actor solely for this task; record any audit-actor gap for architect follow-up.

### R12 — tests

Prove at minimum:

```text
plan/configure/welcome signal without durable ACTIVE/TRIALING -> no activation
NO_CONTRACT -> no activation
ACTIVE -> exact pending DRAFT activates
TRIALING -> exact pending DRAFT activates
activeCategoryId already set -> later pending remains untouched
current template edits after selection do not alter pinned prompt
configuration pointer + publication + profile promotion are atomic
mid-transaction failure rolls all three back
repeated activation is idempotent
billing projection remains committed if category activation fails afterward
no Merchant Knowledge preference/source/queue state is mutated
```

## Work Items

- [ ] Add exact environment mapper.
- [ ] Implement idempotent initial activation transaction.
- [ ] Integrate only after an authoritative durable Shopify-side subscription activation commit.
- [ ] Preserve later-category Admin boundary.
- [ ] Add transaction/idempotency/subscription-gate tests.
- [ ] Record the existing Background billing-reconciliation fallback as a separate unresolved implementation boundary if still absent.

## Interfaces / Contracts

Consumes SHOPIFY-002 pending state, current Subscription projection and Commerce prompt/configuration tables.

## Dependencies

- `ARCH-023-SHOPIFY-001`
- `ARCH-023-SHOPIFY-002`

## Acceptance Criteria

- [ ] Only durable current ACTIVE/TRIALING subscription state can activate the initial category.
- [ ] Initial category/prompt activation is exact, atomic and idempotent.
- [ ] Later category changes remain Admin-owned.
- [ ] No plan-handle/onboarding signal is treated as subscription-active authority.
- [ ] No Merchant Knowledge activation or processing is coupled to subscription activation.

## Validation

- [ ] focused activation tests
- [ ] billing/subscription integration regressions
- [ ] transaction integration test
- [ ] `npm run typecheck`
- [ ] changed-file lint/diagnostics
- [ ] `npm run build`
- [ ] `git diff --check`

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

## Completion Report

### Status
Not Started
### Files Changed
None.
### Work Completed
None.
### Validation Results
None.
### Deviations
None.
### Assumptions
None.
### Unresolved Issues
None.
### Architectural Concerns
None.

## Architect Review

### Review Status
Pending
### Review Notes
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
