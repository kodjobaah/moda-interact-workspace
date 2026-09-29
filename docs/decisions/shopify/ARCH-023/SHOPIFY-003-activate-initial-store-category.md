---
id: ARCH-023-SHOPIFY-003
architecture_id: ARCH-023
title: Activate initial pending Store Category after verified subscription
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 51
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-SHOPIFY-001
  - ARCH-023-SHOPIFY-002
enables: []
created: 2026-09-29
updated: 2026-09-29
---

# Activate initial pending Store Category after verified subscription

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Implement the Shopify billing-callback **happy path** for initial Store Category activation.

Once the shop's durable current Subscription is verified `ACTIVE` or `TRIALING`, publish the exact pending Shop prompt DRAFT, make it the current environment's Shop prompt, activate the pending category and clear pending profile fields in one transaction.

Later post-onboarding category changes are not auto-activated; Admin publication owns those.

## Context

A `CommerceShopProfile` with:

```text
activeCategoryId = null
pendingCategoryId != null
pendingPromptRevisionId != null
```

represents initial onboarding category state.

After initial activation:

```text
activeCategoryId != null
```

therefore any later pending category is a post-onboarding change and must wait for Admin publication.

This task implements the billing callback path only. ARCH-023 also requires the existing Background subscription reconciler to perform the same idempotent activation when the callback is missed. That Background hook must be defined separately before ARCH-023 integrated completion.

## Scope

Primary authorized implementation surface:

```text
app/services/store-profile/commerce-environment.server.ts
app/services/store-profile/store-category-activation.server.ts

app/routes/app/billing/callback/route.tsx

tests/unit/store-category-activation.test.ts
tests/unit/routes/billing-callback.test.ts
tests/integration/store-category-activation.integration.test.ts
```

## Out of Scope

- Background subscription-reconciliation fallback.
- later category-change Admin publication.
- Store Category selection.
- plan materialisation logic except calling existing billing projection.
- Merchant Knowledge sources.
- Commerce runtime prompt composition.

## Requirements

### R1 — exact environment mapping

Create:

```ts
resolveShopifyCommerceEnvironment(): CommerceEnvironment
```

using existing `resolveDeploymentEnvironmentName()`.

Map exactly:

```text
local       -> LOCAL
test        -> TEST
development -> DEVELOPMENT
staging     -> STAGING
production  -> PRODUCTION
```

Unknown value throws:

```text
Commerce environment is unavailable.
```

Do not default an unknown deployment environment.

### R2 — activation entrypoint

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

This is a Shopify-repository internal service.

### R3 — exact transaction eligibility

In one transaction:

1. lock Shop/CommerceShopProfile scope for `shopId`;
2. load current Subscription;
3. require:
   ```text
   status IN (ACTIVE, TRIALING)
   planId != null
   ```
4. load/create? No: if no `CommerceShopProfile`, return `NO_PENDING`;
5. if `activeCategoryId != null`, return `ALREADY_ACTIVE`;
6. require all pending fields non-null:
   ```text
   pendingCategoryId
   pendingPromptRevisionId
   pendingSelectedAt
   ```
   otherwise return `NO_PENDING`;
7. if optional expected generation supplied, require exact equality;
8. load pending category and exact pending revision;
9. require revision:
   ```text
   status = DRAFT
   prompt.scope = SHOP
   prompt.shopId = shopId
   sourceTemplateId != null
   sourceTemplateEditVersion != null
   ```
10. require `revision.sourceTemplateId` equals the selected category's persisted `defaultTemplateId` identity expected by the pending selection contract;
11. do not re-read/copy current template `promptText`.

If any structural invariant is inconsistent, throw bounded `STORE_CATEGORY_PENDING_STATE_CONFLICT` and roll back.

### R4 — publish exact pending DRAFT

Calculate:

```text
contentHash = lowercase SHA-256(exact UTF-8 revision.promptText)
now = one transaction timestamp
```

Require `promptText.trim()` non-empty.

Publish exactly:

```text
revision.status      = PUBLISHED
revision.contentHash = contentHash
revision.publishedAt = now
revision.editVersion = editVersion + 1
```

Do not create another revision.

### R5 — set the current Shop prompt pointer atomically

Resolve current Commerce environment from R1.

Find exact `CommerceAgentConfiguration` for:

```text
environment = current
scope       = SHOP
shopId      = shopId
```

If absent, create it using existing required defaults/model fields according to current Commerce configuration conventions. Do not invent a second configuration row.

Set:

```text
activePromptRevisionId = published pending revision.id
promptEditVersion       = previous + 1
```

Preserve:

```text
modelId
modelEditVersion
```

when configuration already exists.

### R6 — promote profile atomically

In the same transaction:

```text
activeCategoryId          = pendingCategoryId
activeCategoryActivatedAt = now

pendingCategoryId       = null
pendingPromptRevisionId = null
pendingSelectedAt       = null
```

Preserve:

```text
pendingSelectionGeneration
```

Do not reset it.

Commit only after R4-R6 all succeed.

### R7 — do not auto-activate later changes

If:

```text
profile.activeCategoryId != null
```

this service returns `ALREADY_ACTIVE` even if a new `pendingCategoryId` exists.

That later pending category remains for Admin review/publication.

### R8 — integrate after durable subscription verification

In `app/routes/app/billing/callback/route.tsx`, call R2 only after the callback path has durable current Subscription status:

```text
ACTIVE
or
TRIALING
```

and a current `planId`.

Call after the billing service has committed the verified projection.

The category activation failure must not roll back the already-verified billing projection. Surface/log a bounded failure and leave pending state intact for reconciliation repair.

Do not call merely because a request contains `plan_handle`.

### R9 — onboarding milestone

Preserve existing `ShopSettings.onboardingCompleted` semantics.

Category activation and onboardingCompleted are distinct durable facts.

Do not use `onboardingCompleted` as the activation gate.

### R10 — idempotency

Repeated callback:

- after successful activation -> `ALREADY_ACTIVE`;
- must not publish again;
- must not increment prompt/config/profile versions again;
- must not clear a later post-onboarding pending category.

### R11 — audit

If Shopify app already writes Commerce audit events through an established helper, use:

```text
PUBLISH_AGENT_PROMPT_REVISION
SET_AGENT_PROMPT
```

for the system activation with bounded metadata:

```json
{"changeKind":"INITIAL_STORE_CATEGORY_ACTIVATION"}
```

If the repository has no authorized system actor/audit helper, do not invent a PlatformAdmin. Record the gap in Completion Report for architect follow-up rather than faking an actor.

### R12 — tests

Prove:

```text
NO_CONTRACT does not activate
ACTIVE activates exact pending DRAFT
TRIALING activates exact pending DRAFT
activeCategoryId already set -> no-op even if later pending exists
content hash exact UTF-8
prompt/template provenance preserved
current template edits after selection do not change published prompt
configuration pointer + prompt publication + profile promotion are atomic
failure midway rolls all three back
repeated callback idempotent
billing projection remains committed if category activation fails afterward
arbitrary plan_handle request without verified subscription does not activate
```

## Work Items

- [ ] Add exact environment mapper.
- [ ] Implement idempotent initial activation transaction.
- [ ] Integrate after verified billing callback projection.
- [ ] Preserve later-category Admin boundary.
- [ ] Add transaction/idempotency/callback tests.
- [ ] Record Background fallback as unresolved dependency if not yet materialised.

## Interfaces / Contracts

Consumes:

```text
CommerceShopProfile pending state from SHOPIFY-002
current Subscription projection
Commerce prompt/configuration tables
```

No new cross-repository contract.

## Dependencies

- `ARCH-023-SHOPIFY-001`
- `ARCH-023-SHOPIFY-002`

## Enables

No terminal architecture validation task yet. The required Background subscription-reconciliation fallback must also exist before system acceptance.

## Acceptance Criteria

- [ ] Initial verified subscription activates exact pending category/prompt atomically.
- [ ] Later category changes are never auto-activated.
- [ ] Callback is idempotent.
- [ ] No current template re-read changes pinned prompt text.
- [ ] Billing state cannot be rolled back by a category activation failure.
- [ ] Reconciliation fallback requirement is explicitly handed back to architect if not yet implemented.

## Validation

- [ ] focused activation tests
- [ ] billing callback regressions
- [ ] transaction integration test
- [ ] `npm run typecheck`
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

Do not implement the Background reconciliation hook inside the Shopify repository.

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
