---
id: ARCH-010-BACKGROUND-020
architecture_id: ARCH-010
title: Remove pre-publication Background consumers of retired Shared billing contracts
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 5
executor: copilot
claimed_at: 2026-09-12T14:49:17Z
attempt: 1
depends_on:
  - ARCH-010-SHARED-006
enables:
  - ARCH-010-SHARED-007
created: 2026-09-12
updated: 2026-09-12
---

# ARCH-010-BACKGROUND-020: Remove pre-publication Background consumers of retired Shared billing contracts

## Architecture

Read first:

```text
docs/architecture/ARCH-010-first-production-baseline.md
docs/architecture/ARCH-010-supersession-map.md
docs/decisions/shared/ARCH-010/ARCHITECT-COORDINATION-NOTE-SHARED-007-consumer-sequencing.md
```

This is a pre-publication consumer cleanup task. It executes against the already
published:

```text
@modainteract/moda-interact-shared@0.10.0
```

It exists only to remove Background consumers that currently prevent SHARED-007 from
making the breaking first-production Shared cleanup.

## Objective

Make `moda-interact-background` compile and test without any runtime/test dependency on
the Shared contracts that SHARED-007 will remove.

The task does **not** implement the later ARCH-010 cancellation reconciliation or full
capacity-resume feature. It only removes superseded pre-production consumers.

## Known blocking consumers

Start with these exact files from the SHARED-007 blocked run:

```text
src/services/subscription-cancellation.service.ts
src/providers/shopify-partner-billing.provider.ts
tests/unit/services/recovery-billing.service.test.ts
```

Before editing, search the entire Background source/tests for:

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
appSubscriptionCancel
```

Record the exact matches in the Completion Report.

## Required behaviour

### 1. Remove the local cancellation executor

ARCH-010 cancellation is Shopify-authoritative observation/reconciliation. Background
must not execute a local Shopify cancellation mutation.

Remove the obsolete local execution path, including all imports/types/mappings whose
only purpose is:

```text
SubscriptionCancellationMode
SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS
appSubscriptionCancel
```

Deterministic rule:

```text
if subscription-cancellation.service.ts exists only to execute the ARCH-009 local
cancellation request/approval workflow:
    delete the service and its focused tests/registration/imports
else:
    remove only the local mutation capability and retain unrelated behaviour
```

In `shopify-partner-billing.provider.ts`:

```text
retain:
  provider subscription reads/reconciliation support
  getActiveSubscription and other ARCH-010 read behaviour

remove:
  cancellation-mode mapping imports
  appSubscriptionCancel mutation wrapper
  any method used only by the superseded local cancellation executor
```

Do not replace the mutation with a differently named local cancellation method.

### 2. Remove Background use of obsolete cancellation message codes

After cleanup, Background source/tests must contain zero active use of:

```text
BILLING_CANCELLATION_REQUEST_RECEIVED
BILLING_CANCELLATION_COMPLETED
BILLING_CANCELLATION_REJECTED
```

Do not replace them with new local-cancellation messages.

Later provider-authoritative cancellation state belongs to
`ARCH-010-BACKGROUND-012`.

### 3. Remove the Free-only exhaustion consumer

Replace/remove Background branches and tests that require:

```text
BILLING_FREE_ALLOWANCE_EXHAUSTED
```

For any current full-capacity exhaustion message producer that still needs to emit a
code, use the already-published canonical code:

```text
BILLING_RECOVERY_CAPACITY_EXHAUSTED
```

Do not implement the broader blocked-recovery persistence/resume semantics owned by:

```text
ARCH-010-BACKGROUND-009
```

This task only eliminates the old Shared symbol dependency.

### 4. Preserve unrelated ARCH-010 contracts

Do not change semantics for:

```text
BILLING_RECOVERY_CAPACITY_EXHAUSTED
BILLING_REFUND_REQUEST_RECEIVED
BILLING_REFUND_COMPLETED
BILLING_REFUND_REJECTED
billing-subscription-reconcile queue contract
provider subscription read/reconciliation behaviour
purchased-credit or promotion accounting
```

### 5. Zero-consumer stop gate

Before returning to review, run a repository-wide source/test search.

The following must have **zero** Background matches:

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
appSubscriptionCancel
```

Matches inside immutable ARCH-009 documentation are irrelevant; this task's zero-match
gate is for `moda-interact-background` source/tests.

If a remaining runtime consumer cannot be removed without implementing a different
ARCH-010 feature task, STOP and return to `moda_architect` with the exact file/symbol.
Do not add a compatibility wrapper.

## Out of Scope

Do not:

- edit `moda-interact-shared`;
- publish or change a Shared package version;
- update to unpublished Shared `0.11.0`;
- implement BACKGROUND-009 blocked recovery resume;
- implement BACKGROUND-012 provider-authoritative cancellation reconciliation;
- implement plan upgrades/downgrades;
- change database schema or historical migrations;
- stage/change the database gitlink;
- add Admin/Shopify UI work.

## Required tests

At minimum prove:

```text
1. no local cancellation executor calls Shopify appSubscriptionCancel;
2. provider subscription read behaviour still works after mutation removal;
3. recovery billing no longer emits/expects BILLING_FREE_ALLOWANCE_EXHAUSTED;
4. any retained full-capacity message path uses BILLING_RECOVERY_CAPACITY_EXHAUSTED;
5. refund/reconciliation contracts remain unaffected.
```

Delete tests whose only purpose was to assert the removed ARCH-009 local cancellation
workflow.

Do not create tests for BACKGROUND-012/BACKGROUND-009 behaviour that this task does not
implement.

## Validation

Inspect `package.json` and run the repository-declared equivalents of:

```text
focused tests covering changed cancellation/provider/recovery-billing files
npm test
npm run typecheck
npm run build
git diff --check
```

Run `npm run prisma:validate` only if it is a declared Background validation script
used by the repository/task baseline.

Record exact pass/fail totals and every unchanged documented baseline condition.

## Completion Report requirements

Record:

```text
exact source/test files changed/deleted
pre-edit symbol matches
post-edit zero-match evidence
focused/full validation totals
implementation commit
parent claim/report commits
canonical parent + implementation worktrees
all isolation/synchronization evidence
Shared package version used: 0.10.0
database gitlink staged: no
```

## Stop condition

When the zero-consumer gate and validation pass:

```text
status -> review
return control to moda_architect
STOP
```

Do not begin SHARED-007 yourself.

## Completion Report

### Status

In Progress
