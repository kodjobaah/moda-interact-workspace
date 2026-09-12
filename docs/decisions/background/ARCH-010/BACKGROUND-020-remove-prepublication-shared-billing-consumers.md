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
status: complete
priority: 5
executor: null
claimed_at: null
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

Ready for Review

### Files Changed

- `src/entrypoints/billing.ts`: removed the obsolete cancellation executor import and billing-cycle invocation.
- `src/providers/shopify-partner-billing.provider.ts`: retained subscription reads and removed the local cancellation mutation, mapping and provider contract.
- `src/services/recovery-billing.service.ts`: replaced `BILLING_FREE_ALLOWANCE_EXHAUSTED` with `BILLING_RECOVERY_CAPACITY_EXHAUSTED` and updated its deterministic exhaustion source key/body.
- `tests/unit/providers/shopify-partner-billing.provider.test.ts`: removed mutation-specific tests while retaining provider read coverage.
- `tests/unit/services/recovery-billing.service.test.ts`: updated exhaustion assertions to the canonical capacity code/source key.
- `src/services/subscription-cancellation.service.ts`: deleted the obsolete local cancellation executor.
- `tests/unit/services/subscription-cancellation.service.test.ts`: deleted tests whose only purpose was the removed executor workflow.

### Work Completed

Removed all pre-publication Background consumers of the retired Shared billing contracts while consuming the published `@modainteract/moda-interact-shared@0.10.0` package. The billing worker no longer schedules local cancellation execution, the Shopify Partner provider has no cancellation mutation method, and provider subscription reconciliation reads remain intact. Free exhaustion now uses the canonical generic recovery-capacity message contract. No Shared, database schema, migration, queue contract, BACKGROUND-009, BACKGROUND-012, or UI files were changed.

### Pre-edit Symbol Matches

The required pre-edit search matched:

- `src/services/subscription-cancellation.service.ts`: `SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS`, `SubscriptionCancellationMode`, and `cancelSubscription`.
- `src/providers/shopify-partner-billing.provider.ts`: `SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS`, `SubscriptionCancellationMode`, `appSubscriptionCancel`, and the cancellation mutation wrapper.
- `tests/unit/providers/shopify-partner-billing.provider.test.ts`: `appSubscriptionCancel` and `cancelSubscription` mutation/error tests.
- `tests/unit/services/recovery-billing.service.test.ts`: `BILLING_FREE_ALLOWANCE_EXHAUSTED` source-key assertions.

The pre-edit search found no active Background matches for `SUBSCRIPTION_CANCELLATION_MODES`, `SubscriptionCancellationModeSchema`, `ShopifySubscriptionCancellationArgs`, the three cancellation message codes, or `BILLING_PLAN_CHANGE_ACTION_REQUIRED`.

### Post-edit Zero-consumer Evidence

Repository-wide `rg` over `src` and `tests` returned zero matches for all eleven retired symbols/codes required by the task, including `appSubscriptionCancel` and `BILLING_FREE_ALLOWANCE_EXHAUSTED`.

### Validation Results

- Focused provider/recovery tests: **2 files, 16 passed**.
- Full `npm test`: **46 files passed, 5 skipped, 525 tests passed, 7 skipped**; 6 unchanged baseline failures remain. Four integration tests require the unavailable `moda_interact_test` database, and `tests/unit/runtime/observability-startup.test.ts` still expects Shared `0.9.0` while this task is required to use published Shared `0.10.0`.
- `npm run prisma:validate`: passed after initializing the recorded database submodule for local validation only.
- `npm run build`: Prisma generation passed; TypeScript compilation remains blocked by 8 unchanged nullable `counterId` errors in `src/services/free-recovery-reservation.service.ts` and `src/services/purchased-recovery-reservation.service.ts`. No changed task file is reported.
- `npm run typecheck`: unavailable because the repository declares no `typecheck` script; the build's `tsc` step was run instead.
- `git diff --check`: passed.
- Database gitlink: not changed or staged.

### Deviations

None. The full-suite and build failures are documented pre-existing repository baseline conditions outside this task's scope.

### Assumptions

The published Shared dependency remains `@modainteract/moda-interact-shared@0.10.0`, as required by the task and confirmed in `package.json` and `package-lock.json`.

### Unresolved Issues

The repository's unrelated full-suite database setup, stale Shared `0.9.0` observability assertion, and eight unrelated nullable `counterId` TypeScript diagnostics remain for their owning tasks/baseline. They do not affect the focused BACKGROUND-020 tests or zero-consumer gate.

### Architectural Concerns

None.

### Git / VCS

Task branch: `task/ARCH-010-BACKGROUND-020`

Physical worktree isolation:

- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-020`
- parent branch: `task/ARCH-010-BACKGROUND-020`
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-020`
- implementation branch: `task/ARCH-010-BACKGROUND-020`
- shared workspace checkout switched/mutated for task work: no
- shared implementation checkout switched/mutated for task work: no
- another task worktree reused: no

Start-of-attempt synchronization:

- parent remote task branch fast-forwarded: not-needed; branch did not exist
- parent `origin/main` incorporated: already-current at worktree creation
- implementation remote task branch fast-forwarded: not-needed; branch did not exist
- implementation `origin/main` incorporated: already-current at worktree creation

Implementation repository:

- repository: `moda-interact-background`
- commit: `3a1c78d376501377b7fab919c9e1ec8851f74d51`
- remote branch: `origin/task/ARCH-010-BACKGROUND-020`
- pushed: yes

Parent workspace:

- task file: `docs/decisions/background/ARCH-010/BACKGROUND-020-remove-prepublication-shared-billing-consumers.md`
- claim commit: `efcf03e`
- report commit: `3ca88e6cf0eccd23029c11e7d12b85137d9a9abe`
- final metadata correction commit: `6e89df9` (pushed)
- remote branch: `origin/task/ARCH-010-BACKGROUND-020`
- pushed: claim yes; report pending
- submodule gitlink staged: no

Merged to implementation main: no

Merged to workspace main: no

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Summary

`ARCH-010-BACKGROUND-020` satisfies the pre-publication consumer-cleanup contract.

Architect inspection confirms the Background repository now has zero active source/test
matches for every retired Shared symbol/code in the task stop gate:

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

The obsolete local cancellation executor and its dedicated tests are deleted.

`ShopifyPartnerBillingProvider` is now read-only for this boundary and retains:

```text
getActiveSubscription(...)
```

with focused provider-read coverage. No replacement local cancellation mutation was
introduced.

`RecoveryBillingService` now uses the already-published canonical Shared registry value:

```text
BILLING_SYSTEM_MESSAGE_CODES.RECOVERY_CAPACITY_EXHAUSTED
```

for exhausted Free admission while preserving the existing deterministic exhaustion
lifecycle/source-key mechanism. This task does not add BACKGROUND-009 blocked-recovery
persistence/resume behaviour.

The implementation continues to consume:

```text
@modainteract/moda-interact-shared@0.10.0
```

as required for the pre-publication cleanup phase.

### Reviewed implementation boundary

Accepted changed/deleted files:

```text
src/entrypoints/billing.ts
src/providers/shopify-partner-billing.provider.ts
src/services/recovery-billing.service.ts
src/services/subscription-cancellation.service.ts                 [deleted]
tests/unit/providers/shopify-partner-billing.provider.test.ts
tests/unit/services/recovery-billing.service.test.ts
tests/unit/services/subscription-cancellation.service.test.ts      [deleted]
```

No Shared implementation, database schema/migration, queue contract, BACKGROUND-009,
BACKGROUND-012, Admin, Shopify UI or Render/infrastructure implementation is introduced
by this task.

### Required behaviour reviewed

Accepted:

1. local Background `appSubscriptionCancel` execution is removed;
2. provider subscription read/reconciliation support remains present;
3. obsolete cancellation message contracts have zero Background consumers;
4. `BILLING_FREE_ALLOWANCE_EXHAUSTED` has zero Background consumers;
5. retained full-capacity exhaustion uses
   `BILLING_RECOVERY_CAPACITY_EXHAUSTED`;
6. `BILLING_PLAN_CHANGE_ACTION_REQUIRED` still has no Background consumer;
7. no compatibility alias/wrapper was added.

The repository-wide full suite provides regression coverage for unrelated billing
reconciliation/refund behaviour; architect inspection found no task-scope change to
those contracts.

### Validation reviewed

Canonical worktree evidence records:

```text
focused provider/recovery tests:
  2 files
  16 passed

full npm test:
  46 files passed
  5 skipped
  525 tests passed
  7 skipped
  6 documented baseline failures

npm run prisma:validate:
  passed

npm run build:
  Prisma generation passed
  TypeScript remains blocked only by 8 unchanged nullable-counterId diagnostics in:
    src/services/free-recovery-reservation.service.ts
    src/services/purchased-recovery-reservation.service.ts

npm run typecheck:
  no repository script exists; build's tsc step is the available compiler validation

git diff --check:
  passed
```

The six full-suite failures are the documented unavailable integration database /
stale observability-baseline conditions reported by the task and are not introduced by
the changed cleanup files.

The portable review archive intentionally has no installed `node_modules`, so
architect-side Vitest rerun is unavailable. Source/test inspection is consistent with
the canonical-worktree results above.

### Git / VCS reviewed

Implementation commit supplied and recorded:

```text
3a1c78d376501377b7fab919c9e1ec8851f74d51
```

The task archive records the canonical dedicated parent/implementation worktrees, all
three physical-isolation declarations and all four start-of-attempt synchronization
outcomes.

The review handoff identifies the latest pushed parent report publication as:

```text
40477d6
```

This supersedes earlier intermediate parent report/metadata hashes present in the
portable task snapshot and is recorded here as the current review evidence.

Database gitlink:

```text
changed: no
staged: no
```

Main branches:

```text
implementation main modified: no
workspace main modified: no
```

### Architecture conformance

Conformant.

This task removes first-party consumers while Shared `0.10.0` still exports the retired
symbols. It does not retain compatibility and does not prematurely implement the later
ARCH-010 cancellation or capacity-resume features.

### Dependency reconciliation

`ARCH-010-BACKGROUND-020` is now Complete and therefore satisfies one of the two
consumer-cleanup prerequisites for `ARCH-010-SHARED-007`.

`ARCH-010-SHARED-007` remains Blocked because:

```text
ARCH-010-SHOPIFY-024
```

is not yet Complete.

Do not transition SHARED-007 to Ready until SHOPIFY-024 has been architect-reviewed
and accepted.

### Architect Decision

**Accepted — Attempt 1.**

Because `completion_mode: automatic`, `ARCH-010-BACKGROUND-020` is now `complete`.
`attempt: 1` is preserved and the active executor/claim is cleared.
