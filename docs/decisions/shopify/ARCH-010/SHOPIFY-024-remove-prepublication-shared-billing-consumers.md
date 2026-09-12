---
id: ARCH-010-SHOPIFY-024
architecture_id: ARCH-010
title: Remove pre-publication Shopify consumers of retired Shared billing contracts
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-SHARED-006
  - ARCH-010-SHOPIFY-002
enables:
  - ARCH-010-SHARED-007
created: 2026-09-12
updated: 2026-09-12
---

# ARCH-010-SHOPIFY-024: Remove pre-publication Shopify consumers of retired Shared billing contracts

## Architecture

Read first:

```text
docs/architecture/ARCH-010-first-production-baseline.md
docs/architecture/ARCH-010-supersession-map.md
docs/decisions/shared/ARCH-010/ARCHITECT-COORDINATION-NOTE-SHARED-007-consumer-sequencing.md
```

This is a narrow pre-publication consumer cleanup task. It runs against published
Shared `0.10.0` so SHARED-007 can later remove obsolete symbols without breaking the
Shopify application.

## Objective

Remove the merchant-runtime/test dependency on the development-only:

```text
BILLING_FREE_ALLOWANCE_EXHAUSTED
```

contract and prove there is no other active Shopify consumer of the Shared contracts
scheduled for SHARED-007 removal.

## Known blocking consumer

The SHARED-007 blocked run identified:

```text
app/services/merchant-support/system-message-actions.ts
```

as an active `BILLING_FREE_ALLOWANCE_EXHAUSTED` consumer.

Inspect its focused tests and all merchant billing/system-message source/tests.

## Pre-edit search

Search `moda-interact` source/tests for:

```text
SUBSCRIPTION_CANCELLATION_MODES
SubscriptionCancellationModeSchema
SubscriptionCancellationMode
ShopifySubscriptionCancellationArgs
SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS
BILLING_CANCELLATION_REQUEST_RECEIVED
BILLING_CANCELLATION_COMPLETED
BILLING_CANCELLATION_REJECTED
BILLING_FREE_ALLOWANCE_EXHAUSTED
BILLING_PLAN_CHANGE_ACTION_REQUIRED
```

The SHARED-007 blocked run found no active `BILLING_PLAN_CHANGE_ACTION_REQUIRED`
consumer. Verify that negative result.

If an active cancellation or plan-change consumer is found that is not merely a test
fixture/documentation reference, STOP and return to `moda_architect` with the exact
file/symbol. Do not silently broaden this task.

## Required behaviour

### 1. Remove Free-only exhaustion action compatibility

Delete the `BILLING_FREE_ALLOWANCE_EXHAUSTED` action/renderer/route branch from:

```text
app/services/merchant-support/system-message-actions.ts
```

and update/delete focused tests that require that development-only code.

Do not preserve a deprecated alias or string-literal fallback.

### 2. Preserve canonical generic exhaustion behaviour

If the current Shopify runtime already handles:

```text
BILLING_RECOVERY_CAPACITY_EXHAUSTED
```

retain that behaviour unchanged.

If the generic presentation has not yet been implemented, do **not** implement
SHOPIFY-008 in this cleanup task. Simply remove the obsolete Free-only compatibility
branch. SHOPIFY-008 owns the complete merchant capacity-exhaustion presentation.

### 3. Preserve Shopify-hosted billing routes

Do not change accepted Shopify App Pricing navigation or:

```text
admin.shopify.com/.../pricing_plans
```

Do not introduce any merchant link to `moda-interact-admin`.

### 4. Zero-consumer gate

Before returning to review, Shopify source/tests must have zero match for:

```text
BILLING_FREE_ALLOWANCE_EXHAUSTED
```

The pre-edit search must also continue to show no active consumer for:

```text
BILLING_PLAN_CHANGE_ACTION_REQUIRED
```

and no active local cancellation-contract consumer.

This zero-match requirement excludes immutable architecture/task documentation; it
applies to `moda-interact` runtime source/tests.

## Out of Scope

Do not:

- edit or publish `moda-interact-shared`;
- update to unpublished Shared `0.11.0`;
- implement SHOPIFY-008 generic capacity UI;
- implement cancellation, upgrade/downgrade, refund or promotion features;
- reopen/change accepted SHOPIFY-002 behaviour;
- change database schema or stage/change the database gitlink;
- add Admin/Render work.

## Required tests

At minimum prove:

```text
1. merchant system-message action handling no longer contains the Free-only code;
2. existing unrelated system-message actions remain unchanged;
3. any existing generic recovery-capacity-exhausted handling still works;
4. Shopify-hosted pricing navigation remains valid;
5. no merchant action points to moda-interact-admin.
```

Use existing test surfaces; do not create a new application abstraction for this task.

## Validation

Inspect `package.json` and run the repository-declared equivalents of:

```text
focused merchant-support/system-message tests
npm test
npm run prisma:validate
npm run prisma:generate
npm run build
changed-file ESLint
npm run typecheck
git diff --check
```

Document known unrelated baseline diagnostics by existing baseline ID where available.
Any diagnostic in a changed SHOPIFY-024 file is a blocker.

## Completion Report requirements

Record:

```text
pre-edit symbol matches
post-edit zero-match evidence
exact files changed
focused/full validation totals
implementation commit
parent claim/report commits
canonical parent + implementation worktrees
all isolation/synchronization evidence
Shared package version used: 0.10.0
database gitlink staged: no
```

## Stop condition

When the obsolete Shopify consumer is gone and validation passes:

```text
status -> review
return control to moda_architect
STOP
```

Do not begin SHARED-007 or SHARED-008.
