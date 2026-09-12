---
id: ARCH-010-SHARED-007
architecture_id: ARCH-010
title: Remove superseded pre-production billing compatibility contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 6
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-010-SHARED-006
- ARCH-010-BACKGROUND-020
- ARCH-010-SHOPIFY-024
enables:
- ARCH-010-SHARED-008
created: 2026-09-12
updated: '2026-09-12'
---

# ARCH-010-SHARED-007: Remove superseded pre-production billing compatibility contracts

## Architecture

Read `docs/architecture/ARCH-010-first-production-baseline.md` and the ARCH-010 supersession map.

ARCH-010 is pre-production. Shared must publish only contracts that belong to the first-release architecture; it must not preserve ARCH-009 cancellation execution contracts merely because they were previously published.

## Objective

Remove Shared exports/system-message values whose only first-party purpose is superseded pre-production billing behaviour, including the local cancellation request/approval/`appSubscriptionCancel` workflow and the historical Free-only exhaustion code, while retaining the canonical ARCH-010 reconciliation, generic capacity-exhaustion and top-up-refund contracts.

## Context

ARCH-009 introduced a local cancellation execution contract including:

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
```

ARCH-010 cancellation is Shopify-authoritative observation/reconciliation, and full-capacity exhaustion uses the generic `BILLING_RECOVERY_CAPACITY_EXHAUSTED` code for both Free and Paid. None of the listed compatibility contracts belongs to first production.

`BILLING_PLAN_CHANGE_ACTION_REQUIRED` was also introduced for the superseded local plan-change request workflow. Current ARCH-010 plan changes use Shopify-hosted App Pricing and do not use that message contract. Remove it unless inspection proves an active ARCH-010 consumer exists; if such a consumer exists, STOP and report the exact consumer rather than silently retaining ambiguous compatibility.

## Scope

Inspect the current package source, public billing entrypoint, schemas, exports and tests.

Remove the obsolete contracts above from their canonical registry/export locations and remove tests that require their presence.

Retain, unchanged in semantics:

```text
ARCH-010 subscription reconciliation queue contract
App Pricing drain constant
recovery-capacity-exhausted message contract
BILLING_REFUND_REQUEST_RECEIVED
BILLING_REFUND_COMPLETED
BILLING_REFUND_REJECTED
createMerchantBillingSystemSourceKey
PurchasedRecoveryCreditCounterSnapshot / availablePurchasedRecoveryCredits if still used
all unrelated messaging/observability contracts
```

## Out of Scope

Do not:

- publish the package;
- edit consumer repositories;
- rename retained ARCH-010 contracts;
- add compatibility aliases or deprecated re-exports;
- remove refund message codes used by ADMIN-002/003;
- change queue payload versions unrelated to cancellation cleanup.

## Requirements

1. obsolete cancellation mode/mapping exports are absent from source, declarations and built public entrypoint;
2. obsolete cancellation message values and `BILLING_FREE_ALLOWANCE_EXHAUSTED` are absent from the billing system-code schema;
3. `BILLING_PLAN_CHANGE_ACTION_REQUIRED` is absent unless an active ARCH-010 consumer is proven; if proven, STOP for architect review;
4. refund message codes remain exact and parseable;
5. subscription reconciliation and generic `BILLING_RECOVERY_CAPACITY_EXHAUSTED` contracts remain exact;
6. no deprecated alias/re-export preserves the removed names;
7. package version is **not** changed in this task; publication/versioning belongs to SHARED-008.

## Work Items

- [x] Inspect current billing public exports and exact consumers represented by repository tests.
- [ ] Remove superseded cancellation mode/provider mapping exports.
- [ ] Remove obsolete cancellation system-message values.
- [ ] Remove `BILLING_FREE_ALLOWANCE_EXHAUSTED` and preserve the generic capacity-exhaustion code.
- [ ] Remove superseded plan-change action-required code if no ARCH-010 consumer exists.
- [ ] Update focused tests to assert retained ARCH-010 contracts and absence of removed exports.
- [ ] Build declarations/public entrypoint and verify removed names are absent.

## Interfaces / Contracts

Retained first-release Shared billing contracts are the only public compatibility surface after SHARED-008 publication.

Removed names intentionally have no compatibility alias because this is a pre-production breaking cleanup.

## Dependencies

`ARCH-010-SHARED-006` is Complete and represents the published 0.10.0 baseline containing all accepted ARCH-010 refund contracts.

## Enables

`ARCH-010-SHARED-008` publishes the cleaned package.

## Acceptance Criteria

1. all five cancellation mode/provider mapping symbols listed in Context are absent;
2. all three cancellation system-message values and `BILLING_FREE_ALLOWANCE_EXHAUSTED` are absent;
3. no deprecated alias or alternate export recreates them;
4. `BILLING_PLAN_CHANGE_ACTION_REQUIRED` is removed unless an active ARCH-010 consumer forced a stop;
5. all three ARCH-010 refund codes remain exact;
6. reconciliation and generic capacity-exhausted contracts remain unchanged;
7. unit tests, typecheck, build and diff check pass;
8. built declarations/public billing entrypoint contain none of the removed symbols.

## Validation

Run repository-declared equivalents of:

```text
npm test
npm run typecheck
npm run build
git diff --check
```

Also inspect the built package/public declaration surface and prove the removed symbol names are absent.

## Implementation Notes

This is deliberately breaking cleanup before first production. Do not add deprecation wrappers.

## Completion Report

### Status
Blocked pending consumer sequencing.

### Files Changed
No implementation files changed. Task metadata/report updated only.

### Work Completed
Confirmed the obsolete cancellation exports and billing message values are
currently published by Shared. Confirmed live consumers prevent safe breaking
removal within this task's scope. Reverted the implementation probe; the
implementation worktree is unchanged.

### Validation Results
`npm test` passed after dependency restore (`109` passed, `1` skipped because
`TEST_REDIS_URL` was not configured). `npm run typecheck` and `npm run build`
passed. `git diff --check` passed during the implementation probe. The built
runtime absence check passed during the probe, but generated output was not
retained because the source change is blocked.

### Deviations
The requested Shared removal was not committed because active consumers in
consumer repositories would break and consumer edits are explicitly out of
scope.

### Assumptions
No production consumer requires ARCH-009 local cancellation contracts.

### Unresolved Issues
Consumer cleanup/sequencing is required before this breaking Shared contract
removal can proceed.

### Architectural Concerns
Active consumers found:
- `moda-interact-background/src/services/subscription-cancellation.service.ts` imports `SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS` and `SubscriptionCancellationMode`, and passes the mode into the provider.
- `moda-interact-background/src/providers/shopify-partner-billing.provider.ts` imports both cancellation exports and indexes the provider mapping when executing cancellation.
- `moda-interact/app/services/merchant-support/system-message-actions.ts` handles `BILLING_FREE_ALLOWANCE_EXHAUSTED`.
- `moda-interact-background/tests/unit/services/recovery-billing.service.test.ts` asserts `BILLING_FREE_ALLOWANCE_EXHAUSTED` source keys.

Per task instruction, stop and return to `moda_architect` for sequencing rather
than editing consumer repositories.

### Git / VCS
Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHARED-007` on `task/ARCH-010-SHARED-007`. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHARED-007` on `task/ARCH-010-SHARED-007`. No implementation commit created because the task is blocked by out-of-scope consumers.

## Architect Review

### Review Status
Blocked — architect-confirmed consumer sequencing dependency.

### Review Notes

The repository agent obeyed the task's stop condition correctly. No Shared
implementation change is accepted or retained from Attempt 1.

The block is architectural sequencing, not a reason to preserve compatibility.

Confirmed active first-party consumers reported by the blocked run:

```text
moda-interact-background/src/services/subscription-cancellation.service.ts
  -> SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS
  -> SubscriptionCancellationMode

moda-interact-background/src/providers/shopify-partner-billing.provider.ts
  -> cancellation mapping/types
  -> local Shopify cancellation mutation path

moda-interact/app/services/merchant-support/system-message-actions.ts
  -> BILLING_FREE_ALLOWANCE_EXHAUSTED

moda-interact-background/tests/unit/services/recovery-billing.service.test.ts
  -> BILLING_FREE_ALLOWANCE_EXHAUSTED expectation/source key
```

`BILLING_PLAN_CHANGE_ACTION_REQUIRED` has no active first-party consumer in the
blocked-run inspection. It remains in SHARED-007's removal set; do not create a
compatibility alias for it.

The original rollout graph was circular:

```text
SHARED-007 removes contracts
  -> SHARED-008 publishes 0.11.0
  -> BACKGROUND-012 / SHOPIFY-023 clean consumers
```

but SHARED-007 cannot safely remove contracts while those consumers still compile
against them.

Architect resolution introduces two bounded pre-publication consumer cleanup tasks:

```text
ARCH-010-BACKGROUND-020
ARCH-010-SHOPIFY-024
```

Both execute against the already-published Shared `0.10.0`. They remove first-party
runtime/test consumers without changing Shared itself.

Corrected rollout:

```text
SHARED-006 / published 0.10.0
        |
        +--> BACKGROUND-020
        |
        +--> SHOPIFY-024
                 |
                 v
        both Accepted Complete
                 |
                 v
        SHARED-007 blocked -> ready
                 |
                 v
        SHARED-007 Attempt 2 removes retired exports/codes
                 |
                 v
        SHARED-008 publishes 0.11.0
```

SHARED-007 now depends on both cleanup tasks. It remains `blocked`, `attempt: 1`,
with no active executor/claim. Once both prerequisites are architect-accepted
Complete, `moda_architect` may transition this same task `blocked -> ready`.
The next execution claim will then be Attempt 2.

### Reviewed Files

```text
docs/decisions/shared/ARCH-010/SHARED-007-remove-preproduction-billing-compatibility-contracts.md
docs/architecture/ARCH-010-first-production-baseline.md
docs/architecture/ARCH-010-implementation-handoff.md
docs/decisions/background/ARCH-010/BACKGROUND-012-reconcile-shopify-subscription-cancellation.md
docs/decisions/background/ARCH-010/BACKGROUND-009-capacity-exhaustion-and-resume.md
docs/decisions/shopify/ARCH-010/SHOPIFY-023-conform-billing-runtime-to-first-production-baseline.md
moda-interact-shared/src/billing.ts
moda-interact-shared/src/billing.test.ts
```

Consumer repository source is not populated in this portable review archive; the
exact live-consumer paths above come from the task's canonical blocked-run Completion
Report and handoff. Existing ARCH-010 task definitions independently confirm that
BACKGROUND-012 owns removal of the local cancellation executor and that
SHOPIFY-023/BACKGROUND-009 own removal of the Free-only exhaustion compatibility.

### Validation Reviewed

Blocked-run validation is accepted as evidence that no retained Shared change was
needed:

```text
109 tests passed
typecheck passed
build passed
git diff --check passed
```

The handoff identifies:

```text
parent task branch commit: 15ef6a4
implementation task branch commit: 243209a
```

Those commits are blocking/report evidence only. They are not an accepted Shared
implementation.

### Architecture Conformance

Conformant.

ARCH-010 is explicitly pre-production, so the correct response is to remove the
first-party consumers before the breaking Shared release. The architect rejects:

```text
deprecated aliases
temporary re-exports
retaining local cancellation mutation contracts
retaining BILLING_FREE_ALLOWANCE_EXHAUSTED for historical rendering
```

The cleaned first-production Shared artifact remains the target.

### Follow-up

1. Execute `ARCH-010-BACKGROUND-020`.
2. Execute `ARCH-010-SHOPIFY-024`.
3. Architect-review both.
4. When both are Complete, return SHARED-007 from `blocked` to `ready`.
5. Reclaim SHARED-007 as Attempt 2 and perform only the originally defined Shared
   removal.
6. After SHARED-007 acceptance, execute publication task SHARED-008.

**Architect decision: Block confirmed; sequencing corrected. SHARED-007 remains
Blocked pending BACKGROUND-020 and SHOPIFY-024.**

## Dependency Resolution — 2026-09-12

The architect-confirmed consumer-sequencing block is resolved.

Both prerequisite consumer-cleanup tasks are Accepted Complete:

```text
ARCH-010-BACKGROUND-020   Complete
ARCH-010-SHOPIFY-024      Complete
```

Their accepted results prove:

```text
Background:
  no local appSubscriptionCancel executor
  no retired cancellation-contract consumer
  no BILLING_FREE_ALLOWANCE_EXHAUSTED consumer
  no BILLING_PLAN_CHANGE_ACTION_REQUIRED consumer
  canonical BILLING_RECOVERY_CAPACITY_EXHAUSTED retained

Shopify:
  no BILLING_FREE_ALLOWANCE_EXHAUSTED consumer
  no active cancellation-contract consumer
  no BILLING_PLAN_CHANGE_ACTION_REQUIRED consumer
  Shopify-hosted pricing navigation preserved
```

There is now no first-party consumer preventing the breaking Shared cleanup.

Canonical SHARED-007 state is therefore:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

Do not alter the previously recorded Attempt-1 blocked-run history.

The next valid execution claim is:

```text
attempt: 2
```

Attempt 2 must implement only the original SHARED-007 removal contract:

```text
remove retired cancellation mode/schema/args exports
remove retired cancellation billing message codes
remove BILLING_FREE_ALLOWANCE_EXHAUSTED
remove BILLING_PLAN_CHANGE_ACTION_REQUIRED
retain reconciliation, generic capacity-exhausted and refund contracts
prove built runtime/declarations contain none of the removed names
```

Do not reintroduce aliases or compatibility exports.

After SHARED-007 is architect-accepted Complete, `ARCH-010-SHARED-008` becomes eligible
to publish the clean Shared first-production baseline as `0.11.0`.

**Architect dependency decision: block cleared; SHARED-007 Ready for Attempt 2.**

